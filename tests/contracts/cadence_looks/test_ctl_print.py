"""Run the unchanged freeze against the controls builder under test discovery."""

from copy import deepcopy
from hashlib import sha256
from importlib.util import find_spec
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import controls_print as controls
from joulewise.cadence_looks import controls_analysis as analysis, controls_manifest as manifest
from joulewise.cadence_looks import controls_release as release

from . import synthetic_acceptance as vectors
from .ctl_print_adapter import check_fixture


class TestFrozenControlsPrint(vectors.Contract):
    def setUp(self):
        super().setUp()
        validator = patch.object(vectors, "VALIDATE", check_fixture)
        validator.start()
        self.addCleanup(validator.stop)


class TestControlsPrintProjection(unittest.TestCase):
    def test_pair_depth_from_fresh_calls(self):
        def episode(kind, counts):
            return controls.Episode(kind, (), controls.Delivery(counts, 0, 0, 0, 120),
                                    (2000,) * len(counts), 106, "a" * 64)

        self.assertEqual(controls.compare_pair(episode("split", (342, 341, 341)),
                                               episode("plain", (1024,))), (2342, 3024))

    def test_zero_pin_refuses_even_if_committed(self):
        committed, candidate = vectors.example()
        committed["plan"]["code_sha"] = candidate["plan"]["code_sha"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "binding"):
            check_fixture(committed, candidate)

    def test_public_projection_is_unchanged_by_private_values(self):
        committed, candidate = vectors.example()
        public = committed["public"]
        expected = (b'{"commit":"' + b"b" * 40 + b'","look_id":"lm-ctl-01","manifest_sha256":"'
                    + public["manifest_sha256"].encode() + b'","n_legs":12,"stage1_sha256":"'
                    + public["stage1_sha256"].encode() + b'"}')
        self.assertEqual(controls.encode_public_projection(candidate["public"], public), expected)

        variant = deepcopy(candidate)
        variant["private"]["phases"]["dc_in"][-1] = 98
        variant["private"]["qualifier"] = "no"
        check_fixture(committed, variant)
        self.assertEqual(controls.encode_public_projection(variant["public"], public), expected)

    def test_public_projection_refuses_a_word_even_if_committed(self):
        committed, candidate = vectors.example()
        committed["public"]["qualifier"] = candidate["public"]["qualifier"] = "yes"
        with self.assertRaisesRegex(ValueError, "public disclosure"):
            check_fixture(committed, candidate)


ROOT = Path(__file__).resolve().parents[3]


def worker_fixture(directory, mode):
    """Drive the dedicated worker in a child with only invented inputs."""
    restricted = directory / "private" / controls.LOOK_ID / "RESTRICTED"
    public = directory / "public" / controls.LOOK_ID / release.PUBLIC_NAME
    stage1_bytes = manifest.canonical({"n_legs": 0})
    floor_reason = "synthetic_floor_unavailable"
    floor_schema = manifest.canonical({"$defs": {"undefined": {"properties": {
        "reason": {"enum": [floor_reason]},
    }}}})
    artifacts = dict.fromkeys(manifest.ROLES, b"synthetic code bytes")
    for role in ("output_schema", "restricted_schema", "controls_route"):
        artifacts[role] = (ROOT / manifest.CODE_PATHS[role]).read_bytes()
    artifacts.update(instrument_floor_schema=floor_schema, instrument_manifest=manifest.canonical({
        "schema": "joulewise.cadence_look_manifest.v2", "look_kind": "description",
        "look_id": "lm-inst-01", "status": "committed",
        "code_pins": {"restricted_schema": {"path": manifest.LOOK_DIR + "lm-inst-01.restricted.schema.json",
                                            "sha256": sha256(floor_schema).hexdigest()}},
    }))
    pins = {name: sha256(raw).hexdigest() for name, raw in artifacts.items()}
    artifacts["manifest"] = manifest.canonical(dict(schema=manifest.SCHEMA_ID, status="final",
        look_id=controls.LOOK_ID, look_kind="controls", kit_id=controls.KIT_ID, pins=pins))
    digest = sha256(artifacts["manifest"]).hexdigest()
    revision = "b" * 40
    history = [dict(kind="design_pass", look_id=controls.LOOK_ID),
               dict(kind="byte_pass", look_id=controls.LOOK_ID, manifest_sha256=digest, hand_vectors_passed=True),
               dict(kind="receipt", look_id=controls.LOOK_ID, manifest_sha256=digest, revision=revision)]
    if mode == "withheld":
        history.append({"kind": "ctl01_withheld", "reason": "no_dc_in_floor"})

    class SyntheticFailure(Exception):
        pass

    def first_read():
        print("invented reader output", flush=True)
        subprocess.run([sys.executable, "-B", "-c", "import os; os.write(2, b'invented child output\\n')"], check=True)
        if mode == "builtin":
            raise ValueError("invented diagnostic")
        if mode == "custom":
            raise SyntheticFailure("invented diagnostic")
        return [analysis.LegInput(leg, "plain", False, False) for leg in controls.PILOT + controls.REMAINDER]

    release.run_controls_worker(
        freeze_inputs=dict(current_revision=revision, committed={revision: artifacts}, working=artifacts,
                           history=history), stage1_bytes=stage1_bytes,
        blind=dict(look_id=controls.LOOK_ID, manifest_sha256=digest, commit=revision,
                   stage1_sha256=sha256(stage1_bytes).hexdigest(), n_legs=0),
        execution_host="invented-host", local_host="wrong-host" if mode == "host" else "invented-host",
        restricted=restricted, public=public, first_read=first_read,
        kernel=SimpleNamespace(phases=SimpleNamespace(TIMING_EDGE_J=1,
                                                      qualify_ctl01=lambda _: {"qualified": "not_run"})),
        pooled=analysis.pool_hold_windows([], set(), reason_enum={floor_reason}), gap_limits_ns={},
    )


class TestControlsRelease(unittest.TestCase):
    def test_withheld_precedence_and_closed_rows(self):
        for dc, sizes, reason in (([], [], "no_dc_in_floor"), ([800], [], "no_prefill_size"),
                                  ([800], [2000], "dose_under_floor_at_k2")):
            recorded = []
            self.assertFalse(manifest.select_reservation(observations=dict(gpu_token_floors=[900],
                dc_token_floors=dc, qualified_prefills=sizes), append=recorded.append))
            self.assertEqual(recorded, [{"kind": "ctl01_withheld", "reason": reason}])
            with self.assertRaisesRegex(ValueError, "ctl01_withheld"):
                manifest.append_withheld({**recorded[0], "value": None}, self.fail)

    def test_worker_publishes_once_and_confines_failure_diagnostics(self):
        if find_spec("joulewise.cadence_looks.transfer_release") is None:
            self.skipTest("shared instrument failure vocabulary awaits the combined checkout")
        launcher = ("import sys; from pathlib import Path; "
                    "from tests.contracts.cadence_looks.test_ctl_print import worker_fixture; "
                    "worker_fixture(Path(sys.argv[1]), sys.argv[2])")
        for mode, status, stderr in (
            ("ok", 0, b""), ("builtin", 1, b"stage2_error\nValueError\n"),
            ("custom", 1, b"stage2_error\nOtherError\n"),
            ("withheld", 2, b"REFUSE controls look before read\n"),
            ("host", 2, b"REFUSE controls look before read\n"),
        ):
            with self.subTest(mode=mode), TemporaryDirectory(dir=ROOT) as directory:
                base = Path(directory)
                restricted = base / "private" / controls.LOOK_ID / "RESTRICTED"
                public = base / "public" / controls.LOOK_ID / release.PUBLIC_NAME
                for parent in (restricted.parent, public.parent):
                    parent.mkdir(parents=True)
                command = [sys.executable, "-B", "-c", launcher, directory, mode]
                result = subprocess.run(command, cwd=ROOT, capture_output=True)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (status, b"", stderr))
                self.assertIs(public.exists(), status == 0)
                self.assertIs(restricted.exists(), status < 2)
                if status < 2:
                    self.assertIn(b"invented reader output", (restricted / "stdout").read_bytes())
                    self.assertIn(b"invented child output", (restricted / "stderr").read_bytes())
                    original = public.read_bytes() if status == 0 else None
                    self.assertEqual({file.name for file in restricted.iterdir()},
                                     release.PRIVATE_NAMES if status == 0 else {"stdout", "stderr"})
                    retry = subprocess.run(command, cwd=ROOT, capture_output=True)
                    self.assertEqual((retry.returncode, retry.stdout, retry.stderr),
                                     (2, b"", b"REFUSE controls look before read\n"))
                    if original is not None:
                        self.assertEqual(public.read_bytes(), original)
                        self.assertEqual(set(json.loads(original)),
                                         {"look_id", "manifest_sha256", "commit", "stage1_sha256", "n_legs"})
