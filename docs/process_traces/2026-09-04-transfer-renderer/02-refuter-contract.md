```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "CR-01",
        "severity": "blocker",
        "title": "The projection cannot authenticate the exact 20-edge census or maximum selection"
      },
      {
        "id": "CR-02",
        "severity": "blocker",
        "title": "The existing estimator revision is recorded but not authenticated"
      },
      {
        "id": "CR-03",
        "severity": "blocker",
        "title": "Refusal reasons are accepted with contradictory census state and truthful incomplete state is rejected"
      },
      {
        "id": "CR-04",
        "severity": "should_fix",
        "title": "The renderer installs an unruled reason-code vocabulary"
      }
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: exact prose/token surfaces pass, but the v1 validator cannot prove the 20-edge maximum, accepts arbitrary estimator revisions, and admits contradictory refusal records.",
  "workspace": {
    "base_requested": "886ec4d2",
    "base_mode": "exact",
    "head_start": "886ec4d204e68c9178f9d53aab7ad55396434185",
    "head_end": "886ec4d204e68c9178f9d53aab7ad55396434185",
    "upstream_end": "c74c7e6a7448be34e7de54ba839004c2ace6cc03",
    "branch": null
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-transfer-renderer/02-refuter-contract.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_transfer",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.006s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 13 tests in 3.145s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 13 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check origin/main..HEAD -- docs/paper/results-fill-registry.md docs/process_traces/2026-09-04-transfer-renderer/01-seat-landing-report.md joulewise/results_fill_transfer.py tests/fixtures/results_fill_transfer/not_evaluated.json tests/fixtures/results_fill_transfer/not_supported.json tests/fixtures/results_fill_transfer/supported.json tests/test_results_fill_transfer.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --name-only origin/main..HEAD -- runs evidence artifacts experiments configs/campaigns tests/fixtures/d117_v2_production",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "python3 -c 'import json; from pathlib import Path; from joulewise.results_fill_transfer import transfer_result_id,validate_transfer_fiducial_result as v; s=json.loads(Path(\"tests/fixtures/results_fill_transfer/supported.json\").read_text()); s[\"source_capture\"][\"estimator_revision\"]=\"arbitrary_changed_estimator.v99\"; s[\"result_id\"]=transfer_result_id(s); print(\"arbitrary_estimator_errors=\",v(s)); r=json.loads(Path(\"tests/fixtures/results_fill_transfer/not_evaluated.json\").read_text()); r[\"reason_codes\"]=[\"run_census_incomplete\"]; r[\"result_id\"]=transfer_result_id(r); print(\"incomplete_reason_with_complete_10_20_errors=\",v(r)); r[\"census\"][\"observed_run_count\"]=9; r[\"census\"][\"observed_edge_count\"]=18; r[\"result_id\"]=transfer_result_id(r); print(\"truthful_incomplete_9_18_errors=\",v(r))'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "arbitrary_estimator_errors= []",
          "incomplete_reason_with_complete_10_20_errors= []",
          "truthful_incomplete_9_18_errors= ['census.observed_run_count must equal 10', 'census.observed_edge_count must equal 20']"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "arbitrary_estimator_errors= \\[.+\\]"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "for f in tests/fixtures/results_fill_transfer/*.json; do printf '%s bundles=%s edge_records=%s\\n' \"$(basename \"$f\")\" \"$(jq '.source_capture.bundle_sha256|length' \"$f\")\" \"$(jq '[..|objects|select(has(\"edge\"))]|length' \"$f\")\"; done",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "not_evaluated.json bundles=10 edge_records=0",
          "not_supported.json bundles=10 edge_records=1",
          "supported.json bundles=10 edge_records=1"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "edge_records=20"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main is not an ancestor of this exact detached HEAD; the requested review therefore used origin/main..HEAD with the seven landing paths as an explicit pathspec.",
      "needs": "Lead should continue to review/land the transfer commit as a bounded patch, not treat the unscoped 77-file branch comparison as this seat's diff."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The capture producer at d67ee56c remains outside this HEAD and unreviewed, so its producer/validator modules were inspected from Git objects but not executed; only the preflight-allowed current-HEAD tests ran.",
      "needs": "Review and accept a capture revision separately before wiring a real result projection."
    }
  ]
}
```

## Findings

### CR-01 — blocker — The projection cannot authenticate the exact 20-edge census or maximum selection

**Text.** R3 adopts an auditable raw-interval witness and the packet requires the exact run/edge census (`docs/process_traces/2026-09-04-paper-i/05-adjudication-packet-contracts.md:176`). The agreed detailed contract requires recomputation for every accepted edge, exact two-edge-per-run coverage, unrounded maximum selection, deterministic tie-breaking, and replay of duplicated capture summaries (`docs/process_traces/2026-09-04-paper-i/02-consult-sol-contracts.md:302`); its fixture clause requires twenty exact edge records (`:312`). The landed schema contains ten bundle digests and only one selected witness (`joulewise/results_fill_transfer.py:75-101,228-250,272-320`). The fixtures merely assert census scalars 10/20 and contain zero or one edge record (`tests/fixtures/results_fill_transfer/supported.json:2-24,29-83`; refusal equivalent at `not_evaluated.json:2-24`). The test mutates declared census fields but never an unselected edge or tie (`tests/test_results_fill_transfer.py:190-205`).

**Counterfactual.** A reissued projection may claim 20 edges, select a 0.022 s witness, and render `supported` even if an omitted edge in the source capture is 0.500 s; the validator has no bytes from which to detect the false maximum.

**Cure shape.** Authenticate and reopen the reviewed capture bytes (including all ten runs/twenty edges) or add their closed edge inventory to the projection; require two named edges per ordered bundle, replay every interval-plus-anchor bound, select the unrounded maximum with the registered tie-break, and cross-check every duplicated capture summary. Add non-selected-largest, missing/duplicate edge, swapped-edge, and tie-break mutations.

### CR-02 — blocker — The existing estimator revision is recorded but not authenticated

**Text.** The registered task requires the EXISTING estimator unmodified and says a changed estimator voids the comparison (`docs/process/state_kernel.json:5335-5338,5407-5411`); the current registered implementation revision is `joint_loss_sublevel_interval_branch_v2` (`joulewise/powermetrics_fiducial.py:169`). The validator accepts any nonempty revision (`joulewise/results_fill_transfer.py:203-207`) and any syntactically valid source digest, while every fixture invents `existing_pulse_estimator.synthetic_fixture.v1` (`tests/fixtures/results_fill_transfer/supported.json:72-73`). A freshly content-addressed mutation to `arbitrary_changed_estimator.v99` validates with no errors.

**Counterfactual.** A projection produced by a changed estimator can be reissued with its new string/hash and render a favorable comparison, despite the existing contract making that a different, void measurement.

**Cure shape.** Bind v1 to the exact registered estimator revision and authenticated source digest/receipt of the reviewed capture; reject a freshly reissued changed revision or digest. Keep fixture values synthetic, but use the real registered revision identity and synthetic custody hashes.

### CR-03 — blocker — Refusal reasons are accepted with contradictory census state and truthful incomplete state is rejected

**Text.** The agreed contract says `not_evaluated` represents an authentication/schema/coverage refusal and nullable quantities must reflect what actually authenticated (`docs/process_traces/2026-09-04-paper-i/02-consult-sol-contracts.md:302`). Instead, the validator always requires observed 10 runs/20 edges (`joulewise/results_fill_transfer.py:253-269`), then accepts `not_evaluated` on the presence of any allowed reason alone (`:399-401`). Thus a reissued `run_census_incomplete` record with complete 10/20 scalars passes, while truthful 9/18 scalars fail. The shipped `source_capture_refused` fixture likewise asserts complete 10/20 census and ten source bundle hashes (`tests/fixtures/results_fill_transfer/not_evaluated.json:2-24,24-79`).

**Counterfactual.** The renderer prints an authenticated-sounding refusal whose issued reason contradicts its issued census, while the producer cannot represent the actual incomplete census that caused refusal.

**Cure shape.** Define reason-specific field/status invariants: comparable outcomes require the exact complete census; refusal projections carry authenticated observed counts and nullable/unavailable parents; each reason must agree with those fields. Test both contradictory complete-state reasons and truthful partial-state refusals.

### CR-04 — should_fix — The renderer installs an unruled reason-code vocabulary

**Text.** The adopted material specifies only a closed ordered unique list and a semicolon rendering (`docs/process_traces/2026-09-04-paper-i/02-consult-sol-contracts.md:298-308`); neither R3 nor TR-01 enumerates its members (`docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:19-21`; `docs/paper/results-fill-registry.md:920`). The implementation nevertheless registers seven literals and their order (`joulewise/results_fill_transfer.py:45-55`).

**Counterfactual.** A future ruled producer cannot know whether to emit these invented literals or its own authenticated capture reasons; either choice can fail interoperability without violating the written R3 contract.

**Cure shape.** Register the exact reason-code enum and order in the owning schema/registry (including reason-to-field semantics from CR-03), then make producer, validator, fixture, and rendering test consume that one contract.

The token name, schema name, public quantity names, `b_fiducial_s` source-field literal, three outcome literals, six-decimal rendering, all three exact sentences, and nine site names match R3/TR-01 (`joulewise/results_fill_transfer.py:20-40,209-220,431-460`; `docs/paper/results-fill-registry.md:920`). No rendered magnitude is inferred or defaulted: `<R>` and `<B>` are read from issued fields and only formatted after unrounded relation checks (`joulewise/results_fill_transfer.py:364-398,431-453`). The defect is that the issued maximum/census/estimator assertions are insufficiently authenticated.

## Residual risk

The capture producer at `d67ee56c` is expressly unreviewed and was not executed from this HEAD. Frozen campaign/evidence paths are isolated: `git diff --name-only origin/main..HEAD -- runs evidence artifacts experiments configs/campaigns tests/fixtures/d117_v2_production` returned no paths. The exact landing range `85b75cf2..886ec4d2` contains only the registry row, renderer, three new synthetic fixtures, one test, and the seat report; no frozen artifact was touched.
