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

# The finalizer binds the calibration ledger baseline to the issued acceptance
# cutoff. The synthetic fixture's ledger starts at genesis, so its consumers
# read the fixture's genesis acceptance (fixture["acceptance_path"]) instead of
# the production artifact, as every other finalize test does in process
# (tests.test_analysis_integration.pinned_genesis_acceptance). This child runs
# the real CLI main() under that same routing; argv[1] is the acceptance path
# and the CLI arguments follow it unchanged.
_ACCEPTANCE_ROUTED_CLI = """
import sys
from pathlib import Path
from tests.test_analysis_integration import pinned_genesis_acceptance
from scripts.finalize_analysis_manifest import main
with pinned_genesis_acceptance({"acceptance_path": Path(sys.argv[1])}):
    code = main(sys.argv[2:])
raise SystemExit(code)
"""


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
            sys.executable, "-B", "-c", _ACCEPTANCE_ROUTED_CLI, str(fixture["acceptance_path"]),
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


class Block5FinalizerContinuationTests(unittest.TestCase):
    def argv(self, fixture, *, sidecar=False, indexed=False):
        values = [('prospective-manifest', fixture['prospective_path']), ('plan-tree', fixture['plan_tree_path']),
                  ('custody-root', fixture['root']), ('runs-root', fixture['runs_root']),
                  ('whole-window-verdict', fixture['verdict_path']), ('bracket-binding', fixture['bracket_path']),
                  ('calibration-ledger', fixture['ledger_path']), ('aggregate-floor-artifact', fixture['floor_path']),
                  ('output-dir', fixture['root'])]
        if sidecar: values.append(('dominance-replay-sidecar', fixture['acceptance_path']))
        if indexed: values.append(('window-index', fixture['root'] / 'window-index.json'))
        return [word for name, path in values for word in ('--' + name, str(path))]

    def test_programming_value_error_is_not_printed_as_refusal(self):
        from unittest import mock
        from scripts import finalize_analysis_manifest as script
        from tests.b5_analysis import fixtures_s5 as fx
        with fx.finalization_case() as f, \
             mock.patch.object(script, 'finalize_prospective_analysis_manifest_v3', side_effect=ValueError('programming defect')):
            with self.assertRaisesRegex(ValueError, '^programming defect$'):
                script.main(self.argv(f))

    def test_named_analysis_refusals_are_printed(self):
        import contextlib
        import io
        from unittest import mock
        from scripts import finalize_analysis_manifest as script
        from tests.b5_analysis import fixtures_s5 as fx
        errors = [script.AnalysisManifestFinalizationError('analysis_finalization_attachment_invalid', 'synthetic'),
                  script.AnalysisRefusal('window_index_invalid'), script.AnalysisInputError('kept_quads_required')]
        with fx.finalization_case() as f:
            for error in errors:
                with self.subTest(error=type(error).__name__):
                    output = io.StringIO()
                    with mock.patch.object(script, 'finalize_prospective_analysis_manifest_v3', side_effect=error), \
                         contextlib.redirect_stdout(output):
                        self.assertEqual(script.main(self.argv(f)), 2)
                    self.assertEqual(json.loads(output.getvalue())['status'], 'REFUSE')

    def test_script_builds_once_for_real_preflight_and_final_handoff(self):
        import contextlib
        import io
        from unittest import mock
        from scripts import finalize_analysis_manifest as script
        from tests.b5_analysis import fixtures_s5 as fx
        with fx.finalization_case() as f:
            manifest = {'manifest_id': 's5', 'lineage': {'prospective_manifest_id': f['prospective']['manifest_id']}}
            missing = script.AnalysisManifestFinalizationError('analysis_finalization_attachment_missing',
                'dominance-enabled prospective manifest requires a dominance replay sidecar')
            with mock.patch.object(script, 'block5_claim_gate_inputs', return_value=f['block5_inputs']) as builder, \
                 mock.patch.object(script, '_dominance_floor_identity_enabled', return_value=True), \
                 mock.patch.object(script, 'stage_dominance_replay_sidecar', return_value=f['acceptance_path']), \
                 mock.patch.object(script, 'finalize_prospective_analysis_manifest_v3', side_effect=[missing, manifest]) as finalize, \
                 contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(script.main(self.argv(f, sidecar=True, indexed=True)), 0)
            builder.assert_called_once()
            self.assertEqual(finalize.call_count, 2)
            for call in finalize.call_args_list:
                self.assertIs(call.kwargs['_block5_inputs'], f['block5_inputs'])

    def test_library_reuses_authenticated_block5_inputs(self):
        from unittest import mock
        from joulewise import analysis_manifest_v3 as mv3
        from joulewise.analysis_engine import inputs
        from tests.b5_analysis import fixtures_s5 as fx
        with fx.finalization_case() as f, \
             mock.patch.object(inputs, 'block5_claim_gate_inputs') as builder, \
             mock.patch.object(mv3, '_authenticate_finalization_inputs', return_value={}) as authenticate, \
             mock.patch.object(mv3, '_build_finalized_manifest', return_value={'manifest_id': 's5'}), \
             mock.patch.object(mv3, 'validate_finalized_analysis_manifest_v3', return_value=()), \
             mock.patch.object(mv3, '_write_append_only'):
            mv3.finalize_prospective_analysis_manifest_v3(f['prospective_path'], plan_tree_path=f['plan_tree_path'],
                custody_root=f['root'], runs_root=f['runs_root'], whole_window_verdict_path=f['verdict_path'],
                bracket_binding_path=f['bracket_path'], calibration_ledger_path=f['ledger_path'],
                aggregate_floor_artifact_path=f['floor_path'], output_dir=f['root'],
                window_index=f['root'] / 'unopened-index.json', _block5_inputs=f['block5_inputs'])
            builder.assert_not_called()
            self.assertIs(authenticate.call_args.kwargs['block5_inputs'], f['block5_inputs'])
