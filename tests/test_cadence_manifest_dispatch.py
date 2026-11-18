"""RL-183 manifest and refusal contracts, exercised on public draft bytes and fixtures."""

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from hashlib import sha256
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

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


def _buffering_environment(unbuffered):
    environment = os.environ.copy()
    if unbuffered:
        environment["PYTHONUNBUFFERED"] = "1"
    else:
        environment.pop("PYTHONUNBUFFERED", None)
    return environment


def run_with_closed_consumer(command, *, channel, unbuffered):
    reader, writer = os.pipe()
    os.close(reader)
    with os.fdopen(writer, "wb") as sink:
        streams = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE}
        streams[channel] = sink
        return subprocess.run(
            command, cwd=ROOT, env=_buffering_environment(unbuffered), check=False, **streams,
        )


def cli_with_closed_consumer(*args, channel, unbuffered):
    command = [sys.executable, "-B", "-m", "joulewise.cadence_looks.manifest_dispatch", *map(str, args)]
    return run_with_closed_consumer(command, channel=channel, unbuffered=unbuffered)


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
                    candidate.write_bytes(encode(dict(document, schema=dispatch.V1, look_id="lm-interim-01")))
                    # A v1 delegation receives the original payload. It cannot
                    # be overridden via its v2 look_kind or filename.
                    v1_tool = Path(tmp) / "synthetic_v1.py"
                    v1_tool.write_text("print('synthetic legacy delegation')\nraise SystemExit(17)\n",
                                       encoding="utf-8")
                    legacy = cli(candidate, "--v1-tool", v1_tool)
                    self.assertEqual((legacy.returncode, legacy.stdout), (2, b"synthetic legacy delegation\n"))

    def test_dispatch_refusals_survive_disconnected_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            unknown = folder / "unknown.json"
            unknown.write_bytes(encode({"schema": "unknown"}))
            interim = folder / "interim.json"
            interim.write_bytes(encode({"schema": dispatch.V1, "look_id": "lm-interim-01"}))
            v1_tool = folder / "legacy.py"
            v1_tool.write_text(
                "import sys\nprint('synthetic legacy refusal', file=sys.stderr)\nraise SystemExit(1)\n",
                encoding="utf-8",
            )
            for route, args in (
                ("validate", ["validate", unknown]),
                ("transfer final", ["validate", "--final", DRAFT]),
                ("qualification final", ["validate", "--final", QUALIFICATION]),
                ("description final", ["validate", "--final", INSTRUMENT]),
                ("root parser", []),
                ("validate parser", ["validate", DRAFT, "--unknown"]),
                ("delegated v1 final", ["validate", "--final", interim, "--v1-tool", v1_tool]),
            ):
                for unbuffered in (False, True):
                    with self.subTest(route=route, unbuffered=unbuffered):
                        result = cli_with_closed_consumer(*args, channel="stderr", unbuffered=unbuffered)
                        self.assertEqual((result.returncode, result.stdout), (2, b""))
            connected = cli(interim, "--v1-tool", v1_tool, "--final")
            self.assertEqual((connected.returncode, connected.stderr), (2, b"synthetic legacy refusal\n"))

    def test_dispatch_stdout_notices_survive_disconnected_reader(self):
        for args in (["validate", DRAFT], ["--help"], ["validate", "--help"]):
            for unbuffered in (False, True):
                with self.subTest(args=args, unbuffered=unbuffered):
                    result = cli_with_closed_consumer(*args, channel="stdout", unbuffered=unbuffered)
                    self.assertEqual((result.returncode, result.stderr), (2, b""))

    def test_dispatch_exits_two_with_descriptor_exhaustion(self):
        script = """
from contextlib import redirect_stdout
from io import StringIO
import resource
import sys
from joulewise.cadence_looks import manifest_dispatch

prime = getattr(manifest_dispatch, "_dispatch", manifest_dispatch.main)
with redirect_stdout(StringIO()):
    assert prime(["validate", sys.argv[1]]) == 0
_, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
resource.setrlimit(resource.RLIMIT_NOFILE, (3, hard))
manifest_dispatch.main(["validate", "--final", sys.argv[1]])
raise SystemExit(97)
"""
        command = [sys.executable, "-B", "-c", script, str(DRAFT)]
        for unbuffered in (False, True):
            with self.subTest(unbuffered=unbuffered):
                connected = subprocess.run(command, cwd=ROOT, env=_buffering_environment(unbuffered),
                                           capture_output=True, check=False)
                self.assertEqual((connected.returncode, connected.stdout), (2, b""))
                self.assertIn(b"Too many open files", connected.stderr)
                disconnected = run_with_closed_consumer(command, channel="stderr", unbuffered=unbuffered)
                self.assertEqual((disconnected.returncode, disconnected.stdout), (2, b""))

    def test_oversized_json_integer_refuses_before_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "numeric.json"
            draft = DRAFT.read_bytes()
            field = b'"max_dates": 20'
            self.assertEqual(draft.count(field), 1)
            environment = os.environ.copy()
            environment.pop("PYTHONINTMAXSTRDIGITS", None)
            limit = sys.int_info.default_max_str_digits
            for digits in (limit, limit + 1):
                candidate.write_bytes(draft.replace(field, b'"max_dates": ' + b"1" * digits))
                command = [sys.executable, "-B", "-m", "joulewise.cadence_looks.manifest_dispatch",
                           "validate", "--final", str(candidate)]
                with self.subTest(digits=digits):
                    result = subprocess.run(command, env=environment, cwd=ROOT, capture_output=True, check=False)
                    self.assertEqual((result.returncode, result.stdout), (2, b""))
                    self.assertTrue(result.stderr.startswith(b"REFUSE "))

    def test_dispatch_boundary_contains_arbitrary_pre_read_exceptions(self):
        script = """
from pathlib import Path
import sys
from unittest.mock import patch
from joulewise.cadence_looks import manifest_dispatch as dispatch

class InjectedFailure(BaseException):
    pass

def fail(*args, **kwargs):
    raise InjectedFailure("synthetic injected failure")

def exit_during_parse(*args, **kwargs):
    raise SystemExit(0)

step, candidate, registration = sys.argv[1:]
read_bytes = Path.read_bytes

def fail_registration(path):
    if path == Path(registration):
        fail()
    return read_bytes(path)

target, name, inject = {
    "parser": (dispatch, "_NoticeArgumentParser", fail),
    "parser-system-exit": (dispatch._NoticeArgumentParser, "parse_args", exit_during_parse),
    "candidate-open": (Path, "read_bytes", fail),
    "decode": (dispatch.schema_check, "_decode", fail),
    "validate": (dispatch, "_validate_v2_document", fail),
    "registration-open": (Path, "read_bytes", fail_registration),
    "legacy-delegation": (dispatch, "_validate_legacy", fail),
    "success-notice": (dispatch, "finish_notice", fail),
}[step]
argv = ["validate", candidate]
if step == "registration-open":
    argv += ["--final", "--registration", registration]
with patch.object(target, name, inject):
    dispatch.main(argv)
raise SystemExit(97)
"""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registration = root / "registered.json"
            registration.write_bytes(registered_fixture())
            final = root / "final.json"
            final.write_bytes(registration.read_bytes().replace(
                dispatch.REGISTRATION_PLACEHOLDER, json.dumps(H).encode()
            ))
            interim = root / "interim.json"
            interim.write_bytes(encode({"schema": dispatch.V1, "look_id": "lm-interim-01"}))
            for step, source in (
                ("parser", DRAFT), ("parser-system-exit", DRAFT), ("candidate-open", DRAFT), ("decode", DRAFT),
                ("validate", DRAFT), ("registration-open", final),
                ("legacy-delegation", interim), ("success-notice", DRAFT),
            ):
                with self.subTest(step=step):
                    result = subprocess.run([sys.executable, "-B", "-c", script, step,
                                             str(source), str(registration)], cwd=ROOT,
                                            capture_output=True, check=False)
                    self.assertEqual((result.returncode, result.stdout), (2, b""))
                    self.assertNotIn(b"Traceback", result.stderr)

    def test_v1_refuses_v2_look_ids_and_final_markers_before_delegating(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "interim.json"
            tool = Path(tmp) / "legacy.py"
            tool.write_text("raise SystemExit(0)\n", encoding="utf-8")
            interim = {
                "schema": dispatch.V1,
                "look_kind": "interim",
                "look_id": "lm-interim-01",
                "status": "committed",
                "title": "Synthetic interim final",
            }
            args = ["validate", str(candidate), "--v1-tool", str(tool)]
            candidate.write_bytes(encode(interim))
            self.assertEqual(cli(candidate, "--v1-tool", tool, "--final").returncode, 0)

            with patch.object(dispatch.subprocess, "run") as delegate:
                for look_id in ("lm-transfer-01", "lm-qual-01", "lm-qual-42",
                                "lm-inst-01", "lm-stab-01", "lm-stab-02"):
                    for flags in ([], ["--final"]):
                        candidate.write_bytes(encode(dict(interim, look_id=look_id)))
                        with self.subTest(look_id=look_id, flags=flags), redirect_stderr(StringIO()) as stderr:
                            self.assertEqual(dispatch._dispatch([*args, *flags]), 2)
                            self.assertIn("reserved for v2", stderr.getvalue())
                for variant in (
                    dict(interim, title="OPEN-19"),
                    dict(interim, rulings=[["PENDING:CODE"]]),
                    dict(interim, review={"OPEN-19": "synthetic"}),
                ):
                    candidate.write_bytes(encode(variant))
                    with self.subTest(variant=variant), redirect_stderr(StringIO()) as stderr:
                        self.assertEqual(dispatch._dispatch([*args, "--final"]), 2)
                        self.assertIn("final manifest contains", stderr.getvalue())
                delegate.assert_not_called()

    def test_v1_delegate_receives_checked_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "interim.json"
            tool = Path(tmp) / "legacy.py"
            tool.touch()
            interim = {"schema": dispatch.V1, "look_kind": "interim", "look_id": "lm-interim-01"}
            payload = encode(interim)
            candidate.write_bytes(payload)

            def delegate(command, *, check, capture_output, text, encoding, errors):
                candidate.write_bytes(encode(dict(interim, look_id="lm-transfer-01")))
                self.assertEqual(Path(command[4]).read_bytes(), payload)
                self.assertTrue(capture_output)
                return subprocess.CompletedProcess(command, 0)

            with patch.object(dispatch.subprocess, "run", side_effect=delegate):
                self.assertEqual(dispatch._dispatch(["validate", str(candidate), "--v1-tool", str(tool)]), 0)

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

    def test_kit_commitments_refuse_relabelling_and_substituted_paths(self):
        transfer = json.loads(DRAFT.read_bytes())
        filler = json.loads(INSTRUMENT.read_bytes())["kits"][0]
        true_kit = transfer["reads"]["kits"][0]
        filler_path = str(
            LOOKS.relative_to(ROOT).parent / "item-drafts-f2/f2-inst-01.v1.1.json"
        )
        for substitute in (
            {"path": filler_path, "sha256": filler["sha256"]},
            {"path": filler_path},
            {"sha256": filler["sha256"]},
            {"sha256": transfer["reads"]["kits"][1]["sha256"]},
        ):
            trial = deepcopy(transfer)
            trial["reads"]["kits"][0].update(substitute)
            with self.subTest(substitute=substitute, status="draft"), self.assertRaisesRegex(
                dispatch.ManifestError, "cl-transfer-01.*commitment"
            ):
                dispatch.validate_v2(encode(trial))
            trial["status"] = "registered"
            registration = encode(trial)
            final = registration.replace(dispatch.REGISTRATION_PLACEHOLDER, json.dumps(H).encode())
            with self.subTest(substitute=substitute, status="registered"), self.assertRaises(dispatch.ManifestError):
                dispatch.validate_v2(registration)
            with self.subTest(substitute=substitute, status="final"), self.assertRaises(dispatch.ManifestError):
                dispatch.validate_v2(final, final=True, registration=registration)
            valid_final = registered_fixture().replace(dispatch.REGISTRATION_PLACEHOLDER, json.dumps(H).encode())
            with self.subTest(substitute=substitute, status="registration only"), self.assertRaisesRegex(
                dispatch.ManifestError, "cl-transfer-01.*commitment"
            ):
                dispatch.validate_v2(valid_final, final=True, registration=registration)

        for source in (INSTRUMENT, STABILITY):
            original = json.loads(source.read_bytes())
            for digest in (true_kit["sha256"], original["kits"][1]["sha256"]):
                trial = deepcopy(original)
                kit = trial["kits"][0]
                kit["sha256"] = digest
                with self.subTest(source=source.name, status="draft"), self.assertRaisesRegex(
                    dispatch.ManifestError, f"{kit['kit_id']}.*commitment"
                ):
                    dispatch.validate_v2(encode(trial))
                trial["status"] = "committed"
                final = encode(trial).replace(dispatch.REGISTRATION_PLACEHOLDER, json.dumps(H).encode())
                with self.subTest(source=source.name, status="final"), self.assertRaises(dispatch.ManifestError):
                    dispatch.validate_v2(final, final=True)

        transfer["reads"]["planned_date_places"]["sha256"] = H
        with self.assertRaisesRegex(dispatch.ManifestError, "date-place roster commitment"):
            dispatch.validate_v2(encode(transfer))
        qualification = json.loads(QUALIFICATION.read_bytes())
        qualification["reads"]["blocks"][0]["kit_sha256"] = filler["sha256"]
        with self.assertRaisesRegex(dispatch.ManifestError, "kit SHA-256 differs"):
            dispatch.validate_v2(encode(qualification))

    def test_rejects_unused_registration_before_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            registration = Path(tmp) / "RESTRICTED" / "coefficients.json"
            description = Path(tmp) / "description.json"
            payload = json.loads(INSTRUMENT.read_bytes())
            payload["status"] = "committed"
            for pin in payload["code_pins"].values():
                pin["sha256"] = H
            description.write_bytes(encode(payload))
            read_bytes = Path.read_bytes

            def guard(path):
                if path == registration:
                    raise AssertionError("unneeded registration reached open")
                return read_bytes(path)

            for candidate, flags in (
                (description, ["--final"]),
                (DRAFT, ["--final"]),
                (QUALIFICATION, []),
            ):
                with self.subTest(candidate=candidate.name), patch.object(Path, "read_bytes", guard):
                    with redirect_stderr(StringIO()) as stderr:
                        status = dispatch._dispatch(["validate", str(candidate), *flags, "--registration", str(registration)])
                    self.assertEqual(status, 2)
                    self.assertIn("--registration", stderr.getvalue())

    def test_qualification_span_commitments_refuse_altered_registration(self):
        authentic = QUALIFICATION.read_bytes()
        original = json.loads(authentic)
        for spans in (
            ["f2-inst-01-l004", "f2-inst-01-l005"],
            original["reads"]["blocks"][1]["spans"],
            [original["reads"]["blocks"][0]["spans"][0]] * 2,
        ):
            trial = deepcopy(original)
            trial["reads"]["blocks"][0]["spans"] = spans
            registration = encode(trial)
            final = registration.replace(dispatch.REGISTRATION_PLACEHOLDER, json.dumps(H).encode())
            with self.subTest(spans=spans, status="registered"), self.assertRaisesRegex(
                dispatch.ManifestError, "qual-01.*span commitment"
            ):
                dispatch.validate_v2(registration)
            for trusted in (registration, authentic):
                with self.subTest(spans=spans, status="final"), self.assertRaisesRegex(
                    dispatch.ManifestError, "qual-01.*span commitment"
                ):
                    dispatch.validate_v2(final, final=True, registration=trusted)

    def test_rejects_invalid_final_candidate_before_registration_open(self):
        with tempfile.TemporaryDirectory() as tmp:
            candidate = Path(tmp) / "final.json"
            registration = Path(tmp) / "RESTRICTED" / "coefficients.json"
            read_bytes = Path.read_bytes

            def guard(path):
                if path == registration:
                    raise AssertionError("invalid final candidate reached registration open")
                return read_bytes(path)

            for source in (QUALIFICATION, DRAFT):
                original = json.loads(source.read_bytes())
                original["status"] = "registered"
                pending = encode(original)
                valid = pending.replace(dispatch.REGISTRATION_PLACEHOLDER, json.dumps(H).encode())
                substituted = json.loads(valid)
                kits = substituted["reads"]
                if source == QUALIFICATION:
                    kits["blocks"][0]["spans"] = ["f2-inst-01-l004", "f2-inst-01-l005"]
                else:
                    kits["kits"][0]["sha256"] = H
                for defect, payload in (
                    ("pending", pending),
                    ("open marker", encode(dict(json.loads(valid), title="OPEN-19"))),
                    ("unknown field", encode(dict(json.loads(valid), extra=True))),
                    ("substituted identity", encode(substituted)),
                ):
                    candidate.write_bytes(payload)
                    with self.subTest(source=source.name, defect=defect), patch.object(Path, "read_bytes", guard):
                        with redirect_stderr(StringIO()) as stderr:
                            status = dispatch._dispatch(["validate", str(candidate), "--final",
                                                    "--registration", str(registration)])
                        self.assertEqual(status, 2)
                        self.assertIn("REFUSE", stderr.getvalue())

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
            status = dispatch._dispatch(["validate", str(DRAFT)])
        self.assertEqual((status, stdout.getvalue(), stderr.getvalue()), (0, "ok lm-transfer-01 (draft)\n", ""))
        stdout, stderr = StringIO(), StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = dispatch._dispatch(["validate", "--final", str(DRAFT)])
        self.assertEqual((status, stdout.getvalue()), (2, ""))
        self.assertIn("draft cannot pass final validation", stderr.getvalue())


class DescriptionManifestTests(unittest.TestCase):
    def test_closed_description_is_separate_from_transfer(self):
        pin = {"path": "synthetic/file", "sha256": H}
        names = ["hold.json", "turn.json", "gain.json", "edges.json"]
        fixture = {
            "schema": dispatch.V2, "look_kind": "description", "status": "committed",
            "look_id": "lm-inst-01", "title": "Synthetic design", "rulings": ["RL-181 §2.1"],
            "kits": json.loads(INSTRUMENT.read_bytes())["kits"],
            "channels": ["gpu_rail", "rail_sum", "dc_in"], "when": "after effective freeze 2",
            "rail_sum_columns": RAIL_SUM_COLUMNS,
            "stage1": "Synthetic operational roster",
            "freeze2": {"look_id": "lm-interim-01", "hash_key": "freeze2_sha256", "authority": "RL-183 §2.3"},
            "prints": [{"description": name, "destination": name} for name in names],
            "code_pins": {
                **dict.fromkeys(("reader", "manifest_schema", "stage1_schema", "output_schema"), pin),
                "kit_commitments": {"path": str(dispatch.KIT_COMMITMENTS.relative_to(ROOT)), "sha256": H},
            },
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
