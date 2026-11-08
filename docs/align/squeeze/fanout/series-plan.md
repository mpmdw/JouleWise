# series-plan handoff

Planning date: 2026-11-08. Branch: `align/2026-11-08-v5-series-plan`.
Base: `d600baba029f70592bb8e792098338e4cd6811d3`, the locally available
`origin/lane/2026-11-08-v5-squeeze`. Local commit subject:
`docs(align): plan registration-grade v4 series and v5 test windows`.

Built [SERIES-PLAN.md](../SERIES-PLAN.md) and four non-executable planning
sheets under [configs/campaigns/align_v4/series](../../../../configs/campaigns/align_v4/series/README.md),
plus their README and `tests/test_align_v4_series_plan.py`. No existing runtime,
W1/R1 kit, protocol, decision log or coordination-state file changed.

The plan provides seven 22-member D calibration windows, the required
T1/D4/T2/D5/T3/D6 interleave, disjoint seed allocations, 30 balanced test
attempts, 12 specificity benign, six D controls and a proposed 24-member
30B physics roster. All sheets require KM003C capture beside rails and sealed
full reasoning transcripts. These requirements are **planning fields, not
implemented capture enforcement or evidence of live hardware**.

Key arithmetic: at 14% iid member exclusion, seven windows give P(m≥39) =
0.926871 per pair (both-pair independence reference 0.859090; union lower
reference 0.853742). Six give only 0.142233 per pair. Whole-window failure
and correlated exclusions can invalidate those marginals. Baseline reservation:
13 windows / 746,087 s / 207.25 h, excluding R0, turnaround and refusals;
proposed D8 and separately reported T4 add at most 33.07 h. D/T planning
maximum is 58,260 s against the 59,520 s cap. Two extra sentinels would
exceed that cap on planning costs.

Assumed binding rulings: v4 changes only by meter capture and sealed full
transcript retention; same frozen D configuration for v5; Q4/Q6 are already
approved in principle; the meter sees all wall-brick-to-MagSafe input and its
whole-member integral is small-effect authority; API frontier monitor primary,
local secondary, off-box and no scoring before registration; scoped agent
adversary only; real unmediated-compute controls; per-channel rank-m maxima
at m≥39; primary escape rate per assigned attempt, all-cells survival descriptive.
The original v4 minimum of three sabotage members per pair is preserved;
the synthesis's proposed increase to six was not silently adopted.

Verification, one unittest module per process, synthetic/repository inputs only:

| Command/check | Result |
|---|---|
| `python3.13 -B -m unittest tests.test_align_v4_series_plan` before sheets existed | Expected red: 10 missing-file errors, 0.008 s |
| Same command after implementation | PASS: 10 tests, final 0.088 s |
| `python3.13 -B -m unittest tests.align.test_v4_w1_plan` | PASS: 12 tests, 0.858 s |
| `python3.13 -B -m unittest tests.align.test_protocol_v4_doc` | PASS: 5 tests, 0.362 s |
| JSON parse, test AST parse, clone-contained Markdown link checks | PASS |
| `git diff --check` / staged equivalent | PASS |

Tests verify anchor byte hashes, cohort separation and seed ranges, role/attack
counts, controls outside runtime accounting, budget/yield arithmetic, meter and
custody requirements, and rejection of every new sheet by the real NightPlan
parser. Full suite was forbidden and not run. No MLX execution, hardware probe,
measurement pipeline, real study data, model download, network or push occurred.
Requested refs were read locally with `git show`; no fetch was attempted.
No writes to RUN_STATE, TASK_QUEUE, the kernel, or tests/test_gen_state.py.

Native follow-up is lead-owned, outside this sandbox and outside the running
blinded job. The existing tiny no-download thermal-stream test can be run there:
`JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`.
It does not qualify a real model generator, capture or injector. Before arm,
the capture/injection lanes must also supply native streaming/coverage, clock
and battery evidence, synchronized actual-work witnesses, exact visible replay
identity and per-site fit within unchanged T_dead/member caps. No new native
MLX test or hardware qualification was added on this documentation lane.

## NEEDS_RULING before registration or executable kits

- **Question:** seven fixed D windows plus D8, or the older six-window cap?
  **Options:** six; seven plus one count reserve; unbounded extensions.
  **Recommendation:** admit seven plus D8 using counts/U1–U3 only.
  **Blocked:** registration and executable schedule; plan drafting is complete.
- **Question:** which 30B roster resolves the source's inconsistent totals?
  **Options:** literal 28 total with five injections/carrier; 24 total matching
  its four-site/two-dose/two-replicate matrix and 20 science members.
  **Recommendation:** the proposed 24-member roster, qualified independently.
  **Blocked:** physics kit and native fit. The six D controls are not replicated
  by pair; do not claim site-by-pair detection rates from them.
- **Question:** how are v5 calibration and test scores made comparable?
  **Options:** justify the proposed pooled LOTO/full-fit scoring or admit a
  separately justified recipe without changing v4.
  **Recommendation:** analysis-lane ruling; m≥39 alone is insufficient proof.
  **Blocked:** nominal FPR claim and final threshold freeze.
- **Question:** does the red team know development cuts or final D7/D8 cuts?
  **Options:** the designed interleave with development feedback; a later test
  cohort after final cuts. **Recommendation:** preserve the interleave and
  explicitly scope knowledge. **Blocked:** a claim of adaptation to final cuts.
- **Question:** should count-triggered T4 enter primary inference?
  **Options:** separate follow-up; preregister a stopping-aware pooled design.
  **Recommendation:** separate unless prospectively admitted before T1.
  **Blocked:** pooled T4 confirmatory claims, not fixed T1–T3 reporting.

Next exact step: lead disposition of the SERIES-PLAN decision table, then the
owning kit/capture lanes materialize and independently review the final seed,
config, capture and sizing receipts. This run clears no live or admission gate.
