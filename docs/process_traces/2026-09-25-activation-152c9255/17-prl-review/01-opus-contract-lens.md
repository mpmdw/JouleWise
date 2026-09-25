# PR-L contract lens (Opus 5.5): `feat/2026-09-25-acc-launch-context` @ 26c52306 vs c034a56f

**Verdict: FIX-FIRST.** There is one blocker: the new R16 refusal code was never registered in the arm-retry table, and a test that PR-L's seats never ran now fails. R1, R2, R3, R6 and R16 otherwise match the ruling texts closely. The pinned estimator files are unchanged, and nothing about the magistrate plist changes.

## Checks that pass
- **Pinned files:** `git diff --quiet c034a56f HEAD -- joulewise/powermetrics_fiducial.py joulewise/reduce.py joulewise/adapters/powermetrics.py joulewise/uncertainty_evidence.py` returns rc 0. All four are byte-identical.
- **R1:** `<key>ProcessType</key><string>Interactive</string>` is added to exactly the two templates. No `com.joulewise.magistrate` file is in the diff.
- **R2:**
  - The installer parses every rendered payload with `plistlib.loads` and refuses unless `ProcessType == "Interactive"` (missing key included). This happens in `Prepared.render` (Refused 3), `render_probe` (Refused 2) and `Prepared.launch_context` (Refused 2), at `joulewise/night_agent_install.py:577-594, 655-657, 1041-1042`.
  - The three-way equality check is at `:591-592`.
  - `validate_install` calls `launch_context()` (`:1213`).
  - The transaction checks, per label, that the digest it publishes equals the authenticated context (`:490-494`).
  - The context (ProcessType and rendered sha256 per label) goes into the installer's `validated pins` stdout, which `evidence_night.installer_call` records. It also goes into the probe receipt (`:1146-1152`).
  - Tests cover each of the three labels with missing key, `Background`, `Standard`, `Adaptive` and `Interactive` (`tests/test_night_agent_install.py` `RenderedProcessTypeTests`).
- **R3:** `tests/test_launch_context_no_qos_override.py` scans exactly `scripts/run_night.py` and `joulewise/adapters/powermetrics.py`.
- **R6:**
  - Production code is reused, not re-implemented: `_idle_count`, `_capture_timeout_s` and `_command` come from `PowermetricsTelemetryAdapter`, with the default `sudo -n` and `/usr/bin/powermetrics`. The bench argv matches production byte for byte, and the test pins 300 frames and a 55 s bound.
  - Pass rule (`scripts/run_night.py:3739-3741`): 300 frames, elapsed ≤ bound, median ≤ 150 ms and max ≤ 200 ms. Comparisons are `<=`, exactly as ruled.
  - The receipt schema is `joulewise.night_probe_receipt.v2`.
  - `validate_probe_receipt` requires `median_ms`, `p95_ms`, `max_ms`, `count == 300`, `elapsed_s` ≤ 55, `bound_s == 55`, `passed`, a `launch_context` for all three labels, and top-level `ProcessType`.
  - On failure, the refusal text carries all three numbers: the worker writes `detail` (`:3879-3882`) and the installer reports it (`:846-847`).
  - The census adds a `powermetrics.*night-probe-` pgrep and `-g powermetrics_pgid`.
  - The run is under the probe label, and bench records 26–27 cover both regimes.
- **R16:**
  - The cutoff is `authored_epoch_s >= 1790340000`, which is 2026-09-25 05:40 PDT, as ruled.
  - The check resolves both paths, then uses `relative_to` and requires the result to differ from `.`. So the custody root itself is refused, a sibling prefix such as `measurement-evil` is refused (ValueError), a symlink escape is refused, and `..` components are refused.
  - It runs before any measurement-clone probe, and tests cover all of these cases.
  - The exemption for older plans expires on its own: `PLAN_MAX_AGE_S` = 36 h, so no pre-cutoff plan passes the age check after 2026-09-26 17:40 PDT.

## BLOCKER

**B1. The new reason code is not registered in the arm-retry table; `tests.test_arm_retry` fails.**
- `joulewise/night_gate.py:214` adds `measurement_root_outside_custody` to `NIGHT_GATE_REASON_CODES`. `joulewise/arm_retry.py:34` (`COLD_GATE_CODES`) has no entry for it.
- In clone `/tmp/152c9255/prl-lens-opus` at 26c52306, `tests.test_arm_retry.ArmRetryTests.test_every_cold_assignment_is_explicit` FAILS. The same test is OK at c034a56f.
- Neither seat ran `test_arm_retry`: seat 13 ran V1–V7, seat 19 ran five modules.
- There is also a runtime cost: the arm/retry classifier has no disposition for this refusal.
- **Fix:** add to `COLD_GATE_CODES` in `joulewise/arm_retry.py`:
  `"measurement_root_outside_custody": "A plan authored at/after 1790340000 whose resolved measurement_root is not strictly inside /Users/edr/night-custody/measurement (acceptance ruling v2.1 R16). Re-author the plan; never a retry cause.",`
- Add the matching row to the reason table in `docs/process/NIGHT_HANDBACK.md` (near `:92`, which lists `night_plan_stale`). Then run `tests.test_arm_retry`.

## SHOULD-FIX

**S1. R16 makes new T0-rehearsal pack plans impossible to satisfy (a behaviour change for other plans).**
- `evaluate_night` runs `_check_static_start` first, and R16 there requires the measurement root to be inside `/Users/edr/night-custody/measurement`.
- For `T0_REHEARSAL` plans, `_pack_rehearsal_roots` (`joulewise/night_gate.py:1105-1154`, called at `:1186`) requires `measurement_root` to be outside `~/night-custody`. For that field, the `night_custody_parent` rule falls through to `_contains(...)` and raises `rehearsal_roots_not_disjoint: measurement_root`.
- So every rehearsal plan authored after the cutoff is refused, whichever root it uses. The ruling says "any newly authored plan", and its M3 intent was the calibration and evidence clones. This is from reading the code only; no fixture exercises it, because the `test_night_gate` plans use `authored_epoch_s=900`.
- **Fix (needs a magistrate ruling):** either exempt `pack_night` plans whose purpose is `T0_REHEARSAL`, or record that T0 rehearsals are retired. Add a both-direction test.

**S2. The install step does not check the probe receipt's launch context against the install's own.**
- `validate_install:1285` discards the result of `validate_probe_receipt` and only checks the receipt's digests are well-formed 64-hex strings.
- So the digests recorded in the receipt never have to match the plists actually installed. Registration Revision 5(a) will seal "rendered-plist digests", so one authenticated source is needed.
- **Fix:** `receipt = validate_probe_receipt(...)`, then refuse (`Refused(2, "probe receipt launch_context differs from install")`) unless `receipt["launch_context"][L] == prepared.launch_context()[L]` for L in `LABELS`.
- Leave the probe label out of the comparison: its bytes depend on `--probe-timeout-s`, which may differ between the probe run and the install.

**S3. On timeout, SIGKILL on sudo can leave the root-owned `powermetrics` running (from reading the code; I did not run it, since sudo is barred for this lens).**
- `_probe_cadence` (`scripts/run_night.py:3746-3756`) and the supervisor (`:3624-3630`) send SIGKILL to sudo's group.
- sudo cannot relay SIGKILL, and a user process cannot signal the root `powermetrics`. The orphan keeps running until it finishes its 300 frames (about 20 s more at 248 ms frames).
- The result is fail-closed but mislabelled: `probe_process_survived` instead of a cadence timeout. Also, the `except ProcessLookupError` at `:3749` does not catch `PermissionError`; if that is raised it escapes the TimeoutExpired handler and becomes `probe_receipt_invalid`.
- **Fix:**
  1. Send `SIGTERM` to the group first (sudo relays it to the command).
  2. Poll up to 2 s for the group to be gone, then `SIGKILL`.
  3. Catch `(ProcessLookupError, PermissionError)`.
  4. On timeout, write `detail` with `elapsed_s` and `bound_s`.

## NIT

- **N1. First frame kept, unlike record 01.** `_probe_cadence` keeps all 300 frames including the first. Record 01 (`2026-09-24-interactive-4b/01-…:12`) drops the first sample.
  - Keeping it is defensible and conservative: production's 55 s bound counts every frame. Record 00 item 26 found the first frame (158 ms) is not an outlier, and the passing smoke's max of 132.8 ms includes it.
  - Say this in the `_probe_cadence` docstring, and tell PR-R so the R17 script states its own convention and the two are never compared blindly.
- **N2. `ProcessType` written as a literal.** `:1151` writes `"Interactive"`. Use `context[label]["ProcessType"]` so the value is derived, not asserted.
- **N3. The R3 regex misses argv forms.** It does not catch `"nice"`, `"/usr/bin/nice"` or `renice` as argv tokens. Add `|["'/](?:re)?nice["']` and `\brenice\b`.
- **N4. Hardcoded thresholds in the validator.** `validate_probe_receipt` hardcodes 300, 55, 150 and 200, and does not check `cadence.argv` or that p95 ≤ max. Name module constants and cite R6 once.
- **N5. `_probe_cadence` restates adapter defaults.** It passes `executable="/usr/bin/powermetrics"` and `privilege_prefix=("sudo","-n")` explicitly. Use the adapter defaults (`POWER_METRICS`) so they cannot drift.
- **N6. New refusal strings are unregistered.** `ProcessType must be exactly Interactive`, `probe cadence …` and `rendered plist changed during publication` are not in `arm_retry.INSTALLER_REFUSALS`.
  - Register them: ProcessType is never an auto-retry. A cadence failure counts toward R12's "fails twice".
- **N7. Sudo precondition recorded by execution, not listing.** R6 asks that `sudo -n -l` shows a matching rule. The record (00:45) shows rc 0 from the real argv instead. That is equivalent evidence, but paste the literal `sudo -n -l` line into the PR body to match the ruling text.
- **N8. pgid reuse risk.** `killpg` on a stored pgid after the group has exited could hit a reused pgid. Same pattern as the existing `chain_pgid` handling; low risk.

## Behaviour changes for other labels
- **Evidence nights** share the night template, so they now run Interactive, as R1 intends.
- Their probe receipts gain `launch_context` and `ProcessType` (added by the installer). `evidence_night` records the receipt's sha256, so the digest changes. No validator rejects the extra keys.
- Evidence probes do **not** run the cadence phase, which is consistent with R6 scoping it to the calibration `_probe_worker`.
- `--render-only` now refuses a template that is not Interactive.
- The magistrate plist is not touched.

## Tests run
All runs were in clone `/tmp/152c9255/prl-lens-opus`; no sudo, launchctl or real powermetrics.
- `test_night_kinds`, `test_quiet_admission`, `test_launch_window`, `test_arm_retry`, `test_gen_derivation_night`, `test_night_plan_writer` and `test_rehearse_t0_unattended` together: 161 tests, **1 failure (B1)**.
- B1's test passes at c034a56f.
