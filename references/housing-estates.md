# Public Housing Estates Inventory

Location and profile of all Hong Kong Housing Authority public housing estates, including Public Rental Housing (PRH), HOS/PSPS/GSH courts, shopping centres, and flatted factories.

**Dataset ID:** `hk-housing-eslocator-eslocator`
**Provider:** Hong Kong Housing Authority
**Category:** housing

## API

**Endpoint (JSON API):** `https://data.housingauthority.gov.hk/psi/rest/export/prh-estates`

**Static JSON (also available):** `https://www.housingauthority.gov.hk/datagovhk/prh-estates.json`

### Response Structure

Returns `{"data": [...]}` where each record has:

| Field | Description |
|-------|-------------|
| `Estate_Name` | Estate name (English) |
| `District_Name` | District name (e.g., "Kwun Tong", "Central & Western") |
| `Region_Name` | Region: "Hong Kong", "Kowloon", or "New Territories" |
| `Type_of_Estate` | "Public Rental Housing", "HOS/PSPS/GSH Courts", etc. |
| `Year_of_Intake` | Year(s) of intake |
| `No_of_Blocks` | Number of blocks |
| `No_of_Rental_Flats` | Number of rental flats |
| `Map_Latitude` / `Map_Longitude` | GPS coordinates |
| `Type_of_Block` | Block type (e.g., "Non-standard", "Cruciform") |

### District Name Normalization

PRH API uses `&` (e.g., "Central & Western") while Censtatd uses `and` (e.g., "Central and Western"). Normalize by replacing `&` with `and` before joining.

### Related Resources

| Resource | URL |
|----------|-----|
| HOS/PSPS/GSH Courts API | `https://data.housingauthority.gov.hk/psi/rest/export/hos-courts` |
| HA Shopping Centres API | `https://data.housingauthority.gov.hk/psi/rest/export/shopping-centres` |
| HA Flatted Factories API | `https://data.housingauthority.gov.hk/psi/rest/export/flatted-factory` |

## Examples

```bash
# Fetch all PRH estates and count by district
curl -s "https://data.housingauthority.gov.hk/psi/rest/export/prh-estates" | python3 -c "
import sys, json
from collections import Counter
data = json.load(sys.stdin)
prh = [e for e in data['data'] if e['Type_of_Estate'] == 'Public Rental Housing']
counts = Counter(e['District_Name'] for e in prh)
for dc, c in counts.most_common():
    print(f'{dc}: {c}')
"
```

## Notes

- Total PRH estates: 197 (as of 2026-06-22)
- Total all estate types (including HOS, shopping centres, factories): 241
- Districts with 0 PRH estates: Wan Chai, Yau Tsim Mong
- Update frequency: "As and when there are new entries or records"
- District names use `&` not `and` — normalize before joining with Censtatd data

---

**Date Added:** 2026-06-22
