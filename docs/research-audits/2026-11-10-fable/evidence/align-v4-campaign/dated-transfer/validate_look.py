"""Validate the audit draft only. This CLI has no look execution or finalization path."""
import argparse
from hashlib import sha256
import json
import re
import sys

from build_kits import HERE, ROOT

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from joulewise.cadence_looks.manifest_dispatch import PRE_READ_REFUSAL, validate_v2

LOOK_ID = "lm-transfer-01"
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
    validate_v2(json.dumps(doc).encode())
    require((doc["look_kind"], doc["look_id"], doc["status"]) == ("transfer", LOOK_ID, "draft"), "audit draft only")
    registered_path = doc["registered_paths"]["manifest"]
    require(doc["title"].startswith("DRAFT") and "effective freeze 2" in doc["title"], "draft hold missing")
    roster_path = HERE / "date-place-roster.json"
    reads = doc["reads"]
    verify_ref(reads["planned_date_places"], roster_path)
    roster = load(roster_path)
    require(len(roster["places"]) == len(reads["kits"]), "expected twenty date places in the roster")
    for place, (entry, row) in enumerate(zip(reads["kits"], roster["places"]), 1):
        kit_id = f"cl-transfer-{place:02}"
        require(row["date_place"] == place and row["kit_id"] == kit_id,
                "kit order must be the date-place order")
        kit_ref = {key: value for key, value in entry.items() if key != "kit_id"}
        require(kit_ref == row["kit"], f"kit ref differs from the roster: {kit_id}")
        verify_ref(kit_ref, HERE / "kits" / f"{kit_id}.v1.1.json")

    outputs = doc["outputs"]
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
        parser.exit(PRE_READ_REFUSAL, "REFUSE: audit draft awaits registration and Fable cold pass\n")
    manifest = HERE / "looks" / f"{LOOK_ID}.json"
    try:
        validate_draft(load(manifest), manifest)
    except (KeyError, OSError, TypeError, ValueError) as error:
        parser.exit(PRE_READ_REFUSAL, f"REFUSE {error}\n")
    print(f"{LOOK_ID}: audit draft, output schema, kit references and ledger validated.")


if __name__ == "__main__":
    main()
