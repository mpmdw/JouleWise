# W1 smoke / PREQUAL review — Sol seat 1, 2026-11-08

**Verdict: HOLD at `f6251227ae4d4258a6397230f6ff6e755a3fcb88`.**
There are reproducible isolation escapes, a native-arm false refusal, and checks
that PASS without their claimed property. This is a review of the merged kit,
not a release of W1 or a native hardware validation. No production code is
changed here; the lead can dispatch fixes using the witnesses below.

Authority read: repository AGENTS/CLAUDE conventions, Mission M0 and orchestration,
the restart/queue safety sections, `W1-SMOKE-AGREEMENT.md` (including §6/§6a),
`W1-SMOKE.md`, and `git show origin/main:docs/perf/SPEED-TOOLBOX.md`. The explicit
brief takes precedence over coordination-state updates and the full-suite rule.
The supplied review branch was already checked out and clean:
`align/2026-11-08-w1-smoke-review-sol1`.

## Findings

IDs correspond to test method names in
[`test_smoke_review_sol1.py`](../../../tests/align/test_smoke_review_sol1.py).
P1 findings prevent admission. P2 findings are narrower coverage weaknesses,
not independent reasons to block the current candidate.

### S4 — P1: isolation is checked after writes; path coverage has escapes

`w1_smoke.SmokeRunner.run` creates the smoke directory and log, clones, then calls
the real prepare/reducer before its first `check_isolation` (lines 622–650).
Neither `guards` nor `isolate` rejects a smoke directory under the measurement
checkout before those writes. The CLI's documented home-directory exclusion is
also absent. A stand-in production checkout gets a smoke clone/session written
inside it before the runner eventually returns 2.

A stronger witness plants a manifest symlink into a **temporary stand-in**
production directory. The real `measurement_view` and `reduce_view` follow it and
rewrite the victim manifest before any runner isolation check. The victim bytes
actually change. No real production directory was involved.

`isolation_violations` also ignores relative write paths (lines 157–196).
Configured production roots are left lexical while candidate paths are resolved;
a configured custody symlink and its real target therefore compare unequal.
Both are missed by the scanner in synthetic fixtures. These are conditional
escapes, not a claim that today's configured production roots are symlinks.

Required fix: validate the destination before creating even the directory/log;
constrain writable locators to the isolated subtree; reject relative write
locators; validate each write target before prepare/reduction. Preserve the
no-probing-real-production-roots rule: use an authorized canonical root inventory
or refuse ambiguous aliases rather than resolving sealed roots in this review.

### S5 — P1: fault isolation failures do not stop the main arm

`arm_fault` passes only state, not the copied plan, to `isolation_violations`
(line 478). A fault plan with `claim_runs_root` in stand-in production reaches
the install command. The past-t0 interlock still prevents this fault attempt
from installing a job; it does not establish plan isolation.

When an unsafe **state** is detected, `run` catches the resulting exception,
logs that fault FAIL, and continues to the main install (lines 653–674). A
synthetic arm-control escape demonstrates the main install being called.
Use the same complete state/plan validation at every arm, log a fatal isolation
row, and abort the whole smoke on a hit.

### S6 — P1: an installed but unloaded production plan is invisible

The gap guard checks the loaded `com.joulewise.night` service, a process-name
search and a briefly acquired lock. It does not inspect published plan plists,
the deadman service, or retain an exclusive smoke reservation. With an unloaded
published production plist in a fake home, it admits. This violates the brief's
"never armed while a real plan is installed" requirement.

This matters beyond a conservative guard: the installer snapshots existing
plists and replaces them (`night_agent_install.Target.stage` / `write_plist`).
Do not infer absence of an installed production plan from launchctl absence.
The global `pkill -KILL -f scripts/km003c_monitor.py` at line 564 is an additional
static safety concern: bind the injected kill to this smoke's recorded reader
identity rather than all readers with that script name. No global kill was
executed by this review.

### S7 — P1: the 45-minute limit and teardown are reporting checks, not limits

The runner can exhaust its 2,700 seconds during fault attempts, restage, and
still install the main job. It also installs the main job after a disk-image
detach has demonstrably left the image mounted. Both execute in fake-clock
witnesses. The parser notices later, after the unsafe continuation.

On a terminal timeout, the runner has no finally-path that uninstalls its own
job or proves its processes stopped. A fake installed job remains loaded when
`run` returns. `terminal` can wait until `deadline + 300`; `chain` then has an
additional 900-second command budget. Individual command limits and sleeps are
not clipped to the remaining total budget. The ordinary prepared window maximum
is much larger than the smoke budget. The 37–42 minute native estimate remains
unmeasured.

Required fix: stop on failed fault/teardown checks; reserve enough time before
arming; enforce one elapsed-time deadline across commands and sleeps; bound the
smoke plan itself; finally tear down **only the job/process identities this
smoke owns**, preserving a recoverable record if teardown cannot be proved.

### S8 — P1: command timeout can leave descendants alive

`bounded_run` breaks its TERM/KILL loop as soon as the parent's `communicate`
returns after TERM (lines 327–337). A descendant that ignores TERM and redirects
its streams can survive after its parent exits, so no KILL is sent to its group.
The witness simulates that exact parent lifecycle; it runs no real orphan.
Also, the contender's kill fallback has no final `wait` (line 582).

Required fix: complete group teardown independently of the parent's pipe/exit
state, reap the parent, and prove the owned group/contender gone before recording
stopped. Native process verification remains necessary.

### S9 — P1: the real disposable view cannot pass receipt path validation

The measurement view links `configs/campaigns/align_v4` (the source kit) and code
to the isolated clone. Its reduced launch pack is the separate
`configs/campaigns/align-v4`. Production `align_v4_session.install` calls
`kit.generate(..., check=True)` on that view, which reaches
`require_registration(view)`. `v4_registration._local` rejects the symlink in
the receipt path before receipt contents matter (lines 397–408, 506–511).

The real view plus the real receipt locator reproduces this refusal. Thus the
native arm-control and main arm will fail even after the source kit is ready.
`smoke-kit` tests the view/reduction and the arm faults separately, so its PASS
does not exercise this connection. Test a ready synthetic source through the
actual reduced-view install, not a separate arm fixture, when fixing this.

**Rejected suspicion:** reduction does NOT itself cause generated-kit byte
drift. A passing control runs the real generator byte comparison with only
pending readiness bypassed. The different underscore/hyphen pack paths explain
why. The receipt locator refusal above is the actual defect.

### S1 — P1: deadline PASS is unbound schedule arithmetic

`check_deadline` / `validate_deadline` (lines 890–956) accept
`window_max_s=1`, a top-level `programmed_span_s=43200`, one projected one-second
segment, and zero overhead. They report PASS and a one-second requirement. No
installed-plan identity/digest or deterministic schedule projection is checked.
Additionally, `kind='d'` qualifies `--w1-next w1`, contrary to the documented
kind match; it bypasses R1 floors at the R1 gate too.

The arithmetic and R1 floors work for honest projections. What is missing is
proof that the projection describes the plan being armed. Derive/verify the
segments, retries, encounters and overhead against a bound source plan and
require the actual next-window kind. Do not solve this by increasing a stale
printed deadline.

### S2 — P1: a hash binds series bytes but not the projected roster

`check_series_manifest` (lines 931–944) hashes the supplied source, then validates
only the independent `windows` projection. A source with one benign per pair
and a projection claiming seven per pair PASS together with a correct source
hash. Source bytes need not even represent the claimed series.

Derive the projection deterministically from the frozen manifest, or compare
every projected roster/order/count to it. The present PASS proves only that
some named bytes have the supplied digest and a separate roster is fixed-8.

### S3 — P2: packet probes accept unrelated refusals as evidence

`packet-rebuild` (lines 557–584) passes a rebuilding arm whose canonical packet
has **no expiry field**, provided it refuses 30 days later for an unrelated
host/record freshness rule. This is a false PASS for mandatory packet expiry.
Use a nonexpired control and just-before/after-expiry probes with all other
inputs valid, and require the expiration-specific refusal.

`packet-tamper` (lines 587–614) independently passes an arm that rejects every
request but returns a rebuild. Add an admitted control in that probe. The
paired `packet-rebuild` check DOES catch reject-everything, so this latter
witness alone is not a whole-PREQUAL bypass. Existing tests do catch ignored
record-commit mutations and omitted `C3#1` elements; preserve those controls.
Checking equality with a reported rebuild alone does not prove authentic
re-derivation of every record/predecessor; add source-chain corruption witnesses
when the production packet-as-pointer implementation lands.

### S10 — P2: receipt coverage silently excludes executed scripts

The coverage comprehension at line 749 filters closure files to `joulewise/`.
An executed but unbound `scripts/unbound.py` therefore does not fail the check.
The witness uses a tiny committed synthetic repo; exact/digest/working-drift
receipt self-tests remain real, while only provisioned-registration acceptance
is stubbed independently of coverage.

Today's static closure has 230 files and **zero** uncovered paths, including
scripts. This is a future-regression hole, not a claim of a currently unbound
script. Check all first-party closure entries and preserve the broader
configured/script-launch-edge closure checks already owned by registration.

The ordinary copied-ledger path is supported by the existing real-clone
`IsolationTests`: distinct ledger inodes and unchanged source bytes. The base
launcher's semantic comparison and help probes pass here. No batching, caching,
or performance change was made, and no runtime saving is claimed.

## Verification and runtime

One unittest module per process, sequentially; no full suite, no analysis
pipeline, no model weights, no network, no native smoke/hardware access.
Every attack used temporary synthetic roots, including the symlink victim.
Coordination-state files were neither edited nor registered.

| Command | Result / measured time |
|---|---|
| `python3.13 -B -m unittest tests.align.test_w1_prequal` | 34 tests, 2 failures, 272.065 s. Both meter tests: killed reader did not restart; crash-radius lacked member evidence. All other cases passed. The initial `nice -n 15` wrapper printed a sandbox priority warning but ran the tests. |
| `python3.13 -B -m unittest tests.align.test_w1_smoke` | 19 tests OK, 22.714 s. |
| `env -u JW_PREQUAL_HF HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python3.13 -B -m unittest tests.align.test_v4_prequal` | 36 tests OK, 3 tokenizer skips, 13.139 s. Includes the real `origin/main` launcher and semantic argv controls; expected argparse usage-error output is part of the tests. |
| `python3.13 -B -m unittest -v tests.align.test_smoke_review_sol1` | 21 tests OK: 18 expected failures, 3 passing controls, 15.489 s. Expected failures are the reproduced defects, NOT green qualification. |
| Clean-clone `python3.13 -B scripts/align_v4_prequal.py --w1-next w1 --jobs 1 --output <scratch>/prequal` | FAIL, exit 1; 392.184 s externally / 392.0 s reported. Exact candidate `f6251227a`, `checkout_dirty=false`. Seven PASS, nine FAIL, one WARN. Full WP22 module: 20 tests in 179.296 s, one documented expected failure. |
| `python3.13 -B -m compileall -q joulewise tests` | PASS (exit 0). |

The clean-clone failures were:

- `packet-rebuild`, `packet-tamper`: production arm has no rebuilt packet at
  this candidate (the already-declared G1/G1b work remains outstanding).
- `kit-ready`, `receipt`, `w1-window-max`: pending R0/R1 values and uncommitted
  W1 prerequisites. Receipt coverage itself is complete, but `r1_soak_reference`,
  `u3_bar`, `w1_plan` and `wp19_receipt` are absent.
- `series-manifest`, `deadline`: no projections supplied. No real measurement
  inputs were read or fabricated to make these prerequisites green.
- `km003c-launch`, `km003c-crash-radius`: the stand-in killed reader never
  restarted, matching the sandbox-limited module failures.

Passing rows: arm CLI, calibration stop, escalation exit, R1-to-W1 chain,
WP22, smoke kit and W1 arm route. `optin-required` WARN lists 134 opt-in-only
required tests, 14 covered here and 120 still requiring other provisioned/native
routes. These results do not qualify W1. This measured runtime uses **one**
probe worker under the concurrent blinded-job load, not the documented parallel
Air timing and not the native 45-minute budget.

Local raw synthetic/software evidence is retained at
`/private/tmp/jwsol/squeeze/smoke-review-sol1/tmp/w1review-qualification-0x78anb7/`:
`prequal/prequal-w1.json`, `prequal-console.txt`, and `witness-audit.json`.
The PREQUAL JSON SHA-256 is
`5588e50149c7bae7154882113b085d219e64fe79c3ad50e543608e7b7126408d`.
These temporary files are not additional committed deliverables.

The first witness run exposed two mistaken assumptions in the tests: the
generated source kit remained byte-identical (now a passing control), and a
receipt scratch clone inside its own candidate made the candidate dirty (moved
the scratch work outside the tiny fixture repo). That exploratory run had two
unexpected successes; the final run above has none.

A final, separate process loaded only `tests.align.test_smoke_review_sol1`
through `unittest.defaultTestLoader.loadTestsFromName` and inspected every
`result.expectedFailures` traceback. It again ran 21 tests, 18 expected failures,
in 9.164 s. All 18 failed at the intended assertion or at the receipt symlink
refusal, rather than an unrelated setup/import failure. Aggregate test/PREQUAL
command time, including the exploratory witness run and this audit, was about
12.5 minutes, below the requested approximately 20-minute budget.

The sandbox denies even `/bin/ps -p <this Python pid> -o pid=` with EPERM. Thus
the meter restart failures here are not evidence that the native KM003C path is
broken; native restart/crash-radius validation is outstanding. Likewise the
mock MBP clock and child-lifecycle witnesses are software proofs, not measured
native runtime/process-census evidence. MLX was never imported or exercised.

## Handoff

Changed files are this report and `tests/align/test_smoke_review_sol1.py` only.
No production fixes or approvals are implied. Witness commit: `d27c0fc87`
(`test(align): witness W1 smoke isolation and qualification gaps`). The separate
report commit is identified in the final handoff; nothing is pushed.

Open uncertainties: the native budget, injection offsets and process teardown
have not been measured; meter restart/crash radius cannot be certified in this
sandbox; the frozen series and installed-plan projection source schemas are
not yet supplied at this candidate. Their authoritative producer/binding format
belongs to the lead. This review does not invent a replacement scientific rule.

Next exact step: fix S4–S9 before any native smoke; fix S1/S2 and strengthen S3
before treating the corresponding PREQUAL PASS rows as those properties. Have
the lead independently review fixes and witnesses, remove the matching
expectedFailure decorators, then rerun the targeted modules and clean-clone
PREQUAL with genuine planning-only projections and completed W1 prerequisites.
Only in a lead-controlled MBP gap with **no real plan installed**, run the native
smoke, verify meter restart/crash radius and owned-process teardown, and measure
the total wall time. The native MLX/R0/model/launchd/KM003C/CPU-contention gates
remain the lead's responsibility outside this sandbox.

In particular, rerun `tests.align.test_w1_prequal` where stand-in meter signals
and process census are permitted; then run Part B of `W1-SMOKE.md` on the native
MBP and the provisioned MLX/checkpoint, R0 MLX, thermal MLX and SMC opt-in tests
listed by `optin-required`. No native claim is discharged by this review.
