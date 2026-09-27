#!/bin/bash
# Single entry point for the hkdata CLI.
# Usage: bash ./hk.sh <subcommand> [args...]
# Picks the venv interpreter when it exists (chromadb lives there), else python3.
set -eo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$ROOT/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"
exec "$PY" "$ROOT/scripts/hkdata.py" "$@"
