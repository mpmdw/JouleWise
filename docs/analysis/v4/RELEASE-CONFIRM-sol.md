# ALIGN v4 release confirmation — Sol

2026-11-08. **Verdict: HOLD.** F2 is only partially closed: required output can
still disappear and turn a detected disagreement into AGREE. The other prior
findings are closed in the exercised synthetic paths.

Reviewed release-tools `99875485d..8ba59ac55`, engine-r23j
`50f4958b6ded78f5f9f38e7d2cec9587e8f7f2e2`, and recompute
`9f8a8749eda8387a827fe6c96afb942ceec89df5`. Authority: adopted A0–A36
(`a3465eda8:docs/analysis/v4/INTERPRETATION-RULINGS-DRAFT.md`, adoption in
`origin/main:RUN_STATE.md` 230), A37, R22–R26 and the A2(4)/A21/A27 amendments
in items 233–242; D-161's mistake/functional-failure scope.

## Prior findings

| Finding | Confirmation |
|---|---|
| F1, both seats: stale calibration rule | Closed in tested paths. Both predicates require eight admitted windows; barred C1/C4 contribute nothing, C9/C10 replace them. Frozen C9–C14 order/seeds and R25 N=22 are installed. An unbarred low-m window cannot obtain a reserve. |
| F2, both seats: omitted rows | Original H-grid, curve-dose, H*, U3 replay-pair and residual-tail witnesses now reject. **Not fully closed:** additional missing rows/cells below still AGREE. |
| Seat 1 F3: W1 unavailable reason | Closed. `insufficient_contrast_runs` and common absent fit statistics compare; prose is exempt. |
| Seat 1 F4 / seat 2 F3: producer identity | Closed for the demonstrated operator mistake. Identities are recomputed from the pinned engine under the release interpreter; contradictory scorer/reducer identities refuse even with an updated ordinary run record. |
| Seat 2 F4: journal digests | Closed. Nested member references, including journals, are rehashed; the changed-journal witness refuses. |
| Seat 2 F5: malformed export exit | Closed for exercised malformed nested shapes: fixed refusal, exit 2 and structured stdout. |
| Seat 2 F6: runbook pin | Closed. The command uses pinned defaults; CPython 3.13 and the actual build pins match the wrapper. |
| Seat 2 F7: U5 mapping | Closed. Point = abs(beta) × delta; upper shift = absolute slope bound × delta. Negative slope and delta=2 controls agree. |

## Release blocker: completeness still depends on printed output

`scripts/compare_v4_recompute.py:1185–1211` visits only printed U4 window keys,
optional statistics and interval elements. Neither the new `row_completeness`
checks nor `row_manifest()` requires these rows. U6 position checks similarly
iterate printed `means_j` keys (1343–1351); its manifest counts pairs only.
For H* (692–698), required presence is inferred from the recompute's `h_star`
field, rather than independently required by the registered member role.

New witnesses in `tests/v4_release/test_confirm_sol.py` establish:

| Synthetic change | With required output present | After omission |
|---|---|---|
| Change recompute C5's cumulative U4 verdict (W ≥ 3) | Exit 1, `u4` HOLD | Delete engine `U4.per_window.C5`: exit 0, AGREE |
| Add 0.1 to recompute C5's upper U4 interval endpoint | Exit 1, `u4_values` HOLD | Keep only engine interval endpoint 0: exit 0, AGREE |
| Add 1 J to one recompute spam U6 position mean | Exit 1, `u6_values` HOLD | Remove that position from all three engine position maps: exit 0, AGREE |
| Omit a short C benign carrier's undefined H* record | Engine-only omission refuses via `row_completeness` | Omit its recompute H* record too: exit 0, AGREE |

Every false AGREE has zero unmapped leaves and an agreeing `row_completeness`
family. Inventories are regenerated consistently; raw inputs and numerical
bars are untouched. The H* witness removes a null H* **with missing-dose
disclosures**, modeling a shared serializer/interpretation mistake that prints
only defined H*. R26 explicitly requires that undefined record too.

The stronger wrapper witness removes C5's U4 row from the otherwise agreeing
fill, hashes it into the ordinary synthetic run record, and runs the complete
release from a clean disposable checkout. It returns **exit 0 / AGREE**, with
producer identity verified and zero unmapped leaves. The wrapper therefore
does not independently close this gap.

This is an omitted-output/serialization failure of the same kind as original
F2, with a registered control result at stake (A14/R20). These mutations do
**not** establish that the pinned
producers currently omit those rows on an unmodified input.

**Required next step:** derive U4 window keys and required statistics/interval
cardinalities from the crosswalk and independent structural availability;
require U6 position keys from the recomputed turns; require H* records on the
R26 roster on **both** sides, including undefined records. Audit the remaining
print-driven loops for the same omission pattern. Convert these observational
witnesses to rejection regressions and repeat the synthetic release. No change
to numerical bars or to the frozen engine is requested by this finding.

## Other checks and limits

Reviewed scale-specific bars, exact ranks/member identities and bootstrap
comparisons; no separate tolerance blocker was established. The exercised
A2(4)/A21/A37 fixtures cover owned edge gaps, gate-only gaps and large-epoch
rounding/snapping. A27 injected token counts refuse without printing the
literal publicly; inspected value-bearing outputs remain private. I found no
additional demonstrated shared arithmetic-rule defect or public sealed-value
escape. This is bounded review evidence, not proof for all possible records.

## Verification and handoff

All unittest commands ran sequentially, one module per Python 3.13 process.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.v4_release.test_review_sol1` | 12 passed, 223.503 s, including the cold full rehearsal |
| `python3.13 -B -m unittest tests.v4_release.test_review_sol2` | 14 passed, 35.219 s |
| `python3.13 -B -m unittest -v tests.v4_release.test_confirm_sol` | Final: 6 passed, 40.509 s; preliminary 5-test version also passed in 40.722 s |
| `python3.13 -B -m unittest tests.v4_release.test_compare_v4` | 19 passed, 36.909 s |
| `python3.13 -B -m unittest tests.v4_release.test_release_v4` | 17 passed, 30.880 s |
| Selected `test_rehearsal_v4` methods, command below | 5 passed, 120.211 s, including the cold probe rehearsal |
| AST parse of the new witness module; `git diff --check` | OK |

```bash
python3.13 -B -m unittest \
  tests.v4_release.test_rehearsal_v4.RehearsalTests.test_series_shape \
  tests.v4_release.test_rehearsal_v4.RehearsalTests.test_bar_plus_reserve_on_both_sides \
  tests.v4_release.test_rehearsal_v4.RehearsalTests.test_short_trajectory_h_star_rows \
  tests.v4_release.test_rehearsal_v4.RehearsalTests.test_owned_time_and_large_epoch_fixtures \
  tests.v4_release.test_rehearsal_v4.RehearsalTests.test_probe_series_agrees
```

The final commands passed 73 tests. Including the preliminary five-test run,
total unittest time was 527.953 s (about nine minutes). The full suite was not
run, as instructed. Existing immutable synthetic
rehearsal outputs are reused as fixture inputs; every comparison/release
witness executes its checks afresh. No production decision cache was added.

Only this report and the new witness module are changed. Production programs,
pins, coordination state and kernel tasks are untouched. No network, weights,
real measurement files, real restricted directories, B5 pipeline, quiet-machine
operation or MLX execution was used. No native MLX test is needed for these
stdlib review artifacts. Real-data execution and unsealing remain with the
lead. Handoff branch: `align/2026-11-08-release-confirm-sol`; local commit
message: `review(v4): hold release confirmation on incomplete row coverage`.
Nothing is pushed.

The new module deliberately asserts the observed bad behavior; its passing
omission tests reproduce the blocker and are **not** passing safety tests.
Open question for the lead: disposition the incomplete F2 closure and repair
the comparator before release admission.
