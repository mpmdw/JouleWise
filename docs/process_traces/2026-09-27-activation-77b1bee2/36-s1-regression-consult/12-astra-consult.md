```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Hold S1: most failures need fixture repairs, but G7 also exposes a replay-relocation regression; preserve strict claim gates, rule mock completion, and repin synthetic paper receipts before merge.",
  "workspace": {
    "base_requested": "42e2af3e",
    "base_mode": "exact",
    "head_start": "42e2af3e460af1aef021ec2b5004a1121cdd4b52",
    "head_end": "42e2af3e460af1aef021ec2b5004a1121cdd4b52",
    "upstream_end": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "joulewise/calibration_bracketing.py",
        "line": 1909,
        "summary": "Battery classification reads the original locator before read_replay can resolve replacement custody; G7 is not entirely fixture-only."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "file": "scripts/run_campaign.py",
        "line": 9032,
        "summary": "The claim-window gate also prevents non-claim mock campaign completion; a narrowly ruled completion path is preferable to converting workflow tests wholesale to refusal."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "file": "configs/paper_supply/supply_map.json",
        "line": 117,
        "summary": "Three synthetic paper-custody receipt families have stale source-dependent pins."
      },
      {
        "id": "F4",
        "severity": "blocker",
        "file": "tests/test_aggregate.py",
        "line": 29,
        "summary": "Legacy fixture migration and full-suite closure remain incomplete; targeted green results do not establish a mergeable candidate."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "file": "tests/fixtures/paper_custody/repin.py",
        "line": 24,
        "summary": "The existing repin helper overwrites pending_roles and would remove the qwen3-8b production placeholder."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -c '^(FAIL|ERROR): ' /tmp/s1-regress-scout-77b1bee2/row9.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["533"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^533$"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/s1-consult-astra-77b1bee2 /opt/homebrew/bin/python3 -B /tmp/s1-consult-astra-77b1bee2/check.py /Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "stale_receipt_families=d165_closeout,reported_energy_parents,whole_window_verdict",
          "pending_production_roles=2",
          "mock_reader=not_applicable",
          "mock_window=REFUSED:not_applicable",
          "passing_pair_window=pass",
          "tampered_pair=CustodyFailure"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tampered_pair=CustodyFailure"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/s1-consult-astra-77b1bee2 /opt/homebrew/bin/python3 -B /tmp/s1-consult-astra-77b1bee2/check.py /Users/edr/code/JouleWise",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "stale_receipt_families=",
          "pending_production_roles=2"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "pending_production_roles=2"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/s1-consult-astra-77b1bee2 /opt/homebrew/bin/python3 -B /tmp/s1-consult-astra-77b1bee2/aggregate_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "original_fixture=ERROR:metadata.json_missing",
          "complete_synthetic_fixture=PASS:original_numeric_assertions_unchanged"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "complete_synthetic_fixture=PASS:original_numeric_assertions_unchanged"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/s1-consult-astra-77b1bee2 /opt/homebrew/bin/python3 -B /tmp/s1-consult-astra-77b1bee2/relocation_probe.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "replacement_battery_pair=pass:digest_bound",
          "existing_read_replay_resolver=replacement_visited",
          "S1_discovery=CustodyFailure:original_read_before_replay_resolver"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "S1_discovery=CustodyFailure:original_read_before_replay_resolver"
      }
    }
  ],
  "flags": [
    {
      "id": "A1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The repair cannot be authorized as fixture-only: replay relocation, mock completion, and previously excluded test files require explicit disposition.",
      "needs": "Issue bounded repair authority and preserve the issuing/read_replay distinction."
    },
    {
      "id": "A2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This consult inspected recorded full-suite results and ran bounded probes; it did not rerun either complete suite.",
      "needs": "Require the full suite on each repair candidate and the exact final integration tree."
    }
  ]
}
```

## Findings

**F1 — BLOCKER: G7 contains a production regression, not just incomplete fixtures.**

At [calibration_bracketing.py:1909](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/joulewise/calibration_bracketing.py:1909), S1 authenticates battery evidence before `_candidate_from_observation(..., mode=mode)` reaches the existing custody resolver. The battery check reads `observation.custody_locator` directly.

I reproduced this with:

- An absent original locator.
- Replacement custody containing digest-bound battery evidence that authenticates as `pass`.
- The existing `read_replay` resolver successfully reaching that replacement.
- S1 discovery raising `CustodyFailure` on the absent original **before reaching the resolver**.

The probe substitutes only the physical candidate-loading leaf; it does not substitute battery authentication or custody resolution. This isolates the ordering defect.

The existing relocation tests expressly require the original to remain absent: [test_run_campaign.py:8096](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/tests/test_run_campaign.py:8096). Creating evidence at that original location would weaken their purpose.

**Required correction:** authenticate battery evidence through the same mode-aware custody resolution used for the candidate, preserving recorded identity and digest checks. Audit the repeated original-locator classifications at `calibration_bracketing.py:2260`, `:2289`, and the candidate-path recheck at `:2333`. Issuing must still reject replay-only replacement custody; corruption must still raise.

This needs a bounded production repair in `joulewise/calibration_bracketing.py`, with regression coverage in `tests/test_bfgs_calibration_bracketing.py` and the existing relocation tests. I disagree with the scout’s unconditional fixture-only classification of G7.

**F2 — BLOCKER: keep mock refusal at claim-window scope; permit narrowly defined non-claim campaign completion.**

Final texts v1.1 distinguishes three obligations:

- Text 8 admits digest-bound mock bundles to `BundleReader.metadata()` with `battery_float_status = "not_applicable"`.
- Text 12 requires every consumer building bundles “whose numbers are claimed” to refuse `not_applicable`.
- Text 18 says “a MOCK bundle reduces as today.”

These appear in the [Final texts ruling:115](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md:115), with the claim-window rule at `:123` and hermeticity at `:137`. Text 9 also expressly rejects `not_applicable` in scored reduction.

Therefore:

| Operation | Required behavior |
|---|---|
| Individual mock bundle reading/reduction | Admit as `not_applicable`; no battery probe. |
| Claim-bearing window, aggregate, mint, scored reduction, or licensing verdict | Refuse the whole computation. |
| Explicitly non-claim mock campaign collection | May complete operationally, with no successful claim verdict or claim artifact. |

I recommend the third row as a **small, explicitly ruled campaign-completion branch**, preserving the strict window helper unchanged. Currently [run_campaign.py:9032](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/scripts/run_campaign.py:9032) invokes that helper before even recording collection classification.

The branch must authenticate mock identity from bound config bytes, retain collection failures, visibly report non-claim status and `not_applicable`, and stop before claim finalization. Mixed, unknown, tampered, or explicitly claim-requesting inputs must not obtain this completion exemption. Do not use the later `claim_bearing` boolean alone as a universal bypass.

The SWEEPCLASS/RETURNS definition concerns what an output actually supplies or licenses. A `non_claim` label cannot make an energy-bearing claim artifact harmless. See [RETURNS amendment 72:155](/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-3ba66eeb/60-s1-fix3/21-coldgate-fable-ruling.md:155).

**Least production change:** one completion boundary in `scripts/run_campaign.py`; no `allow_mock` option on the shared gate and no parallel non-claim implementation of all eight consumers. G2 tests exercising claims should receive complete synthetic passing evidence, while dedicated mock-claim tests assert refusal. Do not change all 98 outcomes into expected refusals.

**F3 — BLOCKER: G9 requires an authorized, reviewed repin before the mergeable candidate is approved.**

I independently recomputed receipt digests. Exactly these families are stale on S1 and current on main:

- `d165_closeout`
- `reported_energy_parents`
- `whole_window_verdict`

The relevant map entries are **`test_fixture_non_issuing`**, not issued paper measurements; see [supply_map.json:114](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/configs/paper_supply/supply_map.json:114). Their temporary receipts are constructed by [test_paper_custody.py:157](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/tests/test_paper_custody.py:157). The source digest deliberately includes complete owner modules, so S1 changing those modules legitimately invalidates the pins.

**Who:** the lead may explicitly authorize a bounded paper-custody repair seat. Original S1 authority does not include the supply map. The repin is not implicitly authorized by a failing test.

**Order:** finalize production repairs—including F1 and the mock ruling—then regenerate these synthetic receipts and their dependent inventory digests, then verify the exact combined candidate.

**Same PR?** Not an inherent custody requirement. Separate commits or a separately reviewed companion change are fine. But merging S1 first and promising a later repin leaves the required suite red. The simplest landing is one combined, explicitly authorized PR containing separately reviewable repair and repin commits. Any alternative must preserve a green main.

The review should verify:

1. The validator-source census still covers every intended owner; no owner was removed to regain matching hashes.
2. Only the affected receipt/inventory pins change—expected to be six digest fields if no additional owner changes affect other families.
3. Both pending production roles, non-issuing modes, subjects, issuance gates, input bindings, and source census remain unchanged.
4. Stale-source, tampered-input, and fixture-to-production promotion cases still refuse.
5. Paper-custody, reported-energy, rendering, and the full suite pass.

No immutable issued receipt or scientific result should be rewritten under this synthetic-fixture repair.

**F4 — BLOCKER: complete the fixture migration without replacing the tests’ original propositions.**

Verified evidence supports the reported integration failure: **7,647 tests, 115 failures, 418 errors**, representing **478 distinct test IDs across 42 modules**. The recorded main result is **7,540 tests, zero failures/errors**. S1’s branch/head and the final pass’s `MERGE` text match the prompt.

One qualification: the final pass itself says the entire targeted V1 had not been rerun on `c7593edb`. Thus “every targeted check passed” describes accumulated evidence, not one complete run at that head.

At [test_aggregate.py:29](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/tests/test_aggregate.py:29), the fixture writes only a summary. I reran its confidence-interval test, then supplied complete temporary synthetic battery evidence through an in-memory fixture-writer replacement. **The original numerical assertions passed unchanged.** That is the repair pattern.

**Ordered repair plan**

1. **Install authority and dispositions.** Rule F1/F2; explicitly authorize previously excluded tests. Preserve the original historical set and historical scope-fence evidence.
2. **Establish shared synthetic builders.** Propose `tests/bfgs_fixture.py`, reusing `tests/battery_float_fixture.py` read-only. Provide explicit bundle and capture construction, bound config bytes, journal span, raw battery pair, and final digest sealing. Builders write only into test-owned temporary roots.
3. **Repair shared builders before dependent modules.** Key existing owners include:
   - `tests/test_run_campaign.py:1320` and its generated fake CLI at `:1452`.
   - `tests/test_analysis_finalizer.py:212`.
   - `tests/test_floor_extraction.py:398`.
   - `tests/test_mint_floor_artifact_generalized.py:416`.
   - `tests/test_calibration_bracketing.py:440`.
   - `tests/test_calibration_live_three_window.py:88` and `:118`.
4. **Repair module groups with disjoint ownership.** Retain every original scientific, provenance, custody, and lifecycle assertion.
5. **Reclassify G11 after upstream repairs.** Nested-suite failures should disappear through their dependencies. Investigate every survivor. The observed unbound locals are in test code following failed subtests; keep assertions inside the corresponding subtest rather than initializing dummy values to conceal an earlier failure.
6. **Repin G9 last**, then run the full suite and review the combined diff.

**Proposed exact test/fixture WRITE_SCOPE**

This is a proposed future allowlist, not authority exercised by this consult. Three repair seats are justified; split by builder dependencies, not G-number. Shared builders need one owner and an agreed interface before parallel work.

**Foundation/calibration seat:**
```text
tests/bfgs_fixture.py
tests/test_bfgs_calibration_bracketing.py
tests/test_bfgs_window_consumers.py
tests/test_calibration_bracketing.py
tests/test_calibration_live_three_window.py
tests/test_epoch_continuation.py
tests/test_bracket_binding_cli.py
```

**Analysis/floor seat:**
```text
tests/test_aggregate.py
tests/test_analysis_claims.py
tests/test_analysis_finalizer.py
tests/test_analysis_integration.py
tests/test_check_window_provenance.py
tests/test_custody_mode_inventory.py
tests/test_d117_floor_qwen25_1p5b_plan.py
tests/test_d117_floor_qwen25_7b_plan.py
tests/test_d165_dominance_closeout.py
tests/test_detection_floor.py
tests/test_dominance_closeout.py
tests/test_floor_extraction.py
tests/test_floor_mint_estimator.py
tests/test_mint_floor_artifact.py
tests/test_mint_floor_artifact_generalized.py
tests/test_phase_share.py
tests/test_pipeline_smoke_tail.py
tests/test_uncertainty_p2029.py
tests/test_window_duration_margins.py
```

**Controller/campaign seat:**
```text
tests/test_arm_readiness_dry_run.py
tests/test_arm_readiness_evidence_author.py
tests/test_audit_amplification.py
tests/test_cli.py
tests/test_cli_run.py
tests/test_collector_analysis_manifest_id.py
tests/test_corpus_strict_validation.py
tests/test_experiment.py
tests/test_launch_window.py
tests/test_p2038_production_path.py
tests/test_package_bundle_pack.py
tests/test_partial_record_enclosure.py
tests/test_powermetrics.py
tests/test_run_campaign.py
tests/test_whole_window.py
tests/test_whole_window_selection.py
```

These cover the 39 failing non-G9 modules. Many dependents should require no edit once their builders are repaired; scope permits inspection-driven repairs, not obligatory churn.

Separately authorize the production changes in `joulewise/calibration_bracketing.py` and `scripts/run_campaign.py`; add `tests/test_bfgs_consumer_sweep.py` only for truthful coverage of those changes. G9’s bounded scope is `configs/paper_supply/supply_map.json`, `tests/fixtures/paper_custody/repin.py`, and `tests/test_paper_custody.py`.

Do not initially include `tests/receipt_corpus.py`, recorded fixture corpora, calibration configuration, the historical allowlist, or epoch issuance builders: no demonstrated repair requires changing them. Return an exact scope request if that changes. Final texts explicitly excluded several proposed legacy test files; a green fixed-range fence does not grant permission to edit them.

**Defect-shaped acceptance checks**

| Group | Required checks |
|---|---|
| G1/G3/G4 | Complete synthetic control reaches the old assertion; absent evidence and absent required artifacts still refuse distinctly. |
| G5 | Legitimate fixture edits rebind dependent digests before the intended mutation. Deliberate digest mismatches remain mismatches. Modified historical-looking copies gain no exemption by name. |
| G6 | Replace placeholder capture bytes with valid serialized evidence; derive manifest, ledger, receipt, and head hashes from those bytes. Invalid JSON remains a custody refusal. |
| G7 | Valid relocated evidence passes replay with the original absent; issuing rejects replacement-only custody; altered replacement bytes refuse. Preserve derivation/open-session exclusion assertions. |
| G8/G10 | Inject the battery **runner**, not a passing gate verdict. Charging, timeout, missing post, raw tamper, and real-runner-default cases retain their behavior. |
| G2 | Mock collection can complete only through the ruled non-claim path; every claim route still refuses mock evidence. Mixed and forged-mock cases cannot bypass. |
| G11 | Restore the intended downstream assertion. A test of another defect must not become merely “some battery exception occurred.” |

Never solve these groups through skips, broad exception assertions, global gate mocks, production fixture flags, relaxed tolerances, or automatic resealing after the deliberate defect has been planted.

**Process change:** make a full-suite result a mandatory prerequisite for **every completed fix head advancing to review**, and repeat it on the exact final integration tree whenever that tree differs. Use the canonical `/opt/homebrew/bin/python3 -B -m unittest discover -s tests`; any accepted sharded equivalent must cover the same inventory and propagate all failures. Record head, command, counts, skips, and exit status together. A later targeted pass cannot supersede a red full suite.

**F5 — SHOULD-FIX: do not run the existing repin helper unchanged.**

[repin.py:24](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/tests/fixtures/paper_custody/repin.py:24) replaces `pending_roles` with only the 1.7B role. The current map also contains the 8B role at [supply_map.json:11](/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2/configs/paper_supply/supply_map.json:11).

It also rewrites modes, source census, and an extraction-spec file. Replace that broad operation with a digest-only repin that preserves unrelated structure and refuses unexpected semantic changes. Add a preservation assertion for both pending roles.

## Residual risk

This was a completed read-only consult. No repository writes, commits, other-model calls, or other consult-seat answers were used. Scratch probes are under `/tmp/s1-consult-astra-77b1bee2/`.

I inspected recorded full-suite evidence rather than rerunning both suites. The relocation probe authenticates real synthetic battery bytes but substitutes the physical-fit leaf; the eventual repair still needs an end-to-end relocation test.

I would **not merge S1 in its current form**. F1 is an additional production reason, beyond suite closure. I would split repair ownership and commits, but keep controller evidence and claim-consumer enforcement together at landing. Nothing found here justifies discarding the gate or reopening already-routed unrelated lanes.

RECOMMEND: Hold S1; fix replay custody resolution, rule minimal non-claim mock completion, repair fixtures without weakening assertions, repin synthetic receipts after final source changes, and merge only the fully green combined candidate.