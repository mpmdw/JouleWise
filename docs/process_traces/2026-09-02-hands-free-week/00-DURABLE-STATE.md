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
