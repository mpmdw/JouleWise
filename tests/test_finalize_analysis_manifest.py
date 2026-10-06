from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from joulewise import detection_floor, dominance_closeout
from tests.test_analysis_finalizer import install_synthetic_finalization_fixture
from tests.test_d165_dominance_closeout import (
    builder_recomputations,
    replay_sidecar,
)

ROOT = Path(__file__).resolve().parents[1]


class FinalizeSidecarCLITests(unittest.TestCase):
    def matching_sidecar(self, fixture: dict, source: Path) -> tuple[dict, bytes]:
        floor = json.loads(fixture["floor_path"].read_bytes())
        records = builder_recomputations(floor, replay_sidecar(floor))
        self.assertTrue(all(r.estimator_path == "common_mode" for r in records.values()))
        sidecar = dominance_closeout.build_d165_replay_sidecar(floor, records)
        self.assertEqual(dominance_closeout.validate_d165_replay_sidecar(sidecar), [])
        self.assertEqual(dominance_closeout._sidecar_floor_alignment_errors(floor, sidecar), [])
        self.assertIsNone(dominance_closeout._floor_member_census_error(floor, sidecar))
        raw = (json.dumps(sidecar, indent=2, sort_keys=True) + "\n").encode()
        source.write_bytes(raw)
        return sidecar, raw

    def custody_bytes(self, fixture: dict) -> dict[str, str]:
        return {str(path.relative_to(fixture["root"])): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in fixture["root"].rglob("*") if path.is_file()}

    def refuse_then_finalize(self, fixture: dict, source: Path, correct: Path) -> None:
        before = self.custody_bytes(fixture)
        result = subprocess.run(self.command(fixture) + ["--dominance-replay-sidecar", str(source)],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["reason"], "analysis_finalization_attachment_invalid")
        self.assertEqual(self.custody_bytes(fixture), before)
        result = subprocess.run(self.command(fixture) + ["--dominance-replay-sidecar", str(correct)],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "FINALIZED")

    def command(self, fixture: dict) -> list[str]:
        return [
            sys.executable, "-B", str(ROOT / "scripts/finalize_analysis_manifest.py"),
            "--prospective-manifest", str(fixture["prospective_path"]),
            "--plan-tree", str(fixture["plan_tree_path"]),
            "--custody-root", str(fixture["root"]),
            "--runs-root", str(fixture["runs_root"]),
            "--whole-window-verdict", str(fixture["verdict_path"]),
            "--bracket-binding", str(fixture["bracket_path"]),
            "--calibration-ledger", str(fixture["ledger_path"]),
            "--aggregate-floor-artifact", str(fixture["floor_path"]),
            "--output-dir", str(fixture["root"]),
        ]

    def test_documented_finalize_stages_real_common_mode_sidecar(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "custody", dominance_criterion={"rule_id": "test-dominance"}
            )
            # Real sidecar producer and replay arithmetic on labelled fixture operands.
            self.assertEqual(
                detection_floor.two_shared_edge_common_mode_registration()["estimator_id"],
                detection_floor.COMMON_MODE_ESTIMATOR_ID,
            )
            source = root / "mint-replay.json"
            sidecar, raw = self.matching_sidecar(fixture, source)
            command = self.command(fixture) + ["--dominance-replay-sidecar", str(source)]
            result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            manifest = json.loads(Path(json.loads(result.stdout)["output"]).read_text())
            attachment = manifest["evidence"]["dominance_replay_sidecar"]
            staged = fixture["root"] / attachment["path"]
            self.assertEqual(staged.read_bytes(), raw)
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(attachment["sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(attachment["sidecar_id"], sidecar["sidecar_id"])
            replay = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(replay.returncode, 0, replay.stdout + replay.stderr)
            self.assertEqual(json.loads(replay.stdout), json.loads(result.stdout))

    def test_skeleton_sidecar_refuses_without_custody_then_correct_finalizes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "custody", dominance_criterion={"rule_id": "test-dominance"}
            )
            correct = root / "correct.json"
            sidecar, _raw = self.matching_sidecar(fixture, correct)
            source = root / "skeleton.json"
            source.write_text(json.dumps({key: sidecar[key] for key in ("schema_version", "sidecar_id")}))
            self.refuse_then_finalize(fixture, source, correct)

    def test_foreign_floor_sidecar_refuses_without_custody_then_correct_finalizes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "custody", dominance_criterion={"rule_id": "test-dominance"}
            )
            correct = root / "correct.json"
            self.matching_sidecar(fixture, correct)
            foreign_floor = json.loads(fixture["floor_path"].read_bytes())
            foreign_floor["artifact_id"] = "another-floor"
            sidecar = dominance_closeout.build_d165_replay_sidecar(
                foreign_floor, builder_recomputations(foreign_floor, replay_sidecar(foreign_floor))
            )
            self.assertEqual(dominance_closeout.validate_d165_replay_sidecar(sidecar), [])
            source = root / "foreign.json"
            source.write_text(json.dumps(sidecar))
            self.refuse_then_finalize(fixture, source, correct)

    def test_same_id_sidecar_must_align_floor_operands_and_members(self) -> None:
        for defect in ("operands", "members"):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixture = install_synthetic_finalization_fixture(
                    root / "custody", dominance_criterion={"rule_id": "test-dominance"}
                )
                correct = root / "correct.json"
                self.matching_sidecar(fixture, correct)
                floor = json.loads(fixture["floor_path"].read_bytes())
                foreign = copy.deepcopy(floor)
                if defect == "operands":
                    foreign["cells"][0]["absolute"]["corner_widened_unguarded_floor_j"] += 1.0
                else:
                    foreign["cells"][0]["comparative"]["blocks"][0]["members"][0]["bundle_id"] += "-foreign"
                sidecar = dominance_closeout.build_d165_replay_sidecar(
                    foreign, builder_recomputations(foreign, replay_sidecar(foreign))
                )
                self.assertEqual(dominance_closeout.validate_d165_replay_sidecar(sidecar), [])
                if defect == "members":
                    self.assertEqual(dominance_closeout._sidecar_floor_alignment_errors(floor, sidecar), [])
                    self.assertIsNotNone(dominance_closeout._floor_member_census_error(floor, sidecar))
                source = root / "foreign.json"
                source.write_text(json.dumps(sidecar))
                self.refuse_then_finalize(fixture, source, correct)

    def test_other_input_refusals_do_not_stage_sidecar(self) -> None:
        for defect, reason in (("prospective", "analysis_finalization_prospective_invalid"),
                               ("verdict", "analysis_finalization_verdict_not_passed"),
                               ("bracket", "analysis_finalization_bracket_binding_mismatch"),
                               ("output", "analysis_finalization_noncanonical")):
            with self.subTest(defect=defect), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixture = install_synthetic_finalization_fixture(
                    root / "custody", dominance_criterion={"rule_id": "test-dominance"}
                )
                source = root / "mint-replay.json"
                self.matching_sidecar(fixture, source)
                command = self.command(fixture) + ["--dominance-replay-sidecar", str(source)]
                if defect == "output":
                    command[command.index("--output-dir") + 1] = str(root)
                else:
                    path = fixture[f"{defect}_path"]
                    value = json.loads(path.read_bytes())
                    key = {"prospective": "freeze_status", "verdict": "status", "bracket": "plan_id"}[defect]
                    value[key] = "invalid"
                    path.write_text(json.dumps(value))
                before = self.custody_bytes(fixture)
                result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)["reason"], reason)
                self.assertEqual(self.custody_bytes(fixture), before)

    def test_occupied_staged_path_refuses_without_replacing_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "custody", dominance_criterion={"rule_id": "test-dominance"}
            )
            source = root / "mint-replay.json"
            _sidecar, raw = self.matching_sidecar(fixture, source)
            occupied = fixture["root"] / f"dominance-replay-{hashlib.sha256(raw).hexdigest()}.json"
            occupied.write_bytes(raw + b" ")
            before = self.custody_bytes(fixture)
            result = subprocess.run(self.command(fixture) + ["--dominance-replay-sidecar", str(source)],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["reason"], "analysis_finalization_output_conflict")
            self.assertEqual(self.custody_bytes(fixture), before)

    def test_occupied_staged_symlink_refuses_even_with_same_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "custody", dominance_criterion={"rule_id": "test-dominance"}
            )
            source = root / "mint-replay.json"
            _sidecar, raw = self.matching_sidecar(fixture, source)
            occupied = fixture["root"] / f"dominance-replay-{hashlib.sha256(raw).hexdigest()}.json"
            occupied.symlink_to(source)
            result = subprocess.run(self.command(fixture) + ["--dominance-replay-sidecar", str(source)],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["reason"], "analysis_finalization_output_conflict")
            self.assertTrue(occupied.is_symlink())
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(list(fixture["root"].glob("*.finalized.json")), [])

    def test_without_sidecar_preserves_existing_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture = install_synthetic_finalization_fixture(
                Path(tmp), dominance_criterion={"rule_id": "test-dominance"}
            )
            result = subprocess.run(self.command(fixture), cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["reason"], "analysis_finalization_attachment_missing")
            self.assertEqual(list(Path(tmp).glob("*.finalized.json")), [])

    def test_sidecar_symlink_refuses_without_staging(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture = install_synthetic_finalization_fixture(
                root / "custody", dominance_criterion={"rule_id": "test-dominance"}
            )
            target = root / "target.json"
            target.write_text(json.dumps({"schema_version": dominance_closeout.REPLAY_SCHEMA_VERSION,
                                          "sidecar_id": "valid-sidecar"}) + "\n")
            source = root / "link.json"
            source.symlink_to(target)
            result = subprocess.run(self.command(fixture) + ["--dominance-replay-sidecar", str(source)],
                                    cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(result.stdout)["status"], "REFUSE")
            self.assertEqual(list(fixture["root"].glob("*.finalized.json")), [])


if __name__ == "__main__":
    unittest.main()
