BRIDGE_REPORT_V1
{"seat": "S11-INDEX-1", "genre": "implementation", "status": "DONE_WITH_OPEN_ISSUES",
 "branch": "lane/2026-10-28-b5-window-index", "base": "2b3047d5b",
 "acceptance": {"I1": "met", "I2": "met", "I3": "met", "I4": "met", "I5": "met (inputs listed; two Mac-side actions needed)"},
 "needs_ruling": [], "needs_scope": []}
END_BRIDGE_REPORT_V1

# S11-INDEX-1: block-5 window index

## SUMMARY

`configs/analysis/b5/analysed_windows.json` is written from tracked records only. It holds all 11 block-5 attempts:
first seal ALPHA a1–a3, and second seal ALPHA a1, BETA a1–a6 and GAMMA a1. It loads with the real
`load_window_index`, using the real seal pins and the sealed pack table. The real `select_analysed_attempts` picks
exactly ALPHA a1, BETA a6 and GAMMA a1 from it. No measured value was opened, and no code, registration, plan, seal
record or L9 file was changed.

**The laptop dry run cannot start with only the bytes transferred so far.** L9 opens the attempt record of
*every* indexed attempt (`archive.py:114`, reached from `dry_run.py:528` at step 0 and again by each child
program). The 8 history archives were deliberately not transferred, so step 0 would refuse with
`harvest_record_not_the_indexed_one`. The schema can still represent them, so this is a missing input, not a
NEEDS_RULING. A second gap: 4 calibration captures that the archived ledgers reference are MISSING on the
measurement Mac. Whether step 3b reads them depends on their ledger rows (details under I5).

## I1–I5

| # | Result | Evidence |
|---|---|---|
| I1 | met | 11 entries. Attempts are numbered 1..n with no gap per (pack, seal): first/alpha 1,2,3; second/alpha 1; second/beta 1..6; second/gamma 1. t0 is non-decreasing, which `_complete_history` enforces when the file loads. Each entry carries `record_citation` as a map from field to `file:line`, for verdict, claim_usable, harvest sha256, pin, t0, archive root, custody/runs/measurement roots, G10 and cause key, plus `history_table` (`seal2-gamma-a1-window.md:65-80`). The generator checked that every cited line contains the cited value. The test re-checks the main ones, and a mutation of one t0 makes it fail. All entries are `entry_kind: harvested`, because every attempt has an archive. The first seal is `seal: "first"`, pin1 `7e6158d6`, which `governing_pin` gives for the first seal. |
| I2 | met | Paths are absolute under `/Users/edr`. `archive_root` is `/Users/edr/night-archive/harvest-<plan>` (BETA a4: `…-r2`, with the cut-short first harvest in `superseded_archive_roots`). `claim_runs_root` is `/Users/edr/night-b5/<plan>/runs_<pack_id>`, and `bound_runs_root` is the same path plus `_bound`. `custody_root` is `/Users/edr/night-custody/<plan>`. `measurement_root` is `…/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18` for the second seal (`second-clone.md:11`) and `…-20261008T0817Z-b5` for the first seal (`SEAL_RECORD.md:278`). The analysed windows' roots each contain manifest files; see the manifest evidence below. |
| I3 | met | `harvest.json` sha256 in the harvest manifest equals the index value for each analysed window (ALPHA `baf397d6…7ab5`, BETA `80398a5d…97fe`, GAMMA `4bb49435…d1c7`). `harvest_pin`: ALPHA a1 `224a264c5faaae90cdf56118df37e773a932700b` (pin2; t0 1791587520 ≤ erratum-2 epoch 1791649800). BETA a6 and GAMMA a1: `b039c0257d1b1d407ee9598222db3f78f6ad7beb` (pin4; t0 > erratum-3 epoch 1791738000). This is the full 40-hex head that `seal_pins.json` lists and `IndexEntry.harvest_pin` requires. |
| I4 | met | `tests/b5_analysis/test_analysed_windows_index.py`, 5 tests: (1) the attempt census plus pin and pack-table checks; (2) the real `select_analysed_attempts` over structural stand-in records built from the index's own verdict and claim_usable fields; (3) citation lines; (4) the manifest cross-check, which skips with a reason because the manifests are on main and not on this branch; (5) the real `open_attempt_record` + `select_analysed_attempts` over the archives, which skips with a reason when `JW_B5_SYNTHETIC_ONLY=1` or when any root is absent, naming the absent roots. |
| I5 | met | See the INPUTS table below. |

Manifest evidence (main `286269100`, `docs/process_traces/2026-10-27-l9-restart/b5-transfer/`, data_root `/Users/edr`):

| Window | root | manifest | a file under it |
|---|---|---|---|
| ALPHA a1 | archive_root | `v5-b5-alpha-a1-20261009T2312Z-harvest.manifest.json` | `night-archive/harvest-v5-b5-alpha-a1-20261009T2312Z/harvest.json` (sha `baf397d6…`) |
| | claim_runs_root | `…-runs.manifest.json` | `night-b5/v5-b5-alpha-a1-20261009T2312Z/runs_d117_floor_qwen3-1p7b_v5/campaign_log.jsonl` (3186 files) |
| | bound_runs_root | `…-runs.manifest.json` | `…/runs_d117_floor_qwen3-1p7b_v5_bound/…` (551 files) |
| | custody_root | `…-custody.manifest.json` | `night-custody/v5-b5-alpha-a1-20261009T2312Z/b5-window-plan-record.json` |
| BETA a6 | archive_root | `v5-b5-beta-a6-20261011T2011Z-harvest.manifest.json` | `night-archive/harvest-v5-b5-beta-a6-20261011T2011Z/harvest.json` (sha `80398a5d…`) |
| | claim / bound | `…-runs.manifest.json` | `night-b5/v5-b5-beta-a6-20261011T2011Z/runs_d117_floor_qwen3-8b_v5/campaign_log.jsonl` (3170) / `…_bound` (534) |
| | custody_root | `…-custody.manifest.json` | `night-custody/v5-b5-beta-a6-20261011T2011Z/b5-window-plan-record.json` |
| GAMMA a1 | archive_root | `v5-b5-gamma-a1-20261012T0420Z-harvest.manifest.json` | `night-archive/harvest-v5-b5-gamma-a1-20261012T0420Z/harvest.json` (sha `4bb49435…`) |
| | claim / bound | `…-runs.manifest.json` | `night-b5/v5-b5-gamma-a1-20261012T0420Z/runs_d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/campaign_log.jsonl` (2609) / `…_bound` (526) |
| | custody_root | `…-custody.manifest.json` | `night-custody/v5-b5-gamma-a1-20261012T0420Z/b5-window-plan-record.json` |
| all three | measurement_root | `measurement-corpus18-data.manifest.json` | `night-custody/measurement/JouleWise-measurement-20261009T1814Z-b5-corpus18/runs/calibration_observation_ledger.jsonl` |

In each harvest archive, the `sources/claim-runs/` count equals the runs-manifest file count of the claim root
(3186 / 3170 / 2609). This matters for step 0's `compare_runs_root` (`archive.py:310-335`). The claim roots are not
under `custody_root`, so the `claim-runs/` prefix applies. Test 4 passes when the main manifests are copied into
the tree (run here and then removed).

## Entry table

| pack | seal | att | plan id | verdict | claim_usable | cause_key | pin | citation (verdict / sha) |
|---|---|---|---|---|---|---|---|---|
| alpha | first | 1 | v5-b5-alpha-a1-20261008T2201Z | COLLECTED | false | NEG8+cell.below_minimum | 7e6158d6 | alpha-a1-window.md:60 / :59 |
| alpha | first | 2 | v5-b5-alpha-a2-20261009T0515Z | NULL | false | hazard:contention | 7e6158d6 | alpha-a2-window.md:55 / :54 |
| alpha | first | 3 | v5-b5-alpha-a3-20261009T0644Z | COLLECTED | false | NEG8 | 7e6158d6 | alpha-a3-window.md:98 / :97 |
| alpha | second | 1 | v5-b5-alpha-a1-20261009T2312Z | COLLECTED | **true** | null | 224a264c5 | seal2-alpha-a1-window.md:66 / :65 |
| beta | second | 1 | v5-b5-beta-a1-20261010T0742Z | COLLECTED | false | NEG8 | 224a264c5 | seal2-beta-a1-window.md:73 / :72 |
| beta | second | 2 | v5-b5-beta-a2-20261010T1756Z | COLLECTED | false | CALIBRATION+NEG8+cell.below_minimum | 0699abbb0 | seal2-beta-a2-window.md:68 / :74 |
| beta | second | 3 | v5-b5-beta-a3-20261010T2151Z | NO_COLLECTION | false | CALIBRATION+NEG8+ROSTER+cell.below_minimum | 0699abbb0 | seal2-beta-a3-window.md:63 / :68 |
| beta | second | 4 | v5-b5-beta-a4-20261010T2237Z | COLLECTED | false | CALIBRATION | 0699abbb0 | seal2-beta-a4-window.md:137 / :139 |
| beta | second | 5 | v5-b5-beta-a5-20261011T0739Z | COLLECTED | false | CALIBRATION | 0699abbb0 | seal2-beta-a5-window.md:16 / :19 |
| beta | second | 6 | v5-b5-beta-a6-20261011T2011Z | COLLECTED | **true** | null | b039c0257 | seal2-beta-a6-window.md:20 / :23 |
| gamma | second | 1 | v5-b5-gamma-a1-20261012T0420Z | COLLECTED | **true** | null | b039c0257 | seal2-gamma-a1-window.md:24 / :29 |

t0 comes from each arm record (for example `seal2-beta-a6-arm.md:5`, epoch 1791749460). G10: only first-seal ALPHA a1
requested it (`alpha-a1-arm.md:33`). `g10_redraw_cycles` is null everywhere because no record gives it.

## INPUTS (I5): what L9 steps 0–11 read that the transfer manifests do not hold

This census traced the code at `2b3047d5b` (identical to `2ea99f51f`); no data was read. A delegated read-only
agent did the trace. I re-read the lines it rests on: `archive.py:114,210`, `calibration_bracketing.py:1966-1984`
and `:2955-2967`, `calibration_ledger.py:5517` and `identity_pins.py:858`.

| Input | Read at | Step | Status |
|---|---|---|---|
| History archives (8): `harvest.json`, `derived/exclusions.json`, `derived/window_flags.json`, and for pin3 records that list it (BETA a2–a5) `derived/neg8-screen.json`, each at its indexed `archive_root` (BETA a4: `…-r2`) | `archive.py:114,142,177,210-211` via `open_attempt_record` for every entry: `dry_run.py:528`; also each child's `--window-index` load (`scripts/extract_detection_floors.py:79`, `scripts/mint_floor_artifact_generalized.py:153`, `joulewise/analysis_engine/inputs.py:347`, `paper_custody.py:698`, `scripts/produce_b5_disclosures.py:156`, `scripts/build_results_fill_input.py:70`) | 0, 4, 5, 8, 6, 9, 9b, 10, 11 | **ABSENT, Mac-side action.** Transfer these files from the 8 history archives on the measurement Mac (the restricted `derived/` files stay automation-only). Without them step 0 refuses with `harvest_record_not_the_indexed_one`. |
| Calibration captures named by custody locator in each analysed archive's `sources/ledger/calibration_observation_ledger.jsonl` (truncated at `derived/terminal-pin.json`) | `bracket.py:256-261` → `calibration_bracketing.py:1986`, `:1815-1819`; backup roots disabled (`dry_run.py:55-65`) | 3b, and again inside children 4–11 | 126 present (`ledger-captures.manifest.json`, plus 6 inside the runs items). **4 MISSING**: BETA a2 and BETA a3 `cal-post` (referenced by the BETA a6 and GAMMA ledgers), and two `night-g2a/d117-g2a-prefill-probe-…-cal-post` (referenced by all three). A capture is read only if its row is `valid`, not a historical import, in a finalized or no session, not derivation-kind and not pipeline-refused (`calibration_bracketing.py:1966-1984`). If one is read and is absent, the custody count fails (`:2955-2967`), and every bracket gives `window_bracket_not_passed` at 3b. **Mac-side action:** a structure-only check of those 4 rows' disposition and session fields in the three archived ledger copies. Do not guess. |
| Path layout `/Users/edr/…`, including `Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup/…` | locators are absolute; remapping disabled | 3b+ | needs a laptop check that the unpacked paths are exact |
| Analysis checkout: HEAD contained in `origin/main`; no untracked files | `identity_pins.py:858` (mint, step 5); `dry_run.py:38-43`; `paper_custody.py:565,629-634` (index read as the HEAD blob and required to equal the working tree) | 0, 5, 9b, 10 | **not yet:** this index is on a lane branch, so it must be merged with L9 before the real run. |
| Env `JOULEWISE_NIGHT_CUSTODY_BUDGET_S` | `calibration_ledger.py:5517` refuses every locator read if set | 3b+ | must be unset on the laptop |
| Custody `night/chain.exited`, `night/result.json` | `window_lineage.py:601,611` | 4–11 | present (custody manifests); the path comes from bundle-stamped `night_dir`, which was not seen |
| Bound runs root NEG-8 corpus bundles | `whole_window.py:3477-3505` (data-dependent) | 4–11 | present (runs manifests) |
| Live ledger `runs/calibration_observation_ledger.jsonl` | `dry_run.py:555,1159` | 0 | present (corpus18 manifest) |

Present or not needed: the analysed archives, claim and bound roots, tracked repo configs (`seal_pins.json`, sizing,
plan trees, catalog, pack specs, supply map). Nothing reads `superseded_archive_roots` except an emptiness test
(`dry_run.py:999`). Found not read: the results-clone, seal-record FILL text, `night-plan-staging/*`, the measurement
clone's tracked code and its local-only pin commits, and `/private/tmp`. The seal-record analysis addendum and its
FILLs are release-record obligations (scout report §2), not driver inputs.

## FILES CHANGED

`git diff --name-only 2b3047d5b`: `.codex-report/S11-INDEX-1.md`, `configs/analysis/b5/analysed_windows.json`,
`tests/b5_analysis/test_analysed_windows_index.py`. These are exactly the WRITE_SCOPE paths.

## VERIFICATION

```
$ JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest tests.b5_analysis.test_analysed_windows_index tests.b5_analysis.test_windows
Ran 28 tests in 9.387s
OK (skipped=2)
```

Also run: `tests.test_digest_pin_census`, `tests.test_repin` (51 OK, with the index tracked), `scripts/repin.py --check`
(PASS 16 families), and `tests.test_docs_freshness` (31 OK).

## DECISIONS I MADE

1. **cause_key format.** The value follows registration §7.3 (`registration_block5.md:4711`): the catalog families of
   the `exclude_window_reasons` codes, with `cell.below_minimum` a family of its own, sorted and joined with `+`. A NULL
   attempt is keyed `hazard:<module>`. Families come from the sealed catalog (`5d77c725…`). Claim-usable attempts get
   null. Where a record states the key, it is cited (`alpha-a2-window.md:64-65`, `alpha-a3-window.md:130`,
   `seal2-beta-a1-consult.md:151`); otherwise the rule and the catalog are cited.
2. **BETA a4's cut-short harvest** (`seal2-beta-a4-window.md:12-14`) goes in `superseded_archive_roots`, and `-r2` is
   the deciding archive. This is history only; no code reads it.
3. **record_citation is a field→`file:line` map**, which the schema allows as a Mapping. Where an attempt's own records
   do not state a root (BETA a3–a6 runs roots, BETA a4 custody), the citation says so ("pattern of the other attempts
   of this seal"). No code reads those roots for history entries.
4. Test 2 uses structural stand-in records, because the archives are not in the cloud. Test 5 is the real-reader
   version, and it skips under `JW_B5_SYNTHETIC_ONLY=1`.

## OPEN ISSUES

1. History archives absent on the laptop (I5 row 1): this blocks step 0.
2. Four MISSING calibration captures (I5 row 2): they may block 3b, depending on their ledger rows.
3. `t0_epoch_s` must equal each archive's `derived/window_flags.json` `window.t0_epoch_s` (`archive.py:188`). The
   index takes t0 from the arm records' plan epochs. Only the real reader on the laptop (test 5) can confirm this.
4. Cause-key reading differs from a record: `seal2-beta-a2-window.md:77-78` says BETA a1 and a2's cause families
   differ, but under the sealed catalog `whole_window.verdict_absent` is family NEG8, so both keys contain NEG8.
   This is disclosure text only, and it affects no number or selection. The lead may want to note it.
5. The index must merge with L9 so HEAD is in `origin/main` (I5 row 4).

## NEEDS_RULING

None. L9's schema represents every record as it stands.
