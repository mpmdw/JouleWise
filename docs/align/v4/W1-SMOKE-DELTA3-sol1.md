# W1 smoke delta3 review — Sol seat 1

2026-11-08. Candidate `8ebc175c3`, review branch
`align/2026-11-08-smoke-delta3-sol1`.

**Verdict: HOLD.** The named old witnesses pass, and several fixes work as
intended, but runner writes can still escape isolation, a publication-before-record
timeout still leaves the smoke job unowned, and isolation's new subprocess wrapper
does not clean up descendants. The installed-plan bundle also has an argv-binding
false PASS. The findings below concern the smoke kit, not scientific outcomes.

## Scope and authority

Reviewed `d48ab1f77..8ebc175c3` excluding the v4-r11 merge content: principally
`d2c9749f9`, the smoke adaptations in `0762c3b9f`, and their smoke documentation.
The fix map is `W1-SMOKE-AGREEMENT.md` §8. Read the repository instructions,
Mission M0, orchestration, relevant source-of-truth pointers and decision-log
entries. The active stop card says NONE. The explicit brief governs the branch,
targeted tests, forbidden paths and coordination-file exclusion.

The lead's accepted residual is accepted here: directory renames during production
prepare/installer pathname writes, and the child's own later TMPDIR resolution,
are outside the guarantee. None of the findings below requires either case.
The directory replacement witness runs only the smoke runner's own fault-session
builder. Other write witnesses use pre-existing synthetic links without a rename.

Only this report and `tests/align/test_smoke_delta3_sol1.py` are changed. Witness
assertions describe the required safety property; open findings deliberately fail
without `expectedFailure` or skips. No production fixes were made.

## Findings

### D3-1 — HIGH: some runner writes still bypass the isolation mechanism

Locations: `w1_smoke.SmokeRunner.finalize`, `teardown_owned`, `fault_session`,
`detach`, and the detached CLI's adjacent-log validation.

Failure scenarios, each witnessed:

- A symlink at `<smoke>/finalize.json` redirects the inventory write into a
  synthetic production victim. `finalize` uses `Path.write_text` directly.
- A symlink at `<smoke>/teardown-unproven.json` redirects the recovery record
  written after refusing to touch another plan. This writer also uses
  `Path.write_text` directly.
- An existing `<smoke>.out` hardlink names a synthetic production file. The CLI
  discards the log's "already exists" violation, and containment cannot identify
  hardlinks. `detach` opens it with ordinary `open(..., 'a')`; synthetic child
  output appends to the production victim. Only `Popen` is replaced; the CLI's
  validation and log open run for real.
- Just after the runner creates `faults/`, replace it with a symlink to an empty
  synthetic production directory. `fault_session(..., base=self.dir)` immediately
  overwrites its `base` parameter with `root / name`. Its mkdirs and its newly
  anchored `safe_write` calls then create the fault session and plan under the
  victim. `O_NOFOLLOW` on the new base's final component cannot detect a link
  in that base's parent. The subsequent isolation refusal comes after the writes.

These are runner writes, not the accepted production-writer residual. The direct
`safe_write` control correctly refuses a final symlink, an intermediate symlink
below its base, and a multiply linked file, preserving all victim bytes.
That narrower helper success does not establish the documented "every write"
claim. Inspection also finds ordinary writes in the receipt-clone perturbation
and venv `.pth` creation; these two sites have not been independently exercised
with replacement links in this review.

Repair: use the same trusted smoke anchor for all runner writers, including
directory creation; preserve the supplied anchor in `fault_session`; and reserve
the detached log with non-following, regular-file/single-link semantics. Audit
the remaining direct writers. A containment check alone cannot detect a hardlink.

Witnesses: `WriteSafety.test_finalize_does_not_follow_a_planted_symlink`,
`test_teardown_recovery_record_does_not_follow_a_planted_symlink`,
`test_detached_cli_does_not_append_to_a_hardlinked_production_log`, and
`test_fault_session_preserves_the_original_smoke_write_anchor`.

### D3-2 — HIGH: publication before the install record is still missed

Locations: `SmokeRunner.reconcile_pending_install` and `published_plan_owner`;
the relevant write ordering is in `scripts/bytes_h_session.py:install`.

Failure scenario: the installer publishes this smoke's plist and loads its job,
then times out before returning to `h.install`. The session already has its plan
path and digest but no `install` member: `h.install` saves that member only after
the installer subprocess returns. Reconciliation's first branch therefore does
not adopt it. Its fallback calls `published_plan_owner`, which determines "ours"
from `self.installed`. That field is necessarily None on this fallback, so even
the exact pending plan is reported as `other:<plan>`. No teardown runs; the fake
job remains loaded. The run also returns zero in this synthetic exit path.

The old timeout witness writes successful install state before reporting the
failure. It passes, but misses this earlier real ordering boundary. The new
witness publishes only a synthetic plist and returns rc 124 without updating
the session's install state.

Repair: compare the published `--plan` with the independently retained pending
plan identity, without requiring ownership to be populated first. Preserve the
different-plan refusal. The new different-plan control passes: no uninstall is
issued and the other synthetic plist stays byte-identical.

Witness: `Lifecycle.test_publication_before_install_record_is_adopted_and_cleaned`.

### D3-3 — HIGH: isolation's new timeout wrapper leaves descendants alive

Location: `SmokeRunner.isolate_run`.

Failure scenario: an isolation command starts a descendant and exceeds its
remaining budget. The new wrapper creates a fresh session but calls plain
`subprocess.run`. On timeout, Python kills/reaps the command leader, not its
process group. A descendant with closed output pipes survives after
`TimeoutExpired`. The witness executes only a tiny Python fork tree, proves its
group still exists after timeout, then kills that exact group and proves it gone
in its own `finally` cleanup. It never signals an unrelated process.

This reopens the descendant-lifetime problem on the newly added isolation path,
despite the existing `bounded_run` controls passing. A surviving Git/helper child
can continue consuming resources or writing after the smoke aborts. The budget's
switch to monotonic time itself is correct; the wall-clock-jump control passes.
The old isolate/preparation budget-gate and TMPDIR tests also pass.

Repair: route isolation through the same process-group kill/reap/proof mechanism
as other commands, preserve subprocess check/output behavior, and verify TMPDIR
afterward as well. The current isolation wrapper checks TMPDIR only before the
command; the report's "before and after every command" claim is broader than
that implementation.

Witness: `Lifecycle.test_isolation_timeout_kills_its_descendants`.

### D3-4 — MEDIUM: bundle membership does not bind the executed plan argument

Location: `w1_prequal.check_deadline`, the two argv entries in `binding`.

Failure scenario: a valid production-generated plan and session name P, while the
copied plist actually has `--plan Q` and mentions P as another argument. The gate
tests only `P in ProgramArguments`, so it PASSes. Independently, the session's
installer argv can have `--plan Q --courier-bin P` and PASS for the same reason.
Both witnessed variants retain a valid plan, matching digest and exit code zero;
all reported binding booleans are true. This can qualify P's deadline while the
argv actually selects a different plan.

Repair: parse and validate the exact `--plan` argument in both argv vectors,
reject missing/duplicate/ambiguous bindings, and compare that argument to the
session plan path. The genuine bundle and mismatched-digest controls pass.
The authoritative hazard span is now used correctly: increasing it beyond the
maximum, while updating the session digest, fails sizing. The old forged-schema,
lone-plan, kind and decoy-span witnesses also pass.

Witness: `DeadlineBundle.test_only_the_actual_plan_flag_can_bind_the_bundle`
(two failing subcases).

### D3-5 — MEDIUM: safe_write can block before rejecting a nonregular file

Locations: `_open_beneath` and `safe_write`.

Failure scenario: a destination is a FIFO with no reader. The helper opens it
`O_WRONLY` before it can `fstat` and reject nonregular files. That open blocks,
bypassing the monotonic command budget because it is an in-process file write.
The witness runs only this call in a disposable Python child; its one-second
timeout kills and reaps the child. It never reaches `IsolationAbort` on this head.

Repair: make the open nonblocking where necessary and reject nonregular files
without an unbounded wait, preserving the no-follow and single-link checks.
This is a denial of the claimed bounded refusal, not an observed ordinary-run
FIFO or a claim that the helper follows a symlink.

Witness: `WriteSafety.test_safe_write_refuses_fifo_without_blocking`.

### D3-6 — LOW: safe_write silently accepts partial writes

Location: `safe_write`'s single `os.write` call.

Failure scenario: `os.write` returns a short count. The helper ignores the count
and returns success, leaving a truncated log, packet or reducer manifest. The
witness wraps the real file write to accept three bytes at a time and observes
only `b'com'` from `b'complete record'`. It does not simulate a symlink or a path
race. A subsequent parser may fail closed, but the helper's success result and
byte-completeness contract are wrong.

Repair: write until all bytes are consumed, treating zero progress or an error
as failure. This is an advisory robustness defect; the HOLD does not depend on it.

Witness: `WriteSafety.test_safe_write_finishes_a_short_write`.

## Disposition of every prior finding

| Prior finding | Result at this head |
|---|---|
| D1 / detached part of D2-1 | Original forbidden-destination mkdir/spawn escape closes. Adjacent-log write protection remains incomplete: D3-1. |
| D2 / replacement part of D2-1 | Original reducer-manifest and main staging swaps refuse; TMPDIR swap before launch refuses. `safe_write` correctly protects targets below its anchor. Other runner writers and the fault-session anchor still escape: D3-1. Accepted production-writer/child-TMPDIR residual is not a finding. |
| D3 / D2-2 | Monotonic clock, remaining-time clipping, local TMPDIR and boundary gates work on the named witnesses. New isolation wrapper leaks timeout descendants: D3-3; in-process FIFO write is unbounded: D3-5. Native total duration remains unmeasured. |
| D4 / D2-3 | The old post-record timeout and terminal-timeout cleanup cases close. Earlier publication without an install record remains open: D3-2. A different published plan is left untouched. |
| D5 / D2-4 | Full NightPlan parsing, authoritative hazard span, digest, kind and bundle-presence gates close the old forged-plan cases. Argv membership permits the mismatched-plan bundle: D3-4. |
| D6 / D2-5 | Recursive changed/removed chain leaves are covered; see packet verification below. No new packet-tamper HOLD. |
| D7 | Path-typed launch bindings are write locators, so they cannot borrow the read-only exception. The old three-binding witness passes. |

## Verification

Tests ran one module per process, sequentially, with Python 3.13.18. Total
test execution, including the initial witness harness correction, was about
six minutes, below the brief's approximately twenty-minute limit.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_smoke_delta_sol1` | PASS, 15 tests, 6.514 s. |
| `python3.13 -B -m unittest tests.align.test_smoke_delta_sol2` | PASS, 15 tests, 14.375 s. |
| `python3.13 -B -m unittest tests.align.test_w1_prequal.CadenceTests.test_packet_rebuild_and_tamper_pass_on_the_production_arm` | PASS, 1 test, 310.907 s. |
| `python3.13 -B -m unittest -v tests.align.test_smoke_delta3_sol1` | Final run: 16 tests, 11.968 s; 7 methods pass, 9 methods fail (10 assertion failures because the argv witness has two subcases); no errors. Failures reproduce D3-1 through D3-6. |
| `python3.13 -B -m unittest tests.align.test_w1_prequal.PortedSolTests.test_deadline_is_bound_to_the_installed_plan_plist_and_session` | PASS, 1 test, 1.957 s; genuine bundle, other plist, bad hash, failed installer, smoke/w1/r1 kind, lone-plan and R1-floor controls. |
| Python built-in `compile` on the new witness source | PASS. No bytecode files written. |
| `git diff --check` | PASS. |

The initial new-module run took 13.300 s and had eight finding assertions plus
four setup errors: the bundle fixture's `Context` tried to look up HEAD in its
deliberately non-Git evidence directory. Supplying the synthetic commit fixed
the fixture. The final full-module rerun above has no setup/import errors.

For packet coverage, the production-arm test admits its control and refuses
every tamper case for a packet-specific reason. The new witness independently
confirms exactly **357 generated mutations plus the zero-capture chain omission
= 358**, using the real producer's rebuilt packet and an admitted production
control. A separate mutation oracle checks changed and removed leaves through
nested dictionaries, lists and an empty container in both chain lists and a
check entry. The exact `checks.record_committed.pushed_tip` exemption is retained;
top-level `pushed_tip` and `packet_preflight` also remain the defined exemptions.
The prior delta witnesses additionally catch stand-ins ignoring a chain digest,
a later chain leaf, a nested status or an entire element. No packet-coverage
regression was found on the present schema; this does not prove future packet
shapes automatically have the same mutation count.

## Limits and next step

Synthetic only. No network, launchd, real plist, measurement pipeline, model
download, sealed outcome or real restricted/custody directory was accessed.
Configured production paths were read as text only; fixtures replace them before
the root-resolution helper is called. The full test suite was not run, as the
brief forbids it while the independent eight-worker analysis job runs. No MLX
code changed, and no MLX native test is needed for these review-only artifacts.

No other current review seat was consulted. No coordination state, task kernel
or production code changed. Process inventory through `ps` was denied by the
sandbox; the child witness instead uses its own recorded process-group identity
and signal-zero proof. Native MBP wall time, production prepare/install behavior
and real launchd teardown remain unverified; all require a lead-controlled
agent-free smoke outside this sandbox after the code findings are resolved.

Next exact step: the lead dispositions D3-1 through D3-6, repairs the blocking
runner/cleanup/binding paths, and reruns the old delta modules and this witness
module one at a time. Keep the lead's accepted residual unchanged. Only then
consider the native smoke gate.
