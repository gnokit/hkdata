---
name: hkdata
description: >
  Answer Hong Kong queries with reliable, accurate data sourced directly from
  data.gov.hk official APIs. Includes verified integrations for transport,
  weather, location, population, finance, health, employment, commerce,
  recreation, education, and city services. Use when the user asks about Hong
  Kong statistics, public data, government datasets, transport schedules,
  weather, facilities, or demographics. Trigger phrases: "hkdata", "Hong Kong
  data", "data.gov.hk", "HK statistics", "HK population", "HK weather",
  "MTR/bus schedule", "HK public holidays", "badminton courts", "schools in HK".
---

# HK Data.gov.hk Query Tool

Search and retrieve data from Hong Kong's open data portal (data.gov.hk).
This skill provides a structured discovery workflow for finding, testing, and
documenting government datasets, plus a registry of pre-verified APIs.

**Scope: Hong Kong data.gov.hk dataset discovery and query only.**
General web search, non-HK data, or data from non-government sources is handled
by the agent's native web search tools, not this skill.

> **Out-of-scope redirect:** This request is outside the scope of hkdata.
> For non-Hong-Kong data or non-government sources, use web search directly.

---

## Dependencies

| Package / Capability | Purpose | Install / Note |
|----------------------|---------|----------------|
| `curl` | HTTP requests to data.gov.hk CKAN API | Pre-installed on macOS/Linux |
| `python3` | JSON parsing in shell scripts | Pre-installed on macOS/Linux |
| `data.gov.hk CKAN API` | Official open data portal | No auth required for most endpoints |
| `web_search_exa` or `SearchWeb` | Fallback when CKAN search returns 0 results | Built-in agent tool |
| `Agent` tool | Spawn subagent for discovery workflow | Built-in agent tool |

---

## Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `SKILL_PATH` | `.agents/skills/hkdata` | Root path of this skill |
| `BIN_PATH` | `./bin` | Shell scripts location |
| `REFERENCES_PATH` | `./references` | Verified dataset docs |
| `API_BASE_URL` | `https://data.gov.hk/en-data/api/3/action/` | CKAN API base |
| `RESULTS_PER_PAGE` | `50` | Pagination page size |
| `SUBAGENT_MODEL` | `minimax-m2.7` | Model for discovery subagent |

---

## Step 1 — Check Verified Datasets

**Command:**
```bash
ls ./references/
```

**What it does:**
- Lists all pre-verified dataset reference files
- Checks if the user's query matches any known dataset by name or category
- If a match is found, reads the corresponding `{category}-{dataset}.md` file

**Output:**
- Direct answer from verified dataset (skip to query response)
- Or confirmation that no verified dataset matches, proceed to Step 2

---

## Step 2 — Search data.gov.hk

**Command:**
```bash
bash ./bin/hkdata-find.sh "<keyword>"
```

**What it does:**
- Queries the CKAN `package_search` API for datasets matching the keyword
- Returns dataset ID, title, and description for up to 50 results
- If 0 results, triggers the auto-fallback (see Error Handling)

**Output:**
- List of candidate datasets: `dataset-id | Title | Description`
- Pagination info if more than 50 results

**CLI flags:**
| Flag | Default | Description |
|------|---------|-------------|
| `--page N` | `1` | Show page N of results |

---

## Step 3 — Inspect Promising Dataset

**Command:**
```bash
bash ./bin/hkdata-info.sh "<dataset-id>"
```

**What it does:**
- Calls CKAN `package_show` API for the selected dataset ID
- Returns full metadata: resources, formats, update frequency, provider
- Identifies the actual API endpoint or download URL

**Output:**
- Raw JSON metadata from data.gov.hk
- Extracted: resource URLs, formats, organization, tags

---

## Step 4 — Test API Endpoint

**Command:**
```bash
curl -s "<resource-url>" | python3 -m json.tool | head -50
```

**What it does:**
- Executes a live request to the dataset's API endpoint
- Validates the response is valid JSON/XML/CSV
- Confirms the data answers the user's query

**Output:**
- Sample data confirming the endpoint works
- Or error if endpoint is unreachable/invalid

---

## Step 5 — Document New Dataset (Mandatory)

**Command:**
```bash
cp ./references/template.md \
   ./references/<category>-<dataset>.md
```

**What it does:**
1. Determines category from data.gov.hk tags (see Category Mapping)
2. Creates `references/{category}-{dataset}.md` from template
3. Updates `references/index.md` with new entry
4. Updates SKILL.md Verified Datasets table (below)
5. Updates `failure-log.md` if fallback was used
6. Updates `strategy-registry.md` if new search strategy succeeded

**Output:**
- New reference file: `references/{category}-{dataset}.md`
- Updated `references/index.md`
- Updated `SKILL.md` (if new dataset added)

**Before claiming completion, verify:**
- [ ] `references/{category}-{dataset}.md` exists
- [ ] `references/index.md` is updated
- [ ] `SKILL.md` Verified Datasets table is updated
- [ ] `failure-log.md` is updated (if fallback used)
- [ ] `strategy-registry.md` is updated (if new strategy discovered)

**If you cannot complete Step 5:** State clearly: "Step 5 incomplete — documentation pending" and explain why.

---

## Full Workflow

```bash
# Step 1: Check verified
ls ./references/

# Step 2: Search
bash ./bin/hkdata-find.sh "<keyword>"

# Step 3: Inspect
bash ./bin/hkdata-info.sh "<dataset-id>"

# Step 4: Test
curl -s "<resource-url>"

# Step 5: Document
cp ./references/template.md \
   ./references/<category>-<dataset>.md
```

---

## Verified Datasets

| Dataset | Category | Description | Reference |
|---------|----------|-------------|-----------|
| KMB Bus ETA | transport | Real-time bus arrival times | [transport-kmb.md](references/transport-kmb.md) |
| MTR Real-time Train | transport | Next-train arrival times (10s updates) | [transport-mtr.md](references/transport-mtr.md) |
| Sunrise/Sunset | weather | Daily sunrise and sunset times | [weather-sunrise.md](references/weather-sunrise.md) |
| Current Weather | weather | Real-time weather and forecasts | [weather-current.md](references/weather-current.md) |
| Address Lookup | location | Hong Kong address geocoding | [location-address.md](references/location-address.md) |
| Population Statistics | population | HK population by district (mid-2024: 7.52M) | [population-census.md](references/population-census.md) |
| GDP Statistics | finance | GDP, deflator, per capita GDP (2025 growth: 3.5%) | [finance-gdp.md](references/finance-gdp.md) |
| Birth Statistics | health | Live births by sex, crude birth rate (2024: 36,723 births) | [health-births.md](references/health-births.md) |
| Unemployment Rate | employment | Monthly unemployment rate by age/sex (Jan 2026: 3.6%) | [employment-unemployment.md](references/employment-unemployment.md) |
| Consumer Price Index | commerce | Monthly CPI and inflation rate (Jan 2026: 1.1%) | [commerce-cpi.md](references/commerce-cpi.md) |
| Badminton Courts (Free Outdoor) | recreation | Free outdoor badminton courts across 14 HK venues | [recreation-badminton-outdoor.md](references/recreation-badminton-outdoor.md) |
| Badminton Court Sessions | recreation | Real-time session availability at 105 LCSD venues (5-min updates) | [recreation-badminton-sessions.md](references/recreation-badminton-sessions.md) |
| School Statistics | education | Number of schools by type/sector and region (2024: 590 primary schools) | [education-schools.md](references/education-schools.md) |
| Public Holidays | city | Hong Kong public holidays 2024-2026 (official 1823 data) | [city-holidays.md](references/city-holidays.md) |
| PRH Income & Asset Limits | housing | Monthly income/asset limits for public rental housing application | [housing-prh.md](references/housing-prh.md) |
| River Water Quality | environment | Recent DO and BOD5 data at downstream river monitoring stations | [environment-river-water.md](references/environment-river-water.md) |
| Monthly Transport Digest | transport | Monthly CSV stats: passenger journeys, accidents, tunnel flows, licences | [transport-digest.md](references/transport-digest.md) |
| Government Car Parks | city | Government car parks open for public use: locations, spaces, fees | [city-parking.md](references/city-parking.md) |
| Crime Statistics | security | Persons arrested for crime by offence type, age group and sex | [security-crime.md](references/security-crime.md) |
| Cinemas | recreation | HK cinema inventory: locations, screens, seats, coordinates | [recreation-cinema.md](references/recreation-cinema.md) |
| Film Development Fund | recreation | Approved FDF film projects since 2009: titles, funding, dates | [recreation-film-fund.md](references/recreation-film-fund.md) |
| Film Box Office (FDF) | recreation | HK box office revenue for FDF-funded films | [recreation-film-boxoffice.md](references/recreation-film-boxoffice.md) |

---

## Category Mapping

Map data.gov.hk tags to reference file prefixes:

| data.gov.hk Category | Reference Prefix | Example Filename |
|---------------------|------------------|------------------|
| climate-and-weather | `weather-` | weather-sunrise.md |
| transport | `transport-` | transport-kmb.md |
| development | `location-` | location-address.md |
| housing | `housing-` | housing-estates.md |
| health | `health-` | health-clinics.md |
| education | `education-` | education-schools.md |
| environment | `environment-` | environment-air.md |
| city-management | `city-` | city-services.md |
| commerce-and-industry | `commerce-` | commerce-licenses.md |
| employment-and-labour | `employment-` | employment-stats.md |
| finance | `finance-` | finance-budget.md |
| food | `food-` | food-hygiene.md |
| law-and-security | `security-` | security-crime.md |
| population | `population-` | population-census.md |
| recreation-and-culture | `recreation-` | recreation-facilities.md |
| tourism | `tourism-` | tourism-arrivals.md |
| legislature | `legislature-` | legislature-bills.md |
| social-welfare | `welfare-` | welfare-services.md |
| information-technology-and-broadcasting | `it-` | it-licenses.md |
| miscellaneous | `misc-` | misc-other.md |

---

## Quick Reference

```bash
# Find datasets by keyword (shows ID, title, description)
bash ./bin/hkdata-find.sh "transport"

# Paginate through results
bash ./bin/hkdata-find.sh "transport" --page 2

# Get dataset details by ID
bash ./bin/hkdata-info.sh "hk-td-tis_21-etakmb"

# List all verified datasets
ls ./references/
```

### Search Output Format

The `hkdata-find.sh` script displays results as:
```
dataset-id | Title | Description
```

**Example:**
```
hk-censtatd-tablechart-110-02001 | Hong Kong Population - Table 110-02001 : Land area... | Hong Kong Population - Table 110-02001 : Land area...

Showing results 1-50 of 123 (page 1 of 3)
Use --page 2 to see more results
```

---

## Auto-Fallback Trigger

**When `hkdata-find.sh` returns 0 results, automatically trigger fallback:**

1. Read `failure-log.md` to check if this failure pattern is already known
2. Read `strategy-registry.md` to check if a successful strategy exists
3. If known failure → use documented workaround
4. If no known strategy → try web search: `site:data.gov.hk <topic>` to find dataset IDs directly
5. If workaround succeeds → record in both `failure-log.md` AND `strategy-registry.md`
6. If workaround fails → record failure in `failure-log.md` and return "no dataset found"

### Search Fallback: hkdata-find.sh Script Failures

The `hkdata-find.sh` script uses CKAN `package_search` API which may fail to
find datasets with certain keywords (metadata indexing issues). If the script
returns 0 results:

1. **Try alternative keywords** — synonyms, broader terms, or English/Chinese variants
2. **Use web search fallback** — search `site:data.gov.hk <topic>` via web search to find dataset IDs directly
3. **Once ID is found** — use `hkdata-info.sh` or `package_show` API to inspect the dataset

**Example workaround:**
```bash
# Step 1: Script fails
bash ./bin/hkdata-find.sh "badminton"  # 0 results

# Step 2: Use web search to find dataset ID
# Search: "site:data.gov.hk badminton lcsd facility"
# Found: hk-lcsd-facility-facility-bmtc

# Step 3: Inspect directly
bash ./bin/hkdata-info.sh "hk-lcsd-facility-facility-bmtc"
```

---

## Success Path Memory

**After EVERY successful discovery, record the winning strategy:**

1. Open `strategy-registry.md`
2. Add entry: topic → keywords/methods that worked → result
3. This creates a growing "what works" knowledge base for future agents

---

## Weekly Self-Evolution Review (Every 7 Days)

**Process:**
1. Read `failure-log.md` and `strategy-registry.md`
2. Identify patterns: common failure causes, effective fallback strategies
3. Consolidate learnings into SKILL.md (update relevant sections)
4. Archive old/deprecated entries
5. Update `failure-log.md` and `strategy-registry.md` with cleaned state

**Trigger:** Spawn subagent with task "hkdata weekly self-evolution review"

---

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
- **Reference:** [population-census.md](references/population-census.md)

---

### Template Structure

All responses should include:
1. **Direct Answer** — The factual answer to the query
2. **Methodology** — Which workflow steps were followed (with checkmarks)
3. **Dataset Details** — Source, ID, API endpoint, documentation reference
4. **Data Quality Note** — Update frequency, data date, any caveats

---

## Subagent Configuration

For complex discovery workflows, spawn a SINGLE subagent to execute Steps 2–5:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Model** | `minimax-m2.7` | High-reasoning model for dataset analysis |
| **Subagent Type** | `coder` | Can execute shell commands and read files |
| **Scope** | Steps 2–5 | Complete discovery and documentation |

**Spawn via Agent tool:**
```
Agent(
  subagent_type="coder",
  model="minimax-m2.7",
  description="hkdata discovery workflow",
  prompt="Read ./SKILL.md and strictly follow Steps 1–5 to answer: <user query>\n\nYou MUST:\n1. Read the SKILL.md file completely\n2. Follow Steps 1–5 exactly as documented\n3. Execute Steps 2–5 yourself (do not ask the main agent)\n4. Return your final answer with the data retrieved, confirmation that documentation was created (if applicable), and any errors encountered."
)
```

**Why a single subagent for Steps 2–5:**
- **Complete isolation** — Discovery context stays in subagent
- **End-to-end execution** — One subagent handles search → inspect → test → document
- **Clean handoff** — Main agent receives only final results
- **Efficient** — No multiple spawn overhead

---

## When No Suitable Dataset Exists

If Steps 2–4 reveal no dataset answers the query:

### Required: Show Exploration Log

**Your answer MUST include:**

1. **Clear statement:** "No suitable dataset found on data.gov.hk"
2. **Exploration log:** List each dataset examined and why it didn't fit
3. **Datasets considered:** Show the search was thorough

**Example:**
> **Answer:** Unable to find real-time AQI data for Hong Kong.
>
> **Exploration Log:**
> 1. ❌ Searched "air quality" → Found 0 datasets
> 2. ❌ Searched "pollution" → Found 0 datasets
> 3. ❌ Searched "AQI" → Found 0 datasets
> 4. ❌ Searched "environment" → Found `hk-epd-noise` (noise pollution only, not air quality)
>
> **Conclusion:** No air quality API available on data.gov.hk

**Why this matters:**
- Prevents false claims of "no data found" without evidence
- Documents dead ends for future queries
- Shows due diligence in the discovery process
- Saves time on repeated searches for the same data

---

## API Notes

- **Base URL:** `https://data.gov.hk/en-data/api/3/action/`
- **Authentication:** Most APIs do not require authentication
- **Formats:** JSON or CSV
- **Rate limits:** Follow data.gov.hk terms of use

---

## Verification Checklist

Before reporting to the user or proceeding to the next step, confirm ALL of the following:

- [ ] The query falls within scope (Hong Kong data.gov.hk data)
- [ ] All expected output files exist (`references/{category}-{dataset}.md`, updated `index.md`)
- [ ] No required fields are null or missing in the API response
- [ ] Dataset metadata matches the query intent (category, description, update frequency)
- [ ] If fallback was used, `failure-log.md` and `strategy-registry.md` are updated
- [ ] All internal paths in documentation point to `./`

**If any check fails:** Stop. Do not generate output. Report which check failed
and the last known good value. Do NOT silently skip or produce partial output.

---

## Error Handling

| Failure Type | Recovery Action |
|---|---|
| Network / download failure | Retry once; if still failing, fall back to most recent verified reference data and flag output as stale with date |
| `hkdata-find.sh` returns 0 results | Trigger auto-fallback: read failure-log → read strategy-registry → web search `site:data.gov.hk <topic>` |
| Missing file / dependency | Verify `curl` and `python3` are installed; verify `./` exists |
| Invalid / corrupt dataset metadata | Skip dataset, log ID, continue with next candidate |
| All datasets failed | Abort entirely; return "No suitable dataset found on data.gov.hk" with exploration log |
| Unexpected API schema | Report exact mismatch; do not attempt to parse |
| API endpoint returns error | Check if auth is required; if not, document as broken endpoint in failure-log.md |

**Stale data rule:** If the skill falls back to cached/local data, the output MUST
include a visible warning:
```
⚠️ Stale Data: [source] — last updated [YYYY-MM-DD]. Live fetch failed.
```

---

## Known Failure Patterns

| Symptom | Root Cause | Permanent Fix |
|---------|------------|---------------|
| `hkdata-find.sh "badminton"` returns 0 results | CKAN `package_search` metadata indexing incomplete for LCSD facility datasets | Use web search fallback: `site:data.gov.hk badminton lcsd` → find IDs directly → use `hkdata-info.sh` |
| `hkdata-find.sh "sport"` returns 0 results | Same as above — "sport" keyword not indexed for LCSD datasets | Use broader web search or known IDs from strategy-registry |
| Subagent fails to create reference file | Permission issue or wrong path | Verify `REFERENCES_PATH` is `./references` |
| Agent tool syntax error | Using legacy `sessions_spawn` instead of `Agent` | Always use `Agent(subagent_type="coder", ...)` as documented in Subagent Configuration |

**When a new failure pattern is discovered:**
1. Fix the immediate issue
2. Add a new row to this table
3. Update the relevant step, script, or verification checklist to prevent recurrence

---

## References

- [data.gov.hk Developer Guide](https://data.gov.hk/en/help/developer-guide)
- [CKAN API Documentation](https://docs.ckan.org/en/latest/api/)
- [HK Census and Statistics Department](https://www.censtatd.gov.hk/)
- [HK Observatory](https://www.hko.gov.hk/)

---

## Last Updated

2026-04-30 (Imported to user scope with harness engineering compliance)
