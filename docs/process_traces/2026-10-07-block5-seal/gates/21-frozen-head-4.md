# Frozen head 4: int5 after the census-ancestors and neg8-delta lanes, the sealed reference pin and the T3 prune (integrator, 2026-10-07)

- **Branch:** `integrate/2026-10-07-int5`, pushed.
- **Head:** `fe28e5a0cc6125842ecf4b53f24385c73e4d6dd7`.
- **Previous frozen head:** `43ac12d0c` (`FROZEN_HEAD_3.md`).
- **Not touched:** the pinned estimator files. `git diff a434e363d..fe28e5a0c` is empty for `joulewise/reduce.py`, `joulewise/uncertainty_evidence.py`, `joulewise/powermetrics_fiducial.py` and `joulewise/adapters/powermetrics.py`.

## T3 prune

Ed, 2026-10-07: "I've abandoned all t3 integration as a control plane so you can prune all that out".

- The agent census is now `/usr/bin/pgrep -a -lf '[c]odex|[c]laude'`. This covers:
  - `night_gate.AGENT_CENSUS_PATTERN` and `AGENT_CENSUS_ARGV`;
  - `hazards.arm.AGENT_CENSUS_ARGV`;
  - `arm_census` discovery, which follows night_gate.
- Removed T3 matching:
  - `agent_identity` no longer names the T3 Code app or its helpers;
  - `arm_census` no longer treats the T3 Code CLI as an interactive root;
  - `t0_rehearsal._AGENT_TOKEN_RE` drops `t3`;
  - `prewindow.py` drops `t3` from its comm list;
  - `gen_derivation_night.CENSUS_SUBSTRINGS` and the `gen_g2_phase_d` path guards drop `t3`.
- `t0_rehearsal`'s registry of census argvs gains the new argv and keeps both former ones (`-a … |[t]3` and `-lf … |[t]3`), so journals recorded with them still resolve.
- The physics-row check texts and the `arm.py` base-line comments name the new pattern.
- The runsheet region was regenerated with `gen_derivation_night.py` (`--check` PASS).
- Tests:
  - argv pins updated;
  - t3-specific cases deleted (T3 Code executable and app rules, the t3-code root, the "t3 code" census hit, the t3 prewindow comm line and fence cases, the t3 census marker);
  - fixture rules that kept temp roots free of "t3" for the census now check codex and claude only;
  - the live ancestor test puts its foreign `run_campaign` under `.claude`, so pgrep still lists it by substring.
- **Kept on purpose:** `scripts/prewindow_check.sh` keeps its sealed bytes, including `t3` in its comm list. It is a live pin of the sealed revision-6 registration (`prewindow_check_sha256` d8458eea…; calibration acceptance issuance checks the dwell script against it), so changing it needs a registration erratum. The only effect is that a process named t3 is over-refused at the legacy pre-window check.
- The T3 harness commit 7786b24d6 was reverted (430f3b8ef) before the prune.

## Commits since 43ac12d0c

On int5 (first parent):

| Commit | What |
|---|---|
| 73d2b2024 | Merge `lane/2026-10-07-census-ancestors` (ca25d9299). No conflicts. |
| 2f7893d45 | Merge `lane/2026-10-07-neg8-delta-fixes` (294f6e573). No conflicts. |
| 7786b24d6 | T3 Code harness as an agent (orchestrator call). **Reverted by 430f3b8ef.** |
| 754c8c093 | **Sealed `neg8_reference` identity pin.** Orchestrator call; details below. |
| bbdae1e86 | Suite fixes, described below. |
| 430f3b8ef | Revert of 7786b24d6, on Ed's T3 decision. |
| 63d2b9bad | Prune T3 from the agent census. |
| fe28e5a0c | T3 prune follow-up: the sealed `prewindow_check.sh` keeps its bytes; the g2a fence cases are updated. |

bbdae1e86 has two fixes:
- `whole_window._archive_bytes` and `harvest_neg8_allowance_bracket` read the harvest archive through `read_authentication_input`, so an authenticated session records the bytes the claim's allowance rests on (`test_authentication_io`).
- `test_battery_float_consumers` registers the `t0` `_agent_lines_decided` replace site (14 → 15 rows).

Lane commits:

| Commit | What |
|---|---|
| c0f37974a | census-ancestors: `pgrep -a` (an agent that launched the census is a hit) |
| ca25d9299 | census-ancestors: interpreter-option parsing (Sol delta A4); the quiet sampler and the t0 probe go through `agent_identity` |
| 6fd863645 | neg8-delta A1: the claim's drift allowance comes from the harvest's `derived/neg8-allowance.json` |
| 66c956dba | neg8-delta A2: the `neg8_reference` identity group |
| 3cf9d6b2f | neg8-delta A3: the roster names the references |
| 294f6e573 | neg8-delta A5: a strict-invalid reference is lost |

Measurement-code diff (`git diff --stat 43ac12d0c..fe28e5a0c -- joulewise scripts`):

```
 joulewise/agent_identity.py            | 197 ++++++++++++++++++++++++++++++++++++++++++++------
 joulewise/analysis_engine/__init__.py  |   2 +
 joulewise/analysis_engine/inputs.py    |   7 ++
 joulewise/arm_census.py                |  22 +++---
 joulewise/arm_readiness_evidence_t0.py |  21 +++++-
 joulewise/b5/harvest.py                | 193 +++++++++++++++++++++++++++++++++++++++++++------
 joulewise/cli.py                       |  14 ++++
 joulewise/hazards/arm.py               |  21 +++---
 joulewise/night_gate.py                |  16 ++++-
 joulewise/prewindow.py                 |   2 +-
 joulewise/quiet_admission.py           |  10 ++-
 joulewise/t0_rehearsal.py              |   9 ++-
 joulewise/whole_window.py              | 288 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-
 scripts/gen_derivation_night.py        |   6 +-
 scripts/gen_g2_phase_d.py              |   8 +--
 scripts/run_campaign.py                |  13 ++++
 scripts/write_b5_identity_pins.py      | 205 ++++++++++++++++++++++++++++++++++++++--------------
 17 files changed, 905 insertions(+), 129 deletions(-)
```

## The sealed `neg8_reference` pin (754c8c093)

`scripts/write_b5_identity_pins.py` derives the unit the same way it derives a pack unit.

- **Configs.** All 20 committed reference and spare configs (`window_references_v5`, `window_reference_spares_v5`: 7 references and 13 spares). They name one model (Qwen2.5-1.5B-Instruct-4bit, revision 8b403126…) and one output policy (`run_workload`, fixed_budget_exact 256).
- **Runtime stack.** Taken from the six real `neg8-window-*` bundles of the 2026-10-06 real-model rehearsal's harvest archives (`rehearsal-real/{alpha-1,gamma-2}/archive/sources/claim-runs`). All six share one stack and pass the same runtime-environment check against the measurement interpreter.
- **Model digest.** fea4cb940b54448a693c95a0734949cbdca21a39dda990d669b7f615e4a7c712, as the bundles recorded it. It is required to equal the frozen pins of the same model and revision in the committed plan trees `d117_floor_qwen25_1p5b_v1` and `d117_contrast_qwen25_1p5b_vs_7b_v1`; it does.
- **Runtime identity.** e769305d149c49ec2ec5b1ecca1be2c3a5152838a49d25d2b7d22b26d157891a.
- **Pack units are unchanged.** Their reference bundles are not mixed with these.
- **Tests:**
  - The committed draft carries the unit's config set, policy, stack and panel pin.
  - The harvest's majority tests remove the sealed pin explicitly.
  - A new test runs the committed sealed pin (`pin_source` `sealed_pin`).

## Hashes at fe28e5a0c (every check passes)

| Check | Result |
|---|---|
| ALPHA / BETA / GAMMA `generate_configs.py --check` | rc 0; plan trees 1d87a30955fa978d3a3a22dc0048720691e0128e4a3fe83477fc375d13dd031a / 0cdb33836f4632827bc74be194e388450c53b3314db1c72d9e9904e625868670 / 8b1d1d7176f5ee2286038e91df6427e47476c3a4bdee45a1c24687d49d80e3bf (unchanged) |
| `size_b5_window.py --check` | rc 0; sizing_b5.json 89e7ea70be34d855285c7d2c87df42b646d179a632a1e05ed57a4682a961b3aa (unchanged) |
| `write_b5_identity_pins.py --check` | OK; **identity_pins.json a0865895dc7eeb4ecea28c611b65fab9eee69d5e16f5f8126dbe08ac5255bda9** (was f78a27f8…; adds `units.neg8_reference`) |
| `reference_spares --check` | rc 0 |
| generator parity (`--baseline-ref 2011ec285`) | PARITY_OK, 357 files |
| `repin.py --check` | PASS, 16 families; registry.json a4a2be94912c4a3c33b1fb04e0f91e9e691290e2a7b7ee98898783ff307033b2 (unchanged) |
| `gen_derivation_night.py --check` | PASS |
| refusal census | clean at 63d2b9bad and fe28e5a0c |

## Whole suite (shard method)

How it was run:
- Suite head: 63d2b9bad. fe28e5a0c restores one sealed script and edits one test; its modules were rerun alone.
- 6 shards, then the two exclusive modules. Interpreter `/opt/homebrew/bin/python3.13 -B`, `TMPDIR=/private/tmp/int5suite5`.
- Logs: `~/night-archive/gate-prune/frozen-suite-int5-5/` (`shard1..6.log`, `excl_*.log`, `rerun_*.log`, `run.sh`, `head.txt`).
- An earlier run at 754c8c093 (`frozen-suite-int5-4/`, `ABORTED.txt`) was stopped on Ed's T3 change. It found the two failures fixed in bbdae1e86.

| Part | Tests | In-suite result | Disposition |
|---|---|---|---|
| shard 1 | 1,728 | 3 F `test_sample_quiet_predicate_evidence` | Load/deadline class. Alone: 96 OK. |
| shard 2 | 1,538 | PASS (includes `hazards.test_monitor`: cost 0.251 %, OK) | |
| shard 3 | 1,415 | PASS | |
| shard 4 | 1,928 | 1 E `test_harvest_b5_window` WorkerPoolTests | Load class. Alone: 176 OK. |
| shard 5 | 1,461 | 1 F `test_revision6_seal` (`prewindow_check_sha256`) | **Real**, fixed in fe28e5a0c (sealed bytes restored). Alone: 3 OK. |
| shard 6 | 1,683 | 2 F `test_gen_g2a_window` (t3 fence cases), 1 F `test_v5_s1_qualification` courier timing | g2a: **real**, fixed in fe28e5a0c (alone 15 OK). Courier: load class (alone 23 OK). |
| calibration_exits | 48 | OK | |
| calibration_writer_crash_matrix | 20 | OK | |

Total: 9,753 tests in shards + 68 exclusive = **9,821**.

`test_prewindow_check` with the restored script: 13 OK alone.

**Known load flakes**
- **`hazards.test_monitor` (half-a-percent CPU cost):**
  - In the suite: PASS, 0.251 % plain and 0.659 % background.
  - Alone it failed every time it was run here: 0.541 %, 0.591 %, 0.681 % and 0.585 % plain (background 1.05–1.47 %).
  - The monitor code is unchanged since phase 1. At a434e363d, one rerun alone was also 0.537 % FAIL and the next OK.
  - Recorded as the known load flake.
- **`test_b5_driver_p3 … test_the_reaper_reads_the_named_journal`:** passed in this suite.

Affected-module runs before the suite, all OK:
- the census, identity, arm_census and prewindow group (256);
- evidence_night, night_kinds, gen_evidence_night and gen_derivation_night (243, after the prune commit, because these clone the committed head);
- run_night, t0 and arm_readiness (432);
- watchdog and b5_driver (272);
- tests/hazards (286, apart from the monitor-cost flake).

After the suite, `ps` showed no leftover test processes, and no `__pycache__` was left in the pack directories.
