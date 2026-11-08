# W1 smoke delta4 review — independent Sol seat 2

2026-11-08. Reviewed candidate `80bbfa2cd`, specifically the smoke fix commit
`80bbfa2cd^..80bbfa2cd` within `8ebc175c3..80bbfa2cd`; the v4-r11 merge
`90d3f8dc7` is excluded. Authority is the brief, its operator/host/functional
threat-model ruling, and `W1-SMOKE-AGREEMENT.md` section 9. Branch:
`align/2026-11-08-smoke-delta4-sol2`. The workspace began clean on that branch.

D4-S2-1 — MEDIUM: production functions imported during prepare retain the
smoke's runner after prepare exits. `_prepare_budget` snapshots only the
modules loaded at `w1_smoke.py:1016`, then replaces `subprocess.run` at line
1031. The ordinary cold path imports `scripts.align_v4_session` and
`scripts.align_pilot_session` inside `prepare_smoke`, after that snapshot.
Their `_probe_meter_live(..., runner=subprocess.run)` and
`desk(..., run=subprocess.run)` defaults therefore capture the temporary
wrapper, but receive no restoration callback. The global `subprocess.run`
does restore; both production defaults do not.

Failure scenario: a Python control process prepares the smoke and later uses
the production live-meter probe or desk in the same process. Those functions
continue to use the earlier smoke's deadline and TMPDIR checks. Once that
deadline has expired, their ordinary subprocess invocation raises
`BudgetExpired` before running. This requires an ordinary cold import and a
later function call, with no link planting or rename race. Both a synthetic
successful prepare and a failed prepare leave the stale defaults. The two
`PrepareBudget.test_cold_production_import_defaults_restore_after_*` witnesses
run in fresh interpreters. The success case returns synthetic staged state
after importing the production modules; the failure case enters the real
`prepare_smoke` and stops at an injected callback before production preparation. Both inspect
the two real production defaults and invoke the real `_probe_meter_live`
afterward against a tiny synthetic monitor script: it raises the stale smoke
budget exception. No real monitor or meter is used. These are same-process
API failures; I did not establish a later consumer of those defaults in the
current standalone detached CLI sequence.

D4-S2-2 — LOW: interruption while installing the patches loses already
registered restoration callbacks. `_prepare_budget` constructs an `ExitStack`
at line 1010 but does not enter or guard it before changing defaults at line
1028. `prepare_main` only enters the returned stack at line 1072. An exception
before the return leaves that stack unclosed. `prepare_main` restores TMPDIR,
but cannot restore those defaults.

Failure scenario: an operator interrupts patch installation after the first
default changes, catches the interruption in a long-lived Python caller, and
continues work. `bytes_h_session.important_capacity` retains the abandoned
smoke wrapper. The witness
`PrepareBudget.test_setup_interruption_restores_already_patched_defaults`
injects `KeyboardInterrupt` on the second wrapper construction, proves the
first default remains changed, and explicitly repairs its own test process
afterward. This is a narrow cancellation window, not an observed spontaneous
interrupt. An uncaught interruption that terminates the standalone CLI also
terminates the contaminated process, limiting its practical exposure.

D4-S2-3 — LOW/NOTE: the temporary patch affects unrelated threads. While the
context is active, an unrelated thread's `subprocess.run` uses the smoke's
deadline and group wrapper. An overlapping prepare also sees
`smoke_budgeted` and returns an empty stack at lines 1012–1013, inheriting the
first caller's wrapper rather than its own budget. The witness
`PrepareBudget.test_unrelated_thread_does_not_inherit_the_smoke_budget` fails
its desired isolation assertion: an unrelated thread receives `BudgetExpired`
from the smoke. No current native CLI path starting such a competing thread
was established; this note is not
an independent HOLD.

Verdict: HOLD. F6's subprocess coverage improves, but its restoration guarantee
does not hold. D4-S2-1 is a demonstrated functional failure in later production
code, rather than an adversarial-only race. The lead should close that leak
before accepting the F6 fix. D4-S2-2 and D4-S2-3 describe narrower lifecycle
and concurrency limits, not claims of a presently broken native launch.

The other named delta3 fixes pass the inherited witnesses. F3/D3-1 use the
pinned descriptor for the tested runner writes, refuse existing output links
and an existing detached log, and preserve the protected synthetic bytes.
D3-2 adopts publication of the pending plan before the install record and
cleans it up; the other-plan control remains untouched. D3-3 kills and proves
the fixture-owned descendant gone after isolation timeout. The new module also
proves cleanup after a successful leader exits with a live descendant, and
checks success, failure and timeout group cleanup. D3-4 rejects the mismatched
plist/installer `--plan` options while accepting genuine bundles. D3-5 refuses
the FIFO without blocking. D3-6 completes positive short writes; the added
zero-progress control raises instead of silently succeeding. These are bounded
synthetic checks, not an exhaustive proof about every possible native writer.
The lead's accepted production-writer/TMPDIR residual remains unchanged; no
adversarial-only race is promoted to HOLD.

F6's previously loaded defaults restore on normal return, `ValueError`,
`BudgetExpired` and `KeyboardInterrupt` from the prepare body; TMPDIR and
`tempfile.tempdir` restore too. Direct calls with no timeout acquire the
remaining budget, explicit smaller timeouts stay smaller, and the capacity
probe's inherited five-seconds-left witness passes. Thus the finding concerns
context setup and imports during the context, not a claim that every ordinary
prepare exception defeats the `with` cleanup.

The failed-main-arm return is consistent with the callers inspected. A fake
host refusing the main arm makes `SmokeRunner.run()` return 1, and the actual
CLI `main()` forwards a runner result of 1. The module entry point uses that
return as its exit status. Detached submission still returns success for
spawning the child; the parent cannot synchronously report the child's result.
The separate parser remains necessary for the complete smoke verdict; this
change does not make every later failed check produce a nonzero run result.

Verification ran sequentially, one unittest module per process, using Python
3.13 and `-B`. `python3.13 -B -m unittest
tests.align.test_smoke_delta3_sol2` passed all 15 tests in 362.042 seconds,
including the real-production-arm synthetic packet mutation check.
`python3.13 -B -m unittest tests.align.test_smoke_delta3_sol1` passed all 16
tests in 10.151 seconds. The final `python3.13 -B -m unittest -v
tests.align.test_smoke_delta4_sol2` ran 11 tests in 3.136 seconds: seven pass
and four property assertions fail as described above, with no errors, skips
or expected failures.
Three earlier new-module runs took 3.857, 2.862 and 4.664 seconds. The first two
had three restoration failures and merely observed thread interference; the
final version asserts the desired thread isolation too. The final version
also invokes the real production probe against its stand-in script and uses
atomic publication of its fixture-child identity. Total unittest execution
was under seven minutes, well below twenty minutes. Built-in Python compilation
of the new witness source and `git diff --check` pass. The full suite was intentionally omitted
under the brief's machine-load restriction.

Only this report and `tests/align/test_smoke_delta4_sol2.py` are changed. No
production fix or coordination-state edit was made. No other review seat or
subagent was consulted. No network, launchd, real plist, measurement pipeline,
model weights, real restricted directory, external home path or sealed outcome
was accessed; configured production roots were replaced before path resolution.
Git object reads used only the permitted repository/shared object store.

Next exact step: the lead adjudicates D4-S2-1, repairs restoration for modules
loaded during prepare, and guards patch setup with cleanup on failure. Running
prepare in a bounded separate interpreter, or passing runners explicitly,
avoids process-wide mutation; merely preloading the two named modules would
not address future late imports or other threads. Re-run the three targeted
modules separately after the fix. Native prepare/arm/fault behavior, the
45-minute budget and real launchd teardown remain unverified and require the
lead's agent-free native smoke outside this sandbox after admission. No MLX
code changed, so this review adds no MLX-native test requirement. No contract
ruling is needed to reproduce the findings; the remaining uncertainty is the
lead's intended support boundary for same-process and concurrent callers.
