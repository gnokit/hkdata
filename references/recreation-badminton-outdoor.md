# Badminton Courts (Free Outdoor Pitches/Courts)

**Dataset ID:** `hk-lcsd-facility-facility-bmtc`
**Provider:** Leisure and Cultural Services Department
**Category:** Recreation, Sports and Culture (recreation-and-culture)

## Description

Location data for free outdoor badminton courts managed by LCSD. Covers 14 venues across Hong Kong, including district, address, opening hours, ancillary facilities, and contact information.

## API

**Endpoint:** `https://www.lcsd.gov.hk/datagovhk/facility/facility-bmtc.json`

### Data Fields

| Field (EN) | Field (CN) | Description |
|------------|------------|-------------|
| District_en | District_cn | District name |
| Name_en | Name_cn | Venue name |
| Address_en | Address_cn | Venue address |
| GIHS | - | Geo-reference ID |
| Court_no_en | Court_no_cn | Number of courts |
| Ancillary_facilities_en | Ancillary_facilities_cn | Barrier-free facilities |
| Opening_hours_en | Opening_hours_cn | Opening hours |
| Phone | - | Contact phone |

## Examples

```bash
# Fetch all outdoor badminton courts
curl -s "https://www.lcsd.gov.hk/datagovhk/facility/facility-bmtc.json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for d in data:
    print(f'{d[\"District_cn\"]} {d[\"Name_cn\"]} - {d[\"Address_cn\"]} ({d[\"Court_no_cn\"]})')
"

# Count by district
curl -s "https://www.lcsd.gov.hk/datagovhk/facility/facility-bmtc.json" | python3 -c "
import sys, json
from collections import Counter
data = json.load(sys.stdin)
districts = Counter([d['District_cn'] for d in data])
for dist, count in districts.most_common():
    print(f'{dist}: {count}')
"
```

## Data Summary (as of 2026-03-18)

- **Total venues:** 14 free outdoor courts
- **Districts covered:** 北區 (6), 屯門區 (2), 元朗區 (1), 沙田區 (1), 油尖旺區 (1), 灣仔區 (1), 荃灣區 (1), 葵青區 (1)

## Notes

- All venues are free outdoor pitches/courts
- Some venues share courts with volleyball (排球場連羽毛球場)
- Floodlight availability varies by venue (noted in Opening_hours)
- Update frequency: As and when new facility is added or amendment is made

---

**Date Added:** 2026-03-18
