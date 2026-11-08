# R22 cap sweep — Sol1 handoff

Branch `align/2026-11-08-r22-cap-sweep-sol`, precreated and clean at intake,
base `8f81bf7bd` (`origin/align/2026-11-08-r22-sim-sol`). This `[AGENT]`
synthetic-only task is selected by the explicit user brief, superseding
ordinary queue selection and coordination-state updates. M0 intake found
no active stop card or global selection gate. `RUN_STATE.md`, `TASK_QUEUE.md`,
`docs/process/state_kernel.json`, and `tests/test_gen_state.py` are unchanged;
no kernel task or registration policy is installed.

The [short study report](../align/v4/b3-sim/R22-CAP-SWEEP-sol1.md) explains the
model, exact availability/workload, FPR populations, paired comparisons,
calendar assumption, and limitations. The
[joined table](../align/v4/b3-sim/r22-cap-sweep-table-sol1.csv) contains all
requested settings/rules; separate full scores retain both individual pairs.

Findings: C10/C11/C12 qualify **52.5588%/71.3297%/84.2348%** at q=1/4,
e=.10. None reaches 95%; exact availability first reaches it at **C14,
96.1720%** (C14 FPR is not simulated). Matching future admission does not
remove the threshold difference versus an oracle calibrated on all states.
At b=0, increasing the cap changes supply rather than the successful
eight-window calibration law. Under positive drift, additional successful
studies calibrate later relative to the common T horizon, changing their
conditional FPR. Already-C10-qualified studies are exactly unchanged.

Across the requested b=.05 grid, C12−C10 gate-risk point differences are
−.259 to −.054 percentage points for maximum, −.420 to −.080 for rank05.
The admitted target still exceeds nominal rates in some settings: C12's
worst no-drift maximum/rank05 means are 3.368%/5.836%; with b=.05 they are
5.936%/9.783%. Larger caps do not establish nominal FPR control.

Only new files under `docs/align/v4/b3-sim/` and this report are added:
simulator extension, stdlib audit/table builder, study report, numeric tables,
metadata/audit receipts, and check/pilot/run logs. Original simulator,
helpers, and all original evidence remain unchanged. C1–C10 preserve the
original RNG stream; C11/C12 use the documented independent suffix stream.

Verification commands, run one module per process:

- `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 python3 -B docs/align/v4/b3-sim/simulate_r22_sol1.py --check`: 8 passed, .374 s baseline.
- Same environment, `python3 -B docs/align/v4/b3-sim/simulate_r22_cap_sweep_sol1.py --check`: 6 passed, .260 s. Exhaustive structural tapes, exact probabilities/attempts, no top-up, original prefix byte identity, scalar future tails, deterministic serialization.
- Same environment, new simulator `--profile`: 10,000 synthetic studies in 1.061 s, one process/thread; no performance optimization made.
- Same environment, new simulator without flags: 72 settings × 100,000 studies, both horizons. Exact qualification and iid-rank checks execute inside each setting.
- `python3.13 -B -m unittest tests.align.test_v4_estimands`: 15 passed, .002 s.
- Python 3.13 AST checks of the two new scripts: passed.
- `python3.13 -B docs/align/v4/b3-sim/audit_r22_cap_sweep_sol1.py`: validates all rows/intervals, pair means, exact counts/workload, hashes, horizons, and original-result replay; emits joined and availability tables.

The main run completed in **1,158.7 s**, one process and one numerical thread.
All **17,568** overlapping original numerical fields serialize identically
(matching digest `d6a0e5c5e1406feb1404552a2960b6d06ed8f2ee113058f50b3a1ea75f7bdca9`).
The stdlib audit passed for 288 count rows, 5,184 score rows, 864 joined rows,
and 52,992 intervals. Its initial tau=0 mixture identity assertion was made
too strict (exact decimal equality); it now permits 2e−14 absolute rounding
error for algebraically equal hot/cool mixtures. Independent-mechanism
identity and old-result replay remain exact. No numerical result changed.

Python 3.13.18 has no NumPy; numerical execution uses the available
Python 3.14.6 / NumPy 2.2.6, as in the previous simulator. An initial
large-array `np.testing.assert_array_equal` check failed from the host's
documented comparison issue despite matching shape/dtype/raw bytes. The
test now checks those bytes directly. Supported Python 3.11/3.13 + NumPy
reproduction remains required before reliance on the numerical conclusions.
No installation was attempted. No MLX or product code changed; no new native
MLX tests are owed by this artifact. Live scorer/eligibility gates remain
lead-owned.

The common T positions 13–15 after C12 are an explicit assumption. The old
11–13 horizon is retained only for compatibility, since it overlaps new
reserve slots. This is not a test-calendar ruling. All results remain
synthetic and model-dependent, with pointwise Monte Carlo intervals.

No full suite, measurement pipeline, measurement data, real restricted
directory, external user path, other-job inspection/control, network,
weights, push, merge, or external integration was used. Targeted checks
replace the canonical suite under the user's explicit machine-load rule.
No outcome summary was used as an input; the unchanged synthetic assumptions
come from the task-authorized original simulator.

Next exact step: lead confirms the admitted target and test calendar,
reproduces on a supported numerical runtime, then separately qualifies C14
FPR and detection cost if ≥95% availability is required. Actual gate/state
dependence, state persistence, dependent member exclusions, residual tails,
and native eligibility remain uncertain. No scientific policy is adopted.
