"""Lands Department — GeoInfo Map Location Search (POI / place / MTR exit)."""


def location_search(query: str, convert_wgs84: bool = True,
                    max_convert: int = 10) -> list:
    """Free-text Location Search for buildings, POIs, landmarks and MTR exits.

    Provides:
        - nameEN / nameZH, addressEN / addressZH, districtEN / districtZH
        - HK1980 grid x/y (EPSG:2326); when convert_wgs84, also lat/lng WGS84

    Coverage:
        - Geography: HK-wide GeoInfo Map gazetteer (buildings, place names,
          iGeoCom POIs, Wi-Fi / post boxes, MTR exits as "港鐵…進出口")
        - Time:      static inventory (no timestamp in response)

    Datasets:   hk-landsd-openmap-development-location-search-api
                (+ optional hk-landsd-openmap-coordinates-transformation-api)
    Department: Lands Department (GeoInfo Map)
    Endpoint:   https://www.map.gov.hk/gs/api/v1.0.0/locationSearch?q={query}
                https://www.geodetic.gov.hk/transform/v2/?inSys=hkgrid&outSys=wgsgeog&e=&n=
    Format:     JSON

    Usage:
        >>> hits = location_search("時代廣場")
        >>> hits[0]["nameZH"], hits[0].get("lat"), hits[0].get("lng")
        >>> location_search("港鐵深水埗站進出口")   # MTR exits

    Questions:
        - "where is Times Square / 時代廣場喺邊"
        - "coordinates of a shopping centre"
        - "nearest MTR exit to X"
        - "黃金電腦商場地址"

    Quirks:
        - use www.map.gov.hk (geodata.gov.hk host does not resolve)
        - urllib without User-Agent gets HTTP 403
        - x/y are HK1980 metres — convert before plotting on OSM/Google
        - distinct from ALS address_lookup (formal street address / GeoAddress);
          popular trade names may hit here but miss ALS
        - response has no data timestamp — report retrieval time (HKT)
        - throttle; API terms forbid bursts
        - WGS84 conversion calls geodetic.gov.hk per hit; default
          max_convert=10 to avoid long waits on broad queries
    """
    import json
    import urllib.parse
    import urllib.request

    q = (query or "").strip()
    if not q:
        return []

    url = ("https://www.map.gov.hk/gs/api/v1.0.0/locationSearch?q="
           + urllib.parse.quote(q))
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        hits = json.loads(resp.read().decode("utf-8"))
    if not isinstance(hits, list):
        return []

    if not convert_wgs84:
        return hits

    out = []
    for i, h in enumerate(hits):
        if i >= int(max_convert):
            out.extend(dict(x) for x in hits[i:])
            break
        row = dict(h)
        try:
            e = float(h.get("x"))
            n = float(h.get("y"))
        except (TypeError, ValueError):
            out.append(row)
            continue
        turl = (f"https://www.geodetic.gov.hk/transform/v2/"
                f"?inSys=hkgrid&outSys=wgsgeog&e={e}&n={n}")
        treq = urllib.request.Request(
            turl, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(treq, timeout=20) as tresp:
                tj = json.loads(tresp.read().decode("utf-8"))
            # API returns wgs84 lat/long under various keys across versions
            lat = (tj.get("wgsLat") or tj.get("wgs84Latitude")
                   or tj.get("latitude") or tj.get("lat"))
            lng = (tj.get("wgsLong") or tj.get("wgs84Longitude")
                   or tj.get("longitude") or tj.get("long")
                   or tj.get("lng"))
            if lat is not None and lng is not None:
                row["lat"] = float(lat)
                row["lng"] = float(lng)
        except Exception:
            pass
        out.append(row)
    return out
