#!/usr/bin/env bash
# public-preflight.sh — refuse to push private knowledge, secrets, or personal data
# to a public remote.
#
# Manual use:  bash scripts/public-preflight.sh
# Hook use:    .githooks/pre-push calls it; refs being pushed arrive on stdin as
#              "<local ref> <local sha> <remote ref> <remote sha>" (git's pre-push format).
#
# Exit 1 blocks the push. Bypass with `git push --no-verify` — GitHub-side push
# protection is the layer that cannot be bypassed.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
FAIL=0
bad() { FAIL=1; printf '  \033[31m✗\033[0m %s\n' "$*"; }
ok()  { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }

# ---------------------------------------------------------------------------
# Policy: which paths are private knowledge (never pushed) and which .md files
# are method docs (always pushed). Keep in sync with .gitignore.
PRIVATE_RE='^(data/experiences\.jsonl$|logs/|references/index\.md$|references/search-index\.json$|references/[^/]+\.md$)'
KEEP_RE='^references/(template|category-mapping|workflow-guides)\.md$'
SECRET_RE='(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY)'
PERSONAL_RE='(/Users/[A-Za-z0-9._-]+|[A-Z]{1,2}[0-9]{6}\([0-9A]\)|\+852[ -]?[0-9]{4}[ -]?[0-9]{4})'
EMAIL_RE='[A-Za-z0-9._%+-]+@(gmail|googlemail|hotmail|outlook|icloud|yahoo|qq|163|126)\.[A-Za-z]{2,}'
BIG=$((5 * 1024 * 1024))
# ---------------------------------------------------------------------------

printf 'public-preflight: %s%s%s\n' "$ROOT" "${1:+ (remote=$1)}" "${2:+ (url=$2)}"

# [1] scope — nothing private may be tracked
echo "[1] tracked-file scope"
offenders="$(git ls-files | grep -E "$PRIVATE_RE" | grep -vE "$KEEP_RE" || true)"
if [ -n "$offenders" ]; then
  bad "private knowledge is tracked (someone ran 'git add -f'?):"
  printf '      %s\n' $offenders
else
  ok "only engine files are tracked"
fi

# [2] incoming commits — the refs git is about to send (hook mode only)
echo "[2] incoming commits"
incoming=""
if [ ! -t 0 ]; then
  while read -r _lref lsha _rref rsha; do
    case "$lsha" in 0000000*|"") continue ;; esac
    base="$rsha"
    case "$rsha" in 0000000*|"") base="$(git hash-object -t tree /dev/null)" ;; esac
    incoming="${incoming}$(git diff --name-only "$base" "$lsha" 2>/dev/null || true)"$'\n'
  done
fi
if [ -z "$incoming" ]; then
  ok "no refs on stdin (manual run) — checked the tracked tree instead"
else
  off="$(printf '%s' "$incoming" | sed '/^$/d' | grep -E "$PRIVATE_RE" | grep -vE "$KEEP_RE" || true)"
  if [ -n "$off" ]; then
    bad "this push would ADD/CHANGE private files:"
    printf '      %s\n' $off
  else
    ok "no private paths in the incoming commits"
  fi
fi

# [3] secrets anywhere in the tracked tree
echo "[3] credential patterns"
if hits="$(git grep -InE "$SECRET_RE" -- . 2>/dev/null)" && [ -n "$hits" ]; then
  bad "possible credential:"
  printf '%s\n' "$hits" | head -10 | sed 's/^/      /'
else
  ok "no credential patterns"
fi

# [4] personal data
echo "[4] personal-data patterns"
if hits="$(git grep -InE "$PERSONAL_RE" -- . 2>/dev/null)" && [ -n "$hits" ]; then
  bad "possible personal data (path / HKID / +852 phone):"
  printf '%s\n' "$hits" | head -10 | sed 's/^/      /'
else
  ok "no local paths, HKIDs or mobile numbers"
fi
if hits="$(git grep -InE "$EMAIL_RE" -- . 2>/dev/null)" && [ -n "$hits" ]; then
  bad "personal email domain in tracked files:"
  printf '%s\n' "$hits" | head -10 | sed 's/^/      /'
else
  ok "no personal email domains (.gov.hk addresses are fine)"
fi

# [5] bulk warning
echo "[5] bulk"
big="$(git ls-tree -r -l HEAD 2>/dev/null | awk -v lim="$BIG" '$4 > lim {printf "      %s (%.1f MB)\n", $5, $4/1048576}')"
if [ -n "$big" ]; then
  warn "tracked files over 5 MB:"
  printf '%s\n' "$big"
else
  ok "no tracked file over 5 MB"
fi

echo
if [ "$FAIL" -eq 0 ]; then
  echo "public-preflight: PASS"
else
  echo "public-preflight: FAIL — push blocked. Fix above, or \`git push --no-verify\` to bypass."
fi
exit "$FAIL"
