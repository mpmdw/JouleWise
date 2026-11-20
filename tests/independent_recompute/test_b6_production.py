"""RL-24 seat 7: synthetic-only production, 7b and authenticated zstd witnesses."""
import contextlib
import copy
from dataclasses import replace
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
        cls.root = Path(cls.tmp.name).resolve()
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
                               ["lines/whole_machine/qwen3-1p7b/prefill-p2048/mean_j"], 40.)
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
            meter = Path(directory).resolve()
            stream = pin["meter_streams"][0]
            (meter / Path(stream).name).write_bytes(session.inputs.read(archive / stream))
            oracle = {"disclosures": {}}
            selected = {(session.pack, cid): values for cid, values in result["_selections"].items()}
            proxy = types.SimpleNamespace(**vars(session))
            proxy.member = session.member
            proxy.reader = b6.Reader(session.pack, session.session_id, flags)
            b6.B5.add_machine(oracle, selected, {session.pack: proxy}, meter)
        self.assertEqual(result["whole_machine"], oracle["disclosures"]["whole_machine"])
        cells = oracle["disclosures"]["whole_machine"]["windows"][session.pack]["cells"]
        quantities = b6.session_quantities(result)
        labels = {"boundary", "implementation", "request_assisted_members", "request_assisted_count"}
        for cid, line in result["lines"].items():
            with self.subTest(cell=cid):
                printed, expected = line["whole_machine"], cells[cid]
                # B6 replaces the boundary sentence and adds three labels;
                # every arithmetic field, including all corners, must match.
                self.assertEqual({k: v for k, v in printed.items() if k not in labels},
                                 {k: v for k, v in expected.items() if k not in labels})
                self.assertEqual(len(printed["edge_shift_sensitivity"]["corners"]), 4)
                self.assertEqual(printed["boundary"], b6.PHASE_BOUNDARY)
                if "p42" not in cid:
                    key = "lines/whole_machine/" + b6.tag_of(b6.MODELS[session.pack]) + "/" + b6.contrast_key(cid) + "/mean_j"
                    self.assertEqual(quantities[key], expected["mean_j"])
        self.assertNotEqual(cells["df-ph-decode-qwen3-1p7b"]["mean_j"],
                            cells["df-ph-prefill-p2048-qwen3-1p7b"]["mean_j"])

    def test_option_c_second_producer_disagreement_stops_with_exit_three(self):
        from joulewise.b6_analysis_check import harvest
        original = harvest.overlap_energy
        # Change an actual second-producer energy, rather than its verdict.
        deltas = iter([.01])
        with mock.patch.object(harvest, "overlap_energy", side_effect=lambda *a: original(*a) + next(deltas, 0.)):
            rc, numbers, public, _, _ = self.execute(1)
        output = json.loads(numbers)
        self.assertFalse(output["block"]["option_c"]["pass"])
        # The gate names failed comparator rows (cold-review finding 5, commit
        # 10116d0d9), so one perturbed energy is named twice: once by
        # `harvest_energy` and once by the comparator row for the same run and phase.
        self.assertEqual(output["block"]["option_c"]["failures"],
                         ["harvest_energy:neg8-refcorpus-r01/prefill",
                          "comparator:run_phase_energy:b6-alpha-r1:neg8-refcorpus-r01/prefill"])
        self.assertFalse(output["block"]["option_c"]["comparator"]["pass"])
        self.assertIn("option_c_disagrees", {f["code"] for f in output["flags"]})
        self.assertTrue(json.loads(public)["comparison_stopped"])
        self.assertEqual(rc, 3)

    def test_option_c_checker_only_disagreement_stops_with_exit_three(self):
        from joulewise.b6_analysis_check import harvest
        original = harvest.anchor_envelope
        deltas = iter([.01])
        def changed_bound(*args):
            envelope = original(*args)
            # Only harvest_bound consumes this field; the comparison table
            # contains phase energies, which remain unchanged.
            return replace(envelope, max_abs_delta_j=envelope.max_abs_delta_j + next(deltas, 0.))
        with mock.patch.object(harvest, "anchor_envelope", side_effect=changed_bound):
            rc, numbers, public, _, _ = self.execute(1)
        output = json.loads(numbers)
        checks = output["block"]["option_c"]
        self.assertTrue(checks["comparator"]["pass"])
        self.assertEqual(len(checks["failures"]), 1)
        self.assertTrue(checks["failures"][0].startswith("harvest_bound:"), checks["failures"])
        self.assertFalse(checks["pass"])
        self.assertIn("option_c_disagrees", {f["code"] for f in output["flags"]})
        self.assertTrue(json.loads(public)["comparison_stopped"])
        self.assertEqual(rc, 3)

    def test_c3_gamma_window_midpoint_loss_has_no_pack_scoped_primary_reason(self):
        with tempfile.TemporaryDirectory(prefix="b6-gamma-window-synthetic-") as folder:
            archive, _ = build_session(Path(folder).resolve(), "GAMMA", 1, 0)
            path = archive / "derived/flags.jsonl"
            path.write_text(json.dumps({"code": "neg8.midpoint_lost", "flag_id": "synthetic-midpoint",
                "scope": {"level": "window", "plan_id": archive.name, "attempt": 1},
                "interval": {"monotonic_ns": None}}) + "\n")
            session = b6.Session(archive, [])
            self.assertNotIn("neg8.midpoint_lost_primary", session.window_codes)
            self.assertEqual(session.exclusion_check["status"], "agrees")
            compute = b6.compute_exclusions
            def pack_scoped(*args, **kwargs):
                return compute(*args, **{**kwargs, "pack_scoped": True})
            with mock.patch.object(b6, "compute_exclusions", side_effect=pack_scoped):
                check = session.check_exclusions()
            self.assertEqual(check["status"], "disagrees")
            self.assertIn("neg8.midpoint_lost_primary", check["reasons"])

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
            archive, _ = build_session(Path(folder).resolve(), "ALPHA", 1, 0)
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
        alias = archive / "synthetic-alias"
        alias.symlink_to(archive / "harvest.json")
        with self.assertRaisesRegex(InputRefusal, "input_symlink"):
            inputs.read(alias)
        directory_alias = archive / "synthetic-directory-alias"
        directory_alias.symlink_to(archive / "derived", target_is_directory=True)
        with self.assertRaisesRegex(InputRefusal, "input_symlink"):
            inputs.read(directory_alias / "roster.json")
        root_alias = self.root / "synthetic-root-alias"
        root_alias.symlink_to(archive, target_is_directory=True)
        with self.assertRaisesRegex(InputRefusal, "^input_path_invalid$"):
            AuthenticatedInputs(root_alias / "derived" / "..", pin)
        with self.assertRaisesRegex(InputRefusal, "input_symlink"):
            AuthenticatedInputs(root_alias, pin)
        ancestor = self.root / "synthetic-ancestor-alias"
        ancestor.symlink_to(archive.parent, target_is_directory=True)
        relocated = AuthenticatedInputs(ancestor / archive.name, pin)
        self.assertEqual(relocated.archive, archive)
        self.assertEqual(relocated.read(ancestor / archive.name / "harvest.json"),
                         inputs.read(archive / "harvest.json"))

    def test_compression_and_digest_refusals(self):
        archive = self.archives[0]
        pin = json.loads(self.document.read_bytes())["sessions"][archive.name]
        bad = copy.deepcopy(pin)
        del bad["compression"]
        inputs = AuthenticatedInputs(archive, bad)
        with self.assertRaisesRegex(InputRefusal, "^compression_record_missing$"):
            inputs.read(archive / pin["meter_streams"][0])
        for relocations, refusal in (({"sources": "/synthetic-absolute"}, "input_path_invalid"),
                                     ({"sources": "sources", "sources/night-custody": "sources/night-custody"},
                                      "compression_relocation_ambiguous")):
            with self.subTest(relocations=relocations):
                bad = copy.deepcopy(pin)
                bad["compression"]["relocations"] = relocations
                with self.assertRaisesRegex(InputRefusal, "^" + refusal + "$"):
                    AuthenticatedInputs(archive, bad)
        bad = copy.deepcopy(pin)
        bad["files"] = {"harvest.json": "0" * 64}
        with self.assertRaisesRegex(InputRefusal, "^input_digest_conflict$"):
            AuthenticatedInputs(archive, bad)

        # Absolute collection locators are string inputs only. An explicit,
        # unique relocation admits them without probing that old location.
        record_path = archive / pin["compression"]["path"]
        rows = [json.loads(line) for line in record_path.read_text().splitlines()]
        relocated = "".join(json.dumps({**row, "path": "/synthetic-collection/" + row["path"].removeprefix("sources/")}) + "\n"
                            for row in rows).encode()
        bad = copy.deepcopy(pin)
        bad["compression"]["sha256"] = hashlib.sha256(relocated).hexdigest()
        from joulewise import desk_compress
        read = desk_compress.read_bytes
        with mock.patch.object(desk_compress, "read_bytes", side_effect=lambda p: relocated if p == record_path else read(p)):
            with self.assertRaisesRegex(InputRefusal, "^compression_relocation_ambiguous$"):
                AuthenticatedInputs(archive, bad)
            bad["compression"]["relocations"] = {"/synthetic-collection": "sources"}
            admitted = AuthenticatedInputs(archive, bad)
            self.assertEqual(set(admitted.compressed), {row["path"] for row in
                             (json.loads(line) for line in record_path.read_text().splitlines())})

    def test_request_comparison_and_disclosure_refusals(self):
        archive = self.archives[0]
        pin = json.loads(self.document.read_bytes())["sessions"][archive.name]
        session = b6.Session(archive, [], inputs=AuthenticatedInputs(archive, pin), input_pin=pin)
        for supplied, refusal in (({}, "disclosure_coverage_missing"),
                                  ({**pin["copied_records"], "monitor_cost": []}, "disclosure_coverage_invalid"),
                                  ({**pin["copied_records"], "monitor_cost": "record"}, "disclosure_coverage_invalid"),
                                  ({**pin["copied_records"], "monitor_cost": [None]}, "disclosure_coverage_invalid")):
            with self.subTest(refusal=refusal, supplied=supplied):
                session.input_pin = {**pin, "copied_records": supplied}
                with self.assertRaisesRegex(InputRefusal, "^" + refusal + "$"):
                    b6.compute_session(session)
        session.input_pin = pin
        result = b6.compute_session(session)
        original = session.reader.raw
        record_path = archive / "withheld/meter.json"
        record = json.loads(original(record_path, "test"))
        del record["members"]["fixture-decode-r01"]
        for data, refusal in ((None, "request_comparison_record_missing"),
                              (json.dumps(record).encode(), "request_comparison_member_missing")):
            with self.subTest(refusal=refusal):
                def raw(path, scope, required=True):
                    return data if path == record_path else original(path, scope, required)
                with mock.patch.object(session.reader, "raw", side_effect=raw):
                    with self.assertRaisesRegex(InputRefusal, "^" + refusal + "$"):
                        b6.add_session_machine(session, result, result["_selections"])

    def test_listed_disclosure_record_absent_refuses_by_name(self):
        # RL-125 item 4 term 3: a copied-record file that the run-input document
        # lists and the archive lacks is a named refusal (exit 4, no output),
        # not an AttributeError at the record's decode.
        document = json.loads(self.document.read_bytes())
        archive = self.archives[0]
        absent = "derived/synthetic-absent-record.json"
        self.assertFalse((archive / absent).exists())
        document["sessions"][archive.name]["copied_records"]["monitor_cost"].append(absent)
        listed = self.root / "run-inputs-absent-record.json"
        listed.write_text(json.dumps(document))
        args = [*self.args[:self.args.index("--inputs")], "--inputs", str(listed), "--inputs-sha256", sha(listed)]
        restricted, public = self.root / "absent-numbers.json", self.root / "absent-public.json"
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = b6.main([*args, "--workers", "1", "--restricted-out", str(restricted), "--public-out", str(public)])
        self.assertEqual(rc, 4)
        self.assertEqual(stderr.getvalue(), "refused: disclosure_record_missing\n")
        self.assertFalse(restricted.exists())
        self.assertFalse(public.exists())

    def test_pinned_session_not_supplied_refuses_by_name(self):
        # RL-133 §1b: every session the run-input document pins must be supplied before any session is read.
        omitted = self.archives[1]
        args = [x for x in self.args]
        i = args.index(str(omitted))
        self.assertEqual(args[i - 1], "--session")
        del args[i - 1:i + 1]
        restricted, public = self.root / "unsupplied-numbers.json", self.root / "unsupplied-public.json"
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = b6.main([*args, "--workers", "1", "--restricted-out", str(restricted), "--public-out", str(public)])
        self.assertEqual(rc, 4)
        self.assertEqual(stderr.getvalue(), "refused: session_input_unsupplied\n")
        self.assertFalse(restricted.exists())
        self.assertFalse(public.exists())

    def test_member_pool_refuses_paths_outside_authenticated_contexts(self):
        pool = b6.MemberPool(2, [types.SimpleNamespace(archive=self.archives[0])])
        def probe(_pool):
            reader = b6.B5.Reader("ALPHA", [])
            with mock.patch.object(b6.Reader, "raw", side_effect=AssertionError("unauthenticated fallback")):
                with self.assertRaisesRegex(InputRefusal, "^input_outside_archive$"):
                    reader.raw(self.root / "outside-archive", "test")
        with mock.patch.object(b6.B5.MemberPool, "_start", probe):
            pool._start()

    def test_listed_clock_journal_requires_pin_and_is_authenticated(self):
        from .support_b6_production import seal
        with tempfile.TemporaryDirectory(prefix="b6-clock-synthetic-") as folder:
            archive, _ = build_session(Path(folder).resolve(), "ALPHA", 1, 0, n=1)
            name = "sources/synthetic/monitor/clock.jsonl"
            path = archive / name
            path.parent.mkdir(parents=True)
            path.write_text('{"synthetic": true}\n')
            pin = seal(archive)
            with self.assertRaisesRegex(InputRefusal, "^clock_journal_required$"):
                AuthenticatedInputs(archive, pin)
            with self.assertRaisesRegex(InputRefusal, "^clock_journal_required$"):
                AuthenticatedInputs(archive, {**pin, "clock_journal": "sources/wrong/monitor/clock.jsonl"})
            inputs = AuthenticatedInputs(archive, {**pin, "clock_journal": name})
            self.assertEqual(inputs.read(path), b'{"synthetic": true}\n')
            path.write_text('{"synthetic": false}\n')
            with self.assertRaisesRegex(InputRefusal, "^input_digest_mismatch$"):
                inputs.read(path)


if __name__ == "__main__":
    unittest.main()
