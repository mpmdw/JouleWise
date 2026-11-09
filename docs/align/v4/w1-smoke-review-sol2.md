# Sol seat 2: merged W1 smoke review

Date: 2026-11-08. Candidate: `f6251227ae4d4258a6397230f6ff6e755a3fcb88`.
Branch: `align/2026-11-08-w1-smoke-review-sol2`.
Authority: the smoke-review brief, `W1-SMOKE-AGREEMENT.md` §§6/6a and
`W1-SMOKE.md`. **Verdict: HOLD.** The native runner has isolation escapes and
does not enforce its shutdown/budget promises. Several PREQUAL probes can
certify a weaker property than their row claims. These are concrete witnesses,
not a request for additional general hardening.

This review changes only the witness module and this report. It does not fix
production code, change registration, arm anything, or alter coordination state.
The current packet checks already fail correctly because the production arm
does not yet implement the ruled rebuild. The latent probe escapes matter when
the fixer makes that arm green.

## Blocking findings

### S2-1 — Isolation is checked too late, and incompletely

Locations: `joulewise/align/w1_smoke.py:174`, `:190`, `:478`, `:622`, `:654`;
`scripts/align_v4_w1_smoke.py:60`.

* `run()` creates the smoke directory and writes its log, then clones/copies the
  ledger and prepares, before the first isolation check. The CLI only tests
  whether the directory already exists. A new smoke directory under the
  synthetic production checkout's `runs/` is populated and only then rejected.
  This contradicts the runbook's promise that such a root is refused without
  writing there. The stated prohibition on other paths under home is also not
  implemented.
* `arm_fault()` calls `isolation_violations` without its `plan` argument. A
  past-t0 fault plan can name a production `claim_runs_root`, while its session
  state remains local, and still reach the install command. The witness also
  proves that the same checker **with** that plan catches the escape. The past
  t0 still prevents a real installation; it does not prove isolation of the
  commands and checks preceding that guard.
* The `readonly` exception is applied to every absolute string in the plan.
  The explicit write-key check inspects only state/inputs, not plan write keys.
  A plan's `custody_root` inside the production site-packages directory therefore
  returns **zero violations**. A read-only import exception must never authorize
  a custody/runs/ledger write. Its `startswith` test also lacks a path-component
  boundary.
* An isolation exception from a fault session is caught as an ordinary failed
  fault. The loop continues and installs the main smoke. No abort isolation row
  is recorded for that exception. This violates the HARD ruling that any
  isolation hit aborts before another arm.

Witnesses: all `IsolationWitnesses` except the passing symlink control. All
targets are disposable synthetic production directories; no real root was
probed. Existing symlink detection and distinct-ledger-inode tests pass.

Required repair: validate destination containment before **any** mkdir, detached
output-log write, clone or prepare; check every fault's actual plan; distinguish
read paths from write paths; make any isolation hit terminal for the run.

### S2-2 — Failed teardown and an expired budget still reach the main arm

Locations: `w1_smoke.py:319`, `:524`, `:564`, `:580`, `:586`, `:622`.

* A failed disk-image detach is stored in a teardown result but does not change
  `arm_fault()`'s return value or stop `run()`. The main arm is attempted with
  the injected image still mounted. The parser notices later. A production disk
  gate may refuse that arm, but that is not teardown and does not restore the
  host.
* The 2,700-second deadline does not guard preparation, the fault loop, restaging
  or `arm_main`. The runner can install after its global deadline, as the fake
  clock witness demonstrates. Fixed fault sleeps can cross the deadline;
  terminal unload polling allows another 300 seconds and the native R1→W1
  probe another 900. There is no outer `finally` to unload an owned smoke job
  when terminal polling, an injection or another post-install operation fails.
  A final `wall-time` FAIL is retrospective, not a 45-minute stop. The builder
  also obtains its plan limit from full-kit sizing, not from the smoke's
  remaining global budget (`bytes_h_session.prepare` / `plan_inputs`). Native
  duration and cleanup are therefore still unproved.
* `bounded_run()` stops escalation when `communicate()` returns after TERM.
  A descendant that ignores TERM and has closed its pipes can survive after
  its group leader exits. The mocked process witness sees TERM and no KILL.
  After a contender wait timeout, the runner sends KILL but never waits again,
  yet logs it as stopped.
* The meter injection uses global `pkill -KILL -f scripts/km003c_monitor.py`,
  rather than the reader identity from this smoke's journal. This gives it
  host-wide reach. Gap guards are useful but do not scope the signal itself.

Witnesses: `NativeSafetyWitnesses`. Existing tests already detect leftover
mounts and excess wall time **in parse**, but do not prevent continuation.

Required repair: one monotonic deadline, remaining-budget command timeouts,
pre-arm deadline checks, and ownership-checked cleanup in `finally`; abort on
failed teardown; target and reap only this smoke's processes. Before native
admission, prove no installed smoke job/reader/contender remains on each failure
exit. The current tests use fake hosts and are not MBP validation.

### S2-3 — Both packet probes can pass an arm that accepts an edited nested status

Location: `w1_prequal.py:508`.

`_mutations()` changes/removes top-level keys, adds a field, and edits the basis
of only the first sorted check. It does not change the nested status of each
check. A rebuilding arm that silently rewrites
`checks.full_desk_gate.status = 'fail'` to `'pass'` passes **both** packet probes.
The witness separately supplies that exact edit and proves the lenient arm
admits it. `packet-tamper` nevertheless reports all 12 generated mutations
refused and PASS. This falsifies the §6a claim that a lenient arm is caught.

Witness: `PacketWitnesses.test_both_packet_probes_reject_an_arm_lenient_on_nested_status`.
Extend mutations to nested leaves, removals and additions in each gating check
and chain element, retaining the positive control and the two exact ignored
fields. Current unknown-commit, expiry, top-level mutation and omitted-attempt
checks remain useful.

### S2-4 — Deadline admission validates an unbound declaration

Locations: `w1_prequal.py:890`, `:946`.

A W1 projection with `window_max_s=0`, one zero-duration segment and zero
overheads PASSes. No installed plan is opened or identified; the segment/retry/
batch schedule is never compared with its source. Hashing the supplied
projection as `plan_sha256` does not establish that it projects the installed
plan. A stale or incomplete declaration can therefore green-light an
undersized real schedule.

Additionally, `kind not in (ctx.next, 'd')` accepts a D projection for **either**
R1 or W1. This also bypasses the R1-only 67,371/96,427-second floors. The runbook
explicitly requires the kind to match the next measurement.

Witnesses: the two deadline tests in `ProjectionWitnesses`. Bind to exact source
plan bytes and independently derive/check schedule completeness. Require the
actual next kind; introduce an explicit D gate if needed. An absent projection
correctly fails today.

## Additional false-PASS coverage gaps

**S2-5 — Series source hash is not a roster binding.** At
`w1_prequal.py:931`, a source declaring only W1 and T1 is hashed correctly and
accepted alongside an invented projected C1–C8 roster. The fixed-eight predicate
is tested on the projection alone. No source schema, frozen/committed status,
window order or per-pair counts are verified against that source. Witness:
`ProjectionWitnesses.test_series_projection_must_match_hashed_source_roster`.
Define the owning source-manifest schema and derive/compare the projection; a
valid source digest alone is insufficient. No actual frozen manifest was
available in the candidate, so this is a supplied-input escape, not a claim
about a real registered series.

**S2-6 — Receipt coverage excludes scripts.** At `w1_prequal.py:749`, the
uncovered-set comprehension filters to `joulewise/`, although `executed_closure`
also returns `scripts/`. With the real validator's exact/mismatch/working-drift
self-tests retained, a stand-in ready registration and a newly unbound imported
script yield PASS. Witness: `ReceiptWitnesses`. Check all first-party closure
paths. **Current-tree qualification:** all 230 paths returned by this static
walker are in `ARTIFACTS`; I found no currently unbound path through this walker.
The witness demonstrates a hole in the proposed guard, not a present missing
receipt artifact. Dynamic/shell closure coverage remains the separate existing
registration tests' responsibility.

## Verification and runtime

All modules ran separately with Python 3.13 and `-B`. No full suite, network,
model-weight download, native MLX run, measurement, production install or real
restricted-directory access was performed. Tests used repository code and
synthetic temporary checkouts/ledgers/hosts. No agents were delegated and no
external consult was used. Coordination files were left untouched as instructed.

| Command | Result | Measured seconds |
|---|---|---:|
| `python3.13 -B -m unittest tests.align.test_w1_prequal` | 34 tests, 2 failures (killed-meter cases) | 273.525 |
| `python3.13 -B -m unittest tests.align.test_w1_smoke` | 19 tests OK | 23.306 |
| `python3.13 -B -m unittest tests.align.test_v4_prequal` | 36 tests OK, 3 tokenizer-tier skips | 11.196 |
| `python3.13 -B -m unittest tests.align.test_smoke_review_sol2` | 14 tests, 13 intentional property failures, symlink control passes | 3.251 |
| Clean-clone `scripts/align_v4_prequal.py --w1-next w1 --jobs 1 --output …` | exit 1, FAIL, `checkout_dirty=false`; 7 PASS / 9 FAIL / 1 WARN | 440.3 |

The first witness run (before adding the read-only-path witness and the R1
subcase) ran 13 tests in 6.130 seconds: 12 assertion failures and one passing
symlink control. These tests intentionally assert the required properties;
their failures are executable repair criteria, **not** claimed green coverage.
No skip or expected-failure decorator hides them. The final witness transcript
is `/private/tmp/jw-smoke-review-sol2-axzrs5o8/witness-final.log`.

The base launcher tests pass against this clone's `origin/main`, including the
semantic `runner.json` comparison and the unresolved-venv negative control.
The arm CLI module's help/flag/control checks and ordinary smoke path tests
pass. The two initial KM003C failures report no restart into stream-002; do not
infer from that that the production pre-kill DC salvage is broken. The crash
radius probe did not reach its member assertion. The clean PREQUAL result and
the distinction between environment/injection failure and a production defect
are recorded below.

Clean PREQUAL execution: a fresh `git clone --shared --no-checkout` of this
clone, detached at the candidate, no untracked changes and no production ledger;
`origin` removed. Command:

```sh
python3.13 -B scripts/align_v4_prequal.py --w1-next w1 --jobs 1 \
  --output /private/tmp/jw-smoke-review-sol2-axzrs5o8/prequal
```

The working directory was
`/private/tmp/jw-smoke-review-sol2-axzrs5o8/candidate`. No `--only`, waiver or
fabricated projection was supplied. Serial probes avoid adding concurrent test
load to the user's running analysis. Outputs remain under that synthetic tmp
root, outside git. Final result: **exit 1, FAIL in 440.3 s**, exact candidate
commit, `checkout_dirty=false`. JSON and Markdown are in `prequal/` beneath
that root.

* PASS: `arm-cli` (12 cases), `calibration-stop`, `cal-escalation-exit`,
  `r1-w1-chain`, `wp22-dry-run`, `smoke-kit`, `arm-route` (all 7 steps).
* Correctly blocked pending work: `packet-rebuild`, `packet-tamper` (no rebuilt
  packet); `kit-ready` (R0/R1 placeholders); `receipt` (four absent artifacts:
  R1 soak reference, U3 bar, W1 plan, WP19 receipt); `series-manifest` and
  `deadline` (no projections); `w1-window-max` (R1-filled plan absent).
  W1 sizing code paths still agree at 26,927 s programmed / 44,640 s maximum.
* `km003c-launch` FAIL in 65.1 s and `km003c-crash-radius` FAIL in 44.2 s:
  the killed fixture again reports starts=1, restarts=0, one stream. These
  two checks are not accepted as evidence of a production crash-radius defect.
* `wp22-dry-run` PASS in 223.6 s, including its full module: **20 tests in
  211.671 s, OK (expected failures=1)**. This is the existing documented
  expected failure, not a new exemption introduced by this review.
* `optin-required` WARN: 134 required opt-in tests listed, 14 covered here,
  120 still needing native/base PREQUAL/provisioned fixtures. This remains
  disclosed debt, not an accidental PASS of those 120 tests.

The module runs, first/final witnesses and serial PREQUAL together took about
12.6 minutes of measured test/command time; no tests were parallelized. One
additional synthetic killed-meter diagnostic brought the total to approximately
13.5 minutes, within the brief's test budget.

### Killed-meter false refusal: confirmed environment limitation

After the serial PREQUAL and final witnesses completed, I ran one isolated
`python3.13 -B` diagnostic calling `_meter_window(kill_mid=True)`, reading only
that harness's synthetic custody stderr before `census.stop()` and
`case.doCleanups()`. Driver exit was 0; the reader had starts=1, restarts=0,
no exits and no start failures. Its ordinary final SIGTERM stop was recorded.
`night/chain.stderr.log` contained:

```text
sysmon request failed with error: sysmond service not found
pkill: Cannot get process list
```

The fault injection never killed the reader. These are **environment-induced
false refusals of the synthetic restart checks**, not evidence against the
production salvage fix. Do not weaken the meter/DC assertions or waive their
native proof. Prefer killing the fixture's own recorded PID (which also removes
its process-list dependency), or rerun the unchanged probes in an environment
that supports process enumeration. The repaired/native DC path remains
unverified here. This diagnostic did not touch a real meter or measurement.

## Handoff

First fix the isolation and native ownership/cleanup exits (S2-1/2), then close
the packet/deadline/source-binding coverage gaps and rerun these witnesses plus
the named targeted modules. Supply the actual frozen planning projections and
registered W1-ready kit before seeking a PREQUAL PASS; do not waive missing
registration evidence into readiness.

The lead must run the repaired detached native smoke in a clean MBP gap, after
all real plans/jobs are disarmed and with no agent active during collection.
That run must measure wall time ≤2,700 seconds, verify PID-scoped meter restart,
pre-kill/straddling/post-restart DC, request-overlap contention, volume teardown,
terminal job unload, and absence of owned processes. MLX/native execution is
unavailable in this sandbox. No native runtime or hardware correctness is
claimed here.

Open question: name the authoritative installed-plan and frozen-series source
schemas for projection verification (the current code has none). The native
timing/fault-offset assumptions, real plan admission and DC salvage still need
the lead's MBP run; sandbox stand-ins cannot settle them.

Commits: `9a2519def` adds the witness module; the subsequent report-only commit
adds this review. No push or merge was performed.
