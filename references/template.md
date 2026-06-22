# Dataset Template

Use this template when documenting a new dataset.

---

**Dataset ID:** ``
**Provider:** 
**Category:** 

## Description

Brief description of what this dataset provides.

## Data Temporality

Choose one and adjust "latest available" language accordingly:

- **Real-time feed:** sub-daily updates, reflects a rolling window, no historical archive via API
- **Historical series:** periodic (monthly/quarterly/annual), full time series available, lag of weeks to months
- **Static inventory:** updated "as needed", no time series, point-in-time snapshot

## API

**Endpoint:** `https://...`

**Format:** JSON / XML / CSV

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| param1 | Yes | Description |
| param2 | No | Description |

### Headers (if needed)

```
Accept: application/json
```

## Examples

```bash
# Basic query
curl -s "https://api.example.com/endpoint?param=value"

# With headers
curl -H "Accept: application/json" "https://api.example.com/endpoint"
```

## Related Resources

- Sibling endpoints or related tables

## Join Keys

- If this dataset is keyed by district, period, station, etc., state the canonical key form here

## Known Quirks

- Broken endpoints, auth requirements, encoding gotchas, or other caveats

## Notes

- Important notes about the API
- Deprecation warnings
- Rate limit information

---

**Date Added:** YYYY-MM-DD
