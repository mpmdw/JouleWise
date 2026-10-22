# Whole-GPU campaign kit (internal, build only)

Status: PROVISIONAL. No rental or hardware measurement is authorized by this kit.
Ed must approve the provider and spend before anyone starts a paid session.
Power counts work; it cannot identify what one forward pass computes.

## What is supplied

- configs/align/shade.json: five public SHADE pairs, benign/sabotage,
  Qwen3-8B and Qwen3-30B-A3B, three seed slots: 60 episodes.
- configs/align/moe_stage_a.json: the same pairs, conditions and seeds for
  the MoE model: 30 episodes. Join to the MoE subset of the baseline by
  task, condition, model and seed. This is an instrumented repeat.
- configs/align/budget.json: Qwen3-4B/8B/14B and Phi-3.5-mini-instruct,
  whose multi-head attention contrasts with Qwen3's grouped-query attention.
  There are 32 item slots, three seeds and 11 conditions: thinking on/off,
  concise, budgets 1/0.6/0.4/0.3 of the per-item median, and four matching
  random-deletion controls. This means 4,224 trial rows, 5,760 fresh
  generation episodes including calibration and paired no-hint generations,
  and 4,224 monitor calls. Deletion reuses generation energy.
- gpukit/matrix.schema.json describes the lane-local input format;
  matrix.validate adds expansion-count checks. No runner format exists
  on the spine at the build base.
- bootstrap.sh and session.py install and orchestrate serial campaigns.
- cost.py calculates serial wall time, GPU-hours and a supplied hourly price.

The five public pair names come from jkutaso/SHADE-Arena at
6614e77191c1f8e2d0c44c123c6f915905ebafae: american_airlines_2,
api_key_calendar_agendas_2, bank_transfer_2, expenditure_accounting,
spam_filter_update. No upstream source is vendored.

## Estimate and approval

All throughput, setup, model-load, token-volume, tool-wait and router-overhead
values are operator-editable planning parameters authored on 2026-10-22.
They are NOT measured performance or vendor claims. Each parameter group has
a source string saying this. Replace them using the approved hardware profile
and preflight observations; preserve the plan and actual receipt.

For each model the estimate is:

    fresh episodes * (prefill tokens / prefill tokens per second
                      + decode tokens / decode tokens per second
                      + tool wait seconds + host overhead seconds)

Stage A multiplies that by 1 + router_overhead_fraction. Add monitor calls
at their own model's throughput, setup, and (2 * model count + 1) model loads.
The latter is a conservative serial agent/monitor swap plan. Actual runner
scheduling can differ; it must not run a competing monitor on the sampled GPU
during an agent episode. Multiply wall seconds by every allocated GPU and
divide by 3,600 for billed GPU-hours. No batching, overlap or free installation
is assumed.

The committed scenario gives these hours on one GPU, rounded for planning.
These are model calculations, not hardware evidence.

| Matrix | A100 80 GB | H100 80 GB | L40S 48 GB |
|---|---:|---:|---:|
| SHADE | 4.16 | 2.93 | 4.44 |
| MoE Stage A | 2.90 | 2.09 | 3.09 |
| Budget | 61.27 | 37.37 | 66.69 |

Use exact seconds from the estimator for approval. The budget scenario is
large enough to require an explicit pilot-size choice. Its 32 slots and
three seeds are editable inputs, not statistical recommendations.
The attention baseline may not obey Qwen-specific thinking controls;
unsupported controls remain flags.

Example prices are empty. Supply an actual quote:

    python3 -m joulewise.align.gpukit.cost configs/align/shade.json \
      --gpu-class H100-80GB --usd-per-gpu-hour "$APPROVED_HOURLY_USD"

Ed approves the provider/region, whole-GPU class/count, storage and return
destination; immutable repo/model/dataset revisions and pilot size; a dated
hourly quote, maximum billed hours and total spend; and who stops the instance.
The concrete runner/router integration must pass an offline rehearsal first.
GPU-hour estimates exclude provider storage, transfer, taxes and billing
granularity. Timeouts are operational parameters, not cost caps.
The kit does not provision, rent, terminate, or stop billing a VM.

## Integration dependency before rental

The spine contains shared records/interfaces only. Session invokes
python -m joulewise.align.power.preflight by module name, expecting the NVML
lane's module. Stdout/stderr and return code are retained in preflight.log.
A nonzero code becomes nvml_preflight_failed; evidence is retained.

Pass the integrated runner as --runner-command, a JSON argv array. Session
substitutes these fields, one model at a time:

| Placeholder | Meaning |
|---|---|
| {matrix} | Absolute path to bundled normalized gpukit matrix |
| {model} | Model ID to select from that matrix |
| {endpoint} | Loopback vLLM base URL |
| {output} | Required shared-record Episode JSONL output |
| {sample_interval_ns} | Requested NVML polling cadence |
| {router_logging} | true for Stage A, otherwise false |

The runner reads the schema, selects the named model, runs requested rows
with a PowerSampler beside every episode, and writes shared Episode records.
For budget, export fresh generation episodes only: calibration plus hinted
and no-hint generations, never duplicated deletion views. Keep trial journals
and monitor outputs beside {output}; packaging includes them automatically.
All cross-lane outputs use the shared records.

The command adapter avoids inventing the absent runner CLI. Its concrete argv
must be rehearsed on an integrated checkout before rental. Missing commands,
preflight, power, output or router logs remain recorded flags. No runner command
means no endpoint work.

The current MoE lane hooks target Hugging Face eager execution, not vLLM
workers. A vLLM router-capture bridge remains a MoE/runner integration dependency.
Session checks Episode.router_log and records episode_router_log_missing.
A populated RouterLog still needs the MoE lane's coverage validation.

Budget item slots must resolve to an immutable public item manifest through
the budget adapter; they are not invented MMLU examples. Committed model
revisions are null and flagged. Fill them with immutable Hub commit IDs,
use the same tokenizer revision, and recheck attention layouts before the
scientific run. No live compatibility or calibration claim is made for
the selected vLLM 0.10.2 install pin.

## Session procedure

Use a fresh Ubuntu 24.04-style host with NVIDIA driver, Python >=3.11, venv,
git and rsync (or AWS CLI for S3) available. Clone the reviewed integration
head. No credentials belong in files or command templates; SSH/AWS use
ambient operator authentication.

From the checkout root:

    bash joulewise/align/gpukit/bootstrap.sh --check-only

Inventory reads NVIDIA XML. Explicit MIG or vGPU refuses, as required by
the brief. Unknown/unavailable isolation information is flagged. Provider
confirmation and NVML preflight must complete the tenancy check. Session
checks the selected GPU; bootstrap's preliminary check uses GPU 0.

After the integrated offline rehearsal and Ed's approval, supply RUNNER_ARGV_JSON
as the concrete argv above and timeouts from the approved loading/campaign plan:

    bash joulewise/align/gpukit/bootstrap.sh configs/align/shade.json \
      --output /data/campaign-unique-id \
      --runner-command "$RUNNER_ARGV_JSON" \
      --ready-timeout-s "$APPROVED_MODEL_LOAD_TIMEOUT_S" \
      --command-timeout-s "$APPROVED_COMMAND_TIMEOUT_S" \
      --poll-s "$APPROVED_READINESS_POLL_S" \
      --destination return-host:/approved/results/ --copy-kind rsync

Bootstrap creates .gpukit-venv (JOULEWISE_VENV overrides it), installs
vllm==0.10.2 and this checkout, then enters session.py. --skip-install reuses
a prepared environment; JOULEWISE_PYTHON selects the initial interpreter.
No CUDA install has been tested by this build.

Session starts one agent endpoint on loopback, polls /health, invokes the
runner, and terminates its serving process group before loading another
model. Select GPU and port with --gpu-index and --port. GPU index is the
physical nvidia-smi index, exported to the child as CUDA_VISIBLE_DEVICES.
The runner owns monitor placement/scheduling and must prevent unrelated
work during sampled agent episodes.

--ready-command, --preflight-command and --vllm-command accept JSON argv arrays
for operational adapters and offline tests. Readiness commands replace HTTP
polling. Never substitute test stubs for scientific hardware preflight.

Output includes matrix, inventory/receipt, package list and Git head, preflight
log, server/runner logs, Episodes and runner sidecars. CLI exit 2 is explicit
MIG/vGPU refusal; exit 0 still requires reading flags and inspecting completeness.

## Copy-back and integrity

Existing output directories are never reused. Session hashes all regular
output files, creates a sibling tar.gz and detached archive checksum, then
copies both. Symlinks are omitted and flagged. The manifest does not hash
itself; the archive checksum covers it.

Use rsync, or --copy-kind s3 with an S3 destination and ambient AWS credentials.
The local copy kind is for offline rehearsal. Failed transfer preserves the
local archive and writes a sibling transfer receipt. This receipt is outside
the sealed archive because transfer happens after sealing. Retry the copy
from preserved files; do not rerun the campaign to repair a transfer.

At the destination use sha256sum -c on the detached checksum, extract into an
empty directory, then run:

    python3 -c 'from pathlib import Path; from joulewise.align.gpukit.session import verify_manifest; print(verify_manifest(Path("/returned/campaign-unique-id")))'

An empty tuple means inventory and bytes match. Hashes establish copy integrity,
not independent custody against an adversary who can rewrite data and manifest.
Keep an off-box copy and verify it before stopping billing in the provider console.

## Offline verification

Tests never contact a network or GPU:

    python3 -m unittest tests.align.test_gpukit -v
    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest discover -s tests

The shell rehearsal uses fake NVIDIA XML, fake vLLM and a runner fixture writing
shared records through the real session, packer and copy-back. It does not
validate the agentic runner or CUDA stack. JSON Schema tests lazily import
optional jsonschema and skip if absent. See the lane report for actual commands
and results; test descriptions alone are not evidence.
