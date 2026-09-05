```json
{
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "CWI-01",
        "severity": "blocker",
        "location": "docs/process/coldgate_charter_registry.md:49-66; docs/process/coldgate_charter_v3_candidate.md:49-64; tests/test_coldgate_charter_v3.py:28-36",
        "text": "The registry adopted clean-launch and contamination-disclosure clauses and orders both folded into charter v3 at the next byte-change opportunity. The landed v3 candidate adds only D-170's packet-input clause, and its test enforces byte equality with v2 after removing exactly that one amendment. V2's two deferred clauses are therefore absent from the bytes whose digest is queued for Ed re-ratification. V2 remains operative, so no live gate is presently misdescribed; the defect is in the candidate/promotion contract. V2 below executes the omission proof.",
        "counterfactual": "Add both adopted convening clauses to the v3 candidate, recompute and replace its registry digest, and change the test from a one-amendment invariant to assertions covering all three required amendments. Supplying or promoting the current digest would make registry item 4 false."
      },
      {
        "id": "CWI-02",
        "severity": "blocker",
        "location": "docs/contracts/bridge_protocol.md:56-75; docs/process_traces/2026-09-04-fanout/CHARTER-V3-PACKET-INPUTS-01/01-sol-report.md:159; docs/process_traces/2026-09-04-fanout/{DG071-PROVENANCE-TEST-01,MIDCAMPAIGN-CURE-GENERATION-01,PREWINDOW-REGEX-01,R7F-DX-PROSE-SCAN-01}/01-sol-report.md",
        "text": "Five ruling-backed implementation seats did not return the mandatory exact `## Clause map` surface before execution-refuter fan-out: CHARTER uses `### Clause map`; DG071, MIDCAMPAIGN, PREWINDOW, and R7F omit the heading. The filename-scoped S1 shape test at protocol lines 77-81 does not narrow the substantive delegated-report and sequencing requirements at lines 56-75. The five reports identify genre `implementation`; their missions implement the magistrate's D-170, DG071 fixture-shape synthesis, D-153, C-6/S-7, and coldgate-A2 rulings respectively. V3 is the executed heading census.",
        "counterfactual": "Return a compliant `## Clause map` for each of the five seats (including production site, biting assertion, and one-site counterfactual or `NOT PINNED`), have the magistrate read the maps, hand every missing/unpinned row to both lenses, and rerun the affected refuter disposition. Until then the prior LANDABLE sequence cannot satisfy the bridge contract."
      }
    ]
  },
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The requested 12-landing tree is NOT LANDABLE: charter v3 omits two adopted clauses, and five ruling-backed implementation seats bypassed the mandatory clause-map/refuter sequence.",
  "workspace": {
    "base_requested": "origin/main@04cd6e52e9d6ed2da369398bb448c5454f1917b3",
    "base_mode": "exact",
    "head_start": "7eed7c5f02837d5621ef8153a349ea03f37f2c9a",
    "head_end": "fc8994c939585569068842c45419735c3c1833df",
    "upstream_end": "04cd6e52e9d6ed2da369398bb448c5454f1917b3",
    "branch": "int/2026-09-04-fan-wave-1"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/wave-1/01-refuter-contract-integrated.md"
  ],
  "unowned_dirty": [],
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_exits tests.test_coldgate_charter_v3 tests.test_coldgate_receipt tests.test_issue_dg071_dg075_statistics tests.test_midcampaign_cure_generation_docs tests.test_paper_round7_artifacts tests.test_prewindow_check tests.test_quiet_guard tests.test_quiet_guard_process tests.test_receipt_histsem",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 310 tests in 3750.994s",
          "OK (skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 310 tests in [0-9.]+s\\n\\nOK \\(skipped=2\\)$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'from pathlib import Path; r=Path(\"docs/process/coldgate_charter_registry.md\").read_text(); c=Path(\"docs/process/coldgate_charter_v3_candidate.md\").read_text(); assert \"Fold items 1-2 into charter v3 at the next byte-change opportunity\" in r; missing=[s for s in (\"Clean launch environment\", \"Contamination disclosure duty\") if s not in c]; assert missing==[\"Clean launch environment\", \"Contamination disclosure duty\"], missing; print(\"registry obligation present; candidate omissions:\", \", \".join(missing))'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "registry obligation present; candidate omissions: Clean launch environment, Contamination disclosure duty"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "registry obligation present; candidate omissions: Clean launch environment, Contamination disclosure duty"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "for f in docs/process_traces/2026-09-04-fanout/{CHARTER-V3-PACKET-INPUTS-01,DG071-PROVENANCE-TEST-01,MIDCAMPAIGN-CURE-GENERATION-01,PREWINDOW-REGEX-01,R7F-DX-PROSE-SCAN-01}/01-sol-report.md; do if rg -q '^## Clause map$' \"$f\"; then echo \"$f EXACT_HEADING\"; elif rg -q '^### Clause map$' \"$f\"; then echo \"$f WRONG_LEVEL\"; else echo \"$f MISSING\"; fi; done",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "docs/process_traces/2026-09-04-fanout/CHARTER-V3-PACKET-INPUTS-01/01-sol-report.md WRONG_LEVEL",
          "docs/process_traces/2026-09-04-fanout/DG071-PROVENANCE-TEST-01/01-sol-report.md MISSING",
          "docs/process_traces/2026-09-04-fanout/MIDCAMPAIGN-CURE-GENERATION-01/01-sol-report.md MISSING",
          "docs/process_traces/2026-09-04-fanout/PREWINDOW-REGEX-01/01-sol-report.md MISSING",
          "docs/process_traces/2026-09-04-fanout/R7F-DX-PROSE-SCAN-01/01-sol-report.md MISSING"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(EXACT_HEADING\\n){5}$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --quiet 7eed7c5f..HEAD -- joulewise scripts tests docs/process docs/paper docs/designs docs/process_traces/2026-08-22-t20/real-transaction-runbook.md; rc=$?; echo \"requested-tree substantive/test delta rc=$rc\"; git merge-base --is-ancestor 7eed7c5f HEAD; rc=$?; echo \"requested HEAD ancestor rc=$rc\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "requested-tree substantive/test delta rc=0",
          "requested HEAD ancestor rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "requested-tree substantive/test delta rc=0\\nrequested HEAD ancestor rc=0$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "While this review ran, the shared branch advanced from requested HEAD 7eed7c5f to fc8994c9 by adding the twelve execution-refuter reports and the Opus counter-review. V4 proves the requested HEAD is an ancestor and that the intervening commits changed no substantive or test path reviewed here; all contract conclusions remain pinned to origin/main..7eed7c5f.",
      "needs": "The magistrate should consume this verdict against requested tree 7eed7c5f, while separately adjudicating the later review artifacts."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Per the preflight rule, only the ten test modules touched by origin/main..7eed7c5f were run; no repository-wide suite was run in this seat.",
      "needs": "Magistrate runs the canonical whole suite separately."
    }
  ]
}
```

## Findings

### CWI-01 — blocker

The candidate digest presented in the registry binds incomplete v3 bytes. The adopted registry instruction at lines 65-66 is unambiguous: both clean-launch and contamination-disclosure duties go into v3 at its next byte change. The D-170 landing created exactly that opportunity but copied v2 and added only the packet-input paragraph. Its regression locks in the omission by requiring the remainder to equal v2. This contract reading refutes the execution-LANDABLE result and blocks sending the present candidate digest to Ed.

### CWI-02 — blocker

The clause map is an acceptance artifact and an ordering gate, not optional report decoration. The five named ruling installs lack the required exact surface; consequently the magistrate could not have read their maps before the already-landed execution refuters ran. A compliant map must precede renewed refutation. This contract reading refutes those execution-LANDABLE results even though the integrated code tests are green.

## Ruling and name conformance

| Landing | Contract/name result |
|---|---|
| CALEXITS-EVIDENCE-BYTES-01 | Exact completed-seat name; deterministic fixed `ps` fixture matches the catch-all ruling. |
| CALEXITS-HYGIENE-FIXES-01 | Exact completed-seat name; hygiene/default-origin/E-4 work matches the catch-all ruling. |
| CGV-HARDEN-01 | Matches the ruling to land a persistence primitive but defer wiring until the handoff exists. |
| CHARTER-V3-PACKET-INPUTS-01 | Candidate/nonoperative/Ed-reratification naming matches; content fails CWI-01. |
| DG071-PROVENANCE-TEST-01 | Exact completed-seat name; test-only footprint leaves producer and issued artifacts unchanged. |
| MIDCAMPAIGN-CURE-GENERATION-01 | Matches the ruling: transaction record landed; the paper paragraph remains pending after paper e/f/g. |
| NODE-CUSTODY-DEFAULT-01 | Matches adopted Option A as a design decision; production remains intentionally pending. |
| PINSET-GRAMMAR-EXCLUSION-01 | Exact completed-seat name and direct-child projection grammar. |
| PREWINDOW-REGEX-01 | Matches the completion ruling by strengthening the regression around the already-landed alternation. |
| QUIET-GUARD-01 | Matches Option A's desk repair and digest update; makes no false live-install/closure claim. |
| R7F-DX-PROSE-SCAN-01 | Exact completed-seat name and coldgate-A2 bounded DX scan. |
| p2-rows | Matches four logical retirements and leaves P2-010/P2-046B physically queued. |

The five exact mission names absent from individual rows in `01-magistrate-rulings.md` are covered by its completed-seat catch-all; no unresolved alias was found.

## Cross-unit seams

An executed per-landing path census returned exactly one overlap: `2 tests/test_calibration_exits.py 50bcbbfe,5f0ccc38`. CALEXITS-HYGIENE adds constants/default-origin/E-4 assertions; CALEXITS-EVIDENCE-BYTES adds the fixed `ps` evidence fixture in disjoint hunks. The integrated module passed.

Other conceptual overlaps do not interfere: CGV remains unwired while charter v3 remains nonoperative; PREWINDOW changes only a regression around the existing process-name alternation while QUIET changes start-time identity classification and its install digest; PINSET tightens the pre-authoring grammar while MIDCAMPAIGN records the v4 cure-family limitation; DG071 leaves the producer/artifacts unchanged while R7F scans only the bounded draft-DX region. No new guard trips another landing.

## D-161-sensitive surfaces

The integrated tree changes these evidence, claim, digest, registry, or pre-registration-adjacent surfaces:

- `tests/test_calibration_exits.py`: a deterministic `ps` fixture now proves nonempty `observed_processes` bytes; justification is closing an evidence-byte coverage hole without changing the collector or evidence format.
- `joulewise/arm_readiness.py:2980-3032`: pre-authoring evidence exclusion is narrowed to direct `projection-NNNN.(json|sha256)` children; justification is the ruled grammar fence while preserving the full post-authoring custody set.
- `docs/process_traces/2026-08-22-t20/real-transaction-runbook.md:1225-1236`: the D-153 transaction limitation declares any non-config mid-campaign cure a new family with all ALPHA/BETA/GAMMA generations; the paper claim remains deferred.
- `joulewise/quiet_guard_process.py:318-328` and `scripts/setup_quiet_guard.sh:14`: evidence admission distinguishes changed start time from same-start churn, and the reviewed-artifact digest is recomputed; justification is the quiet-guard identity contract.
- `docs/process/coldgate_charter_registry.md:21-37`: candidate status and digest are added under D-170 pending Ed re-ratification; CWI-01 refutes the completeness of those candidate bytes.
- `scripts/check_paper_round7_artifacts.py:726-796,859-867` and `docs/paper/round7/fill-checklist.md:36-39`: the claim-publication fence gains a bounded DX prose scan under coldgate A2; it changes no scientific value or issued artifact.
- `joulewise/coldgate_receipt.py`: a new TOCTOU-resistant, no-overwrite, file-and-directory-fsynced custody primitive lands under the CGV ruling and remains deliberately unwired.

No campaign config, pre-registered physics constant, `docs/paper/draft-v2-skeleton.md`, issued DG artifact, result-registry disposition, or scientific claim value changes in the requested tree.

## Docs-versus-code truth

Aside from CWI-01, sampled claims agree with implementation: quiet-guard prose matches its discriminator and pinned digest; PINSET prose matches direct-child `fullmatch` grammar and the unchanged identity contract; R7F's checklist matches its bounded scanner; CGV's design accurately says the primitive is unwired; MIDCAMPAIGN accurately leaves paper work pending. CWI-02 is instead a process-evidence truth failure: required clause-map evidence is absent from five implementation reports.

## Residual risk

The shared branch advanced only through review artifacts while V1 ran; V4 proves no reviewed substantive/test path changed. No `[QUIET-MAC]` campaign, Darwin root install, live hardware validation, or full suite was attempted. Those external and magistrate-owned gates remain separate from this contract verdict.
