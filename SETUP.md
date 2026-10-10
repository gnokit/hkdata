# Setup

First-time setup for **港數通 (hkdata)**. Follow this once; after that an agent can
run the workflow in [`SKILL.md`](SKILL.md) directly.

The catalog shards in `data/catalog/` are committed, so setup only needs to
install the search dependencies and build the vector store — **no crawl required**.

---

## Prerequisites

| Component | Why | Check |
|---|---|---|
| `python3` | the CLI is stdlib-only | `python3 --version` |
| [Ollama](https://ollama.com) | serves the default embedding model (optional — any embedding API works) | `ollama --version` |
| `chromadb` | search store | installed in step 2 |

The default embedding model is **`qwen3-embedding:0.6b`** — multilingual (English +
Chinese), 1024-dimensional, ~640 MB. To use a different embedding service, set
`HKDATA_EMBED_PROVIDER` / `HKDATA_EMBED_MODEL` / `HKDATA_EMBED_URL` /
`HKDATA_EMBED_API_KEY` (see *Using a different embedding provider* below).

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
Vector store:  empty (run: catalog-embed)
```

`Vector store: empty` at this point is normal — it is built next. (If you run with
plain `python3` and no `.venv`, ChromaDB is absent and it prints `unavailable` instead.
Run `bash ./hk.sh catalog-status` again after step 5 to see the dataset and
experience counts.)

**5. Build the vector stores**

```bash
bash ./hk.sh catalog-embed      # 3,822 datasets (~10 min)
bash ./hk.sh experience-embed   # experiences are private; empty on a fresh clone (seconds)
```

Both are incremental: re-running only re-embeds content that changed. Only the
catalog shards in `data/catalog/` are committed, so no crawl is needed.
`data/experiences.jsonl` is **private** (gitignored) and starts empty on a fresh
clone — it grows as you use the skill. `experience-embed` on an empty store is a
no-op that exits 0.

**6. Validate the skill loop — 3 hard questions**

Setup is complete only when the skill loop runs end-to-end. Drive each question
below through all five steps of [`SKILL.md`](SKILL.md) — Step 1
(`experience-search`) → Step 2 (`catalog-search`) → Step 3 (`info`) → Step 4
(`test`) → Step 5 (`experience-log` + `log-render`) — and confirm a sourced
answer, or an honest "no dataset". None has a recorded recipe, two need a
cross-dataset join and live endpoints, so this also exercises Step 5's memory
write.

1. **Q6 — crime trend by district** (`security-` category; likely CSV/XLSX):
   *"Which district saw the largest year-on-year % increase in reported violent
   crimes in the most recent full year, and what was the change?"*
2. **Q7 — school places per child** (education + population cross-join):
   *"Which district has the most primary school places per 5-year-old child, and
   is it above or below the territory-wide average?"*
3. **Q8 — Mainland arrivals + hotel occupancy** (tourism + commerce):
   *"How many Mainland Chinese visitors arrived last month, and what was the
   average hotel occupancy rate for the same period?"*

Sanity-check the stores first:

```bash
bash ./hk.sh embed-status     # active backend + match for both stores
```

A run is a PASS when, for each question, the answer cites the dataset ID, the
endpoint queried, and the data's own HKT timestamp (or states clearly that no
dataset exists), and Step 5 has recorded one experience card. Record anything
that breaks — a dead endpoint, a missing file, an install error.

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
any time. The store is keyed by the **embedding fingerprint** (`provider:model`);
`embed-status` reports match/mismatch, so switching embedding provider or model
invalidates the vectors and needs a fresh `catalog-embed` (see *Using a different
embedding provider* below).

---

## Using a different embedding provider (optional)

Ollama + `qwen3-embedding:0.6b` is the default, but any embedding service can be
plugged in. Two built-in backends ship with the skill — `ollama` (local) and
`openai` (any OpenAI-compatible `/v1/embeddings` API) — and you can add your own
without editing this repo (see *Integrating a new backend* below):

```bash
export HKDATA_EMBED_PROVIDER=openai
export HKDATA_EMBED_MODEL=text-embedding-3-small
export HKDATA_EMBED_URL=https://api.openai.com/v1/embeddings
export HKDATA_EMBED_API_KEY=sk-...
bash ./hk.sh catalog-embed      # rebuild the store with the new provider
bash ./hk.sh experience-embed
bash ./hk.sh embed-status       # should show "match" for both stores
```

The same four values are available as per-command flags
(`--provider` / `--model` / `--url` / `--api-key`). A store is tied to its
provider+model — every vector stores a **fingerprint** (`provider:model`), so
switching providers re-embeds everything and `embed-status` reports a MISMATCH
until you rebuild. The OpenAI-compatible path uses the plain `/v1/embeddings`
format, so OpenRouter, LM Studio, vLLM, etc. all work with no code changes.

### Integrating a new backend

An embedding backend is anything that implements the `Embedder` interface —
a class with an `embed(texts) -> list[vectors]` method plus `name`, `model`, and
`query_instruction` attributes. Wire it up one of two ways:

**1. Dotted path (no repo changes).** Point `HKDATA_EMBED_PROVIDER` at a
`pkg.module:ClassName` on the interpreter's import path:

```bash
HKDATA_EMBED_PROVIDER=myproject.myembed:AcmeEmbedder bash ./hk.sh embed-status
```

**2. Register it in code.** For backends you ship in the same environment:

```python
from hkdata.embeddings import Embedder, register_embedder

class AcmeEmbedder(Embedder):
    name = "acme"              # part of the fingerprint
    query_instruction = ""     # "" if the model takes plain queries

    def __init__(self, model=None, url=None, api_key=""):
        self.model = model or "acme-default-model"
        self.url = url or "https://api.acme.example/v1/embeddings"
        self.api_key = api_key or ""

    def embed(self, texts):
        # POST to self.url (send self.api_key as a bearer token if set),
        # return one vector per text in the same order.

register_embedder("acme", AcmeEmbedder)   # now --provider acme works
```

The rest of the toolkit (`catalog-embed`, `catalog-search`, `experience-*`)
only talks to the `Embedder` interface, never to a concrete provider, so a new
backend drops in with no changes to the search layer.

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

## Publishing to a public remote (guard rails)

This repo is meant to be **shareable as an engine**: `SKILL.md`, `scripts/`,
`SETUP.md`, the three method docs under `references/`, and the pinned catalog
shards. The knowledge you accumulate — `data/experiences.jsonl`, the
`references/<dataset>.md` recipes, `logs/`, `references/index.md` and
`search-index.json` — is **private** and untracked (see `.gitignore`).

Install the pre-push gate once per clone:

```bash
git config core.hooksPath .githooks
```

`.githooks/pre-push` then runs `scripts/public-preflight.sh` automatically on
**every** `git push`, checking:

| Check | Blocks when |
|---|---|
| tracked-file scope | a private path was re-added (typically `git add -f`) |
| incoming commits | the commits being pushed add/change private paths |
| credentials | `sk-…`, `ghp_…`, `github_pat_…`, `AKIA…`, private keys … |
| personal data | `/Users/<name>`, HKID, `+852` numbers, personal email domains |
| bulk | warns (does not block) on tracked files over 5 MB |

Run it by hand any time with `bash scripts/public-preflight.sh`. It exits
non-zero to block the push; `git push --no-verify` bypasses it entirely, which
is why the repository also has GitHub-side **secret scanning + push protection**
enabled — that layer cannot be bypassed from the client.

Untracking is **not** unpublishing: history keeps whatever was once committed,
and a fork keeps a snapshot of it. Decide a repo's class (engine vs knowledge)
before the first push.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Vector store: unavailable` | You are running with plain `python3`, which has no `chromadb`. Use `bash ./hk.sh catalog-status`. |
| `Vector store: empty (run: catalog-embed)` | Normal on a fresh clone — build the store with `bash ./hk.sh catalog-embed`. |
| `ChromaDB is not installed` | `.venv/bin/pip install -r requirements-vectors.txt` |
| `Ollama embedding failed` | The Ollama server is not running (`ollama serve`) or the model is missing (`ollama pull qwen3-embedding:0.6b`). |
| `Vector store is empty` | Run `bash ./hk.sh catalog-embed`. |
| `catalog-search` returns nothing useful | Confirm `catalog-status` shows `Vector store: 3822 datasets`; then try broader terms or add an abbreviation to `references/aliases.json`. |
| Tests fail | `.venv/bin/pip install -r requirements-dev.txt` then `.venv/bin/python -m pytest tests/ -q` — the suite is stdlib-only and passes without Ollama. |
