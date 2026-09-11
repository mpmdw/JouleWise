"""Continued-epoch writer preflight and the G2-a caller; synthetic inputs only."""

from contextlib import redirect_stderr
from dataclasses import replace
from decimal import Decimal
import io
import json
from pathlib import Path
import re
import tempfile
import types
import unittest
from unittest.mock import patch

from joulewise import calibration_bracketing as bracket
from joulewise.calibration_exits import RefusalCode
from joulewise.calibration_ledger import load_calibration_ledger_snapshot
from scripts import generate_g2a_probe_inputs as probe
from scripts import validate_powermetrics_fiducial as writer
from tests.fixtures.epoch_bootstrap.build import TARGET_EPOCH, SESSION_ID
from tests.fixtures.epoch_continuation.build import registered_continuation


def documented_keys(name):
    contract = (writer.REPO_ROOT / "docs/contracts/powermetrics_fiducial.md").read_text()
    match = re.search(
        rf"`{name}` has exactly these keys:\n\n```json\n(.*?)\n```", contract, re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"missing documented {name} key list")
    keys = json.loads(match.group(1))
    if len(keys) != len(set(keys)):
        raise AssertionError(f"duplicate documented {name} key")
    return set(keys)


class ContinuedEpochPreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.artifact = bracket.load_calibration_acceptance_bound()

    def _continuation_snapshot(self):
        root = self.root / "night"
        snapshot = load_calibration_ledger_snapshot(
            root / "runs/calibration_observation_ledger.jsonl",
            root / "runs/calibration_ledger_head_pin.json",
            repo_root=root, require_committed_pin=True,
            verify_custody=False, mode="read_replay",
        )
        self.assertEqual(snapshot.refusal_reasons, ())
        return snapshot

    def test_contract_documented_key_lists_equal_emitted_preflight_and_screen_basis(self):
        with registered_continuation(self.root):
            record = {}
            writer._derive_preflight_systematic_screen_s(TARGET_EPOCH, preflight_record=record)
            _, basis = writer._derivation_only_screen_basis()
        self.assertEqual(documented_keys("acceptance_preflight"), set(record))
        self.assertEqual(documented_keys("screen_basis"), set(basis))

    def test_snapshot_preflight_authenticates_terminal_session_and_records_basis(self):
        with registered_continuation(self.root):
            snapshot = self._continuation_snapshot()
            record = {}
            screen = writer._derive_preflight_systematic_screen_s(
                TARGET_EPOCH, ledger_snapshot=snapshot, preflight_record=record,
            )
        self.assertEqual(screen, Decimal(self.artifact["decimal_derivation"][
            "ratified_operatives"]["preflight_level_screen_s"]))
        self.assertEqual(record["judged_epochs"], [self.artifact["identity_epoch"], TARGET_EPOCH])
        self.assertEqual(record["judged_epochs_basis"], "ledger_snapshot")
        self.assertEqual(record["continuation_refusals"], [])

    def test_snapshot_preflight_refuses_absent_or_nonterminal_continuation_session(self):
        with registered_continuation(self.root):
            snapshot = self._continuation_snapshot()
            session = snapshot.bracket_session_by_id[SESSION_ID]
            for sessions, detail in (
                ((), "session_absent"),
                ((replace(session, state="open"),), "session_not_terminal_or_state_mismatch"),
            ):
                with self.subTest(detail=detail):
                    with self.assertRaises(writer._AcceptancePreflightError) as raised:
                        writer._derive_preflight_systematic_screen_s(
                            TARGET_EPOCH, ledger_snapshot=replace(snapshot, bracket_sessions=sessions),
                        )
                    self.assertEqual(raised.exception.reason, "acceptance_artifact_epoch_mismatch")
                    self.assertEqual(raised.exception.context["judged_epochs_basis"], "ledger_snapshot")
                    self.assertEqual(raised.exception.context["continuation_refusals"][0]["detail"], detail)

    def test_derivation_basis_forwards_snapshot_and_refuses_unbacked_continuation(self):
        with registered_continuation(self.root):
            snapshot = replace(self._continuation_snapshot(), bracket_sessions=())
            _, basis = writer._derivation_only_screen_basis(ledger_snapshot=snapshot)
        self.assertEqual(basis["judged_epochs_basis"], "ledger_snapshot")
        self.assertEqual(basis["judged_epochs"], [self.artifact["identity_epoch"]])
        self.assertEqual(basis["continuation_refusals"][0]["detail"], "session_absent")

    def test_invalid_acceptance_id_returns_named_cli_refusal_without_traceback(self):
        for value in (None, "", 7, True):
            artifact = dict(self.artifact)
            if value is None:
                del artifact["acceptance_id"]
            else:
                artifact["acceptance_id"] = value
            with (
                self.subTest(acceptance_id=value),
                patch.object(writer, "load_calibration_acceptance_bound", return_value=artifact),
                patch.object(writer, "_sysctl_identity", return_value="test"),
                redirect_stderr(io.StringIO()) as error,
            ):
                try:
                    rc = writer.main([
                        "--allow-live", "--power-policy", TARGET_EPOCH["power_policy"],
                        "--output-root", str(self.root / "captures"),
                    ])
                except Exception as exc:
                    self.fail(f"CLI leaked {type(exc).__name__} instead of a refusal: {exc}")
                self.assertEqual(rc, 2, error.getvalue())
                refusal = json.loads(error.getvalue())
                self.assertEqual(refusal["code"], RefusalCode.FROZEN_PROTOCOL_INVALID.value)
                self.assertEqual(refusal["context"]["reason"], "acceptance_artifact_derivation_invalid")
                self.assertFalse((self.root / "captures").exists())

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
            snapshot = self._continuation_snapshot()
            # CLI owns the snapshot; this test only replaces disk custody I/O.
            with patch.object(writer, "load_calibration_ledger_snapshot", return_value=snapshot):
                rc = writer.main([
                    "--allow-live", "--derivation-only", "--power-policy", TARGET_EPOCH["power_policy"],
                    "--identity-epoch-json-for-test", str(identity),
                    "--output-root", str(self.root / "captures"),
                ])
        self.assertEqual(rc, 2, error.getvalue())
        refusal = json.loads(error.getvalue())
        self.assertEqual(refusal["code"], RefusalCode.DERIVATION_ONLY_EPOCH_UNCHANGED.value)
        self.assertFalse((self.root / "captures").exists())

    def test_derivation_only_cli_uses_snapshot_before_epoch_guard(self):
        identity = self.root / "identity.json"
        identity.write_text(json.dumps(TARGET_EPOCH))
        with registered_continuation(self.root), redirect_stderr(io.StringIO()) as error:
            snapshot = replace(self._continuation_snapshot(), bracket_sessions=())
            with patch.object(writer, "load_calibration_ledger_snapshot", return_value=snapshot) as loader:
                rc = writer.main([
                    "--allow-live", "--derivation-only", "--power-policy", TARGET_EPOCH["power_policy"],
                    "--identity-epoch-json-for-test", str(identity),
                    "--output-root", str(self.root / "captures"),
                ])
        self.assertEqual(rc, 2, error.getvalue())
        loader.assert_called_once()
        refusal = json.loads(error.getvalue())
        # The absent terminal session excludes the continuation, so this epoch
        # reaches the derivation-session requirement instead of the epoch guard.
        self.assertEqual(refusal["code"], RefusalCode.DERIVATION_ONLY_SESSION_KIND_REQUIRED.value)
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
