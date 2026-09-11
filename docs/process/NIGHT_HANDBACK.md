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

## Purpose of this night

Plan `rehearsal-20260912`, class `REHEARSAL_STUB`, is planned for
2026-09-12 at 00:30:00 PDT (`t0`, epoch 1789198200), with a 900-second
window. The courier deadline is `t0 + 900 + 300`, epoch 1789199400,
00:50:00 PDT that morning. The driver runs its built-in stub,
`sleep 2; echo REHEARSAL`: no pack, no model, no measurement, no sudo.
This notice describes the planned night; the arm record establishes
whether installation happened.

`rehearsal-20260911` is RETIRED: its night never ran. At 02:56 PDT on
2026-09-11 macOS's job scheduler started the driver with the Command Line
Tools Python 3.9, and the driver crashed on its first import before any
census, gate or stub ran; the 07:00 dead-man then refused on an orphaned
agent process. Harvest record
`docs/process_traces/2026-09-11-activation-58a3bcfc/01-rehearsal-20260911-harvest-record.md`
and retirement record `02-…-uninstall-and-retirement.md` hold the evidence.
Acceptance item 5 is MET on that night; item 6 is NOT.

This third stub night exists for acceptance item 6 alone. Since PR #309 no
launchd-started driver has reached night-gate rows C1, C4 or the tail of C3:
the 09-09 night stopped at the C5 chain read and the 09-11 night never
started. This night runs those rows live, on a head carrying the interpreter
cure, and fires the cured job file's executable line under launchd for the
first time. Cold-gate ruling
`docs/process_traces/2026-09-11-activation-58a3bcfc/06-coldgate-ruling-item6.md`
§4(c) authorises the off-convention t0 and lists conditions C-1…C-9; its
fallback is a 02:56 stub on 09-13. Item 5 needs nothing from this night, so
the day-before 03:00–06:30 install span does not apply: the agents are
installed on the evening of 2026-09-11, after 07:00 PDT and after 00:30 has
passed that day, so the night agent's first firing IS t0. Both agents are
uninstalled at harvest, before 07:00 on 09-12, so the 07:00 dead-man never
fires; if uninstallation slips past 07:00 it takes the `courier already sent`
branch and is harmless.

`repo_head = measurement_head = H`, where H is **this commit**, the main
commit that rewrites this handback for this night. The disposable detached
checkout at H is `/private/tmp/joulewise-rehearsal-20260912-checkout`, and it
carries a `.venv` whose `bin/python` is Python 3.13 — the interpreter the two
LaunchAgents name by absolute path. Both night agents are installed from that
checkout. It is used only by this stub and is removed with the plan root after
harvest; it is never reused for a real plan.

The consolidated notice with these pins is sent after commit H and before the
plan is moved into place. Ed's NO on the notice thread stands the night down.
The arming activation exits after recording the arm. The watchdog's plan span
opens, and its stand-down request lands, at 00:05:00 PDT on 09-12
(epoch 1789196700, `t0 − 25 minutes`); TERM is `t0 − 16 minutes`
(1789197240) and KILL is `t0 − 15 minutes` (1789197300). The fixed
02:45–03:30 belt does not touch this night. Power source, powermode and the
timer probe are recorded at arm time. Powermode is recorded, not gated, for
this stub; a green stub says nothing about the capture-timeout seam.

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

## Where the results are

- Custody root: `/Users/edr/night-custody/rehearsal-20260912`; records in
  `night/` — `result.json` (expected verdict `REHEARSAL_ONLY`,
  `chain_exit_code` 0), `receipt.json` or `refusal.json` as `result.json`
  directs, `chain.started`, `chain.exited`, `censuses.jsonl`, `courier.sent`,
  `courier.json`.
- Driver log: `/Users/edr/night-custody/rehearsal-20260912/night.log`.
  At harvest, look for `night driver started` and a `night gate verdict=`
  line. There is no pre-night dead-man firing on this night, by design.
- Launchd streams: `night/launchd.night.out` and `night/launchd.night.err`.
  `launchd.night.err` must be EMPTY; the 2026-09-11 traceback signature in it
  is the defect this night exists to disprove.
- Results branch: `night-results/20260912` on `origin`, if the driver's push
  succeeded — verify, do not presume.

## Next lane

The relaunched magistrate (its prompt carries the frozen triple
`rehearsal-20260912` / `/private/tmp/joulewise-rehearsal-20260912-checkout`
/ this commit) harvests `result.json`, the receipt or refusal, the courier
message id and the results-branch evidence, and records them under
`NIGHT-REHEARSAL-01` item 6. Acceptance requires `receipt.json` verdict
`REHEARSAL_ONLY` with C1/C3/C4/C5 PASS and C2 `NOT_APPLICABLE`
(`no_pack_by_design`); C1 carrying a measured `registration_sha256`; C3
carrying measured `hid_idle_raw`, `ac_power_raw`, `pmset_g_raw`,
`load_average_raw` and `thermal_raw`; C4 carrying the boot-UUID and
epoch/monotonic pair; C5 recording `chain_stub: built_in_stub_by_design` with
null `chain_sha256` and `expected_chain_sha256`; `result.json`
`REHEARSAL_ONLY` with `chain_exit_code` 0; and `launchd.night.err` empty.
The stub's launchd exit status 3 is not a receipt-refusal signal.

A receipt refusing `night_refused_agent_present`, `night_refused_not_quiet`
or `night_refused_hid_idle` is a CORRECT refusal — the rows ran and refused —
and discharges nothing for item 6; the fallback route of ruling 06 §4(c) C-9
follows. Any `night_probe_error`, crash, non-empty `launchd.night.err`, or
refusal of any other kind is a finding to cure before any plan.

After preserving the evidence, and BEFORE the equivalence night's install
begins at 03:00 PDT on 09-12, the magistrate runs
`scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260912/night_plan.json --hour 0 --minute 30 --uninstall`
FROM the stub checkout, then removes the stub checkout
(`git worktree remove`) and the plan root. Never re-arm this plan, and never
reuse this stub root for a real plan.
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
