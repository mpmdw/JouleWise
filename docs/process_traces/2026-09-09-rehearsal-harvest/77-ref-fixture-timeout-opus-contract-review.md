# Refuter (Opus, CONTRACT lens) — PR #310 / FIXTURE-TIMEOUT-WALLCLOCK-01

Fresh, non-author, read-only refuter. Worked only in the detached worktree `/Users/edr/code/JouleWise-wt-ref-stub-astra`.
Canonical `/Users/edr/code/JouleWise` never touched. No edits except this file. No background tasks, no subagents.

## Head reviewed

`git rev-parse HEAD` → `112e86e4a0ca38cca6540f46aa42d93ffc6571b8` (matches the brief; `git status --porcelain` empty).
Diff under review: `21e31107..112e86e4`, three test-side files, `239 insertions(+), 14 deletions(-)`.

## Lens

CONTRACT: does the change stay inside the ruled envelope (kernel goal, cold gate 44 C5, refuter 45's F2 fence); does it move
any production byte; does it preserve what the claim-bearing tests PROVE about production; is any assertion vacuous; is any
rule silently amended or any knob smuggled into production.

## Independent execution performed

1. `git rev-parse HEAD` → `112e86e4a0ca38cca6540f46aa42d93ffc6571b8`.

2. **Production-byte check.** `git diff --stat 21e31107..112e86e4 -- joulewise scripts` → **empty**.
   `git diff --name-only 21e31107..112e86e4` → exactly `tests/fixtures/fake_powermetrics_process.py`,
   `tests/test_idle_admission.py`, `tests/test_run_campaign.py`. **Zero production bytes.**

3. **Mandated run.**
   `PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise JOULEWISE_BACKUP_ROOTS= python3 -m unittest tests.test_idle_admission.PowermetricsFixtureTimingTests`

   ```
   ..
   ----------------------------------------------------------------------
   Ran 2 tests in 3.466s

   OK
   ```

4. **Blast-radius probe (`/tmp/probe_nosleep_argv.py`)** — instrumented `_command` inside the real
   `produce_retry_powermetrics_bundle` run to record every capture and whether it received `--no-sleep`:

   ```
   === _command invocations (capture_file, count, got --no-sleep) ===
   ('joulewise-powermetrics-15_h_jpl.plist', None, False)
   ('joulewise-powermetrics-scgiwetv.plist', 100, True)
   bounded count: 1
   continuous count: 1
   ```

   This was an attempted refutation of the helper's comment ("Only the bounded sentinel is synthetic") on the ground that the
   predicate is `count is not None` rather than an artifact-name test, and `_run_bounded_capture` has a second production call
   site (`joulewise/adapters/powermetrics.py:291`, the pre-run idle admission capture). **Refuted:** in this producer the
   admission captures take the `_admission_sampling_handoff_pending` branch into `_capture_idle_slice`
   (`joulewise/adapters/powermetrics.py:284-288`), which reads frames from the live continuous stream and never calls
   `_command`. Exactly one capture — the count=100 post-idle sentinel — is unpaced. The comment is accurate as the code stands.

5. **Vacuity probe on the identity assertion (`/tmp/probe_identity_vacuity.py`)** — generated two `--no-sleep` sentinel
   captures differing *only* in native timestamps (via the existing `P2038_FAKE_POWERMETRICS_MODE=inconsistent` knob, which
   adds exactly `timedelta(seconds=60)` at `tests/fixtures/fake_powermetrics_process.py:112-113` and changes nothing else),
   then fed both to `measure_post_run_idle`:

   ```
   normal:  n=100 first_ts=1788972126.000 last_ts=1788972130.950 elapsed_ns=50000000
   plus60s: n=100 first_ts=1788972186.000 last_ts=1788972190.950 elapsed_ns=50000000
   result keys: ['idle_drift', 'idle_drift_bound_w', 'idle_drift_guard', 'post_idle_duration_requested_s']
   60-SECOND TIMESTAMP SHIFT CHANGES RESULT? False
   ```

6. **Seat-report base claim.** `git diff --stat 0656bb98..21e31107 -- joulewise scripts tests` → **empty**, confirming
   report 74's "This worktree's intervening changes are documentation-only".

7. **Knob reach.** `grep -rn FAKE_POWERMETRICS_SLEEP_SCALE` (excluding traces) → `tests/fixtures/fake_powermetrics_process.py:43`,
   `tests/test_run_campaign.py:9642,9645`, `tests/test_idle_admission.py:508,579`. `grep -rn 'no_sleep|"--no-sleep"' joulewise/
   scripts/ tests/` → hits only in the fixture and the two test files. **No production file reads either.**

## Answers to the six contract questions

**Q1 — Envelope. In-lane; no production byte.** The kernel goal names the permitted cures verbatim: `"cure = capture-timeout
margin sized against measured slack on the fixture side (fixture-aware timeout or a non-sleeping fixture), production timeout
unchanged"` (`docs/process/state_kernel.json`, `/tasks/FIXTURE-TIMEOUT-WALLCLOCK-01/goal`). The change takes the second branch —
a non-sleeping fixture for bounded captures only. Cold gate 44 C5 (`44-coldgate-ruling-replay-verdict.md:117-118`) authorised
exactly this: `"cure = fixture-aware timeout or a non-sleeping fixture"`. Production timeout is not merely unchanged but
positively pinned by the new `test_real_powermetrics_capture_timeout_is_unchanged`
(`tests/test_run_campaign.py:9667-9668`: `17.5` for n=100 and the `15.0` floor), which reads
`_capture_timeout_s` at `joulewise/adapters/powermetrics.py:1468-1470`. Probe 2 confirms the empty production diff.

Refuter 45's F2 fence — quoted in `41-rootcause-idle-admission-local-astra-report.md:87` and endorsed at
`44-coldgate-ruling-replay-verdict.md:211` as `"do not weaken strict equality or declare scientific neutrality before
identifying the divergent input"` — is **satisfied on both halves**. Strict equality is untouched: the helper still asserts
`self.assertIs(evaluation.strict_valid, expected_strict_valid, ...)` (`tests/test_run_campaign.py:9597-9601`); the only change
is a third argument supplying `validation_problems` and the drift evidence as a failure message. That is a diagnostic
addition, not a relaxation — no comparison, tolerance, or expected value moved. And the divergent input was identified before
the cure, not assumed away: seat report 74's V1 records
`"COUNTERFACTUAL artifact=powermetrics_idle_post.plist count=100 exception=TimeoutExpired timeout=17.5"` followed by
`"post_idle_unavailable"` and `FAILED (failures=1)`.

**Q2 — What the tests prove about production: net coverage is preserved and slightly increased.**

*Before.* The bounded sentinel was a real child process that slept `n × interval × slack` (100 × 50 ms, `tests/fixtures/
fake_powermetrics_process.py:74-80` pre-change), producing `elapsed_ns` from measured `time.monotonic()` deltas and native
dates from `datetime.now(UTC)` at write time, under the real `subprocess.run(..., timeout=17.5)` at
`joulewise/adapters/powermetrics.py:1201-1210`. So the four `IdleAdmissionCoreVerdictTests` incidentally exercised the real
deadline margin — 5.0 s nominal against 17.5 s — and would flip to `post_idle_unavailable` whenever machine slack exceeded
3.5×. That coupling is the defect, not a property worth keeping: it is a *wall-clock* coupling, and refuter 45's R2 already
characterised it as `"a knife-edge, not a state"`.

*After.* The sentinel is still a real child process, still spawned through the real `_command`, still run through the real
`subprocess.run` with the real `timeout=17.5`, still parsed by the real parser, still persisted through the real
`_persist_capture` / `_write_rich_artifact` path. Only the pacing and the timestamp source are synthetic: `elapsed_ns =
args.i * 1_000_000` (`:88-93`) and `native_start + (index+1)*interval_s` (`:106-110`).

*What became untested, and whether it is recovered.* Exactly one thing: the TimeoutExpired arm of `_run_bounded_capture` is no
longer reachable by accident. It is now covered **deliberately and better** by `test_real_capture_timeout_leaves_post_idle_
unavailable` (`tests/test_idle_admission.py:546-590`), which is a genuinely stronger test than the accident it replaces: it
asserts the production deadline is the real one before shortening it (`self.assertEqual(kwargs["timeout"], 17.5)`), it drives
a **real** `subprocess.TimeoutExpired` from a **real** sleeping child (`FAKE_POWERMETRICS_SLEEP_SCALE=1`, 5.0 s nominal
against a 0.75 s deadline) rather than fabricating the exception, it asserts the exact fail-closed value
`{"idle_drift": {"status": "unknown", "reason": "post_idle_unavailable"}}`, and it asserts the capture-registry cleanup
`adapter._pending_captures == {}` — which exercises the real `except BaseException: if context is None: self._release_capture(...)`
arm at `joulewise/adapters/powermetrics.py:1214-1217`. The old arrangement asserted none of these; it merely *sometimes* hit
the path and then failed the suite.

*Do the retry tests still guard what they are claim-bearing for?* Yes, and I verified the mechanism rather than taking the
seat's word. The strict validator re-derives idle drift at `joulewise/cli.py:1369-1400` from the persisted pre/post plists,
and it consumes **only** `[record.combined_power_w for record in pre_records/post_records]` plus
`idle_window_gpu_quality(decode_rich_telemetry(...))`; `idle_window_gpu_quality`
(`joulewise/adapters/powermetrics.py:1949-1979`) reads only `gpu.idle_ratio` and `gpu.freq_hz`. No timestamp from the sentinel
enters that comparison. The test pins the powers identical between paced and synthetic captures
(`tests/test_idle_admission.py:530-533`). Separately, the regression brackets the real controller sentinel stage and asserts
the measured cadence ratio and the `clock_anchor` are byte-identical across it (`tests/test_run_campaign.py:9633,9634-9636`) —
and those come from the **continuous** stream, which never receives `--no-sleep` (probe 4).

**Q3 — D-078 causal constraint: respected where it is enforced, and not bypassed.** The enforcement is
`derive_powermetrics_anchor_v2` (`joulewise/uncertainty_evidence.py:332-345`, docstring: *"the intersection over every record
… is intersected with the causal interval from the controller clock stamps"*), whose causal lower bound is
`causal_lower_s = pre_spawn.monotonic_before_s + offset_lower_s + records[0].elapsed_s`
(`joulewise/uncertainty_evidence.py:452-454`) — i.e. precisely the "record 0's window end follows the spawn by elapsed_ns"
relation the fixture docstring names. I traced every producer of its `records` argument: `joulewise/reduce.py:1782-1803`
(`raw_path = reader.path / "raw" / RAW_POWERMETRICS_NAME`), `joulewise/cli.py:1269-1294` (same `raw_path`),
`joulewise/environment_admission.py:326-355` (`bundle_path / "raw" / "powermetrics.plist"`), and
`joulewise/adapters/powermetrics.py:546,571,765` (the live continuous `native_records`). **Every one reads the continuous
capture. None reads the bounded sentinel.** `grep -rn RAW_IDLE_POST_NAME joulewise/` returns only the adapter, `cli.py`'s
strict re-derivation, `uncertainty_evidence.py:1417` (a literal string in the evidence dict), and
`publication_privacy.py:274` (an artifact allowlist) — no causal or window check among them.

So bounded sentinels are **not** subject to the D-078 causal check, and the change does not weaken it. The design also
protects the case that *is* checked: `--no-sleep` is refused for continuous captures at
`tests/fixtures/fake_powermetrics_process.py:40-41` (`parser.error("--no-sleep requires a bounded capture (-n)")`), and the
index-0 sleep that establishes the causal relation survives untouched for them (`:74-78`). This guard is the load-bearing part
of the cure and it is correctly placed in the fixture rather than the caller.

One residual worth recording (nit N1 below): under `--no-sleep` the emitted native window ends run *ahead* of real wall clock —
probe 5 shows a 4.95 s span emitted by a process that exits in milliseconds. That is unavoidable: an unpaced fixture cannot
simultaneously place record 0's window end after the spawn (D-078) and the last record's window end at process exit. The
implementation chose the direction that preserves the D-078 relation, which is the right choice; it is simply undocumented.

**Q4 — `self.assertEqual(results[0], results[1])` (`tests/test_idle_admission.py:544`) is TRUE but vacuous as a
timestamp-neutrality proof.** `measure_post_run_idle` returns exactly four keys
(`joulewise/adapters/powermetrics.py:1066-1073`): `idle_drift`, `idle_drift_guard`, `post_idle_duration_requested_s`,
`idle_drift_bound_w`. `idle_drift` comes from `derive_idle_drift_evidence`, whose entire signature is
`pre_power_w, post_power_w, pre_power_w_mean, pre_idle_window_suspect, post_idle_window_suspect, calibration_guard`
(`joulewise/uncertainty_evidence.py:1348-1355`) — **no timestamp argument**, and its emitted dict
(`:1413-1430`) carries counts, means, suspect flags, envelope and calibration fields only.
`post_idle_duration_requested_s` is derived from config and baseline at `joulewise/adapters/powermetrics.py:1029-1031`, not
from the capture. Therefore, once the line immediately above it has asserted the power sequences equal
(`tests/test_idle_admission.py:530-533`), the identity assertion cannot fail for any timestamp reason whatsoever.

Probe 5 demonstrates this directly: shifting every native timestamp by **60 seconds** leaves the returned dict bit-identical.
So no timestamp-derived field "could differ but is excluded" — there is no timestamp-derived field at all. The assertion is a
true statement about a function that structurally ignores what it is being offered as proof of. The *substantive* neutrality
claim does hold, but it is established by the artifact-consumer analysis in Q2/Q3, not by this line.

**Q5 — No rule change, no widened waiver, no production knob.** `FAKE_POWERMETRICS_SLEEP_SCALE` is read at exactly one place,
`tests/fixtures/fake_powermetrics_process.py:43`, defaulting to `"1"` (identity), and is referenced only by the two test files
(probe 7). `--no-sleep` appears only in the fixture's own parser and the two test call sites; production `_command`
(`joulewise/adapters/powermetrics.py:1472-1497`) cannot emit it, so a real `powermetrics` binary can never receive it. No
waiver text, gate row, or acceptance threshold is touched. The `assertIs` change adds a message and nothing else.

Seat-report over-statements: two, both minor, listed as S2 and N3.

**Q6 — run performed; tail pasted in "Independent execution performed" item 3 (`Ran 2 tests in 3.466s / OK`).**

## Blockers

None.

## Should-fix

**S1 — The regression's stress level is silently overridable by ambient environment, so the acceptance condition it encodes
is not guaranteed to be exercised.**

(a) `tests/test_run_campaign.py:9642`:
```python
scale = os.environ.get("FAKE_POWERMETRICS_SLEEP_SCALE", "3.5")
```
and `tests/test_run_campaign.py:9654-9655`:
```python
if float(scale) >= 3.5:
    self.assertEqual(drift["post_sample_count"], 100)
```

(b) Governing text: the kernel acceptance summary,
`docs/process/state_kernel.json` `/tasks/FIXTURE-TIMEOUT-WALLCLOCK-01/acceptance/summary` —
`"The four IdleAdmissionCoreVerdictTests pass under a simulated ≥3.5× timer slack without changing _capture_timeout_s;
defect-shaped regression names the observed trigger"`.

(c) As written, `FAKE_POWERMETRICS_SLEEP_SCALE=1 python3 -m unittest …test_retry_member_survives_fixture_sleep_slack` passes
while exercising 1× slack — the seat's own V3 run did exactly that and recorded `OK`. The test then also skips its only
scale-dependent assertion, so nothing records that the named condition went untested. A regression whose defect-shaped
condition can be turned off by an inherited environment variable is a recording obligation wearing a gate's clothes — the same
shape refuter 45 objected to in row 9. Proposed correction: pin the floor and drop the conditional —
`scale = str(max(3.5, float(os.environ.get("FAKE_POWERMETRICS_SLEEP_SCALE", "3.5"))))`, then assert
`self.assertEqual(drift["post_sample_count"], 100)` unconditionally (it is config-derived and is 100 at any scale, so the guard
buys nothing even today).

**S2 — Seat report 74 presents the identity assertion as production call-site proof; it cannot bear that weight.**

(a) `74-seat-fixture-timeout-wallclock-astra-report.md`, "Production call-site proof and assertions" table, Idle-drift row:
`"The pacing test asserts identical powers and self.assertEqual(results[0], results[1]) for paced versus synthetic
timestamps."`

(b) Governing text: refuter 45's F2 fence as endorsed at `44-coldgate-ruling-replay-verdict.md:211` —
`"do not weaken strict equality or declare scientific neutrality before identifying the divergent input"`. Neutrality of the
synthetic timestamps is exactly the "scientific neutrality" claim at issue, and it must be evidenced, not asserted.

(c) Per Q4 and probe 5, that assertion is entailed by the power-equality assertion on the preceding line and is insensitive to
a 60-second timestamp error. The claim is nonetheless **true**, and I verified it by a sound route the report does not give:
the strict validator re-derives idle drift from `combined_power_w` plus GPU idle-ratio/frequency only
(`joulewise/cli.py:1369-1400`, `joulewise/adapters/powermetrics.py:1949-1979`), and the D-078 anchor reads
`raw/powermetrics.plist` exclusively (`joulewise/reduce.py:1782-1803`, `joulewise/cli.py:1269-1294`,
`joulewise/environment_admission.py:326-355`). Proposed correction: replace that table row's justification with the
consumer-side citations above, and state the identity assertion for what it is — a cheap invariant, not the proof.

## Nits

**N1 — The fixture docstring does not disclose that synthetic window ends lead real wall clock.**
(a) `tests/fixtures/fake_powermetrics_process.py:7-10`: `"Bounded sentinel tests may opt into --no-sleep: elapsed_ns and
native dates then advance by the requested interval without waiting."`
(b) The paragraph immediately below it (`:66-68`, retained) explains the D-078 rationale for the index-0 sleep, so this file
already holds itself to explaining physical rationale.
(c) The sentence is true but omits the consequence: with `native_start` taken at spawn (`:69`) and record *i* stamped
`native_start + (i+1)·interval` (`:106-110`), the last of 100 records claims a window ending 5.0 s after a process that exits
in milliseconds (probe 5: 4.95 s span). Add one sentence recording that this direction is deliberate — it preserves the D-078
record-0 relation, which back-dating would violate — and that no consumer reads sentinel timestamps (naming the strict
re-derivation and the anchor's `raw/powermetrics.plist` source), so a future validator that *did* read them would need this
fixture revisited.

**N2 — The unpaced predicate is positional-argument-shaped, not artifact-shaped, and nothing pins the count.**
(a) `tests/test_run_campaign.py:9553-9556`:
```python
# Only the bounded sentinel is synthetic. The continuous stream
# still owns admission, measured cadence, and the clock bracket.
if kwargs.get("count") is not None:
```
(b) Same comment's own claim.
(c) Probe 4 confirms the comment is true **today** — one continuous, one bounded — but only because the admission captures
happen to take the `_capture_idle_slice` branch (`joulewise/adapters/powermetrics.py:284-288`). If that branch condition ever
changes, `powermetrics_idle.plist` would silently become unpaced too and no test would notice. Also, `kwargs.get("count")`
returns `None` if a future caller passes `count` positionally. Cheap correction: collect the unpaced invocations in the helper
and assert exactly one, or key on the `-o` artifact name.

**N3 — "exists only in fixture code" is inaccurate as written.**
(a) `74-seat-fixture-timeout-wallclock-astra-report.md`, "Change": `"FAKE_POWERMETRICS_SLEEP_SCALE exists only in fixture
code."`
(b) Probe 7.
(c) It is also read at `tests/test_run_campaign.py:9642` and set at `:9645`, `tests/test_idle_admission.py:508,579`. The
intended claim — that it reaches no production file — is true and is the one worth making. Say "is read only by the fixture
and its tests; no file under `joulewise/` or `scripts/` references it."

## Same-signature statement

No same-signature repeat. My one substantive refutation attempt (N2's premise, that the `count is not None` predicate silently
unpaces the pre-run admission captures as well) was **refuted by execution** (probe 4), and I have recorded it as a fragility
nit rather than a defect. The findings above are three distinct signatures — an environment-overridable regression threshold
(S1), an entailed assertion offered as independent proof (S2/Q4), and undocumented deliberate non-physicality (N1) — none of
which matches a defect class from the prior rounds in this lane (44/45 were about machine-state attribution and gate-row
wording). No blocker was downgraded; there was none to downgrade.

## Verdict

**findings** — no blockers; 2 should-fix (S1 env-overridable regression strength, S2 seat-report proof over-claim), 3 nits.
The cure is in-lane, changes zero production bytes, honours refuter 45's F2 fence on both halves, does not bypass the D-078
causal check (which never reads bounded sentinels), and nets *more* coverage of the production timeout path than it removes.
