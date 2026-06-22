# Monthly Traffic and Transport Digest (CSV) (data.gov.hk)

## Dataset Info
- **Dataset ID:** `hk-td-tis_17-monthly-traffic-and-transport-digest-csv`
- **URL:** https://data.gov.hk/en-data/dataset/hk-td-tis_17-monthly-traffic-and-transport-digest-csv
- **Provider:** Transport Department (TD)
- **Category:** Transport
- **Update Frequency:** MONTHLY

## Description
Comprehensive monthly statistics on Hong Kong's transport system, including passenger journeys by public transport operator, vehicle registration and licensing, driving licences, vehicle inspection, road traffic accidents, tunnel traffic flows, and cross-boundary vehicular traffic.

## API

**Base URL:**
```
https://www.td.gov.hk/datagovhk_tis/mttd-csv/en/
```

**Key Tables (English CSV):**

| Table | Description |
|-------|-------------|
| `DATA_LAST_REVISION_DATE_eng.csv` | Last revision date of the dataset |
| `table11_eng.csv` | Passenger journeys by public transport operator |
| `table21s_eng.csv` | Vehicle registration and licensing |
| `table31a-31d_eng.csv` | Driving licences |
| `table32a-32q_eng.csv` | Vehicle inspection and examination |
| `table41a-41h_eng.csv` | Road traffic accidents |
| `table51a-51f_eng.csv` | Traffic flows through tunnels |
| `table61-63_eng.csv` | Cross-boundary vehicular traffic |
| `table71-73_eng.csv` | Vehicle registration by fuel type |
| `table81a-81f_eng.csv` | Public transport patronage |
| `table91-93_eng.csv` | Licensed vehicles by class |

**Data Dictionary:**
```
https://www.td.gov.hk/datagovhk_tis/mttd-csv/en/mttd_dataspec_eng.pdf
```

## Examples

```bash
# Last revision date
curl -s "https://www.td.gov.hk/datagovhk_tis/mttd-csv/en/DATA_LAST_REVISION_DATE_eng.csv"

# Passenger journeys by operator
curl -s "https://www.td.gov.hk/datagovhk_tis/mttd-csv/en/table11_eng.csv" | head -10

# Road traffic accidents
curl -s "https://www.td.gov.hk/datagovhk_tis/mttd-csv/en/table41a_eng.csv" | head -10
```

## Notes

- ~100 CSV files per language (EN/TC/SC)
- Updated monthly; revision date available in `DATA_LAST_REVISION_DATE_eng.csv`
- Historical data available through full_series parameter on some tables
- Contact: tdenq@td.gov.hk

---

**Date Added:** 2026-04-30
