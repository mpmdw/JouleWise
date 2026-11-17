#!/bin/bash
set -eu
set -o pipefail
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
date -u '+Verification started %Y-%m-%dT%H:%M:%SZ'
python3 -B tests/test_rl173_gates.py
python3 -B ../item-drafts-1115/tests/test_close_selection.py "$PWD"
if [ "$#" -gt 0 ]; then
  python3 -B tests/verify_kit.py "$1"
  python3 -B tests/test_staging.py "${2:-$1}"
fi
