```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented independent history and strict NULL-restore primitives; canonical integration requires expanded scope and lead rulings.",
  "workspace": {
    "base_requested": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "base_mode": "exact",
    "head_start": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "head_end": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "upstream_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "branch": "lane/2026-10-05-b4-x7"
  },
  "pathspec": [
    "joulewise/v5_qualification.py",
    "scripts/restore_v5_null_reservation.py",
    "tests/test_v5_block4_x7.py",
    "tests/test_v5_qualification_plan.py",
    "tests/test_v5_s1_qualification.py",
    "tests/test_authentication_io.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_v5_block4_x7 tests.test_authentication_io > /tmp/dd5-x7/independent-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK", "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_v5_block4_x7 tests.test_v5_qualification_plan tests.test_harvest_v5_g2b_window tests.test_harvest_v5_qualification tests.test_v5_block4_x6 tests.test_v5_block4_replay tests.test_v5_s1_qualification tests.test_v5_s1_desk_closeout > /tmp/dd5-x7/focused-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=5, skipped=4)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_authentication_io tests.test_git_fixture_maintenance > /tmp/dd5-x7/registries-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=1)", "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. TMPDIR=/tmp/dd5-x7 python3 /tmp/dd5-x7/prove_schema_blocker.py > /tmp/dd5-x7/scope-blocker.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PLAN BLOCKER: night_plan_malformed", "AUTHORIZATION BLOCKER: authorization_record.keys"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "AUTHORIZATION BLOCKER: authorization_record.keys"
      }
    },
    {
      "id": "V5",
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
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest discover -s tests > /tmp/dd5-x7/canonical.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: canonical NightPlan and authorization consumers reject previous_attempt. No out-of-scope paths were modified. The writer, s2 occurrence, and both harvester integrations remain blocked.",
      "needs": "Expand scope for the canonical schema/serialization consumers and remaining fixture repairs listed below."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: a native reservation appends two physical rows: append-intent then bracket-session-open. The literal one-row restore rule correctly refuses this native tail.",
      "needs": "Choose literal single-row recovery or permit the authenticated native intent plus exactly one open business row. Recommend the latter without changing ledger format."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: existing --archive-root identifies one derived harvest; the reviewed drafts do not provide a concrete block-wide census layout distinguishing G2-b, qualification, and identical-byte R3 reharvests.",
      "needs": "Specify the create-once block-root binding and counted harvest layout. Recommend a registered structural-attempt root with qualification and derived reharvest outputs separately placed."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "blocking",
      "text": "The requested focused run completed 160 tests with five failures and four skips. All failures are in unchanged test_v5_block4_replay.py: one obsolete pack-source pin assertion and four expected refusal-code assertions. Git fixture maintenance still finds direct initialization in three unlisted tests.",
      "needs": "Authorize the listed replay and Git-fixture test repairs."
    },
    {
      "id": "F5",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The canonical suite was started and interrupted for the blocked handoff; V6 records no completed suite result.",
      "needs": "Complete canonical verification after integration and scoped fixture repair."
    },
    {
      "id": "F6",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "The admission evidence primitive currently authenticates display/screensaver guard aborts. CPU/GPU admission-abort causal replay is incomplete. History and restore verification primitives are not wired into the canonical writer or harvesters.",
      "needs": "Complete admission replay and integration after scope and layout rulings."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/night_gate.py",
      "joulewise/night_plan_writer.py",
      "joulewise/arm_readiness.py",
      "tests/test_v5_block4_replay.py",
      "tests/test_v5_block4_x1.py",
      "tests/test_v5_block4_x2.py",
      "tests/test_v5_s1_desk_closeout.py"
    ],
    "reason": "Required plan/authorization fields cannot pass the current exact-key consumers; remaining required verification repairs are outside the allowlist.",
    "blocked_work": "Mandatory create-once previous_attempt output, s2 writer, canonical history census and restore verification, admission rearm integration, and remaining fixture checks.",
    "minimal_change": "Extend the canonical G2-b plan/authorization schema and serializer, wire the authorized writer/harvesters to the new primitives, and repair stale replay expectations and direct Git initialization."
  }
}
```

## Change

Added authenticated chain/census and allowance primitives, strict NULL reservation restore with create-once custody and replay verification, and 18 X7 tests. Registered the restore authentication surface and repaired authorized fixture drift. Changes remain uncommitted; nothing was pushed.

## Verification notes

Independent X7/authentication checks passed. The requested suite retains five replay-fixture failures; Git maintenance retains three unlisted offenders. Resume with the scope expansion and two rulings above.

## Residual risk

This is not an integrated solution: mandatory history enforcement, the `s2` writer, and harvester rearm behavior remain incomplete. Native reservation tails currently refuse restoration under the literal one-row rule.