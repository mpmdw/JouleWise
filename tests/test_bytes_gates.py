"""C5 execution on native non-claim exports shaped like every Mac-kit member."""
from copy import deepcopy
import csv
from decimal import Decimal
from fractions import Fraction
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
from tests.b6.test_export_runs import seal_reference_inputs

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
            write(bundle / "metadata.json", {"device": {"telemetry": "mock", "rail_manifest": ["mock"]}})
            write(bundle / "status.json", {"status": {"state": "succeeded"}})
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
                {"event_type": "phase_start", "phase": "tokenize", "timestamp_s": start - 1},
                {"event_type": "phase_start", "phase": "decode", "timestamp_s": start},
                {"event_type": "phase_end", "phase": "decode", "timestamp_s": start + duration})))
            (bundle / "power_trace.csv").write_text("timestamp_s,power_w,rail,source\n" +
                "".join(f"{t},20,mock,mock\n" for t in range(start - 1, start + duration + 1)))
            write(archive / "withheld/reductions" / (rid + ".summary_metrics.rereduced.json"),
                  {"phase_energy_j": {"decode": duration * 20},
                   "idle_baseline": {"power_w_mean": 3}})
            measured["runs"][rid] = {"request_s": request, "member_wall_s": request + 80,
                                      "stream_s": request + 60, "retained_bytes": 2 * 1024**2, "raw_allocated_bytes": 1024**2,
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
    seal_reference_inputs(archive)
    registration = ROOT / "configs/campaigns/bytes_mac_check/registration"
    result = export_runs.export(archive, {}, registration, root / "private", root / "export",
        non_claim=True, evidence=evidence, acceptance_record={"pack_id": "bytes-mac-check", "session_id": session,
                                                           "counting": False, "verdict": "NON_CLAIM"})
    write(root / "measurements.json", measured)
    return result, measured


class ReplayTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Integer identities: WAIT=ceil((1/3 B/s)*7200s)=2400B;
        # B=101B, fixed=7B, c=2, hence P=5009B with no padding.
        self.p = 2 * (101 + 2400) + 7
        self.c5 = {"session_id": "h", "gates": [{"gate": "disk:kit",
            "extra_wait_raw_bytes": 2400, "fixed_retained_bytes": 7}],
            "sessions": {"bytes-s1-p1": {"required_free_bytes": self.p + 1}}}
        self.measured = {"session_id": "h", "runs": {
            "one": {"stream_s": 3, "raw_allocated_bytes": 101},
            "never": {"stream_s": None, "raw_allocated_bytes": None}}}

    def b6(self, name, free):
        root = self.root / name
        root.mkdir()
        device = root.stat().st_dev
        write(root / "custody/hazards/arm.json", {"hazards": {"disk": [
            {"measurement": {"error": "ignore", "values": {"targets": [{"device": device, "free_bytes": 0}]}}},
            {"measurement": {"values": {"targets": [
                {"device": device + 1, "free_bytes": 0},
                {"device": device, "free_bytes": free + 10},
                {"device": device, "free_bytes": free},
                {"device": device, "error": "ignore", "free_bytes": 0}]}}}]}})
        write(root / "archive.desk/compression-summary.json", {"free_bytes_before": free - 50})
        (root / "archive.desk/compression.jsonl").write_text("".join(json.dumps(r) + "\n" for r in [
            {"event": "compress", "root": "runs", "size": 100},
            {"event": "compress", "root": "runs", "size": 1},
            {"event": "skip", "root": "runs", "size": 999},
            {"event": "compress", "root": "archive", "size": 999}]))
        return root

    def test_nine_plus_h_replay_and_integer_boundaries(self):
        roots = [self.b6("r" + str(i), self.p + i) for i in range(9)]
        h = self.root / "h"
        write(h / "desk.json", {"disk": {"free_at_arm_bytes": self.p, "free_at_desk_start_bytes": self.p - 50}})
        result = gates.replay_disk([*roots, h], self.c5, self.measured)
        self.assertEqual(result["session_count"], 10)
        self.assertEqual(result["refusal_count"], 0)
        self.assertEqual(result["unavailable_count"], 0)
        self.assertEqual(result["largest_pass_refusal_count"], 2)
        for row in result["sessions"]:
            self.assertEqual(row["required_free_bytes"], self.p)
            self.assertEqual(row["D_bytes"], 50)
            # Same integer division on both sides: bit identity is the property.
            self.assertEqual(row["measured_c"], 50 / 101)
        below = self.b6("below", self.p - 1)
        self.assertTrue(gates.replay_disk([below], self.c5, self.measured)["sessions"][0]["refused"])

    def test_missing_inputs_are_listed_never_refused(self):
        missing = self.root / "absent"
        result = gates.replay_disk([missing], self.c5, self.measured)
        self.assertEqual(result["session_count"], 1)
        self.assertEqual(result["unavailable_count"], 1)
        self.assertEqual(result["refusal_count"], 0)
        self.assertEqual(result["refusal_census"], [])
        self.assertIsNone(result["sessions"][0]["refused"])
        self.assertTrue(result["sessions"][0]["flags"])

    def test_cli_outputs_rows_and_refusal_count(self):
        root = self.b6("below", self.p - 1)
        write(self.root / "c5.json", self.c5)
        write(self.root / "measurements.json", self.measured)
        out = self.root / "replay.json"
        run = subprocess.run([sys.executable, str(ROOT / "scripts/bytes_gates.py"), "replay",
            "--c5", str(self.root / "c5.json"), "--measurements", str(self.root / "measurements.json"),
            "--out", str(out), str(root)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2, run.stderr)
        self.assertIn("refusal_count=1/1 unavailable=0", run.stdout)
        self.assertEqual(json.loads(out.read_text())["refusal_count"], 1)


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
    def test_varying_stream_overhead_uses_largest_and_exact_p(self):
        receipts = [dict(request_s=2, stream_s=3, member_wall_s=4, raw_allocated_bytes=150),
                    dict(request_s=4, stream_s=7, member_wall_s=8, raw_allocated_bytes=350)]
        # Request spread gives margin=4/2-1=1. Overheads are 1 and 3 seconds.
        # Exact rationals/bytes pin the ruling, rather than a floating tolerance.
        margin = Fraction(4, 2) - 1
        expected_allowance = (Fraction(2 + 4, 2) + Fraction(3)) * (1 + margin)
        allowance = gates.disk_allowance(receipts, count=3, margin=margin)
        self.assertEqual(allowance['stream_allowance_s'], expected_allowance)
        # r_s=max(150/3,350/7)=50; r_w=max(150/4,350/8)=175/4.
        # Stream basis=ceil(50*3*12)=1800; wall=ceil((175/4)*3*12)=1575.
        # WAIT=ceil(50*7200)=360000; fixed=7; P=2*(1800+360000)+7.
        terms = gates.disk_terms(Fraction(50), Fraction(175, 4), {'model': allowance}, 7)
        expected_stream = math.ceil(Fraction(50) * 3 * expected_allowance)
        expected_wall = math.ceil(Fraction(175, 4) * 3 * Fraction(4 + 8, 2) * 2)
        expected_p = 2 * (expected_stream + math.ceil(Fraction(50) * 7200)) + 7
        self.assertGreater(expected_stream, expected_wall)
        self.assertEqual(terms['stream_basis_bytes'], expected_stream)
        self.assertEqual(terms['wall_basis_bytes'], expected_wall)
        self.assertEqual(terms['B_bytes'], expected_stream)
        self.assertEqual(terms['required_free_bytes'], expected_p)

    def test_hand_computed_p_includes_margin_reference_and_tree_counts(self):
        measured = deepcopy(self.measured)
        science = {m['run_id'] for m in self.plan['members'] if m['model_id'] != 'reference'}
        for rid, receipt in measured['runs'].items():
            receipt.update(request_s=1, stream_s=2, member_wall_s=3,
                           raw_allocated_bytes=100, retained_bytes=200)
        for model in measured['regimes']:
            for purpose in ('check', 'soak', 'test'):
                ids = [m['run_id'] for m in self.plan['members']
                       if m['model_id'] == model and m['purpose'] == purpose]
                for i, rid in enumerate(ids):
                    request = 2 + 2 * (i % 2)
                    measured['runs'][rid].update(request_s=request, stream_s=request + 2,
                        member_wall_s=request + 4, raw_allocated_bytes=10, retained_bytes=20)
        # Other science purposes must not set a higher rate than references.
        for rid in science:
            measured['runs'][rid]['raw_allocated_bytes'] = 10
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for path in (ROOT / 'configs/campaigns').glob('bytes-s*/plan_tree.json'):
                tree = gates.read(path)
                if path.parent.name == 'bytes-s1-p1':
                    mids = tree['module_order']
                    tree['science'] = ([{'module_id': mids[0]}] * 2 +
                                       [{'module_id': mids[1]}] * 3)
                    tree['stage_graph'] = [{'kind': 'campaign_collection', 'expected_count': 6}]
                write(root / 'configs/campaigns' / path.parent.name / path.name, tree)
            source = root / 'fixed.json'
            write(source, {'packs': {'bytes-mac-check': {'disk_derivation': {'fixed_retained_bytes': 7}}}})
            result = gates.calculate(deepcopy(self.rows), deepcopy(self.sidecar), measured,
                deepcopy(self.plan), repo_root=root, committed_sizing=source)
        terms = result['sessions']['bytes-s1-p1']['disk_derivation']
        # Five checks have requests 2,4,2,4,2: mean=14/5; margin=4/2-1=1.
        # Science stream=(14/5+2)*2=48/5; wall=(14/5+4)*2=68/5.
        # Reference stream=(1+1)*2=4; wall=3*2=6; counts science=2,3; ref=1.
        # Reference raw=100 gives r_s=100/2=50, r_w=100/3 (science rates lower).
        # stream=ceil(50*(2*48/5+3*48/5+4))=2600;
        # wall=ceil((100/3)*(2*68/5+3*68/5+6))=2467; B=2600.
        # WAIT=ceil(50*7200)=360000; fixed=7; P=2*(2600+360000)+7=725207.
        allowance = terms['allowances_by_model']['qwen3-1p7b']['stream_allowance_s']
        self.assertEqual(Fraction(allowance['numerator'], allowance['denominator']), Fraction(48, 5))
        reference = terms['allowances_by_model']['reference']
        self.assertEqual(reference['count'], 1)
        self.assertEqual(reference['stream_allowance_s'], {'numerator': 4, 'denominator': 1})
        self.assertEqual(reference['member_allowance_s'], {'numerator': 6, 'denominator': 1})
        self.assertEqual(terms['stream_basis_bytes'], 2600)
        self.assertEqual(terms['wall_basis_bytes'], 2467)
        self.assertEqual(terms['B_bytes'], 2600)
        self.assertEqual(terms['extra_wait_raw_bytes'], 360000)
        self.assertEqual(terms['fixed_retained_bytes'], 7)
        self.assertEqual(terms['required_free_bytes'], 725207)

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
        self.assertEqual(len(report["inputs"]), 5)
        self.assertEqual(len(result.stdout.splitlines()), len(report["gates"]))
        for session in report["sessions"].values():
            self.assertIn("disclosure only; no gate reads", session["projected_footprint_bytes_note"])
        for model in report["models"].values():
            self.assertIn("two-copy retained maximum", model["bytes_per_member_note"])
        for gate in report["gates"]:
            if gate["gate"].startswith("disk:") and "B_bytes" in gate:
                output = next(s for s in result.stdout.splitlines() if s.startswith(gate["gate"] + ":"))
                terms = [("r_s=", gate["stream_rate_bytes_per_s"]),
                         ("r_w=", gate["wall_rate_bytes_per_s"])]
                for model, allowance in gate["allowances_by_model"].items():
                    terms.extend([(model + ":stream_s=", allowance["stream_allowance_s"]),
                                  (",member_wall_s=", allowance["member_allowance_s"])])
                for label, value in terms:
                    exact = Fraction(value["numerator"], value["denominator"])
                    # Printed representation is exact formatting, not a
                    # numerical agreement bar; nine digits exceed ruled seven.
                    self.assertIn(label + f"{float(exact):.9g} ({exact.numerator}/{exact.denominator})", output)
        lines = {r["gate"]: r for r in report["gates"]}
        for model in self.measured["regimes"]:
            contention = lines["contention:" + model]
            self.close(contention["P_limit_w"], 4 / (4 * (200 if model in self.plan["long_regimes"] else 20)))
            self.assertEqual(contention["status"], "flag_only")
            self.assertEqual(contention["reason"], "registered_T_phase_absent")
            self.assertEqual(lines["calibration_T10:" + model]["status"], "flag_only")
        # No MLX/hardware or key material is read by the C5 desk path.
        self.assertFalse((self.root / "private").exists())

    def test_committed_fixed_source_override_and_missing_never_fallback(self):
        source = self.root / "committed-sizing.json"
        # Exact integer artifact sizes: changing committed fixed changes P byte for byte.
        write(source, {"packs": {"bytes-mac-check": {"disk_derivation": {"fixed_retained_bytes": 7}}}})
        baseline = self.result()
        result = gates.calculate(deepcopy(self.rows), deepcopy(self.sidecar),
            deepcopy(self.measured), deepcopy(self.plan), committed_sizing=source)
        committed = gates.committed_fixed(gates.COMMITTED_SIZING)[0]
        for pack, sized in result["sessions"].items():
            self.assertEqual(sized["required_free_bytes"], baseline["sessions"][pack]["required_free_bytes"] - committed + 7)
        self.assertEqual(result["committed_fixed_source"], {"path": str(source),
            "sha256": gates.hashlib.sha256(source.read_bytes()).hexdigest(), "json_pointer": gates.FIXED_POINTER})
        self.assertEqual(result["measured_fixed_retained_bytes_unused"], 1024**2)
        for value in (None, True, -1, "7", 1.5):
            write(source, {"packs": {"bytes-mac-check": {"disk_derivation": {"fixed_retained_bytes": value}}}})
            result = gates.calculate(deepcopy(self.rows), deepcopy(self.sidecar),
                deepcopy(self.measured), deepcopy(self.plan), committed_sizing=source)
            self.assertEqual({g["status"] for g in result["gates"] if g["gate"].startswith("disk:")}, {"unavailable"})
            self.assertIn("disk.committed_fixed_missing", [f["code"] for f in result["flags"]])
        source.unlink()
        out = self.root / "missing-fixed-c5.json"
        code = gates.main(["--runs", str(self.export.csv_path), "--measurements", str(self.root / "measurements.json"),
                           "--committed-sizing", str(source), "--out", str(out)])
        self.assertEqual(code, 1)
        self.assertTrue(out.is_file())

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

    def test_disk_p_and_thermal_counterexamples_reach_fail_lines(self):
        measured = deepcopy(self.measured)
        result = self.result(measured)
        disk = next(g for g in result["gates"] if g["gate"] == "disk:kit")
        measured["disk"]["pre_arm_free_bytes"] = disk["required_free_bytes"]
        self.assertEqual(next(g for g in self.result(measured)["gates"] if g["gate"] == "disk:kit")["status"], "pass")
        measured["disk"]["pre_arm_free_bytes"] -= 1  # One integer byte below P (no reserve).
        measured["runs"][next(iter(measured["runs"]))]["thermal_level"] = 1  # Catalog excludes OS level > 0.
        lines = {g["gate"]: g for g in self.result(measured)["gates"]}
        self.assertEqual(lines["disk:kit"]["status"], "fail")
        self.assertEqual(lines["thermal"]["status"], "fail")

    def test_measured_copy_factor_is_disclosure_only(self):
        original = self.result()
        measured = deepcopy(self.measured)
        measured["disk"]["measured_c"] = Decimal("0.8020750916018277")
        disclosed = self.result(measured)
        for pack, sized in original["sessions"].items():
            other = disclosed["sessions"][pack]
            self.assertEqual(sized["required_free_bytes"], other["required_free_bytes"])
            self.assertEqual(other["disk_derivation"]["peak_copies"], 2)
            self.assertEqual(other["disk_derivation"]["measured_c"], measured["disk"]["measured_c"])

    def test_disk_missing_raw_bytes_is_unavailable_and_flagged(self):
        measured = deepcopy(self.measured)
        for receipt in measured["runs"].values():
            receipt.pop("raw_allocated_bytes")
        result = self.result(measured)
        self.assertEqual({g["status"] for g in result["gates"] if g["gate"].startswith("disk:")}, {"unavailable"})
        self.assertEqual(result["flags"][0]["code"], "disk.raw_bytes_missing")
        self.assertEqual(result["flags"][0]["count"], len(measured["runs"]))
        self.assertEqual(result["status"], "unavailable")

    def test_disk_terms_round_whole_bases_once_and_ignore_retained_copies(self):
        from fractions import Fraction as F
        terms = gates.disk_terms(F(1, 3), F(1, 2), {
            "a": {"count": 2, "stream_allowance_s": F(1), "member_allowance_s": F(1)},
            "b": {"count": 1, "stream_allowance_s": F(2), "member_allowance_s": F(1)}}, 7)
        # ceil(4/3)=2, ceil(3/2)=2; WAIT=7200/3; P=2*(2+2400)+7.
        self.assertEqual((terms["stream_basis_bytes"], terms["wall_basis_bytes"], terms["required_free_bytes"]), (2, 2, 4811))
        crossed = gates.disk_terms(F(1), F(1), {
            "a": {"count": 1, "stream_allowance_s": F(9), "member_allowance_s": F(1)},
            "b": {"count": 1, "stream_allowance_s": F(1), "member_allowance_s": F(9)}}, 0)
        # max(sum(9,1),sum(1,9))=10, unlike sum(max(9,1),max(1,9))=18.
        self.assertEqual(crossed["B_bytes"], 10)
        first = self.result()
        measured = deepcopy(self.measured)
        for receipt in measured["runs"].values():
            receipt["retained_bytes"] *= 3
        second = self.result(measured)
        for pack, sized in first["sessions"].items():
            self.assertEqual(sized["disk_derivation"], second["sessions"][pack]["disk_derivation"])
            # Free is an integer byte count: equality passes, P-1 fails.
            measured["disk"]["pre_arm_free_bytes"] = sized["required_free_bytes"]
            self.assertEqual(next(g for g in self.result(measured)["gates"] if g["gate"] == "disk:" + pack)["status"], "pass")
            measured["disk"]["pre_arm_free_bytes"] -= 1
            self.assertEqual(next(g for g in self.result(measured)["gates"] if g["gate"] == "disk:" + pack)["status"], "fail")

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
                measured["runs"][row["run_id"]] = {**{f: None for f in gates.TIMING_FIELDS}, "retained_bytes": 0, "raw_allocated_bytes": None}
        if receipts_absent:
            measured["cpu_contention"] = {"w_j_per_cpu_s": None, "c_q_cpu_s": None}
            for regime in measured["regimes"].values():
                regime.update(F_min_j=None, census_resolution_w=None, outside_power_w=None, operative_bound_s=None)
            measured["sizing"] = {"fixed_desk_s": None, "collection_stage_overhead_s": None}
        return rows, measured, dropped

    def test_remainder_without_checks_writes_independent_lines(self):
        # BY-H2 runs only both soaks, three models' test-7s, and references.
        plan = deepcopy(self.plan)
        plan["members"] = [m for m in plan["members"] if m["purpose"] != "check"]
        keep = {m["run_id"] for m in plan["members"]}
        keep.update(r["run_id"] for r in self.rows if r["run_id"] not in {m["run_id"] for m in self.plan["members"]})
        rows = [r for r in deepcopy(self.rows) if r["run_id"] in keep]
        measured = deepcopy(self.measured)
        measured["runs"] = {k: v for k, v in measured["runs"].items() if k in keep}
        measured["cpu_contention"] = {"w_j_per_cpu_s": None, "c_q_cpu_s": None}
        for regime in measured["regimes"].values():
            regime.update(F_min_j=None, census_resolution_w=None, outside_power_w=None)
        result = gates.calculate(rows, self.sidecar, measured, plan)
        lines = {g["gate"]: g for g in result["gates"]}
        self.assertEqual(lines["clock:llama-70b"]["status"], "pass")
        self.assertEqual(lines["disk:bytes-s5-p1"]["status"], "pass")
        self.assertEqual(lines["disk:bytes-s1-p1"]["status"], "unavailable")
        self.assertEqual(lines["resolvability:llama-70b"]["status"], "unavailable")
        self.assertTrue(any(f.get("input") == "llama-70b.check_decode_energies" for f in result["flags"]))

    def test_zero_run_session_has_no_margin_reference_or_clock_operands(self):
        rows, measured = deepcopy(self.rows), deepcopy(self.measured)
        for row in rows:
            row.update(status="failed", dur_decode_s="", phase_decode_j="")
            measured["runs"][row["run_id"]] = {
                **dict.fromkeys(gates.TIMING_FIELDS), "retained_bytes": 0, "raw_allocated_bytes": None}
        measured["clock"] = {"rate_ppm": None, "frequency_word_ppm": None}
        result = self.result(measured, rows)
        lines = {g["gate"]: g for g in result["gates"]}
        self.assertEqual(result["status"], "fail")  # Failed completeness, usable JSON.
        self.assertEqual(lines["clock:session"]["status"], "unavailable")
        self.assertEqual(lines["thermal"]["status"], "unavailable")
        for pack in result["sessions"].values():
            self.assertIsNone(pack["programmed_span_s"])
            self.assertIsNone(pack["disk_derivation"])
        self.assertTrue(any(f.get("input") == "measured_margin" for f in result["flags"]))

    def test_missing_or_malformed_operands_disable_only_dependent_lines(self):
        for value in (None, "", "not-a-number", "NaN", "Infinity", True, -1):
            with self.subTest(value=value):
                measured = deepcopy(self.measured)
                measured["cpu_contention"]["w_j_per_cpu_s"] = value
                measured["sizing"]["fixed_desk_s"] = value
                measured["regimes"]["llama-70b"]["F_min_j"] = value
                result = self.result(measured)
                lines = {g["gate"]: g for g in result["gates"]}
                self.assertEqual(lines["cpu_contention:llama-70b"]["status"], "unavailable")
                self.assertEqual(lines["contention:llama-70b"]["status"], "unavailable")
                self.assertEqual(lines["sizing:bytes-s1-p1"]["status"], "unavailable")
                self.assertEqual(lines["disk:bytes-s1-p1"]["status"], "pass")
                self.assertTrue(any(f["code"] == "receipt.operand_unavailable" for f in result["flags"]))
        measured, rows = deepcopy(self.measured), deepcopy(self.rows)
        measured["regimes"].pop("llama-70b")
        measured["clock"]["rate_ppm"] = "NaN"
        rid = next(m["run_id"] for m in self.plan["members"] if m["purpose"] == "check")
        row = next(r for r in rows if r["run_id"] == rid)
        row.update(dur_decode_s="", phase_decode_j="")
        result = self.result(measured, rows)
        lines = {g["gate"]: g for g in result["gates"]}
        self.assertEqual(lines["clock:session"]["status"], "unavailable")
        self.assertEqual(lines["contention:qwen3-1p7b"]["status"], "unavailable")
        self.assertEqual(lines["resolvability:qwen3-1p7b"]["status"], "unavailable")
        self.assertTrue(any(f.get("input") == rid + ".dur_decode_s" for f in result["flags"]))
        for k in (None, "2", True, 1.5):
            with self.subTest(census_quanta=k):
                measured = deepcopy(self.measured)
                measured['runs'][rid]['census_quanta'] = k
                result = self.result(measured)
                lines = {g['gate']: g for g in result['gates']}
                self.assertEqual(lines['cpu_contention:qwen3-1p7b']['status'], 'unavailable')
                self.assertTrue(any(f.get('input') == rid + '.census_quanta' for f in result['flags']))

    def test_model_never_ran_cli_writes_unavailable_dependent_packs(self):
        rows, measured = deepcopy(self.rows), deepcopy(self.measured)
        missing = {m["run_id"] for m in self.plan["members"] if m["model_id"] == "qwen35-122b"}
        # Five checks, twelve soaks and four test-7 probes are planned for this model.
        self.assertEqual(len(missing), 5 + 12 + 4)
        for row in rows:
            if row["run_id"] in missing:
                row["status"] = "failed"
                measured["runs"][row["run_id"]] = {
                    **dict.fromkeys(gates.TIMING_FIELDS), "retained_bytes": 0, "raw_allocated_bytes": None}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "early.runs.csv"
            with csv_path.open("w", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
            write(root / "early.session.json", self.sidecar)
            write(root / "measurements.json", measured)
            out = root / "c5.json"
            cli = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/bytes_gates.py"),
                "--runs", str(csv_path), "--measurements", str(root / "measurements.json"),
                "--out", str(out)], capture_output=True, text=True)
            self.assertEqual(cli.returncode, 2, cli.stderr)  # Incomplete check/soak groups fail.
            result = gates.read(out)
            self.assertIn({"code": "model.observations_missing", "model_id": "qwen35-122b"}, result["flags"])
            lines = {g["gate"]: g for g in result["gates"]}
            for prefix in ("contention:", "cpu_contention:", "calibration_T10:", "resolvability:", "clock:"):
                self.assertEqual(lines[prefix + "qwen35-122b"]["status"], "unavailable")
            for pack, sized in result["sessions"].items():
                affected = "qwen35-122b" in sized["modules"]
                for prefix in ("disk:", "sizing:"):
                    self.assertEqual(lines[prefix + pack]["status"] == "unavailable", affected)
                if affected:
                    for field in ("programmed_span_s", "required_free_bytes", "T_stream_max_s", "disk_derivation"):
                        self.assertIsNone(sized[field])
            self.assertIn("clock:llama-70b: pass", cli.stdout)

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

    def test_bad_mandatory_operand_never_drops_a_run_from_sizing(self):
        rid = next(r["run_id"] for r in self.rows if r["status"] == "succeeded")
        for key, value in (("request_s", None), ("request_s", -1), ("stream_s", ""),
                           ("retained_bytes", 1.5), ("thermal_level", None)):
            with self.subTest(key=key, value=value):
                measured = deepcopy(self.measured)
                measured["runs"][rid][key] = value
                result = self.result(measured)
                self.assertEqual(result['status'], 'unavailable')
                self.assertEqual(result['gates'][0]['status'], 'unavailable')
                self.assertEqual(result['flags'][0]['code'], 'receipt.operand_unavailable')
                self.assertIn(rid + '.' + key, result['flags'][0]['reason'])
                self.assertTrue(all(s['disk_derivation'] is None for s in result['sessions'].values()))
