from __future__ import annotations

import copy
import importlib.util
import hashlib
import io
import json
import os
import shutil
import shlex
import subprocess
import sys
import tempfile
import textwrap
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

from scripts.run_campaign import (
    ShakedownGateError,
    execute_production_uncertainty_gate,
    failed_shakedown_record,
)
from joulewise.authentication_io import V2AuthenticationReadSession
from joulewise.calibration_ledger import (
    CUSTODY_STORE_MANIFEST_NAME,
    GENESIS_DIGEST,
    GOVERNED_ARTIFACTS,
    LEDGER_SCHEMA,
    append_pending_receipt,
    artifact_hashes,
    calibration_custody_store_manifest_bytes,
    finalize_attempt_receipt,
    head_pin_for_receipt,
    load_calibration_ledger_snapshot,
)
from joulewise.environment import evaluate_environment_policy
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from joulewise.uncertainty_evidence import (
    ACTIVE_CAPTURE_ANCHOR_METHOD,
    SCHEMA_FOR_ANCHOR_METHOD,
)
from joulewise.calibration_bracketing import discover_calibration_candidates
from joulewise import whole_window as whole_window_module
from joulewise.whole_window import (
    MINTED_CONSUMPTION_SEMANTICS_ID,
    NEG8_DRIFT_BOUND_MAX_AGE_S,
    canonical_sha256,
)
from tests.test_calibration_bracketing import (
    _fixture_snapshot,
    _unissued_acceptance_fixture,
)
from tests.test_arm_readiness import LaunchConsumptionV2Tests


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_campaign.py"
BASE_CONFIG = ROOT / "configs" / "examples" / "mock_local.json"
SUITE_CONFIG = ROOT / "configs" / "examples" / "mock_suite_local.json"
COMMAND_TIMEOUT_S = 60
GENERATOR = ROOT / "scripts" / "generate_matrix.py"
TEST_CAMPAIGN_POLICY = ROOT / "tests" / "fixtures" / "campaign_policy_test.json"
REAL_CAMPAIGN_LOGS = (
    Path("/Users/edr/code/JouleWise/runs_window_contrast_20260730/campaign_log.jsonl"),
    Path("/Users/edr/code/JouleWise/runs/p2_015_floors_window_a/campaign_log.jsonl"),
)

spec = importlib.util.spec_from_file_location("run_campaign_module", SCRIPT)
run_campaign_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["run_campaign_module"] = run_campaign_module
spec.loader.exec_module(run_campaign_module)


def campaign_lock_path(token) -> Path:
    """Return the lock path for both legacy path and identity-object tokens."""

    return Path(getattr(token, "lock_path", token))


@contextmanager
def held_campaign_lock(runs_dir: Path):
    lock_path = run_campaign_module.acquire_campaign_lock(runs_dir)
    try:
        yield lock_path
    except BaseException as exc:
        run_campaign_module.release_campaign_lock(lock_path, in_flight=exc)
        raise
    else:
        run_campaign_module.release_campaign_lock(lock_path)


class CampaignLaunchLineagePreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.config_dir = self.root / "configs"
        self.config_dir.mkdir()
        self.runs_dir = self.root / "runs"

    def _write_config(self, name: str, *, marker: bool) -> Path:
        tags = ["launch_lineage_required"] if marker else []
        path = self.config_dir / name
        path.write_text(
            json.dumps(
                {
                    "run_id": path.stem,
                    "run_metadata": {"project": "joulewise", "tags": tags},
                }
            )
            + "\n"
        )
        return path

    def test_outer_preflight_derives_from_runs_root_and_exact_configs(self) -> None:
        first = self._write_config("first.json", marker=True)
        second = self._write_config("second.json", marker=True)
        expected = {"launch_lineage": {"schema_version": "test"}}
        with patch.object(
            run_campaign_module,
            "authenticate_campaign_launch_lineage",
            return_value=expected,
        ) as authenticate:
            actual = run_campaign_module.authenticate_campaign_writer_preflight(
                [first, second], self.runs_dir
            )
        self.assertIs(actual, expected)
        authenticate.assert_called_once_with(
            self.runs_dir, config_paths=[first, second]
        )

    def test_outer_preflight_refuses_mixed_marker_selection(self) -> None:
        marked = self._write_config("marked.json", marker=True)
        legacy = self._write_config("legacy.json", marker=False)
        with self.assertRaises(run_campaign_module.LaunchLineageError) as caught:
            run_campaign_module.authenticate_campaign_writer_preflight(
                [marked, legacy], self.runs_dir
            )
        self.assertEqual(caught.exception.reason_code, "launch_binding_mismatch")

    def test_ceremony_bypass_refuses_before_lock_provenance_or_child(self) -> None:
        self._write_config("member.json", marker=True)
        self.runs_dir.mkdir()
        args = run_campaign_module.parse_args(
            [
                str(self.config_dir),
                "--runs-dir",
                str(self.runs_dir),
                "--campaign-policy",
                str(TEST_CAMPAIGN_POLICY),
            ]
        )
        with patch.object(
            run_campaign_module, "acquire_campaign_lock"
        ) as acquire, patch.object(
            run_campaign_module, "new_campaign_provenance"
        ) as provenance, patch.object(
            run_campaign_module.subprocess, "run"
        ) as child:
            with self.assertRaises(run_campaign_module.LaunchLineageError) as caught:
                run_campaign_module.run_campaign(args)
        self.assertEqual(
            caught.exception.reason_code, "launch_consumption_missing"
        )
        acquire.assert_not_called()
        provenance.assert_not_called()
        child.assert_not_called()

    def test_consistent_locator_swap_after_outer_preflight_refuses(self) -> None:
        first = LaunchConsumptionV2Tests(
            methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
        )
        first.setUp()
        try:
            first._settle()
            first_root = Path(first.arm["arm_context"]["claim_runs_root"])
            selector = self.root / "selected-runs"
            selector.symlink_to(first_root, target_is_directory=True)
            outer = first._authenticate_campaign(selector)

            second = LaunchConsumptionV2Tests(
                methodName="test_v2_claim_is_fsynced_and_replays_from_consumption"
            )
            second.setUp()
            try:
                second._settle()
                second_root = Path(second.arm["arm_context"]["claim_runs_root"])
                bundle = selector / "child-bundle"

                def swap_and_stamp(command, **_kwargs):
                    selector.unlink()
                    selector.symlink_to(second_root, target_is_directory=True)
                    inner = second._authenticate_campaign(selector)
                    bundle.mkdir()
                    (bundle / "metadata.json").write_text(
                        json.dumps(
                            {
                                "extra": {
                                    "launch_lineage": inner["launch_lineage"],
                                    "launch_lineage_locator_sha256": inner[
                                        "locator_sha256"
                                    ],
                                }
                            }
                        )
                        + "\n"
                    )
                    return subprocess.CompletedProcess(command, 0)

                with patch.object(
                    run_campaign_module.subprocess,
                    "run",
                    side_effect=swap_and_stamp,
                ):
                    with self.assertRaises(
                        run_campaign_module.LaunchLineageError
                    ) as caught:
                        run_campaign_module.run_authenticated_campaign_child(
                            ["child"],
                            env=None,
                            outer_authentication=outer,
                            bundle_paths=[bundle],
                        )
                self.assertEqual(
                    caught.exception.reason_code, "launch_lineage_conflict"
                )
            finally:
                second.doCleanups()
        finally:
            first.doCleanups()


class CampaignLockIdentityTests(unittest.TestCase):
    def test_r1_foreign_same_named_lock_with_matching_pid_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            owner_root = root / "owner"
            foreign_root = root / "foreign"
            foreign_root.mkdir()
            token = run_campaign_module.acquire_campaign_lock(owner_root)
            try:
                foreign_token = foreign_root / "campaign.lock"
                foreign_token.write_bytes(campaign_lock_path(token).read_bytes())
                with self.assertRaisesRegex(RuntimeError, "acquired by this process"):
                    run_campaign_module._assert_campaign_lock_token(foreign_token)
            finally:
                run_campaign_module.release_campaign_lock(token)

    def test_r2_stale_pid_reuse_without_acquisition_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "campaign.lock").write_text(
                f"pid={os.getpid()} nonce=stale created_at=old\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "acquired by this process"):
                run_campaign_module._assert_campaign_lock_held(root)
            self.assertNotIn(
                (root / "campaign.lock").resolve(),
                run_campaign_module._CAMPAIGN_LOCK_OWNERSHIP,
            )

    def test_r3_out_of_band_unlink_recreate_refuses_on_inode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token = run_campaign_module.acquire_campaign_lock(root)
            token_path = campaign_lock_path(token)
            acquired_content = token_path.read_bytes()
            acquired_identity = (token_path.stat().st_dev, token_path.stat().st_ino)
            replacement = root / "replacement.lock"
            replacement.write_bytes(acquired_content)
            replacement_identity = (
                replacement.stat().st_dev,
                replacement.stat().st_ino,
            )
            self.assertNotEqual(replacement_identity, acquired_identity)
            token_path.unlink()
            os.replace(replacement, token_path)
            try:
                with self.assertRaisesRegex(RuntimeError, "acquisition identity"):
                    run_campaign_module._assert_campaign_lock_token(token)
            finally:
                run_campaign_module.release_campaign_lock(token)
            self.assertTrue(
                token_path.is_file(), "release must preserve a replacement inode"
            )

    def test_lock_nonce_tamper_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            token = run_campaign_module.acquire_campaign_lock(Path(tmp))
            token_path = campaign_lock_path(token)
            try:
                fields = token_path.read_text(encoding="utf-8").split()
                fields[1] = "nonce=forged"
                token_path.write_text(" ".join(fields) + "\n", encoding="utf-8")
                with self.assertRaisesRegex(RuntimeError, "acquisition identity"):
                    run_campaign_module._assert_campaign_lock_token(token)
            finally:
                run_campaign_module.release_campaign_lock(token)

    def test_r4_cross_root_append_into_lockable_root_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            owner_root = root / "owner"
            foreign_root = root / "foreign"
            foreign_root.mkdir()
            foreign_log = foreign_root / "campaign_log.jsonl"
            before = b'{"existing": true}\n'
            foreign_log.write_bytes(before)
            (foreign_root / "campaign.lock").write_text(
                f"pid={os.getpid()} nonce=foreign created_at=now\n",
                encoding="utf-8",
            )
            with held_campaign_lock(owner_root) as token:
                with self.assertRaisesRegex(RuntimeError, "foreign lock token"):
                    run_campaign_module.append_log(
                        foreign_log, {"new": True}, lock_token=token
                    )
            self.assertEqual(foreign_log.read_bytes(), before)

    def test_r5_owned_root_and_external_unlocked_log_are_legal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_root = root / "runs"
            external_log = root / "external" / "campaign.jsonl"
            with held_campaign_lock(runs_root) as token:
                run_campaign_module.append_log(
                    runs_root / "campaign_log.jsonl",
                    {"target": "owned"},
                    lock_token=token,
                )
                run_campaign_module.append_log(
                    external_log,
                    {"target": "external"},
                    lock_token=token,
                )
            self.assertEqual(
                read_wire_jsonl(runs_root / "campaign_log.jsonl"),
                [{"target": "owned"}],
            )
            self.assertEqual(
                read_wire_jsonl(external_log),
                [{"target": "external"}],
            )
            self.assertFalse((external_log.parent / "campaign.lock").exists())

    def test_r6_post_release_token_refuses_even_if_content_returns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token = run_campaign_module.acquire_campaign_lock(root)
            token_path = campaign_lock_path(token)
            acquired_content = token_path.read_bytes()
            run_campaign_module.release_campaign_lock(token)
            token_path.write_bytes(acquired_content)
            before = b'{"existing": true}\n'
            log_path = root / "campaign_log.jsonl"
            log_path.write_bytes(before)
            with self.assertRaisesRegex(RuntimeError, "acquired by this process"):
                run_campaign_module.append_log(
                    log_path, {"new": True}, lock_token=token
                )
            self.assertEqual(log_path.read_bytes(), before)
            run_campaign_module.release_campaign_lock(token)

    def test_b1_release_reacquire_stale_token_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stale = run_campaign_module.acquire_campaign_lock(root)
            run_campaign_module.release_campaign_lock(stale)
            current = run_campaign_module.acquire_campaign_lock(root)
            try:
                self.assertIsNot(stale, current)
                with self.assertRaisesRegex(RuntimeError, "acquired by this process"):
                    run_campaign_module._assert_campaign_lock_token(stale)
                run_campaign_module.release_campaign_lock(stale)
                self.assertIs(
                    run_campaign_module._assert_campaign_lock_token(current),
                    current,
                )
            finally:
                run_campaign_module.release_campaign_lock(current)

    def test_s1_identity_and_nonce_are_read_from_one_descriptor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token = run_campaign_module.acquire_campaign_lock(root)
            token_path = campaign_lock_path(token)
            replacement = root / "replacement.lock"
            replacement.write_bytes(token_path.read_bytes())
            self.assertNotEqual(
                (replacement.stat().st_dev, replacement.stat().st_ino),
                (token_path.stat().st_dev, token_path.stat().st_ino),
            )
            replaced = False
            real_os_open = run_campaign_module.os.open
            real_read_text = Path.read_text

            def replace_lock_once() -> None:
                nonlocal replaced
                if replaced:
                    return
                replaced = True
                token_path.unlink()
                os.replace(replacement, token_path)

            def replacing_os_open(path, flags, *args, **kwargs):
                if Path(path) == token_path and flags == os.O_RDONLY:
                    replace_lock_once()
                return real_os_open(path, flags, *args, **kwargs)

            def replacing_read_text(path, *args, **kwargs):
                if Path(path) == token_path:
                    replace_lock_once()
                return real_read_text(path, *args, **kwargs)

            try:
                with patch.object(
                    run_campaign_module.os, "open", side_effect=replacing_os_open
                ), patch.object(Path, "read_text", replacing_read_text):
                    with self.assertRaisesRegex(
                        RuntimeError, "acquisition identity"
                    ):
                        run_campaign_module._assert_campaign_lock_token(token)
            finally:
                run_campaign_module.release_campaign_lock(token)
            self.assertTrue(replaced)

    def test_s2_registry_install_failure_removes_lock_file(self) -> None:
        class FailingRegistry(dict):
            def __setitem__(self, key, value):
                raise MemoryError("injected registry install failure")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            lock_path = root.resolve() / "campaign.lock"
            registry = FailingRegistry(run_campaign_module._CAMPAIGN_LOCK_OWNERSHIP)
            with patch.object(
                run_campaign_module, "_CAMPAIGN_LOCK_OWNERSHIP", registry
            ):
                with self.assertRaisesRegex(MemoryError, "registry install failure"):
                    run_campaign_module.acquire_campaign_lock(root)
                self.assertFalse(lock_path.exists())
                self.assertNotIn(lock_path, registry)

    def test_s2_unlink_failure_retains_registry_and_chains_body_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token = run_campaign_module.acquire_campaign_lock(root)
            token_path = campaign_lock_path(token)
            original = RuntimeError("injected body failure")
            real_unlink = Path.unlink

            def refusing_unlink(path, *args, **kwargs):
                if Path(path) == token_path:
                    raise PermissionError("injected unlink failure")
                return real_unlink(path, *args, **kwargs)

            caught = None
            with patch.object(Path, "unlink", refusing_unlink):
                try:
                    raise original
                except RuntimeError as exc:
                    try:
                        run_campaign_module.release_campaign_lock(
                            token, in_flight=exc
                        )
                    except RuntimeError as chained:
                        caught = chained
            self.assertIs(caught, original)
            self.assertIsInstance(caught.__cause__, PermissionError)
            self.assertIs(
                run_campaign_module._CAMPAIGN_LOCK_OWNERSHIP.get(token_path),
                token,
            )
            self.assertTrue(token_path.exists())
            run_campaign_module.release_campaign_lock(token)
            self.assertFalse(token_path.exists())

    def test_f3_stat_failure_retains_registry_and_chains_body_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            token = run_campaign_module.acquire_campaign_lock(root)
            token_path = campaign_lock_path(token)
            original = RuntimeError("injected body failure")
            caught = None
            with patch.object(
                run_campaign_module.os,
                "stat",
                side_effect=PermissionError("injected stat failure"),
            ):
                try:
                    raise original
                except RuntimeError as exc:
                    try:
                        run_campaign_module.release_campaign_lock(
                            token, in_flight=exc
                        )
                    except RuntimeError as chained:
                        caught = chained
            self.assertIs(caught, original)
            self.assertIsInstance(caught.__cause__, PermissionError)
            self.assertIs(
                run_campaign_module._CAMPAIGN_LOCK_OWNERSHIP.get(token_path),
                token,
            )
            self.assertTrue(token_path.exists())
            run_campaign_module.release_campaign_lock(token)

    def test_sf1_failure_immediately_after_acquisition_releases_lock(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_root = root / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            args = run_campaign_module.parse_args(
                [
                    str(config_dir),
                    "--runs-dir",
                    str(runs_root),
                    "--campaign-policy",
                    str(TEST_CAMPAIGN_POLICY),
                ]
            )
            with patch.object(
                run_campaign_module,
                "new_campaign_provenance",
                side_effect=OSError("injected post-acquire failure"),
            ):
                with self.assertRaisesRegex(OSError, "post-acquire failure"):
                    run_campaign_module.run_campaign(args)
            lock_path = runs_root.resolve() / "campaign.lock"
            self.assertFalse(lock_path.exists())
            self.assertNotIn(
                lock_path,
                run_campaign_module._CAMPAIGN_LOCK_OWNERSHIP,
            )


class CampaignLogTailGrammarTests(unittest.TestCase):
    @staticmethod
    def _parse(raw: bytes):
        from joulewise.campaign_provenance import parse_campaign_log_bytes

        return parse_campaign_log_bytes(raw)

    def test_r7_every_nonempty_proper_prefix_of_writer_rows_is_tolerable(self) -> None:
        corpus = (
            {},
            {
                "array": [1, -2, None, True, False],
                "nested": {"inner": ["ascii", {"leaf": 7}]},
            },
            {
                "escaped": (
                    "snowman=☃ emoji=😀 quote=\" slash=\\ line=\n "
                    "nul=\x00 del=\x7f"
                ),
                "float": 1e-05,
                "integer": 123456789,
                "nothing": None,
                "truth": True,
                "falsehood": False,
            },
            {
                "negative_zero": -0.0,
                "nan": float("nan"),
                "positive_infinity": float("inf"),
                "negative_infinity": -float("inf"),
            },
        )
        for row in corpus:
            wire = json.dumps(row, sort_keys=True).encode("ascii")
            for boundary in range(1, len(wire)):
                with self.subTest(row=wire, boundary=boundary):
                    self.assertEqual(
                        self._parse(wire[:boundary]),
                        ([], "torn_prefix"),
                    )

    @unittest.skipUnless(
        all(path.is_file() for path in REAL_CAMPAIGN_LOGS),
        "real campaign-log corpus is unavailable",
    )
    def test_r7_real_campaign_log_writer_rows_are_complete(self) -> None:
        for log_path in REAL_CAMPAIGN_LOGS:
            lines = log_path.read_bytes().splitlines()
            windows = (
                range(0, min(5, len(lines))),
                range(max(0, len(lines) // 2 - 2), min(len(lines), len(lines) // 2 + 3)),
                range(max(0, len(lines) - 5), len(lines)),
            )
            sample_indexes = [
                min(window, key=lambda index: (len(lines[index]), index))
                for window in windows
            ]
            for row_index in sample_indexes:
                wire = lines[row_index]
                self.assertIsInstance(json.loads(wire), dict)
                for boundary in range(1, len(wire)):
                    with self.subTest(
                        log=log_path.name,
                        row_index=row_index,
                        boundary=boundary,
                    ):
                        self.assertEqual(
                            self._parse(wire[:boundary]),
                            ([], "torn_prefix"),
                        )

    def test_r7_non_bmp_key_prefix_known_f1_exact_set(self) -> None:
        """C3-RECOGNIZER-EXACT-01: the high-surrogate key tear (registered
        blocker F1) is pinned as an EXACT misclassification set — every
        misclassified boundary must fall inside the known surrogate-pair
        escape span, and every boundary outside it must classify
        correctly, so ANY second regression is a hard failure while the
        registered blocker stays documented. When the row closes and F1
        is fixed, the non-empty assertion below fails deliberately:
        update this pin to full correctness at closure."""

        wire = json.dumps({"\ue000": 1, "😀": 2}, sort_keys=True).encode("ascii")
        # The EXACT boundary set misclassified by registered blocker F1,
        # frozen literally (boundaries torn inside the high-surrogate
        # escape's hex digits and the following low-surrogate prefix).
        # ANY deviation is a hard failure: an addition anywhere is a new
        # recognizer regression; a removal means F1 was (partly) fixed —
        # close C3-RECOGNIZER-EXACT-01 and update this pin to the full
        # correctness property.
        known_f1_misclassified = {21, 22, 23, 24, 25, 26}
        misclassified = {
            boundary
            for boundary in range(1, len(wire))
            if self._parse(wire[:boundary]) != ([], "torn_prefix")
        }
        self.assertEqual(
            misclassified,
            known_f1_misclassified,
            "recognizer misclassification set changed: additions are NEW "
            "regressions; removals mean registered blocker F1 was fixed — "
            "close C3-RECOGNIZER-EXACT-01 and update this pin",
        )

    def test_r7_named_prefix_pins(self) -> None:
        for name, prefix in (
            ("exponent", b'{"a": 1e'),
            ("object_key", b'{"a'),
            ("literal", b'{"a": tru'),
        ):
            with self.subTest(name=name):
                self.assertEqual(self._parse(prefix), ([], "torn_prefix"))

    def test_b2_out_of_order_duplicate_and_decoded_torn_keys_refuse(self) -> None:
        for name, segment in (
            ("out_of_order", b'{"b": 1, "a'),
            ("duplicate", b'{"a": 1, "a"'),
            ("decoded_out_of_order", b'{"\\u2603": 1, "\\u00e9'),
        ):
            with self.subTest(name=name):
                self.assertEqual(self._parse(segment), (None, "invalid"))

    def test_b2_number_grammar_round_trips_writer_forms_byte_exactly(self) -> None:
        for name, value, literal in (
            ("nan", float("nan"), b"NaN"),
            ("positive_infinity", float("inf"), b"Infinity"),
            ("negative_infinity", -float("inf"), b"-Infinity"),
        ):
            with self.subTest(name=name):
                special_segment = json.dumps(
                    {"a": value}, sort_keys=True
                ).encode("ascii")
                self.assertIn(literal, special_segment)
                parsed, final_segment = self._parse(special_segment)
                self.assertEqual(final_segment, "mapping")
                assert parsed is not None
                self.assertEqual(
                    json.dumps(parsed[0], sort_keys=True).encode("ascii"),
                    special_segment,
                )

        self.assertEqual(self._parse(b'{"a": -0'), ([], "torn_prefix"))
        row = {"a": -0.0}
        segment = json.dumps(row, sort_keys=True).encode("ascii")
        parsed, final_segment = self._parse(segment)
        self.assertEqual(final_segment, "mapping")
        assert parsed is not None
        self.assertEqual(
            json.dumps(parsed[0], sort_keys=True).encode("ascii"), segment
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "campaign_log.jsonl"
            log_path.write_bytes(segment)
            with held_campaign_lock(root) as token:
                run_campaign_module.append_log(
                    log_path, {"next": 1}, lock_token=token
                )
            self.assertEqual(
                log_path.read_bytes(),
                segment
                + b"\n"
                + json.dumps({"next": 1}, sort_keys=True).encode("ascii")
                + b"\n",
            )

    def test_r8_complete_row_missing_lf_is_preserved_byte_exactly(self) -> None:
        from joulewise import campaign_provenance

        row = {"escaped": "☃\n", "nested": [1e-05, None, True, False]}
        segment = json.dumps(row, sort_keys=True).encode("ascii")
        with patch.object(
            campaign_provenance.json,
            "loads",
            wraps=json.loads,
        ) as loads_mock:
            self.assertEqual(self._parse(segment), ([row], "mapping"))
        self.assertEqual(loads_mock.call_count, 1)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "campaign_log.jsonl"
            log_path.write_bytes(segment)
            with held_campaign_lock(root) as token:
                run_campaign_module.append_log(
                    log_path, {"next": 1}, lock_token=token
                )
            self.assertEqual(
                log_path.read_bytes(),
                segment + b"\n" + json.dumps({"next": 1}, sort_keys=True).encode()
                + b"\n",
            )

    def test_r9_refusal_table_is_global_and_append_touches_nothing(self) -> None:
        refusals = (
            ("complete_then_junk", b'{"a":1}x'),
            ("two_objects", b'{"a":1}{'),
            ("trailing_space", b'{"a":1} '),
            ("trailing_tab", b'{"a":1}\t'),
            ("double_comma", b'{"a":1,,'),
            ("missing_colon", b'{"a"}'),
            ("garbage", b"garbage"),
            ("scalar_exponent", b"1e"),
            ("array", b"[1, 2"),
            ("non_ascii", b"\xff"),
            ("leading_zero_exponent", b'{"a": 1e+000'),
            ("raw_del", b'{"a": "\x7f'),
            ("whitespace_only", b" \t"),
            ("noncanonical_key_separator", b'{"a" : 1'),
        )
        prior = json.dumps({"prior": True}, sort_keys=True).encode() + b"\n"
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp)
            for index, (name, tail) in enumerate(refusals):
                with self.subTest(name=name):
                    root = parent / str(index)
                    root.mkdir()
                    log_path = root / "campaign_log.jsonl"
                    before = prior + tail
                    log_path.write_bytes(before)
                    self.assertEqual(self._parse(before), (None, "invalid"))
                    with held_campaign_lock(root) as token:
                        with self.assertRaisesRegex(
                            ValueError, "non-final corruption"
                        ):
                            run_campaign_module.append_log(
                                log_path, {"new": True}, lock_token=token
                            )
                    self.assertEqual(log_path.read_bytes(), before)

    def test_r10_torn_prefix_truncation_boundary_is_exact(self) -> None:
        first = json.dumps({"first": 1}, sort_keys=True).encode() + b"\n"
        torn = b'{"nested": [1, {"value": 1e'
        appended = {"after": "tear"}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "campaign_log.jsonl"
            log_path.write_bytes(first + torn)
            with held_campaign_lock(root) as token:
                run_campaign_module.append_log(
                    log_path, appended, lock_token=token
                )
            self.assertEqual(
                log_path.read_bytes(),
                first + json.dumps(appended, sort_keys=True).encode() + b"\n",
            )

    def test_torn_tail_is_quarantined_exactly_before_truncation(self) -> None:
        first = json.dumps({"first": 1}, sort_keys=True).encode() + b"\n"
        torn = b'{"torn": [1, 2'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "campaign_log.jsonl"
            log_path.write_bytes(first + torn)
            stderr = io.StringIO()
            with held_campaign_lock(root) as token, patch.object(
                run_campaign_module,
                "utc_timestamp",
                return_value="2026-08-02T12:34:56.789Z",
            ), redirect_stderr(stderr):
                run_campaign_module.append_log(
                    log_path, {"after": True}, lock_token=token
                )
            sidecars = list(root.glob("campaign_log.jsonl.torn-*-*"))
            self.assertEqual(len(sidecars), 1)
            self.assertEqual(sidecars[0].read_bytes(), torn)
            self.assertIn(str(sidecars[0]), stderr.getvalue())
            self.assertIn(f"{len(torn)} torn campaign-log bytes", stderr.getvalue())

    def test_torn_tail_sidecar_failure_refuses_without_truncation(self) -> None:
        first = json.dumps({"first": 1}, sort_keys=True).encode() + b"\n"
        torn = b'{"torn": tru'
        before = first + torn
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "campaign_log.jsonl"
            log_path.write_bytes(before)
            real_open = run_campaign_module.os.open

            def refusing_sidecar_open(path, flags, *args, **kwargs):
                if flags & os.O_EXCL and ".torn-" in str(path):
                    raise PermissionError("injected sidecar failure")
                return real_open(path, flags, *args, **kwargs)

            with held_campaign_lock(root) as token, patch.object(
                run_campaign_module.os,
                "open",
                side_effect=refusing_sidecar_open,
            ), patch.object(run_campaign_module.os, "ftruncate") as truncate_mock:
                with self.assertRaisesRegex(PermissionError, "sidecar failure"):
                    run_campaign_module.append_log(
                        log_path, {"after": True}, lock_token=token
                    )
            truncate_mock.assert_not_called()
            self.assertEqual(log_path.read_bytes(), before)
            self.assertEqual(list(root.glob("campaign_log.jsonl.torn-*-*")), [])

    def test_append_log_rejects_non_string_and_non_ascii_key_paths(self) -> None:
        cases = (
            ({"outer": [{1: "bad"}]}, "row['outer'][0][1]"),
            ({"outer": [{"😀": "bad"}]}, "row['outer'][0]['😀']"),
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "campaign_log.jsonl"
            with held_campaign_lock(root) as token:
                for row, key_path in cases:
                    with self.subTest(key_path=key_path):
                        with self.assertRaises(ValueError) as caught:
                            run_campaign_module.append_log(
                                log_path, row, lock_token=token
                            )
                        self.assertIn(key_path, str(caught.exception))
            self.assertFalse(log_path.exists())

    def test_r11_mid_file_malformation_refuses_and_is_untouched(self) -> None:
        first = json.dumps({"first": 1}, sort_keys=True).encode() + b"\n"
        before = first + b'{"bad": }\n' + b'{"torn": tru'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "campaign_log.jsonl"
            log_path.write_bytes(before)
            self.assertEqual(self._parse(before), (None, "invalid"))
            with held_campaign_lock(root) as token:
                with self.assertRaisesRegex(ValueError, "non-final corruption"):
                    run_campaign_module.append_log(
                        log_path, {"new": True}, lock_token=token
                    )
            self.assertEqual(log_path.read_bytes(), before)


def run_campaign(
    config_dir: Path,
    runs_dir: Path,
    *,
    cli_cmd: str | None = None,
    dry_run: bool = False,
    max_failures: int | None = None,
    log_path: Path | None = None,
    backup: Path | None = None,
    waivers: Path | None = None,
    shakedown_gate: bool = False,
    ack_config_warnings: bool = False,
    campaign_policy: Path | None = TEST_CAMPAIGN_POLICY,
    environment_override: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), str(config_dir), "--runs-dir", str(runs_dir)]
    if log_path is not None:
        command.extend(["--log", str(log_path)])
    if dry_run:
        command.append("--dry-run")
    if backup is not None:
        command.extend(["--backup", str(backup)])
    if shakedown_gate:
        command.extend(["--shakedown-gate", "production_uncertainty_v1"])
    if ack_config_warnings:
        command.append("--ack-config-warnings")
    if campaign_policy is not None:
        command.extend(["--campaign-policy", str(campaign_policy)])
    if environment_override is not None:
        command.extend(["--environment-override", str(environment_override)])
    if waivers is not None:
        command.extend(["--waivers", str(waivers)])
    if cli_cmd is not None:
        command.extend(["--cli-cmd", cli_cmd])
    if max_failures is not None:
        command.extend(["--max-failures", str(max_failures)])
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=COMMAND_TIMEOUT_S,
    )


def cli_cmd_for(fake_cli: Path) -> str:
    return shlex.join([sys.executable, str(fake_cli)])


def rendered_cli_command(cli_cmd: str, config_path: Path, runs_dir: Path) -> str:
    return shlex.join(shlex.split(cli_cmd) + ["run", str(config_path), "--runs-dir", str(runs_dir)])


def write_config(config_dir: Path, filename: str, run_id: str, repetitions: int = 1) -> Path:
    path = config_dir / filename
    payload = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
    payload["run_id"] = run_id
    payload["workload_profile"]["repetitions"] = repetitions
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def write_suite_config(
    config_dir: Path,
    filename: str,
    run_id: str,
    *,
    sidecar: str | Path | None = None,
    suite_manifest: str | Path | None = None,
    prompt_token_evidence_policy: str | None = None,
) -> Path:
    path = config_dir / filename
    payload = json.loads(SUITE_CONFIG.read_text(encoding="utf-8"))
    payload["run_id"] = run_id
    if suite_manifest is not None:
        payload["workload_profile"]["suite_manifest_ref"] = str(suite_manifest)
    if sidecar is not None:
        payload["workload_profile"]["generator_sidecar_ref"] = str(sidecar)
    if prompt_token_evidence_policy is not None:
        payload["workload_profile"]["prompt_token_evidence_policy"] = (
            prompt_token_evidence_policy
        )
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
    return path


def write_prompt_sidecar(
    path: Path,
    *,
    item_003_hash: str,
    subset_sha256: str = "mock-subset",
    include_item_003: bool = True,
) -> None:
    items: dict[str, dict[str, str]] = {
        "mock_item_002": {
            "prompt_source": "token_ids",
            "token_ids_sha256": "5d7c51bfa697d3e72c8b79b97ba7396ffd399406ccb332b028bd38f44557a284",
        },
    }
    if include_item_003:
        items["mock_item_003"] = {"token_ids_sha256": item_003_hash}
    path.write_text(
        json.dumps(
            {
                "suite": "jw_mixed_v1",
                "source_manifest": {
                    "source_id": "mock_suite_source",
                    "subset_sha256": subset_sha256,
                },
                "tokenizer": {"tokenizer_id": "mock"},
                "items": items,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def write_single_bundle(
    runs_dir: Path,
    run_id: str,
    status: str = "succeeded",
    *,
    idle_window_suspect: bool | None = None,
    config_path: Path | None = None,
    start_s: float = 0.0,
    runtime_cleanup_ok: bool | None = None,
    remote_cleanup_failed: list[str] | None = None,
) -> None:
    _write_bundle(
        runs_dir,
        run_id,
        status,
        idle_window_suspect=idle_window_suspect,
        config_path=config_path,
        start_s=start_s,
        runtime_cleanup_ok=runtime_cleanup_ok,
        remote_cleanup_failed=remote_cleanup_failed,
    )


def write_experiment(
    runs_dir: Path,
    run_id: str,
    repetitions: int,
    *,
    statuses: list[str] | None = None,
    completed: int | None = None,
    config_path: Path | None = None,
) -> None:
    if statuses is None:
        statuses = ["succeeded"] * repetitions
    if completed is None:
        completed = repetitions
    members: list[str] = []
    for rep in range(1, completed + 1):
        member_name = f"{run_id}__r{rep}"
        members.append(member_name)
        _write_bundle(
            runs_dir,
            member_name,
            statuses[rep - 1],
            config_path=config_path,
        )
    experiments = runs_dir / "experiments"
    experiments.mkdir(parents=True, exist_ok=True)
    (experiments / f"{run_id}.json").write_text(
        json.dumps(
            {
                "experiment_id": run_id,
                "config_sha256": "fake",
                "members": members,
                "condition_order": ["test"] * len(members),
                "cooldown": [],
                "created_at_s": 0.0,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def _write_bundle(
    runs_dir: Path,
    run_id: str,
    status: str,
    *,
    idle_window_suspect: bool | None = None,
    config_path: Path | None = None,
    start_s: float = 0.0,
    runtime_cleanup_ok: bool | None = None,
    remote_cleanup_failed: list[str] | None = None,
) -> None:
    from joulewise import reduce as reduce_module
    from joulewise.bundle import RunBundleWriter, sanitize_id_component
    from joulewise.clock import FakeClock
    from joulewise.interfaces import PowerSample, RuntimeEvent
    from joulewise.provenance import output_policy, prompt_provenance
    from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus, SummaryMetrics

    source_config = config_path if config_path is not None else BASE_CONFIG
    config_data = json.loads(source_config.read_text(encoding="utf-8"))
    if sanitize_id_component(config_data["run_id"]) != run_id:
        config_data["run_id"] = run_id
    if config_path is None:
        config_data["workload_profile"]["repetitions"] = 1
    config = BenchmarkConfig.from_mapping(config_data)
    telemetry_backend = config.hardware_target.telemetry_backend.value
    writer = RunBundleWriter.create(runs_dir, config, FakeClock(start=start_s + 1.1))

    def event(timestamp_s: float, event_type: str, phase: str, message: str = "") -> None:
        writer.append_event(
            RuntimeEvent(
                timestamp_s=start_s + timestamp_s,
                event_type=event_type,
                phase=phase,
                message=message or f"{event_type} {phase}",
                metadata={},
            )
        )

    if status == "succeeded":
        event(0.0, "stage_started", "measured_run")
        event(0.0, "sampling_started", "measured_run")
        event(0.0, "phase_start", "prefill")
        event(0.5, "phase_end", "prefill")
        event(0.5, "phase_start", "decode")
        event(0.6, "token", "decode")
        event(0.7, "token", "decode")
        event(0.8, "phase_end", "decode")
        event(1.0, "sampling_stopped", "measured_run")
        event(1.0, "stage_completed", "measured_run")
        if runtime_cleanup_ok is not None:
            writer.append_event(
                RuntimeEvent(
                    timestamp_s=start_s + 1.05,
                    event_type="stage_completed",
                    phase="cleanup",
                    message="stage_completed cleanup",
                    metadata={"cleanup_ok": runtime_cleanup_ok},
                )
            )
        writer.write_power_trace(
            [
                PowerSample(
                    timestamp_s=start_s + step / 10.0,
                    power_w=7.5,
                    source=telemetry_backend,
                    rail="mock",
                )
                for step in range(11)
            ]
        )
        idle = {
            "power_w_mean": 5.0,
            "power_w_stddev": 0.0,
            "duration_s": 1.0,
            "sample_count": 2,
            "telemetry_backend": telemetry_backend,
            "idle_window_suspect": False,
        }
        if idle_window_suspect is not None:
            idle["idle_window_suspect"] = idle_window_suspect
        metadata = {
                "device": {"telemetry": telemetry_backend, "rail_manifest": ["mock"]},
                "adapters": {"telemetry": {"name": telemetry_backend}},
                "clock_anchor_bound_s": 0.0,
                "idle_drift_bound_w": 0.0,
                "idle_baseline": idle,
                "workload_observed": {"token_count": 34, "output_token_count": 2},
                "workload_provenance": {
                    "prompt": prompt_provenance([1, 2, 3], text="test"),
                    "generator": {"name": "fake_cli", "version": "test"},
                    "tokenizer": {
                        "backend": "mock",
                        "identifier": "fake",
                        "revision": "test",
                        "class": "FakeTokenizer",
                        "vocab_size": None,
                    },
                    "model": {"source": config.model.source, "revision": config.model.revision},
                    "output_policy": output_policy(
                        "fixed_budget_exact",
                        requested_tokens=2,
                        emitted_tokens=2,
                        stop_condition="requested_tokens_emitted",
                    ),
                },
            }
        if remote_cleanup_failed:
            metadata["extra"] = {
                "node_cleanup": [
                    {"path": path, "removed": False}
                    for path in remote_cleanup_failed
                ]
            }
        writer.write_metadata(metadata)
        summary = reduce_module.reduce_bundle(writer.path)
    else:
        writer.write_metadata(
            {
                "device": {"telemetry": "mock", "rail_manifest": ["mock"]},
                "adapters": {"telemetry": {"name": "mock"}},
            }
        )
        summary = SummaryMetrics(
            status=RunStatus.FAILED,
            failure_reason=FailureReason.UNKNOWN_ERROR,
            failure_message="fake failure",
        )
    writer.write_summary(summary)
    writer.finalize()


def make_fake_cli(tmp: Path, sentinel: Path | None = None) -> Path:
    sentinel_line = f"Path({str(sentinel)!r}).write_text('invoked\\n', encoding='utf-8')" if sentinel else "pass"
    script = tmp / "fake_cli.py"
    script.write_text(
        textwrap.dedent(
            f"""
            import json
            import sys
            from pathlib import Path

            ROOT = Path({str(ROOT)!r})
            if str(ROOT) not in sys.path:
                sys.path.insert(0, str(ROOT))
            from joulewise import reduce as reduce_module
            from joulewise.bundle import sanitize_id_component
            from joulewise.bundle import RunBundleWriter
            from joulewise.clock import FakeClock
            from joulewise.interfaces import PowerSample, RuntimeEvent
            from joulewise.provenance import output_policy, prompt_provenance
            from joulewise.schemas import BenchmarkConfig, FailureReason, RunStatus, SummaryMetrics

            {sentinel_line}
            if len(sys.argv) < 5 or sys.argv[1] != "run":
                raise SystemExit(64)

            config_path = Path(sys.argv[2])
            runs_dir = Path(sys.argv[sys.argv.index("--runs-dir") + 1])
            config = json.loads(config_path.read_text(encoding="utf-8"))
            run_id = sanitize_id_component(config["run_id"])
            repetitions = config.get("workload_profile", {{}}).get("repetitions", 1)
            runs_dir.mkdir(parents=True, exist_ok=True)
            with (runs_dir / "order.log").open("a", encoding="utf-8") as handle:
                handle.write(run_id + "\\n")

            def emit_bundle(bundle, status):
                print(f"bundle: {{bundle}} status={{status}}")

            def write_bundle(bundle_run_id, status):
                config_data = json.loads(config_path.read_text(encoding="utf-8"))
                config_data["run_id"] = bundle_run_id
                config = BenchmarkConfig.from_mapping(config_data)
                telemetry_backend = config.hardware_target.telemetry_backend.value
                writer = RunBundleWriter.create(runs_dir, config, FakeClock(start=3.0))

                def event(timestamp_s, event_type, phase, metadata=None):
                    writer.append_event(
                        RuntimeEvent(
                            timestamp_s=timestamp_s,
                            event_type=event_type,
                            phase=phase,
                            message=f"{{event_type}} {{phase}}",
                            metadata=metadata or {{}},
                        )
                    )

                if status == "succeeded":
                    event(0.0, "stage_started", "measured_run")
                    event(0.0, "sampling_started", "measured_run")
                    event(0.0, "phase_start", "tokenize")
                    event(0.05, "phase_end", "tokenize", {{"prompt_tokens": 3}})
                    event(0.05, "phase_start", "prefill", {{"prompt_tokens": 3}})
                    event(0.5, "phase_end", "prefill")
                    event(0.5, "phase_start", "decode")
                    event(0.6, "token", "decode")
                    event(0.7, "token", "decode")
                    event(0.8, "phase_end", "decode")
                    event(1.0, "sampling_stopped", "measured_run")
                    event(1.0, "stage_completed", "measured_run")
                    writer.write_power_trace(
                        [
                            PowerSample(timestamp_s=0.0, power_w=7.5, source=telemetry_backend, rail="mock"),
                            PowerSample(timestamp_s=0.25, power_w=7.5, source=telemetry_backend, rail="mock"),
                            PowerSample(timestamp_s=0.5, power_w=7.5, source=telemetry_backend, rail="mock"),
                            PowerSample(timestamp_s=0.75, power_w=7.5, source=telemetry_backend, rail="mock"),
                            PowerSample(timestamp_s=1.0, power_w=7.5, source=telemetry_backend, rail="mock"),
                        ]
                    )
                    writer.write_metadata(
                        {{
                            "device": {{"telemetry": telemetry_backend, "rail_manifest": ["mock"]}},
                            "adapters": {{"telemetry": {{"name": telemetry_backend}}}},
                            "clock_anchor_bound_s": 0.0,
                            "idle_drift_bound_w": 0.0,
                            "idle_baseline": {{
                                "power_w_mean": 5.0,
                                "power_w_stddev": 0.0,
                                "duration_s": 1.0,
                                "sample_count": 2,
                                "telemetry_backend": telemetry_backend,
                                "idle_window_suspect": False,
                            }},
                            "workload_observed": {{"token_count": 5, "output_token_count": 2}},
                            "workload_provenance": {{
                                "prompt": prompt_provenance([1, 2, 3], text="test"),
                                "generator": {{"name": "fake_cli", "version": "test"}},
                                "tokenizer": {{
                                    "backend": "mock",
                                    "identifier": "fake",
                                    "revision": "test",
                                    "class": "FakeTokenizer",
                                    "vocab_size": None,
                                }},
                                "model": {{"source": config.model.source, "revision": config.model.revision}},
                                "output_policy": output_policy(
                                    "fixed_budget_exact",
                                    requested_tokens=2,
                                    emitted_tokens=2,
                                    stop_condition="requested_tokens_emitted",
                                ),
                            }},
                        }}
                    )
                    summary = reduce_module.reduce_bundle(writer.path)
                else:
                    writer.write_metadata(
                        {{
                            "device": {{"telemetry": "mock", "rail_manifest": ["mock"]}},
                            "adapters": {{"telemetry": {{"name": "mock"}}}},
                        }}
                    )
                    summary = SummaryMetrics(
                        status=RunStatus.FAILED,
                        failure_reason=FailureReason.UNKNOWN_ERROR,
                        failure_message="fake failure",
                    )
                writer.write_summary(summary)
                bundle = writer.finalize()
                emit_bundle(bundle, status)

            def write_single(status):
                write_bundle(run_id, status)

            def write_manifest(members):
                experiments = runs_dir / "experiments"
                experiments.mkdir(parents=True, exist_ok=True)
                manifest = experiments / f"{{run_id}}.json"
                manifest.write_text(
                    json.dumps(
                        {{
                            "experiment_id": run_id,
                            "config_sha256": "fake",
                            "members": members,
                            "condition_order": ["test"] * len(members),
                            "cooldown": [],
                            "created_at_s": 0.0,
                        }}
                    )
                    + "\\n",
                    encoding="utf-8",
                )
                return manifest

            def write_experiment(statuses, completed=None):
                if completed is None:
                    completed = repetitions
                members = []
                for rep in range(1, completed + 1):
                    member_name = f"{{run_id}}__r{{rep}}"
                    members.append(member_name)
                    write_bundle(member_name, statuses[rep - 1])
                manifest = write_manifest(members)
                print(f"experiment: {{manifest}} members={{len(members)}}")

            if "fail" in run_id:
                if repetitions > 1:
                    statuses = ["succeeded"] * repetitions
                    statuses[-1] = "failed"
                    write_experiment(statuses)
                else:
                    write_single("failed")
                raise SystemExit(3)

            if "exit2" in run_id:
                raise SystemExit(2)

            if "crash2" in run_id:
                if repetitions > 1:
                    write_experiment(["succeeded"] * repetitions, completed=min(2, repetitions))
                else:
                    (runs_dir / run_id).mkdir(parents=True, exist_ok=True)
                raise SystemExit(3)

            if "partial" in run_id:
                if repetitions > 1:
                    write_experiment(["succeeded"] * repetitions, completed=max(1, repetitions - 2))
                else:
                    (runs_dir / run_id).mkdir(parents=True, exist_ok=True)
                raise SystemExit(3)

            if repetitions > 1:
                write_experiment(["succeeded"] * repetitions)
            else:
                write_single("succeeded")
            raise SystemExit(0)
            """
        ).lstrip(),
        encoding="utf-8",
    )
    return script


def read_jsonl(path: Path) -> list[dict]:
    return [
        row
        for row in read_all_jsonl(path)
        if row.get("record_type") != "campaign_verdict"
    ]


def read_all_jsonl(path: Path) -> list[dict]:
    return [
        row
        for row in read_wire_jsonl(path)
        if row.get("record_type") != "campaign_provenance_attestation"
    ]


def read_wire_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def write_strict_analysis_campaign(
    config_dir: Path,
    runs_dir: Path | None = None,
    *,
    telemetry_backend: str = "mock",
) -> dict:
    base_payload = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
    base_payload["hardware_target"]["telemetry_backend"] = telemetry_backend
    base_path = config_dir.parent / "analysis-base.json"
    base_path.write_text(json.dumps(base_payload) + "\n", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            str(GENERATOR),
            "--base",
            str(base_path),
            "--model-tag",
            "mock",
            "--out-dir",
            str(config_dir),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=COMMAND_TIMEOUT_S,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    manifest = json.loads(
        (config_dir / "analysis_manifest.json").read_text(encoding="utf-8")
    )
    if runs_dir is not None:
        for index, entry in enumerate(manifest["entries"]):
            write_single_bundle(
                runs_dir,
                entry["run_id"],
                config_path=config_dir / entry["config"],
                start_s=float(index * 2),
            )
    return manifest


def write_prior_campaign_provenance(
    runs_dir: Path,
    evidence_by_bundle: dict[str, str],
    analysis_manifest_id: str,
) -> None:
    manifest_dir = runs_dir / "campaign_manifests"
    raw_dir = manifest_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    session_id = "campaign-fixture"
    members = []
    for index, (bundle_id, result) in enumerate(evidence_by_bundle.items()):
        raw_name = f"fixture-{index}.jsonl"
        raw_payload = json.dumps(
            {
                "rolling_mean_power_w": 5.0,
                "release": result == "recovered",
                "release_criteria_met_late": False,
            }
        ) + "\n"
        (raw_dir / raw_name).write_text(raw_payload, encoding="utf-8")
        raw_sha = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
        cooldown: dict[str, object] = {
            "result": result,
            "session_id": session_id,
            "following_run_id": bundle_id,
        }
        if result in {"recovered", "cap_hit"}:
            cooldown["raw_artifact"] = {
                "path": f"raw/{raw_name}",
                "sha256": raw_sha,
                "records": 1,
            }
        members.append(
            {
                "config": f"{bundle_id}.json",
                "run_id": bundle_id,
                "bundle_ids": [bundle_id],
                "execution": "invoked",
                "preceding_campaign_cooldown": cooldown,
            }
        )
    (manifest_dir / "fixture.json").write_text(
        json.dumps(
            {
                "schema_version": "joulewise.campaign_provenance.v1",
                "session_id": session_id,
                "created_at": "2026-07-10T00:00:00Z",
                "config_dir": "fixture",
                "analysis_manifest_id": analysis_manifest_id,
                "first_physical_run_id": next(iter(evidence_by_bundle), None),
                "members": members,
                "cooldown_gates": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def write_malformed_first_exemption_provenance(
    runs_dir: Path,
    manifest: dict,
    *,
    fan_out_one_note: bool,
) -> None:
    manifest_dir = runs_dir / "campaign_manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    session_id = "campaign-malformed-first-exemptions"
    run_ids = [entry["run_id"] for entry in manifest["entries"]]
    first_run_id = run_ids[0]
    if fan_out_one_note:
        members = [
            {
                "config": manifest["entries"][0]["config"],
                "run_id": first_run_id,
                "bundle_ids": run_ids,
                "execution": "invoked",
                "preceding_campaign_cooldown": {
                    "result": "first_run_exempt",
                    "session_id": session_id,
                    "following_run_id": first_run_id,
                },
            }
        ]
    else:
        members = [
            {
                "config": entry["config"],
                "run_id": entry["run_id"],
                "bundle_ids": [entry["run_id"]],
                "execution": "invoked",
                "preceding_campaign_cooldown": {
                    "result": "first_run_exempt",
                    "session_id": session_id,
                    "following_run_id": entry["run_id"],
                },
            }
            for entry in manifest["entries"]
        ]
    (manifest_dir / "malformed-first-exemptions.json").write_text(
        json.dumps(
            {
                "schema_version": "joulewise.campaign_provenance.v1",
                "session_id": session_id,
                "created_at": "2026-07-10T00:00:00Z",
                "config_dir": "fixture",
                "analysis_manifest_id": manifest["manifest_id"],
                "first_physical_run_id": first_run_id,
                "members": members,
                "cooldown_gates": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def analysis_manifest_id(config_dir: Path) -> str:
    return json.loads(
        (config_dir / "analysis_manifest.json").read_text(encoding="utf-8")
    )["manifest_id"]


class RunCampaignTests(unittest.TestCase):
    def test_campaign_policy_defaults_to_production_sidecar(self) -> None:
        args = run_campaign_module.parse_args(["configs"])
        binding = run_campaign_module.load_campaign_policy(args.campaign_policy)
        self.assertEqual(binding.policy.policy_id, "quiet-mac-p2-production")
        self.assertEqual(binding.policy.profile.value, "production")
        self.assertEqual(binding.policy.idle_admission.on_fail.value, "abort")
        self.assertEqual(binding.policy.post_window_sampling_dwell_s, 1.0)

    def test_campaign_policy_rejects_subsecond_post_window_dwell(self) -> None:
        from joulewise.schemas import SchemaError

        payload = json.loads(TEST_CAMPAIGN_POLICY.read_text())
        payload["post_window_sampling_dwell_s"] = 0.999
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            path.write_text(json.dumps(payload) + "\n")
            with self.assertRaisesRegex(SchemaError, ">= 1.0"):
                run_campaign_module.load_campaign_policy(str(path))

    def test_frozen_campaign_anchor_is_explicit_child_experiment_argument(self) -> None:
        from joulewise import cli as cli_module
        from joulewise.clock import FakeClock

        anchor = {
            "schema_version": "joulewise.cooldown_anchor.v1",
            "source_kind": "neg8_reference_start",
            "bundle_id": "neg8-anchor",
            "policy_sha256": "a" * 64,
            "environment_snapshot_sha256": "b" * 64,
            "immutable_after_freeze": True,
            "eligibility": {
                "eligible": True,
                "provenance_present": True,
            },
            "baseline": {
                "power_w_mean": 5.0,
                "power_w_stddev": 0.0,
                "duration_s": 30.0,
                "sample_count": 30,
                "telemetry_backend": "powermetrics",
                "idle_window_suspect": False,
            },
        }
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_dir = root / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "multi.json", "multi", repetitions=2
            )
            with (
                patch(
                    "run_campaign_module.prior_campaign_cooldown_anchor",
                    return_value=anchor,
                ),
                patch(
                    "run_campaign_module.command_for",
                    wraps=run_campaign_module.command_for,
                ) as parent_command,
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                parent_code = run_campaign_module.main(
                    [
                        str(config_dir),
                        "--runs-dir",
                        str(runs_dir),
                        "--dry-run",
                        "--campaign-policy",
                        str(TEST_CAMPAIGN_POLICY),
                    ]
                )

            self.assertEqual(parent_code, 0)
            self.assertEqual(
                parent_command.call_args.kwargs["frozen_cooldown_anchor"], anchor
            )
            command = run_campaign_module.command_for(
                config_path,
                runs_dir,
                None,
                frozen_cooldown_anchor=anchor,
            )
            self.assertIn("--frozen-cooldown-anchor-json", command)
            anchor_index = command.index("--frozen-cooldown-anchor-json") + 1
            self.assertEqual(json.loads(command[anchor_index]), anchor)

            with (
                patch("joulewise.cli._select_clock", return_value=FakeClock()),
                patch(
                    "joulewise.cli.run_experiment",
                    return_value=(runs_dir / "experiments" / "multi.json", []),
                ) as child_experiment,
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                child_code = cli_module.main(command[3:])

            self.assertEqual(child_code, 0)
            self.assertEqual(
                child_experiment.call_args.kwargs["frozen_cooldown_anchor"], anchor
            )

    def test_campaign_command_forwards_instrument_calibration_attachment(self) -> None:
        # F7/F9 production plumbing regression: the campaign layer must not
        # strand a validated directory outside the benchmark controller.
        command = run_campaign_module.command_for(
            BASE_CONFIG,
            Path("runs"),
            None,
            instrument_calibration_dir="validated/calibration",
            instrument_power_policy="ac_high_power",
        )
        self.assertEqual(
            command[command.index("--instrument-calibration-dir") + 1],
            "validated/calibration",
        )
        self.assertEqual(
            command[command.index("--instrument-power-policy") + 1],
            "ac_high_power",
        )

    def test_campaign_command_forwards_policy_post_window_dwell(self) -> None:
        # R4 defect shape: the sidecar formerly had no route to the existing
        # controller dwell, so live campaigns stopped sampling immediately.
        command = run_campaign_module.command_for(
            BASE_CONFIG,
            Path("runs"),
            None,
            post_window_sampling_dwell_s=1.0,
        )
        self.assertEqual(
            command[command.index("--post-window-sampling-dwell-s") + 1],
            "1.0",
        )

    def test_parent_anchor_validator_has_canonical_child_parity(self) -> None:
        from joulewise.cooldown_anchor import cooldown_anchor_eligibility

        policy_sha256 = "a" * 64
        anchor = {
            "schema_version": "joulewise.cooldown_anchor.v1",
            "source_kind": "neg8_reference_start",
            "bundle_id": "neg8-anchor",
            "policy_sha256": policy_sha256,
            "environment_snapshot_sha256": "b" * 64,
            "immutable_after_freeze": True,
            "eligibility": {
                "eligible": True,
                "provenance_present": True,
            },
            "baseline": {
                "power_w_mean": 5.0,
                "power_w_stddev": 0.0,
                "duration_s": 30.0,
                "sample_count": 30,
                "telemetry_backend": "powermetrics",
                "idle_window_suspect": False,
            },
        }
        malformed = json.loads(json.dumps(anchor))
        malformed["policy_sha256"] = "c" * 64
        malformed["eligibility"].pop("provenance_present")
        malformed["baseline"]["idle_window_suspect"] = True

        for candidate in (anchor, malformed):
            with self.subTest(eligible=candidate is anchor):
                self.assertEqual(
                    run_campaign_module._cooldown_anchor_eligibility(
                        candidate, policy_sha256
                    ),
                    cooldown_anchor_eligibility(candidate, policy_sha256),
                )

    def test_environment_preflight_fails_closed_and_override_binds_exact_snapshot(self) -> None:
        binding = run_campaign_module.load_campaign_policy(
            str(ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json")
        )
        snapshot = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "display_power_state": "any_awake",
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
            "load_average_1m": 0.0,
        }
        with tempfile.TemporaryDirectory() as tmp:
            with patch(
                "run_campaign_module.collect_environment_snapshot",
                return_value=snapshot,
            ):
                blocked = run_campaign_module.campaign_environment_preflight(
                    binding,
                    arm_quiet_mode=False,
                    arm_countdown_s=0,
                    override_path=None,
                )
            self.assertFalse(blocked["admitted"])
            evaluation = blocked["evaluation"]
            override_path = Path(tmp) / "override.json"
            override_path.write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.environment_override.v1",
                        "snapshot_sha256": evaluation["snapshot_sha256"],
                        "findings_sha256": evaluation["findings_sha256"],
                        "reason": "bounded exploratory collection",
                        "approver": "campaign-owner",
                        "timestamp": "2026-07-17T00:00:00Z",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            with patch(
                "run_campaign_module.collect_environment_snapshot",
                return_value=snapshot,
            ):
                overridden = run_campaign_module.campaign_environment_preflight(
                    binding,
                    arm_quiet_mode=False,
                    arm_countdown_s=0,
                    override_path=str(override_path),
                )

        self.assertTrue(overridden["admitted"])
        self.assertEqual(overridden["override"]["classification"], "override")
        self.assertFalse(overridden["override"]["claim_eligible"])

    def test_rejected_environment_preflight_appends_terminal_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_dir = root / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            args = run_campaign_module.parse_args(
                [
                    str(config_dir),
                    "--runs-dir",
                    str(runs_dir),
                    "--campaign-policy",
                    str(
                        ROOT
                        / "configs"
                        / "campaign_policies"
                        / "quiet_mac_p2_production.json"
                    ),
                ]
            )
            rejected = {
                "power_source": "AC Power",
                "power": {"external_connected": True},
                "low_power_mode": False,
                "display_power_state": "any_awake",
                "screensaver_engaged": False,
                "thermal_pressure": "nominal",
            }
            with patch(
                "run_campaign_module.collect_environment_snapshot",
                return_value=rejected,
            ):
                result = run_campaign_module.run_campaign(args)

            self.assertEqual(result, 1)
            rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[-1]["schema_version"], "joulewise.campaign_verdict.v2")
            self.assertEqual(rows[-1]["record_type"], "campaign_verdict")
            self.assertEqual(rows[-1]["collection"]["verdict"], "invalid")
            self.assertIn(
                "environment preflight rejected",
                rows[-1]["collection"]["reasons"][0],
            )

    def test_malformed_environment_override_appends_terminal_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_dir = root / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            override = root / "override.json"
            override.write_text("{not-json\n", encoding="utf-8")
            args = run_campaign_module.parse_args(
                [
                    str(config_dir),
                    "--runs-dir",
                    str(runs_dir),
                    "--campaign-policy",
                    str(
                        ROOT
                        / "configs"
                        / "campaign_policies"
                        / "quiet_mac_p2_production.json"
                    ),
                    "--environment-override",
                    str(override),
                ]
            )
            clean = {
                "power_source": "AC Power",
                "power": {"external_connected": True},
                "low_power_mode": False,
                "display_power_state": "all_asleep",
                "screensaver_engaged": False,
                "thermal_pressure": "nominal",
            }
            with patch(
                "run_campaign_module.collect_environment_snapshot",
                return_value=clean,
            ):
                result = run_campaign_module.run_campaign(args)

            self.assertEqual(result, 2)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["record_type"], "campaign_verdict")
            self.assertEqual(verdict["collection"]["verdict"], "invalid")

    def test_arm_quiet_mode_counts_down_sleeps_display_and_reprobes(self) -> None:
        binding = run_campaign_module.load_campaign_policy(
            str(ROOT / "configs" / "campaign_policies" / "quiet_mac_p2_production.json")
        )
        base = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "screensaver_engaged": False,
            "thermal_pressure": "nominal",
            "load_average_1m": 0.0,
        }
        awake = {**base, "display_power_state": "any_awake"}
        asleep = {**base, "display_power_state": "all_asleep"}
        completed = subprocess.CompletedProcess(
            ["pmset", "displaysleepnow"], 0, "", ""
        )
        with (
            patch(
                "run_campaign_module.collect_environment_snapshot",
                side_effect=[awake, asleep],
            ) as collect,
            patch("run_campaign_module.subprocess.run", return_value=completed) as run,
        ):
            result = run_campaign_module.campaign_environment_preflight(
                binding,
                arm_quiet_mode=True,
                arm_countdown_s=0,
                override_path=None,
            )

        self.assertEqual(collect.call_count, 2)
        self.assertEqual(run.call_args.args[0], ["pmset", "displaysleepnow"])
        self.assertTrue(result["admitted"])
        self.assertTrue(result["arm_quiet_mode"]["verified_by_reprobe"])

    def test_cooldown_v2_contaminated_reference_falls_back_to_frozen_anchor(self) -> None:
        from joulewise.clock import FakeClock
        from joulewise.interfaces import ThermalState
        from joulewise.schemas import IdleBaseline, TelemetryBackend

        class CooldownTelemetry:
            name = "cooldown-fixture"

            def __init__(self, clock):
                self.clock = clock

            def measure_idle(self, config, context=None):
                self.clock.sleep(config.sampling.idle_seconds)
                return IdleBaseline(
                    power_w_mean=0.15,
                    power_w_stddev=0.0,
                    duration_s=config.sampling.idle_seconds,
                    sample_count=5,
                    telemetry_backend=TelemetryBackend.POWERMETRICS,
                    idle_window_suspect=False,
                )

            def thermal_state(self, config, context=None):
                return ThermalState(
                    timestamp_s=self.clock.now(), thermal_pressure="Nominal"
                )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_path = root / "previous.json"
            payload = json.loads(BASE_CONFIG.read_text(encoding="utf-8"))
            payload["run_id"] = "previous"
            payload["hardware_target"]["telemetry_backend"] = "powermetrics"
            config_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            previous_info = run_campaign_module.ConfigInfo(
                path=config_path,
                run_id="previous",
                raw_run_id="previous",
                repetitions=1,
            )
            following_info = run_campaign_module.ConfigInfo(
                path=config_path,
                run_id="following",
                raw_run_id="following",
                repetitions=1,
            )
            contaminated = {
                "power_w_mean": 0.8,
                "power_w_stddev": 0.1,
                "duration_s": 30.0,
                "sample_count": 30,
                "telemetry_backend": "powermetrics",
                "idle_window_suspect": True,
            }
            previous = run_campaign_module.MemberEvaluation(
                bundle_id="previous",
                bundle_path=root / "previous",
                config_name=config_path.name,
                status="succeeded",
                strict_valid=True,
                summary={"idle_baseline": contaminated},
                metadata={
                    "campaign_policy": {"sha256": "b" * 64},
                    "environment_admission": {
                        "critical_environment_passed": False,
                        "decision": "flagged",
                        "reference_provenance_present": True,
                    },
                },
            )
            binding = run_campaign_module.load_campaign_policy(
                str(
                    ROOT
                    / "configs"
                    / "campaign_policies"
                    / "quiet_mac_p2_production.json"
                )
            )
            anchor = {
                "schema_version": "joulewise.cooldown_anchor.v1",
                "source_kind": "neg8_reference_start",
                "bundle_id": "p2015-neg8-reference-start",
                "policy_sha256": binding.sha256,
                "baseline": {
                    **contaminated,
                    "power_w_mean": 0.2,
                    "idle_window_suspect": False,
                },
                "eligibility": {
                    "eligible": True,
                    "provenance_present": True,
                },
                "environment_snapshot_sha256": "a" * 64,
                "immutable_after_freeze": True,
            }
            provenance_path = root / "campaign_manifests" / "session.json"
            provenance_path.parent.mkdir()
            clock = FakeClock()
            telemetry = CooldownTelemetry(clock)
            with (
                patch("joulewise.clock.SystemClock", return_value=clock),
                patch(
                    "joulewise.adapters.resolve_telemetry",
                    return_value=(telemetry, None),
                ),
            ):
                note = run_campaign_module.campaign_cooldown_before_member(
                    previous_info=previous_info,
                    previous_evaluation=previous,
                    following_info=following_info,
                    provenance_path=provenance_path,
                    session_id="session",
                    policy_binding=binding,
                    frozen_anchor=anchor,
                )

        self.assertEqual(note["result"], "recovered")
        self.assertEqual(note["reference_selection"], "frozen_clean_anchor")
        self.assertFalse(note["reference_eligibility"]["eligible"])
        self.assertEqual(note["reference_power_w"], 0.2)
        self.assertGreaterEqual(note["window_coverage_s"], 30.0)
        self.assertTrue(note["thermal_nominal"])
        self.assertEqual(
            note["anchor_provenance"]["bundle_id"],
            "p2015-neg8-reference-start",
        )

    def test_physical_repetitions_receive_distinct_cooldown_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "configs"
            runs_dir = root / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "three.json", "three", repetitions=3
            )
            write_experiment(
                runs_dir, "three", 3, config_path=config_path
            )
            manifest_path = runs_dir / "experiments" / "three.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["cooldown"] = [
                {"after_member": "three__r1", "result": "recovered"},
                {"after_member": "three__r2", "result": "cap_hit"},
            ]
            manifest_path.write_text(json.dumps(manifest) + "\n")
            info = run_campaign_module.load_config_info(config_path)
            self.assertIsInstance(info, run_campaign_module.ConfigInfo)
            binding = run_campaign_module.load_campaign_policy(
                str(TEST_CAMPAIGN_POLICY)
            )
            with held_campaign_lock(runs_dir):
                provenance_path, _provenance = (
                    run_campaign_module.new_campaign_provenance(
                        config_dir, runs_dir, None, binding
                    )
                )
            first = {
                **run_campaign_module._cooldown_policy_decision_surface(
                    binding.policy.cooldown
                ),
                "result": "first_run_exempt",
                "session_id": "session",
                "following_run_id": "three__r1",
            }
            evidence = run_campaign_module._physical_cooldown_evidence_for_config(
                info,
                runs_dir,
                first,
                provenance_path,
                binding.policy.cooldown,
            )

        self.assertEqual(evidence["three__r1"]["result"], "first_run_exempt")
        self.assertEqual(evidence["three__r2"]["result"], "recovered")
        self.assertEqual(evidence["three__r3"]["result"], "cap_hit")
        self.assertNotEqual(evidence["three__r2"], evidence["three__r1"])
        self.assertNotEqual(evidence["three__r3"], evidence["three__r1"])

    def test_marker_bearing_axi_refuses_before_child_dispatch(self) -> None:
        state = run_campaign_module.load_analysis_manifest(
            ROOT / "tests" / "fixtures" / "axi_ap_spec"
        )
        self.assertIsNotNone(state)
        assert state is not None
        binding = run_campaign_module.load_campaign_policy(
            str(TEST_CAMPAIGN_POLICY)
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            marker_config = root / "marker.json"
            config = json.loads(
                (ROOT / "tests" / "fixtures" / "axi_ap_spec" / "draft_spec_off.json")
                .read_text()
            )
            config["run_metadata"]["tags"].append("launch_lineage_required")
            marker_config.write_text(json.dumps(config) + "\n")
            marked_raw = copy.deepcopy(state.raw)
            for entry in marked_raw["entries"]:
                entry["config"] = str(marker_config)
            marked_state = replace(state, raw=marked_raw)
            runs_dir = root / "runs"
            with patch.object(
                run_campaign_module, "run_authenticated_campaign_child"
            ) as child:
                with self.assertRaises(
                    run_campaign_module.LaunchLineageError
                ) as caught:
                    run_campaign_module.run_axi_spec_campaign(
                        run_campaign_module.argparse.Namespace(
                            dry_run=False,
                            cli_cmd=None,
                            arm_quiet_mode=False,
                            arm_countdown_s=0,
                            environment_override=None,
                        ),
                        marked_state,
                        runs_dir=runs_dir,
                        policy_binding=binding,
                    )
            self.assertEqual(
                caught.exception.reason_code,
                "launch_lineage_axi_unsupported",
            )
            child.assert_not_called()
            self.assertFalse(runs_dir.exists())

    def test_non_marker_axi_multi_entry_campaign_records_gate_before_entry_two(self) -> None:
        state = run_campaign_module.load_analysis_manifest(
            ROOT / "tests" / "fixtures" / "axi_ap_spec"
        )
        self.assertIsNotNone(state)
        binding = run_campaign_module.load_campaign_policy(
            str(TEST_CAMPAIGN_POLICY)
        )
        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            result = run_campaign_module.run_axi_spec_campaign(
                run_campaign_module.argparse.Namespace(
                    dry_run=False,
                    cli_cmd=None,
                    arm_quiet_mode=False,
                    arm_countdown_s=0,
                    environment_override=None,
                ),
                state,
                runs_dir=runs_dir,
                policy_binding=binding,
            )
            manifests = list((runs_dir / "campaign_manifests").glob("*.json"))
            self.assertEqual(len(manifests), 1)
            provenance = json.loads(manifests[0].read_text())

        self.assertEqual(result, 0)
        self.assertGreaterEqual(len(provenance["members"]), 2)
        first = provenance["members"][0]["physical_members"][0]
        second = provenance["members"][1]["physical_members"][0]
        self.assertEqual(
            first["preceding_campaign_cooldown"]["result"],
            "first_run_exempt",
        )
        self.assertNotEqual(
            second["preceding_campaign_cooldown"]["result"],
            "first_run_exempt",
        )
        self.assertEqual(len(provenance["cooldown_gates"]), 3)
        selection = provenance["attempt_ledger_selection"]
        self.assertEqual(
            {row["bundle_id"] for row in selection["selected_bundles"]},
            set(selection["selected_bundle_ids"]),
        )

    def test_axi_runner_emits_campaign_wide_idle_admission_verdict(self) -> None:
        # F5 defect shape: the AXI path formerly returned immediately after
        # attempt-ledger/output-identity work, never constructing the core
        # whole-window barrier at all.
        state = run_campaign_module.load_analysis_manifest(
            ROOT / "tests" / "fixtures" / "axi_ap_spec"
        )
        self.assertIsNotNone(state)
        binding = run_campaign_module.load_campaign_policy(
            str(ROOT / "configs" / "campaign_policies" / "quiet_mac_exploratory.json")
        )
        snapshot = {
            "power_source": "AC Power",
            "power": {"external_connected": True},
            "low_power_mode": False,
            "display_power_state": "all_asleep",
            "screensaver_engaged": False,
            "screensaver_module": "fixture",
            "screensaver_delay_s": 1200,
            "hid_idle_s": 1200.0,
            "thermal_pressure": "nominal",
            "load_average_1m": 0.0,
            "capture_scope": "provided_test_fixture",
            "python_packages": {"mlx": {"version": "test"}},
        }
        admitted = {
            "schema_version": "joulewise.campaign_environment_preflight.v1",
            "policy_sha256": binding.sha256,
            "snapshot": snapshot,
            "evaluation": evaluate_environment_policy(
                snapshot, binding.policy.environment_guard
            ),
            "override": None,
            "admitted": True,
        }
        calibration_snapshot, _candidates = _fixture_snapshot([])
        loaded_drift_bound = {"sentinel": "loaded-neg8-bound"}

        def passing_core_evaluation(evaluations, policy_binding, **_kwargs):
            return run_campaign_module._IdleAdmissionCoreEvaluation(
                core={
                    "schema_version": run_campaign_module.IDLE_ADMISSION_CORE_SCHEMA,
                    "policy_sha256": policy_binding.sha256,
                    "members": [
                        {
                            "bundle_id": evaluation.bundle_id,
                            "cpu_admission": {"decision": "admitted"},
                        }
                        for evaluation in evaluations
                    ],
                    "adapter_wattage_continuity": {"decision": "stable"},
                    "neg8_bracket": {"decision": "passed"},
                    "instrument_calibration_bracket": None,
                    "conditions": [],
                },
                member_failures=(),
            )

        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            log_path = runs_dir / "campaign_log.jsonl"
            real_subprocess_run = subprocess.run

            def run_child_without_policy_environment(command, *, check, env):
                clean_env = dict(env or {})
                for name in (
                    run_campaign_module.CAMPAIGN_POLICY_PATH_ENV,
                    run_campaign_module.CAMPAIGN_POLICY_SHA256_ENV,
                    run_campaign_module.CAMPAIGN_PREFLIGHT_JSON_ENV,
                ):
                    clean_env.pop(name, None)
                return real_subprocess_run(command, check=check, env=clean_env)

            with (
                patch.object(
                    run_campaign_module,
                    "campaign_environment_preflight",
                    return_value=admitted,
                ),
                patch.object(
                    run_campaign_module.subprocess,
                    "run",
                    side_effect=run_child_without_policy_environment,
                ),
                patch.object(
                    run_campaign_module,
                    "campaign_cooldown_before_member",
                    return_value={"result": "recovered"},
                ),
                patch.object(
                    run_campaign_module,
                    "_load_calibration_snapshot_for_evaluation",
                    return_value=calibration_snapshot,
                ),
                patch.object(
                    run_campaign_module,
                    "_idle_admission_core_evaluation",
                    side_effect=passing_core_evaluation,
                ) as core_evaluation,
                patch.object(
                    run_campaign_module,
                    "load_neg8_drift_bound_artifact",
                    return_value=loaded_drift_bound,
                ),
                patch.object(
                    run_campaign_module,
                    "build_evaluation_basis",
                    wraps=run_campaign_module.build_evaluation_basis,
                ) as basis_builder,
                patch(
                    "joulewise.calibration_bracketing."
                    "load_calibration_acceptance_bound",
                    return_value=_unissued_acceptance_fixture(),
                ),
            ):
                result = run_campaign_module.run_axi_spec_campaign(
                    run_campaign_module.argparse.Namespace(
                        dry_run=False,
                        cli_cmd=None,
                        arm_quiet_mode=False,
                        arm_countdown_s=0,
                        environment_override=None,
                    ),
                    state,
                    runs_dir=runs_dir,
                    policy_binding=binding,
                    log_path=log_path,
                )
            rows = read_all_jsonl(log_path)
        self.assertEqual(result, 0)
        whole = [
            row
            for row in rows
            if row.get("record_type") == "idle_admission_whole_window_verdict"
        ]
        self.assertEqual(len(whole), 1)
        core_evaluation.assert_called_once()
        basis_builder.assert_called_once()
        self.assertIs(
            basis_builder.call_args.kwargs["drift_bound_artifact"],
            loaded_drift_bound,
        )
        self.assertEqual(whole[0]["status"], "passed")
        self.assertFalse(whole[0]["claim_licensing"])
        self.assertEqual(whole[0]["member_failures"], [])
        self.assertEqual(
            whole[0]["idle_admission_core"]["schema_version"],
            run_campaign_module.IDLE_ADMISSION_CORE_SCHEMA,
        )

    def test_axi_restart_after_quarantined_attempt_cannot_reuse_first_run_exemption(self) -> None:
        # F15 audit reproduction: a fresh process has a new provenance object,
        # but the persisted technical-invalid attempt row is durable physical
        # evidence and therefore forbids another first-run exemption.
        fresh_provenance = {"first_physical_run_id": None}
        quarantined = {
            "entry_id": "entry-a",
            "attempt_ordinal": 0,
            "eligible_for_analysis": False,
            "technical_invalid_reason_code": "strict_bundle_invalid",
        }
        self.assertFalse(
            run_campaign_module._axi_first_run_exemption_allowed(
                fresh_provenance, [quarantined]
            )
        )
        self.assertTrue(
            run_campaign_module._axi_first_run_exemption_allowed(
                fresh_provenance, []
            )
        )

    def test_truncated_self_hashed_attempt_ledger_is_refused(self) -> None:
        # F5 exact defect: self-consistent bytes are not selection semantics.
        # This deliberately truncated ledger used to admit the selected set.
        binding = run_campaign_module.load_campaign_policy(str(TEST_CAMPAIGN_POLICY))
        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp)
            selected_ids = [
                "p2-neg8-reference-start__a1__start",
                "p2-neg8-reference-end__a0__end",
            ]
            selected_paths = []
            for index, bundle_id in enumerate(selected_ids):
                path = runs_dir / "axi_attempt_bundles" / f"selected-{index}"
                path.mkdir(parents=True)
                selected_paths.append(path)
            evidence_dir = runs_dir / "axi_attempt_evidence" / "m"
            evidence_dir.mkdir(parents=True)
            ledger_path = evidence_dir / "attempt_ledger.jsonl"
            ledger_path.write_text('{"persisted":true}\n')
            manifest_dir = runs_dir / "campaign_manifests"
            manifest_dir.mkdir()
            selection = {
                "schema_version": "joulewise.attempt_ledger_selection.v1",
                "attempt_ledger_path": ledger_path.relative_to(runs_dir).as_posix(),
                "attempt_ledger_sha256": hashlib.sha256(
                    ledger_path.read_bytes()
                ).hexdigest(),
                "selected_bundle_ids": sorted(selected_ids),
                "selected_membership_sha256": hashlib.sha256(
                    json.dumps(
                        sorted(selected_ids),
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode()
                ).hexdigest(),
                "selected_bundles": [
                    {
                        "bundle_id": bundle_id,
                        "path": path.relative_to(runs_dir).as_posix(),
                    }
                    for bundle_id, path in zip(selected_ids, selected_paths)
                ],
                "quarantined_attempts": [
                    {
                        "properly_quarantined": True,
                        "recovery_continuity_verified": True,
                    }
                ],
            }
            (manifest_dir / "retry.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.campaign_provenance.v1",
                        "analysis_manifest_id": "m",
                        "campaign_policy": {"sha256": binding.sha256},
                        "attempt_ledger_selection": selection,
                        "members": [
                            {
                                "execution": "invoked",
                                "run_id": "retry-selection",
                                "bundle_ids": [
                                    "p2-neg8-reference-start__a0__quarantined",
                                    *selected_ids,
                                ],
                            }
                        ],
                    }
                )
                + "\n"
            )
            paths, _sources, conditions, _supersessions = (
                run_campaign_module._whole_window_campaign_membership(
                    runs_dir, binding.sha256
                )
            )
        self.assertEqual(paths, [])
        self.assertIn("whole_window_campaign_membership_unresolved", conditions)

    def test_anchor_freezes_first_eligible_repetition_in_execution_order(self) -> None:
        binding = run_campaign_module.load_campaign_policy(
            str(
                ROOT
                / "configs"
                / "campaign_policies"
                / "quiet_mac_p2_production.json"
            )
        )
        info = run_campaign_module.ConfigInfo(
            path=BASE_CONFIG,
            run_id="multi",
            raw_run_id="multi",
            repetitions=3,
        )
        clean_baseline = {
            "power_w_mean": 5.0,
            "power_w_stddev": 0.0,
            "duration_s": 30.0,
            "sample_count": 30,
            "telemetry_backend": "powermetrics",
            "idle_window_suspect": False,
        }
        clean_metadata = {
            "campaign_policy": {"sha256": binding.sha256},
            "environment_admission": {
                "critical_environment_passed": True,
                "decision": "admitted",
                "reference_provenance_present": True,
                "per_run_environment_evaluation": {
                    "snapshot_sha256": "a" * 64
                },
            },
        }
        r1 = run_campaign_module.MemberEvaluation(
            bundle_id="multi__r1",
            bundle_path=Path("multi__r1"),
            config_name="multi.json",
            status="succeeded",
            strict_valid=True,
            summary={"idle_baseline": clean_baseline},
            metadata=clean_metadata,
        )
        r3 = run_campaign_module.MemberEvaluation(
            bundle_id="multi__r3",
            bundle_path=Path("multi__r3"),
            config_name="multi.json",
            status="succeeded",
            strict_valid=True,
            summary={
                "idle_baseline": {
                    **clean_baseline,
                    "idle_window_suspect": True,
                }
            },
            metadata={
                **clean_metadata,
                "environment_admission": {
                    **clean_metadata["environment_admission"],
                    "decision": "flagged",
                },
            },
        )
        anchor = run_campaign_module._first_eligible_cooldown_anchor(
            [r1, r3],
            info,
            binding,
            source_kind="first_admission_passing_baseline",
        )
        self.assertIsNotNone(anchor)
        self.assertEqual(anchor["bundle_id"], "multi__r1")

    def test_environment_admission_claim_reason_is_not_cleared_by_waiver(self) -> None:
        summary = {
            "window_evidence_precheck": {
                "gross_request": {
                    "eligible": False,
                    "reasons": ["environment_admission_failed"],
                },
                "idle_subtracted_request": {
                    "eligible": False,
                    "reasons": ["environment_admission_failed"],
                },
                "throughput": {
                    "eligible": False,
                    "reasons": ["environment_admission_failed"],
                },
            }
        }
        waiver = run_campaign_module.Waiver(
            target_kind="bundle_id",
            target="flagged",
            reason="collection-only review",
            approver="owner",
            timestamp="2026-07-17T00:00:00Z",
            scope="any",
        )
        evaluation = run_campaign_module.MemberEvaluation(
            bundle_id="flagged",
            bundle_path=Path("flagged"),
            config_name="flagged.json",
            status="succeeded",
            strict_valid=True,
            claim_evidence_flags=run_campaign_module.claim_evidence_flags(summary),
            waiver=waiver,
            summary=summary,
        )
        self.assertIn(
            "environment_admission_failed",
            evaluation.unwaived_claim_evidence_flags(),
        )

    def test_doctor_config_warning_gate_blocks_unacknowledged_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(config_dir, "warn.json", "warn")
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            payload["workload_profile"]["output_tokenz"] = 64
            config_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(sentinel.exists())
            self.assertIn("DOCTOR CONFIG PREFLIGHT: 1 warning(s), unacknowledged", result.stdout)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(verdict["claim_readiness"]["verdict"], "not_assessed")
            preflight = verdict["preflight"]
            self.assertEqual(preflight["schema_version"], "joulewise.doctor.v1")
            acknowledgement = preflight["config_warning_acknowledgement"]
            self.assertTrue(acknowledgement["required"])
            self.assertFalse(acknowledgement["acknowledged"])
            self.assertEqual(acknowledgement["warnings"][0]["path"], "workload_profile.output_tokenz")

    def test_doctor_config_warning_acknowledgement_is_logged_and_allows_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(config_dir, "warn.json", "warn")
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            payload["sampling"]["power_hzz"] = 10.0
            config_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                ack_config_warnings=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DOCTOR CONFIG PREFLIGHT: 1 warning(s), acknowledged", result.stdout)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "usable")
            acknowledgement = verdict["preflight"]["config_warning_acknowledgement"]
            self.assertTrue(acknowledgement["acknowledged"])
            self.assertEqual(acknowledgement["mechanism"], "--ack-config-warnings")

    def test_discover_configs_excludes_order_and_analysis_manifest_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config_dir = Path(tmp)
            config = write_config(config_dir, "cell.json", "cell")
            (config_dir / "order_manifest.json").write_text("{}\n", encoding="utf-8")
            (config_dir / "analysis_manifest.json").write_text("{}\n", encoding="utf-8")

            self.assertEqual(run_campaign_module.discover_configs(config_dir), [config])

    def test_dry_run_executes_nothing_and_reports_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(config_dir, "one.json", "one", repetitions=5)
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)
            cli_cmd = cli_cmd_for(fake_cli)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd,
                dry_run=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(sentinel.exists())
            self.assertIn("Config files to execute:", result.stdout)
            self.assertIn(str(config_path), result.stdout)
            self.assertIn("Dry run", result.stdout)
            self.assertIn("dry_run one: would run", result.stdout)
            self.assertIn(str(fake_cli), result.stdout)
            self.assertIn(rendered_cli_command(cli_cmd, config_path, runs_dir), result.stdout)
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())

    def test_resume_skip_complete_experiment_records_member_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "complete.json", "complete-exp", repetitions=5
            )
            write_experiment(
                runs_dir, "complete-exp", 5, config_path=config_path
            )
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(sentinel.exists())
            self.assertIn("skipped complete-exp", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["skipped"])
            self.assertEqual(rows[0]["members_succeeded"], 5)
            self.assertEqual(rows[0]["members_total"], 5)

    def test_unvalidated_existing_summary_is_not_skippable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "complete.json", "complete")
            write_single_bundle(runs_dir, "complete")
            summary_path = runs_dir / "complete" / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["gross_energy_j"] = summary["gross_energy_j"] + 1.0
            summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 1)
            self.assertIn("not skippable", result.stderr)
            self.assertIn("fresh re-reduction", result.stderr)
            self.assertFalse((runs_dir / "order.log").exists())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            self.assertFalse(rows[0]["members"][0]["strict_valid"])

    def test_skipped_experiment_with_failed_member_fails_campaign(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir,
                "failed-member.json",
                "failed-member-exp",
                repetitions=5,
            )
            write_experiment(
                runs_dir,
                "failed-member-exp",
                5,
                statuses=["succeeded", "succeeded", "failed", "succeeded", "succeeded"],
                config_path=config_path,
            )
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            self.assertIn("not skippable", result.stderr)
            self.assertIn("failed-member-exp__r3", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            self.assertEqual(rows[0]["members_succeeded"], 4)
            self.assertEqual(rows[0]["members_total"], 5)

    def test_claim_waiver_is_visible_without_changing_usable_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "01-good.json", "good")
            write_config(config_dir, "02-idle.json", "idle")
            write_single_bundle(runs_dir, "good")
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "idle",
                            "reason": "manual idle-window review accepted",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "idle_window_suspect",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("COLLECTION VERDICT:", result.stdout)
            self.assertIn("verdict: usable", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["skipped", "skipped"])
            self.assertEqual(rows[1]["members"][0]["collection_classification"], "usable")
            self.assertEqual(rows[1]["members"][0]["claim_evidence_classification"], "flagged")
            self.assertEqual(rows[1]["members"][0]["waiver"]["scope"], "idle_window_suspect")
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            verdict = all_rows[-1]
            self.assertEqual(verdict["record_type"], "campaign_verdict")
            self.assertEqual(verdict["collection"]["verdict"], "usable")
            self.assertEqual(
                verdict["collection"]["categories"]["usable"], ["good", "idle"]
            )
            self.assertEqual(verdict["collection"]["categories"]["waived"], [])
            self.assertEqual(verdict["claim_readiness"]["verdict"], "not_assessed")

    def test_waiver_target_namespace_is_exact_and_does_not_poison_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "good.json", "bad")
            write_single_bundle(runs_dir, "bad", idle_window_suspect=True)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "good",
                            "reason": "wrong namespace must not match run_id or config",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "any",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "skipped")
            self.assertIsNone(rows[0]["members"][0].get("waiver"))

    def test_waiver_unknown_scope_class_fails_at_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "idle.json", "idle")
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "idle",
                            "reason": "typo scope must fail closed",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "idle_window_suspect,not_a_real_class",
                        }
                    ]
                )
            )
            fake_cli = make_fake_cli(tmp_path)
            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unknown scope class", result.stdout + result.stderr)

    def test_unmatched_claim_waiver_scope_does_not_change_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "idle.json", "idle")
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "idle",
                            "reason": "wrong failure class",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "status_failed",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "skipped")
            self.assertEqual(
                rows[0]["members"][0]["collection_classification"], "usable"
            )
            self.assertEqual(
                rows[0]["members"][0]["claim_evidence_classification"], "flagged"
            )
            self.assertIn(
                "idle_window_suspect",
                rows[0]["members"][0]["claim_evidence_flags"],
            )

    def test_duplicate_waiver_targets_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "good.json", "good")
            entry = {
                "config": "good.json",
                "reason": "duplicate",
                "approver": "council",
                "timestamp": "2026-07-08T00:00:00Z",
                "scope": "any",
            }
            duplicate = {**entry, "config": "good"}
            waivers.write_text(json.dumps([entry, duplicate]) + "\n", encoding="utf-8")

            result = run_campaign(config_dir, runs_dir, waivers=waivers)

            self.assertEqual(result.returncode, 2)
            self.assertIn("duplicate waiver target", result.stderr)

    def test_idle_suspect_member_is_collection_usable_but_claim_evidence_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "idle.json", "idle")
            write_single_bundle(runs_dir, "idle", idle_window_suspect=True)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "skipped")
            member = rows[0]["members"][0]
            self.assertEqual(member["collection_classification"], "usable")
            self.assertEqual(member["claim_evidence_classification"], "flagged")
            self.assertEqual(member["collection_integrity_flags"], [])
            self.assertIn("idle_window_suspect", member["claim_evidence_flags"])

    def test_all_waived_campaign_is_invalid_not_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "idle.json", "idle")
            write_single_bundle(runs_dir, "idle")
            summary_path = runs_dir / "idle" / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["gross_energy_j"] += 1.0
            summary_path.write_text(json.dumps(summary) + "\n", encoding="utf-8")
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "idle",
                            "reason": "strict-invalid member retained for collection audit",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "strict_invalid",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                waivers=waivers,
            )

            self.assertEqual(result.returncode, 1)
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            verdict = all_rows[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(verdict["collection"]["categories"]["waived"], ["idle"])

    def test_one_bundle_campaign_is_usable_and_claim_readiness_not_assessed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("COLLECTION VERDICT:", result.stdout)
            self.assertIn("CLAIM-INPUT READINESS:", result.stdout)
            self.assertNotIn("publish" + "able", result.stdout)
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(all_rows[-1]["record_type"], "campaign_verdict")
            self.assertEqual(
                all_rows[-1]["schema_version"], "joulewise.campaign_verdict.v2"
            )
            self.assertEqual(all_rows[-1]["collection"]["verdict"], "usable")
            self.assertEqual(
                all_rows[-1]["claim_readiness"]["verdict"], "not_assessed"
            )
            self.assertEqual(
                all_rows[-1]["collection"]["categories"]["usable"], ["one"]
            )
            self.assertEqual(
                all_rows[-1]["collection"]["categories"]["failed"], []
            )

    def test_current_era_claim_eligibility_only_never_becomes_ready(self) -> None:
        contrast = {
            "contrast_id": "ctr-b-minus-a",
            "metric": {"name": "gross_energy_j", "metric_tag": "gross_request"},
            "cell_a_id": "cell-a",
            "cell_b_id": "cell-b",
            "block_ids": ["block-1"],
        }
        state = run_campaign_module.AnalysisManifestState(
            path=Path("analysis_manifest.json"),
            raw={
                "design": {"sampling_plan": {"planned_n_blocks": 1}},
                "entries": [
                    {"run_id": "a", "block_id": "block-1", "cell_id": "cell-a"},
                    {"run_id": "b", "block_id": "block-1", "cell_id": "cell-b"},
                ],
                "contrasts": [contrast],
            },
            manifest_id="am-fixture",
            file_sha256="fixture",
        )
        legacy_named_summary = {
            "gross_energy_j": 1.0,
            "claim_eligibility": {
                "gross_request": {"eligible": True, "reasons": []}
            },
            "measurement_quality": {"idle_window_suspect": False},
        }
        evaluations = [
            run_campaign_module.MemberEvaluation(
                bundle_id=bundle_id,
                bundle_path=Path(bundle_id),
                config_name=f"{bundle_id}.json",
                status="succeeded",
                strict_valid=True,
                summary=legacy_named_summary,
                preceding_campaign_cooldown=cooldown,
            )
            for bundle_id, cooldown in (
                ("a", {"result": "first_run_exempt"}),
                (
                    "b",
                    {
                        "result": "recovered",
                        "raw_artifact": {
                            "path": "raw/fixture.jsonl",
                            "sha256": "fixture",
                            "records": 1,
                        },
                    },
                ),
            )
        ]

        readiness = run_campaign_module.claim_readiness_for(
            state, "usable", evaluations
        )

        self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
        self.assertIn("window_evidence_precheck_missing", readiness["reasons"])

    def test_metric_specific_precheck_routing_has_no_generic_request_alias(self) -> None:
        gross = {"eligible": True, "reasons": []}
        idle = {"eligible": False, "reasons": ["drift_term_unknown"]}
        summary = {
            "window_evidence_precheck": {
                "gross_request": gross,
                "idle_subtracted_request": idle,
            }
        }

        self.assertIs(
            run_campaign_module._precheck_for_contrast(
                summary,
                {"metric": {"name": "gross_energy_j", "metric_tag": "gross_request"}},
            ),
            gross,
        )
        self.assertIs(
            run_campaign_module._precheck_for_contrast(
                summary,
                {
                    "metric": {
                        "name": "idle_subtracted_energy_j",
                        "metric_tag": "idle_request",
                    }
                },
            ),
            idle,
        )
        self.assertNotIn("request", summary["window_evidence_precheck"])

        mutated_summary = {
            "gross_energy_j": 1.0,
            "idle_subtracted_energy_j": 1.0,
            "window_evidence_precheck": {
                "request": {"eligible": False, "reasons": ["drift_term_unknown"]},
                "gross_request": gross,
                "idle_subtracted_request": idle,
            },
            "measurement_quality": {"idle_window_suspect": True},
        }
        evaluation = run_campaign_module.MemberEvaluation(
            bundle_id="member",
            bundle_path=Path("member"),
            config_name="member.json",
            status="succeeded",
            strict_valid=True,
            summary=mutated_summary,
            preceding_campaign_cooldown={"result": "first_run_exempt"},
        )
        gross_reasons = run_campaign_module._member_readiness_reasons(
            evaluation,
            {"metric": {"name": "gross_energy_j", "metric_tag": "gross_request"}},
        )
        idle_reasons = run_campaign_module._member_readiness_reasons(
            evaluation,
            {
                "metric": {
                    "name": "idle_subtracted_energy_j",
                    "metric_tag": "idle_request",
                }
            },
        )
        self.assertNotIn("idle_window_suspect", gross_reasons)
        self.assertNotIn("drift_term_unknown", gross_reasons)
        self.assertIn("idle_window_suspect", idle_reasons)
        self.assertIn("drift_term_unknown", idle_reasons)

    def test_missing_nan_and_infinite_metric_fail_readiness(self) -> None:
        contrast = {
            "metric": {"name": "gross_energy_j", "metric_tag": "gross_request"}
        }
        for label, value in (
            ("missing", None),
            ("null", None),
            ("nan", float("nan")),
            ("inf", float("inf")),
        ):
            with self.subTest(value=label):
                summary = {
                    "window_evidence_precheck": {
                        "gross_request": {"eligible": True, "reasons": []}
                    },
                    "measurement_quality": {"idle_window_suspect": False},
                }
                if label != "missing":
                    summary["gross_energy_j"] = value
                evaluation = run_campaign_module.MemberEvaluation(
                    bundle_id="member",
                    bundle_path=Path("member"),
                    config_name="member.json",
                    status="succeeded",
                    strict_valid=True,
                    summary=summary,
                    preceding_campaign_cooldown={"result": "first_run_exempt"},
                )

                reasons = run_campaign_module._member_readiness_reasons(
                    evaluation, contrast
                )

                self.assertIn("metric_missing_or_nonfinite", reasons)

    def test_missing_campaign_cooldown_evidence_fails_closed_with_named_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_strict_analysis_campaign(config_dir, runs_dir)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "usable")
            readiness = verdict["claim_readiness"]
            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("campaign_cooldown_evidence_missing", readiness["reasons"])
            self.assertNotIn("idle_window_suspect", readiness["reasons"])
            self.assertEqual(readiness["ready_contrast_ids"], [])

    def test_cooldown_cap_hit_propagates_without_poisoning_collection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            evidence = {
                entry["run_id"]: "recovered" for entry in manifest["entries"]
            }
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            evidence[manifest["entries"][1]["run_id"]] = "cap_hit"
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "usable")
            self.assertEqual(
                verdict["claim_readiness"]["verdict"], "not_ready_for_analysis"
            )
            self.assertIn("cooldown_cap_hit", verdict["claim_readiness"]["reasons"])

    def test_explicit_campaign_cooldown_evidence_allows_ready_for_analysis(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            evidence = {
                entry["run_id"]: "recovered" for entry in manifest["entries"]
            }
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(
                verdict["claim_readiness"]["verdict"], "ready_for_analysis"
            )
            self.assertEqual(
                set(verdict["claim_readiness"]["ready_contrast_ids"]),
                {contrast["contrast_id"] for contrast in manifest["contrasts"]},
            )
            sampling_audit = verdict["sampling_audit"]
            self.assertEqual(
                set(sampling_audit),
                {
                    "design",
                    "planned_n_blocks",
                    "registered_bundle_ids",
                    "unregistered_matching_bundle_ids",
                    "valid_replacements",
                    "top_up_suspected",
                },
            )
            self.assertEqual(sampling_audit["unregistered_matching_bundle_ids"], [])
            self.assertEqual(sampling_audit["valid_replacements"], [])
            self.assertIs(sampling_audit["top_up_suspected"], False)
            self.assertNotIn("detection_scope", sampling_audit)
            self.assertNotIn("reasons", sampling_audit)

    def test_cleanup_suspect_waiver_is_visible_but_never_clears_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            target = next(entry for entry in manifest["entries"] if entry["role"] == "condition")
            target_bundle = runs_dir / target["run_id"]
            shutil.rmtree(target_bundle)
            write_single_bundle(
                runs_dir,
                target["run_id"],
                config_path=config_dir / target["config"],
                runtime_cleanup_ok=False,
                remote_cleanup_failed=["/remote/tmp/joulewise-task"],
            )
            suspect_summary = json.loads(
                (target_bundle / "summary_metrics.json").read_text(encoding="utf-8")
            )
            self.assertEqual(suspect_summary["status"], "succeeded")
            self.assertGreater(suspect_summary["energy_request_j"], 0.0)
            evidence = {entry["run_id"]: "recovered" for entry in manifest["entries"]}
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            write_prior_campaign_provenance(
                runs_dir, evidence, analysis_manifest_id(config_dir)
            )

            unwaived = run_campaign(config_dir, runs_dir)

            self.assertEqual(unwaived.returncode, 0, unwaived.stderr)
            first_verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(first_verdict["collection"]["verdict"], "usable")
            self.assertEqual(
                first_verdict["claim_readiness"]["verdict"],
                "not_ready_for_analysis",
            )
            self.assertIn(
                "required_error_term_unknown",
                first_verdict["claim_readiness"]["reasons"],
            )
            first_member = next(
                member
                for member in first_verdict["members"]
                if member["bundle_id"] == target["run_id"]
            )
            self.assertEqual(first_member["status"], "succeeded")
            self.assertIs(first_member["runtime_cleanup_ok"], False)
            self.assertEqual(
                first_member["remote_cleanup_failed"],
                ["/remote/tmp/joulewise-task"],
            )
            self.assertEqual(
                first_member["claim_evidence_flags"],
                ["remote_cleanup_failed", "runtime_cleanup_ok"],
            )

            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": target["run_id"],
                            "reason": "cleanup residue reviewed and bounded",
                            "approver": "campaign-owner",
                            "timestamp": "2026-07-11T00:00:00Z",
                            "scope": "runtime_cleanup_ok,remote_cleanup_failed",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            waived = run_campaign(config_dir, runs_dir, waivers=waivers)

            self.assertEqual(waived.returncode, 0, waived.stderr)
            second_verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(second_verdict["collection"]["verdict"], "usable")
            self.assertEqual(
                second_verdict["claim_readiness"]["verdict"],
                "not_ready_for_analysis",
            )
            self.assertIn(
                "required_error_term_unknown",
                second_verdict["claim_readiness"]["reasons"],
            )
            second_member = next(
                member
                for member in second_verdict["members"]
                if member["bundle_id"] == target["run_id"]
            )
            self.assertEqual(second_member["claim_evidence_classification"], "flagged")
            self.assertEqual(
                second_member["waiver"]["scope"],
                "runtime_cleanup_ok,remote_cleanup_failed",
            )
            provenance_rows = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in (runs_dir / "campaign_manifests").glob("*.json")
            ]
            provenance_row = next(
                row
                for row in provenance_rows
                if any(
                    item.get("waiver") is not None
                    for member in row["members"]
                    for item in member.get("claim_evidence", [])
                )
            )
            recorded = next(
                item
                for member in provenance_row["members"]
                for item in member["claim_evidence"]
                if item["bundle_id"] == target["run_id"]
            )
            self.assertEqual(recorded["waiver"], second_member["waiver"])

    def test_cleanup_claim_waiver_does_not_skip_shakedown_or_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            waivers = tmp_path / "waivers.json"
            backup = tmp_path / "backup.sh"
            config_dir.mkdir()
            config_path = write_config(config_dir, "cleanup.json", "cleanup")
            write_single_bundle(
                runs_dir,
                "cleanup",
                config_path=config_path,
                runtime_cleanup_ok=False,
                remote_cleanup_failed=["/remote/tmp/joulewise-task"],
            )
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "bundle_id": "cleanup",
                            "reason": "collection may continue after visible review",
                            "approver": "campaign-owner",
                            "timestamp": "2026-07-11T00:00:00Z",
                            "scope": "runtime_cleanup_ok,remote_cleanup_failed",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            completed = subprocess.CompletedProcess([], 0)
            argv = [
                str(config_dir),
                "--runs-dir",
                str(runs_dir),
                "--backup",
                str(backup),
                "--shakedown-gate",
                "production_uncertainty_v1",
                "--waivers",
                str(waivers),
                "--campaign-policy",
                str(TEST_CAMPAIGN_POLICY),
            ]
            with (
                patch("run_campaign_module.validate_bundle", return_value=[]),
                patch("run_campaign_module.subprocess.run", return_value=completed),
                patch(
                    "run_campaign_module.assert_production_uncertainty",
                    return_value={"bundle_id": "cleanup", "request_eligible": True},
                ),
                patch("run_campaign_module.backup_runs", return_value=0) as backup_runs,
                redirect_stdout(io.StringIO()),
                redirect_stderr(io.StringIO()),
            ):
                result = run_campaign_module.main(argv)

            self.assertEqual(result, 0)
            backup_runs.assert_called_once_with(runs_dir, backup)
            rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            gate = next(row for row in rows if row.get("record_type") == "shakedown_gate")
            campaign = next(row for row in rows if row.get("run_id") == "cleanup")
            self.assertEqual(gate["status"], "passed")
            self.assertEqual(campaign["status"], "skipped")
            self.assertEqual(
                campaign["members"][0]["collection_classification"], "usable"
            )
            self.assertEqual(
                campaign["members"][0]["claim_evidence_classification"], "flagged"
            )

    def test_ratio_readiness_reuses_engine_token_denominator_gate(self) -> None:
        ratio = {
            "form": "mean_of_request_ratios",
            "numerator_metric": "energy_request_j",
            "denominator": "runtime_observed_output_tokens",
            "denominator_unit": "token",
            "tokenizer_scope": "same_identity_required",
            "output_policy_scope": "same_policy_required",
        }
        contrast = {
            "contrast_id": "ratio-contrast",
            "metric": {
                "name": "energy_output_token_j",
                "metric_tag": "energy_output_token",
                "window_class": "idle_subtracted_request",
                "unit": "J/token",
                "ratio_estimand": ratio,
            },
            "cell_a_id": "cell-a",
            "cell_b_id": "cell-b",
            "block_ids": ["block-1"],
        }
        state = run_campaign_module.AnalysisManifestState(
            path=Path("analysis_manifest.json"),
            raw={
                "design": {"sampling_plan": {"planned_n_blocks": 1}},
                "entries": [
                    {"run_id": "a", "block_id": "block-1", "cell_id": "cell-a"},
                    {"run_id": "b", "block_id": "block-1", "cell_id": "cell-b"},
                ],
                "contrasts": [contrast],
            },
            manifest_id="ratio-fixture",
            file_sha256="fixture",
        )
        summary = {
            "energy_request_j": 2.0,
            "window_evidence_precheck": {
                "idle_subtracted_request": {"eligible": True, "reasons": []}
            },
            "measurement_quality": {"idle_window_suspect": False},
        }
        valid_provenance = {
            "output_tokens": 2,
            "token_count_source": "runtime_observed",
            "stop_reason": "requested_tokens_emitted",
            "output_policy": {
                "name": "fixed_budget_exact",
                "requested_tokens": 2,
                "sampler": None,
            },
            "tokenizer_identity": {"backend": "mock", "identifier": "tok"},
        }
        evaluations = [
            run_campaign_module.MemberEvaluation(
                bundle_id=bundle_id,
                bundle_path=Path(bundle_id),
                config_name=f"{bundle_id}.json",
                status="succeeded",
                strict_valid=True,
                summary=summary,
                ratio_token_provenance={
                    **valid_provenance,
                    **({"token_count_source": "config_fallback"} if bundle_id == "b" else {}),
                },
                preceding_campaign_cooldown={"result": "first_run_exempt"},
            )
            for bundle_id in ("a", "b")
        ]

        readiness = run_campaign_module.claim_readiness_for(
            state, "usable", evaluations
        )

        self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
        self.assertIn("runtime_token_denominator_required", readiness["reasons"])
        self.assertNotIn("metric_missing_or_nonfinite", readiness["reasons"])
        self.assertNotIn("window_evidence_precheck_missing", readiness["reasons"])

    def test_existing_resume_provenance_does_not_shadow_invoked_cooldown_evidence(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            first_contrast = manifest["contrasts"][0]
            first_inferential_entry = next(
                entry
                for entry in manifest["entries"]
                if entry["cell_id"] == first_contrast["cell_a_id"]
                and entry["block_id"] == first_contrast["block_ids"][0]
            )
            evidence = {first_inferential_entry["run_id"]: "first_run_exempt"}
            evidence.update(
                {
                    entry["run_id"]: "recovered"
                    for entry in manifest["entries"]
                    if entry["run_id"] != first_inferential_entry["run_id"]
                }
            )
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )
            manifest_dir = runs_dir / "campaign_manifests"
            (manifest_dir / "fixture.json").rename(
                manifest_dir / "campaign-00000000T000000000000Z-p0.json"
            )

            first_resume = run_campaign(config_dir, runs_dir)
            second_resume = run_campaign(config_dir, runs_dir)

            self.assertEqual(first_resume.returncode, 0, first_resume.stderr)
            self.assertEqual(second_resume.returncode, 0, second_resume.stderr)
            verdicts = [
                row
                for row in read_all_jsonl(runs_dir / "campaign_log.jsonl")
                if "claim_readiness" in row
            ]
            self.assertEqual(
                [row["claim_readiness"]["verdict"] for row in verdicts[-2:]],
                ["ready_for_analysis", "ready_for_analysis"],
            )
            resumed_provenance = [
                json.loads(path.read_text(encoding="utf-8"))
                for path in sorted(manifest_dir.glob("campaign-202*.json"))
            ]
            self.assertEqual(len(resumed_provenance), 2)
            for provenance in resumed_provenance:
                self.assertTrue(provenance["members"])
                self.assertTrue(
                    all(
                        member["execution"] == "existing"
                        and member["preceding_campaign_cooldown"] is None
                        for member in provenance["members"]
                    )
                )

    def test_non_invoked_provenance_cannot_originate_cooldown_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir)
            evidence = {
                entry["run_id"]: "recovered" for entry in manifest["entries"]
            }
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )
            provenance_path = runs_dir / "campaign_manifests" / "fixture.json"
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            for member in provenance["members"]:
                member["execution"] = "existing"
            provenance_path.write_text(
                json.dumps(provenance) + "\n",
                encoding="utf-8",
            )

            self.assertEqual(
                run_campaign_module.prior_campaign_cooldown_evidence(
                    runs_dir, manifest["manifest_id"]
                ),
                {},
            )

    def test_recovered_cooldown_without_raw_provenance_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            evidence = {
                entry["run_id"]: "recovered" for entry in manifest["entries"]
            }
            evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
            write_prior_campaign_provenance(
                runs_dir,
                evidence,
                analysis_manifest_id(config_dir),
            )
            provenance = json.loads(
                (runs_dir / "campaign_manifests" / "fixture.json").read_text(
                    encoding="utf-8"
                )
            )
            raw_path = next(
                member["preceding_campaign_cooldown"]["raw_artifact"]["path"]
                for member in provenance["members"]
                if "raw_artifact" in member["preceding_campaign_cooldown"]
            )
            (runs_dir / "campaign_manifests" / raw_path).unlink()

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            readiness = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1][
                "claim_readiness"
            ]
            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("campaign_cooldown_evidence_missing", readiness["reasons"])

    def test_nonexistent_nonhex_cooldown_descriptor_has_readiness_objection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            evaluation = run_campaign_module.MemberEvaluation(
                bundle_id="member",
                bundle_path=runs_dir / "member",
                config_name="member.json",
                status="succeeded",
                strict_valid=True,
                summary={
                    "gross_energy_j": 1.0,
                    "window_evidence_precheck": {
                        "gross_request": {"eligible": True, "reasons": []}
                    },
                    "measurement_quality": {"idle_window_suspect": False},
                },
                preceding_campaign_cooldown={
                    "result": "recovered",
                    "raw_artifact": {
                        "path": "raw/nonexistent.jsonl",
                        "sha256": "not-a-hex-digest",
                        "records": 1,
                    },
                },
            )

            reasons = run_campaign_module._member_readiness_reasons(
                evaluation,
                {"metric": {"name": "gross_energy_j", "metric_tag": "gross_request"}},
            )

            self.assertNotEqual(reasons, [])
            self.assertIn("campaign_cooldown_evidence_missing", reasons)

    def test_fresh_cooldown_raw_provenance_is_reverified_at_verdict_time(self) -> None:
        for mutation in (
            "valid",
            "hash_mismatch",
            "count_mismatch",
            "malformed_jsonl",
        ):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                runs_dir = Path(tmp) / "runs"
                provenance_path = runs_dir / "campaign_manifests" / "fresh.json"
                raw_artifact = run_campaign_module._write_campaign_cooldown_trace(
                    provenance_path,
                    "member",
                    [
                        {
                            "rolling_mean_power_w": 5.0,
                            "release": True,
                            "release_criteria_met_late": False,
                        }
                    ],
                )
                raw_path = provenance_path.parent / raw_artifact["path"]
                if mutation == "hash_mismatch":
                    raw_path.write_text('{"rolling_mean_power_w": 6.0}\n', encoding="utf-8")
                elif mutation == "count_mismatch":
                    raw_artifact["records"] = 2
                elif mutation == "malformed_jsonl":
                    payload = b'{"rolling_mean_power_w":\n'
                    raw_path.write_bytes(payload)
                    raw_artifact["sha256"] = hashlib.sha256(payload).hexdigest()
                evaluation = run_campaign_module.MemberEvaluation(
                    bundle_id="member",
                    bundle_path=runs_dir / "member",
                    config_name="member.json",
                    status="succeeded",
                    strict_valid=True,
                    summary={
                        "gross_energy_j": 1.0,
                        "window_evidence_precheck": {
                            "gross_request": {"eligible": True, "reasons": []}
                        },
                        "measurement_quality": {"idle_window_suspect": False},
                    },
                    preceding_campaign_cooldown={
                        "result": "recovered",
                        "raw_artifact": raw_artifact,
                    },
                )

                reasons = run_campaign_module._member_readiness_reasons(
                    evaluation,
                    {
                        "metric": {
                            "name": "gross_energy_j",
                            "metric_tag": "gross_request",
                        }
                    },
                )

                if mutation == "valid":
                    self.assertNotIn("campaign_cooldown_evidence_missing", reasons)
                else:
                    self.assertIn("campaign_cooldown_evidence_missing", reasons)

    def test_cooldown_verifier_authenticates_raw_terminal_disposition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            manifest_dir = Path(tmp) / "campaign_manifests"
            raw_dir = manifest_dir / "raw"
            raw_dir.mkdir(parents=True)
            fixture_events = Path("tests/fixtures/d078_r01/events.jsonl").read_bytes()
            cases = (
                ("workload", fixture_events, "recovered", False),
                (
                    "cap",
                    (
                        json.dumps(
                            {"release": False, "release_criteria_met_late": True}
                        )
                        + "\n"
                    ).encode(),
                    "recovered",
                    False,
                ),
                (
                    "honest-cap",
                    (
                        json.dumps(
                            {"release": False, "release_criteria_met_late": True}
                        )
                        + "\n"
                    ).encode(),
                    "cap_hit",
                    True,
                ),
            )
            for name, payload, claim, accepted in cases:
                path = raw_dir / f"{name}.jsonl"
                path.write_bytes(payload)
                cooldown = {
                    "result": claim,
                    "raw_artifact": {
                        "path": f"raw/{name}.jsonl",
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "records": len(payload.splitlines()),
                    },
                }
                with self.subTest(name=name):
                    self.assertEqual(
                        run_campaign_module.verify_cooldown_raw_provenance(
                            cooldown, manifest_dir
                        ),
                        accepted,
                    )

    def test_cooldown_provenance_symlink_loop_fails_closed(self) -> None:
        # Path.resolve() may raise (RuntimeError, or OSError ELOOP depending
        # on Python version) for a symlink loop; the verifier must return a
        # fail-closed False, never abort verdict construction.
        with tempfile.TemporaryDirectory() as tmp:
            manifest_dir = Path(tmp) / "campaign_manifests"
            raw_dir = manifest_dir / "raw"
            raw_dir.mkdir(parents=True)
            loop = raw_dir / "loop.jsonl"
            loop.symlink_to(loop)

            self.assertFalse(
                run_campaign_module.verify_cooldown_raw_provenance(
                    {
                        "result": "recovered",
                        "raw_artifact": {
                            "path": "raw/loop.jsonl",
                            "sha256": "0" * 64,
                            "records": 1,
                        },
                    },
                    manifest_dir,
                )
            )

    def test_resumed_cooldown_hash_and_count_mismatches_block_readiness(self) -> None:
        for mutation in ("hash_mismatch", "count_mismatch"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                config_dir = tmp_path / "configs"
                runs_dir = tmp_path / "runs"
                config_dir.mkdir()
                manifest = write_strict_analysis_campaign(config_dir, runs_dir)
                evidence = {
                    entry["run_id"]: "recovered" for entry in manifest["entries"]
                }
                evidence[manifest["entries"][0]["run_id"]] = "first_run_exempt"
                write_prior_campaign_provenance(
                    runs_dir,
                    evidence,
                    analysis_manifest_id(config_dir),
                )
                provenance_path = runs_dir / "campaign_manifests" / "fixture.json"
                if mutation == "hash_mismatch":
                    provenance = json.loads(
                        provenance_path.read_text(encoding="utf-8")
                    )
                    raw_path = next(
                        member["preceding_campaign_cooldown"]["raw_artifact"]["path"]
                        for member in provenance["members"]
                        if "raw_artifact" in member["preceding_campaign_cooldown"]
                    )
                    (provenance_path.parent / raw_path).write_text(
                        '{"rolling_mean_power_w": 6.0, "release": true, '
                        '"release_criteria_met_late": false}\n',
                        encoding="utf-8",
                    )
                else:
                    provenance = json.loads(
                        provenance_path.read_text(encoding="utf-8")
                    )
                    for member in provenance["members"]:
                        raw_artifact = member["preceding_campaign_cooldown"].get(
                            "raw_artifact"
                        )
                        if raw_artifact is not None:
                            raw_artifact["records"] = 2
                    provenance_path.write_text(
                        json.dumps(provenance) + "\n", encoding="utf-8"
                    )

                result = run_campaign(config_dir, runs_dir)

                self.assertEqual(result.returncode, 0, result.stderr)
                readiness = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1][
                    "claim_readiness"
                ]
                self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
                self.assertIn(
                    "campaign_cooldown_evidence_missing", readiness["reasons"]
                )

    def test_all_members_cannot_claim_one_session_first_run_exemption(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir, runs_dir)
            write_malformed_first_exemption_provenance(
                runs_dir, manifest, fan_out_one_note=False
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            readiness = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1][
                "claim_readiness"
            ]
            self.assertEqual(readiness["verdict"], "not_ready_for_analysis")
            self.assertIn("campaign_cooldown_evidence_missing", readiness["reasons"])

    def test_first_run_exemption_note_cannot_fan_out_to_unrelated_members(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir)
            write_malformed_first_exemption_provenance(
                runs_dir, manifest, fan_out_one_note=True
            )

            evidence = run_campaign_module.prior_campaign_cooldown_evidence(
                runs_dir, manifest["manifest_id"]
            )

            self.assertEqual(
                set(evidence),
                {entry["run_id"] for entry in manifest["entries"]},
            )
            self.assertTrue(
                all(note["result"] == "unknown" for note in evidence.values())
            )
            self.assertTrue(
                all("physical-session" in note["reason"] for note in evidence.values())
            )

    def test_analysis_manifest_config_hash_mismatch_refuses_execution(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sentinel = tmp_path / "invoked"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir)
            config_path = config_dir / manifest["entries"][0]["config"]
            payload = json.loads(config_path.read_text(encoding="utf-8"))
            payload["run_metadata"]["notes"] = "tampered after freeze"
            config_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path, sentinel=sentinel)

            result = run_campaign(
                config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli)
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertIn("config_hash_mismatch", verdict["claim_readiness"]["reasons"])

    def test_readiness_preflight_uses_real_validator_for_fixed_n_mutation(self) -> None:
        from joulewise.analysis_manifest import calculate_manifest_id

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sentinel = tmp_path / "invoked"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(config_dir)
            manifest["design"]["sampling_plan"]["planned_n_blocks"] = 1
            for contrast in manifest["contrasts"]:
                contrast["block_ids"] = contrast["block_ids"][:1]
            manifest["manifest_id"] = calculate_manifest_id(manifest)
            (config_dir / "analysis_manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
            )
            fake_cli = make_fake_cli(tmp_path, sentinel=sentinel)

            result = run_campaign(
                config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli)
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(
                verdict["claim_readiness"]["verdict"],
                "not_ready_for_analysis",
            )
            self.assertIn(
                "analysis_manifest_invalid",
                verdict["claim_readiness"]["reasons"],
            )

    def test_malformed_analysis_manifest_is_not_assessed_as_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            (config_dir / "analysis_manifest.json").write_text("{}\n", encoding="utf-8")

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1, result.stderr)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(
                verdict["claim_readiness"]["verdict"],
                "not_ready_for_analysis",
            )
            self.assertIn(
                "analysis_manifest_invalid",
                verdict["claim_readiness"]["reasons"],
            )

    def test_campaign_provenance_records_first_run_exemption_and_unknown_mock_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            manifest = write_strict_analysis_campaign(
                config_dir, telemetry_backend="mock"
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            manifests = list((runs_dir / "campaign_manifests").glob("*.json"))
            self.assertEqual(len(manifests), 1)
            provenance = json.loads(manifests[0].read_text(encoding="utf-8"))
            first_run_id = manifest["entries"][0]["run_id"]
            second_run_id = manifest["entries"][1]["run_id"]
            self.assertEqual(provenance["first_physical_run_id"], first_run_id)
            members = {
                member["run_id"]: member for member in provenance["members"]
            }
            self.assertEqual(
                members[first_run_id]["preceding_campaign_cooldown"]["result"],
                "first_run_exempt",
            )
            first_cooldown = members[first_run_id]["preceding_campaign_cooldown"]
            self.assertEqual(first_cooldown["policy_version"], "cooldown-v2")
            self.assertEqual(first_cooldown["thresholds"]["sustained_window_s"], 2.0)
            self.assertEqual(first_cooldown["window_coverage_s"], 0.0)
            self.assertIsNone(first_cooldown["thermal_nominal"])
            self.assertEqual(
                first_cooldown["release_criterion"]["window"],
                "complete_sustained_span_and_minimum_coverage",
            )
            second = members[second_run_id]["preceding_campaign_cooldown"]
            self.assertEqual(second["result"], "unknown")
            self.assertIn("mock telemetry", second["reason"])

    def test_v2_writer_outcomes_and_snapshot_attestations(self) -> None:
        from joulewise.campaign_provenance import (
            CAMPAIGN_PROVENANCE_SCHEMA_V2,
            load_authenticated_campaign_catalog,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_dir = root / "runs"
            custom_log = root / "external" / "campaign.jsonl"
            info = run_campaign_module.ConfigInfo(
                path=root / "source.json",
                run_id="source",
                raw_run_id="source",
                repetitions=2,
            )
            lock_context = held_campaign_lock(runs_dir)
            lock_context.__enter__()
            self.addCleanup(lock_context.__exit__, None, None, None)
            path, manifest = run_campaign_module.new_campaign_provenance(
                root, runs_dir, None, log_path=custom_log
            )
            usable = run_campaign_module.MemberEvaluation(
                bundle_id="usable",
                bundle_path=root / "usable",
                config_name="source.json",
                status="succeeded",
                strict_valid=True,
            )
            waiver = run_campaign_module.Waiver(
                target_kind="bundle_id",
                target="waived",
                reason="fixture waiver",
                approver="test",
                timestamp="2026-08-01T12:00:00Z",
                scope="any",
            )
            waived = run_campaign_module.MemberEvaluation(
                bundle_id="waived",
                bundle_path=root / "waived",
                config_name="source.json",
                status="failed",
                strict_valid=False,
                waiver=waiver,
            )
            failed = run_campaign_module.MemberEvaluation(
                bundle_id="failed",
                bundle_path=root / "failed",
                config_name="source.json",
                status="failed",
                strict_valid=False,
            )

            def record(
                bundle_ids: list[str],
                evaluations: list,
                *,
                execution: str = "existing",
                existing_incomplete: bool = False,
                existing_invalid: bool = False,
            ) -> None:
                run_campaign_module.record_campaign_member_provenance(
                    path,
                    manifest,
                    info=info,
                    bundle_ids=bundle_ids,
                    evaluations=evaluations,
                    execution=execution,
                    cooldown=None,
                    existing_incomplete=existing_incomplete,
                    existing_invalid=existing_invalid,
                    log_path=custom_log,
                )

            record(["usable"], [usable])
            record(["waived"], [waived])
            record(["failed"], [failed])
            record(["partial"], [failed], existing_incomplete=True)
            record(["usable", "failed"], [usable, failed])
            record(["usable", "waived"], [usable, waived])
            record(["usable"], [usable], existing_invalid=True)
            record(["usable"], [usable], execution="invoked")
            record(["blocked"], [], execution="blocked_before_invoke")

            persisted = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(
                persisted["schema_version"], CAMPAIGN_PROVENANCE_SCHEMA_V2
            )
            self.assertEqual(
                [member.get("outcome") for member in persisted["members"][:7]],
                [
                    "usable",
                    "waived",
                    "failed",
                    "incomplete",
                    "failed",
                    "waived",
                    "failed",
                ],
            )
            self.assertNotIn("outcome", persisted["members"][7])
            self.assertNotIn("outcome", persisted["members"][8])

            run_campaign_module.write_campaign_provenance(
                path, manifest, custom_log
            )
            wire_rows = read_wire_jsonl(custom_log)
            attestations = [
                row
                for row in wire_rows
                if row.get("record_type") == "campaign_provenance_attestation"
            ]
            self.assertEqual(len(attestations), 10)
            current_sha = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(
                sum(
                    row["campaign_provenance_manifest_sha256"] == current_sha
                    for row in attestations
                ),
                1,
            )
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())
            self.assertIsNone(load_authenticated_campaign_catalog(runs_dir))
            self.assertIsNotNone(
                load_authenticated_campaign_catalog(runs_dir, custom_log)
            )

    def test_v2_writer_equality_branch_is_concurrently_idempotent(self) -> None:
        from joulewise.campaign_provenance import (
            load_authenticated_campaign_catalog,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_dir = root / "runs"
            path = runs_dir / "campaign_manifests" / "equality.json"
            path.parent.mkdir(parents=True)
            manifest = {
                "schema_version": "joulewise.campaign_provenance.v2",
                "session_id": "equality-session",
                "members": [
                    {
                        "execution": "invoked",
                        "run_id": "member",
                        "bundle_ids": ["member"],
                    }
                ],
            }
            payload = (
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")
            path.write_bytes(payload)
            log_path = runs_dir / "campaign_log.jsonl"

            with held_campaign_lock(runs_dir), ThreadPoolExecutor(
                max_workers=2
            ) as executor:
                futures = [
                    executor.submit(
                        run_campaign_module.write_campaign_provenance,
                        path,
                        manifest,
                        log_path,
                    )
                    for _ in range(2)
                ]
                for future in futures:
                    future.result()

            rows = read_wire_jsonl(log_path)
            self.assertEqual(len(rows), 1)
            self.assertEqual(
                rows[0]["campaign_provenance_manifest_sha256"],
                hashlib.sha256(payload).hexdigest(),
            )
            self.assertIsNotNone(load_authenticated_campaign_catalog(runs_dir))

    def test_v2_wal_faults_never_publish_an_unattested_snapshot(self) -> None:
        from joulewise.campaign_provenance import (
            load_authenticated_campaign_catalog,
        )

        for stage in ("tmp_write", "tmp_fsync", "attest", "replace"):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as tmp:
                runs_dir = Path(tmp) / "runs"
                path = runs_dir / "campaign_manifests" / "faulted.json"
                manifest = {
                    "schema_version": "joulewise.campaign_provenance.v2",
                    "session_id": "faulted-session",
                    "members": [
                        {
                            "execution": "invoked",
                            "run_id": "faulted",
                            "bundle_ids": ["faulted"],
                        }
                    ],
                }
                owner, attribute = {
                    "tmp_write": (
                        run_campaign_module,
                        "_write_campaign_provenance_tmp",
                    ),
                    "tmp_fsync": (run_campaign_module.os, "fsync"),
                    "attest": (
                        run_campaign_module,
                        "_append_campaign_provenance_attestation_if_missing",
                    ),
                    "replace": (run_campaign_module.os, "replace"),
                }[stage]
                with held_campaign_lock(runs_dir), patch.object(
                    owner, attribute, side_effect=OSError(f"injected {stage}")
                ):
                    with self.assertRaisesRegex(OSError, f"injected {stage}"):
                        run_campaign_module.write_campaign_provenance(
                            path, manifest
                        )

                self.assertFalse(path.exists())
                leftover_tmp = path.parent / f".{path.name}.tmp-dead-process"
                leftover_tmp.write_bytes(b"crash-left tmp bytes")
                driver = textwrap.dedent(
                    """
                    import json
                    import os
                    import sys
                    from pathlib import Path
                    from scripts import run_campaign

                    runs_dir = Path(sys.argv[1])
                    leftover_tmp = Path(sys.argv[2])
                    lock_token = run_campaign.acquire_campaign_lock(runs_dir)
                    try:
                        fresh_path, fresh = run_campaign.new_campaign_provenance(
                            runs_dir.parent, runs_dir, None
                        )
                        fresh["members"] = [{
                            "execution": "invoked",
                            "run_id": "fresh-child",
                            "bundle_ids": ["fresh-child"],
                        }]
                        run_campaign.write_campaign_provenance(
                            fresh_path, fresh
                        )
                        print(json.dumps({
                            "pid": os.getpid(),
                            "session_id": fresh["session_id"],
                            "manifest_path": str(fresh_path),
                            "lock_existed_while_held": getattr(
                                lock_token, "lock_path", lock_token
                            ).is_file(),
                            "leftover_tmp_existed": leftover_tmp.is_file(),
                        }, sort_keys=True))
                    finally:
                        run_campaign.release_campaign_lock(lock_token)
                    """
                )
                completed = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        driver,
                        str(runs_dir),
                        str(leftover_tmp),
                    ],
                    cwd=ROOT,
                    text=True,
                    capture_output=True,
                    timeout=COMMAND_TIMEOUT_S,
                    check=False,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr)
                child = json.loads(completed.stdout)
                self.assertNotEqual(child["pid"], os.getpid())
                self.assertTrue(child["session_id"].endswith(f"-p{child['pid']}"))
                self.assertTrue(child["lock_existed_while_held"])
                self.assertTrue(child["leftover_tmp_existed"])
                fresh_path = Path(child["manifest_path"])
                self.assertTrue(fresh_path.is_file())
                self.assertTrue(leftover_tmp.is_file())
                self.assertFalse((runs_dir / "campaign.lock").exists())
                catalog = load_authenticated_campaign_catalog(runs_dir)
                self.assertIsNotNone(catalog)
                assert catalog is not None
                self.assertEqual([row.path for row in catalog], [fresh_path])

    def test_v2_a_b_a_content_revisit_reuses_existing_attestation(self) -> None:
        from joulewise.campaign_provenance import (
            load_authenticated_campaign_catalog,
        )

        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            path = runs_dir / "campaign_manifests" / "revisit.json"
            manifest = {
                "schema_version": "joulewise.campaign_provenance.v2",
                "session_id": "revisit-session",
                "members": [],
            }
            payloads = []
            with held_campaign_lock(runs_dir):
                for run_id in ("a", "b", "a"):
                    manifest["members"] = [
                        {
                            "execution": "invoked",
                            "run_id": run_id,
                            "bundle_ids": [run_id],
                        }
                    ]
                    payloads.append(
                        (
                            json.dumps(manifest, indent=2, sort_keys=True) + "\n"
                        ).encode("utf-8")
                    )
                    run_campaign_module.write_campaign_provenance(path, manifest)

            rows = read_wire_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(len(rows), 2)
            self.assertEqual(
                [
                    row["campaign_provenance_manifest_sha256"]
                    for row in rows
                ],
                [
                    hashlib.sha256(payloads[0]).hexdigest(),
                    hashlib.sha256(payloads[1]).hexdigest(),
                ],
            )
            self.assertIsNotNone(load_authenticated_campaign_catalog(runs_dir))

    def test_operator_repair_heals_only_lineage_proven_legacy_strand(self) -> None:
        from joulewise.campaign_provenance import (
            load_authenticated_campaign_catalog,
        )

        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            path = runs_dir / "campaign_manifests" / "legacy-strand.json"
            manifest = {
                "schema_version": "joulewise.campaign_provenance.v2",
                "session_id": "legacy-session",
                "members": [
                    {
                        "execution": "invoked",
                        "run_id": "a",
                        "bundle_ids": ["a"],
                    }
                ],
            }
            with held_campaign_lock(runs_dir):
                run_campaign_module.write_campaign_provenance(path, manifest)
            manifest["members"][0]["run_id"] = "b"
            manifest["members"][0]["bundle_ids"] = ["b"]
            stranded = (
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")
            path.write_bytes(stranded)
            log_path = runs_dir / "campaign_log.jsonl"
            before_reader = log_path.read_bytes()

            self.assertIsNone(load_authenticated_campaign_catalog(runs_dir))
            self.assertEqual(log_path.read_bytes(), before_reader)

            fresh_path = runs_dir / "campaign_manifests" / "new-session.json"
            fresh = {
                "schema_version": "joulewise.campaign_provenance.v2",
                "session_id": "new-session",
                "members": [
                    {
                        "execution": "invoked",
                        "run_id": "fresh",
                        "bundle_ids": ["fresh"],
                    }
                ],
            }
            with held_campaign_lock(runs_dir):
                run_campaign_module.write_campaign_provenance(fresh_path, fresh)
            self.assertIsNone(load_authenticated_campaign_catalog(runs_dir))

            repaired = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "repair-campaign-provenance",
                    "--runs-dir",
                    str(runs_dir),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=COMMAND_TIMEOUT_S,
                check=False,
            )
            self.assertEqual(repaired.returncode, 0, repaired.stderr)
            report = json.loads(repaired.stdout)
            self.assertEqual(report["status"], "repaired")
            self.assertEqual(report["repaired"], [str(path)])
            self.assertIsNotNone(load_authenticated_campaign_catalog(runs_dir))
            current_sha = hashlib.sha256(stranded).hexdigest()
            self.assertEqual(
                sum(
                    row.get("campaign_provenance_manifest_sha256") == current_sha
                    for row in read_wire_jsonl(log_path)
                ),
                1,
            )

    def test_operator_repair_refuses_lineage_less_relabel_probe(self) -> None:
        from joulewise.campaign_provenance import (
            load_authenticated_campaign_catalog,
        )

        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            path = runs_dir / "campaign_manifests" / "relabelled.json"
            path.parent.mkdir(parents=True)
            manifest = {
                "schema_version": "joulewise.campaign_provenance.v2",
                "session_id": "relabelled-session",
                "members": [
                    {
                        "execution": "existing",
                        "outcome": "usable",
                        "config": "member.json",
                        "run_id": "member",
                        "bundle_ids": ["member"],
                    }
                ],
            }
            path.write_text(json.dumps(manifest) + "\n", encoding="utf-8")
            output = io.StringIO()
            with redirect_stdout(output):
                code = run_campaign_module.main(
                    [
                        "repair-campaign-provenance",
                        "--runs-dir",
                        str(runs_dir),
                    ]
                )
            self.assertEqual(code, 1)
            report = json.loads(output.getvalue())
            self.assertEqual(report["status"], "refused")
            self.assertEqual(
                report["refused"],
                [{"path": str(path), "reason": "lineage_unproven"}],
            )
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())
            self.assertIsNone(load_authenticated_campaign_catalog(runs_dir))

    def test_writer_requires_lock_and_strict_mint_path_grammar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            manifest = {
                "schema_version": "joulewise.campaign_provenance.v2",
                "session_id": "grammar-session",
                "members": [],
            }
            valid = runs_dir / "campaign_manifests" / "A-valid_1.thing.json"
            with self.assertRaisesRegex(RuntimeError, "requires held lock"):
                run_campaign_module.write_campaign_provenance(valid, manifest)
            with held_campaign_lock(runs_dir):
                run_campaign_module.write_campaign_provenance(valid, manifest)
            self.assertTrue(valid.is_file())

            invalid_names = (
                ".leading.json",
                "unicodé.json",
                "back\\slash.json",
                "line\nbreak.json",
                ("a" * 252) + ".json",
            )
            with held_campaign_lock(runs_dir):
                for name in invalid_names:
                    with self.subTest(name=name), self.assertRaisesRegex(
                        ValueError, "strict grammar"
                    ):
                        run_campaign_module.write_campaign_provenance(
                            runs_dir / "campaign_manifests" / name,
                            {**manifest, "session_id": f"invalid-{len(name)}"},
                        )

    def test_post_window_commands_refuse_while_campaign_lock_is_held(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_dir = root / "runs"
            runs_dir.mkdir()
            quarantine = root / "quarantine"
            quarantine.mkdir()
            commands = (
                [
                    "--record-supersession",
                    "bundle",
                    "--quarantine-path",
                    str(quarantine),
                    "--reason",
                    "concurrent lock probe",
                    "--runs-dir",
                    str(runs_dir),
                    "--campaign-policy",
                    str(TEST_CAMPAIGN_POLICY),
                ],
                [
                    "--whole-window-verdict",
                    "--runs-dir",
                    str(runs_dir),
                    "--campaign-policy",
                    str(TEST_CAMPAIGN_POLICY),
                ],
            )
            with held_campaign_lock(runs_dir) as lock_token:
                locked_content = campaign_lock_path(lock_token).read_bytes()
                for arguments in commands:
                    with self.subTest(command=arguments[0]):
                        completed = subprocess.run(
                            [sys.executable, str(SCRIPT), *arguments],
                            cwd=ROOT,
                            text=True,
                            capture_output=True,
                            timeout=COMMAND_TIMEOUT_S,
                            check=False,
                        )
                        self.assertEqual(completed.returncode, 2)
                        self.assertIn(
                            "another campaign appears to be running",
                            completed.stderr,
                        )
                        self.assertEqual(
                            campaign_lock_path(lock_token).read_bytes(),
                            locked_content,
                        )
                        self.assertFalse(
                            (runs_dir / "campaign_log.jsonl").exists()
                        )

    def test_equality_branch_propagates_non_missing_os_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runs_dir = Path(tmp) / "runs"
            path = runs_dir / "campaign_manifests" / "permission.json"
            manifest = {
                "schema_version": "joulewise.campaign_provenance.v2",
                "session_id": "permission-session",
                "members": [],
            }
            with held_campaign_lock(runs_dir), patch.object(
                Path, "read_bytes", side_effect=PermissionError("denied")
            ):
                with self.assertRaisesRegex(PermissionError, "denied"):
                    run_campaign_module.write_campaign_provenance(path, manifest)

    def test_campaign_log_torn_final_line_only_is_tolerated(self) -> None:
        from joulewise.campaign_provenance import (
            load_authenticated_campaign_catalog,
            load_campaign_log_rows,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "campaign_log.jsonl"
            first = {"status": "ok", "run_id": "first"}
            second = {"status": "ok", "run_id": "second"}
            log_path.write_bytes(
                (json.dumps(first) + "\n").encode("utf-8") + b'{"status":'
            )
            self.assertEqual(load_campaign_log_rows(log_path), [first])

            complete_without_lf = (
                json.dumps(first, sort_keys=True)
                + "\n"
                + json.dumps(second, sort_keys=True)
            ).encode("utf-8")
            log_path.write_bytes(complete_without_lf)
            self.assertEqual(load_campaign_log_rows(log_path), [first, second])

            log_path.write_bytes((json.dumps(first) + "\n[]").encode("utf-8"))
            self.assertIsNone(load_campaign_log_rows(log_path))

            log_path.write_bytes(
                (json.dumps(first) + "\n").encode("utf-8")
                + b'{"status":\n'
                + (json.dumps(second) + "\n").encode("utf-8")
            )
            self.assertIsNone(load_campaign_log_rows(log_path))

            log_path.write_bytes(
                (json.dumps(first) + "\n").encode("utf-8")
                + b'{"first_torn"\n{"second_torn"'
            )
            self.assertIsNone(load_campaign_log_rows(log_path))

            manifest_dir = root / "campaign_manifests"
            manifest_dir.mkdir()
            (manifest_dir / "legacy.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.campaign_provenance.v1",
                        "session_id": "legacy",
                        "members": [
                            {
                                "execution": "invoked",
                                "run_id": "legacy",
                                "bundle_ids": ["legacy"],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            log_path.write_bytes(
                (json.dumps(first) + "\n").encode("utf-8") + b'{"torn"'
            )
            self.assertEqual(load_campaign_log_rows(log_path), [first])
            self.assertIsNotNone(load_authenticated_campaign_catalog(root))

    def test_append_log_uses_one_o_append_write_and_recovers_torn_tail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            log_path = root / "campaign_log.jsonl"
            with self.assertRaisesRegex(RuntimeError, "held campaign.lock"):
                run_campaign_module.append_log(log_path, {"row": 0})

            with (
                held_campaign_lock(root) as lock_token,
                patch.object(
                    run_campaign_module.os,
                    "open",
                    wraps=run_campaign_module.os.open,
                ) as open_mock,
                patch.object(
                    run_campaign_module.os,
                    "write",
                    wraps=run_campaign_module.os.write,
                ) as write_mock,
            ):
                run_campaign_module.append_log(
                    log_path, {"row": 1}, lock_token=lock_token
                )
            self.assertEqual(write_mock.call_count, 1)
            flags = open_mock.call_args.args[1]
            self.assertTrue(flags & os.O_APPEND)

            log_path.write_bytes(log_path.read_bytes() + b'{"torn"')
            with held_campaign_lock(root) as lock_token:
                run_campaign_module.append_log(
                    log_path, {"row": 2}, lock_token=lock_token
                )
            self.assertEqual(
                read_wire_jsonl(log_path),
                [{"row": 1}, {"row": 2}],
            )

            complete_mapping = json.dumps({"row": "preserved"}).encode("utf-8")
            log_path.write_bytes(complete_mapping)
            original_read_bytes = Path.read_bytes
            with held_campaign_lock(root) as lock_token, patch.object(
                Path,
                "read_bytes",
                autospec=True,
                side_effect=original_read_bytes,
            ) as read_mock:
                run_campaign_module.append_log(
                    log_path, {"row": "new"}, lock_token=lock_token
                )
            self.assertEqual(read_mock.call_count, 1)
            self.assertEqual(
                read_wire_jsonl(log_path),
                [{"row": "preserved"}, {"row": "new"}],
            )

    def test_v2_attestation_hashes_exact_noncanonical_manifest_bytes(self) -> None:
        from joulewise.campaign_provenance import (
            campaign_provenance_attestation,
            load_authenticated_campaign_catalog,
        )

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            runs_dir = root / "runs"
            manifest_dir = runs_dir / "campaign_manifests"
            manifest_dir.mkdir(parents=True)
            path = manifest_dir / "odd-wire.json"
            raw = (
                b'{ "members" : [ { "run_id" : "odd", '
                b'"bundle_ids" : [ "odd" ], "execution" : "invoked" } ],\n'
                b'  "session_id" : "odd-session",\n'
                b' "schema_version" : "joulewise.campaign_provenance.v2" }\n\n'
            )
            path.write_bytes(raw)
            manifest = json.loads(raw.decode("utf-8"))
            canonical = (
                json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            ).encode("utf-8")
            self.assertNotEqual(
                hashlib.sha256(raw).digest(),
                hashlib.sha256(canonical).digest(),
            )
            row = campaign_provenance_attestation(
                manifest_path=path,
                raw_manifest_bytes=raw,
                manifest=manifest,
                timestamp="2026-08-01T12:00:00Z",
            )
            self.assertEqual(
                row["campaign_provenance_manifest_sha256"],
                hashlib.sha256(raw).hexdigest(),
            )
            log_path = runs_dir / "campaign_log.jsonl"
            log_path.write_text(json.dumps(row) + "\n", encoding="utf-8")

            catalog = load_authenticated_campaign_catalog(runs_dir)

            self.assertIsNotNone(catalog)
            assert catalog is not None
            self.assertEqual(catalog[0].raw_bytes, raw)

    def test_prompt_hash_sidecar_match_records_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            write_suite_config(config_dir, "suite.json", "suite-match", sidecar=sidecar)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "ok")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "matched")
            self.assertEqual(check["checked_items"], 1)
            self.assertEqual(
                [match["item_id"] for match in check["matches"]],
                ["mock_item_003"],
            )

    def test_prompt_hash_sidecar_can_be_inferred_next_to_suite_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            write_suite_config(config_dir, "suite.json", "suite-inferred", suite_manifest=manifest)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "matched")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["checked_items"], 1)

    def test_malformed_inferred_prompt_hash_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text("{not-json\n", encoding="utf-8")
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-malformed", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn(str(sidecar), result.stderr)
            self.assertIn("not valid JSON", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertIn("not valid JSON", check["problems"][0])

    def test_neighboring_non_prompt_annotations_sidecar_is_missing_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text(
                json.dumps(
                    {
                        "annotations": [
                            {
                                "item_id": "affine_v1_L01_i00",
                                "scorer_id": "affine_mod_ladder_v1/score_v1",
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-annotations", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            member = rows[0]["members"][0]
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "missing_evidence")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["checked_items"], 0)
            self.assertEqual(
                member["collection_integrity_flags"],
                ["prompt_token_evidence_missing"],
            )
            self.assertEqual(member["collection_classification"], "failed")

    def test_explicit_affine_text_evidence_exemption_is_honored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "affine_smoke_v1.json"
            sidecar = tmp_path / "affine_smoke_v1_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text(
                json.dumps({"schema_version": "affine_smoke_annotations.v1"}) + "\n",
                encoding="utf-8",
            )
            write_suite_config(
                config_dir,
                "suite.json",
                "suite-inferred-schema",
                suite_manifest=manifest,
                prompt_token_evidence_policy="exempt_affine_generated_text",
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            member = rows[0]["members"][0]
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "policy_exempt")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["checked_items"], 0)
            self.assertEqual(member["collection_integrity_flags"], [])
            self.assertEqual(member["collection_classification"], "usable")

    def test_unknown_schema_inferred_prompt_hash_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text(
                json.dumps({"schema_version": "joulewise.prompt_hash_sidecar.v2"}) + "\n",
                encoding="utf-8",
            )
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-unknown-schema", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn(str(sidecar), result.stderr)
            self.assertIn("ambiguous", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(
                check["problems"],
                [
                    "inferred generator sidecar is ambiguous: "
                    "missing prompt-hash items and no recognized other-type marker"
                ],
            )

    def test_non_object_items_inferred_prompt_hash_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text(json.dumps({"items": []}) + "\n", encoding="utf-8")
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-non-object-items", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn(str(sidecar), result.stderr)
            self.assertIn("inferred generator sidecar items is not an object", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(
                check["problems"], ["inferred generator sidecar items is not an object"]
            )

    def test_empty_object_inferred_prompt_hash_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            sidecar = tmp_path / "mock_suite_manifest_annotations.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            sidecar.write_text("{}\n", encoding="utf-8")
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-empty", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn(str(sidecar), result.stderr)
            self.assertIn("ambiguous", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(
                check["problems"],
                [
                    "inferred generator sidecar is ambiguous: "
                    "missing prompt-hash items and no recognized other-type marker"
                ],
            )

    def test_required_text_evidence_missing_flags_member_unusable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mock_suite_manifest.json"
            config_dir.mkdir()
            manifest.write_text(
                (ROOT / "configs" / "suite_manifests" / "mock_suite_manifest.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            write_suite_config(
                config_dir, "suite.json", "suite-inferred-absent", suite_manifest=manifest
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            member = rows[0]["members"][0]
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "missing_evidence")
            self.assertIn("missing prompt-token evidence", check["problems"][0])
            self.assertEqual(
                member["collection_integrity_flags"],
                ["prompt_token_evidence_missing"],
            )
            self.assertEqual(member["collection_classification"], "failed")

    def test_ids_prompt_label_does_not_bypass_text_evidence_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "mislabeled_text_suite.json"
            config_dir.mkdir()
            manifest_data = json.loads(
                (
                    ROOT
                    / "configs"
                    / "suite_manifests"
                    / "mock_suite_manifest.json"
                ).read_text(encoding="utf-8")
            )
            text_item = next(
                item
                for item in manifest_data["items"]
                if item["source"].get("prompt_text") is not None
            )
            text_item["item_type"] = "ids_prompt"
            manifest.write_text(json.dumps(manifest_data) + "\n", encoding="utf-8")
            config = write_suite_config(
                config_dir,
                "suite.json",
                "suite-mislabeled-text",
                suite_manifest=manifest,
            )
            from joulewise.suite import suite_manifest_sha256

            config_data = json.loads(config.read_text(encoding="utf-8"))
            config_data["workload_profile"]["suite_manifest_sha256"] = (
                suite_manifest_sha256(manifest_data)
            )
            config.write_text(json.dumps(config_data) + "\n", encoding="utf-8")

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            member = rows[0]["members"][0]
            self.assertEqual(
                member["prompt_hash_check"]["status"],
                "missing_evidence",
            )
            self.assertEqual(
                member["collection_integrity_flags"],
                ["prompt_token_evidence_missing"],
            )
            self.assertEqual(member["collection_classification"], "failed")

    def test_prompt_hash_sidecar_top_level_alias_resolves_relative_to_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar_dir = config_dir / "sidecars"
            sidecar = sidecar_dir / "mixed.annotations.json"
            config_dir.mkdir()
            sidecar_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            config = write_suite_config(config_dir, "suite.json", "suite-relative-sidecar")
            payload = json.loads(config.read_text(encoding="utf-8"))
            payload["suite_sidecar_ref"] = str(Path("sidecars") / sidecar.name)
            config.write_text(json.dumps(payload) + "\n", encoding="utf-8")

            result = run_campaign(
                config_dir, runs_dir, ack_config_warnings=True
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "matched")
            self.assertEqual(check["sidecar_path"], str(sidecar))

    def test_prompt_hash_sidecar_single_item_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(sidecar, item_003_hash="0" * 64)
            write_suite_config(config_dir, "suite.json", "suite-mismatch", sidecar=sidecar)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_mismatch", result.stderr)
            self.assertIn("mock_item_003", result.stderr)
            self.assertIn("expected", result.stderr)
            self.assertIn("realized", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            member = rows[0]["members"][0]
            self.assertTrue(member["strict_valid"])
            self.assertEqual(member["collection_integrity_flags"], ["prompt_hash_mismatch"])
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "mismatch")
            self.assertEqual(check["checked_items"], 1)
            self.assertIn("mock_item_003", check["problems"][0])

    def test_prompt_hash_sidecar_error_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
                include_item_003=False,
            )
            write_suite_config(config_dir, "suite.json", "suite-sidecar-error", sidecar=sidecar)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn("missing from generator sidecar", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            member = rows[0]["members"][0]
            self.assertEqual(member["collection_integrity_flags"], ["prompt_hash_check_error"])
            check = member["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["checked_items"], 0)

    def test_explicit_scorer_shaped_sidecar_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "affine_smoke_v1_annotations.json"
            config_dir.mkdir()
            sidecar.write_text(
                json.dumps(
                    {
                        "annotations": [
                            {
                                "item_id": "affine_v1_L01_i00",
                                "scorer_id": "affine_mod_ladder_v1/score_v1",
                            }
                        ],
                        "schema_version": "affine_smoke_annotations.v1",
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            write_suite_config(
                config_dir, "suite.json", "suite-explicit-affine-sidecar", sidecar=sidecar
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn("generator sidecar items is not an object", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["sidecar_path"], str(sidecar))
            self.assertEqual(check["problems"], ["generator sidecar items is not an object"])

    def test_prompt_hash_sidecar_pairing_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
                subset_sha256="wrong-subset",
            )
            write_suite_config(config_dir, "suite.json", "suite-pairing-error", sidecar=sidecar)

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn("source_manifest.subset_sha256 mismatch", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["checked_items"], 1)

    def test_prompt_hash_sidecar_missing_source_manifest_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            payload = json.loads(sidecar.read_text(encoding="utf-8"))
            del payload["source_manifest"]
            sidecar.write_text(json.dumps(payload) + "\n", encoding="utf-8")
            write_suite_config(
                config_dir, "suite.json", "suite-missing-source-manifest", sidecar=sidecar
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            self.assertIn("prompt_hash_check_error", result.stderr)
            self.assertIn("source_manifest is missing", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check["status"], "error")
            self.assertEqual(check["checked_items"], 1)
            self.assertIn("generator sidecar source_manifest is missing", check["problems"])

    def test_prompt_hash_error_can_be_waived_to_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            waivers = tmp_path / "waivers.json"
            config_dir.mkdir()
            write_config(config_dir, "01-good.json", "good")
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
                include_item_003=False,
            )
            write_suite_config(config_dir, "02-suite.json", "suite-waived-error", sidecar=sidecar)
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "run_id": "suite-waived-error",
                            "reason": "manual prompt-sidecar audit accepted",
                            "approver": "council",
                            "timestamp": "2026-07-08T00:00:00Z",
                            "scope": "prompt_hash_check_error",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_campaign(config_dir, runs_dir, waivers=waivers)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("verdict: partial", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["ok", "waived"])
            member = rows[1]["members"][0]
            self.assertEqual(member["collection_classification"], "waived")
            self.assertEqual(member["waiver"]["scope"], "prompt_hash_check_error")

    def test_id_native_suite_without_sidecar_remains_not_applicable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            manifest = tmp_path / "id_native_suite.json"
            config_dir.mkdir()
            manifest_data = json.loads(
                (
                    ROOT
                    / "configs"
                    / "suite_manifests"
                    / "mock_suite_manifest.json"
                ).read_text(encoding="utf-8")
            )
            for item in manifest_data["items"]:
                if item["item_type"] != "text_prompt":
                    continue
                count = item["shape"]["planned_prompt_tokens"]
                item["item_type"] = "ids_prompt"
                item["source"]["prompt_text"] = None
                item["source"]["prompt_token_ids"] = list(range(1, count + 1))
            manifest.write_text(json.dumps(manifest_data) + "\n", encoding="utf-8")
            config = write_suite_config(
                config_dir,
                "suite.json",
                "suite-no-sidecar",
                suite_manifest=manifest,
            )
            from joulewise.suite import suite_manifest_sha256

            config_data = json.loads(config.read_text(encoding="utf-8"))
            config_data["workload_profile"]["suite_manifest_sha256"] = (
                suite_manifest_sha256(manifest_data)
            )
            config.write_text(json.dumps(config_data) + "\n", encoding="utf-8")

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("prompt_hash", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            check = rows[0]["members"][0]["prompt_hash_check"]
            self.assertEqual(check, {"status": "not_applicable", "checked_items": 0})

    def test_unknown_prompt_token_evidence_policy_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_suite_config(
                config_dir,
                "suite.json",
                "suite-unknown-policy",
                prompt_token_evidence_policy="trust_neighboring_annotations",
            )

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 2)
            self.assertIn("prompt_token_evidence_policy must be one of", result.stderr)
            self.assertFalse(runs_dir.exists())

    def test_post_hoc_prompt_hash_check_flag_on_fixture_pair(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(
                sidecar,
                item_003_hash="059b92ad883522ede0ed6466c53233117801ea5d28c3af1ff6d0777487b37e10",
            )
            write_suite_config(
                config_dir,
                "suite.json",
                "suite-posthoc",
                prompt_token_evidence_policy="exempt_affine_generated_text",
            )
            campaign = run_campaign(config_dir, runs_dir)
            self.assertEqual(campaign.returncode, 0, campaign.stderr)

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--check-prompt-hashes",
                    str(runs_dir / "suite-posthoc"),
                    str(sidecar),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=COMMAND_TIMEOUT_S,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            check = json.loads(result.stdout)
            self.assertEqual(check["status"], "matched")
            self.assertEqual(check["checked_items"], 1)

    def test_post_hoc_prompt_hash_check_nonzero_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            sidecar = tmp_path / "mixed.annotations.json"
            config_dir.mkdir()
            write_prompt_sidecar(sidecar, item_003_hash="0" * 64)
            write_suite_config(
                config_dir,
                "suite.json",
                "suite-posthoc-nonzero",
                prompt_token_evidence_policy="exempt_affine_generated_text",
            )
            campaign = run_campaign(config_dir, runs_dir)
            self.assertEqual(campaign.returncode, 0, campaign.stderr)

            mismatch = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--check-prompt-hashes",
                    str(runs_dir / "suite-posthoc-nonzero"),
                    str(sidecar),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=COMMAND_TIMEOUT_S,
            )
            error = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--check-prompt-hashes",
                    str(runs_dir / "suite-posthoc-nonzero"),
                    str(tmp_path / "missing-sidecar.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=COMMAND_TIMEOUT_S,
            )

            self.assertEqual(mismatch.returncode, 1, mismatch.stderr)
            self.assertEqual(json.loads(mismatch.stdout)["status"], "mismatch")
            self.assertEqual(error.returncode, 2, error.stderr)
            self.assertEqual(json.loads(error.stdout)["status"], "error")

    def test_partial_experiment_is_incomplete_and_does_not_invoke_cli(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "partial.json", "partial-exp", repetitions=5
            )
            write_experiment(
                runs_dir,
                "partial-exp",
                5,
                completed=3,
                config_path=config_path,
            )
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            self.assertIn("incomplete_existing partial-exp", result.stderr)
            self.assertIn("partial-exp__r1", result.stderr)
            self.assertIn("partial-exp__r3", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["incomplete_existing"])
            self.assertNotIn("members_succeeded", rows[0])
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "blocked")
            self.assertEqual(
                verdict["collection"]["categories"]["usable"],
                ["partial-exp__r1", "partial-exp__r2", "partial-exp__r3"],
            )
            self.assertEqual(
                verdict["collection"]["categories"]["missing"],
                ["partial-exp__r4", "partial-exp__r5"],
            )

    def test_existing_incomplete_member_prevents_usable_collection_verdict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-usable.json", "usable")
            write_config(config_dir, "02-incomplete.json", "incomplete")
            write_single_bundle(runs_dir, "usable")
            (runs_dir / "incomplete").mkdir()

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertNotEqual(verdict["collection"]["verdict"], "usable")
            self.assertEqual(verdict["collection"]["verdict"], "invalid")
            self.assertEqual(
                verdict["collection"]["categories"]["usable"], ["usable"]
            )
            self.assertEqual(
                verdict["collection"]["categories"]["failed"], ["incomplete"]
            )
            self.assertEqual(verdict["collection"]["categories"]["missing"], [])

    def test_mixed_complete_incomplete_and_absent_members_are_classified_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(
                config_dir, "mixed.json", "mixed", repetitions=3
            )
            write_single_bundle(
                runs_dir,
                "mixed__r1",
                config_path=config_path,
            )
            (runs_dir / "mixed__r2").mkdir()

            result = run_campaign(config_dir, runs_dir)

            self.assertEqual(result.returncode, 1)
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "blocked")
            self.assertEqual(
                verdict["collection"]["categories"],
                {
                    "usable": ["mixed__r1"],
                    "waived": [],
                    "failed": ["mixed__r2"],
                    "missing": ["mixed__r3"],
                },
            )

    def test_reps_one_resume_uses_single_bundle_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-complete.json", "complete", repetitions=1)
            write_config(config_dir, "02-incomplete.json", "incomplete", repetitions=1)
            write_single_bundle(runs_dir, "complete")
            (runs_dir / "incomplete").mkdir()
            sentinel = tmp_path / "sentinel"
            fake_cli = make_fake_cli(tmp_path, sentinel)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse(sentinel.exists())
            self.assertIn("skipped complete", result.stdout)
            self.assertIn("incomplete_existing incomplete", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["skipped", "incomplete_existing"])
            self.assertEqual([row["exit_code"] for row in rows], [None, None])

    def test_fake_cli_execution_logs_statuses_and_sequential_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-alpha.json", "alpha", repetitions=5)
            write_config(config_dir, "02-beta.json", "beta-fail", repetitions=5)
            write_config(config_dir, "03-gamma.json", "gamma", repetitions=5)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["alpha", "beta-fail", "gamma"])
            self.assertIn(f"bundle: {runs_dir / 'alpha__r1'} status=succeeded", result.stdout)
            self.assertIn(f"bundle: {runs_dir / 'beta-fail__r5'} status=failed", result.stdout)
            self.assertIn(f"experiment: {runs_dir / 'experiments' / 'alpha.json'} members=5", result.stdout)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["alpha", "beta-fail", "gamma"])
            self.assertEqual([row["status"] for row in rows], ["ok", "failed", "ok"])
            self.assertEqual([row["exit_code"] for row in rows], [0, 3, 0])
            self.assertIsInstance(rows[0]["duration_s"], float)
            self.assertTrue((runs_dir / "alpha__r1" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "alpha__r5" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "beta-fail__r5" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "gamma__r5" / "summary_metrics.json").is_file())

    def test_order_manifest_controls_execution_order_and_log_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            alpha = write_config(config_dir, "01-alpha.json", "alpha")
            beta = write_config(config_dir, "02-beta.json", "beta")
            (config_dir / "order_manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.order_manifest.v1",
                        "seed": 2000005,
                        "rotation_scheme": {},
                        "imbalance_note": "test",
                        "executed_order": [
                            {
                                "index": 1,
                                "config": beta.name,
                                "run_id": "beta",
                                "model_tag": "b",
                                "rep": 1,
                                "workload": "short_short",
                            },
                            {
                                "index": 2,
                                "config": alpha.name,
                                "run_id": "alpha",
                                "model_tag": "a",
                                "rep": 1,
                                "workload": "short_short",
                            },
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["beta", "alpha"])
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["beta", "alpha"])
            self.assertEqual([row["run_index"] for row in rows], [1, 2])
            self.assertEqual(rows[0]["executed_order"]["model_tag"], "b")
            self.assertIs(rows[0]["model_load_boundary"], True)
            self.assertIs(rows[1]["model_load_boundary"], True)

    def test_order_manifest_log_echo_carries_drift_covariates_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_cli = make_fake_cli(tmp_path)

            config_dir = tmp_path / "configs-with-covariates"
            runs_dir = tmp_path / "runs-with-covariates"
            config_dir.mkdir()
            sentinel = write_config(config_dir, "sentinel.json", "alpha-r1-short_short_sentinel-start")
            (config_dir / "order_manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.order_manifest.v1",
                        "executed_order": [
                            {
                                "index": 1,
                                "config": sentinel.name,
                                "run_id": "alpha-r1-short_short_sentinel-start",
                                "model_tag": "alpha",
                                "rep": 1,
                                "workload": "short_short_sentinel",
                                "role": "drift_sentinel",
                                "block_index": 7,
                                "position_in_block": 1,
                                "sentinel_position": "start",
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            echoed = rows[0]["executed_order"]
            self.assertEqual(echoed["run_id"], "alpha-r1-short_short_sentinel-start")
            self.assertEqual(echoed["role"], "drift_sentinel")
            self.assertEqual(echoed["block_index"], 7)
            self.assertEqual(echoed["position_in_block"], 1)
            self.assertEqual(echoed["sentinel_position"], "start")

            old_config_dir = tmp_path / "configs-old-manifest"
            old_runs_dir = tmp_path / "runs-old-manifest"
            old_config_dir.mkdir()
            old_config = write_config(old_config_dir, "baseline.json", "alpha-r1-short_short")
            (old_config_dir / "order_manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "joulewise.order_manifest.v1",
                        "executed_order": [
                            {
                                "index": 1,
                                "config": old_config.name,
                                "run_id": "alpha-r1-short_short",
                                "model_tag": "alpha",
                                "rep": 1,
                                "workload": "short_short",
                            }
                        ],
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            old_result = run_campaign(old_config_dir, old_runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(old_result.returncode, 0, old_result.stderr)
            old_rows = read_jsonl(old_runs_dir / "campaign_log.jsonl")
            old_echoed = old_rows[0]["executed_order"]
            self.assertEqual(old_echoed["run_id"], "alpha-r1-short_short")
            self.assertNotIn("role", old_echoed)
            self.assertNotIn("block_index", old_echoed)
            self.assertNotIn("position_in_block", old_echoed)
            self.assertNotIn("sentinel_position", old_echoed)

    def test_order_manifest_rejects_duplicate_and_non_contiguous_entries(self) -> None:
        cases = [
            (
                "duplicate-config",
                [
                    {"index": 1, "config": "01-alpha.json"},
                    {"index": 2, "config": "01-alpha.json"},
                ],
                "duplicate config",
            ),
            (
                "duplicate-index",
                [
                    {"index": 1, "config": "01-alpha.json"},
                    {"index": 1, "config": "02-beta.json"},
                ],
                "duplicate index",
            ),
            (
                "gap-index",
                [
                    {"index": 1, "config": "01-alpha.json"},
                    {"index": 3, "config": "02-beta.json"},
                ],
                "contiguous",
            ),
        ]
        for label, executed_order, expected in cases:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                config_dir = tmp_path / "configs"
                runs_dir = tmp_path / "runs"
                config_dir.mkdir()
                write_config(config_dir, "01-alpha.json", "alpha")
                write_config(config_dir, "02-beta.json", "beta")
                (config_dir / "order_manifest.json").write_text(
                    json.dumps(
                        {
                            "schema_version": "joulewise.order_manifest.v1",
                            "executed_order": executed_order,
                        }
                    )
                    + "\n",
                    encoding="utf-8",
                )

                result = run_campaign(config_dir, runs_dir)

                self.assertEqual(result.returncode, 2)
                self.assertIn(expected, result.stderr)

    def test_missing_order_manifest_records_loud_warning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("no order_manifest.json found", result.stderr)
            all_rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertIn("block_order_warning", all_rows[0])
            self.assertIn("block_order_warning", all_rows[-1])

    def test_fresh_experiment_run_then_second_invocation_skips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "matrix.json", "matrix-exp", repetitions=5)
            fake_cli = make_fake_cli(tmp_path)

            first = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )
            second = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["matrix-exp"])
            self.assertTrue((runs_dir / "matrix-exp__r1" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "experiments" / "matrix-exp.json").is_file())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["ok", "skipped"])
            self.assertEqual(rows[1]["members_succeeded"], 5)
            self.assertEqual(rows[1]["members_total"], 5)

    def test_max_failures_stops_after_n_failures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-one.json", "one-fail")
            write_config(config_dir, "02-two.json", "two-fail")
            write_config(config_dir, "03-three.json", "three")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=1,
            )

            self.assertEqual(result.returncode, 1)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["one-fail"])
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["one-fail"])
            self.assertEqual([row["status"] for row in rows], ["failed"])

    def test_prompt_realization_mismatch_stops_before_second_child(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            first = write_config(
                config_dir, "01-realization-mismatch.json", "realization-mismatch"
            )
            first_value = json.loads(first.read_text(encoding="utf-8"))
            first_value["workload_profile"]["prompt_tokens"] = None
            first_value["workload_profile"]["prompt_text"] = "test"
            first_value["workload_profile"]["output_tokens"] = 2
            first_value["workload_profile"]["prompt_token_expectation"] = {
                "schema_version": "joulewise.prompt_token_expectation.v1",
                "token_hash_domain": "joulewise.prompt_token_ids.v1",
                "token_count": 3,
                "token_ids_sha256": "0" * 64,
            }
            first.write_text(
                json.dumps(first_value) + "\n", encoding="utf-8"
            )
            write_config(config_dir, "02-never.json", "never-dispatched")
            fake_cli = make_fake_cli(tmp_path)
            waivers = tmp_path / "waivers.json"
            waivers.write_text(
                json.dumps(
                    [
                        {
                            "run_id": "realization-mismatch",
                            "reason": "explicit matching fixture waiver",
                            "approver": "test",
                            "timestamp": "2026-09-01T00:00:00Z",
                            "scope": "any",
                        }
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=1,
                waivers=waivers,
            )

            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertEqual(
                (runs_dir / "order.log").read_text(encoding="utf-8").splitlines(),
                ["realization-mismatch"],
            )
            self.assertTrue((runs_dir / "realization-mismatch").is_dir())
            self.assertFalse((runs_dir / "never-dispatched").exists())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["status"], "failed")
            self.assertEqual(len(rows[0]["members"]), 1)
            member = rows[0]["members"][0]
            self.assertEqual(member["collection_classification"], "failed")
            self.assertEqual(member["waiver"]["scope"], "any")
            self.assertFalse(member["strict_valid"])
            self.assertTrue(
                any(
                    problem.startswith("prompt_realization_mismatch:")
                    for problem in member["validation_problems"]
                ),
                member,
            )

    def test_prompt_realization_reader_codes_are_unwaivable_including_any(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "prompt-realization"
            bundle.mkdir()
            (bundle / "summary_metrics.json").write_text(
                json.dumps({"status": "succeeded"}) + "\n", encoding="utf-8"
            )
            (bundle / "metadata.json").write_text("{}\n", encoding="utf-8")
            before = {
                path.name: path.read_bytes()
                for path in bundle.iterdir()
                if path.is_file()
            }
            info = run_campaign_module.load_config_info(BASE_CONFIG)
            waiver = run_campaign_module.Waiver(
                target_kind="bundle_id",
                target=bundle.name,
                reason="explicit matching fixture waiver",
                approver="test",
                timestamp="2026-09-01T00:00:00Z",
                scope="any",
            )
            waiver_map = {("bundle_id", bundle.name): waiver}
            for code in sorted(
                run_campaign_module.PROMPT_REALIZATION_PROBLEM_CODES
            ):
                with self.subTest(code=code), patch.object(
                    run_campaign_module,
                    "validate_bundle",
                    return_value=[f"{code}: fixture"],
                ), patch.object(
                    run_campaign_module,
                    "_bundle_config_binding_problem",
                    return_value=None,
                ):
                    evaluation = run_campaign_module.evaluate_member(
                        bundle, info=info, waivers=waiver_map
                    )
                self.assertEqual(
                    evaluation.collection_integrity_flags, (code,)
                )
                self.assertFalse(evaluation.strict_valid)
                self.assertFalse(evaluation.usable)
                self.assertFalse(evaluation.waived)
                self.assertTrue(evaluation.failed)
            self.assertEqual(
                before,
                {
                    path.name: path.read_bytes()
                    for path in bundle.iterdir()
                    if path.is_file()
                },
            )

    def test_resume_after_partial_failure_sequence_skips_partial_on_second_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            log_path = tmp_path / "campaign.jsonl"
            config_dir.mkdir()
            write_config(config_dir, "01-alpha.json", "alpha", repetitions=5)
            write_config(config_dir, "02-beta.json", "beta-crash2", repetitions=5)
            fake_cli = make_fake_cli(tmp_path)

            first = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
                log_path=log_path,
            )
            second = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
                log_path=log_path,
            )

            self.assertEqual(first.returncode, 1)
            self.assertEqual(second.returncode, 1)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["alpha", "beta-crash2"])
            self.assertTrue((runs_dir / "beta-crash2__r1" / "summary_metrics.json").is_file())
            self.assertTrue((runs_dir / "beta-crash2__r2" / "summary_metrics.json").is_file())
            self.assertFalse((runs_dir / "beta-crash2__r3").exists())
            rows = read_jsonl(log_path)
            self.assertEqual([row["run_id"] for row in rows], ["alpha", "beta-crash2", "alpha", "beta-crash2"])
            self.assertEqual([row["status"] for row in rows], ["ok", "failed", "skipped", "incomplete_existing"])
            verdicts = [
                row
                for row in read_all_jsonl(log_path)
                if row.get("record_type") == "campaign_verdict"
            ]
            self.assertEqual(
                [verdict["collection"]["verdict"] for verdict in verdicts],
                ["blocked", "blocked"],
            )

    def test_malformed_member_summary_is_incomplete_existing_without_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "matrix.json", "matrix", repetitions=5)
            member = runs_dir / "matrix__r1"
            member.mkdir(parents=True)
            (member / "summary_metrics.json").write_text('{"status": ', encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse((runs_dir / "order.log").exists())
            self.assertIn("malformed summary_metrics.json", result.stderr)
            self.assertIn("matrix__r1", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["incomplete_existing"])
            verdict = read_all_jsonl(runs_dir / "campaign_log.jsonl")[-1]
            self.assertEqual(verdict["collection"]["verdict"], "blocked")
            self.assertEqual(
                verdict["collection"]["categories"]["failed"], ["matrix__r1"]
            )
            self.assertEqual(
                verdict["collection"]["categories"]["missing"],
                [
                    "matrix__r2",
                    "matrix__r3",
                    "matrix__r4",
                    "matrix__r5",
                ],
            )

    def test_config_error_aborts_before_invocation_or_log_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            good = write_config(config_dir, "01-good.json", "good")
            bad = config_dir / "02-bad.json"
            bad.write_text('{"run_id": ', encoding="utf-8")
            later = write_config(config_dir, "03-later.json", "later")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("Config files to execute:", result.stdout)
            self.assertIn(str(good), result.stdout)
            self.assertIn(str(bad), result.stdout)
            self.assertIn(str(later), result.stdout)
            self.assertIn("config is not valid JSON", result.stderr)
            self.assertIn(str(bad), result.stderr)
            self.assertFalse((runs_dir / "order.log").exists())
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())

    def test_duplicate_sanitized_run_ids_abort_before_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-space.json", "Foo Bar")
            write_config(config_dir, "02-dash.json", "foo-bar")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 2)
            self.assertIn("duplicate sanitized run_id", result.stderr)
            self.assertIn("01-space.json", result.stderr)
            self.assertIn("02-dash.json", result.stderr)
            self.assertFalse((runs_dir / "order.log").exists())
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())

    def test_sanitized_run_id_is_used_for_path_checks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            config_path = write_config(config_dir, "space.json", "Foo Bar")
            write_single_bundle(runs_dir, "foo-bar", config_path=config_path)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("sanitized run_id", result.stderr)
            self.assertIn("skipped foo-bar", result.stdout)
            self.assertFalse((runs_dir / "order.log").exists())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["run_id"], "foo-bar")
            self.assertEqual(rows[0]["status"], "skipped")

    def test_cli_exit_2_is_failed_log_row_without_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "exit2.json", "exit2")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse((runs_dir / "exit2").exists())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual(rows[0]["status"], "failed")
            self.assertEqual(rows[0]["exit_code"], 2)

    def test_cli_cmd_with_spaces_executes_and_dry_run_quotes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            spaced_dir = tmp_path / "tool dir"
            config_dir.mkdir()
            spaced_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(spaced_dir)
            cli_cmd = cli_cmd_for(fake_cli)

            dry = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd, dry_run=True)
            real = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd)

            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertIn(shlex.quote(str(fake_cli)), dry.stdout)
            self.assertEqual(real.returncode, 0, real.stderr)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["one"])

    def test_max_failures_skips_do_not_consume_incomplete_does(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-skip.json", "skip")
            write_config(config_dir, "02-partial.json", "partial", repetitions=5)
            write_config(config_dir, "03-fresh.json", "fresh")
            write_single_bundle(runs_dir, "skip")
            (runs_dir / "partial__r1").mkdir(parents=True)
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=1,
            )

            self.assertEqual(result.returncode, 1)
            self.assertFalse((runs_dir / "order.log").exists())
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["skip", "partial"])
            self.assertEqual([row["status"] for row in rows], ["skipped", "incomplete_existing"])

    def test_backup_shim_runs_once_per_success_and_failure_is_nonfatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            backup_log = tmp_path / "backup.log"
            backup = tmp_path / "backup shim.sh"
            config_dir.mkdir()
            write_config(config_dir, "01-alpha.json", "alpha")
            write_config(config_dir, "02-beta.json", "beta")
            fake_cli = make_fake_cli(tmp_path)
            backup.write_text(
                f"#!/bin/sh\nprintf '%s\\n' \"$1\" >> {shlex.quote(str(backup_log))}\nexit 1\n",
                encoding="utf-8",
            )
            os.chmod(backup, 0o755)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                backup=backup,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(backup_log.read_text(encoding="utf-8").splitlines(), [str(runs_dir), str(runs_dir)])
            self.assertIn("warning: backup command failed", result.stderr)
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["status"] for row in rows], ["ok", "ok"])

    def test_torn_final_log_row_is_removed_before_new_json_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            log_path = tmp_path / "campaign.jsonl"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            log_path.write_text('{"dead": tru', encoding="utf-8")
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                log_path=log_path,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            lines = log_path.read_text(encoding="utf-8").splitlines()
            self.assertNotIn('{"dead": tru', lines)
            parsed = [
                json.loads(line)
                for line in lines
                if json.loads(line).get("record_type")
                not in {"campaign_verdict", "campaign_provenance_attestation"}
            ]
            self.assertEqual([row["status"] for row in parsed], ["ok"])

    def test_explicit_log_inside_stored_bundle_is_refused_without_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            bundle = runs_dir / "sealed"
            config_dir.mkdir()
            bundle.mkdir(parents=True)
            (bundle / "summary_metrics.json").write_text(
                json.dumps({"status": "succeeded"}) + "\n",
                encoding="utf-8",
            )
            write_config(config_dir, "one.json", "one")
            log_path = bundle / "derived" / "campaign.jsonl"
            fake_cli = make_fake_cli(tmp_path)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                log_path=log_path,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("outside the immutable stored run bundle", result.stderr)
            self.assertFalse(log_path.exists())
            self.assertFalse((runs_dir / "order.log").exists())

    def test_lock_blocks_real_run_is_removed_after_success_and_dry_run_ignores_it(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            runs_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(tmp_path)
            lock = runs_dir / "campaign.lock"
            lock.write_text("pid=123 created_at=manual\n", encoding="utf-8")

            dry = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli), dry_run=True)
            blocked = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))
            self.assertFalse((runs_dir / "campaign_log.jsonl").exists())
            self.assertFalse((runs_dir / "order.log").exists())
            lock.unlink()
            real = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertEqual(blocked.returncode, 2)
            self.assertIn("another campaign appears to be running", blocked.stderr)
            self.assertEqual(real.returncode, 0, real.stderr)
            self.assertFalse(lock.exists())
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["one"])

    def test_dry_run_plan_matches_real_mixed_state_actions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            complete_config = write_config(
                config_dir, "01-complete.json", "complete", repetitions=5
            )
            partial_config = write_config(
                config_dir, "02-partial.json", "partial", repetitions=5
            )
            write_config(config_dir, "03-fresh.json", "fresh", repetitions=5)
            write_experiment(
                runs_dir, "complete", 5, config_path=complete_config
            )
            write_experiment(
                runs_dir,
                "partial",
                5,
                completed=2,
                config_path=partial_config,
            )
            fake_cli = make_fake_cli(tmp_path)

            dry = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                dry_run=True,
            )
            real = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                max_failures=2,
            )

            self.assertEqual(dry.returncode, 0, dry.stderr)
            self.assertIn("dry_run complete: skip complete", dry.stdout)
            self.assertIn("dry_run partial: incomplete existing", dry.stdout)
            self.assertIn("dry_run fresh: would run", dry.stdout)
            self.assertEqual(real.returncode, 1)
            self.assertEqual((runs_dir / "order.log").read_text(encoding="utf-8").splitlines(), ["fresh"])
            rows = read_jsonl(runs_dir / "campaign_log.jsonl")
            self.assertEqual([row["run_id"] for row in rows], ["complete", "partial", "fresh"])
            self.assertEqual([row["status"] for row in rows], ["skipped", "incomplete_existing", "ok"])
            manifests = list((runs_dir / "campaign_manifests").glob("*.json"))
            self.assertEqual(len(manifests), 1)
            provenance = json.loads(manifests[0].read_text(encoding="utf-8"))
            self.assertEqual(provenance["first_physical_run_id"], "fresh__r1")
            fresh = next(
                member
                for member in provenance["members"]
                if member["run_id"] == "fresh"
            )
            self.assertEqual(
                fresh["preceding_campaign_cooldown"]["result"],
                "first_run_exempt",
            )

    def test_first_run_exemption_resets_for_each_physical_campaign_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "01-a.json", "a")
            fake_cli = make_fake_cli(tmp_path)

            first = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))
            write_config(config_dir, "02-b.json", "b")
            second = run_campaign(config_dir, runs_dir, cli_cmd=cli_cmd_for(fake_cli))

            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertEqual(second.returncode, 0, second.stderr)
            manifests = sorted((runs_dir / "campaign_manifests").glob("*.json"))
            self.assertEqual(len(manifests), 2)
            sessions = [json.loads(path.read_text(encoding="utf-8")) for path in manifests]
            self.assertEqual(
                {session["first_physical_run_id"] for session in sessions},
                {"a", "b"},
            )
            for session in sessions:
                first_member = next(
                    member
                    for member in session["members"]
                    if member["run_id"] == session["first_physical_run_id"]
                )
                self.assertEqual(
                    first_member["preceding_campaign_cooldown"]["result"],
                    "first_run_exempt",
                )

    def test_p2038_shakedown_requires_backup_and_exactly_one_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            missing_backup = run_campaign(
                config_dir, runs_dir, shakedown_gate=True
            )
            self.assertEqual(missing_backup.returncode, 2)
            self.assertIn("requires --backup", missing_backup.stderr)

            write_config(config_dir, "two.json", "two")
            backup = tmp_path / "backup.sh"
            backup.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            os.chmod(backup, 0o755)
            too_many = run_campaign(
                config_dir,
                runs_dir,
                backup=backup,
                shakedown_gate=True,
            )
            self.assertEqual(too_many.returncode, 2)
            self.assertIn("exactly one", too_many.stderr)

    def test_p2038_shakedown_rejects_mock_backend_with_named_gate_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            config_dir = tmp_path / "configs"
            runs_dir = tmp_path / "runs"
            config_dir.mkdir()
            write_config(config_dir, "one.json", "one")
            fake_cli = make_fake_cli(tmp_path)
            backup = tmp_path / "backup.sh"
            backup.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            os.chmod(backup, 0o755)

            result = run_campaign(
                config_dir,
                runs_dir,
                cli_cmd=cli_cmd_for(fake_cli),
                backup=backup,
                shakedown_gate=True,
            )

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "SHAKEDOWN_GATE_FAILED[not_production_backend]", result.stderr
            )
            rows = read_all_jsonl(runs_dir / "campaign_log.jsonl")
            gate = next(row for row in rows if row.get("record_type") == "shakedown_gate")
            self.assertEqual(gate["status"], "failed")
            self.assertEqual(gate["code"], "not_production_backend")

    def test_p2038_shakedown_backup_launch_failure_has_named_failed_gate_row(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bundle = root / "bundle"
            bundle.mkdir()
            log_path = root / "campaign_log.jsonl"
            completed = subprocess.CompletedProcess([], 0)
            with (
                patch("scripts.run_campaign.validate_bundle", return_value=[]),
                patch("scripts.run_campaign.subprocess.run", return_value=completed),
                patch(
                    "scripts.run_campaign.assert_production_uncertainty",
                    return_value={"bundle_id": bundle.name},
                ),
                patch(
                    "scripts.run_campaign.backup_runs",
                    side_effect=FileNotFoundError("backup executable missing"),
                ),
            ):
                with self.assertRaises(ShakedownGateError) as raised:
                    execute_production_uncertainty_gate(
                        bundle, root, str(root / "missing-backup")
                    )
            error = raised.exception
            self.assertEqual(error.code, "backup_failed")
            rendered = (
                f"SHAKEDOWN_GATE_FAILED[{error.code}] bundle={error.bundle_id} "
                f"detail={error.detail}"
            )
            self.assertIn("SHAKEDOWN_GATE_FAILED[backup_failed]", rendered)
            with held_campaign_lock(root) as lock_token:
                run_campaign_module.append_log(
                    log_path,
                    failed_shakedown_record("production_uncertainty_v1", error),
                    lock_token=lock_token,
                )
            gate = read_all_jsonl(log_path)[0]
            self.assertEqual(gate["status"], "failed")
            self.assertEqual(gate["code"], "backup_failed")


def _idle_admission_extension_mapping(profile: str) -> dict:
    mapping = {
        "schema_version": "joulewise.idle_admission_extension.v1",
        "policy_version": "idle-admission-core-v1",
        "claim_bearing": True,
        "cpu_criteria": {
            "cpu_busy_ratio_p95_max": 0.5,
            "processor_combined_power_w_p95_max": 1.0,
            "min_samples": 3,
            "on_missing_telemetry": "fail",
        },
        "adapter_wattage": {"require_known_wattage": True},
        "neg8_bracket": {
            "require_bracket": True,
            "max_abs_delta_j": 0.5,
            "max_rel_delta": 0.0625,
        },
    }
    if profile == "exploratory":
        mapping["claim_bearing"] = False
        mapping["cpu_criteria"]["on_missing_telemetry"] = "flag"
        mapping["adapter_wattage"]["require_known_wattage"] = False
        mapping["neg8_bracket"]["require_bracket"] = False
    return mapping


def _clean_idle_records(count: int = 5) -> list[dict]:
    return [
        {
            "processor_combined_power_w": 0.15,
            "clusters": [
                {
                    "cpus": [
                        {"idle_ratio": 0.95, "down_ratio": 0.0},
                        {"idle_ratio": 0.99, "down_ratio": 0.0},
                    ]
                }
            ],
        }
        for _ in range(count)
    ]


def _busy_idle_records(count: int = 5) -> list[dict]:
    return [
        {
            "processor_combined_power_w": 0.2,
            "clusters": [{"cpus": [{"idle_ratio": 0.05, "down_ratio": 0.0}]}],
        }
        for _ in range(count)
    ]


class AnchorFallbackCampaignGateTests(unittest.TestCase):
    @staticmethod
    def _bind_powermetrics_config(
        bundle: Path, bundle_id: str, metadata: dict
    ) -> None:
        config = json.loads(
            Path("tests/fixtures/d078_r01/config.json").read_text(
                encoding="utf-8"
            )
        )
        config["run_id"] = bundle_id
        config_raw = (json.dumps(config, sort_keys=True) + "\n").encode()
        (bundle / "config.json").write_bytes(config_raw)
        metadata["config_sha256"] = hashlib.sha256(config_raw).hexdigest()
        metadata["adapters"] = {
            "telemetry": {"name": "powermetrics"}
        }

    @staticmethod
    def _bundle(
        root: Path, bundle_id: str, *, fallback: bool
    ) -> tuple[Path, bytes]:
        bundle = root / bundle_id
        bundle.mkdir()
        summary = {
            "status": "succeeded",
            "measurement_quality": {"telemetry_source": "powermetrics"},
            "energy_uncertainty_status": (
                "not_estimable" if fallback else "bounded"
            ),
            "window_evidence_precheck": {
                "gross_request": {
                    "eligible": not fallback,
                    "reasons": (
                        ["clock_anchor_unresolved"] if fallback else []
                    ),
                }
            },
        }
        raw_summary = (json.dumps(summary, sort_keys=True) + "\n").encode()
        (bundle / "summary_metrics.json").write_bytes(raw_summary)
        anchor = (
            {
                "status": "unresolved",
                "trace_fallback_method": "legacy_spawn_bracket_midpoint_v1",
            }
            if fallback
            else {"status": "bounded"}
        )
        metadata = {"uncertainty_evidence": {"clock_anchor": anchor}}
        AnchorFallbackCampaignGateTests._bind_powermetrics_config(
            bundle, bundle_id, metadata
        )
        (bundle / "metadata.json").write_text(
            json.dumps(metadata) + "\n",
            encoding="utf-8",
        )
        return bundle, raw_summary

    def _evaluate(self, bundle: Path, *, role: str):
        info = run_campaign_module.ConfigInfo(
            path=BASE_CONFIG,
            run_id=bundle.name,
            raw_run_id=bundle.name,
            repetitions=1,
            role=role,
        )
        with (
            patch.object(
                run_campaign_module, "validate_bundle", return_value=[]
            ),
            patch.object(
                run_campaign_module,
                "_bundle_config_binding_problem",
                return_value=None,
            ),
        ):
            return run_campaign_module.evaluate_member(
                bundle, info=info, waivers={}
            )

    @staticmethod
    def _whole_window_trigger_bundle(
        root: Path, bundle_id: str, trigger: str
    ) -> Path:
        bundle = root / bundle_id
        bundle.mkdir()
        summary = {
            "status": "succeeded",
            "measurement_quality": {"telemetry_source": "powermetrics"},
            "energy_uncertainty_status": "bounded",
            "window_evidence_precheck": {
                "gross_request": {"eligible": True, "reasons": []}
            },
        }
        metadata = {
            "uncertainty_evidence": {
                "clock_anchor": {"status": "bounded"}
            }
        }
        if trigger == "not_estimable":
            summary["energy_uncertainty_status"] = "not_estimable"
        elif trigger == "clock_anchor_unresolved":
            summary["window_evidence_precheck"]["gross_request"] = {
                "eligible": False,
                "reasons": ["clock_anchor_unresolved"],
            }
        elif trigger == "trace_fallback_method":
            metadata["uncertainty_evidence"]["clock_anchor"][
                "trace_fallback_method"
            ] = "legacy_spawn_bracket_midpoint_v1"
        else:
            raise AssertionError(f"unknown trigger {trigger}")
        AnchorFallbackCampaignGateTests._bind_powermetrics_config(
            bundle, bundle_id, metadata
        )
        (bundle / "summary_metrics.json").write_text(
            json.dumps(summary) + "\n", encoding="utf-8"
        )
        (bundle / "metadata.json").write_text(
            json.dumps(metadata) + "\n", encoding="utf-8"
        )
        return bundle

    def _whole_window_evaluate(
        self, bundle: Path, *, role: str, waiver: bool = True
    ):
        waiver_map = (
            {
                ("bundle_id", bundle.name): run_campaign_module.Waiver(
                    target_kind="bundle_id",
                    target=bundle.name,
                    reason="audit fixture",
                    approver="test",
                    timestamp="2026-07-24T00:00:00Z",
                    scope="any",
                )
            }
            if waiver
            else {}
        )
        source = run_campaign_module.WholeWindowMemberSource(
            path=bundle,
            role=role,
        )
        with patch.object(
            run_campaign_module, "validate_bundle", return_value=[]
        ):
            return run_campaign_module._whole_window_member(
                source, waiver_map
            )

    def test_floor_member_fallback_anchor_is_unwaivable_rerun_trigger(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle, raw_summary = self._bundle(
                Path(tmp), "fallback-member", fallback=True
            )
            evaluation = self._evaluate(bundle, role="absolute_repeat")
            self.assertTrue(bundle.is_dir())
            self.assertEqual(
                (bundle / "summary_metrics.json").read_bytes(), raw_summary
            )
        self.assertIn(
            run_campaign_module.ANCHOR_FALLBACK_MEMBER_REFUSAL,
            evaluation.collection_integrity_flags,
        )
        self.assertIn(
            run_campaign_module.ANCHOR_FALLBACK_MEMBER_REFUSAL,
            evaluation.failure_classes(),
        )
        self.assertTrue(evaluation.failed)
        self.assertFalse(evaluation.usable)
        self.assertTrue(evaluation.rerun_required)
        self.assertTrue(evaluation.to_log()["rerun_required"])

    def test_label_disagreement_is_strict_invalid_on_both_member_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "label-disagreement"
            shutil.copytree(Path("tests/fixtures/d078_r01"), bundle)
            summary_path = bundle / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["measurement_quality"]["telemetry_source"] = "mock"
            summary_path.write_text(
                json.dumps(summary, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            ordinary = self._evaluate(bundle, role="absolute_repeat")
            whole_window = self._whole_window_evaluate(
                bundle,
                role="absolute_repeat",
                waiver=False,
            )
        for evaluation in (ordinary, whole_window):
            with self.subTest(path=evaluation.config_name):
                self.assertFalse(evaluation.strict_valid)
                self.assertIn(
                    "bundle_strict_invalid",
                    evaluation.validation_problems,
                )

    def test_coordinated_mock_labels_cannot_override_custody_config(self):
        """D-138 containment lives at consumers of the pinned reducer."""

        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "coordinated-mock-labels"
            shutil.copytree(Path("tests/fixtures/d078_r01"), bundle)
            summary_path = bundle / "summary_metrics.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["measurement_quality"]["telemetry_source"] = "mock"
            summary_path.write_text(
                json.dumps(summary, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            metadata_path = bundle / "metadata.json"
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            metadata["adapters"]["telemetry"]["name"] = "mock"
            metadata_path.write_text(
                json.dumps(metadata, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            identity = whole_window_module.custody_telemetry_identity(
                bundle,
                summary=summary,
                metadata=metadata,
            )
            ordinary = self._evaluate(bundle, role="absolute_repeat")
            whole_window = self._whole_window_evaluate(
                bundle,
                role="absolute_repeat",
                waiver=False,
            )

        self.assertTrue(identity.custody_bound_config)
        self.assertEqual(identity.config_backend_class, "powermetrics")
        self.assertEqual(identity.metadata_backend_class, "mock")
        self.assertEqual(identity.summary_backend_class, "mock")
        self.assertFalse(identity.triangle_agrees)
        for evaluation in (ordinary, whole_window):
            with self.subTest(path=evaluation.config_name):
                self.assertFalse(evaluation.strict_valid)
                self.assertIn(
                    "bundle_strict_invalid",
                    evaluation.validation_problems,
                )

    def test_fully_anchored_floor_member_remains_usable(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle, _raw_summary = self._bundle(
                Path(tmp), "anchored-member", fallback=False
            )
            evaluation = self._evaluate(
                bundle, role="comparative_abba_member"
            )
        self.assertNotIn(
            run_campaign_module.ANCHOR_FALLBACK_MEMBER_REFUSAL,
            evaluation.collection_integrity_flags,
        )
        self.assertTrue(evaluation.usable)
        self.assertFalse(evaluation.rerun_required)

    def test_whole_window_floor_member_triggers_are_individually_unwaivable(self):
        for trigger in (
            "not_estimable",
            "clock_anchor_unresolved",
            "trace_fallback_method",
        ):
            with self.subTest(trigger=trigger), tempfile.TemporaryDirectory() as tmp:
                bundle = self._whole_window_trigger_bundle(
                    Path(tmp), f"whole-window-{trigger}", trigger
                )
                evaluation = self._whole_window_evaluate(
                    bundle, role="absolute_repeat"
                )
            self.assertIn(
                run_campaign_module.ANCHOR_FALLBACK_MEMBER_REFUSAL,
                evaluation.collection_integrity_flags,
            )
            self.assertTrue(evaluation.rerun_required)
            self.assertTrue(evaluation.failed)
            self.assertFalse(evaluation.waived)
            self.assertFalse(evaluation.usable)

    def test_whole_window_comparative_abba_fallback_is_excluded(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = self._whole_window_trigger_bundle(
                Path(tmp), "whole-window-abba-fallback", "trace_fallback_method"
            )
            evaluation = self._whole_window_evaluate(
                bundle, role="comparative_abba_member"
            )
        self.assertIn(
            run_campaign_module.ANCHOR_FALLBACK_MEMBER_REFUSAL,
            evaluation.collection_integrity_flags,
        )
        self.assertTrue(evaluation.rerun_required)
        self.assertTrue(evaluation.failed)
        self.assertFalse(evaluation.waived)


class ProductionUncertaintyAssertionTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.bundle = Path(self._tmp.name) / "bundle"
        (self.bundle / "raw").mkdir(parents=True)
        for name in (
            "powermetrics_idle.plist",
            "powermetrics.plist",
            "powermetrics_idle_post.plist",
        ):
            (self.bundle / "raw" / name).write_bytes(b"fixture")
        from tests.test_p2038_production_path import production_config

        self.config = production_config()
        self.metadata = {
            "uncertainty_evidence": {
                "schema_version": SCHEMA_FOR_ANCHOR_METHOD[
                    ACTIVE_CAPTURE_ANCHOR_METHOD
                ],
                "clock_anchor": {
                    "status": "bounded",
                    "method": ACTIVE_CAPTURE_ANCHOR_METHOD,
                },
                "sample_phase": {"status": "bounded"},
                "idle_drift": {
                    "status": "bounded",
                    "method": "pre_post_idle_observed_envelope_v1",
                },
            },
            "clock_anchor_bound_s": 0.03,
            "marker_to_first_sample_phase_bound_s": 0.01,
            "marker_to_last_sample_phase_bound_s": 0.01,
            "idle_drift_bound_w": 0.01,
            "instrument_calibration": {"verified_effective_b_fiducial_s": 0.04},
            "trace_window_margins": {
                "achieved_pre_window_margin_s": 0.5,
                "achieved_post_window_margin_s": 0.7,
            },
        }
        self.summary = {
            "status": "succeeded",
            "window_evidence_precheck": {
                "idle_subtracted_request": {"eligible": True, "reasons": []}
            },
            "energy_bound_terms_j": {"E_drift_bound_j": 0.01},
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": {
                    "method": "common_trace_shift_plus_independent_edge_span_v2",
                    "wall_minus_monotonic_independent_edge_span_s": 1.0e-5,
                }
            },
        }

    def _assertion(self):
        config = self.config
        metadata = self.metadata
        summary = self.summary

        class Reader:
            def __init__(self, _path):
                pass

            def config(self):
                return config

            def metadata(self):
                return metadata

            def raw_summary(self):
                return summary

        with patch.object(run_campaign_module, "BundleReader", Reader):
            return run_campaign_module.assert_production_uncertainty(
                self.bundle, allow_mock_runtime=True
            )

    def test_current_p2038_3_with_composed_margin_and_envelope_passes(self) -> None:
        result = self._assertion()
        self.assertEqual(result["clock_method"], self.metadata["uncertainty_evidence"]["clock_anchor"]["method"])
        # Three-term composed bound: bundle + fiducial + wall-minus-monotonic
        # edge span (confirmation-round-4 P1 pinned the two-term shortcut).
        self.assertAlmostEqual(
            result["composed_anchor_bound_s"], 0.07001, places=12
        )

    def test_spawn_envelope_only_evidence_is_rejected(self) -> None:
        self.metadata["uncertainty_evidence"]["schema_version"] = "p2-038.1"
        self.metadata["uncertainty_evidence"]["clock_anchor"][
            "method"
        ] = "powermetrics_spawn_ready_wall_monotonic_envelope_v1"
        with self.assertRaises(run_campaign_module.ShakedownGateError) as raised:
            self._assertion()
        self.assertEqual(raised.exception.code, "clock_evidence_missing")

    def test_retained_v2_evidence_is_rejected_at_the_production_gate(self) -> None:
        self.metadata["uncertainty_evidence"]["schema_version"] = "p2-038.2"
        self.metadata["uncertainty_evidence"]["clock_anchor"][
            "method"
        ] = "powermetrics_native_second_censored_intersection_v1"
        with self.assertRaises(run_campaign_module.ShakedownGateError) as raised:
            self._assertion()
        self.assertEqual(raised.exception.code, "clock_evidence_missing")

    def test_margin_below_composed_anchor_bound_is_rejected(self) -> None:
        self.metadata["trace_window_margins"]["achieved_post_window_margin_s"] = 0.06
        with self.assertRaises(run_campaign_module.ShakedownGateError) as raised:
            self._assertion()
        self.assertEqual(raised.exception.code, "clock_evidence_invalid")
        self.assertIn("trace pre/post margins", raised.exception.detail)


class CampaignCalibrationCustodyStoreTests(unittest.TestCase):
    """Production snapshot dispatch preserves exclusive custody modes."""

    _OMITTED = object()

    def test_bracket_binding_is_a_whole_window_only_cli_option(self) -> None:
        binding_path = Path("runs") / "calibration_bracket_binding.json"
        args = run_campaign_module.parse_args(
            [
                "--whole-window-verdict",
                "--bracket-binding",
                str(binding_path),
            ]
        )
        self.assertEqual(args.bracket_binding, str(binding_path))
        with self.assertRaises(SystemExit):
            run_campaign_module.parse_args(
                [
                    str(ROOT / "configs" / "examples"),
                    "--bracket-binding",
                    str(binding_path),
                ]
            )

    def test_verdict_output_is_a_whole_window_only_cli_option(self) -> None:
        output_path = Path("runs") / "whole_window_verdict.json"
        args = run_campaign_module.parse_args(
            [
                "--whole-window-verdict",
                "--whole-window-verdict-output",
                str(output_path),
            ]
        )
        self.assertEqual(args.whole_window_verdict_output, str(output_path))
        with self.assertRaises(SystemExit):
            run_campaign_module.parse_args(
                [
                    str(ROOT / "configs" / "examples"),
                    "--whole-window-verdict-output",
                    str(output_path),
                ]
            )

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.ledger = self.root / "ledger.jsonl"
        self.head = self.root / "head.json"
        self.head.write_text(
            json.dumps(
                {
                    "sequence": 0,
                    "head_digest": GENESIS_DIGEST,
                    "ledger_schema": LEDGER_SCHEMA,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.identity_epoch = {
            "os_build": "25F84",
            "hardware_model": "Mac15,9",
            "power_policy": "ac_high_power",
            "sampling_interval_ms": 100,
            "estimator_revision": "joint_loss_sublevel_interval_branch_v2",
            "pulse_protocol_id": "powermetrics_pulse_fiducial_v3",
        }
        self.t1_bindings = {
            field: f"value-{field}" for field in V2_BINDING_FIELDS
        }
        self.t1_bindings.update(self.identity_epoch)
        self.t1_bindings["anchor_method_version"] = ACTIVE_CAPTURE_ANCHOR_METHOD
        self.legacy_custody = self._write_custody("attempt-a")
        append_pending_receipt(
            self.ledger,
            attempt_id="attempt-a",
            custody_locator=str(self.legacy_custody),
            identity_epoch=self.identity_epoch,
            t1_bindings=self.t1_bindings,
            head_pin_path=self.head,
            require_committed_pin=False,
        )
        receipt = finalize_attempt_receipt(
            self.ledger,
            attempt_id="attempt-a",
            disposition="valid",
            custody_locator=str(self.legacy_custody),
            artifact_sha256=artifact_hashes(self.legacy_custody),
            identity_epoch=self.identity_epoch,
            t1_bindings=self.t1_bindings,
            capture_wall_time_s="99.0",
            exact_bound_lexeme_s="0.025",
        )
        self.head.write_text(
            json.dumps(head_pin_for_receipt(receipt)) + "\n",
            encoding="utf-8",
        )
        legacy_snapshot = self._load_actual()
        self.assertTrue(legacy_snapshot.valid)
        content_id = legacy_snapshot.observations[0].content_id
        assert content_id is not None
        self.store = self.root / "custody-store"
        self.store.mkdir()
        shutil.copytree(self.legacy_custody, self.store / content_id)
        (self.store / CUSTODY_STORE_MANIFEST_NAME).write_bytes(
            calibration_custody_store_manifest_bytes(legacy_snapshot)
        )
        self.content_id = content_id

    def _write_custody(self, attempt_id: str) -> Path:
        custody = self.root / "legacy" / attempt_id
        (custody / "raw").mkdir(parents=True)
        payloads = {
            "raw/powermetrics.plist": b"raw-attempt-a\n",
            "events.jsonl": b'{"timestamp_s":99.0}\n',
            "power_trace.csv": b"timestamp_s,power_w\n1,2\n",
            "instrument_evidence.json": b'{"attempt":"attempt-a"}\n',
            "manifest.json": b'{"attempt":"attempt-a"}\n',
        }
        for relative, raw in payloads.items():
            path = custody / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        return custody

    def _load_actual(self, store: Path | None = None):
        return load_calibration_ledger_snapshot(
            self.ledger,
            self.head,
            baseline_sequence=0,
            baseline_digest=GENESIS_DIGEST,
            require_committed_pin=False,
            repo_root=self.root,
            calibration_custody_store=store,
        )

    def _load_through_campaign(self, store=_OMITTED):
        calls = []

        def load_fixture_snapshot(**kwargs):
            calls.append(dict(kwargs))
            return load_calibration_ledger_snapshot(
                self.ledger,
                self.head,
                require_committed_pin=False,
                repo_root=self.root,
                **kwargs,
            )

        with (
            patch.object(
                run_campaign_module,
                "load_calibration_acceptance_bound",
                return_value={
                    "ledger_cutoff": {
                        "sequence": 0,
                        "head_digest": GENESIS_DIGEST,
                    }
                },
            ),
            patch.object(
                run_campaign_module,
                "load_calibration_ledger_snapshot",
                side_effect=load_fixture_snapshot,
            ),
        ):
            snapshot = (
                run_campaign_module._load_calibration_snapshot_for_evaluation()
                if store is self._OMITTED
                else run_campaign_module._load_calibration_snapshot_for_evaluation(
                    store
                )
            )
        self.assertEqual(len(calls), 1)
        return snapshot, calls[0]

    def _legacy_identities(self) -> set[str]:
        return {
            str((self.legacy_custody / relative).resolve())
            for relative in GOVERNED_ARTIFACTS
        }

    def _store_identities(self) -> set[str]:
        return {
            str((self.store / CUSTODY_STORE_MANIFEST_NAME).resolve()),
            *(
                str((self.store / self.content_id / relative).resolve())
                for relative in GOVERNED_ARTIFACTS
            ),
        }

    def test_store_dispatch_loads_store_without_locator_reads(self) -> None:
        args = run_campaign_module.parse_args(
            [
                "--whole-window-verdict",
                "--calibration-custody-store",
                str(self.store),
            ]
        )
        with V2AuthenticationReadSession() as session:
            snapshot, loader_arguments = self._load_through_campaign(
                args.calibration_custody_store
            )
        self.assertTrue(snapshot.valid)
        self.assertEqual(
            loader_arguments["calibration_custody_store"], self.store
        )
        self.assertLessEqual(self._store_identities(), set(session.records))
        self.assertTrue(self._legacy_identities().isdisjoint(session.records))

    def test_missing_legacy_locators_with_valid_store_passes(self) -> None:
        shutil.rmtree(self.legacy_custody)
        snapshot, _loader_arguments = self._load_through_campaign(self.store)
        self.assertTrue(snapshot.valid)
        self.assertEqual(snapshot.refusal_reasons, ())

    def test_store_routes_candidate_rediscovery_without_locator_fallback(
        self,
    ) -> None:
        snapshot, _loader_arguments = self._load_through_campaign(self.store)
        self.assertEqual(
            snapshot.receipts[-1]["custody_locator"],
            str(self.legacy_custody),
        )
        self.assertEqual(
            snapshot.observations[0].custody_locator,
            str(self.store / self.content_id),
        )
        with patch(
            "joulewise.calibration_bracketing.load_calibration_candidate",
            return_value=None,
        ) as candidate_loader:
            self.assertEqual(discover_calibration_candidates(snapshot), ())
        candidate_loader.assert_called_once_with(
            self.store / self.content_id,
            runs_root=self.root,
        )

    def test_invalid_store_refuses_without_legacy_fallback(self) -> None:
        self.assertTrue(self._load_actual().valid)
        (self.store / self.content_id / "power_trace.csv").unlink()
        with V2AuthenticationReadSession() as session:
            snapshot, _loader_arguments = self._load_through_campaign(self.store)
        self.assertEqual(
            snapshot.refusal_reasons,
            ("calibration_ledger_custody_invalid",),
        )
        self.assertTrue(self._legacy_identities().isdisjoint(session.records))

    def test_omitted_store_preserves_legacy_locator_dispatch(self) -> None:
        with V2AuthenticationReadSession() as session:
            snapshot, loader_arguments = self._load_through_campaign()
        self.assertTrue(snapshot.valid)
        self.assertNotIn("calibration_custody_store", loader_arguments)
        self.assertLessEqual(self._legacy_identities(), set(session.records))
        self.assertTrue(self._store_identities().isdisjoint(session.records))

    def test_store_option_refuses_semantics_that_would_ignore_it(self) -> None:
        with self.assertRaises(SystemExit):
            run_campaign_module.parse_args(
                [
                    "--whole-window-verdict",
                    "--calibration-custody-store",
                    str(self.store),
                    "--consumption-semantics-id",
                    run_campaign_module.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID,
                ]
            )


class IdleAdmissionCoreVerdictTests(unittest.TestCase):
    """T0.5 idle-admission core: sidecar binding + campaign-verdict surface."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def _write_extended_sidecar(
        self, profile: str = "production", mutate=None
    ) -> Path:
        source = (
            ROOT
            / "configs"
            / "campaign_policies"
            / (
                "quiet_mac_p2_production.json"
                if profile == "production"
                else "quiet_mac_exploratory.json"
            )
        )
        payload = json.loads(source.read_text(encoding="utf-8"))
        payload["idle_admission_extension"] = _idle_admission_extension_mapping(
            profile
        )
        if mutate is not None:
            mutate(payload)
        path = self.root / f"policy_{profile}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return path

    def _binding(self, *, profile: str = "production"):
        return run_campaign_module.load_campaign_policy(
            str(self._write_extended_sidecar(profile))
        )

    def _drift_bound(
        self,
        points: list[float] | None = None,
        *,
        derived_at_s: float | None = None,
        launch_lineage: dict | None = None,
    ) -> dict:
        corpus_path = (
            ROOT
            / "configs"
            / "campaigns"
            / "neg8_reference_corpus"
            / "derivation"
            / "settled_corpus.json"
        )
        corpus_raw = corpus_path.read_bytes()
        corpus = json.loads(corpus_raw)
        values = points if points is not None else [
            8.0 + 0.01 * index for index in range(len(corpus["members"]))
        ]
        return run_campaign_module.build_neg8_drift_bound_artifact(
            corpus_id=corpus["corpus_id"],
            condition_id=corpus["condition_id"],
            manifest_sha256=hashlib.sha256(corpus_raw).hexdigest(),
            scientific_config_sha256="b" * 64,
            members=[
                {
                    "bundle_id": corpus_member["bundle_id"],
                    "point_gross_j": point,
                    "point_idle_subtracted_j": point - 0.2,
                    "bundle_evidence_sha256": hashlib.sha256(
                        corpus_member["bundle_id"].encode()
                    ).hexdigest(),
                }
                for corpus_member, point in zip(corpus["members"], values)
            ],
            derivation_timestamp_s=(
                time.time() if derived_at_s is None else derived_at_s
            ),
            freshness_bindings={
                "os_build": "25F84",
                "power_supply_identity_sha256": canonical_sha256(
                    {
                        "power_source": "AC Power",
                        "adapter_watts": 140.0,
                        "adapter_description": "140W USB-C Power Adapter",
                    }
                ),
                "calibration_identity_sha256": "c" * 64,
            },
            launch_lineage=launch_lineage,
        )

    def _write_drift_bound(
        self,
        points: list[float] | None = None,
        *,
        launch_lineage: dict | None = None,
    ) -> Path:
        path = self.root / "neg8-drift-bound.json"
        path.write_text(
            json.dumps(
                self._drift_bound(points, launch_lineage=launch_lineage),
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return path

    def _bound_for_manifest_bytes(self, manifest_raw: bytes) -> dict:
        manifest = json.loads(manifest_raw)
        return run_campaign_module.build_neg8_drift_bound_artifact(
            corpus_id=manifest["corpus_id"],
            condition_id=manifest["condition_id"],
            manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
            scientific_config_sha256="b" * 64,
            members=[
                {
                    "bundle_id": member["bundle_id"],
                    "point_gross_j": 8.0 + index / 100.0,
                    "point_idle_subtracted_j": 7.0 + index / 100.0,
                    "bundle_evidence_sha256": hashlib.sha256(
                        member["bundle_id"].encode()
                    ).hexdigest(),
                }
                for index, member in enumerate(manifest["members"])
            ],
            derivation_timestamp_s=time.time(),
            freshness_bindings={
                "os_build": "25F84",
                "power_supply_identity_sha256": "c" * 64,
                "calibration_identity_sha256": "d" * 64,
            },
        )

    def _unregistered_manifest_bytes(self) -> bytes:
        return (
            json.dumps(
                {
                    "schema_version": "joulewise.neg8_reference_corpus.v1",
                    "corpus_id": "unregistered-corpus",
                    "freeze_status": "settled_reference",
                    "condition_id": "df-rq-mid",
                    "members": [
                        {
                            "bundle_id": f"unregistered-{index:02d}",
                            "bundle_path": f"run-{index:02d}",
                        }
                        for index in range(10)
                    ],
                },
                sort_keys=True,
            )
            + "\n"
        ).encode()

    def _member(
        self,
        bundle_id: str,
        *,
        records: list[dict] | None,
        adapter_watts=140,
        adapter_description="140W USB-C Power Adapter",
        gross_energy_j: float | None = None,
        gross_half_width_j: float = 0.0,
        idle_subtracted_energy_j: float | None = None,
        admission_decision: str | None = "admitted",
        scientific_sampling_hz: float = 10.0,
        neg8_position: str | None = None,
        os_build: str = "25F84",
        calibration_identity_sha256: str = "c" * 64,
    ):
        bundle_path = self.root / bundle_id
        bundle_path.mkdir(parents=True, exist_ok=True)
        config = json.loads(
            (
                ROOT
                / "configs"
                / "campaigns"
                / "p2_015_floors"
                / "00_neg8_start"
                / "p2015-neg8-reference-start.json"
            ).read_text(encoding="utf-8")
        )
        config["run_id"] = bundle_id
        config["sampling"]["power_hz"] = scientific_sampling_hz
        (bundle_path / "config.json").write_text(
            json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        if records is not None:
            (bundle_path / "rich_telemetry_idle.jsonl").write_text(
                "".join(json.dumps(record) + "\n" for record in records)
            )
        metadata: dict = {
            "campaign_environment_preflight": {
                "snapshot": {"build_version": os_build}
            },
            "instrument_calibration": {
                "artifact_sha256": calibration_identity_sha256
            },
            "environment": {
                "power_source": "AC Power",
                "power": {
                    "adapter_watts": adapter_watts,
                    "adapter_description": adapter_description,
                },
                "post_run_observation": {
                    "capture_skipped": False,
                    "display_power_state": "all_asleep",
                    "screensaver_engaged": False,
                    "power_source": "AC Power",
                    "power": {
                        "adapter_watts": adapter_watts,
                        "adapter_description": adapter_description,
                    },
                    "errors": {},
                },
            }
        }
        if admission_decision is not None:
            metadata["environment_admission"] = {
                "schema_version": "joulewise.environment_admission.v1",
                "critical_environment_passed": True,
                "reference_provenance_present": True,
                "per_run_environment_evaluation": {
                    "schema_version": "joulewise.environment_evaluation.v1",
                    "eligible": True,
                    "snapshot_sha256": "ab" * 32,
                },
                "decision": admission_decision,
                "claim_reason": (
                    None
                    if admission_decision == "admitted"
                    else "environment_admission_failed"
                ),
                "attempts": [
                    {
                        "attempt": 1,
                        "admitted": admission_decision == "admitted",
                        "cpu_admission_enforced": True,
                        "cpu_admission": {
                            "admitted": admission_decision == "admitted"
                        },
                    }
                ],
                "guard_observations": [
                    {
                        "phase": phase,
                        "capture_skipped": False,
                        "display_power_state": "all_asleep",
                        "screensaver_engaged": False,
                        "errors": {},
                    }
                    for phase in ("before_attempt_1", "after_attempt_1")
                ],
            }
        summary = {}
        if gross_energy_j is not None:
            if idle_subtracted_energy_j is None:
                idle_subtracted_energy_j = gross_energy_j - 0.2
            summary = {
                "gross_energy_j": gross_energy_j,
                "idle_subtracted_energy_j": idle_subtracted_energy_j,
                "energy_anchor_shift_envelopes": {
                    "/gross_energy_j": {
                        "point_j": gross_energy_j,
                        "lower_j": gross_energy_j - gross_half_width_j,
                        "upper_j": gross_energy_j + gross_half_width_j,
                    }
                },
            }
        normalized = run_campaign_module._normalized_benchmark_config(config)
        return run_campaign_module.MemberEvaluation(
            bundle_id=bundle_id,
            bundle_path=bundle_path,
            config_name=f"{bundle_id}.json",
            status="succeeded",
            strict_valid=True,
            summary=summary,
            metadata=metadata,
            declared_role=(
                run_campaign_module.NEG8_REFERENCE_ROLE
                if neg8_position is not None
                else None
            ),
            sentinel_position=neg8_position,
            scientific_config_sha256=(
                run_campaign_module._scientific_config_sha256(normalized)
                if neg8_position is not None
                else None
            ),
            canonical_neg8_workload=(
                run_campaign_module._declares_canonical_neg8_workload(normalized)
                if neg8_position is not None
                else False
            ),
        )

    def test_load_campaign_policy_parses_and_hash_binds_extension(self) -> None:
        path = self._write_extended_sidecar("production")
        binding = run_campaign_module.load_campaign_policy(str(path))
        self.assertIsNotNone(binding.idle_admission_extension)
        self.assertTrue(binding.idle_admission_extension.claim_bearing)
        self.assertEqual(
            binding.sha256, hashlib.sha256(path.read_bytes()).hexdigest()
        )
        metadata = binding.to_metadata()
        self.assertEqual(
            metadata["idle_admission_extension"]["schema_version"],
            "joulewise.idle_admission_extension.v1",
        )
        # Byte-hash enforcement: changing one new field changes the campaign
        # policy identity (binding hash) and the extension hash.
        changed = self._write_extended_sidecar(
            "production",
            mutate=lambda payload: payload["idle_admission_extension"][
                "cpu_criteria"
            ].update(cpu_busy_ratio_p95_max=0.6),
        )
        rebound = run_campaign_module.load_campaign_policy(str(changed))
        self.assertNotEqual(binding.sha256, rebound.sha256)
        self.assertNotEqual(
            metadata["idle_admission_extension"]["sha256"],
            rebound.to_metadata()["idle_admission_extension"]["sha256"],
        )

    def test_governed_neg8_bound_derivation_cli_writes_sealed_artifact(self) -> None:
        artifact = self._drift_bound()
        corpus = self.root / "settled-corpus.json"
        corpus.write_text("{}\n", encoding="utf-8")
        output = self.root / "derived-bound.json"
        args = run_campaign_module.parse_args(
            [
                "--derive-neg8-drift-bound",
                str(corpus),
                "--neg8-drift-bound-output",
                str(output),
                "--runs-dir",
                str(self.root),
            ]
        )
        with (
            patch.object(
                run_campaign_module,
                "mint_neg8_drift_bound_artifact",
                return_value=artifact,
            ) as mint,
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(
                run_campaign_module.run_derive_neg8_drift_bound(args), 0
            )
        mint.assert_called_once_with(self.root, corpus)
        emitted = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(emitted, artifact)
        self.assertTrue(
            run_campaign_module.validate_neg8_drift_bound_artifact(emitted)
        )

    def _install_neg8_reference_derivation_fixture(self):
        campaign_dir = (
            ROOT / "configs" / "campaigns" / "neg8_reference_corpus"
        )
        corpus_path = campaign_dir / "derivation" / "settled_corpus.json"
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        order = json.loads(
            (campaign_dir / "order_manifest.json").read_text(encoding="utf-8")
        )
        member_ids = [
            member["bundle_id"] for member in corpus["members"]
        ]
        self.assertEqual(
            member_ids,
            [entry["run_id"] for entry in order["executed_order"]],
        )
        reference_condition = json.loads(
            (
                ROOT
                / "configs"
                / "campaigns"
                / "p2_015_floors"
                / "00_neg8_start"
                / "p2015-neg8-reference-start.json"
            ).read_text(encoding="utf-8")
        )
        reference_condition.pop("run_id")

        for index, member in enumerate(corpus["members"], start=1):
            bundle_id = member["bundle_id"]
            bundle = self.root / member["bundle_path"]
            bundle.mkdir()
            config_raw = (
                campaign_dir / f"{bundle_id}.json"
            ).read_bytes()
            config = json.loads(config_raw)
            self.assertEqual(config["run_id"], bundle_id)
            scientific_condition = dict(config)
            scientific_condition.pop("run_id")
            self.assertEqual(scientific_condition, reference_condition)
            (bundle / "config.json").write_bytes(config_raw)
            (bundle / "metadata.json").write_text(
                json.dumps(
                    {
                        "config_sha256": hashlib.sha256(
                            config_raw
                        ).hexdigest(),
                        "adapters": {
                            "telemetry": {"name": "powermetrics"}
                        },
                        "campaign_environment_preflight": {
                            "snapshot": {"build_version": "25F84"}
                        },
                        "environment": {
                            "power_source": "AC Power",
                            "power": {
                                "adapter_watts": 140,
                                "adapter_description": (
                                    "140W USB-C Power Adapter"
                                ),
                            },
                        },
                        "instrument_calibration": {
                            "artifact_sha256": "c" * 64
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            point_j = 8.0 + index / 100.0
            summary = {
                "status": "succeeded",
                "gross_energy_j": point_j,
                "idle_subtracted_energy_j": point_j - 0.2,
                "energy_anchor_shift_envelopes": {
                    "/gross_energy_j": {
                        "point_j": point_j,
                        "lower_j": point_j - 0.01,
                        "upper_j": point_j + 0.01,
                    }
                },
                "summary_provenance": {"reducer_version": "0.5.2"},
                "measurement_quality": {
                    "telemetry_source": "powermetrics"
                },
                "window_evidence_precheck": {
                    "gross_request": {"eligible": True},
                    "idle_subtracted_request": {"eligible": True},
                },
            }
            (bundle / "summary_metrics.json").write_text(
                json.dumps(summary) + "\n", encoding="utf-8"
            )

        class SyntheticReduction:
            def __init__(self, value):
                self.value = value

            def to_dict(self):
                return self.value

        def reduce_synthetic_bundle(bundle_path, *, reducer_version):
            self.assertEqual(reducer_version, "0.5.2")
            return SyntheticReduction(
                json.loads(
                    (Path(bundle_path) / "summary_metrics.json").read_text(
                        encoding="utf-8"
                    )
                )
            )

        return corpus_path, member_ids, reduce_synthetic_bundle

    def test_neg8_reference_campaign_corpus_is_accepted_by_derivation_cli(
        self,
    ) -> None:
        (
            corpus_path,
            member_ids,
            reduce_synthetic_bundle,
        ) = self._install_neg8_reference_derivation_fixture()

        output = self.root / "derived-bound.json"
        args = run_campaign_module.parse_args(
            [
                "--derive-neg8-drift-bound",
                str(corpus_path),
                "--neg8-drift-bound-output",
                str(output),
                "--runs-dir",
                str(self.root),
            ]
        )
        with (
            patch(
                "joulewise.reduce.reduce_bundle",
                side_effect=reduce_synthetic_bundle,
            ),
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(
                run_campaign_module.run_derive_neg8_drift_bound(args), 0
            )
        artifact = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(
            artifact["reference_corpus"]["member_ids"], member_ids
        )
        self.assertEqual(artifact["estimator"]["n"], 12)
        self.assertTrue(
            run_campaign_module.validate_neg8_drift_bound_artifact(artifact)
        )

    def test_derivation_cli_mint_rejects_source_identity_postcondition_failure(
        self,
    ) -> None:
        (
            corpus_path,
            _member_ids,
            reduce_synthetic_bundle,
        ) = self._install_neg8_reference_derivation_fixture()
        real_build = whole_window_module.build_neg8_drift_bound_artifact

        def build_with_self_sealed_wrong_manifest(**kwargs):
            return real_build(
                **{**kwargs, "manifest_sha256": "f" * 64}
            )

        output = self.root / "must-not-mint.json"
        args = run_campaign_module.parse_args(
            [
                "--derive-neg8-drift-bound",
                str(corpus_path),
                "--neg8-drift-bound-output",
                str(output),
                "--runs-dir",
                str(self.root),
            ]
        )
        with (
            patch(
                "joulewise.reduce.reduce_bundle",
                side_effect=reduce_synthetic_bundle,
            ),
            patch.object(
                whole_window_module,
                "build_neg8_drift_bound_artifact",
                side_effect=build_with_self_sealed_wrong_manifest,
            ),
            redirect_stdout(io.StringIO()),
            self.assertRaisesRegex(
                ValueError,
                "corpus identity did not bind to manifest bytes",
            ),
        ):
            run_campaign_module.run_derive_neg8_drift_bound(args)
        self.assertFalse(output.exists())

    def test_prospective_window_reference_configs_are_same_condition_3_1_3(
        self,
    ) -> None:
        root = ROOT / "configs" / "campaigns" / "window_references"
        reference = json.loads(
            (
                ROOT
                / "configs"
                / "campaigns"
                / "p2_015_floors"
                / "00_neg8_start"
                / "p2015-neg8-reference-start.json"
            ).read_text(encoding="utf-8")
        )
        reference.pop("run_id")
        expected = {
            "start_triplet": (3, "start"),
            "midpoint": (1, "midpoint"),
            "end_triplet": (3, "end"),
        }
        observed_run_ids = set()
        for directory, (count, position) in expected.items():
            manifest = json.loads(
                (root / directory / "order_manifest.json").read_text(
                    encoding="utf-8"
                )
            )
            entries = manifest["executed_order"]
            self.assertEqual(manifest["planned_n_bundles"], count)
            self.assertEqual(len(entries), count)
            self.assertEqual(
                {entry["sentinel_position"] for entry in entries},
                {position},
            )
            for entry in entries:
                config = json.loads(
                    (root / directory / entry["config"]).read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(config["run_id"], entry["run_id"])
                self.assertNotIn(config["run_id"], observed_run_ids)
                observed_run_ids.add(config["run_id"])
                config.pop("run_id")
                self.assertEqual(config, reference)
        self.assertEqual(len(observed_run_ids), 7)

    def test_neg8_bound_builder_requires_ten_members_and_detects_tampering(
        self,
    ) -> None:
        artifact = self._drift_bound()
        self.assertGreaterEqual(artifact["estimator"]["n"], 10)
        tampered = json.loads(json.dumps(artifact))
        tampered["bound_j"] += 1.0
        self.assertFalse(
            run_campaign_module.validate_neg8_drift_bound_artifact(tampered)
        )
        with self.assertRaisesRegex(ValueError, "n >= 10"):
            self._drift_bound([8.0 + index * 0.01 for index in range(9)])

    def test_drift_bound_corpus_identity_requires_external_bytes(self) -> None:
        artifact = self._drift_bound()
        self.assertTrue(
            run_campaign_module.validate_neg8_drift_bound_artifact(
                artifact, require_corpus_identity=True
            )
        )

        forged = run_campaign_module.build_neg8_drift_bound_artifact(
            corpus_id="self-asserted-corpus",
            condition_id="df-rq-mid",
            manifest_sha256="a" * 64,
            scientific_config_sha256="b" * 64,
            members=[
                {
                    "bundle_id": f"forged-{index:02d}",
                    "point_gross_j": 8.0 + index / 100.0,
                    "point_idle_subtracted_j": 7.0 + index / 100.0,
                    "bundle_evidence_sha256": hashlib.sha256(
                        f"forged-{index:02d}".encode()
                    ).hexdigest(),
                }
                for index in range(10)
            ],
            derivation_timestamp_s=time.time(),
            freshness_bindings={
                "os_build": "25F84",
                "power_supply_identity_sha256": "c" * 64,
                "calibration_identity_sha256": "d" * 64,
            },
        )
        self.assertTrue(
            run_campaign_module.validate_neg8_drift_bound_artifact(forged)
        )
        self.assertFalse(
            run_campaign_module.validate_neg8_drift_bound_artifact(
                forged, require_corpus_identity=True
            )
        )
        forged_path = self.root / "self-asserted-bound.json"
        forged_path.write_text(json.dumps(forged) + "\n", encoding="utf-8")
        self.assertIsNone(
            run_campaign_module.load_neg8_drift_bound_artifact(forged_path)
        )

    def test_untracked_sibling_manifest_cannot_authenticate_forged_corpus(
        self,
    ) -> None:
        manifest_raw = self._unregistered_manifest_bytes()
        artifact = self._bound_for_manifest_bytes(manifest_raw)
        registry = self.root / "registry"
        registry.mkdir()
        (registry / "untracked.json").write_bytes(manifest_raw)

        self.assertTrue(
            run_campaign_module.validate_neg8_drift_bound_artifact(artifact)
        )
        with patch.object(
            whole_window_module,
            "REGISTERED_NEG8_REFERENCE_CORPUS_DIR",
            registry,
        ):
            self.assertFalse(
                run_campaign_module.validate_neg8_drift_bound_artifact(
                    artifact, require_corpus_identity=True
                )
            )

    def test_claim_row_rejects_structurally_valid_unregistered_drift_corpus(
        self,
    ) -> None:
        forged = self._bound_for_manifest_bytes(
            self._unregistered_manifest_bytes()
        )
        policy_sha = "a" * 64
        family = {"drift_allowance_j": 0.1}
        families = {
            "gross_energy": dict(family),
            "idle_subtracted_energy": dict(family),
        }
        bracket_policy = {"require_bracket": True}
        bracket = {
            "schema_version": whole_window_module.NEG8_BRACKET_SCHEMA,
            "estimand": whole_window_module.NEG8_POINT_DRIFT_ESTIMAND,
            "decision": "passed",
            "policy": bracket_policy,
            "claim_families": families,
            "drift_bound_artifact": forged,
            "bound_freshness": {},
        }
        source_raw = b"{}\n"
        row = {
            "schema_version": whole_window_module.WHOLE_WINDOW_SCHEMA,
            "consumption_semantics_id": MINTED_CONSUMPTION_SEMANTICS_ID,
            "bundle_ids": ["member-1"],
            "campaign_policy": {"sha256": policy_sha},
            "row_provenance": {
                "schema_version": (
                    whole_window_module.WHOLE_WINDOW_PROVENANCE_SCHEMA
                ),
                "policy_sha256": policy_sha,
                "membership_sha256": canonical_sha256(["member-1"]),
                "source_campaign_manifests": [
                    {
                        "path": "campaign_manifests/source.json",
                        "sha256": hashlib.sha256(source_raw).hexdigest(),
                    }
                ],
            },
            "status": "passed",
            "idle_admission_core": {
                "schema_version": whole_window_module.IDLE_ADMISSION_CORE_SCHEMA,
                "policy_sha256": policy_sha,
                "neg8_bracket": bracket,
                "adapter_wattage_continuity": {
                    "schema_version": whole_window_module.ADAPTER_CONTINUITY_SCHEMA,
                    "decision": "stable",
                },
                "members": [
                    {
                        "bundle_id": "member-1",
                        "cpu_admission": {"decision": "admitted"},
                    }
                ],
            },
        }
        authenticated_source = Mock(
            raw_bytes=source_raw,
            value={"campaign_policy": {"sha256": policy_sha}},
        )
        session = Mock(
            ready=True,
            runs_root=self.root,
            referenced_bundle_ids=frozenset({"member-1"}),
            evaluation_basis_sha256=None,
            _row_validation_results={},
        )
        derived = {
            "decision": "passed",
            "claim_families": copy.deepcopy(families),
            "bound_freshness": {},
        }

        with (
            patch.object(
                whole_window_module,
                "load_authenticated_campaign_manifest",
                return_value=authenticated_source,
            ),
            patch.object(
                whole_window_module,
                "_manifest_members",
                return_value={"member-1"},
            ),
            patch.object(
                whole_window_module,
                "_current_core_rederivation_reasons",
                return_value=set(),
            ),
            patch.object(
                whole_window_module,
                "_registered_bracket_policy",
                return_value=bracket_policy,
            ),
            patch.object(
                whole_window_module,
                "_row_references_current_strict_member",
                return_value=True,
            ),
            patch.object(
                whole_window_module,
                "_derived_neg8_decision",
                return_value=(derived, None),
            ),
        ):
            valid, reasons = whole_window_module._validate_row(
                row,
                self.root,
                {"member-1"},
                consumption_session=session,
            )

        self.assertFalse(valid)
        self.assertEqual(
            reasons, ("whole_window_verdict_provenance_invalid",)
        )

    def test_drift_bound_accepts_exact_custodied_manifest_bytes(self) -> None:
        members = [
            {"bundle_id": f"custody-{index:02d}", "bundle_path": f"run-{index:02d}"}
            for index in range(10)
        ]
        manifest_raw = (
            json.dumps(
                {
                    "schema_version": "joulewise.neg8_reference_corpus.v1",
                    "corpus_id": "custodied-corpus",
                    "freeze_status": "settled_reference",
                    "condition_id": "df-rq-mid",
                    "members": members,
                },
                sort_keys=True,
            )
            + "\n"
        ).encode()
        artifact = run_campaign_module.build_neg8_drift_bound_artifact(
            corpus_id="custodied-corpus",
            condition_id="df-rq-mid",
            manifest_sha256=hashlib.sha256(manifest_raw).hexdigest(),
            scientific_config_sha256="b" * 64,
            members=[
                {
                    "bundle_id": member["bundle_id"],
                    "point_gross_j": 8.0 + index / 100.0,
                    "point_idle_subtracted_j": 7.0 + index / 100.0,
                    "bundle_evidence_sha256": hashlib.sha256(
                        member["bundle_id"].encode()
                    ).hexdigest(),
                }
                for index, member in enumerate(members)
            ],
            derivation_timestamp_s=time.time(),
            freshness_bindings={
                "os_build": "25F84",
                "power_supply_identity_sha256": "c" * 64,
                "calibration_identity_sha256": "d" * 64,
            },
        )
        self.assertTrue(
            run_campaign_module.validate_neg8_drift_bound_artifact(
                artifact,
                reference_corpus_bytes=manifest_raw,
                require_corpus_identity=True,
            )
        )

    def test_superseded_gross_only_bound_shape_is_intentionally_not_replayable(
        self,
    ) -> None:
        historical_gross_only = self._drift_bound()
        del historical_gross_only["claim_family_bounds"]
        del historical_gross_only["freshness"]
        self.assertFalse(
            run_campaign_module.validate_neg8_drift_bound_artifact(
                historical_gross_only
            )
        )

    def test_extension_version_and_profile_constraints_fail_closed(self) -> None:
        from joulewise.schemas import SchemaError

        tampered = self._write_extended_sidecar(
            "production",
            mutate=lambda payload: payload["idle_admission_extension"].update(
                schema_version="joulewise.idle_admission_extension.v0"
            ),
        )
        with self.assertRaises(SchemaError):
            run_campaign_module.load_campaign_policy(str(tampered))
        loosened = self._write_extended_sidecar(
            "production",
            mutate=lambda payload: payload["idle_admission_extension"][
                "cpu_criteria"
            ].update(on_missing_telemetry="flag"),
        )
        with self.assertRaises(SchemaError):
            run_campaign_module.load_campaign_policy(str(loosened))

    def test_sidecar_without_extension_yields_named_condition(self) -> None:
        binding = run_campaign_module.load_campaign_policy(
            str(ROOT / "tests" / "fixtures" / "campaign_policy_test.json")
        )
        self.assertIsNone(binding.idle_admission_extension)
        section = run_campaign_module.idle_admission_core_verdict([], binding)
        self.assertEqual(
            section["conditions"], ["idle_admission_extension_unconfigured"]
        )
        self.assertIsNone(section["extension"])

    def test_post_run_environment_condition_is_claim_barrier(self) -> None:
        core = {
            "conditions": ["environment_admission_failed"],
            "members": [{"cpu_admission": {"decision": "admitted"}}],
            "adapter_wattage_continuity": {"decision": "stable"},
            "neg8_bracket": {"decision": "passed"},
        }
        self.assertIn(
            "environment_admission_failed",
            run_campaign_module._idle_admission_claim_barrier_reasons(core),
        )

    def test_idle_admission_core_verdict_golden_characterization(self) -> None:
        binding = self._binding()
        core = run_campaign_module.idle_admission_core_verdict(
            [self._member("golden-member", records=_clean_idle_records())],
            binding,
            evaluation_timestamp_s=1_786_118_400.0,
        )

        self.assertEqual(
            canonical_sha256(core),
            "e7df882bc294a55756f3d791829657eb207d0ca82d4c2208ad6493d029fd7a87",
        )

    def test_prospective_member_failure_namespace_is_frozen(self) -> None:
        self.assertEqual(
            run_campaign_module.PROSPECTIVE_MEMBER_FAILURE_REASON_CODES,
            (
                "cpu_admission_unenforced",
                "cpu_baseline_sample_count_insufficient",
                "cpu_baseline_telemetry_malformed",
                "cpu_baseline_telemetry_missing",
                "cpu_busy_ratio_p95_exceeded",
                "environment_admission_failed",
                "environment_admission_missing",
                "gpu_idle_admission_not_passed",
                "gpu_idle_admission_unknown",
                "idle_admission_attempt_ledger_invalid",
                "processor_combined_power_w_p95_exceeded",
                "thermal_pressure_elevated_in_window",
                "whole_window_bundle_invalid",
            ),
        )

    def test_canonical_member_failures_deduplicates_direct_duplicates(
        self,
    ) -> None:
        # Delta-audit P2: duplicates fed DIRECTLY through the writer-side
        # canonicalizer, so a no-dedup sorted implementation fails here
        # (upstream set-normalization cannot mask it).
        record = {
            "member_id": "m1",
            "reason_code": "environment_admission_failed",
            "detail": "d",
        }
        out = run_campaign_module._canonical_member_failures(
            [dict(record), dict(record), dict(record)]
        )
        self.assertEqual(out, [record])

    def test_conflicting_member_failure_details_drop_the_pair_only(
        self,
    ) -> None:
        keep = {
            "member_id": "m2",
            "reason_code": "whole_window_bundle_invalid",
            "detail": "kept",
        }
        out = run_campaign_module._canonical_member_failures(
            [
                {
                    "member_id": "m1",
                    "reason_code": "environment_admission_failed",
                    "detail": "first",
                },
                {
                    "member_id": "m1",
                    "reason_code": "environment_admission_failed",
                    "detail": "second",
                },
                dict(keep),
            ]
        )
        self.assertEqual(out, [keep])

    def test_undeclared_or_blank_member_failure_degrades_to_none(
        self,
    ) -> None:
        # The verdict row must never be suppressed by its own diagnostics:
        # an undeclared code or unrepresentable detail skips the record
        # instead of raising on the emitter path.
        self.assertIsNone(
            run_campaign_module._member_failure_record(
                "m1", "code_not_in_the_frozen_namespace", "detail"
            )
        )
        self.assertIsNone(
            run_campaign_module._member_failure_record(
                "m1", "environment_admission_failed", "   "
            )
        )
        self.assertIsNotNone(
            run_campaign_module._member_failure_record(
                "m1", "environment_admission_failed", "detail"
            )
        )

    def test_member_failures_map_environment_ledger_and_cpu_to_member(
        self,
    ) -> None:
        binding = self._binding()
        member = self._member(
            "mapped-member", records=_clean_idle_records()
        )
        with (
            patch.object(
                run_campaign_module,
                "_current_member_environment_refusals",
                return_value=("environment_admission_failed",),
            ),
            patch.object(
                run_campaign_module,
                "_final_idle_admission_attempt",
                return_value=None,
            ),
        ):
            result = run_campaign_module._idle_admission_core_evaluation(
                [member], binding
            )

        self.assertEqual(
            [
                (failure["member_id"], failure["reason_code"])
                for failure in result.member_failures
            ],
            [
                ("mapped-member", "cpu_baseline_telemetry_missing"),
                ("mapped-member", "environment_admission_failed"),
                (
                    "mapped-member",
                    "idle_admission_attempt_ledger_invalid",
                ),
            ],
        )
        self.assertTrue(
            all(
                failure["detail"]
                and len(failure["detail"])
                <= run_campaign_module.MEMBER_FAILURE_DETAIL_MAX_CHARS
                for failure in result.member_failures
            )
        )

    def test_member_failures_are_complete_deduplicated_and_sorted(self) -> None:
        binding = self._binding()
        records = [
            {
                "processor_combined_power_w": 1.2,
                "clusters": [
                    {
                        "cpus": [
                            {"idle_ratio": 0.05, "down_ratio": 0.0}
                        ]
                    }
                ],
            }
            for _ in range(5)
        ]
        members = [
            self._member(bundle_id, records=records)
            for bundle_id in ("z-member", "a-member")
        ]
        with patch.object(
            run_campaign_module,
            "_current_member_environment_refusals",
            return_value=(
                "environment_admission_failed",
                "environment_admission_failed",
            ),
        ):
            result = run_campaign_module._idle_admission_core_evaluation(
                members, binding
            )

        observed = [
            (failure["member_id"], failure["reason_code"])
            for failure in result.member_failures
        ]
        expected = [
            (member_id, reason_code)
            for member_id in ("a-member", "z-member")
            for reason_code in (
                "cpu_busy_ratio_p95_exceeded",
                "environment_admission_failed",
                "processor_combined_power_w_p95_exceeded",
            )
        ]
        self.assertEqual(observed, expected)
        self.assertEqual(len(observed), len(set(observed)))

    def test_global_neg8_condition_has_no_fabricated_member_failure(
        self,
    ) -> None:
        binding = self._binding()
        result = run_campaign_module._idle_admission_core_evaluation(
            [self._member("clean-member", records=_clean_idle_records())],
            binding,
        )

        self.assertIn(
            "neg8_bracket_not_evaluated", result.core["conditions"]
        )
        self.assertEqual(result.member_failures, ())

    def test_clean_members_pass_with_stable_wattage_and_neg8_bracket(self) -> None:
        binding = self._binding()
        drift_bound = self._drift_bound()
        evaluations = [
            self._member(
                "p2-neg8-reference-start__r1",
                records=_clean_idle_records(),
                gross_energy_j=8.0,
                neg8_position="start",
            ),
            self._member("p2-work-a__r1", records=_clean_idle_records()),
            self._member(
                "p2-neg8-reference-end__r1",
                records=_clean_idle_records(),
                gross_energy_j=8.04,
                neg8_position="end",
            ),
        ]
        section = run_campaign_module.idle_admission_core_verdict(
            evaluations, binding, neg8_drift_bound=drift_bound
        )
        self.assertEqual(section["conditions"], [])
        self.assertTrue(
            all(row["cpu_admission"]["admitted"] for row in section["members"])
        )
        self.assertEqual(
            section["adapter_wattage_continuity"]["decision"], "stable"
        )
        self.assertEqual(section["neg8_bracket"]["decision"], "passed")
        self.assertEqual(
            section["neg8_bracket"]["bound_freshness"]["decision"],
            "fresh",
        )
        self.assertAlmostEqual(section["neg8_bracket"]["abs_delta_j"], 0.04)
        self.assertEqual(
            section["neg8_bracket"]["drift_bound_artifact"][
                "derivation_sha256"
            ],
            drift_bound["derivation_sha256"],
        )
        self.assertIsNotNone(
            section["neg8_reference_scientific_config_sha256"]
        )

    def test_neg8_bound_horizon_expiry_refuses_as_stale(self) -> None:
        binding = self._binding()
        expired = self._drift_bound(
            derived_at_s=time.time() - NEG8_DRIFT_BOUND_MAX_AGE_S - 1.0
        )
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "neg8-expired-start",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    neg8_position="start",
                ),
                self._member(
                    "neg8-expired-end",
                    records=_clean_idle_records(),
                    gross_energy_j=8.01,
                    neg8_position="end",
                ),
            ],
            binding,
            whole_window=True,
            neg8_drift_bound=expired,
        )
        freshness = section["neg8_bracket"]["bound_freshness"]
        self.assertEqual(freshness["decision"], "stale")
        self.assertIn(
            "validity_horizon_expired",
            freshness["triggered_rederivation_reasons"],
        )
        self.assertIn("neg8_drift_bound_stale", section["conditions"])
        self.assertEqual(section["neg8_bracket"]["decision"], "failed")

    def test_neg8_bound_binding_changes_trigger_stale_refusal(self) -> None:
        binding = self._binding()
        cases = (
            (
                "os_build_change",
                {"os_build": "25F85"},
            ),
            (
                "power_supply_change",
                {
                    "adapter_watts": 96,
                    "adapter_description": "96W USB-C Power Adapter",
                },
            ),
            (
                "calibration_identity_change",
                {"calibration_identity_sha256": "d" * 64},
            ),
        )
        for trigger, overrides in cases:
            with self.subTest(trigger=trigger):
                members = [
                    self._member(
                        f"neg8-{trigger}-{position}",
                        records=_clean_idle_records(),
                        gross_energy_j=8.0 + index * 0.01,
                        neg8_position=position,
                        **overrides,
                    )
                    for index, position in enumerate(("start", "end"))
                ]
                section = run_campaign_module.idle_admission_core_verdict(
                    members,
                    binding,
                    whole_window=True,
                    neg8_drift_bound=self._drift_bound(),
                )
                freshness = section["neg8_bracket"]["bound_freshness"]
                self.assertIn(
                    trigger,
                    freshness["triggered_rederivation_reasons"],
                )
                self.assertIn(
                    "neg8_drift_bound_stale", section["conditions"]
                )
                self.assertEqual(section["neg8_bracket"]["decision"], "failed")

    def test_unissued_prefreshness_bound_wire_is_malformed_and_underived(self) -> None:
        binding = self._binding()
        artifact = self._drift_bound()
        artifact.pop("freshness")
        artifact["derivation_sha256"] = canonical_sha256(
            {
                key: value
                for key, value in artifact.items()
                if key != "derivation_sha256"
            }
        )
        self.assertFalse(
            run_campaign_module.validate_neg8_drift_bound_artifact(artifact)
        )
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "neg8-prefreshness-start",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    neg8_position="start",
                ),
                self._member(
                    "neg8-prefreshness-end",
                    records=_clean_idle_records(),
                    gross_energy_j=8.01,
                    neg8_position="end",
                ),
            ],
            binding,
            whole_window=True,
            neg8_drift_bound=artifact,
        )
        self.assertEqual(
            section["neg8_bracket"]["bound_freshness"]["decision"],
            "underived",
        )
        self.assertIn("neg8_drift_bound_underived", section["conditions"])
        self.assertIn(
            "neg8_idle_sub_drift_bound_underived", section["conditions"]
        )

    def test_family_point_drift_gates_while_gross_corners_are_diagnostic(self) -> None:
        binding = self._binding()
        drift_bound = self._drift_bound()
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "p2-neg8-reference-start__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    gross_half_width_j=0.75,
                    idle_subtracted_energy_j=7.8,
                    neg8_position="start",
                ),
                self._member(
                    "p2-neg8-reference-end__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.04,
                    gross_half_width_j=0.75,
                    idle_subtracted_energy_j=7.87,
                    neg8_position="end",
                ),
            ],
            binding,
            whole_window=True,
            neg8_drift_bound=drift_bound,
        )
        bracket = section["neg8_bracket"]
        self.assertEqual(bracket["decision"], "passed")
        self.assertGreater(
            bracket["corner_abs_delta_j"], drift_bound["bound_j"]
        )
        self.assertEqual(
            bracket["corner_statistic_role"], "diagnostic_not_gating"
        )
        self.assertAlmostEqual(
            bracket["idle_subtracted_companion"]["abs_delta_j"], 0.07
        )
        self.assertEqual(
            bracket["idle_subtracted_companion"]["role"],
            "claim_family_screen_and_budget",
        )
        self.assertEqual(
            bracket["drift_bound_artifact"]["reference_corpus"]["member_ids"],
            [f"neg8-refcorpus-r{index:02d}" for index in range(1, 13)],
        )
        self.assertEqual(
            bracket["drift_bound_artifact"]["estimator"]["id"],
            "d054_point_contrast_guard_v1",
        )
        self.assertEqual(
            bracket["drift_bound_artifact"]["derivation_sha256"],
            drift_bound["derivation_sha256"],
        )

    def test_idle_subtracted_family_can_fail_while_gross_family_passes(self) -> None:
        binding = self._binding()
        drift_bound = self._drift_bound()
        gross_bound = drift_bound["claim_family_bounds"]["gross_energy"][
            "estimator"
        ]["single_member_endpoint_bound_j"]
        idle_bound = drift_bound["claim_family_bounds"][
            "idle_subtracted_energy"
        ]["estimator"]["single_member_endpoint_bound_j"]
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "neg8-gross-pass-idle-fail-start",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    idle_subtracted_energy_j=7.0,
                    neg8_position="start",
                ),
                self._member(
                    "neg8-gross-pass-idle-fail-end",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0 + gross_bound / 2.0,
                    idle_subtracted_energy_j=7.0 + idle_bound * 2.0,
                    neg8_position="end",
                ),
            ],
            binding,
            whole_window=True,
            neg8_drift_bound=drift_bound,
        )
        bracket = section["neg8_bracket"]
        self.assertTrue(
            bracket["claim_families"]["gross_energy"]["screen_passed"]
        )
        self.assertFalse(
            bracket["claim_families"]["idle_subtracted_energy"][
                "screen_passed"
            ]
        )
        self.assertIn(
            "neg8_bracket_idle_sub_abs_delta_exceeded",
            bracket["conditions"],
        )
        self.assertEqual(bracket["decision"], "failed")

    def test_replicated_endpoints_record_sem_and_midpoint_dominates_budget(
        self,
    ) -> None:
        binding = self._binding()
        drift_bound = self._drift_bound()
        evaluations = []
        for index, gross in enumerate((8.00, 8.02, 7.98), start=1):
            evaluations.append(
                self._member(
                    f"neg8-start-r{index}",
                    records=_clean_idle_records(),
                    gross_energy_j=gross,
                    idle_subtracted_energy_j=gross - 0.2,
                    neg8_position="start",
                )
            )
        evaluations.append(
            self._member(
                "neg8-midpoint",
                records=_clean_idle_records(),
                gross_energy_j=8.5,
                idle_subtracted_energy_j=8.3,
                neg8_position="midpoint",
            )
        )
        for index, gross in enumerate((8.01, 8.03, 7.99), start=1):
            evaluations.append(
                self._member(
                    f"neg8-end-r{index}",
                    records=_clean_idle_records(),
                    gross_energy_j=gross,
                    idle_subtracted_energy_j=gross - 0.2,
                    neg8_position="end",
                )
            )
        bracket = run_campaign_module.idle_admission_core_verdict(
            evaluations,
            binding,
            whole_window=True,
            neg8_drift_bound=drift_bound,
        )["neg8_bracket"]
        self.assertEqual(
            bracket["endpoint_protocol"],
            "replicated_endpoints_with_midpoint",
        )
        gross = bracket["claim_families"]["gross_energy"]
        self.assertEqual(gross["start"]["n"], 3)
        self.assertGreater(gross["start"]["standard_error_j"], 0.0)
        self.assertAlmostEqual(gross["point_delta_j"], 0.01)
        self.assertAlmostEqual(gross["trajectory_excursion_max_j"], 0.5)
        self.assertAlmostEqual(gross["drift_allowance_j"], 0.5)
        self.assertGreater(gross["drift_allowance_j"], 0.0)
        self.assertEqual(
            gross["duration_scaling"], "not_applied_no_governed_time_law"
        )
        self.assertEqual(bracket["decision"], "passed")

    def test_legacy_pair_uses_single_member_bound_and_nonzero_allowance(self) -> None:
        binding = self._binding()
        drift_bound = self._drift_bound()
        bracket = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "legacy-start",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    neg8_position="start",
                ),
                self._member(
                    "legacy-end",
                    records=_clean_idle_records(),
                    gross_energy_j=8.01,
                    neg8_position="end",
                ),
            ],
            binding,
            whole_window=True,
            neg8_drift_bound=drift_bound,
        )["neg8_bracket"]
        gross = bracket["claim_families"]["gross_energy"]
        self.assertEqual(
            bracket["endpoint_protocol"], "legacy_single_member_endpoints"
        )
        self.assertEqual(
            gross["derived_repeatability_bound_j"],
            drift_bound["claim_family_bounds"]["gross_energy"]["estimator"][
                "single_member_endpoint_bound_j"
            ],
        )
        self.assertGreater(gross["drift_allowance_j"], 0.0)

    def test_whole_window_refuses_distinct_underived_bound_condition(self) -> None:
        binding = self._binding()
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "p2-neg8-reference-start__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    neg8_position="start",
                ),
                self._member(
                    "p2-neg8-reference-end__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    neg8_position="end",
                ),
            ],
            binding,
            whole_window=True,
        )
        self.assertEqual(section["neg8_bracket"]["decision"], "failed")
        self.assertIn("neg8_drift_bound_underived", section["conditions"])
        self.assertIn(
            "neg8_idle_sub_drift_bound_underived", section["conditions"]
        )

    def test_neg8_substring_without_declared_role_confers_no_reference(self) -> None:
        # R5 defect shape: these IDs formerly conferred both reference roles.
        # With no suite-declared role provenance they are ordinary members.
        binding = self._binding()
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "p2-neg8-reference-start__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                ),
                self._member(
                    "p2-neg8-reference-end__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.01,
                ),
            ],
            binding,
            whole_window=True,
        )
        self.assertEqual(section["neg8_bracket"]["decision"], "failed")
        self.assertIn("neg8_bracket_missing", section["conditions"])
        self.assertIsNone(section["neg8_reference_scientific_config_sha256"])

    def test_declared_neg8_role_with_noncanonical_workload_is_config_error(self) -> None:
        source = json.loads(
            (
                ROOT
                / "configs"
                / "campaigns"
                / "p2_015_floors"
                / "00_neg8_start"
                / "p2015-neg8-reference-start.json"
            ).read_text(encoding="utf-8")
        )
        source["workload_profile"]["prompt_tokens"] = 999
        path = self.root / "declared-invalid-neg8.json"
        path.write_text(json.dumps(source) + "\n", encoding="utf-8")
        entry = run_campaign_module.OrderEntry(
            index=1,
            config=path.name,
            role=run_campaign_module.NEG8_REFERENCE_ROLE,
            sentinel_position="start",
        )
        with self.assertRaisesRegex(ValueError, "canonical NEG-8 workload"):
            run_campaign_module.load_config_info(path, order_entry=entry)

    def test_neg8_reference_scientific_config_mismatch_fails_closed(self) -> None:
        # T2 defect shape: ID substrings plus similar energy formerly licensed
        # a bracket even when the end reference used a different collection
        # configuration.  Canonical workload identity alone is not enough;
        # the complete normalized scientific hashes must also match.
        binding = self._binding()
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "p2-neg8-reference-start__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    neg8_position="start",
                ),
                self._member(
                    "p2-neg8-reference-end__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.01,
                    scientific_sampling_hz=5.0,
                    neg8_position="end",
                ),
            ],
            binding,
            whole_window=True,
        )
        self.assertEqual(section["neg8_bracket"]["decision"], "failed")
        self.assertIn("neg8_bracket_reference_invalid", section["conditions"])
        self.assertIsNone(section["neg8_reference_scientific_config_sha256"])

    def test_missing_idle_telemetry_fails_closed_under_production(self) -> None:
        binding = self._binding()
        evaluations = [self._member("p2-work-a__r1", records=None)]
        section = run_campaign_module.idle_admission_core_verdict(
            evaluations, binding
        )
        member = section["members"][0]["cpu_admission"]
        self.assertEqual(member["decision"], "failed")
        self.assertIn("cpu_baseline_telemetry_missing", section["conditions"])

    def test_cpu_active_member_fails_and_is_named(self) -> None:
        binding = self._binding()
        active = [
            {
                "processor_combined_power_w": 0.2,
                "clusters": [{"cpus": [{"idle_ratio": 0.05, "down_ratio": 0.0}]}],
            }
            for _ in range(5)
        ]
        section = run_campaign_module.idle_admission_core_verdict(
            [self._member("p2-work-a__r1", records=active)], binding
        )
        self.assertIn("cpu_busy_ratio_p95_exceeded", section["conditions"])
        self.assertEqual(
            section["members"][0]["cpu_admission"]["decision"], "failed"
        )

    def test_wattage_discontinuity_and_description_change_are_named(self) -> None:
        binding = self._binding()
        evaluations = [
            self._member("m1__r1", records=_clean_idle_records(), adapter_watts=140),
            self._member("m2__r1", records=_clean_idle_records(), adapter_watts=70),
            self._member("m3__r1", records=_clean_idle_records(), adapter_watts=140),
            self._member(
                "m4__r1",
                records=_clean_idle_records(),
                adapter_watts=140,
                adapter_description="96W USB-C Power Adapter",
            ),
        ]
        section = run_campaign_module.idle_admission_core_verdict(
            evaluations, binding
        )
        continuity = section["adapter_wattage_continuity"]
        self.assertEqual(continuity["decision"], "flagged")
        self.assertIn("adapter_wattage_discontinuity", section["conditions"])
        self.assertIn("adapter_description_changed", section["conditions"])
        self.assertEqual(
            [
                (row["from_watts"], row["to_watts"])
                for row in continuity["wattage_transitions"]
            ],
            [(140.0, 70.0), (70.0, 140.0)],
        )

    def test_final_member_post_workload_adapter_renegotiation_is_observed(self) -> None:
        # F6 audit reproduction: the final workload renegotiates 140 W -> 70 W
        # after its pre-run sample.  With no post sample the old campaign
        # verdict incorrectly called the entire campaign stable.
        binding = self._binding()
        first = self._member("m1__r1", records=_clean_idle_records())
        final = self._member("m2__r1", records=_clean_idle_records())
        final.metadata["environment"]["post_run_observation"]["power"][
            "adapter_watts"
        ] = 70
        section = run_campaign_module.idle_admission_core_verdict(
            [first, final], binding
        )
        continuity = section["adapter_wattage_continuity"]
        self.assertNotEqual(continuity["decision"], "stable")
        self.assertIn("adapter_wattage_discontinuity", section["conditions"])
        self.assertIn(
            (140.0, 70.0),
            [
                (row["from_watts"], row["to_watts"])
                for row in continuity["wattage_transitions"]
            ],
        )

    def test_unknown_adapter_wattage_fails_closed_under_production(self) -> None:
        binding = self._binding()
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "m1__r1",
                    records=_clean_idle_records(),
                    adapter_watts=None,
                    adapter_description=None,
                )
            ],
            binding,
        )
        self.assertEqual(
            section["adapter_wattage_continuity"]["decision"], "failed"
        )
        self.assertIn("adapter_wattage_unknown", section["conditions"])

    def test_neg8_bracket_edge_cases_in_verdict(self) -> None:
        binding = self._binding()
        drift_bound = self._drift_bound()

        def section_for(end_gross: float | None) -> dict:
            evaluations = [
                self._member(
                    "p2-neg8-reference-start__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    neg8_position="start",
                )
            ]
            if end_gross is not None:
                evaluations.append(
                    self._member(
                        "p2-neg8-reference-end__r1",
                        records=_clean_idle_records(),
                        gross_energy_j=end_gross,
                        neg8_position="end",
                    )
                )
            return run_campaign_module.idle_admission_core_verdict(
                evaluations, binding, neg8_drift_bound=drift_bound
            )

        within_bound = section_for(8.0 + drift_bound["bound_j"] / 2.0)
        self.assertEqual(within_bound["neg8_bracket"]["decision"], "passed")
        above_bound = section_for(8.0 + drift_bound["bound_j"] * 2.0)
        self.assertEqual(above_bound["neg8_bracket"]["decision"], "failed")
        # Start-only invocation is a per-segment run, not a whole-window pass:
        # the bracket is not evaluated here (non-drift), never a spurious
        # ``failed``/``missing``.
        missing = section_for(None)
        self.assertEqual(missing["neg8_bracket"]["decision"], "not_evaluated")
        self.assertIn("neg8_bracket_not_evaluated", missing["conditions"])
        self.assertNotIn("neg8_bracket_missing", missing["conditions"])

    def test_corrupt_utf8_idle_telemetry_fails_closed_not_crash(self) -> None:
        """Fix round 1: invalid UTF-8 bytes must fail closed, not crash.

        ``_load_idle_rich_telemetry`` promised that unreadable bytes return
        ``None``, but a stray non-UTF-8 byte raised ``UnicodeDecodeError``
        (a ``ValueError``, not ``OSError``) which propagated out of
        ``idle_admission_core_verdict`` and crashed the whole campaign at
        verdict time -- before ``append_verdict`` -- losing the result.
        """

        binding = self._binding()
        bundle_path = self.root / "p2-work-a__r1"
        bundle_path.mkdir(parents=True, exist_ok=True)
        (bundle_path / "rich_telemetry_idle.jsonl").write_bytes(
            b'{"processor_combined_power_w": 0.1}\n\xff\xfe bad bytes\n'
        )
        evaluation = run_campaign_module.MemberEvaluation(
            bundle_id="p2-work-a__r1",
            bundle_path=bundle_path,
            config_name="p2-work-a__r1.json",
            status="succeeded",
            strict_valid=True,
            summary={},
            metadata={"environment_admission": {"decision": "admitted"}},
        )
        # Must not raise.
        section = run_campaign_module.idle_admission_core_verdict(
            [evaluation], binding
        )
        member = section["members"][0]["cpu_admission"]
        self.assertEqual(member["decision"], "failed")
        self.assertIn("cpu_baseline_telemetry_missing", section["conditions"])

    def _produced_retry_member(
        self,
        bundle_id: str,
        *,
        attempt1_records: list[dict] | None,
        attempt2_records: list[dict] | None,
        expected_strict_valid: bool = True,
    ):
        from tests.test_controller import produce_retry_powermetrics_bundle

        bundle_path, _summary = produce_retry_powermetrics_bundle(
            self.root / "runs",
            bundle_id,
        )
        attempt1_path = bundle_path / "rich_telemetry_idle.jsonl"
        attempt2_path = bundle_path / "rich_telemetry_idle_attempt_2.jsonl"
        for path, replacements in (
            (attempt1_path, attempt1_records),
            (attempt2_path, attempt2_records),
        ):
            if replacements is None:
                path.unlink(missing_ok=True)
                continue
            template = replacements[0]
            produced = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line
            ]
            for record in produced:
                record["processor_combined_power_w"] = template[
                    "processor_combined_power_w"
                ]
                record["clusters"] = json.loads(json.dumps(template["clusters"]))
            path.write_text(
                "".join(json.dumps(record) + "\n" for record in produced),
                encoding="utf-8",
            )
        config_path = self.root / f"{bundle_id}.json"
        shutil.copy2(bundle_path / "config.json", config_path)
        evaluation = run_campaign_module.evaluate_member(
            bundle_path,
            info=run_campaign_module.load_config_info(config_path),
            waivers={},
        )
        self.assertIs(evaluation.strict_valid, expected_strict_valid)
        return evaluation

    def test_cpu_admission_reads_final_attempt_telemetry(self) -> None:
        """Fix round 1 (blocker): pair CPU telemetry with the final attempt.

        The controller records the FINAL retry attempt's admission decision,
        so CPU-idle evaluation must read the telemetry from that same attempt.
        Here attempt 1 is CPU-clean but attempt 2 is CPU-busy and the final
        (attempt-2) GPU decision is ``admitted``: reading attempt-1 telemetry
        would fail OPEN and report ``admitted`` on exactly the retried (most
        suspect) admission.  The fix must read attempt-2 telemetry and fail.
        """

        binding = self._binding()
        evaluation = self._produced_retry_member(
            "p2-work-a__r1",
            attempt1_records=_clean_idle_records(),
            attempt2_records=_busy_idle_records(),
        )
        section = run_campaign_module.idle_admission_core_verdict(
            [evaluation], binding
        )
        member = section["members"][0]["cpu_admission"]
        self.assertEqual(member["decision"], "failed")
        self.assertIn("cpu_busy_ratio_p95_exceeded", section["conditions"])

    def test_environment_refusal_does_not_hide_valid_retry_telemetry(self) -> None:
        binding = self._binding()
        evaluation = self._produced_retry_member(
            "environment-refused",
            attempt1_records=_clean_idle_records(),
            attempt2_records=_clean_idle_records(),
        )
        with patch.object(
            run_campaign_module,
            "_current_member_environment_refusals",
            return_value=("environment_admission_failed",),
        ):
            section = run_campaign_module.idle_admission_core_verdict(
                [evaluation], binding
            )
        self.assertIn("environment_admission_failed", section["conditions"])
        self.assertNotIn(
            "idle_admission_attempt_ledger_invalid", section["conditions"]
        )
        self.assertNotIn(
            "cpu_baseline_telemetry_missing", section["conditions"]
        )
        self.assertEqual(
            section["members"][0]["cpu_admission"]["decision"], "admitted"
        )

    def test_missing_final_attempt_telemetry_fails_closed(self) -> None:
        """Fix round 1 (blocker): absent retried telemetry fails closed.

        When the recorded final attempt is >1 but its rich-telemetry file is
        absent, CPU-idle evaluation must fail closed rather than silently fall
        back to attempt-1 telemetry.
        """

        binding = self._binding()
        evaluation = self._produced_retry_member(
            "p2-work-a__r1",
            attempt1_records=_clean_idle_records(),
            attempt2_records=None,
            # At 8018a4b strict verification fired its fresh-reduction
            # mismatch (the stored precheck lacked
            # ``environment_admission_missing``).  The stored-method
            # environment-anchor dispatch hunk makes the writer/replay
            # prechecks agree; final-attempt pairing remains a whole-window
            # admission concern, not a generic bundle-layout requirement.
            expected_strict_valid=True,
        )
        self.assertEqual(evaluation.validation_problems, ())
        self.assertFalse(
            (evaluation.bundle_path / "rich_telemetry_idle_attempt_2.jsonl").exists()
        )
        section = run_campaign_module.idle_admission_core_verdict(
            [evaluation], binding
        )
        member = section["members"][0]["cpu_admission"]
        self.assertEqual(member["decision"], "failed")
        self.assertIn("cpu_baseline_telemetry_missing", section["conditions"])

    def test_retry_attempt_ledger_must_be_ordered_unique_and_decision_bound(self) -> None:
        # W12 exact defect: max(attempts) silently selected rows from duplicate,
        # reordered, skipped, or decision-inconsistent ledgers.
        binding = self._binding()
        cases = (
            ([1, 1], [False, True], "admitted"),
            ([2, 1], [False, True], "admitted"),
            ([1, 3], [False, True], "admitted"),
            ([1, 2], [False, False], "admitted"),
        )
        base_evaluation = self._produced_retry_member(
            "malformed-ledger",
            attempt1_records=_clean_idle_records(),
            attempt2_records=_clean_idle_records(),
        )
        for index, (numbers, admitted, decision) in enumerate(cases):
            with self.subTest(case=index):
                evaluation = replace(
                    base_evaluation,
                    metadata=json.loads(json.dumps(base_evaluation.metadata)),
                )
                evaluation.metadata["environment_admission"][
                    "decision"
                ] = decision
                evaluation.metadata["environment_admission"]["attempts"] = [
                    {"attempt": number, "admitted": outcome}
                    for number, outcome in zip(numbers, admitted)
                ]
                section = run_campaign_module.idle_admission_core_verdict(
                    [evaluation], binding
                )
                self.assertIn(
                    "idle_admission_attempt_ledger_invalid", section["conditions"]
                )

    def test_duplicate_neg8_markers_are_ambiguous_not_order_selected(self) -> None:
        binding = self._binding()
        section = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "a-neg8-reference-start__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    neg8_position="start",
                ),
                self._member(
                    "z-neg8-reference-start__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=99.0,
                    neg8_position="start",
                ),
                self._member(
                    "neg8-reference-end__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.1,
                    neg8_position="end",
                ),
            ],
            binding,
            whole_window=True,
        )
        self.assertIn("neg8_bracket_ambiguous_reference", section["conditions"])
        self.assertNotEqual(section["neg8_bracket"]["decision"], "passed")

    def test_idle_core_failure_removes_claim_readiness(self) -> None:
        # W6 defect shape: readiness was finalized before the core, so an
        # adapter discontinuity/absent whole-window bracket left a ready claim.
        readiness = {
            "verdict": "ready_for_analysis",
            "reasons": [],
            "required_contrast_ids": ["c1"],
            "ready_contrast_ids": ["c1"],
            "not_ready_contrasts": [],
            "note": "test",
        }
        core = {
            "members": [
                {"cpu_admission": {"decision": "admitted"}}
            ],
            "adapter_wattage_continuity": {"decision": "failed"},
            "neg8_bracket": {"decision": "not_evaluated"},
        }
        blocked = run_campaign_module.apply_idle_admission_claim_barrier(
            readiness, core, claim_bearing=True
        )
        self.assertEqual(blocked["verdict"], "not_ready_for_analysis")
        self.assertEqual(blocked["ready_contrast_ids"], [])
        self.assertIn("adapter_continuity_failed", blocked["reasons"])
        self.assertIn("whole_window_neg8_verdict_missing", blocked["reasons"])

    def test_invalid_reference_summary_cannot_supply_gross_energy(self) -> None:
        member = self._member(
            "neg8-reference-start__r1",
            records=_clean_idle_records(),
            gross_energy_j=8.0,
        )
        invalid = replace(member, strict_valid=False)
        self.assertIsNone(run_campaign_module._gross_energy_for(invalid))

    def _install_whole_window_manifest(self, binding, bundle_roles) -> None:
        manifest_dir = self.root / "campaign_manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        (manifest_dir / "window.json").write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.campaign_provenance.v1",
                    "analysis_manifest_id": "window-a",
                    "campaign_policy": {"sha256": binding.sha256},
                    "members": [
                        {
                            "config": f"{bundle_id}.json",
                            "run_id": bundle_id,
                            "execution": "invoked",
                            "bundle_ids": [bundle_id],
                            "role": run_campaign_module.NEG8_REFERENCE_ROLE,
                            "sentinel_position": position,
                            "scientific_config_sha256": evaluation.scientific_config_sha256,
                            "canonical_neg8_workload": True,
                        }
                        for bundle_id, position, evaluation in bundle_roles
                    ],
                }
            )
            + "\n"
        )

    def _install_passing_whole_window_verdict_fixture(
        self,
        *,
        bound_lineage: dict,
    ):
        binding = self._binding()
        drift_bound_path = self._write_drift_bound(
            launch_lineage=bound_lineage
        )
        manifest_members = []
        for bundle_id, gross_energy_j, position in (
            ("p2-neg8-reference-start__r1", 8.0, "start"),
            ("p2-neg8-reference-end__r1", 8.04, "end"),
        ):
            member = self._member(
                bundle_id,
                records=_clean_idle_records(),
                gross_energy_j=gross_energy_j,
                neg8_position=position,
            )
            manifest_members.append((bundle_id, position, member))
            (member.bundle_path / "summary_metrics.json").write_text(
                json.dumps({"status": "succeeded", **member.summary}) + "\n"
            )
            (member.bundle_path / "metadata.json").write_text(
                json.dumps(member.metadata) + "\n"
            )
        self._install_whole_window_manifest(binding, manifest_members)
        return binding, run_campaign_module.parse_args(
            [
                "--whole-window-verdict",
                "--runs-dir",
                str(self.root),
                "--campaign-policy",
                str(binding.path),
                "--neg8-drift-bound",
                str(drift_bound_path),
            ]
        )

    def _install_retry_occurrence_manifests(
        self, binding, bundle_roles
    ) -> str:
        manifest_dir = self.root / "campaign_manifests"
        manifest_dir.mkdir(parents=True, exist_ok=True)
        work_id, _position, work = bundle_roles[1]

        def member_row(bundle_id, position, evaluation):
            return {
                "config": evaluation.config_name,
                "run_id": bundle_id,
                "execution": "invoked",
                "bundle_ids": [bundle_id],
                "role": (
                    run_campaign_module.NEG8_REFERENCE_ROLE
                    if position is not None
                    else None
                ),
                "sentinel_position": position,
                "scientific_config_sha256": evaluation.scientific_config_sha256,
                "canonical_neg8_workload": position is not None,
            }

        common = {
            "schema_version": "joulewise.campaign_provenance.v1",
            "analysis_manifest_id": "window-a",
            "campaign_policy": {"sha256": binding.sha256},
        }
        (manifest_dir / "first-failed.json").write_text(
            json.dumps(
                {
                    **common,
                    "members": [member_row(work_id, None, work)],
                }
            )
            + "\n"
        )
        (manifest_dir / "retry-present.json").write_text(
            json.dumps(
                {
                    **common,
                    "members": [
                        member_row(bundle_id, position, evaluation)
                        for bundle_id, position, evaluation in bundle_roles
                    ],
                }
            )
            + "\n"
        )
        return work_id

    def _install_v2_occurrence_sequence(
        self,
        binding,
        bundle_id: str,
        sequence: list[str],
        *,
        manifest_prefix: str = "",
    ) -> Path:
        manifest_dir = self.root / "campaign_manifests"
        log_path = self.root / "campaign_log.jsonl"
        with held_campaign_lock(self.root):
            for index, execution in enumerate(sequence):
                manifest = {
                    "schema_version": "joulewise.campaign_provenance.v2",
                    "session_id": f"{manifest_prefix}projection-{index}",
                    "analysis_manifest_id": "window-a",
                    "campaign_policy": {"sha256": binding.sha256},
                    "members": [
                        {
                            "config": f"{bundle_id}.json",
                            "run_id": bundle_id,
                            "execution": execution,
                            "bundle_ids": [bundle_id],
                            **(
                                {"outcome": "failed"}
                                if execution == "existing"
                                else {}
                            ),
                        }
                    ],
                }
                run_campaign_module.write_campaign_provenance(
                    manifest_dir
                    / f"{manifest_prefix}{index:02d}-{execution}.json",
                    manifest,
                    log_path,
                )
        canonical = self.root / bundle_id
        canonical.mkdir(exist_ok=True)
        quarantine = Path(tempfile.mkdtemp(prefix="jw-projection-quarantine-"))
        self.addCleanup(shutil.rmtree, quarantine, True)
        for name, payload in (
            ("config.json", {"run_id": bundle_id}),
            ("metadata.json", {"status": "failed"}),
            ("summary_metrics.json", {"status": "failed"}),
        ):
            raw = json.dumps(payload, sort_keys=True) + "\n"
            (canonical / name).write_text(raw, encoding="utf-8")
            (quarantine / name).write_text(raw, encoding="utf-8")
        return quarantine

    def _supersession_argv(
        self, binding, bundle_id: str, quarantine: Path
    ) -> list[str]:
        return [
            "--record-supersession",
            bundle_id,
            "--quarantine-path",
            str(quarantine),
            "--reason",
            "failed occurrence quarantined before retry",
            "--runs-dir",
            str(self.root),
            "--campaign-policy",
            str(binding.path),
        ]

    def test_supersession_recorder_refuses_repeat_without_mutating_log(
        self,
    ) -> None:
        binding = self._binding()
        bundle_id = "repeat-refusal-bundle"
        quarantine = self._install_v2_occurrence_sequence(
            binding, bundle_id, ["existing", "existing", "invoked"]
        )
        argv = self._supersession_argv(binding, bundle_id, quarantine)
        args = run_campaign_module.parse_args(argv)
        first_stdout = io.StringIO()
        with redirect_stdout(first_stdout):
            self.assertEqual(run_campaign_module.run_record_supersession(args), 0)
        first_row = json.loads(first_stdout.getvalue())
        log_path = self.root / "campaign_log.jsonl"
        before_repeat = log_path.read_bytes()

        api_stdout = io.StringIO()
        with (
            redirect_stdout(api_stdout),
            self.assertRaises(
                run_campaign_module.SupersessionRecorderError
            ) as caught,
        ):
            run_campaign_module.run_record_supersession(args)
        self.assertEqual(api_stdout.getvalue(), "")
        self.assertEqual(
            caught.exception.reason_code,
            "campaign_occurrence_supersession_already_recorded",
        )
        expected_message = (
            "supersession recording refused: first recognizable existing row "
            f"bundle_id={json.dumps(bundle_id)}; "
            "recognizable same-bundle row count=1; "
            f"target log path={json.dumps(str(log_path))}; "
            f"recorded timestamp={json.dumps(first_row['timestamp'])}; "
            f"recorded entry_sha256={json.dumps(first_row['entry_sha256'])}; "
            "no row was appended"
        )
        self.assertEqual(str(caught.exception), expected_message)
        self.assertEqual(log_path.read_bytes(), before_repeat)

        cli_stdout = io.StringIO()
        cli_stderr = io.StringIO()
        with redirect_stdout(cli_stdout), redirect_stderr(cli_stderr):
            self.assertEqual(run_campaign_module.main(argv), 2)
        self.assertEqual(cli_stdout.getvalue(), "")
        self.assertEqual(
            cli_stderr.getvalue(),
            "error: campaign_occurrence_supersession_already_recorded: "
            f"{expected_message}\n",
        )
        self.assertEqual(log_path.read_bytes(), before_repeat)
        supersessions = [
            row
            for row in read_wire_jsonl(log_path)
            if row.get("record_type") == "campaign_occurrence_supersession"
            or row.get("schema_version")
            == run_campaign_module.OCCURRENCE_SUPERSESSION_SCHEMA
        ]
        self.assertEqual(supersessions, [first_row])

    def test_supersession_recorder_refuses_widened_third_occurrence(
        self,
    ) -> None:
        binding = self._binding()
        bundle_id = "third-occurrence-refusal-bundle"
        quarantine = self._install_v2_occurrence_sequence(
            binding, bundle_id, ["existing", "existing", "invoked"]
        )
        first_args = run_campaign_module.parse_args(
            self._supersession_argv(binding, bundle_id, quarantine)
        )
        first_stdout = io.StringIO()
        with redirect_stdout(first_stdout):
            self.assertEqual(
                run_campaign_module.run_record_supersession(first_args), 0
            )
        first_row = json.loads(first_stdout.getvalue())

        third_quarantine = self._install_v2_occurrence_sequence(
            binding,
            bundle_id,
            ["invoked"],
            manifest_prefix="third-",
        )
        self.assertTrue(
            run_campaign_module.validate_occurrence_supersession_entry(
                first_row, self.root
            )
        )

        catalog = run_campaign_module.load_authenticated_campaign_catalog(
            self.root, self.root / "campaign_log.jsonl"
        )
        self.assertIsNotNone(catalog)
        assert catalog is not None
        events = []
        for record in catalog:
            source = {
                "path": f"campaign_manifests/{record.path.name}",
                "sha256": hashlib.sha256(record.raw_bytes).hexdigest(),
            }
            for member_index, member in enumerate(record.value["members"]):
                for bundle_index, declared_id in enumerate(member["bundle_ids"]):
                    if declared_id == bundle_id:
                        events.append(
                            (
                                member["execution"],
                                {
                                    "bundle_id": declared_id,
                                    "source_manifest": dict(source),
                                    "member_index": member_index,
                                    "bundle_index": bundle_index,
                                },
                            )
                        )
        would_record = run_campaign_module.normalized_campaign_representatives(
            {bundle_id: events}
        )[bundle_id]
        self.assertNotEqual(would_record[-1], first_row["selected_occurrence"])
        self.assertEqual(
            would_record[:-1],
            [
                *first_row["superseded_occurrences"],
                first_row["selected_occurrence"],
            ],
        )

        log_path = self.root / "campaign_log.jsonl"
        before_repeat = log_path.read_bytes()
        second_args = run_campaign_module.parse_args(
            self._supersession_argv(binding, bundle_id, third_quarantine)
        )
        with self.assertRaises(
            run_campaign_module.SupersessionRecorderError
        ) as caught:
            run_campaign_module.run_record_supersession(second_args)
        self.assertEqual(
            caught.exception.reason_code,
            "campaign_occurrence_supersession_already_recorded",
        )
        self.assertEqual(log_path.read_bytes(), before_repeat)

    def test_supersession_recorder_refuses_invalid_existing_row(self) -> None:
        binding = self._binding()
        bundle_id = "invalid-existing-bundle"
        quarantine = self._install_v2_occurrence_sequence(
            binding, bundle_id, ["existing", "existing", "invoked"]
        )
        args = run_campaign_module.parse_args(
            self._supersession_argv(binding, bundle_id, quarantine)
        )
        with redirect_stdout(io.StringIO()):
            self.assertEqual(run_campaign_module.run_record_supersession(args), 0)
        log_path = self.root / "campaign_log.jsonl"
        lines = log_path.read_bytes().splitlines(keepends=True)
        corrupted_row = None
        for index, raw_line in enumerate(lines):
            row = json.loads(raw_line)
            if row.get("record_type") == "campaign_occurrence_supersession":
                row["entry_sha256"] = "0" * 64
                corrupted_row = row
                lines[index] = (
                    json.dumps(row, sort_keys=True) + "\n"
                ).encode("utf-8")
                break
        self.assertIsNotNone(corrupted_row)
        assert corrupted_row is not None
        log_path.write_bytes(b"".join(lines))
        self.assertFalse(
            run_campaign_module.validate_occurrence_supersession_entry(
                corrupted_row, self.root
            )
        )
        before_repeat = log_path.read_bytes()

        with self.assertRaises(
            run_campaign_module.SupersessionRecorderError
        ) as caught:
            run_campaign_module.run_record_supersession(args)
        self.assertEqual(
            caught.exception.reason_code,
            "campaign_occurrence_supersession_already_recorded",
        )
        self.assertEqual(log_path.read_bytes(), before_repeat)
        self.assertEqual(
            sum(
                row.get("record_type")
                == "campaign_occurrence_supersession"
                for row in read_wire_jsonl(log_path)
            ),
            1,
        )

    def test_supersession_recorder_allows_different_bundle_in_same_log(
        self,
    ) -> None:
        binding = self._binding()
        first_id = "first-bundle"
        second_id = "second-bundle"
        first_quarantine = self._install_v2_occurrence_sequence(
            binding, first_id, ["existing", "existing", "invoked"]
        )
        second_quarantine = self._install_v2_occurrence_sequence(
            binding,
            second_id,
            ["existing", "existing", "invoked"],
            manifest_prefix="second-",
        )
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                run_campaign_module.run_record_supersession(
                    run_campaign_module.parse_args(
                        self._supersession_argv(
                            binding, first_id, first_quarantine
                        )
                    )
                ),
                0,
            )
            self.assertEqual(
                run_campaign_module.run_record_supersession(
                    run_campaign_module.parse_args(
                        self._supersession_argv(
                            binding, second_id, second_quarantine
                        )
                    )
                ),
                0,
            )
        supersessions = [
            row
            for row in read_wire_jsonl(self.root / "campaign_log.jsonl")
            if row.get("record_type") == "campaign_occurrence_supersession"
        ]
        self.assertEqual(
            [row["bundle_id"] for row in supersessions],
            [first_id, second_id],
        )

    def test_supersession_recorder_refuses_unidentifiable_log(self) -> None:
        cases = ("missing", "empty", "non-string")
        for case in cases:
            with self.subTest(bundle_id_shape=case):
                case_root = Path(tempfile.mkdtemp(prefix=f"jw-unidentified-{case}-"))
                self.addCleanup(shutil.rmtree, case_root, True)
                original_root = self.root
                self.root = case_root
                try:
                    binding = self._binding()
                    bundle_id = "requested-bundle"
                    quarantine = self._install_v2_occurrence_sequence(
                        binding,
                        bundle_id,
                        ["existing", "existing", "invoked"],
                    )
                    unidentifiable = {
                        "schema_version": (
                            run_campaign_module.OCCURRENCE_SUPERSESSION_SCHEMA
                        ),
                        "timestamp": None,
                        "entry_sha256": None,
                    }
                    if case == "empty":
                        unidentifiable["bundle_id"] = ""
                    elif case == "non-string":
                        unidentifiable["bundle_id"] = 7
                    log_path = case_root / "campaign_log.jsonl"
                    with log_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(unidentifiable) + "\n")
                    before = log_path.read_bytes()
                    args = run_campaign_module.parse_args(
                        self._supersession_argv(binding, bundle_id, quarantine)
                    )
                    with self.assertRaises(
                        run_campaign_module.SupersessionRecorderError
                    ) as caught:
                        run_campaign_module.run_record_supersession(args)
                    self.assertEqual(
                        caught.exception.reason_code,
                        "campaign_occurrence_supersession_already_recorded",
                    )
                    message = str(caught.exception)
                    self.assertIn(
                        "recognizable same-bundle row count=1", message
                    )
                    self.assertIn(
                        'recorded timestamp="<missing-or-non-string>"',
                        message,
                    )
                    self.assertIn(
                        'recorded entry_sha256="<missing-or-non-string>"',
                        message,
                    )
                    if case == "empty":
                        self.assertIn('bundle_id=""', message)
                    else:
                        self.assertIn(
                            'bundle_id="<missing-or-non-string>"', message
                        )
                    self.assertIn("no row was appended", message)
                    self.assertEqual(log_path.read_bytes(), before)
                finally:
                    self.root = original_root

    def test_supersession_recorder_refuses_torn_recognizable_final_row(
        self,
    ) -> None:
        binding = self._binding()
        bundle_id = "torn-recognizable-refusal-bundle"
        quarantine = self._install_v2_occurrence_sequence(
            binding, bundle_id, ["existing", "existing", "invoked"]
        )
        args = run_campaign_module.parse_args(
            self._supersession_argv(binding, bundle_id, quarantine)
        )
        with redirect_stdout(io.StringIO()):
            self.assertEqual(run_campaign_module.run_record_supersession(args), 0)

        log_path = self.root / "campaign_log.jsonl"
        prefix, final_row, terminator = log_path.read_bytes().rsplit(b"\n", 2)
        self.assertEqual(terminator, b"")
        schema_prefix = (
            f'"schema_version": '
            f'{json.dumps(run_campaign_module.OCCURRENCE_SUPERSESSION_SCHEMA)}'
        ).encode("ascii")
        torn_end = final_row.index(schema_prefix) + len(schema_prefix)
        before_repeat = prefix + b"\n" + final_row[:torn_end]
        log_path.write_bytes(before_repeat)

        lenient_rows = run_campaign_module.load_campaign_log_rows(log_path)
        self.assertIsNotNone(lenient_rows)
        assert lenient_rows is not None
        self.assertGreater(len(lenient_rows), 0)
        self.assertFalse(
            any(
                row.get("record_type") == "campaign_occurrence_supersession"
                or row.get("schema_version")
                == run_campaign_module.OCCURRENCE_SUPERSESSION_SCHEMA
                for row in lenient_rows
            )
        )
        self.assertIsNone(
            run_campaign_module.supersession_entry_validation_results(
                self.root, log_path
            )
        )

        api_stdout = io.StringIO()
        with redirect_stdout(api_stdout), self.assertRaises(
            run_campaign_module.SupersessionRecorderError
        ) as caught:
            run_campaign_module.run_record_supersession(args)
        # The truthful name matters: nothing was already recorded for this
        # bundle, so the already-recorded code would misreport the condition.
        self.assertEqual(
            caught.exception.reason_code,
            "campaign_occurrence_supersession_log_unreadable",
        )
        message = str(caught.exception)
        self.assertIn(
            "no supersession row for this bundle was recorded", message
        )
        self.assertIn(
            "cannot be read by the supersession consumer", message
        )
        self.assertIn(
            "quarantine and truncate the unreadable tail", message
        )
        self.assertIn(f"target log path={json.dumps(str(log_path))}", message)
        self.assertIn("no row was appended", message)
        self.assertEqual(api_stdout.getvalue(), "")
        self.assertEqual(log_path.read_bytes(), before_repeat)

        cli_stdout = io.StringIO()
        cli_stderr = io.StringIO()
        with redirect_stdout(cli_stdout), redirect_stderr(cli_stderr):
            self.assertEqual(
                run_campaign_module.main(
                    self._supersession_argv(binding, bundle_id, quarantine)
                ),
                2,
            )
        self.assertEqual(cli_stdout.getvalue(), "")
        self.assertEqual(
            cli_stderr.getvalue(),
            "error: campaign_occurrence_supersession_log_unreadable: "
            f"{message}\n",
        )
        self.assertEqual(log_path.read_bytes(), before_repeat)

    def test_supersession_recorder_consumes_join_normalized_projection(self) -> None:
        binding = self._binding()
        cases = (
            (
                ["invoked", "existing", "existing"],
                False,
                None,
                [],
            ),
            (
                ["existing", "existing", "invoked"],
                True,
                "campaign_manifests/02-invoked.json",
                ["campaign_manifests/00-existing.json"],
            ),
            (
                ["invoked", "invoked", "existing"],
                True,
                "campaign_manifests/01-invoked.json",
                ["campaign_manifests/00-invoked.json"],
            ),
        )
        for index, (sequence, accepted, selected_path, superseded_paths) in enumerate(cases):
            with self.subTest(sequence=sequence):
                case_root = Path(tempfile.mkdtemp(prefix=f"jw-projection-{index}-"))
                self.addCleanup(shutil.rmtree, case_root, True)
                original_root = self.root
                self.root = case_root
                try:
                    quarantine = self._install_v2_occurrence_sequence(
                        binding, "projection-bundle", sequence
                    )
                    args = run_campaign_module.parse_args(
                        [
                            "--record-supersession",
                            "projection-bundle",
                            "--quarantine-path",
                            str(quarantine),
                            "--reason",
                            "failed occurrence quarantined before retry",
                            "--runs-dir",
                            str(case_root),
                            "--campaign-policy",
                            str(binding.path),
                        ]
                    )
                    if not accepted:
                        with self.assertRaisesRegex(
                            ValueError, "exactly one duplicated ordinary-run"
                        ):
                            run_campaign_module.run_record_supersession(args)
                        continue
                    with redirect_stdout(io.StringIO()), patch.object(
                        run_campaign_module,
                        "acquire_campaign_lock",
                        wraps=run_campaign_module.acquire_campaign_lock,
                    ) as acquire_mock:
                        self.assertEqual(
                            run_campaign_module.run_record_supersession(args), 0
                        )
                    acquire_mock.assert_called_once_with(case_root)
                    self.assertFalse((case_root / "campaign.lock").exists())
                    rows = read_wire_jsonl(case_root / "campaign_log.jsonl")
                    entry = next(
                        row
                        for row in rows
                        if row.get("record_type")
                        == "campaign_occurrence_supersession"
                    )
                    self.assertEqual(
                        entry["selected_occurrence"]["source_manifest"]["path"],
                        selected_path,
                    )
                    self.assertEqual(
                        [
                            row["source_manifest"]["path"]
                            for row in entry["superseded_occurrences"]
                        ],
                        superseded_paths,
                    )
                finally:
                    self.root = original_root

    def _retry_occurrence_fixture(self, binding):
        members = []
        for bundle_id, gross, position in (
            ("p2-neg8-reference-start__r1", 8.0, "start"),
            ("p2-retried-work__r1", None, None),
            ("p2-neg8-reference-end__r1", 8.04, "end"),
        ):
            member = self._member(
                bundle_id,
                records=_clean_idle_records(),
                gross_energy_j=gross,
                neg8_position=position,
            )
            members.append((bundle_id, position, member))
            (member.bundle_path / "summary_metrics.json").write_text(
                json.dumps({"status": "succeeded", **member.summary}) + "\n"
            )
            (member.bundle_path / "metadata.json").write_text(
                json.dumps(member.metadata) + "\n"
            )
        work_id = self._install_retry_occurrence_manifests(binding, members)
        quarantine = Path(tempfile.mkdtemp(prefix="jw-superseded-"))
        self.addCleanup(shutil.rmtree, quarantine, True)
        shutil.copytree(self.root / work_id, quarantine / work_id)
        return members, work_id, quarantine / work_id

    def test_neg8_bracket_not_evaluated_for_per_segment_invocations(self) -> None:
        """Fix round 1 (blocker): the bracket is a whole-window check.

        The canonical Window-A sequence runs the start and end NEG-8
        references as SEPARATE run_campaign invocations.  An end-only or a
        no-reference invocation must record the non-drift
        ``neg8_bracket_not_evaluated`` condition, never a spurious
        ``failed``/``missing`` -- otherwise every real production verdict is
        red and the prospective bracket acceptance never actually compares.
        A whole-window pass (both references) still performs the comparison.
        """

        binding = self._binding()

        end_only = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "p2-neg8-reference-end__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.5,
                    neg8_position="end",
                )
            ],
            binding,
        )
        self.assertEqual(end_only["neg8_bracket"]["decision"], "not_evaluated")
        self.assertIn("neg8_bracket_not_evaluated", end_only["conditions"])
        self.assertNotIn("neg8_bracket_missing", end_only["conditions"])

        no_reference = run_campaign_module.idle_admission_core_verdict(
            [self._member("p2-work-a__r1", records=_clean_idle_records())],
            binding,
        )
        self.assertEqual(
            no_reference["neg8_bracket"]["decision"], "not_evaluated"
        )
        self.assertIn(
            "neg8_bracket_not_evaluated", no_reference["conditions"]
        )

        whole_window = run_campaign_module.idle_admission_core_verdict(
            [
                self._member(
                    "p2-neg8-reference-start__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.0,
                    neg8_position="start",
                ),
                self._member(
                    "p2-neg8-reference-end__r1",
                    records=_clean_idle_records(),
                    gross_energy_j=8.04,
                    neg8_position="end",
                ),
            ],
            binding,
            neg8_drift_bound=self._drift_bound(),
        )
        self.assertEqual(whole_window["neg8_bracket"]["decision"], "passed")
        self.assertNotIn(
            "neg8_bracket_not_evaluated", whole_window["conditions"]
        )

    def test_whole_window_runner_threads_calibration_custody_store(self) -> None:
        binding = self._binding()
        custody_store = self.root / "portable-calibration-custody"
        args = run_campaign_module.parse_args(
            [
                "--whole-window-verdict",
                "--runs-dir",
                str(self.root),
                "--campaign-policy",
                str(binding.path),
                "--calibration-custody-store",
                str(custody_store),
            ]
        )
        with (
            patch.object(
                run_campaign_module,
                "_load_calibration_snapshot_for_evaluation",
                return_value=object(),
            ) as snapshot_loader,
            patch.object(
                run_campaign_module,
                "calibration_bracket_for_bundles",
                return_value=(None, ("instrument_calibration_bracket_missing",)),
            ),
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 1)
        snapshot_loader.assert_called_once_with(str(custody_store))

    def test_whole_window_runner_threads_binding_into_consumption_session(self) -> None:
        _policy_binding, args = self._install_passing_whole_window_verdict_fixture(
            bound_lineage={"schema_version": "test-lineage", "plan_id": "plan-1"}
        )
        args.consumption_semantics_id = (
            run_campaign_module.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
        )
        args.bracket_binding = str(self.root / "calibration_bracket_binding.json")
        snapshot = object()
        bracket_binding = {"schema_version": "test-binding"}
        bracket_identity = {
            "window_id": "window-1",
            "plan_id": "plan-1",
            "plan_sha256": "a" * 64,
            "evidence_root_id": "evidence-1",
        }
        session = Mock()
        session._prepare.side_effect = RuntimeError("stop after session construction")

        with (
            patch.object(
                run_campaign_module,
                "_load_calibration_snapshot_for_evaluation",
                return_value=snapshot,
            ),
            patch.object(
                run_campaign_module,
                "_validated_bracket_binding_input",
                return_value=(bracket_binding, bracket_identity),
            ),
            patch.object(
                run_campaign_module,
                "AuthenticatedConsumptionSession",
                return_value=session,
            ) as session_type,
            self.assertRaisesRegex(RuntimeError, "stop after session construction"),
        ):
            run_campaign_module.run_whole_window_verdict(args)

        session_type.assert_called_once_with(
            self.root,
            set(),
            consumption_semantics_id=(
                run_campaign_module.MAX_BRACKET_CONSUMPTION_SEMANTICS_ID
            ),
            calibration_ledger_snapshot=snapshot,
            calibration_bracket_binding=bracket_binding,
        )

    def test_whole_window_cli_uses_campaign_membership_and_strict_validation(self) -> None:
        lineage = {"schema_version": "test-lineage", "plan_id": "plan-1"}
        _binding, args = self._install_passing_whole_window_verdict_fixture(
            bound_lineage=lineage
        )
        calibration_bracket = {
            "schema_version": "joulewise.instrument_calibration_bracket.v1",
            "status": "passed",
            "b_fiducial_s": 0.02,
            "pre": {"bracket_runs_root": str(self.root)},
            "post": {},
        }
        with (
            patch.object(run_campaign_module, "validate_bundle", return_value=[]),
            patch.object(
                run_campaign_module,
                "calibration_bracket_for_bundles",
                return_value=(calibration_bracket, ()),
            ),
            patch(
                "joulewise.whole_window.authenticate_launch_lineage",
                side_effect=lambda value, **_kwargs: {
                    "launch_lineage": dict(value)
                },
            ),
            patch(
                "joulewise.whole_window._authenticated_bundle_launch_lineage_set",
                return_value=lineage,
            ),
            patch(
                "joulewise.whole_window._calibration_launch_lineages",
                return_value=(lineage, lineage),
            ),
            patch.object(
                run_campaign_module,
                "acquire_campaign_lock",
                wraps=run_campaign_module.acquire_campaign_lock,
            ) as acquire_mock,
        ):
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 0)
        acquire_mock.assert_called_once_with(self.root)
        self.assertFalse((self.root / "campaign.lock").exists())
        verdict = read_all_jsonl(self.root / "campaign_log.jsonl")[-1]
        self.assertEqual(
            verdict["record_type"], "idle_admission_whole_window_verdict"
        )
        self.assertEqual(verdict["status"], "passed")
        self.assertEqual(verdict["member_failures"], [])
        self.assertEqual(
            verdict["idle_admission_core"]["neg8_bracket"]["decision"],
            "passed",
        )
        self.assertNotIn(
            "neg8_bracket_not_evaluated",
            verdict["idle_admission_core"]["conditions"],
        )
        self.assertEqual(
            verdict["evaluation_basis"]["schema_version"],
            "joulewise.idle_admission_evaluation_basis.v1",
        )
        self.assertEqual(
            verdict["evaluation_basis"]["consumption_semantics_id"],
            MINTED_CONSUMPTION_SEMANTICS_ID,
        )
        self.assertEqual(verdict["evaluation_basis"]["launch_lineage"], lineage)

    def test_existing_verdict_output_refuses_after_one_log_append(self) -> None:
        lineage = {"schema_version": "test-lineage", "plan_id": "plan-1"}
        _binding, args = self._install_passing_whole_window_verdict_fixture(
            bound_lineage=lineage
        )
        output_path = self.root / "whole_window_verdict.json"
        occupied = b"occupied\n"
        output_path.write_bytes(occupied)
        args.whole_window_verdict_output = str(output_path)
        calibration_bracket = {
            "schema_version": "joulewise.instrument_calibration_bracket.v1",
            "status": "passed",
            "b_fiducial_s": 0.02,
            "pre": {"bracket_runs_root": str(self.root)},
            "post": {},
        }
        stderr = io.StringIO()
        with (
            patch.object(run_campaign_module, "parse_args", return_value=args),
            patch.object(run_campaign_module, "validate_bundle", return_value=[]),
            patch.object(
                run_campaign_module,
                "calibration_bracket_for_bundles",
                return_value=(calibration_bracket, ()),
            ),
            patch(
                "joulewise.whole_window.authenticate_launch_lineage",
                side_effect=lambda value, **_kwargs: {
                    "launch_lineage": dict(value)
                },
            ),
            patch(
                "joulewise.whole_window._authenticated_bundle_launch_lineage_set",
                return_value=lineage,
            ),
            patch(
                "joulewise.whole_window._calibration_launch_lineages",
                return_value=(lineage, lineage),
            ),
            redirect_stdout(io.StringIO()),
            redirect_stderr(stderr),
        ):
            self.assertEqual(run_campaign_module.main([]), 2)

        self.assertIn(
            "refusing to overwrite existing whole-window verdict output",
            stderr.getvalue(),
        )
        verdict_rows = [
            row
            for row in read_all_jsonl(self.root / "campaign_log.jsonl")
            if row.get("record_type") == "idle_admission_whole_window_verdict"
        ]
        self.assertEqual(len(verdict_rows), 1)
        self.assertEqual(output_path.read_bytes(), occupied)
        self.assertFalse((self.root / "campaign.lock").exists())

    def test_verdict_output_publish_failure_leaves_no_target_and_one_log_row(self) -> None:
        lineage = {"schema_version": "test-lineage", "plan_id": "plan-1"}
        _binding, args = self._install_passing_whole_window_verdict_fixture(
            bound_lineage=lineage
        )
        output_path = self.root / "whole_window_verdict.json"
        args.whole_window_verdict_output = str(output_path)
        calibration_bracket = {
            "schema_version": "joulewise.instrument_calibration_bracket.v1",
            "status": "passed",
            "b_fiducial_s": 0.02,
            "pre": {"bracket_runs_root": str(self.root)},
            "post": {},
        }
        stderr = io.StringIO()
        with (
            patch.object(run_campaign_module, "parse_args", return_value=args),
            patch.object(
                run_campaign_module.os, "link", side_effect=OSError("injected link failure")
            ),
            patch.object(run_campaign_module, "validate_bundle", return_value=[]),
            patch.object(
                run_campaign_module,
                "calibration_bracket_for_bundles",
                return_value=(calibration_bracket, ()),
            ),
            patch(
                "joulewise.whole_window.authenticate_launch_lineage",
                side_effect=lambda value, **_kwargs: {
                    "launch_lineage": dict(value)
                },
            ),
            patch(
                "joulewise.whole_window._authenticated_bundle_launch_lineage_set",
                return_value=lineage,
            ),
            patch(
                "joulewise.whole_window._calibration_launch_lineages",
                return_value=(lineage, lineage),
            ),
            redirect_stdout(io.StringIO()),
            redirect_stderr(stderr),
        ):
            self.assertEqual(run_campaign_module.main([]), 2)

        self.assertIn("injected link failure", stderr.getvalue())
        verdict_rows = [
            row
            for row in read_all_jsonl(self.root / "campaign_log.jsonl")
            if row.get("record_type") == "idle_admission_whole_window_verdict"
        ]
        self.assertEqual(len(verdict_rows), 1)
        self.assertFalse(output_path.exists())
        self.assertEqual(
            list(output_path.parent.glob(f"{output_path.name}.tmp-*")), []
        )
        self.assertFalse((self.root / "campaign.lock").exists())

    def test_whole_window_verdict_refuses_mismatched_bound_lineage(self) -> None:
        member_lineage = {
            "schema_version": "test-lineage",
            "plan_id": "plan-1",
        }
        bound_lineage = {
            "schema_version": "test-lineage",
            "plan_id": "plan-2",
        }
        _binding, args = self._install_passing_whole_window_verdict_fixture(
            bound_lineage=bound_lineage
        )
        calibration_bracket = {
            "schema_version": "joulewise.instrument_calibration_bracket.v1",
            "status": "passed",
            "b_fiducial_s": 0.02,
            "pre": {"bracket_runs_root": str(self.root)},
            "post": {},
        }
        with (
            patch.object(run_campaign_module, "validate_bundle", return_value=[]),
            patch.object(
                run_campaign_module,
                "calibration_bracket_for_bundles",
                return_value=(calibration_bracket, ()),
            ),
            patch(
                "joulewise.whole_window.authenticate_launch_lineage",
                side_effect=lambda value, **_kwargs: {
                    "launch_lineage": dict(value)
                },
            ),
            patch(
                "joulewise.whole_window._authenticated_bundle_launch_lineage_set",
                return_value=member_lineage,
            ),
            patch(
                "joulewise.whole_window._calibration_launch_lineages",
                return_value=(member_lineage, member_lineage),
            ),
        ):
            with self.assertRaisesRegex(
                run_campaign_module.LaunchLineageError,
                "members, calibrations, and bound",
            ):
                run_campaign_module.run_whole_window_verdict(args)
        self.assertFalse((self.root / "campaign_log.jsonl").exists())

    def test_duplicate_occurrence_without_supersession_still_refuses(self) -> None:
        binding = self._binding()
        _members, _work_id, _quarantine = self._retry_occurrence_fixture(binding)
        _sources, _manifests, conditions, supersessions = (
            run_campaign_module._whole_window_campaign_membership(
                self.root, binding.sha256
            )
        )
        self.assertIn(
            "whole_window_campaign_membership_unresolved", conditions
        )
        self.assertEqual(supersessions, [])

    def test_recorded_supersession_resolves_present_retry_and_is_reported(
        self,
    ) -> None:
        binding = self._binding()
        drift_bound_path = self._write_drift_bound()
        _members, work_id, quarantine = self._retry_occurrence_fixture(binding)
        record_args = run_campaign_module.parse_args(
            [
                "--record-supersession",
                work_id,
                "--quarantine-path",
                str(quarantine),
                "--reason",
                "failed member moved before retry",
                "--runs-dir",
                str(self.root),
                "--campaign-policy",
                str(binding.path),
            ]
        )
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                run_campaign_module.run_record_supersession(record_args), 0
            )
        verdict_args = run_campaign_module.parse_args(
            [
                "--whole-window-verdict",
                "--runs-dir",
                str(self.root),
                "--campaign-policy",
                str(binding.path),
                "--neg8-drift-bound",
                str(drift_bound_path),
            ]
        )
        with (
            patch.object(run_campaign_module, "validate_bundle", return_value=[]),
            patch.object(
                run_campaign_module,
                "calibration_bracket_for_bundles",
                return_value=(
                    {
                        "schema_version": "joulewise.instrument_calibration_bracket.v1",
                        "status": "passed",
                        "pre": {"evidence_sha256": "a" * 64},
                        "post": {"evidence_sha256": "b" * 64},
                        "b_fiducial_s": 0.02,
                    },
                    (),
                ),
            ),
        ):
            self.assertEqual(
                run_campaign_module.run_whole_window_verdict(verdict_args), 0
            )
        verdict = read_all_jsonl(self.root / "campaign_log.jsonl")[-1]
        self.assertEqual(verdict["status"], "passed")
        self.assertEqual(
            verdict["occurrence_supersessions"][0]["bundle_id"], work_id
        )
        self.assertEqual(
            verdict["evaluation_basis"]["calibration_bracket_set"],
            {
                "pre": {"evidence_sha256": "a" * 64},
                "post": {"evidence_sha256": "b" * 64},
            },
        )

    def test_recorded_supersession_never_resolves_two_present_copies(self) -> None:
        binding = self._binding()
        _members, work_id, quarantine = self._retry_occurrence_fixture(binding)
        record_args = run_campaign_module.parse_args(
            [
                "--record-supersession",
                work_id,
                "--quarantine-path",
                str(quarantine),
                "--reason",
                "failed member moved before retry",
                "--runs-dir",
                str(self.root),
                "--campaign-policy",
                str(binding.path),
            ]
        )
        with redirect_stdout(io.StringIO()):
            self.assertEqual(
                run_campaign_module.run_record_supersession(record_args), 0
            )
        shutil.copytree(self.root / work_id, self.root / "moved-copy")
        _sources, _manifests, conditions, supersessions = (
            run_campaign_module._whole_window_campaign_membership(
                self.root, binding.sha256
            )
        )
        self.assertIn(
            "whole_window_campaign_membership_ambiguous", conditions
        )
        self.assertEqual(supersessions, [])

    def test_whole_window_verdict_honors_and_reports_failed_member_waiver(
        self,
    ) -> None:
        binding = self._binding()
        drift_bound_path = self._write_drift_bound()
        manifest_members = []
        for bundle_id, status, gross_energy_j, position in (
            ("p2-neg8-reference-start__r1", "succeeded", 8.0, "start"),
            ("p2-waived-work__r1", "failed", None, None),
            ("p2-neg8-reference-end__r1", "succeeded", 8.04, "end"),
        ):
            member = self._member(
                bundle_id,
                records=_clean_idle_records(),
                gross_energy_j=gross_energy_j,
                neg8_position=position,
            )
            manifest_members.append((bundle_id, position, member))
            (member.bundle_path / "summary_metrics.json").write_text(
                json.dumps({"status": status, **member.summary}) + "\n"
            )
            (member.bundle_path / "metadata.json").write_text(
                json.dumps(member.metadata) + "\n"
            )
        self._install_whole_window_manifest(binding, manifest_members)
        waivers = self.root / "waivers.json"
        waivers.write_text(
            json.dumps(
                [
                    {
                        "bundle_id": "p2-waived-work__r1",
                        "reason": "operator reviewed failed member",
                        "approver": "test-operator",
                        "timestamp": "2026-07-23T07:00:00Z",
                        "scope": "status_failed",
                    }
                ]
            )
            + "\n"
        )
        args = run_campaign_module.parse_args(
            [
                "--whole-window-verdict",
                "--runs-dir",
                str(self.root),
                "--campaign-policy",
                str(binding.path),
                "--waivers",
                str(waivers),
                "--neg8-drift-bound",
                str(drift_bound_path),
            ]
        )
        with (
            patch.object(run_campaign_module, "validate_bundle", return_value=[]),
            patch.object(
                run_campaign_module,
                "calibration_bracket_for_bundles",
                return_value=(
                    {
                        "schema_version": "joulewise.instrument_calibration_bracket.v1",
                        "status": "passed",
                        "b_fiducial_s": 0.02,
                    },
                    (),
                ),
            ),
        ):
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 0)
        verdict = read_all_jsonl(self.root / "campaign_log.jsonl")[-1]
        self.assertEqual(verdict["status"], "flagged")
        self.assertEqual(
            verdict["waived_bundles"][0]["bundle_id"], "p2-waived-work__r1"
        )
        self.assertEqual(
            verdict["waived_bundles"][0]["waiver"]["scope"], "status_failed"
        )
        self.assertNotIn(
            "whole_window_bundle_invalid",
            verdict["idle_admission_core"]["conditions"],
        )
        self.assertEqual(verdict["member_failures"], [])

    def test_whole_window_invalid_reference_is_excluded_and_cannot_pass(self) -> None:
        binding = self._binding()
        bundle_ids = [
            "p2-neg8-reference-start__r1",
            "p2-neg8-reference-end__r1",
        ]
        manifest_members = []
        for bundle_id, gross, position in zip(
            bundle_ids, (8.0, 8.04), ("start", "end")
        ):
            member = self._member(
                bundle_id,
                records=_clean_idle_records(),
                gross_energy_j=gross,
                neg8_position=position,
            )
            manifest_members.append((bundle_id, position, member))
            (member.bundle_path / "summary_metrics.json").write_text(
                json.dumps({"status": "succeeded", **member.summary}) + "\n"
            )
            (member.bundle_path / "metadata.json").write_text(
                json.dumps(member.metadata) + "\n"
            )
        self._install_whole_window_manifest(binding, manifest_members)
        args = run_campaign_module.parse_args(
            [
                "--whole-window-verdict",
                "--runs-dir",
                str(self.root),
                "--campaign-policy",
                str(binding.path),
            ]
        )

        def validate(path, strict):
            return ["quarantined reference"] if "start" in path.name else []

        with patch.object(run_campaign_module, "validate_bundle", side_effect=validate):
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 1)
        verdict = read_all_jsonl(self.root / "campaign_log.jsonl")[-1]
        self.assertEqual(verdict["status"], "failed")
        self.assertEqual(
            verdict["excluded_bundles"][0]["bundle_id"], bundle_ids[0]
        )
        self.assertEqual(
            [
                (failure["member_id"], failure["reason_code"])
                for failure in verdict["member_failures"]
            ],
            [(bundle_ids[0], "whole_window_bundle_invalid")],
        )
        self.assertIn(
            "quarantined reference",
            verdict["member_failures"][0]["detail"],
        )
        self.assertIn(
            "whole_window_bundle_invalid",
            verdict["idle_admission_core"]["conditions"],
        )

    def test_whole_window_production_verdict_fails_closed_without_end_reference(self) -> None:
        binding = self._binding()
        member = self._member(
            "p2-neg8-reference-start__r1",
            records=_clean_idle_records(),
            gross_energy_j=8.0,
            neg8_position="start",
        )
        (member.bundle_path / "summary_metrics.json").write_text(
            json.dumps({"status": "succeeded", **member.summary}) + "\n"
        )
        (member.bundle_path / "metadata.json").write_text(
            json.dumps(member.metadata) + "\n"
        )
        args = run_campaign_module.parse_args(
            [
                "--whole-window-verdict",
                "--runs-dir",
                str(self.root),
                "--campaign-policy",
                str(binding.path),
            ]
        )

        self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 1)
        verdict = read_all_jsonl(self.root / "campaign_log.jsonl")[-1]
        self.assertEqual(verdict["status"], "failed")
        self.assertEqual(
            verdict["idle_admission_core"]["neg8_bracket"]["decision"],
            "failed",
        )
        self.assertIn(
            "neg8_bracket_missing",
            verdict["idle_admission_core"]["conditions"],
        )
        self.assertEqual(
            {
                failure["reason_code"]
                for failure in verdict["member_failures"]
            },
            {"whole_window_bundle_invalid"},
        )


def _d100_authenticated_bracket(bound_s: float = 0.02) -> dict:
    return {
        "schema_version": "joulewise.instrument_calibration_bracket.v1",
        "status": "passed",
        "b_fiducial_s": bound_s,
        "pre": {
            "manifest_sha256": "1" * 64,
            "evidence_sha256": "2" * 64,
            "b_fiducial_s": bound_s,
        },
        "post": {
            "manifest_sha256": "3" * 64,
            "evidence_sha256": "4" * 64,
            "b_fiducial_s": bound_s,
        },
    }


@contextmanager
def d100_real_salvage_leaf_patches():
    """Stub only hardware/strict leaves, preserving every D-100 constructor."""

    bracket = _d100_authenticated_bracket()
    calibration_snapshot, _candidates = _fixture_snapshot([])

    class StoredSummaryReduction:
        def __init__(self, bundle_path: Path):
            self.bundle_path = Path(bundle_path)

        def to_dict(self) -> dict:
            return json.loads(
                (self.bundle_path / "summary_metrics.json").read_text(
                    encoding="utf-8"
                )
            )

    with (
        patch.object(run_campaign_module, "validate_bundle", return_value=[]),
        patch.object(
            run_campaign_module,
            "_load_calibration_snapshot_for_evaluation",
            return_value=calibration_snapshot,
        ),
        patch.object(
            run_campaign_module,
            "calibration_bracket_for_bundles",
            return_value=(bracket, ()),
        ),
        patch(
            "joulewise.whole_window.calibration_bracket_for_bundles",
            return_value=(bracket, ()),
        ),
        patch(
            "joulewise.whole_window.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ),
        patch(
            "joulewise.whole_window.load_calibration_ledger_snapshot",
            return_value=calibration_snapshot,
        ),
        patch(
            "joulewise.analysis_engine.inputs.load_calibration_acceptance_bound",
            return_value=_unissued_acceptance_fixture(),
        ),
        patch(
            "joulewise.analysis_engine.inputs.load_calibration_ledger_snapshot",
            return_value=calibration_snapshot,
        ),
        patch(
            "joulewise.whole_window._verify_instrument_calibration",
            return_value=(0.02, None),
        ),
        patch.object(
            run_campaign_module,
            "_current_member_environment_refusals",
            return_value=(),
        ),
        patch(
            "joulewise.whole_window.current_environment_refusals",
            return_value=(),
        ),
        patch(
            "joulewise.reduce.reduce_bundle",
            side_effect=lambda bundle_path, **_kwargs: StoredSummaryReduction(
                Path(bundle_path)
            ),
        ),
    ):
        yield


def install_real_salvage_window(
    root: Path,
    *,
    ordinary_bundle_ids: tuple[str, ...] = (),
    session_id: str = "d100-real-salvage-window",
) -> tuple[object, dict, list[str]]:
    """Install real manifests, binding, closure, bundles, and runner arguments."""

    from joulewise.salvage_dangler import (
        SALVAGE_CLOSURE_SCHEMA,
        inspect_salvage_attempt,
    )

    root.mkdir(parents=True, exist_ok=True)
    policy_path = (
        ROOT
        / "configs"
        / "campaign_policies"
        / "quiet_mac_p2_production.json"
    )
    policy = run_campaign_module.load_campaign_policy(str(policy_path))
    helper = IdleAdmissionCoreVerdictTests()
    helper.root = root
    drift_bound_path = helper._write_drift_bound()

    reference_rows: list[tuple[str, str, object]] = []
    all_bundle_ids = [
        "d100-neg8-reference-start",
        *ordinary_bundle_ids,
        "d100-neg8-reference-end",
    ]
    for index, bundle_id in enumerate(all_bundle_ids):
        position = (
            "start"
            if bundle_id == "d100-neg8-reference-start"
            else "end"
            if bundle_id == "d100-neg8-reference-end"
            else None
        )
        point_j = 8.0 + index * 0.01
        evaluation = helper._member(
            bundle_id,
            records=_clean_idle_records(30),
            gross_energy_j=point_j,
            neg8_position=position,
        )
        config_raw = (evaluation.bundle_path / "config.json").read_bytes()
        metadata = dict(evaluation.metadata)
        metadata["config_sha256"] = hashlib.sha256(config_raw).hexdigest()
        metadata["adapters"] = {"telemetry": {"name": "powermetrics"}}
        metadata["instrument_calibration"] = {
            **metadata["instrument_calibration"],
            "verified_effective_b_fiducial_s": 0.02,
        }
        metadata["uncertainty_evidence"] = {
            "clock_anchor": {"method": ACTIVE_CAPTURE_ANCHOR_METHOD},
        }
        (evaluation.bundle_path / "metadata.json").write_text(
            json.dumps(metadata, sort_keys=True) + "\n", encoding="utf-8"
        )

        def envelope(value: float) -> dict:
            return {
                "method": "common_trace_shift_plus_independent_edge_corners_v3",
                "anchor_bound_s": 0.02,
                "point_j": value,
                "lower_j": value - 0.01,
                "upper_j": value + 0.01,
                "max_abs_delta_j": 0.01,
            }

        summary = {
            "status": "succeeded",
            "gross_energy_j": point_j,
            "idle_subtracted_energy_j": point_j - 0.2,
            "summary_provenance": {"reducer_version": "0.5.2"},
            "measurement_quality": {"telemetry_source": "powermetrics"},
            "energy_anchor_shift_envelopes": {
                "/gross_energy_j": envelope(point_j),
                "/idle_subtracted_energy_j": envelope(point_j - 0.2),
            },
            "window_evidence_precheck": {
                "gross_request": {"eligible": True, "reasons": []},
                "idle_subtracted_request": {"eligible": True, "reasons": []},
            },
        }
        (evaluation.bundle_path / "summary_metrics.json").write_text(
            json.dumps(summary, sort_keys=True) + "\n", encoding="utf-8"
        )
        (evaluation.bundle_path / "events.jsonl").write_text(
            json.dumps(
                {
                    "event_type": "stage_started",
                    "phase": "measured_run",
                    "timestamp_s": 100.0,
                    "message": "",
                    "metadata": {},
                }
            )
            + "\n"
            + json.dumps(
                {
                    "event_type": "stage_completed",
                    "phase": "measured_run",
                    "timestamp_s": 101.0,
                    "message": "",
                    "metadata": {},
                }
            )
            + "\n",
            encoding="utf-8",
        )
        if position is not None:
            reference_rows.append((bundle_id, position, evaluation))

    manifest_dir = root / "campaign_manifests"
    manifest_dir.mkdir()
    manifest_path = manifest_dir / f"{session_id}.json"
    evaluated_by_id = {
        bundle_id: evaluation
        for bundle_id, _position, evaluation in reference_rows
    }
    manifest_members = []
    for bundle_id in all_bundle_ids:
        position = (
            "start"
            if bundle_id == "d100-neg8-reference-start"
            else "end"
            if bundle_id == "d100-neg8-reference-end"
            else None
        )
        member = {
            "config": f"{bundle_id}.json",
            "run_id": bundle_id,
            "execution": "invoked",
            "bundle_ids": [bundle_id],
            "role": (
                run_campaign_module.NEG8_REFERENCE_ROLE
                if position is not None
                else None
            ),
            "sentinel_position": position,
            "canonical_neg8_workload": position is not None,
        }
        if position is not None:
            member["scientific_config_sha256"] = evaluated_by_id[
                bundle_id
            ].scientific_config_sha256
        manifest_members.append(member)
    manifest_members.insert(
        -1,
        {
            "config": "d100-dangler.json",
            "run_id": "d100-dangler",
            "execution": "invoked",
            "bundle_ids": ["d100-dangler"],
            "role": None,
            "sentinel_position": None,
            "canonical_neg8_workload": False,
        },
    )
    manifest = {
        "schema_version": "joulewise.campaign_provenance.v1",
        "session_id": session_id,
        "analysis_manifest_id": None,
        "campaign_policy": {"sha256": policy.sha256},
        "members": manifest_members,
    }
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8"
    )
    record = run_campaign_module.load_campaign_provenance_manifest(manifest_path)
    if record is None:
        raise AssertionError("real D-100 source manifest did not parse")
    descriptors = [run_campaign_module._membership_manifest_descriptor(root, record)]
    membership_id = run_campaign_module.whole_window_membership_id(descriptors)
    binding_path = root / "d100-membership-binding.json"
    binding_path.write_text(
        json.dumps(
            {
                "schema_version": run_campaign_module.MEMBERSHIP_BINDING_SCHEMA,
                "campaign_policy_sha256": policy.sha256,
                "source_campaign_manifests": descriptors,
                "membership_id": membership_id,
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    quarantine = root / "d100-quarantine"
    quarantine.mkdir()
    inspected = []
    attempt_paths = []
    fixture = ROOT / "tests" / "fixtures" / "salvage_dangler" / "r5a_idle_abort"
    for index in range(3):
        attempt = quarantine / f"attempt-{index}"
        shutil.copytree(fixture, attempt)
        for name in ("config.json", "metadata.json"):
            payload = json.loads((attempt / name).read_text(encoding="utf-8"))
            payload["run_id"] = "d100-dangler"
            (attempt / name).write_text(
                json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8"
            )
        inspected.append(inspect_salvage_attempt(attempt))
        attempt_paths.append(attempt)
    quarantine_manifest = [
        {
            "path": path.relative_to(quarantine).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "size": path.stat().st_size,
        }
        for path in sorted(
            candidate for candidate in quarantine.rglob("*") if candidate.is_file()
        )
    ]
    closure_path = root / "d100-salvage-closure.json"
    closure_path.write_text(
        json.dumps(
            {
                "schema_version": SALVAGE_CLOSURE_SCHEMA,
                "campaign_policy_sha256": policy.sha256,
                "membership_binding_sha256": hashlib.sha256(
                    binding_path.read_bytes()
                ).hexdigest(),
                "opened_at": "2026-08-01T10:00:00Z",
                "closed_at": "2026-08-01T12:00:00Z",
                "custody_roots": [str(quarantine)],
                "quarantine_root": str(quarantine),
                "quarantine_manifest": quarantine_manifest,
                "terminal_occurrence_index": 2,
                "occurrences": [
                    {
                        "timestamp": f"2026-08-01T10:0{index}:00Z",
                        "quarantine_path": str(attempt),
                        "license_branch": observation["license_branch"],
                        "failure_signature_sha256": observation[
                            "failure_signature_sha256"
                        ],
                        "evidence_paths": observation["artifact_manifest"],
                        "operator_deviations": [],
                    }
                    for index, (attempt, observation) in enumerate(
                        zip(attempt_paths, inspected, strict=True)
                    )
                ],
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    failed_row = {
        "record_type": "idle_admission_whole_window_verdict",
        "status": "failed",
        "bundle_ids": ["d100-dangler"],
    }
    log_path = root / "campaign_log.jsonl"
    log_path.write_text(
        json.dumps(failed_row, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    args = run_campaign_module.parse_args(
        [
            "--whole-window-verdict",
            "--runs-dir",
            str(root),
            "--log",
            str(log_path),
            "--campaign-policy",
            str(policy_path),
            "--neg8-drift-bound",
            str(drift_bound_path),
            "--consumption-semantics-id",
            run_campaign_module.SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
            "--window-membership-binding",
            str(binding_path),
            "--salvage-closure",
            str(closure_path),
        ]
    )
    return args, failed_row, all_bundle_ids


class D100MembershipRepairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    @staticmethod
    def occurrence(bundle_id: str, index: int) -> dict:
        return {
            "bundle_id": bundle_id,
            "source_manifest": {
                "path": f"campaign_manifests/{index}.json",
                "sha256": str(index) * 64,
            },
            "member_index": 0,
            "bundle_index": 0,
        }

    def test_r3_presence_first_resolution_is_count_independent(self) -> None:
        bundle_id = "ordinary"
        one = [self.occurrence(bundle_id, 1)]
        many = [self.occurrence(bundle_id, 1), self.occurrence(bundle_id, 2)]
        present = self.root / bundle_id
        selected = many[-1]
        supersession = {
            "bundle_id": bundle_id,
            "campaign_policy_sha256": "a" * 64,
            "selected_occurrence": selected,
            "superseded_occurrences": many[:-1],
        }
        cases = (
            ([present], one, ([], []), "selected"),
            ([], one, ([], []), "terminal_absent"),
            ([present], many, ([supersession], [True]), "selected"),
            ([], many, ([], []), "terminal_absent"),
            ([present, self.root / "copy"], one, ([], []), "ambiguous"),
            ([present], many, ([supersession], [False]), "ambiguous"),
            ([present], one, ([supersession], [False]), "ambiguous"),
            (
                [present],
                many,
                ([supersession, supersession], [True, False]),
                "ambiguous",
            ),
        )
        for paths, occurrences, evidence, expected in cases:
            with self.subTest(expected=expected), patch.object(
                run_campaign_module,
                "ordinary_present_bundle_paths",
                return_value=paths,
            ):
                resolution = run_campaign_module._resolve_ordinary_occurrence(
                    self.root,
                    bundle_id,
                    occurrences,
                    "a" * 64,
                    evidence,
                )
            self.assertEqual(resolution.status, expected)

    def test_reader_failopen_valid_plus_wrong_schema_manifest_refuses(self) -> None:
        self._write_manifest(
            "valid.json",
            [
                self._member("neg8-start", position="start"),
                self._member("neg8-end", position="end"),
            ],
        )
        malformed = self.root / "campaign_manifests" / "malformed.json"
        malformed.write_text(
            json.dumps(
                {
                    "schema_version": "joulewise.campaign_provenance.future",
                    "analysis_manifest_id": "d100-window",
                    "campaign_policy": {"sha256": "a" * 64},
                    "members": [self._member("neg8-start", position="start")],
                }
            )
            + "\n"
        )
        for bundle_id in ("neg8-start", "neg8-end"):
            path = self.root / bundle_id
            path.mkdir()
            (path / "summary_metrics.json").write_text('{"status":"succeeded"}\n')
        resolution = run_campaign_module._whole_window_campaign_membership(
            self.root, "a" * 64
        )
        self.assertEqual(
            resolution.conditions,
            ("whole_window_campaign_membership_unresolved",),
        )

    def _write_manifest(self, name: str, members: list[dict]) -> object:
        directory = self.root / "campaign_manifests"
        directory.mkdir(exist_ok=True)
        path = directory / name
        payload = {
            "schema_version": "joulewise.campaign_provenance.v1",
            "analysis_manifest_id": "d100-window",
            "campaign_policy": {"sha256": "a" * 64},
            "members": members,
        }
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        record = run_campaign_module.load_campaign_provenance_manifest(path)
        self.assertIsNotNone(record)
        return record

    @staticmethod
    def _member(bundle_id: str, *, position: str | None = None) -> dict:
        return {
            "config": f"{bundle_id}.json",
            "run_id": bundle_id,
            "execution": "invoked",
            "bundle_ids": [bundle_id],
            "role": (
                run_campaign_module.NEG8_REFERENCE_ROLE
                if position is not None
                else None
            ),
            "sentinel_position": position,
            "canonical_neg8_workload": position is not None,
        }

    def test_r2_unrelated_supersession_survives_failing_sibling(self) -> None:
        start = "neg8-start"
        retried = "retried"
        absent = "absent"
        end = "neg8-end"
        records = [
            self._write_manifest("00.json", [self._member(retried)]),
            self._write_manifest(
                "01.json",
                [
                    self._member(start, position="start"),
                    self._member(retried),
                    self._member(absent),
                    self._member(end, position="end"),
                ],
            ),
        ]
        for bundle_id in (start, retried, end):
            path = self.root / bundle_id
            path.mkdir()
            (path / "config.json").write_text(json.dumps({"run_id": bundle_id}))
            (path / "summary_metrics.json").write_text('{"status":"succeeded"}\n')
        descriptors = run_campaign_module.source_manifest_descriptors(
            self.root, [record.path for record in records]
        )
        first = {
            "bundle_id": retried,
            "source_manifest": descriptors[0],
            "member_index": 0,
            "bundle_index": 0,
        }
        second = {
            "bundle_id": retried,
            "source_manifest": descriptors[1],
            "member_index": 1,
            "bundle_index": 0,
        }
        supersession = {
            "bundle_id": retried,
            "campaign_policy_sha256": "a" * 64,
            "selected_occurrence": second,
            "superseded_occurrences": [first],
        }
        with (
            patch.object(
                run_campaign_module,
                "load_authenticated_campaign_catalog",
                return_value=records,
            ),
            patch.object(
                run_campaign_module,
                "supersession_entry_validation_results",
                return_value=([supersession], [True]),
            ),
        ):
            resolution = run_campaign_module._whole_window_campaign_membership(
                self.root, "a" * 64
            )
        self.assertIn("whole_window_campaign_membership_unresolved", resolution.conditions)
        self.assertEqual(
            [row["bundle_id"] for row in resolution.occurrence_supersessions],
            [retried],
        )

    def test_r4_null_identity_binding_is_exhaustive_and_descriptor_derived(self) -> None:
        records = [
            self._write_manifest("00.json", [self._member("one")]),
            self._write_manifest("01.json", [self._member("two")]),
        ]
        for record in records:
            record.value["analysis_manifest_id"] = None
        descriptors = [
            run_campaign_module._membership_manifest_descriptor(self.root, record)
            for record in records
        ]
        descriptors.sort(key=lambda row: row["path"])
        membership_id = run_campaign_module.whole_window_membership_id(descriptors)
        binding = self.root / "binding.json"
        binding.write_text(
            json.dumps(
                {
                    "schema_version": run_campaign_module.MEMBERSHIP_BINDING_SCHEMA,
                    "campaign_policy_sha256": "a" * 64,
                    "source_campaign_manifests": descriptors,
                    "membership_id": membership_id,
                }
            )
            + "\n"
        )
        loaded = run_campaign_module.load_window_membership_binding(
            binding,
            runs_dir=self.root,
            policy_sha256="a" * 64,
            catalog=records,
        )
        self.assertEqual(loaded["membership_id"], membership_id)

        value = json.loads(binding.read_text())
        falsifiers = (
            descriptors[:-1],
            [descriptors[1], descriptors[0]],
            [*descriptors, {"path": "extra.json", "sha256": "c" * 64, "size": 1}],
        )
        for supplied in falsifiers:
            with self.subTest(supplied=supplied):
                value["source_campaign_manifests"] = supplied
                value["membership_id"] = run_campaign_module.whole_window_membership_id(
                    supplied
                )
                binding.write_text(json.dumps(value) + "\n")
                with self.assertRaisesRegex(ValueError, "exhaustive"):
                    run_campaign_module.load_window_membership_binding(
                        binding,
                        runs_dir=self.root,
                        policy_sha256="a" * 64,
                        catalog=records,
                    )

    def test_r1_r6_r8_terminal_absence_requires_exactly_one_salvage_license(self) -> None:
        records = [
            self._write_manifest(
                "window.json",
                [
                    self._member("neg8-start", position="start"),
                    self._member("dangler"),
                    self._member("neg8-end", position="end"),
                ],
            )
        ]
        records[0].value["analysis_manifest_id"] = None
        for bundle_id in ("neg8-start", "neg8-end"):
            path = self.root / bundle_id
            path.mkdir()
            (path / "config.json").write_text(json.dumps({"run_id": bundle_id}))
            (path / "summary_metrics.json").write_text('{"status":"succeeded"}\n')
        descriptors = [
            run_campaign_module._membership_manifest_descriptor(self.root, record)
            for record in records
        ]
        binding_path = self.root / "binding.json"
        binding_path.write_text(
            json.dumps(
                {
                    "schema_version": run_campaign_module.MEMBERSHIP_BINDING_SCHEMA,
                    "campaign_policy_sha256": "a" * 64,
                    "source_campaign_manifests": descriptors,
                    "membership_id": run_campaign_module.whole_window_membership_id(
                        descriptors
                    ),
                }
            )
            + "\n"
        )
        with patch.object(
            run_campaign_module,
            "load_authenticated_campaign_catalog",
            return_value=records,
        ):
            default = run_campaign_module._whole_window_campaign_membership(
                self.root, "a" * 64, membership_binding_path=binding_path
            )
        self.assertIn("whole_window_campaign_membership_unresolved", default.conditions)

        exclusion = {"bundle_id": "dangler", "payload_sha256": "c" * 64}
        with (
            patch.object(
                run_campaign_module,
                "load_authenticated_campaign_catalog",
                return_value=records,
            ),
            patch.object(
                run_campaign_module,
                "authorize_salvage_dangler_exclusion",
                return_value=exclusion,
            ) as authorize,
        ):
            salvage = run_campaign_module._whole_window_campaign_membership(
                self.root,
                "a" * 64,
                membership_binding_path=binding_path,
                consumption_semantics_id=(
                    run_campaign_module.SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
                ),
                salvage_closure_path=self.root / "closure.json",
            )
        self.assertEqual(salvage.conditions, ())
        self.assertEqual(
            {source.path.name for source in salvage.sources},
            {"neg8-start", "neg8-end"},
        )
        self.assertEqual(salvage.salvage_dangler_exclusion, exclusion)
        authorize.assert_called_once()

        # A second absent ordinary member exceeds the mechanical cap before
        # authorization is even considered.
        records[0].value["members"].insert(2, self._member("second-dangler"))
        with (
            patch.object(
                run_campaign_module,
                "load_authenticated_campaign_catalog",
                return_value=records,
            ),
            patch.object(
                run_campaign_module,
                "authorize_salvage_dangler_exclusion",
            ) as authorize_two,
        ):
            two = run_campaign_module._whole_window_campaign_membership(
                self.root,
                "a" * 64,
                membership_binding_path=binding_path,
                consumption_semantics_id=(
                    run_campaign_module.SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID
                ),
                salvage_closure_path=self.root / "closure.json",
            )
        self.assertIn("whole_window_campaign_membership_unresolved", two.conditions)
        authorize_two.assert_not_called()

    def test_r7_missing_bytes_refuse_despite_clean_strict_ledger_flags(self) -> None:
        manifest_path = self.root / "campaign_manifests" / "window.json"
        manifest_path.parent.mkdir()
        manifest = {
            "schema_version": "joulewise.campaign_provenance.v1",
            "analysis_manifest_id": "d100-window",
            "campaign_policy": {"sha256": "a" * 64},
            "members": [
                {
                    **self._member("neg8-start", position="start"),
                    "outcome": "succeeded",
                    "strict_valid": True,
                    "classification": "clean",
                },
                {
                    **self._member("neg8-end", position="end"),
                    "outcome": "succeeded",
                    "strict_valid": True,
                    "classification": "clean",
                },
            ],
        }
        raw = (json.dumps(manifest) + "\n").encode()
        manifest_path.write_bytes(raw)
        record = type("CatalogRecord", (), {})()
        record.path = manifest_path
        record.raw_bytes = raw
        record.value = manifest
        records = [record]
        with patch.object(
            run_campaign_module,
            "load_authenticated_campaign_catalog",
            return_value=records,
        ):
            resolution = run_campaign_module._whole_window_campaign_membership(
                self.root, "a" * 64
            )
        self.assertIn("whole_window_campaign_membership_unresolved", resolution.conditions)
        self.assertEqual(resolution.sources, ())

    def test_salvage_cli_requires_binding_closure_and_refuses_waivers(self) -> None:
        base = [
            "--whole-window-verdict",
            "--consumption-semantics-id",
            run_campaign_module.SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
        ]
        with self.assertRaises(SystemExit):
            run_campaign_module.parse_args(base)
        with self.assertRaises(SystemExit):
            run_campaign_module.parse_args(
                [
                    *base,
                    "--window-membership-binding",
                    "binding.json",
                    "--salvage-closure",
                    "closure.json",
                    "--waivers",
                    "waivers.json",
                ]
            )

    def test_r8_salvage_runner_appends_new_pinned_row_without_editing_failure(self) -> None:
        args, failed_row, expected_bundle_ids = install_real_salvage_window(self.root)
        log_path = self.root / "campaign_log.jsonl"
        original = log_path.read_bytes()
        with d100_real_salvage_leaf_patches(), redirect_stdout(io.StringIO()):
            self.assertEqual(run_campaign_module.run_whole_window_verdict(args), 0)
        self.assertTrue(log_path.read_bytes().startswith(original))
        rows = read_all_jsonl(log_path)
        self.assertIn(failed_row, rows[:-1])
        row = rows[-1]
        self.assertEqual(row["status"], "passed")
        self.assertEqual(row["bundle_ids"], expected_bundle_ids)
        self.assertEqual(
            row["evaluation_basis"]["consumption_semantics_id"],
            run_campaign_module.SALVAGE_DANGLER_CONSUMPTION_SEMANTICS_ID,
        )
        self.assertEqual(
            row["salvage_dangler_exclusion"],
            row["evaluation_basis"]["salvage_dangler_exclusion"],
        )
        self.assertEqual(
            row["salvage_dangler_exclusion"]["bundle_id"], "d100-dangler"
        )


if __name__ == "__main__":
    unittest.main()
