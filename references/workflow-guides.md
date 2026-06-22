# Workflow Guides

Supplementary guidance for the hkdata discovery workflow.

## Query Response Template

When answering queries using this skill, follow this structure:

### Example: "How many people living in Hong Kong now?"

**Answer:**
According to the Census and Statistics Department (data.gov.hk):

**Hong Kong Population (mid-2024): 7,523,000**

**Methodology:**
Followed hkdata/SKILL.md discovery workflow:
1. ✅ Checked verified datasets — Found `population-census.md`
2. ✅ Read reference file — Confirmed API endpoint
3. ✅ Executed API — Retrieved mid-2024 population data

**Dataset Details:**
- **Source:** Census and Statistics Department
- **Dataset ID:** `hk-censtatd-tablechart-110-02001`
- **API:** `https://www.censtatd.gov.hk/api/get.php?id=110-02001&lang=en&full_series=1`
- **Reference:** [population-census.md](population-census.md)

### Template Structure

All responses should include:
1. **Direct Answer** — The factual answer to the query
2. **Methodology** — Which workflow steps were followed (with checkmarks)
3. **Dataset Details** — Source, ID, API endpoint, documentation reference
4. **Data Quality Note** — Update frequency, data date, any caveats

---

## Cross-Dataset Composition

Some questions require combining two or more datasets:

1. **Identify the join need** — e.g., "unemployment by district" needs unemployment (not available) + labour force by district (proxy) + district normalization.
2. **Normalize join keys** — especially district names:
   - Censtatd form uses `and` (e.g., `Central and Western`)
   - Housing Authority uses `&` (e.g., `Central & Western`)
   - Use `normalize_district()` from the Python CLI or standardize to the Censtatd form
3. **Fetch both datasets**, normalize keys in Python, and join
4. **Cite both datasets** in the answer and state the join key

---

## Proxy Indicators

If the exact metric is unavailable, a related published metric may be used as a proxy **only if** you explicitly state it:

- Define the proxy: a metric that correlates with the requested metric but is not identical
- Required caveat: "X is not available on data.gov.hk; using Y as a proxy because Z"
- The caveat must appear in the final answer, not only in the methodology

**Example:** District-level unemployment rate is not published; use Labour Force Participation Rate (LFPR) by district as the closest available proxy, with the caveat that LFPR ≠ unemployment rate.

---

## Data Temporality

Classify every dataset you use and adjust "latest available" language accordingly:

| Type | Update pattern | Example |
|------|----------------|---------|
| **Real-time feed** | Sub-daily updates, rolling window, no historical archive via API | Vessel arrivals XML (36h window) |
| **Historical series** | Periodic (monthly/quarterly/annual), full time series, lag | GDP, CPI, unemployment |
| **Static inventory** | Updated as needed, point-in-time snapshot | School list, car parks |

State the temporality in the answer when it affects interpretation (e.g., "last month cannot be answered with a 36-hour rolling snapshot").

---

## Known Broken Endpoints

- **Censtatd `wbr.html?download_csv=1`** — returns an HTML viewer page, not CSV. Use the equivalent Censtatd JSON API (`api/get.php?id=<table-id>`) instead.

---

## Error Handling

| Failure Type | Recovery Action |
|---|---|
| Network / download failure | Retry once; if still failing, fall back to most recent verified reference data and flag output as stale with date |
| `hkdata.py search` returns 0 results | Trigger auto-fallback: `hkdata.py log-search` → web search `site:data.gov.hk <topic>` |
| Missing file / dependency | Verify `python3` is installed; verify `./` exists |
| Invalid / corrupt dataset metadata | Skip dataset, log ID, continue with next candidate |
| All datasets failed | Abort entirely; return "No suitable dataset found on data.gov.hk" with exploration log |
| Unexpected API schema | Report exact mismatch; do not attempt to parse |
| API endpoint returns error | Check if auth is required; if not, document as broken endpoint in `logs/failure-log.jsonl` |

**Stale data rule:** If the skill falls back to cached/local data, the output MUST include a visible warning:
```
⚠️ Stale Data: [source] — last updated [YYYY-MM-DD]. Live fetch failed.
```

---

## Known Failure Patterns

| Symptom | Root Cause | Permanent Fix |
|---------|------------|---------------|
| `hkdata.py search "badminton"` returns 0 results | CKAN `package_search` metadata indexing incomplete for LCSD facility datasets | Use `log-search`, then web search fallback: `site:data.gov.hk badminton lcsd` → find IDs directly → use `hkdata.py info` |
| `hkdata.py search "sport"` returns 0 results | Same as above | Use broader web search or known IDs from strategy-registry |
| `hkdata.py search "vessel"` / `"ship"` / `"arrival"` returns 0 results | Marine Department datasets not indexed | Use `log-search "vessel"`, then web search `site:data.gov.hk vessel arrival marine department` |
| `hkdata.py search "AQHI"` / `"pollution"` returns 0 results | EPD airteam datasets not indexed | Use `log-search "AQHI"`, then web search `site:data.gov.hk AQHI EPD monitoring station` |
| `hkdata.py search "ferry"` only returns Star Ferry | TD, Sun Ferry, and HKKF datasets not indexed | Use `log-search "ferry"`, then web search `site:data.gov.hk ferry timetable outlying island` |
| Subagent fails to create reference file | Permission issue or wrong path | Verify references are written to `./references` |
| Agent tool syntax error | Legacy spawn syntax | Use your agent tool's equivalent of a single coder subagent with shell access |

When a new failure pattern is discovered, fix it, add a row here, and update the relevant step or checklist.
