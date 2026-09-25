# PR-L fix round 1: delta re-audit (Opus 5.5, contract + execution)

**Delta:** `26c52306..9500545f`. **Verdict: all nine dispositioned items are closed, with no new BLOCKER.** One SHOULD-FIX is a test gap: the magistrate's T0_REHEARSAL test was required to show both directions, and it doesn't show the second one end to end. Two NITs.

## How each item closed

| Item | Result | Evidence |
|---|---|---|
| **Opus B1** (reason code not registered) | CLOSED | `arm_retry.py:43` now has the entry, with the lens text verbatim. The `NIGHT_HANDBACK.md:93` row and the generated runbook row match. `tests.test_arm_retry` passes and `gen_state.py --check` returns rc 0. |
| **Opus S1** (T0_REHEARSAL exemption, provisional ruling) | CLOSED; narrow keying confirmed | See below. |
| **Opus S2 + Astra F1** (install must bind the probe receipt) | CLOSED | `night_agent_install.py:1285-1294`. See below. |
| **Opus S3** (SIGTERM before SIGKILL on timeout) | CLOSED; fails closed | See below. |
| **Astra F2** (keep partial frames; timing in refusal) | CLOSED | Complete frames are now parsed on the timeout and nonzero-exit paths, and `passed` stays false. The worker's refusal text (`run_night.py:3903-3908`) carries elapsed_s, bound_s, count, median, p95 and max. The installer shows it through `outcome is not ok: …: <detail>` (`:846`). There are new regressions for 220 frames and for exit 7. |
| **Astra F3** (case aliases of the custody root) | CLOSED | See below. |
| **Opus N1** (first frame kept) | CLOSED | The docstring states the convention. |
| **Opus N2** (ProcessType literal) | CLOSED | `:1151` now derives the value from `context[label]`. |

**S1: can a measurement plan use the exemption to escape R16? No.** The exemption applies only when all of these hold:
- `receipt_class == "TRANSACTION_PACK"` and `pack_night` is present;
- the authorization record's bytes match the sha256 bound in the plan;
- the record says `purpose == "T0_REHEARSAL"`.

A missing record, a mismatched digest or a JSON error all raise, and the exemption is not granted (`night_gate.py:1252-1260`).

Why a mislabelled measurement plan still cannot measure:
- Quiet-admission (v4) plans are packless only (`:1791`), so they can never reach the exemption.
- Every pack plan goes on to `_evaluate_pack_conditions`, where `_authenticate_pack_records` re-reads the same record under the same digest. So the purpose cannot change between the two reads.
- That second read also requires exact keys and `claim_eligible=False` for T0.
- `_pack_rehearsal_roots` then requires the rehearsal window-id prefix, disjointness from production custody, and the rehearsal clone prefix.

In short, a plan that labels itself a rehearsal becomes a non-claim rehearsal.

I checked this with real files and no mocks, in a `/tmp` clone with the tmp path resolved:
- Authentic T0 record: R16 is skipped, and the plan is refused further down (`night_probe_error` with the fake probes).
- T0 record with a tampered digest: `measurement_root_outside_custody`.
- Authentic CAMPAIGN_TRANSACTION record: `measurement_root_outside_custody`.

The citation comment is present as dictated. Note that `_pack_bytes` refuses symlinked record paths, so on macOS a `/var/folders` tmp path fails closed back into R16. That is correct.

**S2 + F1: are the right labels compared, and is a mutated digest refused? Yes.**
- `LABELS` is (night, dead-man), and the probe label is excluded as ruled.
- The whole entry is compared: ProcessType and digest.
- A receipt with no `launch_context` refuses.
- The tests mutate each label's digest, confirm a changed probe digest is tolerated, and edit the template after the receipt is written.
- Both the probe step (`launchd_probe`) and the install step render with the same inputs:
  - NIGHT_HANDBACK:1150/1153 passes the same `--python` to both runs.
  - `admit()` pins the plan path.

**S3: does timeout handling still fail closed? Yes, and a timeout is never reported as PASS.**
- `passed` requires `completed`, which is set only when the command exits with rc 0 inside `communicate()`. A timeout can never set it.
- Probe 1: a fake writes all 300 frames at 120 ms, then hangs and ignores SIGTERM. Result: `passed=False`, count 300, the SIGKILL fallback fires, wall time 2.73 s.
- Probe 2: the same fake, but it honours TERM. Result: `passed=False`, 0.56 s.
- `(ProcessLookupError, PermissionError)` are caught at all three signal sites.
- The supervisor site mirrors the pattern (`:3641`).
- Worst-case supervisor cleanup is about 2.2 + 2.2 + 1.5 + 1 ≈ 7 s. That is inside the installer's `timeout_s + 10` slack (`:1092`).

**F3: does samefile containment still refuse what it should? Yes.** I probed it with real paths and the custody root patched:

| Case | Result |
|---|---|
| Child inside the custody root | GO |
| Inward symlink | GO |
| Case alias of a child (APFS, test not skipped) | GO |
| Missing child inside the root (the lexical branch) | GO |
| Custody root itself | refused |
| Root with a trailing slash | refused |
| Case alias of the root | refused |
| `child/..` | refused |
| Existing sibling prefix `measurement-evil` | refused |
| Missing sibling prefix | refused |
| Symlink escape | refused |
| Symlink escape followed by a missing child | refused |
| `..` escape | refused |
| Custody root absent (`strict=True` → OSError) | refused |

## SHOULD-FIX

**SF1. The T0_REHEARSAL test does not show that the disjointness rule still applies after the cutoff** (`tests/test_night_gate.py:901-939`).
- The dictated closure test needed both directions: a T0 rehearsal plan outside custody passes the R16 check *and still gets the disjointness rule*.
- The test mocks `_pack_object`. For the exempt case it asserts only `reason != R16`; it never shows the plan is refused.
- For disjointness it defers to `test_run_night.py:3684`. That test calls `_pack_rehearsal_roots` directly with pre-cutoff fixtures, so it never goes through the exemption branch.
- The real risk is that a later refactor turns the exemption into "skip every root rule for T0" and no test notices. The cold Fable final pass will want this evidence for a provisional ruling.
- **Fix:**
  1. In the exempt branch of the new test, add `self.assertNotEqual("GO", receipt.verdict)`.
  2. Add an unmocked case: write a real authorization file under `Path(tmp).resolve()`. With the correct sha, R16 is skipped. With a `"0"*64` sha, the plan refuses `measurement_root_outside_custody`. My probe `probe_ex.py` in `/tmp/152c9255/prl-reaudit-opus` already does this.
  3. In `test_run_night`'s pack fixture, add one end-to-end case: a post-cutoff T0 plan whose `measurement_root` is inside the (patched) custody root must refuse `rehearsal_roots_not_disjoint`.

## NIT

- **N-a. `elapsed_s` and `bound_s` appear twice in the cadence refusal** (`run_night.py:3780-3781` + `:3903`). The worker prefixes both fields, and the cadence detail already ends with `; elapsed_s=… bound_s=…`. Fix: drop the suffix in `_probe_cadence`, or drop the two prefix fields in `_probe_worker`.
- **N-b. The supervisor-timeout detail has no timing** (`:3665-3667`). It still prints `median_ms=None …: supervisor timeout`. Fix: add `custody_elapsed_s` and `timeout_s` to that detail string.
- **N-c. The new installer refusal string is not in `arm_retry.INSTALLER_REFUSALS`.** This is the undispositioned prior N6 plus one new string. It is safe for now: `classify_abort` defaults unknown causes to `cold_gate`. Fix: register it with the other N6 strings.
- **N-d. Operational note on S2.** The night plist embeds the resolved `claude` courier path. If Claude Code auto-updates between the probe and the install (the receipt can be up to 6 h old), install refuses. That is fail-closed and cured by re-running the probe. The runbook runs the two back to back, so the risk is low. Fix: name the label that differs in the refusal text, so the operator knows to re-probe.

## Test runs

Clone `/tmp/152c9255/prl-reaudit-opus` at `9500545f`; no sudo, launchctl or real powermetrics.

| Run | Result |
|---|---|
| `tests.test_arm_retry`, `tests.test_night_gate`, `tests.test_run_night_probe_cadence`, `tests.test_evidence_arm_sequence` | `Ran 144 tests in 6.559s` — `OK` |
| `tests.test_night_agent_install` | `Ran 81 tests in 838.521s` — `OK` |
| `tests.test_run_night` | `Ran 233 tests in 215.973s` — `FAILED (failures=1)` |
| `gen_state.py --check` | rc 0 |
| `tests.test_gen_derivation_night`, `tests.test_launch_context_no_qos_override` | `Ran 45 tests` — `OK` |

About the `tests.test_run_night` failure:
- The failing test was `BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go`, with `external watchdog (8 s): bind supervisor blocked in journal_block`.
- It happened while the install suite was running concurrently. Run alone, the test passed 3/3.
- The bind supervisor does not call the changed helpers (`_stop_probe_group` and `_term_then_kill_probe_group` are used only at `:3560/3641/3750`), so this is load flakiness, not something the delta caused.

Two notes on the runs:
- The `test_night_agent_install` run passed the Bash tool's 10-minute limit, and the harness moved it to the background by itself. I did not background anything on purpose; its result was read from the harness's output file.
- The worktree was not modified.
