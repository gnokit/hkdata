"""Command-line interface for hkdata."""

import argparse
import json
import sys
import urllib.error
import urllib.request
from typing import List

from . import __version__
from .common import USER_AGENT
from .inspect import info, info_multiple
from .index import build_index, save_index, search_local
from .logs import load_jsonl, log_search, migrate, render
from .normalize import expand_synonyms
from .parse import parse_data
from .search import search_multiple


def _eprint(message: str) -> None:
    print(message, file=sys.stderr)


def cmd_search(args: argparse.Namespace) -> int:
    keywords = list(args.keywords)
    if args.synonyms and len(keywords) == 1:
        keywords = expand_synonyms(keywords[0])

    if not keywords:
        _eprint("Error: at least one keyword is required.")
        return 1

    _eprint(f"Searching data.gov.hk for: {', '.join(keywords)} (page {args.page})")

    results = search_multiple(
        keywords,
        page=args.page,
        rows=args.rows,
        parallel=args.parallel,
    )

    seen_ids = set()
    total_matches = 0
    multi_source = len(keywords) > 1

    for keyword, result in results:
        if result.get("error"):
            _eprint(f"Error for '{keyword}': {result['error']}")
            continue

        count = result.get("count", 0)
        total_matches = max(total_matches, count)
        datasets = result.get("datasets", [])

        if not datasets:
            if multi_source:
                print(f"{keyword} | (0 results)")
            continue

        for ds in datasets:
            if ds["id"] in seen_ids:
                continue
            seen_ids.add(ds["id"])
            if multi_source:
                print(f"{keyword} | {ds['id']} | {ds['title']} | {ds['notes']}")
            else:
                print(f"{ds['id']} | {ds['title']} | {ds['notes']}")

    if not multi_source:
        start = (args.page - 1) * args.rows + 1
        end = start + len(seen_ids) - 1
        if total_matches > 0:
            total_pages = (total_matches + args.rows - 1) // args.rows
            print(f"\nShowing results {start}-{end} of {total_matches} (page {args.page} of {total_pages})")
            if args.page < total_pages:
                print(f"Use --page {args.page + 1} to see more results")
            if args.page > 1:
                print(f"Use --page {args.page - 1} to see previous results")
        else:
            print("No matching datasets found.")

    return 0


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
        print("No matching log entries.")
        return 0
    for record in results:
        print(json.dumps(record, ensure_ascii=False, indent=2))
    return 0


def cmd_log_render(args: argparse.Namespace) -> int:
    render()
    _eprint("Rendered logs/failure-log.md and logs/strategy-registry.md from JSONL.")
    return 0


def cmd_migrate_logs(args: argparse.Namespace) -> int:
    migrate()
    _eprint("Migrated logs/failure-log.md and logs/strategy-registry.md to JSONL.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="hkdata",
        description="Query and discover Hong Kong data.gov.hk datasets.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Search data.gov.hk")
    search_parser.add_argument("keywords", nargs="+", help="One or more search keywords")
    search_parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    search_parser.add_argument("--rows", type=int, default=50, help="Results per page (default: 50)")
    search_parser.add_argument("--parallel", action="store_true", default=True, help="Run searches in parallel (default)")
    search_parser.add_argument("--sequential", action="store_true", help="Run searches sequentially")
    search_parser.add_argument("--synonyms", action="store_true", help="Expand keyword to known synonyms")
    search_parser.set_defaults(func=cmd_search)

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

    log_search_parser = subparsers.add_parser("log-search", help="Search failure/strategy logs")
    log_search_parser.add_argument("keywords", nargs="+", help="Keywords to search")
    log_search_parser.add_argument(
        "--names",
        nargs="+",
        help="Log files to search (default: failure-log strategy-registry)",
    )
    log_search_parser.set_defaults(func=cmd_log_search)

    log_render_parser = subparsers.add_parser("log-render", help="Regenerate markdown logs from JSONL")
    log_render_parser.set_defaults(func=cmd_log_render)

    migrate_parser = subparsers.add_parser("migrate-logs", help="One-off migration from markdown logs to JSONL")
    migrate_parser.set_defaults(func=cmd_migrate_logs)

    return parser


def main(argv: List[str] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # Handle --sequential overriding --parallel default.
    if hasattr(args, "sequential") and args.sequential:
        args.parallel = False

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
