ARM GATE on a staged night plan (JouleWise magistrate activation 3ba66eeb): the W2 derivation window of the macOS 25G83 calibration epoch.

READ-ONLY review. Do not modify, create, move or delete anything except your single answer file named below. Never run launchctl, sudo, powermetrics, install_night_agent.sh, any step*.zsh script, or any `python -m joulewise.evidence_night` subcommand. Never write under ~/Library/LaunchAgents or /Users/edr/night-custody. Reading is fine. Foreground only, no background tasks or subagents. Budget: 15 minutes. A missing answer file is a protocol failure: if a probe cannot finish, write the answer with it marked NOT EXECUTED. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files.

**Staged candidate:**
- `/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-w2-20260927/`:
  - `night_plan.json`, sha256 `0395a605…c0ce`;
  - `schedule.json`;
  - `render-context.json`;
  - `rendered-agents/*.plist` (night, dead-man, probe);
  - `battery-gate.txt` (the step-0 observation);
  - `arm-attempts/000001/` (plan snapshot, census, the notice body `notice-body.txt`, the unfilled `notice.json`).
  
  Digests of every staged file are in `09-staging-sha256.txt` beside this charge.
- Custody root: `/Users/edr/night-custody/d079-epoch-25g83-derivation-w2-20260927/`.
- Measurement clone: `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w2`, pinned head H = `a71a5e7999b5364e8477685b13c6a1e440fa7b27`. That is current main: the W1 harvest merge (PR #432), which carries ledger head pin 226 and W1's battery verdict.

**Arm scripts and their outputs:** `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/40-w2-arm/` (`scripts/`, `step0.out`, `step1.out`, `step2.out`, `step3.out`, `step3.err`, `arm-machine-state.txt`).
- They derive from the W1 scripts that armed W1 successfully, at `docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/scripts/`, whose W1 arm gate was ARM (`…/50-armgate/06-armgate-fable-verdict.md`).
- Diff the two script sets yourself. The intended changes are:
  - ids `w1` → `w2`;
  - H and T0;
  - `LEDGER_SOURCE` = the W1 measurement clone's 226-row ledger, with digest pin `b03be938…c63f`;
  - notice text: the W1 harvest line, NIT-1/3/6, the ordering departure and the d11 sentence.
- The W1 harvest record is `../00-activation-record.md` items 5–22. Its gate reports are in `../20-harvest-gate/`, including the cold Fable final pass `22-fable-finalpass-ruling.md`.

**The night:**
- a DIAGNOSTIC_NO_PACK derivation window under Revision 5 plus A-R5b (pre-registration sha256 `81b65f08…ddf1`);
- frozen calibration plan `9ab4776f…a072`;
- 600 s settle, then 12 slots at a 600 s cadence;
- t0 2026-09-27 09:00:00 PDT (1790524800); window_max_s 9000.

W1's window ended 03:00 PDT and its chain at 02:33:42, so the registration's "at least 6 hours apart" is met from either endpoint.

After you, the magistrate will:
1. send the notice to Ed and fill `notice.json` from the observed acceptance;
2. run `step4-publish-install.zsh`;
3. run `step5`;
4. exit before t0 − 8 min (08:52).

A Codex seat of this session (S1 test/code work in another worktree) is running now and appears in the census as `codex_exec` under the magistrate's own session root. It will be finished or stopped before step 4's final census and long before REQUEST.

**Answer each question with the executed probe that decides it:**
- **Q1 Bindings.**
  - Does the plan bind H as repo_head and measurement_head?
  - Does it bind the plan id, t0, window_max_s, the custody root and the measurement root above?
  - Is the clone's HEAD = H with a clean tree, and is the clone full (not shallow)?
  - Do the pre-registration, frozen-plan, protocol_v3, D-166 registration and both template digests in the notice recompute from the clone?
- **Q2 Ledger.**
  - Is the clone's ledger byte-equal to the W1 measurement clone's ledger, sha256 `b03be938…c63f`?
  - Is its authenticated head (226, `bd7aee7a…6693`) equal to `configs/calibration/calibration_ledger_head.json` at H?
  - Does `check --session-ids d079-epoch-25g83-derivation-w1-20260927` with the registration flags, run in the W2 clone, still authenticate W1's committed verdict (`battery=pass recorded=pass`)?
  - Is any other ledger on this machine a later head (check `/Users/edr/night-custody/measurement/*` and `/Users/edr/JouleWise-measurement-*`)?
- **Q3 Script changes.** Are the changes exactly the intended ones, and each no weaker than W1's check?
- **Q4 Wrapper and schedule.**
  - Does `chain.zsh` bind the plan and the clone at H, and match its sidecar?
  - Are the rendered calendars right (night: Month 9, Day 27, Hour 9, Minute 0; dead-man per the plan's derived time), and are the interpreter paths right?
  - Do the boundaries follow t0?
- **Q5 Notice.** Is anything in `notice-body.txt` false or stale? Quote any false line. The header address is a known alias; the notice goes to `claude2.glaring610@passmail.net`.
- **Q6 Science.** Anything else that makes arming unsound:
  - the battery gate (`battery-gate.txt`);
  - the 6 h spacing;
  - daytime operation. The window runs 09:00–11:30 local. Is there anything in Revision 5 or the plan about time of day? Ed's standing ruling is that quiet windows may run at any time the machine is census-clean.
  - the identity epoch and the T1 bindings;
  - the plan's relation to Revision 5 and A-R5b, including W1's 6/12 yield and the W3-on-count rule.

Tier each finding BLOCKER (no arm), MATERIAL (arm only after the cure) or NIT. End with a verdict line: ARM / ARM AFTER CURES (exact cures) / NO ARM. Keep it under 6 KB. Write it with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-27-activation-3ba66eeb/40-w2-arm/50-armgate/06-armgate-fable-verdict.md`.
