# Fully automatic measurement windows: the work it took (2026-08-08 → 2026-09-16)

Written 2026-09-16 from the checkout at main `11ea57db`. Every load-bearing number is cited to a repo path;
anything not verifiable in the checkout is marked `ASSUMED:` inline. Register: the person who built it.

## 1. What "fully automatic window" means, and the four invariants

A **window** is one scheduled, agent-free period in which the machine runs a measurement chain (a zsh script of
capture steps and pauses) under `powermetrics`, with nothing else alive that could add joules. A **plan** is the JSON
record (`joulewise.night_plan.v2`) that fixes the window: `t0_epoch_s` (the start), `window_max_s` (the span cap;
9000 s for a derivation night, 900 s for a stub), the frozen checkout triple `(plan_id, measurement_root, head)`, the
custody root (the directory that will retain the night's records), and the chain's SHA-256. **Arming** is the act of
publishing that plan where the supervisor will find it and installing two launchd jobs from it: `com.joulewise.night`
(fires at t0, runs `scripts/run_night.py`) and `com.joulewise.night.deadman` (fires after the planned completion and
refuses or stands down anything still alive). "Fully automatic" means: no human types anything between the decision
to run and the harvested result — the plan is authored, noticed, armed, executed, harvested and retired by the
headless **magistrate** (a `claude -p` session launched by a user LaunchAgent) and the **courier** (the session the night
driver spawns after the chain exits to push the results branch and email Ed).

Four invariants survive every mechanism below; each later section is a way of making one of them true by construction:

1. **No capture with an agent active.** The night gate runs a process census at t0 (`pgrep -lf 'codex|claude|t3'` plus
   load, HID-idle, boot-clock and custody guards); any hit refuses the night and no chain starts
   (`docs/phase_2/derivation_night_runbook.md` §0.6). The magistrate must therefore be gone before t0; the **plan
   span** — the agent-free interval from `t0 − PLAN_LEAD_S` through completion — is the interval in which the watchdog
   refuses to launch one (`docs/process/MAGISTRATE_WATCHDOG.md` §Fence and deadlines).
2. **Publication is the single irreversible instant.** The plan is staged outside the watchdog's `*/night_plan.json`
   discovery glob, validated there, and moved into the custody root by one atomic `os.replace`; everything before it can
   be abandoned without trace and everything after it is a re-arm (runbook §1.4 step 5, "the one irreversible
   instant"; `docs/decision_log.md` D-175's eight conditions).
3. **Every refusal is a printed result.** A refusal at any stage writes a record — `night/refusal.json` at t0, an
   `outcome.json` per arm attempt, a typed exit code from the installer — and the next reader classifies from that
   record, never from an absent success (`scripts/run_night.py` `REFUSAL_SCHEMA`; `joulewise/arm_retry.py`
   `classify_abort`).
4. **Plan frozen and hashed before data.** The plan pins `repo_head = measurement_head = H`, the chain's sha256 sidecar,
   and the pre-registration path; the harvest re-derives the chain from the clone and compares bytes before reading any
   result (runbook §2.0; harvest records under `docs/process_traces/2026-09-1*-activation-*/01-*harvest-record.md`).

## 2. Dated timeline

### 2.1 Charter: D-127 and D-128 (2026-08-08)

D-127 chartered the loop (harvest → mint → judge → build next pack → launch → exit for the capture → relaunch a
fresh headless session) with the zero-agent-during-capture fence unchanged and a relaunch harness shaped as
preflight → launch → liveness proof → bounded retries → independent launchd fallback timer ("never one mechanism").
D-128 ratified it the same day: run the loop until the paper is defensible (`docs/decision_log.md` D-127 items 1, 2, 4;
D-128 item 1).

### 2.2 The hands-free week and the watchdog (2026-09-02 → 09-08)

Ed left for up to a week on 2026-09-02. D-171 delegated the launcher invocation (E-10 amendment), the step-6 custody
digest, the transaction GO and the watchdog install; stand-down margin 5 min before t0 ("30 min … seems too much");
machine state: lid open, AC, FileVault on — "an unplanned reboot halts everything until someone types the disk
password (accepted)" (`docs/decision_log.md` D-171 items 1–4, 7, closing paragraph).

The **watchdog** (`scripts/magistrate_watchdog.py`, user LaunchAgent `com.joulewise.magistrate`, tick at load and every
300 s, resident supervisor at 10 s resolution) was designed by a three-seat consult, built, refuted twice and cold-gated
(hands-free-week records 02–20), landed on PR #284 (`TASK_QUEUE.md` WATCHDOG-BUILD-01 row) and installed by the
interactive magistrate on 2026-09-06, which was reaped by design (`RUN_STATE.md` T36). The first watchdog-owned
activation came only at 2026-09-08 00:51:55: the tick had sat in `CLOCK_UNCERTAIN` since 09-06 03:36 because the closed
lid put the MacBook into Maintenance Sleep every ~5 min and wall/monotonic deltas disagreed
(`docs/process_traces/2026-09-02-hands-free-week/21-first-launchd-activation-1ef89702.md`, seq 1–4). That activation hit
the 600 s background-task ceiling at 01:33:28 and the watchdog relaunched `784a764e` at 01:41:58 after the 300 s
cooldown (`RUN_STATE.md` T38). Also 2026-09-08: D-175 amended the relaunch prompt so a headless magistrate may arm a
REHEARSAL_STUB (stage outside the glob, `--render-only` from the pinned checkout, `os.replace`, install from that
checkout, email with pins before the move, no other agent alive) and D-176 fixed the pack-night GO receipt and
step-6 custody (`docs/decision_log.md` D-175, D-176).

### 2.3 Stub rehearsals and their failures (09-09 → 09-15)

A **stub** (`REHEARSAL_STUB`) is a plan whose chain is a built-in three-second script; it exercises launchd, gate,
courier and harvest with zero acquisition. Each one found a different seam:

- **rehearsal-20260909** (armed by `784a764e`, fired 02:56 09-09): verdict `REHEARSAL_ONLY`, chain exit 0, results branch
  `night-results/20260909`, but the receipt read `REFUSED night_probe_error` because the gate tried to read a chain
  sidecar a stub does not have → NIGHT-GATE-STUB-CHAIN-01, PR #309 (`RUN_STATE.md` T38d/T38e).
- **rehearsal-20260911** (t0 02:56 09-11): the driver crashed in its first second — the plist ran `/usr/bin/env python3`
  under launchd's `PATH`, which resolved to `/usr/bin/python3` = 3.9.6, and `joulewise/arm_readiness.py:26`
  `from datetime import UTC` raised `ImportError`. At 07:00:02 the dead-man's census found an orphaned Claude daemon tree
  (pid 83102, parent session already gone) and wrote `night_refused_agent_present`. Cure: NIGHT-INTERPRETER-PIN-01
  (the plist pins the clone's interpreter) (`docs/process_traces/2026-09-11-activation-58a3bcfc/01-rehearsal-20260911-harvest-record.md`).
- **rehearsal-20260912** (t0 00:30 09-12, clone at `a7d1eb88` with the 3.13 pin): driver started 00:30:04.29, gate
  `REHEARSAL_ONLY` at 00:30:04.76, stub chain exit 0 at 00:30:07.09, `launchd.night.err` empty, courier email
  `1a09487237fa6be2`; the courier harvested and retired the night itself because the magistrate was not alive
  (`docs/process_traces/2026-09-12-courier-rehearsal-20260912/01-rehearsal-20260912-harvest-record.md`). First end-to-end
  pass of the unattended chain.
- **n1-20260913**, the first science night (epoch-equivalence check, directive #316): fired 02:56:02, REFUSED at t0 —
  Ed's interactive session (pid 24974) and the ChatGPT desktop app's bundled Codex helper were in the census
  (`docs/process_traces/2026-09-13-activation-c5048879/01-equivalence-night-20260913-harvest-record.md`). The 09-14
  03:00–06:30 install span then closed without an arm because the arm-time census never cleared
  (`docs/process_traces/2026-09-13-activation-24b9d3dd/49-no-arm-record-n1-20260915.md`).
- **n1-20260915**: Ed's directive #336 authorised an evening install; armed 16:45:46 09-14 after Ed closed his session
  and the census went clean at 16:44:13 (`…24b9d3dd/52-arm-record-n1-20260915.md`); fired 02:56:03 09-15 and was REFUSED
  on load alone — 1-min load 2.55 > 2.0 with a clean census; the load was `fseventsd` (pid 553) at ~184 % CPU with
  4721 CPU-minutes over 12 days of uptime (`docs/process_traces/2026-09-15-activation-1acf2aee/01-equivalence-night-20260915-harvest-record.md`).

Two rulings came out of these nights. **D-180** (Ed, 2026-09-10, after the 09-10 arm was blocked by two idle interactive
sessions): install spans recur within a day; a pre-authorised retry class for non-physics arm aborts (idle interactive
session, stale notice hash, watchdog `CLOCK_UNCERTAIN`/`NETWORK_UNCERTAIN`, transport failure); idle interactive
sessions are not foreign at a stub's arm-time census (`docs/decision_log.md` D-180 items 1–3). **D-181** (Ed, directive
#337, 2026-09-14 16:43): windows run whenever the machine is quiet, day or night, several per day, no cadence rule; the
fixed daily minute inside the 02:45–03:30 belt and the calendar-day install span were "a mechanism limit, not a
scientific one"; lanes INSTALL-WINDOWS-MULTI-01 → ARM-RETRY-CLASS-01 → ARM-CENSUS-IDLE-INTERACTIVE-01 to the top of the
queue (`docs/decision_log.md` D-181 clause 1).

### 2.4 Census and refusal semantics

The t0 census matches helper processes of the desktop apps that bundle an agent runtime (ChatGPT's `codex … app-server`,
the Claude app's helpers) and does not match the apps' top-level processes; the ruling kept the pattern rather than
narrowing it (runbook §0.6; NIGHT-CENSUS-CHATGPT-APP-01 in `TASK_QUEUE.md`). An earlier arm-time browser probe matched
Apple's always-present Safari XPC services and could never pass; cold gate 34 anchored the patterns
(ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01, `TASK_QUEUE.md`). Refusal codes are an enumerated set —
`night_refused_agent_present`, `_not_quiet`, `_hid_idle`, `_boot_clock`, `_registration`, `_class_unbuilt`
(`joulewise/night_gate.py:103-109` per `docs/process_traces/2026-09-15-activation-08ca8197/06-refusal-fast-retry-lane-registration.md`)
— and a status publisher (`scripts/window_status.sh`) may not run while a recorded chain or campaign is live or its
liveness is indeterminate (`docs/contracts/window_liveness.md` §1–§2).

### 2.4a Shrinking the security scope back to sensible (08-27 → 09-13)

Automation cannot run through fences built against an adversary who does not exist. Three rulings cut them back to the
ones that protect the measurement:

- **D-161 threat-model prune (Ed, 2026-08-27, "yes to all 3. right instincts").** The in-process adversary was already
  out of the threat model (D-139 A1, D-148 (6)) and the paper's §7 states a single trusted operator, so custody
  mechanisms whose only defended-against actor is that operator touching a file were over-engineering: that week they
  cost three hand edits and blocked the mint twice. Rulings: the reviewed pinset gets a REVIEWED REFRESH LANE
  (`--refresh-row`, re-derived by the verifier's own code path, diff printed, lands as a PR) and "no update lane"
  becomes "no UNREVIEWED update"; THREAT-MODEL-PRUNE-01 enumerates every refusal whose only actor is the trusted
  operator and downgrades it to warn-and-record or retires it; fail-closed STAYS where the failure is physics/evidence
  or pre-registration (missing calibration, unresolved anchor, absent floor, stale drift evidence, unfrozen plan,
  post-hoc analysis choice); the repository is tamper-EVIDENT for the operator's benefit, not tamper-PROOF. The
  addendum's operative test: MISTAKE vs DELIBERATE — guard against mistakes, retire deliberate-only guards
  (`docs/decision_log.md:207` index row; `:10685-10696`).
- **Sensible gates (Ed, 2026-09-10 ~04:20).** "make sure there are no silly gates on accepting numbers … recall that
  time where you wanted a tolerance of like 1e-15 sensitivity or something ridiculously microscopic compared to the
  measurement". Every tolerance on the claim path is sized to the instrument — attribution limit ≈ 1 J, claim bar ≈ 5 J
  (D-078 cl.11) — never to decimal places; physics/evidence refusals stay. GATE-SENSIBILITY-SWEEP-01 inventoried 299
  gates, merged repairs R1/R3/R4 and the G2-a `idle_seconds 75` in PR #314 (`0d4bb4fb`), and sent the D-165 zero-point
  band (an `isclose(rel_tol=1e-9, abs_tol=1e-12)` comparison of two binary64 routes over the same four numbers) to
  cold gate 47, which ruled it scale-bounded (sound below 8,192 J per member, not G2-a-blocking)
  (`memory/sensible-gates-directive.md`; `TASK_QUEUE.md` GATE-SENSIBILITY-SWEEP-01 row; `docs/decision_log.md` D-124
  addendum 2026-09-13). ASSUMED: the 1e-15 figure is Ed's recollection; the log shows a 1e-15 s quantization at
  `decision_log.md:6667`, not a 1e-15 J tolerance.
- **The census fence that survived (2026-09-13).** NIGHT-CENSUS-CHATGPT-APP-01 asked whether the t0 census should stop
  refusing on the ChatGPT desktop app's bundled Codex helper. Ruled option (i): keep `codex|claude|t3`; desktop apps that
  bundle an agent runtime count as agents; the operator quits both apps before every plan span (PR #334, `8980f85a`,
  cold gate packet 05 + Opus pairing; `TASK_QUEUE.md` row). It survived the prune because it protects the measurement —
  a helper that can start inference or a build inside the window — not the operator.

### 2.5 The 09-15 restart: what 13 days of unattended operation left behind

At 19:45 PDT 09-15 the machine had `fseventsd` at ~61 GB RSS and ~190 % CPU after 12 d 23 h up (boot 09-02), load 8.8,
~100 GB of local churn: 314 git worktrees under `~/code` (121 detached, 154 on already-merged branches), ~540 `iw-*`
test-matrix directories in `/private/tmp` (18 GB), `$TMPDIR` 39 GB, and 35 orphaned `vllm serve /fake/model` fixture
processes (10–12 days old, from `tests/test_node_worker_subprocess.py`, leaked when the test parent died)
(`~/.claude/projects/-Users-edr-code-JouleWise/memory/checkpoint-2026-09-15-restart-fseventsd.md`;
`docs/process_traces/2026-09-15-activation-08ca8197/00-launch-record.md`; the memory index says 312 worktrees, the
09-15 census says 314). Ed restarted at 19:55; the interactive session opened 19:58 and pruned 314 → 76 worktrees
(`docs/process_traces/2026-09-15-interactive-b0ae8462/00-session-record.md`, seat 05). Lanes registered: worktree
prune, fixture-orphan sentinel (A208), temp-dir hygiene.

Two other operational facts were established the same morning. Headless `claude -p` exits when the model ends its
turn, and the exit kills every `run_in_background` task; activations `1acf2aee` and `decae362` each ended a turn with
"the seats will wake me" and lost all three seats within minutes. The watchdog logged both as `clean activation exit`
(exit 0, 300 s cooldown), but `state.json` still read `last_exit_class: usage_exhausted` from 09-09 because the clean
path never resets that field (`scripts/magistrate_watchdog.py:1714-1723` sets backoff indices and transitions to IDLE
without touching `last_exit_class`; only `apply_backoff` at `:1372` writes it), so the next reader saw "usage"
(`memory/headless-turn-end-kills-seats.md`). Earlier, on 09-10 08:41, the Codex weekly quota fell after ~20 Astra seats
in one activation and the Claude 5-hour limit fired at 09:46 under Opus fan-out; Ed restored Codex usage ~21:25
(`memory/codex-usage-limit-2026-09-10.md`).

### 2.6 The transactional installer: why four zsh rounds failed, and the redesign

`scripts/install_night_agent.sh` installed the two LaunchAgents: render two plists → bootout priors → bootstrap night →
bootstrap dead-man → verify → succeed; plus `--uninstall` and `--render-only`. D-180/D-181 made its preconditions
time-varying (install only inside a listed span and before `install_close_epoch`) and every mutation is machine state a
fence reads — `installed_agent_fence` decides from the two plist files whether a plan is armed
(`docs/process_traces/2026-09-15-activation-d6888966/33-brief-redesign-consult-transactional-installer.md`, forcing problem).
Two defect classes were named: **class 1**, exiting 0 with a job loaded but no clock read after the last mutation
below `min(selected_span_close, install_close_epoch)`; **class 2**, ending with a job loaded and its plist absent (the
fence-blind state), or exiting 0 while a label it tried to bootout is still loaded.

Rounds 1–3 in zsh each closed the class at one site and the class reappeared at the next: final bootstrap → a
`set -e`-skipped EXIT trap → post-gate `rm -rf` → `--uninstall`. Cold gate 25 measured the shell fact under it —
zsh 5.9 `set -e` inside a function returns rc 1 with the EXIT trap NOT fired, and `always` blocks do not run either —
and rejected a `MAX_INSTALL_DURATION_S` ceiling as an invented number ("bounds are observed, not predicted")
(`…d6888966/25-coldgate-packet-install-windows/10-coldgate-fable-ruling.md`, probe table and Q2). Cold gate 28 executed
the round-3 head: a failed `rm -rf <backup>` after the commit gate tore down a verified arm (rc 1, both labels booted
out), and `--uninstall` with both bootouts failing exited 0 with both jobs loaded and no plists — `installed_agent_fence()
= None` (`…/28-coldgate-packet-install-windows-round-3/10-coldgate-fable-ruling.md`, Q1b, Q2a). The mechanism: every
verification re-read was `launchctl print … >/dev/null 2>&1 &&`, so ANY non-zero exit read as "not loaded" — but only a
not-found code means that; an error code means unknown, and unknown must mean loaded. The stub `launchctl` in the tests
emitted only 0/1 and could not express unknown, which is why the tests never saw it (`…/lt-21-delta-3-stop.md` F2;
`…/lt-22-opus-design-seat-transactional-installer.md` Q3).

The adopted, judgment-free stop condition fired at delta 3 (head `073a9763`, 11:42 09-15): class 1 YES, class 2 YES,
"no fix seat, no round 4" (`lt-21`). At 11:48 a blind three-seat consult (Astra xhigh, Opus, Fable) was asked one
question — keep zsh and fix the predicate at three sites, or a Python transaction module. All three chose the module
(`33a/33b/33c`). Its four devices, from the Opus seat: one mutation channel (`write_plist`, `bootstrap`, `bootout`; nothing
else touches `launch_dir` or launchctl); the clock gate as a precondition of the mutator, not a statement between
mutators; teardown dispatching on transaction state, never on `$?`; proof-carrying deletion — `require_absent(label)`
raises on LOADED and UNKNOWN, and `remove_plist` takes the `Absent` token (`lt-22` Q1 devices 1–4). Liveness became
three-valued from an executed probe: `launchctl print gui/501/<missing>` exits 113 with stderr
`Could not find service "<label>" in domain for user gui: 501`; rc 0 → LOADED; rc 113 with that exact line → ABSENT;
anything else → UNKNOWN (`lt-22` Q3; live code `joulewise/night_agent_install.py:274-280`).

The engine (`joulewise/night_agent_install.py`, system Python 3.9, states PARSED → VALIDATED → ADMITTED → STAGED →
PUBLISHED → NIGHT_LOADED → DEADMAN_LOADED → VERIFIED → COMMITTED → SUCCESS; terminal REFUSED / ROLLED_BACK / RETAINED,
`:351-364`) then went through rounds 4–5 (pre-restart), the restart, and rounds 5–8b in the interactive session. Rounds
5 and 6 were two consecutive rounds on one signature — signal handling: the handler raised from inside the signal
frame, the mask was left blocked, teardown was skipped. Cold gate 06 licensed round 6 as the LAST same-shape round and
wrote the STOP CONDITION: any further signal-class defect in the delta re-audit means no round 7 but a blind consult on
one question, replace raise-from-handler with record-and-poll
(`…interactive-b0ae8462/06-coldgate-packet-install-windows-round-6/10-coldgate-fable-ruling.md` Q3). The execution lens
drove real SIGINT/SIGTERM/SIGHUP at every seam under Python 3.14.7 and 3.9.6 on `efdaed87`: seam e failed 60/222 per
interpreter — a signal queued after its original disposition was re-installed was delivered at the final `SIG_SETMASK`
with that disposition and killed the process AFTER the result was complete (`08f`). Consult 13 convened 22:58; by 23:10
two of three seats had converged with executed probes on the same design: the handler only RECORDS one integer, ordinary
code polls at every state boundary and before every mutation, the last poll after the clock predicate is the commit
latch, no `pthread_sigmask` anywhere, `SIG_IGN` from the end of teardown to process death, teardown never polls. Opus
added the physical finding that the round-5/6 `SIG_BLOCK` in the handler was inherited by every launchctl child spawned
afterwards, making the subprocess unkillable (`13-consult-signal-redesign/03-magistrate-adoption.md`). Round 8b fixed the
one self-contradiction — `_commit` polled twice — into: predicate on the clock read → the last poll (latch) → direct
assignment of COMMITTED; a signal during the clock read rolls back with the signal's code, a signal after the latch is
ignored (`08j`; live `:459-464`).

Round 8 landed at `d5ec18bb` 23:52 with 54 + 2 mutation pairs RED→GREEN under both interpreters and `grep -c
pthread_sigmask = 0`. The live smoke (Ed-approved, memory `live-smoke-dummy-label-approved`) ran REAL launchd with
throwaway labels `com.joulewise.smoke.night`/`.deadman`, a throwaway launch dir and custody root, plists rendered from
the real template with `/usr/bin/true`: `print` rc 113 with the exact absence line ×2 → `bootstrap` rc 0 ×2 → `print`
rc 0 ×2 → engine install rc 0 (VALIDATED → … → VERIFIED → SUCCESS) → `bootout` rc 0 ×2 → `print` rc 113 ×2 → uninstall
rc 0 → `SMOKE VERDICT exit=0: PASS`, pinning the D2 wire signature on macOS 25G83 twice (`08k`, log `08m-…-PASS.log`).
PR #341 merged as `2944a45d` (`TASK_QUEUE.md` INSTALL-WINDOWS-MULTI-01 row). The shell script survives as an 88-line
argv wrapper (`scripts/install_night_agent.sh`).

### 2.7 The speed pass (09-15 20:55 → 09-16 00:45)

Ed's directive this evening: "science quality the ONLY gate on window cadence" (memory `speed-pass-directive`). Four
lanes, in D-181 order after the installer:

- **A172 ARM-RETRY-CLASS-01** (rulings 20:55): the enumeration lives in one executable module, `joulewise/arm_retry.py`,
  with `classify_abort(cause) → "retry" | "cold_gate"` over the four D-180 causes (`arm_idle_interactive`,
  `arm_notice_mismatch`, `arm_watchdog_uncertain`, `arm_transport`) plus every gate/driver/installer code, and
  `retry_allowed(now, plan, attempts, notice)`: plan fingerprint = raw-plan SHA-256, no count cap ("a hard count
  re-inserts the human decision point D-180 cl.2 removes"), ≥ 60 s spacing (`RETRY_INTERVAL_S = 60`), retries allowed until
  `install_close_epoch(plan)`, every attempt re-sends the notice, per-attempt directory `$STAGE/arm-attempts/NNNNNN/`
  (`…b0ae8462/03b-a172-rulings.md` R1–R3; `joulewise/arm_retry.py:16-27`). PR #342, `cb70e97f`.
- **A173 ARM-CENSUS-IDLE-INTERACTIVE-01** (rulings 21:05): an enumerated-inert-set design was rejected because Claude
  Code spawns a `zsh -c` child per tool call, so no real idle session would ever pass; adopted the workload-positive
  classifier — a session is BUSY iff any descendant matches the workload table (`unittest`/`pytest`/`shard_tests.py`,
  `powermetrics`, `run_night.py`, `run_campaign.py`, `chain.zsh`, `vllm`/`mlx` serve, `codex … exec`, `claude -p`…),
  else idle; UNKNOWN reads as IDLE (a wrong idle costs one stub, no physics); the exemption applies to `REHEARSAL_STUB`
  only, and the t0 plan-span refusal is untouched (`04b` blockers 1–3, R1; `joulewise/arm_census.py:230-235`). Discovery
  is PID-only so multi-line seat argv cannot masquerade as hits (`arm_census.py:23-27`). PR #343, `b8b4406d`.
- **A210 LEAD-MARGIN-01**: `INSTALL_CLOSE_MARGIN_S` 3600 → 120 s (`scripts/run_night.py:75`; round-1 RED was
  `AssertionError: 3600 != 120`, `18`), and the resident ladder PLAN/REQUEST/TERM/KILL 25/25/16/15 → 8/8/6/5 min
  (`scripts/magistrate_watchdog.py:86-89`), ratified by Ed 2026-09-16 00:20 "do whichever is safest first quick second";
  the 5/5/3/2 variant is recorded as the quick alternative (`docs/decision_log.md:11009-11016`, D-171(b) addendum).
  The physics that had justified 25 min — ≥ 10 min of untouched idle so XProtect-class daemons run before the first
  capture — is met by KILL at t0−5 plus the chain's `SETTLE_S = 600` before d01: quiet-to-first-capture
  ≥ 300 + 10 + 600 s ≈ 15.2 min (runbook §1.3). Arm-to-t0 floor: `t0 − 8 min − 2 min = t0 − 10 min`. PR #344, `e79eac14`.
- **A212 REFUSAL-FAST-RETRY-01**: Ed at ~00:05, "how have we not made this a lower cost to pay". Mechanism: a refusal
  at t0 in the first second still held the magistrate away for the full span `t0 + 9000 + 300` s as if the night had
  run, then harvest → §2.5 → fresh plan → arm lead: ≈ 3 h per refusal. Cure: (a) the span ends at the refusal record when
  no capture started (`refusal.json` present, no receipt, no `chain.started`); (b) a zero-capture machine-state refusal
  is a pre-authorised retry in the A172 shape; (c) a counterfactual test that a started chain never shortens the span.
  Ed ruled (b) at 00:35: "unless there's a scientific reason that's an unsound decision absolutely reduce the hours to
  20 min". Registered rank 212, blocked on A172 + installer; queued, not landed (`19-refusal-cost-analysis.md`;
  `…08ca8197/06-refusal-fast-retry-lane-registration.md`).

Integration found two cross-lane defects single-lane gates cannot: an A172 test pinned `install_close_epoch = t0 − 85
min` by construction and broke under A210's 10-min floor (fixed to derive the lead from `run_night.install_close_epoch`),
and an A208 checklist sentence tripped the docs-freshness fence's literal (`24-integration-tree-findings.md`).

### 2.8 CI and the quick tier (09-15 → 09-16)

Full-matrix pushes measured 39.82 / 32.57 / 32.05 min, dominated by queueing under GitHub's 20-concurrent-job cap; one
run ended on an 11-second wheel smoke after an 18-minute wait (`10b-ci-trim-2-astra-report.md`). Changes, in order:
six ordinary shards per interpreter with refreshed timings (ordinary shard ≈ 13.83 min, below the ~19 min
calibration-exits floor; `.github/workflows/ci.yml:136-148`); PRs on Python 3.13 only, main pushes on 3.11 + 3.13
(`ci.yml:39-49`); a `quick` job (`scripts/quick_suite.py --tier quick --workers 4`, 153 isolated fast modules) that every
matrix job `needs` (`ci.yml:14-33, 132`); GitHub Pro raising the cap to 40 jobs for $4/month, chosen over Blacksmith
($65–300/month) because the bottleneck was the cap, not runner speed (`15-blacksmith-investigation.md`); and the
docs-only skip restored fail-open after ~30 bookkeeping pushes × 21 jobs stalled the queue for 30 min — Ed, 00:20:
"obviously doc changes don't need to go through ci and clog the queue" (`ci.yml:57-97`; `memory/ci-queue-bookkeeping-pushes.md`).
Measured after: under Pro all 13 PR jobs started within 60 s and the execution wall was the longest job (14.2 min);
with the quick gate and docs-only skip a code PR ran 20.1 min wall, `quick` 2.1 min on the hosted runner, and a red
quick tier fails the PR in ≈ 3 min (`10-ci-trim-2-astra-plan.md` Measurements 2–3). Locally the quick tier is ≈ 59–61 s
for 153 modules (`26-merge-wave-record.md`). Ed also ruled merges proceed on a green LOCAL full replay plus the quick
tier, with hosted CI as post-merge confirmation (`memory/ci-postmerge-ruling.md`). Test-speed levers that did not land:
the 3.8× fitter (bit-identical but it changes source bytes pinned by the issued calibration acceptance — deferred to the
next acceptance re-issue, `12a`); the calexits pool (17 cases must stay serial, `12c`); histsem H1 (`git cat-file
--batch`, CLI 73.5 → 59.7 s) landed as PR #347, H2 dropped (`12e`).

### 2.9 Merge wave (09-16 01:26 → 02:05)

Integration tree `int/2026-09-16-merge-wave` @ `881a8d6b` = main `2944a45d` + all lanes; full replay
`scripts/shard_tests.py --workers 12 --split`: `shards=12 modules=239 tests=6240 failures=0 errors=0 skipped=109
result=PASS` at 01:26:19 (`26a-integration-replay-881a8d6b.txt`). Per-lane: merge `origin/main` (conflicts take the
integration tree's version) → `quick_suite.py --tier quick` on the lane head → `gh pr merge`: A172 #342 `cb70e97f`,
A173 #343 `b8b4406d`, A210 #344 `e79eac14`, CI-TRIM-02 + quick #340 `bf870fed`, A208 #345 `e41cb4c2`, render-only fix
#346 `a77067cc`, histsem #347 `68e5dce6` (`26-merge-wave-record.md`). #346 came from the post-merge cross-unit review:
`Prepared.admit` required the published custody path even in render-only mode, so D-175's staged validation step would
refuse `plan_outside_custody_root` (`25-postmerge-cross-unit-review.md` R1).

Defects in the wave itself: all seven PR bodies were written with `gh pr create --body`, which replaces
`.github/pull_request_template.md`, so none carried the twelve-row gate ledger; the `gate-ledger` check failed on each
and nothing blocked the bare merge because main had no branch protection. Backfilled post-merge with
`scripts/check_gate_ledger.py` (`KEYS = 1..12`, heading `## Gate ledger (D-118 / D-121)`, `:13-15`); Ed: "probably make
sure that don't happen again innit?"; by 02:18 main was branch-protected on the `gate-ledger` context
(`memory/pr-body-gate-ledger-required.md`; `memory/checkpoint-2026-09-15-activation-08ca8197.md` 02:18 update). Eight
queued CI runs for superseded heads were cancelled. A failed `cd` in a chained command let a `git diff --stat` run in
canonical (no state changed; `memory/bash-chain-cd-guard`).

### 2.10 Handoff, the Gmail abort, and directive #349 (09-16 01:55 → 02:35)

The interactive session handed the installer lane to headless `08ca8197` at ~01:55 with step 0 "wait for a green CI run
on main before re-cloning"; at 02:11 that run was still queued, and the ruling was (B): arm the stub with CI recorded as
pending, because a stub acquires nothing and the merge gate that applied was the integration replay
(`26-merge-wave-record.md` Addendum 02:12). `08ca8197` re-cut `rehearsal-20260916` at handback commit `cf249594`:
clone `JouleWise-measurement-rehearsal-20260916b`, plan sha `dff929bc…`, t0 03:00:00 PDT (1789552800), install close
02:50 (10-min floor read from the merged code: `PLAN_LEAD_S 480 + INSTALL_CLOSE_MARGIN_S 120`), REQUEST 02:52, TERM
02:54, KILL 02:55, window end 03:15, dead-man 04:20; `--render-only` rc 0; arm census rc 3 on the peer's six detached
bookkeeping seats at 02:00:49, CLEAR at 02:05 (`…08ca8197/10-rehearsal-20260916-arm-record.md`). Attempt 1's notice
send failed — the claude.ai Gmail MCP session had expired — and was classified `arm_transport` → `retry`,
`not_published`, abort epoch 1789549940 (02:12:20 PDT), intended notice preserved verbatim. A headless activation
cannot re-authorise the connector, so `08ca8197` exited cleanly at 02:18 to get a fresh MCP session; the watchdog
mislabelled the exit `usage_exhausted` and held `BACKOFF_USAGE` until 02:29 (relaunch cycle ≈ 11 min). `736e2aed`
launched 02:29:14 with the connector loading unauthenticated — no send tool in the process at all; Ed's own reconnect
returned `not_found_error "Server not found"` (a claude.ai-side outage, req `req_011Cf6t8mYgEBLHarG6c4aBi`); it held,
then exited 02:35 on the peer's GO for one more relaunch probe. The 03:00 t0 lapsed unarmed
(`docs/process_traces/2026-09-16-activation-736e2aed/00-launch-record.md`; `memory/checkpoint-2026-09-16-activation-736e2aed.md`).

Ed filed directive #349 at 02:34:30 PDT (`gh issue view 349`: label `directive`, author `mpmdw`): when Gmail is
unavailable, the arm notice may be posted as a new issue labelled `directive-notice` with exactly the email's content
(plan id, sha, t0, install close, dead-man, clone H, span list); GitHub emails Ed, so the no-objection window and the NO
channel are unchanged; email stays primary; lane NOTICE-TRANSPORT-FALLBACK-01 (`memory/notice-transport-fallback-ruling.md`).

## 3. Component inventory

| File | Contract (one line) | Failure classes | What catches them |
|---|---|---|---|
| `scripts/magistrate_watchdog.py` | LaunchAgent tick every 300 s; launches a headless magistrate only when no plan span is active, the census is clean, stop refs are clear and the clock is sane; resident supervisor drains it at t0−8/−6/−5 min | `CLOCK_UNCERTAIN` (wall/monotonic disagree > 60 s), `NETWORK_UNCERTAIN`, `HOLD_CENSUS`, `HOLD_UNSAFE` (malformed plan, twin, lock), `BACKOFF`/`BACKOFF_USAGE` | Typed states + one transition event each in `events.jsonl`; `installed_agent_fence` reads both plists; `classify_exit` on the session's output tail (`:1343-1348`) |
| `joulewise/night_agent_install.py` (+ `scripts/install_night_agent.sh` wrapper) | One `Transaction` with one commit latch and one teardown dispatching on state; only `LaunchctlAdapter` calls launchctl; deletion requires an `Absent` proof | Class 1 (exit 0 past the clock bound), class 2 (job loaded, plist gone / uninstall lies), signalled installs, teardown exceptions (RETAINED, exit 1) | Three-valued liveness (rc 113 + exact stderr line = ABSENT), record-and-poll signals, 54 + 2 mutation pairs under 3.14.7 and 3.9.6, live launchctl smoke (`08k`) |
| `scripts/run_night.py` | Night driver: t0 gate (census, load, HID, boot clock, custody), chain launch, result/refusal records, courier spawn; owns `install_close_epoch`, `schedule`, dead-man arithmetic (`:64-76, :972-977, :1044`) | Refusals (enumerated codes), chain abort, courier deadline miss | `refusal.json`/`result.json` always written; dead-man job fires after completion + 3600 s and refuses on its own census |
| `joulewise/arm_retry.py` | Pure classifier: `classify_abort` → retry / cold_gate; `retry_allowed` bounds retries by fingerprint, ≥ 60 s spacing, install close, veto | Mis-classifying a physics refusal as retryable | Explicit dictionaries for every code (`RETRY_CAUSES`, `COLD_GATE_CODES`, `INSTALLER_REFUSALS`); tests pin the live `INSTALL_SPANS` |
| `joulewise/arm_census.py` | Pre-publication census; PID-only discovery; idle interactive sessions exempt for `REHEARSAL_STUB` only; `publication_blocked` for stubs | A busy session read as idle (costs one stub) | Workload table over the full descendant tree; UNKNOWN → idle by ruling (`04b`) |
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
| Cost of a zero-capture t0 refusal | ≈ 3 h (full span held) | ≈ 15–20 min (ruled; A212 queued, not landed) | `19-refusal-cost-analysis.md`; `memory/refusal-fast-retry-ruling.md` |
| Install spans | one 03:00–06:30 block per calendar day | `INSTALL_SPANS = (("00:00","24:00"),)`, list-valued, dead-man per span | D-180 cl.1; `run_night.py:76` |
| t0 | fixed minute in the 02:45–03:30 belt (02:56) | any whole minute the margins allow | D-181 cl.1; `…08ca8197/10-…arm-record.md` schedule |
| Windows per day (mechanism) | 1 | ≈ 4–5 estimated with the old 1-h close (`memory/quiet-windows-any-time.md`); derived at the 10-min floor: 10 min lead + 150 min window + 5 min courier + harvest/re-clone/stage (clone+ledger+stage ≈ 3 min on 09-16) ≈ 2.8 h/cycle ≈ 8/day upper bound, before any refusal | this doc's arithmetic; `10-…arm-record.md` timeline |
| CI wall on a code PR | 32–40 min (3.11 + 3.14 matrices, 20-job cap) | 20.1 min measured; ≈ 15 min execution when the queue is clear; red quick tier ≈ 3 min | `10b`, `10-…plan.md` Measurements 2–3 |
| CI jobs, docs-only push | 21 (full matrix) | 4 short jobs | `10-…plan.md` step 3; `ci.yml:57-97` |
| Test count in the full replay | 5653 (PR #312, 09-09) | 6240 across 239 modules, 12 shards | `RUN_STATE.md` T38f; `26a` |
| Installer | 1 zsh script, `$?`-dispatched teardown, two-valued fake launchctl | Python state machine, one commit latch, three-valued liveness, 88-line shell wrapper | §2.6 |
| Worktrees on disk | 314 | 76 | `00-session-record.md` seat 05 |

## 5. What still touches Ed, and known limitations

- **FileVault / login.** Any unattended reboot parks at the disk-password screen and nothing relaunches until Ed types
  it; accepted in D-171 and reaffirmed 09-15 (Ed: FileVault stays ON). `sudo fdesetup authrestart` is a one-shot cure
  Ed must run himself (`memory/checkpoint-2026-09-15-restart-fseventsd.md`).
- **Headless connector re-auth.** The claude.ai Gmail MCP is an OAuth session a running `claude -p` cannot re-acquire;
  a dropped connector costs one clean exit + relaunch (≈ 11 min with the stale-label backoff) and a claude.ai-side outage
  costs the window. #349's issue-transport fallback is ruled but its lane (NOTICE-TRANSPORT-FALLBACK-01) is not landed;
  the relaunch prompt still says email-then-arm only.
- **Stale `last_exit_class` (A197).** A clean exit leaves the previous `usage_exhausted` label in `state.json`, so the
  next tick waits `USAGE_BACKOFF_S[0] = 900` s instead of the 300 s clean cooldown and reports the wrong class
  (`magistrate_watchdog.py:96, :1507, :1714-1723`); read `events.jsonl` for the truth. Registered, not fixed.
- **Refusal cost cure not landed.** A212 is ruled and queued; until it lands a t0 refusal still holds the full span.
- **Machine hygiene is not self-healing.** fseventsd's leak clears only on restart (Ed's sudo); worktree pruning,
  `iw-*` matrix cleanup and orphan fixtures are lanes and a sentinel, not an atexit kill.
- **The first science night still waits for green hosted CI** on its clone head (surviving condition of the 02:12
  ruling) and for a quiet machine: Ed's interactive sessions and the agent desktop apps must be closed through t0.
- **Physics gates unchanged by design:** load > 2.0 refuses (that is what refused 09-15); XProtect/mds/backupd
  > 5 % CPU refuses; the 25F84 → 25G83 acceptance-epoch mismatch still returns `check` rc 3 and gates real numbers on
  ACCEPTANCE-EPOCH-25G83-01's derivation nights.
- **Stale prose on main:** the A172-rendered first-use block in `docs/phase_2/derivation_night_runbook.md:1622-1626` and
  `docs/process/NIGHT_HANDBACK.md:55-59` still reads "25 minutes before t0" and "`t0 − 85 minutes`"; the constants and
  §1.3 say 8 and 10.

## 6. Lessons that became rules

- A headless turn end is a process exit; hold with bounded waits and launch seats detached — `memory/headless-turn-end-kills-seats`.
- Never trust `state.json` `last_exit_class` alone; the transition reason in `events.jsonl` is the exit class — same memory; lane A197.
- Windows are never artificially scarce; every frequency bound must trace to a scientific requirement — `memory/quiet-windows-any-time` (Ed 09-08, reaffirmed 09-15); D-181 cl.1.
- Science quality is the only gate on cadence; arm-to-t0 ≈ 10 min — `memory/speed-pass-directive`; D-171(b) addendum (A210).
- A zero-capture t0 refusal auto-retries; the span ends at the refusal — `memory/refusal-fast-retry-ruling` (A212).
- When Gmail is down, the notice goes out as a `directive-notice` issue — directive #349; `memory/notice-transport-fallback-ruling`.
- Merge on green local replay + quick tier; hosted CI is post-merge confirmation — `memory/ci-postmerge-ruling`.
- Never `gh pr create --body` without the twelve-row ledger; `gh pr checks` must show gate-ledger green; branch protection is the durable fix — `memory/pr-body-gate-ledger-required`.
- Batch bookkeeping pushes; docs-only pushes skip the matrix; cancel redundant queued main runs — `memory/ci-queue-bookkeeping-pushes`.
- Two consecutive fix rounds on one signature → consult, not round three — CLAUDE.local.md rule 11; cold gate 06 Q3; `lt-21`.
- "No round N" rules stop death spirals, not nearly-done designs converging under executed evidence — `memory/stop-conditions-are-antispiral` (Ed 09-15, applied at 23:15 to round 8).
- A bound is observed, not predicted; no invented ceiling constants — cold gate 25 Q2 (`MAX_INSTALL_DURATION_S` rejected).
- Fail-closed only for physics, evidence and pre-registration; operator-only-adversary refusals retire; tolerances are sized to the instrument (≈ 1 J / ≈ 5 J) — D-161; `memory/sensible-gates-directive`; the `codex|claude|t3` census kept (PR #334).
- Unknown liveness means loaded; a fake that cannot express unknown tests the bug, not the contract — `lt-22` Q3.
- Seats run in linked worktrees, never main; briefs under enforced `WRITE_SCOPE` — `memory/codex-seat-launch-rules`.
- Never guard a bookkeeping chain on a clean tree; read every commit's `--stat` before claiming it landed — `memory/bookkeeping-chain-guard`.
- `cd "$W" && …` before any destructive step; `set -e` is not a guarantee in this harness — `memory/bash-chain-cd-guard`.
- Live smoke on throwaway launchd labels is standing-approved before PR/arm — `memory/live-smoke-dummy-label-approved`.
- Offload archives to iCloud, never live worktrees or custody roots; sync clients generate churn — `memory/icloud-offload-directive`.
- Decided ≠ done: a ruling names its implementation lane and the prior mechanism's limit stands until that lane lands — D-180 preamble; D-181 preamble.
