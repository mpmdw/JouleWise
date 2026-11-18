"""RL-183 manifest validation and refusals on standalone synthetic inputs."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from hashlib import sha256
from io import StringIO
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import manifest_dispatch as dispatch
from tests.test_qualification_manifest import MANIFEST, _final_bytes

H = sha256(b"synthetic digest").hexdigest()
V1_SCHEMA_PINS = {
    "5c0724bd39cb41d2a0e155de31b9930a850286d395213e658be3e0e0e231b723",  # 9a7defbb
    "78f312feb24e3ee95ac8bdd386cdb38f56fc0ab6846d27edc66f522f3a7acd3d",  # f09469894
}


def encode(document):
    return (json.dumps(document, indent=2, ensure_ascii=False) + "\n").encode()


def transfer_fixture(status="draft"):
    text = "Synthetic contract fixture"
    registry = "docs/process/cadence/looks"
    return {
        "schema": dispatch.V2,
        "look_kind": "transfer",
        "look_id": "lm-transfer-01",
        "status": status,
        "title": text,
        "rulings": ["RL-183 §3.2"],
        "registered_paths": {"manifest": f"{registry}/lm-transfer-01.json", "ledger": f"{registry}/LOOKS.json"},
        "registration": dict.fromkeys(("before", "final", "review"), text),
        "reads": {
            "planned_date_places": {"path": "synthetic/roster.json", "sha256": H},
            "kits": [
                {"kit_id": f"cl-transfer-{place:02}", "path": f"synthetic/kit-{place}.json", "sha256": H}
                for place in range(1, 21)
            ],
            "timezone": "America/Los_Angeles", "max_dates": 20, "max_legs": 120,
            **dict.fromkeys(("leg_budget", "opportunity", "stop", "when", "stage1"), text),
            "freeze2": {"look_id": "lm-interim-01", "hash_key": "freeze2_sha256", "authority": text},
        },
        "inclusion": {
            "stage1": text, "stage2": text, "tail_rule": text,
            "short_legs": [
                {"decode_cap": 3724, "closing_stamp": 3583, "last_token_stamp": 3723, "gaps": 140},
                {"decode_cap": 3151, "closing_stamp": 3071, "last_token_stamp": 3150, "gaps": 79},
            ],
        },
        "estimate": {
            "channels": ["gpu_rail", "dc_in"],
            "daily_error": "(sum(predicted) - sum(measured)) / sum(measured)",
            "minimum_hot_legs_per_date": 3,
            **dict.fromkeys(("denominator", "across_dates", "support", "pair_description"), text),
            "interval": {
                "series": "signed_daily_error", "level": 0.9, "quantile": 0.95, "ddof": 1,
                "formula": "mean(e) ± t(0.95, D - 1) × SD(e, ddof=1) / sqrt(D)", "minimum_dates": 2,
            },
            "comparison_only_abs_error_cutoff": 0.02,
            "restricted_prints": [
                {"id": name, "description": text, "destination": "scores.json"} for name in dispatch.TRANSFER_PRINTS
            ],
        },
        "code_pins": {
            "predictor_equivalence": text,
            **{key: {"path": f"synthetic/{key}", "sha256": "PENDING:CODE"} for key in (
                "predictor", "inclusion", "scorer", "manifest_schema", "stage1_schema", "output_schema",
                "validator", "schema_validator", "release_boundary",
            )},
        },
        "outputs": {
            "public_file": "PUBLIC.json", "audit_output_schema": {"path": "synthetic/public.json", "sha256": H},
            "words": {"transfer_interval": ["estimated", "not_evaluable"], "stage2_error": ["no"]},
            "hashes": ["manifest_sha256", "stage1_roster_sha256", "freeze2_sha256"],
            "interval_status_rule": text, "custody_names": ["scores.json", "stdout", "stderr"],
            "after_read_failure": {
                "stderr_lines": ["stage2_error", "<allowed error type or OtherError>"],
                "type_allowlist": ["builtins", "numpy.linalg.LinAlgError", "json.JSONDecodeError", "OtherError"],
                "exit_status": 1, "behavior": text,
            },
            "pre_read_refusal_exit_status": 2,
        },
        "reservation": dict.fromkeys(("host", "preflight", "exclusive", "spent_id"), text),
        "cold_pass_checks": [text],
    }


class SchemaPinTests(unittest.TestCase):
    def test_integrated_v1_schema_retains_interim_pin(self):
        legacy = dispatch.V2_SCHEMA.with_name("look_manifest.schema.json")
        if not legacy.exists():
            self.skipTest("v1 schema lives on the separate interim line")
        self.assertIn(sha256(legacy.read_bytes()).hexdigest(), V1_SCHEMA_PINS)

    def test_missing_transfer_variant_refuses_before_shape_validation(self):
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="transfer-unavailable-")))
        schema = tmp / "manifest.schema.json"
        schema.write_bytes(encode({"$defs": {}}))
        with patch.object(dispatch, "V2_SCHEMA", schema):
            with self.assertRaisesRegex(dispatch.ManifestError, "does not define the transfer variant"):
                dispatch.validate_v2(encode(transfer_fixture()))


class TransferManifestTests(unittest.TestCase):
    def setUp(self):
        definitions = json.loads(dispatch.V2_SCHEMA.read_bytes())["$defs"]
        if "transfer" not in definitions:
            self.skipTest("the approved transfer schema variant is pending")

    def test_schema_inventory_and_draft(self):
        schema = json.loads(dispatch.V2_SCHEMA.read_bytes())
        self.assertEqual(
            schema["oneOf"],
            [{"$ref": f"#/$defs/{kind}"} for kind in ("qualification", "description", "transfer")],
        )
        for kind in ("qualification", "description", "transfer"):
            self.assertIs(schema["$defs"][kind]["additionalProperties"], False)
        document = dispatch.validate_v2(encode(transfer_fixture()))
        self.assertEqual(document["status"], "draft")
        outputs = document["outputs"]
        self.assertEqual(outputs["custody_names"], ["scores.json", "stdout", "stderr"])
        self.assertEqual(outputs["pre_read_refusal_exit_status"], 2)
        self.assertEqual(outputs["after_read_failure"]["exit_status"], 1)
        self.assertEqual(outputs["after_read_failure"]["stderr_lines"],
                         ["stage2_error", "<allowed error type or OtherError>"])

    def test_final_validation_changes_only_literal_hash_slots(self):
        registered = encode(transfer_fixture("registered"))
        final = registered.replace(dispatch.REGISTRATION_PLACEHOLDER, json.dumps(H).encode())
        self.assertEqual(dispatch.validate_v2(final, final=True, registration=registered)["look_kind"], "transfer")
        with self.assertRaisesRegex(dispatch.ManifestError, "registered manifest bytes"):
            dispatch.validate_v2(final, final=True)
        with self.assertRaisesRegex(dispatch.ManifestError, "PENDING:CODE"):
            dispatch.validate_v2(registered, final=True, registration=registered)

        edits = (
            (b"Synthetic contract fixture", b"Changed scientific text"),
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
        fixture = transfer_fixture()
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
        payload = encode(transfer_fixture()).replace(b'"status": "draft",', b'"status": "draft", "status": "registered",', 1)
        with self.assertRaisesRegex(dispatch.ManifestError, "duplicate JSON key"):
            dispatch.validate_v2(payload)

    def test_entrypoint_draft_and_pre_read_refusal(self):
        tmp = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="transfer-dispatch-")))
        draft = tmp / "manifest.json"
        draft.write_bytes(encode(transfer_fixture()))
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = dispatch.main(["validate", str(draft)])
        self.assertEqual((status, stdout.getvalue(), stderr.getvalue()), (0, "ok lm-transfer-01 (draft)\n", ""))
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = dispatch.main(["validate", "--final", str(draft)])
        self.assertEqual((status, stdout.getvalue()), (2, ""))
        self.assertIn("draft cannot pass final validation", stderr.getvalue())


class QualificationDispatchTests(unittest.TestCase):
    def test_pr_821_manifest_bytes_validate_through_dispatch(self):
        registered = MANIFEST.read_bytes()
        doc = dispatch.validate_v2(registered)
        self.assertEqual((doc["look_id"], doc["status"]), ("lm-qual-01", "registered"))
        candidate = _final_bytes(registered)
        self.assertEqual(dispatch.validate_v2(candidate, final=True, registration=registered)["look_id"], "lm-qual-01")


class DescriptionManifestTests(unittest.TestCase):
    def test_closed_description_is_separate_from_transfer(self):
        definitions = json.loads(dispatch.V2_SCHEMA.read_bytes())["$defs"]
        if "description" not in definitions:
            self.skipTest("the approved description schema variant is pending")
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
