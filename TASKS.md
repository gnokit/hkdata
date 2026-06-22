# TASKS.md — Improvement Backlog

Findings from evaluating the skill against five complex, undocumented problems (see [EVAL_QUESTIONS.md](EVAL_QUESTIONS.md) for full details):
- **Q1:** Port cargo throughput + vessel call counts (non-JSON resources, real-time vs historical)
- **Q2:** District-level unemployment + PRH estate count (cross-dataset join, missing data, keyword bugs)
- **Q3:** Elderly support services (ambiguity, Chinese keywords, UTF-16-LE CSV, unused prefix)
- **Q4:** Air quality at Causeway Bay (endpoint health, format diversity, station parameters)
- **Q5:** Next ferry Central→Cheung Chau (real-time vs static, partial-answer honesty, operator mapping)

Each task is tagged with the question(s) that surfaced it. Priorities: **P0** (correctness/security), **P1** (capability gap blocking real queries), **P2** (polish/robustness).

---

## P0 — Script bugs

### T1. `hkdata-find.sh` URL-encode the keyword
**Surfaced by:** Q2, Q3, Q4, Q5 (crash on `unemployment district`, `public housing`, `air quality`, `長者`)
**Symptom:** Multi-word keywords with spaces cause `json.decoder.JSONDecodeError: Expecting value` because the raw space in `q=${KEYWORD}` produces an invalid CKAN request. Non-ASCII keywords (Chinese) crash with 400 Bad Request.
**Fix:** In `bin/hkdata-find.sh:44`, URL-encode `KEYWORD` before substituting into `API_URL`. Use bash-native escaping or `python3 -c "import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))" "$KEYWORD"`.
**Verify:** `bash ./bin/hkdata-find.sh "unemployment district"` returns results, not a traceback. `bash ./bin/hkdata-find.sh "長者"` doesn't crash.

### T2. `hkdata-info.sh` output breaks JSON parsers
**Surfaced by:** Q1, Q2, Q3, Q4, Q5 (had to use `tail -n +2` before `python3 -m json.tool` in every run)
**Symptom:** The script prints `Fetching dataset info for: <id>` before the JSON body, so `| python3 -m json.tool` and `| python3 -c "import json"` fail on the combined output.
**Fix:** Either (a) print the status line to stderr (`echo "..." >&2`) so stdout is pure JSON, or (b) document that consumers must skip the first line. Option (a) is cleaner and matches `hkdata-find.sh`'s behavior (its echo goes to stdout too — same bug there).
**Verify:** `bash ./bin/hkdata-info.sh "<id>" | python3 -m json.tool` works without `tail`.

---

## P1 — Capability gaps that block real queries

### T3. Step 4 assumes JSON — no XML/CSV handling
**Surfaced by:** Q1 (Marine Dept vessel data is XML; Censtatd report CSV download returns HTML), Q3 (SWD CSVs are UTF-16-LE tab-delimited), Q4 (EPD AQHI is RSS/XML; DPO is JSON; Smart Lampposts is ZIP), Q5 (TD ferry CSV, Sun Ferry JSON, HKKF JSON)
**Symptom:** SKILL.md:117 hard-codes `curl -s "<url>" | python3 -m json.tool | head -50`. XML and CSV endpoints require different parsers. The skill currently has no documented fallback when the resource is not JSON.
**Fix:** Rewrite Step 4 to:
1. Detect format from `Content-Type` header or resource `format` field from `package_show`.
2. Branch: JSON → `python3 -m json.tool`; XML → `python3 -c "import xml.etree.ElementTree as ET; ..."`; CSV → `python3 -c "import csv,sys; ..."`; HTML → flag as "not a data endpoint, likely a viewer page".
3. Add a worked XML example (Marine Dept `RP05005i.XML`) and a worked CSV example to SKILL.md.
**Verify:** Agent can test a known XML endpoint without improvising.

### T4. No cross-dataset join guidance
**Surfaced by:** Q2 (unemployment by district + PRH estate count by district)
**Symptom:** All 21 verified datasets are standalone. SKILL.md has no concept of composing two datasets to answer one question. The agent had to improvise normalization, joining, and partial-answer framing.
**Fix:** Add a "Cross-Dataset Composition" section to SKILL.md covering:
- When to join (user question spans 2+ datasets)
- Key normalization rules (district names: `&` vs `and`, case, Chinese vs English)
- Join strategy (fetch both, normalize keys, join in Python)
- How to present a joined answer (both datasets cited, join key stated)
**Verify:** A new problem that needs 2 datasets can be answered following the docs.

### T5. No "partial answer / proxy indicator" guidance
**Surfaced by:** Q2 (unemployment rate by district does not exist; LFPR is the closest proxy)
**Symptom:** SKILL.md's "When No Suitable Dataset Exists" section only covers the all-or-nothing case. There's no guidance for "exact metric unavailable, but a related proxy is" — the agent had to invent the LFPR-as-proxy framing and the caveat language.
**Fix:** Add a "Proxy Indicators" subsection under "When No Suitable Dataset Exists":
- Define proxy: a published metric that correlates with the requested metric but is not identical
- Require explicit caveat: state "X is not available; using Y as a proxy because Z"
- Require the caveat to appear in the final answer, not just the methodology
**Verify:** Agent faced with a missing metric delivers a proxy + caveat instead of just "not found".

### T6. No real-time vs static distinction
**Surfaced by:** Q1 (Marine Dept vessel feed is a 36h real-time snapshot; Censtatd throughput is quarterly historical), Q5 (Sun Ferry ETA is real-time 1-min; TD timetable is static)
**Symptom:** SKILL.md treats all datasets as "data". The agent had to invent language to distinguish a real-time operational feed from a historical statistical series, and to explain why "last month" can't be answered with a 36h snapshot.
**Fix:** Add a "Data Temporality" note to the reference template (`references/template.md`) and a short section in SKILL.md:
- **Real-time feed:** sub-daily updates, reflects a rolling window (e.g., last 36h), no historical archive via API
- **Historical series:** periodic (monthly/quarterly/annual), full time series available, lag of weeks to months
- **Static inventory:** updated "as needed", no time series, point-in-time snapshot
- Agent must state which type a dataset is and adjust "latest available" language accordingly.
**Verify:** Reference files for new datasets classify temporality explicitly.

---

## P1 — Skill wording / portability

### T7. Subagent Configuration is OpenCode-specific
**Surfaced by:** User feedback ("this skill can be used by other agent tool so the wording should be common")
**Symptom:** SKILL.md:374-392 hard-codes `Agent(subagent_type="coder", model="minimax-m2.7", ...)` — OpenCode syntax. Other agent tools (Claude Code, Cursor, etc.) use different APIs and model names.
**Fix:** Rewrite the section to:
1. Describe the requirement abstractly: "spawn a single subagent with shell + file access to run Steps 2–5 end-to-end"
2. Give OpenCode syntax as ONE example, not the canonical form
3. Add examples for other common agent tools if known, or leave a placeholder
4. Remove the specific model name from the requirement — say "high-reasoning model" and let the host agent pick.
**Verify:** A non-OpenCode agent can follow the section and spawn an equivalent subagent.

### T8. No "set up a task list before starting" instruction
**Surfaced by:** User feedback ("you do not fully utilize the current tools' capability such as using todo to keep track of progress")
**Symptom:** The 5-step workflow is non-trivial (3+ steps, branching fallback, mandatory documentation) but SKILL.md never tells the agent to create a task list first. Agents may lose track of steps, skip fallback, or forget Step 5.
**Fix:** Add to the "Full Workflow" section, before the bash block:
> "Before starting Steps 2–5, create a task list with one item per step. Mark each item `in progress` before executing it and `completed` when done. If a fallback is triggered, add it as a sub-task. This applies to any agent tool that supports task/todo tracking."
Use generic "task list" wording, not OpenCode-specific `todowrite`.
**Verify:** Next run of a complex problem shows live task tracking.

---

## P2 — Robustness / knowledge base

### T9. Censtatd API requires User-Agent — document it
**Surfaced by:** Q2 (`urllib.request.urlopen` got 403; `curl` worked)
**Symptom:** Censtatd's `api/get.php` blocks requests without a browser-like User-Agent. `curl` sends one by default; Python `urllib` does not. Agents that use Python's `requests` or `urllib` will hit 403 and may misdiagnose as "endpoint dead".
**Fix:** Add a note to SKILL.md "API Notes" section:
> "Censtatd `api/get.php` rejects requests without a User-Agent header. `curl` works by default. If using Python, set `headers={'User-Agent': 'curl/8.0'}` or equivalent."
**Verify:** Python-based test of Censtatd API succeeds with the documented header.

### T10. Censtatd `wbr.html?download_csv=1` is broken for programmatic use
**Surfaced by:** Q1 (Shipping Statistics Report CSV returned an HTML viewer page)
**Symptom:** The resource URL in `package_show` for Censtatd report datasets points to `wbr.html?download_csv=1`, which returns a JavaScript-rendered HTML page, not CSV data. Agents will waste time trying to parse it as CSV.
**Fix:** Add to failure-log.md (already done) and add a permanent warning in SKILL.md "Known Broken Endpoints" subsection:
> "Censtatd report datasets (e.g., `B1020008`) expose `wbr.html?download_csv=1` URLs that return HTML, not CSV. Use the JSON API (`api/get.php?id=<table-id>`) for the same data instead."
**Verify:** Agent encountering a `wbr.html` URL skips it without retrying.

### T11. CKAN `package_search` indexing gaps — expand the known-broken list
**Surfaced by:** Q1 (`vessel` → 0 results; Marine Dept not indexed), Q3 (`長者`/`老人` → 0 results; SWD not indexed), Q4 (`AQHI`/`pollution` → 0 results; EPD airteam not indexed), Q5 (`ferry`/`pier`/`harbour`/`outlying`/`ETA` → 0 results; TD/Sun Ferry/HKKF not indexed)
**Symptom:** AGENTS.md lists LCSD-related broken keywords only. Marine Department datasets are also not indexed under expected keywords (`vessel`, `arrival`, `ship`).
**Fix:** Update AGENTS.md "Known broken keywords" list to add: `vessel`, `arrival`, `ship` (Marine Dept); and add a general note that any department's datasets may be unindexed — always try web search fallback.
**Verify:** AGENTS.md reflects the expanded list.

### T12. District name normalization reference
**Surfaced by:** Q2 (Housing Authority `&` vs Censtatd `and`; also Chinese vs English variants), Q3 (SWD district names in Chinese `觀塘` vs English `Kwun Tong`)
**Symptom:** Cross-dataset joins on district name fail silently if names don't match exactly. No reference exists for the canonical forms.
**Fix:** Add a "District Name Normalization" appendix to SKILL.md listing the 18 District Council districts with:
- Canonical English name (Censtatd form, with `and`)
- Housing Authority variant (with `&`)
- Chinese name (Traditional)
- Censtatd DC code (A–T)
**Verify:** Agent can join any two district-keyed datasets without guessing.

### T13. Step 5 checklist is a comment block, not enforceable
**Surfaced by:** Q1–Q5 (Step 5 has 5 sub-items that are easy to skip)
**Symptom:** SKILL.md:152-157 has a `- [ ]` checklist, but agents treat it as documentation, not a gate. In practice, some sub-items get missed.
**Fix:** Reframe Step 5 as a hard gate: "Step 5 is not complete until ALL checklist items are ticked. If any item cannot be completed, state `Step 5 incomplete — documentation pending` and list which items failed." (The "incomplete" phrasing already exists at SKILL.md:159 but is not reinforced at the checklist.)
**Verify:** Agent self-reports incomplete Step 5 when blocked, rather than silently skipping.

---

## P2 — Reference doc improvements

### T14. Reference template missing fields
**Surfaced by:** Q1 & Q2 (had to improvise "Data Temporality", "Related Resources", "District Name Variants" sections)
**Symptom:** `references/template.md` has minimal fields. New reference files ended up with inconsistent sections.
**Fix:** Update `references/template.md` to include:
- **Data Temporality:** real-time feed / historical series / static inventory
- **Related Resources:** sibling endpoints or tables
- **Join Keys:** if dataset is keyed by district/period/etc., state the canonical key form
- **Known Quirks:** broken endpoints, auth requirements, format gotchas
**Verify:** New reference files created from the template have consistent structure.

### T15. `references/index.md` By Category section is incomplete
**Surfaced by:** Q2 (Employment and Housing sections existed but were missing entries; had to edit)
**Symptom:** The By Category section drifts out of sync with the Verified Datasets table above it.
**Fix:** Add a maintenance note at the top of the By Category section: "Keep in sync with the Verified Datasets table above. When adding a dataset, update BOTH." Consider a single-source-of-truth approach (one table, auto-grouped) in a future refactor.
**Verify:** No drift between table and category listing after next addition.

---

## P1 — Scalability / architecture (after 2 eval runs)

The skill is designed for linear growth — every new dataset adds a row to SKILL.md, an entry to index.md, a reference file, and possibly log entries. After only 2 eval runs we're at 25 reference files, 505-line SKILL.md, 80 table rows in SKILL.md, and Step 1 (`ls ./references/`) can no longer reliably tell the agent whether a query matches a verified dataset. This will not scale to 50+ datasets.

### T16. Local search index for verified datasets and experience history
**Surfaced by:** Q1–Q5 (Step 1 is just `ls ./references/` — agent had to open multiple files and guess matches from filenames; strategy-registry is a flat markdown table that doesn't surface relevant past strategies by query pattern)
**Symptom:**
- 25+ reference files, 80+ table rows across SKILL.md + index.md, failure-log and strategy-registry growing in flat markdown
- Step 1 (`ls ./references/`) only returns filenames — no keyword, category, or topic match
- Agent must read several reference files to determine if a verified dataset answers the query
- Strategy-registry entries are grouped by category but not searchable by symptom or keyword pattern
- Failure-log is chronological — agent can't find a known failure by symptom without reading the whole file
**Fix:** Build a lightweight local retrieval layer (no heavy deps — keep curl + python3 only):

1. **Structured index file:** `references/search-index.json` — a single JSON document rebuilt from all reference files, containing per-dataset:
   - `id`, `title`, `category`, `filename`, `description`
   - `keywords` (extracted from title + description + notes)
   - `endpoint`, `format` (JSON/XML/CSV), `temporality` (real-time/historical/static)
   - `join_keys` (e.g., "district", "period") if the dataset is joinable
   - `last_verified` date
   - `known_quirks` (broken endpoint, auth required, etc.)

2. **Search script:** `bin/hkdata-search-local.sh "<query>"` — takes a natural-language query, tokenizes it, and returns ranked matching datasets from `search-index.json` using simple TF/keyword overlap (no embeddings needed at this scale). Output: `dataset-id | title | category | score | filename`.

3. **Index builder:** `bin/hkdata-reindex.sh` — walks `references/*.md` (excluding template + index), extracts structured fields, writes `search-index.json`. Run automatically at end of Step 5, or manually.

4. **Replace Step 1:** Change SKILL.md Step 1 from `ls ./references/` to `bash ./bin/hkdata-search-local.sh "<user query>"`. If score > threshold, read the matched reference file. If no match, proceed to Step 2.

5. **Experience history:** Extend the index to include entries from `strategy-registry.md` and `failure-log.md` as searchable records (type: `strategy` or `failure`), so the agent can ask "has anyone solved a `<symptom>` before?" and get a ranked list.

**Scope guardrail:** This is keyword/TF search, NOT vector embeddings. At 25–200 datasets, keyword overlap is fast, deterministic, debuggable, and needs no model. Revisit embeddings only if the dataset count exceeds ~500 and keyword search recall drops.

**Verify:**
- `bash ./bin/hkdata-search-local.sh "vessel arrival port"` returns the Marine Dept dataset in top 3
- `bash ./bin/hkdata-search-local.sh "district unemployment"` returns the LFPR dataset and surfaces the failure-log entry about "UR by district not available"
- Step 1 no longer requires the agent to read multiple files by hand

### T17. SKILL.md is a data registry — extract the registry, stop growing the skill file
**Surfaced by:** Q1–Q5 (every new dataset adds a row to SKILL.md:187-210; file is 505 lines and growing; the Verified Datasets table is duplicated in `references/index.md`)
**Symptom:**
- SKILL.md is 505 lines, 23 sections, 80 table rows — and grows with every dataset
- The "Verified Datasets" table (SKILL.md:187-210) is duplicated in `references/index.md:7-32`
- Two sources of truth → drift risk (already seen: index.md By Category section was out of sync)
- SKILL.md should be the workflow definition (stable), not a data registry (growing)
- New contributors have to read 500+ lines to understand the workflow
**Fix:** Separate concerns:

1. **SKILL.md = workflow only.** Remove the full Verified Datasets table and the Category Mapping table from SKILL.md. Replace with a short pointer:
   > "Verified datasets are listed in `references/index.md` and are searchable via `bash ./bin/hkdata-search-local.sh "<query>"` (see T16). The category → filename prefix mapping is in `references/category-mapping.md`."

2. **`references/index.md` = the single dataset registry.** Already exists — make it the canonical source. Remove the duplicate table from SKILL.md.

3. **`references/category-mapping.md` = the category mapping.** Extract the Category Mapping table (SKILL.md:214-239) into its own small reference file. SKILL.md points to it.

4. **Add a size budget to SKILL.md:** State at the top: "This file defines the workflow only. It should not grow when datasets are added. If it exceeds ~300 lines, extract content to `references/`."

5. **Keep SKILL.md stable:** After this refactor, adding a new dataset should only touch `references/` files and the search index — never SKILL.md.

**Verify:**
- SKILL.md drops from 505 to <300 lines
- Adding a new dataset (run Step 5) does not modify SKILL.md
- `references/index.md` is the only place the full dataset table lives
- No information is lost — everything moved, not deleted

### T18. Failure-log and strategy-registry should be structured, not prose markdown
**Surfaced by:** Q1–Q5 (agent had to read the entire failure-log to check if a symptom was known; strategy-registry's Cantonese prose is hard to scan programmatically)
**Symptom:**
- `failure-log.md` is chronological Cantonese prose — good for humans, bad for lookup
- `strategy-registry.md` is grouped by category but entries are free-text
- Both files will grow indefinitely and become unreadable past ~50 entries
- The agent in Step 2 fallback has to "read failure-log + strategy-registry" — at 50+ entries this is expensive context
**Fix:** Convert both to structured JSON (or JSONL) with a thin markdown rendering layer:

1. **`failure-log.jsonl`** — one record per line, fields: `date`, `task`, `component`, `symptom`, `root_cause`, `solution`, `verified`, `keywords` (for search).
2. **`strategy-registry.jsonl`** — one record per line, fields: `category`, `topic`, `method`, `result`, `keywords`.
3. **`bin/hkdata-log-render.sh`** — regenerates the existing markdown files (`failure-log.md`, `strategy-registry.md`) from the JSONL sources, preserving the Cantonese format for human reading.
4. **`bin/hkdata-log-search.sh "<symptom>"`** — searches the JSONL by keyword match, returns matching records.
5. Step 2 fallback becomes: `bash ./bin/hkdata-log-search.sh "<keyword>"` instead of "read the whole file".
6. Step 5 appends to the JSONL, then re-renders the markdown.

**Migrate existing entries:** Write a one-off parser that converts the current markdown entries to JSONL. Keep the markdown files as the rendered view (humans still read those).

**Verify:**
- `bash ./bin/hkdata-log-search.sh "vessel 0 results"` returns the Marine Dept failure entry
- `bash ./bin/hkdata-log-search.sh "district unemployment"` returns the UR-by-district failure entry
- The markdown files still render correctly after re-indexing
- Agent no longer needs to read the full failure-log during Step 2 fallback

### T19. Migrate from bash scripts to a Python CLI — unblocks T1, T2, T3, T16, T18 together
**Surfaced by:** Q1–Q5 (every script issue traces to bash + inline Python being the wrong abstraction)
**Symptom:**
- T1 (URL encoding): `hkdata-find.sh` crashes on multi-word and non-ASCII keywords because bash string-concatenates the keyword into the URL
- T2 (stdout pollution): `hkdata-info.sh` prints a status line before JSON, breaking `| python3 -m json.tool`
- T3 (format-aware parsing): Step 4 is hard-coded to `curl | python3 -m json.tool` — no XML, CSV, or HTML-detection branch
- Q3 (UTF-16-LE tab CSV): SWD elderly CSVs required ad-hoc inline Python with encoding detection + tab delimiter; the standard Step 4 pipeline cannot handle this
- Q3 (Chinese keywords): `hkdata-find.sh "長者"` crashes because bash mangles non-ASCII bytes; even manually URL-encoded, the inline Python heredoc has escaping issues
- Cross-dataset joins (T4): require ad-hoc Python in heredocs — untestable, fragile, hard to reuse
- Error handling: `set -e` + raw Python tracebacks give no structured recovery; agents can't distinguish "endpoint dead" from "format wrong" from "network error"
- Testability: inline Python in heredocs cannot be unit tested; every fix is a manual end-to-end run

**Root cause:** Bash is the wrong abstraction for JSON/XML/CSV parsing, URL encoding, Unicode handling, and structured error handling. The current `hkdata-find.sh:47-76` is already ~30 lines of fragile heredoc-with-shell-interpolation Python — moving it to a real module is net simpler, not more complex.

**Fix:** Migrate to a Python CLI with thin bash wrappers for backward compatibility.

1. **Single CLI entry point:** `bin/hkdata.py` with argparse subcommands:
   - `search "<keyword>" [--page N]` — CKAN package_search (replaces `hkdata-find.sh`)
   - `info "<dataset-id>"` — CKAN package_show (replaces `hkdata-info.sh`)
   - `test "<resource-url>"` — format-aware endpoint tester (replaces Step 4's `curl | json.tool`)
   - `reindex` — rebuild `search-index.json` (T16)
   - `log-search "<keyword>"` — search failure-log + strategy-registry (T18)

2. **Internal modules** (stdlib only — `urllib.request`, `json`, `csv`, `xml.etree`, `urllib.parse`):
   ```
   hkdata/
     __init__.py
     cli.py          # argparse, subcommand dispatch
     search.py       # package_search — URL-encoded, Unicode-safe
     inspect.py      # package_show — clean JSON to stdout, status to stderr
     parse.py        # format dispatch: JSON / XML / CSV (any encoding, any delimiter) / HTML-detect
     normalize.py    # district names, keyword synonyms, category mapping
     index.py        # search-index.json builder (T16)
     logs.py         # failure-log/strategy-registry JSONL (T18)
   ```

3. **Thin bash wrappers** (preserve backward compat for agents/skills that already call the old scripts):
   ```bash
   # bin/hkdata-find.sh
   exec python3 "$(dirname "$0")/hkdata.py" search "$@"
   # bin/hkdata-info.sh
   exec python3 "$(dirname "$0")/hkdata.py" info "$@"
   ```

4. **Format-aware tester** (`hkdata.py test <url>`) replaces Step 4:
   - Detect `Content-Type` header or `format` field from `package_show`
   - Branch: JSON → pretty-print; XML → ElementTree summary; CSV → encoding-detect + first 5 rows; HTML → flag "not a data endpoint, likely viewer page"
   - Handle UTF-16-LE, UTF-8-sig, tab-delimited — all the SWD CSV quirks
   - Output structured summary, not raw dump

5. **Proper error handling:**
   - Network errors → `HKDataNetworkError` (retry once, then report)
   - Format errors → `HKDataFormatError` (report expected vs actual)
   - CKAN 0-results → `HKDataEmptyResultError` (trigger fallback guidance)
   - All errors print to stderr with actionable messages; exit codes: 0=success, 1=user error, 2=network, 3=format, 4=empty

6. **Set `User-Agent` header** in `urllib.request` for all Censtatd calls — eliminates the `curl`-vs-`urllib` 403 issue (T9).

**Dependency constraint (preserve AGENTS.md promise):**
- **Stdlib only.** No `requests`, no `pandas`, no `chardet`. Use `urllib.request`, `json`, `csv`, `xml.etree.ElementTree`, `urllib.parse`.
- BOM detection: check first 2-3 bytes manually (`\xff\xfe` → UTF-16-LE, `\xfe\xff` → UTF-16-BE, `\xef\xbb\xbf` → UTF-8-sig).
- Delimiter detection: sniff first line for `\t` vs `,`.
- `curl` no longer required if `User-Agent` is set — but keep it as a fallback for endpoints that block Python's urllib regardless.

**What this unblocks (do T19 before these):**
- T1 (URL encoding) → `urllib.parse.quote()` in `search.py`
- T2 (stdout pollution) → `logging` to stderr, clean JSON to stdout in `inspect.py`
- T3 (format-aware parsing) → `parse.py` dispatch
- T16 (search index) → `index.py` module + `reindex` subcommand
- T18 (structured logs) → `logs.py` module + `log-search` subcommand
- T9 (Censtatd User-Agent) → set in `urllib.request` globally
- T12 (district normalization) → `normalize.py` module, reusable across all joins

**Verify:**
- `python3 ./bin/hkdata.py search "長者"` works without crash (URL-encoded, Unicode-safe)
- `python3 ./bin/hkdata.py search "unemployment district"` works (multi-word)
- `python3 ./bin/hkdata.py info "hk-censtatd-tablechart-210-06821" | python3 -m json.tool` works (no `tail -n +2` needed)
- `python3 ./bin/hkdata.py test "https://www.swd.gov.hk/datagovhk/elderly/list-of-neighbourhood-elderly-centres.csv"` detects UTF-16-LE + tab and parses correctly
- `python3 ./bin/hkdata.py test "https://www.mardep.gov.hk/e_files/en/opendata/RP05005i.XML"` detects XML and summarizes structure
- `bash ./bin/hkdata-find.sh "elderly"` still works (backward compat wrapper)
- `pytest tests/` passes (basic unit tests for `parse.py`, `normalize.py`, `search.py`)
- No third-party imports — only stdlib

**Scope guardrail:** This is a refactor of the script layer, not the skill workflow. SKILL.md's 5-step workflow stays the same; only the commands in Steps 2–4 change from `bash ./bin/hkdata-*.sh` to `python3 ./bin/hkdata.py <subcommand>` (with bash wrappers preserving old syntax). AGENTS.md's "Dependencies are only curl + python3" becomes "Dependencies are only python3 (curl optional fallback)".

**Do alongside T20** (folder structure alignment) — the Python migration is the natural moment to rename `bin/` → `scripts/` and move logs out of the root, since every path reference in SKILL.md and AGENTS.md will be updated anyway.

---

### T20. Align folder structure with the agent-skills spec
**Surfaced by:** Web research into the cross-tool agent-skills standard (agentskills.io spec, Anthropic engineering blog, Microsoft APM, Claude Code docs, community best practices)
**Symptom:**
- Current layout uses `bin/` (non-standard), root-level `failure-log.md` + `strategy-registry.md` (no standard bucket), and no `tests/` directory
- The cross-tool agent-skills spec (agentskills.io, adopted by Anthropic, Microsoft APM, Claude Code, Windsurf, Kiro) defines a canonical structure: `SKILL.md` + `scripts/` + `references/` + `assets/` + `examples/`
- Our current structure works but is non-standard — other agent tools scanning for skills won't find scripts where they expect them
- Logs (failure-log, strategy-registry) don't fit `references/` (those are for docs loaded into context) or `assets/` (those are for static templates). They need their own home.

**Standard structure (from agentskills.io spec + Anthropic + APM):**
```
skill-name/
├── SKILL.md              # Required: metadata + instructions (<500 lines)
├── scripts/              # Optional: executable code (Python/Bash/JS)
├── references/           # Optional: docs loaded into context on demand (one level deep)
├── assets/               # Optional: templates, images, schemas, lookup tables
└── examples/             # Optional: sample inputs/outputs
```

**Key conventions to follow:**
- `SKILL.md` is the only required file, at the directory root
- `scripts/` holds executable code — tiny CLIs, not library code. No `.md` docs here.
- `references/` holds docs loaded into context on demand. One level deep. No executables here.
- `assets/` holds static resources (templates, JSON schemas, lookup tables). Non-executable.
- File references in SKILL.md use relative paths from skill root, forward slashes
- Directory name = `name` field in frontmatter (lowercase, hyphen-separated)
- `SKILL.md` <500 lines / <5,000 tokens
- No deep nesting (one level deep in subdirectories)
- No empty directories (don't create `examples/` if unused)

**Target structure for hkdata:**
```
hkdata/
├── SKILL.md                    # Workflow only, <300 lines (T17)
├── AGENTS.md                   # Agent-facing gotchas (stays at root, project-level)
├── TASKS.md                    # Improvement backlog (stays at root, project-level)
├── scripts/                    # was bin/ — Python CLI + thin bash wrappers (T19)
│   ├── hkdata.py               # single CLI entry point
│   ├── hkdata/                 # Python package (internal modules)
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── search.py
│   │   ├── inspect.py
│   │   ├── parse.py
│   │   ├── normalize.py
│   │   ├── index.py            # T16
│   │   └── logs.py             # T18
│   ├── hkdata-find.sh          # thin wrapper (backward compat)
│   └── hkdata-info.sh          # thin wrapper (backward compat)
├── references/                 # Verified dataset docs + category mapping + template
│   ├── index.md                # single dataset registry (T17)
│   ├── category-mapping.md     # extracted from SKILL.md (T17)
│   ├── template.md             # reference doc template
│   ├── search-index.json       # built by scripts/hkdata.py reindex (T16)
│   └── *.md                    # per-dataset reference docs
├── logs/                       # Experience history (non-standard but necessary)
│   ├── failure-log.jsonl       # structured (T18)
│   ├── strategy-registry.jsonl # structured (T18)
│   ├── failure-log.md          # rendered Cantonese view (human reading)
│   └── strategy-registry.md    # rendered Cantonese view (human reading)
└── tests/                      # Unit tests for Python CLI (T19)
    ├── test_parse.py
    ├── test_normalize.py
    └── test_search.py
```

**Why `logs/` is not in the standard but is necessary here:**
The agent-skills spec doesn't define a logs directory because most skills are stateless — they don't accumulate experience over time. hkdata is different: it has a self-healing knowledge base (failure-log + strategy-registry) that grows with every query. Options considered:
1. `references/` — semantically wrong (logs are not docs loaded into context; they're searchable structured data)
2. `assets/` — semantically wrong (logs are mutable, not static templates)
3. `.skills-data/<name>/logs/` (boilerplate-skill convention) — too heavy for our needs, introduces a separate data root
4. `logs/` at skill root — simple, discoverable, non-standard but doesn't violate any spec constraint (the spec says "any additional files or directories" are allowed)

**Decision:** Use `logs/` at the skill root. It's non-standard but the spec explicitly allows additional directories. Document the rationale in AGENTS.md so future contributors understand why.

**Migration steps (do as part of T19):**
1. `git mv bin/ scripts/` — rename the directory
2. `mkdir logs/` — create the logs directory
3. `git mv failure-log.md logs/failure-log.md` — move rendered view
4. `git mv strategy-registry.md logs/strategy-registry.md` — move rendered view
5. Create `logs/failure-log.jsonl` and `logs/strategy-registry.jsonl` (T18 migration)
6. Update ALL path references in SKILL.md, AGENTS.md, and reference files:
   - `./bin/hkdata-find.sh` → `./scripts/hkdata-find.sh` (or `python3 ./scripts/hkdata.py search`)
   - `./bin/hkdata-info.sh` → `./scripts/hkdata-info.sh` (or `python3 ./scripts/hkdata.py info`)
   - `failure-log.md` → `logs/failure-log.md` (or `logs/failure-log.jsonl` for structured access)
   - `strategy-registry.md` → `logs/strategy-registry.md` (or `logs/strategy-registry.jsonl`)
   - `./references/` paths stay the same
7. Update `.gitignore` if needed (no changes expected)
8. Create `tests/` directory with initial test files (T19)

**Verify:**
- `ls scripts/` shows `hkdata.py`, `hkdata-find.sh`, `hkdata-info.sh`, `hkdata/` package
- `ls logs/` shows `failure-log.jsonl`, `strategy-registry.jsonl`, `failure-log.md`, `strategy-registry.md`
- `ls references/` shows `index.md`, `category-mapping.md`, `template.md`, `search-index.json`, per-dataset docs
- `ls tests/` shows `test_parse.py`, `test_normalize.py`, `test_search.py`
- No `bin/` directory remains
- No `failure-log.md` or `strategy-registry.md` at root
- `grep -r "bin/hkdata" SKILL.md AGENTS.md references/` returns 0 matches
- `grep -r "failure-log.md\|strategy-registry.md" SKILL.md AGENTS.md` only matches `logs/` paths
- Skill still loads and runs correctly from the new structure
- Structure matches agentskills.io spec (with documented `logs/` extension)

### T21. Batch / multi-query support
**Surfaced by:** All 5 eval runs (agent had to issue multiple parallel bash tool calls to simulate batch search — `port` + `cargo` + `container` + `vessel` in Q1; `elderly` + `welfare` + `social` in Q3; `air` + `AQHI` + `pollution` + `monitoring` + `epd` in Q4; `ferry` + `pier` + `harbour` in Q5)
**Symptom:**
- Every command is single-query: `hkdata-find.sh` takes 1 keyword, `hkdata-info.sh` takes 1 dataset ID, Step 4 tests 1 URL
- The skill's own workflow already implies multi-query patterns:
  - Step 2: try multiple keyword synonyms when the first returns 0 (every eval run did this)
  - Step 2 fallback: web search + CKAN search should run in parallel
  - Step 3: inspect multiple candidate datasets from Step 2 results
  - Step 4: test multiple endpoints (Q4 tested 4 air quality datasets across RSS/XML/JSON/ZIP)
- An agent that can't parallelize tool calls (or a human running the CLI) must run searches sequentially — 4 keywords × ~2s per CKAN call = 8s+ of blocking
- No way to say "search for these 5 synonyms and tell me which ones returned results" in one command
- No way to inspect multiple dataset IDs in one call
- No way to test multiple endpoints in one call

**Fix:** Implement batch support in the Python CLI (T19). All subcommands accept multiple arguments:

1. **`search` — multiple keywords:**
   ```bash
   # Search multiple synonyms in one call (parallel HTTP, merged results)
   python3 ./scripts/hkdata.py search "vessel" "arrival" "ship" "marine" --parallel
   
   # Output: merged + deduplicated, with source keyword annotated
   # vessel  | hk-md-mardep-vessel-arrivals-and-departures | Vessel arrivals...
   # arrival | (0 results)
   # ship    | hk-censtatd-tablechart-b1020008 | Hong Kong Shipping...
   ```

2. **`search` — auto-synonym expansion:**
   ```bash
   # --synonyms flag auto-expands to common synonyms from normalize.py
   python3 ./scripts/hkdata.py search "elderly" --synonyms
   # Equivalent to: search "elderly" "aged" "senior" "welfare" "長者" "老人"
   ```

3. **`info` — multiple dataset IDs:**
   ```bash
   # Inspect multiple datasets in one call
   python3 ./scripts/hkdata.py info "hk-epd-airteam-current-aqhi-of-individual-air-quality-monitoring-stations" "hk-epd-airteam-past24hr-pc-of-individual-air-quality-monitoring-stations" "hk-dpo-datagovhk2-city-dashboard-aqhi"
   
   # Output: JSON array of package_show results (one per ID)
   ```

4. **`test` — multiple URLs:**
   ```bash
   # Test multiple endpoints in one call, format-auto-detected per URL
   python3 ./scripts/hkdata.py test \
     "https://www.aqhi.gov.hk/epd/ddata/html/out/aqhi_ind_rss_Eng.xml" \
     "https://www.aqhi.gov.hk/epd/ddata/html/out/24pc_Eng.xml" \
     "https://dashboard.data.gov.hk/api/aqhi-individual?format=json"
   
   # Output: per-URL summary (format detected, status, sample data, station count)
   ```

5. **`search` + `info` pipeline (discover-and-inspect):**
   ```bash
   # Search, then auto-inspect top N results
   python3 ./scripts/hkdata.py search "air" --inspect-top 3
   
   # Output: search results + full package_show for top 3 datasets
   ```

6. **`log-search` — multiple keywords (T18):**
   ```bash
   python3 ./scripts/hkdata.py log-search "vessel" "0 results" "marine"
   # Searches failure-log + strategy-registry for any of these terms
   ```

**Implementation notes:**
- Use `concurrent.futures.ThreadPoolExecutor` for parallel HTTP requests (stdlib, no deps)
- Default thread pool size: 5 (CKAN rate limits are generous)
- Merge + deduplicate results by dataset ID
- Each result row annotated with which keyword matched
- `--parallel` flag defaults to True for `search`; can be disabled with `--sequential` for debugging
- Output format stays the same (`dataset-id | title | description`) for single-query backward compat
- Multi-query output adds a `source` column: `source | dataset-id | title | description`

**Why this matters for the skill workflow:**
- Step 2 becomes one command instead of 4-6 sequential calls
- Step 2 fallback (CKAN + web search) can run in parallel
- Step 3 (inspect multiple candidates) becomes one command
- Step 4 (test multiple endpoints) becomes one command with per-format dispatch
- Reduces agent round-trips from ~15 commands per complex query to ~4-5
- Makes the skill usable by humans running the CLI directly, not just agents with parallel tool call capability

**Verify:**
- `python3 ./scripts/hkdata.py search "vessel" "arrival" "ship" --parallel` returns merged results from all 3 keywords in one call
- `python3 ./scripts/hkdata.py search "elderly" --synonyms` auto-expands and searches all synonyms
- `python3 ./scripts/hkdata.py info <id1> <id2> <id3>` returns JSON array of 3 package_show results
- `python3 ./scripts/hkdata.py test <url1> <url2> <url3>` tests all 3 endpoints, auto-detects format per URL
- `python3 ./scripts/hkdata.py search "air" --inspect-top 3` returns search results + 3 full inspections
- Single-query calls still work unchanged (backward compat)
- `tests/test_search.py` covers multi-keyword + dedup + synonym expansion
- Total round-trips for a complex query (4 keywords + 3 inspections + 4 endpoint tests) drops from ~11 to ~3

---

## Summary

| Priority | Count | Theme |
|----------|-------|-------|
| P0 | 2 | Script bugs (URL encoding, stdout pollution) — subsumed by T19 |
| P1 | 12 | Python migration (T19) + folder structure (T20) + batch support (T21) + capability gaps (XML/CSV, joins, proxies, temporality) + portability (subagent syntax, task lists) + scalability (search index, SKILL.md extraction, structured logs) |
| P2 | 7 | Robustness (User-Agent, broken endpoints, indexing gaps, normalization, checklist enforcement, template, index sync) |
| **Total** | **21** | |

Suggested order: **T19 + T20 + T21 together** (Python migration + folder structure + batch support — do as one refactor since batch support is trivial to implement during the Python CLI design), then T16 + T17 (scalability on the new Python base + SKILL.md extraction), then T4 + T5 + T6 (capability gaps now that parsing is solid), then T7 + T8 (portability + task tracking), then T18 (structured logs on the new `logs.py` module + `logs/` directory), then the remaining P2 items.
