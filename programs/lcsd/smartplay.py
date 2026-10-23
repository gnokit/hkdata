"""LCSD SmartPLAY activity / recreation class programmes."""


def activity_programs(keyword: str = None, district: str = None,
                      places_left_only: bool = False,
                      limit: int = 100) -> list:
    """LCSD SmartPLAY activity-programme catalogue (classes you can enrol in).

    Provides:
        - ACTIVITY_NO, TC/EN_PGM_NAME, TC_ACT_TYPE_NAME, TC_DISTRICT, TC_VENUE
        - PGM_START/END_DATE/TIME, TC_DAY, MIN/MAX_AGE, FEE, QUOTA, PLACES_LEFT
        - ENROL_METHOD (BALLOT/FCFS/WALKIN), enrol/ballot/open-enrol dates,
          TC_URL (SmartPLAY enrolment page)

    Coverage:
        - Geography: all 18 districts (filter by TC_DISTRICT)
        - Time:      programmes uploaded around the 15th for ~1.5 months ahead;
                     PLACES_LEFT refreshes about every 10 minutes

    Datasets:   hk-lcsd-prog-smartplay-prog
    Department: Leisure and Cultural Services Department
    Endpoint:   https://data.smartplay.lcsd.gov.hk/rest/cms/api/v1/publ/contents/open-data/activity-prog/file
    Format:     JSON (~12 MB list)

    Usage:
        >>> rows = activity_programs(keyword="羽毛球")
        >>> rows = activity_programs(keyword="游泳", district="深水埗",
        ...                          places_left_only=True, limit=20)

    Questions:
        - "康文署有咩活動班可以報名"
        - "LCSD badminton / running / swimming class enrolment"
        - "SmartPLAY places left"

    Quirks:
        - follow redirects; send User-Agent; download can take ~40s
        - filter with TC_ACT_TYPE_NAME (e.g. 羽毛球), not loose substring 「跑」
        - ~90% are BALLOT; PLACES_LEFT == QUOTA before ballot is normal
        - do NOT use hk-lcsd-event-event-leisure (stale leisure_prog.json)
        - enrolment still happens on SmartPLAY via TC_URL
    """
    import json
    import urllib.request

    url = ("https://data.smartplay.lcsd.gov.hk/rest/cms/api/v1/publ/"
           "contents/open-data/activity-prog/file")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if not isinstance(data, list):
        data = data.get("data") or data.get("results") or []

    kw = (keyword or "").strip()
    dist = (district or "").strip()
    out = []
    for row in data:
        if kw:
            hay = " ".join([
                str(row.get("TC_ACT_TYPE_NAME") or ""),
                str(row.get("EN_ACT_TYPE_NAME") or ""),
                str(row.get("TC_PGM_NAME") or ""),
                str(row.get("EN_PGM_NAME") or ""),
            ])
            if kw not in hay and kw.lower() not in hay.lower():
                continue
        if dist:
            dhay = str(row.get("TC_DISTRICT") or "") + " " + str(
                row.get("EN_DISTRICT") or "")
            if dist not in dhay and dist.lower() not in dhay.lower():
                continue
        if places_left_only:
            try:
                left = int(row.get("PLACES_LEFT") or 0)
            except (TypeError, ValueError):
                left = 0
            if left <= 0:
                continue
        out.append(row)
        if limit and len(out) >= int(limit):
            break
    return out
