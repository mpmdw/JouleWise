"""Frozen source-tree changes for the four audit spelling regressions."""
import json

POLICY_PATH = "configs/campaign_policies/quiet_mac_p2_production.json"
MANIFEST_PATH = "configs/campaigns/fixture-derivation/settled_corpus.json"
LEDGER_PATH = "runs/calibration_observation_ledger.jsonl"
HEAD_PATH = "configs/calibration/calibration_ledger_head.json"
KINDS = {"derivation": "bound_derivation", "ledger": "bracket_reservation",
         "head_pin": "bracket_reservation", "policy": "campaign_collection", "session_kind": "bracket_reservation"}
POLICY = {
    "schema_version": "joulewise.campaign_policy.v1", "policy_id": "invented-audit-policy",
    "policy_version": "fixture-1", "profile": "production", "idle_admission": {},
    "environment_guard": {}, "cooldown": {},
    "calibration_bracketing": {"require_bracket": True, "calibration_bracket_max_drift_s": 1.0},
}


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode()


def literal(value):
    return {"kind": "literal", "value": value}


def apply(form_class, spelling, tree):
    """Mutate the actual materialized source template before rendering or committing it."""
    rows = [s for s in tree["stage_graph"] if s["kind"] == KINDS[form_class]]
    if not rows:
        raise AssertionError("fixture lacks the production stage")
    for stage in rows:
        args = stage["launch"]["commands"][0]["argv_template"]["arguments"]
        if form_class == "derivation":
            index = args.index(literal("--derive-neg8-drift-bound")) + 1
            args[index] = ({"kind": "repo_path", "value": MANIFEST_PATH} if spelling == "repo_path"
                           else {"kind": "binding_path", "value": "repo_root", "relative": MANIFEST_PATH})
        elif form_class == "policy":
            if spelling == "explicit":
                args.extend([literal("--campaign-policy"), {"kind": "repo_path", "value": POLICY_PATH}])
            elif spelling == "equals":
                args.append(literal("--campaign-policy=" + POLICY_PATH))
        elif form_class == "ledger" and spelling != "default":
            args.extend([literal("--ledger"), ({"kind": "binding", "value": "ledger_path"} if spelling == "bare"
                                              else {"kind": "repo_path", "value": LEDGER_PATH})])
        elif form_class == "head_pin" and spelling == "explicit":
            args.extend([literal("--head-pin"), {"kind": "repo_path", "value": HEAD_PATH}])
        elif form_class == "session_kind" and spelling == "explicit":
            args.extend([literal("--session-kind"), literal("bracket")])
    return {POLICY_PATH: encoded(POLICY), LEDGER_PATH: b"",
            HEAD_PATH: encoded({"sequence": 0, "head_digest": "0" * 64,
                                "ledger_schema": "joulewise.calibration_observation_ledger.v1"}),
            MANIFEST_PATH: encoded({"members": [{"bundle_path": f"invented-{i:02}"} for i in range(1, 13)]})}
