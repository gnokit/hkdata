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
| `chromadb` | Search store for `catalog-search` | `.venv/bin/pip install -r requirements-vectors.txt` |
| Ollama + `qwen3-embedding:0.6b` | Local multilingual embeddings (1024-dim) | `ollama pull qwen3-embedding:0.6b` |
| Web search tool | Fallback when catalog search returns 0 results | Built-in agent tool |
| Agent tool | Spawn subagent for discovery workflow | Built-in agent tool |

> **First time using this repo?** Follow [`SETUP.md`](SETUP.md) to create the venv,
> pull the Ollama embedding model, and build the ChromaDB store. The catalog shards
> are committed, so no crawl is needed.

---

## Configuration

| Parameter | Value | Description |
|-----------|-------|-------------|
| `SCRIPTS_PATH` | `./scripts` | CLI entry point and thin bash wrappers |
| `REFERENCES_PATH` | `./references` | Verified dataset docs, registry, and search index |
| `LOGS_PATH` | `./logs` | Rendered views of the experience store (failure log / strategy registry) |
| `CATALOG_PATH` | `data/catalog/` (shards, committed) + `.cache/catalog/chroma/` (vectors) | Offline catalog + ChromaDB store |
| `API_BASE_URL` | `https://data.gov.hk/en-data/api/3/action/` | CKAN API base (`en`/`tc`/`sc` locales) |
| `SUBAGENT_MODEL` | high-reasoning model available in your agent tool | Single subagent for Steps 2–5 |

---

## Step 1 — Check Past Experience

```bash
.venv/bin/python ./scripts/hkdata.py experience-search "<user query>"
```

Semantic search over past experiences — **positive** (something worked) and
**negative** (a dead end):

- **positive** → read the cited `references/...md` and follow the recipe; then Step 3/4
  to refresh the endpoint if the data is live.
- **negative** (`outcome: unavailable`) → the data is not on data.gov.hk; answer
  accordingly **without re-searching**.
- no useful hit → proceed to Step 2.

> **Experiences carry a date.** They can be superseded by a newer dataset or a better
> method, so check `date` (and `last_verified`). For live/real-time data, still run
> Step 3–4 rather than trusting an old card.

`search-local` remains available for a plain lexical lookup of the curated
reference index, but Step 1 is the semantic experience search.

---

## Step 2 — Search the Full Catalog

```bash
.venv/bin/python ./scripts/hkdata.py catalog-search "<user query>"
```

ChromaDB search over all **3,822** datasets (dense multilingual embeddings fused with a
keyword pass). If the store is empty, build it once:

```bash
python3 ./scripts/hkdata.py catalog-sync --full --lang en,tc   # crawl (resumable)
.venv/bin/python ./scripts/hkdata.py catalog-embed              # embed into ChromaDB
```

> **Why not the CKAN search API:** `package_search` is Solr-backed and indexes only
> ~631 of the 3,822 datasets that `package_list` returns — it misses `badminton`,
> `vessel`, `AQHI`, `ferry`, and Chinese keywords. `catalog-search` covers the whole
> catalog and understands Chinese.

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
# record the experience (positive or negative) and index it
.venv/bin/python ./scripts/hkdata.py experience-log \
  --kind positive --topic "<short description>" \
  --pattern "<example query>" --dataset <dataset-id> \
  --method "<what worked>" --source references/<category>-<dataset>.md
python3 ./scripts/hkdata.py log-render
```

For a dead end (no dataset exists), log a **negative** experience instead:

```bash
.venv/bin/python ./scripts/hkdata.py experience-log \
  --kind negative --topic "<what was asked>" --outcome unavailable \
  --method "<what was searched>" --caveat "<closest proxy>"
```

`experience-log` appends to `data/experiences.jsonl` **and** indexes the card
immediately (needs Ollama). If ChromaDB is unavailable it appends to the JSONL only —
run `experience-embed` later.

**Step 5 is a hard gate.** It is not complete until **all** of these are true:
- [ ] Query is in scope (Hong Kong data.gov.hk data)
- [ ] `references/{category}-{dataset}.md` exists
- [ ] `references/index.md` is updated
- [ ] `references/search-index.json` is rebuilt
- [ ] `data/experiences.jsonl` has a positive **or** negative card (`experience-log`)
- [ ] Markdown views are re-rendered with `log-render` (into `logs/failure-log.md` / `logs/strategy-registry.md`)
- [ ] API response has no missing required fields and matches query intent
- [ ] Internal paths in documentation point to `./`

If any item cannot be completed, state: "Step 5 incomplete — documentation pending" and list which items failed.

---

## Full Workflow

Before starting Steps 2–5, create a task list with one item per step. Mark each item `in progress` before executing it and `completed` when done. If a fallback is triggered, add it as a sub-task.

```bash
# Step 1: Check past experience (semantic; run from the venv)
.venv/bin/python ./scripts/hkdata.py experience-search "<user query>"

# Step 2: Search the full catalog (ChromaDB; run from the venv)
.venv/bin/python ./scripts/hkdata.py catalog-search "<user query>"

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
.venv/bin/python ./scripts/hkdata.py experience-log --kind positive \
  --topic "..." --dataset <dataset-id> --method "..."
python3 ./scripts/hkdata.py log-render
```

---

## Command Summary

| Command | Purpose |
|---------|---------|
| `.venv/bin/python ./scripts/hkdata.py experience-search "<query>"` | Semantic search over past experiences, ± (Step 1) |
| `.venv/bin/python ./scripts/hkdata.py experience-log --kind positive\|negative …` | Record + index an experience (Step 5) |
| `.venv/bin/python ./scripts/hkdata.py experience-embed` | Build the experience index from `data/experiences.jsonl` |
| `python3 ./scripts/hkdata.py experience-migrate` | Regenerate experiences from references + logs |
| `python3 ./scripts/hkdata.py search-local "<query>"` | Lexical lookup of the curated reference index |
| `.venv/bin/python ./scripts/hkdata.py catalog-search "<query>"` | ChromaDB search over the full catalog (Step 2) |
| `python3 ./scripts/hkdata.py catalog-sync [--full] [--refresh] [--lang en,tc]` | Seed/crawl the offline catalog |
| `.venv/bin/python ./scripts/hkdata.py catalog-embed [--model ...]` | Build the ChromaDB vector store (Ollama) |
| `python3 ./scripts/hkdata.py catalog-status` | Show catalog coverage and vector count |
| `python3 ./scripts/hkdata.py info "<id>" ...` | CKAN `package_show` metadata (Step 3) |
| `python3 ./scripts/hkdata.py test "<url>" ...` | Test endpoint and detect format (Step 4) |
| `python3 ./scripts/hkdata.py reindex` | Rebuild `references/search-index.json` (curated docs) |
| `python3 ./scripts/hkdata.py log-search "<kw>" ...` | Lexical search of experiences (by kind) |
| `python3 ./scripts/hkdata.py log-render` | Regenerate the `logs/` markdown views |
| `bash ./scripts/hkdata-info.sh "<id>"` | Backward-compatible wrapper for `info` |

---

## Verified Datasets

Verified datasets are listed in [`references/index.md`](references/index.md). Find them
semantically via the experience index (Step 1), or lexically with:

```bash
python3 ./scripts/hkdata.py search-local "<query>"
```

The category → filename prefix mapping is in [`references/category-mapping.md`](references/category-mapping.md).

---

## Auto-Fallback Trigger

When Step 1 (experience) and Step 2 (`catalog-search`) both return nothing useful:

1. Search structured logs: `python3 ./scripts/hkdata.py log-search "<topic>" "0 results"`
2. If a known strategy exists → use it; otherwise web search `site:data.gov.hk <topic>`
3. Record the outcome as an experience:
   `.venv/bin/python ./scripts/hkdata.py experience-log --kind negative …`
   then `python3 ./scripts/hkdata.py log-render`

**Example:** `catalog-search "badminton"` → finds `hk-lcsd-facility-facility-bmtc` →
`info "hk-lcsd-facility-facility-bmtc"` → Step 5 logs the positive experience so the
next identical question is answered straight from Step 1.

---

## Success Path Memory

After every successful discovery, record the topic, working keywords and method as a
**positive experience** (`experience-log --kind positive …`); after a dead end, record
a **negative** one. Then run `log-render` to refresh the markdown views in `logs/`.

---

## Weekly Self-Evolution Review (Every 7 Days)

**Process:**
1. Read `data/experiences.jsonl` (and the rendered views in `logs/`)
2. Identify patterns: common failure causes, effective fallback strategies,
   experiences whose `date` is stale or superseded
3. Update `references/workflow-guides.md` and `AGENTS.md` if guidance changes
4. Archive/dedupe experiences, then `experience-migrate` + `experience-embed`
5. Run `python3 ./scripts/hkdata.py log-render` after cleanup

**Trigger:** Spawn a single subagent with task "hkdata weekly self-evolution review"

---

## Subagent Configuration

For complex discovery workflows, spawn a **single subagent** with shell and file access to execute Steps 2–5 end-to-end. Requirements: one agent only, shell + file access, high-reasoning model. See [`references/workflow-guides.md`](references/workflow-guides.md) for a worked example and response templates.

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

2026-09-27 (Offline catalog: `package_list`+`package_show` → JSONL shards → ChromaDB search; CKAN `package_search` retired)
