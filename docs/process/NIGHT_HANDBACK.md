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

Plan `d079-epoch-25g83-derivation-n1-20260913`, class `DIAGNOSTIC_NO_PACK`,
is planned for 2026-09-13 at 02:56:00 PDT (`t0`, epoch 1789293360) with a
9000-second window (`window_max_s`; the acquisition allocation ends at
05:26:00 PDT, epoch 1789302360). The courier deadline is
`t0 + 9000 + 300`, epoch 1789302660, 05:31:00 PDT; the next 07:00 dead-man
minute is epoch 1789308000, 89 minutes after it. This notice describes the
planned night; the arm record establishes whether installation happened.

**What the night does.** It is the epoch-equivalence check that Ed's
directive issue 316 ruled on 2026-09-10, transcribed as revision 2 of
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
`b8bf5b0a85bb2012eed9763f70743963d6f24c3ec3038142525766c00f1ac8cf`, the value
this commit also writes into the pre-registration's chain-digest field).

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

**Pins.** `repo_head = measurement_head = H`, where H is **this commit**: the
main commit that rewrites this handback, appends the production inventory
row for the measurement root, and fills the pre-registration's five
commit-time fields (authoring day 10, MLX 0.31.2, head pin 76 /
`08456d5076c18a9a7f758969b02f5b6f7ad9fcc267dd12e2d3778c22458094d7`, chain
digest above). The measurement root is
`/Users/edr/JouleWise-measurement-20260913-derivation`, a fresh GitHub clone
detached at H whose `.venv/bin/python` is Python 3.13 built from
`env/mac-measurement-lock.txt`; both LaunchAgents are installed FROM it and
name that interpreter by absolute path; its
`runs/calibration_observation_ledger.jsonl` is the canonical 76-record
ledger restored byte-exact and authenticated against its committed head pin
with custody verification. The night root (`custody_root`) is
`/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913`; the runs
root is `<night root>/runs`; the chain's own log is
`<night root>/operator_logs/derivation-chain.log`. The session id equals the
plan id. The evidence root id is
`evidence-d079-epoch-25g83-derivation-n1-20260913`, registered by this
night's arm record (the runbook names no derivable default; the form follows
the G2-a runbook's `evidence-<window id>`). The frozen calibration plan is
the committed bytes of
`configs/campaigns/d117_floor_qwen25_1p5b_v3/calibration_plan.json` copied to
`<night root>/calibration_plan.json`: the ledger session records it by
`plan_id` and SHA-256 as an identity binding, and a derivation-only capture
reads nothing else from it. The two desk inputs `identity-epoch.json` and
`t1-bindings.json` are written into the night root by
`scripts/write_derivation_night_inputs.py` at the arm and their digests are
baked into the wrapper.

**Timeline.** Both agents are installed on 2026-09-12 inside 03:00–06:30
PDT, the calendar day before `t0`. The 07:00 dead-man firing on 09-12 stands
down with one log line and writes nothing else into `night/`; that line is
expected evidence. The watchdog's plan span opens, and its stand-down request
lands, at `t0 − 25 minutes`, 02:31:00 PDT on 09-13 (epoch 1789291860); TERM
is `t0 − 16 minutes` (1789292400) and KILL is `t0 − 15 minutes`
(1789292460); `t0` sits inside the fixed 02:45–03:30 belt, which is correct
for a night. The consolidated notice with these pins is sent after commit H
and before the plan is moved into its discoverable place; Ed's NO on the
notice thread stands the night down. The arming activation exits after
recording the arm. Power source, powermode and the timer probe are recorded
at arm time.

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

## Where the results are

- Custody root: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913`;
  driver records in `night/` — `result.json` (expected verdict `GO` for
  this class when every gate row passes, `chain_exit_code` 0),
  `receipt.json` or `refusal.json` as `result.json` directs (C1 PASS with the
  D-166 registration hash, C2 `NOT_APPLICABLE` / `no_pack_by_design`, C3, C4
  and C5 PASS with C5's `chain_sha256` equal to the wrapper's digest),
  `chain.started`, `chain.exited`, `censuses.jsonl`, `chain.stdout.log`,
  `chain.stderr.log` (the wrapper's `FAIL <reason>` lines, if any),
  `courier.sent`, `courier.json`, `courier.heartbeat`.
- Driver log: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913/night.log`.
  At harvest, look for the 09-12 07:00 dead-man stand-down line, then
  `night driver started` and a `night gate verdict=` line for 09-13.
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
- Results branch: `night-results/20260913` on `origin`, if the driver's push
  succeeded — verify, do not presume.

## Next lane

The relaunched magistrate (its prompt carries the frozen triple
`d079-epoch-25g83-derivation-n1-20260913` /
`/Users/edr/JouleWise-measurement-20260913-derivation` / this commit) harvests
only after the plan span's completion boundary has passed and `courier.sent`
exists. It follows runbook §2 in order: §2.0 rebuilds the night's
coordinates from the frozen triple and verifies the wrapper against its
sidecar before reading anything out of it; §2.1 reads `result.json`, the
receipt or refusal, the chain log, the launchd streams and
`check --session-ids <session id>`; the custody root is preserved byte-exact
outside watchdog discovery with an `lstat` inventory before anything is
moved. Then §2.5: run `scripts/epoch_equivalence_check.py` twice (the clone,
and a second checkout at the same head, different `--out`), compare the two
records byte for byte, and take exactly the one action the outcome table
names — INCONCLUSIVE (m < 6): arm one more equivalence night; PASS: write the
dated D-102 continuation addendum quoting the session id, the twelve slot
outcomes, m and the m retained lexemes, then the first real G2-a window under
the ordinary path; FAIL: revision 1's nights two and three follow (§3, §4)
with this night counted as night one. Before applying the rule, re-hash the
committed pre-registration at H and require equality with the arm record's
digest.

A receipt refusing `night_refused_agent_present`, `night_refused_not_quiet`
or `night_refused_hid_idle` is a correct refusal — the rows ran and refused —
and the night is re-planned, never re-armed on the same plan. Any
`night_probe_error`, crash, non-empty `launchd.night.err`, a wrapper `FAIL`
before the settle, or a `slot_refused` line is a finding to cure before any
further night.

After the harvest, run `scripts/install_night_agent.sh --plan
/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260913/night_plan.json
--hour 2 --minute 56 --uninstall` FROM the clone. Do NOT remove the clone or
the night root: the ledger session and the captures live there and the clone
is a production inventory row. Never re-arm this plan; every further night is
its own plan, session id, night root, desk inputs and wrapper.

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
