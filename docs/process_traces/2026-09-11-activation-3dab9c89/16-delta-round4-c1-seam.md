```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "S3 CURED. No factual correction is needed; the parenthesis changes no fact. One required formatting check fails: line 515 is 117 columns. All 98 tests pass.",
  "workspace": {
    "base_requested": "7fc058b9",
    "base_mode": "descendant",
    "head_start": "d8cf309a813e5d58d49d4cdb9451b620e24203b0",
    "head_end": "d8cf309a813e5d58d49d4cdb9451b620e24203b0",
    "upstream_end": "d8cf309a813e5d58d49d4cdb9451b620e24203b0",
    "branch": "fix/2026-09-11-c1-registration-seam"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGEABLE AFTER FIXES",
    "same_signature": "S3 CURED: the first-use explanation class from rounds 2 and 3 no longer survives.",
    "findings": [
      {
        "id": "S4",
        "severity": "should_fix",
        "path": "docs/phase_2/derivation_night_runbook.md",
        "line": 515,
        "summary": "The parenthesis rewording leaves a 117-column line, violating the requested 79-column limit."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_gen_derivation_night tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 98 tests in 51.219s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 98 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "other",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 scripts/gen_derivation_night.py --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS generated derivation-night wrapper region matches"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS generated derivation-night wrapper region matches"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check 7fc058b9..HEAD",
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
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "diff -u /tmp/pr322-consult-q4.txt /tmp/pr322-head-paragraph.txt",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "+ledger sessions a derivation corpus is drawn from.) A receipt class is the plan's category, and it selects which gate",
          " checks apply; this night's is `DIAGNOSTIC_NO_PACK`, the class for a night",
          " that launches no measurement pack — no campaign's committed bundle of runs,",
          " pinned in a plan by id, root and digest — because this night takes only the"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "python3 -B -c 'from pathlib import Path; lines=Path(\"/tmp/pr322-head-paragraph.txt\").read_text().splitlines(); bad=[(503+i,len(s)) for i,s in enumerate(lines) if len(s)>79]; print(\"Lines over 79:\",bad); raise SystemExit(bool(bad))'",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Lines over 79: [(515, 117)]"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Lines over 79: \\[\\]"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --porcelain",
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
  "flags": []
}
```

**Same-signature: S3 CURED — the first-use explanation class from rounds 2 and 3 no longer survives.**

## Findings

**S4 — SHOULD_FIX — `docs/phase_2/derivation_night_runbook.md:515`: 117 columns exceeds the required 79.**

The paragraph has 21 lines; only line 515 fails. V5’s command returns:

```text
Lines over 79: [(515, 117)]
```

Replace that single line with these two lines, preserving every word:

```text
ledger sessions a derivation corpus is drawn from.) A receipt class is the
plan's category, and it selects which gate
```

No BLOCKER or additional SHOULD_FIX/NIT finding.

**Byte comparison**

I extracted consult 15 §Q4’s fenced text and the committed paragraph directly from `git show HEAD:docs/phase_2/derivation_night_runbook.md`, preserving bytes, into the two `/tmp` files named in V4.

They are **not byte-identical**. `diff -u` returns 1 with this sole hunk:

```diff
@@ -7,10 +7,10 @@
 class and checks exactly one thing, recorded as gate condition C1: it reads
 the file as UTF-8 text and requires the SHA-256 of that text to equal the
 literal `night_gate.D166_REGISTRATION_SHA256` in the same module. Nothing
-else about the file is read. (Beware one word collision: `registration_path`
-and C1's "registration" are the gate's own names for THIS file, not §Terms'
-**Registration**, the set of ledger sessions a derivation corpus is drawn
-from.) A receipt class is the plan's category, and it selects which gate
+else about the file is read. (Beware one word collision: the plan's
+`registration_path` — the D-166 literal above — and C1's "registration" are
+the gate's own names for THIS file, not §Terms' **Registration**, the set of
+ledger sessions a derivation corpus is drawn from.) A receipt class is the plan's category, and it selects which gate
 checks apply; this night's is `DIAGNOSTIC_NO_PACK`, the class for a night
 that launches no measurement pack — no campaign's committed bundle of runs,
 pinned in a plan by id, root and digest — because this night takes only the
```

The only wording additions are **“the plan’s”** and **“— the D-166 literal above —”**; the remaining differences are wrapping. **The lead’s rewording changes no fact.** Lines 500–502 already identify that plan field and literal.

**Independent factual verification**

Primary inspection commands included:

```sh
nl -ba joulewise/night_gate.py | sed -n '30,42p;120,138p;428,457p;530,555p;1295,1330p'
nl -ba scripts/run_night.py | sed -n '287,298p'
rg -n 'D-165|D-166' docs/decision_log.md
nl -ba docs/decision_log.md | sed -n '10728,10772p;11270,11305p'
nl -ba configs/campaigns/d117_contrast_v5/generate_configs.py | sed -n '1,4p;525,540p'
nl -ba configs/calibration/preregistration_d079_epoch_25g83_rev1.md | sed -n '355,370p'
nl -ba scripts/issue_calibration_acceptance_generation.py | sed -n '1168,1182p'
```

| Claim | Primary evidence and result |
|---|---|
| Separate D-117 experiment; D-165 comparison rule fixed before collection | Generator `:2` identifies the D-117 contrast pack; `:526` says “the frozen D-165 ratio and common-mode replay contract.” Decision-log D-165 index `:211` and entry `:10733–10734` establish prospective registration. **Supported.** |
| Filename names D-166, which set the workload | `night_gate.py:40` supplies the filename. Decision-log D-166 `:10751–10758` sets the workload; its dated addendum `:11290–11305` amends the prompt. **Supported.** |
| C1 reads UTF-8 text, hashes it, compares the constant, and does not evaluate the rule | `night_gate.py:1302–1307` calls `read_text` then hashes `.encode("utf-8")`; `:1315–1328` compares the constant and marks C1. Production `read_text(encoding="utf-8")` is now at **`scripts/run_night.py:296`**, one line after the supplied pointer. No rule parsing occurs. **Supported.** |
| Receipt class selects applicable checks | `_initial_conditions`, `night_gate.py:536–543`, selects `class_table()[receipt_class]`. The diagnostic class makes only C2 not applicable. **Supported.** |
| Pack is a committed bundle identified by id, root and digest | Runbook `:374` identifies the frozen campaign pack and committed capture plan; `_PACK_NIGHT_KEYS`, `night_gate.py:128–131`, contains `pack_id`, `pack_root`, and `pack_sha256`. **Supported.** |
| This night has no measurement pack and takes twelve calibration captures | Runbook §1.1 `:770–797` specifies no pack. Its `:1062` sets `SLOT_COUNT=12`; `:1064` says “then twelve captures.” Pre-registration revision 2 `:360–369` independently specifies twelve slots and `DIAGNOSTIC_NO_PACK`. **Supported as the planned schedule**, with unused-slot handling already stated at runbook `:140–142`. |
| Gate registration differs from §Terms’ Registration | Runbook `:150–155` defines the latter as the declared set of ledger sessions. The parenthesis correctly distinguishes the file. **Supported.** |
| Scientific pre-registration is separately bound by H and its recorded digest | Runbook `:243–247`, `:496–497`, `:544–555`, and §1.5 `:1433` specify those bindings. Issuer `:1171–1181` independently hashes the pre-registration bytes and refuses mismatch. **Supported.** |

Directly hashing the registration using the production text-reading operation returned:

```text
text SHA-256: dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265
matches C1 constant: True
DIAGNOSTIC_NO_PACK: {'C1': ('PASS', None), 'C2': ('NOT_APPLICABLE', 'no_pack_by_design'), 'C3': ('PASS', None), 'C4': ('PASS', None), 'C5': ('PASS', None)}
```

No wrong or unsupported paragraph claim requires a dictated factual replacement.

**First-use census**

Line references below are in the runbook.

| Term or reference | Earlier construction or inline explanation |
|---|---|
| D-117 contrast campaign; D-165; D-166/workload | `:503–507`: different experiment, comparison-rule decision, and workload-setting decision. |
| Night gate; C1 | Gate introduced `:11–12`; C1’s exact operation supplied inline `:508–511`. |
| SHA-256/digest; UTF-8 text | Digest gloss `:14`; `:510` explicitly specifies the text-reading format and hashing operation. |
| `night_gate` module and constants; `registration_path` | `:500–502` identifies the module, field and path; `:511–514` identifies the digest constant and disambiguates the field. |
| Registration; ledger sessions; derivation corpus | `:143–155` and `:172–174`; the collision is explicitly resolved at `:512–515`. |
| Plan; receipt class; `DIAGNOSTIC_NO_PACK` | Plan’s role established `:53–56`, `:191–194`, `:243–247`; category and class explained inline `:515–519`. |
| Measurement pack; committed bundle; id/root/digest | Inline bundle-and-identity gloss `:517–518`, supported by earlier committed-file and directory context `:187–197`, `:374`. |
| Calibration captures; scientific pre-registration | Purpose and before-data rule built at `:107–136`; twelve captures already specified `:118–123`. |
| H; measurement commit; tree; pin | Committed-file identity `:187–189`, exact H binding `:243–247`, and inline explanation `:521–522`. |
| “the file named at the top of this section” | **Correct:** first content line of §0.5, `:496`, quoted below. |

```text
496  `configs/calibration/preregistration_d079_epoch_25g83_rev1.md` must be
```

No first-use failure remains. The earlier scientific vocabulary is removed, the pack gloss is corrected, and the Registration collision is explicit.

## Residual risk

This was a documentation delta review with the requested 98 focused tests; the full repository suite and live hardware checks were not run. No repository files changed, and HEAD/upstream remained `d8cf309a` with a clean worktree.

Next exact step: the lead wraps line 515, checks the resulting diff, and performs final verification.

VERDICT: MERGEABLE AFTER FIXES