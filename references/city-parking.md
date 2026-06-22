# Government Car Parks Open for Public Use (data.gov.hk)

## Dataset Info
- **Dataset ID:** `hk-gpa-msd-gpa-psi-t-cp`
- **URL:** https://data.gov.hk/en-data/dataset/hk-gpa-msd-gpa-psi-t-cp
- **Provider:** Government Property Agency (GPA)
- **Category:** City Management
- **Update Frequency:** As and when there are changes to data

## Description
Location, address, and number of car parking spaces by type for all Government car parks open for public use under the purview of the Government Property Agency. Includes EV charger counts and parking fee information.

## API

**Endpoint (English JSON):**
```
https://www.gpa.gov.hk/doc/psi/ds/psi-t-cp_ENG.json
```

**Endpoint (English CSV):**
```
https://www.gpa.gov.hk/doc/psi/ds/psi-t-cp_ENG.csv
```

**Data Dictionary:**
```
https://www.gpa.gov.hk/doc/psi/dd/DataDictionary-t-cp_ENG.pdf
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| lang | No | `ENG`, `TC`, `SC` for language variants |
| format | No | `.json` or `.csv` |

## Examples

```bash
# English JSON
curl -s "https://www.gpa.gov.hk/doc/psi/ds/psi-t-cp_ENG.json" | python3 -m json.tool | head -30

# English CSV
curl -s "https://www.gpa.gov.hk/doc/psi/ds/psi-t-cp_ENG.csv" | head -5
```

## Notes

- JSON response may include a UTF-8 BOM; strip first 3 bytes if parsing fails
- Fields include: Car Park Name, District, Address, Vehicle Type, Size, Height Restriction, Opening Hours, EV Chargers, Parking Fees
- Some car parks are only open night-time on weekdays, 24h on weekends
- Contact: Ms. TSE Lai Ping | plptse@gpa.gov.hk

---

**Date Added:** 2026-04-30
