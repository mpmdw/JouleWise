VERDICT: ACCEPT_WITH_FIXES

# L9-ENV-FINAL-FABLE: cold final pass on lane L9-ENV (opt-in analysis-side inverted-corner clamp)

Seat L9-ENV-FINAL-FABLE (gate policy gate 4, Fable family; an Opus delta review runs in parallel).
Reviewed cold: `origin/main` (`12ce1241d`) `...` `d8050fca6` on `lane/2026-10-30-l9-env-analysis-clamp`
(lane base `7ebb7db2a`, 8 lane commits). Branch `review/2026-10-30-l9-env-final-fable` is `d8050fca6`
plus this report and `.codex-report/l9-env-final-fable/` (evidence). The lane head has one later
commit (`6b7063860`, interim L9-ENV-5 report and mutation evidence, no code); its `L9-ENV-5.md` was read as
claims. Synthetic data only (`JW_B5_SYNTHETIC_ONLY=1`); I did not open or search for real block-5/6/BYTES
data. Full history fetched (`git fetch --unshallow origin`).

## Bottom line

The clamp itself is right and bounded. `joulewise/reduce.py` and the other three `ESTIMATOR_CODE_PATHS`
files are byte-identical to `origin/main` (reduce.py sha256 `7b9c0d28…`, the block-5 registration pin).
`scripts/run_campaign.py` is untouched, constructs the session without the flag, and refuses exactly as at
`origin/main`. The clamp is reachable only through `AuthenticatedConsumptionSession(analysis_clamp=True)`,
which only the eleven analysis consumers pass; `origin/main` added no new consumer since the lane base.
The clamped envelope's `lower_j` is the exact minimum over the admissible `(delta, eps_on, eps_off)` set
with inverted intervals counted as 0 J, re-derived independently on five hand-built cases. On the suite's
synthetic 0.5.2 bundle the analysis re-derivation changes no energy figure: only
`energy_anchor_shift_envelopes` gains the omitted member pointers and their precheck reasons move from
`anchor_energy_envelope_unrecorded` to `anchor_energy_envelope_exceeds_quarter_metric` (both metric-local;
the global refusal set is identical). All five `tests/test_whole_window*.py` modules pass.

One fix is required before merge (F1). `d8050fca6` merged with current `origin/main` fails one test in the
whole `tests/b5_analysis` run: `test_step4_reason_table` R1, because the string literal `"analysis_clamp"`
that the signature-gated opt-in at `joulewise/analysis_engine/inputs.py:3801-3804` introduces is picked up
by main's blind step-4 reason-table generator, which scans `inputs.py` for every snake_case string
constant. The lane at `d8050fca6` alone cannot see this (main added the table and its test after the lane
base); `origin/main` alone passes. The fix is the seat's own NR1, now mandatory: pass `analysis_clamp=True`
as a literal keyword at that site, which I verified restores the generator output to `origin/main`'s bytes
and turns the module green; it needs a one-line change to an out-of-scope test fake. Two further
observations (F2, F3) are low/informational and do not block.

## Answers to the five questions

**(1) Can the clamp change a point estimate, or any session whose envelope reduce.py already defines?**
No.
- Point estimates: `_clamp_inverted_operative_envelopes` (`joulewise/whole_window.py:1202`) touches only
  `energy_anchor_shift_envelopes` (`:1318-1333`) and the clamped members' `window_evidence_precheck`
  reasons (`:1340-1355`). A clamped envelope's `point_j` is `_shift_energy_j(contributions, 0.0)`, the same
  expression reduce uses (`:1029`). Probe (`l9-env-final-fable/q1_probe.py`, log in `logs/`): on the
  synthetic 0.5.2 bundle at two dominating bounds the flat diff between reduce's re-derivation and the
  analysis re-derivation has 20 and 30 changed leaves, all under `energy_anchor_shift_envelopes/...` or
  `window_evidence_precheck/phase/*/reasons`; `energy figures changed: 0`. The clamped prefill envelope's
  `point_j` equals both the re-derived `phase_energy_j.prefill` and the minted `point_j`.
- Envelopes reduce defines: `_clamped_corner_composed_anchor_shift_envelope` calls reduce's own mint
  function first and returns its result when it is not `None` (`:968-975`), so non-inverting input is
  reduce's bytes by construction (confirmed equal on my cases C and E, including the boundary case where
  the window is exactly `2*edge` long: reduce defines it, `lower_j = 1.9e-07`, and the clamp returns the
  same values). Recorded member envelopes are never replaced: a recorded pointer is only compared (`:1264-1268`)
  and a mismatch returns the summary unchanged. With no omitted pointer, `clamped` is empty and the
  function returns the input object (`:1308-1309`).
- Session: the session's acceptance test of the operative envelopes is unchanged (`:1900-1940`): every
  minted pointer must be present with equal `point_j` and a containing interval. A clamped envelope has
  `lower_j = 0 <= minted lower_j` and an upper bound that is monotone in the edge bound, so it can only
  discharge a member that `origin/main` refused with `anchor_energy_envelope_unrecorded`; it cannot alter
  a member `origin/main` already discharged.

**(2) Can the clamp make a refused envelope "defined" in the listed failure modes?** No, each path is
fail-closed to `summary` unchanged:
- Mirror does not reproduce a recorded member envelope: `:1264-1268` (`!= recorded` returns `summary`).
  No recorded member envelope reproduced at all: `:1286-1289` (O-F3).
- Input window already inverted at zero shift: `:992` returns `None` (O-F5); reduce returns `None` for the
  same input, so nothing is added.
- Negative power: `:989` (same guard as reduce's `_corner_composed_anchor_shift_envelope`).
- Unknown recorded member pointer: `:1312-1317`.
- Tail-refusal context (`post_window_trace_tail_shorter_than_anchor_bound`): envelopes are added and the
  gates are left alone (`:1334-1338`), which is what reduce does in that context (it mints envelopes and
  stamps only the tail reason, `reduce.py:2441-2456`). The tail reason is not in
  `_METRIC_LOCAL_PRECHECK_REASONS` (`whole_window.py:721`), so the session fails globally either way.
- Unresolved anchor, mock backend, non-powermetrics, non-current reducer version, non-succeeded status:
  `:1224-1251`.
- A clamped envelope whose own gate reasons are empty is not added (`:1299-1309`, L9-ENV-4 F1), so a member
  never becomes eligible through the clamp. `_restamp_clamped_gate` (`:1172`) requires the gate to be
  ineligible and to carry the `unrecorded` stamp, including on every inner window entry; on any failure
  the whole operative copy is discarded (`:1353-1355`). Both current reducers stamp inner windows
  (`reduce.py:3290-3298` and `:3651-3660`, `include_inner_windows=True`), so the recursion is consistent.
- Exceptions: the mirror calls the same reader and reduce helpers that already ran inside the succeeded
  re-derivation, on the same inputs; it adds no exception type that reduce's own path could not raise.

**(3) Does anything outside analysis change behaviour?** No.
- `git diff --stat origin/main...d8050fca6` touches 16 files: `whole_window.py`, the eleven call sites,
  two reports and three test files. Not in the diff: `joulewise/reduce.py`, `scripts/run_campaign.py`,
  `joulewise/calibration_bracketing.py`, `joulewise/controller.py`, `configs/**`, `tests/b5_analysis/**`.
- Byte identity: `git diff origin/main d8050fca6 -- joulewise/reduce.py joulewise/powermetrics_fiducial.py
  joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py scripts/run_campaign.py` is empty;
  `git hash-object joulewise/reduce.py` = `origin/main:joulewise/reduce.py` = `82449d58…`;
  `sha256sum joulewise/reduce.py` starts `7b9c0d28`.
- `scripts/run_campaign.py` constructs the session once (`:8425`) without `analysis_clamp`; the flag
  defaults to `False` (`whole_window.py:1410`) and is honoured only when literally `True` (`:1426`); the
  default session calls reduce's `_rederive_summary_for_authenticated_fiducial_bound` exactly as at
  `origin/main` (`:1853-1857`). The constructor appears in the same twelve files at `origin/main` and in
  the merged tree; no file `origin/main` changed since the lane base references the constructor or the
  re-derivation seam.
- The new module-level names (`_clamped_corner_composed_anchor_shift_envelope`,
  `_group_envelope_contributions`, `_restamp_clamped_gate`, `_clamp_inverted_operative_envelopes`,
  `_rederive_operative_summary`) have no caller outside `whole_window.py`; the only entry is `_prepare`
  behind the flag. Nothing is monkeypatched.

**(4) Is the lower bound really the minimum over the four corners with zero-length clamped windows?**
Yes. Independent derivation (`l9-env-final-fable/q4_rederive_exact.py`, log in `logs/`): I evaluate the
energy over `(delta, eps_on, eps_off)` directly (an inverted interval contributes 0 J), take eps at the
four corners (energy is monotone nonincreasing in each start and nondecreasing in each end, so corners are
exact), take delta at every window-edge-minus-trace-edge breakpoint in `[-B, B]` plus the endpoints
(piecewise linear in delta for interval-support traces), and additionally sample 20 000 random interior
points which must lie inside `[lower_j, upper_j]`. Results, all with containment `True`:

```
A single short window (0.30 s, 2e = 0.40): reduce None; clamp lower 0.0 upper 1.79999942779541; exact min 0.0 max 1.79999942779541
B two intervals (1.0 s and 0.10 s), e = 0.12: reduce None; clamp lower 1.8399997138977042 upper 3.899999380111695; exact equal (1e-9)
C non-inverting control (1.0 s): reduce defined; clamp values == reduce values == exact
D zero-length input window: reduce None; clamp point 0.0 lower 0.0 upper 1.0000000476837156 == exact
E window exactly 2e long: reduce defined (lower 1.9073486345888568e-07); clamp == reduce == exact
```

Case B is the multi-interval case: only the 0.10 s interval inverts, the clamp's `lower_j` equals the
true minimum (the surviving interval's energy at the (+e, -e) corner minimised over delta), not 0.
The code (`:1036-1058`) applies the clamp per window at each corner and then runs reduce's own
breakpoint-exact scanner, and `lower_j = min` over the four corners (`:1062`).

**(5) Whole `tests/b5_analysis` and `tests/test_whole_window*.py` at `d8050fca6` merged with `origin/main`.**
Merge `d8050fca6` + `origin/main` (`12ce1241d`) is clean (`50499b7b2`); `origin/main` changed none of the
lane's files. `tests/b5_analysis`: `Ran 1035 tests`, `FAILED (failures=1, skipped=13)`, the one failure is
F1. The five `tests/test_whole_window*.py` modules: all `OK` (26, 11, 32, 8 and 57 tests). Exact tails in
VERIFICATION.

## Findings (ranked)

### F1 (High for merge; fix before merge). The merged tree fails `tests/b5_analysis/test_step4_reason_table.py` R1

- Evidence: on `d8050fca6` merged with `origin/main` (`50499b7b2`), the whole-directory run ends
  `Ran 1035 tests ... FAILED (failures=1, skipped=13)`; the failure is
  `test_R1_generator_output_plus_the_recorded_ruling_is_the_registered_file`
  (`tests/b5_analysis/test_step4_reason_table.py:165`, `self.assertEqual(self.table, expected)`). The module
  alone: `origin/main` `12ce1241d` `Ran 8 tests ... OK`; merged tree `Ran 8 tests ... FAILED (failures=1)`
  (`logs/step4_reason_table_main.log`, `logs/step4_reason_table_merge.log`).
- Cause: `tests/b5_analysis/step4_reasons/make_table.py` (byte-pinned, added to main in #609 after the lane
  base) collects every string constant matching `[a-z][a-z0-9]*(_[a-z0-9]+)+` in eleven modules, including
  `joulewise/analysis_engine/inputs.py` and `joulewise/whole_window.py`, and the registered
  `configs/analysis/b5/step4_reason_classes.json` must equal that output plus the recorded ruling. The lane's
  gated opt-in at `inputs.py:3801` (`if "analysis_clamp" in inspect.signature(...)`) and `:3804`
  (`session_kwargs["analysis_clamp"] = True`) adds the literal `analysis_clamp`. Running the generator on
  both trees, the only difference is `tooling added: ['analysis_clamp']` (`gen_main.json` versus
  `gen_merge.json`). `whole_window.py` contributes no such literal; `floor_mint_estimator.py:490-491` has
  the same idiom but is not a scanned module.
- Why not regenerate the table: `analysis_clamp` is a constructor keyword, not a reason code, and the
  table is a registered blind classification that changes only with its test and a ruling.
- Fix (verified in a scratch worktree, reverted): at `inputs.py:3801-3810` drop the signature probe and
  pass the keyword literally on the constructor call (`analysis_clamp=True,` beside `mode=mode,`). After
  that change the generator output is byte-equal to `origin/main`'s (`gen_merge_fixed.json`),
  `tests.b5_analysis.test_step4_reason_table` is `Ran 8 tests ... OK`, and
  `tests.test_whole_window_analysis_clamp_flag` stays `Ran 11 tests ... OK` (its `SIGNATURE_GATED` branch
  is only taken when the keyword is absent). One out-of-scope test then needs one line:
  `tests/test_analysis_integration.py:2643` `FakeConsumptionSession.__init__(self, runs_root, bundle_ids, *, mode)`
  must accept `analysis_clamp` (`TypeError: ... got an unexpected keyword argument 'analysis_clamp'`,
  `logs/scratch_fix_integration_error.log`); the other 115 tests in that module pass. The lead needs to
  widen the lane's write scope to that test file (and, for consistency, `tests/test_floor_mint_estimator.py`
  so `floor_mint_estimator.py:490-491` can pass the literal too). The seat's `CallSiteTests` keeps pinning
  every consumer, so the change cannot silently drop the opt-in.

### F2 (Low, hardening). An omitted pointer that the mirror can define *without* clamping is still added

`whole_window.py:1271-1275`: for a pointer the re-derivation omitted, the result of
`_clamped_corner_composed_anchor_shift_envelope` is added whatever it is. That function returns reduce's
own (unclamped) envelope when reduce's mint function defines one (`:968-975`). Reduce omits a current-wire
member pointer only when that function returns `None` on *its* contributions, so a non-`None` reduce
result on the mirror's contributions for an omitted pointer can only mean the mirror disagrees with
reduce on that pointer. The reproduction proof (`:1264-1270`) sees only recorded pointers, so it cannot
catch a per-pointer disagreement on an omitted one. The L9-ENV-4 F1 guard (`:1299-1309`) discards such an
envelope when it passes its gate, which is the usual case for a narrow envelope, so the residual exposure
is an unclamped envelope that also exceeds the quarter-metric ratio. No real input reaches it: the
grouping code is the same for every pointer of a kind, and both fixture sweeps reproduce every recorded
pointer. Under a *simulated* discrepancy it is reachable (`l9-env-final-fable/f1_probe.py`: with the
mirror's prefill window stretched to 0.14 s and every recorded row untouched, reduce omits prefill, the
clamp adds an unclamped envelope with `lower_j = 0.0081` and the gate reads `exceeds_quarter_metric`).
The session still catches the case where the pointer was minted, because `point_j` would differ
(`:1926`); a pointer that was never minted is not checked and would reach `summary_for()`. Fix (one
line, strictly fail-closed): before computing the clamp for an omitted pointer, require
`_corner_composed_anchor_shift_envelope(contributions, *bounds) is None`, else `return summary`; that
is, the mirror must agree with reduce that the envelope is undefined before it is allowed to define it.

### F3 (Info; O-F6 and L9-ENV-4 O1). Clamped envelopes appear in the operative summary but not in provenance

On the synthetic bundle, `tokenize` (0.4 ms) and `generation_setup` (0 s) invert at every dominating bound,
so every flagged dominated member gains `lower_j = 0` envelopes for pointers that were never minted
(probe log, "non-inverting" case: both pointers added, prefill not). Analysis consumers read them from
`summary_for()`; the session's `operative_envelopes` provenance (`:1955`) records only minted
pointers, so a verdict row does not show that the clamp ran. This is sound (a wider interval with the
same point) and consistent with the ruling, and the gates stay ineligible with a metric-local reason.
Optional: record the clamped pointers in the per-member provenance (for example
`"analysis_clamped_pointers": sorted(clamped)`) so an auditor can see them without re-deriving; that is a
schema addition and needs the lead's call, not a merge blocker.

## Seat-claim check (L9-ENV-5.md, read as claims)

- "reduce.py stays byte-identical", "run_campaign never opts in", "12 constructor calls in 10 analysis
  consumers opt in", "no other constructor exists": confirmed (Q3 above; I count 11 files with 13 call
  sites including the two gated ones, matching the seat's table).
- "O-F3: at least one reproduced recorded member envelope": confirmed at `:1286-1289`.
- "O-F5: input window inverted at zero shift refused": confirmed at `:992`; reduce refuses the same input.
- "Non-inverting input gets reduce's bytes": confirmed by code (`:974-975`) and by my cases C and E.
- "Every dominated member's tokenize/generation_setup gates move to exceeds_quarter_metric (O-F6)":
  reproduced on the synthetic bundle.
- "The whole tests/b5_analysis directory is OK": true at `d8050fca6` alone, false once merged with current
  `origin/main` (F1). The seat's open issue that main's 62 commits "touch no file in this lane's scope" is
  correct but incomplete: main's new `test_step4_reason_table.py` scans `inputs.py`.
- "7 modules fail identically on origin/main because /bin/zsh is missing": not re-checked here; outside
  the requested scope.
- The L9-ENV-5 report at `6b7063860` still carries `STATUS: BLOCKED verification in progress` and two
  `*_PLACEHOLDER` tails; the lead should expect the seat's final tails before merge, but my own run below
  covers the requested scope.

## Mutation and probe notes

I did not re-run the seat's 38 mutants. I spot-checked the two survivors the seat argues equivalent that
matter for the bound: `<=` versus `<` at `:1050` (a zero-length shifted window maps to itself bit for
bit, since `(s + s) / 2.0 == s` for finite `s`), and the always-recompute body (reduce's operations in
reduce's order; my cases C and E give equal values). Both arguments hold.

## VERIFICATION (exact tails)

Worktree: `d8050fca6` merged with `origin/main` `12ce1241d` (merge commit `50499b7b2`, no conflicts, no
lane file touched by the merge). Python 3.13.17, Linux container, `unittest` (no pytest installed).
Environment: `TMPDIR=/tmp/lnine-final-fable/tmp` (outside the checkout, no float-like token),
`JOULEWISE_CUSTODY_PARENT=/tmp/lnine-final-fable/custody`, `JW_B5_SYNTHETIC_ONLY=1`,
`PYTHONDONTWRITEBYTECODE=1`. Commands:

```
python3.13 -m unittest discover -s tests/b5_analysis -t .
python3.13 -m unittest tests.test_whole_window
python3.13 -m unittest tests.test_whole_window_analysis_clamp_flag
python3.13 -m unittest tests.test_whole_window_inverted_corner_clamp
python3.13 -m unittest tests.test_whole_window_parallel_strict
python3.13 -m unittest tests.test_whole_window_selection
```

Tails (`module | Ran line | last line | exit`):

```
tests/b5_analysis (discover)                   | Ran 1035 tests in 3802.021s | FAILED (failures=1, skipped=13) | exit=1
  FAIL: test_R1_generator_output_plus_the_recorded_ruling_is_the_registered_file (tests.b5_analysis.test_step4_reason_table.Step4ReasonTableTests...)
tests.test_whole_window                        | Ran 26 tests in 1.131s      | OK | exit=0
tests.test_whole_window_analysis_clamp_flag    | Ran 11 tests in 87.964s     | OK | exit=0
tests.test_whole_window_inverted_corner_clamp  | Ran 32 tests in 126.092s    | OK | exit=0
tests.test_whole_window_parallel_strict        | Ran 8 tests in 1.101s       | OK | exit=0
tests.test_whole_window_selection              | Ran 57 tests in 196.653s    | OK | exit=0
```

Baseline and fix evidence for F1 (same environment):

```
origin/main 12ce1241d: python3.13 -m unittest tests.b5_analysis.test_step4_reason_table | Ran 8 tests in 5.999s | OK
merged 50499b7b2:      python3.13 -m unittest tests.b5_analysis.test_step4_reason_table | Ran 8 tests in 5.804s | FAILED (failures=1)
merged + literal keyword at inputs.py (scratch, reverted):
  tests.b5_analysis.test_step4_reason_table    | Ran 8 tests in 6.244s   | OK
  tests.test_whole_window_analysis_clamp_flag  | Ran 11 tests in 77.394s | OK
  tests.test_analysis_integration              | Ran 116 tests in 167.479s | FAILED (errors=1)  (FakeConsumptionSession keyword, see F1)
```

Full logs: `.codex-report/l9-env-final-fable/logs/*.log`.
