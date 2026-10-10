# AGENTS.md

This is an AI-agent **skill** directory, not an application. There is no build, lint, or typecheck (there is a pytest suite). The entrypoint is `SKILL.md`, which defines a mandatory 5-step dataset discovery workflow. Everything below is stuff `SKILL.md` implies but an agent commonly gets wrong.

## Running the scripts

First-time setup (venv, Ollama model, vector store) is in [`SETUP.md`](SETUP.md).

Always invoke from the skill root via `bash ./hk.sh <subcommand>` — the wrapper picks the venv interpreter (needed by search/embed commands, which require `chromadb`) and falls back to `python3` otherwise. Never run `./hk.sh` directly; from another cwd, use the absolute path (`bash ~/.agents/skills/hkdata/hk.sh …` for the symlink install) — the wrapper is cwd-safe, but the doc text that names `./` paths assumes the skill root. All paths in `SKILL.md` and the reference docs are `./`-relative.

```bash
# step 1: past experience
bash ./hk.sh experience-search "<keyword>" [--kind positive|negative]
bash ./hk.sh experience-log --kind positive --topic "..." --dataset <id> --method "..."
# step 2: the full catalog
bash ./hk.sh catalog-search "<keyword>"
# catalog maintenance
bash ./hk.sh catalog-sync [--full] [--lang en,tc]
bash ./hk.sh catalog-embed
bash ./hk.sh catalog-status
# metadata / endpoint inspection
bash ./hk.sh info "<dataset-id>"
bash ./hk.sh test "<endpoint-url>"
```

Under the hood this is `"$PWD/.venv/bin/python" ./scripts/hkdata.py <subcommand>`
(or `python3 ./scripts/hkdata.py <subcommand>` when no venv exists).

Core dependency for the catalog is `python3` (stdlib) for crawling, but **search
requires the venv**: `chromadb` + a local Ollama model (`qwen3-embedding:0.6b`).
There is no SQLite/FTS5 fallback and no CKAN search anymore — the CKAN
`package_search` API has been retired from this skill.

## The one gotcha that wastes the most time

CKAN's `package_search` is **Solr-backed and covers only ~631 of the ~3,822 datasets**
that the DB-backed `package_list` returns. That is why the old `search` command missed
`badminton`, `vessel`, `AQHI`, `ferry`, and Chinese keywords. It has been removed; the
catalog is crawled once via `package_list` + `package_show` into JSONL shards
(`data/catalog/`, sanitized PII-free) and searched through ChromaDB.

Search in two steps: `experience-search` (past positive/negative lessons, Step 1) then
`catalog-search` (the catalog, Step 2). Experiences are dated and can be superseded —
check the date and re-test live endpoints.

If a store is empty, it is probably not built:
1. `bash ./hk.sh catalog-sync --full --lang en,tc` (once, ~2 h, resumable)
2. `bash ./hk.sh catalog-embed && bash ./hk.sh experience-embed`
3. Then search with `bash ./hk.sh catalog-search "<topic>"`

After a successful (or failed) discovery, record it:
`bash ./hk.sh experience-log --kind positive|negative …`

Otherwise fall back to:
1. `bash ./hk.sh log-search "<topic>" "0 results"` — recorded workarounds.
2. Web search `site:data.gov.hk <topic> lcsd` (or `... transport`, `... census`).
3. Feed the ID to `bash ./hk.sh info "<dataset-id>"`.
4. Record the outcome as an experience and re-render the views:
   `bash ./hk.sh experience-log --kind negative …`
   then `bash ./hk.sh log-render`.

## Step 5 is a memory write, not a documentation gate

`SKILL.md`'s Step 5 records every discovery as an experience card (positive or
negative) via `experience-log`, then `log-render`. The canonical hard gate is
there; the repo-side specifics for **reference docs** apply only when the recipe
is non-trivial (endpoint quirks, multi-endpoint joins, proxy logic):
1. `cp ./references/template.md ./references/{category}-{dataset}.md` and fill it in.
2. Run `bash ./hk.sh reindex` — it rebuilds `references/search-index.json` and the generated `references/index.md` registry (never edit `index.md` by hand).
3. Cite the doc via `--source` on `experience-log`.
4. One outcome → one card, and never both kinds for the same outcome.

## Category → filename prefix mapping (non-obvious ones)

Reference files are named `{prefix}-{dataset}.md`. Most prefixes match the data.gov.hk category, but these differ and agents guess them wrong:

| data.gov.hk category | File prefix |
|---|---|
| `commerce-and-industry` | `commerce-` |
| `law-and-security` | `security-` |
| `city-management` | `city-` |
| `employment-and-labour` | `employment-` |
| `recreation-and-culture` | `recreation-` |
| `social-welfare` | `welfare-` |
| `information-technology-and-broadcasting` | `it-` |
| `development` | `location-` |

Full mapping is in [`references/category-mapping.md`](references/category-mapping.md).

## Conventions for the rendered log views

`logs/failure-log.md` and `logs/strategy-registry.md` are **rendered views** of the canonical experience store (`data/experiences.jsonl`): the failure log shows **negative** experiences, the strategy registry shows **positive** ones. Do not edit the markdown by hand — record an experience (`experience-log`) and run `bash ./hk.sh log-render`. Existing entries are partly in **Cantonese**; keep that language when adding related experiences.

## Scope boundary

Only Hong Kong government data from data.gov.hk. Non-HK data, non-government sources, or general web queries are out of scope — redirect those to the agent's native web search. Do not try to satisfy them with this skill.

## Subagent delegation

For complex discovery you may spawn a **single** subagent with shell and file access to run Steps 2–5 end-to-end. Do not split into multiple subagents. Use the highest-reasoning model available in your agent tool. A worked example and response templates are in [`references/workflow-guides.md`](references/workflow-guides.md).

## End-to-end test (clean clone)

Verifies the **public** artifact actually runs — an agent following `SETUP.md` then `SKILL.md` from a fresh clone. Run it before a release or after large changes. The private knowledge layer (`data/experiences.jsonl`, `references/*.md`, `references/index.md`, `references/search-index.json`, `logs/`, `.cache/`) is gitignored; a clone carrying only the engine is exactly what the test checks.

1. `e2e-test/` is gitignored. Clean it and clone the **public remote** (not a local copy):
   ```bash
   rm -rf e2e-test/hkdata && mkdir -p e2e-test
   git clone https://github.com/gnokit/hkdata.git e2e-test/hkdata
   ```
2. Spawn **one** high-reasoning subagent (shell + file access). It must:
   - work only inside `e2e-test/hkdata`; never read/write the working repo or `~/.agents/skills/hkdata`;
   - **not** use `SKILL.md`'s root-resolution snippet — the `~/.agents/skills/hkdata` symlink points at the private repo and would silently contaminate the run. Set `export HKDATA_SKILL_DIR=$PWD` inside the clone and run `bash ./hk.sh …`;
   - follow `SETUP.md` steps 1–5, then `SETUP.md` §6 — the 3 hard questions through the **full** `SKILL.md` loop (Steps 1→5, one `experience-log` card each);
   - write raw commands + output to `e2e-test/REPORT.md` with a verdict and a per-finding PASS/FAIL table.
3. Expect ~59 tracked files and a green `bash ./hk.sh`-driven run; the suite needs `requirements-dev.txt`. No BLOCKER = pass.

## Keeping SKILL.md minimal

`SKILL.md` is the **runtime entrypoint** — what a skill consumer reads to answer a
query. Keep it to the workflow contract only. It must not grow when datasets are
added, and it must not carry development, setup, or maintenance material:

| Content | Belongs in |
|---|---|
| Query workflow (Steps 1–5), fallback, answer contracts | `SKILL.md` |
| First-run install, venv, Ollama, building/refreshing the stores | `SETUP.md` |
| CLI reference, architecture, attribution | `README.md` |
| Repo upkeep, conventions, gotchas for maintainers | `AGENTS.md` |
| Response templates, deep guidance, failure patterns | `references/workflow-guides.md` |

Verified datasets live in `references/index.md` (a registry generated by `reindex`), the category mapping in
`references/category-mapping.md`, and experience history in `logs/`.

## Weekly self-evolution review (every 7 days)

1. Read `data/experiences.jsonl` (and the rendered views in `logs/`)
2. Identify patterns: common failure causes, effective fallback strategies,
   experiences whose `date` is stale or superseded
3. Update `references/workflow-guides.md` and `AGENTS.md` if guidance changes
4. Archive/dedupe experiences, then `experience-migrate` + `experience-embed`
5. Run `bash ./hk.sh log-render` after cleanup

**Trigger:** spawn a single subagent with the task "hkdata weekly self-evolution review".
