from __future__ import annotations

import base64
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
        prefix: str = "",
        pin_section_prefix: str = "",
    ) -> tuple[Path, bytes, bytes]:
        if manifest_body is None:
            manifest_body = f"{sha256(self.exhibit_bytes)}  inputs/evidence.txt\n"
        pin_section = ""
        if pin is not None:
            pin_section = (
                "## 6. Charter pin\n\n"
                f"{pin_section_prefix}"
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
            f"{prefix}"
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
    ) -> tuple[subprocess.CompletedProcess[bytes], dict[str, object]]:
        arguments = [
            "--packet",
            str(packet),
            "--charter",
            str(self.charter),
            "--expected-packet-sha256",
            expected_packet if expected_packet is not None else sha256(packet.read_bytes()),
            "--expected-charter-sha256",
            expected_charter if expected_charter is not None else self.charter_sha,
        ]
        completed = self.run_cli(arguments)
        receipt = json.loads(completed.stdout.decode("utf-8"))
        return completed, receipt

    def run_cli(self, arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), *arguments],
            cwd=REPO_ROOT,
            text=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def assert_refusal(
        self,
        completed: subprocess.CompletedProcess[bytes],
        receipt: dict[str, object],
        reason: str,
    ) -> None:
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(receipt["result"], "REFUSE")
        self.assertEqual(receipt["reason"], reason)
        self.assertEqual(receipt["schema"], "coldgate-validator-receipt/v2")
        self.assertEqual(
            receipt["binding_scope"], "validation_time_observation_only"
        )
        self.assertIs(receipt["judge_handoff_bound"], False)

    def test_accepts_valid_packet_and_receipt_identifies_exact_bytes(self) -> None:
        packet, packet_bytes, manifest_bytes = self.write_packet(
            pin=self.charter_sha.upper()
        )
        completed, receipt = self.run_validator(
            packet,
            expected_charter=self.charter_sha.upper(),
            expected_packet=sha256(packet_bytes).upper(),
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(receipt["result"], "PASS")
        self.assertEqual(receipt["digests"]["packet_sha256"], sha256(packet_bytes))
        self.assertEqual(
            receipt["digests"]["exhibit_manifest_sha256"], sha256(manifest_bytes)
        )
        self.assertEqual(receipt["inputs"], {"charter": "charter.md", "packet": "PACKET.md"})
        self.assertEqual(receipt["digests"]["exhibits"][0]["path"], "evidence.txt")
        self.assertEqual(receipt["schema"], "coldgate-validator-receipt/v2")
        self.assertEqual(
            receipt["binding_scope"], "validation_time_observation_only"
        )
        self.assertIs(receipt["judge_handoff_bound"], False)
        self.assertNotIn("convening_attestations", receipt)
        self.assertNotIn(str(self.root).encode("utf-8"), completed.stdout)

    def test_runner_delivers_original_snapshot_after_path_replacement(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        original_capture = VALIDATOR_MODULE.capture_and_validate
        transported: list[bytes] = []

        def capture_then_replace(**kwargs: object) -> object:
            result = original_capture(**kwargs)
            replacement_packet = self.packet_directory / "replacement-packet"
            replacement_packet.write_bytes(b"replacement packet\n")
            os.replace(replacement_packet, packet)
            replacement_charter = self.root / "replacement-charter"
            replacement_charter.write_bytes(b"replacement charter\n")
            os.replace(replacement_charter, self.charter)
            replacement_exhibit = self.exhibit.parent / "replacement-exhibit"
            replacement_exhibit.write_bytes(b"replacement exhibit\n")
            os.replace(replacement_exhibit, self.exhibit)
            return result

        def fake_transport(request_bytes: bytes) -> dict[str, str]:
            transported.append(request_bytes)
            return {
                "judge_request_id": "judge-request-1",
                "observed_request_sha256": sha256(request_bytes),
            }

        with mock.patch.object(
            VALIDATOR_MODULE,
            "capture_and_validate",
            side_effect=capture_then_replace,
        ):
            result = VALIDATOR_MODULE.run_gate_handoff(
                packet_arg=str(packet),
                charter_arg=str(self.charter),
                expected_packet_sha256=sha256(packet_bytes),
                expected_charter_sha256=self.charter_sha,
                transport=fake_transport,
            )

        self.assertEqual(result.runner_receipt["result"], "PASS")
        self.assertEqual(len(transported), 1)
        request = json.loads(transported[0].decode("utf-8"))
        self.assertEqual(
            base64.b64decode(request["sources"]["packet"]["bytes_base64"]),
            packet_bytes,
        )
        self.assertEqual(
            base64.b64decode(request["sources"]["charter"]["bytes_base64"]),
            self.charter_bytes,
        )
        self.assertEqual(
            base64.b64decode(request["sources"]["exhibits"][0]["bytes_base64"]),
            self.exhibit_bytes,
        )

    def test_runner_delivers_original_snapshot_after_same_inode_mutation(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        original_identity = self.exhibit.stat().st_ino
        original_capture = VALIDATOR_MODULE.capture_and_validate
        transported: list[bytes] = []

        def capture_then_mutate(**kwargs: object) -> object:
            result = original_capture(**kwargs)
            with self.exhibit.open("r+b") as second_descriptor:
                second_descriptor.seek(0)
                second_descriptor.write(b"mutated evidence")
                second_descriptor.truncate()
            return result

        def fake_transport(request_bytes: bytes) -> dict[str, str]:
            transported.append(request_bytes)
            return {
                "judge_session_id": "judge-session-1",
                "observed_request_sha256": sha256(request_bytes),
            }

        with mock.patch.object(
            VALIDATOR_MODULE,
            "capture_and_validate",
            side_effect=capture_then_mutate,
        ):
            result = VALIDATOR_MODULE.run_gate_handoff(
                packet_arg=str(packet),
                charter_arg=str(self.charter),
                expected_packet_sha256=sha256(packet_bytes),
                expected_charter_sha256=self.charter_sha,
                transport=fake_transport,
            )

        self.assertEqual(self.exhibit.stat().st_ino, original_identity)
        self.assertNotEqual(self.exhibit.read_bytes(), self.exhibit_bytes)
        self.assertEqual(result.runner_receipt["result"], "PASS")
        self.assertEqual(len(transported), 1)
        request = json.loads(transported[0].decode("utf-8"))
        self.assertEqual(
            base64.b64decode(request["sources"]["exhibits"][0]["bytes_base64"]),
            self.exhibit_bytes,
        )

    def test_refusal_never_releases_a_snapshot(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        self.exhibit.write_bytes(b"tampered before capture\n")
        receipt, snapshot = VALIDATOR_MODULE.capture_and_validate(
            packet_arg=str(packet),
            charter_arg=str(self.charter),
            expected_packet_sha256=sha256(packet_bytes),
            expected_charter_sha256=self.charter_sha,
        )
        self.assertEqual(receipt["result"], "REFUSE")
        self.assertEqual(receipt["reason"], "exhibit_digest_mismatch")
        self.assertIsNone(snapshot)

    def test_handoff_binding_is_invariant_to_semantically_equivalent_json_encodings(
        self,
    ) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        non_ascii_packet = packet.with_name("PACKÉT-測試.md")
        packet.rename(non_ascii_packet)
        encoders = {
            "compact_raw_utf8": lambda value: (
                json.dumps(
                    value,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                + "\n"
            ).encode("utf-8"),
            "spaced": lambda value: (
                json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n"
            ).encode("utf-8"),
            "ascii_escaped": lambda value: (
                json.dumps(
                    value,
                    ensure_ascii=True,
                    separators=(",", ":"),
                    sort_keys=True,
                )
                + "\n"
            ).encode("utf-8"),
        }
        emitted_by_encoding: dict[str, bytes] = {}

        for encoding_name, encoder in encoders.items():
            transported: list[bytes] = []

            def fake_transport(request_bytes: bytes) -> dict[str, str]:
                transported.append(request_bytes)
                return {
                    "judge_request_id": "judge-request-binding",
                    "observed_request_sha256": sha256(request_bytes),
                }

            with self.subTest(encoding=encoding_name), mock.patch.object(
                VALIDATOR_MODULE,
                "_canonical_json",
                side_effect=encoder,
            ):
                result = VALIDATOR_MODULE.run_gate_handoff(
                    packet_arg=str(non_ascii_packet),
                    charter_arg=str(self.charter),
                    expected_packet_sha256=sha256(packet_bytes),
                    expected_charter_sha256=self.charter_sha,
                    transport=fake_transport,
                )

                self.assertEqual(len(transported), 1)
                emitted = transported[0]
                emitted_by_encoding[encoding_name] = emitted
                emitted_sha256 = sha256(emitted)
                request = json.loads(emitted.decode("utf-8"))
                receipt = result.runner_receipt
                self.assertEqual(request["schema"], "coldgate-judge-request/v1")
                self.assertEqual(
                    request["validator_receipt"], result.validator_receipt
                )
                self.assertEqual(receipt["schema"], "coldgate-runner-receipt/v1")
                self.assertEqual(receipt["result"], "PASS")
                self.assertIs(receipt["judge_handoff_bound"], True)
                self.assertEqual(
                    receipt["judge_identity"],
                    {"kind": "request", "value": "judge-request-binding"},
                )
                self.assertEqual(receipt["request_sha256"], emitted_sha256)
                self.assertEqual(
                    receipt["transport_observed_request_sha256"], emitted_sha256
                )
                self.assertEqual(
                    receipt["source_digests"], result.validator_receipt["digests"]
                )

                packet_source = request["sources"]["packet"]
                self.assertEqual(packet_source["name"], non_ascii_packet.name)
                self.assertEqual(
                    base64.b64decode(packet_source["bytes_base64"]), packet_bytes
                )
                self.assertEqual(
                    sha256(packet_bytes),
                    packet_source["sha256"],
                )
                self.assertEqual(
                    packet_source["sha256"],
                    result.validator_receipt["digests"]["packet_sha256"],
                )
                charter_source = request["sources"]["charter"]
                self.assertEqual(
                    base64.b64decode(charter_source["bytes_base64"]),
                    self.charter_bytes,
                )
                self.assertEqual(
                    sha256(self.charter_bytes),
                    charter_source["sha256"],
                )
                self.assertEqual(
                    charter_source["sha256"],
                    result.validator_receipt["digests"]["charter_sha256"],
                )
                exhibit_source = request["sources"]["exhibits"][0]
                self.assertEqual(
                    base64.b64decode(exhibit_source["bytes_base64"]),
                    self.exhibit_bytes,
                )
                self.assertEqual(
                    sha256(self.exhibit_bytes),
                    exhibit_source["sha256"],
                )
                self.assertEqual(
                    exhibit_source["sha256"],
                    result.validator_receipt["digests"]["exhibits"][0][
                        "observed_sha256"
                    ],
                )

        self.assertEqual(len(set(emitted_by_encoding.values())), len(encoders))

    def test_runner_refuses_bad_acknowledgements_after_one_delivery(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        cases = (
            (
                "digest_mismatch",
                {
                    "judge_request_id": "request-1",
                    "observed_request_sha256": "0" * 64,
                },
                "request_digest_unacknowledged",
            ),
            (
                "digest_missing",
                {
                    "judge_request_id": "request-1",
                    "observed_request_sha256": None,
                },
                "request_digest_unacknowledged",
            ),
            (
                "identity_missing",
                {"observed_request_sha256": None},
                "judge_identity_unacknowledged",
            ),
        )
        for name, acknowledgement, reason in cases:
            delivered: list[bytes] = []

            def fake_transport(request_bytes: bytes) -> dict[str, str | None]:
                delivered.append(request_bytes)
                response = dict(acknowledgement)
                if name == "identity_missing":
                    response["observed_request_sha256"] = sha256(request_bytes)
                return response

            with self.subTest(name=name):
                result = VALIDATOR_MODULE.run_gate_handoff(
                    packet_arg=str(packet),
                    charter_arg=str(self.charter),
                    expected_packet_sha256=sha256(packet_bytes),
                    expected_charter_sha256=self.charter_sha,
                    transport=fake_transport,
                )
                self.assertEqual(len(delivered), 1)
                self.assertEqual(result.runner_receipt["result"], "REFUSE")
                self.assertIs(result.runner_receipt["judge_handoff_bound"], False)
                self.assertEqual(result.runner_receipt["reason"], reason)

    def test_stdin_transport_delivers_canonical_request_once(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        captured_request = self.root / "captured-request.json"
        fake_judge = (
            "import hashlib,json,pathlib,sys;"
            "data=sys.stdin.buffer.read();"
            "pathlib.Path(sys.argv[1]).open('xb').write(data);"
            "json.dump({'judge_session_id':'stdin-session-1',"
            "'observed_request_sha256':hashlib.sha256(data).hexdigest()},sys.stdout)"
        )

        result = VALIDATOR_MODULE.run_gate_handoff(
            packet_arg=str(packet),
            charter_arg=str(self.charter),
            expected_packet_sha256=sha256(packet_bytes),
            expected_charter_sha256=self.charter_sha,
            transport=VALIDATOR_MODULE.stdin_json_transport(
                [sys.executable, "-c", fake_judge, str(captured_request)]
            ),
        )

        delivered = captured_request.read_bytes()
        self.assertEqual(result.runner_receipt["result"], "PASS")
        self.assertEqual(result.runner_receipt["request_sha256"], sha256(delivered))
        self.assertEqual(
            result.runner_receipt["judge_identity"],
            {"kind": "session", "value": "stdin-session-1"},
        )
        self.assertEqual(
            json.loads(delivered.decode("utf-8"))["schema"],
            "coldgate-judge-request/v1",
        )

    def test_validation_refusal_never_invokes_judge_transport(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        calls: list[bytes] = []

        result = VALIDATOR_MODULE.run_gate_handoff(
            packet_arg=str(packet),
            charter_arg=str(self.charter),
            expected_packet_sha256="0" * 64,
            expected_charter_sha256=self.charter_sha,
            transport=lambda request_bytes: calls.append(request_bytes),
        )

        self.assertEqual(calls, [])
        self.assertEqual(result.validator_receipt["reason"], "packet_digest_mismatch")
        self.assertEqual(result.runner_receipt["result"], "REFUSE")
        self.assertEqual(result.runner_receipt["reason"], "validation_refused")
        self.assertIsNone(result.runner_receipt["request_sha256"])

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

    def test_help_is_informational_and_lists_no_deleted_options(self) -> None:
        completed = self.run_cli(["--help"])
        self.assertEqual(completed.returncode, 0)
        self.assertIn(b"usage:", completed.stdout)
        self.assertIn(b"PASS is not launch authorization", completed.stdout)
        for deleted_option in (
            b"--launch-environment-attestation",
            b"--contamination-disclosure",
            b"--receipt-out",
        ):
            self.assertNotIn(deleted_option, completed.stdout)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(completed.stdout.decode("utf-8"))

    def test_every_nonzero_path_emits_one_v2_refusal_receipt(self) -> None:
        captured = mock.Mock(buffer=io.BytesIO())
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        with (
            mock.patch.object(
                VALIDATOR_MODULE, "validate", side_effect=RuntimeError("fixture")
            ),
            mock.patch.object(VALIDATOR_MODULE.sys, "stdout", captured),
        ):
            internal_returncode = VALIDATOR_MODULE.main(
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

        malformed = self.run_cli(["--not-a-validator-option"])
        missing_required = self.run_cli(
            [
                "--packet",
                str(packet),
                "--charter",
                str(self.charter),
                "--expected-charter-sha256",
                self.charter_sha,
            ]
        )
        validation_refusal, _ = self.run_validator(
            packet, expected_packet="0" * 64
        )
        cases = (
            (
                "malformed_argument",
                malformed.returncode,
                malformed.stdout,
                "cli_invalid",
            ),
            (
                "missing_required_argument",
                missing_required.returncode,
                missing_required.stdout,
                "cli_invalid",
            ),
            (
                "validation_refusal",
                validation_refusal.returncode,
                validation_refusal.stdout,
                "packet_digest_mismatch",
            ),
            (
                "unexpected_internal_failure",
                internal_returncode,
                captured.buffer.getvalue(),
                "internal_error",
            ),
        )
        for name, returncode, output, reason in cases:
            with self.subTest(name=name):
                self.assertNotEqual(returncode, 0)
                receipt = json.loads(output.decode("utf-8"))
                self.assertEqual(receipt["schema"], "coldgate-validator-receipt/v2")
                self.assertEqual(receipt["result"], "REFUSE")
                self.assertEqual(receipt["reason"], reason)
                self.assertEqual(
                    receipt["binding_scope"],
                    "validation_time_observation_only",
                )
                self.assertIs(receipt["judge_handoff_bound"], False)
                self.assertEqual(output, VALIDATOR_MODULE._canonical_json(receipt))
                self.assertNotIn(str(self.root).encode("utf-8"), output)

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

    def test_fenced_heading_examples_do_not_create_duplicates(self) -> None:
        packet, packet_bytes, manifest_bytes = self.write_packet(
            pin=self.charter_sha,
            prefix=(
                "```markdown\n"
                "## Charter pin\n"
                "```\n\n"
                "~~~ text\n"
                "## Exhibit manifest\n"
                "~~~~\n\n"
            ),
        )
        completed, receipt = self.run_validator(
            packet, expected_packet=sha256(packet_bytes)
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(receipt["result"], "PASS")
        self.assertEqual(
            receipt["digests"]["exhibit_manifest_sha256"], sha256(manifest_bytes)
        )

    def test_fenced_heading_does_not_end_real_charter_section(self) -> None:
        packet, _, _ = self.write_packet(
            pin=self.charter_sha,
            pin_section_prefix=(
                "   ````markdown\n"
                "# This fenced heading does not end the section\n"
                "   `````\n\n"
            ),
        )
        completed, receipt = self.run_validator(packet)
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(receipt["result"], "PASS")
        self.assertEqual(receipt["packet_charter_pin_sha256"], self.charter_sha)

    def test_backtick_in_backtick_info_string_exposes_duplicate_headings(self) -> None:
        manifest = f"{sha256(self.exhibit_bytes)}  inputs/evidence.txt\n"
        charter_section = (
            "## Charter pin\n\n"
            "Charter: `charter.md`\n"
            f"sha256 `{self.charter_sha}`\n\n"
        )
        manifest_section = (
            "## Exhibit manifest\n\n"
            "```\n"
            f"{manifest}"
            "```\n\n"
        )

        cases = (
            (
                "charter_and_manifest_duplicates",
                charter_section
                + "## First section end\n\n"
                + manifest_section
                + "## Second section end\n\n"
                + "````bogus`\n"
                + charter_section
                + manifest_section
                + "````\n",
                "charter_pin_duplicate",
            ),
            (
                "manifest_duplicate",
                charter_section
                + "## First section end\n\n"
                + manifest_section
                + "## Second section end\n\n"
                + "````bogus`\n"
                + manifest_section
                + "````\n",
                "manifest_parse_error",
            ),
        )
        for name, body, reason in cases:
            with self.subTest(name=name):
                packet = self.packet_directory / "PACKET.md"
                packet_bytes = ("# Synthetic cold gate\n\n" + body).encode("utf-8")
                packet.write_bytes(packet_bytes)
                completed, receipt = self.run_validator(
                    packet, expected_packet=sha256(packet_bytes)
                )
                self.assert_refusal(completed, receipt, reason)

    def test_markdown_fence_state_edge_behaviors(self) -> None:
        lines = [
            "```python",
            "# masked by backtick fence",
            "~~~~",
            "# different marker neither nests nor closes",
            "````",
            "# visible after closer",
            "    ```",
            "# visible after four-space-indented pseudo-fence",
            "~~~ info with ` backtick",
            "# masked by tilde fence",
            "```",
            "# backticks do not close tilde fence",
            "~~~~",
            "# visible after tilde closer",
            "```unterminated",
            "# masked through EOF",
        ]
        self.assertEqual(
            VALIDATOR_MODULE._outside_fence_mask(lines),
            [
                False,
                False,
                False,
                False,
                False,
                True,
                True,
                True,
                False,
                False,
                False,
                False,
                False,
                True,
                False,
                False,
            ],
        )

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

    def test_removed_attestation_flag_history_refuses_without_echo(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        base_arguments = [
            "--packet",
            str(packet),
            "--charter",
            str(self.charter),
            "--expected-packet-sha256",
            sha256(packet_bytes),
            "--expected-charter-sha256",
            self.charter_sha,
            "--launch-environment-attestation",
        ]
        cases = (
            ("/Users/edr/secret", "/Users/edr/secret"),
            ("cwd=/Users/edr/secret", "/Users/edr/secret"),
            ("cwd='/ secret'", "/ secret"),
            ("input / output", None),
        )
        for value, embedded_path in cases:
            with self.subTest(value=value):
                completed = self.run_cli([*base_arguments, value])
                receipt = json.loads(completed.stdout.decode("utf-8"))
                self.assert_refusal(completed, receipt, "cli_invalid")
                self.assertEqual(
                    completed.stdout, VALIDATOR_MODULE._canonical_json(receipt)
                )
                self.assertNotIn(value.encode("utf-8"), completed.stdout)
                if embedded_path is not None:
                    self.assertNotIn(
                        embedded_path.encode("utf-8"), completed.stdout
                    )

    def test_deleted_cli_surfaces_are_unknown_and_do_not_write(self) -> None:
        packet, packet_bytes, _ = self.write_packet(pin=self.charter_sha)
        receipt_path = self.root / "must-not-exist.json"
        common = [
            "--packet",
            str(packet),
            "--charter",
            str(self.charter),
            "--expected-packet-sha256",
            sha256(packet_bytes),
            "--expected-charter-sha256",
            self.charter_sha,
        ]
        cases = (
            ("--contamination-disclosure", "/private/disclosure"),
            ("--receipt-out", str(receipt_path)),
        )
        for option, value in cases:
            with self.subTest(option=option):
                completed = self.run_cli([*common, option, value])
                receipt = json.loads(completed.stdout.decode("utf-8"))
                self.assert_refusal(completed, receipt, "cli_invalid")
                self.assertNotIn(value.encode("utf-8"), completed.stdout)
        self.assertFalse(receipt_path.exists())

    def test_receipt_privacy_is_structural_for_absolute_input_paths(self) -> None:
        """Separate v2-shape checks from privacy regressions.

        ``assert_refusal`` and the explicit PASS assertions guard the new v2
        binding fields.  Basename-only serialization of valid packet/charter
        paths pre-existed at 38b6570.  The malformed-digest null/no-echo cases
        below are the B1-discriminating privacy behavior added after that
        baseline; the remaining CLI cases pin the already leak-free V4/V5/V7
        paths.
        """
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        passed, pass_receipt = self.run_validator(packet)
        refused, refuse_receipt = self.run_validator(
            packet, expected_packet="0" * 64
        )
        self.assertEqual(passed.returncode, 0)
        self.assertEqual(pass_receipt["result"], "PASS")
        self.assertEqual(
            pass_receipt["binding_scope"], "validation_time_observation_only"
        )
        self.assertIs(pass_receipt["judge_handoff_bound"], False)
        self.assert_refusal(refused, refuse_receipt, "packet_digest_mismatch")
        for output in (passed.stdout, refused.stdout):
            self.assertNotIn(str(self.root).encode("utf-8"), output)
            self.assertNotIn(str(packet).encode("utf-8"), output)
            self.assertNotIn(str(self.charter).encode("utf-8"), output)

        digest_cases = (
            (
                "expected_packet_sha256",
                "/Users/edr/private/digest-secret",
                self.charter_sha,
                "expected_packet_sha256_invalid",
            ),
            (
                "expected_charter_sha256",
                sha256(packet.read_bytes()),
                "/Users/edr/private/charter-digest-secret",
                "expected_charter_sha256_invalid",
            ),
        )
        for field, expected_packet, expected_charter, reason in digest_cases:
            supplied = (
                expected_packet
                if field == "expected_packet_sha256"
                else expected_charter
            )
            with self.subTest(field=field):
                completed = self.run_cli(
                    [
                        "--packet",
                        str(packet),
                        "--charter",
                        str(self.charter),
                        "--expected-packet-sha256",
                        expected_packet,
                        "--expected-charter-sha256",
                        expected_charter,
                    ]
                )
                receipt = json.loads(completed.stdout.decode("utf-8"))
                self.assert_refusal(completed, receipt, reason)
                self.assertIsNone(receipt[field])
                self.assertNotIn(supplied.encode("utf-8"), completed.stdout)

        private_packet = "/Users/edr/private/PACKET.md"
        private_charter = "/Users/edr/private/charter.md"
        cli_cases = (
            (
                "unknown_option",
                ["--unknown-option", "/Users/edr/private/secret"],
                "cli_invalid",
            ),
            (
                "missing_digest",
                [
                    "--packet",
                    private_packet,
                    "--charter",
                    private_charter,
                    "--expected-charter-sha256",
                    "0" * 64,
                ],
                "cli_invalid",
            ),
            (
                "unreadable_packet",
                [
                    "--packet",
                    private_packet,
                    "--charter",
                    private_charter,
                    "--expected-packet-sha256",
                    "0" * 64,
                    "--expected-charter-sha256",
                    "0" * 64,
                ],
                "packet_unreadable",
            ),
        )
        for name, arguments, reason in cli_cases:
            with self.subTest(name=name):
                completed = self.run_cli(arguments)
                receipt = json.loads(completed.stdout.decode("utf-8"))
                self.assert_refusal(completed, receipt, reason)
                for raw_value in (
                    b"/Users/edr/private/secret",
                    private_packet.encode("utf-8"),
                    private_charter.encode("utf-8"),
                ):
                    self.assertNotIn(raw_value, completed.stdout)

    def test_receipt_is_byte_deterministic(self) -> None:
        packet, _, _ = self.write_packet(pin=self.charter_sha)
        first, first_receipt = self.run_validator(packet)
        second, second_receipt = self.run_validator(packet)
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first_receipt["result"], "PASS")
        self.assertEqual(second_receipt["result"], "PASS")
        for receipt in (first_receipt, second_receipt):
            self.assertEqual(
                receipt["binding_scope"], "validation_time_observation_only"
            )
            self.assertIs(receipt["judge_handoff_bound"], False)


if __name__ == "__main__":
    unittest.main()
