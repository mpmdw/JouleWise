# Cold final pass (Fable) on fix/2026-10-17-b6-mt2-fixes (0276a3327 vs base f3ef7804b)

Reviewer: Claude Fable 5.1, single non-interactive session, blind to the other cold pass.
Worktree: /Users/edr/code/JouleWise-wt-cold-mt2-fable (detached at 0276a3327, not edited).
Base copy for side-by-side replays: `git archive f3ef7804b joulewise scripts configs | tar -x -C /tmp/cold-fable/base`.
Scratch: /tmp/cold-fable (probe scripts, an APFS clone of the archived claim-runs for the whole-window probe).
Evidence read only: /Users/edr/night-b6/machine-test/MT-20261017T1735Z/.

## Verdict: MERGE-WITH-FIXES

The three desk fixes are correct on the real archived inputs and survive every opposite-error construction I could
build: no production-shaped record that fails power, GPU, or evidence is admitted; block-5-shaped records keep their
exact previous outcomes; no import cycle; the diff adds no threshold or tolerance. One MAJOR defect remains in the lane
outside the diff's four files: the whole-window verdict writer in scripts/run_campaign.py still carries the block-5
raw-CPU veto, so a clean real window containing one busy-only member is still written with status "failed". The
catalog makes that disclose-only, so it is a wrong label rather than a lost run, but it contradicts council Q3 and
the very validator this diff fixes. Fix it in the same lane before the live gate.

## Findings

### F1 MAJOR: verdict writer still vetoes busy-only members (scripts/run_campaign.py:9047-9054, unchanged by the diff)

`_idle_admission_claim_barrier_reasons(core)` maps any member whose stored raw `cpu_admission.decision != "admitted"`
to `cpu_admission_core_failed`. The writer at 10212 turns a non-empty reasons list into `whole_status = "failed"`
(production profile) and writes it as the row's `status`; at 11610 the same list sets `core_blocks_claim` and
`campaign_failed` (the producer's exit 1 seen in `withheld/desk-verdict-run.json`). The writer deliberately
preserves the raw failed CPU result for busy-only members (7236-7246 strip the busy condition from member failures
but leave `cpu_admission` as the evaluator wrote it), so this veto fires on every busy-only member.

Command (file-based so PYTHONPATH selects the tree; `/tmp/cold-fable/probe_writer.py`):
```
PYTHONPATH=. python3.13 -B /tmp/cold-fable/probe_writer.py .
module: /Users/edr/code/JouleWise-wt-cold-mt2-fable/scripts/run_campaign.py
archived core conditions: ['environment_admission_failed', 'neg8_drift_bound_underived', 'neg8_idle_sub_drift_bound_underived', 'whole_window_bundle_invalid']
barrier reasons on ARCHIVED core: ['cpu_admission_core_failed', 'environment_admission_failed', 'whole_window_neg8_verdict_failed']
barrier reasons on CLEAN core with busy-only members: ['cpu_admission_core_failed']
writer whole_status would be: failed (production profile)
control (raw cpu admitted): []
```
"CLEAN core" = the archived core with conditions emptied, bracket decision "passed", continuity "stable"; its only
irregularity is the two busy-only members (prefill, end reference). Base tree gives the identical output.

Consequence in a real window: row status "failed"; harvest emits `whole_window.not_passed` (catalog: NUMBER,
DISCLOSE) on every window with a busy-only member; the fixed validator returns `whole_window_neg8_verdict_failed`
because `row.status != "passed"` (whole_window.py:6758); the NEG-8 screen itself reads the bracket decision, not the
status, so the window still counts. No wrong number, no lost run; a wrong verdict label and a non-zero producer exit
on physically sound windows. Fix: in `_idle_admission_claim_barrier_reasons`, accept a member whose stored cpu passes
`busy_fraction_admission_admitted(final, cpu)` with `final` read from the member's metadata (the writer has it at
7239-7243); add a writer test asserting `whole_status == "passed"` for a clean core with a busy-only member. The added
test `test_writer_preserves_raw_cpu_and_does_not_name_busy_only_member` does not exercise this function (grep of the
test diff for `_idle_admission_claim_barrier_reasons|apply_idle_admission_claim_barrier|whole_status`: 0 hits).

### F2 MINOR: the "absent stage" predicate is narrowed beyond the cap-skip case (joulewise/b6/acceptance.py:191-193)

Base: a stage is absent when every member is `bundle_present False` or carries any `member.bytes_missing`.
Fixed: absent only when every member is `bundle_present False` or is missing `raw/powermetrics.plist`. The cap-skip
exemption needed only `and not recorded_wait_cap_skip(m)`; the rewrite also stops treating a stage whose members all
lost `summary_metrics.json` (plist present) as structural. REQUIRED_BUNDLE_FILES (harvest.py:237) lists five files,
so four of them can now vanish from every member of a stage without `structure.missing_stage_bundles`.

Construction (`/tmp/cold-fable/probe_smoke.py`, real archive, cap member rewritten as "no cap record, files_missing =
summary_metrics.json", stage rc forced to 0):
```
stage rc 0 but all members missing summary, no cap record    stages_succeeded=True  structural=False [] classify=physics
stage rc 0, plist missing, no cap record                      stages_succeeded=True  structural=True  ['structure.missing_stage_bundles'] classify=fail
```
Base code on the first case would have been structural (any bytes missing). With the campaign's own rc 1 the smoke
still fails through the stage-exit path (shown below), so the exposure is a post-hoc loss after a clean exit, e.g. the
10-12 iCloud eviction fault. The members are still excluded individually (`member.bytes_missing`, EXCLUDE_MEMBER) and
the window reads EXCLUDE through `cell.below_minimum`, so no number is wrong; the loop loses the structural hold.
Suggested predicate: `bundle_present is False or ("member.bytes_missing" in m.flags and not recorded_wait_cap_skip(m))`.

### F3 NIT: desk helper calls busy_fraction_only without the controller's evidence-conditions set

Controller (controller.py:2116) admits `{busy} ∪ evidence conditions`; the desk helper admits exactly `{busy}`.
Decision: the asymmetry neither loses a countable run nor admits one that should be excluded. A run admitted with
busy plus an evidence condition goes through A18 (`_hazard_admit_on_missing_evidence`), which sets
`reference_provenance_present = False`, and `environment_admission_refusals` refuses that independently
(environment_admission.py:491). Constructed case, fixed tree:
```
busy + samples insufficient                                   refusals=('environment_admission_failed',)  helper=False
busy + samples insufficient + A18 ref_provenance False        refusals=('environment_admission_failed',)  helper=False
```
Base gives the same. If A18 runs ever become claim-eligible, the helper must take the evidence set; today the
stricter helper is redundant, not harmful.

### F4 NIT: the validator trusts the conditions list, not the printed watt number (same trust model as base)

A record whose `processor_combined_power_w_p95` is 1.4 W but whose `conditions` still says busy-only is admitted by
the fixed validator; base admitted the same record whenever its `admitted` boolean said so, so this is not a
regression. The whole-window replay re-derives `cpu_admission` from `rich_telemetry_idle.jsonl` and refuses on
`dict(stored_cpu) != cpu` (whole_window.py:5400), which catches a stored/derived mismatch. No action.

### F5 NIT: smoke desk needs the acceptance loader to reach the cap explanation (smoke.py:493)

`stages_succeeded` runs only when `_harvest_hooks()` finds `joulewise.b6.acceptance`; otherwise a cap-skip stage still
reads "fail". Fail-closed and acceptable; noting it so a missing-module smoke "fail" is not misread as a cap defect.

### F6 NIT: configs/b6/executing_reviews.json row has commit "pending" and reviewer "pending"

Lead fills it at re-pin; tests.b6.test_code_check passes with the placeholder.

## Claims checked and confirmed

Real-archive replay, base vs fixed (`/tmp/cold-fable/replay_env.py`, `replay_acc.py`, `replay_ww.py`; module path
printed by each run confirms the tree):
```
BASE  environment_admission_refusals  prefill-p2048-abs-r01 ('environment_admission_failed',)  neg8-window-end-r1 ('environment_admission_failed',)  neg8-window-start-r1 ()  decode-abs-r01 ('environment_admission_failed',)
FIXED environment_admission_refusals  prefill-p2048-abs-r01 ()                                 neg8-window-end-r1 ()                                 neg8-window-start-r1 ()  decode-abs-r01 ('environment_admission_failed',)
BASE  reduce._environment_claim_reasons (strict, real bundle + measured window): prefill ['environment_admission_failed'], end ['environment_admission_failed'], start []; gross_request eligible False
FIXED reduce._environment_claim_reasons: prefill [], end [], start []; gross_request eligible True; constructed busy+power>1W: ['environment_admission_failed']
BASE  ACCEPTANCE structural=true  ['structure.missing_stage_bundles']  stages_ok(rc)=False  CLASSIFY fail
FIXED ACCEPTANCE structural=false []  stages_succeeded=True  CLASSIFY physics
BASE  validate_whole_window_verdict_row reasons: calibration_ledger_snapshot_required, cpu_admission_core_failed, environment_admission_failed, whole_window_neg8_verdict_failed, whole_window_verdict_conflict, whole_window_verdict_provenance_invalid
FIXED validate_whole_window_verdict_row reasons: calibration_ledger_snapshot_required, whole_window_neg8_verdict_failed, whole_window_verdict_conflict, whole_window_verdict_provenance_invalid
```
The decode member (cap-skipped, `skip_reason wait_cap_reached`, `files_missing ['raw/powermetrics.plist']`) stays
refused in both trees: correct, it has no measurement.

Opposite-error table through `environment_admission_refusals` (prefill record as template, `/tmp/cold-fable/probe_env.py`
on the fixed tree, `probe_env_base.py` on the base tree; "helper" = `busy_fraction_admission_admitted(final)`):
```
case                                                           FIXED refusals                        helper   BASE refusals
REAL prefill (busy only, 0.406 W, marker)                      ()                                    True     ('environment_admission_failed',)
busy + power>1.0W (1.4 W, condition added)                     ('environment_admission_failed',)     False    same
busy + gpu not admitted                                        ('environment_admission_failed',)     False    same
busy + gpu_admitted None with unknown condition                ('environment_admission_failed',)     False    same
busy + telemetry missing / malformed / samples insufficient    ('environment_admission_failed',) x3  False    same
marker set, final admitted=False                               ('environment_admission_failed',)     False    same
marker set, final admitted=False, decision abort + claim_reason('environment_admission_failed',)     False    same
marker set, cpu conditions [] but cpu.admitted False           ('environment_admission_failed',)     False    same
marker set, cpu conditions None                                ('environment_admission_failed',)     False    same
marker 'true' as string                                        ('environment_admission_failed',)     False    same
marker on attempt 1 of 2, final attempt unmarked and failed    ('..._failed', '..._missing')          False    same
BLOCK-5: no marker, final admitted False, decision abort       ('environment_admission_failed',)     False    same
BLOCK-5: no marker, final admitted True (inconsistent)         ('environment_admission_failed',)     False    same
BLOCK-5 clean: no marker, cpu admitted, no conditions          ()                                    False    ()
cpu_admission_enforced False + marker                          ('cpu_admission_unenforced',)         True     ('cpu_admission_unenforced', 'environment_admission_failed')
marker + critical_environment_passed False                     ('environment_admission_failed',)     True     same
marker + evaluation eligible False                             ('environment_admission_failed',)     True     same
```
Every block-5-shaped row is identical between trees. The only rows that change are genuine explicit busy-only
admissions (and the unenforced row, which still refuses on `cpu_admission_unenforced`).

Whole-window core check end to end (`/tmp/cold-fable/probe_wwcore.py` on an APFS clone `cp -Rc` of claim-runs, 1.3 G,
mutating the prefill metadata or the stored row member):
```
baseline (scratch copy of real archive)                core_failed=False
metadata: marker removed                               core_failed=True  (+environment_admission_failed)
metadata: final admitted=False                         core_failed=True  (+environment_admission_failed)
metadata: cpu conditions += power exceeded             core_failed=True  (+environment_admission_failed)
row: stored member cpu conditions += power exceeded    core_failed=True
row: stored member cpu gpu_admitted False              core_failed=True
row: stored member cpu conditions += samples insuff.   core_failed=True
metadata.json missing for prefill                      core_failed=True  (+environment_admission_missing)
```

Smoke stage classification (`/tmp/cold-fable/probe_smoke.py`, `probe_full.py`; real reduced tree and a synthetic
full tree with the 10-member manifest from `plan.resolve_stage_dispatches`):
```
REAL: cap stage rc 1, recorded cap skip                        stages_succeeded=True   structural=False  classify=physics
crash: cap stage rc 2 / rc 137                                 False  False  fail
unexplained: cap stage rc None (journal row missing)           False  False  fail
rc 1 but member lacks idle.wait_cap_skip                       False  True ['structure.missing_stage_bundles']  fail
rc 1 but admission skip_reason absent / 'skip_budget'          False  True  fail
rc 1 but member status 'succeeded' (contradiction)             False  False  fail
rc 1 on prefill stage whose member succeeded                   False  False  fail
cap member bundle_present False                                False  True  fail
FULL pack: 1 cap-skipped + 9 succeeded, rc 1                   stages_succeeded=True
FULL pack: all 10 cap-skipped, rc 1                            stages_succeeded=True
FULL pack: 1 cap-skipped + 1 failed without cap + 8 ok         False
FULL pack: only 9 of 10 members recorded                       False
FULL pack: 10 present, one run_id not in manifest              False
FULL acceptance: all 10 cap-skipped                            structural=False  verdict=EXCLUDE counting=False
FULL acceptance: 9 cap-skipped + 1 bundle absent               structural=True ['structure.missing_stage_bundles']
FULL acceptance: 10 cap-skipped, only 9 recorded               structural=True ['structure.missing_stage_bundles']
```
A crash or an unexplained missing stage cannot reach "physics": `classify` returns before the physics branch whenever
`stages_ok` is false, and `stages_succeeded` requires rc exactly 1, an exact dispatch match, and every non-succeeded
member to be a recorded cap skip. A real cap-skip stage in a full pack is not called "fail": the prefix rule applies
only when `smoke_reduction.keep[stage] == expected_count`, so a full manifest is compared whole. The `cap_skipped`
structural exemption requires the full expected count, so a partially vanished stage stays structural. A full stage
loss to cap skips still fails to count through `cell.below_minimum` (verdict EXCLUDE above), so the survivor minimum
is not waived.

Import direction: `environment_admission -> b6.idle_wait -> b6.sleep_guard` (stdlib only). Fresh imports of
`joulewise.environment_admission`, `joulewise.b6.idle_wait`, `joulewise.whole_window`, `joulewise.controller` all
succeed; `joulewise/b6/__init__.py` is a docstring. Block-5 callers that now import idle_wait transitively
(floor_extraction, reduce, v5_qualification) see identical outputs on block-5 shapes (table above).

Numbers: the diff adds no threshold, tolerance, or estimator. Its comparisons are integer counts (`len(run_ids) ==
expected`, `len(stage.members) == stage.expected_count`), exact code strings, and exact run-id sets, all of which
exact equality is right for. The 0.5 busy fraction and 1.0 W stay inside the evaluator, untouched.

## What I ran

1. `TMPDIR=$(mktemp -d) JW_B5_SYNTHETIC_ONLY=1 /opt/homebrew/bin/python3.13 -B -m unittest tests.test_environment_admission tests.test_whole_window tests.test_hazard_whole_window_verdict tests.test_harvest_b5_p3harv tests.hazards.test_refusal_allowlist` -> Ran 125 tests in 59.853s, OK.
2. `... -m unittest tests.b6.test_acceptance tests.b6.test_smoke` -> Ran 59 tests in 45.109s, OK.
3. `... -m unittest` over the 22 other fast tests/b6 modules -> Ran 159 tests, FAILED (failures=8); all 8 are `/private/var/...` vs `/var/...` path assertions in test_b6_plan_render and test_lane_adapters (files untouched by the diff). Re-run of those two modules with `TMPDIR` set to the realpath -> Ran 24 tests, OK. Artefact of a symlinked TMPDIR, not the diff.
4. Fresh-interpreter import probes for the four modules above (cycle check).
5. `/tmp/cold-fable/replay_env.py` base and fixed (admission validator on the four archived records, lenient and strict timing).
6. `/tmp/cold-fable/replay_acc.py` base and fixed (evidence_from_archive, ACCEPTANCE.evaluate, stages_succeeded, classify on the real archive).
7. `/tmp/cold-fable/replay_ww.py` base and fixed (validate_whole_window_verdict_row on the archived row).
8. `/tmp/cold-fable/probe_reduce.py` base and fixed (reduce._environment_claim_reasons and _apply_environment_claim_barrier on the real bundles with their measured windows, plus a busy+power construction).
9. `/tmp/cold-fable/probe_env.py` (fixed) and `probe_env_base.py` (base): 22 constructed admission records. My first base run of this table used a stdin heredoc, which let the worktree package shadow PYTHONPATH; it was discarded and re-run as a file.
10. `/tmp/cold-fable/probe_wwcore.py`: whole-window core check on an APFS clone with eight metadata/row mutations.
11. `/tmp/cold-fable/probe_smoke.py` and `probe_full.py`: fifteen reduced-tree and nine full-tree stage/acceptance constructions.
12. `/tmp/cold-fable/probe_writer.py` base and fixed: run_campaign._idle_admission_claim_barrier_reasons on the archived core, a clean busy-only core, and a raw-admitted control.
13. `git diff --stat f3ef7804b 0276a3327`; confirmed idle_wait.py, b5/harvest.py, reduce.py, scripts/run_campaign.py unchanged by the diff.

## NOT EXECUTED

- tests/b6 slow round modules: test_capture_screen_reachability, test_cold_pass_fixes, test_desk_resume_finalize, test_loop_round_desk (author's V3: 18 methods, 2388 s, OK). They exceed the single-foreground-call limit and the 60-minute budget; nothing in them touches the four changed modules' new branches beyond what tests 1 and 2 cover.
- The full re-reduction replay of the archive (regenerated summaries, member assessments, verdict) described in ROOT-CAUSE.md; the deciding functions were replayed instead (items 5 to 8).
- Whole repository suite; live collection; the harvest's `_precheck_flags` on regenerated summaries (the stored summaries still embed the old refusal, so that replay needs the re-reduction above).
