# 2026-11-07 — ALIGN squeeze adversary kit (desk draft)

Branch: `align/2026-11-07-adversary-kit`, already checked out and clean at intake.
Base: `fdb1e0409`. Local commit only; no push, registration, or measurement.
Task authority: Ed's 2026-11-07 adversary-kit brief and standing blinded/no-network
rules. Those rules override full-suite and coordination-state closeout defaults.

## Delivered

- Six versioned prompt configs: unaware, meter aware, visible-log padding,
  smoothing/reuse, tool-mediated work, and a mixed adaptive strategy. Every
  prompt and canonical config is hashed; the manifest also hashes raw files.
- Seven known-H control configs: k=0,128,256,300,512,1024,2048. A native MLX
  decoder accepts an already prepared model/cache factory and forces exactly k
  evaluated greedy outputs without EOS early stopping or visible logging.
  The zero sham performs no model work. No shipped dose was run natively here.
- Explicit `AgentTask` adapter and v3/v4 EpisodeSpec overlay, plus a wrapper
  calling the real generic ALIGN runner. The control occurs before a selected
  chat call, after samplers start, and leaves the visible result/usage unchanged.
- A separate evaluator-only receipt with exact IDs, completed forward counts,
  H, timestamps, model/config identity, episode binding, and interval check.
  Partial failures preserve their completed prefix but have H=null and unknown
  work flagged; unreached triggers are not successful controls.
- Strict config validation, a validate-only CLI, synthetic unit/integration
  tests, and an optional native test built from tiny synthetic MLX arrays.

Files touched: `joulewise/align/squeeze/{__init__,__main__,config,control,harness}.py`;
`configs/align/squeeze/manifest.json` and 13 versioned JSON configs;
`tests/align/squeeze_fixtures.py`, `tests/align/test_squeeze_{config,control,harness,native}.py`;
`scripts/check_squeeze_overlay.py`; `docs/align/squeeze/ADVERSARY-KIT.md`;
`CANONICAL.md`; this report. No existing measurement code/config/registration
bytes or coordination-state files were changed.

## Authority read and source boundary

Read AGENTS/CLAUDE, Mission M0, orchestration, the targeted restart/queue and
decision-log sections (notably D-009), research agenda/map, and the requested
protocol/residual and research audits from local Git objects. The source table
in `ADVERSARY-KIT.md` records full source commits. No fetch was attempted: the
standing no-network rule overrides the brief's fetch instruction.

`CANONICAL.md` correctly places the ALIGN harness on another branch. This task
adds an extension package without restoring that lane or reading its model/data
paths. `check_squeeze_overlay.py` reads only `records.py`, `interfaces.py`, and
`runner.py` from local commit `e901eb2a480d51377a494be9d797733dfcd0220b`, then imports
them from a temporary directory inside this clone to execute the actual runner
on synthetic episodes. It cleans up its own temporary source files.

The source hashes observed in that check:

| File under `joulewise/align/` | SHA-256 |
|---|---|
| `records.py` | `d5b8f8583716ba5419c0c84710ffec30735128a31b056830767dca6d13cccf93` |
| `interfaces.py` | `6b43491d42b3fc002870e16beb552c9bcb011533597d87046cc165b428b9be00` |
| `runner.py` | `7c3e5015bc9b3f14f4c8a9e872e7501d7876b2758799178df81a56d12db9c638` |

The positive control uses gross episode energy: its extra work occupies an
unowned gap before the visible endpoint request timestamps. A visible-turn-only
reducer could drop it. H counts generated outputs, with one hidden prompt
prefill plus k−1 incremental forwards; the receipt also reports P+k−1 completed
forward input tokens. This includes a prefill cost and is not equivalent to
stripping k existing logged reasoning tokens with joules held fixed.

## Verification

Executed serially on Python 3.13, synthetic only; aggregate test time was seconds,
well below the 20-minute ceiling. No full suite, analysis pipeline, hardware run,
real SHADE episode, model download, or remote consult was performed.

| Command | Final result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_squeeze_config` | 8 passed |
| `python3.13 -B -m unittest tests.align.test_squeeze_control` | 8 passed |
| `python3.13 -B scripts/check_squeeze_overlay.py` | 7 passed against the pinned actual runner, zero skips |
| `python3.13 -B -m unittest tests.align.test_squeeze_harness` | 7 skipped as expected on this main-based branch without the runner; those same tests passed through the overlay above |
| `python3.13 -B -m unittest tests.align.test_squeeze_native` | 1 skipped: MLX absent; no native execution claimed |
| `python3.13 -B -m joulewise.align.squeeze validate --kit configs/align/squeeze` | All 13 versioned configs and manifest hashes passed |
| `python3.13 -B -m compileall -q joulewise/align/squeeze tests/align/squeeze_fixtures.py tests/align/test_squeeze_config.py tests/align/test_squeeze_control.py tests/align/test_squeeze_harness.py tests/align/test_squeeze_native.py scripts/check_squeeze_overlay.py` | Exit 0 |
| `git diff --check` / staged diff check | Passed |

The integrated checks cover active sampling during hidden forwards, timing
containment, unchanged visible trajectories/counts under sham versus dose,
no receipt disclosure in any monitor view or endpoint usage, failures/unreached
triggers, prompt-only mode, protocol conformance, and non-aliasing episode IDs.
These are information-boundary/accounting checks. No synthetic power trace or
alarm/detection-rate evidence was fabricated.

During implementation the first overlay attempt failed because a namespace
package's `__path__` has no `.insert` method. The helper now assigns a new search
path list; subsequent overlay runs pass. Review also caught Python >=3.12's
static runtime-Protocol checks: the task adapter now declares every required
AgentTask property/method explicitly rather than relying on `__getattr__`.

## Limitations, uncertainty, and exact lead steps

1. **Addendum class definitions are unavailable.** No authoritative squeeze
   addendum was found in the named local sources. An optional clarification was
   requested; this draft uses descriptive mappings, not invented official class
   numbers. Lead: supply the addendum path/ref and reconcile that table first.
2. **Apple campaign driver is not activated.** Prompt overlays use its existing
   task-factory seam. Positive controls are implemented/tested through the
   generic `run_episode` entrypoint. The Apple `EpisodeRuntimeAdapter` constructs
   `MlxEndpoint` directly and has no endpoint-injection config slot at the read
   head. Lead: use the generic wrapper with prepared components, or land/review
   an Apple endpoint hook and private-receipt custody path before a campaign.
   No modification of frozen anchors or W1 schedules is implied.
3. **Native tests remain mandatory.** Lead: run
   `python3.13 -B -m unittest tests.align.test_squeeze_native` outside this sandbox
   where MLX imports and Metal is available. It uses a tiny recurrent array
   model and needs no download. Then, in a separately authorized quiet session,
   qualify the actual model/cache, visible RNG/trajectory stability, deadman
   interruption, external-meter clock alignment and gross integration. The toy
   test cannot establish those production properties. Python 3.11 was not
   available here; the package uses only 3.11-compatible syntax/APIs.
4. **Threat scope is deliberately explicit.** The adaptive arm reacts to tool
   results/task progress, without meter/monitor-score feedback. Tools are the
   original SHADE tools; forged counters, remote offload, meter tampering, and
   privilege escalation are not implemented. Lead: rule whether the addendum
   needs any of those capabilities, and freeze adaptation/selection budgets
   before held-out evaluation. Prompt-induced extra work and compute-neutral
   semantic attacks remain potential confounds/defeaters.
5. **No scientific result follows.** No external DC-meter integration or joint
   detector/false-positive rule is implemented here. No claim that the squeeze
   holds, catches semantic sabotage, or resists optimized adaptive attacks is
   supported by these tests. The historical W1 pre-arm audit's blockers remain
   lead owned. All kit artifacts remain DRAFT/PROVISIONAL.

`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and
`tests/test_gen_state.py` remain untouched. No kernel tasks were registered.
No sealed outcomes or real restricted/measurement directories were accessed.
