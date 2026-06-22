# Elderly Service Statistics

Annual and monthly statistics on elderly service recipients across three service categories from the Census and Statistics Department.

**Provider:** Census and Statistics Department
**Category:** welfare (data.gov.hk: "Social Welfare")

## Datasets

| Table ID | Title | Service Type |
|----------|-------|-------------|
| `935-88005` | Community support services for the elderly | NEC, DECC, SCE |
| `935-88006` | Community care services for the elderly | DE/DCU, home care, home support |
| `935-88004` | Residential care services for the elderly | C&A Homes, Nursing Homes, Homes for the Aged |

## API

**Endpoint:** `https://www.censtatd.gov.hk/api/get.php`

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | Table ID (e.g., `935-88005`) |
| `lang` | Yes | `en`, `tc`, or `sc` |
| `full_series` | Yes | `1` for full series |

### Response Fields

| Field | Description |
|-------|-------------|
| `TYPE_SERV_ELDDesc` | Service type (e.g., "Neighbourhood Elderly Centres") |
| `freq` | `Y` (annual) or `M` (monthly) |
| `period` | Year (`2024`) or month (`202512`) |
| `sv` / `svDesc` | `SERV_ELDERLY_CSS` = "Number" |
| `figure` | Number of service recipients (NOT centre count) |

### Service Programmes (2024)

**Community Support Services (935-88005):**
| Programme | Recipients (2024) |
|-----------|-------------------|
| District Elderly Community Centres (DECC) | 85,025 |
| Neighbourhood Elderly Centres (NEC) | 197,401 |
| Social Centre for the Elderly (SCE) | 1,421 |

**Community Care Services (935-88006):**
| Programme | Recipients (2024) |
|-----------|-------------------|
| Day Care Centres/Units for the Elderly | 4,532 |
| Enhanced Home and Community Care Services | N/A |
| Home Care Services for Frail Elderly Persons | 13,195 |
| Home Support Services | 20,733 |
| Integrated Home Care Services | N/A |

**Residential Care Services (935-88004):**
| Programme | Recipients (2024) |
|-----------|-------------------|
| Care and Attention Homes for the Elderly | 14,645 |
| Contract Home | 4,394 |
| Homes for the Aged | 54 |
| Nursing Homes | 1,518 |

## Notes

- **These are recipient counts, NOT centre counts.** For centre counts, see `welfare-elderly-centres.md`.
- Financial year runs from 1 April to 31 March.
- Figures are "as at end of period".
- Some 2024 figures are blank (N/A) — may be revised or discontinued categories.
- Update frequency: Annual (Y) + Monthly (M)
- Latest annual: 2024; latest monthly: 202512 (Dec 2025)
- Requires User-Agent header — use `curl`, not `urllib` without headers.

---

**Date Added:** 2026-06-22
