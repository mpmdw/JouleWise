# Cold final pass (Opus 5.5): b6 MT-20261017T1735Z desk fixes

- Change: `git diff f3ef7804b 0276a3327` (branch `fix/2026-10-17-b6-mt2-fixes`, base `lane/2026-10-16-b6-round2`)
- Worktree: `/Users/edr/code/JouleWise-wt-cold-mt2-opus`, detached at 0276a3327, left unedited
- Scratch: `$TMPDIR/coldopus.9WLM`, where `TMPDIR=/Users/edr/night-archive/b6-mt2-fix/tmp/cold-opus.l4EO`. It holds the base code from `git archive f3ef7804b`, APFS clones of the archive, and every probe script under `probes/`.
- Evidence was read only. Every replay that writes ran on an APFS clone (`cp -Rc`).
- I did not open the other cold pass.

## Verdict: MERGE-WITH-FIXES

All three fixes do what they claim on the real archived inputs. None of my 24 adversarial admission records gets through, at any of the three layers I tested:

- the shared validator (`environment_admission_refusals`);
- the reducer precheck (`current_environment_refusals` / `reduce._environment_claim_reasons`, on the real bundle and its measured window);
- the whole-window core check (the real `validate_whole_window_verdict_row` on a mutated clone).

A run is admitted only in two cases: the explicit controller busy-only shape, and the block-5 clean shape (unchanged). Block-5-shaped records keep their outcome. There is no import cycle, and the diff adds no tolerance or threshold.

The one fix I ask for (F1, MAJOR) is not a regression. The same defect class survives for the other physical skip. A **wait-budget** skip (`idle.wait_budget_skip`) is still called `structure.missing_stage_bundles` and a smoke "fail". The design says waits become skips once the 2-hour session budget is spent, and that the session continues. So a noisy night will reach this case. The change is two lines. Do it before the first full night, in this lane or right after it. Nothing I found produces a wrong number or admits a run that should be excluded.

---

## Findings

### F1: MAJOR. A wait-budget skip is still misclassified as structural and as a smoke stage failure

`recorded_wait_cap_skip` (`joulewise/b6/acceptance.py:29`) accepts a member only if it has `idle.wait_cap_skip` and `skip_reason == "wait_cap_reached"`. The controller (`joulewise/controller.py:2167-2169`) records the same physical event, "no quiet 576-record idle span", in one of two ways:

- as `idle.wait_budget_skip` with `skip_reason="wait_budget_exhausted"`, when the session budget runs out (`next_step` returns `skip_budget`);
- as `idle.wait_cap_skip` with `wait_cap_reached`, when the per-member cap is hit.

Both codes are cataloged `MEMBER_VALIDITY / PHYSICS / EXCLUDE_MEMBER` (`joulewise/flags/catalog.py:356-357`). The design (`docs/design/block6_collection_draft.md:377`) says: "a per-session wait budget of 2 h, after which waits become skips … the session continues". With `SESSION_WAIT_BUDGET_S=7200` and `WAIT_CAP_S=1500`, about five cap-length waits use up the budget. After that, every member that fails its first idle attempt is budget-skipped. So two cases are reachable on a noisy night:

- a whole science stage is budget-skipped while a later member passes on its first attempt;
- a stage mixes cap skips and budget skips (`cap_skipped` needs *every* member to be a cap skip).

`smoke.stages_succeeded` has the same gap, because it also uses `recorded_wait_cap_skip`.

Constructed case D: the real archive, with the decode member's `idle.wait_cap_skip` replaced by `idle.wait_budget_skip` and `skip_reason` set to `wait_budget_exhausted`.

```
cd <worktree> && PYTHONPATH=. /opt/homebrew/bin/python3.13 -B $S/probes/smoke_cases.py $PWD
A real archive (cap-skip decode, rc1)                  structural=False sf=[] stages_ok=True classify=physics
D decode: wait BUDGET skip (physical, cataloged PHYSICS) structural=True sf=['structure.missing_stage_bundles'] stages_ok=False classify=fail
```

The result is a physical loss reported as a desk defect, which holds the loop ("physics refuses; everything else is a flag"). It changes no numbers.

Fix: in `recorded_wait_cap_skip`, accept either pair: (`idle.wait_cap_skip`, `wait_cap_reached`) or (`idle.wait_budget_skip`, `wait_budget_exhausted`). Add one acceptance regression and one `stages_succeeded` regression, including the mixed cap-plus-budget stage.

### F2: MINOR. A whole stage that crashed after capture is no longer structural in session acceptance

The new `absent` test treats a member as absent only if `bundle_present is False` or `raw/powermetrics.plist` is in `files_missing`. Before the fix, any `member.bytes_missing` counted. `REQUIRED_BUNDLE_FILES` (`joulewise/b5/harvest.py:237`) also includes `config.json`, `metadata.json`, `events.jsonl` and `summary_metrics.json`. Take a stage where every member kept its plist but lost, say, `summary_metrics.json` (a kill after capture), with no physical record, while later stages ran. That stage is now not structural.

Constructed case C (decode member: `files_missing=('summary_metrics.json',)`, no cap-skip flag or reason, status failed):

```
fixed: C decode: crash after capture (summary missing, plist present) structural=False sf=[] stages_ok=False classify=fail
       C-nonsmoke same, smoke=False                                   structural=False sf=[] stages_ok=False classify=fail
base:  C ...                                                           structural=True  sf=['structure.missing_stage_bundles'] ... classify=fail
```

This produces no wrong number. The members are still excluded (`member.bytes_missing` and `member.status_not_succeeded` are EXCLUDE_MEMBER), and the smoke still fails because of the stage's exit code. But in a full-night session acceptance, an unexplained whole-stage crash now shows up only as count loss (`cell.below_minimum`). The author's reading, that "the stage left no measurement records" means no plist, is defensible. I would still add a structural or flag code for "every member of a stage failed with no physical record", so a repeated code crash cannot pass night after night as a count shortfall.

### F3: NIT. `busy_fraction_only` accepts `gpu_admitted is None` when the GPU-unknown condition is missing

`joulewise/b6/idle_wait.py:68` uses `cpu_admission.get("gpu_admitted") is not False`. I built an inconsistent record: busy-only conditions, `gpu_admitted=None`, and no `gpu_idle_admission_unknown` condition. It passes the shared validator: `env=() current=() reduce=() core=ADMIT`. The evaluator never writes this shape, because `evaluate_cpu_idle_admission` always adds `CONDITION_GPU_ADMISSION_UNKNOWN` when the GPU result is None (`joulewise/idle_admission.py:442-443`). The whole-window writer also recomputes `cpu_admission` from the records. So this is not reachable from real data. The desk helper could still check `is True`. That would cost nothing, because the evidence-conditions path already refuses GPU-unknown at the desk.

### F4: NIT. The `executing_reviews.json` row still says `commit: "pending"` and `reviewer: "pending"`

`configs/b6/executing_reviews.json` (the new last row) has to be filled in when this lands, or whatever gate reads that file will see an unreviewed number-bearing change.

### Observation: `classify` order changed (no defect)

The new `if acceptance_result.structural: return "fail"` (`joulewise/b6/smoke.py:409`) now runs before the physics check. Before, `stages_ok=True`, structural acceptance and a physical flag gave "physics". Now that case gives "fail". This moves toward failing safe: a structural defect can no longer be laundered as physics. I found no physical path that reaches structural with `stages_ok=True` once F1 is fixed.

---

## Checked and found correct

### Fix 1: the shared admission validator, on the real archive

| run_id | final conditions | busy p95 | power p95 | base refusals | fixed refusals |
|---|---|---|---|---|---|
| d117fq31p7-df-ph-prefill-p2048-abs-r01 | [cpu_busy_ratio_p95_exceeded] | 0.87254 | 0.406085 W | ('environment_admission_failed',) | () |
| neg8-window-end-r1 | [cpu_busy_ratio_p95_exceeded] | 0.8717 | 0.417253 W | ('environment_admission_failed',) | () |

Both have `decision=admitted`, `final.admitted=True` and `busy_fraction_admitted=True`. Source: `probes/replay_admission.py`.

The decode member keeps `('environment_admission_failed',)` in both versions. It is `abort`, `wait_cap_reached`, with conditions busy **and** `processor_combined_power_w_p95_exceeded`, so it is a real physical loss and is correctly still refused.

Reducer precheck, which feeds `member.target_phase_precheck_failed`: `reduce._environment_claim_reasons(metadata, strict=True, bundle_path=<real bundle>, measured_window=BundleReader(...).measured_window())` gives base `('environment_admission_failed',)` and fixed `()`. Source: `probes/adversarial.py`, first row.

Whole-window validator on the archived row (`probes/replay_ww.py`):

- base reasons include `cpu_admission_core_failed` and `environment_admission_failed`;
- fixed reasons include neither.

Both versions keep `calibration_ledger_snapshot_required`, `whole_window_neg8_verdict_failed`, `whole_window_verdict_conflict` and `whole_window_verdict_provenance_invalid`. Those come from the archived row having been written by the base writer with `status: failed`, and from no ledger snapshot being passed. They are not caused by this diff.

### Fix 2 and fix 3: acceptance and smoke classification on the real archive

`probes/replay_desk.py`, which calls `stages_succeeded` directly:

```
FIXED  ACCEPTANCE {"verdict":"EXCLUDE","structural":false,"structural_failures":[],"physics_stop":true}  STAGES_OK True   CLASSIFY physics
BASE   ACCEPTANCE {"verdict":"EXCLUDE","structural":true,"structural_failures":["structure.missing_stage_bundles"],"physics_stop":true}  STAGES_OK False  CLASSIFY fail
```

The decode member now carries `files_missing=('raw/powermetrics.plist',)` and is recognized as a recorded cap skip.

End-to-end through the **production** `smoke.desk` branch (`acceptance=None`, `evidence_loader=None`, so the desk reads `derived/b6-acceptance.json`, gates on `flag_counts` and loads evidence itself). This ran on an APFS clone of the whole smoke dir with paths rewritten. The archived acceptance record was replaced by the record that each version's code computes, standing in for the harvest. Harvest was stubbed to return 0 and pin-advance was a no-op. Source: `probes/desk_e2e.py`.

```
FIXED  STATUS physics  ACC {'verdict': 'EXCLUDE', 'structural': False, 'reasons': ()}
BASE   STATUS fail     ACC {'verdict': 'EXCLUDE', 'structural': True, 'reasons': ('structure.missing_stage_bundles',)}
```

So the desk gate `"idle.wait_cap_skip" in a_result.flags` really fires in production: `flags` is the tuple of `flag_counts` keys, which are codes.

### The opposite error: can the fix admit a run it should exclude? (No)

`probes/adversarial.py` mutates the real prefill admission in memory and runs each record through `environment_admission_refusals`, through `current_environment_refusals` on the real bundle and measured window, through `reduce._environment_claim_reasons`, and through the core predicate `busy_fraction_admission_admitted(final, core_cpu)`. Fixed-code results:

| Constructed record | env / current / reduce | core |
|---|---|---|
| real busy-only, marker, admitted | () | ADMIT |
| busy + power 1.37 W > 1.0 W, marker and admitted forced | environment_admission_failed | core_failed |
| busy + GPU not admitted, marker and admitted forced | environment_admission_failed | core_failed |
| busy + cpu telemetry missing / malformed / samples insufficient / GPU unknown, `reference_provenance_present` False (as the controller sets it) **and** True | environment_admission_failed (all 8) | core_failed |
| marker set, raw CPU result power-only (no busy) | environment_admission_failed | core_failed |
| marker set, final admitted=False, decision abort | environment_admission_failed | core_failed |
| marker set, final admitted=False, decision admitted | environment_admission_failed | core_failed |
| block-5 shape: busy-only, admitted, **no marker** | environment_admission_failed (same as base) | core_failed |
| marker `"true"` (string) / `1` (int) | environment_admission_failed | core_failed |
| busy + an unknown future condition | environment_admission_failed | core_failed |
| `conditions` is a string, not a list | environment_admission_failed | core_failed |
| busy-only, `cpu_admission_enforced` False | cpu_admission_unenforced (still refused) | n/a |
| busy-only, critical environment failed | environment_admission_failed | (env refusal governs) |
| busy-only, decision admitted with `claim_reason` set | environment_admission_failed | (env refusal governs) |
| block-5 clean (CPU admitted, no marker) | () (same as base) | ADMIT |
| busy-only, `gpu_admitted` None with no GPU-unknown condition | () | ADMIT (F3, not reachable) |

The real whole-window validator on a mutated APFS clone of `claim-runs` (`probes/ww_mut.py`):

```
FIXED unmutated                                    core_failed=False env_failed=False
FIXED metadata raw cpu busy+power, marker kept     core_failed=True  env_failed=True
FIXED metadata marker removed (block-5 shape)      core_failed=True  env_failed=True
FIXED core row cpu busy+power, metadata busy-only  core_failed=True  env_failed=False
FIXED core member bundle_id not in manifests       core_failed=True  (fails closed)
BASE  all five                                      core_failed=True  env_failed=True
```

The core check needs **both** the core row's CPU result and the final attempt's raw CPU result (read from the verified source manifest's metadata) to be busy-only, plus the explicit marker and `admitted is True`. It fails closed when the bundle cannot be resolved.

Harvest exclusion: `reduce._environment_claim_reasons` (above) is the function behind the phase precheck. The verdict writer reaches the same validator through `current_environment_refusals`. `scripts/run_campaign.py:7244` already stripped busy only on marker plus admitted at base (`git show f3ef7804b:scripts/run_campaign.py | grep -c busy_fraction_admitted` gives 1), so that path is unchanged. NOT EXECUTED: a full re-reduction and re-harvest of the real bundles (see below).

### The asymmetry: the desk helper omits `evidence_conditions`

The controller calls `busy_fraction_only(cpu, evidence_conditions=_IDLE_ADMISSION_EVIDENCE_CONDITIONS)`, so it admits busy plus missing evidence. In that case it also calls `_hazard_admit_on_missing_evidence(..., ignored_conditions={busy})`, which sets `reference_provenance_present=False`. The desk helper calls `busy_fraction_only(raw_cpu)` with no evidence conditions, so busy plus missing evidence is refused.

Result: **neither** a lost run nor a wrongly admitted one. The desk treats busy plus missing evidence exactly like a plain evidence-only record (A18). Base and fixed both refuse A18 records, independently through `reference_provenance_present` and `cpu.admitted`. Source: `probes/a18.py`.

```
A18 evidence-only, no busy, no marker   ref_prov=False -> ('environment_admission_failed',)  (base: same)
busy + missing telemetry, marker        ref_prov=False -> ('environment_admission_failed',)  (base: same)
busy + missing telemetry, marker        ref_prov=True  -> ('environment_admission_failed',)  (base: same)
```

If the evidence set were passed to the helper, the outcome would still be refusal, because the controller's `reference_provenance_present=False` refuses independently. So the omission changes nothing today and is the stricter choice. Whether A18 runs (CPU quietness not measured) should count at all is an older, separate policy question that this diff does not touch.

### Crash or unexplained missing stage classified "physics"? (No)

`probes/smoke_cases.py`, fixed code. Every case is `classify=fail`:

- B: plist missing with no cap-skip flag or reason;
- B2: flag present but no admission `skip_reason`;
- D2: flag and reason present but bundle absent;
- E: decode stage rc 2 with cap-skip records;
- E2: decode stage rc -9;
- F: a stage with a succeeded member also rc 1;
- F2: the non-collection post-calibration stage rc 1;
- G: rc 1 with no failed member.

B, B2 and D2 are also `structural=True`.

### Full non-reduced pack: does a real cap skip still read as "fail"? (No, for cap skips)

`stages_succeeded` needs the dispatch length to equal the graph's `expected_count`. On the registered full packs, every collection stage matches. `probes/dispatch_full.py` on `d117_floor_qwen3-1p7b_v5`, `d117_floor_qwen3-8b_v5` and `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` showed 30 of 30 stages with `dispatch_n == expected` and no resolver errors. Example: alpha-science-absolute 10/10, abba 20/20, reference-start 3/3. In the reduced archive tree the dispatch is the full order (for example 10) and expected is 1; the registered `smoke_reduction.keep` prefix reconciles them. So a cap-skip stage in a full pack is explained. A budget skip is not (F1).

### Import direction and block 5

- `joulewise/environment_admission.py` now imports `joulewise.b6.idle_wait`, which imports only `joulewise.b6.sleep_guard` (stdlib only). `joulewise/b6/__init__.py` is just a docstring. Importing `environment_admission` loads exactly `['joulewise.b6', 'joulewise.b6.idle_wait', 'joulewise.b6.sleep_guard']`.
- Each of these imported cleanly in a fresh interpreter: environment_admission, b6.idle_wait, whole_window, reduce, floor_extraction, controller, b5.harvest, b6.acceptance, b6.smoke. There is no cycle.
- Block-5 paths that call the validator (`reduce`, `floor_extraction:1867`, `whole_window:5369`, `current_environment_refusals`) change only when the final attempt carries `busy_fraction_admitted is True`. Only `controller._wait_hazard_idle` (the block-6 waiting path, `controller.py:2121`) writes that marker. Block-5-shaped records (no marker) keep their previous refusals; see the table above and the `ww_mut` "marker removed" row.
- `floor_extraction` now also accepts busy-only-admitted baselines. That follows the controller: a busy-only admission does not clear `reference_provenance_present`, and Q3 adopts busy fraction as a disclosure. I saw no new risk there.

### Tolerances and thresholds (checked as their own dimension)

I grepped every added non-test line for numeric literals (`git diff f3ef7804b 0276a3327 -- joulewise/ | grep '^+' | grep -E '[0-9]'`). The only numbers are campaign exit codes (`rc != 1`, `harvest_exit in (0, 6)`) and list indexing (`attempts[-1]`). Those are integer process codes, where exact equality is right. The diff adds no tolerance or threshold and changes no estimator. The 1.0 W power limit and the busy-ratio limit are untouched: power over the limit still refuses, as the "busy + power 1.37 W" row shows. One piece of context, not a finding: the admitted runs had CPU busy p95 of about 0.87 at about 0.41 W. That is inside the 0.17 to 0.42 W range the council's Q3 cites.

---

## What I ran

Here `$S` = `$TMPDIR/coldopus.9WLM`; base code is in `$S/base` (`git archive f3ef7804b | tar -x -C $S/base`); fixed code is the worktree. Every probe ran with `/opt/homebrew/bin/python3.13 -B` and `PYTHONPATH=.` from the code root of the version under test.

1. **Changed tests:** `TMPDIR=$(mktemp -d) JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.test_environment_admission tests.test_whole_window tests.test_hazard_whole_window_verdict tests.test_harvest_b5_p3harv tests.hazards.test_refusal_allowlist` gave `Ran 125 tests in 60.986s  OK`.
2. **b6 suite**, run as modules instead of `discover` to stay inside the foreground time limit. These are all 24 `tests/b6/test_*.py` modules except the four slow round modules: `TMPDIR=$(mktemp -d) JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest <24 modules>` gave `Ran 218 tests  FAILED (failures=8)`.
   - All 8 failures are in `test_b6_plan_render` (6 subtests) and `test_lane_adapters` (2). Each one is `/private/var/folders/...` != `/var/folders/...`: `mktemp -d` returned a path under the `/var` symlink. Neither module is touched by the diff.
   - Rerun with a non-symlinked TMPDIR: `TMPDIR=$S/tmp2 JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest tests.b6.test_b6_plan_render tests.b6.test_lane_adapters tests.b6.test_acceptance tests.b6.test_smoke` gave `Ran 83 tests  OK`.
3. **Slow round and desk methods**, batch 1 (`TMPDIR=$S/tmp2 JW_B5_SYNTHETIC_ONLY=1`): `test_loop_round_desk.RoundTests.test_alpha_smoke_session_desk_and_beta_rotation`, `…test_physics_refusal_wait_reprepare_then_retry`, `test_capture_screen_reachability.ChainReachabilityTests.test_opening_150ms_stops_at_13_and_full_pack_outcome_is_physics` gave `Ran 3 tests in 133.599s  OK`.
4. **Slow round methods, batch 2** (8 methods; outcome under "NOT EXECUTED / partial" below).
5. `probes/replay_admission.py`: real-archive admission refusals, fixed vs base.
6. `probes/replay_desk.py`: real-archive acceptance, `stages_succeeded` and `classify`, fixed vs base.
7. `probes/replay_ww.py`: real `validate_whole_window_verdict_row` on the archived row, fixed vs base.
8. `probes/adversarial.py`: 24 constructed admission records, run through validator, current, reduce and the core predicate, fixed vs base.
9. `probes/ww_mut.py`: real whole-window validator on 5 mutations of an APFS clone of `claim-runs`, fixed vs base.
10. `probes/a18.py`: the evidence-conditions asymmetry against the A18 baseline, fixed vs base.
11. `probes/smoke_cases.py`: 12 constructed acceptance and smoke cases (A–G), fixed vs base.
12. `probes/dispatch.py` and `probes/dispatch_full.py`: dispatch length vs `expected_count` for the reduced archive tree and three registered full packs.
13. `probes/desk_e2e.py`: production `smoke.desk` branch end to end on an APFS clone of the smoke dir, fixed vs base.
14. Import checks: a fresh-interpreter import of each of the 9 modules, plus the `sys.modules` b6 set after importing `environment_admission`.
15. Numeric-literal grep of the added non-test lines.
16. Code reading: `controller._wait_hazard_idle` (lines 2044-2180), `_hazard_admit_on_missing_evidence`, `evaluate_cpu_idle_admission`, `environment_admission_refusals`, `current_environment_refusals`, the `reduce` precheck callers, the `floor_extraction` caller, `run_campaign.py:7225-7265`, acceptance `evaluate` (structural and flags), `smoke.desk` and `classify`, `desk_lane.evaluate_smoke`, harvest `member.bytes_missing` producers, `REQUIRED_BUNDLE_FILES`, the catalog entries for `idle.*`, and the design line on the wait budget.

## NOT EXECUTED / partial

- `unittest discover -s tests/b6 -t .` as one command. I replaced it with items 2–4, because a single foreground call is capped at 10 minutes and the author's own record puts the 18 slow methods at 2,388 s. These remaining slow methods were not run by me: `test_cold_pass_fixes.FullRoundTests.test_exit4_and_acceptance_unavailable_reharvest_into_new_archive`, `…test_lost_start_reference_without_spare_counts`, and `test_desk_resume_finalize` (`test_block5_recovery_retains_systematic_invalid_pre_abort`, `test_failed_resume_with_lineage_writes_slot_flag_to_custody`, `test_resume_commits_then_times_out_is_finalized_without_failure_flag`, `test_unfinalized_post_40ms_finalizes_valid_and_keeps_window_stop`, `test_unfinalized_pre_40ms_keeps_physical_abort`). Batch 2's outcome is recorded in the addendum below.
- A full re-reduction (`reduce.py`), campaign verdict writer and `harvest_b6 --smoke` on the real bundles with the fixed code. I replayed each deciding function on the real inputs instead (reducer precheck function, shared validator, whole-window validator, acceptance, desk). A newly written verdict row and summary prechecks were not produced.
- Whether a used spare-retry member could make `len(stage.members) != len(run_ids)` in `stages_succeeded` for a full pack. All three registered science packs have no spares in their collection stages (dispatch = expected), so I did not build a spare case.

## Addendum: slow-method batch 2

Command: `TMPDIR=$S/tmp2 JW_B5_SYNTHETIC_ONLY=1 python3.13 -B -m unittest` on these 8 methods: `test_capture_screen_reachability…test_opening_40ms_reaches_real_screen_and_desk`, `test_cold_pass_fixes.FullRoundTests.{test_completed_full_alpha, test_physical_and_opening_no_bound_stops_rotate, test_gamma_lost_midpoint_counts_and_overrides_b5_claim}`, `test_loop_round_desk.RoundTests.{test_lost_session_reaches_desk_and_holds_before_beta, test_resume_after_hold_continues_real_round, test_stops_close_bracket_advance_pin_and_reach_next_smoke}`, `test_desk_resume_finalize…test_bare_named_and_unmapped_exits_abort_by_table`.

Outcome: **NOT EXECUTED (no result).** The harness stopped the run at its background time limit, about 20 minutes in, before unittest printed a summary. The output file holds only `[killed]`, so I do not know whether any of these 8 methods passed or failed. The author's report (V3) claims all 18 slow methods pass. Of those, I confirmed only the 3 in batch 1 (OK). The other 15 slow methods are unverified by me. This does not change the verdict: none of these methods covers F1, the budget-skip case.
