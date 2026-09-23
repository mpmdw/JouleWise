# Cold-gate ruling 16 (Fable 5.1), activation f2d6899b — A234 fix round 2, A271 science fence, A271 blocker B1

Judge worktree `/Users/edr/code/wt-f2d6899b-coldgate` detached at `a74fa312`, 2026-09-23 11:13–11:3x PDT. One non-interactive session, foreground only, no subagents, no watchers, nothing committed. Scratch worktrees `/tmp/f2d6899b-judge-a234` (4c76ab69) and `/tmp/f2d6899b-judge-a271` (f81e34ec) were created for tests and removed at the end.

## 0. Contamination disclosure

Loaded beyond the packet, all by the harness before I acted: the user-level `/Users/edr/.claude/CLAUDE.md` (multi-model playbook names and the writing standard, no lane facts), the project `CLAUDE.md` at `a74fa312` (bridge policy), and the auto-memory index `MEMORY.md` (one-line pointers; it names lane A234, the 09-23 pilot harvest, D-183, and a memory titled "fseventsd cure passwordless"). I opened no memory file, no RUN_STATE.md, no TASK_QUEUE.md, no council log, no skill. Beyond the packet I read: `docs/decision_log.md` D-182 (lines 11958–12035 and the index row at 228), `docs/contracts/evidence_night_entry.md` slice B1 (lines 142–262), `configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json` and README lines 50–70, the code on both branches via the scratch worktrees, the base `plan_is_armed` at af879efb, and (read-only) the C5 rows of two archived receipts under `/Users/edr/night-archive/`. I did not read `/Users/edr/night-custody`.

## 1. Packet-hash check

`shasum -a 256 -c /tmp/f2d6899b/packet-shas.txt` from the judge worktree: all 16 entries `OK` (records 01–15 of this activation and `2026-09-23-activation-5fe5a59b/04-cold-fable-final-pass-aab8e004.md`). Packet diffs 14 and 15 are byte-identical to `git diff af879efb 4c76ab69` and `git diff 971e60d8 f81e34ec` (`diff -q` → `SAME14`, `SAME15`). Both branch heads exist locally as commits.

Baseline tests (scratch worktrees, `PYTHONDONTWRITEBYTECODE=1 …/.venv/bin/python -B -m pytest -q -p no:cacheprovider`):

```
4c76ab69  tests/test_magistrate_watchdog.py tests/test_arm_retry.py   139 passed, 222 subtests passed in 3.42s
f81e34ec  tests/test_corecaptured_loop.py tests/test_night_gate.py     86 passed, 138 subtests passed in 1.93s
```

The long modules (`test_evidence_night*.py`, `test_install_magistrate_watchdog.py`, `test_magistrate_watchdog_cli.py`) were NOT EXECUTED here (5–13 min each per records 02/06/12); the seat and both refuters report them green.

## Q1. A234 fix round 2 — is the census-backed, latched design sound?

### RULING

**Sound in shape; one more bounded fix round is the right spend.** The recurrence is not the same defect. Round 0 released with no census at all; round 1 censuses on every tick and latches one way. What the refuters found is that the census's *coverage* of the driver is incidental (F1) and that the *eligibility* input is a claim nobody writes (F3). Both are cured inside the present shape. Do not redesign around a durable driver-exit record or around waiting for the harvest.

Exact cures, each with the counterfactual it must be tested against:

**F1 — driver absence must come from a plan-bound driver probe, not from the courier path string.** Add a second probe to the release tick: `/usr/bin/pgrep -lf '[r]un_night\.py'` (bracketed like `AGENT_CENSUS_ARGV` so the probe never matches itself). Release requires the agent census AND the driver probe both empty on the same tick. Any live driver holds, not only this plan's: a foreign `run_night.py` on the box is itself a reason not to launch. I prefer this over a durable exit record because (a) it needs no `scripts/run_night.py` scope, (b) a record written by the driver at the end of `_finish_reporting` (`scripts/run_night.py:1795–1841`) is never written when the driver is killed or hangs after `courier.sent`, and a process-table probe covers every exit, (c) the installer renders the driver argv from the tracked template (`configs/launchd/com.joulewise.night.plist.template:9–10`), so the script path is a stable identity. Counterfactual input: process table with the driver argv `…/python3 …/scripts/run_night.py run --plan <root>/night_plan.json --courier-bin /opt/x/cl` (no `claude`, `codex` or `t3` substring anywhere) and an empty agent census, inside the nominal span, delivered zero-capture refusal → `decide()` must return `HOLD_CENSUS` and must not latch; the same tick with the driver row removed → `LAUNCHING` and the latch written. Executed today (§EVIDENCE): that first input returns `LAUNCHING`.

**F2 — bind the latch to the refusal instance.** `_release_key` must be `plan_id:custody_root:<sha256 of result.json bytes>`. The sha, not `ended_epoch_s`: a rewritten result with the same second would still collide, and the sha is what the courier already hashes for custody. Pruning stays as is (keys of unloaded plans drop). Counterfactual: state holds the latch for K1; `result.json` is replaced by a later refusal at the same id and root; census shows courier and driver alive → `decide()` must take a census (`census_calls` 1) and return `HOLD_CENSUS`, `plan_is_armed` True. Executed today: `LAUNCHING`, zero censuses, armed False.

**F3 — early release must require positive zero-capture evidence, and the watchdog must establish it itself from custody, not read it from the receipt.** D-182's words are "the successor route requires positive evidence of all three, never the mere existence of a refusal file" (decision_log.md:11994–11997). A bare `{"condition_id":"C5","measured":{}}` row is the mere existence of a refusal file in receipt form, and `terminal_zero_capture_refusal` accepts it (executed: `Decision(allowed=True)`, `decide()` → `LAUNCHING`). The cure is to make the watchdog observe the three facts on disk at release time: (1) `night/chain.started` absent and `result.json` has `chain_exit_code` and `chain_sha256` both null (already checked); (2) reservation absent: no `*.consumed.json` anywhere under the custody root (the marker the pack gate itself walks, `joulewise/night_gate.py:1030`); (3) capture writer did not run: the plan's `runs/instrument_validation` directory (the one D-182 names; `joulewise/arm_readiness.py:8170` builds it under `runs_root`) is absent or empty. The seat must resolve `runs_root` for the plan from the same code the gate uses and cite the line. The receipt keeps its veto role only (any positive claim of capture in any row blocks), never a licensing role. Add the receipt-derived clause to the docstring: a bare C5 row is neither evidence nor a veto. Because all three facts are on disk the moment the driver writes the refusal, **early release can fire before harvest, and the lane is worth landing.** It does not wait for the harvest.

Counterfactuals for F3, each run through `decide()` with an empty census and a bare C5 row: (a) a `*.consumed.json` present under the custody root → no release; (b) `runs/instrument_validation/<attempt>/anything` present → no release; (c) `chain.started` present → no release (exists); (d) all three facts clean → `LAUNCHING` and latch. Mutation: collapse each of the three disk checks to `True` individually; each mutant must fail at least one test.

A finding for the lead, outside this fix round's scope but load-bearing for the lane's purpose: nothing in production writes `zero_capture_evidence` (`rg -n zero_capture_evidence --type py -g '!tests/**'` at 4c76ab69 hits only `joulewise/arm_retry.py`; the only writer of `chain_started_absent` is `produce_g7_control` at `scripts/run_night.py:2187–2189`, a G7 control artifact). So `zero_capture_successor_allowed` refuses every live receipt with `missing_zero_capture_evidence` (executed on the bare row; and the two archived C5 rows I read carry only chain identity fields). The desk-side successor route is dead code until a harvest step writes that block, or until it is rewritten to the same on-disk facts as above. Early release alone frees the hold; it does not by itself deliver the 20-minute successor.

**S1 — restore the base tail for an undelivered chain-started refusal.** In `plan_is_armed`, the new branch `if _terminal_refusal_result(...) is not None: return now <= plan_completion_epoch(plan)` must become `return now <= plan_completion_epoch(plan) or (not courier.sent and now <= deadman_epoch(plan) + COURIER_LOCK_FRESH_S)`; equivalently, fall through to the base tail when `courier.sent` is absent. Counterfactual: chain.started + chain.exited + REFUSED result, no courier.sent, `now = completion + 60 s` → armed must be True (base) while the span is active. Executed today at head: span True, armed False, dead-man bound still ahead.

**S3 — docs.** In both paragraphs (`NIGHT_HANDBACK.md:57`, runbook `:1856`): gloss "on machine state" at first use as "one of the five refusal codes that describe the machine rather than the plan: an agent process present, not quiet (load, power, thermal, or one busy process), bind window expired, screensaver guard, boot clock"; define "tick" at first use as "one pass of the watchdog's periodic check, every `<interval constant>` seconds" with the constant's name; define "owner veto" as "a NO reply on the notice email thread" and "notice" as "the email that announces a plan before it is armed"; replace "while the plan's scheduled window remains open" with "from eight minutes before t0 until t0 plus the plan's `window_max_s` plus the five-minute courier deadline". Test: the first-use read, not a factual check (this packet proves factual passes miss it: record 10 S3 survived record 02's docs pass).

### REASONS

1. The shape is right because the release condition is now an observation (empty census on this tick) rather than a marker (`courier.sent`), and the latch removes the only feedback loop (the spawned magistrate re-holding itself). Both refuter blockers are about *what the observation covers* and *what the candidate set admits*, which are parameters of the shape.
2. F1 is a coverage defect, not a design defect: today the driver argv contains `/Users/edr/.local/share/claude/versions/…/claude` (record 10, executed by Opus), so the pattern `[c]odex|[c]laude|[t]3` matches it. Executed: the pattern matches today's argv and does not match a courier path without `claude`. Coverage by accident is not coverage.
3. F3 is the more important cure because the census cannot see capture; only custody can. Reading the facts from disk also removes the receipt-schema dependency that the docstring flags.
4. A durable driver-exit record would need `run_night.py` in scope and would still miss abnormal exits; a harvest-gated release would give up the entire point of the lane (the hold would run to the ~3 h nominal end while the harvest happens after the magistrate launches).

### EVIDENCE (executed)

Probe script `/tmp/f2d6899b-judge-probe_a234.py`, a subclass of `tests.test_magistrate_watchdog.FenceTests` at 4c76ab69, calling the production `wd.decide()`:

```
F1 driver_alive_but_unmatched -> LAUNCHING census_calls 1
F1 pattern matches today's argv: True ; matches a non-claude courier-bin path: False
F2 same_key_new_refusal_with_live_census -> LAUNCHING new census calls 0 armed False
F3 bare C5 terminal_zero_capture_refusal -> Decision(allowed=True, reason='terminal_zero_capture_refusal')
F3 bare C5 zero_capture_successor_allowed -> Decision(allowed=False, reason='missing_zero_capture_evidence')
F3 bare C5 decide (empty census) -> LAUNCHING
S1 undelivered chain-started refusal at completion+60: span_active True armed(head) False deadman+fresh bound True
```

Base `plan_is_armed` at af879efb (`git show af879efb:scripts/magistrate_watchdog.py`, lines 793–803): chain.started without chain.exited → True; courier.sent → False; else `now <= deadman + COURIER_LOCK_FRESH_S`. Driver locks: the only lock in `run_night.py` is `night/courier.lock` (lines 1281–1304, removed at 1561); there is no driver pid file or exit marker. Census pattern: `joulewise/night_gate.py:162`. Plist argv: template lines 9–16.

### REQUIRED TESTS (all through `decide()`, each failing at 4c76ab69 and passing after)

1. F1 hold-then-release pair above (driver argv without any census substring).
2. F2 same-id/same-root replacement with live census → `HOLD_CENSUS`, census taken, armed True.
3. F3 (a)–(d) plus the three single-fact mutants.
4. S1 undelivered chain-started refusal at completion+60 → armed True.
5. Opus N1: the chain-field guard in `terminal_zero_capture_refusal` (`arm_retry.py:216`) gets a test that fails on `if False`.
6. Existing 139 + 222 stay green; the seat re-runs the long modules and the lead replays the full suite at the fix head (record 09 §1 covers 31124f68 only).

## Q2. A271 science fence and the t0 detection-only ruling

### RULING

**(a) Admissible machine-state gate, not an amendment of the pinned pilot registration; Ed's ratification is not required.** Conditions: record it where the precedent recorded the 0.5-busy-core rule (a field in `pilot_protocol_v3.json`, e.g. `t0_corecaptured_spawns_max: 2`, and this ruling's id appended to the `ruling` string), update the four stale texts Opus S1 lists (`arm_retry.py:31`, `NIGHT_HANDBACK.md:84`, the entry contract's check-row inventory, README:60), and have the next arm notice name the new refusal in plain words so Ed's standing veto covers it.

**(b) The magistrate's t0 detection-only ruling (record 05) is sound.**

### REASONS

1. What `pilot_protocol_v3.json` pins is the science of a captured night: envelopes, pairing, exclusions, sizing, the observer floor, `start_drift_abort_s` and the per-envelope `non_observer_process_busy` bar. A t0 refusal captures nothing, so it changes no estimator, no exclusion and no sizing. Selection on pre-capture machine state cannot bias the paired contrast; it only decides whether tonight's data exist.
2. D-182 already classes `night_refused_not_quiet` as a machine-state code eligible for the successor route, and its "what this does not change" paragraph keeps only physics, evidence and pre-registration refusals fail-closed. A loop detector is machine state.
3. Precedent: the 0.5-busy-core t0 predicate entered the protocol in commit `c8e6408b` on the authority of cold gate QPE01-DAEMON-CONTAMINATION-01 (rulings 10, 21, 31) with no Ed ratification line, and the protocol's `ruling` field cites those gates. The corecaptured gate guards the same contamination (fseventsd pegged by the respawn loop) one step earlier in the causal chain.
4. The threshold is instrument-sized: a looping machine shows one spawn per ~80 s (record 09 §3: 605 spawns in 24 h, maximum 8 per 10-minute window), a quiet one shows 0 (live read count 0). "More than 2" leaves a margin of at least four events on either side.
5. On (b): a Wi-Fi toggle plus a 180 s wait at t0 moves the collector start by more than the registration's own `start_drift` exclusion tolerates (10 s from the frozen schedule) and would either abort under `start_drift_abort_s` or exclude envelopes; it also actuates the radio and, on the fallback path, kills `fseventsd` inside the agent-free window. The arm check runs with slack before install close and is the right place. The lane row is a registration of intent, and the seat brief invited the seat to disagree with evidence; the seat (record 04) reached the same design independently.

### EVIDENCE

`pilot_protocol_v3.json` keys read this session: `cadence_exclusion = "start_drift: absolute collector start drift greater than 10 s from the frozen schedule"`, `t0_non_observer_share_max = 0.5`, `ruling = "cold gate 10 Q1/Q2 (2026-09-19); adjudication 10a; sizing ruling 46b; A269 cold gate 10 (2026-09-22) …; cold gate 10 QPE01-DAEMON-CONTAMINATION-01 (2026-09-23) Q1(c)/Q2/Q3(a)"`. `git log -S't0_non_observer_share_max' -- …/pilot_protocol_v3.json` → `c8e6408b`, body: "Authorities: cold gate QPE01-DAEMON-CONTAMINATION-01 rulings 10 (Q1(c)/Q2/Q3(a)), 21 and 31, syntheses 15, 25 and 35". D-182 terms paragraph, decision_log.md:11983–11997. t0 block at f81e34ec `joulewise/night_gate.py:1505–1528` (read-only, `not_measured` on failure, refuse on `count > 2`). Sealing: `evidence_night.sealed_candidate` (lines 234–268) hashes the registration bytes per candidate; no plan is armed (earlier cold verdict §"Uninstall"), so editing the protocol file drifts nothing sealed.

### REQUIRED TESTS / ACTIONS for the A271 landing (these accompany Q3's PR)

1. Sol A271 F1 (blocker, `night_gate.py:1515`): read the clock BEFORE issuing the log read and anchor the 10-minute window at that instant; keep lines timestamped after it. Counterfactual: three spawns at 590, 300 and 1 s before the read with a 30 s read duration → still refuses.
2. Sol A271 F2 (blocker, `evidence_night.py:849`): every arm actuator command gets a timeout (`probe_command(..., timeout=…)`; the log read 30 s, `networksetup` 30 s, the restart 60 s) and a timed-out `off` still reaches the `on` attempt. Counterfactual: hanging `off` → `on` issued, check refuses.
3. Opus S4: post-toggle persistence threshold `>= 1` new spawn in the 180 s wait (a cured loop shows 0; at a 95 s period `>= 2` misses ~10 %).
4. Sol A271 F4 / F3: kill the surviving `> 2` → `>= 2` and `<= 2` → `< 2` mutants with exactly-two boundary tests; tolerate a trailing blank line in the parser.
5. Opus N3 stays as a recorded latent risk (arm-to-t0 under ~13 min would let pre-toggle spawns into t0's window); no code change while the lead is 40 min.

## Q3. A271 blocker B1 — amending contract §B1 "the one move"

### RULING

**May land in the same PR under the normal gate plus a cold Fable final pass. No separate ruling.** Conditions:

1. Actuation (Wi-Fi off/on, `sudo -n /usr/local/sbin/joulewise-restart-fseventsd`) runs only when item 0 passed (`nothing_loaded` true: no night label loaded, no plist or sidecar present, discovery known) AND every earlier check row passed (`not failed` at that point, which includes `retained_roots` reporting no active span and the census row clean). Otherwise the corecaptured row is read-only: count recorded, `remediation: "not_licensed"`, verdict fail on `count > 2`.
2. The contract line at `docs/contracts/evidence_night_entry.md:175` is replaced by an enumeration: "`check` makes at most three machine moves, each at most once per invocation and each only after item 0 and every earlier row passed: (1) the fast-forward-only pull of the canonical checkout (item 1, D-183); (2) one Wi-Fi power off/on cycle (`networksetup -setairportpower en0 off`, 8 s, `on`) when more than two `corecaptured` spawns were counted in the last ten minutes; (3) one `sudo -n /usr/local/sbin/joulewise-restart-fseventsd` when new spawns persist 180 s after that cycle. Every move and its exit code is recorded in `check.json`." Add the corecaptured row to the check-row inventory with its side effects.
3. Counterfactual tests through `check()`: (a) night label loaded + 5 spawns → `REFUSED: night agents already loaded…` and zero actuator commands issued (Opus's executed probe shape); (b) census row failed + 5 spawns → refusal names the census, zero commands; (c) all earlier rows pass + 5 spawns → exactly one off, one on, and the restart only on persistence.
4. The cold Fable final pass reads the amended line against the code path (`evidence_night.py:1054–1079`) and the tests in 3.

### REASONS

1. The authority to actuate at arm time is not new: the lane text itself places the toggle in the arm check, the seat brief (record 03 §1) cites the owner-session record for the 01:41 Wi-Fi cure and the passwordless restart route, and the magistrate's design ruling (record 05 (b)) specified the exact commands. The contract line is a description of what `check` does, and the slice's own header calls B1 "a mechanical façade for the lead's bench procedure". Keeping a description true to licensed code is the normal gate's job.
2. The hazard Opus B1 names (toggling the radio or killing `fseventsd` while a window is armed or running) is exactly what condition 1 removes; the D-183 pull already uses the same licence shape ("With item 0 failed the pull is not licensed and the check refuses without moving anything", contract item 1). The amendment generalises an existing rule rather than creating a new class of authority.
3. A separate ruling would be needed only if actuation were moved outside `check` (t0, watchdog, courier), if any sudo route beyond the single allowlisted command were used, or if the toggle were to run when a night is loaded.

### EVIDENCE

`joulewise/evidence_night.py` at f81e34ec: `nothing_loaded = inspect("night_agents", …)` at 1055; `inspect("corecaptured", …)` at 1077 is gated only on `payload_kind == KIND` (1076), not on `nothing_loaded` or on `failed` (source read; Opus's counterexample in record 13 executed it: loaded label → commands `networksetup off`, `networksetup on`, `sudo -n …` issued). `probe_command` default `timeout=None` (598–601). Contract text at 175 and item 1's "not licensed" sentence (lines 175 and 197–200).

## Dissent risks

1. **Q1, F1.** A reviewer may hold that a second `pgrep` is still a string match and that only a driver-written exit record is "durable". I weighed it: the exit record is absent on every abnormal exit, which is precisely when a live driver matters most; the process table is the ground truth for "alive". If the lead wants both, the record is additive, never a substitute.
2. **Q1, F3.** A reviewer may read D-182 as requiring the *receipt* to carry the positive block. I read it as requiring the facts to be established, and the watchdog reading custody directly is stronger than a receipt claim written by the same driver. The lead should also decide who writes the harvested block, or the desk-side successor route stays unreachable.
3. **Q2.** A stricter reading says any change to t0 admission of the pinned pilot is an amendment for Ed. The precedent (0.5-core rule on cold-gate authority) and D-182's classing decided me; the notice email is the veto point, and if Ed objects there the gate is removed before the next arm at no science cost.
4. **Q3.** Someone may prefer a standalone contract ruling because the sudo restart kills a system daemon. The command is the owner-provided allowlisted route, runs at most once, only when nothing is loaded and no span is active, and is recorded; that is within the normal gate plus cold final pass.
5. **Not executed:** full suites at either head; live `pgrep`, `log show`, `networksetup` or `sudo`; the long test modules; the Opus B1 counterexample script (I confirmed it from source instead); the log-read duration.

Judge: Fable 5.1, cold, session ended after this file was written and the scratch worktrees removed.
