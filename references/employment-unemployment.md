# Dataset: Hong Kong Unemployment Rate

**Dataset ID:** `hk-censtatd-tablechart-210-06401`
**Provider:** Census and Statistics Department
**Category:** Employment and Labour

## Description

Statistics on Labour Force, Unemployment and Underemployment - Table 210-06401: Unemployed persons and unemployment rate by age and sex.

This dataset provides monthly and annual unemployment statistics for Hong Kong, broken down by age groups and sex.

### Key Metrics
- **Unemployment Rate**: Proportion of unemployed persons in the labour force
- **Unemployed Persons**: Number of unemployed individuals (in thousands)

### Update Frequency
Monthly

## API

**Endpoint:** `https://www.censtatd.gov.hk/api/get.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| id | Yes | Table ID: `210-06401` |
| lang | Yes | Language: `en` (English), `tc` (Traditional Chinese), `sc` (Simplified Chinese) |
| full_series | No | Set to `1` to get complete data series |

### Response Structure

The API returns a flat list of records with the following fields:

| Field | Description |
|-------|-------------|
| `AGE` / `AGEDesc` | Age group (e.g., "15-19", "20-24", empty string for total) |
| `SEX` / `SEXDesc` | Sex (M/F, empty string for total) |
| `freq` | Frequency: `Y` (Yearly) or `M` (Monthly) |
| `period` | Time period (YYYY for yearly, YYYYMM for monthly) |
| `sv` / `svDesc` | Statistics variable: `UE` (Unemployed persons), `UR` (Unemployment rate) |
| `figure` | The data value |
| `sd_value` | Standard deviation or provisional flag (`p` = provisional) |

## Examples

```bash
# Get latest unemployment rate data (English)
curl -s "https://www.censtatd.gov.hk/api/get.php?id=210-06401&lang=en&full_series=1"

# Get data in Traditional Chinese
curl -s "https://www.censtatd.gov.hk/api/get.php?id=210-06401&lang=tc&full_series=1"
```

### Python: Get Latest Unemployment Rate

```python
import requests

url = "https://www.censtatd.gov.hk/api/get.php?id=210-06401&lang=en&full_series=1"
data = requests.get(url).json()

# Filter for overall unemployment rate (UR, total age, total sex)
records = [
    r for r in data['dataSet'] 
    if r.get('sv') == 'UR' and r.get('AGE') == '' and r.get('SEX') == ''
]

# Sort by period (most recent first)
records.sort(key=lambda x: x.get('period', ''), reverse=True)

latest = records[0]
print(f"Period: {latest['period']}")
print(f"Unemployment Rate: {latest['figure']}%")
print(f"Provisional: {'Yes' if latest['sd_value'] == 'p' else 'No'}")
```

## Latest Data (as of 2026-03-13)

| Period | Unemployment Rate | Note |
|--------|-------------------|------|
| 2026 Jan | 3.6% | Provisional |
| 2025 Dec | 3.6% | |
| 2025 Nov | 3.8% | |
| 2025 Oct | 3.9% | |
| 2025 Sep | 4.1% | |

## Definitions

**Unemployed Persons:** Persons aged 15 and over who:
1. Have not had a job and have not performed any work for pay or profit during the 7 days before enumeration
2. Have been available for work during the 7 days before enumeration
3. Have sought work during the 30 days before enumeration

**Unemployment Rate:** The proportion of unemployed persons in the labour force.

## Notes

- Monthly figures are 3-month moving averages (e.g., 202601 = Nov 2025 - Jan 2026)
- Figures marked with `p` are provisional and subject to revision
- Annual figures from 2001 onwards are compiled based on survey results from January to December

## Data Dictionary

Full data dictionary available at: https://www.censtatd.gov.hk/datagovhk/WT_data_dict_en.pdf

---

**Date Added:** 2026-03-13
