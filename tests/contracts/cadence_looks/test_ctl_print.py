"""Run the unchanged freeze against the controls builder under test discovery."""

from contextlib import ExitStack
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from importlib import import_module
from importlib.util import find_spec, spec_from_file_location
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import controls_print as controls
from joulewise.cadence_looks import controls_analysis as analysis, controls_manifest as manifest
from joulewise.cadence_looks import controls_release as release

from . import synthetic_acceptance as vectors
from .ctl_print_adapter import check_fixture
from .frozen_v3.test_ctl01_hand_vectors import frozen_kernel


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


SHARED_MODULES = "5a8ac8ff6753caf76cac01bfc4d15d6f0385afc5"


def worker_fixture(directory, mode, synthetic_path=False):
    """Drive the real worker in a child with invented commitments and records."""
    import joulewise.cadence_looks as looks

    with ExitStack() as scope:
        scope.enter_context(patch.object(tempfile, "tempdir", str(directory)))
        scope.enter_context(frozen_kernel())
        if find_spec("joulewise.cadence_looks.transfer_release") is None:
            source = directory / "shared-source"
            source.mkdir(exist_ok=True)
            for name in ("manifest_dispatch.py", "transfer_release.py"):
                git_path = f"{SHARED_MODULES}:joulewise/cadence_looks/{name}"
                (source / name).write_bytes(subprocess.check_output(["git", "show", git_path], cwd=ROOT))
            looks.__path__.append(str(source))
        v2 = import_module("tests.contracts.cadence_looks.frozen_v3.test_ctl01_print_v2")
        from . import ctl_v2_adapter as adapter

        _run_worker_fixture(directory, mode, synthetic_path, v2, adapter, scope)


def _run_worker_fixture(directory, mode, synthetic_path, v2, adapter, scope):
    private = directory / "private" / controls.LOOK_ID
    restricted = private / ("synthetic-output" if synthetic_path else "RESTRICTED")
    public = directory / "public" / controls.LOOK_ID / release.PUBLIC_NAME
    if synthetic_path:
        # The local host denies even an invented RESTRICTED directory.
        scope.enter_context(patch.object(release, "reserve_outputs", release.reserve_directory))

    positions = v2.complete()
    roster = {"n_legs": len(positions), "legs": vectors.example()[0]["legs"]}
    for leg in positions:
        roster["legs"][leg.leg_id]["script_sha"] = leg.work_sha256
    committed_stage1 = manifest.canonical(roster)
    selected = deepcopy(roster)
    if mode in ("stale_bytes_only", "prior_kit_self_digest"):
        for row in selected["legs"].values():
            row["identity"][1] = sha256(b"prior synthetic kit revision").hexdigest()
    if mode in ("diagnostic_3w", "diagnostic_4w"):
        selected["synthetic_mean_w"] = int(mode[-2])
    if mode == "committed_nested_extra":
        selected["legs"]["L002"]["synthetic_mean_w"] = 4

    stage1_bytes = manifest.canonical(selected)
    if mode == "committed_nested_extra":
        committed_stage1 = stage1_bytes

    artifacts = dict(adapter.freeze_artifacts())
    pins = {name: sha256(raw).hexdigest() for name, raw in artifacts.items()}
    artifacts["manifest"] = adapter.make_manifest(controls.LOOK_ID, "controls", pins)
    digest = sha256(artifacts["manifest"]).hexdigest()
    stage1_sha = sha256(committed_stage1).hexdigest()
    revision = "b" * 40
    stage1_revision = "c" * 40
    history = [dict(kind="design_pass", look_id=controls.LOOK_ID),
               dict(kind="byte_pass", look_id=controls.LOOK_ID, manifest_sha256=digest, hand_vectors_passed=True),
               dict(kind="receipt", look_id=controls.LOOK_ID, manifest_sha256=digest, revision=revision)]
    if mode != "unregistered_stage1":
        history.append(dict(kind="stage1", look_id=controls.LOOK_ID, manifest_sha256=digest,
                            revision=stage1_revision, stage1_sha256=stage1_sha, n_legs=len(positions)))
    if mode == "withheld":
        history.append({"kind": "ctl01_withheld", "reason": "no_dc_in_floor"})

    class SyntheticFailure(Exception):
        pass

    def first_read(bindings):
        (directory / "first-read").touch(exist_ok=False)
        for (binding, script_sha), leg in zip(bindings, positions, strict=True):
            assert binding.leg_id == leg.leg_id and script_sha == leg.work_sha256
        print("invented reader output", flush=True)
        subprocess.run([sys.executable, "-B", "-c", "import os; os.write(2, b'invented child output\\n')"], check=True)
        if mode == "builtin":
            raise ValueError("invented diagnostic")
        if mode == "custom":
            raise SyntheticFailure("invented diagnostic")
        return positions

    pool = analysis.pool_hold_windows([], set(), reason_enum={"synthetic_floor_unavailable"})
    pool.update(adapter._positive_pool())
    args = dict(
        freeze_inputs=dict(current_revision=revision, committed={revision: artifacts,
                           stage1_revision: {"stage1": committed_stage1}}, working=artifacts, history=history),
        stage1_bytes=stage1_bytes,
        blind=dict(look_id=controls.LOOK_ID,
                   manifest_sha256=sha256(b"wrong manifest").hexdigest() if mode == "wrong_manifest" else digest,
                   commit=stage1_revision, n_legs=len(positions),
                   stage1_sha256=stage1_sha if mode == "stale_bytes_only" else sha256(stage1_bytes).hexdigest()),
        execution_host="invented-host", local_host="wrong-host" if mode == "host" else "invented-host",
        restricted=restricted, public=public, first_read=first_read, pooled=pool,
        gap_limits_ns=dict.fromkeys(analysis.CHANNELS, 2 * v2.NS),
    )
    if mode == "other_integrator":
        def constant_level(trace, start, end, *, mapping):
            return v2.EnergyEstimate(trace.values[0] * ((end - start) / v2.NS), 0, "constant", ())

        alternate = replace(v2.KERNEL, trace_energy=constant_level)
        hidden = v2.pri(positions, kernel=alternate)["legs"][1]["channels"]["gpu_rail"]["hidden"]
        assert hidden["call_j"] == 0.0
        try:
            release.run_controls_worker(**args, kernel=alternate)
        except TypeError as error:
            if "unexpected keyword argument 'kernel'" not in str(error):
                raise
            return
        raise AssertionError("worker accepted a caller-selected integrator")
    if mode == "foreign_integrator_source":
        foreign = directory / "other_integrator.py"
        foreign.write_bytes(b"def _integrate(*args, **kwargs): return 0\n")
        scope.enter_context(patch.object(release, "find_spec", side_effect=lambda name:
            spec_from_file_location(name, foreign) if name == "joulewise.reduce" else find_spec(name)))
    release.run_controls_worker(**args)


class TestControlsRelease(unittest.TestCase):
    def test_v3_and_v31_have_independent_verified_inventories(self):
        path = Path(__file__).resolve().parent
        inventories = (
            ("frozen_v3", "SUITE-v3.sha256",
             "71e9f515023092b5313c9fa1facc5c7d9b2a7977b0dbaf860cee121dbdd48c74"),
            ("frozen_v3_1", "SUITE-v3.1.sha256",
             "98ee283dd85b5da44dca7f730cef8e4bbfb4fdcdb5bf688a2420e791548a31c2"),
        )
        for folder, inventory, inventory_digest in inventories:
            root = path / folder
            raw = (root / inventory).read_bytes()
            self.assertEqual(sha256(raw).hexdigest(), inventory_digest)
            for line in raw.decode("ascii").splitlines():
                digest, name = line.split("  ", 1)
                with self.subTest(freeze=folder, artifact=name):
                    self.assertEqual(sha256((root / name).read_bytes()).hexdigest(), digest)
        relative = "test_ctl01_print_v2.py"
        historical = (path / "frozen_v3" / relative).read_bytes()
        active = (path / "frozen_v3_1" / relative).read_bytes()
        old = b'(None, "incomplete_recovery"))'
        self.assertEqual(historical.count(old), 1)
        self.assertEqual(active, historical.replace(old, b'(None, "recovery_incomplete"))', 1))

    def run_worker(self, directory, mode, *, synthetic_path=False):
        for destination in ("private", "public"):
            (directory / destination / controls.LOOK_ID).mkdir(parents=True, exist_ok=True)
        launcher = ("import sys; from pathlib import Path; "
                    "from tests.contracts.cadence_looks.test_ctl_print import worker_fixture; "
                    "worker_fixture(Path(sys.argv[1]), sys.argv[2], sys.argv[3] == '1')")
        command = [sys.executable, "-B", "-c", launcher, str(directory), mode, str(int(synthetic_path))]
        return subprocess.run(command, cwd=ROOT, capture_output=True)

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
                result = self.run_worker(base, mode)
                self.assertEqual((result.returncode, result.stdout, result.stderr), (status, b"", stderr))
                self.assertIs(public.exists(), status == 0)
                self.assertIs(restricted.exists(), status < 2)
                if status < 2:
                    self.assertIn(b"invented reader output", (restricted / "stdout").read_bytes())
                    self.assertIn(b"invented child output", (restricted / "stderr").read_bytes())
                    original = public.read_bytes() if status == 0 else None
                    self.assertEqual({file.name for file in restricted.iterdir()},
                                     release.PRIVATE_NAMES if status == 0 else {"stdout", "stderr"})
                    retry = self.run_worker(base, mode)
                    self.assertEqual((retry.returncode, retry.stdout, retry.stderr),
                                     (2, b"", b"REFUSE controls look before read\n"))
                    if original is not None:
                        self.assertEqual(public.read_bytes(), original)
                        self.assertEqual(set(json.loads(original)),
                                         {"look_id", "manifest_sha256", "commit", "stage1_sha256", "n_legs"})

    def test_worker_refuses_uncommitted_or_nonblind_stage1_before_reservation(self):
        for mode in ("wrong_manifest", "stale_bytes_only", "prior_kit_self_digest",
                     "diagnostic_3w", "diagnostic_4w", "committed_nested_extra", "unregistered_stage1"):
            with self.subTest(mode=mode), TemporaryDirectory(dir=ROOT) as directory:
                base = Path(directory)
                result = self.run_worker(base, mode, synthetic_path=True)
                self.assertEqual((result.returncode, result.stdout, result.stderr),
                                 (2, b"", b"REFUSE controls look before read\n"))
                self.assertFalse((base / "first-read").exists())
                self.assertFalse((base / "private" / controls.LOOK_ID / "synthetic-output").exists())
                self.assertFalse((base / "public" / controls.LOOK_ID / release.PUBLIC_NAME).exists())

    def test_worker_uses_exact_pinned_integrator_and_committed_stage1(self):
        with TemporaryDirectory(dir=ROOT) as directory:
            base = Path(directory)
            result = self.run_worker(base, "ok", synthetic_path=True)
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
            self.assertTrue((base / "first-read").exists())
            restricted = base / "private" / controls.LOOK_ID / "synthetic-output"
            public = base / "public" / controls.LOOK_ID / release.PUBLIC_NAME
            report = json.loads((restricted / "controls.json").read_bytes())
            hidden = report["legs"][1]["channels"]["gpu_rail"]["hidden"]
            self.assertEqual(hidden["call_j"], 14.0)
            self.assertEqual(json.loads(public.read_bytes())["commit"], "c" * 40)
        for mode, expected in (
            ("other_integrator", (0, b"", b"")),
            ("foreign_integrator_source", (2, b"", b"REFUSE controls look before read\n")),
        ):
            with self.subTest(mode=mode), TemporaryDirectory(dir=ROOT) as directory:
                base = Path(directory)
                result = self.run_worker(base, mode, synthetic_path=True)
                self.assertEqual((result.returncode, result.stdout, result.stderr), expected)
                self.assertFalse((base / "first-read").exists())
                self.assertFalse((base / "private" / controls.LOOK_ID / "synthetic-output").exists())
                self.assertFalse((base / "public" / controls.LOOK_ID / release.PUBLIC_NAME).exists())
