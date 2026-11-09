# W1 smoke delta 3 — independent Sol seat 2

2026-11-08. Reviewed `d48ab1f77..8ebc175c3`, excluding the v4-r11 merge
content. The smoke changes are principally `d2c9749f9` and `0762c3b9f`;
the fix map is §8 of `W1-SMOKE-AGREEMENT.md`. Branch:
`align/2026-11-08-smoke-delta3-sol2`.

**Verdict: HOLD.** The exact earlier witnesses can pass while an installer
interrupted before saving its session record still escapes cleanup. Runner
writes also retain isolation holes. The deadline bundle improves validation
but does not actually bind the `--plan` options. Findings below have executable
synthetic witnesses in `tests/align/test_smoke_delta3_sol2.py`.

I accept the lead's residual: concurrent renames during production prepare's
or the installer's own pathname writes, and a child's pathname resolution of
TMPDIR after the check, are outside the guarantee. Those are not findings.
F2/F3 concern the smoke runner's own writes. No other review seat was consulted.

## Findings

### F1 — HIGH: pending ownership cannot recognize its own published plan

`joulewise/align/w1_smoke.py:993` calls `published_plan_owner()` while
`self.installed` is still `None`. That function takes the expected plan solely
from `self.installed` (line 1025). Its return therefore cannot equal
`ours:<pending-plan>` on the fallback branch at line 1009.

Failure scenario: the installer publishes/loads this smoke's job, then times
out before `bytes_h_session.install` saves `state['install']`. That save occurs
after the installer subprocess returns (`scripts/bytes_h_session.py:443`).
Reconciliation logs `nothing-installed`; finally skips uninstall and leaves
the job loaded. The witness reproduces the missing session record, rather
than the earlier fixtures' already-recorded successful install.

Witness: `LifecycleWitnesses.test_published_own_plan_without_session_install_record_is_cleaned`.
The different-plan control passes: a published plist naming another plan is
left untouched. Repair should compare the pending identity directly and keep
that refusal; do not remove the ownership check.

### F2 — HIGH: finalize and recovery writes still follow symlinks

`joulewise/align/w1_smoke.py:1069` and line 1082 use `Path.write_text`, bypassing
`safe_write`. A symlink at `teardown-unproven.json` or `finalize.json` overwrites
the target. Both witnesses overwrite disposable protected-root sentinel bytes.
These files are written after the last arm isolation check; a check before
arming does not protect their later use.

Witnesses: `WriteWitnesses.test_finalize_cannot_follow_an_output_symlink` and
`test_unproven_teardown_cannot_follow_an_output_symlink`.

The claim that every runner write uses `safe_write` is also too broad by
inspection: `_receipt_clone` appends through `open('ab')` (line 866), isolate
writes its `.pth` through `write_text` (line 450), and `detach` opens its output
log through ordinary `open` (line 1359). The two output receipts above are the
independently exercised cases, not a claim that every remaining site has been
exercised. Audit all runner-owned writes when fixing this.

### F3 — HIGH: safe_write follows ancestors of its base directory

`_open_beneath` reopens `base` by absolute pathname at line 83. `O_NOFOLLOW`
there protects only the final component of that open. The descriptor walk
protects descendants of whichever directory that open happened to reach.

Failure scenario: after destination validation, rename the parent of the smoke
directory and replace that parent with a symlink into a synthetic production
root containing an equally named smoke directory. `safe_write` opens the
replacement directory and creates a file there. No production prepare,
installer, or child TMPDIR write is involved in this witness.

Witness: `WriteWitnesses.test_base_ancestor_replacement_cannot_redirect_safe_write`.
Pin the owned base directory's descriptor/identity at establishment; do not
re-establish its identity by following an absolute pathname on every write.

### F4 — HIGH: the new isolation runner leaves timeout descendants alive

`SmokeRunner.isolate_run` uses `subprocess.run` at line 735, bypassing
`bounded_run`. `start_new_session=True` establishes a group but does not make
`subprocess.run` kill that group on timeout.

Failure scenario: an isolation command spawns a descendant which closes its
output pipes and continues work. At timeout only the leader is killed. The
test's real, tiny descendant continues appending heartbeat bytes after the
timeout; the test then explicitly kills only its fixture-owned group. Such a
descendant is untracked load after the smoke aborts.

Witness: `LifecycleWitnesses.test_isolate_timeout_kills_its_descendant`.
Use the existing group timeout/reap/proof path for isolation too. This does
not allege that a particular native git/venv command has already leaked.

### F5 — MEDIUM: deadline evidence checks argv membership, not --plan

`joulewise/align/w1_prequal.py:1117` and line 1119 accept the copied plan path
anywhere in the plist and installer argument arrays.

Failure scenario: take a valid production-plan bundle, change the plist's
`--plan` to another path, and retain the copied path as the value of
`--courier-bin`. The deadline gate still PASSes. Changing the install record
in the same way also PASSes. The copied plan has matching bytes, hash and
custody; it is the launch/installer option binding that is wrong. These are
schema-shaped synthetic evidence mutations, not native installation claims.

Witnesses: `AdmissionWitnesses.test_deadline_binds_the_plan_option_not_arbitrary_argument_membership`
and `test_deadline_binds_the_installer_plan_option`.
Require exactly one properly parsed `--plan` option naming the session plan
in each relevant argv, with the intended command shape.

### F6 — MEDIUM: production prepare still has commands outside the budget runner

Passing `run=self.prepare_run` at `w1_smoke.py:772` does not reach every command.
The real `bytes_h_session.prepare` calls `disk_snapshot`; its default capacity
callback is `important_capacity`, whose own default is `subprocess.run`. Its
osascript timeout remains 30 seconds (`scripts/bytes_h_session.py:281`).

Failure scenario: preparation starts with 65 seconds remaining, passing the
ordinary 60-second entry reserve. Synthetic sizing work spends 60 seconds.
The subsequent real capacity-probe path still requests a 30-second subprocess
timeout with only five seconds left. The witness intercepts that subprocess
before it runs, so no osascript or real capacity probe executes. The after-
prepare deadline check cannot prevent this overrun. The kit's direct
`subprocess.run` in `align_v4_kit.frozen` also has no timeout by inspection.

Witness: `LifecycleWitnesses.test_production_prepare_capacity_probe_uses_remaining_budget`.
Propagate the deadline runner through all preparation callbacks, or bound the
whole preparation process. This is independent of the accepted pathname-write
residual.

### F7 — MEDIUM: safe_write can block before checking the file type

The leaf open at `w1_smoke.py:95` uses blocking `O_WRONLY`; the regular-file
check occurs afterward. A FIFO at an output path blocks without a reader.
The smoke budget cannot interrupt that blocking open.

Failure scenario: `safe_write` encounters a FIFO where its log or evidence
file should be. The fixture-owned child blocks until the test's one-second
group timeout kills it; the nonregular file is never refused by the helper.

Witness: `WriteWitnesses.test_fifo_is_refused_without_blocking_before_fstat`.
Use nonblocking open/type verification before accepting a leaf. No naturally
occurring FIFO in an actual smoke was observed.

### F8 — LOW: safe_write silently accepts a short write

`w1_smoke.py:117` calls `os.write` once and ignores the returned byte count.
Unlike the former buffered file writes, that does not promise all bytes were
written. A legal positive short write leaves a truncated log/plan/packet while
the helper returns success.

Witness: `WriteWitnesses.test_short_write_does_not_silently_truncate_evidence`.
It uses a real regular file and limits each syscall to two bytes: the helper
writes `co` instead of `complete evidence\n`. Loop until the buffer is written
and handle a zero-byte result. This is injected syscall behavior; I did not
observe spontaneous disk-related truncation.

## Prior finding disposition

| Prior finding | Assessment at the reviewed head |
|---|---|
| D1 / D2-1 detached entry before validation | Destination validation is now before mkdir/spawn. Earlier detached-entry witnesses pass. Later write safety is covered separately by F2/F3. |
| D2 / D2-1 check/write race | Named reducer/staging/TMPDIR re-attacks are closed. Final/descendant symlinks and multi-link leaf files are refused by the helper. The complete runner guarantee remains open: F2/F3/F7. Accepted production/child residual is not raised. |
| D7 launch bindings and read-only exemption | Closed for the named re-attacks; all path-typed launch bindings feed the write-locator check, outside the read-only exception. |
| D3 / D2-2 isolate/prepare budget | Monotonic budget and wall-time separation are correct; expired-budget guards pass. Completeness remains open: F4/F6/F7. |
| D4 / D2-3 install timeout | The already-recorded-install witness is fixed. Publication before install-state save remains open: F1. Another-plan refusal passes. |
| D5 / D2-4 forged deadline plan | Lone/declaration plans, invalid NightPlans and wrong hashes are now refused; span comes from hazard_window. The installed identity binding remains incomplete: F5. |
| D6 / D2-5 missing chain leaves | See packet verification below; no new HOLD finding for the mutation walker. |

## Verification and handoff

All unittest invocations below ran sequentially, one module per process,
under Python 3.13 with `-B` and
`TMPDIR=/private/tmp/jw-smoke-delta3-sol2.0xfMqq`. No startup shim was needed.

| Command after `python3.13 -B -m unittest` | Result | Seconds |
|---|---|---:|
| `-v tests.align.test_smoke_delta3_sol2` | 14 tests: 5 pass, 9 intended property failures, no errors/skips/expected failures | 282.518 |
| `-v tests.align.test_smoke_delta3_sol2.LifecycleWitnesses.test_production_prepare_capacity_probe_uses_remaining_budget` | 1 intended property failure: 30-second timeout with 5 seconds remaining | 0.390 |
| `tests.align.test_smoke_delta_sol1` | 15 tests OK | 3.344 |
| `tests.align.test_smoke_delta_sol2` | 15 tests OK | 13.217 |
| `tests.align.test_w1_prequal.PortedSolTests.test_deadline_is_bound_to_the_installed_plan_plist_and_session` | 1 test OK | 1.372 |

The capacity witness was added after the corrected 14-test invocation had
started, then run separately. Together these exercise all 15 tests in the
delivered module: 5 pass and 10 fail at the intended property assertions.
The first exploratory invocation took 4.255 seconds and had four harness
errors because the synthetic projection directory was not a Git checkout.
Supplying an explicit synthetic Context commit corrected those errors. They
are not product findings. Total unittest time, including that invocation,
was about 305 seconds, well below 20 minutes.

The packet test uses the real production arm and producer, with fake host
commands: the admitted control and all **358 mutations** behave as expected,
including the zero-capture C3 hole. An independent recursive leaf walk
checks change/remove coverage for every check entry and every element of
`window_chain` and `calibration_windows`; it confirms the exact nested
`checks.record_committed.pushed_tip` exemption is excluded. This closes D6 /
D2-5 for the present packet schema. The earlier tests also detect stand-in
arms that ignore a later chain leaf or one chain hash. A fixed count alone
would not establish that coverage.

`PYTHONPYCACHEPREFIX=/private/tmp/jw-smoke-delta3-sol2.0xfMqq/pycache
python3.13 -B -m compileall -q joulewise tests` exited 0. `git diff --check`
passed. No full suite or PREQUAL campaign was run; the full suite is forbidden
by the brief, and this review uses the relevant delta modules and focused
deadline/packet checks instead.

Logs remain in the synthetic evidence directory above:

| Log | SHA-256 |
|---|---|
| `delta3.log` | `12819ff6912271ce0627031e38376ae4fc1f09f1ce1f4a44efb0c902722f16cd` |
| `prepare-budget.log` | `6a788c2c4a9e33f190b5a162c2d0abda4a18d65cbd685f4c5a9264625b00c8c0` |
| `delta-sol1.log` | `bd2a6cc33765d67127fb54903dbaadb7efbdd7c5bcf09b0eb305cfb0116baf70` |
| `delta-sol2.log` | `94ef76dbc7bef2415dc42728fea8e471eb334f9f95947e55f13f574ca3edfbb1` |
| `deadline-controls.log` | `9340af90cbb330fe12c17160cc8489d3d2a18b6ffa591e0caf37cb9a673e1410` |

Only this report and the new witness module are deliverables. No production
code or coordination state is changed. The requested branch already existed
at `8ebc175c3` on intake and was clean. No network, weights, real measurement
data, real plist, launchd, block-5 analysis, restricted-directory access,
consult or sub-agent was used. All plist reads/writes in the new module use
a patched synthetic home. Configured production-root text is replaced before
the smoke runner can resolve it.

The witness commit is `f0758e25d` (`test(align): witness W1 smoke delta3 safety
gaps`). This report is the following documentation commit on the same local
branch. Nothing is pushed. No open policy question is needed to reproduce
F1–F8; their severity and acceptance remain the lead's disposition.

Native wall time, actual launchd teardown/ownership, KM003C restart/DC salvage,
and real request-overlap flags remain unverified. After fixes and targeted
rechecks, the lead must run the native smoke in a clean magistrate-controlled
MBP gap with agents absent during collection. Existing native MLX qualification
(`tests.align.test_cache_checkpoint_native`, `tests.align.test_r0_mlx_native`,
`tests.align.test_thermal_mlx`, and the MLX case in `tests.align.test_decode_budget`)
also requires a provisioned host outside this sandbox and its existing opt-ins.
No new MLX behavior was changed or validated here.

Next exact step: disposition F1–F8, fix the accepted findings in the smoke kit,
and rerun the new witness module plus both previous delta modules separately.
The HIGH findings are sufficient for HOLD; the LOW short-write finding does
not depend on a new policy ruling. Severity is a review judgment, while the
individual synthetic failure scenarios are reproducible.
