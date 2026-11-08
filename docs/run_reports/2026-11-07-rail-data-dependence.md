# Rail data dependence — desk implementation handoff

Date: 2026-11-07. Branch: `interp/2026-11-07-rail-data-dependence`.
Base: `3edb715df`. Implementation commit: `0931c1747`
(`feat(interp-energy): add synthetic fixed-work operand ladder`). This report
is committed separately as the local handoff record. No push or merge.

## Scope and authority

Read the two requested interp × energy study/check documents, targeted M0
intake, the inactive stop card, queue fences, repository conventions,
source-of-truth map and D-003/D-009/D-050. The explicit user brief selects
this later-research desk task and overrides ordinary queue selection and
coordination-file closure. The requested branch already existed on entry,
at the study commit, with a clean working tree; it was used as supplied.

No coordination state, existing measurement code, registrations or decision
entries changed. No kernel task registered. No network, model download,
measurement-data access, block-5 analysis, hardware capture or full suite.
No external data paths cited in repository text were followed. All executed
workloads/tests used tiny synthetic arrays, and collector tests used mocks.
No agents were delegated and no external judgment consult was requested.

## Delivered files

- `joulewise/interp_energy/__init__.py`: optional-dependency package boundary.
- `joulewise/interp_energy/operand_stats.py`: NumPy storage popcount per
  element, numerical-zero fraction, aligned consecutive-tile XOR density,
  bf16 round-to-nearest-even encoding/decoding and count-weighted pooling.
- `joulewise/interp_energy/rail_data_dependence.py`: synthetic fills, pure
  stdlib planning, seeded ABBA/BAAB scheduling, NumPy dry backend, lazy MLX
  GPU backend, fixed-dispatch timing, whole-ring calibration, budget checks,
  partial/abort retention, median timing ratios and CLI.
- `joulewise/interp_energy/capture_hooks.py`: lifecycle wrappers around the
  existing powermetrics adapter/current-era clock evidence and existing
  KM003C monitor. No new sampler or energy reducer. Native opt-in only.
- `scripts/interp_energy/rail_data_dependence.py`: direct CLI entry point.
- `tests/interp_energy/__init__.py`, `test_operand_stats.py`,
  `test_rail_data_dependence.py`, `test_capture_hooks.py`,
  `test_mlx_native.py`: fast unittest modules, all synthetic, optional
  NumPy/MLX guards, capture ownership/failure cleanup and native tiny checks.
- `docs/research-audits/2026-11-07/rail-data-dependence-DRAFT.md`: sizing,
  interpretation limits, operator commands, output schema and native gate.
- This run report.

The default pilot has eight geometry/format blocks, twelve normal-versus-fill
comparisons each, four slots per comparison: 384 slots and an **estimated
81.2 minutes** including a ten-minute setup reserve. GEMM is 2048³; GEMV
uses at least 1 GiB of distinct weight buffers per condition. Estimated
resident weights peak near 13 GiB plus temporaries/allocator overhead.
All shapes/dtypes/dispatch counts match within each comparison. Integer
full-ring cycles are calibrated once per block and held fixed across fills.
The two quantized formats use MLX's mlx-lm-style affine packed weights with
fp16 activations, not signed int8-by-int8 GEMM.

## Verification

Each command below was run separately, sequentially; all finished in seconds.
The default `python3` here is Python 3.14.6 with NumPy. Python 3.13.18 has
neither NumPy nor MLX. No dependency was installed.

| Command | Result |
|---|---|
| `python3 -B -W error -m unittest tests.interp_energy.test_operand_stats` | 6 passed |
| `python3 -B -W error -m unittest tests.interp_energy.test_rail_data_dependence` | 11 passed |
| `python3 -B -W error -m unittest tests.interp_energy.test_capture_hooks` | 5 passed |
| `python3 -B -m unittest tests.interp_energy.test_mlx_native` | 2 skipped; MLX absent |
| `python3.13 -B -m unittest tests.interp_energy.test_operand_stats` | 6 skipped; NumPy absent |
| `python3.13 -B -m unittest tests.interp_energy.test_rail_data_dependence` | 6 passed, 5 skipped; NumPy absent |
| `python3.13 -B -m unittest tests.interp_energy.test_capture_hooks` | 5 passed |
| `python3.13 -B -m unittest tests.interp_energy.test_mlx_native` | 2 skipped; MLX/NumPy absent |
| `python3.13 -B -m compileall -q joulewise/interp_energy tests/interp_energy scripts/interp_energy` | passed |
| `git diff --cached --check` | passed before implementation commit |

The dry entry-point test executes all 384 tiny slots and verifies that only
plan/timing files are written. Other checks cover ABBA drift balance,
fixed FLOP/dispatch counts, related-fill identities, storage versus logical
zeros, endianness/noncontiguous arrays, bf16 rounding, partial tiles,
dependency-free help/planning, refusal before capture when budget is spent,
and cleanup after startup/workload/collector failure. Native tests are
present but **not executed**. Python 3.11 was not exercised.

During development the local NumPy BLAS matmul emitted floating-point
warnings even for bounded finite tiny inputs. The dry backend now uses
NumPy's explicit float32 einsum reference contraction, bypassing BLAS; the
full dry path then passed with warnings promoted to errors. This establishes
only a functioning CPU surrogate, not anything about native matmul behavior.

The full canonical suite was deliberately not run: the user's blinded-job
machine-load restriction requires focused modules only. Tests did not call
any production analysis or collector entry point.

## Uncertainties and next step

No blocking design question was discovered. The scientific and native gates
remain open:

1. The lead must run `python3.13 -B -m unittest
   tests.interp_energy.test_mlx_native` **outside this sandbox on Metal with
   MLX and NumPy**. This checks every fill/format, quantized matmul against
   dequantized dense matmul, zero reconstruction, exact A/A′ components,
   Hamming ordering and native bf16 rounding. Installed MLX API/layout,
   numerical tolerances and all-zero quantization behavior are unverified
   here. Run the other three focused modules under that Python as well.
2. Actual allocation/residency, peak memory, warmup cost, sustainable
   throughput, frequency/thermal matching and the 81.2-minute estimate need
   native validation. The budget guard can stop a partial schedule; it cannot
   interrupt an in-flight GPU dispatch. Do not treat setup reserve as measured.
3. Collector startup/shutdown and current-era evidence integration were
   validated with mocks only. No independent IOReport collector was added;
   powermetrics is the existing software rail path. A separate IOReport arm
   still needs the lead's approved tooling if wanted.
4. Extreme Hamming fills also alter numeric values/sign. Sorted rows preserve
   dense histograms but may change affine group quantization. Masked zeros
   may not remain exact zeros after quantization; actual dequantized and
   packed/scales/bias statistics are reported separately. Tile XOR is a host
   placement proxy and never an observation of physical switching.
5. Timing changes, compression/zero-line handling, DVFS and software rail
   modeling remain alternative explanations. The draft requires later review
   of timing ratios, raw frequency/residency, thermal state, CPU contention,
   A/A′ and DC/clock validity. There is no estimator, transferred floor,
   energy result or claim-bearing validation in this implementation.

After the tiny native software checks, the lead can review the draft and
choose a prospectively sized, authorized quiet-Mac pilot with agents stopped.
No quiet-Mac work may be continued from this desk session.
