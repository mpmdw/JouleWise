# V4 primary engine — Sol run report

2026-11-08. Branch `align/2026-11-08-v4-analysis-engine-sol`, base
`9891d679b95784dc3c09e1cd146de31f62ac7840`.

**Outcome: PROVISIONAL primary engine candidate, synthetic-tested. Scientific
claim certification and complete native pipeline integration are blocked.**
The ordinary C1-C8/T1-T3 path runs end to end, emits a numeric fill with every
scalar inventoried and a structure-only verdict, and has byte-identical serial
and bounded-parallel output. No measurement corpus or outcome-bearing analysis
artifact was opened, and no native result is claimed. Pre-existing operational
summaries in the requested authority documents were read as text.

## Intake and fences

Read repository AGENTS/CLAUDE, Mission M0, targeted state/queue views,
orchestration, protocol v4 and its source pins. The checkout's coordination
views predate the requested rulings, so RUN_STATE 203-226 was read through
origin/main Git objects. The active stop card was NONE. Explicit user task
authority superseded ordinary queue selection and the full-suite/state-update
checklists. No coordination file or kernel task was written.

Only clone files, synthetic temporary artifacts, and allowed Git object reads
were used. No network, package installation, weights, real measurement data,
quiet measurement, native MLX, B5 analysis program, external user path or real
restricted directory was accessed. No running job was inspected or controlled.
No agent was spawned or external consult made. No commit was pushed.

Reference Git objects:

| Source | Ref/object |
|---|---|
| Intake code | `9891d679b95784dc3c09e1cd146de31f62ac7840` |
| Lead RUN_STATE/SPEED/B5 precedents | origin/main `6b6d5a1348e1dc62d8e3dcacd3100916bdf9518e` |
| R11 agreement | `4526de7d5` Track 1 |
| R15 source allocation | dct-series-opus `f9f9f7c4c6733969f8673798a0324f40d9936de4` |
| Available merged blocker procedure | `ca3306f90fa97151239410b24a3e8832d0b7451a` |
| Frozen sequence fitter | `4d54cb47b:joulewise/align/energy_residual.py`, via `cda28a5ef` pin |

The available dct-series-merged script still generated the earlier separate
fit proposal. The engine instead implements RUN_STATE 226's adopted Opus
allocation. A static comparison against the original Opus manifest found
**242/242 routing rows exactly equal**, including episode seeds, pair,
condition, ordinal, role and held-out seed indices.

## Changed files and behavior

* `joulewise/align/v4_analysis/`: engine, explicit digest-bound reader,
  thermal/acceptance calculations, sequence adapter, unchanged pinned fitter,
  synthetic fixture generator, package entry point.
* `scripts/analyze_align_v4.py`: C-only prospective freeze, guarded full run,
  numeric fill and structure-only stdout/verdict.
* `scripts/benchmark_v4_engine.py`: synthetic 11x22 rehearsal, cProfile,
  serial/two-worker exact-byte check and timing receipt.
* `tests/align/test_v4_analysis_engine.py`: targeted analytic, attrition,
  refusal, byte-identity, sensitivity and CLI tests.
* `docs/analysis/v4/ENGINE-sol.md`: input/output contract, authority pins,
  protocol section/clause-to-function map and explicit coverage limits.
* This report; no existing acquisition, legacy estimator, protocol, config or
  coordination source was edited.

Main behavior: final membership is derived from planned rows and desk evidence;
no successful-only discovery, replacement, best-39 or outcome-driven top-up.
Captured failed windows count toward eight. Zero captures retry the same seed
slot and two consecutive refusals require a signed release. C6 requires final
prior eligibility. Charging/accumulator members are excluded individually,
other members retained, assist disclosed. Configuration/stack/policy changes
cannot pool. Per-session, per-pair benign fits are LOTO; test sabotage uses
that session's full benign fit. C sabotage counts toward nothing. Thresholds
are the prospective maximum, strict `>`, m>=39 per pair; generic ranks and the
rank-38 sensitivity are separately printed. U3/U4/U5/U6, known-H, H*, carriers,
window bootstrap, hold-count and rebuild diagnostics retain missing/undefined
states. Non-benign DC is hash-only, never a primary selection variable.

The frozen fitter copy hashes to
`d187698d5cc8a0856ffe730079e16a164a5ac338b9dd0a4b10be8cac6206acef`.
No edits were made to the original energy_residual or historical pilot paths.

## Failing-first and verification

Initial command, before implementation:

`python3.13 -B -m unittest tests.align.test_v4_analysis_engine`

**RED:** import error, `joulewise.align.v4_analysis` absent. After implementation,
the first substantive series test also caught an overly broad assertion that
forbade the word “threshold” in a fixed structural refusal code; it was corrected
to forbid a numerical threshold field. The public verdict still carries only
fixed codes and structural counts.

Development checks (not final-head evidence):

| Command | Result |
|---|---|
| New module, first implementation | 13 tests OK, 49.407 s |
| Expanded module | 19 tests OK, 45.605 s |
| CLI class | 3 tests OK, 7.029 s; no-freeze run read C only, no T exports |
| Expanded module including CLI | 22 tests OK, 53.710 s |
| Loaded-code-bound reader instrumentation rehearsal | 24 tests: one failure, 64.529 s; the test had replaced the reader after creating its freeze, so the code-change guard correctly refused it. Test instrumentation moved to the stdlib byte-read boundary; CLI class then passed 3/3 in 10.445 s. |
| ResidualTests, exact frozen score comparison included | 4 tests OK, 0.034 s |
| Python 3.11 targeted invocation | Not run: `python3.11` unavailable (exit 127) |
| compileall over joulewise/tests and new scripts | Passed; bytecode redirected to synthetic /private/tmp prefix |
| `git diff --check` | Passed |

Final-head checks/timings are appended below after completion. Tests were run
as targeted unittest modules, one module at a time. The full suite was not run
because Ed explicitly prohibited it during the separate blinded eight-worker
analysis. Total targeted test time remained far below twenty minutes.

## Speed evidence

Profile first: small synthetic inputs, 35,188,587 calls / 16.071 profiled
seconds, 13.457 s in 44 fit tasks; 4,160 wrapper predictions called the frozen
predictor twice. An exact-score test supports reusing that prediction within
the operation. There is no persistent cache of decisions, fits or refusals.

Full realistic synthetic desk size: **11 windows x 22 members x 12 turns**, full
prompt/output token ID arrays, 130,790,353 source bytes in the initial fixture.
All scenarios are synthetic. Each window's combined export is referenced twice
but hashed/parsed once (11 source reads). Parallel tasks contain compact turn
inputs; large identity arrays stay in the read-only parent evidence. Each
task's arithmetic and final reduction order match serial exactly.

| Rehearsal | Serial total | 2 workers total | Exact bytes |
|---|---:|---:|---|
| Small initial identity check | 4.459 s | 4.236 s | yes |
| Full arrays before eliminating deep copy | 18.016 s | 16.813 s | yes |
| Full arrays after sharing immutable evidence | 6.987 s | 5.507 s | yes |
| Final implementation, unprofiled | **4.331 s** | **5.091 s** | **yes** |

These were wall-clock observations under the existing external load, with no
guaranteed utilization or throughput claim. Profiling has overhead and is not
used as the speedup denominator. Parallelism itself gave a modest gain; most
of the full-size saving came from avoiding unnecessary token-array copies.

An early benchmark **failed** byte equality only at the loaded-code SHA field;
all numerical/decision leaves were equal. `marshal` object-reference/interning
encoding was runtime-sensitive. Explicit semantic code fields, default values
and scientific globals replaced it. Subsequent whole fill and verdict outputs
matched exactly. This defect and the failed rehearsal are retained here.

Temporary artifacts are synthetic and live under `/private/tmp/v4-engine-sol-*`.
Only small timing/profile summaries are committed; no generated token corpus
or large fill is committed.

## NEEDS_RULING / native handoff

1. **Question:** what admitted source owns the qualified scorer and final
   sabotage-signature claim decision? Options: qualify the supplied per-session
   LOTO/full-fit design; provide a prospectively adopted alternative and claim
   rule. **Recommendation:** keep claim held until a signed contract and the
   independent common-shift/dependence gate exist. **Blocked:** confirmatory
   claim issuance. This question was sent through the async user-input tool;
   no answer was received during this run.
2. **Question:** U3's heavy-tail trigger uses the whole-sample s0 in item 226,
   versus leave-one-out RMS in the available merged helper. **Recommendation:**
   obtain an explicit lead disposition before signing; code currently follows
   item 226 literally. **Blocked:** native U3 registration/adoption.
3. **Question:** what is the admitted +2 sentinel placement/alternate reference
   manifest? **Recommendation:** integrate the owning series lane's final
   manifest; never invent ordinals or a singleton E_ref. **Blocked:** the
   conditional 24-member route (ordinary 22-member route is implemented).

Other declared limits: U5/U6 conventions remain scientifically PENDING-FREEZE;
native exporter/session wiring is not installed; warmth/soak/wait disclosures
and a separate benign DC residual fit remain upstream. The protocol map calls
these out rather than making a complete-coverage claim.

Next exact step: lead adjudicates these contracts/manifest issues, supplies
native desk export/identity bindings and the prospective freeze record, wires
the exporter into the selected session, updates the strict registration/static
and dynamic closure, then runs Opus's **independent** recompute/comparator over
every fill leaf. No model or study data is needed to review the present patch.

Native checks not run here: Python 3.11 targeted module, MLX/Metal tests and
cache native script, real D/R1 qualification, physical battery/meter/clock/
thermal/mount checks, Stage A/B/full-desk gates at the final admitted head.
Only the lead may perform hardware gates and native arm decisions. There was
no network request, commit push, or measurement job operation.

## Final verification receipts

| Command/check | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_v4_analysis_engine` | **24 tests OK**, 85.553 s |
| `python3.13 -B -m unittest tests.align.test_v4_estimands` | **15 tests OK**, 0.014 s |
| `python3.13 -B -m unittest tests.align.test_v4_cadence` | **27 tests OK**, 1.212 s |
| `PYTHONPYCACHEPREFIX=/private/tmp/v4-engine-sol-final-compile python3.13 -B -m compileall -q joulewise tests scripts/analyze_align_v4.py scripts/benchmark_v4_engine.py` | Passed |
| Three fresh Python processes, PYTHONHASHSEED 0/1/123 | Loaded scorer identity identical: `6d69fa03df38ff0413a164701ea1d51b5221581ca677d2c77d349f66bbc80923` |
| Frozen source copy SHA-256 | Equal to original pinned Git source, digest above |
| Coordination-file diff | Empty for RUN_STATE, TASK_QUEUE, state_kernel and test_gen_state |

Implementation commit: **`f0b141ee080039a8cfbc92521e06b9d23b43cac9`**
(`align: add provisional v4 primary analysis engine`). The report and small
receipts are in the follow-up documentation commit on the same branch.

Final commands:

* `python3.13 -B scripts/benchmark_v4_engine.py --output /private/tmp/v4-engine-sol-final-bench`
  — exit 0, full-array 130,790,353-byte fixture, 11 physical source reads,
  **4.331130 s serial / 5.091412 s two-worker**, byte-identical fill/verdict.
  Serial remains the default because two workers were slower in this final
  receipt. Earlier receipts show variability under the shared external load;
  no universal parallel speedup is claimed.
  The final fill inventories **75,964 scalar leaves** for the independent
  comparator; no comparator agreement is claimed by this implementation.
* `python3.13 -B scripts/benchmark_v4_engine.py --output /private/tmp/v4-engine-sol-final-profile --profile`
  — exit 0, realistic full-size cProfile completed, 28,156,043 calls / 29.858
  profiled seconds; fits/prediction dominate. Instrumented serial total
  35.647 s versus uninstrumented two-worker 16.461 s is **not** a speedup
  comparison. The benchmark labels that overhead. All four profiled output
  files also equal the corresponding unprofiled bytes exactly.

Final output digests:

* Fill, both worker counts and with/without profiler:
  `2dd1b8bc7e717ad3969cad4ebf4a045ef7fdb92c5bfdf219692ed1ae09768cdf`.
* Verdict, all four paths:
  `b81ac4809bc0716205cd3ba9567cfc047597fc54d4d3490bd9371f53ffec7ee8`.

Small committed receipts:
[timing JSON](../analysis/v4/ENGINE-sol-synthetic-timing.json),
[synthetic profile](../analysis/v4/ENGINE-sol-synthetic-profile.txt).
No full suite or native tests ran. No push occurred.
