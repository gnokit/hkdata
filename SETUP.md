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
bash ./hk.sh catalog-status
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

`Vector store: unavailable` at this point is normal — it is built next. (Run with
`bash ./hk.sh catalog-status` again after step 5 to see the dataset and experience
counts.)

**5. Build the vector stores**

```bash
bash ./hk.sh catalog-embed      # 3,822 datasets (~10 min)
bash ./hk.sh experience-embed   # ~120 experiences (seconds)
```

Both are incremental: re-running only re-embeds content that changed. The committed
shards in `data/catalog/` and `data/experiences.jsonl` mean no crawl is needed.

**6. Smoke test**

```bash
bash ./hk.sh experience-search "gym room Cheung Sha Wan" --top-n 3
bash ./hk.sh catalog-search "康文署羽毛球場" --top-n 3
```

Step 1 should surface past experiences; Step 2 should return LCSD badminton datasets.
Setup is complete.

---

## Which interpreter runs what

Every command in this guide goes through `bash ./hk.sh`: it picks
`.venv/bin/python` when the venv exists (search and embed need `chromadb` from
there), and falls back to `python3` otherwise. You never need to choose.

---

## Refreshing the catalog

The committed shards are a snapshot. To update:

```bash
bash ./hk.sh catalog-sync --refresh            # 14-day RSS delta, ~2 min
bash ./hk.sh catalog-sync --full --lang en,tc  # full re-crawl, ~2 h, resumable
bash ./hk.sh catalog-embed            # re-embed only what changed
```

`catalog-sync` writes sanitized, PII-free shards to `data/catalog/`. The ChromaDB
store under `.cache/catalog/chroma/` is derived and can be deleted and rebuilt at
any time.

---

## Using from another project (shared skill install)

Symlink the repo into the agents' skills folder — one venv, one Ollama model,
and one vector store serve every project:

```bash
ln -s "$(pwd)" ~/.agents/skills/hkdata
```

All commands resolve their own root, so from any other codebase call
`bash ~/.agents/skills/hkdata/hk.sh <subcommand> …` instead of `bash ./hk.sh …`.
Nothing else differs: the committed shards and the rebuilt `.cache/` store are
shared through the link.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Vector store: unavailable` | You are running with plain `python3`, which has no `chromadb`. Use `bash ./hk.sh catalog-status`. |
| `ChromaDB is not installed` | `.venv/bin/pip install -r requirements-vectors.txt` |
| `Ollama embedding failed` | The Ollama server is not running (`ollama serve`) or the model is missing (`ollama pull qwen3-embedding:0.6b`). |
| `Vector store is empty` | Run `bash ./hk.sh catalog-embed`. |
| `catalog-search` returns nothing useful | Confirm `catalog-status` shows `Vector store: 3822 datasets`; then try broader terms or add an abbreviation to `references/aliases.json`. |
| Tests fail | `.venv/bin/python -m pytest tests/ -q` — the suite is stdlib-only and should pass without Ollama. |
