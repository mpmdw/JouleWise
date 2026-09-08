```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Reconstruction and all 50 decisions pass; terminology, one overbroad sentence, and inaccurate code pins need correction.",
  "workspace": {
    "base_requested": "5cf1660f",
    "base_mode": "exact",
    "head_start": "5cf1660f378a0c0934216247d27ecf2519878305",
    "head_end": "5cf1660f378a0c0934216247d27ecf2519878305",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "docs/2026-09-08-window-liveness-docs"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "B1", "severity": "should_fix"},
      {"id": "B2", "severity": "should_fix"},
      {"id": "A1", "severity": "nit"}
    ]
  },
  "verification": [{
    "id": "V1",
    "kind": "inspection",
    "cmd": "git diff --exit-code 655b3368 5cf1660f -- joulewise/measurement_liveness.py scripts/run_night.py scripts/run_campaign.py scripts/window_status.sh",
    "cwd": ".",
    "observed": {
      "result": "pass",
      "exit_code": 0,
      "tail": ["git: warning: confstr() failed with code 5: couldn't get path of DARWIN_USER_TEMP_DIR; using /tmp instead"]
    },
    "expected": {"exit_code": 0, "tail_regex": "using /tmp instead$"}
  }],
  "flags": []
}
```

## Findings

**B1 — should_fix: C5 still overstates token refusal.** At `docs/contracts/window_liveness.md:157`, “The census refuses any start object without a usable token” contradicts `joulewise/measurement_liveness.py:189–198`: an accepted exit bypasses token validation, including for a tokenless start object. Qualify this sentence with “when neither exit check accepts an exit.” C10 and the decision table correctly describe that precedence; C5 should agree.

**B2 — should_fix: Code map pins are inaccurate at both the declared source revision and this head.** The four implementation files are unchanged between those revisions. Corrections:

- P1: status redirection is `scripts/window_status.sh:94`; commit/push are `:107–108`, outside the cited `:99–106`.
- C2: JSON encoding/newline is `scripts/run_night.py:102–103`, not `:105–106`.
- C4: temporary exclusive creation is `scripts/run_night.py:117`, outside the cited `:119–129`; use `:116–125`.
- C5: null assignment is `scripts/run_night.py:382`, not `:381`.
- T7: local-only branch is `scripts/window_status.sh:96–99`; cited `:94–97` omits its return.

Other mapped implementation ranges support their associated mechanisms.

**A1 — nit: Remaining first-use gaps, in reading order.** In `docs/contracts/window_liveness.md`: “courier-delivery” (`:193`) precedes the delivery explanation at `:670`; “collector” (`:696`) and “watchdog” (`:699`) lack local definitions. Explain the delivery program, measurement-collection program, and agent-monitoring program at those first uses.

**Lens A otherwise passes.** The probe, marker sequence, registry, and census can be reconstructed from the text and examples. Every diagram identifies its elements and explains its arrows or indentation. A read-only check found exactly 50 unique chain/registry combinations, all consistent with refusal precedence. Traversal errors are explicitly handled outside that Cartesian table.

**Lens B correspondence.** For sentence-level citations, the paragraph-ID Code map is corroborated with B2’s corrections. Compact audit index below uses **M**=`joulewise/measurement_liveness.py`, **N**=`scripts/run_night.py`, **C**=`scripts/run_campaign.py`, **S**=`scripts/window_status.sh`:

- P1–P3: S12–19,41–47,60–112; M71–72,224–272. Historical motivation matches the linked terminal review.
- F1–F3: M25–68,113–116,175–182; N373–385,431–437.
- C1–C6: N102–125,360–385,431–452,1247–1266; M199–201, subject to B1.
- C7–C9: N312–357,438–450,498–499,1339–1422; M159–163.
- C10: M144–148,187–201. Both exit checks and malformed-start interruption match.
- I1–I8: M23–68,166–212. Empty-success UNKNOWN, zombie DEAD, and token comparison match.
- R1–R5: M71–72,100–130; C3160–3184,7246–7288,8239–8261.
- R6–R11: M75–97,144–182,204–212; C8030–8035,8952–8957. DEAD campaigns bypass token validation at M172–174.
- D1–D6: M215–262. Escaping errors stop traversal at M261–262; nested disappearance retries and discarded partial registry findings match.
- T1–T5: M139–141,166–212,261–272.
- T6–T8: M3–7,47,266–272; S30–47,94–112; N459–460.
- W1–W3: preceding identity/table mappings; M159–163,237–262; S44–47,94–112.

No additional mechanism contradiction found.

## Residual risk

Static review and table verification only; no live probes, measurement collection, repair commands, or test suite executed.