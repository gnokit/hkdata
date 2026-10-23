# Cross-cutting pitfalls (not a runnable program)

**Do not** treat this file as a callable function. It is agent memory for traps
that span many datasets. Per-endpoint gotchas live in each program's `Quirks:`
docstring (and are embedded by `reindex`). Read this when discovery fails or
before inventing a new search strategy.

Also see: `data/unavailable.jsonl` (topics confirmed missing on data.gov.hk).

---

## Search & catalog

1. **Prefer `bash ./hk.sh catalog-search` / `programs-search`.**  
   Raw CKAN `package_search` historically had no URL encoding: multi-word
   queries (`air quality`) and Chinese (`長者`) broke or returned 0. This skill
   uses the local Chroma catalog (~3,822 datasets); do not reintroduce raw
   CKAN `package_search` as Path B.

2. **CKAN / Solr covered only ~631 packages** historically. Keywords that often
   **missed** even when datasets existed:
   - ferry / outlying / Sun Ferry ETA / HKKF (TD licensed ferry id lacks
     "ferry" in indexed metadata; Star Ferry was indexed)
   - AQHI / pollution / air quality (EPD airteam)
   - crime / violent crime (HKPF)
   - Chinese elderly-service terms (中文索引不全)
   - vague singles like `district`, `facility`, `centre`, `ship`, `ETA`

3. **Strategy when a topic "should" exist but search is empty:**  
   - English synonym first (`elderly` not only `長者`)  
   - `programs-search` → `catalog-search` → web `site:data.gov.hk …` →
     `package_show` / `info` / `test`  
   - Check `data/unavailable.jsonl` before declaring "not found" as a bug

4. **Single-word vs multi-word:** Prefer a distinctive single English token for
   catalog probes when unsure; then narrow. Multi-word is fine on
   `catalog-search` (proper encoding), but vague words (`district`) return
   land/property noise — pair with the domain term (`unemployment`, `elderly`).

---

## Encoding & download traps

5. **SWD elderly CSVs** are UTF-16-LE + **tab**-delimited despite `.csv`.  
   See `swd.elderly_centres` Quirks. Same pattern: DE/DCU, STE lists.

6. **Censtatd `wbr.html?download_csv=1`** returns **HTML**, not CSV — the flag
   is client-side JS. Always use `https://www.censtatd.gov.hk/api/get.php?id=…`.  
   See `censtatd.port_cargo_throughput` Quirks.

7. **HKPF crime detail CSV** is Big5, not UTF-8 (`hkpf.crime_detail`).

8. **EDB / many gov CSVs** need `utf-8-sig` (BOM). Housing Authority districts
   use `&`; Censtatd uses `and` — normalise before joins.

---

## Library (HKPL webcat)

9. Endpoint is `https://webcat.hkpl.gov.hk/search/syndication` — **not**
   `/rss/new`. Sort values: `sort=relevance` and `sort=dateNewest` — **not**
   `sort=date`.

10. `match_1=PHRASE` must match the **catalogue title string** (譯名 may differ
    from user wording). On 0 hits: shorter unique phrase or English original.
    Cap = 5 items/query; full page may mean more exist.  
    See `lcsd.catalogue_search` / `lcsd.new_arrivals` Quirks.

11. No full holdings REST/OAI-PMH API on data.gov.hk — RSS + HTML scrape only
    (`data/unavailable.jsonl` topic on advanced catalogue API).

---

## Ferry / ETA

12. **HKKF** `/opendata/route/` **requires trailing slash**; `/eta/{id}/{dir}`
    must **not** have one. Bare `/opendata/pier/` → 422 (needs extra params).  
    Central↔Cheung Chau live ETA is **Sun Ferry**, not HKKF.  
    See `td.ferry` Quirks (`hkkf_routes`, `hkkf_eta`, `sunferry_eta`,
    `ferry_with_eta`).

---

## Parking

13. Street meter inventory: header on **line 3**; PoleId > 90000 = test;
    status NU = exclude. ALS always returns something — check score.
    See `td.parking_street` / `td.parking_near` Quirks.

---

## Employment / crime / education proxies

14. **No District Council unemployment rate** on data.gov.hk (GHS sample).  
    Proxy: `labour_force_by_district` (LF / LFPR only). LFPR ≠ UR.

15. **No district violent-crime series** — territory-wide HKPF CSVs only.

16. **No 殺校 closure list** — proxy school-register diffs + net enrolment
    tables; verify against EDB/LegCo. Exact primary **places** (not enrolment)
    by district / age-5 demand is also unpublished — say so.

---

## Source

Collected from repeated Path B discovery failures and Quirks that span more
than one program. Prefer Quirks on the owning function when the trap is
endpoint-specific; keep only cross-cutting items here.
