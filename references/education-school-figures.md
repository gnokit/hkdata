# School Figures — Day Schools, Enrolment and Classes (EDB)

**Dataset IDs:**
- `hk-edb-figustat-day-sch-lev-sec` — Day Schools by Type/Sector (tab0101)
- `hk-edb-figustat-stu-day-sch-lev-sec` — Student Enrolment in Day Schools by Type/Sector (tab0103)
- `hk-edb-figustat-ope-acc-stu-rep-pri-sec` — Operating Classes, Accommodation, Student Enrolment and Repeaters in Primary Schools by Sector (tab0302)

**Provider:** Education Bureau (EDB)
**Category:** Education

## Description

Territory-wide annual time series used to track the number of schools, student
enrolment and operating classes by level (kindergarten / primary / secondary /
special) and sector (government / aided / DSS / private / international). These
are the tables that show the effect of Hong Kong's falling birth rate on the
school system. They do **not** enumerate individual school closures.

## Data Temporality

**Historical series** — yearly, released as a new file each school year, wide
format with years as columns (2015–2025). The latest column may be provisional.

## API

**Format:** CSV / XLSX (static files), no auth. URL pattern:

```
http://www.edb.gov.hk/attachment/{lang}/about-edb/publications-stat/figures/{table}.csv
```

| Table | English CSV |
|-------|-------------|
| Day schools by type/sector | `.../figures/tab0101_en.csv` |
| Student enrolment by type/sector | `.../figures/tab0103_en.csv` |
| Primary classes/accommodation/enrolment by sector | `.../figures/tab0302_en.csv` |

### Parameters

None — static CSV downloads (`_en`, `_tc`, `_sc` variants).

## Examples

```bash
# Number of day schools by level and sector
curl -s "http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0101_en.csv"

# Student enrolment by level and sector
curl -s "http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0103_en.csv"

# Primary operating classes / capacity / enrolment by sector
curl -s "http://www.edb.gov.hk/attachment/en/about-edb/publications-stat/figures/tab0302_en.csv"
```

## Verified Trend (2015 → 2025)

| Indicator | 2015 | Peak | 2025 | Change |
|-----------|------|------|------|--------|
| Kindergarten enrolment (All) | 185,398 | — | 113,204 | **−72,194 (−39%)** |
| Kindergarten schools (All) | 1,000 | 1,049 (2017) | 958 | −42 |
| Primary enrolment (All) | 337,558 | 373,228 (2019) | 317,233 | −56,000 from peak (−15%) |
| Primary operating classes (All) | 12,618 | 13,725 (2019) | 12,714 | −1,011 from peak |
| Primary capacity/accommodation (All) | 345,485 | 383,845 (2019) | 336,568 | −47,277 from peak |
| Secondary schools (Aided) | 360 | — | 357 | −3 |
| Secondary schools (DSS) | 61 | — | 57 | −4 |
| Total day schools (all levels) | 2,139 | — | 2,125 | −14 |

Driver (see [health-births.md](health-births.md)): live births fell from
**95,451 (2011)** to **32,501 (2022)**, recovering to 36,723 (2024); crude
birth rate 13.5 → 4.9 per 1,000.

## Cohort Lag (why the decline propagates)

A smaller birth cohort moves through the system with a fixed lag, so the
kindergarten decline appears in primary ~6 years later and secondary ~12 years
later. Using P1 intake ≈ births 6 years earlier and S1 intake ≈ births 12 years
earlier (2025 = 100):

| School year | P1 intake index | S1 intake index |
|-------------|-----------------|-----------------|
| 2025 | 100 | 100 |
| 2026 | 81 | 109 |
| 2027 | 70 | 105 |
| 2028 | 61 | 107 |
| 2029 | 63 | 99 |
| 2030 | 69 | 94 |
| 2031 | – | 93 |
| 2032 | – | 75 |
| 2033 | – | 65 |
| 2034 | – | 57 |

Interpretation: the cohort born 2019–2022 (which cut kindergarten enrolment
39%) reaches P1 in 2025–2028 and S1 in 2031–2034. The primary squeeze is
already visible (enrolment peaked 2019, −1,011 classes); secondary still looks
stable because it is riding the larger 2007–2013 cohorts.

This is a **projection from birth data, not a reported figure**. Relative
decline is robust; absolute totals are not (the naive cohort model overstates —
it ignores immigration and talent-scheme arrivals, cross-boundary students,
non-local/international school growth, repeaters and class-size policy).

### Primary school roll projection (territory-wide)

Aging the **actual 2025/26** primary enrolment by grade and filling each new P1
from births × the recent P1/births ratio (0.922), the territory-wide primary
roll falls every year:

| School year | P1 intake | Total roll (P1–P6) | vs 2025/26 | vs 2019/20 peak |
|-------------|-----------|--------------------|------------|-----------------|
| 2025/26 | 49,723 | **317,233** (actual) | 0% | −15% |
| 2026/27 | 39,686 | 302,103 | −5% | −19% |
| 2027/28 | 34,081 | 280,961 | −11% | −25% |
| 2028/29 | 29,975 | 256,236 | −19% | −31% |
| 2029/30 | 30,649 | 234,235 | −26% | −37% |
| 2030/31 | 33,869 | 217,983 | **−31%** | −42% |

So a cohort entering P1 in 2025/26 sees its school's roll shrink about **31% by
P6** — roughly **3 in 10 pupils gone** — relative to the year it started. (The
fall is steeper against the 2019/20 peak: −42%.) The rate eases after 2028/29
because births ticked up in 2023–24.

**Class-count implication.** P1 classes follow intake, but in whole classes
bounded by the minimum class size (small-class teaching ≈ 25). Territory-wide
P1 already runs at ~23.9 pupils/class (2,082 P1 classes, 49,723 pupils in 2025),
so schools partly absorb the fall by shrinking class size before cutting
classes. Scaling a 5-class P1 to the territory intake ratio gives ~**4 classes
by 2026/27** and ~**3–4 by 2030/31** (trough ~3 around 2028/29). A 5-class P1 is
above the ~3.5 territory average, so a larger/popular school may retain more
classes by absorbing pupils from schools that close.

## Related Resources

- [education-schools.md](education-schools.md) — Censtatd 925-92023, day schools
  by type and region.
- [education-primary-enrolment.md](education-primary-enrolment.md) — enrolment
  and classes by district/grade (tab0307/tab0301).
- [health-births.md](health-births.md) — the birth-rate driver.

## Join Keys

- **Level** (`Kindergarten` / `Primary` / `Secondary` / `Special School`) ×
  **Sector** (`Government` / `Aided` / `Direct Subsidy Scheme` / `International`
  / `Other Private`).
- `Classes` / `Accommodation` / `Enrolment` / `Repeaters` row labels within
  tab0302.

## Known Quirks

- **Wide format:** years are columns, so parse by header rather than position.
- Files are UTF-8 **with BOM** and CRLF line endings — decode `utf-8-sig`.
- No dataset on data.gov.hk enumerates school closures / 殺校; closures can only
  be inferred from declining school counts, classes and enrolment.
- EDB figures are territory-wide; district detail needs the tab0307/tab0104
  series instead.

## Notes

- Rate limits: follow data.gov.hk terms of use.

---

**Date Added:** 2026-09-27
