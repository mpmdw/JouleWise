VERDICT: ACCEPT

# L9-ENV6-FINAL-FABLE: cold final pass on the block-5 analysis-only envelope clamp lane

Seat L9-ENV6-FINAL-FABLE (gate policy gate 4, Fable family; an Opus delta review runs in parallel).
Reviewed cold: `origin/main` (`fb14d26a9`) `...` `555661945` on
`lane/2026-10-30-l9-env-analysis-clamp-l6`. `555661945` is itself a merge of current `origin/main`
into the lane (merge-base `fb14d26a9` = `origin/main`), so "555661945 merged with current origin/main"
is `555661945`. Branch `review/2026-10-31-l9-env6-final-fable` is `555661945` plus this report and
`.codex-report/l9-env6-final-fable/` (logs and probes). Every earlier report (L9-ENV-3/4/5/6, the
L9-ENV-3/5 Opus and Fable reviews, and the superseded `L9-ENV-FINAL-FABLE.md` on
`origin/review/2026-10-30-l9-env-final-fable`) was read as claims only. Synthetic data only; I did not
open or search for real block-5/6/BYTES data. Full history fetched (`git fetch --unshallow origin`).

## Bottom line

The lane does what Ed ruled and nothing more. The clamp lives in `joulewise/whole_window.py` only, is
reachable only through `AuthenticatedConsumptionSession(analysis_clamp=True)`, and the 13 constructor
calls that pass it (10 analysis consumer files) are pinned by `tests/test_whole_window_analysis_clamp_flag.py`.
`joulewise/reduce.py` (sha256 `7b9c0d2886904022…`, the block-5 registration pin), the other three
`ESTIMATOR_CODE_PATHS` files, `scripts/run_campaign.py` and `configs/analysis/b5/step4_reason_classes.json`
are byte-identical to `origin/main` (`l9-env6-final-fable/byte_identity.log`). A clamped envelope has
the same `point_j` as reduce's, `lower_j` equal to the exact minimum over the admissible set with inverted
intervals counted as 0 J (re-derived independently on five hand-built cases plus two refusal cases,
`l9-env6-final-fable/q4_rederive.{py,log}`), is never added when it would pass its own gate, and every
mirror-disagreement path, including the new omitted-pointer guard, returns reduce's summary unchanged.

The two fixes the superseded final pass asked for are in: the literal `analysis_clamp=True` at
`joulewise/analysis_engine/inputs.py:3805` and `joulewise/floor_mint_estimator.py:490` (its F1, the
step-4 reason-table failure), and the omitted-pointer guard at `joulewise/whole_window.py:1274-1277`
(its F2). The whole `tests/b5_analysis` directory and all five `tests/test_whole_window*.py` modules
pass at `555661945`; exact tails are in VERIFICATION below, from runs that completed, with full logs
committed. No finding blocks the merge. The findings below are consequences the lead should state in
the merge record (F1, F2) and carried informational notes.

## Answers to the five questions

**(1) Can the clamp change a point estimate, or any session whose envelope reduce.py already defines?**
No.
- `_clamp_inverted_operative_envelopes` (`joulewise/whole_window.py:1202`) edits exactly two things in a
  deep copy of reduce's re-derivation: `energy_anchor_shift_envelopes` (`:1325-1340`) and the clamped
  members' `window_evidence_precheck` reasons (`:1346-1363`). No energy field is touched. The copy is
  `json.loads(json.dumps(summary))`; `SummaryMetrics` has no tuple-typed field (checked
  `joulewise/schemas.py:1763-2289`), so the copy is shape-neutral and float-exact.
- A clamped envelope's `point_j` is `_shift_energy_j(contributions, 0.0)` (`:1029`), the expression
  reduce uses (`joulewise/reduce.py:2219`). The session then requires `operative point_j == minted point_j`
  for every minted pointer (`whole_window.py:1933`), so a mirror that disagreed on the point would refuse.
- Envelopes reduce defines are returned as reduce's bytes: `_clamped_corner_composed_anchor_shift_envelope`
  calls reduce's mint function first and returns its result when it is not `None` (`:968-975`); my cases
  C and D (non-inverting, and a window exactly `2*edge` long) give dict-equal results. A recorded pointer is
  only compared (`:1265-1269`); any mismatch returns the summary unchanged. With nothing to clamp the
  function returns the input object (`:1315-1316`), so a session whose every pointer reduce defines is
  bit-for-bit `origin/main`'s.
- The session's acceptance test of operative envelopes is unchanged (`:1920-1947`). A clamped envelope has
  `lower_j = 0 <= minted lower_j` and an upper bound that is monotone in the edge bound, so it can only
  discharge a member `origin/main` refused with `anchor_energy_envelope_unrecorded`, never alter one
  `origin/main` already discharged.

**(2) Can it make a refused envelope defined in the listed failure modes?** No; each path returns
`summary` unchanged (reduce's fail-closed result):
- Mirror does not reproduce a recorded member envelope exactly: `:1265-1268`. No recorded member envelope
  reproduced at all (mirror unproven for this bundle): `:1293-1296`.
- Mirror disagrees with reduce on an omitted pointer (reduce's own mint defines it on the mirror's
  contributions): `:1274-1277`, the new L9-ENV-6 guard, tested by
  `test_mirror_disagreeing_with_reduce_on_an_omitted_pointer_fails_closed` with a counterfactual at the
  L9-ENV-5 commit.
- Input window already inverted at zero shift: `:992` returns `None` (reduce returns `None` too; my case F).
- Negative power: `:989` (same guard as reduce; my case G).
- Unknown recorded member pointer: `:1318-1324`.
- Tail-refusal context (`post_window_trace_tail_shorter_than_anchor_bound`): envelopes are added, gates are
  left alone (`:1341-1345`), which mirrors reduce (`reduce.py:2441-2457`: mint, then stamp only the tail
  reason). The tail reason is not in `_METRIC_LOCAL_PRECHECK_REASONS` (`whole_window.py:721-736`), so the
  session fails globally either way.
- Unresolved anchor, mock backend, non-current reducer version, non-succeeded status: `:1225-1251`.
- A clamped envelope whose own gate reasons are empty is not added (`:1305-1316`), so no member becomes
  eligible through the clamp. `_restamp_clamped_gate` (`:1172`) requires the gate to be ineligible and to
  carry the `unrecorded` stamp, recursing into inner windows; both current reducers stamp inner windows
  (`reduce.py:3298` and `:3659`, `include_inner_windows=True`), and any restamp failure discards the copy
  (`:1360-1362`).
- Mirror parity, verified by reading both mint arms: same `_derive_anchor_context` arguments
  (`strict_calibration=True`, the member's reducer version, the authenticated override, the shared physics
  cache; `reduce.py:2928-2939`, `:3494-3505` vs `whole_window.py:1238-1249`); same bounds tuple
  (`bundle_bound_s`, `fiducial_bound_s or 0.0`, `edge_span_s`; `reduce.py:3195-3199`, `:2541-2546` vs
  `whole_window.py:1255-1259`); same window sets (0.5.2: `reader.phase_windows()`, `item_windows()`,
  `block_windows()`, `level_windows()` in reduce's order, `reduce.py:3581-3600`; 0.6.2: per-`(source, phase)`
  unions over `request_phase_windows()` with `source_curve` shifted by `anchor_curve[0].t - summed_curve[0].t`,
  `reduce.py:2946-2970`, `:3224-3238`); same raw curve (`reader.summed_curve()`, `reduce.py:2918`, `:3484`).
  Because the reproduction check is dict equality on reduce's own output (`:1265-1268`), any divergence in
  bounds, curve or windows fails closed before a clamp is added.
- Exceptions: the mirror's `except` (`:1283-1292`) covers reduce's own error types plus `KeyError`,
  `TypeError`, `ValueError`, `OverflowError`. The JSON copy at `:1325` is outside it; a `TypeError` there
  would reach `_prepare`'s handler (`:1885-1895`) and refuse the member as `instrument_calibration_invalid`,
  still fail-closed.

**(3) Does anything outside analysis change behaviour?** No.
- `git diff --stat origin/main...555661945`: 32 files; code changes are `joulewise/whole_window.py`, the 13
  constructor calls in 10 consumer files (`floor_extraction.py:3181`, `analysis_engine/inputs.py:2031`,
  `:2135`, `:3805`, `b5_analysis/dry_run.py:1081`, `paper_reported_energy_issuer.py:149`,
  `window_duration_margins.py:802`, `floor_mint_estimator.py:490`, `analysis_manifest_v3.py:3776`,
  `scripts/mint_floor_artifact.py:557`, `:1261`, `scripts/check_window_provenance.py:1055`,
  `scripts/produce_b5_disclosures.py:117`), two one-line test fakes, three new test modules, and reports.
- Byte identity against `origin/main` (blob ids equal, `git diff` empty; `byte_identity.log`):
  `joulewise/reduce.py` (sha256 `7b9c0d2886904022…`), `joulewise/powermetrics_fiducial.py`,
  `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py` (the four `ESTIMATOR_CODE_PATHS`,
  `joulewise/calibration_bracketing.py:239-244`), `scripts/run_campaign.py`,
  `configs/analysis/b5/step4_reason_classes.json`.
- `scripts/run_campaign.py` contains no `analysis_clamp` token; the flag defaults to `False`
  (`whole_window.py:1417`), is honoured only when literally `True` (`:1433`), and the default session calls
  reduce's `_rederive_summary_for_authenticated_fiducial_bound` (`:1860-1864`) exactly as at `origin/main`.
  `test_rederive_selection_reads_the_flag_alone` pins that selection to the flag alone.
- The vendored oracle `tests/oracle_l9_env_2_reduce_clamp.py` is imported by no production module.
- The new module-level helpers have no caller outside `whole_window.py`; the only entry is `_prepare`
  behind the flag, and removed-member audit sessions inherit the flag (`:1755`).

**(4) Independent re-derivation of the clamp lower bound.** Done, `l9-env6-final-fable/q4_rederive.py`
(log `q4_rederive.log`, `ALL PASS (7/7)`). My own integrator evaluates the energy over
`(delta, eps_on, eps_off)` directly, counts an inverted interval as 0 J, takes eps at the four corners
(energy is monotone in each edge for nonnegative power) and delta at every window-edge minus trace-edge
breakpoint in `[-B, B]` plus the endpoints (piecewise linear for interval-support traces), and checks
20 000 random interior points for containment. Hand-built case A: 10 W constant trace, window 0.30 s,
`edge = 0.15 + 0.05 = 0.20` so `2*edge = 0.40 > 0.30`; by hand the `(+edge, -edge)` corner inverts and
contributes 0 J, the `(-edge, +edge)` corner is `10 W × 0.70 s = 7 J`, the point is `10 W × 0.30 s = 3 J`:

```
A: reduce None; clamp point 2.9999999999999982 lower 0.0 upper 7.000000000000002; exact equal; containment True
B two intervals (1.0 s, 0.10 s), edge 0.08: reduce None; clamp lower 4.562595892656736 upper 8.386908191356447; exact equal (1e-9)
C non-inverting control: reduce defined; clamp == reduce (dict equality) == exact
D window exactly 2*edge: reduce defined (lower 0.0); clamp == reduce == exact
E window just under 2*edge: reduce None; clamp lower 0.0; exact equal
F already-inverted input window: reduce None, clamp None
G negative power sample: reduce None, clamp None
```

Case B shows the multi-interval behaviour: only the short interval is zero-lengthed, and `lower_j` is the
true minimum (the long interval at the `(+edge, -edge)` corner minimised over delta), not 0. The code applies
the clamp per window at each corner (`:1046-1056`) and then runs reduce's breakpoint-exact scanner, taking
`min` over the four corners (`:1062`).

**(5) Whole `tests/b5_analysis` and every `tests/test_whole_window*.py` at 555661945 merged with current
origin/main.** `555661945` already contains `origin/main` `fb14d26a9`. Results in VERIFICATION.

## Findings (ranked)

### F1 (Low; state it in the merge record, no code change). Behind the flag a clamped member's refusal moves from the tooling class to the stop-side R3 class at step 4

- Where: `joulewise/whole_window.py:1172-1198` and `:1346-1363` replace `anchor_energy_envelope_unrecorded`
  by the clamped envelope's gate reasons, in practice `anchor_energy_envelope_exceeds_quarter_metric`
  (`reduce.py:2328-2362`). Both reasons are metric-local for the session (`whole_window.py:721-736`), so the
  session's global set is unchanged for never-minted pointers. For a pointer that WAS minted and inverts only
  at the dominating operative bound, the session moves from a global `anchor_energy_envelope_unrecorded`
  refusal (`:1945-1946`) to a ready session with a metric-local path refusal; that is the ruling's intent.
- Consequence: `configs/analysis/b5/step4_reason_classes.json` lists
  `anchor_energy_envelope_exceeds_quarter_metric` in `r3` and `anchor_energy_envelope_unrecorded` in `tooling`
  only. `joulewise/b5_analysis/steps.py:107-108` names a refused non-p42 cell `extraction_cell_r3_refusal`
  (stop-side) when any of its reasons is in `r3`, else `extraction_cell_tooling_refusal`. So a step-4 cell
  whose member window inverts under the operative bound is, after this lane, an R3 refusal instead of a
  tooling refusal (or instead of a session-level refusal). This is consistent with Ed's ruling (the envelope
  is defined but too wide, a substantive refusal), and the table itself is untouched.
- Fix: none in code. Record in the PR/merge note and in the lane report that step-4 classes can move
  tooling -> R3 for such cells, so the block-5 step-4 reading is not surprised by it. If Ed did not intend
  the class change, the only alternative is a ruling, not a lane edit.

### F2 (Info). `scripts/check_window_provenance.py` F5-2 now checks "independently clean pass" with analysis semantics

- Where: `scripts/check_window_provenance.py:1049-1065` builds the session with `analysis_clamp=True` and
  asserts `status == "passed"` and no refusal reasons.
- Effect: the clamp only removes refusals, so no stored pass can newly fail F5-2. A stored pass that reduce's
  unclamped re-run would refuse (a member window inverting under the snapshot's operative bound) now reads
  as independently clean. With the collection-time snapshot the operative bound equals the mint bound and
  nothing inverts, so the case is theoretical.
- Fix: none required. If the lead wants that checker to keep collection semantics, drop the flag at this one
  site and remove the entry from `ANALYSIS_CONSUMERS` in `tests/test_whole_window_analysis_clamp_flag.py:38-49`;
  otherwise note the semantics in the lane report.

### F3 (Info; carried from L9-ENV-3 O1, L9-ENV-4 O1, superseded final pass F3). Provenance does not show that the clamp ran

- `whole_window.py:1948-1963` records `operative_envelopes` for minted pointers only. A minted pointer that
  inverted at the operative bound is recorded with the clamped values (`lower_j = 0`) and no marker; a
  never-minted clamped pointer (tokenize, generation_setup on the synthetic bundle) is not recorded at all,
  though `summary_for()` returns it. Sound and consistent with the ruling; every such gate stays ineligible.
- Optional: add `"analysis_clamped_pointers": sorted(clamped)` to the per-member provenance. Schema addition,
  lead's call, not a merge blocker.

### F4 (Info; report nit). `L9-ENV-6.md` says "all 12 sites must pass a literal True"

The diff and `ANALYSIS_CONSUMERS` (`tests/test_whole_window_analysis_clamp_flag.py:38-49`) have 13
constructor calls in 10 files (`inputs.py` has three, `mint_floor_artifact.py` two). `CallSiteTests`
pins the per-file counts, so the code is right; only the prose count is off.

## Seat-claim check (L9-ENV-6.md and the superseded final pass, read as claims)

- "inputs.py and floor_mint_estimator.py now pass analysis_clamp=True literally": confirmed
  (`inputs.py:3805`, `floor_mint_estimator.py:490`); no `"analysis_clamp"` string constant remains in any
  module the step-4 generator scans; `tests.b5_analysis.test_step4_reason_table` passes inside the whole-
  directory run below.
- "Omitted-pointer disagreement fails closed": confirmed at `:1274-1277` with its test and counterfactual.
- "Selection pin": confirmed, `test_rederive_selection_reads_the_flag_alone`.
- "The registered table is NOT regenerated": confirmed byte-identical to `origin/main`.
- Superseded final pass: its F1 and F2 are fixed in this head; its F3 is carried as F3 here; its Q1-Q4
  answers agree with my reading; its Q5 claim (whole `tests/b5_analysis` on the merged tree) is replaced by
  the completed run below.
- L9-ENV-5 O-F6 ("tokenize and generation_setup gates move to exceeds_quarter_metric behind the flag"):
  confirmed by code; its step-4 class consequence is F1 here.
- I did not re-run the seats' mutant tables; my own probe covers the function body (Q4).

## VERIFICATION (exact tails)

Tree: `555661945` checked out on `review/2026-10-31-l9-env6-final-fable` (it already contains current
`origin/main` `fb14d26a9`; merge-base `fb14d26a9`). Linux container, Python 3.13.18, `unittest`.
Environment: `TMPDIR=/tmp/jw-review-tmp` (outside the checkout, no float-like token),
`JOULEWISE_CUSTODY_PARENT=/tmp/jw-review-custody`. Every run below completed; each log's first line
records the HEAD and start time and its last line the exit code and finish time. Commands:

```
python3.13 -m unittest discover -s tests/b5_analysis -t .
python3.13 -m unittest tests/test_whole_window.py
python3.13 -m unittest tests/test_whole_window_analysis_clamp_flag.py
python3.13 -m unittest tests/test_whole_window_inverted_corner_clamp.py
python3.13 -m unittest tests/test_whole_window_parallel_strict.py
python3.13 -m unittest tests/test_whole_window_selection.py
python3.13 -m unittest tests.b5_analysis.test_step4_reason_table
```

Tails, quoted from the committed logs in `.codex-report/l9-env6-final-fable/`:

```
b5_analysis_discover.log                       | Ran 1035 tests in 3237.339s | OK (skipped=13) | exit=0
test_whole_window.log                          | Ran 26 tests in 0.881s      | OK              | exit=0
test_whole_window_analysis_clamp_flag.log      | Ran 12 tests in 68.010s     | OK              | exit=0
test_whole_window_inverted_corner_clamp.log    | Ran 33 tests in 107.550s    | OK              | exit=0
test_whole_window_parallel_strict.log          | Ran 8 tests in 0.373s       | OK              | exit=0
test_whole_window_selection.log                | Ran 57 tests in 166.345s    | OK              | exit=0
step4_reason_table_module.log                  | Ran 8 tests in 5.813s       | OK              | exit=0
```

Probe and identity evidence: `q4_rederive.log` ends `ALL PASS (7/7)` / `exit=0`; `byte_identity.log`
lists equal blob ids at HEAD and `origin/main` for the six pinned files and an empty `git diff`.

Not done here: the seats' mutant tables were not re-run; the L9-ENV-3 note that seven unrelated modules
fail on `origin/main` for a missing `/bin/zsh` was not re-checked (outside the requested scope).
