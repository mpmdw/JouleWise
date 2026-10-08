#!/bin/zsh
# Desk check before an arm: run the arm's own identity collectors in the measurement clone, but compare
# with the sealed commit H_claim instead of with the plan's measurement_head.
#
# Why: at the arm the driver passes the plan's measurement_head as the reference commit
# (joulewise/b5/driver.py:712), and the installer forces that field to equal the clone's HEAD
# (joulewise/night_agent_install.py:1234-1242). So the arm compares HEAD with itself, and a window input
# changed after H_claim is first seen by the harvest, after the window has collected. This check makes the
# same comparison before the window, at the desk, in under ten seconds.
#
# It writes into a scratch custody directory, never into the window's own custody: the harvest reads
# <custody>/flags/desk.jsonl of the real custody as part of the window's record.
#
# Usage: b5_desk_seal_check.sh <measurement clone> <H_claim, 40 hex> <night_plan.json> <new scratch directory>
# Exit 0: no flag. Exit 1: at least one flag (printed). Exit 3: usage or a missing input.
set -u
M="$1"; H_CLAIM="$2"; PLAN="$3"; OUT="$4"
PY="$M/.venv/bin/python"; D5="$M/configs/campaigns/v5_claim_25g83"
[ -x "$PY" ] && [ -f "$PLAN" ] && [ ! -e "$OUT" ] || { echo "usage or missing input"; exit 3; }
mkdir -p "$OUT" || exit 3
PACK_ROOT=$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["hazard_window"]["pack"]["pack_root"])' "$PLAN") || exit 3
PACK_SHA=$(/usr/bin/python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["hazard_window"]["pack"]["pack_sha256"] or "")' "$PLAN") || exit 3
[ -n "$PACK_SHA" ] || { echo "the plan records no pack digest (pack_digest_error at plan time)"; exit 1; }
( cd "$M" && PYTHONDONTWRITEBYTECODE=1 "$PY" -B scripts/collect_window_flags.py --stage desk --custody "$OUT" --repo "$M" \
    --pack "$PACK_ROOT" --plan-id desk-seal-check --attempt 1 --h-claim "$H_CLAIM" \
    --expected-pack-tree-sha256 "$PACK_SHA" --sealed-inventory "$D5/sealed_inventory.json" \
    --identity-pins "$D5/identity_pins.json" --catalog "$D5/flag_catalog.json" \
    --collector checkout_identity --collector executed_code --collector pack_identity --collector model_identity \
    > "$OUT/stdout.json" 2> "$OUT/stderr.txt" ) || { echo "the collector program did not run: $(tail -1 "$OUT/stderr.txt")"; exit 3; }
[ -f "$OUT/flags/collector_runs.jsonl" ] || { echo "no collector run record was written"; exit 3; }
if [ -s "$OUT/flags/desk.jsonl" ]; then
  /usr/bin/python3 -c 'import json,sys
for line in open(sys.argv[1]):
    flag = json.loads(line); print("FLAG", flag["code"], json.dumps(flag.get("observed"))[:300])' "$OUT/flags/desk.jsonl"
  exit 1
fi
echo "no flag: the clone's code, pack, models and interpreter are the sealed ones"
