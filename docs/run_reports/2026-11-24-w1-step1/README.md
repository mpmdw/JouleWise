# W1 runbook step 1: ready to run once PR #824 is admitted

This is trial PR #958 report §9 step 1, made mechanical under lead decision D3 (2026-11-24 00:30). It waits only
on #824 r3: R0 admitted and the authorized R0 record's digest named. `w1_step1.py` does the step and prints
digests, key names and pass/fail lines only. It never prints a value from `inputs.json`, `r1_slots.json` or the
planning release. It commits nothing.

## Inputs the lead supplies

| Input | Where it comes from |
|---|---|
| `--pin` | The issued W1 commit with the frozen R1 source inventory and blobs |
| `--component-heads` | Lead-reviewed JSON object mapping PR numbers as strings to full commit IDs |
| `--r0-record-sha256` | The authorized R0 record's sha256, from #824's admission (RL-193 item 6) |
| `--r0-note` | Needed only if that digest is not `e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b`, the frozen `configs/align/v4/r1_runtime.json` `sensors.r0_sha256` (RL-89's `smc/r0.json`). One line naming which record each digest names and why (RL-207's missing fact). It goes into the cold-pass packet |
| `--member-seconds` | R1's `member_s` for the 18 W1 members, as a JSON list in ordinal order (FINAL-DESIGN B8). The lead's file. The script never chooses or derives one |
| `--plan-id` | The W1 plan id |

## Preconditions (the script checks all of them)

1. A clean checkout `$J` of the W1 integration branch after every merge, the port last (§9 "Before step 1").
2. Clear Git environment overrides for the directory, working tree, and index (F-10).
3. The ten R1 source blobs match `--pin`. The tool reads the source names from that commit.
4. Every commit in `--component-heads` is an ancestor of HEAD.

## Command

```sh
python3.13 -B docs/run_reports/2026-11-24-w1-step1/w1_step1.py --repo "$J" \
  --pin "$PIN" --component-heads heads.json \
  --r0-record-sha256 <64 hex> [--r0-note "<one line>"] \
  --member-seconds member_s.json --plan-id <id> --out /Volumes/JW-EXT/scratch/<seat>/w1-step1 \
  --reader-census /Volumes/JW-EXT/scratch/d-w1-signing-reader-census/run_census.py --trace
```

Run it from a checkout of this trial branch, or copy the one file; `--repo` points at the integration checkout.
The dynamic closure trace takes about 22 minutes. The reader census runs after trace generation against
the generated Git tree from a temporary index. The receipt records the tree ID for review.

## What it does, and what to expect

| Step | Action | Expected |
|---|---|---|
| 0 | Preconditions | Clean checkout, component ancestry, and ten source blobs equal to the pin |
| 1 | RL-207 completion: `heavy: true`, `per_turn: true`, `sensors.fan_keys` = `["F0Ac", "F1Ac"]` from `r1_runtime.json` (blob `bf8479b26`), and `sensors.r0_sha256` = `R0.record_sha256` = the given digest | Exactly five key paths change. DEC2's five-leaf digest is unchanged: `0f80e5939c5496ca4402b397ce6689f55261d5e12c8f91660ea6a0dcf8f83d6a` on #886's `inputs.json`, blob `3becfed63` |
| 2 | Kit regeneration with R0 bound | exit 0 |
| 3 | `w1_plan.json` from the validator's own template, filled with inputs' B_D, I_D, T_dead, effort and policy, r1_slots' `max_r1_tail_s` and the lead's `member_s` | `validate_align_v4_w1_plan.py` prints VALID |
| 4 | Kit and template regeneration to a fixed point. The plan is rebuilt if its member bindings moved | `regeneration: fixed point after N round(s)` |
| 5 | `align_v4_kit.py --check`, then the refusal census | `--check` passes every gate before registration. Its first stop is **`registration_receipt is pending or malformed`**, because `require_registration` reads the receipt, then `u3_bar.json`, `battery_window_policy.json` and `wp19_receipt.json`. The census reports no difference |
| 6 | Dynamic closure trace and reader census | Every scenario passes, the trace is copied into `docs/align/v4/dynamic_closure_trace.json`, and the census passes against the generated tree |
| 7 | Digest table and `step1-receipt.json` | Every changed path with its blob and sha256, plus evidence status |

Exit 0 and `READY_FOR_LEAD_REVIEW` require the exact registration receipt stop and both evidence checks.
Omitting an evidence check yields exit 1 and `PARTIAL`, with the missing items in the receipt. An unexpected
kit exit, including exit 0, or another refusal yields exit 2 and `PARTIAL`. Refusal diagnostics report a
fixed code, exception type, and known field or path names. Opaque child diagnostics are hashed.

**Historical synthetic dry run (2026-11-24).** On a throwaway checkout of trial head `59314f6a7`, the
synthetic run passed the pre-registration gates and stopped at the receipt. The run predates the trace
and generated-tree census requirements. It changed 23 paths:
- `inputs.json`, `w1_plan.json` and `sizing_b5.json`;
- `collection_plan.json`, `plan_tree.json` and `identity_pins.json`;
- the 16 stage files and their 2 order manifests;
- `night_plan.template.json`.

The refusals were checked as well: a dirty tree, an exported `GIT_DIR`, and a non-frozen digest with no
note. The dry-run digests are synthetic and are not the real ones.

## After the script

1. Review `git status` and commit on the integration branch. This is the candidate head (§9 step 1).
2. **Step 4** (§9 step 2, RL-210): run the RL-184 three-blob check once on this head with #839's block
   (`a37a3462b`). Its three blobs are `scripts/align_v4_u3_export.py` (`b35c94801` now),
   `u3_sources/selection.json` (`729e8667d`) and `collection_plan.json`. `collection_plan.json` moves
   in step 1: it is `fbd357c45` before.
3. The U3, B policy and WP19 steps (W1-BLOCKERS §4 steps 1–12; MBP or lead), then the receipt (§9 step 3),
   then signing (§9 step 4). `--check` must then exit 0.

## Accepted-diff proof

```sh
python3.13 -B docs/run_reports/2026-11-24-w1-step1/accepted_diff.py "$REV" "$BASE" \
  --repo "$J" --presign "$PRESIGN" --component-heads proof-heads.json \
  --step1 "$STEP1_BEFORE..$STEP1_AFTER" --pr973 "$PR973_BEFORE..$PR973_AFTER" \
  --kit-root "$J"
```

Use immutable commits for review. `BASE` identifies the comparison base and the reference for each
component's merge base. `--presign` supplies the starting tree and defaults to `BASE`. The Part C port
from PR #959 is in presign. Supply the remaining component heads in application order in
`proof-heads.json`, with PR numbers as strings and full commit IDs as values. PR #839 supersedes PR #826
where both changed a path. Repeat `--step1` or `--pr973` for disjoint reviewed ranges in replay order.

`--kit-root` enables `step1-generated` classification using `build_files` in memory from the reviewed
tool checkout. Point it to a clean checkout at `REV`. Kit inputs carried through byte-for-byte still
require an accepted delta. The proof compares bytes and Git modes, and it records residuals with their
owners and any merge conflict. Review each residual before accepting it with a separate exact
`--accept-residual PATH` argument. Any unaccepted residual gives exit 1, and a proof setup error gives
exit 2.

Known pre-state at #886 `8fc76a0b9`, as blob and sha256 prefix:

| File | Blob | sha256 |
|---|---|---|
| `inputs.json` | `3becfed63` | `a18ca653…` |
| `r1_slots.json` | `b6056ef6f` | `f156239e…` |
| `r1_planning_release.json` | `daeb4708a` | `171b2a3b…df6a`, which RL-189 §2.5 item 1 requires |
| `collection_plan.json` | `fbd357c45` | `b06f8ca2…` |
| `night_plan.template.json` | `6bfc797bc` | `ff0c4d41…` |
