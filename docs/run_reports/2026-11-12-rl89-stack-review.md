# RL-89 / RL-94 stack: executing cold review

2026-11-12, Fable 5.2 (cold reviewer, Air). I did not write the stack; Opus built it.
Blind: sensor metadata, smoke engineering tables and code only. No v4 outcome and no energy value was read.

## Verdict: ADMIT-WITH-FIXES

Nothing blocks the Part A smoke or tonight's arm. The fixes are test gaps and wording, listed under Findings;
none changes bytes the smoke or the night runs.

- **Reviewed:** `fix/2026-11-12-r1-smoke-fresh-soak` @ `384449027`, five commits on presign `22f438fd3`
  (`bfd25fc72`, `1590f0f4f`, `06b706065`, `e0d3d407d`, `384449027`).
  `fix/2026-11-12-rl89-sensor-config` @ `06b706065` is the first three.
- **Rulings read:** RL-89, RL-93 and RL-94 in `origin/audit/2026-11-10-fable` @ `cc8825611`.
- **Not done:** no MBP access. The magistrate's Mac check (RL-89 item 4) and Part A itself are still owed.

## Checks

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | The 60-key derivation | PASS | Re-derived with my own code from the saved `r0.json` (sha256 `e6231a8f…769b`, verified). 403 ranking rows: 16 die and 44 heatsink eligible, 343 record-only. Keys, classes and ranking order equal the config. The fixture equals the (key, class, eligible) projection of the record, row for row. The script's `check` mode passes, also under the system Python 3.9, and refuses a swapped order. |
| 2 | The config diff | PASS | Five fields differ from presign: `sensors.s_slow` (Tf08 to Th0C), `r0_picks` (new), `r0_classified_keys`, `r0_classes`, `r0_classes_authority`. Fans, `record_keys`, `r0_sha256`, `slow_band_floor_c` 1.0 and `g0_timeout_s` 1200 are unchanged. Config sha256 `95825997…1dad`. No file in the tree pins a digest of this config, so none needed regenerating. `load_config` accepts the new top-level field. |
| 3 | Table regeneration | PASS | My `smoke_table` run on the saved segment gives `1fdd980c…eba3`, byte-equal to the committed table. The four acceptance checks hold (below). At presign `22f438fd3` the same segment reproduces `6b05379d…f373`, the table RUN_STATE 282 records, so the saved inputs are the MBP's. |
| 4 | `validate_sensor_ruling` | PASS | Accepts the new table with the ruling file and the branch config. Refuses the old table (sha mismatch; with the sha forced, "smoke R0 key set changed"). Refuses the new table under the old config, and a ruling without `authorizes_night`. |
| 5 | Deviation row | PASS | Applying RL-89's two quoted edits and the citation change to the presign row reproduces the committed row exactly. |
| 6 | Runner `--fresh-soak` and `--parts A` | PASS, with test gaps | See "The runner" below. |
| 7 | The kit commit | PASS | See "The kit commit" below. |
| 8 | Tests | PASS | See "Tests" below. |

### Check 3: the four acceptance identities

1. `classification_sha256` is `0b9cdb9e…e0a6` in both tables.
2. `coverage` is deep-equal.
3. `selection` is `ok` true, `fallback` false, TV0h / Th0C, `reasons` empty.
4. The top-level fields that differ are `r0_classified_keys`, `selection` (`ok` and `reasons` only) and `status`
   (`SELECTION_FAILED` to `FOR_RESEARCH_LEAD_RULING`). `rejected_keys`, `classification_table`,
   `candidate_replays`, `class_edge_margins`, `schema` and `note` are equal.

The five input files `smoke_table` reads hash to the values in the builder's `remote_sums.txt`. The receipt hashes to
`f69e5649…aaa1`, as RUN_STATE 282 says.

### Check 6: the runner

- **Smoke-only.** The commit touches `run_align_r1_smoke.py`, `launch_align_r0.py`, the allowlist and one test file.
  Neither script is in `R1_EXECUTED_SOURCES`. The watchdog imports only `FENCE_NAME`, `fence_lock` and `read_fence`
  from the launcher, and the diff does not touch them. With default arguments the runner argv, the part caps and the
  minimum are unchanged.
- **Soak semantics.** `soak_child` calls the rehearsal's own functions, compared line by line with the night's
  `_admission_unit`:
  - `_invoke(..., "idle", …/idle_soak, 1800.0, quiet=True, contract_key="idle_soak")`;
  - `os_load_verdict` with the same wall time;
  - `soak_detrended` on the same three result fields;
  - `write_soak_reference`.
  The duration comes from the phase table. The band is not computed in the smoke: the runtime's `bands_c` reads the
  reference and gives max(1.0, 3 × SD) with `slow_band_floor_c` 1.0, unchanged code.
- **Differences from the night, all as RL-94 allows.** One attempt and no redo. An OS-batch overlap refuses and does
  not wait. No volume watch argument (the smoke's own volume feed runs). The reference holds TV0h and Th0C only;
  carrying Tf08 would need runtime code.
- **Refusals.** Unsettled slope, sustained CPU load and batch-window overlap each raise before the reference is
  written. A soak failure runs no part.
- **`--parts A`.** The part loop iterates the requested string, so Part B cannot start.
- **Receipt.** `fresh_soak`, `parts_requested`, the `soak` step, `soak_reference` (the fresh path) and
  `soak_reference_sha256` are recorded.
- **Deadline.** `r1_minimum_seconds("A", True)` is 3120 + 1950 + 300 + 360 + 10 = 5,740 s.

### Check 6: the two changed launcher guard digests

I recomputed every launcher and runner site with the census at base and at head. Both lists match the allowlist with
no unlisted, stale or miscounted key (43 keys at base, 49 at head).

| Key | Guard | Category | Cause |
|---|---|---|---|
| `launch / r smoke requires` | `ba3ce19d…` to `fba845f5f16782a0` | INTERNAL, unchanged | The condition gained `not fresh`. |
| `launch / r smoke deadline` | `14289bc9…` to `0935aebb27b6709c` | NUMBER_INTEGRITY, unchanged | `r1_minimum_seconds()` now takes `parts, fresh`. |

**Ruling: both digests are correct.** Each follows from exactly one edited condition. Counts and `protects` text are
unchanged. This is consistent with RL-86 and RL-93: RL-93's "counts and guards do not change" speaks of its
rewording, which is not yet done, and the code changed after it. The RL-93 rework must carry the new digests.

- The rework now covers 25 rows, not 19: four new runner rows and two new launch rows are added.
- Three of the new runner rows are PHYSICS and one is NUMBER_INTEGRITY. That matches the style of the existing
  unreworked rows and becomes INTERNAL with a per-site clause under RL-93, before signing.
- The first narrowing (no soak file needed when fresh) is compensated: the launcher refuses both sources together,
  and the runner refuses when the soak wrote no reference.

### Check 7: the kit commit `384449027`

- `r0_heatsink_key()` returns `config["r0_picks"]["s_slow"]` (Tf08). It refuses a missing or empty pick and a pick
  that is not in `sensors.record_keys`.
- **Fails before, passes after.** With the new test file and the old kit, 7 of the 12 tests fail (64 failures with
  subtests), including the generated-policy witness and the new RL-94 test. With the new kit all 12 pass. On branch 1
  the old witness was red, as stated.
- **W1 policy.** The new test shows `record_keys` ["Tf08"] with gates on TV0h / Th0C, and that changing
  `sensors.s_slow` alone moves nothing. The generated collection plan has `record_keys` ["Tf08"] on all 14 sidecar
  members and no sidecar on the 4 anchors.
- **Regenerated artifacts.** I ran `build_files` at presign and at the head and compared all 30 generated files.
  Exactly two differ, by one line each:
  - `plan_tree.json`: `generator.sha256` `7759ac42…fad5` to `69761abc…2c24e`, which is the sha256 of the new kit;
  - `identity_pins.json`: `tree_sha256` `8835b4b1…d769` to `452ea0de…39d9fb`, which is the sha256 of the new tree.
  The other 28 files are byte-equal, the collection plan among them. The committed tree equals the generator's output
  at both commits. `--check` gives the same BLOCKED-by-R1-placeholders message at both.
- Not condition 13: the kit, the tree and the pins are outside `R1_EXECUTED_SOURCES`.

## Mutants

Run in a scratch worktree at `384449027` against `tests.align.test_r1_smoke_launcher` (53 tests, green unmutated).

| Mutant | Result | Killed by |
|---|---|---|
| M1 Part B runs despite `--parts A` | killed | `test_order_and_receipt` |
| M2 soak skipped | killed | `test_order_and_receipt` and two more |
| M3a soak SD doubled in the written reference | **survived** | none |
| M3b runtime band 3 × SD to 2 × SD | **survived** | none green (see F2) |
| M3c runtime band floor ignored | **survived** | none green (see F2) |
| M3d soak duration 900 s | killed | `test_night_idle_soak_path_and_reference` |
| M4 batch-window guard off | killed | `test_unsettled_soak_and_os_batch_overlap_refuse` |
| M5a receipt lacks `fresh_soak` | killed | `test_order_and_receipt` |
| M5b soak step lacks `soak_reference_sha256` | killed | `test_order_and_receipt` |
| M5c receipt `soak_reference` not set to the fresh path | killed | `test_order_and_receipt` |
| M5d receipt lacks `parts_requested` | killed | `test_order_and_receipt` |
| M6 unsettled-slope refusal removed | killed | `test_unsettled_soak_and_os_batch_overlap_refuse` |
| M7 sustained-CPU refusal removed | **survived** | none |
| M8 `contract_key="idle_soak"` dropped | killed | `test_night_idle_soak_path_and_reference` |
| M9 launcher minimum ignores the soak | killed | `test_launcher_argv_minimum_and_cap` |
| M10 launcher minimum ignores parts | killed | two tests |
| M11 launcher does not forward `--parts` | killed | two tests |
| M12 launcher allows both soak sources | killed | `test_launch_fresh_soak_part_a_spec_and_deadline` |
| M13 r0 kind accepts the smoke options | killed | `test_launch_fresh_soak_part_a_spec_and_deadline` |
| M14 Part A handed no fresh reference | killed | `test_order_and_receipt` |
| M15 missing reference file tolerated | **survived** | none |
| M16 soak failure code ignored | killed | `test_soak_failure_runs_no_part` |
| M17 soak runs under Part A's cap | **survived** | none |
| M18 soak child skips the executed-source check | **survived** | none |
| M19 runner CLI accepts neither source | killed | `test_runner_cli_takes_exactly_one_soak_source` |
| M20 `os_load_verdict` loses `wall_s` | **survived** | none |

Of the five mutants the brief names, four are killed. "Soak band wrong" is not: see F1 and F2.

## Tests

One module at a time, `nice -n 10 python3.13 -B -m unittest`, 31 to 32 GB free throughout.

| Module | At `384449027` |
|---|---|
| `test_r1_r0_classes` | 7 OK, 1 skipped; 7 OK with `JOULEWISE_R0_JSON` set to the saved record |
| `test_v4_registration` | 24 OK |
| `test_v4_executed_closure` | 6 OK |
| `test_v4_dynamic_closure` | 10 OK |
| `test_r1_followup` | 12 OK |
| `test_r1_smoke_launcher` | 53 OK |
| `tests.hazards.test_refusal_allowlist` | 24 OK, 1 skipped |
| `test_w1_tf08_record` | 12 OK |
| `test_v4_kit` | 116 OK |
| `test_w1_kit_r10` | 30 OK |
| `test_r1_runtime` | 33 run, 7 failures and 2 errors: the same nine tests as at presign |

Run at `e0d3d407d` only, on files the kit commit does not touch: `test_r1_inventory` 14 OK, `test_smc_selection`
10 OK, `test_smc_classifier_v4` 27 OK, `test_r1_round7_science` 18 OK.

At `e0d3d407d`, before the kit commit, `test_v4_kit` (8 failures, 1 error), `test_w1_kit_r10` (1) and
`test_w1_tf08_record` (1) were red from the generator drift. All three are green at the head and at presign.

`test_r1_round6_lows` has 1 failure and 1 error at presign and at the head, the same two tests. It is outside the
brief's list and I ran it only for F2.

## Findings

None blocks the smoke or the arm.

- **F1 (low, test).** No test pins the values the soak child writes. `test_night_idle_soak_path_and_reference`
  checks the schema, keys, roles and `settled`, so a reference with a wrong SD passes (M3a). The code is right by
  reading. Fix: assert the reference's `detrended` equals `r1.soak_detrended` of the fake result. Until then, check
  the real smoke after the run: `soak/soak_reference.json` `detrended` equals `soak/soak_row.json`
  `soak_detrended`, and Part A's recorded bands equal max(1.0, 3 × SD) of it.
- **F2 (low, pre-existing, not this stack).** No green test pins the runtime's band formula. M3b and M3c survive
  `test_r1_smoke_launcher`, `test_r1_followup`, `test_r1_rehearsal`, `test_r1_round2`, `3`, `4`, `7_science`,
  `test_r1_runtime_contract` and `test_r11_delta2_sol1`, `2`. `test_r1_runtime` and `test_r1_round6_lows` show
  the same failures mutated and unmutated. `r1_runtime.py` is unchanged here and RL-89 forbids changing it. This
  belongs to the post-smoke test migration.
- **F3 (low, test).** Four more survivors: the sustained-CPU refusal (M7), the missing-reference refusal (M15), the
  soak's own cap (M17) and the soak child's executed-source check (M18). M20 is the same kind. Each needs one
  assertion in `SoakChildTests` or `FreshSoakPartATests`.
- **F4 (low, record).** The regeneration record says the input hashes were compared on both hosts but does not
  list them. They exist only in scratch (`remote_sums.txt`). Add the five lines to the record.
- **F5 (low, wording).** The `launch / r smoke deadline` row's `protects` still says "complete A and B caps", and
  the refusal message says "both part caps"; both now also cover the soak and A alone. Fold into the RL-93 rework,
  which now covers 25 rows.
- **F6 (note).** The kit commit message says all 12 tests fail with the old kit. Seven do (64 subtest failures).
- **F7 (note, operations).** The fresh soak refuses if it would end after 11:45 local. With the 300 s dwell and the
  1,800 s soak, the launch must be before about 11:08. A late launch refuses after the dwell, about six minutes in,
  and costs nothing else. Part A itself has no batch-window guard.

## What I did not verify

- Anything on the MBP: the magistrate's `r0.json` check, the live SMC read of Th0C, and the soak child's native run.
  The native path is the night's idle-soak call, which ran on the R1 night with Tf08.
- CI on the pushed branches.
