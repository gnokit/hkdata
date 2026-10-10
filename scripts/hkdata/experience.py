"""Experience memory: positive and negative lessons from past discoveries.

Canonical store: ``data/experiences.jsonl`` (append-only, committed, PII-free).
Semantic index: Chroma collection ``hkdata_experiences`` (derived, gitignored).

An experience is a short **pointer card**, not an answer. It records the
questions it answers, the datasets/endpoints involved, the method that worked
(positive) or the dead end (negative), and caveats. The embedded document
deliberately excludes any finished answer so the vector index *routes* the agent
rather than serving stale prose.
"""

import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from . import catalog, vectors

EXPERIENCES_PATH = catalog.ROOT / "data" / "experiences.jsonl"
LOGS_DIR = catalog.ROOT / "logs"
COLLECTION_NAME = "hkdata_experiences"

KIND_POSITIVE = "positive"
KIND_NEGATIVE = "negative"

# Controlled --outcome vocabulary (see SKILL.md Step 5). "unavailable" means the
# data does not exist on data.gov.hk; "pitfall" means this *path* is dead/retired
# but the data may still live elsewhere — Step 1 must handle them differently.
OUTCOMES = ("verified", "located", "resolved", "unavailable", "pitfall")
NEGATIVE_OUTCOMES = ("unavailable", "pitfall")

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


# ---------------------------------------------------------------------------
# Record construction (pure)
# ---------------------------------------------------------------------------


def _scrub(text: str) -> str:
    """Remove email addresses so cards stay PII-free."""
    return _EMAIL_RE.sub("[email]", str(text)).strip()


def make_id(kind: str, topic: str, source: str = "") -> str:
    digest = hashlib.sha1(f"{kind}|{topic}|{source}".encode("utf-8")).hexdigest()
    return f"exp-{digest[:12]}"


def _as_list(value) -> List[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [_scrub(v) for v in value if str(v).strip()]
    return [_scrub(value)] if str(value).strip() else []


def normalize(exp: Dict) -> Dict:
    """Coerce a loose dict into the canonical experience card."""
    kind = str(exp.get("kind") or KIND_POSITIVE).lower()
    if kind not in (KIND_POSITIVE, KIND_NEGATIVE):
        kind = KIND_POSITIVE
    topic = _scrub(exp.get("topic") or "untitled")
    source = _scrub(exp.get("source") or "")
    return {
        "id": exp.get("id") or make_id(kind, topic, source),
        "kind": kind,
        "topic": topic,
        "query_patterns": _as_list(exp.get("query_patterns")),
        "category": _scrub(exp.get("category") or ""),
        "datasets": _as_list(exp.get("datasets")),
        "method": _scrub(exp.get("method") or ""),
        "endpoint": _scrub(exp.get("endpoint") or ""),
        "outcome": _scrub(exp.get("outcome") or ""),
        "caveats": _as_list(exp.get("caveats")),
        "details": _scrub(exp.get("details") or ""),
        "source": source,
        "date": str(exp.get("date") or time.strftime("%Y-%m-%d")),
        "last_verified": str(exp.get("last_verified") or exp.get("date")
                             or time.strftime("%Y-%m-%d")),
    }


def build_document(exp: Dict) -> str:
    """The text embedded for an experience. Never includes a finished answer."""
    exp = normalize(exp)
    parts = [exp["topic"]]
    if exp["query_patterns"]:
        parts.append("Questions: " + "; ".join(exp["query_patterns"]))
    if exp["category"]:
        parts.append("Category: " + exp["category"])
    if exp["datasets"]:
        parts.append("Datasets: " + ", ".join(exp["datasets"]))
    if exp["method"]:
        parts.append("Method: " + exp["method"])
    if exp["endpoint"]:
        parts.append("Endpoint: " + exp["endpoint"])
    if exp["outcome"]:
        parts.append("Outcome: " + exp["outcome"])
    if exp["caveats"]:
        parts.append("Caveats: " + "; ".join(exp["caveats"]))
    if exp["details"]:
        parts.append("Details: " + exp["details"][:400])
    parts.append("Kind: " + exp["kind"])
    return "\n".join(parts)


def build_metadata(exp: Dict, model: str = "") -> Dict:
    exp = normalize(exp)
    return {
        "id": exp["id"],
        "kind": exp["kind"],
        "topic": exp["topic"],
        "category": exp["category"],
        "datasets": ",".join(exp["datasets"]),
        "endpoint": exp["endpoint"],
        "outcome": exp["outcome"],
        "source": exp["source"],
        "date": exp["date"],
        "last_verified": exp["last_verified"],
        "text_hash": vectors.text_hash(build_document(exp)),
        "model": model or vectors.DEFAULT_MODEL,
    }


# ---------------------------------------------------------------------------
# Canonical JSONL store
# ---------------------------------------------------------------------------


def load_experiences(path: Path = EXPERIENCES_PATH) -> List[Dict]:
    if not Path(path).exists():
        return []
    records = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(normalize(json.loads(line)))
            except json.JSONDecodeError:
                continue
    return records


def save_experiences(records: List[Dict], path: Path = EXPERIENCES_PATH) -> None:
    merged: Dict[str, Dict] = {}
    for record in records:
        record = normalize(record)
        merged[record["id"]] = record
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for record in merged.values():
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_experience(exp: Dict, paths: Optional[catalog.CatalogPaths] = None,
                      path: Path = EXPERIENCES_PATH, *,
                      model: str = vectors.DEFAULT_MODEL,
                      url: str = vectors.DEFAULT_OLLAMA_URL,
                      embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
                      client=None,
                      collection_name: str = COLLECTION_NAME,
                      upsert: bool = True,
                      verbose: bool = True) -> Dict:
    """Append one experience to the JSONL store and (optionally) its vector."""
    record = normalize(exp)
    records = load_experiences(path)
    records = [r for r in records if r["id"] != record["id"]] + [record]
    save_experiences(records, path)
    if upsert:
        upsert_experiences([record], paths=paths, model=model, url=url,
                           embed_fn=embed_fn, client=client,
                           collection_name=collection_name, verbose=verbose)
    return record


# ---------------------------------------------------------------------------
# ChromaDB index
# ---------------------------------------------------------------------------


def upsert_experiences(records: List[Dict],
                       paths: Optional[catalog.CatalogPaths] = None,
                       model: str = vectors.DEFAULT_MODEL,
                       url: str = vectors.DEFAULT_OLLAMA_URL,
                       batch: int = vectors.EMBED_BATCH,
                       collection_name: str = COLLECTION_NAME,
                       embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
                       client=None, verbose: bool = True) -> int:
    if embed_fn is None:
        def embed_fn(texts: List[str]) -> List[List[float]]:
            return vectors.embed_texts(texts, model=model, url=url)
    if client is None:
        client = vectors._client(paths or catalog.default_paths())
    collection = vectors._collection(client, collection_name)
    for start in range(0, len(records), batch):
        chunk = [normalize(r) for r in records[start:start + batch]]
        collection.upsert(
            ids=[r["id"] for r in chunk],
            embeddings=embed_fn([build_document(r) for r in chunk]),
            documents=[build_document(r) for r in chunk],
            metadatas=[build_metadata(r, model) for r in chunk],
        )
    return len(records)


def embed_experiences(paths: Optional[catalog.CatalogPaths] = None,
                      model: str = vectors.DEFAULT_MODEL,
                      url: str = vectors.DEFAULT_OLLAMA_URL,
                      batch: int = vectors.EMBED_BATCH,
                      collection_name: str = COLLECTION_NAME,
                      embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
                      client=None, verbose: bool = True) -> dict:
    """Rebuild the experience collection, re-embedding only changed cards."""
    records = load_experiences()
    if embed_fn is None:
        def embed_fn(texts: List[str]) -> List[List[float]]:
            return vectors.embed_texts(texts, model=model, url=url)
    if client is None:
        client = vectors._client(paths or catalog.default_paths())
    collection = vectors._collection(client, collection_name)

    existing = collection.get(include=["metadatas"])
    known = {i: (m or {}) for i, m in zip(existing["ids"], existing["metadatas"])}

    pending = []
    for record in records:
        meta = build_metadata(record, model)
        old = known.get(record["id"])
        if (old is None or old.get("text_hash") != meta["text_hash"]
                or old.get("model") != model):
            pending.append(record)

    written = 0
    for start in range(0, len(pending), batch):
        chunk = pending[start:start + batch]
        collection.upsert(
            ids=[r["id"] for r in chunk],
            embeddings=embed_fn([build_document(r) for r in chunk]),
            documents=[build_document(r) for r in chunk],
            metadatas=[build_metadata(r, model) for r in chunk],
        )
        written += len(chunk)
        if verbose:
            print(f"  embedded {written}/{len(pending)}", file=sys.stderr)

    stale = [i for i in known if i not in {r["id"] for r in records}]
    if stale:
        collection.delete(ids=stale)

    if verbose:
        print(f"Experiences: {collection.count()} total, {written} (re)embedded, "
              f"{len(stale)} removed", file=sys.stderr)
    return {"total": collection.count(), "embedded": written, "removed": len(stale)}


def count(paths: Optional[catalog.CatalogPaths] = None,
          collection_name: str = COLLECTION_NAME) -> int:
    try:
        client = vectors._client(paths or catalog.default_paths())
        return vectors._collection(client, collection_name).count()
    except Exception:
        return 0


DEFAULT_MIN_SIM = 0.5


def search(query: str, paths: Optional[catalog.CatalogPaths] = None,
           top_n: Optional[int] = 5, offset: int = 0,
           min_sim: float = DEFAULT_MIN_SIM, kind: Optional[str] = None,
           model: str = vectors.DEFAULT_MODEL,
           url: str = vectors.DEFAULT_OLLAMA_URL,
           collection_name: str = COLLECTION_NAME,
           embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
           client=None, verbose: bool = True,
           query_instruction: str = vectors.QUERY_INSTRUCTION) -> List[dict]:
    """Return a relevance-ranked page of past experience cards.

    Cards are ranked by **dense cosine similarity** (nearest first), with a
    secondary keyword pass for literal-token recall. Cards below ``min_sim`` are
    dropped, so an unrelated query returns fewer (or zero) cards instead of a
    fixed-length list of loosely related ones. ``top_n=None`` returns all matches
    (used for paging); ``offset`` pages through them.
    """
    if embed_fn is None:
        def embed_fn(texts: List[str]) -> List[List[float]]:
            return vectors.embed_texts(texts, model=model, url=url)
    if client is None:
        client = vectors._client(paths or catalog.default_paths())
    collection = vectors._collection(client, collection_name)
    if collection.count() == 0:
        if verbose:
            print("No experiences yet. Run: hkdata.py experience-migrate && "
                  "hkdata.py experience-embed", file=sys.stderr)
        return []

    where = {"kind": kind} if kind in (KIND_POSITIVE, KIND_NEGATIVE) else None
    # The dense query uses the raw query only: alias expansion belongs to the
    # keyword pass. Appending department aliases here (e.g. 康文署 → 康樂及文化
    # 事務署/LCSD/…) drowns the domain term (e.g. 羽毛球場) and drops the match.
    query_vector = embed_fn([query_instruction + query])[0]
    total = collection.count()

    def _card(meta: dict, exp_id: str, sim: Optional[float]) -> dict:
        return {
            "id": exp_id,
            "kind": meta.get("kind", ""),
            "topic": meta.get("topic", ""),
            "category": meta.get("category", ""),
            "datasets": [d for d in (meta.get("datasets") or "").split(",") if d],
            "endpoint": meta.get("endpoint", ""),
            "outcome": meta.get("outcome", ""),
            "source": meta.get("source", ""),
            "date": meta.get("date", ""),
            "similarity": sim,
        }

    matched: List[dict] = []
    seen: set = set()

    dense = collection.query(query_embeddings=[query_vector], n_results=total,
                             where=where, include=["metadatas", "distances"])
    for meta, dist in zip(dense["metadatas"][0], dense["distances"][0]):
        meta = meta or {}
        exp_id = meta.get("id", "")
        sim = 1.0 - float(dist)
        if sim < min_sim:
            continue
        seen.add(exp_id)
        matched.append(_card(meta, exp_id, sim))

    # Keyword pass: literal-token recall (query terms + alias spellings, incl.
    # multi-word official names), appended after the dense hits.
    tokens = [t for t in re.findall(r"[A-Za-z0-9\u3400-\u4dbf\u4e00-\u9fff]+", query)
              if len(t) >= 2]
    for value in vectors.expand_query(query):
        if value:
            tokens.append(value)
    for token in list(dict.fromkeys(tokens))[:4]:
        try:
            kw = collection.query(
                query_embeddings=[query_vector], n_results=total, where=where,
                where_document={"$regex": f"(?i){re.escape(token)}"},
                include=["metadatas", "distances"])
        except Exception:
            continue
        for meta, dist in zip(kw["metadatas"][0], kw["distances"][0]):
            meta = meta or {}
            exp_id = meta.get("id", "")
            if exp_id in seen:
                continue
            seen.add(exp_id)
            matched.append(_card(meta, exp_id, 1.0 - float(dist)))

    if top_n is None:
        return matched[offset:]
    return matched[offset:offset + top_n]


# ---------------------------------------------------------------------------
# Migration from existing references + logs
# ---------------------------------------------------------------------------


def _load_jsonl(path: Path) -> List[Dict]:
    if not Path(path).exists():
        return []
    out = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out


_CANDIDATE_RE = re.compile(r"\b[a-z][a-z0-9_]*(?:-[a-z0-9_]+)+\b")
_seed_cache: Optional[set] = None


def _dataset_ids(text: str) -> List[str]:
    """Extract dataset IDs from free text, keeping only ones in the catalog seed."""
    global _seed_cache
    if _seed_cache is None:
        _seed_cache = set(catalog.load_seed(catalog.default_paths()))
    candidates = set(_CANDIDATE_RE.findall(text.lower()))
    return sorted(candidates & _seed_cache)


# Phrases that mean "this data does not exist on the portal", regardless of
# whether the search itself succeeded (verification ✅).
_UNAVAILABLE = (
    "無此數據", "並不存在", "不存在", "唔存在", "沒有此", "無可用",
    "not available", "not published", "no dataset", "not on data.gov.hk",
    "0 results", "unavailable", "not found",
)


def _is_unavailable(*texts: str) -> bool:
    blob = " ".join(t.lower() for t in texts if t)
    return any(phrase in blob for phrase in _UNAVAILABLE)


def cards_from_references(references_dir: Path) -> List[Dict]:
    """One positive card per curated dataset reference document."""
    from .index import parse_reference_file

    cards = []
    for path in sorted(Path(references_dir).glob("*.md")):
        if path.name in ("template.md", "index.md", "category-mapping.md",
                         "workflow-guides.md"):
            continue
        try:
            rec = parse_reference_file(path)
        except Exception:
            continue
        if not rec:
            continue
        cards.append({
            "kind": KIND_POSITIVE,
            "topic": rec.get("title") or path.stem,
            "query_patterns": [rec.get("title") or path.stem],
            "category": rec.get("category") or "",
            "datasets": [rec["id"]],
            "method": rec.get("description") or "",
            "endpoint": rec.get("endpoint") or "",
            "outcome": "verified",
            "caveats": rec.get("known_quirks") or [],
            "source": f"references/{path.name}",
            "last_verified": rec.get("last_verified") or "",
        })
    return cards


def cards_from_logs(logs_dir: Path = LOGS_DIR) -> List[Dict]:
    """Positive/negative cards from the strategy registry and failure log."""
    cards = []
    for rec in _load_jsonl(Path(logs_dir) / "strategy-registry.jsonl"):
        result = str(rec.get("result") or "")
        method = str(rec.get("method") or "")
        kind = KIND_POSITIVE
        if "❌" in result or result.strip().startswith("⚠️") or _is_unavailable(result, method):
            kind = KIND_NEGATIVE
        cards.append({
            "kind": kind,
            "topic": f"{rec.get('category', '')} — {rec.get('topic', '')}".strip(" —"),
            "query_patterns": [rec.get("topic", "")],
            "category": str(rec.get("category") or ""),
            "datasets": _dataset_ids(f"{method} {result}"),
            "method": method,
            "outcome": result,
            "caveats": [],
            "details": "",
            "source": "strategy-registry",
            "date": str(rec.get("date") or ""),
        })
    for rec in _load_jsonl(Path(logs_dir) / "failure-log.jsonl"):
        verification = str(rec.get("verification") or "")
        kind = KIND_POSITIVE
        if ("✅" not in verification) or _is_unavailable(
                rec.get("task", ""), rec.get("symptom", ""),
                rec.get("root_cause", ""), rec.get("solution", ""), verification):
            kind = KIND_NEGATIVE
        details = " ".join(str(rec.get(k) or "") for k in
                           ("symptom", "root_cause", "verification")).strip()
        cards.append({
            "kind": kind,
            "topic": str(rec.get("task") or ""),
            "query_patterns": [],
            "category": str(rec.get("component") or ""),
            "datasets": _dataset_ids(f"{rec.get('task','')} {rec.get('solution','')}"),
            "method": str(rec.get("solution") or rec.get("root_cause") or ""),
            "outcome": "resolved" if kind == KIND_POSITIVE else "unavailable",
            "caveats": [str(rec.get("root_cause"))] if rec.get("root_cause") else [],
            "details": details,
            "source": "failure-log",
            "date": str(rec.get("date") or ""),
        })
    return cards


def migrate(references_dir: Path = catalog.REFERENCES_DIR,
            logs_dir: Path = LOGS_DIR,
            path: Path = EXPERIENCES_PATH, verbose: bool = True) -> dict:
    """Upsert reference-derived cards into ``data/experiences.jsonl``.

    ``experiences.jsonl`` is the canonical store: existing cards (including ones
    originally seeded from the logs, and hand-written ones) are preserved, while
    a card per curated reference document is added or refreshed. Where the legacy
    ``logs/*.jsonl`` files still exist they are also ingested, then deduped by
    ``(topic, source)``.
    """
    cards = cards_from_references(references_dir) + cards_from_logs(logs_dir)
    merged: Dict[str, Dict] = {r["id"]: r for r in load_experiences(path)}
    for card in cards:
        record = normalize(card)
        merged[record["id"]] = record

    # Collapse true duplicates (same topic+source+method, e.g. a kind flip whose
    # id changed), while keeping distinct methods for the same topic.
    deduped: Dict[Tuple[str, str, str], Dict] = {}
    for record in merged.values():
        deduped[(record["topic"], record["source"], record["method"])] = record
    records = list(deduped.values())
    save_experiences(records, path)

    positives = sum(1 for r in records if r["kind"] == KIND_POSITIVE)
    negatives = len(records) - positives
    if verbose:
        print(f"Experiences: {len(records)} cards ({positives} positive, "
              f"{negatives} negative) -> {path}", file=sys.stderr)
    return {"total": len(records), "positive": positives, "negative": negatives}
