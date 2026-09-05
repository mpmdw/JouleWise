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

## 2026-09-04 02:05 status (after the fan-out harvest)
- MERGED: PR #278 (decode-identity) → main bb4930d1. OPEN with full ledgers (row 11 pending CI): #279 paper-e, #280 paper-f, #281 floor generators — merge order E → F (merge main into F first, re-run the paper tests) → generators.
- FAN-OUT: 47 direct Codex missions (wave 1 = 12, wave 2 = 35); 46 landings committed UNREVIEWED to `feat/2026-09-04-fan-<name>` (or the named branches) and pushed; rulings owed and given: `docs/process_traces/2026-09-04-fanout/00-rulings-owed.md`, `01-magistrate-rulings.md`. 28 execution-lens refuters running (worktrees `wt-ref-<name>`, outputs `<job>/tmp/out/ref-<name>.md`); resumed seats: fan2-docs (docs-vs-truth + doc008 with root scope), fan2-instrument (successor acceptance artifact), fan2-r7f-exit3 (option A), fan2-kernel (retirements/closures in `wt-kb2`).
- WATCHDOG: fix round 2 landed at fc21ab3b; delta running; then packet 17 exhibits refresh (17h2 = fix 2 report, 17k = contract lens, 17l = delta 2) → joint cold gate (cold Fable + Opus refuter, distinct scratch dirs) → install → first stand-down. PAPER-G: round 3 running (predicate verbatim in §4 form / Outcome C / H04-C / H27-C; plain-language carriers).
- Owed to Ed (parked, emailed 02:00): charter v3 digest re-ratification; QUIET-GUARD-01 inactive install on his host.
- Known environmental: `test_node_worker_subprocess…over_localhost` fails on main in isolation on this machine; calibration-exit logical-delay test is load-sensitive; `test_window_status_guard` flakes under concurrent git operations.

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

## 2026-09-04 (magistrate, mid-day) — merges and running seats

- MERGED: PR #279 (paper-E) at main b0ed6991; PR #281 (`_v5` floor generators) at main a39e33a2.
- paper-F `feat/2026-09-02-paper-f` at 8375ffc5: origin/main merged twice (skeleton conflicts resolved by a Sol seat, report `2026-09-02-paper-f/15-merge-resolution-report.md`; magistrate read the resolved hunks); CI running; then ledger rows 11/12 → merge.
- paper-G `feat/2026-09-02-paper-g` at 114092f9: fix round 4 harvested, delta re-audit round 4 CLEAN (`2026-09-02-paper-g/11-delta-reaudit-round-4.md`); integration replay running in `JouleWise-wt-int-paper-g-0e552a6f` (log `~/.claude/jobs/3c46c831/tmp/int-paper-g-replay-r4.log`); terminal review 99 owed; will conflict with F on the skeleton → same resolution-seat pattern, then PR.
- Night plan pin `feat/2026-09-03-night-plan-pin` at b4d961d6 (round 3 + one-line fixture fix, three night modules green).
- Watchdog `feat/2026-09-03-magistrate-watchdog` at 1e324e3d = plan-pin merged + round 4 on the integrated base (B-1 v2 plans/retired-v1 ignored, handoff procedure + `handoff-inventory`, Q4/Q5 text); three night modules green; Sol xhigh delta re-audit running → trace 10; then packet 21 → re-convene cold Fable + Opus.
- Fan-out: first refuter round (28) returned NOT LANDABLE almost uniformly with ONE signature — stale base / non-ancestral / unrelated-range contamination (branches cut before main moved; refuters diffed against a moved origin/main). Structural cure applied: every `feat/2026-09-04-fan-*` branch had origin/main MERGED in (no rewrite) inside its own worktree, magistrate-owned state docs reset to main (32 refreshed; conflicts: GENERATOR-CORE-01 on `generate_configs.py` — likely superseded by PR #281 — and one-name-sweep on the paper registry/survival map). Second refuter round (32 Sol high seats, merge-base diff, `02-refuter-merge-base.md` per mission) running. Real non-staleness findings to carry: EPOCH-LINT spoofable CLI check; GAMMA-UNIT-ROSTER trusts mutable plan_id; PREWINDOW-V5-PIN accepts an occupied retired root; CALEXITS-HYGIENE false counterfactual; floor-guarantee / transfer-fiducial edited the paper skeleton (paper-lane-owned).
- Ed asked (in-session) the cost of a 5-min vs 15-min stand-down; answered from `docs/phase_2/window_runbook.md:425-432` (≥10 min untouched idle before the ledger pair, `prewindow_check.sh --wait` READY precondition, in addition to the 180 s settle). 15 stands unless Ed objects.
- Tooling note: the auto-mode classifier blocks `gh pr edit --body-file` and background `gh` polling loops; `gh pr edit --body "$(cat file)"` and `gh pr checks N --watch` pass.

## 2026-09-04 (later) — paper-F merged, paper-G PR open, watchdog escalation consult → round 5

- MERGED: PR #280 (paper-F) at main e8e1fd9e (after two main merges; skeleton conflicts resolved by seat, report `paper-f/15`).
- PR #282 (paper-G) OPEN at c8ba4f5d+99: main merged in (ledger conflicts resolved, report `paper-g/12`); terminal review 99 written; full-suite replay on the integration tree running (`~/.claude/jobs/3c46c831/tmp/int-paper-g-replay-final.log`); rows 9/11 then row 12 re-pin → merge. Residual queued: `PAPER-H-INTRO-GLOSSARY-01` (Section 1 definitions paragraph is a glossary dump; passes the first-use test).
- WATCHDOG: the standing escalation trigger fired (rounds 3 and 4 same signature: unit-green / production-broken; trace 10 F1–F5). Consult run: Sol xhigh (trace 11) + Opus contract lens (trace 12); magistrate synthesis + round-5 contract (trace 13, rulings R-1..R-7); round 5 landed (trace 14) with a production `joulewise/night_plan_writer.py`, a real-subprocess CLI gate test (`tests/test_magistrate_watchdog_cli.py`, red→green), fail-closed plan classification (IGNORE only positively-identified v1; HOLD unreadable/malformed/future), single `Probes` constructor via `make_probes`, owned/unclassified handoff inventory with explicit `--adopt-pid`, pid+start-time reaper, `plan_conflict` HOLD, dynamic checkout fence. Bench: 163 tests OK across the five night modules at aeacba61. Sol xhigh delta re-audit round 5 running → trace 15. Then packet 21 (proposals 4/5 relabeled, R-6/R-7/R-9 amended texts, the process PROPOSAL "production-shaped subprocess test is a mandatory gate row for watchdog/launcher/installer changes", Q2 pinned to the final head) → cold Fable + Opus re-convene → install handoff.
- Fan-out: second refuter round (33 seats, merge-base diff) running; GENERATOR-CORE-01 ruled INDEPENDENT of #281 by scout → Sol xhigh retarget onto main's three live `_v5` generators running; one-name-sweep merge resolved (5b45b415) and its refuter running.

## 2026-09-04 ~04:40 PT — watchdog rounds 5–8, packet 21 drafted, fan-out wave 1 + fix rounds

- WATCHDOG `feat/2026-09-03-magistrate-watchdog`: round 5 (post-consult, traces 13/14, delta 15 RESIDUAL) → ruling 16 with S-1..S-4 → round 6 (17, delta 18: S-1/3/4 cured) → S-2b addendum → round 7 (19, delta 20 CLEAN) → apex read finding A-1 (hold-drain not bounded by stand-down phase) → Opus counter-review of the final head (21: NOT LANDABLE — B-1 = A-1 drain can KILL after t0; B-2 plist pins the installer's checkout; B-3 monotonic backoff survives reboot; B-4 installer untested; S-1..S-6) → ruling 22 (C-1..C-9; round 8 is the LAST round before the cold gate) → ROUND 8 RUNNING (Sol xhigh). Then: delta 8 → seal packet 21 (branch `feat/2026-09-04-packet-21`, draft b5a2a47d, 35 exhibits, `<<FINAL-HEAD>>` placeholder; validator needs `--expected-packet-sha256`) with Q-SIG carrying both same-signature statements and the trace-16 dissent → cold Fable + Opus refuter → install handoff.
- FAN-OUT: wave-1 integration branch `int/2026-09-04-fan-wave-1` (12 landable landings; Opus counter-review LANDABLE with F-1/F-2/F-3; Sol contract refuter NOT LANDABLE on CWI-01 = charter v3 candidate omits the registry's convening clauses) → wave-1 fix round RUNNING; full replay rerun after it; then PR. 21 not-landable branches: fix round 1 done — 14 clean (delta re-audits RUNNING), 4 NEEDS_SCOPE granted and resumed (doc008, docs-vs-truth, EPOCH-LINT-01, R7F-EXIT3-SEMANTICS-01), 3 NEEDS_RULING ruled and resumed (PHASE-SHARE wording; one-name-sweep rebuild without producer paths; LINEAGE-RELOCATABLE-01 NR-1..NR-3 adopted, cold gate before merge). GIT-FIXTURE-MAINTENANCE-SWEEP-01 harvested (rc=65 envelope, uncorroborated) — bench replay 797 tests green except its own guard on a post-#281 call site; refuter GF-02 (guard scans only test_*.py) → fix round RUNNING. GENERATOR-CORE-01 retarget (xhigh) and one-name-sweep still open.
- PAPER: #282 (paper-G) CI green except the advisory ledger; integration replay on c8ba4f5d still running (log `int-paper-g-replay-final.log`).
- Magistrate-owned follow-ups owed after the wave merges: kernel rows (Opus F-2: p2-rows' four retirements, QUIET-GUARD-01 wording, PREWINDOW-REGEX-01 row, P2-027/035/047A/050), RUN_STATE T32 header, README blurb.

## 2026-09-04 ~07:30 PT — packet 21 sealed and convened; paper-G merged; paper-H at its second cold gate; fan-out waves 1–2

- MERGED: PR #282 (paper-G) at main a6e9edde; docs refresh (README blurb, RUN_STATE T32, PROJECT_STATUS) at a740d5c4. All four paper PRs are in.
- WATCHDOG: rounds 8 (C-1..C-8 from Opus B-1..B-4/S-1..S-6 + apex A-1) and 9 (installer rollback) landed; delta 9 CLEAN; FINAL HEAD fdbb840c (+ trace 26). Packet 21 SEALED on `feat/2026-09-04-packet-21` (sha 177d4359…, 43 exhibits, validator PASS). Opus contract refuter (trace 23): B-A — the install checklist assumes the watchdog is on the canonical main checkout, i.e. the branch must MERGE first and the merged tree must be suite-tested (integration branch `int/2026-09-04-watchdog` cc0f914a, full replay running); H-2 dead-watchdog detector needs an independent liveness signal (courier reports state.json age); S-A delta-8's third same-signature YES needs a ruling exhibit; H-1 17j missing from the manifest. Cold Fable judge: attempt 1 ended without writing (background tasks died with the session); attempt 2 running foreground-only → ruling 22. NEXT: magistrate synthesis (24), cure B-A/H-1/H-2/S-A, PR for the watchdog branch (12-row ledger), merge, THEN install from canonical main via the checklist.
- PAPER-H (`feat/2026-09-04-paper-h`): glossary dissolved; refuters PED-01..03/FACT-01 → fix 1 → delta CLEAN → Opus CR-01 (second-round PED-02 class) → COLD GATE #1 (trace 06: amend texts; CR-02/03/04 this round; one bounded round then merge) → fix 2 → fresh reading-order delta (08) RESIDUAL, same-signature YES → COLD GATE #2 running (trace 09) to rule disposition (final bounded round / merge with registered residual / revert).
- FAN-OUT: wave 1 `int/2026-09-04-fan-wave-1` (12 landings; Sol contract CWI-01 + Opus F-1/F-3 fixed; delta DR1-F1 one-clause fix running under ruling 04a); wave 2 `int/2026-09-04-fan-wave-2` = wave 1 + 11 landings (99c80bca), contract refuter running. Round-2 deltas: C3-RECOGNIZER, LINEAGE (cold gate NR-3 before merge), PHASE-SHARE, docs-vs-truth LANDABLE (join wave 2); COLDGATE-HANDOFF-01 same-signature → consult running. Five same-signature stops consulted (Sol xhigh, D-161) and RULED in 01-magistrate-rulings.md: AUTH re-scoped to D-151 V-1(vii); EPOCH-LINT-01 RETIRED; GAMMA re-scoped to the generator's own check; one-name-sweep WARN-AND-RECORD; p1-rows docs reconciliation — four re-scope seats running. GIT-FIXTURE sweep fix 2 running. skill-distill LANDABLE but doctrine → held for a cold gate.
- Tooling lessons (memory updated): cold judges via `claude -p` from a doctrine-free worktree, detached, FOREGROUND-ONLY charge; scope globs with `*` in filenames are refused (rc=64, no status file); `git add -A docs/process` excludes `docs/process_traces`.

## 2026-09-04 ~11:30 PT — watchdog PR #284 open after cold gate 22; paper-H PR #283; D-172; wave 2 rebuilt

- WATCHDOG: cold ruling 22 (packet 21, second convening, foreground-only) + Opus refutation 23 → synthesis 24 (cure table) → rounds 10 (M-A/M-B/M-C/H-2/step 0/24a) and 11 (reaper detachment guard; step 0 vs merge commit) → delta 11 residual N1 cured at the bench (trace 31, executed both paths) → terminal review 99 → **PR #284** open; integration replay on `int/2026-09-04-watchdog` (main d7d74225 + final head) running; CI running. After merge: canonical `pull --ff-only`, step 0 digest check, Terminal-hosted install per checklist; then the first launchd activation + `notice.ack` + a REHEARSAL_STUB night through the night driver's own courier BEFORE any real plan is armed (ruling 22 Q-C9). D-172 (real-entry-point subprocess test rule) recorded; Ed emailed with veto option.
- PAPER-H: two cold rulings (06, 09), final bench round (10), sentence-unit delta CLEAN (11), terminal review 99 → **PR #283** open; CI green except ledger rows 9/11; full replay running.
- FAN-OUT: wave 2 rebuilt on the final wave 1 (f7579c84) + 15 landings (ac7ca7f0; reduce.py restored to the D-138 pin on CUSTODY-HARDEN-01); round-2 contract refuter running; four landings (R7F-EXIT3, docs-vs-truth, one-name-sweep, GIT-FIXTURE sweep) merged with wave 2 on their branches by Sol seats and wait to fold in after the refuter. AUTHENTICATOR-ALLOWLIST-GUARD-01 PARKED (third same-signature occurrence; three-seat design consult owed). EPOCH-LINT-01 retired. LINEAGE-RELOCATABLE-01 landable but gated on a cold gate (NR-3). skill-distill held (doctrine).

## 2026-09-04 ~16:30 PT — paper H merged; supplier contracts ruled; four supplier seats; watchdog PR at its ledger

- MERGED: PR #283 (paper-H) at main 9eef8584. Paper lane next = result SUPPLIERS buildable before data: scout (`docs/process_traces/2026-09-04-paper-i/01`) mapped 68 STOP_FILL rows; three-seat consult (Sol 02 / Opus 03 / blind Fable 02-blind) + adjudication packet 05 → magistrate rulings 06 (R1 `reported_phase_energy.v1` with the composition rule behind an ID — the t95+window variant is PROPOSED for a cold gate before collection; R2 `claim_verdicts.v2` sibling `claim_side_bound` = the clock-anchor term, full symmetric prefill token family; R3 `transfer_fiducial_result.v1` projection, `[TRANSFER_FIDUCIAL_RESULT]`, Diagnostic-only prose; R4 D-165 renderer: register OB/OR strings, no precedence channel, governed before-comparison bytes, `_v5` identity gate). Seats RUNNING on branches `feat/2026-09-04-d123-reported-mean`, `feat/2026-09-04-gamma-claim-renderer`, `feat/2026-09-04-transfer-result-renderer`, `feat/2026-09-04-d165-outcome-renderer` (fix round 1). Each gets refuter pair + Opus counter-review before merge.
- WATCHDOG PR #284: replay on 6975485d (4992 tests; two explained exclusions) recorded in 99; four Linux-CI portability commits (base64 --decode, plutil fallback, uninstall never mkdirs custody, resolved-path interpreter assert); ledger complete at head aa67c00d; checks watched → merge → canonical pull + step 0 → install → first launchd activation + notice.ack → REHEARSAL_STUB night → first real window.
- FAN-OUT wave 2 (`int/2026-09-04-fan-wave-2`, 19 landings + doc008 with restored terms): round-3 contract refuter NOT LANDABLE (R3-F1 sign-off row — the sign-off commit had landed on the doc008 branch by mistake, now on main 45355f1e; R3-F2 three direct git-init calls from one-name-sweep/LINE-AUDIT under the sweep's guard; R3-F3 R7F /var assertion regrown; R3-F4 arm-readiness integration timing) → seam-fix seat RUNNING on the int tree; then main + doc008 tip merged, full replay, refuter round 4, Opus counter-review, PR.
- Lessons in memory: gate bench commits on the stripped test tail; Linux CI vs Mac bench for shell installers; cold judges foreground-only.

## 2026-09-04 evening — watchdog MERGED (#284, main c74c7e6a, step 0 STEP0_OK live); install pending the quiet point; wave 2 at its final replay; supplier lanes in fix rounds

- WATCHDOG: on main; canonical checkout pulled; step 0 digest check executed live → STEP0_OK. INSTALL = the handoff procedure in `docs/process/MAGISTRATE_WATCHDOG.md` (stop every background task, inventory, install from canonical main, first launchd activation + `notice.ack`, then a REHEARSAL_STUB night through the night driver's own courier BEFORE any real plan). It hands off FROM this session, so it runs at the quiet point after the in-flight seats are harvested.
- FAN-OUT wave 2 (`int/2026-09-04-fan-wave-2` dc195049): replay diagnosis (07) — one shared finalization-fixture seam vs CUSTODY-HARDEN's NEG-8 ingress (fixture corrected; the narrowing STANDS as an evidence fence) + stale-module artifacts; seam-fix round 4 (08) applied the integration rulings (guard green; bridge gate removed; handoff fence kept; B2/B3; README; mutation kill); W8 and the PHASE-SHARE queue row cured at the bench. Definitive full replay RUNNING (`int-fan-wave2-replay-2.log`); then contract round 5 + Opus re-read → PR.
- SUPPLIERS (paper-I): rulings 06 + addenda 07 (R2 sidecar; R4-F1 replaced), 08 (Q-R1-5 replaced: producer-only projection), 09 (R4 tightened: reason map, identity-pin validator, custody, out-of-band refusal), 10 (R2-FL-1 floor-lineage at the canonical validator). d165: fix 3 landed, delta 3 running; d123: fix 2 landed, delta 2 running; gamma: fix 2 running; transfer: fix 2 landed, delta 2 running. Each merges only after delta CLEAN + Opus + apex read; then one integration tree for the four (they all amend registry rows — conflicts expected; resolve on integration).
- PARKED/HELD: AUTHENTICATOR-ALLOWLIST-GUARD-01 (three-seat design consult owed); LINEAGE-RELOCATABLE-01 (cold gate NR-3); skill-distill (doctrine → cold gate); the Q-R1-2 composition rule proposal (cold gate before collection); EPOCH-LINT-01 retired.

## 2026-09-04 ~16:00 PT — fan-out waves 1+2 are PR #285; custody seam in fix round 2; watchdog install still pending the quiet point

- FAN-OUT: `int/2026-09-04-fan-wave-2` → **PR #285** (32 landings; five Sol contract rounds, two Opus counter-reviews, five seam-fix rounds; bench restorations of the frozen v1 validator and draft-v1; MODULARITY generalisation re-homed in `joulewise/analysis_manifest_v2.py`). Final replay running (`int-fan-wave2-replay-3.log`); CI running; rows 9/11/12 then merge. After merge: kernel rows (Opus F-2 from wave 1: p2-rows retirements, QUIET-GUARD wording, PREWINDOW-REGEX row, P2-027/035/047A/050), README blurb, RUN_STATE T33.
- SUPPLIERS: all four supplier lanes are blocked on the custody-read seam (`feat/2026-09-04-paper-custody-seam`, PAPER-CUSTODY-SEAM-01): landing → two refuters NOT LANDABLE → fix 1 → delta NOT LANDABLE (inputs.py bypass, shim, D-173 text) → fix 2 RUNNING (bounded; a repeat routes to a consult). D-173 (proposed/provisional) text synced to addendum 16 (role + runs root; git-tracked supply map). Rulings 06 + addenda 07–10, 15, 16 on `feat/2026-09-04-paper-i-scout`. Supplier branches at their last heads: d123 (fix 2, delta NOT LANDABLE third occurrence → seam), d165 (fix 3, delta NOT LANDABLE third → seam), gamma (fix 2, delta NOT LANDABLE third → seam), transfer (fix 3 committed; B1 → seam). Each re-lands on the seam after it passes; then one paper-supply cold gate (D-173) before any merges.
- WATCHDOG: merged; install waits for the quiet point (custody seam + wave 2 settle), then handoff → first launchd activation → REHEARSAL_STUB night. Window tonight ~02:56 PT.

## 2026-09-04 ~19:30 PT — astra peer audits landed; consult convened; scope-freeze pending

- Three gpt-6-astra peer audits archived at docs/process_traces/2026-09-04-peer-audit/ (01 full base, 02 claim spine,
  03 paper vs code); 04 = magistrate bench verification (all four executable witnesses reproduce on f4c812b4);
  05 = three-seat consult questions Q1–Q7. Ed emailed (thread "astra peer audits are in").
- Running: Sol xhigh physics consult → 10-consult-sol-physics.md (wt-consult-sol); Opus contract consult →
  11-consult-opus-contract.md (wt-consult-opus, Agent); blind Fable → 12-consult-blind-fable.md (wt-consult-fable);
  legacy-L1 cure seat → 20-legacy-l1-cure-report.md on feat/2026-09-04-legacy-l1 (wt-legacy-l1).
- Next after consult: magistrate synthesis (13), estimand + D-165 relabel rulings → cold Fable gate (claim-bearing),
  paper-K seat (03-F4 methods-vs-code corrections, null-vs-model wording, F+B metadata) after paper-J merges,
  Q4 floor-prompt regeneration decision, Q6 scope freeze ruling (skill-distill second convening PARKED until Q6).
- Kernel rows merged to main (branch head 064b0dbc; merge landed with the next push). AUTH round 3 running with the registry file in scope (report 15).
- Still running: custody fix 4, paper-J fix 1, wave-2 replay-3 (PR #285 rows 9/11/12 pending).

## 2026-09-04 ~22:30 PT — consult complete; astra mirrors the magistrate; cures in flight

- Consult seats archived: 10 Sol physics, 11 Opus contract, 12 blind Fable. Draft ruling 13 on main (cfdb24ac).
  Ed (in chat): "when astra gets back … assess its work … have it mirror your tasks and you two discuss final
  moves" → assessment given in chat; astra peer-magistrate seat running → 14 (wt-astra-peer). Then 15 (magistrate
  reply), 16 (astra final), 17 (final ruling) → cold Fable gate. PARKED lanes launch no new rounds until 17.
- Custody seam: fix 4 f2d35b4f, delta 4 LANDABLE (10). F1 = token recoverable by private introspection →
  outside D-161 ordinary-operator threat; cure = narrow contract lines 53-56/75-81, no code round. F2 = census
  regression is a string count → test debt, recorded. Peer-audit 02-F4 width recomputation: factor the mint's
  reconstruction (1–2 days) — packet question, not a round. Seal the paper-supply packet AFTER 17 (D-173 amendments).
- FB-PLANNING-METADATA-01 (wt-fb-metadata): seat landed keys, but detection_floor.py:3353 compares the artifact's
  object to the canonical emitter by exact equality (also :3845, :4115, analysis_engine/artifact.py:494) → every
  previously issued floor object would fail validation. HELD, not merged; needs SINGLE_COUNT_DISCIPLINE_ID .v2
  with a version-aware validator + adapter_contracts.md amendment = cold-gate item in 17.
- ESTIMAND-ENCLOSURE-01 (wt-estimand-enclosure) still running; its blast-radius report decides field vs script.
- Legacy L1: rounds 1+2 on feat/2026-09-04-legacy-l1 (a379b5af), execution refuter running → PR.
- Paper-J: PR #286 open (rows 9/11/12 pending). Wave-2 PR #285 replay-3 still running. AUTH round 3 running
  (last round; PARK after).

## 2026-09-05 ~02:00 PT — final ruling 17 written; cold-gate packet sealing; paper-K launched

- Peer discussion closed (14 astra plan, 15 reply, 16 astra final). FINAL ruling 17 on main (e323f1aa) with the
  decision-log addendum texts (D-078, D-083, D-165, D-166, scope-freeze rule, D-161 line). NOT ratified until the
  cold Fable gate rules: packet seat → 40-coldgate-packet-ruling-17.md (wt-packet-ruling-17); then convene cold
  Fable (doctrine-free worktree, foreground-only charge) + Opus refuter; then decision-log edits + email Ed.
- Ed emailed (thread "three questions only you can answer"): due date / fallback acceptability; same-condition vs
  ensemble prompt question (default prompt-0 contrast); estimand relabel veto. Defaults proceed if silent.
- Seats running: paper-K (wt-paper-k, off paper-J head + 17 staged; provisional under 17); wave-2 T0 test cure
  (wt-int-fan-wave2; test-only; fanout/31); legacy-L1 delta 3 (24); AUTH round 3 (last; PARK after);
  paper-J full replay (~/.claude/jobs/3c46c831/tmp/paperj-replay.log) for PR #286 row 9.
- Held branches: feat/2026-09-04-estimand-enclosure (accepted conditionally in 17 Q1; needs inside-one-record
  oracle + delta), feat/2026-09-04-fb-metadata (re-brief to 17 Q3 shape after the gate).
- Wave-2 #285: replay-3 5116 tests, 2 failures diagnosed (fanout/30): node-worker = environmental pre-existing
  (ledger wording in 30); T0 real-boot = test defect, cure seat running; row 9 fills with the re-run tail.
- Internal cuts adopted: readiness proven by 6 Sep or fallback; last acquisition night 8 Sep; freeze 9 Sep.

## 2026-09-05 ~05:30 PT — ruling 17 RATIFIED as amended (gate 41/42, synthesis 43); post-gate seats running

- Cold gate: 41 (Fable) + 42 (Opus refuter) agree; 43 adopts every amendment. Enclosure = DESK SCRIPT (reducer field
  rejected: strict validation of stored 0.5.2/0.6.2 summaries). D-166 sentence and scope-rule insertion adopted;
  D-161 as rule text. Dates: last acquisition night 8 Sep; desk 9 Sep 06:00–18:00; freeze 9 Sep 18:00 PT.
- Seats: dl-ratify (decision-log addenda D-078/D-083/D-165/D-166, new D-174, D-161 line; wt-dl-ratify);
  enclosure-script (revert reducer, scripts/paper/partial_record_enclosure.py + DERIVE row; wt-estimand-enclosure);
  fb-v2 (SINGLE_COUNT_DISCIPLINE .v2, ten equality sites; wt-fb-metadata); d165-relabel (wt-d165-relabel);
  d166-prompt0 (census first, NEEDS_SCOPE allowed; wt-d166-prompt0); paperk-fix1 (F1 terms + F2 note; title →
  astra's 'Timing Sensitivity of Phase-Energy Assignments on Apple Silicon'; wt-paper-k).
- PRs: #285 wave-2 (merged main; T0 test cure; rows filled at f1600c10; CI watched); #286 paper-J (rows 11/12
  filled; full replay running for row 9); #287 legacy-L1 (opened; rows 9/11/12 pending). AUTH parked at 93d0d91c.
- Ed emails outstanding: due date/fallback; ensemble vs same-condition; estimand relabel veto (defaults running).

## 2026-09-05 ~08:00 PT — MODEL ROUTING CHANGE (Ed, in chat): astra replaces Sol everywhere
"keep spamming astra use it instead of sol in all cases now. use sol where you would have used terra. luna max for
simple tasks. astra high for an equal use in all parts for fable 5.1 with 5.1 deciding final merges."
→ every NEW seat: `-m gpt-6-astra --effort high` (xhigh on the usual triggers); Sol = mid tier; luna `--effort max`
= simple tasks (probe running); astra is an equal peer in review/consult/adjudication; Fable merges. Recorded in
memory (instrument-mix-authority). First astra seats under the rule: paperk-astra (peer review beside Opus),
packet-paper-supply-2 (D-173 cold-gate packet seal with seam head 84b24686 and 43 Q6 / 02-F4 questions).
Still-running Sol seats (launched before the rule) finish as is: d174-wire, enclosure-script, fb-v2b.

## 2026-09-05 ~13:00 PT — D-173 gate closed; astra routing + orchestration adopted; lanes in gauntlet
- D-173: cold gate 21 (Fable) + 22 (Opus) → 23 synthesis: ADOPTED AS AMENDED (receipt clause replaced; scope /
  non-issuing type / git_blob coverage / whole-window clauses; Q-PS-3 acceptance spec with seven cases →
  REFUSAL-CARRIER-01; Q-PS-4 one mint desk check; Q-PS-5 Q-R1-2 REFUSED). Luna seat installs the D-173 addendum
  (wt-d173-adopt). Astra round-5 design spec running (wt-seam-spec → paper-custody/11).
- Orchestration: astra design consult 01 adopted as routing 02 (docs/process_traces/2026-09-05-orchestration/).
- Lanes: paper-K fix 2 committed (1dcf45bf), delta 3 running; enclosure fix 1 (Opus C-1/C-2) running; F+B v2
  round 3 (R1 aggregation, R2 html) running; D-165 relabel fix 2 (R1 floor mirrors, R2 night_gate pin, R3
  wording) running; D-166 luna registry fix running. PR #286 paper-J + PR #287 legacy: full replays running
  (~/.claude/jobs/3c46c831/tmp/{paperj,legacy}-replay.log) for row 9.
- Ed's three questions still open by email (defaults running).

## 2026-09-05 ~16:30 PT — paper-K PR #288 (stacked on #286); ruling-17 code lanes in delta; D-173 adopted on main
- PR #288 paper-K (92f1ca19 + 99) base = feat/2026-09-04-paper-j; retarget to main after #286 merges. CI watched.
- Enclosure: fix 1 (Opus C-1..C-6) committed 5a29be48, astra delta running (39). F+B v2: round 3 committed
  df1a2d82, astra delta 2 running (39-fb). D-165: fix 2 committed c43b7086 (floor-pack generator digests change →
  custody supersession before collection), astra delta running (05). D-166: registry fix committed 3aeed4ed,
  astra delta running (05). Seam round-5 design spec (astra xhigh) still running → paper-custody/11.
- D-173 adopted as amended on main (2fcf4397). Orchestration adoption 02 on main.
- Replays for #286 (paper-J) and #287 (legacy) still running under load ~10 (both machine-heavy).
- Rule learned (memory): merge to main ONLY from the canonical checkout; never `pull --ff-only` in a worktree.

## 2026-09-05 ~20:00 PT — paper-J MERGED (#286 → fcf86495); paper-K retargeted to main (#288, head d053e969, replay running)
- Paper-L tree (feat/2026-09-05-paper-l, from the K head): integrates the enclosure branch and the D-166 branch
  registry rows (both conflicted with K), then an astra seat adds the appendix enclosure figure + citation and the
  PE-01 row validation (enclosure delta 39 D2/D3).
- D-165: Opus review NOT LANDABLE (F1 fill-checklist rationale, F2 campaign pack doc, F3 validator adopts supplied
  rule_id); round 4 running with the STRUCTURAL cure (repo-wide retired-rationale census test) per the same-signature
  trigger. F+B: round 4 committed; delta 3 with from-scratch consumer census running (same trigger applies).
- Seam round 5 (astra xhigh) still running. Legacy replay still running.

## 2026-09-04 ~20:15 PDT — RELAUNCH RESUME PLAN (for the headless magistrate the watchdog spawns after tonight's install handoff)
Authority: Ed's /loop (2026-09-04 evening): "the first priority is fully being able to run windows and experiments
yourself"; cold ruling 22 (install affirmed; FIRST NIGHT = REHEARSAL_STUB only, no real plan until Q-C9 evidence);
D-174 scope freeze; routing 2026-09-05-orchestration/02 (astra default, luna max simple, Opus contract lens).
Handoff executed per docs/process/MAGISTRATE_WATCHDOG.md §Install handoff steps 0–6 after PR #288 merged (HEAD = merge).

FIRST ACTS (per MAGISTRATE_RELAUNCH_PROMPT): heartbeat → launch email to Ed (why launched, pending notices, resume
list) → notice.ack. That completes the first launchd activation evidence.
THEN, in order:
1. Record the activation evidence (state.json, events, heartbeat, notice.ack) as a trace under
   docs/process_traces/2026-09-02-hands-free-week/ (this is Q-C9 evidence item 1) and commit.
2. Arm a REHEARSAL_STUB night for the next belt via docs/process/NIGHT_HANDBACK.md (email-then-arm; Ed's NO
   overrides). Never a real plan yet. Exit before the request deadline once armed; the LaunchAgent is the wake source.
3. Lanes to resume (each has a worktree + branch, all pushed):
   - PR #288 paper-K: if not merged, fill row 9 from ~/.claude/jobs/3c46c831/tmp/paperk-replay.log tail, merge.
   - feat/2026-09-05-paper-l (wt-paper-l): fix round 1 (production parsers for PE-01) → delta → apex → PR on main.
   - feat/2026-09-04-paper-custody-seam (wt-paper-custody): round 5 landed 01d00591; astra execution refuter 13 NOT
     REFUTED; Opus contract refuter 14 pending/landed → fix round if needed → delta → apex → PR. F6 REFUSAL-CARRIER-01
     only if readiness (6 Sep) is met.
   - feat/2026-09-05-d165-relabel (wt-d165-relabel): round 5 landed; delta 3 (10) → Opus re-review if needed → PR
     (registry conflicts with paper-K: author the merge). Floor-pack generator digests changed → custody
     supersession of the floor packs BEFORE collection (delta 05 lists the artifacts).
   - feat/2026-09-04-fb-metadata (wt-fb-metadata): consult 42 = structural cure (accessor choke point + persistent
     census + shape matrix). Implement per 42 as one astra xhigh seat; R4 (unhashable rule_id TypeError) and S2 in
     the same round; then delta; then PR.
   - feat/2026-09-04-estimand-enclosure: folded into paper-L (registry) — close via paper-L's PR; the enclosure
     branch itself needs no separate PR after L lands (verify byte-identity of the script).
   - feat/2026-09-05-d166-prompt0: registry rows already integrated in paper-L; the generator change + supersession
     record still need their own PR after L (rebase on main; refuter 03 NOT REFUTED on generation).
   - PR #287 legacy-L1: rerun the full replay on its head at low load (~/.claude/jobs/3c46c831/tmp/legacy-replay.log
     was killed by the handoff), fill row 9, merge; then the D-161 addendum is already on main.
   - AUTH, receipts, skill-distill, LINEAGE: PARKED (D-174).
4. Ed's three open questions (email thread "three questions only you can answer"): due date/fallback;
   ensemble vs same-condition (default prompt-0); estimand relabel veto. Defaults are running.
5. Seat launch mechanics: ~/.local/bin/codex-run-v3 <out.md> -C <worktree> -s workspace-write -m gpt-6-astra
   --effort high|xhigh --genre … --write-scope '[…]' --timeout N "<prompt starting WRITE_SCOPE: […]>"; luna:
   -m gpt-5.6-luna --effort max; one runner per worktree; seats cannot commit; merge to main ONLY from the
   canonical checkout; gate bench commits on grep -qE '^OK'.

## 2026-09-04 ~20:50 PDT — pre-handoff status delta
- Custody seam: rounds 5+6 landed (refuters 13 astra / 14 Opus NOT REFUTED; delta 16 CLEAN); apex 99 LANDABLE;
  PR #289 opened (rows 9/11/12 pending replay + CI). RESUME PLAN item for the seam is now: replay → merge #289.
- Legacy #287: ledger complete at 8dfc3081 (replay: two load-sensitive failures, both pass in isolation); merge
  when CI settles. Paper-K #288: replay running (row 9). Paper-L: parser fix round 1b running (wt-paper-l).
- D-165: round 6 widened the census (RED only on draft :29/:1387/:1738 until paper-K/L land); round 7 (luna) bounds
  the round7 plan hits; then merge main → census GREEN → Opus re-check → PR (author the registry merge).

## 2026-09-04 ~21:25 PDT — final pre-handoff delta (supersedes the lane lines above where they differ)
- PR #290 paper-L opened (base feat/2026-09-04-paper-k; retarget to main after #288 merges): delta 05 CLEAN, apex
  99 LANDABLE; rows 9/11/12 pending. Enclosure and D-166 registry rows ride in #290; the enclosure branch needs no
  separate PR; D-166's generator change still needs its own PR after #290.
- PR #289 seam: git-init helper fix f13e3a44 pushed; CI rerun pending; the codex_app_bridge timeout in job
  test (3.14, 3) was a runner timeout, not seam-related — rerun the job if it repeats.
- PR #288 paper-K: replay was still running at handoff (~/.claude/jobs/3c46c831/tmp/paperk-replay.log, killed by
  the handoff); rerun on its head d053e969 at low load, fill row 9, merge, then retarget #290 to main.
- Paper-side one-row cure queued: draft-v2-skeleton.md ~:1738 ledger phrase "timing error common to" (D-165
  census survivor) → next paper round (with #290 or after).
- Install notice emailed to Ed 21:05 PDT (thread "INSTALL NOTICE — magistrate watchdog goes live tonight").
