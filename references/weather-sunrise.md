# Sunrise/Sunset Times

Daily sunrise, sunset, and sun transit times from Hong Kong Observatory.

**Dataset ID:** `hk-hko-rss-times-of-sunrise-suntransit-sunset`
**Provider:** Hong Kong Observatory
**Category:** weather

## API

**Endpoint:** `https://data.weather.gov.hk/weatherAPI/opendata/opendata.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `dataType` | Yes | `SRS` |
| `year` | Yes | YYYY (e.g., 2026) |
| `rformat` | Yes | `csv` or `json` |

## Examples

```bash
# Get sunrise/sunset for 2026
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=SRS&year=2026&rformat=csv"

# Get specific date
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=SRS&year=2026&rformat=csv" | grep "2026-03-13"
```

**Added:** 2026-03-13
