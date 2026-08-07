```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REVISE: value/ID hygiene and structural cross-references pass, but pending demonstrations are written as completed results, the two-gate claim rule is collapsed into a summed threshold, and several claims exceed the custodied evidence boundary.",
  "workspace": {
    "base_requested": "5e472e8",
    "base_mode": "exact",
    "head_start": "5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e",
    "head_end": "5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e",
    "upstream_end": "5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e",
    "branch": "impl/paper-mvp-complete"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "REVISE",
    "source_conflicts": [],
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "docs/paper/draft-v1.md",
        "line": 5,
        "related_lines": [168, 248],
        "title": "Pending demonstration evidence is presented as an achieved result",
        "failing_scenario": "A reviewer follows the abstract's claim that the paper demonstrates two-model measurements and refusal behavior, but reaches entirely pending tables and no re-issued demonstration verdict. The placeholder does not retract the preceding present-tense empirical assertion.",
        "source": "docs/paper/draft-v1.md:180-196; docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md:3-5,28-30",
        "recommended": "Use prospective design language until re-issued artifacts exist; do not claim demonstrated resolution or refusal in the abstract or conclusion yet."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "file": "docs/paper/draft-v1.md",
        "line": 172,
        "related_lines": [193],
        "title": "The ratified two-gate claim rule is collapsed into one summed acceptance threshold",
        "failing_scenario": "For an 8 J point effect, 5 J floor, and 2 J claim-side bound, an interval of 6-10 J can pass the separate floor and direction gates, while the draft's rule that the interval must clear a 7 J effective bar would reject it. That is not the implemented or ratified decision rule.",
        "source": "docs/decision_log.md:5130-5184; docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:135-147,195-207; joulewise/analysis_engine/claims.py:321-370",
        "recommended": "Present floor clearance and interval-supported direction as separate gates. Retain floor plus claim-side bound only as the required practical sizing disclosure, and expose both components separately in the result table."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "file": "docs/paper/draft-v1.md",
        "line": 230,
        "related_lines": [248],
        "title": "The short-prompt prefill diagnostic is incorrectly called below-bar and already refused",
        "failing_scenario": "A reviewer compares the source diagnostic with the paper: its point estimate is 5.809930 J, above the approximate 5 J practical bar, while its composed interval overlaps the bar. The paper instead says the effect is below the bar and has been refused, converting MARGINAL diagnostic evidence into a completed result.",
        "source": "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md:7-25; docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:121-133,195-221",
        "recommended": "State that the historical, non-claim diagnostic point was marginally above the practical bar but its composed interval overlapped it; describe floors-only/decode-only as the prospective default, not an issued refusal."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": 176,
        "title": "The longer-prompt projection does not disclose the missing 7B evidence",
        "failing_scenario": "A reader can interpret the roughly twice-bar projection as supported by prompt-length observations for both models and treat the longer-prompt design as de-risked, although no historical 7B corpus exceeds 128 prompt tokens and the fresh arm would be the first direct test.",
        "source": "docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md:16-25; docs/process_traces/2026-08-07-prefill-feasibility/CONSULT-RESPONSE.md:193-221,252-259",
        "recommended": "Explicitly label the projection an extrapolation from smaller-model scaling and say that no long-prompt 7B evidence exists."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": 244,
        "related_lines": [5, 141, 228],
        "title": "Artifact availability overstates both present release state and end-to-end binding",
        "failing_scenario": "A reader obtains a standalone floor/result artifact expecting the claimed cryptographic chain to authenticate its extraction widths and exact source membership, but the registered L1 boundary still requires governed extraction and consuming analysis in the same lead-controlled custody session. Archive locators are also still pending.",
        "source": "docs/phase_2/window_runbook.md:53-58; docs/paper/draft-v1.md:141; docs/contracts/capstone_scope.md:60-66",
        "recommended": "State the current L1 artifact boundary and make archive/reproduction availability conditional until locators and released evidence are actually available."
      },
      {
        "id": "F6",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": 230,
        "title": "The limitations section generalizes a one-stack result to an instrument class",
        "failing_scenario": "A reviewer cites the sentence as evidence that the powermetrics instrument class cannot support short-prompt effects generally, although one physical unit and named stack establish only a stack-specific operating domain.",
        "source": "docs/contracts/capstone_scope.md:44-46,108-120,155-172",
        "recommended": "Replace 'what this instrument class can support' with the named stack, boundary, and method instance."
      },
      {
        "id": "F7",
        "severity": "should_fix",
        "file": "docs/paper/draft-v1.md",
        "line": 5,
        "related_lines": [230],
        "title": "Universal LABELLED-path wording omits the sole-condition and terminal-refusal requirements",
        "failing_scenario": "A fresh floor cell has attribution dominance plus stale drift or missing calibration evidence. The draft's 'all/every floor' wording suggests LABELLED publication, but the contract allows the path only when attribution dominance is the sole condition and an exact corner-widened floor exists; every other refusal remains terminal.",
        "source": "docs/phase_2/detection_floor.md:75-84,115-121",
        "recommended": "Qualify that claim-ready attribution-limited floors use the LABELLED path only when the registered dominance condition is the sole condition; the label never rescues another refusal."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "set -eu; paper_path=docs/paper/draft-v1.md; test \"$(git rev-parse HEAD)\" = \"5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e\"; test \"$(git rev-parse '@{upstream}')\" = \"5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e\"; test -z \"$(git status --porcelain)\"; section7_text=$(sed -n '166,199p' \"$paper_path\"); if printf '%s\\n' \"$section7_text\" | rg -i '([0-9]+([.][0-9]+)?[[:space:]]*(j(oule(s)?)?|w(att(s)?)?)(/|\\b))' >/dev/null; then exit 1; fi; if rg '\\b(D|WO|C)-[0-9]{2,}\\b|\\bcouncil[- ]?(row|id)\\b' \"$paper_path\" >/dev/null; then exit 1; fi; test \"$(rg -c '^## [0-9]+\\.' \"$paper_path\")\" = 11; test \"$(rg -c '^## ([3-7]|10)\\..*\\(C-(i|ii|iii|iv|v|vi)\\)' \"$paper_path\")\" = 6; printf 'TARGET_EXACT 5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e\\nWORKTREE_UNCHANGED clean\\nDEMO_ENERGY_VALUE_SCAN none\\nINTERNAL_ID_SCAN none\\nSECTION_NUMBERING 1-through-11\\nCONTRIBUTION_SECTION_MAP 6-of-6\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "TARGET_EXACT 5e472e8f9c1e59d50ac55f820a61e5e6dd99ee9e",
          "WORKTREE_UNCHANGED clean",
          "DEMO_ENERGY_VALUE_SCAN none",
          "INTERNAL_ID_SCAN none",
          "SECTION_NUMBERING 1-through-11",
          "CONTRIBUTION_SECTION_MAP 6-of-6"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DEMO_ENERGY_VALUE_SCAN none\\nINTERNAL_ID_SCAN none\\nSECTION_NUMBERING 1-through-11\\nCONTRIBUTION_SECTION_MAP 6-of-6"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "set -eu; rg -Fq 'The attribution-limited path does not relax corpus soundness.' docs/phase_2/detection_floor.md; rg -Fq 'the project owes its readers, **not** a gate a claim must clear.' docs/decision_log.md; rg -Fq 'NO long-prompt 7B corpus' docs/process_traces/2026-08-07-prefill-feasibility/SYNTHESIS.md; rg -Fq 'Until FLOOR-BIND-01 closes' docs/phase_2/window_runbook.md; rg -Fq 'Single-unit data characterize named' docs/contracts/capstone_scope.md; rg -Fq 'n=2 of the planned n=3' docs/process_traces/2026-08-04-t3-char-pair/ANALYSIS-APPUP-R01R02.md; rg -Fq 'Calibration-bracket account omits the derived drift screen' docs/paper/draft-v1-review-round1.md; printf 'METHOD_CONTRACTS_INSPECTED detection_floor,window_runbook,capstone_scope\\nCUSTODIED_TRACES_INSPECTED sizing_synthesis,sizing_consult,idle_pair\\nPRIOR_REVIEW_DISCIPLINE_INSPECTED pass\\nSOURCE_CONFLICT_CHECK pass\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "METHOD_CONTRACTS_INSPECTED detection_floor,window_runbook,capstone_scope",
          "CUSTODIED_TRACES_INSPECTED sizing_synthesis,sizing_consult,idle_pair",
          "PRIOR_REVIEW_DISCIPLINE_INSPECTED pass",
          "SOURCE_CONFLICT_CHECK pass"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PRIOR_REVIEW_DISCIPLINE_INSPECTED pass\\nSOURCE_CONFLICT_CHECK pass"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The historical diagnostic calculations were not recomputed from raw run bundles; this audit checked the draft against the custodied synthesis and consult response.",
      "needs": "Re-run the desk-check extraction only if independent numerical reproduction is required."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "External literature, novelty, and bibliography assertions were outside this metrology/claims-boundary lens and were not independently source-verified.",
      "needs": "Retain the separate bibliography and novelty audit before submission."
    }
  ]
}
```

## Findings

### F1 — Blocker: Pending demonstration evidence is presented as achieved

At `docs/paper/draft-v1.md:5`, the abstract says “We demonstrate” two-model measurements and refusal behavior. Lines 168 and 248 likewise say the measurements “are collected” and that the instrument “resolves” and “must refuse” demonstrated effects.

That exceeds the evidence state: all result cells remain pending, while the sizing evidence is explicitly historical, diagnostic, and non-claim-bearing. The placeholder does not grammatically retract the completed empirical claim.

Failing scenario: a reviewer follows the abstract expecting issued two-model measurements and verdicts, but finds no populated value, interval, or re-issued result artifact. Recast these sentences prospectively until those artifacts exist.

### F2 — Blocker: The two-gate decision rule is collapsed into one summed threshold

At `docs/paper/draft-v1.md:172`, the statement that the composed interval “must clear the effective bar” is not the ratified rule. The table’s single “Effective bar” column at line 193 reinforces the error.

The uncertainty magnitudes do add when constructing a contrast interval. But acceptance uses two separate gates:

- The point effect must exceed the operative floor.
- The metrology-aware and decision intervals must support direction, with the other registered statistical gates satisfied.

`floor + claim-side bound` is a mandatory practical sizing disclosure, not a single acceptance threshold. For example, an 8 J estimate, 5 J floor, and 2 J claim-side bound could have a 6–10 J interval and pass the separate gates; requiring that interval to clear a 7 J summed bar would incorrectly refuse it.

### F3 — Blocker: §9 changes MARGINAL into below-bar and already refused

At `docs/paper/draft-v1.md:230`, the short-prompt prefill contrast is described as an effect below the bar that “is refused.” The source says something materially different: the diagnostic point is 5.809930 J against an approximate 5 J practical bar, while its composed interval extends below the bar. The verdict is therefore MARGINAL, not a demonstrated below-bar effect.

The faithful limitation is that historical non-claim evidence suggests insufficient clearance margin, motivating a prospective floors-only/decode-only default. No fresh refusal verdict has yet been issued. Line 248’s reference to “smaller” natural-workload contrasts repeats the same error.

### F4 — Should-fix: The projection’s missing 7B evidence is not disclosed

Line 176 correctly calls the longer-prompt result “projected,” identifies scaling evidence only for the smaller model, and states that resizing changes the estimand. It does not explicitly disclose the decisive evidence gap: no historical 7B corpus uses more than 128 prompt tokens.

Failing scenario: a reader treats the roughly twice-bar projection as an interpolation supported for both models. The paper should call it an extrapolation and state that a longer-prompt arm would be the first direct 7B check.

### F5 — Should-fix: Artifact availability exceeds the current binding and release state

At `docs/paper/draft-v1.md:244`, the claim that every number is cryptographically bound through the full chain conflicts with the registered L1 boundary already acknowledged at line 141. Until the floor-binding work closes, claim-bearing use requires the floor to come from governed extraction in the same lead-controlled custody session as the consuming analysis; a standalone floor artifact does not independently authenticate that complete relation.

The repository/archive locator is also still pending. The tool can be described as open, but the demonstration evidence chain should not be described as presently open and independently re-reducible until the archive is released and the current binding limitation is stated.

### F6 — Should-fix: One-stack evidence is generalized to an instrument class

Line 230 calls the refusal a finding about “what this instrument class can support.” That is broader than the capstone contract permits. One physical unit supports conclusions about the named machine, software stack, boundary, and measurement configuration—not the `powermetrics` instrument class generally.

Failing scenario: the sentence is cited as a class-wide detection-limit result for Apple software counters. Replace it with stack-specific language.

### F7 — Should-fix: LABELLED-path wording omits its admission conditions

The abstract says “All floors” are labelled, and §9 says “Every floor” uses that path. The governing design permits LABELLED publication only when attribution dominance is the sole registered condition and the exact corner-widened floor exists. Any additional refusal remains terminal.

Failing scenario: a fresh cell has attribution dominance plus stale drift evidence. The current prose implies that labelling licenses publication, while the contract requires refusal. Qualify the statement and explicitly say that LABELLED never rescues another admission failure.

Checks performed: the checkout and upstream are exact and clean; §7 contains no demonstration energy value; no numeric decision, work-order, or council ID appears in the draft; sections number cleanly from 1 through 11; all six contribution labels map to real sections; and §7’s references to §§8 and 9 are correct. The §9 idle-floor paragraph is faithful to the source’s two permanently non-claim captures, low-but-bursty framing, steady-part subtraction, and zero-agent claim-window rule. No prompt characterization contradicted its source.

## Residual risk

This review did not recompute the historical diagnostic values from raw run bundles; it relied on the custodied synthesis and consult response. External literature and novelty assertions also remain outside this lens and need their separate audit.