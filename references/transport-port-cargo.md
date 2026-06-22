# Port Cargo Throughput

Port cargo throughput statistics (seaborne + river cargo) in '000 tonnes, with year-on-year % change. Quarterly and annual data from 1993 onwards.

**Dataset ID:** `hk-censtatd-tablechart-410-55110`
**Provider:** Census and Statistics Department (Electronic Trading Services and Cargo Statistics Section)
**Category:** transport

## API

**Endpoint:** `https://www.censtatd.gov.hk/api/get.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | `410-55110` (Port Cargo Throughput table ID) |
| `lang` | Yes | `en`, `tc`, or `sc` |
| `full_series` | Yes | `1` to retrieve full time series |

### Response Fields

| Field | Description |
|-------|-------------|
| `DIRECTION` / `DIRECTIONDesc` | `In` (Inward), `Out` (Outward), `` (Total) |
| `SHIPMENT_TYPE` / `SHIPMENT_TYPEDesc` | `DS` (Direct Shipment), `TS` (Transhipment), `` (Total) |
| `freq` | `Y` (Yearly), `Q` (Quarterly) |
| `period` | Year (`2025`) or quarter end (`202603` = Q1 2026) |
| `sv` / `svDesc` | `PORT_CARGO_TP` = `('000 tonnes)` or `Year-on-year % change` |
| `figure` | Numeric value |

## Examples

```bash
# Full series, English
curl -s "https://www.censtatd.gov.hk/api/get.php?id=410-55110&lang=en&full_series=1"

# Extract latest quarterly totals with YoY change
curl -s "https://www.censtatd.gov.hk/api/get.php?id=410-55110&lang=en&full_series=1" | python3 -c "
import sys, json
data = json.load(sys.stdin)
records = [r for r in data['dataSet'] if r['freq']=='Q' and r['DIRECTION']=='' and r['SHIPMENT_TYPE']=='']
records.sort(key=lambda x: x['period'])
for r in records[-6:]:
    print(f\"{r['period']}: {r['figure']} {r['svDesc']}\")
"
```

## Notes

- Update frequency: Quarterly. Latest available period may lag 2-3 months.
- Period format for quarterly: `YYYYQQ` where QQ is quarter end month (03=Q1, 06=Q2, 09=Q3, 12=Q4).
- Data dictionary: https://www.censtatd.gov.hk/datagovhk/WT_data_dict_en.pdf
- Also available as CSV/XLSX download via `web_table.html` endpoint, but those return HTML (JavaScript-rendered), not raw files — use the JSON API instead.
- Related tables: `410-55290` (Container Throughput in TEUs), `410-55111` (Seaborne Cargo), `410-55112` (River Cargo).

---

**Date Added:** 2026-06-22
