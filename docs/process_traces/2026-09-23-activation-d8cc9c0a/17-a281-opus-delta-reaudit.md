# 17 — A281 delta re-audit, contract lens (Opus 5.5 subagent), head d2f9a273

Transcribed by the magistrate from the subagent's final report (brief 13). Probes: `/tmp/a281delta/p1.py`–`p4.py`, `mut.py`.

**Verdict: FAIL. 1 blocker, 5 should_fix, 8 nits.** Named acceptance: `Ran 30 tests in 1.144s OK`. Independent operand-collapse gate: packer 84/84, reducer 34/34, estimator 112/112 killed. 13 targeted mutants, 2 survived (N6).

## Clause table

| Clause | Status | Evidence |
|---|---|---|
| X1 crossover | PARTIAL | 88111 → none, 1n888 → 3, merged boundary → `boundary_in_merged_group` pass; fallback `energy_per_correct.py:241-245` contradicts 08 (S2); packet C's non-monotone rule missing (B1) |
| X2 split pairing | MET | `:17-18`, `:87-91`, one bound per window `:99-100` |
| X3 terminal single | MET in packer | `scored_packer.py:233-244`; no estimator handling (S4) |
| X4 worst-case singles | MET | `:217-232`, `:247-256`; worst-case input unchecked (N2) |
| X5 cell balance | MET on the stated grid | F1 order reproduces, both means 5.2, gap 0; five-level rosters reach 0.6–0.88 (N1) |
| X6 estimability | MET | `:203-205`; pooled constituents mislabelled (S1) |
| X7 decide API | PARTIAL | arm/role/level checked, ready ratios refused (`:153-163`); family not tied to arm (S3) |
| X8 floor gate | MET | `:82-84`; equality case untested (N6) |
| X9 digest chain | MET | registered_sha256 survives four requeues; parent_sha256 correct; cap/envelope/offset/pitch bound; incoming digest not verified (N3) |
| X10 levels | MET | `:159-161` |
| X11 reducer M2 | MET | `scored_reduce.py:50-52`; missing retry_stage filled silently (S5) |
| X12 Holm | MET | |
| X13 zero-token | MET | `:60-65` |
| X14 mutation gate | MET | 230/230 |

**Open ruling (split interval):** the seat's reading is honest. The point estimate is a ratio of measured gross sums, so it equals the unsplit estimate when the singles sum to the parent. Each extra window carries its own floor and anchor, so k singles mean k bounds. Recommend a dated addendum reading X2's "equals the unsplit result" as the estimate.

**Same-signature:** (i) crossover YES (B1, S2); (ii) pairing YES (S4, N7); (iii) labels-vs-cells NO; (iv) silent defaults YES (S3, S5, N2); (v) surviving mutants YES at nit level (N6). "This is the second round with class (i) findings. Under the standing escalation rule, the next step should be a consult, not a blind third fix round."

## Blocker

**B1. A non-monotone pattern produces a crossover.** Packet C §3: "Non-monotone: per-level results, no crossover claimed." Ruling 08 says L\* is packet C's definition restricted by M9, so this binds. Code `:233-240` takes the lowest "8B cheaper" level with any lower "1.7B cheaper" level. Probe: 81888 → L\* 3; 18188 → L\* 2; 1818n → L\* 2. (Levels 1–5: `8` = 8B cheaper, `1` = 1.7B cheaper, `n` = not resolved.) For 81888 it also contradicts 08's plain reading: the lowest 8B-cheaper level is 1, which has no lower licensing level.

## Should-fix

- **S1.** Constituents of an ESTIMATED pooled group get `status: "not estimable"` (`:209-212`, locked in by test `:162`). Packet C reserves "not estimable" for when no valid merge remains. Fix: a distinct status such as `"pooled"` with the existing `pooled_in` pointer.
- **S2.** Fallback `:241-245` sets `boundary_in_merged_group` whenever a merged group lies above any "1.7B cheaper" level, whatever its own status. Probes: `1111+[45]1` (all 1.7B cheaper) and `1nnn+[45]n` (no 8B-cheaper result) both give that reason. Test `:283-294` locks it in.
- **S3.** The M9 family is not bound to the arm: `arm off ... L* 4 ... headline True`. Fix: derive family from a registered arm-to-family map, or refuse primary for thinking-off.
- **S4.** One ceiling violation aborts the whole family, untyped: pack, requeue twice, overrun a single twice → reducer `ValueError paired models must have identical block membership`; `decide` does not catch it (`:199`). 08 F2(c) requires a typed refusal for that item; the estimator's behaviour needs specifying (recorded pairwise exclusion of the item, or the level not estimable).
- **S5.** `retry_stage` silently defaults (`scored_reduce.py:72`: rows without it yield `{'initial': 10}`); refuse rows lacking it.

## Nits

N1 `drift_lever_slots` not recomputed by `requeue_overrun`; five-level registered shape reaches 0.60 (n = 64, block 13) and 0.88 (block 8, 30 s vs 20 s), so the ≤ 0.5 grid should not size AP-5M. N2 the worst-case input is never compared with the failed prediction. N3 the incoming roster digest is trusted (bounded by D-161). N4 `pack` accepts incoherent timings (interior 900 with offset 60 and envelope 600; pitch 10). N5 `decide` hard-codes "8B"/"1.7B" role labels; a registered role→model_id map would remove relabelling. N6 survivors: `all`→`any` at `:236` (mixed merged/unmerged licensing untested); `<=`→`<` at `:83` (equality untested; behaviour correct). N7 `by_membership` (`:87-89`) lets the last entry win on a collision (2.4 vs true 2.0 in a probe; unreachable through `reduce`). N8 attempts 2 and 3 share `retry_stage: "single_problem"`.
