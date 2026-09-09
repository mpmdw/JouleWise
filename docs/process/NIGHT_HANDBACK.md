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

Cut rehearsal checkouts as `JouleWise-rehearsal-<date>-<sha>`; the reviewed
`JouleWise-rehearsal-` prefix is exact and case-sensitive. Replace `<sha>` in
examples with the reviewed checkout commit. The clone must NOT be listed in
`configs/production_custody_inventory.json` and must sit at a head carrying
that file. For T0_REHEARSAL it must also be disjoint from every inventoried
measurement root (no equality or containment in either direction).

Plan `rehearsal-20260909`, class `REHEARSAL_STUB`, armed by the headless
magistrate (activation 1ef89702, spawned by the relaunch watchdog on
2026-09-08 00:51:55 PDT) for 02:56 local on 2026-09-09 with a 900 s
window, inside the 02:45–03:30 belt. It is the fresh post-watchdog
rehearsal the state kernel requires before any real plan
(`NIGHT-REHEARSAL-01`, last acceptance item). The chain is the driver's
built-in stub (`sleep 2; echo REHEARSAL`); no pack, no model, no
measurement, no sudo. The plan is v2: `repo_head` and `measurement_head`
both pin THIS commit (the one that rewrote this file), and
`measurement_root` is a disposable detached checkout of this commit at
`/private/tmp/JouleWise-rehearsal-20260909-<sha>`, used only by this
stub and removed with the plan root before any real plan; the measurement
checkout of record (`/Users/edr/JouleWise-measurement-20260813`) is
untouched. Both night agents are installed FROM that checkout. Ed was
emailed the arming notice before the arm (thread `1a0800cdb282c3f1`, with
the exact pins in its follow-up); a NO on that thread stands the night
down. Expected: `result.json` verdict `REHEARSAL_ONLY`, chain exit 0,
courier deadline `t0 + 900 + 300` = 03:16 PDT. A receipt refusing
`night_refused_agent_present` is acceptable for a stub (it can never
carry GO); any other refusal is a finding. If the agents were installed
before 07:00 on 2026-09-08, that morning's dead-man firing stands down
with one `night.log` line (the R-7 observable); otherwise this night does
not repeat that case. The design ruling and bench pass are in
`docs/process_traces/2026-09-02-hands-free-week/21b-rehearsal-20260909-arm-plan.md`.

## Executed — reconciliation dated 2026-09-09 (activation 628c2eed; harvest record 21i)

The night described above was armed by headless activation `784a764e` (not `1ef89702`, which prepared it) with the frozen triple
(`rehearsal-20260909`, `/private/tmp/joulewise-rehearsal-20260909-checkout`, `ae8f074f`) — the checkout name differs from the
`JouleWise-rehearsal-20260909-<sha>` example above; the arm record is
`docs/process_traces/2026-09-02-hands-free-week/21h-rehearsal-20260909-arm-record.md`. It fired at 02:56 PDT on 2026-09-09:
result `REHEARSAL_ONLY`, chain exit 0, results branch `night-results/20260909` at `a84e0f7f`, courier email `1a08599a4ff4d005`.
The receipt refused `night_probe_error` (the gate read `chain.zsh`, which the stub arm never writes) — a finding; the cure is committed on branch `fix/2026-09-09-night-gate-stub-chain` at `bb7090e2` under review, not yet merged, as lane
NIGHT-GATE-STUB-CHAIN-01; the plan is not re-armed on that signature. The §Next lane harvest, `--uninstall` from the stub checkout,
and removal of the stub checkout and plan root are DONE (record 21i); nothing is armed and the frozen-checkout list is empty apart
from the canonical repo. The standing rules below are unchanged; the next plan's author rewrites §Purpose, §Where the results are and
§Next lane for that plan under the same procedure.

## Where the results are

- Custody root: `/Users/edr/night-custody/rehearsal-20260909/night/` —
  `result.json` (expected verdict `REHEARSAL_ONLY`, `chain_exit_code` 0),
  `receipt.json` or `refusal.json` as `result.json` directs,
  `chain.started`, `chain.exited`, `censuses.jsonl`, `courier.sent`,
  `courier.json`.
- Driver log: `/Users/edr/night-custody/rehearsal-20260909/night.log`
  (and the dead-man stand-down line if the 2026-09-08 07:00 firing
  preceded the night).
- Results branch: `night-results/20260909` on `origin`, if the driver's
  push succeeded — verify, do not presume.

## Next lane

The relaunched magistrate (its prompt carries the frozen triple
`rehearsal-20260909` / `/private/tmp/JouleWise-rehearsal-20260909-<sha>`
/ this commit) harvests `result.json`, the receipt or refusal, the courier
message id and the results-branch evidence, records them under
`NIGHT-REHEARSAL-01`, then runs
`scripts/install_night_agent.sh --plan /Users/edr/night-custody/rehearsal-20260909/night_plan.json --hour 2 --minute 56 --uninstall`
FROM the stub checkout, removes the stub checkout (`git worktree remove`)
and the plan root before any real plan, and then sends the stage-1 plan
email to Ed before any `DIAGNOSTIC_NO_PACK` plan is armed. Accept only
`night_refused_agent_present` as a receipt refusal; cure any other cause
before re-arming; never re-arm the same plan on the same signature twice.
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
needs `claude` on PATH.
Ordinary
daytime work in the dev checkout no longer invalidates an armed night; only
moving the pinned measurement checkout does. Once authored, every armed
plan's canonical `(plan_id, measurement_root, measurement_head)` is included
in the magistrate relaunch prompt's frozen-checkout list until completion.

G2-a routing handoff (2026-09-08; installed):
`scripts/run_night.py::_run_chain_once` derives `MEASUREMENT_ROOT`,
`MEASUREMENT_HEAD`, and `PY` from the parsed v2 plan and overwrites inherited
values in the child environment alongside `NIGHT_PLAN_ID`. There is no v2
interpreter field: the driver, chain, and preflight always derive
`<measurement_root>/.venv/bin/python`. The chain and preflight verify checkout
HEAD against `measurement_head`. The preflight's sole argument is the absolute
v2 plan filename. Future clone naming and the exact locked venv creation
commands live in [the runsheet's plan-derived block](../process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md#plan-derived-measurement-variables).

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
