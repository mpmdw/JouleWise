```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "BLOCKERS FOUND: contaminated references can retain claim influence, while missing records and failed probes can suppress entire windows; report persistence and child-process cleanup remain runner actions.",
  "workspace": {
    "base_requested": "a434e363d96621318657418e60b8d14410079d82",
    "base_mode": "exact",
    "head_start": "a434e363d96621318657418e60b8d14410079d82",
    "head_end": "a434e363d96621318657418e60b8d14410079d82",
    "upstream_end": "a434e363d96621318657418e60b8d14410079d82",
    "branch": "integrate/2026-10-06-gate-prune-4"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "seat": "astra",
    "arming": "BLOCKERS FOUND",
    "findings": [
      {"id":"A1","severity":"blocker","task_severity":"BLOCKER","evidence":"EXECUTED","title":"Excluded NEG-8 references retain influence over claim uncertainty"},
      {"id":"A2","severity":"blocker","task_severity":"BLOCKER","evidence":"EXECUTED","title":"Missing chain.started suppresses a populated window"},
      {"id":"A3","severity":"blocker","task_severity":"BLOCKER","evidence":"EXECUTED","title":"Unmeasured hazard probes refuse collection"},
      {"id":"A4","severity":"blocker","task_severity":"BLOCKER","evidence":"EXECUTED","title":"Missing contention journal excludes every member"},
      {"id":"A5","severity":"should_fix","task_severity":"MAJOR","evidence":"EXECUTED","title":"Missing hazard locator restores legacy collection refusal"},
      {"id":"A6","severity":"should_fix","task_severity":"MAJOR","evidence":"EXECUTED","title":"Missing desk identity JSON aborts bracket reservation"},
      {"id":"A7","severity":"nit","task_severity":"MINOR","evidence":"READ","title":"Claim issuance reads evidence_class from the wrong location"}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"test",
      "cmd":"TMPDIR=/private/tmp/audit-astra.cw3cOH PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_audit_powermetrics_parser tests.test_audit_reduce_degenerate tests.test_harvest_b5_p3harv.SmcBatteryRuleTests tests.test_harvest_b5_window.ExclusionSeamTests tests.test_gate_prune_integration.PlanThresholdsReachTheRealArm.test_refusals_and_unmeasured_reads_reach_the_driver_as_no_go",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V2","kind":"test",
      "cmd":"TMPDIR=/private/tmp/audit-astra.cw3cOH PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_window.ReadinessAndNullTests tests.test_harvest_b5_window.WholeWindowMemberFailureTests tests.test_harvest_b5_window.CollectedWindowTests.test_flipped_raw_plist_byte_is_a_member_exclusion_not_a_fault",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V3","kind":"test",
      "cmd":"TMPDIR=/private/tmp/audit-astra.cw3cOH PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_issued_allowance_projection_uses_exact_decimal_authority tests.test_calibration_bracketing.CalibrationBracketingTests.test_attempted_operatives_poisoning_does_not_accept_crosswire tests.test_calibration_bracketing.CalibrationBracketingTests.test_exact_session_binding_selects_reserved_pair_not_neighbors tests.test_magistrate_watchdog_yield.DriverRecordsToWatchdogTests tests.test_harvest_b5_window.IdentityReplayTests.test_executed_inventory_without_a_head_is_identity_unmeasured tests.test_harvest_b5_window.CollectedWindowTests.test_derived_outputs_carry_no_energy_and_no_span_edges",
      "cwd":".",
      "observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=3)"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V4","kind":"test",
      "cmd":"TMPDIR=/private/tmp/audit-astra.cw3cOH PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3.13 -m unittest tests.test_uncertainty_evidence tests.test_powermetrics_fiducial.DetectorTests tests.test_results_fill_adapter.ResultsFillAdapterTests",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V5","kind":"inspection",
      "cmd":"git rev-parse HEAD && git status --short --branch && git rev-parse @{upstream}",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["a434e363d96621318657418e60b8d14410079d82","## integrate/2026-10-06-gate-prune-4...origin/integrate/2026-10-06-gate-prune-4","a434e363d96621318657418e60b8d14410079d82"]},
      "expected":{"exit_code":0,"tail_regex":"a434e363d96621318657418e60b8d14410079d82"}
    }
  ],
  "flags": [
    {
      "id":"F1","kind":"environment","level":"blocking",
      "text":"The requested report directory is outside this session's writable sandbox. No REPORT.md was written and no repository files were modified.",
      "needs":"Runner must persist this report to /Users/edr/night-archive/gate-prune/triple-audit/astra/REPORT.md."
    },
    {
      "id":"F2","kind":"verification_gap","level":"blocking",
      "text":"Three watchdog tests failed amid sandbox denials of process inspection and termination. ResourceWarnings named child PIDs 2546, 2658 and 2755; termination attempts were denied and cleanup could not be verified.",
      "needs":"Runner must verify cleanup using process identities before any quiet measurement and rerun the three watchdog tests in an environment permitting their normal process lifecycle."
    }
  ]
}
```

## Findings

**Verdict: BLOCKERS FOUND.** Seat: **astra**. The audited head remained exactly `a434e363d96621318657418e60b8d14410079d82`; the working tree remained clean.

| ID | Severity | Evidence | Finding and primary location |
|---|---|---|---|
| A1 | BLOCKER | EXECUTED | Excluded NEG-8 references retain claim influence — [harvest.py:1453](/Users/edr/code/JouleWise-wt-int4/joulewise/b5/harvest.py:1453) |
| A2 | BLOCKER | EXECUTED | Missing launch marker suppresses a populated window — [harvest.py:6686](/Users/edr/code/JouleWise-wt-int4/joulewise/b5/harvest.py:6686) |
| A3 | BLOCKER | EXECUTED | Failed probes become collection refusals — [driver.py:767](/Users/edr/code/JouleWise-wt-int4/joulewise/b5/driver.py:767) |
| A4 | BLOCKER | EXECUTED | Missing contention journal excludes every member — [harvest.py:5186](/Users/edr/code/JouleWise-wt-int4/joulewise/b5/harvest.py:5186) |
| A5 | MAJOR | EXECUTED | Lost hazard locator restores legacy refusal — [window_lineage.py:349](/Users/edr/code/JouleWise-wt-int4/joulewise/window_lineage.py:349) |
| A6 | MAJOR | EXECUTED | Missing desk identity file aborts reservation — [reserve_calibration_window_bracket.py:309](/Users/edr/code/JouleWise-wt-int4/scripts/reserve_calibration_window_bracket.py:309) |
| A7 | MINOR | READ | Issuance reads the wrong schema location — [paper_custody.py:632](/Users/edr/code/JouleWise-wt-int4/joulewise/paper_custody.py:632) |

**A1 — Physics exclusions do not propagate through auxiliary dependencies.**

- **Trigger:** Measured external CPU contention overlaps `neg8-window-start-r1`. Its bundle otherwise satisfies the reference checks.
- **Wrong output:** The real ALPHA roster classifies this reference as auxiliary with no cell dependencies. A probe through `contention_member_flags`, `FlagLedger`, and `exclusions.compute` produced:

  ```
  members_excluded: neg8-window-start-r1 / contention.request_overlap
  claim_usable: True
  reasons: []
  ```

  NEG-8 assessment runs before monitor joins at [harvest.py:6714](/Users/edr/code/JouleWise-wt-int4/joulewise/b5/harvest.py:6714). The later exclusion neither invalidates nor recomputes the reference-derived allowance.

  A concrete numeric probe supplied start references `[130, 100, 100]` J, midpoint/end means `110` J, and a repeatability bound of `1` J. `_family_drift_record` returned `point_delta_j=0`, `screen_passed=True`, and `drift_allowance_j=1`. If the first reference contains 30 J of external-work contamination, the uncontaminated start mean is 100 J: the actual endpoint difference is 10 J and the screen should fail. Claim input construction consumes that retained allowance at [inputs.py:4031](/Users/edr/code/JouleWise-wt-int4/joulewise/analysis_engine/inputs.py:4031).
- **Minimal fix:** Apply physics exclusions before reference selection and propagate them through reference/corpus dependencies. Recompute eligible corpus bounds; invalidate a bracket whose required references are contaminated. Do not retain its previous allowance.

The exclusion and arithmetic seams were executed; the downstream dependency path was read. This was not a complete issued-claim reproduction.

**A2 — A missing `chain.started` marker makes collected data disappear from assessment.**

- **Trigger:** Completed member bundles remain, but `night/chain.started` is absent.
- **Wrong output:** Harvest returns `NULL`, sets `claim_usable=False` with `window.null`, and creates no reductions. The executed `test_null_window_without_chain_start` demonstrates this using a populated six-member fixture.
- **Minimal fix:** **Flag, not refuse.** Determine collection presence from preserved bundles and other execution evidence. Assess attributable members while disclosing the missing marker. Reserve `NULL` for a genuinely unlaunched, empty window.

**A3 — `UNMEASURED` is treated as a measured hazard.**

- **Trigger:** The disk probe fails, with no measured low-space condition and all other arm modules passing.
- **Wrong output:** [arm.py:355](/Users/edr/code/JouleWise-wt-int4/joulewise/hazards/arm.py:355) refuses every status other than `PASS`; driver normalization also requires six passes. Executed output was `go=False, not_pass=['disk']`. The real-arm integration test confirms this route to no-go.
- **Related partial-window route:** Four unreadable in-window agent censuses cause `night_stopped_census_unmeasured` at [driver.py:1283](/Users/edr/code/JouleWise-wt-int4/joulewise/b5/driver.py:1283), despite no observed agent.
- **Minimal fix:** **Flag, not refuse** failed or unreadable probes. Preserve refusals for directly measured hazards and independently established number-integrity failures.

**A4 — Missing contention evidence excludes the entire roster.**

- **Trigger:** The contention journal is absent or supplies no readings; there is no measured contender.
- **Wrong output:** Harvest emits `contention.unmeasured` per member. Its effect is `EXCLUDE_MEMBER` at [catalog.py:121](/Users/edr/code/JouleWise-wt-int4/joulewise/flags/catalog.py:121). Using the real ALPHA roster and supplied draft catalog, the executed probe excluded **119 of 119** members and returned `claim_usable=False`, reason `cell.below_minimum`. `battery.unmeasured` has the same exclusion pattern.
- **Minimal fix:** **Flag, not refuse.** Make missing-journal and failed-probe codes disclosure effects. Retain exclusions for observed contamination and invalid numerical evidence.

**A5 — An optional locator controls whether the permissive hazard path exists.**

- **Trigger:** The driver cannot publish the hazard locator, or its JSON becomes unreadable. The driver explicitly permits collection after recording that failure.
- **Wrong output:** `is_hazard_locator` returns false; [arm_readiness.py:11554](/Users/edr/code/JouleWise-wt-int4/joulewise/arm_readiness.py:11554) enters legacy authentication. Executing campaign preflight with a production marker-bearing config and an absent locator raised `launch_consumption_missing`, before a member could run.
- **Minimal fix:** **Flag, not refuse.** Carry the hazard mode and window identity independently of the optional locator, using the explicit invocation or immutable plan. Keep checks for actual foreign-window/configuration mismatches.

**A6 — Missing desk JSON stops calibration before measured identity is attempted.**

- **Trigger:** In hazard mode, `--identity-epoch-json` names a missing or malformed desk-prepared file.
- **Wrong output:** Eager `_json_object` evaluation raises before `_hazard_measured_identity` runs. The executed probe returned exit 2, `calibration_reservation_json_invalid`; a sentinel confirmed that measured identity was never attempted. [chain.py:1035](/Users/edr/code/JouleWise-wt-int4/joulewise/b5/chain.py:1035) turns a reservation failure into a chain stop.
- **Minimal fix:** **Flag, not refuse** the missing desk record. Obtain the required identity independently and disclose unavailable bookkeeping. Refuse only if an actual measurement or attribution requirement cannot be satisfied.

**A7 — Valid analysis output raises `KeyError` during issuance.**

- **Trigger:** A valid current analysis artifact reaches `_claim_issuance_gate` with an otherwise admissible subject.
- **Wrong output:** The writer puts `evidence_class` under `inputs`, and the validator requires that location at [artifact.py:1094](/Users/edr/code/JouleWise-wt-int4/joulewise/analysis_engine/artifact.py:1094). Issuance reads `artifact["evidence_class"]` at lines 632 and 643, causing `KeyError` instead of evaluating the claim.
- **Minimal fix:** Read `artifact["inputs"]["evidence_class"]` at both sites and exercise issuance with an actual writer-produced artifact. The draft analysis plan already identifies this as pending L9 work.

### Re-derivation from raw bytes

**Quantity:** decode-phase CPU + GPU + ANE energy in [strict_seed_bundle](/Users/edr/code/JouleWise-wt-int4/tests/fixtures/d117_v2_production/strict_seed_bundle).

Raw `powermetrics.plist` SHA-256:

`3935ab7ebe038f347b161a614de02ef00fd4bfe0fed56a71c5dc544e96977c82`

I independently decoded the NUL-separated plists with `plistlib`, converted each rail from mW to W, and integrated sample support overlapping the decode phase.

- First sample endpoint anchor: `1786206671.1986418` s.
- Decode interval: `[1786206674.2571142, 1786206674.374248)` s.
- Subsequent endpoints: anchor plus cumulative subsequent `elapsed_ns / 10⁹`.
- Each contribution: `(CPU + GPU + ANE) × overlap_seconds`.

| Frame, zero-based | CPU W | GPU W | ANE W | Overlap s | Energy J |
|---|---:|---:|---:|---:|---:|
| 52 | 0.484971 | 0.052906 | 0 | 0.03814411163330078 | 0.020516840332984922 |
| 53 | 0.104852 | 0.00489963 | 0 | 0.061487674713134766 | 0.006748372524676323 |
| 54 | 0.151135 | 0.0215908 | 0 | 0.0175020694732666 | 0.003023058951425552 |

Thus:

`0.020516840332984922 + 0.006748372524676323 + 0.003023058951425552 = 0.030288271809086796 J`

This exactly matched both stored `phase_energy_j.decode` and a fresh `reduce_bundle(..., reducer_version="0.5.2")` result. This is fixture evidence, not live hardware validation.

## Residual risk

The targeted unittest runs executed **125 tests: 122 passed and three failed**. The failures were watchdog release tests; sandbox restrictions prevented process inspection and termination, so their product-level significance remains unresolved. No whole suite, live powermetrics collection, `launchctl`, or `sudo` was run.

The draft’s L9 analysis work remains incomplete. This audit did not establish a complete block-5 collection-to-issued-claim execution.

**Runner actions:** Save this report as `/Users/edr/night-archive/gate-prune/triple-audit/astra/REPORT.md`; the sandbox prevented writing there. Verify cleanup of the test children reported as PIDs **2546, 2658, and 2755**, checking process identity before termination. Cleanup was not confirmed. Fix A1–A4 and rerun their focused reproductions before arming.