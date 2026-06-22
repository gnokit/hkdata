# Primary School Enrolment and Accommodation (EDB)

## Dataset Info

### Student Enrolment by District and Grade
- **Dataset ID:** `hk-edb-figustat-stu-pri-dis-gra`
- **Provider:** Education Bureau
- **Category:** Education
- **Update Frequency:** Yearly
- **Description:** Student enrolment in primary schools by District Council district and grade (P1–P6).

### Operating Classes, Accommodation, Enrolment and Repeaters by Grade
- **Dataset ID:** `hk-edb-figustat-ope-acc-stu-rep-pri-gra`
- **Provider:** Education Bureau
- **Category:** Education
- **Update Frequency:** Yearly
- **Description:** Territory-wide operating classes, accommodation (capacity/places), enrolment and repeaters in primary schools by grade.

## Data Temporality

- **Historical series:** annual figures, typically for the most recent school year
- **Static inventory-style** update: EDB publishes a new file each year

## API

**Endpoints (CSV):**
- Student enrolment by district and grade: `http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0307_en.csv`
- Operating classes / accommodation / enrolment / repeaters by grade: `http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0301_en.csv`

### Parameters

No query parameters. Files are static CSV downloads hosted on edb.gov.hk.

## Examples

```bash
# Enrolment by district and grade
python3 ./scripts/hkdata.py test \
  "http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0307_en.csv"

# Territory-wide accommodation / enrolment by grade
python3 ./scripts/hkdata.py test \
  "http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0301_en.csv"
```

## Related Resources

- `hk-censtatd-tablechart-110-06811` — Population by District Council district, sex and age (needed for child-population denominator)
- `hk-censtatd-tablechart-925-92023` — Number of day schools by type and region

## Join Keys

- `District` (EDB names use `&`, e.g., `Central & Western`)
- `Grade` / `P1` for Primary One

## Known Quirks

- District names in EDB CSVs use `&` (e.g., `Central & Western`) while Censtatd uses `and` (`Central and Western`). Normalize before joining.
- `tab0307_en.csv` has a trailing space in the `Kwai Tsing` row label.
- These datasets provide **enrolment**, not **places/capacity**. For district-level "places", enrolment is usually used as a proxy because public-sector schools are generally fully utilised.
- The accommodation/capacity figure is only available **territory-wide** in `tab0301_en.csv`, not by district.

## Notes

- Contact: edstat@edb.gov.hk | 3509 8437

---

**Date Added:** 2026-06-22
