"""Census of ordinary routes to calibration claim authority."""

from __future__ import annotations

import ast
from pathlib import Path
import re
import unittest

from joulewise import arm_readiness as arm
from joulewise import calibration_bracketing as bracket
from joulewise.claim_hold import CLAIM_HELD_OS_BUILDS

ROOT = Path(__file__).resolve().parents[1]

# Every file is paired with the reason it can reach a calibration file.
CALIBRATION_READERS = {
    "joulewise/analysis_engine/claims.py": "claim calibration projection",
    "joulewise/analysis_engine/inputs.py": "analysis calibration input",
    "joulewise/arm_readiness.py": "pack calibration admission",
    "joulewise/arm_readiness_evidence_t0.py": "T0 evidence calibration reference",
    "joulewise/battery_float.py": "battery calibration provenance",
    "joulewise/calibration_bracketing.py": "issued calibration loader and evaluator",
    "joulewise/calibration_dispositions.py": "disposition registry calibration path",
    "joulewise/floor_mint_estimator.py": "floor calibration input",
    "joulewise/whole_window.py": "whole-window calibration evaluation",
    "scripts/calibration_cadence_report.py": "calibration cadence report",
    "scripts/calibration_ledger_bootstrap.py": "calibration ledger bootstrap",
    "scripts/epoch_equivalence_check.py": "epoch equivalence calibration reference",
    "scripts/gen_derivation_night.py": "derivation-night calibration path",
    "scripts/generate_g2a_probe_inputs.py": "probe calibration reference",
    "scripts/issue_calibration_acceptance_generation.py": "calibration issuance",
    "scripts/issue_epoch_continuation.py": "continuation issuance",
    "scripts/mint_floor_artifact.py": "floor artifact calibration",
    "scripts/mint_floor_artifact_generalized.py": "generalized floor calibration",
    "scripts/promote_calibration_candidate.py": "candidate promotion",
    "scripts/reissue_calibration_acceptance.py": "calibration reissue",
    "scripts/run_campaign.py": "campaign calibration route",
    "scripts/sim_acc_25g83_rev5.py": "calibration simulation",
    "scripts/validate_powermetrics_fiducial.py": "capture calibration preflight",
    "scripts/write_derivation_night_inputs.py": "derivation-night inputs",
}


def production_sources():
    for directory in (ROOT / "joulewise", ROOT / "scripts"):
        for path in directory.rglob("*.py"):
            yield path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8")


def files_with(pattern: str) -> set[str]:
    matcher = re.compile(pattern)
    return {name for name, source in production_sources() if matcher.search(source)}


class ClaimHoldCensusTests(unittest.TestCase):
    def test_c1_unchecked_authenticator_stays_local(self):
        self.assertEqual(files_with(r"_authenticate_acceptance_bytes"),
                         {"joulewise/calibration_bracketing.py"})

    def test_c2_inspection_and_unchecked_operatives_stay_local(self):
        self.assertEqual(files_with(r"inspect_acceptance_without_claim_authority|_registered_operatives_unchecked"),
                         {"joulewise/calibration_bracketing.py"})

    def test_c3_hold_table_has_one_owner(self):
        self.assertEqual(files_with(r"CLAIM_HELD_OS_BUILDS"), {"joulewise/claim_hold.py"})

    def test_c4_old_escape_vocabulary_absent(self):
        self.assertEqual(files_with(r"allow_claim_held|CLAIM_HELD_ACCEPTANCE_IDS"), set())

    def test_c5_calibration_readers_are_reviewed(self):
        found = files_with(r"configs/calibration|_CALIBRATION_CONFIG_DIR|calibration_acceptance_|\b[A-Za-z_]\w*_ACCEPTANCE_BOUND_PATH\b")
        self.assertEqual(found, set(CALIBRATION_READERS))
        self.assertTrue(all(CALIBRATION_READERS.values()))

    def test_c6_only_pass_site_has_top_level_build_guard(self):
        tree = ast.parse((ROOT / "joulewise/calibration_bracketing.py").read_text())
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name == "evaluate_calibration_bracket"]
        self.assertEqual(len(functions), 1)
        function = functions[0]
        passed_sites = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                value = node.value
                if isinstance(value, ast.Constant) and value.value == "passed":
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    if any(isinstance(target, ast.Subscript) and isinstance(target.value, ast.Name)
                           and target.value.id == "result" and isinstance(target.slice, ast.Constant)
                           and target.slice.value == "status" for target in targets):
                        passed_sites.append(node)
        self.assertEqual(len(passed_sites), 1)
        self.assertIn(passed_sites[0], list(ast.walk(function)))
        guards = [node for node in function.body if isinstance(node, ast.If)
                  and any(isinstance(call, ast.Call) and isinstance(call.func, ast.Name)
                          and call.func.id == "claim_hold_for_os_build" for call in ast.walk(node.test))
                  and any(isinstance(child, ast.Return) for child in ast.walk(ast.Module(body=node.body, type_ignores=[])))]
        self.assertEqual(len(guards), 1)
        self.assertLess(guards[0].lineno, passed_sites[0].lineno)

    def test_c7_registered_builds_and_held_routes(self):
        self.assertEqual(set(bracket.ISSUED_ACCEPTANCE_REGISTRY),
                         set(bracket.REGISTERED_GENERATION_OS_BUILD))
        for acceptance_id, row in bracket.ISSUED_ACCEPTANCE_REGISTRY.items():
            with self.subTest(acceptance_id=acceptance_id):
                raw = row["path"].read_bytes()
                inspection = bracket.inspect_acceptance_without_claim_authority(row["path"])
                self.assertIsNotNone(inspection)
                self.assertEqual(bracket.REGISTERED_GENERATION_OS_BUILD[acceptance_id],
                                 inspection.artifact["identity_epoch"]["os_build"])
                if inspection.artifact["identity_epoch"]["os_build"] in CLAIM_HELD_OS_BUILDS:
                    self.assertIsNone(bracket.load_calibration_acceptance_bound(row["path"]))
                    self.assertIsNone(bracket._acceptance_bound_from_authenticated_bytes(raw))
                    self.assertIsNone(bracket.acceptance_generation_operatives(acceptance_id))
                    self.assertFalse(arm._issued_d079({"acceptance_policy": {
                        "selection": "issued_d116_artifact_only", "issued": acceptance_id}}))
        for row in bracket.EPOCH_CONTINUATION_REGISTRY.values():
            self.assertNotIn(row["continued_identity_epoch"]["os_build"], CLAIM_HELD_OS_BUILDS)


    def test_c8_every_admitted_identifier_is_registered(self):
        # HOLD-BY-CONSTRUCTION-01-A1 §4.4: an identifier the admission list admits must name a
        # registered calibration file. Planting a build for the bare "d079" must turn this RED.
        def admitted():
            return [
                identifier for identifier in sorted(arm._ISSUED_D079_IDS)
                if arm._issued_d079({"acceptance_policy": {
                    "selection": "issued_d116_artifact_only", "issued": identifier}})
            ]
        self.assertTrue(admitted())
        self.assertEqual(
            [i for i in admitted() if i not in bracket.ISSUED_ACCEPTANCE_REGISTRY], [])

if __name__ == "__main__":
    unittest.main()
