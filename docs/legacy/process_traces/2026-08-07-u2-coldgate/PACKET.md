Reading additional input from stdin...
OpenAI Codex v0.146.1
--------
workdir: /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
model: gpt-5.6-sol
provider: openai
approval: never
sandbox: workspace-write [workdir, /tmp, $TMPDIR]
reasoning effort: xhigh
reasoning summaries: none
session id: 019fde17-07ee-7351-85ac-d0304de45a22
--------
user
U2 COLD-GATE PACKET ASSEMBLY (read-only; no writes; final message = the packet). Rule 11 requires a cold-gate ruling on the D-102 successor engine before it can land. Assemble the packet MECHANICALLY — a cold Fable instance and an Opus contract-lens refuter will rule on it with NO loop context, so it must be self-contained and must NOT argue for a conclusion.
SOURCES: docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md (the 12 open questions with recommendations) + the implementation on branch impl/d117-u2-successor (fetch origin; read the diff; find all 12 COLD-GATE-Qn tags and report what each one currently implements) + D-102 and D-116 in docs/decision_log.md + docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md finding L4.
PACKET STRUCTURE: (1) THE QUESTION for the gate, stated neutrally in one paragraph; (2) BINDING CONTEXT — quote the governing clauses of D-102/D-116 IN FULL, to the period, including any that cut AGAINST the implemented choices (this is a hard requirement: selective quotation has been a recorded packet defect three times); (3) for EACH of the 12 questions: the question, the brief's recommendation, what the code currently does at its COLD-GATE-Qn tag with file:line, the strongest argument FOR and the strongest argument AGAINST, and what would change if the gate ruled the other way; (4) UNSWEPT EVIDENCE — state explicitly what was NOT examined, so the gate defers rather than assumes (this is a recorded packet-quality rule); (5) the decision the gate must return per question. Do NOT recommend an outcome; the packet must read the same whichever way it rules.
codex
I’ll assemble this as an evidence packet only: inspect the repository gates and workspace state, resolve the successor branch without altering the worktree, then trace every `COLD-GATE-Qn` tag and quote the full governing decision clauses. I’ll keep all conclusions neutral and put only the completed packet in the final response.
exec
/bin/zsh -lc 'git status --short --branch && rg -n "ACTIVE_STOP_CARD|Current Project Status|Known Workspace State|What Is Next" RUN_STATE.md && rg -n "Current Queue|Do-Not-Do-Yet|Do Not Do Yet|D-117|U2" TASK_QUEUE.md && rg -n "Mission M0|M0" docs/agent_playbook.md && rg -n "D-102|D-116" docs/decision_log.md' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## main...origin/main
 M CLAIMS_STATUS.md
 M PROJECT_STATUS.md
 M README.md
 M WINDOW_STATUS.md
 M docs/decision_log.md
2026:12. If an `ACTIVE_STOP_CARD` exists below, it overrides every normal
2061:## ACTIVE_STOP_CARD
2200:## Current Project Status
2774:## Known Workspace State
96:Current Queue region is the sole live work-selection view.
213:## Current Do-Not-Do-Yet List
306:## Current Queue
26:1. Run Mission M0 (preflight) — always.
50:## Mission M0: Preflight (every session)
472:The M0 step-6 handoff list, plus: if you changed an adapter or bundle
127:| D-102 | CAL-BRACKET-D079-01 pins: budget cap 0.001275166090593858 s (99% two-draw prediction ceiling 0.012093166090593858 s, blind n=19 derivation), exact-identity-epoch freshness with prospective re-derivation triggers, never-zero allowance max(drift, screen) embedded once, decimal-source numeric semantics with labelled presentation values | accepted (magistrate ratification, lead-replayed arithmetic, 2026-08-01) |
135:| D-110 | Mint #1 retroactively NON-CLAIM-BEARING (taint-and-remint, Ed ruling on sweep finding RT-1: floors embed zero allowance where D-102 pin 3 mandates +max(drift, 0.010818 s)); re-mint gated on D-109 landing + artifact issuance + validator pin widening; RT-2 dependency edge minted (MINT-GENERALIZE-01 hard-blocked on CAL-BRACKET-D079-01); night-consult 7B-mint license suspended; RT-5 recorded: all four PASSED window verdicts untainted | accepted (Ed 2026-08-03, sweep-triggered) |
141:| D-116 | D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (seq 76 / head 08456d50…; issued sha 316113960c…; 30/2/6 dispositions); D-110 condition (b) SATISFIED → MINT-GENERALIZE-01 unblocked for re-mint; two-cold-gate history (plan HELD → consumer impl + gauntlet → bytes PROCEED, sequencing HOLD resolved by consumer-first merge); window_metrologyB calibration fiducials in completeness record are NOT a D-113 violation | executed (Fable magistrate, 2026-08-06; Ed pre-authorized) |
6339:## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics
7072:D-116 is retained unchanged as historical context. Current rule ownership:
7073:D-116.
7090:  a faithful IMPLEMENTATION of D-102 (no threshold/freshness
7091:  amendment); it supplies the authority/universe rulings D-102 left
7155:   artifact (D-102's prospective rule).
7162:8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38
7188:never-zero allowance of ZERO where D-102 pin 3 mandates
7196:D-102 epoch; the taint is confined to floor artifacts.
7585:## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)
7600:**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).
7606:**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.
7629:   `A_s = max(observed_drift_s, 0.010818)` allowance (D-102 pin 3)
7667:   D-102 successor-artifact packet; results/methods prose placeholders.

codex
The worktree already contains unrelated modified files, including the decision log, so I’m preserving it untouched. I’m now separating the live decision text from branch implementation evidence and will flag any branch/ref freshness limitation explicitly under “Unswept Evidence.”
exec
/bin/zsh -lc "sed -n '2061,2245p' RUN_STATE.md
sed -n '2774,2865p' RUN_STATE.md
sed -n '200,370p' TASK_QUEUE.md
sed -n '50,120p' docs/agent_playbook.md
sed -n '1,220p' docs/orchestration.md
git branch --all --no-color
git remote -v
git show-ref | rg 'impl/d117-u2-successor|refs/remotes/origin'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
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

**2026-08-07 supersession (D-117):** the historical a10/re-mint and old
C/D plan are retired. Claim authority can now arise only from the
prospective alpha, beta, and gamma windows; the separately named Window C
characterization night remains Ed ruling #1. The table above is retained
unchanged as dated collection history, not present claim authority.

Window B's cause is established and is NOT a clock problem: a GPU DVFM
power ramp that the rectangular-pulse fiducial estimator aliases into an
apparent onset shift (93.28% of the drift; the wall-clock term moved the
OPPOSITE way, −0.201464 ms). D-079 clause 3 adds a pre-flight screen that
detects it in the ~4-minute pre-calibration, with cause-removal (never
outcome-selection) retry semantics.

**Corrected floor figures — the old ones must not be repeated.** a10's
**absolute** floors are **3.823787 J prefill / 3.592138 J decode**,
INCLUDING the 0.652272 J whole-window drift allowance. The 3.17 / 2.94 J
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
  `QA-10A-JOIN-OMISSION`, `QA-10B-EXISTING-RETRY`) is folded in. Any
  further change means editing the kernel and then running
  `python3 scripts/gen_state.py` — never hand-editing the generated
  regions.
- (2026-07-25, historical) `main` and `origin/main` were at `c3e2647`,
  the PR #85 merge; PR #79's repair and PR #85's SCREEN+BUDGET
  implementation both landed with green final PR-head CI.
- The generated state-kernel blocks are authoritative for work selection.
  Hand-authored `RUN_STATE.md` and `TASK_QUEUE.md` text remains authoritative
  only for its own factual, policy, and historical domains;
  `docs/decision_log.md` remains the policy authority, exit checklists own
  phase completion, and evidence artifacts own scientific truth.
- Retained corpus and session scratchpad evidence are immutable.

## Historical Next-Work Snapshot (superseded 2026-07-15)

The following 2026-07-13 narrative is retained for chronology only. It is not
a live queue or restart instruction; the generated work-selection region is
the sole selector.

The comprehensive whole-project audit is the declared gate (Ed,
2026-07-13): method proposal pending Ed's approval, then the audit runs
and its findings are adjudicated before any further feature work. After
that: Window A in the first clean quiet-machine window (C-019/P2-015-SMOKE,
then P2-015 floors, P2-006 baselines), with post-audit [AGENT] heads
P2-050 adjudication, SITE-02, and P2-027 publication prep outside quiet
windows. `TASK_QUEUE.md` remains the ordering authority.

Hardware-gated (unchanged): 2K/2L (P1-006; NV-GATE-2 additions from
C-027 apply at live promotion), wall meter (P1-003), topology (P1-004),
calendar mapping (P1-008).

## Reference Decisions And Blockers (non-selection context)

These pointers retain external-dependency context but do not rank or select
work. The generated region controls task selection.

- Supervisor approval and scope pending (P1-001, R-001 — mitigation
  holding); gates FULL D-016 closure.
- D-013 SSH-controlled vs co-resident controller comparison — SHELF,
  trigger: first 2K live session (validation cell rides that session).
- Empirical corpus for the 0.40 GPU-idle contamination threshold — SHELF,
  trigger: Window-A calibration data exists (P2-015 output feeds it).
- `dvfm_states` slimming option — SHELF, trigger: bundle-size pain during
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
removed from this table. Of the six, only `MINT-GENERALIZE-01` and
`SUPERSESSION-DUP-REFUSAL-01` remain LIVE as of 2026-08-02: the
gauntlet trio retired with PR #93 and `MANIFEST-CONTRAST-01` with
PR #95 (see the completed table).
`COOLDOWN-JOIN-DA1-01` followed on 2026-07-31 (D-093), in the same pass
that retired `P2-015` to the completed table and closed
`QUEUE-RECONCILE-01`; both of those staged rows were removed too. It was
short-lived as a live row: DA-1 closed later the same day inside the
gauntlet's commit 2 and `COOLDOWN-JOIN-DA1-01` is now retired to the
completed table (PR #91, `67d268a`).

**The rows that remain below are STAGED, not live**, and stay staged by
magistrate scope decision 2026-07-30 (the P2/P3/P4 residue is not
competing for this window's selection). Work selection is the generated
region below; nothing here competes with it until the magistrate folds a
row into `docs/process/state_kernel.json` and runs
`python3 scripts/gen_state.py`. They are recorded here — hand-authored,
outside the generated markers — so the 2026-07-29/30 arc's owed rows
cannot be lost between the ruling and the kernel refresh (kernel refresh
is magistrate-owned).

Sources: `docs/decision_log.md` D-083..D-093; `docs/council_log.md` C-039
addendum + addendum II; the delegated related-work sweep
(`docs/run_reports/2026-07-30-sweep-techniques.md`); the
`splitwise_decode_v1` campaign doc §2
(`docs/phase_2/splitwise_decode_campaign.md`, on main since `27ffc91`).

| ID | Priority | Lane | Task | Evidence / Acceptance | Authority |
|---|---|---|---|---|---|
| QA-1-COOLDOWN-LAUNDER | P0 Safety | [AGENT] | **CLOSED at `16c7af0` (FIX-10, 2026-07-30).** The fail-open declared-occurrence edge the FIX-9 delta re-audit found (a member declaring `bundle_ids: ["x", "x"]` with only one usable `physical_members` row resolved via the one-row fast path without the supersession matcher) is closed by declared-occurrence tallying; both defect-shaped regressions failed pre-fix and pass post-fix. The FIX-10 delta re-audit confirmed this shape closed while finding the two successor edges now carried as the LIVE kernel rows `QA-10A-JOIN-OMISSION` and `QA-10B-EXISTING-RETRY` (folded 2026-07-30; see the generated region below). | Closed: fast path licensed only at declared count exactly 1; regressions in `SupersessionAwareCooldownJoinTests`; lead-verified 48/48 focused. | [D-086/D-088](docs/decision_log.md); FIX-10 delta re-audit 2026-07-30 |
| POWERMETRICS-AUDIT-01 | P3 Research Expansion | [QUIET-MAC] | powermetrics counter-mechanics audit (Khan checklist): sampling-interval jitter, window-alignment semantics, update granularity, instrument self-overhead per cadence. Citable: unpublished for Apple Silicon. | Khan-style per-property table, each property bounded or recorded unmeasurable, plus self-overhead per cadence. | [Sweep-techniques #9](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MDE-ADOPT-01 | P2 Next Slice | [AGENT] | Powered MDE for the **repeatability arm** + workload-sizing inversion: replace the informal repeatability statistic with δ\* = 2.80·σ_D/√m (α = 0.05, power 0.80) over ABBA pair differences, and size the pilot with m ≥ 2.80²·σ_D²/δ². Desk work on existing data; makes the ad hoc "+5 J claim-side" principled. | Floor computation carries a powered MDE for the repeatability arm with its α and power stated. **Hard boundary, do not cross:** this does NOT apply to the systematic arm — RSS composition is valid only for independent random components, and RSS-ing a worst-case attribution bound as if it were an SD is anti-conservative. `max(repeatability, corner) + drift` stays. | [Sweep-techniques top-10 #1 + §5](docs/run_reports/2026-07-30-sweep-techniques.md) |
| MIN-WINDOW-RULE-01 | P2 Next Slice | [AGENT] | Minimum-window rule + loop-to-60 s for short phases: declare a duration-conditional validity domain (N× the powermetrics cadence; SPEC's 60 s reached by looping the workload if shorter) and **fail-close** phases below it. Attacks the attribution-dominated 6–14 J floors directly, since edge error amortizes with window length. | A declared, enforced validity domain with phases below it refused rather than reported. Note the coupling: changing workload duration resizes the science, so any loop-to-60 s change is a pre-registration change and therefore Ed's call (see `FLOOR-WORKLOAD-SIZING-01`). | [Sweep-techniques top-10 #3](docs/run_reports/2026-07-30-sweep-techniques.md) |
| BATTERY-CROSSCHECK-01 | P2 Next Slice | [QUIET-MAC] | Internal dual-instrument cross-check **before** any wall meter: validate powermetrics integrals against an independent on-device channel (battery/SMC drain over long windows; channel-sum vs package reconciliation) and publish the agreement bound **with its validity domain**. Narrows "never externally validated" without a purchase. | A published agreement bound with its stated validity domain. Caution carried from the same memo: embedded telemetry (BMC/SMC) must NOT be treated as a trusted second reference without its own characterization — the bound is a cross-check, not a calibration. | [Sweep-techniques top-10 #4](docs/run_reports/2026-07-30-sweep-techniques.md) |
| REFUSAL-VOCAB-RATIFY-01 | P1 Phase Gate | [AGENT] + magistrate | Ratification question, deferred out of cold gate F1: reordering the separation-validation phases would **alter refusal precedence**, which D-087 placed in "vocabulary-ratification territory". The refusal vocabulary needs a ruling before any reorder is attempted. | A ruling on the refusal vocabulary and precedence, recorded in the decision log; only then may a phase reorder be proposed. | [D-087](docs/decision_log.md); refusal-scope spec v1 (`ea16730`, on main via PR #88) |
| MOCK-SAMPLER-PROV-01 | P4 Polish | [AGENT] | (Cold-gate finding **F2**.) The mock runtime should emit **truthful sampler provenance**; today the integration tests rewrite metadata to inject a sampler — a test-honesty item. | Mock runtime emits real sampler provenance and the metadata-rewriting test helper is deleted. Mitigated meanwhile: mock bundles are already refused at claim binding by `MOCK_TELEMETRY_CLAIM_REFUSAL`, so there is no claim exposure. | [D-087](docs/decision_log.md) (F2 disposition) |
| COOLDOWN-JOIN-FIXTURE-01 | P4 Polish | [AGENT] | (FIX-9 delta re-audit finding **QA-2**.) No repository fixture composes the **real** supersession validator/reader with the cooldown join; the FIX-9 regressions stub the reader, which is adequate for join/matcher behavior and insufficient as custody-path closure. | A real validator-reader-join fixture exercising the composed custody path end-to-end. | [C-039 addendum](docs/council_log.md); FIX-9 delta re-audit QA-2 |
| MINT-TOCTOU-01 | P4 Polish | [AGENT] | (Audit finding **Audit-F1**, adjudicated QUEUE.) TOCTOU between the mint's pre-check and its authenticated artifact read. Requires concurrent mutation of a frozen input; a different signature from the FIX-8 defect class. | Either the read is made atomic with the pre-check, or the exposure is recorded as an accepted limitation with its precondition stated. | Session ledger, staged-mint section; D-087 sibling dispositions |
| FLOOR-ARTIFACT-SHA-PIN-01 | P2 Next Slice | [AGENT] | Review finding **B2** — artifact-SHA pin. **Detail owed:** the finding's text lives in the review packet, not in the session ledger; whoever promotes this row must restate the defect from the packet before it can be READY per the Ready/Shelf rule. | Not yet acceptance-specified — promote to READY only after the B2 finding text is recovered and restated. | Session ledger, F2 disposition paragraph ("register at bookkeeping with … B2 artifact-SHA-pin row") |
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

## Mission M1: Slice 2N — Pre-Hardware Hardening (queue P2-007)

**Gate:** none. **Spec + acceptance:** `docs/phase_2/phase_2_plan.md`
Slice 2N. This mission adds the code-level route for each work item,
sourced from the 2026-07-05 external code review. Line numbers are from
commit `ae48abe` — re-locate by symbol name if the files have moved on.

Read first: `phase_2_plan.md` Slice 2N + Cross-Slice Contracts;
`joulewise/bundle.py`, `controller.py`, `reduce.py`, `interfaces.py`
(skim whole files — they are small and the invariants interlock).

2N is one mission but NOT one sitting: it touches adapter interfaces,
controller timing, reducer behavior, report parsing, CLI, schema export,
and validation policy. Work item-by-item with the suite green after each,
and land it as roughly three commits so a failure bisects cleanly:

- **Commit A — the adapter seam:** 2N.1 (RunContext + raw evidence),
  2N.2 (measured-window boundaries). Both touch controller/interfaces.
- **Commit B — the read layer:** 2N.8 (BundleReader), with 2N.4 (rail
  contract), 2N.7 (report alignment), and 2N.6's structured read
  failures implemented on top of it. 2N.6's CLI verb rides along.
- **Commit C — schema + metrics:** 2N.5 (schema round-trip), 2N.3
  (token-count fallback), 2N.9 (v0.2 compatibility note).

If a session ends mid-slice, a completed commit group is a clean
handoff point — say which group landed in `RUN_STATE.md`.

Per-item detail (each item = tests green before the next; items 1+2
change the controller/adapter contract and go first):

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

The following policy text is the R2-ratified section, landed verbatim per
audit work order WO-022 (`docs/reviews/2026-07-13-comprehensive-audit/`).

SPEND GUARDRAILS (capstone benchmark bands) — provisional calibration constants; review after two completed arcs; sunset at capstone submission.

1. ACCOUNTING SOURCE. Sol spend: `codex-usage` local accounting (the standing snapshot convention), corroborated by codex-run-v3 manifest `token_usage` rows where populated. The extraction window must cover the full arc — sum incremental snapshots for multi-day arcs; a single trailing-24h view is insufficient. Fable spend: estimated from local usage accounting; each snapshot names its method and price-table version. Price table v2026-07 (pinned until amended): GPT-5.6-sol $5/$30 per M in/out, cached input $0.50; Fable 5 $10/$50, cache reads $1. All figures are estimates, not billing truth, and are recorded as such. Missing data is recorded as `accounting_unknown`, never as zero.

2. DENOMINATOR AND CACHED-TOKEN TREATMENT. Token bands count total tokens (cached + uncached, all directions) exactly as codex-usage reports them — cached tokens are never excluded (exclusion invites cache-heavy gaming). Dollar figures apply cached pricing honestly. Cross-family aggregate ceilings bind in combined estimated dollars, because raw cross-family token sums are not commensurable (C-028: Sol ~180x the token volume, Fable ~3.4x the cost).

  c027-council-review
  c027-int-docs
  c027-int-p2040
  c027-spec-wave
  c028-integration
+ claude/cs-pedagogy-ai-cf3aed
  claude/magical-jones-79e5f4
  impl/ap-edit
  impl/audit-s1
  impl/audit-s2
  impl/audit-s3
  impl/audit-s5
  impl/audit-wave
  impl/cal-rebracket
  impl/ci002
  impl/collection-retry-thermal
  impl/cooldown-gauntlet
  impl/d100-bii-binding
+ impl/d117-u1-ledger-session
+ impl/d117-u2-successor
+ impl/d117-u3-pinset-v2
+ impl/d117-u4-regression
+ impl/d117-u8-readiness
  impl/doc008-kernel
  impl/doc009
  impl/floor-label
  impl/floor-label-clean
  impl/floor-mint
  impl/int-findings
  impl/manifest-contrast-v3
  impl/met-dangler-disposition
  impl/met001
  impl/metrology-campaigns
  impl/mint-tool
  impl/neg8-estimand
  impl/neg8-refcorpus
  impl/neg8-screen-budget
  impl/nvgate2-codenow
  impl/p0-instrument-repair
  impl/p2037
  impl/p2038
  impl/p2039
  impl/p2040-core
  impl/p2040-io-nv2
  impl/p2040-remainder
  impl/p2041
  impl/p2041-vetted
  impl/p2042
  impl/p2043
  impl/p2044
  impl/p2045
  impl/p2046a
+ impl/paper-mvp-complete
  impl/repro001
  impl/repro002
  impl/rpt001
  impl/rpt002
  impl/slice-cursor
  impl/verdict-occurrence
* main
  stream/test-audit
  work/extraction-diag
  worktree-wf_74b33c13-c1c-1
  worktree-wf_74b33c13-c1c-2
  worktree-wf_74b33c13-c1c-3
+ worktree-wf_d910c76a-264-2
  remotes/origin/HEAD -> origin/main
  remotes/origin/advisor-status-site
  remotes/origin/affine-ladder
  remotes/origin/bundle-pack
  remotes/origin/c027-council-review
  remotes/origin/c027-int-docs
  remotes/origin/c027-int-p2040
  remotes/origin/c027-spec-wave
  remotes/origin/capture-hardening
  remotes/origin/envelope-gate
  remotes/origin/impl/advisor-refresh
  remotes/origin/impl/ap-edit
  remotes/origin/impl/audit-integration
  remotes/origin/impl/audit-s1
  remotes/origin/impl/audit-s2
  remotes/origin/impl/audit-s3
  remotes/origin/impl/audit-s4
  remotes/origin/impl/audit-s5
  remotes/origin/impl/audit-wave
  remotes/origin/impl/audit-wo021
  remotes/origin/impl/audit-wo027
  remotes/origin/impl/axi-sa
  remotes/origin/impl/axi-sb
  remotes/origin/impl/axi-sc
  remotes/origin/impl/ci002
  remotes/origin/impl/codex-fast-tier
  remotes/origin/impl/coldgate-validator
  remotes/origin/impl/collection-retry-thermal
  remotes/origin/impl/cooldown-gauntlet
  remotes/origin/impl/cooldown-gauntlet-c3
  remotes/origin/impl/d079-issuance
  remotes/origin/impl/d100-bii-binding
  remotes/origin/impl/d117-u1-ledger-session
  remotes/origin/impl/d117-u2-successor
  remotes/origin/impl/d117-u3-pinset-v2
  remotes/origin/impl/d117-u4-regression
  remotes/origin/impl/d117-u8-readiness
  remotes/origin/impl/doc008-kernel
  remotes/origin/impl/doc009
  remotes/origin/impl/floor-label
  remotes/origin/impl/floor-label-clean
  remotes/origin/impl/floor-mint
  remotes/origin/impl/int-findings
  remotes/origin/impl/issuance-consumer
  remotes/origin/impl/ledger-bootstrap
  remotes/origin/impl/manifest-contrast-v3
  remotes/origin/impl/met-dangler-disposition
  remotes/origin/impl/met001
  remotes/origin/impl/metrology-campaigns
  remotes/origin/impl/microdelta-f2-hardening
  remotes/origin/impl/mint-generalize
  remotes/origin/impl/mint-tool
  remotes/origin/impl/neg8-estimand
  remotes/origin/impl/neg8-refcorpus
  remotes/origin/impl/nvgate2-codenow
  remotes/origin/impl/nvidia-retention-flake
  remotes/origin/impl/p0-instrument-repair
  remotes/origin/impl/p2037
  remotes/origin/impl/p2038
  remotes/origin/impl/p2038-drain
  remotes/origin/impl/p2038-drain2
  remotes/origin/impl/p2039
  remotes/origin/impl/p2040-core
  remotes/origin/impl/p2040-io-nv2
  remotes/origin/impl/p2040-remainder
  remotes/origin/impl/p2041
  remotes/origin/impl/p2041-vetted
  remotes/origin/impl/p2042
  remotes/origin/impl/p2043
  remotes/origin/impl/p2044
  remotes/origin/impl/p2045
  remotes/origin/impl/p2046a
  remotes/origin/impl/p2049
  remotes/origin/impl/paper-draft-v1
  remotes/origin/impl/paper-mvp-complete
  remotes/origin/impl/queue-registration
  remotes/origin/impl/quiet-guard
  remotes/origin/impl/repro001
  remotes/origin/impl/repro002
  remotes/origin/impl/rpt001
  remotes/origin/impl/rpt002
  remotes/origin/impl/site-02
  remotes/origin/impl/site-readme
  remotes/origin/impl/site-tabs
  remotes/origin/impl/slice-cursor
  remotes/origin/impl/split-ap
  remotes/origin/impl/test-speed
  remotes/origin/impl/validator-rootpins
  remotes/origin/impl/verdict-occurrence
  remotes/origin/jw-mixed-generators
  remotes/origin/main
  remotes/origin/p2-021-drift-sentinels
  remotes/origin/p2015-floor
  remotes/origin/p2029-uncertainty
  remotes/origin/p2030-ordering
  remotes/origin/p2031-token-norm
  remotes/origin/p2032-campaign-packs
  remotes/origin/p2033-claims-linter
  remotes/origin/p2034-broad-packs
  remotes/origin/rq-registry
  remotes/origin/rqvar-design-sketch
  remotes/origin/runner-hash-check
  remotes/origin/scope-headline
  remotes/origin/stats-registry
  remotes/origin/stream/2k-nvidia
  remotes/origin/stream/2m-campaign-tooling
  remotes/origin/stream/critique-response
  remotes/origin/stream/d014-uncertainty
  remotes/origin/stream/doc007-docs
  remotes/origin/stream/kv-size-helper
  remotes/origin/stream/kv-spike-301
  remotes/origin/stream/p2-008-mock-telemetry
  remotes/origin/stream/p2-009-rich-telemetry
  remotes/origin/stream/p2013-integrity
  remotes/origin/strict-era-fix
  remotes/origin/suite-substrate
  remotes/origin/tokenizer-id-widening
  remotes/origin/window-a-capture
origin	https://github.com/mpmdw/JouleWise (fetch)
origin	https://github.com/mpmdw/JouleWise (push)
399ffebdf96d883857fa9effdb579e0e09b0857d refs/heads/impl/d117-u2-successor
e74cc03723dae5810a0aaad1c913ad94261a7eb3 refs/remotes/origin/HEAD
2cfe51f8c9946ce1e8360def9541211f45f5985b refs/remotes/origin/advisor-status-site
cd36e2ca21eb38c0c47709c6752bb17899174eca refs/remotes/origin/affine-ladder
88382bf44cd45fce6a9db591273819ad14676213 refs/remotes/origin/bundle-pack
0a5c5e68d25cf1865b90195c876e394cd2aa17ab refs/remotes/origin/c027-council-review
9cdeb5db8f4bf0742dd0b926fca367d309ea2005 refs/remotes/origin/c027-int-docs
71365d419a139dede9df6524a8cc1ff3b5886705 refs/remotes/origin/c027-int-p2040
f25864e17c62509e439e09133772152536ff0c4f refs/remotes/origin/c027-spec-wave
f7c4599a0897aa6bd818af010be88be7d71f11bc refs/remotes/origin/capture-hardening
9b12ef76d54a70757290dd0597b252737c9ffc2e refs/remotes/origin/envelope-gate
db5f8df082e8a5db04be2d269c5ac16d3a3b0aef refs/remotes/origin/impl/advisor-refresh
0b79fbc27b4989e081283b1d6de46a6ebd12d790 refs/remotes/origin/impl/ap-edit
3f9eee2542204dbf231579de16aadbe8034116f2 refs/remotes/origin/impl/audit-integration
f664d69df0452a31034d2d4b20841f7bebc9b75e refs/remotes/origin/impl/audit-s1
b23b262d1489d646b423fd6c71a944925e7547b8 refs/remotes/origin/impl/audit-s2
3e9c60bf1436f89edd840cea5ec7884d85a37b90 refs/remotes/origin/impl/audit-s3
7b1299cbc3350aac9e57c9ed9cddee4ff6ee297b refs/remotes/origin/impl/audit-s4
b1f3aac9e9ab9d8142ef8d4b70567d9976e3a355 refs/remotes/origin/impl/audit-s5
dd2c9f1b91041f265509eb5dbeec2fecd1e6c63b refs/remotes/origin/impl/audit-wave
c7ee7cac43349e5efb2463ebd2466606ee6e582f refs/remotes/origin/impl/audit-wo021
3e0e928b998551fc52b642fdee648946ca056114 refs/remotes/origin/impl/audit-wo027
0914374f5d2cafb5ab02a82bf94a4d72ab681166 refs/remotes/origin/impl/axi-sa
7c90093b42839dad823c0badbdef92c392e3bb78 refs/remotes/origin/impl/axi-sb
646fc91af1a293a07e228aede6d523abb88515f8 refs/remotes/origin/impl/axi-sc
a5f10491b344bd643a10de94b2d42c010bbec402 refs/remotes/origin/impl/ci002
e8f10425644cb8af82da561cdb713b004b24d437 refs/remotes/origin/impl/codex-fast-tier
0bea908b43261a14386dda3868294e5f5b9ea3f1 refs/remotes/origin/impl/coldgate-validator
6037d78075e6ff72ae2f0ad8f33ef66080077589 refs/remotes/origin/impl/collection-retry-thermal
a9b9d4a6bf7d36f74819698990103b1706204a54 refs/remotes/origin/impl/cooldown-gauntlet
6070ac43f86639d78b11886032af79e1f82fad96 refs/remotes/origin/impl/cooldown-gauntlet-c3
d85b4f9e3c73c582ee19c460eed2d1c997f4a5ac refs/remotes/origin/impl/d079-issuance
751e6eea680d0fef37cccb9e9d3218b5e3be9d7d refs/remotes/origin/impl/d100-bii-binding
1cf7a42048a5bfe3841b699c430bf6ebc7cd0664 refs/remotes/origin/impl/d117-u1-ledger-session
399ffebdf96d883857fa9effdb579e0e09b0857d refs/remotes/origin/impl/d117-u2-successor
454f77795f5ed2f1841055a7ce125e1456f583de refs/remotes/origin/impl/d117-u3-pinset-v2
35ba641f049b043668b2a45b8005ca94c83b061f refs/remotes/origin/impl/d117-u4-regression
6b497d78c529829fab54ce72dc80c081a7038dd3 refs/remotes/origin/impl/d117-u8-readiness
f16b83e15e0f8a180c25858dbd3eeca314d10af5 refs/remotes/origin/impl/doc008-kernel
5efce5b17482975c76791211c8557ffcf0653cb0 refs/remotes/origin/impl/doc009
060c4070b56e430f686eae03ec298454cb4fd086 refs/remotes/origin/impl/floor-label
397242cb0232331024271e50fa5dedc8cab20eaa refs/remotes/origin/impl/floor-label-clean
dd86d2b2f46361b303ebe45dae8aa5ffc6209ca9 refs/remotes/origin/impl/floor-mint
0cb15591b808a0a28757e9fcfcbe154d2d55d296 refs/remotes/origin/impl/int-findings
71bf5ceec25c16982a33f398b4a4b9f21d549662 refs/remotes/origin/impl/issuance-consumer
f08158e9f6b7cd0e8cbefd00445f385505156dc7 refs/remotes/origin/impl/ledger-bootstrap
e94d4a7a5e92177e74c077a5647fd0dc59f56eb1 refs/remotes/origin/impl/manifest-contrast-v3
05d99b65c1954c845f483628754ec67aed8dc3fe refs/remotes/origin/impl/met-dangler-disposition
ae5faf48db886d2f5861396de87e50a38d4430a7 refs/remotes/origin/impl/met001
a93a2c646eb31d4bf953fd16843db334927529e0 refs/remotes/origin/impl/metrology-campaigns
3e251bfcc4f4ccd8b6b3e80eb4699e73d9d0b1cf refs/remotes/origin/impl/microdelta-f2-hardening
4e94e7059b637a46d07c128a262f5e386ef3998d refs/remotes/origin/impl/mint-generalize
707f76ea3ec067584bc928b0057b4f4e19446ad1 refs/remotes/origin/impl/mint-tool
8eef6eec05d7385415bf878fb3df96edc7b8e421 refs/remotes/origin/impl/neg8-estimand
c891ef8b010a5ed872713473b4a598a6962939ca refs/remotes/origin/impl/neg8-refcorpus
10e0ad2a2d5943d8c6c31a08476cd908fd3fe099 refs/remotes/origin/impl/nvgate2-codenow
87fb1437580b4a797d5861d9f3600ca28e368c13 refs/remotes/origin/impl/nvidia-retention-flake
56647a6f6cda7fc004fc72c7c27312faeb04f3a7 refs/remotes/origin/impl/p0-instrument-repair
36475563c6a3f21062be8fe1379e1b95a16d17c1 refs/remotes/origin/impl/p2037
dd245eb53a1623cb8968a970e6ec62fb46baa624 refs/remotes/origin/impl/p2038
1fa05e3fe603991de957300da2cd744d30f37524 refs/remotes/origin/impl/p2038-drain
f13c10986c06a47d6fc62513f94cd1eab9e0cb29 refs/remotes/origin/impl/p2038-drain2
769e5abd8af80aa49f8040d28788d09a5e756f7c refs/remotes/origin/impl/p2039
d39d4b366c8235202376d4233380d289ed6fe40e refs/remotes/origin/impl/p2040-core
c7440e91e1f592b352477e4422d085bedec486e6 refs/remotes/origin/impl/p2040-io-nv2
5558160a96c7b986800b874ef47414acaf3b3340 refs/remotes/origin/impl/p2040-remainder
5135c1d21cd51ac7b110ae6be4224c57827a019f refs/remotes/origin/impl/p2041
5f1f1613fea647354121938948d8d46de746332b refs/remotes/origin/impl/p2041-vetted
12cb4e0aeb6a11d947f6f36efceb4a5601dc2e99 refs/remotes/origin/impl/p2042
359641ee1a559a7d7d784ea736b86f2a676b5eea refs/remotes/origin/impl/p2043
dc1ab95a456ab7780c0d0f9831a28579118f520a refs/remotes/origin/impl/p2044
0186dd6dd5ee5b85b75db49e69432ea4d4e677f0 refs/remotes/origin/impl/p2045
5ba272758a6897d76694a86175bf83240e4cc670 refs/remotes/origin/impl/p2046a
9e0b0dc3360d88a2d5d4c210d682d89e4105679b refs/remotes/origin/impl/p2049
ee4f1a5829ac7a692de79450f52625f81f358abe refs/remotes/origin/impl/paper-draft-v1
d9b8c5fdd44a66a0a9f993f52c2fd3b9838be643 refs/remotes/origin/impl/paper-mvp-complete
f650d282b0f8b672e34412c44f5040996b2dd66f refs/remotes/origin/impl/queue-registration
83572a257af7baedfd11be6552d9e78cc9271f77 refs/remotes/origin/impl/quiet-guard
a63b25119f672ebda4273c43a1572a362b3d87f2 refs/remotes/origin/impl/repro001
cb597854718fe639ac894b3fa53f162ac683cc3f refs/remotes/origin/impl/repro002
06f9be08ba157ea5ea3893d946594000970b5a9c refs/remotes/origin/impl/rpt001
b8b70afadb67ba8eaa6f3abff48047e7a78aaa33 refs/remotes/origin/impl/rpt002
5363ca3a2e3f4adf1fcc4c8bf25ce971af1cbaee refs/remotes/origin/impl/site-02
05002b1b543d3f152f32b98c08a6a8b54135e5d9 refs/remotes/origin/impl/site-readme
3a9c297d36aea2f980627a20735c3ba93b1b1854 refs/remotes/origin/impl/site-tabs
fdb311f4042db63f2e6266e4272ca475a47a3383 refs/remotes/origin/impl/slice-cursor
2f505db3c451b66501112ab0dd84678d0c3e4d22 refs/remotes/origin/impl/split-ap
61c7d2ca143fc63f40103ec5d7fec480cb008ddb refs/remotes/origin/impl/test-speed
5b229f64af824e3e174e39775c9316ed2510b3b7 refs/remotes/origin/impl/validator-rootpins
63797697b49937a05cb4dcdf13d88c693f96e845 refs/remotes/origin/impl/verdict-occurrence
9b5bfe075baa3c69bf541fd12400f50236728e72 refs/remotes/origin/jw-mixed-generators
e74cc03723dae5810a0aaad1c913ad94261a7eb3 refs/remotes/origin/main
4edda47350d03e722fc35f1034183324c1cd1ebb refs/remotes/origin/p2-021-drift-sentinels
b66548157d5d4aea822ae30ddab6a0d4236501fe refs/remotes/origin/p2015-floor
d27745159b72a5bb38d1792c8f3b62d42f375d2c refs/remotes/origin/p2029-uncertainty
fe3e4b540496d04809dbaa521fa804151018e58b refs/remotes/origin/p2030-ordering
d4a1fbee4bdc59aba363900fd35fa9cb89560cac refs/remotes/origin/p2031-token-norm
957c4d807a69ff55b40f27707b86c9bb459878fc refs/remotes/origin/p2032-campaign-packs
a4c7d58ec1271479b9df14a2e55b14fb594dce4d refs/remotes/origin/p2033-claims-linter
faac77bc1331b6bcf919e9e6f77e56f1f5b0b445 refs/remotes/origin/p2034-broad-packs
f0f4dd3c240a412bd75ca8c069f7c5a166702acb refs/remotes/origin/rq-registry
f4e8236135a71727f27fcc140ed7d33dd78f6636 refs/remotes/origin/rqvar-design-sketch
d61eebbf9077cb9e41e1aef8d5bf41051281d64c refs/remotes/origin/runner-hash-check
3f4d656358e1221ac4ce54a1497276c4164639e0 refs/remotes/origin/scope-headline
8197b0588d795fe09497b2662f162ce9a4b126bf refs/remotes/origin/stats-registry
5ff9839bd9a6b67ef0517a3b3de2ef5c86c2ccb6 refs/remotes/origin/stream/2k-nvidia
4e2526a7c20e0ed084a2b5b467d7bbaa29f0c4d8 refs/remotes/origin/stream/2m-campaign-tooling
ad5a06eb9fbdf76e39e37bb05e54b69f58de30f5 refs/remotes/origin/stream/critique-response
441fab3a4b563a6d254700b49a0921885d7a5b35 refs/remotes/origin/stream/d014-uncertainty
f4d7db517661fd4c6387738a94dd7f759cf43ed2 refs/remotes/origin/stream/doc007-docs
9ef47c0e2d0fe9cbb2156dc0f4dfc252cae9433e refs/remotes/origin/stream/kv-size-helper
b80bf4f637ec88334ea256a2be1cd46b07f1e8a7 refs/remotes/origin/stream/kv-spike-301
f3cec33b1cf839c302b52762aa8b975d4c56cff3 refs/remotes/origin/stream/p2-008-mock-telemetry
e08746d6cd48e05ccf39d99ff952fa3ab17dd050 refs/remotes/origin/stream/p2-009-rich-telemetry
4f0d7bcb88ce3f4ffb039d4a1e2ea2a92f903c09 refs/remotes/origin/stream/p2013-integrity
c91d7b3ae223d2da90d6e2f7563a5a62b7c32c76 refs/remotes/origin/strict-era-fix
fdcf80053c9b8079100f1be890c4d7822643059d refs/remotes/origin/suite-substrate
c9c4272e4c82d4e79dce02d7598322cfa594c663 refs/remotes/origin/tokenizer-id-widening
db54cc2631a3307002e56f2f323aabd1eb1112eb refs/remotes/origin/window-a-capture

codex
A literal fetch is blocked because this checkout’s shared Git metadata is mounted read-only (`FETCH_HEAD: Operation not permitted`). I can still inspect the existing local and remote-tracking refs, which both point to `399ffebd…`; I’m attempting a read-only remote ref check so the packet can distinguish verified freshness from cached-ref evidence.
exec
/bin/zsh -lc 'git ls-remote origin refs/heads/impl/d117-u2-successor' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 exited 128 in 0ms:
fatal: unable to access 'https://github.com/mpmdw/JouleWise/': Could not resolve host: github.com

web search: 
web search: https://github.com/mpmdw/JouleWise/tree/impl/d117-u2-successor
exec
/bin/zsh -lc "rg -n '"'^## D-(102|103|116|117):'"' docs/decision_log.md
nl -ba docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md
rg -n -C 8 '("'^|[''^A-Za-z0-9])L4([''^A-Za-z0-9]|$)|Finding L4|L4:'"' docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md
git diff --stat main...origin/impl/d117-u2-successor
git diff --name-status main...origin/impl/d117-u2-successor
git grep -n 'COLD-GATE-Q' origin/impl/d117-u2-successor --" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 20ms:
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:86:# COLD-GATE-Q1: the successor corpus is the complete content-distinct valid
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:91:# COLD-GATE-Q2: retain both protections; the successor level screen is the
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:94:# COLD-GATE-Q3: dependency-free Decimal incomplete-beta inversion is pinned at
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:98:# COLD-GATE-Q4: a range successor below the pending boundary retains it; once
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:101:# COLD-GATE-Q5: a new systematic observation remains new and blocks every
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:104:# COLD-GATE-Q6: no-content attempts are recorded, but only an explicit unused
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:107:# COLD-GATE-Q7: v3 artifacts use cutoff-derived immutable names, remain present
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:110:# COLD-GATE-Q8: the checked-in registry is the sole rotating trust anchor; it
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:113:# COLD-GATE-Q9: publish immutable artifact bytes first and switch the registry
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:116:# COLD-GATE-Q10: a pre-science probe may inspect exactly U1's governed open
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:120:# COLD-GATE-Q11: post evidence may be consumed under the successor only when
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:123:# COLD-GATE-Q12: this four-file exhibit closes the authenticated probe API;

exec
/bin/zsh -lc "sed -n '6339,6402p' docs/decision_log.md
sed -n '7585,7607p' docs/decision_log.md
sed -n '30,39p' docs/process_traces/2026-08-07-night-hardening/FINDINGS-REGISTER.md
git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '70,145p'
sed -n '9520,9820p' docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics

- Date: 2026-08-01
- Status: accepted (magistrate ratification after the two-round Sol xhigh
  design consult + the independent n=19 corpus reconstruction; ALL
  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)
  quantile by numerical CDF, window B pre-cal value against primary
  evidence bytes)
- Applies to: CAL-BRACKET-D079-01, the future
  `configs/calibration/calibration_acceptance_d079_v2.json` artifact

The four pins D-079 left unexecutable, now pinned:

1. **Budget cap (Candidate A, 99% two-draw prediction family, derived
   blind from the pre-window-B n=19 corpus):**
   `max_budgetable_excess_s = 0.001275166090593858`;
   `maximum_budgetable_drift_s = 0.012093166090593858`
   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;
   cap = ceiling − operative screen 0.010818). Consequences verified: a
   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.
   **Window B itself remains refused regardless** — its pre-calibration
   0.035435840879704805 s (verified in primary evidence) exceeds the
   pre-flight level screen, and D-079 cl.2's systematic failure is
   never budgetable. The CAL-BRACKET regression at ~11 ms models the
   DRIFT BRANCH only, never a whole-window B pass.
2. **Freshness = exact identity epoch, no calendar hard expiry:** the
   artifact binds {os_build, hardware_model, power_policy,
   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any
   change → `calibration_acceptance_bound_stale`. Mandatory prospective
   re-derivation triggers: any identity-field change; protocol/estimator
   byte change; a new valid same-identity calibration expanding the
   observed range; corpus doubling (19→38); a new systematic failure
   challenging the pre-flight screen. A trigger observation is judged
   under the PRIOR artifact — never incorporated into a threshold that
   judges itself. Calendar-age fields are provenance/advisory only (the
   corpus spans four days; a calendar constant would be invented).
3. **Never-zero allowance confirmed:**
   `A_s = max(observed_drift_s, 0.010818)`;
   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the
   authenticated operative fiducial bound (anchor-envelope
   re-reduction); no second calibration-drift energy term anywhere
   downstream (D-078 cl.11 single-count).
4. **Decimal numeric semantics:** the artifact stores source decimal
   lexemes and exact-decimal derivations (range
   0.010817749309353528 s; 95% prediction 0.008826584887500717 s;
   pre-flight exact max 0.03355875667989999 s) SEPARATELY from the
   ratified operative comparators (0.010818; 0.033558756679900;
   ROUND_HALF_EVEN at the declared quantum), hashing the decimal
   strings + rounding rule into the derivation sha256. D-079's
   12-place `0.010817749309` is a LABELLED presentation value, never a
   comparator. Acceptance comparisons run in decimal semantics;
   binary64 conversion happens only at the reducer boundary and is
   recorded.

Corpus provenance: the n=19 member list with per-member manifest and
evidence sha256s is reconstructed and lead-spot-verified (2026-08-01
session records; summary in the session custody dir) — the artifact
copies those tables verbatim with re-verification at authoring, never
retyped. Implementation remains sequenced behind gauntlet commit 3 and
the D-100 repair (shared write surfaces).

Revisit when: CAL-BRACKET-D079-01's delta audit reports, or any
re-derivation trigger fires.

## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)

**2026-08-07 supersession note:** The historical re-mint consequence later
superseded by D-117 is retained unchanged as historical context. Current
rule ownership: D-117.

**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**

**What was written.**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).

**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).

**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.

**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.

**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.

- L4 HIGH: pre-flight screens only a COPIED SCALAR (0.033558…), not
  the issued artifact/identity epoch/range triggers — science can run
  all night then be rejected at the morning verdict (identity epoch
  change; sub-corpus-minimum lag). Closure = memo §5A step 6 pre-science
  acceptance + D-102 trigger probe (U2) + de-duplicating the hardcoded
  literal. U2 review must include both scenarios.
- Loader itself verified correct at HEAD (issued role, file sha
  316113960c…, estimator hashes match).

## Disposition
    70	)
    71	_REPO_ROOT = Path(__file__).resolve().parents[1]
    72	ESTIMATOR_CODE_PATHS = (
    73	    "joulewise/powermetrics_fiducial.py",
    74	    "joulewise/uncertainty_evidence.py",
    75	    "joulewise/adapters/powermetrics.py",
    76	    "joulewise/reduce.py",
    77	)
    78	ACCEPTANCE_IDENTITY_FIELDS = IDENTITY_EPOCH_FIELDS
    79	_D102_OPERATIVE_VALUES = {
    80	    "bracket_screen_s": "0.010818",
    81	    "preflight_level_screen_s": "0.033558756679900",
    82	    "max_budgetable_excess_s": "0.001275166090593858",
    83	    "maximum_budgetable_drift_s": "0.012093166090593858",
    84	}
    85	
    86	# COLD-GATE-Q1: the successor corpus is the complete content-distinct valid
    87	# same-epoch ledger prefix, not the triggering suffix or the frozen n=19 set.
    88	SUCCESSOR_CORPUS_SELECTION = (
    89	    "all_content_distinct_valid_same_epoch_observations_through_cutoff"
    90	)
    91	# COLD-GATE-Q2: retain both protections; the successor level screen is the
    92	# larger of the observed maximum and the 95% two-draw prediction.
    93	SUCCESSOR_PREFLIGHT_SCREEN_RULE = "max(observed_maximum,prediction_95_two_draw)"
    94	# COLD-GATE-Q3: dependency-free Decimal incomplete-beta inversion is pinned at
    95	# 80 digits. The D-102 df=18 coefficients remain explicit compatibility pins.
    96	SUCCESSOR_QUANTILE_METHOD = "decimal_incomplete_beta_bisection_v1"
    97	SUCCESSOR_DECIMAL_PRECISION = 80
    98	# COLD-GATE-Q4: a range successor below the pending boundary retains it; once
    99	# crossed, the next boundary is twice the newly issued corpus count.
   100	SUCCESSOR_COUNT_BOUNDARY_RULE = "retain_until_crossed_then_double_issued_count"
   101	# COLD-GATE-Q5: a new systematic observation remains new and blocks every
   102	# automatic build until an authority ruling disposes it.
   103	SUCCESSOR_SYSTEMATIC_POLICY = "persistent_refusal_pending_new_ruling"
   104	# COLD-GATE-Q6: no-content attempts are recorded, but only an explicit unused
   105	# U1 slot closed by its terminal abort is non-concealing; other shapes refuse.
   106	SUCCESSOR_NONCONTENT_POLICY = "record_and_refuse_unless_governed_unused_slot"
   107	# COLD-GATE-Q7: v3 artifacts use cutoff-derived immutable names, remain present
   108	# in the checkout, and form a single-parent ancestry rooted at the issued v2.
   109	SUCCESSOR_LINEAGE_POLICY = "immutable_present_single_parent_cutoff_named_v3"
   110	# COLD-GATE-Q8: the checked-in registry is the sole rotating trust anchor; it
   111	# has exactly one active row and authenticates that artifact's exact bytes.
   112	ACCEPTANCE_REGISTRY_AUTHORITY = "committed_registry_one_active_exact_sha256"
   113	# COLD-GATE-Q9: publish immutable artifact bytes first and switch the registry
   114	# last; the registry replace is the authority commit point. The head is input.
   115	SUCCESSOR_PUBLICATION_POLICY = "artifact_first_registry_last_head_input_only"
   116	# COLD-GATE-Q10: a pre-science probe may inspect exactly U1's governed open
   117	# two-slot extension; a triggered build requires an aborted/finalized terminal
   118	# session and a committed head before issuance.
   119	PRE_PROBE_OPEN_SESSION_POLICY = "permit_governed_open_u1_extension_probe_only"
   120	# COLD-GATE-Q11: post evidence may be consumed under the successor only when
   121	# lineage records its parent-artifact judgment before self-fit construction.
   122	POST_SUCCESSOR_POLICY = "require_explicit_parent_judgment_lineage"
   123	# COLD-GATE-Q12: this four-file exhibit closes the authenticated probe API;
   124	# writer scalar removal and the U8 arm-path call remain separately scoped.
   125	WRITER_INTEGRATION_SCOPE_STATUS = "probe_closed_writer_and_arm_path_residual"
   126	SUCCESSOR_DECISION_IDS = (
   127	    "D-102",
   128	    "D-109",
   129	    "D-117",
   130	    "COLD-GATE-U2-PENDING",
   131	)
   132	
   133	_SUCCESSOR_TOP_LEVEL_FIELDS = {
   134	    "schema_version",
   135	    "acceptance_id",
   136	    "decision_ids",
   137	    "artifact_role",
   138	    "issuance",
   139	    "lineage",
   140	    "ledger_cutoff",
   141	    "identity_epoch",
   142	    "prospective_rederivation",
   143	    "derivation_corpus",
   144	    "prior_observation_set",
   145	    "decimal_derivation",
  - `reason`
  - No free-form timestamp that would make bytes nondeterministic.

- `lineage`
  - `generation`
  - `root_acceptance_id`
  - `parent_acceptance_id`
  - `parent_artifact_sha256`
  - `parent_derivation_sha256`
  - `parent_ledger_cutoff` containing `sequence`, `head_digest`, and `ledger_schema`.
  - The first registry entry for the current issued artifact has a null parent; every successor has exactly one parent.

- `ledger_cutoff`
  - `sequence`
  - `head_digest`, which is also the exact cutoff receipt digest.
  - `ledger_schema`
  - `role: "issued_acceptance_baseline"`
  - It must identify the terminal finalized receipt at the chosen cutoff, not an intermediate reservation.

- `identity_epoch`
  - Exactly:
    - `os_build`
    - `hardware_model`
    - `power_policy`
    - `sampling_interval_ms`
    - `estimator_revision`
    - `pulse_protocol_id`

- `prospective_rederivation`
  - `calendar_expiry: null`
  - `trigger_observation_rule: "judge_under_prior_artifact_never_self_fit"`
  - `triggers`
  - `protocol_sha256`
  - `estimator_code_sha256`, with the four currently governed code paths.
  - `count_trigger` containing the source corpus count, next boundary, and rule. This removes the present hard-coded `19→38` assumption from executable code.

- `derivation_corpus`
  - `selection: "all_content_distinct_valid_same_epoch_observations_through_cutoff"`
  - `n`
  - `members`, sorted by `content_id`.
  - Each member must contain:
    - `content_id`
    - `attempt_id` for the deterministic representative receipt
    - `finalization_sequence`
    - `receipt_digest`
    - `custody_locator`
    - `b_fiducial_s`, preserving the source Decimal lexeme
    - `manifest_sha256`
    - `instrument_evidence_sha256`
  - Duplicate attempts with the same content ID do not add observations. Choose the lowest authenticated finalization sequence as representative and record all aliases in the prior set.
  - Systematic-invalid, ordinary-invalid, abandoned, pending, unresolved, other-epoch, imported-copy duplicates, or non-v3 observations never enter this list.

- `prior_observation_set`
  - `cutoff`, exactly equal to `ledger_cutoff` without its role.
  - `content_identity_method`
  - `epoch_catalog`
  - `observations`, one row per content ID, containing:
    - `content_id`
    - `epoch_id`
    - `disposition`
    - `representative_attempt_id`
    - `attempts`, each with attempt ID, finalization sequence, and receipt digest.
  - `noncontent_attempts`, recording governed abandoned/unresolved attempts that lack a content ID.
  - Thus invalid and noncontent attempts remain visible without influencing derivation.
  - Any conflicting disposition or epoch for one content ID refuses; it is never resolved by choosing a favorable copy.

- `decimal_derivation`
  - `numeric_semantics: "decimal_source_lexemes"`
  - `quantile_method`, including algorithm/version, precision, probabilities, and rounding.
  - `source_statistics`:
    - `minimum_s`, `minimum_content_id`
    - `maximum_s`, `maximum_content_id`
    - `range_s`
    - exact or explicitly rounded mean
    - exact or explicitly rounded sample SD
    - `prediction_95_two_draw_s`
    - `prediction_99_two_draw_s`
  - `presentation_values`, including the labelled 12-place range.
  - `rounding`:
    - `mode: "ROUND_HALF_EVEN"`
    - bracket-screen quantum `0.000001`
    - preflight-screen quantum `0.000000000000001`
    - every source field and resulting value.
  - `ratified_operatives`:
    - `bracket_screen_s`
    - `preflight_level_screen_s`
    - `max_budgetable_excess_s`
    - `maximum_budgetable_drift_s`
    - `allowance_rule: "max(observed_drift_s,bracket_screen_s)"`
    - `operative_bound_rule`
    - `embedding_count: 1`

- `derivation_sha256`
  - SHA-256 of canonical JSON for every preceding field, excluding only `derivation_sha256`.
  - Artifact file SHA remains external in the registry, avoiding a self-hash.

### Derivation rule

Using an 80-digit Decimal context:

1. Parse each authenticated `exact_bound_lexeme_s` directly as `Decimal`; never round-trip through binary64.
2. Coalesce by canonical `content_id`.
3. Select every valid observation whose six-field epoch exactly equals the active artifact epoch and whose finalization sequence is at or before the cutoff.
4. Sort by content ID for deterministic bytes.
5. Compute:
   - `minimum = min(values)`
   - `maximum = max(values)`
   - `range = maximum - minimum`
   - `mean = sum(values) / n`
   - sample SD with denominator `n - 1`
   - `prediction95 = t(0.975, n-1) × SD × sqrt(2)`
   - `prediction99 = t(0.995, n-1) × SD × sqrt(2)`
6. Round mean, SD, and prediction displays to `1e-18`, half-even.
7. `bracket_screen_s = range.quantize(1e-6, ROUND_HALF_EVEN)`.
8. `maximum_budgetable_drift_s = prediction99`.
9. `max_budgetable_excess_s = max(0, prediction99 - bracket_screen_s)`.
10. Preserve `A_s = max(observed_drift_s, bracket_screen_s)` and single embedding.

The preflight level-screen derivation needs an explicit cold ruling; see open question 2 below.

## 2. Deterministic builder algorithm

1. Load the committed registry and resolve its single active entry.
2. Reject absolute paths, traversal, symlinks, duplicate IDs, duplicate artifact paths, lineage cycles, or multiple active entries.
3. Read the parent artifact once; verify exact file SHA against the registry, recompute its derivation hash, validate schema, and verify registry ancestry.
4. Load one immutable ledger snapshot.
5. Verify genesis-to-cutoff chain continuity, receipt digests, attempt transitions, content classifications, custody hashes, physical/current head, and committed head pin.
6. Require the requested cutoff to be the authenticated current terminal finalized head.
7. Reconstruct the complete prefix through the cutoff. Never accept a caller-supplied corpus or directory list.
8. Compare every post-parent-cutoff observation against the parent’s `prior_observation_set`.
9. Judge each new observation under the parent:
   - malformed/unresolved/unclassifiable → refuse;
   - systematic-invalid or above the parent preflight level screen → refuse;
   - valid range-expanding observation → successor required;
   - total valid same-epoch count reaching the boundary → successor required;
   - in-range valid observation below the count boundary → no successor;
   - ordinary-invalid → record, but do not derive.
10. When a successor is required, select the entire valid same-epoch corpus through cutoff—not merely the new suffix.
11. Re-authenticate every selected member from ledger-bound custody and verify exact bound lexeme, content ID, protocol, epoch, manifest, evidence, and receipt.
12. Derive all Decimal statistics and operative values.
13. Construct parent ancestry and complete prior-set records.
14. Serialize deterministically with sorted keys, UTF-8, `allow_nan=false`, fixed indentation, and one trailing newline.
15. Validate the constructed object through the production loader before writing anything.
16. Re-run the trigger probe against the proposed successor; the triggering observation must now be in its prior set and no longer appear “new.”
17. In dry-run mode, emit bytes, artifact SHA, derivation SHA, proposed registry entry, and proposed head pin to stdout; write nothing.
18. In issue mode, require explicit artifact and registry destinations, refuse overwrite/path substitution, stage both validated byte buffers, and publish only under the governed head-pin/commit procedure.
19. A second run over identical parent, ledger, cutoff, and code must produce byte-identical artifact and registry output.

## 3. Trigger probe and §5A hook

The probe should return one of four closed outcomes:

- `accepted_under_active_artifact`
- `successor_required`
- `systematic_refusal`
- `authentication_or_epoch_refusal`

It must report active acceptance ID, artifact file SHA, derivation SHA, parent cutoff, current ledger head, observed six-field epoch, new content IDs, and observed triggers.

Trigger rules:

- Range expansion: a new valid same-epoch Decimal bound is strictly below the parent corpus minimum or above its maximum.
- Count boundary: total authenticated, content-distinct, valid same-epoch observations reaches 38 for the current n=19 generation.
- Systematic condition: evidence-valid bound exceeds the parent preflight screen, or is finalized systematic-invalid. This refuses; the builder cannot reclassify or absorb it.
- Identity, protocol, or estimator change: refuse as stale/new-epoch work; do not silently combine epochs.

At §5A step 6:

1. Finalize the pre slot.
2. Run the probe before member one.
3. If accepted, arm.
4. If successor-required, do not arm:
   - govern the still-open post slot according to U1’s state machine;
   - commit/authenticate the current ledger head;
   - build and cold-authenticate the successor;
   - update its registry entry and active pointer;
   - reload the artifact from disk;
   - rerun the probe;
   - arm only after a clean result.
5. If systematic or authentication refusal, close/abort the bracket session and end the attempt.

A post trigger runs after science but before bracket binding and verdict issuance.

### L4 closure

Today, both the production writer and runbook compare copied literals:

- [writer scalar](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/validate_powermetrics_fiducial.py:92)
- [writer classification](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/scripts/validate_powermetrics_fiducial.py:664)
- [runbook scalar check](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/phase_2/window_runbook.md:574)

The writer must obtain the screen and epoch from the authenticated active artifact before assigning `valid` versus `systematic-invalid`. The §5A chain must call the U2 probe rather than re-reading the evidence and applying a shell scalar. This specifically closes both registered L4 counterexamples: an identity-epoch change and a new sub-corpus-minimum lag.

## 4. Refusal vectors and tests

Required focused tests:

- Current issued n=19 artifact and initial registry entry authenticate unchanged.
- Exact current SHA, derivation SHA, cutoff, and 30/2/6 inventory reproduce.
- Range expansion below minimum and above maximum both require a successor.
- An in-range observation does not trigger before the count boundary.
- Counts 37 and 38 distinguish no-trigger/trigger exactly.
- A first live range successor contains all 30 existing valid observations plus the new valid observation.
- Systematic-invalid and above-screen observations refuse and never enter a successor.
- Ordinary-invalid observations remain in the prior set but not the corpus.
- Pending, abandoned, null-content, unresolved, or unknown disposition refuses issuance.
- Same content copied to another path does not increase n.
- Same content with conflicting disposition, epoch, bound, or hashes refuses.
- Other-epoch valid observations are recorded but excluded.
- Missing/tampered custody, manifest, evidence, receipt, protocol, T1, or bound lexeme refuses.
- Prefix omission, insertion, reordering, content substitution, import-marker removal, or live/import leakage refuses.
- Physical/pin mismatch, rollback, fork, uncommitted head, torn ledger, duplicate finalization, or nonterminal cutoff refuses.
- Parent artifact tamper, wrong registry SHA, wrong derivation SHA, orphan parent, ancestry cycle, inactive-parent build, or registry rollback refuses.
- Artifact-path traversal, symlink substitution, duplicate IDs, and alternate self-consistent unregistered artifact refuse.
- Protocol/estimator byte drift and six-field epoch mismatch refuse before science.
- Probe result is unchanged if the old copied scalar is modified or removed.
- Decimal halfway rounding, long lexemes, negative/nonfinite values, and binary64-substitution attempts are discriminating.
- n=19 golden reproduces the current predictions and operatives.
- Successor golden produces byte-identical artifact, registry entry, and expected head pin across repeated builds and shuffled input enumeration.
- Dry run writes nothing.
- Failed final validation publishes neither artifact nor registry mutation.
- Pre-trigger observation is proven judged under the parent; self-fit construction is rejected.
- Post-trigger successor preserves the exact authenticated parent prefix.

Focused command:

```text
python3 -m unittest tests.test_calibration_acceptance_successor
```

Then the required canonical suite:

```text
python3 -m unittest discover -s tests
```

## 5. Exact WRITE_SCOPE

The frozen memo currently authorizes exactly:

```text
joulewise/calibration_bracketing.py
scripts/build_calibration_acceptance_successor.py
configs/calibration/calibration_acceptance_registry.json
tests/test_calibration_acceptance_successor.py
```

That scope is sufficient for the core builder and probe API, but insufficient to claim L4 fully closed because the copied scalar lives in the production writer.

Recommended rule-11 expansion for U2:

```text
joulewise/calibration_bracketing.py
scripts/build_calibration_acceptance_successor.py
scripts/validate_powermetrics_fiducial.py
configs/calibration/calibration_acceptance_registry.json
tests/test_calibration_acceptance_successor.py
tests/test_powermetrics_fiducial.py
```

The §5A operator-chain replacement remains in U8’s already-frozen scope:

```text
docs/phase_2/window_runbook.md
scripts/validate_frozen_plan_readiness.py
tests/test_frozen_plan_readiness.py
```

Therefore L4 should be marked “code closed by U2, arm-path closed by U8,” and retired only after both land. Do not silently add these paths to a delegated U2 session; the cold gate must authorize the expansion.

A future live issuance also needs a separately authorized exact successor-artifact output path and the then-current `configs/calibration/calibration_ledger_head.json`. Those are operational evidence writes, not implied by the implementation scope above.

## 6. Cold-gate questions

1. Ratify the corpus rule exactly: every content-distinct valid same-epoch observation through cutoff, including the 30 already valid at sequence 76.

2. Ratify the preflight-screen formula for successors. The loader currently uses rounded observed maximum; the runbook says the larger of observed maximum and a 95% upper prediction. Those agree for n=19 but need not agree later.

3. Ratify the deterministic Student-t implementation and precision. Decimal accumulation is exact, but the numerical CDF/quantile algorithm must be versioned and pinned.

4. After a range-triggered n=31 successor, is the next count boundary still the original 38, and after the n=38 successor does it become 76? Recommended: retain 38 until crossed, then double the newly issued corpus count.

5. Decide whether any new systematic failure permanently blocks automatic successor issuance pending a new ruling, as recommended, or merely blocks that attempt.

6. Resolve abandoned/no-content handling: record it in `noncontent_attempts` but refuse issuance until governed closure establishes it cannot conceal a classifiable observation.

7. Ratify the v3 schema, deterministic acceptance-ID format, immutable artifact path convention, and whether old parent bytes must remain present or may be recovered from Git history.

8. Ratify registry authentication: committed registry bytes as trust anchor, one active entry, exact artifact SHA, no code-side per-successor constants.

9. Ratify artifact/registry/head-pin co-landing and crash behavior. No claim evaluation may occur between ledger advancement and committed successor authority.

10. Resolve U1 interaction: whether the pre probe may run with the post slot prospectively open, and how that slot is preserved or closed while a triggered head is committed and a successor issued.

11. Ratify whether a post observation accepted under the parent may subsequently participate in bracket evaluation under the successor, provided the artifact retains explicit parent-judgment evidence.

12. Approve the six-file U2 scope expansion above, or accept that writer-side copied-scalar removal remains a separately gated hardening unit.

No files were written, no tests were run, and the worktree remained clean.

codex
The branch carries exactly twelve tags, all in `joulewise/calibration_bracketing.py:86–125`. I’m checking each tag against its executable consumers—not treating the comments as proof—because several choices span the probe, builder, registry loader, writer integration, and U1 ledger-session state machine.
exec
/bin/zsh -lc 'for sym in SUCCESSOR_CORPUS_SELECTION SUCCESSOR_PREFLIGHT_SCREEN_RULE SUCCESSOR_QUANTILE_METHOD SUCCESSOR_DECIMAL_PRECISION SUCCESSOR_COUNT_BOUNDARY_RULE SUCCESSOR_SYSTEMATIC_POLICY SUCCESSOR_NONCONTENT_POLICY SUCCESSOR_LINEAGE_POLICY ACCEPTANCE_REGISTRY_AUTHORITY SUCCESSOR_PUBLICATION_POLICY PRE_PROBE_OPEN_SESSION_POLICY POST_SUCCESSOR_POLICY WRITER_INTEGRATION_SCOPE_STATUS; do git grep -n "$sym" origin/impl/d117-u2-successor --; done

git grep -n -E '"'def (load_calibration_acceptance_registry|probe_calibration_acceptance_successor|build_calibration_acceptance_successor|publish_calibration_acceptance_successor|_student_t|_decimal|_successor|_build|_validate)' origin/impl/d117-u2-successor -- joulewise/calibration_bracketing.py scripts/build_calibration_acceptance_successor.py scripts/validate_powermetrics_fiducial.py

git grep -n -E 'acceptance_registry|successor|preflight_level_screen|systematic' origin/impl/d117-u2-successor -- scripts/validate_powermetrics_fiducial.py | head -200" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 661ms:
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:96:SUCCESSOR_QUANTILE_METHOD = "decimal_incomplete_beta_bisection_v1"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:468:            "algorithm": SUCCESSOR_QUANTILE_METHOD,
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:37:    SUCCESSOR_QUANTILE_METHOD,
origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py:540:            bracketing.SUCCESSOR_QUANTILE_METHOD,
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:97:SUCCESSOR_DECIMAL_PRECISION = 80
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:309:    tiny = Decimal(1).scaleb(-(SUCCESSOR_DECIMAL_PRECISION - 8))
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:310:    epsilon = Decimal(1).scaleb(-(SUCCESSOR_DECIMAL_PRECISION - 12))
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:389:        context.prec = SUCCESSOR_DECIMAL_PRECISION
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:396:        tolerance = Decimal(1).scaleb(-(SUCCESSOR_DECIMAL_PRECISION - 8))
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:426:        context.prec = SUCCESSOR_DECIMAL_PRECISION
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:469:            "precision_decimal_digits": SUCCESSOR_DECIMAL_PRECISION,
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:100:SUCCESSOR_COUNT_BOUNDARY_RULE = "retain_until_crossed_then_double_issued_count"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:941:        != SUCCESSOR_COUNT_BOUNDARY_RULE
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:34:    SUCCESSOR_COUNT_BOUNDARY_RULE,
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:402:                "rule": SUCCESSOR_COUNT_BOUNDARY_RULE,
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:103:SUCCESSOR_SYSTEMATIC_POLICY = "persistent_refusal_pending_new_ruling"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1882:            refusal_reasons=(SUCCESSOR_SYSTEMATIC_POLICY,),
origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py:385:                    [bracketing.SUCCESSOR_SYSTEMATIC_POLICY],
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:106:SUCCESSOR_NONCONTENT_POLICY = "record_and_refuse_unless_governed_unused_slot"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:109:SUCCESSOR_LINEAGE_POLICY = "immutable_present_single_parent_cutoff_named_v3"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:112:ACCEPTANCE_REGISTRY_AUTHORITY = "committed_registry_one_active_exact_sha256"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:597:        or value.get("authority") != ACCEPTANCE_REGISTRY_AUTHORITY
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:29:    ACCEPTANCE_REGISTRY_AUTHORITY,
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:444:        "authority": ACCEPTANCE_REGISTRY_AUTHORITY,
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:115:SUCCESSOR_PUBLICATION_POLICY = "artifact_first_registry_last_head_input_only"
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:36:    SUCCESSOR_PUBLICATION_POLICY,
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:84:            "publication_policy": SUCCESSOR_PUBLICATION_POLICY,
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:119:PRE_PROBE_OPEN_SESSION_POLICY = "permit_governed_open_u1_extension_probe_only"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:122:POST_SUCCESSOR_POLICY = "require_explicit_parent_judgment_lineage"
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:32:    POST_SUCCESSOR_POLICY,
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:461:        "parent_judgment_policy": POST_SUCCESSOR_POLICY,
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:125:WRITER_INTEGRATION_SCOPE_STATUS = "probe_closed_writer_and_arm_path_residual"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1686:        "writer_integration_scope_status": WRITER_INTEGRATION_SCOPE_STATUS,
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:250:def _decimal(value: Any) -> Decimal | None:
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:260:def _decimal_text(value: Decimal) -> str:
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:268:def _decimal_pi() -> Decimal:
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:287:def _decimal_beta_a_half(df: int) -> Decimal:
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:300:def _decimal_beta_continued_fraction(
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:343:def _decimal_regularized_incomplete_beta_df_half(
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:365:def _decimal_student_t_survival(value: Decimal, df: int) -> Decimal:
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:712:def load_calibration_acceptance_registry(
origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py:234:def build_calibration_acceptance_successor(
origin/impl/d117-u2-successor:scripts/validate_powermetrics_fiducial.py:289:def _validate_reserved_bracket_slot(
origin/impl/d117-u2-successor:scripts/validate_powermetrics_fiducial.py:916:            "systematic-invalid"

exec
/bin/zsh -lc "git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '220,535p'
git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '570,1030p'
git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '1550,1915p'
git show origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py | nl -ba | sed -n '1,520p'
git show origin/impl/d117-u2-successor:scripts/validate_powermetrics_fiducial.py | nl -ba | sed -n '850,945p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   220	            "protocol_id": self.protocol_id,
   221	            "capture_wall_time_s": self.capture_wall_time_s,
   222	            # This descriptor is the recorded reducer boundary.  Keep both the
   223	            # exact acceptance lexeme and its explicit binary64 projection.
   224	            "b_fiducial_s": float(bound) if bound is not None else self.b_fiducial_s,
   225	            "b_fiducial_decimal_s": str(bound) if bound is not None else None,
   226	            "attempt_id": self.attempt_id,
   227	            "content_id": self.content_id,
   228	            "ledger_receipt_digest": self.ledger_receipt_digest,
   229	            "bracket_session_id": self.bracket_session_id,
   230	            "bracket_slot": self.bracket_slot,
   231	            "bracket_window_id": self.bracket_window_id,
   232	            "bracket_plan_id": self.bracket_plan_id,
   233	            "bracket_plan_sha256": self.bracket_plan_sha256,
   234	            "bracket_evidence_root_id": self.bracket_evidence_root_id,
   235	            "bracket_runs_root": self.bracket_runs_root,
   236	        }
   237	
   238	
   239	def _canonical_sha256(value: Mapping[str, Any]) -> str:
   240	    raw = json.dumps(
   241	        dict(value),
   242	        sort_keys=True,
   243	        separators=(",", ":"),
   244	        ensure_ascii=False,
   245	        allow_nan=False,
   246	    ).encode("utf-8")
   247	    return hashlib.sha256(raw).hexdigest()
   248	
   249	
   250	def _decimal(value: Any) -> Decimal | None:
   251	    if not isinstance(value, str) or not value:
   252	        return None
   253	    try:
   254	        result = Decimal(value)
   255	    except InvalidOperation:
   256	        return None
   257	    return result if result.is_finite() else None
   258	
   259	
   260	def _decimal_text(value: Decimal) -> str:
   261	    """Render one finite Decimal without exponent or binary64 mediation."""
   262	
   263	    if not value.is_finite():
   264	        raise ValueError("decimal value must be finite")
   265	    return format(value, "f")
   266	
   267	
   268	def _decimal_pi() -> Decimal:
   269	    """Return pi deterministically at the active Decimal precision."""
   270	
   271	    one = Decimal(1)
   272	    two = Decimal(2)
   273	    four = Decimal(4)
   274	    a = one
   275	    b = one / two.sqrt()
   276	    t = Decimal(1) / four
   277	    power = one
   278	    for _ in range(10):
   279	        midpoint = (a + b) / two
   280	        b = (a * b).sqrt()
   281	        t -= power * (a - midpoint) ** 2
   282	        a = midpoint
   283	        power *= two
   284	    return (a + b) ** 2 / (four * t)
   285	
   286	
   287	def _decimal_beta_a_half(df: int) -> Decimal:
   288	    """Compute B(df/2, 1/2) for an integer df without a gamma primitive."""
   289	
   290	    if df % 2 == 0:
   291	        m = df // 2
   292	        numerator = Decimal(4**m * math.factorial(m) * math.factorial(m - 1))
   293	        return numerator / Decimal(math.factorial(2 * m))
   294	    m = (df - 1) // 2
   295	    numerator = Decimal(math.factorial(2 * m)) * _decimal_pi()
   296	    denominator = Decimal(4**m * math.factorial(m) ** 2)
   297	    return numerator / denominator
   298	
   299	
   300	def _decimal_beta_continued_fraction(
   301	    a: Decimal, b: Decimal, x: Decimal
   302	) -> Decimal:
   303	    """Evaluate the incomplete-beta continued fraction by Lentz iteration."""
   304	
   305	    one = Decimal(1)
   306	    qab = a + b
   307	    qap = a + one
   308	    qam = a - one
   309	    tiny = Decimal(1).scaleb(-(SUCCESSOR_DECIMAL_PRECISION - 8))
   310	    epsilon = Decimal(1).scaleb(-(SUCCESSOR_DECIMAL_PRECISION - 12))
   311	
   312	    def guarded(value: Decimal) -> Decimal:
   313	        if abs(value) >= tiny:
   314	            return value
   315	        return -tiny if value < 0 else tiny
   316	
   317	    c = one
   318	    d = one / guarded(one - qab * x / qap)
   319	    result = d
   320	    for iteration in range(1, 10_001):
   321	        i = Decimal(iteration)
   322	        doubled = Decimal(2 * iteration)
   323	        numerator = i * (b - i) * x / ((qam + doubled) * (a + doubled))
   324	        d = one / guarded(one + numerator * d)
   325	        c = guarded(one + numerator / c)
   326	        result *= d * c
   327	
   328	        numerator = -(
   329	            (a + i)
   330	            * (qab + i)
   331	            * x
   332	            / ((a + doubled) * (qap + doubled))
   333	        )
   334	        d = one / guarded(one + numerator * d)
   335	        c = guarded(one + numerator / c)
   336	        change = d * c
   337	        result *= change
   338	        if abs(change - one) <= epsilon:
   339	            return result
   340	    raise ArithmeticError("Decimal incomplete beta did not converge")
   341	
   342	
   343	def _decimal_regularized_incomplete_beta_df_half(
   344	    x: Decimal, df: int
   345	) -> Decimal:
   346	    if x <= 0:
   347	        return Decimal(0)
   348	    if x >= 1:
   349	        return Decimal(1)
   350	    a = Decimal(df) / Decimal(2)
   351	    b = Decimal("0.5")
   352	    beta = _decimal_beta_a_half(df)
   353	    front = (x**a) * ((Decimal(1) - x) ** b) / beta
   354	    if x < (a + 1) / (a + b + 2):
   355	        result = front * _decimal_beta_continued_fraction(a, b, x) / a
   356	    else:
   357	        result = Decimal(1) - (
   358	            front
   359	            * _decimal_beta_continued_fraction(b, a, Decimal(1) - x)
   360	            / b
   361	        )
   362	    return min(Decimal(1), max(Decimal(0), result))
   363	
   364	
   365	def _decimal_student_t_survival(value: Decimal, df: int) -> Decimal:
   366	    if value == 0:
   367	        return Decimal("0.5")
   368	    argument = Decimal(df) / (Decimal(df) + value * value)
   369	    return Decimal("0.5") * _decimal_regularized_incomplete_beta_df_half(
   370	        argument, df
   371	    )
   372	
   373	
   374	def decimal_student_t_quantile(probability: str, df: int) -> Decimal:
   375	    """Return the pinned deterministic Student-t quantile as a Decimal."""
   376	
   377	    if isinstance(df, bool) or not isinstance(df, int) or df < 1:
   378	        raise ValueError("df must be an integer >= 1")
   379	    target = _decimal(probability)
   380	    if target is None or not Decimal(0) < target < Decimal(1):
   381	        raise ValueError("probability must be a finite decimal between zero and one")
   382	    pinned = _D102_RATIFIED_T_QUANTILES.get((df, probability))
   383	    if pinned is not None:
   384	        return pinned
   385	    if target == Decimal("0.5"):
   386	        return Decimal(0)
   387	
   388	    with localcontext() as context:
   389	        context.prec = SUCCESSOR_DECIMAL_PRECISION
   390	        sign = Decimal(-1) if target < Decimal("0.5") else Decimal(1)
   391	        tail = target if target < Decimal("0.5") else Decimal(1) - target
   392	        lower = Decimal(0)
   393	        upper = Decimal(1)
   394	        while _decimal_student_t_survival(upper, df) > tail:
   395	            upper *= 2
   396	        tolerance = Decimal(1).scaleb(-(SUCCESSOR_DECIMAL_PRECISION - 8))
   397	        while upper - lower > tolerance:
   398	            midpoint = (lower + upper) / 2
   399	            if _decimal_student_t_survival(midpoint, df) > tail:
   400	                lower = midpoint
   401	            else:
   402	                upper = midpoint
   403	        return +(sign * ((lower + upper) / 2))
   404	
   405	
   406	def derive_successor_decimal_derivation(
   407	    members: Sequence[Mapping[str, Any]],
   408	) -> dict[str, Any]:
   409	    """Derive the complete v3 Decimal record from authenticated members."""
   410	
   411	    if len(members) < 2:
   412	        raise ValueError("successor derivation requires at least two members")
   413	    content_ids: list[str] = []
   414	    values: list[Decimal] = []
   415	    for member in members:
   416	        content_id = member.get("content_id") if isinstance(member, Mapping) else None
   417	        value = _decimal(member.get("b_fiducial_s")) if isinstance(member, Mapping) else None
   418	        if not _valid_sha256(content_id) or value is None or value < 0:
   419	            raise ValueError("successor member has invalid content ID or bound")
   420	        content_ids.append(content_id)
   421	        values.append(value)
   422	    if content_ids != sorted(content_ids) or len(content_ids) != len(set(content_ids)):
   423	        raise ValueError("successor members must be content-ID sorted and distinct")
   424	
   425	    with localcontext() as context:
   426	        context.prec = SUCCESSOR_DECIMAL_PRECISION
   427	        count = Decimal(len(values))
   428	        mean = sum(values, Decimal(0)) / count
   429	        sample_sd = (
   430	            sum((value - mean) ** 2 for value in values)
   431	            / Decimal(len(values) - 1)
   432	        ).sqrt()
   433	        minimum = min(values)
   434	        maximum = max(values)
   435	        observed_range = maximum - minimum
   436	        prediction_95 = (
   437	            decimal_student_t_quantile("0.975", len(values) - 1)
   438	            * sample_sd
   439	            * Decimal(2).sqrt()
   440	        )
   441	        prediction_99 = (
   442	            decimal_student_t_quantile("0.995", len(values) - 1)
   443	            * sample_sd
   444	            * Decimal(2).sqrt()
   445	        )
   446	        display_quantum = Decimal("0.000000000000000001")
   447	        prediction_95_display = prediction_95.quantize(
   448	            display_quantum, rounding=ROUND_HALF_EVEN
   449	        )
   450	        prediction_99_display = prediction_99.quantize(
   451	            display_quantum, rounding=ROUND_HALF_EVEN
   452	        )
   453	        bracket_screen = observed_range.quantize(
   454	            Decimal("0.000001"), rounding=ROUND_HALF_EVEN
   455	        )
   456	        preflight_source = max(maximum, prediction_95)
   457	        preflight_screen = preflight_source.quantize(
   458	            Decimal("0.000000000000001"), rounding=ROUND_HALF_EVEN
   459	        )
   460	        maximum_budgetable_drift = prediction_99_display
   461	        max_budgetable_excess = max(
   462	            Decimal(0), maximum_budgetable_drift - bracket_screen
   463	        )
   464	
   465	    return {
   466	        "numeric_semantics": "decimal_source_lexemes",
   467	        "quantile_method": {
   468	            "algorithm": SUCCESSOR_QUANTILE_METHOD,
   469	            "precision_decimal_digits": SUCCESSOR_DECIMAL_PRECISION,
   470	            "probabilities": {
   471	                "prediction_95_two_draw": "0.975",
   472	                "prediction_99_two_draw": "0.995",
   473	            },
   474	            "rounding": "ROUND_HALF_EVEN",
   475	            "d102_df18_compatibility_pin": True,
   476	        },
   477	        "source_statistics": {
   478	            "minimum_s": _decimal_text(minimum),
   479	            "minimum_content_id": content_ids[values.index(minimum)],
   480	            "maximum_s": _decimal_text(maximum),
   481	            "maximum_content_id": content_ids[values.index(maximum)],
   482	            "range_s": _decimal_text(observed_range),
   483	            "mean_s": _decimal_text(
   484	                mean.quantize(display_quantum, rounding=ROUND_HALF_EVEN)
   485	            ),
   486	            "sample_sd_s": _decimal_text(
   487	                sample_sd.quantize(display_quantum, rounding=ROUND_HALF_EVEN)
   488	            ),
   489	            "prediction_95_two_draw_s": _decimal_text(prediction_95_display),
   490	            "prediction_99_two_draw_s": _decimal_text(prediction_99_display),
   491	        },
   492	        "presentation_values": {
   493	            "range_12_places_s": {
   494	                "value": _decimal_text(
   495	                    observed_range.quantize(
   496	                        Decimal("0.000000000001"), rounding=ROUND_HALF_EVEN
   497	                    )
   498	                ),
   499	                "label": "presentation_only_not_a_comparator",
   500	            }
   501	        },
   502	        "rounding": {
   503	            "mode": "ROUND_HALF_EVEN",
   504	            "source_fields": "authenticated_decimal_lexemes_unrounded",
   505	            "statistics_quantum_s": "0.000000000000000001",
   506	            "bracket_screen": {
   507	                "source": "source_statistics.range_s",
   508	                "quantum_s": "0.000001",
   509	                "value_s": _decimal_text(bracket_screen),
   510	            },
   511	            "preflight_level_screen": {
   512	                "source_rule": SUCCESSOR_PREFLIGHT_SCREEN_RULE,
   513	                "quantum_s": "0.000000000000001",
   514	                "value_s": _decimal_text(preflight_screen),
   515	            },
   516	        },
   517	        "ratified_operatives": {
   518	            "bracket_screen_s": _decimal_text(bracket_screen),
   519	            "preflight_level_screen_s": _decimal_text(preflight_screen),
   520	            "max_budgetable_excess_s": _decimal_text(max_budgetable_excess),
   521	            "maximum_budgetable_drift_s": _decimal_text(
   522	                maximum_budgetable_drift
   523	            ),
   524	            "allowance_rule": "max(observed_drift_s,bracket_screen_s)",
   525	            "operative_bound_rule": (
   526	                "max(pre_b_fiducial_s,post_b_fiducial_s)"
   527	                "+calibration_drift_allowance_s"
   528	            ),
   529	            "embedding_count": 1,
   530	        },
   531	    }
   532	
   533	
   534	def _candidate_decimal(candidate: CalibrationCandidate) -> Decimal | None:
   535	    value = candidate.b_fiducial_s
   570	    current = root
   571	    for part in relative.parts:
   572	        current = current / part
   573	        try:
   574	            if current.is_symlink():
   575	                return True
   576	        except OSError:
   577	            return True
   578	    return False
   579	
   580	
   581	def _repository_relative_path(value: Any) -> str | None:
   582	    if not isinstance(value, str) or not value or "\\" in value:
   583	        return None
   584	    candidate = Path(value)
   585	    if candidate.is_absolute() or value != candidate.as_posix():
   586	        return None
   587	    if any(part in {"", ".", ".."} for part in candidate.parts):
   588	        return None
   589	    return value
   590	
   591	
   592	def _valid_registry(value: Any) -> bool:
   593	    if (
   594	        not isinstance(value, Mapping)
   595	        or set(value) != {"schema_version", "authority", "entries"}
   596	        or value.get("schema_version") != ACCEPTANCE_REGISTRY_SCHEMA
   597	        or value.get("authority") != ACCEPTANCE_REGISTRY_AUTHORITY
   598	        or not isinstance(value.get("entries"), list)
   599	        or not value["entries"]
   600	    ):
   601	        return False
   602	    expected_keys = {
   603	        "acceptance_id",
   604	        "artifact_path",
   605	        "artifact_sha256",
   606	        "derivation_sha256",
   607	        "artifact_schema",
   608	        "generation",
   609	        "active",
   610	        "parent_acceptance_id",
   611	        "parent_artifact_sha256",
   612	        "ledger_cutoff",
   613	    }
   614	    ids: set[str] = set()
   615	    paths: set[str] = set()
   616	    entries_by_id: dict[str, Mapping[str, Any]] = {}
   617	    active_count = 0
   618	    for entry in value["entries"]:
   619	        cutoff = entry.get("ledger_cutoff") if isinstance(entry, Mapping) else None
   620	        if (
   621	            not isinstance(entry, Mapping)
   622	            or set(entry) != expected_keys
   623	            or not isinstance(entry.get("acceptance_id"), str)
   624	            or not entry["acceptance_id"]
   625	            or _repository_relative_path(entry.get("artifact_path")) is None
   626	            or not entry["artifact_path"].startswith("configs/calibration/")
   627	            or not _valid_sha256(entry.get("artifact_sha256"))
   628	            or not _valid_sha256(entry.get("derivation_sha256"))
   629	            or entry.get("artifact_schema")
   630	            not in {ACCEPTANCE_BOUND_SCHEMA, ACCEPTANCE_SUCCESSOR_SCHEMA}
   631	            or isinstance(entry.get("generation"), bool)
   632	            or not isinstance(entry.get("generation"), int)
   633	            or entry["generation"] < 1
   634	            or not isinstance(entry.get("active"), bool)
   635	            or not isinstance(cutoff, Mapping)
   636	            or set(cutoff) != {"sequence", "head_digest", "ledger_schema"}
   637	            or isinstance(cutoff.get("sequence"), bool)
   638	            or not isinstance(cutoff.get("sequence"), int)
   639	            or cutoff["sequence"] < 1
   640	            or not _valid_sha256(cutoff.get("head_digest"))
   641	            or cutoff.get("ledger_schema") != LEDGER_SCHEMA
   642	        ):
   643	            return False
   644	        acceptance_id = entry["acceptance_id"]
   645	        artifact_path = entry["artifact_path"]
   646	        if acceptance_id in ids or artifact_path in paths:
   647	            return False
   648	        ids.add(acceptance_id)
   649	        paths.add(artifact_path)
   650	        entries_by_id[acceptance_id] = entry
   651	        active_count += int(entry["active"])
   652	    if active_count != 1:
   653	        return False
   654	
   655	    roots = 0
   656	    child_counts = {entry["acceptance_id"]: 0 for entry in value["entries"]}
   657	    for entry in value["entries"]:
   658	        parent_id = entry["parent_acceptance_id"]
   659	        parent_sha = entry["parent_artifact_sha256"]
   660	        if parent_id is None:
   661	            roots += 1
   662	            if parent_sha is not None or entry["generation"] != 1:
   663	                return False
   664	            continue
   665	        parent = entries_by_id.get(parent_id)
   666	        if (
   667	            not isinstance(parent_id, str)
   668	            or parent is None
   669	            or parent_sha != parent["artifact_sha256"]
   670	            or entry["generation"] != parent["generation"] + 1
   671	            or entry["ledger_cutoff"]["sequence"]
   672	            <= parent["ledger_cutoff"]["sequence"]
   673	        ):
   674	            return False
   675	        child_counts[parent_id] += 1
   676	        if child_counts[parent_id] > 1:
   677	            return False
   678	        seen = {entry["acceptance_id"]}
   679	        cursor: Mapping[str, Any] | None = parent
   680	        while cursor is not None:
   681	            cursor_id = cursor["acceptance_id"]
   682	            if cursor_id in seen:
   683	                return False
   684	            seen.add(cursor_id)
   685	            next_parent = cursor["parent_acceptance_id"]
   686	            cursor = entries_by_id.get(next_parent) if next_parent is not None else None
   687	    leaves = [entry_id for entry_id, count in child_counts.items() if count == 0]
   688	    active_ids = [entry["acceptance_id"] for entry in value["entries"] if entry["active"]]
   689	    return bool(
   690	        roots == 1
   691	        and len(leaves) == 1
   692	        and active_ids == leaves
   693	        and {entry["generation"] for entry in value["entries"]}
   694	        == set(range(1, len(value["entries"]) + 1))
   695	    )
   696	
   697	
   698	def _git_head_bytes(path: Path, repo_root: Path) -> bytes | None:
   699	    try:
   700	        relative = path.relative_to(repo_root).as_posix()
   701	        completed = subprocess.run(
   702	            ["git", "show", f"HEAD:{relative}"],
   703	            cwd=repo_root,
   704	            check=False,
   705	            capture_output=True,
   706	        )
   707	    except (OSError, ValueError):
   708	        return None
   709	    return completed.stdout if completed.returncode == 0 else None
   710	
   711	
   712	def load_calibration_acceptance_registry(
   713	    path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
   714	    *,
   715	    repo_root: Path = _REPO_ROOT,
   716	    require_committed: bool = True,
   717	) -> dict[str, Any] | None:
   718	    """Load the single-active acceptance registry and authenticate ancestry."""
   719	
   720	    path = Path(path)
   721	    lexical_repo_root = Path(repo_root).absolute()
   722	    repo_root = Path(repo_root).resolve()
   723	    try:
   724	        if _path_has_symlink_component(path.absolute(), lexical_repo_root):
   725	            return None
   726	        resolved = path.resolve(strict=True)
   727	        resolved.relative_to(repo_root)
   728	        raw = resolved.read_bytes()
   729	        value = json.loads(raw)
   730	    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
   731	        return None
   732	    if require_committed and _git_head_bytes(resolved, repo_root) != raw:
   733	        return None
   734	    if not _valid_registry(value):
   735	        return None
   736	    entries_by_id = {entry["acceptance_id"]: entry for entry in value["entries"]}
   737	    artifacts_by_id: dict[str, Mapping[str, Any]] = {}
   738	    for entry in value["entries"]:
   739	        artifact_path = repo_root / entry["artifact_path"]
   740	        try:
   741	            if _path_has_symlink_component(artifact_path.absolute(), repo_root):
   742	                return None
   743	            artifact_resolved = artifact_path.resolve(strict=True)
   744	            artifact_resolved.relative_to(repo_root)
   745	            artifact_raw = artifact_resolved.read_bytes()
   746	            artifact = json.loads(artifact_raw)
   747	        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
   748	            return None
   749	        if (
   750	            hashlib.sha256(artifact_raw).hexdigest() != entry["artifact_sha256"]
   751	            or not _valid_acceptance_bound(artifact)
   752	            or artifact.get("acceptance_id") != entry["acceptance_id"]
   753	            or artifact.get("schema_version") != entry["artifact_schema"]
   754	            or artifact.get("derivation_sha256") != entry["derivation_sha256"]
   755	            or {
   756	                key: artifact["ledger_cutoff"].get(key)
   757	                for key in ("sequence", "head_digest", "ledger_schema")
   758	            }
   759	            != entry["ledger_cutoff"]
   760	        ):
   761	            return None
   762	        artifacts_by_id[entry["acceptance_id"]] = artifact
   763	        if entry["artifact_schema"] == ACCEPTANCE_SUCCESSOR_SCHEMA:
   764	            filename_match = _SUCCESSOR_ARTIFACT_NAME_RE.fullmatch(
   765	                Path(entry["artifact_path"]).name
   766	            )
   767	            if (
   768	                filename_match is None
   769	                or int(filename_match.group(1))
   770	                != entry["ledger_cutoff"]["sequence"]
   771	                or filename_match.group(2)
   772	                != entry["ledger_cutoff"]["head_digest"][:16]
   773	            ):
   774	                return None
   775	    for entry in value["entries"]:
   776	        if entry["artifact_schema"] != ACCEPTANCE_SUCCESSOR_SCHEMA:
   777	            continue
   778	        artifact = artifacts_by_id[entry["acceptance_id"]]
   779	        lineage = artifact["lineage"]
   780	        parent_entry = entries_by_id.get(entry["parent_acceptance_id"])
   781	        parent = artifacts_by_id.get(entry["parent_acceptance_id"])
   782	        if parent_entry is None or parent is None:
   783	            return None
   784	        count = artifact["derivation_corpus"]["n"]
   785	        parent_boundary = _artifact_count_boundary(parent)
   786	        expected_boundary = parent_boundary if count < parent_boundary else 2 * count
   787	        if (
   788	            lineage["generation"] != entry["generation"]
   789	            or lineage["parent_acceptance_id"] != entry["parent_acceptance_id"]
   790	            or lineage["parent_artifact_sha256"] != parent_entry["artifact_sha256"]
   791	            or lineage["parent_derivation_sha256"] != parent["derivation_sha256"]
   792	            or lineage["parent_ledger_cutoff"] != parent_entry["ledger_cutoff"]
   793	            or artifact["prospective_rederivation"]["count_trigger"][
   794	                "next_boundary"
   795	            ]
   796	            != expected_boundary
   797	        ):
   798	            return None
   799	    return dict(value)
   800	
   801	
   802	def _active_registry_entry(registry: Mapping[str, Any]) -> Mapping[str, Any] | None:
   803	    active = [
   804	        entry
   805	        for entry in registry.get("entries", ())
   806	        if isinstance(entry, Mapping) and entry.get("active") is True
   807	    ]
   808	    return active[0] if len(active) == 1 else None
   809	
   810	
   811	def _valid_successor_acceptance_bound(value: Mapping[str, Any]) -> bool:
   812	    if (
   813	        set(value) != _SUCCESSOR_TOP_LEVEL_FIELDS
   814	        or value.get("schema_version") != ACCEPTANCE_SUCCESSOR_SCHEMA
   815	        or value.get("artifact_role") != "issued"
   816	        or not isinstance(value.get("acceptance_id"), str)
   817	        or not value["acceptance_id"].startswith("d079_calibration_acceptance_v3_s")
   818	        or value.get("decision_ids") != list(SUCCESSOR_DECISION_IDS)
   819	        or value.get("derivation_sha256")
   820	        != _canonical_sha256(
   821	            {key: item for key, item in value.items() if key != "derivation_sha256"}
   822	        )
   823	    ):
   824	        return False
   825	    issuance = value.get("issuance")
   826	    lineage = value.get("lineage")
   827	    cutoff = value.get("ledger_cutoff")
   828	    identity = value.get("identity_epoch")
   829	    prospective = value.get("prospective_rederivation")
   830	    corpus = value.get("derivation_corpus")
   831	    prior = value.get("prior_observation_set")
   832	    derivation = value.get("decimal_derivation")
   833	    if (
   834	        not isinstance(issuance, Mapping)
   835	        or set(issuance) != {"status", "claim_eligible", "reason"}
   836	        or issuance.get("status") != "issued"
   837	        or issuance.get("claim_eligible") is not True
   838	        or not isinstance(issuance.get("reason"), str)
   839	        or not issuance["reason"]
   840	        or not isinstance(cutoff, Mapping)
   841	        or set(cutoff) != {"sequence", "head_digest", "ledger_schema", "role"}
   842	        or isinstance(cutoff.get("sequence"), bool)
   843	        or not isinstance(cutoff.get("sequence"), int)
   844	        or cutoff["sequence"] < 1
   845	        or not _valid_sha256(cutoff.get("head_digest"))
   846	        or value["acceptance_id"]
   847	        != (
   848	            f"d079_calibration_acceptance_v3_s{cutoff['sequence']}_"
   849	            f"{cutoff['head_digest'][:16]}"
   850	        )
   851	        or cutoff.get("ledger_schema") != LEDGER_SCHEMA
   852	        or cutoff.get("role") != "issued_acceptance_baseline"
   853	        or not isinstance(identity, Mapping)
   854	        or set(identity) != set(ACCEPTANCE_IDENTITY_FIELDS)
   855	        or any(identity.get(field) in (None, "") for field in ACCEPTANCE_IDENTITY_FIELDS)
   856	    ):
   857	        return False
   858	    if (
   859	        not isinstance(lineage, Mapping)
   860	        or set(lineage)
   861	        != {
   862	            "generation",
   863	            "root_acceptance_id",
   864	            "parent_acceptance_id",
   865	            "parent_artifact_sha256",
   866	            "parent_derivation_sha256",
   867	            "parent_ledger_cutoff",
   868	            "trigger_judgment",
   869	        }
   870	        or isinstance(lineage.get("generation"), bool)
   871	        or not isinstance(lineage.get("generation"), int)
   872	        or lineage["generation"] < 2
   873	        or any(
   874	            not isinstance(lineage.get(field), str) or not lineage[field]
   875	            for field in ("root_acceptance_id", "parent_acceptance_id")
   876	        )
   877	        or not _valid_sha256(lineage.get("parent_artifact_sha256"))
   878	        or not _valid_sha256(lineage.get("parent_derivation_sha256"))
   879	        or not isinstance(lineage.get("parent_ledger_cutoff"), Mapping)
   880	        or set(lineage["parent_ledger_cutoff"])
   881	        != {"sequence", "head_digest", "ledger_schema"}
   882	        or isinstance(lineage["parent_ledger_cutoff"].get("sequence"), bool)
   883	        or not isinstance(lineage["parent_ledger_cutoff"].get("sequence"), int)
   884	        or lineage["parent_ledger_cutoff"]["sequence"] >= cutoff["sequence"]
   885	        or not _valid_sha256(lineage["parent_ledger_cutoff"].get("head_digest"))
   886	        or lineage["parent_ledger_cutoff"].get("ledger_schema") != LEDGER_SCHEMA
   887	        or not isinstance(lineage.get("trigger_judgment"), Mapping)
   888	    ):
   889	        return False
   890	    judgment = lineage["trigger_judgment"]
   891	    if (
   892	        set(judgment)
   893	        != {
   894	            "judged_under_acceptance_id",
   895	            "judged_under_artifact_sha256",
   896	            "result",
   897	            "new_content_ids",
   898	            "triggers",
   899	        }
   900	        or judgment.get("judged_under_acceptance_id")
   901	        != lineage["parent_acceptance_id"]
   902	        or judgment.get("judged_under_artifact_sha256")
   903	        != lineage["parent_artifact_sha256"]
   904	        or judgment.get("result") != "successor_required"
   905	        or not isinstance(judgment.get("new_content_ids"), list)
   906	        or judgment["new_content_ids"] != sorted(set(judgment["new_content_ids"]))
   907	        or not all(_valid_sha256(item) for item in judgment["new_content_ids"])
   908	        or not isinstance(judgment.get("triggers"), list)
   909	        or not judgment["triggers"]
   910	        or judgment["triggers"]
   911	        != [
   912	            trigger
   913	            for trigger in (
   914	                "new_valid_same_identity_capture_expands_observed_range",
   915	                "content_distinct_valid_same_epoch_count_boundary",
   916	            )
   917	            if trigger in judgment["triggers"]
   918	        ]
   919	    ):
   920	        return False
   921	    if (
   922	        not isinstance(prospective, Mapping)
   923	        or prospective.get("calendar_expiry") is not None
   924	        or prospective.get("trigger_observation_rule")
   925	        != "judge_under_prior_artifact_never_self_fit"
   926	        or prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
   927	        or prospective.get("estimator_code_sha256")
   928	        != _current_estimator_code_sha256()
   929	        or prospective.get("triggers")
   930	        != [
   931	            "identity_field_change",
   932	            "protocol_or_estimator_byte_change",
   933	            "new_valid_same_identity_capture_expands_observed_range",
   934	            "content_distinct_valid_same_epoch_count_boundary",
   935	            "new_systematic_failure_challenges_preflight_screen",
   936	        ]
   937	        or not isinstance(prospective.get("count_trigger"), Mapping)
   938	        or set(prospective["count_trigger"])
   939	        != {"source_corpus_count", "next_boundary", "rule"}
   940	        or prospective["count_trigger"].get("rule")
   941	        != SUCCESSOR_COUNT_BOUNDARY_RULE
   942	    ):
   943	        return False
   944	    if (
   945	        not isinstance(corpus, Mapping)
   946	        or set(corpus) != {"selection", "n", "members"}
   947	        or corpus.get("selection") != SUCCESSOR_CORPUS_SELECTION
   948	        or isinstance(corpus.get("n"), bool)
   949	        or not isinstance(corpus.get("n"), int)
   950	        or corpus["n"] < 2
   951	        or not isinstance(corpus.get("members"), list)
   952	        or len(corpus["members"]) != corpus["n"]
   953	        or prospective["count_trigger"].get("source_corpus_count") != corpus["n"]
   954	        or isinstance(prospective["count_trigger"].get("next_boundary"), bool)
   955	        or not isinstance(prospective["count_trigger"].get("next_boundary"), int)
   956	        or prospective["count_trigger"]["next_boundary"] <= corpus["n"]
   957	    ):
   958	        return False
   959	    member_keys = {
   960	        "content_id",
   961	        "attempt_id",
   962	        "finalization_sequence",
   963	        "receipt_digest",
   964	        "custody_locator",
   965	        "b_fiducial_s",
   966	        "manifest_sha256",
   967	        "instrument_evidence_sha256",
   968	    }
   969	    member_ids: list[str] = []
   970	    for member in corpus["members"]:
   971	        if (
   972	            not isinstance(member, Mapping)
   973	            or set(member) != member_keys
   974	            or not _valid_sha256(member.get("content_id"))
   975	            or not isinstance(member.get("attempt_id"), str)
   976	            or not member["attempt_id"]
   977	            or isinstance(member.get("finalization_sequence"), bool)
   978	            or not isinstance(member.get("finalization_sequence"), int)
   979	            or member["finalization_sequence"] < 1
   980	            or member["finalization_sequence"] > cutoff["sequence"]
   981	            or not _valid_sha256(member.get("receipt_digest"))
   982	            or not isinstance(member.get("custody_locator"), str)
   983	            or not member["custody_locator"]
   984	            or (bound := _decimal(member.get("b_fiducial_s"))) is None
   985	            or bound < 0
   986	            or not _valid_sha256(member.get("manifest_sha256"))
   987	            or not _valid_sha256(member.get("instrument_evidence_sha256"))
   988	        ):
   989	            return False
   990	        member_ids.append(member["content_id"])
   991	    if member_ids != sorted(set(member_ids)):
   992	        return False
   993	    if (
   994	        not isinstance(prior, Mapping)
   995	        or set(prior)
   996	        != {
   997	            "cutoff",
   998	            "content_identity_method",
   999	            "epoch_catalog",
  1000	            "observations",
  1001	            "noncontent_attempts",
  1002	        }
  1003	        or prior.get("cutoff")
  1004	        != {key: cutoff[key] for key in ("sequence", "head_digest", "ledger_schema")}
  1005	        or prior.get("content_identity_method")
  1006	        != "sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))"
  1007	        or not isinstance(prior.get("epoch_catalog"), Mapping)
  1008	        or prior["epoch_catalog"].get("active_epoch") != identity
  1009	        or any(
  1010	            not isinstance(epoch_id, str)
  1011	            or not epoch_id
  1012	            or not isinstance(epoch, Mapping)
  1013	            or set(epoch) != set(ACCEPTANCE_IDENTITY_FIELDS)
  1014	            or any(epoch.get(field) in (None, "") for field in ACCEPTANCE_IDENTITY_FIELDS)
  1015	            for epoch_id, epoch in prior["epoch_catalog"].items()
  1016	        )
  1017	        or len(
  1018	            {
  1019	                tuple((field, epoch[field]) for field in ACCEPTANCE_IDENTITY_FIELDS)
  1020	                for epoch in prior["epoch_catalog"].values()
  1021	            }
  1022	        )
  1023	        != len(prior["epoch_catalog"])
  1024	        or not isinstance(prior.get("observations"), list)
  1025	        or not isinstance(prior.get("noncontent_attempts"), list)
  1026	    ):
  1027	        return False
  1028	    for row in prior["noncontent_attempts"]:
  1029	        if (
  1030	            not isinstance(row, Mapping)
  1550	        if isinstance(row, Mapping) and _valid_sha256(row.get("content_id"))
  1551	    }
  1552	
  1553	
  1554	def _artifact_corpus_values(artifact: Mapping[str, Any]) -> tuple[Decimal, ...]:
  1555	    values = tuple(
  1556	        value
  1557	        for member in artifact["derivation_corpus"]["members"]
  1558	        if (value := _decimal(member.get("b_fiducial_s"))) is not None
  1559	    )
  1560	    return values
  1561	
  1562	
  1563	def _artifact_count_boundary(artifact: Mapping[str, Any]) -> int:
  1564	    if artifact.get("schema_version") == ACCEPTANCE_SUCCESSOR_SCHEMA:
  1565	        return int(
  1566	            artifact["prospective_rederivation"]["count_trigger"][
  1567	                "next_boundary"
  1568	            ]
  1569	        )
  1570	    return 38
  1571	
  1572	
  1573	def _probe_observation_universe(
  1574	    snapshot: CalibrationLedgerSnapshot,
  1575	) -> tuple[LedgerObservation, ...]:
  1576	    observations = list(snapshot.observations)
  1577	    visible_attempts = {observation.attempt_id for observation in observations}
  1578	    # U1 deliberately withholds open-session evidence from the ordinary
  1579	    # consumption universe. The pre-science probe is the one authorized reader
  1580	    # of a finalized PRE in that governed open capability.
  1581	    if snapshot.is_governed_open_bracket_extension:
  1582	        for session in snapshot.bracket_sessions:
  1583	            if session.state != "open":
  1584	                continue
  1585	            observations.extend(
  1586	                observation
  1587	                for observation in session.finalized_slots.values()
  1588	                if observation.attempt_id not in visible_attempts
  1589	            )
  1590	    return tuple(sorted(observations, key=lambda observation: observation.sequence))
  1591	
  1592	
  1593	def _group_probe_observations(
  1594	    observations: Sequence[LedgerObservation],
  1595	) -> tuple[dict[str, tuple[LedgerObservation, ...]], tuple[LedgerObservation, ...]] | None:
  1596	    grouped: dict[str, list[LedgerObservation]] = {}
  1597	    noncontent: list[LedgerObservation] = []
  1598	    for observation in observations:
  1599	        if observation.content_id is None:
  1600	            noncontent.append(observation)
  1601	            continue
  1602	        grouped.setdefault(observation.content_id, []).append(observation)
  1603	    result: dict[str, tuple[LedgerObservation, ...]] = {}
  1604	    for content_id, aliases in sorted(grouped.items()):
  1605	        ordered = tuple(sorted(aliases, key=lambda observation: observation.sequence))
  1606	        first = ordered[0]
  1607	        expected = (
  1608	            first.classification_disposition,
  1609	            dict(first.identity_epoch),
  1610	            dict(first.artifact_sha256),
  1611	            first.exact_bound_lexeme_s,
  1612	        )
  1613	        if any(
  1614	            (
  1615	                alias.classification_disposition,
  1616	                dict(alias.identity_epoch),
  1617	                dict(alias.artifact_sha256),
  1618	                alias.exact_bound_lexeme_s,
  1619	            )
  1620	            != expected
  1621	            for alias in ordered[1:]
  1622	        ):
  1623	            return None
  1624	        result[content_id] = ordered
  1625	    return result, tuple(sorted(noncontent, key=lambda observation: observation.sequence))
  1626	
  1627	
  1628	def _observation_custody_authentic(observation: LedgerObservation) -> bool:
  1629	    if observation.content_id is None or not observation.artifact_sha256:
  1630	        return False
  1631	    candidate = _candidate_from_observation(
  1632	        observation
  1633	        if observation.disposition == "valid"
  1634	        else replace(observation, disposition="valid")
  1635	    )
  1636	    return candidate is not None
  1637	
  1638	
  1639	def _probe_result(
  1640	    *,
  1641	    outcome: str,
  1642	    active: Mapping[str, Any] | None,
  1643	    artifact: Mapping[str, Any] | None,
  1644	    snapshot: CalibrationLedgerSnapshot,
  1645	    observed_identity_epoch: Mapping[str, Any] | None,
  1646	    new_content_ids: Sequence[str] = (),
  1647	    triggers: Sequence[str] = (),
  1648	    refusal_reasons: Sequence[str] = (),
  1649	) -> dict[str, Any]:
  1650	    cutoff = artifact.get("ledger_cutoff") if isinstance(artifact, Mapping) else None
  1651	    return {
  1652	        "schema_version": ACCEPTANCE_TRIGGER_PROBE_SCHEMA,
  1653	        "outcome": outcome,
  1654	        "active_acceptance_id": (
  1655	            artifact.get("acceptance_id") if isinstance(artifact, Mapping) else None
  1656	        ),
  1657	        "artifact_sha256": active.get("artifact_sha256") if active else None,
  1658	        "derivation_sha256": (
  1659	            artifact.get("derivation_sha256")
  1660	            if isinstance(artifact, Mapping)
  1661	            else None
  1662	        ),
  1663	        "parent_cutoff": (
  1664	            {
  1665	                key: cutoff.get(key)
  1666	                for key in ("sequence", "head_digest", "ledger_schema")
  1667	            }
  1668	            if isinstance(cutoff, Mapping)
  1669	            else None
  1670	        ),
  1671	        "current_ledger_head": {
  1672	            "sequence": snapshot.head_sequence,
  1673	            "head_digest": snapshot.head_digest,
  1674	            "ledger_schema": snapshot.ledger_schema,
  1675	            "committed_sequence": snapshot.committed_head_sequence,
  1676	            "committed_digest": snapshot.committed_head_digest,
  1677	        },
  1678	        "observed_identity_epoch": (
  1679	            dict(observed_identity_epoch)
  1680	            if isinstance(observed_identity_epoch, Mapping)
  1681	            else None
  1682	        ),
  1683	        "new_content_ids": list(new_content_ids),
  1684	        "observed_triggers": list(triggers),
  1685	        "refusal_reasons": list(refusal_reasons),
  1686	        "writer_integration_scope_status": WRITER_INTEGRATION_SCOPE_STATUS,
  1687	    }
  1688	
  1689	
  1690	def probe_calibration_acceptance_trigger(
  1691	    ledger_snapshot: CalibrationLedgerSnapshot,
  1692	    *,
  1693	    observed_identity_epoch: Mapping[str, Any] | None,
  1694	    registry_path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
  1695	    repo_root: Path = _REPO_ROOT,
  1696	    require_committed_registry: bool = True,
  1697	    verify_custody: bool = True,
  1698	) -> dict[str, Any]:
  1699	    """Authenticate the active artifact and classify the pre/post trigger.
  1700	
  1701	    This is the U2 hook shape for §5A. It performs no writes and returns one of
  1702	    the four closed outcomes required by the cold-gate brief.
  1703	    """
  1704	
  1705	    empty_snapshot = isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
  1706	    if not empty_snapshot:
  1707	        raise TypeError("ledger_snapshot must be a CalibrationLedgerSnapshot")
  1708	    registry = load_calibration_acceptance_registry(
  1709	        registry_path,
  1710	        repo_root=repo_root,
  1711	        require_committed=require_committed_registry,
  1712	    )
  1713	    active = _active_registry_entry(registry) if registry is not None else None
  1714	    artifact: dict[str, Any] | None = None
  1715	    if active is not None:
  1716	        try:
  1717	            raw = (Path(repo_root) / str(active["artifact_path"])).read_bytes()
  1718	        except OSError:
  1719	            raw = b""
  1720	        artifact = _acceptance_bound_from_authenticated_bytes(
  1721	            raw,
  1722	            expected_sha256=str(active["artifact_sha256"]),
  1723	        )
  1724	    if active is None or artifact is None:
  1725	        return _probe_result(
  1726	            outcome="authentication_or_epoch_refusal",
  1727	            active=active,
  1728	            artifact=artifact,
  1729	            snapshot=ledger_snapshot,
  1730	            observed_identity_epoch=observed_identity_epoch,
  1731	            refusal_reasons=("acceptance_registry_or_artifact_invalid",),
  1732	        )
  1733	    cutoff = artifact["ledger_cutoff"]
  1734	    allow_open = ledger_snapshot.is_governed_open_bracket_extension
  1735	    snapshot_reasons = set(ledger_snapshot.refusal_reasons)
  1736	    if (
  1737	        snapshot_reasons
  1738	        and not allow_open
  1739	        or allow_open
  1740	        and snapshot_reasons
  1741	        != {
  1742	            "calibration_ledger_bracket_session_open",
  1743	            "calibration_ledger_head_mismatch",
  1744	        }
  1745	        or ledger_snapshot.ledger_schema != LEDGER_SCHEMA
  1746	        or ledger_snapshot.head_sequence < cutoff["sequence"]
  1747	        or cutoff["sequence"] > len(ledger_snapshot.receipts)
  1748	        or cutoff["sequence"] > 0
  1749	        and ledger_snapshot.receipts[cutoff["sequence"] - 1].get("receipt_digest")
  1750	        != cutoff["head_digest"]
  1751	        or ledger_snapshot.head_sequence != len(ledger_snapshot.receipts)
  1752	        or ledger_snapshot.head_sequence > 0
  1753	        and ledger_snapshot.receipts[-1].get("receipt_digest")
  1754	        != ledger_snapshot.head_digest
  1755	        or not _prior_set_matches_import_cutoff_prefix(artifact, ledger_snapshot)
  1756	    ):
  1757	        return _probe_result(
  1758	            outcome="authentication_or_epoch_refusal",
  1759	            active=active,
  1760	            artifact=artifact,
  1761	            snapshot=ledger_snapshot,
  1762	            observed_identity_epoch=observed_identity_epoch,
  1763	            refusal_reasons=("calibration_ledger_prefix_not_authenticated",),
  1764	        )
  1765	    expected_epoch = artifact["identity_epoch"]
  1766	    if (
  1767	        not isinstance(observed_identity_epoch, Mapping)
  1768	        or set(observed_identity_epoch) != set(ACCEPTANCE_IDENTITY_FIELDS)
  1769	        or any(
  1770	            observed_identity_epoch.get(field) != expected_epoch.get(field)
  1771	            for field in ACCEPTANCE_IDENTITY_FIELDS
  1772	        )
  1773	    ):
  1774	        return _probe_result(
  1775	            outcome="authentication_or_epoch_refusal",
  1776	            active=active,
  1777	            artifact=artifact,
  1778	            snapshot=ledger_snapshot,
  1779	            observed_identity_epoch=observed_identity_epoch,
  1780	            triggers=("identity_field_change",),
  1781	            refusal_reasons=("observed_identity_epoch_mismatch",),
  1782	        )
  1783	    prospective = artifact["prospective_rederivation"]
  1784	    if (
  1785	        prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
  1786	        or prospective.get("estimator_code_sha256")
  1787	        != _current_estimator_code_sha256()
  1788	    ):
  1789	        return _probe_result(
  1790	            outcome="authentication_or_epoch_refusal",
  1791	            active=active,
  1792	            artifact=artifact,
  1793	            snapshot=ledger_snapshot,
  1794	            observed_identity_epoch=observed_identity_epoch,
  1795	            triggers=("protocol_or_estimator_byte_change",),
  1796	            refusal_reasons=("protocol_or_estimator_bytes_changed",),
  1797	        )
  1798	    grouped_result = _group_probe_observations(
  1799	        _probe_observation_universe(ledger_snapshot)
  1800	    )
  1801	    if grouped_result is None:
  1802	        return _probe_result(
  1803	            outcome="authentication_or_epoch_refusal",
  1804	            active=active,
  1805	            artifact=artifact,
  1806	            snapshot=ledger_snapshot,
  1807	            observed_identity_epoch=observed_identity_epoch,
  1808	            refusal_reasons=("conflicting_content_classification_or_bytes",),
  1809	        )
  1810	    grouped, noncontent = grouped_result
  1811	    prior_ids = _artifact_prior_content_ids(artifact)
  1812	    new_ids = sorted(set(grouped) - prior_ids)
  1813	    new_observations = [grouped[content_id][0] for content_id in new_ids]
  1814	    new_noncontent = [
  1815	        observation
  1816	        for observation in noncontent
  1817	        if observation.sequence > cutoff["sequence"]
  1818	    ]
  1819	    if new_noncontent or any(
  1820	        observation.classification_disposition
  1821	        not in {"valid", "systematic-invalid", "ordinary-invalid"}
  1822	        for observation in new_observations
  1823	    ):
  1824	        return _probe_result(
  1825	            outcome="authentication_or_epoch_refusal",
  1826	            active=active,
  1827	            artifact=artifact,
  1828	            snapshot=ledger_snapshot,
  1829	            observed_identity_epoch=observed_identity_epoch,
  1830	            new_content_ids=new_ids,
  1831	            refusal_reasons=("unresolved_or_unclassifiable_observation",),
  1832	        )
  1833	    if verify_custody and any(
  1834	        not _observation_custody_authentic(observation)
  1835	        for observation in new_observations
  1836	    ):
  1837	        return _probe_result(
  1838	            outcome="authentication_or_epoch_refusal",
  1839	            active=active,
  1840	            artifact=artifact,
  1841	            snapshot=ledger_snapshot,
  1842	            observed_identity_epoch=observed_identity_epoch,
  1843	            new_content_ids=new_ids,
  1844	            refusal_reasons=("new_observation_custody_or_physics_invalid",),
  1845	        )
  1846	    preflight = _decimal(
  1847	        artifact["decimal_derivation"]["ratified_operatives"][
  1848	            "preflight_level_screen_s"
  1849	        ]
  1850	    )
  1851	    if preflight is None:
  1852	        return _probe_result(
  1853	            outcome="authentication_or_epoch_refusal",
  1854	            active=active,
  1855	            artifact=artifact,
  1856	            snapshot=ledger_snapshot,
  1857	            observed_identity_epoch=observed_identity_epoch,
  1858	            refusal_reasons=("active_preflight_screen_invalid",),
  1859	        )
  1860	    systematic = [
  1861	        observation
  1862	        for observation in new_observations
  1863	        if dict(observation.identity_epoch) == dict(expected_epoch)
  1864	        and (
  1865	            observation.classification_disposition == "systematic-invalid"
  1866	            or observation.classification_disposition == "valid"
  1867	            and (
  1868	                (bound := _decimal(observation.exact_bound_lexeme_s)) is None
  1869	                or bound > preflight
  1870	            )
  1871	        )
  1872	    ]
  1873	    if systematic:
  1874	        return _probe_result(
  1875	            outcome="systematic_refusal",
  1876	            active=active,
  1877	            artifact=artifact,
  1878	            snapshot=ledger_snapshot,
  1879	            observed_identity_epoch=observed_identity_epoch,
  1880	            new_content_ids=new_ids,
  1881	            triggers=("new_systematic_failure_challenges_preflight_screen",),
  1882	            refusal_reasons=(SUCCESSOR_SYSTEMATIC_POLICY,),
  1883	        )
  1884	    corpus_values = _artifact_corpus_values(artifact)
  1885	    if not corpus_values:
  1886	        return _probe_result(
  1887	            outcome="authentication_or_epoch_refusal",
  1888	            active=active,
  1889	            artifact=artifact,
  1890	            snapshot=ledger_snapshot,
  1891	            observed_identity_epoch=observed_identity_epoch,
  1892	            refusal_reasons=("active_derivation_corpus_invalid",),
  1893	        )
  1894	    new_valid_same_epoch = [
  1895	        observation
  1896	        for observation in new_observations
  1897	        if observation.classification_disposition == "valid"
  1898	        and dict(observation.identity_epoch) == dict(expected_epoch)
  1899	    ]
  1900	    triggers: list[str] = []
  1901	    if any(
  1902	        (bound := _decimal(observation.exact_bound_lexeme_s)) is not None
  1903	        and (bound < min(corpus_values) or bound > max(corpus_values))
  1904	        for observation in new_valid_same_epoch
  1905	    ):
  1906	        triggers.append("new_valid_same_identity_capture_expands_observed_range")
  1907	    total_valid_same_epoch = sum(
  1908	        aliases[0].classification_disposition == "valid"
  1909	        and dict(aliases[0].identity_epoch) == dict(expected_epoch)
  1910	        for aliases in grouped.values()
  1911	    )
  1912	    if total_valid_same_epoch >= _artifact_count_boundary(artifact):
  1913	        triggers.append("content_distinct_valid_same_epoch_count_boundary")
  1914	    outcome = "successor_required" if triggers else "accepted_under_active_artifact"
  1915	    return _probe_result(
     1	#!/usr/bin/env python3
     2	"""Build and optionally publish one deterministic D-102 successor artifact.
     3	
     4	Dry-run is the default. Issuance publishes immutable artifact bytes first and
     5	switches the committed registry last; it never writes the ledger head pin.
     6	"""
     7	
     8	from __future__ import annotations
     9	
    10	import argparse
    11	import fcntl
    12	import hashlib
    13	import json
    14	import os
    15	import stat
    16	import sys
    17	import tempfile
    18	from dataclasses import dataclass
    19	from pathlib import Path
    20	from typing import Any, Mapping, Sequence
    21	
    22	REPO_ROOT = Path(__file__).resolve().parents[1]
    23	if str(REPO_ROOT) not in sys.path:
    24	    sys.path.insert(0, str(REPO_ROOT))
    25	
    26	from joulewise.calibration_bracketing import (  # noqa: E402
    27	    ACCEPTANCE_IDENTITY_FIELDS,
    28	    ACCEPTANCE_REGISTRY_SCHEMA,
    29	    ACCEPTANCE_REGISTRY_AUTHORITY,
    30	    ACCEPTANCE_SUCCESSOR_SCHEMA,
    31	    DEFAULT_ACCEPTANCE_REGISTRY_PATH,
    32	    POST_SUCCESSOR_POLICY,
    33	    SUCCESSOR_CORPUS_SELECTION,
    34	    SUCCESSOR_COUNT_BOUNDARY_RULE,
    35	    SUCCESSOR_DECISION_IDS,
    36	    SUCCESSOR_PUBLICATION_POLICY,
    37	    SUCCESSOR_QUANTILE_METHOD,
    38	    _active_registry_entry,
    39	    _artifact_count_boundary,
    40	    _canonical_sha256,
    41	    _group_probe_observations,
    42	    _observation_custody_authentic,
    43	    _probe_observation_universe,
    44	    _valid_acceptance_bound,
    45	    _valid_registry,
    46	    derive_successor_decimal_derivation,
    47	    load_calibration_acceptance_registry,
    48	    probe_calibration_acceptance_trigger,
    49	)
    50	from joulewise.calibration_ledger import (  # noqa: E402
    51	    BRACKET_SESSION_ABORT_EVENT,
    52	    DEFAULT_HEAD_PIN_PATH,
    53	    DEFAULT_LEDGER_PATH,
    54	    LEDGER_SCHEMA,
    55	    CalibrationLedgerSnapshot,
    56	    LedgerObservation,
    57	    load_calibration_ledger_snapshot,
    58	)
    59	from joulewise.powermetrics_fiducial import PROTOCOL_ID, protocol_sha256  # noqa: E402
    60	
    61	
    62	BUILD_OUTPUT_SCHEMA = "joulewise.calibration_acceptance_successor_build.v1"
    63	CONTENT_IDENTITY_METHOD = (
    64	    "sha256(canonical_json({instrument_evidence.json,manifest.json} byte sha256s))"
    65	)
    66	
    67	
    68	@dataclass(frozen=True)
    69	class SuccessorBuild:
    70	    artifact: Mapping[str, Any]
    71	    artifact_bytes: bytes
    72	    artifact_sha256: str
    73	    registry: Mapping[str, Any]
    74	    registry_bytes: bytes
    75	    registry_sha256: str
    76	    artifact_path: str
    77	    head_pin: Mapping[str, Any]
    78	    parent_probe: Mapping[str, Any]
    79	    successor_probe: Mapping[str, Any]
    80	
    81	    def output_record(self) -> dict[str, Any]:
    82	        return {
    83	            "schema_version": BUILD_OUTPUT_SCHEMA,
    84	            "publication_policy": SUCCESSOR_PUBLICATION_POLICY,
    85	            "artifact_path": self.artifact_path,
    86	            "artifact_sha256": self.artifact_sha256,
    87	            "derivation_sha256": self.artifact["derivation_sha256"],
    88	            "artifact_file_content": self.artifact_bytes.decode("utf-8"),
    89	            "registry_sha256": self.registry_sha256,
    90	            "registry_file_content": self.registry_bytes.decode("utf-8"),
    91	            "proposed_registry_entry": next(
    92	                entry
    93	                for entry in self.registry["entries"]
    94	                if entry["active"] is True
    95	            ),
    96	            "proposed_head_pin": dict(self.head_pin),
    97	            "parent_probe": dict(self.parent_probe),
    98	            "successor_probe": dict(self.successor_probe),
    99	        }
   100	
   101	
   102	class SuccessorDurabilityUncertain(RuntimeError):
   103	    """Registry authority switched, but its directory sync failed."""
   104	
   105	
   106	def _pretty_json_bytes(value: Mapping[str, Any]) -> bytes:
   107	    return (
   108	        json.dumps(
   109	            dict(value),
   110	            sort_keys=True,
   111	            ensure_ascii=False,
   112	            allow_nan=False,
   113	            indent=2,
   114	        )
   115	        + "\n"
   116	    ).encode("utf-8")
   117	
   118	
   119	def _epoch_id(epoch: Mapping[str, Any], active: Mapping[str, Any]) -> str:
   120	    if dict(epoch) == dict(active):
   121	        return "active_epoch"
   122	    raw = json.dumps(
   123	        dict(epoch),
   124	        sort_keys=True,
   125	        separators=(",", ":"),
   126	        ensure_ascii=False,
   127	        allow_nan=False,
   128	    ).encode("utf-8")
   129	    return f"epoch_{hashlib.sha256(raw).hexdigest()[:16]}"
   130	
   131	
   132	def _attempt_row(observation: LedgerObservation) -> dict[str, Any]:
   133	    return {
   134	        "attempt_id": observation.attempt_id,
   135	        "finalization_sequence": observation.sequence,
   136	        "receipt_digest": observation.receipt_digest,
   137	        "observation_kind": observation.observation_kind,
   138	        "custody_locator": observation.custody_locator,
   139	        "exact_bound_lexeme_s": observation.exact_bound_lexeme_s,
   140	        "manifest_sha256": observation.artifact_sha256.get("manifest.json"),
   141	        "instrument_evidence_sha256": observation.artifact_sha256.get(
   142	            "instrument_evidence.json"
   143	        ),
   144	    }
   145	
   146	
   147	def _governed_unused_slots(
   148	    snapshot: CalibrationLedgerSnapshot,
   149	) -> list[dict[str, Any]]:
   150	    """Record only unused U1 slots whose terminal abort proves no capture."""
   151	
   152	    rows: list[dict[str, Any]] = []
   153	    receipts_by_session: dict[str, list[Mapping[str, Any]]] = {}
   154	    for receipt in snapshot.receipts:
   155	        session_id = receipt.get("session_id")
   156	        if isinstance(session_id, str):
   157	            receipts_by_session.setdefault(session_id, []).append(receipt)
   158	    for session in snapshot.bracket_sessions:
   159	        if session.state != "aborted":
   160	            continue
   161	        receipts = receipts_by_session.get(session.session_id, [])
   162	        opens = [receipt for receipt in receipts if receipt.get("event") == "bracket-session-open"]
   163	        aborts = [
   164	            receipt
   165	            for receipt in receipts
   166	            if receipt.get("event") == BRACKET_SESSION_ABORT_EVENT
   167	        ]
   168	        if len(opens) != 1 or len(aborts) != 1:
   169	            raise ValueError("aborted bracket session lacks one authenticated closure")
   170	        opened = opens[0]
   171	        aborted = aborts[0]
   172	        for slot in aborted["unused_slots"]:
   173	            reservation = opened["slots"][slot]
   174	            rows.append(
   175	                {
   176	                    "attempt_id": reservation["attempt_id"],
   177	                    "closure_sequence": aborted["sequence"],
   178	                    "receipt_digest": aborted["receipt_digest"],
   179	                    "disposition": "governed-unused-slot",
   180	                    "custody_locator": reservation["custody_locator"],
   181	                }
   182	            )
   183	    return rows
   184	
   185	
   186	def _noncontent_rows(
   187	    noncontent: Sequence[LedgerObservation],
   188	    snapshot: CalibrationLedgerSnapshot,
   189	) -> list[dict[str, Any]]:
   190	    if noncontent:
   191	        # A terminal `abandoned` receipt can still conceal already-created
   192	        # classifiable bytes. Q6 requires a ruling before automatic issuance.
   193	        raise ValueError("noncontent observation blocks automatic successor issuance")
   194	    return sorted(
   195	        _governed_unused_slots(snapshot),
   196	        key=lambda row: (row["closure_sequence"], row["attempt_id"]),
   197	    )
   198	
   199	
   200	def _load_parent_artifact(
   201	    registry: Mapping[str, Any], repo_root: Path
   202	) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
   203	    active = _active_registry_entry(registry)
   204	    if active is None:
   205	        raise ValueError("acceptance registry does not have one active entry")
   206	    path = repo_root / str(active["artifact_path"])
   207	    try:
   208	        raw = path.read_bytes()
   209	        artifact = json.loads(raw)
   210	    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
   211	        raise ValueError("active acceptance artifact is unreadable") from exc
   212	    if (
   213	        hashlib.sha256(raw).hexdigest() != active["artifact_sha256"]
   214	        or not _valid_acceptance_bound(artifact)
   215	    ):
   216	        raise ValueError("active acceptance artifact is not registry-authenticated")
   217	    return active, artifact
   218	
   219	
   220	def _assert_terminal_committed_snapshot(snapshot: CalibrationLedgerSnapshot) -> None:
   221	    if (
   222	        not snapshot.valid
   223	        or snapshot.head_sequence < 1
   224	        or snapshot.head_sequence != len(snapshot.receipts)
   225	        or snapshot.committed_head_sequence != snapshot.head_sequence
   226	        or snapshot.committed_head_digest != snapshot.head_digest
   227	        or snapshot.receipts[-1].get("receipt_digest") != snapshot.head_digest
   228	        or snapshot.receipts[-1].get("event")
   229	        in {"reservation", "bracket-session-open", "bracket-session-slot-claim"}
   230	    ):
   231	        raise ValueError("successor issuance requires a committed terminal ledger head")
   232	
   233	
   234	def build_calibration_acceptance_successor(
   235	    ledger_snapshot: CalibrationLedgerSnapshot,
   236	    *,
   237	    observed_identity_epoch: Mapping[str, Any],
   238	    registry_path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
   239	    repo_root: Path = REPO_ROOT,
   240	    require_committed_registry: bool = True,
   241	    verify_custody: bool = True,
   242	) -> SuccessorBuild:
   243	    """Build deterministic artifact and registry buffers without writing."""
   244	
   245	    repo_root = Path(repo_root).resolve()
   246	    _assert_terminal_committed_snapshot(ledger_snapshot)
   247	    registry = load_calibration_acceptance_registry(
   248	        registry_path,
   249	        repo_root=repo_root,
   250	        require_committed=require_committed_registry,
   251	    )
   252	    if registry is None:
   253	        raise ValueError("acceptance registry is invalid or uncommitted")
   254	    parent_entry, parent = _load_parent_artifact(registry, repo_root)
   255	    parent_probe = probe_calibration_acceptance_trigger(
   256	        ledger_snapshot,
   257	        observed_identity_epoch=observed_identity_epoch,
   258	        registry_path=registry_path,
   259	        repo_root=repo_root,
   260	        require_committed_registry=require_committed_registry,
   261	        verify_custody=verify_custody,
   262	    )
   263	    if parent_probe["outcome"] != "successor_required":
   264	        raise ValueError(
   265	            f"active artifact does not require a successor: {parent_probe['outcome']}"
   266	        )
   267	
   268	    grouped_result = _group_probe_observations(
   269	        _probe_observation_universe(ledger_snapshot)
   270	    )
   271	    if grouped_result is None:
   272	        raise ValueError("content identity has conflicting classifications or bytes")
   273	    grouped, noncontent = grouped_result
   274	    noncontent_rows = _noncontent_rows(noncontent, ledger_snapshot)
   275	    active_epoch = dict(parent["identity_epoch"])
   276	    if dict(observed_identity_epoch) != active_epoch:
   277	        raise ValueError("observed identity epoch differs from the parent artifact")
   278	
   279	    epoch_values: dict[str, dict[str, Any]] = {"active_epoch": active_epoch}
   280	    prior_rows: list[dict[str, Any]] = []
   281	    corpus_members: list[dict[str, Any]] = []
   282	    for content_id, aliases in grouped.items():
   283	        representative = aliases[0]
   284	        epoch_id = _epoch_id(representative.identity_epoch, active_epoch)
   285	        epoch_values.setdefault(epoch_id, dict(representative.identity_epoch))
   286	        prior_rows.append(
   287	            {
   288	                "content_id": content_id,
   289	                "epoch_id": epoch_id,
   290	                "disposition": representative.classification_disposition,
   291	                "representative_attempt_id": representative.attempt_id,
   292	                "attempts": [_attempt_row(alias) for alias in aliases],
   293	            }
   294	        )
   295	        if (
   296	            representative.classification_disposition != "valid"
   297	            or epoch_id != "active_epoch"
   298	        ):
   299	            continue
   300	        if verify_custody and any(
   301	            not _observation_custody_authentic(alias) for alias in aliases
   302	        ):
   303	            raise ValueError("selected corpus member fails custody reauthentication")
   304	        bound = representative.exact_bound_lexeme_s
   305	        if not isinstance(bound, str):
   306	            raise ValueError("selected corpus member lacks an exact bound lexeme")
   307	        corpus_members.append(
   308	            {
   309	                "content_id": content_id,
   310	                "attempt_id": representative.attempt_id,
   311	                "finalization_sequence": representative.sequence,
   312	                "receipt_digest": representative.receipt_digest,
   313	                "custody_locator": representative.custody_locator,
   314	                "b_fiducial_s": bound,
   315	                "manifest_sha256": representative.artifact_sha256.get(
   316	                    "manifest.json"
   317	                ),
   318	                "instrument_evidence_sha256": representative.artifact_sha256.get(
   319	                    "instrument_evidence.json"
   320	                ),
   321	            }
   322	        )
   323	    prior_rows.sort(key=lambda row: row["content_id"])
   324	    corpus_members.sort(key=lambda member: member["content_id"])
   325	    if len(corpus_members) < 2:
   326	        raise ValueError("successor corpus has fewer than two valid same-epoch members")
   327	
   328	    derivation = derive_successor_decimal_derivation(corpus_members)
   329	    parent_boundary = _artifact_count_boundary(parent)
   330	    count = len(corpus_members)
   331	    next_boundary = parent_boundary if count < parent_boundary else 2 * count
   332	    cutoff_core = {
   333	        "sequence": ledger_snapshot.head_sequence,
   334	        "head_digest": ledger_snapshot.head_digest,
   335	        "ledger_schema": LEDGER_SCHEMA,
   336	    }
   337	    acceptance_id = (
   338	        f"d079_calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
   339	        f"{ledger_snapshot.head_digest[:16]}"
   340	    )
   341	    artifact_path = (
   342	        "configs/calibration/"
   343	        f"calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
   344	        f"{ledger_snapshot.head_digest[:16]}.json"
   345	    )
   346	    root_acceptance_id = (
   347	        parent["lineage"]["root_acceptance_id"]
   348	        if parent.get("schema_version") == ACCEPTANCE_SUCCESSOR_SCHEMA
   349	        else parent["acceptance_id"]
   350	    )
   351	    parent_cutoff = {
   352	        key: parent["ledger_cutoff"][key]
   353	        for key in ("sequence", "head_digest", "ledger_schema")
   354	    }
   355	    artifact: dict[str, Any] = {
   356	        "schema_version": ACCEPTANCE_SUCCESSOR_SCHEMA,
   357	        "acceptance_id": acceptance_id,
   358	        "decision_ids": list(SUCCESSOR_DECISION_IDS),
   359	        "artifact_role": "issued",
   360	        "issuance": {
   361	            "status": "issued",
   362	            "claim_eligible": True,
   363	            "reason": (
   364	                "authenticated live-prefix trigger judged under the parent "
   365	                "artifact and rederived under D-102/D-109/D-117"
   366	            ),
   367	        },
   368	        "lineage": {
   369	            "generation": int(parent_entry["generation"]) + 1,
   370	            "root_acceptance_id": root_acceptance_id,
   371	            "parent_acceptance_id": parent["acceptance_id"],
   372	            "parent_artifact_sha256": parent_entry["artifact_sha256"],
   373	            "parent_derivation_sha256": parent["derivation_sha256"],
   374	            "parent_ledger_cutoff": parent_cutoff,
   375	            "trigger_judgment": {
   376	                "judged_under_acceptance_id": parent["acceptance_id"],
   377	                "judged_under_artifact_sha256": parent_entry["artifact_sha256"],
   378	                "result": "successor_required",
   379	                "new_content_ids": list(parent_probe["new_content_ids"]),
   380	                "triggers": list(parent_probe["observed_triggers"]),
   381	            },
   382	        },
   383	        "ledger_cutoff": {**cutoff_core, "role": "issued_acceptance_baseline"},
   384	        "identity_epoch": active_epoch,
   385	        "prospective_rederivation": {
   386	            "calendar_expiry": None,
   387	            "trigger_observation_rule": "judge_under_prior_artifact_never_self_fit",
   388	            "triggers": [
   389	                "identity_field_change",
   390	                "protocol_or_estimator_byte_change",
   391	                "new_valid_same_identity_capture_expands_observed_range",
   392	                "content_distinct_valid_same_epoch_count_boundary",
   393	                "new_systematic_failure_challenges_preflight_screen",
   394	            ],
   395	            "protocol_sha256": protocol_sha256(PROTOCOL_ID),
   396	            "estimator_code_sha256": parent["prospective_rederivation"][
   397	                "estimator_code_sha256"
   398	            ],
   399	            "count_trigger": {
   400	                "source_corpus_count": count,
   401	                "next_boundary": next_boundary,
   402	                "rule": SUCCESSOR_COUNT_BOUNDARY_RULE,
   403	            },
   404	        },
   405	        "derivation_corpus": {
   406	            "selection": SUCCESSOR_CORPUS_SELECTION,
   407	            "n": count,
   408	            "members": corpus_members,
   409	        },
   410	        "prior_observation_set": {
   411	            "cutoff": cutoff_core,
   412	            "content_identity_method": CONTENT_IDENTITY_METHOD,
   413	            "epoch_catalog": dict(sorted(epoch_values.items())),
   414	            "observations": prior_rows,
   415	            "noncontent_attempts": noncontent_rows,
   416	        },
   417	        "decimal_derivation": derivation,
   418	    }
   419	    artifact["derivation_sha256"] = _canonical_sha256(artifact)
   420	    if not _valid_acceptance_bound(artifact):
   421	        raise ValueError("constructed successor fails the production loader")
   422	    artifact_bytes = _pretty_json_bytes(artifact)
   423	    artifact_sha256 = hashlib.sha256(artifact_bytes).hexdigest()
   424	
   425	    registry_entries = []
   426	    for entry in registry["entries"]:
   427	        registry_entries.append({**entry, "active": False})
   428	    registry_entries.append(
   429	        {
   430	            "acceptance_id": acceptance_id,
   431	            "artifact_path": artifact_path,
   432	            "artifact_sha256": artifact_sha256,
   433	            "derivation_sha256": artifact["derivation_sha256"],
   434	            "artifact_schema": ACCEPTANCE_SUCCESSOR_SCHEMA,
   435	            "generation": int(parent_entry["generation"]) + 1,
   436	            "active": True,
   437	            "parent_acceptance_id": parent["acceptance_id"],
   438	            "parent_artifact_sha256": parent_entry["artifact_sha256"],
   439	            "ledger_cutoff": cutoff_core,
   440	        }
   441	    )
   442	    proposed_registry = {
   443	        "schema_version": ACCEPTANCE_REGISTRY_SCHEMA,
   444	        "authority": ACCEPTANCE_REGISTRY_AUTHORITY,
   445	        "entries": registry_entries,
   446	    }
   447	    if not _valid_registry(proposed_registry):
   448	        raise ValueError("constructed registry fails ancestry validation")
   449	    registry_bytes = _pretty_json_bytes(proposed_registry)
   450	
   451	    # Step 16's self-fit guard is explicit: every parent-new content ID is now
   452	    # in the successor prior set, while the next count boundary is above n.
   453	    successor_prior_ids = {row["content_id"] for row in prior_rows}
   454	    if not set(parent_probe["new_content_ids"]).issubset(successor_prior_ids):
   455	        raise ValueError("successor omits a parent-judged trigger observation")
   456	    successor_probe = {
   457	        "outcome": "accepted_under_active_artifact",
   458	        "active_acceptance_id": acceptance_id,
   459	        "new_content_ids": [],
   460	        "observed_triggers": [],
   461	        "parent_judgment_policy": POST_SUCCESSOR_POLICY,
   462	    }
   463	    return SuccessorBuild(
   464	        artifact=artifact,
   465	        artifact_bytes=artifact_bytes,
   466	        artifact_sha256=artifact_sha256,
   467	        registry=proposed_registry,
   468	        registry_bytes=registry_bytes,
   469	        registry_sha256=hashlib.sha256(registry_bytes).hexdigest(),
   470	        artifact_path=artifact_path,
   471	        head_pin=cutoff_core,
   472	        parent_probe=parent_probe,
   473	        successor_probe=successor_probe,
   474	    )
   475	
   476	
   477	def _stage_bytes(destination: Path, payload: bytes) -> Path:
   478	    destination.parent.mkdir(parents=True, exist_ok=True)
   479	    descriptor, name = tempfile.mkstemp(
   480	        prefix=f".{destination.name}.", suffix=".stage", dir=destination.parent
   481	    )
   482	    staged = Path(name)
   483	    try:
   484	        with os.fdopen(descriptor, "wb") as handle:
   485	            handle.write(payload)
   486	            handle.flush()
   487	            os.fsync(handle.fileno())
   488	    except BaseException:
   489	        staged.unlink(missing_ok=True)
   490	        raise
   491	    return staged
   492	
   493	
   494	def _fsync_directory(path: Path) -> None:
   495	    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
   496	    try:
   497	        os.fsync(descriptor)
   498	    finally:
   499	        os.close(descriptor)
   500	
   501	
   502	def publish_successor(
   503	    build: SuccessorBuild,
   504	    *,
   505	    artifact_destination: Path,
   506	    registry_destination: Path,
   507	    expected_registry_bytes: bytes,
   508	    repo_root: Path = REPO_ROOT,
   509	) -> None:
   510	    """Publish validated buffers with the registry as the commit point."""
   511	
   512	    repo_root = Path(repo_root).resolve()
   513	    artifact_destination = Path(artifact_destination)
   514	    registry_destination = Path(registry_destination)
   515	    expected_artifact = repo_root / build.artifact_path
   516	    expected_registry = (
   517	        repo_root / "configs/calibration/calibration_acceptance_registry.json"
   518	    )
   519	    if (
   520	        artifact_destination.resolve(strict=False)
   850	    }
   851	    ledger_lifecycle.identity_epoch = {
   852	        field: bindings.get(field)
   853	        for field in (
   854	            "os_build",
   855	            "hardware_model",
   856	            "power_policy",
   857	            "sampling_interval_ms",
   858	            "estimator_revision",
   859	            "pulse_protocol_id",
   860	        )
   861	    }
   862	    ledger_lifecycle.t1_bindings = bindings
   863	    ledger_lifecycle.capture_wall_time_s = str(sampling_started.epoch_s)
   864	    evidence_payload = instrument_evidence(
   865	        detection,
   866	        bindings=bindings,
   867	        validation_id=validation_id,
   868	        artifact_sha256={
   869	            "raw/powermetrics.plist": sha256_path(capture_path),
   870	            "events.jsonl": sha256_path(events_path),
   871	            "power_trace.csv": sha256_path(trace_path),
   872	        },
   873	        capture_wall_time_s=sampling_started.epoch_s,
   874	    )
   875	    evidence_payload["clock_anchor"] = evidence["clock_anchor"]
   876	    evidence_payload["clock_anchor_resolved"] = anchor_resolved
   877	    if not anchor_resolved:
   878	        evidence_payload["status"] = "invalid"
   879	        evidence_payload["reasons"] = sorted(
   880	            set(evidence_payload.get("reasons", [])) | {"clock_anchor_unresolved"}
   881	        )
   882	    (out_dir / "instrument_evidence.json").write_text(
   883	        json.dumps(evidence_payload, indent=2, sort_keys=True) + "\n",
   884	        encoding="utf-8",
   885	    )
   886	    manifest = {
   887	        "schema_version": "joulewise.instrument_validation_manifest.v1",
   888	        "validation_id": validation_id,
   889	        "protocol_id": PROTOCOL_ID,
   890	        "pulse_count": args.pulse_count,
   891	        "artifacts": {
   892	            name: sha256_path(out_dir / name)
   893	            for name in (
   894	                "events.jsonl",
   895	                "power_trace.csv",
   896	                "instrument_evidence.json",
   897	            )
   898	        }
   899	        | {"raw/powermetrics.plist": sha256_path(capture_path)},
   900	    }
   901	    (out_dir / "manifest.json").write_text(
   902	        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
   903	    )
   904	    serialized_evidence = json.loads(
   905	        json.dumps(evidence_payload, sort_keys=True),
   906	        parse_float=str,
   907	        parse_int=str,
   908	    )
   909	    bound_lexeme = serialized_evidence.get("b_fiducial_s")
   910	    ledger_lifecycle.exact_bound_lexeme_s = (
   911	        bound_lexeme if isinstance(bound_lexeme, str) else None
   912	    )
   913	    disposition = "ordinary-invalid"
   914	    if evidence_payload["status"] == "valid":
   915	        disposition = (
   916	            "systematic-invalid"
   917	            if isinstance(bound_lexeme, str)
   918	            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
   919	            else "valid"
   920	        )
   921	    _final_receipt, head_pin_candidate = ledger_lifecycle.finalize(disposition)
   922	    atexit.unregister(finalize_abandoned)
   923	    output = {
   924	        "validation_id": validation_id,
   925	        "status": evidence_payload["status"],
   926	        "b_fiducial_s": evidence_payload["b_fiducial_s"],
   927	        "output": str(out_dir),
   928	        "ledger_head_pin_candidate": head_pin_candidate,
   929	        "claim_evaluation_blocked_until_pin_commit": True,
   930	    }
   931	    if bracket_mode:
   932	        output["bracket_session"] = {
   933	            "session_id": args.session_id,
   934	            "slot": args.slot,
   935	            "attempt_id": args.attempt_id,
   936	        }
   937	    print(json.dumps(output, indent=2))
   938	    return 0 if disposition == "valid" else 1
   939	
   940	
   941	if __name__ == "__main__":
   942	    raise SystemExit(main())

exec
/bin/zsh -lc "git grep -n 'PREFLIGHT_SYSTEMATIC_SCREEN_S' origin/impl/d117-u2-successor --
git diff --unified=20 main...origin/impl/d117-u2-successor -- scripts/validate_powermetrics_fiducial.py | sed -n '1,260p'
git show origin/impl/d117-u2-successor:scripts/validate_powermetrics_fiducial.py | nl -ba | sed -n '1,135p'
git show origin/impl/d117-u2-successor:scripts/validate_powermetrics_fiducial.py | nl -ba | sed -n '760,850p'
git show origin/impl/d117-u2-successor:scripts/validate_powermetrics_fiducial.py | nl -ba | sed -n '905,925p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:9181: PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:9968:             and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:10639:   909	            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:7113:   909	            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:8368:   909	            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:8335:    92	PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:8913:   669	            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:9608:   669	            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
origin/impl/d117-u2-successor:scripts/validate_powermetrics_fiducial.py:103:PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")
origin/impl/d117-u2-successor:scripts/validate_powermetrics_fiducial.py:918:            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py:461:        with patch.object(writer, "PREFLIGHT_SYSTEMATIC_SCREEN_S", Decimal("999")):
diff --git a/scripts/validate_powermetrics_fiducial.py b/scripts/validate_powermetrics_fiducial.py
index f7a5686..31725f6 100644
--- a/scripts/validate_powermetrics_fiducial.py
+++ b/scripts/validate_powermetrics_fiducial.py
@@ -17,58 +17,69 @@ byte-frozen validation identities.
   detected, no spurious plateaus - otherwise the artifact is invalid.
 
 NEVER run this while another agent session is active on the machine
 ([QUIET-MAC] discipline); the run is refused without --allow-live.
 """
 
 from __future__ import annotations
 
 import argparse
 import atexit
 import hashlib
 import json
 import math
 import subprocess
 import sys
 import time
 import uuid
 from dataclasses import asdict, replace
 from decimal import Decimal
 from pathlib import Path
+from typing import Any, Mapping
 
 REPO_ROOT = Path(__file__).resolve().parents[1]
 sys.path.insert(0, str(REPO_ROOT))
 
 from joulewise.adapters.powermetrics import (  # noqa: E402
     POWER_METRICS,
     SAMPLERS,
     anchor_records_from_powermetrics,
     parse_powermetrics_records,
     samples_from_records,
 )
 from joulewise.clock import SystemClock  # noqa: E402
 from joulewise.calibration_ledger import (  # noqa: E402
+    BRACKET_SESSION_OPEN_EVENT,
+    BRACKET_SESSION_SCHEMA,
+    BRACKET_SESSION_SLOTS,
     DEFAULT_LEDGER_PATH,
+    DEFAULT_HEAD_PIN_PATH,
+    CalibrationLedgerError,
+    abort_bracket_session,
     append_pending_receipt,
     artifact_hashes as ledger_artifact_hashes,
+    claim_bracket_session_slot,
     finalize_attempt_receipt,
+    finalize_bracket_session_slot,
     head_pin_for_receipt,
+    load_calibration_ledger_snapshot,
+    terminal_head_pin_for_session,
 )
 from joulewise.powermetrics_fiducial import (  # noqa: E402
     BASELINE_S,
     LEGACY_PROTOCOL_ID,
     PROTOCOL_ID,
     PROTOCOL_V2_ID,
     PROTOCOL_V2_PULSE_COUNT,
     RESIDUAL_REGION_METHOD,
     PULSE_COUNT,
     PULSE_DURATION_S,
     SAMPLING_INTERVAL_MS,
     CommandedPulse,
     TraceInterval,
     WARMUP_PULSE_COUNT,
     allocate_matmul_buffers,
     capture_wall_time_from_events,
     clock_stamp_half_width_s,
     detect_pulses,
     instrument_evidence,
     protocol_definition_matches,
@@ -258,156 +269,394 @@ def rederive_artifact(source_dir: Path, output: Path) -> dict[str, object]:
         artifact_sha256={
             relative: hashlib.sha256(raw_by_name[relative]).hexdigest()
             for relative in ("raw/powermetrics.plist", "events.jsonl")
         },
         capture_wall_time_s=capture_wall_time_from_events(
             raw_by_name["events.jsonl"]
         ),
         protocol_id=PROTOCOL_V2_ID,
         protocol_pulse_count=PROTOCOL_V2_PULSE_COUNT,
     )
     payload["clock_anchor"] = stored.get("clock_anchor")
     payload["clock_anchor_resolved"] = True
     output.parent.mkdir(parents=True, exist_ok=True)
     # Exclusive create: re-derivation must never clobber an existing evidence
     # artifact (same rule as the extraction and campaign-log outputs).
     with output.open("x", encoding="utf-8") as handle:
         handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
     return payload
 
 
-def main() -> int:
+def _validate_reserved_bracket_slot(
+    ledger_path: Path,
+    head_pin_path: Path,
+    *,
+    session_id: str,
+    slot: str,
+    attempt_id: str,
+    custody_locator: str,
+    identity_epoch: Mapping[str, Any],
+    t1_bindings: Mapping[str, Any],
+    require_committed_pin: bool = True,
+) -> None:
+    """Authenticate the exact predeclared slot before capture state exists."""
+
+    snapshot = load_calibration_ledger_snapshot(
+        ledger_path,
+        head_pin_path,
+        require_committed_pin=require_committed_pin,
+        verify_custody=True,
+    )
+    session = snapshot.bracket_session_by_id.get(session_id)
+    finalized_slots = set(session.finalized_slots) if session is not None else set()
+    expected_slot = (
+        "pre"
+        if not finalized_slots
+        else "post"
+        if finalized_slots == {"pre"}
+        else None
+    )
+    open_receipt = next(
+        (
+            receipt
+            for receipt in snapshot.receipts
+            if receipt.get("schema_version") == BRACKET_SESSION_SCHEMA
+            and receipt.get("event") == BRACKET_SESSION_OPEN_EVENT
+            and receipt.get("session_id") == session_id
+        ),
+        None,
+    )
+    reserved = (
+        open_receipt.get("slots", {}).get(slot)
+        if isinstance(open_receipt, Mapping)
+        and isinstance(open_receipt.get("slots"), Mapping)
+        else None
+    )
+    if (
+        not snapshot.is_governed_open_bracket_extension
+        or session is None
+        or session.state != "open"
+        or slot not in BRACKET_SESSION_SLOTS
+        or slot != expected_slot
+        or session.slot_attempt_ids.get(slot) != attempt_id
+        or not isinstance(reserved, Mapping)
+        or reserved.get("attempt_id") != attempt_id
+        or reserved.get("custody_locator") != custody_locator
+        or dict(reserved.get("identity_epoch", {})) != dict(identity_epoch)
+        or dict(reserved.get("t1_bindings", {})) != dict(t1_bindings)
+    ):
+        raise CalibrationLedgerError(
+            "capture does not match the exact reserved bracket session slot"
+        )
+
+
+class _CaptureLedgerLifecycle:
+    """Route one writer attempt through ordinary or bracket-session APIs."""
+
+    def __init__(
+        self,
+        *,
+        ledger_path: Path,
+        head_pin_path: Path,
+        attempt_id: str,
+        custody_locator: str,
+        identity_epoch: Mapping[str, Any],
+        t1_bindings: Mapping[str, Any],
+        session_id: str | None = None,
+        slot: str | None = None,
+        require_committed_pin: bool = True,
+    ) -> None:
+        if (session_id is None) != (slot is None):
+            raise CalibrationLedgerError(
+                "bracket session id and slot must be supplied together"
+            )
+        self.ledger_path = Path(ledger_path)
+        self.head_pin_path = Path(head_pin_path)
+        self.attempt_id = attempt_id
+        self.custody_locator = custody_locator
+        self.identity_epoch: Mapping[str, Any] = identity_epoch
+        self.t1_bindings: Mapping[str, Any] = t1_bindings
+        self.capture_wall_time_s: str | None = None
+        self.exact_bound_lexeme_s: str | None = None
+        self.session_id = session_id
+        self.slot = slot
+        self.require_committed_pin = require_committed_pin
+        self.claim_id = uuid.uuid4().hex
+        self.begun = False
+        self.closed = False
+
+    @property
+    def is_bracket_session(self) -> bool:
+        return self.session_id is not None
+
+    def begin(self) -> None:
+        """Reserve ordinarily, or authenticate a previously reserved slot."""
+
+        if self.begun:
+            raise CalibrationLedgerError("capture ledger lifecycle already began")
+        if self.is_bracket_session:
+            assert self.session_id is not None and self.slot is not None
+            _validate_reserved_bracket_slot(
+                self.ledger_path,
+                self.head_pin_path,
+                session_id=self.session_id,
+                slot=self.slot,
+                attempt_id=self.attempt_id,
+                custody_locator=self.custody_locator,
+                identity_epoch=self.identity_epoch,
+                t1_bindings=self.t1_bindings,
+                require_committed_pin=self.require_committed_pin,
+            )
+            claim_bracket_session_slot(
+                self.ledger_path,
+                session_id=self.session_id,
+                slot=self.slot,
+                attempt_id=self.attempt_id,
+                claim_id=self.claim_id,
+            )
+        else:
+            append_pending_receipt(
+                self.ledger_path,
+                attempt_id=self.attempt_id,
+                custody_locator=self.custody_locator,
+                identity_epoch=self.identity_epoch,
+                t1_bindings=self.t1_bindings,
+                head_pin_path=self.head_pin_path,
+                require_committed_pin=self.require_committed_pin,
+            )
+        self.begun = True
+
+    def abandon(self, reason: str) -> Mapping[str, Any] | None:
+        """Best-effort governed closure for an interrupted writer."""
+
+        if not self.begun or self.closed:
+            return None
+        if self.is_bracket_session:
+            assert self.session_id is not None
+            receipt = abort_bracket_session(
+                self.ledger_path,
+                session_id=self.session_id,
+                reason=reason,
+            )
+        else:
+            receipt = finalize_attempt_receipt(
+                self.ledger_path,
+                attempt_id=self.attempt_id,
+                disposition="abandoned",
+                custody_locator=self.custody_locator,
+                artifact_sha256=ledger_artifact_hashes(
+                    Path(self.custody_locator)
+                ),
+                identity_epoch=self.identity_epoch,
+                t1_bindings=self.t1_bindings,
+                capture_wall_time_s=self.capture_wall_time_s,
+                exact_bound_lexeme_s=self.exact_bound_lexeme_s,
     1	#!/usr/bin/env python3
     2	"""Lead-owned [QUIET-MAC] pulse-fiducial calibration run (D-078).
     3	
     4	The current claim-bearing protocol is frozen in
     5	configs/calibration/powermetrics_fiducial/protocol_v3.json and documented in
     6	docs/contracts/powermetrics_fiducial.md. Historical protocol files remain
     7	byte-frozen validation identities.
     8	
     9	- preallocated 4096x4096 FP16 MLX matmuls, mx.eval GPU fencing;
    10	- 3 warmup pulses, then k=59 pulses of 1.0 s each;
    11	- deterministic low-discrepancy spacing 1.5 + vanDerCorput_2(j) s
    12	  (avoids 10 Hz phase lock);
    13	- >= 5 s baseline before and after the pulse train;
    14	- events pulse_command_on/off carry full paired ClockStamps;
    15	- primary rail gpu_power; CPU+GPU combined is corroboration only;
    16	- gates: plateau >= 10 W over baseline, robust SNR >= 10, all pulses
    17	  detected, no spurious plateaus - otherwise the artifact is invalid.
    18	
    19	NEVER run this while another agent session is active on the machine
    20	([QUIET-MAC] discipline); the run is refused without --allow-live.
    21	"""
    22	
    23	from __future__ import annotations
    24	
    25	import argparse
    26	import atexit
    27	import hashlib
    28	import json
    29	import math
    30	import subprocess
    31	import sys
    32	import time
    33	import uuid
    34	from dataclasses import asdict, replace
    35	from decimal import Decimal
    36	from pathlib import Path
    37	from typing import Any, Mapping
    38	
    39	REPO_ROOT = Path(__file__).resolve().parents[1]
    40	sys.path.insert(0, str(REPO_ROOT))
    41	
    42	from joulewise.adapters.powermetrics import (  # noqa: E402
    43	    POWER_METRICS,
    44	    SAMPLERS,
    45	    anchor_records_from_powermetrics,
    46	    parse_powermetrics_records,
    47	    samples_from_records,
    48	)
    49	from joulewise.clock import SystemClock  # noqa: E402
    50	from joulewise.calibration_ledger import (  # noqa: E402
    51	    BRACKET_SESSION_OPEN_EVENT,
    52	    BRACKET_SESSION_SCHEMA,
    53	    BRACKET_SESSION_SLOTS,
    54	    DEFAULT_LEDGER_PATH,
    55	    DEFAULT_HEAD_PIN_PATH,
    56	    CalibrationLedgerError,
    57	    abort_bracket_session,
    58	    append_pending_receipt,
    59	    artifact_hashes as ledger_artifact_hashes,
    60	    claim_bracket_session_slot,
    61	    finalize_attempt_receipt,
    62	    finalize_bracket_session_slot,
    63	    head_pin_for_receipt,
    64	    load_calibration_ledger_snapshot,
    65	    terminal_head_pin_for_session,
    66	)
    67	from joulewise.powermetrics_fiducial import (  # noqa: E402
    68	    BASELINE_S,
    69	    LEGACY_PROTOCOL_ID,
    70	    PROTOCOL_ID,
    71	    PROTOCOL_V2_ID,
    72	    PROTOCOL_V2_PULSE_COUNT,
    73	    RESIDUAL_REGION_METHOD,
    74	    PULSE_COUNT,
    75	    PULSE_DURATION_S,
    76	    SAMPLING_INTERVAL_MS,
    77	    CommandedPulse,
    78	    TraceInterval,
    79	    WARMUP_PULSE_COUNT,
    80	    allocate_matmul_buffers,
    81	    capture_wall_time_from_events,
    82	    clock_stamp_half_width_s,
    83	    detect_pulses,
    84	    instrument_evidence,
    85	    protocol_definition_matches,
    86	    pulse_schedule,
    87	    run_matmul_pulse,
    88	    trim_trace_after_pulses,
    89	    rederive_detection_from_artifacts,
    90	)
    91	from joulewise.uncertainty_evidence import (  # noqa: E402
    92	    CLOCK_METHOD_V2,
    93	    derive_powermetrics_clock_evidence_v2,
    94	)
    95	
    96	PROTOCOL_PATH = (
    97	    REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v3.json"
    98	)
    99	PROTOCOL_V2_PATH = (
   100	    REPO_ROOT / "configs" / "calibration" / "powermetrics_fiducial" / "protocol_v2.json"
   101	)
   102	ROLLOVER_GATE_TIMEOUT_REASON = "pulse_calibration_rollover_gate_timeout"
   103	PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")
   104	
   105	
   106	def sha256_path(path: Path) -> str:
   107	    return hashlib.sha256(path.read_bytes()).hexdigest()
   108	
   109	
   110	def _sysctl_identity(name: str) -> str:
   111	    """Read a reservation-time macOS identity before capture begins."""
   112	
   113	    value = subprocess.run(
   114	        ["/usr/sbin/sysctl", "-n", name],
   115	        check=True,
   116	        stdout=subprocess.PIPE,
   117	        stderr=subprocess.PIPE,
   118	        text=True,
   119	    ).stdout.strip()
   120	    if not value:
   121	        raise RuntimeError(f"empty reservation identity: {name}")
   122	    return value
   123	
   124	
   125	def verify_frozen_protocol(path: Path = PROTOCOL_PATH) -> bool:
   126	    """Load and field-bind the frozen JSON to executable module constants."""
   127	
   128	    try:
   129	        payload = json.loads(path.read_text(encoding="utf-8"))
   130	    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
   131	        return False
   132	    return protocol_definition_matches(payload)
   133	
   134	
   135	def _terminate_powermetrics(process: subprocess.Popen) -> None:
   760	        run_matmul_pulse(PULSE_DURATION_S, buffers)
   761	        off_stamp = clock.stamp()
   762	        emit(
   763	            "pulse_command_off",
   764	            {"clock_stamp": asdict(off_stamp), "planned_off_offset_s": off_offset_s},
   765	        )
   766	        pulses.append(
   767	            CommandedPulse(
   768	                on_s=on_stamp.epoch_s,
   769	                off_s=off_stamp.epoch_s,
   770	                on_uncertainty_s=clock_stamp_half_width_s(on_stamp),
   771	                off_uncertainty_s=clock_stamp_half_width_s(off_stamp),
   772	            )
   773	        )
   774	    time.sleep(BASELINE_S)
   775	    sampling_stopped = clock.stamp()
   776	    emit("sampling_stopped", {})
   777	    _terminate_powermetrics(process)
   778	    post_parse = clock.stamp()
   779	
   780	    data = capture_path.read_bytes()
   781	    native_records = parse_powermetrics_records(data)
   782	    evidence, point_anchor_s = derive_powermetrics_clock_evidence_v2(
   783	        stamps={
   784	            "pre_spawn": pre_spawn,
   785	            "first_parse": first_parse,
   786	            "sampling_started": sampling_started,
   787	            "sampling_stopped": sampling_stopped,
   788	            "post_parse": post_parse,
   789	        },
   790	        records=anchor_records_from_powermetrics(native_records),
   791	    )
   792	    anchor_resolved = point_anchor_s is not None
   793	    if not anchor_resolved:
   794	        print(
   795	            "clock_anchor_unresolved: calibration capture cannot be anchored",
   796	            file=sys.stderr,
   797	        )
   798	        # Fail closed: an unanchored capture can never be a valid calibration.
   799	        # Detection still runs against the 1 s-quantized native stamps so the
   800	        # diagnostic artifact records why, but the evidence is forced invalid
   801	        # and the script exits nonzero below.
   802	        anchored = native_records
   803	    else:
   804	        anchored = parse_powermetrics_records(
   805	            data, first_record_endpoint_s=point_anchor_s
   806	        )
   807	    samples = samples_from_records(anchored)
   808	    trace_path = out_dir / "power_trace.csv"
   809	    with trace_path.open("w", encoding="utf-8") as handle:
   810	        handle.write(
   811	            "timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
   812	        )
   813	        for sample in samples:
   814	            handle.write(
   815	                f"{sample.timestamp_s!r},{sample.power_w!r},{sample.source},"
   816	                f"{sample.rail},{sample.interval_start_s!r},{sample.interval_end_s!r}\n"
   817	            )
   818	
   819	    intervals = [
   820	        TraceInterval(
   821	            start_s=record.timestamp_s - record.elapsed_ns / 1e9,
   822	            end_s=record.timestamp_s,
   823	            power_w=record.rail_power_w["gpu_power"],
   824	        )
   825	        for record in anchored
   826	    ]
   827	    detection = detect_pulses(
   828	        trim_trace_after_warmups(intervals, warmups),
   829	        pulses,
   830	        trace_anchor_bound_s=(
   831	            float(evidence["clock_anchor"]["effective_clock_anchor_bound_s"])
   832	            if anchor_resolved
   833	            else 0.0
   834	        ),
   835	    )
   836	    events.close()
   837	
   838	    device_meta = native_records[0].metadata if native_records else {}
   839	    bindings = {
   840	        "hardware_model": device_meta.get("hw_model"),
   841	        "os_build": device_meta.get("kern_osversion"),
   842	        "powermetrics_sha256": sha256_path(Path(POWER_METRICS)),
   843	        "sampling_interval_ms": SAMPLING_INTERVAL_MS,
   844	        "anchor_method_version": evidence["clock_anchor"].get("method"),
   845	        "mlx_version": getattr(mx, "__version__", None),
   846	        "pulse_protocol_id": PROTOCOL_ID,
   847	        "power_policy": args.power_policy,
   848	        "estimator_revision": RESIDUAL_REGION_METHOD,
   849	        "protocol_sha256": sha256_path(PROTOCOL_PATH),
   850	    }
   905	        json.dumps(evidence_payload, sort_keys=True),
   906	        parse_float=str,
   907	        parse_int=str,
   908	    )
   909	    bound_lexeme = serialized_evidence.get("b_fiducial_s")
   910	    ledger_lifecycle.exact_bound_lexeme_s = (
   911	        bound_lexeme if isinstance(bound_lexeme, str) else None
   912	    )
   913	    disposition = "ordinary-invalid"
   914	    if evidence_payload["status"] == "valid":
   915	        disposition = (
   916	            "systematic-invalid"
   917	            if isinstance(bound_lexeme, str)
   918	            and Decimal(bound_lexeme) > PREFLIGHT_SYSTEMATIC_SCREEN_S
   919	            else "valid"
   920	        )
   921	    _final_receipt, head_pin_candidate = ledger_lifecycle.finalize(disposition)
   922	    atexit.unregister(finalize_abandoned)
   923	    output = {
   924	        "validation_id": validation_id,
   925	        "status": evidence_payload["status"],

exec
/bin/zsh -lc "sed -n '9450,9535p' docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md
rg -n \"Recommended|recommend|should|must remain|must be|needs an explicit cold ruling|preflight-screen|count boundary|systematic failure|abandoned|no-content|immutable artifact|Git history|registry|co-landing|post slot|post observation|six-file\" docs/process_traces/2026-08-07-d117-u-units/U2-DESIGN-BRIEF.md | tail -160" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
12. Approve the six-file U2 scope expansion above, or accept that writer-side copied-scalar removal remains a separately gated hardening unit.

No files were written, no tests were run, and the worktree remained clean.
tokens used
170,362
# U2 design brief — D-102 calibration-acceptance successor engine

## Decision summary

U2 should replace the single hard-coded issued-artifact pin with a Git-authenticated acceptance registry and an immutable lineage of acceptance artifacts. A successor is derived from every content-distinct, valid observation in the artifact’s exact six-field epoch through a selected authenticated ledger cutoff.

Critically, the first successor is not “n=19 plus the triggering observation.” The issued cutoff already contains 30 valid same-epoch observations. If the next valid pre observation triggers range expansion, the successor corpus is therefore all 31 valid observations through that cutoff.

The pre-science probe must load and authenticate the actual active artifact, its registry entry, ledger ancestry, estimator/protocol bytes, and observed epoch. Reading `b_fiducial_s` and comparing it to a copied scalar is not sufficient.

Authority: [D-102](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/decision_log.md:6280), [D-109](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/decision_log.md:6990), [F3/U2 work order](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:153), and [RATIFICATION ruling 3](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/docs/process_traces/2026-08-07-d117-plan-freeze/RATIFICATION.md:15).

## 1. Existing authority and successor artifact

Current issued state:

- Artifact: `configs/calibration/calibration_acceptance_d079_v2.json`
- Exact file SHA-256: `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`
- Whole-core `derivation_sha256`: `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`
- Ledger cutoff/head: sequence `76`, digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`
- Repo head pin: `configs/calibration/calibration_ledger_head.json`
- Physical ledger: `runs/calibration_observation_ledger.jsonl`
- Inventory: 30 valid, 2 systematic-invalid, 6 ordinary-invalid.
- Proposed registry: `configs/calibration/calibration_acceptance_registry.json`; it does not exist yet.

The current loader in [calibration_bracketing.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk/joulewise/calibration_bracketing.py:431) recognizes only two code-pinned byte states and hard-codes n=19, its values, and its acceptance ID. U2 must generalize all of those.

### Exact successor artifact shape

Recommended new schema: `joulewise.calibration_acceptance_bound.v3`. It must contain exactly these top-level fields:

```text
schema_version
acceptance_id
decision_ids
artifact_role
issuance
lineage
ledger_cutoff
identity_epoch
prospective_rederivation
derivation_corpus
prior_observation_set
decimal_derivation
derivation_sha256
```

Required substructure:

- `schema_version`
  - Exactly `joulewise.calibration_acceptance_bound.v3`.

- `acceptance_id`
  - Deterministically derived from schema generation and cutoff, not wall-clock time.
  - Recommended form: `d079_calibration_acceptance_v3_s<sequence>_<head-prefix>`.

- `decision_ids`
  - At least `["D-102", "D-109", "D-117"]`, plus the eventual U2 cold-gate ruling ID.

- `artifact_role`
  - Exactly `issued`.

- `issuance`
  - `status: "issued"`
  - `claim_eligible: true`
  - `reason`
  - No free-form timestamp that would make bytes nondeterministic.

- `lineage`
  - `generation`
  - `root_acceptance_id`
  - `parent_acceptance_id`
  - `parent_artifact_sha256`
  - `parent_derivation_sha256`
  - `parent_ledger_cutoff` containing `sequence`, `head_digest`, and `ledger_schema`.
  - The first registry entry for the current issued artifact has a null parent; every successor has exactly one parent.

- `ledger_cutoff`
  - `sequence`
  - `head_digest`, which is also the exact cutoff receipt digest.
  - `ledger_schema`
7784:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:11107:docs/site/adapter_contracts.html:48:</code></pre> <p>Only the reducer may assign <code>below_floor</code>; <code>excluded_from_claim</code> is analysis-only and invalid in runtime events or summaries (D-045.4).</p> <p>Prompt-source handling is per item and mutually exclusive. <code>prompt_text</code> is encoded at generation time with adapter-normal special-token behavior (MLX uses <code>add_special_tokens=True</code>, so BOS is inside the planned prompt budget). <code>prompt_token_ids</code> is ids-native and delivered exactly as listed, with no BOS added; this is required for D-046 sentinel conditions. Absent text and ids use a synthetic prompt with <code>shape.planned_prompt_tokens</code>. Any field named <code>prompt_sha256</code> means the domain-separated token-ID hash, not a text hash.</p> <p>For prompt-text items with a SHA-256-shaped <code>source.source_sha256</code>, runtimes compare the realized prompt token-ID hash against <code>source_sha256</code>; if it does not match, they may accept <code>sha256(prompt_text)</code> as a text-domain manifest. Any other value fails the item closed as <code>malformed</code> with <code>status_reason: &quot;prompt_ids_mismatch&quot;</code>. For planned prompt token counts, <code>jw_mixed_v1</code> prompt-text items are budgeted and a realized/planned mismatch is fatal; affine ladder prompt-text items are nominal and receive an advisory annotation instead.</p> <p><code>suite_items.jsonl.prompt_source</code> is one of <code>prompt_text</code>, <code>token_ids</code>, or <code>synthetic</code>. <code>bos_present</code> records whether BOS is present in the realized prompt. For text-path adapters, when the tokenizer exposes a BOS id this is <code>add_special_tokens=True</code> and first realized id equals the tokenizer BOS id; when the tokenizer does not expose BOS identity, <code>bos_present</code> records the honest encode-mode proxy (<code>add_special_tokens=True</code>). Ids-native and synthetic suite prompts record <code>false</code> unless a future adapter explicitly materializes BOS as part of those sources.</p> <h2 id="telemetry-adapter">Telemetry Adapter</h2> <p>Telemetry answers how power and thermal state are measured.</p> <p>Required behavior:</p> <ul> <li>Report device metadata, including the rail manifest: the exact rail names whose per-timestamp sum defines the backend&#39;s canonical <code>power_w</code> (D-018). Rail manifest entries are strings; non-string entries are rejected by the bundle reader rather than coerced.</li> <li>Measure idle baseline.</li> <li>Start power sampling.</li> <li>Stop power sampling.</li> <li>Emit raw power samples.</li> <li>Report thermal state when available.</li> <li>Return structured failure if telemetry permission is missing.</li> </ul> <p>Rail-row timestamp contract (D-027, Slice 2N.4): one sample instant is one clock read, fanned out to one row per manifest rail, all carrying that instant&#39;s single <code>timestamp_s</code>. A manifest rail may appear at most once for a given timestamp; duplicate <code>(timestamp_s, rail)</code> rows are invalid, including single-rail manifests. With a multi-rail manifest, a timestamp carrying only a subset of the manifest rails is a misalignment: the shared bundle reader raises a structured failure (the reducer reports FAILED; the report omits the chart) and default bundle validation reports the same trace-policy problem rather than silently producing an interleaved, undersummed, or double-counted curve. An adapter whose hardware samples rails at genuinely different instants must resample/align to shared timestamps before emitting rows - alignment policy belongs to the adapter that knows its hardware.</p> <p>Powermetrics NUL-framed plist parsing is lenient only for the final unparseable frame, and only after at least one complete frame parsed successfully. The adapter preserves the raw plist verbatim, drops that final frame only from derived parsing (<code>power_trace.csv</code> and rich telemetry), and records a non-gating <code>metadata.device.parse_diagnostics[]</code> entry describing the dropped tail. A midstream unparseable frame, or a capture with no complete frames, is still a hard parse failure.</p> <p>Mock telemetry sampling convention (D-019): for any nonzero <code>start_sampling</code>/<code>stop_sampling</code> span, <code>MockTelemetryAdapter</code> stamps synthetic measured samples strictly inside that adapter span, never at the boundary clock reads. It uses a centered nominal-period grid at the configured <code>sampling.power_hz</code>; if that would produce fewer than two samples, it emits two evenly spaced interior samples instead. This preserves deterministic constant-power math while ensuring the controller&#39;s post-start/pre-stop measured markers contain enough samples for reducer integration under both fake and real clocks.</p> <p>Initial telemetry backends:</p> <ul> <li><code>mock</code></li> <li><code>powermetrics</code></li> <li><code>nvidia_smi</code></li> <li><code>jetson_rails</code></li> <li><code>wall_meter</code></li> </ul> <h2 id="idle-admission-core-policy-extension-t0-5-audit-p1-1-p1-2-additive">Idle-Admission Core Policy Extension (T0.5, audit P1.1/P1.2; additive)</h2> <p>GPU-idle-only admission is no longer sufficient. The pure evaluators in <code>joulewise/idle_admission.py</code> add three fail-closed surfaces, driven by an additive campaign-policy sidecar section keyed <code>idle_admission_extension</code> (schema <code>joulewise.idle_admission_extension.v1</code>):</p> <ul> <li><p><strong>CPU-aware idle admission</strong>: policy-configurable criteria over the pre-run baseline rich telemetry (<code>rich_telemetry_idle.jsonl</code>) - nearest-rank p95 of the per-record max per-CPU busy ratio (<code>1 - idle_ratio - down_ratio</code>, clamped, so parked CPUs never read as busy) against <code>cpu_criteria.cpu_busy_ratio_p95_max</code>, and p95 of <code>processor_combined_power_w</code> against <code>cpu_criteria.processor_combined_power_w_p95_max</code>, with at least <code>cpu_criteria.min_samples</code> records. Admission requires the existing GPU-idle admission AND these criteria. Missing, malformed, or insufficient telemetry FAILS CLOSED when <code>cpu_criteria.on_missing_telemetry</code> is <code>fail</code> (mandatory for a production profile); an exploratory policy may use <code>flag</code> but must set <code>claim_bearing: false</code> (explicitly non-claim-bearing).</p> </li> <li><p><strong>Adapter-wattage continuity</strong>: <code>collect_environment_guard_observation</code> records the adapter surface (<code>power.adapter_watts</code>, <code>power.adapter_description</code>, plus a normalized <code>adapter_power_observation</code>) per admission observation when called with <code>include_adapter_power=True</code> (default off so pre-hookup callers keep their exact probe sequence AND their exact observation shape; the controller hookup opts in). Under the default flag the <code>power</code> block and <code>adapter_power_observation</code> keys are ABSENT entirely - not present as all-None placeholders - so the verdict&#39;s continuity scan (which treats any guard observation carrying a <code>power</code> key as an adapter observation) never ingests unverifiable unknown-wattage placeholders from callers that did not opt in. The campaign verdict evaluates the ordered observation sequence: wattage discontinuities (the live 140-&gt;70-&gt;140 W negotiation precedent) and description/power-source changes are NAMED conditions - recorded data, never a silent pass and never an implicit abort. Unknown adapter wattage fails closed when <code>adapter_wattage.require_known_wattage</code> is true (mandatory for production); stable known wattage passes.</p> </li> <li><p><strong>Prospective NEG-8 SCREEN + BUDGET</strong> — <strong>Ed-ratified 2026-07-24, superseding the prior gross-only amendment:</strong> the screen is claim-family aligned. It independently gates gross and idle-subtracted point drift against distinct bounds derived from the same named, settled, same-condition <code>n &gt;= 10</code> corpus. The hash-sealed <code>joulewise.neg8_drift_bound.v1</code> artifact records both families. For legacy one-member endpoints, <code>d054_point_contrast_guard_v1</code> remains <code>max(sample_range_j, t_0.975,n-1 * s * sqrt(2))</code>. Prospective endpoints are three members each: the screen uses the start/end endpoint means, records their standard errors, and compares the absolute mean delta (not a second SEM-inflated margin) to <code>max(mean(largest_3)-mean(smallest_3), t_0.975,n-1 * s * sqrt(2/3))</code>. The extreme-triplet term retains the largest corpus-supported endpoint-mean contrast; the Student-t term predicts two new three-member endpoint means. Recording SEM without adding it again avoids double-counting repeatability already represented by the bound. Gross envelope corners remain diagnostics only.</p> <p>Every evaluated window also mints a strictly positive allowance per family: <code>max(max(start_mean,midpoint,end_mean)-min(...), derived_bound)</code>. One midpoint member is mandatory for the prospective 3+1+3 protocol, so a non-monotone interior excursion cannot disappear behind similar endpoints. No duration multiplier is applied: the settled corpus identifies repeatability, not a drift-per-time law, and inventing linear physics would be less defensible than the observed trajectory maximum. The verdict records the no-scaling decision, member counts/means/SEMs, midpoint, excursion, selected bound, allowance, and derivation hash. Floor records add the family-matched allowance after the guarded/corner-widened floor; validation recomputes the sum and claim consumption uses both the drift-widened floor and the named deterministic allowance term.</p> <p>Missing/invalid family evidence refuses distinctly: <code>neg8_drift_bound_underived</code> (gross) and <code>neg8_idle_sub_drift_bound_underived</code> (idle-subtracted); both spellings are Ed-ratified D-078 registry additions. Family failures retain <code>neg8_bracket_abs_delta_exceeded</code> for gross and add <code>neg8_bracket_idle_sub_abs_delta_exceeded</code> for idle-subtracted. A delta exactly on its bound passes. The v1 sidecar&#39;s <code>max_abs_delta_j</code>/<code>max_rel_delta</code> remain legacy transport fields and do not gate amended rows.</p> <p><strong>BOUND FRESHNESS addendum — Ed-ratified 2026-07-24:</strong> the same sealed artifact carries <code>freshness.derived_at_s</code>, a fixed 24-hour <code>max_age_s = 86400</code>, and exact OS-build, power-supply-identity, and calibration-artifact-identity bindings. Twenty-four hours mirrors the governed instrument-calibration horizon: it permits one controlled measurement day without treating repeatability as indefinitely transferable. Evaluation records its timestamp, expiry, artifact and observed bindings, binding-resolution status, and every triggered re-derivation reason. Horizon expiry, OS build change, power-supply change, calibration identity change, or unresolved current binding makes both family bounds stale and refuses with the registered <code>neg8_drift_bound_stale</code>. A v1 artifact with an authentic pre-addendum seal but no freshness block is replay-readable only to produce that stale refusal; it is never grandfathered. Malformed or unsealed artifacts remain underived under the two family-specific spellings. The superseded pre-SCREEN+BUDGET gross-only v1 shape (no <code>claim_family_bounds</code>) is not replayable and refuses as malformed/underived; &quot;pre-addendum replay&quot; applies only to the dual-family shape with <code>claim_family_bounds</code> present and freshness absent.</p> <p>The bracket is a WHOLE-WINDOW check: the evaluated basis must contain both endpoints. Legacy pair-only windows (a5-a8) remain evaluable as 1+0+1: both families screen and each allowance is <code>max(abs(delta), bound)</code>. Replicated endpoints plus midpoint apply prospectively; existing basis-scoped legacy verdict rows retain their frozen interpretation. Per-segment invocations with only one endpoint (or neither) record <code>neg8_bracket_not_evaluated</code>, never a spurious missing/failure. A reference genuinely absent from an explicit whole-window pass still fails closed.</p> </li> </ul> <p>Verdict surface: <code>scripts/run_campaign.py</code> records the additive <code>idle_admission_core</code> section (schema <code>joulewise.idle_admission_core_verdict.v1</code>) on the campaign verdict with per-member CPU-admission results, the continuity result, the bracket result, and the union of named conditions. A sidecar without the extension yields the named condition <code>idle_admission_extension_unconfigured</code>.</p> <p>Hash/version enforcement: the campaign policy binding hash is the sha256 of the full sidecar bytes, extension included - changing any new field changes the policy identity; the extension additionally records its own canonical-JSON sha256 and requires exact schema/policy version strings and exact keys (unknown or missing keys are rejected).</p> <p>Deployment note (C2 hookup complete): <code>CampaignPolicy.from_mapping</code> now owns the typed additive extension parse, including profile-dependent fail-closed validation, so controller child runs re-parse the full hash-bound sidecar without a runner-side strip/parse workaround. The tracked production and exploratory sidecars carry the extension. During each live admission attempt, the powermetrics adapter exposes that attempt&#39;s rich CPU records in memory; the controller evaluates CPU/combined-power criteria before workload invoke, records the result in the existing <code>environment_admission.attempts</code> ledger, and retries/aborts or flags according to the base policy. Attempt selection is explicit, so the final admission decision and final CPU telemetry cannot be paired across retries. Current-mint attempt rows bind each measurement to a finite <code>start_s</code>/<code>end_s</code> wall-clock (epoch) window; the ordered ledger must be strictly increasing and non-overlapping (<code>end_i &lt;= start_(i+1)</code>). Missing or malformed timing refuses current claims, while frozen replay semantics remain unchanged. Because the windows are wall-clock, a backwards clock step between attempts mints an out-of-order ledger that strict validation permanently refuses — a fail-closed false refusal, never an admission; re-run the campaign member if this occurs. Missing adapter telemetry fails closed on live clocks; <code>FakeClock</code> fixture runs retain the pre-hookup GPU decision and record <code>cpu_admission_enforced: false</code> alongside the named missing-telemetry result. That field is an unconditional claim barrier in reducers/extraction; it is never evidence that GPU-only admission was scientifically sufficient. Live guard observations opt in to adapter-power capture, including a mandatory post-workload observation for every member. A missing post sample is unknown wattage (and therefore a production refusal), so renegotiation during the final workload cannot be hidden by an earlier clean sample.</p> <p>At window end, chain scripts can run:</p> <pre><code class="language-sh">python3 scripts/run_campaign.py --whole-window-verdict \
7785:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:11152:docs/process_traces/2026-08-06-d079-issuance-coldgate/FABLE-COLD-PROCEED.jsonl:26:{"parentUuid":"585790f4-ed03-47a7-a672-58c7e6a19ec2","isSidechain":true,"promptId":"5c9e22f4-f072-4d90-ba34-2746cfa6a676","agentId":"ad24a0f43262b600c","type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_01MTCt2qxs79KvHBbRHArVNQ","type":"tool_result","content":"- Date: 2026-08-01\n- Status: accepted (magistrate ratification after the two-round Sol xhigh\n  design consult + the independent n=19 corpus reconstruction; ALL\n  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)\n  quantile by numerical CDF, window B pre-cal value against primary\n  evidence bytes)\n- Applies to: CAL-BRACKET-D079-01, the future\n  `configs/calibration/calibration_acceptance_d079_v2.json` artifact\n\nThe four pins D-079 left unexecutable, now pinned:\n\n1. **Budget cap (Candidate A, 99% two-draw prediction family, derived\n   blind from the pre-window-B n=19 corpus):**\n   `max_budgetable_excess_s = 0.001275166090593858`;\n   `maximum_budgetable_drift_s = 0.012093166090593858`\n   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;\n   cap = ceiling − operative screen 0.010818). Consequences verified: a\n   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.\n   **Window B itself remains refused regardless** — its pre-calibration\n   0.035435840879704805 s (verified in primary evidence) exceeds the\n   pre-flight level screen, and D-079 cl.2's systematic failure is\n   never budgetable. The CAL-BRACKET regression at ~11 ms models the\n   DRIFT BRANCH only, never a whole-window B pass.\n2. **Freshness = exact identity epoch, no calendar hard expiry:** the\n   artifact binds {os_build, hardware_model, power_policy,\n   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any\n   change → `calibration_acceptance_bound_stale`. Mandatory prospective\n   re-derivation triggers: any identity-field change; protocol/estimator\n   byte change; a new valid same-identity calibration expanding the\n   observed range; corpus doubling (19→38); a new systematic failure\n   challenging the pre-flight screen. A trigger observation is judged\n   under the PRIOR artifact — never incorporated into a threshold that\n   judges itself. Calendar-age fields are provenance/advisory only (the\n   corpus spans four days; a calendar constant would be invented).\n3. **Never-zero allowance confirmed:**\n   `A_s = max(observed_drift_s, 0.010818)`;\n   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the\n   authenticated operative fiducial bound (anchor-envelope\n   re-reduction); no second calibration-drift energy term anywhere\n   downstream (D-078 cl.11 single-count).\n4. **Decimal numeric semantics:** the artifact stores source decimal","is_error":false}]},"uuid":"eac85bd1-611c-4be6-8230-e4a152e4c8d1","timestamp":"2026-08-06T08:36:09.447Z","toolUseResult":{"stdout":"- Date: 2026-08-01\n- Status: accepted (magistrate ratification after the two-round Sol xhigh\n  design consult + the independent n=19 corpus reconstruction; ALL\n  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)\n  quantile by numerical CDF, window B pre-cal value against primary\n  evidence bytes)\n- Applies to: CAL-BRACKET-D079-01, the future\n  `configs/calibration/calibration_acceptance_d079_v2.json` artifact\n\nThe four pins D-079 left unexecutable, now pinned:\n\n1. **Budget cap (Candidate A, 99% two-draw prediction family, derived\n   blind from the pre-window-B n=19 corpus):**\n   `max_budgetable_excess_s = 0.001275166090593858`;\n   `maximum_budgetable_drift_s = 0.012093166090593858`\n   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;\n   cap = ceiling − operative screen 0.010818). Consequences verified: a\n   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.\n   **Window B itself remains refused regardless** — its pre-calibration\n   0.035435840879704805 s (verified in primary evidence) exceeds the\n   pre-flight level screen, and D-079 cl.2's systematic failure is\n   never budgetable. The CAL-BRACKET regression at ~11 ms models the\n   DRIFT BRANCH only, never a whole-window B pass.\n2. **Freshness = exact identity epoch, no calendar hard expiry:** the\n   artifact binds {os_build, hardware_model, power_policy,\n   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any\n   change → `calibration_acceptance_bound_stale`. Mandatory prospective\n   re-derivation triggers: any identity-field change; protocol/estimator\n   byte change; a new valid same-identity calibration expanding the\n   observed range; corpus doubling (19→38); a new systematic failure\n   challenging the pre-flight screen. A trigger observation is judged\n   under the PRIOR artifact — never incorporated into a threshold that\n   judges itself. Calendar-age fields are provenance/advisory only (the\n   corpus spans four days; a calendar constant would be invented).\n3. **Never-zero allowance confirmed:**\n   `A_s = max(observed_drift_s, 0.010818)`;\n   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the\n   authenticated operative fiducial bound (anchor-envelope\n   re-reduction); no second calibration-drift energy term anywhere\n   downstream (D-078 cl.11 single-count).\n4. **Decimal numeric semantics:** the artifact stores source decimal","stderr":"","interrupted":false,"isImage":false,"noOutputExpected":false},"sourceToolAssistantUUID":"585790f4-ed03-47a7-a672-58c7e6a19ec2","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
7787:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:11160:docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:17:{"parentUuid":"2fc2b92b-d2e9-4c73-a6fb-e992b18b91c8","isSidechain":true,"promptId":"70846291-da47-443c-8a9a-b0e660a3b23b","agentId":"a46e6644985dd75fd","type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_01SLx5iR5UiSnUajeoqc6qzi","type":"tool_result","content":"6278\t## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics\n6279\t\n6280\t- Date: 2026-08-01\n6281\t- Status: accepted (magistrate ratification after the two-round Sol xhigh\n6282\t  design consult + the independent n=19 corpus reconstruction; ALL\n6283\t  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)\n6284\t  quantile by numerical CDF, window B pre-cal value against primary\n6285\t  evidence bytes)\n6286\t- Applies to: CAL-BRACKET-D079-01, the future\n6287\t  `configs/calibration/calibration_acceptance_d079_v2.json` artifact\n6288\t\n6289\tThe four pins D-079 left unexecutable, now pinned:\n6290\t\n6291\t1. **Budget cap (Candidate A, 99% two-draw prediction family, derived\n6292\t   blind from the pre-window-B n=19 corpus):**\n6293\t   `max_budgetable_excess_s = 0.001275166090593858`;\n6294\t   `maximum_budgetable_drift_s = 0.012093166090593858`\n6295\t   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;\n6296\t   cap = ceiling − operative screen 0.010818). Consequences verified: a\n6297\t   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.\n6298\t   **Window B itself remains refused regardless** — its pre-calibration\n6299\t   0.035435840879704805 s (verified in primary evidence) exceeds the\n6300\t   pre-flight level screen, and D-079 cl.2's systematic failure is\n6301\t   never budgetable. The CAL-BRACKET regression at ~11 ms models the\n6302\t   DRIFT BRANCH only, never a whole-window B pass.\n6303\t2. **Freshness = exact identity epoch, no calendar hard expiry:** the\n6304\t   artifact binds {os_build, hardware_model, power_policy,\n6305\t   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any\n6306\t   change → `calibration_acceptance_bound_stale`. Mandatory prospective\n6307\t   re-derivation triggers: any identity-field change; protocol/estimator\n6308\t   byte change; a new valid same-identity calibration expanding the\n6309\t   observed range; corpus doubling (19→38); a new systematic failure\n6310\t   challenging the pre-flight screen. A trigger observation is judged\n6311\t   under the PRIOR artifact — never incorporated into a threshold that\n6312\t   judges itself. Calendar-age fields are provenance/advisory only (the\n6313\t   corpus spans four days; a calendar constant would be invented).\n6314\t3. **Never-zero allowance confirmed:**\n6315\t   `A_s = max(observed_drift_s, 0.010818)`;\n6316\t   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the\n6317\t   authenticated operative fiducial bound (anchor-envelope\n6318\t   re-reduction); no second calibration-drift energy term anywhere\n6319\t   downstream (D-078 cl.11 single-count).\n6320\t4. **Decimal numeric semantics:** the artifact stores source decimal\n6321\t   lexemes and exact-decimal derivations (range\n6322\t   0.010817749309353528 s; 95% prediction 0.008826584887500717 s;\n6323\t   pre-flight exact max 0.03355875667989999 s) SEPARATELY from the\n6324\t   ratified operative comparators (0.010818; 0.033558756679900;\n6325\t   ROUND_HALF_EVEN at the declared quantum), hashing the decimal\n6326\t   strings + rounding rule into the derivation sha256. D-079's\n6327\t   12-place `0.010817749309` is a LABELLED presentation value, never a\n6328\t   comparator. Acceptance comparisons run in decimal semantics;\n6329\t   binary64 conversion happens only at the reducer boundary and is\n6330\t   recorded.\n6331\t\n6332\tCorpus provenance: the n=19 member list with per-member manifest and\n6333\tevidence sha256s is reconstructed and lead-spot-verified (2026-08-01\n6334\tsession records; summary in the session custody dir) — the artifact\n6335\tcopies those tables verbatim with re-verification at authoring, never\n6336\tretyped. Implementation remains sequenced behind gauntlet commit 3 and\n6337\tthe D-100 repair (shared write surfaces)."}]},"uuid":"f4593aea-dece-47d7-9c8f-04796e9bb788","timestamp":"2026-08-06T10:42:34.528Z","toolUseResult":{"type":"text","file":{"filePath":"/Users/edr/code/JouleWise/docs/decision_log.md","content":"## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics\n\n- Date: 2026-08-01\n- Status: accepted (magistrate ratification after the two-round Sol xhigh\n  design consult + the independent n=19 corpus reconstruction; ALL\n  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)\n  quantile by numerical CDF, window B pre-cal value against primary\n  evidence bytes)\n- Applies to: CAL-BRACKET-D079-01, the future\n  `configs/calibration/calibration_acceptance_d079_v2.json` artifact\n\nThe four pins D-079 left unexecutable, now pinned:\n\n1. **Budget cap (Candidate A, 99% two-draw prediction family, derived\n   blind from the pre-window-B n=19 corpus):**\n   `max_budgetable_excess_s = 0.001275166090593858`;\n   `maximum_budgetable_drift_s = 0.012093166090593858`\n   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;\n   cap = ceiling − operative screen 0.010818). Consequences verified: a\n   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.\n   **Window B itself remains refused regardless** — its pre-calibration\n   0.035435840879704805 s (verified in primary evidence) exceeds the\n   pre-flight level screen, and D-079 cl.2's systematic failure is\n   never budgetable. The CAL-BRACKET regression at ~11 ms models the\n   DRIFT BRANCH only, never a whole-window B pass.\n2. **Freshness = exact identity epoch, no calendar hard expiry:** the\n   artifact binds {os_build, hardware_model, power_policy,\n   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any\n   change → `calibration_acceptance_bound_stale`. Mandatory prospective\n   re-derivation triggers: any identity-field change; protocol/estimator\n   byte change; a new valid same-identity calibration expanding the\n   observed range; corpus doubling (19→38); a new systematic failure\n   challenging the pre-flight screen. A trigger observation is judged\n   under the PRIOR artifact — never incorporated into a threshold that\n   judges itself. Calendar-age fields are provenance/advisory only (the\n   corpus spans four days; a calendar constant would be invented).\n3. **Never-zero allowance confirmed:**\n   `A_s = max(observed_drift_s, 0.010818)`;\n   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the\n   authenticated operative fiducial bound (anchor-envelope\n   re-reduction); no second calibration-drift energy term anywhere\n   downstream (D-078 cl.11 single-count).\n4. **Decimal numeric semantics:** the artifact stores source decimal\n   lexemes and exact-decimal derivations (range\n   0.010817749309353528 s; 95% prediction 0.008826584887500717 s;\n   pre-flight exact max 0.03355875667989999 s) SEPARATELY from the\n   ratified operative comparators (0.010818; 0.033558756679900;\n   ROUND_HALF_EVEN at the declared quantum), hashing the decimal\n   strings + rounding rule into the derivation sha256. D-079's\n   12-place `0.010817749309` is a LABELLED presentation value, never a\n   comparator. Acceptance comparisons run in decimal semantics;\n   binary64 conversion happens only at the reducer boundary and is\n   recorded.\n\nCorpus provenance: the n=19 member list with per-member manifest and\nevidence sha256s is reconstructed and lead-spot-verified (2026-08-01\nsession records; summary in the session custody dir) — the artifact\ncopies those tables verbatim with re-verification at authoring, never\nretyped. Implementation remains sequenced behind gauntlet commit 3 and\nthe D-100 repair (shared write surfaces).","numLines":60,"startLine":6278,"totalLines":7476}},"sourceToolAssistantUUID":"2fc2b92b-d2e9-4c73-a6fb-e992b18b91c8","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
7788:docs/process_traces/2026-08-07-night-hardening/AUDIT-LEDGER.md:11178:docs/process_traces/2026-08-04-calbracket-collision-consult/consult-solhigh.log:2165:./docs/site/decision_log.html:1:<!DOCTYPE html> <html lang="en"> <head> <meta charset="utf-8"> <meta name="viewport" content="width=device-width, initial-scale=1"> <title>Decision Log - JouleWise</title> <script>document.documentElement.classList.add("js-enabled");</script> <link rel="stylesheet" href="style.css"> <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>"> </head> <body> <header class="site"> <nav class="nav"> <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a> <div class="links"> <a href="index.html">Project</a> <a href="research.html">Learn</a> <a href="advisor_brief.html">Advisor Brief</a> <a href="project_status.html">Status</a> <a href="status.html">Live Status</a> <a href="roadmap.html">Roadmap</a> <a href="process.html">Process</a> <a href="record.html">Record</a> <a href="library.html" class="active">Sources</a> <a href="results.html">Measurements</a> </div> </nav> </header> <main> <div class="doc-layout"> <aside class="toc-sidebar"><div class="card-label">Table of contents</div><a href="#d-078-soundness-gate-no-claim-bearing-extraction-from-time-anchor-defective-powermetrics-corpora">D-078: Soundness gate — no claim-bearing extraction from time-anchor-defective powermetrics corpora</a></aside> <div class="doc-wrap doc-source-docs-decision-log-md"> <p class="doc-meta"><a href="library.html">Back to sources</a> · rendered from <code>docs/decision_log.md</code></p> <nav class="doc-meta" aria-label="Decision log parts"><span>Decision log parts:</span> <strong aria-current="page">Recent</strong> · <a href="decision_log_archive_1.html">Archive 1</a></nav> <div class="provenance-plate"><span class="source-chip" title="docs/decision_log.md · commit 1af9f92 + uncommitted"><span class="source-file">docs/<wbr>decision_log.md</span><span class="source-commit">commit 1af9f92 + uncommitted</span></span></div> <!-- rendered: marked@18.0.6 --> <h1>Decision Log — Recent Entries</h1> <p>The guide and complete decision index continue on Archive 1; the navigation on this page links every rendered part.</p> <span id="d-078"></span><h2 id="d-078-soundness-gate-no-claim-bearing-extraction-from-time-anchor-defective-powermetrics-corpora">D-078: Soundness gate — no claim-bearing extraction from time-anchor-defective powermetrics corpora</h2> <p>Date: 2026-07-19. Owner: lead session under Ed&#39;s soundness-audit directive; recorded so the gate binds future sessions immediately. Status update 2026-07-22: the gate has been operative under Ed&#39;s direction through the entire repair arc, and Ed explicitly ratified the close-out cap (clause 8); formal ratification of this original text rides the PR #79 review (Ed may amend).</p> <p>The 2026-07-19 measurement-soundness audit (<code>docs/reviews/2026-07-19-measurement-soundness-audit.md</code>; all P0 findings lead-verified from primary evidence) found that powermetrics trace timestamps are misaligned with runtime events at the ~0.5–1 s scale (pre-spawn/first-parse midpoint anchor), making request/phase/item point energies physically non-attributable as recorded across ALL existing powermetrics corpora, including the 2026-07-17 published floor extraction.</p> <p>Binding until amended:</p> <ol> <li>No claim-bearing floor, MDE, or L2/L3 energy claim may be published from any corpus collected under the defective anchor. Existing corpora are instrument/calibration evidence only.</li> <li>Extraction must treat <code>window_evidence_precheck</code> as a hard gate and must join campaign-log cooldown/admission evidence (cap hits are not clean n). &quot;Claim-eligible&quot; narrative language may describe METRIC-level eligibility only, never source provenance alone.</li> <li>The repair path (roadmap Phase 0, <code>docs/phase_2/splitwise_replication_roadmap.md</code>): tight causal anchor + anchor-shift joule envelope in reduction, analysis-engine 0.5.0/v2 wire compat, CPU-aware idle admission, prospective NEG-8 acceptance threshold. Stored summaries are never rewritten; fixes are prospective.</li> <li>The 2026-07-17 published floor table is caveated in PROJECT_STATUS pending re-extraction; advisor-brief/site correction timing is Ed&#39;s deployment decision (D-068).</li> </ol> <p>Revisit trigger: Phase 0 repair lands with live pulse-validation evidence, or Ed rules a different salvage/disposition for existing corpora.</p> <h3>D-078 amendment — 2026-07-20: fail-closed vocabulary and immutable summaries</h3> <p>Additive amendment under the adversarial soundness fix round. The following spellings are the binding, closed registry for D-078 claim refusals and campaign conditions. Consumers preserve these strings verbatim; an unknown claim/refusal spelling never becomes a pass.</p> <ul> <li>Reducer/analysis claim barriers: <code>nonpositive_window_duration</code>, <code>insufficient_in_window_samples</code>, <code>cadence_ratio_unrecorded</code>, <code>cadence_ratio_below_threshold</code>, <code>clock_bound_unrecorded</code>, <code>clock_bound_exceeds_quarter_window</code>, <code>interpolation_bound_unrecorded</code>, <code>drift_term_unknown</code>, <code>idle_baseline_unrecorded</code>, <code>cooldown_cap_hit</code>, <code>environment_admission_failed</code>, <code>environment_override</code>, <code>environment_admission_missing</code>, <code>cpu_admission_unenforced</code>, <code>clock_anchor_unresolved</code>, <code>anchor_energy_envelope_unrecorded</code>, <code>anchor_energy_envelope_exceeds_quarter_metric</code>, <code>instrument_calibration_missing</code>, <code>instrument_calibration_mismatch</code>, and <code>instrument_calibration_invalid</code>.</li> <li>Floor-extraction refusals: <code>bundle_missing</code>, <code>summary_unreadable</code>, <code>bundle_strict_invalid</code>, <code>bundle_hash_unresolved</code>, <code>bundle_status_not_succeeded</code>, <code>reducer_wire_unknown</code>, <code>idle_method_pair_invalid</code>, <code>metric_missing_or_nonfinite</code>, <code>window_evidence_precheck_failed</code>, <code>campaign_cooldown_evidence_missing</code>, <code>cooldown_cap_hit_unverified</code>, <code>campaign_member_omitted_from_spec</code>, <code>campaign_member_unattributable</code>, <code>cap_hit_drift_term_unavailable</code>, <code>insufficient_members_after_exclusion</code>, plus every applicable reducer barrier above and <code>whole_window_neg8_verdict_missing</code>, <code>whole_window_neg8_verdict_failed</code>, <code>adapter_continuity_evidence_missing</code>, <code>adapter_continuity_failed</code>, <code>cpu_admission_core_missing</code>, and <code>cpu_admission_core_failed</code>.</li> <li>Idle-admission/campaign conditions: <code>cpu_baseline_telemetry_missing</code>, <code>cpu_baseline_telemetry_malformed</code>, <code>cpu_baseline_sample_count_insufficient</code>, <code>cpu_busy_ratio_p95_exceeded</code>, <code>processor_combined_power_w_p95_exceeded</code>, <code>gpu_idle_admission_not_passed</code>, <code>gpu_idle_admission_unknown</code>, <code>adapter_observations_missing</code>, <code>adapter_wattage_unknown</code>, <code>adapter_wattage_discontinuity</code>, <code>adapter_description_changed</code>, <code>adapter_power_source_changed</code>, <code>neg8_bracket_missing</code>, <code>neg8_bracket_reference_invalid</code>, <code>neg8_bracket_abs_delta_exceeded</code>, <code>neg8_bracket_rel_delta_exceeded</code>, <code>neg8_bracket_not_evaluated</code>, <code>neg8_bracket_ambiguous_reference</code>, <code>idle_admission_attempt_ledger_invalid</code>, <code>idle_admission_extension_unconfigured</code>, <code>whole_window_bundle_invalid</code>, <code>whole_window_campaign_membership_unresolved</code>, and <code>whole_window_campaign_membership_ambiguous</code>.</li> <li>Instrument-evidence diagnostics: <code>pulse_detection_incomplete</code>, <code>spurious_plateau_detected</code>, <code>residual_interval_unbounded</code>, <code>not_all_pulses_detected</code>, <code>binding_fields_missing:</code>, <code>pulse_count_below_protocol:</code>, and <code>raw_or_event_hash_missing_or_invalid</code>. These diagnostics can only make <code>instrument_calibration_invalid</code>; they never directly license a claim.</li> </ul> <p>Governance ruling GOV-02: D-078 supersedes only D-028&#39;s former exception that allowed <code>summary_metrics.json</code> to be rewritten after finalization. Stored summary bytes are now immutable evidence. Post-hoc reduction writes a new, non-clobbering artifact (including the repaired anchor envelope) or refuses; the raw-artifact immutability and pure-reducer portions of D-002/D-028 remain in force. Frozen 0.5.0/0.6.0 numeric semantics remain replayable and are not claim-bearing merely because they can be read.</p> <h3>D-078 additive registry addendum — 2026-07-20: causal-set repair</h3> <p>The closed registry additionally includes floor/whole-window barriers <code>admissible_set_uncertainty_dominates_point_floor</code>, <code>whole_window_verdict_coverage_incomplete</code>, <code>whole_window_verdict_provenance_invalid</code>, and <code>whole_window_verdict_conflict</code>. Instrument-evidence diagnostics additionally include <code>no_plateau_interior_intervals</code>, <code>plateau_below_minimum</code>, <code>robust_snr_below_minimum</code>, <code>edge_coverage_missing</code>, <code>model_fit_not_significant</code>, and <code>fitted_shift_exceeds_validation_limit</code>. These additions only refuse or widen uncertainty; none can license a claim.</p> <h3>D-078 amendment — 2026-07-21: convergence fix wave (lead adjudications)</h3> <p>Recorded by the lead after the two-round cross-model convergence loop over <code>impl/p0-instrument-repair</code> (round-2 and round-3 fix waves; council log carries the layer accounting). Six rulings:</p> <ol> <li><strong>Additive causal-bound composition.</strong> <code>B_effective = B_bundle + B_fiducial</code> replaces <code>max(B_bundle, B_fiducial)</code>. The bundle-local censored-constraint anchor interval and the instrument&#39;s emission-lag bound sit on disjoint causal links; no containment proof exists, so <code>max()</code> under-composes. <code>B_fiducial</code> itself additively folds in the calibration capture&#39;s own trace-anchor bound. The prior <code>max()</code> text in this log is superseded prospectively; stored summaries are never rewritten.</li> <li><strong>Identity bump, not in-place semantics change.</strong> The additive composition, fiducial protocol_v2 physics (<code>joint_loss_sublevel_interval_branch_v2</code> full 2-D branch-and-bound region), and the stricter evidence-admission semantics are minted as reducer <code>0.5.2</code> / AXI <code>0.6.2</code> with <code>configs/calibration/powermetrics_fiducial/protocol_v2.json</code>. <code>0.5.1</code> / <code>0.6.1</code> and <code>protocol_v1.json</code> remain byte-frozen replay arms.</li> <li><strong>Superseded arms are claim-ineligible.</strong> <code>0.5.1</code>/<code>0.6.1</code> summaries refuse claim-bearing use with a registered refusal (superseded max-composition envelope semantics); <code>0.5.2</code>/<code>0.6.2</code> are the sole claim-eligible mints.</li> <li><strong>Registry additions (closing the F11/PENDING exception).</strong> The closed refusal vocabulary additionally includes <code>token_count_stream_chunk_fallback</code> (renamed from the source-label reuse of <code>stream_chunk_fallback</code>), <code>pulse_calibration_rollover_gate_timeout</code> (pre-workload rollover gate timeout now refuses fail-closed, no artifact minting), and <code>post_window_trace_tail_shorter_than_anchor_bound</code> (reduce-time refusal when the post-window trace tail cannot support the composed anchor bound; collection policy raises the minimum post-window dwell to 1.0 s). These only refuse; none can license a claim.</li> <li><strong>Registry closure is one-way by design.</strong> Every emitted spelling must be registered here; a registered spelling with no current emission site (e.g. <code>window_evidence_precheck_failed</code>, <code>cap_hit_drift_term_unavailable</code>) is permitted — unemittable names cannot launder anything.</li> <li><strong>Member-level <code>claim_evidence_flags</code> is an all-leaf union — documented, not changed.</strong> Adjudicated a documentation defect only: the union is fail-safe (it can only over-flag, never over-admit) and gating decisions read the per-metric leaves. Scope documented in <code>docs/contracts/run_bundle_layout.md</code>; no wire rename.</li> </ol> <h3>D-078 amendment — 2026-07-21 (second): two-edge envelope and confirmation-round rulings</h3> <p>Recorded by the lead after the first confirmation round over <code>5093355</code> correctly withheld sign-off (fresh Sol xhigh audit; 8 confirmed findings, one P0). Rulings:</p> <ol> <li><strong>Corner-composed two-edge envelope (P0 repair).</strong> The calibration fits independent start-edge and stop-edge emission lags; a single common trace shift under-covers because independent endpoint errors move energy by up to <code>2·P·B_fiducial</code> even when a common shift cancels. The claim envelope is now the extrema over start = <code>delta_common + eps_on</code>, stop = <code>delta_common + eps_off</code> with <code>|delta_common| &lt;= B_bundle</code> and <code>|eps_on|, |eps_off| &lt;= B_fiducial</code> independent. For nonnegative power the energy is monotone in each edge separately, so exact extrema are attained at the four edge corners with the common shift scanned continuously — the existing breakpoint-exact scan run per corner. The per-edge corner offset is <code>±(B_fiducial + wall_minus_monotonic_span)</code>: the span is a third disjoint per-edge error source, folded into the corners (delta-review amendment) rather than the frozen arms&#39; cruder <code>2·span·maxP</code> additive term, and the composed <code>anchor_bound_s</code> = <code>B_bundle + B_fiducial + span</code> governs the tail-sufficiency gate identically. Idle-subtracted and per-token envelopes additionally widen by <code>2·(B_fiducial + span)·P_idle</code> because independent edges vary the subtracted idle duration (delta re-audit catch). New registered method spelling for the 0.5.2/0.6.2 mints; v1/v2 spellings remain replay-read-only.</li> <li><strong>In-place revision of the unreleased mints.</strong> Reducer 0.5.2 / AXI 0.6.2 were never merged or used for stored artifacts; their envelope semantics are revised in place (no 0.5.3/0.6.3 inflation). Goldens regenerated and hand-verified against the formula.</li> <li><strong>Registry additions.</strong> The closed refusal vocabulary additionally includes <code>negative_power_sample</code> (negative rail power reaching the envelope/energy path breaks the monotonicity argument and refuses fail-closed) and <code>instrument_calibration_stale</code> (calibration artifacts now record capture wall time and a 24 h <code>max_age_s</code> validity horizon in protocol_v2; claim-time verification refuses missing/invalid capture time or age exceeded — a finite 40-pulse residual maximum is not an out-of-sample bound without recency enforcement). Instrument-evidence diagnostics additionally include <code>capture_time_missing_or_invalid</code> (a v2 capture without a valid recorded capture wall time is invalid at minting, with the reason stated rather than silent). All only refuse; the PENDING_DECISION_LOG_REGISTRATION exception is retired with this entry. Replay purity note: the 0.5.1/0.6.1 arms keep their frozen binding expectation against the protocol_v2.json bytes current at their mint (<code>REPLAY_PROTOCOL_V2_SHA256</code>); custody-manifest verification and the staleness horizon are current-mint gates only.</li> <li><strong>Environment admission consumes the full evidence object.</strong> The shared validator fails closed on <code>critical_environment_passed</code>, <code>reference_provenance_present</code>, per-run evaluation eligibility, guard observations, and schema identity — and the post-run environment observation passes through the failure predicate on claim/whole-window paths (a post-run critical-environment failure refuses claim eligibility). This closes the Window-A screensaver contamination class end-to-end.</li> <li><strong>Calibration custody verified at claim time.</strong> The reducer enforces the validation-manifest reference: in-bundle containment, manifest hash, and presence + sha256 of every manifest member; any failure refuses as <code>instrument_calibration_invalid</code>. Current-era (0.5.2/0.6.2) claim-bearing use requires a protocol_v2 calibration artifact.</li> <li><strong>Collection floors.</strong> The 1.0 s post-window dwell minimum is enforced on every collection path (controller default, schema minimum, campaign-policy validation); sub-minimum configs refuse at validation. Scope spelling (delta-review adjudication): controller/CLI pre-collection rejection applies wherever powermetrics telemetry collects; mock-backend runs are not dwell-gated at the controller (mock telemetry cannot reach any claim path), while the campaign-policy schema minimum applies universally. Inner phase/item/block/level window entries carry the whole-trace anchor/calibration/tail barrier stamps whenever the top-level barrier fires.</li> <li><strong>Cooldown terminal-evidence normativity documented.</strong> The required terminal JSONL row fields (<code>release</code>, <code>release_criteria_met_late</code>), the cap-first precedence rule (&quot;the cap is causal and wins&quot;), and rejection semantics are contract text in <code>docs/contracts/run_bundle_layout.md</code>, matching <code>joulewise/cooldown.py</code> exactly.</li> </ol> <h3>D-078 amendment — 2026-07-21 (third): provenance authentication rulings</h3> <p>Recorded by the lead after confirmation round 2 over <code>233e9e3</code> withheld sign-off (9 confirmed; the physics verified clean from every lens — all findings are provenance/governance). Rulings, implemented in the round-3 fix wave (frozen 0.5.1/0.6.1 replay semantics unchanged throughout):</p> <ol> <li><strong>Declared facts are authenticated against primary bytes.</strong> The calibration&#39;s declared <code>capture_wall_time_s</code> must agree (±1 s) with the capture time independently derived from the hash-verified source events — a stale calibration can no longer be relabeled fresh (the P0).</li> <li><strong>Freshness covers the whole measurement.</strong> The 24 h horizon binds both <code>run_started</code> and the measured window END: <code>capture &lt;= run_started</code> and <code>window_end &lt;= capture + max_age_s</code>, inclusive. Pre-run delays cannot carry sampling past the declared validity of its calibration.</li> <li><strong>Version identity is validated generically.</strong> Generic bundle validation checks <code>reducer_version</code> against the closed known set and the §8.1 version/event-semantics pairing rules as a validation-time structured problem (no wire-schema enum — frozen-arm byte replay preserved); an unsupported <code>--reducer-version</code> yields the standard structured refusal, never a traceback.</li> <li><strong>Stored verdicts are re-derived, never trusted.</strong> The whole-window verifier rejects duplicated NEG-8 core members (occurrence-count semantics) and re-derives the bracket verdict from member evidence; disagreement with the stored row is <code>whole_window_verdict_conflict</code>. Delta-review strengthening (lead ruling): the re-derivation tolerances come from the repo-REGISTERED campaign policy whose file hash matches the row&#39;s <code>policy_sha256</code> — the one trust anchor that does not terminate at bundle custody. Unknown policy hashes, and rows whose self-asserted tolerances disagree with the registered policy, refuse <code>whole_window_verdict_provenance_invalid</code> before re-derivation. The custody boundary is otherwise explicit: a forger with bundle write access can rewrite row-internal hashes consistently, but cannot mint a matching tracked policy file.</li> <li><strong>Protocol identity is shape-authenticated.</strong> A v2 <code>protocol_id</code> requires the v2 estimator identity, capture/horizon fields, and v2 residual shape; v1-shaped bodies relabeled v2 refuse <code>instrument_calibration_invalid</code>.</li> <li><strong>Admission attempts have timing semantics.</strong> Attempt-ledger rows carry strictly increasing, non-overlapping declared windows on the strict path; violations refuse <code>environment_admission_missing</code>. 7a. <strong>(Fourth-wave addendum — claim-aggregation rulings, same date.)</strong> After confirmation round 3 over <code>0925480</code> (instrument core verified defensible on fresh head collections by every lens; all four P0s in the claim-aggregation layer), the lead ruled: (1) floors/MDEs widen by EXACT linear-corner evaluation over member envelope intervals — residual widening <code>w_i·(n−1)/n + Σ_{j≠i}w_j/n</code>, contrast widening <code>Σ|c_i|·w_i</code> — never a max-width shortcut, and the dominance refusal fires against the widened quantity; (2) admission is causally bound to its run: the final attempt window ends at-or-before window start within <code>MAX_ADMISSION_GAP_S = 600</code> (inclusive), the post-run observation is captured at-or-after window end, and attempt windows must contain their stage&#39;s recorded idle-capture interval; (3) the whole-window verifier re-derives CPU admission and adapter continuity from member-bundle primary evidence, refuses nonempty condition lists and undecodable log lines (laundering must require consistent cross-bundle forgery, never a one-line edit — full erasure resistance inside bundle custody is impossible and is recorded as the honest boundary); (4) NEG-8 reference energies are re-reduced from primary evidence at the current mint at claim time (minutes-scale cost accepted), with canonical-workload identity (<code>canonical_neg8_workload</code> + <code>scientific_config_sha256</code> against the custody-bound config) enforced; (5) the four byte-frozen goldens carry executable sha256 pins. Round-4 confirmation follow-ups (same date): the universal <code>clock_anchor_unresolved</code> barrier covers the <code>0.4.1</code>/<code>0.4.2</code> arms (every pre-repair wire, not only 0.5.0/0.6.0 — the former 0.4.x escape is closed and its test assertion inverted); the production trace-margin gate uses the full three-term composed bound including the wall-minus-monotonic span; campaign <code>ready_for_analysis</code> requires a registered claim-eligible mint (<code>0.5.2</code>/<code>0.6.2</code>; mock telemetry exempt — it can never bear claims). Recorded custody boundary: the 24 h calibration horizon compares host wall time, so an operator with host time control can evade it — accepted (host time integrity is an operator obligation, like bundle custody itself).</li> </ol> <p>7b. <strong>(Fifth-wave addendum — calibration epistemics, same date.)</strong> After confirmation round 5 over <code>09b5de6</code> (the P0 was statistical, not mechanical: a 40-pulse sample maximum is not an out-of-sample deterministic bound — 87.1% confidence on the 95th percentile vs the D-054 doctrine&#39;s n=59 for 95/95), the lead ruled: (1) <strong>protocol_v3</strong> raises the pulse count to 59, satisfying the repo&#39;s own nonparametric 95/95 doctrine; v3 is required for future claim-bearing calibration captures (v2 artifacts stay verifiable as this arc&#39;s validation evidence). (2) <strong>B_fiducial&#39;s epistemic status is stated honestly everywhere</strong>: a 95/95 nonparametric calibration bound, deterministic for claims only under REGISTERED transfer assumptions — T1 binding-vector stationarity, T2 the authenticated 24 h horizon, T3 load-regime transfer (calibration pulses are GPU-matmul under CPU-light load; sustained mixed-load transfer is an assumption; a loaded-calibration protocol variant is the registered roadmap mitigation). (3) <strong>Calibration bracketing is required for claim-bearing collections</strong>: two valid artifacts bracketing the window (pre at-or-before start, post at-or-after end, each within its own horizon), consumed as <code>max(pre, post)</code>, refusing <code>instrument_calibration_bracket_missing</code> or on bracket drift beyond <code>calibration_bracket_max_drift_s</code> (production 10 ms). Single-calibration reduction remains valid only for non-claim-bearing probe/exploratory use. (4) <strong>Environment state is window-enforced</strong>: per-interval thermal-pressure records are scanned over the measured window (<code>thermal_pressure_elevated_in_window</code> refusal); admission objects are recomputed from their embedded snapshots — a stored <code>eligible: true</code> is never trusted. (5) <strong>Loop-termination doctrine</strong>: convergence sign-off means zero UNADDRESSED P0/P1, where &quot;addressed&quot; includes a registered limitation with recorded justification, adjudicated by the lead. A physical instrument&#39;s uncertainty budget always rests on stated assumptions; the honest end state is registered assumptions, not infinite hardening. T3 is the first entry in that register. Round-6 follow-up (same date): the bracket maximum must be CONSUMED, not merely recorded — a claim refuses <code>calibration_bracket_exceeds_minted_bound</code> whenever <code>max(B_pre, B_post)</code> exceeds any member envelope&#39;s minted effective bound (the member must be re-reduced under the dominating calibration); the whole-window producer refuses duplicated member occurrences (occurrence-count doctrine at the producer, not just the claim verifier); the registered-policy trust anchor refuses duplicate-JSON-key policy bytes; and the standalone reducer horizon predicate upper-bounds <code>run_started</code> as well as the window end. Round-7 follow-ups (same date): the operative floor is the EXACT maximum of the complete D-054 guarded floor over the joint per-member interval corners (every component is convex in the member vector, so vertex enumeration is exact; n &lt;= 16 enumerated, larger widths refuse) — the linear-corner residual widening alone under-covered the Student-t prediction component; claim-licensing whole-window evidence requires the registered policy to be production-profile AND claim-bearing (exploratory rows can never license claims); the bracket-dominance gate authenticates each member&#39;s consumed bound from hash-verified calibration evidence (never the mint-time metadata scalar, whose disagreement is itself provenance-invalid); claim brackets accept protocol v3 artifacts ONLY (v2 stays valid as reduction/validation evidence). Round-8 follow-ups (2026-07-22): calibration identity is SEMANTICALLY authenticated, not just byte-authenticated — every calibration command event&#39;s two clocks (top-level <code>timestamp_s</code> and embedded ClockStamp epoch) must agree within 1 s on the strict path, and any event carrying a ClockStamp is skew-checked (the live artifact agrees within 0.205 ms; a shifted-freshness relabel now refuses); claim-time rederivation authenticates the EXECUTED v3 schedule (pulse durations, the deterministic van-der-Corput gap sequence within ±0.25 s, ≥4.5 s commanded-quiet baselines) so phase-locked or degenerate captures cannot claim the 95/95 identity; and the canonical floor/MDE artifact carries the corner-widened floor additively (validator recomputes it; the analysis engine consumes the WIDENED guarded floor as operative) — closing the honest-artifact-fails-closed gap so a sound end-to-end floor/MDE handoff exists. Registry additions for this wave: <code>instrument_calibration_bracket_missing</code>, <code>calibration_bracket_exceeds_minted_bound</code>, (claim-bearing window not bracketed by two authenticated, fresh calibration artifacts, or bracket drift beyond the registered tolerance) and <code>thermal_pressure_elevated_in_window</code> (per-interval thermal-pressure records non-nominal — or missing on the strict path — anywhere in the admission-to-window span). Both only refuse; the PENDING_DECISION_LOG_REGISTRATION exception for them is retired with this entry.</p> <ol start="7"> <li><p><strong>Sign-off evidence must be head-minted.</strong> Any artifact or re-reduction quoted as validation evidence for a head must be regenerated AT that head (the pre-233e9e3 rederived calibration artifact lacks the horizon fields the head requires, and the probe re-reductions predate the strict calibration gates — both are re-minted at the final head before the sign-off record is written). Claim-bearing measurement additionally requires fresh live [QUIET-MAC] calibration under protocol v3 (59 pulses, fifth-wave addendum), bracketing the window, within 24 h of collection.</p> </li> <li><p><strong>Confirmation round 9 (2026-07-22, FINAL under the Ed-ratified cap) — outcome and registered limitation L1.</strong> The round-9 review over head 040ca3a confirmed the fiducial chain, reduce-side verification taxonomy, and contract coherence clean, with ONE surviving blocker (CR9-1, repro-backed, lead-reproduced): the canonical floor/MDE artifact is SELF-ATTESTING about its admissible half-widths and campaign membership — <code>validate_floor_artifact</code> recomputes widened floors only from artifact-internal widths, and evidence binding authenticates identities, hashes, and ordering but neither rederives source widths nor requires complete governed campaign membership. A substituted artifact with understated widths (or one omitting a member) validates, binds, and licenses an exact claim floor. Per the loop-termination doctrine (clause 5), the lead adjudicates this a REGISTERED LIMITATION rather than a tenth round:</p> <ul> <li><strong>L1 (registered): canonical floor artifacts are not independently claim-licensing.</strong> Until floor↔extraction binding lands, a claim-bearing analysis may consume a floor artifact ONLY when it was produced by the governed extraction in the same custody session as the analysis (same run manifest; extraction gates demonstrably executed). Standalone or externally supplied floor artifacts are non-claim-bearing evidence. Justification: the exposure is artifact substitution or a defective producer BETWEEN extraction and analysis; an honest same-session pipeline computes widths and membership under the already -hardened extraction gates, so no measurement this program will make under L1&#39;s workflow rule is affected. The gap is a third-party verifiability deficit, not an instrument-physics defect.</li> <li><strong>Queued fix (next cycle, P1):</strong> bind each canonical floor cell to its extraction report and source-member disposition (or rederive the extraction gates and widths at binding), refusing on any stored width/corner mismatch or membership deviation, with integration regressions for width substitution and member omission (TASK_QUEUE FLOOR-BIND-01). Round-9 verification note: the focused 357-test review surface passed at the head in-session; the lead&#39;s full-suite gate over the identical tree content (2088 passed / 15 skipped / 1570 subtests / 0 failures) stands as the aggregate confirmation.</li> </ul> </li> <li><p><strong>Live collection arc (2026-07-22/23) — collection-path regressions, occurrence supersession, and basis-scoped verdicts.</strong> The first live Window-A members after sign-off exposed collection-path defects invisible to nine review rounds without hardware; each was fixed under the ratified contracts (PR #80 canonical-attempt promotion + sole-sampler gapless design; PR #81 idle-slice cursor after forensics proved the slicer&#39;s own parsing contaminated the admission interval at the real ~120 ms powermetrics cadence). Two doctrine amendments were then ruled by the lead when the whole-window verdict path contradicted operational guidance (both defaults preserved, both overrides explicit and auditable):</p> <ul> <li><strong>Occurrence supersession (amends the round-6 occurrence-count doctrine):</strong> duplicated member occurrences still REFUSE by default; a duplicate may resolve to the present bundle only when an explicit operator supersession artifact (append-only, hash-sealed, naming the superseded occurrence, quarantine destination, and reason — <code>--record-supersession</code>) exists; two present bundles always refuse.</li> <li><strong>Basis-scoped whole-window verdicts:</strong> latest-wins remains rejected (verdict-shopping prevention); every verdict records a canonical evaluation-basis hash (member occurrence set + calibration bracket set<ul> <li>policy) and binds only that basis; consumers match the claim&#39;s basis; legacy basis-less verdict rows never govern new claims. Diagnostic-cascade decoupling and whole-window waiver consumption landed in the same wave. Windows a5 (108 members) and prior attempts remain NON-claim-bearing as whole windows (true clock-anchor refusal on one member; NEG-8 end reference measured ~2 h post-collection failed the drift gate at 0.778 J — the instrument correctly refusing a stale bracket); their corpora stand as instrument-proving evidence. The next clean bracketed window is the first claim attempt.</li> </ul> </li> </ul> </li> <li><p><strong>NEG-8 drift-gate estimand ruling (2026-07-24; lead-ruled; RATIFIED in amended SCREEN+BUDGET form by the clause-10 addendum below — this original gross-only form was superseded the same day and never collected under).</strong> The whole-window drift adjudication proved the gate as previously implemented compared the two reference cells&#39; admissible envelopes at opposite corners (~0.9-1.5 J stacked) against an underived 0.05 J constant — structurally unpassable even for a physically perfect window (a8 measured point drift 0.006718 J over 2.96 h on ~38.5 J references). Ruling: the gate estimand is POINT DRIFT abs(end_point_gross − start_point_gross); the idle-subtracted point drift and the opposite-corner envelope statistic are recorded diagnostics, never gating (envelope stacking double-counts instrument uncertainty already composed into floor envelopes). The bound is DERIVED: a hash-sealed <code>joulewise.neg8_drift_bound.v1</code> artifact minted by governed CLI from a named settled-reference corpus (n&gt;=10, predeclared estimator <code>d054_point_contrast_guard_v1</code> = max(sample_range_j, t_{0.975,n-1}·s·sqrt(2))), consumed with full provenance in the verdict output. Registry addition: <code>neg8_drift_bound_underived</code> (fail-closed refusal whenever no valid governed bound artifact exists). Windows a6/a8 may be re-verdicted under the derived bound (with explicit waivers for aborted-member fragments); a5 and a7 remain refused on their genuine grounds.</p> </li> </ol> <p> <strong>Clause-10 addendum — debate and Ed ratification (2026-07-24).</strong> Per Ed&#39;s direction the ruling was formally debated with the peer model before ratification. The peer DISAGREED with the ruling as written on one structural point and was adjudicated correct: the point-drift statistic is the right estimand but an anomaly screen is not proof of stability — passing the gate must never erase observed drift from the claim error budget (consistent with the repo&#39;s own D-054/D-057 language). Ed RATIFIED the amended SCREEN + BUDGET design (the debate&#39;s option F, full variant, Ed explicitly directing the maximal build): per-claim-family point-drift screens (gross AND idle-subtracted, each with its own derived bound); per-family drift ALLOWANCES propagated additively into every floor/claim envelope of the window, never zero even on passing windows (allowance = max(observed excursion, derived repeatability bound)); replicated endpoint references (n=3 per endpoint, means with standard errors) and one midpoint reference prospectively, with the allowance taken over the maximum absolute excursion across sampled points; drift-bound artifacts carry a freshness horizon and re-derivation triggers (OS/build, power-supply, calibration-identity changes) with a distinct stale-bound refusal spelling; legacy pair-only windows evaluate under the single-member-endpoint minimum. Ed&#39;s recorded guardrails: watch the RIGOR SPIRAL (floors inflating past the effect sizes the science needs — monitor floor-vs-expected-effect at every extraction) and NO INVENTED PHYSICS (no functional form without a defensible basis; stated limitations beat unjustified formulas). Guiding light for all measurement-program decisions: the Splitwise replication (P2-006); methodology grounding against the Splitwise paper and comparable energy-measurement literature is in flight and feeds the collection design. Economics note recorded: Ed values artifact quality over time/tokens/machine-hours (project runs months ahead of deadline).</p> <p> <strong>Clause-10 addendum 2 — screen+budget wave registry + anchor-fallback gate ruling (lead, 2026-07-24).</strong> Registers the wave&#39;s spellings in the D-078 closed registry: <code>neg8_idle_sub_drift_bound_underived</code>, <code>neg8_bracket_idle_sub_abs_delta_exceeded</code>, and <code>neg8_drift_bound_stale</code> (freshness horizon exceeded or re-derivation trigger fired) — the ratified clause-10 design&#39;s concrete spellings — plus <code>anchor_fallback_member_unusable</code> (unwaivable, no waiver spelling exists: a fallback-clock-anchored member may not anchor a floor or claim cell; in a floor cell it is an unwaivable re-run trigger). The latter is a LEAD-INITIATED ruling from the 2026-07-24 a7-vs-a5 prefill-scatter root cause (<code>a7_vs_a5_prefill_scatter_analysis.md</code>): a7&#39;s 11.85 J prefill &quot;floor&quot; was one fallback-anchored member (r03), half-width-zero envelope — instrument artifact (true floor ≈ 3.3–3.7 J). Flagged for Ed&#39;s PR-gate review. Also registered (fix-round F3): <code>whole_window_drift_allowance_unrecorded</code> (passing basis-bearing verdict with no authenticated per-family allowance, or a claim missing its named allowance term — refuse, never zero; in both the floor-extraction and reducer vocabularies, mirroring <code>interpolation_bound_unrecorded</code>).</p> <p> <strong>Clause-10 addendum 3 — terminal mock bar (lead, 2026-07-24).</strong> The ratified premise &quot;mock telemetry can never bear claims&quot; had no terminal enforcement at the analysis claim boundary: honest mock members reached floor cells and claim evidence with the mock-exempted barriers disabled. Registered spelling: <code>mock_telemetry_claim_ineligible</code> (claim-bearing consumption of a member whose custody-bound config telemetry backend is the mock class; refuse — development-only evidence, no waiver spelling exists). Mockness derives from the custody-bound config (<code>hardware_target.telemetry_backend</code>, bytes bound via <code>metadata.config_sha256</code>), never from summary/metadata labels alone; where such a config exists, config/metadata/summary telemetry identities must agree by backend class (governed <code>mock:*</code> tags are mock class) or the bundle is strict-invalid. Config absence is non-production evidence (fixture-only permissive paths keep their ratified intent). Lead-initiated; flagged for Ed&#39;s PR-gate review.</p> <ol start="11"> <li><strong>Attribution-limited detection floors — Ed-RATIFIED amendment (2026-07-25).</strong> The first collection under the merged SCREEN+BUDGET rules (windows a9, a10; both whole-window verdicts PASSED) could not produce a floor: all three of a10&#39;s phase-absolute cells refuse <code>admissible_set_uncertainty_dominates_point_floor</code>. <strong>Finding: the instrument is ATTRIBUTION-limited, not NOISE-limited.</strong> Repeatability is 0.29-0.49 J on ~50 J points (and a settled reference pair three hours apart agreed to 0.007 J), but each member carries a clock-anchor-shift envelope of ~0.7-1.0 J: a +/-31 ms window shift across a phase boundary where power swings ~33 W mis-attributes ~1 J between prefill and decode. The composed bound is additive and measured — fiducial 24.9 ms (80-87%) plus bundle-local 3.3-6.1 ms plus edge span. Because repeatability will always beat attribution here, the refusal is STRUCTURALLY PERMANENT: no future phase corpus can pass it and there is nothing to re-collect around.</li> </ol> <p> <strong>Alternatives measured and eliminated</strong> (authenticated replay, 2026-07-25): (a) the calibration-bracket gap is NOT the cause — every cell refuses under both its minted and its post-bracket bound (delta +0.167 ms); (b) instrument tightening cannot rescue it — extraction would require a 10x (decode) to 32x (prefill) bound reduction, and each cell&#39;s bundle-local term ALONE (3.3-6.1 ms) already exceeds the entire required bound (0.99-2.9 ms), so even a perfect fiducial calibration would still refuse; (c) coarser granularity does not rescue it — request-level cells replayed on a10 and a8 have smaller envelopes (1.5-1.9 J) but still dominate and still refuse; (d) an ABBA common-mode estimator gives a real 3x gain (a5 decode 6.46 J -&gt; 2.13 J) but remains above that cell&#39;s 0.60 J point floor. The labelled path below is therefore not the preferred option among several — it is the only remaining path to any detection floor at all, at any granularity, on this instrument.</p> <p> <strong>Ruling (Ed-ratified).</strong> D-054 registers the detection floor as a practical prediction bound on FALSE OBSERVED EFFECTS, not as a repeatability statistic; a false observed effect may arise from scatter OR from anchor mis-attribution, and the corner-widened maximum is exactly the largest false effect this instrument can produce. <code>admissible_set_uncertainty_dominates_point_floor</code> therefore becomes a LABELLED CLAIM PATH rather than a hard refusal: extraction publishes the widened floor with a <code>floor_source</code> field naming the dominant term (here <code>E_clock_anchor_shift_bound_j</code>) and retains the point floor separately as the repeatability diagnostic. The gate keeps its real function — preventing a repeatability-only number from publishing as if it were the whole story — while no longer conflating &quot;unsound corpus&quot; with &quot;instrument-limited floor&quot;. a10 is sound.</p> <p> <strong>Binding condition — SINGLE-COUNT DISCIPLINE (Ed: &quot;the cost seems sensible as long as it&#39;s noted&quot;).</strong> The floor gate now contains the anchor term, and each claim&#39;s decision interval separately consumes the member&#39;s <code>E_clock_anchor_shift_bound_j</code>. These are different objects (calibration false-effect bound vs claim-side measurement uncertainty) and both are legitimate, but the consequence is that the effective clearable effect is FLOOR + CLAIM-SIDE BOUND (~5 J for phase contrasts), not the floor alone. Every artifact publishing an attribution-limited floor must state this explicitly so that neither term is later removed as an apparent double count. Science must be sized to the ~5 J bar; Splitwise-class effects (tens of percent of tens of joules) clear it with margin.</p> <p> <strong>Not authorised by this amendment:</strong> any instrument-tightening program. Revisit only if a pilot shows target effects below ~3x the widened floor. The free lever is workload sizing — attribution error is approximately duration-independent while effects scale with workload, so longer prefill/decode raises effect-to-floor linearly at zero instrument cost (queue FLOOR-WORKLOAD-SIZING-01).</p> <nav class="doc-meta" aria-label="Decision log parts"><span>Decision log parts:</span> <strong aria-current="page">Recent</strong> · <a href="decision_log_archive_1.html">Archive 1</a></nav> </div> </div> </main> <footer class="site"> <div class="inner"> <span>JouleWise · github.com/mpmdw/JouleWise</span> <span>docs/decision_log.md · commit 1af9f92 + uncommitted · regenerate: <span class="mono">python3 scripts/build_site.py</span></span> </div> </footer> </body> </html>
7803:docs/reviews/c027/lens-stats.md:140:The primary Student-t choice is right-sized for a descriptive mean at \(n=5\): it is better than a normal-z interval, and percentile bootstrap is not reliably better with five points. The implementation of that narrow calculation is correct. Its assumptions—iid, approximate normality, no informative missingness—are fragile in a thermally drifting, block-ordered benchmark, so it should not be promoted into the claim engine.
7805:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:1553:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7808:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-quantization-ladder.md:2937:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7811:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-advisor.md:2171:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7814:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:2145:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7817:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-cross-runtime-contrast.md:2642:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7818:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mvp-icpe-upgrade.md:955:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7821:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-param-scaling-energy.md:1566:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7824:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:2574:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7825:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:2867:1. **Ruling gate:** lead accepts the session-capability semantics, zero-retry policy, successor corpus rule, four-cell artifact shape, and fourth-window treatment.
7826:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-registry.md:2898:- Ratify the D-102 successor corpus rule: all content-distinct valid same-epoch observations through the cutoff.
7827:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:748:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7830:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-kv-context-energy.md:1694:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7833:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-contamination-characterization.md:2185:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7836:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-attention-variant-energy.md:2220:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7839:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:471:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7842:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-moe-routing-energy.md:1815:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7845:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-contrarian.md:2487:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7848:docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:2276:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7851:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-long-generation-dynamics.md:1919:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7854:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-prefill-scaling-laws.md:2188:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7857:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-open-explore-repo.md:1637:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7860:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-drift-thermal-science.md:1678:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7863:docs/strategy/2026-08-07-paper-portfolio/SYNTHESIS-PRAGMATICS-FIRST.md:1111:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7866:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-refusal-as-result.md:1774:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7871:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:899:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7872:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-floor-methodology-general.md:3838:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7875:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:1235:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7878:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:3183:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7881:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:3684:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7882:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-wall-meter-validation.md:5718:docs/process_traces/2026-08-06-d079-issuance-coldgate/FABLE-COLD-PROCEED.jsonl:14:{"parentUuid":"95303f9d-7523-4544-89e9-e0e2c5aa3014","isSidechain":true,"promptId":"5c9e22f4-f072-4d90-ba34-2746cfa6a676","agentId":"ad24a0f43262b600c","type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_018LjASorgBFpMjfaTz9pbY8","type":"tool_result","content":"1\t```json\n2\t{\n3\t  \"schema\": \"claude-codex-report/v1\",\n4\t  \"genre\": \"verification\",\n5\t  \"status\": \"findings\",\n6\t  \"completion\": \"complete\",\n7\t  \"summary\": \"BLOCKED. All 38 content-distinct candidates were recovered, hash-authenticated, epoch-checked, and replayed from raw physics: 32 VERIFIED-VALID and 6 VERIFIED-INVALID, with no missing raw evidence. Issuance is not ready because two verified-valid observations exceed the systematic-failure screen and therefore lack an unambiguous ledger disposition, and the repository does not specify a deterministic authenticated historical-import/bootstrap transaction from which one authoritative sequence/head digest can be computed.\",\n8\t  \"workspace\": {\n9\t    \"head_start\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n10\t    \"head_end\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n11\t    \"branch\": \"main\",\n12\t    \"pathspec\": [],\n13\t    \"unowned_dirty\": [],\n14\t    \"write_scope\": \"none\",\n15\t    \"edits\": \"none\"\n16\t  },\n17\t  \"verdict\": {\n18\t    \"overall\": \"BLOCKED\",\n19\t    \"prompt_vs_R2_divergence\": false,\n20\t    \"raw_member_results\": {\n21\t      \"VERIFIED-VALID\": 32,\n22\t      \"VERIFIED-INVALID\": 6,\n23\t      \"UNRESOLVED\": 0\n24\t    },\n25\t    \"blocking_items\": [\n26\t      {\n27\t        \"id\": \"B1\",\n28\t        \"type\": \"ledger_disposition_ruling\",\n29\t        \"members\": [\n30\t          \"20260726T000039-491995f3\",\n31\t          \"20260801T064830-c76f5d1c\"\n32\t        ],\n33\t        \"reason\": \"Both replay as physically valid, matching the candidate inventory, but their bounds 0.035435840879704805 and 0.0350400833260715 exceed the ratified 0.033558756679900 preflight screen. The production writer maps such a valid capture to systematic-invalid at scripts/validate_powermetrics_fiducial.py:664-671; D-102 explicitly calls the first member a systematic failure at docs/decision_log.md:6298-6301. The backfill candidate tool instead proposes valid solely from stored status at scripts/calibration_ledger_backfill.py:58-63. Selecting either disposition is lead-owned.\"\n34\t      },\n35\t      {\n36\t        \"id\": \"B2\",\n37\t        \"type\": \"bootstrap_contract_gap\",\n38\t        \"members\": \"all 38\",\n39\t        \"reason\": \"No historical-import/bootstrap API, receipt ordering, duplicate-custody selection rule, or import-transaction schema exists. The candidate tool emits only an unauthoritative candidate set and never appends the ledger (scripts/calibration_ledger_backfill.py:2-7,90-117). Because receipt digests bind sequence, predecessor, disposition, artifact hashes and absolute custody locator (joulewise/calibration_ledger.py:590-622), more than one valid head digest is possible.\"\n40\t      }\n41\t    ]\n42\t  },\n43\t  \"binding_clauses\": [\n44\t    {\n45\t      \"clause\": \"D-109 R1.4\",\n46\t      \"source\": \"docs/decision_log.md:7027-7039\",\n47\t      \"verbatim\": \"4. The acceptance artifact pins its baseline ledger head. Evaluation ALSO requires the independent current-head pin (clause below), verifies one complete non-forked chain extension from baseline to current, and threads ONE immutable ledger snapshot through every consumer path (session, direct runner path, secondary verifier) — repeated independent loads are a refusal-grade defect. Anti-rollback authority: a REPO-COMMITTED head-pin file `{sequence, head_digest, ledger_schema}` (existing checked-in byte-pin trust model; no second trusted latest-sequence store). Rotation is epoch-bounded — at most one lead-controlled quiet-machine collection session — and NO claim evaluation may occur between ledger advancement and pin commit; a physical head differing from the committed pin refuses.\",\n48\t      \"verification_plan\": \"After an authorized bootstrap, recompute every receipt digest, require one linear chain, require the artifact cutoff to equal an exact receipt, require the physical head to equal the separately committed pin, and trace one snapshot object through every consumer. This session verified the implemented digest/head machinery but could not select an authoritative bootstrap head because no import transaction is specified.\"\n49\t    },\n50\t    {\n51\t      \"clause\": \"D-109 R2.1\",\n52\t      \"source\": \"docs/decision_log.md:7053\",\n53\t      \"verbatim\": \"1. The issuance cutoff is an exact ledger sequence + head digest.\",\n54\t      \"verification_plan\": \"Compute the final receipt count and digest only after disposition, ordering and custody-locator rules are fixed. Current fixture cutoff remains non-production genesis sequence 0/all-zero digest at configs/calibration/calibration_acceptance_d079_v2.json:14-18.\"\n55\t    },\n56\t    {\n57\t      \"clause\": \"D-109 R2.2\",\n58\t      \"source\": \"docs/decision_log.md:7054-7055\",\n59\t      \"verbatim\": \"2. `derivation_corpus` remains exactly the n=19 threshold-producing observations.\",\n60\t      \"verification_plan\": \"Re-run the corpus verifier against all 19 pinned member manifest/evidence hashes and recompute the decimal statistics and artifact canonical hash. Result: PASS.\"\n61\t    },\n62\t    {\n63\t      \"clause\": \"D-109 R2.3\",\n64\t      \"source\": \"docs/decision_log.md:7056-7060\",\n65\t      \"verbatim\": \"3. `prior_observation_set` = every content-distinct governed observation known at the cutoff — valid, systematic-invalid, ordinary-invalid, blind holdout, and unresolved — with epoch and disposition recorded separately. (The current artifact's two ID-only `blind_exclusions` are insufficient and are superseded.)\",\n66\t      \"verification_plan\": \"Enumerate every exact-epoch validation tree, collapse copies by canonical content ID, authenticate the raw bytes, and assign one epoch plus one ruled disposition per content ID. The 38 identities are complete for the located candidate, but two dispositions require a ruling.\"\n67\t    },\n68\t    {\n69\t      \"clause\": \"D-109 R2.4\",\n70\t      \"source\": \"docs/decision_log.md:7061-7063\",\n71\t      \"verbatim\": \"4. Content identity is path-independent, derived from canonical primary-byte hashes; attempt identity is separate; copies do not create new observations.\",\n72\t      \"verification_plan\": \"Hash manifest.json and instrument_evidence.json bytes, canonical-JSON encode the two-name hash map, SHA-256 it, and collapse identical IDs. Implementation is joulewise/calibration_ledger.py:94-105,120-134. Result: 53 checkout copies collapse to 38 IDs.\"\n73\t    },\n74\t    {\n75\t      \"clause\": \"D-109 R2.5\",\n76\t      \"source\": \"docs/decision_log.md:7064-7068\",\n77\t      \"verbatim\": \"5. \\\"New\\\" (trigger population) = current authentic content IDs − `prior_observation_set`, regardless of capture timestamp or source root; a previously unknown historical artifact IS new when discovered. Every new observation is judged under the PRIOR artifact (D-102's prospective rule).\",\n78\t      \"verification_plan\": \"After issuance, subtract the exact 38-ID prior set from the authenticated ledger snapshot, independent of path/time, before applying triggers. The implemented subtraction is at joulewise/calibration_bracketing.py:870-893.\"\n79\t    },\n80\t    {\n81\t      \"clause\": \"D-109 R2.6\",\n82\t      \"source\": \"docs/decision_log.md:7069-7070\",\n83\t      \"verbatim\": \"6. New unresolved or unclassifiable attempts cause refusal; only after trigger disposition may a successor artifact absorb them.\",\n84\t      \"verification_plan\": \"Require every post-cutoff receipt to classify as valid, systematic-invalid or ordinary-invalid; unresolved/abandoned/null-content rows must refuse. Implemented refusal is at joulewise/calibration_bracketing.py:895-900.\"\n85\t    },\n86\t    {\n87\t      \"clause\": \"D-109 R2.7\",\n88\t      \"source\": \"docs/decision_log.md:7071-7074\",\n89\t      \"verbatim\": \"7. The 32-valid/6-invalid same-epoch inventory is a backfill CANDIDATE, not a ratified classification: identities may seed the backfill, but dispositions require raw-physics + hash verification before issuance, and any unresolved member blocks issuance.\",\n90\t      \"verification_plan\": \"For all 38 members: verify manifest and evidence hashes, verify raw/event hashes, replay causal clock-anchor derivation and the strict 59-pulse detector, verify the six-field epoch, then compare with candidate labeling. Result: 32 VERIFIED-VALID, 6 VERIFIED-INVALID, zero raw-physics unresolved; two final ledger dispositions remain ambiguous.\"\n91\t    },\n92\t    {\n93\t      \"clause\": \"D-109 R2.8\",\n94\t      \"source\": \"docs/decision_log.md:7075-7079\",\n95\t      \"verbatim\": \"8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38 TOTAL authenticated, content-distinct, VALID same-epoch observations — including previously blind observations once unblinded — not 38 post-cutoff observations. Under the candidate inventory, six further valid observations trigger re-derivation.\",\n96\t      \"verification_plan\": \"Count content-distinct ledger observations whose disposition is exactly valid and whose epoch equals d079_epoch. The implementation does this at joulewise/calibration_bracketing.py:901-908. Result is six further only under the candidate-tool 32-valid disposition proposal; it is eight further under the production writer's systematic-screen mapping.\"\n97\t    }\n98\t  ],\n99\t  \"inventory\": {\n100\t    \"where_it_lives\": {\n101\t      \"count_only_authority\": [\n102\t        \"docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:296-308\",\n103\t        \"configs/calibration/calibration_acceptance_d079_v2.json:225-233\"\n104\t      ],\n105\t      \"candidate_emitter\": \"scripts/calibration_ledger_backfill.py:42-117\",\n106\t      \"concrete_membership\": \"Implicit in the 53 exact-epoch validation custody trees under runs*/instrument_validation; no standalone serialized 38-row candidate file exists in the checkout or .desk.\",\n107\t      \"raw_archive\": \"/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup\",\n108\t      \"important_non_inventory\": \"docs/process_traces/2026-08-03-d111-backfill/MANIFEST.md is a manifest of 41 process artifacts, not the 38 calibration observations.\"\n109\t    },\n110\t    \"identity_method\": \"sha256(canonical_json({\\\"instrument_evidence.json\\\": sha256(evidence bytes), \\\"manifest.json\\\": sha256(manifest bytes)}))\",\n111\t    \"identity_method_source\": \"joulewise/calibration_ledger.py:94-105,120-134\",\n112\t    \"checkout_copy_count\": 53,\n113\t    \"content_distinct_count\": 38,\n114\t    \"candidate_label_counts\": {\n115\t      \"valid\": 32,\n116\t      \"invalid\": 6\n117\t    },\n118\t    \"analysis_only_member_set_sha256\": {\n119\t      \"value\": \"7c0ae751e3be9d180c932b14da1cc9b50f85a73a0821de03c7a7911728a25e95\",\n120\t      \"definition\": \"canonical SHA-256 of the ordered 38 candidate rows containing attempt_id, content_id, all artifact hashes, epoch, full T1, capture lexeme and bound lexeme; custody locator deliberately excluded. This digest is verification evidence, not a contract-defined production identity.\"\n121\t    }\n122\t  },\n123\t  \"epoch\": {\n124\t    \"epoch_id\": \"d079_epoch\",\n125\t    \"all_38_match\": true,\n126\t    \"fields\": {\n127\t      \"os_build\": \"25F84\",\n128\t      \"hardware_model\": \"Mac15,9\",\n129\t      \"power_policy\": \"ac_high_power\",\n130\t      \"sampling_interval_ms\": 100,\n131\t      \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n132\t      \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n133\t    },\n134\t    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:20-26,193-200\"\n135\t  },\n136\t  \"per_member\": [\n137\t    {\n138\t      \"n\": 1,\n139\t      \"attempt_id\": \"20260722T145535-e941c821\",\n140\t      \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n141\t      \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n142\t      \"evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\",\n143\t      \"raw_sha256\": \"b55f3471c70c54e0174b09e67486759fc532742e9bd671e53ce8324fe23209ef\",\n144\t      \"events_sha256\": \"605e2330d27f874621edb698c233542d7eb31fb8b8d1def044852a77a223b1bc\",\n145\t      \"bound_s\": \"0.03018980442653224\",\n146\t      \"verdict\": \"VERIFIED-VALID\",\n147\t      \"disposition\": \"valid\"\n148\t    },\n149\t    {\n150\t      \"n\": 2,\n151\t      \"attempt_id\": \"20260722T194118-9dc0749d\",\n152\t      \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n153\t      \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n154\t      \"evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\",\n155\t      \"raw_sha256\": \"aa36a9c1e8451e2a0de875a7ff45232c98bf0cce5cdcd5b827d176ea24aa85f7\",\n156\t      \"events_sha256\": \"0f543eb7f697d442a5c0ddce1fe6f3f69c268c96bdc7a5ffbb6e84f70e8f1d66\",\n157\t      \"bound_s\": \"0.026300679324099796\",\n158\t      \"verdict\": \"VERIFIED-VALID\",\n159\t      \"disposition\": \"valid\"\n160\t    },\n161\t    {\n162\t      \"n\": 3,\n163\t      \"attempt_id\": \"20260722T213749-563b9849\",\n164\t      \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n165\t      \"manifest_sha256\": \"b7dd23cf8a9e30d81a01ba0b3c5c5e0c21b4c325e48e1d02e046fb61b77cb0ac\",\n166\t      \"evidence_sha256\": \"1cc789e9558667e188f1859ba591a584a73eb4d2309612c924eebfb4cf5ffe80\",\n167\t      \"raw_sha256\": \"3684b27080f6b4254d61e1c5b3f0f25e8401257078145331ef2122b2c1893fd1\",\n168\t      \"events_sha256\": \"b179d606c17148e754bba07bb61c3d7a5c094e5a0e701251e7674b45472f5a4b\",\n169\t      \"bound_s\": \"0.2079182387602739\",\n170\t      \"verdict\": \"VERIFIED-INVALID\",\n171\t      \"disposition\": \"ordinary-invalid\",\n172\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n173\t    },\n174\t    {\n175\t      \"n\": 4,\n176\t      \"attempt_id\": \"20260722T214220-1acdbbc0\",\n177\t      \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n178\t      \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n179\t      \"evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\",\n180\t      \"raw_sha256\": \"7a4b62258d4d6afe251c4ed60a02835ac4d2b743f926260b2f621cb2301a72de\",\n181\t      \"events_sha256\": \"6f0c813bf5489f1fce820bddd1160d6936ec5dc6e89f1c3ca2aecdbedc2834af\",\n182\t      \"bound_s\": \"0.03312014638436772\",\n183\t      \"verdict\": \"VERIFIED-VALID\",\n184\t      \"disposition\": \"valid\"\n185\t    },\n186\t    {\n187\t      \"n\": 5,\n188\t      \"attempt_id\": \"20260722T215127-eeef661a\",\n189\t      \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n190\t      \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n191\t      \"evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\",\n192\t      \"raw_sha256\": \"8e275c342b5dde493e24e69f5a30fd7224ec36c21b324bd489508cda5860bff8\",\n193\t      \"events_sha256\": \"30efea52cd15580aa4f4f52b959a4b6a881db0df0f72a488ae4d4493d51a8f75\",\n194\t      \"bound_s\": \"0.022741007370546462\",\n195\t      \"verdict\": \"VERIFIED-VALID\",\n196\t      \"disposition\": \"valid\"\n197\t    },\n198\t    {\n199\t      \"n\": 6,\n200\t      \"attempt_id\": \"20260722T222332-901c5c13\",\n201\t      \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n202\t      \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n203\t      \"evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\",\n204\t      \"raw_sha256\": \"84adafc6e55a45a10e56d5cea6571f1b12dae15656a2a0274822eb96500f4744\",\n205\t      \"events_sha256\": \"1b7ce059e4b72885a77cb398704590e50e51b925cdae7bf77db1ad2b36dd7d59\",\n206\t      \"bound_s\": \"0.03355875667989999\",\n207\t      \"verdict\": \"VERIFIED-VALID\",\n208\t      \"disposition\": \"valid\"\n209\t    },\n210\t    {\n211\t      \"n\": 7,\n212\t      \"attempt_id\": \"20260722T232509-82642517\",\n213\t      \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n214\t      \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n215\t      \"evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\",\n216\t      \"raw_sha256\": \"56555a10ee248cb6e5692280881d3daaf406b0432c2c3d068e06c5b8d8d76e40\",\n217\t      \"events_sha256\": \"1c2b84546ed000dbb6f3378f5a1ef24ae008048209bcffee95644bbad585df6b\",\n218\t      \"bound_s\": \"0.027654085293084385\",\n219\t      \"verdict\": \"VERIFIED-VALID\",\n220\t      \"disposition\": \"valid\"\n221\t    },\n222\t    {\n223\t      \"n\": 8,\n224\t      \"attempt_id\": \"20260723T023058-8732d1c9\",\n225\t      \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n226\t      \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n227\t      \"evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\",\n228\t      \"raw_sha256\": \"49d0b16529d40d6ce7a8d125f9787ab37e46ddfeb6b06e1b69a28e1a7011cf67\",\n229\t      \"events_sha256\": \"962780bf83e89c2e5a4720e074e49f06c0aa49cac3989bed9035436ed734455a\",\n230\t      \"bound_s\": \"0.024753340330112727\",\n231\t      \"verdict\": \"VERIFIED-VALID\",\n232\t      \"disposition\": \"valid\"\n233\t    },\n234\t    {\n235\t      \"n\": 9,\n236\t      \"attempt_id\": \"20260723T052051-d9358c8a\",\n237\t      \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n238\t      \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n239\t      \"evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\",\n240\t      \"raw_sha256\": \"dac05b535d4faa2f8864a2be91a6c56df812b1631fd60aaebde8e680a6aebc8e\",\n241\t      \"events_sha256\": \"7e79ef10b6d9caae132b04ae1e59d584c569aa751084fa02e62e2cad5f794fd3\",\n242\t      \"bound_s\": \"0.025964638697819786\",\n243\t      \"verdict\": \"VERIFIED-VALID\",\n244\t      \"disposition\": \"valid\"\n245\t    },\n246\t    {\n247\t      \"n\": 10,\n248\t      \"attempt_id\": \"20260723T183306-4ce692b4\",\n249\t      \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n250\t      \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n251\t      \"evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\",\n252\t      \"raw_sha256\": \"bcd97c9bd9b0a0686fc84bfa9d117685b6a68f8beed7f84dfa503eacaf78d941\",\n253\t      \"events_sha256\": \"7341d55729c2a3ebf68739900105893b5f2d59bb55d57092ef20e2b94d6c95ca\",\n254\t      \"bound_s\": \"0.027262160888545217\",\n255\t      \"verdict\": \"VERIFIED-VALID\",\n256\t      \"disposition\": \"valid\"\n257\t    },\n258\t    {\n259\t      \"n\": 11,\n260\t      \"attempt_id\": \"20260723T194632-d04e038e\",\n261\t      \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n262\t      \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n263\t      \"evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\",\n264\t      \"raw_sha256\": \"b1660d10fcc5015f0ccc0e4e0a7464db3a5220d415c952f3d9635e512faab57c\",\n265\t      \"events_sha256\": \"a965e301af8f2cb662dca60a7b9706d9b6e7dbabdc6971abd3119c46fc7711d6\",\n266\t      \"bound_s\": \"0.024593263907495888\",\n267\t      \"verdict\": \"VERIFIED-VALID\",\n268\t      \"disposition\": \"valid\"\n269\t    },\n270\t    {\n271\t      \"n\": 12,\n272\t      \"attempt_id\": \"20260723T195730-bc4ba14a\",\n273\t      \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n274\t      \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n275\t      \"evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\",\n276\t      \"raw_sha256\": \"81669d5e0e81ccb1d05ae7d19befffbf41441a92a1e14f0dcb8c0b8d9b6f7a86\",\n277\t      \"events_sha256\": \"0343c61d357465919f99b13000e39f02b43575c68c5383e1f03ffc46a3a2ee24\",\n278\t      \"bound_s\": \"0.025305226022515448\",\n279\t      \"verdict\": \"VERIFIED-VALID\",\n280\t      \"disposition\": \"valid\"\n281\t    },\n282\t    {\n283\t      \"n\": 13,\n284\t      \"attempt_id\": \"20260723T221449-e9ae755e\",\n285\t      \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n286\t      \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n287\t      \"evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\",\n288\t      \"raw_sha256\": \"4e971efc4abef1f51a636a095fa807d1b395ed8342f5e7386aead5e9c466ce50\",\n289\t      \"events_sha256\": \"1caf0be478a75308070e0a93818618af2dd8ca69f51bd2e35f1994c5b7f9b2d0\",\n290\t      \"bound_s\": \"0.027702588281732055\",\n291\t      \"verdict\": \"VERIFIED-VALID\",\n292\t      \"disposition\": \"valid\"\n293\t    },\n294\t    {\n295\t      \"n\": 14,\n296\t      \"attempt_id\": \"20260723T223406-314f6d9e\",\n297\t      \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n298\t      \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n299\t      \"evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\",\n300\t      \"raw_sha256\": \"2c92bf2a3065493b00caf678a5ee8d78c93d3dba406979cb824058b355274f73\",\n301\t      \"events_sha256\": \"4a4a990161e35f05d9fbd36c1eb52f78c46551145348036e073aa2494519df29\",\n302\t      \"bound_s\": \"0.026173651901677253\",\n303\t      \"verdict\": \"VERIFIED-VALID\",\n304\t      \"disposition\": \"valid\"\n305\t    },\n306\t    {\n307\t      \"n\": 15,\n308\t      \"attempt_id\": \"20260724T014109-57844352\",\n309\t      \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n310\t      \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n311\t      \"evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\",\n312\t      \"raw_sha256\": \"9c806bcd26a0f6cce7f33c00d930d803e39f9bd4a6e186971d6123a470a1b13d\",\n313\t      \"events_sha256\": \"221c42b7f214515f9af84c2b9486315df70e3466c66b7beb5bf35e476bf5ae14\",\n314\t      \"bound_s\": \"0.02547564583006129\",\n315\t      \"verdict\": \"VERIFIED-VALID\",\n316\t      \"disposition\": \"valid\"\n317\t    },\n318\t    {\n319\t      \"n\": 16,\n320\t      \"attempt_id\": \"20260725T005132-a64711b7\",\n321\t      \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n322\t      \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n323\t      \"evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\",\n324\t      \"raw_sha256\": \"a22005ea981f8e3ac1f3ea65cfa6bd1d0777dc009203b5e2db73cce44d2aca4e\",\n325\t      \"events_sha256\": \"459dc8a3ec34eb7a3f2095d0c5b72e931f8d87199fd48812386684f36162f617\",\n326\t      \"bound_s\": \"0.023241581438247116\",\n327\t      \"verdict\": \"VERIFIED-VALID\",\n328\t      \"disposition\": \"valid\"\n329\t    },\n330\t    {\n331\t      \"n\": 17,\n332\t      \"attempt_id\": \"20260725T011533-0b5ec77c\",\n333\t      \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n334\t      \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n335\t      \"evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\",\n336\t      \"raw_sha256\": \"9934c97547e2cd77de640754c2c51399a66bc96a265f31d38616677ab9973c3d\",\n337\t      \"events_sha256\": \"c15516d15ae525051012e8655817625d37803dda2b8473917720cc5a29ef3043\",\n338\t      \"bound_s\": \"0.028891617940876635\",\n339\t      \"verdict\": \"VERIFIED-VALID\",\n340\t      \"disposition\": \"valid\"\n341\t    },\n342\t    {\n343\t      \"n\": 18,\n344\t      \"attempt_id\": \"20260725T022712-0a9534f5\",\n345\t      \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n346\t      \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n347\t      \"evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\",\n348\t      \"raw_sha256\": \"bb99b0b7086ee939a8fb789253e2c0502de27a05d056c78d46dc30fccfb862cf\",\n349\t      \"events_sha256\": \"a42487bd9202c043485eebc42a68f505b35faf158c8640f1393d287a1d36e0d1\",\n350\t      \"bound_s\": \"0.029197264796726408\",\n351\t      \"verdict\": \"VERIFIED-VALID\",\n352\t      \"disposition\": \"valid\"\n353\t    },\n354\t    {\n355\t      \"n\": 19,\n356\t      \"attempt_id\": \"20260725T030533-d3f076e5\",\n357\t      \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n358\t      \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n359\t      \"evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\",\n360\t      \"raw_sha256\": \"26b9ad5ba13e2c73e78ddfdf5be6a2b1cf4b8eb31881aad575ac1bb7ae0dabb9\",\n361\t      \"events_sha256\": \"180a700366e1a97a9e8649a6d98bbd2d814fe9d5fed7246f99b47aa1af5e6b84\",\n362\t      \"bound_s\": \"0.024879191521227362\",\n363\t      \"verdict\": \"VERIFIED-VALID\",\n364\t      \"disposition\": \"valid\"\n365\t    },\n366\t    {\n367\t      \"n\": 20,\n368\t      \"attempt_id\": \"20260725T055825-b10cb348\",\n369\t      \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n370\t      \"manifest_sha256\": \"eebf3524d9e0b41c022c5e57d4b16787e98302e0d7c28381036415117fafb3ba\",\n371\t      \"evidence_sha256\": \"e0d525e0923f88572f7530f447a3bc8e889ef80a47d662840b86c40b4a35f285\",\n372\t      \"raw_sha256\": \"ed13e60dcfe12d7ce3900798dfbafb7936baa3700cdf58d0f6c1d0fc1790a4b8\",\n373\t      \"events_sha256\": \"fbb3d05c9185ed416d9c138fc63dc32d56b1cd465059007962f9273b53dce671\",\n374\t      \"bound_s\": null,\n375\t      \"verdict\": \"VERIFIED-INVALID\",\n376\t      \"disposition\": \"ordinary-invalid\",\n377\t      \"raw_reason\": \"fresh causal anchor unknown: wall_minus_monotonic_span_exceeded\"\n378\t    },\n379\t    {\n380\t      \"n\": 21,\n381\t      \"attempt_id\": \"20260725T060617-97c5cba6\",\n382\t      \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n383\t      \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n384\t      \"evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\",\n385\t      \"raw_sha256\": \"85583f5f07299f38f4f912581e2cfc03453d3a0e85a0de486b3406a355b2c9f2\",\n386\t      \"events_sha256\": \"c904c5f1a1c6557117b6fbde70dc8358dca773f94fc0c611cd50e92c3a3e2ffa\",\n387\t      \"bound_s\": \"0.025045994537554683\",\n388\t      \"verdict\": \"VERIFIED-VALID\",\n389\t      \"disposition\": \"valid\"\n390\t    },\n391\t    {\n392\t      \"n\": 22,\n393\t      \"attempt_id\": \"20260726T000039-491995f3\",\n394\t      \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n395\t      \"manifest_sha256\": \"b5e1d1195eb8c52bb41211b464909723754e5753bb866ced6f5715d83769ef65\",\n396\t      \"evidence_sha256\": \"9584cd7cdc44e5ba4d176475ce2bf6f70d04e163778fd6e9d5e46cec02303c00\",\n397\t      \"raw_sha256\": \"b916d0b8fc79e8fc7b261c6d608307fbae94bd3c89189e2256cafcf483378c2d\",\n398\t      \"events_sha256\": \"579c2adf45f245dbf31e69b83617fceaf28e63be70677fe0dcd8104a82c79248\",\n399\t      \"bound_s\": \"0.035435840879704805\",\n400\t      \"verdict\": \"VERIFIED-VALID\",\n401\t      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer and D-102\"\n402\t    },\n403\t    {\n404\t      \"n\": 23,\n405\t      \"attempt_id\": \"20260726T031222-e0ce33f5\",\n406\t      \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n407\t      \"manifest_sha256\": \"5ec9e27a9bdef89d8e83ca2fd2ee0c1c2d8d2effd56139ac904d1b032c3fc378\",\n408\t      \"evidence_sha256\": \"8d0b2d48460c71d35b2b3b7124b3168c86a497b5a674348451ea5d73931adab3\",\n409\t      \"raw_sha256\": \"c5674ce16dba60b5f0f61ffa5dbe6d7c38bc11747f627e120f6b96af7b9f2fe1\",\n410\t      \"events_sha256\": \"7ba5009ade8a7a870fcb119297dc34a54dcd78f54d13d463e2b4de721db7100b\",\n411\t      \"bound_s\": \"0.023854405254729094\",\n412\t      \"verdict\": \"VERIFIED-VALID\",\n413\t      \"disposition\": \"valid\"\n414\t    },\n415\t    {\n416\t      \"n\": 24,\n417\t      \"attempt_id\": \"20260726T225227-1f550773\",\n418\t      \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n419\t      \"manifest_sha256\": \"5837bd2c5be6769d63faa57a5d59311241038be7f92de6101b61566b54d89131\",\n420\t      \"evidence_sha256\": \"95941785a8fca5b74019da42d18d280abda639f92442ad57195b852ca567b564\",\n421\t      \"raw_sha256\": \"db6416cada6ea8c0bc84109903fc734d71c0f5a4d8451bafa05a05a76dd7b89d\",\n422\t      \"events_sha256\": \"2de1638cb73fa1a23105a81fe9cdcf9774f467adfcf6fa59bd29029c15a1a9cf\",\n423\t      \"bound_s\": \"0.04916527633725107\",\n424\t      \"verdict\": \"VERIFIED-INVALID\",\n425\t      \"disposition\": \"ordinary-invalid\",\n426\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n427\t    },\n428\t    {\n429\t      \"n\": 25,\n430\t      \"attempt_id\": \"20260726T225920-ab4272f5\",\n431\t      \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n432\t      \"manifest_sha256\": \"1696f470f0cc543a62cc40a819068a4b7b9f62058fd8d0dd1707870dd25b59e5\",\n433\t      \"evidence_sha256\": \"5b1c9dce56202e1d8af74e71b37aaa1538f0e53fcdded1e05c61cff90f41cda5\",\n434\t      \"raw_sha256\": \"4f83a36625a199a1e5e552953afbdc004bd5144756c8aa2bf657c8c714b4453f\",\n435\t      \"events_sha256\": \"dc704274c1c608a3a87387575c7a36e868c988f9737b033775f55d12791f80f5\",\n436\t      \"bound_s\": \"0.028145704403191807\",\n437\t      \"verdict\": \"VERIFIED-VALID\",\n438\t      \"disposition\": \"valid\"\n439\t    },\n440\t    {\n441\t      \"n\": 26,\n442\t      \"attempt_id\": \"20260727T015824-45feb516\",\n443\t      \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n444\t      \"manifest_sha256\": \"a7ac96e151419313594510f7511071cbdd710a1ab0837fef25a792ccc1b38d48\",\n445\t      \"evidence_sha256\": \"96f2af22ae5b18ba70f08ec2ed40c54abe0934508ae0d7cfb8fadb9de19432d8\",\n446\t      \"raw_sha256\": \"d0f8ab38ade1df00d957597f6ae0bfdffce047d8611416ecb434f91c4e35ae47\",\n447\t      \"events_sha256\": \"c75224662805694c090f458e6462f8a69581e39e7cf9a4f03d1c3d3b2ae7a371\",\n448\t      \"bound_s\": \"0.029425288011457773\",\n449\t      \"verdict\": \"VERIFIED-VALID\",\n450\t      \"disposition\": \"valid\"\n451\t    },\n452\t    {\n453\t      \"n\": 27,\n454\t      \"attempt_id\": \"20260727T020611-4a409a30\",\n455\t      \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n456\t      \"manifest_sha256\": \"dc30e9df75b0e4bc561c6f9d641ed3dff696697508333de6707d354151bd96ec\",\n457\t      \"evidence_sha256\": \"e3f4df9cf8bf4f1edfacbd10072bd53c5c1b59a873e4c25ee1727d74307ab3f8\",\n458\t      \"raw_sha256\": \"0961bf040013bf35d7d9fd2e5ad4b9d212d0dab9d733357c5193569ba7b92acd\",\n459\t      \"events_sha256\": \"bea8ab60b84b2ff7e00eff035c1187c837f26fdc30b91bfd0d4ca8ee6d15ecab\",\n460\t      \"bound_s\": \"0.029339001207750293\",\n461\t      \"verdict\": \"VERIFIED-VALID\",\n462\t      \"disposition\": \"valid\"\n463\t    },\n464\t    {\n465\t      \"n\": 28,\n466\t      \"attempt_id\": \"20260727T050047-95e2f87e\",\n467\t      \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n468\t      \"manifest_sha256\": \"d572e55594e97a4d4f3fb82295c8ad7aedac68c15c18e7615f3ac13e91ebea8a\",\n469\t      \"evidence_sha256\": \"2d70134135398b613638ae6ec62607913026c7d0cdfa9da1dfc77c657fa0e091\",\n470\t      \"raw_sha256\": \"b439d5bc06855943055795db69117ab612866d397eef219d73e0a576545b06c5\",\n471\t      \"events_sha256\": \"a90f500e118b1e88041167fb9fb3808ae0e27b83fa5b664f63c98adecf1ae7a1\",\n472\t      \"bound_s\": \"0.028854562420070173\",\n473\t      \"verdict\": \"VERIFIED-VALID\",\n474\t      \"disposition\": \"valid\"\n475\t    },\n476\t    {\n477\t      \"n\": 29,\n478\t      \"attempt_id\": \"20260729T204105-39d25f8a\",\n479\t      \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n480\t      \"manifest_sha256\": \"3aec4fc319e1de5a3b34d3552774ee4cf59ad9b1134001c8176d538f1304871f\",\n481\t      \"evidence_sha256\": \"4323c8c5242812b95e544213367dd75f0bc927605d73c78c1a491a84dd829026\",\n482\t      \"raw_sha256\": \"4f0cd62a013d6cc639e11637e425b8e09af02703828d4d0e9638a30ef70e88fc\",\n483\t      \"events_sha256\": \"0ef0f3e5779fb6b1aec6bb48fb60a76c175106b192f16f8aeaf95e3961b75c59\",\n484\t      \"bound_s\": \"0.031467745880268516\",\n485\t      \"verdict\": \"VERIFIED-VALID\",\n486\t      \"disposition\": \"valid\"\n487\t    },\n488\t    {\n489\t      \"n\": 30,\n490\t      \"attempt_id\": \"20260730T014035-124df355\",\n491\t      \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n492\t      \"manifest_sha256\": \"bb894782e7dd95d38576514fe9360335552129d6de116e2a05a82c17a70702f5\",\n493\t      \"evidence_sha256\": \"f8946df7f5495d6e5c64f90490b94ca2eab94f10ed16b7298e5741dadbe182b1\",\n494\t      \"raw_sha256\": \"95d50522d5eef61dbf2b9b815dce3f62e8791fe417942883908dde762351332b\",\n495\t      \"events_sha256\": \"d66899983a1d8e7b4bc7ecb11c5740534e101f4fbdd2810dd41ff00910277379\",\n496\t      \"bound_s\": \"0.027788174032371493\",\n497\t      \"verdict\": \"VERIFIED-VALID\",\n498\t      \"disposition\": \"valid\"\n499\t    },\n500\t    {\n501\t      \"n\": 31,\n502\t      \"attempt_id\": \"20260730T210703-f76b5771\",\n503\t      \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n504\t      \"manifest_sha256\": \"e40353dfd883d773414378893f27bc617cfa972f62793b0f35cc9efa30ed7d44\",\n505\t      \"evidence_sha256\": \"0f5e3ea38ff0f833840895e065941494c71c4cd9bf0fe222a9e08ca24ddc3ed8\",\n506\t      \"raw_sha256\": \"718b9046d134fc2a9f089818ea2e5c3aac05c10f056f942c8702ec3b4cdabf75\",\n507\t      \"events_sha256\": \"aaf29ec68222439453b790725b6849040c3f7c1cb5accf096d3a722edebf9664\",\n508\t      \"bound_s\": \"0.026131301462788137\",\n509\t      \"verdict\": \"VERIFIED-VALID\",\n510\t      \"disposition\": \"valid\"\n511\t    },\n512\t    {\n513\t      \"n\": 32,\n514\t      \"attempt_id\": \"20260731T012210-374020b6\",\n515\t      \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n516\t      \"manifest_sha256\": \"f64a179f03a6b3efecaea6e3ad8ff08ba8c354b9f57023f0929781fd2d133545\",\n517\t      \"evidence_sha256\": \"21a6296fc74542a6400ab5562376b9bf969a1d906c8f9076f89dc9916cef1b52\",\n518\t      \"raw_sha256\": \"0f3b509c48e42a9cbcf32ac3a446d9c13d38766328f9569a96d397a685ad2f2d\",\n519\t      \"events_sha256\": \"624b9c26e71648272e36c85fa7884aa258851039a7e77a7be123e1290d2c4b79\",\n520\t      \"bound_s\": \"0.024850427856341006\",\n521\t      \"verdict\": \"VERIFIED-VALID\",\n522\t      \"disposition\": \"valid\"\n523\t    },\n524\t    {\n525\t      \"n\": 33,\n526\t      \"attempt_id\": \"20260731T161713-b8b08280\",\n527\t      \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n528\t      \"manifest_sha256\": \"e65aed76d770fbcd9c07b6c2dc26335ddf593533ff1ab6a46cb1bc9bdd119d0a\",\n529\t      \"evidence_sha256\": \"2cda4856ae7939067f0a6ebbbdb865871e437e1c652b0dd438e33cb5ffef1583\",\n530\t      \"raw_sha256\": \"464f5f9ca38818544e54061407251ef3d13541c90c8e5c6f05ee54fe8a913068\",\n531\t      \"events_sha256\": \"2bfd2ac5f0ba88e02a89dbc070837ce3bb1161b2d3067a6176e720bb778b4df1\",\n532\t      \"bound_s\": \"0.030972654450356962\",\n533\t      \"verdict\": \"VERIFIED-VALID\",\n534\t      \"disposition\": \"valid\"\n535\t    },\n536\t    {\n537\t      \"n\": 34,\n538\t      \"attempt_id\": \"20260731T214355-126fc2ab\",\n539\t      \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n540\t      \"manifest_sha256\": \"ad3aa2345df71df05fb5913ef52210443eb07cfbbb5824e48794b6892557848d\",\n541\t      \"evidence_sha256\": \"1958d58c35dfa30c18671abafcddf3d43c9328f586ce2051d1fb83ab99b51d5f\",\n542\t      \"raw_sha256\": \"c14ef61161fc9bf463840d5f62e1cdcd9bc2fe586297e5d89a6334e19f8dd21f\",\n543\t      \"events_sha256\": \"89808fe44225b7870585a1f2883ff43b01ec0b02507775900ada0a60251f145c\",\n544\t      \"bound_s\": null,\n545\t      \"verdict\": \"VERIFIED-INVALID\",\n546\t      \"disposition\": \"ordinary-invalid\",\n547\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n548\t    },\n549\t    {\n550\t      \"n\": 35,\n551\t      \"attempt_id\": \"20260801T010113-e859f3aa\",\n552\t      \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n553\t      \"manifest_sha256\": \"52aa9e9b4485a352d1ba2bd40e500f71cab989967d1db6e7a130fe9c157e0647\",\n554\t      \"evidence_sha256\": \"6c350a69406f92f4f1d68e30684f6b36b2f233fba5f52070a73f23c3d767fd45\",\n555\t      \"raw_sha256\": \"1302b53b6aeab97ee57b35cda8003ffb6d107265979614880910c24fdbbb5e7c\",\n556\t      \"events_sha256\": \"887ea9f6bc663ac5bc8cfe1c6d898262a2089602406186f83ff0f750983a841b\",\n557\t      \"bound_s\": \"0.41198917978147415\",\n558\t      \"verdict\": \"VERIFIED-INVALID\",\n559\t      \"disposition\": \"ordinary-invalid\",\n560\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n561\t    },\n562\t    {\n563\t      \"n\": 36,\n564\t      \"attempt_id\": \"20260801T010805-ff3fdc88\",\n565\t      \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n566\t      \"manifest_sha256\": \"fd5906ccd884670c9d40a57e7b8b4755357bc91c89f281449a080fe5c2007402\",\n567\t      \"evidence_sha256\": \"62967d66a74467735011f159a523f50b6409287bf96899446e4a02fa2c8e2eed\",\n568\t      \"raw_sha256\": \"c39bc0c6c55a3deabdffdf8bfdad95e061fb464def586edafdc19dbd1d8ea5c2\",\n569\t      \"events_sha256\": \"10e9035731a2d54a9469c66318568b6f2e91a0ac3fecdbfad94dfb62c22bf0fc\",\n570\t      \"bound_s\": null,\n571\t      \"verdict\": \"VERIFIED-INVALID\",\n572\t      \"disposition\": \"ordinary-invalid\",\n573\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n574\t    },\n575\t    {\n576\t      \"n\": 37,\n577\t      \"attempt_id\": \"20260801T014059-8c3bfe9e\",\n578\t      \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n579\t      \"manifest_sha256\": \"7d2967b125324c65e0d57a16950a0e1c2e2946464b7eb89667e8fc2410550149\",\n580\t      \"evidence_sha256\": \"c1653f369e05e9186d0c6d06231993575ee23c1fd813b96f1094d74dfbaac0ad\",\n581\t      \"raw_sha256\": \"f1a9350cbfdb0ec4c0a909b5d2b77798e16f754132499602b426a1068274465f\",\n582\t      \"events_sha256\": \"33f78ee6e299643d8f5929fc2e339f3e13959eb6983a7db8b8af4bd936a0700d\",\n583\t      \"bound_s\": \"0.032786870825707914\",\n584\t      \"verdict\": \"VERIFIED-VALID\",\n585\t      \"disposition\": \"valid\"\n586\t    },\n587\t    {\n588\t      \"n\": 38,\n589\t      \"attempt_id\": \"20260801T064830-c76f5d1c\",\n590\t      \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n591\t      \"manifest_sha256\": \"6127f706081c4686164ecca83032ab86bdc467170d55b24e537255cfdacac4dc\",\n592\t      \"evidence_sha256\": \"4c2752a194dbd1fc39aaf82e11071cccab4283c81f46208657bd849af6c23a06\",\n593\t      \"raw_sha256\": \"dab52b86df50235d78c39ddda87b3f4620b6dfdead9050640184204630cd5b1f\",\n594\t      \"events_sha256\": \"31e245dcaf050740a69f52ab3afa1783e2081e43a089dc57045be6039f7503e6\",\n595\t      \"bound_s\": \"0.0350400833260715\",\n596\t      \"verdict\": \"VERIFIED-VALID\",\n597\t      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer\"\n598\t    }\n599\t  ],\n600\t  \"raw_physics_method\": {\n601\t    \"valid_members\": \"Used verify_stored_evidence_physics, which rejects stored-status substitution, re-derives the causal anchor, reconstructs all pulse commands from events.jsonl, re-fits all 59 pulses, requires complete detection/no spurious plateaus/no reasons, checks every stored residual enclosure contains the refit, and returns max(stored,fresh) bound.\",\n602\t    \"valid_method_source\": \"joulewise/powermetrics_fiducial.py:1088-1164; docs/contracts/powermetrics_fiducial.md:183-211\",\n603\t    \"invalid_members\": \"Re-derived the causal anchor directly from native powermetrics records and recorded ClockStamps. All six independently returned unknown; an unresolved own anchor is forced invalid under the contract.\",\n604\t    \"hash_evidence\": \"Each selected custody manifest's lines 3-6 bind events, instrument evidence, power trace and raw plist. Every listed digest matched the bytes.\"\n605\t  },\n606\t  \"bootstrap_computation\": {\n607\t    \"authoritative_result\": \"NOT COMPUTABLE WITHOUT RULING/IMPORT CONTRACT\",\n608\t    \"required_prior_observation_set\": \"The exact 38 content IDs in per_member, each with epoch_id=d079_epoch and the final ruled disposition. No additional fixture-known-holdout row is evidenced by a real content bundle; configs/calibration/calibration_acceptance_d079_v2.json:222 is explicitly fixture data.\",\n609\t    \"receipt_algorithm_from_schema\": [\n610\t      \"receipt_core is canonical JSON with sorted keys, separators ',' and ':', UTF-8, allow_nan=false; receipt_digest=sha256(receipt_core). See joulewise/calibration_ledger.py:94-105,155-160.\",\n611\t      \"Each receipt contains sequence, predecessor_digest, event, attempt_id, content_id, artifact hashes, six-field epoch, full T1, capture lexeme, exact bound lexeme, disposition and custody locator. See joulewise/calibration_ledger.py:590-622.\",\n612\t      \"The parser requires a reservation before each finalization. See joulewise/calibration_ledger.py:409-465 and finalize_attempt_receipt at :716-777.\",\n613\t      \"The head pin is the final receipt's sequence and receipt_digest with ledger_schema. See joulewise/calibration_ledger.py:780-789.\"\n614\t    ],\n615\t    \"conditional_non_authoritative_replays\": [\n616\t      {\n617\t        \"assumptions\": \"Attempt IDs sorted ascending; one synthetic reservation immediately followed by one finalization per content ID; first hash-complete custody copy selected; candidate-tool mapping of all stored-valid rows to valid and stored-invalid rows to ordinary-invalid.\",\n618\t        \"sequence\": 76,\n619\t        \"head_digest\": \"cb410907660ed8a120d4e1d04a7e9af489b69d83686a8bf7658b3f73e7e3335a\",\n620\t        \"prior_observation_rows_sha256\": \"d29404feea08496453538d8b3994af1c4b64c12a86b950a3aa96a604cb6690c6\",\n621\t        \"dispositions\": {\n622\t          \"valid\": 32,\n623\t          \"ordinary-invalid\": 6\n624\t        },\n625\t        \"warning\": \"Illustrative only; the assumptions are not authorized by D-109 or an import schema.\"\n626\t      },\n627\t      {\n628\t        \"assumptions\": \"Same ordering/custody rules, but apply the production writer's preflight-screen mapping to members 22 and 38.\",\n629\t        \"sequence\": 76,\n630\t        \"head_digest\": \"8e80b6e93804df098f9fbec66740757073d235019e19990c7a9d8270b28337f1\",\n631\t        \"prior_observation_rows_sha256\": \"f28ddf8e0995230857c7e7db11c031084e18e8919ea1b9b373ae2112a9a936bf\",\n632\t        \"dispositions\": {\n633\t          \"valid\": 30,\n634\t          \"systematic-invalid\": 2,\n635\t          \"ordinary-invalid\": 6\n636\t        },\n637\t        \"warning\": \"Illustrative only; differs from D-109 R2.8's stated six-further consequence.\"\n638\t      }\n639\t    ],\n640\t    \"additional_implementation_gap\": \"append_pending_receipt requires the current physical ledger head to equal the committed pin before each new reservation (joulewise/calibration_ledger.py:673-690). Once one reservation/finalization pair advances the physical ledger, another reservation cannot be appended under the unchanged genesis pin. A batch bootstrap/import route is therefore required; none exists.\"\n641\t  },\n642\t  \"derivation_corpus\": {\n643\t    \"n\": 19,\n644\t    \"unchanged\": true,\n645\t    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:46-183\",\n646\t    \"artifact_file_sha256\": \"9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb\",\n647\t    \"stored_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n648\t    \"computed_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n649\t    \"match\": true,\n650\t    \"reconstructed_statistics\": {\n651\t      \"minimum_s\": \"0.022741007370546462\",\n652\t      \"minimum_member\": \"20260722T215127-eeef661a\",\n653\t      \"maximum_s\": \"0.03355875667989999\",\n654\t      \"maximum_member\": \"20260722T222332-901c5c13\",\n655\t      \"range_s\": \"0.010817749309353528\",\n656\t      \"mean_s\": \"0.026950033977532761\",\n657\t      \"sample_sd_s\": \"0.002970761365307205\"\n658\t    },\n659\t    \"note\": \"The current derivation_sha256 covers the complete artifact core excluding the hash field, not only the n=19 table (joulewise/calibration_bracketing.py:155-177). Issuance edits will therefore require a new canonical hash even though the threshold-producing n=19 remains unchanged.\"\n660\t  },\n661\t  \"D102_corpus_doubling\": {\n662\t    \"binding_rule\": \"38 total authenticated, content-distinct, valid same-epoch observations\",\n663\t    \"implementation_source\": \"joulewise/calibration_bracketing.py:901-908\",\n664\t    \"candidate_tool_disposition_result\": {\n665\t      \"current_valid_total\": 32,\n666\t      \"additional_valid_needed\": 6,\n667\t      \"trigger_now\": false,\n668\t      \"matches_D109_R2_8\": true\n669\t    },\n670\t    \"production_writer_disposition_result\": {\n671\t      \"current_valid_total\": 30,\n672\t      \"additional_valid_needed\": 8,\n673\t      \"trigger_now\": false,\n674\t      \"matches_D109_R2_8\": false\n675\t    },\n676\t    \"decision\": \"BLOCKED pending the B1 disposition ruling. The report does not choose between these counts.\"\n677\t  },\n678\t  \"verification\": [\n679\t    {\n680\t      \"id\": \"V1\",\n681\t      \"result\": \"PASS\",\n682\t      \"check\": \"Enumerated runs*/instrument_validation manifests, exact six-field epoch filtered, canonical content IDs recomputed.\",\n683\t      \"observed\": \"53 checkout custody copies; 38 distinct IDs; stored labels 32 valid/6 invalid.\"\n684\t    },\n685\t    {\n686\t      \"id\": \"V2\",\n687\t      \"result\": \"PASS\",\n688\t      \"check\": \"For every selected representative, rehashed every manifest-listed artifact and every evidence-internal artifact hash.\",\n689\t      \"observed\": \"Zero missing or mismatched bytes.\"\n690\t    },\n691\t    {\n692\t      \"id\": \"V3\",\n693\t      \"result\": \"PASS\",\n694\t      \"check\": \"Replayed strict raw physics for every candidate-valid observation and causal-anchor physics for every candidate-invalid observation.\",\n695\t      \"observed\": \"32 VERIFIED-VALID; 6 VERIFIED-INVALID; 0 raw unresolved.\"\n696\t    },\n697\t    {\n698\t      \"id\": \"V4\",\n699\t      \"result\": \"PASS\",\n700\t      \"check\": \"PYTHONDONTWRITEBYTECODE=1 python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact configs/calibration/calibration_acceptance_d079_v2.json\",\n701\t      \"observed\": \"PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK; n=19 statistics reproduced.\"\n702\t    },\n703\t    {\n704\t      \"id\": \"V5\",\n705\t      \"result\": \"PASS\",\n706\t      \"check\": \"Canonical artifact-core SHA-256 recomputation.\",\n707\t      \"observed\": \"stored=computed=3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d.\"\n708\t    },\n709\t    {\n710\t      \"id\": \"V6\",\n711\t      \"result\": \"PASS\",\n712\t      \"check\": \"Final git status.\",\n713\t      \"observed\": \"## main...origin/main; no changes.\"\n714\t    }\n715\t  ],\n716\t  \"flags\": [\n717\t    {\n718\t      \"id\": \"NO_EDITS\",\n719\t      \"level\": \"informational\",\n720\t      \"text\": \"Read-only verification; no artifact, ledger, pin, report or state file was created or modified.\"\n721\t    },\n722\t    {\n723\t      \"id\": \"ISSUANCE_BLOCKED\",\n724\t      \"level\": \"blocking\",\n725\t      \"text\": \"Lead must first rule the two high-bound dispositions and authorize a deterministic historical-import/bootstrap contract, including ordering and custody selection. Only then can one exact prior_observation_set, sequence and head digest be issued.\"\n726\t    }\n727\t  ],\n728\t  \"next_exact_step\": \"Lead rules whether members 20260726T000039-491995f3 and 20260801T064830-c76f5d1c are ledger-valid or systematic-invalid, then specifies the authenticated batch-import ordering/custody rule. Recompute the single resulting 76-receipt chain, review its exact head, and only in a separately authorized write session bootstrap the ledger, update and commit the head pin, and issue the acceptance artifact.\"\n729\t}\n730\t```"}]},"uuid":"db5a984e-c70e-4f45-a319-007973acd308","timestamp":"2026-08-06T08:35:26.699Z","toolUseResult":{"type":"text","file":{"filePath":"/Users/edr/code/JouleWise/docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md","content":"```json\n{\n  \"schema\": \"claude-codex-report/v1\",\n  \"genre\": \"verification\",\n  \"status\": \"findings\",\n  \"completion\": \"complete\",\n  \"summary\": \"BLOCKED. All 38 content-distinct candidates were recovered, hash-authenticated, epoch-checked, and replayed from raw physics: 32 VERIFIED-VALID and 6 VERIFIED-INVALID, with no missing raw evidence. Issuance is not ready because two verified-valid observations exceed the systematic-failure screen and therefore lack an unambiguous ledger disposition, and the repository does not specify a deterministic authenticated historical-import/bootstrap transaction from which one authoritative sequence/head digest can be computed.\",\n  \"workspace\": {\n    \"head_start\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n    \"head_end\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n    \"branch\": \"main\",\n    \"pathspec\": [],\n    \"unowned_dirty\": [],\n    \"write_scope\": \"none\",\n    \"edits\": \"none\"\n  },\n  \"verdict\": {\n    \"overall\": \"BLOCKED\",\n    \"prompt_vs_R2_divergence\": false,\n    \"raw_member_results\": {\n      \"VERIFIED-VALID\": 32,\n      \"VERIFIED-INVALID\": 6,\n      \"UNRESOLVED\": 0\n    },\n    \"blocking_items\": [\n      {\n        \"id\": \"B1\",\n        \"type\": \"ledger_disposition_ruling\",\n        \"members\": [\n          \"20260726T000039-491995f3\",\n          \"20260801T064830-c76f5d1c\"\n        ],\n        \"reason\": \"Both replay as physically valid, matching the candidate inventory, but their bounds 0.035435840879704805 and 0.0350400833260715 exceed the ratified 0.033558756679900 preflight screen. The production writer maps such a valid capture to systematic-invalid at scripts/validate_powermetrics_fiducial.py:664-671; D-102 explicitly calls the first member a systematic failure at docs/decision_log.md:6298-6301. The backfill candidate tool instead proposes valid solely from stored status at scripts/calibration_ledger_backfill.py:58-63. Selecting either disposition is lead-owned.\"\n      },\n      {\n        \"id\": \"B2\",\n        \"type\": \"bootstrap_contract_gap\",\n        \"members\": \"all 38\",\n        \"reason\": \"No historical-import/bootstrap API, receipt ordering, duplicate-custody selection rule, or import-transaction schema exists. The candidate tool emits only an unauthoritative candidate set and never appends the ledger (scripts/calibration_ledger_backfill.py:2-7,90-117). Because receipt digests bind sequence, predecessor, disposition, artifact hashes and absolute custody locator (joulewise/calibration_ledger.py:590-622), more than one valid head digest is possible.\"\n      }\n    ]\n  },\n  \"binding_clauses\": [\n    {\n      \"clause\": \"D-109 R1.4\",\n      \"source\": \"docs/decision_log.md:7027-7039\",\n      \"verbatim\": \"4. The acceptance artifact pins its baseline ledger head. Evaluation ALSO requires the independent current-head pin (clause below), verifies one complete non-forked chain extension from baseline to current, and threads ONE immutable ledger snapshot through every consumer path (session, direct runner path, secondary verifier) — repeated independent loads are a refusal-grade defect. Anti-rollback authority: a REPO-COMMITTED head-pin file `{sequence, head_digest, ledger_schema}` (existing checked-in byte-pin trust model; no second trusted latest-sequence store). Rotation is epoch-bounded — at most one lead-controlled quiet-machine collection session — and NO claim evaluation may occur between ledger advancement and pin commit; a physical head differing from the committed pin refuses.\",\n      \"verification_plan\": \"After an authorized bootstrap, recompute every receipt digest, require one linear chain, require the artifact cutoff to equal an exact receipt, require the physical head to equal the separately committed pin, and trace one snapshot object through every consumer. This session verified the implemented digest/head machinery but could not select an authoritative bootstrap head because no import transaction is specified.\"\n    },\n    {\n      \"clause\": \"D-109 R2.1\",\n      \"source\": \"docs/decision_log.md:7053\",\n      \"verbatim\": \"1. The issuance cutoff is an exact ledger sequence + head digest.\",\n      \"verification_plan\": \"Compute the final receipt count and digest only after disposition, ordering and custody-locator rules are fixed. Current fixture cutoff remains non-production genesis sequence 0/all-zero digest at configs/calibration/calibration_acceptance_d079_v2.json:14-18.\"\n    },\n    {\n      \"clause\": \"D-109 R2.2\",\n      \"source\": \"docs/decision_log.md:7054-7055\",\n      \"verbatim\": \"2. `derivation_corpus` remains exactly the n=19 threshold-producing observations.\",\n      \"verification_plan\": \"Re-run the corpus verifier against all 19 pinned member manifest/evidence hashes and recompute the decimal statistics and artifact canonical hash. Result: PASS.\"\n    },\n    {\n      \"clause\": \"D-109 R2.3\",\n      \"source\": \"docs/decision_log.md:7056-7060\",\n      \"verbatim\": \"3. `prior_observation_set` = every content-distinct governed observation known at the cutoff — valid, systematic-invalid, ordinary-invalid, blind holdout, and unresolved — with epoch and disposition recorded separately. (The current artifact's two ID-only `blind_exclusions` are insufficient and are superseded.)\",\n      \"verification_plan\": \"Enumerate every exact-epoch validation tree, collapse copies by canonical content ID, authenticate the raw bytes, and assign one epoch plus one ruled disposition per content ID. The 38 identities are complete for the located candidate, but two dispositions require a ruling.\"\n    },\n    {\n      \"clause\": \"D-109 R2.4\",\n      \"source\": \"docs/decision_log.md:7061-7063\",\n      \"verbatim\": \"4. Content identity is path-independent, derived from canonical primary-byte hashes; attempt identity is separate; copies do not create new observations.\",\n      \"verification_plan\": \"Hash manifest.json and instrument_evidence.json bytes, canonical-JSON encode the two-name hash map, SHA-256 it, and collapse identical IDs. Implementation is joulewise/calibration_ledger.py:94-105,120-134. Result: 53 checkout copies collapse to 38 IDs.\"\n    },\n    {\n      \"clause\": \"D-109 R2.5\",\n      \"source\": \"docs/decision_log.md:7064-7068\",\n      \"verbatim\": \"5. \\\"New\\\" (trigger population) = current authentic content IDs − `prior_observation_set`, regardless of capture timestamp or source root; a previously unknown historical artifact IS new when discovered. Every new observation is judged under the PRIOR artifact (D-102's prospective rule).\",\n      \"verification_plan\": \"After issuance, subtract the exact 38-ID prior set from the authenticated ledger snapshot, independent of path/time, before applying triggers. The implemented subtraction is at joulewise/calibration_bracketing.py:870-893.\"\n    },\n    {\n      \"clause\": \"D-109 R2.6\",\n      \"source\": \"docs/decision_log.md:7069-7070\",\n      \"verbatim\": \"6. New unresolved or unclassifiable attempts cause refusal; only after trigger disposition may a successor artifact absorb them.\",\n      \"verification_plan\": \"Require every post-cutoff receipt to classify as valid, systematic-invalid or ordinary-invalid; unresolved/abandoned/null-content rows must refuse. Implemented refusal is at joulewise/calibration_bracketing.py:895-900.\"\n    },\n    {\n      \"clause\": \"D-109 R2.7\",\n      \"source\": \"docs/decision_log.md:7071-7074\",\n      \"verbatim\": \"7. The 32-valid/6-invalid same-epoch inventory is a backfill CANDIDATE, not a ratified classification: identities may seed the backfill, but dispositions require raw-physics + hash verification before issuance, and any unresolved member blocks issuance.\",\n      \"verification_plan\": \"For all 38 members: verify manifest and evidence hashes, verify raw/event hashes, replay causal clock-anchor derivation and the strict 59-pulse detector, verify the six-field epoch, then compare with candidate labeling. Result: 32 VERIFIED-VALID, 6 VERIFIED-INVALID, zero raw-physics unresolved; two final ledger dispositions remain ambiguous.\"\n    },\n    {\n      \"clause\": \"D-109 R2.8\",\n      \"source\": \"docs/decision_log.md:7075-7079\",\n      \"verbatim\": \"8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38 TOTAL authenticated, content-distinct, VALID same-epoch observations — including previously blind observations once unblinded — not 38 post-cutoff observations. Under the candidate inventory, six further valid observations trigger re-derivation.\",\n      \"verification_plan\": \"Count content-distinct ledger observations whose disposition is exactly valid and whose epoch equals d079_epoch. The implementation does this at joulewise/calibration_bracketing.py:901-908. Result is six further only under the candidate-tool 32-valid disposition proposal; it is eight further under the production writer's systematic-screen mapping.\"\n    }\n  ],\n  \"inventory\": {\n    \"where_it_lives\": {\n      \"count_only_authority\": [\n        \"docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:296-308\",\n        \"configs/calibration/calibration_acceptance_d079_v2.json:225-233\"\n      ],\n      \"candidate_emitter\": \"scripts/calibration_ledger_backfill.py:42-117\",\n      \"concrete_membership\": \"Implicit in the 53 exact-epoch validation custody trees under runs*/instrument_validation; no standalone serialized 38-row candidate file exists in the checkout or .desk.\",\n      \"raw_archive\": \"/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup\",\n      \"important_non_inventory\": \"docs/process_traces/2026-08-03-d111-backfill/MANIFEST.md is a manifest of 41 process artifacts, not the 38 calibration observations.\"\n    },\n    \"identity_method\": \"sha256(canonical_json({\\\"instrument_evidence.json\\\": sha256(evidence bytes), \\\"manifest.json\\\": sha256(manifest bytes)}))\",\n    \"identity_method_source\": \"joulewise/calibration_ledger.py:94-105,120-134\",\n    \"checkout_copy_count\": 53,\n    \"content_distinct_count\": 38,\n    \"candidate_label_counts\": {\n      \"valid\": 32,\n      \"invalid\": 6\n    },\n    \"analysis_only_member_set_sha256\": {\n      \"value\": \"7c0ae751e3be9d180c932b14da1cc9b50f85a73a0821de03c7a7911728a25e95\",\n      \"definition\": \"canonical SHA-256 of the ordered 38 candidate rows containing attempt_id, content_id, all artifact hashes, epoch, full T1, capture lexeme and bound lexeme; custody locator deliberately excluded. This digest is verification evidence, not a contract-defined production identity.\"\n    }\n  },\n  \"epoch\": {\n    \"epoch_id\": \"d079_epoch\",\n    \"all_38_match\": true,\n    \"fields\": {\n      \"os_build\": \"25F84\",\n      \"hardware_model\": \"Mac15,9\",\n      \"power_policy\": \"ac_high_power\",\n      \"sampling_interval_ms\": 100,\n      \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n      \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n    },\n    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:20-26,193-200\"\n  },\n  \"per_member\": [\n    {\n      \"n\": 1,\n      \"attempt_id\": \"20260722T145535-e941c821\",\n      \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n      \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n      \"evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\",\n      \"raw_sha256\": \"b55f3471c70c54e0174b09e67486759fc532742e9bd671e53ce8324fe23209ef\",\n      \"events_sha256\": \"605e2330d27f874621edb698c233542d7eb31fb8b8d1def044852a77a223b1bc\",\n      \"bound_s\": \"0.03018980442653224\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 2,\n      \"attempt_id\": \"20260722T194118-9dc0749d\",\n      \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n      \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n      \"evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\",\n      \"raw_sha256\": \"aa36a9c1e8451e2a0de875a7ff45232c98bf0cce5cdcd5b827d176ea24aa85f7\",\n      \"events_sha256\": \"0f543eb7f697d442a5c0ddce1fe6f3f69c268c96bdc7a5ffbb6e84f70e8f1d66\",\n      \"bound_s\": \"0.026300679324099796\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 3,\n      \"attempt_id\": \"20260722T213749-563b9849\",\n      \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n      \"manifest_sha256\": \"b7dd23cf8a9e30d81a01ba0b3c5c5e0c21b4c325e48e1d02e046fb61b77cb0ac\",\n      \"evidence_sha256\": \"1cc789e9558667e188f1859ba591a584a73eb4d2309612c924eebfb4cf5ffe80\",\n      \"raw_sha256\": \"3684b27080f6b4254d61e1c5b3f0f25e8401257078145331ef2122b2c1893fd1\",\n      \"events_sha256\": \"b179d606c17148e754bba07bb61c3d7a5c094e5a0e701251e7674b45472f5a4b\",\n      \"bound_s\": \"0.2079182387602739\",\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 4,\n      \"attempt_id\": \"20260722T214220-1acdbbc0\",\n      \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n      \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n      \"evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\",\n      \"raw_sha256\": \"7a4b62258d4d6afe251c4ed60a02835ac4d2b743f926260b2f621cb2301a72de\",\n      \"events_sha256\": \"6f0c813bf5489f1fce820bddd1160d6936ec5dc6e89f1c3ca2aecdbedc2834af\",\n      \"bound_s\": \"0.03312014638436772\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 5,\n      \"attempt_id\": \"20260722T215127-eeef661a\",\n      \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n      \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n      \"evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\",\n      \"raw_sha256\": \"8e275c342b5dde493e24e69f5a30fd7224ec36c21b324bd489508cda5860bff8\",\n      \"events_sha256\": \"30efea52cd15580aa4f4f52b959a4b6a881db0df0f72a488ae4d4493d51a8f75\",\n      \"bound_s\": \"0.022741007370546462\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 6,\n      \"attempt_id\": \"20260722T222332-901c5c13\",\n      \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n      \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n      \"evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\",\n      \"raw_sha256\": \"84adafc6e55a45a10e56d5cea6571f1b12dae15656a2a0274822eb96500f4744\",\n      \"events_sha256\": \"1b7ce059e4b72885a77cb398704590e50e51b925cdae7bf77db1ad2b36dd7d59\",\n      \"bound_s\": \"0.03355875667989999\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 7,\n      \"attempt_id\": \"20260722T232509-82642517\",\n      \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n      \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n      \"evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\",\n      \"raw_sha256\": \"56555a10ee248cb6e5692280881d3daaf406b0432c2c3d068e06c5b8d8d76e40\",\n      \"events_sha256\": \"1c2b84546ed000dbb6f3378f5a1ef24ae008048209bcffee95644bbad585df6b\",\n      \"bound_s\": \"0.027654085293084385\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 8,\n      \"attempt_id\": \"20260723T023058-8732d1c9\",\n      \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n      \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n      \"evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\",\n      \"raw_sha256\": \"49d0b16529d40d6ce7a8d125f9787ab37e46ddfeb6b06e1b69a28e1a7011cf67\",\n      \"events_sha256\": \"962780bf83e89c2e5a4720e074e49f06c0aa49cac3989bed9035436ed734455a\",\n      \"bound_s\": \"0.024753340330112727\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 9,\n      \"attempt_id\": \"20260723T052051-d9358c8a\",\n      \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n      \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n      \"evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\",\n      \"raw_sha256\": \"dac05b535d4faa2f8864a2be91a6c56df812b1631fd60aaebde8e680a6aebc8e\",\n      \"events_sha256\": \"7e79ef10b6d9caae132b04ae1e59d584c569aa751084fa02e62e2cad5f794fd3\",\n      \"bound_s\": \"0.025964638697819786\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 10,\n      \"attempt_id\": \"20260723T183306-4ce692b4\",\n      \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n      \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n      \"evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\",\n      \"raw_sha256\": \"bcd97c9bd9b0a0686fc84bfa9d117685b6a68f8beed7f84dfa503eacaf78d941\",\n      \"events_sha256\": \"7341d55729c2a3ebf68739900105893b5f2d59bb55d57092ef20e2b94d6c95ca\",\n      \"bound_s\": \"0.027262160888545217\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 11,\n      \"attempt_id\": \"20260723T194632-d04e038e\",\n      \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n      \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n      \"evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\",\n      \"raw_sha256\": \"b1660d10fcc5015f0ccc0e4e0a7464db3a5220d415c952f3d9635e512faab57c\",\n      \"events_sha256\": \"a965e301af8f2cb662dca60a7b9706d9b6e7dbabdc6971abd3119c46fc7711d6\",\n      \"bound_s\": \"0.024593263907495888\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 12,\n      \"attempt_id\": \"20260723T195730-bc4ba14a\",\n      \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n      \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n      \"evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\",\n      \"raw_sha256\": \"81669d5e0e81ccb1d05ae7d19befffbf41441a92a1e14f0dcb8c0b8d9b6f7a86\",\n      \"events_sha256\": \"0343c61d357465919f99b13000e39f02b43575c68c5383e1f03ffc46a3a2ee24\",\n      \"bound_s\": \"0.025305226022515448\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 13,\n      \"attempt_id\": \"20260723T221449-e9ae755e\",\n      \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n      \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n      \"evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\",\n      \"raw_sha256\": \"4e971efc4abef1f51a636a095fa807d1b395ed8342f5e7386aead5e9c466ce50\",\n      \"events_sha256\": \"1caf0be478a75308070e0a93818618af2dd8ca69f51bd2e35f1994c5b7f9b2d0\",\n      \"bound_s\": \"0.027702588281732055\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 14,\n      \"attempt_id\": \"20260723T223406-314f6d9e\",\n      \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n      \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n      \"evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\",\n      \"raw_sha256\": \"2c92bf2a3065493b00caf678a5ee8d78c93d3dba406979cb824058b355274f73\",\n      \"events_sha256\": \"4a4a990161e35f05d9fbd36c1eb52f78c46551145348036e073aa2494519df29\",\n      \"bound_s\": \"0.026173651901677253\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 15,\n      \"attempt_id\": \"20260724T014109-57844352\",\n      \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n      \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n      \"evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\",\n      \"raw_sha256\": \"9c806bcd26a0f6cce7f33c00d930d803e39f9bd4a6e186971d6123a470a1b13d\",\n      \"events_sha256\": \"221c42b7f214515f9af84c2b9486315df70e3466c66b7beb5bf35e476bf5ae14\",\n      \"bound_s\": \"0.02547564583006129\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 16,\n      \"attempt_id\": \"20260725T005132-a64711b7\",\n      \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n      \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n      \"evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\",\n      \"raw_sha256\": \"a22005ea981f8e3ac1f3ea65cfa6bd1d0777dc009203b5e2db73cce44d2aca4e\",\n      \"events_sha256\": \"459dc8a3ec34eb7a3f2095d0c5b72e931f8d87199fd48812386684f36162f617\",\n      \"bound_s\": \"0.023241581438247116\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 17,\n      \"attempt_id\": \"20260725T011533-0b5ec77c\",\n      \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n      \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n      \"evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\",\n      \"raw_sha256\": \"9934c97547e2cd77de640754c2c51399a66bc96a265f31d38616677ab9973c3d\",\n      \"events_sha256\": \"c15516d15ae525051012e8655817625d37803dda2b8473917720cc5a29ef3043\",\n      \"bound_s\": \"0.028891617940876635\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 18,\n      \"attempt_id\": \"20260725T022712-0a9534f5\",\n      \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n      \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n      \"evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\",\n      \"raw_sha256\": \"bb99b0b7086ee939a8fb789253e2c0502de27a05d056c78d46dc30fccfb862cf\",\n      \"events_sha256\": \"a42487bd9202c043485eebc42a68f505b35faf158c8640f1393d287a1d36e0d1\",\n      \"bound_s\": \"0.029197264796726408\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 19,\n      \"attempt_id\": \"20260725T030533-d3f076e5\",\n      \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n      \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n      \"evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\",\n      \"raw_sha256\": \"26b9ad5ba13e2c73e78ddfdf5be6a2b1cf4b8eb31881aad575ac1bb7ae0dabb9\",\n      \"events_sha256\": \"180a700366e1a97a9e8649a6d98bbd2d814fe9d5fed7246f99b47aa1af5e6b84\",\n      \"bound_s\": \"0.024879191521227362\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 20,\n      \"attempt_id\": \"20260725T055825-b10cb348\",\n      \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n      \"manifest_sha256\": \"eebf3524d9e0b41c022c5e57d4b16787e98302e0d7c28381036415117fafb3ba\",\n      \"evidence_sha256\": \"e0d525e0923f88572f7530f447a3bc8e889ef80a47d662840b86c40b4a35f285\",\n      \"raw_sha256\": \"ed13e60dcfe12d7ce3900798dfbafb7936baa3700cdf58d0f6c1d0fc1790a4b8\",\n      \"events_sha256\": \"fbb3d05c9185ed416d9c138fc63dc32d56b1cd465059007962f9273b53dce671\",\n      \"bound_s\": null,\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: wall_minus_monotonic_span_exceeded\"\n    },\n    {\n      \"n\": 21,\n      \"attempt_id\": \"20260725T060617-97c5cba6\",\n      \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n      \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n      \"evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\",\n      \"raw_sha256\": \"85583f5f07299f38f4f912581e2cfc03453d3a0e85a0de486b3406a355b2c9f2\",\n      \"events_sha256\": \"c904c5f1a1c6557117b6fbde70dc8358dca773f94fc0c611cd50e92c3a3e2ffa\",\n      \"bound_s\": \"0.025045994537554683\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 22,\n      \"attempt_id\": \"20260726T000039-491995f3\",\n      \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n      \"manifest_sha256\": \"b5e1d1195eb8c52bb41211b464909723754e5753bb866ced6f5715d83769ef65\",\n      \"evidence_sha256\": \"9584cd7cdc44e5ba4d176475ce2bf6f70d04e163778fd6e9d5e46cec02303c00\",\n      \"raw_sha256\": \"b916d0b8fc79e8fc7b261c6d608307fbae94bd3c89189e2256cafcf483378c2d\",\n      \"events_sha256\": \"579c2adf45f245dbf31e69b83617fceaf28e63be70677fe0dcd8104a82c79248\",\n      \"bound_s\": \"0.035435840879704805\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer and D-102\"\n    },\n    {\n      \"n\": 23,\n      \"attempt_id\": \"20260726T031222-e0ce33f5\",\n      \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n      \"manifest_sha256\": \"5ec9e27a9bdef89d8e83ca2fd2ee0c1c2d8d2effd56139ac904d1b032c3fc378\",\n      \"evidence_sha256\": \"8d0b2d48460c71d35b2b3b7124b3168c86a497b5a674348451ea5d73931adab3\",\n      \"raw_sha256\": \"c5674ce16dba60b5f0f61ffa5dbe6d7c38bc11747f627e120f6b96af7b9f2fe1\",\n      \"events_sha256\": \"7ba5009ade8a7a870fcb119297dc34a54dcd78f54d13d463e2b4de721db7100b\",\n      \"bound_s\": \"0.023854405254729094\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 24,\n      \"attempt_id\": \"20260726T225227-1f550773\",\n      \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n      \"manifest_sha256\": \"5837bd2c5be6769d63faa57a5d59311241038be7f92de6101b61566b54d89131\",\n      \"evidence_sha256\": \"95941785a8fca5b74019da42d18d280abda639f92442ad57195b852ca567b564\",\n      \"raw_sha256\": \"db6416cada6ea8c0bc84109903fc734d71c0f5a4d8451bafa05a05a76dd7b89d\",\n      \"events_sha256\": \"2de1638cb73fa1a23105a81fe9cdcf9774f467adfcf6fa59bd29029c15a1a9cf\",\n      \"bound_s\": \"0.04916527633725107\",\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 25,\n      \"attempt_id\": \"20260726T225920-ab4272f5\",\n      \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n      \"manifest_sha256\": \"1696f470f0cc543a62cc40a819068a4b7b9f62058fd8d0dd1707870dd25b59e5\",\n      \"evidence_sha256\": \"5b1c9dce56202e1d8af74e71b37aaa1538f0e53fcdded1e05c61cff90f41cda5\",\n      \"raw_sha256\": \"4f83a36625a199a1e5e552953afbdc004bd5144756c8aa2bf657c8c714b4453f\",\n      \"events_sha256\": \"dc704274c1c608a3a87387575c7a36e868c988f9737b033775f55d12791f80f5\",\n      \"bound_s\": \"0.028145704403191807\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 26,\n      \"attempt_id\": \"20260727T015824-45feb516\",\n      \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n      \"manifest_sha256\": \"a7ac96e151419313594510f7511071cbdd710a1ab0837fef25a792ccc1b38d48\",\n      \"evidence_sha256\": \"96f2af22ae5b18ba70f08ec2ed40c54abe0934508ae0d7cfb8fadb9de19432d8\",\n      \"raw_sha256\": \"d0f8ab38ade1df00d957597f6ae0bfdffce047d8611416ecb434f91c4e35ae47\",\n      \"events_sha256\": \"c75224662805694c090f458e6462f8a69581e39e7cf9a4f03d1c3d3b2ae7a371\",\n      \"bound_s\": \"0.029425288011457773\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 27,\n      \"attempt_id\": \"20260727T020611-4a409a30\",\n      \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n      \"manifest_sha256\": \"dc30e9df75b0e4bc561c6f9d641ed3dff696697508333de6707d354151bd96ec\",\n      \"evidence_sha256\": \"e3f4df9cf8bf4f1edfacbd10072bd53c5c1b59a873e4c25ee1727d74307ab3f8\",\n      \"raw_sha256\": \"0961bf040013bf35d7d9fd2e5ad4b9d212d0dab9d733357c5193569ba7b92acd\",\n      \"events_sha256\": \"bea8ab60b84b2ff7e00eff035c1187c837f26fdc30b91bfd0d4ca8ee6d15ecab\",\n      \"bound_s\": \"0.029339001207750293\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 28,\n      \"attempt_id\": \"20260727T050047-95e2f87e\",\n      \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n      \"manifest_sha256\": \"d572e55594e97a4d4f3fb82295c8ad7aedac68c15c18e7615f3ac13e91ebea8a\",\n      \"evidence_sha256\": \"2d70134135398b613638ae6ec62607913026c7d0cdfa9da1dfc77c657fa0e091\",\n      \"raw_sha256\": \"b439d5bc06855943055795db69117ab612866d397eef219d73e0a576545b06c5\",\n      \"events_sha256\": \"a90f500e118b1e88041167fb9fb3808ae0e27b83fa5b664f63c98adecf1ae7a1\",\n      \"bound_s\": \"0.028854562420070173\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 29,\n      \"attempt_id\": \"20260729T204105-39d25f8a\",\n      \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n      \"manifest_sha256\": \"3aec4fc319e1de5a3b34d3552774ee4cf59ad9b1134001c8176d538f1304871f\",\n      \"evidence_sha256\": \"4323c8c5242812b95e544213367dd75f0bc927605d73c78c1a491a84dd829026\",\n      \"raw_sha256\": \"4f0cd62a013d6cc639e11637e425b8e09af02703828d4d0e9638a30ef70e88fc\",\n      \"events_sha256\": \"0ef0f3e5779fb6b1aec6bb48fb60a76c175106b192f16f8aeaf95e3961b75c59\",\n      \"bound_s\": \"0.031467745880268516\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 30,\n      \"attempt_id\": \"20260730T014035-124df355\",\n      \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n      \"manifest_sha256\": \"bb894782e7dd95d38576514fe9360335552129d6de116e2a05a82c17a70702f5\",\n      \"evidence_sha256\": \"f8946df7f5495d6e5c64f90490b94ca2eab94f10ed16b7298e5741dadbe182b1\",\n      \"raw_sha256\": \"95d50522d5eef61dbf2b9b815dce3f62e8791fe417942883908dde762351332b\",\n      \"events_sha256\": \"d66899983a1d8e7b4bc7ecb11c5740534e101f4fbdd2810dd41ff00910277379\",\n      \"bound_s\": \"0.027788174032371493\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 31,\n      \"attempt_id\": \"20260730T210703-f76b5771\",\n      \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n      \"manifest_sha256\": \"e40353dfd883d773414378893f27bc617cfa972f62793b0f35cc9efa30ed7d44\",\n      \"evidence_sha256\": \"0f5e3ea38ff0f833840895e065941494c71c4cd9bf0fe222a9e08ca24ddc3ed8\",\n      \"raw_sha256\": \"718b9046d134fc2a9f089818ea2e5c3aac05c10f056f942c8702ec3b4cdabf75\",\n      \"events_sha256\": \"aaf29ec68222439453b790725b6849040c3f7c1cb5accf096d3a722edebf9664\",\n      \"bound_s\": \"0.026131301462788137\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 32,\n      \"attempt_id\": \"20260731T012210-374020b6\",\n      \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n      \"manifest_sha256\": \"f64a179f03a6b3efecaea6e3ad8ff08ba8c354b9f57023f0929781fd2d133545\",\n      \"evidence_sha256\": \"21a6296fc74542a6400ab5562376b9bf969a1d906c8f9076f89dc9916cef1b52\",\n      \"raw_sha256\": \"0f3b509c48e42a9cbcf32ac3a446d9c13d38766328f9569a96d397a685ad2f2d\",\n      \"events_sha256\": \"624b9c26e71648272e36c85fa7884aa258851039a7e77a7be123e1290d2c4b79\",\n      \"bound_s\": \"0.024850427856341006\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 33,\n      \"attempt_id\": \"20260731T161713-b8b08280\",\n      \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n      \"manifest_sha256\": \"e65aed76d770fbcd9c07b6c2dc26335ddf593533ff1ab6a46cb1bc9bdd119d0a\",\n      \"evidence_sha256\": \"2cda4856ae7939067f0a6ebbbdb865871e437e1c652b0dd438e33cb5ffef1583\",\n      \"raw_sha256\": \"464f5f9ca38818544e54061407251ef3d13541c90c8e5c6f05ee54fe8a913068\",\n      \"events_sha256\": \"2bfd2ac5f0ba88e02a89dbc070837ce3bb1161b2d3067a6176e720bb778b4df1\",\n      \"bound_s\": \"0.030972654450356962\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 34,\n      \"attempt_id\": \"20260731T214355-126fc2ab\",\n      \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n      \"manifest_sha256\": \"ad3aa2345df71df05fb5913ef52210443eb07cfbbb5824e48794b6892557848d\",\n      \"evidence_sha256\": \"1958d58c35dfa30c18671abafcddf3d43c9328f586ce2051d1fb83ab99b51d5f\",\n      \"raw_sha256\": \"c14ef61161fc9bf463840d5f62e1cdcd9bc2fe586297e5d89a6334e19f8dd21f\",\n      \"events_sha256\": \"89808fe44225b7870585a1f2883ff43b01ec0b02507775900ada0a60251f145c\",\n      \"bound_s\": null,\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 35,\n      \"attempt_id\": \"20260801T010113-e859f3aa\",\n      \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n      \"manifest_sha256\": \"52aa9e9b4485a352d1ba2bd40e500f71cab989967d1db6e7a130fe9c157e0647\",\n      \"evidence_sha256\": \"6c350a69406f92f4f1d68e30684f6b36b2f233fba5f52070a73f23c3d767fd45\",\n      \"raw_sha256\": \"1302b53b6aeab97ee57b35cda8003ffb6d107265979614880910c24fdbbb5e7c\",\n      \"events_sha256\": \"887ea9f6bc663ac5bc8cfe1c6d898262a2089602406186f83ff0f750983a841b\",\n      \"bound_s\": \"0.41198917978147415\",\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 36,\n      \"attempt_id\": \"20260801T010805-ff3fdc88\",\n      \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n      \"manifest_sha256\": \"fd5906ccd884670c9d40a57e7b8b4755357bc91c89f281449a080fe5c2007402\",\n      \"evidence_sha256\": \"62967d66a74467735011f159a523f50b6409287bf96899446e4a02fa2c8e2eed\",\n      \"raw_sha256\": \"c39bc0c6c55a3deabdffdf8bfdad95e061fb464def586edafdc19dbd1d8ea5c2\",\n      \"events_sha256\": \"10e9035731a2d54a9469c66318568b6f2e91a0ac3fecdbfad94dfb62c22bf0fc\",\n      \"bound_s\": null,\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 37,\n      \"attempt_id\": \"20260801T014059-8c3bfe9e\",\n      \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n      \"manifest_sha256\": \"7d2967b125324c65e0d57a16950a0e1c2e2946464b7eb89667e8fc2410550149\",\n      \"evidence_sha256\": \"c1653f369e05e9186d0c6d06231993575ee23c1fd813b96f1094d74dfbaac0ad\",\n      \"raw_sha256\": \"f1a9350cbfdb0ec4c0a909b5d2b77798e16f754132499602b426a1068274465f\",\n      \"events_sha256\": \"33f78ee6e299643d8f5929fc2e339f3e13959eb6983a7db8b8af4bd936a0700d\",\n      \"bound_s\": \"0.032786870825707914\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 38,\n      \"attempt_id\": \"20260801T064830-c76f5d1c\",\n      \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n      \"manifest_sha256\": \"6127f706081c4686164ecca83032ab86bdc467170d55b24e537255cfdacac4dc\",\n      \"evidence_sha256\": \"4c2752a194dbd1fc39aaf82e11071cccab4283c81f46208657bd849af6c23a06\",\n      \"raw_sha256\": \"dab52b86df50235d78c39ddda87b3f4620b6dfdead9050640184204630cd5b1f\",\n      \"events_sha256\": \"31e245dcaf050740a69f52ab3afa1783e2081e43a089dc57045be6039f7503e6\",\n      \"bound_s\": \"0.0350400833260715\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer\"\n    }\n  ],\n  \"raw_physics_method\": {\n    \"valid_members\": \"Used verify_stored_evidence_physics, which rejects stored-status substitution, re-derives the causal anchor, reconstructs all pulse commands from events.jsonl, re-fits all 59 pulses, requires complete detection/no spurious plateaus/no reasons, checks every stored residual enclosure contains the refit, and returns max(stored,fresh) bound.\",\n    \"valid_method_source\": \"joulewise/powermetrics_fiducial.py:1088-1164; docs/contracts/powermetrics_fiducial.md:183-211\",\n    \"invalid_members\": \"Re-derived the causal anchor directly from native powermetrics records and recorded ClockStamps. All six independently returned unknown; an unresolved own anchor is forced invalid under the contract.\",\n    \"hash_evidence\": \"Each selected custody manifest's lines 3-6 bind events, instrument evidence, power trace and raw plist. Every listed digest matched the bytes.\"\n  },\n  \"bootstrap_computation\": {\n    \"authoritative_result\": \"NOT COMPUTABLE WITHOUT RULING/IMPORT CONTRACT\",\n    \"required_prior_observation_set\": \"The exact 38 content IDs in per_member, each with epoch_id=d079_epoch and the final ruled disposition. No additional fixture-known-holdout row is evidenced by a real content bundle; configs/calibration/calibration_acceptance_d079_v2.json:222 is explicitly fixture data.\",\n    \"receipt_algorithm_from_schema\": [\n      \"receipt_core is canonical JSON with sorted keys, separators ',' and ':', UTF-8, allow_nan=false; receipt_digest=sha256(receipt_core). See joulewise/calibration_ledger.py:94-105,155-160.\",\n      \"Each receipt contains sequence, predecessor_digest, event, attempt_id, content_id, artifact hashes, six-field epoch, full T1, capture lexeme, exact bound lexeme, disposition and custody locator. See joulewise/calibration_ledger.py:590-622.\",\n      \"The parser requires a reservation before each finalization. See joulewise/calibration_ledger.py:409-465 and finalize_attempt_receipt at :716-777.\",\n      \"The head pin is the final receipt's sequence and receipt_digest with ledger_schema. See joulewise/calibration_ledger.py:780-789.\"\n    ],\n    \"conditional_non_authoritative_replays\": [\n      {\n        \"assumptions\": \"Attempt IDs sorted ascending; one synthetic reservation immediately followed by one finalization per content ID; first hash-complete custody copy selected; candidate-tool mapping of all stored-valid rows to valid and stored-invalid rows to ordinary-invalid.\",\n        \"sequence\": 76,\n        \"head_digest\": \"cb410907660ed8a120d4e1d04a7e9af489b69d83686a8bf7658b3f73e7e3335a\",\n        \"prior_observation_rows_sha256\": \"d29404feea08496453538d8b3994af1c4b64c12a86b950a3aa96a604cb6690c6\",\n        \"dispositions\": {\n          \"valid\": 32,\n          \"ordinary-invalid\": 6\n        },\n        \"warning\": \"Illustrative only; the assumptions are not authorized by D-109 or an import schema.\"\n      },\n      {\n        \"assumptions\": \"Same ordering/custody rules, but apply the production writer's preflight-screen mapping to members 22 and 38.\",\n        \"sequence\": 76,\n        \"head_digest\": \"8e80b6e93804df098f9fbec66740757073d235019e19990c7a9d8270b28337f1\",\n        \"prior_observation_rows_sha256\": \"f28ddf8e0995230857c7e7db11c031084e18e8919ea1b9b373ae2112a9a936bf\",\n        \"dispositions\": {\n          \"valid\": 30,\n          \"systematic-invalid\": 2,\n          \"ordinary-invalid\": 6\n        },\n        \"warning\": \"Illustrative only; differs from D-109 R2.8's stated six-further consequence.\"\n      }\n    ],\n    \"additional_implementation_gap\": \"append_pending_receipt requires the current physical ledger head to equal the committed pin before each new reservation (joulewise/calibration_ledger.py:673-690). Once one reservation/finalization pair advances the physical ledger, another reservation cannot be appended under the unchanged genesis pin. A batch bootstrap/import route is therefore required; none exists.\"\n  },\n  \"derivation_corpus\": {\n    \"n\": 19,\n    \"unchanged\": true,\n    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:46-183\",\n    \"artifact_file_sha256\": \"9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb\",\n    \"stored_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n    \"computed_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n    \"match\": true,\n    \"reconstructed_statistics\": {\n      \"minimum_s\": \"0.022741007370546462\",\n      \"minimum_member\": \"20260722T215127-eeef661a\",\n      \"maximum_s\": \"0.03355875667989999\",\n      \"maximum_member\": \"20260722T222332-901c5c13\",\n      \"range_s\": \"0.010817749309353528\",\n      \"mean_s\": \"0.026950033977532761\",\n      \"sample_sd_s\": \"0.002970761365307205\"\n    },\n    \"note\": \"The current derivation_sha256 covers the complete artifact core excluding the hash field, not only the n=19 table (joulewise/calibration_bracketing.py:155-177). Issuance edits will therefore require a new canonical hash even though the threshold-producing n=19 remains unchanged.\"\n  },\n  \"D102_corpus_doubling\": {\n    \"binding_rule\": \"38 total authenticated, content-distinct, valid same-epoch observations\",\n    \"implementation_source\": \"joulewise/calibration_bracketing.py:901-908\",\n    \"candidate_tool_disposition_result\": {\n      \"current_valid_total\": 32,\n      \"additional_valid_needed\": 6,\n      \"trigger_now\": false,\n      \"matches_D109_R2_8\": true\n    },\n    \"production_writer_disposition_result\": {\n      \"current_valid_total\": 30,\n      \"additional_valid_needed\": 8,\n      \"trigger_now\": false,\n      \"matches_D109_R2_8\": false\n    },\n    \"decision\": \"BLOCKED pending the B1 disposition ruling. The report does not choose between these counts.\"\n  },\n  \"verification\": [\n    {\n      \"id\": \"V1\",\n      \"result\": \"PASS\",\n      \"check\": \"Enumerated runs*/instrument_validation manifests, exact six-field epoch filtered, canonical content IDs recomputed.\",\n      \"observed\": \"53 checkout custody copies; 38 distinct IDs; stored labels 32 valid/6 invalid.\"\n    },\n    {\n      \"id\": \"V2\",\n      \"result\": \"PASS\",\n      \"check\": \"For every selected representative, rehashed every manifest-listed artifact and every evidence-internal artifact hash.\",\n      \"observed\": \"Zero missing or mismatched bytes.\"\n    },\n    {\n      \"id\": \"V3\",\n      \"result\": \"PASS\",\n      \"check\": \"Replayed strict raw physics for every candidate-valid observation and causal-anchor physics for every candidate-invalid observation.\",\n      \"observed\": \"32 VERIFIED-VALID; 6 VERIFIED-INVALID; 0 raw unresolved.\"\n    },\n    {\n      \"id\": \"V4\",\n      \"result\": \"PASS\",\n      \"check\": \"PYTHONDONTWRITEBYTECODE=1 python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact configs/calibration/calibration_acceptance_d079_v2.json\",\n      \"observed\": \"PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK; n=19 statistics reproduced.\"\n    },\n    {\n      \"id\": \"V5\",\n      \"result\": \"PASS\",\n      \"check\": \"Canonical artifact-core SHA-256 recomputation.\",\n      \"observed\": \"stored=computed=3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d.\"\n    },\n    {\n      \"id\": \"V6\",\n      \"result\": \"PASS\",\n      \"check\": \"Final git status.\",\n      \"observed\": \"## main...origin/main; no changes.\"\n    }\n  ],\n  \"flags\": [\n    {\n      \"id\": \"NO_EDITS\",\n      \"level\": \"informational\",\n      \"text\": \"Read-only verification; no artifact, ledger, pin, report or state file was created or modified.\"\n    },\n    {\n      \"id\": \"ISSUANCE_BLOCKED\",\n      \"level\": \"blocking\",\n      \"text\": \"Lead must first rule the two high-bound dispositions and authorize a deterministic historical-import/bootstrap contract, including ordering and custody selection. Only then can one exact prior_observation_set, sequence and head digest be issued.\"\n    }\n  ],\n  \"next_exact_step\": \"Lead rules whether members 20260726T000039-491995f3 and 20260801T064830-c76f5d1c are ledger-valid or systematic-invalid, then specifies the authenticated batch-import ordering/custody rule. Recompute the single resulting 76-receipt chain, review its exact head, and only in a separately authorized write session bootstrap the ledger, update and commit the head pin, and issue the acceptance artifact.\"\n}\n```","numLines":730,"startLine":1,"totalLines":730}},"sourceToolAssistantUUID":"95303f9d-7523-4544-89e9-e0e2c5aa3014","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
7883:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-mtp-energy.md:1265:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7886:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-tokenizer-honesty.md:1281:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7889:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-energy-nutrition-label.md:1679:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7892:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-spec-decode-energy.md:2047:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7895:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:1433:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7898:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:5392:docs/process_traces/2026-08-06-d079-issuance-coldgate/FABLE-COLD-PROCEED.jsonl:14:{"parentUuid":"95303f9d-7523-4544-89e9-e0e2c5aa3014","isSidechain":true,"promptId":"5c9e22f4-f072-4d90-ba34-2746cfa6a676","agentId":"ad24a0f43262b600c","type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_018LjASorgBFpMjfaTz9pbY8","type":"tool_result","content":"1\t```json\n2\t{\n3\t  \"schema\": \"claude-codex-report/v1\",\n4\t  \"genre\": \"verification\",\n5\t  \"status\": \"findings\",\n6\t  \"completion\": \"complete\",\n7\t  \"summary\": \"BLOCKED. All 38 content-distinct candidates were recovered, hash-authenticated, epoch-checked, and replayed from raw physics: 32 VERIFIED-VALID and 6 VERIFIED-INVALID, with no missing raw evidence. Issuance is not ready because two verified-valid observations exceed the systematic-failure screen and therefore lack an unambiguous ledger disposition, and the repository does not specify a deterministic authenticated historical-import/bootstrap transaction from which one authoritative sequence/head digest can be computed.\",\n8\t  \"workspace\": {\n9\t    \"head_start\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n10\t    \"head_end\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n11\t    \"branch\": \"main\",\n12\t    \"pathspec\": [],\n13\t    \"unowned_dirty\": [],\n14\t    \"write_scope\": \"none\",\n15\t    \"edits\": \"none\"\n16\t  },\n17\t  \"verdict\": {\n18\t    \"overall\": \"BLOCKED\",\n19\t    \"prompt_vs_R2_divergence\": false,\n20\t    \"raw_member_results\": {\n21\t      \"VERIFIED-VALID\": 32,\n22\t      \"VERIFIED-INVALID\": 6,\n23\t      \"UNRESOLVED\": 0\n24\t    },\n25\t    \"blocking_items\": [\n26\t      {\n27\t        \"id\": \"B1\",\n28\t        \"type\": \"ledger_disposition_ruling\",\n29\t        \"members\": [\n30\t          \"20260726T000039-491995f3\",\n31\t          \"20260801T064830-c76f5d1c\"\n32\t        ],\n33\t        \"reason\": \"Both replay as physically valid, matching the candidate inventory, but their bounds 0.035435840879704805 and 0.0350400833260715 exceed the ratified 0.033558756679900 preflight screen. The production writer maps such a valid capture to systematic-invalid at scripts/validate_powermetrics_fiducial.py:664-671; D-102 explicitly calls the first member a systematic failure at docs/decision_log.md:6298-6301. The backfill candidate tool instead proposes valid solely from stored status at scripts/calibration_ledger_backfill.py:58-63. Selecting either disposition is lead-owned.\"\n34\t      },\n35\t      {\n36\t        \"id\": \"B2\",\n37\t        \"type\": \"bootstrap_contract_gap\",\n38\t        \"members\": \"all 38\",\n39\t        \"reason\": \"No historical-import/bootstrap API, receipt ordering, duplicate-custody selection rule, or import-transaction schema exists. The candidate tool emits only an unauthoritative candidate set and never appends the ledger (scripts/calibration_ledger_backfill.py:2-7,90-117). Because receipt digests bind sequence, predecessor, disposition, artifact hashes and absolute custody locator (joulewise/calibration_ledger.py:590-622), more than one valid head digest is possible.\"\n40\t      }\n41\t    ]\n42\t  },\n43\t  \"binding_clauses\": [\n44\t    {\n45\t      \"clause\": \"D-109 R1.4\",\n46\t      \"source\": \"docs/decision_log.md:7027-7039\",\n47\t      \"verbatim\": \"4. The acceptance artifact pins its baseline ledger head. Evaluation ALSO requires the independent current-head pin (clause below), verifies one complete non-forked chain extension from baseline to current, and threads ONE immutable ledger snapshot through every consumer path (session, direct runner path, secondary verifier) — repeated independent loads are a refusal-grade defect. Anti-rollback authority: a REPO-COMMITTED head-pin file `{sequence, head_digest, ledger_schema}` (existing checked-in byte-pin trust model; no second trusted latest-sequence store). Rotation is epoch-bounded — at most one lead-controlled quiet-machine collection session — and NO claim evaluation may occur between ledger advancement and pin commit; a physical head differing from the committed pin refuses.\",\n48\t      \"verification_plan\": \"After an authorized bootstrap, recompute every receipt digest, require one linear chain, require the artifact cutoff to equal an exact receipt, require the physical head to equal the separately committed pin, and trace one snapshot object through every consumer. This session verified the implemented digest/head machinery but could not select an authoritative bootstrap head because no import transaction is specified.\"\n49\t    },\n50\t    {\n51\t      \"clause\": \"D-109 R2.1\",\n52\t      \"source\": \"docs/decision_log.md:7053\",\n53\t      \"verbatim\": \"1. The issuance cutoff is an exact ledger sequence + head digest.\",\n54\t      \"verification_plan\": \"Compute the final receipt count and digest only after disposition, ordering and custody-locator rules are fixed. Current fixture cutoff remains non-production genesis sequence 0/all-zero digest at configs/calibration/calibration_acceptance_d079_v2.json:14-18.\"\n55\t    },\n56\t    {\n57\t      \"clause\": \"D-109 R2.2\",\n58\t      \"source\": \"docs/decision_log.md:7054-7055\",\n59\t      \"verbatim\": \"2. `derivation_corpus` remains exactly the n=19 threshold-producing observations.\",\n60\t      \"verification_plan\": \"Re-run the corpus verifier against all 19 pinned member manifest/evidence hashes and recompute the decimal statistics and artifact canonical hash. Result: PASS.\"\n61\t    },\n62\t    {\n63\t      \"clause\": \"D-109 R2.3\",\n64\t      \"source\": \"docs/decision_log.md:7056-7060\",\n65\t      \"verbatim\": \"3. `prior_observation_set` = every content-distinct governed observation known at the cutoff — valid, systematic-invalid, ordinary-invalid, blind holdout, and unresolved — with epoch and disposition recorded separately. (The current artifact's two ID-only `blind_exclusions` are insufficient and are superseded.)\",\n66\t      \"verification_plan\": \"Enumerate every exact-epoch validation tree, collapse copies by canonical content ID, authenticate the raw bytes, and assign one epoch plus one ruled disposition per content ID. The 38 identities are complete for the located candidate, but two dispositions require a ruling.\"\n67\t    },\n68\t    {\n69\t      \"clause\": \"D-109 R2.4\",\n70\t      \"source\": \"docs/decision_log.md:7061-7063\",\n71\t      \"verbatim\": \"4. Content identity is path-independent, derived from canonical primary-byte hashes; attempt identity is separate; copies do not create new observations.\",\n72\t      \"verification_plan\": \"Hash manifest.json and instrument_evidence.json bytes, canonical-JSON encode the two-name hash map, SHA-256 it, and collapse identical IDs. Implementation is joulewise/calibration_ledger.py:94-105,120-134. Result: 53 checkout copies collapse to 38 IDs.\"\n73\t    },\n74\t    {\n75\t      \"clause\": \"D-109 R2.5\",\n76\t      \"source\": \"docs/decision_log.md:7064-7068\",\n77\t      \"verbatim\": \"5. \\\"New\\\" (trigger population) = current authentic content IDs − `prior_observation_set`, regardless of capture timestamp or source root; a previously unknown historical artifact IS new when discovered. Every new observation is judged under the PRIOR artifact (D-102's prospective rule).\",\n78\t      \"verification_plan\": \"After issuance, subtract the exact 38-ID prior set from the authenticated ledger snapshot, independent of path/time, before applying triggers. The implemented subtraction is at joulewise/calibration_bracketing.py:870-893.\"\n79\t    },\n80\t    {\n81\t      \"clause\": \"D-109 R2.6\",\n82\t      \"source\": \"docs/decision_log.md:7069-7070\",\n83\t      \"verbatim\": \"6. New unresolved or unclassifiable attempts cause refusal; only after trigger disposition may a successor artifact absorb them.\",\n84\t      \"verification_plan\": \"Require every post-cutoff receipt to classify as valid, systematic-invalid or ordinary-invalid; unresolved/abandoned/null-content rows must refuse. Implemented refusal is at joulewise/calibration_bracketing.py:895-900.\"\n85\t    },\n86\t    {\n87\t      \"clause\": \"D-109 R2.7\",\n88\t      \"source\": \"docs/decision_log.md:7071-7074\",\n89\t      \"verbatim\": \"7. The 32-valid/6-invalid same-epoch inventory is a backfill CANDIDATE, not a ratified classification: identities may seed the backfill, but dispositions require raw-physics + hash verification before issuance, and any unresolved member blocks issuance.\",\n90\t      \"verification_plan\": \"For all 38 members: verify manifest and evidence hashes, verify raw/event hashes, replay causal clock-anchor derivation and the strict 59-pulse detector, verify the six-field epoch, then compare with candidate labeling. Result: 32 VERIFIED-VALID, 6 VERIFIED-INVALID, zero raw-physics unresolved; two final ledger dispositions remain ambiguous.\"\n91\t    },\n92\t    {\n93\t      \"clause\": \"D-109 R2.8\",\n94\t      \"source\": \"docs/decision_log.md:7075-7079\",\n95\t      \"verbatim\": \"8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38 TOTAL authenticated, content-distinct, VALID same-epoch observations — including previously blind observations once unblinded — not 38 post-cutoff observations. Under the candidate inventory, six further valid observations trigger re-derivation.\",\n96\t      \"verification_plan\": \"Count content-distinct ledger observations whose disposition is exactly valid and whose epoch equals d079_epoch. The implementation does this at joulewise/calibration_bracketing.py:901-908. Result is six further only under the candidate-tool 32-valid disposition proposal; it is eight further under the production writer's systematic-screen mapping.\"\n97\t    }\n98\t  ],\n99\t  \"inventory\": {\n100\t    \"where_it_lives\": {\n101\t      \"count_only_authority\": [\n102\t        \"docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:296-308\",\n103\t        \"configs/calibration/calibration_acceptance_d079_v2.json:225-233\"\n104\t      ],\n105\t      \"candidate_emitter\": \"scripts/calibration_ledger_backfill.py:42-117\",\n106\t      \"concrete_membership\": \"Implicit in the 53 exact-epoch validation custody trees under runs*/instrument_validation; no standalone serialized 38-row candidate file exists in the checkout or .desk.\",\n107\t      \"raw_archive\": \"/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup\",\n108\t      \"important_non_inventory\": \"docs/process_traces/2026-08-03-d111-backfill/MANIFEST.md is a manifest of 41 process artifacts, not the 38 calibration observations.\"\n109\t    },\n110\t    \"identity_method\": \"sha256(canonical_json({\\\"instrument_evidence.json\\\": sha256(evidence bytes), \\\"manifest.json\\\": sha256(manifest bytes)}))\",\n111\t    \"identity_method_source\": \"joulewise/calibration_ledger.py:94-105,120-134\",\n112\t    \"checkout_copy_count\": 53,\n113\t    \"content_distinct_count\": 38,\n114\t    \"candidate_label_counts\": {\n115\t      \"valid\": 32,\n116\t      \"invalid\": 6\n117\t    },\n118\t    \"analysis_only_member_set_sha256\": {\n119\t      \"value\": \"7c0ae751e3be9d180c932b14da1cc9b50f85a73a0821de03c7a7911728a25e95\",\n120\t      \"definition\": \"canonical SHA-256 of the ordered 38 candidate rows containing attempt_id, content_id, all artifact hashes, epoch, full T1, capture lexeme and bound lexeme; custody locator deliberately excluded. This digest is verification evidence, not a contract-defined production identity.\"\n121\t    }\n122\t  },\n123\t  \"epoch\": {\n124\t    \"epoch_id\": \"d079_epoch\",\n125\t    \"all_38_match\": true,\n126\t    \"fields\": {\n127\t      \"os_build\": \"25F84\",\n128\t      \"hardware_model\": \"Mac15,9\",\n129\t      \"power_policy\": \"ac_high_power\",\n130\t      \"sampling_interval_ms\": 100,\n131\t      \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n132\t      \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n133\t    },\n134\t    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:20-26,193-200\"\n135\t  },\n136\t  \"per_member\": [\n137\t    {\n138\t      \"n\": 1,\n139\t      \"attempt_id\": \"20260722T145535-e941c821\",\n140\t      \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n141\t      \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n142\t      \"evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\",\n143\t      \"raw_sha256\": \"b55f3471c70c54e0174b09e67486759fc532742e9bd671e53ce8324fe23209ef\",\n144\t      \"events_sha256\": \"605e2330d27f874621edb698c233542d7eb31fb8b8d1def044852a77a223b1bc\",\n145\t      \"bound_s\": \"0.03018980442653224\",\n146\t      \"verdict\": \"VERIFIED-VALID\",\n147\t      \"disposition\": \"valid\"\n148\t    },\n149\t    {\n150\t      \"n\": 2,\n151\t      \"attempt_id\": \"20260722T194118-9dc0749d\",\n152\t      \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n153\t      \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n154\t      \"evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\",\n155\t      \"raw_sha256\": \"aa36a9c1e8451e2a0de875a7ff45232c98bf0cce5cdcd5b827d176ea24aa85f7\",\n156\t      \"events_sha256\": \"0f543eb7f697d442a5c0ddce1fe6f3f69c268c96bdc7a5ffbb6e84f70e8f1d66\",\n157\t      \"bound_s\": \"0.026300679324099796\",\n158\t      \"verdict\": \"VERIFIED-VALID\",\n159\t      \"disposition\": \"valid\"\n160\t    },\n161\t    {\n162\t      \"n\": 3,\n163\t      \"attempt_id\": \"20260722T213749-563b9849\",\n164\t      \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n165\t      \"manifest_sha256\": \"b7dd23cf8a9e30d81a01ba0b3c5c5e0c21b4c325e48e1d02e046fb61b77cb0ac\",\n166\t      \"evidence_sha256\": \"1cc789e9558667e188f1859ba591a584a73eb4d2309612c924eebfb4cf5ffe80\",\n167\t      \"raw_sha256\": \"3684b27080f6b4254d61e1c5b3f0f25e8401257078145331ef2122b2c1893fd1\",\n168\t      \"events_sha256\": \"b179d606c17148e754bba07bb61c3d7a5c094e5a0e701251e7674b45472f5a4b\",\n169\t      \"bound_s\": \"0.2079182387602739\",\n170\t      \"verdict\": \"VERIFIED-INVALID\",\n171\t      \"disposition\": \"ordinary-invalid\",\n172\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n173\t    },\n174\t    {\n175\t      \"n\": 4,\n176\t      \"attempt_id\": \"20260722T214220-1acdbbc0\",\n177\t      \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n178\t      \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n179\t      \"evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\",\n180\t      \"raw_sha256\": \"7a4b62258d4d6afe251c4ed60a02835ac4d2b743f926260b2f621cb2301a72de\",\n181\t      \"events_sha256\": \"6f0c813bf5489f1fce820bddd1160d6936ec5dc6e89f1c3ca2aecdbedc2834af\",\n182\t      \"bound_s\": \"0.03312014638436772\",\n183\t      \"verdict\": \"VERIFIED-VALID\",\n184\t      \"disposition\": \"valid\"\n185\t    },\n186\t    {\n187\t      \"n\": 5,\n188\t      \"attempt_id\": \"20260722T215127-eeef661a\",\n189\t      \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n190\t      \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n191\t      \"evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\",\n192\t      \"raw_sha256\": \"8e275c342b5dde493e24e69f5a30fd7224ec36c21b324bd489508cda5860bff8\",\n193\t      \"events_sha256\": \"30efea52cd15580aa4f4f52b959a4b6a881db0df0f72a488ae4d4493d51a8f75\",\n194\t      \"bound_s\": \"0.022741007370546462\",\n195\t      \"verdict\": \"VERIFIED-VALID\",\n196\t      \"disposition\": \"valid\"\n197\t    },\n198\t    {\n199\t      \"n\": 6,\n200\t      \"attempt_id\": \"20260722T222332-901c5c13\",\n201\t      \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n202\t      \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n203\t      \"evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\",\n204\t      \"raw_sha256\": \"84adafc6e55a45a10e56d5cea6571f1b12dae15656a2a0274822eb96500f4744\",\n205\t      \"events_sha256\": \"1b7ce059e4b72885a77cb398704590e50e51b925cdae7bf77db1ad2b36dd7d59\",\n206\t      \"bound_s\": \"0.03355875667989999\",\n207\t      \"verdict\": \"VERIFIED-VALID\",\n208\t      \"disposition\": \"valid\"\n209\t    },\n210\t    {\n211\t      \"n\": 7,\n212\t      \"attempt_id\": \"20260722T232509-82642517\",\n213\t      \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n214\t      \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n215\t      \"evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\",\n216\t      \"raw_sha256\": \"56555a10ee248cb6e5692280881d3daaf406b0432c2c3d068e06c5b8d8d76e40\",\n217\t      \"events_sha256\": \"1c2b84546ed000dbb6f3378f5a1ef24ae008048209bcffee95644bbad585df6b\",\n218\t      \"bound_s\": \"0.027654085293084385\",\n219\t      \"verdict\": \"VERIFIED-VALID\",\n220\t      \"disposition\": \"valid\"\n221\t    },\n222\t    {\n223\t      \"n\": 8,\n224\t      \"attempt_id\": \"20260723T023058-8732d1c9\",\n225\t      \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n226\t      \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n227\t      \"evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\",\n228\t      \"raw_sha256\": \"49d0b16529d40d6ce7a8d125f9787ab37e46ddfeb6b06e1b69a28e1a7011cf67\",\n229\t      \"events_sha256\": \"962780bf83e89c2e5a4720e074e49f06c0aa49cac3989bed9035436ed734455a\",\n230\t      \"bound_s\": \"0.024753340330112727\",\n231\t      \"verdict\": \"VERIFIED-VALID\",\n232\t      \"disposition\": \"valid\"\n233\t    },\n234\t    {\n235\t      \"n\": 9,\n236\t      \"attempt_id\": \"20260723T052051-d9358c8a\",\n237\t      \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n238\t      \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n239\t      \"evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\",\n240\t      \"raw_sha256\": \"dac05b535d4faa2f8864a2be91a6c56df812b1631fd60aaebde8e680a6aebc8e\",\n241\t      \"events_sha256\": \"7e79ef10b6d9caae132b04ae1e59d584c569aa751084fa02e62e2cad5f794fd3\",\n242\t      \"bound_s\": \"0.025964638697819786\",\n243\t      \"verdict\": \"VERIFIED-VALID\",\n244\t      \"disposition\": \"valid\"\n245\t    },\n246\t    {\n247\t      \"n\": 10,\n248\t      \"attempt_id\": \"20260723T183306-4ce692b4\",\n249\t      \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n250\t      \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n251\t      \"evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\",\n252\t      \"raw_sha256\": \"bcd97c9bd9b0a0686fc84bfa9d117685b6a68f8beed7f84dfa503eacaf78d941\",\n253\t      \"events_sha256\": \"7341d55729c2a3ebf68739900105893b5f2d59bb55d57092ef20e2b94d6c95ca\",\n254\t      \"bound_s\": \"0.027262160888545217\",\n255\t      \"verdict\": \"VERIFIED-VALID\",\n256\t      \"disposition\": \"valid\"\n257\t    },\n258\t    {\n259\t      \"n\": 11,\n260\t      \"attempt_id\": \"20260723T194632-d04e038e\",\n261\t      \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n262\t      \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n263\t      \"evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\",\n264\t      \"raw_sha256\": \"b1660d10fcc5015f0ccc0e4e0a7464db3a5220d415c952f3d9635e512faab57c\",\n265\t      \"events_sha256\": \"a965e301af8f2cb662dca60a7b9706d9b6e7dbabdc6971abd3119c46fc7711d6\",\n266\t      \"bound_s\": \"0.024593263907495888\",\n267\t      \"verdict\": \"VERIFIED-VALID\",\n268\t      \"disposition\": \"valid\"\n269\t    },\n270\t    {\n271\t      \"n\": 12,\n272\t      \"attempt_id\": \"20260723T195730-bc4ba14a\",\n273\t      \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n274\t      \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n275\t      \"evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\",\n276\t      \"raw_sha256\": \"81669d5e0e81ccb1d05ae7d19befffbf41441a92a1e14f0dcb8c0b8d9b6f7a86\",\n277\t      \"events_sha256\": \"0343c61d357465919f99b13000e39f02b43575c68c5383e1f03ffc46a3a2ee24\",\n278\t      \"bound_s\": \"0.025305226022515448\",\n279\t      \"verdict\": \"VERIFIED-VALID\",\n280\t      \"disposition\": \"valid\"\n281\t    },\n282\t    {\n283\t      \"n\": 13,\n284\t      \"attempt_id\": \"20260723T221449-e9ae755e\",\n285\t      \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n286\t      \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n287\t      \"evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\",\n288\t      \"raw_sha256\": \"4e971efc4abef1f51a636a095fa807d1b395ed8342f5e7386aead5e9c466ce50\",\n289\t      \"events_sha256\": \"1caf0be478a75308070e0a93818618af2dd8ca69f51bd2e35f1994c5b7f9b2d0\",\n290\t      \"bound_s\": \"0.027702588281732055\",\n291\t      \"verdict\": \"VERIFIED-VALID\",\n292\t      \"disposition\": \"valid\"\n293\t    },\n294\t    {\n295\t      \"n\": 14,\n296\t      \"attempt_id\": \"20260723T223406-314f6d9e\",\n297\t      \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n298\t      \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n299\t      \"evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\",\n300\t      \"raw_sha256\": \"2c92bf2a3065493b00caf678a5ee8d78c93d3dba406979cb824058b355274f73\",\n301\t      \"events_sha256\": \"4a4a990161e35f05d9fbd36c1eb52f78c46551145348036e073aa2494519df29\",\n302\t      \"bound_s\": \"0.026173651901677253\",\n303\t      \"verdict\": \"VERIFIED-VALID\",\n304\t      \"disposition\": \"valid\"\n305\t    },\n306\t    {\n307\t      \"n\": 15,\n308\t      \"attempt_id\": \"20260724T014109-57844352\",\n309\t      \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n310\t      \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n311\t      \"evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\",\n312\t      \"raw_sha256\": \"9c806bcd26a0f6cce7f33c00d930d803e39f9bd4a6e186971d6123a470a1b13d\",\n313\t      \"events_sha256\": \"221c42b7f214515f9af84c2b9486315df70e3466c66b7beb5bf35e476bf5ae14\",\n314\t      \"bound_s\": \"0.02547564583006129\",\n315\t      \"verdict\": \"VERIFIED-VALID\",\n316\t      \"disposition\": \"valid\"\n317\t    },\n318\t    {\n319\t      \"n\": 16,\n320\t      \"attempt_id\": \"20260725T005132-a64711b7\",\n321\t      \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n322\t      \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n323\t      \"evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\",\n324\t      \"raw_sha256\": \"a22005ea981f8e3ac1f3ea65cfa6bd1d0777dc009203b5e2db73cce44d2aca4e\",\n325\t      \"events_sha256\": \"459dc8a3ec34eb7a3f2095d0c5b72e931f8d87199fd48812386684f36162f617\",\n326\t      \"bound_s\": \"0.023241581438247116\",\n327\t      \"verdict\": \"VERIFIED-VALID\",\n328\t      \"disposition\": \"valid\"\n329\t    },\n330\t    {\n331\t      \"n\": 17,\n332\t      \"attempt_id\": \"20260725T011533-0b5ec77c\",\n333\t      \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n334\t      \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n335\t      \"evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\",\n336\t      \"raw_sha256\": \"9934c97547e2cd77de640754c2c51399a66bc96a265f31d38616677ab9973c3d\",\n337\t      \"events_sha256\": \"c15516d15ae525051012e8655817625d37803dda2b8473917720cc5a29ef3043\",\n338\t      \"bound_s\": \"0.028891617940876635\",\n339\t      \"verdict\": \"VERIFIED-VALID\",\n340\t      \"disposition\": \"valid\"\n341\t    },\n342\t    {\n343\t      \"n\": 18,\n344\t      \"attempt_id\": \"20260725T022712-0a9534f5\",\n345\t      \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n346\t      \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n347\t      \"evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\",\n348\t      \"raw_sha256\": \"bb99b0b7086ee939a8fb789253e2c0502de27a05d056c78d46dc30fccfb862cf\",\n349\t      \"events_sha256\": \"a42487bd9202c043485eebc42a68f505b35faf158c8640f1393d287a1d36e0d1\",\n350\t      \"bound_s\": \"0.029197264796726408\",\n351\t      \"verdict\": \"VERIFIED-VALID\",\n352\t      \"disposition\": \"valid\"\n353\t    },\n354\t    {\n355\t      \"n\": 19,\n356\t      \"attempt_id\": \"20260725T030533-d3f076e5\",\n357\t      \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n358\t      \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n359\t      \"evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\",\n360\t      \"raw_sha256\": \"26b9ad5ba13e2c73e78ddfdf5be6a2b1cf4b8eb31881aad575ac1bb7ae0dabb9\",\n361\t      \"events_sha256\": \"180a700366e1a97a9e8649a6d98bbd2d814fe9d5fed7246f99b47aa1af5e6b84\",\n362\t      \"bound_s\": \"0.024879191521227362\",\n363\t      \"verdict\": \"VERIFIED-VALID\",\n364\t      \"disposition\": \"valid\"\n365\t    },\n366\t    {\n367\t      \"n\": 20,\n368\t      \"attempt_id\": \"20260725T055825-b10cb348\",\n369\t      \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n370\t      \"manifest_sha256\": \"eebf3524d9e0b41c022c5e57d4b16787e98302e0d7c28381036415117fafb3ba\",\n371\t      \"evidence_sha256\": \"e0d525e0923f88572f7530f447a3bc8e889ef80a47d662840b86c40b4a35f285\",\n372\t      \"raw_sha256\": \"ed13e60dcfe12d7ce3900798dfbafb7936baa3700cdf58d0f6c1d0fc1790a4b8\",\n373\t      \"events_sha256\": \"fbb3d05c9185ed416d9c138fc63dc32d56b1cd465059007962f9273b53dce671\",\n374\t      \"bound_s\": null,\n375\t      \"verdict\": \"VERIFIED-INVALID\",\n376\t      \"disposition\": \"ordinary-invalid\",\n377\t      \"raw_reason\": \"fresh causal anchor unknown: wall_minus_monotonic_span_exceeded\"\n378\t    },\n379\t    {\n380\t      \"n\": 21,\n381\t      \"attempt_id\": \"20260725T060617-97c5cba6\",\n382\t      \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n383\t      \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n384\t      \"evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\",\n385\t      \"raw_sha256\": \"85583f5f07299f38f4f912581e2cfc03453d3a0e85a0de486b3406a355b2c9f2\",\n386\t      \"events_sha256\": \"c904c5f1a1c6557117b6fbde70dc8358dca773f94fc0c611cd50e92c3a3e2ffa\",\n387\t      \"bound_s\": \"0.025045994537554683\",\n388\t      \"verdict\": \"VERIFIED-VALID\",\n389\t      \"disposition\": \"valid\"\n390\t    },\n391\t    {\n392\t      \"n\": 22,\n393\t      \"attempt_id\": \"20260726T000039-491995f3\",\n394\t      \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n395\t      \"manifest_sha256\": \"b5e1d1195eb8c52bb41211b464909723754e5753bb866ced6f5715d83769ef65\",\n396\t      \"evidence_sha256\": \"9584cd7cdc44e5ba4d176475ce2bf6f70d04e163778fd6e9d5e46cec02303c00\",\n397\t      \"raw_sha256\": \"b916d0b8fc79e8fc7b261c6d608307fbae94bd3c89189e2256cafcf483378c2d\",\n398\t      \"events_sha256\": \"579c2adf45f245dbf31e69b83617fceaf28e63be70677fe0dcd8104a82c79248\",\n399\t      \"bound_s\": \"0.035435840879704805\",\n400\t      \"verdict\": \"VERIFIED-VALID\",\n401\t      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer and D-102\"\n402\t    },\n403\t    {\n404\t      \"n\": 23,\n405\t      \"attempt_id\": \"20260726T031222-e0ce33f5\",\n406\t      \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n407\t      \"manifest_sha256\": \"5ec9e27a9bdef89d8e83ca2fd2ee0c1c2d8d2effd56139ac904d1b032c3fc378\",\n408\t      \"evidence_sha256\": \"8d0b2d48460c71d35b2b3b7124b3168c86a497b5a674348451ea5d73931adab3\",\n409\t      \"raw_sha256\": \"c5674ce16dba60b5f0f61ffa5dbe6d7c38bc11747f627e120f6b96af7b9f2fe1\",\n410\t      \"events_sha256\": \"7ba5009ade8a7a870fcb119297dc34a54dcd78f54d13d463e2b4de721db7100b\",\n411\t      \"bound_s\": \"0.023854405254729094\",\n412\t      \"verdict\": \"VERIFIED-VALID\",\n413\t      \"disposition\": \"valid\"\n414\t    },\n415\t    {\n416\t      \"n\": 24,\n417\t      \"attempt_id\": \"20260726T225227-1f550773\",\n418\t      \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n419\t      \"manifest_sha256\": \"5837bd2c5be6769d63faa57a5d59311241038be7f92de6101b61566b54d89131\",\n420\t      \"evidence_sha256\": \"95941785a8fca5b74019da42d18d280abda639f92442ad57195b852ca567b564\",\n421\t      \"raw_sha256\": \"db6416cada6ea8c0bc84109903fc734d71c0f5a4d8451bafa05a05a76dd7b89d\",\n422\t      \"events_sha256\": \"2de1638cb73fa1a23105a81fe9cdcf9774f467adfcf6fa59bd29029c15a1a9cf\",\n423\t      \"bound_s\": \"0.04916527633725107\",\n424\t      \"verdict\": \"VERIFIED-INVALID\",\n425\t      \"disposition\": \"ordinary-invalid\",\n426\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n427\t    },\n428\t    {\n429\t      \"n\": 25,\n430\t      \"attempt_id\": \"20260726T225920-ab4272f5\",\n431\t      \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n432\t      \"manifest_sha256\": \"1696f470f0cc543a62cc40a819068a4b7b9f62058fd8d0dd1707870dd25b59e5\",\n433\t      \"evidence_sha256\": \"5b1c9dce56202e1d8af74e71b37aaa1538f0e53fcdded1e05c61cff90f41cda5\",\n434\t      \"raw_sha256\": \"4f83a36625a199a1e5e552953afbdc004bd5144756c8aa2bf657c8c714b4453f\",\n435\t      \"events_sha256\": \"dc704274c1c608a3a87387575c7a36e868c988f9737b033775f55d12791f80f5\",\n436\t      \"bound_s\": \"0.028145704403191807\",\n437\t      \"verdict\": \"VERIFIED-VALID\",\n438\t      \"disposition\": \"valid\"\n439\t    },\n440\t    {\n441\t      \"n\": 26,\n442\t      \"attempt_id\": \"20260727T015824-45feb516\",\n443\t      \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n444\t      \"manifest_sha256\": \"a7ac96e151419313594510f7511071cbdd710a1ab0837fef25a792ccc1b38d48\",\n445\t      \"evidence_sha256\": \"96f2af22ae5b18ba70f08ec2ed40c54abe0934508ae0d7cfb8fadb9de19432d8\",\n446\t      \"raw_sha256\": \"d0f8ab38ade1df00d957597f6ae0bfdffce047d8611416ecb434f91c4e35ae47\",\n447\t      \"events_sha256\": \"c75224662805694c090f458e6462f8a69581e39e7cf9a4f03d1c3d3b2ae7a371\",\n448\t      \"bound_s\": \"0.029425288011457773\",\n449\t      \"verdict\": \"VERIFIED-VALID\",\n450\t      \"disposition\": \"valid\"\n451\t    },\n452\t    {\n453\t      \"n\": 27,\n454\t      \"attempt_id\": \"20260727T020611-4a409a30\",\n455\t      \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n456\t      \"manifest_sha256\": \"dc30e9df75b0e4bc561c6f9d641ed3dff696697508333de6707d354151bd96ec\",\n457\t      \"evidence_sha256\": \"e3f4df9cf8bf4f1edfacbd10072bd53c5c1b59a873e4c25ee1727d74307ab3f8\",\n458\t      \"raw_sha256\": \"0961bf040013bf35d7d9fd2e5ad4b9d212d0dab9d733357c5193569ba7b92acd\",\n459\t      \"events_sha256\": \"bea8ab60b84b2ff7e00eff035c1187c837f26fdc30b91bfd0d4ca8ee6d15ecab\",\n460\t      \"bound_s\": \"0.029339001207750293\",\n461\t      \"verdict\": \"VERIFIED-VALID\",\n462\t      \"disposition\": \"valid\"\n463\t    },\n464\t    {\n465\t      \"n\": 28,\n466\t      \"attempt_id\": \"20260727T050047-95e2f87e\",\n467\t      \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n468\t      \"manifest_sha256\": \"d572e55594e97a4d4f3fb82295c8ad7aedac68c15c18e7615f3ac13e91ebea8a\",\n469\t      \"evidence_sha256\": \"2d70134135398b613638ae6ec62607913026c7d0cdfa9da1dfc77c657fa0e091\",\n470\t      \"raw_sha256\": \"b439d5bc06855943055795db69117ab612866d397eef219d73e0a576545b06c5\",\n471\t      \"events_sha256\": \"a90f500e118b1e88041167fb9fb3808ae0e27b83fa5b664f63c98adecf1ae7a1\",\n472\t      \"bound_s\": \"0.028854562420070173\",\n473\t      \"verdict\": \"VERIFIED-VALID\",\n474\t      \"disposition\": \"valid\"\n475\t    },\n476\t    {\n477\t      \"n\": 29,\n478\t      \"attempt_id\": \"20260729T204105-39d25f8a\",\n479\t      \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n480\t      \"manifest_sha256\": \"3aec4fc319e1de5a3b34d3552774ee4cf59ad9b1134001c8176d538f1304871f\",\n481\t      \"evidence_sha256\": \"4323c8c5242812b95e544213367dd75f0bc927605d73c78c1a491a84dd829026\",\n482\t      \"raw_sha256\": \"4f0cd62a013d6cc639e11637e425b8e09af02703828d4d0e9638a30ef70e88fc\",\n483\t      \"events_sha256\": \"0ef0f3e5779fb6b1aec6bb48fb60a76c175106b192f16f8aeaf95e3961b75c59\",\n484\t      \"bound_s\": \"0.031467745880268516\",\n485\t      \"verdict\": \"VERIFIED-VALID\",\n486\t      \"disposition\": \"valid\"\n487\t    },\n488\t    {\n489\t      \"n\": 30,\n490\t      \"attempt_id\": \"20260730T014035-124df355\",\n491\t      \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n492\t      \"manifest_sha256\": \"bb894782e7dd95d38576514fe9360335552129d6de116e2a05a82c17a70702f5\",\n493\t      \"evidence_sha256\": \"f8946df7f5495d6e5c64f90490b94ca2eab94f10ed16b7298e5741dadbe182b1\",\n494\t      \"raw_sha256\": \"95d50522d5eef61dbf2b9b815dce3f62e8791fe417942883908dde762351332b\",\n495\t      \"events_sha256\": \"d66899983a1d8e7b4bc7ecb11c5740534e101f4fbdd2810dd41ff00910277379\",\n496\t      \"bound_s\": \"0.027788174032371493\",\n497\t      \"verdict\": \"VERIFIED-VALID\",\n498\t      \"disposition\": \"valid\"\n499\t    },\n500\t    {\n501\t      \"n\": 31,\n502\t      \"attempt_id\": \"20260730T210703-f76b5771\",\n503\t      \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n504\t      \"manifest_sha256\": \"e40353dfd883d773414378893f27bc617cfa972f62793b0f35cc9efa30ed7d44\",\n505\t      \"evidence_sha256\": \"0f5e3ea38ff0f833840895e065941494c71c4cd9bf0fe222a9e08ca24ddc3ed8\",\n506\t      \"raw_sha256\": \"718b9046d134fc2a9f089818ea2e5c3aac05c10f056f942c8702ec3b4cdabf75\",\n507\t      \"events_sha256\": \"aaf29ec68222439453b790725b6849040c3f7c1cb5accf096d3a722edebf9664\",\n508\t      \"bound_s\": \"0.026131301462788137\",\n509\t      \"verdict\": \"VERIFIED-VALID\",\n510\t      \"disposition\": \"valid\"\n511\t    },\n512\t    {\n513\t      \"n\": 32,\n514\t      \"attempt_id\": \"20260731T012210-374020b6\",\n515\t      \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n516\t      \"manifest_sha256\": \"f64a179f03a6b3efecaea6e3ad8ff08ba8c354b9f57023f0929781fd2d133545\",\n517\t      \"evidence_sha256\": \"21a6296fc74542a6400ab5562376b9bf969a1d906c8f9076f89dc9916cef1b52\",\n518\t      \"raw_sha256\": \"0f3b509c48e42a9cbcf32ac3a446d9c13d38766328f9569a96d397a685ad2f2d\",\n519\t      \"events_sha256\": \"624b9c26e71648272e36c85fa7884aa258851039a7e77a7be123e1290d2c4b79\",\n520\t      \"bound_s\": \"0.024850427856341006\",\n521\t      \"verdict\": \"VERIFIED-VALID\",\n522\t      \"disposition\": \"valid\"\n523\t    },\n524\t    {\n525\t      \"n\": 33,\n526\t      \"attempt_id\": \"20260731T161713-b8b08280\",\n527\t      \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n528\t      \"manifest_sha256\": \"e65aed76d770fbcd9c07b6c2dc26335ddf593533ff1ab6a46cb1bc9bdd119d0a\",\n529\t      \"evidence_sha256\": \"2cda4856ae7939067f0a6ebbbdb865871e437e1c652b0dd438e33cb5ffef1583\",\n530\t      \"raw_sha256\": \"464f5f9ca38818544e54061407251ef3d13541c90c8e5c6f05ee54fe8a913068\",\n531\t      \"events_sha256\": \"2bfd2ac5f0ba88e02a89dbc070837ce3bb1161b2d3067a6176e720bb778b4df1\",\n532\t      \"bound_s\": \"0.030972654450356962\",\n533\t      \"verdict\": \"VERIFIED-VALID\",\n534\t      \"disposition\": \"valid\"\n535\t    },\n536\t    {\n537\t      \"n\": 34,\n538\t      \"attempt_id\": \"20260731T214355-126fc2ab\",\n539\t      \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n540\t      \"manifest_sha256\": \"ad3aa2345df71df05fb5913ef52210443eb07cfbbb5824e48794b6892557848d\",\n541\t      \"evidence_sha256\": \"1958d58c35dfa30c18671abafcddf3d43c9328f586ce2051d1fb83ab99b51d5f\",\n542\t      \"raw_sha256\": \"c14ef61161fc9bf463840d5f62e1cdcd9bc2fe586297e5d89a6334e19f8dd21f\",\n543\t      \"events_sha256\": \"89808fe44225b7870585a1f2883ff43b01ec0b02507775900ada0a60251f145c\",\n544\t      \"bound_s\": null,\n545\t      \"verdict\": \"VERIFIED-INVALID\",\n546\t      \"disposition\": \"ordinary-invalid\",\n547\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n548\t    },\n549\t    {\n550\t      \"n\": 35,\n551\t      \"attempt_id\": \"20260801T010113-e859f3aa\",\n552\t      \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n553\t      \"manifest_sha256\": \"52aa9e9b4485a352d1ba2bd40e500f71cab989967d1db6e7a130fe9c157e0647\",\n554\t      \"evidence_sha256\": \"6c350a69406f92f4f1d68e30684f6b36b2f233fba5f52070a73f23c3d767fd45\",\n555\t      \"raw_sha256\": \"1302b53b6aeab97ee57b35cda8003ffb6d107265979614880910c24fdbbb5e7c\",\n556\t      \"events_sha256\": \"887ea9f6bc663ac5bc8cfe1c6d898262a2089602406186f83ff0f750983a841b\",\n557\t      \"bound_s\": \"0.41198917978147415\",\n558\t      \"verdict\": \"VERIFIED-INVALID\",\n559\t      \"disposition\": \"ordinary-invalid\",\n560\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n561\t    },\n562\t    {\n563\t      \"n\": 36,\n564\t      \"attempt_id\": \"20260801T010805-ff3fdc88\",\n565\t      \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n566\t      \"manifest_sha256\": \"fd5906ccd884670c9d40a57e7b8b4755357bc91c89f281449a080fe5c2007402\",\n567\t      \"evidence_sha256\": \"62967d66a74467735011f159a523f50b6409287bf96899446e4a02fa2c8e2eed\",\n568\t      \"raw_sha256\": \"c39bc0c6c55a3deabdffdf8bfdad95e061fb464def586edafdc19dbd1d8ea5c2\",\n569\t      \"events_sha256\": \"10e9035731a2d54a9469c66318568b6f2e91a0ac3fecdbfad94dfb62c22bf0fc\",\n570\t      \"bound_s\": null,\n571\t      \"verdict\": \"VERIFIED-INVALID\",\n572\t      \"disposition\": \"ordinary-invalid\",\n573\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n574\t    },\n575\t    {\n576\t      \"n\": 37,\n577\t      \"attempt_id\": \"20260801T014059-8c3bfe9e\",\n578\t      \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n579\t      \"manifest_sha256\": \"7d2967b125324c65e0d57a16950a0e1c2e2946464b7eb89667e8fc2410550149\",\n580\t      \"evidence_sha256\": \"c1653f369e05e9186d0c6d06231993575ee23c1fd813b96f1094d74dfbaac0ad\",\n581\t      \"raw_sha256\": \"f1a9350cbfdb0ec4c0a909b5d2b77798e16f754132499602b426a1068274465f\",\n582\t      \"events_sha256\": \"33f78ee6e299643d8f5929fc2e339f3e13959eb6983a7db8b8af4bd936a0700d\",\n583\t      \"bound_s\": \"0.032786870825707914\",\n584\t      \"verdict\": \"VERIFIED-VALID\",\n585\t      \"disposition\": \"valid\"\n586\t    },\n587\t    {\n588\t      \"n\": 38,\n589\t      \"attempt_id\": \"20260801T064830-c76f5d1c\",\n590\t      \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n591\t      \"manifest_sha256\": \"6127f706081c4686164ecca83032ab86bdc467170d55b24e537255cfdacac4dc\",\n592\t      \"evidence_sha256\": \"4c2752a194dbd1fc39aaf82e11071cccab4283c81f46208657bd849af6c23a06\",\n593\t      \"raw_sha256\": \"dab52b86df50235d78c39ddda87b3f4620b6dfdead9050640184204630cd5b1f\",\n594\t      \"events_sha256\": \"31e245dcaf050740a69f52ab3afa1783e2081e43a089dc57045be6039f7503e6\",\n595\t      \"bound_s\": \"0.0350400833260715\",\n596\t      \"verdict\": \"VERIFIED-VALID\",\n597\t      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer\"\n598\t    }\n599\t  ],\n600\t  \"raw_physics_method\": {\n601\t    \"valid_members\": \"Used verify_stored_evidence_physics, which rejects stored-status substitution, re-derives the causal anchor, reconstructs all pulse commands from events.jsonl, re-fits all 59 pulses, requires complete detection/no spurious plateaus/no reasons, checks every stored residual enclosure contains the refit, and returns max(stored,fresh) bound.\",\n602\t    \"valid_method_source\": \"joulewise/powermetrics_fiducial.py:1088-1164; docs/contracts/powermetrics_fiducial.md:183-211\",\n603\t    \"invalid_members\": \"Re-derived the causal anchor directly from native powermetrics records and recorded ClockStamps. All six independently returned unknown; an unresolved own anchor is forced invalid under the contract.\",\n604\t    \"hash_evidence\": \"Each selected custody manifest's lines 3-6 bind events, instrument evidence, power trace and raw plist. Every listed digest matched the bytes.\"\n605\t  },\n606\t  \"bootstrap_computation\": {\n607\t    \"authoritative_result\": \"NOT COMPUTABLE WITHOUT RULING/IMPORT CONTRACT\",\n608\t    \"required_prior_observation_set\": \"The exact 38 content IDs in per_member, each with epoch_id=d079_epoch and the final ruled disposition. No additional fixture-known-holdout row is evidenced by a real content bundle; configs/calibration/calibration_acceptance_d079_v2.json:222 is explicitly fixture data.\",\n609\t    \"receipt_algorithm_from_schema\": [\n610\t      \"receipt_core is canonical JSON with sorted keys, separators ',' and ':', UTF-8, allow_nan=false; receipt_digest=sha256(receipt_core). See joulewise/calibration_ledger.py:94-105,155-160.\",\n611\t      \"Each receipt contains sequence, predecessor_digest, event, attempt_id, content_id, artifact hashes, six-field epoch, full T1, capture lexeme, exact bound lexeme, disposition and custody locator. See joulewise/calibration_ledger.py:590-622.\",\n612\t      \"The parser requires a reservation before each finalization. See joulewise/calibration_ledger.py:409-465 and finalize_attempt_receipt at :716-777.\",\n613\t      \"The head pin is the final receipt's sequence and receipt_digest with ledger_schema. See joulewise/calibration_ledger.py:780-789.\"\n614\t    ],\n615\t    \"conditional_non_authoritative_replays\": [\n616\t      {\n617\t        \"assumptions\": \"Attempt IDs sorted ascending; one synthetic reservation immediately followed by one finalization per content ID; first hash-complete custody copy selected; candidate-tool mapping of all stored-valid rows to valid and stored-invalid rows to ordinary-invalid.\",\n618\t        \"sequence\": 76,\n619\t        \"head_digest\": \"cb410907660ed8a120d4e1d04a7e9af489b69d83686a8bf7658b3f73e7e3335a\",\n620\t        \"prior_observation_rows_sha256\": \"d29404feea08496453538d8b3994af1c4b64c12a86b950a3aa96a604cb6690c6\",\n621\t        \"dispositions\": {\n622\t          \"valid\": 32,\n623\t          \"ordinary-invalid\": 6\n624\t        },\n625\t        \"warning\": \"Illustrative only; the assumptions are not authorized by D-109 or an import schema.\"\n626\t      },\n627\t      {\n628\t        \"assumptions\": \"Same ordering/custody rules, but apply the production writer's preflight-screen mapping to members 22 and 38.\",\n629\t        \"sequence\": 76,\n630\t        \"head_digest\": \"8e80b6e93804df098f9fbec66740757073d235019e19990c7a9d8270b28337f1\",\n631\t        \"prior_observation_rows_sha256\": \"f28ddf8e0995230857c7e7db11c031084e18e8919ea1b9b373ae2112a9a936bf\",\n632\t        \"dispositions\": {\n633\t          \"valid\": 30,\n634\t          \"systematic-invalid\": 2,\n635\t          \"ordinary-invalid\": 6\n636\t        },\n637\t        \"warning\": \"Illustrative only; differs from D-109 R2.8's stated six-further consequence.\"\n638\t      }\n639\t    ],\n640\t    \"additional_implementation_gap\": \"append_pending_receipt requires the current physical ledger head to equal the committed pin before each new reservation (joulewise/calibration_ledger.py:673-690). Once one reservation/finalization pair advances the physical ledger, another reservation cannot be appended under the unchanged genesis pin. A batch bootstrap/import route is therefore required; none exists.\"\n641\t  },\n642\t  \"derivation_corpus\": {\n643\t    \"n\": 19,\n644\t    \"unchanged\": true,\n645\t    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:46-183\",\n646\t    \"artifact_file_sha256\": \"9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb\",\n647\t    \"stored_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n648\t    \"computed_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n649\t    \"match\": true,\n650\t    \"reconstructed_statistics\": {\n651\t      \"minimum_s\": \"0.022741007370546462\",\n652\t      \"minimum_member\": \"20260722T215127-eeef661a\",\n653\t      \"maximum_s\": \"0.03355875667989999\",\n654\t      \"maximum_member\": \"20260722T222332-901c5c13\",\n655\t      \"range_s\": \"0.010817749309353528\",\n656\t      \"mean_s\": \"0.026950033977532761\",\n657\t      \"sample_sd_s\": \"0.002970761365307205\"\n658\t    },\n659\t    \"note\": \"The current derivation_sha256 covers the complete artifact core excluding the hash field, not only the n=19 table (joulewise/calibration_bracketing.py:155-177). Issuance edits will therefore require a new canonical hash even though the threshold-producing n=19 remains unchanged.\"\n660\t  },\n661\t  \"D102_corpus_doubling\": {\n662\t    \"binding_rule\": \"38 total authenticated, content-distinct, valid same-epoch observations\",\n663\t    \"implementation_source\": \"joulewise/calibration_bracketing.py:901-908\",\n664\t    \"candidate_tool_disposition_result\": {\n665\t      \"current_valid_total\": 32,\n666\t      \"additional_valid_needed\": 6,\n667\t      \"trigger_now\": false,\n668\t      \"matches_D109_R2_8\": true\n669\t    },\n670\t    \"production_writer_disposition_result\": {\n671\t      \"current_valid_total\": 30,\n672\t      \"additional_valid_needed\": 8,\n673\t      \"trigger_now\": false,\n674\t      \"matches_D109_R2_8\": false\n675\t    },\n676\t    \"decision\": \"BLOCKED pending the B1 disposition ruling. The report does not choose between these counts.\"\n677\t  },\n678\t  \"verification\": [\n679\t    {\n680\t      \"id\": \"V1\",\n681\t      \"result\": \"PASS\",\n682\t      \"check\": \"Enumerated runs*/instrument_validation manifests, exact six-field epoch filtered, canonical content IDs recomputed.\",\n683\t      \"observed\": \"53 checkout custody copies; 38 distinct IDs; stored labels 32 valid/6 invalid.\"\n684\t    },\n685\t    {\n686\t      \"id\": \"V2\",\n687\t      \"result\": \"PASS\",\n688\t      \"check\": \"For every selected representative, rehashed every manifest-listed artifact and every evidence-internal artifact hash.\",\n689\t      \"observed\": \"Zero missing or mismatched bytes.\"\n690\t    },\n691\t    {\n692\t      \"id\": \"V3\",\n693\t      \"result\": \"PASS\",\n694\t      \"check\": \"Replayed strict raw physics for every candidate-valid observation and causal-anchor physics for every candidate-invalid observation.\",\n695\t      \"observed\": \"32 VERIFIED-VALID; 6 VERIFIED-INVALID; 0 raw unresolved.\"\n696\t    },\n697\t    {\n698\t      \"id\": \"V4\",\n699\t      \"result\": \"PASS\",\n700\t      \"check\": \"PYTHONDONTWRITEBYTECODE=1 python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact configs/calibration/calibration_acceptance_d079_v2.json\",\n701\t      \"observed\": \"PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK; n=19 statistics reproduced.\"\n702\t    },\n703\t    {\n704\t      \"id\": \"V5\",\n705\t      \"result\": \"PASS\",\n706\t      \"check\": \"Canonical artifact-core SHA-256 recomputation.\",\n707\t      \"observed\": \"stored=computed=3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d.\"\n708\t    },\n709\t    {\n710\t      \"id\": \"V6\",\n711\t      \"result\": \"PASS\",\n712\t      \"check\": \"Final git status.\",\n713\t      \"observed\": \"## main...origin/main; no changes.\"\n714\t    }\n715\t  ],\n716\t  \"flags\": [\n717\t    {\n718\t      \"id\": \"NO_EDITS\",\n719\t      \"level\": \"informational\",\n720\t      \"text\": \"Read-only verification; no artifact, ledger, pin, report or state file was created or modified.\"\n721\t    },\n722\t    {\n723\t      \"id\": \"ISSUANCE_BLOCKED\",\n724\t      \"level\": \"blocking\",\n725\t      \"text\": \"Lead must first rule the two high-bound dispositions and authorize a deterministic historical-import/bootstrap contract, including ordering and custody selection. Only then can one exact prior_observation_set, sequence and head digest be issued.\"\n726\t    }\n727\t  ],\n728\t  \"next_exact_step\": \"Lead rules whether members 20260726T000039-491995f3 and 20260801T064830-c76f5d1c are ledger-valid or systematic-invalid, then specifies the authenticated batch-import ordering/custody rule. Recompute the single resulting 76-receipt chain, review its exact head, and only in a separately authorized write session bootstrap the ledger, update and commit the head pin, and issue the acceptance artifact.\"\n729\t}\n730\t```"}]},"uuid":"db5a984e-c70e-4f45-a319-007973acd308","timestamp":"2026-08-06T08:35:26.699Z","toolUseResult":{"type":"text","file":{"filePath":"/Users/edr/code/JouleWise/docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md","content":"```json\n{\n  \"schema\": \"claude-codex-report/v1\",\n  \"genre\": \"verification\",\n  \"status\": \"findings\",\n  \"completion\": \"complete\",\n  \"summary\": \"BLOCKED. All 38 content-distinct candidates were recovered, hash-authenticated, epoch-checked, and replayed from raw physics: 32 VERIFIED-VALID and 6 VERIFIED-INVALID, with no missing raw evidence. Issuance is not ready because two verified-valid observations exceed the systematic-failure screen and therefore lack an unambiguous ledger disposition, and the repository does not specify a deterministic authenticated historical-import/bootstrap transaction from which one authoritative sequence/head digest can be computed.\",\n  \"workspace\": {\n    \"head_start\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n    \"head_end\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n    \"branch\": \"main\",\n    \"pathspec\": [],\n    \"unowned_dirty\": [],\n    \"write_scope\": \"none\",\n    \"edits\": \"none\"\n  },\n  \"verdict\": {\n    \"overall\": \"BLOCKED\",\n    \"prompt_vs_R2_divergence\": false,\n    \"raw_member_results\": {\n      \"VERIFIED-VALID\": 32,\n      \"VERIFIED-INVALID\": 6,\n      \"UNRESOLVED\": 0\n    },\n    \"blocking_items\": [\n      {\n        \"id\": \"B1\",\n        \"type\": \"ledger_disposition_ruling\",\n        \"members\": [\n          \"20260726T000039-491995f3\",\n          \"20260801T064830-c76f5d1c\"\n        ],\n        \"reason\": \"Both replay as physically valid, matching the candidate inventory, but their bounds 0.035435840879704805 and 0.0350400833260715 exceed the ratified 0.033558756679900 preflight screen. The production writer maps such a valid capture to systematic-invalid at scripts/validate_powermetrics_fiducial.py:664-671; D-102 explicitly calls the first member a systematic failure at docs/decision_log.md:6298-6301. The backfill candidate tool instead proposes valid solely from stored status at scripts/calibration_ledger_backfill.py:58-63. Selecting either disposition is lead-owned.\"\n      },\n      {\n        \"id\": \"B2\",\n        \"type\": \"bootstrap_contract_gap\",\n        \"members\": \"all 38\",\n        \"reason\": \"No historical-import/bootstrap API, receipt ordering, duplicate-custody selection rule, or import-transaction schema exists. The candidate tool emits only an unauthoritative candidate set and never appends the ledger (scripts/calibration_ledger_backfill.py:2-7,90-117). Because receipt digests bind sequence, predecessor, disposition, artifact hashes and absolute custody locator (joulewise/calibration_ledger.py:590-622), more than one valid head digest is possible.\"\n      }\n    ]\n  },\n  \"binding_clauses\": [\n    {\n      \"clause\": \"D-109 R1.4\",\n      \"source\": \"docs/decision_log.md:7027-7039\",\n      \"verbatim\": \"4. The acceptance artifact pins its baseline ledger head. Evaluation ALSO requires the independent current-head pin (clause below), verifies one complete non-forked chain extension from baseline to current, and threads ONE immutable ledger snapshot through every consumer path (session, direct runner path, secondary verifier) — repeated independent loads are a refusal-grade defect. Anti-rollback authority: a REPO-COMMITTED head-pin file `{sequence, head_digest, ledger_schema}` (existing checked-in byte-pin trust model; no second trusted latest-sequence store). Rotation is epoch-bounded — at most one lead-controlled quiet-machine collection session — and NO claim evaluation may occur between ledger advancement and pin commit; a physical head differing from the committed pin refuses.\",\n      \"verification_plan\": \"After an authorized bootstrap, recompute every receipt digest, require one linear chain, require the artifact cutoff to equal an exact receipt, require the physical head to equal the separately committed pin, and trace one snapshot object through every consumer. This session verified the implemented digest/head machinery but could not select an authoritative bootstrap head because no import transaction is specified.\"\n    },\n    {\n      \"clause\": \"D-109 R2.1\",\n      \"source\": \"docs/decision_log.md:7053\",\n      \"verbatim\": \"1. The issuance cutoff is an exact ledger sequence + head digest.\",\n      \"verification_plan\": \"Compute the final receipt count and digest only after disposition, ordering and custody-locator rules are fixed. Current fixture cutoff remains non-production genesis sequence 0/all-zero digest at configs/calibration/calibration_acceptance_d079_v2.json:14-18.\"\n    },\n    {\n      \"clause\": \"D-109 R2.2\",\n      \"source\": \"docs/decision_log.md:7054-7055\",\n      \"verbatim\": \"2. `derivation_corpus` remains exactly the n=19 threshold-producing observations.\",\n      \"verification_plan\": \"Re-run the corpus verifier against all 19 pinned member manifest/evidence hashes and recompute the decimal statistics and artifact canonical hash. Result: PASS.\"\n    },\n    {\n      \"clause\": \"D-109 R2.3\",\n      \"source\": \"docs/decision_log.md:7056-7060\",\n      \"verbatim\": \"3. `prior_observation_set` = every content-distinct governed observation known at the cutoff — valid, systematic-invalid, ordinary-invalid, blind holdout, and unresolved — with epoch and disposition recorded separately. (The current artifact's two ID-only `blind_exclusions` are insufficient and are superseded.)\",\n      \"verification_plan\": \"Enumerate every exact-epoch validation tree, collapse copies by canonical content ID, authenticate the raw bytes, and assign one epoch plus one ruled disposition per content ID. The 38 identities are complete for the located candidate, but two dispositions require a ruling.\"\n    },\n    {\n      \"clause\": \"D-109 R2.4\",\n      \"source\": \"docs/decision_log.md:7061-7063\",\n      \"verbatim\": \"4. Content identity is path-independent, derived from canonical primary-byte hashes; attempt identity is separate; copies do not create new observations.\",\n      \"verification_plan\": \"Hash manifest.json and instrument_evidence.json bytes, canonical-JSON encode the two-name hash map, SHA-256 it, and collapse identical IDs. Implementation is joulewise/calibration_ledger.py:94-105,120-134. Result: 53 checkout copies collapse to 38 IDs.\"\n    },\n    {\n      \"clause\": \"D-109 R2.5\",\n      \"source\": \"docs/decision_log.md:7064-7068\",\n      \"verbatim\": \"5. \\\"New\\\" (trigger population) = current authentic content IDs − `prior_observation_set`, regardless of capture timestamp or source root; a previously unknown historical artifact IS new when discovered. Every new observation is judged under the PRIOR artifact (D-102's prospective rule).\",\n      \"verification_plan\": \"After issuance, subtract the exact 38-ID prior set from the authenticated ledger snapshot, independent of path/time, before applying triggers. The implemented subtraction is at joulewise/calibration_bracketing.py:870-893.\"\n    },\n    {\n      \"clause\": \"D-109 R2.6\",\n      \"source\": \"docs/decision_log.md:7069-7070\",\n      \"verbatim\": \"6. New unresolved or unclassifiable attempts cause refusal; only after trigger disposition may a successor artifact absorb them.\",\n      \"verification_plan\": \"Require every post-cutoff receipt to classify as valid, systematic-invalid or ordinary-invalid; unresolved/abandoned/null-content rows must refuse. Implemented refusal is at joulewise/calibration_bracketing.py:895-900.\"\n    },\n    {\n      \"clause\": \"D-109 R2.7\",\n      \"source\": \"docs/decision_log.md:7071-7074\",\n      \"verbatim\": \"7. The 32-valid/6-invalid same-epoch inventory is a backfill CANDIDATE, not a ratified classification: identities may seed the backfill, but dispositions require raw-physics + hash verification before issuance, and any unresolved member blocks issuance.\",\n      \"verification_plan\": \"For all 38 members: verify manifest and evidence hashes, verify raw/event hashes, replay causal clock-anchor derivation and the strict 59-pulse detector, verify the six-field epoch, then compare with candidate labeling. Result: 32 VERIFIED-VALID, 6 VERIFIED-INVALID, zero raw-physics unresolved; two final ledger dispositions remain ambiguous.\"\n    },\n    {\n      \"clause\": \"D-109 R2.8\",\n      \"source\": \"docs/decision_log.md:7075-7079\",\n      \"verbatim\": \"8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38 TOTAL authenticated, content-distinct, VALID same-epoch observations — including previously blind observations once unblinded — not 38 post-cutoff observations. Under the candidate inventory, six further valid observations trigger re-derivation.\",\n      \"verification_plan\": \"Count content-distinct ledger observations whose disposition is exactly valid and whose epoch equals d079_epoch. The implementation does this at joulewise/calibration_bracketing.py:901-908. Result is six further only under the candidate-tool 32-valid disposition proposal; it is eight further under the production writer's systematic-screen mapping.\"\n    }\n  ],\n  \"inventory\": {\n    \"where_it_lives\": {\n      \"count_only_authority\": [\n        \"docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:296-308\",\n        \"configs/calibration/calibration_acceptance_d079_v2.json:225-233\"\n      ],\n      \"candidate_emitter\": \"scripts/calibration_ledger_backfill.py:42-117\",\n      \"concrete_membership\": \"Implicit in the 53 exact-epoch validation custody trees under runs*/instrument_validation; no standalone serialized 38-row candidate file exists in the checkout or .desk.\",\n      \"raw_archive\": \"/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup\",\n      \"important_non_inventory\": \"docs/process_traces/2026-08-03-d111-backfill/MANIFEST.md is a manifest of 41 process artifacts, not the 38 calibration observations.\"\n    },\n    \"identity_method\": \"sha256(canonical_json({\\\"instrument_evidence.json\\\": sha256(evidence bytes), \\\"manifest.json\\\": sha256(manifest bytes)}))\",\n    \"identity_method_source\": \"joulewise/calibration_ledger.py:94-105,120-134\",\n    \"checkout_copy_count\": 53,\n    \"content_distinct_count\": 38,\n    \"candidate_label_counts\": {\n      \"valid\": 32,\n      \"invalid\": 6\n    },\n    \"analysis_only_member_set_sha256\": {\n      \"value\": \"7c0ae751e3be9d180c932b14da1cc9b50f85a73a0821de03c7a7911728a25e95\",\n      \"definition\": \"canonical SHA-256 of the ordered 38 candidate rows containing attempt_id, content_id, all artifact hashes, epoch, full T1, capture lexeme and bound lexeme; custody locator deliberately excluded. This digest is verification evidence, not a contract-defined production identity.\"\n    }\n  },\n  \"epoch\": {\n    \"epoch_id\": \"d079_epoch\",\n    \"all_38_match\": true,\n    \"fields\": {\n      \"os_build\": \"25F84\",\n      \"hardware_model\": \"Mac15,9\",\n      \"power_policy\": \"ac_high_power\",\n      \"sampling_interval_ms\": 100,\n      \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n      \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n    },\n    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:20-26,193-200\"\n  },\n  \"per_member\": [\n    {\n      \"n\": 1,\n      \"attempt_id\": \"20260722T145535-e941c821\",\n      \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n      \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n      \"evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\",\n      \"raw_sha256\": \"b55f3471c70c54e0174b09e67486759fc532742e9bd671e53ce8324fe23209ef\",\n      \"events_sha256\": \"605e2330d27f874621edb698c233542d7eb31fb8b8d1def044852a77a223b1bc\",\n      \"bound_s\": \"0.03018980442653224\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 2,\n      \"attempt_id\": \"20260722T194118-9dc0749d\",\n      \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n      \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n      \"evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\",\n      \"raw_sha256\": \"aa36a9c1e8451e2a0de875a7ff45232c98bf0cce5cdcd5b827d176ea24aa85f7\",\n      \"events_sha256\": \"0f543eb7f697d442a5c0ddce1fe6f3f69c268c96bdc7a5ffbb6e84f70e8f1d66\",\n      \"bound_s\": \"0.026300679324099796\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 3,\n      \"attempt_id\": \"20260722T213749-563b9849\",\n      \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n      \"manifest_sha256\": \"b7dd23cf8a9e30d81a01ba0b3c5c5e0c21b4c325e48e1d02e046fb61b77cb0ac\",\n      \"evidence_sha256\": \"1cc789e9558667e188f1859ba591a584a73eb4d2309612c924eebfb4cf5ffe80\",\n      \"raw_sha256\": \"3684b27080f6b4254d61e1c5b3f0f25e8401257078145331ef2122b2c1893fd1\",\n      \"events_sha256\": \"b179d606c17148e754bba07bb61c3d7a5c094e5a0e701251e7674b45472f5a4b\",\n      \"bound_s\": \"0.2079182387602739\",\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 4,\n      \"attempt_id\": \"20260722T214220-1acdbbc0\",\n      \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n      \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n      \"evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\",\n      \"raw_sha256\": \"7a4b62258d4d6afe251c4ed60a02835ac4d2b743f926260b2f621cb2301a72de\",\n      \"events_sha256\": \"6f0c813bf5489f1fce820bddd1160d6936ec5dc6e89f1c3ca2aecdbedc2834af\",\n      \"bound_s\": \"0.03312014638436772\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 5,\n      \"attempt_id\": \"20260722T215127-eeef661a\",\n      \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n      \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n      \"evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\",\n      \"raw_sha256\": \"8e275c342b5dde493e24e69f5a30fd7224ec36c21b324bd489508cda5860bff8\",\n      \"events_sha256\": \"30efea52cd15580aa4f4f52b959a4b6a881db0df0f72a488ae4d4493d51a8f75\",\n      \"bound_s\": \"0.022741007370546462\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 6,\n      \"attempt_id\": \"20260722T222332-901c5c13\",\n      \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n      \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n      \"evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\",\n      \"raw_sha256\": \"84adafc6e55a45a10e56d5cea6571f1b12dae15656a2a0274822eb96500f4744\",\n      \"events_sha256\": \"1b7ce059e4b72885a77cb398704590e50e51b925cdae7bf77db1ad2b36dd7d59\",\n      \"bound_s\": \"0.03355875667989999\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 7,\n      \"attempt_id\": \"20260722T232509-82642517\",\n      \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n      \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n      \"evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\",\n      \"raw_sha256\": \"56555a10ee248cb6e5692280881d3daaf406b0432c2c3d068e06c5b8d8d76e40\",\n      \"events_sha256\": \"1c2b84546ed000dbb6f3378f5a1ef24ae008048209bcffee95644bbad585df6b\",\n      \"bound_s\": \"0.027654085293084385\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 8,\n      \"attempt_id\": \"20260723T023058-8732d1c9\",\n      \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n      \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n      \"evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\",\n      \"raw_sha256\": \"49d0b16529d40d6ce7a8d125f9787ab37e46ddfeb6b06e1b69a28e1a7011cf67\",\n      \"events_sha256\": \"962780bf83e89c2e5a4720e074e49f06c0aa49cac3989bed9035436ed734455a\",\n      \"bound_s\": \"0.024753340330112727\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 9,\n      \"attempt_id\": \"20260723T052051-d9358c8a\",\n      \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n      \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n      \"evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\",\n      \"raw_sha256\": \"dac05b535d4faa2f8864a2be91a6c56df812b1631fd60aaebde8e680a6aebc8e\",\n      \"events_sha256\": \"7e79ef10b6d9caae132b04ae1e59d584c569aa751084fa02e62e2cad5f794fd3\",\n      \"bound_s\": \"0.025964638697819786\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 10,\n      \"attempt_id\": \"20260723T183306-4ce692b4\",\n      \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n      \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n      \"evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\",\n      \"raw_sha256\": \"bcd97c9bd9b0a0686fc84bfa9d117685b6a68f8beed7f84dfa503eacaf78d941\",\n      \"events_sha256\": \"7341d55729c2a3ebf68739900105893b5f2d59bb55d57092ef20e2b94d6c95ca\",\n      \"bound_s\": \"0.027262160888545217\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 11,\n      \"attempt_id\": \"20260723T194632-d04e038e\",\n      \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n      \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n      \"evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\",\n      \"raw_sha256\": \"b1660d10fcc5015f0ccc0e4e0a7464db3a5220d415c952f3d9635e512faab57c\",\n      \"events_sha256\": \"a965e301af8f2cb662dca60a7b9706d9b6e7dbabdc6971abd3119c46fc7711d6\",\n      \"bound_s\": \"0.024593263907495888\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 12,\n      \"attempt_id\": \"20260723T195730-bc4ba14a\",\n      \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n      \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n      \"evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\",\n      \"raw_sha256\": \"81669d5e0e81ccb1d05ae7d19befffbf41441a92a1e14f0dcb8c0b8d9b6f7a86\",\n      \"events_sha256\": \"0343c61d357465919f99b13000e39f02b43575c68c5383e1f03ffc46a3a2ee24\",\n      \"bound_s\": \"0.025305226022515448\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 13,\n      \"attempt_id\": \"20260723T221449-e9ae755e\",\n      \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n      \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n      \"evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\",\n      \"raw_sha256\": \"4e971efc4abef1f51a636a095fa807d1b395ed8342f5e7386aead5e9c466ce50\",\n      \"events_sha256\": \"1caf0be478a75308070e0a93818618af2dd8ca69f51bd2e35f1994c5b7f9b2d0\",\n      \"bound_s\": \"0.027702588281732055\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 14,\n      \"attempt_id\": \"20260723T223406-314f6d9e\",\n      \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n      \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n      \"evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\",\n      \"raw_sha256\": \"2c92bf2a3065493b00caf678a5ee8d78c93d3dba406979cb824058b355274f73\",\n      \"events_sha256\": \"4a4a990161e35f05d9fbd36c1eb52f78c46551145348036e073aa2494519df29\",\n      \"bound_s\": \"0.026173651901677253\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 15,\n      \"attempt_id\": \"20260724T014109-57844352\",\n      \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n      \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n      \"evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\",\n      \"raw_sha256\": \"9c806bcd26a0f6cce7f33c00d930d803e39f9bd4a6e186971d6123a470a1b13d\",\n      \"events_sha256\": \"221c42b7f214515f9af84c2b9486315df70e3466c66b7beb5bf35e476bf5ae14\",\n      \"bound_s\": \"0.02547564583006129\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 16,\n      \"attempt_id\": \"20260725T005132-a64711b7\",\n      \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n      \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n      \"evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\",\n      \"raw_sha256\": \"a22005ea981f8e3ac1f3ea65cfa6bd1d0777dc009203b5e2db73cce44d2aca4e\",\n      \"events_sha256\": \"459dc8a3ec34eb7a3f2095d0c5b72e931f8d87199fd48812386684f36162f617\",\n      \"bound_s\": \"0.023241581438247116\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 17,\n      \"attempt_id\": \"20260725T011533-0b5ec77c\",\n      \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n      \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n      \"evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\",\n      \"raw_sha256\": \"9934c97547e2cd77de640754c2c51399a66bc96a265f31d38616677ab9973c3d\",\n      \"events_sha256\": \"c15516d15ae525051012e8655817625d37803dda2b8473917720cc5a29ef3043\",\n      \"bound_s\": \"0.028891617940876635\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 18,\n      \"attempt_id\": \"20260725T022712-0a9534f5\",\n      \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n      \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n      \"evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\",\n      \"raw_sha256\": \"bb99b0b7086ee939a8fb789253e2c0502de27a05d056c78d46dc30fccfb862cf\",\n      \"events_sha256\": \"a42487bd9202c043485eebc42a68f505b35faf158c8640f1393d287a1d36e0d1\",\n      \"bound_s\": \"0.029197264796726408\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 19,\n      \"attempt_id\": \"20260725T030533-d3f076e5\",\n      \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n      \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n      \"evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\",\n      \"raw_sha256\": \"26b9ad5ba13e2c73e78ddfdf5be6a2b1cf4b8eb31881aad575ac1bb7ae0dabb9\",\n      \"events_sha256\": \"180a700366e1a97a9e8649a6d98bbd2d814fe9d5fed7246f99b47aa1af5e6b84\",\n      \"bound_s\": \"0.024879191521227362\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 20,\n      \"attempt_id\": \"20260725T055825-b10cb348\",\n      \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n      \"manifest_sha256\": \"eebf3524d9e0b41c022c5e57d4b16787e98302e0d7c28381036415117fafb3ba\",\n      \"evidence_sha256\": \"e0d525e0923f88572f7530f447a3bc8e889ef80a47d662840b86c40b4a35f285\",\n      \"raw_sha256\": \"ed13e60dcfe12d7ce3900798dfbafb7936baa3700cdf58d0f6c1d0fc1790a4b8\",\n      \"events_sha256\": \"fbb3d05c9185ed416d9c138fc63dc32d56b1cd465059007962f9273b53dce671\",\n      \"bound_s\": null,\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: wall_minus_monotonic_span_exceeded\"\n    },\n    {\n      \"n\": 21,\n      \"attempt_id\": \"20260725T060617-97c5cba6\",\n      \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n      \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n      \"evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\",\n      \"raw_sha256\": \"85583f5f07299f38f4f912581e2cfc03453d3a0e85a0de486b3406a355b2c9f2\",\n      \"events_sha256\": \"c904c5f1a1c6557117b6fbde70dc8358dca773f94fc0c611cd50e92c3a3e2ffa\",\n      \"bound_s\": \"0.025045994537554683\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 22,\n      \"attempt_id\": \"20260726T000039-491995f3\",\n      \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n      \"manifest_sha256\": \"b5e1d1195eb8c52bb41211b464909723754e5753bb866ced6f5715d83769ef65\",\n      \"evidence_sha256\": \"9584cd7cdc44e5ba4d176475ce2bf6f70d04e163778fd6e9d5e46cec02303c00\",\n      \"raw_sha256\": \"b916d0b8fc79e8fc7b261c6d608307fbae94bd3c89189e2256cafcf483378c2d\",\n      \"events_sha256\": \"579c2adf45f245dbf31e69b83617fceaf28e63be70677fe0dcd8104a82c79248\",\n      \"bound_s\": \"0.035435840879704805\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer and D-102\"\n    },\n    {\n      \"n\": 23,\n      \"attempt_id\": \"20260726T031222-e0ce33f5\",\n      \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n      \"manifest_sha256\": \"5ec9e27a9bdef89d8e83ca2fd2ee0c1c2d8d2effd56139ac904d1b032c3fc378\",\n      \"evidence_sha256\": \"8d0b2d48460c71d35b2b3b7124b3168c86a497b5a674348451ea5d73931adab3\",\n      \"raw_sha256\": \"c5674ce16dba60b5f0f61ffa5dbe6d7c38bc11747f627e120f6b96af7b9f2fe1\",\n      \"events_sha256\": \"7ba5009ade8a7a870fcb119297dc34a54dcd78f54d13d463e2b4de721db7100b\",\n      \"bound_s\": \"0.023854405254729094\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 24,\n      \"attempt_id\": \"20260726T225227-1f550773\",\n      \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n      \"manifest_sha256\": \"5837bd2c5be6769d63faa57a5d59311241038be7f92de6101b61566b54d89131\",\n      \"evidence_sha256\": \"95941785a8fca5b74019da42d18d280abda639f92442ad57195b852ca567b564\",\n      \"raw_sha256\": \"db6416cada6ea8c0bc84109903fc734d71c0f5a4d8451bafa05a05a76dd7b89d\",\n      \"events_sha256\": \"2de1638cb73fa1a23105a81fe9cdcf9774f467adfcf6fa59bd29029c15a1a9cf\",\n      \"bound_s\": \"0.04916527633725107\",\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 25,\n      \"attempt_id\": \"20260726T225920-ab4272f5\",\n      \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n      \"manifest_sha256\": \"1696f470f0cc543a62cc40a819068a4b7b9f62058fd8d0dd1707870dd25b59e5\",\n      \"evidence_sha256\": \"5b1c9dce56202e1d8af74e71b37aaa1538f0e53fcdded1e05c61cff90f41cda5\",\n      \"raw_sha256\": \"4f83a36625a199a1e5e552953afbdc004bd5144756c8aa2bf657c8c714b4453f\",\n      \"events_sha256\": \"dc704274c1c608a3a87387575c7a36e868c988f9737b033775f55d12791f80f5\",\n      \"bound_s\": \"0.028145704403191807\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 26,\n      \"attempt_id\": \"20260727T015824-45feb516\",\n      \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n      \"manifest_sha256\": \"a7ac96e151419313594510f7511071cbdd710a1ab0837fef25a792ccc1b38d48\",\n      \"evidence_sha256\": \"96f2af22ae5b18ba70f08ec2ed40c54abe0934508ae0d7cfb8fadb9de19432d8\",\n      \"raw_sha256\": \"d0f8ab38ade1df00d957597f6ae0bfdffce047d8611416ecb434f91c4e35ae47\",\n      \"events_sha256\": \"c75224662805694c090f458e6462f8a69581e39e7cf9a4f03d1c3d3b2ae7a371\",\n      \"bound_s\": \"0.029425288011457773\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 27,\n      \"attempt_id\": \"20260727T020611-4a409a30\",\n      \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n      \"manifest_sha256\": \"dc30e9df75b0e4bc561c6f9d641ed3dff696697508333de6707d354151bd96ec\",\n      \"evidence_sha256\": \"e3f4df9cf8bf4f1edfacbd10072bd53c5c1b59a873e4c25ee1727d74307ab3f8\",\n      \"raw_sha256\": \"0961bf040013bf35d7d9fd2e5ad4b9d212d0dab9d733357c5193569ba7b92acd\",\n      \"events_sha256\": \"bea8ab60b84b2ff7e00eff035c1187c837f26fdc30b91bfd0d4ca8ee6d15ecab\",\n      \"bound_s\": \"0.029339001207750293\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 28,\n      \"attempt_id\": \"20260727T050047-95e2f87e\",\n      \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n      \"manifest_sha256\": \"d572e55594e97a4d4f3fb82295c8ad7aedac68c15c18e7615f3ac13e91ebea8a\",\n      \"evidence_sha256\": \"2d70134135398b613638ae6ec62607913026c7d0cdfa9da1dfc77c657fa0e091\",\n      \"raw_sha256\": \"b439d5bc06855943055795db69117ab612866d397eef219d73e0a576545b06c5\",\n      \"events_sha256\": \"a90f500e118b1e88041167fb9fb3808ae0e27b83fa5b664f63c98adecf1ae7a1\",\n      \"bound_s\": \"0.028854562420070173\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 29,\n      \"attempt_id\": \"20260729T204105-39d25f8a\",\n      \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n      \"manifest_sha256\": \"3aec4fc319e1de5a3b34d3552774ee4cf59ad9b1134001c8176d538f1304871f\",\n      \"evidence_sha256\": \"4323c8c5242812b95e544213367dd75f0bc927605d73c78c1a491a84dd829026\",\n      \"raw_sha256\": \"4f0cd62a013d6cc639e11637e425b8e09af02703828d4d0e9638a30ef70e88fc\",\n      \"events_sha256\": \"0ef0f3e5779fb6b1aec6bb48fb60a76c175106b192f16f8aeaf95e3961b75c59\",\n      \"bound_s\": \"0.031467745880268516\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 30,\n      \"attempt_id\": \"20260730T014035-124df355\",\n      \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n      \"manifest_sha256\": \"bb894782e7dd95d38576514fe9360335552129d6de116e2a05a82c17a70702f5\",\n      \"evidence_sha256\": \"f8946df7f5495d6e5c64f90490b94ca2eab94f10ed16b7298e5741dadbe182b1\",\n      \"raw_sha256\": \"95d50522d5eef61dbf2b9b815dce3f62e8791fe417942883908dde762351332b\",\n      \"events_sha256\": \"d66899983a1d8e7b4bc7ecb11c5740534e101f4fbdd2810dd41ff00910277379\",\n      \"bound_s\": \"0.027788174032371493\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 31,\n      \"attempt_id\": \"20260730T210703-f76b5771\",\n      \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n      \"manifest_sha256\": \"e40353dfd883d773414378893f27bc617cfa972f62793b0f35cc9efa30ed7d44\",\n      \"evidence_sha256\": \"0f5e3ea38ff0f833840895e065941494c71c4cd9bf0fe222a9e08ca24ddc3ed8\",\n      \"raw_sha256\": \"718b9046d134fc2a9f089818ea2e5c3aac05c10f056f942c8702ec3b4cdabf75\",\n      \"events_sha256\": \"aaf29ec68222439453b790725b6849040c3f7c1cb5accf096d3a722edebf9664\",\n      \"bound_s\": \"0.026131301462788137\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 32,\n      \"attempt_id\": \"20260731T012210-374020b6\",\n      \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n      \"manifest_sha256\": \"f64a179f03a6b3efecaea6e3ad8ff08ba8c354b9f57023f0929781fd2d133545\",\n      \"evidence_sha256\": \"21a6296fc74542a6400ab5562376b9bf969a1d906c8f9076f89dc9916cef1b52\",\n      \"raw_sha256\": \"0f3b509c48e42a9cbcf32ac3a446d9c13d38766328f9569a96d397a685ad2f2d\",\n      \"events_sha256\": \"624b9c26e71648272e36c85fa7884aa258851039a7e77a7be123e1290d2c4b79\",\n      \"bound_s\": \"0.024850427856341006\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 33,\n      \"attempt_id\": \"20260731T161713-b8b08280\",\n      \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n      \"manifest_sha256\": \"e65aed76d770fbcd9c07b6c2dc26335ddf593533ff1ab6a46cb1bc9bdd119d0a\",\n      \"evidence_sha256\": \"2cda4856ae7939067f0a6ebbbdb865871e437e1c652b0dd438e33cb5ffef1583\",\n      \"raw_sha256\": \"464f5f9ca38818544e54061407251ef3d13541c90c8e5c6f05ee54fe8a913068\",\n      \"events_sha256\": \"2bfd2ac5f0ba88e02a89dbc070837ce3bb1161b2d3067a6176e720bb778b4df1\",\n      \"bound_s\": \"0.030972654450356962\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 34,\n      \"attempt_id\": \"20260731T214355-126fc2ab\",\n      \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n      \"manifest_sha256\": \"ad3aa2345df71df05fb5913ef52210443eb07cfbbb5824e48794b6892557848d\",\n      \"evidence_sha256\": \"1958d58c35dfa30c18671abafcddf3d43c9328f586ce2051d1fb83ab99b51d5f\",\n      \"raw_sha256\": \"c14ef61161fc9bf463840d5f62e1cdcd9bc2fe586297e5d89a6334e19f8dd21f\",\n      \"events_sha256\": \"89808fe44225b7870585a1f2883ff43b01ec0b02507775900ada0a60251f145c\",\n      \"bound_s\": null,\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 35,\n      \"attempt_id\": \"20260801T010113-e859f3aa\",\n      \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n      \"manifest_sha256\": \"52aa9e9b4485a352d1ba2bd40e500f71cab989967d1db6e7a130fe9c157e0647\",\n      \"evidence_sha256\": \"6c350a69406f92f4f1d68e30684f6b36b2f233fba5f52070a73f23c3d767fd45\",\n      \"raw_sha256\": \"1302b53b6aeab97ee57b35cda8003ffb6d107265979614880910c24fdbbb5e7c\",\n      \"events_sha256\": \"887ea9f6bc663ac5bc8cfe1c6d898262a2089602406186f83ff0f750983a841b\",\n      \"bound_s\": \"0.41198917978147415\",\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 36,\n      \"attempt_id\": \"20260801T010805-ff3fdc88\",\n      \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n      \"manifest_sha256\": \"fd5906ccd884670c9d40a57e7b8b4755357bc91c89f281449a080fe5c2007402\",\n      \"evidence_sha256\": \"62967d66a74467735011f159a523f50b6409287bf96899446e4a02fa2c8e2eed\",\n      \"raw_sha256\": \"c39bc0c6c55a3deabdffdf8bfdad95e061fb464def586edafdc19dbd1d8ea5c2\",\n      \"events_sha256\": \"10e9035731a2d54a9469c66318568b6f2e91a0ac3fecdbfad94dfb62c22bf0fc\",\n      \"bound_s\": null,\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 37,\n      \"attempt_id\": \"20260801T014059-8c3bfe9e\",\n      \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n      \"manifest_sha256\": \"7d2967b125324c65e0d57a16950a0e1c2e2946464b7eb89667e8fc2410550149\",\n      \"evidence_sha256\": \"c1653f369e05e9186d0c6d06231993575ee23c1fd813b96f1094d74dfbaac0ad\",\n      \"raw_sha256\": \"f1a9350cbfdb0ec4c0a909b5d2b77798e16f754132499602b426a1068274465f\",\n      \"events_sha256\": \"33f78ee6e299643d8f5929fc2e339f3e13959eb6983a7db8b8af4bd936a0700d\",\n      \"bound_s\": \"0.032786870825707914\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 38,\n      \"attempt_id\": \"20260801T064830-c76f5d1c\",\n      \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n      \"manifest_sha256\": \"6127f706081c4686164ecca83032ab86bdc467170d55b24e537255cfdacac4dc\",\n      \"evidence_sha256\": \"4c2752a194dbd1fc39aaf82e11071cccab4283c81f46208657bd849af6c23a06\",\n      \"raw_sha256\": \"dab52b86df50235d78c39ddda87b3f4620b6dfdead9050640184204630cd5b1f\",\n      \"events_sha256\": \"31e245dcaf050740a69f52ab3afa1783e2081e43a089dc57045be6039f7503e6\",\n      \"bound_s\": \"0.0350400833260715\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer\"\n    }\n  ],\n  \"raw_physics_method\": {\n    \"valid_members\": \"Used verify_stored_evidence_physics, which rejects stored-status substitution, re-derives the causal anchor, reconstructs all pulse commands from events.jsonl, re-fits all 59 pulses, requires complete detection/no spurious plateaus/no reasons, checks every stored residual enclosure contains the refit, and returns max(stored,fresh) bound.\",\n    \"valid_method_source\": \"joulewise/powermetrics_fiducial.py:1088-1164; docs/contracts/powermetrics_fiducial.md:183-211\",\n    \"invalid_members\": \"Re-derived the causal anchor directly from native powermetrics records and recorded ClockStamps. All six independently returned unknown; an unresolved own anchor is forced invalid under the contract.\",\n    \"hash_evidence\": \"Each selected custody manifest's lines 3-6 bind events, instrument evidence, power trace and raw plist. Every listed digest matched the bytes.\"\n  },\n  \"bootstrap_computation\": {\n    \"authoritative_result\": \"NOT COMPUTABLE WITHOUT RULING/IMPORT CONTRACT\",\n    \"required_prior_observation_set\": \"The exact 38 content IDs in per_member, each with epoch_id=d079_epoch and the final ruled disposition. No additional fixture-known-holdout row is evidenced by a real content bundle; configs/calibration/calibration_acceptance_d079_v2.json:222 is explicitly fixture data.\",\n    \"receipt_algorithm_from_schema\": [\n      \"receipt_core is canonical JSON with sorted keys, separators ',' and ':', UTF-8, allow_nan=false; receipt_digest=sha256(receipt_core). See joulewise/calibration_ledger.py:94-105,155-160.\",\n      \"Each receipt contains sequence, predecessor_digest, event, attempt_id, content_id, artifact hashes, six-field epoch, full T1, capture lexeme, exact bound lexeme, disposition and custody locator. See joulewise/calibration_ledger.py:590-622.\",\n      \"The parser requires a reservation before each finalization. See joulewise/calibration_ledger.py:409-465 and finalize_attempt_receipt at :716-777.\",\n      \"The head pin is the final receipt's sequence and receipt_digest with ledger_schema. See joulewise/calibration_ledger.py:780-789.\"\n    ],\n    \"conditional_non_authoritative_replays\": [\n      {\n        \"assumptions\": \"Attempt IDs sorted ascending; one synthetic reservation immediately followed by one finalization per content ID; first hash-complete custody copy selected; candidate-tool mapping of all stored-valid rows to valid and stored-invalid rows to ordinary-invalid.\",\n        \"sequence\": 76,\n        \"head_digest\": \"cb410907660ed8a120d4e1d04a7e9af489b69d83686a8bf7658b3f73e7e3335a\",\n        \"prior_observation_rows_sha256\": \"d29404feea08496453538d8b3994af1c4b64c12a86b950a3aa96a604cb6690c6\",\n        \"dispositions\": {\n          \"valid\": 32,\n          \"ordinary-invalid\": 6\n        },\n        \"warning\": \"Illustrative only; the assumptions are not authorized by D-109 or an import schema.\"\n      },\n      {\n        \"assumptions\": \"Same ordering/custody rules, but apply the production writer's preflight-screen mapping to members 22 and 38.\",\n        \"sequence\": 76,\n        \"head_digest\": \"8e80b6e93804df098f9fbec66740757073d235019e19990c7a9d8270b28337f1\",\n        \"prior_observation_rows_sha256\": \"f28ddf8e0995230857c7e7db11c031084e18e8919ea1b9b373ae2112a9a936bf\",\n        \"dispositions\": {\n          \"valid\": 30,\n          \"systematic-invalid\": 2,\n          \"ordinary-invalid\": 6\n        },\n        \"warning\": \"Illustrative only; differs from D-109 R2.8's stated six-further consequence.\"\n      }\n    ],\n    \"additional_implementation_gap\": \"append_pending_receipt requires the current physical ledger head to equal the committed pin before each new reservation (joulewise/calibration_ledger.py:673-690). Once one reservation/finalization pair advances the physical ledger, another reservation cannot be appended under the unchanged genesis pin. A batch bootstrap/import route is therefore required; none exists.\"\n  },\n  \"derivation_corpus\": {\n    \"n\": 19,\n    \"unchanged\": true,\n    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:46-183\",\n    \"artifact_file_sha256\": \"9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb\",\n    \"stored_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n    \"computed_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n    \"match\": true,\n    \"reconstructed_statistics\": {\n      \"minimum_s\": \"0.022741007370546462\",\n      \"minimum_member\": \"20260722T215127-eeef661a\",\n      \"maximum_s\": \"0.03355875667989999\",\n      \"maximum_member\": \"20260722T222332-901c5c13\",\n      \"range_s\": \"0.010817749309353528\",\n      \"mean_s\": \"0.026950033977532761\",\n      \"sample_sd_s\": \"0.002970761365307205\"\n    },\n    \"note\": \"The current derivation_sha256 covers the complete artifact core excluding the hash field, not only the n=19 table (joulewise/calibration_bracketing.py:155-177). Issuance edits will therefore require a new canonical hash even though the threshold-producing n=19 remains unchanged.\"\n  },\n  \"D102_corpus_doubling\": {\n    \"binding_rule\": \"38 total authenticated, content-distinct, valid same-epoch observations\",\n    \"implementation_source\": \"joulewise/calibration_bracketing.py:901-908\",\n    \"candidate_tool_disposition_result\": {\n      \"current_valid_total\": 32,\n      \"additional_valid_needed\": 6,\n      \"trigger_now\": false,\n      \"matches_D109_R2_8\": true\n    },\n    \"production_writer_disposition_result\": {\n      \"current_valid_total\": 30,\n      \"additional_valid_needed\": 8,\n      \"trigger_now\": false,\n      \"matches_D109_R2_8\": false\n    },\n    \"decision\": \"BLOCKED pending the B1 disposition ruling. The report does not choose between these counts.\"\n  },\n  \"verification\": [\n    {\n      \"id\": \"V1\",\n      \"result\": \"PASS\",\n      \"check\": \"Enumerated runs*/instrument_validation manifests, exact six-field epoch filtered, canonical content IDs recomputed.\",\n      \"observed\": \"53 checkout custody copies; 38 distinct IDs; stored labels 32 valid/6 invalid.\"\n    },\n    {\n      \"id\": \"V2\",\n      \"result\": \"PASS\",\n      \"check\": \"For every selected representative, rehashed every manifest-listed artifact and every evidence-internal artifact hash.\",\n      \"observed\": \"Zero missing or mismatched bytes.\"\n    },\n    {\n      \"id\": \"V3\",\n      \"result\": \"PASS\",\n      \"check\": \"Replayed strict raw physics for every candidate-valid observation and causal-anchor physics for every candidate-invalid observation.\",\n      \"observed\": \"32 VERIFIED-VALID; 6 VERIFIED-INVALID; 0 raw unresolved.\"\n    },\n    {\n      \"id\": \"V4\",\n      \"result\": \"PASS\",\n      \"check\": \"PYTHONDONTWRITEBYTECODE=1 python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact configs/calibration/calibration_acceptance_d079_v2.json\",\n      \"observed\": \"PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK; n=19 statistics reproduced.\"\n    },\n    {\n      \"id\": \"V5\",\n      \"result\": \"PASS\",\n      \"check\": \"Canonical artifact-core SHA-256 recomputation.\",\n      \"observed\": \"stored=computed=3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d.\"\n    },\n    {\n      \"id\": \"V6\",\n      \"result\": \"PASS\",\n      \"check\": \"Final git status.\",\n      \"observed\": \"## main...origin/main; no changes.\"\n    }\n  ],\n  \"flags\": [\n    {\n      \"id\": \"NO_EDITS\",\n      \"level\": \"informational\",\n      \"text\": \"Read-only verification; no artifact, ledger, pin, report or state file was created or modified.\"\n    },\n    {\n      \"id\": \"ISSUANCE_BLOCKED\",\n      \"level\": \"blocking\",\n      \"text\": \"Lead must first rule the two high-bound dispositions and authorize a deterministic historical-import/bootstrap contract, including ordering and custody selection. Only then can one exact prior_observation_set, sequence and head digest be issued.\"\n    }\n  ],\n  \"next_exact_step\": \"Lead rules whether members 20260726T000039-491995f3 and 20260801T064830-c76f5d1c are ledger-valid or systematic-invalid, then specifies the authenticated batch-import ordering/custody rule. Recompute the single resulting 76-receipt chain, review its exact head, and only in a separately authorized write session bootstrap the ledger, update and commit the head pin, and issue the acceptance artifact.\"\n}\n```","numLines":730,"startLine":1,"totalLines":730}},"sourceToolAssistantUUID":"95303f9d-7523-4544-89e9-e0e2c5aa3014","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
7899:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-batch-concurrency-energy.md:5511:docs/process_traces/2026-08-06-d079-issuance-coldgate/COLDGATE2-FABLE-transcript.jsonl:11:{"parentUuid":"e07187f2-62a1-40a1-856e-b8be22861d57","isSidechain":true,"promptId":"70846291-da47-443c-8a9a-b0e660a3b23b","agentId":"a46e6644985dd75fd","type":"user","message":{"role":"user","content":[{"tool_use_id":"toolu_015ZCGto8giwKkf5gfLXLBT7","type":"tool_result","content":"1\t```json\n2\t{\n3\t  \"schema\": \"claude-codex-report/v1\",\n4\t  \"genre\": \"verification\",\n5\t  \"status\": \"findings\",\n6\t  \"completion\": \"complete\",\n7\t  \"summary\": \"BLOCKED. All 38 content-distinct candidates were recovered, hash-authenticated, epoch-checked, and replayed from raw physics: 32 VERIFIED-VALID and 6 VERIFIED-INVALID, with no missing raw evidence. Issuance is not ready because two verified-valid observations exceed the systematic-failure screen and therefore lack an unambiguous ledger disposition, and the repository does not specify a deterministic authenticated historical-import/bootstrap transaction from which one authoritative sequence/head digest can be computed.\",\n8\t  \"workspace\": {\n9\t    \"head_start\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n10\t    \"head_end\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n11\t    \"branch\": \"main\",\n12\t    \"pathspec\": [],\n13\t    \"unowned_dirty\": [],\n14\t    \"write_scope\": \"none\",\n15\t    \"edits\": \"none\"\n16\t  },\n17\t  \"verdict\": {\n18\t    \"overall\": \"BLOCKED\",\n19\t    \"prompt_vs_R2_divergence\": false,\n20\t    \"raw_member_results\": {\n21\t      \"VERIFIED-VALID\": 32,\n22\t      \"VERIFIED-INVALID\": 6,\n23\t      \"UNRESOLVED\": 0\n24\t    },\n25\t    \"blocking_items\": [\n26\t      {\n27\t        \"id\": \"B1\",\n28\t        \"type\": \"ledger_disposition_ruling\",\n29\t        \"members\": [\n30\t          \"20260726T000039-491995f3\",\n31\t          \"20260801T064830-c76f5d1c\"\n32\t        ],\n33\t        \"reason\": \"Both replay as physically valid, matching the candidate inventory, but their bounds 0.035435840879704805 and 0.0350400833260715 exceed the ratified 0.033558756679900 preflight screen. The production writer maps such a valid capture to systematic-invalid at scripts/validate_powermetrics_fiducial.py:664-671; D-102 explicitly calls the first member a systematic failure at docs/decision_log.md:6298-6301. The backfill candidate tool instead proposes valid solely from stored status at scripts/calibration_ledger_backfill.py:58-63. Selecting either disposition is lead-owned.\"\n34\t      },\n35\t      {\n36\t        \"id\": \"B2\",\n37\t        \"type\": \"bootstrap_contract_gap\",\n38\t        \"members\": \"all 38\",\n39\t        \"reason\": \"No historical-import/bootstrap API, receipt ordering, duplicate-custody selection rule, or import-transaction schema exists. The candidate tool emits only an unauthoritative candidate set and never appends the ledger (scripts/calibration_ledger_backfill.py:2-7,90-117). Because receipt digests bind sequence, predecessor, disposition, artifact hashes and absolute custody locator (joulewise/calibration_ledger.py:590-622), more than one valid head digest is possible.\"\n40\t      }\n41\t    ]\n42\t  },\n43\t  \"binding_clauses\": [\n44\t    {\n45\t      \"clause\": \"D-109 R1.4\",\n46\t      \"source\": \"docs/decision_log.md:7027-7039\",\n47\t      \"verbatim\": \"4. The acceptance artifact pins its baseline ledger head. Evaluation ALSO requires the independent current-head pin (clause below), verifies one complete non-forked chain extension from baseline to current, and threads ONE immutable ledger snapshot through every consumer path (session, direct runner path, secondary verifier) — repeated independent loads are a refusal-grade defect. Anti-rollback authority: a REPO-COMMITTED head-pin file `{sequence, head_digest, ledger_schema}` (existing checked-in byte-pin trust model; no second trusted latest-sequence store). Rotation is epoch-bounded — at most one lead-controlled quiet-machine collection session — and NO claim evaluation may occur between ledger advancement and pin commit; a physical head differing from the committed pin refuses.\",\n48\t      \"verification_plan\": \"After an authorized bootstrap, recompute every receipt digest, require one linear chain, require the artifact cutoff to equal an exact receipt, require the physical head to equal the separately committed pin, and trace one snapshot object through every consumer. This session verified the implemented digest/head machinery but could not select an authoritative bootstrap head because no import transaction is specified.\"\n49\t    },\n50\t    {\n51\t      \"clause\": \"D-109 R2.1\",\n52\t      \"source\": \"docs/decision_log.md:7053\",\n53\t      \"verbatim\": \"1. The issuance cutoff is an exact ledger sequence + head digest.\",\n54\t      \"verification_plan\": \"Compute the final receipt count and digest only after disposition, ordering and custody-locator rules are fixed. Current fixture cutoff remains non-production genesis sequence 0/all-zero digest at configs/calibration/calibration_acceptance_d079_v2.json:14-18.\"\n55\t    },\n56\t    {\n57\t      \"clause\": \"D-109 R2.2\",\n58\t      \"source\": \"docs/decision_log.md:7054-7055\",\n59\t      \"verbatim\": \"2. `derivation_corpus` remains exactly the n=19 threshold-producing observations.\",\n60\t      \"verification_plan\": \"Re-run the corpus verifier against all 19 pinned member manifest/evidence hashes and recompute the decimal statistics and artifact canonical hash. Result: PASS.\"\n61\t    },\n62\t    {\n63\t      \"clause\": \"D-109 R2.3\",\n64\t      \"source\": \"docs/decision_log.md:7056-7060\",\n65\t      \"verbatim\": \"3. `prior_observation_set` = every content-distinct governed observation known at the cutoff — valid, systematic-invalid, ordinary-invalid, blind holdout, and unresolved — with epoch and disposition recorded separately. (The current artifact's two ID-only `blind_exclusions` are insufficient and are superseded.)\",\n66\t      \"verification_plan\": \"Enumerate every exact-epoch validation tree, collapse copies by canonical content ID, authenticate the raw bytes, and assign one epoch plus one ruled disposition per content ID. The 38 identities are complete for the located candidate, but two dispositions require a ruling.\"\n67\t    },\n68\t    {\n69\t      \"clause\": \"D-109 R2.4\",\n70\t      \"source\": \"docs/decision_log.md:7061-7063\",\n71\t      \"verbatim\": \"4. Content identity is path-independent, derived from canonical primary-byte hashes; attempt identity is separate; copies do not create new observations.\",\n72\t      \"verification_plan\": \"Hash manifest.json and instrument_evidence.json bytes, canonical-JSON encode the two-name hash map, SHA-256 it, and collapse identical IDs. Implementation is joulewise/calibration_ledger.py:94-105,120-134. Result: 53 checkout copies collapse to 38 IDs.\"\n73\t    },\n74\t    {\n75\t      \"clause\": \"D-109 R2.5\",\n76\t      \"source\": \"docs/decision_log.md:7064-7068\",\n77\t      \"verbatim\": \"5. \\\"New\\\" (trigger population) = current authentic content IDs − `prior_observation_set`, regardless of capture timestamp or source root; a previously unknown historical artifact IS new when discovered. Every new observation is judged under the PRIOR artifact (D-102's prospective rule).\",\n78\t      \"verification_plan\": \"After issuance, subtract the exact 38-ID prior set from the authenticated ledger snapshot, independent of path/time, before applying triggers. The implemented subtraction is at joulewise/calibration_bracketing.py:870-893.\"\n79\t    },\n80\t    {\n81\t      \"clause\": \"D-109 R2.6\",\n82\t      \"source\": \"docs/decision_log.md:7069-7070\",\n83\t      \"verbatim\": \"6. New unresolved or unclassifiable attempts cause refusal; only after trigger disposition may a successor artifact absorb them.\",\n84\t      \"verification_plan\": \"Require every post-cutoff receipt to classify as valid, systematic-invalid or ordinary-invalid; unresolved/abandoned/null-content rows must refuse. Implemented refusal is at joulewise/calibration_bracketing.py:895-900.\"\n85\t    },\n86\t    {\n87\t      \"clause\": \"D-109 R2.7\",\n88\t      \"source\": \"docs/decision_log.md:7071-7074\",\n89\t      \"verbatim\": \"7. The 32-valid/6-invalid same-epoch inventory is a backfill CANDIDATE, not a ratified classification: identities may seed the backfill, but dispositions require raw-physics + hash verification before issuance, and any unresolved member blocks issuance.\",\n90\t      \"verification_plan\": \"For all 38 members: verify manifest and evidence hashes, verify raw/event hashes, replay causal clock-anchor derivation and the strict 59-pulse detector, verify the six-field epoch, then compare with candidate labeling. Result: 32 VERIFIED-VALID, 6 VERIFIED-INVALID, zero raw-physics unresolved; two final ledger dispositions remain ambiguous.\"\n91\t    },\n92\t    {\n93\t      \"clause\": \"D-109 R2.8\",\n94\t      \"source\": \"docs/decision_log.md:7075-7079\",\n95\t      \"verbatim\": \"8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38 TOTAL authenticated, content-distinct, VALID same-epoch observations — including previously blind observations once unblinded — not 38 post-cutoff observations. Under the candidate inventory, six further valid observations trigger re-derivation.\",\n96\t      \"verification_plan\": \"Count content-distinct ledger observations whose disposition is exactly valid and whose epoch equals d079_epoch. The implementation does this at joulewise/calibration_bracketing.py:901-908. Result is six further only under the candidate-tool 32-valid disposition proposal; it is eight further under the production writer's systematic-screen mapping.\"\n97\t    }\n98\t  ],\n99\t  \"inventory\": {\n100\t    \"where_it_lives\": {\n101\t      \"count_only_authority\": [\n102\t        \"docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:296-308\",\n103\t        \"configs/calibration/calibration_acceptance_d079_v2.json:225-233\"\n104\t      ],\n105\t      \"candidate_emitter\": \"scripts/calibration_ledger_backfill.py:42-117\",\n106\t      \"concrete_membership\": \"Implicit in the 53 exact-epoch validation custody trees under runs*/instrument_validation; no standalone serialized 38-row candidate file exists in the checkout or .desk.\",\n107\t      \"raw_archive\": \"/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup\",\n108\t      \"important_non_inventory\": \"docs/process_traces/2026-08-03-d111-backfill/MANIFEST.md is a manifest of 41 process artifacts, not the 38 calibration observations.\"\n109\t    },\n110\t    \"identity_method\": \"sha256(canonical_json({\\\"instrument_evidence.json\\\": sha256(evidence bytes), \\\"manifest.json\\\": sha256(manifest bytes)}))\",\n111\t    \"identity_method_source\": \"joulewise/calibration_ledger.py:94-105,120-134\",\n112\t    \"checkout_copy_count\": 53,\n113\t    \"content_distinct_count\": 38,\n114\t    \"candidate_label_counts\": {\n115\t      \"valid\": 32,\n116\t      \"invalid\": 6\n117\t    },\n118\t    \"analysis_only_member_set_sha256\": {\n119\t      \"value\": \"7c0ae751e3be9d180c932b14da1cc9b50f85a73a0821de03c7a7911728a25e95\",\n120\t      \"definition\": \"canonical SHA-256 of the ordered 38 candidate rows containing attempt_id, content_id, all artifact hashes, epoch, full T1, capture lexeme and bound lexeme; custody locator deliberately excluded. This digest is verification evidence, not a contract-defined production identity.\"\n121\t    }\n122\t  },\n123\t  \"epoch\": {\n124\t    \"epoch_id\": \"d079_epoch\",\n125\t    \"all_38_match\": true,\n126\t    \"fields\": {\n127\t      \"os_build\": \"25F84\",\n128\t      \"hardware_model\": \"Mac15,9\",\n129\t      \"power_policy\": \"ac_high_power\",\n130\t      \"sampling_interval_ms\": 100,\n131\t      \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n132\t      \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n133\t    },\n134\t    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:20-26,193-200\"\n135\t  },\n136\t  \"per_member\": [\n137\t    {\n138\t      \"n\": 1,\n139\t      \"attempt_id\": \"20260722T145535-e941c821\",\n140\t      \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n141\t      \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n142\t      \"evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\",\n143\t      \"raw_sha256\": \"b55f3471c70c54e0174b09e67486759fc532742e9bd671e53ce8324fe23209ef\",\n144\t      \"events_sha256\": \"605e2330d27f874621edb698c233542d7eb31fb8b8d1def044852a77a223b1bc\",\n145\t      \"bound_s\": \"0.03018980442653224\",\n146\t      \"verdict\": \"VERIFIED-VALID\",\n147\t      \"disposition\": \"valid\"\n148\t    },\n149\t    {\n150\t      \"n\": 2,\n151\t      \"attempt_id\": \"20260722T194118-9dc0749d\",\n152\t      \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n153\t      \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n154\t      \"evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\",\n155\t      \"raw_sha256\": \"aa36a9c1e8451e2a0de875a7ff45232c98bf0cce5cdcd5b827d176ea24aa85f7\",\n156\t      \"events_sha256\": \"0f543eb7f697d442a5c0ddce1fe6f3f69c268c96bdc7a5ffbb6e84f70e8f1d66\",\n157\t      \"bound_s\": \"0.026300679324099796\",\n158\t      \"verdict\": \"VERIFIED-VALID\",\n159\t      \"disposition\": \"valid\"\n160\t    },\n161\t    {\n162\t      \"n\": 3,\n163\t      \"attempt_id\": \"20260722T213749-563b9849\",\n164\t      \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n165\t      \"manifest_sha256\": \"b7dd23cf8a9e30d81a01ba0b3c5c5e0c21b4c325e48e1d02e046fb61b77cb0ac\",\n166\t      \"evidence_sha256\": \"1cc789e9558667e188f1859ba591a584a73eb4d2309612c924eebfb4cf5ffe80\",\n167\t      \"raw_sha256\": \"3684b27080f6b4254d61e1c5b3f0f25e8401257078145331ef2122b2c1893fd1\",\n168\t      \"events_sha256\": \"b179d606c17148e754bba07bb61c3d7a5c094e5a0e701251e7674b45472f5a4b\",\n169\t      \"bound_s\": \"0.2079182387602739\",\n170\t      \"verdict\": \"VERIFIED-INVALID\",\n171\t      \"disposition\": \"ordinary-invalid\",\n172\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n173\t    },\n174\t    {\n175\t      \"n\": 4,\n176\t      \"attempt_id\": \"20260722T214220-1acdbbc0\",\n177\t      \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n178\t      \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n179\t      \"evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\",\n180\t      \"raw_sha256\": \"7a4b62258d4d6afe251c4ed60a02835ac4d2b743f926260b2f621cb2301a72de\",\n181\t      \"events_sha256\": \"6f0c813bf5489f1fce820bddd1160d6936ec5dc6e89f1c3ca2aecdbedc2834af\",\n182\t      \"bound_s\": \"0.03312014638436772\",\n183\t      \"verdict\": \"VERIFIED-VALID\",\n184\t      \"disposition\": \"valid\"\n185\t    },\n186\t    {\n187\t      \"n\": 5,\n188\t      \"attempt_id\": \"20260722T215127-eeef661a\",\n189\t      \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n190\t      \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n191\t      \"evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\",\n192\t      \"raw_sha256\": \"8e275c342b5dde493e24e69f5a30fd7224ec36c21b324bd489508cda5860bff8\",\n193\t      \"events_sha256\": \"30efea52cd15580aa4f4f52b959a4b6a881db0df0f72a488ae4d4493d51a8f75\",\n194\t      \"bound_s\": \"0.022741007370546462\",\n195\t      \"verdict\": \"VERIFIED-VALID\",\n196\t      \"disposition\": \"valid\"\n197\t    },\n198\t    {\n199\t      \"n\": 6,\n200\t      \"attempt_id\": \"20260722T222332-901c5c13\",\n201\t      \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n202\t      \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n203\t      \"evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\",\n204\t      \"raw_sha256\": \"84adafc6e55a45a10e56d5cea6571f1b12dae15656a2a0274822eb96500f4744\",\n205\t      \"events_sha256\": \"1b7ce059e4b72885a77cb398704590e50e51b925cdae7bf77db1ad2b36dd7d59\",\n206\t      \"bound_s\": \"0.03355875667989999\",\n207\t      \"verdict\": \"VERIFIED-VALID\",\n208\t      \"disposition\": \"valid\"\n209\t    },\n210\t    {\n211\t      \"n\": 7,\n212\t      \"attempt_id\": \"20260722T232509-82642517\",\n213\t      \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n214\t      \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n215\t      \"evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\",\n216\t      \"raw_sha256\": \"56555a10ee248cb6e5692280881d3daaf406b0432c2c3d068e06c5b8d8d76e40\",\n217\t      \"events_sha256\": \"1c2b84546ed000dbb6f3378f5a1ef24ae008048209bcffee95644bbad585df6b\",\n218\t      \"bound_s\": \"0.027654085293084385\",\n219\t      \"verdict\": \"VERIFIED-VALID\",\n220\t      \"disposition\": \"valid\"\n221\t    },\n222\t    {\n223\t      \"n\": 8,\n224\t      \"attempt_id\": \"20260723T023058-8732d1c9\",\n225\t      \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n226\t      \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n227\t      \"evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\",\n228\t      \"raw_sha256\": \"49d0b16529d40d6ce7a8d125f9787ab37e46ddfeb6b06e1b69a28e1a7011cf67\",\n229\t      \"events_sha256\": \"962780bf83e89c2e5a4720e074e49f06c0aa49cac3989bed9035436ed734455a\",\n230\t      \"bound_s\": \"0.024753340330112727\",\n231\t      \"verdict\": \"VERIFIED-VALID\",\n232\t      \"disposition\": \"valid\"\n233\t    },\n234\t    {\n235\t      \"n\": 9,\n236\t      \"attempt_id\": \"20260723T052051-d9358c8a\",\n237\t      \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n238\t      \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n239\t      \"evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\",\n240\t      \"raw_sha256\": \"dac05b535d4faa2f8864a2be91a6c56df812b1631fd60aaebde8e680a6aebc8e\",\n241\t      \"events_sha256\": \"7e79ef10b6d9caae132b04ae1e59d584c569aa751084fa02e62e2cad5f794fd3\",\n242\t      \"bound_s\": \"0.025964638697819786\",\n243\t      \"verdict\": \"VERIFIED-VALID\",\n244\t      \"disposition\": \"valid\"\n245\t    },\n246\t    {\n247\t      \"n\": 10,\n248\t      \"attempt_id\": \"20260723T183306-4ce692b4\",\n249\t      \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n250\t      \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n251\t      \"evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\",\n252\t      \"raw_sha256\": \"bcd97c9bd9b0a0686fc84bfa9d117685b6a68f8beed7f84dfa503eacaf78d941\",\n253\t      \"events_sha256\": \"7341d55729c2a3ebf68739900105893b5f2d59bb55d57092ef20e2b94d6c95ca\",\n254\t      \"bound_s\": \"0.027262160888545217\",\n255\t      \"verdict\": \"VERIFIED-VALID\",\n256\t      \"disposition\": \"valid\"\n257\t    },\n258\t    {\n259\t      \"n\": 11,\n260\t      \"attempt_id\": \"20260723T194632-d04e038e\",\n261\t      \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n262\t      \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n263\t      \"evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\",\n264\t      \"raw_sha256\": \"b1660d10fcc5015f0ccc0e4e0a7464db3a5220d415c952f3d9635e512faab57c\",\n265\t      \"events_sha256\": \"a965e301af8f2cb662dca60a7b9706d9b6e7dbabdc6971abd3119c46fc7711d6\",\n266\t      \"bound_s\": \"0.024593263907495888\",\n267\t      \"verdict\": \"VERIFIED-VALID\",\n268\t      \"disposition\": \"valid\"\n269\t    },\n270\t    {\n271\t      \"n\": 12,\n272\t      \"attempt_id\": \"20260723T195730-bc4ba14a\",\n273\t      \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n274\t      \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n275\t      \"evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\",\n276\t      \"raw_sha256\": \"81669d5e0e81ccb1d05ae7d19befffbf41441a92a1e14f0dcb8c0b8d9b6f7a86\",\n277\t      \"events_sha256\": \"0343c61d357465919f99b13000e39f02b43575c68c5383e1f03ffc46a3a2ee24\",\n278\t      \"bound_s\": \"0.025305226022515448\",\n279\t      \"verdict\": \"VERIFIED-VALID\",\n280\t      \"disposition\": \"valid\"\n281\t    },\n282\t    {\n283\t      \"n\": 13,\n284\t      \"attempt_id\": \"20260723T221449-e9ae755e\",\n285\t      \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n286\t      \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n287\t      \"evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\",\n288\t      \"raw_sha256\": \"4e971efc4abef1f51a636a095fa807d1b395ed8342f5e7386aead5e9c466ce50\",\n289\t      \"events_sha256\": \"1caf0be478a75308070e0a93818618af2dd8ca69f51bd2e35f1994c5b7f9b2d0\",\n290\t      \"bound_s\": \"0.027702588281732055\",\n291\t      \"verdict\": \"VERIFIED-VALID\",\n292\t      \"disposition\": \"valid\"\n293\t    },\n294\t    {\n295\t      \"n\": 14,\n296\t      \"attempt_id\": \"20260723T223406-314f6d9e\",\n297\t      \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n298\t      \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n299\t      \"evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\",\n300\t      \"raw_sha256\": \"2c92bf2a3065493b00caf678a5ee8d78c93d3dba406979cb824058b355274f73\",\n301\t      \"events_sha256\": \"4a4a990161e35f05d9fbd36c1eb52f78c46551145348036e073aa2494519df29\",\n302\t      \"bound_s\": \"0.026173651901677253\",\n303\t      \"verdict\": \"VERIFIED-VALID\",\n304\t      \"disposition\": \"valid\"\n305\t    },\n306\t    {\n307\t      \"n\": 15,\n308\t      \"attempt_id\": \"20260724T014109-57844352\",\n309\t      \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n310\t      \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n311\t      \"evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\",\n312\t      \"raw_sha256\": \"9c806bcd26a0f6cce7f33c00d930d803e39f9bd4a6e186971d6123a470a1b13d\",\n313\t      \"events_sha256\": \"221c42b7f214515f9af84c2b9486315df70e3466c66b7beb5bf35e476bf5ae14\",\n314\t      \"bound_s\": \"0.02547564583006129\",\n315\t      \"verdict\": \"VERIFIED-VALID\",\n316\t      \"disposition\": \"valid\"\n317\t    },\n318\t    {\n319\t      \"n\": 16,\n320\t      \"attempt_id\": \"20260725T005132-a64711b7\",\n321\t      \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n322\t      \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n323\t      \"evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\",\n324\t      \"raw_sha256\": \"a22005ea981f8e3ac1f3ea65cfa6bd1d0777dc009203b5e2db73cce44d2aca4e\",\n325\t      \"events_sha256\": \"459dc8a3ec34eb7a3f2095d0c5b72e931f8d87199fd48812386684f36162f617\",\n326\t      \"bound_s\": \"0.023241581438247116\",\n327\t      \"verdict\": \"VERIFIED-VALID\",\n328\t      \"disposition\": \"valid\"\n329\t    },\n330\t    {\n331\t      \"n\": 17,\n332\t      \"attempt_id\": \"20260725T011533-0b5ec77c\",\n333\t      \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n334\t      \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n335\t      \"evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\",\n336\t      \"raw_sha256\": \"9934c97547e2cd77de640754c2c51399a66bc96a265f31d38616677ab9973c3d\",\n337\t      \"events_sha256\": \"c15516d15ae525051012e8655817625d37803dda2b8473917720cc5a29ef3043\",\n338\t      \"bound_s\": \"0.028891617940876635\",\n339\t      \"verdict\": \"VERIFIED-VALID\",\n340\t      \"disposition\": \"valid\"\n341\t    },\n342\t    {\n343\t      \"n\": 18,\n344\t      \"attempt_id\": \"20260725T022712-0a9534f5\",\n345\t      \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n346\t      \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n347\t      \"evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\",\n348\t      \"raw_sha256\": \"bb99b0b7086ee939a8fb789253e2c0502de27a05d056c78d46dc30fccfb862cf\",\n349\t      \"events_sha256\": \"a42487bd9202c043485eebc42a68f505b35faf158c8640f1393d287a1d36e0d1\",\n350\t      \"bound_s\": \"0.029197264796726408\",\n351\t      \"verdict\": \"VERIFIED-VALID\",\n352\t      \"disposition\": \"valid\"\n353\t    },\n354\t    {\n355\t      \"n\": 19,\n356\t      \"attempt_id\": \"20260725T030533-d3f076e5\",\n357\t      \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n358\t      \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n359\t      \"evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\",\n360\t      \"raw_sha256\": \"26b9ad5ba13e2c73e78ddfdf5be6a2b1cf4b8eb31881aad575ac1bb7ae0dabb9\",\n361\t      \"events_sha256\": \"180a700366e1a97a9e8649a6d98bbd2d814fe9d5fed7246f99b47aa1af5e6b84\",\n362\t      \"bound_s\": \"0.024879191521227362\",\n363\t      \"verdict\": \"VERIFIED-VALID\",\n364\t      \"disposition\": \"valid\"\n365\t    },\n366\t    {\n367\t      \"n\": 20,\n368\t      \"attempt_id\": \"20260725T055825-b10cb348\",\n369\t      \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n370\t      \"manifest_sha256\": \"eebf3524d9e0b41c022c5e57d4b16787e98302e0d7c28381036415117fafb3ba\",\n371\t      \"evidence_sha256\": \"e0d525e0923f88572f7530f447a3bc8e889ef80a47d662840b86c40b4a35f285\",\n372\t      \"raw_sha256\": \"ed13e60dcfe12d7ce3900798dfbafb7936baa3700cdf58d0f6c1d0fc1790a4b8\",\n373\t      \"events_sha256\": \"fbb3d05c9185ed416d9c138fc63dc32d56b1cd465059007962f9273b53dce671\",\n374\t      \"bound_s\": null,\n375\t      \"verdict\": \"VERIFIED-INVALID\",\n376\t      \"disposition\": \"ordinary-invalid\",\n377\t      \"raw_reason\": \"fresh causal anchor unknown: wall_minus_monotonic_span_exceeded\"\n378\t    },\n379\t    {\n380\t      \"n\": 21,\n381\t      \"attempt_id\": \"20260725T060617-97c5cba6\",\n382\t      \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n383\t      \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n384\t      \"evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\",\n385\t      \"raw_sha256\": \"85583f5f07299f38f4f912581e2cfc03453d3a0e85a0de486b3406a355b2c9f2\",\n386\t      \"events_sha256\": \"c904c5f1a1c6557117b6fbde70dc8358dca773f94fc0c611cd50e92c3a3e2ffa\",\n387\t      \"bound_s\": \"0.025045994537554683\",\n388\t      \"verdict\": \"VERIFIED-VALID\",\n389\t      \"disposition\": \"valid\"\n390\t    },\n391\t    {\n392\t      \"n\": 22,\n393\t      \"attempt_id\": \"20260726T000039-491995f3\",\n394\t      \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n395\t      \"manifest_sha256\": \"b5e1d1195eb8c52bb41211b464909723754e5753bb866ced6f5715d83769ef65\",\n396\t      \"evidence_sha256\": \"9584cd7cdc44e5ba4d176475ce2bf6f70d04e163778fd6e9d5e46cec02303c00\",\n397\t      \"raw_sha256\": \"b916d0b8fc79e8fc7b261c6d608307fbae94bd3c89189e2256cafcf483378c2d\",\n398\t      \"events_sha256\": \"579c2adf45f245dbf31e69b83617fceaf28e63be70677fe0dcd8104a82c79248\",\n399\t      \"bound_s\": \"0.035435840879704805\",\n400\t      \"verdict\": \"VERIFIED-VALID\",\n401\t      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer and D-102\"\n402\t    },\n403\t    {\n404\t      \"n\": 23,\n405\t      \"attempt_id\": \"20260726T031222-e0ce33f5\",\n406\t      \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n407\t      \"manifest_sha256\": \"5ec9e27a9bdef89d8e83ca2fd2ee0c1c2d8d2effd56139ac904d1b032c3fc378\",\n408\t      \"evidence_sha256\": \"8d0b2d48460c71d35b2b3b7124b3168c86a497b5a674348451ea5d73931adab3\",\n409\t      \"raw_sha256\": \"c5674ce16dba60b5f0f61ffa5dbe6d7c38bc11747f627e120f6b96af7b9f2fe1\",\n410\t      \"events_sha256\": \"7ba5009ade8a7a870fcb119297dc34a54dcd78f54d13d463e2b4de721db7100b\",\n411\t      \"bound_s\": \"0.023854405254729094\",\n412\t      \"verdict\": \"VERIFIED-VALID\",\n413\t      \"disposition\": \"valid\"\n414\t    },\n415\t    {\n416\t      \"n\": 24,\n417\t      \"attempt_id\": \"20260726T225227-1f550773\",\n418\t      \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n419\t      \"manifest_sha256\": \"5837bd2c5be6769d63faa57a5d59311241038be7f92de6101b61566b54d89131\",\n420\t      \"evidence_sha256\": \"95941785a8fca5b74019da42d18d280abda639f92442ad57195b852ca567b564\",\n421\t      \"raw_sha256\": \"db6416cada6ea8c0bc84109903fc734d71c0f5a4d8451bafa05a05a76dd7b89d\",\n422\t      \"events_sha256\": \"2de1638cb73fa1a23105a81fe9cdcf9774f467adfcf6fa59bd29029c15a1a9cf\",\n423\t      \"bound_s\": \"0.04916527633725107\",\n424\t      \"verdict\": \"VERIFIED-INVALID\",\n425\t      \"disposition\": \"ordinary-invalid\",\n426\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n427\t    },\n428\t    {\n429\t      \"n\": 25,\n430\t      \"attempt_id\": \"20260726T225920-ab4272f5\",\n431\t      \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n432\t      \"manifest_sha256\": \"1696f470f0cc543a62cc40a819068a4b7b9f62058fd8d0dd1707870dd25b59e5\",\n433\t      \"evidence_sha256\": \"5b1c9dce56202e1d8af74e71b37aaa1538f0e53fcdded1e05c61cff90f41cda5\",\n434\t      \"raw_sha256\": \"4f83a36625a199a1e5e552953afbdc004bd5144756c8aa2bf657c8c714b4453f\",\n435\t      \"events_sha256\": \"dc704274c1c608a3a87387575c7a36e868c988f9737b033775f55d12791f80f5\",\n436\t      \"bound_s\": \"0.028145704403191807\",\n437\t      \"verdict\": \"VERIFIED-VALID\",\n438\t      \"disposition\": \"valid\"\n439\t    },\n440\t    {\n441\t      \"n\": 26,\n442\t      \"attempt_id\": \"20260727T015824-45feb516\",\n443\t      \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n444\t      \"manifest_sha256\": \"a7ac96e151419313594510f7511071cbdd710a1ab0837fef25a792ccc1b38d48\",\n445\t      \"evidence_sha256\": \"96f2af22ae5b18ba70f08ec2ed40c54abe0934508ae0d7cfb8fadb9de19432d8\",\n446\t      \"raw_sha256\": \"d0f8ab38ade1df00d957597f6ae0bfdffce047d8611416ecb434f91c4e35ae47\",\n447\t      \"events_sha256\": \"c75224662805694c090f458e6462f8a69581e39e7cf9a4f03d1c3d3b2ae7a371\",\n448\t      \"bound_s\": \"0.029425288011457773\",\n449\t      \"verdict\": \"VERIFIED-VALID\",\n450\t      \"disposition\": \"valid\"\n451\t    },\n452\t    {\n453\t      \"n\": 27,\n454\t      \"attempt_id\": \"20260727T020611-4a409a30\",\n455\t      \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n456\t      \"manifest_sha256\": \"dc30e9df75b0e4bc561c6f9d641ed3dff696697508333de6707d354151bd96ec\",\n457\t      \"evidence_sha256\": \"e3f4df9cf8bf4f1edfacbd10072bd53c5c1b59a873e4c25ee1727d74307ab3f8\",\n458\t      \"raw_sha256\": \"0961bf040013bf35d7d9fd2e5ad4b9d212d0dab9d733357c5193569ba7b92acd\",\n459\t      \"events_sha256\": \"bea8ab60b84b2ff7e00eff035c1187c837f26fdc30b91bfd0d4ca8ee6d15ecab\",\n460\t      \"bound_s\": \"0.029339001207750293\",\n461\t      \"verdict\": \"VERIFIED-VALID\",\n462\t      \"disposition\": \"valid\"\n463\t    },\n464\t    {\n465\t      \"n\": 28,\n466\t      \"attempt_id\": \"20260727T050047-95e2f87e\",\n467\t      \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n468\t      \"manifest_sha256\": \"d572e55594e97a4d4f3fb82295c8ad7aedac68c15c18e7615f3ac13e91ebea8a\",\n469\t      \"evidence_sha256\": \"2d70134135398b613638ae6ec62607913026c7d0cdfa9da1dfc77c657fa0e091\",\n470\t      \"raw_sha256\": \"b439d5bc06855943055795db69117ab612866d397eef219d73e0a576545b06c5\",\n471\t      \"events_sha256\": \"a90f500e118b1e88041167fb9fb3808ae0e27b83fa5b664f63c98adecf1ae7a1\",\n472\t      \"bound_s\": \"0.028854562420070173\",\n473\t      \"verdict\": \"VERIFIED-VALID\",\n474\t      \"disposition\": \"valid\"\n475\t    },\n476\t    {\n477\t      \"n\": 29,\n478\t      \"attempt_id\": \"20260729T204105-39d25f8a\",\n479\t      \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n480\t      \"manifest_sha256\": \"3aec4fc319e1de5a3b34d3552774ee4cf59ad9b1134001c8176d538f1304871f\",\n481\t      \"evidence_sha256\": \"4323c8c5242812b95e544213367dd75f0bc927605d73c78c1a491a84dd829026\",\n482\t      \"raw_sha256\": \"4f0cd62a013d6cc639e11637e425b8e09af02703828d4d0e9638a30ef70e88fc\",\n483\t      \"events_sha256\": \"0ef0f3e5779fb6b1aec6bb48fb60a76c175106b192f16f8aeaf95e3961b75c59\",\n484\t      \"bound_s\": \"0.031467745880268516\",\n485\t      \"verdict\": \"VERIFIED-VALID\",\n486\t      \"disposition\": \"valid\"\n487\t    },\n488\t    {\n489\t      \"n\": 30,\n490\t      \"attempt_id\": \"20260730T014035-124df355\",\n491\t      \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n492\t      \"manifest_sha256\": \"bb894782e7dd95d38576514fe9360335552129d6de116e2a05a82c17a70702f5\",\n493\t      \"evidence_sha256\": \"f8946df7f5495d6e5c64f90490b94ca2eab94f10ed16b7298e5741dadbe182b1\",\n494\t      \"raw_sha256\": \"95d50522d5eef61dbf2b9b815dce3f62e8791fe417942883908dde762351332b\",\n495\t      \"events_sha256\": \"d66899983a1d8e7b4bc7ecb11c5740534e101f4fbdd2810dd41ff00910277379\",\n496\t      \"bound_s\": \"0.027788174032371493\",\n497\t      \"verdict\": \"VERIFIED-VALID\",\n498\t      \"disposition\": \"valid\"\n499\t    },\n500\t    {\n501\t      \"n\": 31,\n502\t      \"attempt_id\": \"20260730T210703-f76b5771\",\n503\t      \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n504\t      \"manifest_sha256\": \"e40353dfd883d773414378893f27bc617cfa972f62793b0f35cc9efa30ed7d44\",\n505\t      \"evidence_sha256\": \"0f5e3ea38ff0f833840895e065941494c71c4cd9bf0fe222a9e08ca24ddc3ed8\",\n506\t      \"raw_sha256\": \"718b9046d134fc2a9f089818ea2e5c3aac05c10f056f942c8702ec3b4cdabf75\",\n507\t      \"events_sha256\": \"aaf29ec68222439453b790725b6849040c3f7c1cb5accf096d3a722edebf9664\",\n508\t      \"bound_s\": \"0.026131301462788137\",\n509\t      \"verdict\": \"VERIFIED-VALID\",\n510\t      \"disposition\": \"valid\"\n511\t    },\n512\t    {\n513\t      \"n\": 32,\n514\t      \"attempt_id\": \"20260731T012210-374020b6\",\n515\t      \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n516\t      \"manifest_sha256\": \"f64a179f03a6b3efecaea6e3ad8ff08ba8c354b9f57023f0929781fd2d133545\",\n517\t      \"evidence_sha256\": \"21a6296fc74542a6400ab5562376b9bf969a1d906c8f9076f89dc9916cef1b52\",\n518\t      \"raw_sha256\": \"0f3b509c48e42a9cbcf32ac3a446d9c13d38766328f9569a96d397a685ad2f2d\",\n519\t      \"events_sha256\": \"624b9c26e71648272e36c85fa7884aa258851039a7e77a7be123e1290d2c4b79\",\n520\t      \"bound_s\": \"0.024850427856341006\",\n521\t      \"verdict\": \"VERIFIED-VALID\",\n522\t      \"disposition\": \"valid\"\n523\t    },\n524\t    {\n525\t      \"n\": 33,\n526\t      \"attempt_id\": \"20260731T161713-b8b08280\",\n527\t      \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n528\t      \"manifest_sha256\": \"e65aed76d770fbcd9c07b6c2dc26335ddf593533ff1ab6a46cb1bc9bdd119d0a\",\n529\t      \"evidence_sha256\": \"2cda4856ae7939067f0a6ebbbdb865871e437e1c652b0dd438e33cb5ffef1583\",\n530\t      \"raw_sha256\": \"464f5f9ca38818544e54061407251ef3d13541c90c8e5c6f05ee54fe8a913068\",\n531\t      \"events_sha256\": \"2bfd2ac5f0ba88e02a89dbc070837ce3bb1161b2d3067a6176e720bb778b4df1\",\n532\t      \"bound_s\": \"0.030972654450356962\",\n533\t      \"verdict\": \"VERIFIED-VALID\",\n534\t      \"disposition\": \"valid\"\n535\t    },\n536\t    {\n537\t      \"n\": 34,\n538\t      \"attempt_id\": \"20260731T214355-126fc2ab\",\n539\t      \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n540\t      \"manifest_sha256\": \"ad3aa2345df71df05fb5913ef52210443eb07cfbbb5824e48794b6892557848d\",\n541\t      \"evidence_sha256\": \"1958d58c35dfa30c18671abafcddf3d43c9328f586ce2051d1fb83ab99b51d5f\",\n542\t      \"raw_sha256\": \"c14ef61161fc9bf463840d5f62e1cdcd9bc2fe586297e5d89a6334e19f8dd21f\",\n543\t      \"events_sha256\": \"89808fe44225b7870585a1f2883ff43b01ec0b02507775900ada0a60251f145c\",\n544\t      \"bound_s\": null,\n545\t      \"verdict\": \"VERIFIED-INVALID\",\n546\t      \"disposition\": \"ordinary-invalid\",\n547\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n548\t    },\n549\t    {\n550\t      \"n\": 35,\n551\t      \"attempt_id\": \"20260801T010113-e859f3aa\",\n552\t      \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n553\t      \"manifest_sha256\": \"52aa9e9b4485a352d1ba2bd40e500f71cab989967d1db6e7a130fe9c157e0647\",\n554\t      \"evidence_sha256\": \"6c350a69406f92f4f1d68e30684f6b36b2f233fba5f52070a73f23c3d767fd45\",\n555\t      \"raw_sha256\": \"1302b53b6aeab97ee57b35cda8003ffb6d107265979614880910c24fdbbb5e7c\",\n556\t      \"events_sha256\": \"887ea9f6bc663ac5bc8cfe1c6d898262a2089602406186f83ff0f750983a841b\",\n557\t      \"bound_s\": \"0.41198917978147415\",\n558\t      \"verdict\": \"VERIFIED-INVALID\",\n559\t      \"disposition\": \"ordinary-invalid\",\n560\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n561\t    },\n562\t    {\n563\t      \"n\": 36,\n564\t      \"attempt_id\": \"20260801T010805-ff3fdc88\",\n565\t      \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n566\t      \"manifest_sha256\": \"fd5906ccd884670c9d40a57e7b8b4755357bc91c89f281449a080fe5c2007402\",\n567\t      \"evidence_sha256\": \"62967d66a74467735011f159a523f50b6409287bf96899446e4a02fa2c8e2eed\",\n568\t      \"raw_sha256\": \"c39bc0c6c55a3deabdffdf8bfdad95e061fb464def586edafdc19dbd1d8ea5c2\",\n569\t      \"events_sha256\": \"10e9035731a2d54a9469c66318568b6f2e91a0ac3fecdbfad94dfb62c22bf0fc\",\n570\t      \"bound_s\": null,\n571\t      \"verdict\": \"VERIFIED-INVALID\",\n572\t      \"disposition\": \"ordinary-invalid\",\n573\t      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n574\t    },\n575\t    {\n576\t      \"n\": 37,\n577\t      \"attempt_id\": \"20260801T014059-8c3bfe9e\",\n578\t      \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n579\t      \"manifest_sha256\": \"7d2967b125324c65e0d57a16950a0e1c2e2946464b7eb89667e8fc2410550149\",\n580\t      \"evidence_sha256\": \"c1653f369e05e9186d0c6d06231993575ee23c1fd813b96f1094d74dfbaac0ad\",\n581\t      \"raw_sha256\": \"f1a9350cbfdb0ec4c0a909b5d2b77798e16f754132499602b426a1068274465f\",\n582\t      \"events_sha256\": \"33f78ee6e299643d8f5929fc2e339f3e13959eb6983a7db8b8af4bd936a0700d\",\n583\t      \"bound_s\": \"0.032786870825707914\",\n584\t      \"verdict\": \"VERIFIED-VALID\",\n585\t      \"disposition\": \"valid\"\n586\t    },\n587\t    {\n588\t      \"n\": 38,\n589\t      \"attempt_id\": \"20260801T064830-c76f5d1c\",\n590\t      \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n591\t      \"manifest_sha256\": \"6127f706081c4686164ecca83032ab86bdc467170d55b24e537255cfdacac4dc\",\n592\t      \"evidence_sha256\": \"4c2752a194dbd1fc39aaf82e11071cccab4283c81f46208657bd849af6c23a06\",\n593\t      \"raw_sha256\": \"dab52b86df50235d78c39ddda87b3f4620b6dfdead9050640184204630cd5b1f\",\n594\t      \"events_sha256\": \"31e245dcaf050740a69f52ab3afa1783e2081e43a089dc57045be6039f7503e6\",\n595\t      \"bound_s\": \"0.0350400833260715\",\n596\t      \"verdict\": \"VERIFIED-VALID\",\n597\t      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer\"\n598\t    }\n599\t  ],\n600\t  \"raw_physics_method\": {\n601\t    \"valid_members\": \"Used verify_stored_evidence_physics, which rejects stored-status substitution, re-derives the causal anchor, reconstructs all pulse commands from events.jsonl, re-fits all 59 pulses, requires complete detection/no spurious plateaus/no reasons, checks every stored residual enclosure contains the refit, and returns max(stored,fresh) bound.\",\n602\t    \"valid_method_source\": \"joulewise/powermetrics_fiducial.py:1088-1164; docs/contracts/powermetrics_fiducial.md:183-211\",\n603\t    \"invalid_members\": \"Re-derived the causal anchor directly from native powermetrics records and recorded ClockStamps. All six independently returned unknown; an unresolved own anchor is forced invalid under the contract.\",\n604\t    \"hash_evidence\": \"Each selected custody manifest's lines 3-6 bind events, instrument evidence, power trace and raw plist. Every listed digest matched the bytes.\"\n605\t  },\n606\t  \"bootstrap_computation\": {\n607\t    \"authoritative_result\": \"NOT COMPUTABLE WITHOUT RULING/IMPORT CONTRACT\",\n608\t    \"required_prior_observation_set\": \"The exact 38 content IDs in per_member, each with epoch_id=d079_epoch and the final ruled disposition. No additional fixture-known-holdout row is evidenced by a real content bundle; configs/calibration/calibration_acceptance_d079_v2.json:222 is explicitly fixture data.\",\n609\t    \"receipt_algorithm_from_schema\": [\n610\t      \"receipt_core is canonical JSON with sorted keys, separators ',' and ':', UTF-8, allow_nan=false; receipt_digest=sha256(receipt_core). See joulewise/calibration_ledger.py:94-105,155-160.\",\n611\t      \"Each receipt contains sequence, predecessor_digest, event, attempt_id, content_id, artifact hashes, six-field epoch, full T1, capture lexeme, exact bound lexeme, disposition and custody locator. See joulewise/calibration_ledger.py:590-622.\",\n612\t      \"The parser requires a reservation before each finalization. See joulewise/calibration_ledger.py:409-465 and finalize_attempt_receipt at :716-777.\",\n613\t      \"The head pin is the final receipt's sequence and receipt_digest with ledger_schema. See joulewise/calibration_ledger.py:780-789.\"\n614\t    ],\n615\t    \"conditional_non_authoritative_replays\": [\n616\t      {\n617\t        \"assumptions\": \"Attempt IDs sorted ascending; one synthetic reservation immediately followed by one finalization per content ID; first hash-complete custody copy selected; candidate-tool mapping of all stored-valid rows to valid and stored-invalid rows to ordinary-invalid.\",\n618\t        \"sequence\": 76,\n619\t        \"head_digest\": \"cb410907660ed8a120d4e1d04a7e9af489b69d83686a8bf7658b3f73e7e3335a\",\n620\t        \"prior_observation_rows_sha256\": \"d29404feea08496453538d8b3994af1c4b64c12a86b950a3aa96a604cb6690c6\",\n621\t        \"dispositions\": {\n622\t          \"valid\": 32,\n623\t          \"ordinary-invalid\": 6\n624\t        },\n625\t        \"warning\": \"Illustrative only; the assumptions are not authorized by D-109 or an import schema.\"\n626\t      },\n627\t      {\n628\t        \"assumptions\": \"Same ordering/custody rules, but apply the production writer's preflight-screen mapping to members 22 and 38.\",\n629\t        \"sequence\": 76,\n630\t        \"head_digest\": \"8e80b6e93804df098f9fbec66740757073d235019e19990c7a9d8270b28337f1\",\n631\t        \"prior_observation_rows_sha256\": \"f28ddf8e0995230857c7e7db11c031084e18e8919ea1b9b373ae2112a9a936bf\",\n632\t        \"dispositions\": {\n633\t          \"valid\": 30,\n634\t          \"systematic-invalid\": 2,\n635\t          \"ordinary-invalid\": 6\n636\t        },\n637\t        \"warning\": \"Illustrative only; differs from D-109 R2.8's stated six-further consequence.\"\n638\t      }\n639\t    ],\n640\t    \"additional_implementation_gap\": \"append_pending_receipt requires the current physical ledger head to equal the committed pin before each new reservation (joulewise/calibration_ledger.py:673-690). Once one reservation/finalization pair advances the physical ledger, another reservation cannot be appended under the unchanged genesis pin. A batch bootstrap/import route is therefore required; none exists.\"\n641\t  },\n642\t  \"derivation_corpus\": {\n643\t    \"n\": 19,\n644\t    \"unchanged\": true,\n645\t    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:46-183\",\n646\t    \"artifact_file_sha256\": \"9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb\",\n647\t    \"stored_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n648\t    \"computed_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n649\t    \"match\": true,\n650\t    \"reconstructed_statistics\": {\n651\t      \"minimum_s\": \"0.022741007370546462\",\n652\t      \"minimum_member\": \"20260722T215127-eeef661a\",\n653\t      \"maximum_s\": \"0.03355875667989999\",\n654\t      \"maximum_member\": \"20260722T222332-901c5c13\",\n655\t      \"range_s\": \"0.010817749309353528\",\n656\t      \"mean_s\": \"0.026950033977532761\",\n657\t      \"sample_sd_s\": \"0.002970761365307205\"\n658\t    },\n659\t    \"note\": \"The current derivation_sha256 covers the complete artifact core excluding the hash field, not only the n=19 table (joulewise/calibration_bracketing.py:155-177). Issuance edits will therefore require a new canonical hash even though the threshold-producing n=19 remains unchanged.\"\n660\t  },\n661\t  \"D102_corpus_doubling\": {\n662\t    \"binding_rule\": \"38 total authenticated, content-distinct, valid same-epoch observations\",\n663\t    \"implementation_source\": \"joulewise/calibration_bracketing.py:901-908\",\n664\t    \"candidate_tool_disposition_result\": {\n665\t      \"current_valid_total\": 32,\n666\t      \"additional_valid_needed\": 6,\n667\t      \"trigger_now\": false,\n668\t      \"matches_D109_R2_8\": true\n669\t    },\n670\t    \"production_writer_disposition_result\": {\n671\t      \"current_valid_total\": 30,\n672\t      \"additional_valid_needed\": 8,\n673\t      \"trigger_now\": false,\n674\t      \"matches_D109_R2_8\": false\n675\t    },\n676\t    \"decision\": \"BLOCKED pending the B1 disposition ruling. The report does not choose between these counts.\"\n677\t  },\n678\t  \"verification\": [\n679\t    {\n680\t      \"id\": \"V1\",\n681\t      \"result\": \"PASS\",\n682\t      \"check\": \"Enumerated runs*/instrument_validation manifests, exact six-field epoch filtered, canonical content IDs recomputed.\",\n683\t      \"observed\": \"53 checkout custody copies; 38 distinct IDs; stored labels 32 valid/6 invalid.\"\n684\t    },\n685\t    {\n686\t      \"id\": \"V2\",\n687\t      \"result\": \"PASS\",\n688\t      \"check\": \"For every selected representative, rehashed every manifest-listed artifact and every evidence-internal artifact hash.\",\n689\t      \"observed\": \"Zero missing or mismatched bytes.\"\n690\t    },\n691\t    {\n692\t      \"id\": \"V3\",\n693\t      \"result\": \"PASS\",\n694\t      \"check\": \"Replayed strict raw physics for every candidate-valid observation and causal-anchor physics for every candidate-invalid observation.\",\n695\t      \"observed\": \"32 VERIFIED-VALID; 6 VERIFIED-INVALID; 0 raw unresolved.\"\n696\t    },\n697\t    {\n698\t      \"id\": \"V4\",\n699\t      \"result\": \"PASS\",\n700\t      \"check\": \"PYTHONDONTWRITEBYTECODE=1 python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact configs/calibration/calibration_acceptance_d079_v2.json\",\n701\t      \"observed\": \"PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK; n=19 statistics reproduced.\"\n702\t    },\n703\t    {\n704\t      \"id\": \"V5\",\n705\t      \"result\": \"PASS\",\n706\t      \"check\": \"Canonical artifact-core SHA-256 recomputation.\",\n707\t      \"observed\": \"stored=computed=3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d.\"\n708\t    },\n709\t    {\n710\t      \"id\": \"V6\",\n711\t      \"result\": \"PASS\",\n712\t      \"check\": \"Final git status.\",\n713\t      \"observed\": \"## main...origin/main; no changes.\"\n714\t    }\n715\t  ],\n716\t  \"flags\": [\n717\t    {\n718\t      \"id\": \"NO_EDITS\",\n719\t      \"level\": \"informational\",\n720\t      \"text\": \"Read-only verification; no artifact, ledger, pin, report or state file was created or modified.\"\n721\t    },\n722\t    {\n723\t      \"id\": \"ISSUANCE_BLOCKED\",\n724\t      \"level\": \"blocking\",\n725\t      \"text\": \"Lead must first rule the two high-bound dispositions and authorize a deterministic historical-import/bootstrap contract, including ordering and custody selection. Only then can one exact prior_observation_set, sequence and head digest be issued.\"\n726\t    }\n727\t  ],\n728\t  \"next_exact_step\": \"Lead rules whether members 20260726T000039-491995f3 and 20260801T064830-c76f5d1c are ledger-valid or systematic-invalid, then specifies the authenticated batch-import ordering/custody rule. Recompute the single resulting 76-receipt chain, review its exact head, and only in a separately authorized write session bootstrap the ledger, update and commit the head pin, and issue the acceptance artifact.\"\n729\t}\n730\t```"}]},"uuid":"2c3c55f2-cae1-4770-9c14-4491d0e0eb50","timestamp":"2026-08-06T10:42:16.326Z","toolUseResult":{"type":"text","file":{"filePath":"/Users/edr/code/JouleWise/docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md","content":"```json\n{\n  \"schema\": \"claude-codex-report/v1\",\n  \"genre\": \"verification\",\n  \"status\": \"findings\",\n  \"completion\": \"complete\",\n  \"summary\": \"BLOCKED. All 38 content-distinct candidates were recovered, hash-authenticated, epoch-checked, and replayed from raw physics: 32 VERIFIED-VALID and 6 VERIFIED-INVALID, with no missing raw evidence. Issuance is not ready because two verified-valid observations exceed the systematic-failure screen and therefore lack an unambiguous ledger disposition, and the repository does not specify a deterministic authenticated historical-import/bootstrap transaction from which one authoritative sequence/head digest can be computed.\",\n  \"workspace\": {\n    \"head_start\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n    \"head_end\": \"8e68cde6bb67165b6576c331d9631aa353ad0e83\",\n    \"branch\": \"main\",\n    \"pathspec\": [],\n    \"unowned_dirty\": [],\n    \"write_scope\": \"none\",\n    \"edits\": \"none\"\n  },\n  \"verdict\": {\n    \"overall\": \"BLOCKED\",\n    \"prompt_vs_R2_divergence\": false,\n    \"raw_member_results\": {\n      \"VERIFIED-VALID\": 32,\n      \"VERIFIED-INVALID\": 6,\n      \"UNRESOLVED\": 0\n    },\n    \"blocking_items\": [\n      {\n        \"id\": \"B1\",\n        \"type\": \"ledger_disposition_ruling\",\n        \"members\": [\n          \"20260726T000039-491995f3\",\n          \"20260801T064830-c76f5d1c\"\n        ],\n        \"reason\": \"Both replay as physically valid, matching the candidate inventory, but their bounds 0.035435840879704805 and 0.0350400833260715 exceed the ratified 0.033558756679900 preflight screen. The production writer maps such a valid capture to systematic-invalid at scripts/validate_powermetrics_fiducial.py:664-671; D-102 explicitly calls the first member a systematic failure at docs/decision_log.md:6298-6301. The backfill candidate tool instead proposes valid solely from stored status at scripts/calibration_ledger_backfill.py:58-63. Selecting either disposition is lead-owned.\"\n      },\n      {\n        \"id\": \"B2\",\n        \"type\": \"bootstrap_contract_gap\",\n        \"members\": \"all 38\",\n        \"reason\": \"No historical-import/bootstrap API, receipt ordering, duplicate-custody selection rule, or import-transaction schema exists. The candidate tool emits only an unauthoritative candidate set and never appends the ledger (scripts/calibration_ledger_backfill.py:2-7,90-117). Because receipt digests bind sequence, predecessor, disposition, artifact hashes and absolute custody locator (joulewise/calibration_ledger.py:590-622), more than one valid head digest is possible.\"\n      }\n    ]\n  },\n  \"binding_clauses\": [\n    {\n      \"clause\": \"D-109 R1.4\",\n      \"source\": \"docs/decision_log.md:7027-7039\",\n      \"verbatim\": \"4. The acceptance artifact pins its baseline ledger head. Evaluation ALSO requires the independent current-head pin (clause below), verifies one complete non-forked chain extension from baseline to current, and threads ONE immutable ledger snapshot through every consumer path (session, direct runner path, secondary verifier) — repeated independent loads are a refusal-grade defect. Anti-rollback authority: a REPO-COMMITTED head-pin file `{sequence, head_digest, ledger_schema}` (existing checked-in byte-pin trust model; no second trusted latest-sequence store). Rotation is epoch-bounded — at most one lead-controlled quiet-machine collection session — and NO claim evaluation may occur between ledger advancement and pin commit; a physical head differing from the committed pin refuses.\",\n      \"verification_plan\": \"After an authorized bootstrap, recompute every receipt digest, require one linear chain, require the artifact cutoff to equal an exact receipt, require the physical head to equal the separately committed pin, and trace one snapshot object through every consumer. This session verified the implemented digest/head machinery but could not select an authoritative bootstrap head because no import transaction is specified.\"\n    },\n    {\n      \"clause\": \"D-109 R2.1\",\n      \"source\": \"docs/decision_log.md:7053\",\n      \"verbatim\": \"1. The issuance cutoff is an exact ledger sequence + head digest.\",\n      \"verification_plan\": \"Compute the final receipt count and digest only after disposition, ordering and custody-locator rules are fixed. Current fixture cutoff remains non-production genesis sequence 0/all-zero digest at configs/calibration/calibration_acceptance_d079_v2.json:14-18.\"\n    },\n    {\n      \"clause\": \"D-109 R2.2\",\n      \"source\": \"docs/decision_log.md:7054-7055\",\n      \"verbatim\": \"2. `derivation_corpus` remains exactly the n=19 threshold-producing observations.\",\n      \"verification_plan\": \"Re-run the corpus verifier against all 19 pinned member manifest/evidence hashes and recompute the decimal statistics and artifact canonical hash. Result: PASS.\"\n    },\n    {\n      \"clause\": \"D-109 R2.3\",\n      \"source\": \"docs/decision_log.md:7056-7060\",\n      \"verbatim\": \"3. `prior_observation_set` = every content-distinct governed observation known at the cutoff — valid, systematic-invalid, ordinary-invalid, blind holdout, and unresolved — with epoch and disposition recorded separately. (The current artifact's two ID-only `blind_exclusions` are insufficient and are superseded.)\",\n      \"verification_plan\": \"Enumerate every exact-epoch validation tree, collapse copies by canonical content ID, authenticate the raw bytes, and assign one epoch plus one ruled disposition per content ID. The 38 identities are complete for the located candidate, but two dispositions require a ruling.\"\n    },\n    {\n      \"clause\": \"D-109 R2.4\",\n      \"source\": \"docs/decision_log.md:7061-7063\",\n      \"verbatim\": \"4. Content identity is path-independent, derived from canonical primary-byte hashes; attempt identity is separate; copies do not create new observations.\",\n      \"verification_plan\": \"Hash manifest.json and instrument_evidence.json bytes, canonical-JSON encode the two-name hash map, SHA-256 it, and collapse identical IDs. Implementation is joulewise/calibration_ledger.py:94-105,120-134. Result: 53 checkout copies collapse to 38 IDs.\"\n    },\n    {\n      \"clause\": \"D-109 R2.5\",\n      \"source\": \"docs/decision_log.md:7064-7068\",\n      \"verbatim\": \"5. \\\"New\\\" (trigger population) = current authentic content IDs − `prior_observation_set`, regardless of capture timestamp or source root; a previously unknown historical artifact IS new when discovered. Every new observation is judged under the PRIOR artifact (D-102's prospective rule).\",\n      \"verification_plan\": \"After issuance, subtract the exact 38-ID prior set from the authenticated ledger snapshot, independent of path/time, before applying triggers. The implemented subtraction is at joulewise/calibration_bracketing.py:870-893.\"\n    },\n    {\n      \"clause\": \"D-109 R2.6\",\n      \"source\": \"docs/decision_log.md:7069-7070\",\n      \"verbatim\": \"6. New unresolved or unclassifiable attempts cause refusal; only after trigger disposition may a successor artifact absorb them.\",\n      \"verification_plan\": \"Require every post-cutoff receipt to classify as valid, systematic-invalid or ordinary-invalid; unresolved/abandoned/null-content rows must refuse. Implemented refusal is at joulewise/calibration_bracketing.py:895-900.\"\n    },\n    {\n      \"clause\": \"D-109 R2.7\",\n      \"source\": \"docs/decision_log.md:7071-7074\",\n      \"verbatim\": \"7. The 32-valid/6-invalid same-epoch inventory is a backfill CANDIDATE, not a ratified classification: identities may seed the backfill, but dispositions require raw-physics + hash verification before issuance, and any unresolved member blocks issuance.\",\n      \"verification_plan\": \"For all 38 members: verify manifest and evidence hashes, verify raw/event hashes, replay causal clock-anchor derivation and the strict 59-pulse detector, verify the six-field epoch, then compare with candidate labeling. Result: 32 VERIFIED-VALID, 6 VERIFIED-INVALID, zero raw-physics unresolved; two final ledger dispositions remain ambiguous.\"\n    },\n    {\n      \"clause\": \"D-109 R2.8\",\n      \"source\": \"docs/decision_log.md:7075-7079\",\n      \"verbatim\": \"8. Counting rule for the D-102 corpus-doubling trigger (19→38): 38 TOTAL authenticated, content-distinct, VALID same-epoch observations — including previously blind observations once unblinded — not 38 post-cutoff observations. Under the candidate inventory, six further valid observations trigger re-derivation.\",\n      \"verification_plan\": \"Count content-distinct ledger observations whose disposition is exactly valid and whose epoch equals d079_epoch. The implementation does this at joulewise/calibration_bracketing.py:901-908. Result is six further only under the candidate-tool 32-valid disposition proposal; it is eight further under the production writer's systematic-screen mapping.\"\n    }\n  ],\n  \"inventory\": {\n    \"where_it_lives\": {\n      \"count_only_authority\": [\n        \"docs/process_traces/2026-08-03-d111-backfill/calbracket_d079/F3-fix-investigation.md:296-308\",\n        \"configs/calibration/calibration_acceptance_d079_v2.json:225-233\"\n      ],\n      \"candidate_emitter\": \"scripts/calibration_ledger_backfill.py:42-117\",\n      \"concrete_membership\": \"Implicit in the 53 exact-epoch validation custody trees under runs*/instrument_validation; no standalone serialized 38-row candidate file exists in the checkout or .desk.\",\n      \"raw_archive\": \"/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup\",\n      \"important_non_inventory\": \"docs/process_traces/2026-08-03-d111-backfill/MANIFEST.md is a manifest of 41 process artifacts, not the 38 calibration observations.\"\n    },\n    \"identity_method\": \"sha256(canonical_json({\\\"instrument_evidence.json\\\": sha256(evidence bytes), \\\"manifest.json\\\": sha256(manifest bytes)}))\",\n    \"identity_method_source\": \"joulewise/calibration_ledger.py:94-105,120-134\",\n    \"checkout_copy_count\": 53,\n    \"content_distinct_count\": 38,\n    \"candidate_label_counts\": {\n      \"valid\": 32,\n      \"invalid\": 6\n    },\n    \"analysis_only_member_set_sha256\": {\n      \"value\": \"7c0ae751e3be9d180c932b14da1cc9b50f85a73a0821de03c7a7911728a25e95\",\n      \"definition\": \"canonical SHA-256 of the ordered 38 candidate rows containing attempt_id, content_id, all artifact hashes, epoch, full T1, capture lexeme and bound lexeme; custody locator deliberately excluded. This digest is verification evidence, not a contract-defined production identity.\"\n    }\n  },\n  \"epoch\": {\n    \"epoch_id\": \"d079_epoch\",\n    \"all_38_match\": true,\n    \"fields\": {\n      \"os_build\": \"25F84\",\n      \"hardware_model\": \"Mac15,9\",\n      \"power_policy\": \"ac_high_power\",\n      \"sampling_interval_ms\": 100,\n      \"estimator_revision\": \"joint_loss_sublevel_interval_branch_v2\",\n      \"pulse_protocol_id\": \"powermetrics_pulse_fiducial_v3\"\n    },\n    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:20-26,193-200\"\n  },\n  \"per_member\": [\n    {\n      \"n\": 1,\n      \"attempt_id\": \"20260722T145535-e941c821\",\n      \"content_id\": \"c2a4412ee77fd2c10a397c8c4072d06c31bf26ea6b6a9a2ad1764dced71de2e9\",\n      \"manifest_sha256\": \"e34cdc199a479364dfdc539b3f924aefc997f7fecdeaa5d3d706028bf78e13a7\",\n      \"evidence_sha256\": \"148a7b45fa5efe88c6d925c836cb9c11596ffc1412960f6248e6bd8114b3eb7a\",\n      \"raw_sha256\": \"b55f3471c70c54e0174b09e67486759fc532742e9bd671e53ce8324fe23209ef\",\n      \"events_sha256\": \"605e2330d27f874621edb698c233542d7eb31fb8b8d1def044852a77a223b1bc\",\n      \"bound_s\": \"0.03018980442653224\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 2,\n      \"attempt_id\": \"20260722T194118-9dc0749d\",\n      \"content_id\": \"029a412be038ce88428ff1e8d302d90f2020e5cb0179ef4a750613fffc51f8ee\",\n      \"manifest_sha256\": \"0852da1adb0d0dd243b2142bd67da636f26c07eee4bbfbe1f79f78c771742041\",\n      \"evidence_sha256\": \"b763e5d6703255d7ebb18113c56cccda8908bb9d8049ab4210935304f50faa3f\",\n      \"raw_sha256\": \"aa36a9c1e8451e2a0de875a7ff45232c98bf0cce5cdcd5b827d176ea24aa85f7\",\n      \"events_sha256\": \"0f543eb7f697d442a5c0ddce1fe6f3f69c268c96bdc7a5ffbb6e84f70e8f1d66\",\n      \"bound_s\": \"0.026300679324099796\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 3,\n      \"attempt_id\": \"20260722T213749-563b9849\",\n      \"content_id\": \"ec850ad5359df234cf091b452194753acbd609f8c5102443fca8cfb40b3c72aa\",\n      \"manifest_sha256\": \"b7dd23cf8a9e30d81a01ba0b3c5c5e0c21b4c325e48e1d02e046fb61b77cb0ac\",\n      \"evidence_sha256\": \"1cc789e9558667e188f1859ba591a584a73eb4d2309612c924eebfb4cf5ffe80\",\n      \"raw_sha256\": \"3684b27080f6b4254d61e1c5b3f0f25e8401257078145331ef2122b2c1893fd1\",\n      \"events_sha256\": \"b179d606c17148e754bba07bb61c3d7a5c094e5a0e701251e7674b45472f5a4b\",\n      \"bound_s\": \"0.2079182387602739\",\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 4,\n      \"attempt_id\": \"20260722T214220-1acdbbc0\",\n      \"content_id\": \"7232cfa1de9e6e19543d00c976e184ee23f8e4a17d2b05f7f4fa44fc6461f01f\",\n      \"manifest_sha256\": \"ee78c1a87e5ab21f5c042e4dd2db38b9b7742be1ecaaa75fe0280f7c75a2f5b1\",\n      \"evidence_sha256\": \"3ea8f946d3522de46b01a90d29b0462f138a7048aa96df33bac79509d46349ea\",\n      \"raw_sha256\": \"7a4b62258d4d6afe251c4ed60a02835ac4d2b743f926260b2f621cb2301a72de\",\n      \"events_sha256\": \"6f0c813bf5489f1fce820bddd1160d6936ec5dc6e89f1c3ca2aecdbedc2834af\",\n      \"bound_s\": \"0.03312014638436772\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 5,\n      \"attempt_id\": \"20260722T215127-eeef661a\",\n      \"content_id\": \"7d7e898178e7fac74d9733a6703319d3458785abb671a2d43907a1018549f554\",\n      \"manifest_sha256\": \"9bf378fb924b96cf88015bd35f8733a2a31b2a965872a7781f7c3170fc55e0a5\",\n      \"evidence_sha256\": \"0659f79270fca6fa1459c01cf7ba8163337b28c3224b3c751eaa2241ca728024\",\n      \"raw_sha256\": \"8e275c342b5dde493e24e69f5a30fd7224ec36c21b324bd489508cda5860bff8\",\n      \"events_sha256\": \"30efea52cd15580aa4f4f52b959a4b6a881db0df0f72a488ae4d4493d51a8f75\",\n      \"bound_s\": \"0.022741007370546462\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 6,\n      \"attempt_id\": \"20260722T222332-901c5c13\",\n      \"content_id\": \"273e6326b8a43c4b97d2d9437cee84320488dc5857cf3bd663e916c53601f02f\",\n      \"manifest_sha256\": \"ef74ebd5f0a94ba05786c19fe068be3fd797542dd9d7ce988dd7b55f1b6e8c54\",\n      \"evidence_sha256\": \"e6d338d5061f0f1258d47bfc0600fb1f458a6780e954024020b136a3ac5bf8fe\",\n      \"raw_sha256\": \"84adafc6e55a45a10e56d5cea6571f1b12dae15656a2a0274822eb96500f4744\",\n      \"events_sha256\": \"1b7ce059e4b72885a77cb398704590e50e51b925cdae7bf77db1ad2b36dd7d59\",\n      \"bound_s\": \"0.03355875667989999\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 7,\n      \"attempt_id\": \"20260722T232509-82642517\",\n      \"content_id\": \"5092d2cd9912f5dd0fa79161e86e7eb07c0196f61585a0770500a27be46df55c\",\n      \"manifest_sha256\": \"5dcba24e377004801d8630dc7007955c85d6e0df42d23766474ef8e70e9bfe70\",\n      \"evidence_sha256\": \"e2741fe23dcf9bf972f037d6736ec78d3733dbb76d3522d03818b705a8a444d7\",\n      \"raw_sha256\": \"56555a10ee248cb6e5692280881d3daaf406b0432c2c3d068e06c5b8d8d76e40\",\n      \"events_sha256\": \"1c2b84546ed000dbb6f3378f5a1ef24ae008048209bcffee95644bbad585df6b\",\n      \"bound_s\": \"0.027654085293084385\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 8,\n      \"attempt_id\": \"20260723T023058-8732d1c9\",\n      \"content_id\": \"08ea40cb06c6290ad056a698a0803e4dbfc4591203121f4524169e380d8fc7fa\",\n      \"manifest_sha256\": \"ce4b3866ad92fa0be6ae5c2d8dead3c745aae5fd572b2b12f22ce6315977317d\",\n      \"evidence_sha256\": \"68680e5371e0cfac4313e4f0198e29ad89b477f6e6b470d6813d2131f83f921c\",\n      \"raw_sha256\": \"49d0b16529d40d6ce7a8d125f9787ab37e46ddfeb6b06e1b69a28e1a7011cf67\",\n      \"events_sha256\": \"962780bf83e89c2e5a4720e074e49f06c0aa49cac3989bed9035436ed734455a\",\n      \"bound_s\": \"0.024753340330112727\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 9,\n      \"attempt_id\": \"20260723T052051-d9358c8a\",\n      \"content_id\": \"eac62f5e4fa7600afbb6d822b6770e25513ae79e00a5e2ad12c0e89cfb205df1\",\n      \"manifest_sha256\": \"0f13d2f89242aa06ac921ef8e80c90f10079fefa78ecc313195fc82ad729be02\",\n      \"evidence_sha256\": \"62bd8e967bfd6f6c61e86f68fc427ded99d3cc301ecd3b6263571010b87a4e1c\",\n      \"raw_sha256\": \"dac05b535d4faa2f8864a2be91a6c56df812b1631fd60aaebde8e680a6aebc8e\",\n      \"events_sha256\": \"7e79ef10b6d9caae132b04ae1e59d584c569aa751084fa02e62e2cad5f794fd3\",\n      \"bound_s\": \"0.025964638697819786\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 10,\n      \"attempt_id\": \"20260723T183306-4ce692b4\",\n      \"content_id\": \"c75a8d727664c28ff3bbce88eab6e4065e00bc965f2f447fb2a41df488faa9fd\",\n      \"manifest_sha256\": \"baf1f2f0d1c27ae9fc70a341b35965a1259ea951ccd7997d662d4846ca568a9c\",\n      \"evidence_sha256\": \"689456dab5e5723155dfb237439671475a220b8f9f0329fc12d67dadfd69d3dd\",\n      \"raw_sha256\": \"bcd97c9bd9b0a0686fc84bfa9d117685b6a68f8beed7f84dfa503eacaf78d941\",\n      \"events_sha256\": \"7341d55729c2a3ebf68739900105893b5f2d59bb55d57092ef20e2b94d6c95ca\",\n      \"bound_s\": \"0.027262160888545217\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 11,\n      \"attempt_id\": \"20260723T194632-d04e038e\",\n      \"content_id\": \"0c5851939bac8e93973dbf8464e7c053ce4b1da0a708efa062a80d169004e6d9\",\n      \"manifest_sha256\": \"b1835c633161226ce71b5b7ba17ad95d12719eba00201819f6b0a725aa01d1ec\",\n      \"evidence_sha256\": \"f321e38ef08d08455a89084e07de65beea4be43c4d5157e4432c04b908b909a6\",\n      \"raw_sha256\": \"b1660d10fcc5015f0ccc0e4e0a7464db3a5220d415c952f3d9635e512faab57c\",\n      \"events_sha256\": \"a965e301af8f2cb662dca60a7b9706d9b6e7dbabdc6971abd3119c46fc7711d6\",\n      \"bound_s\": \"0.024593263907495888\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 12,\n      \"attempt_id\": \"20260723T195730-bc4ba14a\",\n      \"content_id\": \"2ae2573af972e9c9b3fbe0aa98d57d265056b58902b35eb5995925fa10c1fbe8\",\n      \"manifest_sha256\": \"1a9e9776d1286bf8b3f7f3e01b943baed8e275d4d27271e25e91ab773eeb2005\",\n      \"evidence_sha256\": \"71c646f3cd2d3c960d98061b8b3d27679aea357397bb9602a8bb3e456eb43eb7\",\n      \"raw_sha256\": \"81669d5e0e81ccb1d05ae7d19befffbf41441a92a1e14f0dcb8c0b8d9b6f7a86\",\n      \"events_sha256\": \"0343c61d357465919f99b13000e39f02b43575c68c5383e1f03ffc46a3a2ee24\",\n      \"bound_s\": \"0.025305226022515448\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 13,\n      \"attempt_id\": \"20260723T221449-e9ae755e\",\n      \"content_id\": \"418db55fa63dd5a0bae1ebb2291d860748df350d1b94aae4645d858c0527741c\",\n      \"manifest_sha256\": \"448d30359957c3786d24806d8f39a4577709abdb4144e6b5f29058dd9448e319\",\n      \"evidence_sha256\": \"3d8f80a7bc3870f3472fa4dc0cf82eb6570e78b2371f5b52f019e70e934fcf2a\",\n      \"raw_sha256\": \"4e971efc4abef1f51a636a095fa807d1b395ed8342f5e7386aead5e9c466ce50\",\n      \"events_sha256\": \"1caf0be478a75308070e0a93818618af2dd8ca69f51bd2e35f1994c5b7f9b2d0\",\n      \"bound_s\": \"0.027702588281732055\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 14,\n      \"attempt_id\": \"20260723T223406-314f6d9e\",\n      \"content_id\": \"f3db4bc343a25c25734a017a02089ddc15db5169d67b222356d5a6fc09e143e4\",\n      \"manifest_sha256\": \"d8801c8c0bcc1b429c5ec20eefaa341e0506cf749227936a409e2c6cb4fac7fe\",\n      \"evidence_sha256\": \"e39f93a9ad22e0003a47947f028feef857029910cd1c41f0134d5802eb24b803\",\n      \"raw_sha256\": \"2c92bf2a3065493b00caf678a5ee8d78c93d3dba406979cb824058b355274f73\",\n      \"events_sha256\": \"4a4a990161e35f05d9fbd36c1eb52f78c46551145348036e073aa2494519df29\",\n      \"bound_s\": \"0.026173651901677253\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 15,\n      \"attempt_id\": \"20260724T014109-57844352\",\n      \"content_id\": \"35ae646c47747e8561982ec8a7128e2e1a84e5c3255de66ee18ba51415017dc3\",\n      \"manifest_sha256\": \"4cd0fac603ea08c8ae27f4f7be9a3abf0e05a4800852f632d95622ae04ebda6e\",\n      \"evidence_sha256\": \"ee681d97af16f831b9d29cf54f43669ca5b138b4521524ec02946f58d0e6e736\",\n      \"raw_sha256\": \"9c806bcd26a0f6cce7f33c00d930d803e39f9bd4a6e186971d6123a470a1b13d\",\n      \"events_sha256\": \"221c42b7f214515f9af84c2b9486315df70e3466c66b7beb5bf35e476bf5ae14\",\n      \"bound_s\": \"0.02547564583006129\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 16,\n      \"attempt_id\": \"20260725T005132-a64711b7\",\n      \"content_id\": \"bf7c217c20effafa210cb53e86db0e6743df4e5eafca779d79ae0e8073c8f7b3\",\n      \"manifest_sha256\": \"c239775f1005a3461338fcd6ed7b0354253fd9b19631c4254354a0951f8f3cc9\",\n      \"evidence_sha256\": \"54a882afb71d601086053db862e448b61b34574b83b414c146f9c2d3761df1be\",\n      \"raw_sha256\": \"a22005ea981f8e3ac1f3ea65cfa6bd1d0777dc009203b5e2db73cce44d2aca4e\",\n      \"events_sha256\": \"459dc8a3ec34eb7a3f2095d0c5b72e931f8d87199fd48812386684f36162f617\",\n      \"bound_s\": \"0.023241581438247116\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 17,\n      \"attempt_id\": \"20260725T011533-0b5ec77c\",\n      \"content_id\": \"10fe0bff822d2c2546f2cbc45d85e9fb46cbd739dc4a972585775a2e2f29a0ec\",\n      \"manifest_sha256\": \"1b0e39338fc15aaf35395a1a5ae91834bd4af626fc07743e13ec72a5bd998fa0\",\n      \"evidence_sha256\": \"63fd3bf3415720558f2925d6997288b250c4ef4d48f95b577e0357799dc38ca5\",\n      \"raw_sha256\": \"9934c97547e2cd77de640754c2c51399a66bc96a265f31d38616677ab9973c3d\",\n      \"events_sha256\": \"c15516d15ae525051012e8655817625d37803dda2b8473917720cc5a29ef3043\",\n      \"bound_s\": \"0.028891617940876635\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 18,\n      \"attempt_id\": \"20260725T022712-0a9534f5\",\n      \"content_id\": \"ff6de7a0496f834973007f3c355b3c2dd3bd37e9701b632b049904f134f52e00\",\n      \"manifest_sha256\": \"c3c8e5aae83fbc7865d8daba433384538402c412db40e2269d398665458d9185\",\n      \"evidence_sha256\": \"d0853c448ddc47be11c08b00c410fb169a534d3ad0180a9716b4689f235235da\",\n      \"raw_sha256\": \"bb99b0b7086ee939a8fb789253e2c0502de27a05d056c78d46dc30fccfb862cf\",\n      \"events_sha256\": \"a42487bd9202c043485eebc42a68f505b35faf158c8640f1393d287a1d36e0d1\",\n      \"bound_s\": \"0.029197264796726408\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 19,\n      \"attempt_id\": \"20260725T030533-d3f076e5\",\n      \"content_id\": \"51f24f06cc5d99a58fc354423f4b08b03dfe5c2e8ece4ea148967896802cb984\",\n      \"manifest_sha256\": \"f1c6a4b2c965c689916a4be0c49ea6515e1f78b28ea4b7a7df3c1e85132e348a\",\n      \"evidence_sha256\": \"e2f83efb8effb6a305cd5d09b3465a23b68e0e4dd96624507e96c1d45384802e\",\n      \"raw_sha256\": \"26b9ad5ba13e2c73e78ddfdf5be6a2b1cf4b8eb31881aad575ac1bb7ae0dabb9\",\n      \"events_sha256\": \"180a700366e1a97a9e8649a6d98bbd2d814fe9d5fed7246f99b47aa1af5e6b84\",\n      \"bound_s\": \"0.024879191521227362\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 20,\n      \"attempt_id\": \"20260725T055825-b10cb348\",\n      \"content_id\": \"1ef9ce6167865f3e04304b73ada774e11515b3895a5b51d5c1d8b7eb18af9aea\",\n      \"manifest_sha256\": \"eebf3524d9e0b41c022c5e57d4b16787e98302e0d7c28381036415117fafb3ba\",\n      \"evidence_sha256\": \"e0d525e0923f88572f7530f447a3bc8e889ef80a47d662840b86c40b4a35f285\",\n      \"raw_sha256\": \"ed13e60dcfe12d7ce3900798dfbafb7936baa3700cdf58d0f6c1d0fc1790a4b8\",\n      \"events_sha256\": \"fbb3d05c9185ed416d9c138fc63dc32d56b1cd465059007962f9273b53dce671\",\n      \"bound_s\": null,\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: wall_minus_monotonic_span_exceeded\"\n    },\n    {\n      \"n\": 21,\n      \"attempt_id\": \"20260725T060617-97c5cba6\",\n      \"content_id\": \"ac89c0d106fdf4aff146f11f77c95dea4682d35d71e6c3582c9169772149acc9\",\n      \"manifest_sha256\": \"984bbe85e6b2ab4a6ade95fc567972636d62b347e5686f16878764396a66b704\",\n      \"evidence_sha256\": \"10c31305f00245cadef3d71b75ddbf46f542811177da8d13e3def6308e19efa2\",\n      \"raw_sha256\": \"85583f5f07299f38f4f912581e2cfc03453d3a0e85a0de486b3406a355b2c9f2\",\n      \"events_sha256\": \"c904c5f1a1c6557117b6fbde70dc8358dca773f94fc0c611cd50e92c3a3e2ffa\",\n      \"bound_s\": \"0.025045994537554683\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 22,\n      \"attempt_id\": \"20260726T000039-491995f3\",\n      \"content_id\": \"03a6a20dae1071f7c74e5c006e891849e83c317080390b64473ed319545a4710\",\n      \"manifest_sha256\": \"b5e1d1195eb8c52bb41211b464909723754e5753bb866ced6f5715d83769ef65\",\n      \"evidence_sha256\": \"9584cd7cdc44e5ba4d176475ce2bf6f70d04e163778fd6e9d5e46cec02303c00\",\n      \"raw_sha256\": \"b916d0b8fc79e8fc7b261c6d608307fbae94bd3c89189e2256cafcf483378c2d\",\n      \"events_sha256\": \"579c2adf45f245dbf31e69b83617fceaf28e63be70677fe0dcd8104a82c79248\",\n      \"bound_s\": \"0.035435840879704805\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer and D-102\"\n    },\n    {\n      \"n\": 23,\n      \"attempt_id\": \"20260726T031222-e0ce33f5\",\n      \"content_id\": \"20d2518c3d99619a1ba56ffa679fadf9a5e5870064324c27f5cb6a7a99e9afdb\",\n      \"manifest_sha256\": \"5ec9e27a9bdef89d8e83ca2fd2ee0c1c2d8d2effd56139ac904d1b032c3fc378\",\n      \"evidence_sha256\": \"8d0b2d48460c71d35b2b3b7124b3168c86a497b5a674348451ea5d73931adab3\",\n      \"raw_sha256\": \"c5674ce16dba60b5f0f61ffa5dbe6d7c38bc11747f627e120f6b96af7b9f2fe1\",\n      \"events_sha256\": \"7ba5009ade8a7a870fcb119297dc34a54dcd78f54d13d463e2b4de721db7100b\",\n      \"bound_s\": \"0.023854405254729094\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 24,\n      \"attempt_id\": \"20260726T225227-1f550773\",\n      \"content_id\": \"ce9373a047879fbf94c30d5119b2735ca6a9b9f16ddb460f8310f8654642b96b\",\n      \"manifest_sha256\": \"5837bd2c5be6769d63faa57a5d59311241038be7f92de6101b61566b54d89131\",\n      \"evidence_sha256\": \"95941785a8fca5b74019da42d18d280abda639f92442ad57195b852ca567b564\",\n      \"raw_sha256\": \"db6416cada6ea8c0bc84109903fc734d71c0f5a4d8451bafa05a05a76dd7b89d\",\n      \"events_sha256\": \"2de1638cb73fa1a23105a81fe9cdcf9774f467adfcf6fa59bd29029c15a1a9cf\",\n      \"bound_s\": \"0.04916527633725107\",\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 25,\n      \"attempt_id\": \"20260726T225920-ab4272f5\",\n      \"content_id\": \"8872864d1c97f40987dab4d693479fee6405c8616ea1effdf2a0457c10f5a8f8\",\n      \"manifest_sha256\": \"1696f470f0cc543a62cc40a819068a4b7b9f62058fd8d0dd1707870dd25b59e5\",\n      \"evidence_sha256\": \"5b1c9dce56202e1d8af74e71b37aaa1538f0e53fcdded1e05c61cff90f41cda5\",\n      \"raw_sha256\": \"4f83a36625a199a1e5e552953afbdc004bd5144756c8aa2bf657c8c714b4453f\",\n      \"events_sha256\": \"dc704274c1c608a3a87387575c7a36e868c988f9737b033775f55d12791f80f5\",\n      \"bound_s\": \"0.028145704403191807\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 26,\n      \"attempt_id\": \"20260727T015824-45feb516\",\n      \"content_id\": \"03497b300c7d35bd6fe08855dc468687e788f81481ab7285b04fa726a202d440\",\n      \"manifest_sha256\": \"a7ac96e151419313594510f7511071cbdd710a1ab0837fef25a792ccc1b38d48\",\n      \"evidence_sha256\": \"96f2af22ae5b18ba70f08ec2ed40c54abe0934508ae0d7cfb8fadb9de19432d8\",\n      \"raw_sha256\": \"d0f8ab38ade1df00d957597f6ae0bfdffce047d8611416ecb434f91c4e35ae47\",\n      \"events_sha256\": \"c75224662805694c090f458e6462f8a69581e39e7cf9a4f03d1c3d3b2ae7a371\",\n      \"bound_s\": \"0.029425288011457773\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 27,\n      \"attempt_id\": \"20260727T020611-4a409a30\",\n      \"content_id\": \"51633cd3498a0c234962301bd608f5a31916bd3a3cb3f2e805fd2215edc849ca\",\n      \"manifest_sha256\": \"dc30e9df75b0e4bc561c6f9d641ed3dff696697508333de6707d354151bd96ec\",\n      \"evidence_sha256\": \"e3f4df9cf8bf4f1edfacbd10072bd53c5c1b59a873e4c25ee1727d74307ab3f8\",\n      \"raw_sha256\": \"0961bf040013bf35d7d9fd2e5ad4b9d212d0dab9d733357c5193569ba7b92acd\",\n      \"events_sha256\": \"bea8ab60b84b2ff7e00eff035c1187c837f26fdc30b91bfd0d4ca8ee6d15ecab\",\n      \"bound_s\": \"0.029339001207750293\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 28,\n      \"attempt_id\": \"20260727T050047-95e2f87e\",\n      \"content_id\": \"20ff4e73d0a329e3ecfc4b98be496c66392c77ea353a96f9885d5e52bdb98e37\",\n      \"manifest_sha256\": \"d572e55594e97a4d4f3fb82295c8ad7aedac68c15c18e7615f3ac13e91ebea8a\",\n      \"evidence_sha256\": \"2d70134135398b613638ae6ec62607913026c7d0cdfa9da1dfc77c657fa0e091\",\n      \"raw_sha256\": \"b439d5bc06855943055795db69117ab612866d397eef219d73e0a576545b06c5\",\n      \"events_sha256\": \"a90f500e118b1e88041167fb9fb3808ae0e27b83fa5b664f63c98adecf1ae7a1\",\n      \"bound_s\": \"0.028854562420070173\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 29,\n      \"attempt_id\": \"20260729T204105-39d25f8a\",\n      \"content_id\": \"7410aafd9448b8da07e4b919e324b24bc7b15ac9b01a3200e39ef6f615cadfc3\",\n      \"manifest_sha256\": \"3aec4fc319e1de5a3b34d3552774ee4cf59ad9b1134001c8176d538f1304871f\",\n      \"evidence_sha256\": \"4323c8c5242812b95e544213367dd75f0bc927605d73c78c1a491a84dd829026\",\n      \"raw_sha256\": \"4f0cd62a013d6cc639e11637e425b8e09af02703828d4d0e9638a30ef70e88fc\",\n      \"events_sha256\": \"0ef0f3e5779fb6b1aec6bb48fb60a76c175106b192f16f8aeaf95e3961b75c59\",\n      \"bound_s\": \"0.031467745880268516\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 30,\n      \"attempt_id\": \"20260730T014035-124df355\",\n      \"content_id\": \"4451d9a9cd5c6b5a801d146908b549886bd11559fc4c2ee3e771434fb4b95bd9\",\n      \"manifest_sha256\": \"bb894782e7dd95d38576514fe9360335552129d6de116e2a05a82c17a70702f5\",\n      \"evidence_sha256\": \"f8946df7f5495d6e5c64f90490b94ca2eab94f10ed16b7298e5741dadbe182b1\",\n      \"raw_sha256\": \"95d50522d5eef61dbf2b9b815dce3f62e8791fe417942883908dde762351332b\",\n      \"events_sha256\": \"d66899983a1d8e7b4bc7ecb11c5740534e101f4fbdd2810dd41ff00910277379\",\n      \"bound_s\": \"0.027788174032371493\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 31,\n      \"attempt_id\": \"20260730T210703-f76b5771\",\n      \"content_id\": \"6026cb9f72b5a76f2a4b5b4f88bde06d644e3cd47e4e0cdc11d44ab6ecf5fabf\",\n      \"manifest_sha256\": \"e40353dfd883d773414378893f27bc617cfa972f62793b0f35cc9efa30ed7d44\",\n      \"evidence_sha256\": \"0f5e3ea38ff0f833840895e065941494c71c4cd9bf0fe222a9e08ca24ddc3ed8\",\n      \"raw_sha256\": \"718b9046d134fc2a9f089818ea2e5c3aac05c10f056f942c8702ec3b4cdabf75\",\n      \"events_sha256\": \"aaf29ec68222439453b790725b6849040c3f7c1cb5accf096d3a722edebf9664\",\n      \"bound_s\": \"0.026131301462788137\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 32,\n      \"attempt_id\": \"20260731T012210-374020b6\",\n      \"content_id\": \"e522d8fabdebaa446776c52f8c263be6d853b700107d21c835557be475b165c2\",\n      \"manifest_sha256\": \"f64a179f03a6b3efecaea6e3ad8ff08ba8c354b9f57023f0929781fd2d133545\",\n      \"evidence_sha256\": \"21a6296fc74542a6400ab5562376b9bf969a1d906c8f9076f89dc9916cef1b52\",\n      \"raw_sha256\": \"0f3b509c48e42a9cbcf32ac3a446d9c13d38766328f9569a96d397a685ad2f2d\",\n      \"events_sha256\": \"624b9c26e71648272e36c85fa7884aa258851039a7e77a7be123e1290d2c4b79\",\n      \"bound_s\": \"0.024850427856341006\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 33,\n      \"attempt_id\": \"20260731T161713-b8b08280\",\n      \"content_id\": \"bd170c828910f4543f60ee76fae1f04b10707c58cd907be4c707706faea78aae\",\n      \"manifest_sha256\": \"e65aed76d770fbcd9c07b6c2dc26335ddf593533ff1ab6a46cb1bc9bdd119d0a\",\n      \"evidence_sha256\": \"2cda4856ae7939067f0a6ebbbdb865871e437e1c652b0dd438e33cb5ffef1583\",\n      \"raw_sha256\": \"464f5f9ca38818544e54061407251ef3d13541c90c8e5c6f05ee54fe8a913068\",\n      \"events_sha256\": \"2bfd2ac5f0ba88e02a89dbc070837ce3bb1161b2d3067a6176e720bb778b4df1\",\n      \"bound_s\": \"0.030972654450356962\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 34,\n      \"attempt_id\": \"20260731T214355-126fc2ab\",\n      \"content_id\": \"ff49477c8c7d71df3a9b7f86681e436ede8b7c1ac8c2b3fb2ee745cd6421ada1\",\n      \"manifest_sha256\": \"ad3aa2345df71df05fb5913ef52210443eb07cfbbb5824e48794b6892557848d\",\n      \"evidence_sha256\": \"1958d58c35dfa30c18671abafcddf3d43c9328f586ce2051d1fb83ab99b51d5f\",\n      \"raw_sha256\": \"c14ef61161fc9bf463840d5f62e1cdcd9bc2fe586297e5d89a6334e19f8dd21f\",\n      \"events_sha256\": \"89808fe44225b7870585a1f2883ff43b01ec0b02507775900ada0a60251f145c\",\n      \"bound_s\": null,\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 35,\n      \"attempt_id\": \"20260801T010113-e859f3aa\",\n      \"content_id\": \"473a8aec1aba846e270ddccaa6bbea5b315cd36f28616e2daff2d7edefe52518\",\n      \"manifest_sha256\": \"52aa9e9b4485a352d1ba2bd40e500f71cab989967d1db6e7a130fe9c157e0647\",\n      \"evidence_sha256\": \"6c350a69406f92f4f1d68e30684f6b36b2f233fba5f52070a73f23c3d767fd45\",\n      \"raw_sha256\": \"1302b53b6aeab97ee57b35cda8003ffb6d107265979614880910c24fdbbb5e7c\",\n      \"events_sha256\": \"887ea9f6bc663ac5bc8cfe1c6d898262a2089602406186f83ff0f750983a841b\",\n      \"bound_s\": \"0.41198917978147415\",\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 36,\n      \"attempt_id\": \"20260801T010805-ff3fdc88\",\n      \"content_id\": \"9add6b6926ef2eb45722cfcdc8562a643dba0fd43f045ae534419fc7a7ecfd21\",\n      \"manifest_sha256\": \"fd5906ccd884670c9d40a57e7b8b4755357bc91c89f281449a080fe5c2007402\",\n      \"evidence_sha256\": \"62967d66a74467735011f159a523f50b6409287bf96899446e4a02fa2c8e2eed\",\n      \"raw_sha256\": \"c39bc0c6c55a3deabdffdf8bfdad95e061fb464def586edafdc19dbd1d8ea5c2\",\n      \"events_sha256\": \"10e9035731a2d54a9469c66318568b6f2e91a0ac3fecdbfad94dfb62c22bf0fc\",\n      \"bound_s\": null,\n      \"verdict\": \"VERIFIED-INVALID\",\n      \"disposition\": \"ordinary-invalid\",\n      \"raw_reason\": \"fresh causal anchor unknown: native_intersection_empty\"\n    },\n    {\n      \"n\": 37,\n      \"attempt_id\": \"20260801T014059-8c3bfe9e\",\n      \"content_id\": \"ea0c34c63f1c9bed2649081eab80a3fbaf5c4ffd1ea37da12bc11945053aefca\",\n      \"manifest_sha256\": \"7d2967b125324c65e0d57a16950a0e1c2e2946464b7eb89667e8fc2410550149\",\n      \"evidence_sha256\": \"c1653f369e05e9186d0c6d06231993575ee23c1fd813b96f1094d74dfbaac0ad\",\n      \"raw_sha256\": \"f1a9350cbfdb0ec4c0a909b5d2b77798e16f754132499602b426a1068274465f\",\n      \"events_sha256\": \"33f78ee6e299643d8f5929fc2e339f3e13959eb6983a7db8b8af4bd936a0700d\",\n      \"bound_s\": \"0.032786870825707914\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"valid\"\n    },\n    {\n      \"n\": 38,\n      \"attempt_id\": \"20260801T064830-c76f5d1c\",\n      \"content_id\": \"ef01bcca6caf35f7abea2dcaa7acf8cc53d5a9e3463c413dba61d17f9179c448\",\n      \"manifest_sha256\": \"6127f706081c4686164ecca83032ab86bdc467170d55b24e537255cfdacac4dc\",\n      \"evidence_sha256\": \"4c2752a194dbd1fc39aaf82e11071cccab4283c81f46208657bd849af6c23a06\",\n      \"raw_sha256\": \"dab52b86df50235d78c39ddda87b3f4620b6dfdead9050640184204630cd5b1f\",\n      \"events_sha256\": \"31e245dcaf050740a69f52ab3afa1783e2081e43a089dc57045be6039f7503e6\",\n      \"bound_s\": \"0.0350400833260715\",\n      \"verdict\": \"VERIFIED-VALID\",\n      \"disposition\": \"UNRESOLVED_LEDGER_DISPOSITION: valid per candidate-tool proposal; systematic-invalid per production writer\"\n    }\n  ],\n  \"raw_physics_method\": {\n    \"valid_members\": \"Used verify_stored_evidence_physics, which rejects stored-status substitution, re-derives the causal anchor, reconstructs all pulse commands from events.jsonl, re-fits all 59 pulses, requires complete detection/no spurious plateaus/no reasons, checks every stored residual enclosure contains the refit, and returns max(stored,fresh) bound.\",\n    \"valid_method_source\": \"joulewise/powermetrics_fiducial.py:1088-1164; docs/contracts/powermetrics_fiducial.md:183-211\",\n    \"invalid_members\": \"Re-derived the causal anchor directly from native powermetrics records and recorded ClockStamps. All six independently returned unknown; an unresolved own anchor is forced invalid under the contract.\",\n    \"hash_evidence\": \"Each selected custody manifest's lines 3-6 bind events, instrument evidence, power trace and raw plist. Every listed digest matched the bytes.\"\n  },\n  \"bootstrap_computation\": {\n    \"authoritative_result\": \"NOT COMPUTABLE WITHOUT RULING/IMPORT CONTRACT\",\n    \"required_prior_observation_set\": \"The exact 38 content IDs in per_member, each with epoch_id=d079_epoch and the final ruled disposition. No additional fixture-known-holdout row is evidenced by a real content bundle; configs/calibration/calibration_acceptance_d079_v2.json:222 is explicitly fixture data.\",\n    \"receipt_algorithm_from_schema\": [\n      \"receipt_core is canonical JSON with sorted keys, separators ',' and ':', UTF-8, allow_nan=false; receipt_digest=sha256(receipt_core). See joulewise/calibration_ledger.py:94-105,155-160.\",\n      \"Each receipt contains sequence, predecessor_digest, event, attempt_id, content_id, artifact hashes, six-field epoch, full T1, capture lexeme, exact bound lexeme, disposition and custody locator. See joulewise/calibration_ledger.py:590-622.\",\n      \"The parser requires a reservation before each finalization. See joulewise/calibration_ledger.py:409-465 and finalize_attempt_receipt at :716-777.\",\n      \"The head pin is the final receipt's sequence and receipt_digest with ledger_schema. See joulewise/calibration_ledger.py:780-789.\"\n    ],\n    \"conditional_non_authoritative_replays\": [\n      {\n        \"assumptions\": \"Attempt IDs sorted ascending; one synthetic reservation immediately followed by one finalization per content ID; first hash-complete custody copy selected; candidate-tool mapping of all stored-valid rows to valid and stored-invalid rows to ordinary-invalid.\",\n        \"sequence\": 76,\n        \"head_digest\": \"cb410907660ed8a120d4e1d04a7e9af489b69d83686a8bf7658b3f73e7e3335a\",\n        \"prior_observation_rows_sha256\": \"d29404feea08496453538d8b3994af1c4b64c12a86b950a3aa96a604cb6690c6\",\n        \"dispositions\": {\n          \"valid\": 32,\n          \"ordinary-invalid\": 6\n        },\n        \"warning\": \"Illustrative only; the assumptions are not authorized by D-109 or an import schema.\"\n      },\n      {\n        \"assumptions\": \"Same ordering/custody rules, but apply the production writer's preflight-screen mapping to members 22 and 38.\",\n        \"sequence\": 76,\n        \"head_digest\": \"8e80b6e93804df098f9fbec66740757073d235019e19990c7a9d8270b28337f1\",\n        \"prior_observation_rows_sha256\": \"f28ddf8e0995230857c7e7db11c031084e18e8919ea1b9b373ae2112a9a936bf\",\n        \"dispositions\": {\n          \"valid\": 30,\n          \"systematic-invalid\": 2,\n          \"ordinary-invalid\": 6\n        },\n        \"warning\": \"Illustrative only; differs from D-109 R2.8's stated six-further consequence.\"\n      }\n    ],\n    \"additional_implementation_gap\": \"append_pending_receipt requires the current physical ledger head to equal the committed pin before each new reservation (joulewise/calibration_ledger.py:673-690). Once one reservation/finalization pair advances the physical ledger, another reservation cannot be appended under the unchanged genesis pin. A batch bootstrap/import route is therefore required; none exists.\"\n  },\n  \"derivation_corpus\": {\n    \"n\": 19,\n    \"unchanged\": true,\n    \"source\": \"configs/calibration/calibration_acceptance_d079_v2.json:46-183\",\n    \"artifact_file_sha256\": \"9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb\",\n    \"stored_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n    \"computed_derivation_sha256\": \"3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d\",\n    \"match\": true,\n    \"reconstructed_statistics\": {\n      \"minimum_s\": \"0.022741007370546462\",\n      \"minimum_member\": \"20260722T215127-eeef661a\",\n      \"maximum_s\": \"0.03355875667989999\",\n      \"maximum_member\": \"20260722T222332-901c5c13\",\n      \"range_s\": \"0.010817749309353528\",\n      \"mean_s\": \"0.026950033977532761\",\n      \"sample_sd_s\": \"0.002970761365307205\"\n    },\n    \"note\": \"The current derivation_sha256 covers the complete artifact core excluding the hash field, not only the n=19 table (joulewise/calibration_bracketing.py:155-177). Issuance edits will therefore require a new canonical hash even though the threshold-producing n=19 remains unchanged.\"\n  },\n  \"D102_corpus_doubling\": {\n    \"binding_rule\": \"38 total authenticated, content-distinct, valid same-epoch observations\",\n    \"implementation_source\": \"joulewise/calibration_bracketing.py:901-908\",\n    \"candidate_tool_disposition_result\": {\n      \"current_valid_total\": 32,\n      \"additional_valid_needed\": 6,\n      \"trigger_now\": false,\n      \"matches_D109_R2_8\": true\n    },\n    \"production_writer_disposition_result\": {\n      \"current_valid_total\": 30,\n      \"additional_valid_needed\": 8,\n      \"trigger_now\": false,\n      \"matches_D109_R2_8\": false\n    },\n    \"decision\": \"BLOCKED pending the B1 disposition ruling. The report does not choose between these counts.\"\n  },\n  \"verification\": [\n    {\n      \"id\": \"V1\",\n      \"result\": \"PASS\",\n      \"check\": \"Enumerated runs*/instrument_validation manifests, exact six-field epoch filtered, canonical content IDs recomputed.\",\n      \"observed\": \"53 checkout custody copies; 38 distinct IDs; stored labels 32 valid/6 invalid.\"\n    },\n    {\n      \"id\": \"V2\",\n      \"result\": \"PASS\",\n      \"check\": \"For every selected representative, rehashed every manifest-listed artifact and every evidence-internal artifact hash.\",\n      \"observed\": \"Zero missing or mismatched bytes.\"\n    },\n    {\n      \"id\": \"V3\",\n      \"result\": \"PASS\",\n      \"check\": \"Replayed strict raw physics for every candidate-valid observation and causal-anchor physics for every candidate-invalid observation.\",\n      \"observed\": \"32 VERIFIED-VALID; 6 VERIFIED-INVALID; 0 raw unresolved.\"\n    },\n    {\n      \"id\": \"V4\",\n      \"result\": \"PASS\",\n      \"check\": \"PYTHONDONTWRITEBYTECODE=1 python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root . --artifact configs/calibration/calibration_acceptance_d079_v2.json\",\n      \"observed\": \"PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK; n=19 statistics reproduced.\"\n    },\n    {\n      \"id\": \"V5\",\n      \"result\": \"PASS\",\n      \"check\": \"Canonical artifact-core SHA-256 recomputation.\",\n      \"observed\": \"stored=computed=3cece3b2c816476887613c3c25d8d186dbefa61047275c5b157d32980249da9d.\"\n    },\n    {\n      \"id\": \"V6\",\n      \"result\": \"PASS\",\n      \"check\": \"Final git status.\",\n      \"observed\": \"## main...origin/main; no changes.\"\n    }\n  ],\n  \"flags\": [\n    {\n      \"id\": \"NO_EDITS\",\n      \"level\": \"informational\",\n      \"text\": \"Read-only verification; no artifact, ledger, pin, report or state file was created or modified.\"\n    },\n    {\n      \"id\": \"ISSUANCE_BLOCKED\",\n      \"level\": \"blocking\",\n      \"text\": \"Lead must first rule the two high-bound dispositions and authorize a deterministic historical-import/bootstrap contract, including ordering and custody selection. Only then can one exact prior_observation_set, sequence and head digest be issued.\"\n    }\n  ],\n  \"next_exact_step\": \"Lead rules whether members 20260726T000039-491995f3 and 20260801T064830-c76f5d1c are ledger-valid or systematic-invalid, then specifies the authenticated batch-import ordering/custody rule. Recompute the single resulting 76-receipt chain, review its exact head, and only in a separately authorized write session bootstrap the ledger, update and commit the head pin, and issue the acceptance artifact.\"\n}\n```","numLines":730,"startLine":1,"totalLines":730}},"sourceToolAssistantUUID":"e07187f2-62a1-40a1-856e-b8be22861d57","userType":"external","entrypoint":"cli","cwd":"/Users/edr/code/JouleWise","sessionId":"df9ee343-36aa-42b0-8bbf-cc7598ecfdb3","version":"2.1.223","gitBranch":"main"}
7900:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:663:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7903:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:3093:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7906:docs/strategy/2026-08-07-paper-portfolio/proposals/prop-split-inference-metrology.md:4181:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7907:docs/process_traces/2026-08-05-d079-issuance/VERIFICATION-REPORT.md:84:      "verification_plan": "Require every post-cutoff receipt to classify as valid, systematic-invalid or ordinary-invalid; unresolved/abandoned/null-content rows must refuse. Implemented refusal is at joulewise/calibration_bracketing.py:895-900."
7909:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:37049:4538:+- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7910:docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md:158:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7914:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:838:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7918:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:11549:   158	- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7921:docs/process_traces/2026-08-07-d117-u-units/U3-AUDIT-CONTRACT.md:4446:- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
7960:tests/test_d078_reason_registry.py:76:            "scripts/validate_powermetrics_fiducial.py",
8008:        uncaught_finalizer = source.index("atexit.register(finalize_abandoned)")
8056:    def test_content_bearing_abandoned_receipt_is_unresolved_evidence(self) -> None:
8057:        custody = self._custody("abandoned-content")
8058:        self._reserve("abandoned-content", custody)
8060:            "abandoned-content", custody, disposition="abandoned"
8064:        observation = snapshot.observation_by_attempt["abandoned-content"]
8066:        self.assertEqual(observation.disposition, "abandoned")
8209:The L4 gap is now pinned to two concrete sites: the live calibration writer classifies with a hard-coded `Decimal("0.033558756679900")`, and the runbook’s §5A shell template independently compares the same copied literal. Neither authenticates the active artifact, registry entry, ledger cutoff, or six-field identity epoch. The U2 brief will therefore separate the successor builder from a mandatory pre-science probe and call out the frozen work-order scope mismatch needed to close L4 mechanically.
8228:   158	- authenticated acceptance registry mapping acceptance ID to exact artifact SHA, derivation SHA, cutoff receipt, parent acceptance ID, and parent ledger head;
8235:   165	I recommend deriving a successor from all content-distinct, valid, same-epoch observations through the chosen cutoff. Systematic, ordinary-invalid, aborted, or unresolved attempts remain recorded but excluded. The lead should explicitly ratify that corpus rule because D-102 establishes the successor obligation but does not fully spell out this live-prefix derivation policy.
8239:   169	### F4 — Referenced trace missing (should-fix)
8255:   346	1. Capture the post observation before changing power, network-time, or workload state.
8256:   347	2. Finalize the post slot or write the governed failure/abort closure.
8263:   423	- open or abandoned session without a governed closure;
8270:   430	- the observation-count boundary reaching the D-102 limit;
8279:   439	The floor riders here use the prefill phase of the 128-prompt decode workload. They do not automatically transport to a prospectively defined 256-token contrast. The fourth plan needs either exact matching prefill floor cells or a separately predeclared and justified transport rule. No placeholder members or plan ID should be added to gamma now.
8297:   457	| U2 — D-102 successor engine | `joulewise/calibration_bracketing.py`; `scripts/build_calibration_acceptance_successor.py`; `configs/calibration/calibration_acceptance_registry.json`; `tests/test_calibration_acceptance_successor.py` | Complete authenticated live prefix, deterministic bytes, parent ancestry, exact Decimal derivation, range/count triggers, systematic refusal. Focused cold-gate fixtures plus full suite. | Sequential after U1 because of shared bracketing semantics |
8307:   467	Every unit should run its focused tests and `python3 -m unittest discover -s tests`. Shared files make U1→U2 sequential; U1 and U3 can proceed independently. U5 and U6 can proceed independently after U3 freezes the vocabulary. U7 waits for final floor-cell and transport identifiers. U10 is deliberately absent from the desk freeze.
8309:   469	### What the lead should double-check
8312:   472	- Ratify the two-slot ledger capability against D-109/D-116, especially whether an open post slot may exist during the pre-science successor probe.
8358:  6302	   pre-flight level screen, and D-079 cl.2's systematic failure is
8367:  6311	   observed range; corpus doubling (19→38); a new systematic failure
8412:  7020	   as valid / systematic-invalid / ordinary-invalid / abandoned. Any
8489:  7500	**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).
8493:  7504	**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.
8495:  7506	**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.
9093:U2 should replace the single hard-coded issued-artifact pin with a Git-authenticated acceptance registry and an immutable lineage of acceptance artifacts. A successor is derived from every content-distinct, valid observation in the artifact’s exact six-field epoch through a selected authenticated ledger cutoff.
9097:The pre-science probe must load and authenticate the actual active artifact, its registry entry, ledger ancestry, estimator/protocol bytes, and observed epoch. Reading `b_fiducial_s` and comparing it to a copied scalar is not sufficient.
9112:- Proposed registry: `configs/calibration/calibration_acceptance_registry.json`; it does not exist yet.
9118:Recommended new schema: `joulewise.calibration_acceptance_bound.v3`. It must contain exactly these top-level fields:
9143:  - Recommended form: `d079_calibration_acceptance_v3_s<sequence>_<head-prefix>`.
9164:  - The first registry entry for the current issued artifact has a null parent; every successor has exactly one parent.
9204:  - Systematic-invalid, ordinary-invalid, abandoned, pending, unresolved, other-epoch, imported-copy duplicates, or non-v3 observations never enter this list.
9216:  - `noncontent_attempts`, recording governed abandoned/unresolved attempts that lack a content ID.
9235:    - preflight-screen quantum `0.000000000000001`
9248:  - Artifact file SHA remains external in the registry, avoiding a self-hash.
9272:The preflight level-screen derivation needs an explicit cold ruling; see open question 2 below.
9276:1. Load the committed registry and resolve its single active entry.
9278:3. Read the parent artifact once; verify exact file SHA against the registry, recompute its derivation hash, validate schema, and verify registry ancestry.
9289:   - in-range valid observation below the count boundary → no successor;
9298:17. In dry-run mode, emit bytes, artifact SHA, derivation SHA, proposed registry entry, and proposed head pin to stdout; write nothing.
9299:18. In issue mode, require explicit artifact and registry destinations, refuse overwrite/path substitution, stage both validated byte buffers, and publish only under the governed head-pin/commit procedure.
9300:19. A second run over identical parent, ledger, cutoff, and code must produce byte-identical artifact and registry output.
9304:The probe should return one of four closed outcomes:
9326:   - govern the still-open post slot according to U1’s state machine;
9329:   - update its registry entry and active pointer;
9351:- Current issued n=19 artifact and initial registry entry authenticate unchanged.
9354:- An in-range observation does not trigger before the count boundary.
9359:- Pending, abandoned, null-content, unresolved, or unknown disposition refuses issuance.
9366:- Parent artifact tamper, wrong registry SHA, wrong derivation SHA, orphan parent, ancestry cycle, inactive-parent build, or registry rollback refuses.
9372:- Successor golden produces byte-identical artifact, registry entry, and expected head pin across repeated builds and shuffled input enumeration.
9374:- Failed final validation publishes neither artifact nor registry mutation.
9397:configs/calibration/calibration_acceptance_registry.json
9403:Recommended rule-11 expansion for U2:
9409:configs/calibration/calibration_acceptance_registry.json
9422:Therefore L4 should be marked “code closed by U2, arm-path closed by U8,” and retired only after both land. Do not silently add these paths to a delegated U2 session; the cold gate must authorize the expansion.
9430:2. Ratify the preflight-screen formula for successors. The loader currently uses rounded observed maximum; the runbook says the larger of observed maximum and a 95% upper prediction. Those agree for n=19 but need not agree later.
9432:3. Ratify the deterministic Student-t implementation and precision. Decimal accumulation is exact, but the numerical CDF/quantile algorithm must be versioned and pinned.
9434:4. After a range-triggered n=31 successor, is the next count boundary still the original 38, and after the n=38 successor does it become 76? Recommended: retain 38 until crossed, then double the newly issued corpus count.
9436:5. Decide whether any new systematic failure permanently blocks automatic successor issuance pending a new ruling, as recommended, or merely blocks that attempt.
9438:6. Resolve abandoned/no-content handling: record it in `noncontent_attempts` but refuse issuance until governed closure establishes it cannot conceal a classifiable observation.
9440:7. Ratify the v3 schema, deterministic acceptance-ID format, immutable artifact path convention, and whether old parent bytes must remain present or may be recovered from Git history.
9442:8. Ratify registry authentication: committed registry bytes as trust anchor, one active entry, exact artifact SHA, no code-side per-successor constants.
9444:9. Ratify artifact/registry/head-pin co-landing and crash behavior. No claim evaluation may occur between ledger advancement and committed successor authority.
9446:10. Resolve U1 interaction: whether the pre probe may run with the post slot prospectively open, and how that slot is preserved or closed while a triggered head is committed and a successor issued.
9448:11. Ratify whether a post observation accepted under the parent may subsequently participate in bracket evaluation under the successor, provided the artifact retains explicit parent-judgment evidence.
9450:12. Approve the six-file U2 scope expansion above, or accept that writer-side copied-scalar removal remains a separately gated hardening unit.
9459:U2 should replace the single hard-coded issued-artifact pin with a Git-authenticated acceptance registry and an immutable lineage of acceptance artifacts. A successor is derived from every content-distinct, valid observation in the artifact’s exact six-field epoch through a selected authenticated ledger cutoff.
9463:The pre-science probe must load and authenticate the actual active artifact, its registry entry, ledger ancestry, estimator/protocol bytes, and observed epoch. Reading `b_fiducial_s` and comparing it to a copied scalar is not sufficient.
9478:- Proposed registry: `configs/calibration/calibration_acceptance_registry.json`; it does not exist yet.
9484:Recommended new schema: `joulewise.calibration_acceptance_bound.v3`. It must contain exactly these top-level fields:
9509:  - Recommended form: `d079_calibration_acceptance_v3_s<sequence>_<head-prefix>`.
9530:  - The first registry entry for the current issued artifact has a null parent; every successor has exactly one parent.
9570:  - Systematic-invalid, ordinary-invalid, abandoned, pending, unresolved, other-epoch, imported-copy duplicates, or non-v3 observations never enter this list.
9582:  - `noncontent_attempts`, recording governed abandoned/unresolved attempts that lack a content ID.
9601:    - preflight-screen quantum `0.000000000000001`
9614:  - Artifact file SHA remains external in the registry, avoiding a self-hash.
9638:The preflight level-screen derivation needs an explicit cold ruling; see open question 2 below.
9642:1. Load the committed registry and resolve its single active entry.
9644:3. Read the parent artifact once; verify exact file SHA against the registry, recompute its derivation hash, validate schema, and verify registry ancestry.
9655:   - in-range valid observation below the count boundary → no successor;
9664:17. In dry-run mode, emit bytes, artifact SHA, derivation SHA, proposed registry entry, and proposed head pin to stdout; write nothing.
9665:18. In issue mode, require explicit artifact and registry destinations, refuse overwrite/path substitution, stage both validated byte buffers, and publish only under the governed head-pin/commit procedure.
9666:19. A second run over identical parent, ledger, cutoff, and code must produce byte-identical artifact and registry output.
9670:The probe should return one of four closed outcomes:
9692:   - govern the still-open post slot according to U1’s state machine;
9695:   - update its registry entry and active pointer;
9717:- Current issued n=19 artifact and initial registry entry authenticate unchanged.
9720:- An in-range observation does not trigger before the count boundary.
9725:- Pending, abandoned, null-content, unresolved, or unknown disposition refuses issuance.
9732:- Parent artifact tamper, wrong registry SHA, wrong derivation SHA, orphan parent, ancestry cycle, inactive-parent build, or registry rollback refuses.
9738:- Successor golden produces byte-identical artifact, registry entry, and expected head pin across repeated builds and shuffled input enumeration.
9740:- Failed final validation publishes neither artifact nor registry mutation.
9763:configs/calibration/calibration_acceptance_registry.json
9769:Recommended rule-11 expansion for U2:
9775:configs/calibration/calibration_acceptance_registry.json
9788:Therefore L4 should be marked “code closed by U2, arm-path closed by U8,” and retired only after both land. Do not silently add these paths to a delegated U2 session; the cold gate must authorize the expansion.
9796:2. Ratify the preflight-screen formula for successors. The loader currently uses rounded observed maximum; the runbook says the larger of observed maximum and a 95% upper prediction. Those agree for n=19 but need not agree later.
9798:3. Ratify the deterministic Student-t implementation and precision. Decimal accumulation is exact, but the numerical CDF/quantile algorithm must be versioned and pinned.
9800:4. After a range-triggered n=31 successor, is the next count boundary still the original 38, and after the n=38 successor does it become 76? Recommended: retain 38 until crossed, then double the newly issued corpus count.
9802:5. Decide whether any new systematic failure permanently blocks automatic successor issuance pending a new ruling, as recommended, or merely blocks that attempt.
9804:6. Resolve abandoned/no-content handling: record it in `noncontent_attempts` but refuse issuance until governed closure establishes it cannot conceal a classifiable observation.
9806:7. Ratify the v3 schema, deterministic acceptance-ID format, immutable artifact path convention, and whether old parent bytes must remain present or may be recovered from Git history.
9808:8. Ratify registry authentication: committed registry bytes as trust anchor, one active entry, exact artifact SHA, no code-side per-successor constants.
9810:9. Ratify artifact/registry/head-pin co-landing and crash behavior. No claim evaluation may occur between ledger advancement and committed successor authority.
9812:10. Resolve U1 interaction: whether the pre probe may run with the post slot prospectively open, and how that slot is preserved or closed while a triggered head is committed and a successor issued.
9814:11. Ratify whether a post observation accepted under the parent may subsequently participate in bracket evaluation under the successor, provided the artifact retains explicit parent-judgment evidence.
9816:12. Approve the six-file U2 scope expansion above, or accept that writer-side copied-scalar removal remains a separately gated hardening unit.

exec
/bin/zsh -lc "git log --oneline --decorate --reverse main..origin/impl/d117-u2-successor
git merge-base main origin/impl/d117-u2-successor
git log -1 --format='%P' origin/impl/d117-u2-successor

git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '700,790p'
git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '900,985p'
git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '1630,1910p'
git show origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py | nl -ba | sed -n '130,205p'
git show origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py | nl -ba | sed -n '225,345p'
git show origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py | nl -ba | sed -n '325,475p'
git show origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py | nl -ba | sed -n '500,585p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
399ffeb (origin/impl/d117-u2-successor, impl/d117-u2-successor) U2 speculative implementation (COLD-GATE EXHIBIT — not a landing candidate): D-102 successor engine with registry authentication, deterministic Decimal derivation, trigger probing, guarded publication. All 12 contested design choices implemented at the design brief's recommended answer and tagged COLD-GATE-Q1..Q12 so the gate can flip any ruling with a minimal diff.
f665dd4d8bfb7eaca3256a0709b3310254e308fe
f665dd4d8bfb7eaca3256a0709b3310254e308fe
   700	        relative = path.relative_to(repo_root).as_posix()
   701	        completed = subprocess.run(
   702	            ["git", "show", f"HEAD:{relative}"],
   703	            cwd=repo_root,
   704	            check=False,
   705	            capture_output=True,
   706	        )
   707	    except (OSError, ValueError):
   708	        return None
   709	    return completed.stdout if completed.returncode == 0 else None
   710	
   711	
   712	def load_calibration_acceptance_registry(
   713	    path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
   714	    *,
   715	    repo_root: Path = _REPO_ROOT,
   716	    require_committed: bool = True,
   717	) -> dict[str, Any] | None:
   718	    """Load the single-active acceptance registry and authenticate ancestry."""
   719	
   720	    path = Path(path)
   721	    lexical_repo_root = Path(repo_root).absolute()
   722	    repo_root = Path(repo_root).resolve()
   723	    try:
   724	        if _path_has_symlink_component(path.absolute(), lexical_repo_root):
   725	            return None
   726	        resolved = path.resolve(strict=True)
   727	        resolved.relative_to(repo_root)
   728	        raw = resolved.read_bytes()
   729	        value = json.loads(raw)
   730	    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
   731	        return None
   732	    if require_committed and _git_head_bytes(resolved, repo_root) != raw:
   733	        return None
   734	    if not _valid_registry(value):
   735	        return None
   736	    entries_by_id = {entry["acceptance_id"]: entry for entry in value["entries"]}
   737	    artifacts_by_id: dict[str, Mapping[str, Any]] = {}
   738	    for entry in value["entries"]:
   739	        artifact_path = repo_root / entry["artifact_path"]
   740	        try:
   741	            if _path_has_symlink_component(artifact_path.absolute(), repo_root):
   742	                return None
   743	            artifact_resolved = artifact_path.resolve(strict=True)
   744	            artifact_resolved.relative_to(repo_root)
   745	            artifact_raw = artifact_resolved.read_bytes()
   746	            artifact = json.loads(artifact_raw)
   747	        except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
   748	            return None
   749	        if (
   750	            hashlib.sha256(artifact_raw).hexdigest() != entry["artifact_sha256"]
   751	            or not _valid_acceptance_bound(artifact)
   752	            or artifact.get("acceptance_id") != entry["acceptance_id"]
   753	            or artifact.get("schema_version") != entry["artifact_schema"]
   754	            or artifact.get("derivation_sha256") != entry["derivation_sha256"]
   755	            or {
   756	                key: artifact["ledger_cutoff"].get(key)
   757	                for key in ("sequence", "head_digest", "ledger_schema")
   758	            }
   759	            != entry["ledger_cutoff"]
   760	        ):
   761	            return None
   762	        artifacts_by_id[entry["acceptance_id"]] = artifact
   763	        if entry["artifact_schema"] == ACCEPTANCE_SUCCESSOR_SCHEMA:
   764	            filename_match = _SUCCESSOR_ARTIFACT_NAME_RE.fullmatch(
   765	                Path(entry["artifact_path"]).name
   766	            )
   767	            if (
   768	                filename_match is None
   769	                or int(filename_match.group(1))
   770	                != entry["ledger_cutoff"]["sequence"]
   771	                or filename_match.group(2)
   772	                != entry["ledger_cutoff"]["head_digest"][:16]
   773	            ):
   774	                return None
   775	    for entry in value["entries"]:
   776	        if entry["artifact_schema"] != ACCEPTANCE_SUCCESSOR_SCHEMA:
   777	            continue
   778	        artifact = artifacts_by_id[entry["acceptance_id"]]
   779	        lineage = artifact["lineage"]
   780	        parent_entry = entries_by_id.get(entry["parent_acceptance_id"])
   781	        parent = artifacts_by_id.get(entry["parent_acceptance_id"])
   782	        if parent_entry is None or parent is None:
   783	            return None
   784	        count = artifact["derivation_corpus"]["n"]
   785	        parent_boundary = _artifact_count_boundary(parent)
   786	        expected_boundary = parent_boundary if count < parent_boundary else 2 * count
   787	        if (
   788	            lineage["generation"] != entry["generation"]
   789	            or lineage["parent_acceptance_id"] != entry["parent_acceptance_id"]
   790	            or lineage["parent_artifact_sha256"] != parent_entry["artifact_sha256"]
   900	        or judgment.get("judged_under_acceptance_id")
   901	        != lineage["parent_acceptance_id"]
   902	        or judgment.get("judged_under_artifact_sha256")
   903	        != lineage["parent_artifact_sha256"]
   904	        or judgment.get("result") != "successor_required"
   905	        or not isinstance(judgment.get("new_content_ids"), list)
   906	        or judgment["new_content_ids"] != sorted(set(judgment["new_content_ids"]))
   907	        or not all(_valid_sha256(item) for item in judgment["new_content_ids"])
   908	        or not isinstance(judgment.get("triggers"), list)
   909	        or not judgment["triggers"]
   910	        or judgment["triggers"]
   911	        != [
   912	            trigger
   913	            for trigger in (
   914	                "new_valid_same_identity_capture_expands_observed_range",
   915	                "content_distinct_valid_same_epoch_count_boundary",
   916	            )
   917	            if trigger in judgment["triggers"]
   918	        ]
   919	    ):
   920	        return False
   921	    if (
   922	        not isinstance(prospective, Mapping)
   923	        or prospective.get("calendar_expiry") is not None
   924	        or prospective.get("trigger_observation_rule")
   925	        != "judge_under_prior_artifact_never_self_fit"
   926	        or prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
   927	        or prospective.get("estimator_code_sha256")
   928	        != _current_estimator_code_sha256()
   929	        or prospective.get("triggers")
   930	        != [
   931	            "identity_field_change",
   932	            "protocol_or_estimator_byte_change",
   933	            "new_valid_same_identity_capture_expands_observed_range",
   934	            "content_distinct_valid_same_epoch_count_boundary",
   935	            "new_systematic_failure_challenges_preflight_screen",
   936	        ]
   937	        or not isinstance(prospective.get("count_trigger"), Mapping)
   938	        or set(prospective["count_trigger"])
   939	        != {"source_corpus_count", "next_boundary", "rule"}
   940	        or prospective["count_trigger"].get("rule")
   941	        != SUCCESSOR_COUNT_BOUNDARY_RULE
   942	    ):
   943	        return False
   944	    if (
   945	        not isinstance(corpus, Mapping)
   946	        or set(corpus) != {"selection", "n", "members"}
   947	        or corpus.get("selection") != SUCCESSOR_CORPUS_SELECTION
   948	        or isinstance(corpus.get("n"), bool)
   949	        or not isinstance(corpus.get("n"), int)
   950	        or corpus["n"] < 2
   951	        or not isinstance(corpus.get("members"), list)
   952	        or len(corpus["members"]) != corpus["n"]
   953	        or prospective["count_trigger"].get("source_corpus_count") != corpus["n"]
   954	        or isinstance(prospective["count_trigger"].get("next_boundary"), bool)
   955	        or not isinstance(prospective["count_trigger"].get("next_boundary"), int)
   956	        or prospective["count_trigger"]["next_boundary"] <= corpus["n"]
   957	    ):
   958	        return False
   959	    member_keys = {
   960	        "content_id",
   961	        "attempt_id",
   962	        "finalization_sequence",
   963	        "receipt_digest",
   964	        "custody_locator",
   965	        "b_fiducial_s",
   966	        "manifest_sha256",
   967	        "instrument_evidence_sha256",
   968	    }
   969	    member_ids: list[str] = []
   970	    for member in corpus["members"]:
   971	        if (
   972	            not isinstance(member, Mapping)
   973	            or set(member) != member_keys
   974	            or not _valid_sha256(member.get("content_id"))
   975	            or not isinstance(member.get("attempt_id"), str)
   976	            or not member["attempt_id"]
   977	            or isinstance(member.get("finalization_sequence"), bool)
   978	            or not isinstance(member.get("finalization_sequence"), int)
   979	            or member["finalization_sequence"] < 1
   980	            or member["finalization_sequence"] > cutoff["sequence"]
   981	            or not _valid_sha256(member.get("receipt_digest"))
   982	            or not isinstance(member.get("custody_locator"), str)
   983	            or not member["custody_locator"]
   984	            or (bound := _decimal(member.get("b_fiducial_s"))) is None
   985	            or bound < 0
  1630	        return False
  1631	    candidate = _candidate_from_observation(
  1632	        observation
  1633	        if observation.disposition == "valid"
  1634	        else replace(observation, disposition="valid")
  1635	    )
  1636	    return candidate is not None
  1637	
  1638	
  1639	def _probe_result(
  1640	    *,
  1641	    outcome: str,
  1642	    active: Mapping[str, Any] | None,
  1643	    artifact: Mapping[str, Any] | None,
  1644	    snapshot: CalibrationLedgerSnapshot,
  1645	    observed_identity_epoch: Mapping[str, Any] | None,
  1646	    new_content_ids: Sequence[str] = (),
  1647	    triggers: Sequence[str] = (),
  1648	    refusal_reasons: Sequence[str] = (),
  1649	) -> dict[str, Any]:
  1650	    cutoff = artifact.get("ledger_cutoff") if isinstance(artifact, Mapping) else None
  1651	    return {
  1652	        "schema_version": ACCEPTANCE_TRIGGER_PROBE_SCHEMA,
  1653	        "outcome": outcome,
  1654	        "active_acceptance_id": (
  1655	            artifact.get("acceptance_id") if isinstance(artifact, Mapping) else None
  1656	        ),
  1657	        "artifact_sha256": active.get("artifact_sha256") if active else None,
  1658	        "derivation_sha256": (
  1659	            artifact.get("derivation_sha256")
  1660	            if isinstance(artifact, Mapping)
  1661	            else None
  1662	        ),
  1663	        "parent_cutoff": (
  1664	            {
  1665	                key: cutoff.get(key)
  1666	                for key in ("sequence", "head_digest", "ledger_schema")
  1667	            }
  1668	            if isinstance(cutoff, Mapping)
  1669	            else None
  1670	        ),
  1671	        "current_ledger_head": {
  1672	            "sequence": snapshot.head_sequence,
  1673	            "head_digest": snapshot.head_digest,
  1674	            "ledger_schema": snapshot.ledger_schema,
  1675	            "committed_sequence": snapshot.committed_head_sequence,
  1676	            "committed_digest": snapshot.committed_head_digest,
  1677	        },
  1678	        "observed_identity_epoch": (
  1679	            dict(observed_identity_epoch)
  1680	            if isinstance(observed_identity_epoch, Mapping)
  1681	            else None
  1682	        ),
  1683	        "new_content_ids": list(new_content_ids),
  1684	        "observed_triggers": list(triggers),
  1685	        "refusal_reasons": list(refusal_reasons),
  1686	        "writer_integration_scope_status": WRITER_INTEGRATION_SCOPE_STATUS,
  1687	    }
  1688	
  1689	
  1690	def probe_calibration_acceptance_trigger(
  1691	    ledger_snapshot: CalibrationLedgerSnapshot,
  1692	    *,
  1693	    observed_identity_epoch: Mapping[str, Any] | None,
  1694	    registry_path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
  1695	    repo_root: Path = _REPO_ROOT,
  1696	    require_committed_registry: bool = True,
  1697	    verify_custody: bool = True,
  1698	) -> dict[str, Any]:
  1699	    """Authenticate the active artifact and classify the pre/post trigger.
  1700	
  1701	    This is the U2 hook shape for §5A. It performs no writes and returns one of
  1702	    the four closed outcomes required by the cold-gate brief.
  1703	    """
  1704	
  1705	    empty_snapshot = isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
  1706	    if not empty_snapshot:
  1707	        raise TypeError("ledger_snapshot must be a CalibrationLedgerSnapshot")
  1708	    registry = load_calibration_acceptance_registry(
  1709	        registry_path,
  1710	        repo_root=repo_root,
  1711	        require_committed=require_committed_registry,
  1712	    )
  1713	    active = _active_registry_entry(registry) if registry is not None else None
  1714	    artifact: dict[str, Any] | None = None
  1715	    if active is not None:
  1716	        try:
  1717	            raw = (Path(repo_root) / str(active["artifact_path"])).read_bytes()
  1718	        except OSError:
  1719	            raw = b""
  1720	        artifact = _acceptance_bound_from_authenticated_bytes(
  1721	            raw,
  1722	            expected_sha256=str(active["artifact_sha256"]),
  1723	        )
  1724	    if active is None or artifact is None:
  1725	        return _probe_result(
  1726	            outcome="authentication_or_epoch_refusal",
  1727	            active=active,
  1728	            artifact=artifact,
  1729	            snapshot=ledger_snapshot,
  1730	            observed_identity_epoch=observed_identity_epoch,
  1731	            refusal_reasons=("acceptance_registry_or_artifact_invalid",),
  1732	        )
  1733	    cutoff = artifact["ledger_cutoff"]
  1734	    allow_open = ledger_snapshot.is_governed_open_bracket_extension
  1735	    snapshot_reasons = set(ledger_snapshot.refusal_reasons)
  1736	    if (
  1737	        snapshot_reasons
  1738	        and not allow_open
  1739	        or allow_open
  1740	        and snapshot_reasons
  1741	        != {
  1742	            "calibration_ledger_bracket_session_open",
  1743	            "calibration_ledger_head_mismatch",
  1744	        }
  1745	        or ledger_snapshot.ledger_schema != LEDGER_SCHEMA
  1746	        or ledger_snapshot.head_sequence < cutoff["sequence"]
  1747	        or cutoff["sequence"] > len(ledger_snapshot.receipts)
  1748	        or cutoff["sequence"] > 0
  1749	        and ledger_snapshot.receipts[cutoff["sequence"] - 1].get("receipt_digest")
  1750	        != cutoff["head_digest"]
  1751	        or ledger_snapshot.head_sequence != len(ledger_snapshot.receipts)
  1752	        or ledger_snapshot.head_sequence > 0
  1753	        and ledger_snapshot.receipts[-1].get("receipt_digest")
  1754	        != ledger_snapshot.head_digest
  1755	        or not _prior_set_matches_import_cutoff_prefix(artifact, ledger_snapshot)
  1756	    ):
  1757	        return _probe_result(
  1758	            outcome="authentication_or_epoch_refusal",
  1759	            active=active,
  1760	            artifact=artifact,
  1761	            snapshot=ledger_snapshot,
  1762	            observed_identity_epoch=observed_identity_epoch,
  1763	            refusal_reasons=("calibration_ledger_prefix_not_authenticated",),
  1764	        )
  1765	    expected_epoch = artifact["identity_epoch"]
  1766	    if (
  1767	        not isinstance(observed_identity_epoch, Mapping)
  1768	        or set(observed_identity_epoch) != set(ACCEPTANCE_IDENTITY_FIELDS)
  1769	        or any(
  1770	            observed_identity_epoch.get(field) != expected_epoch.get(field)
  1771	            for field in ACCEPTANCE_IDENTITY_FIELDS
  1772	        )
  1773	    ):
  1774	        return _probe_result(
  1775	            outcome="authentication_or_epoch_refusal",
  1776	            active=active,
  1777	            artifact=artifact,
  1778	            snapshot=ledger_snapshot,
  1779	            observed_identity_epoch=observed_identity_epoch,
  1780	            triggers=("identity_field_change",),
  1781	            refusal_reasons=("observed_identity_epoch_mismatch",),
  1782	        )
  1783	    prospective = artifact["prospective_rederivation"]
  1784	    if (
  1785	        prospective.get("protocol_sha256") != protocol_sha256(PROTOCOL_ID)
  1786	        or prospective.get("estimator_code_sha256")
  1787	        != _current_estimator_code_sha256()
  1788	    ):
  1789	        return _probe_result(
  1790	            outcome="authentication_or_epoch_refusal",
  1791	            active=active,
  1792	            artifact=artifact,
  1793	            snapshot=ledger_snapshot,
  1794	            observed_identity_epoch=observed_identity_epoch,
  1795	            triggers=("protocol_or_estimator_byte_change",),
  1796	            refusal_reasons=("protocol_or_estimator_bytes_changed",),
  1797	        )
  1798	    grouped_result = _group_probe_observations(
  1799	        _probe_observation_universe(ledger_snapshot)
  1800	    )
  1801	    if grouped_result is None:
  1802	        return _probe_result(
  1803	            outcome="authentication_or_epoch_refusal",
  1804	            active=active,
  1805	            artifact=artifact,
  1806	            snapshot=ledger_snapshot,
  1807	            observed_identity_epoch=observed_identity_epoch,
  1808	            refusal_reasons=("conflicting_content_classification_or_bytes",),
  1809	        )
  1810	    grouped, noncontent = grouped_result
  1811	    prior_ids = _artifact_prior_content_ids(artifact)
  1812	    new_ids = sorted(set(grouped) - prior_ids)
  1813	    new_observations = [grouped[content_id][0] for content_id in new_ids]
  1814	    new_noncontent = [
  1815	        observation
  1816	        for observation in noncontent
  1817	        if observation.sequence > cutoff["sequence"]
  1818	    ]
  1819	    if new_noncontent or any(
  1820	        observation.classification_disposition
  1821	        not in {"valid", "systematic-invalid", "ordinary-invalid"}
  1822	        for observation in new_observations
  1823	    ):
  1824	        return _probe_result(
  1825	            outcome="authentication_or_epoch_refusal",
  1826	            active=active,
  1827	            artifact=artifact,
  1828	            snapshot=ledger_snapshot,
  1829	            observed_identity_epoch=observed_identity_epoch,
  1830	            new_content_ids=new_ids,
  1831	            refusal_reasons=("unresolved_or_unclassifiable_observation",),
  1832	        )
  1833	    if verify_custody and any(
  1834	        not _observation_custody_authentic(observation)
  1835	        for observation in new_observations
  1836	    ):
  1837	        return _probe_result(
  1838	            outcome="authentication_or_epoch_refusal",
  1839	            active=active,
  1840	            artifact=artifact,
  1841	            snapshot=ledger_snapshot,
  1842	            observed_identity_epoch=observed_identity_epoch,
  1843	            new_content_ids=new_ids,
  1844	            refusal_reasons=("new_observation_custody_or_physics_invalid",),
  1845	        )
  1846	    preflight = _decimal(
  1847	        artifact["decimal_derivation"]["ratified_operatives"][
  1848	            "preflight_level_screen_s"
  1849	        ]
  1850	    )
  1851	    if preflight is None:
  1852	        return _probe_result(
  1853	            outcome="authentication_or_epoch_refusal",
  1854	            active=active,
  1855	            artifact=artifact,
  1856	            snapshot=ledger_snapshot,
  1857	            observed_identity_epoch=observed_identity_epoch,
  1858	            refusal_reasons=("active_preflight_screen_invalid",),
  1859	        )
  1860	    systematic = [
  1861	        observation
  1862	        for observation in new_observations
  1863	        if dict(observation.identity_epoch) == dict(expected_epoch)
  1864	        and (
  1865	            observation.classification_disposition == "systematic-invalid"
  1866	            or observation.classification_disposition == "valid"
  1867	            and (
  1868	                (bound := _decimal(observation.exact_bound_lexeme_s)) is None
  1869	                or bound > preflight
  1870	            )
  1871	        )
  1872	    ]
  1873	    if systematic:
  1874	        return _probe_result(
  1875	            outcome="systematic_refusal",
  1876	            active=active,
  1877	            artifact=artifact,
  1878	            snapshot=ledger_snapshot,
  1879	            observed_identity_epoch=observed_identity_epoch,
  1880	            new_content_ids=new_ids,
  1881	            triggers=("new_systematic_failure_challenges_preflight_screen",),
  1882	            refusal_reasons=(SUCCESSOR_SYSTEMATIC_POLICY,),
  1883	        )
  1884	    corpus_values = _artifact_corpus_values(artifact)
  1885	    if not corpus_values:
  1886	        return _probe_result(
  1887	            outcome="authentication_or_epoch_refusal",
  1888	            active=active,
  1889	            artifact=artifact,
  1890	            snapshot=ledger_snapshot,
  1891	            observed_identity_epoch=observed_identity_epoch,
  1892	            refusal_reasons=("active_derivation_corpus_invalid",),
  1893	        )
  1894	    new_valid_same_epoch = [
  1895	        observation
  1896	        for observation in new_observations
  1897	        if observation.classification_disposition == "valid"
  1898	        and dict(observation.identity_epoch) == dict(expected_epoch)
  1899	    ]
  1900	    triggers: list[str] = []
  1901	    if any(
  1902	        (bound := _decimal(observation.exact_bound_lexeme_s)) is not None
  1903	        and (bound < min(corpus_values) or bound > max(corpus_values))
  1904	        for observation in new_valid_same_epoch
  1905	    ):
  1906	        triggers.append("new_valid_same_identity_capture_expands_observed_range")
  1907	    total_valid_same_epoch = sum(
  1908	        aliases[0].classification_disposition == "valid"
  1909	        and dict(aliases[0].identity_epoch) == dict(expected_epoch)
  1910	        for aliases in grouped.values()
   130	
   131	
   132	def _attempt_row(observation: LedgerObservation) -> dict[str, Any]:
   133	    return {
   134	        "attempt_id": observation.attempt_id,
   135	        "finalization_sequence": observation.sequence,
   136	        "receipt_digest": observation.receipt_digest,
   137	        "observation_kind": observation.observation_kind,
   138	        "custody_locator": observation.custody_locator,
   139	        "exact_bound_lexeme_s": observation.exact_bound_lexeme_s,
   140	        "manifest_sha256": observation.artifact_sha256.get("manifest.json"),
   141	        "instrument_evidence_sha256": observation.artifact_sha256.get(
   142	            "instrument_evidence.json"
   143	        ),
   144	    }
   145	
   146	
   147	def _governed_unused_slots(
   148	    snapshot: CalibrationLedgerSnapshot,
   149	) -> list[dict[str, Any]]:
   150	    """Record only unused U1 slots whose terminal abort proves no capture."""
   151	
   152	    rows: list[dict[str, Any]] = []
   153	    receipts_by_session: dict[str, list[Mapping[str, Any]]] = {}
   154	    for receipt in snapshot.receipts:
   155	        session_id = receipt.get("session_id")
   156	        if isinstance(session_id, str):
   157	            receipts_by_session.setdefault(session_id, []).append(receipt)
   158	    for session in snapshot.bracket_sessions:
   159	        if session.state != "aborted":
   160	            continue
   161	        receipts = receipts_by_session.get(session.session_id, [])
   162	        opens = [receipt for receipt in receipts if receipt.get("event") == "bracket-session-open"]
   163	        aborts = [
   164	            receipt
   165	            for receipt in receipts
   166	            if receipt.get("event") == BRACKET_SESSION_ABORT_EVENT
   167	        ]
   168	        if len(opens) != 1 or len(aborts) != 1:
   169	            raise ValueError("aborted bracket session lacks one authenticated closure")
   170	        opened = opens[0]
   171	        aborted = aborts[0]
   172	        for slot in aborted["unused_slots"]:
   173	            reservation = opened["slots"][slot]
   174	            rows.append(
   175	                {
   176	                    "attempt_id": reservation["attempt_id"],
   177	                    "closure_sequence": aborted["sequence"],
   178	                    "receipt_digest": aborted["receipt_digest"],
   179	                    "disposition": "governed-unused-slot",
   180	                    "custody_locator": reservation["custody_locator"],
   181	                }
   182	            )
   183	    return rows
   184	
   185	
   186	def _noncontent_rows(
   187	    noncontent: Sequence[LedgerObservation],
   188	    snapshot: CalibrationLedgerSnapshot,
   189	) -> list[dict[str, Any]]:
   190	    if noncontent:
   191	        # A terminal `abandoned` receipt can still conceal already-created
   192	        # classifiable bytes. Q6 requires a ruling before automatic issuance.
   193	        raise ValueError("noncontent observation blocks automatic successor issuance")
   194	    return sorted(
   195	        _governed_unused_slots(snapshot),
   196	        key=lambda row: (row["closure_sequence"], row["attempt_id"]),
   197	    )
   198	
   199	
   200	def _load_parent_artifact(
   201	    registry: Mapping[str, Any], repo_root: Path
   202	) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
   203	    active = _active_registry_entry(registry)
   204	    if active is None:
   205	        raise ValueError("acceptance registry does not have one active entry")
   225	        or snapshot.committed_head_sequence != snapshot.head_sequence
   226	        or snapshot.committed_head_digest != snapshot.head_digest
   227	        or snapshot.receipts[-1].get("receipt_digest") != snapshot.head_digest
   228	        or snapshot.receipts[-1].get("event")
   229	        in {"reservation", "bracket-session-open", "bracket-session-slot-claim"}
   230	    ):
   231	        raise ValueError("successor issuance requires a committed terminal ledger head")
   232	
   233	
   234	def build_calibration_acceptance_successor(
   235	    ledger_snapshot: CalibrationLedgerSnapshot,
   236	    *,
   237	    observed_identity_epoch: Mapping[str, Any],
   238	    registry_path: Path = DEFAULT_ACCEPTANCE_REGISTRY_PATH,
   239	    repo_root: Path = REPO_ROOT,
   240	    require_committed_registry: bool = True,
   241	    verify_custody: bool = True,
   242	) -> SuccessorBuild:
   243	    """Build deterministic artifact and registry buffers without writing."""
   244	
   245	    repo_root = Path(repo_root).resolve()
   246	    _assert_terminal_committed_snapshot(ledger_snapshot)
   247	    registry = load_calibration_acceptance_registry(
   248	        registry_path,
   249	        repo_root=repo_root,
   250	        require_committed=require_committed_registry,
   251	    )
   252	    if registry is None:
   253	        raise ValueError("acceptance registry is invalid or uncommitted")
   254	    parent_entry, parent = _load_parent_artifact(registry, repo_root)
   255	    parent_probe = probe_calibration_acceptance_trigger(
   256	        ledger_snapshot,
   257	        observed_identity_epoch=observed_identity_epoch,
   258	        registry_path=registry_path,
   259	        repo_root=repo_root,
   260	        require_committed_registry=require_committed_registry,
   261	        verify_custody=verify_custody,
   262	    )
   263	    if parent_probe["outcome"] != "successor_required":
   264	        raise ValueError(
   265	            f"active artifact does not require a successor: {parent_probe['outcome']}"
   266	        )
   267	
   268	    grouped_result = _group_probe_observations(
   269	        _probe_observation_universe(ledger_snapshot)
   270	    )
   271	    if grouped_result is None:
   272	        raise ValueError("content identity has conflicting classifications or bytes")
   273	    grouped, noncontent = grouped_result
   274	    noncontent_rows = _noncontent_rows(noncontent, ledger_snapshot)
   275	    active_epoch = dict(parent["identity_epoch"])
   276	    if dict(observed_identity_epoch) != active_epoch:
   277	        raise ValueError("observed identity epoch differs from the parent artifact")
   278	
   279	    epoch_values: dict[str, dict[str, Any]] = {"active_epoch": active_epoch}
   280	    prior_rows: list[dict[str, Any]] = []
   281	    corpus_members: list[dict[str, Any]] = []
   282	    for content_id, aliases in grouped.items():
   283	        representative = aliases[0]
   284	        epoch_id = _epoch_id(representative.identity_epoch, active_epoch)
   285	        epoch_values.setdefault(epoch_id, dict(representative.identity_epoch))
   286	        prior_rows.append(
   287	            {
   288	                "content_id": content_id,
   289	                "epoch_id": epoch_id,
   290	                "disposition": representative.classification_disposition,
   291	                "representative_attempt_id": representative.attempt_id,
   292	                "attempts": [_attempt_row(alias) for alias in aliases],
   293	            }
   294	        )
   295	        if (
   296	            representative.classification_disposition != "valid"
   297	            or epoch_id != "active_epoch"
   298	        ):
   299	            continue
   300	        if verify_custody and any(
   301	            not _observation_custody_authentic(alias) for alias in aliases
   302	        ):
   303	            raise ValueError("selected corpus member fails custody reauthentication")
   304	        bound = representative.exact_bound_lexeme_s
   305	        if not isinstance(bound, str):
   306	            raise ValueError("selected corpus member lacks an exact bound lexeme")
   307	        corpus_members.append(
   308	            {
   309	                "content_id": content_id,
   310	                "attempt_id": representative.attempt_id,
   311	                "finalization_sequence": representative.sequence,
   312	                "receipt_digest": representative.receipt_digest,
   313	                "custody_locator": representative.custody_locator,
   314	                "b_fiducial_s": bound,
   315	                "manifest_sha256": representative.artifact_sha256.get(
   316	                    "manifest.json"
   317	                ),
   318	                "instrument_evidence_sha256": representative.artifact_sha256.get(
   319	                    "instrument_evidence.json"
   320	                ),
   321	            }
   322	        )
   323	    prior_rows.sort(key=lambda row: row["content_id"])
   324	    corpus_members.sort(key=lambda member: member["content_id"])
   325	    if len(corpus_members) < 2:
   326	        raise ValueError("successor corpus has fewer than two valid same-epoch members")
   327	
   328	    derivation = derive_successor_decimal_derivation(corpus_members)
   329	    parent_boundary = _artifact_count_boundary(parent)
   330	    count = len(corpus_members)
   331	    next_boundary = parent_boundary if count < parent_boundary else 2 * count
   332	    cutoff_core = {
   333	        "sequence": ledger_snapshot.head_sequence,
   334	        "head_digest": ledger_snapshot.head_digest,
   335	        "ledger_schema": LEDGER_SCHEMA,
   336	    }
   337	    acceptance_id = (
   338	        f"d079_calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
   339	        f"{ledger_snapshot.head_digest[:16]}"
   340	    )
   341	    artifact_path = (
   342	        "configs/calibration/"
   343	        f"calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
   344	        f"{ledger_snapshot.head_digest[:16]}.json"
   345	    )
   325	    if len(corpus_members) < 2:
   326	        raise ValueError("successor corpus has fewer than two valid same-epoch members")
   327	
   328	    derivation = derive_successor_decimal_derivation(corpus_members)
   329	    parent_boundary = _artifact_count_boundary(parent)
   330	    count = len(corpus_members)
   331	    next_boundary = parent_boundary if count < parent_boundary else 2 * count
   332	    cutoff_core = {
   333	        "sequence": ledger_snapshot.head_sequence,
   334	        "head_digest": ledger_snapshot.head_digest,
   335	        "ledger_schema": LEDGER_SCHEMA,
   336	    }
   337	    acceptance_id = (
   338	        f"d079_calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
   339	        f"{ledger_snapshot.head_digest[:16]}"
   340	    )
   341	    artifact_path = (
   342	        "configs/calibration/"
   343	        f"calibration_acceptance_v3_s{ledger_snapshot.head_sequence}_"
   344	        f"{ledger_snapshot.head_digest[:16]}.json"
   345	    )
   346	    root_acceptance_id = (
   347	        parent["lineage"]["root_acceptance_id"]
   348	        if parent.get("schema_version") == ACCEPTANCE_SUCCESSOR_SCHEMA
   349	        else parent["acceptance_id"]
   350	    )
   351	    parent_cutoff = {
   352	        key: parent["ledger_cutoff"][key]
   353	        for key in ("sequence", "head_digest", "ledger_schema")
   354	    }
   355	    artifact: dict[str, Any] = {
   356	        "schema_version": ACCEPTANCE_SUCCESSOR_SCHEMA,
   357	        "acceptance_id": acceptance_id,
   358	        "decision_ids": list(SUCCESSOR_DECISION_IDS),
   359	        "artifact_role": "issued",
   360	        "issuance": {
   361	            "status": "issued",
   362	            "claim_eligible": True,
   363	            "reason": (
   364	                "authenticated live-prefix trigger judged under the parent "
   365	                "artifact and rederived under D-102/D-109/D-117"
   366	            ),
   367	        },
   368	        "lineage": {
   369	            "generation": int(parent_entry["generation"]) + 1,
   370	            "root_acceptance_id": root_acceptance_id,
   371	            "parent_acceptance_id": parent["acceptance_id"],
   372	            "parent_artifact_sha256": parent_entry["artifact_sha256"],
   373	            "parent_derivation_sha256": parent["derivation_sha256"],
   374	            "parent_ledger_cutoff": parent_cutoff,
   375	            "trigger_judgment": {
   376	                "judged_under_acceptance_id": parent["acceptance_id"],
   377	                "judged_under_artifact_sha256": parent_entry["artifact_sha256"],
   378	                "result": "successor_required",
   379	                "new_content_ids": list(parent_probe["new_content_ids"]),
   380	                "triggers": list(parent_probe["observed_triggers"]),
   381	            },
   382	        },
   383	        "ledger_cutoff": {**cutoff_core, "role": "issued_acceptance_baseline"},
   384	        "identity_epoch": active_epoch,
   385	        "prospective_rederivation": {
   386	            "calendar_expiry": None,
   387	            "trigger_observation_rule": "judge_under_prior_artifact_never_self_fit",
   388	            "triggers": [
   389	                "identity_field_change",
   390	                "protocol_or_estimator_byte_change",
   391	                "new_valid_same_identity_capture_expands_observed_range",
   392	                "content_distinct_valid_same_epoch_count_boundary",
   393	                "new_systematic_failure_challenges_preflight_screen",
   394	            ],
   395	            "protocol_sha256": protocol_sha256(PROTOCOL_ID),
   396	            "estimator_code_sha256": parent["prospective_rederivation"][
   397	                "estimator_code_sha256"
   398	            ],
   399	            "count_trigger": {
   400	                "source_corpus_count": count,
   401	                "next_boundary": next_boundary,
   402	                "rule": SUCCESSOR_COUNT_BOUNDARY_RULE,
   403	            },
   404	        },
   405	        "derivation_corpus": {
   406	            "selection": SUCCESSOR_CORPUS_SELECTION,
   407	            "n": count,
   408	            "members": corpus_members,
   409	        },
   410	        "prior_observation_set": {
   411	            "cutoff": cutoff_core,
   412	            "content_identity_method": CONTENT_IDENTITY_METHOD,
   413	            "epoch_catalog": dict(sorted(epoch_values.items())),
   414	            "observations": prior_rows,
   415	            "noncontent_attempts": noncontent_rows,
   416	        },
   417	        "decimal_derivation": derivation,
   418	    }
   419	    artifact["derivation_sha256"] = _canonical_sha256(artifact)
   420	    if not _valid_acceptance_bound(artifact):
   421	        raise ValueError("constructed successor fails the production loader")
   422	    artifact_bytes = _pretty_json_bytes(artifact)
   423	    artifact_sha256 = hashlib.sha256(artifact_bytes).hexdigest()
   424	
   425	    registry_entries = []
   426	    for entry in registry["entries"]:
   427	        registry_entries.append({**entry, "active": False})
   428	    registry_entries.append(
   429	        {
   430	            "acceptance_id": acceptance_id,
   431	            "artifact_path": artifact_path,
   432	            "artifact_sha256": artifact_sha256,
   433	            "derivation_sha256": artifact["derivation_sha256"],
   434	            "artifact_schema": ACCEPTANCE_SUCCESSOR_SCHEMA,
   435	            "generation": int(parent_entry["generation"]) + 1,
   436	            "active": True,
   437	            "parent_acceptance_id": parent["acceptance_id"],
   438	            "parent_artifact_sha256": parent_entry["artifact_sha256"],
   439	            "ledger_cutoff": cutoff_core,
   440	        }
   441	    )
   442	    proposed_registry = {
   443	        "schema_version": ACCEPTANCE_REGISTRY_SCHEMA,
   444	        "authority": ACCEPTANCE_REGISTRY_AUTHORITY,
   445	        "entries": registry_entries,
   446	    }
   447	    if not _valid_registry(proposed_registry):
   448	        raise ValueError("constructed registry fails ancestry validation")
   449	    registry_bytes = _pretty_json_bytes(proposed_registry)
   450	
   451	    # Step 16's self-fit guard is explicit: every parent-new content ID is now
   452	    # in the successor prior set, while the next count boundary is above n.
   453	    successor_prior_ids = {row["content_id"] for row in prior_rows}
   454	    if not set(parent_probe["new_content_ids"]).issubset(successor_prior_ids):
   455	        raise ValueError("successor omits a parent-judged trigger observation")
   456	    successor_probe = {
   457	        "outcome": "accepted_under_active_artifact",
   458	        "active_acceptance_id": acceptance_id,
   459	        "new_content_ids": [],
   460	        "observed_triggers": [],
   461	        "parent_judgment_policy": POST_SUCCESSOR_POLICY,
   462	    }
   463	    return SuccessorBuild(
   464	        artifact=artifact,
   465	        artifact_bytes=artifact_bytes,
   466	        artifact_sha256=artifact_sha256,
   467	        registry=proposed_registry,
   468	        registry_bytes=registry_bytes,
   469	        registry_sha256=hashlib.sha256(registry_bytes).hexdigest(),
   470	        artifact_path=artifact_path,
   471	        head_pin=cutoff_core,
   472	        parent_probe=parent_probe,
   473	        successor_probe=successor_probe,
   474	    )
   475	
   500	
   501	
   502	def publish_successor(
   503	    build: SuccessorBuild,
   504	    *,
   505	    artifact_destination: Path,
   506	    registry_destination: Path,
   507	    expected_registry_bytes: bytes,
   508	    repo_root: Path = REPO_ROOT,
   509	) -> None:
   510	    """Publish validated buffers with the registry as the commit point."""
   511	
   512	    repo_root = Path(repo_root).resolve()
   513	    artifact_destination = Path(artifact_destination)
   514	    registry_destination = Path(registry_destination)
   515	    expected_artifact = repo_root / build.artifact_path
   516	    expected_registry = (
   517	        repo_root / "configs/calibration/calibration_acceptance_registry.json"
   518	    )
   519	    if (
   520	        artifact_destination.resolve(strict=False)
   521	        != expected_artifact.resolve(strict=False)
   522	        or registry_destination.resolve(strict=False)
   523	        != expected_registry.resolve(strict=False)
   524	        or artifact_destination.is_symlink()
   525	        or registry_destination.is_symlink()
   526	    ):
   527	        raise ValueError("issuance destinations changed or are substituted")
   528	    try:
   529	        registry_stat = registry_destination.stat()
   530	    except OSError as exc:
   531	        raise ValueError("registry destination is absent") from exc
   532	    if not stat.S_ISREG(registry_stat.st_mode) or registry_stat.st_nlink != 1:
   533	        raise ValueError("registry destination is not one regular unaliased file")
   534	    lock_path = registry_destination.with_name(f"{registry_destination.name}.lock")
   535	    flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
   536	    try:
   537	        lock_descriptor = os.open(lock_path, flags, 0o600)
   538	    except OSError as exc:
   539	        raise ValueError("registry lock is unavailable or substituted") from exc
   540	    try:
   541	        lock_stat = os.fstat(lock_descriptor)
   542	        if not stat.S_ISREG(lock_stat.st_mode) or lock_stat.st_nlink != 1:
   543	            raise ValueError("registry lock is not one regular unaliased file")
   544	        fcntl.flock(lock_descriptor, fcntl.LOCK_EX)
   545	        if registry_destination.read_bytes() != expected_registry_bytes:
   546	            raise ValueError("registry changed since the successor was built")
   547	        artifact_already_published = artifact_destination.exists()
   548	        if (
   549	            artifact_already_published
   550	            and artifact_destination.read_bytes() != build.artifact_bytes
   551	        ):
   552	            raise ValueError("immutable successor artifact path is occupied")
   553	        artifact_stage = (
   554	            None
   555	            if artifact_already_published
   556	            else _stage_bytes(artifact_destination, build.artifact_bytes)
   557	        )
   558	        registry_stage = _stage_bytes(registry_destination, build.registry_bytes)
   559	        try:
   560	            # An interruption after this replace leaves only an inert
   561	            # unregistered immutable artifact. Authority changes only at the
   562	            # registry replace; an exact orphan is an idempotent retry state.
   563	            if artifact_stage is not None:
   564	                os.replace(artifact_stage, artifact_destination)
   565	                _fsync_directory(artifact_destination.parent)
   566	            os.replace(registry_stage, registry_destination)
   567	            try:
   568	                _fsync_directory(registry_destination.parent)
   569	            except OSError as exc:
   570	                raise SuccessorDurabilityUncertain(
   571	                    "registry committed with directory durability uncertain"
   572	                ) from exc
   573	        finally:
   574	            if artifact_stage is not None:
   575	                artifact_stage.unlink(missing_ok=True)
   576	            registry_stage.unlink(missing_ok=True)
   577	    finally:
   578	        os.close(lock_descriptor)
   579	
   580	
   581	def _parser() -> argparse.ArgumentParser:
   582	    parser = argparse.ArgumentParser(description=__doc__)
   583	    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
   584	    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
   585	    parser.add_argument(

exec
/bin/zsh -lc "git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '1838,1915p'
git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '780,835p'
git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '1010,1115p'
git show origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py | nl -ba | sed -n '145,200p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
  1838	            outcome="authentication_or_epoch_refusal",
  1839	            active=active,
  1840	            artifact=artifact,
  1841	            snapshot=ledger_snapshot,
  1842	            observed_identity_epoch=observed_identity_epoch,
  1843	            new_content_ids=new_ids,
  1844	            refusal_reasons=("new_observation_custody_or_physics_invalid",),
  1845	        )
  1846	    preflight = _decimal(
  1847	        artifact["decimal_derivation"]["ratified_operatives"][
  1848	            "preflight_level_screen_s"
  1849	        ]
  1850	    )
  1851	    if preflight is None:
  1852	        return _probe_result(
  1853	            outcome="authentication_or_epoch_refusal",
  1854	            active=active,
  1855	            artifact=artifact,
  1856	            snapshot=ledger_snapshot,
  1857	            observed_identity_epoch=observed_identity_epoch,
  1858	            refusal_reasons=("active_preflight_screen_invalid",),
  1859	        )
  1860	    systematic = [
  1861	        observation
  1862	        for observation in new_observations
  1863	        if dict(observation.identity_epoch) == dict(expected_epoch)
  1864	        and (
  1865	            observation.classification_disposition == "systematic-invalid"
  1866	            or observation.classification_disposition == "valid"
  1867	            and (
  1868	                (bound := _decimal(observation.exact_bound_lexeme_s)) is None
  1869	                or bound > preflight
  1870	            )
  1871	        )
  1872	    ]
  1873	    if systematic:
  1874	        return _probe_result(
  1875	            outcome="systematic_refusal",
  1876	            active=active,
  1877	            artifact=artifact,
  1878	            snapshot=ledger_snapshot,
  1879	            observed_identity_epoch=observed_identity_epoch,
  1880	            new_content_ids=new_ids,
  1881	            triggers=("new_systematic_failure_challenges_preflight_screen",),
  1882	            refusal_reasons=(SUCCESSOR_SYSTEMATIC_POLICY,),
  1883	        )
  1884	    corpus_values = _artifact_corpus_values(artifact)
  1885	    if not corpus_values:
  1886	        return _probe_result(
  1887	            outcome="authentication_or_epoch_refusal",
  1888	            active=active,
  1889	            artifact=artifact,
  1890	            snapshot=ledger_snapshot,
  1891	            observed_identity_epoch=observed_identity_epoch,
  1892	            refusal_reasons=("active_derivation_corpus_invalid",),
  1893	        )
  1894	    new_valid_same_epoch = [
  1895	        observation
  1896	        for observation in new_observations
  1897	        if observation.classification_disposition == "valid"
  1898	        and dict(observation.identity_epoch) == dict(expected_epoch)
  1899	    ]
  1900	    triggers: list[str] = []
  1901	    if any(
  1902	        (bound := _decimal(observation.exact_bound_lexeme_s)) is not None
  1903	        and (bound < min(corpus_values) or bound > max(corpus_values))
  1904	        for observation in new_valid_same_epoch
  1905	    ):
  1906	        triggers.append("new_valid_same_identity_capture_expands_observed_range")
  1907	    total_valid_same_epoch = sum(
  1908	        aliases[0].classification_disposition == "valid"
  1909	        and dict(aliases[0].identity_epoch) == dict(expected_epoch)
  1910	        for aliases in grouped.values()
  1911	    )
  1912	    if total_valid_same_epoch >= _artifact_count_boundary(artifact):
  1913	        triggers.append("content_distinct_valid_same_epoch_count_boundary")
  1914	    outcome = "successor_required" if triggers else "accepted_under_active_artifact"
  1915	    return _probe_result(
   780	        parent_entry = entries_by_id.get(entry["parent_acceptance_id"])
   781	        parent = artifacts_by_id.get(entry["parent_acceptance_id"])
   782	        if parent_entry is None or parent is None:
   783	            return None
   784	        count = artifact["derivation_corpus"]["n"]
   785	        parent_boundary = _artifact_count_boundary(parent)
   786	        expected_boundary = parent_boundary if count < parent_boundary else 2 * count
   787	        if (
   788	            lineage["generation"] != entry["generation"]
   789	            or lineage["parent_acceptance_id"] != entry["parent_acceptance_id"]
   790	            or lineage["parent_artifact_sha256"] != parent_entry["artifact_sha256"]
   791	            or lineage["parent_derivation_sha256"] != parent["derivation_sha256"]
   792	            or lineage["parent_ledger_cutoff"] != parent_entry["ledger_cutoff"]
   793	            or artifact["prospective_rederivation"]["count_trigger"][
   794	                "next_boundary"
   795	            ]
   796	            != expected_boundary
   797	        ):
   798	            return None
   799	    return dict(value)
   800	
   801	
   802	def _active_registry_entry(registry: Mapping[str, Any]) -> Mapping[str, Any] | None:
   803	    active = [
   804	        entry
   805	        for entry in registry.get("entries", ())
   806	        if isinstance(entry, Mapping) and entry.get("active") is True
   807	    ]
   808	    return active[0] if len(active) == 1 else None
   809	
   810	
   811	def _valid_successor_acceptance_bound(value: Mapping[str, Any]) -> bool:
   812	    if (
   813	        set(value) != _SUCCESSOR_TOP_LEVEL_FIELDS
   814	        or value.get("schema_version") != ACCEPTANCE_SUCCESSOR_SCHEMA
   815	        or value.get("artifact_role") != "issued"
   816	        or not isinstance(value.get("acceptance_id"), str)
   817	        or not value["acceptance_id"].startswith("d079_calibration_acceptance_v3_s")
   818	        or value.get("decision_ids") != list(SUCCESSOR_DECISION_IDS)
   819	        or value.get("derivation_sha256")
   820	        != _canonical_sha256(
   821	            {key: item for key, item in value.items() if key != "derivation_sha256"}
   822	        )
   823	    ):
   824	        return False
   825	    issuance = value.get("issuance")
   826	    lineage = value.get("lineage")
   827	    cutoff = value.get("ledger_cutoff")
   828	    identity = value.get("identity_epoch")
   829	    prospective = value.get("prospective_rederivation")
   830	    corpus = value.get("derivation_corpus")
   831	    prior = value.get("prior_observation_set")
   832	    derivation = value.get("decimal_derivation")
   833	    if (
   834	        not isinstance(issuance, Mapping)
   835	        or set(issuance) != {"status", "claim_eligible", "reason"}
  1010	            not isinstance(epoch_id, str)
  1011	            or not epoch_id
  1012	            or not isinstance(epoch, Mapping)
  1013	            or set(epoch) != set(ACCEPTANCE_IDENTITY_FIELDS)
  1014	            or any(epoch.get(field) in (None, "") for field in ACCEPTANCE_IDENTITY_FIELDS)
  1015	            for epoch_id, epoch in prior["epoch_catalog"].items()
  1016	        )
  1017	        or len(
  1018	            {
  1019	                tuple((field, epoch[field]) for field in ACCEPTANCE_IDENTITY_FIELDS)
  1020	                for epoch in prior["epoch_catalog"].values()
  1021	            }
  1022	        )
  1023	        != len(prior["epoch_catalog"])
  1024	        or not isinstance(prior.get("observations"), list)
  1025	        or not isinstance(prior.get("noncontent_attempts"), list)
  1026	    ):
  1027	        return False
  1028	    for row in prior["noncontent_attempts"]:
  1029	        if (
  1030	            not isinstance(row, Mapping)
  1031	            or set(row)
  1032	            != {
  1033	                "attempt_id",
  1034	                "closure_sequence",
  1035	                "receipt_digest",
  1036	                "disposition",
  1037	                "custody_locator",
  1038	            }
  1039	            or not isinstance(row.get("attempt_id"), str)
  1040	            or not row["attempt_id"]
  1041	            or isinstance(row.get("closure_sequence"), bool)
  1042	            or not isinstance(row.get("closure_sequence"), int)
  1043	            or row["closure_sequence"] < 1
  1044	            or row["closure_sequence"] > cutoff["sequence"]
  1045	            or not _valid_sha256(row.get("receipt_digest"))
  1046	            or row.get("disposition") != "governed-unused-slot"
  1047	            or not isinstance(row.get("custody_locator"), str)
  1048	            or not row["custody_locator"]
  1049	        ):
  1050	            return False
  1051	    prior_ids: list[str] = []
  1052	    valid_active_ids: set[str] = set()
  1053	    prior_by_id: dict[str, Mapping[str, Any]] = {}
  1054	    all_attempt_ids: set[str] = set()
  1055	    all_sequences: set[int] = set()
  1056	    all_receipts: set[str] = set()
  1057	    for observation in prior["observations"]:
  1058	        if (
  1059	            not isinstance(observation, Mapping)
  1060	            or set(observation)
  1061	            != {
  1062	                "content_id",
  1063	                "epoch_id",
  1064	                "disposition",
  1065	                "representative_attempt_id",
  1066	                "attempts",
  1067	            }
  1068	            or not _valid_sha256(observation.get("content_id"))
  1069	            or observation.get("epoch_id") not in prior["epoch_catalog"]
  1070	            or observation.get("disposition")
  1071	            not in {"valid", "systematic-invalid", "ordinary-invalid"}
  1072	            or not isinstance(observation.get("representative_attempt_id"), str)
  1073	            or not isinstance(observation.get("attempts"), list)
  1074	            or not observation["attempts"]
  1075	        ):
  1076	            return False
  1077	        attempts = observation["attempts"]
  1078	        sequences: list[int] = []
  1079	        for attempt in attempts:
  1080	            if (
  1081	                not isinstance(attempt, Mapping)
  1082	                or set(attempt)
  1083	                != {
  1084	                    "attempt_id",
  1085	                    "finalization_sequence",
  1086	                    "receipt_digest",
  1087	                    "observation_kind",
  1088	                    "custody_locator",
  1089	                    "exact_bound_lexeme_s",
  1090	                    "manifest_sha256",
  1091	                    "instrument_evidence_sha256",
  1092	                }
  1093	                or not isinstance(attempt.get("attempt_id"), str)
  1094	                or not attempt["attempt_id"]
  1095	                or isinstance(attempt.get("finalization_sequence"), bool)
  1096	                or not isinstance(attempt.get("finalization_sequence"), int)
  1097	                or attempt["finalization_sequence"] < 1
  1098	                or attempt["finalization_sequence"] > cutoff["sequence"]
  1099	                or not _valid_sha256(attempt.get("receipt_digest"))
  1100	                or attempt.get("observation_kind")
  1101	                not in {
  1102	                    "historical-import",
  1103	                    "live-capture",
  1104	                    "bracket-session-finalized",
  1105	                    "bracket-session-aborted",
  1106	                }
  1107	                or not isinstance(attempt.get("custody_locator"), str)
  1108	                or not attempt["custody_locator"]
  1109	                or not _valid_sha256(attempt.get("manifest_sha256"))
  1110	                or not _valid_sha256(attempt.get("instrument_evidence_sha256"))
  1111	                or (
  1112	                    attempt.get("exact_bound_lexeme_s") is not None
  1113	                    and (
  1114	                        (attempt_bound := _decimal(attempt["exact_bound_lexeme_s"]))
  1115	                        is None
   145	
   146	
   147	def _governed_unused_slots(
   148	    snapshot: CalibrationLedgerSnapshot,
   149	) -> list[dict[str, Any]]:
   150	    """Record only unused U1 slots whose terminal abort proves no capture."""
   151	
   152	    rows: list[dict[str, Any]] = []
   153	    receipts_by_session: dict[str, list[Mapping[str, Any]]] = {}
   154	    for receipt in snapshot.receipts:
   155	        session_id = receipt.get("session_id")
   156	        if isinstance(session_id, str):
   157	            receipts_by_session.setdefault(session_id, []).append(receipt)
   158	    for session in snapshot.bracket_sessions:
   159	        if session.state != "aborted":
   160	            continue
   161	        receipts = receipts_by_session.get(session.session_id, [])
   162	        opens = [receipt for receipt in receipts if receipt.get("event") == "bracket-session-open"]
   163	        aborts = [
   164	            receipt
   165	            for receipt in receipts
   166	            if receipt.get("event") == BRACKET_SESSION_ABORT_EVENT
   167	        ]
   168	        if len(opens) != 1 or len(aborts) != 1:
   169	            raise ValueError("aborted bracket session lacks one authenticated closure")
   170	        opened = opens[0]
   171	        aborted = aborts[0]
   172	        for slot in aborted["unused_slots"]:
   173	            reservation = opened["slots"][slot]
   174	            rows.append(
   175	                {
   176	                    "attempt_id": reservation["attempt_id"],
   177	                    "closure_sequence": aborted["sequence"],
   178	                    "receipt_digest": aborted["receipt_digest"],
   179	                    "disposition": "governed-unused-slot",
   180	                    "custody_locator": reservation["custody_locator"],
   181	                }
   182	            )
   183	    return rows
   184	
   185	
   186	def _noncontent_rows(
   187	    noncontent: Sequence[LedgerObservation],
   188	    snapshot: CalibrationLedgerSnapshot,
   189	) -> list[dict[str, Any]]:
   190	    if noncontent:
   191	        # A terminal `abandoned` receipt can still conceal already-created
   192	        # classifiable bytes. Q6 requires a ruling before automatic issuance.
   193	        raise ValueError("noncontent observation blocks automatic successor issuance")
   194	    return sorted(
   195	        _governed_unused_slots(snapshot),
   196	        key=lambda row: (row["closure_sequence"], row["attempt_id"]),
   197	    )
   198	
   199	
   200	def _load_parent_artifact(

exec
/bin/zsh -lc "git grep -n 'is_governed_open_bracket_extension' origin/impl/d117-u2-successor --
git show origin/impl/d117-u2-successor:joulewise/calibration_ledger.py | nl -ba | sed -n '205,290p'
git show origin/impl/d117-u2-successor:joulewise/calibration_ledger.py | nl -ba | sed -n '1400,1510p'
git grep -n -E 'open.*probe|probe.*open|post.*successor|parent_judgment|governed-unused|persistent_refusal|count_boundary' origin/impl/d117-u2-successor -- tests/test_calibration_acceptance_successor.py tests/test_calibration_bracketing.py tests/test_calibration_ledger.py" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:1483:+    def is_governed_open_bracket_extension(self) -> bool:
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:3447:265:    def is_governed_open_bracket_extension(self) -> bool:
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:3746:   265	    def is_governed_open_bracket_extension(self) -> bool:
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:7362:+        and not ledger_snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:8059:920:        and not ledger_snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:8274:   920	        and not ledger_snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:9352:+        not snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:10063:   334	        not snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:14239:   **Failing scenario:** after finalizing PRE, call the familiar generic helper. My probe successfully produced a sequence-2 pin candidate for `slot=pre`. If committed, the snapshot has `bracket_session_open` but no head mismatch; `is_governed_open_bracket_extension` becomes false and the writer refuses the reserved POST, stranding the night. Reject bracket-open/PRE receipts in the generic helper and make `terminal_head_pin_for_session()` the only session pin route.
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-CONTRACT.md:14284:   **Failing scenario:** after finalizing PRE, call the familiar generic helper. My probe successfully produced a sequence-2 pin candidate for `slot=pre`. If committed, the snapshot has `bracket_session_open` but no head mismatch; `is_governed_open_bracket_extension` becomes false and the writer refuses the reserved POST, stranding the night. Reject bracket-open/PRE receipts in the generic helper and make `terminal_head_pin_for_session()` the only session pin route.
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:3272:   265	    def is_governed_open_bracket_extension(self) -> bool:
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:6526:   334	        not snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:8059:   920	        and not ledger_snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:docs/process_traces/2026-08-07-d117-u-units/U1-AUDIT-EXEC.md:8413:   920	        and not ledger_snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1581:    if snapshot.is_governed_open_bracket_extension:
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1734:    allow_open = ledger_snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2357:        and not ledger_snapshot.is_governed_open_bracket_extension
origin/impl/d117-u2-successor:joulewise/calibration_ledger.py:281:    def is_governed_open_bracket_extension(self) -> bool:
origin/impl/d117-u2-successor:scripts/validate_powermetrics_fiducial.py:335:        not snapshot.is_governed_open_bracket_extension
   205	    return {key: value for key, value in receipt.items() if key != "receipt_digest"}
   206	
   207	
   208	def _receipt_digest(receipt: Mapping[str, Any]) -> str:
   209	    return canonical_sha256(receipt_core(receipt))
   210	
   211	
   212	@dataclass(frozen=True)
   213	class LedgerObservation:
   214	    sequence: int
   215	    receipt_digest: str
   216	    attempt_id: str
   217	    content_id: str | None
   218	    artifact_sha256: Mapping[str, str]
   219	    identity_epoch: Mapping[str, Any]
   220	    t1_bindings: Mapping[str, Any]
   221	    capture_wall_time_s: str | None
   222	    exact_bound_lexeme_s: str | None
   223	    disposition: str
   224	    custody_locator: str
   225	    observation_kind: str = "live-capture"
   226	    bracket_session_id: str | None = None
   227	    bracket_slot: str | None = None
   228	    bracket_window_id: str | None = None
   229	    bracket_plan_id: str | None = None
   230	    bracket_plan_sha256: str | None = None
   231	    bracket_evidence_root_id: str | None = None
   232	    bracket_runs_root: str | None = None
   233	
   234	    @property
   235	    def classification_disposition(self) -> str:
   236	        """Map the writer terminal state onto the R2 observation schema."""
   237	
   238	        return (
   239	            "unresolved" if self.disposition == "abandoned" else self.disposition
   240	        )
   241	
   242	    @property
   243	    def is_historical_import(self) -> bool:
   244	        return self.observation_kind == "historical-import"
   245	
   246	
   247	@dataclass(frozen=True)
   248	class CalibrationLedgerSnapshot:
   249	    """One immutable, fully checked view threaded through an evaluation."""
   250	
   251	    ledger_schema: str
   252	    ledger_path: Path
   253	    head_sequence: int
   254	    head_digest: str
   255	    receipts: tuple[Mapping[str, Any], ...]
   256	    observations: tuple[LedgerObservation, ...]
   257	    refusal_reasons: tuple[str, ...]
   258	    bracket_sessions: tuple["CalibrationBracketSession", ...] = ()
   259	    baseline_sequence: int | None = None
   260	    baseline_digest: str | None = None
   261	    committed_head_sequence: int | None = None
   262	    committed_head_digest: str | None = None
   263	
   264	    @property
   265	    def valid(self) -> bool:
   266	        return not self.refusal_reasons
   267	
   268	    @property
   269	    def observation_by_attempt(self) -> Mapping[str, LedgerObservation]:
   270	        return MappingProxyType(
   271	            {observation.attempt_id: observation for observation in self.observations}
   272	        )
   273	
   274	    @property
   275	    def bracket_session_by_id(self) -> Mapping[str, "CalibrationBracketSession"]:
   276	        return MappingProxyType(
   277	            {session.session_id: session for session in self.bracket_sessions}
   278	        )
   279	
   280	    @property
   281	    def is_governed_open_bracket_extension(self) -> bool:
   282	        """Whether the physical/pin gap is exactly one reserved open session."""
   283	
   284	        allowed = {
   285	            "calibration_ledger_bracket_session_open",
   286	            "calibration_ledger_head_mismatch",
   287	        }
   288	        if (
   289	            set(self.refusal_reasons) != allowed
   290	            or self.committed_head_sequence is None
  1400	    event: str,
  1401	    session_identity: Mapping[str, Any],
  1402	    fields: Mapping[str, Any],
  1403	) -> dict[str, Any]:
  1404	    receipt = {
  1405	        "schema_version": BRACKET_SESSION_SCHEMA,
  1406	        "ledger_schema": LEDGER_SCHEMA,
  1407	        "sequence": sequence,
  1408	        "predecessor_digest": predecessor_digest,
  1409	        "event": event,
  1410	        **{field: session_identity.get(field) for field in _SESSION_IDENTITY_KEYS},
  1411	        **dict(fields),
  1412	    }
  1413	    receipt["receipt_digest"] = _receipt_digest(receipt)
  1414	    return receipt
  1415	
  1416	
  1417	def _json_object_from_bytes(raw: bytes, source: Path) -> Mapping[str, Any]:
  1418	    try:
  1419	        value = json.loads(raw)
  1420	    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
  1421	        raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
  1422	    if not isinstance(value, Mapping):
  1423	        raise CalibrationLedgerError(f"{source}: expected a JSON object")
  1424	    return value
  1425	
  1426	
  1427	def _authenticated_json_object(
  1428	    raw: bytes,
  1429	    expected_sha256: str,
  1430	    *,
  1431	    label: str,
  1432	) -> Mapping[str, Any]:
  1433	    if not _is_sha256(expected_sha256):
  1434	        raise CalibrationLedgerError(f"expected {label} sha256 is malformed")
  1435	    observed = hashlib.sha256(raw).hexdigest()
  1436	    if observed != expected_sha256:
  1437	        raise CalibrationLedgerError(f"{label} sha256 mismatch")
  1438	    return _json_object_from_bytes(raw, Path(label))
  1439	
  1440	
  1441	def _number_lexemes(raw: bytes, source: Path) -> Mapping[str, Any]:
  1442	    try:
  1443	        value = json.loads(raw, parse_float=str, parse_int=str)
  1444	    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
  1445	        raise CalibrationLedgerError(f"{source}: malformed JSON") from exc
  1446	    if not isinstance(value, Mapping):
  1447	        raise CalibrationLedgerError(f"{source}: expected a JSON object")
  1448	    return value
  1449	
  1450	
  1451	def _historical_import_table(
  1452	    value: Mapping[str, Any],
  1453	) -> tuple[dict[str, Any], dict[str, Mapping[str, Any]]]:
  1454	    if set(value) != {
  1455	        "schema_version",
  1456	        "ledger_schema",
  1457	        "identity_epoch",
  1458	        "members",
  1459	    }:
  1460	        raise CalibrationLedgerError("historical import table has invalid keys")
  1461	    if (
  1462	        value.get("schema_version") != HISTORICAL_IMPORT_TABLE_SCHEMA
  1463	        or value.get("ledger_schema") != LEDGER_SCHEMA
  1464	    ):
  1465	        raise CalibrationLedgerError("historical import table schema mismatch")
  1466	    epoch = value.get("identity_epoch")
  1467	    members = value.get("members")
  1468	    if (
  1469	        not isinstance(epoch, Mapping)
  1470	        or set(epoch) != set(IDENTITY_EPOCH_FIELDS)
  1471	        or any(epoch.get(field) in (None, "") for field in IDENTITY_EPOCH_FIELDS)
  1472	        or not isinstance(members, list)
  1473	        or not members
  1474	    ):
  1475	        raise CalibrationLedgerError("historical import table is incomplete")
  1476	
  1477	    by_content: dict[str, Mapping[str, Any]] = {}
  1478	    attempt_ids: set[str] = set()
  1479	    for member in members:
  1480	        if not isinstance(member, Mapping) or set(member) != {
  1481	            "attempt_id",
  1482	            "content_id",
  1483	            "artifact_sha256",
  1484	            "disposition",
  1485	        }:
  1486	            raise CalibrationLedgerError("historical import member has invalid keys")
  1487	        attempt_id = member.get("attempt_id")
  1488	        content_id = member.get("content_id")
  1489	        artifacts = member.get("artifact_sha256")
  1490	        disposition = member.get("disposition")
  1491	        if (
  1492	            not isinstance(attempt_id, str)
  1493	            or not attempt_id
  1494	            or not _is_sha256(content_id)
  1495	            or not isinstance(artifacts, Mapping)
  1496	            or set(artifacts) != set(GOVERNED_ARTIFACTS)
  1497	            or any(not _is_sha256(item) for item in artifacts.values())
  1498	            or content_id_from_artifact_hashes(artifacts) != content_id
  1499	            or disposition not in HISTORICAL_IMPORT_DISPOSITIONS
  1500	        ):
  1501	            raise CalibrationLedgerError("historical import member is malformed")
  1502	        if attempt_id in attempt_ids:
  1503	            raise CalibrationLedgerError(
  1504	                "historical import attempt_id collision; content_id tiebreak is "
  1505	                "diagnostic only"
  1506	            )
  1507	        if str(content_id) in by_content:
  1508	            raise CalibrationLedgerError("historical import content_id is duplicated")
  1509	        attempt_ids.add(attempt_id)
  1510	        by_content[str(content_id)] = member
origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py:335:    def test_pre_probe_accepts_only_governed_open_u1_extension_shape(self) -> None:
origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py:336:        result = _probe(_open_pre_snapshot())
origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py:371:            ["content_distinct_valid_same_epoch_count_boundary"],
origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py:586:    def test_count_boundary_advances_only_after_crossing(self) -> None:

2026-08-07T21:19:53.826267Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "git show origin/impl/d117-u2-successor:joulewise/calibration_ledger.py | nl -ba | sed -n '281,335p'
git show origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py | nl -ba | sed -n '320,410p'
git show origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py | nl -ba | sed -n '445,485p'
git show origin/impl/d117-u2-successor:tests/test_calibration_acceptance_successor.py | nl -ba | sed -n '500,610p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   281	    def is_governed_open_bracket_extension(self) -> bool:
   282	        """Whether the physical/pin gap is exactly one reserved open session."""
   283	
   284	        allowed = {
   285	            "calibration_ledger_bracket_session_open",
   286	            "calibration_ledger_head_mismatch",
   287	        }
   288	        if (
   289	            set(self.refusal_reasons) != allowed
   290	            or self.committed_head_sequence is None
   291	            or self.committed_head_digest is None
   292	        ):
   293	            return False
   294	        open_sessions = [
   295	            session for session in self.bracket_sessions if session.state == "open"
   296	        ]
   297	        if len(open_sessions) != 1:
   298	            return False
   299	        session = open_sessions[0]
   300	        if session.capability_sequence != self.committed_head_sequence + 1:
   301	            return False
   302	        tail = self.receipts[self.committed_head_sequence :]
   303	        return bool(
   304	            tail
   305	            and tail[0].get("event") == BRACKET_SESSION_OPEN_EVENT
   306	            and tail[0].get("predecessor_digest") == self.committed_head_digest
   307	            and all(row.get("session_id") == session.session_id for row in tail)
   308	        )
   309	
   310	    @property
   311	    def observations_by_content(self) -> Mapping[str, tuple[LedgerObservation, ...]]:
   312	        grouped: dict[str, list[LedgerObservation]] = {}
   313	        for observation in self.observations:
   314	            if observation.content_id is not None:
   315	                grouped.setdefault(observation.content_id, []).append(observation)
   316	        return MappingProxyType(
   317	            {key: tuple(value) for key, value in sorted(grouped.items())}
   318	        )
   319	
   320	    def post_cutoff_live_observations(
   321	        self, cutoff_sequence: int
   322	    ) -> tuple[LedgerObservation, ...]:
   323	        """Return only fresh live-capture observations after ``cutoff_sequence``.
   324	
   325	        Historical bootstrap finalizations are deliberately excluded even
   326	        when a caller compares them with the genesis sequence-zero cutoff.
   327	        """
   328	
   329	        if (
   330	            isinstance(cutoff_sequence, bool)
   331	            or not isinstance(cutoff_sequence, int)
   332	            or cutoff_sequence < 0
   333	        ):
   334	            raise CalibrationLedgerError("cutoff_sequence must be nonnegative")
   335	        return tuple(
   320	            config = root / "configs/calibration"
   321	            config.mkdir(parents=True)
   322	            target = root / "target.json"
   323	            target.write_bytes(ACCEPTANCE_PATH.read_bytes())
   324	            (config / "calibration_acceptance_d079_v2.json").symlink_to(target)
   325	            registry_path = config / "calibration_acceptance_registry.json"
   326	            registry_path.write_bytes(REGISTRY_PATH.read_bytes())
   327	            self.assertIsNone(
   328	                bracketing.load_calibration_acceptance_registry(
   329	                    registry_path, repo_root=root, require_committed=False
   330	                )
   331	            )
   332	
   333	
   334	class TriggerProbeTests(unittest.TestCase):
   335	    def test_pre_probe_accepts_only_governed_open_u1_extension_shape(self) -> None:
   336	        result = _probe(_open_pre_snapshot())
   337	        self.assertEqual(result["outcome"], "successor_required")
   338	        malformed = replace(
   339	            _open_pre_snapshot(),
   340	            refusal_reasons=("calibration_ledger_head_mismatch",),
   341	        )
   342	        self.assertEqual(
   343	            _probe(malformed)["outcome"], "authentication_or_epoch_refusal"
   344	        )
   345	
   346	    def test_range_expansion_below_and_above_require_successor(self) -> None:
   347	        for index, bound in enumerate(
   348	            ("0.0200000000000000001", "0.033558756679899995")
   349	        ):
   350	            with self.subTest(bound=bound):
   351	                result = _probe(_snapshot((_new_observation(index, bound=bound),)))
   352	                self.assertEqual(result["outcome"], "successor_required")
   353	                self.assertEqual(
   354	                    result["observed_triggers"],
   355	                    ["new_valid_same_identity_capture_expands_observed_range"],
   356	                )
   357	
   358	    def test_in_range_observation_does_not_trigger_before_boundary(self) -> None:
   359	        result = _probe(_snapshot((_new_observation(0, bound="0.0271"),)))
   360	        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
   361	        self.assertEqual(result["observed_triggers"], [])
   362	
   363	    def test_counts_37_and_38_are_distinct(self) -> None:
   364	        seven = tuple(_new_observation(index, bound="0.0271") for index in range(7))
   365	        eight = tuple(_new_observation(index, bound="0.0271") for index in range(8))
   366	        self.assertEqual(_probe(_snapshot(seven))["outcome"], "accepted_under_active_artifact")
   367	        result = _probe(_snapshot(eight))
   368	        self.assertEqual(result["outcome"], "successor_required")
   369	        self.assertEqual(
   370	            result["observed_triggers"],
   371	            ["content_distinct_valid_same_epoch_count_boundary"],
   372	        )
   373	
   374	    def test_systematic_classification_and_above_screen_both_refuse(self) -> None:
   375	        cases = (
   376	            _new_observation(0, disposition="systematic-invalid", bound="0.02"),
   377	            _new_observation(0, disposition="valid", bound="0.04"),
   378	        )
   379	        for observation in cases:
   380	            with self.subTest(disposition=observation.disposition, bound=observation.exact_bound_lexeme_s):
   381	                result = _probe(_snapshot((observation,)))
   382	                self.assertEqual(result["outcome"], "systematic_refusal")
   383	                self.assertEqual(
   384	                    result["refusal_reasons"],
   385	                    [bracketing.SUCCESSOR_SYSTEMATIC_POLICY],
   386	                )
   387	
   388	    def test_ordinary_invalid_is_recorded_but_does_not_trigger(self) -> None:
   389	        result = _probe(
   390	            _snapshot((_new_observation(0, disposition="ordinary-invalid", bound="0.04"),))
   391	        )
   392	        self.assertEqual(result["outcome"], "accepted_under_active_artifact")
   393	        self.assertEqual(len(result["new_content_ids"]), 1)
   394	
   395	    def test_unresolved_or_null_content_refuses(self) -> None:
   396	        observation = replace(
   397	            _new_observation(0, disposition="abandoned"),
   398	            content_id=None,
   399	            artifact_sha256={},
   400	            exact_bound_lexeme_s=None,
   401	        )
   402	        result = _probe(_snapshot((observation,)))
   403	        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
   404	        self.assertIn("unresolved_or_unclassifiable_observation", result["refusal_reasons"])
   405	
   406	    def test_same_content_alias_does_not_increment_count(self) -> None:
   407	        original = _parent_observations()[0]
   408	        alias = replace(
   409	            original,
   410	            sequence=77,
   445	            _snapshot(),
   446	            observed_identity_epoch=epoch,
   447	            require_committed_registry=False,
   448	            verify_custody=False,
   449	        )
   450	        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
   451	        with patch.object(bracketing, "_current_estimator_code_sha256", return_value={"x": "0" * 64}):
   452	            result = _probe(_snapshot())
   453	        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
   454	        self.assertEqual(result["observed_triggers"], ["protocol_or_estimator_byte_change"])
   455	
   456	    def test_probe_does_not_consult_writer_copied_scalar(self) -> None:
   457	        import scripts.validate_powermetrics_fiducial as writer
   458	
   459	        snapshot = _snapshot((_new_observation(0, bound="0.034"),))
   460	        expected = _probe(snapshot)
   461	        with patch.object(writer, "PREFLIGHT_SYSTEMATIC_SCREEN_S", Decimal("999")):
   462	            actual = _probe(snapshot)
   463	        self.assertEqual(actual, expected)
   464	
   465	    def test_prefix_omission_and_physical_pin_mismatch_refuse(self) -> None:
   466	        omitted = replace(_snapshot(), observations=tuple(_parent_observations()[1:]))
   467	        self.assertEqual(_probe(omitted)["outcome"], "authentication_or_epoch_refusal")
   468	        mismatched = replace(
   469	            _snapshot(),
   470	            refusal_reasons=("calibration_ledger_head_mismatch",),
   471	        )
   472	        self.assertEqual(_probe(mismatched)["outcome"], "authentication_or_epoch_refusal")
   473	
   474	    def test_missing_custody_refuses_when_reauthentication_enabled(self) -> None:
   475	        result = bracketing.probe_calibration_acceptance_trigger(
   476	            _snapshot((_new_observation(0),)),
   477	            observed_identity_epoch=_parent_artifact()["identity_epoch"],
   478	            require_committed_registry=False,
   479	            verify_custody=True,
   480	        )
   481	        self.assertEqual(result["outcome"], "authentication_or_epoch_refusal")
   482	        self.assertIn("new_observation_custody_or_physics_invalid", result["refusal_reasons"])
   483	
   484	
   485	class DecimalDerivationTests(unittest.TestCase):
   500	            key=lambda member: member["content_id"],
   501	        )
   502	        derived = bracketing.derive_successor_decimal_derivation(members)
   503	        stats = derived["source_statistics"]
   504	        operatives = derived["ratified_operatives"]
   505	        self.assertEqual(stats["prediction_95_two_draw_s"], "0.008826584887500717")
   506	        self.assertEqual(stats["prediction_99_two_draw_s"], "0.012093166090593858")
   507	        self.assertEqual(operatives["bracket_screen_s"], "0.010818")
   508	        self.assertEqual(operatives["preflight_level_screen_s"], "0.033558756679900")
   509	        self.assertEqual(operatives["max_budgetable_excess_s"], "0.001275166090593858")
   510	
   511	    def test_half_even_long_lexeme_and_preflight_max_rule(self) -> None:
   512	        members = [
   513	            {"content_id": "1" * 64, "b_fiducial_s": "0.0000000000000000000000000000000"},
   514	            {"content_id": "2" * 64, "b_fiducial_s": "0.0000005000000000000000000000000"},
   515	        ]
   516	        derived = bracketing.derive_successor_decimal_derivation(members)
   517	        self.assertEqual(derived["ratified_operatives"]["bracket_screen_s"], "0.000000")
   518	        self.assertEqual(
   519	            derived["rounding"]["preflight_level_screen"]["source_rule"],
   520	            bracketing.SUCCESSOR_PREFLIGHT_SCREEN_RULE,
   521	        )
   522	        self.assertGreater(
   523	            Decimal(derived["ratified_operatives"]["preflight_level_screen_s"]),
   524	            Decimal(derived["source_statistics"]["maximum_s"]),
   525	        )
   526	
   527	    def test_negative_nonfinite_and_binary_float_inputs_refuse(self) -> None:
   528	        for invalid in ("-0.1", "NaN", "Infinity", 0.1):
   529	            with self.subTest(invalid=invalid):
   530	                with self.assertRaises(ValueError):
   531	                    bracketing.derive_successor_decimal_derivation(
   532	                        [
   533	                            {"content_id": "1" * 64, "b_fiducial_s": invalid},
   534	                            {"content_id": "2" * 64, "b_fiducial_s": "0.2"},
   535	                        ]
   536	                    )
   537	
   538	    def test_quantile_algorithm_and_d102_pin_are_stable(self) -> None:
   539	        self.assertEqual(
   540	            bracketing.SUCCESSOR_QUANTILE_METHOD,
   541	            "decimal_incomplete_beta_bisection_v1",
   542	        )
   543	        self.assertEqual(
   544	            bracketing.decimal_student_t_quantile("0.995", 18),
   545	            Decimal(
   546	                "2.8784404727135853941939366597008136821841052811738896572381901955286218320347263"
   547	            ),
   548	        )
   549	
   550	
   551	class SuccessorBuilderTests(unittest.TestCase):
   552	    def test_first_range_successor_contains_all_30_plus_trigger(self) -> None:
   553	        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
   554	        build = successor.build_calibration_acceptance_successor(
   555	            snapshot,
   556	            observed_identity_epoch=_parent_artifact()["identity_epoch"],
   557	            require_committed_registry=False,
   558	            verify_custody=False,
   559	        )
   560	        self.assertEqual(build.artifact["derivation_corpus"]["n"], 31)
   561	        self.assertEqual(build.artifact["prospective_rederivation"]["count_trigger"]["next_boundary"], 38)
   562	        self.assertTrue(bracketing._valid_acceptance_bound(build.artifact))
   563	        self.assertEqual(build.successor_probe["outcome"], "accepted_under_active_artifact")
   564	        self.assertEqual(build.artifact["lineage"]["parent_acceptance_id"], "d079_calibration_acceptance_v2_n19")
   565	        self.assertIn(_digest("live-content-0"), build.artifact["lineage"]["trigger_judgment"]["new_content_ids"])
   566	
   567	    def test_repeated_and_shuffled_builds_are_byte_identical(self) -> None:
   568	        snapshot = _snapshot((_new_observation(0, bound="0.02"),))
   569	        first = successor.build_calibration_acceptance_successor(
   570	            snapshot,
   571	            observed_identity_epoch=_parent_artifact()["identity_epoch"],
   572	            require_committed_registry=False,
   573	            verify_custody=False,
   574	        )
   575	        shuffled = replace(snapshot, observations=tuple(reversed(snapshot.observations)))
   576	        second = successor.build_calibration_acceptance_successor(
   577	            shuffled,
   578	            observed_identity_epoch=_parent_artifact()["identity_epoch"],
   579	            require_committed_registry=False,
   580	            verify_custody=False,
   581	        )
   582	        self.assertEqual(first.artifact_bytes, second.artifact_bytes)
   583	        self.assertEqual(first.registry_bytes, second.registry_bytes)
   584	        self.assertEqual(first.head_pin, second.head_pin)
   585	
   586	    def test_count_boundary_advances_only_after_crossing(self) -> None:
   587	        extras = tuple(_new_observation(index, bound="0.0271") for index in range(8))
   588	        build = successor.build_calibration_acceptance_successor(
   589	            _snapshot(extras),
   590	            observed_identity_epoch=_parent_artifact()["identity_epoch"],
   591	            require_committed_registry=False,
   592	            verify_custody=False,
   593	        )
   594	        self.assertEqual(build.artifact["derivation_corpus"]["n"], 38)
   595	        self.assertEqual(build.artifact["prospective_rederivation"]["count_trigger"]["next_boundary"], 76)
   596	
   597	    def test_systematic_and_unresolved_never_build(self) -> None:
   598	        cases = (
   599	            _snapshot((_new_observation(0, disposition="systematic-invalid"),)),
   600	            _snapshot((replace(_new_observation(0, disposition="abandoned"), content_id=None, artifact_sha256={}, exact_bound_lexeme_s=None),)),
   601	        )
   602	        for snapshot in cases:
   603	            with self.subTest(head=snapshot.head_digest):
   604	                with self.assertRaisesRegex(ValueError, "does not require a successor"):
   605	                    successor.build_calibration_acceptance_successor(
   606	                        snapshot,
   607	                        observed_identity_epoch=_parent_artifact()["identity_epoch"],
   608	                        require_committed_registry=False,
   609	                        verify_custody=False,
   610	                    )

2026-08-07T21:19:57.786701Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `base_instructions` at line 94 column 5
exec
/bin/zsh -lc "git reflog show --date=iso origin/impl/d117-u2-successor -1 || true
git show -s --format='commit=%H%nauthor_date=%aI%ncommit_date=%cI%nsubject=%s' origin/impl/d117-u2-successor
git diff --check main...origin/impl/d117-u2-successor
git status --short --branch" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
399ffeb refs/remotes/origin/impl/d117-u2-successor@{2026-08-07 13:15:09 -0700}: update by push
commit=399ffebdf96d883857fa9effdb579e0e09b0857d
author_date=2026-08-07T13:15:07-07:00
commit_date=2026-08-07T13:15:07-07:00
subject=U2 speculative implementation (COLD-GATE EXHIBIT — not a landing candidate): D-102 successor engine with registry authentication, deterministic Decimal derivation, trigger probing, guarded publication. All 12 contested design choices implemented at the design brief's recommended answer and tagged COLD-GATE-Q1..Q12 so the gate can flip any ruling with a minimal diff.
## main...origin/main
 M CLAIMS_STATUS.md
 M PROJECT_STATUS.md
 M README.md
 M WINDOW_STATUS.md
 M docs/decision_log.md

exec
/bin/zsh -lc "git grep -n -E 'parent_judgment_policy|trigger_judgment|judged_under_acceptance_id|POST_SUCCESSOR_POLICY' origin/impl/d117-u2-successor -- ':"'!docs/**'"'
git grep -n -E 'claim_evaluation_blocked|registry_commit|publication_policy' origin/impl/d117-u2-successor -- ':"'!docs/**'"'
git show origin/impl/d117-u2-successor:scripts/build_calibration_acceptance_successor.py | nl -ba | sed -n '580,675p'
git show origin/impl/d117-u2-successor:configs/calibration/calibration_acceptance_registry.json | nl -ba" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 16ms:
   580	
   581	def _parser() -> argparse.ArgumentParser:
   582	    parser = argparse.ArgumentParser(description=__doc__)
   583	    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER_PATH)
   584	    parser.add_argument("--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH)
   585	    parser.add_argument(
   586	        "--registry", type=Path, default=DEFAULT_ACCEPTANCE_REGISTRY_PATH
   587	    )
   588	    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
   589	    parser.add_argument("--observed-identity", type=Path, required=True)
   590	    parser.add_argument("--issue", action="store_true")
   591	    parser.add_argument("--artifact-out", type=Path)
   592	    parser.add_argument("--registry-out", type=Path)
   593	    return parser
   594	
   595	
   596	def main(argv: Sequence[str] | None = None) -> int:
   597	    args = _parser().parse_args(argv)
   598	    try:
   599	        registry_raw = args.registry.read_bytes()
   600	        registry = load_calibration_acceptance_registry(
   601	            args.registry,
   602	            repo_root=args.repo_root,
   603	            require_committed=True,
   604	        )
   605	        if registry is None:
   606	            raise ValueError("registry is not committed or authenticated")
   607	        _, parent = _load_parent_artifact(registry, Path(args.repo_root).resolve())
   608	        cutoff = parent["ledger_cutoff"]
   609	        snapshot = load_calibration_ledger_snapshot(
   610	            args.ledger,
   611	            args.head_pin,
   612	            baseline_sequence=cutoff["sequence"],
   613	            baseline_digest=cutoff["head_digest"],
   614	            require_committed_pin=True,
   615	            verify_custody=True,
   616	            repo_root=args.repo_root,
   617	        )
   618	        observed_identity = json.loads(args.observed_identity.read_bytes())
   619	        if not isinstance(observed_identity, Mapping):
   620	            raise ValueError("observed identity must be a JSON object")
   621	        build = build_calibration_acceptance_successor(
   622	            snapshot,
   623	            observed_identity_epoch=observed_identity,
   624	            registry_path=args.registry,
   625	            repo_root=args.repo_root,
   626	            require_committed_registry=True,
   627	            verify_custody=True,
   628	        )
   629	        if args.issue:
   630	            if args.artifact_out is None or args.registry_out is None:
   631	                raise ValueError("--issue requires --artifact-out and --registry-out")
   632	            publish_successor(
   633	                build,
   634	                artifact_destination=args.artifact_out,
   635	                registry_destination=args.registry_out,
   636	                expected_registry_bytes=registry_raw,
   637	                repo_root=args.repo_root,
   638	            )
   639	        elif args.artifact_out is not None or args.registry_out is not None:
   640	            raise ValueError("dry-run forbids output destinations")
   641	        sys.stdout.buffer.write(_pretty_json_bytes(build.output_record()))
   642	        return 0
   643	    except SuccessorDurabilityUncertain as exc:
   644	        print(f"committed_durability_uncertain: {exc}", file=sys.stderr)
   645	        return 3
   646	    except (OSError, TypeError, ValueError) as exc:
   647	        print(f"refusing: {exc}", file=sys.stderr)
   648	        return 2
   649	
   650	
   651	if __name__ == "__main__":
   652	    raise SystemExit(main())
     1	{
     2	  "schema_version": "joulewise.calibration_acceptance_registry.v1",
     3	  "authority": "committed_registry_one_active_exact_sha256",
     4	  "entries": [
     5	    {
     6	      "acceptance_id": "d079_calibration_acceptance_v2_n19",
     7	      "artifact_path": "configs/calibration/calibration_acceptance_d079_v2.json",
     8	      "artifact_sha256": "316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985",
     9	      "derivation_sha256": "4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02",
    10	      "artifact_schema": "joulewise.calibration_acceptance_bound.v2",
    11	      "generation": 1,
    12	      "active": true,
    13	      "parent_acceptance_id": null,
    14	      "parent_artifact_sha256": null,
    15	      "ledger_cutoff": {
    16	        "sequence": 76,
    17	        "head_digest": "08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7",
    18	        "ledger_schema": "joulewise.calibration_observation_ledger.v1"
    19	      }
    20	    }
    21	  ]
    22	}

exec
/bin/zsh -lc "git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '2280,2405p'
git grep -n -E 'acceptance_id|calibration_acceptance' origin/impl/d117-u2-successor -- joulewise/calibration_bracketing.py | tail -120" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
  2280	        protocol_id=str(protocol_id),
  2281	        capture_wall_time_s=float(capture),
  2282	        b_fiducial_s=effective_bound_lexeme,
  2283	        bindings=dict(bindings),
  2284	    )
  2285	
  2286	
  2287	def _candidate_from_observation(
  2288	    observation: LedgerObservation,
  2289	) -> CalibrationCandidate | None:
  2290	    """Authenticate one valid ledger observation from its custody locator."""
  2291	
  2292	    if observation.disposition != "valid" or observation.content_id is None:
  2293	        return None
  2294	    custody = Path(observation.custody_locator)
  2295	    candidate = load_calibration_candidate(
  2296	        custody,
  2297	        runs_root=custody.parent.parent,
  2298	    )
  2299	    if candidate is None:
  2300	        return None
  2301	    bound = _candidate_decimal(candidate)
  2302	    receipt_bound = _decimal(observation.exact_bound_lexeme_s)
  2303	    try:
  2304	        receipt_capture = float(observation.capture_wall_time_s)
  2305	    except (TypeError, ValueError):
  2306	        return None
  2307	    if (
  2308	        candidate.manifest_sha256
  2309	        != observation.artifact_sha256.get("manifest.json")
  2310	        or candidate.evidence_sha256
  2311	        != observation.artifact_sha256.get("instrument_evidence.json")
  2312	        or content_id_from_artifact_hashes(observation.artifact_sha256)
  2313	        != observation.content_id
  2314	        or bound is None
  2315	        or receipt_bound is None
  2316	        or bound != receipt_bound
  2317	        or candidate.capture_wall_time_s != receipt_capture
  2318	        or any(
  2319	            candidate.bindings.get(field) != observation.t1_bindings.get(field)
  2320	            for field in V2_BINDING_FIELDS
  2321	        )
  2322	        or any(
  2323	            candidate.bindings.get(field) != observation.identity_epoch.get(field)
  2324	            for field in ACCEPTANCE_IDENTITY_FIELDS
  2325	        )
  2326	    ):
  2327	        return None
  2328	    return replace(
  2329	        candidate,
  2330	        relative_path=observation.custody_locator,
  2331	        attempt_id=observation.attempt_id,
  2332	        content_id=observation.content_id,
  2333	        ledger_receipt_digest=observation.receipt_digest,
  2334	        bracket_session_id=observation.bracket_session_id,
  2335	        bracket_slot=observation.bracket_slot,
  2336	        bracket_window_id=observation.bracket_window_id,
  2337	        bracket_plan_id=observation.bracket_plan_id,
  2338	        bracket_plan_sha256=observation.bracket_plan_sha256,
  2339	        bracket_evidence_root_id=observation.bracket_evidence_root_id,
  2340	        bracket_runs_root=observation.bracket_runs_root,
  2341	    )
  2342	
  2343	
  2344	def discover_calibration_candidates(
  2345	    ledger_snapshot: CalibrationLedgerSnapshot,
  2346	) -> tuple[CalibrationCandidate, ...]:
  2347	    """Enumerate valid endpoints from the sole ledger authority.
  2348	
  2349	    The mechanism closes workflow omission, unregistered evidence, and
  2350	    rollback/stale-head consumption; it does not defend against a malicious
  2351	    trusted writer or a rewrite of both Git and full ledger history.
  2352	    """
  2353	
  2354	    if (
  2355	        not isinstance(ledger_snapshot, CalibrationLedgerSnapshot)
  2356	        or not ledger_snapshot.valid
  2357	        and not ledger_snapshot.is_governed_open_bracket_extension
  2358	    ):
  2359	        return ()
  2360	    finalized_session_ids = {
  2361	        session.session_id
  2362	        for session in ledger_snapshot.bracket_sessions
  2363	        if session.state == "finalized"
  2364	    }
  2365	    candidates: list[CalibrationCandidate] = []
  2366	    for observation in ledger_snapshot.observations:
  2367	        if (
  2368	            observation.disposition != "valid"
  2369	            or observation.is_historical_import
  2370	            or observation.bracket_session_id is not None
  2371	            and observation.bracket_session_id not in finalized_session_ids
  2372	        ):
  2373	            continue
  2374	        candidate = _candidate_from_observation(observation)
  2375	        if candidate is None:
  2376	            return ()
  2377	        candidates.append(candidate)
  2378	    return tuple(candidates)
  2379	
  2380	
  2381	def _governed_unused_slot_rows(
  2382	    ledger_snapshot: CalibrationLedgerSnapshot,
  2383	    cutoff_sequence: int,
  2384	) -> list[dict[str, Any]] | None:
  2385	    receipts_by_session: dict[str, list[Mapping[str, Any]]] = {}
  2386	    for receipt in ledger_snapshot.receipts[:cutoff_sequence]:
  2387	        session_id = receipt.get("session_id")
  2388	        if isinstance(session_id, str):
  2389	            receipts_by_session.setdefault(session_id, []).append(receipt)
  2390	    rows: list[dict[str, Any]] = []
  2391	    for session in ledger_snapshot.bracket_sessions:
  2392	        if session.state != "aborted" or session.capability_sequence > cutoff_sequence:
  2393	            continue
  2394	        receipts = receipts_by_session.get(session.session_id, [])
  2395	        opened = [row for row in receipts if row.get("event") == "bracket-session-open"]
  2396	        aborted = [row for row in receipts if row.get("event") == "bracket-session-abort"]
  2397	        if len(opened) != 1 or len(aborted) != 1:
  2398	            return None
  2399	        for slot in aborted[0]["unused_slots"]:
  2400	            reservation = opened[0]["slots"][slot]
  2401	            rows.append(
  2402	                {
  2403	                    "attempt_id": reservation["attempt_id"],
  2404	                    "closure_sequence": aborted[0]["sequence"],
  2405	                    "receipt_digest": aborted[0]["receipt_digest"],
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:46:ACCEPTANCE_BOUND_SCHEMA = "joulewise.calibration_acceptance_bound.v2"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:47:ACCEPTANCE_SUCCESSOR_SCHEMA = "joulewise.calibration_acceptance_bound.v3"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:49:    "joulewise.calibration_acceptance_bound.v2.fixture.v1"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:51:ACCEPTANCE_EVALUATION_SCHEMA = "joulewise.calibration_acceptance_evaluation.v2"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:52:ACCEPTANCE_REGISTRY_SCHEMA = "joulewise.calibration_acceptance_registry.v1"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:54:    "joulewise.calibration_acceptance_trigger_probe.v1"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:60:    / "calibration_acceptance_d079_v2.json"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:66:    / "calibration_acceptance_registry.json"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:135:    "acceptance_id",
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:149:    r"^calibration_acceptance_v3_s([1-9][0-9]*)_([0-9a-f]{16})\.json$"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:171:                    and entry.get("acceptance_id")
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:172:                    == "d079_calibration_acceptance_v2_n19"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:603:        "acceptance_id",
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:610:        "parent_acceptance_id",
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:623:            or not isinstance(entry.get("acceptance_id"), str)
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:624:            or not entry["acceptance_id"]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:644:        acceptance_id = entry["acceptance_id"]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:646:        if acceptance_id in ids or artifact_path in paths:
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:648:        ids.add(acceptance_id)
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:650:        entries_by_id[acceptance_id] = entry
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:656:    child_counts = {entry["acceptance_id"]: 0 for entry in value["entries"]}
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:658:        parent_id = entry["parent_acceptance_id"]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:678:        seen = {entry["acceptance_id"]}
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:681:            cursor_id = cursor["acceptance_id"]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:685:            next_parent = cursor["parent_acceptance_id"]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:688:    active_ids = [entry["acceptance_id"] for entry in value["entries"] if entry["active"]]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:712:def load_calibration_acceptance_registry(
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:736:    entries_by_id = {entry["acceptance_id"]: entry for entry in value["entries"]}
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:752:            or artifact.get("acceptance_id") != entry["acceptance_id"]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:762:        artifacts_by_id[entry["acceptance_id"]] = artifact
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:778:        artifact = artifacts_by_id[entry["acceptance_id"]]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:780:        parent_entry = entries_by_id.get(entry["parent_acceptance_id"])
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:781:        parent = artifacts_by_id.get(entry["parent_acceptance_id"])
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:789:            or lineage["parent_acceptance_id"] != entry["parent_acceptance_id"]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:816:        or not isinstance(value.get("acceptance_id"), str)
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:817:        or not value["acceptance_id"].startswith("d079_calibration_acceptance_v3_s")
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:846:        or value["acceptance_id"]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:848:            f"d079_calibration_acceptance_v3_s{cutoff['sequence']}_"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:863:            "root_acceptance_id",
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:864:            "parent_acceptance_id",
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:875:            for field in ("root_acceptance_id", "parent_acceptance_id")
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:894:            "judged_under_acceptance_id",
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:900:        or judgment.get("judged_under_acceptance_id")
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:901:        != lineage["parent_acceptance_id"]
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1227:        or value.get("acceptance_id") != "d079_calibration_acceptance_v2_n19"
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1434:def load_calibration_acceptance_bound(
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1450:        registry = load_calibration_acceptance_registry(
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1513:    pinned = load_calibration_acceptance_bound()
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1522:    registry = load_calibration_acceptance_registry(
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1529:    if active is not None and active.get("acceptance_id") == artifact.get("acceptance_id"):
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1654:        "active_acceptance_id": (
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1655:            artifact.get("acceptance_id") if isinstance(artifact, Mapping) else None
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1690:def probe_calibration_acceptance_trigger(
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:1708:    registry = load_calibration_acceptance_registry(
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2564:        load_calibration_acceptance_bound()
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2577:        return result, ("calibration_acceptance_bound_stale",)
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2584:                "acceptance_id": artifact["acceptance_id"],
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2595:        return result, ("calibration_acceptance_bound_stale",)
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2600:            "acceptance_id": artifact["acceptance_id"],
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2639:            "acceptance_bound_id": artifact["acceptance_id"],
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2659:            "acceptance_id": artifact["acceptance_id"],
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2707:        return result, ("calibration_acceptance_bound_stale",)
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:2941:        return result, ("calibration_acceptance_bound_stale",)
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:3060:        return result, ("calibration_acceptance_bound_stale",)
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:3227:    "load_calibration_acceptance_bound",
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:3228:    "load_calibration_acceptance_registry",
origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py:3230:    "probe_calibration_acceptance_trigger",

codex
The mechanical comparison has exposed two material “implemented choice vs. brief” distinctions the gate needs to see neutrally: Q9 publishes only artifact+registry after the ledger head is already committed, and Q12 leaves the live writer’s copied scalar intact. I’m preserving both as explicit FOR/AGAINST evidence rather than normalizing them to the commit message’s claim that all recommendations were implemented.
exec
/bin/zsh -lc "git diff --unified=3 -- docs/decision_log.md | rg -n -C 5 'D-102|D-116|"'^@@'"' || true
git diff --name-only main...origin/impl/d117-u2-successor
git grep -n 'COLD-GATE-Q' origin/impl/d117-u2-successor -- | wc -l
git grep -n 'COLD-GATE-Q' origin/impl/d117-u2-successor -- | sed -E 's/.*COLD-GATE-Q([0-9]+).*/Q\\1/' | sort -V | uniq -c" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 9ms:
   1 Q1
   1 Q2
   1 Q3
   1 Q4
   1 Q5
   1 Q6
   1 Q7
   1 Q8
   1 Q9
   1 Q10
   1 Q11
   1 Q12

exec
/bin/zsh -lc 'git rev-parse main origin/main origin/impl/d117-u2-successor
git merge-base main origin/impl/d117-u2-successor
git diff --stat main...origin/impl/d117-u2-successor
git diff --name-status main...origin/impl/d117-u2-successor' in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
cdb7896cb4c7f68613e659879bd4a323ddd7e481
cdb7896cb4c7f68613e659879bd4a323ddd7e481
399ffebdf96d883857fa9effdb579e0e09b0857d
f665dd4d8bfb7eaca3256a0709b3310254e308fe
 .../calibration_acceptance_registry.json           |   22 +
 joulewise/calibration_bracketing.py                | 1537 +++++++++++++++++++-
 scripts/build_calibration_acceptance_successor.py  |  652 +++++++++
 tests/test_calibration_acceptance_successor.py     |  704 +++++++++
 4 files changed, 2902 insertions(+), 13 deletions(-)
A	configs/calibration/calibration_acceptance_registry.json
M	joulewise/calibration_bracketing.py
A	scripts/build_calibration_acceptance_successor.py
A	tests/test_calibration_acceptance_successor.py

exec
/bin/zsh -lc "git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '145,165p'
git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '840,925p'
git show origin/impl/d117-u2-successor:joulewise/calibration_bracketing.py | nl -ba | sed -n '1430,1540p'" in /private/tmp/claude-501/-Users-edr-code-JouleWise/58ce57f7-1ee6-4b35-a1b3-457ccf40dff7/scratchpad/desk
 succeeded in 0ms:
   145	    "decimal_derivation",
   146	    "derivation_sha256",
   147	}
   148	_SUCCESSOR_ARTIFACT_NAME_RE = re.compile(
   149	    r"^calibration_acceptance_v3_s([1-9][0-9]*)_([0-9a-f]{16})\.json$"
   150	)
   151	_D102_RATIFIED_T_QUANTILES = {
   152	    (18, "0.975"): Decimal(
   153	        "2.1009220402410352934446802481715190309096147708883899652987837826492167345329145"
   154	    ),
   155	    (18, "0.995"): Decimal(
   156	        "2.8784404727135853941939366597008136821841052811738896572381901955286218320347263"
   157	    ),
   158	}
   159	
   160	
   161	def _registry_bootstrap_issued_sha256() -> str:
   162	    """Compatibility export for the one legacy issuance-only consumer."""
   163	
   164	    try:
   165	        value = json.loads(DEFAULT_ACCEPTANCE_REGISTRY_PATH.read_bytes())
   840	        or not isinstance(cutoff, Mapping)
   841	        or set(cutoff) != {"sequence", "head_digest", "ledger_schema", "role"}
   842	        or isinstance(cutoff.get("sequence"), bool)
   843	        or not isinstance(cutoff.get("sequence"), int)
   844	        or cutoff["sequence"] < 1
   845	        or not _valid_sha256(cutoff.get("head_digest"))
   846	        or value["acceptance_id"]
   847	        != (
   848	            f"d079_calibration_acceptance_v3_s{cutoff['sequence']}_"
   849	            f"{cutoff['head_digest'][:16]}"
   850	        )
   851	        or cutoff.get("ledger_schema") != LEDGER_SCHEMA
   852	        or cutoff.get("role") != "issued_acceptance_baseline"
   853	        or not isinstance(identity, Mapping)
   854	        or set(identity) != set(ACCEPTANCE_IDENTITY_FIELDS)
   855	        or any(identity.get(field) in (None, "") for field in ACCEPTANCE_IDENTITY_FIELDS)
   856	    ):
   857	        return False
   858	    if (
   859	        not isinstance(lineage, Mapping)
   860	        or set(lineage)
   861	        != {
   862	            "generation",
   863	            "root_acceptance_id",
   864	            "parent_acceptance_id",
   865	            "parent_artifact_sha256",
   866	            "parent_derivation_sha256",
   867	            "parent_ledger_cutoff",
   868	            "trigger_judgment",
   869	        }
   870	        or isinstance(lineage.get("generation"), bool)
   871	        or not isinstance(lineage.get("generation"), int)
   872	        or lineage["generation"] < 2
   873	        or any(
   874	            not isinstance(lineage.get(field), str) or not lineage[field]
   875	            for field in ("root_acceptance_id", "parent_acceptance_id")
   876	        )
   877	        or not _valid_sha256(lineage.get("parent_artifact_sha256"))
   878	        or not _valid_sha256(lineage.get("parent_derivation_sha256"))
   879	        or not isinstance(lineage.get("parent_ledger_cutoff"), Mapping)
   880	        or set(lineage["parent_ledger_cutoff"])
   881	        != {"sequence", "head_digest", "ledger_schema"}
   882	        or isinstance(lineage["parent_ledger_cutoff"].get("sequence"), bool)
   883	        or not isinstance(lineage["parent_ledger_cutoff"].get("sequence"), int)
   884	        or lineage["parent_ledger_cutoff"]["sequence"] >= cutoff["sequence"]
   885	        or not _valid_sha256(lineage["parent_ledger_cutoff"].get("head_digest"))
   886	        or lineage["parent_ledger_cutoff"].get("ledger_schema") != LEDGER_SCHEMA
   887	        or not isinstance(lineage.get("trigger_judgment"), Mapping)
   888	    ):
   889	        return False
   890	    judgment = lineage["trigger_judgment"]
   891	    if (
   892	        set(judgment)
   893	        != {
   894	            "judged_under_acceptance_id",
   895	            "judged_under_artifact_sha256",
   896	            "result",
   897	            "new_content_ids",
   898	            "triggers",
   899	        }
   900	        or judgment.get("judged_under_acceptance_id")
   901	        != lineage["parent_acceptance_id"]
   902	        or judgment.get("judged_under_artifact_sha256")
   903	        != lineage["parent_artifact_sha256"]
   904	        or judgment.get("result") != "successor_required"
   905	        or not isinstance(judgment.get("new_content_ids"), list)
   906	        or judgment["new_content_ids"] != sorted(set(judgment["new_content_ids"]))
   907	        or not all(_valid_sha256(item) for item in judgment["new_content_ids"])
   908	        or not isinstance(judgment.get("triggers"), list)
   909	        or not judgment["triggers"]
   910	        or judgment["triggers"]
   911	        != [
   912	            trigger
   913	            for trigger in (
   914	                "new_valid_same_identity_capture_expands_observed_range",
   915	                "content_distinct_valid_same_epoch_count_boundary",
   916	            )
   917	            if trigger in judgment["triggers"]
   918	        ]
   919	    ):
   920	        return False
   921	    if (
   922	        not isinstance(prospective, Mapping)
   923	        or prospective.get("calendar_expiry") is not None
   924	        or prospective.get("trigger_observation_rule")
   925	        != "judge_under_prior_artifact_never_self_fit"
  1430	        and screen + excess == maximum
  1431	    )
  1432	
  1433	
  1434	def load_calibration_acceptance_bound(
  1435	    path: Path | None = None,
  1436	) -> dict[str, Any] | None:
  1437	    """Load the registry-selected D-102 acceptance artifact fail-closed.
  1438	
  1439	    An explicit path retains the exact-byte v2 bootstrap route;
  1440	    successors are accepted only through a registry entry.
  1441	    """
  1442	
  1443	    if path is None:
  1444	        # The exhibit must execute before its new registry can be committed.
  1445	        # Once this path exists at Git HEAD (the only landing shape), every
  1446	        # ordinary consumer automatically upgrades to strict commit equality.
  1447	        registry_head_bytes = _git_head_bytes(
  1448	            DEFAULT_ACCEPTANCE_REGISTRY_PATH.resolve(), _REPO_ROOT
  1449	        )
  1450	        registry = load_calibration_acceptance_registry(
  1451	            require_committed=registry_head_bytes is not None,
  1452	        )
  1453	        active = _active_registry_entry(registry) if registry is not None else None
  1454	        if active is None:
  1455	            return None
  1456	        requested = _REPO_ROOT / str(active["artifact_path"])
  1457	        try:
  1458	            raw = requested.read_bytes()
  1459	        except OSError:
  1460	            return None
  1461	        return _acceptance_bound_from_authenticated_bytes(
  1462	            raw,
  1463	            expected_sha256=str(active["artifact_sha256"]),
  1464	        )
  1465	
  1466	    requested = Path(path)
  1467	    try:
  1468	        raw = requested.read_bytes()
  1469	    except OSError:
  1470	        return None
  1471	    return _acceptance_bound_from_authenticated_bytes(raw)
  1472	
  1473	
  1474	def _acceptance_bound_from_authenticated_bytes(
  1475	    raw: bytes,
  1476	    *,
  1477	    expected_sha256: str | None = None,
  1478	) -> dict[str, Any] | None:
  1479	    """Parse acceptance bytes only when their role-indexed pin authenticates."""
  1480	
  1481	    try:
  1482	        value = json.loads(raw)
  1483	    except (UnicodeDecodeError, json.JSONDecodeError):
  1484	        return None
  1485	    # Any file route is authenticated by one of the two reviewed exact-byte
  1486	    # states: the genesis fixture retained for pre-issuance tests, or the
  1487	    # deterministically emitted issued artifact. A caller cannot turn an
  1488	    # alternate self-consistent document into authority by choosing a path.
  1489	    role = value.get("artifact_role") if isinstance(value, Mapping) else None
  1490	    schema = value.get("schema_version") if isinstance(value, Mapping) else None
  1491	    authenticated_sha256 = expected_sha256
  1492	    if authenticated_sha256 is None:
  1493	        authenticated_sha256 = {
  1494	            "schema_fixture_unissued": DEFAULT_ACCEPTANCE_BOUND_SHA256,
  1495	            "issued": (
  1496	                ISSUED_ACCEPTANCE_BOUND_SHA256
  1497	                if schema == ACCEPTANCE_BOUND_SCHEMA
  1498	                else None
  1499	            ),
  1500	        }.get(role)
  1501	    if hashlib.sha256(raw).hexdigest() != authenticated_sha256:
  1502	        return None
  1503	    if not _valid_acceptance_bound(value):
  1504	        return None
  1505	    return dict(value)
  1506	
  1507	
  1508	def _authenticated_explicit_acceptance_bound(
  1509	    value: Mapping[str, Any],
  1510	) -> dict[str, Any] | None:
  1511	    """Authenticate an in-memory artifact against the checked-in byte pin."""
  1512	
  1513	    pinned = load_calibration_acceptance_bound()
  1514	    if pinned is None or dict(value) != pinned:
  1515	        return None
  1516	    return pinned
  1517	
  1518	
  1519	def _acceptance_artifact_sha256(artifact: Mapping[str, Any]) -> str:
  1520	    """Return the reviewed exact-byte pin for a validated artifact role."""
  1521	
  1522	    registry = load_calibration_acceptance_registry(
  1523	        require_committed=(
  1524	            _git_head_bytes(DEFAULT_ACCEPTANCE_REGISTRY_PATH.resolve(), _REPO_ROOT)
  1525	            is not None
  1526	        )
  1527	    )
  1528	    active = _active_registry_entry(registry) if registry is not None else None
  1529	    if active is not None and active.get("acceptance_id") == artifact.get("acceptance_id"):
  1530	        return str(active["artifact_sha256"])
  1531	    return (
  1532	        ISSUED_ACCEPTANCE_BOUND_SHA256
  1533	        if artifact.get("artifact_role") == "issued"
  1534	        else DEFAULT_ACCEPTANCE_BOUND_SHA256
  1535	    )
  1536	
  1537	
  1538	def _valid_sha256(value: Any) -> bool:
  1539	    return (
  1540	        isinstance(value, str)

codex
# U2 Cold-Gate Packet — D-102 Successor Engine

Exhibit under review: `impl/d117-u2-successor` at locally available commit `399ffebdf96d883857fa9effdb579e0e09b0857d`. Against current `main` (`cdb7896cb4c7f68613e659879bd4a323ddd7e481`), the exhibit changes four files: `configs/calibration/calibration_acceptance_registry.json`, `joulewise/calibration_bracketing.py`, `scripts/build_calibration_acceptance_successor.py`, and `tests/test_calibration_acceptance_successor.py`. It contains exactly one tag for each `COLD-GATE-Q1` through `COLD-GATE-Q12`.

## 1. The question

Should the twelve independently contestable semantics implemented by exhibit commit `399ffebd` be ratified as the D-102 calibration-acceptance successor engine: specifically, its corpus selection, successor preflight comparator, numerical method, count-boundary progression, systematic-failure policy, no-content policy, artifact lineage, registry authority, publication ordering, open-session probe behavior, post-observation reuse, and residual integration scope? The gate is asked to rule each question separately from the binding text and implementation evidence below; it is not asked to infer approval from the exhibit’s commit message or to approve live use, merge sequencing, or evidence not listed as examined.

## 2. Binding context

### D-102 — quoted in full

```text
## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics

- Date: 2026-08-01
- Status: accepted (magistrate ratification after the two-round Sol xhigh
  design consult + the independent n=19 corpus reconstruction; ALL
  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)
  quantile by numerical CDF, window B pre-cal value against primary
  evidence bytes)
- Applies to: CAL-BRACKET-D079-01, the future
  `configs/calibration/calibration_acceptance_d079_v2.json` artifact

The four pins D-079 left unexecutable, now pinned:

1. **Budget cap (Candidate A, 99% two-draw prediction family, derived
   blind from the pre-window-B n=19 corpus):**
   `max_budgetable_excess_s = 0.001275166090593858`;
   `maximum_budgetable_drift_s = 0.012093166090593858`
   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;
   cap = ceiling − operative screen 0.010818). Consequences verified: a
   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.
   **Window B itself remains refused regardless** — its pre-calibration
   0.035435840879704805 s (verified in primary evidence) exceeds the
   pre-flight level screen, and D-079 cl.2's systematic failure is
   never budgetable. The CAL-BRACKET regression at ~11 ms models the
   DRIFT BRANCH only, never a whole-window B pass.
2. **Freshness = exact identity epoch, no calendar hard expiry:** the
   artifact binds {os_build, hardware_model, power_policy,
   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any
   change → `calibration_acceptance_bound_stale`. Mandatory prospective
   re-derivation triggers: any identity-field change; protocol/estimator
   byte change; a new valid same-identity calibration expanding the
   observed range; corpus doubling (19→38); a new systematic failure
   challenging the pre-flight screen. A trigger observation is judged
   under the PRIOR artifact — never incorporated into a threshold that
   judges itself. Calendar-age fields are provenance/advisory only (the
   corpus spans four days; a calendar constant would be invented).
3. **Never-zero allowance confirmed:**
   `A_s = max(observed_drift_s, 0.010818)`;
   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the
   authenticated operative fiducial bound (anchor-envelope
   re-reduction); no second calibration-drift energy term anywhere
   downstream (D-078 cl.11 single-count).
4. **Decimal numeric semantics:** the artifact stores source decimal
   lexemes and exact-decimal derivations (range
   0.010817749309353528 s; 95% prediction 0.008826584887500717 s;
   pre-flight exact max 0.03355875667989999 s) SEPARATELY from the
   ratified operative comparators (0.010818; 0.033558756679900;
   ROUND_HALF_EVEN at the declared quantum), hashing the decimal
   strings + rounding rule into the derivation sha256. D-079's
   12-place `0.010817749309` is a LABELLED presentation value, never a
   comparator. Acceptance comparisons run in decimal semantics;
   binary64 conversion happens only at the reducer boundary and is
   recorded.

Corpus provenance: the n=19 member list with per-member manifest and
evidence sha256s is reconstructed and lead-spot-verified (2026-08-01
session records; summary in the session custody dir) — the artifact
copies those tables verbatim with re-verification at authoring, never
retyped. Implementation remains sequenced behind gauntlet commit 3 and
the D-100 repair (shared write surfaces).

Revisit when: CAL-BRACKET-D079-01's delta audit reports, or any
re-derivation trigger fires.
```

### D-116 — quoted in full

```text
## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)

**2026-08-07 supersession note:** The historical re-mint consequence later
superseded by D-117 is retained unchanged as historical context. Current
rule ownership: D-117.

**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**

**What was written.**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).

**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).

**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.

**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.

**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.
```

### Finding L4 — quoted in full

```text
- L4 HIGH: pre-flight screens only a COPIED SCALAR (0.033558…), not
  the issued artifact/identity epoch/range triggers — science can run
  all night then be rejected at the morning verdict (identity epoch
  change; sub-corpus-minimum lag). Closure = memo §5A step 6 pre-science
  acceptance + D-102 trigger probe (U2) + de-duplicating the hardcoded
  literal. U2 review must include both scenarios.
- Loader itself verified correct at HEAD (issued role, file sha
  316113960c…, estimator hashes match).
```

## 3. The twelve questions

### Q1 — Successor corpus

**Question.** Must a successor derive from every content-distinct valid observation in the active six-field epoch through the authenticated cutoff, including all 30 valid observations already present at sequence 76?

**Brief’s recommendation.** Yes: use the complete valid same-epoch prefix. The brief states that a first range-triggered successor would contain the existing 30 valid observations plus the triggering observation, not the frozen n=19 corpus plus only the trigger.

**Current exhibit.** `COLD-GATE-Q1` at `joulewise/calibration_bracketing.py:86`. The builder groups the full ledger observation universe by content ID, selects every `valid` representative in `active_epoch`, sorts by content ID, and derives from that list (`scripts/build_calibration_acceptance_successor.py:268–328,405–409`). The first-successor test expects `n=31` (`tests/test_calibration_acceptance_successor.py:552–565`).

**Strongest argument FOR the current choice.** It prevents suffix selection and duplicate-copy inflation, retains every governed valid observation, and matches D-116’s statement that 30 valid observations already count toward the 38-observation trigger. It also makes the successor reproducible from a complete authenticated prefix rather than a caller-chosen subset.

**Strongest argument AGAINST the current choice.** D-102 ratified its numerical basis as the blind pre-Window-B n=19 corpus, and D-116 says the issued artifact preserved that n=19 derivation corpus byte-identically while later valid observations did not influence the bound. D-102 requires re-derivation when a new valid observation expands the range, but does not itself say every intervening in-range observation becomes part of the next derivation.

**If ruled otherwise.** The gate must define the replacement corpus rule—such as frozen n=19 plus qualifying triggers, or post-parent valid observations under another fixed rule. Corpus construction, `n`, statistics, next-boundary calculation, lineage, loader validation, and golden tests would change.

---

### Q2 — Successor preflight screen

**Question.** Is the successor preflight level screen the rounded maximum of the observed corpus maximum and the 95% two-draw prediction, or is it derived from another source?

**Brief’s recommendation.** The proposed derivation uses `max(observed maximum, prediction_95_two_draw)` rounded half-even at `1e-15`. The brief also marks this formula as requiring an explicit cold ruling because the current loader’s observed-maximum rule and the runbook’s max rule agree at n=19 but can diverge later.

**Current exhibit.** `COLD-GATE-Q2` at `joulewise/calibration_bracketing.py:91`. The code computes `preflight_source = max(maximum, prediction_95)` and quantizes it to `0.000000000000001` (`joulewise/calibration_bracketing.py:456–459`), recording the rule and operative value at lines `511–519`.

**Strongest argument FOR the current choice.** It preserves both observed-level and modeled-tail information in a deterministic Decimal comparator and matches the rule described in the runbook-facing design. It also reproduces the issued n=19 operative exactly.

**Strongest argument AGAINST the current choice.** D-102 identifies the preflight source as the “pre-flight exact max” and records the 95% prediction separately. Taking the larger value can make the systematic-failure threshold more permissive when the prediction exceeds the observed maximum, changing which future observations are classified as systematic. D-102 does not explicitly ratify that combination.

**If ruled otherwise.** `derive_successor_decimal_derivation`, the schema’s `source_rule`, operative-value validation, systematic classification, discriminating fixtures, and golden bytes must use the ruled source formula.

---

### Q3 — Student-t numerical method and precision

**Question.** Which deterministic Student-t quantile implementation and Decimal precision govern successor corpora whose degrees of freedom differ from 18?

**Brief’s recommendation.** Version and pin the numerical algorithm and precision, perform accumulation in an 80-digit Decimal context, and retain an explicit compatibility pin for D-102’s df=18 values. The brief does not independently establish the particular incomplete-beta implementation later chosen by the exhibit.

**Current exhibit.** `COLD-GATE-Q3` at `joulewise/calibration_bracketing.py:94`. It selects `decimal_incomplete_beta_bisection_v1` at 80 Decimal digits. The implementation computes π, beta functions, an incomplete-beta continued fraction, Student-t survival, and bisection (`joulewise/calibration_bracketing.py:268–403`). It hard-codes extended df=18 quantiles at lines `151–158` and records algorithm and precision in artifact bytes at lines `465–475`.

**Strongest argument FOR the current choice.** It is deterministic, dependency-free, avoids binary64 mediation, records its identity in the artifact, and reproduces the issued n=19 operative values. New degrees of freedom can be derived without relying on an ambient library version.

**Strongest argument AGAINST the current choice.** D-102 ratified the df=18 coefficient and a bench-replayed numerical CDF, not this general-purpose custom incomplete-beta implementation or its additional digits. An 80-digit context does not itself establish convergence or error bounds across future degrees of freedom and tail probabilities; no independent numerical comparison was included among the examined evidence.

**If ruled otherwise.** Replace or version the quantile implementation, precision and convergence contract; regenerate quantile metadata, predictions, operatives, derivation hashes, and numerical golden tests.

---

### Q4 — Count-boundary progression

**Question.** After a range-triggered successor below the pending boundary, does the old boundary remain; once the boundary is reached or crossed, is the next boundary twice the newly issued corpus count?

**Brief’s recommendation.** Retain 38 after an n=31 range successor; after an n=38 successor, advance to 76.

**Current exhibit.** `COLD-GATE-Q4` at `joulewise/calibration_bracketing.py:98`. The builder sets `next_boundary = parent_boundary` when `count < parent_boundary`, otherwise `2 * count` (`scripts/build_calibration_acceptance_successor.py:329–332`). The loader recomputes that rule (`joulewise/calibration_bracketing.py:784–797`), and the probe triggers at `total_valid_same_epoch >= boundary` (`joulewise/calibration_bracketing.py:1907–1913`).

**Strongest argument FOR the current choice.** It preserves D-102’s literal 19→38 boundary and D-116’s statement that the existing 30 need eight more. A range-triggered n=31 artifact does not erase the already-near count trigger by resetting it to 62.

**Strongest argument AGAINST the current choice.** “Corpus doubling” can be read as doubling each newly issued derivation corpus, which would make an n=31 successor’s next boundary 62. Conversely, if a batch crosses 38 at n=40, the exhibit sets the next boundary to 80 rather than the original schedule’s 76; the result depends on batch size rather than only on the ratified 19→38 lineage.

**If ruled otherwise.** Specify whether boundaries double every issued corpus, follow a fixed 19/38/76 schedule, or use another rule. Builder arithmetic, probe triggers, schema validation, and boundary tests must change accordingly.

---

### Q5 — New systematic failure

**Question.** Does a newly authenticated systematic failure block every automatic successor build until an authority ruling disposes it, or does it block only the affected attempt?

**Brief’s recommendation.** Persistent refusal pending a new ruling.

**Current exhibit.** `COLD-GATE-Q5` at `joulewise/calibration_bracketing.py:101`. A new same-epoch `systematic-invalid` observation—or a nominally valid one above the active artifact’s preflight screen—returns `systematic_refusal` with policy `persistent_refusal_pending_new_ruling` (`joulewise/calibration_bracketing.py:1846–1883`). The builder accepts only `successor_required`, so it cannot issue through this outcome.

**Strongest argument FOR the current choice.** It prevents an automatic successor from loosening a threshold to absorb the observation that challenged it. That preserves D-102’s prior-artifact judgment rule and its statement that the Window-B systematic failure is never budgetable.

**Strongest argument AGAINST the current choice.** D-102 calls a new systematic failure a mandatory re-derivation trigger, not expressly a permanent issuance stop. D-116 issued an artifact even though the prior set contains two systematic-invalid observations; this shows that governed systematic observations can coexist with issuance once classified. A persistent stop can also prevent an unrelated later valid range/count trigger from being processed.

**If ruled otherwise.** Define the closure that makes a systematic observation no longer “new.” The probe and builder would need to record and exclude it while allowing later qualifying successors, with tests proving it never enters the derivation corpus or judges itself.

---

### Q6 — Abandoned and no-content attempts

**Question.** Which no-content attempts may be recorded without blocking issuance?

**Brief’s recommendation.** Record them in `noncontent_attempts`, but refuse issuance until governed closure establishes that they cannot conceal a classifiable observation.

**Current exhibit.** `COLD-GATE-Q6` at `joulewise/calibration_bracketing.py:104`. Actual noncontent observations cause probe refusal and builder failure (`joulewise/calibration_bracketing.py:1814–1832`; `scripts/build_calibration_acceptance_successor.py:186–197`). The sole allowed record is an explicitly unused U1 slot identified by one terminal session abort, emitted as `governed-unused-slot` (`scripts/build_calibration_acceptance_successor.py:147–183`). The named policy constant is not otherwise consumed.

**Strongest argument FOR the current choice.** A terminal `abandoned` row can coexist with already-created evidence bytes; treating it as harmless could hide a valid, ordinary-invalid, or systematic observation and make prefix completeness outcome-selective. An unused reserved slot closed by the U1 state machine has a narrower non-concealment proof.

**Strongest argument AGAINST the current choice.** A sufficiently authenticated terminal no-content closure may establish that no observation exists and therefore cannot affect D-102’s corpus or triggers. Treating all other no-content shapes as an indefinite authority stop can turn an availability event into a permanent successor blockade even when the ledger honestly preserves it.

**If ruled otherwise.** Define the admissible terminal evidence for no-content rows. The probe, `_noncontent_rows`, successor schema, and tests must either admit those rows or refuse even governed unused U1 slots.

---

### Q7 — v3 lineage, naming, and parent availability

**Question.** Must successors use the proposed v3 schema, cutoff-derived immutable filenames, a single-parent chain, and locally present historical parent bytes?

**Brief’s recommendation.** Use schema `joulewise.calibration_acceptance_bound.v3`, deterministic ID/path `..._s<sequence>_<head-prefix>`, immutable artifacts, and single-parent ancestry. The brief leaves “parents always present” versus “recoverable from Git history” for the gate.

**Current exhibit.** `COLD-GATE-Q7` at `joulewise/calibration_bracketing.py:107`. IDs and paths derive from the cutoff sequence and first 16 head-digest characters (`scripts/build_calibration_acceptance_successor.py:337–345`). Registry validation enforces one root, one child per parent, one active leaf and contiguous generations (`joulewise/calibration_bracketing.py:655–695`). Loading reads and authenticates every registered artifact from the current checkout; missing parents refuse (`joulewise/calibration_bracketing.py:738–798`). Successor filenames are pattern-checked at lines `763–774`.

**Strongest argument FOR the current choice.** Exact on-disk ancestry makes the trust chain reviewable and available to ordinary consumers without reconstructing Git history. Immutable cutoff-derived paths avoid overwriting authority bytes and preserve D-116’s issued anchor as the lineage root.

**Strongest argument AGAINST the current choice.** D-102 does not prescribe v3 naming or permanent working-tree retention of every ancestor. Git-authenticated recovery could retain exact bytes without making every inactive artifact a runtime dependency; requiring all ancestors locally increases load cost and makes deletion or checkout sparsity invalidate the active artifact.

**If ruled otherwise.** If Git recovery is allowed, the loader must authenticate missing inactive parents from a defined commit/object identity. Any different schema, name, prefix length, branching rule, or retention rule requires corresponding builder, registry, validator, and fixture changes.

---

### Q8 — Registry authority

**Question.** Is the committed registry the sole rotating trust anchor, with exactly one active leaf and exact SHA-256 authentication of every artifact?

**Brief’s recommendation.** Yes: committed registry bytes, one active entry, exact artifact SHA, and no new code-side constant for each successor.

**Current exhibit.** `COLD-GATE-Q8` at `joulewise/calibration_bracketing.py:110`. The bootstrap registry has one active v2 entry and exact artifact/derivation/cutoff hashes (`configs/calibration/calibration_acceptance_registry.json:1–22`). `load_calibration_acceptance_registry` rejects non-HEAD-equal committed bytes when commitment is required, invalid topology, path substitution, and artifact/hash mismatch (`joulewise/calibration_bracketing.py:712–799`). The builder deactivates old entries and adds one active successor (`scripts/build_calibration_acceptance_successor.py:425–449`).

**Strongest argument FOR the current choice.** It allows authority to rotate without a new executable constant for every successor, while keeping the active bytes, derivation, cutoff and ancestry exact and Git-reviewed. One active leaf removes ambiguous selection.

**Strongest argument AGAINST the current choice.** D-102 authenticates the artifact but does not independently ratify a registry as the sole trust root. The implementation’s ordinary committed mode compares the registry to `git show HEAD:<path>`; after publication changes the worktree registry, consumers refuse it until a separate Git commit lands. That creates another sequencing boundary around the active authority.

**If ruled otherwise.** Specify the replacement trust anchor—such as a code pin, head-pin binding, signed root, or another committed manifest—and its rollback, rotation, and active-selection rules. Registry loading and all ordinary consumers must follow that authority.

---

### Q9 — Publication and head-pin ordering

**Question.** Must artifact, registry and head pin co-land as one governed transition, or may the ledger head be committed first and treated as immutable input while artifact bytes publish before a registry-last authority switch?

**Brief’s recommendation.** Co-land artifact, registry and head-pin authority, with no claim evaluation between ledger advancement and committed successor authority.

**Current exhibit.** `COLD-GATE-Q9` at `joulewise/calibration_bracketing.py:113` chooses `artifact_first_registry_last_head_input_only`. Building requires a terminal snapshot whose physical and committed head already match (`scripts/build_calibration_acceptance_successor.py:220–231`). Publication locks the registry, stages both buffers, installs the immutable artifact first, then replaces the registry as the authority point (`scripts/build_calibration_acceptance_successor.py:502–578`). It does not write or commit the head pin.

**Strongest argument FOR the current choice.** The builder cannot derive from an uncommitted or moving ledger. Artifact-first makes an interrupted artifact an inert orphan; registry-last prevents authority from pointing at absent bytes and gives a clear retryable filesystem commit point.

**Strongest argument AGAINST the current choice.** It does not implement the brief’s co-landing rule. There is an interval after ledger/head commitment but before registry replacement, followed by another interval before the changed registry equals Git HEAD. The four-file exhibit contains no universal claim-evaluation barrier spanning those intervals. D-116 records an earlier sequencing HOLD involving the same general risk class.

**If ruled otherwise.** A co-landing ruling requires a specified transaction, journal, sealed bundle, or external start fence that binds head, artifact and registry across filesystem replacement and Git commitment. If head-first is accepted, the operational barrier and recovery states must be explicit and mechanically enforced.

---

### Q10 — Probe with an open U1 post slot

**Question.** May the pre-science probe inspect a governed U1 two-slot session after pre evidence exists while the post slot remains prospectively open, and what closure is required before successor issuance?

**Brief’s recommendation.** The brief does not give an unconditional yes/no. Its proposed sequence permits the probe before science with the post slot still governed; if a successor is required, the session must be closed or aborted under U1, the terminal head committed, and only then may issuance proceed.

**Current exhibit.** `COLD-GATE-Q10` at `joulewise/calibration_bracketing.py:116`. The probe accepts the otherwise-invalid physical/pin gap only when `is_governed_open_bracket_extension` holds and the refusal set is exactly `calibration_ledger_bracket_session_open` plus `calibration_ledger_head_mismatch` (`joulewise/calibration_bracketing.py:1733–1755`). U1’s predicate requires one open session whose tail extends the committed head (`joulewise/calibration_ledger.py:281–308`). The builder separately refuses any nonterminal or uncommitted head (`scripts/build_calibration_acceptance_successor.py:220–231`). The named Q10 policy constant is not otherwise consumed.

**Strongest argument FOR the current choice.** It lets §5A judge pre evidence before science without discarding the reserved post capability, while keeping issuance behind terminal closure and committed-head equality. The exception is tied to a narrow authenticated ledger shape.

**Strongest argument AGAINST the current choice.** The predicate relaxes normal head equality and does not itself state “pre finalized and post unclaimed”; it recognizes a broader open-session tail. A stricter reading could require the pre slot’s exact terminal state or prohibit any probe while the committed trust anchor lags physical receipts.

**If ruled otherwise.** A no-open-session ruling requires abort/finalization and head commitment before probing. A narrower-open ruling requires an explicit pre-finalized/post-unused predicate and discriminating tests for every other U1 state.

---

### Q11 — Parent-judged post evidence under a successor

**Question.** May an observation judged under the parent artifact later participate in bracket evaluation under the successor that incorporates it, provided parent judgment is recorded explicitly?

**Brief’s recommendation.** Permit it only with explicit parent-artifact judgment evidence retained in lineage.

**Current exhibit.** `COLD-GATE-Q11` at `joulewise/calibration_bracketing.py:120`. The builder stores the parent acceptance ID, parent artifact SHA, `successor_required` result, new content IDs and triggers in `lineage.trigger_judgment` (`scripts/build_calibration_acceptance_successor.py:368–381`). The loader verifies that structure against the parent (`joulewise/calibration_bracketing.py:887–918`). The builder then constructs an in-memory `successor_probe` carrying the policy name (`scripts/build_calibration_acceptance_successor.py:451–462`). No non-test consumer of `POST_SUCCESSOR_POLICY` was found beyond that output field.

**Strongest argument FOR the current choice.** It preserves evidence that the triggering observation was classified under the old threshold before inclusion, so the successor does not erase the prior judgment. It can avoid discarding a completed pre/post bracket solely because a mandatory successor was issued afterward.

**Strongest argument AGAINST the current choice.** D-102 says a trigger observation is “never incorporated into a threshold that judges itself.” Even if a parent probe is recorded, later bracket evaluation under successor operatives derived partly from that same observation may be read as self-fit. The exhibit validates lineage but does not show a downstream consumer enforcing the exact post-reuse condition.

**If ruled otherwise.** If reuse is forbidden, the affected bracket must remain evaluated under its parent or be aborted and recollected under the successor. If reuse is allowed, a landing gate must determine whether lineage validation alone is sufficient or whether the bracket consumer must explicitly bind and verify the parent judgment.

---

### Q12 — U2 scope and L4 closure

**Question.** Must U2 remove the writer’s copied scalar now, or may it land only the successor/probe API while writer and arm-path integration remain separately gated?

**Brief’s recommendation.** Expand U2 from four files to six by adding `scripts/validate_powermetrics_fiducial.py` and `tests/test_powermetrics_fiducial.py`; leave the runbook/readiness arm-path call to U8. The brief says L4 should retire only after both integrations land.

**Current exhibit.** `COLD-GATE-Q12` at `joulewise/calibration_bracketing.py:123` declares `probe_closed_writer_and_arm_path_residual`. The diff is limited to four files. On the exhibit branch, the writer still defines `PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")` at `scripts/validate_powermetrics_fiducial.py:103` and uses it to assign `systematic-invalid` at lines `913–920`. The new test only proves that changing the copied scalar does not alter the separate U2 probe (`tests/test_calibration_acceptance_successor.py:456–463`). No U8 arm-path integration is present.

**Strongest argument FOR the current choice.** It keeps the exhibit within the original four-file U2 work order and separates the authenticated pure probe from live-writer and operator-chain changes. The residual can remain an explicit landing or arm blocker.

**Strongest argument AGAINST the current choice.** Finding L4 says closure requires both the U2 probe and de-duplication of the hardcoded literal, and specifically requires U2 review of identity-change and sub-corpus-minimum scenarios. The current live writer can still classify from the copied scalar without authenticating the registry, active artifact, epoch or range trigger.

**If ruled otherwise.** A six-file ruling requires the writer to load the authenticated active artifact, obtain its epoch and preflight comparator, invoke or consume the trigger probe at the proper point, and add writer-level regressions. U8 would still own the runbook/readiness arm path. A four-file ruling must preserve writer integration as a named blocking unit and must not describe L4 as closed.

## 4. Unswept evidence

The following was not examined or established:

- Remote freshness was not independently established. A literal `git fetch origin impl/d117-u2-successor` was attempted but could not write the shared checkout’s `FETCH_HEAD` because Git metadata is mounted read-only. A read-only `git ls-remote` then failed because `github.com` could not be resolved. The local branch and cached `origin/impl/d117-u2-successor` both point to `399ffebd`; the remote-tracking reflog records an update by push at `2026-08-07 13:15:09 -0700`.
- No tests were run. The focused test source was inspected, but neither `tests.test_calibration_acceptance_successor` nor the canonical suite was executed.
- No live ledger, raw calibration custody, iCloud backup, evidence artifact, or quiet-machine/hardware behavior was examined.
- D-109, D-117, the full plan-freeze memo, RATIFICATION ruling 3, U1’s complete contract record, and U8’s readiness implementation were not substantively reviewed as governing sources. D-116’s supersession note expressly assigns current rule ownership to D-117; any ruling that depends on D-117 rather than the quoted D-102/D-116 text should defer on that missing authority.
- No independent numerical reference implementation, error-bound analysis, or cross-library Student-t comparison was examined for Q3.
- No crash injection, concurrent publisher test, Git-commit transition test, or recovery exercise was performed for Q8/Q9.
- No end-to-end consumer was traced that enforces Q11’s post-observation reuse condition beyond validating the successor’s lineage record.
- The live runbook’s copied-scalar site and U8 arm path were not changed by this exhibit.
- The working tree already contained unrelated user modifications. The quoted D-102 text is unchanged from `HEAD`; the quoted D-116 entry includes the current working-tree supersession note. No repository file was written by packet assembly.

A gate should return `DEFER` rather than assume facts from any unswept category on which its ruling depends.

## 5. Required gate return

For each question, return exactly one of:

- `RATIFY_AS_IMPLEMENTED`
- `OVERRULE — <replacement semantic>`
- `DEFER — <specific missing evidence or authority>`

The proposition to decide for each line is:

1. **Q1:** complete content-distinct valid same-epoch prefix through cutoff.
2. **Q2:** preflight screen = `max(observed maximum, 95% two-draw prediction)`, rounded half-even at `1e-15`.
3. **Q3:** `decimal_incomplete_beta_bisection_v1`, 80 Decimal digits, with explicit df=18 compatibility pins.
4. **Q4:** retain the pending boundary until reached/crossed, then set the next boundary to twice the newly issued corpus count.
5. **Q5:** persistent automatic-issuance refusal after a new systematic observation until an authority ruling.
6. **Q6:** refuse actual no-content observations; allow only explicitly unused U1 slots proven by terminal session abort.
7. **Q7:** v3 cutoff-named immutable artifacts, single-parent ancestry, all registered parent bytes present in the checkout.
8. **Q8:** committed registry as sole rotating trust anchor, exactly one active leaf, exact artifact hashes.
9. **Q9:** committed terminal head as input; immutable artifact first; registry replacement last as authority point.
10. **Q10:** permit the probe over the narrowly recognized governed open U1 extension; require terminal committed closure before building.
11. **Q11:** permit successor-era use of parent-judged evidence when explicit parent judgment is retained in lineage.
12. **Q12:** four-file probe exhibit with writer copied-scalar removal and U8 arm-path integration left as separately gated residuals.
tokens used
160,331
# U2 Cold-Gate Packet — D-102 Successor Engine

Exhibit under review: `impl/d117-u2-successor` at locally available commit `399ffebdf96d883857fa9effdb579e0e09b0857d`. Against current `main` (`cdb7896cb4c7f68613e659879bd4a323ddd7e481`), the exhibit changes four files: `configs/calibration/calibration_acceptance_registry.json`, `joulewise/calibration_bracketing.py`, `scripts/build_calibration_acceptance_successor.py`, and `tests/test_calibration_acceptance_successor.py`. It contains exactly one tag for each `COLD-GATE-Q1` through `COLD-GATE-Q12`.

## 1. The question

Should the twelve independently contestable semantics implemented by exhibit commit `399ffebd` be ratified as the D-102 calibration-acceptance successor engine: specifically, its corpus selection, successor preflight comparator, numerical method, count-boundary progression, systematic-failure policy, no-content policy, artifact lineage, registry authority, publication ordering, open-session probe behavior, post-observation reuse, and residual integration scope? The gate is asked to rule each question separately from the binding text and implementation evidence below; it is not asked to infer approval from the exhibit’s commit message or to approve live use, merge sequencing, or evidence not listed as examined.

## 2. Binding context

### D-102 — quoted in full

```text
## D-102: CAL-BRACKET-D079-01 pins ratified — corpus-derived budget cap, identity-epoch freshness, never-zero allowance, decimal numeric semantics

- Date: 2026-08-01
- Status: accepted (magistrate ratification after the two-round Sol xhigh
  design consult + the independent n=19 corpus reconstruction; ALL
  arithmetic lead-replayed at the bench: ceiling, cap, t(0.995,18)
  quantile by numerical CDF, window B pre-cal value against primary
  evidence bytes)
- Applies to: CAL-BRACKET-D079-01, the future
  `configs/calibration/calibration_acceptance_d079_v2.json` artifact

The four pins D-079 left unexecutable, now pinned:

1. **Budget cap (Candidate A, 99% two-draw prediction family, derived
   blind from the pre-window-B n=19 corpus):**
   `max_budgetable_excess_s = 0.001275166090593858`;
   `maximum_budgetable_drift_s = 0.012093166090593858`
   (= t(0.995,18)=2.878440472713585 × sd 0.002970761365307205 × √2;
   cap = ceiling − operative screen 0.010818). Consequences verified: a
   ~11.58 ms drift branch is budgetable; a 15 ms bracket refuses.
   **Window B itself remains refused regardless** — its pre-calibration
   0.035435840879704805 s (verified in primary evidence) exceeds the
   pre-flight level screen, and D-079 cl.2's systematic failure is
   never budgetable. The CAL-BRACKET regression at ~11 ms models the
   DRIFT BRANCH only, never a whole-window B pass.
2. **Freshness = exact identity epoch, no calendar hard expiry:** the
   artifact binds {os_build, hardware_model, power_policy,
   sampling_interval_ms, estimator_revision, pulse_protocol_id}; any
   change → `calibration_acceptance_bound_stale`. Mandatory prospective
   re-derivation triggers: any identity-field change; protocol/estimator
   byte change; a new valid same-identity calibration expanding the
   observed range; corpus doubling (19→38); a new systematic failure
   challenging the pre-flight screen. A trigger observation is judged
   under the PRIOR artifact — never incorporated into a threshold that
   judges itself. Calendar-age fields are provenance/advisory only (the
   corpus spans four days; a calendar constant would be invented).
3. **Never-zero allowance confirmed:**
   `A_s = max(observed_drift_s, 0.010818)`;
   `B_operative = max(B_pre, B_post) + A_s`, embedded ONCE in the
   authenticated operative fiducial bound (anchor-envelope
   re-reduction); no second calibration-drift energy term anywhere
   downstream (D-078 cl.11 single-count).
4. **Decimal numeric semantics:** the artifact stores source decimal
   lexemes and exact-decimal derivations (range
   0.010817749309353528 s; 95% prediction 0.008826584887500717 s;
   pre-flight exact max 0.03355875667989999 s) SEPARATELY from the
   ratified operative comparators (0.010818; 0.033558756679900;
   ROUND_HALF_EVEN at the declared quantum), hashing the decimal
   strings + rounding rule into the derivation sha256. D-079's
   12-place `0.010817749309` is a LABELLED presentation value, never a
   comparator. Acceptance comparisons run in decimal semantics;
   binary64 conversion happens only at the reducer boundary and is
   recorded.

Corpus provenance: the n=19 member list with per-member manifest and
evidence sha256s is reconstructed and lead-spot-verified (2026-08-01
session records; summary in the session custody dir) — the artifact
copies those tables verbatim with re-verification at authoring, never
retyped. Implementation remains sequenced behind gauntlet commit 3 and
the D-100 repair (shared write surfaces).

Revisit when: CAL-BRACKET-D079-01's delta audit reports, or any
re-derivation trigger fires.
```

### D-116 — quoted in full

```text
## D-116: D-079 calibration acceptance artifact ISSUED; ledger genesis import executed (D-110 condition (b) SATISFIED)

**2026-08-07 supersession note:** The historical re-mint consequence later
superseded by D-117 is retained unchanged as historical context. Current
rule ownership: D-117.

**Date:** 2026-08-06 (Fable magistrate, overnight; issuance pre-authorized by Ed 2026-08-05 conditional on the gate passing).
**Status:** EXECUTED. This retires the schema fixture and issues the authoritative calibration acceptance artifact — the anchor all future floor-mint claims authenticate against. D-110 re-mint condition (b) ("R2 backfill verified, ledger bootstrapped, head pinned") is now SATISFIED; (a) was satisfied by PR #100, (c) by PR #105. **MINT-GENERALIZE-01 is UNBLOCKED for the re-mint.**

**What was written.**
- `runs/calibration_observation_ledger.jsonl` — the 76-receipt genesis historical-import chain (git-ignored local custody artifact, sha256 `aa80684848d0ce156ed2d14df47472006175840eda17f9025eff9754af694e3f`; deterministic from the custodied inputs below + the raw evidence; MUST be backed up per the runbook before the re-mint consumes it).
- `configs/calibration/calibration_ledger_head.json` — the repo-committed head pin (sequence 76, head_digest `08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`), the D-109 R1.4 anti-rollback trust anchor.
- `configs/calibration/calibration_acceptance_d079_v2.json` — flipped `schema_fixture_unissued` → **issued** (file sha256 `316113960c596a6f927987dbdf8f2bca4b0cca9ee4a59a540bbd32bba9048985`, whole-core `derivation_sha256` `4f6633d5fb89a6e8fd137a834728b843915027b6f0b0afd6c37ae24e65d23f02`; `claim_eligible=true`). Emitted deterministically (not hand-edited) from the historical-import finalizations.
- Reproducibility inputs custodied at `docs/process_traces/2026-08-06-d079-issuance-coldgate/` (disposition table sha `5da820aa…`, custody manifest sha `99cbf3df…`, execute summary, ledger sha).

**Disposition inventory (B1 lead-ruled).** 30 valid / 2 systematic-invalid / 6 ordinary-invalid. The two systematic-invalid members (`20260726T000039-491995f3`, `20260801T064830-c76f5d1c`) have bounds `0.035435840879704805` / `0.0350400833260715`, both exceeding the ratified pre-flight screen `0.033558756679900`; D-102 (§~6298) explicitly names the first a systematic failure "never budgetable." R2.8 counting: 30 valid < 38 threshold, so issuance does NOT itself trigger corpus-doubling re-derivation (eight further valid same-epoch observations would; R2.8's literal "six further" was conditioned on the superseded 32-valid candidate). derivation_corpus preserved byte-identical at n=19 (its fixture whole-core digest was `3cece3b2…`; that value is NOT carried into the issued artifact — embedding it would fail the loader). All 38 custody locators are iCloud-backup copies (raw evidence is git-ignored by repo convention; integrity rests on the committed hash chain, not the custody pointer).

**Window-B completeness note (soundness-critical, for any reviewer asking "why Window-B in the anchor?").** The `prior_observation_set` correctly includes 6 `window_metrologyB` **calibration fiducial** observations (2 valid: `e0ce33f5`, `8c3bfe9e`), as mandated by D-109 R2.3/R2.8 completeness (every content-distinct governed CALIBRATION observation). This is NOT a D-113 violation: D-113 retired Window B's WINDOW CLAIM consumption (its null-ladder/additivity science members), not the calibration fiducials collected in that period; the general calibration machinery survives per D-113. These fiducials are EXCLUDED from the frozen n=19 threshold basis (which is Window-A-only) and do not influence the bound.

**Gate history (the process earned its keep on the anchor).** Two rule-11 cold gates. Cold gate #1 (on the plan) HELD correctly — the naive JSON-edit plan had no issued-artifact consumer (F1) and would have invalidated the whole-core digest (F2). That forced a real consumer implementation, which then ran the full C-028 gauntlet: adversarial audit (consumer proven false-ACCEPT-resistant; 3 emission/execute blockers incl. ledger-commit-BEFORE-artifact-validation) → fix → delta (exit-3 masking) → fix → final delta ACCEPT. Cold gate #2 (on the exact bytes): both lenses PROCEED on CONTENT (head/dispositions/B1/R2 all independently reproduced); HOLD on sequencing only — the consumer had to land on main before writing the issued artifact, else the anchor bricks. Resolved by merging PR #108 first, then executing against consumer-present main, with the co-landing verification (`_valid_acceptance_bound(issued)=True`) confirmed post-write. Full records: `docs/process_traces/2026-08-06-d079-issuance-coldgate/`.

**Consequences.** MINT-GENERALIZE-01 (b) satisfied; the re-mint (a10 extraction + mint #1 re-derivation under the corrected selector, embedding the D-102 pin-3 never-zero drift allowance) is the next step — the path to a non-empty claims table. The runs/ ledger must be custody-backed before the re-mint consumes it.
```

### Finding L4 — quoted in full

```text
- L4 HIGH: pre-flight screens only a COPIED SCALAR (0.033558…), not
  the issued artifact/identity epoch/range triggers — science can run
  all night then be rejected at the morning verdict (identity epoch
  change; sub-corpus-minimum lag). Closure = memo §5A step 6 pre-science
  acceptance + D-102 trigger probe (U2) + de-duplicating the hardcoded
  literal. U2 review must include both scenarios.
- Loader itself verified correct at HEAD (issued role, file sha
  316113960c…, estimator hashes match).
```

## 3. The twelve questions

### Q1 — Successor corpus

**Question.** Must a successor derive from every content-distinct valid observation in the active six-field epoch through the authenticated cutoff, including all 30 valid observations already present at sequence 76?

**Brief’s recommendation.** Yes: use the complete valid same-epoch prefix. The brief states that a first range-triggered successor would contain the existing 30 valid observations plus the triggering observation, not the frozen n=19 corpus plus only the trigger.

**Current exhibit.** `COLD-GATE-Q1` at `joulewise/calibration_bracketing.py:86`. The builder groups the full ledger observation universe by content ID, selects every `valid` representative in `active_epoch`, sorts by content ID, and derives from that list (`scripts/build_calibration_acceptance_successor.py:268–328,405–409`). The first-successor test expects `n=31` (`tests/test_calibration_acceptance_successor.py:552–565`).

**Strongest argument FOR the current choice.** It prevents suffix selection and duplicate-copy inflation, retains every governed valid observation, and matches D-116’s statement that 30 valid observations already count toward the 38-observation trigger. It also makes the successor reproducible from a complete authenticated prefix rather than a caller-chosen subset.

**Strongest argument AGAINST the current choice.** D-102 ratified its numerical basis as the blind pre-Window-B n=19 corpus, and D-116 says the issued artifact preserved that n=19 derivation corpus byte-identically while later valid observations did not influence the bound. D-102 requires re-derivation when a new valid observation expands the range, but does not itself say every intervening in-range observation becomes part of the next derivation.

**If ruled otherwise.** The gate must define the replacement corpus rule—such as frozen n=19 plus qualifying triggers, or post-parent valid observations under another fixed rule. Corpus construction, `n`, statistics, next-boundary calculation, lineage, loader validation, and golden tests would change.

---

### Q2 — Successor preflight screen

**Question.** Is the successor preflight level screen the rounded maximum of the observed corpus maximum and the 95% two-draw prediction, or is it derived from another source?

**Brief’s recommendation.** The proposed derivation uses `max(observed maximum, prediction_95_two_draw)` rounded half-even at `1e-15`. The brief also marks this formula as requiring an explicit cold ruling because the current loader’s observed-maximum rule and the runbook’s max rule agree at n=19 but can diverge later.

**Current exhibit.** `COLD-GATE-Q2` at `joulewise/calibration_bracketing.py:91`. The code computes `preflight_source = max(maximum, prediction_95)` and quantizes it to `0.000000000000001` (`joulewise/calibration_bracketing.py:456–459`), recording the rule and operative value at lines `511–519`.

**Strongest argument FOR the current choice.** It preserves both observed-level and modeled-tail information in a deterministic Decimal comparator and matches the rule described in the runbook-facing design. It also reproduces the issued n=19 operative exactly.

**Strongest argument AGAINST the current choice.** D-102 identifies the preflight source as the “pre-flight exact max” and records the 95% prediction separately. Taking the larger value can make the systematic-failure threshold more permissive when the prediction exceeds the observed maximum, changing which future observations are classified as systematic. D-102 does not explicitly ratify that combination.

**If ruled otherwise.** `derive_successor_decimal_derivation`, the schema’s `source_rule`, operative-value validation, systematic classification, discriminating fixtures, and golden bytes must use the ruled source formula.

---

### Q3 — Student-t numerical method and precision

**Question.** Which deterministic Student-t quantile implementation and Decimal precision govern successor corpora whose degrees of freedom differ from 18?

**Brief’s recommendation.** Version and pin the numerical algorithm and precision, perform accumulation in an 80-digit Decimal context, and retain an explicit compatibility pin for D-102’s df=18 values. The brief does not independently establish the particular incomplete-beta implementation later chosen by the exhibit.

**Current exhibit.** `COLD-GATE-Q3` at `joulewise/calibration_bracketing.py:94`. It selects `decimal_incomplete_beta_bisection_v1` at 80 Decimal digits. The implementation computes π, beta functions, an incomplete-beta continued fraction, Student-t survival, and bisection (`joulewise/calibration_bracketing.py:268–403`). It hard-codes extended df=18 quantiles at lines `151–158` and records algorithm and precision in artifact bytes at lines `465–475`.

**Strongest argument FOR the current choice.** It is deterministic, dependency-free, avoids binary64 mediation, records its identity in the artifact, and reproduces the issued n=19 operative values. New degrees of freedom can be derived without relying on an ambient library version.

**Strongest argument AGAINST the current choice.** D-102 ratified the df=18 coefficient and a bench-replayed numerical CDF, not this general-purpose custom incomplete-beta implementation or its additional digits. An 80-digit context does not itself establish convergence or error bounds across future degrees of freedom and tail probabilities; no independent numerical comparison was included among the examined evidence.

**If ruled otherwise.** Replace or version the quantile implementation, precision and convergence contract; regenerate quantile metadata, predictions, operatives, derivation hashes, and numerical golden tests.

---

### Q4 — Count-boundary progression

**Question.** After a range-triggered successor below the pending boundary, does the old boundary remain; once the boundary is reached or crossed, is the next boundary twice the newly issued corpus count?

**Brief’s recommendation.** Retain 38 after an n=31 range successor; after an n=38 successor, advance to 76.

**Current exhibit.** `COLD-GATE-Q4` at `joulewise/calibration_bracketing.py:98`. The builder sets `next_boundary = parent_boundary` when `count < parent_boundary`, otherwise `2 * count` (`scripts/build_calibration_acceptance_successor.py:329–332`). The loader recomputes that rule (`joulewise/calibration_bracketing.py:784–797`), and the probe triggers at `total_valid_same_epoch >= boundary` (`joulewise/calibration_bracketing.py:1907–1913`).

**Strongest argument FOR the current choice.** It preserves D-102’s literal 19→38 boundary and D-116’s statement that the existing 30 need eight more. A range-triggered n=31 artifact does not erase the already-near count trigger by resetting it to 62.

**Strongest argument AGAINST the current choice.** “Corpus doubling” can be read as doubling each newly issued derivation corpus, which would make an n=31 successor’s next boundary 62. Conversely, if a batch crosses 38 at n=40, the exhibit sets the next boundary to 80 rather than the original schedule’s 76; the result depends on batch size rather than only on the ratified 19→38 lineage.

**If ruled otherwise.** Specify whether boundaries double every issued corpus, follow a fixed 19/38/76 schedule, or use another rule. Builder arithmetic, probe triggers, schema validation, and boundary tests must change accordingly.

---

### Q5 — New systematic failure

**Question.** Does a newly authenticated systematic failure block every automatic successor build until an authority ruling disposes it, or does it block only the affected attempt?

**Brief’s recommendation.** Persistent refusal pending a new ruling.

**Current exhibit.** `COLD-GATE-Q5` at `joulewise/calibration_bracketing.py:101`. A new same-epoch `systematic-invalid` observation—or a nominally valid one above the active artifact’s preflight screen—returns `systematic_refusal` with policy `persistent_refusal_pending_new_ruling` (`joulewise/calibration_bracketing.py:1846–1883`). The builder accepts only `successor_required`, so it cannot issue through this outcome.

**Strongest argument FOR the current choice.** It prevents an automatic successor from loosening a threshold to absorb the observation that challenged it. That preserves D-102’s prior-artifact judgment rule and its statement that the Window-B systematic failure is never budgetable.

**Strongest argument AGAINST the current choice.** D-102 calls a new systematic failure a mandatory re-derivation trigger, not expressly a permanent issuance stop. D-116 issued an artifact even though the prior set contains two systematic-invalid observations; this shows that governed systematic observations can coexist with issuance once classified. A persistent stop can also prevent an unrelated later valid range/count trigger from being processed.

**If ruled otherwise.** Define the closure that makes a systematic observation no longer “new.” The probe and builder would need to record and exclude it while allowing later qualifying successors, with tests proving it never enters the derivation corpus or judges itself.

---

### Q6 — Abandoned and no-content attempts

**Question.** Which no-content attempts may be recorded without blocking issuance?

**Brief’s recommendation.** Record them in `noncontent_attempts`, but refuse issuance until governed closure establishes that they cannot conceal a classifiable observation.

**Current exhibit.** `COLD-GATE-Q6` at `joulewise/calibration_bracketing.py:104`. Actual noncontent observations cause probe refusal and builder failure (`joulewise/calibration_bracketing.py:1814–1832`; `scripts/build_calibration_acceptance_successor.py:186–197`). The sole allowed record is an explicitly unused U1 slot identified by one terminal session abort, emitted as `governed-unused-slot` (`scripts/build_calibration_acceptance_successor.py:147–183`). The named policy constant is not otherwise consumed.

**Strongest argument FOR the current choice.** A terminal `abandoned` row can coexist with already-created evidence bytes; treating it as harmless could hide a valid, ordinary-invalid, or systematic observation and make prefix completeness outcome-selective. An unused reserved slot closed by the U1 state machine has a narrower non-concealment proof.

**Strongest argument AGAINST the current choice.** A sufficiently authenticated terminal no-content closure may establish that no observation exists and therefore cannot affect D-102’s corpus or triggers. Treating all other no-content shapes as an indefinite authority stop can turn an availability event into a permanent successor blockade even when the ledger honestly preserves it.

**If ruled otherwise.** Define the admissible terminal evidence for no-content rows. The probe, `_noncontent_rows`, successor schema, and tests must either admit those rows or refuse even governed unused U1 slots.

---

### Q7 — v3 lineage, naming, and parent availability

**Question.** Must successors use the proposed v3 schema, cutoff-derived immutable filenames, a single-parent chain, and locally present historical parent bytes?

**Brief’s recommendation.** Use schema `joulewise.calibration_acceptance_bound.v3`, deterministic ID/path `..._s<sequence>_<head-prefix>`, immutable artifacts, and single-parent ancestry. The brief leaves “parents always present” versus “recoverable from Git history” for the gate.

**Current exhibit.** `COLD-GATE-Q7` at `joulewise/calibration_bracketing.py:107`. IDs and paths derive from the cutoff sequence and first 16 head-digest characters (`scripts/build_calibration_acceptance_successor.py:337–345`). Registry validation enforces one root, one child per parent, one active leaf and contiguous generations (`joulewise/calibration_bracketing.py:655–695`). Loading reads and authenticates every registered artifact from the current checkout; missing parents refuse (`joulewise/calibration_bracketing.py:738–798`). Successor filenames are pattern-checked at lines `763–774`.

**Strongest argument FOR the current choice.** Exact on-disk ancestry makes the trust chain reviewable and available to ordinary consumers without reconstructing Git history. Immutable cutoff-derived paths avoid overwriting authority bytes and preserve D-116’s issued anchor as the lineage root.

**Strongest argument AGAINST the current choice.** D-102 does not prescribe v3 naming or permanent working-tree retention of every ancestor. Git-authenticated recovery could retain exact bytes without making every inactive artifact a runtime dependency; requiring all ancestors locally increases load cost and makes deletion or checkout sparsity invalidate the active artifact.

**If ruled otherwise.** If Git recovery is allowed, the loader must authenticate missing inactive parents from a defined commit/object identity. Any different schema, name, prefix length, branching rule, or retention rule requires corresponding builder, registry, validator, and fixture changes.

---

### Q8 — Registry authority

**Question.** Is the committed registry the sole rotating trust anchor, with exactly one active leaf and exact SHA-256 authentication of every artifact?

**Brief’s recommendation.** Yes: committed registry bytes, one active entry, exact artifact SHA, and no new code-side constant for each successor.

**Current exhibit.** `COLD-GATE-Q8` at `joulewise/calibration_bracketing.py:110`. The bootstrap registry has one active v2 entry and exact artifact/derivation/cutoff hashes (`configs/calibration/calibration_acceptance_registry.json:1–22`). `load_calibration_acceptance_registry` rejects non-HEAD-equal committed bytes when commitment is required, invalid topology, path substitution, and artifact/hash mismatch (`joulewise/calibration_bracketing.py:712–799`). The builder deactivates old entries and adds one active successor (`scripts/build_calibration_acceptance_successor.py:425–449`).

**Strongest argument FOR the current choice.** It allows authority to rotate without a new executable constant for every successor, while keeping the active bytes, derivation, cutoff and ancestry exact and Git-reviewed. One active leaf removes ambiguous selection.

**Strongest argument AGAINST the current choice.** D-102 authenticates the artifact but does not independently ratify a registry as the sole trust root. The implementation’s ordinary committed mode compares the registry to `git show HEAD:<path>`; after publication changes the worktree registry, consumers refuse it until a separate Git commit lands. That creates another sequencing boundary around the active authority.

**If ruled otherwise.** Specify the replacement trust anchor—such as a code pin, head-pin binding, signed root, or another committed manifest—and its rollback, rotation, and active-selection rules. Registry loading and all ordinary consumers must follow that authority.

---

### Q9 — Publication and head-pin ordering

**Question.** Must artifact, registry and head pin co-land as one governed transition, or may the ledger head be committed first and treated as immutable input while artifact bytes publish before a registry-last authority switch?

**Brief’s recommendation.** Co-land artifact, registry and head-pin authority, with no claim evaluation between ledger advancement and committed successor authority.

**Current exhibit.** `COLD-GATE-Q9` at `joulewise/calibration_bracketing.py:113` chooses `artifact_first_registry_last_head_input_only`. Building requires a terminal snapshot whose physical and committed head already match (`scripts/build_calibration_acceptance_successor.py:220–231`). Publication locks the registry, stages both buffers, installs the immutable artifact first, then replaces the registry as the authority point (`scripts/build_calibration_acceptance_successor.py:502–578`). It does not write or commit the head pin.

**Strongest argument FOR the current choice.** The builder cannot derive from an uncommitted or moving ledger. Artifact-first makes an interrupted artifact an inert orphan; registry-last prevents authority from pointing at absent bytes and gives a clear retryable filesystem commit point.

**Strongest argument AGAINST the current choice.** It does not implement the brief’s co-landing rule. There is an interval after ledger/head commitment but before registry replacement, followed by another interval before the changed registry equals Git HEAD. The four-file exhibit contains no universal claim-evaluation barrier spanning those intervals. D-116 records an earlier sequencing HOLD involving the same general risk class.

**If ruled otherwise.** A co-landing ruling requires a specified transaction, journal, sealed bundle, or external start fence that binds head, artifact and registry across filesystem replacement and Git commitment. If head-first is accepted, the operational barrier and recovery states must be explicit and mechanically enforced.

---

### Q10 — Probe with an open U1 post slot

**Question.** May the pre-science probe inspect a governed U1 two-slot session after pre evidence exists while the post slot remains prospectively open, and what closure is required before successor issuance?

**Brief’s recommendation.** The brief does not give an unconditional yes/no. Its proposed sequence permits the probe before science with the post slot still governed; if a successor is required, the session must be closed or aborted under U1, the terminal head committed, and only then may issuance proceed.

**Current exhibit.** `COLD-GATE-Q10` at `joulewise/calibration_bracketing.py:116`. The probe accepts the otherwise-invalid physical/pin gap only when `is_governed_open_bracket_extension` holds and the refusal set is exactly `calibration_ledger_bracket_session_open` plus `calibration_ledger_head_mismatch` (`joulewise/calibration_bracketing.py:1733–1755`). U1’s predicate requires one open session whose tail extends the committed head (`joulewise/calibration_ledger.py:281–308`). The builder separately refuses any nonterminal or uncommitted head (`scripts/build_calibration_acceptance_successor.py:220–231`). The named Q10 policy constant is not otherwise consumed.

**Strongest argument FOR the current choice.** It lets §5A judge pre evidence before science without discarding the reserved post capability, while keeping issuance behind terminal closure and committed-head equality. The exception is tied to a narrow authenticated ledger shape.

**Strongest argument AGAINST the current choice.** The predicate relaxes normal head equality and does not itself state “pre finalized and post unclaimed”; it recognizes a broader open-session tail. A stricter reading could require the pre slot’s exact terminal state or prohibit any probe while the committed trust anchor lags physical receipts.

**If ruled otherwise.** A no-open-session ruling requires abort/finalization and head commitment before probing. A narrower-open ruling requires an explicit pre-finalized/post-unused predicate and discriminating tests for every other U1 state.

---

### Q11 — Parent-judged post evidence under a successor

**Question.** May an observation judged under the parent artifact later participate in bracket evaluation under the successor that incorporates it, provided parent judgment is recorded explicitly?

**Brief’s recommendation.** Permit it only with explicit parent-artifact judgment evidence retained in lineage.

**Current exhibit.** `COLD-GATE-Q11` at `joulewise/calibration_bracketing.py:120`. The builder stores the parent acceptance ID, parent artifact SHA, `successor_required` result, new content IDs and triggers in `lineage.trigger_judgment` (`scripts/build_calibration_acceptance_successor.py:368–381`). The loader verifies that structure against the parent (`joulewise/calibration_bracketing.py:887–918`). The builder then constructs an in-memory `successor_probe` carrying the policy name (`scripts/build_calibration_acceptance_successor.py:451–462`). No non-test consumer of `POST_SUCCESSOR_POLICY` was found beyond that output field.

**Strongest argument FOR the current choice.** It preserves evidence that the triggering observation was classified under the old threshold before inclusion, so the successor does not erase the prior judgment. It can avoid discarding a completed pre/post bracket solely because a mandatory successor was issued afterward.

**Strongest argument AGAINST the current choice.** D-102 says a trigger observation is “never incorporated into a threshold that judges itself.” Even if a parent probe is recorded, later bracket evaluation under successor operatives derived partly from that same observation may be read as self-fit. The exhibit validates lineage but does not show a downstream consumer enforcing the exact post-reuse condition.

**If ruled otherwise.** If reuse is forbidden, the affected bracket must remain evaluated under its parent or be aborted and recollected under the successor. If reuse is allowed, a landing gate must determine whether lineage validation alone is sufficient or whether the bracket consumer must explicitly bind and verify the parent judgment.

---

### Q12 — U2 scope and L4 closure

**Question.** Must U2 remove the writer’s copied scalar now, or may it land only the successor/probe API while writer and arm-path integration remain separately gated?

**Brief’s recommendation.** Expand U2 from four files to six by adding `scripts/validate_powermetrics_fiducial.py` and `tests/test_powermetrics_fiducial.py`; leave the runbook/readiness arm-path call to U8. The brief says L4 should retire only after both integrations land.

**Current exhibit.** `COLD-GATE-Q12` at `joulewise/calibration_bracketing.py:123` declares `probe_closed_writer_and_arm_path_residual`. The diff is limited to four files. On the exhibit branch, the writer still defines `PREFLIGHT_SYSTEMATIC_SCREEN_S = Decimal("0.033558756679900")` at `scripts/validate_powermetrics_fiducial.py:103` and uses it to assign `systematic-invalid` at lines `913–920`. The new test only proves that changing the copied scalar does not alter the separate U2 probe (`tests/test_calibration_acceptance_successor.py:456–463`). No U8 arm-path integration is present.

**Strongest argument FOR the current choice.** It keeps the exhibit within the original four-file U2 work order and separates the authenticated pure probe from live-writer and operator-chain changes. The residual can remain an explicit landing or arm blocker.

**Strongest argument AGAINST the current choice.** Finding L4 says closure requires both the U2 probe and de-duplication of the hardcoded literal, and specifically requires U2 review of identity-change and sub-corpus-minimum scenarios. The current live writer can still classify from the copied scalar without authenticating the registry, active artifact, epoch or range trigger.

**If ruled otherwise.** A six-file ruling requires the writer to load the authenticated active artifact, obtain its epoch and preflight comparator, invoke or consume the trigger probe at the proper point, and add writer-level regressions. U8 would still own the runbook/readiness arm path. A four-file ruling must preserve writer integration as a named blocking unit and must not describe L4 as closed.

## 4. Unswept evidence

The following was not examined or established:

- Remote freshness was not independently established. A literal `git fetch origin impl/d117-u2-successor` was attempted but could not write the shared checkout’s `FETCH_HEAD` because Git metadata is mounted read-only. A read-only `git ls-remote` then failed because `github.com` could not be resolved. The local branch and cached `origin/impl/d117-u2-successor` both point to `399ffebd`; the remote-tracking reflog records an update by push at `2026-08-07 13:15:09 -0700`.
- No tests were run. The focused test source was inspected, but neither `tests.test_calibration_acceptance_successor` nor the canonical suite was executed.
- No live ledger, raw calibration custody, iCloud backup, evidence artifact, or quiet-machine/hardware behavior was examined.
- D-109, D-117, the full plan-freeze memo, RATIFICATION ruling 3, U1’s complete contract record, and U8’s readiness implementation were not substantively reviewed as governing sources. D-116’s supersession note expressly assigns current rule ownership to D-117; any ruling that depends on D-117 rather than the quoted D-102/D-116 text should defer on that missing authority.
- No independent numerical reference implementation, error-bound analysis, or cross-library Student-t comparison was examined for Q3.
- No crash injection, concurrent publisher test, Git-commit transition test, or recovery exercise was performed for Q8/Q9.
- No end-to-end consumer was traced that enforces Q11’s post-observation reuse condition beyond validating the successor’s lineage record.
- The live runbook’s copied-scalar site and U8 arm path were not changed by this exhibit.
- The working tree already contained unrelated user modifications. The quoted D-102 text is unchanged from `HEAD`; the quoted D-116 entry includes the current working-tree supersession note. No repository file was written by packet assembly.

A gate should return `DEFER` rather than assume facts from any unswept category on which its ruling depends.

## 5. Required gate return

For each question, return exactly one of:

- `RATIFY_AS_IMPLEMENTED`
- `OVERRULE — <replacement semantic>`
- `DEFER — <specific missing evidence or authority>`

The proposition to decide for each line is:

1. **Q1:** complete content-distinct valid same-epoch prefix through cutoff.
2. **Q2:** preflight screen = `max(observed maximum, 95% two-draw prediction)`, rounded half-even at `1e-15`.
3. **Q3:** `decimal_incomplete_beta_bisection_v1`, 80 Decimal digits, with explicit df=18 compatibility pins.
4. **Q4:** retain the pending boundary until reached/crossed, then set the next boundary to twice the newly issued corpus count.
5. **Q5:** persistent automatic-issuance refusal after a new systematic observation until an authority ruling.
6. **Q6:** refuse actual no-content observations; allow only explicitly unused U1 slots proven by terminal session abort.
7. **Q7:** v3 cutoff-named immutable artifacts, single-parent ancestry, all registered parent bytes present in the checkout.
8. **Q8:** committed registry as sole rotating trust anchor, exactly one active leaf, exact artifact hashes.
9. **Q9:** committed terminal head as input; immutable artifact first; registry replacement last as authority point.
10. **Q10:** permit the probe over the narrowly recognized governed open U1 extension; require terminal committed closure before building.
11. **Q11:** permit successor-era use of parent-judged evidence when explicit parent judgment is retained in lineage.
12. **Q12:** four-file probe exhibit with writer copied-scalar removal and U8 arm-path integration left as separately gated residuals.
