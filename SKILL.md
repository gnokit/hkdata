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

> **File size budget:** This file defines the workflow only. It should not grow
> when datasets are added. Verified datasets live in `references/index.md`, the
> category mapping in `references/category-mapping.md`, and experience history
> in `logs/`.

> **Out-of-scope redirect:** This request is outside the scope of hkdata.
> For non-Hong-Kong data or non-government sources, use web search directly.

---

## Dependencies

| Package / Capability | Purpose | Install / Note |
|----------------------|---------|----------------|
| `python3` | Stdlib-only Python CLI (`urllib`, `json`, `csv`, `xml`) | Pre-installed on macOS/Linux |
| `curl` | Optional fallback for endpoints that block Python | Pre-installed on macOS/Linux |
| `data.gov.hk CKAN API` | Official open data portal | No auth required for most endpoints |
| Web search tool | Fallback when CKAN search returns 0 results | Built-in agent tool |
| Agent tool | Spawn subagent for discovery workflow | Built-in agent tool |

---

## Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `SCRIPTS_PATH` | `./scripts` | CLI entry point and thin bash wrappers |
| `REFERENCES_PATH` | `./references` | Verified dataset docs, registry, and search index |
| `LOGS_PATH` | `./logs` | Structured failure log and strategy registry (JSONL + rendered markdown) |
| `API_BASE_URL` | `https://data.gov.hk/en-data/api/3/action/` | CKAN API base |
| `RESULTS_PER_PAGE` | `50` | Default page size |
| `SUBAGENT_MODEL` | high-reasoning model available in your agent tool | Single subagent for Steps 2–5 |

---

## Step 1 — Check Verified Datasets

```bash
python3 ./scripts/hkdata.py search-local "<user query>"
```

If a verified dataset matches, read `references/{category}-{dataset}.md` and answer directly. Otherwise proceed to Step 2.

---

## Step 2 — Search data.gov.hk

```bash
python3 ./scripts/hkdata.py search "<keyword>"
python3 ./scripts/hkdata.py search "<keyword1>" "<keyword2>" --parallel
```

Queries the CKAN `package_search` API. If 0 results, trigger the auto-fallback.

---

## Step 3 — Inspect Promising Dataset

```bash
python3 ./scripts/hkdata.py info "<dataset-id>"
python3 ./scripts/hkdata.py info "<id1>" "<id2>" "<id3>"
```

Calls CKAN `package_show` to get metadata, resources, and endpoint URLs.

---

## Step 4 — Test API Endpoint

```bash
python3 ./scripts/hkdata.py test "<resource-url>"
python3 ./scripts/hkdata.py test "<url1>" "<url2>"
```

Fetches the endpoint and auto-detects JSON/XML/CSV.

---

## Step 5 — Document New Dataset (Mandatory)

```bash
cp ./references/template.md ./references/<category>-<dataset>.md
# fill in the reference file
python3 ./scripts/hkdata.py reindex
python3 ./scripts/hkdata.py log-render
```

**Step 5 is a hard gate.** It is not complete until **all** of these are true:
- [ ] Query is in scope (Hong Kong data.gov.hk data)
- [ ] `references/{category}-{dataset}.md` exists
- [ ] `references/index.md` is updated
- [ ] `references/search-index.json` is rebuilt
- [ ] `logs/failure-log.jsonl` is updated (if fallback used)
- [ ] `logs/strategy-registry.jsonl` is updated (if new strategy discovered)
- [ ] Markdown views are re-rendered with `log-render`
- [ ] API response has no missing required fields and matches query intent
- [ ] Internal paths in documentation point to `./`

If any item cannot be completed, state: "Step 5 incomplete — documentation pending" and list which items failed.

---

## Full Workflow

Before starting Steps 2–5, create a task list with one item per step. Mark each item `in progress` before executing it and `completed` when done. If a fallback is triggered, add it as a sub-task.

```bash
# Step 1: Check verified
python3 ./scripts/hkdata.py search-local "<user query>"

# Step 2: Search
python3 ./scripts/hkdata.py search "<keyword>"
# or multi-keyword batch search:
python3 ./scripts/hkdata.py search "<keyword1>" "<keyword2>" --parallel

# Step 3: Inspect
python3 ./scripts/hkdata.py info "<dataset-id>"
# or inspect multiple candidates:
python3 ./scripts/hkdata.py info "<id1>" "<id2>" "<id3>"

# Step 4: Test
python3 ./scripts/hkdata.py test "<resource-url>"
# or test multiple endpoints:
python3 ./scripts/hkdata.py test "<url1>" "<url2>"

# Step 5: Document
cp ./references/template.md ./references/<category>-<dataset>.md
python3 ./scripts/hkdata.py reindex
python3 ./scripts/hkdata.py log-render
```

---

## Command Summary

| Command | Purpose |
|---------|---------|
| `python3 ./scripts/hkdata.py search-local "<query>"` | Search verified datasets + experience history (Step 1) |
| `python3 ./scripts/hkdata.py search "<kw>" ...` | CKAN `package_search` (Step 2) |
| `python3 ./scripts/hkdata.py info "<id>" ...` | CKAN `package_show` (Step 3) |
| `python3 ./scripts/hkdata.py test "<url>" ...` | Test endpoint and detect format (Step 4) |
| `python3 ./scripts/hkdata.py reindex` | Rebuild `references/search-index.json` |
| `python3 ./scripts/hkdata.py log-search "<kw>" ...` | Search structured failure/strategy logs |
| `python3 ./scripts/hkdata.py log-render` | Regenerate markdown views from JSONL |
| `bash ./scripts/hkdata-find.sh "<kw>"` | Backward-compatible wrapper for `search` |
| `bash ./scripts/hkdata-info.sh "<id>"` | Backward-compatible wrapper for `info` |

---

## Verified Datasets

Verified datasets are listed in [`references/index.md`](references/index.md). Search them locally with:

```bash
python3 ./scripts/hkdata.py search-local "<query>"
```

The category → filename prefix mapping is in [`references/category-mapping.md`](references/category-mapping.md).

---

## Auto-Fallback Trigger

When `hkdata.py search` returns 0 results:

1. Search structured logs: `python3 ./scripts/hkdata.py log-search "<topic>" "0 results"`
2. If known strategy → use it; otherwise web search `site:data.gov.hk <topic>`
3. Record outcome: append to JSONL, then `python3 ./scripts/hkdata.py log-render`

**Example:** `python3 ./scripts/hkdata.py search "badminton"` → 0 results → `log-search "badminton"` → web search → `info "hk-lcsd-facility-facility-bmtc"`.

---

## Success Path Memory

After every successful discovery, append the topic, working keywords, and method to `logs/strategy-registry.jsonl`, then run `log-render`.

---

## Weekly Self-Evolution Review (Every 7 Days)

**Process:**
1. Read `logs/failure-log.jsonl` and `logs/strategy-registry.jsonl` (or rendered `.md` views)
2. Identify patterns: common failure causes, effective fallback strategies
3. Update `references/workflow-guides.md` and `AGENTS.md` if guidance changes
4. Archive old/deprecated entries
5. Run `python3 ./scripts/hkdata.py log-render` after cleanup

**Trigger:** Spawn a single subagent with task "hkdata weekly self-evolution review"

---

## Subagent Configuration

For complex discovery workflows, spawn a **single subagent** with shell and file access to execute Steps 2–5 end-to-end. Requirements: one agent only, shell + file access, high-reasoning model. See [`references/workflow-guides.md`](references/workflow-guides.md) for an OpenCode example and response templates.

---

## Advanced Workflow Guidance

- Response templates, cross-dataset joins, proxy indicators, temporality, and known broken endpoints are documented in [`references/workflow-guides.md`](references/workflow-guides.md).

---

## When No Suitable Dataset Exists

If Steps 2–4 reveal no dataset answers the query, your answer MUST:

1. State clearly: "No suitable dataset found on data.gov.hk"
2. Include an exploration log listing each dataset examined and why it didn't fit
3. If a proxy exists, use it with an explicit caveat (see `references/workflow-guides.md`)

**Example:**
> **Answer:** Unable to find real-time AQI data for Hong Kong.
>
> **Exploration Log:**
> 1. ❌ Searched "air quality" → 0 datasets
> 2. ❌ Searched "pollution" → 0 datasets
> 3. ❌ Searched "AQI" → 0 datasets
> 4. ❌ Searched "environment" → `hk-epd-noise` (noise only)
>
> **Conclusion:** No air quality API available on data.gov.hk

---

## API Notes

- **Base URL:** `https://data.gov.hk/en-data/api/3/action/`
- **Authentication:** Most APIs do not require authentication
- **Formats:** JSON, XML, or CSV
- **User-Agent:** The CLI sets a browser-like User-Agent globally.
- **Rate limits:** Follow data.gov.hk terms of use

---

## Error Handling & Known Patterns

See [`references/workflow-guides.md`](references/workflow-guides.md) for the error-handling table, known failure patterns, and stale-data rules.

---

## References

- [data.gov.hk Developer Guide](https://data.gov.hk/en/help/developer-guide)
- [CKAN API Documentation](https://docs.ckan.org/en/latest/api/)
- [HK Census and Statistics Department](https://www.censtatd.gov.hk/)
- [HK Observatory](https://www.hko.gov.hk/)

---

## Last Updated

2026-06-22 (Python CLI, structured logs, and local search index added)
