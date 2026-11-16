"""Cold-review admission regressions. Every custody byte is generated here; no recordings are read."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from joulewise.cadence_looks import inclusion_34 as I34
from joulewise.cadence_looks import manifest as M
from joulewise.cadence_looks import step3_roster as S3
from joulewise.cadence_looks import time_fields as TF
from tests.cadence import look_minirepo as MR

try:
    from scripts import cadence_look_run as R
    from scripts import cadence_look_synth as SY
    from joulewise.cadence_looks import fit_interim as F
    from tests.cadence.test_time_fields import gpu_hole, bundle_of
except ModuleNotFoundError as exc:
    if exc.name != "numpy":
        raise
    R = SY = F = None


def read(path):
    return json.loads(Path(path).read_text())


class FittedIntervals(unittest.TestCase):
    def test_rule_replay_config_and_optional_g0_sources_are_bound(self):
        with tempfile.TemporaryDirectory(prefix="replay-map-") as td:
            root = Path(td)
            (root / "runner_receipt.json").write_text(json.dumps({"roster": ["L001"]}))
            ldir = root / "legs/L001"
            bundle = ldir / "runtime/bundle"
            (bundle / "outputs").mkdir(parents=True)
            (ldir / "leg_record.json").write_text(json.dumps({"spec": {"leg_type": "A"},
                                                              "result": {"bundle": "bundle"}}))
            replay_paths = ("config.json", "outputs/align_runtime_events.jsonl", "align_runtime_events.jsonl")
            for name in replay_paths:
                (bundle / name).write_text('{}\n')
            files = M.nonenergy_files(root)
            for name in replay_paths:
                self.assertIn("legs/L001/runtime/bundle/" + name, files)

    def test_union_preserves_disjoint_support_and_prefix_tails(self):
        ivs = TF.connected_intervals([(10, 20), (0, 10), (5, 12), (30, 35), (35, 38)])
        self.assertEqual(ivs, [(0, 20), (30, 38)])
        # The ten seconds outside the fit must not become a fitted trace hole.
        self.assertEqual(max(TF.gpu_max_uncovered([0, 30], [20, 38], a, b) for a, b in ivs), 0)


@unittest.skipIf(F is None, "numpy is not installed; runs in the look-fit CI job")
class Admission(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="round7-generated-")
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.source = Path(cls.tmp.name) / "custody"
        tokens = {}
        li, en, _ = SY.build("exact", tokens=tokens)
        wanted = {f"dev-01-s0{day}/L00{leg}" for day in (1, 2) for leg in (1, 2, 3)}
        wanted.add("dev-01-s02/L007")
        li["legs"] = [leg for leg in li["legs"] if leg["leg_key"] in wanted]
        ids = {leg["span_id"] for leg in li["legs"]}
        li["spans"] = [span for span in li["spans"] if span["span_id"] in ids]
        SY.write_custody(str(cls.source), li, en, tokens)
        cls.roster = read(cls.source / "roster.json")
        cls.selected = I34.keys(read(MR.REPO / I34.RUNTIME_CONFIG)["sensors"])
        cls.verdicts = I34.judge_custody(cls.roster, R.span_dirs(cls.source, []), cls.selected)[0]
        assert all(all(v.values()) for v in cls.verdicts.values())
        (cls.source / "rules_3_4.json").write_text(json.dumps(cls.verdicts))

    def source_copy(self):
        td = tempfile.TemporaryDirectory(prefix="round7-case-")
        self.addCleanup(td.cleanup)
        root = Path(td.name) / "custody"
        shutil.copytree(self.source, root)
        return root

    def stage1(self, root):
        li = R.read_look_input(self.roster, R.span_dirs(root, []), self.verdicts)
        return F.stage1(li, hashlib.sha256(F.dump(li)).hexdigest())

    def test_boundary_hole_is_one_gap_in_stage1(self):
        for width, excluded in ((3.0, True), (2.0, False)):
            with self.subTest(width=width):
                root = self.source_copy()
                key = "dev-01-s01/L001"
                leg = next(leg for leg in self.stage1(root)["legs"] if leg["leg_key"] == key)
                edge = leg["segments"][2]["wall_end_s"]
                gpu_hole(bundle_of(root / leg["span_id"], key) / "power_trace.csv", edge - width / 2, width)
                got = next(leg for leg in self.stage1(root)["legs"] if leg["leg_key"] == key)
                self.assertEqual(got["trace_holes"]["gpu_rail"]["max_gap_s"], width)
                self.assertEqual(got["trace_holes"]["gpu_rail"]["excluded"], excluded)
                self.assertEqual(got["in_energy_fit"], not excluded)

    def test_boundary_hole_is_refused_by_stage2_backstop(self):
        root = self.source_copy()
        stage1 = self.stage1(root)
        leg = stage1["legs"][0]
        edge = leg["segments"][2]["wall_end_s"]
        gpu_hole(bundle_of(root / leg["span_id"], leg["leg_key"]) / "power_trace.csv", edge - 1.5, 3.0)
        # Bypass custody_check deliberately: exercise the independent backstop on decoded row supports.
        with self.assertRaisesRegex(F.LookInputError, leg["leg_key"] + r": 3\.000 s"):
            R.read_segment_energy(stage1, R.span_dirs(root, []), gpu_max_gap_s=2.0)

    def test_repeated_boundary_holes_cannot_hide_missing_coverage(self):
        root = self.source_copy()
        stage1 = self.stage1(root)
        leg = stage1["legs"][0]
        path = bundle_of(root / leg["span_id"], leg["leg_key"]) / "power_trace.csv"
        boundaries = [seg["wall_end_s"] for seg in leg["segments"][1:-1]]
        self.assertEqual(len(boundaries), 15)
        for edge in boundaries:
            gpu_hole(path, edge - 1.5, 3.0)
        got = next(row for row in self.stage1(root)["legs"] if row["leg_key"] == leg["leg_key"])
        self.assertEqual(got["trace_holes"]["gpu_rail"]["max_gap_s"], 3.0)
        self.assertFalse(got["in_energy_fit"])

    def missing_start_fan(self, root):
        key = "dev-01-s02/L007"
        leg = next(leg for leg in self.stage1(root)["legs"] if leg["leg_key"] == key)
        bundle = bundle_of(root / leg["span_id"], key)
        journal = bundle / "outputs/align_thermal.jsonl"
        rows = [json.loads(line) for line in journal.read_text().splitlines()]
        start = max(row["finished"]["wall_ns"] for row in rows
                    if row.get("kind") == "reading"
                    and row["finished"]["wall_ns"] <= round(leg["segments"][0]["wall_start_s"] * 1e9))
        for row in rows:
            if row.get("kind") == "reading" and row["finished"]["wall_ns"] == start:
                row["values"]["sensors"]["F0Ac"] = None
        journal.write_text("".join(json.dumps(row) + "\n" for row in rows))
        return key, bundle

    def test_step3_checks_timing_of_included_leg_outside_energy_fit(self):
        root = self.source_copy()
        key, bundle = self.missing_start_fan(root)
        stage1 = self.stage1(root)
        leg = next(leg for leg in stage1["legs"] if leg["leg_key"] == key)
        self.assertTrue(leg["included"])
        self.assertFalse(leg["in_energy_fit"])
        self.assertEqual(S3.custody_problems(stage1, None, R.span_dirs(root, [])), [])
        x = leg["segments"][3]["wall_start_s"] + 4
        gpu_hole(bundle / "power_trace.csv", x, 4.0)
        problems = S3.custody_problems(stage1, None, R.span_dirs(root, []))
        self.assertTrue(problems, "Step 3 accepted timing stage 1 never judged")
        self.assertIn(key, "; ".join(problems))
        self.assertIn("row stamps", "; ".join(problems))

    def test_step3_cli_refuses_changed_nonfit_trace_before_value_loader(self):
        root = self.source_copy()
        key, bundle = self.missing_start_fan(root)
        mini = MR.mini_repo(self)
        sha = R.sha256_file
        hashes = dict(roster_sha256=sha(root / "roster.json"), verdicts_sha256=sha(root / "rules_3_4.json"))
        MR.commit(mini, **hashes)
        stage1, fit, output = (root.parent / name for name in ("D.json", "O.json", "S3.json"))
        result = MR.py(mini, "scripts/cadence_look_run.py", "stage1", "--roster", root / "roster.json",
                       "--rules-3-4", root / "rules_3_4.json", "--custody", root,
                       "--manifest", mini / MR.MANIFEST, "--out", stage1)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        doc = read(stage1)
        leg = next(row for row in doc["legs"] if row["leg_key"] == key)
        self.assertTrue(leg["included"])
        self.assertFalse(leg["in_energy_fit"])
        MR.commit(mini, stage1_sha256=sha(stage1), **hashes)
        args = ("--stage1", stage1, "--stage1-sha256", sha(stage1), "--custody", root,
                "--manifest", mini / MR.MANIFEST)
        result = MR.py(mini, "scripts/cadence_look_run.py", "stage2", *args, "--out", fit)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = MR.py(mini, "joulewise/cadence_looks/step3_roster.py", *args, "--out", output)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        output.unlink()
        gpu_hole(bundle / "power_trace.csv", leg["segments"][3]["wall_start_s"] + 4, 4.0)
        # An energy decoder reaching this canary would raise; the time-only custody guard must refuse first.
        path = bundle / "power_trace.csv"
        rows = path.read_text().splitlines()
        fields = rows[-1].split(",")
        fields[1] = "ENERGY_CANARY_NEVER_DECODE"
        rows[-1] = ",".join(fields)
        path.write_text("\n".join(rows) + "\n")
        result = MR.py(mini, "joulewise/cadence_looks/step3_roster.py", *args, "--out", output)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(key, result.stdout)
        self.assertIn("row stamps", result.stdout)
        self.assertNotIn("ENERGY_CANARY", result.stdout + result.stderr)
        self.assertFalse(output.exists())

    def test_committed_verdicts_cannot_admit_changed_meter_or_journal(self):
        mini = MR.mini_repo(self)
        sha = R.sha256_file
        MR.commit(mini, roster_sha256=sha(self.source / "roster.json"),
                  verdicts_sha256=sha(self.source / "rules_3_4.json"))
        for fault, rule in ((None, None), ("meter", "km003c_clean"), ("journal", "sidecar_coverage")):
            with self.subTest(fault=fault):
                root = self.source_copy()
                key = "dev-01-s01/L001"
                if fault == "meter":
                    path = root / "dev-01-s01/hazards/meter/stream-0001.jsonl"
                    rows = [json.loads(line) for line in path.read_text().splitlines()]
                    rows[-1]["stop_reason"] = "exception"
                    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
                elif fault == "journal":
                    path = bundle_of(root / "dev-01-s01", key) / "outputs/align_thermal.jsonl"
                    start = self.stage1(root)["legs"][0]["segments"][0]["wall_start_s"]
                    rows = [json.loads(line) for line in path.read_text().splitlines()]
                    rows = [row for row in rows if row.get("kind") != "reading"
                            or not start + 20 <= row["finished"]["wall_ns"] / 1e9 < start + 30]
                    path.write_text("".join(json.dumps(row) + "\n" for row in rows))
                out = root.parent / "D.json"
                result = MR.py(mini, "scripts/cadence_look_run.py", "stage1", "--roster", root / "roster.json",
                               "--rules-3-4", root / "rules_3_4.json", "--custody", root,
                               "--manifest", mini / MR.MANIFEST, "--out", out)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                doc = read(out)
                self.assertFalse(doc["allow_draft"])
                self.assertIsNotNone(doc["ledger_gate"])
                got = next(leg for leg in doc["legs"] if leg["leg_key"] == key)
                if rule:
                    fresh = I34.judge_span(root / "dev-01-s01", "dev-01-s01", self.selected)[0]
                    self.assertFalse(fresh[key][rule])
                    self.assertFalse(got["inclusion"][rule], "committed stale verdict bypassed source replay")
                    self.assertFalse(got["in_energy_fit"])
                else:
                    self.assertTrue(got["in_energy_fit"])
                self.assertEqual(sha(root / "rules_3_4.json"), sha(self.source / "rules_3_4.json"))
