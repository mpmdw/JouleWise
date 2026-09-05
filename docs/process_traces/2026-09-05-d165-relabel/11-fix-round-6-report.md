```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "NEEDS_RULING: census widened; seven checks GREEN, census RED on six lines rather than the requested two.",
  "workspace": {
    "base_requested": "267630cf",
    "base_mode": "exact",
    "head_start": "267630cf7c25599267680d3ad1506a4ead241b24",
    "head_end": "267630cf7c25599267680d3ad1506a4ead241b24",
    "upstream_end": "267630cf7c25599267680d3ad1506a4ead241b24",
    "branch": "feat/2026-09-05-d165-relabel"
  },
  "pathspec": [
    "tests/test_d165_rationale_census.py",
    "tests/fixtures/d165_rationale_allowlist.json",
    "docs/process_traces/2026-09-05-d165-relabel/11-fix-round-6-report.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_d165_rationale_census",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 3.248s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_d165_rationale_census",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "docs/paper/draft-v2-skeleton.md:29: moved together",
          "docs/paper/draft-v2-skeleton.md:1387: moved together",
          "docs/paper/draft-v2-skeleton.md:1738: timing error common to",
          "docs/paper/round7/retensing-plan.md:143: shared timing error",
          "docs/paper/round7/retensing-plan.md:333: shared timing error",
          "docs/paper/round7/retensing-plan.md:335: shared timing error",
          "",
          "----------------------------------------------------------------------",
          "Ran 8 tests in 7.461s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "docs/paper/draft-v2-skeleton\\.md:29: moved together\\ndocs/paper/draft-v2-skeleton\\.md:1387: moved together\\n\\n-+\\nRan 8 tests"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: requested variants also expose draft-v2:1738 and retensing-plan:143/333/335. None is within the existing explicit historical marker boundaries; none is a corrected denial or unrelated caption. The requested RED-only-two acceptance cannot be reported truthfully.",
      "needs": "Rule on correction or explicit bounded supersession of the four additional occurrences, retaining their detection until cured. Lead owns the paper edits; no scope expansion was assumed."
    }
  ]
}
```

## Change

Widened the census from five to twelve candidates: all six requested physical-timing variants plus the literal v1 replay rule. Word boundaries prevent incidental matches such as “common timeline.” Whitespace folding and decoded adjacent Python literals remain covered. Bare active v1 citations are detected even alongside v2; reviewed historical declarations/citations require exact retention entries.

The existing case-sensitive line, paragraph, and paired-block marker rules are unchanged. Removed the draft-v1 file exclusion so its Figure-2 caption is retained by an exact key. Process traces remain outside the five consumer roots.

The allowlist now contains 35 individually reasoned path/line/phrase entries (four preserved, 31 added): corrected code/contract/campaign/registry/checklist denials, both Figure-2 ABBA captions, historical v1 compatibility declarations/citations, and explicitly SUPERSEDED round7 paragraphs. Python AST attribution uses the string's starting line, so the brief's core :63/:602 locators resolve at this HEAD to :65/:606; the physical phrase text appears at :66/:609. No paper, production, registry, or campaign source was edited.

M0: clean exact requested HEAD; no active stop card; explicit FIX-seat direction selects A152/D165-RELABEL-01 in the AGENT lane. Read the binding D1 delta and D-165 addendum. Only the exhaustive three-path write scope was used. No discovery suite, other test module, agent launcher, hardware work, or commit.

## Verification notes

**Actual state: seven tests GREEN; one census test RED with six active occurrences. It is not RED only because of the two requested draft lines.** V1 is the pre-change baseline; V2 is the final focused module. Its expected tail records the requested two-line condition, which the observed output does not meet.

Exact RED tail:
```text
docs/paper/draft-v2-skeleton.md:29: moved together
docs/paper/draft-v2-skeleton.md:1387: moved together
docs/paper/draft-v2-skeleton.md:1738: timing error common to
docs/paper/round7/retensing-plan.md:143: shared timing error
docs/paper/round7/retensing-plan.md:333: shared timing error
docs/paper/round7/retensing-plan.md:335: shared timing error

----------------------------------------------------------------------
Ran 8 tests in 7.461s

FAILED (failures=1)
```

The seven passing tests cover exact reasoned allowlist validity, literal/whitespace detection, active v1 authority (including beside v2), unchanged marker boundaries, and frozen-draft inclusion. The no-blanket-exemption check proves an allowed caption cannot suppress a different line, phrase, or path, and rejects wildcard paths, stale keys, duplicate entries, empty reasons, and unlisted marked occurrences. All six RED keys remain unallowlisted.

**NEEDS_RULING**

- **Question:** Should the four additional unmarked hits be corrected or explicitly superseded by the lead before the requested two-line RED acceptance is retried?
- **Options considered:** (1) Keep the widened detection and route the four extra consumers to a lead-owned cure; (2) treat those four occurrences as legitimate retained history and allowlist them without existing bounded markers. Option 2 would require a ruling that changes the present marker/retention requirement and is not assumed.
- **Recommendation:** Option 1. Draft-v2 :1738 describes one physical timing error moving across four runs. Retensing-plan :143 asserts doubled bounds under shared timing error; :333/:335 retain the timing-error cancellation rationale. These are neither corrected denials nor unrelated captions. The retensing plan's PARKED header is not a SUPERSEDED/LEGACY marker and cannot exempt the file.
- **Completed:** Widening, legitimate exact retentions, regression checks, and observed RED evidence.
- **Blocked work:** Acceptance of “RED only because of :29 and :1387.” Per AGENTS.md, blocking spec/authority conflicts require a NEEDS_RULING early return. This seat neither edits the draft nor silently legitimizes the four extra occurrences.

## Residual risk

The census is a phrase-based guard, not a semantic proof against all possible paraphrases. Exact path/line/phrase retentions do not fingerprint surrounding prose. The lead owns final review and integration, including the paper-K cure after main is merged. Next exact step: adjudicate F1, cure or explicitly supersede the additional consumers in their owning lane, then rerun `python3 -B -m unittest -v tests.test_d165_rationale_census` and refresh exact locators after integration.

