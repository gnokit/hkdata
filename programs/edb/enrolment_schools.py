"""Education Bureau — primary enrolment and accommodation."""


def primary_enrolment_by_district() -> list:
    """Primary school student enrolment by district and grade (P1–P6).

    Provides:
        - student enrolment in primary schools by District Council district
          and grade, for the latest school year

    Coverage:
        - Geography: by District Council district
        - Time:      annual, most recent school year

    Datasets:   hk-edb-figustat-stu-pri-dis-gra
    Department: Education Bureau
    Endpoint:   http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0307_en.csv
    Format:     CSV

    Usage:
        >>> rows = primary_enrolment_by_district()  # list[dict]

    Questions:
        - "primary school enrolment by district"
        - "P1 intake by district"

    Quirks:
        - UTF-8 with BOM — decode utf-8-sig
        - district names use "&" (Central & Western); normalise to "and" for joins
        - "Kwai Tsing" row label has a trailing space
        - enrolment ≠ places allocation; exact 5-year-old / primary-places
          demand by district is not published — use this enrolment table +
          Censtatd age/district population as proxies and say so
    """
    import csv
    import io
    import urllib.request

    url = ("http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/"
           "figures/tab0307_en.csv")
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def primary_accommodation() -> list:
    """Operating classes, accommodation, enrolment and repeaters by grade.

    Provides:
        - territory-wide operating classes, accommodation (places), enrolment,
          and repeaters in primary schools, by grade

    Coverage:
        - Geography: territory-wide (not by district)
        - Time:      annual

    Datasets:   hk-edb-figustat-ope-acc-stu-rep-pri-gra
    Department: Education Bureau
    Endpoint:   http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0301_en.csv
    Format:     CSV

    Usage:
        >>> rows = primary_accommodation()    # list[dict]

    Questions:
        - "how many primary school places are there?"
        - "primary capacity by grade"

    Quirks:
        - capacity/accommodation is territory-wide only (no district split)
        - UTF-8 with BOM
    """
    import csv
    import io
    import urllib.request

    url = ("http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/"
           "figures/tab0301_en.csv")
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def day_schools_by_sector() -> list:
    """Number of day schools by level and sector, wide format (2015–2025).

    Provides:
        - day-school counts by level (kindergarten/primary/secondary/special)
          and sector (government/aided/DSS/private/international), years as columns

    Coverage:
        - Geography: territory-wide
        - Time:      annual, wide format 2015–2025

    Datasets:   hk-edb-figustat-day-sch-lev-sec
    Department: Education Bureau
    Endpoint:   http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0101_en.csv
    Format:     CSV

    Usage:
        >>> rows = day_schools_by_sector()    # list[dict] (wide: years = columns)

    Questions:
        - "how many schools are closing?"
        - "school count by level and sector"

    Quirks:
        - wide format: years are columns, parse by header
        - UTF-8 with BOM + CRLF — decode utf-8-sig
        - no dataset enumerates individual school closures / 殺校名單 —
          proxy via historical-archive diffs of SchoolBasicInfo.xml
          SchoolNumber sets + these net counts; verify names against
          EDB/LegCo (see data/unavailable.jsonl)
    """
    import csv
    import io
    import urllib.request

    url = ("http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/"
           "figures/tab0101_en.csv")
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))


def student_enrolment_by_sector() -> list:
    """Student enrolment in day schools by level and sector (2015–2025).

    Provides:
        - student enrolment by level (kindergarten/primary/secondary/special)
          and sector, years as columns

    Coverage:
        - Geography: territory-wide
        - Time:      annual, wide format 2015–2025

    Datasets:   hk-edb-figustat-stu-day-sch-lev-sec
    Department: Education Bureau
    Endpoint:   http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0103_en.csv
    Format:     CSV

    Usage:
        >>> rows = student_enrolment_by_sector()  # list[dict]

    Questions:
        - "student enrolment trend by level"
        - "kindergarten enrolment decline"

    Quirks:
        - wide format; UTF-8 with BOM
    """
    import csv
    import io
    import urllib.request

    url = ("http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/"
           "figures/tab0103_en.csv")
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        text = resp.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text)))
