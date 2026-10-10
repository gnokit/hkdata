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

Citation rules (see also the *Answer Contract* in [`SKILL.md`](../SKILL.md)):

- Always state the **data's own timestamp in HKT**, separately from "retrieved at".
  e.g. *"figures are as at 2026-03-13 (HKT); retrieved 2026-10-07 09:40 HKT."*
- Always give the **dataset ID** and the **exact endpoint URL** you queried.
- **Rows → table, trend → chart.** A chart must label its source dataset and
  temporality (real-time / historical / static).
- A procedural question ("how do I apply…", "what forms…") is rarely a dataset:
  data.gov.hk carries statistics and fee tables, not application steps. Point to
  the department's site and say so, instead of logging a "dataset miss".

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

**Broad first, then narrow.** A single phrase often maps to several datasets. Ask
"what datasets mention `<concept>` at all" (`catalog-search "<concept>"`) before
picking one. Example — *"where can I park?"* is not one dataset: it is
**government car parks** (`city-parking`) + **on-street meters** + **non-metered
sensor spaces**, each a separate source that must be combined for a full answer.
When a question spans several datasets, say so and enumerate them rather than
answering from the first hit.

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
- **`geodata.gov.hk` is retired.** Geo-spatial endpoints that used to live there
  have moved to the CSDI Portal — `www.map.gov.hk/gs/api/...` (see the CSDI API
  docs). Do not keep hitting the old `geodata.gov.hk` URLs; treat any reference
  to them as a `pitfall` and re-route to `map.gov.hk`.
- **403 without a User-Agent.** Some department APIs (Censtatd, LandsD, map APIs)
  reject the bare Python `urllib` agent. The CLI sets a browser-like User-Agent on
  every fetch; if you hit a 403 from your own script, add that header rather than
  assuming the endpoint is down.

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
| API endpoint returns error | Check if auth is required; if not, record a negative experience (`experience-log --kind negative`) |
| Endpoint rejects the Python client | Retry with `curl` — some endpoints block non-browser clients; the CLI already sends a browser-like User-Agent, so copy that header into any ad-hoc fetch |

**Stale data rule:** If the skill falls back to cached/local data, the output MUST include a visible warning:
```
⚠️ Stale Data: [source] — last updated [YYYY-MM-DD]. Live fetch failed.
```

---

## API Notes

- **Base URL:** `https://data.gov.hk/en-data/api/3/action/`
- **Locales:** swap the `en-data` segment for `tc-data` (Traditional Chinese) or `sc-data` (Simplified Chinese)
- **Authentication:** Most APIs do not require authentication
- **Formats:** JSON, XML, or CSV
- **User-Agent:** The CLI sets a browser-like User-Agent globally
- **Rate limits:** Follow data.gov.hk terms of use

---

## Offline Catalog (the discovery path)

CKAN's `package_search` is a **Solr-backed index covering only ~631 of the ~3,822
datasets** that the DB-backed `package_list` returns, so it is no longer used. The
catalog is crawled once and searched through ChromaDB:

> `$SKILL_DIR` points at the skill root (set by the preamble in
> [`SKILL.md`](../SKILL.md)). If you run from the skill directory you can use
> `bash ./hk.sh …` instead.

```bash
bash "$SKILL_DIR/hk.sh" catalog-sync --full --lang en,tc   # crawl (resumable)
bash "$SKILL_DIR/hk.sh" catalog-embed              # embed into ChromaDB
bash "$SKILL_DIR/hk.sh" catalog-search "康文署羽毛球場"
bash "$SKILL_DIR/hk.sh" catalog-status                      # coverage report
bash "$SKILL_DIR/hk.sh" catalog-sync --refresh              # re-fetch 14-day RSS changes
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

## Embedding backend (pluggable)

Embeddings default to local Ollama (`qwen3-embedding:0.6b`) but any embedding
service can be plugged in. Two backends ship built-in — `ollama` and `openai`
(any OpenAI-compatible `/v1/embeddings` API) — and custom backends drop in
through the `Embedder` interface (see [`SETUP.md`](../SETUP.md) *Integrating a new
backend*).

```bash
export HKDATA_EMBED_PROVIDER=openai              # or "ollama" (default)
export HKDATA_EMBED_MODEL=text-embedding-3-small
export HKDATA_EMBED_URL=https://api.openai.com/v1/embeddings
export HKDATA_EMBED_API_KEY=sk-...
bash "$SKILL_DIR/hk.sh" catalog-embed                       # rebuild with the new provider
bash "$SKILL_DIR/hk.sh" experience-embed
bash "$SKILL_DIR/hk.sh" embed-status                        # confirm "match"
```

The same flags exist per-command (`--provider`, `--model`, `--url`, `--api-key`),
and `--provider` also accepts a dotted path `pkg.module:ClassName` to a custom
backend. Each vector stores a **fingerprint** of its provider+model; switching
providers changes the fingerprint, so `catalog-embed`/`experience-embed` re-embed
everything instead of silently mixing incompatible embedding spaces, and
`embed-status` reports a MISMATCH until you do.

> **Different providers = different vector spaces.** A store built with Ollama must
> be rebuilt from scratch (not searched) when you switch to an API provider.

## Experience outcomes: `unavailable` vs `pitfall`

Two kinds of negative card (see Step 1 of [`SKILL.md`](../SKILL.md)):

| Outcome | Meaning | Step 1 behaviour |
|---|---|---|
| `unavailable` | The data is not published on data.gov.hk | Likely no data — **confirm with a quick `catalog-search` before answering "not available"** (optionally with a proxy); a near-miss card can rank for an unrelated query |
| `pitfall` | This *path* is dead/retired, but the data may live elsewhere | Re-route via the card's `method`/`caveats`, then continue |

Log `pitfall` only when there is a concrete re-route; otherwise `unavailable`.

> **Step 1 is a ranked results page, not a verdict.** `experience-search` returns
> the most relevant cards (paged, `--page`/`--per-page`), withholds cards below a
> similarity floor, and prints `No relevant experience card found.` when nothing
> is close. Apply the cards with judgement — never treat a single negative card as
> proof that no dataset exists.

## Known Failure Patterns

| Symptom | Root Cause | Permanent Fix |
|---------|------------|---------------|
| `catalog-search` returns nothing at all | Vector store not built, or catalog not crawled | `catalog-sync --full --lang en,tc` → `catalog-embed` → `catalog-search` |
| `catalog-search` says "ChromaDB is not installed" | chromadb is missing from the venv | `.venv/bin/pip install -r requirements-vectors.txt`, then retry |
| Chinese abbreviation (e.g. `康文署`) not found | Abbreviations are coined truncations; the full form (`康樂及文化事務署`) is in the tc metadata | Dense embeddings bridge it (cos ≈ 0.79) and `aliases.json` expands it deterministically — add a mapping if one is missing |
| A dataset the CKAN API used to return is now missing | CKAN `package_search` was retired (Solr covered only ~631/3,822) | Use `catalog-search`, which covers the full catalog |
| A `geodata.gov.hk` URL 404s or serves nothing | The geodata.gov.hk portal was retired | Re-route to the CSDI Portal `www.map.gov.hk/gs/api/...`; log a `pitfall` card |
| Subagent fails to create reference file | Permission issue or wrong path | Verify references are written to `./references` |
| Agent tool syntax error | Legacy or over-split spawning | At most one subagent; use your agent tool's equivalent of a single coder subagent with shell access |

When a new failure pattern is discovered, fix it, add a row here, and update the relevant step or checklist.
