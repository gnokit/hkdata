"""Census and Statistics Department — labour force / unemployment."""


def unemployment_rate() -> list:
    """Hong Kong unemployment rate and unemployed persons, by age/sex.

    Provides:
        - unemployment rate (%) and unemployed persons, broken down by age
          group and sex, monthly + annual

    Coverage:
        - Geography: HK-wide
        - Time:      historical series, monthly (YYYYMM) + annual

    Datasets:   hk-censtatd-tablechart-210-06401
    Department: Census and Statistics Department
    Endpoint:   https://www.censtatd.gov.hk/api/get.php?id=210-06401&lang=en&full_series=1
    Format:     JSON

    Usage:
        >>> rows = unemployment_rate()        # list[dict]
        >>> [r for r in rows if r["sv"] == "UR"]

    Questions:
        - "what is Hong Kong's unemployment rate?"
        - "unemployment rate by age group"

    Quirks:
        - needs a browser-like User-Agent
        - sv codes: UE (unemployed persons), UR (unemployment rate %)
        - empty AGE/SEX means total
        - territory-wide only — District Council unemployment rate is NOT
          published (GHS sample too small). For district labour stats use
          labour_force_by_district (LF / LFPR only; LFPR ≠ UR)
    """
    import json
    import urllib.request

    url = ("https://www.censtatd.gov.hk/api/get.php"
           "?id=210-06401&lang=en&full_series=1")
    req = urllib.request.Request(
        url, headers={"User-Agent":
                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["dataSet"]


def labour_force_by_district() -> list:
    """Labour force and participation rate (LFPR) by district, annual.

    Provides:
        - labour force ('000) and LFPR (%) by District Council district,
          by sex and age group

    Coverage:
        - Geography: 18 districts + total
        - Time:      historical series, annual

    Datasets:   hk-censtatd-tablechart-210-06821
    Department: Census and Statistics Department
    Endpoint:   https://www.censtatd.gov.hk/api/get.php?id=210-06821&lang=en&full_series=1
    Format:     JSON

    Usage:
        >>> rows = labour_force_by_district() # list[dict]
        >>> [r for r in rows if r["sv"] == "LFPR"]

    Questions:
        - "labour force participation rate by district"

    Quirks:
        - needs a browser-like User-Agent
        - sv codes: LF (labour force '000), LFPR (participation rate %)
        - DC codes A-T map to districts (A=Central and Western, ..., T=Islands)
        - district labels use "and" (Central and Western) — Housing Authority
          / EDB often use "&"; normalise before joins
        - this is NOT unemployment by district; say so if the user asked for UR
    """
    import json
    import urllib.request

    url = ("https://www.censtatd.gov.hk/api/get.php"
           "?id=210-06821&lang=en&full_series=1")
    req = urllib.request.Request(
        url, headers={"User-Agent":
                      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["dataSet"]
