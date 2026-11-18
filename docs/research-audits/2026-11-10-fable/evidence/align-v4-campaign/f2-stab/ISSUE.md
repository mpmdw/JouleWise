# F2 stability one-leg issue template

Use the selected item under items 418 (d) and 422. Each item authorizes
one leg, one fresh soak and one launch. The draft kit, queue entry and item
identify the same roster, attempt, kit hash and runner pin.
[Manifest](MANIFEST.md)

## Fill and stage

1. Select one item and its matching queue entry in kit order. Check the
   operational record for earlier attempts and completed legs. Each leg
   runs once. Fill the issue number and local timestamp from `date` and
   record the actual committed queue hash. The pointer deadline is the
   Check target. The issued item has `expires_epoch_s: null`.
2. The queue drafts carry the pinned v1 entry fields. Their `not_before`
   is the local date RL-179 took effect. It sets no assigned run date.
   The draft wrapper leaves `expires_at` blank as JSON `null`. The pinned
   queue validator requires an offset timestamp, so the lead commits a
   fresh data queue with that field filled under F-6. Keep the kit path,
   hash, roster, sequence and attempt bound to the selected entry.
   The timestamp serves the pinned format. Kit and item eligibility
   follow the admitted hashes and named stops under item 422. Use the
   committed queue with the pinned `validate-queue` and the audit
   checkout as `--kits-root`.
3. Stage the hash-verified kit and queue outside the detached runner
   checkout. Record the kit and queue commit, hashes, admitted pin and
   new output path. Use the manifest hashes and the selected item's
   explicit roster. Apply item 422 over any legacy window, expiry,
   hand-gate, copy or read wording retained in the copied kit.

## Start and check

- Re-read the issued and READY work, host state and named stops.
  Arm only when higher-priority work cannot arm. Rank the first
  stability leg of the local date at 1 and further stability legs that
  date at 4. Rank 2 is finite F2 instrument work and rank 3 is hp-02
  while `lm-hp-01` has yet to run. F0 ranks last until the
  post-R1 Check. Under rows 1–2, protect each pending dated block so
  every span can still take its t0 on its date. Account for this
  one-leg plan's fence time and the bounded copy wait in that census.
- Record the exact preceding close. Require its receipt, restore
  readback, feed stops, cleared fence, absent process group and no
  foreign process under row 4. The successor's soak and G0 checks
  supply row 5. Let the copy verify or wait up to 600 s and confirm
  it has stopped before the next soak. Record copy debt and page at
  2 h and daily after under row 14.
- Apply the pinned host checklist and current scoped stops. Automatic
  desk failure or a consumer-gate failure holds the kit under row 6.
  Apply row 8 on the first native run of a new pin or leg type.
  Hand table, Q1 and desk-final are look prerequisites under row 7.
  The pinned launcher owns its own fence and host checks.

Fill `SRC` with the checkout containing the admitted kit bytes and
`REPO` with the clean detached runner checkout. Fill `KIT` and `QUEUE`
with the staged files and `KIT_SHA` and `QUEUE_SHA` with their admitted
SHA-256 hashes. Set `KIT_ID`, `SPAN`, `LEGS` and `SEQ` from the item.
`ARG` names the applicable pinned batch window. The pin judges the
actual t0, single-leg fence and soak window. A refused plan does not arm.
The audit-side validator checks the RL-180 cell order and then runs the
pinned `validate-kit` with frozen-path verification.

```sh
set -eu
cd "$REPO"
PIN=2d347f721552fe03bdd19f113e7bad7a7c24908e
test "$(git rev-parse HEAD)" = "$PIN"
test -z "$(git status --porcelain)"
if git symbolic-ref -q HEAD >/dev/null; then exit 1; fi
case "$ARG" in
  02:00-02:35|13:14-13:15) ;;
  *) exit 1 ;;
esac
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = "$KIT_SHA"
test "$(shasum -a 256 "$QUEUE" | cut -c1-64)" = "$QUEUE_SHA"
VALIDATE="$SRC/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/tools/validate_kit.py"
"$PY" -I -B "$VALIDATE" "$KIT" --repo "$REPO" --batch-window "$ARG"
"$PY" -B scripts/cadence_queue.py validate-queue "$QUEUE" --kits-root "$SRC"
"$PY" -I -B - "$KIT" "$QUEUE" "$KIT_ID" "$KIT_SHA" "$SPAN" "$LEGS" "$SEQ" <<'PY'
import json
from pathlib import Path
import sys

kit_path, queue_path, kit_id, kit_sha, span_id, leg_id, seq = sys.argv[1:]
kit = json.loads(Path(kit_path).read_text())
queue = json.loads(Path(queue_path).read_text())
assert kit["campaign_id"] == kit_id and kit["ruling"]["id"] == "RL-179"
assert queue["queue_id"] == f"cq-{kit_id}" and queue["halt"] is None
entry, = [row for row in queue["spans"] if row["span_id"] == span_id]
assert entry["seq"] == int(seq) and entry["block_id"] == kit_id
assert entry["legs"] == [leg_id] and entry["attempt"] == 1
assert entry["kit"]["sha256"] == kit_sha
PY
T0="$(date +%s)"
PLAN="$("$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs "$LEGS" --batch-window "$ARG" --t0 "$T0")"
printf '%s\n' "$PLAN"
OUT="$OUTPUT_ROOT/$KIT_ID/cq-$SPAN-a1-$(date -u '+%Y%m%dT%H%M%SZ')"
test ! -e "$OUT"
```

## Run

Refresh the gates and actual t0 immediately before launch. Confirm the
rank, dated-block census, selected batch argument, exact admitted hashes,
scope of stops and host readiness against the refreshed plan. Use the
printed fence end as the launcher deadline. The launcher enforces its
minimum reserve again.

```sh
set -eu
cd "$REPO"
test "$(shasum -a 256 "$KIT" | cut -c1-64)" = "$KIT_SHA"
test "$(shasum -a 256 "$QUEUE" | cut -c1-64)" = "$QUEUE_SHA"
VALIDATE="$SRC/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/tools/validate_kit.py"
"$PY" -I -B "$VALIDATE" "$KIT" --repo "$REPO" --batch-window "$ARG"
T0="$(date +%s)"
PLAN="$("$PY" -B scripts/cadence_legs_runner.py plan --kit "$KIT" --legs "$LEGS" --batch-window "$ARG" --t0 "$T0")"
printf '%s\n' "$PLAN"
DEADLINE="$(printf '%s\n' "$PLAN" | "$PY" -I -B -c \
  'import json,sys; p=json.load(sys.stdin); assert p["worst_case_s"]==5850; print(p["fence_end_epoch_s"])')"
test ! -e "$OUT"
"$PY" -B scripts/launch_cadence_span.py launch \
  --repo "$REPO" --python-bin "$PY" --kit "$KIT" --legs "$LEGS" \
  --batch-window "$ARG" --output "$OUT" --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
```

Exit the session immediately after the launch. Record a refusal under
item 422 and hold the affected kit or block until an input changes.

## Check

After the fence is gone, use the operational receipt and the pinned
desk's operational projection. Match the existing `OUT`, runner
pin, kit ID and hash, and sole leg to the item. A clean close requires
the successful receipt, all feeds stopped, restore readback and process
group absent under row 4. Record the close epoch, desk verdict, named
stops, copy status, t0 local date and the RL-179 rows applied. Use the
item 418 (g) daily summary and immediate verdict-change reporting.

Row 12 seals the stability series until freeze 2 is committed and
`lm-stab-01` has its cold pass. Check uses operational projections
only. Any authorized read uses frozen code and the closed roster at
its stage-1 hash. The series is descriptive and enters no fit or count.
