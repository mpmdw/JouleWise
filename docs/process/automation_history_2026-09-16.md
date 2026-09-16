# Fully automatic measurement windows: the work it took (2026-08-08 → 2026-09-16)

Written 2026-09-16 from the checkout at main `11ea57db`. Every number supporting the account is cited to a repo path;
anything not verifiable in the checkout is marked `ASSUMED:` inline. Written for a systems researcher who has not
opened this repository.

## 1. What "fully automatic window" means, and the four invariants

A **window** is one scheduled, agent-free period in which the machine runs a measurement chain (a zsh script of
capture steps and pauses) under `powermetrics`, with nothing else alive that could add joules. A **plan** is the JSON
record (`joulewise.night_plan.v2`) that fixes the window: `t0_epoch_s` (the start), `window_max_s` (the span cap;
9000 s for a calibration-derivation night, 900 s for a stub rehearsal with no acquisition), the frozen checkout triple `(plan_id, measurement_root, head)`, the
evidence directory (**custody root**, retaining the night's records), and the chain's SHA-256. **Arming** is the act of
publishing that plan where the supervisor will find it and installing two launchd jobs from it: `com.joulewise.night`
(fires at t0, runs `scripts/run_night.py`) and a completion-timeout (**dead-man**) job, `com.joulewise.night.deadman` (fires after the
planned completion and records a failed check or stops anything still alive). "Fully automatic" means no human types anything
between the decision to run and the harvested result. Two unattended agent sessions author the plan, send its notice, arm it, execute it, collect its results and
retire it: the headless supervisor (**magistrate**, `claude -p`, launched by
a user LaunchAgent) owns planning and adjudication; the result-publishing session (**courier**) is spawned by the night driver
after the chain exits to push the results branch and email Ed.

Four invariants survive every mechanism below; each later section is a way of making one of them true by construction:

1. **No capture with an agent active.** The admission check runs a process-table scan (**census**) at t0
   for agent runtimes (`pgrep -lf 'codex|claude|t3'`) plus load, HID-idle, boot-clock and custody guards; any hit
   rejects the night (a **refusal**) and no chain starts (`docs/phase_2/derivation_night_runbook.md` §0.6). The magistrate must
   therefore be gone before t0. The agent-free interval (**plan span**) runs from `t0 − PLAN_LEAD_S` through
   completion; inside it the session-relaunch supervisor (*watchdog*) refuses to launch a magistrate (`docs/process/MAGISTRATE_WATCHDOG.md` §Fence and
   deadlines).
2. **Publication is the single irreversible instant.** The plan is staged outside the watchdog's `*/night_plan.json`
   discovery glob, validated there, and moved into the custody root by one atomic `os.replace`; everything before it can
   be abandoned without trace and everything after it is a re-arm (runbook §1.4 step 5, "the one irreversible
   instant"; the eight conditions in `docs/decision_log.md` D-175).
3. **Every refusal is a printed result.** A **refusal** is a gate declining to proceed; at any stage it writes a
   record (`night/refusal.json` at t0, an `outcome.json` per arm attempt, a typed exit code from the installer) and the
   next reader classifies from that record, never from an absent success (`scripts/run_night.py` `REFUSAL_SCHEMA`;
   `joulewise/arm_retry.py` `classify_abort`).
4. **Plan frozen and hashed before data.** The plan pins `repo_head = measurement_head = H`, the chain's sha256 sidecar,
   and the pre-registration path; the harvest re-derives the chain from the clone and compares bytes before reading any
   result (runbook §2.0; harvest records under `docs/process_traces/2026-09-1*-activation-*/01-*harvest-record.md`).

A queued work item is a **lane** (`TASK_QUEUE.md`; multi-span installation is `INSTALL-WINDOWS-MULTI-01`);
a delegated model session working as implementer, reviewer or consultant against a brief is a **seat**.
An independent adjudication (**cold gate**) uses a fresh model session with no implementation-history context and a
mechanically assembled evidence packet; citations identify its rulings by packet number.

## 2. Dated timeline

### 2.1 Charter (2026-08-08)

The autonomous-window decision (`docs/decision_log.md` D-127) authorised the loop (collect results → compute and freeze a resolution bound (*floor*, the largest false difference the instrument can produce) → adjudicate → build the next
pre-registered campaign file set → launch → exit for capture → relaunch a fresh headless session), retaining the prohibition on agents during capture
and a relaunch sequence of preflight → launch → liveness proof → bounded retries → independent launchd
fallback timer ("never one mechanism"). The standing-run mandate (D-128) ratified it the same day: run the loop until
the paper is defensible (D-127 items 1, 2, 4; D-128 item 1).

### 2.2 The hands-free week and the watchdog (2026-09-02 → 09-08)

Ed left for up to a week on 2026-09-02. The hands-free ruling (`docs/decision_log.md` D-171) delegated the launcher
invocation, the evidence-digest step, transaction authorisation and watchdog installation; stand-down margin 5 min before t0
("30 min … seems too much"); machine state: lid open, AC, FileVault on, so "an unplanned reboot halts everything until
someone types the disk password (accepted)" (D-171 items 1–4, 7, closing paragraph).

The **watchdog** (`scripts/magistrate_watchdog.py`, user LaunchAgent `com.joulewise.magistrate`, tick at load and every
300 s, resident supervisor at 10 s resolution) was designed through consultation with three independent agents, built, reviewed adversarially twice and
adjudicated by a cold gate (hands-free-week trace records 02–20), landed on PR #284 (`TASK_QUEUE.md` WATCHDOG-BUILD-01 row) and
installed on 2026-09-06 by the interactive magistrate, whose process was then terminated as designed (`RUN_STATE.md` checkpoint T36). The
first watchdog-owned activation came only at 2026-09-08 00:51:55: the watchdog had remained in `CLOCK_UNCERTAIN` since 09-06
03:36 because the closed lid put the MacBook into Maintenance Sleep every ~5 min and wall/monotonic deltas disagreed
(`docs/process_traces/2026-09-02-hands-free-week/21-first-launchd-activation-1ef89702.md`, seq 1–4). That activation hit
the 600 s background-task ceiling at 01:33:28 and the watchdog relaunched a successor at 01:41:58 after the 300 s
cooldown (`RUN_STATE.md` checkpoint T38). Also 2026-09-08: the relaunch prompt was amended so a headless magistrate may
arm a stub rehearsal (stage outside the glob, `--render-only` from the pinned checkout, `os.replace`, install from that
checkout, email the fixed plan identifiers before the move, no other agent alive), and the authorisation receipt and evidence-digest step for measurement nights were
fixed (`docs/decision_log.md` D-175, D-176).

### 2.3 Stub rehearsals and their failures (09-09 → 09-15)

A stub (`REHEARSAL_STUB`) uses a built-in three-second script to exercise launchd, admission checks,
courier and result collection without acquiring data. Each rehearsal exposed a different integration failure:

- **The first stub rehearsal** (rehearsal-20260909; fired 02:56 09-09): verdict `REHEARSAL_ONLY`, chain exit 0, results branch
  `night-results/20260909`, but the receipt read `REFUSED night_probe_error` because the gate tried to read a chain
  sidecar a stub does not have. Fixed in PR #309 (lane NIGHT-GATE-STUB-CHAIN-01; `RUN_STATE.md` T38d/T38e).
- **The interpreter-failure rehearsal** (rehearsal-20260911; t0 02:56 09-11): the driver crashed in its first second. The plist ran `/usr/bin/env python3`
  under launchd's `PATH`, which resolved to `/usr/bin/python3` = 3.9.6, and `joulewise/arm_readiness.py:26`
  `from datetime import UTC` raised `ImportError`. At 07:00:02 the dead-man's census found an orphaned Claude daemon tree
  (pid 83102, parent session already gone) and wrote `night_refused_agent_present`. Cure: the plist pins the clone's
  interpreter (lane NIGHT-INTERPRETER-PIN-01;
  `docs/process_traces/2026-09-11-activation-58a3bcfc/01-rehearsal-20260911-harvest-record.md`).
- **The first complete rehearsal** (rehearsal-20260912; t0 00:30 09-12, clone at `a7d1eb88` with the 3.13 pin): driver started 00:30:04.29, gate
  `REHEARSAL_ONLY` at 00:30:04.76, stub chain exit 0 at 00:30:07.09, `launchd.night.err` empty, courier email
  `1a09487237fa6be2`; the courier harvested and retired the night itself because the magistrate was not alive
  (`docs/process_traces/2026-09-12-courier-rehearsal-20260912/01-rehearsal-20260912-harvest-record.md`). First end-to-end
  pass of the unattended chain.
- **The first science night**, checking whether calibration remained valid after an OS change (n1-20260913; ordered by issue #316): fired 02:56:02, REFUSED
  at t0 because Ed's interactive session (pid 24974) and the ChatGPT desktop app's bundled Codex helper were in the
  census (`docs/process_traces/2026-09-13-activation-c5048879/01-equivalence-night-20260913-harvest-record.md`). The
  09-14 03:00–06:30 install span then closed without an arm because the arm-time census never cleared
  (`docs/process_traces/2026-09-13-activation-24b9d3dd/49-no-arm-record-n1-20260915.md`).
- **The next science attempt** (n1-20260915): Ed's directive (issue #336) authorised an evening install; the plan was armed 16:45:46 09-14 after Ed closed his
  session and the census went clean at 16:44:13 (`…24b9d3dd/52-arm-record-n1-20260915.md`); fired 02:56:03 09-15 and was
  REFUSED on load alone: 1-min load 2.55 > 2.0 with a clean census. The load was `fseventsd` (pid 553) at ~184 % CPU
  with 4721 CPU-minutes over 12 days of uptime
  (`docs/process_traces/2026-09-15-activation-1acf2aee/01-equivalence-night-20260915-harvest-record.md`).

Two rulings came out of these nights. The **arm-retry ruling** (`docs/decision_log.md` D-180; Ed, 2026-09-10, after
the 09-10 arm was blocked by two idle interactive sessions): permitted installation intervals recur within a day; a pre-authorised retry
class exists for non-physics arm aborts (idle interactive session, stale notice hash, watchdog
`CLOCK_UNCERTAIN`/`NETWORK_UNCERTAIN`, transport failure); idle interactive sessions do not block a stub's
arm-time census (D-180 items 1–3). The **any-time-windows ruling** (D-181; Ed, issue #337, 2026-09-14 16:43): windows
run whenever the machine is quiet, day or night, several per day, no cadence rule; the fixed daily minute inside the
02:45–03:30 belt and the calendar-day install span were "a mechanism limit, not a scientific one"; three work items went to
the top of the queue in order: multi-span installs, the retry class, and the idle-interactive census exemption
(INSTALL-WINDOWS-MULTI-01 → ARM-RETRY-CLASS-01 → ARM-CENSUS-IDLE-INTERACTIVE-01; D-181 clause 1).

### 2.4 Census and refusal semantics

The t0 census matches helper processes of the desktop apps that bundle an agent runtime (ChatGPT's `codex … app-server`,
the Claude app's helpers) and does not match the apps' top-level processes; the ruling kept the pattern rather than
narrowing it (runbook §0.6; lane NIGHT-CENSUS-CHATGPT-APP-01 in `TASK_QUEUE.md`). An earlier arm-time browser probe
matched Apple's always-present Safari XPC services and could never pass; a cold gate fixed the matching patterns (cold gate
34; lane ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01, `TASK_QUEUE.md`). Refusal codes are an enumerated set:
`night_refused_agent_present`, `_not_quiet`, `_hid_idle`, `_boot_clock`, `_registration`, `_class_unbuilt`
(`joulewise/night_gate.py:103-109` per `docs/process_traces/2026-09-15-activation-08ca8197/06-refusal-fast-retry-lane-registration.md`).
A status publisher (`scripts/window_status.sh`) may not run while a recorded chain or campaign is live or its
liveness is indeterminate (`docs/contracts/window_liveness.md` §1–§2).

### 2.4a Shrinking the security scope back to sensible (08-27 → 09-13)

Checks against actors excluded by the threat model had blocked automation. Three rulings limited these checks to
measurement protection:

- **Threat-model prune (Ed, 2026-08-27, "yes to all 3. right instincts"; `docs/decision_log.md` D-161).** The
  in-process adversary was already out of the threat model (earlier decisions D-139 A1, D-148 (6)) and the paper's §7
  states a single trusted operator, so file-integrity mechanisms designed only to prevent deliberate modification by that operator
  exceeded the threat model: that week they required three manual edits and blocked resolution-bound issuance twice. Rulings: the reviewed set of fixed values
  gets a reviewed update procedure (REVIEWED REFRESH LANE) (`--refresh-row`, re-derived by the verifier's own code path, diff printed, lands
  as a PR) and "no update lane" becomes "no UNREVIEWED update"; a review of unnecessary checks (THREAT-MODEL-PRUNE-01) enumerates every
  refusal whose only actor is the trusted operator and downgrades it to warn-and-record or retires it; fail-closed
  behaviour STAYS for measurement validity, evidence or pre-registration (missing calibration, unresolved clock alignment, absent
  floor, stale drift evidence, unfrozen plan, post-hoc analysis choice); the repository is tamper-EVIDENT for the
  operator's benefit, not tamper-PROOF. The addendum's operative test: MISTAKE vs DELIBERATE, guard against mistakes,
  retire deliberate-only guards (`docs/decision_log.md:207` index row; `:10685-10696`).
- **Sensible gates (Ed, 2026-09-10 ~04:20).** "make sure there are no silly gates on accepting numbers … recall that
  time where you wanted a tolerance of like 1e-15 sensitivity or something ridiculously microscopic compared to the
  measurement". Every tolerance on the claim path is sized to the instrument, boundary-attribution limit ≈ 1 J and minimum difference required for a claim
  ≈ 5 J (`docs/decision_log.md` D-078 cl.11), never to decimal places; measurement-validity and evidence refusals stay. The review of measurement checks
  (lane GATE-SENSIBILITY-SWEEP-01) inventoried 299 gates and merged three repairs (R1/R3/R4) plus the prefill probe's idle setting (G2-a `idle_seconds 75`) in
  PR #314 (`0d4bb4fb`), and sent the zero-point band (an `isclose(rel_tol=1e-9, abs_tol=1e-12)` comparison of two
  binary64 routes over the same four numbers, D-165) to a cold gate, which ruled it scale-bounded: sound below 8,192 J
  per run and not a blocker for the prefill probe (G2-a; cold gate 47; the directive is recorded in the assistant memory file
  `sensible-gates-directive.md`; `TASK_QUEUE.md` GATE-SENSIBILITY-SWEEP-01 row; `docs/decision_log.md` D-124 addendum
  2026-09-13). ASSUMED: the 1e-15 figure is Ed's recollection; the log shows a 1e-15 s quantization at
  `decision_log.md:6667`, not a 1e-15 J tolerance.
- **The census fence that survived (2026-09-13).** The question was whether the t0 census should stop refusing on the
  ChatGPT desktop app's bundled Codex helper (lane NIGHT-CENSUS-CHATGPT-APP-01). Ruled option (i): keep
  `codex|claude|t3`; desktop apps that bundle an agent runtime count as agents; the operator quits both apps before
  every plan span (PR #334, `8980f85a`, cold gate packet 05 paired with an Opus reviewer; `TASK_QUEUE.md` row). It
  remained because a helper can start inference or a build inside the
  measurement window.

### 2.5 The 09-15 restart: what 13 days of unattended operation left behind

At 19:45 PDT 09-15 the machine had `fseventsd` at ~61 GB RSS and ~190 % CPU after 12 d 23 h up (boot 09-02), load 8.8,
~100 GB of local churn: 314 git worktrees under `~/code` (121 detached, 154 on already-merged branches), ~540 `iw-*`
test-matrix directories in `/private/tmp` (18 GB), `$TMPDIR` 39 GB, and 35 orphaned `vllm serve /fake/model` fixture
processes (10–12 days old, from `tests/test_node_worker_subprocess.py`, leaked when the test parent died)
(restart note `~/.claude/projects/-Users-edr-code-JouleWise/memory/checkpoint-2026-09-15-restart-fseventsd.md`;
`docs/process_traces/2026-09-15-activation-08ca8197/00-launch-record.md`; the memory index says 312 worktrees, the
09-15 census says 314). Ed restarted at 19:55; the interactive session opened 19:58 and pruned 314 → 76 worktrees
(`docs/process_traces/2026-09-15-interactive-b0ae8462/00-session-record.md`, seat 05). Follow-up work was registered for worktree
pruning, detection of orphaned test fixtures (queue rank A208), and temporary-directory cleanup.

Two other operational facts were established the same morning. Headless `claude -p` exits when the model ends its
turn, and the exit kills every `run_in_background` task; two headless activations each ended a turn with "the seats
will wake me" and lost all three delegated sessions within minutes. The watchdog logged both as `clean activation exit` (exit 0,
300 s cooldown), but `state.json` still read `last_exit_class: usage_exhausted` from 09-09 because the clean path never
resets that field (`scripts/magistrate_watchdog.py:1714-1723` sets backoff indices and transitions to IDLE without
touching `last_exit_class`; only `apply_backoff` at `:1372` writes it), so the next reader saw "usage" (recorded in the
assistant memory file `headless-turn-end-kills-seats.md`). Earlier, on 09-10 08:41, the Codex weekly quota fell after
~20 GPT-6 (Astra) delegated sessions in one activation and the Claude 5-hour limit fired at 09:46 during parallel Opus work; Ed restored
Codex usage ~21:25 (memory file `codex-usage-limit-2026-09-10.md`).

### 2.6 The transactional installer: why four zsh rounds failed, and the redesign

`scripts/install_night_agent.sh` installed the two LaunchAgents: render two plists → bootout priors → bootstrap night →
bootstrap dead-man → verify → succeed; plus `--uninstall` and `--render-only`. The two rulings of §2.3 made its
preconditions time-varying (install only inside a listed span and before `install_close_epoch`) and every mutation changes
machine state read by an installation check: `installed_agent_fence` decides from the two plist files whether a plan is armed
(`docs/process_traces/2026-09-15-activation-d6888966/33-brief-redesign-consult-transactional-installer.md`, forcing problem).
Two defect classes were named: **class 1**, exiting 0 with a job loaded but no clock read after the last mutation
below `min(selected_span_close, install_close_epoch)`; **class 2**, ending with a job loaded and its plist absent (a state invisible to that
check), or exiting 0 while a label it tried to bootout is still loaded.

Rounds 1–3 in zsh each fixed a defect at one site, only for the same failure class to appear at the next: final bootstrap → a
`set -e`-skipped EXIT trap → post-gate `rm -rf` → `--uninstall`. A cold gate reproduced the underlying shell behaviour: zsh 5.9
`set -e` inside a function returns rc 1 with the EXIT trap NOT fired, and `always` blocks do not run either. It also
rejected a `MAX_INSTALL_DURATION_S` ceiling as an invented number ("bounds are observed, not predicted") (cold gate 25,
`…d6888966/25-coldgate-packet-install-windows/10-coldgate-fable-ruling.md`, probe table and Q2). The next cold gate
tested the round-3 commit: a failed `rm -rf <backup>` after the commit gate tore down a verified arm (rc 1, both labels
booted out), and `--uninstall` with both bootouts failing exited 0 with both jobs loaded and no plists, so
`installed_agent_fence() = None` (cold gate 28,
`…/28-coldgate-packet-install-windows-round-3/10-coldgate-fable-ruling.md`, Q1b, Q2a). The mechanism: every
verification re-read was `launchctl print … >/dev/null 2>&1 &&`, so ANY non-zero exit read as "not loaded", but only a
not-found code means that; an error code means unknown, and unknown must mean loaded. The stub `launchctl` in the tests
emitted only 0/1 and could not express unknown, which is why the tests never saw it (the delta-3 stop record
`…/lt-21-delta-3-stop.md` F2; the Opus design seat `…/lt-22-opus-design-seat-transactional-installer.md` Q3).

The agreed stop condition required no further judgment at the third incremental review (delta 3; head `073a9763`, 11:42 09-15): both late-success and missing-plist defects remained (class 1 YES, class 2 YES),
so the ruling was "no fix seat, no round 4" (delta-3 stop record). At 11:48 a consultation with three independently briefed agents (GPT-6 Astra at xhigh effort,
Claude Opus, Claude Fable) was asked one question: keep zsh and fix the predicate at three sites, or a Python
transaction module. All three chose the module (consult records `33a/33b/33c`). The Opus design specified four mechanisms:
one mutation channel (`write_plist`, `bootstrap`, `bootout`; nothing else touches `launch_dir` or launchctl); the clock
gate as a precondition of the mutator, not a statement between mutators; teardown dispatching on transaction state,
never on `$?`; proof-carrying deletion, where `require_absent(label)` raises on LOADED and UNKNOWN and `remove_plist`
takes the `Absent` token (Opus design seat, Q1 devices 1–4). Liveness became three-valued from an executed probe:
`launchctl print gui/501/<missing>` exits 113 with stderr `Could not find service "<label>" in domain for user gui:
501`; rc 0 → LOADED; rc 113 with that exact line → ABSENT; anything else → UNKNOWN (Opus design seat, Q3; live code
`joulewise/night_agent_install.py:274-280`).

The engine (`joulewise/night_agent_install.py`, system Python 3.9, states PARSED → VALIDATED → ADMITTED → STAGED →
PUBLISHED → NIGHT_LOADED → DEADMAN_LOADED → VERIFIED → COMMITTED → SUCCESS; terminal REFUSED / ROLLED_BACK / RETAINED,
`:351-364`) then went through rounds 4–5 (pre-restart), the restart, and rounds 5–8b in the interactive session. Rounds
5 and 6 were two consecutive rounds on one signature, signal handling: the handler raised from inside the signal
frame, the mask was left blocked, teardown was skipped. The independent review allowed round 6 as the LAST repair attempt for that failure class (round-6 cold gate).
Its STOP CONDITION required any further signal-class defect in the incremental re-audit to trigger independent
consultation on replacing raise-from-handler with record-and-poll, with no round 7
(`…interactive-b0ae8462/06-coldgate-packet-install-windows-round-6/10-coldgate-fable-ruling.md` Q3). The execution-based review
sent real SIGINT/SIGTERM/SIGHUP at every transition under Python 3.14.7 and 3.9.6 on `efdaed87`: the final signal-mask restoration failed 60/222 per
interpreter (seam e), because a signal queued after its original disposition was re-installed was delivered at the final
`SIG_SETMASK` with that disposition and killed the process AFTER the result was complete (trace record `08f`). The
signal-redesign consult convened 22:58; by 23:10 two of three reviewers had converged with executed probes on the same
design: the handler only RECORDS one integer, ordinary code polls at every state boundary and before every mutation,
the last poll after the clock predicate is the commit latch, no `pthread_sigmask` anywhere, `SIG_IGN` from the end of
teardown to process death, teardown never polls. The Opus seat added the physical finding that the round-5/6
`SIG_BLOCK` in the handler was inherited by every launchctl child spawned afterwards, so the teardown's SIGTERM never reached the child (only SIGKILL, which cannot be blocked, would have)
(`13-consult-signal-redesign/03-magistrate-adoption.md`). The commit-latch repair (round 8b) removed the contradictory second poll in `_commit`, leaving
this sequence: predicate on the clock read → the last poll (latch) → direct assignment of COMMITTED; a signal during the
clock read rolls back with the signal's code, a signal after the latch is ignored (trace record `08j`; live `:459-464`).

The repaired installer (round 8) landed at `d5ec18bb` 23:52 with 54 + 2 paired tests failing with an injected defect and passing with the repair (RED→GREEN) under both interpreters and `grep -c
pthread_sigmask = 0`. The live smoke (Ed-approved as a standing permission, memory file
`live-smoke-dummy-label-approved.md`) ran REAL launchd with throwaway labels `com.joulewise.smoke.night`/`.deadman`, a
throwaway launch dir and custody root, plists rendered from the real template with `/usr/bin/true`: `print` rc 113
with the exact absence line ×2 → `bootstrap` rc 0 ×2 → `print` rc 0 ×2 → engine install rc 0 (VALIDATED → … → VERIFIED
→ SUCCESS) → `bootout` rc 0 ×2 → `print` rc 113 ×2 → uninstall rc 0 → `SMOKE VERDICT exit=0: PASS`, confirming the
launchctl "service absent" response (rc 113 plus its stderr line) on macOS 25G83 twice (trace record `08k`, log `08m-…-PASS.log`). PR #341 merged as `2944a45d`
(`TASK_QUEUE.md` INSTALL-WINDOWS-MULTI-01 row). The shell script survives as an 88-line argv wrapper
(`scripts/install_night_agent.sh`).

### 2.7 The speed pass (09-15 20:55 → 09-16 00:45)

Ed's directive this evening: "science quality the ONLY gate on window cadence" (memory file `speed-pass-directive.md`).
Four work items followed the installer, in the order set by the any-time-windows ruling:

- **Pre-authorised retries during arming** (lane ARM-RETRY-CLASS-01, rank A172; rulings 20:55): the enumeration lives in one executable
  module, `joulewise/arm_retry.py`, with `classify_abort(cause) → "retry" | "cold_gate"` over the four ruled causes
  (`arm_idle_interactive`, `arm_notice_mismatch`, `arm_watchdog_uncertain`, `arm_transport`) plus every
  gate/driver/installer code, and `retry_allowed(now, plan, attempts, notice)`: plan fingerprint = raw-plan SHA-256, no
  count cap ("a hard count re-inserts the human decision point D-180 cl.2 removes"), ≥ 60 s spacing
  (`RETRY_INTERVAL_S = 60`), retries allowed until `install_close_epoch(plan)`, every attempt re-sends the notice,
  per-attempt directory `$STAGE/arm-attempts/NNNNNN/` (`…b0ae8462/03b-a172-rulings.md` R1–R3;
  `joulewise/arm_retry.py:16-27`). PR #342, `cb70e97f`.
- **Idle-interactive census exemption** (lane ARM-CENSUS-IDLE-INTERACTIVE-01, rank A173; rulings 21:05): a
  design that allowed only enumerated inert processes was rejected because Claude Code spawns a `zsh -c` child per tool call, so no real idle
  session would ever pass; the adopted classifier instead identifies active workloads: a session is BUSY iff any descendant matches the
  workload table (`unittest`/`pytest`/`shard_tests.py`, `powermetrics`, `run_night.py`, `run_campaign.py`,
  `chain.zsh`, `vllm`/`mlx` serve, `codex … exec`, `claude -p`…), else idle; UNKNOWN reads as IDLE (a false idle classification costs
  one stub, which acquires no data); the exemption applies to `REHEARSAL_STUB` only, and the t0 plan-span refusal is untouched
  (rulings record `04b` blockers 1–3, R1; `joulewise/arm_census.py:230-235`). Discovery is PID-only so multi-line agent
  argv cannot produce false matches (`arm_census.py:23-27`). PR #343, `b8b4406d`.
- **Delay between arming and measurement start** (lane LEAD-MARGIN-01, rank A210): `INSTALL_CLOSE_MARGIN_S` 3600 → 120 s (`scripts/run_night.py:75`;
  the failing test before the repair reported `AssertionError: 3600 != 120`, round-1, trace record `18`), and the supervisor's launch-block, exit-request, SIGTERM and SIGKILL deadlines (PLAN/REQUEST/TERM/KILL)
  25/25/16/15 → 8/8/6/5 min (`scripts/magistrate_watchdog.py:86-89`), ratified by Ed 2026-09-16 00:20 "do whichever is
  safest first quick second"; the 5/5/3/2 variant is recorded as the quick alternative
  (`docs/decision_log.md:11009-11016`, D-171(b) addendum). The physics that had justified 25 min, ≥ 10 min of untouched
  idle so XProtect-class daemons run before the first capture, is met by KILL at t0−5 plus the chain's `SETTLE_S = 600`
  before the first derivation capture (d01): quiet-to-first-capture ≥ 300 + 10 + 600 s ≈ 15.2 min (runbook §1.3). Arm-to-t0 floor:
  `t0 − 8 min − 2 min = t0 − 10 min`. PR #344, `e79eac14`.
- **Fast retry after a refusal** (lane REFUSAL-FAST-RETRY-01, rank A212): Ed at ~00:05, "how have we not made this a lower cost
  to pay". Mechanism: a refusal at t0 in the first second still held the magistrate away for the full span
  `t0 + 9000 + 300` s as if the night had run, then result collection → the runbook's calibration-equivalence assessment (§2.5) → fresh plan → arming delay: ≈ 3 h per refusal. Cure:
  (a) the span ends at the refusal record when no capture started (`refusal.json` present, no receipt, no
  `chain.started`); (b) a machine-state refusal with no capture is pre-authorised for the same retry procedure used during arming; (c) a
  counterfactual test that a started chain never shortens the span. Ed ruled (b) at 00:35: "unless there's a
  scientific reason that's an unsound decision absolutely reduce the hours to 20 min". Registered rank 212, blocked on
  the retry class + installer; queued, not landed (`19-refusal-cost-analysis.md`;
  `…08ca8197/06-refusal-fast-retry-lane-registration.md`).

Integration found two interactions missed by the individual work-item checks: a retry-class test pinned `install_close_epoch = t0
− 85 min` by construction and broke under the reduced 10-min arming delay (fixed to derive the lead from
`run_night.install_close_epoch`), and a checklist sentence about orphaned fixtures failed an exact-text documentation check
(`24-integration-tree-findings.md`).

### 2.8 CI and the quick tier (09-15 → 09-16)

Full-matrix pushes measured 39.82 / 32.57 / 32.05 min, dominated by queueing under GitHub's 20-concurrent-job cap; one
run ended on an 11-second wheel smoke after an 18-minute wait (`10b-ci-trim-2-astra-report.md`). Changes, in order:
six ordinary shards per interpreter with refreshed timings (ordinary shard ≈ 13.83 min, below the ~19 min
minimum imposed by calibration-exit tests; `.github/workflows/ci.yml:136-148`); PRs on Python 3.13 only, main pushes on 3.11 + 3.13
(`ci.yml:39-49`); a `quick` job (`scripts/quick_suite.py --tier quick --workers 4`, 153 isolated fast modules) that every
matrix job `needs` (`ci.yml:14-33, 132`); GitHub Pro raising the cap to 40 jobs for $4/month, chosen over Blacksmith
($65–300/month) because the bottleneck was the cap, not runner speed (`15-blacksmith-investigation.md`); and the
docs-only skip restored fail-open after ~30 bookkeeping pushes × 21 jobs stalled the queue for 30 min, per Ed at 00:20:
"obviously doc changes don't need to go through ci and clog the queue" (`ci.yml:57-97`; memory file
`ci-queue-bookkeeping-pushes.md`). Measured after: under Pro all 13 PR jobs started within 60 s and the execution wall
was the longest job (14.2 min); with the quick gate and docs-only skip a code PR ran 20.1 min wall, `quick` 2.1 min on
the hosted runner, and a red quick tier fails the PR in ≈ 3 min (`10-ci-trim-2-astra-plan.md` Measurements 2–3).
Locally the quick tier is ≈ 59–61 s for 153 modules (`26-merge-wave-record.md`). Ed also ruled merges proceed on a
green LOCAL full replay plus the quick tier, with hosted CI as post-merge confirmation (memory file
`ci-postmerge-ruling.md`). Test-speed changes that did not land: the 3.8× fitter (bit-identical but it changes source
bytes pinned by the issued calibration acceptance; deferred to the next acceptance re-issue, trace record `12a`); the
calibration-exits pool (17 cases must stay serial, `12c`); the first receipt-history optimisation (`git cat-file --batch`, CLI
73.5 → 59.7 s; H1) landed as PR #347, and the second was dropped (H2) (`12e`).

### 2.9 Merge wave (09-16 01:26 → 02:05)

The combined branch (`int/2026-09-16-merge-wave` @ `881a8d6b`) contained main `2944a45d` plus all work items; full replay
`scripts/shard_tests.py --workers 12 --split`: `shards=12 modules=239 tests=6240 failures=0 errors=0 skipped=109
result=PASS` at 01:26:19 (`26a-integration-replay-881a8d6b.txt`). For each branch: merge `origin/main` (conflicts take the
integration tree's version) → `quick_suite.py --tier quick` on the branch head → `gh pr merge`: retry class #342
`cb70e97f`, idle-interactive census #343 `b8b4406d`, shorter arming delay #344 `e79eac14`, CI trim + quick tier #340
`bf870fed`, orphaned-fixture detection #345 `e41cb4c2`, render-only fix #346 `a77067cc`, receipt-history optimisation #347 `68e5dce6`
(`26-merge-wave-record.md`). #346 came from the post-merge cross-unit review: `Prepared.admit` required the published
custody path even in render-only mode, so the staged validation step of invariant 2 would refuse
`plan_outside_custody_root` (`25-postmerge-cross-unit-review.md` R1).

Defects in the wave itself: all seven PR bodies were written with `gh pr create --body`, which replaces
`.github/pull_request_template.md`, so none carried the twelve-row gate ledger; the `gate-ledger` check failed on each
and nothing blocked the bare merge because main had no branch protection. Backfilled post-merge with
`scripts/check_gate_ledger.py` (`KEYS = 1..12`, heading `## Gate ledger (D-118 / D-121)`, `:13-15`); Ed: "probably make
sure that don't happen again innit?"; by 02:18 main was branch-protected on the `gate-ledger` context (memory file
`pr-body-gate-ledger-required.md`; memory file `checkpoint-2026-09-15-activation-08ca8197.md` 02:18 update). Eight
queued CI runs for superseded heads were cancelled. A failed `cd` in a chained command let a `git diff --stat` run in
the canonical checkout (no state changed; memory file `bash-chain-cd-guard.md`).

### 2.10 Handoff, the Gmail abort, and the notice-transport directive (09-16 01:55 → 02:35)

The interactive session transferred responsibility for the installer to a headless magistrate at ~01:55 with step 0 "wait for a green CI
run on main before re-cloning"; at 02:11 that run was still queued, and the ruling was (B): arm the stub with CI
recorded as pending, because a stub acquires nothing and the merge gate that applied was the integration replay
(`26-merge-wave-record.md` Addendum 02:12). The headless magistrate rebuilt the rehearsal plan (`rehearsal-20260916`) from the successor handoff record
(**handback**, commit `cf249594`): clone
`JouleWise-measurement-rehearsal-20260916b`, plan sha `dff929bc…`, t0 03:00:00 PDT (1789552800), install close 02:50
(10-min floor read from the merged code: `PLAN_LEAD_S 480 + INSTALL_CLOSE_MARGIN_S 120`), REQUEST 02:52, TERM 02:54,
KILL 02:55, window end 03:15, dead-man 04:20; `--render-only` rc 0; arm census rc 3 on the other session's six detached
bookkeeping agents at 02:00:49, CLEAR at 02:05 (`…08ca8197/10-rehearsal-20260916-arm-record.md`). Attempt 1's notice
send failed because the claude.ai Gmail MCP session had expired, and was classified `arm_transport` → `retry`,
`not_published`, abort epoch 1789549940 (02:12:20 PDT), intended notice preserved verbatim. A headless activation
cannot re-authorise the connector, so the magistrate exited cleanly at 02:18 to get a fresh MCP session; the watchdog
mislabelled the exit `usage_exhausted` and held `BACKOFF_USAGE` until 02:29 (relaunch cycle ≈ 11 min). The successor
launched 02:29:14 with the connector loading unauthenticated, no send tool in the process at all; Ed's own reconnect
returned `not_found_error "Server not found"` (a claude.ai-side outage, req `req_011Cf6t8mYgEBLHarG6c4aBi`); it waited,
then exited 02:35 on the other session's authorisation for one more relaunch probe. The 03:00 t0 lapsed unarmed
(`docs/process_traces/2026-09-16-activation-736e2aed/00-launch-record.md`; memory file
`checkpoint-2026-09-16-activation-736e2aed.md`).

Ed filed directive issue #349 at 02:34:30 PDT (`gh issue view 349`: label `directive`, author `mpmdw`): when Gmail is
unavailable, the arm notice may be posted as a new issue labelled `directive-notice` with exactly the email's content
(plan id, sha, t0, install close, dead-man, clone H, span list); GitHub emails Ed, so the no-objection window and the NO
channel are unchanged; email stays primary; implementation is tracked as a notice-transport fallback (lane NOTICE-TRANSPORT-FALLBACK-01; memory file
`notice-transport-fallback-ruling.md`).

## 3. Component inventory

| File | Contract (one line) | Failure classes | What catches them |
|---|---|---|---|
| `scripts/magistrate_watchdog.py` | LaunchAgent tick every 300 s; launches a headless magistrate only when no plan span is active, the census is clean, stop refs are clear and the clock is sane; resident supervisor drains it at t0−8/−6/−5 min | `CLOCK_UNCERTAIN` (wall/monotonic disagree > 60 s), `NETWORK_UNCERTAIN`, `HOLD_CENSUS`, `HOLD_UNSAFE` (malformed plan, twin, lock), `BACKOFF`/`BACKOFF_USAGE` | Typed states + one transition event each in `events.jsonl`; `installed_agent_fence` reads both plists; `classify_exit` on the session's output tail (`:1343-1348`) |
| `joulewise/night_agent_install.py` (+ `scripts/install_night_agent.sh` wrapper) | One `Transaction` with one commit latch and one teardown dispatching on state; only `LaunchctlAdapter` calls launchctl; deletion requires an `Absent` proof | Class 1 (exit 0 past the clock bound), class 2 (job loaded, plist gone / uninstall lies), signalled installs, teardown exceptions (RETAINED, exit 1) | Three-valued liveness (rc 113 + exact stderr line = ABSENT), record-and-poll signals, 54 + 2 mutation pairs under 3.14.7 and 3.9.6, live launchctl smoke (trace record `08k`) |
| `scripts/run_night.py` | Night driver: t0 gate (census, load, HID, boot clock, custody), chain launch, result/refusal records, courier spawn; owns `install_close_epoch`, `schedule`, dead-man arithmetic (`:64-76, :972-977, :1044`) | Refusals (enumerated codes), chain abort, courier deadline miss | `refusal.json`/`result.json` always written; dead-man job fires after completion + 3600 s and refuses on its own census |
| `joulewise/arm_retry.py` | Pure classifier: `classify_abort` → retry / cold_gate; `retry_allowed` bounds retries by fingerprint, ≥ 60 s spacing, install close, veto | Mis-classifying a physics refusal as retryable | Explicit dictionaries for every code (`RETRY_CAUSES`, `COLD_GATE_CODES`, `INSTALLER_REFUSALS`); tests pin the live `INSTALL_SPANS` |
| `joulewise/arm_census.py` | Pre-publication census; PID-only discovery; idle interactive sessions exempt for `REHEARSAL_STUB` only; `publication_blocked` for stubs | A busy session read as idle (costs one stub) | Workload table over the full descendant tree; UNKNOWN → idle by ruling (rulings record `04b`) |
| `scripts/fixture_orphan_census.py` | Report registered fixture processes reparented to PID 1; never signal them | Leaked fake servers inflating load/census | Signature registry `tests/fixture_signatures.json`; session-end check; watchdog spawn census (0 rows on 09-16 02:29) |
| `scripts/quick_suite.py` | Isolated fast tier (153 modules) as the first CI job and the local merge gate | Slow/flaky modules poisoning the gate | Tier selection with exclusions; `--module` replays one failure in isolation |
| `.github/workflows/ci.yml` | `changes` selects interpreters (PR → 3.13) and fails open on any detector error; `quick` gates six shards + two exclusive jobs; docs-only diffs skip them | Queue starvation, wrong skip | Detector requires a successful, non-empty, all-`docs/*`-or-`*.md` diff; fences/build/wheel run regardless |
| `scripts/check_gate_ledger.py` | Validate the twelve-row `## Gate ledger (D-118 / D-121)` table in a PR body | Missing/malformed ledger | `gate-ledger` check, now a required context on main |
| `docs/process/NIGHT_HANDBACK.md`, `NIGHT_COURIER_PROMPT.md` | The three sections the magistrate rewrites before every arm; the courier reads them first and decides nothing from them | Handback/result disagreement | "the result record is right and the courier says so" (§head) |
| `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` | Headless launch duties: heartbeat → launch email → notice.ack; poll `standdown.request`; never arm outside email-then-arm; exit by REQUEST; preserve the email if Gmail is down | Connector outage, stale pointer | "If Gmail is unavailable, preserve the exact intended message … include that failure in the durable pointer" |

## 4. Before → after

| Quantity | Before | After | Source |
|---|---|---|---|
| Arm-to-t0 floor | 85 min (`INSTALL_CLOSE_MARGIN_S` 3600 + 25-min lead) | 10 min (120 s + 8-min lead) | `run_night.py:75`; `magistrate_watchdog.py:86`; runbook §1.3 |
| Resident ladder PLAN/REQUEST/TERM/KILL | 25/25/16/15 min | 8/8/6/5 min (5/5/3/2 recorded alternative) | `decision_log.md:11009-11016` |
| Cost of a zero-capture t0 refusal | ≈ 3 h (full span held) | ≈ 15–20 min (ruled; refusal fast-retry lane queued, not landed) | `19-refusal-cost-analysis.md`; memory file `refusal-fast-retry-ruling.md` |
| Install spans | one 03:00–06:30 block per calendar day | `INSTALL_SPANS = (("00:00","24:00"),)`, list-valued, dead-man per span | arm-retry ruling D-180 cl.1; `run_night.py:76` |
| t0 | fixed minute in the 02:45–03:30 belt (02:56) | any whole minute the margins allow | any-time-windows ruling D-181 cl.1; `…08ca8197/10-…arm-record.md` schedule |
| Windows per day (mechanism) | 1 | ≈ 4–5 estimated with the old 1-h close (memory file `quiet-windows-any-time.md`); derived at the 10-min floor: 10 min lead + 150 min window + 5 min courier + harvest/re-clone/stage (clone+ledger+stage ≈ 3 min on 09-16) ≈ 2.8 h/cycle ≈ 8/day upper bound, before any refusal | this doc's arithmetic; `10-…arm-record.md` timeline |
| CI wall on a code PR | 32–40 min (3.11 + 3.14 matrices, 20-job cap) | 20.1 min measured; ≈ 15 min execution when the queue is clear; red quick tier ≈ 3 min | `10b`, `10-…plan.md` Measurements 2–3 |
| CI jobs, docs-only push | 21 (full matrix) | 4 short jobs | `10-…plan.md` step 3; `ci.yml:57-97` |
| Test count in the full replay | 5653 (PR #312, 09-09) | 6240 across 239 modules, 12 shards | `RUN_STATE.md` checkpoint T38f; `26a` |
| Installer | 1 zsh script, `$?`-dispatched teardown, two-valued fake launchctl | Python state machine, one commit latch, three-valued liveness, 88-line shell wrapper | §2.6 |
| Worktrees on disk | 314 | 76 | `00-session-record.md` seat 05 |

## 5. What still touches Ed, and known limitations

- **FileVault / login.** Any unattended reboot parks at the disk-password screen and nothing relaunches until Ed types
  it; accepted in the hands-free ruling (D-171) and reaffirmed 09-15 (Ed: FileVault stays ON). `sudo fdesetup
  authrestart` is a one-shot cure Ed must run himself (memory file `checkpoint-2026-09-15-restart-fseventsd.md`).
- **Headless connector re-auth.** The claude.ai Gmail MCP is an OAuth session a running `claude -p` cannot re-acquire;
  a dropped connector costs one clean exit + relaunch (≈ 11 min with the stale-label backoff) and a claude.ai-side outage
  costs the window. The issue-transport fallback is authorised but not merged (directive #349; lane NOTICE-TRANSPORT-FALLBACK-01); the relaunch prompt still says email-then-arm only.
- **Stale `last_exit_class`** (lane rank A197). A clean exit leaves the previous `usage_exhausted` label in
  `state.json`, so the next tick waits `USAGE_BACKOFF_S[0] = 900` s instead of the 300 s clean cooldown and reports the
  wrong class (`magistrate_watchdog.py:96, :1507, :1714-1723`); read `events.jsonl` for the truth. Registered, not fixed.
- **Refusal cost cure not landed.** Fast retry after a zero-capture refusal is authorised and queued (A212); until it lands a t0 refusal still
  holds the full span.
- **Machine hygiene is not self-healing.** fseventsd's leak clears only on restart (Ed's sudo); worktree pruning and
  `iw-*` matrix cleanup are tracked work items, and orphaned fixtures are detected without an atexit kill.
- **The first science night still waits for green hosted CI** on its clone head (surviving condition of the 02:12
  ruling) and for a quiet machine: Ed's interactive sessions and the agent desktop apps must be closed through t0.
- **Physics gates unchanged by design:** load > 2.0 refuses (that is what refused 09-15); XProtect/mds/backupd
  > 5 % CPU refuses; the 25F84 → 25G83 macOS acceptance-epoch mismatch still returns `check` rc 3 and blocks research results
  until derivation nights support re-issuing calibration acceptance (ACCEPTANCE-EPOCH-25G83-01).
- **Stale prose on main:** the introductory block written during retry-class implementation in
  `docs/phase_2/derivation_night_runbook.md:1622-1626` and `docs/process/NIGHT_HANDBACK.md:55-59` still reads "25
  minutes before t0" and "`t0 − 85 minutes`"; the constants and §1.3 say 8 and 10.

## 6. Lessons that became rules

The cited assistant memory files live under `~/.claude/projects/-Users-edr-code-JouleWise/memory/`.

- A headless turn end is a process exit; hold with bounded waits and launch delegated sessions detached (memory file `headless-turn-end-kills-seats.md`).
- Never trust `state.json` `last_exit_class` alone; the transition reason in `events.jsonl` is the exit class (same memory file; lane rank A197).
- Windows are never artificially scarce; every frequency bound must trace to a scientific requirement (memory file `quiet-windows-any-time.md`, Ed 09-08, reaffirmed 09-15; any-time-windows ruling `docs/decision_log.md` D-181 cl.1).
- Science quality is the only gate on cadence; arm-to-t0 ≈ 10 min (memory file `speed-pass-directive.md`; lead-margin addendum to D-171(b) in `docs/decision_log.md`).
- A zero-capture t0 refusal auto-retries; the span ends at the refusal (memory file `refusal-fast-retry-ruling.md`; lane REFUSAL-FAST-RETRY-01).
- When Gmail is down, the notice goes out as a `directive-notice` issue (directive issue #349; memory file `notice-transport-fallback-ruling.md`).
- Merge on green local replay + quick tier; hosted CI is post-merge confirmation (memory file `ci-postmerge-ruling.md`).
- Never `gh pr create --body` without the twelve-row ledger; `gh pr checks` must show gate-ledger green; branch protection is the durable fix (memory file `pr-body-gate-ledger-required.md`).
- Batch bookkeeping pushes; docs-only pushes skip the matrix; cancel redundant queued main runs (memory file `ci-queue-bookkeeping-pushes.md`).
- Two consecutive repair rounds for the same failure class require consultation before further repair (orchestration rule 11 in `/Users/edr/code/JouleWise/CLAUDE.local.md`; the round-6 cold gate ruling Q3 and the delta-3 stop record cited in §2.6).
- "No round N" rules stop death spirals, not nearly-done designs converging under executed evidence (memory file `stop-conditions-are-antispiral.md`, Ed 09-15, applied at 23:15 to round 8).
- A bound is observed, not predicted; no invented ceiling constants (cold gate 25 Q2 in §2.6, `MAX_INSTALL_DURATION_S` rejected).
- Fail-closed only for physics, evidence and pre-registration; checks only against deliberate operator tampering retire; tolerances are sized to the instrument (≈ 1 J / ≈ 5 J) (threat-model prune `docs/decision_log.md` D-161; memory file `sensible-gates-directive.md`; the `codex|claude|t3` census kept in PR #334).
- Treat unknown process liveness as loaded; a test double that cannot represent unknown cannot verify that rule (Opus design seat record Q3 in §2.6).
- Delegated sessions run in linked worktrees, never main; briefs under enforced `WRITE_SCOPE` (memory file `codex-seat-launch-rules.md`).
- Never guard a bookkeeping chain on a clean tree; read every commit's `--stat` before claiming it landed (memory file `bookkeeping-chain-guard.md`).
- `cd "$W" && …` before any destructive step; `set -e` is not a guarantee in this harness (memory file `bash-chain-cd-guard.md`).
- Live smoke on throwaway launchd labels is standing-approved before PR/arm (memory file `live-smoke-dummy-label-approved.md`).
- Offload archives to iCloud, never live worktrees or custody roots; sync clients generate churn (memory file `icloud-offload-directive.md`).
- Decided ≠ done: a ruling identifies the required implementation, and the existing mechanism's limit remains until that work is merged (preambles of `docs/decision_log.md` D-180 and D-181).
