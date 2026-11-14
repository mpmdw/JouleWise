# Measurement cadence: campaign kit, span queue, Air desk, liveness

Opus builder (Opus 5.5), 2026-11-13 23:10 PST (`date`). Branch `ops/2026-11-13-cadence-queue`.
Ed approved the top three changes of the throughput plan on 2026-11-13: "yes, def do the top
three changes ... design next blocks BEFORE we get the blocks ... blocks should be fairly quick and
modular". The measured basis is `/Volumes/JW-EXT/scratch/throughput-plan/REPORT.md`. Over 11-08 to 11-14
the MBP measured for 19 % of the time. Refused arms that nobody noticed took 44 %. Per-span rulings,
builds, CI and PI decisions took 22 %, and smokes forced by byte churn took 10 %.

This document is a design. It authorizes nothing. Every scientific choice in it, including the
campaign, its legs, its stops and its looks, belongs to the research lead's campaign ruling. The
magistrate's prompt, its launchd job and the arm route do not change until a reviewed PR changes
them (phase 3 below). An independent Sol xhigh design (`/Volumes/JW-EXT/scratch/cadence-sol/MEMO-sol.md`,
22:18 PST) was read after the first draft. §11 lists where the two designs agree and where they differ.

## 0. What exists today (inventory, read-only, 11-13)

| Piece | Where | State |
|---|---|---|
| Magistrate | LaunchAgent `com.joulewise.magistrate` → `scripts/magistrate_watchdog.py` (template `configs/launchd/com.joulewise.magistrate.plist.template`, 300 s tick, resident supervisor). It forks headless `claude` with `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md` | Live on the MBP |
| Work intake | The highest RUN_STATE item that carries a ` ```pointer ` block → `docs/process/CURRENT.json` (`scripts/gen_current.py`; `scripts/gen_state.py` already calls it, so CANONICAL's "integration pending" sentence is stale (Sol)). The magistrate executes the item body's procedure | Every span needs a new lead item |
| Arm route (R1) | `scripts/arm_align_r1.py` → plan writer → `com.joulewise.night{,.deadman}` → `scripts/run_night.py` → `scripts/night_chains/align_r1_rehearsal.zsh` (all at `f006b7aa6`). Smokes go through `scripts/launch_align_r0.py launch` with a desk fence | Driver span fixed at 108,768 s (Sol). It is not a campaign runner |
| Batch window | `scripts/align_r1_rehearsal.py:906-944` `wait_outside_os_batch`: a unit is admitted only if its whole worst-case bound avoids 11:45-13:15 local; two encounters → refusal (`:1023-1027`). The launcher refuses a fresh-soak smoke from 11:05 to 13:15 | Heavy legs are blocked from 10:24 to 13:15 |
| Results | `run_night._publish_terminal_result` pushes `refs/heads/night-results/<plan_id>` (`docs/process_traces/night-results/<plan_id>/result.json`, markers and censuses) about 10 s after the chain exits, refusals included. The 11-08 refusal was published at 01:26 with `verdict GO` and `chain_exit_code 3`. Nobody was watching the ref | Watched only by hand |
| After-session record | `docs/process_traces/<date>-<slug>/AFTER-NIGHT-<activation>.md` (result and packet, runbook §4 restore, dispositions, flags, mail) | Prose per span, 14-16 min |
| Results watcher | `scripts/air/night_results_watch.py`: structure-only `inspect_ref`, early-result and deadline alarms (CANONICAL row "Air results watcher") | Code on main. **Not installed** (`com.joulewise.air-watch` is not loaded on the Air) |
| Pipeline watcher | `scripts/pipeline_watch.py` + `joulewise/pipeline_time/**`, LaunchAgent `com.joulewise.pipeline-watch` (120 s) with ARM_MISSING, SESSION_OVERDUE, CLOSE_ITEM_MISSING and MBP_IDLE | Installed. **It last polled at 17:45:07 on 11-13.** The job is loaded (`runs = 134`, last exit 0) but launchd has not spawned it for about 4 h 50 min. Its heartbeat file is just as old. Tonight's Part C smoke has no live watcher |
| RL-128 probe | `joulewise/pipeline_time/sources.py` `rl128_probe` | A disabled hook. It had no body and no forced command until this branch |
| Desk | `/Volumes/JW-EXT/scratch/mythos-keep-s/mbp/r1fu-1113-desk/scripts/` (`fetch*.sh` rsync allowlisted journals from the MBP; `build_table.py` gate/hold table; `p1.py`..`p6p8.py` prints) | Run by hand, per span |

## 1. Shape of the change

```
 campaign ruling (RL) ──► campaign kit (frozen, validated) ──► BLOCK-QUEUE (blocks designed ahead)
                                                                  │ READY blocks
                                                                  ▼
                                QUEUE.json (ordered spans, finite, expiring; lead writes)
                                                                  │
     magistrate after-session activation:  close span k  ──► next_action ──► checklist ──► arm span k+1
                                                                  ▲                          │
     Air: results-ref watcher + RL-128 probe ── alarms ──┐        │ halts (veto / stop)      ▼
     Air desk (AIR-QUIET.lock) ── named stops ──► cadence-stop issue                     MBP span
```

Two rules hold throughout. First, nothing writes span state into a shared file. Each reader derives
state from evidence: results refs, arm and close records, the probe and the clock. Second, a refusal,
a fault, a stranded span or a named stop never chains.

## 2. The queue file

**Where.** `docs/process/cadence/QUEUE.json` on `main`. It is an operational state record, so its
commit is class A under RL-144 term 1, with no test dependency. Schema `joulewise.cadence_queue.v1`.
Library: `joulewise/cadence/queue.py`. CLI: `scripts/cadence_queue.py validate-queue|next`.

```json
{
  "schema": "joulewise.cadence_queue.v1",
  "queue_id": "cq-conditionless-dev",
  "expires_at": "2026-11-22T12:00:00-08:00",
  "halt": null,
  "standing_notice": {"issue": 812},
  "spans": [
    {"seq": 1, "span_id": "cl-dev-s01", "block_id": "dev-01",
     "kit": {"path": "configs/campaigns/conditionless-v1/campaign_kit.json", "sha256": "<64 hex>"},
     "legs": ["L001", "L002", "..."], "attempt": 1, "not_before": "2026-11-15"}
  ]
}
```

- **Who writes it.** The lead, and only after the research lead's campaign ruling names the kit. The
  magistrate and the Air never write it. Extending it is a new commit that only appends spans. A span
  that has started is never edited. A re-run is a new span with `attempt` + 1 and `rerun_of`, and it
  needs a ruling.
- **Who reads it.** The magistrate reads it at the activation (`scripts/cadence_queue.py next`) and
  records the queue file's sha256 in its arm record. The Air watcher reads it from a private ref
  (`refs/cadence-watch/main`).
- **Validation** (`validate_queue`). The schema is closed, so a span cannot carry a `command`. `seq`
  strictly increases. Span and plan ids are unique. `expires_at` has an explicit offset, so a queue is
  finite. Each span pins its kit by sha256. Its legs are kit legs in the kit's seeded order, at most
  `legs_per_span`, and no leg appears twice unless the later span names `rerun_of`.
- **Ordering and identity.** The plan id is `cq-<span_id>-a<attempt>`, which makes the results ref
  `night-results/cq-…`. The plan writer refuses an existing plan directory, so an arm cannot repeat.
- **Idempotence.** `next_action(queue, evidence, halts, now)` is a pure function. Two activations
  with the same evidence get the same answer. `magistrate.lock` already serializes the activations,
  and the plan writer's once-only directory stops a second arm (§3, races).
- **The veto.** `halts_from_issues` reads open issues by `mpmdw`. Comments are never read, matching
  the prompt's directive rule. Three kinds of issue halt the chain:
  - A `directive` issue whose title or first body line starts with `VETO`, `NO`, `STOP` or `HALT`. If
    it names a span id, only that span is vetoed. If it names the queue id or the words
    "cadence", "queue" or "all", the whole queue halts.
  - A `cadence-stop` issue, which the Air desk opens on a named stop. It halts the queue until the
    lead closes it.
  - `QUEUE.json` `halt` set to an object.

  A veto stops the next arm. It does not stand down an armed span. The current rule stays: Ed's NO
  on the arm notice withdraws a plan whose window has not started (prompt line 16). The email-thread
  NO stays in force until the campaign ruling names its replacement (Sol §11). A controller cannot
  assume that an unread mailbox holds no veto.

## 3. The chaining state machine

**Span states**, derived by `span_state`:

| State | Evidence |
|---|---|
| QUEUED | none |
| ARMED / RUNNING | an arm record names the plan id (a RUN_STATE ARMED item or a pointer `armed`); `chain.started` (from the probe) |
| EXITED | the results ref exists and is a clean completion. Clean means `chain_exit_code == 0`, not `fault`, `chain_outcome` COMPLETE, and the watcher outcome MEASURED_*. `verdict: GO` alone is never success |
| CLOSED_OK / STOPPED | an after-session record exists, with no named stop (CLOSED_OK) or with a named stop (STOPPED) |
| REFUSED / FAULT | the results ref is not clean, or it carries `fault: true` |
| STRANDED | armed, past end-by plus grace, no results ref |
| CHECKLIST_FAILED / WITHDRAWN | the pre-arm checklist failed, or Ed's NO came before t0 |

`TRANSITIONS` in `queue.py` is the legal table. Every bad terminal state is absorbing.

**The decision** (`next_action`). The checks run in this order:

1. The queue is expired, halted or vetoed: **halt**.
2. Walk the spans in `seq` order and skip each CLOSED_OK span. The first other span decides:
   - a bad terminal state: **halt**;
   - EXITED: **close**;
   - ARMED or RUNNING: **wait**;
   - QUEUED and vetoed: **halt**;
   - QUEUED otherwise: **arm**.
3. Before **arm** of span k+2, apply the k+2 rule from the harvest-off contract: span k's desk must be
   final (`desk_final`). If it is not, the decision is **wait** (`WAIT_AIR`).
4. No span is left: **drained**.

**What triggers the next span.** The watchdog already releases a finished `HAZARD_PACK` plan early,
once `result.json` and `courier.sent` exist, no chain is open and no process is left
(`arm_retry.terminal_window_release`). Its next 300 s tick then launches an activation. That
activation reads the governing pointer, which names the queue, and does all of this in one pass:

1. **Close span k.** Uninstall and restore, then run the checks of §4. Read the projected result
   fields. Evaluate the named stops that are visible on the MBP (REFUSAL, INSTRUMENT_FAULT) with
   `joulewise.cadence.stops`. Write the short after-session record and the RUN_STATE item whose
   heading names the plan id and says CLOSED or STOPPED. Commit.
2. **Decide.** Run `scripts/cadence_queue.py next` with the evidence. Anything except `arm`: report
   and exit. A halt or stop pages through the record, the issue and the notice.
3. **Arm span k+1.** Collect the observations. Run `scripts/cadence_queue.py checklist`; every line
   must hold. Post the per-span arm line on the standing notice issue. Write the plan and install it
   through the existing arm route with t0 at the template's local time. Write the RUN_STATE item with
   the `armed` pointer and `wait: result_json_exists` (an existing `POINTER_RULE.md` form, so the rule
   does not change). This is the activation's last act, and the activation exits.

`chain.exited` only wakes the activation. It is not a receipt that the span succeeded (Sol).
Advancement needs the classified result, proven termination, the restore and the close record.

**The daily turnaround inside the 10:24-13:15 blackout.** The span template fixes t0 at 13:20 local,
after the 13:15 end of the OS batch window. It also fixes `end_by_local` at or before 11:45, and the
real value comes from the worst-case bounds (the kit validator checks the fit). A chain that ends near
10:20 is closed and the next span armed during the blackout, when heavy legs could not run anyway.
The arm-notice NO window runs from the arm (about 10:45) to t0 (13:20). RL-144 term 7 is unchanged:
the hub drains 45 min before t0, and nothing runs on the MBP from install to `chain.exited` plus the
courier. The admission inside a span stays `wait_outside_os_batch` with its exact bound. "10:24" is
the plan's shorthand and is never enforced as a constant (Sol).

**What halts the chain.** Any of these: an expired queue; a lead halt; a veto; a `cadence-stop`
issue; a span that is REFUSED, FAULT, STRANDED, STOPPED, CHECKLIST_FAILED or WITHDRAWN; the k+2 desk
debt (this one waits rather than halts); a checklist line that fails. A stop means *stop before the
next span*. It never adds permission to kill an active measurement. The driver's own dead-man and
hazard rules keep that authority.

**How a refusal or fault pages, within minutes:**

- The results ref appears about 10 s after the chain exits. The Air watcher (`cadence_watch`, or
  `night_results_watch` with the queue's plan ids included) polls every 120 s and raises
  `SPAN_REFUSED` or `SPAN_FAULT` at once, before the activation even starts. It pages by
  notification, `alarms.jsonl` and a `pipeline-alarm` issue.
- A silent launch (no `chain.started` by t0 + 900 s) is caught by the RL-128 probe
  (`PROBE_NOT_STARTED`).
- A stall is caught by the probe as `PROBE_STAGE_STALE` or `PROBE_DRIVER_GONE`.
- A missing ref is caught as `SPAN_STRANDED` past end-by plus grace.

**Races and failure modes:**

| Case | Handling |
|---|---|
| Two activations | `magistrate.lock` (watchdog) serializes them. The plan writer refuses an existing plan directory. `next_action` is pure, so the loser sees ARMED and decides **wait** |
| Stale queue | The arm record names the queue sha. A queue past `expires_at` halts. The kit sha pin and frozen-path hashes are checked again at every arm |
| Partial restore | Any checklist line fails or is unobserved → CHECKLIST_FAILED → halt. A missing observation never passes |
| Air offline | Spans continue locally. The k+2 rule stops a third arm until the desk catches up. `cadence_watch` cannot report its own absence, so the lead's session checks `watch-heartbeat.json` age (see §7: tonight's watcher has been dead since 17:45) |
| Results ref missing | STRANDED past end-by plus grace; local custody stays authoritative |
| Power loss in a span | The probe's boot id changes (`PROBE_REBOOT`). The driver is gone without `chain.exited`. Halt; the old plan is never restarted |
| Magistrate exits mid-chain | Expected: no agent runs during capture, and launchd runs the chain. The next tick after the terminal release resumes from evidence |

## 4. What stays per span

Each line is machine-checked at the arm (`kit.CHECK_KINDS`, which every kit must list) or at the close:

- **Restore checks** (both arm and close): AC power, powermode 0, network time OFF, kernel frequency
  word 0, no stray `km003c_monitor`/`hazard_monitor`/root `powermetrics`, no night or align-r0 label
  loaded, no High Power marker, `sudo -n -l /bin/kill` rc 0. The two completed sessions restored
  network time ON and the magistrate set it OFF afterwards, so the close must set and verify the
  campaign's state explicitly (Sol).
- **No agent and no lead SSH while armed** (`no_other_agent`). The RL-128 probe key is the only
  exception.
- **Desk fence and plan fence:** unchanged watchdog code.
- **KM003C capture** (`km003c_ready` at the arm; at the close `meter.present`, `proven_stopped`,
  `bad_polls == 0`, `usb_errors == 0`, any failure → INSTRUMENT_FAULT).
- **Custody hashes:** the frozen paths are hashed again at the measurement checkout
  (`frozen_paths_hash`, `head_is_frozen_commit`), plus the kit sha, the D-7 packet check and the results
  ref's `result_sha256`.
- **Soak plus G0 per leg:** in the runner, one soak per span. The 30B predecessor is dropped only if the
  campaign ruling drops it.
- **A short after-session report:** about ten lines from a fixed template covering the result line,
  restore lines, named stops (or "none") and the next decision.

## 5. Campaign kit and validator

`joulewise/cadence/kit.py`, schema `joulewise.cadence_campaign_kit.v1`. The CLI is
`scripts/cadence_queue.py validate-kit KIT [--repo R]` and `gen-legs`. The schema is closed at every level.

| Field | Content |
|---|---|
| `campaign_id`, `title`, `model` | identity |
| `ruling` | `{id: RL-n, authorizes_spans: true}`. A kit without a standing ruling arms nothing |
| `frozen` | `{commit: 40-hex, paths: {path: sha256}}`. The executed closure: runner, runtime, gate modules, configs and fit code. `verify_frozen` hashes it again at the commit |
| `runner` | `{kind: cadence-legs-v1, entry: <frozen path>, stage_journal: chain-stages.jsonl}`. The probe reads the stage journal |
| `leg_defaults`, `seed_law`, `legs` | The seeded leg list. The `sha256-v1` law draws seeds and a balanced, shuffled band order from sha256, so it is host- and version-stable. The validator regenerates the list, and a hand-edited list is refused |
| `inclusion_rules` | `[{id, text}]`: the ruling's words |
| `stop_rules` | The named stops. A kit may tighten them and never loosen them (≤3 redos, ≤2 unreachable, ≤1.5×). The scope is `span` or `campaign` |
| `span_template` | t0/end-by local, `legs_per_span`, soak, overhead, leg budget and worst-case bound, redo quota. Refused if it overlaps 11:45-13:15 or cannot hold its legs at their worst-case bound |
| `checklist` | `[{id, kind, args}]`. It must contain every `CHECK_KINDS` line exactly once; `disk_free_gb` takes `min_gb` |
| `looks` | `[{look_id, after_legs, fit: {path: <frozen path>}}]`, strictly increasing. Energy is read only by this frozen fit code at these looks |
| `desk` | `{adapter: leg-summary-v1 \| r1-journal-v1}` |

**The condition/slot refusal** (`deny_scan`), which is defence in depth on top of the closed schema:

- **Keys** are refused if any token, split on `_ - .`, is in `DENY_KEY_TOKENS`: condition, slot,
  sabotage, benign, treatment, instruction, contrast, arm, control, placebo, attack, honest, malicious.
  Keys containing `known_h`, `slot_detail` or `condition_label` are refused too.
- **String values** are refused if they carry a registered condition or contrast label: sabotage,
  benign, spam_filter_update, bank_transfer, known_h, X-G/Y-S/X-S/Y-G, `r1_slots`, slot(s),
  condition(s), contrast, instruction(s).
- **Free text** under the keys `title`, `text` and `notes` is exempt from the value scan only.

## 6. The Air desk, automatic and per span

`joulewise/cadence/desk.py` and `scripts/air/cadence_desk.py build` are called by
`scripts/air/cadence_watch.py`.

- **Trigger.** The span's results ref is clean (EXITED) and the projected inputs are present under
  `/Volumes/JW-EXT/cadence-desk/<plan_id>/input`. The watcher then builds the desk once, under
  `AIR-QUIET.lock` (`label=… pid=… start=…`, serialized by an advisory guard). A live holder means
  wait. A lock whose pid is gone is never stolen; it needs the lead and identity evidence.
- **Inputs.** `leg-summary-v1` is the campaign runner's per-leg `leg_summary.json`, a closed key set
  (leg id, seed, band, band reached, G0 s and outcome, wall, budget, attempts, contaminated redos, redo
  reasons, OS max, nominal, stamps) plus `span/meter.json` and `span/result.json`. Any energy, power,
  slot or transcript key, or any unknown key, in our own format is a **refusal** and nothing is
  written (RL-143 2(d)). `r1-journal-v1` is the 11-13 desk's `build_table.py` ported: gate and hold
  `phase_end` metadata, turn counts and finish reasons, with token ids counted and never kept. Only
  allowlisted basenames are opened. The finished text and summary are scanned for denied words before
  anything is written.
- **Outputs.** `JOURNAL-TABLE.md`, `desk_summary.json`, `stops.json`.
- **Named stops** (`joulewise/cadence/stops.py`): REFUSAL, INSTRUMENT_FAULT, CONTAMINATED_REDOS (3),
  BAND_UNREACHABLE (2), LEG_OVERTIME (1.5×). Only these page the lead and the research lead, through
  the alarm and a `cadence-stop` issue, which also halts the queue. Everything else follows its
  predeclared disposition and is recorded without a page.
- **Energy.** No desk code opens it. The frozen fit at a kit look is the only reader, run as its own
  step under the look's terms.
- **How the inputs reach the Air** (open question Q4). The journals live on the MBP. Today a
  person rsyncs them over SSH while the MBP is unarmed. In a chain the unarmed gap is only the
  after-session activation, and RL-144 term 7 forbids fleet SSH from install onward. **Proposed:** in
  the close step, the magistrate runs a frozen projection
  (`scripts/cadence_desk_export.py`, phase 3) that writes exactly the `leg-summary-v1` files into a
  bundle. The bundle is either pushed as `refs/heads/desk-bundles/<plan_id>`, which is public and
  carries no energy, token ids or text, or pulled by the Air over the ordinary key before the next
  install. The research lead chooses.
- **One span of lag.** A desk-only stop (CONTAMINATED_REDOS, BAND_UNREACHABLE, LEG_OVERTIME) is found
  after span k+1 is armed and stops k+2. The magistrate evaluates the MBP-visible stops itself before
  arming. The k+2 rule bounds the debt to one span.

## 7. Probe and watcher (the prerequisite; phase 1)

- **RL-128 forced command** (`scripts/mbp/night_status.py`). It reads the installed
  `com.joulewise.night.plist` `--plan`, the plan's `plan_id` and sha256, `chain.started` (pid and epoch
  only), `chain.started`/`chain.exited`/`courier.sent` existence, the last three `chain-stages.jsonl`
  lines **projected** to `stage_id,kind,rc,started,ended` (never verbatim), the boot session uuid and
  free disk. Driver liveness is the pid's `ps -o lstart` start time checked against `chain.started`'s
  epoch, so PID reuse reads as gone. There is no `kill -0`. The command writes nothing.
- **Install** (the magistrate, in an unarmed span, phase 2). It goes in `authorized_keys` on the MBP:
  `command="/usr/bin/python3 -I -S <repo>/scripts/mbp/night_status.py",no-pty,no-port-forwarding,no-agent-forwarding,no-X11-forwarding,no-user-rc <probe key>`.
- **Air side.** `joulewise/cadence/probe.py` has `probe_argv` (dedicated key, BatchMode, no
  forwarding), a strict `parse_status` and `probe_alarms`:
  - PROBE_DRIVER_GONE, PROBE_STAGE_STALE (1.1 × the largest stage cap), PROBE_NOT_STARTED
    (t0 + 900 s), PROBE_PLAN_MISMATCH, PROBE_REBOOT, PROBE_UNREADABLE.
  - `pipeline_time.sources.rl128_probe` now has its body: the 30-min spacing, the deadline extra and
    the 60-per-night cap, as before; one host-event line per probe in `rl128-probes.jsonl`.
  - `scripts/pipeline_watch.py` runs the probe only while a session is open and turns the report into
    alarms. `RL128_PROBE_ENABLED` stays **False** until the 20-probe calibration of RL-128 passes and a
    reviewed PR flips it and names the record.
- **Results-ref watcher.** `night_results_watch.inspect_ref` is reused, and `cadence_watch` adds
  queue order:
  - SPAN_REFUSED, SPAN_FAULT, SPAN_STRANDED, CLOSE_OVERDUE (1 h), ARM_OVERDUE (2 h after the
    previous results, the RL-127 row), CADENCE_STOP, QUEUE_HALTED, QUEUE_DRAINED.
  - Phase 1 can run today without the queue: install `com.joulewise.air-watch` (Ed runs the
    installer) with `--include-plan` for every active plan.
- **Watcher health.** Pipeline-watch has not polled since 17:45 on 11-13, and launchd still shows the
  job loaded. "Installed" is not "live". The lead's session should alarm when
  `/Volumes/JW-EXT/ledger/watch-heartbeat.json` is older than 10 min. Production chaining requires a
  fresh heartbeat as a pre-arm line. The magistrate cannot see the Air, so the lead posts a
  `watcher-ok` stamp, and that line is ruled in phase 3.

## 8. Blocks designed ahead: BLOCK-QUEUE

`docs/process/cadence/BLOCK-QUEUE.json` (`joulewise/cadence/blocks.py`; `scripts/cadence_queue.py blocks`).

- **Unit.** The unit is a *scientific block*, the study's unit of independence. It is distinct from a
  span. More spans in a day never make more independent blocks.
- **Statuses.** DRAFT → SPECIFIED → REVIEWED → AUTHORIZED → READY → ASSIGNED → COLLECTED →
  DESK_FINAL, plus HALTED and WITHDRAWN.
- **READY is earned.** The validator refuses READY without a kit pin that validates, a review record,
  a ruling and `ready_since`. A block "designed except for one ruling" is AUTHORIZED at most.
- **Target.** `ready_min` 1 and `ready_max` 2 READY blocks beyond the running one. Below that,
  `DESIGN_QUEUE_LOW` names the next block to advance.
- **Workflow.**
  - The lead designs and builds during the long span, on the Air.
  - The research lead's reviews and rulings are batched into the daily turnaround.
  - When a block reaches READY, the lead appends its spans to `QUEUE.json`.
  - Development completion holds the queue (`HOLD_FOR_FIT_FREEZE`), and qualification never crosses
    that boundary automatically.
  - Reserve blocks are specified before they are needed.
- **The committed ledger** holds the throughput-plan calendar as it stands: `pilot-01` SPECIFIED;
  `dev-01`, `dev-02`, `qual-01` and `reserve-01` DRAFT. It reports `DESIGN_QUEUE_LOW` now, which is
  correct.

## 9. Rulings each part amends (for the research lead)

| Part | Ruling | Change asked |
|---|---|---|
| Standing campaign authorization | RL-119 step 4, RL-122 "Authorization" | From one named night to the N spans of one finite queue on one frozen kit, while every checklist line holds |
| No smoke between spans | RL-143 item 1 | A counted 3-leg pilot on the final bytes is the qualification. Unchanged later spans need no smoke |
| Turnaround and notice budgets | RL-127 term 6 | Add "span close to next arm (blackout turnaround) 2 h"; "refused or stranded noticed" 30 min → 10 min |
| Probe | RL-128 terms 2-4 | Term 2 adds `plan_id` and the plan sha256 (attribution in a chain); term 3's "per night" becomes "per span"; the watcher reads the queue |
| Probe in a fleet | RL-144 terms 7-8 | Unchanged (no local timer) |
| Current holds | RL-145 §6, close §12, RL-148 | Stand. No campaign span arms until the campaign ruling names its adopted values |
| Pointer and prompt | `POINTER_RULE.md`, `MAGISTRATE_RELAUNCH_PROMPT.md` line 9 | No rule change: each span's arm item uses `result_json_exists`. The prompt gets one line naming the queue procedure as an arming procedure. That is a reviewed PR, and the cold gate rules on it |
| Email NO | Prompt line 4 | Kept until the campaign ruling defines the standing-notice replacement |

## 10. Rollout and tests

| Phase | What | Gate |
|---|---|---|
| **1. Liveness (now)** | Restart and repair pipeline-watch (dead since 17:45). Ed installs `com.joulewise.air-watch` with `--include-plan`. Merge this branch's probe body (disabled) and forced command after review. Show refusal, missing-ref and silent-launch alarms on synthetic refs | A refused ref alarms in under 5 min on the Air; heartbeat alarm exists |
| 2. Probe calibration | The magistrate installs the probe key in an unarmed span. 20 probes 30 s apart with the hazard monitor (RL-128 gate). Then a reviewed PR flips `RL128_PROBE_ENABLED` | RL-128 CPU and DC-in bars |
| 3. Kit and queue without dispatch | Campaign ruling. The first real kit validates. `QUEUE.json`. Magistrate procedure doc plus prompt line (reviewed PR, cold gate). `cadence_desk_export.py` | `validate-kit --repo` clean at the frozen commit; `next` on recorded evidence |
| 4. Counted pilot | 3 legs, full close, full desk by hand alongside the automatic one; compare the tables | Tables agree; no stop |
| 5. Two serial spans | Full desk final before each next arm (k+1, stricter than k+2) | Turnaround inside the blackout; probe quiet |
| 6. Overlap | Light close, then arm; desk concurrent; the k+2 rule | MBP capture share and refusal-notice latency in the Monday report |

**Tests on this branch** (`tests/cadence/`). All are synthetic, and none contacts a host:

| Module | Tests | Covers |
|---|---|---|
| `test_kit` | 18 | closed schema, condition/slot refusal, seed law, stop bounds, template window and capacity, mandatory checklist, look fit, `verify_frozen` on a git fixture |
| `test_queue` | 12 | format refusals, the clean walk, GO with exit 3 = REFUSED, fault, named stop, stranded, k+2, drained/halt/expiry, transitions, veto scopes and authority |
| `test_stops_desk` | 14 | each named stop, desk tables, planted energy/slot/unknown keys refuse, allowlist, the R1 adapter never prints token ids or planted energy, the quiet lock is exclusive and is never stolen when stale |
| `test_probe_watch` | 18 | the forced command's projection, PID reuse, unarmed; the parser refuses raw lines; probe alarms; the enabled probe body (patched on) with spacing, deadline and log; queue alarms; evidence from RUN_STATE; the output guard; the ledger |

## 11. Cross-check with the Sol design (MEMO-sol.md, 22:18)

**Agreements, adopted here:**

- Liveness comes first, then authorization, then the serial queue, then the overlapped desk.
- `verdict GO` is not success.
- `chain.exited` is a wake, not a receipt.
- The queue holds ordered work and no mutable state, is finite, expires and is append-only.
- A refusal never chains.
- A stop means stop-next, never kill.
- Scientific blocks are distinct from spans.
- READY is earned.
- The k+2 desk-finality rule.
- Energy is read only by frozen fit code; leak guards plant values.
- `AIR-QUIET.lock` keeps its label/pid/start format, with no stale steal.
- The probe is projected, not verbatim; driver identity is checked by start time; `plan_id` is added
  to RL-128 term 2.
- The batch bound is the exact one, never "10:24".
- The email NO stays until it is replaced.
- Watcher health needs its own check.

**Differences, for the lead and the research lead:**

1. **Who executes routine transitions.**
   - Sol: a deterministic `cadence_step` inside the watchdog, so no LLM runs between ordinary spans.
     State is a hash-chained event journal with atomic projection on the MBP.
   - Here: the magistrate activation that Ed's brief describes, made mechanical by a pure decision
     library (`next_action`, `evaluate_checklist`, `evaluate_named_stops`). State is derived from
     evidence that already exists (results refs, RUN_STATE items, custody), so there is no new
     mutable store.
   - Sol's version removes the LLM from the loop and survives an API outage better. It is also a
     larger change to frozen watchdog code. **Proposal:** phase 3 uses the activation, and the
     watchdog-called step becomes phase 7, once the library has run a campaign. The library is the
     same either way.
2. **Status projection.** Sol publishes a `cadence-status/<campaign>` ref. Here the Air derives
   status from the queue, results refs and RUN_STATE. One more ref is cheap, and it becomes worth it
   if a second consumer appears.
3. **Desk transport.** Sol reuses the harvest-off pack, unpack and triage contracts (W1 tooling) with
   a conditionless adapter. Here a smaller projected bundle (`leg-summary-v1`) is used, because a
   conditionless leg has no slots to harvest. The research lead decides. Harvest-off reuse is the
   right answer if custody copies for the Air are wanted anyway.
4. **Pre-arm Air readiness receipt.** Sol requires one. Here only the k+2 rule bounds Air debt, plus
   a proposed `watcher-ok` line. Sol's is stricter; I would adopt it if the research lead wants the
   Air on the critical path.

## 12. Open questions

1. **Scope of the named stops.** Are "3 contaminated redos" and "a band unreachable twice" per span
   or per campaign? Both are coded (`*_scope`), and the kit picks one.
2. **One span of lag** for desk-only stops (§6). Is it acceptable, or must the full desk finish before
   each arm (phase 5 forever)?
3. **Early exit.** A span that ends at 03:00 leaves the MBP idle until 13:20. Should the kit allow a
   short fill span that must end by 10:24?
4. **Desk transport:** a public projected ref, SSH pull before install, or harvest-off.
5. **Counted pilot:** does the 3-leg pilot count toward development (it must be registered before it runs)?
6. **Per-span RUN_STATE items:** keep them (the pointer rule and watchers depend on them) or move to a
   campaign ledger? This design keeps them.
7. **After a named stop:** who may restart, and is it always a new `attempt` with a ruling?
