"""The R2-5 same-signature sweep of cold ruling BFG-D-PARSER-ESC-01 §6, as a guard.

A-R5b's obligation is on outputs and decisions: no B lexeme of a Revision-5
derivation session may be printed, written, compared or used in a decision
before an authentic committed battery-float verdict is loaded, and never for a
non-pass window.  Every production module that names a B lexeme
(`b_fiducial_s` or `exact_bound_lexeme_s`) is classified below with the gate it
sits behind; the seat report (19) carries the file:line table and the test
that proves each gate.  A new reader fails this test until it is classified,
so the sweep cannot silently go stale (refuter N-2).

Every production caller of `battery_float.observe` is likewise listed with
the runner that feeds it, which must hand the grammar the probe's exact stdout
bytes (obligation R2-11).
"""

from __future__ import annotations

from pathlib import Path
import ast
import re
import unittest

from joulewise import battery_float

ROOT = Path(__file__).resolve().parents[1]
B_LEXEME = re.compile(r"b_fiducial_s|exact_bound_lexeme_s")

# file -> (classification, gate, and for a refusal the test that proves it).
READERS = {
    "scripts/issue_calibration_acceptance_generation.py": (
        "gated", "check dry run and prepare-candidate, both through authenticate_battery_epoch "
        "(authenticate_committed_verdict); proved by test_battery_float_consumers and the "
        "BatteryFloatRevisionFiveTests parity matrix"),
    "scripts/epoch_equivalence_check.py": ("refuses Revision 5", "evaluate_session (R2-2)"),
    "scripts/issue_epoch_continuation.py": ("refuses Revision 5", "derive_record (R2-10)"),
    "joulewise/calibration_epoch_continuation.py": (
        "transitively gated", "records come only from issue_epoch_continuation plus a registry pin"),
    "scripts/reissue_calibration_acceptance.py": (
        "transitively gated", "members of an authenticated issued acceptance"),
    "scripts/validate_powermetrics_fiducial.py": (
        "writer; re-derivation gated", "--rederive-from accepts only v1/v2 40-pulse evidence"),
    "joulewise/calibration_ledger.py": ("writer", "finalization extracts the lexeme; prints none"),
    "joulewise/powermetrics_fiducial.py": ("writer (pinned)", "computes a capture's own bound"),
    "joulewise/calibration_bracketing.py": (
        "issued acceptance and bracket rows (pinned)", "outside the derivation scope"),
    "joulewise/reduce.py": ("issued acceptance (pinned)", "measurement reduction"),
    "joulewise/whole_window.py": ("issued acceptance and bracket rows", "outside the derivation scope"),
    "joulewise/detection_floor.py": ("bracket rows", "outside the derivation scope"),
    "scripts/mint_floor_artifact_generalized.py": ("bracket rows", "outside the derivation scope"),
    "joulewise/controller.py": (
        "refuses Revision 5", "instrument calibration attachment raises 'revision_five evidence cannot be "
        "attached as instrument calibration'; test_revision_five_b_readers."
        "test_controller_attachment_refuses_before_physics_or_bound"),
    "scripts/run_campaign.py": ("run metadata", "reads the run's own controller attachment"),
    "scripts/calibration_ledger_backfill.py": (
        "refuses Revision 5", "raises '<dir>: revision_five evidence is not a backfill candidate'; "
        "test_revision_five_b_readers.test_backfill_refuses_revision_five_before_bound"),
    "scripts/paper_anchor_correction_quantified.py": (
        "historical", "pinned by sha in docs/paper/results-fill-registry.md; reads only "
        "retained historical corpora in docs/paper/round7/anchor-correction-quantified.md; "
        "Revision-5 roots are outside its inputs "
        "(docs/process_traces/2026-09-25-activation-ed17a643/bfg-d/26-fix-contract-r7b.md H-4)"),
    "scripts/paper_excursion_decomposition.py": ("historical", "pinned member 20260722T145535-e941c821"),
    "scripts/check_paper_replay_fence.py": ("historical", "pinned member 20260722T145535-e941c821"),
    "scripts/check_paper_round7_artifacts.py": ("historical", "committed paper artifacts only"),
    "scripts/sim_acc_25g83_rev5.py": ("synthetic", "opens no file"),
    "joulewise/receipt_oracle.py": ("synthetic", "constant lexeme in a fixture receipt"),
    "joulewise/arm_readiness.py": ("synthetic", "constant lexeme in a rehearsal lifecycle"),
}

# file -> the runner each `battery_float.observe(` call there uses.
OBSERVE_CALLERS = {
    "joulewise/night_gate.py": ["t0: probes.run (run_night._probe_runner captures bytes)"],
    "joulewise/evidence_night.py": ["arm_check: probe_command (bytes for the ioreg argv)",
                                    "publish_install: probe_command (bytes for the ioreg argv)"],
    "joulewise/night_agent_install.py": ["validate_install: observe's own bytes subprocess.run"],
    "joulewise/arm_readiness_evidence_t0.py": ["t0_power_row: _execute_probe stdout_bytes"],
    "scripts/validate_powermetrics_fiducial.py": ["slot_pre/slot_post: observe's own bytes subprocess.run"],
}


def _production_sources():
    for directory in ("joulewise", "scripts"):
        for path in sorted((ROOT / directory).rglob("*.py")):
            yield path.relative_to(ROOT).as_posix(), path.read_text(encoding="utf-8", errors="replace")


class SweepGuardTests(unittest.TestCase):
    def test_every_production_observe_phase_is_registered(self):
        seen = set()
        for name, source in _production_sources():
            tree = ast.parse(source, filename=name)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                    continue
                if node.func.attr != "observe" or not isinstance(node.func.value, ast.Name):
                    continue
                if node.func.value.id not in ("battery_float", "_battery_float"):
                    continue
                [phase] = [kw.value for kw in node.keywords if kw.arg == "phase"]
                if isinstance(phase, ast.Constant) and isinstance(phase.value, str):
                    self.assertIn(phase.value, battery_float.PHASES, (name, node.lineno))
                    seen.add(phase.value)
                else:
                    # The existing slot writer formats only its pre/post loop.
                    self.assertEqual(name, "scripts/validate_powermetrics_fiducial.py")
                    self.assertIsInstance(phase, ast.JoinedStr)
                    self.assertEqual(ast.unparse(phase), "f'slot_{phase}'")
                    self.assertTrue({"slot_pre", "slot_post"} <= set(battery_float.PHASES))
                    seen.update(("slot_pre", "slot_post"))
        self.assertEqual(seen, set(battery_float.PHASES[:7]))

    def test_every_b_lexeme_reader_is_classified(self):
        readers = {name for name, text in _production_sources() if B_LEXEME.search(text)}
        self.assertEqual(readers, set(READERS))

    def test_every_battery_observe_caller_is_listed_with_a_bytes_runner(self):
        calls = {}
        for name, text in _production_sources():
            count = len(re.findall(r"battery_float\.observe\(", text))
            if count and name != "joulewise/battery_float.py":
                calls[name] = count
        self.assertEqual(calls, {name: len(runners) for name, runners in OBSERVE_CALLERS.items()})


    def test_no_reader_is_ungated_and_each_refusal_names_its_proof(self):
        for name, (classification, gate) in READERS.items():
            with self.subTest(reader=name):
                self.assertNotIn("UNGATED", classification)
                self.assertNotIn("NEEDS_SCOPE", gate)
                if classification == "refuses Revision 5" and name not in (
                        "scripts/epoch_equivalence_check.py", "scripts/issue_epoch_continuation.py"):
                    test_name = gate.rsplit(".", 1)[1]
                    source = (ROOT / "tests/test_revision_five_b_readers.py").read_text(encoding="utf-8")
                    self.assertIn(f"def {test_name}(", source)


if __name__ == "__main__":
    unittest.main()
