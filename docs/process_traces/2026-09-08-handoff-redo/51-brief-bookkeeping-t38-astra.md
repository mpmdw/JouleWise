WRITE_SCOPE: ["RUN_STATE.md","TASK_QUEUE.md","docs/process/state_kernel.json","docs/process_traces/2026-09-02-hands-free-week/00-DURABLE-STATE.md","README.md","docs/process_traces/2026-09-08-handoff-redo/50-bookkeeping-t38-astra.md"]

# Bookkeeping seat — T38 checkpoint after the 2026-09-08 handoff-redo session (gpt-6-astra, medium; dictated fills — verify EVERY fact against the repo/git before writing; flag any that does not check out)

HEAD = main 138e7edb. Dictated facts (all bench-verified by the interactive magistrate this session; you verify
each against `git log`, the PR list, and the named trace files under docs/process_traces/2026-09-08-handoff-redo/):

A. Watchdog state: the 09-06 install handoff TOOK once the laptop lid was opened; the watchdog left CLOCK_UNCERTAIN
   at 2026-09-08 00:51:55 PDT and spawned headless activation 1ef89702 (pid 84232; events.jsonl seq 3-4; PR #295
   trace 21 by that headless magistrate); it died at the Claude Code 600 s background-task ceiling at 01:33 and the
   watchdog relaunched activation 784a764e (pid 83086) at 01:41:58 after its 5-min backoff. Two magistrates exist:
   the Ed-launched interactive session (this one) and the headless resident; lanes split (headless: trace 21/21b/21c,
   PR #295, rehearsal-20260909 prep, email-then-arm; interactive: everything below). The headless magistrate arms
   NOTHING until the interactive magistrate's stand-down message.
B. Merged to main this session (all no-ff merges): e4ce8b3b T0-ACID-CLOCK-01 (acid fixture R0 from the author's
   RAW clock); 3c366db7 T0-ACID-CLOCK-02 (launch-window fixture) + 019f9bba its Linux follow-up (main CI went red
   at a969e526 for one run because the −2 h subcase failed on fresh Linux runners; green again at 019f9bba);
   a969e526 PR #296 D-175 (relaunch prompt line 19 amended: headless magistrate may arm a REHEARSAL_STUB via
   NIGHT_HANDBACK under eight conditions; cold gate + Opus refuter; packet 09-*); 138e7edb PR #297
   WATCHDOG-CENSUS-01 + RESUME-DAEMON-01 (scoped handoff census, per-signal outcome labels, daemon-retirement
   preflight + `handoff-daemons` CLI, resumed-twin classification, dead-lock twin refusal, corrupt-lock recovery
   bound to state.json resident_session per cold gate packet 16 disposition B; gauntlet in traces 06-25, 43, 99).
C. Open PRs: #298 G2A-CHAIN-ROUTING-01 (feat/2026-09-08-g2a-chain-routing, head 44519d14: emitted G2-a chain,
   preflight and night driver take measurement_root/head/interpreter from the v2 plan; retired-literal
   regressions; Opus B1-B3 cured; delta re-audit R1 = test-strength follow-up; replay pending → ledger row 9);
   branch fix/2026-09-08-icloud-backup-probe (ICLOUD-BACKUP-PROBE-01: bounded 2 s backup-root discovery +
   JOULEWISE_BACKUP_ROOTS override in paper_excursion_decomposition, paper_anchor_correction_quantified,
   check_paper_replay_fence; XS/AS pins re-recorded; golden replay byte-identical; Opus fix round C1-C5 running;
   PR to open after).
D. New queue rows to add (H1 unless noted; [AGENT]): WINDOW-STATUS-GUARD-CENSUS-01 (scripts/window_status.sh:42
   greps the whole process table for `run_campaign|window-chain`; a parallel replay's sibling test process trips it
   → guard must match a real measurement chain or the test must isolate the process view; trace 43); ICLOUD-
   CUSTODY-LOCATOR-01 (H2: joulewise/calibration_ledger.py ~4650-4658 `_custody_state()` calls exists()/is_dir()
   on tracked fixture `custody_locator` values under the iCloud path with no budget; static finding, trace 47 C8);
   G2A-PREFLIGHT-ARGV-ASSERT-01 (H2: executable refusal assertions for two positional args and NIGHT_PLAN env
   fallback in the preflight; trace 39 R1); WATCHDOG-NITS-01 (H2: corrupt-lock refusal event appended every tick,
   notice dedupe keyed on reason vs ack keyed on id; installer re-implements the daemon classifier inline; step-4
   block reads lock bytes before an existence check; PID+seconds-resolution lstart identity residual; trace 23
   F2-F4, 24); G2A-FIRST-WINDOW-01 (H1: create the `_v5` measurement clone by the documented recipe at a reviewed
   head, author the G2-a DIAGNOSTIC_NO_PACK v2 plan, install both night agents, email-then-arm; after the
   rehearsal stub; runbook = trace 27); D169-STAGE3-01 (H1, needs_ruling: unattended pack-bound launch — GO-receipt
   consumer + T0 rehearsal closure — required before G2-b and campaign nights; trace 27 §H).
   Mark DONE: WATCHDOG-CENSUS-01, RESUME-DAEMON-01, T0-ACID-CLOCK-01 (all with merge SHAs above); T0-ACID-CLOCK-02
   add as DONE (3c366db7 + 019f9bba); MAC-SLEEP-01 already resolved.
E. State kernel (docs/process/state_kernel.json): tasks.WATCHDOG-INSTALL-01 — all four acceptance evidence items
   are satisfied (install notice emailed 09-04 21:05; installed from canonical main 09-06; first LaunchAgent
   activation 1ef89702 spawned 2026-09-08 00:51:55 PDT with notice_acknowledged at epoch 1788854136.9 for
   transition-2-clock_uncertain, launch email Gmail id 1a0800383847cde1 as reported by the headless magistrate,
   evidence docs/process_traces/2026-09-02-hands-free-week/21-first-launchd-activation-1ef89702.md on PR #295's
   branch; no real plan armed); its dependency ACTIVE-SEATS-HARVESTED-FOR-WATCHDOG-HANDOFF → satisfied (09-06 step 1).
   Decide with the kernel's own conventions whether a fully-satisfied row is removed from the kernel and moved to
   TASK_QUEUE's DONE table (look at how prior DONE rows were handled in git history) — do that.
   tasks.NIGHT-REHEARSAL-01: dependency target WATCHDOG-INSTALL-01 → satisfied with the same evidence pointer; row
   stays blocked until the post-watchdog REHEARSAL_STUB night runs (rehearsal-20260909, t0 2026-09-09 02:56 PDT,
   prepared by the headless magistrate). Then `python3 scripts/gen_state.py` to regenerate the marker-fenced
   regions in RUN_STATE.md and TASK_QUEUE.md and `python3 scripts/gen_state.py --check` must exit 0.
F. RUN_STATE.md: add a T38 pointer paragraph at the top (2026-09-08 ~04:45 PDT) stating A-D in the file's existing
   voice; do not delete T37/T36. README.md: refresh the Status blurb's last sentence to say the watchdog is live with
   a headless magistrate resident and the first rehearsal night is being prepared (plain language; Ed's standing
   rule).
G. 00-DURABLE-STATE.md: APPEND one dated section "2026-09-08 ~04:45 PDT — handoff-redo session (interactive
   magistrate)" with A-D and the exact next actions: (1) headless magistrate arms rehearsal-20260909 after the
   interactive stand-down + Ed's no-NO; (2) PR #298 merge after replay; (3) iCloud PR; (4) G2A-FIRST-WINDOW-01.
   The headless magistrate has ALREADY appended its own dated section on its branch (PR #295) — do not touch
   existing text; append only at the end.
H. Write docs/process_traces/2026-09-08-handoff-redo/50-bookkeeping-t38-astra.md: the list of every fact you
   verified (command + result) and every fact you could NOT verify (flag, do not write it as fact).
Constraints: WRITE_SCOPE exhaustive; do not run the repository-wide suite; acceptance = `python3
scripts/gen_state.py --check` rc 0 plus `python3 -m unittest tests.test_docs_freshness` to a log with rc; no
`git commit`; header < 8192 bytes; genre implementation verdict keys.
