# hkdata

A discovery and search toolkit for **Hong Kong government open data** ([DATA.GOV.HK](https://data.gov.hk)).

It answers questions like *"any government gym room in Cheung Sha Wan?"*, *"what's the air quality index right now?"*, or *"are schools closing because of falling enrolment?"* by finding the right dataset and querying its official API — with an honest answer when the data doesn't exist.

It is designed as a **skill for AI agents**: [`SKILL.md`](SKILL.md) defines the discovery workflow an agent follows, and the CLI works standalone for humans. The instructions are plain Markdown, so any agent with shell and file access can use it — it is not tied to a particular agent runtime.

## Why not just use the portal's search API?

DATA.GOV.HK's CKAN `package_search` is **Solr-backed and indexes only ~631 of the ~3,822 datasets** that the DB-backed `package_list` returns. It returns zero results for keywords that definitely have datasets — `badminton`, `vessel`, `AQHI`, `ferry`, and most Chinese terms. This repo works around that by building a complete offline catalog from the reliable endpoints (`package_list` + `package_show`) and searching it locally.

## How it works

```
catalog-sync --full --lang en,tc   crawl the whole catalog (resumable)
        │                          package_list seed -> package_show per dataset
        ▼
data/catalog/*.jsonl               8 shards, 500 datasets each, PII-free
        │
catalog-embed                      embed with a local Ollama model
        ▼
.cache/catalog/chroma/             ChromaDB stores (gitignored)
   ├── hkdata_datasets             "what datasets exist"
   └── hkdata_experiences          "how to answer this question"  (± lessons)
```

The agent workflow in [`SKILL.md`](SKILL.md) is:

1. **`experience-search`** — semantic lookup of past **positive and negative** experiences. A hit short-circuits the search; a negative hit ("not on data.gov.hk") avoids re-searching.
2. **`catalog-search`** — semantic + keyword search over all 3,822 datasets.
3. **`info`** → **`test`** — inspect the dataset and test its endpoint.
4. **`experience-log`** — record the outcome so the next similar question hits at step 1.

- **Bilingual:** en + Traditional Chinese metadata (`--lang en,tc`), so `康文署` resolves to `康樂及文化事務署`.
- **Hybrid retrieval:** ChromaDB dense KNN fused with a case-insensitive keyword pass (`references/aliases.json` expands common HK abbreviations).
- **Experience memory:** `data/experiences.jsonl` (committed) holds ~112 positive/negative cards derived from the curated references and logs, each dated so stale lessons are visible. Discoveries are recorded as cards per Step 5 of [`SKILL.md`](SKILL.md) — a reference doc in `references/` is only written when the recipe is non-trivial.
- **No finished answers are embedded** — cards point to datasets and methods; the agent still queries the live endpoint.

## Requirements

| Component | Purpose |
|---|---|
| `python3` | the CLI is stdlib-only |
| [`chromadb`](requirements-vectors.txt) | search store |
| [Ollama](https://ollama.com) + `qwen3-embedding:0.6b` | local multilingual embeddings |

## Setup

Full first-run instructions are in **[SETUP.md](SETUP.md)**. In short:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-vectors.txt
ollama pull qwen3-embedding:0.6b
```

The catalog shards (`data/catalog/`) are committed, so a fresh clone only needs to build the vector store:

```bash
bash ./hk.sh catalog-embed      # ~10 min for 3,822 datasets
```

To refresh from source: `catalog-sync --full --lang en,tc` (~2 h, resumable) or `catalog-sync --refresh` (14-day RSS delta, ~2 min).

## Usage

```bash
# Step 1 — past experience (positive + negative)
bash ./hk.sh experience-search "gym room Cheung Sha Wan"

# Step 2 — the full catalog
bash ./hk.sh catalog-search "badminton courts"
bash ./hk.sh catalog-search "康文署羽毛球場" --top-n 5

# Inspect a dataset and test its endpoint
bash ./hk.sh info hk-lcsd-facility-facility-fit
bash ./hk.sh test "http://www.lcsd.gov.hk/datagovhk/facility/facility-fitrm.json"

# Curated verified datasets + catalog coverage
bash ./hk.sh search-local "enrolment"
bash ./hk.sh catalog-status
```

### Commands

| Command | Purpose |
|---|---|
| `experience-search "<query>"` | Semantic search over past experiences (±) — Step 1 |
| `experience-log --kind positive\|negative …` | Record + index an experience |
| `experience-embed` / `experience-migrate` | Build / regenerate the experience index |
| `catalog-search "<query>"` | ChromaDB hybrid search over the full catalog — Step 2 |
| `catalog-sync [--full] [--refresh] [--lang en,tc]` | Seed/crawl/refresh the offline catalog |
| `catalog-embed` | Build the ChromaDB vector store |
| `catalog-status` | Coverage and vector-store report |
| `info "<id>"` | Dataset metadata (`package_show`) |
| `test "<url>"` | Test an endpoint and detect JSON/XML/CSV |
| `search-local "<query>"` | Search the curated reference docs |
| `reindex` | Rebuild `references/search-index.json` from the curated docs |
| `log-search` / `log-render` | Query/regenerate the failure & strategy logs |
| `bash ./hk.sh "<subcommand>"` | Single entry point — picks the venv interpreter when present, else `python3` |
| `bash ./scripts/hkdata-info.sh "<id>"` | Backward-compatible wrapper for `info` |

All commands run through `bash ./hk.sh`, which picks the `.venv` interpreter automatically when chromadb is needed and falls back to plain `python3` otherwise — no need to choose the interpreter yourself.

## Layout

```
hk.sh                     single CLI entry point (picks venv or python3)
SKILL.md                  discovery workflow (the entrypoint)
AGENTS.md                 notes for agents using the skill
scripts/hkdata/           CLI (catalog.py, vectors.py, index.py, logs.py, …)
data/catalog/             sanitized catalog shards (committed)
references/               curated dataset docs + registry + aliases
logs/                     rendered views (failure log = negative, strategy registry = positive)
tests/                    pytest suite
```

## Data source & attribution

All dataset metadata comes from **[DATA.GOV.HK](https://data.gov.hk)** and remains subject to its [terms and conditions](https://data.gov.hk/en/terms-and-conditions). The committed shards in `data/catalog/` are a **sanitized projection** of `package_show` responses: personal contact details (author/maintainer emails and phones) are stripped, and only the fields needed for search are retained. The JSONL store can be regenerated at any time with `catalog-sync`.

### Further reading

- [data.gov.hk Developer Guide](https://data.gov.hk/en/help/developer-guide)
- [CKAN API Documentation](https://docs.ckan.org/en/latest/api/)
- [HK Census and Statistics Department](https://www.censtatd.gov.hk/)
- [HK Observatory](https://www.hko.gov.hk/)

## Tests

```bash
.venv/bin/python -m pytest tests/ -q
```

## License

[MIT](LICENSE) for the code and documentation. The underlying government data is covered by the DATA.GOV.HK terms of use, not the MIT licence.

---

_Last updated 2026-09-27 — offline catalog (`package_list` + `package_show` → JSONL shards → ChromaDB search); CKAN `package_search` retired._
