# BY-MERGE: BYTES pass-1 deltas onto lane/2026-10-22-bytes-pass1

Director: local Opus 5.5 (resumed after interactive session 2dc9c377 ended;
the previous director had stopped before any merge). Worktree
`/Users/edr/code/jw-wt/by-merge`. Synthetic data only.

## Heads merged (origin heads at 18:03 PDT 10-22)

| Order | Branch | Item | Head | Merge commit |
|---|---|---|---|---|
| base | lane/2026-10-22-bytes-pass1 | BY-INT (+fix1) | b66963564 | |
| 1 | lane/2026-10-22-bytes-pass1-review-fixes | BY-REV | 478873066 | eda7a6282 |
| 2 | lane/2026-10-22-bytes-c4-pins | BY-G | 683a37534 | 592ee5c1f |
| 3 | lane/2026-10-22-bytes-c5-gates | BY-C5 (+fix1 parts 1-3) | 4d722be8a | 85c231b09 |
| 4 | lane/2026-10-22-bytes-loop | BY-LOOP (+fix1) | e4e71de43 | d379e37c1 |
| 5 | lane/2026-10-22-bytes-battery-term | BAT-3 (+fix1 rounds b, c) | fda9b380d | 640d4db16 |
| 6 | lane/2026-10-22-bytes-twin-parity | BY-TWIN | 043dfb32a | a831cd0a8 |
| 7 | origin/main | | 7c23ea4b7 | ea72a8be9 |

Not merged: draft PRs #573 (into battery-term) and #574 (into twin-parity),
per the brief. The twin-parity head 043dfb32a does not carry BY-TWIN-BAT:
that work exists only as the scratch merge
`scratch/2026-10-22-by-twin-bat` 624adf821 with no twin battery code.

## Conflicts

| File | Branches | Resolution | Governing text |
|---|---|---|---|
| joulewise/bytes_analysis.py, `reduce_models` phase cell | pass1 (h1_family) vs battery-term (decode-assist block) | Battery-term block verbatim, with pass1's `h1_family=h1_checks(manifest)` kept on its `_phase_cell` call | Addendum 8 and BY-INT-fix1's registered roster (H1 family size k read from the manifest); BAT-RULING.md s8 placements for the decode-assist cell. Each text governs its own part, so no ruling was needed. |
| tests/fixtures/bytes/campaign.py, `archive_campaign` signature | pass1 (`drop_8b_8bit`) vs battery-term (`battery_assist`, `battery_publication`) | Both keyword sets; bodies auto-merged | Same as above (fixture feeds both). Identical to the BY-TWIN-BAT scratch resolution 624adf821. |
| tests/hazards/test_monitor.py, `SupervisorTests` header | main (setUpClass live-hardware opt-in, PR #563) vs BY-LOOP-fix1 (run()/track_supervisor reaper) | Both kept | Disjoint behaviour; no text needed. |

One conflict did not show up in the text merge. CI run 39883766703 shard 7
found it after the merges, and it reproduced on the Mac:

| File | Branches | Resolution | Governing text |
|---|---|---|---|
| tests/b6/round_support.py `bytes_rehearsal` | BY-LOOP (rehearsal must reach SMOKE_RUN on bytes-s1-p1) vs BY-C5-fix1 (R2-3: a BYTES pack whose sizing row has no valid registered P holds as `LaneMissing("driver:disk.budget_missing")`) | The rehearsal's fixture-only sizing rows also carry fixture-only `disk_derivation` terms. They use the same inputs as tests.b6.test_plan_inputs (B 1000001, wait 7200, fixed 19, P = 2(B+wait)+fixed, peak_copies 2, session_wait_budget_s from joulewise.b5.plan) and are labelled as not a BYTES C5 measurement. Production code is unchanged, and the R2-3 hold stays (tests.b6.test_lane_adapters still pins it). | R2-3 (BY-C5-fix1 director ruling, LEDGER line 111) governs production. BY-LOOP's acceptance (NEXT, PRECHECK, SMOKE_RUN, then the fake launchctl argv) governs what the rehearsal must show. A rehearsal without P can only show the hold, so to meet both texts the fixture must register P. This is a decision I made; the lead may overrule it. The alternative is to make the rehearsal assert the hold. |

Before the fix, `test_bytes_guard_shaped_rehearsal` ended in HOLD_LOOP
with `lane_missing:driver:disk.budget_missing`. After it, the test passes.
The whole tests.b6.test_loop_round_desk module passes (6 tests), along with
lane_adapters 22, precheck 24, b6_plan_render 5, session_wrapper 6 and
hazards.test_monitor 35 (1 skip, live-hardware opt-in).

What this means for real runs: the BYTES loop will hold at prepare until
the BYTES sizing rows carry a registered P (BY-SLOTS/BY-PIN).
tests.b6.test_plan_inputs reports "registered BYTES sizing rows checked: 0".

NEEDS_RULING: none.

## Generated files

Regenerated once with their generators on the merged tree
(`scripts/bytes_plan_trees.py`, `scripts/build_b6_flag_catalog.py --write`,
`scripts/bytes_mac_kit.py`): `git status` empty afterwards, so every
generated file reproduces byte for byte. `--check` exit 0 for all three
(12 draft registrations and 12 fixed pass trees; catalog; non-claim Mac kit).

## Modules (JW_B5_SYNTHETIC_ONLY=1, one TMPDIR per module)

All OK except `tests.test_bytes_agreement.AgreementTests.test_defects_campaign`.

| Module | Tests | Result |
|---|---|---|
| tests.test_bytes_analysis (18 classes run separately, each under 10 min) | 98 | OK |
| tests.test_bytes_twin | 68 | OK |
| tests.test_bytes_agreement | 10 | 1 FAIL (defects) |
| tests.test_bytes_gates | 21 | OK |
| tests.test_bytes_manifest | 17 | OK |
| tests.test_bytes_mac_kit | 4 | OK |
| tests.test_bytes_h_session | 36 | OK |
| tests.b6.test_bytes_packs | 10 | OK |
| tests.b6.test_blinding | 8 | OK |
| tests.b6.test_release_subset | 4 | OK |
| tests.b6.test_catalog | 4 | OK |
| tests.b6.test_plan_inputs | 9 | OK |
| tests.test_b6_loop | 64 | OK |
| tests.hazards.test_import_graph | 6 | OK |
| tests.hazards.test_refusal_allowlist | 23 | OK |

Agreement: 0 fields above the bar in bytes, resident, time, minimum,
edge_locked and withheld. The defects campaign has 387 fields above the bar.
All of them come from the battery term, which the analysis now applies and
the twin does not yet implement (BY-TWIN-BAT). For example, the held-out
qwen3-30b-a3b dc_input gross cell mean is 23.62 J in the analysis and
19.59 J in the twin. The same test on the scratch merge 624adf821
(twin-parity plus battery-term only, without the other lanes) gives the
same 387 fields; the 40 it prints are the same fields with the same
analysis values, and the twin values differ only in the last float digit.
So this merge adds no disagreement. BAT-3's CI predicted this failure
("expected until BY-TWIN-BAT"). The acceptance line "agreement 0 above the
bar" is therefore NOT met until BY-TWIN-BAT lands on twin-parity and is
merged here.

Logs: /Users/edr/night-archive/forward-20261021/BY-MERGE/logs/.

## CI

- c7e3973e0 (merge head plus this report), run 39883766703: 18 of 20 jobs green.
  Shard 5 has one failure, `test_bytes_agreement` defects (the BY-TWIN-BAT gap above).
  Shard 7 has one failure, `test_bytes_guard_shaped_rehearsal` (the cross-lane
  conflict above, fixed in the next commit). gate-ledger 39883766618 skipped (draft).
- The next head's run is recorded in the PR #535 comment and the ledger.

## Open

- BY-TWIN-BAT: the twin's battery term, then a merge of twin-parity into this branch.
- #573 and #574 audit-fix PRs: merge into their lanes, then a second BY-MERGE pass.
