# Night handback

This file is what the night courier reads first (`NIGHT_COURIER_PROMPT.md`).
The magistrate rewrites the three sections below before every armed night
(ruling R-9, `docs/process_traces/2026-09-01-unattended/MAGISTRATE-RULING-UNATTENDED-STAGE1.md`)
and commits the rewrite with the night's plan. Between nights the sections
hold the standing template text, so a courier that reads this file on a
night nobody armed reports exactly that.

The courier does not decide anything from this file. A **chain** is the child
process running the night's measurements and pauses; its **exit code** is the
integer result returned when it ends. The verdict, that exit code, and every
refusal reason come from the result record under the night's **custody root**,
the directory retaining that night's records: `night/result.json`, then
`night/receipt.json` or
`night/refusal.json` as `result.json` directs. If this file and the result
record disagree, the result record is right and the courier says so.

The **custody parent** is the directory containing those per-night record
directories. The night driver independently reads the plan-configured sibling
path
`<custody-parent>/magistrate/state.json` when it constructs every courier
message; for the production plan layout this is
`~/night-custody/magistrate/state.json`. The email body reports that file's age
and its last `state` decision without importing the watchdog. Operational
liveness is 15 minutes: an age greater than 900 seconds, a missing file, or an
unreadable decision means the watchdog is dead and must be reported as such.

For a status update through `scripts/window_status.sh`, the script inventories
recorded measurement processes before any status-file or Git change. A
**campaign** is one execution of the program controlling a set of measurements,
within a chain or launched separately. Handback delivery alone does not permit
an update: `courier.sent`, the delivery record, does not clear either process
check; `chain.exited`, the chain's end record, clears only the chain check when
its required fields are acceptable. A running recorded campaign, or
**indeterminate** evidence (insufficient to establish whether it still runs),
still stops the update. The [window-liveness contract](../contracts/window_liveness.md)
gives the exact record checks, shared custody-parent settings, decision table,
and operator repair for records whose processes have ended or whose numbers
have been assigned to later processes.

**Live-template timing update — 2026-09-15, INSTALL-WINDOWS-MULTI-01.**
The live schedule, procedure, notice and harvest instructions below use the
D-180 clause 1 / D-181 clause 1 adopted design. They require a measurement
head containing that implementation; they do not establish an arm. Every
Executed section and prior dated addendum remains historical evidence,
verbatim. The arm record identifies the code and schedule actually installed.

## Pre-authorized recovery before a night runs

The **magistrate** is the headless lead agent that prepares and installs a night. A **candidate** is a prepared plan file together with its fixed input files. **Publication** moves the plan to the location where the supervisor discovers it. A **scheduled job** is a task registered with launchd, macOS's task scheduler. An **arm attempt** is one attempt to publish an approved candidate and install its two scheduled jobs. A **retry** repeats that preparation and installation after a recorded arm abort; it never repeats a measurement that started. A **cold gate** is an independent adjudication by a fresh review session. D-180 clause 2 permits the four causes below to be retried without a new cold gate, after the cause has cleared and a fresh notice email has been accepted. The **plan class** is the plan's `receipt_class` value, which selects its measurement or rehearsal path; it stays the same. **Pre-registration** is the scientific protocol fixed before data collection. Ed's NO still overrides. Every physics, evidence and pre-registration requirement still applies.

The **watchdog** is the supervisor that starts and stops magistrate sessions around measurement windows. The **night gate** checks prerequisites before measurements; its **receipt** records the decision and observations. The **driver** is the program that runs that check, launches the measurement chain and arranges result delivery by the **courier**. A **ledger** is the capture-history record; **custody** means retaining the files that establish what ran and what it produced. A **measurement pack** is the fixed collection of experiment instructions and inputs required by a pack-class plan. A **reviewed head**, written H, is the full Git commit identifier of the reviewed code and instructions. A **fingerprint** is the lowercase SHA-256 digest of exact file bytes. A **binding** is a recorded equality tying a plan to its file bytes, head or other fixed input; a **pin** is the expected value in that equality. A **sidecar** is a companion file, such as a stored fingerprint or previous job-file bytes. An **API** is a programmatic service interface, such as the mail-send operation. A **committed installation** means both jobs were loaded, verified and accepted by the installer's final time check; this is separate from recording a Git commit. **Noncommit evidence** positively establishes that this installation did not reach that state. A missing response does not establish noncommit.

The **arm-time census** is the process inventory before publication. The **plan span** is the agent-free interval beginning eight minutes before `t0`, the plan's scheduled measurement start, and ending under the existing chain and courier completion rules. Permission to retry an arm abort does not excuse a process inside that span. `production_census` uses the night gate's raw process check. `handoff_census` checks departure of owned processes only, and `_is_interactive_claude` recognizes command shape only; neither proves the arm or plan-span census clean. A172 changes none of them.

A **zero-capture refusal** is a final night-gate refusal on machine state: one of the five refusal codes that describe the machine rather than the plan (an agent process present, not quiet because of load, power, thermal state, one busy process or a `corecaptured` respawn loop, bind window expired, screensaver guard, or boot clock). The driver's result and receipt must agree, and the result must have null chain fields. The watchdog also checks that no `*.consumed.json` marker exists under the custody root (or a calibration chain's absolute `RUNS_ROOT`), and that no capture file exists under that root's `instrument_validation` directory or, for an evidence night, under `night/evidence`, with `night/evidence_envelopes.jsonl` absent or empty. `courier.sent` records completed delivery, but the courier and driver may still be running. While such a refusal is delivered but not yet released, and only from eight minutes before `t0` until `t0` plus the plan's `window_max_s` plus the five-minute courier deadline, the watchdog checks the agent census and a separate `run_night.py` driver probe on each **tick** (one pass of its periodic check; launchd starts one every 300 seconds, the watchdog job's `StartInterval`). Both probes must be empty on the same tick before the watchdog latches an early release in `state.json`. The driver probe exists only for this early release; after the interval ends, or once the release is latched, no driver probe runs. The release is one-way: the magistrate the watchdog then starts is itself an agent-census match, so a later non-empty census does not restore the hold. The cost is then delivery, harvest (inspection and preservation of the night's records), cleanup and preparation of a fresh plan, not the unused window. For a calibration chain, the driver creates `chain.started` before launching the chain; the chain opens its ledger session during reservation, and no `*.consumed.json` marker is guaranteed to precede that append. The shared disk scan therefore also checks calibration-ledger rows bound to the predecessor plan. The **successor** is that fresh plan: it needs a new identity and **notice** (the email that announces a plan before it is armed), at least 60 seconds after the refusal's final write, installation before its own cutoff, and the usual **owner veto** (a NO reply on the notice email thread) and checks at its own scheduled start. The current next-start planner puts that start at least 40 minutes ahead of preparation, so the 20-minute recovery target is not a guarantee of a new measurement within 20 minutes. Registration and class refusals, or any night whose chain started, keep the full plan-span hold and cold-gate review.

A **listed install span** is a local-time interval from `run_night.INSTALL_SPANS`,
resolved for its local date; an **epoch second** counts from 1970-01-01 00:00 UTC.
`install_close_epoch(plan)` is the exclusive install cutoff, `t0 − 10 minutes`
(the eight-minute REQUEST lead plus `INSTALL_CLOSE_MARGIN_S = 2 × 60 s`);
`PLAN_MAX_AGE_S` is the night gate's 36-hour plan-age limit. A **dead-man** is
the scheduled recovery job after planned completion. A **plist** is a launchd
job file; **UNKNOWN** means a query cannot establish whether a job is loaded.
A **stub** is a rehearsal chain without scientific acquisition. `$STAGE` is the
existing staging directory outside plan discovery. **Unpublication** removes
only this activation's plan from discovery after documented successful cleanup.

<!-- BEGIN ARM-RETRY-POLICY v1 -->

D-180 clause 2; A172 rulings R1–R3 and fix-round-1 R1–R4 (2026-09-15). Exact arm-event IDs are labels for recorded observations, not receipt codes.

| Retry cause | Meaning and required clearance |
|---|---|
| `arm_idle_interactive` | Only an otherwise idle interactive agent session blocked the arm-time census. Its complete descendant process tree must establish no test, measurement or capture work; unknown activity is not idle. Repeat the unchanged census after the session closes; never signal a foreign process. A173 alone owns any future stub exemption. |
| `arm_notice_mismatch` | The notice fingerprint or reviewed head differs from the approved candidate. Recheck preserved candidate bytes and all fixed inputs, then send a new notice. Changed science, custody or unexplained candidate bytes are evidence drift, not a notice-only fault. |
| `arm_watchdog_uncertain` | A watchdog tick (one supervisor evaluation) returned CLOCK_UNCERTAIN (wall and elapsed clocks disagree) or NETWORK_UNCERTAIN (the remote stop check is inconclusive). Let the watchdog clear its hold: two sane clock samples, or a successful network positive control with the stop reference absent. Never clear its state by hand. |
| `arm_transport` | A named mail/API/network/process-transport operation failed before publication, or installation transport failed with positive noncommit and completed cleanup evidence. A bare nonzero exit or lost response is insufficient. Restore transport and obtain accepted notice delivery; after publication require uninstall exit 0, preserved matching bytes and completed unpublication. Committed, retained, unknown or failed-restoration outcomes stop. |

**Gate and driver refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `night_refused_agent_present` | Production census refusal, including a receipt at t0; never an idle arm event. Zero-capture successor route per D-182. |
| `night_refused_not_quiet` | One-shot load refusal for v2, a terminal power/thermal predicate failure, or one named non-observer process at or above 0.5 busy cores over a single 30 s observation at t0 or at the arm check (registration v3; cold gate QPE01-DAEMON-CONTAMINATION-01 ruling 10 Q2, 2026-09-23). Also: more than two launchd spawns of corecaptured (the Wi-Fi log-capture helper) in the last 10 min at t0, detection only, or new spawns persisting 180 s after the arm check's one licensed Wi-Fi cycle (cold ruling 16 Q2, 2026-09-23). The detail names the process, its pid and its share, and the receipt's C3 row carries top_consumers_at_decision. For v4, load is diagnostic and the CPU cutoff is a sealed plan parameter with a named ruling. Zero-capture successor route per D-182. |
| `night_refused_battery_float` | Battery-float predicate failed on a successfully observed reading (ExternalConnected/IsCharging/|InstantAmperage| ≤ 200 mA, directive #421); never waived. Zero-capture successor route per D-182. |
| `night_refused_bind_expired` | Bind window expired with every sample recorded. Load is diagnostic; the CPU cutoff is a sealed plan parameter. Zero-capture successor route per D-182. |
| `night_refused_hid_idle` | Screensaver-configuration guard failed; this is not a live inactivity measurement. Zero-capture successor route per D-182. |
| `night_refused_boot_clock` | Measurement boot/clock guard failed; not a watchdog uncertainty tick. Zero-capture successor route per D-182. |
| `night_refused_registration` | The registration digest is not in the ruled table, or its bound chain-source digest differs from the measured source. |
| `night_window_expired` | Measurement window expired. |
| `night_plan_stale` | Plan age, pinned head, or a clean measurement clone failed; not a stale notice. |
| `measurement_root_outside_custody` | A plan authored at/after 1790340000 whose resolved measurement_root is not strictly inside /Users/edr/night-custody/measurement (acceptance ruling v2.1 R16). Re-author the plan; never a retry cause. |
| `night_plan_malformed` | Plan structure or fields failed their contract. |
| `night_chain_digest_mismatch` | Executable chain bytes differ from their fixed fingerprint. |
| `launch_go_receipt_missing` | Required measurement-pack launch authorization is absent. |
| `launch_go_receipt_invalid` | Required measurement-pack launch authorization is invalid. |
| `night_refused_class_unbuilt` | This gate cannot execute the requested plan class. |
| `night_receipt_class_invalid` | Receipt class/condition contract is invalid. |
| `night_probe_error` | An observation failed; missing evidence grants no permission. |
| `night_aborted_agent_present` | An agent appeared while the chain ran. |
| `night_chain_already_started` | The once-only chain-start record exists. |
| `night_chain_alive` | The existing chain has not been proved ended. |
| `night_chain_launch_failed` | Launch failed after the once-only start claim; not pre-arm transport. |
| `night_courier_running` | The result-delivery process is still running. |
| `night_courier_unavailable` | The driver's delivery executable is unavailable; not a failed notice send. |
| `night_plan_overruns_deadman` | Completion/dead-man schedule was refused; retained even if normally unreachable. |
| `night_record_exists` | A write-once night record proves invocation already occurred. |
| `night_calibration_refused` | The chain's calibration ledger refused (custody timeout, strict pre-reserve, or invalid custody); the document names the exact code; never an auto-retry cause. |
| `night_window_exceeded` | The chain ran past the exclusive window end and was terminated by the driver; reservation or capture intent may have been written and the session may need desk recovery; never an auto-retry cause. |
| `non_observer_process_busy` | Two CONSECUTIVE envelopes were excluded because one non-observer process held at least 30 busy-core-seconds inside each (registration v3's per-envelope integral; cold gate QPE01-DAEMON-CONTAMINATION-01 ruling 10 Q2, 2026-09-23). The chain ends about 31 minutes after t0 with a typed refusal naming the process, its pid and its core-seconds. This is a machine-state abort AFTER capture, so D-182's zero-capture route does not apply by itself; Ed's 2026-09-23 addendum to D-182 licenses ONE new-plan successor when fewer than minimum_retained envelopes were captured (installed by lane QPE01-ABORT-SUCCESSOR-01; until that lane lands the chain ends with no successor); the captured envelopes stay in the archive. One such envelope followed by a clean one never aborts; never an auto-retry cause. |

**Installer §1.3 refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `install_span_closed` | The selected transaction ended; never switch spans mid-install or bypass the plan cutoff. |
| `install_outside_span` | Wait for an allowed span before the cutoff; scheduling wait is not a fifth retry cause. |
| `plan_t0_in_the_past` | Author a future plan through ordinary planning. |
| `night_agent_already_loaded` | A loaded or UNKNOWN job blocks admission; follow harvest/uninstall and human resolution. |
| `plan_outside_custody_root` | Wrong published location; the existing installation rule still applies. |
| `night_plan_malformed` | Invalid plan fields; not a notice-only fault. |
| `plan_schedule_unrepresentable` | The schedule cannot be represented; no new duration ceiling is implied. |
| `install_spans_unresolvable_on_day` | Local-date spans fail resolution; never repair or drop them silently. |
| `plan_t0_not_minute_aligned` | t0 must name a whole minute. |
| `plan_t0_ambiguous_local_time` | t0's local minute occurs twice; choose an unambiguous minute. |
| `retained prior plist: <path>; re-run --uninstall` | A saved previous job file remains; follow the existing human-resolution/uninstall path. |
| `unsupported plist destination: <path>` | The job-file destination is not a regular file; resolve it under the existing path. |
| `--render-only directory must differ from launch_dir` | Use a separate directory for rendered job files. |
| `probe receipt launch_context differs from install: <label>` | The installed night or dead-man job differs from the verified probe rendering; re-run the probe before installing. |

**Other explicit refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `HOLD_CENSUS` | A supervisor census hold alone does not establish the narrowly evidenced idle arm cause. |
| `slot_refused` | A measurement slot refused; cure the finding before any further night. |

Unknown or mixed causes and every capture, clock, custody, ledger or pre-registration guard stay on the cold-gate path; receipt refusals remain ineligible for same-plan retries. Known concurrent refusal evidence overrides an eligible arm cause. These dispositions preserve existing harvest, delivery and human-resolution remedies; they do not call a review into a live chain.

R1's operative time bounds are `now < install_close_epoch(plan)` and plan age within `PLAN_MAX_AGE_S` (including the existing authored-to-t0 check), with at least 60 seconds between arm attempts. D-180's same-or-next-listed-span ceiling is subsumed by `install_close_epoch(plan)` and `PLAN_MAX_AGE_S`, because with whole-day install spans it could otherwise bind 15 minutes before install close. There is no attempt-count cap, separate notice-age limit, new window cadence or delay after a successful harvest.

D-182: binding observations inside the window are not retries. A zero-capture machine-state refusal may license ONE new-plan successor after courier delivery. A successor is a fresh plan with its own id and SHA-256 digest. The evidence-night successor check reads the predecessor (the refused plan), the shared disk facts (chain start, reservation markers, capture entries and envelope index), and the courier.sent delivery marker with message id. run_night.py creates chain.started before starting the chain (lines 536 and 3170); a calibration ledger session is appended only inside that chain, so absent chain.started also proves no ledger session. A bare C5 receipt row supplies none of these disk facts. The successor route also requires the driver's receipt shape with exactly one C5 row; early release keeps the receipt's veto-only role. The check requires the watchdog's early-release latch, at least 60 s since result.ended_epoch_s, and an unspent successor claim; a claim is the create-once file under night-custody/successor-claims that binds the predecessor to the successor id and digest. Real publish-install creates that claim immediately before publication; a rehearsal does not. The real launchctl must be spelled launchctl; any other spelling that resolves to it is refused, never treated as a rehearsal. A predecessor whose plan id cannot name a claim file fails the successor check. The claim binds only until the predecessor's completion time. Re-preparing with changed bytes after failed publication gives up the successor for the rest of that span. Removing released predecessor custody during its span is an operator action that forfeits the successor bound. The candidate still needs a fresh accepted notice, its own future install close, and no observed NO on any notice thread. Never re-arm the predecessor or treat this as a same-candidate retry. Direct install_night_agent.sh performs no successor check; a follow-up lane owns that route.

Every actual attempt sends a newly accepted notice and repeats the existing notice-to-publication lead: accepted email before publication, with no additional minimum interval. A notice is stale if its SHA-256 fingerprint (digest of the exact plan bytes) or reviewed head differs, a newer abort or NO exists, or it belongs to an earlier attempt. A new thread never clears an earlier NO. Waiting observations send no repeated email. Preserve each attempt in `$STAGE/arm-attempts/NNNNNN/` (a positive ordinal padded to at least six digits, without a count limit), created exclusively; never overwrite prior notice, candidate or failure evidence.

`prerequisites_clear` covers census, watchdog, science, custody, no invocation and authorized observable stop/directive checks; `veto_clear` covers directive issues (`gh issue list --label directive`), `standdown.request`/STOP and any NO relayed into a readable channel. Record an unreadable notice thread as a limitation in the attempt directory; it is not a stop and neither clearance boolean requires reading it. Preserve every observed NO; each stops publication.

<!-- END ARM-RETRY-POLICY v1 -->

The ruled-registration table in `night_gate.py` is amended only by cold-gate ruling; each entry names its ruling and the tracked records that hold it (`records`; a test asserts each exists). Its serialized form is pinned by
`test_ruled_registration_serialization_requires_dated_ruling_amendment`; any
amendment requires a dated test comment with the ruling (2026-09-19, record 61a).

For the QPE evidence pilot, isolated `collect_error` and `cleanup_unproven`
envelopes are excluded while the frozen cadence continues. Two consecutive
cleanup failures or a chain refusal/crash abort with a typed refusal document.
A pre-execute refusal has no process journal and nothing to clean. The executor
or courier writes one idempotent cleanup record, proved by process absence,
and the courier reads it and reports success, partial evidence or refusal.
Dispatch uses the admitted receipt's payload identity, never a fresh wrapper
read. This delivery rule includes unproven evidence cleanup (61a addendum 2).
The registered interior starts 60 seconds after the scheduled envelope start;
actual-start drift is recorded and excluded as `start_drift` above 10 seconds.

**Evidence payload probe diagnostics.**

| Exact cause | Meaning |
|---|---|
| `probe receipt kind does not match payload kind` | The receipt describes a different payload; use the matching verify-only probe. |
| `probe payload kind ambiguous` | The pinned chain repeats the payload-kind export, names an unknown kind, or exports both an evidence kind and a calibration ledger. |

A retry-class abort recorded by a prior activation authorises a successor's ordinary fresh-plan arm of the same class without a new cold gate; the predecessor's published plan directory, if any, stays untouched under the existing human-resolution path.

Follow runbook §1.4a for classification, refreshed notice evidence, byte checks
and cleanup. This applies to every plan class; pack authorization stays hard.

## Arm-time census for rehearsal plans

Follow [runbook §0.6 step 3b and §1.4](../phase_2/derivation_night_runbook.md#06-census-clean-and-the-night-is-agent-free): only a parsed `REHEARSAL_STUB` plan may treat an idle interactive Claude or Node/T3 session as not foreign, unknown observations count as idle, the caller's own PPID chain is exempt, the own interactive or headless root receives the same stub-only idle-tree exemption (workload descendants still block; sibling seats outside its subtree remain foreign), and the new census blocks publication only for that stub class while other classes retain the existing all-agents-closed rule with diagnostic output.
All agents must still close before the plan span: the unchanged night gate records `night_refused_agent_present` for an agent hit, real chains do not start on that refusal, and rehearsals retain their harmless-stub continuation and census-hit recording; the runbook's §8 owns the term definitions.

## Purpose of this night

Plan `qpe01-pilot-n1-20260923-0700` is the third attempt at QPE-01's
idle-variance PILOT NIGHT ONE, using the evidence executor (the program the
chain runs to take the night's measurements). QPE-01 asks how
much the machine's own idle energy draw varies from one ten-minute stretch to
the next. Each measured stretch is an **envelope**: 600 s of power capture.
Only its middle 480 s, the **interior**, is used as energy; the interior
starts 60 s after the envelope's scheduled start, so start-up and shutdown
effects fall outside it. This night takes twelve envelopes with nothing else
running on the machine.

**Attempt 1** was plan `qpe01-pilot-n1-20260922-0217`, which ran 02:17–04:27
PDT on 2026-09-22. The gate said GO, the chain captured all twelve envelopes,
cleanup was proven, and the night was harvested — but the pilot summary (the
report computed from the night's files by fixed rules, set out under "What
happens with the result" below) came out **INCONCLUSIVE**: only 2 of the 12
envelopes survived the pre-registered exclusion rules, and two envelopes cannot
form even one of the adjacent pairs (envelopes 1 and 2, 3 and 4, and so on)
whose energy differences set how many envelope pairs the follow-on experiment,
block two (described below), must measure. Its full record is the Executed block for that
plan id below. Two separate causes were found, and both were ruled and cured
on 2026-09-22 (records under `docs/process_traces/2026-09-22-activation-59857fe5/`
and the two cold-gate packets cited there). Both cures remain in force,
unchanged, on this night:

1. **Seven envelopes lost their clock anchor.** A **clock anchor** is the
   tie between the power samples' own timestamps and wall-clock time; it
   is what lets the night state which real seconds an envelope covered.
   macOS's `timed` service continuously corrects the system clock — this
   is **clock discipline** — and on that night its corrections exceeded
   the old anchor's flat 5 ms absolute caps, so no anchor could be
   established and the envelope was excluded with the reason
   `clock_anchor_unresolved`. The cure is clock-anchor version 3.1: the
   cap is now rate-aware, meaning a sustained frequency correction is
   priced against the envelope's own length instead of being compared to
   one flat number, under a frozen 15 ms absolute backstop that no rate
   arithmetic can talk past, with integer-nanosecond tiling so the
   arithmetic itself contributes no rounding. Version 3.1 also gives
   every envelope an **attestation**: a statement, read back from the
   `timed` log in the gap after that envelope's capture, about whether
   the clock was being corrected during it. Its three states are
   `authenticated` (the log is provably the output of the ruled query and
   shows no correction in that envelope's window), `slew_attested` (the
   log shows a correction) and `asserted` (the log could not be read or
   parsed, so nothing is established). **Only an `authenticated` envelope
   is claim-bearing**; the other two states exclude the envelope under
   the reasons `network_time_slew_attested` and `network_time_unattested`.
2. **The schedule slipped.** Each envelope was started only once its
   predecessor had finished writing its files out, so every envelope
   after the first began 7.6–10.2 s later than the frozen schedule said,
   and the lateness was inherited down the night. The cure separates the
   schedule from the capture: envelopes are now started on a fixed **slot
   pitch** of 620 s — 600 s of capture plus a 20 s gap for the previous
   collector (the process that captures one envelope's power samples) to
   finish and for the attestation query — each measured from its own
   scheduled instant rather than from its predecessor's finish. The same
   cure fixed `start_drift_abort_s` 2, a pre-registered stop rather than a
   data filter: if any envelope after the first would begin more than 2 s
   after its own scheduled instant, the chain refuses the whole night there
   and then, before that capture starts, writing a `start_drift_abort` row.

**Attempt 2** was plan `qpe01-pilot-n1-20260922-2100`, which ran 21:00:01 →
23:13:51 PDT on 2026-09-22. Both cures held: the gate said GO, chain exit 0,
twelve envelopes captured with cleanup proven, attestation `authenticated` on
all twelve, every clock anchor established within its caps, and **start
drift** — how many seconds after its scheduled instant an envelope actually
started, as seen by the chain — 0.191 s on envelope 1 and 0.150 s on
envelopes 2–12. **But the machine was not idle.** The macOS
file-system-events daemon `fseventsd` used one full processor core in every
30 s load sample all night — it was stuck in a `scan_old` failure loop that
macOS's system log (the unified log) shows from 04:49:03 PDT that day, sixteen hours before t0 —
and the Photos analysis daemon `mediaanalysisd` added 1.3–1.8 cores for about
five minutes inside envelope 1. Each interior read ≈ 305 J (envelope 1:
649.69 J) where attempt 1's two retained envelopes, on the same machine five
hours earlier, read 154.88 J and 151.03 J: about 153 J more over 480 s, or
about 0.32 W, the right order for one busy core on this processor. Nothing on
the night could see it. The census looks only for agent processes (command
lines matching `codex`, `claude` or `t3`), and under registration v2 the
load figures were a **covariate** — recorded beside the energy for a later
reader, never used to exclude an envelope. Harvest record:
`docs/process_traces/2026-09-22-activation-a022aecc/01-qpe01-pilot-n1-20260922-2100-harvest-record.md`
(§6 is the diagnosis; the §2 addendum carries the ruled label; of the two
dated addenda at its end, the 03:10 PDT one by magistrate 7a0f14bd is the
correction in force for the observer accounting described below).

The loop was caused by `launchd`, macOS's service manager, respawning
`corecaptured`, the Wi-Fi log-capture helper, about every 80–95 seconds. Each
spawn made `fseventsd`, the file-system event daemon, replay its event history
and burn one processor core. Both the pre-arm check (the **arm check**: the checks that run before a night is installed) and the night gate at `t0` read `/usr/bin/log show --last 10m
--style syslog --predicate 'process == "launchd" AND eventMessage CONTAINS
"corecaptured"'` and counts lines of this exact form from the captured log:
`2026-09-22 10:23:33.210175-0700  localhost launchd[1]: [system/com.apple.corecaptured [38329]:] Successfully spawned corecaptured[38329] because xpc event`.
The arm check (on a real arm, never a rehearsal with a fixture `launchctl`) toggles Wi-Fi once if it counts at least three spawns, waits at
least three minutes after Wi-Fi is back on, and counts only new spawns. One or
more new spawns triggers `/usr/bin/sudo -n
/usr/local/sbin/joulewise-restart-fseventsd` once and refuses the arm check
with `night_refused_not_quiet` (the refusal code for a machine that is not quiet). That restart runs `pkill -x fseventsd`;
launchd respawns the daemon. The following `machine_quiet` row observes for
30 seconds and refuses any non-observer process averaging at least 0.5 busy
cores, including `fseventsd` if it remains busy. If any earlier arm check
fails, the `corecaptured` row reads the log for a count, records remediation
`not_licensed`, and fails if the count exceeds two; it does not touch the radio
or restart the daemon. A failed log read refuses at the arm check. At t0,
the admission check reads the log and refuses above two spawns; it never
actuates. Its read adds about 1–3 seconds before the existing 30-second
processor observation. A failed t0 log read is recorded as not measured;
the processor check still guards the machine.

A cold gate, QPE01-DAEMON-CONTAMINATION-01, ruled on that night in three
rounds; its packet is
`docs/process_traces/2026-09-22-activation-a022aecc/03-coldgate-packet-daemon-contamination/`.
Ruling 10 (Q1) keeps the night in the record exactly as registered, under the
label "MEASURED ON A NON-IDLE MACHINE", and not used to size block two — the
follow-on experiment that will add a small deliberate CPU load and measure its
extra energy against idle envelopes, whose number of envelope pairs the pilot
exists to choose. Ruling 10 (Q3, §4) orders the pilot re-run ONCE under a new
registration — the protocol file fixed before any data is taken — v3, set
out in the next paragraphs, "on a machine passing the t0 predicate" —
the check at t0 that no single outside process is busy, rule 1 below. **This
night is that re-run.**

**The quantities v3 is built from.**

- A process's **CPU time** is the number of seconds of processor-core work
  it has consumed; macOS `ps` reports it as a running total. If that total
  rose by c seconds during an observation lasting I seconds, the process
  averaged **c ÷ I busy cores**: 15 s of CPU time over a 30 s observation
  is 0.5 busy cores, and a process keeping one core fully occupied is 1.00.
  The code reads `ps` before and after a `top -l 2 -s 30` interval
  (`joulewise/quiet_admission.py`, `sample_interval` and `interval_metrics`).
- **Core-seconds** are busy cores multiplied by seconds: one full core for
  30 s is 30 core-seconds, and so is 0.05 of a core held for 600 s.
- An **observer** process is one the measurement itself started: the
  night's executor, which is the root of the chain's process tree, and every
  process reached from it by following parent–child links down — the
  collector, `sudo`, `powermetrics` (the power sampler, reading every
  100 ms), `top`, the collector's census and the load recorder (the night
  driver's own census runs in the chain's parent, so it is not an observer).
  The executor's process
  id is the **chain root pid**. Every other process on the machine is a
  **non-observer**.
- The **load recorder** is one process the executor starts beside the
  collectors. Every 30 s it writes a row to `night/evidence_busy_cores.jsonl`
  (the **journal**) listing the ten busiest processes of that 30 s interval
  (`top_consumers`), each with its pid, command, busy cores and an `observer`
  mark, true or false. v3 starts it as `record --observer-pid <chain root
  pid>`; a process is marked observer when following its parent pids leads to
  that root.

Why the marking had to change first: under v2 the recorder marked only its
own descendants, so not one journal row on either archived night carried
`observer: true`, and `powermetrics` — started by the collector, not by the
recorder — read as a non-observer at 0.094–0.112 busy cores (ruling 10 §1;
synthesis 15, "BLOCKER, both seats"). Any rule over non-observers would have
blamed the power sampler.

**What registration v3 changes.** A **registration** is the protocol file
fixed before any data is taken; the night gate admits a plan only if the
file's SHA-256 digest is in the gate's ruled table. This night's is
`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json`,
sha256 `69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616`,
the file `joulewise/night_gate.py` names as `QPE01_PILOT_REGISTRATION_PATH`
with that digest as `QPE01_PILOT_REGISTRATION_SHA256`. v2 (`2c539240…79f1`)
stays in the table as superseded history: a new plan pinned to it refuses
`night_refused_registration`. v3 keeps every v2 number — `settle_s` 600 (the seconds the chain waits
after starting before envelope 1),
`envelope_s` 600, `slot_pitch_s` 620, `envelopes` 12, `interior_offset_s`
60, `interior_s` 480, `start_drift_abort_s` 2, `start_drift_max_s` 10,
`minimum_retained` 8, `minimum_adjacent_pairs` 4, `top_up` false,
`window_max_s` 9000 — and the tracked chain-source digest (`568a2771…51b7ea`)
is unchanged. It adds four rules and one corrected statistic. Their sources
are ruling 10 §3 (Q2) as adopted in synthesis 15, the brief
`docs/process_traces/2026-09-22-activation-a022aecc/04-brief-nonobserver-predicate-v3.md`
(items 2–6), the seat report
`docs/process_traces/2026-09-22-activation-a022aecc/05-nonobserver-predicate-seat/00-seat-report.md`
and the magistrate's fix-round record
`docs/process_traces/2026-09-22-activation-a022aecc/08-magistrate-fix-round-record.md`.

1. **Before capture: no single non-observer at 0.5 busy cores or more.**
   The pre-arm `check` and the night gate at t0 each take one 30 s
   observation, marking observers from the checking process's own pid (no
   `powermetrics` exists yet at either moment). If any one non-observer
   process averages 0.5 busy cores or more, the arm `check` records
   `armable: false`, and at t0 the gate refuses `night_refused_not_quiet`
   with the detail `non-observer process busy: <basename> pid <pid> at
   <busy cores, 3 decimals> busy cores over <seconds, 1 decimal> s (bar 0.5);
   observation in top_consumers_at_decision`; the receipt's C3 row (its
   machine-state row) carries `top_consumers_at_decision`, the observation's
   busiest processes. Nothing has been captured, so D-182's
   zero-capture successor route (table above) applies. Why 0.5: it is half
   the runaway signature (1.00 core), and it is above every single 30 s
   sample of any other non-observer process on either archived night — the
   largest being `XprotectService` at 0.353 in one row on attempt 2; the
   largest recurring one is `corespotlightd`, at most 0.104 over 14 rows
   (harvest record §6 table). Ruling 10 §3(i) states the margin as "5× the
   largest single-sample transient … (`corespotlightd` 0.104)"; that
   overlooks the 0.353 row, so the true margin over any observed transient
   is 1.4×, not 5×. Worked example: last night's `fseventsd` at 1.00 busy
   cores is refused before any chain starts; `XprotectService` at 0.353 and
   `corespotlightd` at 0.104 pass. A process that stays below 0.5 but runs
   for long is caught by rule 2. An observation that fails or cannot be read
   is `armable: false` at the check and `night_probe_error` at t0, never a
   pass (seat report §4a, §2 F3). The check spends this 30 s observation only
   on an evidence chain (record 08 §3, F12).
2. **Per envelope: 30 core-seconds from one non-observer excludes it.** For
   each envelope, take the journal rows whose 30 s interval lies wholly
   inside that envelope's scheduled 600 s. For each non-observer process —
   identified by pid together with its start time, so a recycled pid counts
   as a different process — add busy cores × interval seconds over those
   rows. A total of 30 core-seconds or more excludes the envelope with reason
   `non_observer_process_busy`, recorded with the process's name, pid and
   core-seconds. Why a total and not a median: an eight-row (four-minute)
   burst at 1.5 cores is 8 × 1.5 × 30 = 360 core-seconds, about 115 J at the
   0.3194 W per busy core below (1.5 × 240 s × 0.3194 W; ruling 10 put it
   near 270 J using ≈ 1.1 W of extra draw), yet it passes a twenty-row
   median, because twelve of the twenty rows are near zero; the total
   catches it (ruling 10 §3, MATERIAL, and its regression 6). Why 30: it is 0.05 of a core — the
   smallest extra load block two is registered to add — held for 600 s.
   Spread evenly over the envelope, 30 core-seconds is 0.05 core; only the
   480 s interior counts as energy, so that is 0.05 × 480 = 24 core-seconds
   inside it, and at 0.3194 W per busy core about 7.7 J (0.05 × 480 ×
   0.3194 = 7.67), above the ≈ 5 J smallest energy difference the project's claims
   rest on (v3 `non_observer_process_busy.bar_basis`). The 0.3194 W is the
   extra power attempt 2 drew with `fseventsd` on one core, (306.2873 −
   152.9535) J ÷ 480 s (ruling 21 §2); it is a rate for one daemon on an
   efficiency-class core (one of the processor's low-power cores), used
   here only to size the bar. Worked examples:
   attempt 2's journal, run through v3's own summary code on a copy in which
   the observer processes are marked by command name (the archived rows carry
   no marks), loses every envelope — `fseventsd` at 544.7–575.6 core-seconds,
   and `mediaanalysisd` at 528.1 in envelope 1 (seat report, fix round 2,
   R2); attempt 1 loses none, its largest non-observer total being 6.3
   core-seconds (`WindowServer`, envelope 2; ruling 10 §3), 4.8 times under
   the bar. A process below the bar does not exclude an envelope by itself:
   `XprotectService` reached 10.7 core-seconds in envelope 12 of attempt 2 and
   alone would have left that envelope in, as idle variance by design (ruling
   10 §3).
3. **Two excluded envelopes in a row end the night.** If envelope n and
   envelope n + 1 are both excluded under rule 2, the chain stops and writes
   `night/refusal.json` with reason `non_observer_process_busy`, naming the
   process, pid and core-seconds. The earliest this can happen is after
   envelope 2: t0 + 600 s of settling (the chain's wait before envelope 1) +
   2 × 620 s = t0 + 1,840 s after the chain starts; the chain starts only
   after the t0 gate's own 30 s observation (rule 1), so about 07:31:10 PDT
   for this plan. One excluded envelope followed by a clean one never
   aborts.
   Why: a daemon stuck the way `fseventsd` was would otherwise spend the whole
   2.2-hour span on envelopes that will all be excluded (ruling 10 §3,
   "Abort count"). This abort comes AFTER capture, so D-182, which licenses a
   successor only when nothing was captured, does not cover it. Ed ratified
   an addendum (`docs/decision_log.md`, D-182 "Addendum (2026-09-23)", Gmail
   `1a0cd4d699a90f29`): such an abort with fewer than `minimum_retained` (8)
   envelopes captured licenses one new-plan successor. **The code that
   installs that successor has not landed**: the successor-installing change
   (lane A270, QPE01-ABORT-SUCCESSOR-01) is registered in `TASK_QUEUE.md` but not
   implemented, and
   `joulewise/arm_retry.py`'s own text for this reason says "until that lane
   lands the chain ends with no successor". On this night, therefore, the
   abort ends the span with no successor; the captured envelopes stay in the
   archive, and any later night is an ordinary new arm.
4. **In-chain marking guard.** After each envelope, before applying rule 2,
   the executor checks that envelope's journal rows: if they name processes
   but mark none as observer, the marking has failed. The chain then refuses
   with reason `night_probe_error` and the text "recorder journal carries no
   observer-marked consumer; ancestry marking failed". Why: `powermetrics`
   alone runs at about 0.11 busy cores all night (0.112 mean on attempt 1,
   harvest record §6), about 67 core-seconds per 600 s envelope — over the
   bar — so without the guard a marking failure would abort after envelope 2
   under `non_observer_process_busy`, blaming a busy machine for a broken
   measurement. The realistic case is that the guard fires at envelope 01:
   the capture directory `envelope-01` stays on disk,
   `evidence_envelopes.jsonl` is not written, and `evidence_outcome.json`
   reports `envelopes_attempted` 0. If it fired at envelope n, rows 1 … n − 1
   exist and `envelopes_attempted` is n − 1 (seat
   report, fix round 2, R1 and deviation 2; record 08 §4, item D1).

**The observer floor: corrected, reported, and fed to an unchanged stop.**
(A **stop** — in full, a stop branch — is a registered condition under which
the pilot summary reports "no cutoff qualifies": the pilot then sets nothing
from its numbers. The full list is under "What happens with the result".)
The measurement's own processes use CPU and so draw power. For each envelope
the collector records `whole_envelope_observer_cpu_s`: its own CPU time plus
that of every child process it reaped once that child ended. That covers two
parts: the collector's own periodic sampling and census work, which it
records per round as `observer_cpu_s` (the **round block**), and the 100 ms
power sampler. The **observer floor** is the sum of that figure over the
night's readable envelopes (those whose session record could be read)
divided by the sum of their **envelope spans** (an envelope span is the
collector's own clock window for that envelope, end stamp minus start stamp),
in busy cores. v2 summed only the round block and
missed the power sampler: it reported 0.0531 cores on attempt 1 and 0.0528 on
attempt 2. v3's statistic gives 0.176 and 0.159 on the same bytes (v3
`observer_floor.supersedes`; ruling 31 §2; both harvest records' addenda).
Per envelope, the summary splits the floor into `round_block` (about 0.052
cores) and `power_recorder_residue` (whole minus round block: 0.123 on
attempt 1, 0.107 on attempt 2). The load recorder is started by the
executor, not by the collector, so its CPU is outside that total; the summary
reports it beside the floor (0.0073 and 0.0071 cores, `inside_whole: false`)
and adds a **companion floor** that includes it: 0.183 on attempt 1 and 0.166
on attempt 2 (`observer_floor_including_load_recorder_cores`; record 08 §2),
reported only, never a stop input. It also reports `observer_variation_cores`,
the standard deviation of the per-envelope share across envelopes (0.0021
and 0.0027), which is not a stop (v3 `observer_floor.variation`). What the
floor feeds is under "What happens with the result" below.

The **D-079 calibration acceptance** — the frozen artifact that pins the exact
bytes of the code deriving the energy numbers, so a later run can be shown to
have used the same estimator — is generation r7 (PR #380, merge
`7eb53effc78b8c90995ca8206df67c0e10ff18e5`), unchanged for this night: none
of the four estimator source files and the protocol file whose digests
`configs/calibration/calibration_acceptance_d079_v2_n17_r7.json` pins changed
between the attempt-2 arm head `dbd5cd59` and the v3 merge `3a411784`.

**Pre-arm precondition.** No ruling in the contamination gate (rulings 10,
21 and 31; syntheses 15, 25 and 35), brief 04 or record 08 sets a bench
check for this arm like the v2 arm's bench replay (a daytime run of the real
chain and collector fed the 02:17 night's recorded power files, with no
measurement, required by cold gate #3 ruling 10 §Q7 before attempt 2). The one ruled condition,
"a machine passing the t0 predicate" (ruling 10 §4), is enforced by the arm
`check` and the t0 gate themselves (rule 1). The v2 bench replay (artifact
`docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay-start-drift.md`,
chain-level start drift at most 0.352 s on twelve slots) stands for the
scheduling code: between its code (merge `4f8bc36d`, byte-identical over
`joulewise scripts configs` to `dbd5cd59`) and `3a411784`, the chain script,
the collector, the evidence-night generator and the night driver are
unchanged, and the executor's slot arithmetic (scheduled instant = first
start + (index − 1) × 620 s) is unchanged. The one new step inside the 20 s
gap is rule 2's in-chain reading of the journal, which the replay did not
exercise; the 2 s in-chain start-drift abort remains the backstop, and
attempt 2's live start drift of 0.150–0.191 s ran on the same scheduling
code.

Ed's written ruling (c), 10:57 PDT on 2026-09-19, still governs the
scientific order: it treats equivalence night two's **FAIL (m = 7)** as
the instrument's answer, so instrument characterisation precedes any
further derivation night. Authority:
`docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md`.
The three-night D-166 derivation is NOT continued from the two 25G83
equivalence nights. Their arm and harvest records remain in the Executed
blocks below. This is preparation, not a claim that anything is armed;
the published plan and arm record establish the night's exact bindings.

This `DIAGNOSTIC_NO_PACK` plan uses `joulewise.night_plan.v2` and the
plan's `window_max_s = 9000` (the value `joulewise/evidence_night.py` writes
into every plan it prepares). t0 is planned for 07:00 PDT on 2026-09-23
(epoch 1790172000); `prepare` names a plan `qpe01-pilot-n1-` plus t0's local
date and time as `%Y%m%d-%H%M`, which gives this plan id. **The exact t0 is
the one in the published plan.** Its acquisition end is t0 + 9000 s
(09:30 PDT), its completion / courier boundary is t0 + 9300 s (09:35 PDT),
and its daily dead-man is `ceil((t0 + 9300 + 3600) / 60) × 60` in epoch
seconds (1790184900, 10:35 PDT), until uninstalled. The programmed span is
600 + 11 × 620 + 600 = 8,020 s from chain start, which follows the t0
gate's 30 s observation, so it ends about 09:14:10 PDT, inside the
9,000 s window. No capture is run by the preparation scripts.

**What the night does.** The authority is cold gate packet 10 → 10a,
ruling 46b and record 85 in
`docs/process_traces/2026-09-19-activation-d0b83820/`, as amended by the
A269 cold-gate ruling 10 of 2026-09-22 that issued registration v2 and by
the QPE01-DAEMON-CONTAMINATION-01 rulings adopted into registration v3
(above). The plan-pinned wrapper `<custody_root>/chain.zsh`, emitted by
`scripts/gen_evidence_night.py`, executes
`scripts/night_chains/quiet_predicate_evidence.zsh`, which invokes
`joulewise.quiet_predicate_campaign run`. The frozen protocol is 600 s of
settling, then twelve 600 s idle envelopes started on the 620 s slot
pitch, each 480 s interior measured from the SCHEDULED envelope start
after a 60 s offset. `powermetrics` samples at the 100 ms setting. Census,
AC power, thermal state and the load recorder's 30 s journal are recorded
alongside; the machine-wide busy-cores total stays a covariate only
(`busy_cores_role: covariate_only`), while the per-process non-observer
totals drive rules 2–4 above. NO model, NO load generator, NO
calibration-ledger session and NO pack.

For the night the chain turns macOS network time synchronisation OFF, and
its final step turns it back ON; both are `systemsetup` commands that an
administrator rule lets this chain run without a password, and each is
recorded. In the 20 s gap after each envelope it then reads the `timed`
log for that envelope's window and writes the attestation described
above, and applies rules 4 and 2 to that envelope's journal rows. The
chain runs ONE read-only `git show` to verify the tracked chain bytes at
`measurement_head` (ruling 87a F2); it performs no commit, push, checkout
or fetch.

**What happens with the result, fixed before the night.** The pilot
summary (`night/evidence/summary.json`, written by `pilot_summary` in
`joulewise/quiet_predicate_campaign.py`) applies these rules:

- An envelope is **retained** only if none of v3's eleven exclusion reasons
  applies to it.
- **Disjoint adjacent pairs** are (e1, e2), (e3, e4), …, (e11, e12), each
  used only when both members are retained, never bridged across a gap;
  each pair gives one difference, even minus odd interior joules.
- The status is `SPREAD_RECORDED` when at least 8 envelopes are retained
  and at least 4 pairs formed (`minimum_retained`, `minimum_adjacent_pairs`);
  otherwise it is **INCONCLUSIVE**, with no top-up and no pooling with any
  other night.
- On `SPREAD_RECORDED`, the sample standard deviation of the n pair
  differences, `s_pair`, is raised to a one-sided 90 % upper bound (a value
  the true spread lies below with 90 % confidence), `s_upper = s_pair ×
  sqrt((n − 1) / χ²₀.₁₀(n − 1))`, where χ²₀.₁₀(k) is the value a chi-square
  variable with k degrees of freedom falls below 10 % of the time. Block
  two's pair count is `max(3, ceil(8 × s_upper² / δ²))`, where δ = 1 J
  (`sizing.delta_j`) is the smallest energy difference block two is sized to
  resolve, set at the instrument's ≈ 1 J attribution limit (ruling 46b;
  ruling 21 §2). Worked example (illustrative numbers): 6 pairs with
  `s_pair` 0.5 J give χ²₀.₁₀(5) = 1.6103, factor sqrt(5 / 1.6103) = 1.762
  (the registration's `reference_factors.n_6`), `s_upper` 0.881 J, and
  max(3, ceil(8 × 0.776)) = 7 pairs — the figures
  `joulewise/quiet_predicate_campaign.py` (`chi_square_lower_decile`,
  `size_block_two`) returns for these inputs.
- A **stop branch** is a registered condition under which the summary
  reports "no cutoff qualifies": this pilot then sets no busy-cores cutoff
  for a future quiet-machine admission rule and no block-two size. v3 has
  two that a pilot can reach: more than 24 pairs needed (`sized_pairs_above_24`), and an observer floor above
  `block_two.smallest_holdable_share`, 0.05 cores
  (`observer_floor_above_smallest_holdable_share`).

**A clean night is expected to report that second stop cause.** Block two is
the follow-on experiment, authored only after the pilot
(`authored_after_pilot: true`), that compares idle envelopes with envelopes
carrying a deliberate extra CPU load; its registered smallest load is 0.05
busy cores (`levels [0, 0.05]`). The apparatus measuring it already costs
0.159–0.176 busy cores per envelope on both archived nights — more than three
times that load. v3 keeps the comparison `observer floor > 0.05` exactly as
registered and feeds it the corrected floor (synthesis 35, adjudication 3;
brief 04 item 6(b); `stop_branch` in `joulewise/quiet_predicate_campaign.py`,
whose comment says "a clean pilot is EXPECTED to stop on it"); under it both
archived nights carry the cause (0.176 and 0.159 > 0.05; harvest-record
addenda). That outcome is pre-registered — the registered reading that
block two at a 0.05-core level "is not holdable above this apparatus"
(synthesis 35, adjudication 3): the extra load it would add is less than a
third of what the measuring processes already use — and it is not a failure
of the night and not a reason to re-run it. The observer-floor cause is
evaluated on every summary, SPREAD_RECORDED or INCONCLUSIVE, because the
floor is computed over all readable envelopes, retained or not. The night is
still for four things: (i) the first spread measurement (`s_pair`, `s_upper`)
on a machine v3's rules certify as clean, since attempt 1 retained 2
envelopes and attempt 2 is labelled non-idle; (ii) the busy-cores
distribution over envelopes passing census, AC and thermal probes (the
field `clean_machine_busy_cores`, which ruling 10 §2 says must be glossed
that way); (iii) the first live exercise of v3's arm check, t0 predicate,
per-envelope rule and marking guard; and (iv) input to block two's
redesign under option (c), which Ed chose at 01:06 PDT on 2026-09-23 (Gmail
`1a0cd4d699a90f29`, recorded in `RUN_STATE.md`'s activation 7a0f14bd block)
and released for work in directive issue #386 (his GitHub instruction "go on
block 2"): a load level of at least 0.18 cores, or
a lighter apparatus (synthesis 35, decision brief).

Results and busy-core covariates remain **PROVISIONAL** (the summary's
`evidence_status`: not usable as a claim until a ruling admits them). The
summary also re-derives rule 2 from disk and compares it with the executor's
in-chain list (`executor_non_observer_process_busy`); a difference is
reported as `non_observer_verdict_disagreement: true`, and nothing acts on
it (seat report §7). No quiet-admission threshold is activated by this
night. Only the lead, after a ruling on the pilot summary, may arm block
two; the courier has no scientific decision authority.

**Pins.** A **pin** is a recorded expected value that a later check must
match exactly. Here `repo_head = measurement_head = H`, where H is the main
head at which this handback rewrite lands: a docs-only commit on top of
`3d668e98`, which sits on the v3 merge
`3a411784` (PR #387). The code that runs is the code the independent v3
reviews covered — records 06 and 07 (reviews of the change against its
rulings) and 09 and 10 (re-reviews of each fix round) under
`docs/process_traces/2026-09-22-activation-a022aecc/` — exactly when
`git diff --stat 3a411784..H -- joulewise scripts configs` prints nothing.
The lead runs that check at the bench before arming; if it prints anything,
there is no arm on H. (At `3d668e98` it prints nothing.) The published plan
and the notice record H's full SHA as both `repo_head` and
`measurement_head`, and the courier reads this handback from the clone at
the plan's `measurement_head`. The custody root is
`/Users/edr/night-custody/qpe01-pilot-n1-20260923-0700-20260923-0700-1790172000-<H>`
and the measurement clone
`/Users/edr/JouleWise-measurement-20260923-0700-1790172000-<H>-qpe01-pilot-n1`
(the naming in `joulewise/evidence_night.py` `locations` as of 2026-09-23;
from 2026-09-25 new clones live under `/Users/edr/night-custody/measurement/`,
see `docs/contracts/evidence_night_entry.md`); the exact
directories are the ones named in the published plan. The plan's
repo-relative `registration_path` is
`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json`,
sha256
`69321c693b3370b949b0a4a1b8548e35dd081a36165ba8f6799a387c2d813616`, the
ruled registration bound to the tracked chain-source digest.
No calibration ledger is seeded, and no identity-epoch / t1-bindings desk
inputs or calibration-plan copy are required for this evidence payload
(record 85).

**Census.** This is a real night: no stub-only idle-interactive exemption.
The arm-time census classifies every `[c]odex|[c]laude|[t]3` match by ancestry
and aborts on any foreign process; every owned helper closes before
REQUEST (ruling 87a F6). Retained production roots remain discoverable;
the lead confirms the discovery set at the bench (87a F4).
Every census producer that can run while the chain runs must carry the
2026-09-20 self-match fix (`[c]odex|[c]laude|[t]3`): the driver and chain (from
the clone at the plan's `measurement_head`), the t0 author, and the WATCHDOG
PROCESS. `com.joulewise.magistrate` is a launchd job with `StartInterval`
300: each tick is a short-lived process that re-imports `night_gate` from
the canonical checkout, so an ordinary tick is never stale. Only a tick
that spawned or adopted a magistrate session and stayed alive as the
resident supervisor keeps the module it imported; its stale bare-word
pgrep is visible to the new driver census and reproduces the 09-20 abort
(the reverse is not true). Its census rows carry no argv, so check the
processes before arming: (a) `git -C /Users/edr/code/JouleWise merge-base
--is-ancestor <fix commit> HEAD` must exit 0 and `git -C …
--no-optional-locks status --porcelain -uno` must be empty (the watchdog
imports the working tree; untracked files cannot change it), else no arm;
(b) read
`resident_session.supervisor_pid` from
`/Users/edr/night-custody/magistrate/state.json` — `launchctl print` shows
the supervisor as "not running" once it is reparented, so it is not the
source — and `null`, or a pid that `ps -o pid=,lstart=,command= -p "$pid"`
cannot find or whose command line does not name `magistrate_watchdog.py`
(pid reuse), means no resident supervisor and nothing stale; a live pid
whose start is later than the moment the checkout came to contain the fix
imported the fixed module and is fine (it ends with its magistrate session
before REQUEST — the arming magistrate's own supervisor is always alive at
arm time); a live supervisor that started before that moment blocks the
arm (re-check after it has ended). That moment is the OLDEST reflog entry
from which HEAD has continuously contained the fix: walk
`git -C /Users/edr/code/JouleWise reflog --date=unix --format='%gd %H'`
newest to oldest while `merge-base --is-ancestor <fix commit> <sha>` holds,
and take the last stamp that held (not `reflog -1`: a later unrelated move
would refuse a fresh supervisor, and an older one would pass a stale one).
Per-night arm scripts re-authored from the trace templates must use the
bracketed pattern, single-quoted in zsh (unquoted brackets glob).
`scripts/prewindow_check.sh` is a bench tool run before an arm, never inside
acquisition: its `grep -E "codex|claude|t3|…"` child's argv would match the
new pattern. The next plan needs fresh artefacts (manifest/wrapper/digest/plan/
probe receipt) because `quiet_predicate_campaign.MANIFEST_PATHS` hashes
`night_gate.py`, and the registration it binds is now v3.

**Arm procedure via the tracked commands.** Use `python -m joulewise.evidence_night`
in this order: `prepare --kind quiet_predicate_evidence --t0 1790172000 --head <H>`
(`--t0 next` would instead pick the first whole minute at least 40 minutes
after the moment `prepare` runs, not 07:00) → `check` (it now also spends
rule 1's 30 s non-observer observation) →
`notice` (stdout's first two lines, `To: …` and `Subject: …`, are mail headers;
a blank line separates them from the body, also saved alone in
`lifecycle/notice.txt`; the magistrate sends that body via Gmail using those
header values, with no cc, and records the accepted message id) → `veto` →
`publish-install --notice-accepted <id>` → `verify` → exit before REQUEST →
after the night, `uninstall`. Pass `--candidate <staging>` to each command
after prepare; relay any mailbox NO into `<staging>/lifecycle/NO` before veto;
`publish-install` repeats the veto observation and the loaded-jobs probe at the publication boundary and requires a fresh `check` record; the lead re-runs `check` after any change.
The notice subject's "attempt" number counts only candidates prepared for the
same local date (`attempt = 1 + prior qpe01-pilot-n1-<date>` candidates), so
it reads 1 for this night's first candidate even though this is the third
attempt at pilot night one.
Record 17's script set remains the fallback until the first live use succeeds.

Pre-check step, ruled by the cold gate 2026-09-21 (packet 05 Q3, wording
corrected by the cold gate's packet 06 ruling): the census lists every process
whose full command line matches `codex`, `claude` or `t3` (the exact command is
`night_gate.AGENT_CENSUS_ARGV`, a `pgrep -lf` over those three words) and
classifies each listed process that is neither the checking process nor one of
its ancestors as foreign (`arm_census.classify_arm_census`); a process whose
command line matches none of the three words is never foreign, whatever its
ancestry. The tracked check refuses on any foreign PID, so the session's own
MCP helpers, which match `codex`, must be gone first. The ruled text, with its
commands corrected by the cold gate 2026-09-21 (activation ce7c57a9, round-3
packet, Q2; `pgrep -lP` prints process names only and `pkill -P` reaches
immediate children only, both verified against the installed manual and a live
process tree):

Before running `check` on a real plan, this session terminates its own idle MCP
helpers, and nothing else. Let `ROOT` be the PID of the session root: the
interactive `claude` process this session is running in, which the census
recognises by executable basename `claude` and an argv carrying no `-p` or
`--print` (`arm_census._interactive_root`). Find it with `pgrep -lf claude`,
take the PID whose command line carries no `-p`, and confirm it with `ps -o
pid=,command= -p $ROOT` before using it. List the session root's children with
their full command lines: `pgrep -flP $ROOT`. Every child whose command line
contains `codex mcp-server` is a helper. For each helper, enumerate all of its
descendants, at every depth, and send SIGTERM to the helper and every
descendant:

```zsh
descendants() { local pid; for pid in $(pgrep -P $1); do print -- $pid; descendants $pid; done }
for h in $(pgrep -flP $ROOT | grep -F 'codex mcp-server' | cut -d' ' -f1); do
  victims=($h $(descendants $h)); print -r -- "helper $h: TERM ${(j:,:)victims}"; kill -TERM $victims
done
```

Then wait until no descendant of the session root, at any depth, has `codex
mcp-server` in its command line: repeat `for d in $(descendants $ROOT); do ps
-o pid=,command= -p $d; done | grep -F 'codex mcp-server'` until it prints
nothing. Record every PID terminated, with its command line, in the check
record. Terminate nothing that is not a descendant of `ROOT`. Then run `check`.
If the census still reports any descendant of the session root as foreign,
stop; never relabel it "diagnostic" (a diagnostic is the census's own report
that it could not observe something: a discovery command that failed or printed
an unparsable row, or a listed PID with no readable process record; the check
refuses on diagnostics exactly as on foreign PIDs, so the relabel would not
clear it).

**Timeline.** The plan's relative boundaries are: install strictly before
t0 − 600 s (06:50 PDT for this t0; the close is excluded); REQUEST and
magistrate exit at t0 − 480 s (06:52); TERM at t0 − 360 s (06:54); KILL at
t0 − 300 s (06:55). Acquisition, completion / courier and daily dead-man use
the plan values above. The notice is generated from staged bytes and sent
after H is pinned, before publication and installation. Power, powermode,
census, load and probe evidence are recorded at the bench. Ed's NO on the
notice thread stands the night down.

## Executed — rehearsal-20260909 (history)

Reconciliation recorded 2026-09-09 by activation 628c2eed (harvest record 21i).
The following is the dated record as written then; its pending-cure and
section references describe that earlier handback. The cure has since
merged at `a52810c9`, as recorded in the synthesis for the new night.

The night described above was armed by headless activation `784a764e` (not `1ef89702`, which prepared it) with the frozen triple
(`rehearsal-20260909`, `/private/tmp/joulewise-rehearsal-20260909-checkout`, `ae8f074f`) — the checkout name differs from the
`JouleWise-rehearsal-20260909-<sha>` example above; the arm record is
`docs/process_traces/2026-09-02-hands-free-week/21h-rehearsal-20260909-arm-record.md`. It fired at 02:56 PDT on 2026-09-09:
result `REHEARSAL_ONLY`, chain exit 0, results branch `night-results/20260909` at `a84e0f7f`, courier email `1a08599a4ff4d005`.
The receipt refused `night_probe_error` (the gate read `chain.zsh`, which the stub arm never writes) — a finding; the cure is committed on branch `fix/2026-09-09-night-gate-stub-chain` at `5db38b58` (PR #309) under review, not yet merged, as lane
NIGHT-GATE-STUB-CHAIN-01; the plan is not re-armed on that signature. The §Next lane harvest, `--uninstall` from the stub checkout,
and removal of the stub checkout and plan root are DONE (record 21i); nothing is armed and the frozen-checkout list is empty apart
from the canonical repo. The standing rules below are unchanged. RECORD: harvest, uninstall and removal for this night are complete; no next plan is
armed; §Purpose, §Where the results are and §Next lane describe the completed night (this file's history holds no separate
between-nights template text; whether one should exist is referred to the cold gate, not decided here).

## Executed — rehearsal-20260911 (2026-09-11)

The night did not run. At 02:56 PDT, Python 3.9.6 crashed on the
`datetime.UTC` import before any census, gate or stub. At 07:00 PDT, the
dead-man refused `night_refused_agent_present` on an orphaned Claude daemon;
that refusal is not a night-gate verdict. No `result.json` or `receipt.json`
was produced. Courier email `1a090c8424231111` reported the failures.

Harvest is complete in
[record 01](../process_traces/2026-09-11-activation-58a3bcfc/01-rehearsal-20260911-harvest-record.md):
item 5 MET, item 6 NOT MET. Item 5 rests on the pre-night 2026-09-10 07:00
dead-man stand-down, not the 09-11 refusal. Both agents were uninstalled FROM
the stub checkout, and the checkout and plan root were retired in
[record 02](../process_traces/2026-09-11-activation-58a3bcfc/02-rehearsal-20260911-uninstall-and-retirement.md).
RECORD: harvest, uninstall and removal for this night are complete; nothing
is armed. The next plan is authored under record 13 of the same directory;
this entry assigns it no pins.

## Executed — rehearsal-20260912 (2026-09-12)

The night ran. Launchd started the driver at 00:30:04 PDT under the pinned
Python 3.13 (H′ `a7d1eb88`); gate verdict `REHEARSAL_ONLY`; the built-in stub
exited 0; `result.json` `REHEARSAL_ONLY` with `chain_exit_code` 0; receipt
C1/C3/C4/C5 PASS with measured keys, C2 `NOT_APPLICABLE`
(`no_pack_by_design`), refusal null; `launchd.night.err` EMPTY; results
branch `night-results/20260912` at `e657f30f`; courier email
`1a09487237fa6be2`. Ruling 06 C-7 is MET clause by clause and acceptance
item 6 is MET in
[record 01](../process_traces/2026-09-12-courier-rehearsal-20260912/01-rehearsal-20260912-harvest-record.md).
Both agents were uninstalled FROM the stub checkout, the checkout was
removed, and the plan root was moved out of discovery (delete refused by the
harness; bytes archived) in
[record 02](../process_traces/2026-09-12-courier-rehearsal-20260912/02-rehearsal-20260912-uninstall-and-retirement.md).
RECORD: harvest, uninstall and retirement for this night are complete; nothing
is armed; this file's §Purpose / §Where the results are / §Next lane still
describe this completed night until the magistrate rewrites them for the
next plan.

## Executed — d079-epoch-25g83-derivation-n1-20260913 (2026-09-13)

The night fired and was REFUSED at the gate. Launchd started the driver at
02:56:02 PDT from the clone at H `f90cb8c0`; gate verdict `REFUSED`, reason
`night_refused_agent_present` (census `pgrep -lf codex|claude|t3` exit 0:
Ed's interactive `claude` session pid 24974 with its two Codex MCP servers,
and the ChatGPT desktop app's Codex helper); no chain started
(`chain_exit_code` null), no ledger session opened, nothing captured;
`launchd.night.err` EMPTY; results branch `night-results/20260913` at
`e2dd56d5`; courier email `1a09a3319d602a37`. Per §Next lane this refusal
kind is correct behaviour and the night is re-planned, never re-armed.
Harvest per runbook §2.0–§2.2, byte-exact preservation with an `lstat`
inventory, and the §2.5 tool's refusal (`session … is not in the ledger`,
rc 3) are in
[record 01](../process_traces/2026-09-13-activation-c5048879/01-equivalence-night-20260913-harvest-record.md).
Both agents were uninstalled FROM the clone at 05:39:52 PDT (rc 0); the
clone and the night root are RETAINED. RECORD: harvest and uninstall for this
night are complete; nothing is armed; the successor plan is
`d079-epoch-25g83-derivation-n1-20260915` once this file's §Purpose /
§Where the results are / §Next lane are rewritten for it.

## Executed — d079-epoch-25g83-derivation-n1-20260915 (2026-09-14, NOT ARMED)

The plan was never published. Activation `24b9d3dd` was the activation alive
for the 2026-09-14 03:00–06:30 PDT install span: it retired the refused
20260913 root out of the watchdog's discovery glob (bytes archived, 20/20
checksums), ran runbook §0.3–§1.1b at 00:03 (desk inputs, staged plan,
wrapper `356a0810…` VERIFIED, preflight ok; record 48), and then held with a
census poll every 20 s. From 00:02 through the 06:05 cutoff the census never
cleared — Ed's interactive `claude` pid 24974 with its Codex MCP servers, the
ChatGPT desktop app's Codex helpers, the Claude desktop app's helpers and a
`Codex Computer Use` service — and no reply, NO or directive arrived. §1.4 was
therefore not executed: no notice, no publication, no install (`launchctl
list` showed only the magistrate throughout). At 06:06 the session removed its
own staged plan and night root after copying the wrapper, sidecars, desk
inputs and staged plan into
[record 49](../process_traces/2026-09-13-activation-24b9d3dd/49-no-arm-record-n1-20260915.md)'s
evidence; the clone at H `27957b60` is retained. RECORD: nothing was armed;
the plan id carries its date and is not reused; the successor is
`d079-epoch-25g83-derivation-n1-20260916` (this file's §Purpose / §Where the
results are / §Next lane, rewritten by the commit that is its H).

**Dated addendum 2026-09-14 16:50 PDT (activation `24b9d3dd`) — ARMED THE SAME EVENING UNDER DIRECTIVE ISSUE #336.** Ed's directive issue #336 (owner, at the machine) ordered this very plan id armed tonight from the retained clone at H `27957b60`, with a one-night owner authorization for an evening install span (from the notice send until 23:30 PDT 09-14; every other gate unchanged), and kept the census clean himself. The session first retired its own never-published `n1-20260916` staging and night root (clone at `3c8bd220` retained), re-ran the desk block (staged plan authored 16:26:43, wrapper `356a0810…` VERIFIED — same digest as the morning), sent the notice at 16:30:20 (`1a0a241a8415794f`), and at 16:45:46 — census clean by ancestry, no NO — published the plan and installed both agents from the 20260915 clone (record 52). **`d079-epoch-25g83-derivation-n1-20260915` IS ARMED: t0 2026-09-15 02:56:00 PDT (1789466160), `window_max_s` 9000, courier deadline 05:31:00, dead-man 07:00; published plan sha256 `207245e1…`.** The §Purpose / §Where / §Next-lane text of THIS file on main describes the 20260916 successor written by `3c8bd220`; the clone at H `27957b60` carries the 20260915 text, which is the text in force for the armed night. The 20260916 plan id was never published; nothing else is armed.

## Executed — rehearsal-20260916c (2026-09-16)

Armed 02:50:45 PDT by activation `83d93f5a` (notice by email
`1a0a99fa2717d749`; H `be221f6a`; both agents installed rc 0 from the clone).
Fired 03:25:00.82 PDT. The t0 gate recorded `night_refused_agent_present`
(Ed's interactive Claude session 7066, its codex MCP pair 7086/7094 and its
zsh wait loop 9850, the outcome §Purpose named as expected while that session
is open); the stub still ran: `chain.started` 03:25:00.85, `chain.exited`
exit 0 at 03:25:03.12, stdout `REHEARSAL`, stderr empty; `result.json`
verdict `REHEARSAL_ONLY`, `chain_exit_code` 0; `launchd.night.err` EMPTY;
courier email `1a0a9c0fd1fc101e` 03:26:37, `courier.sent` written; results
branch `night-results/rehearsal-20260916c` at `558d7b83`. Acceptance MET on
all three clauses. Harvested 03:53 by activation `0bd12d79` (byte-exact copy
with `SHA256SUMS`, 15/15 OK), both agents uninstalled from the clone 03:53:50
rc 0, plan root retired to `~/night-archive` 03:54 (record-48 procedure,
15/15 checksums re-verified), lapsed `rehearsal-20260916` staging archived,
stub clones retained (delete refused by the harness):
[record 01](../process_traces/2026-09-16-activation-0bd12d79/01-rehearsal-20260916c-harvest-record.md).
This was the first night under the 2026-09-16 machinery (transactional
installer, 8/8/6/5-minute leads, `t0 − 10 min` install close): the install
transaction, the resident ladder (the watchdog's HOLD_CENSUS through the plan
span, sequence 161) and the courier all behaved as specified.

## Executed — d079-epoch-25g83-derivation-n1-20260916 (05:40 candidate, 2026-09-16, NOT ARMED)

The first candidate for this plan id (H `82ea3eef`, t0 09:45:00 PDT) was
staged, desk-checked and preflighted by activation `0bd12d79` at 04:15 but
never noticed, published or installed: Ed's interactive Claude session (pid
7066, with its codex MCP pair) stayed alive past its own 04:14 exit
announcement because its terminal was never closed, the real-class census
refuses on it, Ed did not answer the 04:21 email asking him to close it, and
the candidate lapsed at its 05:30 install close. Staged plan and night root
preserved unpublished under
[record 02](../process_traces/2026-09-16-activation-0bd12d79/02-n1-20260916-arm-record.md)'s
evidence. RECORD: nothing was armed; the same plan id is re-planned to a new
t0 by the next handback commit once the census clears.

**Dated addendum 2026-09-16 09:27 PDT (activation `0bd12d79`) — ARMED on H `32243adc` for t0 09:45:00 PDT.** Ed ran `/exit` (pid 7066 left the census 09:24:07; his reply `1a0ab095f3673122` 09:25); re-planned by `replan.py` to t0 1789577100, notice by email `1a0ab0a61def58d3` 09:26:18, published 1789576035.63, both agents installed rc 0 from the clone at H, final census `foreign_pids []`; frozen triple (`d079-epoch-25g83-derivation-n1-20260916`, `/Users/edr/JouleWise-measurement-20260916-derivation`, `32243adca1bfc8822e8001e4bac58000d591aa4f`); [record 02](../process_traces/2026-09-16-activation-0bd12d79/02-n1-20260916-arm-record.md). The activation exits before REQUEST 09:37.

## Executed — d079-epoch-25g83-derivation-n1-20260917 (2026-09-17, REFUSED at t0 on load, harvested)

The frozen triple was (`d079-epoch-25g83-derivation-n1-20260917`,
`/Users/edr/JouleWise-measurement-20260917-derivation`,
`92c178f863ccc9a9742f080108433a5afd148b2e`). The arm is
[record 77](../process_traces/2026-09-16-activation-9853dd2b/77-arm-record-n1-20260917.md);
the completed harvest is
[record 01](../process_traces/2026-09-17-activation-8789ee70/01-n1-20260917-harvest-record.md).
At 15:30:01 PDT the gate returned `REFUSED`, `night_refused_not_quiet`:
load 3.66 exceeded 2.0. The production agent census was empty. No chain
started, no reservation or ledger session opened, and `runs/` was never
created. The result's chain exit code and chain hash are null; no
scientific equivalence verdict was available (REFUSED-NO-DATA).

Courier message `1a0b17fdd4f8043a` is recorded by `night/courier.sent` at
15:32:27 PDT. The harvest preserved the root byte-exact in
`~/night-archive/d079-epoch-25g83-derivation-n1-20260917-harvest-20260917`
with 22-file SHA256SUMS and a separate lstat inventory. Both agents were
uninstalled FROM its clone at 18:16:24 PDT, rc 0; no night label remained.
The root and clone were retained at harvest. The upcoming step 0 moves the
root only after re-verification; that move is not recorded as executed here.
The courier also found the handback still described 09-16 at H; this
rewrite supplies the new 09-19 plan's own Purpose / Where / Next lane.

RECORD: harvest and uninstall complete; no measurement or successor arm
is established by this historical block. D-182's separate positive evidence
and ordinary fresh-plan gates apply to the proposed successor.

## Executed — d079-epoch-25g83-derivation-n1-20260919 (2026-09-18, ARMED)

Armed 2026-09-18 19:38:28 PDT by headless activation d8ca3a36 as the D-182 successor of the 09-17 refusal: triple `(d079-epoch-25g83-derivation-n1-20260919, /Users/edr/JouleWise-measurement-20260919-derivation, d595aa9f42cdc3d49d0ecae5f2ef33321fd6f90f)`, plan sha256 `78edf5667807432912eec9ce381be8baed563cf7b4cf0efe217b8840d3ddda66`, t0 2026-09-19 00:00:00 PDT, notice `1a0b78109400cce8` accepted 19:33:32 before publication at 19:37:23, probe ok, both agents installed from the clone. Record: `docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-record-n1-20260919.md`. Outcome: see the harvest record of the next activation.

**Dated addendum 2026-09-19 03:20 PDT (harvested by activation b165c535; recorded by activation 4ca26e9c) — GO, HARVESTED, EPOCH_EQUIVALENCE INCONCLUSIVE (m = 4 < 6).** Fired at 00:00:00 PDT on 2026-09-19: gate GO on every row (census EMPTY, load
0.32, AC, chain digest `a830b521…`); the chain opened the derivation session,
settled 600 s, ran all twelve slots on the 600 s cadence and exited 0 at
02:03:35; 247 censuses, all empty; results branch
`night-results/d079-epoch-25g83-derivation-n1-20260919` (`7f13bfa6`); courier
delivered at 02:05 (`1a0b8e9d530d5e5c`). Harvested 02:38–03:0x by activation
b165c535 (byte-exact copy to
`~/night-archive/d079-epoch-25g83-derivation-n1-20260919-harvest-20260919`,
86/86 checksums OK against the live root); the completed harvest is
[record 01](../process_traces/2026-09-19-activation-b165c535/01-n1-20260919-harvest-record.md).

Slot outcomes: d01, d03, d05, d12 `valid`; d02, d04, d06, d08, d09, d11
`ordinary-invalid` (`not_all_pulses_detected`); d07, d10 `ordinary-invalid`
(`clock_anchor_unresolved`, 0 pulses). The terminal pin candidate (126 /
`ffd12051…`) was committed at the desk before the §2.5 check (runbook §3
item 4). `scripts/epoch_equivalence_check.py` from two checkouts at H:
**EPOCH_EQUIVALENCE INCONCLUSIVE (m = 4 < 6)**, records byte-identical. Under
directive issue 316 the ONE next action is one more equivalence night under a
fresh plan id; nothing else. Both night agents were uninstalled from the clone
(rc 0). The clone and the night root are RETAINED (a session opened).
RECORD: harvest and uninstall for this night are complete; the successor
equivalence night is prepared under this handback's §Next lane.

## Executed — d079-epoch-25g83-derivation-n2-20260919 (2026-09-19, ARMED)

Armed 2026-09-19 03:15:29 PDT by headless activation 4ca26e9c as the runbook §2.5 INCONCLUSIVE successor of night one: triple `(d079-epoch-25g83-derivation-n2-20260919, /Users/edr/JouleWise-measurement-20260919-derivation-n2, 22b92ec764f445b01c6e1cc110ca93c6679a27d5)`, plan sha256 `d76776571029fc73df8599d2bc28973cf3d224af75dfcfdc96ed0c7c7e17557c`, t0 05:00:00 PDT (1789819200), notice Gmail `1a0b9295e7b733be` accepted 03:15:21 before publication (03:15:25) and install (03:15:28); ledger restored byte-exact from the night-one clone (126 rows, `c004eee5…`) and authenticated head-equals-pin 126 / `ffd12051…`; probe admitted (`custody_elapsed_s` 1.82); both agents loaded and verified against the plan schedule. Arm record `../process_traces/2026-09-19-activation-4ca26e9c/01-arm-record-n2-20260919.md`. RECORD: this block establishes installation only; the result, harvest and §2.5 outcome are the successor's to append.

**Dated addendum 2026-09-19 07:41 PDT (harvested by activation d0b83820) — GO, HARVESTED, EPOCH_EQUIVALENCE FAIL (m = 7).** Both night agents were uninstalled from the clone at 07:41:02 PDT (rc 0); the clone and night root are RETAINED. Record: `docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md`.

## Executed — qpe01-pilot-n1-20260922-0217 (2026-09-22, ARMED, GO, HARVESTED, INCONCLUSIVE)

Armed 2026-09-22 02:03 PDT by headless activation dc2237d5 through the tracked entry point (check → notice Gmail `1a0c85878b76e926` → veto → publish-install → verify, all rc 0): triple `(qpe01-pilot-n1-20260922-0217, /Users/edr/JouleWise-measurement-20260922-0217-1790068620-d45378c6010b538ca1bb74ae0f2222dceb4df1e4-qpe01-pilot-n1, d45378c6010b538ca1bb74ae0f2222dceb4df1e4)`, custody root `/Users/edr/night-custody/qpe01-pilot-n1-20260922-0217-20260922-0217-1790068620-d45378c6010b538ca1bb74ae0f2222dceb4df1e4`, t0 02:17:00 PDT (1790068620), `window_max_s` 9000. Arm record: `docs/process_traces/2026-09-22-activation-dc2237d5/01-first-live-arm.md`. This block, not the plan-`qpe01-pilot-n1-20260920` text above, names the night that ran; the result record is authoritative where they differ.

**Dated addendum 2026-09-22 05:20 PDT (harvested by activation 22666c9f) — GO, chain exit 0, twelve envelopes captured with cleanup proven, pilot summary INCONCLUSIVE (retained 2 of 12, zero disjoint pairs, "no cutoff qualifies").** Courier Gmail `1a0c8e258b89b05f` sent 04:31. Both night agents were uninstalled from the clone at 04:59:32 PDT (`python -m joulewise.evidence_night uninstall --candidate <staging>`, rc 0); the clone and night root are RETAINED; the harvest archive with checksums is `/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922`. The results branch `night-results/qpe01-pilot-n1-20260922-0217` is NOT on origin: the driver's push failed on twelve raw `powermetrics` plists above GitHub's 100 MB limit (lane NIGHT-RESULTS-LARGE-FILES-01, Ed's choice of destination). Seven envelopes lost their clock anchor to macOS `timed` clock slews against the anchor's 5 ms absolute caps (lane QPE01-CLOCK-DISCIPLINE-ANCHOR-01, cold gate before the pilot is repeated). Record: `docs/process_traces/2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md`. RECORD: harvest and uninstall for this night are complete; nothing is armed; the next pilot night waits for the anchor ruling.

## Executed — qpe01-pilot-n1-20260922-2100 (2026-09-22, ARMED)

Armed 2026-09-22 20:12:28 PDT by headless activation ca45291d through the tracked entry point (check `3f8ccb3136fd` → notice Gmail `1a0cc3fa26b13a44` → veto → publish-install → verify, all rc 0): triple `(qpe01-pilot-n1-20260922-2100, /Users/edr/JouleWise-measurement-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432-qpe01-pilot-n1, dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432)`, custody root `/Users/edr/night-custody/qpe01-pilot-n1-20260922-2100-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432`, t0 21:00:00 PDT (1790136000), `window_max_s` 9000, registration `pilot_protocol_v2.json` (`2c539240…`). Pre-arm bench replay per cold ruling 21: artifact 24 + `24-bench-replay.json` + addendum 24b at H, chain-level start drift max 0.352 s on twelve slots, replay merge `4f8bc36d` (code at H byte-identical over `joulewise scripts configs`). Arm record: `docs/process_traces/2026-09-22-activation-ca45291d/01-arm-record-qpe01-pilot-n1-20260922-2100.md`. The §"Where the results are" / §"Next lane" text below still names the runbook's planned suffix `…-2030`; this block, not that text, names the night that ran, and the custody root above is the one to read. Owed after the night: harvest, uninstall, then the driver-amendment PR (ruling 21 C3).

**Addendum 2026-09-22 23:40–23:55 PDT (activation a022aecc, harvest).** The night ran to completion: chain 21:00:01 → 23:13:51 PDT exit 0, verdict GO, twelve envelopes each rc 0 with cleanup proven, clock attestation `authenticated` on all twelve, every anchor bounded and every interior complete; chain-level start drift 0.191 s on envelope 1 and 0.150 s on envelopes 2–12 (the A269 cure held). Courier Gmail `1a0cceaea8afe162` at 23:19; 268 censuses, zero hits. Harvest: byte-exact copy to `/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-20260922` (15,958 files verified OK against the live root; the one non-OK line is the temporary sums file that existed only in the copy); custody root and clone RETAINED. Uninstall: `python -m joulewise.evidence_night uninstall --candidate <staging>` from the clone at 23:42:02 rc 0 (`lifecycle/uninstall.json`); `launchctl list` shows no `joulewise.night` label and no night plist remains. Canonical fast-forwarded by hand `48842569` → `91f80870` afterwards (nothing loaded, D-183). Results branch NOT on origin (twelve raw plists over 100 MB again; A268). **The machine was not idle:** the load journal shows `fseventsd` at 1.00 busy cores in every sample (a `scan_old` loop in the unified log since 04:49:03 PDT that day) and `mediaanalysisd` at 1.4–1.8 cores for about five minutes inside envelope 1; interior joules ≈ 305 J (649.7 on envelope 1) against ≈ 152 J the night before. The census cannot see either and busy cores are covariate-only by registration v2, so the summary as registered reads SPREAD_RECORDED / PROVISIONAL, twelve retained, six pairs, "no cutoff qualifies" — on the wrong machine. Referred to the cold gate (packet `docs/process_traces/2026-09-22-activation-a022aecc/03-coldgate-packet-daemon-contamination/00-PACKET.md`): the standing of that outcome and a machine-state predicate for registration v3 and the arm check. Harvest record: `docs/process_traces/2026-09-22-activation-a022aecc/01-qpe01-pilot-n1-20260922-2100-harvest-record.md`. Owner action emailed (Gmail `1a0cd027cacb7206`): restart `fseventsd` (sudo). No next night is prepared while that daemon is pegged. The driver-amendment PR (ruling 21 C3) is in flight on `feat/2026-09-22-replay-driver-fidelity-rule`.

## Executed — qpe01-pilot-n1-20260923-0700 (2026-09-23, ARMED)

Armed 2026-09-23 at 05:37:32 PDT by headless activation 4e8918fa (Opus 5.5), through the tracked entry point: check `70c510f35ef9`, then notice (Gmail `1a0ce4522dbdbf03`, `notice.txt` verbatim plus the one correction line of 4158e658 record 01 §3), then veto, publish-install and verify, all rc 0. Triple `(qpe01-pilot-n1-20260923-0700, /Users/edr/JouleWise-measurement-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15-qpe01-pilot-n1, 26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15)`. Custody root `/Users/edr/night-custody/qpe01-pilot-n1-20260923-0700-20260923-0700-1790172000-26fb4280b1e2b3ab5b239884a2c1abbd5f9e1f15`. t0 07:00:00 PDT (1790172000), `window_max_s` 9000, registration `pilot_protocol_v3.json` (`69321c69…3616`), plan sha256 `6193c6b6…b566`. Arm gate on the staged bytes (activation 4158e658, records 05–08): cold Fable 5.1 ARM, Opus 5.5 ARM, Sol 6.0 ARM AFTER CURES (dissent recorded; lane A276). Arm record: `docs/process_traces/2026-09-23-activation-4e8918fa/01-arm-record-qpe01-pilot-n1-20260923-0700.md`. Its divergence 1 records that the helper-termination recipe above misses the `npm exec @openai/codex@<version> mcp-server` wrapper. Owed after the night: harvest, uninstall, and a harvest record that names the F2 `summary.md` sentence.

## Where the results are

- Custody root: `/Users/edr/night-custody/qpe01-pilot-n1-20260923-0700-…`,
  the exact directory named in the published plan (its suffix carries t0
  and the pinned head H).
  Driver records in `night/`: `result.json`, `receipt.json` or
  `refusal.json` as the result directs, `chain.started`, `chain.exited`,
  `censuses.jsonl`, `chain.stdout.log` and `chain.stderr.log`. The result
  record owns the verdict and chain exit code; report them as recorded.
  On a t0 refusal under rule 1, the receipt's C3 row carries
  `top_consumers_at_decision`; report the named process, pid and share.
- Evidence records under `<custody_root>/night/`:
  `evidence_outcome.json`, `evidence_envelopes.jsonl`,
  `evidence_cleanup.json`, `evidence_busy_cores.jsonl` (the load
  recorder's journal, now with `observer` marks),
  `evidence/summary.json` and `evidence/summary.md`. Envelope directories
  under `night/evidence/` retain `rounds.jsonl`, `session.json` and native
  power files. `evidence_envelopes.jsonl` carries each envelope's
  `start_drift_s` against the frozen schedule, its clock-discipline
  attestation state (`authenticated`, `slew_attested` or `asserted`) and its
  in-chain `non_observer_process_busy` list (empty when no non-observer
  reached 30 core-seconds); report all three, and report a
  `start_drift_abort` row as the pre-registered night-ending refusal it is,
  not as a data outcome. A `refusal.json` with reason
  `non_observer_process_busy` is rule 3's abort (report the process, pid and
  core-seconds it names, and that no successor is installed); one with
  reason `night_probe_error` and the text "ancestry marking failed" is rule
  4's guard, and then `evidence_envelopes.jsonl` is absent by design if it
  fired at envelope 1 (if at envelope n, it holds rows 1 … n − 1).
- The pilot summary reports retained and excluded envelopes with their
  reasons, disjoint-pair spread, `s_upper` and δ = 1 J sizing for block two
  or "no cutoff qualifies" with its causes; `observer_floor_cores`,
  `observer_floor_including_load_recorder_cores`,
  `observer_variation_cores` and each envelope's `observer_floor_components`;
  `non_observer_process_busy` per envelope beside the executor's
  `executor_non_observer_process_busy`, and
  `non_observer_verdict_disagreement`. The cause
  `observer_floor_above_smallest_holdable_share` is the expected,
  pre-registered outcome of a clean night (§"Purpose of this night"); report
  it as that, with the floor's value. Missing files or an unset bound are
  limitations to report, and all results remain PROVISIONAL.
- Refusal documents: every path in `result.json.refusal_documents` and
  any later refusal document, following `NIGHT_COURIER_PROMPT.md`.
  Read `evidence_cleanup.json` for proof of collector, recorder and sampler
  cleanup; a successful probe is not evidence of capture or cleanup.
- Driver log: `<custody_root>/night.log`, including the evidence
  boundary's diagnostics. Launchd streams: `night/launchd.night.out` and
  `night/launchd.night.err`.
- Courier records under `<custody_root>/night/`: `courier.sent`,
  `courier.json` and `courier.heartbeat`. `courier.sent` records the
  Gmail message id of the result email actually delivered; that id, not
  an expectation, is what the report names. Results branch:
  `night-results/qpe01-pilot-n1-20260923-0700` on `origin`, if the
  driver's push succeeded — verify, do not presume. On both earlier pilot
  nights the push failed because twelve raw `powermetrics` files each
  exceeded GitHub's 100 MB per-file limit; the same failure here is a
  reporting matter, never a reason to treat the custody root as incomplete.
- After the night, harvest is a byte-exact copy of the whole custody
  root to `/Users/edr/night-archive/<plan-id>-harvest-<date>`, checked by
  re-verifying the copy's `SHA256SUMS` against the live root before
  anything is removed, and then the two scheduled jobs are removed with
  `python -m joulewise.evidence_night uninstall --candidate <staging>`
  run from the measurement clone. Record its exit code.

## Next lane

The successor magistrate rebuilds the coordinates from the frozen triple
`qpe01-pilot-n1-20260923-0700` / the measurement clone named by the
plan's `measurement_root` / H (the SHA in the published plan), resolved
in the published plan and arm record. Harvest after `night/courier.sent`,
per record 85 step 5 in
`docs/process_traces/2026-09-19-activation-d0b83820/85-pilot-night-one-arm-recipe.md`,
respecting the standing process-liveness checks above. Read the result,
receipt or refusal, evidence outcome, envelope and cleanup records,
busy-cores journal, pilot summary, `night.log`, launchd streams and
courier record. Preserve the evidence byte-exact; report attempted and
retained envelopes, exclusions (with every `non_observer_process_busy`
process, pid and core-seconds), incomplete support, spread, covariates,
per-envelope start drift and attestation state, the observer floor and
companion floor, missing evidence and whether cleanup was proven.

After harvest, uninstall both scheduled jobs FROM the measurement clone
with the tracked entry point and record the exit code:
`python -m joulewise.evidence_night uninstall --candidate <staging>`.
Retain the clone and custody root if any envelope was captured. Cleanup
that depends on uninstall waits for exit 0; an uncertain cleanup is
reported for the lead to resolve.

Then the magistrate rules on the pilot summary, and the ruling turns on
two numbers it reports: how many of the twelve envelopes were retained,
and how many disjoint adjacent pairs those form. `SPREAD_RECORDED` (at
least 8 retained and 4 pairs) gives the spread and `s_upper` that block
two's redesign consumes; the expected stop cause
`observer_floor_above_smallest_holdable_share` is recorded as the
pre-registered finding about block two's 0.05-core level, not as a defect of
the night. An INCONCLUSIVE summary names the cause (which exclusion reasons
removed which envelopes — in particular whether rule 2 excluded envelopes and
which processes it named) and returns the work to the diagnosis loop. A
rule-3 abort ends the span with no successor until the successor-installing
change (lane A270) lands. There is
no top-up and no pooling of an aborted night's envelopes with a later one.
No courier or successor may turn sizing into an arm without that ruling;
only the lead may arm block two. No quiet-admission threshold is activated,
and the results remain PROVISIONAL.

Two standing items for Ed, carried over in substance from the
previous handback text (written by activation 59857fe5 on 2026-09-22), are
not decided here: a proposed standing rule that a sealed cold-gate
ruling governs over a later brief that contradicts it, and a proposed
lane for a live pre-arm check of the `timed` log header, so that an
attestation query that cannot be read is found at the bench rather than
at t0.

The pilot's result feeds the block-two design work under option (c)
(Purpose section, item (iv)). The next instrument lane after the pilot is
`INSTRUMENT-CADENCE-25G83-01` (`TASK_QUEUE.md` row A257, blocked until a
pilot night is harvested), on the doubled `powermetrics` cadence
(consult 06 in `docs/process_traces/2026-09-19-activation-a743be05/`),
followed by restore-or-re-characterise, and only then derivation nights.
Ed's ruling (c) at
`docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md`
governs that order: the two 25G83 equivalence nights do not continue the
three-night D-166 derivation. Every later night requires its own plan and
the ordinary arm gates.

For every v2 plan, run `scripts/install_night_agent.sh` FROM the checkout
named by the plan's `measurement_root`, with that checkout at the plan's
`measurement_head`; never install the two night agents from the development
checkout. Once authored, every armed plan's canonical
`(plan_id, measurement_root, measurement_head)` is included in the magistrate
relaunch prompt's frozen-checkout list until completion.

Before installing a new calibration night, run the launchd access probe from
that same pinned checkout, with the owner present. A **LaunchAgent** is a macOS
launchd job file. A terminal inherits the owner's file-access consent; a
launchd job does not inherit the terminal's consent, so a terminal preflight
cannot establish unattended access. The temporary job uses the same driver
and chain interpreters and the real reservation arguments, with **verify-only**
meaning enforcing custody checks without appending a session, settling, or
capturing data.

After the published plan and wrapper have passed the earlier arm checks:

```zsh
# PLAN is the published <custody_root>/night_plan.json; PY is the pinned
# absolute driver interpreter in the measurement checkout.
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --launchd-probe
# Continue only after exit 0: the job was booted out (unloaded), and its
# process census (a check for surviving processes) proved it gone.
scripts/install_night_agent.sh --plan "$PLAN" --python "$PY"
```

The non-authorizing **receipt**, `<plan_dir>/night_probe_receipt.json`, is a
record of successful access, never permission to capture. It binds the plan,
measurement checkout commit, code fingerprints, wrapper, and both interpreters' paths,
versions and binary SHA-256 fingerprints. A calibration payload also binds the
ledger head (the latest ledger record's digest) and ledger bytes. An evidence
payload instead binds the sealed manifest, harness and registration digests,
and the tracked chain-source digest at the measurement commit. Its distinct
receipt, `joulewise.night_evidence_probe_receipt.v1`, verifies files and imports
only: it never starts `collect`, `load` or power sampling and carries no ledger
custody fields. The single literal `NIGHT_PAYLOAD_KIND=quiet_predicate_evidence`
in the pinned wrapper selects that receipt; absence retains the calibration
probe. Install recomputes those bindings
and requires success less than six hours old. A missing, stale, failed, or
mismatched receipt refuses installation with exit 2 and the field name.
`--probe-timeout-s 600` bounds the temporary job; `--probe-max-age-s 21600`
sets the receipt age limit. The installer always unloads the temporary label
`com.joulewise.night-probe.<plan_id>` and checks for surviving processes.
`--render-only DIR` also renders its job file into `DIR`, without launchctl.
The driver first writes `night_probe_receipt.pending.json`; the installer
publishes `night_probe_receipt.json` only after unloading and process cleanup
are proven. An interrupted or failed cleanup leaves no installable receipt.
Treat every Homebrew Python replacement as invalidating the successful launchd access probe; verify again.
An interpreter replacement changes the executable fingerprint the receipt
binds. After a consent dialog, repeat the probe successfully without further
interaction before installing.

For the 2026-09-16 example, 190 governed files (3.33 GB) at 38 iCloud custody
locators held the 09:45 reservation for 11 h 07 m, until 20:52; there were no
captures or verdict. Consent is the leading explanation; materialization
(a cloud file becoming locally available) remains an alternative in the
root-cause record. The whole custody pass now has a 120 s budget, clipped ten
seconds before the window ends. One **custody pass** is one sweep over every
governed file the ledger names that actually opens and hashes those files;
the arm-time probe times exactly one, and the capture writer makes
at most `WRITER_CUSTODY_PASSES` of them (3 today, in
`joulewise/night_agent_install.py`) inside that one budget, so installation
refuses unless `custody_elapsed_s × WRITER_CUSTODY_PASSES × 1.5 ≤
custody_budget_s` — T ≤ 26.67 s at 3 passes and a 120 s budget — and unless the
probe verified at least one observation while the ledger holds finalized ones.
The writer sweeps the corpus four times per slot but on a healthy slot reads it
twice: lane CUSTODY-PASS-MEMO-01 keeps the verified set on the shared allowance
while the writer lease is held and the ledger's head digest is unchanged, so the
two sweeps after the under-lease one read nothing. Three is the worst case, and
it is counted rather than absorbed by the 1.5 margin: a recovery step that
appends moves the head digest and costs one more read, and a corrupt corpus
costs three reads on its own, because a sweep that refuses is never memoized —
and that slot has to reach its typed `calibration_ledger_custody_invalid`
instead of timing out first.
Each capture writer's success receipt reports its own `custody_passes`. The chain
also exports `JOULEWISE_NIGHT_CUSTODY_BUDGET_S`, a per-operation allowance in
seconds that every process it starts inherits — reservation, capture writer
and the end-of-window session abort alike — so a governed read that was handed
no budget of its own is still bounded, and one that cannot be bounded refuses
`calibration_ledger_custody_invalid` instead of blocking. The abort is also
passed that allowance as a flag, and it reads ONE slot's custody state (the
next slot, the only such value it consumes), so its whole bill is one 120 s
allowance rather than one per declared slot.

**What happens after the window ends** (NIGHT-STALL-WALLCLOCK-ABORT-01). Every
instant below is measured from the exclusive window end, `t0 + window_max_s`;
the constants are in `scripts/run_night.py`.

| From the window end | What happens |
|---|---|
| acquisition already fenced | The chain refuses to START a slot whose capture budget would cross the end, and its reservation and every writer carry a custody deadline of `window end − 10 s`. Nothing new is acquired after this point. |
| the closing abort | The chain's end-of-window `abort-session` runs with the window already spent: one 120 s custody allowance plus seconds of lease and repair work. It acquires nothing. |
| `+ 300 s` (`WINDOW_SHUTDOWN_GRACE_S`) | The driver's wall-clock deadline. The instant is computed once from the driver's clock when the chain starts and then tracked on a monotonic clock, so a clock change cannot move it. A census-loop check and an independent watchdog thread both enforce it, because the loop itself can block on a census probe or on a write to the custody volume. |
| `≤ 70 s` more (`TERMINATION_BOUND_S`) | Terminating the chain's whole process group and PROVING it gone: SIGTERM, up to 30 s to reap the chain, up to 5 s of re-signalled `pgrep -g` census, then the SIGKILL escalation with the same two bounds. The census re-sends the phase's signal before each look because a member forked by a survivor after the first signal inherits the group unsignalled. Proven means reaped AND the census came back empty. |
| `≤ 300 s` more (`COURIER_DEADLINE_S`) | The courier delivers the result, verdict `ABORTED`, reason `night_window_exceeded`. If termination was NOT proven the night reports `night_chain_alive` instead and the courier is suppressed. |
| `+ 3900 s` | The dead-man (`COURIER_DEADLINE_S + DEADMAN_GRACE_S`). The 670 s above leave it at least 3230 s of margin, so it fires only when the driver itself is gone. |

A typed refusal means a machine-readable
cause: `calibration_ledger_custody_timeout` stops and preserves the night.
Read `calibration-refusal.json`, its `<pid>.json` siblings, and every path in
`result.json.refusal_documents`; also discover later `refusal-NN.json` files.
Report the exact code, budget, elapsed seconds, and `existing_session` so the
owner knows whether an existing ledger session needs desk recovery.

**Standing rules** <!-- F11 -->

Author every new v2 plan with
`joulewise.night_plan_writer.write_night_plan`; invalid-plan tests begin with
that writer's bytes and apply a named mutation. The writer emits both
`schema: joulewise.night_plan.v2` and integer `schema_version: 2`; either field
missing or inconsistent makes the plan malformed.
The installer records the first SIGINT/SIGTERM/SIGHUP and polls before mutations
and at the final commit latch after the clock check; rollback never polls, and
signals after the latch or completion cannot replace the completed exit code
(post-commit Ctrl-C keeps exit 0 and the pins).

Installer note: on install the installer checks `repo_head` against the
driver checkout HEAD and `measurement_head` against the HEAD of the plan's
`measurement_root`, while `--uninstall` checks neither pin and no longer
needs `claude` on PATH or a Python virtual environment (a project-specific
Python installation).
Install and `--render-only DIR` (render the two night job files and the access-probe file to a directory
without installing anything) default to `<measurement_root>/.venv/bin/python`;
pass `--python /absolute/path/to/python` to select the interpreter (the
executable running the driver). A stub checkout needs that venv or an absolute
path to a Python whose version is at least `MIN_PYTHON` in `scripts/run_night.py`
(currently 3.11) and for which `run_night.py preflight --plan PLAN.json` exits 0
from the stub checkout under the job's PATH.

At 02:56 PDT on 2026-09-11, the night driver crashed before any gate because
`python3` found through PATH selected macOS Python 3.9.6, which cannot import
`datetime.UTC`. A **LaunchAgent** is a macOS launchd job file; each job now names
an absolute interpreter path. A **driver preflight** loads the driver module
and every project module it imports at module scope, under the job's
interpreter and PATH, and parses the plan before installation. Its JSON
`modules` list names the driver and those direct module-scope project imports.
It does not exercise functions' lazy imports inside `joulewise` or run the
night's gates or measurements. The installer prints the JSON success record
for the arm record and refuses installation if preflight fails.

Ordinary daytime work in the dev checkout no longer invalidates an armed night; only
moving the pinned measurement checkout does. Once authored, every armed
plan's canonical `(plan_id, measurement_root, measurement_head)` is included
in the magistrate relaunch prompt's frozen-checkout list until completion.

G2-a routing handoff (2026-09-08; installed):
`scripts/run_night.py::_run_chain_once` derives `MEASUREMENT_ROOT`,
`MEASUREMENT_HEAD`, and `PY` from the parsed v2 plan and overwrites inherited
values in the child environment alongside `NIGHT_PLAN_ID`. There is no v2
interpreter field: the driver always gives the chain
`<measurement_root>/.venv/bin/python`, independently of the driver interpreter
selected at install time. (Since PR #321 the installer also pins the driver's
own interpreter by absolute path; before it, the driver ran under whatever
`python3` the LaunchAgent's PATH resolved to, which is the 2026-09-11 defect.)
The chain and its input preflight (checks before measurements start) verify checkout HEAD against `measurement_head`; that
input preflight's sole argument is the absolute v2 plan filename. The separate
driver import check is `run_night.py preflight --plan PLAN.json`. Future clone
naming and the exact locked venv creation commands live in [the runsheet's plan-derived block](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md#plan-derived-measurement-variables).

D-176 pack-bound T0_REHEARSAL post-night handback (separate from the stub above):

1. Harvest and preserve the completed rehearsal's GO, consumption, capture and
   bundle evidence. The completed bundle loads and evaluates G1–G6 + G8–G10
   before control production; an absent `g7_control` locator yields G7 FAIL,
   detail `g7_control_pending`, rather than a bundle load error.
2. Prepare the fresh sibling control with the production TRANSACTION_PACK plan
   specified in [the GO contract §10.5](../contracts/pack_night_go_receipt.md#105-g7-control-2026-09-08).
   Run `scripts/run_night.py g7-control --plan CONTROL_PLAN --rehearsal-receipt
   REHEARSAL_RECEIPT --rehearsal-go REHEARSAL_GO` after the night. The two source
   receipts come from the completed rehearsal; the destination is its separate
   `-g7-control` sibling. Neither the control nor its `night` directory may be a
   symlink. Retain the returned `{path, sha256}` locator as `records.g7_control`
   in the bundle manifest, preserving the completed consumption/capture bytes.
3. Re-evaluate with `scripts/rehearse_t0_unattended.py --custody-root REHEARSAL_ROOT`.
   G7 PASS requires this post-night control and acceptance from its authenticated
   bytes; closure requires all ten gates PASS. The sequence is harvest →
   g7-control → re-evaluate bundle.
