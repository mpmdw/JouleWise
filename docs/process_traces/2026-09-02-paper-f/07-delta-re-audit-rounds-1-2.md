# Delta re-audit of fix rounds 1+2 at a59c8863 (terra xhigh, direct run), verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All eight original blockers and all should-fixes are closed, but a new §3 supplier-set blocker makes this head NOT LANDABLE.",
  "workspace": {
    "base_requested": "a4fcc7ac",
    "base_mode": "exact",
    "head_start": "a59c886334b9361850e0490bf976e9c1eb12636f",
    "head_end": "a59c886334b9361850e0490bf976e9c1eb12636f",
    "upstream_end": "a59c886334b9361850e0490bf976e9c1eb12636f",
    "branch": "feat/2026-09-02-paper-f"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "NOT LANDABLE",
    "findings": [
      {
        "id": "B9",
        "severity": "blocker",
        "title": "§3's two remaining table rows cannot be shown to be exactly the V5 data-producing supplier set.",
        "evidence": "The V5 registry says every characterization token has a producing field (results-fill-registry.md:400-431). It supplies MEASURED fields for workload response/linearity (441-442), identical-condition null (444), phase accounting (447-448), and drift/recovery (450-451), while draft §3's table retains only phase accounting and drift/recovery (375-376).",
        "impact": "The round-2 selection criterion is unproved by its named authority; either the table omits supplier-backed rows or the registry lacks the transaction-membership predicate needed to justify excluding them.",
        "needs": "Lead ruling plus one authoritative V5 collection-membership source: restore the omitted rows if all producing fields qualify, or bind an explicit transaction-specific exclusion for linearity/null."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".............", "Ran 13 tests in 2.744s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PAPER_FIRST_USE_DRAFT=docs/paper/draft-v2-skeleton.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger.PaperFirstUseLedgerTests.test_required_gloss_is_present_by_first_use_paragraph",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.098s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PAPER_FIRST_USE_DRAFT=/private/tmp/paper-f-reaudit.dmRhX0/fixture-main.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger.PaperFirstUseLedgerTests.test_required_gloss_is_present_by_first_use_paragraph",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["First extra element 0:", "'Apple M3 Max / 128 GB unified memory: required ledger row is missing'", "Ran 1 test in 0.022s", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PAPER_FIRST_USE_DRAFT=/private/tmp/paper-f-reaudit.dmRhX0/draft-cure14-reverted.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger.PaperFirstUseLedgerTests.test_required_gloss_is_present_by_first_use_paragraph",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["sampling flags / cadence ratio: first-use paragraph (line 356) is missing defining words", "Ran 1 test in 0.100s", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "sampling flags / cadence ratio.*FAILED \\(failures=1\\)"
      }
    }
  ],
  "flags": []
}
```

## Findings

| Severity | ID | Evidence |
|---|---|---|
| blocker | B9 | Registry V5 characterization fields cover linearity/null as well as phase/drift, but the table retains only phase/drift. The claimed exact supplier selection cannot be confirmed from the named registry. |

| Original finding | Result | Landed evidence |
|---|---|---|
| 02 B1 | Closed | Draft 356–362 restores cadence conditions/constants; `reduce.py` 116–118, 983–988 matches. |
| 02 B2 | Closed | Draft 177 matches manifest verification (`reduce.py` 1219–1256), reservation-plan pins (`calibration_ledger.py` 4626–4646), and acceptance registry (`calibration_bracketing.py` 727–745). |
| 03 P-B1 / 02 S1 | Closed | Figure 3 prose, embed, and caption at draft 887–900. |
| 03 P-B2 / 02 S2 | Closed as prose/anchor repair | Four-question framing and method-only relocation at 238–276; anchors retained; table at 375–376. Superseded by new B9 supplier-set issue. |
| 03 P-B3 | Closed | Entry-check and admitted definitions at 187–190. |
| 03 P-B4 | Closed | Plain check descriptions at 179; Appendix A.3.5/.6/.7 are correctly cited. |
| 03 P-B5 | Closed | Interpolation-edge construction at 844–850. |
| 03 P-B6 | Closed | Paragraph joining/line map at test 264–300; regression forms at 519–549. |
| 02 S3 | Closed | Independent and shared numerators separated at 122–134. |
| 02 S4 | Closed | Gloss binding, exact-main fixture, and deletion mutations at test 346–368 and 551–594. |
| 03 P-S1/P-S2/P-S3/P-S4 | Closed | Block precedes member use (129–131); widening-factor purpose (441–442); split cell definition (118–120); derivational/dash/modifier matching tests. |

| Check | Result |
|---|---|
| Reader-order first-use scan | 37 changed diff hunks; 46 ledger first uses in changed locations; all at declared homes; zero gloss failures. |
| Protected regions vs `33290b8b` | Abstract 23–80, §6, §7 “What the finding changes,” and §10 are byte-identical. The report-named Abstract `named-counter` wording is unchanged, so no exception was used. |
| Fixture directions | Current draft passes; exact-main fixture fails as required. |
| Cure-14 mutation | Reverting the cadence cure only in `/private/tmp` fails on the required cadence-ratio gloss. |

## Residual risk

Figure 3’s Markdown embed and SVG source were inspected, but no rendered-PDF visual pass was run. No checkout files were modified.