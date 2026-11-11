# Agent-free R1 follow-up smoke launcher — 2026-11-11

Status: implemented and synthetically exercised; **native smoke and independent executing review remain owed**. Branch `ops/2026-11-11-r1-smoke-launcher`, based exactly on `9b4817f362524a443d92547453d68023faa1bd95` (`ops/2026-11-11-w1-presign`). No night was armed or measurement captured. No model weights, network, real host-setting command, or sealed custody was accessed.

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

These commands are a **future native handoff**, not commands executed here. First obtain the independent executing review requested by the refusal record, reconcile RL-86, and select the committed branch head descended from `9b4817f36`. Set `PY` to the already installed, pinned measurement venv; do not resolve its interpreter symlink or download weights. Set `MAGISTRATE_PID` to the real magistrate process that will exit, not a tool-shell PID. `CUSTODY` must be the watchdog's actual configured root; its default is printed below as text only.

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
DEADLINE="$("$PY" -B -c 'import time; print(time.time()+7200)')"
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
