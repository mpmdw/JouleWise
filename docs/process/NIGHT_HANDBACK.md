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
| `night_refused_not_quiet` | One-shot load refusal for v2, or a terminal power/thermal predicate failure. For v4, load is diagnostic and the CPU cutoff is a sealed plan parameter with a named ruling. Zero-capture successor route per D-182. |
| `night_refused_bind_expired` | Bind window expired with every sample recorded. Load is diagnostic; the CPU cutoff is a sealed plan parameter. Zero-capture successor route per D-182. |
| `night_refused_hid_idle` | Screensaver-configuration guard failed; this is not a live inactivity measurement. Zero-capture successor route per D-182. |
| `night_refused_boot_clock` | Measurement boot/clock guard failed; not a watchdog uncertainty tick. Zero-capture successor route per D-182. |
| `night_refused_registration` | The registration digest is not in the ruled table, or its bound chain-source digest differs from the measured source. |
| `night_window_expired` | Measurement window expired. |
| `night_plan_stale` | Plan age or pinned head failed; not a stale notice. |
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

**Other explicit refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `HOLD_CENSUS` | A supervisor census hold alone does not establish the narrowly evidenced idle arm cause. |
| `slot_refused` | A measurement slot refused; cure the finding before any further night. |

Unknown or mixed causes and every capture, clock, custody, ledger or pre-registration guard stay on the cold-gate path; receipt refusals remain ineligible for same-plan retries. Known concurrent refusal evidence overrides an eligible arm cause. These dispositions preserve existing harvest, delivery and human-resolution remedies; they do not call a review into a live chain.

R1's operative time bounds are `now < install_close_epoch(plan)` and plan age within `PLAN_MAX_AGE_S` (including the existing authored-to-t0 check), with at least 60 seconds between arm attempts. D-180's same-or-next-listed-span ceiling is subsumed by `install_close_epoch(plan)` and `PLAN_MAX_AGE_S`, because with whole-day install spans it could otherwise bind 15 minutes before install close. There is no attempt-count cap, separate notice-age limit, new window cadence or delay after a successful harvest.

D-182: binding observations inside the window are not retries; a terminal zero-capture machine-state refusal permits ONE new-plan successor only after positive evidence of no chain.started claim, no reservation or ledger session, no capture writer run and an empty runs/instrument_validation inventory, plus completed courier.sent delivery. zero_capture_successor_allowed checks that evidence separately. successor_arm_allowed requires a new id and digest, fresh notice, at least 60 s after the predecessor's terminal write, and now before the successor's own install_close_epoch. Every observed NO on any notice thread still stops. Never re-arm the predecessor or put a new plan in same-candidate retry history.

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

Plan `qpe01-pilot-n1-20260920` is QPE-01 idle-variance PILOT NIGHT ONE,
using the evidence executor. Ed's written ruling (c), 10:57 PDT on
2026-09-19, treats equivalence night two's **FAIL (m = 7)** as the
instrument's answer: instrument characterisation precedes any further
derivation night. Authority:
`docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md`.
The three-night D-166 derivation is NOT continued from the two 25G83
equivalence nights. Their arm and harvest records remain in the Executed
blocks below. This is preparation, not a claim that anything is armed;
the published plan and arm record establish the night's exact bindings.

This `DIAGNOSTIC_NO_PACK` plan uses `joulewise.night_plan.v2` and the
plan's `window_max_s = 9000`. t0 is expected shortly after midnight PDT
on 2026-09-20; the lead selects the next quiet slot at least 40 minutes
after arm. **The exact t0 is the one in the published plan.** Its
acquisition end is t0 + 9000 s, its completion / courier boundary is
t0 + 9300 s, and its daily dead-man is
`ceil((t0 + 9300 + 3600) / 60) × 60` in epoch seconds, until uninstalled.
No capture is run by the preparation scripts.

**What the night does.** The authority is cold gate packet 10 → 10a,
ruling 46b and record 85 in
`docs/process_traces/2026-09-19-activation-d0b83820/`. The plan-pinned
wrapper `<custody_root>/chain.zsh`, emitted by
`scripts/gen_evidence_night.py`, executes
`scripts/night_chains/quiet_predicate_evidence.zsh`, which invokes
`joulewise.quiet_predicate_campaign run`. The plan's frozen protocol
specifies 600 s settle, then twelve 600 s idle envelopes. Each 480 s
interior is measured from its SCHEDULED envelope start after a 60 s
offset. `powermetrics` samples at the 100 ms setting; census, AC, thermal
and the 30 s busy-cores journal record covariates. The programmed span
is 7,800 s inside the 9,000 s window. NO model, NO load generator,
NO calibration-ledger session and NO pack. The chain runs ONE read-only
`git show` to verify the tracked chain bytes at `measurement_head`
(ruling 87a F2); it performs no commit, push, checkout or fetch.

**What happens with the result, fixed before the night.** The pilot
summary uses disjoint adjacent pairs and the chi-square upper confidence
bound ruled in 46b, with δ = 1 J, to size block two or report "no cutoff
qualifies". Insufficient retained evidence is INCONCLUSIVE, with no
top-up. Results and busy-core covariates remain **PROVISIONAL**. No
quiet-admission threshold is activated by this night. Only the lead,
after a ruling on the pilot summary, may arm block two; the courier has
no scientific decision authority.

**Pins.** `repo_head = measurement_head = H`, where H is the main head the
fresh measurement clone is detached at (PR #369, the render-only fix, merged
and this handback landed); the published plan and the notice record its full
SHA as both `repo_head` and `measurement_head`. The frozen triple is
`(qpe01-pilot-n1-20260920, /Users/edr/JouleWise-measurement-20260920-qpe01-pilot-n1, H)`.
The fresh measurement clone is detached at the merge of the render-only
fix; the lead pins H at the bench before arm, and the plan and notice carry
its full SHA. The courier reads this handback from
the clone at the plan's `measurement_head`. The custody root is
`/Users/edr/night-custody/qpe01-pilot-n1-20260920`. The plan's repo-relative
`registration_path` is
`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json`,
the ruled registration bound to the tracked chain-source digest.
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
`night_gate.py`; no ruled registration hash changes.

**Arm procedure via the tracked commands.** Use `python -m joulewise.evidence_night`
in this order: `prepare --kind quiet_predicate_evidence --t0 next` → `check` →
`notice` (stdout's first two lines, `To: …` and `Subject: …`, are mail headers;
a blank line separates them from the body, also saved alone in
`lifecycle/notice.txt`; the magistrate sends that body via Gmail using those
header values, with no cc, and records the accepted message id) → `veto` →
`publish-install --notice-accepted <id>` → `verify` → exit before REQUEST →
after the night, `uninstall`. Pass `--candidate <staging>` to each command
after prepare; relay any mailbox NO into `<staging>/lifecycle/NO` before veto;
`publish-install` repeats the veto observation and the loaded-jobs probe at the publication boundary and requires a fresh `check` record; the lead re-runs `check` after any change.
Record 17's script set remains the fallback until the first live use succeeds.

Pre-check step, ruled by the cold gate 2026-09-21 (packet 05 Q3): the census
classifies every process outside the caller's ancestor chain as foreign, and
the tracked check refuses on any foreign PID, so the session's own MCP helpers
must be gone first. The ruled text:

Before running `check` on a real plan, this session terminates its own idle
MCP helpers. List the children of the session root: `pgrep -lP
<session-root-pid>`. For every child whose command line contains `codex
mcp-server`, send SIGTERM to that child and its descendants (`pkill -TERM -P
<child-pid>`; `kill -TERM <child-pid>`), wait until `pgrep -f 'codex
mcp-server'` lists no descendant of the session root, and record the PIDs
terminated in the check record. Terminate nothing outside the session root's
descendants. Then run `check`. If the census still reports any descendant of
the own session root as foreign, stop; never relabel it "diagnostic".

**Timeline.** The plan's relative boundaries are: install strictly before
t0 − 600 s (the close is excluded); REQUEST and magistrate exit at
t0 − 480 s; TERM at t0 − 360 s; KILL at t0 − 300 s. Acquisition,
completion / courier and daily dead-man use the plan values above.
The notice is generated from staged bytes and sent after H is pinned,
before publication and installation. Power, powermode, census, load and
probe evidence are recorded at the bench. Ed's NO on the notice thread
stands the night down.

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

## Where the results are

- Custody root: `/Users/edr/night-custody/qpe01-pilot-n1-20260920`.
  Driver records in `night/`: `result.json`, `receipt.json` or
  `refusal.json` as the result directs, `chain.started`, `chain.exited`,
  `censuses.jsonl`, `chain.stdout.log` and `chain.stderr.log`. The result
  record owns the verdict and chain exit code; report them as recorded.
- Evidence records under `<custody_root>/night/`:
  `evidence_outcome.json`, `evidence_envelopes.jsonl`,
  `evidence_cleanup.json`, `evidence_busy_cores.jsonl`,
  `evidence/summary.json` and `evidence/summary.md`. Envelope directories
  under `night/evidence/` retain `rounds.jsonl`, `session.json` and native
  power files. The pilot summary reports retained and excluded envelopes,
  disjoint-pair spread, the chi-square upper bound and δ = 1 J sizing
  for block two or "no cutoff qualifies"; missing files or an unset bound
  are limitations to report, and all results remain PROVISIONAL.
- Refusal documents: every path in `result.json.refusal_documents` and
  any later refusal document, following `NIGHT_COURIER_PROMPT.md`.
  Read `evidence_cleanup.json` for proof of collector, recorder and sampler
  cleanup; a successful probe is not evidence of capture or cleanup.
- Driver log: `<custody_root>/night.log`, including the evidence
  boundary's diagnostics. Launchd streams: `night/launchd.night.out` and
  `night/launchd.night.err`.
- Courier records under `<custody_root>/night/`: `courier.sent`,
  `courier.json` and `courier.heartbeat`. Results branch:
  `night-results/qpe01-pilot-n1-20260920` on `origin`, if the driver's
  push succeeded — verify, do not presume.

## Next lane

The successor magistrate rebuilds the coordinates from the frozen triple
`qpe01-pilot-n1-20260920` /
`/Users/edr/JouleWise-measurement-20260920-qpe01-pilot-n1` / H (the SHA in the published plan),
resolved in the published plan and arm record. Harvest after
`night/courier.sent`, per record 85 step 5 in
`docs/process_traces/2026-09-19-activation-d0b83820/85-pilot-night-one-arm-recipe.md`,
respecting the standing process-liveness checks above. Read the result,
receipt or refusal, evidence outcome, envelope and cleanup records,
busy-cores journal, pilot summary, `night.log`, launchd streams and
courier record. Preserve the evidence byte-exact; report attempted and
retained envelopes, exclusions, incomplete support, spread, covariates,
missing evidence and whether cleanup was proven.

After harvest, uninstall both agents FROM the clone and record the exit
code:
`scripts/install_night_agent.sh --plan /Users/edr/night-custody/qpe01-pilot-n1-20260920/night_plan.json --uninstall`.
Retain the clone and custody root if any envelope was captured. Cleanup
that depends on uninstall waits for exit 0; an uncertain cleanup is
reported for the lead to resolve.

The pilot summary goes to the lead for a ruling on block two. No courier
or successor may turn sizing into an arm without that ruling; only the
lead may arm block two. No quiet-admission threshold is activated, and
the results remain PROVISIONAL. The next scientific lane is then
`INSTRUMENT-CADENCE-25G83-01`, on the doubled `powermetrics` cadence
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
