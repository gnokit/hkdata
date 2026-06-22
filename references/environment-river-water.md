# Recent River Water Quality Data (data.gov.hk)

## Dataset Info
- **Dataset ID:** `hk-epd-riverteam-river-water-quality-recent-data`
- **URL:** https://data.gov.hk/en-data/dataset/hk-epd-riverteam-river-water-quality-recent-data
- **Provider:** Environmental Protection Department (EPD)
- **Category:** Environment
- **Update Frequency:** Every mid of month

## Description
Recent Dissolved Oxygen (DO) and 5-day Biochemical Oxygen Demand (BOD5) data at downstream monitoring stations of major rivers in Hong Kong. Data covers 04/2024 to 03/2026.

## API

**Endpoint (English CSV):**
```
https://cd.epic.epd.gov.hk/riverpsi/en/riverrecent/river-recent-en.csv
```

**Data Dictionary:**
```
https://cd.epic.epd.gov.hk/riverpsi/recent_river_data_dictionary_en.pdf
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| lang | No | `en`, `tc`, `sc` for language variants |

## Examples

```bash
# English CSV
curl -s "https://cd.epic.epd.gov.hk/riverpsi/en/riverrecent/river-recent-en.csv" | head -10

# Traditional Chinese CSV
curl -s "https://cd.epic.epd.gov.hk/riverpsi/tc/riverrecent/river-recent-tc.csv" | head -10
```

## Notes

- Monitors all major river systems across Hong Kong
- Water Control Zones include: Deep Bay, Victoria Harbour, Tolo Harbour, etc.
- Key metrics: Dissolved Oxygen (mg/L) and 5-Day BOD (mg/L)
- Contact: enquiry@epd.gov.hk | 2838 3111

---

**Date Added:** 2026-04-30
