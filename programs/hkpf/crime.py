"""Hong Kong Police Force — crime statistics."""


def crime_overall() -> list:
    """Overall and violent crime counts, monthly (territory-wide, UTF-8).

    Provides:
        - monthly overall crime and violent crime counts

    Coverage:
        - Geography: territory-wide only (no district breakdown)
        - Time:      monthly from 2022

    Datasets:   hk-hkpf-stat-crm-stat-detail
    Department: Hong Kong Police Force
    Endpoint:   https://www.police.gov.hk/info/doc/crime_details_overall.csv
    Format:     CSV (UTF-8)

    Usage:
        >>> rows = crime_overall()            # list[dict]

    Questions:
        - "what is the monthly crime trend?"
        - "violent crime by month"

    Quirks:
        - territory-wide only; no District Council breakdown (violent crime
          by district) exists on data.gov.hk — say so; do not invent a join
        - older CKAN package_search often missed "crime" keywords; prefer
          this program / catalog-search over raw CKAN
    """
    import csv
    import io
    import urllib.request

    url = "https://www.police.gov.hk/info/doc/crime_details_overall.csv"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def crime_detail() -> list:
    """Annual crime counts by offence type (territory-wide, Big5 encoded).

    Provides:
        - annual crime counts broken down by offence type, from 2014

    Coverage:
        - Geography: territory-wide only
        - Time:      historical series, annual

    Datasets:   hk-hkpf-stat-crm-stat-detail
    Department: Hong Kong Police Force
    Endpoint:   https://www.police.gov.hk/info/doc/crime_details.csv
    Format:     CSV (Big5)

    Usage:
        >>> rows = crime_detail()             # list[list] (Big5, positional)

    Questions:
        - "crime statistics by offence type"

    Quirks:
        - Big5 encoded, not UTF-8 — decode 'big5'
        - no district breakdown
    """
    import csv
    import io
    import urllib.request

    url = "https://www.police.gov.hk/info/doc/crime_details.csv"
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("big5")
    return list(csv.reader(io.StringIO(text)))
