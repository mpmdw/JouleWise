# W1 smoke delta review — Sol seat 1

2026-11-08. Candidate `ed65d90944bba3afb8d560d24f4da5dbba3c94c6`.
Branch `align/2026-11-08-w1-smoke-delta-sol1` (already checked out, initially clean).
**Verdict: HOLD.** The earlier fixes close several concrete cases, but isolation
escapes, an installer cleanup gap and deadline/probe false PASSes remain. This
verdict concerns the smoke/PREQUAL implementation, not Block 5 outcomes or W1
scientific readiness. No production fix or native clearance is implied.

Authority: the task brief; `W1-SMOKE-AGREEMENT.md` §7 and its underlying §6/6a
rulings; `W1-SMOKE.md`; the original reports read from both review refs;
AGENTS/CLAUDE, Mission M0 and orchestration; targeted D-050/D-064; and
`git show origin/main:docs/perf/SPEED-TOOLBOX.md`. No active stop card exists.
The explicit brief overrides the full-suite and coordination-file write rules.

Only this report and the [witness module](../../../tests/align/test_smoke_delta_sol1.py) change. Witnesses
assert required properties with ordinary assertions: surviving defects FAIL,
without skips or expected failures. Every victim, home, published plist and
installed-job stand-in below is disposable and synthetic.

## Surviving findings

### D1 — detached entry writes before destination validation

`scripts/align_v4_w1_smoke.py:57`: `--detach` creates `smoke_dir.parent` and
calls `smoke.detach`, which opens the adjacent output log, before constructing
the runner that calls `destination_violations`. A destination under the
synthetic production checkout is known to the validator to be forbidden, yet
the real CLI creates its parent. The witness mocks only the detach launcher;
it launches no process. Thus fixing `SmokeRunner.run` did not fix the documented
operator entry point.

Validate and reserve the detached destination before either mkdir or log open;
preserve the same containment guarantee across the detached handoff.

### D2 — manifest replacement after the check still writes through a symlink

`w1_smoke.reduce_view`: `writable(path)` checks the locator, then a separate
`read_bytes` and `write_text` use it by pathname. The witness uses the real
measurement view, reducer and chain validation. At the return from the first
manifest read, after `writable` returned, it replaces that manifest with a
symlink to a synthetic production victim. The later write changes the victim
bytes. This is an exercised check/use race, beyond the now-passing planted-link
control. No production file or sealed path is involved.

Use directory/file descriptors or another race-safe publication mechanism that
cannot follow a replacement file or parent symlink. A second pathname check
alone leaves the same race.

### D3 — isolate/prepare remain outside the hard deadline

`SmokeRunner.isolate` calls `isolate_fn` without the command wrapper; the real
`isolate` has its own per-command 600-second timeouts and does not receive the
runner's command environment. `prepare_main` is also an unbounded in-process
call. No budget check separates these stages. With a fake isolation operation
consuming 2,701 seconds, the runner still calls preparation and writes a session
after its 2,700-second deadline. It subsequently refuses to arm, which is useful,
but does not enforce the hard duration promise. The default deadline clock is
also `time.time`, rather than a monotonic elapsed-time clock.

Put isolation/preparation under the same bounded, owned execution and command
TMPDIR as the other steps, check remaining time at their boundaries, and use a
monotonic deadline independently of epoch t0. Native duration remains unmeasured.

### D4 — an installer timeout can leave its published smoke job untracked

`SmokeRunner.arm_main` records `self.installed` only after `cmd` returns and
session state is read. `cmd` raises immediately if its timed-out process group
survived. A synthetic installer that writes successful installation state and
publishes the job before returning this timeout outcome leaves the fake job
loaded: `run` catches `TeardownFailure`, but `finally` sees `installed is None`
and performs no uninstall or teardown proof. The old terminal-timeout control
passes because ownership has already been recorded on that path.

Track the pending arm's identity before invoking the installer, and reconcile
its owned installation on abnormal return/exception before deciding cleanup is
unnecessary. Verify ownership before touching the shared launchd label.

### D5 — matching labels still let a forged plan PASS the deadline gate

`w1_prequal.check_deadline` checks schema, receipt class, a plan-id prefix and
the first recursively found `programmed_span_s`. It neither parses a complete
night plan nor binds its computed digest to an independently named installed
plan. A five-field JSON document with those labels, a one-second span and the
formula-derived 17,760-second maximum PASSes. The real `NightPlan.from_mapping`
rejects the same document. Its reported digest authenticates only the supplied
declaration.

Validate the actual plan schema and canonical span location, bind the copy to
the intended arm/session's plan identity and bytes, and verify schedule sizing
from that bound plan. Preserve kind matching and the R1-only floors. The review
does not invent an authoritative installed-plan handoff format for the lead.

### D6 — chain hashes can be ignored while packet-tamper PASSes

`w1_prequal._mutations` edits only the first sorted field of each chain element.
The real producer's `window_chain` entries also contain `path`, `sha256` and
`previous_sha256`. A deterministic rebuilding stand-in that ignores the first
element's `sha256` admits a direct edited digest, yet the real tamper probe
PASSes because no generated mutation tests that leaf. Its strict control
PASSes; arms lenient on a nested check status or an entire chain element are
correctly caught. This is a probe-sensitivity gap, not a claim that the current
production arm accepts the digest edit.

Mutate/remove the identity and digest leaves of every chain element, retaining
the admitted control, expiry-specific cases and exact informational exemptions.

### D7 — launch write bindings can still borrow the read-only exception

`SMOKE_WRITE_KEYS` omits `operator_log_root`, `pre_calibration_dir` and
`post_calibration_dir`, although the hazard launch contract and generated chain
use them as output locations. Each can point into a synthetic production
site-packages directory and return zero isolation violations when that directory
is declared read-only. The new write-before-readonly logic works only for keys
in the incomplete list. These are real launch binding names, not invented keys.

Classify the complete launch write contract and check every such locator for
absolute containment before applying import-only exceptions.

## Fixes that withstand the named re-attacks

- Literal/resolved production aliases, relative recognized write locators,
  `/private/tmp` folding and command TMPDIR escape controls refuse correctly.
- Published but unloaded night and deadman plists each block the smoke in a
  synthetic account home.
- Exhaustion during the fault loop and failed disk-image teardown prevent the
  main arm. A recorded owned job is uninstalled on terminal timeout.
- Real process-group tests kill TERM-ignoring descendants even when the leader
  exits after TERM; normal exit and unproven-group controls also pass.
- Source roster order/count/omission differences fail; an identical fixed-eight
  source/projection passes.
- Packet probes catch the edited nested status and an ignored complete chain
  element. Expiry specificity and admitted-control regressions remain covered
  by the earlier review modules.
- The static first-party closure includes scripts and is covered by receipt
  artifacts. This does not establish dynamic/shell closure completeness or
  registration readiness.

## Verification

All original review witnesses now pass (21 Sol1 and 14 Sol2). The new module
runs 15 tests: eight methods pass, seven finding methods fail, with nine failed
assertions because D7 has three binding subcases. Every failure reaches the
intended property assertion; there are no setup/import errors.

| Single-module selection (each in its own process) | Result | unittest seconds |
|---|---|---:|
| `python3.13 -B -m unittest tests.align.test_w1_smoke` | 23 tests, OK | 20.176 |
| `python3.13 -B -m unittest tests.align.test_smoke_review_sol1` | 21 tests, OK | 11.836 |
| `python3.13 -B -m unittest tests.align.test_smoke_review_sol2` | 14 tests, OK | 7.678 |
| `python3.13 -B -m unittest tests.align.test_smoke_delta_sol1` | 15 tests, 9 intended assertion failures (D1–D7) | 2.777 |
| `python3.13 -B -m unittest tests.align.test_w1_prequal` | 35 tests, 2 environment-induced meter failures | 365.337 |

The commands above were launched via a small `unittest` loader/runner wrapper
with the same single-module selection; its separate elapsed markers include
import overhead. For example, the actual witness invocation was:

```sh
R=/private/tmp/jw-smoke-delta-sol1-wwdhh551
sh "$R/safe-run" python3.13 -B "$R/run-module.py" tests.align.test_smoke_delta_sol1
```

For the focused PREQUAL module the wrapper also retains each synthetic fixture's
`chain.stderr.log` before test cleanup, without changing its return or assertions.
Its other 33 tests pass. The two failures are the unchanged meter restart and
crash-radius tests discussed below, not new assertion exemptions.

`PYTHONPYCACHEPREFIX="$R/pycache" python3.13 -B -m compileall -q joulewise tests`
exits 0 in 3.740 s, with bytecode outside the checkout. Aggregate test/PREQUAL
command time, including wrapper imports, is 707.126 s (11.8 minutes); adding
compilation gives 710.866 s. The full suite was not run, as explicitly required.

Clean-clone PREQUAL exits **1, FAIL**, in 298.923 seconds (report wall 298.8),
at exactly `ed65d9094`, `checkout_dirty=false`; the clone is still clean after
the run. Nine checks PASS, seven FAIL, one WARN:

- PASS: arm CLI (13 cases), packet rebuild/expiry, packet tamper (97 changes),
  calibration stop, escalation exit, R1→W1 chain, WP22, smoke kit, W1 arm route.
  WP22 runs its full module: 22 tests in 91.152 s, OK, one existing expected
  failure. No new exemption is added by this review.
- Five missing-readiness failures: R1 placeholders in `kit-ready`; four absent
  receipt artifacts (`r1_soak_reference.json`, `u3_bar.json`, `w1_plan.json`,
  `wp19_receipt.json`); absent series and deadline inputs; absent R1-filled W1
  plan. The sizing code paths still agree at 26,927 s span / 44,640 s maximum.
- `km003c-launch` and `km003c-crash-radius` fail: the killed stand-in reader
  remains starts=1, restarts=0, one stream. The focused module's retained
  synthetic stderr confirms the injection itself failed:

  ```text
  sysmon request failed with error: sysmond service not found
  pkill: Cannot get process list
  ```

  The marker-scoped fixture kill never happened. These sandbox false refusals
  do not establish a production DC-salvage regression, and do not validate the
  restart/crash-radius path. Assertions remain intact; rerun where signalling
  is supported.
- `optin-required` WARN retains 134 required opt-in tests, 14 covered by this
  PREQUAL and 120 requiring other provisioned/native/base routes. It does not
  discharge their gates.

The missing prerequisites and sandbox-limited meter outcomes do not constitute
the new HOLD findings. D1–D7 are independently reproduced above. PREQUAL JSON
SHA-256: `de5e5262aca8bc508518f0a815c7bd576cf714df895add50f6e66dbc0175b877`.

The outer test/probe runs are serial, one unittest module per process, with
Python 3.13 and `-B`. The existing packet probe internally uses six threads.
`TMPDIR` is the resolved path
`/private/tmp/jw-smoke-delta-sol1-wwdhh551/tmp`. A temporary `sitecustomize`
redirects `Path.home()` and tilde expansion to a synthetic account home for
these runs; no real home plist/configured production root is resolved. Git's
global configuration is disabled. This test environment adaptation changes no
candidate bytes or admission assertion.

The clean candidate is a shared clone detached at `ed65d9094`, with its origin
removed and no projections, waivers or `--only` supplied. The exact command is:

```sh
python3.13 -B scripts/align_v4_prequal.py --w1-next w1 --jobs 1 \
  --output /private/tmp/jw-smoke-delta-sol1-wwdhh551/prequal
```

Raw console logs and synthetic PREQUAL output are retained under the temporary
root above. No full suite, network, weight download, native smoke, powermetrics,
real measurement input or Block 5 analysis pipeline was run. No other agent or
external consult was invoked. Coordination state remains untouched.

## Handoff

Witness commit: `c79c0afe8eaab6f6a9f9530531552d93178e039b`
(`test(align): witness remaining W1 smoke delta safety gaps`). This report is
the following documentation commit; its hash is in the final handoff. No
production files, registration, analysis or coordination state are changed.

Open contract question for the lead: which independent planning-only
producer/arm binding authenticates the installed-plan copy? The candidate's
gate defines none. Merely parsing a complete plan will not settle that binding.

Fix D1/D2/D4/D7 before native smoke use, and close D3/D5/D6 before relying on the
stated hard-budget/deadline/probe guarantees. Then rerun the failing methods,
the two original review modules, the runner/PREQUAL modules and clean-clone W1
PREQUAL with genuine lead-provided planning prerequisites. Nothing is pushed.

Native uncertainty remains: the lead must run Part B only in a clean, disarmed
MBP gap, outside an active agent/measurement session, measuring total duration
and proving reader/job/contender/image teardown on failure exits. Rerun the
killed-meter PREQUAL checks where fixture process signalling is supported.
The provisioned native modules include `tests.align.test_cache_checkpoint_native`,
`tests.align.test_r0_mlx_native`, `tests.align.test_thermal_mlx` and
`tests.align.test_smc_native`, with their documented live opt-ins. The full
`optin-required` ledger remains the authority for the other uncovered tests.
These fixtures do not certify native MLX/Metal behavior.
