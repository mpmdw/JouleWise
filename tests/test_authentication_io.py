from __future__ import annotations

import ast
import builtins
import hashlib
import shutil
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
    v2_authentication_path,
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
CLASSIFIED_NON_AUTHENTICATION_READS = {
    # Linux mountinfo describes OS filesystem topology, not project evidence.
    "joulewise/calibration_ledger.py:_filesystem_type:2842:read_text",
    # The lock sidecar descriptor is used for inode/lock state, never content.
    "joulewise/calibration_ledger.py:_open_slot_sidecar:2946:os.open",
    # O_RDWR descriptor factory for the writer lane; its read-consumers are
    # classified at their own sites (_locked_append writer-exempt;
    # repair/abandon below). This supersedes the earlier "append handle"
    # description, which its callers falsified.
    "joulewise/calibration_ledger.py:open_append_descriptor:3277:os.open",
    # The exclusive genesis staging descriptor receives newly written output.
    "joulewise/calibration_ledger.py:publish_genesis_payload:3222:os.open",
    # The parent dirfd binds a pathname slot and cannot supply evidence content.
    "joulewise/calibration_ledger.py:resolve_ledger_lease_identity:2894:os.open",
    # The ledger fd is fstat-only here to bind inode identity, not read bytes.
    "joulewise/calibration_ledger.py:resolve_ledger_lease_identity:2908:os.open",
    # Writer-lease repair scan of possibly-corrupt physical ledger bytes;
    # recovery/operator lane only (callers: governed exit paths
    # resume_finalize_bracket_session/abort_calibration_session,
    # scripts/recover_calibration_ledger.py, and
    # scripts/validate_powermetrics_fiducial.py), not reachable from the v2
    # mint evidence-read perimeter. Registration is inapplicable because the
    # bytes' integrity is the thing under repair.
    "joulewise/calibration_ledger.py:repair_calibration_ledger:3906:os.fdopen",
    # Writer-lease tail-abandonment scan of possibly-corrupt physical ledger
    # bytes; recovery/operator lane only (caller:
    # scripts/recover_calibration_ledger.py), not reachable from the v2 mint
    # evidence-read perimeter. Registration is inapplicable because the
    # bytes' integrity is the thing under repair.
    "joulewise/calibration_ledger.py:abandon_calibration_ledger_tail:3963:os.fdopen",
}
ISSUED_REDUCE_SHA256 = (
    "5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615"
)
ISSUED_REDUCE_DIRECT_READS = (
    "_derive_anchor_context:1780:read_bytes",
    "_verify_instrument_calibration:1229:read_bytes",
    "_verify_instrument_calibration:1252:read_bytes",
    "_verify_instrument_calibration:1295:read_bytes",
    "_verify_instrument_calibration:1472:read_bytes",
)


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

    def test_overflow_numbers_refuse_json_and_jsonl_but_finite_value_parses(self) -> None:
        cases = (
            ("overflow.json", b'{"x":1e999}'),
            ("overflow.jsonl", b'{"row":1}\n{"x":1e999}\n'),
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, raw in cases:
                with self.subTest(name=name):
                    path = root / name
                    path.write_bytes(raw)
                    grammar = "jsonl" if name.endswith(".jsonl") else "json"
                    with V2AuthenticationReadSession() as session:
                        with self.assertRaisesRegex(
                            V2AuthenticationInputError,
                            "non-finite JSON number '1e999'",
                        ):
                            read_authentication_input(
                                path, grammar=grammar, label=name
                            )
                        self.assertEqual(dict(session.records), {})

            finite = root / "finite.json"
            finite.write_bytes(b'{"x":1e308}')
            with V2AuthenticationReadSession() as session:
                self.assertEqual(
                    read_authentication_input(
                        finite, grammar="json", label="finite.json"
                    ),
                    b'{"x":1e308}',
                )
                self.assertTrue(
                    session.records[str(finite.resolve())].strict_parse_succeeded
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

    def test_path_capability_preserves_derivation_and_readable_operations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            nested = root / "nested"
            nested.mkdir()
            path = nested / "input.json"
            raw = b'{"value":1}\n'
            path.write_bytes(raw)
            self.assertIs(type(v2_authentication_path(root)), type(root))
            with V2AuthenticationReadSession() as session:
                capability = v2_authentication_path(root)
                derived = (capability / "nested" / "input.json").resolve()
                self.assertIs(type(derived), type(capability))
                self.assertIs(type(derived.parent), type(capability))
                self.assertEqual(derived.read_bytes(), raw)
                self.assertEqual(derived.read_text(), raw.decode("utf-8"))
                with derived.open("rb") as handle:
                    self.assertEqual(handle.read(), raw)
                record = session.records[str(path.resolve())]
                self.assertEqual(record.grammar, "json")
                self.assertEqual(record.read_count, 3)

    def test_issued_reducer_aba_read_refuses_transient_bytes(self) -> None:
        from joulewise.bundle_read import BundleReader
        from joulewise.reduce import _derive_anchor_context

        fixture = REPO_ROOT / "tests" / "fixtures" / "d078_r01"
        with tempfile.TemporaryDirectory() as temporary:
            bundle = Path(temporary) / "bundle"
            shutil.copytree(fixture, bundle)
            raw_path = bundle / "raw" / "powermetrics.plist"
            authentic = raw_path.read_bytes()
            transient = authentic.replace(b"2026-", b"2025-", 1)
            self.assertNotEqual(transient, authentic)
            reader = BundleReader(bundle)
            metadata = reader.metadata()
            with V2AuthenticationReadSession() as session:
                # The boundary sees A, just as the rejected pre-hash design did.
                read_authentication_input(raw_path, grammar="raw", label="boundary A")
                raw_path.write_bytes(transient)
                try:
                    with self.assertRaisesRegex(
                        V2AuthenticationInputError,
                        V2_AUTHENTICATION_INPUT_CHANGED,
                    ):
                        _derive_anchor_context(
                            reader,
                            metadata,
                            reducer_version="0.5.2",
                        )
                finally:
                    # Restore A before the hypothetical post-return boundary.
                    raw_path.write_bytes(authentic)
                self.assertEqual(raw_path.read_bytes(), authentic)
                self.assertEqual(
                    session.records[str(raw_path.resolve())].read_count,
                    1,
                )


class AuthenticationSurfaceGuardTests(unittest.TestCase):
    def test_issued_reducer_sha_and_five_direct_reads_are_characterized(self) -> None:
        path = REPO_ROOT / "joulewise" / "reduce.py"
        raw = path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), ISSUED_REDUCE_SHA256)
        self.assertEqual(
            direct_read_violations(
                raw.decode("utf-8"),
                marked_functions={
                    "_verify_instrument_calibration",
                    "_derive_anchor_context",
                },
            ),
            ISSUED_REDUCE_DIRECT_READS,
        )

    def test_marked_v2_surface_has_no_direct_readable_io(self) -> None:
        violations: list[str] = []
        classified_non_authentication_reads: set[str] = set()
        for relative in AUTHENTICATION_SURFACE:
            source = (REPO_ROOT / relative).read_text(encoding="utf-8")
            tree = ast.parse(source)
            names = {
                node.name
                for node in ast.walk(tree)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            } - NON_AUTHENTICATION_WRITERS
            direct = direct_read_violations(source, marked_functions=names)
            source_sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()
            if (relative, source_sha256) == (
                "joulewise/reduce.py",
                ISSUED_REDUCE_SHA256,
            ):
                self.assertEqual(direct, ISSUED_REDUCE_DIRECT_READS)
                continue
            for item in direct:
                finding = f"{relative}:{item}"
                if finding in CLASSIFIED_NON_AUTHENTICATION_READS:
                    classified_non_authentication_reads.add(finding)
                else:
                    violations.append(finding)
        self.assertEqual(violations, [])
        self.assertEqual(
            classified_non_authentication_reads,
            CLASSIFIED_NON_AUTHENTICATION_READS,
        )

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

    def test_guard_detects_readable_fdopen_and_ignores_write_only_fdopen(self) -> None:
        source = """
import os
def authenticate(fd):
    os.fdopen(fd, "r+b")
    os.fdopen(fd, "rb")
    os.fdopen(fd, "wb")
"""
        self.assertEqual(
            direct_read_violations(source, marked_functions={"authenticate"}),
            (
                "authenticate:4:os.fdopen",
                "authenticate:5:os.fdopen",
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
