# AGENTS.md

This is an OpenCode **skill** directory, not an application. There is no build, test, lint, or typecheck. The entrypoint is `SKILL.md`, which defines a mandatory 5-step dataset discovery workflow. Everything below is stuff `SKILL.md` implies but an agent commonly gets wrong.

## Running the scripts

Always invoke from the skill root via `bash ./scripts/...sh` or `python3 ./scripts/hkdata.py <subcommand>` — never `./scripts/...sh` directly, never from another cwd. All paths in `SKILL.md` and the reference docs are `./`-relative.

```bash
bash ./scripts/hkdata-find.sh "<keyword>" [--page N]   # CKAN package_search (wrapper)
bash ./scripts/hkdata-info.sh "<dataset-id>"            # CKAN package_show (wrapper)
python3 ./scripts/hkdata.py search "<keyword>" [--page N]
python3 ./scripts/hkdata.py info "<dataset-id>"
```

Dependencies are only `python3`. `curl` is no longer required for normal operation but can be used as a fallback. No auth needed for most data.gov.hk endpoints.

## The one gotcha that wastes the most time

`hkdata.py search` returns **0 results for many keywords that definitely have datasets**, because data.gov.hk's CKAN `package_search` metadata indexing is incomplete. Confirmed-broken keywords include:

- LCSD facilities: `badminton`, `sport`, `court`, `facility`, `recreation`, `venue`, `leisure`, `gymnasium`, `ball`, `indoor`, `outdoor`, `booking`
- Marine Department: `vessel`, `arrival`, `ship`
- EPD air quality: `AQHI`, `pollution`
- Ferry datasets: `ferry` (only Star Ferry indexed), `pier`, `harbour`, `outlying`, `ETA`
- Chinese keywords: `長者`, `老人`

**Mandatory fallback** (do not give up after 0 results):
1. Search structured logs: `python3 ./scripts/hkdata.py log-search "<topic>" "0 results"` — the workaround may already be recorded.
2. Web search `site:data.gov.hk <topic> lcsd` (or `... transport`, `... census` depending on category) to find the dataset ID directly.
3. Feed the ID to `python3 ./scripts/hkdata.py info "<dataset-id>"` to inspect.
4. Append the winning strategy to `logs/strategy-registry.jsonl` and the failure to `logs/failure-log.jsonl`, then run `python3 ./scripts/hkdata.py log-render`.

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
