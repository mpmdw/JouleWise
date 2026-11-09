# W1 smoke delta review — Sol seat 2

2026-11-08. Candidate: `ed65d9094` on
`origin/align/2026-11-08-w1-smoke-merged`. Review branch:
`align/2026-11-08-w1-smoke-delta-sol2`.

**Verdict: HOLD.** The earlier repairs are substantial, but isolation escapes,
an unbounded preparation route, a missed installed-job cleanup exit and two
false-PASS checks remain. These are within Ed's four blocking categories;
the hold does not demand general hardening or native proof from this sandbox.

Authority: the smoke-delta brief; `W1-SMOKE-AGREEMENT.md` §7 and its HARD
isolation ruling; `W1-SMOKE.md`; decision-log D-009 and D-186. The explicit
brief overrides coordination-file updates and the full-suite checklist.
No coordination state or production code was edited.

## D2-1 — Isolation still has a detached-entry escape and a check/write race

`scripts/align_v4_w1_smoke.py:56` creates the detached output's parent and
calls `detach()` before constructing a runner. It never invokes
`destination_violations`. With a new `--smoke-dir` under a synthetic production
checkout, the CLI creates that protected parent and reaches the spawn boundary.
The actual `detach` opens the sibling `.out` file before spawning. The child's
later refusal cannot undo those writes. The witness replaces the spawn with a
spy; no native command or real plan is launched.

`SmokeRunner._sequence` checks isolation and then calls `arm_main`, which uses
ordinary path-based writes and commands. The two deterministic TOCTOU witnesses
swap a directory immediately after the successful final check:

- Replacing `main/staging` with a symlink to a synthetic production directory
  redirects `smoke-next-arm-triage.json` there and still reaches the main arm.
- Replacing `<smoke-dir>/tmp` redirects the install command's `TMPDIR` into a
  synthetic production directory. A fake child writes through the supplied
  environment to prove the redirect.

The preexisting-symlink guard works; neither attack plants its link before
that guard. The race requires another writer able to rename smoke directories.
This is an explicit attack in the brief, not evidence of a spontaneously
occurring race. The HARD promise currently depends on that writer's absence.

Repair: route detached output creation through the same destination policy;
enforce containment when opening writable targets and launching commands.
A repeated pathname check alone still leaves a race. Use an ownership and
directory-handle strategy with non-following opens, or have the lead explicitly
rule a narrower trust boundary; do not silently claim race-safe isolation.

Witnesses: `IsolationDelta.test_detach_refuses_protected_destination_before_mkdir_or_spawn`,
`test_symlink_swap_after_final_check_cannot_redirect_packet_write`,
`test_tmpdir_swap_after_final_check_cannot_reach_command`.

## D2-2 — Preparation bypasses the remaining-budget runner and command TMPDIR

`SmokeRunner.isolate` invokes `isolate_fn` without passing its `cmd` runner.
The real `isolate` uses its own `subprocess.run(..., timeout=600)` for Git and
venv creation. With **one second left**, its first Git command still receives
600 seconds and no smoke command environment. Every subsequent isolate command
has that independent timeout. The production prepare function is likewise
called synchronously, outside `cmd`'s remaining-budget clipping.

The witness intercepts the first real isolate command before executing it and
records its actual keyword arguments. This does not require a long-running
fixture. Also, the default deadline clock is `time.time`, not monotonic elapsed
time. Passing the existing expired-budget/pre-arm tests therefore does not
prove a hard 2,700-second bound over the whole sequence.

Repair: pass the bounded runner and local command environment through isolation
and preparation, using one monotonic elapsed deadline. Keep wall-clock plan t0
separate. Reserve and bound cleanup time as part of the declared native limit.

Witness: `LifecycleDelta.test_isolate_commands_use_remaining_budget_and_local_tmpdir`.

## D2-3 — A command failure after installation can escape the outer cleanup

`arm_main` records `self.installed` only **after** `self.cmd` returns and the
session is re-read. `cmd` can raise `TeardownFailure` on a surviving command
group after that command has already installed a launchd job and published the
session state. The outer `finally` sees neither an owned job nor a contender,
so it skips teardown altogether.

The fake host executes its ordinary successful install, leaves the job loaded,
then returns the new `group_survived=True` result. `run()` correctly returns
nonzero but never calls uninstall, leaves the job loaded and writes no
unproven-teardown record. This is a failure exit in the new safety handling,
not a claim that the real installer has produced this outcome on an MBP.

Repair: establish an owned attempted installation before invoking the command,
then reconcile the session and installed identity in `finally`, including
timeouts, transcript/read failures and partial installs. Preserve identity
checks before uninstalling anything.

Witness: `LifecycleDelta.test_install_side_effect_is_cleaned_when_command_reports_surviving_group`.

## D2-4 — The deadline check still accepts a forged installed plan

`w1_prequal.check_deadline` checks two schema labels, the plan-id prefix and
two numeric declarations. It hashes the supplied file but never establishes
that the file is the installed plan or validates the complete plan schema.

The witness supplies only `schema`, `receipt_class`, `plan_id`, `window_max_s`
and `pack.programmed_span_s`. The production `NightPlan.from_mapping` refuses
it as malformed; PREQUAL nevertheless PASSes it with `span=0`, a required
17,700 seconds and a declared maximum of 20,000 seconds. A second witness
adds a top-level `programmed_span_s=0` alongside the actual-shaped
`hazard_window.programmed_span_s=26927`. Recursive first-match `_find_key`
selects the decoy and again PASSes 20,000 seconds instead of requiring 44,640.

Repair: validate the copied plan using the production schema, read the one
authoritative hazard span field, and bind the exact copied bytes/identity to
the intended installed or prepared session via an independently checked
locator/digest. A self-computed hash of an arbitrary supplied file is not that
binding. Do not follow any of the real data locators while implementing the
planning-only verification.

Witnesses: `AdmissionDelta.test_forged_installed_plan_is_refused`,
`test_decoy_span_cannot_override_actual_hazard_span`.

## D2-5 — Packet mutations still miss later leaves of each chain element

The nested **check status** repair works: a stand-in that rewrites an edited
`checks.capture_faults.status` to `pass` is detected. But `_mutations` edits
only the first sorted leaf of each `window_chain` / `calibration_windows`
element, rather than every nested field.

The new stand-in rebuilds a deterministic packet and ignores only the
`status` field of the second calibration-chain element. Every generated
mutation is correctly refused, including the C3 omission; `packet-tamper`
PASSes. A separate direct mutation of that one element's `status` is admitted.
Thus the probe can still certify an arm that fails the promised canonical
equality. This is a probe-coverage defect; the production arm is not accused
of that leniency.

Repair: walk every non-ignored leaf and structure in every check/chain
element, including removal/addition cases, and retain the admitted control
and specific refusal attribution.

Witness: `AdmissionDelta.test_packet_probe_rejects_arm_ignoring_one_chain_elements_later_leaf`.

## Repairs that hold within the exercised scope

The delta controls cover literal/resolved/relative write paths, `/private/tmp`
folding and escaped command TMPDIR; both published-but-unloaded night and
deadman plists; failed volume teardown and expired-budget prevention of the
main arm; a real TERM-ignoring descendant with closed output pipes; exact
series roster/source equality and source-hash refusal; nested check-status
leniency; and receipt static closure coverage including `scripts/`. All 233
paths returned by the current static closure walker are receipt-bound.
The earlier witnesses and production modules are recorded below with their
actual results. These controls do not qualify live hardware.

## Verification and handoff

All unittest modules run in separate processes, sequentially, with Python 3.13,
`-B` and the realpath'd
`TMPDIR=/private/tmp/jw-smoke-delta-sol2-27s0h_9x`. The new delta module runs
without a startup shim and supplies its own synthetic home/configuration.
For older modules and PREQUAL, a temporary `sitecustomize.py` substitutes a
synthetic `Path.home()` and substitutes only the configured real production
roots returned by `smoke.load_config`. This prevents even link-metadata reads
of the sealed paths. Synthetic test-owned roots, aliases, checkers, plan and
packet logic remain unchanged. This is disclosed review scaffolding, not an
unmodified native qualification run. The shim and clean clone live outside Git.

| Command (common environment as above) | Result | Seconds |
|---|---|---:|
| `python3.13 -B -m unittest -v tests.align.test_smoke_delta_sol2` | 15 tests; 7 controls pass, 8 property tests fail with 9 assertion failures (two subtests in the isolate case); no errors/skips/expected failures | 16.779 |
| `python3.13 -B -m unittest tests.align.test_w1_smoke` | 23 tests OK | 23.886 |
| `python3.13 -B -m unittest tests.align.test_smoke_review_sol1` | 21 tests OK | 11.102 |
| `python3.13 -B -m unittest tests.align.test_smoke_review_sol2` | 14 tests OK | 9.418 |
| `python3.13 -B -m unittest tests.align.test_w1_prequal` | 35 tests, 3 failures: two killed-meter cases; one pinned-R1 import failure caused by the initial safety shim (isolated rerun below) | 355.930 |
| `python3.13 -B -m unittest tests.align.test_w1_prequal.RouteTests.test_r1_route_is_pinned_at_its_armed_commit` | 1 test OK with the lazy safety shim | 3.128 |
| Clean-clone `python3.13 -B scripts/align_v4_prequal.py --w1-next w1 --jobs 1 --output /private/tmp/jw-smoke-delta-sol2-27s0h_9x/prequal` | exit 1, FAIL; exact candidate, `checkout_dirty=false`; 9 PASS / 7 FAIL / 1 WARN | 259.4 |
| `PYTHONPYCACHEPREFIX=/private/tmp/jw-smoke-delta-sol2-27s0h_9x/pycache python3.13 -B -m compileall -q joulewise tests` | exit 0 | — |
| `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` | exit 2: `PermissionError: [Errno 1] Operation not permitted: 'ps'`; census unavailable, not a clean result | — |

The first delta run (14.753 s) had one extra harness failure: the clean TMPDIR
control still contained its deliberately planted forbidden alias. Removing
that alias before the clean control fixed the test; the final run above has
only intended property failures, each audited at its assertion traceback.
Aggregate test/PREQUAL command time, including that exploratory run and the
isolated R1 rerun, was approximately 12 minutes, below the requested budget.

The initial safety shim eagerly imported this candidate's `joulewise` package.
That incorrectly made the older pinned R1 route import the current package
instead of its own checkout (`ImportError: cannot import name 'r1_arm'`).
The temporary replacement `lazy-safety/sitecustomize.py` patches on the
natural import of `w1_smoke`, preserving the probed checkout's package identity.
The exact failed R1 test then passes in a separate process. This third baseline
failure is a review-harness defect, not a product finding. The other module
runs and W1 PREQUAL used the first shim, loading the same candidate's package;
the original transcripts and shim are retained rather than overwritten.

The clean clone was created by local `git clone --shared --no-checkout`,
detached at `ed65d9094`, with `origin` removed. PREQUAL received no `--only`,
waiver, fabricated series projection or fabricated deadline projection.
Its PASS rows are arm CLI (13 cases), packet rebuild, packet tamper (97
mutations), calibration stop, escalation exit, R1→W1 chain, WP22, smoke kit,
and W1 arm route. WP22 reports 22 tests OK with one existing expected failure
in 62.553 seconds. The missing R1-filled kit/receipt/W1 plan and both absent
planning projections correctly block admission.

The two other FAIL rows, `km003c-launch` and `km003c-crash-radius`, again have
one reader stream and zero restarts. The synthetic injection still uses
`pkill`, and even `/bin/ps -p <this shell> -o pid=` is denied here with
`operation not permitted`. The prior Sol2 report identified this same
environment-induced failure. This run does not independently establish that
the native KM003C path is defective; rerun these checks with working process
enumeration or a fixture-owned PID injection. Do not waive the assertions.

The opt-in audit remains WARN: 134 listed tests, 14 marked covered and 120
requiring other routes. Native MLX/checkpoint, R0 MLX and thermal MLX tests
were not run here. The lead must run `tests.align.test_cache_checkpoint_native`,
`tests.align.test_r0_mlx_native`, `tests.align.test_thermal_mlx` and the MLX
case in `tests.align.test_decode_budget` on a provisioned native host, following
their opt-ins; also retain the SMC/KM003C/launchd host checks listed by PREQUAL.
No weights were downloaded for this review.

Local evidence root: `/private/tmp/jw-smoke-delta-sol2-27s0h_9x/`.

| Artifact | SHA-256 |
|---|---|
| `delta-final.log` | `21645ff70f44d34cd0d479870d7b88256fc70bdb5029255b80071642d109f1af` |
| `prequal/prequal-w1.json` | `760a6f8382d9af2850e41fab1fe0483275af42bc5aaf06cf4fd67a97dfe79164` |
| `sitecustomize.py` | `d6851de755d6d9d3c5e7db92e4495602972838b7489fd24dc85681029561d912` |
| `lazy-safety/sitecustomize.py` | `f34bc21f0a61c9cad01244abece02b8dd0e0afa62d7d91161e7adf27643c5d3b` |

Other transcripts are `delta.log` (exploratory), `w1-smoke.log`,
`review-sol1.log`, `review-sol2.log`, `w1-prequal.log`, `r1-route-rerun.log`,
`prequal-console.txt`, `ps-own-process.log` and `fixture-census.json` beneath that root. They are
synthetic/software evidence and were not promoted as measurement records.

Only `tests/align/test_smoke_delta_sol2.py` and this report are deliverables.
No full suite, network, model downloads, block-5 analysis, real measurement,
real restricted directory, external consult or delegation was used. No
coordination-state file was edited. The branch is local only; nothing is pushed.

Next exact step: the lead dispositions D2-1–5, fixes the accepted findings,
and reruns this module and the named production checks. A lead-controlled MBP
gap, with no real plan/job installed and no agent active during collection,
remains necessary for the actual ≤45-minute smoke, launchd unload/owned-reader
and contender teardown, KM003C restart/DC salvage, request-overlap flag and
native MLX gates. Keep those PROVISIONAL. Source identity for the installed-plan
copy and any narrower TOCTOU trust assumption are lead-owned open decisions;
this review does not invent either contract.
