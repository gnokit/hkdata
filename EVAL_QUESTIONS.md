# EVAL_QUESTIONS.md — Skill Evaluation Questions

> **Historical record.** These questions were run against the original CKAN
> `package_search` implementation. References to `hkdata-find.sh` / `hkdata.py search`
> describe that retired setup; the current search path is ChromaDB via
> `catalog-search` (see [SKILL.md](SKILL.md)).

Five complex questions used to stress-test the hkdata skill. Each probes untested axes of the workflow, scripts, and documentation. Questions were designed before evaluation to have checkable ground truth and to surface gaps not covered by the 21 pre-existing verified datasets.

---

## Q1 — Port cargo throughput + vessel call counts
> "How many container vessels called at Hong Kong port last month, and what's the year-on-year % change in tonnage?"

**Untested axes probed:**
- Non-JSON resource format (CSV/XLSX/XML downloads, not JSON APIs)
- Real-time vs historical data distinction (36h vessel snapshot vs quarterly tonnage)
- Time-series comparison (last month vs same month last year)

**Outcome:**
- Tonnage: Answered via Censtatd JSON API (Table 410-55110). 2026 Q1: 42,048 '000 tonnes, +2.2% YoY. Data is quarterly, not monthly.
- Vessel counts: Real-time 36h snapshot from Marine Dept XML feed (36 container vessels arrived in last 36h). Historical monthly vessel call counts NOT available via any programmatic API — Censtatd report CSV download is broken (returns HTML viewer page).
- Partial answer delivered with scope caveats.

**Datasets discovered:** `hk-censtatd-tablechart-410-55110` (port cargo throughput JSON), `hk-md-mardep-vessel-arrivals-and-departures` (vessel XML feed)
**Reference files created:** `transport-port-cargo.md`, `transport-vessel-arrivals.md`
**Failures logged:** vessel/arrival/ship keywords → 0 CKAN results; Censtatd `wbr.html` CSV download returns HTML

---

## Q2 — Cross-dataset district join (unemployment + PRH estates)
> "Which Hong Kong district currently has the highest unemployment rate, and how many public rental housing estates are located in that district?"

**Untested axes probed:**
- Cross-dataset join / composition (no two-dataset answer exists in the registry)
- District name normalization (`&` vs `and`, Chinese vs English)
- Proxy indicators when exact metric is unavailable (LFPR as proxy for unemployment rate)

**Outcome:**
- Unemployment rate by district does NOT exist on data.gov.hk (GHS sample too small). LFPR by district (Table 210-06821) used as closest proxy.
- Wong Tai Sin has lowest LFPR (52.7%) — proxy for weakest labour market. Has 18 PRH estates.
- 197 PRH estates total across 16 districts (from Housing Authority API). District names normalized (`&` → `and`) before joining.
- Honest caveat delivered: "LFPR is NOT unemployment rate."

**Datasets discovered:** `hk-censtatd-tablechart-210-06821` (LFPR by district), `hk-housing-eslocator-eslocator` (PRH estate inventory)
**Reference files created:** `employment-district-lf.md`, `housing-estates.md`
**Failures logged:** unemployment by district not published; multi-word keyword crash (`unemployment district`, `public housing`); Censtatd API blocks urllib (403 without User-Agent)

---

## Q3 — Elderly support services (ambiguity + Chinese keywords)
> "What government support services are available for the elderly (長者) in Hong Kong, and how many elderly centres are operating?"

**Untested axes probed:**
- Ambiguity resolution (query spans 4 categories: welfare, health, housing, population)
- Chinese keyword handling + URL-encoding in shell script
- Deriving unused filename prefix from Category Mapping (`social-welfare` → `welfare-`)

**Outcome:**
- Chinese keyword `長者` crashed `hkdata-find.sh` (no URL-encoding). Even manually URL-encoded, CKAN returns 0 results (indexing gap for Chinese metadata).
- English `elderly` found 3 Censtatd service statistics tables. Web search found 4 SWD centre inventory datasets.
- 332 elderly centres/teams total: NEC (172), DE/DCU (96), STE (64). SCE dataset stale (1 entry, migrated to CSDI).
- SWD CSVs are UTF-16-LE encoded + tab-delimited (not standard CSV) — required custom encoding detection.
- First use of `welfare-` filename prefix.

**Datasets discovered:** `hk-swd-elderly-list-of-*` (4 SWD centre datasets), `hk-censtatd-tablechart-935-88004/5/6` (3 Censtatd service tables)
**Reference files created:** `welfare-elderly-centres.md`, `welfare-elderly-services.md`
**Failures logged:** Chinese keyword crash + indexing gap; SWD CSV UTF-16-LE tab-delimited format

---

## Q4 — Air quality at a specific station (endpoint health + format diversity)
> "What is the current Air Quality Health Index and PM2.5 reading at the Causeway Bay monitoring station right now?"

**Untested axes probed:**
- Dead/broken endpoint recovery (Error Handling table path, never exercised)
- Distinguishing "no dataset" vs "endpoint dead" vs "wrong format" — three recovery paths
- Station-id parameter quirks (EPD station naming)
- Four formats in one domain (RSS, XML, JSON, ZIP)

**Outcome:**
- All 4 endpoints LIVE (no broken endpoints, contrary to expected risk). EPD air quality API stability better than predicted.
- AQHI = 2 (Low) at Causeway Bay. PM2.5 = 7.8 µg/m³. Both from EPD RSS + XML feeds.
- 4 datasets found across 2 providers: EPD (RSS + XML) and DPO (JSON). Plus Smart Lampposts (ZIP, historical, not relevant).
- CKAN indexing gap: `AQHI` and `pollution` return 0 results. `air quality` (multi-word) crashes script.

**Datasets discovered:** `hk-epd-airteam-current-aqhi-of-individual-air-quality-monitoring-stations` (RSS), `hk-epd-airteam-past24hr-pc-of-individual-air-quality-monitoring-stations` (XML), `hk-dpo-datagovhk2-city-dashboard-aqhi` (JSON), `hk-epd-lamppost-air-quality-lamppost` (ZIP)
**Reference files created:** `environment-air-quality.md`
**Failures logged:** AQHI/pollution keywords → 0 CKAN results; `air quality` multi-word crash

---

## Q5 — Next ferry from Central to Cheung Chau (real-time vs static)
> "When is the next scheduled ferry from Central Pier 5 to Cheung Chau, and is the service currently running on time?"

**Untested axes probed:**
- Real-time vs static data distinction (no guidance in SKILL.md)
- Partial-answer honesty (skill assumes "answer or no dataset", not "partial answer with caveat")
- Ferry category gap within transport
- Route-operator mapping (which company runs which route)

**Outcome:**
- Real-time ETA IS available — better than expected. Sun Ferry API (`?route=CECC`) returns next 2 departures + vessel GPS, updated every 1 minute.
- Next ferry: 09:45 fast ferry (FF8), ETA 10:18. Vessel already at pier.
- On-time assessment: inferred from ETA matching expected crossing time + no disruption remarks. API has no explicit "on-time/delayed" flag — caveat delivered.
- 4 ferry data sources documented: TD (static, all routes), Sun Ferry (real-time ETA), HKKF (real-time ETA), Star Ferry (static, 2 routes).
- Central→Cheung Chau is operated by Sun Ferry (not HKKF) — operator mapping is non-obvious.

**Datasets discovered:** `hk-td-wcms_8-ferry-services-tt-ft` (TD static timetables), `sunferry-eta-eta` (Sun Ferry real-time ETA), `hkkf-hkkfdata-hkkf-eta-data` (HKKF ETA), `starferry-starferry-ferry-service-timetables-and-fare-tables-of-star-ferry` (Star Ferry static)
**Reference files created:** `transport-ferry.md`
**Failures logged:** ferry/pier/harbour/outlying/ETA keywords → 0 CKAN results (except Star Ferry); HKKF API trailing slash requirement

---

## Summary

| # | Question | Datasets found | Ref files | Failures logged | Key finding |
|---|----------|---------------|-----------|-----------------|-------------|
| Q1 | Port cargo + vessel counts | 2 | 2 | 2 | Non-JSON resources broken; CSV download returns HTML |
| Q2 | District unemployment + PRH estates | 2 | 2 | 3 | UR by district doesn't exist; LFPR is proxy; multi-word crash |
| Q3 | Elderly services + centres | 7 | 2 | 2 | Chinese keywords crash + not indexed; SWD CSVs are UTF-16-LE tab |
| Q4 | Air quality at Causeway Bay | 4 | 1 | 2 | All endpoints live (better than expected); 4 formats in one domain |
| Q5 | Next ferry Central→Cheung Chau | 4 | 1 | 2 | Real-time ETA available; operator mapping non-obvious |
| **Total** | | **19** | **8** | **11** | |

---

## Q6 — Crime trend by district (security + time-series)

> "Which Hong Kong district saw the largest year-on-year percentage increase in reported violent crimes in the most recent full year, and what was the change?"

**Untested axes probed:**
- Security category (`law-and-security` → `security-` prefix)
- HK Police crime statistics (likely CSV/XLSX, not JSON)
- Year-on-year percentage change from a time-series table
- District-level aggregation across offense types

**Expected challenges:**
- CKAN search for "crime" or "violent crime" may return 0 results or unrelated datasets
- Data may be in Excel/CSV with multiple sheets requiring format detection
- Need to identify "violent crime" row labels and sum across subcategories

**Potential datasets:** HK Police crime statistics tables on data.gov.hk
**Potential reference file:** `security-crime.md`
**Potential failures logged:** "crime" / "violent crime" keyword indexing gaps; CSV/XLSX parsing quirks

---

## Q7 — School capacity vs child population (education + population cross-join)

> "Which district has the most primary school places per 5-year-old child, and is it above or below the territory-wide average?"

**Untested axes probed:**
- Education category (`education-` prefix)
- Cross-dataset join requiring 3 sources: school places by district, child population by district, district name normalization
- Ratio calculation and territory-wide average
- Age-band matching (5-year-olds vs primary school entry age)

**Expected challenges:**
- School data may list "number of schools" rather than "number of places"
- Population data uses different district name variants (Censtatd vs Housing Authority)
- May need proxy: "primary schools per child" if places are unavailable

**Potential datasets:** Censtatd school statistics, Censtatd population by district/age
**Potential reference files:** `education-schools.md` (update), `population-census.md` (update)
**Potential failures logged:** school places metric not directly available; district name variants

---

## Q8 — Mainland tourism + hotel occupancy (tourism + commerce cross-dataset)

> "How many Mainland Chinese visitors arrived in Hong Kong last month, and what was the average hotel occupancy rate for the same period?"

**Untested axes probed:**
- Tourism category (`tourism-` prefix)
- Visitor arrivals by country/region filter
- Hotel occupancy rate dataset (commerce/tourism boundary)
- Temporal alignment of two datasets with different update schedules

**Expected challenges:**
- "Mainland China" may be labeled as "Mainland", "Chinese Mainland", "内地", or similar
- Hotel occupancy data may be monthly/quarterly and lagged differently from arrivals
- Cross-dataset answer requires both datasets to be live and aligned

**Potential datasets:** Censtatd visitor arrivals, HKTB/C&SD hotel occupancy
**Potential reference files:** `tourism-arrivals.md`, `commerce-hotel-occupancy.md`
**Potential failures logged:** tourism keyword indexing gaps; Mainland China label ambiguity

---

## Summary (including Q6–Q8)

| # | Question | Datasets found | Ref files | Failures logged | Key finding |
|---|----------|---------------|-----------|-----------------|-------------|
| Q1 | Port cargo + vessel counts | 2 | 2 | 2 | Non-JSON resources broken; CSV download returns HTML |
| Q2 | District unemployment + PRH estates | 2 | 2 | 3 | UR by district doesn't exist; LFPR is proxy; multi-word crash |
| Q3 | Elderly services + centres | 7 | 2 | 2 | Chinese keywords crash + not indexed; SWD CSVs are UTF-16-LE tab |
| Q4 | Air quality at Causeway Bay | 4 | 1 | 2 | All endpoints live (better than expected); 4 formats in one domain |
| Q5 | Next ferry Central→Cheung Chau | 4 | 1 | 2 | Real-time ETA available; operator mapping non-obvious |
| Q6 | Crime trend by district | ? | ? | ? | Security category; CSV/XLSX time-series; district aggregation |
| Q7 | School capacity vs child population | ? | ? | ? | Education + population join; ratio; age-band matching |
| Q8 | Mainland tourism + hotel occupancy | ? | ? | ? | Tourism + commerce; regional filter; temporal alignment |

**Cumulative impact on skill:**
- Verified datasets: 21 → 32 (11 new)
- Reference files: 24 → 32 (8 new)
- TASKS.md: 0 → 21 tasks identified
- Failure-log: 1 → 12 entries
- Strategy-registry: 1 → 7 category sections + 18 patterns
