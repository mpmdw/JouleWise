#!/bin/bash
set -eu
set -o pipefail
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
date -u '+Verification started %Y-%m-%dT%H:%M:%SZ'
python3 -B tests/lint.py
python3 -B f2-inst-02/tests/test_gates.py
python3 -B f2-inst-03/tests/test_gates.py
python3 -B tests/test_close_selection.py f2-inst-02
python3 -B tests/test_close_selection.py f2-inst-03
python3 -B tests/test_hp_gates.py
python3 -B tests/verify_build.py "$1" "$2"
python3 -B tests/test_staging.py "${3:-$1}"
date -u '+Verification finished %Y-%m-%dT%H:%M:%SZ'
