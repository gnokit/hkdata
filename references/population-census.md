# Hong Kong Population Statistics

Official population data by District Council district from Census and Statistics Department.

**Dataset ID:** `hk-censtatd-tablechart-110-02001`
**Provider:** Census and Statistics Department
**Category:** population

## Description

Land area, land population, and population density by District Council district. Updated annually with mid-year population estimates.

## API

**Endpoint:** `https://www.censtatd.gov.hk/api/get.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Table ID: `110-02001` |
| `lang` | Yes | Language: `en` (English), `tc` (Traditional Chinese), `sc` (Simplified Chinese) |
| `full_series` | Yes | Set to `1` to get all historical data |

## Examples

```bash
# Get all population data (English)
curl -s "https://www.censtatd.gov.hk/api/get.php?id=110-02001&lang=en&full_series=1"

# Get latest total population (2024)
curl -s "https://www.censtatd.gov.hk/api/get.php?id=110-02001&lang=en&full_series=1" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); \
  print([r for r in d['dataSet'] if r['period']=='2024' and r['DC']=='' and \"('000)\" in r['svDesc']][0]['figure']*1000)"
```

## Data Structure

Each record contains:
- `DC`: District code (e.g., "A" = Central and Western, "" = Total)
- `DCDesc`: District name
- `period`: Year (e.g., "2024")
- `svDesc`: Data type:
  - `(sq. km)` - Land area
  - `('000)` - Population in thousands
  - `(Persons per sq. km)` - Population density
- `figure`: Numeric value

## Latest Data (2024)

**Total Hong Kong Population:** 7,523,000 (mid-2024)

## Related Datasets

- `hk-censtatd-tablechart-110-06811` — Population by District Council district, sex and age (broad age groups: 0-14, 15-24, etc.). Useful as a denominator for district-level per-capita calculations.

## Notes

- Population figures are mid-year estimates
- Data available from 2002 to present
- District boundaries changed in 2016 (Wan Chai and Eastern districts)
- Excludes marine population and reservoir areas
- Table `110-06811` only provides broad age groups; single-year age (e.g., 5-year-olds) is not available on data.gov.hk

---

**Date Added:** 2026-03-13
