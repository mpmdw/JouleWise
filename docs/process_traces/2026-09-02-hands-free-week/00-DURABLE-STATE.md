# Durable state — hands-free week, session joulewise-60 (updated 2026-09-02 21:07 PDT)

Read this first after any usage-limit stall or session death. Ed is away
up to a week from 2026-09-02; rulings in `docs/decision_log.md` D-171.
Ed's /loop mandate (21:05): "til done - keep working on paper - be cognizant
of the usage limits ... make sure work persists through that and pause work
when close until it resets."

## Standing constraints tonight
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
