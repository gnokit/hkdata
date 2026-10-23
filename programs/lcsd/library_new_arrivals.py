"""Hong Kong Public Libraries — new arrivals (新到館圖書)."""

#: One entry per collection facet in the dataset's resource list.
#: ``{collection: {language: query-string}}`` — the query string is appended to
#: the WebCat syndication endpoint.
_COLLECTIONS = {
    "adult_books": {
        "en": "facet_format=book&facet_item_class=3&facet_lang=eng",
        "chi": "facet_format=book&facet_item_class=3&facet_lang=chi",
    },
    "adult_fiction": {
        "en": "facet_format=book&facet_item_class=3&facet_lang=eng"
              "&match_1=PHRASE&field_1&term_1=fiction",
        "chi": "facet_format=book&facet_item_class=3&facet_lang=chi"
               "&match_1=PHRASE&field_1&term_1=%E5%B0%8F%E8%AA%AA",
    },
    "adult_audio_cd": {
        "en": "facet_format=sound_recording.cd&facet_item_class=7&facet_lang=eng",
        "chi": "facet_format=sound_recording.cd&facet_item_class=7&facet_lang=chi",
    },
    "adult_reference": {
        "en": "facet_item_class=32&facet_lang=eng&filter_collection_group=EAR+"
              "English+Adult+Reference+%E8%8B%B1%E6%96%87%E6%88%90%E4%BA%BA%E5%8F%83%E8%80%83",
        "chi": "facet_item_class=32&facet_lang=chi&filter_collection_group=CAR+"
               "Chinese+Adult+Reference+%E4%B8%AD%E6%96%87%E6%88%90%E4%BA%BA%E5%8F%83%E8%80%83",
    },
    "hk_information": {
        "en": "facet_lang=eng&filter_collection_group=SC:HKI_Hong+Kong+"
              "Information+%E9%A6%99%E6%B8%AF%E8%B3%87%E6%96%99",
        "chi": "facet_lang=chi&filter_collection_group=SC:HKI_Hong+Kong+"
               "Information+%E9%A6%99%E6%B8%AF%E8%B3%87%E6%96%99",
    },
    "children_books": {
        "en": "facet_format=book&facet_item_class=11&facet_lang=eng",
        "chi": "facet_format=book&facet_item_class=11&facet_lang=chi",
    },
    "children_fiction": {
        "en": "facet_format=book&facet_item_class=11&facet_lang=eng"
              "&match_1=PHRASE&field_1&term_1=fiction",
        "chi": "facet_format=book&facet_item_class=11&facet_lang=chi"
               "&match_1=PHRASE&field_1&term_1=%E5%B0%8F%E8%AA%AA",
    },
    "children_audiobook": {
        "en": "facet_format=sound_recording.audiobook&facet_item_class=15"
              "&facet_lang=eng",
        "chi": "facet_format=sound_recording.audiobook&facet_item_class=15"
               "&facet_lang=chi",
    },
    "children_audio_cd": {
        "en": "facet_format=sound_recording.cd&facet_item_class=15&facet_lang=eng",
        "chi": "facet_format=sound_recording.cd&facet_item_class=15&facet_lang=chi",
    },
    "children_reference": {
        "en": "facet_item_class=32&facet_lang=eng&filter_collection_group=EJR+"
              "English+Children/+Young+Adult+Reference+%E8%8B%B1%E6%96%87%E5%85%92%E7%AB%A5/+"
              "%E9%9D%92%E5%B0%91%E5%B9%B4%E5%8F%83%E8%80%83",
        "chi": "facet_item_class=32&facet_lang=chi&filter_collection_group=CJR+"
               "Chinese+Children/+Young+Adult+Reference+%E4%B8%AD%E6%96%87%E5%85%92%E7%AB%A5/+"
               "%E9%9D%92%E5%B0%91%E5%B9%B4%E5%8F%83%E8%80%83",
    },
    "young_adult_lending": {
        "en": "filter_collection_group=EYL+English+Young+Adult+Lending+"
              "%E8%8B%B1%E6%96%87%E9%9D%92%E5%B0%91%E5%B9%B4%E5%80%9F%E9%96%B1",
        "chi": "filter_collection_group=CYL+Chinese+Young+Adult+Lending+"
               "%E4%B8%AD%E6%96%87%E9%9D%92%E5%B0%91%E5%B9%B4%E5%80%9F%E9%96%B1",
    },
    "young_adult_reference": {
        "en": "filter_collection_group=EYR+English+Young+Adult+Reference+"
              "%E8%8B%B1%E6%96%87%E9%9D%92%E5%B0%91%E5%B9%B4%E5%8F%83%E8%80%83",
        "chi": "filter_collection_group=CYR+Chinese+Young+Adult+Reference+"
               "%E4%B8%AD%E6%96%87%E9%9D%92%E5%B0%91%E5%B9%B4%E5%8F%83%E8%80%83",
    },
}

#: Human-readable labels, in Traditional Chinese and English.
_LABELS = {
    "adult_books": ("成人外借圖書", "Adult lending books"),
    "adult_fiction": ("成人小說", "Adult lending books (fiction)"),
    "adult_audio_cd": ("成人音碟", "Adult lending audio CDs"),
    "adult_reference": ("成人參考資料", "Adult reference materials"),
    "hk_information": ("香港資料", "Hong Kong Information Collection"),
    "children_books": ("兒童及青少年外借圖書", "Children and YA lending books"),
    "children_fiction": ("兒童及青少年小說", "Children and YA lending books (fiction)"),
    "children_audiobook": ("兒童及青少年有聲書", "Children and YA lending audio books"),
    "children_audio_cd": ("兒童及青少年音碟", "Children and YA lending audio CDs"),
    "children_reference": ("兒童及青少年參考資料", "Children and YA reference materials"),
    "young_adult_lending": ("青少年外借資料", "Young adult lending materials"),
    "young_adult_reference": ("青少年參考資料", "Young adult reference materials"),
}

_BASE = "https://webcat.hkpl.gov.hk/search/syndication?"


def new_arrivals(collection="adult_books", language="chi", limit=None) -> list:
    """Newly added items in a Hong Kong Public Libraries collection.

    Provides:
        - title (bibliographic string: title / author / translator, exactly as
          the catalogue renders it)
        - author (the ``<description>`` field of the syndication feed)
        - permalink to the catalogue record (``webcat.hkpl.gov.hk/lib/item?id=...``)
        - date_added as an ISO timestamp in **HKT** (``date_added``) plus the
          raw GMT ``pubDate`` the feed publishes (``pub_date``)
        - collection and language, so results from several facets can be merged

    Coverage:
        - Geography: Hong Kong Public Libraries (all branches; a new item may
          be held at only some of them — the feed does not say which)
        - Time:      weekly refresh; the feed lists items in
          ``dateNewest`` order, newest first

    Datasets:   hk-lcsd-lib-lib-newadd
    Department: Leisure and Cultural Services Department
                (Hong Kong Public Libraries)
    Endpoint:   https://webcat.hkpl.gov.hk/search/syndication
                ?{facet query}&sort=dateNewest&syndication=true&theme=WEB
    Format:     RSS (XML)

    Usage:
        >>> books = new_arrivals()                       # 中文成人外借圖書
        >>> books[0]["title"], books[0]["date_added"]
        ('善意 / A.Z.著.', '2026-09-10T09:08:44+08:00')
        >>> new_arrivals("children_books", "en", limit=5)
        >>> new_arrivals("adult_fiction", "chi")

    Questions:
        - "what are the new arrivals at Hong Kong Public Libraries?"
        - "新到館圖書" / "新到館 書" / "圖書館 新書"
        - "new books in the children's section of the public library"
        - "香港公共圖書館 新增書籍 清單"
        - "what books did the library acquire recently"

    Quirks:
        - the feed holds only a short window (tens of items), not the whole
          acquisition history — it is a "what's new" feed, not a catalogue
        - each collection/language pair is a **separate resource** in the
          dataset; there is no single combined feed
        - sort param must be ``sort=dateNewest`` (NOT ``sort=date``); endpoint
          is ``/search/syndication``, not ``webcat.hkpl.gov.hk/rss/new``
        - ``date_added`` is converted from the feed's GMT ``pubDate`` to HKT
          (UTC+8); the raw value is kept in ``pub_date``
        - titles embed the responsibility statement ("/ A.Z.著."), so the
          author is inside the title as well as in ``author``
        - "adult books" (facet_item_class=3) already includes fiction; the
          separate ``adult_fiction`` facet is a filtered subset of it
        - Chinese-language facets do **not** imply Chinese-only titles — a
          bilingual title such as "善意 / A.Z.著." appears in both
        - ``young_adult_lending`` and ``young_adult_reference`` carry no
          ``facet_format``/``facet_item_class`` — they are collection-group
          filters over the whole catalogue
        - the two **audio** feeds (``children_audiobook``, ``children_audio_cd``)
          publish no ``pubDate``/``dc:date`` at all, so ``date_added`` is None
          for those items and no date can be reported for them
        - ``pubDate`` is the catalogue record's own timestamp and the feeds are
          served in ``dateNewest`` order, so the dates are *not* monotonic
          within a feed
    """
    import feedparser
    import requests
    from datetime import datetime, timedelta, timezone

    if collection not in _COLLECTIONS:
        raise ValueError(
            f"unknown collection {collection!r}; "
            f"expected one of {sorted(_COLLECTIONS)}")
    if language not in _COLLECTIONS[collection]:
        raise ValueError(
            f"unknown language {language!r} for {collection!r}; "
            f"expected one of {sorted(_COLLECTIONS[collection])}")

    query = _COLLECTIONS[collection][language]
    url = f"{_BASE}{query}&sort=dateNewest&syndication=true&theme=WEB"
    resp = requests.get(url, headers={"User-Agent": "curl/8.0"}, timeout=30)
    resp.raise_for_status()
    feed = feedparser.parse(resp.content)

    hkt = timezone(timedelta(hours=8))
    rows = []
    for item in feed.entries:
        pub = (item.get("published") or item.get("updated") or "").strip()
        parsed = item.get("published_parsed") or item.get("updated_parsed")
        added = None
        if parsed:
            stamp = datetime(*parsed[:6], tzinfo=timezone.utc)
            added = stamp.astimezone(hkt).isoformat()
        rows.append({
            "title": (item.get("title") or "").strip(),
            "author": (item.get("description") or "").strip(),
            "link": (item.get("link") or "").strip(),
            "date_added": added,
            "pub_date": pub,
            "collection": collection,
            "language": language,
        })
    if limit:
        rows = rows[:limit]
    return rows


def new_arrivals_collections() -> list:
    """The collection/language facets available in the new-arrivals dataset.

    Provides:
        - collection key (pass to ``new_arrivals``), its Chinese and English
          labels, and the languages it is published in

    Coverage:
        - Geography: n/a (a facet catalogue)
        - Time:      static — mirrors the dataset's resource list

    Datasets:   hk-lcsd-lib-lib-newadd
    Department: Leisure and Cultural Services Department
                (Hong Kong Public Libraries)
    Endpoint:   https://data.gov.hk/dataset/hk-lcsd-lib-lib-newadd
    Format:     metadata

    Usage:
        >>> new_arrivals_collections()[0]
        {'collection': 'adult_books', 'label_chi': '成人外借圖書',
         'label_en': 'Adult lending books', 'languages': ['en', 'chi']}

    Questions:
        - "what sections of the library publish new arrivals?"
        - "which new-arrival feeds are in Chinese?"
        - "圖書館 新到館 分類"

    Quirks:
        - the dataset ships 26 resources = 13 collections x 2 languages
    """
    return [
        {
            "collection": key,
            "label_chi": _LABELS[key][0],
            "label_en": _LABELS[key][1],
            "languages": sorted(_COLLECTIONS[key].keys()),
        }
        for key in _COLLECTIONS
    ]
