from __future__ import annotations

import copy
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest import mock

from joulewise.analysis_manifest_v3 import FINALIZED_BASENAME_SUFFIX
from joulewise.calibration_bracketing import build_calibration_bracket_binding
from joulewise.calibration_ledger import (
    CUSTODY_STORE_MANIFEST_NAME,
    GENESIS_DIGEST,
    LEDGER_SCHEMA,
    append_bracket_session_receipt,
    artifact_hashes,
    calibration_custody_store_manifest_bytes,
    canonical_json_bytes,
    canonical_sha256,
    finalize_bracket_session_slot,
    load_calibration_ledger_snapshot,
    terminal_head_pin_for_session,
)
from joulewise.whole_window import AuthenticatedConsumptionSession
from scripts import build_bracket_binding as binding_cli
from scripts.finalize_analysis_manifest import main as finalize_main
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _install_cli_fixture(
    root: Path,
    *,
    edit_descriptors: object | None = None,
    complete_custody_store: bool = False,
) -> dict:
    fixture = install_synthetic_finalization_fixture(root)
    if complete_custody_store:
        _rebuild_complete_calibration_session(fixture)
    binding = json.loads(fixture["bracket_path"].read_text())
    fixture["original_verdict_bytes"] = fixture["verdict_path"].read_bytes()
    fixture["original_campaign_log_bytes"] = (
        fixture["runs_root"] / "campaign_log.jsonl"
    ).read_bytes()

    def descriptor(role: str) -> dict[str, str]:
        endpoint = binding["endpoints"][role]
        return {
            "bracket_session_id": binding["session_id"],
            "bracket_slot": role,
            "bracket_window_id": binding["window_id"],
            "bracket_plan_id": binding["plan_id"],
            "bracket_plan_sha256": binding["plan_sha256"],
            "bracket_evidence_root_id": binding["evidence_root_id"],
            "bracket_runs_root": binding["runs_root"],
            "attempt_id": endpoint["attempt_id"],
            "ledger_receipt_digest": endpoint["receipt_digest"],
            "content_id": endpoint["content_digest"],
        }

    pre = descriptor("pre")
    post = descriptor("post")
    if edit_descriptors is not None:
        edit_descriptors(pre, post)

    verdict = json.loads(fixture["verdict_path"].read_text())
    bracket_set = verdict["evaluation_basis"]["calibration_bracket_set"]
    bracket_set["pre"] = copy.deepcopy(pre)
    bracket_set["post"] = copy.deepcopy(post)
    stored_bracket = verdict["idle_admission_core"][
        "instrument_calibration_bracket"
    ]
    stored_bracket["pre"] = copy.deepcopy(pre)
    stored_bracket["post"] = copy.deepcopy(post)
    basis = verdict["evaluation_basis"]
    basis["sha256"] = canonical_sha256(
        {key: value for key, value in basis.items() if key != "sha256"}
    )
    _write_json(fixture["verdict_path"], verdict)

    log_path = fixture["runs_root"] / "campaign_log.jsonl"
    rows = [json.loads(line) for line in log_path.read_text().splitlines() if line]
    matches = [
        index
        for index, row in enumerate(rows)
        if row.get("record_type") == "idle_admission_whole_window_verdict"
    ]
    if len(matches) != 1:
        raise AssertionError(f"synthetic fixture has {len(matches)} verdict rows")
    rows[matches[0]] = verdict
    log_path.write_bytes(b"".join(canonical_json_bytes(row) + b"\n" for row in rows))

    fixture["head_pin_path"] = fixture["ledger_path"].with_name(
        "calibration_ledger_head.json"
    )
    fixture["produced_path"] = root / "produced_bracket_binding.json"
    fixture["descriptors"] = {"pre": pre, "post": post}
    return fixture


def _rebuild_complete_calibration_session(fixture: dict) -> None:
    """Upgrade the shared four-artifact fixture for real store authentication."""

    old_snapshot = load_calibration_ledger_snapshot(
        fixture["ledger_path"],
        fixture["ledger_path"].with_name("calibration_ledger_head.json"),
        require_committed_pin=False,
        verify_custody=False,
    )
    old_session = old_snapshot.bracket_sessions[0]
    slots = {}
    for role in ("pre", "post"):
        observation = old_session.finalized_slots[role]
        custody = Path(observation.custody_locator)
        (custody / "power_trace.csv").write_text(
            "timestamp_s,power_w\n99.0,1.0\n",
            encoding="utf-8",
        )
        slots[role] = {
            "attempt_id": observation.attempt_id,
            "custody_locator": observation.custody_locator,
            "identity_epoch": dict(observation.identity_epoch),
            "t1_bindings": dict(observation.t1_bindings),
        }

    ledger_path = fixture["ledger_path"]
    head_pin_path = ledger_path.with_name("calibration_ledger_head.json")
    ledger_path.unlink()
    _write_json(
        head_pin_path,
        {
            "sequence": 0,
            "head_digest": GENESIS_DIGEST,
            "ledger_schema": LEDGER_SCHEMA,
        },
    )
    append_bracket_session_receipt(
        ledger_path,
        session_id=old_session.session_id,
        window_id=old_session.window_id,
        plan_id=old_session.plan_id,
        plan_sha256=old_session.plan_sha256,
        evidence_root_id=old_session.evidence_root_id,
        runs_root=old_session.runs_root,
        slots=slots,
        head_pin_path=head_pin_path,
        require_committed_pin=False,
    )
    for role in ("pre", "post"):
        old_observation = old_session.finalized_slots[role]
        custody = Path(old_observation.custody_locator)
        finalize_bracket_session_slot(
            ledger_path,
            session_id=old_session.session_id,
            slot=role,
            disposition="valid",
            custody_locator=str(custody),
            artifact_sha256=artifact_hashes(custody),
            identity_epoch=old_observation.identity_epoch,
            t1_bindings=old_observation.t1_bindings,
            capture_wall_time_s=old_observation.capture_wall_time_s,
            exact_bound_lexeme_s=old_observation.exact_bound_lexeme_s,
        )
    _write_json(
        head_pin_path,
        terminal_head_pin_for_session(
            ledger_path,
            session_id=old_session.session_id,
        ),
    )
    snapshot = load_calibration_ledger_snapshot(
        ledger_path,
        head_pin_path,
        require_committed_pin=False,
        verify_custody=True,
    )
    binding = build_calibration_bracket_binding(
        snapshot,
        session_id=old_session.session_id,
        window_id=old_session.window_id,
        plan_id=old_session.plan_id,
        plan_sha256=old_session.plan_sha256,
        evidence_root_id=old_session.evidence_root_id,
        runs_root=old_session.runs_root,
    )
    if binding is None:
        raise AssertionError("complete calibration fixture did not bind")
    _write_json(fixture["bracket_path"], binding)


def _restore_original_whole_window_fixture(fixture: dict) -> None:
    """Restore the helper's deliberately descriptor-free calibration seam."""

    fixture["verdict_path"].write_bytes(fixture["original_verdict_bytes"])
    (fixture["runs_root"] / "campaign_log.jsonl").write_bytes(
        fixture["original_campaign_log_bytes"]
    )


def _binding_args(
    fixture: dict,
    *,
    output: Path | None = None,
    custody_store: Path | None = None,
) -> list[str]:
    args = [
        "--custody-root",
        str(fixture["root"]),
        "--whole-window-verdict",
        str(fixture["verdict_path"]),
        "--calibration-ledger",
        str(fixture["ledger_path"]),
        "--head-pin",
        str(fixture["head_pin_path"]),
    ]
    if custody_store is not None:
        args.extend(("--calibration-custody-store", str(custody_store)))
    args.extend(("--output", str(output or fixture["produced_path"])))
    return args


def _run_binding_cli(
    fixture: dict,
    *,
    output: Path | None = None,
    custody_store: Path | None = None,
) -> tuple[int, dict]:
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        code = binding_cli.main(
            _binding_args(
                fixture,
                output=output,
                custody_store=custody_store,
            )
        )
    return code, json.loads(stdout.getvalue())


def _install_calibration_custody_store(fixture: dict) -> Path:
    snapshot = load_calibration_ledger_snapshot(
        fixture["ledger_path"],
        fixture["head_pin_path"],
        require_committed_pin=False,
        verify_custody=True,
    )
    if snapshot.refusal_reasons:
        raise AssertionError(snapshot.refusal_reasons)
    store = fixture["root"] / "calibration-custody-store"
    store.mkdir()
    for observation in snapshot.observations:
        if observation.content_id is not None:
            shutil.copytree(
                observation.custody_locator,
                store / observation.content_id,
            )
    (store / CUSTODY_STORE_MANIFEST_NAME).write_bytes(
        calibration_custody_store_manifest_bytes(snapshot)
    )
    return store


def _finalizer_args(
    fixture: dict,
    *,
    binding_path: Path | None = None,
    runs_root: Path | None = None,
) -> list[str]:
    return [
        "--prospective-manifest",
        str(fixture["prospective_path"]),
        "--plan-tree",
        str(fixture["plan_tree_path"]),
        "--custody-root",
        str(fixture["root"]),
        "--runs-root",
        str(runs_root or fixture["runs_root"]),
        "--whole-window-verdict",
        str(fixture["verdict_path"]),
        "--bracket-binding",
        str(binding_path or fixture["produced_path"]),
        "--calibration-ledger",
        str(fixture["ledger_path"]),
        "--aggregate-floor-artifact",
        str(fixture["floor_path"]),
        "--output-dir",
        str(fixture["root"]),
    ]


def _run_finalizer(
    fixture: dict,
    *,
    binding_path: Path | None = None,
    runs_root: Path | None = None,
) -> tuple[int, dict]:
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        code = finalize_main(
            _finalizer_args(
                fixture, binding_path=binding_path, runs_root=runs_root
            )
        )
    return code, json.loads(stdout.getvalue())


def _finalized_path(fixture: dict) -> Path:
    return fixture["root"] / (
        fixture["prospective"]["manifest_id"] + FINALIZED_BASENAME_SUFFIX
    )


def _rewrite_binding_digest(binding: dict) -> None:
    binding["binding_digest"] = hashlib.sha256(
        canonical_json_bytes(
            {key: value for key, value in binding.items() if key != "binding_digest"}
        )
    ).hexdigest()


class BracketBindingCliTests(unittest.TestCase):
    def test_emits_canonical_bytes_identical_to_whole_window_producer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            code, result = _run_binding_cli(fixture)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "BUILT")

            snapshot = load_calibration_ledger_snapshot(
                fixture["ledger_path"],
                fixture["head_pin_path"],
                require_committed_pin=False,
                verify_custody=True,
            )
            verdict = json.loads(fixture["verdict_path"].read_text())
            session = AuthenticatedConsumptionSession(
                fixture["runs_root"],
                set(),
                evaluation_basis_sha256=verdict["evaluation_basis"]["sha256"],
                calibration_ledger_snapshot=snapshot,
            )
            in_memory = session._basis_bracket_binding()
            self.assertIsNotNone(in_memory)
            expected = canonical_json_bytes(in_memory) + b"\n"
            self.assertEqual(fixture["produced_path"].read_bytes(), expected)

            emitted = json.loads(expected)
            self.assertEqual(
                emitted["binding_digest"],
                canonical_sha256(
                    {
                        key: value
                        for key, value in emitted.items()
                        if key != "binding_digest"
                    }
                ),
            )

    def test_finalizer_accepts_cli_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            self.assertEqual(_run_binding_cli(fixture)[0], 0)
            # The shared finalizer helper intentionally patches its production
            # calibration bracket down to {schema,status,b_fiducial_s}; restore
            # that otherwise-valid whole-window row after exercising the CLI's
            # real descriptor path. Bracket/ledger authentication remains real.
            _restore_original_whole_window_fixture(fixture)
            code, result = _run_finalizer(fixture)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "FINALIZED")
            self.assertTrue(Path(result["output"]).is_file())

    def test_finalizer_refuses_runs_root_different_from_authenticated_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            self.assertEqual(_run_binding_cli(fixture)[0], 0)
            other_runs = fixture["root"] / "other-runs"
            shutil.copytree(fixture["runs_root"], other_runs)

            code, refusal = _run_finalizer(fixture, runs_root=other_runs)
            self.assertEqual(code, 2)
            self.assertEqual(refusal["status"], "REFUSE")
            self.assertEqual(
                refusal["reason"],
                "analysis_finalization_bracket_binding_mismatch",
            )
            self.assertFalse(_finalized_path(fixture).exists())

    def test_finalizer_refuses_each_tampered_binding_without_output(self) -> None:
        attacks = {
            "binding_digest": lambda binding, fixture: binding.__setitem__(
                "binding_digest", "0" * 64
            ),
            "endpoint_receipt": lambda binding, fixture: (
                binding["endpoints"]["pre"].__setitem__(
                    "receipt_digest", "0" * 64
                ),
                _rewrite_binding_digest(binding),
            ),
            "runs_root": lambda binding, fixture: (
                (fixture["root"] / "other-runs").mkdir(),
                binding.__setitem__(
                    "runs_root", str(fixture["root"] / "other-runs")
                ),
                _rewrite_binding_digest(binding),
            ),
        }
        for name, attack in attacks.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                fixture = _install_cli_fixture(Path(tmp))
                self.assertEqual(_run_binding_cli(fixture)[0], 0)
                binding = json.loads(fixture["produced_path"].read_text())
                attack(binding, fixture)
                _write_json(fixture["produced_path"], binding)

                code, refusal = _run_finalizer(fixture)
                self.assertEqual(code, 2)
                self.assertEqual(refusal["status"], "REFUSE")
                self.assertEqual(
                    refusal["reason"],
                    "analysis_finalization_bracket_binding_mismatch",
                )
                self.assertFalse(_finalized_path(fixture).exists())

    def test_refuses_invalid_or_unpinned_ledger_snapshot(self) -> None:
        pin_attacks = {
            "invalid": {"not": "a head pin"},
            "stale": {
                "sequence": 0,
                "head_digest": "0" * 64,
                "ledger_schema": "joulewise.calibration_observation_ledger.v2",
            },
        }
        for name, pin in pin_attacks.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                fixture = _install_cli_fixture(Path(tmp))
                _write_json(fixture["head_pin_path"], pin)
                code, refusal = _run_binding_cli(fixture)
                self.assertEqual(code, 2)
                self.assertEqual(refusal["status"], "REFUSE")
                self.assertEqual(
                    refusal["reason"], binding_cli.REFUSAL_LEDGER_REFUSED
                )
                self.assertFalse(fixture["produced_path"].exists())

    def test_refuses_explicit_invalid_calibration_custody_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            empty_store = fixture["root"] / "empty-custody-store"
            empty_store.mkdir()

            code, refusal = _run_binding_cli(
                fixture,
                custody_store=empty_store,
            )

            self.assertEqual(code, 2)
            self.assertEqual(refusal["status"], "REFUSE")
            self.assertEqual(
                refusal["reason"], binding_cli.REFUSAL_LEDGER_REFUSED
            )
            self.assertIn(
                "calibration_ledger_custody_invalid", refusal["detail"]
            )
            self.assertFalse(fixture["produced_path"].exists())

    def test_accepts_explicit_valid_calibration_custody_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(
                Path(tmp), complete_custody_store=True
            )
            custody_store = _install_calibration_custody_store(fixture)

            code, result = _run_binding_cli(
                fixture,
                custody_store=custody_store,
            )

            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "BUILT")
            self.assertTrue(fixture["produced_path"].is_file())

    def test_refuses_session_that_is_not_finalized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            snapshot = load_calibration_ledger_snapshot(
                fixture["ledger_path"],
                fixture["head_pin_path"],
                require_committed_pin=False,
                verify_custody=True,
            )
            session = snapshot.bracket_sessions[0]
            altered = replace(
                snapshot,
                bracket_sessions=(replace(session, state="open"),),
            )
            with mock.patch.object(
                binding_cli, "load_calibration_ledger_snapshot", return_value=altered
            ):
                code, refusal = _run_binding_cli(fixture)
            self.assertEqual(code, 2)
            self.assertEqual(
                refusal["reason"], binding_cli.REFUSAL_SESSION_NOT_FINALIZED
            )
            self.assertFalse(fixture["produced_path"].exists())

    def test_refuses_session_without_two_valid_slots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            snapshot = load_calibration_ledger_snapshot(
                fixture["ledger_path"],
                fixture["head_pin_path"],
                require_committed_pin=False,
                verify_custody=True,
            )
            session = snapshot.bracket_sessions[0]
            slots = dict(session.finalized_slots)
            slots["pre"] = replace(slots["pre"], disposition="invalid")
            altered = replace(
                snapshot,
                bracket_sessions=(replace(session, finalized_slots=slots),),
            )
            with mock.patch.object(
                binding_cli, "load_calibration_ledger_snapshot", return_value=altered
            ):
                code, refusal = _run_binding_cli(fixture)
            self.assertEqual(code, 2)
            self.assertEqual(
                refusal["reason"], binding_cli.REFUSAL_SESSION_ENDPOINTS_INVALID
            )
            self.assertFalse(fixture["produced_path"].exists())

    def test_refuses_endpoint_digest_not_authenticated_by_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(
                Path(tmp),
                edit_descriptors=lambda pre, post: pre.__setitem__(
                    "ledger_receipt_digest", "0" * 64
                ),
            )
            code, refusal = _run_binding_cli(fixture)
            self.assertEqual(code, 2)
            self.assertEqual(
                refusal["reason"], binding_cli.REFUSAL_ENDPOINT_MISMATCH
            )
            self.assertFalse(fixture["produced_path"].exists())

    def test_refuses_disagreeing_pre_post_descriptors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(
                Path(tmp),
                edit_descriptors=lambda pre, post: post.__setitem__(
                    "bracket_plan_id", "substituted-plan"
                ),
            )
            code, refusal = _run_binding_cli(fixture)
            self.assertEqual(code, 2)
            self.assertEqual(
                refusal["reason"], binding_cli.REFUSAL_DESCRIPTOR_MISMATCH
            )
            self.assertFalse(fixture["produced_path"].exists())

    def test_refuses_runs_root_outside_finalization_custody(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            container = Path(tmp)
            custody = container / "custody"
            custody.mkdir()
            outside_runs = container / "outside-runs"
            outside_runs.mkdir()
            fixture = _install_cli_fixture(
                custody,
                edit_descriptors=lambda pre, post: (
                    pre.__setitem__("bracket_runs_root", str(outside_runs)),
                    post.__setitem__("bracket_runs_root", str(outside_runs)),
                ),
            )
            code, refusal = _run_binding_cli(fixture)
            self.assertEqual(code, 2)
            self.assertEqual(
                refusal["reason"], binding_cli.REFUSAL_CUSTODY_INVALID
            )
            self.assertFalse(fixture["produced_path"].exists())

    def test_refuses_to_clobber_existing_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            fixture["produced_path"].write_bytes(b"owned\n")
            code, refusal = _run_binding_cli(fixture)
            self.assertEqual(code, 2)
            self.assertEqual(refusal["reason"], binding_cli.REFUSAL_OUTPUT_EXISTS)
            self.assertEqual(fixture["produced_path"].read_bytes(), b"owned\n")

    def test_publish_failure_leaves_no_target_or_temporary_and_can_retry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            with mock.patch.object(
                binding_cli.os,
                "write",
                side_effect=OSError("injected write failure"),
            ):
                code, refusal = _run_binding_cli(fixture)

            self.assertEqual(code, 2)
            self.assertEqual(refusal["status"], "REFUSE")
            self.assertEqual(refusal["reason"], binding_cli.REFUSAL_OUTPUT_FAILED)
            self.assertFalse(fixture["produced_path"].exists())
            self.assertEqual(
                list(
                    fixture["produced_path"].parent.glob(
                        f"{fixture['produced_path'].name}.tmp-*"
                    )
                ),
                [],
            )

            retry_code, retry_result = _run_binding_cli(fixture)
            self.assertEqual(retry_code, 0)
            self.assertEqual(retry_result["status"], "BUILT")
            self.assertTrue(fixture["produced_path"].is_file())

    def test_temporary_close_failure_is_an_output_refusal_and_cleans_up(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "binding.json"
            real_close = binding_cli.os.close

            def close_then_fail(descriptor: int) -> None:
                real_close(descriptor)
                raise OSError("injected close failure")

            with mock.patch.object(
                binding_cli.os,
                "close",
                side_effect=close_then_fail,
            ):
                with self.assertRaises(binding_cli.BracketBindingRefusal) as raised:
                    binding_cli._publish_no_clobber(target, b"{}\n")

            self.assertEqual(
                raised.exception.reason, binding_cli.REFUSAL_OUTPUT_FAILED
            )
            self.assertFalse(target.exists())
            self.assertEqual(list(target.parent.glob(f"{target.name}.tmp-*")), [])

    def test_invalid_invocation_is_one_json_refusal_on_stdout(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                code = binding_cli.main([])
            except SystemExit as exc:
                code = exc.code

        self.assertEqual(code, 2)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(len(stdout.getvalue().splitlines()), 1)
        self.assertEqual(
            json.loads(stdout.getvalue()),
            {
                "status": "REFUSE",
                "reason": "bracket_binding_invocation_invalid",
                "detail": (
                    "the following arguments are required: --custody-root, "
                    "--whole-window-verdict, --calibration-ledger, --output"
                ),
            },
        )

    def test_help_keeps_normal_successful_argparse_behavior(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                binding_cli.main(["--help"])

        self.assertEqual(raised.exception.code, 0)
        self.assertIn("usage:", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
