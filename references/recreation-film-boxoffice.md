# Hong Kong Box Office for FDF Projects (data.gov.hk)

## Dataset Info
- **Dataset ID:** `hk-cstb-cstb_ccida-hkboxoffice-for-fdf-projects`
- **URL:** https://data.gov.hk/en-data/dataset/hk-cstb-cstb_ccida-hkboxoffice-for-fdf-projects
- **Provider:** Culture, Sports and Tourism Bureau (Create Hong Kong)
- **Category:** Recreation and Culture
- **Update Frequency:** QUARTERLY

## Description
Hong Kong box office revenue for film production projects funded under the Film Development Fund (FDF). Tracks commercial performance of government-supported films.

## API

**Endpoint (CSV):**
```
https://www.ccidahk.gov.hk/data/hkboxoffice_FDF_projects.csv
```

### Fields

| Field | Description |
|-------|-------------|
| Reference | Film reference ID |
| Film Title_EN / Film Title_TC / Film Title_SC | Film title in three languages |
| Funding Scheme | Scheme category number |
| Hong Kong Box Office (HK$) | Total HK box office revenue |
| Last Update | Data last updated date |
| Remarks_EN / TC / SC | Additional notes |

## Examples

```bash
# Download box office data
curl -s "https://www.ccidahk.gov.hk/data/hkboxoffice_FDF_projects.csv" | head -10

# Top grossing FDF film
curl -s "https://www.ccidahk.gov.hk/data/hkboxoffice_FDF_projects.csv" | sort -t',' -k5 -nr | head -5

# Total FDF box office
curl -s "https://www.ccidahk.gov.hk/data/hkboxoffice_FDF_projects.csv" | awk -F',' 'NR>1 {sum+=$5} END {print sum}'
```

## Sample Data

| Film (TC) | Box Office (HK$) |
|-----------|-----------------|
| 狂舞派 (The Way We Dance) | 13,646,417 |
| 潮性辦公室 (MicroSex Office) | 3,411,062 |
| 熱浪球愛戰 (Beach Spike) | 1,677,655 |
| 高舉‧愛 (Love Lifting) | 1,298,130 |
| 爆3俏嬌娃 (Kick Ass Girls) | 1,450,055 |

## Notes

- Data last updated: 31/12/2025
- Only covers FDF-funded films, not the entire HK box office
- Can be cross-referenced with `recreation-film-fund.md` for funding amount vs. box office return
- Contact: Create Hong Kong

---

**Date Added:** 2026-04-30
