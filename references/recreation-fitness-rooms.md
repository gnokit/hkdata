# Fitness Rooms

**Dataset ID:** `hk-lcsd-facility-facility-fit`
**Provider:** Leisure and Cultural Services Department (LCSD)
**Category:** Recreation and Culture (`recreation-and-culture`)

## Description

Locations of LCSD sports centres that provide a fitness room (健身房 / 健身室),
plus the fitness equipment installed in each room. Covers 87 fitness rooms
across all 18 districts, with English/Chinese venue names, addresses, room
sizes, phone numbers and coordinates.

There is **no real-time fitness-room availability dataset** on data.gov.hk.
The "Available Session of … by Venue" family exists only for tennis,
badminton, basketball and volleyball courts.

## Data Temporality

**Static inventory** — "as and when new facility is added or amendment is
made". No time series and no booking/occupancy state. For actual availability,
users must use LCSD's Leisure Link (康體通) booking system, which is not part
of this dataset.

## API

**Endpoints:**

| Resource | URL |
|----------|-----|
| Locations of LCSD Sports Centres provided with Fitness Rooms (87 rows) | `http://www.lcsd.gov.hk/datagovhk/facility/facility-fitrm.json` |
| Fitness Equipment provided in Fitness Rooms (1,925 rows) | `http://www.lcsd.gov.hk/datagovhk/facility/facility-fiteqmt.json` |

**Format:** JSON (public, no auth)

### Parameters

None.

### Headers (if needed)

```
User-Agent: curl/8.0
```

## Examples

```bash
# Fitness-room locations
curl -s "http://www.lcsd.gov.hk/datagovhk/facility/facility-fitrm.json"

# Filter to one district
curl -s "http://www.lcsd.gov.hk/datagovhk/facility/facility-fitrm.json" \
  | python3 -c "import json,sys; print([r['Name_en'] for r in json.load(sys.stdin) if r['District_en']=='Sham Shui Po'])"

# Equipment in a venue
curl -s "http://www.lcsd.gov.hk/datagovhk/facility/facility-fiteqmt.json" \
  | python3 -c "import json,sys; print([r for r in json.load(sys.stdin) if r['Name_en']=='Po On Road Sports Centre'])"
```

## Related Resources

- `hk-lcsd-csdi-fitness-rooms` — the same fitness-room inventory on the CSDI
  geospatial portal (API available).
- Availability (real-time, by venue) exists only for: tennis
  (`…-tcvenue`), badminton (`…-bmtcvenue`), basketball (`…-bkbcvenue`),
  volleyball (`…-vbcvenue`).
- `hk-lcsd-facility-usage-facilities` — historical usage of recreational
  facilities by venue (not real-time).
- `recreation-badminton-sessions.md` — worked example of the venue-availability
  pattern.

## Join Keys

- **District:** `District_en` uses `&` (e.g. `Central & Western`); normalize to
  the Censtatd form (`and`) before joining district-level statistics.
- **Venue:** `Name_en` / `Name_cn` match `Name_en`/`Name_cn` in the equipment
  resource and in other LCSD venue datasets.

## Known Quirks

- `Size_en` contains HTML (`121m<sup>2</sup>`) — strip tags before display; use
  `Size_cn` (`121平方米`) or parse the number.
- `Phone` values may have trailing spaces.
- `Longitude` / `Latitude` are degree-minute-second strings
  (e.g. `114-9-33`), not decimal degrees — convert before mapping.
- No venue is literally named "Cheung Sha Wan"; 長沙灣 is a sub-area of Sham
  Shui Po District, so match by address rather than District.
- District names differ from the Housing Authority / CSDI forms (`&` vs `and`).

## Notes

- 87 fitness rooms; Sham Shui Po District has 4 (Pei Ho Street, Po On Road,
  Sham Shui Po, Shek Kip Mei Park sports centres). The closest to Cheung Sha
  Wan is Po On Road Sports Centre (保安道體育館, 325–329 Po On Road).
- Rate limits: follow data.gov.hk terms of use.

---

**Date Added:** 2026-09-27
