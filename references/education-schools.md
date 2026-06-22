# Education - Number of Day Schools by Type and Region

**Dataset ID:** `hk-censtatd-tablechart-925-92023`
**Provider:** Census and Statistics Department
**Category:** Education

## Description

Provides the number of day schools in Hong Kong by school type/sector and region. Includes data on:
- Kindergartens (KG)
- Primary schools (PS) - government, aided, private, Direct Subsidy Scheme
- Secondary schools (SS) - day schools by sector

Data is available annually from 2013 onwards, broken down by:
- School type (kindergarten, primary, secondary)
- Sector (public sector, private, Direct Subsidy Scheme)
- Region (Hong Kong Island, Kowloon, New Territories)

## API

**Endpoint:** `https://www.censtatd.gov.hk/api/get.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| id | Yes | Table number (925-92023) |
| lang | Yes | Language: `en` (English), `tc` (Traditional Chinese), `sc` (Simplified Chinese) |
| full_series | No | Set to `1` to retrieve full time series |
| period | No | Year range (e.g., `2020,2024` for 2020-2024) |

### Response Fields

| Field | Description |
|-------|-------------|
| TYPE_INS_SCHOOL | School type code (KG, PS, SS_DAY, etc.) |
| TYPE_INS_SCHOOLDesc | School type description |
| DC | District code (HK, KLN, NT, or empty for total) |
| DCDesc | District description |
| period | Year |
| figure | Number of schools |

## Examples

```bash
# Get full time series (English)
curl -s "https://www.censtatd.gov.hk/api/get.php?id=925-92023&lang=en&full_series=1"

# Get specific year range
curl -s "https://www.censtatd.gov.hk/api/get.php?id=925-92023&lang=en&period=2020,2024"

# Get Traditional Chinese version
curl -s "https://www.censtatd.gov.hk/api/get.php?id=925-92023&lang=tc&full_series=1"
```

## Sample Data

**Primary Schools in Hong Kong (2024):**
- Total: 590
- Public sector: 453
- Private: 116
- Direct Subsidy Scheme: 21

**Historical Trend:**
- 2024: 590
- 2023: 594
- 2022: 593
- 2021: 591
- 2020: 589

## Notes

- **Update Frequency:** Annual
- **Source:** Education Bureau, Government Secretariat
- **Regions** are delineated by the locations of the main campuses of schools
- **Public sector primary schools** include government and aided primary schools
- **Private schools** include international schools and other private schools
- All kindergartens are privately run
- Enquiries: edstat@edb.gov.hk | 3509 8437

## Data Dictionary

Full data dictionary available at: https://www.censtatd.gov.hk/datagovhk/WT_data_dict_en.pdf

---

**Date Added:** 2026-03-13
