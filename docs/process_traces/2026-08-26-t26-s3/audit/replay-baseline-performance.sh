#!/bin/sh
set -eu

source_repo=$(git rev-parse --show-toplevel)
test "$(git -C "$source_repo" rev-parse HEAD)" = 2fd7c920314333535ea2631bec887a19b964f834
audit_tmp=$(mktemp -d /private/tmp/jw-audit-baseline.XXXXXX)
trap 'rm -rf -- "$audit_tmp"' EXIT HUP INT TERM

git clone -q --shared "$source_repo" "$audit_tmp/repository"
cd "$audit_tmp/repository"
/usr/bin/time -p /Users/edr/code/JouleWise/.venv/bin/python -B \
  scripts/verify_receipt_histsem.py --repository-root . >/dev/null
