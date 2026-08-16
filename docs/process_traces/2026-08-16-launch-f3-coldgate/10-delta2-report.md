```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "REJECT: the private consumer accepts and permanently consumes self-authored or foreign-pack launch context, and replay still passes; the mandatory rule-11 cold gate fires.",
  "workspace": {
    "base_requested": "72cd69842434962d95176c9a625d256bc55f4fe5",
    "base_mode": "exact",
    "head_start": "66884c6d3b299275149a66ff12fc7d6ab39b5f35",
    "head_end": "66884c6d3b299275149a66ff12fc7d6ab39b5f35",
    "upstream_end": "66884c6d3b299275149a66ff12fc7d6ab39b5f35",
    "branch": "HEAD detached; impl/wo-launch-binding points to 66884c6"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "REJECT",
    "rule_11_cold_gate_required": true,
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "Unauthenticated or foreign launch context consumes the capability and passes replay",
        "paths": [
          "joulewise/arm_readiness.py:4862",
          "joulewise/arm_readiness.py:4905",
          "joulewise/arm_readiness.py:4711",
          "docs/decision_log.md:9404"
        ],
        "scenario": "Pair a valid ALPHA arm receipt with a complete BETA manifest, window root, environment, chain, digests, and argv from a different pack/session on the same boot. _consume_launch_capability returns CONSUMED, creates the no-clobber primary, and verify_consumed_launch returns PASS.",
        "cause": "The callee authenticates the arm independently but checks the supplied manifest/window inputs only for schema and self-consistency. It never binds their identities to the authenticated T-0 LAUNCH_RECIPE evidence, arm session, pack, or expected custody input path before publication.",
        "required": "Bind the manifest, window.env, chain, root, and argv to identities authenticated through the selected arm receipt before creating arm_readiness.consumptions/*.consumed.json. Then run the mandatory rule-11 cold gate."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Omitted required context has no registered refusal code",
        "paths": [
          "joulewise/arm_readiness.py:4764"
        ],
        "scenario": "Omitting launch_manifest_sha256 raises Python TypeError before the callee and produces no side effect. Passing an explicit null context correctly raises readiness_usage_invalid.",
        "cause": "The keyword-only signature enforces presence at Python call binding, outside the registered refusal mechanism.",
        "required": "If the audit contract requires every missing-input attack to return a registered code, validate a required-context object or sentinel values inside the callee."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse 72cd698 66884c6 HEAD && git diff --check 72cd698..66884c6",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "72cd69842434962d95176c9a625d256bc55f4fe5",
          "66884c6d3b299275149a66ff12fc7d6ab39b5f35",
          "66884c6d3b299275149a66ff12fc7d6ab39b5f35"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "66884c6d3b299275149a66ff12fc7d6ab39b5f35"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "TMPDIR=<fresh-temp> PYTHONDONTWRITEBYTECODE=1 python3 <dynamic module-surface and required-context attack probe>",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "SURFACE {\"delta2_launch_window\": {\"aliases\": [\"_consume_launch_capability\"], \"public_aliases\": []}, \"delta2_run_campaign\": {\"aliases\": [], \"public_aliases\": []}, \"joulewise.arm_readiness\": {\"aliases\": [\"_consume_launch_capability\"], \"public_aliases\": []}}",
          "PUBLIC_NAME False IN_ALL False",
          "MISSING_NULL ArmReadinessError:readiness_usage_invalid side_effect False",
          "FORGED_ARM_VALUE ArmReadinessError:readiness_usage_invalid side_effect False",
          "HONEST_SINGLE_USE CONSUMED ArmReadinessError:readiness_record_consumed"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "HONEST_SINGLE_USE CONSUMED ArmReadinessError:readiness_record_consumed"
      }
    },
    {
      "id": "V3",
      "kind": "other",
      "cmd": "TMPDIR=<fresh-temp> PYTHONDONTWRITEBYTECODE=1 python3 <self-authored and cross-session context substitution probe>",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "SELF_AUTHORED_MANIFEST CONSUMED primary True replay PASS",
          "FOREIGN_SESSION_CONTEXT CONSUMED primary True replay PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REFUSE.*side_effect False"
      }
    },
    {
      "id": "V4",
      "kind": "other",
      "cmd": "TMPDIR=<fresh-temp> PYTHONDONTWRITEBYTECODE=1 python3 <real ARM-reauthentication foreign-pack/session probe>",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "REAL_REAUTH_FOREIGN_PACK_SESSION CONSUMED True PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "REAL_REAUTH_FOREIGN_PACK_SESSION_REFUSED .*launch_binding_mismatch"
      }
    },
    {
      "id": "V5",
      "kind": "other",
      "cmd": "TMPDIR=<fresh-temp> PYTHONDONTWRITEBYTECODE=1 python3 <omitted-required-key attack probe>",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "MISSING_OMITTED TypeError:None side_effect False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MISSING_OMITTED .*readiness_usage_invalid.*side_effect False"
      }
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "This is the third F3 failure: foreign or self-authored launch inputs cross the required-context boundary and burn the single-use capability.",
      "needs": "Invoke the mandatory rule-11 cold gate before another fix or merge decision."
    },
    {
      "id": "G2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The forced final-response interruption occurred before the nine focused suites, AXI execution pair, four lifecycle spot checks, mutation check for the public-absence assertion, and launch_window end-to-end suite could be run.",
      "needs": "Rerun those checks after the blocker is repaired; they cannot overturn this REJECT."
    }
  ]
}
```

## Findings

F1 — blocker: `_consume_launch_capability` authenticates the ARM receipt, but the manifest-side checks only prove that the caller supplied matching parsed values and digests for whatever files it chose. The manifest is not reconciled with the authenticated T-0 `LAUNCH_RECIPE` artifact identity, and `window.env` is hashed without its pack/session bindings being parsed.

The executed production-reauthentication probe paired a valid ALPHA arm with BETA launch inputs. It returned:

```text
REAL_REAUTH_FOREIGN_PACK_SESSION CONSUMED True PASS
```

Thus the wrong context creates the irrevocable primary and survives `verify_consumed_launch`. A separately self-authored manifest/window produced the same `CONSUMED ... replay PASS` outcome. This is not the registered “complete valid inputs stolen verbatim” limitation: the launch context was newly authored or taken from another pack/session.

The decision-log statement that the callee reauthenticates the manifest, roots, environment, chain, and argv therefore overclaims what the code proves.

F2 — should_fix: omitting a required keyword produces `TypeError` with no registered reason code. Explicit null context does correctly refuse with `readiness_usage_invalid`, and neither missing-input form creates the consumption directory.

Deletion completeness itself passed: the old public name is absent, absent from `__all__`, and has no public identity alias in `arm_readiness`, `launch_window`, or `run_campaign`. Only the underscore import remains in the reviewed launcher. The caller-frame/file guards are gone. Honest complete context consumes once, and replay refuses with `readiness_record_consumed`.

## Residual risk

The mandatory suite matrix and requested AXI/lifecycle executions were not completed before the forced final-response handoff. Static inspection shows the AXI code and D-078/Phase-2 decision text in the expected locations, but that is not a substitute for the requested executions.

VERDICT: **REJECT**.