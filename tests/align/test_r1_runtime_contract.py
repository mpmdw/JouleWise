"""WP15 R1 runtime contract: field table and the host-side load journal."""
from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

from joulewise.align.apple import r1_runtime_contract as contract
from scripts import align_r1_rehearsal as r1

PS = ("    1     0   0.5 /sbin/launchd\n"
      "  100     1  40.0 /usr/bin/python3\n"       # measured runtime
      "  101   100  25.0 /usr/bin/python3\n"       # its child
      "  200     1  30.0 /usr/libexec/mds_stores\n"
      "  201     1   1.5 /usr/sbin/cfprefsd\n")


def ps(argv):
    return subprocess.CompletedProcess(argv, 0, PS, "")


class ContractTests(unittest.TestCase):
    def test_every_driver_kind_has_a_declared_contract(self):
        for name, kind, _, _ in r1.phase_plan(True):
            key = "idle_soak" if name == "idle_soak" else kind
            self.assertIn(key, contract.KIND_FIELDS, name)
        for kind in ("g0-release-soak", "harvest", *contract.HIGH_POWER_KINDS):
            self.assertIn(kind, contract.KIND_FIELDS)

    def test_driver_needs_are_declared(self):
        fields = {f for key in contract.KIND_FIELDS for f in contract.required_fields(key, quiet=True)}
        for name in ("cpu_busy_cores", "cpu_busy_t_s", "census", "sensor_series_c", "recovery_curve", "deadman.phases_s",
                     "admitted_turns", "x7", "energy_j", "e_D_j_per_token", "released", "t_decline_s",
                     "delta_slow_c", "g0_release_c", "reference_c", "slots",
                     "battery_drain_pct_per_h", "charge_resume_soc_pct"):
            self.assertIn(name, fields)
        self.assertIn("deadman.phases_s.tail", contract.required_fields("d-bank-benign-s1", quiet=False))

    def test_missing_fields_reports_nested_and_quiet_fields(self):
        result = {"energy_j": 1.0, "admitted_turns": 3, "x7": False, "battery_drain_pct_per_h": 3.0,
                  "reference_c": 38.0, "reference_source": "r1_soak_reference",
                  "gate_waits_s": {"G0": [1.0], "G1": [], "H": []}, "g0_outcome": "released",
                  "inter_member_idle_s": 300.0, "decode_tokens": 0, "g0_wait_s": 1.0, "g0_timeout_s": 1200,
                  "deadman": {"T_dead_s": 1.0, "phases_s": {p: 0.0 for p in contract.DEADMAN_PHASES[:-1]}}}
        self.assertEqual(contract.missing_fields("d-spam-benign-s1-a", result, quiet=False),
                         ["deadman.phases_s.tail"])
        self.assertEqual(contract.missing_fields("step-30b", {}, quiet=True),
                         ["cpu_busy_cores", "cpu_busy_t_s", "census", "battery_drain_pct_per_h",
                          "thermometry.status", "thermometry.classification_sha256", "g0_wait_s", "g0_timeout_s"])
        with self.assertRaisesRegex(ValueError, "no kind"):
            contract.required_fields("unknown", quiet=False)

    def test_soak_reference_kinds(self):
        self.assertIn("idle-until-soak", contract.NEEDS_SOAK_REFERENCE)
        self.assertIn("g0-release-soak", contract.NEEDS_SOAK_REFERENCE)
        # LEAD-RULINGS-2 R5-1: X-G and the gated D runs consume the soak R.
        for kind in ("x-g", *contract.GATED_D_KINDS):
            self.assertIn(kind, contract.NEEDS_SOAK_REFERENCE)
            self.assertIn("reference_source", contract.required_fields(kind, quiet=False))
        # R5-3: an A-B-A leg reports its own G0 outcome; R5-5: both steps classify.
        for kind in contract.HIGH_POWER_KINDS:
            self.assertIn("g0_released", contract.required_fields(kind, quiet=True))
        for kind in ("step-30b", "step-d"):
            self.assertIn("thermometry.classification_sha256", contract.required_fields(kind, quiet=True))
        self.assertIn("released", contract.required_fields("idle-until-soak", quiet=False))
        self.assertNotIn("calibration-pre", contract.NEEDS_SOAK_REFERENCE)


class Round6ContractTests(unittest.TestCase):
    def test_gated_runs_and_x_g_report_w1_s_schedule_g0_and_decode_tokens(self):
        # R6-1: the schedule and the G0 outcome; R6-3: the decode tokens.
        for kind in (*contract.GATED_D_KINDS, "x-g"):
            fields = contract.required_fields(kind, quiet=False)
            self.assertIn("inter_member_idle_s", fields)
            self.assertIn("g0_outcome", fields)
        for kind in contract.GATED_D_KINDS:
            self.assertIn("decode_tokens", contract.required_fields(kind, quiet=False))

    def test_an_inconclusive_step_d_or_designed_state_needs_only_its_g0_and_the_quiet_fields(self):
        # R6-2: a G0 timeout there is INCONCLUSIVE, not a contract failure.
        quiet = {"cpu_busy_cores": [0.1], "cpu_busy_t_s": [0.0], "census": [{}]}
        result = {**quiet, "segment_status": "inconclusive", "g0_released": False, "g0_outcome": "timeout",
                  "g0_wait_s": 1200.0, "g0_timeout_s": 1200}   # R7-2
        for kind in ("step-30b", "step-d", *contract.PLANNING_KINDS):
            self.assertEqual(contract.missing_fields(kind, result, quiet=True), [], kind)
            # Without segment_status the measured fields are required.
            self.assertIn({"step-d": "slots", "step-30b": "thermometry.status"}.get(kind, "energy_j"),
                          contract.missing_fields(kind, quiet, quiet=True))
        # a85ee8ec6 implements RL-72 E3: step-30b may time out flagged,
        # or report an inconclusive member when no turn was observed.
        self.assertEqual(contract.missing_fields("step-30b", result, quiet=True), [])
        self.assertIn("energy_j", contract.missing_fields("d-bank-benign-s1", result, quiet=False))


class LoadJournalTests(unittest.TestCase):
    def test_busy_cores_excludes_the_measured_process_tree(self):
        rows = contract.process_table(ps)
        self.assertEqual(len(rows), 5)
        self.assertAlmostEqual(contract.busy_cores(rows), 0.97)
        self.assertAlmostEqual(contract.busy_cores(rows, exclude_roots=(100,)), 0.32)

    def test_journal_fields_feed_the_driver_verdict(self):
        journal = contract.LoadJournal((100,), runner=ps, clock=lambda: 7.0)
        journal.snapshot("start")
        for _ in range(61):
            journal.sample()
        journal.snapshot("end")
        fields = journal.fields()
        self.assertEqual(len(fields["cpu_busy_cores"]), 61)
        self.assertEqual(len(fields["cpu_busy_t_s"]), 61)
        self.assertEqual([c["label"] for c in fields["census"]], ["start", "end"])
        self.assertFalse(r1.os_load_verdict("seg", fields)["redo"])  # 0.32 cores < 0.5
        busy = contract.LoadJournal((), runner=ps)
        for _ in range(60):
            busy.sample()
        busy.snapshot("end")
        self.assertTrue(r1.os_load_verdict("seg", busy.fields())["redo"])  # 0.97 cores for 60 s

    def test_ps_failure_is_refused(self):
        with self.assertRaisesRegex(ValueError, "ps failed"):
            contract.process_table(lambda argv: subprocess.CompletedProcess(argv, 1, "", ""))

    def test_contract_doc_lists_every_kind(self):
        doc = (Path(__file__).resolve().parents[2] / "docs/align/r1_runtime_contract.md").read_text()
        for kind in contract.KIND_FIELDS:
            self.assertIn(f"`{kind}`", doc)
        for field in contract.QUIET_FIELDS:
            self.assertIn(f"`{field}`", doc)
        self.assertIn("--soak-reference", doc)
        for field in ("`battery_drain_pct_per_h`", "`charge_resume_soc_pct`", "runtime_custody.json",
                      "`inter_member_idle_s`", "`decode_tokens`", "`segment_status`", "`calibration_precool_cap_s`",
                      "`r_decode_step_d_tok_per_s`", "`inputs.R1.thermal_policy.classification_sha256`"):
            self.assertIn(field, doc)

    def test_ruling_4b_battery_fields_are_required_where_the_driver_reads_them(self):
        for kind in ("step-30b", "step-d", *contract.GATED_D_KINDS):
            self.assertIn("battery_drain_pct_per_h", contract.required_fields(kind, quiet=True))
        self.assertIn("charge_resume_soc_pct", contract.required_fields("harvest", quiet=False))


if __name__ == "__main__":
    unittest.main()
