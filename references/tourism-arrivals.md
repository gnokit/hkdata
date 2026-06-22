# Visitor Arrivals by Nationality/Region

## Dataset Info
- **Dataset ID:** `hk-censtatd-tablechart-650-80001`
- **URL:** https://data.gov.hk/en-data/dataset/hk-censtatd-tablechart-650-80001
- **Provider:** Census and Statistics Department
- **Category:** Tourism
- **Update Frequency:** Monthly

## Description
Monthly visitor arrivals to Hong Kong by nationality/region. Includes total arrivals and breakdowns such as Chinese Mainland, The Americas, Europe, Africa, Australia/New Zealand/South Pacific, etc.

## Data Temporality

- **Historical series:** monthly data from 2004 onwards
- Typically released with a short lag (e.g., April data available in May/June)

## API

**Endpoint (JSON):**
```
https://www.censtatd.gov.hk/api/get.php?id=650-80001&lang=en&full_series=1
```

**Endpoint (CSV):**
```
https://www.censtatd.gov.hk/en/web_table.html?id=650-80001&full_series=1&download_csv=1
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| id | Yes | Table ID: 650-80001 |
| lang | Yes | en, tc, sc |
| full_series | No | 1 to include all historical data |

## Examples

```bash
# Full historical series JSON
python3 ./scripts/hkdata.py test \
  "https://www.censtatd.gov.hk/api/get.php?id=650-80001&lang=en&full_series=1"
```

## Related Resources

- `hk-cstb-cstb_tc-tc-hotel-room-occupancy-rate` — Hotel room occupancy rate

## Join Keys

- `period` (YYYYMM)
- `REGION` / `REGIONDesc` (e.g., `CN` = Chinese Mainland)

## Known Quirks

- CKAN `package_search` indexes this dataset for "visitor arrivals" but not for "Mainland" or "tourism".
- The `REGION` field uses short codes (`CN`, `AM`, `EU`, etc.) with a separate `REGIONDesc` description.

## Notes

- Contact: vitstat@censtatd.gov.hk

---

**Date Added:** 2026-06-22
