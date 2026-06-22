# Elderly Centres Inventory

Location and contact information for all Social Welfare Department (SWD) elderly centres and support teams across Hong Kong. Four related datasets covering different service types.

**Provider:** Social Welfare Department
**Category:** welfare (data.gov.hk: "Community and Social Welfare")

## Datasets

| Type | Dataset ID | Centres (as of 2026-06) |
|------|-----------|------------------------|
| Neighbourhood Elderly Centres (NEC) | `hk-swd-elderly-list-of-neighbourhood-elderly-centres` | 172 |
| Day Care Centres/Units (DE/DCU) | `hk-swd-elderly-list-of-de-dcu` | 96 |
| Social Centres for the Elderly (SCE) | `hk-swd-elderly-list-of-social-centres-for-the-elderly` | 1 (stale — migrated to CSDI) |
| Support Teams for the Elderly (STE) | `hk-swd-elderly-list-of-support-teams-for-the-elderly` | 64 |
| **Total (excl. stale SCE)** | | **332** |

## API / Downloads

All four datasets provide **CSV downloads** from SWD. The CSVs are also available via the CSDI Portal API (see each dataset's `package_show` for the CSDI URL).

| Dataset | CSV URL |
|---------|---------|
| NEC | `https://www.swd.gov.hk/datagovhk/elderly/list-of-neighbourhood-elderly-centres.csv` |
| DE/DCU | `https://www.swd.gov.hk/datagovhk/elderly/List-of-DE-DCU.csv` |
| SCE | `https://www.swd.gov.hk/datagovhk/elderly/list-of-social-centres-for-the-elderly.csv` |
| STE | `https://www.swd.gov.hk/datagovhk/elderly/List-of-STE.csv` |

### CSV Format Quirks

**All SWD elderly CSVs are UTF-16-LE encoded and tab-delimited** (despite the `.csv` extension). Standard `csv.reader` with UTF-8 will fail. Must:
1. Read raw bytes, detect BOM (`\xff\xfe` → UTF-16-LE)
2. Decode with `utf-16-le`
3. Strip BOM character (`\ufeff`)
4. Parse with `delimiter='\t'` (NOT comma)
5. DE/DCU has title/note rows before the actual header — skip first 2 rows

### CSV Fields (NEC example)

| Field | Description |
|-------|-------------|
| `S/N` | Serial number |
| `機構名稱` / `Agency` | Operating organisation (Chinese/English) |
| `中心名稱` / `Centre` | Centre name (Chinese/English) |
| `區` / `District` | District (Chinese/English) |
| `地址 1-3` / `Address 1-3` | Address (Chinese/English) |
| `電話 1-2` / `Tel 1-2` | Phone numbers |
| `傳真 1-2` / `Fax 1-2` | Fax numbers |
| `電郵 1-2` / `Email 1-2` | Email addresses |
| `備註` / `Remarks` | Remarks |

## Examples

```bash
# Fetch and parse NEC CSV (handling UTF-16-LE + tab delimiter)
curl -s "https://www.swd.gov.hk/datagovhk/elderly/list-of-neighbourhood-elderly-centres.csv" | python3 -c "
import sys, csv, io
raw = sys.stdin.buffer.read()
content = raw.decode('utf-16-le').lstrip('\ufeff')
reader = csv.reader(io.StringIO(content), delimiter='\t')
rows = list(reader)
print(f'Total NEC: {len(rows)-1} centres')
from collections import Counter
districts = Counter(r[5].strip() for r in rows[1:] if len(r) > 5 and r[0].strip())
for d, c in districts.most_common():
    print(f'  {d}: {c}')
"
```

## Notes

- **SCE dataset is stale** — only 1 entry remains; the rest have been migrated to the CSDI Portal. The data.gov.hk page says "no longer updated since 9/5/2023". Use the CSDI Portal API for current SCE data.
- **DE/DCU dataset is also somewhat stale** — the title row says "as at 1 April 2023". CSDI Portal may have newer data.
- **NEC and STE datasets appear current** — no staleness notice on their data.gov.hk pages.
- Update frequency: "As and when data is updated"
- District names are in Chinese (`觀塘`, `葵青`) — need to map to English district names for cross-dataset joins. See the 18 DC district mapping in `references/employment-district-lf.md`.

---

**Date Added:** 2026-06-22
