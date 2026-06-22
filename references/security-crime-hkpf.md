# HKPF Crime Statistics in Detail

## Dataset Info
- **Dataset ID:** `hk-hkpf-stat-crm-stat-detail`
- **URL:** https://data.gov.hk/en-data/dataset/hk-hkpf-stat-crm-stat-detail
- **Provider:** Hong Kong Police Force
- **Category:** Law and Security (`law-and-security` → `security-`)
- **Update Frequency:** As and when necessary

## Description
Hong Kong Police Force crime statistics. The dataset contains two CSV resources:

1. **Crime Statistics in Detail** (`crime_details.csv`) — annual territory-wide crime counts by offence type, in Traditional Chinese + English (Big5 encoded).
2. **Overall Crime and Violent Crime Situation** (`crime_details_overall.csv`) — monthly territory-wide overall and violent crime counts (UTF-8 encoded).

**Important limitation:** Neither resource provides District Council district-level breakdowns. Data is territory-wide only.

## Data Temporality

- **Historical series:** annual detail table from 2014 onwards; monthly overall table from 2022 onwards.
- Update frequency is "As and when necessary" — typically after year-end or mid-year reviews.

## API

**Endpoints:**
- Detail CSV: `https://www.police.gov.hk/info/doc/crime_details.csv`
- Overall CSV: `https://www.police.gov.hk/info/doc/crime_details_overall.csv`
- Data dictionary: `https://www.police.gov.hk/info/psi/meta/Data_Dictionary_for_Crime_Statistics_in_Detail_2020.pdf`

### Parameters

No query parameters. Files are static CSV downloads.

## Examples

```bash
# Overall + violent crime (UTF-8, monthly)
python3 ./scripts/hkdata.py test "https://www.police.gov.hk/info/doc/crime_details_overall.csv"

# Detailed annual crime (Big5 encoded)
python3 ./scripts/hkdata.py test "https://www.police.gov.hk/info/doc/crime_details.csv"
```

## Related Resources

- `hk-censtatd-tablechart-940-92031` — Censtatd mirror of persons-arrested statistics.

## Join Keys

- `Year` (annual detail table)
- `Year` + `Month` (overall table)

## Known Quirks

- `crime_details.csv` is **Big5 encoded**, not UTF-8. The CLI parser may need Big5 fallback to read it.
- CKAN `package_search` does not index "crime" or "violent crime" keywords; use web search fallback to find this dataset.
- No District Council district breakdown is available on data.gov.hk.

## Notes

- Contact: Police Hotline 2527 7177, pr@police.gov.hk
- Use this dataset for territory-wide trend analysis only. For district-level crime questions, no suitable dataset exists on data.gov.hk.

---

**Date Added:** 2026-06-22
