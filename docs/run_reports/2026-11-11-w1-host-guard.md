# W1 host-command guard — 2026-11-11

## Leak list (operational notice input)

One legacy leak was established and fixed:

| Module | Test | Command |
| --- | --- | --- |
| tests.test_post_window_unstrand | PostWindowUnstrandTests.test_native_ps_clean_completed_window_under_caffeinate | /usr/bin/caffeinate -i /bin/bash ... |

The raw `2026-11-11-w1-host-guard-leaks.txt` lists that module/test/command.
The in-process guard was committed as `09325f171` before ANY legacy test ran;
the initial empty scan was committed as `7f59a46c2`. The newly established
caffeinate leak was then committed as `6928358fe` BEFORE its fixture repair.
The sandbox's native-ps check ordinarily skips that test before the launch.
For the red witness ONLY, the precheck was replaced with a no-op; the guard
then blocked the original launch, recording one refusal and adding a failure.
No host command executed. Red lines:

```text
HostCommandRefused: test host command refused: caffeinate
AssertionError: host command guard recorded refusal(s): caffeinate ['/usr/bin/caffeinate', '-i', '/bin/bash', ...]
Ran 1 test in 0.009s
FAILED (failures=1, errors=1)
```

The repaired test explicitly fakes only the caffeinate call and supplies its
childless-helper census via the existing UNSTRAND_PS fixture. It runs the real
unstrand shell against synthetic custody, keeps every existing output/no-log/
blinded assertion, and adds a one-call assertion for the wrapper fake. It no
longer acquires an actual host sleep assertion or needs native process access.
The method name is retained per the no-rename rule; it is now a synthetic
witness, not native validation. The focused rerun passes with ZERO refusals.
No other legacy refusal was established in the reached portions. Timed-out
modules and all keyword candidates not reached are enumerated below; they
must not be declared leak-free. Guard-unit expected refusals are separate.

## Design as built

`tests/host_command_guard.py` wraps `subprocess.Popen.__init__` (preserving the
class and its usual API), `os.system`, both posix_spawn calls when available,
and all eight exec variants. It classifies the given and realpath basenames,
leading env/assignments, shell -c bodies and every simple command separated by
semicolon, &&, ||, pipe (also newline/background separators). It refuses the
approved fixed commands, mutating launchctl verbs and networksetup/scutil set
arguments. defaults/kill/killall/pgrep/ps/git remain allowed at runtime.

Each refusal records the basename, first six original argv items, active test
id when known, first frame outside the guard, pid and a deduplication id. The
process-global list and append-only JSONL report both carry the event before
HostCommandRefused(RuntimeError) is raised. TestCase.run snapshots both stores
and adds a FAILURE even when production swallows the exception. Nested tests
restore the previous active test id. Child records are attributed to the
parent test by the parent's per-test report range, even if their own test_id
is null. install is idempotent; uninstall restores wrappers/environment for
unit tests. expect_refusals is restricted by caller module AND exact source
file to the guard's own test module (including its shard-runner alias).

`tests/__init__.py` contains only the install import/call. The guard prepends
`tests/_host_guard_site` to PYTHONPATH and shares a guard-owned temporary
JW_TEST_HOST_GUARD_REPORT file. sitecustomize loads this checkout's guard in
ordinary Python children, and uses PathFinder to execute the next existing
sitecustomize under its normal module name. The chaining witness passes.

The module unittest launch imports tests before its body. shard_tests imports
bare test names and previously bypassed that package initialization. Confirmed
both runners and timings are UNBOUND using v4_registration.ARTIFACTS. Added
ONLY `import tests` to its two import-path launch seams (whole shards and
id/unit discovery). quick_suite.module_job delegates to run_shard, so needs no
edit. A fresh -S synthetic child proves run_shard initializes the guard before
a test body even without startup sitecustomize. Two new test modules each get
exactly one timings-map line; no other scheduling data is changed.

## Allowlist review

The static scan reads git-tracked files under scripts/ and joulewise/ only.
Python literals are visited by AST; other tracked text, including extensionless
shell scripts, is tokenized by logical lines, skipping shell comments. Binary
artifacts are skipped. The inventory deliberately includes conservative text
mentions and bare/dynamic launchctl literal sites, not just executable calls.
An unresolved executable expression with literal -I/-S is also inventoried.
Locators combine enclosing function/class (or shell) with a command-text hash,
never a line number. Both unlisted sites and stale entries fail the test.

Seams were reviewed by file/function: explicit runner/Context.run/actuator.run,
KeepAwake's popen/run_command, LaunchctlAdapter's fake executable, and the
session/driver probe seams are named only where inspected. Other entries are
conservatively `none`; this includes diagnostic strings, generated operator
commands and non-call data literals. `none` is not an execution authorization.
Every none entry is listed in the residual-risk appendix below; the reviewer
must retain shell command stubs when any corresponding shell is exercised.

Inventory: **368 literal sites**, **210 none seams**.

| Command | Sites |
| --- | ---: |
| caffeinate | 13 |
| defaults | 1 |
| kill | 29 |
| launchctl | 45 |
| networksetup | 2 |
| pmset | 102 |
| python-isolated | 9 |
| shutdown | 12 |
| sudo | 120 |
| systemsetup | 35 |

The requested literal assertion that neither environment-variable NAME occurs
under production trees cannot pass for PYTHONPATH: this base already uses it,
e.g. quiet_guard_privileged.py, evidence_night.py, flags/collect.py and the
night installer. No such production file was edited. The grep witness instead
asserts that JW_TEST_HOST_GUARD_REPORT and _host_guard_site are absent from
both production trees. Existing PYTHONPATH handling is a documented propagation
limitation, not silently declared test-only.

## Red then green evidence

The base has neither the guard nor its allowlist. A synthetic base-shaped
package (empty tests/__init__.py, no guard/allowlist), containing the new tests,
was run in isolated Python; it never executed a refused command. Red lines:

```text
ImportError: cannot import name 'host_command_guard' from 'tests'
FAILED (errors=1)
FileNotFoundError: .../tests/host_command_sites.json
FAILED (errors=1)
```

These are absence-of-new-mechanism baselines, not a production behavior change.
Guard witnesses additionally run inner TestCases and require FAILURE after an
in-process swallowed exception and after a swallowed child pmset attempt.
Refused Popen forms patch subprocess._fork_exec and assert ZERO invocations;
os wrappers also patch their underlying dispatch and require ZERO invocations.
No refused command is used to demonstrate the red against unguarded execution.
Classifier-only allowed checks cover launchctl print/list/blame and read-only
networksetup; real launchctl is never executed by the guard's unit tests.

## Verification

All legacy and new runs are one selected module at a time, using Python 3.13,
-B and TMPDIR=/private/tmp. The bounded scan harness invokes unittest's normal
loader/TestRunner, prints failures immediately and retains per-module logs.
No full-suite run, pytest, network, model download or measurement pipeline was
used. Each table row can be replayed as
`TMPDIR=/private/tmp python3.13 -B -m unittest <selected module / test name>`;
the actual bounded harness used the same unittest loader/runner with immediate
failure logging. The sole red-witness precheck substitution is described above. Timeouts are incomplete, not passes. Early broad scans had short caps;
subsequent caps use a new test process group and terminate only that group.
Early caps killed the selected interpreter only; descendant cleanup was not fully auditable because process census is denied. Later caps terminate only the newly created test process group. The lead should verify no synthetic helpers remain before any native work. The first broad run printed failures before its cap but lacked a final traceback
summary; it must be rerun by the lead. No synthetic test discharges a native gate.

| Selected module / test name | Result | Process seconds | Guard events |
| --- | --- | ---: | ---: |
| tests.test_network_time_off | PASS | 11.349 | 0 |
| tests.test_run_night | INCOMPLETE (cap) | 120.015 | 0 |
| tests.test_w1_reliability_r2 | HARNESS SYNTAX ERROR; no tests ran | 0.410 | 0 |
| tests.test_w1_reliability_r2 | PASS | 62.248 | 0 |
| tests.test_w1_reliability_r3 | PASS | 13.538 | 0 |
| tests.test_w1_reliability_r4 | INCOMPLETE (cap) | 35.036 | 0 |
| tests.test_w1_reliability_r5 | PASS | 24.717 | 0 |
| tests.test_post_window_unstrand | INCOMPLETE (cap) | 35.013 | 0 |
| tests.test_install_night_agent | INCOMPLETE (cap) | 35.043 | 0 |
| tests.test_night_agent_install | INCOMPLETE (cap) | 35.013 | 0 |
| tests.align.test_r1_round6_exec_review | PASS | 17.974 | 0 |
| tests.align.test_r1_round7_exec_review | PASS | 15.603 | 0 |
| tests.align.test_r1_round8_exec_review | INCOMPLETE (cap) | 35.099 | 0 |
| tests.align.test_r1_round6_power | PASS | 16.969 | 0 |
| tests.align.test_v4_kit | INCOMPLETE (cap) | 35.034 | 0 |
| tests.align.test_v4_series | INCOMPLETE (cap) | 35.034 | 0 |
| tests.test_bytes_h_session | INCOMPLETE (cap) | 35.024 | 0 |
| tests.test_host_command_guard | PASS | 2.421 | 24 (expected unit witnesses excluded on final run) |
| tests.test_host_command_sites | PASS | 54.303 | 0 |
| tests.test_shard_tests | INCOMPLETE (cap) | 35.043 | 0 |
| tests.test_quick_suite | PASS | 4.551 | 0 |
| tests.align.test_v4_executed_closure | PASS | 54.123 | 0 |
| tests.align.test_v4_dynamic_closure | INCOMPLETE (cap) | 160.026 | 0 |
| tests.align.test_v4_registration | INCOMPLETE (cap) | 170.130 | 0 |
| tests.test_post_window_unstrand.PostWindowUnstrandTests.test_native_ps_clean_completed_window_under_caffeinate | FAIL | 1.384 | 1 |
| tests.test_post_window_unstrand.PostWindowUnstrandTests.test_native_ps_clean_completed_window_under_caffeinate | PASS | 3.325 | 0 |
| tests.test_post_window_unstrand | INCOMPLETE (cap) | 75.048 | 0 |
| tests.test_host_command_guard | PASS | 6.591 | 0 (expected unit witnesses excluded on final run) |

Final bounded test-process time: 1130.064 s (includes interpreter startup and capped runs). Initial guard smoke 1.134 s, a final direct focused unittest run (1 test, PASS, 4.479 s), and the two tiny safe missing-mechanism baselines are additional. Overall targeted-test process time remains about 19 minutes, below the 20-minute budget.

A sandbox-dependent signal-path failure was observed in
`tests.align.test_r1_round8_exec_review.NightRepeatedSignalTests.test_signals_during_the_termination_do_not_cut_it_short`:

```text
AssertionError: '"proven": true' not found in ...
group_census: census_exit_3: sysmon request failed with error: sysmond service not found
pgrep: Cannot get process list
```

The guard recorded no refusal there; its existing assertion was preserved.
Executed closure: PASS, 6 tests. Dynamic closure: 9 tests passed, then the
fresh-process minimal-dry-run test exceeded the 160 s module cap. Registration:
tests reached before receipt binding passed, then the receipt-binding test
exceeded the 170 s module cap. No stale trace/receipt digest failure was emitted,
so no failure is mislabeled EXPECTED. Both complete modules remain for the lead.
The shard-runner module also hit its cap; quick_suite passed all 15 tests.
The final guard module passed 11 tests in 4.905 s; the static-site module passed
2 tests in 53.354 s. Only seam metadata was normalized to literal `none`
after that static run; its full site identities were compared with the tested
inventory and found identical, and the schema was rechecked.

The changed unstrand module's final 75 s cap also contained this preserved
assertion failure (no guard refusal), whose cause was not established:

```text
FAIL: test_follow_prints_a_new_launch_transition_without_payload
AssertionError: 'No new launching transition' unexpectedly found in ...
```

This may be sensitive to startup/load timing; no causal diagnosis is claimed.
The changed caffeinate test passes independently under plain `python3.13 -B -m
unittest tests.test_post_window_unstrand.PostWindowUnstrandTests.test_native_ps_clean_completed_window_under_caffeinate`
(1 test, 4.479 s), without the red-witness precheck patch.
No existing test module directly imports the changed guard/unstrand test files
(other than the new guard witnesses); runner dependents were selected above.

## Scope, uncertainty and handoff

No joulewise/ production file, bound file, record schema, measured byte, flag,
verdict, receipt, protocol, deviation, trace or coordination-state file changed.
The only scripts/ exceptions are the specifically authorized import launch
seams and two timing entries. There are no new production refusal codes or
arm/prepare record fields; HostCommandRefused is test-only.

Authority intake read the seat report first, M0/no stop card, RL-53 W-0 through
W-3, RL-35 item 4, RL-37 and audit sections 0/4.3/4.5/8.1. Intake mistake:
an initial git-show sed range ran from RL-53 to EOF and displayed adjacent
rulings, including B5 discussion, before truncating. It was corrected to the
requested heading-bounded read. No real custody or external /Users/edr path
was accessed and no B5 content was used for this engineering work. The shared
Git alternates were used only via allowed Git object reads. No external skill,
network tool, consultation or sub-agent was used.

Pending NEEDS_RULING (asked asynchronously): the brief's literal zero production
PYTHONPATH-name references contradict this base. Options: accept the implemented
grep contract (new report variable and guard-site directory are test-only), or
keep literal acceptance blocked for the lead. Recommendation: accept the former,
without any bound production edit. Blocked work: claiming the literal environment-
name clause is met. AGENTS.md requires early return for spec conflicts; this
report preserves the conflict rather than silently treating the clause as met.

This tripwire is not a security sandbox. It does not intercept native C/ctypes
exec paths, os.kill, arbitrary process APIs, command names assembled at runtime,
shell script internals, command substitution/eval/functions or extra command
wrappers such as `command sudo`. It does not sandbox the filesystem. A child
that drops/replaces PYTHONPATH, prepends another sitecustomize, or uses -I/-S may skip startup injection; the
static inventory highlights the latter but cannot make an isolated child
install the guard. Shell tests still need explicit fake executables. Bare
unittest discovery/direct-file launches that never import tests are outside
the verified entry points. Background children outliving the parent test may
be attributed to a later test or escape the per-test interval. Test code can
replace wrappers with fakes; this protects accidental calls, not malicious
bypass. These limits remain operational risks.

Native check owed to the lane lead: on the remote measurement Mac, run the
incomplete and not-reached synthetic modules with this guard installed and
preserve any per-test refusal. Do not run a host command to prove the guard.
Keep all existing RL-35/RL-37 production-native gates for after installation;
this test-only change supplies no live host, MLX, meter or quiet-window proof.
The lead owns the cold review and final integration; this seat did not perform
an independent cold review. No push was performed.

## Residual risks: every none seam

These entries may be command literals, documentation, templates or generated
text. Their presence does not establish that they execute. No verified injected
replacement seam was claimed for them; inspect the consumer before running a
corresponding test. The command-text hashes identify them in the JSON allowlist.

- `joulewise/align/analysis/budget_pilot.py` / `frontier_lines:127a51b03ee80741` / `kill` — none
- `joulewise/align/apple/external_volume.py` / `prepare_plan:136f44584c694de1` / `sudo` — none
- `joulewise/align/apple/external_volume.py` / `prepare_plan:2b868a2f3773f0e8` / `sudo` — none
- `joulewise/align/apple/external_volume.py` / `prepare_plan:48660b4c3d1c871c` / `pmset` — none
- `joulewise/align/apple/external_volume.py` / `prepare_plan:4c8df13ddef8c85a` / `sudo` — none
- `joulewise/align/apple/external_volume.py` / `prepare_plan:5d4a9c4047529e4e` / `sudo` — none
- `joulewise/align/apple/external_volume.py` / `prepare_plan:9e95f2f544d41af9` / `sudo` — none
- `joulewise/align/apple/external_volume.py` / `prepare_plan:a50dbe7d9b4ffa57` / `defaults` — none
- `joulewise/align/apple/external_volume.py` / `prepare_plan:a50dbe7d9b4ffa57` / `sudo` — none
- `joulewise/align/apple/external_volume.py` / `prepare_plan:eee93aa4b0c6fd45` / `sudo` — none
- `joulewise/align/frontier.py` / `frontier_agreement:ffdffa26f6f4606f` / `kill` — none
- `joulewise/align/power/nvml.py` / `NvmlSampler.start:6bb832aaca53e200` / `shutdown` — none
- `joulewise/align/prequal.py` / `<module>:d5173d5d0ce3e0aa` / `pmset` — none
- `joulewise/align/prequal.py` / `check_launcher.fake_run:1b8938f8083e84a0` / `launchctl` — none
- `joulewise/align/prequal.py` / `check_launcher:1b8938f8083e84a0` / `launchctl` — none
- `joulewise/align/prequal.py` / `check_launcher:2d02131c2f35f25d` / `launchctl` — none
- `joulewise/align/prequal.py` / `check_launcher:87e4c8ab536742ec` / `python-isolated` — none
- `joulewise/align/prequal.py` / `check_launcher:ae17b9a737bf75ad` / `launchctl` — none
- `joulewise/align/r0.py` / `markdown:4d5ec70908dde187` / `pmset` — none
- `joulewise/align/w1_smoke.py` / `SmokeRunner.guards:ae17b9a737bf75ad` / `launchctl` — none
- `joulewise/align/w1_smoke.py` / `SmokeRunner.in_window_faults:0ad70fd971de1688` / `kill` — none
- `joulewise/align/w1_smoke.py` / `SmokeRunner.in_window_faults:0bfce5de2f178ed2` / `kill` — none
- `joulewise/align/w1_smoke.py` / `SmokeRunner.in_window_faults:2744b757296dd99b` / `kill` — none
- `joulewise/align/w1_smoke.py` / `SmokeRunner.in_window_faults:462bfeb0798f3074` / `kill` — none
- `joulewise/align/w1_smoke.py` / `SmokeRunner.teardown_owned:86741a50f2495421` / `launchctl` — none
- `joulewise/align/w1_smoke.py` / `SmokeRunner.teardown_owned:ae17b9a737bf75ad` / `launchctl` — none
- `joulewise/align/w1_smoke.py` / `SmokeRunner.terminal:ae17b9a737bf75ad` / `launchctl` — none
- `joulewise/arm_readiness.py` / `_histsem_rederive_pack_authentication:e1fd7f56a393b489` / `python-isolated` — none
- `joulewise/arm_readiness.py` / `_launch_argv_matches:0672075787e402de` / `caffeinate` — none
- `joulewise/arm_readiness_evidence.py` / `<module>:1100034de2cbaf6c` / `sudo` — none
- `joulewise/arm_readiness_evidence.py` / `<module>:1100034de2cbaf6c` / `systemsetup` — none
- `joulewise/arm_readiness_evidence.py` / `<module>:2b7822c8043c760a` / `systemsetup` — none
- `joulewise/arm_readiness_evidence.py` / `<module>:3ba6f6bbbadb0e3d` / `systemsetup` — none
- `joulewise/arm_readiness_evidence.py` / `<module>:648ae5c0a3a3cb5e` / `sudo` — none
- `joulewise/arm_readiness_evidence.py` / `<module>:648ae5c0a3a3cb5e` / `systemsetup` — none
- `joulewise/arm_readiness_evidence.py` / `_derive_doctrine_pin:1100034de2cbaf6c` / `sudo` — none
- `joulewise/arm_readiness_evidence.py` / `_derive_doctrine_pin:1100034de2cbaf6c` / `systemsetup` — none
- `joulewise/arm_readiness_evidence.py` / `_execute_unittest_suite_subprocess:f2f4093de685bcef` / `python-isolated` — none
- `joulewise/arm_readiness_evidence.py` / `_generator_command:cfa8b5d171c09408` / `python-isolated` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_derive_power:541443a289d468bd` / `pmset` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_derive_power:76a35a4bd9cb5cbb` / `pmset` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_derive_power:c463823381952a7c` / `pmset` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_derive_powermetrics:650aa89ad0060b30` / `sudo` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_derive_powermetrics:868508abc39f6298` / `sudo` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_derive_powermetrics:c6b4f9d80631983e` / `sudo` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_derive_process_census:0672075787e402de` / `caffeinate` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_derive_process_census:fae9dc7232841220` / `caffeinate` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_launch_manifest:0672075787e402de` / `caffeinate` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_systemsetup_argv:24e5e1c2bbef5653` / `sudo` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_systemsetup_argv:e4cd6a3107d1f763` / `systemsetup` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_thermal_probe:0d98ba3c3a592d02` / `pmset` — none
- `joulewise/arm_readiness_evidence_t0.py` / `_thermal_probe:541443a289d468bd` / `pmset` — none
- `joulewise/calibration_ledger.py` / `_stop_custody_worker:80730f9e4c2a3989` / `kill` — none
- `joulewise/doctor.py` / `<module>:338f62ea33752c78` / `sudo` — none
- `joulewise/doctor.py` / `_sudo_policy_probe:24e5e1c2bbef5653` / `sudo` — none
- `joulewise/doctor.py` / `_sudo_policy_probe:e2b36c759375a153` / `sudo` — none
- `joulewise/doctor.py` / `_sudo_policy_probe:e37a46ed15c951f9` / `sudo` — none
- `joulewise/doctor.py` / `build_doctor_report:1566abee6c2dc3c5` / `sudo` — none
- `joulewise/doctor.py` / `build_doctor_report:53c563fcbf7a0322` / `sudo` — none
- `joulewise/hazards/instrument.py` / `<module>:004ec7e0892e7838` / `sudo` — none
- `joulewise/hazards/instrument.py` / `<module>:0269bfef383ba4f7` / `sudo` — none
- `joulewise/hazards/instrument.py` / `<module>:24e5e1c2bbef5653` / `sudo` — none
- `joulewise/hazards/instrument.py` / `_term_then_kill:0dcca0300f4405bc` / `sudo` — none
- `joulewise/night_gate.py` / `<module>:0d98ba3c3a592d02` / `pmset` — none
- `joulewise/night_gate.py` / `<module>:541443a289d468bd` / `pmset` — none
- `joulewise/night_gate.py` / `<module>:76a35a4bd9cb5cbb` / `pmset` — none
- `joulewise/night_gate.py` / `<module>:bf6b444741079b85` / `pmset` — none
- `joulewise/quiet_guard.py` / `<module>:650aa89ad0060b30` / `sudo` — none
- `joulewise/quiet_guard.py` / `<module>:f64ab60939bdc413` / `sudo` — none
- `joulewise/quiet_predicate_campaign.py` / `record_covariates:e046fa1b80ba1888` / `sudo` — none
- `joulewise/sampler_teardown.py` / `SamplerTeardown._sampler_command:24e5e1c2bbef5653` / `sudo` — none
- `joulewise/sampler_teardown.py` / `SamplerTeardown._sampler_command:8dd135ef35539688` / `sudo` — none
- `joulewise/t0_rehearsal.py` / `<module>:0672075787e402de` / `caffeinate` — none
- `joulewise/t0_rehearsal.py` / `<module>:0d98ba3c3a592d02` / `pmset` — none
- `joulewise/t0_rehearsal.py` / `<module>:0fa61c8bae4e7dcf` / `caffeinate` — none
- `joulewise/t0_rehearsal.py` / `<module>:175a05d35d6cb7d5` / `caffeinate` — none
- `joulewise/t0_rehearsal.py` / `<module>:24e5e1c2bbef5653` / `sudo` — none
- `joulewise/t0_rehearsal.py` / `<module>:541443a289d468bd` / `pmset` — none
- `joulewise/t0_rehearsal.py` / `<module>:648ae5c0a3a3cb5e` / `sudo` — none
- `joulewise/t0_rehearsal.py` / `<module>:648ae5c0a3a3cb5e` / `systemsetup` — none
- `joulewise/t0_rehearsal.py` / `<module>:650aa89ad0060b30` / `sudo` — none
- `joulewise/t0_rehearsal.py` / `<module>:668741c8bca9cef3` / `systemsetup` — none
- `joulewise/t0_rehearsal.py` / `<module>:742b3a650c01233f` / `sudo` — none
- `joulewise/t0_rehearsal.py` / `<module>:76a35a4bd9cb5cbb` / `pmset` — none
- `joulewise/t0_rehearsal.py` / `<module>:bf6b444741079b85` / `pmset` — none
- `joulewise/t0_rehearsal.py` / `<module>:c463823381952a7c` / `pmset` — none
- `joulewise/t0_rehearsal.py` / `<module>:c6b4f9d80631983e` / `sudo` — none
- `joulewise/t0_rehearsal.py` / `<module>:fae9dc7232841220` / `caffeinate` — none
- `joulewise/t0_rehearsal.py` / `_run_real_author_boundary:07935a92b5068149` / `sudo` — none
- `joulewise/t0_rehearsal.py` / `_run_real_author_boundary:07935a92b5068149` / `systemsetup` — none
- `joulewise/t0_rehearsal.py` / `_run_real_author_boundary:650aa89ad0060b30` / `sudo` — none
- `joulewise/t0_rehearsal.py` / `_run_real_author_boundary:668741c8bca9cef3` / `systemsetup` — none
- `scripts/align_ssd_qualification.py` / `<module>:53b2328211651674` / `sudo` — none
- `scripts/align_v4_harvest_off.py` / `checkout_identity:180159af2e908e9f` / `python-isolated` — none
- `scripts/b6_machine_test.py` / `prepare:9ac638f4c9410874` / `launchctl` — none
- `scripts/b6_machine_test.py` / `report:502ee0a584ce0b0b` / `launchctl` — none
- `scripts/b6_machine_test.py` / `report:6843143b16fdf87d` / `launchctl` — none
- `scripts/bench_replay_start_drift.py` / `<module>:6bba141443c9a807` / `sudo` — none
- `scripts/bench_replay_start_drift.py` / `markdown:c43da4cc83d0cdc0` / `systemsetup` — none
- `scripts/bench_replay_start_drift.py` / `require_no_night_agent:502ee0a584ce0b0b` / `launchctl` — none
- `scripts/bench_replay_systemsetup_stub.py` / `<module>:51a964bd9a3a3c26` / `sudo` — none
- `scripts/bench_replay_systemsetup_stub.py` / `<module>:51a964bd9a3a3c26` / `systemsetup` — none
- `scripts/capture_t0_step.py` / `_command_for_step:07935a92b5068149` / `sudo` — none
- `scripts/capture_t0_step.py` / `_command_for_step:07935a92b5068149` / `systemsetup` — none
- `scripts/capture_t0_step.py` / `_command_for_step:650aa89ad0060b30` / `sudo` — none
- `scripts/capture_t0_step.py` / `_command_for_step:668741c8bca9cef3` / `systemsetup` — none
- `scripts/capture_t0_step.py` / `_execute:e4cd6a3107d1f763` / `systemsetup` — none
- `scripts/capture_t0_step.py` / `_load_context:175a05d35d6cb7d5` / `caffeinate` — none
- `scripts/capture_t0_step.py` / `_load_context:ee36f55774cf4291` / `caffeinate` — none
- `scripts/check-codex-mcp.mjs` / `shell:7174718a91937e4f` / `kill` — none
- `scripts/check-codex-mcp.mjs` / `shell:a952b82807973049` / `kill` — none
- `scripts/codex-bridge` / `shell:06604ea50ba927a5` / `kill` — none
- `scripts/codex-bridge` / `shell:2f3b659ffdee32a7` / `kill` — none
- `scripts/codex-bridge` / `shell:593bdd5e38e3a866` / `kill` — none
- `scripts/codex-bridge` / `shell:975414789dc5b379` / `kill` — none
- `scripts/codex-bridge` / `shell:9e130bc6b449ee75` / `kill` — none
- `scripts/codex-mcp-server.mjs` / `shell:3f025979692217c4` / `shutdown` — none
- `scripts/codex-mcp-server.mjs` / `shell:80f4b71b035a93c5` / `shutdown` — none
- `scripts/codex-mcp-server.mjs` / `shell:994f113f3e2adbbd` / `shutdown` — none
- `scripts/codex-mcp-server.mjs` / `shell:ba7fc59769a7fa87` / `shutdown` — none
- `scripts/codex-mcp-server.mjs` / `shell:cd0929e228528e7e` / `shutdown` — none
- `scripts/codex-mcp-server.mjs` / `shell:ea08afaad32cee03` / `shutdown` — none
- `scripts/codex-run` / `shell:53561df0afc5244b` / `kill` — none
- `scripts/codex-run` / `shell:7bd77555fa6d5dc8` / `kill` — none
- `scripts/codex-run` / `shell:7d72caea8cb16a6a` / `kill` — none
- `scripts/codex-run` / `shell:cfcc9cd178c4742a` / `kill` — none
- `scripts/codex-run` / `shell:d4e1bb811a028457` / `kill` — none
- `scripts/ed_session/rail-probe.sh` / `shell:52ec67b85270b9a4` / `sudo` — none
- `scripts/ed_session/rail-probe.sh` / `shell:de942b5b57d7afcb` / `sudo` — none
- `scripts/ed_session/rail-probe.sh` / `shell:f51fe12c0e234e10` / `sudo` — none
- `scripts/ed_session/sampler-checklist.sh` / `shell:de942b5b57d7afcb` / `sudo` — none
- `scripts/ed_session/sampler-checklist.sh` / `shell:f51fe12c0e234e10` / `sudo` — none
- `scripts/floor_reconciliation_receipt.py` / `build_receipt:685741836c33233b` / `shutdown` — none
- `scripts/g10_clock_step_control.py` / `<module>:1c72b153e0c2b8c5` / `sudo` — none
- `scripts/g10_clock_step_control.py` / `<module>:1c72b153e0c2b8c5` / `systemsetup` — none
- `scripts/g10_clock_step_control.py` / `<module>:650aa89ad0060b30` / `sudo` — none
- `scripts/g10_clock_step_control.py` / `<module>:668741c8bca9cef3` / `systemsetup` — none
- `scripts/g10_clock_step_control.py` / `real_run:3cfd8a14456eaf86` / `kill` — none
- `scripts/gen_derivation_night.py` / `render_quiet_runsheet:6270da078abfee31` / `shutdown` — none
- `scripts/gen_derivation_night.py` / `render_region:4eb4fa4d76520b72` / `kill` — none
- `scripts/joulewise-network-time.sudoers` / `shell:3ba6f6bbbadb0e3d` / `systemsetup` — none
- `scripts/launch_align_r0.py` / `main:0ad70fd971de1688` / `kill` — none
- `scripts/launch_align_r0.py` / `main:502ee0a584ce0b0b` / `launchctl` — none
- `scripts/launch_align_r0.py` / `main:541443a289d468bd` / `pmset` — none
- `scripts/launch_align_r0.py` / `preflight:1ce72457247d2496` / `pmset` — none
- `scripts/launch_align_r0.py` / `sleep_display:4d225195f0918490` / `pmset` — none
- `scripts/launch_align_r0.py` / `sleep_display:4d225195f0918490` / `sudo` — none
- `scripts/magistrate_watchdog.py` / `reap_handoff:2bda9b4dfbabfdb1` / `kill` — none
- `scripts/magistrate_watchdog.py` / `reap_handoff:34cf09955fae122f` / `kill` — none
- `scripts/night_chains/align_r1_rehearsal.zsh` / `shell:559db711a9b0c2ad` / `pmset` — none
- `scripts/night_chains/align_r1_rehearsal.zsh` / `shell:559db711a9b0c2ad` / `sudo` — none
- `scripts/offload_setup_air.sh` / `shell:1f64604ba090b8c5` / `sudo` — none
- `scripts/offload_setup_air.sh` / `shell:2a7be42bc6f63863` / `launchctl` — none
- `scripts/offload_setup_air.sh` / `shell:49e71a468b3ef83a` / `pmset` — none
- `scripts/offload_setup_air.sh` / `shell:e4abe0777b8523db` / `launchctl` — none
- `scripts/offload_window.py` / `init_store:c812e50b854ee2fa` / `sudo` — none
- `scripts/offload_window.py` / `run_process_group:837c24cde7987e2e` / `kill` — none
- `scripts/prewindow_check.sh` / `shell:319adc4f9aae57fc` / `pmset` — none
- `scripts/quiet_guard_privileged.py` / `<module>:49a7fac5d28f70b9` / `python-isolated` — none
- `scripts/quiet_mac_prep.sh` / `shell:2c084710e3f07ede` / `pmset` — none
- `scripts/quiet_mac_prep.sh` / `shell:2f724750112f5cca` / `pmset` — none
- `scripts/quiet_mac_prep.sh` / `shell:be6240fd1089daca` / `sudo` — none
- `scripts/quiet_mac_prep.sh` / `shell:d2f3f88bbe41d978` / `pmset` — none
- `scripts/quiet_mac_prep.sh` / `shell:dffbcfb056ceb5b2` / `pmset` — none
- `scripts/quiet_window_clock.sh` / `shell:0c5d9b68fa63b3c5` / `sudo` — none
- `scripts/quiet_window_clock.sh` / `shell:0c5d9b68fa63b3c5` / `systemsetup` — none
- `scripts/quiet_window_clock.sh` / `shell:415302ef4b6ed3e7` / `sudo` — none
- `scripts/quiet_window_clock.sh` / `shell:415302ef4b6ed3e7` / `systemsetup` — none
- `scripts/rehearse_b5_real.py` / `<module>:0110c2c503cb7ee3` / `pmset` — none
- `scripts/rehearse_b5_real.py` / `<module>:290cdce8fc49b1ce` / `pmset` — none
- `scripts/rehearse_b5_real.py` / `<module>:290cdce8fc49b1ce` / `sudo` — none
- `scripts/rehearse_b5_real.py` / `<module>:290cdce8fc49b1ce` / `systemsetup` — none
- `scripts/rehearse_b5_real.py` / `<module>:90623fec8b16d827` / `systemsetup` — none
- `scripts/rehearse_b5_real.py` / `<module>:a4e73e824dacbb98` / `pmset` — none
- `scripts/rehearse_b5_real.py` / `write_shims:9d2be7ac15275504` / `pmset` — none
- `scripts/replay_powermetrics_frames.py` / `<module>:e49f8318abcc4dc7` / `sudo` — none
- `scripts/run_campaign.py` / `_HazardMemberWatch:90245e2d68a9c652` / `sudo` — none
- `scripts/run_campaign.py` / `_hazard_is_sampler_wrapper:24e5e1c2bbef5653` / `sudo` — none
- `scripts/run_campaign.py` / `_hazard_is_sampler_wrapper:e5bb6ad9693e5414` / `sudo` — none
- `scripts/run_campaign.py` / `campaign_environment_preflight:817dc28f0bb99139` / `pmset` — none
- `scripts/run_campaign.py` / `campaign_environment_preflight:9d2be7ac15275504` / `pmset` — none
- `scripts/run_campaign.py` / `parse_args:c9736f69220860b6` / `pmset` — none
- `scripts/sample_quiet_predicate_evidence.py` / `PowerRecorder.finish:2bda9b4dfbabfdb1` / `kill` — none
- `scripts/sample_quiet_predicate_evidence.py` / `ReplayRecorder:d00411e5078c765a` / `kill` — none
- `scripts/sample_quiet_predicate_evidence.py` / `collect:2bda9b4dfbabfdb1` / `kill` — none
- `scripts/sample_quiet_predicate_evidence.py` / `power_argv:004ec7e0892e7838` / `sudo` — none
- `scripts/sample_quiet_predicate_evidence.py` / `power_argv:24e5e1c2bbef5653` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:04589b88af92eafd` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:093e123630c3d0e6` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:09abadbb544acfc7` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:280550155add0c09` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:2f30cd0eb198bf11` / `python-isolated` — none
- `scripts/setup_quiet_guard.sh` / `shell:2f30cd0eb198bf11` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:3d7d782275918d1d` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:46e257a7ce5ff0de` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:7a34ce389c3cce69` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:8048f46057ac3668` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:873ca084e5fab8de` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:8ccfab54ad230f77` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:b560cfee718c9a9a` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:c7155b1c1a0004e7` / `sudo` — none
- `scripts/setup_quiet_guard.sh` / `shell:ca1dc62ccac4efb6` / `python-isolated` — none
- `scripts/setup_quiet_guard.sh` / `shell:ca1dc62ccac4efb6` / `sudo` — none
- `scripts/size_b5_window.py` / `<module>:6dcc33183e199cf3` / `shutdown` — none
- `scripts/size_b5_window.py` / `derive_document:04de202a40a1e992` / `shutdown` — none
- `scripts/validate_powermetrics_fiducial.py` / `main:004ec7e0892e7838` / `sudo` — none
- `scripts/validate_powermetrics_fiducial.py` / `main:24e5e1c2bbef5653` / `sudo` — none
- `scripts/validate_powermetrics_fiducial.py` / `main:541443a289d468bd` / `pmset` — none
- `scripts/validate_powermetrics_fiducial.py` / `main:922c47fe7171913e` / `pmset` — none
- `scripts/validate_powermetrics_fiducial.py` / `main:99396a2a5503574e` / `pmset` — none

## Keyword-candidate modules not reached (time budget; lead runs these)

- `tests.align.test_harvest_off`
- `tests.align.test_harvest_off_review_sol1`
- `tests.align.test_harvest_off_review_sol2`
- `tests.align.test_km003c`
- `tests.align.test_measurement_view_identity`
- `tests.align.test_merge_c84_sol`
- `tests.align.test_pilot2_round1`
- `tests.align.test_pilot3`
- `tests.align.test_pilot4`
- `tests.align.test_r0_host`
- `tests.align.test_r11_delta3_sol1`
- `tests.align.test_r11_delta3_sol2`
- `tests.align.test_r11_delta4_sol1`
- `tests.align.test_r11_delta4_sol2`
- `tests.align.test_r11_delta5_sol1`
- `tests.align.test_r11_delta5_sol2`
- `tests.align.test_r11_delta6_sol1`
- `tests.align.test_r11_delta6_sol2`
- `tests.align.test_r11_delta_sol1`
- `tests.align.test_r11_delta_sol2`
- `tests.align.test_r1_rehearsal`
- `tests.align.test_r1_round5_exec_review`
- `tests.align.test_r1_round7_install`
- `tests.align.test_r1_round7_power`
- `tests.align.test_r1_round8`
- `tests.align.test_r1_runtime_e2e`
- `tests.align.test_smc_quiet`
- `tests.align.test_smoke_delta3_sol1`
- `tests.align.test_smoke_delta3_sol2`
- `tests.align.test_smoke_delta4_sol1`
- `tests.align.test_smoke_delta4_sol2`
- `tests.align.test_smoke_delta_sol1`
- `tests.align.test_smoke_delta_sol2`
- `tests.align.test_smoke_review_sol1`
- `tests.align.test_smoke_review_sol2`
- `tests.align.test_timing_receipts`
- `tests.align.test_timing_receipts_opus_witnesses`
- `tests.align.test_v4_cadence`
- `tests.align.test_v4_dc_sealing`
- `tests.align.test_v4_disclosure_only_desk`
- `tests.align.test_v4_next_arm_packet`
- `tests.align.test_v4_next_arm_packet_opus_witnesses`
- `tests.align.test_v4_powermode_record`
- `tests.align.test_v4_r11`
- `tests.align.test_v4_receipt_tiers`
- `tests.align.test_v4_record_binding`
- `tests.align.test_v4_series_e2e`
- `tests.align.test_v4_series_r20`
- `tests.align.test_v4_w1_blockers`
- `tests.align.test_v4_w1_plan`
- `tests.align.test_v4_w1_synthetic`
- `tests.align.test_w1_kit_r10`
- `tests.align.test_w1_prequal`
- `tests.align.test_w1_smoke`
- `tests.align.test_w1bm_sol1`
- `tests.align.test_w1bm_sol2`
- `tests.align.test_window_timing`
- `tests.b6.test_b6_plan_render`
- `tests.b6.test_capture_screen_reachability`
- `tests.b6.test_desk_resume_finalize`
- `tests.b6.test_lane_adapters`
- `tests.b6.test_round2_review_fixes`
- `tests.flags.test_flags_catalog`
- `tests.flags.test_flags_exclusions`
- `tests.flags.test_flags_import_graph`
- `tests.flags.test_number_coverage`
- `tests.hazards.test_arm`
- `tests.hazards.test_arm_identity`
- `tests.hazards.test_import_graph`
- `tests.hazards.test_smc_enumeration`
- `tests.test_acc_25g83_rev6`
- `tests.test_align_pilot_session`
- `tests.test_arm_census`
- `tests.test_arm_readiness`
- `tests.test_arm_readiness_evidence`
- `tests.test_arm_readiness_evidence_t0`
- `tests.test_arm_readiness_registry`
- `tests.test_arm_readiness_schemas`
- `tests.test_arm_retry`
- `tests.test_b5_driver`
- `tests.test_b5_driver_p2`
- `tests.test_b5_driver_p3`
- `tests.test_b5_plan`
- `tests.test_b6_machine_test`
- `tests.test_battery_float`
- `tests.test_battery_float_consumers`
- `tests.test_battery_float_sweep`
- `tests.test_bench_replay_entrypoint`
- `tests.test_capture_t0_anchor_positive_control`
- `tests.test_capture_t0_step`
- `tests.test_controller`
- `tests.test_environment`
- `tests.test_evidence_arm_sequence`
- `tests.test_evidence_night`
- `tests.test_experiment`
- `tests.test_g10_clock_step_control`
- `tests.test_gate_prune_integration`
- `tests.test_gen_derivation_night`
- `tests.test_gen_evidence_night`
- `tests.test_gen_g2a_window`
- `tests.test_harvest_b5_window`
- `tests.test_harvest_g2a_window`
- `tests.test_harvest_window`
- `tests.test_launch_context_no_qos_override`
- `tests.test_launch_window`
- `tests.test_launch_window_realization_recheck`
- `tests.test_live_hw_optin`
- `tests.test_magistrate_watchdog`
- `tests.test_magistrate_watchdog_b6`
- `tests.test_magistrate_watchdog_span`
- `tests.test_magistrate_watchdog_v5`
- `tests.test_night_gate`
- `tests.test_night_kinds`
- `tests.test_offload_window`
- `tests.test_prewindow_check`
- `tests.test_promote_calibration_candidate`
- `tests.test_quiet_admission`
- `tests.test_quiet_predicate_campaign`
- `tests.test_receipt_histsem`
- `tests.test_rev6_custody_plan_id`
- `tests.test_rev6_prior_start_plan_id`
- `tests.test_run_night_probe_cadence`
- `tests.test_run_night_probe_worker_cadence`
- `tests.test_sample_quiet_predicate_evidence`
- `tests.test_scheduler_gates`
- `tests.test_t0_anchor_positive_control`
- `tests.test_t0_rehearsal`
- `tests.test_v5_arm_abort`
- `tests.test_v5_block4_replay`
- `tests.test_v5_block4_x1`
- `tests.test_v5_block4_x10`
- `tests.test_v5_block4_x12a`
- `tests.test_v5_block4_x12b`
- `tests.test_v5_block4_x16`
- `tests.test_v5_block4_x2`
- `tests.test_v5_block4_x4`
- `tests.test_v5_block4_x7`
- `tests.test_v5_block4_x9`
- `tests.test_v5_pack_rehearsal`
- `tests.test_v5_qualification_plan`
- `tests.test_v5_s1_desk_closeout`
- `tests.test_v5_s1_qualification`
- `tests.test_w1_reliability`
- `tests.test_w1_reliability_r7`

## Final diff and local commits

All bound paths have +0 / -0 lines. AST parsing, git diff --check, the seam schema and the unchanged inventory identities passed.

| Changed path | Added / removed |
| --- | ---: |
| `docs/run_reports/2026-11-11-w1-host-guard-leaks.txt` | +1 / -0 |
| `scripts/shard_tests.py` | +2 / -0 |
| `scripts/test_timings.json` | +2 / -0 |
| `tests/__init__.py` | +1 / -0 |
| `tests/_host_guard_site/sitecustomize.py` | +25 / -0 |
| `tests/host_command_guard.py` | +261 / -0 |
| `tests/host_command_sites.json` | +2210 / -0 |
| `tests/test_host_command_guard.py` | +176 / -0 |
| `tests/test_host_command_sites.py` | +143 / -0 |
| `tests/test_post_window_unstrand.py` | +23 / -8 |
| `docs/run_reports/2026-11-11-w1-host-guard.md` | New handoff report (this file) |

Code/scan commits, in order (all local, assigned branch only):

- 09325f171 test: install suite-wide in-process host command refusal guard
- 7f59a46c2 test: record first guarded legacy scan before fixture repairs
- 7005836fb test: propagate host guard to child Python and inventory command sites
- 15b3c4f8d test: return acknowledged guard refusals without a test failure
- 6928358fe test: record guarded unstrand caffeinate leak before repair
- 4217aa0ae test: fake unstrand caffeinate and restrict guard removal to witnesses

This report is committed separately after final review. Next exact step: lead rules on the PYTHONPATH grep exception, cold-reviews the seven requested test artifacts and runner import seams, then reruns the capped modules and not-reached candidates with the guard installed. Preserve every new refusal for the operational notice; keep native production gates separate.
