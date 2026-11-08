# W1 smoke: software gates and native gap checklist

**Status: PARTIAL / NOT CLEARED FOR MBP LAUNCH.** The offline extension and
transcript recorder/parser are implemented. A runnable native reduced-window
builder and automatic fault orchestration are blocked on the lead choices
below. No native smoke has run on this lane. Synthetic PASS is never hardware
validation, and this document does not authorize a collection during a window.

Ed's objective is to catch a cheap fault before spending a 12 h W1/D window.
The native target is **45 min total**, including setup and teardown, in a gap
with no measurement window, no active collection and no agent load. The
magistrate owns that machine-state decision. Do not use the R1 integrated lane.

## Decisions required before native preparation

1. **Reduced scaffold:** unchanged W1 has 4,995 s of scaffold alone (83.25 min,
   `align_v4_kit.SCAFFOLD_S`), before members. A complete production chain cannot
   meet 45 min. Recommendation: use the existing isolated-copy/reduced-stage
   approach in `joulewise.b6.smoke`, with a separately reviewed W1 reduction,
   keeping production arm/launcher/member/meter/finalizer code. That reduction
   still needs a W1 builder and tests. Never silently drop scientific stages in
   a W1 plan. The source receipt must remain bound to the unedited candidate;
   a reduced smoke tree cannot be represented as that registered tree.
2. **Stale/edited valid triage:** current `v4_cadence.next_arm_triage` checks
   schema and all 14 gate statuses, but consumes no timestamp or previous-record
   digest. A stale valid packet is accepted; editing nonempty `basis` text is
   accepted too. Recommendation: leave the production contract change to the
   lead and keep PREQUAL red until freshness/byte binding is installed. A
   changed status of `fail` already refuses, but does not test this hazard.
3. **Inputs:** the branch's registration receipt is pending; the R1-filled
   `registration/w1_plan.json` and frozen series projection are absent. The
   candidate check must fail until the lead supplies them. Never fabricate a
   lead signature, register a smoke, or substitute synthetic sizing for R1.

The minimum registered D episode budget is 6,144, with a 4,096 token turn cap
(`align_v4_kit.BUDGET_FLOOR`, `d_turn_cap_tokens`). A one-token arbitrary config
would not be a registered W1 member. The native builder must state its exact
token controls and whether it uses those minima or a separately approved
smoke-only reduction. This is another reason not to advertise a measured
45-minute bound yet.

## Air gate: one command

At the clean candidate commit, with reviewed planning inputs inside this clone:

```sh
python3.13 -B scripts/align_v4_prequal.py --offline --w1-smoke-only --stage w1 \
  --output /private/tmp/w1-prequal-NEW --w1-candidate FULL_CANDIDATE_SHA \
  --w1-series RELATIVE_SERIES_PROJECTION.json \
  --w1-window-plan RELATIVE_PLANNED_WINDOW.json
```

Expected today: a nonzero exit, with explicit missing-registration, missing-plan
and stale-valid-triage failures. The production arm CLI, R1 chain and meter path
probes can pass synthetically while those gates remain red. Full PREQUAL still
has its existing model/runtime requirements; this command is its offline W1
extension only. [PREQUAL.md](PREQUAL.md#w1-extension-offline-w1-smoke-lane)
documents both projection formats and the limits of their validation.

## Native checklist after those decisions are installed

All artifacts must live under a fresh dedicated root whose window and plan IDs
contain `smoke`. Set its eligibility to NON-REGISTRABLE, never pool it and never
run study analysis on it. Copies of the calibration ledger and head pin must
have distinct inodes and remain within the smoke root, as in `b6.smoke.copy_ledger`.
Do not use `bytes_h_session.measurement_view` as an isolated ledger copy: that
function deliberately links the source `runs/` directory.

| Attempt | Exact path / expected outcome | Target budget |
|---|---|---|
| Baseline window | Production v4 arm CLI with every argument below; one or two declared minimum-budget members; production HAZARD_PACK launch, real KM003C samples, finalized bundles, authenticated terminal closure. Every executed member has available DC; GPU capture succeeds. | 15 min |
| `triage-stale` | A stale but structurally valid copy of the packet; **must refuse** for triage freshness before installation/chain start. Currently not implemented by production. | 1 min |
| `triage-edited` | Change bound packet bytes while keeping statuses valid; **must refuse** for digest mismatch before installation/chain start. Currently not implemented by production. | 1 min |
| `receipt-digest` | Edit one executed-closure file in a scratch checkout; real receipt validator refuses with `registration_receipt digest drift`. Restore/discard only that scratch copy. | 1 min |
| `disk-image` | Attach a tiny disk image; a separate arm refuses with `external_volume`; detach that exact image and verify absence. | 2 min |
| `cpu-contender` | A bounded single CPU contender launched outside the measurement tree; separate production dry arm refuses for **contention**, not the agent census or another fault. Reap only that owned process. | 2 min |
| `meter-killed` | Separate short smoke window; kill only its journal-identified meter while a member is active. Affected member has `status: missing`, a `meter.*` flag, and unchanged GPU admissibility. GPU capture must still succeed. Supervised restarts cannot splice DC across the member. | 15 min |
| `missing-topup` | Separate arm with required CLI arguments present but blank top-up evidence; refuses with `completed top-up evidence missing`, before installation. Merely omitting required argv tests argparse instead. | 1 min |
| `r1-chain` | Real export → backfill-x-g → backfill-turn-counts → derive-contrast → kit --check over a **synthetic** R1 record in the smoke root, never a sealed record. | 2 min |
| Teardown / report | Image unmounted; contender, meter and chain processes proven gone; smoke job uninstalled; no High Power restore owed; all transcripts retained. | 5 min |

Targets sum to 45 min; they are estimates pending the native builder and an
actual MBP timing. Do not reduce thermal waits, meter coverage or production
physical checks to force this estimate to pass.

## Known production commands (reference; do not launch before the gates above)

The magistrate resolves `M` to the clean candidate checkout, `P` to its pinned
venv interpreter, `S` to the fresh dedicated smoke root, `H` to the full
candidate SHA, and `TOPUP`/`OPERATOR` to real current evidence. Nothing below
uses the R1 integrated lane or downloads weights.

```sh
"$P" -B scripts/align_v4_smoke.py init --root "$S" --candidate "$H"

# Source production prepare (complete W1; NOT a <=45-min reduced smoke builder).
"$P" -B scripts/align_v4_session.py prepare \
  --measurement-root "$M" --session-root "$S/source-prepare"

# Production arm CLI; the future W1 smoke builder must supply this session.
"$P" -B scripts/align_v4_session.py install --session-root "$S/baseline-session" \
  --w1-disk-config "$S/arm/disk.json" --next-arm-triage "$S/arm/triage.json" \
  --topup-completed-at "$TOPUP" --topup-source "$OPERATOR" \
  --obc-off-attested-by "$OPERATOR"

# Shared HAZARD_PACK dry-arm path for the separate contention attempt.
"$P" -B scripts/run_night.py run --dry-arm --plan "$S/cpu-session/custody/night_plan.json"

# Existing archive/finalization route, smoke/non-claim only. Do not use
# --allow-missing-terminal to turn a failed terminal check into a pass.
"$P" -B scripts/harvest_b6_session.py --plan "$S/baseline-session/custody/night_plan.json" \
  --archive-root "$S/archive" --registration-dir "$S/registration" \
  --pack-records-root "$S/private" --export-dir "$S/export" --non-claim --smoke
```

These are command interfaces, not a completed native launch recipe: the W1
reduction, isolated session builder and terminal/finalize receipt adapters are
still blocked. In particular, don't point `install` at a normal W1 session and
call it a small smoke.

Safe fault ingredients, to be wrapped in the separate attempt's teardown:

```sh
# Scratch checkout only; never edit the measurement candidate.
git clone --no-hardlinks --shared "$M" "$S/receipt-checkout"
git -C "$S/receipt-checkout" checkout --detach "$H"
printf '\n# smoke receipt drift\n' >> "$S/receipt-checkout/joulewise/align/apple/prompt_cache.py"
"$P" -B -c 'import sys; from joulewise.align.apple.v4_registration import require_registration; require_registration(sys.argv[1])' \
  "$S/receipt-checkout"
# Expected: exit 1, registration_receipt digest drift.

hdiutil create -size 32m -fs APFS -volname JW-W1-SMOKE "$S/disk-fault.dmg"
hdiutil attach -nobrowse -plist "$S/disk-fault.dmg" > "$S/disk-attach.plist"
# Run only this attempt's arm; retain its v4-arm-NNN.json. In a finally/trap,
# detach the exact dev-entry from disk-attach.plist; retain hdiutil info -plist
# proving it is gone. No forced detach and no unmount of unrelated volumes.

# Single CPU process outside the tree, self-limited to 30 s. Retain its PID
# and reap that same child in a finally/trap after the separate dry arm.
(cd /private/tmp && "$P" -I -S -c 'import time; end=time.monotonic()+30
while time.monotonic()<end: pass') &
CONTENDER_PID=$!
# Run the separate dry arm, then wait "$CONTENDER_PID"; never kill by name.
```

No code on this lane attaches an image, creates a contender or signals a native
reader automatically. Fault orchestration and its native teardown verification
remain part of the blocked native builder.

## Transcript recorder and parser

The recorder accepts explicit argv, an injected runner in tests, a bounded
timeout, and named safe relative artifacts. Native CLI recording requires
`--gap-confirmed` and macOS. It captures exit/stdout/stderr; it does not decide
whether a nonzero exit was the expected refusal. Every attempt is create-once.

For an already prepared **separate** disk-image attempt, for example:

```sh
"$P" -B scripts/align_v4_smoke.py record --root "$S" --case disk-image \
  --gap-confirmed --timeout-s 120 \
  --chain-start disk-session/custody/night/chain.started \
  --artifact refusal=disk-session/staging/v4-arm-001.json -- \
  "$P" -B scripts/align_v4_session.py install --session-root "$S/disk-session" \
  --w1-disk-config "$S/arm/disk.json" --next-arm-triage "$S/arm/triage.json" \
  --topup-completed-at "$TOPUP" --topup-source "$OPERATOR" \
  --obc-off-attested-by "$OPERATOR"

# Record actual exact-image cleanup plus absence verification with teardown;
# the operator-supplied command must do BOTH and return nonzero on failure.
# A successful /bin/true is not cleanup evidence.
"$P" -B scripts/align_v4_smoke.py teardown --root "$S" --case disk-image \
  --gap-confirmed -- "$P" -B "$S/reviewed-detach-and-verify.py"

"$P" -B scripts/align_v4_smoke.py report --root "$S"
```

The parser emits a table and a create-once `smoke-report.json`, exit 0 only if
all nine cases and the 2,700 s wall-time target pass. Missing cases, missing
cleanup, wrong refusal reason, unexpected chain start, timeout, or changed
hashed artifact fail. Wall time includes gaps from initialization through the
last teardown. It cannot prove arbitrary operator cleanup commands correct;
native orchestration must supply reviewed verification commands.

Artifact aliases for `record --artifact NAME=RELATIVE_PATH`:

| Case | Required artifacts |
|---|---|
| Refused arm | `refusal`: real arm/refusal JSON. Receipt drift instead uses the real validator exception stderr. `--chain-start` is mandatory for negatives. |
| `window`, `meter-killed` | `night_result`, `hazard_result`: production records; `dc_members`: `km003c.session_report` output; `gpu_members`: run-id map of `align_pilot_session.episode_summary` results, requiring a finite GPU energy channel without blocking flags. `finalize: {status: ok}` and `terminal: {terminal: true}` are **adapter receipts still to be implemented**, not substitutes an operator should hand-author. |
| `r1-chain` | `chain: {synthetic_only: true, steps: {export: 0, backfill-x-g: 0, backfill-turn-counts: 0, derive-contrast: 0, kit-check: 0}}`; automatic receipt adapter is still to be implemented. |

The parser's positive cases are synthetic-tested against that adapter interface.
Until the adapters, isolated native builder and fault teardown are implemented,
there is no end-to-end native PASS claim.

## Verification outside this sandbox

After the lead resolves the blockers, complete the builder/adapters, then run
the complete checklist on the MBP in a clean agent-free gap. Repeat native MLX
tiny-config checks and the pinned stack import there (no Metal/CPU MLX fallback
was available in the sandbox). Preserve real capture and teardown transcripts;
never pool or analyse these smoke results. A successful native smoke qualifies
the exercised launch/fault paths, not long-window thermal stability or D model
numerics.
