"""Rendered views of the experience store.

The canonical source is ``data/experiences.jsonl`` (see :mod:`hkdata.experience`).
This module renders the human-readable markdown views:

  * ``logs/failure-log.md``       <- negative experiences (dead ends)
  * ``logs/strategy-registry.md`` <- positive experiences (what worked)

The markdown files are generated artefacts: edit the experiences, then run
``hkdata.py log-render``.
"""

from pathlib import Path
from typing import Dict, List, Optional

from . import experience

LOGS_DIR = Path(__file__).parent.parent.parent / "logs"

FAILURE_HEADER = """# hkdata Failure Log

Rendered from `data/experiences.jsonl` — **negative** experiences (dead ends).
Do not edit by hand; record an experience and run `hkdata.py log-render`.

"""
STRATEGY_HEADER = """# hkdata Strategy Registry

Rendered from `data/experiences.jsonl` — **positive** experiences (what worked).
Do not edit by hand; record an experience and run `hkdata.py log-render`.

"""


def _md_path(name: str) -> Path:
    return LOGS_DIR / f"{name}.md"


def _by_kind(records: List[Dict], kind: str) -> List[Dict]:
    return [r for r in records if r.get("kind") == kind]


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def render_failure_log(records: List[Dict]) -> str:
    """Render negative experiences as markdown cards (newest first)."""
    records = _by_kind(records, experience.KIND_NEGATIVE)
    lines = [FAILURE_HEADER]
    for rec in sorted(records, key=lambda r: r.get("date", ""), reverse=True):
        title = rec.get("topic") or "(untitled)"
        lines.append(f"### {rec.get('date') or '-'} | {title}\n")
        for label, value in [
            ("Kind", rec.get("kind")),
            ("Category", rec.get("category")),
            ("Datasets", ", ".join(rec.get("datasets") or [])),
            ("Method", rec.get("method")),
            ("Outcome", rec.get("outcome")),
            ("Caveats", "; ".join(rec.get("caveats") or [])),
            ("Details", rec.get("details")),
            ("Source", rec.get("source")),
        ]:
            if value:
                lines.append(f"- **{label}:** {value}")
        lines.append("\n---\n")
    return "\n".join(lines) + "\n"


def render_strategy_registry(records: List[Dict]) -> str:
    """Render positive experiences grouped by category."""
    records = _by_kind(records, experience.KIND_POSITIVE)
    by_category: Dict[str, List[Dict]] = {}
    for rec in records:
        by_category.setdefault(rec.get("category") or "Uncategorised", []).append(rec)

    lines = [STRATEGY_HEADER]
    for category in sorted(by_category):
        lines.append(f"### {category}\n")
        lines.append("| Topic | Method | Datasets | Date | Source |")
        lines.append("|-------|--------|----------|------|--------|")
        for rec in sorted(by_category[category], key=lambda r: r.get("date", ""), reverse=True):
            topic = (rec.get("topic") or "").replace("|", "\\|")
            method = (rec.get("method") or "").replace("|", "\\|").replace("\n", " ")
            datasets = ", ".join(rec.get("datasets") or []) or "-"
            lines.append(f"| {topic} | {method} | {datasets} | "
                         f"{rec.get('date') or '-'} | {rec.get('source') or '-'} |")
        lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# CLI actions
# ---------------------------------------------------------------------------


def render() -> None:
    """Regenerate both markdown views from the experience store."""
    records = experience.load_experiences()
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    _md_path("failure-log").write_text(
        render_failure_log(records), encoding="utf-8")
    _md_path("strategy-registry").write_text(
        render_strategy_registry(records), encoding="utf-8")


_KIND_ALIASES = {
    "failure-log": experience.KIND_NEGATIVE,
    "strategy-registry": experience.KIND_POSITIVE,
}


def log_search(names: Optional[List[str]], keywords: List[str]) -> List[Dict]:
    """Keyword search over experiences, optionally restricted by log name/kind."""
    wanted = {_KIND_ALIASES[n] for n in (names or []) if n in _KIND_ALIASES}
    needles = [k.lower() for k in keywords]
    results = []
    for rec in experience.load_experiences():
        if wanted and rec["kind"] not in wanted:
            continue
        blob = " ".join(str(v) for v in _flatten(rec)).lower()
        if all(n in blob for n in needles):
            results.append(rec)
    return results


def _flatten(obj):
    if isinstance(obj, dict):
        for value in obj.values():
            yield from _flatten(value)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            yield from _flatten(item)
    else:
        yield obj
