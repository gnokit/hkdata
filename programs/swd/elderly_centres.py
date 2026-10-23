"""Social Welfare Department — elderly centres inventory."""


def elderly_centres() -> list:
    """SWD elderly centres (NEC) — name, agency, district, address, contact.

    Provides:
        - centre name (tc/en), operating agency, district, address, phone,
          fax, email, remarks

    Coverage:
        - Geography: 172 Neighbourhood Elderly Centres across all districts
        - Time:      static inventory, updated as data changes

    Datasets:   hk-swd-elderly-list-of-neighbourhood-elderly-centres
    Department: Social Welfare Department
    Endpoint:   https://www.swd.gov.hk/datagovhk/elderly/list-of-neighbourhood-elderly-centres.csv
    Format:     CSV (UTF-16-LE, tab-delimited)

    Usage:
        >>> rows = elderly_centres()          # list[list] (UTF-16 tab CSV)

    Questions:
        - "elderly centres in Kwun Tong"
        - "neighbourhood elderly centres by district"

    Quirks:
        - UTF-16-LE encoded and TAB-delimited despite the .csv extension
          (not UTF-8 comma CSV) — decode utf-16, strip BOM, delimiter='\\t'
        - related: DE/DCU (List-of-DE-DCU.csv), STE (List-of-STE.csv) — same format
        - Chinese keyword catalog hits for 長者 are unreliable; prefer English
          synonyms (elderly / neighbourhood elderly centre) or this program
    """
    import csv
    import io
    import urllib.request

    url = ("https://www.swd.gov.hk/datagovhk/elderly/"
           "list-of-neighbourhood-elderly-centres.csv")
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-16-le").lstrip("\ufeff")
    return list(csv.reader(io.StringIO(text), delimiter="\t"))
