# Opus cold review: CI timing lane (PR #685) and record-only window timing reader

Date: 2026-11-08. Reviewer: Claude Opus 5.5 (cross-family cold review; Sol 6.1 built both branches).
Scope: engineering only. Audit source: `origin/perf/2026-11-08-latency-synthesis`,
`docs/perf/2026-11-08-latency-synthesis.md` §4 ranks 2 and 4. No measurement, restricted
directory, custody path or real record was read. Tests ran one module per process
(`python3.13 -B -m unittest <module>`, Python 3.13.18, Air). No full suite.

| Branch | Head reviewed | Verdict |
|---|---|---|
| 1. `origin/lane/2026-11-06-ci-timings-main` (PR #685) | `858d9f91b` (pushed); also Sol's local-only `perf/2026-11-08-eng-ci` `eaf3143f7` | **HOLD** as pushed; **ADMIT_WITH_FIXES** once `eaf3143f7` replaces the PR head |
| 2. `origin/perf/2026-11-08-eng-timing` (base `origin/align/2026-11-08-v4-r11`) | `44fb124cc` | **ADMIT_WITH_FIXES** (fix H1 before any real-record run) |

Witnesses and the plan-replay script are in
[`2026-11-08-opus-review-witnesses/`](2026-11-08-opus-review-witnesses/) (outside `tests/`, so CI does
not discover them).

---

## 1. PR #685: CI shard timings, BYTES campaign split, flake fixes

### What is actually on the PR

PR #685's head `858d9f91b` is **not** Sol's finished work. It is the old lane head `87d9b445c`
plus one commit that adds Sol's run report. That report says the real work is on
`perf/2026-11-08-eng-ci`, "Nothing pushed". That branch exists only in the local clone
`/Users/edr/code/CapstoneProject/jw-wt/sol-eng-ci`: `14b16ff79` (merge of `origin/main` `c07b388e9`),
`ba05d3c14` (timing repair, fail-fast, BYTES patch) and `eaf3143f7` (docs). I reviewed both.

`gh pr checks 685` reports "no checks reported". The PR is `mergeable: CONFLICTING`, `DIRTY`, so
GitHub runs no `pull_request` CI on it. The last CI run was at `87d9b445c` on 2026-11-06 (run
42268062591). Every test job passed there, and the slowest shard took 30.1 min. `gate-ledger` failed
(run 42268062558) because rows 1, 2, 3 and 5 are NOT-RUN.

### Coverage proof: nothing dropped, skipped or moved

Method: [`ci_plan_replay.py`](2026-11-08-opus-review-witnesses/ci_plan_replay.py) replays `ci.yml`'s
own planning code on a tree. That code covers the 12 ordinary shards (discover, drop exclusives,
expand splits, LPT-partition), the two crash-matrix shards and the calibration-exits job. The
script then resolves every unit to concrete test ids by importing each module without running it.
I ran it on three trees:

* `main`: `origin/main` `ae60ae22c`. Later main commits change only `RUN_STATE.md`.
* `pr685+main`: `858d9f91b` merged with `ae60ae22c`. The only conflict was the modify/delete of
  `tests/test_harvest_v5_qualification.py`, resolved by main's deletion per the prune report §6.
* `sol+main`: `eaf3143f7` merged with `ae60ae22c`. It merged cleanly; only `RUN_STATE.md` changed.

| Tree | Modules discovered | Test ids | Ids run by no job | Ids run by two jobs | Untimed ordinary modules | Planned slowest ordinary shard |
|---|---:|---:|---:|---:|---:|---:|
| main | 485 | 12,217 | 0 | 0 | 52 | 1,316.8 s |
| pr685+main | 485 | 12,222 | 0 | 0 | 15 | 1,384.7 s |
| sol+main | 486 | 12,227 | 0 | 0 | 16 (all exempted) | 1,386.9 s |

Set difference against main: **lost = ∅ on both trees.**

* pr685+main adds 5 ids: 3 `test_shard_split` and 2 `test_shard_tests` tests.
* sol+main adds those 5, plus 4 in `tests.test_bytes_campaign_split` and 1 in
  `tests.test_git_fixture_maintenance`.

The set of jobs carrying tests is unchanged: 12 `test`, 2 crash-matrix and 1 calibration-exits.
`quick`, `fences`, `build` and `installed-wheel` are untouched. `scripts/quick_suite.py` and
`gate-ledger.yml` are unchanged.

The only `ci.yml` edit on Sol's branch is `fail-fast: false` on the test matrix (`ci.yml:139-140`)
plus comments. That change can only add execution.

**Required checks.** `gh api repos/mpmdw/JouleWise/branches/main/protection` requires `gate-ledger`,
`quick`, `fences`, `test (3.13, 1..12)`, `calibration-exits-exclusive (3.13)` and
`calibration-writer-crash-matrix-exclusive (3.13, 1|2)`. Job ids, matrix keys and names are unchanged,
so every name still matches. Every test-bearing job is a required context. Nothing moved to a
non-required job.

**Timing map.** `scripts/test_timings.json` changes no existing weight (0 of 456 changed), adds
226 keys and leaves `exclusive_modules` byte-equal. The weights are scheduling hints; no step
asserts them.

### Findings

**HIGH-1. PR #685 as pushed cannot merge and fails its own new guard once main is merged.**
Evidence: `858d9f91b`. The PR conflicts with main, so it gets no CI. After the conflict is resolved, the
branch's own new test fails on the merged tree:
`tests.test_shard_tests.ShardPartitionInvariantTests.test_every_discovered_module_has_timing_or_documented_exemption`
(`tests/test_shard_tests.py:128` at `858d9f91b`) → `FAILED (failures=1)`. The cause is 15 modules that
main added after the lane's timing harvest. This existing test is the failing-first witness.

Sol's local `ba05d3c14` fixes it: on sol+main the test passes, with explicit `timing_exemptions` at
`scripts/test_timings.json:774`. The fix is unpushed.

Fix: push `perf/2026-11-08-eng-ci` (`eaf3143f7`) as the PR #685 head, or open a successor PR from it.
Then merge the 2 newer `RUN_STATE` commits, run hosted CI and fill the gate ledger. Refresh
`docs/run_reports/2026-11-06-ci-timings-pr-body.md` too. It still describes the older lane and lists
the harvest-v5 flake fix, which main has since deleted.

**MED-1. The 152 → 56.3 min headline is not a main CI effect. Main's slowest shard is already ~31 min.**
`tests.test_bytes_analysis` is not on main. On every merged tree it carries `awaiting_lane` and is
inert. The last green main run (42457786443, `c07b388e9`) had a slowest test shard of 31 min. On main,
PR #685 does two things:

* It gives 37 previously untimed modules hosted weights, which tightens LPT balance.
* It adds `fail-fast: false`.

The 56.3 min figure is a static projection for the ALIGN lane. It needs two steps:

1. PR #685's map reaches ALIGN.
2. `docs/perf/2026-11-08-bytes-world-split.patch` is applied there.

The three world weights in that patch are equal-thirds estimates (1,913.983 s each), not measurements.

`origin/align/2026-11-08-v4-r11` currently has **no** weight for `tests.test_bytes_analysis`. Its CI
packs a ~9,122 s module at the 26.98 s fallback. The patch's test hunk applies to v4-r11's
`tests/test_bytes_analysis.py`, which I checked with `git apply --check`. Its `scripts/test_timings.json`
hunk does not apply until step 1 lands. Sol's report states the projection status honestly. The
synthesis §4 rank-4 line should not be read as a main-CI saving.

**LOW-1. No assertion was weakened by the flake fixes.** Details:

* **histsem.** Seven `git clone --shared` call sites become `clone_git_fixture(...)`. The redundant
  per-test `gc.auto`/`maintenance.auto` lines are removed because the helper installs a superset
  (`tests/git_fixture.py:9-14`), and it installs them at clone time. No `assert` changed.
* **git_fixture.** There is a new regression test for clone-time controls. It fails before the fix,
  per Sol's report.
* **BYTES world split** (patch). All per-world assertions are kept: `assertGreaterEqual(n,20)`,
  `sum(counts)==n`, `unavailable==[]` and `assert_d3_exercised`. The patch adds a world-set equality
  assert. The worlds are independent: `epsilon`, `duration_scale` and the counters are per world, and
  each seed uses its own `random.Random(seed)` in `tests/fixtures/bytes/campaign.py:107-108`. So
  splitting cannot change any per-world value.
* **harvest-v5 hex-boundary exemption** (on `858d9f91b` only). This does narrow the
  `assertNotIn(secret, public)` scans, but only for an all-decimal secret inside a ≥32-hex-char
  digest run. Tests guard both the narrowing and the leak cases. It is moot because main deleted that
  module.

**LOW-2. The BYTES split changes the log format.** `BYTES_SIMULATION_REPORT=` becomes three one-world
lines instead of one three-world line (`tests/fixtures/ci/bytes_campaign_word_rates.py.txt:86`). No code
consumer exists outside the test on v4-r11. Anyone harvesting that line by hand for the BYTES
validation section must concatenate the three lines in world order. Sol's test proves the canonical
bytes are equal after that.

**LOW-3. `timing_exemptions` expire only when a weight arrives.** The guard rejects an exemption for a
module that has gained a weight (`tests/test_shard_tests.py:139-145` on Sol's branch). It does not
reject one for a module that has been deleted, so stale exemptions can pile up. A one-line
`assertIn(module, self.modules)` would close this.

**LOW-4. Projected balance is optimistic.** Up to 16 modules on sol+main are packed at 26.98 s
fallback weights. The planner's evenly balanced estimates (1,386.9 s × 12) are a lower bound until
the next hosted harvest. Sol says so.

### Branch-1 verdict

* **HOLD** on PR #685's current head `858d9f91b`. It conflicts, gets no CI and its own guard fails
  once merged.
* **ADMIT_WITH_FIXES** for Sol's `eaf3143f7`. Coverage is preserved exactly and required names
  match. The changes are scheduling plus mechanical fixture hardening. Fixes: push it as the PR head
  (HIGH-1), refresh the PR body, then run hosted CI and the gate ledger. Fold in LOW-3 if convenient.
  Apply the BYTES patch on the ALIGN lane only after the map lands there (MED-1).

Targeted runs (one module per process). A first histsem run used a TMPDIR under the session scratchpad that vanished mid-run (27 `FileNotFoundError` in `mkdtemp`); rerun on both trees with a dedicated `/private/tmp` TMPDIR, both clean, so that was environmental:

| Module | pr685+main | sol+main |
|---|---|---|
| `tests.test_shard_split` | 36 OK | 36 OK |
| `tests.test_shard_tests` | **8 run, 1 failure** (HIGH-1) | 8 OK |
| `tests.test_git_fixture_maintenance` | 5 OK | 6 OK |
| `tests.test_git_fixture_hygiene` | 7 OK | 7 OK |
| `tests.test_bytes_campaign_split` | n/a | 4 OK |
| `tests.test_receipt_histsem` | not run | 74 OK (skipped=1), 980 s; main same tree: 74 OK (skipped=1) |

---

## 2. `perf/2026-11-08-eng-timing`: record-only window timing ledger

The branch adds 6 new files: `joulewise/align/window_timing.py`, three test/fixture/benchmark files
under `tests/align/` and two docs. No existing file changed.

`tests.align.test_window_timing` ran 25 tests, OK. `tests.align.test_records` ran 4 tests, OK.

### Read-only, capture-free, outcome-free

* **Read-only.** The module imports only stdlib (`window_timing.py:10-18`). `GitRecords`
  (`:53-81`) reads committed regular blobs with `git ls-tree` / `cat-file`. It refuses symlinks,
  non-blobs, absolute paths, `..`, `.git`, `restricted`, `night-custody`, `night-archive`, `jw-b5-*`
  and `night-*` (`:40-50`). It sets `GIT_OPTIONAL_LOCKS=0`, takes no worktree reads, writes only to
  stdout, and touches no capture or controller code.
* **No energy or outcome values used.** It only accesses timing keys:
  * `started/ended_*`, `epoch_s`, `monotonic_ns` and `timestamp_s` timestamps.
  * Event type/phase.
  * Turn/tool/gate `start_ns`/`end_ns`, `first_token_ns` and `decode_tokens`.
  * Gate `kind`/`outcome` (released/timeout).
  * `os_batch_wait_s` and `result.phases_s`.

  It does json-parse whole files that also hold outcome fields: `align_episode.json` holds
  `condition`, `main_task_score` and `side_task_success` (`joulewise/align/apple/workload.py:718-725`),
  and `r1_result.json` holds energy fields elsewhere in the record. It never reads or emits them.
  See LOW-B1.

### Correctness on the synthetic fixtures

* **Disjointness holds.** The sweep in `partition()` (`:101-142`) matches an integer-grid oracle on
  80 random cases and a full-report scan implementation. Phase sums equal envelope wall, and member
  ledgers reconcile.
* **Unattributed time is explicit and never invented.** I dropped each journal row in turn (`refs`,
  `science`, `verdict`) and the missing time moved to `unattributed`; for `verdict` it also showed in
  `post_last_stage_ns`=25 s. Nothing was fabricated. A missing `chain.exited` gives
  `ceiling.status=unavailable` and does not use the last stage as a substitute.
* **Clock sign is correct.** `epoch = episode_ns − offset_ns` matches the native consumers
  (`thermal_desk.py:768`, `endpoint.py:793`).

### Findings

**HIGH-B1. Ordinary wall/monotonic drift makes every real episode unplaceable.**
`window_timing.py:358-365` refuses episode placement whenever the first and last
`paired_clock_stamps_ns` disagree by more than 1 ms in elapsed time. The refusal happens even when a
valid `clock_mappings` entry exists, and before that entry is consulted.

Every native episode carries start and end paired stamps (`workload.py:728`). Wall time is
NTP-disciplined and monotonic time is not. I measured 9.2 ppm drift on this Air, which crosses 1 ms
after about 110 s. The native mapping already absorbs that drift into `uncertainty_ns`
(`sampler.py:96-121`).

On real R1/W1 episodes, which last minutes, each member therefore loses all of its decode, prefill,
tool, G0/G1/H and hold time to `episode_clock` unavailable. That is the reader's main deliverable.

Witness: `test_h1_ordinary_wall_monotonic_drift_keeps_mapped_episode_placed` uses a 28 s episode,
2 ms stamp disagreement and 5 ms mapping uncertainty. It fails on `44fb124cc`
(`'episode_clock' unexpectedly found`).

Fix: when a mapping exists, keep the drift as a warning plus added uncertainty and do not refuse.
In the paired-stamp fallback, refuse only if the drift exceeds the computed bracket uncertainty plus
a stated ppm allowance. Then add the witness as a regression test.

**MED-B1. A member without `run_finalized` skips the episode bounds check, so a bad mapping can inflate the
window.** The guard at `:391-396` runs only when the member has run bounds. A torn or crashed bundle
with no `run_finalized` event places its episode unchecked and adds it to `bounds` (`:397-398`).

Witness: `test_m1_member_without_run_finalized_cannot_expand_window_by_bad_mapping`. A mapping
shifted by 1,000 s turns a 100 s envelope into 1,058 s; this fails on `44fb124cc`.

Fix: fall back to the member's first and last event timestamps as bounds, or refuse placement
without bounds.

**MED-B2. "Where do R1's hours go?" is only partly answerable.** Several things land in unlabelled
gaps between attempt envelopes:

* `os_batch_wait_s` is kept as an unplaced aggregate (`:272-287`). That is correct when a release
  intervenes. Note that it is the sum of *requested* sleep delays, not measured wall
  (`scripts/align_r1_rehearsal.py:980-995`).
* `row["g0_release"]` is ignored entirely. Each heavy redo or leg pays a 65 s pre-roll plus up to
  600 s G0 wait before `started_ns` (`align_r1_rehearsal.py:1071-1077`, `r1_runtime.py:1637-1646`).
* Non-bracket, non-soak R1 segments are `unattributed` at window level (`:268-270`) unless their
  bundles are passed.

All of this lands as `unattributed`. Proportionate fix: for each attempt, report the gap
`started_ns − previous ended_ns` beside its recorded wait and its G0 release wait fields. When there
is no `g0_release`, the wait can be placed as `[started − wait, started)`. That turns R1's
unattributed hours into a labelled table without guessing.

**LOW-B1. Blinding stays procedural.** The reader loads whole episode and R1 files and emits per-member
decode seconds and tokens keyed by `run_id`. Joined with condition elsewhere, those are
outcome-adjacent. The doc's custodian step ("export only unblinded R1/W1/D records") is the control.
Keep it. Phase timing is operational per the brief, so this is not a blocker.

**LOW-B2. The 1 ms wall-vs-monotonic warning on chain and driver envelopes will always fire.** At
`:219-223` and `:476-479`, multi-hour records drift by about 0.5 s over 16 h, so the warning becomes
noise. Report drift in ppm, or warn only above a ppm threshold.

**LOW-B3. Without `chain.started`, `chain.exited` is left out of the envelope.** Bounds are added
only when both exist (`:470-475`), but `end` still feeds the ceiling, so the tail after the last
stage can fall outside the ledger. Add `end` to `bounds` on its own.

**LOW-B4. The reader's `decode` excludes tool-call time, unlike native `phases_s.decode`.** Tool
calls have priority 40 over decode's 30 (`:416-427`). Native `episode_phases`
(`r1_runtime.py:675-695`) subtracts only holds. The worksheet prints both, so state the definitional
difference there to avoid false cross-check alarms.

### The two questions

* **"Does any path idle to the 59,520 s ceiling?"** Partly, per record. The reader compares
  `chain.exited` with the plan's `t0_epoch_s + window_max_s`. It reports `closed_before_ceiling` (and
  then `idle_to_ceiling: not_in_this_record`) or `at_or_after_ceiling_cause_unproven`. It also gives
  headroom and `post_last_stage_ns` (`:557-571`).
  * It cannot prove anything about code paths a record did not exercise. That needs a static audit
    of the driver's wait loops.
  * R1 has no `chain-stages.jsonl`, so `post_last_stage_ns` is unavailable for R1.
* **"Where do R1's hours go?"** Partly. It gives attempt envelopes by segment, superseded attempts,
  unplaced batch waits, recorded `phases_s`, and member ledgers when bundles are supplied. Today,
  though, HIGH-B1 would blank the member activity split on real episodes, and MED-B2 leaves release
  and wait gaps unlabelled. With those two fixed, it answers the question.

### Branch-2 verdict

**ADMIT_WITH_FIXES.** The reader is read-only, capture-free and outcome-free, with sound disjoint
accounting. Fix HIGH-B1 and MED-B1, landing the witnesses as regressions, before the first real
committed-record run. MED-B2 is the change that makes the R1 question answerable. The LOW items are
optional.

## Reproduction

```sh
# Branch 1 coverage replay (run from each tree root; imports test modules, runs none)
python3.13 -B docs/perf/2026-11-08-opus-review-witnesses/ci_plan_replay.py /tmp/plan.json
# Branch 2 witnesses: copy into tests/align/ on perf/2026-11-08-eng-timing, then
python3.13 -B -m unittest tests.align.test_window_timing_opus_witness   # 2 failures on 44fb124cc
```
