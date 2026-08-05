from __future__ import annotations

import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_gate_packet.py"


VALIDATOR_SPEC = importlib.util.spec_from_file_location("validate_gate_packet", VALIDATOR)
assert VALIDATOR_SPEC is not None and VALIDATOR_SPEC.loader is not None
VALIDATOR_MODULE = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(VALIDATOR_MODULE)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ValidateGatePacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.packet_directory = self.root / "packet"
        self.packet_directory.mkdir()
        self.charter = self.root / "charter.md"
        self.charter_bytes = b"synthetic charter v2\n"
        self.charter.write_bytes(self.charter_bytes)
        self.charter_sha = sha256(self.charter_bytes)
        self.exhibit = self.packet_directory / "inputs" / "evidence.txt"
        self.exhibit.parent.mkdir()
        self.exhibit_bytes = b"sealed evidence\n"
        self.exhibit.write_bytes(self.exhibit_bytes)

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def write_packet(
        self,
        *,
        pin: str | None = None,
        duplicate_pin: bool = False,
        manifest_body: str | None = None,
        ambiguous_pin: bool = False,
    ) -> tuple[Path, bytes, bytes]:
        if manifest_body is None:
            manifest_body = f"{sha256(self.exhibit_bytes)}  inputs/evidence.txt\n"
        pin_section = ""
        if pin is not None:
            pin_section = (
                "## 6. Charter pin\n\n"
                "Charter under validation: `charter.md`\n"
                "v2, sha256\n"
                f"`{pin}`.\n\n"
            )
            if ambiguous_pin:
                pin_section = pin_section.replace(
                    f"`{pin}`.", f"`{pin}` and `{pin}`."
                )
            if duplicate_pin:
                pin_section += (
                    "## Charter pin\n\n"
                    "Charter: `charter.md`\n"
                    f"sha256 `{pin}`\n\n"
                )
        packet_text = (
            "# Synthetic cold gate\n\n"
            "## Exhibit manifest (sha256, fixture)\n\n"
            "```\n"
            f"{manifest_body}"
            "```\n\n"
            f"{pin_section}"
            "## Bootstrap declaration\n\n"
            f"The same digest may recur here: {self.charter_sha}.\n"
        )
        packet = self.packet_directory / "PACKET.md"
        packet_bytes = packet_text.encode("utf-8")
        packet.write_bytes(packet_bytes)
        return packet, packet_bytes, manifest_body.encode("utf-8")

    def run_validator(
        self,
        packet: Path,
        *,
        expected_charter: str | None = None,
        expected_packet: str | None = None,
        receipt_out: Path | None = None,
        launch_environment_attestation: str | None = None,
        contamination_disclosure: str | None = None,
    ) -> tuple[subprocess.CompletedProcess[bytes], dict[str, object]]:
        command = [
            sys.executable,
            str(VALIDATOR),
            "--packet",
            str(packet),
            "--charter",
            str(self.charter),
            "--expected-packet-sha256",
            expected_packet if expected_packet is not None else sha256(packet.read_bytes()),
            "--expected-charter-sha256",
            expected_charter if expected_charter is not None else self.charter_sha,
        ]
        if receipt_out is not None:
            command.extend(["--receipt-out", str(receipt_out)])
        if launch_environment_attestation is not None:
            command.extend(
                ["--launch-environment-attestation", launch_environment_attestation]
            )
        if contamination_disclosure is not None:
            command.extend(["--contamination-disclosure", contamination_disclosure])
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        receipt = json.loads(completed.stdout.decode("utf-8"))
        return completed, receipt

    def assert_refusal(
        self,
        completed: subprocess.CompletedProcess[bytes],
        receipt: dict[str, object],
        reason: str,
    ) -> None:
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(receipt["result"], "REFUSE")
        self.assertEqual(receipt["reason"], reason)

    def test_accepts_valid_packet_and_receipt_identifies_exact_bytes(self) -> None:
        packet, packet_bytes, manifest_bytes = self.write_packet(
            pin=self.charter_sha.upper()
        )
        receipt_path = self.root / "receipt.json"

        completed, receipt = self.run_validator(
            packet,
            expected_charter=self.charter_sha.upper(),
            expected_packet=sha256(packet_bytes).upper(),
            receipt_out=receipt_path,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(receipt["result"], "PASS")
        self.assertEqual(receipt["digests"]["packet_sha256"], sha256(packet_bytes))
        self.assertEqual(
            receipt["digests"]["exhibit_manifest_sha256"], sha256(manifest_bytes)
        )
        self.assertEqual(receipt["inputs"], {"charter": "charter.md", "packet": "PACKET.md"})
        self.assertEqual(receipt["digests"]["exhibits"][0]["path"], "evidence.txt")
        self.assertNotIn(str(self.root).encode("utf-8"), completed.stdout)
        self.assertEqual(receipt_path.read_bytes(), completed.stdout)

    def test_refuses_wrong_trusted_charter_digest(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        completed, receipt = self.run_validator(packet, expected_charter="0" * 64)
        self.assert_refusal(completed, receipt, "charter_trusted_observed_mismatch")

    def test_refuses_trusted_equals_observed_but_not_packet_pin(self) -> None:
        packet, _, _ = self.write_packet(pin="0" * 64)
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(
            completed, receipt, "charter_trusted_packet_pin_mismatch"
        )

    def test_refuses_trusted_equals_packet_pin_but_not_observed(self) -> None:
        old_charter_sha = self.charter_sha
        packet, _, _ = self.write_packet(pin=old_charter_sha)
        self.charter.write_bytes(b"changed charter\n")
        completed, receipt = self.run_validator(
            packet, expected_charter=old_charter_sha
        )
        self.assert_refusal(
            completed, receipt, "charter_packet_pin_observed_mismatch"
        )

    def test_refuses_wrong_expected_packet_digest(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        completed, receipt = self.run_validator(packet, expected_packet="0" * 64)
        self.assert_refusal(completed, receipt, "packet_digest_mismatch")

    def test_refuses_tampered_packet_before_manifest_validation(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        packet.write_bytes(packet_bytes + b"tampered\n")
        completed, receipt = self.run_validator(
            packet, expected_packet=sha256(packet_bytes)
        )
        self.assert_refusal(completed, receipt, "packet_digest_mismatch")
        self.assertIsNone(receipt["digests"]["exhibit_manifest_sha256"])
        self.assertEqual(receipt["digests"]["exhibits"], [])

    def test_refuses_missing_expected_packet_argument(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        completed = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--packet",
                str(packet),
                "--charter",
                str(self.charter),
                "--expected-charter-sha256",
                self.charter_sha,
            ],
            cwd=REPO_ROOT,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        receipt = json.loads(completed.stdout.decode("utf-8"))
        self.assert_refusal(completed, receipt, "cli_invalid")

    def test_help_exits_nonzero_without_a_receipt(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--help"],
            cwd=REPO_ROOT,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(b"usage:", completed.stdout)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(completed.stdout.decode("utf-8"))

    def test_unexpected_exception_becomes_internal_error_refusal(self) -> None:
        captured = mock.Mock(buffer=io.BytesIO())
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        with (
            mock.patch.object(
                VALIDATOR_MODULE, "validate", side_effect=RuntimeError("fixture")
            ),
            mock.patch.object(VALIDATOR_MODULE.sys, "stdout", captured),
        ):
            returncode = VALIDATOR_MODULE.main(
                [
                    "--packet",
                    str(packet),
                    "--charter",
                    str(self.charter),
                    "--expected-packet-sha256",
                    sha256(packet_bytes),
                    "--expected-charter-sha256",
                    self.charter_sha,
                ]
            )
        receipt = json.loads(captured.buffer.getvalue().decode("utf-8"))
        self.assertEqual(returncode, 2)
        self.assertEqual(receipt["result"], "REFUSE")
        self.assertEqual(receipt["reason"], "internal_error")

    def test_refuses_tampered_exhibit(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        self.exhibit.write_bytes(b"tampered\n")
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "exhibit_digest_mismatch")
        self.assertEqual(
            receipt["digests"]["exhibits"][0]["observed_sha256"],
            sha256(b"tampered\n"),
        )

    def test_refuses_missing_charter_pin_section(self) -> None:
        packet, _, _ = self.write_packet(pin=None)
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "charter_pin_missing")

    def test_refuses_duplicate_charter_pin_sections(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha, duplicate_pin=True)
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "charter_pin_duplicate")

    def test_refuses_ambiguous_pin_inside_the_scoped_section(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha, ambiguous_pin=True)
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "charter_pin_ambiguous")

    def test_refuses_charter_digest_without_true_token_boundaries(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        packet.write_bytes(
            packet_bytes.replace(
                f"`{self.charter_sha}`.".encode("ascii"),
                f"_{self.charter_sha}_".encode("ascii"),
            )
        )
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "charter_pin_ambiguous")

    def test_refuses_manifest_listing_nonexistent_exhibit(self) -> None:
        missing_digest = sha256(b"not present\n")
        packet, _, _ = self.write_packet(
            pin=self.charter_sha,
            manifest_body=f"{missing_digest}  inputs/missing.txt\n",
        )
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "exhibit_unreadable")
        self.assertEqual(receipt["details"], [{"path": "missing.txt"}])
        self.assertNotIn(str(self.root).encode("utf-8"), completed.stdout)

    def test_malformed_manifest_refuses(self) -> None:
        packet, _, _ = self.write_packet(
            pin=self.charter_sha,
            manifest_body=f"{sha256(self.exhibit_bytes)} inputs/evidence.txt\n",
        )
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "manifest_parse_error")

    def test_refuses_drive_qualified_manifest_paths(self) -> None:
        for path_text in ("C:/evidence.txt", "C:evidence.txt"):
            with self.subTest(path_text=path_text):
                packet, _, _ = self.write_packet(
                    pin=self.charter_sha,
                    manifest_body=f"{sha256(self.exhibit_bytes)}  {path_text}\n",
                )
                completed, receipt = self.run_validator(packet)
                self.assert_refusal(completed, receipt, "manifest_parse_error")

    def test_refuses_symlinked_exhibit(self) -> None:
        self.exhibit.unlink()
        target = self.root / "outside.txt"
        target.write_bytes(self.exhibit_bytes)
        self.exhibit.symlink_to(target)
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "exhibit_custody_invalid")

    def test_refuses_symlinked_intermediate_directory(self) -> None:
        # A deterministic race test is not possible; this proves the dirfd walk's
        # intermediate-component O_NOFOLLOW mechanism.
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "evidence.txt").write_bytes(self.exhibit_bytes)
        (self.packet_directory / "linked").symlink_to(outside, target_is_directory=True)
        packet, _, _ = self.write_packet(
            pin=self.charter_sha,
            manifest_body=f"{sha256(self.exhibit_bytes)}  linked/evidence.txt\n",
        )
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "exhibit_custody_invalid")

    def test_refuses_non_regular_exhibit(self) -> None:
        packet, _, _ = self.write_packet(
            pin=self.charter_sha,
            manifest_body=f"{sha256(b'')}  inputs\n",
        )
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "exhibit_custody_invalid")

    def test_refuses_two_manifest_rows_aliasing_one_file(self) -> None:
        alias = self.exhibit.parent / "alias.txt"
        os.link(self.exhibit, alias)
        digest = sha256(self.exhibit_bytes)
        packet, _, _ = self.write_packet(
            pin=self.charter_sha,
            manifest_body=(
                f"{digest}  inputs/evidence.txt\n"
                f"{digest}  inputs/alias.txt\n"
            ),
        )
        completed, receipt = self.run_validator(packet)
        self.assert_refusal(completed, receipt, "exhibit_alias_duplicate")

    def test_refuses_receipt_out_aliasing_an_input(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        completed, receipt = self.run_validator(packet, receipt_out=packet)
        self.assert_refusal(completed, receipt, "receipt_out_unsafe")
        self.assertTrue(packet.read_bytes().startswith(b"# Synthetic cold gate"))

    def test_refuses_receipt_out_inside_packet_directory(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        receipt_path = self.packet_directory / "new-receipt.json"
        completed, receipt = self.run_validator(
            packet, expected_packet="0" * 64, receipt_out=receipt_path
        )
        self.assert_refusal(completed, receipt, "receipt_out_unsafe")
        self.assertFalse(receipt_path.exists())

    def test_refuses_overwriting_existing_receipt(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        receipt_path = self.root / "existing.json"
        receipt_path.write_bytes(b"preserve me\n")
        completed, receipt = self.run_validator(packet, receipt_out=receipt_path)
        self.assert_refusal(completed, receipt, "receipt_out_exists")
        self.assertEqual(receipt_path.read_bytes(), b"preserve me\n")

    def test_receipt_write_failure_turns_pass_into_refusal(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        receipt_path = self.root / "receipt.json"
        captured = mock.Mock(buffer=io.BytesIO())
        with (
            mock.patch.object(
                VALIDATOR_MODULE,
                "_write_receipt_exclusive",
                side_effect=OSError("fixture"),
            ),
            mock.patch.object(VALIDATOR_MODULE.sys, "stdout", captured),
        ):
            returncode = VALIDATOR_MODULE.main(
                [
                    "--packet",
                    str(packet),
                    "--charter",
                    str(self.charter),
                    "--expected-packet-sha256",
                    sha256(packet_bytes),
                    "--expected-charter-sha256",
                    self.charter_sha,
                    "--receipt-out",
                    str(receipt_path),
                ]
            )
        receipt = json.loads(captured.buffer.getvalue().decode("utf-8"))
        self.assertEqual(returncode, 2)
        self.assertEqual(receipt["result"], "REFUSE")
        self.assertEqual(receipt["reason"], "receipt_write_failed")

    def test_receipt_write_failure_preserves_validation_refusal(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        receipt_path = self.root / "receipt.json"
        captured = mock.Mock(buffer=io.BytesIO())
        with (
            mock.patch.object(
                VALIDATOR_MODULE,
                "_write_receipt_exclusive",
                side_effect=OSError("fixture"),
            ),
            mock.patch.object(VALIDATOR_MODULE.sys, "stdout", captured),
        ):
            returncode = VALIDATOR_MODULE.main(
                [
                    "--packet",
                    str(packet),
                    "--charter",
                    str(self.charter),
                    "--expected-packet-sha256",
                    "0" * 64,
                    "--expected-charter-sha256",
                    self.charter_sha,
                    "--receipt-out",
                    str(receipt_path),
                ]
            )
        receipt = json.loads(captured.buffer.getvalue().decode("utf-8"))
        self.assertEqual(returncode, 2)
        self.assertEqual(receipt["result"], "REFUSE")
        self.assertEqual(receipt["reason"], "packet_digest_mismatch")
        self.assertEqual(
            receipt["receipt_out_error"],
            {"path": "receipt.json", "reason": "receipt_write_failed"},
        )

    def test_refuses_absolute_path_in_convening_attestation(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        for field in (
            "launch_environment_attestation",
            "contamination_disclosure",
        ):
            with self.subTest(field=field):
                completed, receipt = self.run_validator(
                    packet,
                    **{field: str(self.root / "launch-context")},
                )
                self.assert_refusal(completed, receipt, "attestation_invalid")
                self.assertNotIn(str(self.root).encode("utf-8"), completed.stdout)

    def test_receipt_is_byte_deterministic(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        first, first_receipt = self.run_validator(packet)
        second, second_receipt = self.run_validator(packet)
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first_receipt["result"], "PASS")
        self.assertEqual(second_receipt["result"], "PASS")


if __name__ == "__main__":
    unittest.main()
