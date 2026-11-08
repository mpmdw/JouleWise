ADMIT_WITH_FIXES

## Independent executing review of #701 (head `ed2b2d72b`)

Reviewer: Opus 5.5, as a subagent of the laptop lead. I am not an author of this PR. The review ran on a detached worktree of `ed2b2d72b` on the Air, using synthetic data only. I read no BYTES energy, held-out or stage-2 outcome, withheld store, `/Users/edr/jw-b5-*`, `night-*`, `restricted/` or `night-results/*`.

**Verdict in one line.** The lineage merge preserves both sides, and the stage-1 driver's order and stops are correct. One fallout fix must be replaced before merge: the respelling in `environment_admission.py` hides a real change on the step-4 extractor path from the census. The driver has three small census gaps and one refusal that contradicts §11 item 4. These should be fixed on the run branch before the magistrate runs §3.5–§3.8. None of these findings blocks the stage-1 science.

### What I executed (each module in its own process, `nice -n 10`, `JW_B5_SYNTHETIC_ONLY=1`, Python 3.13)

| Module | Result |
|---|---|
| `tests.test_bytes_stage1` | OK, 10 tests (85 s) |
| `tests.b5_analysis.test_floor_kept_units` **alone** | OK (1 skipped), 78 s |
| `b6.test_audit_record_fixes` | OK |
| `b6.test_bytes_p2_thermal_window` | OK (byte identity: 178 files exact for alpha) |
| `b5_analysis.test_auth_recorder_and_verdict_memo` | OK, 34 tests |
| `independent_recompute.test_comparator_meter`, `test_rc_cmp7`, `test_rc_cmp8`, `test_rc_cmp10`, `test_rc_cmp11` | OK |
| `b6.test_capture_screen_reachability` (9), `b6.test_cold_pass_fixes` (14, 1,974 s), `b6.test_desk_resume_finalize`, `b6.test_loop_round_desk`, `b6.test_survivor_screen` | OK |
| `test_fix573f_restore`, `test_fix573g_restore` | OK |
| `b5_analysis.test_step4_reason_table`, `b5_analysis.test_frozen_files` | OK |
| `test_harvest_b5_window` (RF-3 census tests) | OK, 24 skipped (synthetic-only) |
| `hazards.test_refusal_allowlist` | OK (1 skipped) |
| `scripts/repin.py --check` | PASS, 16 pin families |
| `scripts/gen_state.py --check` | rc 0 |
| Reviewer's adversarial tests on `scripts/bytes_stage1.py` (9, below) | 6 pass, 3 expose gaps |

Not run: `test_bytes_analysis` (CI ran it: 112 tests, 7,507 s). `git merge-tree` of the head with current `main` (`6f0bfd2d6`, which adds one docs commit) is clean.

---

### (a) The census respelling: replace it

The step-4 reason census (`tests/b5_analysis/step4_reasons/make_table.py`) collects every snake_case string literal in the 11 extractor modules. It exists so that "a new extractor code literal cannot fall outside the registered table without this test failing". I ran the generator three times: on `main`, on this head, and on the tree just before `373471bbf`. Head and `main` give identical output. The pre-respelling tree adds exactly two literals: `busy_fraction_admitted` and `compression_records`.

- `compression_records` in `whole_window.py` is a keyword-argument name. Respelling it is cosmetic.
- `busy_fraction_admitted` is **not** cosmetic. It comes with a new function, `environment_admission.busy_fraction_admission_admitted`. Two places change their decision when it returns true:
  - `environment_admission_refusals` no longer adds `environment_admission_failed` when `cpu.admitted` is not true;
  - `whole_window`'s whole-window verdict (around `:8765`) no longer adds `cpu_admission_core_failed`.

  That is an admit decision on the step-4 extractor path, which is exactly what this census is meant to surface. Respelling the key as `"busy" + "_fraction_admitted"` with the comment "outside the sealed B5 code census" removes the one signal the census would have given.

**Is it inert for block 5?** Yes, by provenance. The only writer of `busy_fraction_admitted` is `controller.py:2121` (`_wait_hazard_idle`). It was added on the lane in `a1b2b59c3` (2026-10-14). `git grep` finds no writer of the key on `main`. So no block-5 bundle can carry the key, and both new branches stay unreachable on block-5 data.

**Recommendation: replace the workaround with an honest census update plus a deviation entry.**
1. Restore the plain literals.
2. Regenerate `configs/analysis/b5/step4_reason_classes.json` (generator output plus `RULING`). Both literals land in `tooling`, because neither matches the mask pattern. This changes no mask, no R3 code and no step-4 rule.
3. Record the change in the DLE entry drafted under (b), item 6.

The data-level result is the same. The difference is that the guard records the change instead of being written around it. (Frozen-is-not-sacred applies: fix in place with a citation.)

### (b) The rebind of five frozen Block-5 collection files

I diffed each file against `main`. For the **analysis of already-collected block-5 windows**, each edit is inert:

| File | Edit | Why it is inert for block 5 |
|---|---|---|
| `flags/catalog.py` | 17 block-6 `DRAFT_CODES` and 1 DISCLOSE code (`records.claim_usable_counting_disagreement`) | The sealed block-5 catalog is unchanged. None of the 18 codes has a writer on `main`, so none can occur in a block-5 window. |
| `flags/core.py` | 11 block-6 core codes and `calibration.acceptance_preflight_unverified` | Writers exist only in lane code: the controller's idle wait, the runner's sleep and pause hooks, and `validate_powermetrics_fiducial` in HAZARD mode. `git grep` on `main` finds none of them. |
| `flags/exclusions.py` | Keyword-only `pack_scoped=True` default; `cell.below_minimum` added only if the catalog effect is `EXCLUDE_WINDOW` | The sealed catalog (`configs/campaigns/v5_claim_25g83/flag_catalog.json`) sets `cell.below_minimum` to `EXCLUDE_WINDOW`. Behaviour is identical. |
| `scripts/run_campaign.py` | HAZARD collection hooks: pause marker, run clock and sleep flags, member cap plus wait cap | Collection-time only. Block-5 collection is closed. |
| | `_final_idle_admission_attempt` now accepts any `[1..k]` | The block-5 controller wrote at most `[1, 2]`, and both are still accepted. |
| | Busy-fraction exception in `_idle_admission_core_evaluation` and `_idle_admission_claim_barrier_reasons` | Gated on `busy_fraction_admitted`; no block-5 writer exists (see (a)). |
| | `core_passed` now calls `_idle_admission_claim_barrier_reasons` | Equivalent by inspection: bracket passed, continuity stable, every member admitted, and no conditions. |
| | `OrderEntry.block_id` | See caveat 1 below. |
| `scripts/harvest_b5_window.py` | `StorageStop` exits with code 3 | Reached only from a compressed restore. Block-5 archives are plain. |

Caveats the entry should state:

1. **`block_id` is logged by new collections.** The block-5 contrast order manifests carry `block_id` (for example `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/02_.../order_manifest.json`). A new collection from those configs on post-merge `main` would log `block_id` inside `executed_order` and use it as the HAZARD unit key. This is inert for analysis, but it means "inert" holds for analysis of collected windows, not for re-collecting a block-5 config.
2. **New reads on the block-5 path.** `whole_window`'s merged verdict reads the bundle's `metadata.json` for every non-admitted member before deciding. The decision is the same; only the reads are added.
3. **Merge order.** Same as question 1 of the PR body: tag `b5/analysis-r4` before this merges, or re-run the D-188 comparator at a tag that includes the lineage.

**Draft DLE entry for the lead to sign.** It goes in `docs/analysis/b5/DEVIATION-LOG.md`. The log already uses "DLE-5" for a CARE draft that was not adopted, so the entry says it is this log's own DLE-5.

```markdown
## Signing statement for DLE-5

DLE-5 carries the following statement verbatim, made by the signer at signing:

> The release event has not happened. The lead has seen no Block 5 energy or outcome value. Ed delegated
> preregistration rulings to the lead.

Signer: the block-5 lead (Opus), <date>. Found by code reading and synthetic tests only (PR #701 and its
executing review); no block-5 data was read.

---

## DLE-5. BYTES lineage landing: cited in-place rebind of five frozen collection files and two extractor modules

(This is this log's own DLE-5, not the CARE draft of the same number listed above as not adopted.)

- **Status.** ADOPTED, <date>, with the merge of PR #701 (`lane/2026-11-07-bytes-stage1` into `main`). It changes
  no L9 output (result-equal to r4) on block-5 windows. The analysis pin is unchanged: `b5/analysis-r4` is tagged
  on a commit before this merge. Any later analysis tag that includes this merge is re-run through the D-188
  comparator before release (DLE-1 stages (b) and (c)).
- **Source.** The block-6 and BYTES collection lane (`lane/2026-10-28-bytes-pass2-open` @ `ee4ce93fc`,
  BY-THERM-LINES `4e29114ea`) edited these files in place for block 6. They land on `main` with this merge.
- **Frozen files rebound** (`tests/b5_analysis/test_frozen_files.py`: `EVOLVED_ON_MAIN`, `REBOUND_WORKING_TREE`,
  `FROZEN_FILES_TEST_SHA256`):
  1. `joulewise/flags/catalog.py`: 17 block-6 DRAFT codes and the DISCLOSE code
     `records.claim_usable_counting_disagreement`. The sealed block-5 catalog is unchanged, and no block-5 writer
     emits any of them.
  2. `joulewise/flags/core.py`: 11 block-6 core codes (`agent.pause_marker_stale`, `sleep.*`, `idle.*`) and
     `calibration.acceptance_preflight_unverified`. Their only writers are block-6 lane code; none exists at any
     block-5 window's pinned commit.
  3. `joulewise/flags/exclusions.py`: `compute(..., *, pack_scoped=True)`, which keeps the default behaviour.
     `cell.below_minimum` is now added only when the catalog in force maps it to `EXCLUDE_WINDOW`; the sealed
     block-5 catalog does, so block-5 behaviour is identical.
  4. `scripts/run_campaign.py`: block-6 HAZARD collection hooks (pause marker, run clock and sleep flags, idle-wait
     member cap, `StorageStop` exit 2). On the analysis path:
     - `_final_idle_admission_attempt` accepts consecutive `[1..k]`; the block-5 controller wrote at most `[1, 2]`.
     - The busy-fraction admission exception is gated on `busy_fraction_admitted`. Its only writer is
       `joulewise/controller.py` `_wait_hazard_idle`, added on the lane in `a1b2b59c3` (2026-10-14) and absent from
       `main`, so no block-5 bundle carries it.
     - `core_passed` in the whole-window verdict is rewritten through `_idle_admission_claim_barrier_reasons`; it is
       equivalent on every input that lacks `final_admission_attempt`.
  5. `scripts/harvest_b5_window.py`: `StorageStop` exits with code 3. It is reachable only from a compressed-archive
     restore; block-5 archives are plain.
- **Step-4 extractor modules (not frozen, census-pinned).**
  6. `joulewise/environment_admission.py`: adds `busy_fraction_admission_admitted`, which waives
     `environment_admission_failed` and the core CPU failure for an explicit controller busy-fraction admission.
     It is unreachable on block-5 data for the reason in item 4. The step-4 reason census gains `busy_fraction_admitted`
     and `compression_records` in `tooling` (`configs/analysis/b5/step4_reason_classes.json` regenerated). No mask
     or R3 code changes and the step-4 rule is unchanged.
  7. `joulewise/whole_window.py`: the lane's compressed-archive restore wraps main's `_prepare` body
     (`readable_run` yields a plain directory unchanged). The whole-window verdict now reads a non-admitted member's
     `metadata.json` before deciding; the decision is unchanged on block-5 data.
- **Scope of "inert".** Inert for the analysis of collected block-5 windows. Block-5 collection is closed. A new
  collection from block-5 configs on `main` would differ: `block_id` is logged in `executed_order`, the HAZARD
  idle wait replaces the one retry, and run-clock records are written.
- **Release condition.** None beyond DLE-1, provided `b5/analysis-r4` is tagged before this merge. Otherwise the
  D-188 comparator is re-run at the tag that includes it, and any disagreement is a hold.
```

### (c) RF-3 extension: correct, and harmless in effect

Eight codes are added to `PRE_HARVEST_*`: one core code (`calibration.acceptance_preflight_unverified`) and seven driver codes. I confirmed that `joulewise/b5/driver.py` emits all seven (`:1907`, `:2548`, `:2629`, `:2632`, `:2649`, `:2655`, `:2660`). RF-3's rule is that every pre-harvest writer's code is a candidate. Leaving these out would make a torn `agent.pres…` line under-match, so adding them is correct.

The effect is harmless in both blocks:
- **Block 5.** None of the eight is in the sealed catalog, so `_Catalog.effect` returns `UNCLASSIFIED` and nothing new is excluded. The test also pins that the set of window-excluding candidates is unchanged.
- **Block 6.** `agent.presence` and `agent.presence_overlap` are `EXCLUDE_MEMBER` (Appendix A), so a torn line can raise `records.malformed_flag_member_exclusion_possible`. However, all 15 block-6 pack registrations, including the 12 BYTES sub-packs, map both `records.malformed_flag_*_possible` codes to `DISCLOSE`. So the extension changes only the candidate list in a disclosure and cannot exclude a member.

Registration: the rule is block-5 RF-3 (registration §6.2), and the codes' effects are registered in `flag_catalog_b6.json` and the pack registrations. **Accept.** The two-part spelling of the core code follows this file's existing precedent for candidate-only codes, such as `"records" ".checkout_untracked"`. That case is different from (a): these are flag codes in a table the harvest never emits, not decision keys on the extractor path.

One note for the record: the lane's own harvest, which harvested BYTES, already carried the 11 lane core codes as candidates. The 7 driver codes and the preflight code are new relative to the harvest that ran on BYTES. This does not matter for stage 1, which runs from the run branch, and the effect is disclose-only.

### (d) `scripts/bytes_stage1.py`

| Check | Result |
|---|---|
| Census never reads energies | **Holds.** It parses rows with `csv.DictReader` but inspects only `role`, `config_key`, `model_name` and `run_id`. The census record carries only counts and model names, which the existing test checks. |
| Census never opens the withheld store | **Holds for the plan's layout** (stores under `$LOOP/packs`, outside `$S1/export`; existence is checked by `is_file()` only). **Gap (F2):** the filter `p.parent.name != "withheld"` does not match the registered layout `withheld/<pack_id>/<session>.runs.csv`, where the parent is the pack id. Adversarial A2 put a store in that layout under the export root and removed the visible table. Census then **opened the store** as the session table. |
| Refusals fire | Planted held-out model, `run_start_utc`, missing session and missing store: all fire (existing tests). **Gap (F1):** a held-out row with `config_key = Qwen3-32B…` under a fit `model_name` passes census (A1), because science rows are checked by `model_name` only. **Gap (F3):** a `run_end_utc` column passes (A3), because `CLOCK_COLUMNS` holds one exact name. The exporter's schema has only `run_start_utc` today, so F3 is defence in depth. |
| `run` follows §11's pre-commit order | **Yes.** blinded analysis and twin, then comparer, then both sides with no keys (must refuse), then fit release, then `--stage fit` / twin `--stage 1`, then comparer. The commit stays an operator step. |
| Stops before any key release when a field is above the bar | **Yes.** A5: an above-bar field gives rc 3, `release_fn` is never called, the no-keys stage never runs and there is no `released-keys/`. A6, with the real comparer: analysis exits 0 and twin exits 2, giving rc 2 with no release. A7: either side succeeding without keys gives rc 4 with no release. |
| Release is fit plus NEG-8 only | The existing tests replace the release function, so `_release_fit` was never exercised. I exercised it with real registrations and synthetic key files. A9: it releases exactly `{1.7B, 4B, 8B, neg8_reference}` and the directory holds only those config files, `pack.json` and `release.json`. A8: a manifest relabelling the dense held-out 14B as fit still **passes `validate_manifest`**, but the real release refuses it ("held-out key cannot be released at stage 1") and creates no directory. Defence in depth holds through `b6_release_subset.release`. |
| Registered-digest check | **Holds.** `18582818…0a71` matches `joulewise/bytes_analysis.py` on both the head and the run branch, and appears in §13/§18/§21. The check covers that one file. Its imports were already identical between the run branch and the head except `whole_window.py`, and the one function the estimator uses from it, `neg8_count_adjusted_bound`, is identical in AST. The twin and the comparer (`tests/test_bytes_agreement.py`) are byte-identical between lane and head but are not digest-checked by the driver (LOW; a `git status` dirty bit is recorded instead). |
| **F4: §11 item 4 conflict** | A missing withheld store is added to census `reasons`, and `run` refuses on any census reason (A4: rc 1, "census refused; stage 1 not started"). Registration §11 item 4 says "A missing withheld file is never a refusal … No stage refuses for a missing file". Stage 1 does not read the store. After the plan's fresh export (§3.4) every store should exist, so a missing one indicates an export fault worth stopping for. But as written, the tool can block the 12 Nov commitment on a condition the registration says never refuses. Fix: keep it in the census record as a flag (`withheld_store_present: false` plus a warning list) outside `reasons`, and have `run` record it in `stage1-summary.json` and continue. Alternatively, keep the stop as an operator check and say so in the plan with a lead ruling, as a deviation-log line. |

**Fixes F1–F4 go on `lane/2026-11-07-bytes-stage1-run` (the branch the magistrate runs) and merge forward.** Each is a few lines:
- F1: for science rows, also refuse when `config_key` is not one of the three fit keys of the registered manifest.
- F2: exclude any path with a `withheld` component, relative to the export root.
- F3: refuse any header ending `_utc`, or containing `timestamp` or `clock`.
- F4: as above.

### (e) The 10 conflict resolutions: nothing lost

Method: for each conflicted file I took the lines each side added since the merge base `e9aab7ba1` and checked they appear in `003f6e12a`. Then I listed every file where the head differs from the lane but `main` never touched it, and every file where the head differs from `main` but the lane never touched it.

- Every line reported missing is a documented restructuring that keeps both sides:
  - `cli.py`: `_run_reduce_physics_cache(plain)` inside `readable_run`, where `plain` is the bundle path for plain input.
  - `authentication_io.py`: main's `Path(path).read_bytes()` is kept as the plain branch, with the lane's `.zst` fallback only when no plain file exists.
  - `harvest.py`: main's `harvest_checkout` and `HARVEST_PROGRAM_FILES` kept, plus the lane's `block_six` files.
  - `whole_window.py`: `_prepare_plain` folded into `_prepare`; main's archive-context CPU branch kept inside the busy-fraction loop (equivalent on block-5 inputs, (b) caveat 2).
  - `test_harvest_b5_window.py`: the lane's `skipUnless(JW_B5_SYNTHETIC_ONLY …)` guards are kept under main's names.
  - `hazard_refusals.json`: the `_prepare_plain` entry moved to `_prepare`.
  - `registry.json`: regenerated; `repin --check` passes.
- Files where the head differs from the lane and `main` never touched them: only the documented fallout files and the §1/§18 KB fill.
- Files where the head differs from `main` and the lane never touched them: `CANONICAL.md`, the freeze-by-commit addendum, the rebind tests, and `RESUME.md` (from main's own newer commit).
- The later merges (`08aca7ea3`, `d21de1ffd`, `e275b874e`, `ed2b2d72b`) carry no conflict resolution (`--remerge-diff` is empty).

### Other findings

- **M1 (MEDIUM, impact statement).** Answer (i), "No raw-bundle byte", is true for this PR's own code but not for `main` after merge. The lane's `controller._wait_hazard_idle` replaces the one-retry admission for **every HAZARD window with idle admission enabled**, with no block-6 gate (`waiting = self._hazard is not None and admission.enabled`). It writes `busy_fraction_admitted`, `wait_cap_s`, the wait ledger and the run-clock files, and `run_campaign` adds the pause, sleep and member-cap hooks. Any window launched from post-merge `main` collects differently. Please answer (i) Yes, or state that no further window will be launched from `main` without a ruling, and confirm that the ALIGN and other windows the magistrate arms run from pinned kits.
- **LOW.** `run` does not check that the manifest's `sessions` match the census sessions, or that the manifest's `models` equal the registered §4 block. It relies on `validate_manifest` (W/KV/R are checked against the registered digest) and on the release refusing held-out keys (A8). Adding `manifest["models"] == registered["models"]` to `run_stage1` would close it.
- **LOW.** If `compare_campaign` raises, `run` exits 1 without writing `stage1-summary.json`. A `try/finally` around `finish` would keep the record.
- **NIT.** The plan's §3.1 says 10 tests "under a minute"; here it took 85 s on a loaded Air. The 60 s CI weight is fine.
- `test_floor_kept_units` passes alone here, consistent with the PR's diagnosis (order dependency with `test_claim_replay` under the new packing). The lead still has to choose between a fixture fix and a re-weight.

### Adversarial tests (reviewer's, synthetic; `/private/tmp/jwrev701/test_adv_stage1.py` on the Air)

| Test | What it checks | Result |
|---|---|---|
| A1 | Held-out `config_key` under a fit `model_name` | Census passes it (F1) |
| A2 | Withheld store in the registered layout under the export root | Census opens it (F2) |
| A3 | `run_end_utc` column | Census passes it (F3) |
| A4 | Missing store | `run` exits 1 before stage 1 (F4) |
| A5 | Blinded above-bar field | rc 3, no release |
| A6 | Blinded refusal mismatch (real comparer) | rc 2, no release |
| A7 | Stage 1 succeeding without keys (both sides, or one) | rc 4, no release |
| A8 | Real `_release_fit` with a held-out model relabelled fit | Refused, no directory |
| A9 | Real `_release_fit`, registered manifest | Releases exactly fit + `neg8_reference` |

### Summary for the lead

| Question | Answer |
|---|---|
| (a) | **Replace** the respelling with a census update and a DLE line. It hides an admission-relaxing code path from the guard. The path is inert on block-5 data, but it is a real change on the extractor path. |
| (b) | Inert for analysis of collected block-5 windows. DLE-5 text above, with three caveats. |
| (c) | **Accept.** Correct under RF-3 and registered; disclose-only in effect. |
| (d) | Order, stops and digest hold; real release refuses held-out keys. Fix F1–F4 on the run branch before the magistrate's §3.5. |
| (e) | Nothing lost from either side. |
| Before merge | Fix (a), and address M1 in the impact statement. |
