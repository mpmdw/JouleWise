```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"findings","completion":"complete","summary":"Fixed kill-escalation pipe hang with reap-and-close cleanup; added escalation regression and DEVNULL coverage.","workspace":{"base_requested":"ebf76c086","base_mode":"exact","head_start":"ebf76c08684a1ae44a7f97960ddab881f9f84b0b","head_end":"ebf76c08684a1ae44a7f97960ddab881f9f84b0b","upstream_end":"ebf76c08684a1ae44a7f97960ddab881f9f84b0b","branch":"fix/2026-11-02-powermetrics-orphan"},"pathspec":["joulewise/adapters/powermetrics.py","tests/test_powermetrics_bounded_capture_timeout.py","tests/test_powermetrics.py",".codex-report/PM-ORPHAN.md",".codex-report/fix1-baseline-tests.log",".codex-report/fix1-focused-tests.log",".codex-report/fix1-escalation-control.py",".codex-report/fix1-escalation-control.log",".codex-report/fix1-final-tests.log"],"unowned_dirty":[".codex-report/baseline-powermetrics-tests.log",".codex-report/baseline-tests.log",".codex-report/callsite-scan.log",".codex-report/fixture-census.log",".codex-report/focused-tests.log",".codex-report/git-stage.log",".codex-report/mutation-tests.log",".codex-report/regression-tests.log",".codex-report/replay-original.py",".codex-report/round2-callsite-scan.log",".codex-report/round2-final-tests.log",".codex-report/round2-fixture-census.log",".codex-report/round2-focused-tests.log",".codex-report/round2-mutation-tests.log",".codex-report/round2-probe-control.log",".codex-report/round2-probe-control.py",".codex-report/round2-scan-timeout-calls.py",".codex-report/round2-seam-diagnostic.log",".codex-report/round2-seam-fixed.log",".codex-report/round2-test-seam.diff",".codex-report/round2-timeout-candidates.log"],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"test","cmd":"task_tmp=$(mktemp -d /tmp/pm-orphan-fix1-baseline.XXXXXX)\nTMPDIR=\"$task_tmp\" /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_powermetrics_bounded_capture_timeout > /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-baseline-tests.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 7 tests in 0.430s","","OK"]},"expected":{"exit_code":0,"tail_regex":"(?s)Ran 7 tests.*OK"}},{"id":"V2","kind":"test","cmd":"task_tmp=$(mktemp -d /tmp/pm-orphan-fix1-focused.XXXXXX)\nTMPDIR=\"$task_tmp\" /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_powermetrics_bounded_capture_timeout > /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-focused-tests.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 9 tests in 10.421s","","OK"]},"expected":{"exit_code":0,"tail_regex":"(?s)Ran 9 tests.*OK"}},{"id":"V3","kind":"test","cmd":"task_tmp=$(mktemp -d /tmp/pm-orphan-fix1-control.XXXXXX)\nTMPDIR=\"$task_tmp\" /opt/homebrew/bin/python3.13 -B /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-escalation-control.py > /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-escalation-control.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["FAILED (failures=1)","COMMITTED_UNBOUNDED_HELPER_REJECTED=True"]},"expected":{"exit_code":0,"tail_regex":"(?s)FAILED \\(failures=1\\).*COMMITTED_UNBOUNDED_HELPER_REJECTED=True"}},{"id":"V4","kind":"test","cmd":"task_tmp=$(mktemp -d /tmp/pm-orphan-fix1-final.XXXXXX)\nTMPDIR=\"$task_tmp\" /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_powermetrics_bounded_capture_timeout tests.test_powermetrics tests.test_controller tests.test_fixture_orphan_census > /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-final-tests.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 158 tests in 104.126s","","OK (skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"(?s)Ran 158 tests.*OK"}},{"id":"V5","kind":"inspection","cmd":"git -C /Users/edr/code/jw-wt/pm-orphan diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}],"flags":[{"id":"F1","kind":"residual_risk","level":"nonblocking","text":"A root sampler that ignores SIGTERM beyond the 10 s grace survives the sudo SIGKILL fallback. Python cannot remove it without a sudoers kill entry. Fixture evidence is not live hardware validation.","needs":"Lead owns residual acceptance, final review, live gates, and commits."},{"id":"F2","kind":"environment","level":"nonblocking","text":"Two existing live fixture-census tests skipped because the sandbox denies ps; system-wide orphan count is unknown.","needs":"Lead reruns the two live census tests in a permitted terminal."}]}
```

The following pre-round prose is retained as history through ebf76c086; the Fix round 1 section below supersedes its cleanup and timing statements.

## Change

Both `_run_bounded_capture` and `_probe_capability` now launch with `Popen`, wait with `communicate(timeout=...)`, and call the existing `_stop_process` on every `BaseException` from that wait before re-raising. This gives sudo SIGTERM to relay before the existing helper's 10 s grace and SIGKILL fallback. The bounded capture still propagates `TimeoutExpired` through its existing capture-release handler. The probe still maps timeout to the same structured UNKNOWN_ERROR result and metadata, with its 15.0 s timeout unchanged. Capture bytes, nonzero-return decoding/error text, and `_capture_timeout_s` are unchanged.

The new module has seven process-backed tests: bounded timeout propagation and grandchild disappearance; SIGTERM receipt with no launcher SIGKILL; bounded KeyboardInterrupt identity and cleanup; unchanged success bytes; unchanged nonzero error text; probe timeout cleanup and structured failure; and probe KeyboardInterrupt identity and cleanup. No sudo or real powermetrics is used. Both original-code controls reproduce a living grandchild without a SIGTERM receipt and show the corresponding new regression rejecting the old behavior; cleanup kills only those known unprivileged fixtures.

### decisions I made

- Catch BaseException around the wait only. Preserve existing launch-error handling, bounded capture release, and probe result mapping. Do not change measurement policy or printed numbers.
- Reuse `_stop_process` without changing it or adding a grace constant. Tests derive their startup/disappearance poll budget from that helper's actual 10.0 s communicate call.
- Keep the existing pid handshake before forcing a 10 ms timeout, allowing a scheduler turn without depending on interpreter startup speed. Poll spacing derives from that forced timeout. For the probe process test, observe the production 15.0 s request and shorten only the fixture's underlying communicate wait; existing mocked probe timeout tests retain the requested timeout in the exception.
- Migrate all 33 relevant existing test methods to Popen. A shared helper sends finite `-n COUNT` commands to their communicate-time capture fakes and leaves streaming fakes intact. It distinguishes sudo's own `-n` and passes unrelated platform/Git commands through to real Popen because subprocess is a shared module. Missing-binary tests fail at Popen construction. An AST comparison confirmed all existing powermetrics assertion expressions are unchanged.
- Update the real idle timeout test at `_capture_timeout_s` and retain its existing 0.75 s deadline and 17.5 s production-timeout assertion, recording the actual exception reaching the caller's wrapper.
- Register unique relay/sampler argv signatures, with positive, parent-PID, near-name, and production-negative tests. Anchor the sampler signature at the executable's first script argument so it does not misidentify the sampler argument inside the relay command.
- Preflight ps in the existing deliberate-orphan census test before spawning: its reaper also needs ps, so spawning after observation is denied could leak an unrelated fixture. Preserve the existing live skip status; no observation failure is counted as a clean census.
- Preserve inherited logs/control scripts and all out-of-scope state. Round 2 made no staging or commit attempts, as instructed; the historical git-stage.log belongs to Round 1. No other worktree was operated on.

### Other timeout launch sites

The one additional direct sudo/powermetrics `subprocess.run(timeout=...)` site found in Round 1 was `_probe_capability`; it is now fixed in scope. No remaining additional direct launch of that form was identified in tracked Python and shell launchers. Candidate listings are in `round2-timeout-candidates.log` (replay with `round2-scan-timeout-calls.py`) and `round2-callsite-scan.log` (tracked grep for subprocess.run and sudo/powermetrics).

`joulewise/doctor.py:101` still uses `subprocess.run(timeout=timeout_s)` for `sudo -n -l <powermetrics-path>`: it lists policy, without launching the sampler. `scripts/run_night.py:_probe_cadence` already uses Popen/communicate and TERM-first group cleanup. The T0 probe uses observed Popen/wait; the sampler checklist uses the existing sampler lifetime supervisor. Generic run wrappers and historical smoke scripts in the candidate list do not directly launch sudo/powermetrics with a run timeout. No out-of-scope fixes were made.

## Verification notes

The JSON records exact test commands, exit codes, and output tails for this round. All test runs used /opt/homebrew/bin/python3.13, a fresh /tmp TMPDIR, and disabled bytecode writes. The final requested five-module run passed 188 tests with two live census skips. The full suite was not run, as instructed.

The first Round 2 focused run had two errors in bundle tests because the Popen fake also intercepted unrelated platform subprocesses. A single-test diagnostic reproduced that issue; passing unrelated commands through fixed it. The two affected tests passed together, then the entire requested set passed on the final source. Earlier failed logs remain as evidence, not outstanding regressions.

The original-code control logs intentionally contain one unittest failure apiece: those are the regression tests rejecting the old implementation. Both control runners exit 0 only when the orphan reproduction and expected rejection are observed. The final session-end census exits 2 because ps is denied; its rows/count are unknown, not zero. The existing live census tests skip for that same sandbox restriction.

HEAD and upstream remain 4c98bbff59ea4f30d6a85001d7e3a87128ec01b1. RUN_STATE.md, TASK_QUEUE.md, docs/run_reports, and other lead-owned paths were not modified under the delegated allowlist. Next exact step: lead reads the final diff, reruns the live census in a permitted terminal, performs any live sudo verification in a clean lead-controlled session, and commits the authorized changes; CI runs the full suite.

## Residual risk

Fixture evidence is not live sudo/hardware validation. The sandbox prevents an authoritative system-wide orphan census. Lead-owned live gates and final review remain pending.

## Fix round 1

This section supersedes the earlier cleanup/timing statements above. Intake: both cold reports were read (Fable section 4a/findings 1–4; Opus sections 4–6/F1–F6). Mission M0 found no active stop card or global work-selection gate; this is the lead-assigned [AGENT] correction at exact HEAD `ebf76c086`. The exhaustive allowlist leaves state/queue/run-report bookkeeping with the lead.

### Diff summary

After the unchanged SIGTERM-first step and 10 s grace, `_stop_process` now uses `kill()`, `wait()`, then closes each non-None stdout/stderr pipe. Reaping the SIGKILLed sudo process does not read the pipe ends inherited by its sampler. The grace is named `STOP_PROCESS_GRACE_S = 10.0`; this is a refactor of the existing value. Capture exception identity, structured results, capture bytes and measurement policy remain unchanged.

The process-backed escalation regression uses the existing SIGTERM-forwarding relay and installs SIG_IGN in its sampler before publishing the sampler pid. It exercises the real grace, checks relay SIGKILL/reaping and closed pipes, and verifies the sampler is still alive when cleanup returns. Its finally block SIGKILLs only the known unprivileged fixture sampler and reaps the relay. A separate escalation test covers DEVNULL's None pipes. The comments now state the real timeout constraint, latency-only poll spacing, generous startup/disappearance budget and POSIX -SIGTERM returncode.

### Decisions I made

- Read the grace from the named constant instead of extracting a mocked communicate call. The production value and TERM-first order stay unchanged.
- Derive the regression's return bound from the sole timed wait: one grace (10 s), plus one grace-sized scheduling/reap/close allowance (10 s), for a test bound of 20 s. The additional interval is generous test slack, not a new production wait or an OS scheduling guarantee. The sampler lifetime is twice that bound (40 s), so a regression waiting for inherited-pipe EOF cannot pass by reaching natural sampler exit.
- Assert the helper also spends at least the real grace on the ignoring sampler, preserving escalation timing. Assert the sampler remains live and both pipes are closed on return.
- For the existing 0.01 s timeout, any positive value below the sampler lifetime gives the same outcome after the pid handshake. The /10 poll spacing changes observation latency only. Reusing the 10 s grace for startup/disappearance is a generous fixture budget, not a measured startup requirement.
- Keep test_idle_admission unchanged and run only the two touched test modules plus test_controller and test_fixture_orphan_census. No full suite, sudo, real sampler, quiet-window capture, staging, commit or push was run.
- Leave arm_readiness_evidence_t0._execute_probe (Opus F4 / Fable finding 2) and the _probe_cadence KeyboardInterrupt gap (F5) untouched for the lead's follow-up.

### Test commands and output tails


**V1 — test; exit 0.**

```sh
task_tmp=$(mktemp -d /tmp/pm-orphan-fix1-baseline.XXXXXX)
TMPDIR="$task_tmp" /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_powermetrics_bounded_capture_timeout > /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-baseline-tests.log 2>&1
```

```text
Ran 7 tests in 0.430s

OK
```

**V2 — test; exit 0.**

```sh
task_tmp=$(mktemp -d /tmp/pm-orphan-fix1-focused.XXXXXX)
TMPDIR="$task_tmp" /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_powermetrics_bounded_capture_timeout > /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-focused-tests.log 2>&1
```

```text
Ran 9 tests in 10.421s

OK
```

**V3 — test; exit 0.**

```sh
task_tmp=$(mktemp -d /tmp/pm-orphan-fix1-control.XXXXXX)
TMPDIR="$task_tmp" /opt/homebrew/bin/python3.13 -B /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-escalation-control.py > /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-escalation-control.log 2>&1
```

```text
FAILED (failures=1)
COMMITTED_UNBOUNDED_HELPER_REJECTED=True
```

**V4 — test; exit 0.**

```sh
task_tmp=$(mktemp -d /tmp/pm-orphan-fix1-final.XXXXXX)
TMPDIR="$task_tmp" /opt/homebrew/bin/python3.13 -B -m unittest -v tests.test_powermetrics_bounded_capture_timeout tests.test_powermetrics tests.test_controller tests.test_fixture_orphan_census > /Users/edr/code/jw-wt/pm-orphan/.codex-report/fix1-final-tests.log 2>&1
```

```text
Ran 158 tests in 104.126s

OK (skipped=2)
```

**V5 — inspection; exit 0.**

```sh
git -C /Users/edr/code/jw-wt/pm-orphan diff --check
```

No output (clean whitespace check).

The control runner intentionally reports one unittest failure and exits 0 only when the committed helper is rejected by the elapsed-time assertion. It extracts just that helper from the exact committed adapter, substitutes it in memory and runs only the new escalation regression. Its measured old-helper duration was 40.146264584036544 s against the 20 s test bound; the production files are never swapped. The fixed nine-test module, including the real 10 s escalation, passed in 10.421 s. The final four-module run passed 158 tests with two existing live census skips because ps is denied; the orphan census remains unknown. Test commands use /opt/homebrew/bin/python3.13, -B and fresh TMPDIR directories under /tmp. No out-of-scope files were modified.

### Residual risk and next exact step

If the root sampler ignores SIGTERM for the full 10 s grace, SIGKILL kills sudo without relaying to that sampler. The root sampler remains an orphan. Python cannot remove it without a sudoers kill entry. This fix bounds the pipe-related cleanup delay; it does not eliminate that residual orphan. These are unprivileged process fixtures, not live sudo/hardware validation.

Timing disclosure (Opus F2): the earlier TERM-first implementation still adds up to the 10 s grace plus reaping/closing overhead after a capture timeout or interruption. A capability probe can therefore spend its existing 15 s request plus the 10 s stop grace before returning its existing result. The previous unbounded EOF tail after SIGKILL is removed in this round; no production timeout or acceptance number changed.

HEAD and upstream remain ebf76c08684a1ae44a7f97960ddab881f9f84b0b. Existing untracked reports/logs were preserved. Next: the lead reviews this diff, reruns the two skipped live census tests where ps is permitted, owns final/live verification and residual acceptance, then commits. The two excluded launcher follow-ups stay lead-owned.
