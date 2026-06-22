# Air Quality Data

Real-time Air Quality Health Index (AQHI) and pollutant concentration data from Hong Kong's Environmental Protection Department (EPD). Covers 18 monitoring stations (15 general + 3 roadside), updated hourly.

**Provider:** Environmental Protection Department / Digital Policy Office
**Category:** environment

## Datasets

| Dataset | Format | Content | Update |
|---------|--------|---------|--------|
| AQHI by station (EPD) | RSS | Current AQHI per station | Hourly |
| AQHI range + forecast (EPD) | RSS | Current range + forecast | Hourly |
| Past 24h pollutant concentration (EPD) | XML | PM2.5, PM10, NO2, SO2, O3, CO per station | Hourly |
| AQHI City Dashboard (DPO) | JSON/CSV/XML | AQHI per station + forecast | Hourly |
| Smart Lampposts air quality (EPD) | ZIP (JSON archive) | NO, NO2, PM2.5 from lamppost sensors | As needed |
| Past AQHI records (EPD) | CSV/API | Historical hourly AQHI since Dec 2013 | Monthly |

## API Endpoints

### 1. Current AQHI by Station (RSS)

**URL:** `https://www.aqhi.gov.hk/epd/ddata/html/out/aqhi_ind_rss_Eng.xml`

**Structure:** RSS 2.0 with `<item>` per station. Each item:
- `<title>`: Station name (e.g., "Causeway Bay")
- `<description>`: `"<station> - <type>: <aqhi> <risk> - <datetime>"`

### 2. Past 24-Hour Pollutant Concentration (XML)

**URL:** `https://www.aqhi.gov.hk/epd/ddata/html/out/24pc_Eng.xml`

**Structure:** `<AQHI24HrPollutantConcentration>` root, `<PollutantConcentration>` per station-hour:
- `<StationName>`: Station name (e.g., "Causeway Bay")
- `<DateTime>`: RFC 822 format (e.g., "Mon, 22 Jun 2026 09:00:00 +0800")
- `<PM2.5>`: PM2.5 in µg/m³
- `<PM10>`: PM10 in µg/m³
- `<NO2>`: NO2 in µg/m³
- `<SO2>`: SO2 in µg/m³
- `<O3>`: O3 in µg/m³
- `<CO>`: CO in µg/m³

### 3. City Dashboard AQHI (JSON — recommended for programmatic use)

**Individual station AQHI:** `https://dashboard.data.gov.hk/api/aqhi-individual?format=json`

**Response:** JSON array, one object per station:
```json
{
    "station": "Causeway Bay",
    "aqhi": 2,
    "health_risk": "Low",
    "publish_date": "2026-06-20T08:30:00"
}
```

**Other endpoints:**
- AQHI range: `https://datagovhk.blob.core.windows.net/dataset/aqhi/aqhi.json`
- Forecast: `https://datagovhk.blob.core.windows.net/dataset/aqhi/aqhi-forecast.json`
- CSV/XML variants: replace `.json` with `.csv` or `.xml`, or `?format=csv`/`?format=xml`

## Monitoring Stations (18 total)

**General stations (15):** Central/Western, Southern, Eastern, Kwun Tong, Sham Shui Po, Kwai Chung, Tsuen Wan, Tseung Kwan O, Yuen Long, Tuen Mun, Tung Chung, Tai Po, Sha Tin, North, Tap Mun

**Roadside stations (3):** Causeway Bay, Central, Mong Kok

## Examples

```bash
# Get current AQHI for all stations (JSON)
curl -s "https://dashboard.data.gov.hk/api/aqhi-individual?format=json" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for s in data:
    print(f\"{s['station']:30s} AQHI={s['aqhi']:2d}  {s['health_risk']}\")
"

# Get PM2.5 for Causeway Bay (past 24h, XML)
curl -s "https://www.aqhi.gov.hk/epd/ddata/html/out/24pc_Eng.xml" | python3 -c "
import sys, xml.etree.ElementTree as ET
root = ET.fromstring(sys.stdin.read())
for pc in root.iter('PollutantConcentration'):
    if 'Causeway' in pc.findtext('StationName',''):
        print(f\"{pc.findtext('DateTime','')}  PM2.5={pc.findtext('PM2.5','')} µg/m³\")
"

# Get latest AQHI for Causeway Bay (RSS)
curl -s "https://www.aqhi.gov.hk/epd/ddata/html/out/aqhi_ind_rss_Eng.xml" | python3 -c "
import sys, xml.etree.ElementTree as ET
root = ET.fromstring(sys.stdin.read())
for item in root.findall('.//item'):
    if 'Causeway' in item.findtext('title',''):
        print(item.findtext('description',''))
"
```

## Notes

- **AQHI scale:** 1-10 and 10+, grouped into 5 health risk categories: Low (1-3), Moderate (4-6), High (7), Very High (8-10), Serious (10+).
- **AQHI vs PM2.5:** AQHI is a composite health risk index; PM2.5 is a specific pollutant concentration. They come from different endpoints — AQHI from RSS/JSON, PM2.5 from the pollutant XML.
- **No broken endpoints found** — all 4 tested endpoints (RSS, XML, JSON, ZIP) are live and returning current data as of 2026-06-22.
- **CKAN indexing gap:** `AQHI` and `pollution` keywords return 0 results in `package_search`. Use web search `site:data.gov.hk AQHI EPD` to discover these datasets.
- **City Dashboard JSON is ~1 hour behind RSS** — RSS shows 09:30, JSON shows 08:30 for the same hour. Use RSS for most current AQHI; use JSON for programmatic convenience.
- **Smart Lampposts data** is a ZIP archive of historical sensor data (not real-time), and lamppost locations do not include Causeway Bay. Use the EPD station data instead.
- Update frequency: Hourly (AQHI + pollutant concentration)
- Chinese versions: replace `_Eng.xml` with `_ChT.xml` (Traditional) or `_ChS.xml` (Simplified)

---

**Date Added:** 2026-06-22
