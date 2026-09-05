```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The repeated masking signature is caused by treating redundant human Markdown projections as a machine contract; re-scope the mission and retire the bespoke parser gate.",
  "workspace": {
    "base_requested": "4159fa16ecea86b6986b983a5c6ace4f72d8663c",
    "base_mode": "exact",
    "head_start": "4159fa16ecea86b6986b983a5c6ace4f72d8663c",
    "head_end": "4159fa16ecea86b6986b983a5c6ace4f72d8663c",
    "upstream_end": "4159fa16ecea86b6986b983a5c6ace4f72d8663c",
    "branch": "feat/2026-09-04-fan-p1-rows"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/p1-rows/06-consult-sol-structural.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "recommendation": "RE-SCOPE",
    "threat_model": "operator-only maintainability check",
    "findings": [
      {
        "id": "P1S-1",
        "severity": "should_fix",
        "location": "tests/test_phase1_row_dispositions.py:25-69",
        "text": "The landing tries to establish semantic uniqueness over redundant, deliberately flexible Markdown with lossy ad hoc parsers; stricter parsing would deepen an operator-only gate without protecting physics, evidence custody, pre-registration, or live promotion."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "4159fa16ecea86b6986b983a5c6ace4f72d8663c",
          "## feat/2026-09-04-fan-p1-rows...origin/feat/2026-09-04-fan-p1-rows"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "feat/2026-09-04-fan-p1-rows\\.\\.\\.origin/feat/2026-09-04-fan-p1-rows$"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/p1-rows/06-consult-sol-structural.md\"); lines=p.read_text(encoding=\"utf-8\").splitlines(); fence=chr(96)*3; assert lines[0] == fence+\"json\"; end=lines.index(fence,1); b=(\"\\n\".join(lines[1:end])+\"\\n\").encode(\"utf-8\"); obj=json.loads(b); assert len(b)<=8192; assert obj[\"schema\"]==\"claude-codex-report/v1\"; assert obj[\"genre\"]==\"review\"; assert obj[\"completion\"]==\"complete\"; print(\"report-envelope-ok\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report-envelope-ok"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report-envelope-ok$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "test \"$(git status --short)\" = \"?? docs/process_traces/2026-09-04-fanout/p1-rows/06-consult-sol-structural.md\" && echo scope-ok",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "scope-ok"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^scope-ok$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "This consult disagrees with the strict-parser cure proposed by the stopped seat and with treating the remaining parser counterfactuals as landing blockers.",
      "needs": "Adopt the Q4 re-scope row before resuming the landing."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No executable cure was authorized or applied, so the proposed acceptance command was not run.",
      "needs": "Run the single Q3 acceptance command on the re-scoped landing."
    }
  ]
}
```

## Findings

**Q1 — Structural cause (P1S-1).** The repeated signature is self-created: one human-authored disposition is projected into the `Still required` list, the Evidence Matrix, and narrative sections (`docs/phase_1/phase_1_exit_checklist.md:28-36,51-65,83-98,184-193,261-271,372-401`), then tests pretend those redundant Markdown renderings form a machine contract. The original assertions cover only narrative phrases (`tests/test_phase1_row_dispositions.py:71-94`); round 1 added `_first_paragraph_after`, which discards everything after the next blank line (`:25-31`), and `_matrix_statuses`, which silently applies last-write-wins (`:34-42`), before exact assertions at `:50-69`. Each re-audit therefore finds another legal Markdown spelling outside an unstated grammar; the structural fault is neither insufficient counterexamples nor two isolated helper bugs, but attempting exhaustive semantic proof over flexible prose with no canonical schema or machine consumer.

**Q2 — Threat model.** This class is an **operator-only maintainability check and should be removed as a blocking gate**, not promoted into stricter fail-closed machinery. The injected blank paragraph and duplicate prose-table row can confuse a reader, but they do not mutate raw evidence, physics arithmetic, pre-registration, claim artifacts, or the separate live-promotion gate; the checklist itself explicitly leaves acquisition and promotion elsewhere (`docs/phase_1/phase_1_exit_checklist.md:32-36,184-190,372-401`). D-161 keeps fail-closed handling for evidence/tool mistakes but prefers retirement where there is no consumer and explicitly retires prose tripwires (`docs/decision_log.md:10390-10401`; `docs/process_traces/2026-08-27-t26/threat-model-prune/04-MAGISTRATE-RULING.md:8-16,35-51`); a duplicate Markdown label is not the duplicate evidence key/slot/id contemplated there.

**Q3 — Cure.** **RE-SCOPE the mission** to a source-reviewed documentation reconciliation: keep the source-supported checklist corrections and the ruled P1-008-to-ED-DATES-01 split, remove the bespoke `test_phase1_row_dispositions` gate, and stop representing its green result as semantic proof. The protected kernel/queue, D-091/D-092, and the live-promotion contracts remain authoritative; the checklist is a human-readable evidence pointer whose drift is handled by ordinary review and non-blocking documentation hygiene. The one acceptance command is `base=$(git merge-base origin/main HEAD); test -z "$(git diff --name-only "$base"..HEAD -- tests)" && python3 -m unittest tests.test_docs_freshness`: it proves that the landing adds no bespoke prose-enforcement test while still satisfying the repository's general documentation checks.

**Q4 — Magistrate row (verbatim).** `| p1-rows | RE-SCOPE as a documentation reconciliation: retain the source-supported checklist corrections and the ruled P1-008 to ED-DATES-01 split, but remove the bespoke Phase 1 row-disposition test module. Under D-161, formatting variants and duplicate rows in a human-maintained Markdown status projection are maintainability concerns, not physics, evidence, or pre-registration fences, and must not block landing. Accept after source review against D-091, D-092, the P1-004/P1-006 blocker authorities, and the live-promotion gate, with the ordinary docs-freshness check green. |`

## Residual risk

The human-readable checklist can later drift from the protected state projection; this design accepts that as review-time maintainability risk rather than claim-bearing instrument risk. No cure or tests were run because the exhaustive write scope authorizes only this consult report.
