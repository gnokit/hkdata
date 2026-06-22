# Address Lookup Service (ALS)

Hong Kong address search and geocoding service.

**Dataset ID:** `hk-dpo-als_01-als`
**Provider:** Lands Department
**Category:** location

## API

**Endpoint:** `https://www.als.gov.hk/lookup`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `q` | Yes | Address query string |

### Headers

```
Accept: application/json
```

## Examples

```bash
# Search for Times Square
curl -H "Accept: application/json" "https://www.als.gov.hk/lookup?q=時代廣場"

# Search in English
curl -H "Accept: application/json" "https://www.als.gov.hk/lookup?q=Times+Square"
```

## Important Note

As of May 2025, the old endpoint `als.ogcio.gov.hk` has been deprecated. Use `als.gov.hk` instead.

## Response Format

Returns JSON with matched addresses including:
- Chinese and English address strings
- Building name
- Street name and number
- District information
- Geographic coordinates

**Added:** 2026-03-13
