# Durable state — hands-free week, session "Paper experiment loop" 3c46c831 (updated 2026-09-03 19:45 PDT)

Read this first after any usage-limit stall or session death. Ed is away
up to a week from 2026-09-02; rulings in `docs/decision_log.md` D-171.
Ed's /loop mandate (21:05): "til done - keep working on paper - be cognizant
of the usage limits ... make sure work persists through that and pause work
when close until it resets."


## 2026-09-03 19:45 update (read this before the tables below)
- STALL: a 429 monthly-spend limit at 21:50 on 09-02 killed every Claude agent and the loop wakeups; nothing ran until Ed typed "limit reset" at 19:20 on 09-03. Sol runs finished on disk; harvested and committed (below). Lesson recorded in memory `usage-pacing-rule`: ScheduleWakeup is not a wake source across a cutoff; only the watchdog is.
- NIGHT: rehearsal-20260903 delivered (verdict REHEARSAL_ONLY, chain exit 0, gate refused `night_refused_agent_present` as accepted, results branch `night-results/20260903`, courier email 1a066b378497db05, dead-man stood down at 07:00). Courier's harvest = PR #277 (merged 09-03). Night launchd agents UNINSTALLED at the pinned HEAD 33290b8b (`launchctl list` shows none); canonical checkout pulled to origin/main afterwards — the freeze is over.
- TWIN SESSION: the interactive `joulewise-60` in Terminal (pid 1536, session 933847a5) is the session this background job was copied from; its transcript stopped at 20:49 on 09-02. It parents the daemon hosting this job: never message/resume/kill it. Only this session works.
- Decode-identity: round 4 landed and COMMITTED `90689048` (file 50); Opus verifier running → §5 fresh pass → integration replay → PR.
- Paper E: complete, committed `0857bd59`, pushed; two refuters running. Paper F: committed `4cb31a75`, pushed; two refuters running. Paper G: pedagogy refuter 5 blockers (file 02 in its trace dir); Sol fix round 1 running; F2/F4 (Refusal predicate: §4 :800-804 vs retensing plan :26/H04-C/H27-C; DS-32/PG-08 verdict slots) need a magistrate ruling from the quoted texts.
- Floor-pack generator: first run cut before generating packs; resumed Sol seat running in `wt-floorgen` (generators + test exist untracked).
- Watchdog: packet 11 refuted by Opus (file 12: `--bg` base falsified; census narrowing falsified; t0-5 falsified — runbook needs ≥10 min idle, kill by t0-15; plan-pin must precede install; `codex-code-mode-host` escapes the pgid); cold Fable seat re-running with its own scratch dir → synthesis (file 14) → build.
- Code/tests audit (Opus) report exists in the scratchpad (`audit-code-tests/audit-code-tests.md`, 1 test failure seen in its run: `tests.test_reduce.D078R01RegressionTests`) — custody + triage owed.

## PAUSE 2026-09-04 ~00:10 PDT (Ed: "pause work asap usage limit reached") — resume from HERE
Loop stopped; no new launches. Direct Sol runs still in flight write only to their worktrees and `<job>/tmp/out/*.md|.status` (job dir `/Users/edr/.claude/jobs/3c46c831/tmp` — may die with the job; harvest from the WORKTREES: `git status --short` in each, plus the trace dirs' latest numbered reports).

| Lane | Branch @ head | State | Next |
|---|---|---|---|
| Decode-identity | `fix/2026-09-02-decode-identity-set` @ d6805473 | **PR #278 OPEN**, ledger rows 1–10, 12 filled; row 11 NOT-RUN until CI green | when CI green: edit PR body row 11 → `RUN <sha>`, `gh pr merge 278 --merge`, email Ed (merge wave) |
| Paper E | `feat/2026-09-02-paper-e` @ 1ef162b6 | delta round 2 LANDABLE (09); integration replay was running in `wt-int-paper-e` (log `int-paper-e-replay2.log`) | terminal review (item 12), PR with ledger (rows: 02 audit, 03 pedagogy, 03a brief, 05/09 deltas, 06 Opus CR, 07 ruling), CI, merge |
| Paper F | `feat/2026-09-02-paper-f` @ d7ec4568 | rounds 1–4 + bench cures landed; delta 4 (13) + bench (14); Opus CR (11) MERGE; apex read done (mathrm braces) | integration replay was running (`wt-int-paper-f`, `int-paper-f-replay.log`); terminal review, PR, merge after E |
| Paper G | `feat/2026-09-02-paper-g` @ a7da129e | round 2 landed; fact lens done (`out/refute-g-fact2.md`: F1 predicate wording should-fix; F2 = custody files, not a defect); pedagogy lens (luna) was RUNNING in `wt-paper-g` (`out/refute-g-ped2.md`) | custody both (05/06), one fix round (F1 ruling: governed sentence verbatim in §4 form, Outcome C, H04-C, H27-C; abstract/carriers plain-language equivalents naming the same two stages + reason slot), delta, Opus CR, replay, PR |
| Floor generators | `feat/2026-09-02-v5-floor-generator` @ 557b7fc5 | rounds 1–2 landed; delta 2 (09) cleared by the kernel row FLOOR-V5-DRIFT-REPIN-01 (main 0f80c98a); Opus CR (07) MERGE; replay was running (`wt-int-floorgen-bd0c3201`, `int-floorgen-replay2.log`) | apex read (item 7), terminal review, PR, merge |
| Plan pin | `feat/2026-09-03-night-plan-pin` @ 90698150 | rounds 1–2 landed, delta 1 (11) | joint cold gate (packet 17) |
| Watchdog | `feat/2026-09-03-magistrate-watchdog` @ b93f5ffb | build + fix round 1; contract lens (05) NOT LANDABLE: F1 notice-ack race, F2 resident step blocks on git probes (>10 s), F3 glob ruling note, F4 doc rehearsal, F5 clock_uncertain in resident path; **fix round 2 was RUNNING** (`out/watchdog-fix2.md`, report → trace file 06) | harvest fix 2, delta, update packet 17 exhibits (17h2/17k2), re-validate, THEN launch the joint cold gate (cold Fable + Opus refuter, distinct scratch dirs) after a five-hour reset; then install per file 15 row 10 |
| Kernel/bookkeeping | main @ fd12a99d | D-171 addendum, D-170 closed, 14 rows incl. FLOOR-V5-DRIFT-REPIN-01 | after merges: durable state, README blurb, RUN_STATE T31 body, Ed email |

Known environmental: `tests.test_node_worker_subprocess...over_localhost` fails on main in isolation on this machine (pre-existing); `test_calibration_exits` logical-delay test is load-sensitive (CI runs it exclusive).
Budget regime (Ed 2026-09-03): direct `codex-run-v3` seats only (memory `claude-token-burn-regime`, `codex-seat-launch-rules`); Fable reads merge-bound work, Sol writes.

## 2026-09-03 21:05 update — budget regime + lane heads
- BUDGET (Ed 20:45/20:55): budget must last to Monday late evening PST; five-hour window was 60% at 20:35 (resets 00:20). Regime: Sol seats launched DIRECTLY via `codex-run-v3` (no Claude wrapper agents), refuters on Sol/terra/luna, cold Fable only for the mandatory built-artifact gate, Fable reviews everything merge-bound but writes little; 60-min wakeups. Memory: `claude-token-burn-regime`, `codex-seat-launch-rules` (direct-launch pitfalls).
- Main: `14f89811` (kernel batch merged: 13 rows, D-170 closed, ARM-PACKET-01 → V5-TRANSACTION-01) then `2f59e791`, `46eaf18c` (watchdog gate synthesis 15 + build brief 16), `e57bb43e`… hands-free-week files 12 (Opus refutation), 13 (code audit), 14 (cold Fable ruling), 15, 16.
- Decode-identity `fix/2026-09-02-decode-identity-set` @ `3903696c`: round 4 verified 28/28 (file 51), bench cures 52/53/56, fresh pass 54, delta 55; integration replay running at 24df48e8 (prose-only diff since); NEXT: PR with gate ledger, merge.
- Paper E `feat/2026-09-02-paper-e` @ `7e389b53` (fix round 1 landed, bench cures); delta re-audit running. Paper F `feat/2026-09-02-paper-f` @ `a59c8863` (fix rounds 1+2 landed); delta running. Paper G `feat/2026-09-02-paper-g` @ `8b7d20da` (fix round 1 landed); round 2 running with the Refusal-predicate ruling (option 3: one fail-closed Refusal naming the stage) and the 250-word plain-language abstract ruling; after it: fact-lens refuter, integration of E/F/G, PRs.
- Floor generators `feat/2026-09-02-v5-floor-generator` @ `4e742b5b` (ruling: packs generated on the desk day after G2-a with the issued pin); fix round 1 running (ladder schema closure, selection-record parse, registration equality test, p42 addendum); then PR.
- Plan pin `feat/2026-09-03-night-plan-pin` @ `bb5441e3` (fix round 1 landed: age checks before probes, positive production-path test, installer guards, handback sentences); delta running; then the JOINT cold gate with the watchdog build.
- Watchdog `feat/2026-09-03-magistrate-watchdog` @ `2b4476cb` (build landed; bench: probe timeout 10 s, `--permission-prompts none`, tool list; headless `-p` spawn PROVEN with no TTY, rc 0 in 4 s — custody owed as file 02); execution refuter NOT LANDABLE on bench-sized items (429 pattern, zombie poll, two non-biting constant tests) → fix round 1 running; contract-lens refuter running; then joint cold gate (plan pin + watchdog) → install → first stand-down kills this session's tree incl. the Terminal twin (pid 1536) and the daemon.

## Standing constraints (superseded on 09-03: the canonical freeze ended at 03:30; the night agents are uninstalled)
- Canonical checkout `/Users/edr/code/JouleWise`: NO git operations until
  03:30 on 2026-09-03 (rehearsal-20260903 is armed for 02:56 and pins its
  HEAD `33290b8b`). Main pushes only outside 02:45-03:30 and the 07:00 minute.
  Work in worktrees; push to origin from there.
- Bookkeeping to main goes through `/Users/edr/code/JouleWise-wt-bookkeeping`
  (detached, re-fetch before each commit, `git push origin HEAD:main`).
- Tonight's rehearsal refuses `night_refused_agent_present` while this
  session lives; accepted for a stub. Do not touch the night scripts.

## Lanes and where their evidence lives

| Lane | Worktree / branch | State | Evidence |
|---|---|---|---|
| Watchdog (D-169/D-171 item 4) | consult read-only in `JouleWise-wt-watchdog-consult` | designs: Opus (file 03) + blind Fable (file 04) DONE; Sol xhigh design IN FLIGHT (report path `scratchpad/watchdog/sol-watchdog-design.md`, dies with session — custody as file 09 on arrival) | then magistrate synthesis → mechanical packet (validator grammar, see decode-id file 45) → cold Fable + Opus refuter → Sol build → gauntlet → install (Ed authorized). Stand-down margin 5 min. Census must also cover the ChatGPT.app helpers spawned by Codex sessions. |
| Decode-identity | `JouleWise-wt-decode-id`, `fix/2026-09-02-decode-identity-set` @ `04e45f68` (pushed) | packet 45 (sha b31dec0c) at cold gate: cold Fable + Opus refuter IN FLIGHT (`scratchpad/coldgate45/`) | then file 46/47 custody, 48 synthesis, round 4 under formulation 4 (file 44 §3), verify by execution, §5 fresh pass, integration replay, PR. |
| Paper E (§6 negative result) | `JouleWise-wt-paper-e`, `feat/2026-09-02-paper-e` | Sol xhigh IN FLIGHT via codex-run-v3; commits land on the branch | brief file 06; report `scratchpad/paper/REPORT-E.md` |
| Paper F (24 first-use cures, §1 scope, ledger test) | `JouleWise-wt-paper-f`, `feat/2026-09-02-paper-f` | Sol high IN FLIGHT | brief file 07; report REPORT-F.md |
| Paper G (outcome branches) | `JouleWise-wt-paper-g`, `feat/2026-09-02-paper-g` | Sol xhigh IN FLIGHT | brief file 08; report REPORT-G.md |
| `_v5` floor-pack generator (audit B16) | `JouleWise-wt-floorgen`, `feat/2026-09-02-v5-floor-generator` | Sol xhigh IN FLIGHT; NEEDS_RULING likely on the prefill length (no G2-a record committed) | landing report goes to `docs/process_traces/2026-09-02-v5-floor-generator/` in that worktree |
| Measurement checkout | `/Users/edr/JouleWise-measurement-20260813` @ `eeb4e133`, venv relocked | DONE, bench-verified (file 01) | fast-forward again right before each arm |
| Code/tests audit | read-only Opus | IN FLIGHT (`scratchpad/audit-code-tests/`) | custody on arrival |
| Post-freeze bookkeeping (after 03:30) | canonical checkout | TODO | pull canonical; RUN_STATE T31 body; harvest rehearsal-20260903 custody root + stand-down log line under NIGHT-REHEARSAL-01; kernel batch (D-170 close, LINEAGE-RELOCATABLE-01, V4 retirement, ghost-dep retarget, docs-vs-truth 26 corrections in `2026-09-02-fresh-fable-audit/02`) |

If a Sol seat's Claude wrapper died, its Sol run may still have finished:
check the worktree branch for commits and the wrapper's `*-codex-out.md`
beside its prompt; harvest from disk, never relaunch blind.

## Resume sequence after a usage stall
1. `git -C /Users/edr/code/JouleWise-wt-bookkeeping fetch origin` and read
   this file at origin/main; read RUN_STATE.md's T31 pointer.
2. `git worktree list`; for each lane above check the branch head vs the
   state here; harvest any landed reports into this trace dir.
3. Re-launch only what has no evidence on disk.
4. Email Ed (Gmail send_message to the address in the memory file
   ed-notification-channel-email) only at: armed night, stand-down,
   relaunch, merge wave. He reads, does not reply.
