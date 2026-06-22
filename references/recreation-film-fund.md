# Film Development Fund Approved Projects (data.gov.hk)

## Dataset Info
- **Dataset ID:** `hk-cstb-cstb_ccida-approved-projects-funded-under-fdf`
- **URL:** https://data.gov.hk/en-data/dataset/hk-cstb-cstb_ccida-approved-projects-funded-under-fdf
- **Provider:** Culture, Sports and Tourism Bureau (Create Hong Kong)
- **Category:** Recreation and Culture
- **Update Frequency:** QUARTERLY

## Description
List of approved projects funded under the Film Development Fund (FDF) since June 2009. Covers two funding schemes: Film Production Financing (FPF) / Film Production Grant (FPG) and other schemes.

## API

**Endpoint (FPF/FPG CSV):**
```
https://www.ccidahk.gov.hk/data/FDF_approved_projects_FPF_FPG.csv
```

**Endpoint (Other Schemes CSV):**
```
https://www.ccidahk.gov.hk/data/FDF_approved_projects_Others.csv
```

### Fields

| Field | Description |
|-------|-------------|
| Reference | Project reference ID |
| Film Title_EN / Film Title_TC / Film Title_SC | Film title in three languages |
| Name of Applicant_EN / TC / SC | Production company |
| Approval Date of Film (Month/Year) | When funding was approved |
| Approved Amount (HK$) | Funded amount in HK dollars |

## Examples

```bash
# FPF/FPG projects
curl -s "https://www.ccidahk.gov.hk/data/FDF_approved_projects_FPF_FPG.csv" | head -10

# Other schemes
curl -s "https://www.ccidahk.gov.hk/data/FDF_approved_projects_Others.csv" | head -10

# Total funded amount
curl -s "https://www.ccidahk.gov.hk/data/FDF_approved_projects_FPF_FPG.csv" | awk -F',' 'NR>1 {sum+=$6} END {print sum}'
```

## Notes

- FPF/FPG projects typically funded at $9,000,000 per film (standard grant amount)
- Historical data back to June 2009
- Some films listed as "(To be confirmed)" for English title
- Contact: Create Hong Kong

---

**Date Added:** 2026-04-30
