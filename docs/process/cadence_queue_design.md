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

> **11-15 (RL-172 (g)):** for standing queues the per-span magistrate activation of §3 is replaced by the
> controller of §15. `next_action` (§3) stays the library's per-queue view; it does not enforce `not_before`
> or cross-queue debt, and the controller does not call it.

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
  LEG_OVERTIME (two legs over 1.5×). RL-149 §2.4 drops BAND_UNREACHABLE and sets LEG_OVERTIME at two legs. Only these page the lead and the research lead, through
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
- **One span of lag.** A desk-only stop (CONTAMINATED_REDOS, LEG_OVERTIME) is found
  after span k+1 is armed and stops k+2. The magistrate evaluates the MBP-visible stops itself before
  arming. The k+2 rule bounds the debt to one span.

### 6.1 Desk-final from the automatic table (RL-172 section (c), on Sol's conditions)

`scripts/air/cadence_desk.py final` (`joulewise/cadence/desk_final.py`, `desk_transport.py`) is the only path
to line 9's desk-final; `build` keeps the frozen table and writes `desk_final: false`. Sol's probe showed the
frozen desk raises no stop on zero leg rows, skips a missing summary and takes no roster.

**The wire format** is `docs/process/cadence_desk_format.md`, the one contract with the queue controller:
- the controller's SSH-signed bundle commit, with its transition record, goes to the Air;
- the Air's SSH-signed verdict commit goes back to the controller.

**`final`** verifies the bundle commit's signature on the Air. It then judges the bundle against the queue
entry (read from the commit the transition record names) and the kit file. It is final only when:
- the leg ids, order, count and attempts (redos as `runtime.rejected<N>`) equal the roster and the span plan,
  with nothing missing or duplicated and at least one row;
- the kit sha256, frozen commit, plan id, span plan and the consumers' capture leg, its run and its record
  hash all match;
- the manifest hashes to the signed transition record's anchor, and every file hashes to the manifest;
- every feed's own stop proof is present (a feed not proven stopped is INSTRUMENT_FAULT).

**REFUSAL (holds the next arm).** A non-zero receipt rc or error, a failed or missing restore, a failed
stage, no accepted soak, or a close status other than CLOSED_OK. A retried soak that was accepted is not a
stop, and the development pins' receipts (no `soak_attempts`) read as one soak.

**The hand table.** It is mandatory on a redo, an exclusion, a retried soak, a schema change, or a span the
seeded stratified draw (`sha256-hand-sample-v3`, RL-173 E: per span, append-stable, and the first span of each
kit and G0-shape group always) selects. It must carry every comparable field. A disagreeing or incomplete table
holds the next arm.

**Hand gates.** The class A smoke hand-read, the L002 and L005 gates and RL-158 Q1's print are printed and
marked `hand gate required`; the desk never clears them. The Q1 print is counted in line 9's debt by the lead's
typed completion record (RL-173 E; FORMAT section 6).

**Where it runs (RL-173 B).** The same `final` command runs on the MBP as a controller step in the close
interval, and off-host (the Air, or GitHub Actions) from the pushed bundle; a difference between the two verdicts
(`desk_final.compare_verdicts`) holds the next arm (FORMAT section 6).

**Reads and writes.** `desk_verdict.json` is written for every outcome, a refusal included. The desk reads
only `desk_final.ALLOWED_BASENAMES`, each once, and refuses unread anything outside the bundle layout.

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
| `test_desk_final` | 57 | RL-172 (c) desk-final, the #799 gate findings (signed transport and verdict, transition record, legacy pin receipts, command results, complete hand table, seeded draw, reference binding, receipt reuse), the soak retry (no retry, a retry accepted, two refusals), Sol's zero-row probe, a missing summary, a duplicate, roster order and count, redo names, a wrong kit hash, frozen commit and plan id, the span reference, a tampered receipt, the anchor, unlisted and out-of-layout files (unread), every feed's stop proof, the hand table (due, agrees, disagrees), the hand gates, a planted energy key, the CLI |
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

## 13. The campaign runner, `cadence-legs-v1` (RL-149 §5 item 6)

Built on `align/2026-11-14-campaign-runner`. RL-149 governs where this section and the sections above differ.

| Piece | Where | What it does |
|---|---|---|
| Leg kind `cadence-leg` | `joulewise/align/apple/cadence_leg.py`, entry `scripts/cadence_leg_runtime.py` | One type-A leg per invocation: its own G0 (R1 timeout 1,200 s), the band recipe's quiet, one step-task turn with the leg's prompt size, decode cap and seed. Built on the step leg (`StepTask`/`step_spec`, the A-B-A leg's native capture and post-G0 deadman). It writes no energy: no `decode_energy`, no `t_decline`, and its result is refused if a key names energy, power, a slot or a transcript. The ten condition-13 files are byte-identical: the kind subclasses `r1_runtime.Segment` |
| Span driver | `scripts/cadence_legs_runner.py run` | Preflight (frozen commit and paths, night agents, AC, condition 13, the R1 smoke's feeds, powermode 0, display dwell); the plan; one fresh soak (the night's soak path, without its batch window check; one retry after a settle or quiet refusal, RL-171); the roster's legs in seeded order; close (Automatic restore, feeds stopped and hashed, receipt, desk bundle) |
| Plan adapter | `joulewise/cadence/legs.py` `plan_span`; CLI `plan` | worst case = soak + overhead + (roster + redo quota) × leg cap; deadline = t0 + worst case; refuses a t0 whose worst case meets the blackout (RL-149 §2.9 item 6.3); per-leg budgets from the time model |
| Batch admission | `legs.leg_start_delay`, `legs.interval_delay` | Only when `--batch-window` names a blackout: no soak overlaps it, no leg starts in it; a leg in flight finishes. From the qualification pin the default is no blackout (RL-171) |
| Per-leg redo | the driver | RL-72 E2's load rule (`os_load_verdict`); up to the kit's `redo_quota` per span; a rejected attempt stays as `runtime.rejected<N>` |
| Stage stamps | `DIR/chain-stages.jsonl` | A start line (rc null) and an end line per stage, with the probe's five keys |
| Desk bundle | `DIR/desk-bundle/` | `legs/<id>/leg_summary.json` (exactly `desk.LEG_SUMMARY_KEYS`), `span/result.json`, `span/meter.json` (the KM003C stream's header and trailer lines only) |
| Launcher | `scripts/launch_cadence_span.py launch --kit K [--legs ...] [--batch-window ...]` | The desk launcher's procedure (fence, the same LaunchAgent wrapper, Spotlight pause), agent-free like `r1-smoke`; refuses a deadline shorter than the plan's worst case plus the soak retry's budget (one kit soak, RL-171) plus reserves. A separate entry, because `launch_align_r0.py` is in W1's executed closure (via `magistrate_watchdog.py`); it imports that module one way and leaves it at its base bytes |
| Mock | `scripts/cadence_legs_runner.py mock` | The whole span with a fake clock, feeds and leg runtime, then the Air desk on its bundle |

Bands are history recipes (`q0` = the turn starts at the leg's own G0 release). The first leg of a span follows
its fresh soak, the block's cold start. Kits live under `docs/process/cadence/kits/`.


### 13.1 Magistrate note: checkout and kit for the counted pilot (dev-01 L001-L003)

- **Checkout.** The MBP measures from `b4b6aeb192da60d895a7529311b06599efff5be4`, checked out **detached**
  (`git checkout --detach b4b6aeb192da60d895a7529311b06599efff5be4`). That is the kit's `frozen.commit`, and
  the runner's preflight refuses any other HEAD, and any frozen path whose working-tree bytes differ.
- **Kit.** `--kit` points at `docs/process/cadence/kits/cl-dev-01.json` **taken from PR #775's head**, copied
  to a path outside the measurement checkout. The kit file is not in the frozen commit (it was committed
  after it). Against the cold-checked bytes, the kit at the PR head differs in the RL-150 R8 and R7 text and in
  its `frozen` block: `frozen.commit` `b4b6aeb19`, 37 paths, three hashes changed, all launch-side
  (`scripts/launch_cadence_span.py` added, `scripts/launch_align_r0.py` back to its base bytes, the runner's
  docstring). Pin its sha256 in the queue entry.
- **Launch.** `scripts/launch_cadence_span.py launch` (not `launch_align_r0.py`, which no longer knows this
  runner kind).
- **Arm.** `--legs L001,L002,L003` and `--batch-window 02:00-02:35` on every launch (RL-150 §2 F2), with
  `--output` outside every v4 registration and custody root. The arm record states measurement_mode (as
  applied 11-13 23:47) and network time off, checked remotely (RL-150 §2 F5). The first queue holds the
  pilot span only (F3).

## 14. Kit schema v1.1: the cell law and the span-reference leg (RL-155 §5.1; RL-150 R1, R3, R5)

Built on `align/2026-11-14-kit-v1-1`, off PR #775 at `8bd31ae5a`. RL-149 §2, RL-150 and RL-155 govern where
this section differs from them. **v1 is untouched as a schema:** `cl-dev-01` and `cl-dev-02` validate byte for
byte as before, measure from `b4b6aeb19`, and nothing below changes a byte that commit executes for them.
v1.1 is a new schema string and a new runner kind; `kit.load_kit` dispatches on `schema`.

### 14.1 What the runner already takes (verified at `8bd31ae5a`)

- **Per-leg prompt size: yes, below the kit.** `legs.leg_specs` reads each kit leg's `prefill_tokens` and
  `decode_tokens` (the kit's `leg_defaults` only when a leg lacks them), `plan_span` budgets each leg from its
  own size, and the leg runtime builds the step task from the spec's `prefill_chars` (`StepTask(prefill_chars)`,
  `r1_runtime.step_spec`). The leg runtime test already runs a 2,000-token leg.
- **What v1 cannot do:** vary it. The `sha256-v1` law copies `leg_defaults` into every leg and the validator
  refuses any list that is not the law's. So a mixed-size block needs a new law, not new leg code.
- **G0 shape: one only.** `cadence_leg.py` calls `reference_hook(..., capture=True)`: each leg's G0 is judged
  against its own 60 s capture at warm-up entry (RL-150 R1).

### 14.2 The cell law, `sha256-cells-v1`

Inputs: `campaign_id`, `master_seed`, `n_legs`, `bands` (as v1), `prompt_tokens` (the sizes, here
`[2000, 10000, 19458]`) and `g0_shapes` (`["own"]` for v1.1a; `["own", "span"]` for v1.1).

1. **Seeds and bands** are v1's draws on the same `campaign_id` and `master_seed` (tags `seed`, `band`), so a
   leg's seed does not depend on the cell law.
2. **Prompt size by permuted blocks.** `n_legs` must be a multiple of k = len(`prompt_tokens`). Positions
   3b+1..3b+3 (block b) take a Fisher-Yates permutation of the k sizes drawn with tag `size<b>`. So each aligned
   block of three in kit order (L001-L003, L004-L006, L007-L009, L010-L012) holds each size once; two
   neighbouring legs across a block boundary may share a size. Size is balanced against span position (the heat
   history), each size appears 4 times in a 12-leg block, and **the first three legs (a class A pilot) cover all
   three sizes.**
3. **G0 shape** (only when `g0_shapes` holds `span`). L001 is `own`. For each size, the warm legs of that size
   (positions 2..n) are shuffled with tag `shape-<size>` and the first ceil(m/2) become `span`: six span-shaped
   legs in a 12-leg block. A span-shaped leg that is first in its span captures, so the consumers depend on the
   queued layout, and "at least half of the warm legs" is counted on that layout at READY (RL-158 Q6; RL-161
   §1: a chosen cut lands on an own-shaped leg). dev-03 on 3 + 9: 5 of 10 (L002, L008, L009, L010, L012). Draws for size and shape use separate tags, so **v1.1 and v1.1a kits of the same block have
   the same seeds, bands and sizes; only `g0_shape` differs.**
4. `decode_tokens` comes from `leg_defaults` (type A: 4,096).

The anchor size is 19,458 tokens (40,000 characters), so an anchor leg is byte-identical in its prompt to
dev-01's and dev-02's legs. 2,000 and 10,000 tokens are 4,111 and 20,557 characters by the anchor ratio; the
realized count is read back from the bundle, never assumed.

### 14.3 The v1.1 kit (`joulewise/cadence/kit_v11.py`)

| Field | v1.1 |
|---|---|
| `schema` | `joulewise.cadence_campaign_kit.v1.1` |
| `runner.kind` | `cadence-legs-v1.1` (same entry, same LaunchAgent shape) |
| `leg_defaults` | `{decode_tokens}` only |
| `seed_law` | `{method: sha256-cells-v1, master_seed, n_legs, bands, prompt_tokens, g0_shapes}` |
| `legs[]` | `{leg_id, seed, start_band, prefill_tokens, decode_tokens, g0_shape}`, all required, regenerated by the validator |
| `span_template` | v1's keys with **`t0_rule: "free"` in place of `t0_local` and `end_by_local`** (RL-149 §2.9 item 6.3; RL-150 F6-F12 reading 4). Refused if its worst case, plus the blackout, does not fit in a day, or exceeds the launcher's 12 h ceiling. The `plan` refuses a t0 whose worst case meets the blackout, as for v1 |
| checklist `span_window` | for v1.1: `[t0, end_by]` lasts more than 0 s and at most 24 h; when `--batch-window` names one, it meets no batch window. No fixed clock time |
| everything else | as v1: closed keys, `deny_scan`, stop limits, mandatory checklist, frozen fit code for looks, desk adapter |

**Validator rules added for v1.1:** `prompt_tokens` distinct integers in 256..32,768, `n_legs` a multiple of
their count; `g0_shapes` one of the allowed sets; every leg carries its cell; the leg list is the law's.

### 14.4 How the runner consumes the cell (v1.1a: class B under RL-150 R5)

- `leg_specs` takes the leg's own `prefill_tokens` and `decode_tokens`; `plan_span` budgets each leg from its
  size (2k 1,076 s, 10k 1,156 s, anchor 1,251 s under the v1 time model). The runner, mock and launcher
  accept runner kind `cadence-legs-v1.1`; the receipt and plan carry the kit's kind.
- **No byte executed inside a leg changes for v1.1a:** a v1.1a kit (`g0_shapes: ["own"]`) yields v1 leg specs,
  so `cadence_leg.py`, `cadence_leg_runtime.py` and `validate_leg_spec` are the bytes dev-01 runs. The changed
  bytes plan, validate, queue and print: class B (a mock span, a `plan`, a cold check of the diff).

### 14.5 The span-reference leg (v1.1: class A)

**R1's question, answered: no gate-module edit.** A campaign leg takes the span's reference through the
existing `consume` role, exactly as an R1 consumer takes step-D's R_D (`Segment.consume_d_reference`): the
hook loads the source's `align_window_reference.json` with W1's verifier (`thermal_gates.load_window_reference`:
record digest, source config bound by the source runtime's terminal custody, journal re-derivation, sensors
policy) and sets `session.reference` before the G0. `thermal_gates.py` and `r1_runtime.py` are unchanged; the
override lives in `cadence_leg.py` (`CadenceLegSegment`).

- **The span's reference** is the capture of the span's first leg (the first leg after the fresh soak): its
  60 s median at warm-up entry, with the model loaded. That is the series' shape: member 5 captures and the
  later members consume (`align_v4_kit.py`, `capture_last_60s_idle_before_warmup` /
  `consume_member_5_custody_via_WP15`). **Not the soak reference.** The soak's `sensors_c` is a 1,200 s mean
  with no model resident; RL-59/64/72 already moved R1's consumers off the soak onto a captured R_D, and a G0
  judged against the soak would wait for a state the loaded idle may never reach.
- **Roles, per span, by the runner.** The first leg of the roster captures (whatever its kit shape: a span leg
  that is first is judged against itself, which is the span's reference). Every later `span` leg consumes the
  first leg's accepted attempt (`legs/<first>/runtime`). Every `own` leg captures. The leg spec (schema
  `joulewise.cadence_leg_spec.v1.1`) carries `g0_shape` and `g0_role`; the runtime takes `--span-reference DIR`
  for a consumer and refuses it otherwise.
- **A missing or unobserved span reference refuses the consumer before any work** (exit 2, which stops the span
  as any leg-runtime refusal does). It needs a collector fault on the first leg; it is a REFUSAL stop, never a
  silent fall-back to the leg's own capture.
- **Budget.** A consumer's modeled G0 is 600 s (own: 209 s), so a consumer whose G0 runs to its 1,200 s cap is
  still under 1.5 x its budget: a long G0 alone never trips LEG_OVERTIME. The cap and the 2,700 s leg bound
  are unchanged, so the worst case is unchanged (11.4 h for 12 legs).
- **Projection.** The leg result and record gain `g0_shape`, `g0_role` and `g0_reference_source` (a run id);
  the receipt names each consumer's source (`legs[].span_reference`). No temperature, energy or power is
  projected; `leg-summary-v1` is unchanged, so the desk table shows no cell column (the hand-read joins the
  kit by leg id).
- **Which attempt is the source.** The first leg's accepted attempt (`legs/<first>/runtime`). If that leg was
  redone for outside load, the source is the redo's capture, taken after the rejected attempt ran.

### 14.6 Launch bounds, desk marks, review fixes (#788 cold seat; RL-158; RL-161)

- **The fence (#788 F4; RL-155a §3), retired at the qualification pin by RL-171.** `legs.fence_problems` (the
  fence end by 01:50 and the 10:50-13:15 no-launch interval) is no longer called by the launcher, `plan` or the
  checklist; `legs.py` keeps the unused function because the leg child imports that module. With no
  `--batch-window` there is no blackout at all; quiet is the per-leg agent census, process census and rule 5.
- **The desk (#788 F3, F8; dev-01 F8; RL-158 Q2; RL-161 §3 and §4).** `JOURNAL-TABLE.md` gains an `admitted`
  column for every kit. A v1.1 leg summary adds `prefill_tokens`, `g0_shape`, `g0_role` and, for a consumer,
  `span_reference` = {first leg, its supplying attempt, `redone`, `excluded`}; the table gains a cell section
  and prints **MARK: reference from a redo** or **MARK: reference from an excluded leg**, and
  `desk_summary.json` carries `span_reference` with those marks. A consumer's result carries the verified
  reference's `record_sha256` (`g0_reference_record_sha256`).
- **Same span (#788 F8).** A consumer refuses a source that is not `<this span>/legs/<leg>/runtime`.
- **The two drafts share** a campaign id, seeds and run ids: only one may ever run.

### 14.7 Cut-off (RL-155 §5.1)

Sun 15 Nov 18:00 PST. If the span-reference leg is code-complete and has no gate-module edit by then, dev-03
runs on v1.1 (class A: L001-L003 as their own span are its counted smoke). Otherwise dev-03 runs on v1.1a
(class B), pinned at the cell-law commit, and the span leg enters at dev-04 or dev-05 as its own class A kit.

**The two drafts** (same `campaign_id`, master seed 2026111403, seeds, bands and sizes; only `g0_shape` and what
they pin differ). The lead picks one at the cut-off, enters it in the ledger and pins its sha256 in the queue.

| File | Kit | Pin | Class | First span |
|---|---|---|---|---|
| `kits/cl-dev-03.v1.1.json` | cell law and six span-shaped legs (5 of 10 warm legs consume on 3 + 9) | the span-leg commit (re-pinned) | A | L001-L003 as their own span (the counted smoke, one leg per size), then L004-L012 after the hand-read |
| `kits/cl-dev-03.v1.1a.json` | cell law only | the cell-law line (re-pinned on its class B side branch) | B | the whole block, one span |

## 15. The standing-queue controller (RL-172 (g), (f), (c) MBP side, (i) rows 5 and 6)

Opus builder, Sun 15 Nov 2026, rewritten after the #800 gate (Sol: REFUSE, 11 HIGH and 4 MED; Mythos: REFUSE,
5 HIGH, 13 MED and 8 LOW).

| Part | Where |
|---|---|
| The law (pure functions, named reasons) | `joulewise/cadence/standing.py` |
| The I/O (git, `gh`, host readbacks, the launch) | `scripts/cadence_controller.py` |
| The end-to-end synthetic runs | `scripts/cadence_controller_synthetic.py` |
| Install | `configs/launchd/com.joulewise.cadence-controller.plist.template` (KeepAlive, `ProcessType Standard`, Aqua) and `configs/launchd/cadence-controller.config.json.template` |

**The wire contract is the desk's `docs/process/cadence_desk_format.md`** (the lead's decision): the controller
conforms to it and does not re-implement it. It imports:
- `desk_final.pack_bundle`;
- `desk_transport.sign_bundle`;
- `desk_transport.read_verdict`;
- `desk_final.counts_as_final`;
- `desk_final.consumer_gates`.

The controller replaces the per-span work order (the "Start and check", "Run" and "Check" blocks of an item like
331) for campaign spans.

**Frozen paths.** It changes no frozen path:
- no kit pins an added file;
- the controller imports `queue`, `stops`, `desk`, `kit` and `legs` read-only;
- the arm child imports the measurement checkout's own launcher.

### 15.1 Inputs (all read fresh; a missing, stale or contradictory input is a named reason, never a pass)

**On the audit branch, under `records_dir`** (lead data):

| File | Content |
|---|---|
| `STANDING.json` | `joulewise.cadence_standing.v1`, closed schema. **Hand gates are never declared: they are derived** (15.3). Lead records: `gate_records` and `dispositions`. Keys: (1) `queues`: counted queues in priority order with their role (`standing`/`smoke`); (2) per kit sha256: `source` (`commit`, `path`), line 1 and line 2 records, and a batch-window rule (`none`, `rl172`, `HH:MM-HH:MM`); (3) `hand_gates`: extra named gates; (4) `gate_records`: the lead's `release`/`hold` per (plan id, gate); (5) `prior_spans`: hand-armed spans with their kit sha256 and roster (so their hand gates are derived like any other), t0, close and desk-final evidence; (6) `withdrawn`; (7) `dispositions`: `cleared` lifts a desk hold, `rerun`/`withdrawn` takes a span out of line 9's count; (8) v4 `sessions`; (9) `fallback`: F2 queues, or the F0 item; (10) `freeze2` |
| queue files | `joulewise.cadence_queue.v1`; validated with the kits by hash and `qual_roster_problems`; append-only over their whole history |
| `watcher-stamp.json` | `joulewise.cadence_watcher_stamp.v1`; must name the configured watcher (only with `watcher_kind: stamp`, RL-173 C.5) |
| `q1/<plan_id>.json` | the lead's RL-158 Q1 completion record, `joulewise.cadence_q1_record.v1` (RL-173 E; FORMAT section 6) |
| `sessions/READY-<id>.json`, `sessions/DONE-<id>.json` | a v4 session READY, and its end |

**Elsewhere:**
- **The desk's verdicts:** `refs/heads/cadence-desk-final/<plan_id>`, signed by `cadence-desk`. They are fetched
  with the audit branch in one fetch.
- **The owner's open issues:** `gh issue list --author mpmdw --limit 1000`. A full page is unreadable.
- **The host's receipt census:** item 331's census, which also lists every campaign receipt under the output root.
- **The offload markers:** `/Users/Shared/JouleWise/desk-copy/<plan_id>.ok`, typed (15.13; RL-173 A).
- **The Actions watcher's latest completed run** (`watcher_kind: actions`), through the API (15.13; RL-173 C.4).
- **The MBP desk's own verdicts:** local refs `refs/heads/cadence-desk-mbp/<plan_id>`, signed by
  `cadence-controller` (15.13; RL-173 B).

**The controller's memory.** It keeps the audit tip it last read and each queue's first commit and spans. A tip
that does not descend from the last one read halts (`AUDIT_REWRITTEN`). So does a queue whose first commit or
already-read spans changed (`QUEUE_REWRITTEN`). Either one is cleared only by `accept-audit-tip`, after review
(Mythos F4).

### 15.2 The nine conditions, as enforced

1. **Dates.** The local date of t0 must be on or after `not_before`. For development and qualification spans it
   must equal `not_before`; a later date is `DATE_MISSED`.
   - Per date: at most 12 mixed-size and 24 development legs, counting the legs a closed span ran.
   - Qualification needs `freeze2`, stays off development dates, and its blocks use at least two dates.
   - **The lease.** No dated arm within 120 s of midnight. The arm intent carries a lease: the end of the span's
     date less 120 s, the queue's expiry, the watcher stamp's 24 h, and 120 s after the last authority read. The
     arm child refuses to launch past it.
   - **t0.** The recorded t0 is the arm child's own clock, then the runner's receipt `started` (Sol 4; Mythos
     F10, F19).
2. **Line 9 across queues.** Campaign spans are counted in machine order (prior plus controller). Every span up
   to n-2 must count as final by `desk_final.counts_as_final` on its signed verdict (the MBP desk's or the
   off-host desk's), anchored to the `manifest_sha256` this controller published, and, on a v1.1 kit, must have the
   lead's Q1 completion record (`K2_Q1_DEBT`; RL-173 E). A `rerun` or `withdrawn` disposition takes a span out of
   the count (Mythos F8).
3. **Expiry.** Seven days from the queue file's **first** commit, or `expires_at` if that is sooner. An append
   never renews (Mythos F13).
4. **Smoke and pilots.** A span holding the kit's first leg is that kit's pilot.
   - It must be alone in a smoke queue.
   - No other span of the kit is queued anywhere until the pilot closed clean and its class A gate was released.
   - Any other span needs such a pilot (`PILOT_MISSING`).
   - A refused pilot may be re-run alone after a `rerun` disposition.
5. **Typed proofs.**
   - **At the arm:** the readback (powermode, AC, network time, the kernel frequency word, the High Power marker,
     launchd labels, `sudo -n -l /bin/kill`, `measurement_mode.zsh verify`), process absence (monitors, root
     powermetrics, runner/runtime/LaunchAgent processes, any fence not the controller's), no agent (a bounded
     wait), and a **signing probe** (`ssh-keygen -Y sign`; Mythos F11). Then the launch command's result.
   - **At the close:** the receipt's restore, feed stops and command result, plus the same readback and absence.
6. **Trigger.**
   - **Durable state.** State comes from durable files every tick. The arm intent is created once.
   - **Adoption.** After a crash an intent is adopted only if its output exists. A launch fence without an output
     is waited for, not adopted (Mythos F21). Neither halts `ARM_INDETERMINATE`. Nothing is ever relaunched.
   - **Heartbeat.** `heartbeat.json` is written every tick (no fsync while live). The prompt's first act is
     `check-heartbeat`, whose failure is a page (Mythos F15). A dead controller's standing fence expires into the
     watchdog's `desk_fence_stale` notice.
7. **Fresh evidence, twice.** Every authority is read before preparation and **again after the arm proof**:
   - the audit branch, queues, kits, verdicts (both desks), Q1 records, sessions and watcher;
   - the issues, the census and the offload marker.

   The selector must choose the same span again, or nothing arms (Sol 4).
   - **Vetoes.** Any open owner directive starting STOP/NO/HALT/VETO halts, as does a `cadence-stop` issue. A
     failed read is a wait, never "no veto".
   - **The host clock.** It must be within 120 s of the server's `Date` (Mythos F23).
   - **The watcher (RL-173 C).** With the Actions watcher, each arm reads its latest completed run through the API;
     it must have succeeded and have started after the previous close (`WATCHER_NOT_NEWER` is a wait). With the
     Air's hand stamp, one observation under 24 h old may serve several arms, and each arm re-reads it. Either is
     bound into the arm record.
8. **Records and network.**
   - **The transition record.** `transition.json` (FORMAT section 1) is the per-span transition record, and it
     travels in the signed bundle commit. `transitions.jsonl` keeps every arm intent, arm, adoption, close, push
     and page, with their digests.
   - **The standing notice.** The span's line is posted on the queue's standing notice issue before the network
     closes (RL-149 section 2.8; Mythos F16). A queue with spans to run and no notice halts.
   - **The network guard.** Network work is refused after the arm's network phase and while a span or another
     run is live (Sol 3).
9. **Fallback.** F2 queues arm like spans, outside the date counts and line 9. F0 is a page to its standing item.
   Either happens only when no counted span can hold within 2 h 30 min, and only if it ends 20 min before the end
   of a date a counted span is due.

**Every listed queue first (Sol 5).** A missing, invalid, rewritten, halted, expired-with-pending,
notice-less or duplicated queue halts before any candidate is chosen. The same plan id, or the same kit leg
without `rerun_of`, in two queues halts (Mythos F12).

### 15.3 Hand gates, derived (Sol 6; Mythos F2)

At the close the controller derives the span's gates in code:
- `class-a` when the roster holds the kit's first leg;
- `L002` / `L005` from `desk_final.consumer_gates` (dev-03's L002 and dev-04's L005, when span-shaped and in the
  roster).

Each gate holds every later span of that campaign until a `gate_records` entry says `release` for that plan id
and gate. A G0 timeout is not a named stop, so this gate is what holds dev-04's second span after L005 times out.
The desk's verdict names the same gates as `kit:` holds. A verdict naming a gate the controller did not derive
halts (`GATE_DISAGREEMENT`).

### 15.4 The close (RL-172 (c), MBP side; Sol 1, 2, 3)

1. **The interlock.** While a launch fence is held by a live PID, the controller only stats. A deadline that
   passes is a `STRANDED_ALARM` page, never a close.
2. **When the fence goes.** The controller takes its standing fence at once, then proves the runner's processes
   absent (pgrep). Only then does it close.
3. **Packing.** `desk_final.pack_bundle` copies only the allowlisted files: receipt, plan, leg summaries, result,
   meter. It refuses anything else **before reading it**; then nothing is published and the controller halts
   `BUNDLE_REFUSED`.
4. **One set of bytes.** The receipt, summaries and plan are parsed from the packed copy, the same bytes that are
   pushed.
5. **The checks.** The controller's own checks: the command result, the roster and identities, zero leg rows, the
   named stops, and the close proof.
6. **The push.** `desk_transport.sign_bundle` builds the signed parentless commit (`bundle/` and
   `transition.json`). The controller pushes it once to `refs/heads/desk-bundles/<plan_id>`; the same tree again
   is success, another tree a refusal.
7. **The close time.** It is the end of the close work, so the 300 s floor counts after the push (Mythos F25).

### 15.5 The verdict, read (FORMAT section 4)

- **Reading.** `desk_transport.read_verdict` runs on each `cadence-desk-final` ref. It checks the
  `cadence-desk` signature, subject and trailers, `verify_verdict`, and the plan id. A refusal there halts
  (`DESK_VERDICT_INVALID`), as does a verdict on another span or another anchor.
- **Counting.** `counts_as_final` decides line 9. A synthetic run may set `accept_mock_verdicts`, which the
  production config refuses outside `JW_B5_SYNTHETIC_ONLY=1`.
- **Holds.** `next_arm_hold` halts (`DESK_HOLD`) until a `cleared` disposition.

### 15.6 v4 sessions (RL-172 (f); Mythos F5)

- **A READY record** makes `select` return `cede`. The controller pages `V4_SESSION_READY` with the session's
  route, releases its fence, and goes **silent**: no network and no host command until the magistrate
  acknowledges the page after the session's close.
- **Night agents.** A loaded `com.joulewise.night*` agent (a W1, C or T window) also silences the controller.
- **It never launches a session.**

### 15.7 Who wakes whom, and the handoffs (Sol 15; Mythos F14; RL-173 E)

- **The standing fence, continuous (RL-173 E).** The controller holds its own desk fence, which the watchdog
  honours, from startup through arm and close while a queue is live:
  - **startup:** `startup_fence` takes it before the first tick's network work, unless a span it armed is live
    (that launch fence holds the host), an unacknowledged page has handed the host to the magistrate, or a v4
    window is loaded;
  - **every tick and arm stage** renews its deadline (`refresh_fence`), so a long fetch never lets it lapse into
    the watchdog's stale removal; an arm whose fence is gone before the intent halts and writes nothing;
  - **the arm:** the launcher replaces it atomically (below);
  - **the close:** the tick that sees the launch fence gone takes it before anything else, and holds it through
    the push, the MBP desk and the offload.

  Halts, v4 cedes and fallback handoffs release it deliberately. Halts and v4
  pages block until acknowledged. A `WAIT_STALL` notification keeps the live queue's fence held and renewed,
  including subsequent unacknowledged ticks and controller restarts (15.16). `magistrate_watchdog.py` is not touched; the agent census in the arm proof is the
  validity backstop.
- **The arm handoff is atomic.** The arm child hides only the controller's own fence from the launcher's busy
  check, so the launcher's `write_fence` (an `os.replace` under the fence lock) replaces it. The fence file names
  a live owner at every instant. The launcher's bytes are unchanged; this is a call-time substitution in the arm
  child, which the gate should weigh.
- **The close handoff is not atomic.** The LaunchAgent's wrapper unlinks its fence. The controller registers its
  wake (a kqueue on the custody directory) before its last observation of the live fence, and takes its standing
  fence on the wake. The residual is that event latency (milliseconds; Mythos measured 0.1 to 0.2 ms), accepted by
  RL-173 E with the agent census as the backstop.
- **Every wait is bounded (Mythos F7).** It pages `WAIT_STALL` after 30 min (an agent, a refused plan, a missing
  copy marker, a missing standing fence, a failed read), 36 h for a live foreign run or night agent, or 2 h 30 min (anything else). That includes the waits inside the
  arm path.

### 15.8 The journal-copy gate and foreign runs (Sol 10, 11; Mythos F18)

- **The copy gate (RL-173 A).** Every closed controller output and the host's newest campaign receipt retain their own copy debt; each offload marker must exist
  and verify before another arm (15.13). Absent: `JOURNAL_COPY`, a wait. Unverified, a `.failed` file, or the
  controller's own offload step failed: `OFFLOAD_FAILED`, a halt. Either is a global reason, so F0 is held too.
- **Unknown receipts.** A campaign receipt under the output root that no ledger knows halts
  (`UNKNOWN_CAMPAIGN_RECEIPT`). This is the switch-over day's hand-armed spans missing from `prior_spans`.
- **Foreign runs.** When another run's fence goes, its close is recorded as observed with its restore
  **unproven**. That halts until `note-run --restore-ok yes --evidence <its Check>` records the run's Check. It is
  never assumed.

### 15.9 Critical-path ledger (RL-172 (i) row 6; Sol 14)

`critical-path/<span_id>.json` records, per prerequisite (every selector reason, and the arm stages `PREPARE`,
`VALIDATE_PLAN`, `HOST_PROOF`, `AUTHORITY`, `CLOCK`, `NOTICE`):
- its first and last blocking observation;
- `ready_at`, the observation at which it passed.

It also records `ready_all` (set only at the arm intent), `start` (the launch t0), `end` (the receipt) and every
refusal. `ledger` prints the CSV.

### 15.10 The end-to-end runs (RL-172 (i) row 5)

`synthetic` runs five scenarios. Each exercises the whole chain: the controller arms; **the pinned runner of the
kit's own frozen commit** (exported from git) runs its mock; the controller closes, packs, signs and pushes;
then the Air runs the real `cadence_desk.py final --bundle-ref` and `publish`; finally the controller reads the
signed verdict and arms or holds. The lead's acts are explicit (a copy marker, a hand table, a gate release);
no verdict is hand-written.

| Scenario | What it shows |
|---|---|
| `clean` | dev-05 pilot on `2d347f721` (no `soak_attempts`) closes clean. JOURNAL_COPY, then the class A gate, hold dev-05-s02. The verdict is `HAND_TABLE_DUE`, then final with the hand table. The release arms s02 |
| `soak_retry` | qual-01 pilot on `e1b85a59c`, first soak refused. The close is clean; the desk raises no REFUSAL and a "retried soak" hand-table trigger |
| `l005_timeout` | dev-04 pilot with L005's G0 timing out. The close is clean; the derived gates are `class-a` and `L005`; the desk's kit holds match. dev-04-s02 waits through the class A release and arms only after the L005 record |
| `redo` | dev-05 pilot with a load redo, no prior spans. Span 2 arms; span 3 waits on `K2_DESK_DEBT` until the hand table makes span 1 final |
| `tampered` | A bundle re-pushed without the controller's key: the Air refuses it and publishes no verdict. A verdict ref forged without the desk's key: the controller halts `DESK_VERDICT_INVALID` |

### 15.11 What it does not do

- It runs no unit tests on the MBP (RL-172 (i) row 4).
- It reads no thermal journal: the RL-150 R1 and RL-158 Q1 prints stay hand work. The Q1 print is counted in
  line 9's debt by the lead's typed record (RL-173 E).
- It does not decide a re-run, a re-date, a disposition, a gate release or an F0 launch.
- **Watcher stamps.** With the Air's stamp it does not demand a fresh observation per arm: RL-173 C.5 lets one
  observation under 24 h old serve several arms, each re-reading it.

### 15.12 The second gate (Sol: 5 HIGH, 7 MED; Mythos: N1 to N6)

| Finding | What changed |
|---|---|
| N1, Sol R1 | **Packing.** The desk's own deny scan (`desk_final.refuse_denied_content`, imported, not copied) runs on every file packed (`pack_bundle`) and every file signed, `transition.json` included (`sign_bundle`). A hit is `BUNDLE_REFUSED`: nothing is signed or pushed, and a sign-time hit closes the span `STOPPED` without a retry. A symlinked output root, `desk-bundle` root, receipt or plan is refused before any read |
| N2 | **Prior spans' gates.** A prior span carries `kit_sha256` and `roster`, and its gates are derived and released like a controller span's. The pilot rule uses the same gates. The roster and kit are cross-checked against the span's queue entry and its receipt on the host (`PRIOR_CONTRADICTS`). An unreadable kit is `PRIOR_GATES_UNKNOWN` |
| N3, Sol R9 | **Recovery.** The `rerun` and `withdrawn` dispositions also lift the span's desk hold. A smoke queue's "pilot only" counts live spans, so a refused pilot's re-run is appended to its own smoke queue with `rerun_of`. A disposed span's legs may be queued again |
| N4 | **Pages by episode.** An acknowledged page whose situation was absent on a later full evaluation is cleared, and the next occurrence pages again (`-e<n>`) |
| N5 | **Ends of sessions and windows.** The end of a W1, C or T window (a night label that goes) is recorded as a close with its restore unproven, and so is an acknowledged v4 session page. The controller halts until `note-run` with evidence. The 1,200 s floor counts from the observed close, never earlier |
| Sol R2 | **Interlock.** A foreign fence holds the host while its PID lives, whatever its deadline. An unreadable or empty `launchctl list` is `NIGHT_UNKNOWN`: a quiet wait with no network |
| Sol R3, N7 | **The lease.** It counts from the second authority read. The clock check and notice post spend it (`LEASE_EXPIRED`). The arm child refuses the frozen launcher's own `bootstrap` call once the lease has passed, and records that call's instant as t0 |
| N8 | **Commit times.** A first commit dated ahead of the clock is `QUEUE_COMMIT_IN_FUTURE` |
| N9 | **Foreign fences at the close.** A live span accepts only its own launch fence. With its fence gone and another run's up, it waits and does not close |
| N10 | **Verdict refs.** Each verdict ref's tip is remembered, and a tip that does not descend from it is `DESK_VERDICT_INVALID` |
| N11, Sol R8 | **History.** A verdict counts only with `history_source: signed-records`, a clause of the desk's own `counts_as_final` |
| N14 | **Gate records.** A release first committed before its span closed is `GATE_RECORD_PREMATURE`. The verdict-signers file is a line of the arm proof |
| N15 | **v4 windows stay quiet.** Ceded: no host command. Night agents: no fence, nothing synced, a look every five minutes, and a 36 h stall bound |
| N16 | **Leg counts.** A span that never closed counts no legs on its date |
| N17 | **Tests.** The arm child runs against the qualification pin's real launcher with a fake `launchctl`, and `synthetic` resolves its workdir |
| Sol R6 | **The per-span ledger.** A global reason is recorded on every pending head span |
| Sol R7 | **Fences.** No arm without the standing fence held. While a span is live, the kqueue is registered before the tick looks, so no fence removal is lost |

**Left to the desk (#799): Sol R4, R5 and R11; Mythos N6, N12 and N13.**

**Ruled since by RL-173** (15.13): Sol R10 (C.4, C.5), Sol R12 (E, the Q1 record), Sol R7 (E, the continuous fence;
the watchdog is not touched).

### 15.13 RL-173's owner list for the controller builder (fix round 4)

Research lead RL-173 (Sun 15 Nov 11:58). Each item, and where it is enforced:

| RL-173 | What the controller does | Where |
|---|---|---|
| E, watchdog interlock (Sol R7) | The fence is held continuously from startup through arm and close while a queue is live (15.7); the wake is registered before the last observation. `magistrate_watchdog.py` is not touched | `startup_fence`, `refresh_fence`, `run_loop`, `monitor`, `close` |
| C.4 (Sol R10) | `watcher_kind: actions`: each arm (both authority reads) reads the watcher workflow's latest completed run with `gh api repos/<slug>/actions/workflows/<watcher_name>/runs?status=completed&per_page=1&branch=main&event=schedule`. The run must be `completed`/`success`, the configured workflow file, started after the latest close of anything on the host and within 24 h, and not after the host clock. A failed read is `WATCHER_UNREADABLE` (retry); not newer, `WATCHER_NOT_NEWER` (wait); failed or malformed, `WATCHER_FAILED` (halt); none, `WATCHER_RUN_MISSING` (halt). The run is bound into the intent; the lease is its start plus 24 h | `read_watcher_run`, `law.actions_watcher_reasons` |
| C.5 | `watcher_kind: stamp`: the Air's stamp, re-read at every arm; one observation under 24 h may serve several arms | `law.watcher_reasons` |
| E, the draw (Sol R11) | The desk's v3 draw (FORMAT section 5): per span, append-stable, first of each group always | #799 |
| E, Q1 (Sol R12) | The lead's typed record `<records_dir>/q1/<plan_id>.json` on the audit branch, validated by `desk_final.validate_q1_record`; span k's record before span k+2 arms (`K2_Q1_DEBT`), nothing sooner. Invalid, or committed before its span closed: `Q1_RECORD_INVALID` (halt). A kit that cannot be read owes one | `read_audit`, `law.apply_q1`, `law.k2_reasons` |
| E, L002 timeout | A span that raised the L002 gate and whose L002 timed out at G0 (from the packed summaries; for a prior span, its receipt; unknown counts as timed out) halts every arm, fallback included (`L002_TIMEOUT`), until the lead's `release` record for that span's L002 gate | `close` (`g0_unreleased`), `law.l002_reasons` |
| B, the desk | In the close interval, after the push, the controller runs `cadence_desk.py final` from its own checkout on the signed bundle commit, with its own records as history, and signs the verdict with its key under `refs/heads/cadence-desk-mbp/<plan_id>` (local). Either desk's final verdict counts for line 9; either's hold holds; a difference on the automatic part (`desk_final.compare_verdicts`) is `DESK_DISAGREEMENT` (halt, to the research lead) unless the lead records `cleared`. A desk run that left no verdict is retried on the next tick | `desk_close`, `law.apply_verdicts` |
| A.2, A.7 | The offload marker contract below; absent is a wait, unverified or failed a halt; F0 held too | `read_marker`, `law.offload_marker_problems`, `law.census_reasons` |
| A.3 | The maintenance line always lists `bird`, `cloudd`, `fileproviderd` | `MAINTENANCE` |

**The offload interface (consumed, not built here).** The permanent offload tool is built on
`ops/2026-11-15-air-independence`. The controller consumes it by this contract:

- **Invocation (optional).** With `offload_argv` in the config (an absolute program; placeholders `{plan_id}`,
  `{output}` (the span's output directory, read-only to the tool) and `{marker}` (the marker path)), the
  controller runs it in the close interval, after the push and the MBP desk, with a 3,600 s timeout, and
  records its exit code (`close.json` `offload`). A non-zero exit contradicting a verified marker is `OFFLOAD_FAILED` even on the first attempt. Without a marker, retries remain `JOURNAL_COPY` until the three attempts are spent, then `OFFLOAD_FAILED`. Attempts two and three wait 5 and 15 minutes after the previous attempt ended. A changed marker after exhaustion permits a recovery run of the configured tool; its successful exit is required too. The tool must be idempotent on an existing verified marker: validate it and return success without rewriting it.
  With `offload_argv: null` another process runs the tool; the gate is the same.
- **The marker** `<copy_marker_dir>/<plan_id>.ok`, a regular file under 64 KiB, created once when the upload is
  verified, JSON with exactly these keys:

  ```json
  {"schema": "joulewise.offload_marker.v1", "plan_id": "cq-...-a1", "source": "<span output dir>",
   "manifest_sha256": "<plaintext manifest sha256>", "manifest_files": 226,
   "ciphertext_sha256": "<sha256 of the uploaded ciphertext>", "ciphertext_bytes": 110295072,
   "provider": "<provider>", "remote_path": "<object path in the private folder>",
   "upload": {"confirmed": true, "readback": "sha256" | "size",
              "value": "<the provider's read-back hash or size; must equal the ciphertext's>",
              "evidence": "<the provider's confirmation that the upload finished>"},
   "verified": true, "key_second_copy": "<where the key's second copy is>" | null,
   "written_at": "<ISO 8601 with offset>"}
  ```

  `source` is exactly the `{output}` the controller passed; `written_at` falls after the span's receipt and not
  after the host clock (300 s skew). `key_second_copy` may be null only while the current admission time is before
  2026-11-16 11:58 PST (A.1's absolute 24 h deadline), including for older markers. A failed offload may leave
  `<plan_id>.failed` (any content), which holds like a bad marker. The offload tool owns this status file and must remove it before publishing a successful retry's `.ok`; the controller never deletes the failed attempt's evidence. The controller opens nothing else the tool
  writes; the marker carries no denied key.
- **The Actions watcher.** The controller reads the workflow named by `watcher_name` (a file name, e.g.
  `mbp-watcher.yml`) through the runs API. A run concludes `success` when it checked the host's results ref
  (alarm or not); the alarm itself is the watcher's own issue (C.1-C.3). It counts only as a `schedule` run on `main`.

**Install additions:** `controller_signers` (an allowed-signers file naming `cadence-controller` with the
controller's public key), `watcher_kind`, `offload_argv`, `desk_commit` (the commit the off-host desk runs; the
controller's checkout must be at it). The deterministic desk needs no new key. On switch-over day the newest
hand-armed campaign close needs a typed offload marker (a legacy one-line marker is `OFFLOAD_FAILED`).

**Synthetic runs (RL-172 (i) row 5)** add `actions_watcher`, `offload`, `l002_timeout` and `fence`; every
scenario's close runs the MBP desk, and the Air's verdict is its off-host re-check.

**Left open, for the research lead:** Mythos N12 (the reference record hash is bound by the capture run's name
only; the frozen pins record no hash).

### 15.14 Gate 3 (cold Opus seat, REFUSE: 1 HIGH, 2 MED, 6 LOW; Mythos seat, REFUSE: 1 HIGH, 4 MED, 12 LOW)

| Finding | What changed |
|---|---|
| Opus 1 (HIGH): a ceded session or a newer receipt dissolved the copy gate | The copy gate is per span: every controller span that left a receipt, plus the host's newest campaign receipt, needs its own verified marker before any arm, cede or F0 page. `JOURNAL_COPY` also holds a READY session's cede (A.3) |
| Opus 2 (MED): two correct verdicts disagreed | (#799) "schema change" compares with the latest earlier summary; the agreement check leaves out each desk's history-dependent parts |
| Opus 3 (MED): marker not bound to its span | `source` must be the span's output directory; `written_at` after the span's receipt and not after the host clock (300 s skew). Gate 5 corrected A.1's key rule to the current admission clock (15.16) |
| Opus 4 (LOW): a stale desk lock was silent | `MBP_DESK_FAILED` (halt) on a stale lock or three failed runs; the step keeps retrying and the halt lifts when it publishes |
| Opus 5 (LOW): L002 lifted by a disposition; a missing L002 summary read as released | Only the L002 release record lifts `L002_TIMEOUT`; a consumer-gate leg whose summary was not read is "not known" (holds) |
| Opus 6 (LOW): any Actions run counted | The run must be `schedule` on `main` in this repository |
| Opus 7 (LOW): the draw over-selected | (#799) at the desk the history decides first-of-group |
| Opus 8 (LOW): the MBP desk's commit not pinned | Config `desk_commit`; the arm proof's `desk_commit` line checks the controller checkout's HEAD and its clean desk files |
| Opus 9 (LOW): unfenced first tick after an acknowledgement | The tick takes the fence before its network work whenever no page is unacknowledged |
| Mythos T1 (HIGH): only the literal `timeout` counted | Every L002 outcome but `released` counts (`deadman`, `unobserved`, a missing outcome), and a leg with no record though a later leg has one (`law.unreleased`); the prior-span path the same |
| Mythos T2 (MED): a record committed during the offload was premature for ever | Gate releases and Q1 records are judged against the span's receipt time; a release is dated by its latest unbroken presence and a Q1 record by its latest commit, so re-committing recovers |
| Mythos T3 (MED): the Actions read was not bound | The query asks `branch=main&event=schedule`; the law requires `schedule`, `main` and this repository (`head_repository`) |
| Mythos T4 (MED): a stranded page was not delivered; the closing loop spun | While a HALT page is unacknowledged the closing tick does not take the fence; an own fence with time to spare is not rewritten, so the watched directory stays quiet |
| Mythos T5 (MED, #799) | FORMAT section 2 fetches the verdict refs; a history prefix with no record is refused unless `--history-empty` (the controller passes it while it has no MBP record) |
| T6 | = Opus 1 |
| T7 | Gates come from the kit and the queue entry's roster; G0 outcomes and the leg count fall back to the host's receipt when nothing was packed |
| T8 | `controller_signers` is a line of the arm proof (names only `cadence-controller`, carries the signing key) |
| T9 | = Opus 4 |
| T10 | = Opus 2 |
| T11 (#799) | The draw's history clause skips earlier attempts of the same span |
| T12 | Every arm stage renews the fence; a passed deadline is reported `lapsed`, and an arm whose fence is not `held` before the intent halts |
| T13 | Gate 5 corrects informational `WAIT_STALL` pages to retain the continuous fence under RL-173 E (15.16) |
| T14 | A failed offload is retried up to three times in the close interval before `OFFLOAD_FAILED` |
| T15 | = Opus 3; switch-over: the newest hand-armed campaign close needs a typed marker before the first tick (install list) |
| T16 | `desk_code` names the transport, the kit loader and the CLI; the MBP's checkout is pinned (Opus 8) |
| T17 | A second veto issue pages; a foreign-run wait is quiet (nothing synced) with the 36 h bound |


### 15.15 Gate 4 dispositions (Sol fix round 5, 2026-11-15)

Reports: `/Volumes/JW-EXT/scratch/mythos-gate4-800-799/REPORT.md` (ADMIT WITH FIXES) and
`/Volumes/JW-EXT/scratch/opus-gate4-800-799/REPORT.md` (REFUSE), both at #799 `91e26dd66` / #800 `626272a75`.
No fresh admission is claimed. This table supersedes earlier descriptions where they differ.

| Mythos / Opus | Disposition and evidence |
|---|---|
| F1 / 2: premature global L002 release | FIXED. `l002_reasons` checks the release's authenticated commit time against the span's receipt for every campaign and fallback, independently of the candidate. Missing or early time leaves `L002_TIMEOUT` and `GATE_RECORD_PREMATURE`. `Gate4Law.test_l002_release_is_checked_globally_against_the_receipt`. |
| F2: zero-leg receipt or no receipt | PARTLY FIXED. A readable zero-leg receipt stores `[]`; no L002 is invented. Receipt rows are merged with packed summaries, so a started L002 without its summary still counts (Opus 9). A missing receipt remains unknown and holds after rerun/withdrawn: the research lead must choose whether a disposition may release unknown L002 evidence. No fake release is prescribed. |
| F3 / 4: forgotten hand-armed or stranded copy | FIXED. Census retains the newest campaign receipt even after a newer foreign receipt. Every closed controller span with an output owes a copy, including STRANDED without a receipt; all such closes get a completion time and are retried. Gate4Law copy-debt regression. Historical hand spans older than the newest campaign receipt are not retroactively required to have new markers. |
| F4: stale tick time; retry floor | FIXED. Refresh the decision clock after close retries and after watcher acquisition. Desk/offload retry completion advances closed_epoch; every final close records the end of all its work. The 300 s floor cannot elapse during the upload. Gate4Controller upload timeout/floor regression. |
| F5 / 5: fence budget and discarded lapse | FIXED. Long close steps reserve their full timeout plus margin; renew between close proof and log show, before each upload and desk attempt. Every mid-arm renewal acts on lost/lapsed. A default poll still avoids rewriting a fence with time to spare. Gate4Controller mid-arm and upload regressions. |
| F6 / 3,12: offload interface residues | Exit contradiction FIXED. `.failed` remains a conservative hold; the producer removes it before a successful marker (above). DEFERRED to `ops/2026-11-15-air-independence`: prove all descendants have ended, and replace free-text key location/private destination assertions with a jointly reviewed typed contract. The controller cannot infer arbitrary helper identity or verify physical key custody from prose; no broad kill/reap path is introduced. Installation remains gated on that owner evidence. |
| F7 / 8: dispatch documentation | FIXED. Code, query and design require schedule/main/this repository. workflow_dispatch does not count. |
| F8: dead foreign fence waits 36 h | FIXED. An arm missing its own fence uses STANDING_FENCE_MISSING (30 min); a live foreign run retains SPAN_LIVE (36 h). Gate4Law stall-bound regression. |
| F9 / 11: code pin and signer/config/read safety | FIXED. Whole checkout dirty-check at arm and close; isolated desk bytecode cache; missing signing-key .pub fails; production cannot disable the fence; prior receipt read rejects a symlink/nonregular/over-16-MiB file. `accept-audit-tip` is a lead maintenance command, run only at a clean boundary with the controller stopped; its no-op guard is not an arm path and remains an operator prerequisite. |
| F10 / 6: valid rerun draw (T11) | NEEDS RESEARCH-LEAD RULING, #799. Does a disposed executed attempt consume the group's first-span draw? Resolve rerun chains, or count that attempt. Recommend resolving chains; no policy change before ruling. FORMAT now describes actual behavior. F12 sample-plan is an accepted queue-only preview: its printed caveat and FORMAT section 5 already distinguish it from the history-based desk; its hash is exact, its first-of-group prediction is provisional. |
| F11 / 12: history-empty | FIXED auditability/invocation in #799: hash-covered history_empty_asserted; first-record command and host-local lock setup; truthful history error. ASSERTION REMAINS: the operator must fetch all verdict refs and verify the prefix is empty; a machine-verifiable remote-emptiness proof needs an owner contract. |
| F12 / 11: matching refusal, code identity | FIXED in #799: normalize declared local roots only; preserve semantic diagnostics; hash the full 14-file desk import closure. |
| — / 1: old clearance hides later verdicts | FIXED. A disposition's optional verdicts map binds exact verdict_sha256 values by mbp/offhost. A named-stop hold lifts only for the named desk's matching hash. DESK_DISAGREEMENT lifts only on a cleared record naming both current hashes. Missing bindings hold. Duplicate disposition plan ids are invalid. Signed transport commit dates are fixed for reproducibility and cannot date a clearance. New off-host verdicts cannot inherit an earlier clearance. Gate4Law later-verdict regression. |
| — / 7: campaign-scope stops | DEFERRED, #799/#800. All nine current kits use span scope. Campaign-scope support needs shared authenticated history before a future kit uses it; agreement does not suppress such stops. |
| — / 9: receipt row without summary | FIXED with F2: the close merges host receipt rows with packed summaries per leg; a row with no released outcome is unreleased. |
| — / 10: upload attempts too close together | FIXED with F4/F5: delays are 5 then 15 minutes after the previous attempt's end, independent of the 60 s poll. Gate4Controller retry-spacing regression. |

**Research-lead questions (not rulings).** In addition to the draw and unknown L002 recovery above:
Gate 5 resolves the key deadline and informational-stall implementation defects directly under RL-173 A.1/E (15.16).
N12's reference hash is still bound by capture-run name only. Confirm Q1 records for hand-armed v1.1 spans counted in line 9,
and the typed-marker switch-over requirement. A rerun/withdrawn span with desk disagreement currently
needs a cleared record with updated bindings; should there be a non-counting clearance? Free-text custody assertions,
arbitrary offload descendants, and campaign-history support stay with their named owners. The deny scan
covers JSON keys, not arbitrary value semantics; current frozen producers are the supported input surface,
and a stronger value/allowlist projection requires a separately reviewed owner contract.


**Desk-clearance record (gate 4 Opus 1).** A STANDING disposition retains `plan_id`, `resolution`, `record`
and may add `verdicts: {"mbp": "<verdict_sha256>", "offhost": "<verdict_sha256>"}`. Include each desk whose
named-stop hold is being resolved. A disagreement requires both exact hashes and `resolution: cleared`.
A missing binding never clears a hold; legacy three-field records still disposition a bad close (rerun/withdrawn remove its
line-9 count; cleared retains it) but must be extended before they lift a desk hold. A later verdict requires an updated binding.
The producer preserves deterministic fixed Git commit dates; no clearance chronology is inferred from them.


### 15.16 Gate 5 (cold Sol, REFUSE at #799 6b4e32b20 / #800 eb2a2a608)

The four reproduced defects are corrected under RL-173 and RL-172; no new policy ruling is inferred.

| Finding | Disposition and regression |
|---|---|
| F1 HIGH: early keyless marker counted forever | FIXED. A.1's absolute deadline is checked against current admission time, including old markers; an admitted temporary exception also bounds the launch lease, so a slow notice cannot cross the deadline. `Gate5KeyDeadline` advances only now across the boundary; `Gate5Controller` proves an early predecessor marker blocks the next arm. |
| F2 MED: a tick/guard erased a fence lapse by renewing | FIXED. An expired owned deadline is never renewed by refresh or take. Startup preserves it; tick/guard route the lapse to a durable HALT/ARM_INDETERMINATE page before more network or admission. Acknowledgement and a fresh boundary evaluation are required before another arm. Tick, guarded-read and controller-restart regressions exercise callers. |
| F3 MED: WAIT_STALL dropped the live queue fence | FIXED under E's continuous-fence requirement. WAIT_STALL pages retain and renew the fence through unacknowledged polls and restart. Actual halt, cede and fallback handoffs retain their existing release behavior. Regression runs a NOT_BEFORE wait past its stall bound and checks every poll's fence. |
| F4 MED: failed session-directory listing looked empty | FIXED. Failed ls-tree/for-each-ref returns None, distinct from a successful empty listing. Session, Q1 and local desk-ref failures become FETCH_FAILED input reasons and hold selection on either authority read. A failed history listing at desk close cannot assert --history-empty or launch the desk. Regressions include a committed READY entry and faults on both admission reads. |
| Valid rerun draw coverage (LOW, #799) | COVERED for the ruled hash and append stability with a schema-valid three-span rerun_of chain. No hash nondeterminism reproduced. First-of-group treatment of an executed disposed ancestor remains NEEDS_RULING; existing options and recommendation in 15.15 remain, without an implementation decision. |

A failed authority listing is retried as FETCH_FAILED; no work arms or cedes from incomplete authority.
Old keyless markers require second-copy evidence from the offload owner after the absolute deadline; this change authors no custody assertion.
All prior unresolved research questions in 15.15 remain except the deadline and informational-stall implementation defects corrected here. Fresh cold admission, installation and the watched native span remain separate lead gates.
