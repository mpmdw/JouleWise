# Interp × energy wave-1 integration — 2026-11-07

**Delivery:** local branch `interp/2026-11-07-integrated`, based on
`origin/research/2026-11-07-interp-weight-edit-energy` at `3edb715df`.
Six `--no-ff` merges landed in the requested order, followed by the package
integration commit containing this report. Nothing was pushed. All software
results below are synthetic desk evidence; native and measurement support
remain **PROVISIONAL**. Both ASTRA documents remain **DRAFT, NOT REGISTERED**.

## Authority, intake and boundaries

The user integration brief is the work selection and overrides the ordinary
queue/state-update/full-suite instructions. Read the repository AGENTS/CLAUDE
conventions, M0, targeted restart/queue sections, orchestration, the source map,
the design study, wave-1 code/tests/drafts, and relevant D-009/D-053/D-054/
D-062/D-067 provisions and the September D-078/D-083 amendments. No active
stop card was present. The tree was clean and already on the named branch.
This was a single-agent integration/static review, not an independent scientific
or final native review. No delegation or external consult was used.

No network, downloads, real measurements, Block-5 pipeline, collectors or
native MLX execution were used. No outside study-data location or real
restricted directory was opened; historical absolute paths in imported reports
were treated as text. Git's allowed object store was used for the merges.
The existing blinded analysis job was not inspected or controlled. Tests ran
sequentially with BLAS thread counts limited, well below the 20-minute budget.
`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` are unchanged relative to the starting base; no kernel
tasks were registered. Coordination remains with the lead.

**Fetch limitation:** origin is an HTTPS remote. The explicit no-network rule
precluded contacting it. Attempted:

```sh
git -c protocol.https.allow=never -c protocol.http.allow=never -c protocol.ssh.allow=never -c protocol.git.allow=never fetch origin
```

Git exited 128: `fatal: transport 'https' not allowed`. All six refs already
existed locally, so those exact heads were merged. Their freshness against
GitHub is **unverified**. This is not a successful remote fetch.

## Merge provenance and conflict resolutions

All source refs below have prefix `origin/interp/2026-11-07-`. Each merge has
the source as its second parent and records its resolution in the message.
No branch implementation was discarded to settle documentation conflicts.

| Order / source suffix | Source head | Merge | Resolution |
|---|---|---|---|
| 1 `lockin` | `40d68dfae` | `76a3a8bbb` | No conflicts. |
| 2 `weight-edits` | `328ac545d` | `1f9da2a58` | Add/add package and test initializers: shared dependency-light docstrings. |
| 3 `forced-decode` | `d02a2eea5` | `a38e0547b` | Same initializer conflicts: retain shared docstrings. |
| 4 `behaviour-channel` | `384a99634` | `ed99cb655` | Initializers as above; add/add README: preserve both replay and behaviour sections under one title. |
| 5 `rail-data-dependence` | `eb3b50161` | `66f8cdf63` | Initializers as above; retain all implementation modules. |
| 6 `astra-prereg` | `1a5b26e4b` | `6c01efcc6` | No conflicts; preserve both drafts verbatim. |

Final checks confirmed all six refs are ancestors of the integrated tree, the
merge index is clear, and no conflict markers remain in the package, scripts
or tests. The integration commit adds no new merge parent or scientific ruling.

## Package integration

The [package README](../../../joulewise/interp_energy/README.md) maps every
module to Stage 0, P/F/T, the lock-in proposal and later banked experiments.
It documents dependencies, entry points, units, hashes, cache boundaries and
compatibility limits. Use `from joulewise import interp_energy as ie`, then
module-qualified names such as `ie.forced_decode.replay`.

Changes beyond the six merges:

- `joulewise/interp_energy/__init__.py`: discoverable lazy module namespaces;
  importing all public namespaces works without NumPy, MLX, Torch or transformers.
- `joulewise/interp_energy/_common.py`: one optional NumPy loader and one
  canonical JSON digest helper. Lock-in, operands, replay, reference models,
  edits and power simulation share them; old helper import locations remain
  compatible where they existed.
- `joulewise/interp_energy/weight_edits.py`: `weights_sha256(parameters)` binds
  sorted names, dtype strings, shapes and raw-byte parameter hashes. Replay
  callers can identify the actual current edited state. This scans weights
  outside timing. Existing `parameter_sha256`/`parameter_hashes` retain their
  raw-byte semantics.
- `joulewise/interp_energy/reference.py`: uses that same aggregate identity,
  preserving the previous NumPy manifest convention; no second hashing
  implementation. `forced_decode.py` re-exports its existing canonical helper.
- `joulewise/interp_energy/rail_data_dependence.py`: canonical `MLXBackend`
  spelling; `MlxBackend` remains an alias for existing callers. Backend
  interfaces remain specific to replay versus synthetic kernels.
- `joulewise/interp_energy/lockin.py`, `operand_stats.py`, `forced_decode.py`
  and `scripts/interp_energy/power_analysis.py`: use shared helpers.
- `tests/interp_energy/test_integration.py`: four cross-component/import
  tests. Edit/revert restores identity and scores; scheduled swaps preserve
  fixed input/output IDs and create fresh caches; hashes distinguish layout,
  name, dtype and signed-zero changes while ignoring mapping order.
- `tests/interp_energy/test_forced_decode_mlx.py`: shared current-weight
  identity and a new resident swap/replay/restore test on a tiny random llama.
  Its gate now checks importability, not just package discovery.
- `tests/interp_energy/test_weight_edits_mlx.py`: also skips an OS-level MLX
  import failure; `test_mlx_native.py` uses the consistent backend spelling.
- This report. Registration and analysis-plan contents were not amended.

The CLI's **on-disk safetensors manifest** and the API's **in-memory parameter
manifest** remain distinct identity schemes with documented purposes; conflating
them would misidentify post-load edits. Likewise the statistical routines are
exploratory component APIs, not one shared registered analysis engine. Domain
validation and different statistical estimators were not collapsed into an
ambiguous generic helper.

## Static review of each wave-1 branch

These are code/document observations, not external literature verification or
hardware findings. Original branch handoff reports are historical; their test
counts and prior commit IDs do not describe this integration's verification.

### 1. Lock-in (`40d68dfae`)

**Correctness:** B−A scaling, window averaging, explicit independent-session
sizing and four-chip HAC/bootstrap units are coherent. ABBA rejects unequal
coverage/centroids; fundamental demodulation uses signed known-phase response,
not an always-positive FFT amplitude. The shared loader duplication is fixed.

**Missing evidence/tests:** coverage is tested on specified finite synthetic
noise populations, not measured nonstationarity, switching transients, actual
sampler transfer functions or cross-session drift. Those need the proposed
independent PSD/chip-length work before a native method is justified.

**Overclaim ceiling:** a synthetic variance gain is conditional on noise and
cadence assumptions; no measured lock-in improvement or 10-mW hardware bound
follows. `plan_power` is known-SD normal detection planning, not small-n t/TOST
power or a registered metrological decision. Manchester coding is not a
maximal-length PRBS. Conservative systematic bounds do not average down.

### 2. Weight edits (`328ac545d`)

**Correctness:** saved-value reversion and raw hashes handle lossy low-precision
arithmetic, signed zero and NaN payloads. Preparation precedes mutation;
callback-failure/clock rollback paths have NumPy tests. NumPy scatters changed
entries; MLX binds prepared resident arrays, with an explicit real-model callback.
Integration adds the missing aggregate current-weight identity and replay tests.

**Missing evidence/tests:** actual bf16/MLX raw views, scatter/rebinding semantics,
synchronization and callback installation are unexecuted here. A native tiny
swap/replay test is now present but still requires execution. Large-array
preparation cost/residency, tied or aliased model parameters and compiled
closures are not validated (the latter two are unsupported). Finite inputs can
still produce nonfinite edited values through arithmetic/storage overflow;
no comprehensive overflow validation is claimed. Actual Astra artifact
provenance/application and a whole-model direction-projection tool are absent.

**Overclaim ceiling:** rank-one is an update primitive, not ROME/MEMIT fitting.
Dense pruning preserves dense bytes/kernels. MLX logical changed-byte counts
do not prove O(changed-bytes) device writes, zero recompilation, or low swap
energy. Full hashes must stay outside measured spans.

### 3. Forced decode (`d02a2eea5`)

**Correctness:** prompt-except-last prefill followed by one-token calls scores
every fixed token without feeding predictions back. Native caches are obtained
fresh through mlx-lm; completion timestamps include evaluated cache states.
NumPy cached scores match independent full-context forwards. CLI loader tests
use fake modules/local synthetic files; they are not actual loader validation.

**Missing evidence/tests:** tiny native llama parity, edited resident replay,
local real-model loading and especially hybrid Qwen/DeltaNet reset remain
unverified. No energy-grade diagnostics-free measurement mode exists. See the
prefill/decode boundary conflict below. Native tests are importability-gated.

**Overclaim ceiling:** deterministic NumPy results and mocked local loading do
not establish native determinism or hybrid support. Caller-supplied digests
are assertions; file manifests do not authenticate later in-memory mutation.
Diagnostics between forwards can change total energy, timing and thermal state.

### 4. Behaviour channel (`384a99634`)

**Correctness:** total attempts' energy divided by successes, paired-ID alignment,
energy/correctness influence covariance, whole-pair resampling, midpoint
accounting and cap-mixture context averaging are consistent with the documented
model. The CLI rejects duplicate/unknown JSON fields and treats sources as
opaque strings. Zero-success draws are disclosed rather than silently dropped.

**Missing evidence/tests:** no fitted/matched calibration, measured-energy input
reducer, accuracy-binomial interval, systematic envelope, floor, registered
TOST or calibrated sparse-ratio coverage is implemented. Existing Monte Carlo
checks cover selected synthetic populations only. Repeated seeds within one
problem need another cluster design.

**Overclaim ceiling:** shared coefficients force a zero rate term; this cannot
show switching is absent. The midpoint identity is not causal mediation.
Intervals condition on coefficients and can be poor with few successes.
Published-rate scenarios are assumptions from the study, not reproduced model
results or calibrated joules. Draft ratio/context policies differ below.

### 5. Rail data dependence (`eb3b50161`)

**Correctness:** synthetic-only generation, fixed X and dispatch counts,
ABBA/BAAB scheduling, explicit affine packed quantization, separate stored/logical
statistics, dry capture rejection and owned-child cleanup are appropriate.
Mock capture tests cannot touch collectors. No independent IOReport collector
or energy reducer is provided. Backend spelling/helper duplication is fixed.

**Missing evidence/tests:** native quantization (especially zero reconstruction),
bf16 encoding, allocation/residency, timing/frequency matching and collector
startup/stop need native checks. Settings/direct-plan APIs are less defensive
than the CLI (e.g. integer-like settings are not comprehensively type-validated,
and `execute_plan` assumes a trusted `make_plan` result). Readiness confirms a
meter header, but a later early child exit is recorded as metadata rather than
a complete continuous-validity gate; callers must reject missing/gapped data.
No actual evidence validator is supplied by this diagnostic hook.

**Overclaim ceiling:** the 81.2-minute estimate includes an assumed setup reserve;
it is not a measured upper bound and cannot interrupt an in-flight dispatch.
Zero-heavy buffers, compression, DVFS and timing remain alternative mechanisms.
Sorted rows can change affine groups; low/high-Hamming fills change values too.
Tile XOR is not physical bus activity. Dry float32 execution validates neither
native bf16/int4/int8 nor switching power. `--rate 2` is the existing meter's
50-samples/s rate index, not 2 Hz; 200-ms polling is a separate cadence. Actual
delivered timing and battery/clock handling are still unverified.

### 6. ASTRA preregistration (`1a5b26e4b`)

**Correctness:** draft labels and seven unfilled slots prevent accidental
registration. The text separates gross DC+battery from rails, preserves
wrong/capped attempt energy, defines problem/reference units, proposes fixed
rosters, keeps systematic bounds separate from sampling error, and limits
causal claims. The September D-078/D-083 distinction remains material: F+B
is a planning diagnostic, not a guaranteed clearable-effect threshold.

**Missing evidence/tests:** these documents have no executable analysis/reducer
or machine-readable sealed registry. Prospective synthetic coverage must include
quad signs, gap/missingness, battery signs, systematic widening, sparse/infinite
ratios, relative floors, TOST boundaries and energy-blind reference selection.
No paper result or formal science gate was reviewed/issued here.

**Overclaim ceiling:** ±0.1% DC, the total window budget, the Astra effect and
small-n power are proposed targets/estimates. Neither commits nor passing desk
tests register a design. External source claims were not reverified in this
no-network session. The study's previously reported floors are not new ASTRA
calibrations. Draft-to-code mismatches require prospective lead decisions.

## Draft-to-code compatibility / open decisions

| Issue | Current code versus draft | Disposition / recommended next step |
|---|---|---|
| Decode boundary | Replay uses p−1 prefill tokens and D one-token forwards. REG §3 T and AP §§3–4 use full prompt prefill and D−1 decode calls. Both consume p+D−1 IDs overall, but phase accounting and first-token execution differ. | Preserve replay's tested policy. Lead must pin one measurement convention and test its exact phase edges before T calibration/registration. |
| Replay diagnostics | Replay computes normalized log-probabilities, top-k and host diagnostics between forwards; draft T discards logits. | Treat this as a validation primitive. Specify and implement an energy-grade execution/diagnostics policy before measuring. |
| Behaviour formula | Code uses d and p*d+d*(d−1)/2, with optional idle duration; AP §6 uses K=D−1 and sum(P+t), fresh gross fitting and no duration covariate. | Do not reuse coefficients between conventions. Lead must choose the registered model; the desk predictor is not AP §6. |
| Zero successes | Code returns null and withholds bootstrap CIs with undefined draws. Draft uses infinite EPC endpoints and special edited/base-ratio rules. | Keep conservative exploratory API semantics. Implement/test the draft's measured-energy estimator separately if adopted; do not report these as equivalent analyses. |
| P ladder scope | Defaults sweep 13 conditions × 4 dtypes × 2 geometries; REG P proposes a smaller bf16 ladder. | Freeze a prospective subset, counts and budget under OPEN[A-3]; defaults are not the registered P manifest. |
| End-to-end runner | No free-generation/scoring runner, Astra-diff verifier, calibrated reducer, complete evidence gate or release custody is integrated. | Stage 0 primitives only. Complete the seven draft slots and missing tools before live use. |

These are not blocking ambiguities for merging the desk components. They are
**blocking for claiming that this package executes the proposed ASTRA plan**.
No registration, estimator choice, margin change or measurement window is
silently installed by integration.

## Sandbox verification

Every non-MLX `tests/interp_energy/test_*.py` module ran in its own Python
process, sequentially. Both final runs used this command form, with `MODULE`
replaced by each full module name in the table:

```sh
PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 python3 -B -s -W error -m unittest tests.interp_energy.MODULE
PYTHONNOUSERSITE=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 OMP_NUM_THREADS=1 python3.13 -B -s -W error -m unittest tests.interp_energy.MODULE
```

| MODULE | Python 3.14.6 / NumPy 2.2.6 | Python 3.13.18 / no NumPy |
|---|---:|---:|
| `test_behaviour_channel` | 25 passed | 25 passed |
| `test_behaviour_energy_cli` | 7 passed | 7 passed |
| `test_capture_hooks` | 5 passed | 5 passed |
| `test_coverage` | 3 passed | 3 skipped |
| `test_forced_decode` | 14 passed | 14 passed |
| `test_integration` | 4 passed | 1 passed, 3 skipped |
| `test_lockin` | 12 passed | 12 skipped |
| `test_operand_stats` | 6 passed | 6 skipped |
| `test_power` | 9 passed | 9 passed |
| `test_power_simulation` | 3 passed | 3 skipped |
| `test_rail_data_dependence` | 11 passed | 6 passed, 5 skipped |
| `test_reference` | 9 passed | 9 skipped |
| `test_weight_edits` | 45 passed | 45 skipped |
| `test_weight_edits_import` | 1 passed | 1 passed |
| **Total** | **154 passed; 0 skips/failures** | **68 passed; 86 skips; 0 failures** |

Final sequential run wall times: **20.70 s** and **9.50 s**. The pre-edit
Python 3.14 baseline was 150 passing tests in 21.89 s; the new four-test
integration module also passed separately. Total unittest execution stayed
under one minute, excluding trivial process startup differences. Python 3.11
was not run. Numerical execution on supported CI Python 3.11/3.13 remains
unverified without an existing NumPy installation; no dependency was installed.

Additional checks:

- `PYTHONNOUSERSITE=1 python3.13 -B -s -m compileall -q joulewise/interp_energy tests/interp_energy scripts/interp_energy` — passed, including native-test syntax without importing MLX.
- `git diff --check` — passed.
- Ancestor/merge-order, protected-file equality, conflict-marker and local README/report link checks — passed.
- Full suite, sharded suite, quick suite, b5 pipeline, native tests and hardware captures — **not run**, per the brief. Tests use unittest, not pytest.

## Native checks the lead must run

No native MLX module was executed in this integration session; do not read
these as sandbox skip results. Run outside the sandbox on an authorized
Metal-capable **non-measurement** machine, with existing dependencies, one
module per process and tiny synthetic weights/configs only:

```sh
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v
python3.13 -B -m unittest tests.interp_energy.test_mlx_native -v
```

Expected discovery: **8 + 5 + 2 = 15 tests**. Check that they execute rather
than skip. They cover low-precision edit/restoration, resident tensor swaps,
synchronization, tiny llama generation/full-forward/replay parity, the new
swap/replay bridge, cache offsets, all tiny synthetic ladder formats and bf16
rounding. They do not validate the real Qwen hybrid, telemetry or a live window.
Passing them does not authorize a measurement or model download.

## Exact next handoff

1. Lead reviews this local integrated head and its code/docs; independent
   final-head/native/scientific review is not claimed by this single-agent run.
2. When network is separately permitted, verify source-ref freshness against
   origin. Do not claim the blocked fetch succeeded or push this branch here.
3. Run the three tiny native modules above and numerical tests on supported CI
   interpreters with NumPy already available. Preserve PROVISIONAL labels.
4. Resolve the compatibility table and OPEN[A-1]…OPEN[A-7] prospectively before
   constructing an ASTRA execution kit. Downloads, hardware windows, calibration
   and release remain lead/Ed-owned; none is needed to review this desk merge.
