"""Continued-epoch writer preflight and the G2-a caller; synthetic inputs only."""

from contextlib import redirect_stderr
from decimal import Decimal
import io
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from joulewise import calibration_bracketing as bracket
from joulewise.calibration_exits import RefusalCode
from scripts import generate_g2a_probe_inputs as probe
from scripts import validate_powermetrics_fiducial as writer
from tests.fixtures.epoch_bootstrap.build import TARGET_EPOCH
from tests.fixtures.epoch_continuation.build import registered_continuation


class ContinuedEpochPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.artifact = bracket.load_calibration_acceptance_bound()

    def test_ordinary_preflight_accepts_continuation_with_unchanged_screen(self):
        with registered_continuation(self.root):
            record = {}
            screen = writer._derive_preflight_systematic_screen_s(
                TARGET_EPOCH, preflight_record=record,
            )
            self.assertEqual(screen, Decimal(self.artifact["decimal_derivation"][
                "ratified_operatives"]["preflight_level_screen_s"]))
            self.assertIn("judged_epochs", record)
            self.assertEqual(record["judged_epochs"], [self.artifact["identity_epoch"], TARGET_EPOCH])
            self.assertEqual(record["judged_epochs_basis"], "registry_pins_only")
            self.assertEqual(record["continuation_refusals"], [])

    def test_unregistered_or_rotated_continuation_refuses_with_epoch_reason(self):
        with registered_continuation(self.root) as (_, path):
            for cut in ("registry", "bytes"):
                with self.subTest(cut=cut):
                    if cut == "bytes":
                        path.write_bytes(path.read_bytes() + b" ")
                    registry = {} if cut == "registry" else dict(bracket.EPOCH_CONTINUATION_REGISTRY)
                    with patch.dict(bracket.EPOCH_CONTINUATION_REGISTRY, registry, clear=True):
                        with self.assertRaises(writer._AcceptancePreflightError) as raised:
                            writer._derive_preflight_systematic_screen_s(TARGET_EPOCH)
                    self.assertEqual(raised.exception.reason, "acceptance_artifact_epoch_mismatch")
                    self.assertEqual(raised.exception.context["stale_fields"], ["os_build"])
                    if cut == "bytes":
                        self.assertEqual(raised.exception.context["continuation_refusals"][0]["reason"],
                                         "calibration_epoch_continuation_invalid")

    def test_continued_epoch_must_match_every_identity_field(self):
        with registered_continuation(self.root):
            for field in TARGET_EPOCH:
                epoch = dict(TARGET_EPOCH)
                epoch[field] = 101 if field == "sampling_interval_ms" else "different"
                with self.subTest(field=field), self.assertRaises(writer._AcceptancePreflightError):
                    writer._derive_preflight_systematic_screen_s(epoch)

    def test_derivation_basis_lists_original_and_continued_judged_epochs(self):
        with registered_continuation(self.root):
            _, basis = writer._derivation_only_screen_basis()
            self.assertEqual(basis["epoch"], self.artifact["identity_epoch"])
            self.assertEqual(basis["judged_epochs"], [self.artifact["identity_epoch"], TARGET_EPOCH])
            self.assertEqual(basis["judged_epochs_basis"], "registry_pins_only")

    def test_derivation_only_refuses_continued_epoch_before_capture(self):
        identity = self.root / "identity.json"
        identity.write_text(json.dumps(TARGET_EPOCH))
        with registered_continuation(self.root), redirect_stderr(io.StringIO()) as error:
            rc = writer.main([
                "--allow-live", "--derivation-only", "--power-policy", TARGET_EPOCH["power_policy"],
                "--identity-epoch-json-for-test", str(identity),
                "--output-root", str(self.root / "captures"),
            ])
        self.assertEqual(rc, 2, error.getvalue())
        refusal = json.loads(error.getvalue())
        self.assertEqual(refusal["code"], RefusalCode.DERIVATION_ONLY_EPOCH_UNCHANGED.value)
        self.assertFalse((self.root / "captures").exists())

    def test_g2a_live_vectors_use_real_continuation_preflight(self):
        # Stub machine observations and MLX only; keep the generator, writer
        # preflight, acceptance loader and continuation authentication real.
        identities = {"kern.osversion": TARGET_EPOCH["os_build"], "hw.model": TARGET_EPOCH["hardware_model"]}
        with (
            registered_continuation(self.root),
            patch.object(writer, "_sysctl_identity", side_effect=identities.__getitem__),
            patch.object(writer, "sha256_path", return_value="a" * 64),
            patch.dict("sys.modules", {"mlx.core": types.SimpleNamespace(__version__="test-mlx")}),
        ):
            epoch, t1, acceptance = probe._derive_live_vectors(TARGET_EPOCH["power_policy"])
            self.assertEqual(epoch, TARGET_EPOCH)
            self.assertEqual({field: t1[field] for field in TARGET_EPOCH}, TARGET_EPOCH)
            self.assertEqual(acceptance, self.artifact)
            with patch.dict(bracket.EPOCH_CONTINUATION_REGISTRY, {}, clear=True):
                with self.assertRaisesRegex(probe.G2AProbeError, "acceptance_artifact_epoch_mismatch"):
                    probe._derive_live_vectors(TARGET_EPOCH["power_policy"])


if __name__ == "__main__":
    unittest.main()
