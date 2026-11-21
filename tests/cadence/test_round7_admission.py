"""Cold-review admission regressions. Every custody byte is generated here; no recordings are read."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

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
    from tests.cadence import test_look_run as TLR
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

    def test_rl174_undecodable_span_excludes_even_fit_leg_without_turn(self):
        root = self.source_copy()
        sid = "dev-01-s01"
        stream = next((root / sid / "hazards/meter").glob("stream-*.jsonl"))
        rows = [json.loads(line) for line in stream.read_text().splitlines()]
        for row in rows:
            if row.get("p"):
                row["p"] = "not-hex"
                break
        stream.write_text("".join(json.dumps(row) + "\n" for row in rows))
        path = root / sid / "legs/L001/leg_record.json"
        rec = read(path)
        rec["result"]["bundle"] = None
        rec["result"]["leg_status"] = "incomplete"
        path.write_text(json.dumps(rec))
        # Isolate A.4 from replay's other reasons to exclude an incomplete leg.
        with patch.object(R.I34, "judge_span", return_value=(self.verdicts, {}, {})):
            got = self.stage1(root)
        self.assertEqual(got["meter_unreadable"], {"span_ids": [sid], "to_research_lead": False})
        rows = [leg for leg in got["legs"] if leg["span_id"] == sid]
        self.assertTrue(rows)
        self.assertTrue(all(not leg["inclusion"]["km003c_clean"] for leg in rows))
        self.assertTrue(all(not leg["in_energy_fit"] for leg in rows))
        self.assertIsNone(next(leg for leg in rows if leg["leg_key"] == sid + "/L001")["state"])

    def staged_plan(self, root, change=None):
        """Archive the span ``dev-01-s01`` of a custody copy (after ``change(span_dir)``), remove it from the custody
        and return the stage-1 arguments that read it back through ``--stage-archives``."""
        import tarfile
        sid = "dev-01-s01"
        parent = root.parent
        if change is not None:
            change(root / sid)
        archive, manifest, marker = [parent / name for name in ("span.tgz", "SHA256SUMS", "marker.json")]
        files = sorted(path for path in (root / sid).rglob("*") if path.is_file())
        manifest.write_text("".join(f"{R.sha256_file(path)}  ./{path.relative_to(root / sid).as_posix()}\n"
                                    for path in files))
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(root / sid, arcname=sid)
        marker.write_text(json.dumps({"schema": "joulewise.span_offload_marker.v1", "span_name": sid,
                                     "provider_confirmed": True, "manifest_files": len(files),
                                     "manifest_sha256": R.sha256_file(manifest),
                                     "archive_sha256": R.sha256_file(archive)}))
        plan = parent / "stage-plan.json"
        plan.write_text(json.dumps([{"span_id": sid, "archive": str(archive), "manifest": str(manifest),
                                    "marker": str(marker)}]))
        shutil.rmtree(root / sid)  # this span can only be read from the staged archive
        out = parent / "stage1.json"
        args = ["stage1", "--roster", str(root / "roster.json"), "--custody", str(root),
                "--rules-3-4", str(root / "rules_3_4.json"), "--out", str(out),
                "--stage-archives", str(plan), "--staging-root", str(parent / "stage")]
        return sid, files, (archive, manifest, marker), out, args

    def test_rl174_staged_span_is_recorded_by_real_stage1_cli(self):
        from tests.cadence.test_look_run import run_cli
        root = self.source_copy()
        sid, files, (archive, manifest, marker), out, args = self.staged_plan(root)
        rc, _, err = run_cli(args)
        self.assertEqual(rc, 0, err)
        self.assertEqual(read(out)["staging"], [{"span_id": sid, "archive_sha256": R.sha256_file(archive),
                                               "manifest_sha256": R.sha256_file(manifest),
                                               "marker_sha256": R.sha256_file(marker), "files_verified": len(files)}])

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
        """A leg stage 1 includes but leaves out of the energy fit: its start reading is unusable (RL-149 section 1.3:
        the last reading at or before the turn start, at most 2 s old, on a fresh power-management stamp). A failed
        read would not do it: the collector writes its row with an error and the reader drops such rows, so the
        writer-shaped way is a stale ``pm_observed_ns``, as the generator's own ``missing_start`` plant does."""
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
                status = row["values"]["status"]
                status["pm_observed_ns"] = row["started"]["monotonic_ns"] - 5_000_000_000
        journal.write_text("".join(json.dumps(row) + "\n" for row in rows))
        return key, bundle

    def test_step3_checks_timing_of_included_leg_outside_energy_fit(self):
        root = self.source_copy()
        key, bundle = self.missing_start_fan(root)
        stage1 = self.stage1(root)
        leg = next(leg for leg in stage1["legs"] if leg["leg_key"] == key)
        self.assertTrue(leg["included"])
        self.assertFalse(leg["in_energy_fit"])
        self.assertEqual(S3.custody_problems(stage1, R.span_dirs(root, [])), [])
        x = leg["segments"][3]["wall_start_s"] + 4
        gpu_hole(bundle / "power_trace.csv", x, 4.0)
        problems = S3.custody_problems(stage1, R.span_dirs(root, []))
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
        stage1, fit = (root.parent / name for name in ("D.json", "O.json"))
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
        rc, _, err = TLR._cli_subprocess(["stage2", *args, "--out", fit], repo=mini)
        self.assertEqual(rc, 0, err + TLR.LAST_RUN.get("private_stderr", ""))
        fit.unlink()
        gpu_hole(bundle / "power_trace.csv", leg["segments"][3]["wall_start_s"] + 4, 4.0)
        # An energy decoder reaching this canary would raise; the time-only custody guard must refuse first.
        path = bundle / "power_trace.csv"
        rows = path.read_text().splitlines()
        fields = rows[-1].split(",")
        fields[1] = "ENERGY_CANARY_NEVER_DECODE"
        rows[-1] = ",".join(fields)
        path.write_text("\n".join(rows) + "\n")
        # RL-194: the committed look pins its inputs. The changed trace is not its pin, so stage 2 refuses at its
        # first act: before the reservation, and before the time-only custody guard above or any decoder sees it.
        rc, stdout, err = TLR._cli_subprocess(["stage2", *args, "--out", fit], repo=mini,
                                              extra={"pin_custody": False, "twin_path": "no-twin-is-launched"})
        self.assertEqual((rc, stdout), (2, ""), err)
        self.assertRegex(err, r"^REFUSED custody pins: .*power_trace\.csv: its bytes are not its pin")
        self.assertNotIn("ENERGY_CANARY", err)
        self.assertEqual((TLR.LAST_RUN["reservation_attempts"], TLR.LAST_RUN["served"]), (0, []))
        self.assertFalse(fit.exists())

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
                    for number, row in enumerate(rows, 1):                   # the collector numbers the rows it wrote
                        row["seq"] = number
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
