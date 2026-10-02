# PR #454: Sol 6.1 executing review (codex-run-v3, gpt-6.1-sol, effort high, fresh clone, WRITE_SCOPE [])

Brief: below the report. Verbatim report:

```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "MERGE: the night-plan binding is correct; 126 requested tests pass; an existing issuer provenance gap is nonblocking.",
  "workspace": {
    "base_requested": "origin/main 96e13107",
    "base_mode": "exact",
    "head_start": "aaaf44ee58d3fdfe7d10529aa176b656ccad67ae",
    "head_end": "aaaf44ee58d3fdfe7d10529aa176b656ccad67ae",
    "upstream_end": "96e13107294a42fcda143549c51c87ea2f9cc377",
    "branch": "fix/2026-10-01-rev6-prior-start-plan-id"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "MERGE",
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "file": "scripts/issue_calibration_acceptance_generation.py",
        "line": 1300,
        "title": "Existing issuer path does not independently replay harvest-to-plan/ledger provenance",
        "blocking": false,
        "introduced_by_commit": false
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_acc_25g83_rev6 tests.test_harvest_window tests.test_rev6_prior_start_plan_id tests.test_revision6_seal tests.test_gen_derivation_night tests.test_custody_mode_inventory",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 126 tests in 169.544s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 126 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_rev6_prior_start_plan_id",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.117s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "cd /tmp/rev6-review-3out3ztc && /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_rev6_prior_start_plan_id",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 3 tests in 0.116s", "", "FAILED (errors=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(errors=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/rev6_review_probes.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ISSUER_AST_DELTA=one plan-ID comparison; no arithmetic changed",
          "ESTIMATOR_BLOBS=identical (4/4)",
          "FULL_SYNTHETIC_COMMITTED_START_AND_R9_REPLAY=PASS",
          "ISSUER_HARVEST_METADATA_MUTATION=ACCEPTED (committed start/R9 unchanged)",
          "ISSUER_SESSION_CALIBRATION_PLAN_MUTATION=ACCEPTED (same session IDs)",
          "CAMPAIGN_EXPECTED_PLAN_AND_WINDOW=ledger session identity",
          "SYNTHETIC_BRACKET_PLAN_AND_WINDOW_CHECKS=PASS (matching ledger calibration identity)",
          "NIGHT_ID_IN_CALIBRATION_BRACKET_FIELD=REFUSED",
          "LEDGER_FROZEN_CALIBRATION_PLAN_CHECK=PASS",
          "FOREIGN_HARVEST_NIGHT_PLAN=REFUSED (start-condition identity)",
          "FOREIGN_START_SESSION=REFUSED (start-condition identity)",
          "REVIEW_PROBES=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REVIEW_PROBES=PASS"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check 96e13107 aaaf44ee",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --porcelain=v1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The real-C1 regression deliberately uses empty finalized_slots and require_committed=False. Full evidence and committed-start validation were exercised with synthetic records, not live capture bundles.",
      "needs": ""
    }
  ]
}
```

## Findings

VERDICT: MERGE

**MINOR F1 — Existing provenance gap, outside this fix.** `scripts/issue_calibration_acceptance_generation.py:1300–1345` does not authenticate the enclosing harvest bytes as committed, reconstruct the night-plan/wrapper binding, or compare harvest ledger metadata with the supplied snapshot. Executed probes accepted altered harvest `sessions`, `plan_sha256`, and `ledger_head`, while preserving committed start/R9 bytes:

```text
ISSUER_HARVEST_METADATA_MUTATION=ACCEPTED (committed start/R9 unchanged)
ISSUER_SESSION_CALIBRATION_PLAN_MUTATION=ACCEPTED (same session IDs)
```

This is a real limitation in independent provenance replay, already present before this commit. It merits a separate hardening change; it does not invalidate this correction.

1. **The fix binds the right window.** At `scripts/issue_calibration_acceptance_generation.py:1327`, start and harvest now agree on the night-plan namespace written by `scripts/run_night.py:3181` and `scripts/harvest_window.py:475`. Window identity remains anchored by `start.session_id == r9.session_id`, membership in the supplied ledger sessions, evidence hashes, and—for non-null windows—committed start/R9 bytes at lines 1335–1337. The old calibration ID was shared across windows and supplied no unique window binding.

   Executed C1 checks confirmed that start/harvest night IDs match and differ from the wrapper’s calibration ID. Full synthetic replay authenticated committed start/R9 records; substitutions were refused:

   ```text
   FOREIGN_HARVEST_NIGHT_PLAN=REFUSED (start-condition identity)
   FOREIGN_START_SESSION=REFUSED (start-condition identity)
   ```

   Thus the window-identity chain is sound. The broader night-plan → wrapper → ledger provenance chain is enforced by the producer, but not independently replayed by the issuer, as F1 describes.

2. **No other analogous namespace error found.** The comparison census and executed probes produced these results:

   | Location | Comparison and production assessment |
   |---|---|
   | `scripts/harvest_window.py:125,409` | Frozen calibration plan → wrapper `PLAN_ID` → session calibration ID/digest. Correct namespace; the committed C1 wrapper carries the expected calibration ID. |
   | `scripts/issue_calibration_acceptance_generation.py:1493` | OFF receipt → start night-plan ID. Correct; updated fixtures pass this validation. |
   | `scripts/run_night.py:3027` | Start manifest → night-plan ID. No comparison with session calibration ID. |
   | `scripts/land_window_records.py:47,76` | Selects current session and authenticates referenced bytes. No plan/window-versus-session comparison. |
   | `scripts/build_bracket_binding.py:228` | Compares supplied frozen calibration/window identity with the ledger session. Matching synthetic identity passed; substituting a night ID into the calibration field refused. |
   | `joulewise/calibration_bracketing.py:1411,1512–1513` | Builds/validates the same calibration/window binding. Matching synthetic binding passed. |
   | `joulewise/calibration_ledger.py:5340,5592,6004` | Frozen calibration plan ID/digest checked against session identity. Executed matching-plan probe passed. |
   | `scripts/run_campaign.py:4969–4995` | Expected plan/window identity comes directly from the ledger session. Executed identity-selection probe confirmed this. |

   `joulewise/calibration_bracketing.py:2328–2329` additionally compares stored bracket identities with ledger observations; both fields use ledger-derived identities. The generation issuer and inspected continuation/reissue paths contain no additional direct plan/window-versus-session comparison. Claim-bracket checks are separate from Revision 6 derivation-window harvesting.

3. **Fixtures retain their refusal coverage.** All 126 requested tests passed:

   ```text
   Ran 126 tests in 169.544s

   OK
   ```

   AST comparison confirmed all **151 assertions** in `tests/test_harvest_window.py` remain unchanged. The fixtures now distinguish night and calibration IDs; the suite still exercises digest, commit, start-condition, timing, OFF-receipt, count, and stop refusals. No test assertion was removed or relaxed.

4. **Counterfactual confirmed.** The `/tmp` copy retained the new tests and restored only the issuer script from `96e13107`. It failed the real-C1 admission test:

   ```text
   PrepareRefusal: Revision 6 harvest record refused: start-condition identity or result disagreement
   Ran 3 tests in 0.116s

   FAILED (errors=1)
   ```

5. **No captured bytes, estimator files, registration text, or arithmetic changed.** The diff contains exactly four paths: the issuer, two fixture/test files, and the new regression test. AST comparison found exactly one executable issuer change—the identity comparison. All four named estimator Git blobs are identical to base. Fixture metadata changes intentionally; previously admitted records retain the same numerical calculations.

## Residual risk

The real-byte regression checks C1 record identity, not its full non-null evidence pipeline. Full committed-start/evidence validation and campaign identity checks passed with synthetic inputs. No live harvest, hardware measurement, or complete live campaign was executed. The repository remains clean and HEAD unchanged.
## Brief

WRITE_SCOPE: []

You are an independent reviewer (non-author) of commit aaaf44ee on branch fix/2026-10-01-rev6-prior-start-plan-id (base: origin/main 96e13107). Review only; WRITE_SCOPE is [] (write nothing in the repo; /tmp scratch is fine). You MUST execute code, not just read it.

Context. scripts/harvest_window.py refused the live harvest of Revision 6 window C2 because issuer.revision_six_records (scripts/issue_calibration_acceptance_generation.py, ~line 1323) compared the PRIOR window's (C1's) start-condition record plan_id with the ledger session's plan_id. Production facts (verified by the author):
- scripts/run_night.py ~line 3181 writes "plan_id": plan.plan_id, i.e. the NIGHT plan id (e.g. d079-epoch-25g83-r6-derivation-c1-20261001T0617Z).
- The calibration ledger's bracket session plan_id is the CALIBRATION plan id (plan-d117-floor-qwen25-1p5b-decode-p128-prefill-rider-v3) for every Revision 6 session.
- The harvest record (joulewise.harvest_window.v1) top-level plan_id is the night plan id; at harvest time harvest_window.py checks session.plan_id == wrapper PLAN_ID and session.plan_sha256 for the current window.
- The network-time OFF receipt (checked against start["plan_id"] ~line 1490) also carries the night plan id.
The fix compares start.plan_id to the harvest record's plan_id. Fixtures (tests/fixtures/epoch_bootstrap/revision6.py, tests/test_harvest_window.py) previously used the calibration id in both places; they now use a distinct night plan id. New test tests/test_rev6_prior_start_plan_id.py replays C1's real committed records under docs/process_traces/rev6-windows/d079-epoch-25g83-r6-20261001T0617Z/.

Questions (answer each with evidence from code you ran):
1. Is the fix correct: does start.plan_id == harvest["plan_id"] bind the start record to the right window, and is anything lost versus the old (wrong) binding? Is the harvest record's plan_id itself authenticated against the ledger session anywhere on the issuer path (it is committed; is the chain harvest-record -> session sound), and if not, is that a real gap or out of scope?
2. Does any OTHER code path compare a record's plan_id/window_id against session.plan_id in a way that will refuse real records (search the issuer, harvest_window, run_night, land_window_records, and the issue/campaign paths used after CLOSE_AND_DERIVE)? Name file:line for each such comparison and whether production bytes would pass.
3. Do the fixture changes still exercise the refusal paths they did before (no test weakened)? Run: python -B -m unittest tests.test_acc_25g83_rev6 tests.test_harvest_window tests.test_rev6_prior_start_plan_id tests.test_revision6_seal tests.test_gen_derivation_night tests.test_custody_mode_inventory and report the tail. Use /Users/edr/code/JouleWise/.venv/bin/python.
4. Counterfactual: revert only the scripts/ change (in /tmp copy or via git stash, then restore) and confirm the new real-bytes test fails.
5. Does the change alter any captured byte, any computed number, any estimator file (joulewise/powermetrics_fiducial.py, joulewise/uncertainty_evidence.py, joulewise/adapters/powermetrics.py, joulewise/reduce.py), or any registration text? 

Output: a verdict line "VERDICT: MERGE" or "VERDICT: BLOCK", then findings each tagged BLOCKER/MAJOR/MINOR/NIT with file:line and the command output that supports it. Do not read any measured value (no B, no slot disposition beyond what the committed records already show, no chain-log slot lines).
