#!/bin/bash
set -eu
set -o pipefail
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
SCRATCH_DIR=$(mktemp -d "$PWD/.synthetic-XXXXXX")
trap 'rm -rf "$SCRATCH_DIR"' EXIT
python3 -B tools/lint.py > evidence/lint.log 2>&1
python3 -B tests/verify_kit.py "$SCRATCH_DIR/mock" > evidence/pinned-checks.log 2>&1
python3 -B tests/test_qual_gates.py "$SCRATCH_DIR" > evidence/gates.log 2>&1
python3 -B tests/test_standing.py > evidence/standing-f0-tests.log 2>&1
python3 -B tests/test_redate.py > evidence/redate-tests.log 2>&1
for log in lint pinned-checks gates standing-f0-tests redate-tests; do tail -1 "evidence/$log.log"; done
