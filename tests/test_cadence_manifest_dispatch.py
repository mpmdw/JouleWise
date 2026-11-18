"""RL-183 manifest and refusal contracts, exercised on public draft bytes and fixtures."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import unittest

from joulewise.cadence_looks import manifest_dispatch as dispatch

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / (
    "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/"
    "dated-transfer/looks/lm-transfer-01.json"
)
H = sha256(b"synthetic digest").hexdigest()
V1_SCHEMA_PINS = {
    "5c0724bd39cb41d2a0e155de31b9930a850286d395213e658be3e0e0e231b723",  # 9a7defbb
    "78f312feb24e3ee95ac8bdd386cdb38f56fc0ab6846d27edc66f522f3a7acd3d",  # f09469894
}


def encode(document):
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode()


def registered_fixture():
    draft = json.loads(DRAFT.read_bytes())
    draft.update(status="registered", title="Synthetic registration fixture")
    return encode(draft)


class TransferManifestTests(unittest.TestCase):
    def test_integrated_v1_schema_retains_interim_pin(self):
        legacy = dispatch.V2_SCHEMA.with_name("look_manifest.schema.json")
        if not legacy.exists():
            self.skipTest("v1 schema lives on the separate interim line")
        self.assertIn(sha256(legacy.read_bytes()).hexdigest(), V1_SCHEMA_PINS)

    def test_schema_inventory_and_draft(self):
        schema = json.loads(dispatch.V2_SCHEMA.read_bytes())
        self.assertEqual(
            schema["oneOf"],
            [{"$ref": f"#/$defs/{kind}"} for kind in ("qualification", "description", "transfer")],
        )
        for kind in ("qualification", "description", "transfer"):
            self.assertIs(schema["$defs"][kind]["additionalProperties"], False)
        document = dispatch.validate_v2(DRAFT.read_bytes())
        self.assertEqual(document["status"], "draft")
        outputs = document["outputs"]
        self.assertEqual(outputs["custody_names"], ["scores.json", "stdout", "stderr"])
        self.assertEqual(outputs["pre_read_refusal_exit_status"], 2)
        self.assertEqual(outputs["after_read_failure"]["exit_status"], 1)
        self.assertEqual(outputs["after_read_failure"]["stderr_lines"],
                         ["stage2_error", "<allowed error type or OtherError>"])

    def test_final_validation_changes_only_literal_hash_slots(self):
        registered = registered_fixture()
        final = registered.replace(dispatch.REGISTRATION_PLACEHOLDER, json.dumps(H).encode())
        self.assertEqual(dispatch.validate_v2(final, final=True, registration=registered)["look_kind"], "transfer")
        with self.assertRaisesRegex(dispatch.ManifestError, "registered manifest bytes"):
            dispatch.validate_v2(final, final=True)
        with self.assertRaisesRegex(dispatch.ManifestError, "PENDING:CODE"):
            dispatch.validate_v2(registered, final=True, registration=registered)

        edits = (
            (b"Synthetic registration fixture", b"Changed scientific text"),
            (b'"max_dates": 20,', b'"max_dates": 19,'),
            (b'"level": 0.9,', b'"level": 0.95,'),
            (b'"level": 0.9,', b'"level": 0.90,'),
            (b'"schema": ', b'"schema":  '),
        )
        for original, changed in edits:
            with self.subTest(original=original), self.assertRaises(dispatch.ManifestError):
                self.assertIn(original, final)
                dispatch.validate_v2(final.replace(original, changed, 1), final=True, registration=registered)
        with self.assertRaisesRegex(dispatch.ManifestError, "literal JSON strings"):
            dispatch.validate_v2(
                final, final=True,
                registration=registered.replace(dispatch.REGISTRATION_PLACEHOLDER, b'"PENDING\\u003aCODE"', 1),
            )

    def test_closed_contract_refuses_extra_and_changed_fields(self):
        fixture = json.loads(DRAFT.read_bytes())
        cases = [
            ("training", lambda d: d.update(fit={})),
            ("word", lambda d: d["outputs"]["words"].update(qualified=["yes"])),
            ("custody", lambda d: d["outputs"]["custody_names"].append("extra.json")),
            ("pre-read", lambda d: d["outputs"].update(pre_read_refusal_exit_status=1)),
            ("post-read", lambda d: d["outputs"]["after_read_failure"].update(exit_status=2)),
            ("rule", lambda d: d["outputs"]["after_read_failure"].update(stderr_lines=["detail"])),
            ("interval", lambda d: d["estimate"]["interval"].update(series="absolute_daily_error")),
            ("ordered family", lambda d: d["reads"]["kits"].reverse()),
            ("missing print", lambda d: d["estimate"]["restricted_prints"].pop()),
            ("repeated print", lambda d: d["estimate"]["restricted_prints"].__setitem__(
                0, d["estimate"]["restricted_prints"][1])),
            ("print destination", lambda d: d["estimate"]["restricted_prints"][0].update(destination="PUBLIC.json")),
            ("placeholder text", lambda d: d.update(title="OPEN-4")),
        ]
        for label, change in cases:
            with self.subTest(label=label), self.assertRaises(dispatch.ManifestError):
                trial = deepcopy(fixture)
                change(trial)
                dispatch.validate_v2(encode(trial))

    def test_duplicate_keys_refused(self):
        payload = DRAFT.read_bytes().replace(b'"status": "draft",', b'"status": "draft", "status": "registered",', 1)
        with self.assertRaisesRegex(dispatch.ManifestError, "duplicate JSON key"):
            dispatch.validate_v2(payload)

    def test_entrypoint_draft_and_pre_read_refusal(self):
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = dispatch.main(["validate", str(DRAFT)])
        self.assertEqual((status, stdout.getvalue(), stderr.getvalue()), (0, "ok lm-transfer-01 (draft)\n", ""))
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = dispatch.main(["validate", "--final", str(DRAFT)])
        self.assertEqual((status, stdout.getvalue()), (2, ""))
        self.assertIn("draft cannot pass final validation", stderr.getvalue())


class DescriptionManifestTests(unittest.TestCase):
    def test_closed_description_is_separate_from_transfer(self):
        pin = {"path": "synthetic/file", "sha256": H}
        names = ["hold.json", "turn.json", "gain.json", "edges.json"]
        fixture = {
            "schema": dispatch.V2, "look_kind": "description", "status": "committed",
            "look_id": "lm-inst-01", "title": "Synthetic design", "rulings": ["RL-181 §2.1"],
            "kits": [{"kit_id": f"f2-inst-{i:02}", "sha256": H} for i in range(1, 4)],
            "channels": ["gpu_rail", "rail_sum", "dc_in"], "when": "after effective freeze 2",
            "stage1": "Synthetic operational roster",
            "freeze2": {"look_id": "lm-interim-01", "hash_key": "freeze2_sha256", "authority": "RL-183 §2.3"},
            "prints": [{"description": name, "destination": name} for name in names],
            "code_pins": dict.fromkeys(("reader", "manifest_schema", "stage1_schema", "output_schema"), pin),
            "outputs": {
                "public_file": "PUBLIC.json", "hashes": ["manifest_sha256", "stage1_sha256"],
                "identifiers": ["look_id", "commit"], "counts": ["n_legs"],
                "custody_names": [*names, "stdout", "stderr"],
            },
        }
        self.assertEqual(dispatch.validate_v2(encode(fixture), final=True)["look_kind"], "description")
        bad = deepcopy(fixture)
        bad["kits"][0]["kit_id"] = "cl-transfer-01"
        with self.assertRaises(dispatch.ManifestError):
            dispatch.validate_v2(encode(bad), final=True)
        fixture["outputs"]["words"] = {}
        with self.assertRaises(dispatch.ManifestError):
            dispatch.validate_v2(encode(fixture), final=True)


if __name__ == "__main__":
    unittest.main()
