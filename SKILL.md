---
name: hkdata
description: >
  Answer Hong Kong queries with accurate data from data.gov.hk official APIs:
  transport, weather, population, finance, health, employment, commerce,
  recreation, education, city services. Use when the user asks about HK
  statistics, government datasets, transport schedules, weather, facilities or
  demographics. Trigger phrases: "hkdata", "港數通", "港数通", "Hong Kong data",
  "data.gov.hk", "HK statistics", "HK population", "HK weather",
  "MTR/bus schedule", "HK public holidays", "badminton courts", "schools in HK".
compatibility: Requires python3 + chromadb for search/embed (see SETUP.md); needs a reachable embedding backend — Ollama by default, or any backend via the Embedder interface (see SETUP.md "Integrating a new backend").
license: MIT
---

# 港數通 · hkdata — Hong Kong Open Data Query Tool

Structured discovery workflow for finding, testing, and documenting datasets on
Hong Kong's open data portal (data.gov.hk).

**Scope: Hong Kong data.gov.hk dataset discovery and query only.** General web
search, non-HK data, or non-government sources are handled by the agent's native
web search tools, not this skill.

Before Steps 2–5, create a task list with one item per step; mark each `in progress`
before executing and `completed` when done, adding a sub-task for any fallback.

First run? Follow [`SETUP.md`](SETUP.md) once. Resolve the skill root once (the
docs never assume a runtime's install directory), then run every command through
`bash "$SKILL_DIR/hk.sh"`:

```bash
: "${SKILL_DIR:=$(for d in "${HKDATA_SKILL_DIR:-}" "${CLAUDE_SKILL_DIR:-}" \
    "$PWD/.agents/skills/hkdata" "$HOME/.agents/skills/hkdata" \
    "$HOME/.config/agents/skills/hkdata" "${HERMES_HOME:-$HOME/.hermes}/skills/hkdata" \
    "$HOME/.claude/skills/hkdata"; do [ -f "$d/hk.sh" ] && { echo "$d"; break; }; done)}"
[ -n "$SKILL_DIR" ] || { echo "hkdata: set HKDATA_SKILL_DIR to the dir containing hk.sh" >&2; exit 1; }
```

The wrapper is cwd-safe (it resolves its own root) and picks the venv interpreter
when present, else `python3`. If you prefer to run from the skill directory, the
same commands work as `bash ./hk.sh "<subcommand>" …`.

## Step 1 — Check Past Experience

```bash
bash "$SKILL_DIR/hk.sh" experience-search "<user query>"
```

Returns a relevance-ranked, **paged** list of past experiences — **positive** (a
working recipe) and **negative** (a dead end). These are *prior answers to
similar questions, presented for you to judge* — not verdicts. Cards below a
similarity floor are withheld (`No relevant experience card found.`). Page with
`--page`/`--per-page`, filter with `--kind positive|negative`.

- **positive** → read the cited `references/...md`, follow the recipe, then run
  Steps 3–4 to refresh live endpoints.
- **negative**, `outcome: unavailable` → likely no data on data.gov.hk — but
  **confirm with a quick Step 2 `catalog-search` before concluding**, since a
  near-miss card can rank for an unrelated query.
- **negative**, `outcome: pitfall` → this *path* is dead/retired but the data may
  still live elsewhere. Do **not** stop: follow the card's `caveats`/`method`
  (e.g. a retired endpoint, a moved portal) and re-route.
- no relevant card → proceed to Step 2.

Experiences carry a `date` and can be superseded — check it, and still run Steps 3–4
for live data.

## Step 2 — Search the Full Catalog

```bash
bash "$SKILL_DIR/hk.sh" catalog-search "<user query>"
```

ChromaDB search over the **full catalog** (`catalog-status` prints the current
count) — dense multilingual embeddings fused with a keyword pass — it covers the
whole catalog and understands Chinese, unlike the CKAN `package_search` API (see
[`README.md`](README.md)). If the store is empty, build it once —
`catalog-sync --full --lang en,tc` then `catalog-embed` (see [`SETUP.md`](SETUP.md)).

## Steps 3–4 — Inspect and Test the Endpoint

```bash
bash "$SKILL_DIR/hk.sh" info "<dataset-id>" ["<id2>" ...]     # CKAN package_show: metadata, resources, endpoint URLs
bash "$SKILL_DIR/hk.sh" test "<resource-url>" ["<url2>" ...]  # fetch the endpoint; auto-detects JSON/XML/CSV
```

## Step 5 — Record as Experience (Mandatory)

The purpose of Step 5 is **memory write**: the next similar question is answered
at Step 1 without redoing Steps 2–4.

```bash
bash "$SKILL_DIR/hk.sh" experience-log --kind positive \
  --topic "<question category>" --pattern "<query with placeholders>" --dataset <dataset-id> \
  --method "<what worked>" <!-- when a reference doc exists, cite it in --source -->
bash "$SKILL_DIR/hk.sh" log-render
```

It indexes the card immediately; if the embedding backend (e.g. Ollama) is down it
only appends to `data/experiences.jsonl` — run `experience-embed` later.

**Keep cards generic** so one card serves a whole class of questions, not one
specific query:

- `--topic` is the *question category* (e.g. "KMB A→B route finder"), not this
  instance's stop names.
- `--pattern` uses placeholders (`A`, `B`, `X`); put the concrete example in
  `--caveat`/`--method`, never in the topic. A specific card would shadow the
  general one at Step 1.
- `--outcome` is a **controlled vocabulary**: `verified` / `located` / `resolved`
  (positive) or `unavailable` / `pitfall` (negative). Descriptive results ("18
  stations", "✅ found") belong in `--method`, not `--outcome`.
- `pitfall` ≠ `unavailable`: `unavailable` means the data isn't on data.gov.hk;
  `pitfall` means this path is dead but the data may be elsewhere. Log `pitfall`
  with `--kind negative` and put the re-route in `--method`.

**Write a reference doc only when the recipe is non-trivial** (endpoint quirks,
multi-endpoint joins, proxy logic): `cp ./references/template.md
./references/<category>-<dataset>.md` and fill it in, then run
`bash "$SKILL_DIR/hk.sh" reindex` — it rebuilds `references/search-index.json`
*and* the generated `references/index.md` registry (never edit `index.md` by
hand). Cite the doc via `--source` on the card. For a dead end there is no doc —
log a **negative** card instead: `… experience-log --kind negative --topic "<what was asked>"
--outcome unavailable --method "<what was searched>" --caveat "<closest proxy>"`.

**Hard gate** — if any cannot be stated true, say "Step 5 incomplete —
documentation pending" and list the failures:
- [ ] One experience card recorded (positive or negative — never both for the same outcome)
- [ ] `log-render` ran after the write
- [ ] Repeat test: the same query can now be answered at Step 1 without Steps 2–4
- [ ] Near-miss test: a *different wording* of the same question class also ranks
      the card first at Step 1 (guards against over-fitting the exact query)

## Command Summary

| Command | Purpose |
|---------|---------|
| `bash "$SKILL_DIR/hk.sh" experience-search "<query>"` | Relevance-ranked, paged search over past experiences, ± (Step 1) |
| `bash "$SKILL_DIR/hk.sh" experience-log --kind positive\|negative …` | Record + index an experience (Step 5) |
| `bash "$SKILL_DIR/hk.sh" catalog-search "<query>"` | ChromaDB search over the full catalog (Step 2) |
| `bash "$SKILL_DIR/hk.sh" info "<id>" …` | CKAN `package_show` metadata (Steps 3–4) |
| `bash "$SKILL_DIR/hk.sh" test "<url>" …` | Test endpoint and detect format (Steps 3–4) |
| `bash "$SKILL_DIR/hk.sh" embed-status` | Active embedding backend + store match |

The full CLI list (build, refresh, `reindex`, `log-*`) is in [`README.md`](README.md).

## Auto-Fallback and No-Dataset Contract

When Step 1 (experience) and Step 2 (`catalog-search`) both return nothing useful:

1. Search structured logs: `bash "$SKILL_DIR/hk.sh" log-search "<topic>" "0 results"`
2. If a known strategy exists → use it; otherwise web search `site:data.gov.hk <topic>`
3. Record the outcome (Step 5, negative card) and `log-render`

If Steps 3–4 reveal no dataset answers the query, your answer MUST:

1. State clearly: "No suitable dataset found on data.gov.hk"
2. Include an exploration log listing each dataset examined and why it didn't fit
3. If a proxy exists, use it with an explicit caveat
   ([`references/workflow-guides.md`](references/workflow-guides.md) has the template)

## Answer Contract (when a dataset is found)

Every successful answer MUST include, alongside the direct answer:

1. **Dataset ID** (and the source department) — so the claim is re-checkable.
2. **Endpoint** actually queried (URL).
3. **Data timestamp** of the figures themselves, in **HKT**, distinct from
   "retrieved at" — e.g. "figures are as at 2026-03-13 (HKT)".

Presentation: multiple rows → a table; a trend → a chart (with the source dataset
and its temporality labelled). A procedural/form question ("how do I apply …") is
rarely a dataset — data.gov.hk holds statistics/fee tables, not application
steps; redirect to the department's site and say so rather than reporting a
"dataset miss".

## Deeper Guidance

- [`references/workflow-guides.md`](references/workflow-guides.md) — response templates, cross-dataset joins, proxy indicators, temporality, error handling, known broken endpoints.
- Verified datasets — `bash "$SKILL_DIR/hk.sh" search-local "<query>"` (the human-readable `references/index.md` registry is generated by `reindex`); category → filename prefix mapping in [`references/category-mapping.md`](references/category-mapping.md).
- [`SETUP.md`](SETUP.md) — install, build, and refresh the catalog and vector stores.
