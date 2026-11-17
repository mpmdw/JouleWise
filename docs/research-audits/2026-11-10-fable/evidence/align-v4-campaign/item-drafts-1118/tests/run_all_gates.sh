#!/bin/bash
set -eu
set -o pipefail
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
SCRATCH_DIR=$(mktemp -d "$PWD/.synthetic-XXXXXX")
trap 'rm -rf "$SCRATCH_DIR"' EXIT
LOG_DIR=${JW_DRAFT_EVIDENCE_DIR:-$PWD/evidence/round10}
mkdir -p "$LOG_DIR"
python3 -B tools/lint.py > "$LOG_DIR/lint.log" 2>&1
python3 -B ../item-drafts-1115/tests/test_close_selection.py "$PWD" > "$LOG_DIR/close-selection.log" 2>&1
python3 -B tests/verify_kit.py "$SCRATCH_DIR/mock" > "$LOG_DIR/pinned-checks.log" 2>&1
python3 -B tests/test_qual_gates.py "$SCRATCH_DIR" > "$LOG_DIR/gates.log" 2>&1
python3 -B tests/test_standing.py > "$LOG_DIR/standing-f0-tests.log" 2>&1
python3 -B tests/test_round10.py > "$LOG_DIR/round10-tests.log" 2>&1
python3 -B tests/test_redate.py > "$LOG_DIR/redate-tests.log" 2>&1
for log in lint close-selection pinned-checks gates standing-f0-tests round10-tests redate-tests; do tail -1 "$LOG_DIR/$log.log"; done
