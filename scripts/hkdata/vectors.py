"""Search layer: ChromaDB over the offline catalog, embedded via local Ollama.

There is no SQLite/FTS5 search anymore — ChromaDB is the only search store.
Embeddings are computed here (via the Ollama HTTP API) and passed to Chroma
explicitly, so the extra ``ollama`` Python package is not required.

Layout::

    .cache/catalog/chroma/           ChromaDB PersistentClient directory (gitignored)
    data/catalog/*.jsonl             sanitized source documents (see hkdata.catalog)
    references/aliases.json          query-time abbreviation expansion
"""

import hashlib
import json
import re
import sys
from typing import Callable, Dict, List, Optional

from . import catalog
from .embeddings import (
    DEFAULT_MODEL,
    DEFAULT_OLLAMA_URL,
    EMBED_BATCH,
    EMBED_TIMEOUT,
    QWEN_QUERY_INSTRUCTION,
    registered_providers,
    resolve_embedder,
)

COLLECTION_NAME = "hkdata_datasets"
ALIASES_PATH = catalog.REFERENCES_DIR / "aliases.json"

# Backward-compatible alias: qwen3's query-side instruction prefix. New code should
# use the per-provider ``query_instruction`` from :func:`resolve_embedder` instead.
QUERY_INSTRUCTION = QWEN_QUERY_INSTRUCTION


# ---------------------------------------------------------------------------
# Embeddings (delegated to the pluggable backend)
# ---------------------------------------------------------------------------


def embed_texts(texts: List[str], model: str = DEFAULT_MODEL,
                url: str = DEFAULT_OLLAMA_URL) -> List[List[float]]:
    """Embed a batch of texts via the local Ollama API (backward-compatible)."""
    from . import embeddings
    return embeddings._ollama_embed(texts, model, url)


def ollama_available(url: str = DEFAULT_OLLAMA_URL) -> bool:
    from . import embeddings
    return embeddings.ollama_available(url)


# ---------------------------------------------------------------------------
# Document / metadata construction (pure, testable)
# ---------------------------------------------------------------------------


def _locale_view(record: Dict, locale: str) -> Dict:
    """Return the per-locale metadata view for ``tc``/``sc`` if present."""
    if locale == "en":
        return record
    locales = record.get("locales") or {}
    view = locales.get(locale)
    return view if isinstance(view, dict) else {}


def _org_title(record: Dict) -> str:
    org = record.get("organization")
    if isinstance(org, dict):
        return org.get("title") or org.get("name") or ""
    return ""


def _formats(record: Dict) -> List[str]:
    formats = {(r.get("format") or "").upper() for r in record.get("resources", [])}
    return sorted(f for f in formats if f)


def _is_api(record: Dict) -> bool:
    return any(r.get("is_api") in (True, "true", "True", 1)
               for r in record.get("resources", []))


def build_document(record: Dict) -> str:
    """Compose the multilingual text that gets embedded for one dataset."""
    en, tc, sc = record, _locale_view(record, "tc"), _locale_view(record, "sc")

    titles = [t for t in (en.get("title"), tc.get("title"), sc.get("title")) if t]
    parts: List[str] = []
    if titles:
        parts.append(" | ".join(dict.fromkeys(titles)))
    for view in (en, tc, sc):
        notes = (view.get("notes") or "").strip()
        if notes:
            parts.append(notes)

    orgs = [o for o in (_org_title(en), _org_title(tc)) if o]
    if orgs:
        parts.append("Organisation: " + " / ".join(dict.fromkeys(orgs)))

    groups = [g.get("title") or g.get("name", "") for g in record.get("groups", [])]
    groups = [g for g in groups if g]
    if groups:
        parts.append("Category: " + ", ".join(groups))

    formats = _formats(record)
    if formats:
        parts.append("Formats: " + ", ".join(formats))

    tags = [t.get("name") for t in record.get("tags", []) if t.get("name")]
    if tags:
        parts.append("Tags: " + ", ".join(tags))

    return "\n".join(parts)


def build_metadata(record: Dict, model: str, text_hash: str) -> Dict:
    """Compose the scalar metadata stored alongside each vector."""
    en, tc, sc = record, _locale_view(record, "tc"), _locale_view(record, "sc")
    groups = [g.get("title") or g.get("name", "") for g in record.get("groups", [])]
    locales = ["en"] + [loc for loc in ("tc", "sc") if _locale_view(record, loc)]
    return {
        "name": record.get("name", ""),
        "title_en": en.get("title") or "",
        "title_tc": tc.get("title") or "",
        "title_sc": sc.get("title") or "",
        "org_en": _org_title(en),
        "org_tc": _org_title(tc),
        "groups": ",".join(g for g in groups if g),
        "formats": ",".join(_formats(record)),
        "num_resources": len(record.get("resources", [])),
        "is_api": _is_api(record),
        "is_open": bool(record.get("isopen")),
        "update_frequency": str(record.get("update_frequency") or ""),
        "metadata_modified": str(record.get("metadata_modified") or ""),
        "locales": ",".join(locales),
        "text_hash": text_hash,
        "model": model,
    }


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Alias expansion (e.g. 康文署 -> 康樂及文化事務署 / LCSD)
# ---------------------------------------------------------------------------


def load_aliases(path=ALIASES_PATH) -> Dict[str, List[str]]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return {str(k): [str(v) for v in (vals or [])]
            for k, vals in data.items() if not str(k).startswith("_")}


def expand_query(query: str, aliases: Optional[Dict[str, List[str]]] = None) -> List[str]:
    """Return alias spellings of any alias key present in the query."""
    if aliases is None:
        aliases = load_aliases()
    expanded: List[str] = []
    for key, values in aliases.items():
        if key and key.lower() in query.lower():
            for value in values:
                if value and value.lower() not in query.lower():
                    expanded.append(value)
    return list(dict.fromkeys(expanded))


# ---------------------------------------------------------------------------
# ChromaDB store
# ---------------------------------------------------------------------------


def _vector_dir(paths: catalog.CatalogPaths):
    # Derived/regenerable -> kept out of the tracked shard directory.
    return catalog.CACHE_DIR / "chroma"


def have_chromadb() -> bool:
    try:
        import chromadb  # noqa: F401
        return True
    except ImportError:
        return False


def _client(paths: catalog.CatalogPaths):
    import chromadb
    from chromadb.config import Settings

    return chromadb.PersistentClient(
        path=str(_vector_dir(paths)),
        settings=Settings(anonymized_telemetry=False),
    )


def _collection(client, name: str):
    return client.get_or_create_collection(
        name=name, metadata={"hnsw:space": "cosine"})


def build_vectors(paths: catalog.CatalogPaths, model: str = DEFAULT_MODEL,
                  url: str = DEFAULT_OLLAMA_URL, batch: int = EMBED_BATCH,
                  collection_name: str = COLLECTION_NAME,
                  embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
                  client=None, verbose: bool = True) -> dict:
    """Embed every shard record into Chroma, skipping unchanged documents."""
    records = catalog.load_records(paths)
    if not records:
        raise RuntimeError("No catalog records. Run: hkdata.py catalog-sync --full")

    if embed_fn is None:
        def embed_fn(texts: List[str]) -> List[List[float]]:
            return embed_texts(texts, model=model, url=url)
    if client is None:
        client = _client(paths)
    collection = _collection(client, collection_name)

    existing = collection.get(include=["metadatas"])
    known: Dict[str, Dict] = {
        id_: (meta or {}) for id_, meta in zip(existing["ids"], existing["metadatas"])
    }

    pending: List[str] = []
    docs: Dict[str, str] = {}
    metas: Dict[str, Dict] = {}
    for name in sorted(records):
        document = build_document(records[name])
        if not document.strip():
            continue
        digest = text_hash(document)
        docs[name] = document
        metas[name] = build_metadata(records[name], model, digest)
        old = known.get(name)
        if old is None or old.get("text_hash") != digest or old.get("model") != model:
            pending.append(name)

    embedded = 0
    for start in range(0, len(pending), batch):
        chunk = pending[start:start + batch]
        vectors = embed_fn([docs[name] for name in chunk])
        collection.upsert(
            ids=chunk,
            embeddings=vectors,
            documents=[docs[name] for name in chunk],
            metadatas=[metas[name] for name in chunk],
        )
        embedded += len(chunk)
        if verbose:
            print(f"  embedded {embedded}/{len(pending)}", file=sys.stderr)

    stale = sorted(set(known) - set(docs))
    if stale:
        collection.delete(ids=stale)

    if verbose:
        print(f"Vectors: {collection.count()} total, {embedded} (re)embedded, "
              f"{len(stale)} removed", file=sys.stderr)
    return {"total": collection.count(), "embedded": embedded, "removed": len(stale)}


def vector_search(query: str, paths: catalog.CatalogPaths, top_n: int = 10,
                  model: str = DEFAULT_MODEL, url: str = DEFAULT_OLLAMA_URL,
                  collection_name: str = COLLECTION_NAME,
                  embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
                  client=None, verbose: bool = True,
                  query_instruction: str = QUERY_INSTRUCTION) -> List[dict]:
    """Semantic search over the vector store. Returns ranked result dicts."""
    if embed_fn is None:
        def embed_fn(texts: List[str]) -> List[List[float]]:
            return embed_texts(texts, model=model, url=url)
    if client is None:
        client = _client(paths)
    collection = _collection(client, collection_name)
    if collection.count() == 0:
        if verbose:
            print("Vector store is empty. Run: hkdata.py catalog-embed",
                  file=sys.stderr)
        return []

    query_vector = embed_fn([query_instruction + query])[0]
    result = collection.query(query_embeddings=[query_vector], n_results=top_n,
                              include=["metadatas", "documents", "distances"])
    items = []
    for meta, distance in zip(result["metadatas"][0], result["distances"][0]):
        items.append({
            "name": (meta or {}).get("name", ""),
            "title": (meta or {}).get("title_en") or (meta or {}).get("title_tc", ""),
            "org": (meta or {}).get("org_en") or (meta or {}).get("org_tc", ""),
            "distance": distance,
            "score": 1.0 - distance,
        })
    return items


def _rrf_rank(items: List[str], k: int = 60) -> Dict[str, float]:
    """Reciprocal Rank Fusion over a ranked list of names.

    Keeps the **first** (best) rank when a name repeats: the keyword pass appends
    a name once per matching token, so a dataset matching several tokens would
    otherwise have its best rank overwritten by a later, worse one.
    """
    scores: Dict[str, float] = {}
    for rank, name in enumerate(items):
        if name:
            scores.setdefault(name, 1.0 / (k + rank + 1))
    return scores


def _result_dicts(query_result) -> List[dict]:
    items = []
    for meta, distance in zip(query_result["metadatas"][0],
                              query_result["distances"][0]):
        meta = meta or {}
        items.append({
            "name": meta.get("name", ""),
            "title": meta.get("title_en") or meta.get("title_tc", ""),
            "org": meta.get("org_en") or meta.get("org_tc", ""),
            "distance": distance,
        })
    return items


def hybrid_search(query: str, paths: catalog.CatalogPaths, top_n: int = 10,
                  model: str = DEFAULT_MODEL, url: str = DEFAULT_OLLAMA_URL,
                  collection_name: str = COLLECTION_NAME,
                  embed_fn: Optional[Callable[[List[str]], List[List[float]]]] = None,
                  client=None, aliases: Optional[Dict[str, List[str]]] = None,
                  verbose: bool = True,
                  query_instruction: str = QUERY_INSTRUCTION) -> List[dict]:
    """ChromaDB retrieval: dense KNN fused (RRF) with a keyword-filtered pass.

    Chroma has no ranked BM25. The keyword pass therefore runs the *same dense
    query* restricted by a case-insensitive substring filter, so candidates are
    still semantically ranked, then RRF merges the two rankings. Falls back to
    dense-only when no token matches. Alias expansion maps abbreviations
    (e.g. 康文署) onto their official names (康樂及文化事務署).
    """
    if embed_fn is None:
        def embed_fn(texts: List[str]) -> List[List[float]]:
            return embed_texts(texts, model=model, url=url)
    if client is None:
        client = _client(paths)
    collection = _collection(client, collection_name)
    if collection.count() == 0:
        if verbose:
            print("Vector store is empty. Run: hkdata.py catalog-embed",
                  file=sys.stderr)
        return []

    expanded = expand_query(query, aliases)
    dense_text = query + ((" " + " ".join(expanded)) if expanded else "")
    fetch = max(top_n * 3, 20)
    query_vector = embed_fn([query_instruction + dense_text])[0]

    dense_res = collection.query(query_embeddings=[query_vector], n_results=fetch,
                                 include=["metadatas", "distances"])
    dense = _result_dicts(dense_res)
    by_name = {item["name"]: item for item in dense}

    # Keyword pass: run a densely-ranked, case-insensitive filtered query for
    # each distinctive token (query terms + CJK alias names), then fuse them.
    # Multi-word English aliases are left to the dense text (per-word tokens
    # like "Department" would be too generic).
    tokens = [t for t in re.findall(r"[A-Za-z0-9\u3400-\u4dbf\u4e00-\u9fff]+", query)
              if len(t) >= 2]
    for value in expanded:
        if value and not re.search(r"\s", value):
            tokens.append(value)
    tokens = sorted(dict.fromkeys(tokens), key=len, reverse=True)[:4]

    keyword_names: List[str] = []
    for token in tokens:
        try:
            kw_res = collection.query(
                query_embeddings=[query_vector], n_results=fetch,
                where_document={"$regex": f"(?i){re.escape(token)}"},
                include=["metadatas", "distances"])
        except Exception:
            continue
        for item in _result_dicts(kw_res):
            by_name.setdefault(item["name"], item)
            keyword_names.append(item["name"])

    scores = _rrf_rank([item["name"] for item in dense])
    for name, score in _rrf_rank(keyword_names).items():
        scores[name] = scores.get(name, 0.0) + score

    ranked = sorted(scores, key=lambda n: (-scores[n], by_name[n]["title"]))
    results = []
    for name in ranked[:top_n]:
        item = dict(by_name[name])
        item["score"] = scores[name]
        results.append(item)
    return results


def vector_status(paths: catalog.CatalogPaths,
                  collection_name: str = COLLECTION_NAME) -> dict:
    if not have_chromadb():
        return {"available": False}
    try:
        client = _client(paths)
        collection = _collection(client, collection_name)
        return {"available": True, "count": collection.count(),
                "path": str(_vector_dir(paths))}
    except Exception as exc:  # pragma: no cover - defensive
        return {"available": False, "error": str(exc)}


def embed_status(paths: catalog.CatalogPaths,
                 collection_name: str = COLLECTION_NAME,
                 embedder=None) -> dict:
    """Report the resolved embedding backend and whether the store matches it.

    The store's fingerprint is the ``model`` metadata on its vectors (set by
    ``build_vectors``); ``catalog-embed`` re-embeds whenever it differs, so a
    mismatch here means "rebuild with ``catalog-embed`` before trusting results".
    """
    if embedder is None:
        try:
            embedder = resolve_embedder()
        except ValueError as exc:
            return {"provider": "?", "model": "?", "error": str(exc)}
    info = {
        "provider": embedder.name,
        "model": embedder.model,
        "fingerprint": embedder.fingerprint,
        "available": False,
        "count": 0,
        "store_fingerprint": None,
        "match": False,
    }
    if not have_chromadb():
        return info
    try:
        client = _client(paths)
        collection = _collection(client, collection_name)
        info["available"] = True
        info["count"] = collection.count()
        existing = collection.get(limit=1, include=["metadatas"])
        if existing.get("metadatas") and existing["metadatas"][0]:
            info["store_fingerprint"] = existing["metadatas"][0].get("model") or ""
            info["match"] = info["store_fingerprint"] == embedder.fingerprint
    except Exception as exc:  # pragma: no cover - defensive
        info["error"] = str(exc)
    return info