# Vessel Arrivals and Departures

Real-time arrival and departure information for ocean-going vessels at Hong Kong port. Updated every 20 minutes. Shows vessels arrived/departed in the last 36 hours, vessels due to arrive, and vessels currently in port.

**Dataset ID:** `hk-md-mardep-vessel-arrivals-and-departures`
**Provider:** Marine Department
**Category:** transport

## API

**Endpoints (XML, no auth):**

| Resource | URL |
|----------|-----|
| Arrived (last 36h) | `https://www.mardep.gov.hk/e_files/en/opendata/RP05005i.XML` |
| Due to arrive | `https://www.mardep.gov.hk/e_files/en/opendata/RP04005i.XML` |
| In port now | `https://www.mardep.gov.hk/e_files/en/opendata/RP06005i.XML` |
| Departed (last 36h) | `https://www.mardep.gov.hk/e_files/en/opendata/RP05505i.XML` |

### XML Structure

Root: `RP05005IXML`, each vessel is a `G_SQL1` element with:
- `CALL_SIGN`, `VESSEL_NAME`, `SHIP_TYPE`, `AGENT_NAME`
- `CURRENT_LOCATION`, `ARRIVAL_TIME` (format: `DD-MMM-YYYY HH:MM`)
- `REMARK` (e.g. "Departed")

### Ship Types (observed)

`CONTAINER`, `BULK/ WOODCHIP/ CEMENT/ ORE CARRIER`, `GENERAL / HEAVY LIFT CARGO`, `TANKER (CRUDE,FUEL,DIESEL,LUB)`, `CHEMICAL`, `LIQUIFIED PETROLEUM GAS TANKER`, `MULTI-PURPOSE(SEMI CONT.)`, `RORO/REEFER CARRIER`, `CAR CARRIER`, `FISHING`

## Examples

```bash
# Fetch arrived vessels (last 36h) and count container ships
curl -s "https://www.mardep.gov.hk/e_files/en/opendata/RP05005i.XML" | python3 -c "
import sys, xml.etree.ElementTree as ET
root = ET.fromstring(sys.stdin.read())
records = root.findall('G_SQL1')
container = sum(1 for r in records if 'CONTAINER' in (r.findtext('SHIP_TYPE','') or '').upper())
print(f'Total arrived: {len(records)}, Container: {container}')
"
```

## Notes

- **Format is XML, not JSON** — use `xml.etree.ElementTree` or similar, not `json.tool`.
- **Real-time snapshot only** — shows last 36 hours, not historical monthly aggregates. Cannot be used for "last month" vessel call counts.
- For historical vessel call statistics, see Censtatd Shipping Statistics Report (`B1020008`) — but note its CSV download endpoint (`wbr.html?download_csv=1`) returns HTML, not CSV data (broken for programmatic access).
- Related dataset: `hk-md-mardep-non-convention-vessel-arrivals-and-departures` (river trade / coastal / Macao vessels, same XML format).
- Related dataset: `hk-md-mardep-vessel-traffic-management-system-report` (daily VTMS report, XML).
- Find this dataset with `catalog-search "vessel"` (retired CKAN search returned 0 for `vessel`).

---

**Date Added:** 2026-06-22
