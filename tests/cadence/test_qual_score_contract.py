"""RL-188 contract checks on generated rows, independent of the frozen module."""

import copy
import json
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
        legs = self.legs + [{"leg_type": "L", "N": 4096 if i % 2 else 3724, "rules": dict.fromkeys(qual.RULES, True),
                             "leg_key": f"L{i}", "span_id": "a"} for i in range(12)]
        word, decision = qual.decision(legs, self.scores, self.dates)
        baseline = {**self.base, "qualified_qualification": word}
        baseline_bytes = qual.public_bytes(baseline, self.schema, self.base)
        self.assertEqual(qual.validate_public(baseline_bytes, self.schema, self.base), baseline)
        fixed = set(baseline) - {"included_legs", "stage1_sha256", "commit"}
        for i, row in enumerate(legs[5:], 1):
            with self.subTest(leg=row["leg_key"]):
                row["rules"]["g0_released"] = False
                actual_word, actual_decision = qual.decision(legs, self.scores, self.dates)
                row["rules"]["g0_released"] = True
                bindings = {**self.base, "included_legs": self.base["included_legs"] - 1,
                            "stage1_sha256": f"{i:064x}", "commit": f"{i:040x}"}
                actual = {**bindings, "qualified_qualification": actual_word}
                raw = qual.public_bytes(actual, self.schema, bindings)
                self.assertEqual(qual.validate_public(raw, self.schema, bindings), actual)
                self.assertEqual(actual.keys(), baseline.keys())
                self.assertEqual(qual.release.dump({k: actual[k] for k in fixed}),
                                 qual.release.dump({k: baseline[k] for k in fixed}))
                self.assertEqual(actual_decision, decision)
                for field in ("stage1_sha256", "commit"):
                    self.assertNotEqual(actual[field], baseline[field])

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
