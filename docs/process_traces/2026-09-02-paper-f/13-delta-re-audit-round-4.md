# Delta re-audit of fix round 4 at 2e455f78 (terra xhigh, direct run), verbatim

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "HEAD is exactly 2e455f78; six counter-findings close, but global TeX spelling and Figure 3 gate naming leave this NOT LANDABLE.",
  "workspace": {
    "base_requested": "225afb0c",
    "base_mode": "exact",
    "head_start": "2e455f786e1323ac15c60540f4d0416b7426be94",
    "head_end": "2e455f786e1323ac15c60540f4d0416b7426be94",
    "upstream_end": "2e455f786e1323ac15c60540f4d0416b7426be94",
    "branch": "feat/2026-09-02-paper-f"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "overall": "NOT LANDABLE",
    "findings": [
      {
        "id": "SF3",
        "severity": "should_fix",
        "title": "The requested single TeX roman-macro spelling is not document-wide.",
        "evidence": "Target-paper grep finds 4 \\rm uses and 67 \\mathrm uses. The repaired U symbols are uniform, but draft lines 285, 295, and 329 retain \\rm.",
        "impact": "The literal one-spelling acceptance criterion fails.",
        "needs": "Replace the four residual \\rm spellings with \\mathrm, or explicitly narrow the criterion to the U symbols."
      },
      {
        "id": "SF4",
        "severity": "should_fix",
        "title": "Figure 3 still assigns the final Gate 1 threshold the pre-safeguard name.",
        "evidence": "§1 assigns detection floor before safeguards and cell floor to the final gate; §4 lines 824-826 gates on F_cell/cell floor. The changed lead-in at line 881 agrees, but the SVG desc/text and printed caption at line 887 still say Gate 1 exceeds the cell's detection floor. The SVG is unchanged in 225afb0c..HEAD.",
        "impact": "One gate has conflicting reader-facing names, so counter-review finding 4 is incomplete.",
        "needs": "Rename Gate 1 and its figure prose/caption to cell floor; retain detection floor only for the pre-safeguard bound."
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
        "tail": [".............", "Ran 13 tests in 3.296s", "OK"]
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
        "tail": ["Ran 1 test in 0.121s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PAPER_FIRST_USE_DRAFT=tests/fixtures/paper_first_use_pre_cure.md PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger.PaperFirstUseLedgerTests.test_required_gloss_is_present_by_first_use_paragraph",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": ["Ran 1 test in 0.026s", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    }
  ],
  "flags": []
}
```

## Findings

| Severity | ID | Evidence |
|---|---|---|
| should_fix | SF3 | `\rm` remains four times in §3; the repaired §1/§4 \(U\) spellings are uniformly `\mathrm`. |
| should_fix | SF4 | The Figure 3 lead-in is repaired, but SVG and caption Gate 1 prose still say “detection floor,” contrary to the §1/§4 stage assignment. |

| Counter finding | Result | Evidence |
|---|---|---|
| 1 | Closed | §1: “evaluated jointly and the largest result retained.” §4: “enumerate every joint choice… Retain the largest result.” Same selection rule. |
| 2 | Closed | Preamble says no varying output length/no such measurements; §3 cell says every output is 512 and supplies no output-length-fit inputs. Generator lines 579, 817, 837 all set 512. |
| 3 | Not closed | SF3. |
| 4 | Not closed | SF4. |
| 5 | Closed | §4 lines 703–706 no longer bold the §1 first-use terms. |
| 6 | Closed | First gloss, ledger, lexicon, and requirement all use “macOS `powermetrics` is the power sampler used here.” |
| 7 | Closed | Generator stages 590–612 are decode-512 and prefill-p512 null blocks; §3 now states one magnitude per arm. |
| 8 | Closed | “Under the current mint” matches `reduce.py`’s `strict_physics` current-mint gate and preserved replay-arm behavior. |

| Check | Result |
|---|---|
| Reader-order changed prose | All changed sentence groups pass the ledger scan; new `mint` is same-sentence glossed, and §3 terms are built/defined in their rows. |
| Protected regions vs `33290b8b` | Abstract 23–80, §6 printed negative result, §7 “What the finding changes,” and §10 are byte-identical. |
| Signature comparison | SF3/SF4 are the same macro/stage-name signatures raised in `11`; `02/03/07` do not resolve the remaining Figure 3 terminology mismatch. |
| Workspace | Clean; no files modified by this audit. |

## Residual risk

No rendered-PDF inspection was run; Figure 3 terminology was checked from Markdown and SVG source.