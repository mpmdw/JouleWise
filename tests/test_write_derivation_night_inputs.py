"""Defect-shaped regressions for the derivation-night desk input writer.

Every test names the defect it would catch.  The two files this script writes
are copied VERBATIM into every slot record the night reserves and their
digests are pinned into the night's wrapper, so a wrong byte here is a burned
night that cannot be discovered until the evidence is read.

No test reads this machine.  ``sysctl``, the sampler digest and the MLX
version are mocked in every test, because a test that reads the real machine
passes at the desk and fails on CI and on any clone - the exact defect class
that cost this lane two CI-only failures already.
"""

from __future__ import annotations

from unittest import mock

import contextlib

from contextlib import contextmanager, redirect_stderr, redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch

from joulewise.calibration_ledger import IDENTITY_EPOCH_FIELDS, T1_FIELDS
from scripts import gen_derivation_night as generator
from scripts import generate_g2a_probe_inputs as probe_inputs
from scripts import validate_powermetrics_fiducial as validation_script
from scripts import write_derivation_night_inputs as script
from tests.fixtures.epoch_bootstrap.build import TARGET_EPOCH
from tests.fixtures.epoch_continuation.build import registered_continuation

REPO_ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE_PATH = validation_script.DEFAULT_ACCEPTANCE_BOUND_PATH
ACCEPTANCE_EPOCH = json.loads(ACCEPTANCE_PATH.read_text(encoding="utf-8"))[
    "identity_epoch"
]
# A build that is not the acceptance's, so `os_build` is the stale field.
NEW_OS_BUILD = "99Z99"
SAMPLER_SHA256 = "b" * 64
MLX_VERSION = "0.99.0-test"


@contextmanager
def mocked_machine(
    *, os_build: str = NEW_OS_BUILD, mlx_version: object = MLX_VERSION
):
    """Stand in for every machine read the writer's helpers perform."""

    real_sha256_path = validation_script.sha256_path

    def sampler_aware_sha256(path: Path) -> str:
        # Only the sampler binary is synthesised; the frozen protocol is a
        # tracked file and must keep its real digest, or the acceptance
        # preflight would refuse for the wrong reason.
        if Path(path) == script.SAMPLER_BINARY:
            return SAMPLER_SHA256
        return real_sha256_path(path)

    mlx_package = ModuleType("mlx")
    mlx_core = ModuleType("mlx.core")
    if mlx_version is not None:
        mlx_core.__version__ = mlx_version
    mlx_package.core = mlx_core
    with (
        patch.dict(sys.modules, {"mlx": mlx_package, "mlx.core": mlx_core}),
        patch.object(
            validation_script,
            "_sysctl_identity",
            side_effect=lambda name: (
                os_build
                if name == "kern.osversion"
                else ACCEPTANCE_EPOCH["hardware_model"]
            ),
        ),
        patch.object(
            validation_script, "sha256_path", side_effect=sampler_aware_sha256
        ),
    ):
        yield


def run_main(argv: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = script.main(argv)
    return code, out.getvalue(), err.getvalue()


class WriteDerivationNightInputsTests(unittest.TestCase):
    def test_continued_epoch_is_an_ordinary_night_and_writes_no_derivation_inputs(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            out = root / "inputs"
            out.mkdir()
            with registered_continuation(root), mocked_machine(os_build=TARGET_EPOCH["os_build"]):
                code, stdout, stderr = run_main(["--out-dir", str(out)])
            self.assertEqual(code, 2, stderr)
            self.assertIn("ORDINARY night, not a derivation night", stderr)
            self.assertEqual(stdout, "")
            self.assertEqual(list(out.iterdir()), [])
        self.assertIn("A continued epoch", script.__doc__)

    def test_writes_exactly_the_six_scalar_identity_fields_and_the_t1_superset(
        self,
    ) -> None:
        """Defect: a file the generator's field check refuses at arm time."""

        with tempfile.TemporaryDirectory() as raw, mocked_machine():
            code, out, err = run_main(["--out-dir", raw])
            self.assertEqual(code, 0, err)
            epoch = json.loads((Path(raw) / "identity-epoch.json").read_text())
            t1 = json.loads((Path(raw) / "t1-bindings.json").read_text())
        self.assertEqual(set(epoch), set(IDENTITY_EPOCH_FIELDS))
        self.assertEqual(set(t1), set(T1_FIELDS))
        for field, value in epoch.items():
            self.assertIsInstance(value, (str, int), field)
            self.assertNotIsInstance(value, bool, field)
            self.assertNotIn(value, (None, ""), field)
        self.assertEqual(epoch["power_policy"], "ac_high_power")
        self.assertEqual(epoch["os_build"], NEW_OS_BUILD)
        self.assertEqual(t1["powermetrics_sha256"], SAMPLER_SHA256)
        self.assertEqual(t1["mlx_version"], MLX_VERSION)
        self.assertIn("stale identity fields", out)
        self.assertIn("os_build", out.splitlines()[0])

    def test_bytes_are_the_probe_generator_canonical_serialization(self) -> None:
        """Defect: a different JSON dialect than every other pinned input."""

        with tempfile.TemporaryDirectory() as raw, mocked_machine():
            code, _out, err = run_main(["--out-dir", raw])
            self.assertEqual(code, 0, err)
            identity_bytes = (Path(raw) / "identity-epoch.json").read_bytes()
            t1_bytes = (Path(raw) / "t1-bindings.json").read_bytes()
        self.assertEqual(
            identity_bytes, probe_inputs._json_bytes(json.loads(identity_bytes))
        )
        self.assertEqual(t1_bytes, probe_inputs._json_bytes(json.loads(t1_bytes)))
        self.assertTrue(identity_bytes.endswith(b"}\n"))

    def test_printed_sha256_lines_match_the_written_files(self) -> None:
        """Defect: arm materials pin a digest no file on disk has."""

        with tempfile.TemporaryDirectory() as raw, mocked_machine():
            code, out, err = run_main(["--out-dir", raw])
            self.assertEqual(code, 0, err)
            lines = out.strip().splitlines()
            self.assertEqual(len(lines), 3, out)
            for line, name, key in (
                (lines[1], "identity-epoch.json", "IDENTITY_EPOCH_JSON"),
                (lines[2], "t1-bindings.json", "T1_BINDINGS_JSON"),
            ):
                path_part, sha_part = line.split(" sha256=")
                self.assertEqual(path_part, f"{key}={Path(raw).absolute() / name}")
                self.assertEqual(
                    sha_part,
                    hashlib.sha256((Path(raw) / name).read_bytes()).hexdigest(),
                )

    def test_written_files_pass_the_wrapper_generator_validators(self) -> None:
        """Defect: inputs this script blesses that gen_derivation_night refuses."""

        with tempfile.TemporaryDirectory() as raw, mocked_machine():
            code, _out, err = run_main(["--out-dir", raw])
            self.assertEqual(code, 0, err)
            epoch = generator._validated_identity_epoch(
                Path(raw) / "identity-epoch.json"
            )
            t1 = generator._validated_json_object(
                Path(raw) / "t1-bindings.json", "t1 bindings json"
            )
        self.assertEqual(set(epoch), set(IDENTITY_EPOCH_FIELDS))
        self.assertEqual(epoch["power_policy"], generator.CHAIN_POWER_POLICY)
        self.assertEqual(set(t1), set(T1_FIELDS))

    def test_refuses_when_the_out_dir_does_not_exist(self) -> None:
        """Defect: inventing a custody location the night files evidence under."""

        with tempfile.TemporaryDirectory() as raw, mocked_machine():
            missing = Path(raw) / "no-such-night-root"
            code, _out, err = run_main(["--out-dir", str(missing)])
            self.assertEqual(code, 2)
            self.assertIn("is not an existing directory", err)
            self.assertFalse(missing.exists())

    def test_refuses_an_existing_file_without_force_and_rewrites_with_force(
        self,
    ) -> None:
        """Defect: silently replacing bytes a generated wrapper already pins."""

        with tempfile.TemporaryDirectory() as raw, mocked_machine():
            identity = Path(raw) / "identity-epoch.json"
            identity.write_bytes(b"{}\n")
            code, _out, err = run_main(["--out-dir", raw])
            self.assertEqual(code, 2)
            self.assertIn("refusing to overwrite", err)
            self.assertEqual(identity.read_bytes(), b"{}\n")
            # The pair is written or not written together: the refusal must not
            # have left the second file behind.
            self.assertFalse((Path(raw) / "t1-bindings.json").exists())
            code, _out, err = run_main(["--out-dir", raw, "--force"])
            self.assertEqual(code, 0, err)
            self.assertNotEqual(identity.read_bytes(), b"{}\n")

    def test_refuses_when_no_identity_field_differs_from_the_acceptance(self) -> None:
        """Defect: handing an ORDINARY night derivation-only inputs.

        The machine is mocked to the acceptance's own epoch, which is what an
        acceptance whose epoch equals this machine looks like to the preflight.
        """

        with (
            tempfile.TemporaryDirectory() as raw,
            mocked_machine(os_build=ACCEPTANCE_EPOCH["os_build"]),
        ):
            code, _out, err = run_main(["--out-dir", raw])
            self.assertEqual(code, 2)
            self.assertIn("already judges", err)
            self.assertIn("ORDINARY night", err)
            self.assertEqual(sorted(Path(raw).iterdir()), [])

    def test_refuses_an_empty_power_policy(self) -> None:
        """Defect: an epoch field the ledger treats as absent."""

        with tempfile.TemporaryDirectory() as raw, mocked_machine():
            code, _out, err = run_main(["--out-dir", raw, "--power-policy", "  "])
            self.assertEqual(code, 2)
            self.assertIn("--power-policy is empty", err)
            self.assertEqual(sorted(Path(raw).iterdir()), [])

    def test_refuses_when_the_mlx_version_is_absent(self) -> None:
        """Defect: an empty T1 binding the night's reserve step would refuse."""

        with (
            tempfile.TemporaryDirectory() as raw,
            mocked_machine(mlx_version=None),
        ):
            code, _out, err = run_main(["--out-dir", raw])
            self.assertEqual(code, 2)
            self.assertIn("t1 bindings fields are empty", err)
            self.assertEqual(sorted(Path(raw).iterdir()), [])

    def test_never_reads_or_writes_the_calibration_ledger(self) -> None:
        """Defect: a desk script that opens the ledger a night is custodian of."""

        source = Path(script.__file__).read_text(encoding="utf-8")
        for forbidden in (
            "load_calibration_ledger_snapshot",
            "read_replay",
            "DEFAULT_LEDGER_PATH",
            "DEFAULT_HEAD_PIN_PATH",
            "_authenticate_ledger_and_acceptance",
        ):
            self.assertNotIn(forbidden, source, forbidden)

    def test_help_glosses_every_term_of_art_at_first_use(self) -> None:
        """Defect: a --help that assumes the vocabulary it has to teach."""

        out = io.StringIO()
        with redirect_stdout(out):
            script._build_parser().print_help()
        text = out.getvalue()
        for gloss in (
            "derivation night",
            "identity epoch",
            "T1 bindings",
            "stale field",
            "IDENTITY_EPOCH_JSON=",
            "T1_BINDINGS_JSON=",
        ):
            self.assertIn(gloss, text, gloss)
        # Each term is explained where it is introduced, not left to the reader.
        self.assertIn("six fields", text)
        self.assertIn("differs", text)

    def test_module_imports_the_writers_own_helpers_rather_than_copying_them(
        self,
    ) -> None:
        """Defect: a second implementation of the epoch that can drift.

        Patching the writer's module attributes changes what this script
        derives; if it had copied the derivation, the patch would not reach it.
        """

        source = Path(script.__file__).read_text(encoding="utf-8")
        self.assertIn("from scripts.validate_powermetrics_fiducial import", source)
        for helper in (
            "_planned_t1_bindings",
            "_sysctl_identity",
            "SAMPLING_INTERVAL_MS",
            "RESIDUAL_REGION_METHOD",
            "PROTOCOL_ID",
        ):
            self.assertIn(helper, source, helper)
        with tempfile.TemporaryDirectory() as raw, mocked_machine(os_build="12A34"):
            code, _out, err = run_main(["--out-dir", raw])
            self.assertEqual(code, 0, err)
            epoch = json.loads((Path(raw) / "identity-epoch.json").read_text())
        self.assertEqual(epoch["os_build"], "12A34")
        self.assertEqual(
            epoch["sampling_interval_ms"], validation_script.SAMPLING_INTERVAL_MS
        )
        self.assertEqual(
            epoch["estimator_revision"], validation_script.RESIDUAL_REGION_METHOD
        )
        self.assertEqual(epoch["pulse_protocol_id"], validation_script.PROTOCOL_ID)

    def test_script_module_is_importable_by_path_as_the_night_desk_runs_it(
        self,
    ) -> None:
        """Defect: a script that only works when imported as a package member."""

        spec = importlib.util.spec_from_file_location(
            "write_derivation_night_inputs_by_path",
            REPO_ROOT / "scripts" / "write_derivation_night_inputs.py",
        )
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(callable(module.main))


if __name__ == "__main__":
    unittest.main()


class OneHomeAndAcceptanceBranchTests(unittest.TestCase):
    """REFUSE-FREE: production call sites write_derivation_night_inputs.SAMPLER_BINARY and _stale_identity_fields (unreadable acceptance)."""

    def test_the_sampler_path_is_the_writers_own(self) -> None:
        from scripts import validate_powermetrics_fiducial as writer
        from scripts import write_derivation_night_inputs as script

        self.assertEqual(script.SAMPLER_BINARY, Path(writer.POWER_METRICS))
        source = Path(script.__file__).read_text(encoding="utf-8")
        self.assertNotIn('Path("/usr/bin/powermetrics")', source)

    def test_an_unreadable_acceptance_refuses_by_name_and_writes_nothing(self) -> None:
        from scripts import write_derivation_night_inputs as script

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bad = root / "acceptance.json"
            bad.write_text("{not json", encoding="utf-8")
            planned = {
                "os_build": "25G83", "hardware_model": "Mac15,9", "power_policy": "ac_high_power",
                "sampling_interval_ms": 100, "estimator_revision": "r", "pulse_protocol_id": "p",
            }
            t1 = dict(planned, powermetrics_sha256="0" * 64, clock_anchor_method="v3",
                      mlx_version="0.0.0", protocol_sha256="1" * 64)
            with mock.patch.object(script, "_derive_planned_vectors", return_value=(planned, t1)):
                stream = io.StringIO()
                with contextlib.redirect_stderr(stream):
                    rc = script.main(["--out-dir", str(root), "--acceptance", str(bad)])
            self.assertEqual(rc, 2)
            self.assertIn("could not be read as an issued artifact", stream.getvalue())
            self.assertFalse((root / "identity-epoch.json").exists())
            self.assertFalse((root / "t1-bindings.json").exists())
