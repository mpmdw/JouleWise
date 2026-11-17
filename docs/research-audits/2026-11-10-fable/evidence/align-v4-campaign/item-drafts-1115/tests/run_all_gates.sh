#!/bin/bash
set -eu
set -o pipefail
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
python3 -B tests/run_suite.py "$@"
