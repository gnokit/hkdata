#!/bin/bash
exec python3 "$(dirname "$0")/hkdata.py" info "$@"
