"""RL-183 manifest and refusal contracts, exercised on public draft bytes and fixtures."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.cadence_looks import manifest_dispatch as dispatch

ROOT = Path(__file__).resolve().parents[1]
LOOKS = ROOT / (
    "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/"
    "looks"
)
DRAFT = LOOKS / "lm-transfer-01.manifest.json"
QUALIFICATION = LOOKS / "lm-qual-01.manifest.json"
INSTRUMENT = LOOKS / "lm-inst-01.manifest.json"
STABILITY = LOOKS / "lm-stab-01.manifest.json"
H = sha256(b"synthetic digest").hexdigest()
INTERIM_REF = "2f67206528f46d227815355ce701bd738233f647"
RAIL_SUM_COLUMNS = ["cpu_power", "gpu_power", "ane_power"]
CUSTODY = {
    INSTRUMENT: ["hold.json", "turn.json", "gain.json", "edges.json", "stdout", "stderr"],
    STABILITY: ["hold.json", "turn.json", "date_spreads.json", "context.json", "stdout", "stderr"],
}
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


def cli(*args):
    return subprocess.run(
        [sys.executable, "-B", "-m", "joulewise.cadence_looks.manifest_dispatch", "validate",
         *map(str, args)],
        cwd=ROOT, capture_output=True, check=False,
    )


def object_paths(value, path=()):
    if isinstance(value, dict):
        yield path
        for key, item in value.items():
            yield from object_paths(item, (*path, key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from object_paths(item, (*path, index))


class VariantContractTests(unittest.TestCase):
    def test_v2_variants_are_closed(self):
        for source in (QUALIFICATION, INSTRUMENT, STABILITY, DRAFT):
            original = json.loads(source.read_bytes())
            dispatch.validate_v2(source.read_bytes())
            for path in object_paths(original):
                document = deepcopy(original)
                target = document
                for step in path:
                    target = target[step]
                target["unexpected"] = 0
                with self.subTest(source=source.name, path=path), self.assertRaises(dispatch.ManifestError):
                    dispatch.validate_v2(encode(document))
            for other_kind in {"qualification", "description", "transfer"} - {original["look_kind"]}:
                with self.subTest(source=source.name, kind=other_kind), self.assertRaises(dispatch.ManifestError):
                    dispatch.validate_v2(encode(dict(original, look_kind=other_kind)))

    def test_dispatch_by_schema_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "unrelated-filename.json"
            for source in (QUALIFICATION, INSTRUMENT, STABILITY, DRAFT):
                with self.subTest(source=source.name):
                    candidate.write_bytes(source.read_bytes())
                    self.assertEqual(cli(candidate).returncode, 0)
                    document = json.loads(candidate.read_bytes())
                    candidate.write_bytes(encode(dict(document, schema="unknown")))
                    result = cli(candidate)
                    self.assertEqual((result.returncode, result.stdout), (2, b""))
                    self.assertIn(b"unknown cadence manifest schema ID", result.stderr)
                    candidate.write_bytes(encode(dict(document, schema=dispatch.V1)))
                    # A v1 delegation receives the original payload. It cannot
                    # be overridden via its v2 look_kind or filename.
                    v1_tool = Path(tmp) / "synthetic_v1.py"
                    v1_tool.write_text("raise SystemExit(17)\n", encoding="utf-8")
                    self.assertEqual(cli(candidate, "--v1-tool", v1_tool).returncode, 17)

    def test_final_refuses_pending_and_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "candidate.json"
            registration = Path(tmp) / "registration.json"
            for source in (QUALIFICATION, INSTRUMENT, STABILITY, DRAFT):
                document = json.loads(source.read_bytes())
                options = []
                if document["look_kind"] == "description":
                    document["status"] = "committed"
                else:
                    document["status"] = "registered"
                    registration.write_bytes(encode(document))
                    options = ["--registration", registration]
                valid = encode(document).replace(dispatch.REGISTRATION_PLACEHOLDER, json.dumps(H).encode())
                candidate.write_bytes(valid)
                result = cli("--final", candidate, *options)
                self.assertEqual(result.returncode, 0, result.stderr)
                for marker in ("PENDING:CODE", "OPEN-19"):
                    list_trial = json.loads(valid)
                    output_list = "energy_dependent_words" if source == QUALIFICATION else "custody_names"
                    list_trial["outputs"][output_list].append(marker)
                    key_trial = json.loads(valid)
                    key_trial["outputs"][marker] = "synthetic"
                    changed = (
                        dict(json.loads(valid), title=f"before {marker} after"),
                        list_trial,
                        key_trial,
                    )
                    for index, trial in enumerate(changed):
                        with self.subTest(source=source.name, marker=marker, index=index):
                            candidate.write_bytes(encode(trial))
                            result = cli("--final", candidate, *options)
                            self.assertEqual((result.returncode, result.stdout), (2, b""))
                            self.assertIn(marker.encode(), result.stderr)

    def test_filler_ban_by_kind(self):
        for source, mutate in (
            (QUALIFICATION, lambda doc: doc["reads"]["blocks"][0].update(block_id="f2-inst-01")),
            (DRAFT, lambda doc: doc["reads"]["kits"][0].update(kit_id="f2-stab-01")),
            (INSTRUMENT, lambda doc: doc["kits"][0].update(kit_id="cl-transfer-01")),
            (STABILITY, lambda doc: doc["kits"][0].update(kit_id="hp-02")),
        ):
            with self.subTest(source=source.name):
                document = dispatch.validate_v2(source.read_bytes())
                mutate(document)
                with self.assertRaises(dispatch.ManifestError):
                    dispatch.validate_v2(encode(document))

    def test_description_shape(self):
        for source, custody in CUSTODY.items():
            document = dispatch.validate_v2(source.read_bytes())
            self.assertEqual(document["outputs"]["custody_names"], custody)
            self.assertEqual(set(document["channels"]), {"gpu_rail", "rail_sum", "dc_in"})
            counts = ["n_legs"] if source == INSTRUMENT else ["n_legs", "n_local_dates"]
            self.assertEqual(document["outputs"]["counts"], counts)
            self.assertEqual(document["outputs"]["hashes"], ["manifest_sha256", "stage1_sha256"])
            self.assertEqual(document["outputs"]["identifiers"], ["look_id", "commit"])
            self.assertEqual({pin["sha256"] for pin in document["code_pins"].values()}, {"PENDING:CODE"})
            for mutate in (
                lambda doc: doc["channels"].__setitem__(0, "wall"),
                lambda doc: doc.update(fit={}),
                lambda doc: doc.update(freeze1={}),
                lambda doc: doc["outputs"].update(words=[]),
                lambda doc: doc["outputs"]["custody_names"].remove("stderr"),
                lambda doc: doc["kits"].pop(),
                lambda doc: doc.update(kit_index_path="f2-stab/KITS.json"),
            ):
                trial = deepcopy(document)
                mutate(trial)
                with self.subTest(source=source.name, trial=mutate), self.assertRaises(dispatch.ManifestError):
                    dispatch.validate_v2(encode(trial))

        later = json.loads(STABILITY.read_bytes())
        later.update(look_id="lm-stab-02", status="committed")
        for pin in later["code_pins"].values():
            pin["sha256"] = H
        with self.assertRaisesRegex(dispatch.ManifestError, "KITS.json index"):
            dispatch.validate_v2(encode(later), final=True)
        later["kit_index_path"] = "f2-stab/KITS.json"
        self.assertEqual(dispatch.validate_v2(encode(later), final=True)["outputs"]["custody_names"],
                         CUSTODY[STABILITY])

    def test_rail_sum_columns_follow_rl185(self):
        for source in CUSTODY:
            original = json.loads(source.read_bytes())
            for final in (False, True):
                document = deepcopy(original)
                if final:
                    document["status"] = "committed"
                    for pin in document["code_pins"].values():
                        pin["sha256"] = H
                with self.subTest(source=source.name, final=final):
                    valid = dispatch.validate_v2(encode(document), final=final)
                    self.assertEqual(valid.get("rail_sum_columns"), RAIL_SUM_COLUMNS)
                    for columns in (
                        ["gpu_power"],
                        ["cpu_power", "gpu_power", "gpu_power"],
                        list(reversed(RAIL_SUM_COLUMNS)),
                        ["cpu_power", "gpu_power", "other_power"],
                    ):
                        trial = dict(document, rail_sum_columns=columns)
                        with self.subTest(columns=columns), self.assertRaisesRegex(
                            dispatch.ManifestError, "rail_sum_columns"
                        ):
                            dispatch.validate_v2(encode(trial), final=final)
                    del document["rail_sum_columns"]
                    with self.assertRaisesRegex(dispatch.ManifestError, "rail_sum_columns"):
                        dispatch.validate_v2(encode(document), final=final)
                    document["channels"].remove("rail_sum")
                    dispatch.validate_v2(encode(document), final=final)

    def test_registered_bytes_unchanged(self):
        self.assertEqual(
            sha256(QUALIFICATION.read_bytes()).hexdigest(),
            "d6fde6918023ea69051da45a6b0e3c06ffcfdafd8975a1773989324fa7c9bdab",
        )
        self.assertEqual(
            subprocess.check_output(
                ["git", "hash-object", "joulewise/cadence_looks/qualification_manifest.py"], cwd=ROOT,
            ).strip(),
            b"35bbd6b2f5f2db62e401038afa4290491c5fc282",
        )

        def tree(ref):
            result = subprocess.run(
                ["git", "ls-tree", "-r", ref, "--", "docs/process/cadence/looks", "joulewise/cadence_looks"],
                cwd=ROOT, capture_output=True, check=False,
            )
            return result, dict(line.split(b"\t")[::-1] for line in result.stdout.splitlines())

        result, interim = tree(INTERIM_REF)
        if result.returncode:
            # Hosted CI may fetch only the PR head.
            return
        result, current = tree("HEAD")
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in (interim.keys() & current.keys()) - {b"docs/process/cadence/looks/LOOKS.json"}:
            self.assertEqual(current[path], interim[path], path)


class TransferManifestTests(unittest.TestCase):
    def test_integrated_v1_schema_retains_interim_pin(self):
        legacy = dispatch.V2_SCHEMA.with_name("look_manifest.schema.json")
        if not legacy.exists():
            self.skipTest("v1 schema lives on the separate interim line")
        self.assertIn(sha256(legacy.read_bytes()).hexdigest(), V1_SCHEMA_PINS)

    def test_transfer_candidate_validates(self):
        schema = json.loads(dispatch.V2_SCHEMA.read_bytes())
        self.assertEqual(
            schema["oneOf"],
            [{"$ref": f"#/$defs/{kind}"} for kind in ("qualification", "description", "transfer")],
        )
        for kind in ("qualification", "description", "transfer"):
            self.assertIs(schema["$defs"][kind]["additionalProperties"], False)
        document = dispatch.validate_v2(DRAFT.read_bytes())
        self.assertEqual(document["status"], "draft")
        self.assertEqual(document["registered_paths"]["manifest"], str(DRAFT.relative_to(ROOT)))
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
            "rail_sum_columns": RAIL_SUM_COLUMNS,
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
