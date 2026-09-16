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

## Purpose of this night

This plan is the SUCCESSOR of `d079-epoch-25g83-derivation-n1-20260916`, which
was staged on 2026-09-14 and NOT ARMED: the census stayed foreign through the
06:05 cutoff of its install span (Ed's interactive `claude` session, the
ChatGPT desktop app's Codex helpers and the Claude desktop app's helpers;
see §Executed below), and that plan was itself the successor of the 20260913
night refused at its own t0 census on the same set. Same purpose, same rule,
same chain and pre-registration; its own plan id, session id, night root,
desk inputs and wrapper. Precondition that only the operator can meet: no
interactive agent session, no ChatGPT desktop app and no Claude desktop app
(quit both apps from their menu bar; a running app refuses the night, so no
chain starts) alive from the plan span (02:31 PDT on 2026-09-16) through t0.

Plan `d079-epoch-25g83-derivation-n1-20260916`, class `DIAGNOSTIC_NO_PACK`,
is planned for 2026-09-16 at 02:56:00 PDT (`t0`, epoch 1789552560) with a
9000-second window (`window_max_s`; the acquisition allocation ends at
05:26:00 PDT, epoch 1789561560). The courier deadline is
`t0 + 9000 + 300`, epoch 1789561860, 05:31:00 PDT. This is also the
**completion boundary**, the plan's window end plus the 300 s (5 × 60 s)
courier allowance. The **dead-man**, the second launchd job that recovers
missing delivery after completion, is scheduled by `deadman_epoch(plan)`:
`60 × ceil((1789561860 + 3600) / 60) = 1789565460`, 06:31:00 PDT on
2026-09-16. Here `ceil` rounds upward to an integer; `DEADMAN_GRACE_S = 3600`
is 60 × 60 s after completion. The job repeats daily at that local minute.
This notice describes the planned night; the arm record establishes whether installation happened.

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
`/Users/edr/JouleWise-measurement-20260916-derivation`, a fresh GitHub clone
detached at H whose `.venv/bin/python` is Python 3.13 built from
`env/mac-measurement-lock.txt`; both LaunchAgents are installed FROM it and
name that interpreter by absolute path; its
`runs/calibration_observation_ledger.jsonl` is the canonical 76-record
ledger restored byte-exact and authenticated against its committed head pin
with custody verification. The night root (`custody_root`) is
`/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916`; the runs
root is `<night root>/runs`; the chain's own log is
`<night root>/operator_logs/derivation-chain.log`. The session id equals the
plan id. The evidence root id is
`evidence-d079-epoch-25g83-derivation-n1-20260916`, registered by this
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

**Timeline — updated 2026-09-15, INSTALL-WINDOWS-MULTI-01.** An
**install span** is an interval in which installation is allowed. The plan's
install span opens when its notice email is sent and closes exclusively at
`install_close_epoch(plan) = t0 − PLAN_LEAD_S − INSTALL_CLOSE_MARGIN_S`.
`PLAN_LEAD_S = 1500 = 25 × 60 s` and `INSTALL_CLOSE_MARGIN_S = 3600 = 60 × 60 s`,
so close is `t0 − 85 min`. Installation must also be inside one entry of
`INSTALL_SPANS` in `scripts/run_night.py`, a recurring list of local per-day
spans, with opening included and closing excluded. The shipped list is
`(("00:00", "24:00"),)`; Ed may narrow it. Install any day satisfying both
bounds and the existing gates; the acquisition window need not be inside an
install span.

For the plan coordinates above and a proposed install day of 2026-09-15,
fill the notice-send row from the actual send acceptance. Times below are
local PDT, UTC−07:00; **epoch seconds** count from 1970-01-01 00:00 UTC.

| Boundary | Local date/time | Epoch seconds / arithmetic |
|---|---|---|
| Plan install open | `<actual notice-send local date/time and offset>` | `<actual notice-send epoch>`; never invent a send time |
| Plan install close (exclusive) | 2026-09-16 01:31:00 PDT | `1789552560 − 1500 − 3600 = 1789547460` |
| Every listed span for install day 2026-09-15: shipped entry 1 | 2026-09-15 00:00:00 PDT … 2026-09-16 00:00:00 PDT (close excluded) | `1789455600 … 1789542000`; `INSTALL_SPANS` = `00:00 … 24:00` |
| Plan span opens; request / activation exit boundary | 2026-09-16 02:31:00 PDT | `1789552560 − 1500 = 1789551060` |
| TERM deadline | 2026-09-16 02:40:00 PDT | `1789552560 − 16 × 60 = 1789551600` |
| KILL deadline | 2026-09-16 02:41:00 PDT | `1789552560 − 15 × 60 = 1789551660` |
| `t0` | 2026-09-16 02:56:00 PDT | `1789552560` |
| Acquisition window end | 2026-09-16 05:26:00 PDT | `1789552560 + 9000 = 1789561560` |
| Completion / courier deadline | 2026-09-16 05:31:00 PDT | `1789561560 + 300 = 1789561860` |
| Derived dead-man D | 2026-09-16 06:31:00 PDT | `60 × ceil((1789561860 + 3600) / 60) = 1789565460` |

The **plan span** forbids magistrate agent sessions from its opening through
completion, both boundaries included. After completion, `courier.sent` closes
it; absent that record, it extends through D plus the courier-lock allowance
`300 + max(60, 180, 600) = 900 s` (15 min). A started chain without an exit
record extends it without a clock limit. TERM asks the owned processes to
terminate; KILL forcibly ends survivors under the watchdog's ownership checks.
These stand-down deadlines do not let the arming activation remain past the
exit boundary.

The consolidated notice with these pins is sent after commit H
and before the plan is moved into its discoverable place; Ed's NO on the
notice thread stands the night down. The arming activation exits after
recording the arm. Power source, powermode and the timer probe are recorded
at arm time.

**Procedure — updated 2026-09-15, INSTALL-WINDOWS-MULTI-01.** Follow runbook
§1.4's email-then-arm order. Send one notice email per plan, never one notice
for several arms. From the plan's measurement checkout, use its interpreter:
`<absolute-interpreter-path> scripts/run_night.py schedule --plan <staged-plan-path>`. The JSON
prints `t0_epoch_s`, `install_close_epoch_s`, `deadman_epoch_s`, `night_calendar`,
`deadman_calendar` and `install_spans_today`. With the shipped whole-day list,
the observed `install_spans_today` for 2026-09-15 is
`[[1789455600.0, 1789542000.0]]`: the notice must name that entire pair,
2026-09-15 00:00:00−07:00 through 2026-09-16 00:00:00−07:00 (close excluded).
Convert each epoch to a local
ISO-8601 date/time with offset using
`datetime.fromtimestamp(epoch).astimezone().isoformat()`. For a different
install day, call `install_spans_for_day(date.fromisoformat("YYYY-MM-DD"))`
from `scripts.run_night` (runbook §1.3 supplies the complete print block);
enumerate every returned pair in the notice and
this timeline, including spans the proposed arm will not use. Recompute for
any changed day or span list; the table above is only the shipped-list example.

After notice acceptance, record its local time and epoch as the install open.
Publish the reviewed plan to `<custody_root>/night_plan.json` through the
runbook's atomic move, then run
`scripts/install_night_agent.sh --plan <custody_root>/night_plan.json --python <absolute-interpreter-path>`.
After both bootstraps (launchd job-load operations) and verification, a single
commit gate reads the clock and requires it to be strictly before both the
plan cutoff and the initially selected install span's close. Passing this
gate commits the install before reporting success; subsequent cleanup cannot
undo it or replace its successful result. The installer refuses
`install_span_closed` (exit 2), `install_outside_span` (2),
`plan_t0_in_the_past` (2), `night_agent_already_loaded` (3), and
`plan_outside_custody_root` (2); runbook §1.3 gives each predicate and recovery.
Check the installed night job's Month/Day/Hour/Minute against `t0`, and the
daily dead-man's Hour/Minute against D. Record the schedule JSON, job files
and actual installation result, then exit before the plan span opens.

**Notice-text template — updated 2026-09-15, INSTALL-WINDOWS-MULTI-01.**
Fill all fields for one plan. The first email describes open as its own send
acceptance; put the actual accepted time in the notice evidence and arm record.

> Plan `<plan_id>`, class `<receipt_class>`, will run from `<measurement_root>`
> at H `<full head>`; handback commit `<same full head>`. Custody `<custody_root>`;
> runs `<runs_root>`; wrapper `<path, digest, sidecar>`; tracked chain
> `<path, digest>`; desk inputs `<each path and digest>`. Install opens when
> this notice is accepted for sending (that local time and epoch will be
> recorded) and closes at `<install_close local + epoch>`. Listed install
> spans on `<install day>`: `<EVERY open/close pair, local + epoch>`.
> Plan span: `<t0 − 25 min local + epoch>` through `<completion local + epoch>`,
> subject to the courier/chain extensions in this handback. `t0` is
> `<local + UTC + epoch>`; `window_max_s = <seconds and duration arithmetic>`.
> Courier deadline: `<completion local + epoch>`. Daily dead-man minute:
> `<D local + epoch>`, completion plus 3600 s rounded up to a minute.
> The arming activation exits before `<t0 − 25 min local + epoch>`.
> Launch needs no action from Ed unless he replies NO; Ed's NO overrides.

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

- Custody root: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916`;
  driver records in `night/` — `result.json` (expected verdict `GO` for
  this class when every gate row passes, `chain_exit_code` 0),
  `receipt.json` or `refusal.json` as `result.json` directs (C1 PASS with the
  D-166 registration hash, C2 `NOT_APPLICABLE` / `no_pack_by_design`, C3, C4
  and C5 PASS with C5's `chain_sha256` equal to the wrapper's digest),
  `chain.started`, `chain.exited`, `censuses.jsonl`, `chain.stdout.log`,
  `chain.stderr.log` (the wrapper's `FAIL <reason>` lines, if any),
  `courier.sent`, `courier.json`, `courier.heartbeat`.
- Driver log: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/night.log`.
  Harvest text updated 2026-09-15 (INSTALL-WINDOWS-MULTI-01): a dead-man
  line dated before completion is expected evidence if its daily minute
  occurred after install; after `courier.sent` the dead-man skips. Read
  `night driver started` and the plan's `night gate verdict=` line.
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
- Results branch: `night-results/<plan_id>` (here `night-results/d079-epoch-25g83-derivation-n1-20260916`) on `origin`, if the driver's push
  succeeded — verify, do not presume. Its trace directory is
  `docs/process_traces/night-results/<plan_id>/`; both use the full plan ID.

## Next lane

The relaunched magistrate (its prompt carries the frozen triple
`d079-epoch-25g83-derivation-n1-20260916` /
`/Users/edr/JouleWise-measurement-20260916-derivation` / this commit) harvests
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
/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260916/night_plan.json
--uninstall` FROM the clone (command updated 2026-09-15,
INSTALL-WINDOWS-MULTI-01). Record its exit code before any retirement (removing
the old night's checkout or files from service) or successor arming. **Only
exit 0 permits uninstall-dependent steps.** Exit 4 means **retained**: a
launchd job name (label) is still loaded, or its query is **UNKNOWN**, meaning
the installer cannot determine whether it is loaded. It changes no files and
keeps the job files (plists) and any `.prior` sidecars. `.prior` sidecars hold
the bytes an install replaced. Nothing restores them automatically after the
installer exits: a later install refuses while one is present, and
`--uninstall` deletes both the plists and the sidecars. Copy a sidecar by hand
if you need the old plist back. This is a deliberate stop, not a crash or a
partial install. **Exit 4
STOPS retirement and successor arming until a human resolves the loaded or
UNKNOWN label and `--uninstall` exits 0.** Re-running `--uninstall` is safe and
**idempotent**: repeating it does not undo a successful uninstall, and a loaded
or UNKNOWN label continues to protect the files from removal. Any other
nonzero exit also stops uninstall-dependent steps.

Do NOT remove the clone or
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
