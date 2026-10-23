"""Census and Statistics Department — port cargo throughput."""


def port_cargo_throughput() -> list:
    """Port cargo throughput ('000 tonnes) with year-on-year % change.

    Provides:
        - cargo throughput by direction (inward/outward/total) and shipment
          type (direct/transhipment), quarterly + annual from 1993

    Coverage:
        - Geography: HK port (seaborne + river cargo)
        - Time:      historical series, quarterly (YYYYQQ) + annual

    Datasets:   hk-censtatd-tablechart-410-55110
    Department: Census and Statistics Department
    Endpoint:   https://www.censtatd.gov.hk/api/get.php?id=410-55110&lang=en&full_series=1
    Format:     JSON

    Usage:
        >>> rows = port_cargo_throughput()    # list[dict]
        >>> [r for r in rows if r["freq"] == "Q" and r["DIRECTION"] == ""]

    Questions:
        - "how much cargo passed through Hong Kong port last quarter?"
        - "port cargo throughput by year"

    Quirks:
        - needs a browser-like User-Agent
        - period for quarterly is YYYYQQ (e.g. 202603 = Q1 2026)
        - empty DIRECTION/SHIPMENT_TYPE = total
        - NEVER use Censtatd report viewer ``wbr.html?download_csv=1`` —
          that flag is a client-side JS action and curl/requests get HTML,
          not CSV. Always use ``api/get.php?id=…`` (this function) for
          programmatic cargo figures; for live vessel movements use
          mardep.vessel_arrivals instead
    """
    import json
    import urllib.request

    url = ("https://www.censtatd.gov.hk/api/get.php"
           "?id=410-55110&lang=en&full_series=1")
    req = urllib.request.Request(
        url, headers={"User-Agent":
                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["dataSet"]
