# AGENTS.md

This is an OpenCode **skill** directory, not an application. There is no build, test, lint, or typecheck. The entrypoint is `SKILL.md`, which defines a mandatory 5-step dataset discovery workflow. Everything below is stuff `SKILL.md` implies but an agent commonly gets wrong.

## Running the scripts

Always invoke from the skill root via `bash ./scripts/...sh` or `python3 ./scripts/hkdata.py <subcommand>` — never `./scripts/...sh` directly, never from another cwd. All paths in `SKILL.md` and the reference docs are `./`-relative.

```bash
# search (ChromaDB) — must run from the venv
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
(`.cache/catalog/raw/`) and searched through ChromaDB.

If `catalog-search` returns nothing, the store is probably not built:
1. `python3 ./scripts/hkdata.py catalog-sync --full --lang en,tc` (once, ~2 h, resumable)
2. `.venv/bin/python ./scripts/hkdata.py catalog-embed`
3. Then search with `.venv/bin/python ./scripts/hkdata.py catalog-search "<topic>"`

Otherwise fall back to:
1. `python3 ./scripts/hkdata.py log-search "<topic>" "0 results"` — recorded workarounds.
2. Web search `site:data.gov.hk <topic> lcsd` (or `... transport`, `... census`).
3. Feed the ID to `python3 ./scripts/hkdata.py info "<dataset-id>"`.
4. Append the strategy to `logs/strategy-registry.jsonl` and the failure to
   `logs/failure-log.jsonl`, then run `python3 ./scripts/hkdata.py log-render`.

## Step 5 (documentation) is mandatory, not optional

When a new dataset is discovered and verified, you MUST:
1. `cp ./references/template.md ./references/{category}-{dataset}.md` and fill it in.
2. Add a row to the table in `references/index.md` AND an entry under the right `### Category` heading there.
3. Run `python3 ./scripts/hkdata.py reindex` to rebuild `references/search-index.json`.
4. If fallback was used, append to `logs/failure-log.jsonl` and `logs/strategy-registry.jsonl`, then run `python3 ./scripts/hkdata.py log-render`.

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

## Conventions for the log files

`logs/failure-log.md` and `logs/strategy-registry.md` are rendered views of the canonical JSONL sources (`logs/failure-log.jsonl` and `logs/strategy-registry.jsonl`). New entries are appended to the JSONL files, then `python3 ./scripts/hkdata.py log-render` regenerates the markdown. Both rendered files are written in **Cantonese**. Preserve that language when appending new entries. Use the existing entry format verbatim — both files declare their format at the top. Append new records above the `<!-- 新記錄請加喺上面 -->` marker.

## Scope boundary

Only Hong Kong government data from data.gov.hk. Non-HK data, non-government sources, or general web queries are out of scope — redirect those to the agent's native web search. Do not try to satisfy them with this skill.

## Subagent delegation

For complex discovery, `SKILL.md` specifies spawning a **single** subagent with shell and file access to run Steps 2–5 end-to-end. Do not split into multiple subagents. Use the highest-reasoning model available in your agent tool. The exact spawn syntax is in the "Subagent Configuration" section of `SKILL.md`.
