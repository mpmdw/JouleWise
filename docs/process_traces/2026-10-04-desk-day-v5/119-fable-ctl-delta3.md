FINAL PASS: PASS

Cold, delta-limited final pass on `868c1a44` (PR #482) against the previous
ruled head `ea6e93a8` (`git diff ea6e93a8..868c1a44`, five files). Reviewer:
Fable 5.1, one foreground session, no subagents, checkout left clean
(`git status --short` empty at the end). Scratch and logs: `/tmp/dd5-fable-ct5/`.

One sentence: the battery reading no longer touches anything the measurement
path uses, a real powermetrics member cannot skip it silently, and no battery
byte reaches a public pack. No blocker, no high or medium finding. Five
low/informational notes follow the four answers.

Terms used below:
- "battery reading": one run of `/usr/sbin/ioreg -r -c AppleSmartBattery`,
  made once before the idle baseline ("pre") and once after the idle drift
  sentinel ("post") of each run ("member"). Its stdout is saved as
  `raw/battery_float.{pre,post}.ioreg`; a parsed record goes to
  `metadata.json` under `battery_float`.
- "measurement clock": the `Clock` object passed to `run_benchmark`; every
  measured stamp and event timestamp comes from it.
- "battery clock": a second, separate `Clock` introduced by this delta
  (`joulewise/controller.py:1156-1159`); a fresh `SystemClock` unless a test
  injects one.
- "span": the pair of monotonic-clock stamps written on the
  `stage_started idle_baseline` and `stage_completed idle_drift_sentinel`
  events. The reader (`battery_float.authenticate_bundle`,
  `joulewise/battery_float.py:1049-1089`) requires the pre reading to end
  before the span starts and the post reading to start after it ends.
- "mock backend": a config whose `hardware_target.telemetry_backend` is
  `mock` (simulated samples, no hardware).
- "public pack": the output of `publication_privacy.transform_public_bundle`,
  which first audits every file and every metadata key of the private bundle
  and refuses anything it has no rule for.

## What changed in the delta

1. `controller.py:1127-1154`: the battery reading takes its wall time and
   monotonic stamps from the battery clock, runs ioreg through
   `battery_float.run_bundle_probe` (a process factory captured at import,
   `battery_float.py:27, 307-326`) unless a battery runner is injected, and
   any exception is recorded under `battery_float.not_observed` instead of
   failing the member (`controller.py:1164-1169`).
2. `controller.py:2690-2709`: the two span stamps also come from the battery
   clock; a failure writes `monotonic_ns: null` and a `not_observed` entry.
3. Battery log lines are appended without a timestamp
   (`controller.py:1154, 1169, 1177`), because the log's timestamp helper
   (`_log`, `:2711`) reads the measurement clock.
4. `publication_privacy.py:134-136, 275-278, 929-930, 1127`: the
   `battery_float` metadata key and the two raw file paths get rules.

## What I ran

- `tests/test_controller_battery_float.py`: 13 passed (12 s).
  `tests/test_publication_privacy.py` + `tests/test_package_bundle_pack.py`:
  27 passed, 15 subtests passed (4 s).
- `probe.py` (log `probe.log`): my own construction, different from the
  in-tree test. The measurement clock records a violation if `now`, `stamp`
  or `sleep` is called while any of the four battery functions
  (`_observe_battery_float`, `_battery_span_metadata`,
  `_salvage_battery_float_post`, `_record_battery_observation_failure`) is on
  the stack; `subprocess.run` and `subprocess.Popen` do the same. Nine
  members through the real controller with the test file's stub adapters:

  | case | member status | violations | `battery_float` in metadata | reader verdict |
  |---|---|---|---|---|
  | normal | succeeded | 0 | pre + post records | `pass` |
  | runner raises | succeeded | 0 | two `probe_error` records | evidence missing |
  | battery clock raises on every read | succeeded | 0 | pre/post null + 4 `not_observed` reasons | evidence missing |
  | battery clock raises at the span start only | succeeded | 0 | records + 1 `not_observed` | evidence missing (span unavailable) |
  | workload fails | failed | 0 | records (post salvaged) | evidence missing (span unavailable) |
  | sampler stop fails | failed | 0 | post null + `not_observed.post` | evidence missing |
  | raw write fails | succeeded | 0 | records flipped to `probe_error` | raises `CustodyFailure` |
  | adapter without sentinel protocol | succeeded | 0 | records | `pass` |
  | mock backend | succeeded | 0 | `{pre: null, post: null, not_applicable: "mock"}` | evidence missing |

  Same script: `run_bundle_probe` refuses any argv other than the registered
  one; with a `/bin/sleep 30` child standing in for a hung ioreg and the
  timeout patched to 0.5 s, the call returned in 0.50 s, the child was killed
  and reaped (return code -9), and the record says `timed_out`, not passed.
- `probe2.py` (log `probe2.log`): publication. The battery metadata, the
  events file and the raw pair written by the controller (fixture ioreg
  output containing `"Serial" = "F5DH62008FG00000EA"`; error text carrying a
  planted secret) were placed on a publishable bundle from the pack test's
  own builder and passed through `transform_public_bundle`. Results in
  question 3.
- NOT run: the whole suite (the lead reports 369 passed on the previously
  failing files at this head; I did not repeat that), a real powermetrics
  member, real ioreg. No powermetrics, sudo, launchctl or model.

## Question 1 — can the battery reading still delay, reorder or alter a measured phase, a stamp or the sampler, or consume anything the measurement path uses?

No.

- Consumption: zero measurement-clock reads and zero uses of the shared
  `subprocess.run`/`subprocess.Popen` attributes from battery code on all
  nine paths above, including the error and salvage paths. The in-tree
  counterfactual (`tests/test_controller_battery_float.py:217-253`) agrees
  from the other direction: the measurement clock's read sequence and every
  event timestamp are identical with the battery code removed and present.
- Placement is unchanged from the ruled rounds: pre after `prepare` and
  before `idle_baseline` (`controller.py:1114`), post after
  `idle_drift_sentinel` and before `cleanup` (`:1119`). The stub adapter's
  liveness assertion (no reading while a sampler is live) held in every case.
- Delay: bounded as before, about 10 s per reading
  (`PROBE_TIMEOUT_S = 10`, `battery_float.py:32, 318`), spent only in the two
  unsampled gaps. The first battery stamp also builds the `SystemClock`
  (three cheap clock calls), in the gap before the idle baseline.
- Alteration: the new `except Exception` (`controller.py:1144`) encloses only
  the battery clock read, the keyword dictionary and `observe`; no
  measurement-path call is inside it, and `KeyboardInterrupt`/`SystemExit`
  still propagate to the interrupt handler.
- The span keeps its physical meaning in production: the command line builds
  a `SystemClock` for any non-mock run (`joulewise/cli.py:261`) and the
  battery clock is another `SystemClock`, so the reading stamps and the span
  stamps are all `time.monotonic()` taken in program order. The reader
  compares battery stamps only with span stamps, both from the battery clock.

## Question 2 — is "skipped for mock backends" decided by something a real measurement cannot trigger?

Yes. The skip tests `config.hardware_target.telemetry_backend == MOCK`
(`controller.py:1128`), the same field the default adapter registry uses to
choose the telemetry adapter (`joulewise/adapters/__init__.py:157-169`): the
real powermetrics adapter is built only when that field is `powermetrics`, in
which case the skip cannot fire. The three other sites that depend on the
backend (`:2394`, `:2694`, `:2699`) read the same field.

The skip is recorded, not silent: `not_applicable: "mock"` in metadata
(`:2394-2395`), and the reader returns evidence missing for it, never `pass`.
For a non-mock member, every way of not obtaining a reading leaves a named
trace: `not_observed.<phase>` with the exception text, `not_reached: <stage>`,
or a `probe_error` record. This condition predates round 4; the delta adds
only the test that a mock member never touches the battery clock.

One limit, by reading: a caller that passes its own registry could pair a
`mock` config with a real adapter. No code under `joulewise/` or `scripts/`
does; the tests do the opposite (a `powermetrics` config with stub adapters).

## Question 3 — is the privacy classification honest; can raw ioreg bytes reach a public pack?

Honest, and no.

- The two raw files are omitted: `_RAW_PATHS` (`publication_privacy.py:272-288`)
  maps them to operation `omit`; the public tree in my probe held exactly
  `config.json, events.jsonl, metadata.json, power_trace.csv,
  summary_metrics.json`.
- `metadata.battery_float` is replaced whole by
  `{"redacted": true, "classification": "omit_backend_native_or_rich_telemetry"}`
  (`:929-930`), so future keys inside it are covered too, and
  `verify_public_bundle` (`:1126-1129`) rejects an unredacted subtree.
- Byte search of every public file for the serial, the planted secret,
  `ioreg`, `AppleSmartBattery`, `InstantAmperage`, `BatteryData`,
  `property_lines`, `not_observed`, `monotonic_ns`, `stderr`: zero hits in
  all four cases (mock as written, normal, runner error with the secret in
  its text, battery clock failure with the secret in its text). The span
  stamps do not leak either, because all event metadata is redacted
  (`:953-960`). `logs/controller.log`, where the new untimestamped lines go,
  is omitted (`:295, 396-397`).
- What the transformation manifest keeps for each raw file: its path name,
  SHA-256 and size. The file changes on every reading (current, update time),
  so the digest is not a stable device identifier.
- Fail-closed controls: `raw/battery_float.t0.ioreg`,
  `raw/battery_float.pre.ioreg.bak` and
  `instrument_calibration/raw/battery_float.pre.ioreg` have no rule, so a
  bundle containing any of them is refused whole (`:821-823`).

## Question 4 — anything else in the delta

Nothing that holds the merge. Notes below.

## Findings

**L1 (low, tests) — unit tests of non-mock members still run the real ioreg,
and can no longer be stopped by patching `subprocess`.**
`joulewise/battery_float.py:27, 316`; `joulewise/controller.py:1134-1135`.
With no injected runner the controller calls `run_bundle_probe`, which holds
the original `Popen` on purpose. No `conftest.py` replaces it (grep). On the
measurement Mac each such test member makes two real ioreg reads; on a
machine without ioreg they record `probe_error`. Members pass either way.
This is round-1 L4, still open and now harder to stub by accident. Cure: one
suite-wide fixture that patches `battery_float._BatteryPopen`.

**L2 (low) — battery stamps live in the battery clock's time base.**
`controller.py:1156-1162, 2704-2709`. Equal to the measurement time base in
production (both `time.monotonic()`), and nothing compares the two (the only
reader of these fields is `authenticate_bundle`). A library caller that
injects a non-system measurement clock with a real backend would get battery
stamps that cannot be compared with the bundle's other stamps. The module
header (`controller.py:9-11`) says so. No action needed for the window.

**L3 (nit) — `not_observed` can go stale and mixes two kinds of key.**
`controller.py:1166, 1176, 1179`. Keys are both reading names (`pre`, `post`)
and stage names (`idle_baseline`, `idle_drift_sentinel`). If a post reading
fails in the normal path and a later stage then fails, the salvage step
retries it; on success the metadata holds a post record and a
`not_observed.post` reason together. Needs the battery clock to raise once
and then recover, which a `SystemClock` does not do. The reader ignores
`not_observed`, so no verdict changes.

**L4 (nit) — after a timeout the new runner drains pipes with no bound.**
`battery_float.py:319-322`: `kill()` then `communicate()` with no timeout,
where `subprocess.run` on this platform only waits for the child. A
grandchild holding the pipe open would hang it; ioreg starts none. In my
hung-child probe the call returned at the timeout.

**L5 (info) — scope and what I did not verify.**
- Battery log lines have no timestamp prefix. No code parses
  `controller.log` (grep: one path listing in `salvage_dangler.py:52`).
- Outside this delta, by reading: a member with an attached calibration
  carries a second copy of the raw ioreg pair under `instrument_calibration/`
  (`controller.py:372, 675-680`). Those paths have no publication rule, so
  such a bundle is refused whole — no leak, but real G2-a/G2-b members are not
  publishable through this route until those paths are classified.
- I did not publish a bundle produced end to end by a real powermetrics
  member; the stub-adapter bundle is refused for an unrelated reason
  (`telemetry_source` of the stub), which is why the publication probe places
  controller-written battery content on the pack test's bundle.
- I did not rerun the whole suite at this head.

## Verdict

Regression (2), battery code consuming injected clock or runner values:
closed — 0 uses on 9 paths, and the in-tree counterfactual passes.
Regression (1), unclassified `metadata.battery_float`: closed — subtree
redacted, raw pair omitted, 0 identifier bytes in the public tree. Mock skip:
decided by the field that selects the adapter, and recorded. Measured phases,
stamps and the sampler: untouched. Safe to merge.
