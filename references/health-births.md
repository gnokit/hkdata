# Hong Kong Birth Statistics

Official birth data from the Department of Health, including number of known live births by sex and crude birth rate.

**Dataset ID:** `hk-dh-dh_ncddhss-ncdd-dataset-2`
**Provider:** Department of Health
**Category:** health

## Description

Birth Statistics from Department of Health:
- (i) Number of Known Births for Different Sexes and Crude Birth Rate for the Period from 1981 to 2024
- (ii) Percentage Distribution of Live Births by Birth Weight for the Period from 2012 to 2024

## API

**Data Format:** CSV (direct download)

**Endpoint (English):** `https://www.dh.gov.hk/datagovhk/ncdd/Number%20of%20Known%20Births%20for%20Different%20Sexes%20and%20Crude%20Birth%20Rate%201981-2024(en).csv`

### Available Files

| File | Description | Format |
|------|-------------|--------|
| Number of Known Births for Different Sexes and Crude Birth Rate 1981-2024 (English) | Annual births by sex and crude birth rate | CSV |
| Number of Known Births for Different Sexes and Crude Birth Rate 1981-2024 (Traditional Chinese) | Annual births by sex and crude birth rate | CSV |
| Number of Known Births for Different Sexes and Crude Birth Rate 1981-2024 (Simplified Chinese) | Annual births by sex and crude birth rate | CSV |
| Percentage Distribution of Live Births by Birth Weight 2012-2024 (English) | Birth weight distribution | CSV |

## Examples

```bash
# Download birth statistics (English)
curl -s "https://www.dh.gov.hk/datagovhk/ncdd/Number%20of%20Known%20Births%20for%20Different%20Sexes%20and%20Crude%20Birth%20Rate%201981-2024(en).csv"

# Get latest year (2024) total births
curl -s "https://www.dh.gov.hk/datagovhk/ncdd/Number%20of%20Known%20Births%20for%20Different%20Sexes%20and%20Crude%20Birth%20Rate%201981-2024(en).csv" | \
  tail -1 | awk -F',' '{print $3 + $4}'
```

## Data Structure

CSV columns:
- `Year`: Calendar year (1981-2024)
- `Crude Birth Rate (No. of known live births per 1,000 population)`: Birth rate per 1,000 population
- `Male Known Births`: Number of male live births
- `Female Known Births`: Number of female live births

## Recent 5 Years Data (2020-2024)

| Year | Male Births | Female Births | Total Births | Crude Birth Rate |
|------|-------------|---------------|--------------|------------------|
| 2020 | 22,463 | 20,568 | 43,031 | 5.8 |
| 2021 | 18,960 | 17,993 | 36,953 | 5.0 |
| 2022 | 16,838 | 15,663 | 32,501 | 4.4 |
| 2023 | 17,414 | 15,818 | 33,232 | 4.4 |
| 2024 | 19,231 | 17,492 | 36,723 | 4.9 |

## Notes

- Data updated as and when necessary (typically annually)
- "Known births" refers to registered live births where sex is known
- Crude birth rate = (Number of known live births / Mid-year population) × 1,000
- Data source: Department of Health, Non-Communicable Diseases Division

---

**Date Added:** 2026-03-13
