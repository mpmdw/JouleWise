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

The **arm-time census** is the process inventory before publication. The **plan span** is the agent-free interval beginning 25 minutes before `t0`, the plan's scheduled measurement start, and ending under the existing chain and courier completion rules. Permission to retry an arm abort does not excuse a process inside that span. `production_census` uses the night gate's raw process check. `handoff_census` checks departure of owned processes only, and `_is_interactive_claude` recognizes command shape only; neither proves the arm or plan-span census clean. A172 changes none of them.

A **listed install span** is a local-time interval from `run_night.INSTALL_SPANS`,
resolved for its local date; an **epoch second** counts from 1970-01-01 00:00 UTC.
`install_close_epoch(plan)` is the exclusive install cutoff, `t0 − 85 minutes`;
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
| `night_refused_agent_present` | Production census refusal, including a receipt at t0; never an idle arm event. |
| `night_refused_not_quiet` | Machine quietness failed; load, power and thermal thresholds stay fixed. |
| `night_refused_hid_idle` | User-input inactivity guard failed. |
| `night_refused_boot_clock` | Measurement boot/clock guard failed; not a watchdog uncertainty tick. |
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

Unknown or mixed causes, any receipt refusal, and every capture, clock, custody, ledger or pre-registration guard stay on the cold-gate path. Known concurrent refusal evidence overrides an eligible arm cause. These dispositions preserve existing harvest, delivery and human-resolution remedies; they do not call a review into a live chain.

R1's operative time bounds are `now < install_close_epoch(plan)` and plan age within `PLAN_MAX_AGE_S` (including the existing authored-to-t0 check), with at least 60 seconds between arm attempts. D-180's same-or-next-listed-span ceiling is subsumed by `install_close_epoch(plan)` and `PLAN_MAX_AGE_S`, because with whole-day install spans it could otherwise bind 15 minutes before install close. There is no attempt-count cap, separate notice-age limit, new window cadence or delay after a successful harvest.

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

Plan `rehearsal-20260916c`, class `REHEARSAL_STUB`, is planned for 2026-09-16
at 03:25:00 PDT (`t0`, epoch 1789554300) with a 900-second window
(`window_max_s`; the window ends at 03:40:00 PDT, epoch 1789555200). The
courier deadline is `t0 + 900 + 300`, epoch 1789555500, 03:45:00 PDT; this is
also the **completion boundary**. The driver runs its built-in stub,
`sleep 2; echo REHEARSAL`: no pack, no model, no measurement, no sudo. The
**dead-man**, the second launchd job that recovers missing delivery after
completion, is `60 × ceil((1789555500 + 3600) / 60) = 1789559100`, 04:45:00 PDT
on 2026-09-16, repeating daily at that local minute until uninstalled. This
notice describes the planned night; the arm record establishes whether
installation happened.

This stub is the first night armed under the machinery merged on 2026-09-16:
the transactional installer (INSTALL-WINDOWS-MULTI-01, PR #341: several
install spans per day, `t0` on any whole minute, record-and-poll signals), the
shortened arm-to-t0 floor (LEAD-MARGIN-01, PR #344: PLAN/REQUEST/TERM/KILL leads
of 8/8/6/5 minutes and a 2-minute install pad, so install close is
`t0 − 10 min`), the stub-only idle-interactive arm census
(ARM-CENSUS-IDLE-INTERACTIVE-01, PR #343), the pre-authorized arm-retry class
(ARM-RETRY-CLASS-01, PR #342) and the staged-plan `--render-only` validation
(PR #346). It rehearses, live under launchd and from a fresh clone: the install
transaction, the resident ladder at the new leads, the driver's gate rows on a
`REHEARSAL_STUB`, and the courier. It acquires nothing.

Ed's interactive session (and its Codex seats) may still be alive at `t0`. For
a stub the unfiltered t0 census then records `night_refused_agent_present`
and the driver retains its harmless-stub continuation: the stub still runs and
the hit is recorded. That is an expected, correct outcome for this rehearsal
of the machinery; a real night refuses on the same hit and starts no chain.

`repo_head = measurement_head = H`, where H is **this commit**, the main
commit that rewrites this handback for this night. The fresh clone at H is
`/Users/edr/JouleWise-measurement-rehearsal-20260916c` (a `.venv` whose
`bin/python` is Python 3.13 from `env/mac-measurement-lock.txt`, the
interpreter both LaunchAgents name by absolute path; the canonical 76-record
ledger restored byte-exact for the desk checks). Both night agents are
installed from that clone. It serves only this stub; it is retired with the
plan root after harvest and never reused for a real plan.

The consolidated notice with these pins is sent after commit H and before the
plan is moved into its discoverable place; Ed's NO on the notice thread stands
the night down. The arming activation (headless magistrate `83d93f5a`) exits
after recording the arm. The plan span opens, and the watchdog's stand-down
request lands, at `t0 − 8 min` = 03:17:00 PDT (epoch 1789553820); TERM is
`t0 − 6 min` (1789553940, 03:19:00) and KILL is `t0 − 5 min` (1789554000,
03:20:00). Install close is `t0 − 10 min` = 03:15:00 PDT (1789553700). The
install-span list is the shipped whole-day span (00:00–24:00 local).

The predecessor plan `d079-epoch-25g83-derivation-n1-20260915` was refused at
its own t0 on 2026-09-15, harvested, its agents uninstalled, and its plan root
retired to `~/night-archive` on 2026-09-15 at 23:25 PDT (activation
`08ca8197`, record 04). The `20260916` successor prepared by record 50 was
never authored as a plan; the equivalence science night is re-planned after
this stub under §Next lane.

The first candidate for this rehearsal, plan `rehearsal-20260916` at H
`cf249594` (t0 03:00:00 PDT 2026-09-16), was staged and preflighted by
activation `08ca8197` but NEVER published: arm attempt 1 aborted on
`arm_transport` (the Gmail connector was expired in that process), activation
`736e2aed` spawned without Gmail tools during the claude.ai connector outage,
and the candidate lapsed unarmed at its install close (02:50). Its staged
bytes and attempt evidence stay under `~/night-plan-staging/rehearsal-20260916`
(no plan under night-custody; nothing was installed). This plan carries the
`c` suffix so that it shares no path with that candidate. Ed's directive
issue #349 (2026-09-16 02:40 PDT) rules that when the Gmail connector is
unavailable the arm notice may be posted as a GitHub issue labelled
`directive-notice` with the same content; the arm record names the transport
used. Email remains primary and is the transport for this plan's notice when
it sends.

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

## Where the results are

- Custody root: `/Users/edr/night-custody/rehearsal-20260916c`; driver records
  in `night/` — `result.json` (expected verdict `REHEARSAL_ONLY` with
  `chain_exit_code` 0 on a clean census; if an agent session is alive at t0
  the gate records `night_refused_agent_present` and the stub still completes),
  `receipt.json` or `refusal.json` as `result.json` directs (C2
  `NOT_APPLICABLE` / `no_pack_by_design`; no chain digest to bind, the stub has
  no wrapper), `chain.started`, `chain.exited`, `censuses.jsonl`,
  `chain.stdout.log` (`REHEARSAL`), `chain.stderr.log`, `courier.sent`,
  `courier.json`, `courier.heartbeat`.
- Driver log: `/Users/edr/night-custody/rehearsal-20260916c/night.log` — read
  `night driver started` and the `night gate verdict=` line; a dead-man line
  dated before completion is expected only if its daily minute occurred after
  install (it does not: 04:45 is after completion).
- Launchd streams: `night/launchd.night.out` and `night/launchd.night.err`;
  `launchd.night.err` must be EMPTY.
- Results branch: `night-results/rehearsal-20260916c` on `origin`, if the
  driver's push succeeded — verify, do not presume; trace directory
  `docs/process_traces/night-results/rehearsal-20260916c/`.
- No captures, no ledger rows, no chain log: a stub acquires nothing.

## Next lane

The relaunched magistrate (its prompt carries the frozen triple
`rehearsal-20260916c` / `/Users/edr/JouleWise-measurement-rehearsal-20260916c` /
this commit) harvests only after the completion boundary (03:45:00 PDT) has
passed and `courier.sent` exists: read `result.json`, the receipt or refusal,
`night.log` and both launchd streams; preserve the custody root byte-exact
outside watchdog discovery with an `lstat` inventory before anything is moved.
The acceptance for this stub is `result.json` verdict `REHEARSAL_ONLY` (or a
recorded `night_refused_agent_present` hit with the stub still completing),
`chain_exit_code` 0, and an EMPTY `launchd.night.err`. Any crash, a non-empty
`launchd.night.err`, a `night_probe_error`, or an installer/launchd
irregularity is a finding to cure before any further night.

After the harvest, run `scripts/install_night_agent.sh --plan
/Users/edr/night-custody/rehearsal-20260916c/night_plan.json --uninstall` FROM
the clone and record its exit code. Only exit 0 permits retiring the plan root
(byte-exact archive to `~/night-archive/rehearsal-20260916c-plan-root-retired-<epoch>`
with `SHA256SUMS`, record-48 procedure) and removing the stub clone.

Then the science: author the equivalence night per Ed's ruling in issue #316
(night one = the equivalence check against the r6 operatives; the D-102
addendum on PASS; the FAIL route's registration nights otherwise) as its own
`DIAGNOSTIC_NO_PACK` plan under runbook §1.1–§1.5 on the merged main, with a
clean all-agents-closed census (no stub exemption for that class), and arm it
under this same handback procedure; loop under D-181 (windows whenever the
machine is quiet). A t0 refusal on machine state follows REFUSAL-FAST-RETRY-01
once it lands; until then it is harvested and re-planned. Physics, evidence and
pre-registration refusals stay on the cold-gate path; email Ed for those only.

For every v2 plan, run `scripts/install_night_agent.sh` FROM the checkout
named by the plan's `measurement_root`, with that checkout at the plan's
`measurement_head`; never install the two night agents from the development
checkout. Once authored, every armed plan's canonical
`(plan_id, measurement_root, measurement_head)` is included in the magistrate
relaunch prompt's frozen-checkout list until completion.

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
Install and `--render-only DIR` (render the two job files to a directory
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
