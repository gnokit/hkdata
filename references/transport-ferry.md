# Ferry Services — Timetables and Real-time ETA

Hong Kong ferry services data from three sources: Transport Department (static timetables for all licensed routes), Sun Ferry (real-time ETA), and HKKF (real-time ETA). Star Ferry also provides static timetables.

**Providers:** Transport Department, Sun Ferry Services, Hong Kong & Kowloon Ferry (HKKF), Star Ferry Company
**Category:** transport

## Datasets

| Dataset | Provider | Format | Content | Update |
|---------|----------|--------|---------|--------|
| Licensed Ferry Schedules & Fares | Transport Department | CSV/XLSX | Static timetables + fares for all licensed ferry routes | As needed |
| Sun Ferry ETA | Sun Ferry | JSON | Real-time ETA of next ferry trips | Every 1 minute |
| HKKF Ferry ETA + Timetables | HKKF | JSON/CSV | Real-time ETA + routes + piers + timetables + fares | ETA: 1 min; others: as needed |
| Star Ferry Timetables & Fares | Star Ferry | CSV/XLSX | Static timetables + fares (Central↔TST, Wan Chai↔TST) | As needed |

## API Endpoints

### 1. Transport Department — Static Timetables (all licensed routes)

**Base URL:** `https://www.td.gov.hk/datagovhk_td/ferry-tt-ft/resources/en/`

**URL pattern:** `ferry_<origin>_<destination>_<type>_eng.csv`

| Route | Timetable URL |
|-------|---------------|
| Central → Cheung Chau | `ferry_central_cc_timetable_eng.csv` |
| Central → Cheung Chau (fare) | `ferry_central_cc_faretable_eng.csv` |
| Central → Mui Wo | `ferry_central_mw_timetable_eng.csv` |
| Central → Peng Chau | `ferry_central_pc_timetable_eng.csv` |
| Central → Yung Shue Wan | `ferry_central_ysw_timetable_eng.csv` |
| Central → Discovery Bay | `ferry_central_db_timetable_eng.csv` |
| Central → Hung Hom | `ferry_central_hh_timetable_eng.csv` |
| North Point → Hung Hom | `ferry_np_hh_timetable_eng.csv` |
| ... and 10+ more routes | |

**CSV format:** UTF-8 with BOM, comma-delimited
**Columns:** `Direction`, `Service Date`, `Service Hour`, `Remark`
- `Service Date`: "Mondays to Saturdays except public holidays", "Sundays and public holidays"
- `Service Hour`: "9:45 a.m." format
- `Remark`: "1.0" = fast ferry, empty = ordinary ferry

### 2. Sun Ferry — Real-time ETA (JSON API)

**Endpoint:** `https://www.sunferry.com.hk/eta/?route={route_code}`

**Route codes:**

| Code | Route |
|------|-------|
| `CECC` | Central → Cheung Chau |
| `CCCE` | Cheung Chau → Central |
| `CEMW` | Central → Mui Wo |
| `MWCE` | Mui Wo → Central |
| `NPHH` | North Point → Hung Hom |
| `HHNP` | Hung Hom → North Point |
| `NPKC` | North Point → Kowloon City |
| `KCNP` | Kowloon City → North Point |
| `IIPECMUW` | Peng Chau → Mui Wo |
| `IIMUWPEC` | Mui Wo → Peng Chau |
| `IICHCMUW` | Cheung Chau → Mui Wo |
| `IIMUWCHC` | Mui Wo → Cheung Chau |

**Response:**
```json
{
    "type": "ETA",
    "version": "1.1",
    "generated_timestamp": "2026-06-22T09:49:06+08:00",
    "data": [
        {
            "routecode": "CECC",
            "route_en": "Central - Cheung Chau",
            "vesselcode": "FF8",
            "depart_time": "09:45",
            "eta": "10:18",
            "lat": "22.292325",
            "lng": "114.156542",
            "rmk_en": null,
            "date_timestamp": "2026-06-22T09:49:07+08:00"
        }
    ]
}
```

**Fields:** `depart_time` (scheduled departure, 24h), `eta` (estimated arrival, 24h), `lat`/`lng` (vessel GPS), `vesselcode`, `rmk_en` (remarks, e.g. service disruptions)

### 3. HKKF — Real-time ETA + Routes + Piers (JSON API)

**Base URL:** `https://www.hkkfeta.com/opendata/` (note: trailing slash required on all endpoints)

| Endpoint | Content |
|----------|---------|
| `route/` | All routes (JSON) |
| `pier/` | All piers (JSON, requires param) |
| `eta/` | ETA by route (JSON, requires param) |
| `time_table/` | Timetables (CSV, requires param) |
| `fare_table/` | Fares (CSV, requires param) |

**HKKF routes:** Central↔Sok Kwu Wan, Central↔Yung Shue Wan, Central↔Peng Chau, Peng Chau↔Hei Ling Chau (NOT Central→Cheung Chau — that's Sun Ferry)

### 4. Star Ferry — Static Timetables

**Base URL:** `https://www.starferry.com.hk/sites/default/files/upload/open_data/csv/`

| Route | URL |
|-------|-----|
| Central ↔ Tsim Sha Tsui | `ferry_sf_central_tsimshatsui_timetable_eng.csv` |
| Wan Chai ↔ Tsim Sha Tsui | `ferry_sf_wanchai_tsimshatsui_timetable_eng.csv` |

## Examples

```bash
# Get real-time ETA for Central → Cheung Chau (Sun Ferry)
curl -s -L "https://www.sunferry.com.hk/eta/?route=CECC" | python3 -m json.tool

# Get static timetable for Central → Cheung Chau (Transport Department)
curl -s "https://www.td.gov.hk/datagovhk_td/ferry-tt-ft/resources/en/ferry_central_cc_timetable_eng.csv" | python3 -c "
import sys, csv, io, re
from datetime import datetime
content = sys.stdin.read().lstrip('\ufeff')
reader = csv.DictReader(io.StringIO(content))
now = datetime.now()
for r in reader:
    if r['Direction'] == 'Central to Cheung Chau' and 'Mondays to Saturdays' in r['Service Date']:
        m = re.match(r'(\d+):(\d+)\s*(a\.m\.|p\.m\.)', r['Service Hour'])
        if m:
            h, mi = int(m.group(1)), int(m.group(2))
            if m.group(3) == 'p.m.' and h != 12: h += 12
            if m.group(3) == 'a.m.' and h == 12: h = 0
            if now.hour < h or (now.hour == h and now.minute < mi):
                ftype = 'Fast' if r['Remark'] == '1.0' else 'Ordinary'
                print(f\"Next: {r['Service Hour']} ({ftype} ferry)\")
                break
"

# Get HKKF routes
curl -s -L "https://www.hkkfeta.com/opendata/route/" | python3 -m json.tool
```

## Notes

- **Central → Cheung Chau is operated by Sun Ferry**, not HKKF. Use Sun Ferry ETA API with `route=CECC`.
- **Real-time vs static:** Sun Ferry and HKKF provide real-time ETA (1-minute updates, vessel GPS). Transport Department and Star Ferry provide static timetables only.
- **No "on-time status" metric** — the ETA APIs give estimated arrival times and vessel GPS, but do not explicitly say "on time" or "delayed". Compare `depart_time` (scheduled) vs actual departure, or `eta` vs scheduled arrival, to infer delays.
- **HKKF endpoints require trailing slash** — `https://www.hkkfeta.com/opendata/route/` works, `https://www.hkkfeta.com/opendata/route` returns 301 redirect with empty body.
- **Sun Ferry ETA returns 2 departures** — the current trip (already departed, with live GPS) and the next scheduled trip.
- TD CSV uses UTF-8 with BOM (`\ufeff`) — strip before parsing.
- `Remark` field in TD CSV: `1.0` = fast ferry, empty = ordinary ferry. Fast ferry is more expensive but ~20 min vs ~55 min for ordinary.
- Chinese versions: replace `_eng` with `_chi` (Traditional) or `_chi1` (Simplified) for TD/Star Ferry; Sun Ferry returns `route_tc`/`route_sc` in the same JSON.
- API spec: https://www.sunferry.com.hk/eta/SunFerry_ETA_API_Specification_and_Data_Dictionary.pdf
- CKAN indexing: `ferry` keyword returns Star Ferry but NOT the TD licensed ferry dataset or Sun Ferry/HKKF ETA datasets. Use web search to discover them.

---

**Date Added:** 2026-06-22
