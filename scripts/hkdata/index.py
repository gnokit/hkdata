"""Local search index builder and searcher for verified datasets."""

import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from .logs import load_jsonl, search_records

REFERENCES_DIR = Path(__file__).parent.parent.parent / "references"
INDEX_PATH = REFERENCES_DIR / "search-index.json"


def _log_record_to_index_record(record: Dict, source: str) -> Dict:
    """Convert a failure/strategy log record into a searchable index record."""
    if source == "failure-log":
        return {
            "id": f"failure:{record['date']}:{record['task']}",
            "title": f"[Failure] {record['task']}",
            "category": "failure",
            "filename": "logs/failure-log.jsonl",
            "description": f"{record['symptom']} Root cause: {record['root_cause']}",
            "keywords": record.get("keywords", []),
            "endpoint": "",
            "format": "",
            "temporality": "",
            "join_keys": [],
            "last_verified": record.get("date", ""),
            "known_quirks": [],
            "fallback_search_terms": [],
            "_type": "failure",
        }
    return {
        "id": f"strategy:{record['category']}:{record['topic']}",
        "title": f"[Strategy] {record['category']} — {record['topic']}",
        "category": "strategy",
        "filename": "logs/strategy-registry.jsonl",
        "description": f"{record['method']} → {record['result']}",
        "keywords": record.get("keywords", []),
        "endpoint": "",
        "format": "",
        "temporality": "",
        "join_keys": [],
        "last_verified": "",
        "known_quirks": [],
        "fallback_search_terms": [],
        "_type": "strategy",
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
    """Find web-search fallback terms from strategy-registry that mention this dataset/topic."""
    terms = []
    seen = set()
    strategies = load_jsonl("strategy-registry")
    for rec in strategies:
        result = rec.get("result", "")
        method = rec.get("method", "")
        topic = rec.get("topic", "")
        text = f"{topic} {method} {result}".lower()
        if dataset_id.lower() in text:
            if "site:data.gov.hk" in method:
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
        if path.name in ("template.md", "index.md", "category-mapping.md"):
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
        for source in ("failure-log", "strategy-registry"):
            for record in search_records(source, query.split()):
                idx_record = _log_record_to_index_record(record, source)
                score = score_dataset(query, idx_record)
                if score > 0:
                    scored.append((idx_record["_type"], score, idx_record))

    scored.sort(key=lambda x: (-x[1], x[2]["title"]))
    return scored[:top_n]
