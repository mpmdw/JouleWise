Reading additional input from stdin...
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: high
reasoning summaries: none
session id: 019fddaa-f398-7dd3-a724-d89866d64584
--------
user
EXECUTION-PLAN DRAFT — TWO CHEAP PROBES (read-only; no writes; final message = both plans). Probe A, spec-decode daytime pilot (~2h, from docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md strengthening move b): stock pinned-runtime tok/s comparison, spec-on (Qwen2.5-1.5B target + 0.5B draft, then 7B target + 0.5B draft) vs spec-off greedy, 128/512 workload, n>=5 each; exact mlx_lm commands from the installed package (cite the API), what to record, decision rule (if spec-on throughput < spec-off, the energy question is CLOSED negative and the K-manipulation study dies at zero cost). Probe B, GPU-cadence characterization evening (from reviews/rev-split-inference-metrology.md strengthening move 1): on the 3080 Ti rig, nvidia-smi/NVML sampling-cadence + averaging-behavior characterization via a step-load pulse train (no LLM needed); protocol, scripts shape, what closes JouleWise_Hardening_Proposal.md Phase-7 item 4, what it would say about any future two-boundary work. NOTE hardware access status for B is an Ed-external gate — plan assumes access, flags the gate. Both: pass/fail criteria, artifacts to custody, ~hours.
codex
I’ll turn both review suggestions into bench-ready, read-only execution plans. I’ll first check the repository’s active gates and source-of-truth language, then verify the installed `mlx_lm` speculative-decoding CLI/API directly so Probe A’s commands are exact.
exec
/bin/zsh -lc 'git status --short --branch && rg -n "ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "Current Queue|Do-Not-Do-Yet|Do Not Do Yet|M0|Mission M0" TASK_QUEUE.md docs/agent_playbook.md && rg -n "spec|decode|strengthening move|Phase.?7|item 4|two-boundary|cadence|averag" docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md JouleWise_Hardening_Proposal.md docs/orchestration.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 exited 2 in 0ms:
## main...origin/main
2008:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
2043:## ACTIVE_STOP_CARD
2182:## Current Project Status
2743:## Known Workspace State
docs/agent_playbook.md:26:1. Run Mission M0 (preflight) — always.
docs/agent_playbook.md:50:## Mission M0: Preflight (every session)
docs/agent_playbook.md:56:2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
docs/agent_playbook.md:326:in the run report. Never close it silently (Do-Not-Do-Yet list).
docs/agent_playbook.md:356:- Land Slice 2N first (Do-Not-Do-Yet list) — 2G builds on the post-2N
docs/agent_playbook.md:472:The M0 step-6 handoff list, plus: if you changed an adapter or bundle
TASK_QUEUE.md:96:Current Queue region is the sole live work-selection view.
TASK_QUEUE.md:213:## Current Do-Not-Do-Yet List
TASK_QUEUE.md:306:## Current Queue
TASK_QUEUE.md:362:| A31 | DOC-008-INTAKE | P4 Polish | READY [AGENT] | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
TASK_QUEUE.md:440:| A31 | DOC-008-INTAKE | P4 Polish | READY | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
rg: JouleWise_Hardening_Proposal.md: No such file or directory (os error 2)
docs/orchestration.md:29:  writing: implementation against pinned specs, adversarial review
docs/orchestration.md:170:  zero-defect streaks. (One layer, the default specialist review lens, was
docs/orchestration.md:173:  altitude (pinned-spec / design-freedom / judgment-call), outcome
docs/orchestration.md:177:  vibes. Current signal: pinned-spec delegation runs essentially
docs/orchestration.md:236:   Calibration anchors (recorded so recalibration stays honest): healthy xhigh ≈ 2.3–3.5M tokens/session (C-030 post effort-fix; C-028 average); the recorded broken state averaged ~9M. C-028 (330.6M / 59 sessions / ~$1,050 / ~17.5h) crosses every substantive arc HARD dimension — it is the anti-example. The 2026-07-13 comprehensive audit (~30 Sol sessions + ~70 Fable agents, Ed-authorized) crosses arc SOFT on session count only — the intended "exceptional: justify and continue" outcome.
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:25:| original_goals | **9** | This *is* the split axis, honestly scoped, honestly silent on spec-decode/MTP/MoE/KDA. Real credit here. |
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:32:lists "nvidia-smi cadence and averaging characterization" as an unexecuted Phase-7 promotion item, and
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:34:*assumes the requested poll rate is the instrument cadence*. That is precisely the class of assumption
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:35:D-078 was created to destroy on the Mac. NVML board power on consumer Ampere is a filtered average whose
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:47:prospective bound smaller than 25% of the shortest claimed interval") while retaining D-078's rhetoric of
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:49:single, 100 ms-cadenced. **This is the deepest flaw: the paper inherits the vocabulary of the calibrated
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:71:~12 J over a 30 s composite window — comparable to the effect. The proposal says the meter spec "must
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:80:re-run determinism/output-identity machinery, and — because floors are stack-specific — **a full floor
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:104:scp a 56-448 MiB cache, decode on a consumer GPU over 1GbE — is not disaggregation as the field means it;
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:115:## Three strengthening moves (if kept)
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:120:   cadence/averaging characterization** (pulse-train step-load on the 3080 Ti, no LLM, no Mac, closes
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:121:   hardening Phase-7 item 4 and costs one non-quiet evening on owned hardware); then publish "the
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:122:   two-boundary composite budget is ~N J against candidate effects of 10-200 J, therefore the split
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:141:probe; if the GPU cadence characterization comes back at 100 ms or better *and* a cross-device power-step
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:1:# Counter-review — `prop-spec-decode-energy.md`
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:8:mis-specifies the floor class it needs, understates the build by roughly a
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:34:  `docs/specs/axi/sc_spec_decode_verdict.md`).
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:35:- **MLX serves external-draft speculative decoding today.** Pinned
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:37:  `--num-draft-tokens`, `speculative_generate_step(...)` with separate
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:39:  (`sc_spec_decode_verdict.md` §A with line cites into `mlx_lm/generate.py`).
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:44:  `docs/contracts/analysis_plans.md:159` already defines it as a *spec-on-only
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:48:- **AP-SPEC exists** as `AP-SPEC-DRAFT` in `docs/specs/axi/se_analysis_plans_draft.md:209`.
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:54:The proposal's primary metric is **paired `spec_on − spec_off` gross joules per
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:60:  `phase_energy_j.decode @ window_class phase`.
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:63:  `phase_energy_j.decode` only; `["phase","decode"]` only". D-117's own U3 work
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:64:  order extends it to **four phase cells** — decode+prefill × 1.5B/7B. It does
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:86:`docs/specs/axi/sc_spec_decode_verdict.md` is a **closed, dated applicability
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:92:> aggregate acceptance, and exact decode-step emitted slices."
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:106:   `speculative_generate_step` at `mlx_lm/generate.py:607-627`. This is real
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:110:   binds "model/runtime/config hashes"; `sc_spec_decode_verdict.md` itself pins
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:114:   but it must be stated, and the spec-off arm must run the *forked* runtime too,
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:118:`decode_emission` event per decode step across a 256-token generation, in the
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:123:the instrumentation load is **asymmetric across arms**: spec-on has fewer decode
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:124:steps but more per-step payload; spec-off has one event per token. So it does
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:134:- Under spec-on, the **draft model performs its own prompt prefill**. If the
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:135:  prefill/decode split is anchored on the target's first committed token, the
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:137:  models' prompt processing — a different physical object than the spec-off
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:139:- Inside "decode", the target's verify pass is a *batched K+1-token forward* —
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:140:  prefill-shaped compute wearing a decode label. Comparing "decode energy"
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:152:  efficiency metric, it is undefined for spec-off, and the D-037 rider in
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:172:2. **No multiplicity control is specified**, unlike the sibling quantization
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:175:3. **Acceptance is a post-treatment mediator observable only in the spec-on
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:176:   arm.** Regressing the paired difference on a spec-on-only covariate is a
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:220:sentence: "on this stack, external-draft speculative decoding never repays its
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:236:  envelope depending on whether spec-on members are ~2.5× slower (see §6) — and
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:257:  probability this gate fires is high — spec decode's exactness guarantee is
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:258:  distributional, and batched verify vs sequential decode differ in float
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:271:  "first speculative-decoding energy study", names EuroMLSys / ICPE emerging as
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:282:## 9. Three strengthening moves
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:289:   Retitle to "Does speculative decoding ever repay its energy at batch 1?" —
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:294:   runtime fork, run a *non-claim, daytime, wall-clock-only* spec-on/off timing
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:296:   works — no instrumentation needed for tok/s). If spec-on is slower than
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:305:   primary metric to `phase_energy_j.decode` with an explicit, pre-registered
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:308:   choice. Additionally: run the spec-off arm on the *same forked runtime*, and
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:310:   instrumented-vs-uninstrumented spec-off pair) before either arm is claimed.

exec
/bin/zsh -lc "sed -n '2000,2215p' RUN_STATE.md; sed -n '2735,2795p' RUN_STATE.md; sed -n '45,90p' docs/agent_playbook.md; sed -n '205,260p' TASK_QUEUE.md; sed -n '300,380p' TASK_QUEUE.md; sed -n '1,210p' docs/orchestration.md; sed -n '280,320p' docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md; sed -n '110,155p' docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md; rg --files | rg 'JouleWise_Hardening_Proposal\\.md"'$|Hardening.*Proposal|hardening.*proposal'"'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
6. Check the last 2-3 commits with `git log --oneline --decorate -3`.
7. Check `git status --short --branch`.
8. Run `python3 -m unittest discover -s tests` unless the task is docs-only.
9. Do not commit local deletions or unrelated changes unless the user asks.
10. Heartbeat rule (`docs/milestones.md`): if >14 days passed with no run
    report and no recorded break, start with a milestones + risk review.
11. Live MLX gates use the repo venv: `.venv/bin/python -m joulewise ...`
    (system python3 lacks mlx → `runtime_unavailable`).
12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
    "restart", "next", queue, and mission pointer until explicitly cleared.

At the end of substantial work:

1. Update only hand-authored factual/history sections of this file.
2. Update `docs/process/state_kernel.json` for live task state and regenerate;
   do not hand-edit either generated region.
3. Add or update a detailed report in `docs/run_reports/`.
4. Record tests, commands, and blockers; generated lane heads own next-work
   selection.
5. Record new decision-log entries and any risk-register status changes.
6. Refresh `PROJECT_STATUS.md` if advisor-visible state changed.
7. Push green commits promptly (small doc/bookkeeping commits straight
   to main; multi-commit code series as branch + PR per D-031). Do not
   accumulate unpushed local state — the remote and the high-level docs
   (README, PROJECT_STATUS) are the user's and advisor's view.
8. Run a docs-consistency sweep before the final bookkeeping commit
   (delegate to a fast subagent): stale test counts, gate-state
   contradictions between prose summaries and checklist matrix rows,
   numbers cited in multiple places (C-002; D-023 extension).
   Refreshing `docs/site/DRIFT.md` is OPTIONAL (D-101: the site gates
   nothing and is fully decoupled); when touched, it informs only:
   per D-068 (2026-07-14) NO agent regenerates or deploys the site,
   ever — automation informs; Ed deploys manually. (Supersedes the
   C-013 regenerate+redeploy convention.)
9. Call out any dirty working-tree state that should not be accidentally
   committed.

## Historical Stop-Card Note

This 2026-07-11 clearance note is retained as history only; current stop-card
and work-selection state is generated immediately below from the kernel.

<!-- BEGIN GENERATED: state-kernel run-state-intake -->
## ACTIVE_STOP_CARD

Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063 ([decision log](docs/decision_log.md)).

## Active Global Work-Selection Gates

NONE — no global work-selection gate is active.

## Restart By Machine-State Lane

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05). Latest report: [16h runway checkpoint 2026-08-03: D-108..D-112 minted; kernel pins 60; CAL-BRACKET held at 2e61ff9 (rule-11 gate owed for B1 round 2); winB license exhausted as drawn (r06 disposition parked, WINB-R06-DISPOSITION-01); mint chain D-110-blocked; CLAIMS_STATUS §1 honestly NONE; checkpoint block at the top of RUN_STATE is the successor resume script.](docs/run_reports/2026-08-03-16h-runway.md).

### [ED-EXTERNAL]

- READY — E1 `P1-008`: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).

### [QUIET-MAC]

- READY — Q2 `P2-006`: Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison.

### [AGENT]

- READY — A0 `P2-035`: RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests).

<!-- END GENERATED: state-kernel run-state-intake -->

## CHECKPOINT 2026-07-18 (late): D-077 adversarial arc complete, PR #77 open

The RESUME list from the 2026-07-17 checkpoint is fully executed. The
relaunched execution-lens review, fix rounds 1-2, and their delta
re-audits had already run earlier on 2026-07-18 (commits `1aebf14`,
`6d80039`); this session closed the surviving P1 (child accepted any
JSON object as the frozen cooldown anchor) plus every finding from four
further delta re-audits, as fix rounds 3-8 in commit `ad0920b`:
canonical anchor validator (`joulewise/cooldown_anchor.py`) enforced
fail-closed at parent/CLI/controller boundaries; collision-safe,
crash-atomic, flock-serialized rejection-verdict custody
(`experiments/rejections/`); physical-domain baseline validation (the
`inf`-anchor fail-open gate is closed); discriminating process-race
regression. Suite green lead-side at every round boundary, final
`Ran 1746 tests`, `OK (skipped=12)`. Awake-half live probe validation
passed on real hardware (zero probe errors); the Ventura screensaver is
now disabled on the machine (`idleTime = 0`). PR #77 carries the gate
narrative; merge is Ed's call. Full record:
`docs/run_reports/2026-07-18-d077-fix-rounds.md`. Tooling: codex-run-v3
xhigh review-genre sessions ended with null final messages 4x
(bridge-resume recovered each; personal-tooling defect, recorded in the
run report and the global codex-delegation skill field notes, not the
repo queue).

## CHECKPOINT 2026-07-18: Claude script bridge runs in the pet's app task

The actual Claude Code fallback route is `scripts/codex-bridge`, not the MCP
server for recent audited work. The wrapper now sends `new` and `review` turns
through a dedicated app-owned Codex desktop task when the local host id is
configured. This is the same local-conversation state the native pet consumes;
the prior observer-only diagnosis was incorrect because the pet never reads
`~/.codex/claude-spawned/index.jsonl`. A live Sol/high smoke appeared in the
Codex app as thread `019f77a6-3612-7332-9f5e-be9fbde56be5`, turn
`019f77a9-2827-7de1-accf-ac2eda21927e`, and returned
`JOULEWISE_NATIVE_PET_BRIDGE_OK` through the script. Adaptive effort remains
unchanged: `high` fallback/default, `xhigh` only on named hard-task triggers,
and `ultra` only for sessions that must spawn subagents. Full record:
`docs/run_reports/2026-07-18-claude-codex-pet-observer.md`.

Committed 2026-07-18 on `impl/env-guard-cooldown` (after the D-077
packet boundary `6d80039`) with a lead execution review at the bench:
IPC socket ownership/permission checks, PID-checked host-task lock,
interrupt-on-terminate, no-network sandbox policy, and one-hop rule all
verified in `scripts/codex-app-bridge.mjs`; real-socket fake-router
tests plus observer lifecycle tests included; canonical suite green
lead-side (`Ran 1722 tests`, `OK (skipped=12)`). The same commit
carries the doctor-driven CLAUDE.md trims (global + repo; content
deduplicated into `.claude/skills/codex/SKILL.md`, which is the
operating home) and stamp-only `docs/site/*.html` provenance refresh.

## CHECKPOINT 2026-07-17 (late session): env-guard branch open, review pending

Window A floors contamination diagnosed from primary data: macOS Ventura
*video* screensaver on an awake display contaminated 43/50 suite-calibration
bundles (~+30% energy, −11% throughput; engage at HID-idle +20 min, dismiss on
unlock — pmset assertion log corroborated to the second). The six "low"
su-ABBA runs (18:16–18:36 UTC) are the only CLEAN suite runs; comparative
suite floors (4.923 J item / 24.62 J suite) are transition artifacts. The
professor's power-source hypothesis is refuted (AC/140 W/100% throughout).
Details: memory note + `docs/run_reports/2026-07-17-environment-guard.md`.

Branch `impl/env-guard-cooldown` (pushed, commit e2813ee) holds the D-077
response: environment-guard preflight (+`--arm-quiet-mode`), per-run idle
admission gate, cooldown v2, unwaivable `environment_admission_failed` claim
barrier, policy sidecars, contract/doc updates. Design consult (Sol xhigh,
thread 019f7356-32d3) adjudicated and encoded; implementation by Sol xhigh
(thread 019f7362-6627, resumed via codex-bridge after an MCP transport
timeout); session-close scope check SCOPE_OK; full suite green lead-side
(OK, 12 skips). Lead bench fix included: `pmset -g systemstate` parser now
accepts the live "Capabilities are:" form (was null → fail-closed on real
hardware); fixtures pinned to verbatim live output.

RESUME (in order):
1. Relaunch the adversarial review round (was stopped mid-run at checkpoint):
   fresh read-only Sol xhigh, execution lens, over `git diff main...impl/env-guard-cooldown`
   (prompt shape in `.codex-bridge/` prompt snapshots); lead holds the
   contract lens (done for cooldown_gate/claim-barrier/anchor hunks).
2. Triage findings → fix rounds (defect-shaped regressions) → DELTA RE-AUDIT.
3. Live-validate flagged probes during next quiet-window prep:
   `pmset -g systemstate` display-asleep form + screensaver-engaged probe
   while a screensaver is actually running (run report flags
   `live_validation_provisional`).
4. PR per operation-loop §5 gate shape; then re-run suite ABBA calibration
   under the new guard ([QUIET-MAC], needs Ed) — floors D-076 figures for
   suite comparative cells must be recomputed/caveated pending re-run.

Status: **CLEARED 2026-07-11.** Every clearance criterion met: all
checkpoint-#4 resume items executed (P2-044 fix+merge #55; P2-037
audit dispositions → two fix rounds + approved NEEDS_SCOPE expansion +
delta re-audit → #58; P2-043 #57; P2-045 #56); the four held hardening
PRs #50-#53 merged after the cross-stream integration review over the
combined tree (38 pre-merge cross-stream failures caught and fixed; 1
review blocker confirmed by refuters → PR #59; SF1 refuted; SF3 →
queue row P2-049); DOC-008 kernel refreshed at final head (schema v2,
authority field, branch impl/doc008-kernel awaiting PR); bookkeeping
arc complete (run report, C-028 council entry with layer catch-rates
and ~57-invocation spend record, D-064 ratified incl. manifest v3 +
claude-codex-report/v1 + WRITE_SCOPE enforcement; queue reconciled;
consistency sweep; site regen+deploy). All clearance-time opens since CLOSED same day: #59 MERGED, DOC-008
MERGED (#60). Remaining queue heads: P2-049/P2-050/TOOL-01.

## Superseded stop card (CP-5)

Status: **CLEARED 2026-07-09** by the CP-5 resume session. Every
clearance criterion was met: all three worktree diffs lead-gated
(envgate live-gated against the real affine mock bundle) and merged as
PRs #23/#24/#25; PR #22 merged after a fresh final-head pass; the
methodology synthesis and suite_next specs packet adjudicated (CP-6 in
the stream log); all accepted pre-campaign changes landed and merged
(PRs #26/#27/#28); both post-merge integration reviews CLEAN; queue
rank 0 closed. Full record:
`docs/run_reports/2026-07-09-cp5-resume.md`. No stop card is active.

## Current Project Status

**Mint era OPEN AND FIRST MINT LANDED (2026-07-30): main `da83337`. The
data exists and passes, and the code path that turns it into a published
floor now exists and has been exercised — `df-ph-decode-floor-mint1` is
mainline.**

### The central measurement fact (read before any measurement decision)

The instrument is **attribution-limited (~1 J), not noise-limited
(~0.3 J)** — D-078 clause 11, Ed-ratified. Floors publish LABELLED with
the widened number; the point floor is a repeatability diagnostic that
may never be the published claim floor. The anchor term appears in
**both** the floor and each claim's decision interval, so the effective
clearable effect is floor + claim-side bound ≈ 5 J for phase contrasts,
and neither term may later be deleted as an apparent double count. Do
not launch an instrument-tightening program; it was measured and
eliminated.

### Collection state

| Window | Contents | Verdict | Notes |
|---|---|---|---|
| a9, a10 | earlier corpora | **PASSED** | a10 supplies the absolute component |
| **B** (`04_phase_prefill_abba`) | 40 prefill ABBA members, 59/59 collected clean | **FAILED** | `instrument_calibration_mismatch`, bracket drift 11.581436 ms; preserved, not claim-bearing |
| **C** (`05_phase_decode_abba`) | 40 decode ABBA members, 59/59 collected | **PASSED** | bracket drift 1.279 ms; first comparative window in project history to pass |
| **D** (absolute) | 30 claim members, 49/49 collected | **PASSED** | bracket drift 0.484 ms, tightest of the campaign |
| **7B floor** (`window_7bfloor_20260729`) | Qwen2.5 7B decode floor, collected 2026-07-29 | **PASSED** | CLAIM-BEARING; governed extraction clean (`all_cells_extractable` true). Floors: absolute 6.294380135190098 J, comparative 13.998036715259254 J; absolute-cell member mean 192.38623252628366 J (n=10). NOT yet minted — `MINT-GENERALIZE-01` is OPEN and unblocked as of 2026-08-02 (gauntlet closed PR #93; D-088 no-mint condition lifted), so these figures live only in prose plus the out-of-repo custody extraction until that mint runs |
| **contrast** (`window_contrast_20260730`) | 40 contrast ABBA members + 7 references, 47 bundles, 1 supersession | **PASSED** | bracket drift 1.281 ms; contrast diagnostic 146.730349 J σ 0.241 (n=10 blocks) UNGATED — MANIFEST-CONTRAST-01 closed 2026-08-02 (PR #95); the gated claim now rides `MINT-GENERALIZE-01` then the D-095 chain |

Window B's cause is established and is NOT a clock problem: a GPU DVFM
power ramp that the rectangular-pulse fiducial estimator aliases into an
apparent onset shift (93.28% of the drift; the wall-clock term moved the
OPPOSITE way, −0.201464 ms). D-079 clause 3 adds a pre-flight screen that
- CI green on every merged head (PR #27's first merge-ref run failed on
  a cross-branch fixture interaction; fixed test-side, then green).
- Post-merge integration reviews (both waves): CLEAN, incl. an
  end-to-end mock campaign → strict → envelope-gate → pack → verify flow
  and a D-033 legacy-identity spoof probe that failed closed.
- `validate-bundle --strict` green over all 6 real corpus bundles under
  the new era rule (PR #22 live gate: 6/6 valid, tamper fails named).

## Known Workspace State

- (2026-08-02, CURRENT) `main` and `origin/main` at `bcbc10b`; working
  tree clean except the untracked private `CLAUDE.local.md` (Ed's;
  never commit) and `.desk/` (adjudication custody; never commit).
  PR #93 merged (the c3 branch is closed). Branch
  `impl/d100-bii-binding` exists in the session worktree
  `scratchpad/d100bii` holding the UNCOMMITTED, audit-pending
  D100-BII-BINDING-01 diff (envelope protocol failure; see §9).
- (2026-07-31, historical) `main` and `origin/main` were both at `6ed1625`:
  the PR #89 merge `7ee680c` (D5-J) plus the close-out commits
  `49c1876`, `0d0bd0b`, and `6ed1625`. Branch `impl/mint-tool` is MERGED
  (verified `git merge-base --is-ancestor impl/mint-tool main`), as are
  `impl/floor-mint` and `impl/floor-label-clean`; all three may be
  deleted. Their scratchpad worktrees are still registered (`minttool`
  plus ~11 review/pin worktrees under the `9c166892…` session dir, and
  prunable entries under `ad48bfae…` and `d714f367…`) — `git worktree
  prune` plus explicit removal is owed as housekeeping. The working tree
  is clean except for the untracked private `CLAUDE.local.md` (Ed's
  file; never commit it).
- (2026-07-28 late, historical) `main` and `origin/main` were at that
  session's bookkeeping commit atop the PR #87 merge `058c918`. Branch
  `impl/mint-tool` (pushed, then UNMERGED) held the 9-commit mint series
  `2a0ecbc..697f741` in worktree
  `/private/tmp/claude-501/-Users-edr-code-JouleWise/9c166892-d763-42c4-8cf7-383912f054c9/scratchpad/minttool`;
  canonical suite at its head `1d83d68` is UNVERIFIED (rerun was in
  flight at checkpoint). Branch `impl/floor-mint` is merged via PR #87
  and may be deleted. NOTE: a concurrent session force-rewrote main
  history this evening (content preserved; see run report Anomalies) —
  verify `git log` freshness before building on a cached head.
- (2026-07-27, historical) `main` and `origin/main` were at `7337b33`. Branch
  `impl/floor-mint` @ `617060a` is pushed and NOT merged; it carries the
  pre-mint floor schema hardening. Window C (+bound) and a10 (+bound)
  remain FULLY resident in the working tree (mint #1 inputs); windows B/D
  and all other runs corpora are locally pruned to small evidence files
  (traces archived + verified in iCloud, see "Disk" above), and custody
  material lives OUTSIDE the repo at `~/JouleWise-window-custody/` — an
  agent searching only the repo will wrongly report quarantined evidence
  missing. Disk has 115 GB free; a window writes ~6 GB. The next quiet-window operator must start
  from a separate clean, merged-main measurement checkout per
  `docs/phase_2/window_runbook.md`.
- The generated state-kernel regions in this file and `TASK_QUEUE.md` are
  IN SYNC with `docs/process/state_kernel.json`
  (`python3 scripts/gen_state.py --check` exits 0), and the kernel's own
  content was refreshed on 2026-08-01 (desk adjudication session):
  stamped `updated: 2026-08-01`, `latest_report` points at
  `docs/run_reports/2026-08-01-desk-adjudication-session.md`, the MET
  rows are folded in, the completed
  `FLOOR-LABEL-01`, `STACK-ID-BIND-01`, `P2-015`, and
  `COOLDOWN-JOIN-DA1-01` rows are retired to
  `TASK_QUEUE.md`'s completed table, and the post-mint intake
  (`COOLDOWN-JOIN-GAUNTLET-01`, `MINT-GENERALIZE-01`,
  `MANIFEST-CONTRAST-01`, `SUPERSESSION-DUP-REFUSAL-01`,
needs 2M baselines:     M10 later pairing-feasibility matrix + split runs
```

---

## Mission M0: Preflight (every session)

1. Read only the targeted `RUN_STATE.md` sections: `ACTIVE_STOP_CARD`
   if present, "Current Project Status", "Known Workspace State", and
   "What Is Next". If the stop card is ACTIVE, it overrides this
   playbook and the task queue until cleared.
2. Read `TASK_QUEUE.md`'s Current Queue and Do-Not-Do-Yet list.
3. Read the selected mission's own read-first list. Read `AGENT_PLAN.md`
   only at phase starts or when the project structure changes. Consult
   `docs/decision_log.md` by targeted decision ID, not as a whole-file
   intake step.
   If the session involves delegation, review, or multi-stream work, also
   read `docs/orchestration.md` (the process layer) — not optional for
   landing code.
4. Check workspace state with `git status --short --branch`; inspect
   recent commits only when the handoff or mission needs them.
5. `python3 -m unittest discover -s tests` — expect `Ran <N> tests` (N per `RUN_STATE.md` Current Verification; `, OK
   (skipped=10)` with zero expected failures as of 2026-07-08 after
   P2-013/P2-014 and the C-011 rigor mechanics. The skips are the `[analysis]`-extra chart tests plus one
   optional-jsonschema test. A red suite is itself the mission: stop and fix
   or report.
6. Review `docs/risk_register.md` at phase starts, before hardware tasks,
   when a trigger fires, or if >14 days passed since the last run report
   with no break recorded in `docs/milestones.md`.
7. At session end, always: update `RUN_STATE.md`, update `TASK_QUEUE.md`,
   write a dated run report in `docs/run_reports/`, update the phase exit
   checklist for anything that closed, and `PROJECT_STATUS.md` if
   advisor-visible state changed. Commit when the user asks or has
   standing-approved it.

Environment cautions:

- The repo must stay at a non-iCloud path (`~/code/...`; R-017). If you
  see `Operation not permitted` on reads inside the repo, stop, wait for
  the lock to clear, re-run the suite, and record the incident.
- CI installs no extras; every new test must pass on a bare Python
  (lazy imports, `skipUnless` for optional deps — D-009).
- Schema changes are additive-only until v0.2 (R-015/D-008).

---

  the 2M campaign; otherwise declined as premature.
- Cold-load / model-load-energy capture — DECLINED for the capstone scope
  (CP-5 deferral made permanent unless an AP row claims it; warm-cache
  protocol is the declared scope).

- CI-003 developer polish (console script, macOS CI job, Ruff, coverage thresholds) — SHELF, trigger: G6-equivalent reference release (hardening adjudication C10).
- DOC-010 historical-archive audit — SHELF, trigger: DOC-008 state kernel proven in use (hardening adjudication C11).

## Current Do-Not-Do-Yet List

- (satisfied 2026-06-12) The mock bundle/reducer path and report generator
  now exist; dashboard/report work is no longer blocked.
- (satisfied 2026-06-12) The mock lifecycle is runnable, so live
  MLX/powermetrics implementation may proceed once its hardware gates open
  (P1-002 + D-016); follow `docs/phase_2/hardware_slice_implementation_guide.md`.
- (resolved 2026-06-12) Hailo feasibility has a verdict
  (`unsupported_workload`); do not implement a Hailo backend — report it as
  an applicability finding.
- Do not implement schema v0.2 before Phase 3 Stage 3.1 (design is fixed in
  D-008; implementation waits).
- Phase 3 DESK feasibility spikes (Stage 3.0.x) may run now — their gate
  (2G/2I + model) is open. Do not start Phase 3 DATA collection, hardware
  pairings, or borrow-window scheduling before 2M baselines and the Stage
  3.0 verdicts exist (C-007 wording fix; was previously stated as a
  blanket Phase 3 hold that contradicted the queue).
- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
  rehearsed runbook exist (R-006).
- Do not start Phase 3 live-split work (3.3) before offline replay (3.2) has
  produced data.
- Do not close D-016 (model selection) without P1-001 supervisor scope or an
  explicit user go-ahead.
- (satisfied 2026-07-06) Slice 2N landed; 2G/2H may start once their own
  gates (D-016 + `[mac]` install; privileged sample + D-004 sudoers) open —
  build on the post-2N seams (RunContext raw evidence, D-026 markers,
  D-027 rail rows, 2N.3 observed-token fallback).

## Queue Maintenance

At the end of substantial work:

- Update live status, rank, dependencies, and new tasks in
  `docs/process/state_kernel.json`.
- Remove terminal tasks from the kernel only after their owning completion
  evidence supports closure; preserve the dated Completed row here.
- Run `python3 scripts/gen_state.py`; never hand-edit generated queue or
  restart rows.
- Keep hand-authored edits here to policy, completed/history records, and
  non-selection context.

## Intake Batch Owed To The Kernel (2026-07-30/31)

**PARTIALLY FOLDED 2026-07-30.** Six rows —
`COOLDOWN-JOIN-GAUNTLET-01`, `QA-10A-JOIN-OMISSION`,
`QA-10B-EXISTING-RETRY`, `MINT-GENERALIZE-01`, `MANIFEST-CONTRAST-01`,
and `SUPERSESSION-DUP-REFUSAL-01` — were folded into
`docs/process/state_kernel.json` on 2026-07-30; their staged rows were
| EXACT-SET-REGRESSION-01 | P2 Next Slice | [AGENT] | Review finding **S2** — exact-set regression. **Detail owed** (same caveat as B2): the ledger names the row but not its content. Likely adjacent to D-086 root cause 1 (exact-set vs governed-subset matching when `--evaluation-basis-sha256` is omitted), but that adjacency is **inference and must be confirmed against the packet**, not assumed. | Not yet acceptance-specified — promote to READY only after the S2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph |
| COLLECTOR-NIT-B1 | P4 Polish | [AGENT] | Review finding **B1** collector nit (distinct from the refuted B1 `device.boundary` placeholder finding — do not conflate). **Detail owed**, same caveat as B2/S2. | Not yet acceptance-specified. | Session ledger, F2 disposition paragraph |
| SITE-ROADMAP-PAGINATE-01 | P3 Tooling | [AGENT] | Paginate or shard the site roadmap page: `roadmap.html` emits one card per live kernel row and now sits at 29,620 of the 30,000-byte capsule shard budget (98.7%) after the 2026-07-30 kernel fold — the NEXT intake fold breaks `CapsulePackError`. | `build_site` succeeds with at least 10 additional live kernel rows; no shard exceeds budget; existing roadmap content preserved. | Kernel-refresh finding 2026-07-30 (session report) |
| DOC-RUNSDIR-ABS-01 | P4 Polish | [AGENT] | Tool contract doc note: the extraction CLI's `--runs-dir` **must be an absolute path**. Document it at the tool contract, and consider a fail-closed check rather than leaving it as operator lore. | Doc note landed; optionally a refusal on a relative `--runs-dir` with a regression. | [D-086](docs/decision_log.md) (queued from lieutenant findings) |
| LITREAD-VERIFY-01 | P4 Polish | [AGENT] | Pre-submission verbatim re-verification of the two load-bearing related-work sources against the **PDFs of record**: TokenPowerBench (arXiv **2512.03024**) and "The Illusion of Power Capping in LLM Decode" (arXiv **2605.11999**). Both were read in full text during the sweep, but through WebFetch's extraction model against the arXiv HTML renders. | Every quote and number cited in a submission re-checked against the PDF. **Note the id correction:** TokenPowerBench is 2512.03024; 2605.11999 is the Illusion paper — earlier handoff text conflated the two. | [Sweep-techniques access summary](docs/run_reports/2026-07-30-sweep-techniques.md) |

## Current Queue

The generated region below is the sole live queue and source of truth for
work selection. Edit the kernel and regenerate; do not hand-edit its rows.

Superseded (2026-07-15, WO-012; D-043): Q4/P2-019 sample size is frozen in the hash-bound analysis registry before outcomes, and outcome-dependent growth permanently demotes the contrast to exploratory; see `docs/contracts/analysis_plans.md` §Required fields.

Superseded (2026-07-15, WO-017; D-043): P2-027 publication and uninvolved-party re-reduction are optional owner-directed evidence-handoff work, not the default reproducibility or project-completion gate; see `docs/specs/c027/rpt-001_report_vertical_slice.md` §0.4 and `docs/contracts/publication_privacy.md` §Publication boundary.

<!-- BEGIN GENERATED: state-kernel current-queue -->
<!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py. Do NOT hand-edit between the markers; edit the kernel and regenerate. -->

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-08-05).

Generated compatibility table for repository consumers; the lane tables below are the detailed view of the same kernel state.

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---|---|---|---|---|---|
| E1 | P1-008 | P1 Phase Gate | READY [ED-EXTERNAL] | Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability). | Colloquium/report dates plus borrow window in docs/milestones.md; phase targets derived; acceptance-bar notes beside the P1-001 scope notes. Evidence: Dates + borrow window in docs/milestones.md; Derived phase targets; Acceptance-bar notes beside P1-001 scope notes. Authority: [Milestones + R-012](docs/milestones.md). Acceptance: [P1-008 acceptance](docs/process/state_kernel.json). Note: R-012 is the biggest active management risk for an undergrad timeline. |
| E2 | P2-027 | P2 Next Slice | READY [ED-EXTERNAL] | Publish a privacy-transformed, integrity-verified three-bundle pack from a clean tagged commit and obtain one documented external re-reduction by an uninvolved party. | Published pack plus a documented external re-reduction; until then the auditability claim stays L0-scoped. Evidence: Published pack; Documented external re-reduction. Authority: [C-020 + C-027 NEG-9](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-027 acceptance](docs/process/state_kernel.json). Note: Environment locks, pack preparation, integrity tooling, and fail-closed privacy transformation are merged; publication and external re-reduction remain ED-EXTERNAL. |
| E3 | P1-001 | P1 Phase Gate | READY [ED-EXTERNAL] | Capture supervisor approval and scope notes. | Dated notes in the Phase 1 exit checklist; unblocks full D-016 closure (P2-004). Evidence: Dated notes in docs/phase_1/phase_1_exit_checklist.md. Authority: [R-001](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: User-deferred 2026-07-06; R-001 mitigation holds: all work stays harness-shaped. |
| E4 | P1-003 | P1 Phase Gate | READY [ED-EXTERNAL] | Record the wall-meter decision: meter make/model or unavailable verdict plus measurement/export method. | Exit-checklist wall-meter section filled; informs D-018 boundary calibration. Evidence: Wall-meter section of the Phase 1 exit checklist filled. Authority: [D-018/C-003](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Elevated value: gates Q6 boundary sensitivity (C-003). |
| E5 | P1-004 | P1 Phase Gate | READY [ED-EXTERNAL] | Fill the network/interconnect topology plan: physical topology, link-speed paths, throughput method. | Network section of the Phase 1 exit checklist recorded. Evidence: Network section of the Phase 1 exit checklist recorded. Authority: [R-011](docs/risk_register.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Partial. |
| E6 | P1-006 | P1 Phase Gate | READY [ED-EXTERNAL] | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |
| Q1 | MET-WINDOW-C-01 | P1 Phase Gate | BLOCKED — FROZEN-PLAN-READINESS-RECORD (A reviewed FROZEN-PLAN READINESS RECORD exists before any collection night: frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight, launcher-verified), ED-5A (Ed section-5A window prep FRESH POST-MOVE (the 2026-08-02 laptop move invalidated settled-machine conditions; network time off, AC, settled machine, walk-away)) [QUIET-MAC] | Execute a reviewed fresh-claim collection plan beginning with Window C: no Window B member enters a replacement claim basis; split prospectively across windows C and D if the complete replacement cannot fit the 2-4 hour envelope with at least 20 percent failure margin. | The fresh-claim metrology plan replaces every still-desired Window-B claim component without using any Window-B member, under reviewed frozen-plan and validated-window controls. Evidence: A fresh-claim plan recollects every still-desired Window-B claim component beginning with Window C; no Window B member enters a replacement claim basis; The fresh plan includes the still-required C2, C4, and C5 collection scope under the frozen-plan discipline, split prospectively across windows C and D if one window cannot retain at least 20 percent failure margin inside the runbook's 2-4 hour envelope; Window operated under the validated protocols: bird-SIGSTOP with identity custody, guarded launcher, one-line arm messages with zero output streaming during idle-gate exposure, third-failure salvage rule; Whole-window verdict emitted by machinery that has passed MET-VERDICT-ADJ-01 adjudication; supersessions recorded once, pre-verdict; both roots backed up rc=0. Authority: [D-113 clauses 7-9 fresh-claim reset, readiness fence, and prospective C/D split](docs/decision_log.md). Acceptance: [MET-WINDOW-C-01 acceptance](docs/process/state_kernel.json). Fence: A window-C dangler seeking the b-ii mechanical license before D100-BII-BINDING-01 closes RETURNS TO THE GATE; the window itself may run (D-106 revisit clause). Fence: Before any collection night, the ordinary launcher verifies a reviewed FROZEN-PLAN READINESS RECORD binding the frozen plan digest, issued calibration acceptance artifact, clean pinned head, empty waivers, fresh roots, and environment preflight (D-113 clauses 8-9 hard start fence). Fence: Plan root assembled and frozen before measurement; no plan edits after freeze (D-096 frozen-plan ratification). Fence: Zero agents AND zero operator output streaming during measurement idle gates; arm messages are one line; bird-SIGSTOP protocol with identity custody and fail-safe CONT trap on all exit paths (2026-08-01 run report: streaming-during-idle-gate hazard + bird-SIGSTOP protocol). Note: D-113 clauses 7 and 9: the former remainder-only scope is SUPERSEDED. A fresh-claim plan is required; no Window B member enters a replacement claim basis. If the full replacement exceeds the runbook's 2-4 hour envelope with at least 20 percent margin, split it prospectively across windows C and D. |
| Q2 | P2-006 | P2 Next Slice | READY [QUIET-MAC] | Homogeneous baselines (slice 2M) on the Mac target: Window A two-model campaign with drift-sentinel profiles, then docs/phase_2/baseline_results.md with variance plus prefill/decode comparison. | Strict-valid reducer-0.5.2/0.6.2 campaign bundles with counterbalanced order and drift sentinels; interpretation uses campaign claim_readiness plus the merged fail-closed analysis engine. Evidence: Strict-valid campaign bundles under the fixed validator; Counterbalanced order manifest + drift sentinel positions recorded; baseline_results.md with variance + prefill/decode comparison. Authority: [Phase 2 plan + analysis plans](docs/phase_2/phase_2_plan.md). Acceptance: [Phase 2 exit checklist](docs/phase_2/phase_2_exit_checklist.md). Note: Software interpretation gates are satisfied; Window-A floors landed 2026-07-31 (mint #1 mainline), so only the campaign remains. |
| Q3 | P2-010 | P2 Next Slice | READY [QUIET-MAC] | P2-010b remainder: affine smoke campaign execution (B=5) plus envelope-gate verdict on its bundles, on a quiet-window tail. | joulewise envelope-gate emits the D-036 verdict from strict-valid smoke bundles; campaign acceptance in AP-5. Evidence: D-036 verdict from strict-valid smoke bundles; AP-5 campaign acceptance met. Authority: [AP-5 + affine stream log](docs/contracts/analysis_plans.md). Acceptance: [P2-010 acceptance](docs/process/state_kernel.json). Note: Envelope-gate script merged 2026-07-09 (PR #23); only the campaign remains. |
| Q4 | P2-019 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | q4_l3_shape_grid_v1 campaign (Window B, AP-1, two models, n sized from Window A): 4x3 prompt/decode grid with holdouts (512,256) and (4096,512); categorical-additive fit first; 8192-prompt anchor on small+mid models feeding D-048 (CP-6). | Grid campaign lands per AP-1; top-up near-floor cells before L3 wording. Evidence: AP-1 grid campaign bundles; Holdout cells honored; 8192 anchor cells on small+mid models. Authority: [AP-1](docs/contracts/analysis_plans.md). Acceptance: [P2-019 acceptance](docs/process/state_kernel.json). |
| Q5 | P2-020 | P2 Next Slice | BLOCKED — P2-006 (Window-A baselines size n) [QUIET-MAC] | Content-sensitivity sentinel campaign (Window B, AP-6): five equal-shape ids-native conditions, n sized from Window A; request-energy deltas and MDE verdicts. | Campaign lands per AP-6; the AP-6 non-generalization caveat applies (D-046). Evidence: Five equal-shape ids-native conditions; Request-energy deltas + MDE verdicts. Authority: [AP-6 + D-046](docs/contracts/analysis_plans.md). Acceptance: [P2-020 acceptance](docs/process/state_kernel.json). Note: Generator merged (PR #19), manifests ready (PR #26); a tiny AP-6 pilot may ride a Window-A tail (CP-6). |
| Q6 | P2-012 | P2 Next Slice | BLOCKED — P2-006 (identification-core runs after Window A) [QUIET-MAC] | Identification-core campaign (jw_mixed) after Window A; natural-EOS pilot plus full panels in later phases. | Campaign bundles strict-valid per AP-4; no category claims outside matched strata. Evidence: Strict-valid bundles per AP-4; No category claims outside matched strata. Authority: [AP-4 + D-039/D-040](docs/contracts/analysis_plans.md). Acceptance: [P2-012 acceptance](docs/process/state_kernel.json). Note: Manifests generated + regenerated (PR #26); runner/runtime/validator hash guards merged (PRs #24/#27). |
| Q8 | P2-046B | P1 Phase Gate | READY [QUIET-MAC] | Execute the frozen load-transition alignment harness on the real Mac and adjudicate the production interval-support bound from offset and residual artifacts. | Real-Mac counterbalanced transitions validate or widen the P2-038 conservative interval-support bound; physical evidence replaces the PROVISIONAL Part-A verdict. Evidence: Counterbalanced real-Mac transition artifacts; Offset, residual, and conservative-bound verdict; P2-038 bound cited or amended. Authority: [Hardening adjudication C6](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-046B acceptance](docs/process/state_kernel.json). Fence: Do not promote Part-A fixture evidence or retain PROVISIONAL interval support after a conflicting physical verdict (Hardening adjudication C6). Note: Part A merged in PR #50; Part B is quiet-machine physical execution. |
| Q9 | P2-047B | P2 Next Slice | BLOCKED — P2-047A (frozen controller-overhead harness exists) [QUIET-MAC] | Run the frozen controller capture-overhead ABBA on the quiet Mac and record the floor-governed overhead verdict. | Real floor-governed ABBA execution yields a named overhead verdict with instrumented-stack scope unless a separate subtraction model is justified. Evidence: Floor-governed quiet-Mac ABBA bundles; Named overhead verdict; Instrumented-stack scope or separately justified model. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047B acceptance](docs/process/state_kernel.json). |
| A0 | P2-035 | P3 Research Expansion | READY [AGENT] | RQ-ENERGY-VARIANCE promotion prerequisites: council round plus harness gaps G-RQVAR-* (per-bundle sampler seed recording, forced-token replay mode, replay manifests). | Promotion decided per registry rules; harness gaps closed before promotion. Evidence: Registry promotion record per docs/research_question_bank.md rules; G-RQVAR-* harness gaps implemented with tests. Authority: [RQ-ENERGY-VARIANCE candidate design](docs/specs/rq_energy_variance_design.md). Acceptance: [P2-035 acceptance](docs/process/state_kernel.json). Fence: C-004 quarantine binds; no promotion before floors exist (C-004 quarantine). |
| A2 | QUIET-GUARD-01 | P1 Phase Gate | READY; GATES live_promotion: T3-CHAR-PAIR-01 [AGENT] | Quiet-guard work order (full gauntlet): host-wide quiet lease, refuse-at-arm, characterized resident watcher; plus Ed requirements recorded 2026-08-03 — t3-armed operation (a t3-launched claude session arms a detached guarded chain, then self-quits and quits t3 with a survivor inventory), t3-relaunch-on-close, and README-banner signaling. | The quiet guard lands through the full C-028 gauntlet with the host-wide lease, refuse-at-arm, characterized resident watcher, and all three Ed-required t3 behaviors working end to end. Evidence: Commit 1 only: host-wide quiet lease implemented and enforced; Refuse-at-arm: arming refuses when the host is not quiet (usable by the ordinary guarded-shell window launcher); Installed-INACTIVE: no arming path, no production lease, live_promotion=false; Seven focused-audit blockers closed (priv-esc interpreter, validate/install TOCTOU, arbitrary-root initializer, macOS process identity, boot/hostname wedge, decision entry, independently-pinned tests); Full gauntlet on the landed commit: independent audit + delta re-audit of every fix round. Authority: [Ed directive 2026-08-03 ~23:55 (t3-drive chain is the critical path; non-in-flight work paused) + t3-doctrine gate synthesis + synthesis-exhibits SX5](docs/process_traces/2026-08-03-t3-doctrine-gate/SYNTHESIS.md). Acceptance: [QUIET-GUARD-01 acceptance](docs/process/state_kernel.json). Note: 2026-08-05: DESCOPED by Ed's directive (t3 control-plane build-out not worth its cost; t3 stays the INTERACTIVE control plane, t3-resident-during-windows dropped; windows return to the zero-agent guarded-shell path). ROW RE-SCOPED TO COMMIT 1 ONLY: the host-wide quiet lease + process census, installed-INACTIVE. Retained because it has non-t3 value — mechanical refuse-at-arm for the ordinary guarded window launcher, replacing procedural eyeballing. SHELVED: commit 2 (launcher interception), commit 3 (t3 handoff + resident watcher), commit 4 (t3-relaunch + README banner projection + all credential handling). In flight at checkpoint: Sol fix round closing 7 audit blockers; work UNCOMMITTED in scratchpad/quietguard (branch impl/quiet-guard); harvest scratchpad/qg-fix-out.md. |
| A3 | FLOOR-BIND-01 | P1 Phase Gate | READY [AGENT] | Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions. | Floor/MDE artifacts stop being self-attesting: claim consumption authenticates admissible widths and complete governed campaign membership against extraction evidence, retiring registered limitation L1. Evidence: Canonical floor cells bound to their extraction report and source-member disposition (or extraction gates and widths rederived at binding); Binding refuses on any stored width/corner mismatch or campaign-membership deviation; Integration regressions reject width substitution and member omission end-to-end. Authority: [D-078 clause 8 (confirmation round 9, registered limitation L1)](docs/decision_log.md). Acceptance: [FLOOR-BIND-01 acceptance](docs/process/state_kernel.json). Fence: Until this row closes, claim-bearing analysis may consume floor artifacts only from same-custody-session governed extraction; standalone artifacts are non-claim-bearing (D-078 clause 8 L1). Note: Minted 2026-07-22 from confirmation round 9 (CR9-1, lead-reproduced). L1 workflow rule mitigates until closed. |
| A4 | AXI-SB-ADAPTER | P2 Next Slice | READY [AGENT] | Implement the static-batch Mac adapter follow-on minted by the AXI-SB supported verdict: batch_size configuration knob, per-sequence request-scoped token events per the AXI-SA contract, realized-vs-configured batch recording, and structured memory-fit outcomes, with strict-valid mock or smoke bundles and no energy claims. | The follow-on static-batch adapter turns the AXI-SB supported verdict into an instrumented batch_size-configurable Mac runtime path emitting per-sequence AXI-SA events, with memory-fit failures structured and zero claim or quiet-Mac consumption. Evidence: A batch-capable Mac adapter exposes a batch_size configuration knob and emits per-sequence request-scoped token events conforming to the landed AXI-SA event contract, validated by strict bundle validation on a mock or live smoke bundle; Realized batch size is recorded alongside configured batch size, and structured memory-fit failures are captured as data rather than crashes; No energy claim, campaign scheduling, or quiet-Mac consumption occurs in this row; AP-BATCH execution remains separately floor-gated per AXI-SE. Authority: [AXI-SB verdict document (supported; mint-on-supported follow-on)](docs/specs/axi/sb_static_batch_verdict.md). Acceptance: [AXI-SB-ADAPTER acceptance](docs/process/state_kernel.json). Fence: Build on the verified BatchGenerator path with per-request observability; a Python loop over singleton calls is not a batch adapter (AXI-SB verdict document classification and scope). Fence: Keep continuous batching deferred and do not infer coalescing, scheduler-optimum, or offered-load claims from static-batch work (D-070 static-batch scope). Fence: Window A retains every quiet-Mac measurement slot; adapter implementation and mock or smoke validation are agent-lane work and consume no quiet-Mac campaign time (D-070 Window A ownership). |
| A5 | TEST-SPEED-01 | P2 Next Slice | READY [AGENT] | Cut suite wall-clock (three Ed-ratified levers, 2026-08-03): collect per-module timing data with the recovered profiling scripts, implement the shard-runner and the PR-fast/full tier split from the data, and evaluate Blacksmith runners. | The three Ed-ratified levers land: timing data drives a shard-runner plus PR-fast/full split with the full suite still holding every authoritative gate, and the Blacksmith runner option is evaluated on evidence. Evidence: Per-module timing corpus collected on a quiet bench (the recovered Sol profiling scripts; timings.jsonl + summary.json banked under .desk/) identifying the slow tail by module and by test; Shard-runner and the ratified PR-fast/full tier split implemented from the data: the fast tier gates PRs, the FULL suite remains the gate for merges, verdicts, and audited heads; zero test deletions; Blacksmith runner evaluation recorded with an adopt/defer recommendation and measured latency/cost comparison against GitHub-hosted runners. Authority: [Ed ratification 2026-08-03 (three levers: suite-speed priority, PR-fast/full split, Blacksmith runner evaluation); origin row in the 2026-07-28 report](docs/run_reports/2026-07-28-floor-mint-implementation.md). Acceptance: [TEST-SPEED-01 acceptance](docs/process/state_kernel.json). Fence: No test deletions, and the fast tier never substitutes for a required full-suite gate: merges, whole-window verdicts, and audited heads keep the full suite (D-061 zero-deletion clearance; the full suite as the authoritative gate). Note: 2026-08-03: timing DATA collected (quiet bench, 93 modules, 695s serial; raw in .desk/test-speed-consult/timings-20260803.jsonl) and DESIGN done (.desk/test-speed-consult/DESIGN-from-timing-data.md). Findings: suite is a 2-module problem (run_campaign 182s + p2038 133s = 45%); module-atomic sharding CAPS at 182s so those two must be split by TestCase class; shard-runner + splits -> ~87s wall @8 workers (6.5x); fast tier (drop 11 heavy integ modules) -> 25-40s PR feedback with the full suite still the merge gate. Blacksmith (lever 3) NEEDS ED (account/cost; likely marginal once sharded). Implementation queued: scripts/shard_tests.py + class-split + CI matrix — mechanical, delegatable, zero deletions (D-061). 2026-08-04: PHASE 1 LANDED — PR #98 MERGED (9b02539): module-atomic shard-runner + 8-way CI shard matrix, main CI green under it (~15min -> ~6min proven); worktree/branch pruned. Remaining scope: class-split of the two heavy modules (Phase 2), fast PR tier (lever 2), Blacksmith runners (lever 3, NEEDS ED). |
| A6 | AXI-SD | P2 Next Slice | READY [AGENT] | Prepare the matched dense/MoE pair proposal with the consult's pre-registered scorecard, including auditable active-parameter calculation and the D-016 cross-target 8 GB-fit question for Ed, plus a mirrored and hashed 2-to-3-level quantization ladder governed by C-023-QUALITY-EQUIV-QUANT. | A pre-registered matched dense/MoE selection scorecard and quantization ladder are artifact-complete before energy data, with active-parameter semantics explicit and the D-016 8 GB-fit choice surfaced to Ed. Evidence: A pre-data dense/MoE scorecard fixes family and tokenizer, runtime and quantization recipe, output policy, active-parameter calculation including shared experts and router top-k, artifact revisions and hashes, quality band, memory headroom, and fallback hierarchy; The scorecard surfaces to Ed whether D-016's cross-target 8 GB fit can be met or a separate Mac-only AXI pair or explicit D-016 amendment is needed; total-parameter fallback is labeled as a different estimand; A mirrored and hashed 2-to-3-level quantization ladder predeclares the C-023-QUALITY-EQUIV-QUANT identity and quality-equivalence gate before energy results. Authority: [AXI handoff work program S-D](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SD acceptance](docs/process/state_kernel.json). Fence: Do not silently substitute total-parameter matching for active-parameter matching; label the fallback as a different estimand and present the D-016 or separate-pair choice to Ed (Binding AXI xhigh consult). Fence: Prepare the pair proposal and scorecard but do not finalize D-016 or the Mac-only alternative without Ed (D-070 D-016 ownership). Fence: Window A retains every quiet-Mac measurement slot; AXI-SD is independent agent-lane desk and artifact work and consumes no quiet-Mac campaign time (D-070 Window A ownership). |
| A7 | AXI-SE | P2 Next Slice | READY [AGENT] | Finalize the AXI analysis plans after P2-015: AP-BATCH with counterbalanced all-B blocks, affine primary and lack-of-fit rule, structured B=16 memory outcome, and provisional n=5 under D-062; complete AP-SPEC and add AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, plus the AP-5 dense/MoE 2M rider with the consult's floor and ownership closures. | The complete AXI analysis-plan family closes AP ownership for batching, speculation, quantization, reasoning variance, MoE-by-batch, and the AP-5 MoE rider with prospective floor, identity, multiplicity, model-fit, and structured-memory-outcome rules. Evidence: AP-BATCH freezes five counterbalanced all-B blocks over a fixed balanced equal-shape request roster, an all-B affine primary with predeclared lack-of-fit, an estimated-intercept interpretation, structured B=16 memory failure, latency bounds, and n=5 as provisional under D-062; AP-SPEC completion preserves S-A's gross request and committed-output primary denominators, accepted-draft diagnostic, exact-token identity gate, separate MTP and draft families, floor mapping, pairing, multiplicity, and divergence dispositions; AP-QUANT, AP-REASON-VARIANCE, AP-MOE-BATCH, and the AP-5 MoE 2M rider close the all-axis ownership gap, with routing-mechanism claims allowed only when auditable expert evidence exists and every plan finalized only against P2-015 floors. Authority: [AXI handoff work program S-E](docs/axi-handoff.md#4-work-program-post-audit-clearance-streams). Acceptance: [AXI-SE acceptance](docs/process/state_kernel.json). Fence: Do not promise a confirmatory breakpoint or fixed n=5 before floors; freeze all-B affine lack-of-fit, final n, floor transport, multiplicity, and forbidden upgrades prospectively (Binding AXI xhigh consult). Fence: Keep every plan at or below L2 and preserve static-batch scope, exact claim boundaries, and structured unsupported or not-resolvable outcomes (D-070 all-axis claim posture). Fence: Window A retains every quiet-Mac measurement slot; AXI-SE is agent-lane analysis-plan finalization after P2-015 and authorizes no measurement campaign by itself (D-070 Window A ownership). |
| A10 | SUPERSESSION-DUP-REFUSAL-01 | P1 Phase Gate | READY [AGENT] | Rule on and then implement write-time refusal in the supersession recorder, which today appends silent duplicate records when run more than once for a member and voids campaign membership downstream; the ruling is the first half of the deliverable. | A repeat recorder invocation for the same member refuses instead of appending a duplicate record. Evidence: The write-time refusal ruling is recorded in the decision log before any implementation; A regression asserts that a second recorder invocation for the same member refuses. Authority: [D-086 supersession-aware cooldown-evidence join (recorder duplicate-append defect)](docs/decision_log.md). Acceptance: [SUPERSESSION-DUP-REFUSAL-01 acceptance](docs/process/state_kernel.json). Fence: Until the refusal lands, run the supersession recorder exactly once per member (D-086 operator mitigation). Note: Minted 2026-07-30 from the D-086 arc; ruling-first, no implementation before it. |
| A11 | T3-PROV-SCHEMA-01 | P2 Next Slice | READY [AGENT] | Implement the tracked four-axis provenance record with authority_class and the ingestion-event schema, then make reverse-consult admission consume authoritative launch-route and owner_kind evidence so bridge §8's transitional convention ends. | The four-axis provenance plus ingestion-event schema ends bridge §8's transitional convention by mechanically enforcing reverse-consult eligibility from authoritative route and ownership evidence. Evidence: A tracked provenance record represents the four axes control_plane, transport, authority_class, and governance, with authority_class explicit; A tracked ingestion-event schema binds native session identity, output digest, lead disposition, and tracked process-trace location; Reverse-consult admission consumes authoritative launch-route and owner_kind evidence rather than self-reported headers; Rejection regressions fail closed on delegated, unknown, or contradictory provenance and prove that merely persisting the schema cannot end the transition. Authority: [Bridge protocol §8 transitional reverse-consult enforcement follow-on](docs/contracts/bridge_protocol.md). Acceptance: [T3-PROV-SCHEMA-01 acceptance](docs/process/state_kernel.json). Fence: The transition ends only when admission consumes authoritative launch-route and owner_kind evidence with rejection tests; defining or persisting the schema alone is insufficient (Bridge protocol §8 fail-closed transition rule). Note: Bridge §8 currently validates only self-reported headers; consumption-side fail-closed is the actual protection until this row supplies real enforcement. |
| A12 | MINT-GENERALIZE-01 | P1 Phase Gate | BLOCKED — D-110 (The remaining D-110 re-mint conditions hold before ANY further mint, including the governed 7B mint: (b) the acceptance artifact is ISSUED after verified R2 backfill and deterministic ledger bootstrap; (c) the evidence_root_id validator pin is widened) [AGENT] | Generalize the mint beyond the mint-1 pair: scripts/mint_floor_artifact.py is hard-pinned to the p2_015, a10, and window-C evidence (cell id, plan sha, both order-manifest ids, the two member counts, the expected operative-floor text), so build a sibling taking those pins per plan and carrying the 7B mint's remaining scope. | A generalized mint sibling takes the mint-1 hard pins per plan so a second floor artifact can be minted without weakening the pre-registration gate. Evidence: A 7B decode-floor artifact mints from qwen25_7b_decode_floor_v1 evidence with its own hard six-decimal operative-floor literal supplied per plan, never derived inside the mint path; The pre-registration gate passes as-embedded and validate_floor_artifact returns no findings; The generalized path mints byte-identical to the reviewed core from the same inputs on the same integration tree (core-vs-wrapper parity per D-109 addendum II; NOT a match against historical mint-1 digests, which D-110's corrected re-mint may legitimately change). Authority: [splitwise_decode_v1 campaign doc section 2 Blocker A (mint pins); D-082, D-084, D-085 Q6](docs/phase_2/splitwise_decode_campaign.md). Acceptance: [MINT-GENERALIZE-01 acceptance](docs/process/state_kernel.json). Fence: Generalize the plumbing, never the pins: six-decimal floor literals and lead-verified digests stay supplied per plan and hard-checked in-tool (D-082 and D-084 operative-floor pins). Note: 2026-08-03: D-110 (sweep finding RT-1/RT-2): mint #1 is retroactively NON-CLAIM-BEARING (taint-and-remint); the night consult's conditional 7B-mint license is SUSPENDED. The mint-1 byte-compare replay completed BYTE-IDENTICAL at pinned 3de370ec (all four digests; docs/process_traces/2026-08-03-q1-remint-bytecompare/). 2026-08-05: condition (a) is satisfied by merged PR #100. Condition (b) preparation is complete and its verification blocker is resolved: the B1 disposition is lead-ruled 30/2/6 and deterministic bootstrap is implemented on impl/ledger-bootstrap, under audit. Condition (c) is in flight on impl/validator-rootpins. The row remains hard-blocked on the still-pending D-110 (b)+(c) completion gate. |
| A13 | CODEX-BRIDGE-SANDBOX-01 | P2 Next Slice | READY [AGENT] | Correct scripts/codex-bridge review-mode sandbox enforcement: pass the read-only sandbox flag instead of launching workspace-write while recording read-only metadata. | codex-bridge review launches read-only exactly as its audit manifest claims, with regression coverage binding recorded and effective sandbox values. Evidence: scripts/codex-bridge review passes the read-only sandbox flag to every non-app review launch; The review audit manifest records the sandbox actually supplied to the launch; A regression proves the recorded review sandbox and launched sandbox are both read-only and cannot drift apart. Authority: [2026-08-05 live inspection: review records observer_sandbox=read-only but the non-app launch omits -s read-only](scripts/codex-bridge). Acceptance: [CODEX-BRIDGE-SANDBOX-01 acceptance](docs/process/state_kernel.json). Note: Caught live 2026-08-05: observer_sandbox is set to read-only, but the non-app review invocation omits the sandbox flag, so audit metadata misstates enforcement. |
| A14 | COLDGATE-HANDOFF-01 | P2 Next Slice | READY [AGENT] | Build runner-owned sealed-byte judge handoff: capture immutable in-process packet, charter, and exhibit byte snapshots; compute digests over those exact buffers; construct judge input from the same buffers; and specify and test transport byte-to-request binding. | The convening runner delivers exactly the bytes the validator observed, with immutable snapshot-to-judge transport binding and a judge-identity-bound runner receipt. Evidence: Deterministic post-hash path replacement delivers the original immutable snapshot or refuses without invoking the judge; Same-inode mutation through a second descriptor never delivers mutated bytes under the old receipt; Judge-received payload hashes equal the receipt hashes and the runner receipt binds the judge request or session identity. Authority: [2026-08-05 COLDGATE-VALIDATOR F3 consult Q2 handoff ruling and tests](docs/process_traces/2026-08-05-cgv-f3-consult/CONSULT-REPORT.md). Acceptance: [COLDGATE-HANDOFF-01 acceptance](docs/process/state_kernel.json). Fence: Until this row lands, no validator PASS may be used to convene a cold judge (2026-08-05 F3 consult standing operational constraint). Note: Design warnings: holding file descriptors open does NOT seal bytes because a second descriptor can mutate the same inode; path-based launch-time revalidation alone leaves a revalidate-to-read race. Pending-ratification payload carried by this row: the proposed amendment to docs/process/coldgate_charter_registry.md separating validator observation from runner custody. The registry is Ed-ratified and is NOT edited by this or any session without a cold-gate/Ed ratification. |
| A15 | C3-RECOGNIZER-EXACT-01 | P1 Phase Gate | READY [AGENT] | Close the two D-105-registered recognizer-exactness blockers: exact escape-ordering completion-feasibility (F1) and the documented decidable superset number grammar (F2, with the D-104 cl.2 subset-direction amendment), plus the bundled F3/N2 release-path hygiene if not already landed. | The two registered recognizer-exactness blockers (escaped-key ordering; number-prefix over-acceptance) close together under D-105's refuter-amended criteria with an independent audit. Evidence: F1 closes via the exact escape-ordering completion-feasibility procedure (hex-digit interval derivation, surrogate-pair arithmetic, prefix-extension rule) with both registered counterexamples pinned verbatim and a BMP/non-BMP boundary property test; F2 closes via a DOCUMENTED DECIDABLE SUPERSET grammar of json.dumps float spellings (fixed-notation exponent window, coefficient rules, two-digit exponent padding) — the D-104 cl.2 subset direction is amended per D-105 to 'accepted within the documented superset AND containing every real writer prefix'; both counterexamples refuse; randomized-float completeness property passes; Both registered blockers close together with an independent delta audit at the exact head; the acceptance-set contract re-proven in both amended directions over a corpus including non-BMP keys. Authority: [D-105 disposition synthesis (F1/F2 registered as a NEW ruling, not D-088 precedent; closure criteria refuter-amended; number-grammar exactness struck)](docs/decision_log.md). Acceptance: [C3-RECOGNIZER-EXACT-01 acceptance](docs/process/state_kernel.json). Fence: F1/F2 severity may not be downgraded by any role; closure ONLY through this row; while open the recognizer's accepted set may only SHRINK; the custody sidecar and writer-side ASCII key assertion (the D-105 micro-commit) are load-bearing compensating controls and may not be weakened (D-105 registration fences). Fence: This registration must not be cited as precedent for registering corpus-absent defects generally; it is a new ruling made with three recorded independent absence scans and mechanical compensating controls (D-105: branch-introduced registration is NOT QA-10A/B precedent). |
| A16 | P3-000 | P3 Research Expansion | BLOCKED — R-003 (user approves the 3.0.2 installs (R-003)) [AGENT] | KV persistence feasibility spikes (Phase 3 Stage 3.0): 3.0.2+ open; 3.0.2 needs installs and inherits the 3.0.1 harness shape plus its two deferred hardening fixes (ledger C-8). | Verdicts recorded in docs/phase_3/kv_feasibility.md; checklist rows are the status authority; must complete before any borrow-window scheduling. Evidence: Verdicts in docs/phase_3/kv_feasibility.md; Checklist rows updated. Authority: [D-035/D-036](docs/decision_log.md). Acceptance: [Phase 3 exit checklist](docs/phase_3/phase_3_exit_checklist.md). Note: 3.0.1 complete and merged (PR #9, replay_supported). |
| A17 | P2-022 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)) [AGENT] | Marker-shim energy-layer feasibility spike: verdict-shaped export path only (external_markers_supported / partial / external_markers_unsupported). | 3+ marked items, external result artifact hashed, strict bundle valid; verdict recorded. Evidence: 3+ marked items; External result artifact hashed; Strict bundle valid. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [Adapter contract](docs/contracts/adapter_contracts.md). Fence: Energy-layer-only pin: no accuracy interpretation, no leaderboard join, no pass@k-energy ratio, no general adapter framework; AP row required before any L2 claim (D-041). Note: C-027: the C-026 revisit-after-Window-A note is a revisit of sequencing, not permission. |
| A18 | P2-023 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists (post-2M per D-041)), P2-022 (P2-022 verdict recorded) [AGENT] | HumanEval import smoke: benchmark_import manifest plus suite profile plumbing goal; freeze subset with C-005 discipline, MIT license/provenance fields, 256/512-token completion policy. | Frozen subset with license/provenance fields lands; no pass@k/accuracy/capability claim. Evidence: Frozen subset manifest with C-005 discipline; License/provenance fields present. Authority: [D-041 (post-2M gate)](docs/decision_log.md). Acceptance: [RQ bank import-smoke design](docs/research_question_bank.md). Fence: No pass@k, accuracy, or capability claim (D-041). |
| A19 | P2-024 | P2 Next Slice | BLOCKED — P2-006 (2M reductions identify floor/MDE headroom) [AGENT] | Cheap-campaign shortlist: select among C5-1.6 sampler ABBA, C5-1.12 quant decomposition, C5-1.8 runtime attribution per measured floors; the selected campaign is then queued [QUIET-MAC]. | Explicit selection recorded after floors; selection cites floor/MDE headroom. Evidence: Selection recorded with floor/MDE headroom rationale; Selected campaign queued as a quiet_mac task. Authority: [C-015 + RQ bank](docs/research_question_bank.md). Acceptance: [P2-024 acceptance](docs/process/state_kernel.json). |
| A21 | P3-001b | P3 Research Expansion | BLOCKED — P2-006 (2M affine coefficients exist) [AGENT] | Seed the split analysis-plan row: pre-registered compositional predictions per pairing/link (including named same-boundary headline and at least one predicted-crossover cell if feasible), per-cell transfer-boundary labels (D-049). | AP row committed before any split hardware run; phase_3_plan amendment line landed. Evidence: AP row committed pre-split-hardware; phase_3_plan amendment line landed. Authority: [D-048/D-049](docs/decision_log.md). Acceptance: [Analysis plans (split row)](docs/contracts/analysis_plans.md). |
| A22 | P2-004 | P2 Next Slice | PARTIAL; READY; GATES close: P1-001 [AGENT] | Close model selection (D-016): decision-log entry with models, revisions, artifact paths, local mirror, fallback candidate; mid-model pick, CUDA load, GGUF paths outstanding. | Decision-log entry complete; full closure gated on P1-001. Evidence: Decision-log entry: models, revisions, artifact paths, mirror, fallback. Authority: [D-016](docs/decision_log.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). Note: Provisional small-model pick 2026-07-06 opens 2G. |
| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 [AGENT] | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) [AGENT] | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
| A25 | P2-047A | P2 Next Slice | READY [AGENT] | Freeze the controller capture-overhead ABBA harness comparing the standard event path with a buffered or minimal-marker path under identical outputs and hashes. | A frozen controller-overhead ABBA harness preserves output identity and defaults to instrumented-stack scope rather than unvalidated subtraction. Evidence: Frozen ABBA manifest; Standard and buffered/minimal-marker paths have identical output policy and hashes; Analysis refuses unsupported subtraction. Authority: [Hardening adjudication C7](docs/reviews/2026-07-10-hardening-adjudication.md). Acceptance: [P2-047A acceptance](docs/process/state_kernel.json). Fence: Do not subtract controller overhead without a separately justified correction model (Hardening adjudication C7). |
| A29 | DOC-008-REFLECTION | P4 Polish | READY [AGENT] | Replace planning_reflection_protocol.md with the DOC-008 redirect stub and reconcile its inbound references under condition 6. | Retire the reflection protocol as an independent intake surface while preserving its compatibility path. Evidence: planning_reflection_protocol.md is the exact redirect stub; Useful fields remain owned by the kernel or run reports; Inbound references use the consolidated intake route. Authority: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 reflection-protocol retirement](docs/specs/c027/doc-008_state_kernel.md). Fence: Keep the compatibility path and do not create another intake checklist (DOC-008 reflection-protocol fence). |
| A30 | DOC-008-STATUS | P4 Polish | READY [AGENT] | Perform the lead-authored PROJECT_STATUS compaction and verbatim history archival required by DOC-008 condition 8. | Lead compacts PROJECT_STATUS and preserves removed dated updates in the specified history archive. Evidence: Lead-authored PROJECT_STATUS has at most seven current sections; Removed dated updates are preserved verbatim in the history archive; Advisor-visible quantitative claims retain evidence pointers. Authority: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 PROJECT_STATUS compaction](docs/specs/c027/doc-008_state_kernel.md). Fence: Lead authors final advisor-facing claims and no generator writes PROJECT_STATUS (DOC-008 PROJECT_STATUS authorship fence). |
| A31 | DOC-008-INTAKE | P4 Polish | READY [AGENT] | Reconcile agent_playbook, AGENT_PLAN, README, orchestration, and remaining intake text with the generated kernel route in DOC-008 conditions 4 and 9. | Reconcile the remaining intake and procedure surfaces without creating another live-state mirror. Evidence: M0 is the sole short intake owner; Inbound procedure references no longer conflict; Generated regions remain the only work-selection views. Authority: [DOC-008 intake and procedure reconciliation](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 intake reconciliation](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not add hand-maintained ranked next-work or phase-completion mirrors (DOC-008 intake reconciliation fence). |
| A32 | DOC-008 | P4 Polish | PARTIAL; READY; GATES close: DOC-008-INTAKE; GATES close: DOC-008-REFLECTION; GATES close: DOC-008-STATUS [AGENT] | Close the reopened DOC-008 migration only after residual conditions 4, 6, 8, and 9 land and every original completion condition is rechecked. | Every original DOC-008 completion condition lands before the reopened task returns to complete. Evidence: All nine DOC-008 required outcomes rechecked; Focused and canonical suites pass; Final-head review confirms one work-selection authority. Authority: [DOC-008 state-kernel specification](docs/specs/c027/doc-008_state_kernel.md). Acceptance: [DOC-008 required outcomes](docs/specs/c027/doc-008_state_kernel.md). Fence: Do not redeclare DOC-008 complete until every original required outcome lands (DOC-008 required outcomes). Note: Reopened by WO-021; phase C repairs work-selection authority while three residual task records remain live. |
| A33 | P2-050 | P3 Hardening Candidates | READY [AGENT] | Adjudicate the C-028 dissent-record candidates separately: frozen-legacy claim_eligibility mapper, semantic cooldown-row verification, once-per-manifest first-run exemption, scoped top-up detection, and cooldown trace v2. | Each C-028 dissent-record candidate receives its own adjudication before any implementation. Evidence: Frozen-legacy claim_eligibility mapper receives its own adjudication; Semantic cooldown-row verification receives its own adjudication; Once-per-manifest first-run exemption receives its own adjudication; Scoped top-up detection and cooldown trace v2 receive their own adjudications. Authority: [C-028 dissent-record queue candidates](docs/run_reports/2026-07-11-c028-continuation.md). Acceptance: [P2-050 acceptance](docs/process/state_kernel.json). Fence: Do not implement any candidate before its own recorded adjudication (C-028 dissent-record queue candidates). |
| A34 | TOOL-01 | P3 Tooling | READY [AGENT] | Fix codex-run-v3 defects: resume-after-NEEDS_SCOPE no-op; preventive permission profiles; NEEDS_RULING recognition; effort-default passthrough; stream-death OK exits with thin out-files; resume --last cross-thread attachment through the global latest session; and session-open paths lacking per-path match specifiers. | All seven codex-run-v3 defects close in lead personal tooling with targeted regressions and updated adapter operations lessons. Evidence: Resume after NEEDS_SCOPE continues the requested work; Preventive permission profiles and NEEDS_RULING recognition are covered; Omitted effort defaults to xhigh instead of config passthrough; Upstream stream death fails instead of exiting OK with a thin out-file; Resume requires an explicit session ID and cannot cross-attach through a global --last pointer; Session-open accepts a per-path match specifier without post-hoc child expansion. Authority: [Bridge v1.1 wrapper and session operations record](docs/run_reports/2026-07-13-bridge-v11.md). Acceptance: [TOOL-01 acceptance](docs/process/state_kernel.json). Fence: Keep implementation in lead personal tooling; this repository owns only the work record (Bridge v1.1 wrapper and session operations record). Note: lead personal tooling, non-repo |
| A35 | AUD-FOLLOWUPS | P3 Hardening Candidates | READY [AGENT] | Close the ULTRA comparison audit's accepted small residue in one bounded agent task: WO-012's owned D-062 lint queue row, WO-014 realized-token discrimination, WO-017 default no-handoff regression, WO-020 standalone bridge-checker decision, and WO-040 authored-instruction absolute-path plus genuine pristine-clone coverage. | The ULTRA comparison audit's five accepted small follow-ups close with discriminating tests or an explicit recorded decision, without creating a ceremony-dispositions task. Evidence: WO-012's owned D-062 lint queue-row obligation is implemented and covered; WO-014 has a realized-token discriminating test; WO-017 has a default no-handoff regression assertion; WO-020 has a recorded standalone bridge-checker decision; WO-040 has authored-instruction absolute-path coverage plus a genuine pristine-clone test. Authority: [Comprehensive-audit close-out and accepted-residue list](docs/reviews/2026-07-13-comprehensive-audit/report.md). Acceptance: [AUD-FOLLOWUPS acceptance](docs/process/state_kernel.json). Fence: Do not create AUD-CEREMONY-DISPOSITIONS; ceremony dispositions remain report-owned (Comprehensive-audit report disposition ledger). Note: Accepted small residue only; audit ceremony dispositions remain in the report. |
| A36 | AUD-WO-033 | P3 Hardening Candidates | READY; GATES close: P2-006 [AGENT] | After 2M, split scripts/run_campaign.py along tested policy seams, pure validation and provenance first and execution lifecycle second, only when campaign-scale or split or multi-node work first forces edits to that path. | The post-2M campaign-runner refactor is behavior-preserving across the full campaign test portfolio and retains every collection and claim-readiness safeguard. Evidence: Pure validation and provenance seams are extracted before execution lifecycle seams; The full campaign behavior-parity portfolio is green before and after the split; Locks, waivers, backups, cooldown, and claim-readiness behavior remain unchanged. Authority: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-033](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Keep this post-2M and behavior-preserving; do not redesign campaigns or weaken locks, waivers, backups, cooldown, or claim-readiness gates (Comprehensive-audit register WO-033 non-goals and risk note). |
| A37 | AUD-WO-034 | P3 Hardening Candidates | READY; GATES close: PHASE-3-SPLIT-SCHEDULED [AGENT] | At Phase-3 split scheduling, assign bounded owners and dependencies for transfer-bench, split replay, composite validate and reduce, KV-economics reduction, and matrix-generator extension before any PLANNED command becomes executable. | When Phase-3 split work is scheduled, every PLANNED pack command gains an owner or explicit deferred marker without pack collapse or premature implementation. Evidence: Every PLANNED command has a bounded owner row or explicit deferred-design marker; Pack-command ownership lint passes positive and negative fixtures; Settled split pre-registration requirements and offline-before-live fences remain intact. Authority: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-034](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not prune draft designs, collapse campaign packs, or implement split or KV work in this ownership pass (Comprehensive-audit register WO-034 non-goals). |
| A38 | AUD-WO-035 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-TRANSFER-SCHEDULED [AGENT] | Before the first 2K-live or remote split-transfer task, define a versioned discriminated node-worker payload and test realistic typed rejection without overloading telemetry blocks. | The 2K-live and remote roadmap has a versioned transfer-task payload seam with typed rejection before split-transfer implementation. Evidence: A versioned discriminated payload path exists for transfer tasks; A realistic unsupported transfer request fails with a typed versioned error; Telemetry blocks are not overloaded with transfer semantics. Authority: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-035](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Define and reject the future transfer shape only; do not implement split execution or transfer benchmarking (Comprehensive-audit register WO-035 non-goals). Note: D-043 supersession closure falls due at landing: add the dated protocol-version supersession line identified by PA-2. |
| A39 | AUD-WO-036 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-CONCURRENCY-SCHEDULED [AGENT] | When 2K-live or remote retries or concurrency are introduced, add a pre-launch node and GPU ownership lease plus idempotent duplicate prepare and start behavior. | Retries or concurrent 2K-live and remote campaigns cannot double-own a node or GPU and duplicate delivery is idempotent. Evidence: Duplicate prepare and start delivery is idempotent; Node and GPU ownership is leased before launch; Concurrency coverage exercises the ownership and duplicate-delivery contract. Authority: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-036](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Do not run concurrent hardware campaigns or make live-correctness claims in this agent task (Comprehensive-audit register WO-036 non-goals). |
| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED [AGENT] | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED [AGENT] | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED [AGENT] | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
| A43 | CUSTODY-HARDEN-01 | P2 Next Slice | READY [AGENT] | Custody hardening follow-on from the screen+budget gauntlet: reduce-layer label-trust removal (G2A), drift-bound seal authentication (A3-r2), dead no-freshness accommodation disposition, artifact_schema_invalid mislabel. | Close the PR #85 gauntlet's deferred custody-hardening seams: config-derived mockness reaches the reduce-layer barriers, the drift-bound seal stops being self-certifying, and two diagnostic nits are resolved. Evidence: Reduce-layer environment/CPU claim barriers derive mockness from the custody-bound config, with metadata/summary-label early returns removed; Drift-bound artifact corpus identities resolve against repo-registered or custody-bound bytes (seal no longer self-certifying); Dead pre-addendum no-freshness accommodation removed or pinned as intentional forward-compatibility; artifact_schema_invalid evidence-binding mislabel renamed or documented at emission site. Authority: [C-045 gauntlet deferrals (council log; detail in docs/run_reports/2026-07-24-screen-budget-gauntlet.md)](docs/council_log.md). Acceptance: [CUSTODY-HARDEN-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from PR #85 gauntlet deferrals; triangle-agreement enforcement (merged) already raises these seams to three-file forgery cost. |
| A46 | FLOOR-WORKLOAD-SIZING-01 | P1 Phase Gate | READY [AGENT] | Re-size the floor/science campaign workloads so measured effects clear the duration-independent attribution floor, and pilot the resulting effect-to-floor ratio before spending quiet-machine nights on ABBA collection at current sizes. | Anchor-attribution error is approximately duration-independent (~1 J regardless of phase size) while effects scale with workload, so lengthening prefill/decode raises effect-to-floor linearly at zero instrument cost. Evidence: Measured effect-to-floor ratio at candidate workload sizes, from a pilot rather than assumption; Re-sized configs for the remaining floor stages, with the sizing rationale recorded; Explicit decision on which queued stages are collected at which sizes. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-WORKLOAD-SIZING-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25; scope corrected same day after the quantitative replay. NOT a blocker on the ABBA roadmap: under the labelled-floor path the queued stages remain scientifically viable at current sizes (tens-of-percent effects on ~50 J clear a ~3 J floor plus claim-side bound). This is a MARGIN optimisation — attribution error is duration-independent while effects scale with workload, so longer prefill/decode buys effect-to-floor ratio for free. Pilot the ratio at candidate sizes before committing the remaining quiet-machine nights. |
| A47 | FLOOR-COMMONMODE-01 | P2 Next Slice | READY [AGENT] | Pre-register and evaluate a common-mode anchor estimator for ABBA blocks: sweep one shared fiducial shift across all four members, re-integrate measured curves, and add only genuinely per-bundle components adversarially. | The fiducial term is ~80% of the composed anchor bound (24.9 of ~31.1 ms, verified) and is literally the same artifact for all four members of a block; treating it as four independent adversarial draws is itself an unphysical modelling choice. Evidence: Block-timescale fiducial stationarity registered as a NAMED transfer assumption with its evidence; Estimator pre-registered before it touches claim-bearing data; The identical estimator applied to BOTH the calibration blocks and the consuming science contrast (a floor calibrated with cancellation the consumer does not get would understate false effects); Quantified gain on a5/a10 blocks versus the worst-case-sum default. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [FLOOR-COMMONMODE-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25. Quantified same day on a5 decode ABBA (10 complete blocks): implemented worst-case-sum half-width gives a 6.46 J comparative floor; a common-mode proxy gives 2.13 J, a 3x improvement — material, but still above that cell's 0.60 J point floor, so it does not by itself restore extraction under the current gate. Value is in tightening the labelled floor, not in avoiding the label. Fiducial share of the composed bound measured at 80-87%. |
| A48 | PHASE-SHARE-ESTIMAND-01 | P2 Next Slice | READY [AGENT] | Investigate the anti-correlated prefill/decode boundary error: energy a shift removes from one phase it adds to the other, so the phase-share estimand has ONE boundary nuisance parameter whose joint envelope is a curve, not a box. | Treating each phase's anchor envelope as an independent box double-spends the shared interior boundary and inflates uncertainty on exactly the split/share quantity the Splitwise replication needs. Evidence: Determined whether _corner_composed_anchor_shift_envelope treats the shared interior boundary independently; Joint envelope over the single boundary-position parameter derived by re-integration sweep (measured-curve arithmetic only); Quantified effect on the phase-asymmetry claim envelope versus the independent-box treatment. Authority: [2026-07-25 attribution-limit adjudication (Fable ruling + Sol replay; plan in session scratchpad)](docs/decision_log.md). Acceptance: [PHASE-SHARE-ESTIMAND-01 acceptance](docs/process/state_kernel.json). Note: Minted 2026-07-25 from the attribution-limit adjudication. Potentially the largest single win available for Splitwise sizing, at no instrument cost. |
| A49 | MODULARITY-01 | P3 Hardening Candidates | READY [AGENT] | Close the campaign-authoring modularity gap surveyed 2026-07-29: parameterize the campaign generator over a campaign-spec artifact and replace code-side literal assertions (analysis-manifest condition pairs, calibration scopes, phase-metric list) with registry-declared hash-validated sets. | Close the campaign-authoring modularity gap: campaign-spec-driven generation and registry-declared closed sets make every experiment axis swappable by config, per Ed's modularity directive. Evidence: Campaign generator is a parameterized function over a campaign-spec artifact (model, N, size profiles, block pattern, suite ref, run-ID prefix); a model swap touches one spec file and MODEL_TAG/PLAN_ID/run-ID prefixes derive from it with no parallel literal edits; Analysis-side closed sets (condition pairs, calibration scopes, phase-metric list) are declared in hash-bound registry artifacts and validated against those declarations, replacing the code-side literals at analysis_manifest.py:29-30,542-549 and detection_floor.py:87,89-95; Recorded-but-deferred residue dispositioned or re-queued: powermetrics references outside the adapter boundary, external-dataset ingestion, chat-template/thinking-mode seam, ABBA arity welded into three sites. Authority: [2026-07-29 modularity survey (Ed directive + per-axis grades)](docs/run_reports/2026-07-29-modularity-survey.md). Acceptance: [MODULARITY-01 acceptance](docs/process/state_kernel.json). Fence: Modularity applies to the harness, never to frozen claim pins: ratified hard literals (six-decimal pre-registration floor pins, lead-verified digests) stay anti-modular on purpose and must not be parameterized. (D-078 provenance amendment + D-079 operative-floor pins (hard literals are lead-verified, never parameterized)). Note: Minted 2026-07-29 from Ed's modularity directive. Survey verdict: runtime/telemetry Protocol layer and content-addressed provenance spine are already modular; the gap is campaign authoring above the adapter and literal assertions below the reader. Practical payoff lands with the planned Qwen3 cross-generation follow-up. |
| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY [AGENT] | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
# The Orchestration Process

How this project is actually built: a human researcher directing a
multi-model AI system whose workflow is itself a deliberate, versioned,
self-instrumenting piece of engineering. This document is the single
in-repo description of that process. (The executable playbooks live
outside the repository as reusable "skills" so they transfer to future
projects; this page describes what they do and where their evidence
lands in this repo.) Binding role and process changes live in
`docs/decision_log.md`; this page avoids copying volatile model versions.

## Roles: a lead, independent implementers/reviewers, and a human at the top

- **Ed (researcher)** sets research direction, methodology
  non-negotiables (raw-evidence bundles, dual-basis capture with gross-energy
  headlines, named
  measurement boundaries, no unauditable claims), hardware/access
  decisions, and — critically — *process policy*: every rule below
  traces to a standing instruction issued after an observed failure or
  opportunity. External-facing claims and merge authority derive from
  him (he granted the lead conditional self-merge authority on
  2026-07-08 once the review gate had proven itself).
- **The designated lead** owns
  decomposition, triage, design adjudication, every final diff gate,
  all live/hardware verification, merge decisions, bookkeeping, and
  process evolution. Other agents save lead capacity without inheriting
  final authority; all escalation paths terminate at the lead.
- **Independent implementation and review agents** do the heavy reading and
  writing: implementation against pinned specs, adversarial review
  lenses, test writing, test *auditing* (never of its own tests — a
  fresh instance audits), docs drafting, and review of the lead's own
  consequential decisions. Cross-model review is load-bearing by
  design: the attributed per-layer catch record (below) shows the two
  roles consistently catching different classes of defect.
- **Specialist agents** handle bounded sweeps (for example, docs
  consistency) and, when a stream genuinely needs
  mid-stream judgment, as a stream director — a role that is now the
  exception rather than the default (see Topology).
- **Image-heavy analysis uses the designated image-capable review route** per
  C-012, after the site-observatory stream's image-critique rounds.
- **Invited-peer validation is allowed to overturn lead designs**; C-014
  recorded two lead designs overturned by an invited peer before
  implementation.

## The loop, end to end

Every substantial session runs one conductor procedure:

1. **Intake** — read `RUN_STATE.md` (the intake pointer), the task
   queue, the latest run report; never re-decide anything the decision
   log settled.
2. **Decompose** — split work into genuinely independent streams
   (disjoint expected diff footprints), one git worktree + branch each;
   assign each stream a review tier by *cost of being wrong*
   (measurement-semantics and contract-bearing work gets the full
   pipeline; docs get a light tier). Preflight gates: hardware-shaped
   streams require a confirmed device inventory; anything pinned
   without live validation carries a PROVISIONAL label; measurement
   sessions require a no-agent "quiet machine" lock.
3. **Per-stream pipeline** — for each reviewable unit: an invited
   design-argument round (the implementer must argue trade-offs before
   coding), implementation, then a layered review stack:
   2–3 fresh-instance counterreview lenses over the diff → lead triage
   with recorded dispositions → fixes → a dedicated test-amplification
   round (an independent writer adds edge-case tests) → a
   writer≠reviewer test audit (a fresh instance hunts tautological,
   vacuous, or wrong-expectation tests) → the lead's diff gate.
4. **Lead live gates** — never delegated: the lead runs the real flow
   (real corpus, real CLI, real hardware where present). This layer has
   repeatedly caught blockers no other layer saw, including defects
   whose own tests were green because the tests encoded the same wrong
   assumption as the code.
5. **Merge gate** — multi-commit series land as branch + PR. Before any
   merge: a pre-merge oversight pass by 2–3 fresh reviewers with
   distinct angles (deep regression hunt; claim-to-evidence trace;
   merge-order simulation across sibling PRs), lead triage, fixes, CI
   green. **Final-head rule:** any commit that lands after the last
   review round gets one more fresh review before merge — no commit
   merges unreviewed, however small (its first application caught a
   crash path in a "trivial" post-review fix).
6. **Integration review** — after parallel streams merge, one dedicated
   review hunts *interaction* defects no single-stream review can see.
   Its catches are definitionally unique (first outing: two).
7. **Bookkeeping** — a single session record (run report) with a
   verbatim process-trace appendix; the intake pointer and queue
   refreshed; a delegated docs-consistency sweep before the final
   commit (its latest pass found 15 real drift items; earlier passes
   found 5–6). Large documentation batches add the pre-commit
   docs-verify mode; the `consistency-sweep` skill owns that shape,
   including the D-043 supersession check.
8. **Same-session distillation** — lessons fold into the process
   playbooks the same session they are learned. Measured effect: one
   failure mode recurred five times before its fix was distilled, zero
   times after. The current operation-loop also runs its §0
   primary-deliverable check and §8 shipped-check before the session is
   considered done.
9. **Post-landing verification and close-out** — landed work gets the
   matching verification workflow with severity-tiered refuters. Sessions
   that change front-facing state refresh `docs/site/DRIFT.md`; no agent
   regenerates or deploys the site. Automation informs and Ed deploys
   manually, per D-068 and `RUN_STATE.md` end-of-work step 8.
10. **Meta-review (the final step)** — event-driven, not calendar-driven:
    when a review layer stops earning its keep, when an intervention
    repeats despite a folded fix, or when the user asks, the loop is
    reviewed with its own evidence discipline (see Topology for the
    consensus one such review produced). After large workloads the
    post-large-workload meta-reassessment (owned by operation-loop §10)
    always fires, and it runs LAST.

### Stop cards and paused work

When a session stops with live work in progress, the lead creates or
updates an `ACTIVE_STOP_CARD` at the top of `RUN_STATE.md`. While active,
that card is the single restart authority and overrides every lower
"what next" list, queue rank, mission guide, and run-report default.

A stop card must name:

- the resume authority and exact artifact pointer,
- the reason for stopping,
- worktrees, branches, PRs, and off-repo artifacts that must not be
  cleaned accidentally,
- status terms for each paused item,
- the first resume action, and
- the clearance criteria.

Use these status terms for paused work:

| Term | Meaning |
|---|---|
| `APPLIED_UNVERIFIED` | A worker reports code or docs are applied, but the lead has not gated the diff. Not merge-safe. |
| `LEAD_GATED` | The lead has reviewed and run the required local/live checks for the item. |
| `PR_OPEN_CI_GREEN` | A PR exists and CI is green, but merge authority has not yet fired. |
| `MERGED` | The accepted work has landed on main. |
| `UNREAD_UNADJUDICATED` | A report/synthesis exists but has not been consumed into decisions, queue rows, or rejected findings. |
| `ADJUDICATED` | Findings have explicit accept/reject/defer disposition and downstream artifacts are updated. |

Before an intentional pause, do the minimal stop sync even if full
bookkeeping cannot fit: update only `RUN_STATE.md`'s stop card and the
rank-0 queue row. That is enough to prevent accidental bypass.

## The artifact system (where rigor becomes auditable)

Each fact has exactly one home; everything else points at it:

| Artifact | Role |
|---|---|
| `docs/decision_log.md` | Binding design decisions, each with alternatives considered, consequences, and revisit conditions. The log is the count authority; nothing re-decides these silently. |
| `docs/council_log.md` | The deliberation record: review-council positions, reasoning exchanged, who prevailed, overridden dissents — so a future reader can reconstruct *why*, not just *what*. The log is the range/count authority. |
| `docs/contracts/` | Claim/evidence contracts: `claims_ladder.md` (D-037) plus `analysis_plans.md` (D-038) form the claim gate; strict validation is the evidence ticket. |
| `docs/stream_logs/` | Per-stream decision ledgers, committed WITH the code they justify: every non-trivial in-stream decision (`A-1..A-30`, `B-1..B-46`, …) with mandatory evidence pointers; wrong pins are SUPERSEDED in place, never erased. |
| `docs/run_reports/` | One record per working session: outcomes, verification evidence, a per-layer catch/yield table, the delegation-calibration ledger, restart instructions. |
| `docs/process/state_kernel.json` | Source of truth for work selection: active gates, dependencies, and machine-state lanes ([QUIET-MAC] / [AGENT] / [ED-EXTERNAL]). |
| `TASK_QUEUE.md` | Generated detailed queue projection plus dated history; do not hand-copy its live rows into reader docs. |
| `RUN_STATE.md` | Intake pointer with the generated restart projection. History lives in run reports. |
| `docs/risk_register.md` | Live risks with triggers and mitigation states. |

Instrumentation ledgers close the loop on the process itself:

- **Per-layer yield:** every review layer's unique catches are
  attributed and tallied per session under D-061 (C-027; replaces the
  earlier two-zero-sessions auto-drop, which the integration-review
  zero/zero/five sequence falsified): applicability is decided by
  PRE-DECLARED mechanical predicates; outcomes are classified
  accepted-unique-defect / duplicate / clean-verification /
  false-positive-suppression (suppression is not a catch); severity
  weights are fixed before the session; three applicable exposures
  TRIGGER an expected-loss review decision, never automatic deletion;
  safety/final-head/integration layers are never auto-dropped on
  zero-defect streaks. (One layer, the default specialist review lens, was
  dropped under the old rule before D-061.)
- **Delegation calibration:** every delegated unit gets a row — task
  altitude (pinned-spec / design-freedom / judgment-call), outcome
  (assigned by the lead after the gate, never self-labeled), catches,
  and lead rework minutes, with prompt-defects separated from
  model-defects. Delegation boundaries move on this evidence, not
  vibes. Current signal: pinned-spec delegation runs essentially
  defect-free; the serious defects cluster in volunteered additions and
  design-freedom wire contracts — which is exactly where the full lens
- **Invocation manifest:** substantial delegated/tool/skill runs get a
  lightweight manifest row per invocation. Minimum fields:
  `run_id`, `parent_report`, `role_or_lens`, `model`, `wrapper`,
  `session_id`, `prompt_sha256`, `prompt_path`, `output_path`, `status`,
  `consumed_by`, `disposition`, and `commit_or_pr`. Raw logs can stay
  out of git; every ephemeral artifact still needs a committed pointer
  row with `path`, `sha256` or stable id, `promoted_to`, and
  `not_promoted_reason`.

## Council discipline

Councils are expensive instruments. Use a full council for methodology,
measurement validity, schema/contract changes, claim boundaries, hardware
protocols, or explicit user requests. For ordinary implementation, use a
small number of targeted lenses plus lead adjudication.

Every high-impact council must leave a durable scorecard:

- unique catches by severity,
- accepted/rejected/deferred/false-positive counts,
- lead triage and rework time when practical,
- shipped artifacts,
- queue rows created or re-ranked,
- decision-log IDs promoted, and
- a disposition table: finding → ruling → owner → artifact/queue/decision
  target → closure check.

Deferred decision-log promotion is itself a tracked obligation, not
ambient prose in a report.

## Spend guardrails (WO-022; R2 ruled, Ed-ratified 2026-07-13)
  walking away from.

## 9. Three strengthening moves

1. **Make K the manipulated variable and drop the break-even curve as the
   headline.** Pre-register a K ∈ {1, 2, 3, 4} sweep at a single draft size
   against a fixed prompt, with acceptance as a *measured mediator*, not the
   x-axis. K is settable, pre-registrable, and generates a monotone design with
   a real dose-response; the current design has no manipulated variable at all.
   Retitle to "Does speculative decoding ever repay its energy at batch 1?" —
   a question this instrument can actually answer, with a directional
   floor-gated answer either way. Keep acceptance-vs-Δenergy as a secondary
   descriptive figure with an honest prompt-level n.
2. **Move the go/no-go evidence to the front and make it cheap.** Before any
   runtime fork, run a *non-claim, daytime, wall-clock-only* spec-on/off timing
   pilot on the 7B/0.5B pair with the stock pinned runtime (generation already
   works — no instrumentation needed for tok/s). If spec-on is slower than
   baseline, as the DSpark/DFlash smoke predicts, the energy answer is settled
   at essentially zero cost and the whole fork/floor/AP build is never funded.
   This is a two-hour desk task that currently sits *after* two to three weeks
   of instrumentation work.
3. **Fix the floor story explicitly, or change the primary metric.** Either
   (a) name the `gross_request` floor-class build as a first-class work item,
   fold it into D-117's U3 pinset-v2 scope so one mint effort serves both, and
   restore the 10+40 member design; or (b) if that is too much, re-scope the
   primary metric to `phase_energy_j.decode` with an explicit, pre-registered
   statement of how the draft's prompt pass is attributed — and accept the
   phase-comparability caveat in the text rather than avoiding it by metric
   choice. Additionally: run the spec-off arm on the *same forked runtime*, and
   pre-register a measured bound on in-window instrumentation energy (an
   instrumented-vs-uninstrumented spec-off pair) before either arm is claimed.

**Bonus route worth a paragraph in any revision:** `mlx-dspark`/`mlx-dflash` are
already vendored and smoked locally, and the smoke README notes they surface
**per-round acceptance and target-forward counts — precisely the observability
surface pinned mlx-lm lacks**. That path needs no fork of the calibrated runtime.
It costs a different target model (Qwen3-4B), a D-016 touch, a non-mirrored
auto-fetched drafter, and a thinking-policy pin (D-074) — but the proposal does
not even mention it, and it may be the cheaper road to the same paper.
*Credited, in fairness:* the kill-criteria section is the best-shaped in the portfolio; the "~5 J is only
a Mac phase-design reference" paragraph is exactly the right instinct; the honest statement that live
split is stretch and that portability failure caps the work at synthetic metrology is correct discipline.
The proposal is not naive — it is under-costed and one step short of following its own best insight.

## Three strengthening moves (if kept)

1. **Invert the paper: make the refusal the result, and drop the meter.** Kill the split-vs-monolithic
   winner claim and contribution 4. Ship a *boundary-composability* paper: pre-register the composite
   budget arithmetic before any collection; add the one cheap missing empirical input — a **GPU-side
   cadence/averaging characterization** (pulse-train step-load on the 3080 Ti, no LLM, no Mac, closes
   hardening Phase-7 item 4 and costs one non-quiet evening on owned hardware); then publish "the
   two-boundary composite budget is ~N J against candidate effects of 10-200 J, therefore the split
   comparison is REFUSED, and here is the exact operating domain where it would resolve (payload >= X GiB,
   link <= Y Gb/s, board TDP <= Z W)." Falsifiable, entirely owned-hardware, and it makes the fail-closed
   machinery do the most interesting work in the paper. This is the version that fits ICPE WIP.
2. **Build a shared physical fiducial or declare its impossibility as the finding.** Replace the NTP-shaped
   clock criterion with a cross-device *power-step* fiducial: a pre-registered train of fixed-size
   transfers whose starts/stops appear as power steps on both endpoints, with the cross-clock bound derived
   from observed step alignment rather than from a software clock. This is the only construction that
   preserves continuity with D-078's actual mechanism. If it cannot produce a bound under 25% of the
   shortest claimed interval, that failure is the headline — and a better one than a crossover plot.
3. **Fix the runtime accounting and the two contradictions, then re-cost in the open.** State plainly that
   the split stack is llama.cpp/GGUF and therefore a *new instrument* needing its own calibration regime
   and floor mints, with the honest 8-12-window budget attached — or drop the real-split arm to future work
   under D-092/C8's existing conditional framing. Separately: delete the sender/receiver wall floors from
   contribution 2 (one meter cannot mint them), and add battery-charge neutralization with verified steady
   state as a hard admission gate before any wall-boundary claim, per the MLPerf rule the draft already
   cites.

**Disposition recommendation:** do not fund as a second paper. Fund move 1 as a ~1-evening desk+bench
probe; if the GPU cadence characterization comes back at 100 ms or better *and* a cross-device power-step
bound lands under the 25% criterion, revisit. Otherwise this direction's correct home is a quantified
future-work section in the MVP paper — which is exactly where D-092 already put it.
docs/JouleWise_Hardening_Proposal.md

codex
The repository has no active stop card, and the requested work is planning-only. Probe B is explicitly not runnable from this agent session: the 3080 Ti access remains an `[ED-EXTERNAL]` gate, so I’ll describe the operator protocol and preserve its results as provisional until Ed runs it on the rig.
exec
/bin/zsh -lc "sed -n '430,470p' docs/JouleWise_Hardening_Proposal.md; sed -n '1,190p' docs/specs/axi/sc_spec_decode_verdict.md; rg -n \"mlx-lm|mlx_lm|Qwen2\\.5.*0\\.5|draft-model|num-draft|generation\" pyproject.toml requirements*.txt docs scripts joulewise tests | head -n 300; ls -la .venv/bin/mlx* 2>/dev/null || true; .venv/bin/python -m pip show mlx-lm 2>/dev/null || true; command -v mlx_lm.generate || true; command -v mlx_lm.generate.py || true; find /Users/edr/code /Users/edr/.cache -path '*/mlx_lm/generate.py' -o -path '*/bin/mlx_lm.generate' 2>/dev/null | head -n 40" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 1684ms:
/Users/edr/code/mlx-dspark-vendor/.venv-dspark/bin/mlx_lm.generate
/Users/edr/code/mlx-dspark-vendor/.venv-dspark/lib/python3.13/site-packages/mlx_lm/generate.py
/Users/edr/code/JouleWise/.venv/bin/mlx_lm.generate
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py

exec
/bin/zsh -lc "rg -n \"target|draft|Qwen|command|--draft-model|Live|live\" docs/specs/axi/sc_spec_decode_verdict.md | head -n 140; sed -n '190,380p' docs/specs/axi/sc_spec_decode_verdict.md; /Users/edr/code/JouleWise/.venv/bin/mlx_lm.generate --help; /Users/edr/code/JouleWise/.venv/bin/python -c 'import importlib.metadata as m, mlx_lm, mlx; print(m.version(\"mlx-lm\")); print(m.version(\"mlx\")); print(mlx_lm.__file__)'; sed -n '180,230p' /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py; sed -n '2000,2095p' /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 268ms:
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise/.venv/bin/mlx_lm.generate", line 3, in <module>
    from mlx_lm.generate import main
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/__init__.py", line 9, in <module>
    from .convert import convert
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/convert.py", line 8, in <module>
    import mlx.nn as nn
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/__init__.py", line 4, in <module>
    from mlx.nn.layers import *
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/__init__.py", line 3, in <module>
    from mlx.nn.layers.activations import (
    ...<52 lines>...
    )
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/activations.py", line 19, in <module>
    @partial(mx.compile, shapeless=True)
     ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
Exception ignored in atexit callback <nanobind.nb_func object at 0x107f58370>:
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import importlib.metadata as m, mlx_lm, mlx; print(m.version("mlx-lm")); print(m.version("mlx")); print(mlx_lm.__file__)
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/__init__.py", line 9, in <module>
    from .convert import convert
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/convert.py", line 8, in <module>
    import mlx.nn as nn
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/__init__.py", line 4, in <module>
    from mlx.nn.layers import *
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/__init__.py", line 3, in <module>
    from mlx.nn.layers.activations import (
    ...<52 lines>...
    )
  File "/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx/nn/layers/activations.py", line 19, in <module>
    @partial(mx.compile, shapeless=True)
     ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
Exception ignored in atexit callback <nanobind.nb_func object at 0x10840a8a0>:
RuntimeError: [metal::load_device] No Metal device available. This typically occurs in headless, sandboxed, or virtualized macOS sessions where the GPU is not accessible.
        "--prompt-cache-file",
        type=str,
        default=None,
        help="A file containing saved KV caches to avoid recomputing them",
    )
    parser.add_argument(
        "--quantize-activations",
        "-qa",
        action="store_true",
        help="Quantize activations using the same quantization config as the corresponding layer.",
    )
    parser.add_argument(
        "--kv-bits",
        type=int,
        help="Number of bits for KV cache quantization. Defaults to no quantization.",
        default=None,
    )
    parser.add_argument(
        "--kv-group-size",
        type=int,
        help="Group size for KV cache quantization.",
        default=64,
    )
    parser.add_argument(
        "--quantized-kv-start",
        help="When --kv-bits is set, start quantizing the KV cache "
        "from this step onwards.",
        type=int,
        default=DEFAULT_QUANTIZED_KV_START,
    )
    parser.add_argument(
        "--draft-model",
        type=str,
        help="A model to be used for speculative decoding.",
        default=None,
    )
    parser.add_argument(
        "--num-draft-tokens",
        type=int,
        help="Number of tokens to draft when using speculative decoding.",
        default=3,
    )
    return parser


# A stream on the default device just for generation
generation_stream = mx.new_thread_local_stream(mx.default_device())


@contextlib.contextmanager
def wired_limit(model: nn.Module, streams: Optional[List[mx.Stream]] = None):
        elif model_path != metadata["model"]:
            raise ValueError(
                f"Providing a different model ({model_path}) than that "
                f"used to create the prompt cache ({metadata['model']}) "
                "is an error."
            )
    model_path = model_path or DEFAULT_MODEL

    model, tokenizer = load(
        model_path,
        adapter_path=args.adapter_path,
        tokenizer_config=tokenizer_config,
        model_config={"quantize_activations": args.quantize_activations},
    )
    for eos_token in args.extra_eos_token:
        tokenizer.add_eos_token(eos_token)

    template_kwargs = {}
    if args.chat_template_config is not None:
        template_kwargs = json.loads(args.chat_template_config)

    prompt = args.prompt.replace("\\n", "\n").replace("\\t", "\t")
    prompt = sys.stdin.read() if prompt == "-" else prompt
    if not args.ignore_chat_template and tokenizer.has_chat_template:
        if args.system_prompt is not None:
            messages = [{"role": "system", "content": args.system_prompt}]
        else:
            messages = []
        messages.append({"role": "user", "content": prompt})

        has_prefill = args.prefill_response is not None
        if has_prefill:
            messages.append({"role": "assistant", "content": args.prefill_response})
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            continue_final_message=has_prefill,
            add_generation_prompt=not has_prefill,
            **template_kwargs,
        )

        # Treat the prompt as a suffix assuming that the prefix is in the
        # stored kv cache.
        if using_cache:
            messages[-1]["content"] = "<query>"
            test_prompt = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                continue_final_message=has_prefill,
                add_generation_prompt=not has_prefill,
            )
            prompt = prompt[test_prompt.index("<query>") :]
        prompt = tokenizer.encode(prompt, add_special_tokens=False)
    else:
        prompt = tokenizer.encode(prompt)

    if args.draft_model is not None:
        draft_model, draft_tokenizer = load(args.draft_model)
        if draft_tokenizer.vocab_size != tokenizer.vocab_size:
            raise ValueError("Draft model tokenizer does not match model tokenizer.")
    else:
        draft_model = None
    sampler = make_sampler(
        args.temp,
        args.top_p,
        args.min_p,
        args.min_tokens_to_keep,
        top_k=args.top_k,
        xtc_probability=args.xtc_probability,
        xtc_threshold=args.xtc_threshold,
        xtc_special_tokens=tokenizer.encode("\n") + list(tokenizer.eos_token_ids),
    )
    response = generate(
        model,
        tokenizer,
        prompt,
        max_tokens=args.max_tokens,
        verbose=args.verbose,
        sampler=sampler,
        max_kv_size=args.max_kv_size,
        prompt_cache=prompt_cache if using_cache else None,
        kv_bits=args.kv_bits,
        kv_group_size=args.kv_group_size,
        quantized_kv_start=args.quantized_kv_start,
        draft_model=draft_model,
        num_draft_tokens=args.num_draft_tokens,
    )
    if not args.verbose:
        print(response)


if __name__ == "__main__":
    print(
        "Calling `python -m mlx_lm.generate...` directly is deprecated."
        " Use `mlx_lm.generate...` or `python -m mlx_lm generate ...` instead."
    )

exec
/bin/zsh -lc "sed -n '1,185p' /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py; sed -n '1900,2015p' /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py; rg -n \"verbose|Prompt:|Generation:|tokens-per-sec|tokens per second|generation_tps|seed|temp|top-p|max-tokens|eos\" /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py | head -n 160; rg -n \"Qwen2.5-7B|7B-Instruct-4bit|0.5B-Instruct-4bit\" docs experiments scripts | head -n 120; find /Users/edr/jw_models/mlx-community -maxdepth 1 -type d -name 'Qwen2.5*' -print 2>/dev/null | sort; /Users/edr/code/JouleWise/.venv/bin/python -c 'import importlib.metadata as m; print(m.version(\"mlx-lm\")); print(m.version(\"mlx\")); print(m.distribution(\"mlx-lm\").locate_file(\"mlx_lm/generate.py\"))'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
# Copyright © 2023-2024 Apple Inc.

import argparse
import contextlib
import copy
import functools
import json
import sys
import time
from collections import deque
from dataclasses import dataclass
from functools import partial
from typing import (
    Any,
    Callable,
    Generator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_reduce
from transformers import PreTrainedTokenizer

from .models import cache
from .models.cache import (
    ArraysCache,
    BatchKVCache,
    BatchRotatingKVCache,
    CacheList,
    KVCache,
    QuantizedKVCache,
    RotatingKVCache,
    TokenBuffer,
    load_prompt_cache,
)
from .sample_utils import make_sampler
from .tokenizer_utils import TokenizerWrapper
from .utils import does_model_support_input_embeddings, load

DEFAULT_PROMPT = "hello"
DEFAULT_MAX_TOKENS = 100
DEFAULT_TEMP = 0.0
DEFAULT_TOP_P = 1.0
DEFAULT_MIN_P = 0.0
DEFAULT_TOP_K = 0
DEFAULT_XTC_PROBABILITY = 0.0
DEFAULT_XTC_THRESHOLD = 0.0
DEFAULT_MIN_TOKENS_TO_KEEP = 1
DEFAULT_SEED = None
DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
DEFAULT_QUANTIZED_KV_START = 5000


def str2bool(string):
    return string.lower() not in ["false", "f"]


def setup_arg_parser():
    """Set up and return the argument parser."""
    parser = argparse.ArgumentParser(description="LLM inference script")
    parser.add_argument(
        "--model",
        type=str,
        help=(
            "The path to the local model directory or Hugging Face repo. "
            f"If no model is specified, then {DEFAULT_MODEL} is used."
        ),
        default=None,
    )
    parser.add_argument(
        "--trust-remote-code",
        action="store_true",
        help="Enable trusting remote code for tokenizer",
    )
    parser.add_argument(
        "--adapter-path",
        type=str,
        help="Optional path for the trained adapter weights and config.",
    )
    parser.add_argument(
        "--extra-eos-token",
        type=str,
        default=(),
        nargs="+",
        help="Add tokens in the list of eos tokens that stop generation.",
    )
    parser.add_argument(
        "--system-prompt",
        default=None,
        help="System prompt to be used for the chat template",
    )
    parser.add_argument(
        "--prompt",
        "-p",
        default=DEFAULT_PROMPT,
        help="Message to be processed by the model ('-' reads from stdin)",
    )
    parser.add_argument(
        "--prefill-response",
        default=None,
        help="Prefill response to be used for the chat template",
    )
    parser.add_argument(
        "--max-tokens",
        "-m",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help="Maximum number of tokens to generate",
    )
    parser.add_argument(
        "--temp", type=float, default=DEFAULT_TEMP, help="Sampling temperature"
    )
    parser.add_argument(
        "--top-p", type=float, default=DEFAULT_TOP_P, help="Sampling top-p"
    )
    parser.add_argument(
        "--min-p", type=float, default=DEFAULT_MIN_P, help="Sampling min-p"
    )
    parser.add_argument(
        "--top-k", type=int, default=DEFAULT_TOP_K, help="Sampling top-k"
    )
    parser.add_argument(
        "--xtc-probability",
        type=float,
        default=DEFAULT_XTC_PROBABILITY,
        help="Probability of XTC sampling to happen each next token",
    )
    parser.add_argument(
        "--xtc-threshold",
        type=float,
        default=0.0,
        help="Thresold the probs of each next token candidate to be sampled by XTC",
    )
    parser.add_argument(
        "--min-tokens-to-keep",
        type=int,
        default=DEFAULT_MIN_TOKENS_TO_KEEP,
        help="Minimum tokens to keep for min-p sampling.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=DEFAULT_SEED,
        help="PRNG seed",
    )
    parser.add_argument(
        "--ignore-chat-template",
        action="store_true",
        help="Use the raw prompt without the tokenizer's chat template.",
    )
    parser.add_argument(
        "--use-default-chat-template",
        action="store_true",
        help="Use the default chat template",
    )
    parser.add_argument(
        "--chat-template-config",
        help="Additional config for `apply_chat_template`. Should be a dictionary of"
        " string keys to values represented as a JSON decodable string.",
        default=None,
    )
    parser.add_argument(
        "--verbose",
        type=str2bool,
        default=True,
        help="Log verbose output when 'True' or 'T' or only print the response when 'False' or 'F'",
    )
    parser.add_argument(
        "--max-kv-size",
        type=int,
        help="Set the maximum key-value cache size",
        default=None,
    )
    parser.add_argument(
        "--prompt-cache-file",
        type=str,
        default=None,
        help="A file containing saved KV caches to avoid recomputing them",
    )
    parser.add_argument(
    Args:
       model (nn.Module): The language model.
       tokenizer (PreTrainedTokenizer): The tokenizer.
       prompts (List[List[int]]): The input prompts.
       prompt_caches (List[List[Any]], optional): Pre-computed prompt-caches
          for each input prompt. Note, unlike ``generate_step``, the caches
          won't be updated in-place.
       verbose (bool): If ``True``, print tokens and timing information.
          Default: ``False``.
       max_tokens (Union[int, List[int]): Maximum number of output tokens. This
          can be per prompt if a list is provided.
       return_prompt_caches (bool): Return the prompt caches in the batch
          responses. Default: ``False``.
       kwargs: The remaining options get passed to :obj:`BatchGenerator`.
          See :obj:`BatchGenerator` for more details.
    """

    gen = BatchGenerator(
        model,
        stop_tokens=[[t] for t in tokenizer.eos_token_ids],
        **kwargs,
    )
    num_samples = len(prompts)
    fin = 0
    if verbose:
        print(f"[batch_generate] Finished processing 0/{num_samples} ...", end="\r")

    if isinstance(max_tokens, int):
        max_tokens = [max_tokens] * len(prompts)

    uids = gen.insert(prompts, max_tokens, caches=prompt_caches)
    results = {uid: [] for uid in uids}
    prompt_caches = {}
    with gen.stats() as stats:
        while responses := gen.next_generated():
            for r in responses:
                if r.finish_reason is not None:
                    if return_prompt_caches:
                        prompt_caches[r.uid] = r.prompt_cache
                    if verbose:
                        fin += 1
                        print(
                            f"[batch_generate] Finished processing {fin}/{num_samples} ...",
                            end="\r",
                        )
                if r.finish_reason != "stop":
                    results[r.uid].append(r.token)
    gen.close()
    if verbose:
        print(f"[batch_generate] Finished processing {fin}/{num_samples}")

    # Return results in correct order
    texts = [tokenizer.decode(results[uid]) for uid in uids]
    caches = [prompt_caches[uid] for uid in uids] if return_prompt_caches else None
    if verbose:
        print(
            f"[batch_generate] Prompt: {stats.prompt_tokens} tokens, {stats.prompt_tps:.3f} tokens-per-sec"
        )
        print(
            f"[batch_generate] Generation: {stats.generation_tokens} tokens, "
            f"{stats.generation_tps:.3f} tokens-per-sec"
        )
        print(f"[batch_generate] Peak memory: {stats.peak_memory:.3f} GB")
    return BatchResponse(texts, stats, caches)


def main():
    parser = setup_arg_parser()
    args = parser.parse_args()

    if args.seed is not None:
        mx.random.seed(args.seed)

    # Load the prompt cache and metadata if a cache file is provided
    using_cache = args.prompt_cache_file is not None
    if using_cache:
        prompt_cache, metadata = load_prompt_cache(
            args.prompt_cache_file,
            return_metadata=True,
        )
        if isinstance(prompt_cache[0], QuantizedKVCache):
            if args.kv_bits is not None and args.kv_bits != prompt_cache[0].bits:
                raise ValueError(
                    "--kv-bits does not match the kv cache loaded from --prompt-cache-file."
                )
            if args.kv_group_size != prompt_cache[0].group_size:
                raise ValueError(
                    "--kv-group-size does not match the kv cache loaded from --prompt-cache-file."
                )

    # Building tokenizer_config
    tokenizer_config = (
        {} if not using_cache else json.loads(metadata["tokenizer_config"])
    )
    tokenizer_config["trust_remote_code"] = True if args.trust_remote_code else None

    model_path = args.model
    if using_cache:
        if model_path is None:
            model_path = metadata["model"]
        elif model_path != metadata["model"]:
            raise ValueError(
                f"Providing a different model ({model_path}) than that "
                f"used to create the prompt cache ({metadata['model']}) "
                "is an error."
            )
    model_path = model_path or DEFAULT_MODEL

    model, tokenizer = load(
        model_path,
        adapter_path=args.adapter_path,
        tokenizer_config=tokenizer_config,
        model_config={"quantize_activations": args.quantize_activations},
    )
    for eos_token in args.extra_eos_token:
        tokenizer.add_eos_token(eos_token)
86:        "--extra-eos-token",
90:        help="Add tokens in the list of eos tokens that stop generation.",
95:        help="System prompt to be used for the chat template",
106:        help="Prefill response to be used for the chat template",
109:        "--max-tokens",
116:        "--temp", type=float, default=DEFAULT_TEMP, help="Sampling temperature"
119:        "--top-p", type=float, default=DEFAULT_TOP_P, help="Sampling top-p"
146:        "--seed",
149:        help="PRNG seed",
152:        "--ignore-chat-template",
154:        help="Use the raw prompt without the tokenizer's chat template.",
157:        "--use-default-chat-template",
159:        help="Use the default chat template",
162:        "--chat-template-config",
163:        help="Additional config for `apply_chat_template`. Should be a dictionary of"
168:        "--verbose",
171:        help="Log verbose output when 'True' or 'T' or only print the response when 'False' or 'F'",
232:    A context manager to temporarily change the wired limit.
280:        prompt_tps (float): The prompt processing tokens-per-second.
282:        generation_tps (float): The tokens-per-second for generation.
294:    generation_tps: float
721:            if token in tokenizer.eos_token_ids:
736:                generation_tps=(n + 1) / (time.perf_counter() - tic),
750:            generation_tps=(n + 1) / (time.perf_counter() - tic),
752:            finish_reason="stop" if token in tokenizer.eos_token_ids else "length",
760:    verbose: bool = False,
770:       verbose (bool): If ``True``, print tokens and timing information.
775:    if verbose:
780:        if verbose:
784:    if verbose:
791:            f"Prompt: {response.prompt_tokens} tokens, "
792:            f"{response.prompt_tps:.3f} tokens-per-sec"
795:            f"Generation: {response.generation_tokens} tokens, "
796:            f"{response.generation_tps:.3f} tokens-per-sec"
821:        prompt_tps (float): The prompt processing tokens-per-second.
824:        generation_tps (float): The tokens-per-second for generation.
833:    generation_tps: float = 0
956:                    (eos, None),
960:                    (eos, None),
964:                    (eos, None)
1582:            stats.generation_tps = stats.generation_tokens / stats.generation_time
1893:    verbose: bool = False,
1907:       verbose (bool): If ``True``, print tokens and timing information.
1919:        stop_tokens=[[t] for t in tokenizer.eos_token_ids],
1924:    if verbose:
1939:                    if verbose:
1948:    if verbose:
1954:    if verbose:
1956:            f"[batch_generate] Prompt: {stats.prompt_tokens} tokens, {stats.prompt_tps:.3f} tokens-per-sec"
1959:            f"[batch_generate] Generation: {stats.generation_tokens} tokens, "
1960:            f"{stats.generation_tps:.3f} tokens-per-sec"
1970:    if args.seed is not None:
1971:        mx.random.seed(args.seed)
2014:    for eos_token in args.extra_eos_token:
2015:        tokenizer.add_eos_token(eos_token)
2017:    template_kwargs = {}
2018:    if args.chat_template_config is not None:
2019:        template_kwargs = json.loads(args.chat_template_config)
2023:    if not args.ignore_chat_template and tokenizer.has_chat_template:
2033:        prompt = tokenizer.apply_chat_template(
2038:            **template_kwargs,
2045:            test_prompt = tokenizer.apply_chat_template(
2063:        args.temp,
2070:        xtc_special_tokens=tokenizer.encode("\n") + list(tokenizer.eos_token_ids),
2077:        verbose=args.verbose,
2087:    if not args.verbose:
rg: experiments: No such file or directory (os error 2)
scripts/axi_sc_spec_decode_spike.py:43:    "/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit"
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-mtp-energy.md:196:1. **Re-target to external-draft speculative decoding on Qwen2.5-7B + 0.5B; demote MTP to one dated
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-param-scaling-energy.md:43:- Artifact availability checks out: `Qwen2.5-0.5B-Instruct-4bit`, `-1.5B-`, `-7B-` are
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:28:  are mirrored locally: `Qwen2.5-0.5B-Instruct-4bit` (276 MB),
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:29:  `Qwen2.5-1.5B-Instruct-4bit` (839 MB), `Qwen2.5-7B-Instruct-4bit` (4.0 GB)
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-prefill-scaling-laws.md:257:  kill criterion. It is a non-risk: Qwen2.5-1.5B and Qwen2.5-7B share the same
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-long-generation-dynamics.md:61:of 4-bit weights; Qwen2.5-7B ≈ **57.3 kB/token** against ~4.2 GB. The *relative* effect
docs/phase_2/splitwise_decode_campaign.md:15:Qwen2.5-7B-Instruct-4bit (arm B), one quiet window under
docs/phase_2/splitwise_decode_campaign.md:157:`mlx-community/Qwen2.5-7B-Instruct-4bit` is **present and complete** on the
docs/phase_2/splitwise_decode_campaign.md:160:- Local directory: `/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit`
docs/phase_2/splitwise_decode_campaign.md:259:  is **greater** for Qwen2.5-7B-Instruct-4bit than for Qwen2.5-1.5B-Instruct-4bit
docs/phase_2/splitwise_decode_campaign.md:303:  Qwen2.5-7B-Instruct-4bit stack. This is a calibration, not a claim; it registers
docs/phase_2/splitwise_decode_campaign.md:343:ls -la /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-cross-runtime-contrast.md:172:`.../mlx-community/Qwen2.5-7B-Instruct-4bit`, `revision` pinned;
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-cross-runtime-contrast.md:173:`DESIGN-MEMO.md` line 208 pins "Exact Qwen2.5-7B stack identity"). A locally
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-moe-routing-energy.md:140:the M3 Max's ~400 GB/s, whereas dense Qwen2.5-7B (0.376 J/tok at ~28–36 W → ~93 tok/s ×
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-attention-variant-energy.md:27:  five: `Qwen2.5-0.5B/1.5B/7B-Instruct-4bit`, `Qwen3-4B-4bit`,
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-attention-variant-energy.md:43:Worse for the proposal's numbers: its sizing anchor is "the diagnostic Qwen2.5-7B
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-attention-variant-energy.md:155:   Qwen2.5-7B-4bit. This measures the same physical quantity — decode energy as a
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:737:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:1602:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:2539:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:2986:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:6393:docs/process_traces/2026-07-17-axi-sc-live-probes/axi-sc-mlx-draft.jsonl:21:{"acceptance_rate":null,"acceptance_rate_reason":"tokens_proposed_unavailable","decode_emission_event_count":0,"decode_emission_observation_source":null,"draft_model_call_count":11,"draft_model_calls":[{"call_index":0,"input_shape":[1,7],"returned_at_s":87641.681954791,"started_at_s":87641.681045916},{"call_index":1,"input_shape":[1,1],"returned_at_s":87641.884285291,"started_at_s":87641.883759916},{"call_index":2,"input_shape":[1,1],"returned_at_s":87641.897267875,"started_at_s":87641.896696208},{"call_index":3,"input_shape":[1,1],"returned_at_s":87641.898896166,"started_at_s":87641.898401333},{"call_index":4,"input_shape":[1,1],"returned_at_s":87641.923045833,"started_at_s":87641.922548041},{"call_index":5,"input_shape":[1,1],"returned_at_s":87641.9247455,"started_at_s":87641.924221875},{"call_index":6,"input_shape":[1,1],"returned_at_s":87641.926452125,"started_at_s":87641.925941958},{"call_index":7,"input_shape":[1,1],"returned_at_s":87641.93755125,"started_at_s":87641.937052916},{"call_index":8,"input_shape":[1,1],"returned_at_s":87641.93927175,"started_at_s":87641.938778625},{"call_index":9,"input_shape":[1,1],"returned_at_s":87641.940946916,"started_at_s":87641.940447833},{"call_index":10,"input_shape":[1,1],"returned_at_s":87641.951204625,"started_at_s":87641.950757333}],"draft_model_identity":{"model_artifact_sha256":"00677cdd25ec2d50ac51fdaed630409dc41257030fa7fe0b38b4d6236cb93b8b","model_name":"Qwen2.5-0.5B-Instruct-4bit","model_revision":"local-artifact-sha256:00677cdd25ec2d50ac51fdaed630409dc41257030fa7fe0b38b4d6236cb93b8b","quantization":"{\"bits\":4,\"group_size\":64}","runtime_backend":"mlx-lm","runtime_version":"0.31.3","tokenizer":{"class":"TokenizerWrapper","name":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","revision":"local-config-sha256:b045e57ea90b8f1b35f89f954b176a5c1faa02bd0af2c89bcec191239d66cef4","vocabulary_size":151643},"weight_format":"safetensors"},"draft_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","event":"capability_observation","generation_completed":true,"loaded_draft_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","loaded_target_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit","max_proposed_tokens":3,"max_tokens":8,"mode":"draft_model","native_mtp_execution_observed":false,"native_mtp_identity":null,"output_token_count":8,"output_token_ids":[362,5546,374,264,3890,429,61600,553],"output_token_ids_sha256":"193ea6ea4e10060f1ccbe0f19d9d03a71acd0fb3ea02e29c88f0324cf2530dd6","prompt_sha256":"0d5d3571058d31054b2108db28821b289de7ecc7266929214ea4dc788b6c5a41","recorded_at_utc":"2026-07-17T07:30:12.415938Z","request_id":"axi-sc-000","runtime_available":true,"runtime_generation_evidence_source":"target_and_draft_model_call_observers_plus_stream_generate","runtime_generation_supported":true,"schema":"joulewise.axi_sc_spec_decode_spike.v1","sequence":20,"target_model_call_count":5,"target_model_calls":[{"call_index":0,"input_shape":[1,7],"returned_at_s":87641.869895,"started_at_s":87641.869069208},{"call_index":1,"input_shape":[1,4],"returned_at_s":87641.900746625,"started_at_s":87641.900121916},{"call_index":2,"input_shape":[1,4],"returned_at_s":87641.928274041,"started_at_s":87641.927640458},{"call_index":3,"input_shape":[1,4],"returned_at_s":87641.942726625,"started_at_s":87641.942138708},{"call_index":4,"input_shape":[1,2],"returned_at_s":87641.952949708,"started_at_s":87641.952387541}],"target_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit","tokens_accepted":4,"tokens_accepted_observation_source":"GenerationResponse.from_draft","tokens_proposed":null,"tokens_proposed_observation_source":null}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:7872:863-Qwen2.5-7B-Instruct, Llama-3.2-1B-Instruct, Llama-3.2-3B-Instruct,
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:8107:| Spec decode on/off | Qwen2.5-7B (or Qwen3-8B) alone | same + 0.5B/0.6B draft | ~4.4 GB | **Verified**: `mlx_lm.generate --draft-model` exists ([issue #250](https://github.com/ml-explore/mlx-lm/issues/250), [#1132](https://github.com/ml-explore/mlx-lm/issues/1132)) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:8127:| 4 | KV-quant 4b vs fp16, long ctx | Qwen2.5-7B KV ≈57 KB/tok fp16 → ~9.6% of decode bandwidth at 8k ctx; save ~75% of it ≈ 3.5% avg over 0→8k | ×8192 ≈ **~100 J** (concentrated late — phase resolution helps) | **~7×** at full 8k; marginal below 4k |
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-quantization-ladder.md:34:- `Qwen2.5-7B-Instruct-4bit` (4.0 GB), revision `c26a38f6…d9fed`
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:1217:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:1866:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:2194:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:2691:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:2800:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:6497:joulewise/analysis_manifest_v3.py:132:                    "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit"
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:6499:joulewise/analysis_manifest_v3.py:150:                    "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit"
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:7682:JouleWise already has the scientific core of this paper: an in-window pulse-train calibration for phase-boundary attribution; the finding that roughly 30 ms of edge uncertainty across roughly 33 W makes the instrument attribution-limited at about 1 J per phase member; separately enforced floor-clearance and interval-supported-direction gates, producing an effective phase-contrast sizing bar near 5 J; and a fail-closed protocol built around pre-registration, admission checks, ABBA ordering, live brackets, immutable custody, and publishable refusals. The [MVP draft](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/paper/draft-v1.md>) supplies essentially all method, metrology, related-work, and limitations prose. First execute D-117 unchanged: the approximately 3.14 h 1.5B MLX floor window, 3.24 h 7B MLX floor window, and 2.80 h MLX model-size contrast window, with prefill floors riding the first two. Mint those four phase-floor cells and populate the MVP. Then perform a read-only/daytime feasibility stage for llama.cpp: pin one llama.cpp commit and Metal build; derive a GGUF 4-bit artifact and the MLX 4-bit artifact from the same Qwen2.5-7B-Instruct source revision; implement and validate real prefill/decode markers; and run explicitly non-claim pilot comparisons. If the desk gate passes, collect one approximately 3.3 h llama.cpp 7B floor window and one approximately 3.0–3.5 h MLX-versus-llama.cpp ABBA contrast window. Thus the proposal costs **five quiet nights from today—three already required by D-117 plus two new nights**—and perhaps 2–4 weeks of desk engineering. It does not displace or weaken the MVP: if the extension dies, the original paper remains intact.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:7696:The primary model is Qwen2.5-7B-Instruct, nominal 4-bit, because the historical diagnostic 7B decode-cell mean is about **192.39 J** for 512 output tokens. Therefore 3%, 5%, and 10% stack differences correspond to approximately **5.77, 9.62, and 19.24 J**. These are planning calculations, not predictions. The comparison becomes difficult only when the stacks are within roughly **2.6%**. Public project documentation establishes that llama.cpp supports Metal on Apple silicon and several 4-bit formats, while MLX-LM supports Apple-silicon inference and its own model conversion/quantization path; it does **not** provide a trustworthy paired energy estimate for this exact machine and workload. [llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/README.md), [llama.cpp quantization](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md), [MLX-LM](https://github.com/ml-explore/mlx-lm).
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:7738:JouleWise already has the scientific core of this paper: an in-window pulse-train calibration for phase-boundary attribution; the finding that roughly 30 ms of edge uncertainty across roughly 33 W makes the instrument attribution-limited at about 1 J per phase member; separately enforced floor-clearance and interval-supported-direction gates, producing an effective phase-contrast sizing bar near 5 J; and a fail-closed protocol built around pre-registration, admission checks, ABBA ordering, live brackets, immutable custody, and publishable refusals. The [MVP draft](</private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/paper/draft-v1.md>) supplies essentially all method, metrology, related-work, and limitations prose. First execute D-117 unchanged: the approximately 3.14 h 1.5B MLX floor window, 3.24 h 7B MLX floor window, and 2.80 h MLX model-size contrast window, with prefill floors riding the first two. Mint those four phase-floor cells and populate the MVP. Then perform a read-only/daytime feasibility stage for llama.cpp: pin one llama.cpp commit and Metal build; derive a GGUF 4-bit artifact and the MLX 4-bit artifact from the same Qwen2.5-7B-Instruct source revision; implement and validate real prefill/decode markers; and run explicitly non-claim pilot comparisons. If the desk gate passes, collect one approximately 3.3 h llama.cpp 7B floor window and one approximately 3.0–3.5 h MLX-versus-llama.cpp ABBA contrast window. Thus the proposal costs **five quiet nights from today—three already required by D-117 plus two new nights**—and perhaps 2–4 weeks of desk engineering. It does not displace or weaken the MVP: if the extension dies, the original paper remains intact.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:7752:The primary model is Qwen2.5-7B-Instruct, nominal 4-bit, because the historical diagnostic 7B decode-cell mean is about **192.39 J** for 512 output tokens. Therefore 3%, 5%, and 10% stack differences correspond to approximately **5.77, 9.62, and 19.24 J**. These are planning calculations, not predictions. The comparison becomes difficult only when the stacks are within roughly **2.6%**. Public project documentation establishes that llama.cpp supports Metal on Apple silicon and several 4-bit formats, while MLX-LM supports Apple-silicon inference and its own model conversion/quantization path; it does **not** provide a trustworthy paired energy estimate for this exact machine and workload. [llama.cpp](https://github.com/ggml-org/llama.cpp/blob/master/README.md), [llama.cpp quantization](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md), [MLX-LM](https://github.com/ml-explore/mlx-lm).
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-advisor.md:1128:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-advisor.md:1892:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-advisor.md:2220:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/phase_3/phase_3_plan.md:82:| Qwen2.5-7B | 28 | 4 | 128 | 56 | 112 | 448 |
docs/phase_3/phase_3_plan.md:92:| Qwen2.5-7B (112 MiB) | ~1.0 s | ~0.4 s | ~0.1 s |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:192:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:520:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:1268:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:1868:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/decision_log.md:864:Qwen2.5-7B-Instruct, Llama-3.2-1B-Instruct, Llama-3.2-3B-Instruct,
docs/decision_log.md:886:supervisor scope, the mid-model pick (leaning Qwen2.5-7B-Instruct, same
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:386:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:797:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:1345:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:1743:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:4994:docs/campaign_packs/split_suite_q1_q2_q3.md:34:| selection_scope | Frozen split matrix for `<<DEVICE_PAIR>>`, `<<MODEL_SET>>` resolved at registry freeze to either `{Qwen2.5-1.5B}` or `{Qwen2.5-1.5B, Qwen2.5-7B}`, prompt lengths `{512,2048,8192}`, decode length `256`, links `<<LINK_MBPS_SET>>`, split mode `offline_replay` unless explicitly frozen as analytical composition, and both required monolithic references for the same model/runtime/artifact. Dropping the 7B cells requires named `DROP-FEASIBILITY-P1-004-P1-006-MODEL-7B` evidence before any campaign bundle exists. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:5443:docs/process_traces/2026-07-17-axi-sc-live-probes/axi-sc-mlx-draft.jsonl:1:{"draft_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","event":"probe_start","max_proposed_tokens":3,"max_tokens":8,"measurement_kind":"feasibility_not_energy","mode":"draft_model","probe":"pinned_mlx_lm_spec_decode","prompt_sha256":"0d5d3571058d31054b2108db28821b289de7ecc7266929214ea4dc788b6c5a41","recorded_at_utc":"2026-07-17T07:30:10.767278Z","request_id":"axi-sc-000","schema":"joulewise.axi_sc_spec_decode_spike.v1","sequence":0,"target_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit","timeout_seconds":300.0}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:5459:rg -n 'Qwen2.5-1.5B|Qwen2.5-7B' docs configs | rg -i 'kv|head|layer|bytes|cache|config' | head -150" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6025:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r02.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6026:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r02.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6027:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r02.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6036:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r03.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6037:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r03.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6038:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r03.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6043:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r04.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6044:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r04.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6045:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r04.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6055:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r08.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6056:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r08.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6057:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r08.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6061:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r09.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6062:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r09.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6063:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r09.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6066:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r05.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6067:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r05.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6068:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r05.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6072:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r10.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6073:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r10.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6074:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r10.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6080:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r06.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6081:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r06.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6082:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r06.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6090:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r07.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6091:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r07.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6092:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r07.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6096:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r01.json:5:    "name": "Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6097:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r01.json:7:    "source": "/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:6098:configs/campaigns/qwen25_7b_decode_floor_v1/01_phase_decode_absolute/sw7bfloor-df-ph-decode-abs-r01.json:22:    "notes": "Qwen2.5-7B decode-phase floor calibration on the current M3 Max; normal powermetrics sampler set only."
docs/stream_logs/2026-07-17-axi-sc.md:133:draft probe target and name Qwen2.5-0.5B-Instruct-4bit as the required smaller
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-long-generation-dynamics.md:1349:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-long-generation-dynamics.md:1968:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-long-generation-dynamics.md:3917:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:956:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:1284:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:2507:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:2896:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:3232:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:3733:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5813:docs/process_traces/2026-07-17-axi-sc-live-probes/axi-sc-mlx-draft.jsonl:5:{"config_present":true,"config_sha256":"b045e57ea90b8f1b35f89f954b176a5c1faa02bd0af2c89bcec191239d66cef4","directory_present":true,"event":"model_artifact","model_type":"qwen2","native_mtp_candidate_config":{"mtp_num_hidden_layers":null,"mtp_use_dedicated_embeddings":null},"quantization":{"bits":4,"group_size":64},"recorded_at_utc":"2026-07-17T07:30:10.774510Z","requested_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","resolved_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","role":"draft","schema":"joulewise.axi_sc_spec_decode_spike.v1","sequence":4,"vocabulary_size":151936}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5814:docs/process_traces/2026-07-17-axi-sc-live-probes/axi-sc-mlx-draft.jsonl:20:{"draft_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","event":"request_terminal","max_proposed_tokens":3,"max_tokens":8,"mode":"draft_model","output_token_count":8,"output_token_ids":[362,5546,374,264,3890,429,61600,553],"output_token_ids_sha256":"193ea6ea4e10060f1ccbe0f19d9d03a71acd0fb3ea02e29c88f0324cf2530dd6","prompt_sha256":"0d5d3571058d31054b2108db28821b289de7ecc7266929214ea4dc788b6c5a41","recorded_at_utc":"2026-07-17T07:30:12.415922Z","request_id":"axi-sc-000","schema":"joulewise.axi_sc_spec_decode_spike.v1","sequence":19,"stop_reason":"length","target_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit","terminal_timestamp_s":87641.963801666}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5815:docs/process_traces/2026-07-17-axi-sc-live-probes/axi-sc-mlx-draft.jsonl:21:{"acceptance_rate":null,"acceptance_rate_reason":"tokens_proposed_unavailable","decode_emission_event_count":0,"decode_emission_observation_source":null,"draft_model_call_count":11,"draft_model_calls":[{"call_index":0,"input_shape":[1,7],"returned_at_s":87641.681954791,"started_at_s":87641.681045916},{"call_index":1,"input_shape":[1,1],"returned_at_s":87641.884285291,"started_at_s":87641.883759916},{"call_index":2,"input_shape":[1,1],"returned_at_s":87641.897267875,"started_at_s":87641.896696208},{"call_index":3,"input_shape":[1,1],"returned_at_s":87641.898896166,"started_at_s":87641.898401333},{"call_index":4,"input_shape":[1,1],"returned_at_s":87641.923045833,"started_at_s":87641.922548041},{"call_index":5,"input_shape":[1,1],"returned_at_s":87641.9247455,"started_at_s":87641.924221875},{"call_index":6,"input_shape":[1,1],"returned_at_s":87641.926452125,"started_at_s":87641.925941958},{"call_index":7,"input_shape":[1,1],"returned_at_s":87641.93755125,"started_at_s":87641.937052916},{"call_index":8,"input_shape":[1,1],"returned_at_s":87641.93927175,"started_at_s":87641.938778625},{"call_index":9,"input_shape":[1,1],"returned_at_s":87641.940946916,"started_at_s":87641.940447833},{"call_index":10,"input_shape":[1,1],"returned_at_s":87641.951204625,"started_at_s":87641.950757333}],"draft_model_identity":{"model_artifact_sha256":"00677cdd25ec2d50ac51fdaed630409dc41257030fa7fe0b38b4d6236cb93b8b","model_name":"Qwen2.5-0.5B-Instruct-4bit","model_revision":"local-artifact-sha256:00677cdd25ec2d50ac51fdaed630409dc41257030fa7fe0b38b4d6236cb93b8b","quantization":"{\"bits\":4,\"group_size\":64}","runtime_backend":"mlx-lm","runtime_version":"0.31.3","tokenizer":{"class":"TokenizerWrapper","name":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","revision":"local-config-sha256:b045e57ea90b8f1b35f89f954b176a5c1faa02bd0af2c89bcec191239d66cef4","vocabulary_size":151643},"weight_format":"safetensors"},"draft_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","event":"capability_observation","generation_completed":true,"loaded_draft_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit","loaded_target_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit","max_proposed_tokens":3,"max_tokens":8,"mode":"draft_model","native_mtp_execution_observed":false,"native_mtp_identity":null,"output_token_count":8,"output_token_ids":[362,5546,374,264,3890,429,61600,553],"output_token_ids_sha256":"193ea6ea4e10060f1ccbe0f19d9d03a71acd0fb3ea02e29c88f0324cf2530dd6","prompt_sha256":"0d5d3571058d31054b2108db28821b289de7ecc7266929214ea4dc788b6c5a41","recorded_at_utc":"2026-07-17T07:30:12.415938Z","request_id":"axi-sc-000","runtime_available":true,"runtime_generation_evidence_source":"target_and_draft_model_call_observers_plus_stream_generate","runtime_generation_supported":true,"schema":"joulewise.axi_sc_spec_decode_spike.v1","sequence":20,"target_model_call_count":5,"target_model_calls":[{"call_index":0,"input_shape":[1,7],"returned_at_s":87641.869895,"started_at_s":87641.869069208},{"call_index":1,"input_shape":[1,4],"returned_at_s":87641.900746625,"started_at_s":87641.900121916},{"call_index":2,"input_shape":[1,4],"returned_at_s":87641.928274041,"started_at_s":87641.927640458},{"call_index":3,"input_shape":[1,4],"returned_at_s":87641.942726625,"started_at_s":87641.942138708},{"call_index":4,"input_shape":[1,2],"returned_at_s":87641.952949708,"started_at_s":87641.952387541}],"target_model_path":"/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit","tokens_accepted":4,"tokens_accepted_observation_source":"GenerationResponse.from_draft","tokens_proposed":null,"tokens_proposed_observation_source":null}
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:384:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:712:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:2814:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:3142:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:3894:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:4230:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:6350:| selection_scope | Frozen split matrix for `<<DEVICE_PAIR>>`, `<<MODEL_SET>>` resolved at registry freeze to either `{Qwen2.5-1.5B}` or `{Qwen2.5-1.5B, Qwen2.5-7B}`, prompt lengths `{512,2048,8192}`, decode length `256`, links `<<LINK_MBPS_SET>>`, split mode `offline_replay` unless explicitly frozen as analytical composition, and both required monolithic references for the same model/runtime/artifact. Dropping the 7B cells requires named `DROP-FEASIBILITY-P1-004-P1-006-MODEL-7B` evidence before any campaign bundle exists. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:6852:docs/campaign_packs/split_suite_q1_q2_q3.md:34:| selection_scope | Frozen split matrix for `<<DEVICE_PAIR>>`, `<<MODEL_SET>>` resolved at registry freeze to either `{Qwen2.5-1.5B}` or `{Qwen2.5-1.5B, Qwen2.5-7B}`, prompt lengths `{512,2048,8192}`, decode length `256`, links `<<LINK_MBPS_SET>>`, split mode `offline_replay` unless explicitly frozen as analytical composition, and both required monolithic references for the same model/runtime/artifact. Dropping the 7B cells requires named `DROP-FEASIBILITY-P1-004-P1-006-MODEL-7B` evidence before any campaign bundle exists. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:7206:| Qwen2.5-7B | 28 | 4 | 128 | 56 | 112 | 448 |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:7216:| Qwen2.5-7B (112 MiB) | ~1.0 s | ~0.4 s | ~0.1 s |
docs/specs/axi/sc_spec_decode_verdict.md:198:  `/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit`. This was the
docs/specs/axi/sc_spec_decode_verdict.md:227:  --draft-model /Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit \
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:193:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:1453:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:2029:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:2627:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:5200:CLAIMS_STATUS.md:62:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:5221:docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.log:2029:./CLAIMS_STATUS.md:49:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **HARD-BLOCKED by D-110** (RT-2 dependency edge): CAL-BRACKET-D079-01 must land (held at `2e61ff9`, one audit blocker B1 outstanding; round 2 needs its rule-11 gate) + acceptance-artifact issuance + validator pin widening — THEN the governed mint. The 2026-08-03 night consult's conditional mint license is SUSPENDED on the record. |
docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:207:| 7B floor | Entire `configs/campaigns/qwen25_7b_decode_floor_v1/`, including plan, SHA, generator, root/stage manifests, ten absolute configs, and two twenty-member ABBA halves | Ratified D-085 condition family, Qwen2.5-7B model identity, 10+40 design, midpoint split |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-contrarian.md:1543:| **7B decode floors (Qwen2.5-7B)** | absolute 6.294380135190098 J / comparative 13.998036715259254 J (absolute-cell member mean 192.386233 J, n=10 — always name the cell) | `window_7bfloor_20260729`, **PASSED**, governed extraction clean | **RE-SCOPED by D-117 (2026-08-07):** `window_7bfloor_20260729` is pre-genesis and cannot be claim-consumed; these values are DIAGNOSTIC and design inputs for the fresh 7B floor window (D-117 cl.2). The prior D-110 condition chain completed and was then superseded. |
/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit
/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit
/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit
0.31.3
0.31.2
/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py

codex
Probe A’s installed pin is confirmed as `mlx-lm 0.31.3` / `mlx 0.31.2`, with all three local Qwen2.5 artifacts present. The stock CLI reports generation tok/s itself; its source exposes `--draft-model`, `--num-draft-tokens`, greedy `--temp 0`, `--seed`, and `--max-tokens`, so the pilot can stay entirely outside JouleWise instrumentation.
exec
/bin/zsh -lc "rg -n \"nvidia-smi|pynvml|nvml|power.draw|power\\.draw|sampling\" joulewise scripts tests docs/phase_2 docs/JouleWise_Hardening_Proposal.md | head -n 300; sed -n '930,990p' docs/decision_log.md; sed -n '2660,2705p' docs/decision_log.md; sed -n '20,90p' docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md; sed -n '250,340p' docs/JouleWise_Hardening_Proposal.md; rg -n \"3080|NVIDIA|P1-006|access|SSH\" docs/milestones.md docs/risk_register.md docs/phase_1 docs/phase_2 TASK_QUEUE.md | head -n 240" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
docs/JouleWise_Hardening_Proposal.md:198:   - Implement `sampling.warmup_seconds` as post-warmup settling outside the measured window, or remove it in a versioned schema change. Do not silently accept a dead experimental control.
docs/JouleWise_Hardening_Proposal.md:283:#### Timing and sampling hardening
docs/JouleWise_Hardening_Proposal.md:453:4. nvidia-smi cadence and averaging characterization.
docs/JouleWise_Hardening_Proposal.md:772:**Capability suite.** Use a small, frozen suite spanning at least factual/commonsense selection, mathematical reasoning, and code generation. Prefer tasks with deterministic scoring. Record prompt templates, tokenizer, chat template, sampling policy, maximum output length, stopping rules, and scorer version. Do not infer broad “intelligence” from one benchmark.
docs/phase_2/splitwise_decode_campaign.md:205:idle, 5 s warmup seconds, arm/settle, sampling teardown); the model-dependent term
docs/phase_2/splitwise_decode_campaign.md:473:   `repetitions: 1`, `warmup_runs: 1`; sampling `power_hz 10.0`,
docs/phase_2/phase_2_plan.md:51:  2G MLX runtime    2H powermetrics telemetry      2K vLLM + nvidia-smi (gated: P1-006)
docs/phase_2/phase_2_plan.md:120:  the sampling factor is recorded in metadata)
docs/phase_2/phase_2_plan.md:228:  warmup 6.0 W, measured 7.5 W) sampled at `sampling.power_hz`, so the
docs/phase_2/phase_2_plan.md:269:- Idle baseline: `telemetry.measure_idle` for `sampling.idle_seconds`;
docs/phase_2/phase_2_plan.md:272:  followed by a `sampling.warmup_seconds` post-active-warmup settling wait,
docs/phase_2/phase_2_plan.md:273:  strictly before the measured-run and `start_sampling` markers. The wait uses
docs/phase_2/phase_2_plan.md:276:- Measured window: `start_sampling` -> `run_workload` -> `stop_sampling`.
docs/phase_2/phase_2_plan.md:278:  log records buffer in memory and flush after `stop_sampling`.
docs/phase_2/phase_2_plan.md:323:- Measurement quality: observed_sampling_hz from median inter-sample gap;
docs/phase_2/phase_2_plan.md:430:   and `start_sampling`; under `SystemClock` real sampler spawn latency
docs/phase_2/phase_2_plan.md:433:   after sampling is confirmed started) or record explicit
docs/phase_2/phase_2_plan.md:434:   sampling-active markers the reducer uses. FakeClock cannot catch
docs/phase_2/phase_2_plan.md:445:   or bucket within a tolerance derived from the sampling interval;
docs/phase_2/phase_2_plan.md:532:Objective: real Apple Silicon power/thermal sampling into the bundle
docs/phase_2/phase_2_plan.md:549:observed_sampling_hz within 20% of requested at 1-10 Hz; permission-denied
docs/phase_2/phase_2_plan.md:606:## Slice 2K: NVIDIA/vLLM + nvidia-smi + SSH Transport
docs/phase_2/phase_2_plan.md:608:Objective: first remote target: vLLM runtime and nvidia-smi telemetry over
docs/phase_2/phase_2_plan.md:611:Gates: P1-006 evidence (SSH reachable, `nvidia-smi` power queries work,
docs/phase_2/phase_2_plan.md:615:protocol — the design center, reused by 2L and Phase 3 — nvidia-smi
docs/phase_2/phase_2_plan.md:625:host/missing nvidia-smi paths demonstrated.
docs/phase_2/phase_2_plan.md:690:- Prefill-heavy vs decode-heavy profiles show the expected power-draw
docs/phase_2/window_runbook.md:319:Ordinary sampling load, thermal state, and CPU activity cannot move the wall
tests/test_controller.py:85:        ("sampling_started", "measured_run"),
tests/test_controller.py:93:        ("sampling_stopped", "measured_run"),
tests/test_controller.py:249:    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
tests/test_controller.py:250:        result = self._inner.start_sampling(config, context)
tests/test_controller.py:256:    def stop_sampling(self, config: BenchmarkConfig, context=None):
tests/test_controller.py:258:        samples = self._inner.stop_sampling(config, context)
tests/test_controller.py:297:    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
tests/test_controller.py:298:        result = self._inner.start_sampling(config, context)
tests/test_controller.py:311:    def stop_sampling(self, config: BenchmarkConfig, context=None):
tests/test_controller.py:313:        samples = self._inner.stop_sampling(config, context)
tests/test_controller.py:360:    def stop_sampling(self, config: BenchmarkConfig, context=None):
tests/test_controller.py:363:            raise AssertionError("stop_sampling must not be called twice")
tests/test_controller.py:364:        samples = self._inner.stop_sampling(config, context)
tests/test_controller.py:399:    metadata AND fails start_sampling (to drive the structured failure path)."""
tests/test_controller.py:424:    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
tests/test_controller.py:428:            message="injected start_sampling failure",
tests/test_controller.py:431:    def stop_sampling(self, config: BenchmarkConfig, context=None):
tests/test_controller.py:432:        return self._inner.stop_sampling(config)
tests/test_controller.py:468:    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
tests/test_controller.py:469:        return self._inner.start_sampling(config, context)
tests/test_controller.py:471:    def stop_sampling(self, config: BenchmarkConfig, context=None):
tests/test_controller.py:472:        return self._inner.stop_sampling(config, context)
tests/test_controller.py:514:    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
tests/test_controller.py:515:        return self._inner.start_sampling(config, context)
tests/test_controller.py:517:    def stop_sampling(self, config: BenchmarkConfig, context=None):
tests/test_controller.py:518:        return self._inner.stop_sampling(config, context)
tests/test_controller.py:749:    config_payload["sampling"].update(
tests/test_controller.py:806:            post_window_sampling_dwell_s=1.0,
tests/test_controller.py:1147:        self.assertEqual(quality["requested_sampling_hz"], 2.0)
tests/test_controller.py:1161:    def test_warmup_seconds_advances_injected_clock_before_sampling(self) -> None:
tests/test_controller.py:1164:        data["sampling"]["warmup_seconds"] = 7.25
tests/test_controller.py:1187:        sampling_started = next(
tests/test_controller.py:1188:            event for event in events if event["event_type"] == "sampling_started"
tests/test_controller.py:1203:            sampling_started["timestamp_s"], measured_started["timestamp_s"]
tests/test_controller.py:1246:        data["sampling"]["power_hzz"] = 99
tests/test_controller.py:1247:        with self.assertWarnsRegex(UserWarning, "sampling.power_hzz"):
tests/test_controller.py:1258:                        "unknown config key 'sampling.power_hzz' ignored by schema 0.1"
tests/test_controller.py:1260:                    "path": "sampling.power_hzz",
tests/test_controller.py:1265:        self.assertNotIn("power_hzz", normalized["sampling"])
tests/test_controller.py:1546:        self.assertNotIn("sampling_started", [event["event_type"] for event in events])
tests/test_controller.py:1616:        self.assertFalse(registry.adapter._admission_sampling_start_requested)
tests/test_controller.py:1617:        self.assertFalse(registry.adapter._admission_sampling_handoff_pending)
tests/test_controller.py:1652:        config_payload["sampling"].update(
tests/test_controller.py:1715:                post_window_sampling_dwell_s=1.0,
tests/test_controller.py:1722:        self.assertFalse(registry.adapter._admission_sampling_handoff_pending)
tests/test_controller.py:1775:            patch.object(adapter, "start_sampling", side_effect=interrupted_start),
tests/test_controller.py:1778:            adapter.begin_admission_window_sampling(config)
tests/test_controller.py:1780:        self.assertFalse(adapter._admission_sampling_start_requested)
tests/test_controller.py:1782:        self.assertEqual(adapter.stop_sampling(config), [])
tests/test_controller.py:1784:        self.assertFalse(adapter._admission_sampling_handoff_pending)
tests/test_controller.py:1785:        self.assertIsNone(adapter._admission_sampling_metadata)
tests/test_controller.py:1793:            adapter._admission_sampling_metadata = dict(metadata)
tests/test_controller.py:1796:        with patch.object(adapter, "start_sampling", side_effect=successful_start):
tests/test_controller.py:1797:            result = adapter.begin_admission_window_sampling(config)
tests/test_controller.py:1799:        self.assertTrue(adapter._admission_sampling_handoff_pending)
tests/test_controller.py:1800:        self.assertEqual(adapter.stop_sampling(config), [])
tests/test_controller.py:1802:        self.assertFalse(adapter._admission_sampling_start_requested)
tests/test_controller.py:1803:        self.assertFalse(adapter._admission_sampling_handoff_pending)
tests/test_controller.py:1804:        self.assertIsNone(adapter._admission_sampling_metadata)
tests/test_controller.py:1808:            adapter._admission_sampling_metadata = {"stale": True}
tests/test_controller.py:1815:        with patch.object(adapter, "start_sampling", side_effect=failed_rollover):
tests/test_controller.py:1816:            result = adapter.begin_admission_window_sampling(config)
tests/test_controller.py:1818:        self.assertFalse(adapter._admission_sampling_start_requested)
tests/test_controller.py:1819:        self.assertFalse(adapter._admission_sampling_handoff_pending)
tests/test_controller.py:1820:        self.assertIsNone(adapter._admission_sampling_metadata)
tests/test_controller.py:2231:        self.assertNotIn("sampling_started", [event["event_type"] for event in events])
tests/test_controller.py:2311:    path (start_sampling fails), must NOT escape execute(): the bundle still
tests/test_controller.py:2401:    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
tests/test_controller.py:2403:        # BEFORE sampling is confirmed active.
tests/test_controller.py:2405:        return self._inner.start_sampling(config, context)
tests/test_controller.py:2407:    def stop_sampling(self, config: BenchmarkConfig, context=None):
tests/test_controller.py:2408:        samples = self._inner.stop_sampling(config, context)
tests/test_controller.py:2519:        self.assertTrue(telemetry.start_sampling(config, context).ok)
tests/test_controller.py:2521:        samples = telemetry.stop_sampling(config, context)
tests/test_controller.py:2525:    def test_stop_sampling_without_context_writes_no_raw_output(self) -> None:
tests/test_controller.py:2533:        self.assertTrue(telemetry.start_sampling(config).ok)
tests/test_controller.py:2535:        samples = telemetry.stop_sampling(config)
tests/test_controller.py:2562:        self.assertIn("sampling_started", types)
tests/test_controller.py:2563:        self.assertIn("sampling_stopped", types)
tests/test_controller.py:2564:        started = types.index("sampling_started")
tests/test_controller.py:2565:        stopped = types.index("sampling_stopped")
tests/test_controller.py:2601:        data["sampling"]["power_hz"] = 100.0
tests/test_controller.py:2630:        # The sampling_stopped timestamp is taken as soon as the runtime
tests/test_controller.py:2637:            if event["event_type"] == "sampling_stopped"
tests/test_controller.py:2654:            post_window_sampling_dwell_s=0.0,
tests/test_controller.py:2660:            post_window_sampling_dwell_s=0.75,
tests/test_controller.py:2675:            if event["event_type"] == "sampling_stopped"
tests/test_controller.py:2680:            if event["event_type"] == "sampling_stopped"
tests/test_controller.py:2695:                post_window_sampling_dwell_s=0.999,
tests/test_controller.py:2710:            by_type["sampling_started"] - by_type["stage_started"], 3.0, places=9
tests/test_controller.py:2713:            by_type["stage_completed"] - by_type["sampling_stopped"], 2.0
tests/test_controller.py:2771:        sampling_started = types.index("sampling_started")
tests/test_controller.py:2772:        sampling_stopped = types.index("sampling_stopped")
tests/test_controller.py:2775:        self.assertLess(sampling_started, types.index("suite_start"))
tests/test_controller.py:2776:        self.assertLess(types.index("suite_end"), sampling_stopped)
tests/test_controller.py:2781:        self.assertTrue(all(sampling_started < index < sampling_stopped for index in suite_indices))
docs/phase_2/splitwise_replication_roadmap.md:104:numeric `nvidia-smi power.draw`, runner behavior, trace integrity); P1-004
joulewise/powermetrics_fiducial.py:89:    "sampling_interval_ms",
joulewise/powermetrics_fiducial.py:239:            "sampling_interval_ms": SAMPLING_INTERVAL_MS,
joulewise/powermetrics_fiducial.py:283:        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
joulewise/powermetrics_fiducial.py:352:    the 0.1 s sampling interval.
joulewise/powermetrics_fiducial.py:566:    This is an analytic interval branch-and-bound, not directional sampling.
tests/test_calibration_bracketing.py:321:                            "sampling_interval_ms",
tests/test_calibration_bracketing.py:389:                "sampling_interval_ms": 100,
tests/test_calibration_bracketing.py:739:                        "sampling_interval_ms",
tests/test_calibration_bracketing.py:1406:                                "sampling_interval_ms",
docs/phase_2/hardware_slice_implementation_guide.md:99:  (the controller already calls warmup before `start_sampling`).
docs/phase_2/hardware_slice_implementation_guide.md:146:  `sampling.power_hz`. `start_sampling` launches it (capturing the `Popen`);
docs/phase_2/hardware_slice_implementation_guide.md:147:  `stop_sampling` terminates the sudo process (sudo relays SIGTERM to the
docs/phase_2/hardware_slice_implementation_guide.md:151:  `start_sampling`): probe `sudo -n /usr/bin/powermetrics -n 1 -i 100 ...`;
docs/phase_2/hardware_slice_implementation_guide.md:162:  `sampling.idle_seconds`; mean/stddev computed from parsed samples;
docs/phase_2/hardware_slice_implementation_guide.md:186:## Slice 2K: NVIDIA/vLLM + nvidia-smi + SSH Transport
docs/phase_2/hardware_slice_implementation_guide.md:214:- **nvidia-smi telemetry** (`name = "nvidia_smi"`): remote
docs/phase_2/hardware_slice_implementation_guide.md:215:  `nvidia-smi --query-gpu=timestamp,power.draw,temperature.gpu
docs/phase_2/hardware_slice_implementation_guide.md:225:nvidia-smi; runner-script arg handling. Real-node smoke when P1-006 evidence
joulewise/doctor.py:440:            "power_hz": row["config"].sampling.power_hz,
joulewise/doctor.py:441:            "idle_seconds": row["config"].sampling.idle_seconds,
joulewise/doctor.py:442:            "warmup_seconds": row["config"].sampling.warmup_seconds,
joulewise/doctor.py:450:            f"{len(sampler_rows)} sampling configuration(s); powermetrics requests {SAMPLERS}",
joulewise/doctor.py:453:                "sampling": sampler_rows,
joulewise/doctor.py:655:            for row in details["sampling"]
joulewise/doctor.py:657:        return f"requested={requested}; {configured or 'no config sampling fields'}"
docs/phase_2/refusal_scope_spec.md:21:| insufficient_in_window_samples | local | same | per-window sampling density |
scripts/run_campaign.py:1238:    post_window_sampling_dwell_s: float | None = None,
scripts/run_campaign.py:1257:    if post_window_sampling_dwell_s is not None:
scripts/run_campaign.py:1260:                "--post-window-sampling-dwell-s",
scripts/run_campaign.py:1261:                str(post_window_sampling_dwell_s),
scripts/run_campaign.py:5651:        sampling_plan = design.get("sampling_plan") if isinstance(design, dict) else None
scripts/run_campaign.py:5653:            sampling_plan.get("planned_n_blocks") if isinstance(sampling_plan, dict) else None
scripts/run_campaign.py:5763:def sampling_audit_for(analysis_manifest: AnalysisManifestState | None) -> dict[str, Any]:
scripts/run_campaign.py:5769:        sampling = design.get("sampling_plan") if isinstance(design, dict) else None
scripts/run_campaign.py:5770:        if isinstance(sampling, dict):
scripts/run_campaign.py:5772:                sampling.get("design")
scripts/run_campaign.py:5773:                if isinstance(sampling.get("design"), str)
scripts/run_campaign.py:5776:            value = sampling.get("planned_n_blocks")
scripts/run_campaign.py:5824:    sampling_audit: dict[str, Any],
scripts/run_campaign.py:5845:        "sampling_audit": sampling_audit,
scripts/run_campaign.py:5884:        sampling_audit=sampling_audit_for(analysis_manifest),
scripts/run_campaign.py:6114:                post_window_sampling_dwell_s=(
scripts/run_campaign.py:6115:                    policy_binding.policy.post_window_sampling_dwell_s
scripts/run_campaign.py:6319:                post_window_sampling_dwell_s=(
scripts/run_campaign.py:6320:                    policy_binding.policy.post_window_sampling_dwell_s
scripts/run_campaign.py:6843:                    sampling_audit=sampling_audit_for(state),
scripts/run_campaign.py:6938:                    sampling_audit=sampling_audit_for(analysis_manifest),
scripts/run_campaign.py:6997:                sampling_audit=sampling_audit_for(analysis_manifest),
scripts/run_campaign.py:7196:                post_window_sampling_dwell_s=(
scripts/run_campaign.py:7197:                    policy_binding.policy.post_window_sampling_dwell_s
scripts/run_campaign.py:7639:        sampling_audit = sampling_audit_for(analysis_manifest)
scripts/run_campaign.py:7680:            sampling_audit=sampling_audit,
docs/phase_2/detection_floor.md:86:  rail manifest, stack identity, sampling requested/observed, and the exact
docs/phase_2/detection_floor.md:219:| DF-RQ-GROSS-SHORT | `gross_energy_j` | gross request | short request profile used to expose request-window sampling edge cases | 10 | `floor_abs_j` |
docs/phase_2/detection_floor.md:345:- no quality flag, cooldown cap-hit pattern, sampling change, or manifest change
docs/phase_2/detection_floor.md:460:  condition, or from a bounded sampling/interpolation model if repetitions are
docs/phase_2/detection_floor.md:508:fallback and no resampling. Other physical backends emit
docs/phase_2/detection_floor.md:558:meter's calibration date/status, stated accuracy, resolution, sampling cadence,
docs/phase_2/detection_floor.md:606:meter/analyzer calibration date/status, stated accuracy, resolution, sampling
joulewise/gensuite/__init__.py:47:    """SHA-256 counter-mode DRBG with exact-uniform rejection sampling."""
docs/phase_2/suite_implementation_research.md:46:- The measured window is bounded by the `sampling_started`/`sampling_stopped` markers (D-026, `controller.py:401-458`, `bundle_read.py:267-296`). One sampling window per bundle; the suite's k items must all execute inside it, back-to-back (D-040: no per-item micro-cooldowns).
docs/phase_2/suite_implementation_research.md:47:- D-013: between `start_sampling` and `stop_sampling` the controller does nothing but block on the runtime. Therefore **the item loop cannot live in the controller** — it is runtime-side work behind a single adapter call, returning one `RuntimeResult` exactly as today.
docs/phase_2/suite_implementation_research.md:71:- Rejected alternative: a suite-aware `run_workload`. That would force every adapter (mock, mlx, vllm, llama_cpp, node client) to grow suite branching or fail mid-window; a separate capability method keeps every existing single-prompt path byte-compatible and lets the controller fail fast **before** sampling starts.
docs/phase_2/suite_implementation_research.md:218:   Tests: extend `tests/test_controller.py` — happy suite run end-to-end on mock (marker ordering vs `sampling_started/stopped` in flushed `events.jsonl`), `UNSUPPORTED_WORKLOAD` when the runtime lacks `run_suite`, FAILED with complete bundle on unreadable/invalid manifest, `run_experiment` with a suite profile ⇒ B bundles + manifest (D-040 shape).
docs/phase_2/suite_implementation_research.md:220:   Tests: extend `tests/test_reduce.py` — closed-form per-item/block/level energies on a synthetic trace; identifiability flag under sparse sampling; runtime_failed/malformed items appear with `energy_gross_j` but only in `status_counts` provenance; **golden test: reducing an existing single-prompt fixture bundle yields the previous summary plus `suite_metrics: null` and reducer_version bump, nothing else changed**; `_check_summary` still accepts old summaries.
docs/phase_2/suite_implementation_research.md:280:    def below(self, n):            # rejection sampling, exact-uniform, deterministic
docs/phase_2/suite_implementation_research.md:450:1. Pin the decoding/sampling policy explicitly. The harness (joulewise/adapters/mlx_runtime.py:174-179) calls mlx_lm.stream_generate with no sampler argument, i.e. greedy/temp-0 deterministic decoding. Under determinism the same item yields the identical response in every bundle, so cross-bundle pooling ('40-80 items/level for the gate statistics') is pseudo-replication: the effective n for all token/stop-reason/correctness statistics is the 8 distinct items per level; bundles replicate energy only. Rewrite section 3 accordingly (this is the scored-side mirror of the repo's own bundle-level-uncertainty rule).
docs/phase_2/suite_implementation_research.md:496:Pins: integers rendered base-10 ASCII unpadded in the hash message; NUL separators; UTF-8 seed bytes. **No rejection sampling of any kind** — any level-dependent rejection would break the core design invariant that the parameter distribution is *identical across levels* (only n_iter varies), which is what makes the envelope claim work. Modulo bias from `2^64 % 900` is ~5e-17 and level-identical; note it, ignore it. Fixed digit lengths (3/2/2/3) hold the prompt shape fixed. Expected answers are uniform-ish on [0, m−1] with an answer-length distribution identical across levels by construction.
scripts/validate_powermetrics_fiducial.py:341:        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
scripts/validate_powermetrics_fiducial.py:467:    sampling_started = clock.stamp()
scripts/validate_powermetrics_fiducial.py:468:    emit("sampling_started", {})
scripts/validate_powermetrics_fiducial.py:497:    # start, not from sampling-start (which precedes it by the baseline +
scripts/validate_powermetrics_fiducial.py:498:    # warmup + baseline preamble). Measuring elapsed against sampling_started
scripts/validate_powermetrics_fiducial.py:526:    sampling_stopped = clock.stamp()
scripts/validate_powermetrics_fiducial.py:527:    emit("sampling_stopped", {})
scripts/validate_powermetrics_fiducial.py:537:            "sampling_started": sampling_started,
scripts/validate_powermetrics_fiducial.py:538:            "sampling_stopped": sampling_stopped,
scripts/validate_powermetrics_fiducial.py:594:        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
scripts/validate_powermetrics_fiducial.py:608:            "sampling_interval_ms",
scripts/validate_powermetrics_fiducial.py:614:    finalization_state["capture_wall_time_s"] = str(sampling_started.epoch_s)
scripts/validate_powermetrics_fiducial.py:624:        capture_wall_time_s=sampling_started.epoch_s,
joulewise/uncertainty_evidence.py:32:    "sampling_started",
joulewise/uncertainty_evidence.py:33:    "sampling_stopped",
joulewise/uncertainty_evidence.py:206:    start = stamps["sampling_started"]
joulewise/uncertainty_evidence.py:207:    stop = stamps["sampling_stopped"]
joulewise/uncertainty_evidence.py:248:        "sampling_started_epoch_s": start.epoch_s,
joulewise/uncertainty_evidence.py:249:        "sampling_stopped_epoch_s": stop.epoch_s,
joulewise/uncertainty_evidence.py:463:    start = stamps["sampling_started"]
joulewise/uncertainty_evidence.py:464:    stop = stamps["sampling_stopped"]
joulewise/uncertainty_evidence.py:485:        "sampling_started_epoch_s": start.epoch_s,
joulewise/uncertainty_evidence.py:486:        "sampling_stopped_epoch_s": stop.epoch_s,
tests/test_cli_run.py:156:                    "--post-window-sampling-dwell-s",
tests/test_cli_run.py:162:            controller_run.call_args.kwargs["post_window_sampling_dwell_s"],
tests/test_cli_run.py:178:                    "--post-window-sampling-dwell-s",
tests/test_cli_run.py:1178:        config_data["sampling"] = {"power_hz": 2.0, "idle_seconds": 5.0}
tests/test_mock_adapters.py:74:        "sampling": {"power_hz": 2.0, "idle_seconds": 1.0},
tests/test_mock_adapters.py:596:        config = make_config(sampling={"idle_seconds": 30.0, "power_hz": 2.0})
tests/test_mock_adapters.py:602:        config = make_config(sampling={"idle_seconds": 0.25, "power_hz": 2.0})
tests/test_mock_adapters.py:606:    def test_stop_sampling_closed_form_short_window(self) -> None:
tests/test_mock_adapters.py:609:        self.assertTrue(self.telemetry.start_sampling(self.config).ok)
tests/test_mock_adapters.py:611:        samples = self.telemetry.stop_sampling(self.config)
tests/test_mock_adapters.py:620:    def test_stop_sampling_centered_grid_samples(self) -> None:
tests/test_mock_adapters.py:622:        self.telemetry.start_sampling(self.config)
tests/test_mock_adapters.py:624:        samples = self.telemetry.stop_sampling(self.config)
tests/test_mock_adapters.py:635:        self.assertTrue(telemetry.start_sampling(config).ok)
tests/test_mock_adapters.py:639:        samples = telemetry.stop_sampling(config)
tests/test_mock_adapters.py:654:    def test_stop_sampling_one_grid_candidate_falls_back_to_thirds(self) -> None:
tests/test_mock_adapters.py:658:        self.telemetry.start_sampling(self.config)
tests/test_mock_adapters.py:660:        samples = self.telemetry.stop_sampling(self.config)
tests/test_mock_adapters.py:667:    def test_stop_sampling_grid_end_boundary_excluded(self) -> None:
tests/test_mock_adapters.py:672:        self.telemetry.start_sampling(self.config)
tests/test_mock_adapters.py:674:        samples = self.telemetry.stop_sampling(self.config)
tests/test_mock_adapters.py:679:    def test_stop_sampling_two_grid_samples_no_fallback(self) -> None:
tests/test_mock_adapters.py:683:        self.telemetry.start_sampling(self.config)
tests/test_mock_adapters.py:685:        samples = self.telemetry.stop_sampling(self.config)
tests/test_mock_adapters.py:690:    def test_stop_sampling_zero_length_span_single_sample_degenerate(self) -> None:
tests/test_mock_adapters.py:695:        self.telemetry.start_sampling(self.config)
tests/test_mock_adapters.py:696:        samples = self.telemetry.stop_sampling(self.config)
tests/test_mock_adapters.py:700:    def test_stop_sampling_interior_invariants_across_durations_and_hz(self) -> None:
tests/test_mock_adapters.py:717:                config = make_config(sampling={"power_hz": power_hz})
tests/test_mock_adapters.py:718:                telemetry.start_sampling(config)
tests/test_mock_adapters.py:721:                samples = telemetry.stop_sampling(config)
tests/test_mock_adapters.py:731:    def test_stop_sampling_without_start_returns_empty(self) -> None:
tests/test_mock_adapters.py:732:        self.assertEqual(self.telemetry.stop_sampling(self.config), [])
tests/test_mock_adapters.py:734:    def test_stop_sampling_twice_second_call_returns_empty(self) -> None:
tests/test_mock_adapters.py:735:        self.telemetry.start_sampling(self.config)
tests/test_mock_adapters.py:737:        self.assertEqual(len(self.telemetry.stop_sampling(self.config)), 2)
tests/test_mock_adapters.py:738:        self.assertEqual(self.telemetry.stop_sampling(self.config), [])
tests/test_mock_adapters.py:740:    def test_restarted_sampling_stamps_from_new_span(self) -> None:
tests/test_mock_adapters.py:743:        self.telemetry.start_sampling(self.config)
tests/test_mock_adapters.py:745:        self.telemetry.stop_sampling(self.config)
tests/test_mock_adapters.py:748:        self.telemetry.start_sampling(self.config)
tests/test_mock_adapters.py:750:        samples = self.telemetry.stop_sampling(self.config)
tests/test_mock_adapters.py:755:    def test_start_sampling_telemetry_denied(self) -> None:
tests/test_mock_adapters.py:757:        result = self.telemetry.start_sampling(config)
tests/test_mock_adapters.py:783:        assert telemetry.start_sampling(config).ok
tests/test_mock_adapters.py:785:        samples = telemetry.stop_sampling(config)
tests/test_2k_amplification.py:168:            "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
tests/test_2k_amplification.py:278:                    "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
tests/test_2k_amplification.py:317:                    "query_fields": ["timestamp", "power.draw", "temperature.gpu"],
tests/test_2k_amplification.py:540:            fake = bin_dir / "nvidia-smi"
tests/test_2k_amplification.py:558:                task["operation"] = "start_sampling"
tests/test_2k_amplification.py:569:            self.assertIn("no numeric power.draw sample", status["message"])
tests/test_2k_amplification.py:570:            self.assertNotIn("nvidia-smi unavailable", status["message"])
joulewise/cli.py:273:    post_window_sampling_dwell_s = (
joulewise/cli.py:274:        args.post_window_sampling_dwell_s
joulewise/cli.py:279:        post_window_sampling_dwell_s is not None
joulewise/cli.py:280:        and post_window_sampling_dwell_s < 1.0
joulewise/cli.py:283:            "--post-window-sampling-dwell-s must be at least 1.0 for powermetrics"
joulewise/cli.py:329:        experiment_kwargs["post_window_sampling_dwell_s"] = (
joulewise/cli.py:330:            post_window_sampling_dwell_s
joulewise/cli.py:359:        post_window_sampling_dwell_s=post_window_sampling_dwell_s,
joulewise/cli.py:1274:        if event_type in {"sampling_started", "sampling_stopped"}:
joulewise/cli.py:1283:            ("sampling_started", "sampling_started_epoch_s"),
joulewise/cli.py:1284:            ("sampling_stopped", "sampling_stopped_epoch_s"),
joulewise/cli.py:1596:                and item.get("stage") == "telemetry.stop_sampling"
joulewise/cli.py:1602:            "strict: raw-to-trace: nvidia_smi telemetry.stop_sampling "
joulewise/cli.py:1608:            "metadata.adapters.telemetry.clock_alignments.stop_sampling.offset_estimate_s",
joulewise/cli.py:2123:        "--post-window-sampling-dwell-s",
joulewise/cli.py:2126:            "retain telemetry sampling for this many seconds after the measured "
tests/test_experiment.py:395:        duration_s = config.sampling.idle_seconds
tests/test_experiment.py:403:            sample_count=max(2, int(duration_s * config.sampling.power_hz)),
tests/test_experiment.py:408:    def start_sampling(self, config: BenchmarkConfig, context=None) -> AdapterResult:
tests/test_experiment.py:412:    def stop_sampling(self, config: BenchmarkConfig, context=None) -> list[PowerSample]:
tests/test_experiment.py:782:                self._clock.sleep(config.sampling.idle_seconds)
tests/test_experiment.py:786:                    duration_s=config.sampling.idle_seconds - (0.005 / 6.0),
tests/test_experiment.py:808:                self._clock.sleep(config.sampling.idle_seconds)
tests/test_experiment.py:1220:                if config.sampling.idle_seconds != policy.cooldown.subwindow_s:
scripts/generate_matrix.py:156:        "sampling": copy.deepcopy(base.get("sampling")),
scripts/generate_matrix.py:454:        frozen_n = manifest["design"]["sampling_plan"]["planned_n_blocks"]
scripts/generate_matrix.py:517:        planned_n_blocks = registry.value["sampling_plan"]["planned_n_blocks"]
tests/test_generate_matrix.py:96:    registry["sampling_plan"]["planned_n_blocks"] = planned_n_blocks
tests/test_generate_matrix.py:128:            self.assertEqual(manifest["design"]["sampling_plan"]["planned_n_blocks"], 10)
tests/test_analysis_engine.py:313:            "output policy": [replace_ratio(base[0], output_policy_b="sampling/temp=1"), base[1]],
tests/test_analysis_engine.py:410:                    "sampling_plan": {"planned_n_blocks": 2},
on a hosted runner; hardware adapters are validated by run bundles, not CI.
Two Python versions catch the realistic compat risks (3.11 floor vs 3.14
local) at trivial cost.

Consequences: `.github/workflows/ci.yml` added; Phase 2 Slice 2E adds the
mock end-to-end step to it; README badges optional, not required.

Revisit when: a self-hosted runner with GPU/Mac hardware ever materializes
(unlikely; not planned).

---

## D-018: Per-backend `power_w` definition and rail policy

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `power_trace.csv` has `power_w`, `source`, and optional `rail`
columns, but "power" means different physical boundaries on different
backends (SoC subsystems vs GPU board vs module input vs wall AC). Without a
fixed definition, cross-target comparisons silently compare different
quantities.

Options considered:

1. One `power_w` row per sample, backend decides what it means. Con: loses
   per-rail information; the meaning varies invisibly.
2. Per-rail rows only, reducers sum everything. Con: "everything" differs by
   backend; accidental double counting (e.g., a backend reporting both
   package and per-subsystem rails).
3. Per-rail rows preserved as reported, plus a per-backend *rail manifest*
   that names exactly which rails sum to the backend's canonical `power_w`
   for reduction, and a methodology table stating each backend's physical
   measurement boundary. powermetrics: cpu_power + gpu_power + ane_power
   (SoC subsystem proxy; excludes display, storage, PSU losses). nvidia-smi:
   board power as reported (GPU board only; excludes host). jetson_rails:
   VDD_IN preferred (module input) with the actually-used rail recorded.
   wall_meter: AC wall power (full system).

Decision: option 3.

Considerations: per-rail rows keep raw fidelity (Apple's per-subsystem split
is itself interesting data); the manifest makes the summation auditable and
fixable post hoc; the boundary table converts an implicit comparability
problem into an explicit, reportable limitation - cross-target absolute
comparisons must state boundaries, and wall-meter deltas (when the meter
exists, P1-003) calibrate the gap.

Consequences: telemetry adapters declare their rail manifest in
`device_metadata`; reducer sums per the manifest; methodology gains the
Measurement Boundaries section; the limitations section of the final report
inherits the boundary table.

Revisit when: a backend exposes a strictly better boundary (e.g., macOS adds
package-level wall-equivalent reporting).

---

## D-019: Mock adapters use simulated time via an injectable clock

prediction or quantified overhead discovery, never presented as a
surprise negative. Design should include at least one pairing/link cell
where the model PREDICTS a crossover, if any exists in the feasible set.

Consequences: `docs/phase_3/phase_3_plan.md` acceptance framing gets a
dated amendment pointing here; the AP row obligation rides the split-prep
queue row; Phase 4 claim wording inherits the thesis sentence.

Revisit when: the 2M-fitted Q4 model fails its own monolithic holdouts
(then the compositional prediction has no validated coefficients and the
sweep reverts to exploratory with that stated).

---

## D-049: Split transfer-energy boundary accounting on discrete-GPU ends

- Date: 2026-07-08
- Status: accepted (C-020; Codex-stack catch, repo-verified)
- Phase: 3

Context: on nvidia-smi-measured ends, board power EXCLUDES the host
CPU/NIC/DRAM work of moving KV bytes over TCP — so "transfer energy"
measured at a discrete-GPU end is near-zero by construction: a silent
undercount in unmeasured silicon, asymmetric across the pairing matrix
(Mac and Jetson boundaries include their NIC/host paths; dGPU boundaries
do not).

Options considered:

1. Ignore — report board-only numbers. Con: cross-pairing transfer
   comparisons silently broken; exactly the boundary sin (D-018) the
   project exists to avoid.
2. Wall-meter (or equivalent host-side measurement of) the GPU host on
   transfer legs so the transfer window has a host-inclusive boundary.
3. Explicitly scope dGPU transfer cells as board-only LOWER BOUNDS in
   the stage accounting, named per cell in the AP row and claim wording.

Decision: option 2 where the meter is available for the leg, option 3
otherwise — never option 1. The per-stage accounting schema must carry a
per-cell boundary label for the transfer stage; the seeded split AP row
(D-048) names which cells are host-inclusive vs board-only lower bounds;
cross-pairing transfer-energy comparisons are permitted only between
like-boundary cells or via the D-018 calibration bridge.

Consequences: split-prep queue row carries this; `docs/contracts/`
boundary docs get the transfer-stage label when the split schema lands
|---|---|---|
| novelty | **4** | Split case study is derivative *and* operationally irrelevant as configured; the cross-boundary budget idea is real but underdeveloped. |
| feasibility | **2** | Two hardware gates never closed, no llama.cpp adapter, no cross-device fiducial exists, meter not owned, laptop AC boundary is battery-buffered. |
| mvp_leverage | **3** | High method reuse (§§3-5), near-zero data reuse — by its own admission. |
| venue_fit | **4** | ICPE full track will reject one unsizable replay pairing; WIP/workshop plausible for the metrology remnant only. |
| original_goals | **9** | This *is* the split axis, honestly scoped, honestly silent on spec-decode/MTP/MoE/KDA. Real credit here. |

## Fatal flaws

**F1 — The joint error budget is not constructible, and the proposal's own arithmetic understates it by
~10x.** The Mac term is known: ~1 J per phase member, 30 ms edge x 33 W (`docs/paper/draft-v1.md:84`).
The GPU term is *unknown by the project's own admission*: `docs/JouleWise_Hardening_Proposal.md:453`
lists "nvidia-smi cadence and averaging characterization" as an unexecuted Phase-7 promotion item, and
`joulewise/adapters/nvidia_smi.py:401-402` computes `interval_ms = 1000/power_hz` — i.e. the harness
*assumes the requested poll rate is the instrument cadence*. That is precisely the class of assumption
D-078 was created to destroy on the Mac. NVML board power on consumer Ampere is a filtered average whose
internal update period is not the poll period; at a 350 W board, a 100 ms edge is ~35 J and a 1 s edge is
~350 J. Four stages x two edges. Against effects the proposal itself sizes at 10-200 J, **the budget is
plausibly larger than every claimable quantity in the paper.** The proposal spots this ("a 100 ms
uncertain edge on a high-power PC can be tens of joules") and then does not act on it: no composite bar
is stated, S2/S3 are unchanged, and contribution 2 still promises transfer floors. A referee reads that
as knowing the study is unsizable and submitting anyway.

**F1b — There is no cross-device fiducial, so the method's core does not transport.** The project's
distinguishing move is an *in-window physical* pulse-train fiducial (`joulewise/powermetrics_fiducial.py`,
`calibration_bracketing.py`). It is intrinsically within-machine: you cannot inject a Mac power pulse and
observe it on a 3080 Ti. The proposal substitutes an ordinary software clock bound ("both clocks produce a
prospective bound smaller than 25% of the shortest claimed interval") while retaining D-078's rhetoric of
calibration. The only shared physical channel that could bracket both clocks is the wall meter — borrowed,
single, 100 ms-cadenced. **This is the deepest flaw: the paper inherits the vocabulary of the calibrated
instrument without its mechanism.**

**F2 — Both endpoint boundaries structurally exclude the quantity the paper is about, and the repo already
ruled on it.** D-049 (`docs/decision_log.md:2673`): on nvidia-smi ends, board power excludes host
CPU/NIC/DRAM, so "transfer energy measured at a discrete-GPU end is near-zero by construction." D-018:
powermetrics = cpu+gpu+ane, an SoC subsystem proxy excluding display/storage/PSU. An M3 Max MacBook Pro
has no Ethernet port — the 1GbE/2.5GbE link runs through a Thunderbolt/USB-C adapter drawing outside the
SoC rails. So sender NIC energy is outside the Mac boundary and receiver host/NIC energy is outside the
GPU boundary: **transfer energy, the load-bearing new quantity, is unmeasurable at both endpoints.**
D-049 already picked the remedy (wall meter, or explicit board-only lower bounds). The proposal takes the
wall meter, which lands it in F3.

**F3 — The wall-meter plan is internally contradictory and physically unsound for a laptop.**
(i) *Contradiction:* one meter on a shared strip cannot mint "sender, receiver, combined-wall and
composite" floors (contribution 2). Sender and receiver wall floors require two meters. Unrepaired.
(ii) *Battery buffer:* a MacBook Pro at the AC boundary is charge-buffered; macOS charges
opportunistically, so second-scale AC draw is decoupled from SoC power. MLPerf Power's battery rule is
quoted in this project's own draft (`draft-v1.md:26,182`) — and the proposal violates it without mention.
First-page referee kill. (iii) *Baseline swamping:* the "unused reference node remains powered and idle"
adds ~60-100 W of PSU-inclusive idle to the combined boundary, with nonlinear efficiency in load, against
10-200 J effects; the WT310E's 0.1% rdg + 0.1% rng at a ~400 W range is ~0.4 W of systematic error, i.e.
~12 J over a 30 s composite window — comparable to the effect. The proposal says the meter spec "must
enter the floor calculation" and never does the arithmetic. (iv) *Standing decision:* D-092 ratified the
meter but recorded **no hardware, C8 conditional, "not assumed by any campaign plan."** The proposal's
headline assumes it.

**F4 — Existing-material compliance is rhetorical.** MLX prompt-cache state is not portable to CUDA;
D-015's hard rule forces same-runtime both ends, which means llama.cpp/GGUF. The repo has
`adapters/{mlx_runtime,vllm_runtime,mock_*}.py` and **no llama.cpp adapter**. So the paper needs a new
runtime adapter, a new artifact/quantization lineage (not the pinned MLX 4-bit Qwen2.5 rev `8b40312`),
re-run determinism/output-identity machinery, and — because floors are stack-specific — **a full floor
re-mint under a runtime that has never been calibrated.** The proposal concedes it in its last section
("D-117 MLX results are *not* direct monolithic comparators for a llama.cpp split stack"), which
contradicts its own claim two paragraphs earlier that it "reuses all three D-117 datasets as the validated
one-boundary baseline." Under Ed's binding constraint this proposal reuses §§3-5 prose and **zero data**.
That is permissible only if stated plainly; it states the opposite.

**F5 — Schedule is off by a large factor, on the project's own record.** Three 2-4 h windows + a pilot +
a contingency, to stand up a *second, harder* instrument. Cost of the first: P0 instrument repair =
nine adversarial confirmation rounds and PR #79; D-078 through D-117 = ~4 months; and `CLAIMS_STATUS.md`
§1 today reads **"VALID — NONE at this checkpoint."** Zero citable numbers exist. Meanwhile the
- Extract stable interfaces only after live NVIDIA behavior is observed.

#### Acceptance gate G2

- CI installs the built package on every supported Python version.
- Strict mock E2E runs in CI.
- macOS dependency/import and captured-fixture jobs pass.
- Lint is clean.
- Coverage is measured and published; any threshold is based on the observed baseline rather than chosen arbitrarily.
- No interpretation rule is implemented independently in more than one consumer without a parity test.

### Phase 3 — Production-shaped Mac shakedown

**Objective:** Demonstrate that a real run naturally emits all evidence required by the current reducer and claim gates, without injecting synthetic metadata afterward.

#### Preflight command

Add a read-only `joulewise doctor` or equivalent preflight that reports:

- Supported macOS and architecture.
- Python and package versions.
- MLX/MLX-LM/transformers versions.
- Model path and artifact hash status.
- Tokenizer identity status.
- powermetrics availability and privilege status.
- Available sampler fields.
- External evidence destination and free space.
- Background-load/quiet-machine warnings.
- Current thermal pressure.
- Config/schema compatibility.

The preflight must never alter sudoers configuration automatically.

#### Timing and sampling hardening

- Define whether each powermetrics value represents a preceding interval, a following interval, or a point estimate.
- Preserve the raw interval duration and anchor evidence.
- Run a controlled load-transition experiment to estimate marker-to-sample alignment.
- Record a conservative alignment bound when the exact phase is not identifiable.
- Refuse phase/item claims when window duration, cadence ratio, or alignment bound is inadequate.
- Retain request-level evidence even when short phase attribution is refused.

#### Controller-overhead hardening

- Measure the cost of per-token event construction using an ABBA or equivalent design.
- Compare the standard capture path with a minimal-marker or buffered-token path while preserving generated outputs.
- Treat any difference above the floor as harness overhead and either subtract through a justified model or scope claims to the instrumented stack.

#### Idle and thermal hardening

- Estimate idle uncertainty from independent idle windows or block means, not raw adjacent samples treated as independent observations.
- Quantify autocorrelation and derive an effective sample count if raw-sample intervals are retained.
- Calibrate the idle-drift guard from pre/post windows.
- Verify that positive `warmup_seconds` and the cooldown gate produce stable starting states.
- Record ambient conditions and thermal-pressure state consistently.

#### Acceptance gate G3

A production-shaped Mac run must:

- Pass strict validation.
- Populate clock/alignment, interpolation, idle-drift, cooldown, stack-identity, token, and output-policy evidence naturally.
- Produce metric-specific eligibility: gross request, idle-subtracted request, and short phase/item windows may legitimately differ.
- Be reducible byte-stably from its published raw evidence.
- Produce no synthetic or manually patched uncertainty fields.

### Phase 4 — Detection-floor and boundary calibration

**Objective:** Turn the existing prospective floor machinery into a real, versioned calibration artifact with a known physical scope.

#### Detection-floor campaign

- Freeze the calibration config, order, model artifact, output policy, environment, and sample size before collection.
- Run absolute-repeatability cells and ABBA null-comparison blocks.
- Generate the floor artifact from bundle identities and verify every source hash.
- Exercise the transport/refusal rules against intentionally mismatched stacks, durations, power envelopes, and cadence.
- Record the floor as an operational false-effect guard, not a population tolerance guarantee.

#### Wall or PD bridge

Where feasible, add an external whole-system meter or USB-C PD meter for controlled steady loads and representative inference loads.

The objective is not to force powermetrics rails to equal wall energy. It is to estimate:

- Offset and load-dependent differences.
- Stability of the mapping across workload regimes.
- Whether relative within-stack rankings survive the boundary change.
- Which claim language remains allowed without the bridge.

If no suitable meter is available, retain L1 rail-bound results and same-boundary L2 comparisons only. Do not delay the entire capstone for unattainable whole-system calibration.

docs/milestones.md:15:| 3080 Ti borrow window | TBD | R-006; needed during Phase 3 Stage 3.4 |
docs/milestones.md:35:| 1: Approval, feasibility, measurement design | supervisor + device access | local auth session CLOSED 2026-07-06; lab answers | TBD |
docs/milestones.md:36:| 2: Harness + Mac slice + baselines | Phase 1 readiness gate | Mac sessions; remote-node access | TBD |
docs/milestones.md:43:- Hardware-gated work is scheduled around access windows; desk work
docs/risk_register.md:14:- Owner: `user` for actions needing human/lab/supervisor access, `agent` for
docs/risk_register.md:26:| R-006 | 3080 Ti borrow window slips or shrinks | 3 | medium | medium | open |
docs/risk_register.md:28:| R-008 | Orin telemetry inaccessible | 2-3 | medium | low | open |
docs/risk_register.md:131:## R-006: 3080 Ti borrow window slips or shrinks
docs/risk_register.md:159:## R-008: Orin telemetry inaccessible
docs/risk_register.md:163:- Trigger: P1-006 evidence shows neither INA3221 sysfs nor tegrastats usable.
docs/risk_register.md:168:- Owner: user (access), agent (adapter).
docs/risk_register.md:189:- Owner: user (device access), agent (verdict documentation - done).
docs/risk_register.md:197:- Trigger (residual): SSH-controlled comparison runs (once transport exists)
docs/risk_register.md:282:  re-collection needs access windows that may not recur).
TASK_QUEUE.md:89:- **[ED-EXTERNAL]** — needs the user: advisor, calendar, device access,
TASK_QUEUE.md:107:| NVIDIA-RETENTION-FLAKE-01 | P2 Next Slice | 2026-08-03 | Fix the test-isolation/load-sensitivity defect in tests/test_nvidia_node_integration.py (RuntimeError: retention record disappeared under suite ordering) | Root-caused to the fixed shared `DEFAULT_RETENTION_ROOT`; closed test-side (node_client.py untouched) via hermetic per-test retention roots + a registry-clients-do-not-share-manifest regression; assertions preserved (re-indented); 20x interleaved stress zero retention-disappearance failures; lead suite `Ran 2437 OK (skipped=82)`; merged via PR #97 (`a32977e`) with green CI 5/5 under D-072. The production DEFAULT_RETENTION_ROOT hardening (concurrent-client collision vs next-session reclamation) is deferred as `NODE-CUSTODY-DEFAULT-01` (non-blocking) |
TASK_QUEUE.md:200:- D-013 SSH-controlled vs co-resident controller comparison — SHELF,
TASK_QUEUE.md:230:- Do not schedule the 3080 Ti borrow window before Stage 3.0 verdicts and the
TASK_QUEUE.md:304:| LITREAD-VERIFY-01 | P4 Polish | [AGENT] | Pre-submission verbatim re-verification of the two load-bearing related-work sources against the **PDFs of record**: TokenPowerBench (arXiv **2512.03024**) and "The Illusion of Power Capping in LLM Decode" (arXiv **2605.11999**). Both were read in full text during the sweep, but through WebFetch's extraction model against the arXiv HTML renders. | Every quote and number cited in a submission re-checked against the PDF. **Note the id correction:** TokenPowerBench is 2512.03024; 2605.11999 is the Illusion paper — earlier handoff text conflated the two. | [Sweep-techniques access summary](docs/run_reports/2026-07-30-sweep-techniques.md) |
TASK_QUEUE.md:329:| E6 | P1-006 | P1 Phase Gate | READY [ED-EXTERNAL] | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |
TASK_QUEUE.md:357:| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 [AGENT] | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
TASK_QUEUE.md:358:| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) [AGENT] | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
TASK_QUEUE.md:371:| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED [AGENT] | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
TASK_QUEUE.md:372:| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED [AGENT] | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
TASK_QUEUE.md:373:| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED [AGENT] | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
TASK_QUEUE.md:379:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
TASK_QUEUE.md:380:| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY [AGENT] | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
TASK_QUEUE.md:397:| E6 | P1-006 | P1 Phase Gate | READY | Confirm NVIDIA/Orin telemetry access paths: SSH/runtime/telemetry command evidence, or marked pending with blocker (gates slices 2K/2L). | Instrumentation section of the Phase 1 exit checklist filled or blocker recorded. Evidence: SSH/runtime/telemetry command evidence in the exit checklist; Or an explicit pending-with-blocker record. Authority: [Remote gate / NV-GATE-2](docs/phase_2/hardware_slice_implementation_guide.md). Acceptance: [Phase 1 exit checklist](docs/phase_1/phase_1_exit_checklist.md). |
TASK_QUEUE.md:435:| A23 | P2-005 | P2 Next Slice | PARTIAL; READY; GATES live_promotion: P1-006 | Remote targets (2K NVIDIA/vLLM/ssh and 2L Orin): fixture-first and NV-GATE-2 code-now hardening are merged; protocol pins remain provisional until the external live-promotion rows execute. | Live 2K/2L evidence or a documented access blocker; applicability table updated; NV-GATE-2 live rows close without promoting fixture evidence. Evidence: Remote bundle or documented access blocker; Applicability table updated; NV-GATE-2 items closed at live promotion. Authority: [NV-GATE-2 live-promotion spec](docs/specs/c027/nv-gate-2_live_promotion.md). Acceptance: [2K live verification checklist](docs/phase_1/2k_live_verification_checklist.md). Note: PR #49 merged the code-now verifier, streaming, cleanup, and localhost gates; P1-006 and device execution remain open. |
TASK_QUEUE.md:436:| A24 | P2-016 | P2 Next Slice | BLOCKED — P2-006 (the 2M corpus exists) | Critique-adjudicated queue batch (umbrella a..i): post-2M controller split; node-worker protocol parity tests; NVIDIA skip counts into measurement quality; per-backend raw-to-trace strict generalization; claims-to-evidence index post-2M; schema v0.2 loader/export parity; boundary labels in report index; summary_provenance strict key; token_count_source naming alignment. | Each item lands with its named gate; dispositions plus rejected items recorded in C-011. Evidence: Each subitem lands with its named gate; Dispositions recorded in C-011. Authority: [C-011 ledger + C-027 (post-2M umbrella)](docs/reviews/2026-07-09-c027-whole-project-review.md). Acceptance: [P2-016 acceptance](docs/process/state_kernel.json). Note: Stage 1 conservatively blocks the parent; a later owning session may split P2-016a..i through normal intake. |
TASK_QUEUE.md:449:| A40 | AUD-WO-037 | P3 Hardening Candidates | READY; GATES live_promotion: 2K-LIVE-PROMOTION-SCHEDULED | Fold non-self-asserted promotion authority into the 2K-live P2-005 and NV-GATE-2 code-now path before live promotion: bind an implementation receipt to commit and protocol pins and derive per-bundle execution class from the transport path. | Before 2K live promotion, non-self-asserted implementation authority and transport-derived execution classification fail closed at claim admission. Evidence: Fixture, unknown, unpromoted-live, and promoted-live classifications are tested; Unknown and unpromoted NVIDIA bundles are refused at claim admission; Promotion receipt is commit and protocol bound and cannot be forged through config or metadata. Authority: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-037](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Land this before, never after, the first claim-bearing NVIDIA live promotion; do not execute NV-GATE-2 or de-provisionalize hardware results here (Comprehensive-audit register WO-037 non-goals). Note: D-043 supersession closure falls due at landing: add the dated D-057 governed-reason amendment identified by PA-2. |
TASK_QUEUE.md:450:| A41 | AUD-WO-038 | P3 Hardening Candidates | READY; GATES close: 2K-LIVE-REMOTE-MULTINODE-DECIDED | At the 2K-live or remote multi-node roadmap decision, choose one owned remote execution boundary, consolidate duplicated lifecycle evidence helpers, and remove only proven-unconsumed transport surface with compatibility disposition. | At the 2K-live or remote multi-node decision, one owned execution boundary replaces only proven duplication while node-worker safeguards and public compatibility remain intact. Evidence: Lifecycle parity covers node-worker, subprocess, SSH, interface, and controller failure paths; Every deleted surface has a bounded absence or deprecation-compatibility trace; node_worker remains self-contained with backend-specific timeout, identity, log, clock, and cleanup safeguards. Authority: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-038](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Re-baseline against WO-001 and WO-010, keep node_worker self-contained, and do not delete public transport methods on repository absence alone (Comprehensive-audit register WO-038 risk boundaries). Note: D-043 supersession closure falls due at landing: back-annotate the public adapter and transport contract as required by PA-2. |
TASK_QUEUE.md:451:| A42 | AUD-WO-039 | P3 Hardening Candidates | PARTIAL; READY; GATES close: SITE-CAPACITY-RIGHTSIZING-DECIDED | At the next explicit site-capacity or right-sizing decision after SITE-02, remove only proven-unused live payload fields and make any further page trim through a recorded retained-route and value-versus-bytes review. | The remaining site payload and right-sizing work removes only proven-unused live fields and any page removal follows an explicit value-versus-bytes retention review. Evidence: Packed-byte and request reduction is measured; Route and link checks pass and every removed page has a retention decision; Consumed views, deep links, source access, and provenance stamps remain intact. Authority: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Acceptance: [Comprehensive-audit register WO-039](docs/reviews/2026-07-13-comprehensive-audit/register.jsonl). Fence: Trim only live payload fields proven unused; preserve advisor-facing pages, navigation, source access, stable deep links, and provenance unless a per-page retention review says otherwise (Comprehensive-audit register WO-039 preservation boundary). Note: Partial page trim landed 2026-07-15 by redirecting the duplicative capsule task-queue mirror while preserving its routes; remaining payload work is open. D-043 supersession closure falls due at landing through the dated D-051 amendment identified by PA-2. |
TASK_QUEUE.md:457:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
TASK_QUEUE.md:458:| A51 | NODE-CUSTODY-DEFAULT-01 | P3 Hardening Candidates | READY | Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted. | Harden the production DEFAULT_RETENTION_ROOT against concurrent-client collision while preserving next-session custody reclamation (the NEEDS_RULING tradeoff deferred from NVIDIA-RETENTION-FLAKE-01). Evidence: The production DEFAULT_RETENTION_ROOT no longer collides for genuinely concurrent NodeClients sharing a scope, without breaking next-session custody reclamation (a later process must still locate the manifest it is entitled to reclaim); A regression proves two default-constructed clients in one process do not clobber each other AND that the documented reclamation contract still resolves the correct manifest across process boundaries; No retention/custody assertion is weakened; only root selection changes. Authority: [NVIDIA-RETENTION-FLAKE-01 fix report F1/F3 (PR #97): unique default roots close concurrent collision but conflict with next-session reclamation](docs/run_reports/2026-08-03-desk-session.md). Acceptance: [NODE-CUSTODY-DEFAULT-01 acceptance](docs/process/state_kernel.json). Fence: Isolation-only: do not weaken any retention/custody assertion; the reclamation contract's cross-process manifest resolution must survive any default-root change (NVIDIA-RETENTION-FLAKE-01 test-side fix (PR #97) already closed the flake). Note: Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario). |
docs/phase_2/splitwise_decode_campaign.md:180:- No network access is required or permitted during the window; the snapshot is
docs/phase_2/splitwise_decode_campaign.md:338:and revision-correct, because the window forbids network access and a missing
docs/phase_1/phase_1_exit_checklist.md:34:- NVIDIA/Orin access evidence (Step 6).
docs/phase_1/phase_1_exit_checklist.md:60:| NVIDIA telemetry permissions | pending | SSH access, `nvidia-smi` path, power-query support, sample command output | Instrumentation section below |
docs/phase_1/phase_1_exit_checklist.md:61:| Orin telemetry permissions | pending | SSH access, selected telemetry source, sample command output, wall-meter fallback | Instrumentation section below |
docs/phase_1/phase_1_exit_checklist.md:62:| Pi/Hailo telemetry permissions | pending | SSH access, wall-meter path, Hailo runtime verdict | Instrumentation + Hailo sections below |
docs/phase_1/phase_1_exit_checklist.md:64:| Phase 2 readiness | complete (2026-06-12) | Review confirming mock-first Phase 2 can begin without hardware access | Readiness section below |
docs/phase_1/phase_1_exit_checklist.md:96:- Does the supported operator set cover attention and KV-cache access
docs/phase_1/phase_1_exit_checklist.md:141:attention only, no KV-cache access pattern; no token-by-token decode
docs/phase_1/phase_1_exit_checklist.md:207:- Linux: `ethtool <interface>` (pending Linux node access).
docs/phase_1/phase_1_exit_checklist.md:249:fail cleanly. Phase 1 records *access* evidence here; Phase 2's
docs/phase_1/phase_1_exit_checklist.md:329:### NVIDIA 3050
docs/phase_1/phase_1_exit_checklist.md:333:- Status: pending device access. Controller-side note from 2026-06-09:
docs/phase_1/phase_1_exit_checklist.md:335:  and must be checked on the NVIDIA node itself.
docs/phase_1/phase_1_exit_checklist.md:337:  - [ ] SSH access.
docs/phase_1/phase_1_exit_checklist.md:345:### NVIDIA 3080 Ti (borrow)
docs/phase_1/phase_1_exit_checklist.md:357:- Status: pending device access.
docs/phase_1/phase_1_exit_checklist.md:359:  - [ ] SSH access.
docs/phase_1/phase_1_exit_checklist.md:361:  - [ ] Rail telemetry accessible (sysfs paths or tegrastats output
docs/phase_1/phase_1_exit_checklist.md:371:  - [ ] SSH access.
docs/phase_1/phase_1_exit_checklist.md:391:NVIDIA/vLLM integration, Hailo work, or report-generator polish - those
docs/phase_1/phase_1_exit_checklist.md:411:P1-006, D-016) and are untouched by this verdict. Phase 1 itself stays
docs/phase_2/phase_2_plan.md:20:targets as Phase 1 access evidence permits - and homogeneous baselines exist
docs/phase_2/phase_2_plan.md:51:  2G MLX runtime    2H powermetrics telemetry      2K vLLM + nvidia-smi (gated: P1-006)
docs/phase_2/phase_2_plan.md:52:  (gated: D-016,    (gated: privileged sample      2L Orin (gated: P1-006)
docs/phase_2/phase_2_plan.md:606:## Slice 2K: NVIDIA/vLLM + nvidia-smi + SSH Transport
docs/phase_2/phase_2_plan.md:609:the SSH transport.
docs/phase_2/phase_2_plan.md:611:Gates: P1-006 evidence (SSH reachable, `nvidia-smi` power queries work,
docs/phase_2/phase_2_plan.md:614:Design and implementation detail (SSH transport, the remote-runner
docs/phase_2/phase_2_plan.md:620:checklist NVIDIA rows (access evidence) and the Phase 2 applicability
docs/phase_2/phase_2_plan.md:635:Gates: P1-006 Orin evidence (SSH, runtime choice, telemetry mechanism).
docs/phase_2/phase_2_plan.md:807:required-if-access-evidence-exists, otherwise their gate evidence documents
docs/phase_1/phase_1_plan.md:51:- NVIDIA/Orin access evidence.
docs/phase_1/phase_1_plan.md:190:Inputs: Pi 5 + Hailo-8L access; Hailo toolchain and docs; a candidate
docs/phase_1/phase_1_plan.md:194:against attention/KV access patterns; attempt one minimal LLM-shaped
docs/phase_1/phase_1_plan.md:207:Fallback: if device access is unavailable, keep `pending` and record
docs/phase_1/phase_1_plan.md:208:exactly what access is missing.
docs/phase_1/phase_1_plan.md:210:### Step 6: Remote NVIDIA/Orin Evidence (queue P1-006)
docs/phase_1/phase_1_plan.md:217:Inputs: SSH access details; the 3050 machine; Orin Nano; 3080 Ti borrow
docs/phase_1/phase_1_plan.md:220:Actions: per target record - SSH reachability; runtime availability or
docs/phase_1/phase_1_plan.md:223:INA3221 sysfs paths or `tegrastats`); memory limits; for the 3080 Ti, the
docs/phase_1/phase_1_plan.md:231:Fallback: mark pending with the missing access named; Phase 2 proceeds
docs/phase_1/2k_live_verification_checklist.md:5:Use for the first live NVIDIA/vLLM + nvidia-smi + SSH contact. Record command
docs/phase_1/2k_live_verification_checklist.md:9:## 1. SSH/SCP Transport
docs/phase_1/2k_live_verification_checklist.md:11:1. Confirm OpenSSH alias/auth outside JouleWise:
docs/phase_1/2k_live_verification_checklist.md:25:   destination for SSH and before operands for SCP.
docs/phase_2/splitwise_replication_roadmap.md:19:   binding cross-target cap at 12 GiB (3080 Ti) — 7B INT4 fits, 14B is
docs/phase_2/splitwise_replication_roadmap.md:103:Unlock conditions (all): P1-006 operational 3080 Ti lane (SSH, CUDA,
docs/phase_2/splitwise_replication_roadmap.md:109:pre-registered AP-1 compositional predictions. Mac SoC rails and NVIDIA
docs/phase_2/phase_2_exit_checklist.md:5:their primary evidence or with a documented blocker that names what access
docs/phase_2/phase_2_exit_checklist.md:26:| 2K NVIDIA/vLLM/ssh | conditional (gate: P1-006 NVIDIA evidence) | pending live promotion; CODE-NOW NV-GATE-2 units, accepted-findings round, and idle-readiness regression fix implemented 2026-07-10 on `impl/nvgate2-codenow`; socket-capable localhost 3x lead rerun remains open | remote bundle from 3050, or documented access blocker | CODE-NOW evidence `docs/run_reports/2026-07-10-nvgate2-codenow.md`; fix evidence `docs/run_reports/2026-07-10-nvgate2-fix-round.md` and `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`; live rows 16–20 and PROVISIONAL-pin exit remain open; applicability table + spec in `hardware_slice_implementation_guide.md` |
docs/phase_2/phase_2_exit_checklist.md:27:| 2L Orin adapter | conditional (gate: P1-006 Orin evidence) | pending | bundle from Orin, or documented blocker | run report + applicability table below; spec in `hardware_slice_implementation_guide.md` |
docs/phase_2/window_c_operator_checklist.md:195:- [ ] **PASS — cloud-sync custody is safe.** If `bird` is absent, record absence. If present, record PID plus process start time, verify state `T` twice, hold its launchers as prescribed, install a fail-safe `CONT` trap, and do not access Mobile Documents while it is stopped.  
docs/phase_2/hardware_slice_implementation_guide.md:186:## Slice 2K: NVIDIA/vLLM + nvidia-smi + SSH Transport
docs/phase_2/hardware_slice_implementation_guide.md:209:- **SSH transport** (`name = "ssh"`): wrap `ssh`/`scp` subprocesses (no
docs/phase_2/hardware_slice_implementation_guide.md:225:nvidia-smi; runner-script arg handling. Real-node smoke when P1-006 evidence
docs/phase_2/hardware_slice_implementation_guide.md:267:5. **2K** (first remote target) when P1-006 NVIDIA evidence exists, then
docs/phase_2/suite_implementation_research.md:49:- `phase_windows()` pairs only `phase_start`/`phase_end` and `token_timestamps()` selects only `token`/`decode` events, so new event types are invisible to every existing accessor: per-item `prefill`/`decode` phase events from suite items will simply sum into `phase_energy_j` (multiple intervals per phase are already supported — documented, intended).
docs/phase_2/suite_implementation_research.md:98:Mirror `phase_windows()` — tolerant pairing in accessors, strictness in validation:
docs/phase_2/suite_implementation_research.md:335:**1) Algorithm sketch.** Generate a synthetic Python module via a small grammar, then ask for a completion. From the DRBG: (a) identifiers = snake_case compounds of seed-drawn syllables + a domain-noun bank (`batch_ledger_totals`, `parse_route_manifest`) — invented, license-clean, and importantly they fragment into multiple subwords like real code identifiers do; (b) module skeleton: 2–3 import lines (stdlib names only), a module docstring, 2 complete small functions (loops, dict access, f-strings, early returns — emitted from statement templates with type-consistent slots so the code is syntactically valid Python), 1 function signature + docstring + `# TODO: implement` stub; (c) prologue instruction: "Complete the final function in this module. Return only code."; (d) epilogue = the stub signature + docstring (must survive so the completion target is intact).

exec
/bin/zsh -lc "sed -n '280,330p' docs/JouleWise_Hardening_Proposal.md; sed -n '186,235p' docs/phase_2/hardware_slice_implementation_guide.md; sed -n '329,366p' docs/phase_1/phase_1_exit_checklist.md; sed -n '95,120p' docs/phase_2/splitwise_replication_roadmap.md; sed -n '940,980p' docs/decision_log.md; sed -n '2670,2695p' docs/decision_log.md; rg -n \"NVIDIA-PORTABILITY-01|NVML counter|pulse anchor|rate-aware|averaging|counter-mechanics\" docs/run_reports/2026-08-01-desk-adjudication-session.md docs/process/state_kernel.json .desk 2>/dev/null | head -n 200" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:

The preflight must never alter sudoers configuration automatically.

#### Timing and sampling hardening

- Define whether each powermetrics value represents a preceding interval, a following interval, or a point estimate.
- Preserve the raw interval duration and anchor evidence.
- Run a controlled load-transition experiment to estimate marker-to-sample alignment.
- Record a conservative alignment bound when the exact phase is not identifiable.
- Refuse phase/item claims when window duration, cadence ratio, or alignment bound is inadequate.
- Retain request-level evidence even when short phase attribution is refused.

#### Controller-overhead hardening

- Measure the cost of per-token event construction using an ABBA or equivalent design.
- Compare the standard capture path with a minimal-marker or buffered-token path while preserving generated outputs.
- Treat any difference above the floor as harness overhead and either subtract through a justified model or scope claims to the instrumented stack.

#### Idle and thermal hardening

- Estimate idle uncertainty from independent idle windows or block means, not raw adjacent samples treated as independent observations.
- Quantify autocorrelation and derive an effective sample count if raw-sample intervals are retained.
- Calibrate the idle-drift guard from pre/post windows.
- Verify that positive `warmup_seconds` and the cooldown gate produce stable starting states.
- Record ambient conditions and thermal-pressure state consistently.

#### Acceptance gate G3

A production-shaped Mac run must:

- Pass strict validation.
- Populate clock/alignment, interpolation, idle-drift, cooldown, stack-identity, token, and output-policy evidence naturally.
- Produce metric-specific eligibility: gross request, idle-subtracted request, and short phase/item windows may legitimately differ.
- Be reducible byte-stably from its published raw evidence.
- Produce no synthetic or manually patched uncertainty fields.

### Phase 4 — Detection-floor and boundary calibration

**Objective:** Turn the existing prospective floor machinery into a real, versioned calibration artifact with a known physical scope.

#### Detection-floor campaign

- Freeze the calibration config, order, model artifact, output policy, environment, and sample size before collection.
- Run absolute-repeatability cells and ABBA null-comparison blocks.
- Generate the floor artifact from bundle identities and verify every source hash.
- Exercise the transport/refusal rules against intentionally mismatched stacks, durations, power envelopes, and cadence.
- Record the floor as an operational false-effect guard, not a population tolerance guarantee.

#### Wall or PD bridge

Where feasible, add an external whole-system meter or USB-C PD meter for controlled steady loads and representative inference loads.
## Slice 2K: NVIDIA/vLLM + nvidia-smi + SSH Transport

**Gate, acceptance, fallback:** `phase_2_plan.md` Slice 2K. Do not start
on assumption.

**New files:** `joulewise/adapters/ssh_transport.py`,
`joulewise/adapters/vllm_runtime.py`, `joulewise/adapters/nvidia_smi.py`, a
self-contained remote runner script (shipped to the node), and matching
tests. **Touch:** the registry (`ssh` transport, `vllm` runtime, `nvidia_smi`
telemetry branches).

**Design center - the node worker protocol:** the transport-independent
contract lives in `docs/contracts/node_worker_protocol.md` (conceptual
shape + the requirements checklist the wire format must satisfy — read
it first; pin the wire-level details into it as you implement). In
short: ship a self-contained runner script to the node, run it with a
JSON task file, collect an artifacts dir (events JSON, output text,
token timeline, runner log, status) back into the bundle. The runner
depends only on the remote env (vLLM); the `joulewise` package is
**not** installed remotely.

**Pinned pieces:**

- **SSH transport** (`name = "ssh"`): wrap `ssh`/`scp` subprocesses (no
  paramiko, D-009); `run_command` with timeout + structured
  `transport_unavailable` on unreachable host; `collect_artifact` via `scp`;
  `connection_metadata` records host, user, and round-trip marker timing
  (D-003 clock-offset bound).
- **nvidia-smi telemetry** (`name = "nvidia_smi"`): remote
  `nvidia-smi --query-gpu=timestamp,power.draw,temperature.gpu
  --format=csv,noheader,nounits -lms <interval>` started in background with a
  pidfile, stopped by pid kill, CSV collected to `raw/`, parsed to trace
  rows; `rail_manifest = ["gpu_board"]` (D-018 boundary: board power only,
  host CPU/DRAM excluded - record the limitation).
- **Clock (D-003):** marker events before/after remote stages bound node
  clock offset; record the bound in metadata; the reducer flags cross-node
  intervals shorter than the bound (relevant in Phase 3, not single-node 2K).

**Tests (CI-safe):** local-loopback fake transport; CSV-fixture parsing for
nvidia-smi; runner-script arg handling. Real-node smoke when P1-006 evidence
exists; record a remote bundle in a run report; fill the applicability table.

---

## Slice 2L: Orin Adapter

**Gate, acceptance, fallback:** `phase_2_plan.md` Slice 2L.

Mirror 2K with Orin specifics: runtime via the 2K remote-runner protocol
(llama.cpp-CUDA or a vendor stack - pick with evidence, log the decision);
### NVIDIA 3050

- Runtime target: vLLM (llama.cpp-CUDA fallback per Slice 2K). Telemetry:
  nvidia-smi, optional wall meter. Transport: ssh.
- Status: pending device access. Controller-side note from 2026-06-09:
  `nvidia-smi` is absent locally, which is expected on the Mac controller
  and must be checked on the NVIDIA node itself.
- Checks:
  - [ ] SSH access.
  - [ ] CUDA runtime present.
  - [ ] vLLM install path (or llama.cpp-CUDA decision recorded).
  - [ ] `nvidia-smi --query-gpu=power.draw` sampling works; sample output
    captured.
  - [ ] VRAM limit documented (8 GB expected; informs D-016).
  - [ ] Wall-meter comparison path noted.

### NVIDIA 3080 Ti (borrow)

- Same checks as the 3050, plus:
  - [ ] Borrow window confirmed and entered in `docs/milestones.md`
    (R-006: schedule only after Stage 3.0 verdicts + rehearsed runbook).
  - [ ] Memory limit documented.

### Jetson Orin Nano Super

- Runtime target: TBD (decided with D-016/Slice 2L evidence). Telemetry:
  INA3221 rails preferred, `tegrastats` fallback, wall meter last resort
  (R-008). Transport: ssh.
- Status: pending device access.
- Checks:
  - [ ] SSH access.
  - [ ] Runtime path selected and recorded.
  - [ ] Rail telemetry accessible (sysfs paths or tegrastats output
    captured; actual rail recorded per D-018).
  - [ ] Wall-meter fallback available.

### Raspberry Pi 5 + Hailo-8L

| W3 | AP-BATCH pilot (B∈{1,2,4,8,16} static) | ~93 group executions, ~3 h | AXI-SB-ADAPTER (agent lane, can start NOW); AP-BATCH freeze; group-level floor/covariance path (single-request floors do NOT transport) | decode batching economics |
| later | AP-BATCH confirmatory | ~155 groups, ~5 h | clean pilot; prospectively frozen rule | confirmed batch scaling |
| methods tail | P2-047A design → P2-047B | 20–40 exec, ~1 h | P2-047A registry entry | controller-overhead credibility |

P2-020 / P2-012 deliberately stay out of these first windows.

## Phase 3 — SPLIT PoC [hardware-gated]

Unlock conditions (all): P1-006 operational 3080 Ti lane (SSH, CUDA,
numeric `nvidia-smi power.draw`, runner behavior, trace integrity); P1-004
measured Mac↔rig topology/throughput; a same-runtime KV-compatible path on
both nodes (e.g., llama.cpp adapters both sides, or a contracted portable
serialization boundary — MLX KV state is NOT assumed portable); split-pack
floor rows for split-total/serialize/transfer/deserialize; the pack's
pre-registered AP-1 compositional predictions. Mac SoC rails and NVIDIA
board power remain separate structural measurement boundaries without a
wall-power bridge (P1-003).

## Zero-new-measurement analysis (existing 288 bundles)

Post-audit status: absolute point energies are unusable, but trace-SHAPE
analysis (the workload blob's internal structure is anchor-independent)
supports exploratory-labeled figures: phase power-profile shapes
(high-power/short prefill vs lower-power/long decode), rail-composition
structure (GPU-rail share prefill vs decode), long-decode per-token
ramp/plateau traces, and the cross-window repeatability/methods figure.
---

## D-018: Per-backend `power_w` definition and rail policy

- Date: 2026-06-09
- Status: accepted
- Phase: 2+

Context: `power_trace.csv` has `power_w`, `source`, and optional `rail`
columns, but "power" means different physical boundaries on different
backends (SoC subsystems vs GPU board vs module input vs wall AC). Without a
fixed definition, cross-target comparisons silently compare different
quantities.

Options considered:

1. One `power_w` row per sample, backend decides what it means. Con: loses
   per-rail information; the meaning varies invisibly.
2. Per-rail rows only, reducers sum everything. Con: "everything" differs by
   backend; accidental double counting (e.g., a backend reporting both
   package and per-subsystem rails).
3. Per-rail rows preserved as reported, plus a per-backend *rail manifest*
   that names exactly which rails sum to the backend's canonical `power_w`
   for reduction, and a methodology table stating each backend's physical
   measurement boundary. powermetrics: cpu_power + gpu_power + ane_power
   (SoC subsystem proxy; excludes display, storage, PSU losses). nvidia-smi:
   board power as reported (GPU board only; excludes host). jetson_rails:
   VDD_IN preferred (module input) with the actually-used rail recorded.
   wall_meter: AC wall power (full system).

Decision: option 3.

Considerations: per-rail rows keep raw fidelity (Apple's per-subsystem split
is itself interesting data); the manifest makes the summation auditable and
fixable post hoc; the boundary table converts an implicit comparability
problem into an explicit, reportable limitation - cross-target absolute
comparisons must state boundaries, and wall-meter deltas (when the meter
exists, P1-003) calibrate the gap.

Consequences: telemetry adapters declare their rail manifest in
`device_metadata`; reducer sums per the manifest; methodology gains the
sweep reverts to exploratory with that stated).

---

## D-049: Split transfer-energy boundary accounting on discrete-GPU ends

- Date: 2026-07-08
- Status: accepted (C-020; Codex-stack catch, repo-verified)
- Phase: 3

Context: on nvidia-smi-measured ends, board power EXCLUDES the host
CPU/NIC/DRAM work of moving KV bytes over TCP — so "transfer energy"
measured at a discrete-GPU end is near-zero by construction: a silent
undercount in unmeasured silicon, asymmetric across the pairing matrix
(Mac and Jetson boundaries include their NIC/host paths; dGPU boundaries
do not).

Options considered:

1. Ignore — report board-only numbers. Con: cross-pairing transfer
   comparisons silently broken; exactly the boundary sin (D-018) the
   project exists to avoid.
2. Wall-meter (or equivalent host-side measurement of) the GPU host on
   transfer legs so the transfer window has a host-inclusive boundary.
3. Explicitly scope dGPU transfer cells as board-only LOWER BOUNDS in
   the stage accounting, named per cell in the AP row and claim wording.
docs/process/state_kernel.json:1439:    "NVIDIA-PORTABILITY-01": {
docs/process/state_kernel.json:1442:          "S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed",
docs/process/state_kernel.json:1443:          "S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery)",
docs/process/state_kernel.json:1447:          "json_pointer": "/tasks/NVIDIA-PORTABILITY-01/acceptance",
docs/process/state_kernel.json:1448:          "label": "NVIDIA-PORTABILITY-01 acceptance",
docs/process/state_kernel.json:1479:      "goal": "NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger.",
docs/process/state_kernel.json:1480:      "id": "NVIDIA-PORTABILITY-01",

exec
/bin/zsh -lc "rg --files .desk 2>/dev/null | rg 'nvidia|NVIDIA|extension' | head -n 100; sed -n '1430,1490p' docs/process/state_kernel.json; rg -n \"counter-mechanics|rate-aware pulse|pulse anchor|averaging window|NVML\" docs | head -n 250" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
      "goal": "Decide and implement whether the production DEFAULT_RETENTION_ROOT should be process/instance-unique: it currently is a fixed shared temp path (a latent collision hazard for genuinely concurrent clients), but making it unique conflicts with next-session custody reclamation. Resolve the tradeoff or record it as accepted.",
      "id": "NODE-CUSTODY-DEFAULT-01",
      "lane": "agent",
      "priority": "p3_hardening_candidates",
      "rank": 51,
      "status": "queued",
      "status_note": "Deferred 2026-08-03 from NVIDIA-RETENTION-FLAKE-01 (PR #97 closed the test-side flake); the production hardening is a NEEDS_RULING tradeoff, non-blocking (no current concurrent-client scenario).",
      "stop_card": null
    },
    "NVIDIA-PORTABILITY-01": {
      "acceptance": {
        "evidence": [
          "S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed",
          "S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery)",
          "A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing)"
        ],
        "pointer": {
          "json_pointer": "/tasks/NVIDIA-PORTABILITY-01/acceptance",
          "label": "NVIDIA-PORTABILITY-01 acceptance",
          "path": "docs/process/state_kernel.json"
        },
        "summary": "Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper."
      },
      "authority": {
        "label": "2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate",
        "path": "docs/run_reports/2026-08-01-desk-adjudication-session.md"
      },
      "dependencies": [
        {
          "evidence": null,
          "kind": "external",
          "required": "Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)",
          "scope": "start",
          "state": "pending",
          "strength": "hard",
          "target": "ED-NVIDIA-RATIFY"
        }
      ],
      "fallback": null,
      "fences": [
        {
          "authority": {
            "label": "Consult synthesis: December claims table stays Mac-only (both lenses)",
            "path": "docs/run_reports/2026-08-01-desk-adjudication-session.md"
          },
          "rule": "No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals"
        }
      ],
      "flags": [],
      "goal": "NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger.",
      "id": "NVIDIA-PORTABILITY-01",
      "lane": "agent",
      "priority": "p3_research_expansion",
      "rank": 50,
      "status": "blocked",
      "stop_card": null
    },
    "P1-001": {
      "acceptance": {
        "evidence": [
          "Dated notes in docs/phase_1/phase_1_exit_checklist.md"
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:30:boundary**. Therefore the NVML and RAPL legs can demonstrate transfer of
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:43:is **pulse-to-workload transfer**. On NVML/RAPL there is no workload at all, so
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:61:The proposal makes NVML portability **contribution #3** and puts it in the results
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:102:and the flagship instrument still has zero citable numbers. NVML on this project
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:123:Ti rig for NVML."* The repo is internally inconsistent and, on either reading,
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:150:is unavailable (F3) and NVML is fenced (F2) — the *modal* branch — this paper is
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:156:methodology across RAPL and NVML is a populated area (RAPL in Action; Jay &
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:191:2. **Demote NVML/RAPL to a desk-only capability appendix with zero claims — which
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-floor-methodology-general.md:193:   backend-neutral counter schema, the counter-mechanics analysis (wrap, cadence,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:819:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3138:boundary**. Therefore the NVML and RAPL legs can demonstrate transfer of
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3151:is **pulse-to-workload transfer**. On NVML/RAPL there is no workload at all, so
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3169:The proposal makes NVML portability **contribution #3** and puts it in the results
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3210:and the flagship instrument still has zero citable numbers. NVML on this project
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3231:Ti rig for NVML."* The repo is internally inconsistent and, on either reading,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3258:is unavailable (F3) and NVML is fenced (F2) — the *modal* branch — this paper is
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3264:methodology across RAPL and NVML is a populated area (RAPL in Action; Jay &
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3299:2. **Demote NVML/RAPL to a desk-only capability appendix with zero claims — which
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:3301:   backend-neutral counter schema, the counter-mechanics analysis (wrap, cadence,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:7247:D-078 was created to destroy on the Mac. NVML board power on consumer Ampere is a filtered average whose
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:7315:IB, GPU-only NVML), Splitwise, Prima.cpp, SplitZip. An *offline file-replay* split — prefill on a Mac,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:7319:the failure mode (PyNVML board vs powermetrics SoC); showing the comparison is invalid is not new, and
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8569:boundary**. Therefore the NVML and RAPL legs can demonstrate transfer of
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8582:is **pulse-to-workload transfer**. On NVML/RAPL there is no workload at all, so
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8600:The proposal makes NVML portability **contribution #3** and puts it in the results
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8641:and the flagship instrument still has zero citable numbers. NVML on this project
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8662:Ti rig for NVML."* The repo is internally inconsistent and, on either reading,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8689:is unavailable (F3) and NVML is fenced (F2) — the *modal* branch — this paper is
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8695:methodology across RAPL and NVML is a populated area (RAPL in Action; Jay &
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8730:2. **Demote NVML/RAPL to a desk-only capability appendix with zero claims — which
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:8732:   backend-neutral counter schema, the counter-mechanics analysis (wrap, cadence,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:10482:D-078 was created to destroy on the Mac. NVML board power on consumer Ampere is a filtered average whose
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:10550:IB, GPU-only NVML), Splitwise, Prima.cpp, SplitZip. An *offline file-replay* split — prefill on a Mac,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:10554:the failure mode (PyNVML board vs powermetrics SoC); showing the comparison is invalid is not new, and
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11456:JouleWise already contains the spine of a strong measurement-methodology paper: a complete-in-structure MVP draft; a 59-pulse, in-window bracket calibration; worst-case phase-edge integration; separately measured repeatability and never-zero drift; two independent claim gates; and a fail-closed, hash-bound protocol whose refusals are retained as evidence. Its central empirical finding is that the M3 Max instrument is attribution-limited: roughly 30 ms of edge uncertainty across a roughly 33 W transition can misassign about 1 J, while ordinary repeatability is nearer 0.3 J. Because the calibrated floor and the contrast’s own interval are separate requirements, practical phase contrasts need roughly 5 J, and repetition cannot average away the boundary term. No current demonstration number is claim-bearing: D-117 therefore requires three fresh prospective windows—1.5B decode floor with a free prefill rider, 7B decode floor with a prefill rider, and a 1.5B-versus-7B decode contrast—budgeted at 3.14, 3.24, and 2.80 hours respectively. From today, first finish the two-slot calibration-ledger session, D-102 successor builder, four-cell mint, campaign packs, extraction specifications, and synthetic refusal regression; then collect and mint the two floor windows, collect gamma, and populate the MVP tables. Only afterward should this paper add two compact portability sessions on the desktop rig: one NVML GPU-counter characterization and, if the host exposes a usable package-energy counter, one RAPL characterization. The honest target is therefore **five quiet-device sessions: three already required Mac nights plus two estimated 2–3-hour desktop sessions**. If RAPL capability fails at the desk gate, the paper shrinks to a counter-agnostic framework evaluated on `powermetrics` and NVML, with RAPL described only as a future instantiation—not falsely presented as validated.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11464:3. **A portability battery for NVML and RAPL.** Each backend must mint its own floor; the Mac’s approximately 5 J bar is never transported. A backend passes only if deliberately super-floor effects clear in both directions while sub-floor effects are refused.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11475:| NVML portability | Pre/post pulse calibration, absolute repeats, identical-label ABBA nulls, and held-out positive/negative duration deltas. Prefer cumulative board-energy readings if supported. | Tentative GPU swing of 200–300 W is **uncertain**: 25–100 ms added work suggests roughly 5–30 J, but Ampere’s reported power may be averaged over one second, making calibration essential. [NVIDIA documents the one-second Ampere average](https://docs.nvidia.com/deploy/nvidia-smi/index.html). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11484:Owned hardware is sufficient for the core: the M3 Max for D-117 and the RTX 3080 Ti rig for NVML. NVML exposes cumulative energy in millijoules on supported devices but can return `NOT_SUPPORTED`, so support must be probed before scheduling collection. [NVML API documentation](https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html). RAPL is conditional on the desktop CPU and OS exposing `energy_uj` and `max_energy_range_uj` through Linux powercap. [Linux powercap documentation](https://cdn.kernel.org/doc/html/latest/power/powercap/powercap.html).
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11490:Without portability data, this is the capstone paper’s methods-first framing. With one additional passing backend, it fits an energy/performance workshop or ICPE emerging-research track. With both NVML and RAPL, held-out floor verification, and preferably wall-total validation, it becomes a plausible ICPE full-paper direction.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11496:Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11505:**Thesis:** Software energy counters should be admitted as scientific instruments only after workload-local calibration establishes what effects they can resolve; JouleWise demonstrates this framework rigorously on `powermetrics` and tests whether it transfers to NVML and RAPL without assuming that it will.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11509:JouleWise already contains the spine of a strong measurement-methodology paper: a complete-in-structure MVP draft; a 59-pulse, in-window bracket calibration; worst-case phase-edge integration; separately measured repeatability and never-zero drift; two independent claim gates; and a fail-closed, hash-bound protocol whose refusals are retained as evidence. Its central empirical finding is that the M3 Max instrument is attribution-limited: roughly 30 ms of edge uncertainty across a roughly 33 W transition can misassign about 1 J, while ordinary repeatability is nearer 0.3 J. Because the calibrated floor and the contrast’s own interval are separate requirements, practical phase contrasts need roughly 5 J, and repetition cannot average away the boundary term. No current demonstration number is claim-bearing: D-117 therefore requires three fresh prospective windows—1.5B decode floor with a free prefill rider, 7B decode floor with a prefill rider, and a 1.5B-versus-7B decode contrast—budgeted at 3.14, 3.24, and 2.80 hours respectively. From today, first finish the two-slot calibration-ledger session, D-102 successor builder, four-cell mint, campaign packs, extraction specifications, and synthetic refusal regression; then collect and mint the two floor windows, collect gamma, and populate the MVP tables. Only afterward should this paper add two compact portability sessions on the desktop rig: one NVML GPU-counter characterization and, if the host exposes a usable package-energy counter, one RAPL characterization. The honest target is therefore **five quiet-device sessions: three already required Mac nights plus two estimated 2–3-hour desktop sessions**. If RAPL capability fails at the desk gate, the paper shrinks to a counter-agnostic framework evaluated on `powermetrics` and NVML, with RAPL described only as a future instantiation—not falsely presented as validated.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11517:3. **A portability battery for NVML and RAPL.** Each backend must mint its own floor; the Mac’s approximately 5 J bar is never transported. A backend passes only if deliberately super-floor effects clear in both directions while sub-floor effects are refused.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11528:| NVML portability | Pre/post pulse calibration, absolute repeats, identical-label ABBA nulls, and held-out positive/negative duration deltas. Prefer cumulative board-energy readings if supported. | Tentative GPU swing of 200–300 W is **uncertain**: 25–100 ms added work suggests roughly 5–30 J, but Ampere’s reported power may be averaged over one second, making calibration essential. [NVIDIA documents the one-second Ampere average](https://docs.nvidia.com/deploy/nvidia-smi/index.html). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11537:Owned hardware is sufficient for the core: the M3 Max for D-117 and the RTX 3080 Ti rig for NVML. NVML exposes cumulative energy in millijoules on supported devices but can return `NOT_SUPPORTED`, so support must be probed before scheduling collection. [NVML API documentation](https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html). RAPL is conditional on the desktop CPU and OS exposing `energy_uj` and `max_energy_range_uj` through Linux powercap. [Linux powercap documentation](https://cdn.kernel.org/doc/html/latest/power/powercap/powercap.html).
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11543:Without portability data, this is the capstone paper’s methods-first framing. With one additional passing backend, it fits an energy/performance workshop or ICPE emerging-research track. With both NVML and RAPL, held-out floor verification, and preferably wall-total validation, it becomes a plausible ICPE full-paper direction.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:11549:Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:13072:The referee was right: this has the portfolio’s best framing—“from repeatability to resolvability”—and an unfundable portability experiment. The NVML/RAPL battery neither transports the phase-attribution finding nor respects existing fences. The surviving content is the MVP’s intellectual packaging plus Window C’s held-out effect ladder. Cost is therefore **the same four MVP nights**, with roughly **1–3 additional desk weeks** for the ladder analysis, refusal taxonomy, and prose. Probability of a useful result is **70–80%** because both correct refusals and correct resolutions support the thesis. Rank four reflects its value to the capstone, not authorization for a second manuscript.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:13267:The referee was right: this has the portfolio’s best framing—“from repeatability to resolvability”—and an unfundable portability experiment. The NVML/RAPL battery neither transports the phase-attribution finding nor respects existing fences. The surviving content is the MVP’s intellectual packaging plus Window C’s held-out effect ladder. Cost is therefore **the same four MVP nights**, with roughly **1–3 additional desk weeks** for the ladder analysis, refusal taxonomy, and prose. Probability of a useful result is **70–80%** because both correct refusals and correct resolutions support the thesis. Rank four reflects its value to the capstone, not authorization for a second manuscript.
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:35:D-078 was created to destroy on the Mac. NVML board power on consumer Ampere is a filtered average whose
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:103:IB, GPU-only NVML), Splitwise, Prima.cpp, SplitZip. An *offline file-replay* split — prefill on a Mac,
docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:107:the failure mode (PyNVML board vs powermetrics SoC); showing the comparison is invalid is not new, and
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:1212:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:1300:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/phase_4/related_work_draft.md:255:software instrumentation layer for ML energy measurement: it reads NVML
docs/phase_4/related_work_draft.md:269:instrumentation approach (NVML on NVIDIA, IOReport-class counters on Apple
docs/phase_4/related_work_draft.md:291:NVML/DCGM, CPU/DRAM power via Intel RAPL, and node/system power via IPMI
docs/phase_4/related_work_draft.md:312:NVML/RAPL/IPMI report, and energy of prefill/decode-disaggregated split
docs/phase_4/related_work_draft.md:330:GPU-only in software via the authors' Zeus library (NVML counters), with a
docs/phase_4/related_work_draft.md:344:single GPU-only NVML boundary (the paper is boundary-transparent, but only
docs/phase_4/related_work_draft.md:361:measurement is device-specific software telemetry sampled at ~50 ms: NVML
docs/phase_4/related_work_draft.md:376:leaves open: IPW mixes powermetrics, NVML, and ROCm SMI readings without
docs/phase_4/related_work_draft.md:396:realistic local deployments. Energy is measured GPU-only via NVIDIA NVML
docs/phase_4/related_work_draft.md:398:dominates LLM inference" and cite NVML error bounds below 5%. Evaluation
docs/phase_4/related_work_draft.md:414:manifests instead of a GPU-only NVML boundary, published auditable raw run
docs/phase_4/related_work_draft.md:426:measured GPU-only via the Zeus library (NVML-based), computing
docs/phase_4/related_work_draft.md:446:manifests instead of GPU-only NVML readings, and energy of
docs/phase_4/related_work_draft.md:474:H100 GPUs across two InfiniBand-connected nodes. Energy is GPU-only: NVML
docs/phase_4/related_work_draft.md:521:also asymmetric—PyNVML GPU-board power for NVIDIA versus powermetrics
docs/phase_4/related_work_draft.md:572:powermetrics/NVML/ROCm SMI without stating comparability, which is the
docs/phase_2/splitwise_replication_roadmap.md:35:   disaggregation result: no NVML-style power capping on Apple Silicon, no
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-advisor.md:572:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-advisor.md:660:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:4808:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:4796:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:4874:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-long-generation-dynamics.md:493:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:1960:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:2048:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5496:docs/process/state_kernel.json:1443:          "S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery)",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5565:docs/paper/related_work_draft.md:15:Software-visible counters such as Intel's Running Average Power Limit (RAPL) counters and Apple's `powermetrics` make repeated energy experiments practical without a laboratory meter, but their readings remain outputs of a measurement system rather than ground truth. RAPL in Action shows that validation should model the relationship between software channels and wall power, search for lag before comparing streams, account for temporal correlation, warm the machine to reduce thermal drift, audit the sampler's overhead, and inspect counter mechanics such as update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. <!-- 2026-07-30-sweep-techniques.md: RAPL in Action contributes model-based wall validation, lag search, autocorrelation-aware analysis, warm-up, sampler-overhead measurement, and a counter-mechanics checklist. --> Jay and Ostapenco likewise compare software meters against wall power with controlled workloads and regression, finding that the gap changes with load rather than behaving as a constant offset; they also refuse component-level rankings where no reference exists [JayOstapenco]. <!-- 2026-07-30-sweep-techniques.md: Jay/Ostapenco regress wall power on software readings, find a load-dependent rather than constant gap, and decline claims where no reference validates subtotals. --> A wall meter can therefore test whole-machine totals, but it cannot by itself validate how a software trace divides that total between prompt processing and token generation [JayOstapenco]. <!-- 2026-07-30-sweep-techniques.md: the sweep states that wall metering validates totals only, while phase splits require a separate phase-attribution method. -->
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5657:docs/run_reports/2026-07-30-sweep-techniques.md:37:**Adopt/adapt:** (i) **Internal dual-instrument cross-validation**: they validate sampled-power integrals against the independent NVML hardware energy counter and publish the agreement bound (2%, valid only for ops ≥200 ms). JouleWise's pre-wall-meter analogue: cross-check powermetrics integrals against an independent on-device channel (battery/SMC drain deltas over long windows) and publish the number with its validity domain. (ii) **Duration-conditional validity**: they name where the method breaks (<100 ms), the affected fraction (44% of prefill configs), and a declared fallback — slots directly into JouleWise's fail-closed gates as a minimum-window rule in units of powermetrics cadence. (iii) **Effect/noise ratio as a standard column** ("spread exceeds noise by 1.2–27×") plus their extra move: distinguishing "above floor" from "operationally meaningful." (iv) **Weight-controlled ablation** (same base weights, one variable changed via TransMLA) — for any JouleWise A/B, hold everything bit-identical and say so. (v) Max-stddev printed in figure captions. (vi) Mechanistic corroboration (rooflines) — corroborate energy splits with powermetrics' utilization/frequency channels so claims aren't single-signal. (vii) Pareto-frontier operating-point template.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5952:   (C7 reconciliation, MDE machinery, the powermetrics counter-mechanics audit)
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:6772:docs/run_reports/2026-07-30-paper-outline-v1.md-143-5. Desk throughout: C7 reconciliation; MDE machinery; counter-mechanics
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:6784:docs/paper/related_work_draft.md-9-The Illusion of Power Capping in LLM Decode provides a stronger measurement template: it samples graphics processing unit (GPU) power, integrates the samples, repeats configurations, and checks the integral against a separate hardware energy counter, while explicitly limiting that check to operations long enough for the counter to be meaningful [IllusionPowerCapping]. <!-- 2026-07-30-sweep-techniques.md: the Illusion study uses sampled-power integration, repetitions, an independent NVML energy-counter cross-check, and a duration-conditional validity domain. --> However, its counter agreement, run-to-run variation, snapshot fallback, and timing alignment are not composed into a bound on the reported savings, and its long sweeps do not include a drift-control design [IllusionPowerCapping]. <!-- 2026-07-30-sweep-techniques.md: the sweep identifies uncomposed error terms and no drift control across long sweeps as the study's open lane. --> JouleWise treats those terms as inputs to a single claim decision rather than as separate caveats.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:6786:docs/paper/related_work_draft.md-11-Benchmark standards reinforce that measurement validity belongs in each run. MLPerf Power and the associated Standard Performance Evaluation Corporation (SPEC) methodology require a qualified external analyzer, uncertainty computed at the actual load, fixed measurement ranges, synchronized clocks, sufficiently long windows, invalid-sample accounting, and special handling for battery-backed systems [MLPerfPower]. <!-- 2026-07-30-sweep-techniques.md: MLPerf Power/SPEC requires load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum windows, per-window invalid-sample accounting, and neutralized battery charge flow. --> These rules are designed for direct power analyzers and data-center-style benchmarks; JouleWise translates their reject-on-missing-evidence discipline to a free software counter on consumer hardware. Apple-focused comparisons show why that translation matters: Silicon Showdown compares deployed ecosystems using a GPU-board boundary on one platform and a whole-system-on-chip software-counter boundary on Apple hardware, with unmatched runtimes and precision stacks and no comparison of model-output accuracy [SiliconShowdown]. <!-- 2026-07-11-rpt002-related-work-refresh.md: Silicon Showdown compares unmatched runtime/artifact/precision stacks across PyNVML GPU-board and powermetrics whole-SoC boundaries and includes no accuracy evaluation. --> JouleWise therefore names the measured boundary and prioritizes within-stack claims instead of treating unlike telemetry boundaries as interchangeable.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:6790:docs/paper/related_work_draft.md:15:Software-visible counters such as Intel's Running Average Power Limit (RAPL) counters and Apple's `powermetrics` make repeated energy experiments practical without a laboratory meter, but their readings remain outputs of a measurement system rather than ground truth. RAPL in Action shows that validation should model the relationship between software channels and wall power, search for lag before comparing streams, account for temporal correlation, warm the machine to reduce thermal drift, audit the sampler's overhead, and inspect counter mechanics such as update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. <!-- 2026-07-30-sweep-techniques.md: RAPL in Action contributes model-based wall validation, lag search, autocorrelation-aware analysis, warm-up, sampler-overhead measurement, and a counter-mechanics checklist. --> Jay and Ostapenco likewise compare software meters against wall power with controlled workloads and regression, finding that the gap changes with load rather than behaving as a constant offset; they also refuse component-level rankings where no reference exists [JayOstapenco]. <!-- 2026-07-30-sweep-techniques.md: Jay/Ostapenco regress wall power on software readings, find a load-dependent rather than constant gap, and decline claims where no reference validates subtotals. --> A wall meter can therefore test whole-machine totals, but it cannot by itself validate how a software trace divides that total between prompt processing and token generation [JayOstapenco]. <!-- 2026-07-30-sweep-techniques.md: the sweep states that wall metering validates totals only, while phase splits require a separate phase-attribution method. -->
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:7304:5. Desk throughout: C7 reconciliation; MDE machinery; counter-mechanics
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:7504:   disaggregation result: no NVML-style power capping on Apple Silicon, no
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:5100:docs/run_reports/2026-07-30-sweep-techniques.md:37:**Adopt/adapt:** (i) **Internal dual-instrument cross-validation**: they validate sampled-power integrals against the independent NVML hardware energy counter and publish the agreement bound (2%, valid only for ops ≥200 ms). JouleWise's pre-wall-meter analogue: cross-check powermetrics integrals against an independent on-device channel (battery/SMC drain deltas over long windows) and publish the number with its validity domain. (ii) **Duration-conditional validity**: they name where the method breaks (<100 ms), the affected fraction (44% of prefill configs), and a declared fallback — slots directly into JouleWise's fail-closed gates as a minimum-window rule in units of powermetrics cadence. (iii) **Effect/noise ratio as a standard column** ("spread exceeds noise by 1.2–27×") plus their extra move: distinguishing "above floor" from "operationally meaningful." (iv) **Weight-controlled ablation** (same base weights, one variable changed via TransMLA) — for any JouleWise A/B, hold everything bit-identical and say so. (v) Max-stddev printed in figure captions. (vi) Mechanistic corroboration (rooflines) — corroborate energy splits with powermetrics' utilization/frequency channels so claims aren't single-signal. (vii) Pareto-frontier operating-point template.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:5108:docs/paper/related_work_draft.md:15:Software-visible counters such as Intel's Running Average Power Limit (RAPL) counters and Apple's `powermetrics` make repeated energy experiments practical without a laboratory meter, but their readings remain outputs of a measurement system rather than ground truth. RAPL in Action shows that validation should model the relationship between software channels and wall power, search for lag before comparing streams, account for temporal correlation, warm the machine to reduce thermal drift, audit the sampler's overhead, and inspect counter mechanics such as update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. <!-- 2026-07-30-sweep-techniques.md: RAPL in Action contributes model-based wall validation, lag search, autocorrelation-aware analysis, warm-up, sampler-overhead measurement, and a counter-mechanics checklist. --> Jay and Ostapenco likewise compare software meters against wall power with controlled workloads and regression, finding that the gap changes with load rather than behaving as a constant offset; they also refuse component-level rankings where no reference exists [JayOstapenco]. <!-- 2026-07-30-sweep-techniques.md: Jay/Ostapenco regress wall power on software readings, find a load-dependent rather than constant gap, and decline claims where no reference validates subtotals. --> A wall meter can therefore test whole-machine totals, but it cannot by itself validate how a software trace divides that total between prompt processing and token generation [JayOstapenco]. <!-- 2026-07-30-sweep-techniques.md: the sweep states that wall metering validates totals only, while phase splits require a separate phase-attribution method. -->
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-contrarian.md:223:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-contrarian.md:311:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-contrarian.md:5232:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-contrarian.md:5320:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-contrarian.md:5398:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/decision_log.md:5662:   (C7 reconciliation, MDE machinery, the powermetrics counter-mechanics audit)
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:857:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:945:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:1060:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:5523:docs/run_reports/2026-07-30-sweep-techniques.md:45:**Adopt/adapt (Khan):** model-based validation, not identity: fit wall = f(software channels), report MAE/RMSE/MAPE on held-out data with channel ablation (Haswell GAM: 1.7% MAPE — the literature benchmark for "good"). Lag-hunt via cross-correlation before comparing streams (they found 10–24 s lags). Autocorrelation-aware stats (subsample/block before fitting). ≥2-min warm-up (kills a ~10–12% thermal power drift they measured, 37→74 °C). Instrument-overhead audit (with/without sampler; <1.2% even at 1 kHz). And the **counter-mechanics checklist** — overflow period, update granularity/jitter, non-atomicity, missing timestamps — is exactly the audit nobody has run on powermetrics' internal counters.
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:413:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:501:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mtp-energy.md:5870:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mtp-energy.md:5958:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mtp-energy.md:6537:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-energy-nutrition-label.md:3938:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-energy-nutrition-label.md:4016:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-energy-nutrition-label.md:4116:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-energy-nutrition-label.md:4204:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1269:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-EXEC.md:1347:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:5211:   disaggregation result: no NVML-style power capping on Apple Silicon, no
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6279:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6308:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6421:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6827:NVML/DCGM, CPU/DRAM power via Intel RAPL, and node/system power via IPMI
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6848:NVML/RAPL/IPMI report, and energy of prefill/decode-disaggregated split
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6866:GPU-only in software via the authors' Zeus library (NVML counters), with a
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6880:single GPU-only NVML boundary (the paper is boundary-transparent, but only
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6898:realistic local deployments. Energy is measured GPU-only via NVIDIA NVML
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6900:dominates LLM inference" and cite NVML error bounds below 5%. Evaluation
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6916:manifests instead of a GPU-only NVML boundary, published auditable raw run
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6928:measured GPU-only via the Zeus library (NVML-based), computing
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:6972:H100 GPUs across two InfiniBand-connected nodes. Energy is GPU-only: NVML
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-spec-decode-energy.md:938:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:477:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:565:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:5928:   998	| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:6006:  1076	| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:6411:  1481	| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:6489:  1559	| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-night-hardening/AUDIT-PAPER-FIDELITY.md:1063:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/process_traces/2026-08-07-night-hardening/AUDIT-PAPER-FIDELITY.md:1151:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-night-hardening/OPERATOR-PACKET-DRAFT.md:1070:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/report_src/source_map.json:46:      "scope_boundary": "Sixteen H100 GPUs across two homogeneous nodes connected by InfiniBand; NVML instantaneous GPU power sampled at 10 ms, not node- or cluster-level energy.",
docs/report_src/source_map.json:62:        "COMPLETED: bounded every energy statement to homogeneous H100 GPU-only NVML measurement."
docs/report_src/source_map.json:173:      "scope_boundary": "NVIDIA uses PyNVML GPU-board power while Apple uses powermetrics whole-SoC power; TensorRT-LLM plus NVFP4 or llama.cpp GGUF is not matched to MLX native 4-bit.",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mvp-icpe-upgrade.md:3742:5. Desk throughout: C7 reconciliation; MDE machinery; counter-mechanics
docs/process_traces/2026-08-07-night-hardening/AUDIT-RUNNER.md:1128:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/process_traces/2026-08-07-night-hardening/AUDIT-MINT.md:998:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-night-hardening/AUDIT-MINT.md:1076:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-night-hardening/AUDIT-MINT.md:1481:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/process_traces/2026-08-07-night-hardening/AUDIT-MINT.md:1559:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:586:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:674:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:4599:docs/run_reports/2026-07-30-sweep-techniques.md:35:The real methods quarry of the six. GQA/MLA/GDN/Mamba2 on one H200; NVML at 50 ms with trapezoidal integration; 10–20 reps, 3 warmups, medians with published max-stddev (≤3%, typically <0.5%).
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:4788:The real methods quarry of the six. GQA/MLA/GDN/Mamba2 on one H200; NVML at 50 ms with trapezoidal integration; 10–20 reps, 3 warmups, medians with published max-stddev (≤3%, typically <0.5%).
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:4790:**Adopt/adapt:** (i) **Internal dual-instrument cross-validation**: they validate sampled-power integrals against the independent NVML hardware energy counter and publish the agreement bound (2%, valid only for ops ≥200 ms). JouleWise's pre-wall-meter analogue: cross-check powermetrics integrals against an independent on-device channel (battery/SMC drain deltas over long windows) and publish the number with its validity domain. (ii) **Duration-conditional validity**: they name where the method breaks (<100 ms), the affected fraction (44% of prefill configs), and a declared fallback — slots directly into JouleWise's fail-closed gates as a minimum-window rule in units of powermetrics cadence. (iii) **Effect/noise ratio as a standard column** ("spread exceeds noise by 1.2–27×") plus their extra move: distinguishing "above floor" from "operationally meaningful." (iv) **Weight-controlled ablation** (same base weights, one variable changed via TransMLA) — for any JouleWise A/B, hold everything bit-identical and say so. (v) Max-stddev printed in figure captions. (vi) Mechanistic corroboration (rooflines) — corroborate energy splits with powermetrics' utilization/frequency channels so claims aren't single-signal. (vii) Pareto-frontier operating-point template.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:4798:**Adopt/adapt (Khan):** model-based validation, not identity: fit wall = f(software channels), report MAE/RMSE/MAPE on held-out data with channel ablation (Haswell GAM: 1.7% MAPE — the literature benchmark for "good"). Lag-hunt via cross-correlation before comparing streams (they found 10–24 s lags). Autocorrelation-aware stats (subsample/block before fitting). ≥2-min warm-up (kills a ~10–12% thermal power drift they measured, 37→74 °C). Instrument-overhead audit (with/without sampler; <1.2% even at 1 kHz). And the **counter-mechanics checklist** — overflow period, update granularity/jitter, non-atomicity, missing timestamps — is exactly the audit nobody has run on powermetrics' internal counters.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:4838:9. **powermetrics counter-mechanics audit** (Paper 3a). Run Khan's checklist against powermetrics itself: sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead (with/without sampler at each cadence) — the characterization nobody has published for Apple Silicon, and a citable contribution in its own right.
docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:871:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:959:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:881:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:969:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:6375:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:6463:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/report_src/chapters/03_background_and_related_work.md:75:across two InfiniBand-connected nodes—and GPU-only, using 10 ms NVML power
docs/report_src/chapters/03_background_and_related_work.md:104:unmatched to MLX native 4-bit, and PyNVML GPU-board power is unmatched to
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:104:The detection-floor methodology generalized beyond LLMs: software-counter metrology (RAPL, powermetrics, NVML) with attribution-limited floors as a general framework — a measurement-methodology paper.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:107:I’ll develop this as a read-only methodology proposal. I’ll first reconstruct the exact D-117 outputs and the draft’s reusable claims, then test how far a RAPL/powermetrics/NVML generalization can honestly go without requiring new apparatus or abandoning the M3 Max evidence base.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5047:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5125:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5226:The honest scope is emerging: the existing evidence can support a counter-agnostic framework and a full `powermetrics` case study, but not the empirical claim that RAPL and NVML are already calibrated. I’m now checking the documented mechanics of those counters to define a small portability experiment whose possible outcome includes “the framework refuses this backend,” rather than presuming successful transfer.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5232:/bin/zsh -lc 'rg -n "NVML|3080 Ti|RAPL|total.energy|energy counter|sampling" docs joulewise tests | head -240' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5482:/bin/zsh -lc "rg -n \"counter-mechanics appendix|capability probe|NVIDIA-PORTABILITY|zero-claim\" . --glob '"'!RUN_STATE.md'"' --glob '"'!TASK_QUEUE.md'"' | head -200" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5490:./docs/process/state_kernel.json:1442:          "S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5494:./docs/process/state_kernel.json:1479:      "goal": "NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger.",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5852:**Thesis:** Software energy counters should be admitted as scientific instruments only after workload-local calibration establishes what effects they can resolve; JouleWise demonstrates this framework rigorously on `powermetrics` and tests whether it transfers to NVML and RAPL without assuming that it will.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5856:JouleWise already contains the spine of a strong measurement-methodology paper: a complete-in-structure MVP draft; a 59-pulse, in-window bracket calibration; worst-case phase-edge integration; separately measured repeatability and never-zero drift; two independent claim gates; and a fail-closed, hash-bound protocol whose refusals are retained as evidence. Its central empirical finding is that the M3 Max instrument is attribution-limited: roughly 30 ms of edge uncertainty across a roughly 33 W transition can misassign about 1 J, while ordinary repeatability is nearer 0.3 J. Because the calibrated floor and the contrast’s own interval are separate requirements, practical phase contrasts need roughly 5 J, and repetition cannot average away the boundary term. No current demonstration number is claim-bearing: D-117 therefore requires three fresh prospective windows—1.5B decode floor with a free prefill rider, 7B decode floor with a prefill rider, and a 1.5B-versus-7B decode contrast—budgeted at 3.14, 3.24, and 2.80 hours respectively. From today, first finish the two-slot calibration-ledger session, D-102 successor builder, four-cell mint, campaign packs, extraction specifications, and synthetic refusal regression; then collect and mint the two floor windows, collect gamma, and populate the MVP tables. Only afterward should this paper add two compact portability sessions on the desktop rig: one NVML GPU-counter characterization and, if the host exposes a usable package-energy counter, one RAPL characterization. The honest target is therefore **five quiet-device sessions: three already required Mac nights plus two estimated 2–3-hour desktop sessions**. If RAPL capability fails at the desk gate, the paper shrinks to a counter-agnostic framework evaluated on `powermetrics` and NVML, with RAPL described only as a future instantiation—not falsely presented as validated.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5864:3. **A portability battery for NVML and RAPL.** Each backend must mint its own floor; the Mac’s approximately 5 J bar is never transported. A backend passes only if deliberately super-floor effects clear in both directions while sub-floor effects are refused.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5875:| NVML portability | Pre/post pulse calibration, absolute repeats, identical-label ABBA nulls, and held-out positive/negative duration deltas. Prefer cumulative board-energy readings if supported. | Tentative GPU swing of 200–300 W is **uncertain**: 25–100 ms added work suggests roughly 5–30 J, but Ampere’s reported power may be averaged over one second, making calibration essential. [NVIDIA documents the one-second Ampere average](https://docs.nvidia.com/deploy/nvidia-smi/index.html). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5884:Owned hardware is sufficient for the core: the M3 Max for D-117 and the RTX 3080 Ti rig for NVML. NVML exposes cumulative energy in millijoules on supported devices but can return `NOT_SUPPORTED`, so support must be probed before scheduling collection. [NVML API documentation](https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html). RAPL is conditional on the desktop CPU and OS exposing `energy_uj` and `max_energy_range_uj` through Linux powercap. [Linux powercap documentation](https://cdn.kernel.org/doc/html/latest/power/powercap/powercap.html).
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5890:Without portability data, this is the capstone paper’s methods-first framing. With one additional passing backend, it fits an energy/performance workshop or ICPE emerging-research track. With both NVML and RAPL, held-out floor verification, and preferably wall-total validation, it becomes a plausible ICPE full-paper direction.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5896:Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5905:**Thesis:** Software energy counters should be admitted as scientific instruments only after workload-local calibration establishes what effects they can resolve; JouleWise demonstrates this framework rigorously on `powermetrics` and tests whether it transfers to NVML and RAPL without assuming that it will.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5909:JouleWise already contains the spine of a strong measurement-methodology paper: a complete-in-structure MVP draft; a 59-pulse, in-window bracket calibration; worst-case phase-edge integration; separately measured repeatability and never-zero drift; two independent claim gates; and a fail-closed, hash-bound protocol whose refusals are retained as evidence. Its central empirical finding is that the M3 Max instrument is attribution-limited: roughly 30 ms of edge uncertainty across a roughly 33 W transition can misassign about 1 J, while ordinary repeatability is nearer 0.3 J. Because the calibrated floor and the contrast’s own interval are separate requirements, practical phase contrasts need roughly 5 J, and repetition cannot average away the boundary term. No current demonstration number is claim-bearing: D-117 therefore requires three fresh prospective windows—1.5B decode floor with a free prefill rider, 7B decode floor with a prefill rider, and a 1.5B-versus-7B decode contrast—budgeted at 3.14, 3.24, and 2.80 hours respectively. From today, first finish the two-slot calibration-ledger session, D-102 successor builder, four-cell mint, campaign packs, extraction specifications, and synthetic refusal regression; then collect and mint the two floor windows, collect gamma, and populate the MVP tables. Only afterward should this paper add two compact portability sessions on the desktop rig: one NVML GPU-counter characterization and, if the host exposes a usable package-energy counter, one RAPL characterization. The honest target is therefore **five quiet-device sessions: three already required Mac nights plus two estimated 2–3-hour desktop sessions**. If RAPL capability fails at the desk gate, the paper shrinks to a counter-agnostic framework evaluated on `powermetrics` and NVML, with RAPL described only as a future instantiation—not falsely presented as validated.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5917:3. **A portability battery for NVML and RAPL.** Each backend must mint its own floor; the Mac’s approximately 5 J bar is never transported. A backend passes only if deliberately super-floor effects clear in both directions while sub-floor effects are refused.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5928:| NVML portability | Pre/post pulse calibration, absolute repeats, identical-label ABBA nulls, and held-out positive/negative duration deltas. Prefer cumulative board-energy readings if supported. | Tentative GPU swing of 200–300 W is **uncertain**: 25–100 ms added work suggests roughly 5–30 J, but Ampere’s reported power may be averaged over one second, making calibration essential. [NVIDIA documents the one-second Ampere average](https://docs.nvidia.com/deploy/nvidia-smi/index.html). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5937:Owned hardware is sufficient for the core: the M3 Max for D-117 and the RTX 3080 Ti rig for NVML. NVML exposes cumulative energy in millijoules on supported devices but can return `NOT_SUPPORTED`, so support must be probed before scheduling collection. [NVML API documentation](https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html). RAPL is conditional on the desktop CPU and OS exposing `energy_uj` and `max_energy_range_uj` through Linux powercap. [Linux powercap documentation](https://cdn.kernel.org/doc/html/latest/power/powercap/powercap.html).
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5943:Without portability data, this is the capstone paper’s methods-first framing. With one additional passing backend, it fits an energy/performance workshop or ICPE emerging-research track. With both NVML and RAPL, held-out floor verification, and preferably wall-total validation, it becomes a plausible ICPE full-paper direction.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:5949:Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.
docs/reviews/2026-07-09-scientific-rigor-review.md:216:   `nvidia-smi power.draw`/NVML is a driver-reported board-power reading, usually sampled/averaged and often updated at coarse cadence. Published HPC measurement work has repeatedly found NVML/nvidia-smi useful for trends but not equivalent to calibrated external meters; reported errors depend on GPU generation and workload dynamics. Low-confidence exact claim: I would expect several-percent systematic error and poor short-window fidelity, but I am not citing a precise bound without network. Failure scenario: comparing two decode kernels with bursty power at 100-300 ms scale; nvidia-smi smooths or aliases bursts and makes the “more efficient” kernel look unchanged.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-contamination-characterization.md:950:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-contamination-characterization.md:4724:docs/reviews/2026-07-09-scientific-rigor-review.md:216:   `nvidia-smi power.draw`/NVML is a driver-reported board-power reading, usually sampled/averaged and often updated at coarse cadence. Published HPC measurement work has repeatedly found NVML/nvidia-smi useful for trends but not equivalent to calibrated external meters; reported errors depend on GPU generation and workload dynamics. Low-confidence exact claim: I would expect several-percent systematic error and poor short-window fidelity, but I am not citing a precise bound without network. Failure scenario: comparing two decode kernels with bursty power at 100-300 ms scale; nvidia-smi smooths or aliases bursts and makes the “more efficient” kernel look unchanged.
docs/process/state_kernel.json:1442:          "S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed",
docs/process/state_kernel.json:1443:          "S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery)",
docs/process/state_kernel.json:1479:      "goal": "NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger.",
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-prefill-scaling-laws.md:934:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:1486:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:1564:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4663:boundary**. Therefore the NVML and RAPL legs can demonstrate transfer of
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4676:is **pulse-to-workload transfer**. On NVML/RAPL there is no workload at all, so
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4694:The proposal makes NVML portability **contribution #3** and puts it in the results
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4735:and the flagship instrument still has zero citable numbers. NVML on this project
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4756:Ti rig for NVML."* The repo is internally inconsistent and, on either reading,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4783:is unavailable (F3) and NVML is fenced (F2) — the *modal* branch — this paper is
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4789:methodology across RAPL and NVML is a populated area (RAPL in Action; Jay &
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4824:2. **Demote NVML/RAPL to a desk-only capability appendix with zero claims — which
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:4826:   backend-neutral counter schema, the counter-mechanics analysis (wrap, cadence,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:8787:D-078 was created to destroy on the Mac. NVML board power on consumer Ampere is a filtered average whose
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:8855:IB, GPU-only NVML), Splitwise, Prima.cpp, SplitZip. An *offline file-replay* split — prefill on a Mac,
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:8859:the failure mode (PyNVML board vs powermetrics SoC); showing the comparison is invalid is not new, and
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10536:**Thesis:** Software energy counters should be admitted as scientific instruments only after workload-local calibration establishes what effects they can resolve; JouleWise demonstrates this framework rigorously on `powermetrics` and tests whether it transfers to NVML and RAPL without assuming that it will.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10540:JouleWise already contains the spine of a strong measurement-methodology paper: a complete-in-structure MVP draft; a 59-pulse, in-window bracket calibration; worst-case phase-edge integration; separately measured repeatability and never-zero drift; two independent claim gates; and a fail-closed, hash-bound protocol whose refusals are retained as evidence. Its central empirical finding is that the M3 Max instrument is attribution-limited: roughly 30 ms of edge uncertainty across a roughly 33 W transition can misassign about 1 J, while ordinary repeatability is nearer 0.3 J. Because the calibrated floor and the contrast’s own interval are separate requirements, practical phase contrasts need roughly 5 J, and repetition cannot average away the boundary term. No current demonstration number is claim-bearing: D-117 therefore requires three fresh prospective windows—1.5B decode floor with a free prefill rider, 7B decode floor with a prefill rider, and a 1.5B-versus-7B decode contrast—budgeted at 3.14, 3.24, and 2.80 hours respectively. From today, first finish the two-slot calibration-ledger session, D-102 successor builder, four-cell mint, campaign packs, extraction specifications, and synthetic refusal regression; then collect and mint the two floor windows, collect gamma, and populate the MVP tables. Only afterward should this paper add two compact portability sessions on the desktop rig: one NVML GPU-counter characterization and, if the host exposes a usable package-energy counter, one RAPL characterization. The honest target is therefore **five quiet-device sessions: three already required Mac nights plus two estimated 2–3-hour desktop sessions**. If RAPL capability fails at the desk gate, the paper shrinks to a counter-agnostic framework evaluated on `powermetrics` and NVML, with RAPL described only as a future instantiation—not falsely presented as validated.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10548:3. **A portability battery for NVML and RAPL.** Each backend must mint its own floor; the Mac’s approximately 5 J bar is never transported. A backend passes only if deliberately super-floor effects clear in both directions while sub-floor effects are refused.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10559:| NVML portability | Pre/post pulse calibration, absolute repeats, identical-label ABBA nulls, and held-out positive/negative duration deltas. Prefer cumulative board-energy readings if supported. | Tentative GPU swing of 200–300 W is **uncertain**: 25–100 ms added work suggests roughly 5–30 J, but Ampere’s reported power may be averaged over one second, making calibration essential. [NVIDIA documents the one-second Ampere average](https://docs.nvidia.com/deploy/nvidia-smi/index.html). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10568:Owned hardware is sufficient for the core: the M3 Max for D-117 and the RTX 3080 Ti rig for NVML. NVML exposes cumulative energy in millijoules on supported devices but can return `NOT_SUPPORTED`, so support must be probed before scheduling collection. [NVML API documentation](https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html). RAPL is conditional on the desktop CPU and OS exposing `energy_uj` and `max_energy_range_uj` through Linux powercap. [Linux powercap documentation](https://cdn.kernel.org/doc/html/latest/power/powercap/powercap.html).
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10574:Without portability data, this is the capstone paper’s methods-first framing. With one additional passing backend, it fits an energy/performance workshop or ICPE emerging-research track. With both NVML and RAPL, held-out floor verification, and preferably wall-total validation, it becomes a plausible ICPE full-paper direction.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10580:Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10589:**Thesis:** Software energy counters should be admitted as scientific instruments only after workload-local calibration establishes what effects they can resolve; JouleWise demonstrates this framework rigorously on `powermetrics` and tests whether it transfers to NVML and RAPL without assuming that it will.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10593:JouleWise already contains the spine of a strong measurement-methodology paper: a complete-in-structure MVP draft; a 59-pulse, in-window bracket calibration; worst-case phase-edge integration; separately measured repeatability and never-zero drift; two independent claim gates; and a fail-closed, hash-bound protocol whose refusals are retained as evidence. Its central empirical finding is that the M3 Max instrument is attribution-limited: roughly 30 ms of edge uncertainty across a roughly 33 W transition can misassign about 1 J, while ordinary repeatability is nearer 0.3 J. Because the calibrated floor and the contrast’s own interval are separate requirements, practical phase contrasts need roughly 5 J, and repetition cannot average away the boundary term. No current demonstration number is claim-bearing: D-117 therefore requires three fresh prospective windows—1.5B decode floor with a free prefill rider, 7B decode floor with a prefill rider, and a 1.5B-versus-7B decode contrast—budgeted at 3.14, 3.24, and 2.80 hours respectively. From today, first finish the two-slot calibration-ledger session, D-102 successor builder, four-cell mint, campaign packs, extraction specifications, and synthetic refusal regression; then collect and mint the two floor windows, collect gamma, and populate the MVP tables. Only afterward should this paper add two compact portability sessions on the desktop rig: one NVML GPU-counter characterization and, if the host exposes a usable package-energy counter, one RAPL characterization. The honest target is therefore **five quiet-device sessions: three already required Mac nights plus two estimated 2–3-hour desktop sessions**. If RAPL capability fails at the desk gate, the paper shrinks to a counter-agnostic framework evaluated on `powermetrics` and NVML, with RAPL described only as a future instantiation—not falsely presented as validated.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10601:3. **A portability battery for NVML and RAPL.** Each backend must mint its own floor; the Mac’s approximately 5 J bar is never transported. A backend passes only if deliberately super-floor effects clear in both directions while sub-floor effects are refused.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10612:| NVML portability | Pre/post pulse calibration, absolute repeats, identical-label ABBA nulls, and held-out positive/negative duration deltas. Prefer cumulative board-energy readings if supported. | Tentative GPU swing of 200–300 W is **uncertain**: 25–100 ms added work suggests roughly 5–30 J, but Ampere’s reported power may be averaged over one second, making calibration essential. [NVIDIA documents the one-second Ampere average](https://docs.nvidia.com/deploy/nvidia-smi/index.html). |
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10621:Owned hardware is sufficient for the core: the M3 Max for D-117 and the RTX 3080 Ti rig for NVML. NVML exposes cumulative energy in millijoules on supported devices but can return `NOT_SUPPORTED`, so support must be probed before scheduling collection. [NVML API documentation](https://docs.nvidia.com/deploy/nvml-api/group__nvmlDeviceQueries.html). RAPL is conditional on the desktop CPU and OS exposing `energy_uj` and `max_energy_range_uj` through Linux powercap. [Linux powercap documentation](https://cdn.kernel.org/doc/html/latest/power/powercap/powercap.html).
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10627:Without portability data, this is the capstone paper’s methods-first framing. With one additional passing backend, it fits an energy/performance workshop or ICPE emerging-research track. With both NVML and RAPL, held-out floor verification, and preferably wall-total validation, it becomes a plausible ICPE full-paper direction.
docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:10633:Kill a backend before a measurement session if its required counter is unsupported, timestamps or wrap behavior cannot be bounded, deterministic pulses cannot be reproduced, telemetry overhead materially perturbs the signal, or a desk pilot projects that a `2F` effect cannot fit inside a four-hour window. Kill the three-counter claim if RAPL is unavailable. Kill “general validation” if NVML’s held-out super-floor contrasts fail; retain it as a documented portability refusal. Never compensate by smoothing, increasing repetitions after seeing results, or borrowing the Mac floor.
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-refusal-as-result.md:5048:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) [AGENT] | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-refusal-as-result.md:5126:| A50 | NVIDIA-PORTABILITY-01 | P3 Research Expansion | BLOCKED — ED-NVIDIA-RATIFY (Ed ratifies the staged plan and answers the intent question (claim vs appendix vs asset)) | NVIDIA extension, staged: S1 NVML counter-mechanics appendix + zero-claim capability probe (desk); S2 single-node RTX 3080 Ti instrument-portability study under four hard gates AFTER the Mac claims table closes; S3 split study deferred to the Phase-3 second paper. P1-008's acceptance-bar answers are the reopening trigger. | Staged NVIDIA extension: desk-only appendix + capability probe now; the single-node RTX instrument-portability study only after the Mac claims table is green and Ed ratifies; split study explicitly deferred to the Phase-3 second paper. Evidence: S1 landed: NVML counter-mechanics appendix drafted (desk-only) + zero-claim rig capability probe recorded + borrow-window doc staleness fixed; S2 (post-Mac-table, Ed-ratified): the four Sol gates — live promotion + retention closure; counter mechanics + rate-aware pulse anchor; RTX-specific floors with the minimal battery; one bounded named-GPU-board-boundary result (wall cross-check only if the D-092 meter passes its own battery); A calibrated non-result at any gate is recorded as publishable evidence and stops escalation (no ad hoc smoothing). Authority: [2026-08-02 two-lens extension consult (Sol feasibility + Fable science advisory), magistrate synthesis in .desk/nvidia-extension/SYNTHESIS.md — ED RATIFIES the S2 gate](docs/run_reports/2026-08-01-desk-adjudication-session.md). Acceptance: [NVIDIA-PORTABILITY-01 acceptance](docs/process/state_kernel.json). Fence: No NVIDIA energy number enters the December paper's claims table; S2 never binds the submission; mixed-boundary sums are never presented as split totals (Consult synthesis: December claims table stays Mac-only (both lenses)). |
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-refusal-as-result.md:6544:5. Desk throughout: C7 reconciliation; MDE machinery; counter-mechanics
docs/strategy/2026-08-07-paper-portfolio/proposals/prop-tokenizer-honesty.md:448:| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
docs/run_reports/2026-07-30-paper-outline-v1.md:143:5. Desk throughout: C7 reconciliation; MDE machinery; counter-mechanics
docs/run_reports/2026-07-30-sweep-techniques.md:35:The real methods quarry of the six. GQA/MLA/GDN/Mamba2 on one H200; NVML at 50 ms with trapezoidal integration; 10–20 reps, 3 warmups, medians with published max-stddev (≤3%, typically <0.5%).
docs/run_reports/2026-07-30-sweep-techniques.md:37:**Adopt/adapt:** (i) **Internal dual-instrument cross-validation**: they validate sampled-power integrals against the independent NVML hardware energy counter and publish the agreement bound (2%, valid only for ops ≥200 ms). JouleWise's pre-wall-meter analogue: cross-check powermetrics integrals against an independent on-device channel (battery/SMC drain deltas over long windows) and publish the number with its validity domain. (ii) **Duration-conditional validity**: they name where the method breaks (<100 ms), the affected fraction (44% of prefill configs), and a declared fallback — slots directly into JouleWise's fail-closed gates as a minimum-window rule in units of powermetrics cadence. (iii) **Effect/noise ratio as a standard column** ("spread exceeds noise by 1.2–27×") plus their extra move: distinguishing "above floor" from "operationally meaningful." (iv) **Weight-controlled ablation** (same base weights, one variable changed via TransMLA) — for any JouleWise A/B, hold everything bit-identical and say so. (v) Max-stddev printed in figure captions. (vi) Mechanistic corroboration (rooflines) — corroborate energy splits with powermetrics' utilization/frequency channels so claims aren't single-signal. (vii) Pareto-frontier operating-point template.
docs/run_reports/2026-07-30-sweep-techniques.md:45:**Adopt/adapt (Khan):** model-based validation, not identity: fit wall = f(software channels), report MAE/RMSE/MAPE on held-out data with channel ablation (Haswell GAM: 1.7% MAPE — the literature benchmark for "good"). Lag-hunt via cross-correlation before comparing streams (they found 10–24 s lags). Autocorrelation-aware stats (subsample/block before fitting). ≥2-min warm-up (kills a ~10–12% thermal power drift they measured, 37→74 °C). Instrument-overhead audit (with/without sampler; <1.2% even at 1 kHz). And the **counter-mechanics checklist** — overflow period, update granularity/jitter, non-atomicity, missing timestamps — is exactly the audit nobody has run on powermetrics' internal counters.
docs/run_reports/2026-07-30-sweep-techniques.md:85:9. **powermetrics counter-mechanics audit** (Paper 3a). Run Khan's checklist against powermetrics itself: sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead (with/without sampler at each cadence) — the characterization nobody has published for Apple Silicon, and a citable contribution in its own right.
docs/run_reports/2026-07-11-rpt002-related-work-refresh.md:26:| `dualscale-2026` | Four authors; arXiv v3 dated 2026-04-03; arXiv-only preprint | Phase placement/per-phase DVFS confirmed; homogeneous 16xH100/two-node InfiniBand scope; energy is GPU-only 10 ms NVML, never node/cluster level. |
docs/run_reports/2026-07-11-rpt002-related-work-refresh.md:31:| `silicon-showdown-2026` | Two authors; v2 record with issued date 2026-05-01; arXiv-only preprint | Ecosystem-as-deployed comparison with unmatched runtime/artifact/precision stacks; PyNVML GPU-board versus powermetrics whole-SoC boundary; every repeated 23x headline flags those unmatched boundaries; no accuracy evaluation and no artifact release. |
docs/paper/related_work_draft.md:9:The Illusion of Power Capping in LLM Decode provides a stronger measurement template: it samples graphics processing unit (GPU) power, integrates the samples, repeats configurations, and checks the integral against a separate hardware energy counter, while explicitly limiting that check to operations long enough for the counter to be meaningful [IllusionPowerCapping]. <!-- 2026-07-30-sweep-techniques.md: the Illusion study uses sampled-power integration, repetitions, an independent NVML energy-counter cross-check, and a duration-conditional validity domain. --> However, its counter agreement, run-to-run variation, snapshot fallback, and timing alignment are not composed into a bound on the reported savings, and its long sweeps do not include a drift-control design [IllusionPowerCapping]. <!-- 2026-07-30-sweep-techniques.md: the sweep identifies uncomposed error terms and no drift control across long sweeps as the study's open lane. --> JouleWise treats those terms as inputs to a single claim decision rather than as separate caveats.
docs/paper/related_work_draft.md:11:Benchmark standards reinforce that measurement validity belongs in each run. MLPerf Power and the associated Standard Performance Evaluation Corporation (SPEC) methodology require a qualified external analyzer, uncertainty computed at the actual load, fixed measurement ranges, synchronized clocks, sufficiently long windows, invalid-sample accounting, and special handling for battery-backed systems [MLPerfPower]. <!-- 2026-07-30-sweep-techniques.md: MLPerf Power/SPEC requires load-specific analyzer uncertainty, fixed ranges, clock synchronization, minimum windows, per-window invalid-sample accounting, and neutralized battery charge flow. --> These rules are designed for direct power analyzers and data-center-style benchmarks; JouleWise translates their reject-on-missing-evidence discipline to a free software counter on consumer hardware. Apple-focused comparisons show why that translation matters: Silicon Showdown compares deployed ecosystems using a GPU-board boundary on one platform and a whole-system-on-chip software-counter boundary on Apple hardware, with unmatched runtimes and precision stacks and no comparison of model-output accuracy [SiliconShowdown]. <!-- 2026-07-11-rpt002-related-work-refresh.md: Silicon Showdown compares unmatched runtime/artifact/precision stacks across PyNVML GPU-board and powermetrics whole-SoC boundaries and includes no accuracy evaluation. --> JouleWise therefore names the measured boundary and prioritizes within-stack claims instead of treating unlike telemetry boundaries as interchangeable.
docs/paper/related_work_draft.md:15:Software-visible counters such as Intel's Running Average Power Limit (RAPL) counters and Apple's `powermetrics` make repeated energy experiments practical without a laboratory meter, but their readings remain outputs of a measurement system rather than ground truth. RAPL in Action shows that validation should model the relationship between software channels and wall power, search for lag before comparing streams, account for temporal correlation, warm the machine to reduce thermal drift, audit the sampler's overhead, and inspect counter mechanics such as update granularity, overflow, jitter, and timestamp behavior [RAPLInAction]. <!-- 2026-07-30-sweep-techniques.md: RAPL in Action contributes model-based wall validation, lag search, autocorrelation-aware analysis, warm-up, sampler-overhead measurement, and a counter-mechanics checklist. --> Jay and Ostapenco likewise compare software meters against wall power with controlled workloads and regression, finding that the gap changes with load rather than behaving as a constant offset; they also refuse component-level rankings where no reference exists [JayOstapenco]. <!-- 2026-07-30-sweep-techniques.md: Jay/Ostapenco regress wall power on software readings, find a load-dependent rather than constant gap, and decline claims where no reference validates subtotals. --> A wall meter can therefore test whole-machine totals, but it cannot by itself validate how a software trace divides that total between prompt processing and token generation [JayOstapenco]. <!-- 2026-07-30-sweep-techniques.md: the sweep states that wall metering validates totals only, while phase splits require a separate phase-attribution method. -->

exec
/bin/zsh -lc "nl -ba /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py | sed -n '47,180p'; nl -ba /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py | sed -n '650,805p'; nl -ba /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py | sed -n '2048,2089p'; nl -ba docs/specs/axi/sc_spec_decode_verdict.md | sed -n '55,90p'; nl -ba docs/JouleWise_Hardening_Proposal.md | sed -n '444,465p'; nl -ba docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md | sed -n '115,146p'; nl -ba docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md | sed -n '289,305p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
    47	DEFAULT_TEMP = 0.0
    48	DEFAULT_TOP_P = 1.0
    49	DEFAULT_MIN_P = 0.0
    50	DEFAULT_TOP_K = 0
    51	DEFAULT_XTC_PROBABILITY = 0.0
    52	DEFAULT_XTC_THRESHOLD = 0.0
    53	DEFAULT_MIN_TOKENS_TO_KEEP = 1
    54	DEFAULT_SEED = None
    55	DEFAULT_MODEL = "mlx-community/Llama-3.2-3B-Instruct-4bit"
    56	DEFAULT_QUANTIZED_KV_START = 5000
    57	
    58	
    59	def str2bool(string):
    60	    return string.lower() not in ["false", "f"]
    61	
    62	
    63	def setup_arg_parser():
    64	    """Set up and return the argument parser."""
    65	    parser = argparse.ArgumentParser(description="LLM inference script")
    66	    parser.add_argument(
    67	        "--model",
    68	        type=str,
    69	        help=(
    70	            "The path to the local model directory or Hugging Face repo. "
    71	            f"If no model is specified, then {DEFAULT_MODEL} is used."
    72	        ),
    73	        default=None,
    74	    )
    75	    parser.add_argument(
    76	        "--trust-remote-code",
    77	        action="store_true",
    78	        help="Enable trusting remote code for tokenizer",
    79	    )
    80	    parser.add_argument(
    81	        "--adapter-path",
    82	        type=str,
    83	        help="Optional path for the trained adapter weights and config.",
    84	    )
    85	    parser.add_argument(
    86	        "--extra-eos-token",
    87	        type=str,
    88	        default=(),
    89	        nargs="+",
    90	        help="Add tokens in the list of eos tokens that stop generation.",
    91	    )
    92	    parser.add_argument(
    93	        "--system-prompt",
    94	        default=None,
    95	        help="System prompt to be used for the chat template",
    96	    )
    97	    parser.add_argument(
    98	        "--prompt",
    99	        "-p",
   100	        default=DEFAULT_PROMPT,
   101	        help="Message to be processed by the model ('-' reads from stdin)",
   102	    )
   103	    parser.add_argument(
   104	        "--prefill-response",
   105	        default=None,
   106	        help="Prefill response to be used for the chat template",
   107	    )
   108	    parser.add_argument(
   109	        "--max-tokens",
   110	        "-m",
   111	        type=int,
   112	        default=DEFAULT_MAX_TOKENS,
   113	        help="Maximum number of tokens to generate",
   114	    )
   115	    parser.add_argument(
   116	        "--temp", type=float, default=DEFAULT_TEMP, help="Sampling temperature"
   117	    )
   118	    parser.add_argument(
   119	        "--top-p", type=float, default=DEFAULT_TOP_P, help="Sampling top-p"
   120	    )
   121	    parser.add_argument(
   122	        "--min-p", type=float, default=DEFAULT_MIN_P, help="Sampling min-p"
   123	    )
   124	    parser.add_argument(
   125	        "--top-k", type=int, default=DEFAULT_TOP_K, help="Sampling top-k"
   126	    )
   127	    parser.add_argument(
   128	        "--xtc-probability",
   129	        type=float,
   130	        default=DEFAULT_XTC_PROBABILITY,
   131	        help="Probability of XTC sampling to happen each next token",
   132	    )
   133	    parser.add_argument(
   134	        "--xtc-threshold",
   135	        type=float,
   136	        default=0.0,
   137	        help="Thresold the probs of each next token candidate to be sampled by XTC",
   138	    )
   139	    parser.add_argument(
   140	        "--min-tokens-to-keep",
   141	        type=int,
   142	        default=DEFAULT_MIN_TOKENS_TO_KEEP,
   143	        help="Minimum tokens to keep for min-p sampling.",
   144	    )
   145	    parser.add_argument(
   146	        "--seed",
   147	        type=int,
   148	        default=DEFAULT_SEED,
   149	        help="PRNG seed",
   150	    )
   151	    parser.add_argument(
   152	        "--ignore-chat-template",
   153	        action="store_true",
   154	        help="Use the raw prompt without the tokenizer's chat template.",
   155	    )
   156	    parser.add_argument(
   157	        "--use-default-chat-template",
   158	        action="store_true",
   159	        help="Use the default chat template",
   160	    )
   161	    parser.add_argument(
   162	        "--chat-template-config",
   163	        help="Additional config for `apply_chat_template`. Should be a dictionary of"
   164	        " string keys to values represented as a JSON decodable string.",
   165	        default=None,
   166	    )
   167	    parser.add_argument(
   168	        "--verbose",
   169	        type=str2bool,
   170	        default=True,
   171	        help="Log verbose output when 'True' or 'T' or only print the response when 'False' or 'F'",
   172	    )
   173	    parser.add_argument(
   174	        "--max-kv-size",
   175	        type=int,
   176	        help="Set the maximum key-value cache size",
   177	        default=None,
   178	    )
   179	    parser.add_argument(
   180	        "--prompt-cache-file",
   650	            if prev_tokens is not None:
   651	                prev_tokens = prev_tokens[: -max(num_draft - n, 1)]
   652	            _rewind_cache(num_draft, n)
   653	    finally:
   654	        _rewind_cache(num_draft, n)
   655	
   656	
   657	def stream_generate(
   658	    model: nn.Module,
   659	    tokenizer: Union[PreTrainedTokenizer, TokenizerWrapper],
   660	    prompt: Union[str, mx.array, List[int]],
   661	    max_tokens: int = 256,
   662	    draft_model: Optional[nn.Module] = None,
   663	    **kwargs,
   664	) -> Generator[GenerationResponse, None, None]:
   665	    """
   666	    A generator producing text based on the given prompt from the model.
   667	
   668	    Args:
   669	        model (nn.Module): The model to use for generation.
   670	        tokenizer (PreTrainedTokenizer): The tokenizer.
   671	        prompt (Union[str, mx.array, List[int]]): The input prompt string or
   672	          integer tokens.
   673	        max_tokens (int): The maximum number of tokens to generate.
   674	          Default: ``256``.
   675	        draft_model (Optional[nn.Module]): An optional draft model. If provided
   676	          then speculative decoding is used. The draft model must use the same
   677	          tokenizer as the main model. Default: ``None``.
   678	        kwargs: The remaining options get passed to :func:`generate_step`.
   679	          See :func:`generate_step` for more details.
   680	
   681	    Yields:
   682	        GenerationResponse: An instance containing the generated text segment and
   683	            associated metadata. See :class:`GenerationResponse` for details.
   684	    """
   685	    if not isinstance(tokenizer, TokenizerWrapper):
   686	        tokenizer = TokenizerWrapper(tokenizer)
   687	
   688	    if not isinstance(prompt, mx.array):
   689	        if isinstance(prompt, str):
   690	            # Try to infer if special tokens are needed
   691	            add_special_tokens = tokenizer.bos_token is None or not prompt.startswith(
   692	                tokenizer.bos_token
   693	            )
   694	            prompt = tokenizer.encode(prompt, add_special_tokens=add_special_tokens)
   695	        prompt = mx.array(prompt)
   696	
   697	    detokenizer = tokenizer.detokenizer
   698	
   699	    kwargs["max_tokens"] = max_tokens
   700	
   701	    if draft_model is None:
   702	        kwargs.pop("num_draft_tokens", None)
   703	        token_generator = generate_step(prompt, model, **kwargs)
   704	        # from_draft always false for non-speculative generation
   705	        token_generator = (
   706	            (token, logprobs, False) for token, logprobs in token_generator
   707	        )
   708	    else:
   709	        kwargs.pop("max_kv_size", None)
   710	        kwargs.pop("prompt_progress_callback", None)
   711	        token_generator = speculative_generate_step(
   712	            prompt, model, draft_model, **kwargs
   713	        )
   714	    with wired_limit(model, [generation_stream]):
   715	        tic = time.perf_counter()
   716	        for n, (token, logprobs, from_draft) in enumerate(token_generator):
   717	            if n == 0:
   718	                prompt_time = time.perf_counter() - tic
   719	                prompt_tps = prompt.size / prompt_time
   720	                tic = time.perf_counter()
   721	            if token in tokenizer.eos_token_ids:
   722	                break
   723	
   724	            detokenizer.add_token(token)
   725	            if (n + 1) == max_tokens:
   726	                break
   727	
   728	            yield GenerationResponse(
   729	                text=detokenizer.last_segment,
   730	                token=token,
   731	                logprobs=logprobs,
   732	                from_draft=from_draft,
   733	                prompt_tokens=prompt.size,
   734	                prompt_tps=prompt_tps,
   735	                generation_tokens=n + 1,
   736	                generation_tps=(n + 1) / (time.perf_counter() - tic),
   737	                peak_memory=mx.get_peak_memory() / 1e9,
   738	                finish_reason=None,
   739	            )
   740	
   741	        detokenizer.finalize()
   742	        yield GenerationResponse(
   743	            text=detokenizer.last_segment,
   744	            token=token,
   745	            logprobs=logprobs,
   746	            from_draft=from_draft,
   747	            prompt_tokens=prompt.size,
   748	            prompt_tps=prompt_tps,
   749	            generation_tokens=n + 1,
   750	            generation_tps=(n + 1) / (time.perf_counter() - tic),
   751	            peak_memory=mx.get_peak_memory() / 1e9,
   752	            finish_reason="stop" if token in tokenizer.eos_token_ids else "length",
   753	        )
   754	
   755	
   756	def generate(
   757	    model: nn.Module,
   758	    tokenizer: Union[PreTrainedTokenizer, TokenizerWrapper],
   759	    prompt: Union[str, List[int]],
   760	    verbose: bool = False,
   761	    **kwargs,
   762	) -> str:
   763	    """
   764	    Generate a complete response from the model.
   765	
   766	    Args:
   767	       model (nn.Module): The language model.
   768	       tokenizer (PreTrainedTokenizer): The tokenizer.
   769	       prompt (Union[str, List[int]]): The input prompt string or integer tokens.
   770	       verbose (bool): If ``True``, print tokens and timing information.
   771	           Default: ``False``.
   772	       kwargs: The remaining options get passed to :func:`stream_generate`.
   773	          See :func:`stream_generate` for more details.
   774	    """
   775	    if verbose:
   776	        print("=" * 10)
   777	
   778	    text = ""
   779	    for response in stream_generate(model, tokenizer, prompt, **kwargs):
   780	        if verbose:
   781	            print(response.text, end="", flush=True)
   782	        text += response.text
   783	
   784	    if verbose:
   785	        print()
   786	        print("=" * 10)
   787	        if len(text) == 0:
   788	            print("No text generated for this prompt")
   789	            return
   790	        print(
   791	            f"Prompt: {response.prompt_tokens} tokens, "
   792	            f"{response.prompt_tps:.3f} tokens-per-sec"
   793	        )
   794	        print(
   795	            f"Generation: {response.generation_tokens} tokens, "
   796	            f"{response.generation_tps:.3f} tokens-per-sec"
   797	        )
   798	        print(f"Peak memory: {response.peak_memory:.3f} GB")
   799	    return text
   800	
   801	
   802	def _left_pad_prompts(prompts, max_length=None):
   803	    if max_length is None:
   804	        max_length = max(len(p) for p in prompts)
   805	    return mx.array([[0] * (max_length - len(p)) + p for p in prompts])
  2048	                continue_final_message=has_prefill,
  2049	                add_generation_prompt=not has_prefill,
  2050	            )
  2051	            prompt = prompt[test_prompt.index("<query>") :]
  2052	        prompt = tokenizer.encode(prompt, add_special_tokens=False)
  2053	    else:
  2054	        prompt = tokenizer.encode(prompt)
  2055	
  2056	    if args.draft_model is not None:
  2057	        draft_model, draft_tokenizer = load(args.draft_model)
  2058	        if draft_tokenizer.vocab_size != tokenizer.vocab_size:
  2059	            raise ValueError("Draft model tokenizer does not match model tokenizer.")
  2060	    else:
  2061	        draft_model = None
  2062	    sampler = make_sampler(
  2063	        args.temp,
  2064	        args.top_p,
  2065	        args.min_p,
  2066	        args.min_tokens_to_keep,
  2067	        top_k=args.top_k,
  2068	        xtc_probability=args.xtc_probability,
  2069	        xtc_threshold=args.xtc_threshold,
  2070	        xtc_special_tokens=tokenizer.encode("\n") + list(tokenizer.eos_token_ids),
  2071	    )
  2072	    response = generate(
  2073	        model,
  2074	        tokenizer,
  2075	        prompt,
  2076	        max_tokens=args.max_tokens,
  2077	        verbose=args.verbose,
  2078	        sampler=sampler,
  2079	        max_kv_size=args.max_kv_size,
  2080	        prompt_cache=prompt_cache if using_cache else None,
  2081	        kv_bits=args.kv_bits,
  2082	        kv_group_size=args.kv_group_size,
  2083	        quantized_kv_start=args.quantized_kv_start,
  2084	        draft_model=draft_model,
  2085	        num_draft_tokens=args.num_draft_tokens,
  2086	    )
  2087	    if not args.verbose:
  2088	        print(response)
  2089	
    55	
    56	The reviewed installation is:
    57	
    58	`/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/`
    59	
    60	`mlx_lm/_version.py:3` records `0.31.3`; distribution metadata reports MLX
    61	`0.31.2`. The live controller independently emits package versions and roots,
    62	then verifies the source hashes before importing MLX.
    63	
    64	| Installed source | SHA-256 |
    65	|---|---|
    66	| `mlx_lm/__init__.py` | `f9ffa88772d26e537a98aa39ab16488a7a0d13cc1fac5d665376132c94b49608` |
    67	| `mlx_lm/_version.py` | `f0da9bc5c5c1bf21d576f7aa67b4eda887f1c7f0666746187b493e6831c4af6c` |
    68	| `mlx_lm/generate.py` | `270778ad53eaca55a8533d82e6752660fe5d2605c4aa0879b48a50a91f69345f` |
    69	| `mlx_lm/server.py` | `cdfcb4ac848636f9927851a0ec7a951584526530cb7832ba58049e4a9144db8b` |
    70	| `mlx_lm/models/qwen3_5.py` | `f0daa30bba5cb521c8bdfa7093101a544c6a37bbba09bca582288219cb04ae3a` |
    71	
    72	## Source-level answer
    73	
    74	### A. External draft model: generation yes; full AXI-SA observability no
    75	
    76	The pinned CLI exposes `--draft-model` and `--num-draft-tokens`
    77	(`mlx_lm/generate.py:211-220`). The low-level
    78	`speculative_generate_step(prompt, model, draft_model, ...)` accepts an
    79	external model and configured draft count (`mlx_lm/generate.py:473-487`),
    80	creates separate target and draft caches (`mlx_lm/generate.py:521-527`), and
    81	requires a trimmable target cache (`mlx_lm/generate.py:529-533`). The public
    82	`stream_generate` signature accepts `draft_model`
    83	(`mlx_lm/generate.py:657-677`) and dispatches to the speculative generator when
    84	that argument is non-null (`mlx_lm/generate.py:701-713`). The CLI separately
    85	loads the requested draft and checks tokenizer vocabulary size
    86	(`mlx_lm/generate.py:2056-2059`), then passes both `draft_model` and
    87	`num_draft_tokens` to generation (`mlx_lm/generate.py:2072-2085`). This is a
    88	real external-draft generation surface, subject to live execution of a
    89	specific compatible pair.
    90	
   444	### Phase 7 — Selective heterogeneous promotion
   445	
   446	**Objective:** Expand only after the reference path is proven.
   447	
   448	#### NVIDIA promotion order
   449	
   450	1. Live transport and host-key behavior.
   451	2. Remote lifecycle cleanup and timeout behavior.
   452	3. vLLM streaming/token-count truth; do not equate SSE chunks with tokenizer tokens.
   453	4. nvidia-smi cadence and averaging characterization.
   454	5. Raw-lineage strict validation for NVIDIA evidence.
   455	6. Host CPU/DRAM/NIC boundary treatment for transfer workloads.
   456	7. Same-boundary calibration and floor artifact.
   457	8. A small NVIDIA reference campaign.
   458	
   459	Only after these pass should NVIDIA be described as validated rather than fixture-first/provisional.
   460	
   461	#### Split-inference promotion order
   462	
   463	1. Reconfirm novelty positioning against current 2026 literature.
   464	2. Freeze the exact split estimand and baselines.
   465	3. Validate KV replay correctness and output identity.
   115	## Three strengthening moves (if kept)
   116	
   117	1. **Invert the paper: make the refusal the result, and drop the meter.** Kill the split-vs-monolithic
   118	   winner claim and contribution 4. Ship a *boundary-composability* paper: pre-register the composite
   119	   budget arithmetic before any collection; add the one cheap missing empirical input — a **GPU-side
   120	   cadence/averaging characterization** (pulse-train step-load on the 3080 Ti, no LLM, no Mac, closes
   121	   hardening Phase-7 item 4 and costs one non-quiet evening on owned hardware); then publish "the
   122	   two-boundary composite budget is ~N J against candidate effects of 10-200 J, therefore the split
   123	   comparison is REFUSED, and here is the exact operating domain where it would resolve (payload >= X GiB,
   124	   link <= Y Gb/s, board TDP <= Z W)." Falsifiable, entirely owned-hardware, and it makes the fail-closed
   125	   machinery do the most interesting work in the paper. This is the version that fits ICPE WIP.
   126	2. **Build a shared physical fiducial or declare its impossibility as the finding.** Replace the NTP-shaped
   127	   clock criterion with a cross-device *power-step* fiducial: a pre-registered train of fixed-size
   128	   transfers whose starts/stops appear as power steps on both endpoints, with the cross-clock bound derived
   129	   from observed step alignment rather than from a software clock. This is the only construction that
   130	   preserves continuity with D-078's actual mechanism. If it cannot produce a bound under 25% of the
   131	   shortest claimed interval, that failure is the headline — and a better one than a crossover plot.
   132	3. **Fix the runtime accounting and the two contradictions, then re-cost in the open.** State plainly that
   133	   the split stack is llama.cpp/GGUF and therefore a *new instrument* needing its own calibration regime
   134	   and floor mints, with the honest 8-12-window budget attached — or drop the real-split arm to future work
   135	   under D-092/C8's existing conditional framing. Separately: delete the sender/receiver wall floors from
   136	   contribution 2 (one meter cannot mint them), and add battery-charge neutralization with verified steady
   137	   state as a hard admission gate before any wall-boundary claim, per the MLPerf rule the draft already
   138	   cites.
   139	
   140	**Disposition recommendation:** do not fund as a second paper. Fund move 1 as a ~1-evening desk+bench
   141	probe; if the GPU cadence characterization comes back at 100 ms or better *and* a cross-device power-step
   142	bound lands under the 25% criterion, revisit. Otherwise this direction's correct home is a quantified
   143	future-work section in the MVP paper — which is exactly where D-092 already put it.
   289	   Retitle to "Does speculative decoding ever repay its energy at batch 1?" —
   290	   a question this instrument can actually answer, with a directional
   291	   floor-gated answer either way. Keep acceptance-vs-Δenergy as a secondary
   292	   descriptive figure with an honest prompt-level n.
   293	2. **Move the go/no-go evidence to the front and make it cheap.** Before any
   294	   runtime fork, run a *non-claim, daytime, wall-clock-only* spec-on/off timing
   295	   pilot on the 7B/0.5B pair with the stock pinned runtime (generation already
   296	   works — no instrumentation needed for tok/s). If spec-on is slower than
   297	   baseline, as the DSpark/DFlash smoke predicts, the energy answer is settled
   298	   at essentially zero cost and the whole fork/floor/AP build is never funded.
   299	   This is a two-hour desk task that currently sits *after* two to three weeks
   300	   of instrumentation work.
   301	3. **Fix the floor story explicitly, or change the primary metric.** Either
   302	   (a) name the `gross_request` floor-class build as a first-class work item,
   303	   fold it into D-117's U3 pinset-v2 scope so one mint effort serves both, and
   304	   restore the 10+40 member design; or (b) if that is too much, re-scope the
   305	   primary metric to `phase_energy_j.decode` with an explicit, pre-registered

exec
/bin/zsh -lc "nl -ba /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py | sed -n '180,225p'; stat -f '%N %z bytes' /Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit; shasum -a 256 /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/_version.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   180	        "--prompt-cache-file",
   181	        type=str,
   182	        default=None,
   183	        help="A file containing saved KV caches to avoid recomputing them",
   184	    )
   185	    parser.add_argument(
   186	        "--quantize-activations",
   187	        "-qa",
   188	        action="store_true",
   189	        help="Quantize activations using the same quantization config as the corresponding layer.",
   190	    )
   191	    parser.add_argument(
   192	        "--kv-bits",
   193	        type=int,
   194	        help="Number of bits for KV cache quantization. Defaults to no quantization.",
   195	        default=None,
   196	    )
   197	    parser.add_argument(
   198	        "--kv-group-size",
   199	        type=int,
   200	        help="Group size for KV cache quantization.",
   201	        default=64,
   202	    )
   203	    parser.add_argument(
   204	        "--quantized-kv-start",
   205	        help="When --kv-bits is set, start quantizing the KV cache "
   206	        "from this step onwards.",
   207	        type=int,
   208	        default=DEFAULT_QUANTIZED_KV_START,
   209	    )
   210	    parser.add_argument(
   211	        "--draft-model",
   212	        type=str,
   213	        help="A model to be used for speculative decoding.",
   214	        default=None,
   215	    )
   216	    parser.add_argument(
   217	        "--num-draft-tokens",
   218	        type=int,
   219	        help="Number of tokens to draft when using speculative decoding.",
   220	        default=3,
   221	    )
   222	    return parser
   223	
   224	
   225	# A stream on the default device just for generation
/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit 448 bytes
/Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit 448 bytes
/Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit 448 bytes
270778ad53eaca55a8533d82e6752660fe5d2605c4aa0879b48a50a91f69345f  /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py
f0da9bc5c5c1bf21d576f7aa67b4eda887f1c7f0666746187b493e6831c4af6c  /Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/_version.py

codex
# Execution-plan draft

These are non-claim feasibility probes. They require no JouleWise instrumentation, no quiet-Mac window, and no runtime fork. No files were changed while preparing the plans.

## Probe A — stock-runtime speculative-decoding pilot

Purpose: determine whether external-draft speculative decoding can beat ordinary greedy decoding on the pinned MLX stack before funding the K sweep, runtime fork, floors, or analysis plan.

Interpretation: `128/512` means exactly 128 or 512 emitted decode tokens at batch 1 from one frozen prompt. Runs that terminate early are invalid.

### Frozen configuration

- Runtime: `mlx-lm==0.31.3`, `mlx==0.31.2`.
- Targets, in order:

  1. `Qwen2.5-1.5B-Instruct-4bit`
  2. `Qwen2.5-7B-Instruct-4bit`

- Draft: `Qwen2.5-0.5B-Instruct-4bit`.
- Spec-on: `num_draft_tokens=3`.
- Spec-off: ordinary target-only generation.
- Greedy: temperature 0, top-p 1, min-p 0, top-k 0, XTC disabled.
- One frozen prompt, SHA-256 recorded. Suggested prompt:

  > Produce a numbered list from 1 through 1000. On each line write the integer, a colon, and the word measurement. Output nothing else and do not stop before 1000.

- One unscored validation/warm-up per arm and cell.
- Five timed runs per arm per target/length: 40 scored invocations total.
- Paired, alternating order: `OFF→ON`, `ON→OFF`, `OFF→ON`, `ON→OFF`, `OFF→ON`.

The installed API defines these CLI arguments, selects speculative generation only when `draft_model` is non-null, and reports generation tokens and wall-clock tok/s: [installed `generate.py`](/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:63), [speculative dispatch](/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:657), [reported tok/s](/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:784). The reviewed package hashes and provenance are already recorded in [the AXI-SC verdict](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/specs/axi/sc_spec_decode_verdict.md:55).

### Exact MLX commands

Set `N=128`, run the complete paired schedule, then repeat with `N=512`. `PROMPT_FILE` and `OUT` must resolve to the frozen custody paths.

```bash
MLXGEN=/Users/edr/code/JouleWise/.venv/bin/mlx_lm.generate
DRAFT=/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit
PROMPT_FILE=/absolute/custody/path/prompt.txt
N=128
```

1.5B spec-off:

```bash
"$MLXGEN" \
  --model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit \
  --prompt - \
  --max-tokens "$N" \
  --temp 0 \
  --top-p 1 \
  --min-p 0 \
  --top-k 0 \
  --xtc-probability 0 \
  --seed 0 \
  --verbose true \
  < "$PROMPT_FILE" > "$OUT" 2>&1
```

1.5B spec-on:

```bash
"$MLXGEN" \
  --model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit \
  --draft-model "$DRAFT" \
  --num-draft-tokens 3 \
  --prompt - \
  --max-tokens "$N" \
  --temp 0 \
  --top-p 1 \
  --min-p 0 \
  --top-k 0 \
  --xtc-probability 0 \
  --seed 0 \
  --verbose true \
  < "$PROMPT_FILE" > "$OUT" 2>&1
```

7B spec-off:

```bash
"$MLXGEN" \
  --model /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit \
  --prompt - \
  --max-tokens "$N" \
  --temp 0 \
  --top-p 1 \
  --min-p 0 \
  --top-k 0 \
  --xtc-probability 0 \
  --seed 0 \
  --verbose true \
  < "$PROMPT_FILE" > "$OUT" 2>&1
```

7B spec-on:

```bash
"$MLXGEN" \
  --model /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit \
  --draft-model "$DRAFT" \
  --num-draft-tokens 3 \
  --prompt - \
  --max-tokens "$N" \
  --temp 0 \
  --top-p 1 \
  --min-p 0 \
  --top-k 0 \
  --xtc-probability 0 \
  --seed 0 \
  --verbose true \
  < "$PROMPT_FILE" > "$OUT" 2>&1
```

### Record per invocation

- Run ID, UTC and monotonic start/end, target, mode, length, block, and order.
- Exact command and exit status.
- Package versions, Python version, `generate.py` SHA-256, Git HEAD.
- Model paths; `config.json`, tokenizer, and folded weight hashes.
- Prompt contents and hash.
- Parsed prompt tokens/tok/s, generation tokens/tok/s, and peak memory.
- Generated-text SHA-256 and whether paired on/off output is byte-identical.
- Whole-process elapsed time as a secondary diagnostic.
- AC/battery state, thermal-pressure state, and notable competing load.
- Raw stdout/stderr plus its SHA-256.

A scored pair is valid only if both commands exit zero, emit exactly `N` tokens, use the frozen identities, and produce identical greedy text. An output mismatch is a feasibility failure, not a speed result.

### Decision rule

For each target/length, compute five paired ratios:

`Rᵢ = spec_on_generation_tps / spec_off_generation_tps`.

Report every ratio, their median, range, and count below 1.0.

- **CLOSE negative:** for either 7B workload, all five valid ratios are below 1.0. This is the pre-registered operational meaning of “spec-on throughput is lower.” Close the pinned-stack energy question negative at the feasibility level and kill the K-manipulation/runtime-fork/floor/AP program at zero measurement cost.
- **SURVIVES:** both 7B lengths have median ratio above 1.0, at least four of five ratios above 1.0, and identical outputs throughout. This only permits consideration of the energy study; it does not demonstrate an energy saving or repair the existing observability verdict.
- **INCONCLUSIVE/NO-FUND:** mixed signs, parity within ordinary run variation, early EOS, identity mismatch, or runtime failures. Do not fund the energy build from ambiguous timing evidence. If desired, extend prospectively to `n=10` within the same two-hour ceiling; do not change the prompt or K after seeing results.

The closure is scoped to this pinned runtime, target/draft pair, batch 1, prompt, and lengths—not speculative decoding universally. This implements the review’s cheap front gate in [strengthening move 2](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:293).

### Custody and time

Use an immutable, out-of-repository directory such as:

`~/JouleWise-probe-custody/<UTC>-spec-decode-stock/`

Custody includes prompt, manifest, order schedule, all raw outputs, parsed CSV/JSONL, comparison summary, environment inventory, and `SHA256SUMS`. A later authorized turn may add only the summary and custody pointer to the repository.

Estimated time: 15 minutes preflight, 20–30 minutes for 1.5B, 45–70 minutes for 7B, and 15–25 minutes parsing/custody: approximately **1.5–2 hours**.

---

## Probe B — RTX 3080 Ti NVML cadence/averaging characterization

Purpose: empirically distinguish requested polling cadence from delivered sample cadence, underlying fresh-value cadence, and the temporal support/averaging behavior of reported board power.

### External gate

This plan assumes Ed has physical or SSH access to the 3080 Ti rig. Repository state still marks the borrow/access evidence and P1-006 NVIDIA telemetry checks pending in [the Phase-1 checklist](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/phase_1/phase_1_exit_checklist.md:329). Therefore execution is an **`[ED-EXTERNAL]` gate**. Without access, Probe B remains open; fixture or Mac evidence cannot substitute.

No LLM and no Mac are involved. The rig need not be globally quiet, but unrelated GPU jobs must be absent and thermal starting conditions controlled.

### Scripts shape

1. `pulse_load.py`

   - Uses an already-installed CUDA path—prefer PyTorch/CuPy; otherwise a prebuilt, hash-recorded minimal CUDA helper.
   - Selects the GPU by UUID.
   - Preallocates fixed matrices/buffers before measurement.
   - Produces high-utilization GEMM pulses without allocations during pulses.
   - Synchronizes CUDA at each transition.
   - Records host `CLOCK_MONOTONIC_RAW` timestamps, CUDA-event durations, achieved loop count, and transition uncertainty.
   - Always restores idle state in `finally`.

2. `sample_nvml.py`

   - Polls `nvmlDeviceGetPowerUsage` at absolute monotonic deadlines, initially every 5 ms.
   - Records timestamps immediately before and after every API call, using their midpoint as sample time and half-call-duration as timestamp uncertainty.
   - Records raw milliwatts, return code, temperature, clocks, utilization, P-state, and throttling reasons.
   - Queries instantaneous/average power fields separately if the installed driver exposes them; unsupported fields remain explicit `NOT_SUPPORTED`.

3. `run_cadence_probe.py`

   - Captures inventory and `nvidia-smi --help-query-gpu`.
   - Starts the direct-NVML sampler and one CLI sampler.
   - Runs the frozen pulse schedule.
   - Terminates both cleanly and verifies raw-line completeness.
   - Repeats requested `nvidia-smi -lms` intervals in seeded counterbalanced order.
   - Never silently installs dependencies or changes power limits, clocks, or fan controls.

4. `analyze_cadence.py`

   - Measures delivered polling intervals and call latency.
   - Detects repeated cached readings and estimates fresh-value update cadence.
   - Fits causal boxcar and first-order averaging models with latency.
   - Validates the selected model on held-out pulses.
   - Reports edge delay, temporal support, 10–90% rise/fall time, short-pulse attenuation, and energy-area recovery.
   - Emits a conservative GPU-edge support bound, `B_GPU`.

### Frozen protocol

1. Inventory:

   - GPU name, UUID, VBIOS, driver/NVML/CUDA versions.
   - OS/kernel, power limit, persistence mode, clocks, P-state, temperature, fan, and throttling reasons.
   - Whether cumulative board energy, `power.draw.instant`, or `power.draw.average` is supported.
   - Baseline process inventory proving no other GPU workload.

2. Stabilize:

   - Five minutes idle.
   - One 30-second unscored load.
   - Return to within 2 °C of the frozen starting-temperature band before scored trains.

3. Pulse train:

   - 15 s idle, 15 s steady load, 15 s idle to establish plateau amplitude.
   - ON durations `{50, 100, 200, 500, 1000, 2000, 5000}` ms.
   - Five appearances of every duration in a seeded shuffled order.
   - At least 3 s idle between pulses.
   - End with another 15 s plateau and idle segment.
   - Hold matrix shape, dtype, GPU clock policy, and load amplitude fixed.

4. Sampling conditions:

   - Direct NVML polling at 5 ms throughout.
   - Concurrent `nvidia-smi` runs at requested intervals `{10, 25, 50, 100, 250, 1000}` ms.
   - Three complete pulse trains per requested interval.
   - Counterbalance interval order; re-admit the temperature band between trains.

The CLI sampler should retain the project’s pinned fields:

```bash
nvidia-smi \
  --id=0 \
  --query-gpu=timestamp,power.draw,temperature.gpu,utilization.gpu,clocks.sm,pstate \
  --format=csv,noheader,nounits \
  -lms 100
```

Repeat with the other frozen `-lms` values. Direct NVML remains the higher-poll-rate comparator; neither stream is treated as ground truth.

### Derived quantities

Keep three concepts separate:

- **Delivery cadence:** when the process returns samples.
- **Fresh-value cadence:** when the underlying reported value demonstrably updates.
- **Temporal support:** the past interval over which a reading appears averaged or filtered.

For every sampler/rate, report:

- Median and p95 delivered inter-sample interval and API latency.
- Fraction of duplicated/cached readings.
- Median and p95 interval between fresh updates.
- Best-supported filter family, averaging width/time constant, lag, and uncertainty.
- Rise/fall asymmetry and held-out transition residual.
- Pulse-amplitude attenuation by duration.
- Integrated area recovery against the long-plateau reference.
- Sampler CPU cost and whether aggressive polling changes idle or steady-load power.

### Pass/fail and Phase-7 closure

Hardening Phase-7 item 4 is [“nvidia-smi cadence and averaging characterization”](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/JouleWise_Hardening_Proposal.md:444).

It closes when the real rig produces a hash-bound positive or negative characterization containing requested cadence, delivered cadence, fresh-value cadence, averaging/support behavior, lag, and a conservative `B_GPU`. Closure does **not** close Phase-7 items 1–3 or 5–8 and does not make NVIDIA claim-bearing.

- **PASS for possible future boundary work:** upper bounds on both fresh-value cadence and `B_GPU` are at most 100 ms; at least 95% of held-out edges fall inside `B_GPU`; missing/unsupported samples are below 1%; and the fitted behavior is stable across repetitions.
- **FAIL/negative characterization:** effective updates or temporal support exceed 100 ms, behavior cannot be bounded, required power fields are unsupported, pulses are irreproducible, or held-out edges violate the proposed bound. Item 4 still closes negatively, but short-stage NVIDIA attribution and the split direction are refused.
- **INCONCLUSIVE:** access loss, competing GPU use, thermal non-admission, malformed raw traces, or insufficient repeated transitions. Item 4 stays open.

### Consequence for future two-boundary work

This probe supplies only the GPU term. A future two-boundary claim still needs a shared physical power-step fiducial and a bound for the other endpoint and cross-device alignment.

The admission equation should be:

`B_composite = B_GPU + B_other_endpoint + B_cross_device`

and require:

`B_composite < 0.25 × shortest_claimed_interval`.

Therefore:

- If `B_GPU` alone is already at least 25% of a candidate interval, that interval is mechanically impossible and must be refused.
- If Probe B passes, it merely keeps a later cross-device fiducial experiment alive; it does not establish the composite bound.
- GPU-board NVML still excludes host CPU, DRAM, and NIC transfer work. Cadence success cannot repair that physical-boundary mismatch; future transfer cells require host-inclusive metering or must remain explicit board-only lower bounds.

This matches the review’s rule: favorable GPU cadence plus a later cross-device bound under 25% is required before reconsideration [review disposition](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:140).

### Custody and time

Use an immutable directory such as:

`~/JouleWise-probe-custody/<UTC>-3080ti-nvml-cadence/`

Retain:

- Frozen protocol and pulse schedule.
- All four scripts and hashes.
- Environment/GPU inventory.
- Raw CLI CSV and direct-NVML JSONL.
- Transition/CUDA-event logs.
- stdout/stderr and exit-status manifests.
- Derived cadence tables, fitted-model parameters, residuals, and plots.
- Phase-7 closure verdict and future-boundary statement.
- Complete `SHA256SUMS`.

Estimated time: 20–30 minutes access/inventory, 20–30 minutes load calibration, 60–90 minutes scored trains, and 30–45 minutes analysis/custody: approximately **2–3 hours, one non-quiet evening**.
tokens used
101,887
# Execution-plan draft

These are non-claim feasibility probes. They require no JouleWise instrumentation, no quiet-Mac window, and no runtime fork. No files were changed while preparing the plans.

## Probe A — stock-runtime speculative-decoding pilot

Purpose: determine whether external-draft speculative decoding can beat ordinary greedy decoding on the pinned MLX stack before funding the K sweep, runtime fork, floors, or analysis plan.

Interpretation: `128/512` means exactly 128 or 512 emitted decode tokens at batch 1 from one frozen prompt. Runs that terminate early are invalid.

### Frozen configuration

- Runtime: `mlx-lm==0.31.3`, `mlx==0.31.2`.
- Targets, in order:

  1. `Qwen2.5-1.5B-Instruct-4bit`
  2. `Qwen2.5-7B-Instruct-4bit`

- Draft: `Qwen2.5-0.5B-Instruct-4bit`.
- Spec-on: `num_draft_tokens=3`.
- Spec-off: ordinary target-only generation.
- Greedy: temperature 0, top-p 1, min-p 0, top-k 0, XTC disabled.
- One frozen prompt, SHA-256 recorded. Suggested prompt:

  > Produce a numbered list from 1 through 1000. On each line write the integer, a colon, and the word measurement. Output nothing else and do not stop before 1000.

- One unscored validation/warm-up per arm and cell.
- Five timed runs per arm per target/length: 40 scored invocations total.
- Paired, alternating order: `OFF→ON`, `ON→OFF`, `OFF→ON`, `ON→OFF`, `OFF→ON`.

The installed API defines these CLI arguments, selects speculative generation only when `draft_model` is non-null, and reports generation tokens and wall-clock tok/s: [installed `generate.py`](/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:63), [speculative dispatch](/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:657), [reported tok/s](/Users/edr/code/JouleWise/.venv/lib/python3.13/site-packages/mlx_lm/generate.py:784). The reviewed package hashes and provenance are already recorded in [the AXI-SC verdict](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/specs/axi/sc_spec_decode_verdict.md:55).

### Exact MLX commands

Set `N=128`, run the complete paired schedule, then repeat with `N=512`. `PROMPT_FILE` and `OUT` must resolve to the frozen custody paths.

```bash
MLXGEN=/Users/edr/code/JouleWise/.venv/bin/mlx_lm.generate
DRAFT=/Users/edr/jw_models/mlx-community/Qwen2.5-0.5B-Instruct-4bit
PROMPT_FILE=/absolute/custody/path/prompt.txt
N=128
```

1.5B spec-off:

```bash
"$MLXGEN" \
  --model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit \
  --prompt - \
  --max-tokens "$N" \
  --temp 0 \
  --top-p 1 \
  --min-p 0 \
  --top-k 0 \
  --xtc-probability 0 \
  --seed 0 \
  --verbose true \
  < "$PROMPT_FILE" > "$OUT" 2>&1
```

1.5B spec-on:

```bash
"$MLXGEN" \
  --model /Users/edr/jw_models/mlx-community/Qwen2.5-1.5B-Instruct-4bit \
  --draft-model "$DRAFT" \
  --num-draft-tokens 3 \
  --prompt - \
  --max-tokens "$N" \
  --temp 0 \
  --top-p 1 \
  --min-p 0 \
  --top-k 0 \
  --xtc-probability 0 \
  --seed 0 \
  --verbose true \
  < "$PROMPT_FILE" > "$OUT" 2>&1
```

7B spec-off:

```bash
"$MLXGEN" \
  --model /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit \
  --prompt - \
  --max-tokens "$N" \
  --temp 0 \
  --top-p 1 \
  --min-p 0 \
  --top-k 0 \
  --xtc-probability 0 \
  --seed 0 \
  --verbose true \
  < "$PROMPT_FILE" > "$OUT" 2>&1
```

7B spec-on:

```bash
"$MLXGEN" \
  --model /Users/edr/jw_models/mlx-community/Qwen2.5-7B-Instruct-4bit \
  --draft-model "$DRAFT" \
  --num-draft-tokens 3 \
  --prompt - \
  --max-tokens "$N" \
  --temp 0 \
  --top-p 1 \
  --min-p 0 \
  --top-k 0 \
  --xtc-probability 0 \
  --seed 0 \
  --verbose true \
  < "$PROMPT_FILE" > "$OUT" 2>&1
```

### Record per invocation

- Run ID, UTC and monotonic start/end, target, mode, length, block, and order.
- Exact command and exit status.
- Package versions, Python version, `generate.py` SHA-256, Git HEAD.
- Model paths; `config.json`, tokenizer, and folded weight hashes.
- Prompt contents and hash.
- Parsed prompt tokens/tok/s, generation tokens/tok/s, and peak memory.
- Generated-text SHA-256 and whether paired on/off output is byte-identical.
- Whole-process elapsed time as a secondary diagnostic.
- AC/battery state, thermal-pressure state, and notable competing load.
- Raw stdout/stderr plus its SHA-256.

A scored pair is valid only if both commands exit zero, emit exactly `N` tokens, use the frozen identities, and produce identical greedy text. An output mismatch is a feasibility failure, not a speed result.

### Decision rule

For each target/length, compute five paired ratios:

`Rᵢ = spec_on_generation_tps / spec_off_generation_tps`.

Report every ratio, their median, range, and count below 1.0.

- **CLOSE negative:** for either 7B workload, all five valid ratios are below 1.0. This is the pre-registered operational meaning of “spec-on throughput is lower.” Close the pinned-stack energy question negative at the feasibility level and kill the K-manipulation/runtime-fork/floor/AP program at zero measurement cost.
- **SURVIVES:** both 7B lengths have median ratio above 1.0, at least four of five ratios above 1.0, and identical outputs throughout. This only permits consideration of the energy study; it does not demonstrate an energy saving or repair the existing observability verdict.
- **INCONCLUSIVE/NO-FUND:** mixed signs, parity within ordinary run variation, early EOS, identity mismatch, or runtime failures. Do not fund the energy build from ambiguous timing evidence. If desired, extend prospectively to `n=10` within the same two-hour ceiling; do not change the prompt or K after seeing results.

The closure is scoped to this pinned runtime, target/draft pair, batch 1, prompt, and lengths—not speculative decoding universally. This implements the review’s cheap front gate in [strengthening move 2](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/strategy/2026-08-07-paper-portfolio/reviews/rev-spec-decode-energy.md:293).

### Custody and time

Use an immutable, out-of-repository directory such as:

`~/JouleWise-probe-custody/<UTC>-spec-decode-stock/`

Custody includes prompt, manifest, order schedule, all raw outputs, parsed CSV/JSONL, comparison summary, environment inventory, and `SHA256SUMS`. A later authorized turn may add only the summary and custody pointer to the repository.

Estimated time: 15 minutes preflight, 20–30 minutes for 1.5B, 45–70 minutes for 7B, and 15–25 minutes parsing/custody: approximately **1.5–2 hours**.

---

## Probe B — RTX 3080 Ti NVML cadence/averaging characterization

Purpose: empirically distinguish requested polling cadence from delivered sample cadence, underlying fresh-value cadence, and the temporal support/averaging behavior of reported board power.

### External gate

This plan assumes Ed has physical or SSH access to the 3080 Ti rig. Repository state still marks the borrow/access evidence and P1-006 NVIDIA telemetry checks pending in [the Phase-1 checklist](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/phase_1/phase_1_exit_checklist.md:329). Therefore execution is an **`[ED-EXTERNAL]` gate**. Without access, Probe B remains open; fixture or Mac evidence cannot substitute.

No LLM and no Mac are involved. The rig need not be globally quiet, but unrelated GPU jobs must be absent and thermal starting conditions controlled.

### Scripts shape

1. `pulse_load.py`

   - Uses an already-installed CUDA path—prefer PyTorch/CuPy; otherwise a prebuilt, hash-recorded minimal CUDA helper.
   - Selects the GPU by UUID.
   - Preallocates fixed matrices/buffers before measurement.
   - Produces high-utilization GEMM pulses without allocations during pulses.
   - Synchronizes CUDA at each transition.
   - Records host `CLOCK_MONOTONIC_RAW` timestamps, CUDA-event durations, achieved loop count, and transition uncertainty.
   - Always restores idle state in `finally`.

2. `sample_nvml.py`

   - Polls `nvmlDeviceGetPowerUsage` at absolute monotonic deadlines, initially every 5 ms.
   - Records timestamps immediately before and after every API call, using their midpoint as sample time and half-call-duration as timestamp uncertainty.
   - Records raw milliwatts, return code, temperature, clocks, utilization, P-state, and throttling reasons.
   - Queries instantaneous/average power fields separately if the installed driver exposes them; unsupported fields remain explicit `NOT_SUPPORTED`.

3. `run_cadence_probe.py`

   - Captures inventory and `nvidia-smi --help-query-gpu`.
   - Starts the direct-NVML sampler and one CLI sampler.
   - Runs the frozen pulse schedule.
   - Terminates both cleanly and verifies raw-line completeness.
   - Repeats requested `nvidia-smi -lms` intervals in seeded counterbalanced order.
   - Never silently installs dependencies or changes power limits, clocks, or fan controls.

4. `analyze_cadence.py`

   - Measures delivered polling intervals and call latency.
   - Detects repeated cached readings and estimates fresh-value update cadence.
   - Fits causal boxcar and first-order averaging models with latency.
   - Validates the selected model on held-out pulses.
   - Reports edge delay, temporal support, 10–90% rise/fall time, short-pulse attenuation, and energy-area recovery.
   - Emits a conservative GPU-edge support bound, `B_GPU`.

### Frozen protocol

1. Inventory:

   - GPU name, UUID, VBIOS, driver/NVML/CUDA versions.
   - OS/kernel, power limit, persistence mode, clocks, P-state, temperature, fan, and throttling reasons.
   - Whether cumulative board energy, `power.draw.instant`, or `power.draw.average` is supported.
   - Baseline process inventory proving no other GPU workload.

2. Stabilize:

   - Five minutes idle.
   - One 30-second unscored load.
   - Return to within 2 °C of the frozen starting-temperature band before scored trains.

3. Pulse train:

   - 15 s idle, 15 s steady load, 15 s idle to establish plateau amplitude.
   - ON durations `{50, 100, 200, 500, 1000, 2000, 5000}` ms.
   - Five appearances of every duration in a seeded shuffled order.
   - At least 3 s idle between pulses.
   - End with another 15 s plateau and idle segment.
   - Hold matrix shape, dtype, GPU clock policy, and load amplitude fixed.

4. Sampling conditions:

   - Direct NVML polling at 5 ms throughout.
   - Concurrent `nvidia-smi` runs at requested intervals `{10, 25, 50, 100, 250, 1000}` ms.
   - Three complete pulse trains per requested interval.
   - Counterbalance interval order; re-admit the temperature band between trains.

The CLI sampler should retain the project’s pinned fields:

```bash
nvidia-smi \
  --id=0 \
  --query-gpu=timestamp,power.draw,temperature.gpu,utilization.gpu,clocks.sm,pstate \
  --format=csv,noheader,nounits \
  -lms 100
```

Repeat with the other frozen `-lms` values. Direct NVML remains the higher-poll-rate comparator; neither stream is treated as ground truth.

### Derived quantities

Keep three concepts separate:

- **Delivery cadence:** when the process returns samples.
- **Fresh-value cadence:** when the underlying reported value demonstrably updates.
- **Temporal support:** the past interval over which a reading appears averaged or filtered.

For every sampler/rate, report:

- Median and p95 delivered inter-sample interval and API latency.
- Fraction of duplicated/cached readings.
- Median and p95 interval between fresh updates.
- Best-supported filter family, averaging width/time constant, lag, and uncertainty.
- Rise/fall asymmetry and held-out transition residual.
- Pulse-amplitude attenuation by duration.
- Integrated area recovery against the long-plateau reference.
- Sampler CPU cost and whether aggressive polling changes idle or steady-load power.

### Pass/fail and Phase-7 closure

Hardening Phase-7 item 4 is [“nvidia-smi cadence and averaging characterization”](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/JouleWise_Hardening_Proposal.md:444).

It closes when the real rig produces a hash-bound positive or negative characterization containing requested cadence, delivered cadence, fresh-value cadence, averaging/support behavior, lag, and a conservative `B_GPU`. Closure does **not** close Phase-7 items 1–3 or 5–8 and does not make NVIDIA claim-bearing.

- **PASS for possible future boundary work:** upper bounds on both fresh-value cadence and `B_GPU` are at most 100 ms; at least 95% of held-out edges fall inside `B_GPU`; missing/unsupported samples are below 1%; and the fitted behavior is stable across repetitions.
- **FAIL/negative characterization:** effective updates or temporal support exceed 100 ms, behavior cannot be bounded, required power fields are unsupported, pulses are irreproducible, or held-out edges violate the proposed bound. Item 4 still closes negatively, but short-stage NVIDIA attribution and the split direction are refused.
- **INCONCLUSIVE:** access loss, competing GPU use, thermal non-admission, malformed raw traces, or insufficient repeated transitions. Item 4 stays open.

### Consequence for future two-boundary work

This probe supplies only the GPU term. A future two-boundary claim still needs a shared physical power-step fiducial and a bound for the other endpoint and cross-device alignment.

The admission equation should be:

`B_composite = B_GPU + B_other_endpoint + B_cross_device`

and require:

`B_composite < 0.25 × shortest_claimed_interval`.

Therefore:

- If `B_GPU` alone is already at least 25% of a candidate interval, that interval is mechanically impossible and must be refused.
- If Probe B passes, it merely keeps a later cross-device fiducial experiment alive; it does not establish the composite bound.
- GPU-board NVML still excludes host CPU, DRAM, and NIC transfer work. Cadence success cannot repair that physical-boundary mismatch; future transfer cells require host-inclusive metering or must remain explicit board-only lower bounds.

This matches the review’s rule: favorable GPU cadence plus a later cross-device bound under 25% is required before reconsideration [review disposition](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/strategy/2026-08-07-paper-portfolio/reviews/rev-split-inference-metrology.md:140).

### Custody and time

Use an immutable directory such as:

`~/JouleWise-probe-custody/<UTC>-3080ti-nvml-cadence/`

Retain:

- Frozen protocol and pulse schedule.
- All four scripts and hashes.
- Environment/GPU inventory.
- Raw CLI CSV and direct-NVML JSONL.
- Transition/CUDA-event logs.
- stdout/stderr and exit-status manifests.
- Derived cadence tables, fitted-model parameters, residuals, and plots.
- Phase-7 closure verdict and future-boundary statement.
- Complete `SHA256SUMS`.

Estimated time: 20–30 minutes access/inventory, 20–30 minutes load calibration, 60–90 minutes scored trains, and 30–45 minutes analysis/custody: approximately **2–3 hours, one non-quiet evening**.
