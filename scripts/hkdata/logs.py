"""Structured failure-log and strategy-registry management.

Records are stored as JSONL (one JSON object per line). Markdown files are
regenerated from JSONL for human reading.
"""

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional


def _log_path(name: str) -> Path:
    return Path(__file__).parent.parent.parent / "logs" / f"{name}.jsonl"


def _md_path(name: str) -> Path:
    return Path(__file__).parent.parent.parent / "logs" / f"{name}.md"


def load_jsonl(name: str) -> List[Dict]:
    path = _log_path(name)
    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(name: str, records: List[Dict]) -> None:
    path = _log_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_record(name: str, record: Dict) -> None:
    path = _log_path(name)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def search_records(name: str, keywords: Iterable[str]) -> List[Dict]:
    """Return records where any keyword appears in any string field."""
    keywords = [kw.lower() for kw in keywords]
    matches = []
    for record in load_jsonl(name):
        text = " ".join(str(v) for v in _flatten(record)).lower()
        if any(kw in text for kw in keywords):
            matches.append(record)
    return matches


def _flatten(obj):
    if isinstance(obj, dict):
        for v in obj.values():
            yield from _flatten(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _flatten(item)
    else:
        yield obj


# ---------------------------------------------------------------------------
# Markdown migration / rendering for failure-log
# ---------------------------------------------------------------------------

FAILURE_HEADER = """# hkdata Failure Log

記錄每次 script/tool 失敗的原因和解決方案。Subagent 起動時自動讀取。

## 格式

```
## [日期] Task: <任務描述>

**失敗組件:** <script/API/tool 名稱>
**錯誤現象:** <實際輸出/錯誤信息>
**根本原因:** <為什麼失敗>
**解決方案:** <用咩方法搞掂>
**驗證:** <成功與否>
```

---

## 記錄

"""

FAILURE_FOOTER = "\n<!-- 新記錄請加喺上面 -->\n"


def parse_failure_markdown(text: str) -> List[Dict]:
    """Parse the existing failure-log.md into structured records."""
    records = []
    # Split on record headings: ### YYYY-MM-DD | Task: ...
    parts = re.split(r"\n### (\d{4}-\d{2}-\d{2}) \| Task: ([^\n]+)\n", text)
    # parts[0] is header, then date, task, body, date, task, body, ...
    for i in range(1, len(parts), 3):
        date = parts[i].strip()
        task = parts[i + 1].strip()
        body = parts[i + 2].strip()

        component = _extract_field(body, "失敗組件")
        symptom = _extract_field(body, "錯誤現象")
        root_cause = _extract_field(body, "根本原因")
        solution = _extract_field(body, "解決方案")
        verification = _extract_field(body, "驗證")

        keywords = [date, task, component, symptom, root_cause]
        records.append({
            "date": date,
            "task": task,
            "component": component,
            "symptom": symptom,
            "root_cause": root_cause,
            "solution": solution,
            "verification": verification,
            "keywords": _extract_keywords(keywords),
        })
    return records


def render_failure_log(records: List[Dict]) -> str:
    lines = [FAILURE_HEADER]
    for rec in records:
        lines.append(f"### {rec['date']} | Task: {rec['task']}\n")
        for field, label in [
            ("component", "失敗組件"),
            ("symptom", "錯誤現象"),
            ("root_cause", "根本原因"),
            ("solution", "解決方案"),
            ("verification", "驗證"),
        ]:
            value = rec.get(field, "")
            if value.startswith("-") or value.startswith("1."):
                lines.append(f"**{label}:**\n{value}\n")
            else:
                lines.append(f"**{label}:** {value}\n")
        lines.append("---\n")
    lines.append(FAILURE_FOOTER)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Markdown migration / rendering for strategy-registry
# ---------------------------------------------------------------------------

STRATEGY_HEADER = """# hkdata Strategy Registry

記錄邊個關鍵字/方法喺邊個 category 成功過，避免重複試失敗的方法。

## 格式

```
## [Category/Topic]
- **關鍵字:** "xxx" → 結果 ✅/❌
- **方法:** "web search: site:data.gov.hk xxx" → 結果
```

---

## 成功策略記錄

"""

STRATEGY_FOOTER = "\n<!-- 新記錄請加喺上面 -->\n"


def parse_strategy_markdown(text: str) -> List[Dict]:
    """Parse the existing strategy-registry.md into structured records."""
    records = []
    # Split on category headings: ### Category Name
    parts = re.split(r"\n### ([^\n]+)\n", text)
    # parts[0] is header, then category, body, ...
    for i in range(1, len(parts), 2):
        category = parts[i].strip()
        body = parts[i + 1].strip()
        # Extract table rows
        for line in body.splitlines():
            line = line.strip()
            if not line or line.startswith("|") and ("---" in line or "Topic" in line):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 3:
                topic, method, result = cells[0], cells[1], cells[2]
                records.append({
                    "category": category,
                    "topic": topic,
                    "method": method,
                    "result": result,
                    "keywords": _extract_keywords([category, topic, method, result]),
                })
    return records


def render_strategy_registry(records: List[Dict]) -> str:
    # Group by category
    by_category: Dict[str, List[Dict]] = {}
    for rec in records:
        by_category.setdefault(rec["category"], []).append(rec)

    lines = [STRATEGY_HEADER]
    for category in sorted(by_category):
        lines.append(f"### {category}\n")
        lines.append("| Topic | 嘗試方法 | 結果 |")
        lines.append("|-------|---------|------|")
        for rec in by_category[category]:
            lines.append(f"| {rec['topic']} | {rec['method']} | {rec['result']} |")
        lines.append("")
    lines.append(STRATEGY_FOOTER)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_field(body: str, field_name: str) -> str:
    # Stop at the next bold field, horizontal rule, next record heading, or EOF.
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s*(.*?)(?=\n\*\*|\n---|\n### |$)"
    match = re.search(pattern, body, re.DOTALL)
    if not match:
        return ""
    value = match.group(1).strip()
    return value


def _extract_keywords(texts: List[str]) -> List[str]:
    """Extract searchable keywords from a list of text snippets."""
    combined = " ".join(str(t) for t in texts if t).lower()
    # Remove backticks and common punctuation
    cleaned = re.sub(r"[`'\".,;:!?()\[\]{}]", " ", combined)
    tokens = set()
    for token in cleaned.split():
        if len(token) > 1:
            tokens.add(token)
    return sorted(tokens)


# ---------------------------------------------------------------------------
# CLI actions
# ---------------------------------------------------------------------------

def migrate() -> None:
    """One-off migration from existing markdown files to JSONL."""
    failure_md = _md_path("failure-log")
    strategy_md = _md_path("strategy-registry")

    if failure_md.exists():
        records = parse_failure_markdown(failure_md.read_text(encoding="utf-8"))
        save_jsonl("failure-log", records)

    if strategy_md.exists():
        records = parse_strategy_markdown(strategy_md.read_text(encoding="utf-8"))
        save_jsonl("strategy-registry", records)


def render() -> None:
    """Regenerate markdown files from JSONL."""
    failure_records = load_jsonl("failure-log")
    _md_path("failure-log").write_text(
        render_failure_log(failure_records), encoding="utf-8"
    )

    strategy_records = load_jsonl("strategy-registry")
    _md_path("strategy-registry").write_text(
        render_strategy_registry(strategy_records), encoding="utf-8"
    )


def log_search(names: List[str], keywords: List[str]) -> List[Dict]:
    """Search one or more log JSONL files by keywords."""
    results = []
    for name in names:
        for record in search_records(name, keywords):
            record["_source"] = name
            results.append(record)
    return results
