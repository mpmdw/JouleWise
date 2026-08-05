from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = REPO_ROOT / "scripts" / "validate_gate_packet.py"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class ValidateGatePacketTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.charter = self.root / "charter.md"
        self.charter_bytes = b"synthetic charter v2\n"
        self.charter.write_bytes(self.charter_bytes)
        self.charter_sha = sha256(self.charter_bytes)
        self.exhibit = self.root / "inputs" / "evidence.txt"
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
            manifest_body = (
                f"{sha256(self.exhibit_bytes)}  inputs/evidence.txt\n"
            )
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
        packet = self.root / "PACKET.md"
        packet_bytes = packet_text.encode("utf-8")
        packet.write_bytes(packet_bytes)
        return packet, packet_bytes, manifest_body.encode("utf-8")

    def run_validator(
        self,
        packet: Path,
        *,
        expected: str | None = None,
        receipt_out: Path | None = None,
        attest: bool = False,
    ) -> tuple[subprocess.CompletedProcess[str], dict[str, object]]:
        command = [
            sys.executable,
            str(VALIDATOR),
            "--packet",
            str(packet),
            "--charter",
            str(self.charter),
            "--expected-charter-sha256",
            expected if expected is not None else self.charter_sha,
        ]
        if receipt_out is not None:
            command.extend(["--receipt-out", str(receipt_out)])
        if attest:
            command.extend(
                [
                    "--launch-environment-attestation",
                    "worktree verified doctrine-free",
                    "--contamination-disclosure",
                    "none disclosed",
                ]
            )
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(completed.stderr, "")
        return completed, json.loads(completed.stdout)

    def test_accepts_valid_packet_and_receipt_identifies_exact_bytes(self) -> None:
        packet, packet_bytes, manifest_bytes = self.write_packet(
            pin=self.charter_sha.upper()
        )
        receipt_path = self.root / "receipt.json"

        completed, receipt = self.run_validator(
            packet,
            expected=self.charter_sha.upper(),
            receipt_out=receipt_path,
            attest=True,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(receipt["result"], "PASS")
        self.assertIsNone(receipt["reason"])
        self.assertEqual(receipt["digests"]["packet_sha256"], sha256(packet_bytes))
        self.assertEqual(
            receipt["digests"]["charter_sha256"], sha256(self.charter_bytes)
        )
        self.assertEqual(
            receipt["digests"]["exhibit_manifest_sha256"],
            sha256(manifest_bytes),
        )
        self.assertEqual(
            receipt["digests"]["exhibits"],
            [
                {
                    "expected_sha256": sha256(self.exhibit_bytes),
                    "observed_sha256": sha256(self.exhibit_bytes),
                    "path": "inputs/evidence.txt",
                }
            ],
        )
        self.assertEqual(receipt["packet_charter_pin_sha256"], self.charter_sha)
        self.assertEqual(receipt["packet_charter_path"], "charter.md")
        self.assertEqual(
            receipt["convening_attestations"],
            {
                "contamination_disclosure": "none disclosed",
                "launch_environment": "worktree verified doctrine-free",
            },
        )
        self.assertEqual(receipt_path.read_text(), completed.stdout)

    def test_refuses_wrong_trusted_charter_digest(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        completed, receipt = self.run_validator(packet, expected="0" * 64)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(receipt["result"], "REFUSE")
        self.assertEqual(receipt["reason"], "charter_digest_mismatch")

    def test_refuses_tampered_exhibit(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        self.exhibit.write_bytes(b"tampered\n")
        completed, receipt = self.run_validator(packet)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(receipt["reason"], "exhibit_digest_mismatch")
        self.assertEqual(
            receipt["digests"]["exhibits"][0]["observed_sha256"],
            sha256(b"tampered\n"),
        )

    def test_refuses_missing_charter_pin_section(self) -> None:
        packet, _, _ = self.write_packet(pin=None)
        completed, receipt = self.run_validator(packet)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(receipt["reason"], "charter_pin_missing")

    def test_refuses_duplicate_charter_pin_sections(self) -> None:
        packet, _, _ = self.write_packet(
            pin=self.charter_sha, duplicate_pin=True
        )
        completed, receipt = self.run_validator(packet)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(receipt["reason"], "charter_pin_duplicate")

    def test_refuses_ambiguous_pin_inside_the_scoped_section(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha, ambiguous_pin=True)
        completed, receipt = self.run_validator(packet)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(receipt["reason"], "charter_pin_ambiguous")

    def test_refuses_manifest_listing_nonexistent_exhibit(self) -> None:
        missing_digest = sha256(b"not present\n")
        packet, _, _ = self.write_packet(
            pin=self.charter_sha,
            manifest_body=f"{missing_digest}  inputs/missing.txt\n",
        )
        completed, receipt = self.run_validator(packet)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(receipt["reason"], "exhibit_unreadable")
        self.assertEqual(receipt["details"], [{"path": "inputs/missing.txt"}])

    def test_refuses_unparseable_manifest(self) -> None:
        packet, _, manifest_bytes = self.write_packet(
            pin=self.charter_sha,
            manifest_body=f"{sha256(self.exhibit_bytes)} inputs/evidence.txt\n",
        )
        completed, receipt = self.run_validator(packet)
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(receipt["reason"], "manifest_parse_error")
        self.assertEqual(
            receipt["digests"]["exhibit_manifest_sha256"], sha256(manifest_bytes)
        )

    def test_receipt_is_byte_deterministic_and_null_attestations_are_explicit(
        self,
    ) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        first, first_receipt = self.run_validator(packet)
        second, second_receipt = self.run_validator(packet)
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout.encode("utf-8"), second.stdout.encode("utf-8"))
        self.assertEqual(first_receipt, second_receipt)
        self.assertEqual(
            first_receipt["convening_attestations"],
            {"contamination_disclosure": None, "launch_environment": None},
        )


if __name__ == "__main__":
    unittest.main()
