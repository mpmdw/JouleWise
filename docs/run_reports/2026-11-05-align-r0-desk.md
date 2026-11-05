# ALIGN R0 desk-check implementation — 2026-11-05

Branch: `lane/2026-11-05-align-r0-desk`, from pilot-9
`c9a0a39437614176bf4e14ff1565a6e4537328fb`.
Implementation: `5dd166d82` (`ALIGN R0: add guarded daytime desk checks and fake-backed tests`).
This report is committed separately as the handoff. No push or merge.

Authority: council commit `219fb151515383cbbcde887d096837a829c67396`,
`docs/align/council-2026-11-05/FINAL-DESIGN.md`, blob
`0a802a3097a20c9f4dd5e8823d858302ae596785`, especially §§2.1, 2.2, 2.8.
Read the repository intake/safety conventions, M0, orchestration, targeted
decision-log dependency policy, restart sections and queue fences. The explicit
implementation brief selects this AGENT lane; coordination state remains
lead-owned and was not edited or registered.

## Delivered

- `scripts/align_r0_checks.py`: one unattended CLI with independently selectable
  checks; incrementally saved JSON and Markdown; exclusive record directories,
  a per-machine runner lock, per-check deadlines and nonzero failure/refusal exits.
- `joulewise/align/r0.py`: fixed short-prompt/NLL/tool round trip, synthetic and
  generated rewrite counts, generated-only B7 decision, D effort/N cap ladders,
  envelope parse census, long-decode and memory decision bars, Markdown tables.
- `joulewise/align/r0_mlx.py`: offline lazy backend using the production endpoint,
  native generation/sampler and `EpisodePromptCache`. No pinned implementation
  was changed. Full-context probes record MLX active/peak memory; #1632 retries
  evaluate recurrent metadata at simulated boundaries. Stack/model pins are fixed.
- `joulewise/align/r0_host.py`: shared agent-identity/custody census and daemon
  helper reuse, additional hand-run chain census, latched refusals, explicit-root
  file inventories, offload hash comparisons, disk figures, pmset/device probes,
  and an optional call to the SMC lane's script. Census runs before model work,
  between checks and at up to 15-second intervals during yielded decode tokens.
- `docs/align/r0_desk_runbook.md` and `r0_desk.example.json`: one-page commands,
  configuration, output interpretation and live dependencies.
- `tests/align/test_r0_checks.py`, `test_r0_host.py`, `test_r0_mlx.py`: fake tasks,
  transport/census, runtime/cache and array APIs. All fake reports identify the
  injected backend and cannot set `complete_r0` true.

No models were loaded here. No network, real measurement data, B5 pipeline,
SMC hardware enumeration, production census or full suite was run. All testing
used tiny, generated local inputs. The existing endpoint regression module also
uses synthetic native streams and generated bundles.

## Verification

Run separately, never concurrently:

| Command | Final result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_r0_checks` | 17 passed |
| `python3.13 -B -m unittest tests.align.test_r0_host` | 9 passed |
| `python3.13 -B -m unittest tests.align.test_r0_mlx` | 5 passed |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 passed (24.328 s) |
| `python3.13 -B -m compileall -q joulewise/align/r0*.py scripts/align_r0_checks.py tests/align/test_r0*.py` | passed |
| `python3.13 -B scripts/align_r0_checks.py --help` | passed; no probes or model imports |
| `git diff --cached --check` | passed before implementation commit |

40 final passing targeted tests; total test time across development reruns was
well below 20 minutes. Full-suite omission follows the user's explicit long-job
constraint. Intermediate tests/review caught a pinned runtime cleanup-signature
mismatch and the schema's positive `warmup_runs` requirement; both were fixed.
One intermediate test had misplaced assertions/NameError; corrected before the
final passing runs. The config's `warmup_runs=1` satisfies its schema; no controller
warmup or telemetry campaign is launched by these desk scripts.

## Choices, uncertainty and live blockers

1. **Stage 1 is absent at this base.** The runner checks for B2's endpoint
   constructor fields and reports missing integration before loading. B1 is
   exercised through real endpoint tool parsing, not duplicated here. These
   fake tests do not certify real Qwen templates or the future Stage-1 API.
2. **SMC hook interface is an integration assumption.** The thermal lane's remote
   ref was not present in this clone. The hook expects
   `scripts/align_smc_enumerate.py --output DIR`; absent is `unavailable`, bad exit
   is failure. Confirm/adapt that invocation against the landed lane before the
   live session. No sensor enumeration was duplicated.
3. **Where the design is silent:** use the first 2,049 rendered benign spam SHADE
   IDs for 2,048 teacher-forced NLL targets (fail if too short); inspect exact
   prompt+generated ID prefixes; run 12 dedicated generated echo-tool transitions
   separately from synthetic renderings; require at least 12 generated eligible
   transitions for either model to waive B7. D excludes unclosed-reasoning
   transitions. This N sample floor is conservative; no synthetic result can
   waive the checkpoint. Synthetic rendering success is not a zero-rewrite bar.
4. Ladder screens keep the 16,384-token ceiling by admitting only full-cap turns
   that fit, avoiding a shortened final turn that could distort cap fractions.
   SHADE tool exceptions return error messages to the model as production does;
   the deterministic echo round trip is strict. Task resets get indices 91/92;
   generation gets the council seed law. No capability judge/monitor is invoked.
5. Memory uses the council's budget floors (N 8,192, D 6,144), not an inferred R1
   budget. Input IDs are valid-vocabulary repeated neutral text, with prompt plus
   forced decode exactly 40,960. Peak bars use decimal GB; they remain council
   guesses. No live peak, swap, throughput, effort choice or quantization choice
   is asserted. The fixed-ID stress uses greedy EOS-suppressed native decode.
6. #1632 mitigation is diagnostic only: evaluation every 4,096 decoded tokens and
   at decode end. A passing retest says evaluation is required, not that production
   boundaries have been qualified. R1/Stage 3 must implement and verify it. Any
   failed retest remains screen-only pending a separate stack-change ruling.
7. Disk inventories require materialized regular-file roots, reject symlinks and
   restricted subdirectories, and fail unreadable walks. Source manifests must
   precede offload and be retained outside the source tree. No copy/deletion or
   revision authentication is attempted. Local hashes document observed bytes;
   a configured HF revision is not independent evidence of that revision.
8. Host readiness records AC and both modern `powermode` and legacy
   `lowpowermode` forms. It does not replace R1 lever adoption or arm readiness.
   The census is a snapshot guard, not mutual exclusion against another program
   starting later; long native load/prefill calls can only observe refusal when
   Python regains control. Do not start agents/chains during the desk run.

No ruling question is needed to finish this implementation. Live qualification
and the Stage-1/SMC integration interfaces remain open, explicitly unverified.
The lead's next exact step is to integrate the reviewed Stage-1 and SMC lanes,
confirm the SMC CLI, configure explicit local paths and existing offload manifests,
then run the full runbook on the measurement Mac after all agents/chains exit.
Review and commit that live record; resolve any required B7/fallback before R1.

`RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` are untouched. Controller, monitor, SMC reader and
pinned MLX runtime are untouched. All native/hardware conclusions remain
**PROVISIONAL / UNMEASURED**. This implementation has not received the council's
independent executing review or cold science review.

## Fix round

Review intake: `/private/tmp/jwsol/rev-661.json` (12 findings, no BLOCKER).
Fix branch: `fix/2026-11-05-pr661-r0`. No network, real custody/data reads,
model loads, full suite, coordination-state edits, push or merge. New tests
use generated temporary inputs only. Each group below has a regression
observed failing before its fix; final commit mapping and checks follow below.

- G1 / HIGH endpoint API and history: imported the actual Stage-1 B1/B2 code
  and its synthetic fixtures/tests from `d01288e25`, rather than inventing a
  desk-only history representation. R0 and workload now use
  `assistant_history_message`; optional `reasoning_effort` reaches both
  production template paths, with the default omitted. Added prompt-ID parity
  and effort regressions (`test_r0_integration`, 2 errors before, 2 pass after).
  Existing fake backends now implement the real history seam.

- G2 / HIGH memory sampling + MEDIUM no-op metadata retest: synchronize each
  sample, exclude the pre-prefill baseline, and use median slopes spanning at
  least 10k positions. Report actual KV-array allocation slope alongside total
  active-memory trend. Preserve raw samples. Isolated-spike and sustained-growth
  regressions fail before/pass after. Count arrays actually evaluated; an empty
  single-stream retest is explicit and cannot claim a mitigation. If the first
  attempt fails and an identical no-metadata retry passes, the result remains
  inconclusive, requiring a lead ruling. The refuted note limits the original
  projection: a D-shaped probe did not reproduce the toy-model effect. This
  change does not assert a D-scale leak or claim to validate #1632 in batching.
  Added `tests.align.test_r0_mlx_native.NativeMemoryTest` using random tiny
  hybrid weights and real streaming/cache APIs. Native test is skipped here
  (MLX absent); the lead must run it on the pinned Metal stack. Existing shim
  now models the real single-stream absence of lengths/left_padding.

- G3 / HIGH custody fail-open: shared default, environment additions and config
  extras are unioned and resolved, every root must exist as a directory, and
  receipts retain the resolved list even on refusal. Added missing-root and
  hidden-default regressions (both fail before/pass after). Example uses the
  actual shared default semantics, with runbook instructions for overrides.
  All guard tests redirect environment roots to generated temporary directories;
  no real custody census ran in this session.

- G5 / MEDIUM armed-window detection: initial and boundary/periodic guard
  checks refuse installed `com.joulewise.night*.plist` files or a loaded night
  service; unknown launchctl failures also refuse. Added installed-but-idle,
  loaded-without-plist and observation-error regressions (fail before/pass
  after). Guard tests mock home and launchctl, so no real LaunchAgent path
  was inspected. This remains a snapshot, not protection against later arming.

- G6 / MEDIUM envelope census + LOW lost tool replies: turn evidence now keeps
  endpoint-visible text, and only that text enters the denominator. Incomplete
  capped envelopes are counted separately; complete malformed envelopes and
  unsupported-format flags still fail. Ladder rows retain tool outputs/errors.
  Reasoning-quote/capped-tail and tool-error evidence regressions fail before
  and pass after.

- G4 / MEDIUM shared deadline and lost partial results: each decode attempt,
  ladder episode and generated turn gets its own timeout. Check rows are added
  before work; attempts, rungs, episodes, turns, transitions and native memory
  samples are saved incrementally. Exceptions update the existing row and mark
  in-flight work interrupted. Three regressions failed before and pass after,
  including reading the partial receipt from disk inside a timed-out retry.
  Runbook gives D's token/time calculation and a 14,400 s slow-host override.

- G8 / LOW extra load bars and outcome semantics: coherence/echo are diagnostic,
  NLL remains a gate, and the echo instruction consistently asks for one call
  per turn. Template is diagnostic-only. Checkpoint `required` and ladder
  `fallback` are completed selection decisions, recorded separately as pending
  lead action rather than run failures. Inconclusive/error results still fail
  completion. Two regressions fail before/pass after. A completed R0 does not
  authorize R1 or waive the resulting checkpoint/fallback actions.

- A1 / binding amendment: active pins, accepted config, CLI defaults and R0
  completion now require D only. Qwen3-Next cannot be requested or loaded through
  this CLI; Flash-Next is not added. Regression fails before/passes after. The
  cached council ref lacks `FINAL-DESIGN-AMENDMENT-1.md`; no network is allowed,
  so this applies the user's explicit amendment summary. Exact amendment text
  and revised disk/member arithmetic remain unverified pending the lead's ref.

- G9 / LOW model bytes and host identity: all model subsets now require at
  least 128 GiB and an exact hw.model match to the lead-supplied
  `measurement_hw_model` config pin, before importing/loading native models.
  The example has a refusing placeholder; no hardware identifier was guessed.
  Host-capacity/identity and load-blocking regressions fail before/pass after.
  **Remaining disposition:** exact weight/revision authentication is deferred.
  The only supplied pin is a whole-download total (includes tokenizer/config
  bytes), not a safetensors-only total or pinned manifest. Treating it as the
  weight total would reject valid mirrors; hashing an unpinned local manifest
  cannot establish remote identity. Lead must supply a revision-authenticated
  manifest/weight-total pin before live qualification. Existing file hashes and
  byte differences remain diagnostics, not a claim of revision authentication.

- G7 / MEDIUM idle-only/exit-code-only SMC: request `--gpu-step`, allow 2,400 s
  for the roughly 1,500 s protocol, and require resolved distinct s_fast/s_slow
  values from r0.json. Missing, malformed or unrecognized receipt schemas are
  inconclusive; exit 0 cannot certify thermometry. Regression fails before and
  passes after for no receipt, two selected keys and unresolved slow key.
  **Integration uncertainty:** #658 exists per the review, but neither its source
  nor its ref is present locally. The adapter currently reads top-level
  s_fast/s_slow keys named by the review. The exact receipt nesting/types and
  step CLI remain to be checked against #658 before live use; unknown shapes
  fail closed. Requested its local commit from the lead; no network fetch ran.
