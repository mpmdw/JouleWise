from __future__ import annotations

import ast
import builtins
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.authentication_io import (
    V2_AUTHENTICATION_INPUT_CHANGED,
    V2AuthenticationInputError,
    V2AuthenticationReadSession,
    direct_read_violations,
    ingest_git_authentication_input,
    read_authentication_input,
    read_authentication_input_nofollow,
    sha256_authentication_input,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
AUTHENTICATION_SURFACE = (
    "scripts/mint_floor_artifact_generalized.py",
    "scripts/mint_floor_artifact.py",
    "joulewise/calibration_ledger.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/whole_window.py",
    "joulewise/campaign_provenance.py",
    "joulewise/analysis_engine/registry.py",
    "joulewise/bundle_read.py",
    "joulewise/cli.py",
    "joulewise/reduce.py",
    "joulewise/environment_admission.py",
    "joulewise/detection_floor.py",
    "joulewise/salvage_dangler.py",
)
NON_AUTHENTICATION_WRITERS = {
    "_fsync_parent_directory",
    "_locked_append",
    "_open_ledger_lock",
    "bootstrap_historical_import",
}


class V2AuthenticationReadSessionTests(unittest.TestCase):
    def test_registration_is_complete_before_bytes_are_returned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.json"
            raw = b'{"value":1}\n'
            path.write_bytes(raw)
            with V2AuthenticationReadSession() as session:
                self.assertEqual(
                    read_authentication_input(
                        path, grammar="json", label="atomic registration"
                    ),
                    raw,
                )
                record = session.records[str(path.resolve())]
                self.assertEqual(record.sha256, hashlib.sha256(raw).hexdigest())
                self.assertEqual(record.grammar, "json")
                self.assertEqual(record.read_count, 1)
                self.assertTrue(record.strict_parse_succeeded)

                self.assertEqual(
                    read_authentication_input(
                        path, grammar="json", label="atomic registration reread"
                    ),
                    raw,
                )
                self.assertEqual(
                    session.records[str(path.resolve())].read_count,
                    2,
                )

    def test_failed_strict_parse_never_registers_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "duplicate.json"
            path.write_bytes(b'{"value":1,"value":2}\n')
            with V2AuthenticationReadSession() as session:
                with self.assertRaisesRegex(
                    V2AuthenticationInputError, "duplicate JSON key"
                ):
                    read_authentication_input(
                        path, grammar="json", label="duplicate object"
                    )
                self.assertEqual(dict(session.records), {})

    def test_duplicate_keys_and_nonfinite_numbers_refuse_json_and_jsonl(self) -> None:
        cases = (
            ("duplicate.json", b'{"x":1,"x":2}', "duplicate JSON key"),
            ("nonfinite.json", b'{"x":NaN}', "non-finite JSON number"),
            (
                "duplicate.jsonl",
                b'{"row":1}\n{"x":1,"x":2}\n',
                "duplicate JSON key",
            ),
            (
                "nonfinite.jsonl",
                b'{"row":1}\n{"x":Infinity}\n',
                "non-finite JSON number",
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, raw, message in cases:
                with self.subTest(name=name):
                    path = root / name
                    path.write_bytes(raw)
                    grammar = "jsonl" if name.endswith(".jsonl") else "json"
                    with V2AuthenticationReadSession():
                        with self.assertRaisesRegex(
                            V2AuthenticationInputError, message
                        ):
                            read_authentication_input(
                                path, grammar=grammar, label=name
                            )

    def test_json_suffix_cannot_be_downgraded_to_raw(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.json"
            path.write_bytes(b'{"x":1,"x":2}')
            with V2AuthenticationReadSession():
                with self.assertRaisesRegex(
                    V2AuthenticationInputError, "duplicate JSON key"
                ):
                    read_authentication_input(
                        path, grammar="raw", label="raw downgrade"
                    )

    def test_repeated_read_detects_toctou_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "input.json"
            path.write_bytes(b'{"value":1}\n')
            with V2AuthenticationReadSession() as session:
                read_authentication_input(path, grammar="json", label="first")
                path.write_bytes(b'{"value":2}\n')
                with self.assertRaisesRegex(
                    V2AuthenticationInputError,
                    V2_AUTHENTICATION_INPUT_CHANGED,
                ):
                    read_authentication_input(path, grammar="json", label="second")
                self.assertEqual(
                    session.records[str(path.resolve())].read_count,
                    1,
                )

    def test_raw_stream_and_git_blob_use_the_same_registry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "trace.plist"
            raw = b"raw\x00evidence" * 128
            path.write_bytes(raw)
            git_raw = b'{"sequence":76,"head_digest":"' + b"0" * 64 + b'"}\n'
            with V2AuthenticationReadSession() as session:
                self.assertEqual(
                    sha256_authentication_input(path, label="large raw trace"),
                    hashlib.sha256(raw).hexdigest(),
                )
                self.assertEqual(
                    ingest_git_authentication_input(
                        "runs/calibration_observation_ledger.head.json",
                        git_raw,
                        grammar="json",
                        label="committed head pin",
                    ),
                    git_raw,
                )
                raw_record = session.records[str(path.resolve())]
                self.assertEqual(raw_record.grammar, "raw")
                self.assertFalse(raw_record.strict_parse_succeeded)
                git_record = session.records[
                    "git:HEAD:runs/calibration_observation_ledger.head.json"
                ]
                self.assertEqual(git_record.grammar, "json")
                self.assertTrue(git_record.strict_parse_succeeded)

    def test_nofollow_reader_registers_contained_input(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "nested" / "input.json"
            path.parent.mkdir()
            raw = b'{"value":1}\n'
            path.write_bytes(raw)
            with V2AuthenticationReadSession() as session:
                self.assertEqual(
                    read_authentication_input_nofollow(
                        root,
                        "nested/input.json",
                        grammar="json",
                        label="contained input",
                    ),
                    raw,
                )
                self.assertIn(str(path.resolve()), session.records)

    def test_inactive_wrapper_preserves_historical_non_strict_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "legacy.json"
            raw = b'{"value":1,"value":2}'
            path.write_bytes(raw)
            self.assertEqual(
                read_authentication_input(path, grammar="json", label="legacy"),
                raw,
            )


class AuthenticationSurfaceGuardTests(unittest.TestCase):
    def test_marked_v2_surface_has_no_direct_readable_io(self) -> None:
        violations: list[str] = []
        for relative in AUTHENTICATION_SURFACE:
            source = (REPO_ROOT / relative).read_text(encoding="utf-8")
            tree = ast.parse(source)
            names = {
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            } - NON_AUTHENTICATION_WRITERS
            violations.extend(
                f"{relative}:{item}"
                for item in direct_read_violations(
                    source,
                    marked_functions=names,
                )
            )
        self.assertEqual(violations, [])

    def test_guard_distinguishes_readable_and_output_only_open(self) -> None:
        source = """
import os
def authenticate():
    open('input.json')
    open('output.json', 'wb')
    os.open('input.bin', os.O_RDONLY)
    os.open('output.bin', os.O_WRONLY | os.O_CREAT)
"""
        self.assertEqual(
            direct_read_violations(source, marked_functions={"authenticate"}),
            (
                "authenticate:4:open",
                "authenticate:6:os.open",
            ),
        )

    def test_low_level_open_auditor_matches_registered_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            paths = {
                root / "policy.json": b'{"policy":"fixture"}\n',
                root / "attempts.jsonl": b'{"attempt":1}\n',
                root / "trace.csv": b"time,power\n0,1\n",
            }
            for path, raw in paths.items():
                path.write_bytes(raw)

            opened: set[str] = set()
            original_open = builtins.open

            def audited_open(file, mode="r", *args, **kwargs):
                candidate = Path(file).resolve(strict=False)
                if ("r" in mode or "+" in mode) and (
                    candidate == root or root in candidate.parents
                ):
                    opened.add(str(candidate))
                return original_open(file, mode, *args, **kwargs)

            with mock.patch("builtins.open", side_effect=audited_open):
                with V2AuthenticationReadSession() as session:
                    read_authentication_input(
                        root / "policy.json", grammar="json", label="policy"
                    )
                    read_authentication_input(
                        root / "attempts.jsonl", grammar="jsonl", label="attempts"
                    )
                    read_authentication_input(
                        root / "trace.csv", grammar="raw", label="trace"
                    )
                    registered = {
                        identity
                        for identity in session.records
                        if not identity.startswith("git:")
                    }
            self.assertEqual(opened, registered)


if __name__ == "__main__":
    unittest.main()
