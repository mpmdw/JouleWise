# RL-37 — meter outage records a fault and collection continues

Date: 2026-11-10 (PST). Seat: local Sol, `meter-outage-rl37`.
Branch: `align/2026-11-10-meter-outage-rl37`; base: `d865d76a3`.
Status: LOCAL_ONLY — targeted validation passed; no push or merge.
Commit: one local commit, `fix(align): continue collection through meter outages (RL-37)`;
its SHA is provided in the final handoff (this report is part of that commit).

## Authority and intake

Read RL-37 verbatim from local Git ref `origin/audit/2026-11-10-fable`,
`docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md`.
The ref resolved to `24b549f25ace51f1cf7059f913503930419db316`;
the document SHA-256 was
`729fd983d126e8e7b01732507ef43222635e7ab609dac8691b1e030ab9ff4ac1`.
Also read the owning protocol's meter clauses, AGENTS/CLAUDE conventions,
Mission M0, the orchestration rules and targeted D-009/D-023/D-170 entries.
The generated intake had no active stop card or global gate. This bounded
AGENT implementation ran under the explicit user brief, ahead of unrelated
queue work. The branch already existed at the requested base and was clean.

The user's coordination-state prohibition overrides the normal end-of-work
bookkeeping: no RUN_STATE, TASK_QUEUE, state kernel or test_gen_state edits,
and no task registration. This report is the handoff. No delegation or
external consult was used. This is a correctness fix, not a throughput change.

## Changes and bound-file census

Every changed **bound file** (all STRICT in the current registration):

1. `joulewise/b5/driver.py`: latch the first meter outage, emit exactly one
   `meter.supervision_fault` with `event: liveness_outage`, and continue the
   supervision pass and chain. The existing terminal fault-reason path adds
   `meter_liveness_outage`, making result/courier `fault: true`. The supervisor,
   t0 probe, first-batch readiness and battery/contention stop are unchanged.
2. `docs/align/v4/DEVIATIONS.md`: one `METER-T0-PROBE` row citing RL-37.
3. `docs/align/v4/dynamic_closure_trace.json`: regenerated through the registered
   generator, first to scratch, then moved into place after success.

Other changed files:

- `tests/test_w1_reliability_r2.py`: replace the obsolete meter-stop assertion
  with an elapsed-clock witness at 590/600/610/1200 s. Check chain completion,
  one flag, terminal and courier faults, and no refusal. Add battery-only and
  contention-only outage witnesses while the meter is also down.
- `tests/align/test_km003c.py`: witness supervisor restart gap endpoints,
  authenticated desk rejection of a member spanning two streams, preserved
  DC for a later covered member, and parity of arm/desk alignment and offset
  rejection for a restarted stream. Strengthen the existing no-splice test.
- This run report.

## Existing restart/coverage checks, located and exercised

`MonitorSupervisor.poll/start` records each observed process gap with
`down_from` and `up_at` paired-clock stamps, journals the restart in
`night/meter_supervision.jsonl`, and includes `gaps` in
`night/hazard_result.json` under `meter`. These are observed process lifecycle
endpoints; they do not assert the exact last/first valid sample times.

At the desk, `joulewise/align/apple/km003c.py:session_report` authenticates and
parses **each** listed stream. `capture_member` requires one stream to cover
the entire member and baseline. Streams are never concatenated for an
integral; an overlapping member gets `meter.member_uncovered` and no DC
integral, while rail admission is unchanged.

The arm/t0 `_probe_meter_live` and desk `capture_member` both use
`joulewise/external/km003c_parse.py:parse` for clock alignment and
`raw_offset_ns` for the start/end RAW-minus-monotonic offset comparison
(1 ms tolerance). This check is repeated for every restarted stream at the
desk, before its DC is used. The desk additionally checks sample drops,
protocol errors and fit residuals. It deliberately calls
`raw_offset_ns(..., allow_unclosed=True)` for the registered crash salvage:
an unclosed stream can retain covered members with `meter.stream_unclosed`;
its missing closing offset cannot be checked. No new in-window gate was added.

## Validation

All tests use repository synthetic fixtures, fake host probes and temporary
local Git remotes. No measurement data, model weights, native meter or
network access was used. Sealed study data and the separate blinded job were
not accessed. No native acquisition or host-setting command was run.

Failing first, before the production edit:

- `python3.13 -B -m unittest tests.test_w1_reliability_r2.MeterGateTests`:
  **expected FAIL**, 4 tests / 2.933 s, 3 failures. Meter silence returned
  EXIT_ABORTED instead of EXIT_GO, and the early meter return prevented the
  battery/contention outage flags from being reached.

After the production edit:

- Same focused command: **PASS**, 4 tests / 2.944 s.
- `python3.13 -B -m unittest tests.test_w1_reliability_r2`:
  **PASS**, 19 tests / 6.773 s.
- `python3.13 -B -m unittest tests.align.test_km003c`:
  **PASS**, 25 tests / 2.569 s (before the final covered-after-restart assertion;
  final replay below).
- `python3.13 -B scripts/align_v4_dynamic_trace.py --out /private/tmp/meter-outage-rl37-dynamic-trace.json`:
  **PASS**, exit 0, 418 reported tests across nine successful scenarios,
  186 executed paths, `not_bound: []`, `not_strict: []`. The tracer does not
  report skip counts. The desk scenario increased from 44 to 46 tests; this
  is the only trace diff. The verified scratch file was moved into place.
  `Path.replace` first refused the cross-device rename; `mv` completed the
  move with an owner/group-preservation warning. The installed JSON was
  subsequently parsed, diff-reviewed and checked by both closure modules.
- `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.align.test_v4_executed_closure`:
  **PASS**, 4 tests / 2.381 s.
- `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.align.test_v4_dynamic_closure`:
  **PASS**, 10 tests / 9.479 s, including its fresh-process execution check.
- `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.align.test_km003c`:
  **PASS**, final replay, 25 tests / 2.628 s.
- `JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.test_b5_driver_p3.MeterWindowTests.test_a_crashed_meter_is_restarted_into_a_new_stream`:
  **PASS**, 1 test / 4.254 s (real synthetic child processes; process-group
  census remains the harness's injected seam).
- AST parse of all three changed Python files: **PASS**.
- Compared the hazard-monitor stop block, t0 meter probe block and whole
  `MonitorSupervisor` class to the base: each is **byte-for-byte unchanged**.
  Checked that the deviation ID appears in exactly one table row.
- `git diff --check`: **PASS**.
- `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans`:
  **UNAVAILABLE**, exit 2,
  `PermissionError: [Errno 1] Operation not permitted: 'ps'`.
  No process was signalled by this observational check; a clean census is
  not claimed. Native census verification remains with the lead.

Full suite intentionally not run: the user requires targeted modules only
while a separate blinded job is active. Test modules are run sequentially.
Only one trace regeneration was needed; total test time stayed below the
approximately 20-minute limit.

The failing-first gate caught the unwanted chain abort and the skipped hazard
check during meter silence. Restart/desk witnesses exercise existing correct
behavior; no restart/parser/desk production change was needed. Closure checks
found no new binding defect. Final source comparison confirmed the preserved
stop/probe/restart paths. No mechanism-pruning recommendation is supported by
this one bounded run.

## Remaining lead gates and uncertainty

These are synthetic code witnesses, not live hardware qualification. Native
RL-37 check 7(a) must independently show arm and t0 refusal with zero capture;
7(b) must show a killed reader restarting, recorded gap/desk missing DC,
and a >600 s outage with the delivered fault and Air alarm while the real
chain reaches its end. The existing native hazard-monitor stop also remains
a lead gate. Check 7(c), real USB re-enumeration, stays deferred to Ed's next
visit; any USB-error exit must be structurally reported before post-restart
DC is used. No new MLX code/tests were introduced or native MLX run here.

Next exact step: lead delta review of the changed STRICT files, then W1
STRICT re-registration before PREQUAL and the smoke, followed by the native
checks above. No scientific-policy question was re-decided in this seat.
