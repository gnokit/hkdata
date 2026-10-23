"""Environmental Protection Department air-quality data."""


def aqhi_now() -> list:
    """Current Air Quality Health Index (AQHI) and health risk per station.

    Provides:
        - station name, AQHI (1-10/10+), health-risk category, publish time

    Coverage:
        - Geography: 18 monitoring stations (15 general + 3 roadside)
        - Time:      hourly

    Datasets:   hk-dpo-datagovhk2-city-dashboard-aqhi
    Department: Environmental Protection Department
    Endpoint:   https://dashboard.data.gov.hk/api/aqhi-individual?format=json
    Format:     JSON

    Usage:
        >>> rows = aqhi_now()                      # list[dict], one per station
        >>> next(r for r in rows if r["station"] == "Causeway Bay")

    Questions:
        - "what is the air quality index now?"
        - "AQHI in Mong Kok"

    Quirks:
        - City Dashboard JSON lags RSS by ~1 hour; use RSS for the very latest
        - AQHI scale 1-10+ -> Low / Moderate / High / Very High / Serious
        - pollutant concentrations (PM2.5/NO2/...) live in a different endpoint
          (see pm25_by_station). Prefer this program over catalog keywords
          ``pollution`` / ``air quality`` — older CKAN search often missed EPD
    """
    import json
    import urllib.request

    url = "https://dashboard.data.gov.hk/api/aqhi-individual?format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pm25_by_station(latest_only: bool = True) -> list:
    """Past-24h (or latest hour) PM2.5 and other pollutants per EPD station.

    Provides:
        - StationName, DateTime (RFC 822 +0800)
        - PM2.5, PM10, NO2, SO2, O3, CO (µg/m³; CO as published)

    Coverage:
        - Geography: 18 monitoring stations (15 general + 3 roadside)
        - Time:      hourly past-24h XML; refreshed hourly

    Datasets:   none — EPD AQHI open data (24pc XML; paired with AQHI feeds)
    Department: Environmental Protection Department
    Endpoint:   https://www.aqhi.gov.hk/epd/ddata/html/out/24pc_Eng.xml
    Format:     XML

    Usage:
        >>> rows = pm25_by_station()                 # latest hour, all stations
        >>> rows = pm25_by_station(latest_only=False)  # full 24h series
        >>> next(r for r in rows if "Causeway" in r["StationName"])

    Questions:
        - "PM2.5 by station"
        - "Causeway Bay particulate matter now"
        - "air pollutant concentration past 24 hours"

    Quirks:
        - AQHI (health index) is a different endpoint from pollutant XML
        - Chinese: replace _Eng.xml with _ChT.xml / _ChS.xml
        - empty pollutant tags appear when a station has no reading that hour
        - City Dashboard AQHI JSON lags RSS ~1h; this XML is the pollutant feed
    """
    import xml.etree.ElementTree as ET
    import urllib.request

    url = "https://www.aqhi.gov.hk/epd/ddata/html/out/24pc_Eng.xml"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())

    fields = ("StationName", "DateTime", "PM2.5", "PM10", "NO2", "SO2", "O3",
              "CO")
    rows = []
    for pc in root.iter("PollutantConcentration"):
        row = {}
        for f in fields:
            # Element names with a dot need find with exact tag
            el = pc.find(f)
            val = el.text if el is not None else None
            if f in ("PM2.5", "PM10", "NO2", "SO2", "O3", "CO") and val not in (
                    None, ""):
                try:
                    val = float(val)
                except ValueError:
                    pass
            row[f] = val
        rows.append(row)

    if not latest_only or not rows:
        return rows

    # Keep the latest DateTime per station
    latest = {}
    for r in rows:
        st = r.get("StationName")
        dt = r.get("DateTime") or ""
        prev = latest.get(st)
        if prev is None or dt > (prev.get("DateTime") or ""):
            latest[st] = r
    return list(latest.values())
