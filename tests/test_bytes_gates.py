"""C5 execution on native non-claim exports shaped like every Mac-kit member."""
from copy import deepcopy
import csv
from decimal import Decimal
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.b6 import export_runs
from joulewise.b6.acceptance_interface import MemberEvidence, StageEvidence, SessionEvidence
from scripts import bytes_gates as gates

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


def synthetic_harvest(root):
    """Actual exporter, immutable synthetic bundles, all 98+25 kit runs."""
    plan = gates.read(gates.KIT)
    members = {m["run_id"]: m for m in plan["members"]}
    tree = gates.read(ROOT / "configs/campaigns/bytes_mac_check/plan_tree.json")
    archive = root / "archive"
    measured = {"schema_version": "joulewise.bytes_mac_measurements.v1", "non_claim": True,
                "session_id": "synthetic-mac-check", "runs": {}, "regimes": {},
                "clock": {"rate_ppm": 1, "frequency_word_ppm": 1},
                "disk": {"fixed_retained_bytes": 1024**2, "pre_arm_free_bytes": 400 * 1024**3},
                "sizing": {"fixed_desk_s": 600, "collection_stage_overhead_s": 10},
                "cpu_contention": {"w_j_per_cpu_s": "5.432", "c_q_cpu_s": ".54"}}
    stages, roster, order = [], [], 0
    for stage in tree["stage_graph"]:
        if stage["kind"] != "campaign_collection":
            continue
        manifest = gates.read(ROOT / stage["input"]["path"])
        evidence = []
        for row in manifest["executed_order"]:
            rid = row["run_id"]
            cfg = gates.read((ROOT / stage["input"]["path"]).parent / row["config"])
            # Source configs contain no decimal fractions; leave actual config
            # identity untouched while producing synthetic event/energy bytes.
            cfg = json.loads(json.dumps(cfg, default=float))
            bundle = archive / "sources/claim-runs" / rid
            write(bundle / "config.json", cfg)
            member = members.get(rid, {"model_id": "reference", "purpose": "reference", "end": "middle"})
            mid = member["model_id"]
            long = mid in plan["long_regimes"]
            # Synthetic long phases deliberately put the R6 milliwatt line
            # below the stated census resolution, exercising flag-only logic.
            duration = 200 if long else 20
            # P6 must see the twelve-run soak's larger spread, not just checks.
            rep = row["index"]
            request = duration + 10 + rep * (10 if member["purpose"] == "soak" else 1)
            start = 1000 + order * 400
            (bundle / "events.jsonl").write_text("".join(json.dumps(e) + "\n" for e in (
                {"event_type": "phase_start", "phase": "decode", "timestamp_s": start},
                {"event_type": "phase_end", "phase": "decode", "timestamp_s": start + duration})))
            write(archive / "withheld/reductions" / (rid + ".summary_metrics.rereduced.json"),
                  {"phase_energy_j": {"decode": duration * 20}})
            measured["runs"][rid] = {"request_s": request, "member_wall_s": request + 80,
                                      "stream_s": request + 60, "retained_bytes": 1024**2,
                                      "thermal_level": 0, "outside_cpu_s": "1.08", "census_quanta": 2}
            if mid != "reference":
                measured["regimes"][mid] = {"F_min_j": 4, "census_resolution_w": .01,
                    "outside_power_w": .001, "operative_bound_s": .04,
                    "registered_T10_s": None, "registered_T_phase_s": None}
            role = "science" if rid in members else "corpus" if "bound-collection" in stage["stage_id"] else "start"
            evidence.append(MemberEvidence(stage["stage_id"], rid, "succeeded", role=role))
            roster.append({"run_id": rid, "stage_id": stage["stage_id"], "role": role, "status": "succeeded"})
            order += 1
        stages.append(StageEvidence(stage["stage_id"], stage["kind"], len(evidence), tuple(evidence)))
    write(archive / "derived/roster.json", {"pack_id": "bytes-mac-check", "members": roster})
    session = measured["session_id"]
    evidence = SessionEvidence("bytes-mac-check", tuple(stages), (), {}, True, (), session_id=session)
    result = export_runs.export(archive, {}, root / "registration", root / "private", root / "export",
        non_claim=True, evidence=evidence, acceptance_record={"pack_id": "bytes-mac-check", "session_id": session,
                                                           "counting": False, "verdict": "NON_CLAIM"})
    write(root / "measurements.json", measured)
    return result, measured


class World(unittest.TestCase):
    """The synthetic native harvest shared by the C5 test classes."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.tmp.name)
        cls.export, cls.measured = synthetic_harvest(cls.root)
        with cls.export.csv_path.open() as stream:
            cls.rows = list(csv.DictReader(stream))
        cls.sidecar = gates.read(cls.export.sidecar_path)
        cls.plan = gates.read(gates.KIT)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def result(self, measured=None, rows=None, sidecar=None):
        return gates.calculate(deepcopy(self.rows if rows is None else rows),
            deepcopy(self.sidecar if sidecar is None else sidecar),
            deepcopy(self.measured if measured is None else measured), deepcopy(self.plan))

    def close(self, actual, expected):
        # Brief: a quantity with no printed half-width uses 1e-6 relative
        # or absolute in its column unit; far above 1e6*float noise.
        self.assertTrue(math.isclose(float(actual), float(expected), rel_tol=1e-6, abs_tol=1e-6), (actual, expected))


class GatesTests(World):
    def test_cli_runs_every_gate_from_native_nonclaim_harvest(self):
        out = self.root / "c5.json"
        result = subprocess.run([sys.executable, str(ROOT / "scripts/bytes_gates.py"),
            "--runs", str(self.export.csv_path), "--measurements", str(self.root / "measurements.json"),
            "--out", str(out)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = gates.read(out)
        self.assertFalse(report["registration_ready"])
        self.assertTrue(report["non_claim"])
        # Native scaffold adds 18 corpus + 3 start + 1 midpoint + 3 end
        # to the brief's 98 structural members: integer membership is exact.
        self.assertEqual(self.export.row_count, 123)
        self.assertEqual(len(report["models"]), 10)
        self.assertEqual(len(report["sessions"]), 12)
        self.assertEqual(len(report["inputs"]), 4)
        self.assertEqual(len(result.stdout.splitlines()), len(report["gates"]))
        lines = {r["gate"]: r for r in report["gates"]}
        for model in self.measured["regimes"]:
            contention = lines["contention:" + model]
            self.close(contention["P_limit_w"], 4 / (4 * (200 if model in self.plan["long_regimes"] else 20)))
            self.assertEqual(contention["status"], "flag_only")
            self.assertEqual(contention["reason"], "registered_T_phase_absent")
            self.assertEqual(lines["calibration_T10:" + model]["status"], "flag_only")
        # No MLX/hardware or key material is read by the C5 desk path.
        self.assertFalse((self.root / "private").exists())

    def test_spread_and_sizing_use_measured_soak_times_without_fixed_margin(self):
        result = self.result()
        expected = Decimal(0)
        for model in result["models"]:
            for purpose in ("check", "soak"):
                times = [Decimal(self.measured["runs"][m["run_id"]]["request_s"])
                         for m in self.plan["members"] if m["model_id"] == model and m["purpose"] == purpose]
                if times:
                    expected = max(expected, max(times) / min(times) - 1)
        self.close(result["measured_margin"], expected)
        self.assertEqual(max(result["spread_groups"], key=lambda x: x["spread"])["purpose"], "soak")
        for model, sized in result["models"].items():
            self.close(sized["est_minutes"], 50 * sized["member_wall_mean_s"] * (1 + expected) / 60)
        for n in range(1, 7):
            self.assertEqual(result["sessions"][f"bytes-s{n}-p1"]["modules"], result["sessions"][f"bytes-s{n}-p2"]["modules"])
        mutated = deepcopy(self.measured)
        for r in mutated["runs"].values():
            r["request_s"] *= 2
            r["member_wall_s"] *= 2
            r["stream_s"] *= 2
        doubled = self.result(mutated)
        self.close(doubled["models"]["llama-70b"]["est_minutes"], 2 * result["models"]["llama-70b"]["est_minutes"])

    def test_registered_gates_flag_unsized_and_fail_only_at_derived_physical_lines(self):
        measured = deepcopy(self.measured)
        for regime in measured["regimes"].values():
            regime.update(registered_T_phase_s=200, registered_T10_s=.05)
        first = self.result(measured)
        lines = {r["gate"]: r for r in first["gates"]}
        # 4 J/(4*200 s) = 5 mW, below the 10 mW synthetic census.
        self.assertEqual(lines["contention:llama-70b"]["reason"], "below_census_resolution")
        for regime in measured["regimes"].values():
            regime.update(census_resolution_w=.001, outside_power_w=.005, operative_bound_s=.06)
        second = {r["gate"]: r for r in self.result(measured)["gates"]}
        # Registered exclusion is >= quarter-floor; equal energy is a fail.
        self.assertEqual(second["contention:llama-70b"]["status"], "fail")
        self.assertEqual(second["calibration_T10:llama-70b"]["status"], "fail")
        measured["clock"]["rate_ppm"] = 30
        self.assertEqual({r["gate"]: r for r in self.result(measured)["gates"]}["clock:session"]["status"], "fail")
        # The registered hold uses r; a divergent word stays diagnostic.
        measured["clock"].update(rate_ppm=1, frequency_word_ppm=30)
        divergent = {r["gate"]: r for r in self.result(measured)["gates"]}["clock:session"]
        self.assertEqual(divergent["status"], "pass")
        self.assertFalse(divergent["frequency_word_clears_gate"])
        # Exactly the registered 5 ms boundary clears; a longer stream fails.
        clock = {"rate_ppm": "24.75", "frequency_word_ppm": "24.75"}
        self.assertEqual(gates.clock_line("x", Decimal(200), clock)["status"], "pass")
        self.assertEqual(gates.clock_line("x", Decimal(201), clock)["status"], "fail")

    def test_disk_reserve_and_thermal_counterexamples_reach_fail_lines(self):
        measured = deepcopy(self.measured)
        result = self.result(measured)
        disk = next(g for g in result["gates"] if g["gate"] == "disk:kit")
        measured["disk"]["pre_arm_free_bytes"] = disk["required_free_bytes"]
        self.assertEqual(next(g for g in self.result(measured)["gates"] if g["gate"] == "disk:kit")["status"], "pass")
        measured["disk"]["pre_arm_free_bytes"] -= 1  # One integer byte below operational reserve.
        measured["runs"][next(iter(measured["runs"]))]["thermal_level"] = 1  # Catalog excludes OS level > 0.
        lines = {g["gate"]: g for g in self.result(measured)["gates"]}
        self.assertEqual(lines["disk:kit"]["status"], "fail")
        self.assertEqual(lines["thermal"]["status"], "fail")

    def test_cpu_contention_uses_registered_quanta_subtraction_and_flags_alternative(self):
        measured = deepcopy(self.measured)
        rid = next(m["run_id"] for m in self.plan["members"] if m["model_id"] == "llama-70b")
        # Registration S-8: exactly two quanta of quiet background is removed;
        # one extra CPU-second costs w, above the synthetic quarter-floor 1 J.
        measured["runs"][rid]["outside_cpu_s"] = "2.08"
        result = self.result(measured)
        row = next(r for r in result["cpu_contention_alternative"] if r["run_id"] == rid)
        self.close(row["added_energy_j"], 5.432)
        self.assertTrue(row["would_exclude"])
        self.assertEqual(next(r for r in result["gates"] if r["gate"] == "cpu_contention:llama-70b")["status"], "flag_only")

    def test_cli_failed_gates_are_written_and_missing_receipts_are_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            measured = deepcopy(self.measured)
            measured["clock"]["rate_ppm"] = 30  # Above 5000/max(run stamp span)-0.25 in this world.
            write(root / "measurements.json", measured)
            out = root / "c5.json"
            args = [sys.executable, str(ROOT / "scripts/bytes_gates.py"),
                    "--runs", str(self.export.csv_path), "--measurements", str(root / "measurements.json"),
                    "--out", str(out)]
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(gates.read(out)["status"], "fail")
            self.assertIn("clock:session: fail", result.stdout)
            self.assertIn("sizing:bytes-s6-p2: pass", result.stdout)
            measured["runs"].pop(next(iter(measured["runs"])))
            write(root / "measurements.json", measured)
            out.unlink()
            result = subprocess.run(args, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertFalse(out.exists())
            self.assertIn("membership differs", result.stderr)

    def test_claim_missing_duplicate_and_nonfinite_inputs_are_refused(self):
        for mutate in (
            lambda m: m.update(non_claim=False),
            lambda m: m["runs"].pop(next(iter(m["runs"]))),
            lambda m: m["regimes"].pop("llama-70b"),
            lambda m: m["clock"].update(rate_ppm="NaN"),
            lambda m: m["runs"][next(iter(m["runs"]))].update(request_s=-1),
            lambda m: m["runs"][next(iter(m["runs"]))].update(retained_bytes=1.5),
        ):
            measured = deepcopy(self.measured)
            mutate(measured)
            with self.assertRaises((ValueError, KeyError)):
                self.result(measured)
        rows = deepcopy(self.rows)
        rows[0]["non_claim"] = "False"
        with self.assertRaises(ValueError):
            self.result(rows=rows)
        with self.assertRaises(ValueError):
            self.result(rows=self.rows + self.rows[:1])


H_CUT_STAGES = ("bytes-mac-check-soak-qwen35-122b", "bytes-mac-check-test7-llama-70b-end",
                "bytes-mac-check-test7-qwen35-122b-end", "bytes-mac-check-test7-qwen3-next-80b-end",
                "bytes-mac-check-reference-end")


class StoppedSessionTests(World):
    """BYTES item H (2026-10-21): the chain was stopped during soak llama-70b
    r12. Harvest exports every planned row; the 28 that never ran are status
    "failed" with empty numeric cells, and desk's MEASUREMENTS.json leaves their
    timing receipts null. The regime, cpu_contention and sizing receipts are
    null too (no stage or program derived them). C5 must print every line the
    95 measured members support and mark the rest, not withhold the file."""

    def stopped_world(self, *, receipts_absent=True):
        rows, measured = deepcopy(self.rows), deepcopy(self.measured)
        dropped = sorted(r["run_id"] for r in rows if r["stage_id"] in H_CUT_STAGES
                         or r["run_id"] == "bytes-mac-check-soak-llama-70b-r12")
        numeric = [k for k in rows[0] if k.startswith(("phase_", "dur_", "bound_E_")) or k.endswith(("_energy_j", "_j"))]
        for row in rows:
            if row["run_id"] in dropped:
                row["status"] = "failed"
                row.update({k: "" for k in numeric})
                measured["runs"][row["run_id"]] = {**{f: None for f in gates.TIMING_FIELDS}, "retained_bytes": 0}
        if receipts_absent:
            measured["cpu_contention"] = {"w_j_per_cpu_s": None, "c_q_cpu_s": None}
            for regime in measured["regimes"].values():
                regime.update(F_min_j=None, census_resolution_w=None, outside_power_w=None, operative_bound_s=None)
            measured["sizing"] = {"fixed_desk_s": None, "collection_stage_overhead_s": None}
        return rows, measured, dropped

    def test_stopped_session_prints_measured_lines_and_marks_the_rest(self):
        rows, measured, dropped = self.stopped_world()
        # The same membership H exported: 95 ran, 28 never started.
        self.assertEqual((len(rows) - len(dropped), len(dropped)), (95, 28))
        result = self.result(measured, rows)
        lines = {g["gate"]: g for g in result["gates"]}
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["unmeasured_members"], dropped)
        self.assertEqual((lines["completeness:llama-70b:soak"]["status"], lines["completeness:llama-70b:soak"]["succeeded"]), ("fail", 11))
        self.assertEqual((lines["completeness:qwen35-122b:soak"]["status"], lines["completeness:qwen35-122b:soak"]["succeeded"]), ("fail", 0))
        for model in self.measured["regimes"]:
            self.assertEqual(lines["completeness:" + model + ":check"]["status"], "pass")
            for gate in ("contention:", "cpu_contention:", "resolvability:"):
                self.assertEqual(lines[gate + model]["status"], "unavailable")
            self.assertEqual(lines["calibration_T10:" + model]["status"], "flag_only")
        self.assertEqual(lines["thermal"]["status"], "pass")
        self.assertEqual(lines["sizing:bytes-s1-p1"]["status"], "unavailable")
        self.assertIsNone(result["sessions"]["bytes-s1-p1"]["est_minutes"])
        groups = {(g["model_id"], g["purpose"]): g for g in result["spread_groups"]}
        self.assertEqual((groups["qwen35-122b", "soak"]["runs"], groups["qwen35-122b", "soak"]["spread"]), (0, None))
        self.assertEqual((groups["llama-70b", "soak"]["runs"], groups["llama-70b", "soak"]["complete"]), (11, False))
        # Independent recomputation over the members that ran.
        ran = {r["run_id"] for r in rows if r["status"] == "succeeded"}
        expected = Decimal(0)
        for model in result["models"]:
            for purpose in ("check", "soak"):
                times = [Decimal(self.measured["runs"][m["run_id"]]["request_s"]) for m in self.plan["members"]
                         if m["model_id"] == model and m["purpose"] == purpose and m["run_id"] in ran]
                if len(times) >= 2:
                    expected = max(expected, max(times) / min(times) - 1)
        self.close(result["measured_margin"], expected)
        kept = [Decimal(self.measured["runs"][m["run_id"]]["request_s"]) for m in self.plan["members"]
                if m["model_id"] == "llama-70b" and m["purpose"] in ("check", "soak") and m["run_id"] in ran]
        self.assertEqual(len(kept), 16)
        self.close(result["models"]["llama-70b"]["request_mean_s"], sum(kept) / len(kept))
        self.assertFalse(result["models"]["llama-70b"]["measured_margin_complete"])

    def test_stopped_session_cli_writes_c5_and_exit_reports_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for receipts_absent, code, status in ((True, 2, "fail"), (False, 2, "fail")):
                rows, measured, _ = self.stopped_world(receipts_absent=receipts_absent)
                csv_path = root / "x.runs.csv"
                with csv_path.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
                write(root / "x.session.json", self.sidecar)
                write(root / "measurements.json", measured)
                out = root / "c5.json"
                result = subprocess.run([sys.executable, str(ROOT / "scripts/bytes_gates.py"), "--runs", str(csv_path),
                                         "--measurements", str(root / "measurements.json"), "--out", str(out)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(gates.read(out)["status"], status)
                self.assertIn("completeness:qwen35-122b:soak: fail", result.stdout)
                self.assertIn("sizing:bytes-s1-p1: " + ("unavailable" if receipts_absent else "flag only"), result.stdout)
                out.unlink()

    def test_complete_runs_with_absent_receipts_are_unavailable_not_withheld(self):
        measured = deepcopy(self.measured)
        measured["cpu_contention"] = {"w_j_per_cpu_s": None, "c_q_cpu_s": None}
        result = self.result(measured)
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual({g["status"] for g in result["gates"] if g["gate"].startswith("cpu_contention:")}, {"unavailable"})
        self.assertEqual(result["cpu_contention_alternative"], [])
        self.assertEqual({g["status"] for g in result["gates"] if g["gate"].startswith("sizing:")}, {"pass"})
        with tempfile.TemporaryDirectory() as tmp:
            write(Path(tmp) / "measurements.json", measured)
            out = Path(tmp) / "c5.json"
            cli = subprocess.run([sys.executable, str(ROOT / "scripts/bytes_gates.py"), "--runs", str(self.export.csv_path),
                                  "--measurements", str(Path(tmp) / "measurements.json"), "--out", str(out)],
                                 capture_output=True, text=True)
            self.assertEqual(cli.returncode, 1, cli.stderr)
            self.assertEqual(gates.read(out)["status"], "unavailable")

    def test_succeeded_member_with_null_timing_is_still_refused(self):
        measured = deepcopy(self.measured)
        rid = next(r["run_id"] for r in self.rows if r["status"] == "succeeded")
        measured["runs"][rid].update({f: None for f in gates.TIMING_FIELDS})
        with self.assertRaises((ValueError, ArithmeticError)):
            self.result(measured)
