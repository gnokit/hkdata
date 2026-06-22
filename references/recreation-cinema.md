# Hong Kong Cinemas (data.gov.hk)

## Dataset Info
- **Dataset ID:** `hk-cstb-cstb_ccida-hkcinemas`
- **URL:** https://data.gov.hk/en-data/dataset/hk-cstb-cstb_ccida-hkcinemas
- **Provider:** Culture, Sports and Tourism Bureau (Create Hong Kong)
- **Category:** Recreation and Culture
- **Update Frequency:** QUARTERLY

## Description
Complete inventory of cinemas in Hong Kong including name, address, number of screens, number of seats, website, contact information, and geographical coordinates (longitude/latitude and HK1980 grid coordinates).

## API

**Endpoint (CSV):**
```
https://www.ccidahk.gov.hk/data/hkcinemas.csv
```

**Geospatial API:**
```
https://portal.csdi.gov.hk/geoportal/?datasetId=cstb_rcd_1639635441187_63023
```

### Fields

| Field | Description |
|-------|-------------|
| Reference | Unique cinema ID (e.g., Cinema001) |
| Name_EN / Name_TC / Name_SC | Cinema name in three languages |
| Address_EN / Address_TC / Address_SC | Full address |
| No_Screen | Number of screens |
| No_Seat | Total seating capacity |
| Website | Official website URL |
| Contact_Information | Phone number |
| Last_Update | Data last updated date |
| longitude_lands / latitude_lands | WGS84 coordinates |
| easting_lands / northing_lands | HK1980 grid coordinates |

## Examples

```bash
# Download full cinema list
curl -s "https://www.ccidahk.gov.hk/data/hkcinemas.csv" | head -10

# Count total cinemas
curl -s "https://www.ccidahk.gov.hk/data/hkcinemas.csv" | wc -l

# Find cinema by name
curl -s "https://www.ccidahk.gov.hk/data/hkcinemas.csv" | grep -i "mongkok"
```

## Notes

- 60+ cinemas listed as of last update (31/03/2026)
- Major circuits: Broadway Circuit, PALACE, MOViE MOViE, MY CINEMA, B+ cinema, MCL, Emperor, Golden Harvest
- Largest venue: MY CINEMA YOHO MALL (8 screens, 1,211 seats)
- Contact: Create Hong Kong

---

**Date Added:** 2026-04-30
