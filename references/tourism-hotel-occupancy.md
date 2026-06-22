# Hotel Room Occupancy Rate

## Dataset Info
- **Dataset ID:** `hk-cstb-cstb_tc-tc-hotel-room-occupancy-rate`
- **URL:** https://data.gov.hk/en-data/dataset/hk-cstb-cstb_tc-tc-hotel-room-occupancy-rate
- **Provider:** Culture, Sports and Tourism Bureau (data from Hong Kong Tourism Board)
- **Category:** Tourism
- **Update Frequency:** Monthly

## Description
Monthly and annual hotel room occupancy rate (%) in Hong Kong. Data covers the past five years and is provided by the Hong Kong Tourism Board.

## Data Temporality

- **Historical series:** monthly data for the past five years
- Typically released with a short lag

## API

**Endpoint (CSV):**
```
https://www.tourism.gov.hk/datagovhk/hotelroomoccupancy/hotel_room_occupancy_rate_monthly_en.csv
```

**Annual endpoint:**
```
https://www.tourism.gov.hk/datagovhk/hotelroomoccupancy/hotel_room_occupancy_rate_yearly_en.csv
```

### Parameters

No query parameters. Files are static CSV downloads.

## Examples

```bash
# Monthly occupancy rate
python3 ./scripts/hkdata.py test \
  "https://www.tourism.gov.hk/datagovhk/hotelroomoccupancy/hotel_room_occupancy_rate_monthly_en.csv"
```

## Related Resources

- `hk-censtatd-tablechart-650-80001` — Visitor arrivals by nationality/region
- `hk-cstb-cstb_tc-tc-average-achieved-hotel-room-rate` — Average achieved hotel room rate

## Join Keys

- `Year-Month` (YYYYMM)

## Known Quirks

- CKAN `package_search` does not index "hotel" or "occupancy" keywords well. Use web search fallback if needed.
- CSV is hosted on tourism.gov.hk, not data.gov.hk, but the dataset metadata is on data.gov.hk.

## Notes

- Contact: tcenq@cstb.gov.hk | (852) 3848 4122

---

**Date Added:** 2026-06-22
