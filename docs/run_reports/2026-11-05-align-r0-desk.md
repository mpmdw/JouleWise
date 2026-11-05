# ALIGN R0 desk-check implementation — 2026-11-05

Original branch: `lane/2026-11-05-align-r0-desk`, implementation `5dd166d82`,
handoff `49e78e178`. Fix branch: `fix/2026-11-05-pr661-r0`.
Local commits only; no push or merge. The Fix round section below supersedes
the original implementation assumptions.

Authority: council commit `219fb151515383cbbcde887d096837a829c67396`,
`docs/align/council-2026-11-05/FINAL-DESIGN.md`, blob
`0a802a3097a20c9f4dd5e8823d858302ae596785`, especially §§2.1, 2.2, 2.8,
plus Amendment 1 at `6eb1ff5be31bec330ae5af262c2b4c7601e7755e` (full text
read with git show): D only; Next dropped, Flash-Next later. Cached refs omit
this commit and #658, but both were located by enumerating Git object metadata
and reading commit objects only. No fetch or outside worktree access occurred.
Intake included AGENTS/CLAUDE, M0, orchestration, targeted decision-log policy,
restart/stop-card and queue fences. The explicit brief selects this AGENT work.
Coordination files and kernel tasks remain lead-owned and untouched.

## Current implementation

- Guarded offline CLI with exclusive outputs, per-machine lock, independent
  checks, per-attempt/episode/turn deadlines, incremental JSON/Markdown and
  retained partial evidence. Native computation can delay Python signal delivery.
- Stage-1 B1/B2 imported from `d01288e25`; R0 uses the workload's structured
  assistant history. Optional effort passes through the production endpoint.
- D-only load/NLL, diagnostic coherence/echo, template diagnostics, generated
  B7 decision, effort ladder, visible-envelope census, long decode and memory.
  `required`/`fallback` are decisions needing lead action; errors/inconclusive
  evidence prevent completion. Synthetic/injected evidence cannot complete R0.
- Synchronized active-memory samples, robust median long-span growth slope and
  separate actual KV-array allocation slope. A retry counts evaluated metadata
  arrays; absent single-stream metadata does not demonstrate a #1632 mitigation.
- Default/environment/config custody roots, fail-closed missing roots, installed
  or loaded night-agent detection, latched process/custody refusals, pinned host
  model and 128 GiB minimum before loading. All census tests use synthetic roots.
- Inventories/offload hashes and free-space gates. Exact remote revision/weight
  identity remains unverified; see G9's disposition. Disk also hashes the 30B
  anchor and reports the amended 37.4 GB W1 estimate. The SMC adapter uses the
  actual #658 receipt schema and the required 60 s step. A verified source/spec
  conflict prevents SMC qualification pending a lead ruling (G7 below).

No native models, hardware enumeration, real custody or measurement data were
read. No network, block-5 pipeline or full suite ran. Controller, monitor, SMC
reader and pinned MLX runtime remain unchanged. Imported template fixtures are
code assets; no Flash-Next model is enabled or loaded.

## Original verification (before this fix round)

The original 40-test total comprised **31 new R0 tests** (17 checks, 9 host,
5 shim) and **9 pre-existing endpoint tests**. It did not mean 40 new R0 tests.
The original modules passed separately, with the endpoint module taking
24.328 s. Compileall, CLI help and diff whitespace checks also passed then.
Final fix-round commands/results are recorded below, separately from this
historical count.

At review time, **CI was not green**: shard 12 failed in
`b6.test_cold_pass_fixes`, with other shards still running. The executing review
reports the same failure on #658 and #660; that is review-provided base-triage
information, not a failure reverified here. No network/CI checks were performed
in this fix session. The lead must obtain green CI or adjudicate the base
failure before merge. No local test result in this report certifies CI.

## Native and integration gates

All native/hardware conclusions remain **PROVISIONAL / UNMEASURED**.
On the pinned Metal host, outside this sandbox, the lead must run:

- `python -B -m unittest tests.align.test_r0_mlx_native`
- `python -B -m unittest tests.align.test_xml_tool_calls` with optional Jinja2
  available, so the seven real-template tests actually execute.

The native test uses random tiny hybrid weights, a local synthetic vocabulary,
real stream_generate, runtime generation and EpisodePromptCache; it downloads
nothing. It was written but cannot be validated here (MLX absent). It does not
project tiny-model allocator behavior to D scale. After the SMC ruling, lane
integration and reviewed model pins, perform live R0 only from a clean measurement-Mac
Terminal with all agents closed and no window armed. R1 remains separate.

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
  amendment was subsequently located at `6eb1ff5be` in local Git objects and
  read in full. Added the A5 30B anchor inventory (`anchor_source`) and A1's
  37.4 GB two-copy W1 figure; the disk regression fails before/passes after.
  No N download field remains. #657's recorded native-exactness/admission gate
  remains lead-owned before enabling the kit safety path; zero rewrites do not
  waive it. This runner does not certify that separate gate.

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

- G7 / MEDIUM idle-only/exit-code-only SMC: source #658 was found at
  `274fec2cb2fcc301798c91140e51c244c2469988` and inspected without running it.
  The adapter uses `response.s_fast`/`response.s_slow`, checks receipt schema,
  GPU-step provenance, distinct temperature keys and >99% successful 1 Hz slots
  over at least 600 s. It invokes the amendment's 60 s load with 600 s idle and
  recovery, and allows 2,400 s. Missing/malformed/unresolved evidence cannot
  pass. The regression failed before and passes after, including actual-schema
  parsing. **Qualification is intentionally inconclusive pending the ruling
  below**; no idle-only or exit-code-only result can complete R0.

- G10 / LOW report/PR-body evidence: corrected the 31+9 original count, removed
  the false assertion that a no-metadata retry demonstrates mitigation, and
  distinguished locally missing refs from the actual existence of #658. CI is
  explicitly unverified/red at review time, with the b6 base failure attributed
  to the review rather than independently confirmed. Two documentation
  regressions failed before/pass after. No remote PR body was edited (no
  network); the lead can copy this corrected handoff into it.

### Finding-to-commit map

| Review finding | Group / local commit | Disposition |
|---|---|---|
| HIGH endpoint API/history | G1 `203dbadbd` | Fixed; imported #659 and added effort/history parity regression |
| HIGH memory transients | G2 `3b9ff0c56` | Fixed sampling/trend; D-scale projection explicitly refuted |
| HIGH custody fail-open | G3 `901ab540f` | Fixed default/extras/missing-root admission |
| MEDIUM metadata no-op | G2 `3b9ff0c56` | Fixed accounting; empty retry cannot claim mitigation |
| MEDIUM deadline/partial loss | G4 `38908cad6` | Fixed incremental receipts and separate deadlines |
| MEDIUM armed windows | G5 `c16c9de46` | Fixed plist/launchctl census |
| MEDIUM envelope denominator | G6 `81d2cad0f` | Fixed visible/capped-envelope accounting |
| MEDIUM SMC | G7 `ac0ac5fb7` | Known hook defects fixed; qualification blocked by source/spec conflict below |
| LOW missing tool outputs | G6 `81d2cad0f` | Fixed tool reply/error evidence |
| LOW load/status/template semantics | G8 `ebc632382` | Fixed diagnostic/decision outcomes |
| LOW bytes/host identity | G9 `32545aba4` | Host fixed; exact weight/revision pin deferred as explained above |
| LOW report accuracy | G10, this documentation commit | Corrected with regression and explicit CI/native limits |
| Binding Amendment 1 | `99b2a5929`, `98786be0e` | D only, anchor inventory, amended disk estimate and authority receipt |

### NEEDS_RULING — SMC step duration versus slow-class fit

**Question:** may R0 run the required 60 s readability step plus a separate
600 s characterization step before accepting the selected classes?

**Evidence:** Amendment 1 A5.3 requires idle plus a 60 s load step and readable
die/heatsink classes at 1 Hz with <1% errors over 10 min. #658's `rank()` requires
`tau < min(load_duration, recovery_duration)`; `select_keys()` requires
`tau > 120` for S_slow. Thus a 60 s load can never resolve its slow class.
The earlier 600 s default would silently change the binding amendment.

**Options considered:** (1) required 60 s readability capture plus a separate
600 s characterization capture; (2) leave R0 inconclusive until the lead revises
#658's class-fitting/qualification rule. **Recommendation:** option 1, with the
lead confirming the design's die/slow class bars. No extra capture route was
implemented without that ruling. **Blocked work:** a passing SMC verdict and
complete live R0; no hardware work has been attempted. The asynchronous question
remains pending; elapsed time is not approval.

### Changed files

- Production: `joulewise/align/r0.py`, `r0_host.py`, `r0_mlx.py`, `r0_runner.py`;
  `joulewise/align/apple/endpoint.py`, `workload.py`, `xml_tool_calls.py`.
- Tests: `tests/align/test_r0_checks.py`, `test_r0_host.py`, `test_r0_mlx.py`,
  `test_r0_mlx_native.py`, `test_r0_integration.py`, `test_r0_progress.py`,
  `test_r0_documentation.py`, `test_xml_tool_calls.py`; six imported Stage-1
  JSON/template/provenance fixtures under `tests/align/fixtures/`.
- Docs/config: `docs/align/r0_desk_runbook.md`, `r0_desk.example.json`, this report.

Coordination state, `tests/test_gen_state.py`, raw evidence and live run bundles
remain untouched. No sub-agents, external consults, network, push or merge.

### Final verification

Each test module ran separately; none ran concurrently. All touched modules
were rerun. No full suite or live/native capture ran. Test execution, including
regression-before-fix runs, stayed well under the ~20-minute budget.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_r0_checks` | 25 passed |
| `python3.13 -B -m unittest tests.align.test_r0_host` | 14 passed |
| `python3.13 -B -m unittest tests.align.test_r0_mlx` | 5 passed |
| `python3.13 -B -m unittest tests.align.test_r0_mlx_native` | 1 skipped: MLX absent; lead must run on Metal |
| `python3.13 -B -m unittest tests.align.test_r0_integration` | 2 passed |
| `python3.13 -B -m unittest tests.align.test_r0_progress` | 3 passed |
| `python3.13 -B -m unittest tests.align.test_r0_documentation` | 2 passed |
| `python3.13 -B -m unittest tests.align.test_xml_tool_calls` | 13 passed, 7 skipped: optional Jinja2 absent |
| `python3.13 -B -m unittest tests.align.test_apple_endpoint` | 9 passed, 28.803 s |
| `python3.13 -B -m unittest tests.align.test_apple_campaign` | 12 passed, 104.146 s |
| `python3.13 -B -m compileall -q` on the seven changed production modules, R0 CLI and eight touched test modules | passed |
| `python3.13 -B scripts/align_r0_checks.py --help` | passed; D-only CLI, no probes |
| `git diff --check` and staged whitespace checks | passed |

Total across the final module runs: **85 passed, 8 skipped** (93 discovered).
The two pre-existing integration modules are included in that total, separately
from the 51 passing R0 tests and 13 passing imported XML tests. Passing fakes
establish control/data-flow behavior; they do not certify model, sensor, memory
or thermal behavior on hardware.

G10 commit title: `docs(r0): correct review evidence and record fix-round verification`.
Next exact step: answer the SMC NEEDS_RULING question above. Then implement and
verify the approved qualification route, supply the deferred authenticated
weight pin, run the native/template gates, and obtain green CI or adjudicate
its base failure. Only the lead, with agents closed, may run and commit live R0.
