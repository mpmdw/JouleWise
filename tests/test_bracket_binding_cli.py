from __future__ import annotations

import copy
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace
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
from joulewise.idle_admission import ADAPTER_CONTINUITY_SCHEMA
from scripts import build_bracket_binding as binding_cli
from scripts.finalize_analysis_manifest import main as finalize_main
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
from tests import test_calibration_live_three_window as live_three_window_module
from tests.test_run_campaign import read_all_jsonl, run_campaign_module
from tests.receipt_corpus import ReceiptCorpus


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def _install_cli_fixture(
    root: Path,
    *,
    complete_custody_store: bool = False,
) -> dict:
    root = root.resolve()
    fixture = install_synthetic_finalization_fixture(root)
    if complete_custody_store:
        _rebuild_complete_calibration_session(fixture)
    binding = json.loads(fixture["bracket_path"].read_text())
    fixture["head_pin_path"] = fixture["ledger_path"].with_name(
        "calibration_ledger_head.json"
    )
    fixture["produced_path"] = (
        fixture["runs_root"] / "produced_bracket_binding.json"
    )
    fixture["identity"] = {
        key: binding[key]
        for key in (
            "session_id",
            "window_id",
            "plan_id",
            "plan_sha256",
            "evidence_root_id",
            "runs_root",
        )
    }
    fixture["frozen_plan_path"] = fixture["prospective_path"].parent / fixture[
        "prospective"
    ]["plan"]["path"]
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


def _binding_args(
    fixture: dict,
    *,
    output: Path | None = None,
    custody_store: Path | None = None,
    identity: dict | None = None,
    frozen_plan: Path | None = None,
) -> list[str]:
    selected = identity or fixture["identity"]
    args = [
        "--custody-root",
        str(fixture["root"]),
        "--session-id",
        selected["session_id"],
        "--window-id",
        selected["window_id"],
        "--plan-id",
        selected["plan_id"],
        "--plan-sha256",
        selected["plan_sha256"],
        "--frozen-plan",
        str(frozen_plan or fixture["frozen_plan_path"]),
        "--evidence-root-id",
        selected["evidence_root_id"],
        "--runs-root",
        selected["runs_root"],
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
    identity: dict | None = None,
    frozen_plan: Path | None = None,
) -> tuple[int, dict]:
    stdout = io.StringIO()
    with redirect_stdout(stdout):
        code = binding_cli.main(
            _binding_args(
                fixture,
                output=output,
                custody_store=custody_store,
                identity=identity,
                frozen_plan=frozen_plan,
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


def _install_three_window_e2e_fixture(
    root: Path,
    source: type[live_three_window_module.CalibrationLiveThreeWindowTests],
) -> dict:
    """Adapt the issued three-window ledger to the finalizer's gamma corpus."""

    root = root.resolve()
    fixture = _install_cli_fixture(root)
    roots = {
        "alpha": root / "calibration-windows" / "alpha",
        "beta": root / "calibration-windows" / "beta",
        "gamma": fixture["runs_root"],
    }
    for path in roots.values():
        path.mkdir(parents=True, exist_ok=True)

    identities = {
        name: {
            key: value
            for key, value in source.windows[name].items()
            if key
            in {
                "session_id",
                "window_id",
                "plan_id",
                "plan_sha256",
                "evidence_root_id",
            }
        }
        | {"runs_root": str(roots[name])}
        for name in ("alpha", "beta", "gamma")
    }
    prospective = fixture["prospective"]
    identities["gamma"].update(
        {
            "window_id": prospective["plan"]["plan_id"],
            "plan_id": prospective["plan"]["plan_id"],
            "plan_sha256": prospective["plan"]["sha256"],
            "evidence_root_id": prospective["evidence_root_id"],
        }
    )
    identity_by_session = {
        value["session_id"]: value for value in identities.values()
    }
    receipts = ReceiptCorpus(
        json.loads(line)
        for line in source.final_ledger_bytes.splitlines()
        if line.strip()
    )

    def rebind(row: dict) -> dict:
        value = copy.deepcopy(row)
        identity = identity_by_session.get(value.get("session_id"))
        if identity is None:
            return value
        for field in (
            "window_id",
            "plan_id",
            "plan_sha256",
            "evidence_root_id",
            "runs_root",
        ):
            if field in value:
                value[field] = identity[field]
        slots = value.get("slots")
        if isinstance(slots, dict):
            for slot in slots.values():
                if isinstance(slot, dict) and isinstance(slot.get("attempt_id"), str):
                    slot["custody_locator"] = str(
                        Path(identity["runs_root"])
                        / "instrument_validation"
                        / slot["attempt_id"]
                    )
        if isinstance(value.get("attempt_id"), str) and "custody_locator" in value:
            value["custody_locator"] = str(
                Path(identity["runs_root"])
                / "instrument_validation"
                / value["attempt_id"]
            )
        return value

    rebound = ReceiptCorpus(rebind(row) for row in receipts)
    rechained = source._rechain(rebound)
    fixture["ledger_path"].write_bytes(
        b"".join(canonical_json_bytes(row) + b"\n" for row in rechained)
    )
    terminal = next(reversed(tuple(rechained)))
    _write_json(
        fixture["head_pin_path"],
        {
            "sequence": terminal["sequence"],
            "head_digest": terminal["receipt_digest"],
            "ledger_schema": LEDGER_SCHEMA,
        },
    )
    snapshot = load_calibration_ledger_snapshot(
        fixture["ledger_path"],
        fixture["head_pin_path"],
        baseline_sequence=source.base_sequence,
        baseline_digest=source.base_digest,
        require_committed_pin=False,
        verify_custody=False,
    )
    if snapshot.refusal_reasons:
        raise AssertionError(snapshot.refusal_reasons)
    fixture["snapshot"] = snapshot
    fixture["three_window_identities"] = identities
    fixture["identity"] = dict(identities["gamma"])
    fixture["produced_path"] = fixture["runs_root"] / "produced_bracket_binding.json"

    log_path = fixture["runs_root"] / "campaign_log.jsonl"
    retained = [
        row
        for row in read_all_jsonl(log_path)
        if row.get("record_type") != "idle_admission_whole_window_verdict"
    ]
    log_path.write_bytes(
        b"".join(canonical_json_bytes(row) + b"\n" for row in retained)
    )
    fixture["verdict_path"].unlink(missing_ok=True)
    return fixture


@contextmanager
def _three_window_runtime(
    fixture: dict,
    source: type[live_three_window_module.CalibrationLiveThreeWindowTests],
):
    gamma = source.windows["gamma"]
    reader = SimpleNamespace(
        measured_window=lambda: SimpleNamespace(
            start_s=gamma["window_start_s"],
            end_s=gamma["window_end_s"],
        ),
        metadata=lambda: {
            "instrument_calibration": {"bindings": dict(source.t1)}
        },
    )
    with (
        mock.patch.object(run_campaign_module, "validate_bundle", return_value=[]),
        mock.patch.object(
            run_campaign_module, "_final_idle_admission_attempt", return_value=1
        ),
        mock.patch.object(
            run_campaign_module, "_load_idle_rich_telemetry", return_value=[]
        ),
        mock.patch.object(
            run_campaign_module, "post_run_environment_refusals", return_value=()
        ),
        mock.patch.object(
            run_campaign_module,
            "evaluate_cpu_idle_admission",
            return_value={"decision": "admitted", "conditions": []},
        ),
        mock.patch.object(
            run_campaign_module, "_adapter_observations_for", return_value=[]
        ),
        mock.patch.object(
            run_campaign_module,
            "evaluate_adapter_wattage_continuity",
            return_value={
                "schema_version": ADAPTER_CONTINUITY_SCHEMA,
                "decision": "stable",
                "conditions": [],
            },
        ),
        mock.patch.object(
            run_campaign_module,
            "_neg8_reference_scientific_config_sha256",
            return_value="8" * 64,
        ),
        mock.patch.object(
            run_campaign_module,
            "_load_calibration_snapshot_for_evaluation",
            return_value=fixture["snapshot"],
        ),
        mock.patch(
            "joulewise.calibration_bracketing.load_calibration_acceptance_bound",
            return_value=source.acceptance,
        ),
        mock.patch(
            "joulewise.calibration_bracketing._candidate_from_observation",
            side_effect=source._candidate,
        ),
        mock.patch(
            "joulewise.calibration_bracketing.BundleReader",
            return_value=reader,
        ),
        mock.patch(
            "joulewise.calibration_ledger.load_calibration_ledger_snapshot",
            return_value=fixture["snapshot"],
        ),
    ):
        yield


def _run_whole_window_evaluation(
    fixture: dict,
    *,
    binding_path: Path | None,
    verdict_output_path: Path | None = None,
) -> tuple[int, dict]:
    arguments = [
        "--whole-window-verdict",
        "--runs-dir",
        str(fixture["runs_root"]),
        "--campaign-policy",
        str(
            Path(__file__).resolve().parents[1]
            / "configs"
            / "campaign_policies"
            / "quiet_mac_p2_production.json"
        ),
        "--neg8-drift-bound",
        str(fixture["root"] / "neg8_drift_bound.json"),
    ]
    if binding_path is not None:
        arguments.extend(("--bracket-binding", str(binding_path)))
    if verdict_output_path is not None:
        arguments.extend(
            ("--whole-window-verdict-output", str(verdict_output_path))
        )
    args = run_campaign_module.parse_args(arguments)
    with redirect_stdout(io.StringIO()):
        code = run_campaign_module.run_whole_window_verdict(args)
    verdict = read_all_jsonl(fixture["runs_root"] / "campaign_log.jsonl")[-1]
    return code, verdict


class BracketBindingCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        live_three_window_module.CalibrationLiveThreeWindowTests.setUpClass()

    @classmethod
    def tearDownClass(cls) -> None:
        live_three_window_module.CalibrationLiveThreeWindowTests.tearDownClass()

    def test_emits_canonical_bytes_identical_to_in_memory_producer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            code, result = _run_binding_cli(fixture)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "BUILT")

            in_memory = json.loads(fixture["bracket_path"].read_text())
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

    def test_build_evaluate_finalize_preserves_binding_and_verdict_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_three_window_e2e_fixture(
                Path(tmp), live_three_window_module.CalibrationLiveThreeWindowTests
            )
            with mock.patch.object(
                binding_cli,
                "load_calibration_ledger_snapshot",
                return_value=fixture["snapshot"],
            ):
                self.assertEqual(_run_binding_cli(fixture)[0], 0)
            binding_before = hashlib.sha256(
                fixture["produced_path"].read_bytes()
            ).hexdigest()

            with _three_window_runtime(
                fixture, live_three_window_module.CalibrationLiveThreeWindowTests
            ):
                evaluate_code, verdict = _run_whole_window_evaluation(
                    fixture,
                    binding_path=fixture["produced_path"],
                    verdict_output_path=fixture["verdict_path"],
                )
            self.assertEqual(evaluate_code, 0)
            self.assertEqual(verdict["status"], "passed")
            binding = json.loads(fixture["produced_path"].read_text())
            bracket_set = verdict["evaluation_basis"]["calibration_bracket_set"]
            for role in ("pre", "post"):
                endpoint = binding["endpoints"][role]
                descriptor = bracket_set[role]
                self.assertEqual(descriptor["attempt_id"], endpoint["attempt_id"])
                self.assertEqual(
                    descriptor["content_id"], endpoint["content_digest"]
                )
                self.assertEqual(
                    descriptor["ledger_receipt_digest"], endpoint["receipt_digest"]
                )
                for descriptor_field, binding_field in (
                    ("bracket_session_id", "session_id"),
                    ("bracket_window_id", "window_id"),
                    ("bracket_plan_id", "plan_id"),
                    ("bracket_plan_sha256", "plan_sha256"),
                    ("bracket_evidence_root_id", "evidence_root_id"),
                    ("bracket_runs_root", "runs_root"),
                ):
                    self.assertEqual(
                        descriptor[descriptor_field], binding[binding_field]
                    )
                self.assertEqual(descriptor["bracket_slot"], role)

            campaign_log_path = fixture["runs_root"] / "campaign_log.jsonl"
            campaign_log_raw_before = campaign_log_path.read_bytes()
            campaign_verdict_row = campaign_log_raw_before.splitlines(keepends=True)[-1]
            verdict_raw_before = fixture["verdict_path"].read_bytes()
            self.assertEqual(verdict_raw_before, campaign_verdict_row)
            verdict_before = hashlib.sha256(verdict_raw_before).hexdigest()
            campaign_log_before = hashlib.sha256(campaign_log_raw_before).hexdigest()
            campaign_row_before = hashlib.sha256(campaign_verdict_row).hexdigest()
            self.assertEqual(verdict_before, campaign_row_before)

            reformatted_path = (
                fixture["runs_root"] / "reformatted_bracket_binding.json"
            )
            _write_json(
                reformatted_path,
                json.loads(fixture["produced_path"].read_bytes()),
            )
            with _three_window_runtime(
                fixture, live_three_window_module.CalibrationLiveThreeWindowTests
            ):
                refused_code, refused = _run_finalizer(
                    fixture, binding_path=reformatted_path
                )
            self.assertEqual(refused_code, 2)
            self.assertEqual(refused["status"], "REFUSE")
            self.assertEqual(
                refused["reason"],
                "analysis_finalization_bracket_binding_mismatch",
            )
            self.assertFalse(_finalized_path(fixture).exists())

            with _three_window_runtime(
                fixture, live_three_window_module.CalibrationLiveThreeWindowTests
            ):
                code, result = _run_finalizer(fixture)
            self.assertEqual(code, 0)
            self.assertEqual(result["status"], "FINALIZED")
            finalized_path = Path(result["output"])
            self.assertTrue(finalized_path.is_file())
            finalized = json.loads(finalized_path.read_text())
            self.assertEqual(
                finalized["evidence"]["bracket_binding"]["sha256"],
                binding_before,
            )
            self.assertEqual(
                finalized["evidence"]["whole_window_verdict"]["sha256"],
                verdict_before,
            )
            self.assertEqual(
                hashlib.sha256(fixture["produced_path"].read_bytes()).hexdigest(),
                binding_before,
            )
            self.assertEqual(
                hashlib.sha256(fixture["verdict_path"].read_bytes()).hexdigest(),
                verdict_before,
            )
            self.assertEqual(
                hashlib.sha256(campaign_log_path.read_bytes()).hexdigest(),
                campaign_log_before,
            )
            self.assertEqual(
                hashlib.sha256(
                    campaign_log_path.read_bytes().splitlines(keepends=True)[-1]
                ).hexdigest(),
                campaign_row_before,
            )

    def test_whole_window_evaluation_without_binding_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_three_window_e2e_fixture(
                Path(tmp), live_three_window_module.CalibrationLiveThreeWindowTests
            )
            binding = build_calibration_bracket_binding(
                fixture["snapshot"],
                **fixture["identity"],
            )
            fixture["produced_path"].write_bytes(
                canonical_json_bytes(binding) + b"\n"
            )
            with _three_window_runtime(
                fixture, live_three_window_module.CalibrationLiveThreeWindowTests
            ):
                code, verdict = _run_whole_window_evaluation(
                    fixture, binding_path=None
                )

            self.assertEqual(code, 1)
            self.assertEqual(verdict["status"], "failed")
            self.assertEqual(
                verdict["idle_admission_core"]["conditions"],
                ["calibration_bracket_binding_missing"],
            )

    def test_whole_window_evaluation_refuses_wrong_or_tampered_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_three_window_e2e_fixture(
                Path(tmp), live_three_window_module.CalibrationLiveThreeWindowTests
            )
            with mock.patch.object(
                binding_cli,
                "load_calibration_ledger_snapshot",
                return_value=fixture["snapshot"],
            ):
                self.assertEqual(_run_binding_cli(fixture)[0], 0)

            alpha = fixture["three_window_identities"]["alpha"]
            wrong_binding = build_calibration_bracket_binding(
                fixture["snapshot"],
                session_id=alpha["session_id"],
                window_id=alpha["window_id"],
                plan_id=alpha["plan_id"],
                plan_sha256=alpha["plan_sha256"],
                evidence_root_id=alpha["evidence_root_id"],
                runs_root=alpha["runs_root"],
            )
            wrong_path = fixture["runs_root"] / "wrong-window-binding.json"
            wrong_path.write_bytes(canonical_json_bytes(wrong_binding) + b"\n")

            tampered = json.loads(fixture["produced_path"].read_text())
            replacement = "0" if tampered["binding_digest"][0] != "0" else "1"
            tampered["binding_digest"] = replacement + tampered["binding_digest"][1:]
            tampered_path = fixture["runs_root"] / "tampered-binding.json"
            tampered_path.write_bytes(canonical_json_bytes(tampered) + b"\n")

            outside_path = fixture["root"] / "outside-binding.json"
            outside_path.write_bytes(fixture["produced_path"].read_bytes())
            symlink_path = fixture["runs_root"] / "symlink-binding.json"
            symlink_path.symlink_to(fixture["produced_path"])
            noncanonical_path = fixture["runs_root"] / "noncanonical-binding.json"
            _write_json(noncanonical_path, json.loads(fixture["produced_path"].read_text()))

            for name, binding_path in (
                ("different-window-plan-session", wrong_path),
                ("flipped-binding-digest", tampered_path),
                ("outside-runs-custody", outside_path),
                ("symlink", symlink_path),
                ("noncanonical-json", noncanonical_path),
            ):
                with self.subTest(name=name), _three_window_runtime(
                    fixture, live_three_window_module.CalibrationLiveThreeWindowTests
                ):
                    code, verdict = _run_whole_window_evaluation(
                        fixture, binding_path=binding_path
                    )
                self.assertEqual(code, 1)
                self.assertEqual(verdict["status"], "failed")
                self.assertEqual(
                    verdict["idle_admission_core"]["conditions"],
                    ["calibration_bracket_binding_invalid"],
                )
                self.assertNotEqual(verdict["status"], "passed")

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

    def test_refuses_frozen_plan_identity_disagreement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            identity = dict(fixture["identity"])
            identity["plan_id"] = "different-plan"
            code, refusal = _run_binding_cli(fixture, identity=identity)
            self.assertEqual(code, 2)
            self.assertEqual(
                refusal["reason"], binding_cli.REFUSAL_PLAN_INVALID
            )
            self.assertFalse(fixture["produced_path"].exists())

    def test_refuses_explicit_identity_disagreement_with_ledger(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = _install_cli_fixture(Path(tmp))
            identity = dict(fixture["identity"])
            identity["window_id"] = "different-window"
            code, refusal = _run_binding_cli(fixture, identity=identity)
            self.assertEqual(code, 2)
            self.assertEqual(
                refusal["reason"], binding_cli.REFUSAL_SESSION_IDENTITY_MISMATCH
            )
            self.assertFalse(fixture["produced_path"].exists())

    def test_refuses_runs_root_outside_finalization_custody(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            container = Path(tmp)
            custody = container / "custody"
            custody.mkdir()
            outside_runs = container / "outside-runs"
            outside_runs.mkdir()
            fixture = _install_cli_fixture(custody)
            identity = dict(fixture["identity"])
            identity["runs_root"] = str(outside_runs)
            code, refusal = _run_binding_cli(fixture, identity=identity)
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
                    "--session-id, --window-id, --plan-id, --plan-sha256, "
                    "--frozen-plan, --evidence-root-id, --runs-root, "
                    "--calibration-ledger, --output"
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
