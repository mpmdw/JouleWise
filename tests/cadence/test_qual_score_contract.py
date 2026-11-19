"""RL-188 contract checks on generated rows, independent of the frozen module."""

import copy
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.cadence_looks import qual_score as qual


class QualificationContractTests(unittest.TestCase):
    def test_default_cli_is_installed(self):
        result = subprocess.run([sys.executable, "-B", str(qual.ROOT / "joulewise/cadence_looks/qual_score.py"),
                                 "--help"], cwd=qual.ROOT, capture_output=True, check=True)
        for name in (b"stage1", b"stage2", b"validate-public"):
            self.assertIn(name, result.stdout)
        for schema in (qual.STAGE_SCHEMA, qual.OUTPUT_SCHEMA):
            self.assertIs(json.loads((qual.ROOT / schema).read_bytes())["additionalProperties"], False)

    def test_terminal_context_uses_produced_tokens(self):
        for cap, lo, gaps, context in ((3724, 3583, 140, 3653.5), (3151, 3071, 79, 3111)):
            turn = {"prefill_tokens": 2000, "decode_tokens": cap, "segments": [{"edge_hi": lo}]}
            with self.subTest(cap=cap):
                self.assertEqual(qual.terminal_edges(turn), {
                    "edge_lo": lo, "edge_hi": cap - 1, "gaps": gaps, "context_tokens": 2000 + context,
                })
        self.assertIsNone(qual.terminal_edges({"decode_tokens": 4096}))

    def test_final_command_checks_exact_registration_bytes(self):
        main = qual.named_commit(qual.ROOT, "HEAD")
        raw = qual.authenticated_registration(qual.ROOT, main, qual.REGISTRATION, qual.REGISTRATION_SHA)
        pins = [{**pin, "sha256": qual.digest((qual.ROOT / pin["path"]).read_bytes())}
                for pin in qual.manifest_pins(json.loads(raw))]
        candidate = qual.filled_manifest(raw, pins)
        qual.validate_final_command(raw, candidate)
        with self.assertRaises(qual.Refusal):
            qual.validate_final_command(raw, candidate + b" ")

    def setUp(self):
        self.schema = json.loads((qual.ROOT / qual.OUTPUT_SCHEMA).read_bytes())
        self.base = {"look_id": qual.LOOK, "manifest_sha256": "a" * 64, "commit": "a" * 40,
                     "stage1_sha256": "b" * 64, "coefficients_sha256": "c" * 64,
                     "development_config_sha256": "d" * 64, "qualification_config_sha256": "e" * 64,
                     "included_legs": 17, "type_m_residual": "not_run", "stage2_error": "no"}
        self.dates = {"a": "2031-02-01", "b": "2031-02-02", "c": "2031-02-03"}
        rules = dict.fromkeys(qual.RULES, True)
        self.legs = [{"leg_type": "A", "N": 4096, "rules": rules.copy(), "leg_key": f"A{i}", "span_id": span}
                     for i, span in enumerate(("a", "a", "b", "c", "c"))]
        self.scores = {f"A{i}": {"gpu_rail": {"residual": value,
                                             "prefixes": {"3724": {"residual": value + 0.25}}}}
                       for i, value in enumerate((-8, -4, 0.5, 3, 10))}

    def test_private_day_prints_and_public_gate(self):
        for days, count, numeric_interval in ((1, 1, False), (2, 2, True), (3, 3, True)):
            dates = {span: min(i, count) for i, span in enumerate(self.dates, 1)}
            word, report = qual.decision(self.legs, self.scores, dates)
            with self.subTest(days=days):
                self.assertEqual(word, "yes" if days == 3 else "not_evaluable")
                self.assertEqual(report["n_days"], days)
                self.assertIsInstance(report["estimate"], float)
                self.assertEqual(report["ci90"] is not None, numeric_interval)
        word, report = qual.decision(self.legs[:2], self.scores, self.dates)
        self.assertEqual((word, report["estimate"], report["ci90"]), ("not_evaluable", None, None))
        scores = copy.deepcopy(self.scores)
        for channels in scores.values():
            channels["gpu_rail"]["residual"] = 2.0
        word, report = qual.decision(self.legs, scores, self.dates)
        self.assertEqual((word, report["estimate"], report["ci90"]), ("not_evaluable", None, None))

    def test_each_l_exclusion_preserves_the_decision_and_eight_bound_public_fields(self):
        from tests.cadence import test_qual_score_acceptance as fixture

        self.assertFalse(os.environ.get("QUAL_TEST_COMMAND"), "A2 requires the default scorer command")
        self.assertEqual(fixture.SOURCE, qual.ROOT)
        self.assertEqual(fixture.PRIVATE, "RESTRICTED")
        fixed = ("look_id", "manifest_sha256", "coefficients_sha256", "development_config_sha256",
                 "qualification_config_sha256", "qualified_qualification", "type_m_residual", "stage2_error")
        decision_fields = ("estimate", "ci90", "sd_long", "sd_short", "n_legs", "n_days", "differences")

        def run_world(world, included):
            fixture.admit(self, world)
            execution = fixture.git(world.repo, "rev-parse", "HEAD").strip().decode("ascii")
            stage1 = fixture.git(world.repo, "show", f"{execution}:{fixture.STAGE}")
            ledger = json.loads(fixture.git(world.repo, "show", f"{execution}:{fixture.LEDGER}"))
            row, = (item for item in ledger["looks"] if item["look_id"] == fixture.LOOK)
            stage1_sha = fixture.sha(stage1)
            blind = json.loads(stage1)
            count = blind["counts"]["included_legs"]
            self.assertEqual(world.stage.read_bytes(), stage1)
            self.assertEqual(row["stage1_sha256"], stage1_sha)
            self.assertIs(type(count), int)
            self.assertEqual(count, len(included))

            result = fixture.launch(world, "stage2")
            if result.returncode == 2:
                fixture.read_trace(self, world)
                self.assertFalse(world.private.exists())
                self.assertFalse(world.public.exists())
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""), result.stderr)
            report = fixture.records(self, world)
            self.assertEqual(report.keys(), set(fixed) | {"included_legs", "stage1_sha256", "commit"})
            self.assertEqual(report["included_legs"], count)
            self.assertEqual(report["stage1_sha256"], stage1_sha)
            self.assertEqual(report["commit"], execution)

            decision = fixture.obj(world.private / "scores.json")["decision"]
            numbers = {field: decision[field] for field in decision_fields}
            self.assertIsInstance(numbers["ci90"], list)
            self.assertEqual(len(numbers["ci90"]), 2)
            self.assertIsInstance(numbers["differences"], dict)
            decision_legs = [leg for leg in included if leg["leg_type"] == "A" and leg["N"] == 4096]
            self.assertEqual(numbers["differences"].keys(), {leg["leg_key"] for leg in decision_legs})
            self.assertIs(type(numbers["n_legs"]), int)
            self.assertIs(type(numbers["n_days"]), int)
            self.assertEqual(numbers["n_legs"], len(decision_legs))
            self.assertEqual(numbers["n_days"], len({blind["dates"][leg["span_id"]] for leg in decision_legs}))
            values = (numbers["estimate"], *numbers["ci90"], numbers["sd_long"], numbers["sd_short"],
                      *numbers["differences"].values())
            for value in values:
                self.assertIn(type(value), (int, float))
                self.assertTrue(math.isfinite(value))
            return report, numbers

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base_world = fixture.World(root / "base").init()
            base_roster = fixture.relation(base_world)
            base_ids = {leg["leg_key"] for leg in base_roster}
            l_ids = [leg["leg_key"] for leg in base_roster if leg["leg_type"] == "L"]
            self.assertEqual(len(set(l_ids)), len(l_ids))
            self.assertEqual(len(l_ids), 12)
            base, base_numbers = run_world(base_world, base_roster)
            base_fixed = fixture.wire({key: base[key] for key in fixed})
            compared = 0
            for index, key in enumerate(l_ids, 1):
                with self.subTest(excluded_leg=key):
                    world = fixture.World(root / f"exclusion-{index}").init(excluded=[key])
                    roster = fixture.relation(world)
                    self.assertEqual({leg["leg_key"] for leg in roster}, base_ids - {key})
                    report, numbers = run_world(world, roster)
                    self.assertEqual(report.keys(), base.keys())
                    self.assertEqual(fixture.wire({field: report[field] for field in fixed}), base_fixed)
                    self.assertEqual(report["included_legs"], base["included_legs"] - 1)
                    self.assertNotEqual(report["stage1_sha256"], base["stage1_sha256"])
                    self.assertNotEqual(report["commit"], base["commit"])
                    self.assertEqual(numbers, base_numbers)
                    compared += 1
            self.assertEqual(compared, 12)

    def test_writer_refuses_invalid_sources_before_publication_and_publishes_exclusively(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reservation = root / "reserved"
            reservation.mkdir()
            destination = root / "PUBLIC.json"
            record = {**self.base, "qualified_qualification": "yes"}
            for bad in (dict(record, included_legs=17.0), dict(record, included_legs=True),
                        dict(record, commit="f" * 40), dict(record, leak=1)):
                with self.subTest(record=bad), self.assertRaises(qual.Refusal):
                    qual.publish_public(destination, reservation, bad, self.schema, self.base)
                self.assertFalse(destination.exists())
                self.assertEqual(list(reservation.iterdir()), [])
            qual.publish_public(destination, reservation, record, self.schema, self.base)
            self.assertEqual(qual.validate_public(destination.read_bytes(), self.schema, self.base), record)
            with self.assertRaises(FileExistsError):
                qual.publish_public(destination, reservation, dict(record, qualified_qualification="no"),
                                    self.schema, self.base)
            self.assertEqual(qual.validate_public(destination.read_bytes(), self.schema, self.base), record)
            self.assertEqual(list(reservation.iterdir()), [])

    def test_validate_public_uses_the_committed_blind_sources(self):
        from tests.cadence import test_qual_score_acceptance as fixture

        with tempfile.TemporaryDirectory() as tmp:
            world = fixture.World(Path(tmp)).init()
            fixture.admit(self, world)
            candidate = world.root / "candidate.json"
            report = {**fixture.bindings(world), "qualified_qualification": "not_evaluable"}
            fixture.put(candidate, report)
            run = fixture.launch(world, "validate-public", ["--candidate", str(candidate)])
            self.assertEqual((run.returncode, run.stdout, run.stderr), (0, b"", b""))
            self.assertEqual(candidate.read_bytes(), fixture.wire(report))
            self.assertFalse(world.public.exists())
            self.assertFalse(world.private.exists())
            fixture.put(candidate, dict(report, included_legs=report["included_legs"] - 1))
            run = fixture.launch(world, "validate-public", ["--candidate", str(candidate)])
            self.assertEqual(run.returncode, 2)
            fixture.read_trace(self, world)
