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
| `catalog-search` returns no useful results | Try `log-search` → web search `site:data.gov.hk <topic>`; if the store is empty, run `catalog-sync --full` then `catalog-embed` |
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

## Offline Catalog (the discovery path)

CKAN's `package_search` is a **Solr-backed index covering only ~631 of the ~3,822
datasets** that the DB-backed `package_list` returns, so it is no longer used. The
catalog is crawled once and searched through ChromaDB:

```bash
python3 ./scripts/hkdata.py catalog-sync --full --lang en,tc   # crawl (resumable)
.venv/bin/python ./scripts/hkdata.py catalog-embed              # embed into ChromaDB
.venv/bin/python ./scripts/hkdata.py catalog-search "康文署羽毛球場"
python3 ./scripts/hkdata.py catalog-status                      # coverage report
python3 ./scripts/hkdata.py catalog-sync --refresh              # re-fetch 14-day RSS changes
```

- Seed: `references/catalog-names.json` (sorted IDs, committed).
- Shard store: `data/catalog/catalog-NNN.jsonl` (500 datasets per shard, committed) —
  a **sanitized** `package_show` projection (title/notes/org/groups/tags/resources +
  `locales.{tc,sc}`). Personal contact fields are stripped on write, so the shards
  carry no maintainer emails/phones.
- Search store: `.cache/catalog/chroma/` (ChromaDB, cosine, gitignored). Rebuild it
  from shards with `catalog-embed`; it never needs a re-crawl.
- Bootstrap: `catalog-sync --full` (~58 min at 2 req/s, resumable). Add `--lang en,tc`
  to also fetch Traditional Chinese metadata from the `tc-data` endpoint (a second
  ~58 min pass over the same 3,822 IDs).

### Search behaviour

`catalog-search` fuses rankings from ChromaDB with Reciprocal Rank Fusion:

1. **Dense pass** — local Ollama embeddings (`qwen3-embedding:0.6b`, multilingual,
   1024-dim) over the en + tc document text.
2. **Keyword pass** — the *same* dense query, restricted per token by a
   case-insensitive `$regex` `where_document` filter. Chroma has no ranked BM25,
   so this narrows candidates to ones containing the token while the dense
   similarity still ranks them.

**Alias expansion:** before searching, keys in [`aliases.json`](aliases.json) that
appear in the query are expanded — e.g. `康文署` → `康樂及文化事務署` / `LCSD` — and
the expansions are added to the dense query and used as extra keyword tokens.
Add a mapping there when a common abbreviation misses.

Documents are keyed by a `text_hash`, so `catalog-embed` only re-embeds changed
datasets; aliases and fusion changes need no re-embedding.

## Known Failure Patterns

| Symptom | Root Cause | Permanent Fix |
|---------|------------|---------------|
| `catalog-search` returns nothing at all | Vector store not built, or catalog not crawled | `catalog-sync --full --lang en,tc` → `catalog-embed` → `catalog-search` |
| `catalog-search` says "ChromaDB is not installed" | Search runs only from the venv | `.venv/bin/python ./scripts/hkdata.py catalog-search "…"` |
| Chinese abbreviation (e.g. `康文署`) not found | Abbreviations are coined truncations; the full form (`康樂及文化事務署`) is in the tc metadata | Dense embeddings bridge it (cos ≈ 0.79) and `aliases.json` expands it deterministically — add a mapping if one is missing |
| A dataset the CKAN API used to return is now missing | CKAN `package_search` was retired (Solr covered only ~631/3,822) | Use `catalog-search`, which covers the full catalog |
| Subagent fails to create reference file | Permission issue or wrong path | Verify references are written to `./references` |
| Agent tool syntax error | Legacy spawn syntax | Use your agent tool's equivalent of a single coder subagent with shell access |

When a new failure pattern is discovered, fix it, add a row here, and update the relevant step or checklist.
