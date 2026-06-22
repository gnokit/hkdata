# Crime Statistics — Persons Arrested (data.gov.hk)

## Dataset Info
- **Dataset ID:** `hk-censtatd-tablechart-940-92031`
- **URL:** https://data.gov.hk/en-data/dataset/hk-censtatd-tablechart-940-92031
- **Provider:** Census and Statistics Department (sourced from Police)
- **Category:** Law and Security
- **Update Frequency:** Annual

## Description
Persons arrested for crime by type of offence, age group and sex. Annual statistics compiled from Hong Kong Police Force records.

## API

**Endpoint (JSON):**
```
https://www.censtatd.gov.hk/api/get.php?id=940-92031&lang=en&full_series=1
```

**Endpoint (CSV):**
```
https://www.censtatd.gov.hk/en/web_table.html?id=940-92031&full_series=1&download_csv=1
```

**Data Dictionary:**
```
https://www.censtatd.gov.hk/datagovhk/WT_data_dict_en.pdf
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| id | Yes | Table ID: 940-92031 |
| lang | Yes | en, tc, sc |
| full_series | No | 1 to include all historical data |
| download_csv | No | 1 to download as CSV |
| download_excel | No | 1 to download as XLSX |

## Examples

```bash
# Full historical series JSON
curl -s "https://www.censtatd.gov.hk/api/get.php?id=940-92031&lang=en&full_series=1" | python3 -m json.tool | head -30

# CSV download
curl -s "https://www.censtatd.gov.hk/en/web_table.html?id=940-92031&full_series=1&download_csv=1" | head -10
```

## Notes

- Data compiled from Hong Kong Police Force
- Age groups typically include: under 10, 10-15, 16-20, 21-30, 31-40, 41-50, 51-60, over 60
- Offence types include: violence against person, criminal damage, burglary, theft, deception, etc.
- Contact: gen-enquiry@censtatd.gov.hk | (852) 3863 2528

---

**Date Added:** 2026-04-30
