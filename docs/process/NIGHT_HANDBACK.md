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

Plan `rehearsal-20260911`, class `REHEARSAL_STUB`, is planned for
2026-09-11 at 02:56:00 PDT (`t0`, epoch 1789120560), with a 900-second
window. The courier deadline is `t0 + 900 + 300`, epoch 1789121760,
03:16:00 PDT that morning. The driver runs its built-in stub,
`sleep 2; echo REHEARSAL`: no pack, no model, no measurement, no sudo.
This notice describes the planned night; the arm record establishes
whether installation happened.

This second stub night combines two checks for `NIGHT-REHEARSAL-01`.
Installing both agents on **2026-09-10 between 03:00 and 06:30 PDT**
lets the 07:00 dead-man fire that morning (epoch 1789048800), before
the night, and stand down with one line in `night.log` and nothing
written into `night/` by that firing. That is acceptance item 5's
R-7 observation. Installing after that day's 02:56 also keeps the night
agent from firing a day early. The night then fires at 02:56 on 09-11;
item 6 is re-satisfied only if its receipt is not refused. An
agent-present refusal can close item 5 only, not item 6.

`repo_head = measurement_head = H`, where H is **this commit**, the main
commit that rewrites this handback for this night, descended from the
cure merge `a52810c9`. The disposable detached checkout at H is
`/private/tmp/joulewise-rehearsal-20260911-checkout`. Both night agents
are installed from it. It is used only by this stub and removed with
the plan root after harvest; it is never reused for a real plan.

The consolidated notice with these pins is sent after commit H and
before the plan is moved into place. Ed's NO on the notice thread
stands the night down. The arming activation exits after recording the
arm. The watchdog's exit boundary is 02:31:00 PDT on 09-11
(epoch 1789119060, `t0 − 25 minutes`); its relaunch belt is
02:45–03:30 PDT. Power source, powermode and the timer probe are
recorded at arm time. Powermode is recorded, not gated, for this stub;
a green stub says nothing about the capture-timeout seam.

These pins and acceptance conditions come from the
[magistrate synthesis](../process_traces/2026-09-09-rehearsal-harvest/65-magistrate-synthesis-second-stub-night.md).
The [arm runbook](../process_traces/2026-09-09-rehearsal-harvest/67-arm-runbook-rehearsal-20260911.md)
gives the command sequence.

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

## Where the results are

- Custody root: `/Users/edr/night-custody/rehearsal-20260911`; records in `night/` —
  `result.json` (expected verdict `REHEARSAL_ONLY`, `chain_exit_code` 0),
  `receipt.json` or `refusal.json` as `result.json` directs,
  `chain.started`, `chain.exited`, `censuses.jsonl`, `courier.sent`,
  `courier.json`.
- Driver log: `/Users/edr/night-custody/rehearsal-20260911/night.log`.
  At harvest, look for the 2026-09-10 07:00 dead-man stand-down line
  before the 09-11 `night gate verdict=` line.
- Results branch: `night-results/20260911` on `origin`, if the driver's
  push succeeded — verify, do not presume.

## Next lane for rehearsal-20260911

The relaunched magistrate (its prompt carries the frozen triple
`rehearsal-20260911` / `/private/tmp/joulewise-rehearsal-20260911-checkout`
/ this commit) harvests `result.json`, the receipt or refusal, the courier
message id and the results-branch evidence, records them under
`NIGHT-REHEARSAL-01`. Acceptance requires `receipt.json` verdict
`REHEARSAL_ONLY`, with C5 recording `chain_stub: built_in_stub_by_design`
and null `chain_sha256` and `expected_chain_sha256`. The log must show
the pre-night dead-man standing down, with nothing in `night/` from
that firing. A receipt refusing `night_refused_agent_present` is
acceptable only for item 5; item 6 still needs a non-refused night.
The stub's launchd exit status 3 is not a receipt-refusal signal.

After preserving the evidence, the magistrate runs
`scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260911/night_plan.json --hour 2 --minute 56 --uninstall`
FROM the stub checkout, removes the stub checkout (`git worktree remove`)
and the plan root before any real plan, and then sends the stage-1 plan
email to Ed before any `DIAGNOSTIC_NO_PACK` plan is armed. Accept only
`night_refused_agent_present` as a receipt refusal; cure any other cause
before re-arming; never re-arm the same plan on the same signature twice.
Item 1, the `cold_start.json` deadline derivation, was desk work
separate from this night and is CLOSED as of 2026-09-09 ~17:00 PDT (derivation 70,
fresh capture 104: median 5158 ms, deadline 300 s).
For every v2 plan, run `scripts/install_night_agent.sh` FROM the checkout
named by the plan's `measurement_root`, with that checkout at the plan's
`measurement_head`; never install the two night agents from the
development checkout. Once authored, every armed plan's canonical
`(plan_id, measurement_root, measurement_head)` is included in the magistrate relaunch prompt's
frozen-checkout list until completion.

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
Install and `--render-only` default to `<measurement_root>/.venv/bin/python`;
pass `--python /absolute/path/to/python` to select another Python 3.11+
interpreter (the executable running the driver). A stub checkout needs that
venv or an explicit compatible interpreter with the driver's imports available.

At 02:56 PDT on 2026-09-11, the night driver crashed before any gate because
`python3` found through PATH selected macOS Python 3.9.6, which cannot import
`datetime.UTC`. A **LaunchAgent** is a macOS launchd job file; each job now names
an absolute interpreter path. A **driver preflight** here runs the driver's
imports under that exact interpreter and the job's environment before the job
is installed. The installer prints its JSON success record for the arm record
and refuses installation if it fails.

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
selected at install time. The chain and its input preflight (checks before
measurements start) verify checkout HEAD against `measurement_head`; that
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
