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
        - Prefer this program over catalog keywords ``pollution`` / ``air quality``
          — older CKAN search often missed EPD AQHI feeds
    """
    import json
    import urllib.request

    url = "https://dashboard.data.gov.hk/api/aqhi-individual?format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))
