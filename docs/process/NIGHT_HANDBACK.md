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
| `night_refused_registration` | Required registration did not validate. |
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

A retry-class abort recorded by a prior activation authorises a successor's ordinary fresh-plan arm of the same class without a new cold gate; the predecessor's published plan directory, if any, stays untouched under the existing human-resolution path.

Follow runbook §1.4a for classification, refreshed notice evidence, byte checks
and cleanup. This applies to every plan class; pack authorization stays hard.

## Arm-time census for rehearsal plans

Follow [runbook §0.6 step 3b and §1.4](../phase_2/derivation_night_runbook.md#06-census-clean-and-the-night-is-agent-free): only a parsed `REHEARSAL_STUB` plan may treat an idle interactive Claude or Node/T3 session as not foreign, unknown observations count as idle, the caller's own PPID chain is exempt, the own interactive or headless root receives the same stub-only idle-tree exemption (workload descendants still block; sibling seats outside its subtree remain foreign), and the new census blocks publication only for that stub class while other classes retain the existing all-agents-closed rule with diagnostic output.
All agents must still close before the plan span: the unchanged night gate records `night_refused_agent_present` for an agent hit, real chains do not start on that refusal, and rehearsals retain their harmless-stub continuation and census-hit recording; the runbook's §8 owns the term definitions.

## Purpose of this night

Plan `d079-epoch-25g83-derivation-n1-20260919` is the proposed D-182
new-plan successor of the 09-17 zero-capture load refusal, recorded in the
Executed block below. This is preparation, not a claim that anything is
armed. Its own plan id, session id, roots, desk inputs, wrapper and notice
are bound at the bench. The predecessor's positive no-capture evidence,
completed courier delivery and zero-successor count remain arm preconditions.

This `DIAGNOSTIC_NO_PACK` v2/2 plan is scheduled for **2026-09-19 00:00:00
PDT / 07:00:00 UTC**, `t0_epoch_s = 1789801200`. Its 9000-second acquisition
window ends at 02:30:00 PDT / 09:30:00 UTC (1789810200). The completion /
courier boundary is 02:35:00 PDT / 09:35:00 UTC (1789810500). The daily
dead-man is 03:35 PDT / 10:35 UTC (1789814100), until uninstalled. The arm
record will establish whether installation happened; no capture is run by
the preparation scripts.

**What the night does.** It is the epoch-equivalence check that Ed's
directive issue 316 ruled on 2026-09-10, transcribed as revision 3 of
`configs/calibration/preregistration_d079_epoch_25g83_rev1.md` and as the
dated addendum under D-102. The 2026-09-02 macOS update moved `os_build`
from 25F84 to 25G83 and replaced the `/usr/bin/powermetrics` binary, so the
issued D-079 calibration acceptance (`d079_calibration_acceptance_v2_n17_r6`)
no longer matches this machine and ordinary capture refuses. Night one asks
one instrument question: did the update move the clock-anchor bound outside
the envelope the instrument was already characterised against? The night
opens one agent-free `derivation`-kind ledger session of 12 declared slots
at head-equals-pin (ledger head sequence 76), settles once for 600 s, then
takes twelve derivation-only `powermetrics` fiducial captures at a 600 s
start-to-start cadence (programmed span 7680 s). No model runs, no
measurement pack, no Git, no claim output. The plan's `chain_path` is the
plan-pinned wrapper `<night root>/chain.zsh`, emitted by
`scripts/gen_derivation_night.py`, which carries the night's environment as
literals, verifies the tracked chain's bytes and `exec`s
`scripts/night_chains/calibration_derivation_only.zsh` (SHA-256
`b5beea464d392621631d9e5060e2c63c804676b28a5b2aea58b714c5cbead6fb` at this
head). The pre-registration keeps its `rev1.md` filename and now contains
revision 3 (PR #355), including the operational chain digest above. Its
scientific equivalence rule and timing constants remain the sealed ones.

The following existing instruction is retained verbatim for authority review;
PR #355 already supplied the revision-3 re-pin described above:
The pre-registration's chain-digest field must be
re-pinned by a dated addendum before the next arm (lane
PREREG-CHAIN-DIGEST-ADDENDUM-01); an arm against the sealed digest refuses
`night_chain_digest_mismatch`.

**What happens with the result, fixed before the night** (runbook
`docs/phase_2/derivation_night_runbook.md` §2.5). Let m be the number of
retained captures: ledger disposition `valid` and a stored anchor record
that resolves. m < 6 is INCONCLUSIVE: one more equivalence night, nothing
else. PASS is every retained `b_fiducial_s` at or below 0.032898493715362 s
AND the retained range (largest minus smallest) at or below 0.009724 s; on
PASS the dated D-102 continuation addendum is written and real G2-a windows
follow under the ordinary window path. FAIL is anything else; on FAIL
revision 1's three-night derivation proceeds with this night as night one.
No member value is read by anyone before the session is terminal; the desk
tool `scripts/epoch_equivalence_check.py` applies the rule at harvest.

**Pins.** `repo_head = measurement_head = H`. The new triple is
`(d079-epoch-25g83-derivation-n1-20260919, /Users/edr/JouleWise-measurement-20260919-derivation, __H__)`.
H is the reviewed, merged and pushed main commit containing this handback
rewrite and the pending-arm inventory entry. The magistrate fills H in
`arm-env.zsh` after that commit lands, before cutting the clone; the plan
and notice record its full SHA as both `repo_head` and `measurement_head`.
The pre-registration revision-3 file SHA-256 at preparation is
`06ac72ba5542cf176732a4360568abe0da49f50a697fe3f7725b395a334dafac`. Its ledger pin remains sequence 76 /
`08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`.

The fresh GitHub clone is
`/Users/edr/JouleWise-measurement-20260919-derivation`, detached at H, with
Python 3.13 from `env/mac-measurement-lock.txt`. Its ledger is copied
byte-exact from the canonical ledger and authenticated head-equals-pin with
custody verification. The custody root is
`/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919`;
`SESSION_ID` equals the plan id and `EVIDENCE_ROOT_ID` is
`evidence-d079-epoch-25g83-derivation-n1-20260919`. The calibration plan is
the committed `configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json`
copied byte-exact into that root. The desk-input writer supplies
`identity-epoch.json` and `t1-bindings.json`; the generator pins their bytes
in `chain.zsh`. The plan's `registration_path` remains the D-166 registration,
separate from the scientific pre-registration. No v4 flags are used.
The ledger session records the frozen calibration plan by
`plan_id` and SHA-256 as an identity binding, and a derivation-only capture
reads nothing else from it.

**Census.** This is a real night: the t0 census has no idle-interactive
exemption (that exemption is stub-only, ARM-CENSUS-IDLE-INTERACTIVE-01), and
the arm-time census classifies every `codex|claude|t3` match by ancestry and
aborts on any foreign process. The first candidate for this plan id (t0
05:40:00 PDT, H `82ea3eef`) was never published: Ed's interactive session
(pid 7066) stayed alive past its own 04:14 exit announcement because its
terminal was never closed, and the candidate lapsed at its 05:30 install
close (its staged plan and night root preserved unpublished under record 02's
evidence). This commit re-plans the same id to the t0 above, chosen at the
moment the census cleared plus the arm-to-t0 floor and a margin; nothing is
published while any foreign agent process lives.

**Timeline.** Install on 2026-09-18 inside the whole-day span
[00:00, 24:00) PDT (1789714800 → 1789801200), after the accepted notice and
strictly before **23:50:00 PDT** / 06:50:00 UTC (1789800600). REQUEST and
the magistrate's exit boundary are **23:52:00 PDT** / 06:52:00 UTC
(1789800720); TERM is 23:54:00 / 06:54:00 UTC (1789800840), and KILL is
23:55:00 / 06:55:00 UTC (1789800900). The notice is generated from staged
bytes. Power, powermode, census, load and probe evidence are recorded at
the bench. The step-0 script prepares byte-preserving retirement of both
09-16 and 09-17 roots out of discovery, leaving both clones untouched;
retirement is not claimed complete here. A230's standing-text conflict
remains for the owning authority; this preparation changes no rule.
The consolidated notice with these pins is sent after commit H
and before the plan is moved into its discoverable place; Ed's NO on the
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

<<<<<<< Updated upstream
## Executed — d079-epoch-25g83-derivation-n1-20260919 (2026-09-18, ARMED)

Armed 2026-09-18 19:38:28 PDT by headless activation d8ca3a36 as the D-182 successor of the 09-17 refusal: triple `(d079-epoch-25g83-derivation-n1-20260919, /Users/edr/JouleWise-measurement-20260919-derivation, d595aa9f42cdc3d49d0ecae5f2ef33321fd6f90f)`, plan sha256 `78edf5667807432912eec9ce381be8baed563cf7b4cf0efe217b8840d3ddda66`, t0 2026-09-19 00:00:00 PDT, notice `1a0b78109400cce8` accepted 19:33:32 before publication at 19:37:23, probe ok, both agents installed from the clone. Record: `docs/process_traces/2026-09-18-activation-d8ca3a36/21-arm-record-n1-20260919.md`. Outcome: see the harvest record of the next activation.
=======
## Executed — d079-epoch-25g83-derivation-n1-20260919 (2026-09-19, GO, harvested, INCONCLUSIVE)

Armed 2026-09-18 19:38:28 PDT by activation d8ca3a36 (arm record
`../process_traces/2026-09-18-activation-d8ca3a36/21-arm-record-n1-20260919.md`, H `d595aa9f`).
Fired at 00:00:00 PDT on 2026-09-19: gate GO on every row (census EMPTY, load
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
>>>>>>> Stashed changes

## Where the results are

- Custody root: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919`;
  driver records in `night/` — `result.json` (expected verdict `GO` for
  this class when every gate row passes, `chain_exit_code` 0),
  `receipt.json` or `refusal.json` as `result.json` directs (C1 PASS with the
  D-166 registration hash, C2 `NOT_APPLICABLE` / `no_pack_by_design`, C3, C4
  and C5 PASS with C5's `chain_sha256` equal to the wrapper's digest),
  `chain.started`, `chain.exited`, `censuses.jsonl`, `chain.stdout.log`,
  `chain.stderr.log` (the wrapper's `FAIL <reason>` lines, if any),
  `courier.sent`, `courier.json`, `courier.heartbeat`.
- Driver log: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night.log`
  — `night driver started` and a `night gate verdict=` line for 00:00 PDT on 2026-09-19;
  no dead-man line is expected before completion (03:35 is after it).
- Chain log: `<custody root>/operator_logs/derivation-chain.log` —
  `session_open kind=derivation slots=12`, `chain_start` (its timestamp
  minus `t0` is the realized Δ), `settle_complete`, twelve `slot_start`
  lines each answered by `slot_end … disposition=valid`,
  `slot_end … disposition=non-valid` or `slot_refused`, then
  `derivation_night_complete slots=12` or `slot_unused … reason=window_exhausted`
  followed by `session_abort`.
- Captures: `<custody root>/runs/instrument_validation/<session id>-dNN/`
  (`manifest.json`, `instrument_evidence.json`, raw trace); ledger rows in
  the clone's `runs/calibration_observation_ledger.jsonl`. The clone and the
  night root are production custody after this night and are RETAINED, not
  removed.
- Launchd streams: `night/launchd.night.out` and `night/launchd.night.err`;
  `launchd.night.err` must be EMPTY.
- Results branch: `night-results/d079-epoch-25g83-derivation-n1-20260919` on
  `origin`, if the driver's push succeeded — verify, do not presume.

## Next lane

The relaunched magistrate (its prompt carries the frozen triple
`d079-epoch-25g83-derivation-n1-20260919` /
`/Users/edr/JouleWise-measurement-20260919-derivation` / `__H__`, resolved in the arm record)
harvests only after the completion boundary (02:35:00 PDT on 2026-09-19) has passed and
`courier.sent` exists, per runbook §2: §2.0 rebuild the night's coordinates
from the frozen triple; §2.1 read `result.json`, the receipt or refusal,
`night.log`, the chain log and both launchd streams; preserve the custody
root byte-exact outside watchdog discovery with an `lstat` inventory before
anything is moved; §2.2 the ledger dry run (`check --session-ids` from the
clone, counts and states only); §2.5 `scripts/epoch_equivalence_check.py`
with `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json`, and
the ONE action its outcome names (PASS → the dated D-102 continuation
addendum through the normal gate, then real G2-a windows; FAIL → revision 1's
three-night derivation with this night as night one; INCONCLUSIVE → one more
equivalence night). A receipt refusing `night_refused_agent_present`,
`night_refused_not_quiet` or `night_refused_hid_idle` is a correct refusal —
the rows ran and refused — and the night is re-planned as a new plan, never
re-armed on the same plan (REFUSAL-FAST-RETRY-01 is queued, not landed).
Physics, evidence and pre-registration refusals stay on the cold-gate path;
email Ed for those only.

After the harvest, run `scripts/install_night_agent.sh --plan
/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/night_plan.json --uninstall`
FROM the clone and record its exit code. The clone and the night root are
production custody after a night that opened a session and are RETAINED;
only a refused night's plan root is retired (byte-exact archive to
`~/night-archive/<plan id>-plan-root-retired-<epoch>` with `SHA256SUMS`,
record-48 procedure).

Then loop under D-181 (windows whenever the machine is quiet): the next plan
is authored as its own plan under runbook §1.1–§1.5 on the merged main, with
a clean all-agents-closed census, and armed under this same handback
procedure.

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
measurement checkout commit, ledger head (the latest ledger record's digest),
code fingerprints, wrapper and ledger bytes, and both interpreters' paths,
versions and binary SHA-256 fingerprints. Install recomputes those bindings
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
