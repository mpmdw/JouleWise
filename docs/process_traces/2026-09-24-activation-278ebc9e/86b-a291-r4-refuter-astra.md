```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The legal corpus and all 71 existing tests pass; the original m3 kill is impossible on this corpus, and two instructions need clarification.",
  "workspace": {
    "base_requested": "24ff94cb96329c1725d72910658090c2070b5e07",
    "base_mode": "exact",
    "head_start": "24ff94cb96329c1725d72910658090c2070b5e07",
    "head_end": "24ff94cb96329c1725d72910658090c2070b5e07",
    "upstream_end": "24ff94cb96329c1725d72910658090c2070b5e07",
    "branch": "test/2026-09-24-a291-ownership-harness"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "R4-5(3)",
        "text": "Original m3 survives both mandated tests, including the clarified superseded-holder witness. The retained count clause already rejects a registered terminal item in any live holder."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "location": "R4-3(4)",
        "text": "The phrase 'in the same envelope' is ambiguous. The parent-envelope reading produces an unchanged B1 with counts violations; the listing-local reading produces the required superseded_live witness."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "location": "R4-4",
        "text": "P's exact read allowlist omits joulewise/scored_packer.py and tests/test_scored_packer.py, which R4-2 requires P to edit."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_ownership_forgery",
      "cwd": "/tmp/278ebc9e/r4ref/baseline",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          ".LEGAL_SEAL accepted=1868 refused=0 first=[]",
          "Ran 7 tests in 632.197s",
          "FAILED (failures=4)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=3\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B listing_local_probe.py",
      "cwd": "/tmp/278ebc9e/r4ref/baseline",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.305s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B mutation_probe.py",
      "cwd": "/tmp/278ebc9e/r4ref/predicate",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "{\"mutant\": \"m3\", \"tests\": 2, \"failures\": 0, \"errors\": 0, \"killed\": false}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"mutant\": \"m3\".*\"killed\": true"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B replacement_mutation_probe.py",
      "cwd": "/tmp/278ebc9e/r4ref/predicate",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{\"mutant\": \"m3-term\", \"tests\": 2, \"failures\": 1, \"errors\": 0, \"killed\": true}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"mutant\": \"m3-term\".*\"killed\": true"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_registration tests.test_scored_roster_checker tests.test_scored_packer tests.test_scored_packer_fuzz tests.test_scored_packer_stress",
      "cwd": "/tmp/278ebc9e/r4ref/predicate",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 71 tests in 1143.532s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 -B m3_listing_local_probe.py",
      "cwd": "/tmp/278ebc9e/r4ref/predicate",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.257s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "python3 -B constructor.py",
      "cwd": "/tmp/278ebc9e/r4ref/forger-sandbox",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["NO_TESTS_CONSTRUCTOR seal=accepted"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "seal=accepted"
      }
    },
    {
      "id": "V8",
      "kind": "smoke",
      "cmd": "python3 -B adjudicate_saved.py",
      "cwd": "/tmp/278ebc9e/r4ref/predicate",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "NO_TESTS_ADJUDICATION oracle=[] rows=['INV-12', 'INV-32', 'INV-38']",
          "NO_TESTS_ADJUDICATION verdict=ESCAPE"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "verdict=ESCAPE"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "R4-5 cannot pass with the mandatory original m3 kill.",
      "needs": "Replace m3 with the executed terminal-multiplicity mutant specified in F1."
    },
    {
      "id": "G2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Results concern scratch reconstructions, not K/P's eventual integrated head. No independent forger seat or full repository suite was run.",
      "needs": ""
    }
  ]
}
```

## Findings

References: [Final texts A291-R4](/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/85-a291-final-texts-r4.md).

| ID | Severity | Finding and executed evidence | Exact replacement text |
|---|---|---|---|
| F1 | **BLOCKER** | R4-5(3)’s original m3 survives both mandated tests. Every terminal item in a live holder already has `LIVE ≥ 1, TERM ≥ 1`, violating the retained count clause. Correcting the superseded witness does not kill m3 either. | Replace **“m3 terminal-item-in-holder clause removed”** with **“m3 `term` overwritten instead of appended when building `_ownership`, retaining only the last entry for each `(model, item)`”**. This replacement was killed by **276 pairwise escapes**, preserving the five-kill gate. |
| F2 | **MATERIAL** | R4-3(4)’s “same envelope” admits two readings. B1 revives the parent in envelope **0**; its singles live in **12 and 13**. Restricting removal to envelope 0 leaves B1 unchanged: two `(2,0)` `counts` violations. Moving each listing within its own envelope gives the required `(1,0)` `superseded_live` violations and passes the oracle/checker test. | Replace **“then move every live listing of that parent's singles in the same envelope from `blocks` to `voided_block_ids`”** with **“then, in every envelope, move each live listing of a single whose `parent_block_id` equals that parent's `block_id` from that envelope's `blocks` to its `voided_block_ids`”**. |
| F3 | **MATERIAL** | R4-4’s exact read list excludes both implementation files. This conflicts with the work assigned by R4-2. | Replace **“P's read set is exactly:”** with **“In addition to `joulewise/scored_packer.py` and `tests/test_scored_packer.py`, P's read set is exactly:”**. |

**Text dispositions**

- **R4-0 — ACCEPT:** closed ownership predicate; retain the terminal-holder clause despite its redundancy on this corpus.
- **R4-1 — ACCEPT after F1:** all **1,868 legal rosters** passed the baseline finalizing seal; no legal refusal found.
- **R4-2 — ACCEPT technically:** scratch implementation passed **all 71 existing tests**, the pairwise property, all seven named seal outcomes, and the requested AST checks. Neither suggested refusal-precedence conflict reproduced.
- **R4-3 — ACCEPT with F2 clarified:** zero operator/refresh errors; exhaustive pairs plus triples took approximately **192 seconds**.
- **R4-4 — ACCEPT seats/order; amend F3:** explicitly permit reading the implementation files.
- **R4-5 — AMEND F1; adjudication operable:** a constructor ran without `tests/`; external adjudication correctly classified an accepted single-prediction forgery as `ESCAPE` through checker `INV-12`.

**Probe tails**

```text
LEGAL_SEAL accepted=1868 refused=0
pairs:  ready=9989   operator_errors=0 refresh_errors=0 escapes=109
triples: ready=101679 operator_errors=0 refresh_errors=0 escapes=287

control: pairwise + named PASS
m1: killed, 45 pair escapes
m2: killed, 2 pair escapes
m3: SURVIVED, 0 pair escapes; named outcomes unchanged
m4: killed, 355 pair escapes
m5: killed, 184 pair escapes
replacement m3-term: killed, 276 pair escapes

Ran 71 tests in 1143.532s
OK
```

The baseline’s unexpected fourth failure was solely the parent-envelope interpretation in F2. The listing-local interpretation removes that failure; named-seal and pair/triple escape assertions remain intentionally RED.

Replay material: [harness reconstruction](/tmp/278ebc9e/r4ref/apply_r43.py), [scratch predicate](/tmp/278ebc9e/r4ref/apply_predicate.py), [mutation results](/tmp/278ebc9e/r4ref/mutations.log), [71-test results](/tmp/278ebc9e/r4ref/predicate-71.log).

## Residual risk

This was a scratch review, not final integrated verification. No other agent, independent forger seat, hardware measurement, or full repository suite was run. The worktree remains clean at `24ff94cb`.

Next step: adopt F1–F3 before K’s harness handoff to P.