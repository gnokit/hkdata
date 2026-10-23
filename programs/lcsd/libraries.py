"""LCSD / HKPL — public library branches and computer-session vacancy."""


def library_branches() -> list:
    """Hong Kong public library branch locations (CSDI WFS GeoJSON).

    Provides:
        - NameEN/NameTC, AddressEN/AddressTC, LibraryTypeTC (固定/流動/自助),
          DistrictTC, TelephoneTC, WebsiteTC, LATITUDE/LONGITUDE
        - GeoJSON geometry Point coordinates (WGS84)

    Coverage:
        - Geography: HK-wide fixed, mobile and self-service libraries
        - Time:      static inventory (OpeningHours field is often N.A.)

    Datasets:   hk-lcsd-csdi-libraries
    Department: Leisure and Cultural Services Department (HKPL)
    Endpoint:   https://portal.csdi.gov.hk/server/services/common/lcsd_rcd_1629267205214_44807/MapServer/WFSServer?service=wfs&request=GetFeature&typeNames=LIBRARY&outputFormat=geojson
    Format:     GeoJSON

    Usage:
        >>> libs = library_branches()
        >>> [b for b in libs if "深水埗" in (b.get("NameTC") or "")]

    Questions:
        - "最近嘅圖書館喺邊"
        - "HK public library branches"
        - "深水埗公共圖書館地址"

    Quirks:
        - data.gov.hk resource is often only a geoportal page — build the WFS
          URL yourself (datasetId ≈ service name)
        - OpeningHours columns are typically N.A.; use WebsiteTC for hours
        - send User-Agent
    """
    import json
    import urllib.request

    url = ("https://portal.csdi.gov.hk/server/services/common/"
           "lcsd_rcd_1629267205214_44807/MapServer/WFSServer"
           "?service=wfs&request=GetFeature&typeNames=LIBRARY"
           "&outputFormat=geojson")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        fc = json.loads(resp.read().decode("utf-8"))
    out = []
    for feat in fc.get("features") or []:
        props = dict(feat.get("properties") or {})
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates") or []
        if len(coords) >= 2:
            props.setdefault("LONGITUDE", coords[0])
            props.setdefault("LATITUDE", coords[1])
            props["lng"] = coords[0]
            props["lat"] = coords[1]
        out.append(props)
    return out


def library_computers(language: str = "zh-HK") -> list:
    """HKPL computer / session facilities with live open status and vacancies.

    Provides:
        - libraryCode, libraryDisplayName, district, address, telephone,
          isOpen, lastUpdateDate, sessionList (per-session vacancy when open)

    Coverage:
        - Geography: ~30 branches that publish computer-session PSI
        - Time:      near real-time; sessionList empty when closed

    Datasets:   hk-lcsd-lib-lib-computers
    Department: Leisure and Cultural Services Department (HKPL)
    Endpoint:   https://sls.hkpl.gov.hk/api/cfm-admin-service/open-api/library/selectLibraryPageInfoForPSI?language={language}
    Format:     JSON

    Usage:
        >>> rows = library_computers()
        >>> [r for r in rows if r.get("isOpen") and "深水埗" in r["libraryDisplayName"]]

    Questions:
        - "圖書館電腦有冇位"
        - "HKPL computer vacancy"
        - "is Sham Shui Po library open for PC sessions?"

    Quirks:
        - only ~30 libraries; not every branch from library_branches()
        - when closed, sessionList is empty — check isOpen / lastUpdateDate
        - language=zh-HK or en
    """
    import json
    import urllib.parse
    import urllib.request

    lang = urllib.parse.quote(language or "zh-HK")
    url = ("https://sls.hkpl.gov.hk/api/cfm-admin-service/open-api/library/"
           f"selectLibraryPageInfoForPSI?language={lang}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data if isinstance(data, list) else data.get("data") or []
