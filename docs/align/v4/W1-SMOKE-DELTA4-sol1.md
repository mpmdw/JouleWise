W1 smoke delta4 review, independent Sol seat 1. 2026-11-08.

Reviewed candidate 80bbfa2cd on align/2026-11-08-smoke-delta4-sol1. The requested
range is 8ebc175c3..80bbfa2cd with v4-r11 merge content excluded; the substantive
fix review is therefore 90d3f8dc7..80bbfa2cd. Authority is the brief's threat-model
ruling, W1-SMOKE-AGREEMENT.md section 9, the two delta3 reports, and repository
instructions. Mission M0, orchestration and targeted decision-log authority were
read; the active stop card is NONE. The requested branch already existed at the
candidate and was clean. Coordination state remains lead-owned.

MEDIUM, D4-1: F6 leaves newly imported production functions bound to the smoke
runner after prepare. At w1_smoke.py:1016-1032, _prepare_budget snapshots loaded
functions, patches their defaults, then patches subprocess.run. prepare_smoke
imports scripts.align_v4_session and scripts.align_pilot_session afterward. Their
_probe_meter_live(runner=subprocess.run) and desk(run=subprocess.run) defaults
capture the patched callable and are absent from the restoration callbacks.
Both successful prepare and a ValueError after those imports leave these defaults
changed, although module-level subprocess.run is correctly restored.

Failure scenario: an operator or harness calls smoke preparation in a reusable
interpreter, then calls a production meter probe or desk through the imported
module. The later command inherits the old smoke deadline and TMPDIR identity
checks. The cold-interpreter witnesses advance the synthetic clock beyond that
deadline and call the real _probe_meter_live with all commands intercepted: it
raises BudgetExpired before issuing any command. Both defaults remain changed;
the command-call count is zero. This requires ordinary lazy imports and later
reuse, without a pathname race. Witnesses are
ColdImportBudget.test_lazily_imported_defaults_are_restored_after_success and
test_lazily_imported_defaults_are_restored_after_failure in
tests/align/test_smoke_delta4_sol1.py. A fresh CLI child does not share these
Python objects, and I found no existing production caller that reuses this
interpreter after SmokeRunner.run. That limits the demonstrated operational
impact; this is not evidence that a later independently launched arm is poisoned.

LOW/NOTE, D4-2: F6's patch has process-wide scope and captured callbacks outlive
its context. Failure scenario: a benign worker in the same interpreter calls
subprocess.run while another thread prepares smoke. Its requested 600-second
timeout becomes 120 seconds, the smoke's remaining budget. A worker retaining
the callback during prepare can also call it after the context has restored
subprocess.run; that retained callback still raises BudgetExpired when the old
deadline expires. Both cases are deterministic, event-synchronized witnesses,
PrepareBudget.test_unrelated_thread_keeps_its_timeout_during_prepare and
test_thread_callback_captured_during_prepare_outlives_the_scope. All commands
in these witnesses are fake and both fixture threads are joined. I did not find
the shipped prepare starting such a worker, so this is a same-process embedding
limitation, not a new HOLD against the documented dedicated CLI. A separate
process, including the existing blinded analysis job, cannot see this monkeypatch.

The named delta3 safety fixes otherwise withstand their witnesses. F3/D3-1 now
pins runner writes and directory operations to the established descriptor.
Both old modules pass their finalize, recovery-record, fault-session,
detached-log and link controls. The new anchor control moves the parent and
creates a replacement directory without planting any link: bytes still land
under the original pinned directory. The broader production prepare/installer
pathname residual remains accepted. No adversarial-only rename race is promoted
to HOLD.

D3-2 correctly adopts publication before the install record exists and cleans
the owned job on the synthetic host; another plan remains untouched. D3-3's
grouped_run closes the descendant-timeout witnesses. New real, tiny child-group
controls also prove cleanup when the leader exits successfully or with status 7
and its descendant has closed its output pipes. Binary stdout, CalledProcessError
and TimeoutExpired behavior are preserved in the exercised cases. The isolation
runner verifies TMPDIR in its finally block. D3-4 binds the unique --plan option;
the positive evidence bundles and wrong-plan mutations pass their expected
admission/refusal assertions. Its plist shape matches the tracked production
template. D3-5 refuses FIFOs without blocking, and D3-6 completes injected short
writes. A new zero-progress control raises OSError instead of spinning.

F6 closes the original capacity-probe budgeting gap: the old witness now sees a
timeout within the five seconds remaining. New controls cover omitted, None,
shorter and longer timeouts, expired-budget refusal, binary output and forwarded
command options. For functions present in the snapshot, subprocess.run,
important_capacity's keyword defaults, os.environ['TMPDIR'] and tempfile.tempdir
are restored after normal return, ValueError, BudgetExpired, KeyboardInterrupt
and SystemExit from the prepare body. These passing controls do not establish
restoration of functions imported after the snapshot or escaped references;
D4-1/D4-2 exercise those separately.

The failed-main-arm return change is consistent with the callers. The actual
foreground CLI forwards run()'s result, and its __main__ uses SystemExit.
FixControls.test_failed_main_arm_reaches_the_cli_as_exit_one drives the CLI with
a real SmokeRunner and a synthetic refused main install: main() returns 1,
the arm row is fail, the final log code is 1 and the anchor closes. Existing
refused-main tests inspect failure rows without requiring zero. Detach's zero
acknowledges spawning; it cannot convey the eventual child's status. The documented
parse command remains the complete qualification verdict, including failures
beyond the main arm; run() is not newly claimed to equal parse's status.

Verification used Python 3.13, with TMPDIR=/private/tmp and -B. Each unittest
command ran separately and sequentially. The exact invocations were
`TMPDIR=/private/tmp python3.13 -B -m unittest -v tests.align.test_smoke_delta3_sol1`
(16 tests OK, 17.540 seconds),
`TMPDIR=/private/tmp python3.13 -B -m unittest -v tests.align.test_smoke_delta3_sol2`
(15 tests OK, 350.515 seconds, including the 358-mutation production-arm probe),
and
`TMPDIR=/private/tmp python3.13 -B -m unittest -v tests.align.test_smoke_delta4_sol1`
(12 tests: eight pass and four intended property failures, 2.712 seconds;
no errors, skips or expected failures). Total unittest time was 370.767 seconds.
The four failures are the two lazy-import scenarios and the two thread scenarios
described above. They remain visible as ordinary assertion failures for the fixer.
`PYTHONPYCACHEPREFIX=/private/tmp/jw-smoke-delta4-sol1-pycache python3.13 -B -m compileall -q joulewise tests`
exited 0, and the staged diff whitespace check passed. The full suite was not run,
as required by the brief. Python 3.11 was not separately exercised.

Only tests/align/test_smoke_delta4_sol1.py and this report are changed. The witness
commit is 1b402857f, test(align): witness delta4 prepare scope leaks; this report
is the following documentation commit. No production fix or coordination-file
edit is included. This review stayed offline and synthetic: configured home
roots were replaced before runner construction, plist fixtures used patched
synthetic homes, and all real child processes belonged to the tests. No model
weights, measurement data, real restricted directory, real plist or launchd
operation was used. Nothing was pushed, and no peer agent or consult was invoked.

Next exact step: replace the global prepare patch with explicit runner propagation
or a bounded dedicated preparation process, then rerun the new module and both
delta3 modules separately. Merely restoring subprocess.run or adding more
pre-imports leaves captured-reference risks. The lead should settle whether
in-process reuse/threaded embedding is supported or explicitly excluded; no such
scope exclusion is currently enforced by the API. I recommend fixing the scope
instead of relying on an undocumented convention.

Actual native smoke wall time, launchd ownership/teardown, meter restart and
request-overlap behavior remain unverified and belong to the lead in a clean,
agent-free native gap. No MLX behavior changed or ran here. If native MLX
qualification is required, its existing tests.align.test_cache_checkpoint_native,
tests.align.test_r0_mlx_native, tests.align.test_thermal_mlx and MLX case in
tests.align.test_decode_budget still require the provisioned host and their
existing opt-ins outside this sandbox.

Verdict: ADMIT-WITH-FIXES. The delta3 host/write/process safety failures are closed
for the exercised scenarios under the binding threat model. F6's original budget
hole is closed, but its restoration/scoping claim is incomplete. D4-1 needs a
fix for reusable-interpreter safety; D4-2 documents the related threaded limit.
I found no new demonstrated HOLD path in the documented fresh-process smoke CLI.
This verdict does not certify the outstanding native hardware gate.
