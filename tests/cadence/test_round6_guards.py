"""Behavioral controls for the eleven round-6 Mythos guard mutants.

All numbers and files here are synthetic. Direct gates isolate the ruled condition from unrelated
pin failures, and the coefficient CLI control injects an invalid writer result before any output write.
"""
from __future__ import annotations

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from joulewise.cadence_looks import manifest as M
from joulewise.cadence_looks import time_fields as TF

try:
    from joulewise.cadence_looks import fit_interim as F
    from scripts import cadence_look_run as R
    from tests.cadence import test_predict as TP
except ModuleNotFoundError as exc:  # dependency-free shards still exercise the non-numeric guards
    if exc.name != "numpy":
        raise
    F = R = TP = None

REPO = Path(__file__).resolve().parents[2]


class ClockFitGuards(unittest.TestCase):
    def test_native_projection_keeps_malformed_excluded_rows_and_skips_type_t_runtime(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "runner_receipt.json").write_text(json.dumps({"roster": ["L001", "L002"]}))
            for lid, kind in (("L001", "A"), ("L002", "T")):
                leg = root / "legs" / lid
                bundle = leg / "runtime/bundle"
                (bundle / "raw").mkdir(parents=True)
                (leg / "leg_record.json").write_text(json.dumps({"spec": {"leg_type": kind},
                                                               "result": {"bundle": "bundle"}}))
                (bundle / "rich_telemetry.jsonl").write_text('{"gpu_energy": 999}\n')
                (bundle / "raw/powermetrics.plist").write_bytes(b"synthetic truncated frame")
            # An A already excluded for an unreadable turn can still carry a blind digest. T runtime
            # is never opened, even if the receipt contains a bundle locator for it.
            original = Path.open
            def guarded(path, *args, **kwargs):
                if "/L002/runtime/" in str(path):
                    raise AssertionError("type-T runtime opened")
                return original(path, *args, **kwargs)
            with mock.patch.object(Path, "open", guarded):
                digest = M.native_pm_files(root)
                files = M.nonenergy_files(root)
            self.assertEqual(set(digest), {"legs/L001/runtime/bundle"})
            self.assertFalse(any("L002/runtime/" in path for path in files))
            self.assertRegex(next(iter(digest.values())), r"^[0-9a-f]{64}$")

    def test_a_negative_clock_fit_excursion_counts(self):
        # A fitted line may put the bad side below zero; 2.5 s must still cross the 2 s clause.
        times = {"clock_fit": {"excess_latency_ms_max": 100, "excess_latency_ms_min": -2500}}
        self.assertEqual(TF.clock_fit_excess_s(times), 2.5)
        self.assertGreater(TF.clock_fit_excess_s(times), TF.CLOCK_FIT_EXCESS_MAX_S)

    def test_an_overlapping_stream_need_not_span_the_entire_leg(self):
        span = TF.SpanMeter.__new__(TF.SpanMeter)
        def stream(a, b, excess):
            return {"present": True, "aligned": True, "t": [a, b],
                    "clock_fit": {"excess_latency_ms_max": excess * 1000, "excess_latency_ms_min": 0}}
        # The noisy stream ends inside the leg, while another stream supplies its end.
        span.times = [stream(0, 4, 3), stream(0, 10, 0.1), stream(20, 30, 9)]
        self.assertEqual(span.excess_over(3, 7), 3)
        self.assertEqual(span.excess_over(5, 7), 0.1)


class LedgerAndManifestGuards(unittest.TestCase):
    H1, H2, RO, VE = "1" * 64, "2" * 64, "3" * 64, "4" * 64

    def entry(self, sha, exclusions=(), ruling="RL-999"):
        return {"stage1_sha256": sha, "roster_sha256": self.RO, "verdicts_sha256": self.VE,
                "ruling": ruling, "ruled_exclusions": [{"leg_key": leg, "rule": rule} for leg, rule in exclusions]}

    @contextlib.contextmanager
    def gate(self, row, raw=b"{}", history=()):
        with tempfile.TemporaryDirectory(prefix="r6-gate-") as td:
            root = Path(td)
            row = dict(row, look_id="lm-interim-01", manifest_path="manifest.json", sha256=hashlib.sha256(raw).hexdigest())
            (root / "manifest.json").write_bytes(raw)
            with mock.patch.object(M, "committed_ledger", return_value=("a" * 40, "refs/remotes/origin/main", {"looks": [row]})), \
                 mock.patch.object(M, "stage1_history", return_value=list(history)), \
                 mock.patch.object(M, "_ledger_history_rows", return_value=[], create=True), \
                 mock.patch.object(M, "_git", return_value=(0, raw, "")):
                yield root, row

    def test_a_later_rerun_cannot_drop_an_earlier_exclusion(self):
        old = ("dev-01-s01/L001", "km003c_clean")
        new = ("dev-02-s01/L001", "sidecar_coverage")
        e1 = self.entry(self.H1, [old])
        e2 = self.entry(self.H2, [new], "RL-1000")
        row = dict(status="committed", roster_sha256=self.RO, verdicts_sha256=self.VE, stage1_superseded=[e1, e2])
        history = [M._triple(e1), M._triple(e2)]
        with self.gate(row, history=history) as (root, r):
            with self.assertRaises(M.ManifestError) as ctx:
                M.require_inputs_committed(root, "lm-interim-01", r["sha256"], roster_sha256=self.RO,
                                           verdicts_sha256=self.VE, ruled_exclusions={new[0]: [new[1], "RL-1000"]})
            self.assertIn("with every earlier one", str(ctx.exception))
        e2 = self.entry(self.H2, [old, new], "RL-1000")
        row["stage1_superseded"] = [e1, e2]
        with self.gate(row, history=history) as (root, r):
            M.require_inputs_committed(root, "lm-interim-01", r["sha256"], roster_sha256=self.RO,
                                       verdicts_sha256=self.VE,
                                       ruled_exclusions={k: [v, "RL-1000"] for k, v in (old, new)})

    def test_the_current_commitment_cannot_be_superseded(self):
        row = dict(status="stage1_committed", stage1_sha256=self.H1, roster_sha256=self.RO,
                   verdicts_sha256=self.VE, stage1_superseded=[self.entry(self.H1)])
        doc = {"code_sha256": {"input:roster_sha256": self.RO, "input:rules_3_4_sha256": self.VE}, "legs": []}
        with self.gate(row) as (root, _):
            with self.assertRaises(M.ManifestError) as ctx:
                M.require_stage1_committed(root, "lm-interim-01", self.H1, stage1_doc=doc)
            self.assertIn("current stage-1 commitment is listed as superseded", str(ctx.exception))
        row.pop("stage1_superseded")
        with self.gate(row) as (root, _):
            M.require_stage1_committed(root, "lm-interim-01", self.H1, stage1_doc=doc)

    def test_a_superseding_entry_names_an_actual_ruling_id(self):
        self.assertEqual(M.superseded_problems([self.entry(self.H1)], "row"), [])
        for ruling in ("approved", "RL-999 extra", "RL-999\n", "", None):
            self.assertTrue(M.superseded_problems([self.entry(self.H1, ruling=ruling)], "row"), repr(ruling))

    def test_the_ruled_q11_value_requires_its_evidence(self):
        doc = json.loads((REPO / "docs/process/cadence/looks/lm-interim-01.json").read_text())
        doc["status"] = "draft"
        M.validate_manifest(doc)
        next(d for d in doc["decisions"] if d["id"] == "drift_tripwire").pop("evidence")
        with self.assertRaises(M.ManifestError) as ctx:
            M.validate_manifest(doc)
        self.assertIn("0.08 cites RL-173", str(ctx.exception))

    def test_freeze_two_requires_the_coefficient_schema(self):
        doc = json.loads((REPO / "docs/process/cadence/looks/lm-interim-01.json").read_text())
        doc["status"] = "draft"
        M.validate_manifest(doc)
        doc["freeze2"].pop("schema")
        with self.assertRaises(M.ManifestError) as ctx:
            M.validate_manifest(doc)
        self.assertIn("freeze2.schema", str(ctx.exception))

    def test_step_three_requires_a_real_stage_ones_custody(self):
        from joulewise.cadence_looks import step3_roster as S3
        stage1 = {"synthetic": False, "roster": {"spans": [{"span_id": "dev-01-s01", "custody": None}]},
                  "legs": [{"leg_key": "dev-01-s01/L001", "span_id": "dev-01-s01", "included": True,
                            "role": "fit", "leg_type": "A"}]}
        problems = S3.custody_problems(stage1, [{"key": "dev-01-s01/L001"}], lambda _: Path("/synthetic-unused"))
        self.assertTrue(problems)
        self.assertIn("no custody record", "; ".join(problems))
        stage1["synthetic"] = True
        self.assertEqual(S3.custody_problems(stage1, [], lambda _: Path("/synthetic-unused")), [])


@unittest.skipIf(F is None, "numpy is not installed; required look-fit job executes this class")
class CoefficientGuards(unittest.TestCase):
    def test_writer_authenticates_the_stage_one_bytes(self):
        _, s1, sha, fit, _ = TP.run("noisy")
        F.write_coefficients(s1, sha, fit, TP.MANIFEST_SHA)
        with self.assertRaisesRegex(F.LookInputError, "does not match the hash"):
            F.write_coefficients(s1, "0" * 64, fit, TP.MANIFEST_SHA)

    def test_predict_refuses_an_inactive_readings_existing_column(self):
        li, s1, _, _, co = TP.run("noisy")
        keys = {leg["leg_key"] for leg in s1["legs"] if leg["in_energy_fit"]}
        leg = next(leg for leg in li["legs"] if leg["leg_key"] in keys)
        soak = next(s["soak_reference_tv0h_c"] for s in li["spans"] if s["span_id"] == leg["span_id"])
        F.predict(co, leg, soak)
        reading = next(n for n, h in F.HEAT_OF.items() if h in co["channels"][F.CHANNELS[0]]["columns"])
        co["active_readings"][reading] = False
        with self.assertRaisesRegex(F.LookInputError, "inactive reading's column"):
            F.predict(co, leg, soak)

    def test_cli_refuses_a_writer_result_that_breaks_the_pinned_schema(self):
        # Inject a broken writer result to show that the read/write boundary, independently of the
        # writer's own checks, enforces the schema before writing either artifact.
        def stage2(a):
            a._stage1_doc = {}
            a._prepared_fit = None
            return {"synthetic": True}
        stderr = io.StringIO()
        with mock.patch.object(M, "verify_pins", return_value={}), \
             mock.patch.object(R, "cmd_stage2", side_effect=stage2), \
             mock.patch.object(R, "sha256_file", return_value="a" * 64), \
             mock.patch.object(F, "write_coefficients", return_value={"schema": "invalid"}), \
             mock.patch.object(R, "write_canonical") as write, \
             mock.patch.object(R, "_VERIFIED", []), \
             contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            rc = R.main(["stage2", "--stage1", "synthetic-D.json", "--stage1-sha256", "b" * 64,
                         "--energy", "synthetic-E.json", "--out", "synthetic-O.json",
                         "--coefficients-out", "synthetic-C.json", "--manifest", "synthetic-manifest.json", "--allow-draft"])
        self.assertEqual(rc, 2, stderr.getvalue())
        self.assertIn("coefficient file does not pass its schema", stderr.getvalue())
        write.assert_not_called()
