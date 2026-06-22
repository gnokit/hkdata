# Dataset: Consumer Price Index (CPI) - Seasonally Adjusted

**Dataset ID:** `hk-censtatd-tablechart-510-60004`
**Provider:** Census and Statistics Department (C&SD)
**Category:** Commerce and Industry

## Description

This dataset provides monthly seasonally adjusted Consumer Price Index (CPI) figures for Hong Kong. The CPI measures changes in the price level of a market basket of consumer goods and services purchased by households over time. It is the primary indicator of inflation in Hong Kong.

Key indices included:
- **Composite CPI**: Overall consumer price index covering all households
- **Underlying inflation rate**: CPI excluding effects of government one-off relief measures
- **Seasonally adjusted CPI**: Adjusted for seasonal patterns

## API

**Endpoint:** `https://www.censtatd.gov.hk/api/get.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Table number: `510-60004` |
| `lang` | Yes | Language: `EN` (English), `TC` (Traditional Chinese), `SC` (Simplified Chinese) |
| `full_series` | No | Set to `1` to retrieve full historical series |

### Headers

No special headers required.

## Examples

```bash
# Get CPI data in English
curl -s "https://www.censtatd.gov.hk/api/get.php?id=510-60004&lang=en"

# Get full historical series
curl -s "https://www.censtatd.gov.hk/api/get.php?id=510-60004&lang=en&full_series=1"

# Get data in Traditional Chinese
curl -s "https://www.censtatd.gov.hk/api/get.php?id=510-60004&lang=tc"
```

## Latest Data

**January 2026:**
- Composite CPI: **110.0** (index points, October 2019 - September 2020 = 100)
- Year-on-year change: **+1.1%**
- Underlying inflation rate: **+1.0%**
- Release date: February 25, 2026

## Notes

- **Update frequency:** Monthly (usually released around the 20th-25th of the following month)
- **Base period:** October 2019 - September 2020 = 100
- The underlying CPI series nets out the effects of government's one-off relief measures
- CPI includes nine commodity/service sections: food, housing, electricity/gas/water, alcoholic drinks/tobacco, clothing/footwear, durable goods, miscellaneous goods, transport, and miscellaneous services
- For detailed breakdowns and non-seasonally adjusted data, refer to additional C&SD tables

## Data Quality

- **Source reliability:** Official statistics from Hong Kong SAR Government
- **Methodology:** Follows international standards for CPI compilation
- **Historical coverage:** Data available from October 2019 (current series)

## Related Resources

- **Data Dictionary:** https://www.censtatd.gov.hk/datagovhk/WT_data_dict_en.pdf
- **Official website:** https://www.censtatd.gov.hk/
- **Contact:** cpi@censtatd.gov.hk / (852) 3903 7374

---

**Date Added:** 2026-03-13
