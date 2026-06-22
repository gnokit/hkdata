# District-Level Labour Force Statistics

Labour force count and labour force participation rate (LFPR) by District Council district, sex, and age. Annual data from Censtatd.

**Dataset ID:** `hk-censtatd-tablechart-210-06821`
**Provider:** Census and Statistics Department (Social Analysis and Research Section)
**Category:** employment

## API

**Endpoint:** `https://www.censtatd.gov.hk/api/get.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | `210-06821` |
| `lang` | Yes | `en`, `tc`, or `sc` |
| `full_series` | Yes | `1` for full series |

### Response Fields

| Field | Description |
|-------|-------------|
| `DC` / `DCDesc` | District code (A–T) / District name (e.g., "Kwun Tong") |
| `SEX` / `SEXDesc` | Sex (M/F, empty = total) |
| `AGE` / `AGEDesc` | Age group (empty = total) |
| `freq` | `Y` (annual) |
| `period` | Year (e.g., "2025") |
| `sv` / `svDesc` | `LF` = No. ('000), `LFPR` = (%) |
| `figure` | Numeric value |

### District Codes

| Code | District |
|------|----------|
| A | Central and Western |
| B | Wan Chai |
| C | Eastern |
| D | Southern |
| E | Yau Tsim Mong |
| F | Sham Shui Po |
| G | Kowloon City |
| H | Wong Tai Sin |
| J | Kwun Tong |
| K | Kwai Tsing |
| L | Tsuen Wan |
| M | Tuen Mun |
| N | Yuen Long |
| P | North |
| Q | Tai Po |
| R | Sai Kung |
| S | Sha Tin |
| T | Islands |

## Examples

```bash
# Get 2025 LFPR by district (total sex/age)
curl -s "https://www.censtatd.gov.hk/api/get.php?id=210-06821&lang=en&full_series=1" | python3 -c "
import sys, json
data = json.load(sys.stdin)
records = [r for r in data['dataSet'] if r['period']=='2025' and r.get('SEX','')=='' and r.get('AGE','')=='' and r['sv']=='LFPR' and r.get('DCDesc','')!='Total']
for r in sorted(records, key=lambda x: x['figure']):
    print(f\"{r['DCDesc']:25s} {r['figure']}%\")
"
```

## Notes

- **This is LFPR, NOT unemployment rate.** LFPR = Labour Force / Working Age Population. A low LFPR does NOT mean high unemployment — it means many people are not in the labour force (retirees, homemakers, students).
- **Unemployment rate by district is NOT published on data.gov.hk.** The monthly General Household Survey (210-06401) only provides UR by age/sex, not by district. The GHS sample size is too small for reliable district-level UR estimates.
- Update frequency: Annual. Latest available: 2025.
- Related table: `210-06822` (same but excluding foreign domestic helpers).
- Censtatd API requires a User-Agent header — `curl` works, but `urllib.request` gets 403 Forbidden. Always use `curl`.
- District names use `and` not `&` — normalize before joining with Housing Authority data.

---

**Date Added:** 2026-06-22
