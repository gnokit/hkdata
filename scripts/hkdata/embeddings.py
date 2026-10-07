"""Pluggable embedding backends.

The search layer embeds text locally via Ollama by default, but any embedding
service can be plugged in. A backend is anything that satisfies the
:class:`Embedder` interface (an ``embed`` method plus a few attributes), and it
gets wired up in one of two ways:

  1. **Register it** with :func:`register_embedder`, or
  2. **Point at it** with ``HKDATA_EMBED_PROVIDER=pkg.module:ClassName`` (a
     dotted import path) — no code changes to this repo needed.

The rest of the toolkit (catalog build, search, experience index) only ever talks
to the :class:`Embedder` interface, never to a concrete provider, so new backends
drop in without touching ``vectors.py`` / ``experience.py`` / ``cli.py``.

A minimal backend::

    from hkdata.embeddings import Embedder, register_embedder

    class MyVendor(Embedder):
        name = "myvendor"           # used in the fingerprint
        query_instruction = ""      # "" if the model takes plain queries

        def __init__(self, model=None, url=None, api_key=""):
            self.model = model or "myvendor-default-model"
            self.url = url or "https://api.myvendor.example/v1/embeddings"
            self.api_key = api_key or ""

        def embed(self, texts):
            # POST to self.url, return one vector per text.
            ...

    register_embedder("myvendor", MyVendor)   # now --provider myvendor works

Environment variables (all optional; defaults keep the existing Ollama setup)::

    HKDATA_EMBED_PROVIDER   provider name or "pkg.module:ClassName" (default "ollama")
    HKDATA_EMBED_MODEL      model name (overrides the backend's default)
    HKDATA_EMBED_URL        endpoint URL (overrides the backend's default)
    HKDATA_EMBED_API_KEY    bearer key (passed to the backend)
"""

import importlib
import json
import os
import time
import urllib.error
import urllib.request
from typing import Callable, Dict, List, Optional

from .common import USER_AGENT

EMBED_BATCH = 32
EMBED_TIMEOUT = 120

# Qwen3-Embedding is trained with an instruction prefix on the query side only.
QWEN_QUERY_INSTRUCTION = (
    "Instruct: Given a search query, retrieve relevant Hong Kong dataset metadata\n"
    "Query: "
)

DEFAULT_MODEL = "qwen3-embedding:0.6b"
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/embed"
DEFAULT_OPENAI_MODEL = "text-embedding-3-small"
DEFAULT_OPENAI_URL = "https://api.openai.com/v1/embeddings"


class Embedder:
    """Interface every embedding backend implements.

    Attributes:
        ``name``               short backend id (part of the fingerprint)
        ``model``              model identifier (part of the fingerprint)
        ``query_instruction``  prefix applied to **queries only**; ``""`` when
                               the model takes plain queries (documents are
                               always embedded raw)

    Methods:
        ``embed(texts)`` -> one vector per text. The only required method.

    ``fingerprint`` identifies the embedding space (``name:model``). It is stored
    on every vector, so switching backend/model is detected and triggers a full
    re-embed instead of silently mixing incompatible spaces.
    """

    name = ""
    model = ""
    query_instruction = ""

    def embed(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError

    @property
    def fingerprint(self) -> str:
        # Ollama stays unprefixed for backward compatibility with stores built
        # before embeddings became pluggable (they stored the bare model name).
        if self.name == "ollama":
            return self.model
        return f"{self.name}:{self.model}"

    def embed_query(self, query: str) -> List[float]:
        return self.embed([self.query_instruction + query])[0]


# ---------------------------------------------------------------------------
# Built-in backends
# ---------------------------------------------------------------------------


class OllamaEmbedder(Embedder):
    name = "ollama"
    query_instruction = QWEN_QUERY_INSTRUCTION

    def __init__(self, model: Optional[str] = None,
                 url: Optional[str] = None, api_key: str = ""):
        self.model = model or DEFAULT_MODEL
        self.url = url or DEFAULT_OLLAMA_URL

    def embed(self, texts: List[str]) -> List[List[float]]:
        return _ollama_embed(texts, self.model, self.url)


class OpenAICompatEmbedder(Embedder):
    name = "openai"
    query_instruction = ""

    def __init__(self, model: Optional[str] = None,
                 url: Optional[str] = None, api_key: str = ""):
        self.model = model or DEFAULT_OPENAI_MODEL
        self.url = url or DEFAULT_OPENAI_URL
        self.api_key = api_key or ""

    def embed(self, texts: List[str]) -> List[List[float]]:
        return _openai_embed(texts, self.model, self.url, self.api_key)


# ---------------------------------------------------------------------------
# Provider registry (the open extension point)
# ---------------------------------------------------------------------------

#: name -> factory(model, url, api_key) -> Embedder
_REGISTRY: Dict[str, Callable] = {}


def register_embedder(name: str, factory: Callable) -> Callable:
    """Register an embedding backend factory under ``name``.

    ``factory`` is called as ``factory(model, url, api_key)`` and must return an
    :class:`Embedder`. The built-in backends are registered this way; register
    your own the same way, or skip registration and point
    ``HKDATA_EMBED_PROVIDER`` at a dotted import path instead.
    """
    _REGISTRY[name.lower().strip()] = factory
    return factory


def registered_providers() -> List[str]:
    return sorted(_REGISTRY)


register_embedder("ollama", OllamaEmbedder)
register_embedder("openai", OpenAICompatEmbedder)
register_embedder("openai-compatible", OpenAICompatEmbedder)


def _import_dotted(path: str) -> Callable:
    """Import ``pkg.module:ClassName`` (or ``pkg.module.ClassName``)."""
    if ":" in path:
        module_name, _, attr = path.partition(":")
    else:
        module_name, _, attr = path.rpartition(".")
    if not module_name or not attr:
        raise ValueError(f"Invalid provider path: {path!r}")
    module = importlib.import_module(module_name)
    return getattr(module, attr)


def resolve_embedder(provider: Optional[str] = None,
                     model: Optional[str] = None,
                     url: Optional[str] = None,
                     api_key: Optional[str] = None) -> Embedder:
    """Resolve an embedding backend from args/env, defaulting to local Ollama.

    Precedence for each value: explicit argument > environment variable >
    backend default. ``provider`` may be a registered name or a dotted import
    path ``pkg.module:ClassName``.
    """
    provider = (provider or os.environ.get("HKDATA_EMBED_PROVIDER")
                or "ollama").strip()
    model = model or os.environ.get("HKDATA_EMBED_MODEL") or None
    url = url or os.environ.get("HKDATA_EMBED_URL") or None
    api_key = api_key or os.environ.get("HKDATA_EMBED_API_KEY") or None

    factory = _REGISTRY.get(provider.lower())
    if factory is None and (":" in provider or "." in provider):
        factory = _import_dotted(provider)
    if factory is None:
        raise ValueError(
            f"Unknown embedding provider: {provider!r}. Registered: "
            f"{', '.join(registered_providers())}. Set HKDATA_EMBED_PROVIDER to "
            f"a registered name or a dotted path 'pkg.module:ClassName'.")
    return factory(model, url, api_key)


# ---------------------------------------------------------------------------
# HTTP backends (used by the built-in classes)
# ---------------------------------------------------------------------------


def _ollama_embed(texts: List[str], model: str, url: str) -> List[List[float]]:
    """Embed a batch of texts via the Ollama HTTP API."""
    payload = json.dumps({"model": model, "input": texts}).encode("utf-8")
    request = urllib.request.Request(
        url, data=payload,
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT})
    last_error: Optional[Exception] = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=EMBED_TIMEOUT) as response:
                body = json.loads(response.read().decode("utf-8"))
            embeddings = body.get("embeddings")
            if not embeddings:
                raise RuntimeError("Ollama returned no embeddings")
            return embeddings
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError,
                RuntimeError) as exc:
            last_error = exc
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Ollama embedding failed: {last_error}")


def _openai_embed(texts: List[str], model: str, url: str,
                  api_key: str) -> List[List[float]]:
    """Embed a batch via an OpenAI-compatible ``/v1/embeddings`` endpoint."""
    payload = json.dumps({"model": model, "input": texts}).encode("utf-8")
    headers = {"Content-Type": "application/json", "User-Agent": USER_AGENT}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, data=payload, headers=headers)
    last_error: Optional[Exception] = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=EMBED_TIMEOUT) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError,
                json.JSONDecodeError) as exc:
            last_error = exc
            time.sleep(2 ** attempt)
            continue
        data = body.get("data") if isinstance(body, dict) else None
        if not data:
            raise RuntimeError("Embedding API returned no 'data' array")
        data = sorted(data, key=lambda d: d.get("index", 0))
        return [d.get("embedding") for d in data]
    raise RuntimeError(f"Embedding API failed: {last_error}")


def ollama_available(url: str = DEFAULT_OLLAMA_URL) -> bool:
    try:
        _ollama_embed(["ping"], DEFAULT_MODEL, url)
        return True
    except Exception:
        return False
