# Whole suite and seal-preparation checks at the block 5 seal commit (run 9)

Written 2026-10-08, about 02:45 PDT. Every log named here is in
`/Users/edr/night-archive/gate-prune/frozen-suite-int5-9/`.

## Head tested

`ab7b21e576a2d74f0b25d9a26b463d6934588368` ("Block 5 seal commit: the sealed inventory, the registration and the
analysis plan"), in the detached worktree `/Users/edr/code/JouleWise-wt-suite9`. `head.txt` holds the hash the run
script read. The worktree was not edited; `git status --short` is empty after the run.

## Result in one paragraph

The suite has 9,853 tests. 9,848 pass inside the suite run. Five do not, and they are the same five that failed at
the previous head (9395cecfb, run 8). All five pass when their module is run alone, and all five pass when run from
a runner saved as a file. None is a defect in measurement, calibration or claim code. Four are caused by how this
run feeds the runner to Python (on standard input). One is caused by the order of two test modules inside one
process. No new failure appeared. The ten checks all return 0 with the hashes of FROZEN_HEAD_4.md. The refusal
census is clean.

## How the suite was run

- `run.sh` (a copy of run 8's script with the paths changed). Interpreter `/opt/homebrew/bin/python3.13 -B`,
  `TMPDIR=/private/tmp/int5suite9`, `PYTHONDONTWRITEBYTECODE=1`, `SHARD_COUNT=6`.
- A shard is one of six groups the repository's own splitter (`scripts/shard_tests.py`) divides the test modules
  into; the six run at the same time, one Python process each. `shard_runner.py` is the body of the continuous
  integration job "Unit tests"; each process reads it on standard input (`python3.13 -B - < shard_runner.py`).
- The two modules the repository marks exclusive (they must run with nothing else running) ran afterwards, one
  after the other, under `-m unittest`: `tests.test_calibration_exits`, `tests.test_calibration_writer_crash_matrix`.
- Started 01:17 PDT, finished 02:29 PDT (`run.out` says `ALLDONE`).

## Parts

| Part | Modules | Tests | In-suite result | Disposition |
|---|---|---|---|---|
| shard 1 | 65 | 1,415 | FAIL: 3 failures, 4 skipped | 3 F in `tests.test_sample_quiet_predicate_evidence` (LoadTests). Standard-input artefact. Alone: 96 OK. |
| shard 2 | 65 | 1,475 | PASS, 21 skipped | Includes `tests.hazards.test_monitor`: 35 tests pass. |
| shard 3 | 64 | 1,722 | FAIL: 1 failure, 6 skipped | 1 F in `tests.test_v5_s1_qualification` (courier timing, 30.2 s against a 5 s limit). Module-order artefact. Alone: 23 OK. |
| shard 4 | 65 | 1,836 | FAIL: 1 error, 11 skipped | 1 E in `tests.test_harvest_b5_window` (WorkerPoolTests). Standard-input artefact. Alone: 184 OK. |
| shard 5 | 64 | 1,711 | PASS, 12 skipped | |
| shard 6 | 64 | 1,626 | PASS, 7 skipped | |
| `tests.test_calibration_exits` | 1 | 48 | OK | |
| `tests.test_calibration_writer_crash_matrix` | 1 | 20 | OK | |

Total: 9,785 tests in the six shards plus 68 in the two exclusive modules = **9,853**. Run 8 had 9,842; the 11
added tests come from the commits between 9395cecfb and this head (shard 1 +1, shard 2 +3, shard 3 +5, shard 4 +2).

## Exact last lines of each log

`shard1.log`
```
Ran 5 tests in 0.007s

OK
MODULE PASS tests.test_zero_capture_facts tests=5 failures=0 errors=0 skipped=0 seconds=0.007
SHARD SUMMARY index=1/6 modules=65 tests=1415 failures=3 errors=0 skipped=4 result=FAIL
```
`shard2.log`
```
Ran 8 tests in 0.001s

OK
MODULE PASS tests.test_workload_sizing tests=8 failures=0 errors=0 skipped=0 seconds=0.001
SHARD SUMMARY index=2/6 modules=65 tests=1475 failures=0 errors=0 skipped=21 result=PASS
```
`shard3.log`
```
Ran 17 tests in 0.402s

OK
MODULE PASS tests.test_write_b5_identity_pins tests=17 failures=0 errors=0 skipped=0 seconds=0.402
SHARD SUMMARY index=3/6 modules=64 tests=1722 failures=1 errors=0 skipped=6 result=FAIL
```
`shard4.log`
```
Ran 11 tests in 2.414s

OK
MODULE PASS tests.test_window_status_guard tests=11 failures=0 errors=0 skipped=0 seconds=2.414
SHARD SUMMARY index=4/6 modules=65 tests=1836 failures=0 errors=1 skipped=11 result=FAIL
```
`shard5.log`
```
Ran 4 tests in 0.012s

OK
MODULE PASS tests.test_window_env_allowlist tests=4 failures=0 errors=0 skipped=0 seconds=0.012
SHARD SUMMARY index=5/6 modules=64 tests=1711 failures=0 errors=0 skipped=12 result=PASS
```
`shard6.log`
```
Ran 16 tests in 5.170s

OK
MODULE PASS tests.test_write_derivation_night_inputs tests=16 failures=0 errors=0 skipped=0 seconds=5.170
SHARD SUMMARY index=6/6 modules=64 tests=1626 failures=0 errors=0 skipped=7 result=PASS
```
`excl_exits.log`
```
----------------------------------------------------------------------
Ran 48 tests in 459.394s

OK
```
`excl_crash.log`
```
----------------------------------------------------------------------
Ran 20 tests in 230.459s

OK
```

The only module lines that are not `MODULE PASS` in the six shard logs:
```
MODULE FAIL tests.test_sample_quiet_predicate_evidence tests=96 failures=3 errors=0 skipped=0 seconds=26.216
MODULE FAIL tests.test_v5_s1_qualification tests=23 failures=1 errors=0 skipped=0 seconds=46.105
MODULE FAIL tests.test_harvest_b5_window tests=184 failures=0 errors=1 skipped=0 seconds=450.930
```

## The five in-suite failures

| # | Test | In suite | Class | Alone, `-m unittest` | Runner saved as a file |
|---|---|---|---|---|---|
| 1 | `test_sample_quiet_predicate_evidence.LoadTests.test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child` (exit_delay=1) | FAIL | standard-input artefact | module 96 OK | ok |
| 2 | the same test (exit_delay=60) | FAIL | standard-input artefact | module 96 OK | ok |
| 3 | `test_sample_quiet_predicate_evidence.LoadTests.test_real_load_tracks_point_one_core_and_guards_worker_budget` | FAIL | standard-input artefact | module 96 OK | ok |
| 4 | `test_harvest_b5_window.WorkerPoolTests.test_worker_pool_matches_serial_assessment` | ERROR (`BrokenProcessPool`) | standard-input artefact | module 184 OK | ok |
| 5 | `test_v5_s1_qualification.QualificationSubsetTests.test_delivered_courier_journal_assembles_with_observed_exit_and_timeout` (still_running=True) | FAIL (`30.217939667170867 not less than 5`) | module-order artefact (timing symptom, not machine load) | module 23 OK | ok |

No failure is classed REAL.

### Failures 1 to 4: the runner was fed on standard input

These tests start worker processes with Python's `multiprocessing` in "spawn" mode. A spawned worker starts a new
interpreter and re-imports the parent's main file. When the parent was started as `python -`, its main file is
recorded as `<stdin>`, which is not a file, so the worker dies before doing any work. The shard logs show this
directly: `FileNotFoundError: [Errno 2] No such file or directory: '/Users/edr/code/JouleWise-wt-suite9/<stdin>'`
appears 13 times in `shard1.log` and once in `shard4.log`. Machine load plays no part: run 8 reproduced the failures
alone on standard input and saw them pass with the same runner saved as a file (`../frozen-suite-int5-8/probe_stdin_*.log`,
`probe_file_*.log`). Continuous integration feeds the runner the same way, so the same four will fail there unless
the job saves the runner to a file first.

### Failure 5: an earlier module leaves three signals ignored in the shard process

The test starts a child process (the "courier"), sends it SIGTERM (the ordinary request to terminate), and requires
the whole exchange to finish in under 5 seconds. Inside shard 3 it took 30.2 seconds: the child did not die on
SIGTERM and was only removed by the 30-second forced kill.

The cause is not load. `probe_courier_order.py` runs two things in one process on an idle machine (load average 1.1):
first the module `tests.test_gen_g2a_window`, then this one test. `probe_courier_order.log` shows:

- before: SIGTERM and SIGHUP have the default action, SIGINT has Python's default handler;
- after `test_gen_g2a_window` (15 tests, OK): SIGTERM, SIGINT and SIGHUP are all set to "ignored";
- the courier test then fails with `30.230757333803922 not less than 5`.

A child process inherits "ignored" from its parent, so the courier child ignores SIGTERM. The setting comes from
`joulewise/night_agent_install.py`: its command-line entry point ends by calling `quiesce()` (defined at line 102; the setting is line 106), which sets
the three signals to ignored "through CLI exit". As a command-line program that is harmless, because the process
exits next. `tests/test_gen_g2a_window.py` line 201 calls `install.main(...)` inside the test process and nothing
restores the signals afterwards (the class has a `release()` method for that purpose). In shard 3,
`test_gen_g2a_window` is module 35 and `test_v5_s1_qualification` is module 59 of the same process. Run 8's
`probe_shard3_order.log` shows the same switch at the same module.

Consequence for the record: this failure will recur in every shard run where the splitter puts those two modules
in one shard in that order, whatever the load. The repair is in test code (restore the signals after the in-process
call), not in measurement code. Nothing was changed here because the tree is sealed.

## Reruns

| Log | Command (in the worktree, same TMPDIR and interpreter) | Result |
|---|---|---|
| `rerun_tests.test_sample_quiet_predicate_evidence.log` | `-m unittest tests.test_sample_quiet_predicate_evidence` | rc 0, `Ran 96 tests in 29.654s`, OK |
| `rerun_tests.test_v5_s1_qualification.log` | `-m unittest tests.test_v5_s1_qualification` | rc 0, `Ran 23 tests in 13.958s`, OK |
| `rerun_tests.test_harvest_b5_window.log` | `-m unittest tests.test_harvest_b5_window` | rc 0, `Ran 184 tests in 465.127s`, OK |
| `probe_file_five.log` | `python3.13 -B probe_file_runner.py` (LoadTests, WorkerPoolTests and the courier test, loaded as the shard runner loads them, runner saved as a file) | rc 0, `Ran 13 tests in 14.610s`, OK; the five known tests each print `ok` |
| `probe_courier_order.log` | `python3.13 -B probe_courier_order.py` | reproduces failure 5 without load (see above) |

## Checks (`checks.log`)

| Check | rc | Hash or output | Against FROZEN_HEAD_4.md |
|---|---|---|---|
| ALPHA `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py --check` | 0 | plan tree `1d87a30955fa978d3a3a22dc0048720691e0128e4a3fe83477fc375d13dd031a` | unchanged |
| BETA `configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py --check` | 0 | plan tree `0cdb33836f4632827bc74be194e388450c53b3314db1c72d9e9904e625868670` | unchanged |
| GAMMA `configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py --check` | 0 | plan tree `8b1d1d7176f5ee2286038e91df6427e47476c3a4bdee45a1c24687d49d80e3bf` | unchanged |
| `scripts/size_b5_window.py --check` | 0 | `sizing_b5.json` `89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa` | unchanged |
| `scripts/write_b5_identity_pins.py --check` | 0 | `identity_pins.json` `a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9` | unchanged |
| `-m joulewise.b5.reference_spares --check` | 0 | prints nothing | unchanged |
| `scripts/check_campaign_generator_core_parity.py --baseline-ref 2011ec285` | 0 | `PARITY_OK generators=3 files=357` | unchanged |
| `scripts/repin.py --check` | 0 | `PASS 16 pin families current`; `configs/pins/registry.json` `a4a2be94912c4a3c33b1fb04e0f91e9e691290e2a7b7ee98898783ff307033b2` | unchanged |
| `scripts/gen_derivation_night.py --check` | 0 | `PASS generated derivation-night wrapper region matches` | unchanged |
| `scripts/gen_state.py --check` | 0 | prints nothing | not in that table; passes |

For each pack the recomputed SHA-256 of `plan_tree.json` equals the committed `plan_tree.sha256` file.

Two observations, neither a failed check:

- `configs/gates/hazard_refusals.json` is `127f835096b4f9b790083f33438931a82167b19801272999ff6288e0b2ba40aa`. Run 8
  recorded `d0a54d5a…` at 9395cecfb. The file is not in the FROZEN_HEAD_4 table. It changed between the two heads
  (7 lines: `cell.below_minimum`, `neg8.midpoint_lost_primary` and `neg8.screen_failed` reworded, `g3.recompute_failed`
  removed), in the seal-gate commits 9980d6296 and 7b88e835a.
- `size_b5_window.py --check` still prints `"status": "UNSEALED_DRAFT"` for `sizing_b5.json` at the seal commit, and
  the two floor packs' checks still print "unfrozen draft". These are the same words as at fe28e5a0c and 9395cecfb;
  the bytes are unchanged. Whether a sealed head should print them is a question for the seal lane, not a check
  result.

## Refusal census

The census lists every place in the code that can refuse to collect or exclude data and compares it with the
allowlist `configs/gates/hazard_refusals.json`.

- `-m unittest -v tests.hazards.test_refusal_allowlist`: rc 0, `Ran 23 tests in 12.794s`, OK (`refusal_census_test.log`).
- `-m tests.hazards.refusal_census`: rc 0; `unlisted`, `stale`, `miscounted`, `guard_changed` and `scope_gaps` are
  all empty lists (`refusal_census_main.log`).

The census is clean at ab7b21e57.

## Not done

- Nothing in the repository was changed, committed or pushed. No branch was created.
- `tests.hazards.test_monitor` was not rerun alone (it passed in shard 2; FROZEN_HEAD_4.md records that it is
  load-sensitive when run alone).
