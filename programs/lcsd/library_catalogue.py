"""Hong Kong Public Libraries — catalogue search and branch holdings."""

_BASE_SEARCH = "https://webcat.hkpl.gov.hk/search/syndication"
_BASE_ITEM = "https://webcat.hkpl.gov.hk/lib/item?id={rid}&theme=WEB"


def _search_url(term, field="", fmt="book"):
    # NB: the term must be percent-encoded (%20), NOT "+" — the catalogue's
    # multi-word phrase matching silently returns nothing when the space is a
    # plus sign. urlencode(quote_via=quote) does the right thing.
    import urllib.parse

    query = urllib.parse.urlencode(
        {"match_1": "PHRASE", "field_1": field, "term_1": term},
        quote_via=urllib.parse.quote)
    return (f"{_BASE_SEARCH}?{query}"
            f"&facet_format={fmt}&syndication=true&theme=WEB")


def _parse_items(feed):
    """RSS items → dicts (feedparser handles the XML quirks)."""
    import feedparser
    import urllib.parse

    out = []
    for item in feedparser.parse(feed).entries:
        link = (item.get("link") or "").strip()
        rid = ""
        if link:
            params = urllib.parse.parse_qs(urllib.parse.urlparse(link).query)
            rid = (params.get("id") or [""])[0]
        out.append({
            "title": (item.get("title") or "").strip(),
            "author": (item.get("description") or "").strip(),
            "record_id": rid,
            "url": link,
        })
    return out


def _parse_holdings(page):
    """HTML record page → one dict per copy (first table with 6+ cells)."""
    from lxml import html as lxml_html

    try:
        doc = lxml_html.fromstring(page)
    except Exception:
        return []
    for table in doc.xpath("//table"):
        trs = table.xpath(".//tbody/tr") or table.xpath(".//tr[td]")
        rows = []
        for tr in trs:
            cells = [" ".join(td.text_content().split())
                     for td in tr.xpath("./td")]
            if len(cells) >= 6 and cells[0]:
                rows.append({
                    "library": cells[0],
                    "call_number": cells[1],
                    "volume": cells[2],
                    "media_code": cells[3],
                    "status": cells[4],
                    "collection": cells[5],
                })
        if rows:
            return rows
    return []


def catalogue_search(term, field="", limit=5, with_holdings=False) -> list:
    """Search the HKPL catalogue (香港公共圖書館館藏目錄).

    Provides:
        - title (as the catalogue renders it, usually "title / author."),
          author, the catalogue record id (``chamo:<n>``) and the record URL
        - with ``with_holdings=True``: the branch holdings of each record —
          library, call number, volume, media code, status, collection
        - the status vocabulary: 館內架上 (on the shelf), 館外備用書庫N (in the
          reserve store), 閉架 (closed stack), 請向館員索閱 (ask staff),
          待上架 (awaiting shelving), 到期日 YYYY-MM-DD (on loan, due back),
          轉移中 (in transit)

    Coverage:
        - Geography: all HKPL branches (including mobile libraries) — a title
          can be held by many branches at once
        - Time:      live catalogue; loan statuses reflect the moment of the
          call

    Datasets:   none for the search — the syndication endpoint below is the
                one published by hk-lcsd-lib-lib-newadd, but that dataset only
                publishes fixed facet queries; searching by title/author uses
                the catalogue's own (undocumented) query parameters
    Department: Leisure and Cultural Services Department
                (Hong Kong Public Libraries)
    Endpoint:   https://webcat.hkpl.gov.hk/search/syndication
                    ?match_1=PHRASE&field_1=&term_1=<phrase>
                    &facet_format=book&syndication=true&theme=WEB
                https://webcat.hkpl.gov.hk/lib/item?id=chamo:<n>&theme=WEB
    Format:     RSS (search) / HTML (record page)

    Usage:
        >>> hits = catalogue_search("harry potter and the goblet of fire")
        >>> hits[0]["title"]
        'Harry Potter and the goblet of fire / by J.K. Rowling'
        >>> catalogue_search("巫術藍", limit=3)
        >>> catalogue_search("dune", with_holdings=True)[0]["holdings"][0]
        {'library': '12. 香港中央圖書館', 'call_number': 'JF ROW', ...}

    Questions:
        - "is [title] in the Hong Kong public library?"
        - "which branch has [book] available on the shelf?"
        - "can I borrow [book] at my local library?"
        - "圖書館 有冇 呢本書" / "公共圖書館 館藏 查詢"
        - "what is the call number for [title]"

    Quirks:
        - the search form is ``match_1=PHRASE&field_1=&term_1=<phrase>``;
          ``search_1=`` is accepted but **ignored** (it returns the unfiltered
          newest-first list), and ``field_1=title`` / ``field_1=author``
          restrict the field
        - PHRASE must match the **catalogue title string** exactly — user
          wording often differs (e.g. 「哈利波特與消失的密室」 vs catalogue
          「哈利波特. 消失的密室」). On 0 hits, retry a shorter unique phrase
          (subtitle) or the English original title
        - correct endpoint is ``/search/syndication`` — NOT ``/rss/new``.
          Valid sort values: ``sort=relevance`` and ``sort=dateNewest``;
          ``sort=date`` is wrong and must not be used
        - the term must be percent-encoded — a ``+`` for the space makes a
          multi-word phrase match **nothing** and returns zero items
        - the feed returns at most **5 items** and has no pagination; run
          several queries (title, Chinese title, author) to see more;
          a full page of 5 may mean more exist
        - merging relevance + dateNewest and deduping: mostly-overlap ≈
          holdings exhausted; zero overlap ≈ more titles exist
        - one title usually has **several printings** with very different
          holdings — aggregate across records (see ``catalogue_availability``)
        - the record page is a Wicket HTML app; holdings live in the first
        ``<tbody>`` table of the 館藏項目 tab
        - search hits carry no date; holdings carry the live loan status
        - there is no REST/OAI-PMH/SRU catalogue API on data.gov.hk — this
          RSS syndication (+ HTML holdings scrape) is the supported path
    """
    import requests

    url = _search_url(term, field=field)
    resp = requests.get(url, headers={"User-Agent": "curl/8.0"}, timeout=30)
    resp.raise_for_status()
    rows = _parse_items(resp.content)
    if limit:
        rows = rows[:limit]
    if with_holdings:
        for row in rows:
            row["holdings"] = catalogue_holdings(row["record_id"])
    return rows


def catalogue_holdings(record) -> list:
    """Branch-by-branch holdings of one catalogue record.

    Provides:
        - for every copy HKPL holds: the branch library, call number, volume,
          media code, the live status (館內架上 / 館外備用書庫N / 閉架 /
          請向館員索閱 / 到期日 YYYY-MM-DD / 轉移中) and the collection
          (兒童借閱圖書館 / 青少年借閱圖書館 / 成人借閱圖書館)

    Coverage:
        - Geography: the branches that hold the copy
        - Time:      live — a due date means the copy is on loan until then

    Datasets:   none — **scraped** from the public catalogue record page.
                There is no data.gov.hk dataset for per-branch holdings or
                loan status; this is the department's own web app
    Department: Leisure and Cultural Services Department
                (Hong Kong Public Libraries)
    Endpoint:   https://webcat.hkpl.gov.hk/lib/item?id=chamo:<n>&theme=WEB
    Format:     HTML (parsed from the 館藏項目 table)

    Usage:
        >>> catalogue_holdings("chamo:3377318")
        [{'library': '12. 香港中央圖書館', 'call_number': 'JF ROW', ...}]
        >>> catalogue_holdings("https://webcat.hkpl.gov.hk/lib/item?id=chamo:3377318&theme=WEB")

    Questions:
        - "which branches hold this book?"
        - "is this copy on the shelf or on loan?"
        - "what branch has Harry Potter on the shelf right now"

    Quirks:
        - one row per copy, so a branch can appear several times (different
          copies, different call numbers, e.g. JF ROW and YF ROW)
        - 館內架上 = borrowable now; 館外備用書庫N = in the reserve store, ask at
          the desk; 閉架 = closed stack (mobile libraries); 請向館員索閱 = ask
          staff; 待上架 = awaiting shelving; 到期日 <date> = on loan until
          that date; 轉移中 = in transit
        - mobile libraries (流動圖書館) and the reserve store hold copies that
          are not walk-up borrowable
        - the record page occasionally returns without its holdings table; the
          function retries three times and returns whatever it got, so an
          empty result means "no holdings parsed", not necessarily "no copy"
    """
    import requests

    rid = record
    if "id=" in str(record):
        rid = str(record).split("id=")[1].split("&")[0]
    url = _BASE_ITEM.format(rid=rid)
    rows = []
    for attempt in range(3):
        try:
            resp = requests.get(url, headers={"User-Agent": "curl/8.0"},
                                timeout=30)
            page = resp.text
        except Exception:
            page = ""
        rows = _parse_holdings(page)
        if rows:
            return rows
        # the record page occasionally comes back without its holdings table;
        # retry rather than reporting a branch count that is too low
        if attempt < 2:
            import time

            time.sleep(0.5 * (attempt + 1))
    return rows


def catalogue_availability(term, field="", with_holdings=False,
                            title_filter=None) -> dict:
    """Is a title in the HKPL catalogue, and where can it be borrowed now?

    Provides:
        - "found": whether any catalogue record matched
        - "records": the matching printings (title, author, record id, url)
        - "branches": every branch holding a copy, with the statuses seen
        - "branches_on_shelf": branches where a copy is borrowable right now
          (館內架上)
        - "editions": how many printings were found

    Coverage:
        - Geography: all HKPL branches
        - Time:      live loan status at the moment of the call

    Datasets:   none — the branch availability is **scraped** from the
                catalogue record page (no open dataset for holdings); the
                search endpoint is the one published by hk-lcsd-lib-lib-newadd
                but with the catalogue's own undocumented query parameters
    Department: Leisure and Cultural Services Department
                (Hong Kong Public Libraries)
    Endpoint:   https://webcat.hkpl.gov.hk/search/syndication
                https://webcat.hkpl.gov.hk/lib/item?id=chamo:<n>&theme=WEB
    Format:     RSS (search) + HTML (holdings, scraped)

    Usage:
        >>> a = catalogue_availability("harry potter and the goblet of fire",
        ...                            title_filter="goblet of fire")
        >>> a["found"], a["editions"], len(a["branches_on_shelf"])
        (True, 4, 21)

    Questions:
        - "is Harry Potter available in the public library?"
        - "can I get [title] at any branch today?"
        - "有冇書可以借"

    Quirks:
        - the 5-item cap per query means "editions" is a lower bound — run the
          title, the Chinese title and the author as separate calls to see more
        - the phrase search also returns **companion volumes** (study guides,
          film companions, almanacs); pass ``title_filter`` to keep only the
          work itself — it matches the **start** of the record title, since the
          catalogue renders "title / author"
        - a title with no holdings rows is catalogued but not on the shelf
    """
    records = catalogue_search(term, field=field, with_holdings=with_holdings)
    if title_filter:
        needle = title_filter.lower()
        # prefix match, not substring: the catalogue puts the title first
        # ("<title> / <author>"), so a study guide whose title merely mentions
        # the work ("Teaching fantasy novels : from The Hobbit to Harry Potter
        # and the goblet of fire") is excluded, while every printing of the
        # novel itself is kept
        records = [r for r in records
                   if r["title"].lower().lstrip("﻿").startswith(needle)]
    branches = {}
    on_shelf = set()
    for rec in records:
        for row in rec.get("holdings") or []:
            branches.setdefault(row["library"], set()).add(row["status"])
            if "館內架上" in row["status"]:
                on_shelf.add(row["library"])
    return {
        "found": bool(records),
        "editions": len(records),
        "records": records,
        "branches": {k: sorted(v) for k, v in sorted(branches.items())},
        "branches_on_shelf": sorted(on_shelf),
    }
