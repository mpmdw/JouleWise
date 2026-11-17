TBD. **Laptop lead, DRAFT NOT ISSUED, prepared by Sol on 2026-11-16;
ISSUED <LEAD FILLS: timestamp from `date`, epoch, main item number>:
MAGISTRATE: prepare and arm ONE slot-producing ALIGN v4 R1 session on
`b2e01464d6d4fbf2901ff4d4154df9455104a12a`, detached at
`/Users/edr/code/jw-wt/r1-slot-b2e01464d`, using its own HAZARD_PACK
LaunchAgent route. Full R1 program, Automatic admission, D no holds,
N_chunk 4096, TV0h/TV1h, Tf08 recorded. No campaign span, campaign queue
extension or W1 is authorized by this item. EARLIEST: the next clean
close after the lead's READY record, its completed Check/restores/copy
and applicable close floor, then ordinary notice/install requirements.
LIMIT <LEAD FILLS: this session's validity/window; do not copy a counted
span's 24 h expiry without authority>. Expected runtime UNKNOWN pending
lead print; driver bound 102168 s (28:22:48), outer 119880 s (33:18),
plus 300 s shutdown grace. Install is your final operational action;
sleep display and exit all agent sessions before t0.**

```pointer
owner: magistrate
wait: LEAD FILLS: predecessor id / latest real running session, clean close and floor, or already-clean host evidence
deadline: LEAD FILLS: latest end plus existing deadman/recovery check timing from generated schedule
on_early_or_refused: any missing/open checklist line, stop/veto, unproven restore/group, failed/unverified offload, stale authorization, or failed prepare/install: NOTHING arms; preserve outputs and report to the lead by the existing authorized route. Do not retry a measured session, skip a hold, extend a queue, reuse S, or erase recovery markers. A new t0/issue goes through the same route. A running lower-priority span finishes.
next_observable: before install: the lead-issued checklist and ordinary notice, PKT_SHA, actual arm.json/plan digest/t0/end/deadman, fresh host and no-veto reads. On next post-fence activation: registered R1 terminal status plus chain exit, restore and process-absence Check; lead handles results/slot fills under the owning procedure.
```

Authorization and priority: RL-149 §5.12 restores the RL-145 step-4
checklist with the close's additions; RL-152/153/156/159/170/172b/172c
govern subsequent repairs and carry. RL-174 B makes this checklist the
lead's first priority. **LEAD FILLS: final CHECKLIST adoption and READY
record on origin/main, with main commit/item/time.** From that READY
record nothing lower priority arms (RL-172(f)); before it queues continue
normally. This typed entry uses ENTRY-DRAFT's R1 route and never
`cadence_queue.py next` or `launch_cadence_span.py`. Never abort F0/F2 or
other running work to make room.

The lead fills these before declaring READY:

- Package audit commit and staging record: **LEAD FILLS**. Measurement
  worktree P, clean/detached, existing venv link only; SOURCES hashes.
- Ticked CHECKLIST: **LEAD FILLS**. Resolve Q1, adopt amendment draft
  path/head, carry/import/S 329 correction and actual Part C typical-case
  table. No new Part C solely for P: S 328 carries under RL-172b/172c.
- Final notice route and veto handling: **LEAD FILLS**, using existing
  authority (S 306's directive-notice fallback if still applicable).
  Record actual notice send and last Ed directive read; no inferred NO.
- Fresh newest-close id/time, fence-seen-gone time, Check/ref, restore,
  process-group absence and verified off-host marker: **LEAD FILLS**.
  Campaign close floor 300 s; other/F0/F2 floor 1200 s. Typed marker
  obeys RL-173 A as amended by RL-174 D. Failed verification holds arm.
- Whole-minute t0, Pacific/UTC, expected-duration print, outer latest end
  including grace and existing deadman time: **LEAD FILLS**.
- Host readback: **LEAD FILLS** — Mac15,9, AC/not charging, no external
  mount; Automatic; network-time/frequency-word state; no High Power
  marker/armed job/monitor/root sampler/R12/packer; free disk. State
  `spotlightknowledged` present/absent, `corespotlightd` present, `/`
  indexing off, Time Machine destination none (or actual recorded
  state). Nothing changes hygiene between freeze 2 and qual-03 close.
- Pending iCloud transfer read: **LEAD FILLS**. Nothing of ours writes
  iCloud during the session; sync daemons remain in maintenance print.
  Key's second copy was recorded in S 353; no new key request is needed.

**Start and check (lead/magistrate in a clean close interval only).**
Run the eight synthetic modules using `run_source_checks.sh` **off the
MBP**, adopt VERIFICATION and the exact pin. Do not build/test/analyze
on the MBP while any queue is live (RL-172(i)). Lead/magistrate runs
`stage_mbp_r1.sh` from a copy of this committed package with
`JW_CLOSE_WINDOW_CONFIRMED=yes`, captures its output and package commit,
then checks native host/environment evidence. The staging script does
not authorize an arm and does not contact the Mac from this worktree.

```zsh
set -euo pipefail
export M=/Users/edr/code/jw-wt/r1-slot-b2e01464d
export PY=/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python
test "$(git -C "$M" rev-parse HEAD)" = b2e01464d6d4fbf2901ff4d4154df9455104a12a
test -z "$(git -C "$M" status --porcelain --untracked-files=all)"
# Native imports only, no package installs. Must print 0.31.2 0.31.3 5.12.1.
"$PY" -B -c 'import mlx.core,mlx_lm,transformers; from importlib.metadata import version; print(*(version(x) for x in ("mlx","mlx_lm","transformers")))'
# Item 377 says the old R0 path was archived. Use the hash-verified restored
# R0 file, whose path the magistrate records; do not re-extract during a run.
: "${R0:?LEAD FILLS: verified restored R0 path from item 377 or later record}"
"$PY" -B "$M/scripts/align_r1_r0_classes_from_r0.py" check --r0 "$R0" --config "$M/configs/align/v4/r1_runtime.json" || { print -u2 'STOP: R0 check failed'; exit 1; }
# Check output against CHECKLIST A14 and SOURCES; fresh host checks above
# use the existing measurement_mode / network-time zero-step procedures.
unset JOULEWISE_HOST_STATE_DIR ALIGN_R1_RUNTIME ALIGN_R1_INPUTS ALIGN_R1_REGISTRATION
unset EVIDENCE_POWER_RECORDER_REPLAY NIGHT_VERIFY_ONLY NIGHT_RESERVATION_ARGV_ONLY
```

D-7, on these final bytes: preserve an existing packet before removing its
fixed name; then regenerate with real registered weight and stack checks.
Never reuse a packet merely because the commit matches. A preparation
failure may leave a REFUSED packet: it is not a valid arm attachment.

```zsh
set -euo pipefail
export S="/Users/edr/night-align/r1-$(date -u +%Y%m%dT%H%M%SZ)"
test ! -e "$S"                    # new session only
# LEAD FILLS: archive prior $M/.align-r1-prepare.json, if present, to a
# private preparation archive; remove the fixed name per D-7. Retain it.
test ! -e "$M/.align-r1-prepare.json"
"$PY" -B "$M/scripts/align_r1_followup_kit.py" prepare \
  --output "$M/.align-r1-prepare.json" \
  --sensor-ruling "$M/docs/run_reports/2026-11-13-rl145/sensor_ruling_rl145.json" \
  --smoke-table "$M/docs/run_reports/2026-11-13-rl145/smoke_part_b.rl145.json"
PKT_SHA=$(shasum -a 256 "$M/.align-r1-prepare.json" | cut -c1-64)
# At P this CLI does not print a digest; shasum records the required value.
print -r -- "D-7 PKT_SHA $PKT_SHA $(date '+%Y-%m-%d %H:%M:%S %Z')"
# Select only once review/notice are ready. T0 must be a whole minute,
# >= now+900 s, and leave the actual clean-close floor and install budget.
export T0="${T0:?LEAD FILLS: final whole-minute epoch}"
"$PY" -B "$M/scripts/arm_align_r1.py" size --t0 "$T0"
"$PY" -B "$M/scripts/arm_align_r1.py" prepare --measurement-root "$M" --custody-root "$S" --t0 "$T0"
df -g /Users/edr > "$S/df-arm.txt"
"$PY" -B "$M/scripts/arm_align_r1.py" render --custody-root "$S" --output "$S/rendered"
plutil -p "$S/rendered/com.joulewise.night.plist"
plutil -p "$S/rendered/com.joulewise.night.deadman.plist"
```

Read only the preparation arm/plan fields needed to verify: both checkout
heads P; packet SHA equal PKT_SHA; no packet-absent flag; no
`ac_powermode` key; one HAZARD_PACK/R1 chain, no W1 roster; bounds as
CHECKLIST B13; correct t0/paths/end. Default allocation is explicitly
unsized, retaining 20 GiB arm headroom and 10 GiB live floor. A sourced
R1-specific footprint estimate may be supplied with `--planned-bytes`;
Block 5's unrelated estimate is not substituted. Installer cutoff is
t0−180−120 s; allow 180 s to install before that cutoff. Move t0 and
repeat the ordinary route when review/notice/install cannot fit.

**Notice (ordinary authorized route, lead/magistrate sends; this draft
sends nothing).** Fill actual times from the fresh arm record:

> ALIGN v4 R1 slot-producing hardware session is arming on Mac15,9,
> after R0 and counted Part C passed. Measurement checkout/head:
> LEAD FILLS; custody: LEAD FILLS. t0: LEAD FILLS Pacific / UTC.
> Expected: LEAD FILLS (currently UNKNOWN); ceiling 119880 s after t0,
> plus 300 s shutdown grace; latest end LEAD FILLS. It normally ends
> when R1 completes. No agents remain at t0. Keep AC connected, battery
> not charging, external SSD unplugged and display asleep; do not touch,
> wake, start agents or other work until latest end. Security Responses
> stay automatic. Scheduled load may redo/refuse the session under its
> existing caps; lead has received any required scheduling notification.
> R1 owns High Power transitions and restores Automatic. KM003C and
> calibration bookends are diagnostic; R1 uses GPU energy. Allocation
> is unsized unless a sourced R1 estimate is supplied. I will report
> terminal status and actual restore afterwards. Existing NO/veto
> interval and route: LEAD FILLS.

**Run.** Immediately re-read issue validity, all host/close/copy/stop and
veto facts; no new lower-priority arm since READY. Only after these and
the notice hold, install, observe both jobs, sleep display, exit:

```zsh
set -euo pipefail
"$PY" -B "$M/scripts/arm_align_r1.py" install --custody-root "$S"
launchctl print "gui/$(id -u)/com.joulewise.night"
launchctl print "gui/$(id -u)/com.joulewise.night.deadman"
pmset displaysleepnow
```

No Git operation in M from install through t0, including status/fetch;
no agent, live driver probe, manual High Power selection, build, test,
analysis, offload or transfer during the armed interval. The existing
LaunchAgent, shared fence, deadman and file-only courier own execution.

**Dispositions (issue unchanged from current rulings).** Thermometry
must be `ok`; any other result comes to research lead. Any H in a gated
D run is a defect. Duty own-stop exception needs all four RL-156 §1
conditions and at least one valid three-turn run in the set. Extra keys
in TV0h's alias group are reported; they do not fail the named pair.
Planning 3(a) remains, TV1h is the heater key; S6 is registered G1 median,
not a hold median. Own-session typical-case fit is evaluated after R1.
No 1(f) receipt/key is permitted. Repeated sustained load/gappy evidence
uses existing refusal/redo rules; no change inside the driver.

**Check after fence gone (separate lead/magistrate activation).** Read
R1 terminal and chain exit first under the registered result boundary;
shared `result.json` GO does not establish R1 success. Record exact
host restore and absence of meter/hazard/root sampler/process group,
not merely power mode. Check three A–B–A sensors-only G0 releases;
if accepted step-30b was a redo, flag R_op to research lead before any
R_op-gated number is used. Preserve complete rejects, bookends, terminal
and recovery markers. Uninstall through `arm_align_r1.py uninstall`.
**LEAD FILLS at issue: exact network-time restore and before-next-arm
OFF/zero sequence (Q6); no worker decides it here.** Lead alone applies
the R1-to-W1 chain and any raw-result/slot reads; this preparation worker
has not opened them. W1 remains unarmed pending its own gates.
