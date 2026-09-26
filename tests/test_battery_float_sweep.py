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
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
B_LEXEME = re.compile(r"b_fiducial_s|exact_bound_lexeme_s")

# file -> (classification, gate).  "UNGATED" rows are reported NEEDS_SCOPE.
READERS = {
    "scripts/issue_calibration_acceptance_generation.py": (
        "gated", "check dry run and _dry_run_epoch_bound; prepare-candidate battery block"),
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
        "UNGATED", "operator-named instrument calibration attachment; NEEDS_SCOPE"),
    "scripts/run_campaign.py": ("run metadata", "reads the run's own controller attachment"),
    "scripts/calibration_ledger_backfill.py": (
        "UNGATED", "writes evidence b_fiducial_s into candidate rows for any root; NEEDS_SCOPE"),
    "scripts/paper_anchor_correction_quantified.py": (
        "UNGATED", "population = every capture under <corpus-root>/runs/instrument_validation; NEEDS_SCOPE"),
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


if __name__ == "__main__":
    unittest.main()
