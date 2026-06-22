# Public Rental Housing Income & Asset Limits (data.gov.hk)

## Dataset Info
- **Dataset ID:** `hk-housing-aas-prhicaslmt`
- **URL:** https://data.gov.hk/en-data/dataset/hk-housing-aas-prhicaslmt
- **Provider:** Hong Kong Housing Authority
- **Category:** Housing
- **Update Frequency:** Annually

## Description
Monthly income and asset limits for Public Rental Housing (PRH) application, broken down by household type and household size. This is the official eligibility criteria used by the Housing Authority to assess PRH applications.

## API

**Endpoint (English JSON):**
```
https://data.housingauthority.gov.hk/dataset/prhicaslmt/prh_income_asset_limit_en.json
```

**Alternative PSI API:**
```
https://data.housingauthority.gov.hk/psi/rest/export/prh-inc-ast-lmt
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| lang | No | `en`, `tc`, `sc` for English, Traditional Chinese, Simplified Chinese |

## Examples

```bash
# English JSON
curl -s "https://data.housingauthority.gov.hk/dataset/prhicaslmt/prh_income_asset_limit_en.json"

# Traditional Chinese JSON
curl -s "https://data.housingauthority.gov.hk/dataset/prhicaslmt/prh_income_asset_limit_tc.json"
```

## Notes

- Data is updated annually when the Housing Authority reviews PRH eligibility limits
- Covers both income limits and asset limits
- Household types include: 2-Person, 3-Person, 4-Person, etc.
- Contact: hkha@housingauthority.gov.hk | 2712 2712

---

**Date Added:** 2026-04-30
