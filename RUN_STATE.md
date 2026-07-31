# JouleWise Run State

This file is the single running pointer for the project: the one doc to
read to get back here. Session records live in `docs/run_reports/` and
`docs/process_traces/`; deliberation lives in `docs/council_log.md`;
policy lives in `docs/decision_log.md`. The three dated restart docs
`docs/process_traces/RESUME-2026-07-26.md`, `RESUME-2026-07-27.md`, and
`RESUME-2026-07-28.md` are now point-in-time session records only — each
carries a superseded banner, and everything still current in them is
folded in below. Do not create another dated restart doc; update this
file instead.

Last updated: 2026-07-31 (contrast-window + D5-J merge session). **Main
is at the PR #89 merge `7ee680c`: the contrast window is COLLECTED AND
PASSED, and D5-J (the structural cooldown-join redesign) is MAINLINE
under the D-093 cold-gate synthesis.** Post-merge canonical suite
lead-run on main: `Ran 2286 tests`, `OK (skipped=12)`. See the CURRENT
STATE block below; the mint-era summary that follows remains accurate
for the mint arc itself.

**Main is at the PR #88
merge `da83337` (historical for this paragraph): mint #1 is MAINLINE.** The full mint arc (FIX-1..10
gauntlet, ratified mint contract, campaign configs, and the
`df-ph-decode-floor-mint1` artifact — absolute 3.592138 / comparative
7.377086 / operative gate 7.377086 J, validator clean lead-run) merged at
the audited head `16c7af0` under the D-088 conditioned license (cold gate
+ Opus contract refuter, unanimous). The 7B floor window
`window_7bfloor_20260729` is claim-bearing (verdict PASSED, floors
absolute 6.294380135190098 / comparative 13.998036715259254; the
absolute cell's member mean is 192.38623252628366 J over n=10 — the
comparative cell has its own, much smaller mean, so always name the cell
when quoting this). D-083..D-088 are in `docs/decision_log.md`.

**Standing conditions from D-088 (bind until COOLDOWN-JOIN-GAUNTLET-01
closes):** any claim consumption through the cooldown join carries a
recorded three-check bench scan (no unlicensed declared duplicates, no
zero-candidate declarations, no failed/incomplete-existing encounters);
no mint from a duplicate-bearing corpus (this includes any future 7B
mint). QA-10A/QA-10B remain registered blockers against the join
contract — re-scoped, corpus-unreachable today, not downgraded.
Session record: `docs/run_reports/2026-07-30-mint-merge-coldgate.md`.

## CURRENT STATE (2026-07-31 close-out; resume script below EXECUTED except step 7, in flight)

The 2026-07-30 19:15 resume script executed overnight, steps 1-6 and 8
complete, step 7 (metrology authoring) in flight at close-out:

1. **Contrast window `window_contrast_20260730`: COLLECTED, verdict
   PASSED.** 47 bundles (start/mid/end references + 40 ABBA science
   members, zero science failures), bracket drift 1.281 ms vs the
   10.818 ms screen, adapter continuity stable, backups verified.
   Recovery arc: start-triplet r1 failed CPU admission twice (XProtect
   Remediator sweep, directly observed at 941 CPU ms/s; round-1 TM
   attribution corrected on evidence); escalation trigger honored with a
   bounded Sol consult; round 3 ran clean end-to-end; supersession
   recorded ONCE (both failed occurrences superseded). Close-out:
   `~/JouleWise-window-custody/window_contrast_20260730/close-out.md`;
   report: `docs/run_reports/2026-07-31-contrast-window-collection.md`.
   Per-block contrast DIAGNOSTIC (prose, ungated): 7B−1.5B decode
   146.730349 J mean, σ 0.241 J, n=10 blocks. The gated claim rides
   MANIFEST-CONTRAST-01.
2. **D5-J MERGED via PR #89** (`aca78f8` + comment-only correction
   `707f76e`): the delta audit FAILED (blocker DA-1: malformed
   supersession records silently dropped pre-ambiguity — PRE-EXISTING on
   main, byte-identical filter; should-fix DA-2: commit-message test
   overcount), which per D-089's revisit clause went to a cold gate
   (fresh Fable + Opus refuter, split verdict) and the **D-093
   magistrate synthesis**: no behavior-changing fix round (DA-1 closes
   in the gauntlet at the validator/reader boundary — COOLDOWN-JOIN-DA1-01,
   intake table), merge at the corrected head, raw-vs-validated
   supersession-record scan added to EVERY claim consumption (initial:
   0-divergence across all four claim-bearing corpora).
3. **Bookkeeping landed** (`49c1876`, `0d0bd0b`): D-089..D-093,
   C-039 addendum II, paper outline archived, window run report,
   WINDOW_STATUS + PROJECT_STATUS refreshed (metrology framing, plain
   language), kernel latest_report/date refreshed.
4. **Metrology campaign suite** (paper claims C1-C5): spec ratified
   (lieutenant-authored, magistrate-ratified this session); Sol xhigh
   generation running at close-out on branch `impl/metrology-campaigns`
   (worktree minttool) — five campaigns (linearity_ramp, null_ladder,
   additivity_shapes, micro_delta k=64 draft-pending-slope, long_holds),
   plans emitted `draft_pending_magistrate_ratification`. If dead on
   resume: relaunch from the spec at scratchpad `metrology-suite-spec.md`
   (old session dir) + prompt `mt_prompt2.md` (current session dir).
5. NEXT (in order): harvest/commit the metrology generation (lead
   review, PR, D-072 gate); ratify the metrology window-A frozen plans;
   run metrology window A (~2.8 h: ramp + additivity + null o0512 +
   holds) next quiet night; MANIFEST-CONTRAST-01 desk work to unlock the
   contrast claim; QUEUE-RECONCILE-01 (P2-015 retirement + 7 stale
   dependents + DA-1 kernel promotion — roadmap page is AT its 30 kB
   shard budget, net additions need compensating retirement or a split).
6. **Ed owes**: network-time restore (`sudo systemsetup
   -setusingnetworktime on` — still OFF from §5A), wall-meter purchase
   (D-092, non-blocking).

Standing D-093 condition (adds to the D-088 block above): every claim
consumption through the cooldown join records the raw-vs-validated
supersession-record scan; any divergence refuses consumption.

## EXECUTED RESUME SCRIPT (2026-07-30 19:15 PT pre-window checkpoint; historical — fully executed, see CURRENT STATE)

Successor is FABLE, MAGISTRATE. THE CRITICAL PATH IS TONIGHT'S CONTRAST
WINDOW — launch it before anything else. The capstone PIVOTED today
(Rivoire-ratified): METROLOGY-CENTRIC paper; the instrument is the
product. Session ledger (all rulings/facts — READ IT FIRST):
/private/tmp/claude-501/-Users-edr-code-JouleWise/abec37a6-31cd-4c56-a8a8-9448acaf12be/scratchpad/magistrate-rulings-2026-07-29.md
Paper outline: same dir /paper-outline-v1.md. Sweep memos: /sweep-*.md.

WINDOW (do first, in order):
1. Ed's §5A is DONE: clock verified, Network Time OFF at 19:02:38 PT
   (record restore after window), charger 140W Apple (power-supply
   identity), machine cleared for the night, last HID 19:02. Ed is
   AWAY — do not wait on him.
2. QUIET-LOCK: a Sol session may still be authoring metrology campaigns
   (`ps aux | grep codex`; check the minttool worktree log for a
   metrology_v1 commit). If committed and exited: fine. If still
   running at launch time: kill the codex processes (authoring resumes
   post-window; the window outranks it). NO agents during measurement.
3. Prep: the chain hardcodes REPO=/Users/edr/code/JouleWise; main
   checkout is currently on `main` — DETACH at the branch head first:
   `git -C /Users/edr/code/JouleWise checkout --detach 16c7af0`
   (campaign configs live on impl/mint-tool). Then
   `bash scripts/quiet_mac_prep.sh`. Its "Graphics capability" FAIL is
   a known false signal on this build — the authoritative display check
   is `pmset -g log` showing "Display is turned off" with no later
   wake (ledger precedent).
4. LAUNCH (~21:00 PT, >=10 min after last local command),
   run_in_background, then ZERO tool calls until measurement_complete:
   caffeinate -is /bin/zsh /Users/edr/JouleWise-window-plans/window_contrast_20260730/window-chain.zsh /Users/edr/JouleWise-window-plans/window_contrast_20260730
   Chain sha 2a334f64… (verified, includes §5B screen). Frozen plan
   RATIFIED: splitwise-decode-v1-m3max-qwen25-1p5b-vs-7b, n=10 ABBA,
   arms 1.5B/8b403126 + 7B/c26a38f6, evidence-bearing-now /
   claim-bearing-later per pre-reg §5. ~2.6h. If a member fails CPU
   admission: quarantine, wait out the idle-daemon intruder, author a
   continuation chain reusing THIS window's pre-cal
   (window_7bfloor_20260729 precedent + §10; supersession recorder:
   run ONCE per member, absolute --runs-dir). A third failure of any
   signature closes the window as salvage (end triplet + post-cal
   only) per cold-gate precedent.
5. POST-WINDOW: §8 bracket check -> §9 whole-window verdict (absolute
   --runs-dir) -> backup_runs.sh -> close-out record (template:
   /Users/edr/JouleWise-window-custody/window_7bfloor_20260729/close-out.md;
   include the network-time-restore reminder for Ed). NO floor
   extraction (science window, not calibration): claim consumption is
   blocked on MANIFEST-CONTRAST desk work; the paper's demonstration
   numbers come from bundle summaries + the one minted floor artifact
   (1.5B, 7.377086 J) plus the 7B prose-only floors (13.998037 J,
   pending MINT-GENERALIZE-01).
6. OVERNIGHT (agents OK after measurement_complete): implement D5-J —
   the STRUCTURAL cooldown-join redesign (adopted design + the struck
   liberalization cell + implementation sketch ALL in the ledger).
   Sol xhigh, WRITE_SCOPE {joulewise/analysis_engine/inputs.py,
   joulewise/whole_window.py matcher contract,
   tests/test_analysis_integration.py}, one commit on impl/mint-tool
   in the minttool worktree
   (/private/tmp/claude-501/-Users-edr-code-JouleWise/9c166892-d763-42c4-8cf7-383912f054c9/scratchpad/minttool).
   Then a fresh INDEPENDENT read-only delta audit (prior auditor
   violated read-only and self-fixed — ledger process flags; emphasize
   REPORT ONLY), full suite, and the merge train resumes (PR, D-072
   gate). MERGE IS HELD until that audit passes (escalation-trigger
   ruling; FIX-10 audited FAIL on B1/B2 — adversarial-shaped, honest
   path verified clean 57/57).
7. THEN: metrology campaign suite (finish/ratify the authoring if Sol
   died mid-run; spec = paper-outline §5 + its campaign->claim map);
   metrology window A next night (linearity ramp + additivity + holds
   -> claims C1/C4/C5).
8. BOOKKEEPING BATCH owed: decision-log entries from the ledger
   (metrology pivot, D5-J adoption + struck cell, trigger firing,
   FIX-10 process flags, Q1-Q9 ratifications, wall meter YES pending
   hardware = P1-003 answered); council-log addendum; queue rows
   MANIFEST-CONTRAST-01, MINT-GENERALIZE-01, POWERMETRICS-AUDIT-01,
   SUPERSESSION-DUP-REFUSAL-01; sweep memos + paper outline into
   docs/run_reports/; kernel refresh + gen_state; consistency sweep.

Standing: gates never waived; magistrate operates windows solo; zero
agents during measurement; plain language on advisor surfaces; the
loop runs until the paper's claims table (outline §5) is measured.

## PRIOR STATE (2026-07-30 afternoon; the resume script below is EXECUTED except where struck)

Steps 2, 3, and 5 of the resume script below are DONE (audit harvested →
FAIL → FIX-10 → escalation → cold gate → D-088 → PR #88 merged
`da83337`; bookkeeping batch on main as `e1e0aec`+`d8b5d54`). Step 1
CLEARED: Ed confirmed network time is **On** (2026-07-30, pre-meeting).
The advisor brief is also LIVE as a private shareable web page (URL in
the external-artifacts-index memory; canonical copy stays
`docs/advisor_briefs/2026-07-30-advisor-brief.md`).
Step 4 (tonight's window per D-085 Q1: `qwen25_7b_decode_floor_v1`
already EXECUTED 07-29; the contrast window `splitwise_decode_v1` is the
one still pending) awaits Ed authorization + AC + settled machine;
frozen-plan + pre-reg ratification by the magistrate happens FIRST when
Ed green-lights. Step 6 (advisor answers → queue reorder) lands on Ed's
return from the ~14:30 meeting; the hardened brief is
`docs/advisor_briefs/2026-07-30-advisor-brief.md`. The kernel refresh is
DONE in the working tree (intake rows folded, STACK-ID-BIND-01 and
FLOOR-LABEL-01 retired to the completed table, `latest_report`
repointed); remaining bookkeeping owed: the consistency sweep's deferred
flags (`PROJECT_STATUS.md` advisor refresh, `WINDOW_STATUS.md` staleness)
and the skill-usage log.

## EXECUTED RESUME SCRIPT (2026-07-30 ~11:00 PT handoff checkpoint; historical)

Roles: successor session is FABLE, MAGISTRATE (rule 11 topology). Ed has
an ADVISOR MEETING (Rivoire) ~5h from checkpoint; brief at
/private/tmp/claude-501/-Users-edr-code-JouleWise/abec37a6-31cd-4c56-a8a8-9448acaf12be/scratchpad/advisor-brief-2026-07-30.md
— her answers to its four questions REORDER the queue (acceptance bar,
write-up scope, wall meter, claim priorities).

STATE (all pushed): branch impl/mint-tool @ 969a4d6 carries the FIX-6..9
series, campaign configs (splitwise_decode_v1 contrast +
qwen25_7b_decode_floor_v1), the campaign doc, and MINT #1 artifact
f188562 (df-ph-decode-floor-mint1.json at branch root, validator clean,
gate 7.377086). Main checkout back on main. WINDOW
window_7bfloor_20260729 COMPLETE and CLAIM-BEARING: verdict PASSED
(basis 3ff9128b…f1173), backup ok, governed extraction clean
(all_cells_extractable true) — 7B floors: absolute 6.294380135190098 /
comparative 13.998036715259254; member mean 192.38623252628366 J; close-out at
/Users/edr/JouleWise-window-custody/window_7bfloor_20260729/close-out.md.
Session ledger (ALL rulings: B3, Q1-Q9 ratifications, FIX-9 shape, cold
gates ×3, staged mint cmd):
/private/tmp/claude-501/-Users-edr-code-JouleWise/abec37a6-31cd-4c56-a8a8-9448acaf12be/scratchpad/magistrate-rulings-2026-07-29.md
(+ sweep memos sweep-{techniques,mechanisms,cv-paths}-2026-07-30.md and
related-work-sweep raw in the same dir — commit to docs/run_reports/ at
bookkeeping).

RESUME (in order):
1. VERIFY Ed restored network time (`sudo systemsetup -getusingnetworktime`
   via Ed → must be On) — instructed this morning, NOT confirmed.
2. Harvest the FIX-9+FIX-8 delta re-audit: a Sol xhigh read-only session
   over f188562^..969a4d6 was RUNNING at handoff (launched via a codex
   subagent; its out-file path unknown to this checkpoint). Look for
   fresh codex out-files/processes; if not recoverable in minutes,
   RELAUNCH the audit fresh (brief: ruled-shape compliance of the
   supersession-aware cooldown join; fail-closed edges; stubbed-reader
   test honesty; one-reader drift risk vs run_campaign private copy; no
   scope creep; mint-artifact data commit consistency). Consume verdict.
3. Merge train: on clean audit → PR for impl/mint-tool (base main; the
   series is FIX-1..9 + contract + campaigns + mint #1), D-072 full gate
   shape, merge. STACK-ID-BIND-01 (A50) closes on the real-bundle
   re-verify already done at 7f2c108+ — record it.
4. TONIGHT (if machine settled + AC + Ed authorizes): contrast window
   splitwise_decode_v1 (~2.6h) per campaign doc on the branch. Magistrate
   ratifies frozen plan + pre-reg FIRST (drafts in the doc; family ids
   ratified Q2-Q8, see ledger). Machine moved since last window → §5A
   (Ed, admin), fresh runs roots, new plan root
   (/Users/edr/JouleWise-window-plans/ template window_7bfloor_20260729 —
   REUSE the runbook-§6 chain extraction procedure incl. §5B screen;
   remember: --evaluation-basis-sha256 on extraction, --hash-bundles,
   absolute --runs-dir, supersession recorder appends silent dupes (run
   ONCE per member). XProtect/TM idle-daemon risk: provoke idle
   daemons pre-window; third-failure-closes rule was cold-gate-ratified
   precedent. Post-window: verdict → extraction → claims (exact
   evidence-root mappings, NO surplus) → the contrast claim needs
   MANIFEST-CONTRAST schema work (Blocker B, campaign doc §2) — claims
   ride AFTER that lands; collection tonight is still correct (evidence
   ages fine, pre-reg is in the plan).
5. BOOKKEEPING BATCH owed (one commit set to main): decision-log
   D-083.. (from ledger: B3 ruling; 7.377086 ratification recorded
   earlier; Q1-Q9; FIX-9 shape; cold-gate consults; third-failure rule),
   council-log C-039 addendum (gauntlet + cold gates + audit layers),
   queue rows: MINT-GENERALIZE-01, MANIFEST-CONTRAST-01,
   SUPERSESSION-DUP-REFUSAL-01 (recorder footgun), POWERMETRICS-AUDIT-01
   (counter-mechanics, citable), TOOL --runs-dir absolute-contract doc
   note, F2 mock-sampler, B2 SHA-pin, S2 exact-set, refusal-vocab
   ratification, MDE-adoption + min-window-rule + battery-crosscheck
   (from techniques sweep top-10), full-PDF reads of TokenPowerBench +
   2605.11999 pre-submission; WINDOW_STATUS stale disk line; kernel
   refresh + gen_state; sweep memos → docs/run_reports/; consistency
   sweep; skill-usage log.
6. Advisor meeting output: capture her four answers as the acceptance
   spec (P1-008/E1 row closes), reorder claim queue per Q4 answer.

Standing constraints intact: gates never waived; quiet-lock during
measurement; magistrate operates windows solo; lead never delegates
final verification; plain language on advisor surfaces.

Historical NEXT (superseded by the block above): (1) close the two
remaining suite errors on `impl/mint-tool` @ `1d83d68` — DONE via
FIX rounds 81193f5/c698711/FIX-5;
(2) full-tier adversarial review of `git diff
main...impl/mint-tool` (two accepted strict-direction interpretation
calls are settled, see the run report); fix rounds with delta re-audits;
(3) lead-reserved live gate — governed extraction for a10
(`--evaluation-basis-sha256 79c6e8b9…e053e`, ~20 min) and window C
(`0cf07a5c…8fa6`), then run the mint; pre-registration gate must pass
as-embedded and `validate_floor_artifact == []`; (4) PR + D-072 gate +
merge; (5) kernel refresh (STALE: stamped 2026-07-25, FLOOR-LABEL still
READY, no mint rows). Window B re-collection follows, under the D-079
pre-flight screen (still unimplemented). Full handoff:
`docs/run_reports/2026-07-28-floor-mint-implementation.md`. New queue
item TEST-SPEED-01 (suite consolidate/redesign, ~3-4 min recoverable,
zero deletions clear D-061; PR-fast/full split is Ed's call).

Prior head (historical, superseded by the block above): main was at
`c3e2647` on 2026-07-25 — PR #79's D-078 instrument repair merged on
2026-07-22, and PR #85's ratified SCREEN+BUDGET rules merged with green
CI after the four-round adversarial gauntlet. The repaired-instrument
collection contains 229 strict members across four bracketed windows
(a5-a8); those windows are non-claim-bearing diagnostic,
instrument-proving evidence and do not license a floor or research claim.
The merged rules screen gross and idle-subtracted energy separately, carry
a never-zero drift allowance for each family, require a fresh 24-hour
drift bound, reject fallback-clock members from floor/claim cells, derive
mockness from custody-bound config, and bar terminal mock evidence. The
capsule was redeployed from `c3e2647` as `dep_2I04CG6tQ4t0mzY7` at
2026-07-25T01:46Z.

Prior context (historical, pre-repair; superseded by the sign-off above):
PRs #77 and #78 are both MERGED (#78 at b52abf3). The recal windows of
2026-07-18/19 collected 94 + 266 strict-valid bundles under the
production environment guard (records:
`docs/run_reports/2026-07-19-d077-recal-window.md`,
`2026-07-19-recal456-extended-window.md`); that corpus is instrument
evidence only — the pre-repair floor re-extraction plan is VOID, and
P2-015 restarts under the repaired instrument per the roadmap.
Ed-side standing: `sudo pmset -c displaysleep 10`.

Prior arc (2026-07-17, SESSION ARC COMPLETE: Window A floors
published (222 strict-valid bundles; P2-015 partial pending P2-039
artifact + P2-037 adjudication); advisor brief delivered
(docs/advisor_briefs/); Ed DEPLOYED the README-first site + Learn
guide (PR #75); exploratory block measured (OLMoE ~229 J / Qwen3-4B
~362.8 J / 122B ~1072 J gross suite, n=3, exploratory-labeled);
DSpark/DFlash MLX feasibility CONFIRMED w/ per-round observability;
D-075 extension-axis intake folded. Session records:
docs/run_reports/2026-07-16-resumption-nohw-batch.md +
2026-07-17-window-a-floors.md.)

## Start Here For Every Big Run

Before starting substantial work:

1. Read this file.
2. Read `TASK_QUEUE.md`.
3. Read `AGENT_PLAN.md` (phase index) and the active phase's plan doc under
   `docs/phase_N/`; per-item status lives in the phase exit checklist
   (D-023).
4. Read `docs/planning_reflection_protocol.md`.
5. Check `docs/decision_log.md` before re-deciding anything; check
   `docs/risk_register.md` if starting a phase or a hardware-dependent task.
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
   After any session that changed front-facing state, refresh
   `docs/site/DRIFT.md` (site-drift report) instead of deploying:
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

Source of truth for work selection: [state kernel](docs/process/state_kernel.json) (updated 2026-07-31). Latest report: [Contrast window collected and PASSED (47 bundles, XProtect recovery per playbook); D5-J merged via PR #89 under the D-093 cold-gate synthesis](docs/run_reports/2026-07-31-contrast-window-collection.md).

### [ED-EXTERNAL]

- READY — E1 `P1-008`: Map phases to the academic calendar and capture the evaluator acceptance bar (minimum figures, demo expectation, reproducibility threshold, Mac-only plus split-deferral acceptability).

### [QUIET-MAC]

- READY — Q1 `P2-015`: Collect the first claim-grade Window A floors in one clean prospective quiet window per the claim-window run-book: mint the drift bound in-window, then run the start triplet, midpoint reference, and end triplet before the a8 re-verdict and Splitwise sizing.

### [AGENT]

- READY — A3 `FLOOR-BIND-01`: Bind canonical floor/MDE artifacts to governed extraction (CR9-1): authenticate admissible half-widths and complete campaign membership at claim consumption, with substitution/omission regressions.

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
| **7B floor** (`window_7bfloor_20260729`) | Qwen2.5 7B decode floor, collected 2026-07-29 | **PASSED** | CLAIM-BEARING; governed extraction clean (`all_cells_extractable` true). Floors: absolute 6.294380135190098 J, comparative 13.998036715259254 J; absolute-cell member mean 192.38623252628366 J (n=10). NOT yet minted — `MINT-GENERALIZE-01` is blocked by the D-088 no-mint-from-duplicate-bearing-corpus condition, so these figures live only in prose plus the out-of-repo custody extraction |
| **contrast** (`window_contrast_20260730`) | 40 contrast ABBA members + 7 references, 47 bundles, 1 supersession | **PASSED** | bracket drift 1.281 ms; contrast diagnostic 146.730349 J σ 0.241 (n=10 blocks) UNGATED — claim rides MANIFEST-CONTRAST-01 |

Window B's cause is established and is NOT a clock problem: a GPU DVFM
power ramp that the rectangular-pulse fiducial estimator aliases into an
apparent onset shift (93.28% of the drift; the wall-clock term moved the
OPPOSITE way, −0.201464 ms). D-079 clause 3 adds a pre-flight screen that
detects it in the ~4-minute pre-calibration, with cause-removal (never
outcome-selection) retry semantics.

**Corrected floor figures — the old ones must not be repeated.** a10's
**absolute** floors are **3.823787 J prefill / 3.592138 J decode**,
INCLUDING the 0.652272 J whole-window drift allowance. The 3.17 / 2.94 J
numbers circulated earlier are the attribution-width floors BEFORE the
allowance and are diagnostics only (D-079 clause 5).

**AMENDED BY D-084 (2026-07-29): `3.592138` is the ABSOLUTE COMPONENT IN
ISOLATION, not the operative decode floor.** Mint #1's cell composes
a10's absolute 3.592138 J with window C's comparative 7.377086 J, and
under W3 rule 8 the cell gate is the **max, never the sum** — so the
canonical **operative decode floor is 7.377086 J**, and that is the hard
six-decimal literal pinned in `scripts/mint_floor_artifact.py`. D-079
clause 5's "3.592138" pin predates window C's comparative extraction and
is superseded for the operative figure; both components remain published
and LABELLED per D-078 clause 11.

### The critical path: build the mint (HISTORICAL — CLOSED 2026-07-30)

All four blockers below are closed and this section is retained as
chronology only: `scripts/mint_floor_artifact.py` is the non-test call
site (1), the 30-vs-37 basis question RESOLVED (2), `production_window`
is in `_CALIBRATION_SCOPES` (3), and `impl/floor-mint` merged via PR #87
(4). Mint #1 merged via PR #88 at `da83337`.

`build_floor_cell` / `build_floor_artifact` / `build_absolute_record` /
`build_comparative_record` in `joulewise/detection_floor.py` have zero
non-test call sites; `scripts/extract_detection_floors.py` writes an
extraction report and stops. Established blockers:

1. **`claim_ready` requires an absolute AND a comparative record in the
   SAME cell**, so a10 alone mints a structurally `smoke_only` artifact.
   Mint #1 must pair a10's absolute cell with window C's decode
   comparative. Verifying that the two share backend, metric,
   `window_class`, condition family, and stack identity is a GO/NO-GO,
   not a task.
2. **A 30-vs-37 member authentication mismatch:** the a10 phase spec
   selects 30 members; the passed verdict authenticates 37. Extraction of
   the authenticated basis takes **20 min 36 s** on real data — budget
   for it.
3. **Windows C and D have no legal `calibration_scope`.**
   `_CALIBRATION_SCOPES` is `("window_a", "window_b_revalidation",
   "smoke")`. D-079 clause 4 adopts one general production name; proposed
   literal `production_window`.
4. **Pre-mint schema hardening was then written but unmerged** (it
   merged via PR #87; the branch is on main): branch
   `impl/floor-mint` @ `617060a` (pushed) makes the extraction report
   export the admissible half-widths it already computes, and moves
   `_WIDENED_FLOOR_KEYS` from optional into the required key sets so
   width ABSENCE is a schema error rather than a silent fall-back to the
   point-only floor. Suite 2198 OK.

### Disk

**EXECUTED 2026-07-28 (Ed-authorized 2026-07-27: iCloud-only acceptable,
delete after verified upload — resolving both open disk questions).**
Disk now has **115 GB free** (was 33 GB; ~61 GB freed by the repo prune described below, the rest by unrelated local housekeeping). The selective-prune plan was
generalized to every runs corpus: all 27 corpora are archived in
`~/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/` with a
per-corpus `MANIFEST.sha256`. Verification before any deletion: APFS-clone
name+byte parity; `brctl evict` of 100% of files (evict success = upload
complete); rematerialize-and-rehash of 20,028 files from iCloud (100% of
small evidence files + sampled traces) against the manifests — 0
mismatches. Then 1,848 `powermetrics*.plist` traces ≈ 61 GB were deleted
locally; **every small evidence file remains resident**, each pruned dir
carries `PRUNED.md` + `MANIFEST.sha256`. Restoring any trace =
`brctl download` its path under the archive.

Kept fully local (no deletion): `runs_window_a10_20260725(+_bound)` and
`runs_window_c_20260726(+_bound)` (mint #1 inputs),
`runs_window_a5_quarantine` (quarantine is evidence), and in `runs/` the
six frozen acceptance-gate bundles (`example-mac-mlx-*`) + `experiments/`
custody — the retained-corpus strict gate re-ran green post-prune (3/3,
incl. six-bundle strict validation), and keep-list file counts verified
unchanged.

### Orchestration

Global `CLAUDE.md` hard rule 11 now defines the topology: Fable as
MAGISTRATE and Ed's direct, Opus 5 as LIEUTENANT / operational chief, a
cold-Fable-instance gate with mandatory (not discretionary) triggers, and
an enumerated forbidden-to-decide-alone list for the lieutenant. D-080's
standing fresh-eyes sweep is the first exercise of that list.

### What needs Ed

1. RESOLVED 2026-07-27/28: Ed answered both disk questions (iCloud-only
   acceptable; delete after verified upload) and the archive+prune
   executed — see "Disk" above. Note the traces are now iCloud-only
   (single durable copy); flag if a second physical copy is wanted.
2. **AC power** for measurement windows — the production policy requires
   it and the machine was on battery.
3. A magistrate ruling on a conflict between D-080 and D-061: D-080's
   anti-ritual clause 4(ii) evaluates a rotating lens against the
   two-zero-sessions drop rule, which D-061 explicitly superseded with an
   expected-loss adjudication ("three applicable exposures TRIGGER an
   expected-loss review decision, never automatic deletion").
4. `FLOOR-WORKLOAD-SIZING-01` — resizing floors resizes the science, so
   it is a pre-registration change and therefore Ed's call.
5. Window B's disposition.
6. (2026-07-28 late) Multi-session coordination: a concurrent session
   force-rewrote main history (no content lost this time, but the mode
   can silently drop peer commits). Whether to adopt a
   no-force-push/branch-only convention is Ed's call.
7. (2026-07-28 late) TEST-SPEED-01's structural lever — a PR-fast/full
   CI split — is a CI-contract change and Ed's call; the
   consolidate/redesign work (~3-4 min, no deletions) needs no ruling.

Records: `docs/run_reports/2026-07-30-mint-merge-coldgate.md` (freshest
session record), `docs/process_traces/RESUME-2026-07-28.md` (superseded
as a pointer), `RESUME-2026-07-27.md`,
`RESUME-2026-07-26.md`, `docs/process_traces/2026-07-26-prereg-clock-mitigation.md`,
`docs/run_reports/2026-07-23-window-a-collection-arc.md`, and
`docs/run_reports/2026-07-24-screen-budget-gauntlet.md`.

**Historical (2026-07-25, superseded by the block above):** main
`c3e2647` contained the merged instrument repair (PR #79) and the merged
SCREEN+BUDGET rules (PR #85); the 229-member a5-a8 collection is
non-claim-bearing diagnostic, instrument-proving evidence, and the next
claim attempt was then framed as one clean prospective quiet window per
`docs/phase_2/window_runbook.md`.

The D-078 Phase-0 instrument repair was signed off and merged through
PR #79 on 2026-07-22. Registered limitation L1 remains owned by
FLOOR-BIND-01; it does not reopen the completed repair. Record:
`docs/run_reports/2026-07-20-p0-instrument-repair.md`. Earlier arcs below
are historical.

**C-028 CLOSED (2026-07-11): the full hardening + analysis-engine arc is
on main.** Reducer lattice 0.4.2 (inter-token metric) / 0.4.1 (idle ESS,
HAC variance — local r1's 47x underestimate closed) / 0.4.0 (verdict
split + window_evidence_precheck) with frozen legacy arms; the analysis
trio complete (P2-042 manifest → P2-041 verdict split → P2-037
contrast/claim engine with unwaivable cleanup claim gating per the
two-layer waiver reconciliation); doctor preflight; publication privacy
pack (fail-closed inventory); packaging CI; primary-verified related
work; load-transition prep (B remains [QUIET-MAC]). Window A's software
gates are ALL satisfied; execution needs a quiet machine + Ed.

PRs #41-#60 form the landed C-028 arc, all merged 2026-07-11 (incl. the
#59 integration-review fixes and the #60 DOC-008 kernel refresh); none
implies live evidence. P0-003 is satisfied
by the verified iCloud backup/restore. All NVIDIA/Orin protocol pins remain
PROVISIONAL pending P1-006 live evidence.

**Historical restart snapshot (recorded 2026-07-13; non-operative).** The
numbered sequence below is retained as dated handoff narrative, not current
work-selection authority. Use the generated region above for selection.
1. DONE 2026-07-13: #61-#63 merged at delta-audited heads; site deployed
   live under the cap; XSI-1 CI hardening green on main; bridge landed
   and lead-verified (8/8 protocol checks; suite 1318 OK).
2. [ED + AGENT] **Comprehensive whole-project audit (declared gate).**
   The audit method proposal is with Ed; no further feature work, queue
   pulls, or campaign prep until the audit runs and its findings are
   adjudicated. Audit focus per Ed: overproduction (excess code/tests),
   plus everything a serious external review would check.
3. [QUIET-MAC + ED] After the audit: Window A — C-019 production-shaped
   shakedown and P2-015-SMOKE, then P2-015 floors and P2-006 baselines.
   Do not run this lane while an agent session is active.
4. [AGENT] Post-audit, outside a quiet window: P2-050 adjudication,
   SITE-02 follow-ups, P2-027 publication prep. P2-022/P2-023 remain
   blocked until the 2M corpus exists.

## Session History (pointers only — run reports own the narrative)

Parenthetical states below are historical at each report's head; they are not
current restart instructions. Current state is the CURRENT STATE block at
the top of this file.

- 2026-07-31 contrast-window collection (`window_contrast_20260730`
  PASSED, 47 bundles) + D5-J merge via PR #89 under the D-093 cold-gate
  synthesis: `docs/run_reports/2026-07-31-contrast-window-collection.md`
- 2026-07-30 paper outline v1 archived (metrology-centric framing,
  D-091): `docs/run_reports/2026-07-30-paper-outline-v1.md`
- 2026-07-30 audit harvest → FIX-10 → escalation → cold gate (D-088) →
  PR #88 merge `da83337` (mint #1 mainline) + advisor-brief hardening:
  `docs/run_reports/2026-07-30-mint-merge-coldgate.md`
- 2026-07-30 D-080 fresh-eyes sweep memos (techniques, mechanisms,
  CV paths): `docs/run_reports/2026-07-30-sweep-techniques.md`,
  `2026-07-30-sweep-mechanisms.md`, `2026-07-30-sweep-cv-paths.md`
- 2026-07-29 modularity survey (MODULARITY-01 intake; STACK-ID-BIND-01
  claim-binding defect CONFIRMED):
  `docs/run_reports/2026-07-29-modularity-survey.md`
- 2026-07-28 (late) mint-implementation session: PR #87 hardening merged;
  mint tool built on `impl/mint-tool` (unmerged, review owed); parser
  fix D-081; pairing GO + 30-vs-37 resolved; suite-pruning consult
  (TEST-SPEED-01): `docs/run_reports/2026-07-28-floor-mint-implementation.md`
- 2026-07-28 iCloud archive + verified selective prune of all runs
  corpora (61 GB freed; keep-list intact; strict corpus gate green):
  `docs/run_reports/2026-07-28-icloud-archive-prune.md`
- 2026-07-27 evening session record (windows C/D passed; the mint is the
  critical path; D-079/D-080): `docs/process_traces/RESUME-2026-07-28.md`
  (superseded as a pointer by this file)
- 2026-07-26 evening session record (window B failed on calibration
  bracket drift; FLOOR-LABEL gauntlet parked):
  `docs/process_traces/RESUME-2026-07-27.md` (superseded as a pointer)
- 2026-07-26 session record (FLOOR-LABEL-01 in gauntlet; windows B/C/D
  planned): `docs/process_traces/RESUME-2026-07-26.md` (superseded as a
  pointer)
- 2026-07-26 pre-registered clock-pin mitigation and its outcome:
  `docs/process_traces/2026-07-26-prereg-clock-mitigation.md`
- 2026-07-18 Claude Code script bridge + native pet integration:
  `docs/run_reports/2026-07-18-claude-codex-pet-observer.md`
- 2026-07-13 Bridge v1: bridge-protocol/v1 contract + scripts/bridge tooling
  (PR #64; co-designed with Sol over the bridge itself):
  `docs/run_reports/2026-07-13-bridge-v1.md`
- 2026-07-13 Restart close: #61-#63 merged at delta-audited heads
  (DRA-001 fixed; XSI-1 CI hardening), site live under cap; audit gate
  declared: `docs/run_reports/2026-07-13-restart-merge-deploy.md`
- 2026-07-12 Claude↔Sol bidirectional bridge (concurrent Ed-directed
  thread; lead-verified 2026-07-13):
  `docs/run_reports/2026-07-12-claude-sol-bridge.md`
- 2026-07-12 Agent-lane triple: SITE-01/P2-049/P2-028 → PRs #61-#63 at
  lead-gated heads; delta re-audits owed pre-merge on #62/#63:
  `docs/run_reports/2026-07-12-agent-lane-triple.md`
- 2026-07-11 P2-041 vetted rebuild (uncommitted; lead pathspec review and
  commit pending): `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`

- 2026-07-10 NV-GATE-2 idle-capture regression debug/fix (uncommitted;
  localhost re-verification remains lead-gated):
  `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`
- 2026-07-10 NV-GATE-2 CODE-NOW implementation (NV-1/NV-3/NV-4/NV-5;
  live promotion evidence still gated):
  `docs/run_reports/2026-07-10-nvgate2-codenow.md`
- 2026-07-10 NV-GATE-2 accepted-findings fix round (uncommitted; merge
  metadata recreation and lead gate pending):
  `docs/run_reports/2026-07-10-nvgate2-fix-round.md`
- 2026-07-10 P2-038 accepted-findings fix round (all FIX-1..FIX-6 green;
  content-merged `origin/main`, Git merge metadata sandbox-blocked):
  `docs/run_reports/2026-07-10-p2038-fix-round.md`
- 2026-07-10 P2-038 production uncertainty software path (live quiet-machine
  closure still open):
  `docs/run_reports/2026-07-10-p2038-production-uncertainty.md`
- 2026-07-10 P2-040 reducer-version compatibility review fix (uncommitted):
  `docs/run_reports/2026-07-10-p2040-versioning-fix.md`
- 2026-07-10 P2-040 remainder implementation (uncommitted, pending lead
  pathspec commit/corpus gate):
  `docs/run_reports/2026-07-10-p2040-remainder.md`
- 2026-07-10 P2-040 / RETRO-001 fix round (committed on c027-int-p2040
  after lead review): `docs/run_reports/2026-07-10-p2040-fix-round.md`
- 2026-07-09 C-027 whole-project council review (7 gpt-5.6-sol lenses +
  counterreview + independent final examiner):
  `docs/reviews/2026-07-09-c027-whole-project-review.md` (compact run
  report: `docs/run_reports/2026-07-09-c027-council-review.md`)
- 2026-07-09 Claude Code → Codex MCP bridge hardening and live smoke:
  `docs/run_reports/2026-07-09-claude-codex-mcp-bridge.md`
- 2026-07-12 adaptive Claude Code ↔ Sol/Fable bridge follow-up:
  `docs/run_reports/2026-07-12-claude-sol-bridge.md`
- 2026-07-09 P2-034 broad campaign packs (C-026; PR #39):
  `docs/run_reports/2026-07-09-p2034-broad-packs.md`
- 2026-07-09 spec-fleshing wave 2, ultracode (C-025; PRs #33..#38;
  D-056..D-059): `docs/run_reports/2026-07-09-spec-fleshing-wave2.md`
- 2026-07-09 spec-fleshing wave 1 (C-024; PRs #29..#32; D-052..D-055):
  `docs/run_reports/2026-07-09-spec-fleshing-wave1.md`
- 2026-07-09 scientific-rigor review of suite/benchmark/question bank
  (C-023; review-only; full record in
  `docs/reviews/2026-07-09-scientific-rigor-review.md`):
  `docs/run_reports/2026-07-09-scientific-rigor-review.md`
- 2026-07-09 CP-5 resume: pre-campaign review completed, stop card
  cleared, PRs #22..#28 merged, Window-A GO
  (C-022): `docs/run_reports/2026-07-09-cp5-resume.md`
- 2026-07-09 meta-process stop-card + codex-bridge audit cleanup
  (D-050; CP-5 preserved untouched):
  `docs/run_reports/2026-07-09-meta-process-stop-card-cleanup.md`
- 2026-07-09 advisor status-site live-depth refresh (D-051/C-021;
  subordinate to the then-active CP-5 stop card):
  `docs/run_reports/2026-07-09-advisor-status-site.md`
- 2026-07-08 suite build (C-017; adjudication + PRs #17/#18/#20/#19;
  D-044..D-047): `docs/run_reports/2026-07-08-suite-build.md`
- 2026-07-08 suite-science + expansion (C-014/C-015; PRs #14/#15/#16;
  D-038..D-042): `docs/run_reports/2026-07-08-suite-science-expansion.md`
- 2026-07-08 Lakebed deploy (C-013):
  `docs/run_reports/2026-07-08-lakebed-deploy.md`
- 2026-07-08 site observatory (PR #13):
  `docs/run_reports/2026-07-08-site-observatory.md`
- 2026-07-08 critique second-pass + councils+critique (C-011 → PR #12):
  `docs/run_reports/2026-07-08-councils-critique-session.md`
- 2026-07-07/08 resume+merge (C-009 first full run; PRs #8..#11):
  `docs/run_reports/2026-07-07-resume-merge-session.md`
- Older: see `docs/run_reports/` (dated files).

## Current Verification

- **Merged main `7ee680c` (2026-07-31, current): canonical `Ran 2286
  tests`, `OK (skipped=12)`, lead-run post-merge.** This is the PR #89
  (D5-J) merge; the close-out commits `49c1876`, `0d0bd0b`, `6ed1625`
  sit atop it and are docs/kernel only.
- **Merged main `da83337` (2026-07-30, historical): canonical `Ran 2280
  tests`, `OK (skipped=12)`, lead-run post-merge.** Branch head
  `16c7af0` pre-merge: lead-run `2280 OK (skipped=21)` (worktree
  convention); Sol-side `2280 OK (skipped=24)` (delegated sandbox). CI
  green on merge ref `ff0dda5` (build, installed-wheel, release-chain,
  test 3.11 + 3.14; two earlier red runs were stale-merge-ref artifacts,
  see the session report). Mint #1 `validate_floor_artifact == []`
  lead-run. Fail-open-shape corpus scans clean ×3 (magistrate, cold
  instance, refuter) across a10, window C, and the 7B window.
- **Post-prune suite on `7337b33` + docs edits (2026-07-28, lead-run):**
  `Ran 2194 tests`, `FAILED (errors=2, skipped=12)`. The two errors are
  `test_build_site_parsers` Lakebed-budget tests and are **pre-existing
  at HEAD, independent of the prune**: `32e510a` rewrote Session History
  with `docs/process_traces/` pointers, but `scripts/build_site.py
  parse_session_history` requires a backticked `docs/run_reports/...md`
  pointer in each dated bullet (verified by running the parser directly
  on the pristine HEAD file — same failure). The affected surface for the
  prune itself, `tests.test_corpus_strict_validation`, is 3/3 OK
  post-prune. RESOLVED by `cb867f3` (Ed-authored): the parser accepts
  `docs/process_traces/` Session History pointers per the
  pointer-retirement convention; `tests.test_build_site_parsers` 21/21 OK
  on that head, clearing both errors.
- **Merged main `7337b33` (2026-07-27, historical):** `FLOOR-LABEL-01`
  merged at `3055315` under the D-072 gate shape (independent Opus
  contract lens returning "comparative coverage COMPLETE" plus a fresh
  Sol xhigh audit, fix rounds each delta-re-audited, five independently
  audited correctness fixes); lead-verified suite **2194 OK** on merged
  main. Branch `impl/floor-mint` @ `617060a` (unmerged at that date;
  merged via PR #87 on 2026-07-28) records
  suite **2198 OK (skipped=24)** from that 2194 baseline plus four
  regressions. Window C's bracket drift (1.279 ms) and window D's
  (0.484 ms) reproduce from the stored `instrument_evidence.json`
  fiducial bounds in `runs_window_c_20260726/instrument_validation/` and
  `runs_window_d_20260726/instrument_validation/`.
- **Merged main `c3e2647` / PR #85 (2026-07-25, historical):** the
  SCREEN+BUDGET implementation completed four adversarial audit rounds.
  Final PR-head CI was green on all five checks (`build`,
  `installed-wheel`, `release-chain`, `test (3.11)`, `test (3.14)`).
  The final lead-side suite recorded 2141 passed / 21 skipped; its one
  battery-timing flake passed on rerun. The capsule was redeployed as
  `dep_2I04CG6tQ4t0mzY7` at 2026-07-25T01:46Z.
- **D-078 repair sign-off gate (2026-07-22, historical merged gate):**
  branch
  `impl/p0-instrument-repair` code/test head `040ca3a` (docs-only
  close-out `debc6d2` carries it unchanged; merged through PR #79):
  lead-run
  `pytest -q tests/` = **2088 passed, 15 skipped, 1570 subtests, 0
  failures**; round-9 focused review surface 357 passed at the same
  head. Entries below are historical.
- PR #65 branch `impl/bridge-v1.1` final head `8b96bd4`: canonical
  `Ran 1387 tests`, `OK (skipped=10)`, lead-run 2026-07-13 (four
  lead-side full-suite runs across the fix arc: 1371→1381→1385→1387);
  CI green on the final head (build, installed-wheel, tests 3.11 +
  3.14); `scripts/check-codex-mcp.mjs` 5/5 PASS with the v1.1 adapter;
  live session-open/close and reverse-consult probes recorded in
  `docs/run_reports/2026-07-13-bridge-v11.md`.
- Merged main `d285989` (post #65): canonical `Ran 1387 tests`, `OK
  (skipped=10)`, lead-run 2026-07-13 on the merged head;
  `scripts/check-codex-mcp.mjs` all PASS; no active workspace leases.
- Previous session (post #61-#63 merges + bridge v1 landing, pre-commit
  head `99b8640`): canonical `Ran 1318 tests in 111.017s`, `OK
  (skipped=10)`, lead-run 2026-07-13; bridge protocol checker 8/8 PASS;
  bridge focused tests 4/4 OK. Merged-main backstop at `12131b0` was
  `Ran 1314 tests`, `OK (skipped=10)`. Live capsule: measured artifact
  854,349 B deployed, routes 5/5 HTTP 200, freshness 14/14 current at
  `7d3ea57`.
- Prior head `main@194ea39` (post #59 + #60 merges): canonical `Ran 1258
  tests`, `OK (skipped=10)`, lead-run 2026-07-11 fresh-thread intake.
  PRs #41-#60 are all merged.
- Prior head `main@cc3afc3`: canonical `Ran 1220 tests`, `OK (skipped=10)`;
  retained corpus strict gate 6/6; PR #59 pre-merge lead replay was
  `Ran 1224 tests`, `OK (skipped=12)`.
- Count convention for C-028 records (SUPERSEDED — historical, applies
  only to the 2026-07-11-era tails above): ordinary worktree replays
  report `skipped=12`, final main reports `skipped=10`, and restricted
  managed sandboxes may report `skipped=13` when their environment-gated
  probe is unavailable. The CURRENT convention is the triple at the top
  of this section: main `skipped=12`, worktree `skipped=21`, delegated
  Sol sandbox `skipped=24`. Preserve those environment labels when citing
  a tail.

### Historical verification archive (exact at the recorded heads)

- P2-041 vetted rebuild: baseline canonical `Ran 1041 tests in 67.995s`,
  `OK (skipped=13)`; final focused recipe modules `Ran 398 tests in 54.964s`,
  `OK (skipped=1)`; final canonical `Ran 1062 tests in 76.436s`, `OK
  (skipped=13)`; `git diff --check` and the dead-private-helper search clean.
  The retained corpus and localhost socket gates skipped loudly; no live or
  quiet-Mac validation was claimed. Report:
  `docs/run_reports/2026-07-11-p2041-vetted-rebuild.md`.

- PR #49 P2-038 rail-only flake: pre-fix exact-test loop failed 4/100;
  retained failure emitted `cadence_ratio_unrecorded` plus
  `interpolation_bound_unrecorded` because the final trace sample preceded the
  stop marker. Archived `origin/main` reproduced on iteration 6. The
  fixture-only terminal-sample handshake fix passed the exact test 100/100,
  focused module `Ran 5 tests in 30.480s`, `OK`, and canonical suite
  `Ran 1041 tests in 66.509s`, `OK (skipped=13)`. Report:
  `docs/run_reports/2026-07-10-pr49-p2038-flake-root-cause.md`.
- NV-GATE-2 idle-capture regression fix: historic fake-sampler plus new
  delayed-readiness regression passed together in 3 consecutive fresh
  processes; canonical suite `Ran 1023 tests in 35.164s`, `OK (skipped=13)`;
  `py_compile` and `git diff --check` clean. The exact localhost contract was
  attempted 3 times but loudly skipped before worker execution because this
  sandbox denied socket bind; lead socket-capable 3x rerun remains required.
  Report: `docs/run_reports/2026-07-10-nvgate2-idle-capture-fix.md`.
- NV-GATE-2 accepted-findings fix round: focused node-worker/subprocess,
  controller, reducer, strict-dispatch, and schema surface `Ran 229 tests in
  4.995s`, `OK (skipped=2)`; the historic fake-sampler test passed three
  consecutive fresh-process runs; canonical suite `Ran 1022 tests in 34.406s`,
  `OK (skipped=13)`; targeted `py_compile` and `git diff --check` clean. The
  0.3.1 dispatch came from `origin/impl/p2040-remainder` because post-main did
  not contain it. Report: `docs/run_reports/2026-07-10-nvgate2-fix-round.md`.
- NV-GATE-2 CODE-NOW worktree: baseline `Ran 910 tests in 32.549s`,
  `OK (skipped=12)`; final canonical suite `Ran 922 tests in 33.551s`,
  `OK (skipped=13)`; focused NV-1/NV-3/NV-4/NV-5 surface `Ran 232 tests
  in 6.085s`, `OK (skipped=2)`; `git diff --check` and targeted
  `py_compile` clean. The added skip is loud and specific: this managed
  sandbox denied localhost socket bind for NV-5. No live NVIDIA evidence or
  de-provisionalization was claimed.
- P2-038 accepted-findings fix round: all FIX-1..FIX-6 complete; focused
  `Ran 70 tests in 41.211s`, `OK`; canonical `Ran 992 tests in 68.140s`,
  `OK (skipped=12)`; `git diff --check` clean. The real-child rail-only path
  now withholds drift on unknown contamination while gross remains eligible;
  P2-039's pending guard validator accepts the emitted block; backup launch
  failure, extreme-sentinel exclusion, child invocation, and literal phase
  constants are regression-tested. The absent worktree `runs/` corpus produced
  the loud six-bundle acceptance-gate skip. Git merge metadata remains absent
  because the managed sandbox cannot write the external worktree admin dir;
  the exact clean three-way `origin/main` content snapshot is applied.
- P2-040 reducer-version review fix: focused strict/reducer run
  `Ran 84 tests in 1.908s`, `OK`; extended strict/reducer/schema run
  `Ran 104 tests in 1.997s`, `OK (skipped=1)`. Canonical run reached
  `Ran 926 tests in 33.732s`, `FAILED (failures=1, skipped=12)` solely at
  pre-existing `test_telemetry_measure_idle_with_fake_nvidia_smi`; isolated
  reruns reproduce its 0.2-second fake-process timing failure. All
  reducer/version tests pass; no out-of-scope node-worker change was made.
- P2-040 remainder worktree: pre-change baseline `Ran 910 tests in 34.584s`,
  `OK (skipped=12)`; post-change focused affected modules `Ran 256 tests in
  3.744s`, `OK (skipped=1)`; canonical `Ran 924 tests in 32.812s`, `OK
  (skipped=12)`; compileall and `git diff --check` clean. The unchanged
  six-corpus test produced its required loud skip because `runs/` is absent;
  lead 6/6 strict read-only rerun remains the landing gate.
- P2-042 emitter branch `impl/p2042` (lead-committed base; draft PR #46;
  targeted-review fix round complete in the worktree, no fix-round commit):
  FIX-1 fail-closed typed identity/linkage validation, FIX-2 semantic
  `run_id` derivation, and FIX-3 raw-byte AP hashing/LF config emission are
  implemented. Focused manifest/generator/campaign checks: `Ran 82 tests in
  12.317s, OK`; final canonical suite: `Ran 989 tests in 33.405s, OK
  (skipped=12)`. Review regressions cover `run_id=[]`, one malformed identity
  at each manifest object layer, a fully rehashed coherent rename, and a CRLF
  AP fixture. Report:
  `docs/run_reports/2026-07-10-p2042-analysis-manifest.md`.
- P2-040 reducer-version review fix: focused strict/reducer run
  `Ran 84 tests in 1.908s`, `OK`; extended strict/reducer/schema run
  `Ran 104 tests in 1.997s`, `OK (skipped=1)`. Canonical run reached
  `Ran 926 tests in 33.732s`, `FAILED (failures=1, skipped=12)` solely at
  pre-existing `test_telemetry_measure_idle_with_fake_nvidia_smi`; isolated
  reruns reproduce its 0.2-second fake-process timing failure. All
  reducer/version tests pass; no out-of-scope node-worker change was made.
- P2-040 remainder worktree: pre-change baseline `Ran 910 tests in 34.584s`,
  `OK (skipped=12)`; post-change focused affected modules `Ran 256 tests in
  3.744s`, `OK (skipped=1)`; canonical `Ran 924 tests in 32.812s`, `OK
  (skipped=12)`; compileall and `git diff --check` clean. The unchanged
  six-corpus test produced its required loud skip because `runs/` is absent;
  lead 6/6 strict read-only rerun remains the landing gate.
- P2-040 / RETRO-001 fix-round worktree: canonical suite `Ran 908 tests in
  32.723s`, `OK (skipped=11)`; focused 211 tests OK; claims lint exit 0 with
  no errors; `git diff --check` clean. The absent `runs/` corpus produced the
  required loud six-bundle acceptance-gate skip; the lead corpus gate then
  PASSED (6/6 strict via corpus symlink), plus mock e2e run+strict+reduce
  and the post-merge full suite (OK, skipped=12).
- Claude Code 2.1.207, Codex CLI 0.144.0, and Node 23.7.0 pass the
  bidirectional protocol checker. Claude → Sol now uses `gpt-5.6-sol` with
  `high` fallback/default and task-triggered xhigh/ultra escalation; the
  final guarded `/codex` smoke returned `JOULEWISE_SOL_HIGH_GUARDED_OK`
  (thread `019f5a2a-2f4a-7b33-8a6d-b44dcc5a7a26`) with source `mcp`, effort
  `high`, read-only sandbox, and `on-request` approvals. Claude-originated
  Sol sessions disable the reverse server. Top-level Sol → Fable uses the
  sole `consult_fable` MCP tool; live token `JOULEWISE_FABLE_MCP_OK` on
  thread `019f5a26-d8a6-7993-b48d-8131d88748b9`. Focused bridge tests pass
  4/4 and `gen_state.py --check` passes. The current full suite ran 1,317
  tests but is not green: one failure + one error in `test_gen_state` are
  caused by the concurrent uncommitted state-kernel removal of `P2-028`
  while the existing fidelity tests still require that ID; bridge tests are
  unaffected. Full details: `docs/run_reports/2026-07-12-claude-sol-bridge.md`.
- Last code-bearing verified head c095c83 (post PR #39; note: 36d5641
  later changed `scripts/build_site.py` on main without a recorded
  verification — flagged by C-027, covered by RETRO-001): suite `OK (skipped=10)` and
  repo lint errors=0, lead-run; pack lint errors=0 warnings=0.
- Prior: main after wave-2 integration fixes: `python3 -m unittest discover -s
  tests` → `Ran 877 tests, OK (skipped=10)`, lead-run; repo lint
  errors=0; CI green on all six PR heads (#33..#38); combined-ref
  pre-merge suite check green; live rotated mock campaign strict-valid
  with order provenance (lead-validated); mock e2e emits uncertainty
  fields per D-057.
- Prior: series head f75134d (post PRs #29..#32; docs-only) lead-verified;
  integration-fix commit 7156295 is also docs-only (no test surface):
  `python3 -m unittest discover -s tests` → `Ran 822 tests, OK
  (skipped=10)`, lead-run; CI green on all four PR heads (py3.11+py3.14);
  integration reviewer independently re-ran the suite and recomputed the
  detection-floor campaign arithmetic.
- Prior verification (7666652, post PRs #22..#28): `Ran 822 tests, OK
  (skipped=10)`, lead-run.
- Live lead gates this session (real MLX, Qwen2.5-1.5B via `.venv`, mock
  telemetry): single-prompt + TWO full 48-item jw_mixed suite runs
  (pre-merge old manifests, then final merged main with the REGENERATED
  manifests) — all strict-valid; 48/48 hash-domain closures on the
  real tokenizer; output token ids, model artifact hash, pinned sampler,
  and package versions verified present in the bundles.
- Envelope gate live: honest `envelope_failed[E1]` on the mock affine
  bundle; refusals for wrong-profile/malformed/mixed inputs; exit codes
  0/2/3.
- Bundle pack live: pack → verify(0) → tamper → verify(2).
- Manifest regen: byte-identical double-regen; all realized counts 512;
  new effective shas 855be4e5 (mixed) / 0316283d (sentinel).
- CI green on every merged head (PR #27's first merge-ref run failed on
  a cross-branch fixture interaction; fixed test-side, then green).
- Post-merge integration reviews (both waves): CLEAN, incl. an
  end-to-end mock campaign → strict → envelope-gate → pack → verify flow
  and a D-033 legacy-identity spoof probe that failed closed.
- `validate-bundle --strict` green over all 6 real corpus bundles under
  the new era rule (PR #22 live gate: 6/6 valid, tamper fails named).

## Known Workspace State

- (2026-07-31, CURRENT) `main` and `origin/main` are both at `6ed1625`:
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
  content was refreshed on 2026-07-31: stamped `updated: 2026-07-31`,
  `latest_report` points at
  `docs/run_reports/2026-07-31-contrast-window-collection.md`, the completed
  `FLOOR-LABEL-01` and `STACK-ID-BIND-01` rows are retired to
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
- Calendar dates pending (P1-008, R-012).
- Wall-meter decision pending (P1-003, R-007).
- Physical network topology pending (P1-004, R-011).
- NVIDIA/Orin access evidence pending (P1-006; gates 2K/2L).
- Git author identity on this machine auto-selected as
  `Ed R <edr@Eds-MacBook-Pro.local>`. Amend future commits if a
  different identity is needed.
