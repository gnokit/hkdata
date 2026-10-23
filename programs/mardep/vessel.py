"""Marine Department — vessel arrivals and departures."""


def vessel_arrivals(feed: str = "arrived") -> list:
    """Ocean-going vessel arrivals/departures at Hong Kong port (real-time).

    Provides:
        - call sign, vessel name, ship type, agent, current location,
          arrival time, remark — per vessel

    Coverage:
        - Geography: HK port
        - Time:      real-time snapshot, updated every 20 min (last 36 h)

    Datasets:   hk-md-mardep-vessel-arrivals-and-departures
    Department: Marine Department
    Endpoint:   https://www.mardep.gov.hk/e_files/en/opendata/{code}.XML
    Format:     XML

    Usage:
        >>> vessels = vessel_arrivals("arrived")  # list[dict]
        >>> [v for v in vessels if "CONTAINER" in v["SHIP_TYPE"]]

    Questions:
        - "which container ships arrived in the last 36 hours?"
        - "vessels in port now"

    Quirks:
        - feed codes: arrived=RP05005i, due=RP04005i, inport=RP06005i, departed=RP05505i
        - XML, not JSON — parse with xml.etree; one <G_SQL1> per vessel
        - snapshot only (36 h), not historical monthly aggregates — there is
          no programmatic monthly vessel-arrival count API; for cargo tonnage
          trends use censtatd port_cargo_throughput (JSON API), not Censtatd
          wbr.html CSV download
    """
    import urllib.request
    import xml.etree.ElementTree as ET

    feeds = {
        "arrived": "RP05005i",
        "due": "RP04005i",
        "inport": "RP06005i",
        "departed": "RP05505i",
    }
    code = feeds.get(feed, feed)
    url = f"https://www.mardep.gov.hk/e_files/en/opendata/{code}.XML"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read().decode("utf-8"))
    out = []
    for node in root.iter("G_SQL1"):
        out.append({child.tag: (child.text or "").strip() for child in node})
    return out
