# Hong Kong Public Holidays Data

**Dataset ID:** `hk-dpo-statistic-cal`
**Provider:** Digital Policy Office (1823 Contact Centre)
**Category:** city (City Management and Utilities)

## Description

Official Hong Kong public holidays data for 2024-2026, provided by the 1823 Contact Centre. Contains dates and names of all statutory holidays in Hong Kong.

## Data Resources

| Language | Resource ID | URL |
|----------|------------|-----|
| English | `1f7326e6-0546-46d3-ad90-6dd1ab8cb1bc` | `https://www.1823.gov.hk/common/ical/en.json` |
| Traditional Chinese | `f37856b7-1b77-40f5-b183-806dc40673fb` | `https://www.1823.gov.hk/common/ical/tc.json` |
| Simplified Chinese | `c245089d-0566-474d-8fd8-e0fadb076da2` | `https://www.1823.gov.hk/common/ical/sc.json` |

## Data Format

iCal JSON format. Extract `vcalendar[0].vevent` array. Each event contains:
- `dtstart`: Holiday date (YYYYMMDD format, with `{"value": "DATE"}`)
- `summary`: Holiday name in the respective language

## Example

```bash
# Fetch English holidays
curl -s "https://www.1823.gov.hk/common/ical/en.json" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for e in data['vcalendar'][0]['vevent']:
    date = e['dtstart'][0]
    name = e['summary']
    print(f'{date}: {name}')
"
```

## Notes

- Data is updated yearly by 1823
- Covers years 2024, 2025, and 2026
- Format follows iCalendar (RFC 5545) specification
- Not a real-time API — static yearly files

## Data Dictionary

https://www.1823.gov.hk/datagovhk/statistics/1823_cal_dictionary.pdf

---

**Date Added:** 2026-04-02
