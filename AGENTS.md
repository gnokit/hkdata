# AGENTS.md

This is an AI-agent **skill** directory, not an application. There is no build, lint, or typecheck (there is a pytest suite). The entrypoint is `SKILL.md`, which defines a mandatory 5-step dataset discovery workflow. Everything below is stuff `SKILL.md` implies but an agent commonly gets wrong.

## Running the scripts

First-time setup (venv, Ollama model, vector store) is in [`SETUP.md`](SETUP.md).

Always invoke from the skill root via `bash ./scripts/...sh` or `python3 ./scripts/hkdata.py <subcommand>` — never `./scripts/...sh` directly, never from another cwd. All paths in `SKILL.md` and the reference docs are `./`-relative.

```bash
# step 1: past experience (ChromaDB) — must run from the venv
.venv/bin/python ./scripts/hkdata.py experience-search "<keyword>" [--kind positive|negative]
.venv/bin/python ./scripts/hkdata.py experience-log --kind positive --topic "..." --dataset <id> --method "..."
# step 2: the full catalog
.venv/bin/python ./scripts/hkdata.py catalog-search "<keyword>"
# catalog maintenance (stdlib python3 is fine)
python3 ./scripts/hkdata.py catalog-sync [--full] [--lang en,tc]
.venv/bin/python ./scripts/hkdata.py catalog-embed
python3 ./scripts/hkdata.py catalog-status
# metadata / endpoint inspection (stdlib)
python3 ./scripts/hkdata.py info "<dataset-id>"
bash ./scripts/hkdata-info.sh "<dataset-id>"
```

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
1. `python3 ./scripts/hkdata.py catalog-sync --full --lang en,tc` (once, ~2 h, resumable)
2. `.venv/bin/python ./scripts/hkdata.py catalog-embed && .venv/bin/python ./scripts/hkdata.py experience-embed`
3. Then search with `.venv/bin/python ./scripts/hkdata.py catalog-search "<topic>"`

After a successful (or failed) discovery, record it:
`.venv/bin/python ./scripts/hkdata.py experience-log --kind positive|negative …`

Otherwise fall back to:
1. `python3 ./scripts/hkdata.py log-search "<topic>" "0 results"` — recorded workarounds.
2. Web search `site:data.gov.hk <topic> lcsd` (or `... transport`, `... census`).
3. Feed the ID to `python3 ./scripts/hkdata.py info "<dataset-id>"`.
4. Record the outcome as an experience and re-render the views:
   `.venv/bin/python ./scripts/hkdata.py experience-log --kind negative …`
   then `python3 ./scripts/hkdata.py log-render`.

## Step 5 (documentation) is mandatory, not optional

The canonical checklist is the **hard gate** in `SKILL.md`'s "Step 5" section. When a new dataset is discovered and verified, the repo-side specifics are:
1. `cp ./references/template.md ./references/{category}-{dataset}.md` and fill it in.
2. Add a row to the table in `references/index.md` AND an entry under the right `### Category` heading there.
3. Run `python3 ./scripts/hkdata.py reindex` to rebuild `references/search-index.json`.
4. If fallback was used, record an experience (`experience-log`) and run `python3 ./scripts/hkdata.py log-render`.

State "Step 5 incomplete — documentation pending" explicitly if you cannot finish; do not silently skip it.

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

`logs/failure-log.md` and `logs/strategy-registry.md` are **rendered views** of the canonical experience store (`data/experiences.jsonl`): the failure log shows **negative** experiences, the strategy registry shows **positive** ones. Do not edit the markdown by hand — record an experience (`experience-log`) and run `python3 ./scripts/hkdata.py log-render`. Existing entries are partly in **Cantonese**; keep that language when adding related experiences.

## Scope boundary

Only Hong Kong government data from data.gov.hk. Non-HK data, non-government sources, or general web queries are out of scope — redirect those to the agent's native web search. Do not try to satisfy them with this skill.

## Subagent delegation

For complex discovery, `SKILL.md` specifies spawning a **single** subagent with shell and file access to run Steps 2–5 end-to-end. Do not split into multiple subagents. Use the highest-reasoning model available in your agent tool. The requirements are in the "Subagent Configuration" section of `SKILL.md`; a worked example and response templates are in [`references/workflow-guides.md`](references/workflow-guides.md).

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

Verified datasets live in `references/index.md`, the category mapping in
`references/category-mapping.md`, and experience history in `logs/`.

## Weekly self-evolution review (every 7 days)

1. Read `data/experiences.jsonl` (and the rendered views in `logs/`)
2. Identify patterns: common failure causes, effective fallback strategies,
   experiences whose `date` is stale or superseded
3. Update `references/workflow-guides.md` and `AGENTS.md` if guidance changes
4. Archive/dedupe experiences, then `experience-migrate` + `experience-embed`
5. Run `python3 ./scripts/hkdata.py log-render` after cleanup

**Trigger:** spawn a single subagent with the task "hkdata weekly self-evolution review".
