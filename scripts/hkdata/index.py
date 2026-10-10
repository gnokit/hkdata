"""Local search index builder and searcher for verified datasets."""

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from . import experience

REFERENCES_DIR = Path(__file__).parent.parent.parent / "references"
INDEX_PATH = REFERENCES_DIR / "search-index.json"
INDEX_MD_PATH = REFERENCES_DIR / "index.md"


def _experience_to_index_record(rec: Dict) -> Dict:
    """Convert an experience card into a searchable index record."""
    return {
        "id": rec["id"],
        "title": f"[{rec['kind']}] {rec['topic']}",
        "category": rec.get("category") or rec["kind"],
        "filename": "data/experiences.jsonl",
        "description": f"{rec.get('method', '')} → {rec.get('outcome', '')}",
        "keywords": _extract_keywords(" ".join([
            rec.get("topic", ""), rec.get("method", ""), rec.get("details", ""),
        ])),
        "endpoint": rec.get("endpoint", ""),
        "format": "",
        "temporality": "",
        "join_keys": [],
        "last_verified": rec.get("last_verified", ""),
        "known_quirks": rec.get("caveats", []),
        "fallback_search_terms": [],
        "_type": rec["kind"],
    }


def _extract_bold_field(text: str, field: str) -> str:
    pattern = rf"\*\*{re.escape(field)}:\*\*\s*(.*?)(?=\n\*\*|\n## |\n---|$)"
    match = re.search(pattern, text, re.DOTALL)
    if not match:
        return ""
    value = match.group(1).strip()
    # Remove backticks
    value = value.strip("`").strip()
    return value


def _extract_section(text: str, heading: str) -> str:
    pattern = rf"## {re.escape(heading)}\s*\n(.*?)(?=\n## |\n---|$)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not match:
        return ""
    return match.group(1).strip()


def _extract_endpoint(text: str) -> str:
    for field in ("Endpoint", "Base"):
        value = _extract_bold_field(text, field)
        if value:
            return value
    return ""


def _detect_format(endpoint: str, text: str) -> str:
    ep_lower = endpoint.lower()
    if ep_lower.endswith(".json") or "format=json" in ep_lower:
        return "json"
    if ep_lower.endswith(".xml") or "rss" in ep_lower:
        return "xml"
    if ep_lower.endswith(".csv"):
        return "csv"
    text_lower = text.lower()
    if "xml" in text_lower or "rss" in text_lower:
        return "xml"
    if "csv" in text_lower:
        return "csv"
    if "json" in text_lower:
        return "json"
    return "unknown"


def _detect_temporality(text: str) -> str:
    text_lower = text.lower()
    if any(k in text_lower for k in ("real-time", "real time", "live", "updates every", "1-min", "5-min", "hourly")):
        return "real-time"
    if any(k in text_lower for k in ("monthly", "quarterly", "annual", "yearly", "weekly")):
        return "historical"
    if any(k in text_lower for k in ("inventory", "list of", "locations", "static")):
        return "static"
    return "unknown"


def _detect_join_keys(text: str) -> List[str]:
    keys = []
    text_lower = text.lower()
    if "district" in text_lower:
        keys.append("district")
    if any(k in text_lower for k in ("period", "year", "month", "quarter", "date")):
        keys.append("period")
    if "station" in text_lower:
        keys.append("station")
    return keys


def _extract_keywords(text: str) -> List[str]:
    text = re.sub(r"[`'\".,;:!?()\[\]{}|\\/]", " ", text.lower())
    tokens = set()
    for token in text.split():
        if len(token) > 1:
            tokens.add(token)
    return sorted(tokens)


def _fallback_terms_for_dataset(dataset_id: str, title: str, category: str) -> List[str]:
    """Find web-search fallback terms from experiences that mention this dataset."""
    terms = []
    seen = set()
    for rec in experience.load_experiences():
        method = rec.get("method", "")
        text = f"{rec.get('topic', '')} {method} {rec.get('outcome', '')}".lower()
        if dataset_id.lower() in text and "site:data.gov.hk" in method:
            term = method.split("`")[1] if "`" in method else method
            if term not in seen:
                terms.append(term)
                seen.add(term)
    return terms


def parse_reference_file(path: Path) -> Optional[Dict]:
    """Parse a single reference markdown file into an index record."""
    text = path.read_text(encoding="utf-8")

    # Title is the first H1.
    title_match = re.search(r"^# (.+)$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem

    dataset_id = _extract_bold_field(text, "Dataset ID")
    provider = _extract_bold_field(text, "Provider")
    category = _extract_bold_field(text, "Category")
    # Strip parenthetical category code if present.
    category = re.sub(r"\s*\(.*\)$", "", category).strip().lower()

    description = _extract_section(text, "Description")
    if not description:
        # Use first paragraph before any section heading.
        first_para = re.split(r"\n## ", text, maxsplit=1)[0]
        # Remove header fields to get description.
        lines = [ln for ln in first_para.splitlines() if not ln.startswith("**") and ln.strip()]
        if lines:
            description = lines[0].strip()

    endpoint = _extract_endpoint(text)
    fmt = _detect_format(endpoint, text)
    temporality = _detect_temporality(text)
    join_keys = _detect_join_keys(text)

    notes = _extract_section(text, "Notes")
    known_quirks = [ln.strip("- ").strip() for ln in notes.splitlines() if ln.strip().startswith("-")]

    date_added = _extract_bold_field(text, "Date Added") or _extract_bold_field(text, "Added")

    if not dataset_id:
        # Aggregate reference files covering multiple datasets use the filename as a stable ID.
        dataset_id = path.stem

    keywords = _extract_keywords(f"{title} {description} {category} {provider} {endpoint}")

    return {
        "id": dataset_id,
        "title": title,
        "category": category,
        "filename": path.name,
        "description": description,
        "keywords": keywords,
        "endpoint": endpoint,
        "format": fmt,
        "temporality": temporality,
        "join_keys": join_keys,
        "last_verified": date_added,
        "known_quirks": known_quirks,
        "fallback_search_terms": _fallback_terms_for_dataset(dataset_id, title, category),
    }


def build_index() -> Dict:
    """Build search-index.json from all reference dataset docs."""
    records = []
    for path in sorted(REFERENCES_DIR.glob("*.md")):
        if path.name in ("template.md", "index.md", "category-mapping.md",
                         "workflow-guides.md"):
            continue
        record = parse_reference_file(path)
        if record:
            records.append(record)

    return {
        "version": 1,
        "count": len(records),
        "datasets": records,
    }


def save_index(index: Dict) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=2)


def _md_cell(text: str) -> str:
    """Escape a value for use inside a markdown table cell."""
    return str(text or "").replace("|", "\\|").replace("\n", " ").strip()


def render_index_md(index: Dict, path: Path = INDEX_MD_PATH) -> None:
    """Render the human-readable ``references/index.md`` registry from the index.

    This file is a **generated view** of ``search-index.json`` (it is private /
    gitignored and rebuilt by ``reindex``); never edit it by hand.
    """
    datasets = index.get("datasets", [])
    lines: List[str] = [
        "# Dataset Registry",
        "",
        "_Generated by `reindex` from `references/*.md` — do not edit by hand._",
        "",
        "Master index of verified Hong Kong open data APIs.",
        "",
        "## Verified Datasets",
        "",
        "| Dataset | Category | Description | File |",
        "|---------|----------|-------------|------|",
    ]
    for rec in sorted(datasets, key=lambda r: (r.get("category", ""), r.get("title", ""))):
        fname = rec.get("filename", "")
        lines.append(
            f"| {_md_cell(rec.get('title'))} | {_md_cell(rec.get('category'))} | "
            f"{_md_cell(rec.get('description'))} | [{_md_cell(fname)}]({fname}) |"
        )

    lines += ["", "## By Category", ""]
    by_category: Dict[str, List[Dict]] = {}
    for rec in datasets:
        by_category.setdefault(rec.get("category") or "Uncategorised", []).append(rec)
    for category in sorted(by_category):
        lines.append(f"### {category}")
        for rec in sorted(by_category[category], key=lambda r: r.get("title", "")):
            fname = rec.get("filename", "")
            lines.append(f"- [{_md_cell(fname)}]({fname}) - {_md_cell(rec.get('title'))}")
        lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def load_index() -> Dict:
    if not INDEX_PATH.exists():
        return {"version": 1, "count": 0, "datasets": []}
    with INDEX_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def score_dataset(query: str, record: Dict) -> float:
    """Simple keyword-overlap scoring."""
    query_tokens = set(_extract_keywords(query))
    if not query_tokens:
        return 0.0

    text = " ".join([
        record.get("title", ""),
        record.get("description", ""),
        record.get("category", ""),
        " ".join(record.get("keywords", [])),
    ]).lower()
    text_tokens = set(text.split())

    matches = query_tokens & text_tokens
    return len(matches) / len(query_tokens)


def search_local(query: str, top_n: int = 10, include_logs: bool = True) -> List[Tuple[str, float, Dict]]:
    """Return top-N matching datasets (and optionally log records) for a query.

    Each result is a tuple of (result_type, score, record).
    """
    index = load_index()
    scored = []
    for record in index.get("datasets", []):
        score = score_dataset(query, record)
        if score > 0:
            record = dict(record)
            record.setdefault("_type", "dataset")
            scored.append((record["_type"], score, record))

    if include_logs:
        for rec in experience.load_experiences():
            idx_record = _experience_to_index_record(rec)
            score = score_dataset(query, idx_record)
            if score > 0:
                scored.append((idx_record["_type"], score, idx_record))

    scored.sort(key=lambda x: (-x[1], x[2]["title"]))
    return scored[:top_n]
