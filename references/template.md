# Dataset Template

Use this template when documenting a new dataset.

---

**Dataset ID:** ``
**Provider:** 
**Category:** 

## Description

Brief description of what this dataset provides.

## API

**Endpoint:** `https://...`

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

## Notes

- Important notes about the API
- Deprecation warnings
- Rate limit information

---

**Date Added:** YYYY-MM-DD
