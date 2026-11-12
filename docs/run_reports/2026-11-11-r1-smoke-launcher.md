# Agent-free R1 follow-up smoke launcher — 2026-11-11

Status: round-2 executing-review fixes implemented and synthetically exercised; **native smoke and RL-86 merge reconciliation remain owed**. The independent review is [recorded here](2026-11-11-r1-smoke-launcher-executing-review.md); the round-2 section below supersedes the original implementation details. Branch `ops/2026-11-11-r1-smoke-launcher`, based exactly on `9b4817f362524a443d92547453d68023faa1bd95` (`ops/2026-11-11-w1-presign`). No night was armed or measurement captured. No model weights, network, real host-setting command, or sealed custody was accessed.

## Intake and scope

Read the magistrate's refusal record from `origin/main` (`42d7450bd`), the R1 runtime contract, M0, the targeted restart/queue sections, orchestration, D-050, and the speed toolbox from `origin/main`. No active stop card. This direct code-only brief takes precedence over the ordinary queue. Coordination state, the ten condition-13 paths, and `scripts/align_r1_followup_kit.py` are unchanged. The real soak path below is argument text only; this session never inspected it. No delegation, consult, full suite, or MLX execution.

## Implementation and rationale

Chose the named-runner generalisation. `launch_align_r0.py launch --runner-kind r1-smoke` uses the same fence lock/publication, one-shot plist, exit wait, Spotlight pause/resume and self-bootout shell. The default remains `r0`; its runner JSON list and argv, including check selection and default `--keep-going`, retain their original bytes. R1 uses a tagged JSON spec, so the outer helper delegates display preparation to the R1 runner after its feeds start. Historical `align-r0` labels and `r0-launches` storage names are retained deliberately; the watchdog treats the fence generically. The shell wrapper is unchanged.

`scripts/run_align_r1_smoke.py` performs:

1. Deadline, AC, wildcard loaded-night-agent census, condition 13 against the checkout's full HEAD, and soak-file existence.
2. KM003C startup through `driver.production_seams(...).meter_argv`, `MonitorRequest`, `MonitorSupervisor(name="meter")`, and `await_meter_ready`/`MeterLiveness`. Plain QoS, normal create-once `hazards/meter/stream-NNN.jsonl`, `meter_supervision.jsonl`; actual fresh DC-in required before proceeding. Ordinary supervisor restarts remain available; neither smoke part is restarted.
3. Agent journal through `run_night.agent_census` and `_append_census` every `CENSUS_INTERVAL_S` (30 s). Volume journal through R1's `VolumeWatch.census` (which calls the existing external-volume census/check), every 60 s. Both sample immediately on start. These are cooperative producers in the runner's poll loop, with no separate process/thread to orphan. Positive/unreadable censuses fail the smoke.
4. Observed AC `powermode == 0` (Automatic), R0's display-sleep helper and 300 s dwell. As with R0, display-command failure is recorded rather than treated as a refusal.
5. Exactly `smoke --part A --output ROOT/part-a --soak-reference SOAK`; only exit 0 admits exactly one corresponding Part B call into `ROOT/part-b`. Each part has one 1,800 s budget, bounded further by the common work deadline. A blocked census cannot extend capture: `PartDeadline` reuses the night's independent `_WindowDeadline` enforcer/cancel machinery and process-group teardown, with a smoke-specific deadline receipt instead of a fabricated night plan.
6. Finally: Automatic setter/readback under the ordinary host lock, stop volumes/agents/meter independently, and create `runner_receipt.json`. Every step has rc/start/end clocks; actual part dispatch flags distinguish spawn failure from a running part; feed files have post-stop SHA-256s. Nonzero Part A rc is preserved. Cleanup failures make the runner nonzero. A failed cleanup step cannot skip later cleanup steps.

The runner stops new work 370 s before the fence deadline; the outer helper reserves 190 s before its own timeout, then permits 180 s of termination cleanup. This covers the shared part-group proof (up to 70 s), meter stop/proof (up to 90 s), and Automatic setter/readback (20 s), plus the parent's margin. Temporary signal handlers defer interruption only while owned child handles are registered; signal masks are not inherited blocked by the meter. Repeated start/stop, including stop-before-start, creates no extra producer. Even an already-exited leader receives a group-absence proof.

Added the new runner to `_NAMED_ARTIFACTS` and the unsigned registration receipt template, strict by default, because the watchdog → launcher execution closure reaches it. This changes no condition-13 source. The one timing-map line is an insertion only: 13.883 s from the final local synthetic module run, a scheduling hint rather than a hosted timing or throughput claim. No batching or decision caching was added.

## Failing-first tests and mutants

The new module was first run with the runner absent, then with an empty runner: all 12 initial test cases were red (15 reported errors including subtests). Additional witnesses were run red before their fixes: expired deadline, actual-dispatch accounting, fresh DC-in, stop-before-start, interruption during meter acquisition, and a blocked census extending a part. Initial harness defects were corrected: its fake group census incorrectly classified `pgrep -g` as a powermode query, and repeated isolated part tests shared a create-once deadline directory. Final tests use distinct roots and explicit owned-feed cleanup on harness failure.

The final new module includes a real fake-launchd handoff through the unchanged shell, real runner orchestration, the existing registered `FAKE_METER`, and synthetic part processes. It proves no output before the magistrate exits, A/B ordering, cleanup on TERM in Part A, unloaded service/fence removal, and absence of the exact meter/part PIDs afterwards. Host interfaces are faked; the fixture process control is limited to owned synthetic children. The part fixture uses a unique `jw-r1-smoke-fixture-XXXXXXXX` tempfile namespace, registered in `tests/fixture_signatures.json` with positive and production-negative census witnesses. No generic production kit command is registered.

Eleven in-memory source mutants are killed by assertion failures (not import/setup errors): changed R0 argv; missing power-order step; admission of B after failed A; omitted meter/agent/volume cleanup (three mutants); omitted process-group proof; corrupt receipt SHA; removed wildcard night-agent refusal; bypassed condition 13; and missing fresh DC-in refusal. Mutants do not edit repository source or study files.

## Verification

Commands use Python 3.13, `-B`, unittest and the installed host-command guard. Full discovery is intentionally not run under the standing host-load rule. The required final regression sequence ran serially. A few short failing-first microtests inadvertently overlapped an earlier allowlist/inventory scan; those overlaps were limited to synthetic tests, and no existing analysis job was touched.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_r1_smoke_launcher` | 24 tests, OK, 13.883 s at final source/fixture bytes; includes 11 killed mutants |
| `python3.13 -B -m unittest tests.test_magistrate_desk_fence` | 42 tests, OK, 69.903 s |
| `python3.13 -B -m unittest tests.align.test_r1_followup` | 12 tests, OK, 54.515 s |
| `python3.13 -B -m unittest tests.hazards.test_refusal_allowlist` | 23 tests, two inherited failures, one skip, 114.580 s; own 41 keys match |
| `python3.13 -B -m unittest tests.align.test_v4_executed_closure` | 6 tests, OK, 22.471 s |
| `python3.13 -B -m unittest tests.align.test_v4_dynamic_closure` | 10 tests, OK, 68.748 s |
| `python3.13 -B -m unittest tests.test_host_command_sites` | 2 tests, OK, 28.365 s after listing the three new literal command sites and their fake seams |
| `python3.13 -B -m unittest tests.align.test_v4_prequal` | 36 tests, OK, 3 skips, 18.266 s |
| `python3.13 -B -m unittest tests.align.test_v4_registration.R1ExecutedSourceTests` | 2 tests, OK, 1.560 s |
| `python3.13 -B -m unittest tests.test_fixture_orphan_census.FixtureOrphanCensusTests.test_r1_smoke_part_fixture_has_a_unique_temporary_namespace tests.test_fixture_orphan_census.FixtureOrphanCensusTests.test_required_fixture_signatures tests.test_fixture_orphan_census.FixtureOrphanCensusTests.test_nonfixtures_do_not_match` | 3 synthetic tests, OK, 0.017 s; live process-table cases excluded |
| `python3.13 -B -m compileall -q joulewise tests scripts/run_align_r1_smoke.py scripts/launch_align_r0.py` | exit 0 |
| `git diff --check` | exit 0 |

The first required allowlist run was already red against this checkout's inherited entries: 23 tests, two failures, one skip, 103.170 s. Baseline versus current site-difference counts are identical: three unlisted, two miscounted, two changed guards, zero stale. None concerns either launcher file. The inherited sites are `driver._run_hazard_night_body` re-raise, watchdog `_decide` FENCED/HOLD_UNSAFE, watchdog `_launch_fence`/`decide` counts/guards, and `harvest.archive_sources`'s `archive_copy_mismatch` guard. There were 11 inherited scope gaps; 10 remain after the explicit launcher/dependency declarations, with no new undeclared dependency. Unrelated source/entries are preserved for their owning seats. After the final signal-registration wrappers, a focused scanner comparison again proved all 41 owned keys/counts/guards equal the allowlist; no unrelated source changed.

## Refusal census / RL-86 handoff

Local census adds 25 current launcher keys (the inherited 24 plus one) and 16 new-runner keys. The counts and guards for these two files match exactly. Four unchanged engineering dependencies are explicitly marked `r1_smoke_existing_dependency`, with RL-86/w1-p2c ownership and **no claim of fresh refusal review**: `align_r0_checks.py`, `align_r1_followup_kit.py`, `align_r1_rehearsal.py`, and `v4_registration.py`. Reconcile those declarations with the parallel census before live use; they are not blanket authority to bypass that review.

Every new refusal key, in `(file, function, kind, detail)` form:

| File | Function | Kind | Detail |
|---|---|---|---|
| `scripts/launch_align_r0.py` | `launch` | raise | `ValueError\|r smoke requires` |
| `scripts/run_align_r1_smoke.py` | `ac_power` | raise | `ValueError\|r smoke requires` |
| same | `night_agents` | raise | `ValueError\|loaded night agent` |
| same | `read_power` | raise | `ValueError\|r smoke requires` |
| same | `restore_power` | raise | `ValueError\|automatic restore blocked` |
| same | `AgentFeed.sample` | raise | `ValueError\|agent census refused` |
| same | `VolumeFeed.sample` | raise | `ValueError\|volume census refused` |
| same | `MeterFeed.start` | raise | `ValueError\|km c supervisor` |
| same | `MeterFeed.start` | raise | `ValueError\|km c has` |
| same | `work_remaining` | raise | `TimeoutError\|r smoke work` |
| same | `part` | raise | `TimeoutError\|part exceeded its` (count 2) |
| same | `part` | raise | `RuntimeError\|part process group` |
| same | `run.step` | raise | `StepFailed\|row[rc]` |
| same | `run.step` | raise | `<reraise>` |
| same | `run.interrupted` | raise | `SystemExit\|128 + signum` |
| same | `run.soak` | raise | `ValueError\|soak reference file` |
| same | `<module>` | raise | `SystemExit\|main()` |

One existing launch key changes guard, not count: `(scripts/launch_align_r0.py, launch, raise, ValueError|measurement checkout runner)`, now `cef3647b206ff276`, because config is required only for R0 and R1 uses its own runner. No other inherited launcher key changes count/guard. The scanner strips digits from message stems (`R1`, `KM003C`), which explains the literal key spelling above.

## Exact magistrate start / check / run sequence

These commands are a **future native handoff**, not commands executed here. The independent executing review and round-2 fixes are recorded below. Before native use, reconcile RL-86 and select the committed merged head descended from `9b4817f36`. Set `PY` to the already installed, pinned measurement venv; do not resolve its interpreter symlink or download weights. Set `MAGISTRATE_PID` to the real magistrate process that will exit, not a tool-shell PID. `CUSTODY` must be the watchdog's actual configured root; its default is printed below as text only.

Start/check while the magistrate is still alive:

```sh
cd /Users/edr/code/jw-wt/r1-followup-smoke
REPO="$PWD"
: "${PY:?Set PY to the existing pinned measurement-venv interpreter}"
: "${MAGISTRATE_PID:?Set the actual exiting magistrate process PID}"
CUSTODY="${MAGISTRATE_WATCHDOG_CUSTODY_ROOT:-/Users/edr/night-custody/magistrate}"
SOAK=/Users/edr/night-align/r1-20261111T043229Z/night/align-r1/soak_reference.json
OUT="$REPO/.desk/r1-followup-smoke-$("$PY" -B -c 'import time; print(time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()))')"
unset JOULEWISE_R0_TEST_DISPLAY_DWELL_S JOULEWISE_HOST_STATE_DIR
git status --short --branch
test -z "$(git status --porcelain)"
git merge-base --is-ancestor 9b4817f36 HEAD
"$PY" -B -c 'from pathlib import Path; import subprocess; from joulewise.align.apple import v4_registration as r; root=Path.cwd(); head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(); print(r.verify_r1_executed_sources(root,{"executed_commit":head}))'
"$PY" -B scripts/launch_align_r0.py preflight --disk-path "$REPO"
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+9000)')"
"$PY" -B scripts/launch_align_r0.py launch \
  --runner-kind r1-smoke --repo "$REPO" --python-bin "$PY" \
  --output "$OUT" --soak-reference "$SOAK" --disk-path "$REPO" \
  --custody-root "$CUSTODY" --magistrate-pid "$MAGISTRATE_PID" \
  --deadline "$DEADLINE" --exit-wait-seconds 180 --start-wait-seconds 30
```

Require launch exit 0 and its printed `next: exit the magistrate session now` with a claimed fence. **Exit the actual magistrate session immediately and close every other agent.** An idle agent or an exited tool shell does not satisfy this step. No agent should poll progress during capture.

The unchanged shell then runs exactly: `handoff` (claim fence / wait for the magistrate PID to disappear), launcher `preflight`, Spotlight pause, launcher `run --deadline ... --runner-spec ... --pmset-bin ...`; R1 starts feeds, observes Automatic, sleeps the display/dwells, then runs the two kit commands. Do not invoke either `run` or bare kit `smoke` directly from an agent session.

On the next permitted activation, after the job has ended, check the saved `OUT` and the launcher's printed job directory. Receipt check (set `OUT` to that same new directory, not a new timestamp):

```sh
"$PY" -B - "$OUT" <<'PY'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1])
r = json.loads((root / "runner_receipt.json").read_text())
print(json.dumps(r, indent=2, sort_keys=True))
assert r["rc"] == 0 and r["parts"] == {"A": True, "B": True}
for feed in r["feeds"].values():
    assert feed["stop"]["proven_stopped"]
    for f in feed["files"]:
        with (root / f["path"]).open("rb") as h:
            assert hashlib.file_digest(h, "sha256").hexdigest() == f["sha256"]
PY
```

Also require the one-shot job to have unloaded and its owned desk fence to be gone; inspect the job's stdout/stderr for cleanup failures. A partial/failed smoke returns to the lead; do not extend, retry a part, or reuse either output directory.

## Limits, open items, next step

Synthetic lifecycle evidence is not native hardware validation. The lead must run the agent-free A/B smoke outside this sandbox with the real existing weights, KM003C, AC/Automatic readback and soak reference, then inspect sampler/Tf08 coverage, D-load duration, censuses, feed liveness and all cleanup receipts before using the result. No native MLX tests were run here; importability alone does not provide a Metal device. No B5 analysis pipeline ran.

Automatic restoration blocked by another host lock is recorded as failure, never forced through another measuring night. SIGKILL/power loss cannot execute a finally path or guarantee a receipt, as with R0; ordinary errors, TERM/INT/HUP and bounded part timeouts are covered. The global fixture census command would invoke a real host process-table binary, so it was not run under the brief's no-real-host-command rule; the end-to-end tests instead prove absence of their exact owned meter/part PIDs. No installed skill or external integration was used.

Changed files: the two launcher/runner scripts; the new test module; the strict artifact inventory and receipt template; refusal and host-command allowlists; the fixture registry and its synthetic census test; one inserted test-timing line; and this report. Implementation commit: `97fcf7f207ec7d2816c5aec637c8867f5ed185c6` (`ops: launch R1 follow-up smoke agent-free with shared feeds`). A subsequent report-only commit records this receipt. Post-commit `reg.verify_r1_executed_sources` against that full HEAD passed; protected-source/state diffs are empty and the timing diff is exactly one insertion. The working tree was clean after the implementation commit. No push. Next exact step: lead's independent executing review of this branch, adjudicate the documented census baseline/dependency declarations with w1-p2c, then the native handoff above. Coordination-state updates remain lead-owned.


## Round 2 — executing-review fixes (2026-11-11)

Continued the brief's existing local branch `ops/2026-11-11-r1-smoke-launcher` from `2d54da7e9`.
Read the executing review in full first, then M0, targeted intake/queue state (no active stop card),
AGENTS/CLAUDE, orchestration, D-050, the runtime contract, and the speed toolbox from `origin/main`.
This direct [AGENT] correction outranks the ordinary queue; the brief explicitly leaves all coordination
state with the lead. No coordination state or condition-13 path was edited. No delegation, skill,
network, measurement-data access, model download, full suite, B5 analysis, or native MLX execution.

### Disposition and implementation

- **H-1 / L-2 / L-3:** `launcher.r1_part_caps()` reads only the bound local runtime JSON and calls
  `r1_runtime.smoke_post_g0_budget(STEP_QUIET_S, config["step"]["deadman_s"])["total"]`.
  A is **1,920 s**; B is **4,520 s** with the current config. Both the launch admission and the
  runner use this helper, without caching. Before spawning either part the runner requires its full
  cap to fit before `deadline - WORK_RESERVE_S` (370 s). A short fence refuses without spawning;
  a fence expiry during work says **work deadline**, while a part-cap expiry names the actual runner cap.
  The successful part receipt records `cap_s`.
- Part A's kit clock is private and starts after the kit's condition-13/config checks. Rather than
  alter the protected kit or infer its private `started` from an output file, the requested extra
  120 s covers startup and final work outside the kit's own 1,800 s verdict. The runner cap still
  includes startup; an extraordinarily slow startup exceeding that margin can still exhaust it.
  This is the review's explicit A-margin remedy, not evidence of a measured startup bound.
- **M-1:** restore is eligible only after this runner successfully completed `read_power`.
  Earlier exits record `no_power_read` and do not acquire the host lock or issue any restore command.
  Under the host lock, `os.path.lexists(powermode.host_marker_path())` returns `foreign_marker_left`
  without reading/removing the marker or setting power mode. Night-agent census now precedes even
  the AC getter, so a loaded foreign W1 scenario issues **no pmset at all** in this runner.
- **M-2:** volume census runs at feed start, before A, before B, and close. `VolumeFeed.poll()`
  performs no work. The close census runs after all owned feeds have stopped, so its multiple
  bounded mount/diskutil probes cannot delay meter teardown. Agent census remains at feed start and
  every 30 s. Agents start before the meter. The terminal volume census retains per-probe
  timeouts/retry rather than an aggregate bound: pathological serial probe timeouts can still
  delay or lose the terminal receipt at the outer timeout, after producer-stop attempts.
- **L-4 / L-5 / L-6 / L-7 / L-8:** only R1 plists get `ExitTimeOut = 400` (two 180 s cleanup
  layers plus 40 s margin). Meter supervisor receives `identity=night.observe_identity`. The configured
  `--pmset-bin` reaches `display()`. The R1 fake-launchd witness holds the magistrate alive beyond
  its 0.5 s dwell seam and checks handoff entry/return plus absent output/meter journal; the
  skip-magistrate-wait mutant is killed directly in this R1 witness.
- **Deadline:** the command sequence above now uses `DEADLINE = now + 9000`. `launch` refuses less
  than A+B+dwell+370 = **7,110 s**, before creating custody/job/fence files. This is a structural
  minimum, not an allowance for magistrate-exit and startup latency. The review's full estimate is
  about 7,440 s; 9,000 s retains slack, and the per-part admission check still protects against delay.
- **Report only, L-1:** an unmeasured agent census still aborts a running part. The night's retry
  policy was not transplanted. This is a known capture-completion limitation for the lead to assess.
- **M-3:** no trial merge or unrelated refusal repair. RL-86 still owns reconciliation and sign-off
  on the `protects` wording. Both new round-2 rows are NUMBER_INTEGRITY engineering-smoke refusals.
  The new cap-helper import also explicitly declares the unchanged `r1_runtime.py` dependency under
  `r1_smoke_existing_dependency`; it calls only the post-G0 budget arithmetic, and this is not a fresh
  review of the runtime module's refusals. RL-86 must retain/reconcile that fifth declaration.

R0 `runner.json` and plist bytes are compared to `2d54da7e9` for both default keep-going and explicit
`smc,battery`/no-keep-going variants, normalizing only the synthetic temp root. The argv comparison
also passes. The shell wrapper and R0 runner branch, including its **5 s** terminate wait, have no diff.
`scripts/test_timings.json` is unchanged: no replacement of the existing timing row and no new module
requiring an inserted row. No throughput saving is claimed.

### Verification and fixture corrections

All tests use unittest/Python 3.13 with the installed test host-command guard, one module at a time,
and the requested `nice -n 10` prefix. **The sandbox prints `nice: setpriority: Operation not permitted`**
and then executes Python, so reduced scheduling priority could not be established. Total test wall time
remained below the brief's approximately 20-minute ceiling. Logs and synthetic TMPDIR are under
`/Volumes/JW-EXT/jwsol/squeeze/r1-smoke-launcher-r2/tmp/r1-smoke-r2/`; the review harness was inspected
but no removed review worktree was recreated. Early scratch logs were moved from this clone's `tmp/`
to that writable external scratch root after their fixtures ended.

The baseline R1 module passed 24 tests (13.465 s). First updated run: 36 tests, one failure and one
error (26.746 s): an uninitialized mocked volume record list, and a wait witness still dependent on
slow runner import. Both fixture defects were repaired. A second run passed 36 (16.534 s).
The first updated end-to-end run also allowed the newly added identity callback to execute read-only
`/bin/ps` on owned fixture PIDs; this deviated from the no-real-host-command brief. It was corrected
by faking `night.observe_identity` in the child fixture. No host-setting command ran. Final synthetic
runs fake that observer, host probes/setters, meter argv, and group census; fixture signals target only
owned synthetic PIDs/groups. The normal and TERM paths assert owned meter and part PIDs are absent.
The global fixture-orphan census was not run because it would execute real host `ps`.

The final inspection moved terminal volume census after owned feed stops; the affected R1 module
passed again (36 tests, 17.212 s). The first allowlist run (23 tests, 121.684 s, two failures/one skip)
confirmed the inherited site differences and also caught one new undeclared dependency from the cap
helper to `r1_runtime.py`. Its explicit unchanged-dependency declaration removes that new scope gap;
the final allowlist run is recorded below.

The final R1 module has 36 tests and 14 killed source mutants (assertion failures, no setup errors):
the original 11, the 1,800 s Part B cap, removed full-cap-before-start admission, and skipped magistrate
wait. A simulated B runs to 2,000 s without waiting in real time; A and B are independently refused
when one second short of their full caps. Additional witnesses cover the dynamic runtime total,
short launch admission, foreign marker/loaded night with no pmset, marker preservation after a read,
four volume boundaries, agent cadence/order, configured display bin, supervisor identity and R1 plist grace.

Final command results (same TMPDIR and `nice -n 10 python3.13 -B -m unittest MODULE` prefix):

| Module / check | Result |
|---|---|
| `tests.align.test_r1_smoke_launcher` | 36 tests OK, 17.212 s; 14 killed mutants |
| `tests.test_magistrate_desk_fence` | 42 tests OK, 64.205 s |
| `tests.align.test_r1_followup` | 12 tests OK, 45.480 s |
| `tests.test_host_command_sites` | 2 tests OK, 28.482 s |
| `tests.hazards.test_refusal_allowlist` | 23 tests; 2 inherited failures, 1 skip, 121.306 s; owned 43 keys match |
| compileall, diff and protected-path checks | compileall exit 0; protected paths/outer-runner bytes/owned refusal and host inventories match; diff check exit 0 |

The final allowlist differences are unchanged outside the owned modules: three unlisted keys
(driver re-raise and watchdog `_decide` FENCED/HOLD_UNSAFE), two watchdog miscounts, two changed
guards (harvest `archive_copy_mismatch`, watchdog `_launch_fence` HOLD_UNSAFE), zero stale keys,
and ten inherited dependency scope gaps. The new runtime dependency gap is gone. The owning
43 keys (46 sites) match exactly after the final cleanup-order change. These inherited failures
remain with RL-86; no overall green allowlist result is claimed.

Additional final commands: `python3.13 -B -m compileall -q joulewise tests scripts/launch_align_r0.py
scripts/run_align_r1_smoke.py` (exit 0), `git diff --check` (exit 0), and a focused guarded source
census plus `git diff --exit-code 2d54da7e9 -- <ten condition-13 paths, kit, state, timing, wrapper>`
(exit 0). The entire outer runner function is byte-identical to the input head, so its R0 5 s wait
is preserved. No further suite expansion was needed after these checks; the full suite remains forbidden.

Mechanism catches: the executing review identified the cap/restore/cadence defects; the R1 witnesses
and 14 mutants verify those boundaries and handoff; the allowlist caught the new dependency declaration;
R0 byte comparisons and protected-path checks caught no drift. No claim-bearing number was produced.

### Exact refusal keys / RL-86 reconciliation

Round 2 adds exactly these keys; no previously listed guard/count changes or removals:

- `(scripts/launch_align_r0.py, launch, raise, ValueError|r smoke deadline)`, count 1,
  guard **`14289bc956d7cebc`**.
- `(scripts/run_align_r1_smoke.py, part, raise, TimeoutError|part not started)`, count 1,
  guard **`009ba56e7bd6dab0`**.

For the merge, the complete branch-vs-`9b4817f36` refusal-allowlist delta follows. This includes the
launcher's inherited sites newly enumerated by the original change, and the existing measurement-checkout
key with changed guard. It is **43 keys / 46 sites** (26 launcher, 17 runner; counts are shown individually).
All keys below match the final owned-source census; this does not assert that unrelated inherited
allowlist/scope gaps are resolved. Kind is `raise` unless shown otherwise.

| File | Function | Kind | Detail | Count | Guard |
|---|---|---|---|---|---|
| `scripts/launch_align_r0.py` | `positive_seconds` | `raise` | `ArgumentTypeError\|seconds must be` | `1` | `58efbc81526ad7cd` |
| `scripts/launch_align_r0.py` | `read_fence` | `raise` | `ValueError\|desk fence must` | `1` | `d4768c794e8a2ca6` |
| `scripts/launch_align_r0.py` | `read_fence` | `raise` | `ValueError\|desk fence exceeds` | `1` | `dcb5516b0df56ce5` |
| `scripts/launch_align_r0.py` | `read_fence` | `raise` | `ValueError\|invalid desk fence` | `1` | `f2c8a97a0763b67b` |
| `scripts/launch_align_r0.py` | `pid_alive` | `kill` | `kill\|` | `1` | `f45dd2ee051df972` |
| `scripts/launch_align_r0.py` | `handoff` | `raise` | `ValueError\|desk fence changed` | `1` | `ed4a5b9de7bfd57b` |
| `scripts/launch_align_r0.py` | `handoff` | `raise` | `TimeoutError\|magistrate did not` | `1` | `3dfa1d7025f17b84` |
| `scripts/launch_align_r0.py` | `preflight` | `raise` | `CalledProcessError\|run` | `1` | `e3b0c44298fc1c14` |
| `scripts/launch_align_r0.py` | `preflight` | `raise` | `ValueError\|r requires ac` | `1` | `c35ede7c1c282a1e` |
| `scripts/launch_align_r0.py` | `run_until_deadline` | `raise` | `TimeoutError\|r desk deadline` | `3` | `149e2a2fd716c21f` |
| `scripts/launch_align_r0.py` | `run_until_deadline.interrupted` | `raise` | `SystemExit\|128 + signum` | `1` | `e3b0c44298fc1c14` |
| `scripts/launch_align_r0.py` | `run_until_deadline` | `kill` | `terminate\|` | `1` | `7ebf051686638e42` |
| `scripts/launch_align_r0.py` | `run_until_deadline` | `kill` | `kill\|` | `1` | `9bec38a7c66bcce0` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `ValueError\|live magistrate pid` | `1` | `70ba2e6f677d8d6e` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `ValueError\|desk deadline is` | `1` | `105e69e6d7e82b2b` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `ValueError\|r output must` | `1` | `f5e7e526a9e48602` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `ValueError\|checks must be` | `1` | `fe8a4761d6289d36` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `ValueError\|r smoke requires` | `1` | `ba3ce19df8fddae7` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `ValueError\|measurement checkout runner` | `1` | `cef3647b206ff276` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `ValueError\|an active desk` | `1` | `fea26754173cfa2d` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `CalledProcessError\|run` | `1` | `400865cc0fa44fbc` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `TimeoutError\|launchagent did not` | `1` | `400865cc0fa44fbc` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `<reraise>` | `1` | `420f332386437c13` |
| `scripts/launch_align_r0.py` | `main` | `return_code` | `2` | `1` | `8cf857c98761b721` |
| `scripts/launch_align_r0.py` | `<module>` | `raise` | `SystemExit\|main()` | `1` | `5972e4a22de36d17` |
| `scripts/run_align_r1_smoke.py` | `ac_power` | `raise` | `ValueError\|r smoke requires` | `1` | `c1ac40146e287262` |
| `scripts/run_align_r1_smoke.py` | `night_agents` | `raise` | `ValueError\|loaded night agent` | `1` | `b3c0de324562cf91` |
| `scripts/run_align_r1_smoke.py` | `read_power` | `raise` | `ValueError\|r smoke requires` | `1` | `7a2c2d4486f25339` |
| `scripts/run_align_r1_smoke.py` | `restore_power` | `raise` | `ValueError\|automatic restore blocked` | `1` | `93f3c8356c1d09e2` |
| `scripts/run_align_r1_smoke.py` | `AgentFeed.sample` | `raise` | `ValueError\|agent census refused` | `1` | `60b83eaf0cb8937e` |
| `scripts/run_align_r1_smoke.py` | `VolumeFeed.sample` | `raise` | `ValueError\|volume census refused` | `1` | `0af62d3a443cba6b` |
| `scripts/run_align_r1_smoke.py` | `MeterFeed.start` | `raise` | `ValueError\|km c supervisor` | `1` | `e236046ee123e156` |
| `scripts/run_align_r1_smoke.py` | `MeterFeed.start` | `raise` | `ValueError\|km c has` | `1` | `2ae2af4fcf176341` |
| `scripts/run_align_r1_smoke.py` | `work_remaining` | `raise` | `TimeoutError\|r smoke work` | `1` | `9e37a3ff2b12e605` |
| `scripts/launch_align_r0.py` | `launch` | `raise` | `ValueError\|r smoke deadline` | `1` | `14289bc956d7cebc` |
| `scripts/run_align_r1_smoke.py` | `part` | `raise` | `TimeoutError\|part not started` | `1` | `009ba56e7bd6dab0` |
| `scripts/run_align_r1_smoke.py` | `part` | `raise` | `TimeoutError\|part exceeded its` | `2` | `47cb9b4ead2779bb` |
| `scripts/run_align_r1_smoke.py` | `part` | `raise` | `RuntimeError\|part process group` | `1` | `fcd5b23f0ff85aab` |
| `scripts/run_align_r1_smoke.py` | `run.step` | `raise` | `StepFailed\|row[rc]` | `1` | `2d9502005a242afb` |
| `scripts/run_align_r1_smoke.py` | `run.step` | `raise` | `<reraise>` | `1` | `420f332386437c13` |
| `scripts/run_align_r1_smoke.py` | `run.interrupted` | `raise` | `SystemExit\|128 + signum` | `1` | `e3b0c44298fc1c14` |
| `scripts/run_align_r1_smoke.py` | `run.soak` | `raise` | `ValueError\|soak reference file` | `1` | `a5ef691ee2acee56` |
| `scripts/run_align_r1_smoke.py` | `<module>` | `raise` | `SystemExit\|main()` | `1` | `5972e4a22de36d17` |

### Handoff

Changed in round 2: `scripts/launch_align_r0.py`, `scripts/run_align_r1_smoke.py`,
`tests/align/test_r1_smoke_launcher.py`, `configs/gates/hazard_refusals.json`,
`tests/host_command_sites.json`, and this report. Implementation commit: `4c27eba472b647c2219c5669a2be0860f706f346` (`fix: honor R1 smoke budgets and preserve foreign power state`).
No push. Coordination state, all ten condition-13 sources, and `align_r1_followup_kit.py` remain unchanged.

Next exact step: the lead reviews this local commit, reconciles the table and inherited gaps with RL-86,
then uses the 9,000 s magistrate sequence on the clean merged checkout in an agent-free native session.
The native A/B smoke and its MLX/runtime, KM003C freshness, sampler/Tf08 coverage, D-load duration,
census and cleanup receipts remain owed outside this sandbox. Synthetic tests do not close any hardware gate.
