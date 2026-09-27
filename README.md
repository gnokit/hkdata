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
.cache/catalog/chroma/             ChromaDB vector store (39 MB, gitignored)
        │
catalog-search "<query>"           dense + keyword retrieval, RRF-fused
        ▼
references/*.md                    curated, tested per-dataset docs (endpoints, quirks)
```

- **Bilingual:** en + Traditional Chinese metadata (`--lang en,tc`), so `康文署` resolves to `康樂及文化事務署`.
- **Hybrid retrieval:** ChromaDB dense KNN fused with a case-insensitive keyword pass (`references/aliases.json` expands common HK abbreviations).
- **Experience memory:** `logs/` records failed searches and the strategies that worked, so the skill improves over time.

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
.venv/bin/python ./scripts/hkdata.py catalog-embed      # ~10 min for 3,822 datasets
```

To refresh from source: `catalog-sync --full --lang en,tc` (~2 h, resumable) or `catalog-sync --refresh` (14-day RSS delta, ~2 min).

## Usage

```bash
# Search (ChromaDB)
.venv/bin/python ./scripts/hkdata.py catalog-search "badminton courts"
.venv/bin/python ./scripts/hkdata.py catalog-search "康文署羽毛球場" --top-n 5

# Inspect a dataset and test its endpoint
python3 ./scripts/hkdata.py info hk-lcsd-facility-facility-fit
python3 ./scripts/hkdata.py test "http://www.lcsd.gov.hk/datagovhk/facility/facility-fitrm.json"

# Curated verified datasets + catalog coverage
python3 ./scripts/hkdata.py search-local "enrolment"
python3 ./scripts/hkdata.py catalog-status
```

### Commands

| Command | Purpose |
|---|---|
| `catalog-search "<query>"` | ChromaDB hybrid search over the full catalog |
| `catalog-sync [--full] [--refresh] [--lang en,tc]` | Seed/crawl/refresh the offline catalog |
| `catalog-embed` | Build the ChromaDB vector store |
| `catalog-status` | Coverage and vector-store report |
| `info "<id>"` | Dataset metadata (`package_show`) |
| `test "<url>"` | Test an endpoint and detect JSON/XML/CSV |
| `search-local "<query>"` | Search the curated reference docs |
| `log-search` / `log-render` | Query/regenerate the failure & strategy logs |

Run search and embed commands from `.venv` (they need `chromadb`); `catalog-sync`, `info` and `test` work with plain `python3`.

## Layout

```
SKILL.md                 discovery workflow (the entrypoint)
AGENTS.md                notes for agents using the skill
scripts/hkdata/          CLI (catalog.py, vectors.py, index.py, logs.py, …)
data/catalog/            sanitized catalog shards (committed)
references/              curated dataset docs + registry + aliases
logs/                    failure log and strategy registry (JSONL + rendered markdown)
tests/                   pytest suite
```

## Data source & attribution

All dataset metadata comes from **[DATA.GOV.HK](https://data.gov.hk)** and remains subject to its [terms and conditions](https://data.gov.hk/en/terms-and-conditions). The committed shards in `data/catalog/` are a **sanitized projection** of `package_show` responses: personal contact details (author/maintainer emails and phones) are stripped, and only the fields needed for search are retained. The JSONL store can be regenerated at any time with `catalog-sync`.

## Tests

```bash
.venv/bin/python -m pytest tests/ -q
```

## License

[MIT](LICENSE) for the code and documentation. The underlying government data is covered by the DATA.GOV.HK terms of use, not the MIT licence.
