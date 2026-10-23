"""Hong Kong Housing Authority — estate inventory."""


def prh_estates() -> list:
    """Public housing estates (PRH, HOS, courts, shopping centres, factories).

    Provides:
        - estate name, district, region, type, year of intake, blocks,
          rental flats, and GPS coordinates

    Coverage:
        - Geography: all districts (district uses "&" form)
        - Time:      static inventory, updated as entries change

    Datasets:   hk-housing-eslocator-eslocator
    Department: Hong Kong Housing Authority
    Endpoint:   https://data.housingauthority.gov.hk/psi/rest/export/prh-estates
    Format:     JSON

    Usage:
        >>> estates = prh_estates()           # list[dict] (197 PRH + others)
        >>> [e for e in estates if e["Type_of_Estate"] == "Public Rental Housing"]

    Questions:
        - "how many public housing estates are in Kwun Tong?"
        - "list PRH estates by district"

    Quirks:
        - district names use "&" (Central & Western) — Censtatd / many C&SD
          tables use "and"; always ``replace("&", "and")`` (and strip spaces
          consistently) before any HA↔Censtatd join
        - related PSI exports: hos-courts, shopping-centres, flatted-factory
    """
    import json
    import urllib.request

    url = "https://data.housingauthority.gov.hk/psi/rest/export/prh-estates"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["data"]
