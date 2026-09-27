#!/bin/bash
# Backward-compatible wrapper for `info`. Delegates to the single hk.sh entry point.
exec bash "$(dirname "$0")/../hk.sh" info "$@"
