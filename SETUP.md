# Setup

First-time setup for the hkdata skill. Follow this once; after that an agent can
run the workflow in [`SKILL.md`](SKILL.md) directly.

The catalog shards in `data/catalog/` are committed, so setup only needs to
install the search dependencies and build the vector store — **no crawl required**.

---

## Prerequisites

| Component | Why | Check |
|---|---|---|
| `python3` | the CLI is stdlib-only | `python3 --version` |
| [Ollama](https://ollama.com) | serves the embedding model | `ollama --version` |
| `chromadb` | search store | installed in step 2 |

The embedding model is **`qwen3-embedding:0.6b`** — multilingual (English +
Chinese), 1024-dimensional, ~640 MB.

---

## Steps

**1. Create a virtual environment**

```bash
python3 -m venv .venv
```

**2. Install the search dependency**

```bash
.venv/bin/pip install -r requirements-vectors.txt
```

**3. Make sure the Ollama server is running, and pull the model**

```bash
ollama serve          # if the server is not already running
ollama pull qwen3-embedding:0.6b
```

**4. Check the catalog is present**

```bash
python3 ./scripts/hkdata.py catalog-status
```

Expected:

```
Seed ids:      3822
Fetched:       3822
Missing:       0
Locales:       en, tc
Shards:        8 (16.0 MB)
Vector store:  unavailable
```

`Vector store: unavailable` at this point is normal — it is built next.

**5. Build the vector store**

```bash
.venv/bin/python ./scripts/hkdata.py catalog-embed
```

This embeds all 3,822 datasets (~10 minutes on CPU). It is incremental: re-running
only re-embeds datasets whose content changed.

**6. Smoke test**

```bash
.venv/bin/python ./scripts/hkdata.py catalog-search "badminton courts" --top-n 3
.venv/bin/python ./scripts/hkdata.py catalog-search "康文署羽毛球場" --top-n 3
```

Both should return LCSD badminton datasets. Setup is complete.

---

## Which Python runs what

Search and embed need `chromadb`, so they must run from the venv. Everything else
is stdlib and runs with plain `python3`.

| Run from `.venv/bin/python` | Run with `python3` |
|---|---|
| `catalog-search` | `catalog-sync` |
| `catalog-embed` | `info`, `test` |
| | `catalog-status`, `search-local`, `log-*` |

---

## Refreshing the catalog

The committed shards are a snapshot. To update:

```bash
python3 ./scripts/hkdata.py catalog-sync --refresh            # 14-day RSS delta, ~2 min
python3 ./scripts/hkdata.py catalog-sync --full --lang en,tc  # full re-crawl, ~2 h, resumable
.venv/bin/python ./scripts/hkdata.py catalog-embed            # re-embed only what changed
```

`catalog-sync` writes sanitized, PII-free shards to `data/catalog/`. The ChromaDB
store under `.cache/catalog/chroma/` is derived and can be deleted and rebuilt at
any time.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Vector store: unavailable` | You are running with plain `python3`, which has no `chromadb`. Use `.venv/bin/python ./scripts/hkdata.py catalog-status`. |
| `ChromaDB is not installed` | `.venv/bin/pip install -r requirements-vectors.txt` |
| `Ollama embedding failed` | The Ollama server is not running (`ollama serve`) or the model is missing (`ollama pull qwen3-embedding:0.6b`). |
| `Vector store is empty` | Run `.venv/bin/python ./scripts/hkdata.py catalog-embed`. |
| `catalog-search` returns nothing useful | Confirm `catalog-status` shows `Vector store: 3822 datasets`; then try broader terms or add an abbreviation to `references/aliases.json`. |
| Tests fail | `.venv/bin/python -m pytest tests/ -q` — the suite is stdlib-only and should pass without Ollama. |
