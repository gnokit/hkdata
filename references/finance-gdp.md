# Hong Kong GDP Data

**Dataset ID:** `hk-censtatd-tablechart-310-31001`
**Provider:** Census and Statistics Department (政府統計處)
**Category:** finance

## Description

Gross Domestic Product (GDP), implicit price deflator of GDP and per capita GDP. This dataset provides:
- GDP at current market prices (名義本地生產總值)
- GDP in chained (2023) dollars (以環比物量計算的實質本地生產總值)
- GDP implicit price deflator (本地生產總值內含平減物價指數)
- Per capita GDP (人均本地生產總值)
- Year-on-year percentage changes (按年變動百分率)

## API

**Endpoint:** `https://www.censtatd.gov.hk/api/get.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| id | Yes | Table ID (e.g., `310-31001`) |
| lang | No | Language: `en` (English) or `tc` (Traditional Chinese) |
| full_series | No | Set to `1` to get all historical data |

### Response Fields

| Field | Description |
|-------|-------------|
| freq | Frequency: `Y` (Annual), `Q` (Quarterly) |
| period | Time period (e.g., `2025`, `2025Q1`) |
| sv | Statistical variable code |
| svDesc | Description of the variable |
| figure | The numerical value |
| sd_value | Supplementary data (if any) |

### Statistical Variables (sv codes)

| Code | Description |
|------|-------------|
| CUR | Current market prices (當時市價) |
| CON | Chained (2023) dollars (環比物量 - 實質 GDP) |
| DEF | Implicit price deflator (內含平減物價指數) |
| CURPGDP | Per capita GDP at current prices (人均名義 GDP) |
| CONPGDP | Per capita GDP in chained dollars (人均實質 GDP) |
| SA1 | Seasonally adjusted quarter-to-quarter change (經季節性調整的按季變動百分率) |

## Examples

```bash
# Get all GDP data in English
curl -s "https://www.censtatd.gov.hk/api/get.php?id=310-31001&lang=en&full_series=1"

# Get data in Traditional Chinese
curl -s "https://www.censtatd.gov.hk/api/get.php?id=310-31001&lang=tc&full_series=1"
```

## Python Example

```python
import requests
import json

# Fetch GDP data
url = "https://www.censtatd.gov.hk/api/get.php"
params = {
    "id": "310-31001",
    "lang": "en",
    "full_series": "1"
}

response = requests.get(url, params=params)
data = response.json()

# Extract 2025 growth rate
for item in data['dataSet']:
    if item['freq'] == 'Y' and item['period'] == '2025':
        if item['sv'] == 'CON' and 'change' in item['svDesc'].lower():
            print(f"2025 Real GDP Growth: {item['figure']}%")
```

## Latest Data Snapshot (2025)

| Metric | Value |
|--------|-------|
| Real GDP Growth (實質增長) | 3.5% |
| Nominal GDP Growth (名義增長) | 4.5% |
| Real GDP (2023 chained $) | HK$3,166,305 million |
| Nominal GDP (current prices) | HK$3,331,774 million |
| Per Capita Real GDP | HK$422,236 |
| Per Capita Nominal GDP | HK$444,302 |

## Notes

- **Advance Estimates:** First released figures are called "advance estimates" and are subject to revision
- **Revised Figures:** Figures published after advance estimates are still subject to regular revision
- **Data Quality:** Figures are finalised when data from all regular sources are incorporated
- **Forecast:** The rate of change of GDP in real terms for 2026 is forecast to be 2.5% to 3.5%
- **Contact:** National Income Section (1), Census and Statistics Department
  - Phone: (852) 2582 5077
  - Email: gdp-e@censtatd.gov.hk

---

**Date Added:** 2026-03-13
