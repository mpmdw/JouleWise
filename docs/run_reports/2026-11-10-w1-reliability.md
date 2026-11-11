# W1 pre-arm reliability — local Sol seat

Intake: explicit 2026-11-10 owner brief, measurement-system audit §3.1
(A-01/A-02/A-04/A-05/A-09), §3.2 (I-01), and implicit-state-machines audit,
both read from `origin/audit/2026-11-10-fable`. Mission M0 intake read; no
active stop card. This request overrides queue selection and state updates.
No coordination files or kernel tasks changed.

Branch: `ops/2026-11-10-w1-reliability`, based on W1 integration head
`9abe6095f98da581e149bfd1fc2bc2d0a582b2a3` of
`align/2026-11-08-v4-r11`. The allowed local Git store's remote-tracking ref
confirms this head; CANONICAL's `57c34f5ab` checkpoint is its ancestor.
RUN_STATE items 246–250 were read from origin/main. The frozen R1 measurement
checkout `20e9edbc4` was not targeted. Local-store fetch only; no network.

## A-01 — implemented

Commit `5bb152acc`. Files: `scripts/run_night.py`, `joulewise/b5/driver.py`,
`tests/test_w1_reliability.py`.

Adds `chain_outcome`, `measurement_outcome`, `fault`, and `fault_reasons` to
the night result. Nonzero chain exits fault even when the existing arm verdict
is GO. Known R1 plans report only the structural status: complete, refused,
aborted, running, absent, unreadable, or invalid. Incomplete R1 status faults
even at exit 0. Hazard result and courier facts carry the same faults;
pre-chain refusal explicitly reports REFUSED_PRE_CHAIN. Existing verdict and
driver exit-code policy are preserved.

Cited rebind: measurement-system audit A-01 / Q3. Both changed production files
are in `v4_registration.ARTIFACTS` (run_night also in _NAMED_ARTIFACTS; driver
in EXECUTED_CLOSURE). They are STRICT: new exact-candidate receipt, signature,
and both registration gates before W1. W1 is not registered yet. No registration
text, inputs, seeds, analysis engine, estimator, or threshold changed.

## A-02 — implemented with results-ref delivery

Commit `c80d4d638`. Files: `scripts/run_night.py`, `scripts/b6_courier.sh`,
`tests/test_w1_reliability.py`.

The repository's B5 courier is an agent mail path. B6's mailer requires an
injected transport (its SMTP adapter also requires an injected sender), not a
ready unattended mail command. The permitted results-ref fallback is used.
ALIGN terminal reporting immediately publishes `night-results/<plan>` with
one 50-second subprocess budget, including pre-chain refusals, before running
the courier. It initializes a small bare publisher, fetching only the prior
results ref when present; it does not clone main before delivering a refusal.
Updates fast-forward without force. Raw chain logs remain excluded; R1 raw
payload/slots are not exported. `result.json` bytes are copied unchanged.

Only successful push acknowledgement produces `courier.delivery.json`, bound
to the result digest, plan, ref and commit. The program courier writes
`courier.sent` after that delivery; failure writes `courier.filed` and returns
nonzero. A changed result cannot reuse a prior delivery receipt.

Cited rebind: audit A-02 / Q11. Both changed production files are STRICT bound
paths. The same STRICT re-registration obligation applies. The existing
artifact set already covers these files; registration code/text was not edited.

Residual risk: the under-one-minute delivery witness uses a local bare remote.
A reachable/authenticated production remote and the Air watcher are external
prerequisites, not proven here. Failed/offline pushes remain filed, unsent and
eligible for the existing courier/dead-man retry flow. No program can guarantee
remote arrival while transport is unavailable. SIGKILL of the reporting process
itself still depends on the existing dead-man; no host job was installed here.

## I-01, production host-state preflight, A-04/A-05 — NEEDS_RULING

No code changes for these items. The brief explicitly says to STOP an item
whose fix changes registered/bound semantics beyond surfacing. An asynchronous
ruling question was sent while independent reporting work continued.

Question: does the owner authorize these specific admission/liveness and host
restore changes to STRICT bound files, followed by STRICT re-registration?

Options considered:

1. Leave these items blocked under the explicit stop rule.
2. Authorize only the specified gating/preflight/restore changes, keeping all
   analysis/threshold/registration-text/seed restrictions, and re-register W1.

Recommendation: option 2, prospectively, before W1 arms. No such ruling has
been assumed.

Blocked work and current evidence:

- **I-01:** `scripts/align_v4_session.py:arm_checks` already performs a live
  meter probe and refuses `triage meter_reader_live` failure. The night hazard
  driver still treats the meter as diagnostic. Making that driver refuse an
  absent reader or stop on stream/USB liveness failure changes the bound
  `joulewise/b5/driver.py` admission/termination behavior, rather than only
  surfacing a fault. Native meter readiness and USB-unplug validation remain owed.
- **Production preflight:** `scripts/align_v4_session.py:install` already takes
  HostLock, but `prepare`'s session-start restore does not exercise the directory
  when no marker exists. Requiring a production-path acquire/release at prepare
  and arm adds admission behavior to a bound script (and requires smoke updates).
  No actual production host-state directory was probed from this sandbox.
- **A-04/A-05:** changing the bound night runner/powermode close and dead-man to
  restore network time and non-W1 power markers changes host side effects and
  lock/ownership behavior. The existing mode-2 close is not a complete solution
  for a mode-0 R1 chain that enters High Power internally. These items need the
  owner ruling, then synthetic every-terminal-path tests and lead-owned native
  kill/dead-man/read-back checks. The current residual strand risk remains.

## Verification

Commands, one targeted module at a time:

- `python3.13 -B -m unittest tests.test_w1_reliability`: initial four tests
  passed after isolating the chain process-group boundary; final **9 passed**,
  7.740 s. Includes a real local bare-Git push, failure/timeout injection,
  pre-chain refusal, repeated fast-forward, digest binding and byte equality.
- `python3.13 -B -m unittest tests.align.test_v4_executed_closure`: **4 passed**,
  3.851 s. No new unbound executed path introduced.
- `sh -n scripts/b6_courier.sh`: passed.
- `git diff --check`: passed before each implementation commit.

Failure/uncertainty: the initial new tests using a real chain process group
returned courier-failure exit 6 rather than expected 0/5; the existing
`tests.test_b5_driver.LaunchTests.test_chain_digest_mismatch_is_a_flag_and_the_chain_runs`
also failed (6 != 0, 12.126 s), with a subprocess ResourceWarning. This was
not proven to fail at the untouched base, so it is reported as an unresolved
environment/integration limitation, not dismissed as a known baseline.
New terminal-reporting witnesses inject a proven chain exit; the arm, monitor,
result and courier-facts path remain production code. Lead must rerun that
existing real-process integration test outside the sandbox before arming.

No full suite, real measurement, analysis pipeline, model download, Metal/MLX
execution, real custody access, external notice, push, install, or machine-state
change was performed. Hardware claims remain PROVISIONAL. Local test pushes
target only synthetic bare repositories under temporary directories.

Next exact step: obtain the bound-semantics ruling for the three blocked work
groups; review these local commits, then complete STRICT re-registration and
native PREQUAL/smoke at the final integrated W1 head. This branch alone is not
an assertion that W1 is ready to arm. Watchdog work has its own second branch
and report.
