# align-gpukit

## SUMMARY

Built a stdlib-only, build-only whole-GPU campaign planning and session kit.
Added SHADE (60 episodes), MoE Stage A (30 episodes), and budget (4,224 trial rows / 5,760 fresh generations) matrices.
Added explicit throughput/overhead parameters and GPU-hour costing with no embedded prices.
Added Ubuntu bootstrap with a vLLM 0.10.2 pin, NVML preflight invocation, endpoint lifecycle and runner-command adapter.
Added shared-record output checks, SHA-256 manifests, archives, and rsync/S3/local copy-back.
Added 12 offline shell/session, cost and schema tests plus an internal approval/recovery runbook.
Shared PIPELINE.md, records.py and interfaces.py are unchanged; no hardware, rental or paid API was used.
Implementation is pushed, but verification is blocked by unavailable cloud execution and the existing shard-discovery census mismatch.

## FILES

- joulewise/align/gpukit/__init__.py: package purpose; no eager optional dependencies.
- joulewise/align/gpukit/matrix.py: matrix expansion, stdlib validation and recorded format flags.
- joulewise/align/gpukit/matrix.schema.json: local JSON Schema because the runner format is absent from the spine.
- joulewise/align/gpukit/cost.py: fresh-generation/monitor counts, serial wall time, billed GPU-hours and supplied-price costing.
- joulewise/align/gpukit/session.py: isolation inventory, preflight, endpoint lifecycle, runner argv adapter, output checks, receipts, archive integrity and copy-back.
- joulewise/align/gpukit/bootstrap.sh: executable Ubuntu/Python-venv install/session wrapper with pinned vLLM.
- configs/align/shade.json: five public pairs, two conditions, two models, three seeds; 60 episodes and 180 monitor calls.
- configs/align/moe_stage_a.json: corresponding MoE subset with router-capture request; 30 episodes and 90 monitor calls.
- configs/align/budget.json: four models, 32 explicit item slots, 11 conditions, three seeds; calibration/pair/deletion accounting.
- tests/align/test_gpukit.py: 12 authored tests, including the full shell/session fixture; optional jsonschema test skips if absent.
- docs/align/gpukit.md: internal setup, estimate derivation, approvals, integration contract, recovery and verification runbook.
- .codex-report/align-gpukit.md: this report.
- Registry exceptions used so far: none. No out-of-scope file has been changed.

## PUBLIC API

- matrix.Run(model: str, task_pair: str, condition: str, seed: int)
- matrix.expand(matrix: Mapping[str, Any]) -> tuple[Run, ...]
- matrix.validate(matrix: Mapping[str, Any]) -> tuple[str, ...]
- matrix.load_matrix(path: Path) -> tuple[dict[str, Any], tuple[str, ...]]
- cost.Estimate(gpu_class, trial_rows, measured_episodes, monitor_calls, wall_seconds, gpu_hours, usd_per_gpu_hour, total_usd, flags)
- cost.work_counts(matrix: Mapping[str, Any]) -> dict[str, tuple[int, int]]
- cost.estimate(matrix: Mapping[str, Any], gpu_class: str, *, usd_per_gpu_hour: float | None = None) -> Estimate
- cost.main(argv: list[str] | None = None) -> int
- session.SessionOptions(matrix, output, runner_command, ready_timeout_s, poll_s, command_timeout_s, preflight_command=(), ready_command=(), vllm_command=("vllm",), gpu_index=0, port=8000, destination=None, copy_kind="rsync")
- session.whole_gpu(*, gpu_index: int, timeout_s: float) -> dict[str, Any]
- session.wait_ready(process: subprocess.Popen, endpoint: str, *, timeout_s: float, poll_s: float, ready_command: Sequence[str], log: Path, probe: Callable[[str, float], bool] = _healthy) -> tuple[str, ...]
- session.package_results(directory: Path) -> tuple[Path, Path]
- session.verify_manifest(directory: Path) -> tuple[str, ...]
- session.copy_back(paths: Sequence[Path], *, kind: str, destination: str, log: Path, timeout_s: float) -> tuple[str, ...]
- session.run_session(options: SessionOptions, *, probe: Callable[[str, float], bool] = _healthy) -> dict[str, Any]
- session.main(argv: list[str] | None = None) -> int

## TESTS RUN

Local execution: none. Repeated exec_command requests for pwd failed with
"No usable execution environment is available." The selected managed runtime
remains pending/starting with connectivity offline. It has no retained
diagnostic records. No shell checkout, local test, pip installation or local
Git mutation could run; connected GitHub tools were used for all branch writes.

Requested commands still awaiting an executable environment:

- python3 -m unittest tests.align.test_gpukit -v
- python3 -m unittest discover -s tests/align -t .
- python3 -m unittest discover -s tests
- python3 scripts/fixture_orphan_census.py --fail-on-orphans

Remote fallback: draft PR https://github.com/mpmdw/JouleWise/pull/521 against
lane/2026-10-21-align-spine, never merged.

CI run 39703500845 at implementation head 9507a4bb091557014cba3f00292910ea4194b563:

- python -m build: PASS (wheel and sdist); no unit-test count.
- Installed-wheel smoke: PASS; no unit-test count.
- Repository fences (state, pins, docs, receipts, CLI/mock smokes): PASS.
- python3 scripts/quick_suite.py --tier quick --workers 4:
  212 modules selected, 176 excluded, one module failure; run canceled on the next push.
  The recorded failed module was tests.test_shard_tests, 4 tests, 1 failure,
  0 errors, 0 skips. Its discovery census compares tests.align.test_records
  and tests.align.test_gpukit with align.test_records and align.test_gpukit.
  This includes the pre-existing spine records test, not only the new test.
- Full-suite jobs were canceled without executing because the quick prerequisite
  did not pass. The gpukit tests were not selected by the quick tier's unknown-weight policy.

CI run 39703855656 at implementation head 11e36a8dfde4075d68d3c0eafa5dc2b9d82ff783:
build, installed-wheel and repository fences PASS; quick tier still pending at
this report checkpoint. The same census failure is expected until its helper is fixed.

Final lane delta after those CI starts: readiness command timeout uses the remaining
load budget rather than the polling cadence, and tests check data_complete.
This delta has not executed. No green final-head test claim is made.

The separate gate-ledger workflow correctly fails: independent review, merged-tree
suite, final CI and cold-review evidence are NOT-RUN. This draft is not merge-ready.
No optional dependency was installed; no extra-dependency run is claimed.
The optional jsonschema test has not yet executed, so no observed skip count is claimed.

## END-TO-END

Authored but NOT EXECUTED yet: Bash bootstrap --skip-install -> real session ->
fake nvidia-smi XML -> preflight module-name command stub -> fake vLLM process ->
runner argv fixture -> shared Episode JSONL -> production read_episodes validation ->
manifest -> tar.gz/checksum -> local copy-back -> byte/hash verification -> deliberate
one-byte-content mutation detected by manifest verification.

The planned synthetic campaign has 60 episodes across the actual SHADE matrix,
each with 12 turns, eight tool calls, 40,000 prefill tokens, 8,000 generated tokens,
148 s duration and 1,481 samples at 100 ms. Fixture power is 280 W plus alternating
+/-1 W, with 80 W reductions during eight two-second tool waits.
The analytic fixture integral is 148*280 - 8*2*80 = 40,160 J per episode;
the test compares the serialized trace integral at the prescribed 1e-6 relative bar.
These are fixture design numbers, not measured results or completed test evidence.
A second Stage A fixture requests 30 episodes and verifies that absent RouterLog
is retained as a flag. Operational failure fixtures preserve sealed evidence.
The fixture boundary is the runner command: it does not claim to test the absent
agentic runner, real CUDA/vLLM or real NVML.

Planning arithmetic was independently expanded in JavaScript while authoring
configs, then encoded in a closed-form Python test. Python execution remains pending.
For the H100 scenario the declared wall times are 10,554.756302521007 s (SHADE),
7,509.731092436974 s (MoE), and 134,532.45362637364 s (budget).
No hardware performance or scientific detection claim follows from these scenarios.

## DECISIONS I MADE

- No previous remote gpukit lane existed; branch from spine 4d47c4362352ccd8d4d904134a79f0d8260b21b5.
- Use GitHub connected tools for early and incremental commits because /workspace never became usable.
- Read AGENTS.md, targeted RUN_STATE/queue intake, playbook M0 and orchestration guidance; retain the exhaustive lane write fence.
- Keep the three shared contract files untouched.
- Define local JSON Schema plus stdlib cross-field validation because no runner docs/code exist on the spine.
- Pass the concrete integrated runner as an argv template; do not invent a parallel lane's CLI.
- Preserve operational problems as flags. Honor the brief's explicit MIG/vGPU refusal requirement; unknown isolation is flagged.
- Use immutable-source SHADE pair names from jkutaso/SHADE-Arena at 6614e77191c1f8e2d0c44c123c6f915905ebafae.
- Use the budget lane's 11 default conditions at 232e8516528cd85d94e3a24760cc85465f275664.
- Keep budget effort conditions out of shared Episode.condition (which only permits benign/sabotage); they remain matrix/budget metadata.
- Count calibration, hinted/no-hint pairs, all monitor calls and on-box setup/loading. Reused deletion energy is never fresh generation.
- Pilot size, seeds, rates, overheads and timeouts are explicit operator parameters, not inferred statistical or physical constants.
- Pin vLLM 0.10.2 as a reproducibility choice, label hardware compatibility unverified, and capture the actual environment.
- Choose Phi-3.5-mini-instruct as the different-attention comparison; flag unsupported thinking control and require immutable-config recheck.
- Leave prices empty; a real dated provider quote remains Ed's input.
- Leave unprovided model revisions and dataset bindings visibly flagged rather than fabricate immutable revisions or public data.
- Keep router capture missing when current HF eager hooks do not instrument vLLM; an endpoint option alone is not evidence.
- Stop the owned serving process group and preserve exclusive output directories.
- Separate readiness polling cadence from command-startup time: a probe command gets the remaining model-load timeout.
- Put the transfer receipt beside the sealed archive because transfer happens after hashing.
- Open draft PR 521 only to use existing CI; no merge or other-branch push.
- Do not modify tests/test_shard_tests.py without scope authorization: its needed logic change is wider than adding new names to a registry.

## CONTRACT-CHANGE

none. Lane-local adapters handle matrix inputs and runner commands.
The records Condition is benign/sabotage only, so budget effort conditions stay
outside that shared field. The runner and MoE integrations must preserve this.

## OPEN ISSUES

- Scope blocker: tests/test_shard_tests.py needs to normalize align.* module names
  to tests.align.* in its discovery census. User approval requested before changing it.
  The brief permits only minimal registry-name additions outside the lane; this
  is a helper logic change and also affects the existing spine records test.
- Cloud execution remains unavailable; no local test, extra installation or
  orphan census can be claimed.
- Full CI cannot reach the new tests until the discovery-census prerequisite passes.
- Runner, SHADE task binding, budget item binding and vLLM router-capture integration
  are absent from the spine; rehearse the concrete integrated argv before renting.
- Model revisions and the 32 budget item slots need immutable operator-supplied bindings.
- Real CUDA install, whole-GPU tenancy, NVML sensor behavior, endpoint controls and
  vLLM router coverage remain unverified; Ed still owns provider/spend approval.
- Independent executing review, cross-model arithmetic review and merge gates remain
  lead-owned and unclaimed. No scientific result is produced by this lane.

## NEEDS_RULING

none on scientific data selection or printed results. The scope authorization
request is listed under OPEN ISSUES, not presented as a scientific ruling.
