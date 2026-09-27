ARM GATE on a staged night plan (JouleWise magistrate activation 22784e38): the W1 derivation window of the macOS 25G83 calibration epoch.

READ-ONLY review. Do not modify, create, move or delete anything except your single answer file named below. Never run launchctl, sudo, powermetrics, install_night_agent.sh, any step*.zsh script, or any `python -m joulewise.evidence_night` subcommand. Never write under ~/Library/LaunchAgents or /Users/edr/night-custody. Reading is fine. Foreground only, no background tasks or subagents. Budget: 15 minutes. A missing answer file is a protocol failure: if a probe cannot finish, write the answer with it marked NOT EXECUTED. Do not read RUN_STATE.md, TASK_QUEUE.md, CLAUDE*.md, AGENTS.md, memory or skill files.

**Staged candidate:**
- `/Users/edr/night-plan-staging/d079-epoch-25g83-derivation-w1-20260927/`:
  - `night_plan.json`, sha256 `388420b5…02f5`;
  - `schedule.json`;
  - `render-context.json`;
  - `rendered-agents/*.plist` (night, dead-man, probe);
  - `battery-gate.txt` (the step-0 observation);
  - `arm-attempts/000001/` (plan snapshot, census, the notice body `notice-body.txt`, the unfilled `notice.json`).
- Custody root: `/Users/edr/night-custody/d079-epoch-25g83-derivation-w1-20260927/` (`calibration_plan.json`, `chain.zsh` + sidecars, `identity-epoch.json`, `t1-bindings.json`, empty `night/`).
- Measurement clone: `/Users/edr/night-custody/measurement/JouleWise-measurement-20260927-derivation-w1`, pinned head H = `97082508f3648ff8575c94b0cdfcf657ba440142` (current main).

**Arm scripts and their outputs:** `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/10-w1-arm/` (`scripts/`, `step0.out`, `step1.out`, `step2.out`, `step3.out`, plus the refused runs `step1-refused.out`, `step2-expectation-refused.out`, `step2-render-refused.out`). The original reviewed scripts are at git `c79816c9`, path `docs/process_traces/2026-09-25-activation-817355d2/10-w1-arm/scripts/`.

Four owner-approved script changes were made tonight; the reasons are in `../00-activation-record.md` items 4–14:
- (a) the ledger source is the n2 clone's 176-row ledger, with a digest pin;
- (b) the refused partial clone was archived;
- (c) the epoch-watch expectation is now `os_build` only, with the sampler row required to `match`;
- (d) the render label sets include the per-plan probe plist.

Diff the scripts against `c79816c9` yourself.

**The night:**
- a DIAGNOSTIC_NO_PACK derivation window under Revision 5 plus A-R5b (pre-registration sha256 `81b65f08…ddf1`);
- frozen calibration plan `9ab4776f…a072`;
- 600 s settle, then 12 slots at a 600 s cadence;
- t0 2026-09-27 00:30:00 PDT (1790494200); window_max_s 9000.

After you, the magistrate will:
1. send the notice to Ed and fill `notice.json` from the observed acceptance;
2. run `step4-publish-install.zsh`: re-checks, a fresh battery gate, `retry_allowed`, atomic publication, the real 300-frame launchd probe, install;
3. run `step5`;
4. exit before t0 − 8 min.

**Answer each question with the executed probe that decides it:**
- **Q1 Bindings.** Does the plan bind H as repo_head and measurement_head, and bind the plan id, t0, window_max_s, the custody root and the measurement root above? Is the clone's HEAD = H with a clean tree? Do the pre-registration, frozen-plan, protocol_v3, D-166 registration and both template digests in the notice recompute from the clone?
- **Q2 Ledger.** Is the clone's `runs/calibration_observation_ledger.jsonl` byte-equal to `/Users/edr/JouleWise-measurement-20260919-derivation-n2/runs/calibration_observation_ledger.jsonl`, with sha256 `95d152f0…5302` equal to `docs/process_traces/2026-09-19-activation-d0b83820/01-harvest-evidence/ledger-176-sha256.txt` at H? Is its authenticated head (seq 176, `0f7609ae…`) equal to `configs/calibration/calibration_ledger_head.json` at H? Is there any reason the n2 ledger is the wrong source (e.g. a later night appended rows elsewhere)? Check the other `/Users/edr/JouleWise-measurement-*` clones' ledgers.
- **Q3 Script changes.** Is each of (a)–(d) correct and no weaker than the original check? Is any other change present?
- **Q4 Wrapper and schedule.** Does `chain.zsh` bind the plan and the clone at H and match its sidecar? Are the rendered calendars (night: Month 9, Day 27, Hour 0, Minute 30; dead-man: Hour 4, Minute 5) and the interpreter paths right? Do the boundaries follow t0?
- **Q5 Notice.** Is anything in `notice-body.txt` false or stale? Quote any false line. The header address `claude.ai.copper531@passmail.net` is a known alias; the notice will be sent to `claude2.glaring610@passmail.net`, and Ed says both reach him.
- **Q6 Science.** Anything else that makes arming unsound: the battery gate (step 0 raw values in `battery-gate.txt`), identity epoch, the T1 bindings, and the plan's relation to Revision 5 and A-R5b.

Tier each finding BLOCKER (no arm), MATERIAL (arm only after the cure) or NIT. End with a verdict line: ARM / ARM AFTER CURES (exact cures) / NO ARM. Keep it under 6 KB. Write it with the Write tool to `/Users/edr/code/JouleWise-wt-22784e38/docs/process_traces/2026-09-26-activation-22784e38/50-armgate/06-armgate-fable-verdict.md`.
