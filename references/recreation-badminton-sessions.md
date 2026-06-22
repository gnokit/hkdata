# Badminton Court Sessions (Available by Venue)

**Dataset ID:** `hk-lcsd-facility-facility-bmtcvenue`
**Provider:** Leisure and Cultural Services Department
**Category:** Recreation, Sports and Culture (recreation-and-culture)

## Description

Real-time availability of badminton court sessions across all LCSD sports centres. Covers 105 venues across 18 districts, with session times, fees, and booking status. Updates every 5 minutes.

## API

**Endpoint:** `https://data.smartplay.lcsd.gov.hk/rest/cms/api/v1/publ/contents/open-data/badminton/file`

### Data Fields

| Field (EN) | Field (TC) | Description |
|------------|------------|-------------|
| District_Name_EN | District_Name_TC | District name |
| Venue_Name_EN | Venue_Name_TC | Venue/sports centre name |
| Venue_Address_EN | Venue_Address_TC | Full address |
| Venue_Phone_No. | - | Contact number |
| Venue_Longitude | Venue_Latitude | Geo-coordinates |
| Facility_Type_Name_EN | Facility_Type_Name_TC | Court type |
| Facility_Location_Name_EN | Facility_Location_Name_TC | Location within venue |
| Available_Date | - | Session date (YYYY-MM-DD) |
| Session_Start_Time | - | Start time (HH:MM) |
| Session_End_Time | - | End time (HH:MM) |
| Session_Status | - | Booking status |

## Examples

```bash
# Fetch all available sessions
curl -s "https://data.smartplay.lcsd.gov.hk/rest/cms/api/v1/publ/contents/open-data/badminton/file" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f'Total session records: {len(data)}')
print(f'Unique venues: {len(set(d[\"Venue_Name_TC\"] for d in data))}')

# List all unique venues
venues = sorted(set(d['Venue_Name_TC'] for d in data))
for v in venues:
    print(f'  - {v}')
"

# Sessions by district
curl -s "https://data.smartplay.lcsd.gov.hk/rest/cms/api/v1/publ/contents/open-data/badminton/file" | python3 -c "
import sys, json
from collections import Counter
data = json.load(sys.stdin)
districts = Counter([d['District_Name_TC'].strip() for d in data])
for dist, count in sorted(districts.items(), key=lambda x: -x[1]):
    print(f'{dist}: {count} sessions')
"

# Search for available sessions at a specific venue
curl -s "https://data.smartplay.lcsd.gov.hk/rest/cms/api/v1/publ/contents/open-data/badminton/file" | python3 -c "
import sys, json
data = json.load(sys.stdin)
target = '港灣道'
sessions = [d for d in data if target in d['Venue_Name_TC']]
print(f'Sessions at {target}: {len(sessions)}')
for s in sessions[:5]:
    print(f'  {s[\"Available_Date\"]} {s[\"Session_Start_Time\"]}-{s[\"Session_End_Time\"]} - {s[\"Facility_Type_Name_TC\"]}')
"
```

## Data Summary (as of 2026-03-18)

- **Total session records:** 13,664
- **Unique venues:** 105 sports centres
- **Districts:** All 18 districts covered
- **Facility types:**
  - 羽毛球場 (新界區): 6,880 records
  - 羽毛球場 (空調)(市區): 6,656 records
  - 羽毛球場 (市區): 128 records
- **Update frequency:** Every 5 minutes

## Notes

- Covers all LCSD indoor badminton courts (not free outdoor courts)
- Sessions include both available and booked slots
- Urban (市區) courts are air-conditioned (A/C)
- Court fees apply (chargeable venues)
- Data dictionary: https://www.lcsd.gov.hk/datagovhk/facility/facility-bmtcvenue_data_dictionary.pdf

---

**Date Added:** 2026-03-18
