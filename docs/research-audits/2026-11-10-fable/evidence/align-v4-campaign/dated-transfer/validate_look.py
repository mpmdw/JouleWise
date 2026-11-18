"""Validate the audit draft only. This CLI has no look execution or finalization path."""
import argparse
from hashlib import sha256
import json
import re

from build_kits import HERE, ROOT

LOOK_ID = "lm-transfer-01"
REGISTERED = "docs/process/cadence/looks"
WORDS = {"transfer_interval": ["estimated", "not_evaluable"], "stage2_error": ["no"]}
HASHES = ["manifest_sha256", "stage1_roster_sha256", "freeze2_sha256"]
HASH_PATTERN = "[0-9a-f]{64}"
OUTPUT_FIELDS = set(WORDS) | set(HASHES)


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_bytes(), object_pairs_hook=unique_pairs)


def validate_public(payload):
    """Check the exact public success payload with the ruled closed fields."""
    require(isinstance(payload, dict) and payload.keys() == OUTPUT_FIELDS, "unexpected public fields")
    for field, allowed in WORDS.items():
        require(type(payload[field]) is str and payload[field] in allowed, f"unexpected public word: {field}")
    for field in HASHES:
        require(type(payload[field]) is str and re.fullmatch(HASH_PATTERN, payload[field]), f"invalid hash: {field}")


def verify_ref(ref, path):
    wanted = {"path": str(path.relative_to(ROOT)), "sha256": sha256(path.read_bytes()).hexdigest()}
    require(ref == wanted, f"reference mismatch: {path.name}")


def validate_draft(doc, manifest_path):
    require(doc.keys() == {
        "schema", "look_kind", "look_id", "status", "title", "rulings", "registered_paths",
        "registration", "reads", "inclusion", "estimate", "code_pins", "outputs", "reservation", "cold_pass_checks",
    }, "unexpected transfer draft fields")
    require((doc["schema"], doc["look_kind"], doc["look_id"], doc["status"]) ==
            ("joulewise.cadence_look_manifest.v2", "transfer", LOOK_ID, "draft"), "audit draft only")
    registered_path = f"{REGISTERED}/{LOOK_ID}.json"
    require(doc["registered_paths"] == {"manifest": registered_path, "ledger": f"{REGISTERED}/LOOKS.json"},
            "registered destinations differ")
    require(doc["title"].startswith("DRAFT") and "effective freeze 2" in doc["title"], "draft hold missing")
    roster_path = HERE / "date-place-roster.json"
    reads = doc["reads"]
    verify_ref(reads["planned_date_places"], roster_path)
    roster = load(roster_path)
    require((reads["max_dates"], reads["max_legs"], reads["timezone"]) == (20, 120, "America/Los_Angeles"),
            "invalid transfer capacity or timezone")
    require(len(reads["kits"]) == len(roster["places"]) == 20, "expected twenty date places and kit hashes")
    for place, (entry, row) in enumerate(zip(reads["kits"], roster["places"]), 1):
        kit_id = f"cl-transfer-{place:02}"
        require(row["date_place"] == place and row["kit_id"] == kit_id and entry.get("kit_id") == kit_id,
                "kit order must be the date-place order")
        kit_ref = {key: value for key, value in entry.items() if key != "kit_id"}
        require(kit_ref == row["kit"], f"kit ref differs from the roster: {kit_id}")
        verify_ref(kit_ref, HERE / "kits" / f"{kit_id}.v1.1.json")

    estimate = doc["estimate"]
    require(estimate["channels"] == ["gpu_rail", "dc_in"] and estimate["minimum_hot_legs_per_date"] == 3,
            "unexpected channels or date guard")
    require(estimate["daily_error"] == "(sum(predicted) - sum(measured)) / sum(measured)", "signed daily error")
    require(estimate["interval"] == {
        "series": "signed_daily_error", "level": 0.9, "quantile": 0.95, "ddof": 1,
        "formula": "mean(e) ± t(0.95, D - 1) × SD(e, ddof=1) / sqrt(D)", "minimum_dates": 2,
    }, "unexpected signed daily interval")
    require(estimate["comparison_only_abs_error_cutoff"] == 0.02, "private comparison cutoff changed")
    require(doc["inclusion"]["short_legs"] == [
        {"decode_cap": 3724, "closing_stamp": 3583, "last_token_stamp": 3723, "gaps": 140},
        {"decode_cap": 3151, "closing_stamp": 3071, "last_token_stamp": 3150, "gaps": 79},
    ], "unexpected type-L terminal segments")

    pins = doc["code_pins"].copy()
    require(bool(pins.pop("predictor_equivalence")), "missing equivalence rule")
    require(pins.keys() == {"predictor", "inclusion", "scorer", "manifest_schema", "stage1_schema", "output_schema"},
            "code pin inventory changed")
    require(all(ref.keys() == {"path", "sha256"} and ref["sha256"] == "PENDING:CODE"
                for ref in pins.values()), "draft uses registration placeholders")
    outputs = doc["outputs"]
    require(outputs.keys() == {"public_file", "audit_output_schema", "words", "hashes", "interval_status_rule",
                               "custody_names", "after_read_failure"}, "unexpected output inventory")
    require(outputs["public_file"] == "PUBLIC.json" and outputs["words"] == WORDS and outputs["hashes"] == HASHES,
            "public success inventory changed")
    require(outputs["custody_names"] == ["scores.json", "stdout", "stderr"], "closed private inventory changed")
    failure = outputs["after_read_failure"]
    require(failure["stderr_lines"] == ["stage2_error", "<allowed error type or OtherError>"] and
            failure["type_allowlist"] == ["builtins", "numpy.linalg.LinAlgError", "json.JSONDecodeError", "OtherError"]
            and type(failure["exit_status"]) is int and 1 <= failure["exit_status"] <= 125,
            "unexpected post-read failure contract")
    schema_path = HERE / "looks" / f"{LOOK_ID}.output.schema.json"
    verify_ref(outputs["audit_output_schema"], schema_path)
    schema = load(schema_path)
    require(schema["type"] == "object" and schema["additionalProperties"] is False and
            schema["required"] == [*WORDS, *HASHES], "public schema must be closed")
    require(schema["properties"] == {
        **{field: {"type": "string", "enum": allowed} for field, allowed in WORDS.items()},
        **{field: {"type": "string", "pattern": f"^{HASH_PATTERN}$", "minLength": 64, "maxLength": 64}
           for field in HASHES},
    }, "public schema differs from the word and hash inventories")

    ledger = load(HERE / "looks" / "LOOKS.json")
    require(ledger == {"schema": "joulewise.cadence_look_ledger.v1", "looks": [{
        "look_id": LOOK_ID, "manifest_path": registered_path,
        "sha256": sha256(manifest_path.read_bytes()).hexdigest(), "status": "draft",
    }]}, "draft ledger does not bind the manifest")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate",))
    parser.add_argument("--final", action="store_true", help="refused for an audit draft")
    args = parser.parse_args()
    if args.final:
        parser.exit(1, "REFUSE: transfer look is an audit draft pending registered v2 validation and Fable cold pass\n")
    manifest = HERE / "looks" / f"{LOOK_ID}.json"
    try:
        validate_draft(load(manifest), manifest)
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.exit(1, f"REFUSE {error}\n")
    print(f"{LOOK_ID}: audit draft, output schema, kit references and ledger validated.")


if __name__ == "__main__":
    main()
