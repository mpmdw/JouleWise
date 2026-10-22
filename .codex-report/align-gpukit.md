# align-gpukit

## SUMMARY

Continued the pushed gpukit lane from b8dbd1f3de61610221b80c4f02fafbd4f80ec039.
Fixed temporary runner imports in the test fixture and strengthened the nonempty MoE/router checks.
Made --skip-install reuse the existing session venv and its vLLM executable.
Replaced invented rates with dated NVIDIA/Hugging Face inputs and derived single-stream BF16 ceilings.
Added wall-time/GPU-hour/cost lower bounds; planning estimates stay null without sourced efficiency.
Added a provisional per-model adapter to the runner lane's documented CLI; budget retains its custom driver.
The lane now contains 17 authored offline tests, source-aware validation and an updated internal runbook.
No shell or Python execution was available; no final-head test pass or hardware result is claimed.
All writes stay in the lane allowlist; PR #521 remains draft and no hardware was rented.

## FILES

- joulewise/align/gpukit/__init__.py: existing package purpose, no eager heavy imports.
- joulewise/align/gpukit/bootstrap.sh: pinned vLLM/repo install; existing-venv interpreter and PATH selection on repeat sessions.
- joulewise/align/gpukit/session.py: whole-GPU check, module-name NVML preflight, endpoint/runner lifecycle, output flags, receipts, manifest/archive and copy-back; default runner CLI/settings integration.
- joulewise/align/gpukit/matrix.py: v2 matrix validation and row expansion; dated-source and efficiency checks.
- joulewise/align/gpukit/matrix.schema.json: v2 local format with physical source values, nullable efficiencies and nullable planning times.
- joulewise/align/gpukit/throughput.py: single-stream BF16 ceilings and two-significant-digit presentation.
- joulewise/align/gpukit/cost.py: fresh-generation/monitor accounting, physical work lower bounds, conditional planning and supplied-price costs.
- joulewise/align/gpukit/runner_adapter.py: provisional per-model translation, required factory names and run limits, budget dependency flags.
- configs/align/shade.json: five public task pairs, two conditions, two models, three seeds; 60 requested/fresh episodes and 180 monitor calls.
- configs/align/moe_stage_a.json: corresponding MoE repeat; 30 requested/fresh episodes and 90 monitor calls.
- configs/align/budget.json: four models, 32 item slots, 11 conditions and three seeds; 4,224 trial rows, 5,760 fresh generation episodes and 4,224 monitor calls.
- tests/align/test_gpukit.py: 17 authored unittest methods; source/hand arithmetic, shell repeat-session path, realistic Episode output, nonempty missing-router case, adapter keys and failure receipts.
- docs/align/gpukit.md: source derivations, approval inputs, default/custom runner usage, repeat-session interpreter behavior, packaging and recovery.
- .codex-report/align-gpukit.md: this report.
- Registry exceptions: none. tests/test_shard_tests.py and all other out-of-scope paths are unchanged.
- docs/align/PIPELINE.md, joulewise/align/records.py and joulewise/align/interfaces.py are unchanged.

## PUBLIC API

All Python modules below are under joulewise.align.gpukit.

- matrix.Run(model: str, task_pair: str, condition: str, seed: int)
- matrix.expand(matrix: Mapping[str, Any]) -> tuple[Run, ...]
- matrix.validate(matrix: Mapping[str, Any]) -> tuple[str, ...]
- matrix.load_matrix(path: Path) -> tuple[dict[str, Any], tuple[str, ...]]
- throughput.ceilings(matrix: Mapping[str, Any], gpu_class: str, model: str) -> tuple[float, float] | None
- throughput.display_number(value: float | None, *, lower_bound: bool = False) -> float | None
- cost.Estimate(gpu_class, trial_rows, measured_episodes, monitor_calls, lower_bound_wall_seconds, lower_bound_gpu_hours, lower_bound_total_usd, wall_seconds, gpu_hours, usd_per_gpu_hour, total_usd, flags)
- cost.work_counts(matrix: Mapping[str, Any]) -> dict[str, tuple[int, int]]
- cost.estimate(matrix: Mapping[str, Any], gpu_class: str, *, usd_per_gpu_hour: float | None = None) -> Estimate
- cost.printable(result: Estimate) -> dict[str, Any]
- cost.main(argv: list[str] | None = None) -> int
- runner_adapter.runner_matrix(matrix: Mapping[str, Any], *, model: str, endpoint: str, output_dir: Path, settings: Mapping[str, Any]) -> tuple[dict[str, Any], tuple[str, ...]]
- runner_adapter.write_runner_matrix(path: Path, matrix: Mapping[str, Any], *, model: str, endpoint: str, output_dir: Path, settings: Mapping[str, Any]) -> tuple[str, ...]
- session.SessionOptions(matrix, output, runner_command, ready_timeout_s, poll_s, command_timeout_s, preflight_command=(), ready_command=(), vllm_command=("vllm",), gpu_index=0, port=8000, destination=None, copy_kind="rsync", runner_settings=None)
- session.whole_gpu(*, gpu_index: int, timeout_s: float) -> dict[str, Any]
- session.wait_ready(process: subprocess.Popen, endpoint: str, *, timeout_s: float, poll_s: float, ready_command: Sequence[str], log: Path, probe: Callable[[str, float], bool] = _healthy) -> tuple[str, ...]
- session.package_results(directory: Path) -> tuple[Path, Path]
- session.verify_manifest(directory: Path) -> tuple[str, ...]
- session.copy_back(paths: Sequence[Path], *, kind: str, destination: str, log: Path, timeout_s: float) -> tuple[str, ...]
- session.run_session(options: SessionOptions, *, probe: Callable[[str, float], bool] = _healthy) -> dict[str, Any]
- session.main(argv: list[str] | None = None) -> int

CLI default runner: <session-python> -m joulewise.align run --matrix {runner_matrix}.
CLI adds --runner-settings PATH; custom --runner-command JSON_ARGV remains supported.
For Python callers, runner_command=() chooses the default with supplied runner_settings.

## TESTS RUN

This continuation seat executed no shell commands, Python tests, installs or hardware work.
The initial and later exec_command attempts with command text:

    pwd
    python3 --version

both failed before process launch: "No usable execution environment is available."
The cloud-environment runtime skill/status reported observed phase pending and
connectivity offline. Connected GitHub tools performed all commits and fast-forward
branch updates. Public web documentation was read for citations; tests make no network calls.

Current-head requested runs (not executed; counts and skips are unavailable):

| Environment | Exact requested command from repo root | Outcome |
|---|---|---|
| Uninstalled source, no external PYTHONPATH | python3 -m unittest tests.align.test_gpukit -v | NOT RUN: no executor |
| Uninstalled source, no external PYTHONPATH | python3 -m unittest discover -s tests/align -t . | NOT RUN: no executor |
| Throwaway venv with jsonschema, uninstalled repo, no external PYTHONPATH | python3 -m unittest tests.align.test_gpukit -v | NOT RUN: no executor |
| Same extra-dependency venv | python3 -m unittest discover -s tests/align -t . | NOT RUN: no executor |

No pip install was possible. The optional test still uses skipUnless(find_spec("jsonschema"),
"optional jsonschema is not installed"); this is its defined skip reason, not an observed skip.
There are 17 test methods by source inspection; this is not a test-run count.
The repository-wide command python3 -m unittest discover -s tests also could not execute.
No passing current-head CI result is claimed or awaited.

Static checks actually performed in this seat:
- GitHub compare confirmed every continuation change is within WRITE_SCOPE.
- Read back all 13 changed files at checkpoint 5e264d2 and compared their content
  with the authored strings: all matched exactly. This is a remote-write custody
  check, not Python verification.
- The read-only documentation-consistency agent required by AGENTS.md inspected
  the report/runbook, test inventory, config bounds/null plans and CLI/settings
  at 5e264d2. It found no concrete inconsistency. It executed no tests and is not
  an independent executing or cross-model arithmetic review.
These static checks caught no additional number-changing issue.

Director evidence supplied in the continuation brief, on the OLD b8dbd1f head,
macOS/Python 3.13.1 (not executed by this seat):

- python3 -m unittest tests.align.test_gpukit -v: Ran 12; FAILED (failures=2, skipped=1).
  Skip reason: optional jsonschema is not installed. Both failures came from the
  temporary runner's ModuleNotFoundError: No module named 'joulewise'.
- With PYTHONPATH=<repo root>, python3 -m unittest discover -s tests/align -t .:
  Ran 16; OK (skipped=1). This proves the reported baseline fixture import cause,
  not the correctness of this continuation's new cost or runner changes.

The lead owns the known tests/test_shard_tests.py discovery-census mismatch;
it is not a scope blocker for this seat and no permission request remains pending.
Independent executing review, merged-tree suite, green final CI and cold final pass
remain NOT RUN. PR #521 stays draft and is not merge-ready.

## END-TO-END

No current-head session executed, so there are no observed episode counts,
integrals, wall times, archive checks or router flags to report from this seat.
The director's old-head discovery run above is the only supplied successful
execution evidence; it did not supply per-episode observations. No fixture design
number is presented here as an observed result.

The repaired end-to-end test runs Bash bootstrap -> production session ->
stub NVIDIA XML/preflight/vLLM -> a subprocess fixture writing real shared
Episodes -> production read_episodes validation -> manifest/archive/local copy ->
byte verification and intentional mutation detection. The fixture is multi-turn,
contains tool calls, and samples a synthetic power trace at an NVML-shaped cadence.
It now supplies the source-root import path only inside SessionTests and restores
the original environment afterward.

The Stage A test additionally requires successful subprocess completion,
reads the episode file and checks every requested row exists with power and no
RouterLog before checking episode_router_log_missing and data_complete=False.
The repeat-session shell test invokes --skip-install from a non-repository cwd
using the venv created by its preceding fake installation; it rejects any repeated
pip/venv call. These checks are authored, not observed passes.

The runner adapter's key test follows the sibling lane's documented format.
Default-runner session tests preserve translated matrices and missing-integration
flags; they do not claim to test the missing runner implementation or factories.

## DECISIONS I MADE

- Continue from the actual existing remote head b8dbd1f; use connected GitHub writes
  because the executor is unavailable. Push small forward-only commits to the
  gpukit branch, never main or another lane.
- Follow the cloud-environment runtime skill for environment diagnosis. No runtime
  credentials were read or printed.
- Preserve the exhaustive write scope and shared records/protocols. Read the lane
  report and shared contracts before writing; inspect AGENTS, M0 and intake.
  TASK_QUEUE.md is empty on this branch; explicit user lane direction controls work.
- Fix only the fixture import environment for the director's reported bug. No
  production PYTHONPATH workaround was added to session.py.
- Make a prepared session venv win on --skip-install, including PATH for vLLM.
  Without one, JOULEWISE_PYTHON/system python remains a documented prepared-env fallback.
- Replace the local planning format with v2 because throughput inputs changed shape.
  This is lane-local; no shared contract version changes.
- Name GPU form factors exactly. Use dated NVIDIA-authored datasheets and Hub model
  cards, with accessed date 2026-10-22 in each physical-input citation. H100 and L40S
  datasheets were accessible through public hosts carrying NVIDIA's documents;
  NVIDIA product specification pages corroborate their values.
- Use dense BF16, not sparse or FP8, and decimal bytes/second. H100 dense BF16 is
  its 1,979 sparse TFLOPS divided by two, as the datasheet states. L40S uses the
  printed dense value 362.05 TFLOPS rather than deriving it from its inconsistent
  sparse value. These are specifications, not observed throughput.
- Use the brief's single-stream ceiling: bandwidth/(active P * 2 BF16 bytes) for
  decode and dense BF16 FLOP/s/(2 FLOPs * active P) for prefill. Exclude KV reads
  and context-dependent attention FLOPs, so the rates are optimistic under the
  stated model. Do not infer batch or tensor-parallel performance.
- Retain total parameter counts as well as active counts. A BF16 MoE's total weights
  exceed L40S memory; record that flag without deleting rows or refusing.
- Sum all fresh generations and local monitor work for the lower bound. Count budget
  calibration and paired generations; deletion controls reuse generation energy.
- Exclude arbitrary setup, loading, waits and router allowances from the physical
  lower bound. Retain them only as explicit operator planning parameters.
- Leave every efficiency/source null. No matching public efficiency measurement has
  been established. Require a dated public source when the operator supplies one;
  a bare scenario number cannot produce a planning estimate.
- Return full-precision arithmetic in cost.estimate; serialize derived times/hours/costs
  at two significant digits (least precise model counts), bounds downward and plans
  nearest. Hand arithmetic tests independently expand the sourced closed form at
  the brief's 1e-6 relative agreement bar, with comments deriving each input.
- Config lower-bound seconds, in A100-SXM4/H100-SXM/L40S-PCIe order, are SHADE
  2,800/1,700/6,500; MoE 830/490/1,800; budget 91,000/54,000/210,000.
  These were calculated while authoring configs in JavaScript, not by executing
  the Python estimator. All planning values remain null. No rental budget is claimed.
- Keep prices empty and operator-supplied. No provider quote or spend approval is inferred.
- Read the sibling runner lane docs/code to match factory/config, outer task_pair,
  output_dir and CLI conventions. Implement only a lane-local provisional adapter,
  with factory names, imports and run limits required from the operator.
- Budget conditions cannot be mapped to Episode.condition, which permits only
  benign/sabotage. Record budget_runner_adapter_required and retain the original
  matrix; use an explicit budget driver argv instead of relabeling conditions.
- Keep vLLM router capture a dependency. A router_logging request is not a RouterLog;
  session checks the actual shared-record output.
- Preserve the original public SHADE pair bindings, budget condition accounting,
  vLLM 0.10.2 reproducibility pin, process-group cleanup and immutable bundle flow.
  None establishes real CUDA/NVML/endpoint compatibility.
- Leave tests/test_shard_tests.py to the lead, as explicitly instructed; do not
  request scope expansion or wait for its quick-tier failure to be repaired.
- Retain draft PR #521 and report unexecuted verification plainly.

## CONTRACT-CHANGE

none for PIPELINE.md, records.py or interfaces.py.
The lane-local matrix schema is now v2. Budget effort conditions remain metadata
outside shared Episode.condition; no cross-lane contract extension is requested.

## OPEN ISSUES

- Current-head Python/shell tests and the jsonschema-extra reruns require the
  director's executable checkout. Execute the four requested runs with the repo
  uninstalled and no external PYTHONPATH, then record actual counts/skips and
  end-to-end observations; do not infer them from this report.
- Runner integration is provisional until its lane merges. The SHADE endpoint,
  sampler, monitor/tokenizer factories and public dataset bindings need a reviewed
  settings file and integrated offline rehearsal before rental.
- Budget needs its own integrated driver, immutable item bindings and condition
  support on the different-attention model. Default runner translation records
  this dependency without running a mislabeled campaign.
- vLLM router capture remains unimplemented in the sibling integration; eager HF
  router hooks do not establish vLLM worker coverage.
- Real GPU tenancy, CUDA/vLLM installation, NVML behavior and factory compatibility
  remain unverified. Ed must approve provider and spend before any paid session.
- Source ceilings are bounds for the stated idealized BF16 stream. Planning remains
  unavailable until appropriate cited efficiencies are supplied; workload volumes,
  setup/load/router allowances, model/tokenizer revisions and pilot size still
  need operator review. L40S cannot hold the MoE's BF16 weights as configured.
- The lead owns the repository discovery census and all executing/cross-model
  verification and merge gates. No final-head green CI claim is made.

## NEEDS_RULING

none.
