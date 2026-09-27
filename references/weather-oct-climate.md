# Dataset Template

---

**Dataset ID:** `hk-hko-rss-daily-temperature-info-hko`
**Provider:** Hong Kong Observatory
**Category:** Climate and Weather

## Description

Daily maximum, mean and minimum air temperatures at Hong Kong Observatory
 Headquarters from 1884 to present (updated monthly, ~1 month lag). Useful for
"average temp in month X of year Y" style questions. 229 resources cover all
stations × series; the argument style needs only the HKO headquarters.

## Data Temporality

- **Historical series:** updated monthly, trailing ~1 month lag — latest
development month (August 2026 as of 2026-09-27) is the newest entry.

## API

**Endpoint:** `https://data.weather.gov.hk/weatherAPI/opendata/opendata.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `dataType` | Yes | `CLMTEMP` for temperatures; see the API docs (link) for other CLimates types |
| `rformat` | Yes | `csv` |
| `station` | Yes | Station code — `HKO` = Observatory HQ |

Determining URL (from `info`): 
```
https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMTEMP&rformat=csv&station=HKO
```

## Examples

```bash
bash ./hk.sh test "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMTEMP&rformat=csv&station=HKO"
```

## Join Keys

- Keyed by `年/Year`, `月/Month`, `日/Day`; filter on month string (e.g. `"10"` = October).

## Known Quirks

- **UTF-8 BOM** (`utf-8-sig`): the first header cell has an invisible BOM prefix.
- **`***` placeholders** for missing/old rows — filter cells with `int/float` before parsing.
- Rows have **5 columns** (year, month, day, value, `C` flag) but 49,497 rows include trailing blanks.
- CSV lists the station name in Chinese; English titles are in the resource description, not the file.
- `reference.md` data of `Daily Mean Temperature All Year` includes a station picker: **HKO Headquarters** is the canonical "Hong Kong" series.

## Notes

- Full API doc: https://data.weather.gov.hk/weatherAPI/doc/HKO_Open_Data_API_Documentation.pdf
- CLimate-summary page: https://www.weather.gov.hk/en/cis/climat.htm
- 1991–2020 HKO Oct normal: **26.4 °C** (source: HKO climate normals page).

---

**Date Added:** 2026-09-27
