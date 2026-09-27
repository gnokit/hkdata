"""Command-line interface for hkdata."""

import argparse
import json
import sys
import time
import urllib.error
import urllib.request
from typing import List

from . import __version__
from . import catalog
from . import experience
from . import vectors
from .common import USER_AGENT
from .inspect import info, info_multiple
from .index import build_index, save_index, search_local
from .logs import log_search, render
from .parse import parse_data


def _eprint(message: str) -> None:
    print(message, file=sys.stderr)


def _require_chromadb() -> bool:
    if vectors.have_chromadb():
        return True
    _eprint("ChromaDB is not installed. Run vector commands with the venv, e.g.:")
    _eprint("  .venv/bin/python ./scripts/hkdata.py catalog-embed")
    _eprint("  .venv/bin/python ./scripts/hkdata.py catalog-search \"<query>\"")
    return False


def cmd_info(args: argparse.Namespace) -> int:
    ids = list(args.dataset_ids)
    if not ids:
        _eprint("Error: at least one dataset ID is required.")
        return 1

    if len(ids) == 1:
        try:
            data = info(ids[0])
        except RuntimeError as exc:
            _eprint(f"Error: {exc}")
            return 1
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    results = info_multiple(ids)
    output = []
    for dsid, result in zip(ids, results):
        if result.get("error"):
            _eprint(f"Error for '{dsid}': {result['error']}")
        output.append(result["data"])
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


def cmd_test(args: argparse.Namespace) -> int:
    urls = list(args.urls)
    if not urls:
        _eprint("Error: at least one URL is required.")
        return 1

    exit_code = 0
    for url in urls:
        _eprint(f"Testing endpoint: {url}")
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": USER_AGENT},
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read()
                content_type = response.headers.get("Content-Type", "")
        except urllib.error.URLError as exc:
            _eprint(f"Error fetching {url}: {exc.reason}")
            exit_code = 1
            continue

        summary = parse_data(data, content_type=content_type, url=url)
        summary["url"] = url
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    return exit_code


def cmd_reindex(args: argparse.Namespace) -> int:
    index = build_index()
    save_index(index)
    _eprint(f"Rebuilt references/search-index.json with {index['count']} datasets.")
    return 0


def cmd_search_local(args: argparse.Namespace) -> int:
    query = " ".join(args.keywords)
    results = search_local(query, top_n=args.top_n)
    if not results:
        print("No matching verified datasets found.")
        return 0
    for rtype, score, record in results:
        if rtype == "dataset":
            print(
                f"{score:.2f} | {record['id']} | {record['title']} | "
                f"{record['category']} | {record['filename']}"
            )
        else:
            print(
                f"{score:.2f} | [{rtype}] {record['title']} | "
                f"{record['description'][:120]}..."
            )
    return 0


def cmd_log_search(args: argparse.Namespace) -> int:
    names = list(args.names) if args.names else ["failure-log", "strategy-registry"]
    keywords = list(args.keywords)
    results = log_search(names, keywords)
    if not results:
        print("No matching experiences.")
        return 0
    for record in results:
        print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


def cmd_log_render(args: argparse.Namespace) -> int:
    render()
    _eprint("Rendered logs/failure-log.md and logs/strategy-registry.md from experiences.")
    return 0


# ---------------------------------------------------------------------------
# Catalog (offline discovery) commands
# ---------------------------------------------------------------------------


def cmd_catalog_sync(args: argparse.Namespace) -> int:
    paths = catalog.default_paths()
    try:
        langs = catalog.parse_langs(args.lang)
    except ValueError as exc:
        _eprint(f"Error: {exc}")
        return 1
    if args.refresh:
        result = catalog.sync_refresh(paths, rate=args.rate, langs=langs)
        if result["new"]:
            _eprint(f"New datasets added to seed: {', '.join(result['new'])}")
        return 0
    if not args.full:
        catalog.sync_seed(paths)
        return 0

    catalog.sync_seed(paths)
    result = catalog.sync_full(paths, rate=args.rate, limit=args.limit, langs=langs)
    if result["failed"]:
        _eprint(f"Failed ids ({len(result['failed'])}): "
                f"{', '.join(result['failed'][:10])}")
    return 0


def cmd_catalog_embed(args: argparse.Namespace) -> int:
    if not _require_chromadb():
        return 1
    paths = catalog.default_paths()
    try:
        result = vectors.build_vectors(
            paths, model=args.model, url=args.url, batch=args.batch)
    except RuntimeError as exc:
        _eprint(f"Error: {exc}")
        return 1
    _eprint(f"Vector store ready: {result['total']} datasets.")
    return 0


def cmd_catalog_search(args: argparse.Namespace) -> int:
    if not _require_chromadb():
        return 1
    paths = catalog.default_paths()
    query = " ".join(args.keywords)
    try:
        results = vectors.hybrid_search(query, paths, top_n=args.top_n,
                                        model=args.model, url=args.url)
    except RuntimeError as exc:
        _eprint(f"Error: {exc}")
        return 1
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    if not results:
        print(f"No catalog matches for: {query}")
        return 0
    for item in results:
        org = item.get("org") or "-"
        print(f"{item['score']:.4f} | {item['name']} | {item['title']} | {org}")
    return 0


def cmd_experience_search(args: argparse.Namespace) -> int:
    if not _require_chromadb():
        return 1
    query = " ".join(args.keywords)
    try:
        results = experience.search(query, top_n=args.top_n, kind=args.kind)
    except RuntimeError as exc:
        _eprint(f"Error: {exc}")
        return 1
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0
    if not results:
        print(f"No experience matches for: {query}")
        return 0
    for item in results:
        datasets = ", ".join(item["datasets"]) or "-"
        print(f"{item['score']:.4f} | [{item['kind']}] {item['topic']} | "
              f"{datasets} | {item['date'] or '-'} | {item['source']}")
    return 0


def cmd_experience_log(args: argparse.Namespace) -> int:
    exp = {
        "kind": args.kind,
        "topic": args.topic,
        "query_patterns": args.pattern or [],
        "category": args.category or "",
        "datasets": args.dataset or [],
        "method": args.method or "",
        "endpoint": args.endpoint or "",
        "outcome": args.outcome or "",
        "caveats": args.caveat or [],
        "source": args.source or "manual",
        "date": args.date,
        "last_verified": args.date,
    }
    upsert = vectors.have_chromadb()
    try:
        record = experience.append_experience(exp, upsert=upsert)
    except RuntimeError as exc:
        _eprint(f"Error: {exc}")
        return 1
    if not upsert:
        _eprint("ChromaDB not installed — appended to JSONL only; "
                "run 'experience-embed' later.")
    print(record["id"])
    return 0


def cmd_experience_embed(args: argparse.Namespace) -> int:
    if not _require_chromadb():
        return 1
    try:
        result = experience.embed_experiences(
            model=args.model, url=args.url, batch=args.batch)
    except RuntimeError as exc:
        _eprint(f"Error: {exc}")
        return 1
    _eprint(f"Experience store ready: {result['total']} cards.")
    return 0


def cmd_experience_migrate(args: argparse.Namespace) -> int:
    result = experience.migrate()
    _eprint(f"Experiences: {result['positive']} positive, "
            f"{result['negative']} negative.")
    return 0


def cmd_catalog_status(args: argparse.Namespace) -> int:
    paths = catalog.default_paths()
    data = catalog.status(paths)
    vec = vectors.vector_status(paths)
    data["vectors"] = vec
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    print(f"Seed ids:      {data['seed_count']}")
    print(f"Fetched:       {data['fetched_count']}")
    print(f"Missing:       {data['missing_count']}")
    print(f"Locales:       {', '.join(data['langs']) or '-'}")
    print(f"Shards:        {data['shards']} ({data['shard_bytes'] / 1e6:.1f} MB)")
    if vec.get("available"):
        print(f"Vector store:  {vec.get('count', 0)} datasets")
        print(f"Experiences:   {experience.count(paths)} cards")
    else:
        print("Vector store:  unavailable (install chromadb in the venv)")
    print(f"Last full sync: {data['last_full_sync'] or '-'}")
    print(f"Last activity:  {data['fetched_at'] or '-'}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hkdata",
        description="Query and discover Hong Kong data.gov.hk datasets.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    info_parser = subparsers.add_parser("info", help="Show dataset metadata")
    info_parser.add_argument("dataset_ids", nargs="+", help="One or more dataset IDs")
    info_parser.set_defaults(func=cmd_info)

    test_parser = subparsers.add_parser("test", help="Test a dataset endpoint")
    test_parser.add_argument("urls", nargs="+", help="One or more endpoint URLs")
    test_parser.set_defaults(func=cmd_test)

    reindex_parser = subparsers.add_parser("reindex", help="Rebuild local search index")
    reindex_parser.set_defaults(func=cmd_reindex)

    search_local_parser = subparsers.add_parser("search-local", help="Search verified dataset index")
    search_local_parser.add_argument("keywords", nargs="+", help="Natural-language query")
    search_local_parser.add_argument("--top-n", type=int, default=10, help="Max results (default: 10)")
    search_local_parser.set_defaults(func=cmd_search_local)

    log_search_parser = subparsers.add_parser(
        "log-search", help="Lexical search of experiences (by kind)")
    log_search_parser.add_argument("keywords", nargs="+", help="Keywords to search")
    log_search_parser.add_argument(
        "--names",
        nargs="+",
        help="Log files to search (default: failure-log strategy-registry)",
    )
    log_search_parser.set_defaults(func=cmd_log_search)

    log_render_parser = subparsers.add_parser(
        "log-render", help="Regenerate the logs/ markdown views from experiences")
    log_render_parser.set_defaults(func=cmd_log_render)

    catalog_sync_parser = subparsers.add_parser(
        "catalog-sync", help="Seed/crawl the offline catalog (package_list + package_show)")
    catalog_sync_parser.add_argument("--full", action="store_true",
                                     help="Crawl every missing dataset (long, resumable)")
    catalog_sync_parser.add_argument("--refresh", action="store_true",
                                     help="Re-fetch datasets from the 14-day RSS feed")
    catalog_sync_parser.add_argument("--rate", type=float, default=catalog.DEFAULT_RATE,
                                     help=f"Requests per second (default: {catalog.DEFAULT_RATE})")
    catalog_sync_parser.add_argument("--limit", type=int, default=None,
                                     help="Max datasets to fetch in this run")
    catalog_sync_parser.add_argument("--lang", default="en",
                                     help="Comma-separated locales to fetch, e.g. en,tc,sc (default: en)")
    catalog_sync_parser.set_defaults(func=cmd_catalog_sync)

    catalog_embed_parser = subparsers.add_parser(
        "catalog-embed", help="Build the ChromaDB vector store (local Ollama embeddings)")
    catalog_embed_parser.add_argument("--model", default=vectors.DEFAULT_MODEL,
                                      help=f"Ollama embedding model (default: {vectors.DEFAULT_MODEL})")
    catalog_embed_parser.add_argument("--url", default=vectors.DEFAULT_OLLAMA_URL,
                                      help="Ollama embed endpoint")
    catalog_embed_parser.add_argument("--batch", type=int, default=vectors.EMBED_BATCH,
                                      help=f"Embedding batch size (default: {vectors.EMBED_BATCH})")
    catalog_embed_parser.set_defaults(func=cmd_catalog_embed)

    catalog_search_parser = subparsers.add_parser(
        "catalog-search", help="Search the offline catalog (ChromaDB: dense + keyword)")
    catalog_search_parser.add_argument("keywords", nargs="+", help="Natural-language query")
    catalog_search_parser.add_argument("--top-n", type=int, default=10,
                                       help="Max results (default: 10)")
    catalog_search_parser.add_argument("--model", default=vectors.DEFAULT_MODEL,
                                       help=f"Ollama embedding model (default: {vectors.DEFAULT_MODEL})")
    catalog_search_parser.add_argument("--url", default=vectors.DEFAULT_OLLAMA_URL,
                                       help="Ollama embed endpoint")
    catalog_search_parser.add_argument("--json", action="store_true", help="JSON output")
    catalog_search_parser.set_defaults(func=cmd_catalog_search)

    catalog_status_parser = subparsers.add_parser(
        "catalog-status", help="Show offline catalog coverage")
    catalog_status_parser.add_argument("--json", action="store_true", help="JSON output")
    catalog_status_parser.set_defaults(func=cmd_catalog_status)

    exp_search = subparsers.add_parser(
        "experience-search", help="Semantic search over past experiences (positive/negative)")
    exp_search.add_argument("keywords", nargs="+", help="Natural-language query")
    exp_search.add_argument("--top-n", type=int, default=5, help="Max results (default: 5)")
    exp_search.add_argument("--kind", choices=["positive", "negative"],
                            help="Only return this kind of experience")
    exp_search.add_argument("--json", action="store_true", help="JSON output")
    exp_search.set_defaults(func=cmd_experience_search)

    exp_log = subparsers.add_parser(
        "experience-log", help="Record a new experience and index it")
    exp_log.add_argument("--kind", choices=["positive", "negative"], default="positive")
    exp_log.add_argument("--topic", required=True, help="Short description")
    exp_log.add_argument("--pattern", action="append", help="Example query (repeatable)")
    exp_log.add_argument("--category", help="Category / component")
    exp_log.add_argument("--dataset", action="append", help="Dataset ID (repeatable)")
    exp_log.add_argument("--method", help="What worked (or the dead end)")
    exp_log.add_argument("--endpoint", help="Endpoint URL")
    exp_log.add_argument("--outcome", help="Short verdict, e.g. located / unavailable")
    exp_log.add_argument("--caveat", action="append", help="Caveat (repeatable)")
    exp_log.add_argument("--source", help="Where this came from (default: manual)")
    exp_log.add_argument("--date", default=time.strftime("%Y-%m-%d"), help="Date (YYYY-MM-DD)")
    exp_log.set_defaults(func=cmd_experience_log)

    exp_embed = subparsers.add_parser(
        "experience-embed", help="Build the ChromaDB experience index")
    exp_embed.add_argument("--model", default=vectors.DEFAULT_MODEL)
    exp_embed.add_argument("--url", default=vectors.DEFAULT_OLLAMA_URL)
    exp_embed.add_argument("--batch", type=int, default=vectors.EMBED_BATCH)
    exp_embed.set_defaults(func=cmd_experience_embed)

    exp_migrate = subparsers.add_parser(
        "experience-migrate", help="Seed experiences.jsonl from references and logs")
    exp_migrate.set_defaults(func=cmd_experience_migrate)

    return parser


def main(argv: List[str] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
