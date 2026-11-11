"""RL-24 seat 7: synthetic-only production, 7b and authenticated zstd witnesses."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import time
import types
import unittest
from unittest import mock

from joulewise.b6_analysis_inputs import AuthenticatedInputs, InputRefusal
from joulewise.b6_analysis_hazards import desk_hazards
from .support_b6 import b6, build_session
from .support_b6_production import production_block, sha


class Production(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(prefix="b6-production-synthetic-")
        cls.root = Path(cls.tmp.name)
        cls.archives, cls.attempts, cls.document = production_block(cls.root / "block")
        cls.args = ["block", *[x for a in cls.archives for x in ("--session", str(a))],
                    "--loop-attempts", str(cls.attempts), "--closed", "--inputs", str(cls.document),
                    "--inputs-sha256", sha(cls.document)]
        cls.r, cls.p = cls.root / "numbers.json", cls.root / "public.json"
        cls.seconds = {}
        cls.serial = cls.execute(1)

    @classmethod
    def execute(cls, workers):
        stdout, stderr = io.StringIO(), io.StringIO()
        started = time.monotonic()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = b6.main([*cls.args, "--workers", str(workers), "--restricted-out", str(cls.r), "--public-out", str(cls.p)])
        cls.seconds[workers] = time.monotonic() - started
        return rc, cls.r.read_bytes() if cls.r.exists() else b"", cls.p.read_bytes() if cls.p.exists() else b"", stdout.getvalue(), stderr.getvalue()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_blind_dry_run_exit_zero_and_independent_comparator_agrees(self):
        self.assertEqual(self.serial[0], 0, self.serial[3:])
        output = json.loads(self.serial[1])
        self.assertEqual(len(output["sessions"]), 10)
        self.assertEqual(json.loads(self.serial[2])["counting_by_pack"], {"ALPHA": 3, "BETA": 3, "GAMMA": 3})
        checks = output["block"]["option_c"]
        self.assertTrue(checks["pass"], checks)
        self.assertTrue(checks["comparator"]["pass"])
        self.assertIn("engine", checks["families"])
        self.assertIn("harvest_bound", checks["families"])
        self.assertTrue(all(r["exclusions_rederivation"]["status"] == "agrees" for r in output["sessions"].values()))
        self.assertTrue(output["inputs"]["census"][self.archives[0].name]["zstd"]["version"])
        self.assertAlmostEqual(output["sessions"][self.archives[0].name]["quantities"]
                               ["lines/whole_machine/qwen3-1p7b/prefill-p2048/mean_j"], 50.)
        b6.require_production_coverage(output["sessions"], output["block"])
        del output["sessions"][self.archives[0].name]["quantities"]["calibration/b_op_s"]
        with self.assertRaisesRegex(InputRefusal, "comparison_session_coverage_mismatch"):
            b6.require_production_coverage(output["sessions"], output["block"])

    def test_pool_and_serial_output_are_byte_identical(self):
        self.assertEqual(self.execute(2), self.serial)

    def test_loaded_b5_is_exactly_the_release_pin_and_tamper_refuses(self):
        self.assertEqual(b6.B5.loaded_sha256, b6.B5_SHA256)
        self.assertEqual(sha(b6._B5_PATH), b6.B5_SHA256)
        for name in ("add_machine", "machine_member", "sampled_gross", "phase_machine_mean",
                     "diagnostic_estimate", "reported_estimate"):
            self.assertEqual(getattr(b6.B5, name).__code__.co_filename, str(b6._B5_PATH))
        bad = self.root / "tampered.py"
        bad.write_bytes(b6._B5_PATH.read_bytes() + b"\n# changed\n")
        with self.assertRaisesRegex(InputRefusal, "b5_script_digest_mismatch"):
            b6.load_pinned_b5(bad)

    def test_7b_b6_phase_output_equals_b5_own_output_including_corners(self):
        archive = self.archives[0]
        pin = json.loads(self.document.read_bytes())["sessions"][archive.name]
        flags = []
        session = b6.Session(archive, flags, inputs=AuthenticatedInputs(archive, pin), input_pin=pin)
        result = b6.compute_session(session)
        # B5's OWN complete function and reader run a second time, directly.
        # Restore only authenticated meter bytes in a fresh synthetic scratch.
        with tempfile.TemporaryDirectory(prefix="b6-7b-witness-") as directory:
            meter = Path(directory)
            stream = pin["meter_streams"][0]
            (meter / Path(stream).name).write_bytes(session.inputs.read(archive / stream))
            oracle = {"disclosures": {}}
            selected = {(session.pack, cid): values for cid, values in result["_selections"].items()}
            proxy = types.SimpleNamespace(**vars(session))
            proxy.member = session.member
            proxy.reader = b6.Reader(session.pack, session.session_id, flags)
            b6.B5.add_machine(oracle, selected, {session.pack: proxy}, meter)
        self.assertEqual(result["whole_machine"], oracle["disclosures"]["whole_machine"])
        for cid, line in result["lines"].items():
            if "p42" in cid:
                continue
            self.assertEqual(len(line["whole_machine"]["edge_shift_sensitivity"]["corners"]), 4)
            self.assertIsNotNone(line["whole_machine"]["mean_j"])
            self.assertEqual(line["whole_machine"]["boundary"], b6.PHASE_BOUNDARY)

    def test_zst_bytes_checked_before_parser_and_bad_digest_stops(self):
        archive = self.archives[0]
        pin = json.loads(self.document.read_bytes())["sessions"][archive.name]
        inputs = AuthenticatedInputs(archive, pin)
        path = archive / pin["meter_streams"][0]
        data = inputs.read(path)
        self.assertEqual(hashlib.sha256(data).hexdigest(), inputs.compressed[str(path.relative_to(archive))])
        inputs.expected[str(path.relative_to(archive))] = "0" * 64
        reader = b6.Reader("ALPHA", "synthetic", [], inputs)
        with mock.patch.object(b6.B5, "sampled_gross", side_effect=AssertionError("parser reached")):
            with self.assertRaisesRegex(InputRefusal, "input_digest_mismatch"):
                reader.lines(path, "meter")
        with mock.patch("joulewise.b6_analysis_inputs.shutil.which", return_value=None):
            with self.assertRaisesRegex(InputRefusal, "zstd_unavailable"):
                inputs.read(path)
        compressed_plist = next(p for p in archive.glob("sources/claim-runs/*/raw/powermetrics.plist.zst"))
        logical = Path(str(compressed_plist)[:-4])
        inputs.expected[str(logical.relative_to(archive))] = "0" * 64
        with mock.patch.object(b6.B5, "plist_records", side_effect=AssertionError("unverified plist parsed")) as parser:
            with self.assertRaisesRegex(InputRefusal, "input_digest_mismatch"):
                b6.B5.Member(logical.parent.parent, logical.parent.parent.name, reader, .04)
            parser.assert_not_called()

    def test_c3_disagreement_and_reducer_disagreement_are_stops(self):
        with tempfile.TemporaryDirectory(prefix="b6-c3-synthetic-") as folder:
            archive, _ = build_session(Path(folder), "ALPHA", 1, 0)
            acceptance = archive / "derived/b6-acceptance.json"
            doc = json.loads(acceptance.read_bytes())
            doc["excluding"].append({"code": "thermal.os_level_nonzero", "scope": "member", "run_id": "fixture-decode-r01"})
            acceptance.write_text(json.dumps(doc))
            flags = []
            session = b6.Session(archive, flags)
            self.assertEqual(session.exclusion_check["status"], "disagrees")
            self.assertTrue(any(b6.stops_comparison(f, {session.session_id: session}) for f in flags))
            summary = archive / "sources/claim-runs/fixture-decode-r02/summary_metrics.json"
            doc = json.loads(summary.read_bytes())
            doc["phase_energy_j"]["decode"] += 1
            summary.write_text(json.dumps(doc))
            session.member("fixture-decode-r02", compared=True)
            self.assertTrue(any(f["code"] == "stored_energy_mismatch" and b6.stops_comparison(f, {}) for f in flags))

    def test_registered_precision_and_placeholder_refusal(self):
        self.assertEqual(b6.decimals_for("reported/qwen3-8b/decode/mean_j", b6.RATIFIED_COMPARISON_DECIMALS), 5)
        self.assertEqual(b6.decimals_for("reported/qwen3-8b/decode/per_token_j", b6.RATIFIED_COMPARISON_DECIMALS), 8)
        path = self.root / "placeholder.json"
        path.write_text(json.dumps({"decimals": [["*_j", 5]], "nested": {"placeholder": True}}))
        with self.assertRaisesRegex(InputRefusal, "placeholder_print_precision"):
            b6.load_spec(path)

    def test_desk_power_and_processor_alternative_follow_registered_sizes(self):
        archive = self.archives[0]
        pin = json.loads(self.document.read_bytes())["sessions"][archive.name]
        session = b6.Session(archive, [], inputs=AuthenticatedInputs(archive, pin), input_pin=pin)
        sizing = json.loads((b6.ROOT_DIR / "configs/b6/recompute/hazard_sizing.json").read_bytes())
        # Mutate the decoded measurement seam only. No authenticated source
        # file or study object is edited; these are independent closed forms.
        original = session.reader.lines
        def busy(path, scope):
            rows = original(path, scope)
            if scope == "contention_journal":
                rows[0]["values"]["outside_total_cpu_s_per_s"] = 1.
            return rows
        with mock.patch.object(session.reader, "lines", side_effect=busy), \
             mock.patch("joulewise.b6_analysis_hazards.idle_graphics_power", return_value=1.):
            hazards = desk_hazards(session, sizing)
        self.assertEqual(len(hazards["power_removed"]), 100)
        self.assertEqual(len(hazards["processor_alternative_removed"]), 100)
        row = next(iter(hazards["records"].values()))
        self.assertAlmostEqual(row["E_add_j"], 5.432 * (10. - .54))
        self.assertFalse(hazards["primary_processor_exclusion"])
        self.assertAlmostEqual(row["P_star_w"] * row["T_phase_s"], .475)

    def test_harvest_pin_and_archive_escape_fail_before_read(self):
        archive = self.archives[0]
        pin = json.loads(self.document.read_bytes())["sessions"][archive.name]
        bad = copy.deepcopy(pin)
        bad["harvest_sha256"] = "0" * 64
        with self.assertRaisesRegex(InputRefusal, "input_digest_mismatch"):
            AuthenticatedInputs(archive, bad)
        inputs = AuthenticatedInputs(archive, pin)
        with self.assertRaisesRegex(InputRefusal, "input_path_invalid"):
            inputs.read(archive / ".." / "external-file")
        alias = self.root / "synthetic-alias"
        alias.symlink_to(archive.parent, target_is_directory=True)
        with self.assertRaisesRegex(InputRefusal, "input_symlink"):
            AuthenticatedInputs(alias / archive.name, pin)


if __name__ == "__main__":
    unittest.main()
