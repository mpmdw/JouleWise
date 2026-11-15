"""The span-reference leg (kit v1.1; RL-150 R1 part 2; design doc section 14.5): the law's G0 shapes, the
runner's roles, and the leg runtime consuming the span's first leg's capture through W1's verifier (on the
synthetic backend). No model, sensor, host setting or energy is touched."""
from __future__ import annotations

import io
import json
import math
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from joulewise.cadence import desk, kit as kitmod, kit_v11, legs as legsmod
from scripts import cadence_legs_runner as runner
from tests.cadence.test_kit_v11 import NEW_WINDOW, SIZES, law, local, v11_kit

TMP = os.environ.get("TMPDIR")


def span_kit(**template):
    return v11_kit(seed_law=law(g0_shapes=["own", "span"]), **{"leg_budget_s": 1660, **template})


def warm_span_share(kit, rosters):
    """Span-shape legs among the block's warm legs (every leg that is not first in its span)."""
    shape = {leg["leg_id"]: leg["g0_shape"] for leg in kit["legs"]}
    warm = [leg_id for roster in rosters for leg_id in roster[1:]]
    return sum(shape[i] == "span" for i in warm), len(warm)


class SpanLaw(unittest.TestCase):
    def test_at_least_half_of_the_warm_legs_and_balanced_by_size(self):
        for seed in range(2026111401, 2026111421):
            own = kit_v11.generate_legs("c-id", law(master_seed=seed), {"decode_tokens": 4096})
            span = kit_v11.generate_legs("c-id", law(master_seed=seed, g0_shapes=["own", "span"]),
                                         {"decode_tokens": 4096})
            # v1.1 and v1.1a lists of one block differ in g0_shape only.
            self.assertEqual([{k: v for k, v in leg.items() if k != "g0_shape"} for leg in span],
                             [{k: v for k, v in leg.items() if k != "g0_shape"} for leg in own])
            self.assertEqual(span[0]["g0_shape"], "own")
            for size in SIZES:
                warm = [leg for leg in span[1:] if leg["prefill_tokens"] == size]
                self.assertEqual(sum(leg["g0_shape"] == "span" for leg in warm), math.ceil(len(warm) / 2))
            kit = {"legs": span}
            ids = [leg["leg_id"] for leg in span]
            n_span, n_warm = warm_span_share(kit, [ids])                  # one span
            self.assertEqual((n_span, n_warm), (6, 11))
            n_span, n_warm = warm_span_share(kit, [ids[:3], ids[3:]])     # the class A pilot, then the rest
            self.assertGreaterEqual(2 * n_span, n_warm)

    def test_the_validator_takes_span_legs(self):
        kit = span_kit()
        self.assertEqual(sum(leg["g0_shape"] == "span" for leg in kit["legs"]), 6)
        kit["legs"][0]["g0_shape"] = "span"
        with self.assertRaises(kitmod.KitError):
            kit_v11.validate_kit(kit, batch_window=NEW_WINDOW)


class Roles(unittest.TestCase):
    def test_first_leg_captures_later_span_legs_consume_own_legs_keep_v1_specs(self):
        kit = span_kit()
        specs = legsmod.leg_specs(kit)
        shape = {leg["leg_id"]: leg["g0_shape"] for leg in kit["legs"]}
        for i, spec in enumerate(specs):
            if shape[spec["leg_id"]] == "own":
                self.assertEqual(spec["schema"], legsmod.LEG_SPEC_SCHEMA)
                self.assertNotIn("g0_role", spec)
            else:
                self.assertEqual((spec["schema"], spec["g0_shape"], spec["g0_role"]),
                                 (legsmod.LEG_SPEC_SCHEMA_V11, "span", "consume" if i else "capture"))
        # A roster that starts on a span leg: that leg is the span's source, so it captures.
        first_span = next(leg["leg_id"] for leg in kit["legs"][1:] if leg["g0_shape"] == "span")
        start = [leg["leg_id"] for leg in kit["legs"]].index(first_span)
        roster = [leg["leg_id"] for leg in kit["legs"][start:]]
        specs = legsmod.leg_specs(kit, roster)
        self.assertEqual(specs[0]["g0_role"], "capture")
        self.assertTrue(all(s.get("g0_role") in (None, "consume") for s in specs[1:]))

    def test_spec_validation(self):
        base = legsmod.leg_specs(span_kit())[0]
        good = {**base, "schema": legsmod.LEG_SPEC_SCHEMA_V11, "g0_shape": "span", "g0_role": "consume"}
        self.assertIs(legsmod.validate_leg_spec(good), good)
        for bad, fragment in (({"g0_shape": "own"}, "is a span leg's"), ({"g0_role": "observe"}, "g0_role one of"),
                              ({"quiet_s": 5}, "quiet_s"), ({"g0_extra": 1}, "unknown key 'g0_extra'")):
            with self.assertRaises(legsmod.PlanError) as ctx:
                legsmod.validate_leg_spec({**good, **bad})
            self.assertTrue(any(fragment in p for p in ctx.exception.problems), ctx.exception.problems)
        missing = {k: v for k, v in good.items() if k != "g0_role"}
        with self.assertRaises(legsmod.PlanError):
            legsmod.validate_leg_spec(missing)
        # A v1 spec may not carry a role.
        with self.assertRaises(legsmod.PlanError):
            legsmod.validate_leg_spec({**base, "g0_role": "consume"})

    def test_consumer_budget_and_plan(self):
        kit = span_kit()
        plan = legsmod.plan_span(kit, t0_epoch=local("2026-11-17T02:40"), windows=[NEW_WINDOW])
        for leg in plan["legs"]:
            own = math.ceil(legsmod.leg_expected_s({**leg, "g0_role": "capture"}))
            self.assertEqual(leg["budget_s"], own + (391 if leg.get("g0_role") == "consume" else 0))
            # A consumer's G0 at its 1,200 s cap alone stays under 1.5 x its budget.
            if leg.get("g0_role") == "consume":
                self.assertLess(legsmod.leg_expected_s(leg) - legsmod.SPAN_G0_S + 1200, 1.5 * leg["budget_s"])
        self.assertEqual(plan["time_model"]["span_g0_s"], legsmod.SPAN_G0_S)
        self.assertEqual(plan["worst_case_s"], 40950)
        self.assertLessEqual(max(leg["budget_s"] for leg in plan["legs"]), kit["span_template"]["leg_budget_s"])
        with self.assertRaises(legsmod.PlanError):   # the v1 leg budget ceiling cannot hold a consumer
            legsmod.plan_span(span_kit(leg_budget_s=1260), t0_epoch=local("2026-11-17T02:40"), windows=[NEW_WINDOW])


class MockSpan(unittest.TestCase):
    def run_mock(self, kit, legs=None):
        tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name) / "span"
        rc, summary, stops, deps = runner.run_mock(kit=kit, kit_sha256="f" * 64, output=out,
                                                   t0_epoch=local("2026-11-17T02:40"), windows=[NEW_WINDOW],
                                                   leg_ids=legs)
        return out, rc, summary, stops, deps, json.loads((out / runner.RECEIPT_NAME).read_text())

    def test_consumers_get_the_first_legs_accepted_attempt(self):
        kit = span_kit()
        out, rc, summary, stops, deps, receipt = self.run_mock(kit)
        self.assertEqual((rc, stops), (0, []), receipt.get("error"))
        shape = {leg["leg_id"]: leg["g0_shape"] for leg in kit["legs"]}
        for leg_id, source in deps.fake.span_references:
            if shape[leg_id] == "span" and leg_id != "L001":
                self.assertEqual(source, out / "legs/L001/runtime")
            else:
                self.assertIsNone(source)
            record = json.loads((out / "legs" / leg_id / "leg_record.json").read_text())
            self.assertEqual(record["result"]["g0_role"], "consume" if source else "capture")
            self.assertEqual(record["result"]["g0_reference_source"], "mock-L001" if source else f"mock-{leg_id}")
        legs = {leg["leg_id"]: leg for leg in receipt["legs"]}
        consumer = next(i for i in shape if shape[i] == "span")
        self.assertEqual(legs[consumer]["span_reference"], {"leg_id": "L001", "dir": "legs/L001/runtime", "attempt": 1,
                                                            "redone": False, "excluded": False})
        # The desk: a cell section, the source by attempt, and no mark on a clean first leg.
        desk_summary = json.loads((out / "desk/desk_summary.json").read_text())
        self.assertEqual(desk_summary["span_reference"], {"leg_id": "L001", "attempt": 1, "consumers": 6,
                                                          "consistent": True, "marks": []})
        table = (out / "desk/JOURNAL-TABLE.md").read_text()
        self.assertIn("## Cells and G0 references (kit v1.1)", table)
        self.assertIn("| consume | L001 attempt 1 |", table)
        self.assertNotIn("MARK:", table)
        # The desk projection is unchanged (leg-summary-v1).
        for path in (out / runner.DESK_BUNDLE).glob("legs/*/leg_summary.json"):
            self.assertLessEqual(set(json.loads(path.read_text())), desk.LEG_SUMMARY_KEYS)

    def test_a_later_span_takes_its_own_first_leg(self):
        kit = span_kit()
        rest = [leg["leg_id"] for leg in kit["legs"][3:]]
        out, rc, summary, stops, deps, receipt = self.run_mock(kit, rest)
        self.assertEqual(rc, 0, receipt.get("error"))
        sources = {source for _, source in deps.fake.span_references if source is not None}
        self.assertEqual(sources, {out / "legs" / rest[0] / "runtime"})

    def test_the_desk_marks_a_reference_from_a_redo_or_an_excluded_leg(self):
        kit = span_kit()
        for name, kw, attempt, marks in (
                ("redo", {"contaminate": ["L001"]}, 2, ["reference from a redo"]),
                ("excluded", {"g0_timeout": ["L001"]}, 1, ["reference from an excluded leg"])):
            tmp = tempfile.TemporaryDirectory(dir=TMP)
            self.addCleanup(tmp.cleanup)
            out = Path(tmp.name) / name
            rc, summary, stops, _ = runner.run_mock(kit=kit, kit_sha256="f" * 64, output=out,
                                                    t0_epoch=local("2026-11-17T02:40"), windows=[NEW_WINDOW], **kw)
            self.assertEqual(rc, 0, name)
            self.assertEqual(summary["span_reference"]["marks"], marks, name)
            self.assertEqual(summary["span_reference"]["attempt"], attempt, name)
            table = (out / "desk/JOURNAL-TABLE.md").read_text()
            self.assertIn(f"**MARK: {marks[0]}**", table)
            self.assertIn(f"| consume | L001 attempt {attempt} |", table)

    def test_a_redone_first_leg_is_the_source_by_its_accepted_attempt(self):
        kit = span_kit()
        tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name) / "span"
        rc, _, _, deps = runner.run_mock(kit=kit, kit_sha256="f" * 64, output=out,
                                         t0_epoch=local("2026-11-17T02:40"), windows=[NEW_WINDOW],
                                         contaminate=["L001"])
        self.assertEqual(rc, 0)
        self.assertTrue((out / "legs/L001/runtime.rejected1").is_dir())
        self.assertEqual({s for _, s in deps.fake.span_references if s is not None}, {out / "legs/L001/runtime"})


class LegRuntimeConsumes(unittest.TestCase):
    """The real leg runtime on the synthetic backend: L001 captures, L002 consumes L001's capture."""

    @classmethod
    def setUpClass(cls):
        from tests.align import r1_synthetic as rs
        from tests.align.test_r1_runtime import write_soak
        cls.tmp = tempfile.TemporaryDirectory(dir=TMP)
        cls.root = Path(cls.tmp.name)
        cls.config = rs.synthetic_config(cls.root / "cfg")
        cls.soak = write_soak(cls.root / "soak.json")
        code, cls.first = cls.call(cls.root / "span/legs/L001/runtime", cls.spec("L001"))
        assert code == 0, code

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @classmethod
    def spec(cls, leg_id, role=None, **kw):
        spec = {"schema": legsmod.LEG_SPEC_SCHEMA, "campaign_id": "cl-test-11", "leg_id": leg_id, "seed": 7,
                "start_band": "q0", "prefill_tokens": 2000, "prefill_chars": legsmod.prefill_chars(2000),
                "decode_tokens": 128, "quiet_s": 0}
        if role:
            spec.update(schema=legsmod.LEG_SPEC_SCHEMA_V11, g0_shape="span", g0_role=role)
        spec.update(kw)
        path = cls.root / f"{leg_id}-{role}.json"
        path.write_text(json.dumps(spec))
        return path

    @classmethod
    def call(cls, out, spec_path, span=None):
        from joulewise.align.apple import cadence_leg
        buffer = io.StringIO()
        argv = ["--config", str(cls.config), "--leg-spec", str(spec_path), "--r1-kind", "cadence-leg",
                "--output", str(out), "--soak-reference", str(cls.soak)]
        argv += ["--span-reference", str(span)] if span is not None else []
        code = cadence_leg.main(argv, stdout=buffer)
        return code, (json.loads(buffer.getvalue()) if code == 0 else None)

    def source_record(self):
        bundle = self.root / "span/legs/L001/runtime" / self.first["bundle"]
        return json.loads((bundle / "outputs/align_window_reference.json").read_text()), bundle.name

    def test_the_first_leg_captures(self):
        record, run_id = self.source_record()
        self.assertEqual(record["status"], "captured")
        self.assertEqual((self.first["g0_shape"], self.first["g0_role"], self.first["g0_reference_source"]),
                         ("own", "capture", run_id))

    def test_a_consumer_judges_its_g0_against_the_first_legs_capture(self):
        from joulewise.align.apple import r1_runtime as rt
        out = self.root / "span/legs/L002/runtime"
        code, result = self.call(out, self.spec("L002", "consume"), span=self.root / "span/legs/L001/runtime")
        self.assertEqual(code, 0, json.loads((out / rt.CUSTODY_NAME).read_text()).get("error"))
        record, run_id = self.source_record()
        self.assertEqual((result["g0_shape"], result["g0_role"], result["g0_reference_source"], result["leg_status"]),
                         ("span", "consume", run_id, "complete"))
        self.assertEqual(result["g0_reference_record_sha256"], record["record_sha256"])
        self.assertIsNone(self.first["g0_reference_record_sha256"])
        episode = json.loads((out / result["bundle"] / "outputs/align_episode.json").read_text())
        g0 = next(r for r in episode["hardware"]["thermal"]["intervals"] if r["kind"] == "G0")
        self.assertEqual((g0["reference"]["fast_c"], g0["reference"]["slow_c"], g0["reference"]["source_member"]),
                         (record["fast_c"], record["slow_c"], run_id))
        # The consumer writes no capture of its own: its G0 reference is the span's, never a fall-back.
        self.assertFalse((out / result["bundle"] / "outputs/align_window_reference.json").exists())
        legsmod.guard_projection({k: result[k] for k in ("g0_shape", "g0_role", "g0_reference_source")}, "t")

    def test_a_span_leg_that_is_first_captures(self):
        out = self.root / "span2/legs/L004/runtime"
        code, result = self.call(out, self.spec("L004", "capture"))
        self.assertEqual(code, 0)
        self.assertEqual((result["g0_shape"], result["g0_role"]), ("span", "capture"))
        self.assertTrue((out / result["bundle"] / "outputs/align_window_reference.json").is_file())

    def test_refusals_before_any_work(self):
        from joulewise.align.apple import r1_runtime as rt
        source = self.root / "span/legs/L001/runtime"
        cases = {"no-source": (self.spec("L005", "consume"), None, "needs --span-reference"),
                 "capture-with-source": (self.spec("L006", "capture"), source, "consumer (g0_role consume) only"),
                 "own-with-source": (self.spec("L007"), source, "consumer (g0_role consume) only"),
                 "missing-dir": (self.spec("L008", "consume"), self.root / "span/legs/L099/runtime",
                                 "no readable result"),
                 "other-span": (self.spec("L011", "consume"), source, "not a leg attempt of this span")}
        for name, (spec, span, fragment) in cases.items():
            out = (self.root / "other-span/legs/L011/runtime" if name == "other-span"
                   else self.root / "span/legs" / f"R-{name}" / "runtime")
            code, _ = self.call(out, spec, span=span)
            self.assertEqual(code, rt.EXIT_REFUSED, name)
            self.assertIn(fragment, json.loads((out / rt.CUSTODY_NAME).read_text())["error"], name)
            self.assertFalse((out / "runs").exists(), name)

    def test_a_tampered_or_consumer_source_refuses(self):
        from joulewise.align.apple import r1_runtime as rt
        source = self.root / "span/legs/L001/runtime"
        # 1. The source result edited after its custody closed.
        tampered = self.root / "span/legs/T1/runtime"
        shutil.copytree(source, tampered)
        value = json.loads((tampered / rt.RESULT_NAME).read_text())
        value["g0_reference_source"] = "x"
        (tampered / rt.RESULT_NAME).write_text(json.dumps(value))
        # 2. The source's reference record edited (W1's verifier re-derives it from the journal).
        forged = self.root / "span/legs/T2/runtime"
        shutil.copytree(source, forged)
        record_path = forged / self.first["bundle"] / "outputs/align_window_reference.json"
        record = json.loads(record_path.read_text())
        record["fast_c"] -= 5.0
        record_path.write_text(json.dumps(record))
        # 3. A consumer's attempt offered as the source.
        consumer = self.root / "span/legs/T3/runtime"
        code, _ = self.call(consumer, self.spec("L009", "consume"), span=source)
        self.assertEqual(code, 0)
        for name, src, fragment in (("tampered", tampered, "bound by complete runtime custody"),
                                    ("forged", forged, "window_reference"),
                                    ("consumer", consumer, "did not capture")):
            out = self.root / "span/legs" / f"S-{name}" / "runtime"
            code, _ = self.call(out, self.spec("L010", "consume"), span=src)
            self.assertEqual(code, rt.EXIT_REFUSED, name)
            self.assertIn(fragment, json.loads((out / rt.CUSTODY_NAME).read_text())["error"], name)


class RunnerThroughTheLegRuntime(unittest.TestCase):
    """The span driver with its leg step wired to the real leg runtime (in process, synthetic backend)."""

    def test_three_legs_the_two_warm_ones_consume_l001(self):
        from unittest.mock import patch
        from joulewise.align.apple import cadence_leg
        from tests.align import r1_synthetic as rs
        from tests.align.test_r1_runtime import write_soak
        kit = v11_kit(seed_law=law(n_legs=3, g0_shapes=["own", "span"]), legs_per_span=3, leg_budget_s=1660)
        self.assertEqual([leg["g0_shape"] for leg in kit["legs"]], ["own", "span", "span"])
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            clock = runner.FakeClock(local("2026-11-17T02:40"))
            out = root / "span"
            deps = runner.mock_deps(out, clock)
            deps.max_span_s = runner.max_span_s()

            def soak(soak_dir, *a):
                Path(soak_dir).mkdir(parents=True)
                return write_soak(Path(soak_dir) / "soak_reference.json")

            def leg(attempt_dir, spec_path, soak_reference, cap_s, feeds, work_remaining, span_reference=None):
                small = {**json.loads(Path(spec_path).read_text()), "prefill_tokens": 2000,
                         "prefill_chars": legsmod.prefill_chars(2000), "decode_tokens": 128}
                path = Path(attempt_dir).parent / "leg_spec.synthetic.json"
                path.write_text(json.dumps(small))
                argv = ["--config", str(config), "--leg-spec", str(path), "--r1-kind", "cadence-leg",
                        "--output", str(attempt_dir), "--soak-reference", str(soak_reference)]
                argv += ["--span-reference", str(span_reference)] if span_reference is not None else []
                if cadence_leg.main(argv, stdout=io.StringIO()):
                    raise runner.LegRuntimeError("leg runtime refused")
                return runner.accepted_result(attempt_dir)
            deps.run_soak, deps.run_leg = soak, leg
            plan = legsmod.plan_span(kit, t0_epoch=clock.time(), windows=[NEW_WINDOW])
            rc = runner.run_span(kit=kit, kit_sha256="f" * 64, output=out, deadline=runner.launch_deadline(plan),
                                 windows=[NEW_WINDOW], deps=deps)
            receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
            self.assertEqual(rc, 0, receipt.get("error"))
            records = {i: json.loads((out / f"legs/{i}/leg_record.json").read_text()) for i in ("L001", "L002", "L003")}
            source = records["L001"]["result"]["g0_reference_source"]
            self.assertTrue(source)
            self.assertEqual([(r["result"]["g0_role"], r["result"]["g0_reference_source"]) for r in records.values()],
                             [("capture", source), ("consume", source), ("consume", source)])
            self.assertEqual([r["spec"].get("g0_role") for r in records.values()], [None, "consume", "consume"])
            summaries = [json.loads((out / f"legs/{i}/leg_summary.json").read_text()) for i in ("L001", "L002", "L003")]
            self.assertEqual([s["g0_outcome"] for s in summaries], ["released"] * 3)

    def test_production_argv_carries_the_span_reference_for_a_consumer_only(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            inputs = root / "inputs.json"
            inputs.write_text(json.dumps({"WP15": {"runtime_entrypoint": [
                "scripts/align_r1_runtime.py", "--config", "configs/align/v4/r1_runtime.json"]}}))
            with patch("scripts.run_align_r1_smoke.AgentFeed"), patch("scripts.run_align_r1_smoke.MeterFeed"), \
                 patch("scripts.run_align_r1_smoke.VolumeFeed"):
                deps = runner.production_deps(inputs=inputs, pmset_bin="fake", output=root / "span")
            argvs = []

            def child(**kw):
                argvs.append(kw["argv"])
                Path(kw["argv"][kw["argv"].index("--output") + 1]).mkdir(parents=True)
                return {"rc": 0}
            source = root / "span/legs/L001/runtime"
            with patch.object(runner, "run_child", side_effect=child), \
                 patch.object(runner, "accepted_result", return_value={"kind": "cadence-leg"}):
                for leg_id, kw in (("L001", {}), ("L002", {"span_reference": source})):
                    leg_dir = root / "span/legs" / leg_id
                    leg_dir.mkdir(parents=True)
                    deps.run_leg(leg_dir / "runtime", leg_dir / "leg_spec.json", root / "soak.json", 2700, [],
                                 lambda: 1e9, **kw)
            self.assertNotIn("--span-reference", argvs[0])
            self.assertEqual(argvs[1][argvs[1].index("--span-reference") + 1], str(source))


class CommittedDev03SpanKit(unittest.TestCase):
    """The dev-03 draft on kit v1.1 (class A): the v1.1a draft's block with span-reference legs."""
    KITS = runner.ROOT / "docs/process/cadence/kits"

    def load(self, name):
        return kitmod.load_kit(self.KITS / name, batch_window=NEW_WINDOW)

    def test_same_block_as_the_v11a_draft_but_the_g0_shapes(self):
        kit, _ = self.load("cl-dev-03.v1.1.json")
        fallback, _ = self.load("cl-dev-03.v1.1a.json")
        self.assertEqual(kit["campaign_id"], fallback["campaign_id"])
        self.assertEqual(kit["seed_law"], {**fallback["seed_law"], "g0_shapes": ["own", "span"]})
        strip = lambda legs: [{k: v for k, v in leg.items() if k != "g0_shape"} for leg in legs]  # noqa: E731
        self.assertEqual(strip(kit["legs"]), strip(fallback["legs"]))
        self.assertEqual(set(kit["frozen"]["paths"]), set(fallback["frozen"]["paths"]))
        self.assertIn("pilot_counted", [r["id"] for r in kit["inclusion_rules"]])
        self.assertNotIn("pilot_counted", [r["id"] for r in fallback["inclusion_rules"]])

    def test_the_counted_smoke_exercises_a_consumer_and_the_share_holds(self):
        kit, _ = self.load("cl-dev-03.v1.1.json")
        ids = [leg["leg_id"] for leg in kit["legs"]]
        pilot = legsmod.leg_specs(kit, ids[:3])
        self.assertEqual(sorted(s["prefill_tokens"] for s in pilot), SIZES)
        self.assertIn("consume", [s.get("g0_role") for s in pilot])
        for rosters in ([ids], [ids[:3], ids[3:]]):
            n_span, n_warm = warm_span_share(kit, rosters)
            self.assertGreaterEqual(2 * n_span, n_warm, rosters)
        t0 = local("2026-11-17T02:40")
        whole = legsmod.plan_span(kit, t0_epoch=t0, windows=[NEW_WINDOW], max_span_s=runner.max_span_s())
        self.assertEqual(whole["worst_case_s"], 40950)
        self.assertLessEqual(max(leg["budget_s"] for leg in whole["legs"]), kit["span_template"]["leg_budget_s"])

    def test_frozen_paths_hash_at_the_frozen_commit(self):
        import subprocess
        kit, _ = self.load("cl-dev-03.v1.1.json")
        have = subprocess.run(["git", "-C", str(runner.ROOT), "cat-file", "-e", kit["frozen"]["commit"] + "^{commit}"],
                              capture_output=True)
        if have.returncode:
            self.skipTest("frozen commit not in this clone")
        self.assertEqual(kitmod.verify_frozen(kit, runner.ROOT), [])
        # The span leg's bytes are in the kit's frozen closure, and no gate module moved since the pilot.
        dev01, _ = kitmod.load_kit(self.KITS / "cl-dev-01.json")
        for path in ("joulewise/align/apple/thermal_gates.py", "joulewise/align/apple/r1_runtime.py",
                     "joulewise/align/apple/workload.py"):
            self.assertEqual(kit["frozen"]["paths"][path], dev01["frozen"]["paths"][path], path)
        self.assertNotEqual(kit["frozen"]["paths"]["joulewise/align/apple/cadence_leg.py"],
                            dev01["frozen"]["paths"]["joulewise/align/apple/cadence_leg.py"])


if __name__ == "__main__":
    unittest.main()
