# AGENTS.md

This is an OpenCode **skill** directory, not an application. There is no build, test, lint, or typecheck. The entrypoint is `SKILL.md`, which defines a mandatory 5-step dataset discovery workflow. Everything below is stuff `SKILL.md` implies but an agent commonly gets wrong.

## Running the scripts

Always invoke from the skill root via `bash ./bin/...sh` — never `./bin/...sh` directly, never from another cwd. All paths in `SKILL.md` and the reference docs are `./`-relative.

```bash
bash ./bin/hkdata-find.sh "<keyword>" [--page N]   # CKAN package_search
bash ./bin/hkdata-info.sh "<dataset-id>"            # CKAN package_show
```

Dependencies are only `curl` + `python3` (for JSON parsing inside `hkdata-find.sh`). No auth needed for most data.gov.hk endpoints.

## The one gotcha that wastes the most time

`hkdata-find.sh` returns **0 results for many keywords that definitely have datasets**, because data.gov.hk's CKAN `package_search` metadata indexing is incomplete — especially for LCSD facility datasets. Confirmed-broken keywords: `badminton`, `sport`, `court`, `facility`, `recreation`, `venue`, `leisure`, `gymnasium`, `ball`, `indoor`, `outdoor`, `booking`.

**Mandatory fallback** (do not give up after 0 results):
1. Read `failure-log.md` + `strategy-registry.md` first — the workaround may already be recorded.
2. Web search `site:data.gov.hk <topic> lcsd` (or `... transport`, `... census` depending on category) to find the dataset ID directly.
3. Feed the ID to `hkdata-info.sh` / `package_show` to inspect.
4. Record the winning strategy in `strategy-registry.md` and the failure in `failure-log.md`.

## Step 5 (documentation) is mandatory, not optional

When a new dataset is discovered and verified, you MUST:
1. `cp ./references/template.md ./references/{category}-{dataset}.md` and fill it in.
2. Add a row to the **Verified Datasets** table in `SKILL.md` (near line 187).
3. Add a row to the table in `references/index.md` AND an entry under the right `### Category` heading there.
4. If fallback was used, append to `failure-log.md` and `strategy-registry.md`.

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

Full mapping is in `SKILL.md` ("Category Mapping" section).

## Conventions for the log files

`failure-log.md` and `strategy-registry.md` are written in **Cantonese**. Preserve that language when appending new entries. Use the existing entry format verbatim — both files declare their format at the top. Append new records above the `<!-- 新記錄請加喺上面 -->` marker.

## Scope boundary

Only Hong Kong government data from data.gov.hk. Non-HK data, non-government sources, or general web queries are out of scope — redirect those to the agent's native web search. Do not try to satisfy them with this skill.

## Subagent delegation

For complex discovery, `SKILL.md` specifies spawning a **single** `coder` subagent with `model="minimax-m2.7"` to run Steps 2–5 end-to-end. Do not split into multiple subagents. The exact spawn syntax is in the "Subagent Configuration" section of `SKILL.md`.
