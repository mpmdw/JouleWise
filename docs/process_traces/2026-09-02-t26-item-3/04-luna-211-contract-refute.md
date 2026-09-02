```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The 600 s production predicate and regressions pass, but stale 5 s documentation/state text and an unresolved D-170 citation remain.",
  "workspace": {
    "base_requested": "6075389a13df206205651175a7a9d52135df6fde",
    "base_mode": "exact",
    "head_start": "6075389a13df206205651175a7a9d52135df6fde",
    "head_end": "e40e75026196d42459a2edeb8eb6e4d2b212914d",
    "upstream_end": "3e6243df8943f6a4ec152cab7ea791a8a161efea",
    "branch": "feat/2026-09-02-t26-liveness"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file": "docs/process_traces/2026-08-23-t22/t0-unattended/MAGISTRATE-RULING-T0-UNATTENDED.md:78",
        "ruled_text": "The cold gate strikes the 5 s bound and 35 s corollary and replaces them with the ordinary-clock 600 s liveness relation.",
        "landed_text": "The authoritative prior T-0 ruling still states R1-completion-to-validity-origin <=5 s and oldest R1 result <=35 s at issuance, without an AMENDED, STRUCK, or superseded marker.",
        "why_they_differ": "A normative source still presents the superseded bound as live, violating the no-live-struck-text clause."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "file": "docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md:491",
        "ruled_text": "Section 6.3 must resolve the old 5 s relation to the ruled 600 s liveness relation.",
        "landed_text": "The new resolved paragraph at :1150-1160 exists, but RF-17, the numeric relation at :522, the COLD-GATE-PENDING heading, and the old options/interim disposition at :990-1148 still state the 5 s/no-upper-bound contract.",
        "why_they_differ": "Appending a resolution does not mark the preceding contradictory contract text superseded; readers can still select the old relation."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "file": "docs/process/state_kernel.json:4289",
        "ruled_text": "The cold-gate ruling installs the 600 s liveness conjunct.",
        "landed_text": "The live state-kernel fence still says the 5 s issuance bound is COLD-GATE-PENDING and must not be relaxed or implemented; the T0 status note at :4345 says the upper bound is deliberately not implemented.",
        "why_they_differ": "The project work-selection source contradicts the landed production behavior and can direct later work to undo or reject the ruled implementation."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "file": "docs/process_traces/2026-08-23-t22/t0-unattended/impl/reason-code-coverage-delta.md:1150",
        "ruled_text": "D-170 records the cold-gate verdict and is cited by the implementation disposition.",
        "landed_text": "The disposition and production comment cite D-170, but HEAD's docs/decision_log.md ends with D-169 at :10437-10448 and contains no D-170 entry.",
        "why_they_differ": "The citation is unresolved on this isolated sibling branch; the ruling file itself exists, but the cited decision-log authority does not."
      },
      {
        "id": "F5",
        "severity": "nit",
        "file": "joulewise/arm_readiness.py:6478",
        "ruled_text": "The 600 s constant is grounded in 11 x 45 s + 105 s and equals the existing _MIN_IDLE_NS.",
        "landed_text": "The comment states that provenance and the values currently equal 600000000000; tests pin the liveness boundary but do not assert equality with _MIN_IDLE_NS.",
        "why_they_differ": "The current values match, but the duplicate production constants are coupled only by comment and inspection."
      }
    ],
    "clause_table": [
      {"id":"C1","proposition":"Exact relation has both lower and upper inequalities.","status":"CONFIRMED","landed":"joulewise/arm_readiness.py:6482-6485","seat_map":"Production :6478-6485"},
      {"id":"C2","proposition":"Both endpoints use ordinary context.clock.monotonic_ns().","status":"CONFIRMED","landed":"joulewise/arm_readiness_evidence_t0.py:1115,2325; :301-304","seat_map":"Production conjunct"},
      {"id":"C3","proposition":"Upper constant is exactly 600_000_000_000 and named.","status":"CONFIRMED","landed":"joulewise/arm_readiness.py:6349,6485","seat_map":"Production :6349"},
      {"id":"C4","proposition":"Comment labels the bound liveness/hang detection, not metrology.","status":"CONFIRMED","landed":"joulewise/arm_readiness.py:6478-6481","seat_map":"Production :6478-6485"},
      {"id":"C5","proposition":"Provenance is 11 x 45 s + 105 s = _MIN_IDLE_NS = 600 s.","status":"CONFIRMED","landed":"joulewise/arm_readiness_evidence_t0.py:51,54; arm_readiness.py:6478-6481","seat_map":"Production conjunct"},
      {"id":"C6","proposition":"Existing evidence_author_t0_predicate_refused is reused; no reason-code census delta.","status":"CONFIRMED","landed":"reason-code-coverage-delta.md:1158-1160; census unchanged at 45 produced/56 registered","seat_map":"Disposition :1158-1160"},
      {"id":"C7","proposition":"Issuance rejects 600 s+1 ns and passes 600 s-1 ns.","status":"CONFIRMED","landed":"tests/test_arm_readiness_evidence_t0.py:831-852","seat_map":"Tests issuance :831"},
      {"id":"C8","proposition":"Arm rejects 600 s+1 ns and passes 600 s-1 ns.","status":"CONFIRMED","landed":"tests/test_arm_readiness.py:59-66; tests/test_t0_rehearsal.py:562-578","seat_map":"Tests arm :59; rehearsal :562"},
      {"id":"C9","proposition":"The former open-item comment is updated.","status":"CONFIRMED","landed":"joulewise/arm_readiness.py:6478-6481","seat_map":"Production :6478-6485"},
      {"id":"C10","proposition":"Section 6.3 is updated to resolved and cites the ruling.","status":"DIVERGES","landed":"reason-code-coverage-delta.md:1150-1160, with stale pending text retained at :990-1148","seat_map":"Disposition :1150"},
      {"id":"C11","proposition":"Struck 5 s/35 s text appears nowhere as a live bound.","status":"DIVERGES","landed":"Prior ruling :78-80; delta :491,522,990-1148; state kernel :4289,4345","seat_map":"Not in seat map"},
      {"id":"C12","proposition":"EVIDENCE sample horizon is R1 + 6 h + 1 s inside the ruled window; ARM remains 10**30 without schema coverage loss.","status":"CONFIRMED","landed":"tests/test_arm_readiness_schemas.py:44-49,221-232,281-289","seat_map":"Not in seat map"},
      {"id":"C13","proposition":"D-170 decision-log record is present at HEAD.","status":"MISSING","landed":"docs/decision_log.md ends at D-169 :10437-10448","seat_map":"Not in seat map"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_evidence_t0 tests.test_t0_rehearsal tests.test_arm_readiness_schemas tests.test_arm_readiness_evidence tests.test_arm_readiness_integration",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["Ran 187 tests in 229.569s","OK (skipped=12)"]},
      "expected": {"exit_code":0,"tail_regex":"Ran 187 tests in [0-9.]+s\\n\\nOK \\(skipped=12\\)"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'import ast,re,subprocess; from pathlib import Path; import joulewise.arm_readiness as r, joulewise.arm_readiness_evidence_t0 as t; s=Path(\"joulewise/arm_readiness_evidence_t0.py\").read_text(); n=[x.lineno for x in ast.walk(ast.parse(s)) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id==\"_fresh_probe\"]; b=subprocess.check_output([\"git\",\"show\",\"6075389a:joulewise/arm_readiness.py\"],text=True); h=Path(\"joulewise/arm_readiness.py\").read_text(); f=lambda x:set(re.findall(r\"\\\"(readiness_[a-z0-9_]+)\\\"\",x.split(\"class ArmReadinessError\",1)[1])); print(f\"post_r1_call_sites={sum(x>1101 for x in n)}\"); print(f\"min_idle_ns={t._MIN_IDLE_NS}\"); print(f\"liveness_constant={r._T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS}\"); print(f\"constants_equal={t._MIN_IDLE_NS==r._T0_R1_TO_VALIDITY_ORIGIN_LIVENESS_NS}\"); print(f\"reason_literal_sets_equal={f(b)==f(h)}\"); print(f\"produced_count={len(f(h))}\"); print(f\"registered_count={len(r.READINESS_REASON_CODES)}\")'",
      "cwd": ".",
      "observed": {"result":"pass","exit_code":0,"tail":["post_r1_call_sites=11","min_idle_ns=600000000000","liveness_constant=600000000000","constants_equal=True","reason_literal_sets_equal=True","produced_count=45","registered_count=56"]},
      "expected": {"exit_code":0,"tail_regex":"post_r1_call_sites=11[\\s\\S]*constants_equal=True[\\s\\S]*reason_literal_sets_equal=True[\\s\\S]*produced_count=45[\\s\\S]*registered_count=56"}
    }
  ],
  "flags": [
    {"id":"G1","kind":"baseline_drift","level":"blocking","text":"HEAD is the liveness sibling branch; the D-170 decision entry and T-0 Horizon amendment are not present on HEAD.","needs":"Integrate or explicitly adjudicate the companion install branch before aggregate closure."},
    {"id":"G2","kind":"verification_gap","level":"nonblocking","text":"The duplicate liveness constant and _MIN_IDLE_NS are equal by inspection, but no focused test asserts that provenance coupling.","needs":"Lead may add a focused equality assertion."}
  ]
}
```

## Independent clause list

| ID | Proposition | Status | Seat-map correspondence |
|---|---|---|---|
| C1 | Exact relation contains both inequalities. | CONFIRMED | Production |
| C2 | Both endpoints use the ordinary monotonic clock. | CONFIRMED | Production |
| C3 | Constant is named and exactly 600,000,000,000 ns. | CONFIRMED | Production |
| C4 | Code comment labels liveness, not metrology. | CONFIRMED | Production |
| C5 | Provenance is 11×45 s + 105 s = `_MIN_IDLE_NS` = 600 s. | CONFIRMED | Production |
| C6 | Existing refusal code and unchanged reason census. | CONFIRMED | Disposition |
| C7 | Issuance boundary regressions. | CONFIRMED | `test_arm_readiness_evidence_t0.py` |
| C8 | Arm boundary regressions. | CONFIRMED | `test_arm_readiness.py`, `test_t0_rehearsal.py` |
| C9 | Former open-item comment updated. | CONFIRMED | Production |
| C10 | §6.3 resolved disposition cites ruling. | DIVERGES | Disposition |
| C11 | No live 5 s/35 s text remains. | DIVERGES | Not in seat map |
| C12 | EVIDENCE fixture is strictly inside the window; ARM fixture coverage remains. | CONFIRMED | Not in seat map |
| C13 | D-170 decision-log record exists at HEAD. | MISSING | Not in seat map |

## Findings

See machine-readable findings F1–F5 above. The production implementation and all named regressions pass; the remaining blockers are documentation/state reconciliation issues.

## Residual risk

The ruling’s sleep-blind ordinary-clock limitation and the single global validity stamp for all fifteen rows remain unchanged and are explicitly outside this install.

