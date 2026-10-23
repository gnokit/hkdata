"""Transport Department / operators — ferry timetables and real-time ETA."""


def ferry_timetable(origin: str = "central", destination: str = "cc",
                    lang: str = "eng") -> list:
    """Licensed ferry static timetable for one TD origin→destination route.

    Provides:
        - Direction, Service Date (weekday vs Sunday/PH), Service Hour,
          Remark (1.0 = fast ferry, empty = ordinary)

    Coverage:
        - Geography: TD licensed ferry routes (Central↔outlying islands,
          North Point↔Hung Hom, etc.)
        - Time:      static timetable, updated as needed (not real-time)

    Datasets:   none — TD open data file under ferry-tt-ft (licensed ferry
                schedules & fares; discover via web, not CKAN "ferry")
    Department: Transport Department
    Endpoint:   https://www.td.gov.hk/datagovhk_td/ferry-tt-ft/resources/{lang}/
                ferry_{origin}_{destination}_timetable_{lang}.csv
    Format:     CSV (UTF-8 with BOM)

    Usage:
        >>> rows = ferry_timetable("central", "cc")   # Central → Cheung Chau
        >>> [r for r in rows if "Mondays to Saturdays" in r["Service Date"]][:3]
        >>> ferry_timetable("central", "mw")          # Central → Mui Wo

    Questions:
        - "中環去長洲渡輪時間表"
        - "Central to Cheung Chau ferry timetable"
        - "when is the next ferry from Central to Peng Chau?"

    Quirks:
        - CSV is UTF-8 with BOM — strip \\ufeff before DictReader
        - origin/destination slugs: central, cc, mw, pc, ysw, db, hh, np, ...
        - Remark "1.0" = fast ferry (~20 min); empty = ordinary (~55 min)
        - Central→Cheung Chau is Sun Ferry for live ETA (see sunferry_eta),
          not HKKF
        - Chinese: lang="chi" (TC) or "chi1" (SC); filename still uses that
          token after timetable_
    """
    import csv
    import io
    import urllib.request

    origin = origin.strip().lower().replace(" ", "_")
    destination = destination.strip().lower().replace(" ", "_")
    lang = lang.strip().lower()
    # Folder is en/tc/sc; filename token is eng/chi/chi1
    folder = {"eng": "en", "chi": "tc", "chi1": "sc",
              "en": "en", "tc": "tc", "sc": "sc"}.get(lang, lang)
    file_lang = {"en": "eng", "tc": "chi", "sc": "chi1",
                 "eng": "eng", "chi": "chi", "chi1": "chi1"}.get(lang, lang)
    url = (f"https://www.td.gov.hk/datagovhk_td/ferry-tt-ft/resources/{folder}/"
           f"ferry_{origin}_{destination}_timetable_{file_lang}.csv")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def sunferry_eta(route_code: str = "CECC") -> dict:
    """Sun Ferry real-time ETA (next trips + vessel GPS) for one route code.

    Provides:
        - type/version/generated_timestamp
        - data[]: routecode, route_en/tc/sc, vesselcode, depart_time, eta,
          lat/lng (vessel GPS), rmk_*, date_timestamp

    Coverage:
        - Geography: Sun Ferry routes (Central↔Cheung Chau/Mui Wo,
          North Point↔Hung Hom/Kowloon City, inter-island)
        - Time:      real-time, refreshed about every 1 minute

    Datasets:   none — operator open ETA API (not under data.gov.hk CKAN)
    Department: Sun Ferry Services Company Limited
    Endpoint:   https://www.sunferry.com.hk/eta/?route={route_code}
    Format:     JSON

    Usage:
        >>> r = sunferry_eta("CECC")          # Central → Cheung Chau
        >>> r["data"][0]["eta"], r["data"][0]["lat"]

    Questions:
        - "Sun Ferry ETA Central to Cheung Chau"
        - "長洲船幾時到"
        - "live ferry arrival Cheung Chau"

    Quirks:
        - follow redirects (-L); send a browser User-Agent
        - typically returns 2 rows: current trip (underway, with GPS) + next
        - no explicit on-time flag — compare depart_time vs actual / eta
        - route codes: CECC/CCCE, CEMW/MWCE, NPHH/HHNP, NPKC/KCNP,
          IIPECMUW/IIMUWPEC, IICHCMUW/IIMUWCHC
        - Central→Cheung Chau is Sun Ferry, NOT HKKF
    """
    import json
    import urllib.parse
    import urllib.request

    code = route_code.strip().upper()
    url = "https://www.sunferry.com.hk/eta/?route=" + urllib.parse.quote(code)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def hkkf_routes() -> list:
    """HKKF (Hong Kong & Kowloon Ferry) route list from the open-data API.

    Provides:
        - route_id, route_name_en/tc/sc, origin_* / destination_* names

    Coverage:
        - Geography: HKKF licensed routes (Central↔Sok Kwu Wan / Yung Shue Wan /
          Peng Chau; Peng Chau↔Hei Ling Chau) — NOT Central↔Cheung Chau
        - Time:      reference list, updated as needed

    Datasets:   none — HKKF open-data API
    Department: Hong Kong & Kowloon Ferry Holdings Limited
    Endpoint:   https://www.hkkfeta.com/opendata/route/
    Format:     JSON (Content-Type may be text/html; body is JSON)

    Usage:
        >>> routes = hkkf_routes()
        >>> [r["route_name_en"] for r in routes]

    Questions:
        - "HKKF ferry routes"
        - "中環去索罟灣渡輪"
        - "list Hong Kong Kowloon Ferry routes"

    Quirks:
        - trailing slash REQUIRED — /route without / returns 301 + empty body
        - follow redirects; User-Agent recommended
        - Central→Cheung Chau is Sun Ferry (sunferry_eta), not HKKF
        - /opendata/pier/ alone returns 422 Incorrect Parameter — pier lookups
          need route/extra params from the HKKF ETA API spec PDF; start from
          hkkf_routes() + hkkf_eta(), not a bare pier URL
    """
    import json
    import urllib.request

    url = "https://www.hkkfeta.com/opendata/route/"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["data"]


def hkkf_eta(route_id: int = 1, direction: str = "outbound") -> dict:
    """HKKF real-time ETA for one route_id and direction.

    Provides:
        - type/version/generated_timestamp
        - data[]: route_id, direction, date, session_time, ETA (ISO-8601 +08:00)

    Coverage:
        - Geography: one HKKF route × direction
        - Time:      real-time, about every 1 minute (data[] may be empty off-service)

    Datasets:   hkkf-hkkfdata-hkkf-eta-data
    Department: Hong Kong & Kowloon Ferry Holdings Limited
    Endpoint:   https://www.hkkfeta.com/opendata/eta/{route_id}/{direction}
    Format:     JSON

    Usage:
        >>> eta = hkkf_eta(1, "outbound")     # Central → Sok Kwu Wan
        >>> eta = hkkf_eta(3, "inbound")      # Peng Chau → Central Pier 6
        >>> eta["data"]

    Questions:
        - "HKKF ETA Sok Kwu Wan"
        - "索罟灣船幾時到"
        - "Central Peng Chau ferry live arrival"

    Quirks:
        - path is /eta/{route_id}/{direction} with NO trailing slash
          (unlike /route/ which REQUIRES a trailing slash)
        - direction must be "inbound" or "outbound" (case-sensitive lower)
        - route_id is integer from hkkf_routes() (1–4), not Sun Ferry letter codes
        - empty data[] is normal when no vessel is running that direction
        - API spec: https://www.hkkfeta.com/datagovhk/HKKF_ETA_API_Specification.pdf
    """
    import json
    import urllib.request

    direction = direction.strip().lower()
    if direction not in ("inbound", "outbound"):
        raise ValueError("direction must be 'inbound' or 'outbound'")
    url = (f"https://www.hkkfeta.com/opendata/eta/"
           f"{int(route_id)}/{direction}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def ferry_with_eta(origin: str = "central", destination: str = "cc",
                   lang: str = "eng") -> dict:
    """Compose TD ferry timetable with operator live ETA where available.

    Provides:
        - route resolution (TD slugs + operator)
        - timetable[] from ferry_timetable (static)
        - eta: operator payload (Sun Ferry or HKKF) or null
        - quirks[] explaining when ETA is missing / which operator applies

    Coverage:
        - Geography: TD licensed routes; live ETA only for Sun Ferry / HKKF
        - Time:      timetable static; ETA real-time when operator supports it

    Datasets:   TD ferry-tt-ft CSV; Sun Ferry ETA API; HKKF ETA
                (hkkf-hkkfdata-hkkf-eta-data)
    Department: Transport Department / Sun Ferry / HKKF
    Endpoint:   (composed) see ferry_timetable, sunferry_eta, hkkf_eta
    Format:     JSON dict joining CSV + operator JSON

    Usage:
        >>> r = ferry_with_eta("central", "cc")
        >>> r["operator"], len(r["timetable"]), r["eta"]
        >>> ferry_with_eta("central", "skw")   # HKKF Sok Kwu Wan

    Questions:
        - "中環去長洲船期同實時ETA"
        - "Central to Cheung Chau ferry timetable and live arrival"
        - "ferry with ETA Peng Chau"
        - "下一班去長洲嘅船"

    Quirks:
        - Central↔Cheung Chau / Mui Wo / Peng Chau (Sun) vs HKKF islands —
          wrong operator → empty ETA
        - Star Ferry / some TD-only routes have NO operator ETA API
        - inlines timetable + ETA fetch (pasteable; does not import sibling
          function objects — duplicates minimal HTTP)
        - Sun Ferry route codes: CECC/CCCE, CEMW/MWCE, CEPC/PCCE, …
        - HKKF needs route_id int + inbound/outbound; trailing slash only on /route/
        - ETA may list underway vessel + next; empty data[] off-service is normal
    """
    import csv
    import io
    import json
    import urllib.parse
    import urllib.request

    # Normalise aliases
    ALIASES = {
        "中環": "central", "central": "central", "cen": "central",
        "長洲": "cc", "cheung chau": "cc", "cc": "cc",
        "梅窩": "mw", "mui wo": "mw", "mw": "mw",
        "坪洲": "pc", "peng chau": "pc", "pc": "pc",
        "索罟灣": "skw", "sok kwu wan": "skw", "skw": "skw",
        "榕樹灣": "ysw", "yung shue wan": "ysw", "ysw": "ysw",
        "喜靈洲": "hlc", "hei ling chau": "hlc", "hlc": "hlc",
        "紅磡": "hh", "hung hom": "hh", "hh": "hh",
        "北角": "np", "north point": "np", "np": "np",
        "南丫": "skw",  # ambiguous — default Sok Kwu Wan quirk
    }

    def _slug(x):
        s = (x or "").strip().lower()
        return ALIASES.get(s, s.replace(" ", "_"))

    o = _slug(origin)
    d = _slug(destination)
    quirks = []

    # TD timetable slug pairs (bidirectional file names)
    TD_PAIR = {
        frozenset(("central", "cc")): ("central", "cc"),
        frozenset(("central", "mw")): ("central", "mw"),
        frozenset(("central", "pc")): ("central", "pc"),
        frozenset(("central", "ysw")): ("central", "ysw"),
        frozenset(("np", "hh")): ("np", "hh"),
    }

    # Sun Ferry codes by ordered (origin, dest)
    SUN = {
        ("central", "cc"): "CECC", ("cc", "central"): "CCCE",
        ("central", "mw"): "CEMW", ("mw", "central"): "MWCE",
        ("central", "pc"): "CEPC", ("pc", "central"): "PCCE",
        ("np", "hh"): "NPHH", ("hh", "np"): "HHNP",
    }

    # HKKF: match by destination keywords via routes list
    HKKF_DEST = {
        "skw": "Sok Kwu Wan",
        "ysw": "Yung Shue Wan",
        "pc": "Peng Chau",
        "hlc": "Hei Ling Chau",
        "central": "Central",
    }

    pair = TD_PAIR.get(frozenset((o, d)))
    tt_origin = tt_dest = None
    timetable = []
    tt_error = None
    if pair:
        # pick file direction matching request when possible
        if (o, d) in ((pair[0], pair[1]), (pair[1], pair[0])):
            tt_origin, tt_dest = o, d
        else:
            tt_origin, tt_dest = pair
        folder = {"eng": "en", "chi": "tc", "chi1": "sc",
                  "en": "en", "tc": "tc", "sc": "sc"}.get(lang, "en")
        file_lang = {"en": "eng", "tc": "chi", "sc": "chi1",
                     "eng": "eng", "chi": "chi", "chi1": "chi1"}.get(lang, "eng")
        url = (f"https://www.td.gov.hk/datagovhk_td/ferry-tt-ft/resources/{folder}/"
               f"ferry_{tt_origin}_{tt_dest}_timetable_{file_lang}.csv")
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                text = resp.read().decode("utf-8-sig")
            timetable = list(csv.DictReader(io.StringIO(text)))
        except Exception as exc:
            # try reverse file name
            url2 = (f"https://www.td.gov.hk/datagovhk_td/ferry-tt-ft/resources/"
                    f"{folder}/ferry_{tt_dest}_{tt_origin}_timetable_{file_lang}.csv")
            try:
                req = urllib.request.Request(
                    url2, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    text = resp.read().decode("utf-8-sig")
                timetable = list(csv.DictReader(io.StringIO(text)))
                tt_origin, tt_dest = tt_dest, tt_origin
            except Exception as exc2:
                tt_error = f"{exc}; reverse: {exc2}"
                quirks.append("TD timetable CSV not found for this pair")
    else:
        quirks.append(
            f"no known TD timetable slug pair for {o!r}→{d!r}; "
            "ETA-only if operator matches")

    eta = None
    operator = None
    sun_code = SUN.get((o, d))
    if sun_code:
        operator = "sunferry"
        url = ("https://www.sunferry.com.hk/eta/?route="
               + urllib.parse.quote(sun_code))
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            eta = json.loads(resp.read().decode("utf-8"))
        eta["_route_code"] = sun_code
    else:
        # Try HKKF
        try:
            req = urllib.request.Request(
                "https://www.hkkfeta.com/opendata/route/",
                headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                routes = json.loads(resp.read().decode("utf-8"))["data"]
        except Exception as exc:
            routes = []
            quirks.append(f"HKKF routes fetch failed: {exc}")

        dest_en = HKKF_DEST.get(d, d)
        orig_en = HKKF_DEST.get(o, o)
        match = None
        direction = None
        for r in routes:
            o_en = (r.get("origin_en") or "").lower()
            d_en = (r.get("destination_en") or "").lower()
            # routes are often bidirectional in name Central<=>X
            name = (r.get("route_name_en") or "").lower()
            if dest_en.lower() in d_en or dest_en.lower() in name:
                if orig_en.lower() in o_en or orig_en.lower() in name:
                    match = r
                    # outbound = origin→destination as listed
                    if orig_en.lower() in o_en:
                        direction = "outbound"
                    else:
                        direction = "inbound"
                    break
            if dest_en.lower() in o_en and orig_en.lower() in d_en:
                match = r
                direction = "inbound"
                break
        if match and direction:
            operator = "hkkf"
            rid = int(match["route_id"])
            url = f"https://www.hkkfeta.com/opendata/eta/{rid}/{direction}"
            req = urllib.request.Request(
                url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                eta = json.loads(resp.read().decode("utf-8"))
            eta["_route_id"] = rid
            eta["_direction"] = direction
            eta["_route_name_en"] = match.get("route_name_en")
        else:
            if not sun_code:
                quirks.append(
                    "no Sun Ferry or HKKF ETA mapping for this OD — "
                    "timetable-only (Star Ferry / other TD routes lack ETA)")
                operator = "timetable_only"

    return {
        "origin": o,
        "destination": d,
        "td_timetable_slugs": {"origin": tt_origin, "destination": tt_dest},
        "operator": operator,
        "timetable": timetable,
        "timetable_rows": len(timetable),
        "timetable_error": tt_error,
        "eta": eta,
        "quirks": quirks,
    }
