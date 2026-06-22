# Current Weather

Real-time weather conditions and forecasts from Hong Kong Observatory.

**Provider:** Hong Kong Observatory
**Category:** weather

## API

**Endpoint:** `https://data.weather.gov.hk/weatherAPI/opendata/weather.php`

### Data Types

| Type | Description |
|------|-------------|
| `rhrread` | Current weather report (temperature, humidity, rainfall) |
| `flw` | Local weather forecast |
| `warnsum` | Weather warnings summary |
| `fnd` | 9-day weather forecast |

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `dataType` | Yes | One of: `rhrread`, `flw`, `warnsum`, `fnd` |
| `lang` | Yes | `tc` (Traditional Chinese), `sc` (Simplified), `en` |

## Examples

```bash
# Current weather report (Traditional Chinese)
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=tc"

# Local weather forecast (English)
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang=en"

# Weather warnings (Traditional Chinese)
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang=tc"

# 9-day forecast (English)
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=en"
```

## Response Format

Returns JSON with:
- Temperature at various stations
- Humidity levels
- Rainfall measurements
- Weather icons and descriptions

**Added:** 2026-03-13
