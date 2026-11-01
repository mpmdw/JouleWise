STATUS: DONE

# TRIM-B1-FABLE-REV: independent executing review of PR #617 and PR #618

Reviewer: Fable (non-author). Branch `review/2026-11-01-trim-b1-fable` from origin/main `8757a6611`. Only this report and its logs are committed. The two PR branches were not pushed to, merged or commented on.

Heads reviewed:
- **#617** `5245912321654c5d93614af755821402084828c3` (`lane/2026-11-01-trim-b1-sha256`): strict SHA-256 digest check in `joulewise/load_transition_alignment.py`.
- **#618** `b04756bd893d37998d634afd0fd78f078ee77a98` (`lane/2026-11-01-trim-b1-mg1112`): retire the MG-11/MG-12 coverage maps; `battery.PROTECTS` becomes a plain tuple.

Both heads are origin/main `8757a6611` plus exactly one commit, so for each PR "current main merged into the head" is the head itself. The two heads merge cleanly with each other (no conflicts, merge commit `0cb919325` in a scratch worktree), and the whole suite was run on that combined tree.

Environment: macOS, `/opt/homebrew/bin/python3.13`, `TMPDIR=/private/tmp/jwrev-tmp`, `JOULEWISE_CUSTODY_PARENT=<fresh temp dir>`, `JW_B5_SYNTHETIC_ONLY=1`. All work in detached scratch worktrees under `/private/tmp/jwrev*`; `/Users/edr/jw-b5-attempt-c` and `/Users/edr/jw-b5-staging` were not modified; no custody or restricted directory was read.

## Verdicts

| PR | Verdict | One line |
| --- | --- | --- |
| #617 | **ACCEPT** | Fix is correct and minimal; no stored or runtime input regresses; both fixes are killed by the new tests; "registry not regenerated" reasoning verified. Two low-severity notes, neither blocking. |
| #618 | **ACCEPT** | No remaining reader of the removed symbols or maps; battery refusals and outputs byte-identical to main on every fixture; registry delta is exactly the two holder rows plus counts; no protected path touched. One low-severity note. |

## Findings

Severity scale: HIGH blocks merge; MEDIUM should be fixed before or soon after merge; LOW is informational or a lead's call.

### #617

1. **LOW (test gap, not a code bug).** The PR body says the `artifact_id` check "also accepted uppercase hex despite its error text" and now rejects it. True (verified: on main `int("A"*64, 16)` parses and the old branch had no lowercase test; at the head `_is_sha256("A"*64)` is False). But `test_artifact_id_must_be_lta_plus_a_strict_digest` iterates only `NOT_DIGESTS[:4]`, which excludes the `"A"*64` case, so the uppercase rejection on the `artifact_id` path is not pinned through `validate_alignment_artifact`. Mutant M4 (allow uppercase in `_LOWER_HEX`) is still killed, but only by the direct `_is_sha256` test and the Part-B source-hash test, not by the artifact_id test. Suggested one-line fix in a follow-up or before merge: iterate `self.NOT_DIGESTS` (all eight) in that test. Not blocking.
2. **LOW (lead's call, gate row 4).** The module is the P2-046A load-transition characterization analyzer and its manifest lives under `configs/calibration/p2_046_load_transition/`. The change touches only the digest shape test, not alignment arithmetic. Whether row 4 reads N/A is for the lead; from an executing lens the end-to-end analyzer output on the shipped manifest and fixture is byte-identical between main and the head (see 1.1 below).

### #618

3. **LOW (informational).** After this PR, `PROTECTS` and `SUPERSEDES` in all seven hazard modules are records with no consumer anywhere in the repo: deleting both from `battery.py` entirely (mutant K2) leaves `tests.hazards.*` and `tests.test_battery_float_consumers` green. That is the PR's stated intent ("a record only"), and it is consistent with MG-11 class X/DELETE, but the lead should know these tuples are now unverified prose. Nothing to fix in this PR.

No MEDIUM or HIGH findings on either PR.

## 1. PR #617

### 1.1 Callers and legitimate inputs

`_is_sha256` is called at five sites in `joulewise/load_transition_alignment.py` (lines 296, 297, 608, 624, 635, 636 at the head): the Part-B `raw_samples_sha256` / `markers_sha256` source fields on build and on validate, the manifest provenance `sha256`, the observations provenance `sha256`, and (new) the `artifact_id` suffix. The module is imported only by `scripts/characterize_load_transition.py` (the only runtime caller) and `tests/test_gate_sensibility_rounding.py` (imports constants).

Stored inputs that reach these checks:
- `configs/calibration/p2_046_load_transition/manifest.json` carries no sha256 field (`git grep sha256` on that directory is empty).
- `tests/fixtures/p2046/*.json` all have `raw_samples_sha256: null`, `markers_sha256: null` (the synthetic-fixture branch, which does not call `_is_sha256`).
- No stored alignment artifact (`"lta-...`) exists anywhere in the repo; the only `lta-` strings are the module, its test and a legacy doc mentioning the prefix.
- No uppercase 64-hex literal exists anywhere under `configs/calibration/`.
- The provenance digests are computed at runtime by `hashlib.sha256(...).hexdigest()` (`canonical_sha256`, `_load_json` in the script), which is always lowercase hex, so they pass the strict check.

End-to-end run of `scripts/characterize_load_transition.py --manifest configs/calibration/p2_046_load_transition/manifest.json --observations tests/fixtures/p2046/valid_observations.json` on clean origin/main and on the head: both exit 0, both write `PROVISIONAL_FIXTURE_ONLY; NO_PHYSICAL_BOUND_CONCLUSION_PART_B_NOT_EXECUTED`, and the two output files are byte-identical (`cmp` equal; `artifact_id` `lta-2321badcb2eba04d8f309ce9cdd7ef199721dbc6755b2b749104fba4d8169814`). `validate_alignment_artifact` on that artifact at the head returns `[]`.

Conclusion: no legitimate input that passed before now fails.

### 1.2 "Registry not regenerated" reasoning

Verified:
- `python scripts/repin.py --check` at the head: `PASS 16 pin families current`.
- `repin.py --write registry` on clean origin/main vs. on the #618 head (which includes the full drift) differs only in #618's own rows (section 2.3). The #617 change touches `joulewise/load_transition_alignment.py` and its test only; that file's registry rows are era records at `c27485347` and the sealed-inventory row, neither of which depends on the main working tree. So regenerating in #617 would add only the pre-existing drift (2,552 changed lines between committed main and regenerated main), which #618 carries. The reasoning is correct, and skipping it avoids a conflict with #618.

### 1.3 Mutant table (kill tests)

Module under test: `tests.test_load_transition_alignment`, run at the head with each mutant applied alone and reverted afterwards (`git status` clean after each). Logs: `.codex-report/logs/trim-b1-fable/mutants/617-*.log`.

| Mutant | Change | Tail | Killed |
| --- | --- | --- | --- |
| M0 baseline | none | `Ran 13 tests in 0.322s` / `OK` | n/a |
| M1 | revert `_is_sha256` only to the `int(value, 16)` + `lower()` form | `Ran 13 tests` / `FAILED (failures=12)`: 4 subtests each in `test_is_sha256_accepts_only_64_lowercase_hex_digits`, `test_part_b_source_hash_must_be_a_strict_digest`, `test_artifact_id_must_be_lta_plus_a_strict_digest` (values `0x`+62, leading space, trailing newline, `_` separator) | yes |
| M2 | revert the `artifact_id` check only to `len == 68` + `int(artifact_id[4:], 16)` | `Ran 13 tests` / `FAILED (failures=4)`: the 4 subtests of `test_artifact_id_must_be_lta_plus_a_strict_digest` | yes |
| M3 | drop `len(value) == 64` from the new check | `Ran 13 tests` / `FAILED (failures=4)`: `a*63` and `a*65` in the `_is_sha256` test and the Part-B test | yes |
| M4 | widen `_LOWER_HEX` to accept `A-F` | `Ran 13 tests` / `FAILED (failures=2)`: `A*64` in the `_is_sha256` test and the Part-B test (not in the artifact_id test; finding 1) | yes |

M1 reproduces the PR body's stated counterfactual tail exactly (12 failures over the three new tests).

## 2. PR #618

### 2.1 No remaining readers

`git grep -nE '\bPROTECTS\b|\bSUPERSEDES\b|COVERAGE_MAP|frozen_grammar_rows|FROZEN_GRAMMAR_FILE|physics_rows|number_rows'` at the head over `joulewise/`, `scripts/`, `tests/`, `.github/`, `docs/process/*.json` and `configs/` (excluding `configs/pins/registry.json`, where the two holder rows are removed) returns only:
- the `PROTECTS: ... = (` and `SUPERSEDES: ... = (` definitions in the seven hazard modules and `base.py`'s module docstring, with comments saying the map was retired by MG-11;
- `tests/fixtures/hazards/README.md`, which says where the builder tools went.

No `getattr(..., "PROTECTS")` string form exists. `.github/workflows/ci.yml` and `scripts/quick_suite.py` do not name the deleted modules; `scripts/test_timings.json` had the two deleted modules' timing rows removed (its 2026-10-06 provenance note still lists them as a historical record, which is fine). `docs/process/*.json` (`audit-baseline-manifest.json`, `state_kernel.json`, `state_kernel.schema.json`) have no reference.

Executed, not just grepped:
- On the head: `import joulewise.hazards.battery as b` gives `len(b.PROTECTS) == 14`, no `COVERAGE_MAP`, no `frozen_grammar_rows`, no module `__getattr__`.
- On main: `len(b.PROTECTS) == 25` = 14 written + 11 rows loaded from the map, and the 11 extra rows are exactly the `FROZEN_ROWS` set the deleted test pinned (all `joulewise/battery_float.py` rows). So the 11 dropped rows are exactly the lazily loaded ones; the 14 written rows are unchanged.

### 2.2 The 11 dropped rows change no runtime decision; battery outputs unchanged

- Mutant K3 (on origin/main, in its own worktree): delete `configs/gates/physics_rows.json`. Importing all seven hazard modules and `scripts/hazard_monitor.py` succeeds; accessing `battery.PROTECTS` then raises `FileNotFoundError`, which proves the read happened only on attribute access. `tests.hazards.test_arm` (`Ran 23 tests` / `OK`), `tests.hazards.test_monitor_p2` (`Ran 6` / `OK`) and `tests.hazards.test_import_graph` (`Ran 6` / `OK`) pass without the map; only `tests.hazards.test_battery::test_protects_carries_the_frozen_grammar_rows` (`Ran 65` / `FAILED (errors=1, skipped=1)`) and `tests.hazards.test_physics_coverage` (`setUpClass` ERROR) fail, and both are the tests this PR deletes. So nothing on the arm or monitor path read the map on main.
- Mutant K2 (on the head): delete `PROTECTS` and `SUPERSEDES` from `battery.py` entirely. `tests.hazards.test_battery` `Ran 64 tests` / `OK (skipped=1)`; `test_import_graph` `Ran 6` / `OK`; `test_arm` `Ran 23` / `OK`; `test_monitor_p2` `Ran 6` / `OK`; `tests.test_battery_float_consumers` `Ran 18` / `OK`. No reader (finding 3).
- Battery replay, main vs head: a scratch script drives `battery.judge(measure_bytes(raw, **kw), LIMITS)` (the test module's own harness) over every `tests/fixtures/hazards/battery/*.ioreg` fixture with four measurement variants (plain, `age_s=240`, `timed_out=True`, `returncode=1`), serialises status plus the full verdict dataclass, and records the publications-table keys: 33 records, 64 verdicts (8 PASS, 20 REFUSE, 36 UNMEASURED). The JSON produced on main and on the head is byte-identical (`cmp` equal). There is no checked-in hazard golden or replay file for the battery module (the instrument module has cadence replay fixtures; its code changes in a comment only), so this replay is the executing comparison.
- `git diff` of `battery.py`: the removed lines are the `json` and `Path` imports, the `COVERAGE_MAP` / `FROZEN_GRAMMAR_FILE` constants, `frozen_grammar_rows`, `__getattr__`, and the comment block; `_PROTECTS_WRITTEN` is renamed to `PROTECTS` with the same 14 rows. `parse_reading`, `measure`, `judge` and every threshold are untouched. The other six hazard modules and `base.py` change in comments or a docstring only.
- `configs/gates/hazard_refusals.json`: the one removed line is the BASELINE census entry for `battery.py::__getattr__` (`AttributeError|module has no`), which no longer exists. Mutant K1 (restore that line at the head) makes `tests.hazards.test_refusal_allowlist` fail with `stale: [{'function': '__getattr__', ...}]`: `Ran 23 tests in 30.588s` / `FAILED (failures=1, skipped=1)`. So the allowlist delta is exactly the required one and the test enforces it.

Suites at the head (one process per module): see 2.5.

### 2.3 Registry delta

`python scripts/repin.py --write registry` run on clean origin/main (`/private/tmp/jwrevmain`, working tree clean) and on the head (`/private/tmp/jwrev618`), each restored afterwards with `git checkout`:
- head committed `registry.json` vs head regenerated: **byte-identical** (`cmp` equal). The committed file is a faithful regeneration.
- main regenerated vs head regenerated (the PR's own delta): 22 diff lines, all of them: `issued_config` count 795 to 793; `P` 23741 to 23739; `files` 2648 to 2646; `literals` 27311 to 27309; removal of the holder `{"owner_lane": "L4", "path": "configs/flags/number_rows.json", ... ["/inventory/sha256", "issued_config", null]}`; removal of the holder `{"path": "configs/gates/physics_rows.json", ... ["/source/inventory_sha256", "issued_config", null]}`. Nothing else.
- main committed vs main regenerated (drift already on main, unrelated to this PR): 2,552 changed lines. main committed vs head committed (what the PR diff shows): 2,556 changed lines. The 4-line difference is the two holder rows and counts above.
- `python scripts/repin.py --check` at the head: `PASS 16 pin families current`.

The PR body's description of the delta is exact.

### 2.4 Protected paths

`git diff --stat origin/main...b04756bd8 -- 'joulewise/b5/**' joulewise/whole_window.py joulewise/reduce.py joulewise/run_campaign.py 'configs/analysis/b5/**' 'tests/b5_analysis/**'` is empty. The 21 changed files are the two deleted maps, `hazard_refusals.json`, `registry.json`, the seven hazard modules plus `base.py`, `scripts/test_timings.json`, the fixtures README, two fixture builder tools, and five test files; none is in the working-tree frozen set of `tests/b5_analysis/test_frozen_files.py` (run_campaign/reduce singles, `joulewise/flags/`, `powermetrics_fiducial.py`, `adapters/powermetrics.py`, `scripts/prewindow_check.sh`, the v5 packs, the pin4 files) and no sealed registration doc is touched. `tests.b5_analysis.test_frozen_files` passes on the merged tree (section 3).

### 2.5 Hazards, flags and affected modules at the head

One process per module at `b04756bd8`, 2 in parallel, logs under `.codex-report/logs/trim-b1-fable/suite-618/`.

Start 2026-11-01T10:22:40Z, end 2026-11-01T10:36:29Z. 32 modules, 32 exit 0, 0 failures. Every tail matches the PR body's Verification block.

```
tests.flags.test_flags_catalog                 Ran 6 tests  OK
tests.flags.test_flags_collect                 Ran 59 tests  OK
tests.flags.test_flags_core                    Ran 20 tests  OK
tests.flags.test_flags_exclusions              Ran 34 tests  OK
tests.flags.test_flags_fx_regressions          Ran 5 tests  OK
tests.flags.test_flags_identity_pins           Ran 6 tests  OK
tests.flags.test_flags_import_graph            Ran 3 tests  OK
tests.flags.test_flags_review_regressions      Ran 16 tests  OK
tests.flags.test_flags_schema                  Ran 10 tests  OK
tests.flags.test_flags_sink                    Ran 9 tests  OK
tests.hazards.test_arm                         Ran 23 tests  OK
tests.hazards.test_arm_dwell_clean_run         Ran 4 tests  OK
tests.hazards.test_arm_identity                Ran 7 tests  OK
tests.hazards.test_battery                     Ran 64 tests  OK (skipped=1)
tests.hazards.test_clock                       Ran 37 tests  OK (skipped=1)
tests.hazards.test_contention                  Ran 48 tests  OK (skipped=3)
tests.hazards.test_disk                        Ran 8 tests  OK
tests.hazards.test_import_graph                Ran 6 tests  OK
tests.hazards.test_instrument                  Ran 20 tests  OK
tests.hazards.test_monitor                     Ran 34 tests  OK (skipped=1)
tests.hazards.test_monitor_p2                  Ran 6 tests  OK
tests.hazards.test_refusal_allowlist           Ran 23 tests  OK (skipped=1)
tests.hazards.test_smc                         Ran 12 tests  OK (skipped=2)
tests.hazards.test_thermal                     Ran 7 tests  OK (skipped=1)
tests.test_b5_seal_landing                     Ran 9 tests  OK
tests.test_battery_float_consumers             Ran 18 tests  OK
tests.test_ci_docs_only                        Ran 12 tests  OK
tests.test_digest_pin_census                   Ran 22 tests  OK
tests.test_docs_freshness                      Ran 31 tests  OK
tests.test_harvest_b5_window                   Ran 208 tests  OK (skipped=24)
tests.test_repin                               Ran 47 tests  OK
tests.test_shard_split                         Ran 33 tests  OK
```

## 3. Whole suite on the merged tree

Tree: `/private/tmp/jwrevmerged` at merge commit `0cb919325` = #617 head `524591232` + #618 head `b04756bd8` (each already contains origin/main `8757a6611`; the merge had no conflicts). Modules enumerated exactly as CI does, via `scripts/shard_tests.discover_test_modules()` (the `unittest discover -s tests` selection, 464 modules including `tests/b5_analysis`). One `python3.13 -m unittest <module>` process per module, 5 in parallel (2 more were in use by the #618 head run), `TMPDIR=/private/tmp/jwrev-tmp`, fresh `JOULEWISE_CUSTODY_PARENT`, `JW_B5_SYNTHETIC_ONLY=1`. Per-module logs under `.codex-report/logs/trim-b1-fable/suite-merged/`.

Start 2026-11-01T10:22:40Z, end 2026-11-01T12:05:11Z (1 h 42 min wall). **464 modules, 463 exit 0, 1 exit 1; 11,738 tests run, 146 skipped, 0 failures attributable to either PR.** The per-PR gate-row-2 tails: #617 head == main+1 and #618 head == main+1, both contained in this tree.

The one non-zero exit is `tests.test_mlx_runtime_detokenizer`: `Ran 1 test in 0.000s` / `FAILED (errors=1)` with `ModuleNotFoundError: No module named 'test_mlx_runtime'` at import. This is a harness artifact of running `python -m unittest tests.<module>` from the repo root: that file does `from test_mlx_runtime import ...`, a bare import that only resolves when `tests/` is on `sys.path`, which `unittest discover -s tests` and CI's `scripts/shard_tests.run_units` (line 298: "Put ROOT and tests/ on sys.path the way discover -s tests does") both arrange. Evidence that it is not the PRs:
- the same command on clean origin/main `8757a6611` fails identically (`Ran 1 test` / `FAILED (errors=1)`, same `ModuleNotFoundError`; log `suite-merged/_rerun-on-clean-main.tests.test_mlx_runtime_detokenizer.log`);
- neither PR touches any mlx file (`git diff --name-only origin/main...0cb919325 | grep -i mlx` is empty);
- run the discovery way on the merged tree (`python -m unittest discover -s tests -t tests -p test_mlx_runtime_detokenizer.py`): the detokenizer module imports and its tests pass. With `-t tests` discovery swept 1,972 tests (39 skipped) in 3,097 s, and the only errors were three `tests.flags.test_flags_collect.RealPackTests` subtests raising `ArmReadinessError: untracked pack directory: b'__pycache__'`: the earlier 464-process run had left ignored `__pycache__/` directories inside `configs/campaigns/*/` of the scratch worktree, which that test treats as pack pollution. That is a scratch-tree side effect of running the suite twice in the same worktree, not a PR effect; `tests.flags.test_flags_collect` is `Ran 59 tests` / `OK` in the per-module run above and at the #618 head. No `tests.test_mlx_runtime_detokenizer` test errored or failed. Log: `suite-merged/_rerun-discover-way.tests.test_mlx_runtime_detokenizer.log`.

Every other module: `OK`. The full per-module list (464 lines of `module  Ran N tests  OK[ (skipped=k)]`) is in `suite-merged/_tails.txt`; the modules both PRs touch read, on the merged tree:

```
tests.test_load_transition_alignment      Ran 13 tests  OK
tests.flags.test_flags_fx_regressions     Ran 5 tests   OK
tests.hazards.test_battery                Ran 64 tests  OK (skipped=1)
tests.hazards.test_refusal_allowlist      Ran 23 tests  OK (skipped=1)
tests.hazards.test_import_graph           Ran 6 tests   OK
tests.test_battery_float_consumers        Ran 18 tests  OK
tests.test_repin                          Ran 47 tests  OK
tests.test_digest_pin_census              Ran 22 tests  OK
tests.test_docs_freshness                 Ran 31 tests  OK
tests.test_ci_docs_only                   Ran 12 tests  OK
tests.test_harvest_b5_window              Ran 208 tests OK (skipped=24)
tests.b5_analysis.test_frozen_files       Ran 3 tests   OK
tests.test_b5_seal_landing                Ran 9 tests   OK
tests.test_shard_split                    Ran 33 tests  OK
```

## 4. Logs committed

- `.codex-report/logs/trim-b1-fable/mutants/617-M0..M4-*.log`, `618-K1..K3-*.log`
- `.codex-report/logs/trim-b1-fable/registry/own-delta.diff` (main-regen vs head-regen)
- `.codex-report/logs/trim-b1-fable/e2e/` (P2-046 analyzer outputs, main and #617 head)
- `.codex-report/logs/trim-b1-fable/battery-replay/` (battery judge replay JSON, main and #618 head)
- `.codex-report/logs/trim-b1-fable/suite-618/` and `.codex-report/logs/trim-b1-fable/suite-merged/` (per-module unittest output, `_modules.txt`, `_exits.txt`, `_start.txt`, `_end.txt`)
