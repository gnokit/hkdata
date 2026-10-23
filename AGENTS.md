# AGENTS.md

This is an AI-agent **skill** directory, not an application. There is no build, lint,
or typecheck (there is a pytest suite). The entrypoint is `SKILL.md`, which frames the
agent as a **coding agent** with a library of runnable functions. Everything below is
stuff `SKILL.md` implies but an agent commonly gets wrong.

## Running the scripts

First-time setup (venv, Ollama model, vector stores) is in [`SETUP.md`](SETUP.md).

Always invoke from the skill root via `bash ./hk.sh <subcommand>` — the wrapper picks
the venv interpreter (needed by search/embed commands, which require `chromadb`) and
falls back to `python3` otherwise. Never run `./hk.sh` directly; from another cwd, use
the absolute path (`bash ~/.agents/skills/hkdata/hk.sh …` for the symlink install) —
the wrapper is cwd-safe, but the doc text that names `./` paths assumes the skill root.
All paths in `SKILL.md` and the reference docs are `./`-relative.

```bash
# Path A — a runnable program already covers the question
bash ./hk.sh programs-search "<query>" [--source] [--json]
bash ./hk.sh reindex                       # extract + embed programs, render the registry
bash ./hk.sh programs-status               # library + vector-store report
# Path B — explore, then write a program
bash ./hk.sh catalog-search "<keyword>"    # full ~3,822-dataset catalog
bash ./hk.sh info "<dataset-id>"
bash ./hk.sh test "<endpoint-url>"
```

Under the hood this is `"$PWD/.venv/bin/python" ./scripts/hkdata.py <subcommand>`
(or `python3 ./scripts/hkdata.py <subcommand>` when no venv exists).

## The one gotcha that wastes the most time

There are **two retrieval layers, and they answer different questions**:

- `programs-search` — the **program library** (`programs/*.py`), the functions
  you have actually written and verified. Small, curated, runnable.
- `catalog-search` — the **full catalog** (`data/catalog/*.jsonl`, ~3,822
  datasets). This is the discovery fallback for anything with no program yet.

A query that misses in `programs-search` must fall through to `catalog-search`,
then `info`/`test`, then you **write a program and `reindex`**. That is the whole
learning loop.

CKAN's `package_search` is **Solr-backed and covers only ~631 of the ~3,822
datasets** that the DB-backed `package_list` returns. It has been removed; the
catalog is crawled once via `package_list` + `package_show` into JSONL shards
(`data/catalog/`, sanitized PII-free) and searched through ChromaDB.

If a store is empty, it is probably not built:
1. `bash ./hk.sh catalog-sync --full --lang en,tc` (once, ~2 h, resumable) — only if shards are missing
2. `bash ./hk.sh catalog-embed && bash ./hk.sh reindex`
3. Then search with `bash ./hk.sh programs-search "<topic>"` or `catalog-search "<topic>"`

## Pitfalls & unavailable memory

Negative / gap memory lives in three layers (there is no separate
`experiences.jsonl`):

1. **Per-program `Quirks:`** in function docstrings (embedded by `reindex`) —
   endpoint-specific traps (HKKF trailing slash, SWD UTF-16, webcat sort,
   district `&`/`and`, …).
2. **`programs/_pitfalls.md`** — cross-cutting search/encoding/tool traps.
   **Not** a runnable program; read it when discovery fails. Do not invent a
   fake function for pitfalls.
3. **`data/unavailable.jsonl`** (+ short `data/unavailable.md`) — topics
   confirmed missing on data.gov.hk (district unemployment rate, 殺校名單,
   smart CCTV counts, SmartPLAY table-tennis session feeds, …). After
   `programs-search` / `catalog-search` miss, check this list before claiming a
   dataset exists.

Flow: `programs-search` → `catalog-search` → if theme matches unavailable →
say so + cite proxies → else Path B discovery.

**`data_dictionary` (數據字典):** When summarizing or storing `package_show`
results, do not drop the `data_dictionary` field. Only look up the matching
data dictionary / guide when a dataset or API is unclear (odd response, complex
structure); then answer. Not required on every query.

## Writing a program (the new "memory write")

When Path B lands on a working recipe, persist it as a function — this is the
replacement for the old experience card, and it is the **hard gate**: until a
program is written and indexed, the discovery is not "remembered".

1. Copy `programs/_template.py` into the right `programs/<org>/<file>.py`.
2. One **function = one capability**; group related functions in one file.
3. Docstring leads with **what the data provides** (`Provides`), then `Coverage`,
   `Datasets`, `Department`, `Endpoint`, `Usage`, `Questions`, `Quirks`.
   `Questions` is the retrieval aid — write several rewordings.
4. The function returns JSON-serializable data and **never prints**; imports go
   *inside* the function so the returned source runs standalone in a heredoc.
5. Use the mainstream library for the job (`requests`, `pandas`, `lxml`,
   `feedparser`, `openpyxl`) — see SKILL.md *"Write efficient programs"*. Do not
   hand-roll HTML/RSS regex or urllib boilerplate.
6. Helpers/constants in the **same file** are fine: `extract()` inlines them into
   the returned source. Importing from another `programs/` module is not — the
   source is pasted standalone, so that import has nothing to resolve against.
7. `bash ./hk.sh reindex` — embeds the docstrings and renders `programs/index.md`
   (a generated view — never edit it by hand). Re-running is incremental on both
   docstring **and** body changes (`source_hash`).

A program that has not run against the live endpoint is not done: `test` the URL
first, then write the function from what you observed — and run it through
`bash ./hk.sh python - <<'EOF' … EOF`, the interpreter the source will meet.

## Org → subpackage guidance

Program files are grouped by **department/org**, not by the data.gov.hk category.
Use short slugs (`lcsd/`, `td/`, `hko/`, `epd/`, `gpa/`, `housing/`, `censtatd/`, …).
A function that joins two departments lives under its **primary** org and declares
**all** dataset IDs it touches in `Datasets:`. The remaining complex multi-endpoint
joins are deliberately deferred: KMB A→B route-finder (terminus-match +
`route-stop` → `stop` resolution — the raw `kmb_routes`/`kmb_stop`/`kmb_eta`
endpoints are done), ferry timetable + live ETA, and MTR real-time (needs MTR's own
API/spec/key, not a data.gov.hk endpoint).

## Scope boundary

Only Hong Kong government data from data.gov.hk. Non-HK data, non-government
sources, or general web queries are out of scope — redirect those to the agent's
native web search. Do not try to satisfy them with this skill.

## Subagent delegation

The **order** in `SKILL.md` is fixed: discover → answer → remember. A delegated
agent must not invert it.

- **Discovery** may run in a **single** subagent with shell and file access
  (catalog-search → info → test). It returns the working recipe — dataset id,
  endpoint, payload shape, observed quirks — and the main agent answers from
  that.
- **The program write** (the "remember" step) may also be delegated, but only
  after the answer is delivered; the main agent still runs `reindex`.
- Do not split discovery across multiple subagents. Use the highest-reasoning
  model available in your agent tool.

**Answer first.** The program is a memory for the *next* question; it must
never delay the current one. If a subagent's write is slow or fails, the
answer stands on its own — a missing program costs a future re-discovery
(seconds), a withheld answer costs the user the whole turn.

## End-to-end test (clean clone)

Verifies the **public** artifact actually runs — an agent following `SETUP.md`
then `SKILL.md` from a fresh clone. Run it before a release or after large
changes. The generated `programs/index.md` registry is gitignored; a clone
carrying only the engine + `programs/*.py` is exactly what the test checks.

> **The clone MUST live outside the skill root.** The agent runtime discovers
> skills by globbing `{*.md,**/SKILL.md}` **recursively** under every skill
> root (and it follows symlinks), then keeps them in a map keyed by the
> *parent directory's name* — last file wins. A clone inside this repo puts a
> second `SKILL.md` whose parent dir is also `hkdata` under `~/.agents/skills/`,
> and the stale clone silently replaces the real skill. `tests/test_skill_layout.py`
> fails the build if that ever happens again.

1. Clean the workspace and clone the **remote** (not a local copy) —
   **outside** this repo, e.g. `~/Projects/agents/hkdata-e2e/`:
   ```bash
   E2E_DIR="${HKDATA_E2E_DIR:-$HOME/Projects/agents/hkdata-e2e}"
   rm -rf "$E2E_DIR" && mkdir -p "$E2E_DIR"
   git clone https://github.com/gnokit/hkdata.git "$E2E_DIR/hkdata"
   ```
2. Spawn **one** high-reasoning subagent (shell + file access). It must:
   - work only inside `$E2E_DIR/hkdata`; never read/write the working repo or `~/.agents/skills/hkdata`;
   - **not** use `SKILL.md`'s root-resolution snippet — the `~/.agents/skills/hkdata` symlink points at the working repo and would silently contaminate the run. Set `export HKDATA_SKILL_DIR=$PWD` inside the clone and run `bash ./hk.sh …`;
   - follow `SETUP.md` steps 1–5, then `SETUP.md` §6 — the 3 hard questions through the **full** two-path loop (Path A → Path B, one written program + `reindex` each);
   - write raw commands + output to `$E2E_DIR/REPORT.md` with a verdict and a per-finding PASS/FAIL table.
3. Expect ~84 tracked files and a green `bash ./hk.sh`-driven run; the suite needs `requirements-dev.txt`. No BLOCKER = pass.
4. **Clean up afterwards** — `rm -rf "$E2E_DIR"`. A leftover clone is a live
   hijack risk the moment the skill is installed by symlink.

## Keeping SKILL.md minimal

`SKILL.md` is the **runtime entrypoint** — what a skill consumer reads to answer a
query. Keep it to the two-path contract only. It must not grow when programs are
added, and it must not carry development, setup, or maintenance material:

| Content | Belongs in |
|---|---|
| Two-path workflow, reusable-program composition, docstring contract, answer contract | `SKILL.md` |
| First-run install, venv, Ollama, building/refreshing the stores | `SETUP.md` |
| CLI reference, architecture, attribution | `README.md` |
| Repo upkeep, conventions, gotchas for maintainers | `AGENTS.md` |
| Response templates, deep guidance, failure patterns | `references/workflow-guides.md` |

The program library lives in `programs/`; its generated registry is
`programs/index.md` (built by `reindex`). The old `references/<dataset>.md` recipes
were migrated into `programs/` and removed.

## Weekly self-evolution review (every 7 days)

1. Read the program library (`programs/*.py`) and `programs/index.md`
2. Identify patterns: stale endpoints, quirks worth folding into docstrings,
   functions that overlap and should be merged
3. Update `references/workflow-guides.md` and `AGENTS.md` if guidance changes
4. Re-test any program whose endpoint looks stale, then `bash ./hk.sh reindex`

**Trigger:** spawn a single subagent with the task "hkdata weekly self-evolution review".
