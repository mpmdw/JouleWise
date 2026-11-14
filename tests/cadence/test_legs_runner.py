"""Campaign runner ``cadence-legs-v1``: the library, the mock span end to end, the leg runtime on the
synthetic backend, and the launcher registration. No model, sensor, host setting or energy is touched."""
from __future__ import annotations

from datetime import datetime
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise.cadence import desk, kit as kitmod, legs as legsmod
from scripts import cadence_legs_runner as runner, launch_align_r0 as launcher

TMP = os.environ.get("TMPDIR")
ZONE = legsmod.LOCAL_ZONE
NEW_WINDOW = [((2, 0), (2, 35))]           # RL-149 section 2.9 item 4
OLD_WINDOW = [((11, 45), (13, 15))]        # ruling 8 as on the base today


def local(text):
    return datetime.fromisoformat(text).replace(tzinfo=ZONE).timestamp()


def campaign_kit(n_legs=12, bands=("q0",), validate=True, **template):
    law = {"method": "sha256-v1", "master_seed": 2026111499, "n_legs": n_legs, "bands": list(bands)}
    defaults = {"prefill_tokens": legsmod.ANCHOR_PREFILL_TOKENS, "decode_tokens": 4096}
    tpl = {"timezone": "America/Los_Angeles", "t0_local": "13:20", "end_by_local": "00:45", "legs_per_span": 12,
           "soak_s": 1950, "fixed_overhead_s": 1200, "leg_budget_s": 1260, "leg_worst_case_s": 2700, "redo_quota": 2}
    tpl.update(template)
    kit = {
        "schema": kitmod.SCHEMA, "campaign_id": "cl-test-01", "title": "Synthetic campaign kit for the runner tests",
        "ruling": {"id": "RL-149 §2", "authorizes_spans": True},
        "frozen": {"commit": "a" * 40, "paths": {"scripts/cadence_legs_runner.py": "1" * 64}},
        "runner": {"kind": "cadence-legs-v1", "entry": "scripts/cadence_legs_runner.py",
                   "stage_journal": "chain-stages.jsonl"},
        "model": "mlx-community/Qwen3.8-27B-8bit", "leg_defaults": defaults, "seed_law": law,
        "legs": kitmod.generate_legs("cl-test-01", law, defaults),
        "inclusion_rules": [{"id": "g0_released", "text": "Its G0 released."}],
        "stop_rules": {"instrument_fault": True, "refusal": True, "contaminated_redos_max": 3,
                       "contaminated_redos_scope": "span", "band_unreachable_max": 2,
                       "band_unreachable_scope": "span", "leg_time_factor": 1.5},
        "span_template": tpl,
        "checklist": [{"id": k, "kind": k, **({"args": {"min_gb": 40}} if k == "disk_free_gb" else {})}
                      for k in kitmod.CHECK_KINDS],
        "looks": [], "desk": {"adapter": "leg-summary-v1"},
    }
    return kitmod.validate_kit(kit) if validate else kit


# --------------------------------------------------------------------------
# Library
# --------------------------------------------------------------------------
class LegSpecTests(unittest.TestCase):
    def test_anchor_maps_exactly_and_sizes_scale(self):
        self.assertEqual(legsmod.prefill_chars(19458), 40000)
        self.assertEqual(legsmod.prefill_chars(9729), 20000)

    def test_specs_follow_the_kit_and_the_roster(self):
        kit = campaign_kit()
        specs = legsmod.leg_specs(kit, ["L001", "L002", "L003"])
        self.assertEqual([s["leg_id"] for s in specs], ["L001", "L002", "L003"])
        self.assertEqual({s["prefill_chars"] for s in specs}, {40000})
        self.assertEqual({s["quiet_s"] for s in specs}, {0})
        self.assertEqual(specs[0]["seed"], kit["legs"][0]["seed"])
        self.assertEqual(len(legsmod.leg_specs(kit)), 12)
        for bad, why in ((["L002", "L001"], "seeded order"), (["L001", "L001"], "twice"), (["L099"], "not kit legs"),
                         ([], "no legs")):
            with self.assertRaisesRegex(legsmod.PlanError, why):
                legsmod.leg_specs(kit, bad)

    def test_spec_validation_is_closed_and_refuses_a_condition_word(self):
        spec = legsmod.leg_specs(campaign_kit(), ["L001"])[0]
        for change, why in (({"extra": 1}, "unknown key"), ({"quiet_s": 300}, "band recipe"),
                            ({"prefill_chars": 1}, "anchor ratio"), ({"start_band": "warm"}, "start_band"),
                            ({"decode_tokens": 5000}, "decode_tokens"), ({"campaign_id": "benign"}, "condition")):
            with self.assertRaisesRegex(legsmod.PlanError, why):
                legsmod.validate_leg_spec({**spec, **change})

    def test_unknown_band_has_no_recipe(self):
        with self.assertRaisesRegex(legsmod.PlanError, "no recipe"):
            legsmod.leg_specs(campaign_kit(bands=("cold",)))


class PlanTests(unittest.TestCase):
    def test_plan_sizes_the_deadline_from_the_roster(self):
        kit = campaign_kit()
        t0 = local("2026-11-15T13:20")
        plan = legsmod.plan_span(kit, t0_epoch=t0, windows=NEW_WINDOW, leg_ids=["L001", "L002", "L003"])
        self.assertEqual(plan["worst_case_s"], 1950 + 1200 + (3 + 2) * 2700)
        self.assertEqual(plan["deadline_epoch_s"], t0 + plan["worst_case_s"])
        self.assertEqual([leg["budget_s"] for leg in plan["legs"]], [1251] * 3)
        self.assertEqual(plan["expected_s"], 1950 + 1200 + 3 * 1251)
        full = legsmod.plan_span(kit, t0_epoch=t0, windows=NEW_WINDOW)
        self.assertEqual(full["worst_case_s"], 1950 + 1200 + 14 * 2700)
        self.assertLessEqual(full["expected_s"], 5.1 * 3600)        # RL-149 2.3: planned for about 5 h

    def test_anchor_budget_is_the_measured_leg(self):
        spec = legsmod.leg_specs(campaign_kit(), ["L001"])[0]
        # The model's 11-13 check: 1,155 s at a 114 s G0 against 1,158 s measured.
        self.assertAlmostEqual(legsmod.leg_expected_s(spec) - 209 + 114, 1155, delta=1.0)

    def test_plan_refuses_a_worst_case_that_meets_the_blackout_and_long_rosters(self):
        kit = campaign_kit()
        with self.assertRaisesRegex(legsmod.PlanError, "meets a batch blackout"):
            legsmod.plan_span(kit, t0_epoch=local("2026-11-15T18:00"), windows=NEW_WINDOW)
        legsmod.plan_span(kit, t0_epoch=local("2026-11-15T02:40"), windows=NEW_WINDOW)   # a night span clears it
        with self.assertRaisesRegex(legsmod.PlanError, "launch ceiling"):
            legsmod.plan_span(kit, t0_epoch=local("2026-11-15T13:20"), windows=NEW_WINDOW, max_span_s=3600)
        small = campaign_kit(legs_per_span=3, end_by_local="18:00")
        with self.assertRaisesRegex(legsmod.PlanError, "legs_per_span"):
            legsmod.plan_span(small, t0_epoch=local("2026-11-15T13:20"), windows=NEW_WINDOW)
        tight = campaign_kit(leg_budget_s=1000)
        with self.assertRaisesRegex(legsmod.PlanError, "leg_budget_s"):
            legsmod.plan_span(tight, t0_epoch=local("2026-11-15T13:20"), windows=NEW_WINDOW, leg_ids=["L001"])

    def test_batch_admission(self):
        inside = local("2026-11-15T02:10")
        self.assertEqual(legsmod.leg_start_delay(inside, NEW_WINDOW), 25 * 60)
        self.assertEqual(legsmod.leg_start_delay(local("2026-11-15T02:35"), NEW_WINDOW), 0)
        self.assertEqual(legsmod.leg_start_delay(local("2026-11-15T01:59"), NEW_WINDOW), 0)
        # A soak may not overlap it: 1,950 s from 01:30 would; it waits to 02:35.
        self.assertEqual(legsmod.interval_delay(local("2026-11-15T01:30"), 1950, NEW_WINDOW), 65 * 60)
        self.assertEqual(legsmod.interval_delay(local("2026-11-15T13:20"), 1950, NEW_WINDOW + OLD_WINDOW), 0)
        self.assertEqual(legsmod.interval_delay(local("2026-11-15T11:30"), 1950, NEW_WINDOW + OLD_WINDOW), 105 * 60)
        self.assertEqual(legsmod.parse_window("02:00-02:35"), NEW_WINDOW[0])
        for bad in ("2:00-2:35", "02:35-02:00", "02:00"):
            with self.assertRaises(ValueError):
                legsmod.parse_window(bad)

    def test_dst_day_keeps_wall_times(self):
        start, end = next((s, e) for s, e in legsmod.window_epochs(local("2026-11-01T12:00"), NEW_WINDOW)
                          if datetime.fromtimestamp(s, ZONE).date().isoformat() == "2026-11-01")
        self.assertEqual(datetime.fromtimestamp(start, ZONE).strftime("%H:%M"), "02:00")
        self.assertEqual(datetime.fromtimestamp(end, ZONE).strftime("%H:%M"), "02:35")


class ProjectionTests(unittest.TestCase):
    def spec(self):
        return legsmod.leg_specs(campaign_kit(), ["L001"])[0]

    def result(self, **kw):
        base = {"leg_status": "complete", "g0_released": True, "g0_outcome": "released", "g0_wait_s": 150.0,
                "decode_cap_reached": True, "ac_powermode": {"value": 0}, "os_level_max": 0, "pm_nominal": True}
        return {**base, **kw}

    def test_summary_is_the_desk_allowlist_and_admission(self):
        attempts = [{"wall_s": 1300.0, "contaminated": True, "redo_reason": "cpu_load"},
                    {"wall_s": 1200.0, "contaminated": False, "redo_reason": None}]
        s = legsmod.leg_summary(spec=self.spec(), budget_s=1250, attempts=attempts, accepted=self.result(),
                                started_epoch_s=1.0, ended_epoch_s=2.0)
        self.assertLessEqual(set(s), desk.LEG_SUMMARY_KEYS)
        self.assertEqual((s["attempts"], s["contaminated_redos"], s["redo_reasons"], s["wall_s"], s["admitted"]),
                         (2, 1, ["cpu_load"], 1200.0, True))
        for change in ({"g0_released": False}, {"decode_cap_reached": False}, {"leg_status": "incomplete"},
                       {"ac_powermode": {"value": 2}}):
            self.assertFalse(legsmod.leg_summary(spec=self.spec(), budget_s=1250, attempts=attempts[1:],
                                                 accepted=self.result(**change), started_epoch_s=1.0,
                                                 ended_epoch_s=2.0)["admitted"])
        last_dirty = [{"wall_s": 1200.0, "contaminated": True, "redo_reason": "cpu_load"}]
        self.assertFalse(legsmod.leg_summary(spec=self.spec(), budget_s=1250, attempts=last_dirty,
                                             accepted=self.result(), started_epoch_s=1.0, ended_epoch_s=2.0)["admitted"])

    def test_guard_refuses_energy_keys_and_condition_values(self):
        for doc in ({"decode_energy_j": 1.0}, {"x": {"power_w": 1}}, {"slot": 1}, {"transcript": "t"},
                    {"note": "benign"}, {"note": ["sabotage"]}):
            with self.assertRaises(legsmod.LeakRefusal):
                legsmod.guard_projection(doc, "t")
        legsmod.guard_projection({"note": "benign"}, "t", values=False)   # key-only mode

    def test_meter_health_reads_only_header_and_trailer(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            path = Path(td) / "stream-0001.jsonl"
            # The middle line is not JSON: a parser that read sample lines would fail.
            path.write_text(json.dumps({"k": "h", "status": "streaming"}) + "\n" + "{not json, a sample\n"
                            + json.dumps({"k": "t", "polls": 100, "bad": 0, "usb_errors": 0, "elapsed_s": 10.0}) + "\n")
            health = legsmod.meter_health([path], started=True, stop_record={"proven_stopped": True})
            self.assertEqual(health, {"present": True, "proven_stopped": True, "bad_polls": 0, "usb_errors": 0,
                                      "polls": 100, "elapsed_s": 10.0})
            path.write_text(json.dumps({"k": "h", "status": "absent"}) + "\n" + json.dumps({"k": "t"}) + "\n")
            self.assertFalse(legsmod.meter_health([path], started=True, stop_record=None)["present"])

    def test_stage_journal_lines_have_the_probe_keys(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            clock = runner.FakeClock(1000.0)
            journal = legsmod.StageJournal(Path(td) / "chain-stages.jsonl", clock)
            started = journal.start("L001.a1", "leg", 2700)
            clock.sleep(10)
            journal.end("L001.a1", "leg", 0, started, 2700)
            rows = [json.loads(x) for x in (Path(td) / "chain-stages.jsonl").read_text().splitlines()]
            for row in rows:
                self.assertLessEqual({"stage_id", "kind", "rc", "started_epoch_s", "ended_epoch_s"}, set(row))
            self.assertEqual((rows[0]["rc"], rows[1]["rc"], rows[1]["ended_epoch_s"]), (None, 0, 1010.0))


class KitValidatorTests(unittest.TestCase):
    def test_ruling_may_name_its_section(self):
        kit = campaign_kit()
        for good in ("RL-149", "RL-149 §2", "RL-149 §2.4"):
            kitmod.validate_kit({**kit, "ruling": {"id": good, "authorizes_spans": True}})
        for bad in ("RL-149 2", "RL-149 §", "RL-149 §2 extra"):
            with self.assertRaisesRegex(kitmod.KitError, "ruling.id"):
                kitmod.validate_kit({**kit, "ruling": {"id": bad, "authorizes_spans": True}})

    def test_blackout_is_a_parameter(self):
        night = campaign_kit(validate=False, t0_local="02:40", end_by_local="14:10")
        with self.assertRaisesRegex(kitmod.KitError, "11:45-13:15"):
            kitmod.validate_kit(night)
        kitmod.validate_kit(night, batch_window=NEW_WINDOW[0])
        with self.assertRaisesRegex(kitmod.KitError, "02:00-02:35"):
            kitmod.validate_kit(campaign_kit(validate=False, t0_local="18:00", end_by_local="06:00"),
                                batch_window=NEW_WINDOW[0])


# --------------------------------------------------------------------------
# The mock span, end to end
# --------------------------------------------------------------------------
class MockSpanTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=TMP)
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_mock(self, name="span", kit=None, t0="2026-11-15T13:20", **kw):
        kit = kit or campaign_kit()
        out = self.root / name
        rc, summary, stops, deps = runner.run_mock(kit=kit, kit_sha256="f" * 64, output=out, t0_epoch=local(t0),
                                                   windows=NEW_WINDOW, **kw)
        receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
        return out, rc, summary, stops, deps, receipt

    def test_full_span_runs_soak_then_every_leg_and_the_desk_is_clean(self):
        out, rc, summary, stops, deps, receipt = self.run_mock()
        self.assertEqual(rc, 0, receipt.get("error"))
        self.assertEqual(stops, [])
        self.assertEqual([leg["leg_id"] for leg in summary["legs"]], [f"L{i:03d}" for i in range(1, 13)])
        self.assertTrue(all(leg["admitted"] for leg in summary["legs"]))
        self.assertEqual(receipt["span_result"], {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": False,
                                                  "outcome": "MEASURED_OK", "verdict": "12/12 legs run"})
        names = [s["name"] for s in receipt["steps"]]
        self.assertEqual(names[:5], ["deadline", "frozen", "night_agents", "ac_power", "condition13"])
        self.assertLess(names.index("dwell"), names.index("plan"))
        self.assertLess(names.index("plan"), names.index("soak"))
        self.assertLess(names.index("soak"), names.index("L001.a1"))
        # Close: restore after the last leg, then the feeds stop in reverse order.
        self.assertEqual(names[names.index("L012.a1") + 1:names.index("L012.a1") + 5],
                         ["restore", "stop-volumes", "stop-meter", "stop-agents"])
        self.assertEqual(deps.host.calls[-1], "restore")
        # Exactly one soak; legs in the kit's seeded order; one attempt each.
        self.assertEqual(names.count("soak"), 1)
        self.assertEqual(deps.fake.calls, [f"L{i:03d}" for i in range(1, 13)])
        # Stage stamps: a start and an end line per step.
        stages = [json.loads(x) for x in (out / "chain-stages.jsonl").read_text().splitlines()]
        self.assertEqual(len(stages), 2 * len(receipt["steps"]))
        self.assertEqual({s["stage_id"] for s in stages if s["kind"] == "leg"}, {f"L{i:03d}.a1" for i in range(1, 13)})
        self.assertTrue(all(s["rc"] == 0 for s in stages if s["event"] == "end"))
        # The span stays inside its plan.
        plan = json.loads((out / runner.PLAN_NAME).read_text())
        self.assertLess(receipt["ended"]["epoch_s"], plan["deadline_epoch_s"])

    def test_the_desk_bundle_is_exactly_the_allowlist_and_carries_no_energy(self):
        out, rc, *_ = self.run_mock()
        bundle = out / runner.DESK_BUNDLE
        files = sorted(p.relative_to(bundle).as_posix() for p in bundle.rglob("*") if p.is_file())
        self.assertEqual(files, sorted(["span/meter.json", "span/result.json",
                                        *(f"legs/L{i:03d}/leg_summary.json" for i in range(1, 13))]))
        deny = re.compile(r"(?i)energy|joule|watt|power_w|_j\"|slot|transcript|benign|sabotage|condition")
        for path in bundle.rglob("*.json"):
            self.assertIsNone(deny.search(path.read_text()), path)
        meter = json.loads((bundle / "span/meter.json").read_text())
        self.assertEqual((meter["present"], meter["bad_polls"], meter["usb_errors"]), (True, 0, 0))
        for summary in bundle.glob("legs/*/leg_summary.json"):
            self.assertLessEqual(set(json.loads(summary.read_text())), desk.LEG_SUMMARY_KEYS)

    def test_pilot_roster_is_the_first_three_legs(self):
        out, rc, summary, stops, deps, receipt = self.run_mock(leg_ids=["L001", "L002", "L003"])
        self.assertEqual(rc, 0, receipt.get("error"))
        self.assertEqual(deps.fake.calls, ["L001", "L002", "L003"])
        self.assertEqual(receipt["span_result"]["verdict"], "3/3 legs run")

    def test_load_redo_keeps_the_rejected_attempt_and_quota_is_per_span(self):
        out, rc, summary, stops, deps, receipt = self.run_mock(contaminate=["L002", "L004", "L006"])
        self.assertEqual(rc, 0, receipt.get("error"))
        legs = {leg["leg_id"]: leg for leg in summary["legs"]}
        self.assertEqual((legs["L002"]["attempts"], legs["L002"]["contaminated_redos"], legs["L002"]["admitted"]),
                         (2, 1, True))
        self.assertTrue((out / "legs/L002/runtime.rejected1").is_dir())
        self.assertTrue((out / "legs/L002/runtime").is_dir())
        self.assertEqual(legs["L004"]["attempts"], 2)
        # The quota (2) is spent: L006's contaminated attempt is kept, not redone, and not admitted.
        self.assertEqual((legs["L006"]["attempts"], legs["L006"]["contaminated_redos"], legs["L006"]["admitted"]),
                         (1, 1, False))
        self.assertEqual(receipt["load_redos_used"], 2)
        self.assertEqual([s["code"] for s in stops], ["CONTAMINATED_REDOS"])   # 3 in the span (RL-149 2.4)

    def test_g0_timeout_is_recorded_and_the_span_goes_on(self):
        out, rc, summary, stops, deps, receipt = self.run_mock(g0_timeout=["L003"])
        self.assertEqual(rc, 0, receipt.get("error"))
        legs = {leg["leg_id"]: leg for leg in summary["legs"]}
        self.assertEqual((legs["L003"]["g0_outcome"], legs["L003"]["admitted"], legs["L003"]["band_reached"]),
                         ("timeout", False, False))
        self.assertEqual(len(summary["legs"]), 12)
        self.assertEqual(stops, [])             # one overtime leg is not a stop (RL-149 2.4 needs two)

    def test_a_leg_runtime_failure_stops_the_span_and_still_closes(self):
        kit = campaign_kit()
        out = self.root / "fail"
        clock = runner.FakeClock(local("2026-11-15T13:20"))
        deps = runner.mock_deps(out, clock)
        real = deps.run_leg

        def failing(attempt_dir, *a):
            if Path(attempt_dir).parent.name == "L002":
                raise runner.LegRuntimeError("L002: leg runtime exit 3")
            return real(attempt_dir, *a)
        deps.run_leg = failing
        deps.max_span_s = runner.max_span_s()
        plan = legsmod.plan_span(kit, t0_epoch=clock.time(), windows=NEW_WINDOW)
        rc = runner.run_span(kit=kit, kit_sha256="f" * 64, output=out, deadline=runner.launch_deadline(plan),
                             windows=NEW_WINDOW, deps=deps)
        receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
        self.assertEqual(rc, 2)
        self.assertEqual(deps.fake.calls, ["L001"])
        self.assertEqual(receipt["span_result"]["chain_outcome"], "INCOMPLETE")
        self.assertEqual(deps.host.calls[-1], "restore")
        self.assertTrue(all(f.events[-1] == "stop" for f in deps.feeds))
        _, stops = desk.build_desk(plan_id="t", input_dir=out / runner.DESK_BUNDLE, out_dir=out / "desk",
                                   adapter="leg-summary-v1", stop_rules=kit["stop_rules"])
        self.assertIn("REFUSAL", [s["code"] for s in stops])

    def test_short_deadline_refuses_at_the_plan_and_runs_nothing(self):
        kit = campaign_kit()
        out = self.root / "short"
        clock = runner.FakeClock(local("2026-11-15T13:20"))
        deps = runner.mock_deps(out, clock)
        deps.max_span_s = runner.max_span_s()
        rc = runner.run_span(kit=kit, kit_sha256="f" * 64, output=out, deadline=clock.time() + 7200,
                             windows=NEW_WINDOW, deps=deps)
        receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
        self.assertEqual(rc, 2)
        self.assertIn("plan needs", receipt["error"])
        self.assertEqual(deps.fake.calls, [])
        self.assertEqual(deps.host.calls[-1], "restore")
        with self.assertRaises(FileExistsError):      # create-once
            runner.run_span(kit=kit, kit_sha256="f" * 64, output=out, deadline=clock.time() + 7200,
                            windows=NEW_WINDOW, deps=deps)

    def test_no_leg_starts_inside_a_blackout(self):
        # The plan normally refuses such a t0; with that check bypassed the driver's own net still holds.
        with patch.object(legsmod, "blackout_bound_s", return_value=0.0):
            out, rc, summary, stops, deps, receipt = self.run_mock(t0="2026-11-15T01:22")
        self.assertEqual(rc, 0, receipt.get("error"))
        waits = [s for s in receipt["steps"] if s["name"].endswith("blackout-wait")]
        self.assertEqual(len(waits), 1)
        for leg in summary["legs"]:
            started = datetime.fromtimestamp(leg["started_epoch_s"], ZONE)
            self.assertFalse(started.hour == 2 and started.minute < 35, leg)

    def test_soak_does_not_overlap_the_driver_window(self):
        out = self.root / "soak"
        clock = runner.FakeClock(local("2026-11-15T11:30"))
        deps = runner.mock_deps(out, clock)
        deps.soak_windows, deps.max_span_s = OLD_WINDOW, runner.max_span_s()
        kit = campaign_kit()
        plan = legsmod.plan_span(kit, t0_epoch=clock.time(), windows=NEW_WINDOW, leg_ids=["L001"])
        rc = runner.run_span(kit=kit, kit_sha256="f" * 64, output=out, deadline=runner.launch_deadline(plan) + 7200,
                             windows=NEW_WINDOW, deps=deps, leg_ids=["L001"])
        receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
        self.assertEqual(rc, 0, receipt.get("error"))
        soak = next(s for s in receipt["steps"] if s["name"] == "soak")
        self.assertGreaterEqual(soak["started"]["epoch_s"], local("2026-11-15T13:15"))

    def test_mock_cli(self):
        kit_path = self.root / "kit.json"
        kit_path.write_text(json.dumps(campaign_kit(), indent=1))
        with patch("sys.stdout", io.StringIO()) as stdout:
            rc = runner.main(["mock", "--kit", str(kit_path), "--output", str(self.root / "cli"),
                              "--t0-local", "2026-11-15T13:20", "--batch-window", "02:00-02:35",
                              "--legs", "L001,L002,L003"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(stdout.getvalue())["legs"], 3)
        with patch("sys.stdout", io.StringIO()) as stdout:
            self.assertEqual(runner.main(["plan", "--kit", str(kit_path), "--t0", str(local("2026-11-15T13:20")),
                                          "--batch-window", "02:00-02:35"]), 0)
        plan = json.loads(stdout.getvalue())
        self.assertEqual(plan["launch_deadline_epoch_s"], plan["deadline_epoch_s"] + runner.LAUNCH_RESERVE_S)


# --------------------------------------------------------------------------
# The leg runtime on the synthetic backend (real r1_runtime orchestration, fake world)
# --------------------------------------------------------------------------
class LegRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tests.align import r1_synthetic as rs
        from tests.align.test_r1_runtime import write_soak
        cls.tmp = tempfile.TemporaryDirectory(dir=TMP)
        cls.root = Path(cls.tmp.name)
        cls.config = rs.synthetic_config(cls.root / "cfg")
        cls.soak = write_soak(cls.root / "soak.json")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def spec(self, leg_id="L001", band="q0", **kw):
        spec = {"schema": legsmod.LEG_SPEC_SCHEMA, "campaign_id": "cl-test-01", "leg_id": leg_id, "seed": 7,
                "start_band": band, "prefill_tokens": 2000, "prefill_chars": legsmod.prefill_chars(2000),
                "decode_tokens": 256, "quiet_s": legsmod.BAND_RECIPES[band]["quiet_s"]}
        spec.update(kw)
        path = self.root / f"{leg_id}-{band}.json"
        path.write_text(json.dumps(spec))
        return path

    def call(self, out, spec_path, *, soak=True, backend_factory=None):
        from joulewise.align.apple import cadence_leg, r1_runtime as rt
        buffer = io.StringIO()
        argv = ["--config", str(self.config), "--leg-spec", str(spec_path), "--r1-kind", "cadence-leg",
                "--output", str(out)] + (["--soak-reference", str(self.soak)] if soak else [])
        code = cadence_leg.main(argv, stdout=buffer, backend_factory=backend_factory)
        self.assertIs(rt.Segment.__name__, "Segment")          # the swap never outlives the call
        return code, (json.loads(buffer.getvalue()) if code == 0 else None)

    def test_one_leg_runs_its_own_g0_then_one_turn_and_writes_no_energy(self):
        from joulewise.align.apple import cadence_leg, r1_runtime as rt
        out = self.root / "q300"
        code, result = self.call(out, self.spec(band="q300"))
        self.assertEqual(code, 0, json.loads((out / rt.CUSTODY_NAME).read_text()).get("error"))
        self.assertEqual((result["kind"], result["leg_status"], result["g0_outcome"], result["decode_tokens"],
                          result["decode_cap_reached"], result["g0_timeout_s"]),
                         ("cadence-leg", "complete", "released", 256, True, 1200))
        for key in cadence_leg.RESULT_FIELDS:
            self.assertIn(key, result)
        legsmod.guard_projection(result, "t", values=False)
        self.assertNotIn("decode_energy_j", json.dumps(result))
        episode = json.loads((out / result["bundle"] / "outputs/align_episode.json").read_text())
        g0 = next(r for r in episode["hardware"]["thermal"]["intervals"] if r["kind"] == "G0")
        self.assertGreaterEqual((episode["turns"][0]["start_ns"] - g0["end_ns"]) / rt.NS, 300)
        self.assertEqual(episode["hardware"]["token_budget"]["deadline_origin"], "R1_after_G0_release_and_quiet")
        self.assertEqual(json.loads((out / rt.CUSTODY_NAME).read_text())["status"], "complete")
        config = json.loads((out / result["bundle"] / "config.json").read_text())
        self.assertIn("cadence-leg=L001", config["run_metadata"]["tags"])
        self.assertEqual(json.loads(config["workload_profile"]["prompt_text"])["task_kwargs"],
                         {"prefill_chars": legsmod.prefill_chars(2000)})
        # The driver's load verdict reads the result (RL-72 E2 journal completeness).
        from scripts import align_r1_rehearsal as r1
        r1.os_load_verdict("L001", result)

    def test_unreleased_g0_is_a_recorded_leg_not_a_failure(self):
        from tests.align.test_r1_runtime import IncompleteMemberTests
        code, result = self.call(self.root / "nog0", self.spec("L002"),
                                 backend_factory=IncompleteMemberTests.NoReleaseBackend)
        self.assertEqual(code, 0)
        self.assertEqual((result["leg_status"], result["g0_released"], result["decode_tokens"]),
                         ("g0_unreleased", False, None))

    def test_bad_spec_and_missing_soak_refuse_before_work(self):
        from joulewise.align.apple import r1_runtime as rt
        code, _ = self.call(self.root / "bad", self.spec("L003", quiet_s=5))
        self.assertEqual(code, rt.EXIT_REFUSED)
        self.assertFalse((self.root / "bad").exists())
        out = self.root / "nosoak"
        code, _ = self.call(out, self.spec("L004"), soak=False)
        self.assertEqual(code, rt.EXIT_REFUSED)
        self.assertIn("soak", json.loads((out / rt.CUSTODY_NAME).read_text())["error"])

    def test_condition13_sources_are_untouched(self):
        from joulewise.align.apple import v4_registration as reg
        changed = subprocess.run(["git", "diff", "--name-only", "origin/align/2026-11-13-rl145-build", "--",
                                  *reg.R1_EXECUTED_SOURCES], cwd=runner.ROOT, capture_output=True, text=True)
        if changed.returncode == 0:
            self.assertEqual(changed.stdout.strip(), "")


class RunnerWithLegRuntimeTests(unittest.TestCase):
    """The driver with its leg step wired to the real leg runtime (in process, synthetic backend)."""

    def test_two_legs_through_the_leg_runtime(self):
        from joulewise.align.apple import cadence_leg
        from tests.align import r1_synthetic as rs
        from tests.align.test_r1_runtime import write_soak
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            config = rs.synthetic_config(root / "cfg")
            kit = campaign_kit(n_legs=2, legs_per_span=2, end_by_local="18:00")
            clock = runner.FakeClock(local("2026-11-15T13:20"))
            out = root / "span"
            deps = runner.mock_deps(out, clock)
            deps.max_span_s = runner.max_span_s()

            def soak(soak_dir, *a):
                Path(soak_dir).mkdir(parents=True)
                return write_soak(Path(soak_dir) / "soak_reference.json")

            def leg(attempt_dir, spec_path, soak_reference, cap_s, feeds, work_remaining):
                small = {**json.loads(Path(spec_path).read_text()), "prefill_tokens": 2000,
                         "prefill_chars": legsmod.prefill_chars(2000), "decode_tokens": 128}
                path = Path(attempt_dir).parent / "leg_spec.synthetic.json"
                path.write_text(json.dumps(small))
                code = cadence_leg.main(["--config", str(config), "--leg-spec", str(path), "--r1-kind",
                                         "cadence-leg", "--output", str(attempt_dir), "--soak-reference",
                                         str(soak_reference)], stdout=io.StringIO())
                if code:
                    raise runner.LegRuntimeError(f"exit {code}")
                return runner.accepted_result(attempt_dir)
            deps.run_soak, deps.run_leg = soak, leg
            plan = legsmod.plan_span(kit, t0_epoch=clock.time(), windows=NEW_WINDOW)
            rc = runner.run_span(kit=kit, kit_sha256="f" * 64, output=out, deadline=runner.launch_deadline(plan),
                                 windows=NEW_WINDOW, deps=deps)
            receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
            self.assertEqual(rc, 0, receipt.get("error"))
            summaries = [json.loads((out / f"legs/L00{i}/leg_summary.json").read_text()) for i in (1, 2)]
            self.assertEqual([s["g0_outcome"] for s in summaries], ["released", "released"])
            self.assertEqual([s["os_level_max"] for s in summaries], [0, 0])
            record = json.loads((out / "legs/L001/leg_record.json").read_text())
            self.assertEqual(record["result"]["decode_tokens"], 128)
            _, stops = desk.build_desk(plan_id="t", input_dir=out / runner.DESK_BUNDLE, out_dir=out / "desk",
                                       adapter="leg-summary-v1", stop_rules=kit["stop_rules"])
            self.assertEqual(stops, [])


# --------------------------------------------------------------------------
# Launcher registration
# --------------------------------------------------------------------------
def launch_files(root, *, kind="cadence-legs-v1", seconds, **extra):
    """launch_align_r0.launch up to the (failing) bootstrap, as the smoke launcher tests do."""
    import plistlib  # noqa: F401
    repo = root / "repo"
    (repo / "scripts").mkdir(parents=True, exist_ok=True)
    for name in ("align_r0_checks.py", "run_align_r1_smoke.py", "cadence_legs_runner.py"):
        (repo / "scripts" / name).write_text("")
    soak = root / "soak"
    soak.write_text("{}")
    args = SimpleNamespace(repo=repo, config=None, soak_reference=None, output=root / "out",
                           python_bin=Path(sys.executable), runner_kind=kind, checks=None, keep_going=True,
                           magistrate_pid=1234, deadline=1000 + seconds, custody_root=root / "custody",
                           exit_wait_seconds=180, start_wait_seconds=30, disk_path=root, launchctl_bin="fake-launchctl",
                           pmset_bin="fake-pmset", pgrep_bin="fake-pgrep", kill_bin="fake-kill",
                           kit=None, legs=None, batch_window=None)
    for name, value in extra.items():
        setattr(args, name, value)
    with patch.object(launcher, "pid_alive", return_value=True), patch.object(launcher.time, "time", return_value=1000), \
         patch.object(launcher.uuid, "uuid4", return_value=SimpleNamespace(hex="fixed")), \
         patch.object(launcher.subprocess, "run", side_effect=[subprocess.CalledProcessError(19, []),
                                                               subprocess.CompletedProcess([], 0, "", "")]):
        try:
            launcher.launch(args)
        except subprocess.CalledProcessError:
            pass
    job = root / "custody/r0-launches/fixed"
    return (job / "runner.json").read_bytes(), (job / "com.joulewise.align-r0.fixed.plist").read_bytes()


class LauncherTests(unittest.TestCase):
    def kit_file(self, root):
        path = root / "kit.json"
        path.write_text(json.dumps(campaign_kit(), indent=1))
        return path

    def test_runner_argv(self):
        args = SimpleNamespace(repo=Path("/synthetic/repo"), python_bin=Path("/synthetic/python"),
                               output=Path("/synthetic/new"), runner_kind="cadence-legs-v1",
                               kit=Path("/synthetic/kit.json"), legs="L001,L002,L003", batch_window="02:00-02:35",
                               deadline=1234, pmset_bin="fake-pmset")
        self.assertEqual(launcher.runner_argv(args), [
            "/synthetic/python", "/synthetic/repo/scripts/cadence_legs_runner.py", "run", "--kit",
            "/synthetic/kit.json", "--output", "/synthetic/new", "--legs", "L001,L002,L003", "--batch-window",
            "02:00-02:35", "--deadline", "1234", "--pmset-bin", "fake-pmset"])

    def test_launch_writes_an_agent_free_interactive_job(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            plan = launcher.cadence_plan(self.kit_file(root), "L001,L002,L003", "02:00-02:35",
                                         t0=local("2026-11-15T13:20"))
            minimum = launcher.cadence_minimum_seconds(plan)
            self.assertEqual(minimum, plan["worst_case_s"] + runner.LAUNCH_RESERVE_S)
            spec, plist = self._launch_at(root, minimum)
            spec = json.loads(spec)
            self.assertEqual(spec["kind"], "cadence-legs-v1")
            self.assertIn("--kit", spec["argv"])
            import plistlib
            job = plistlib.loads(plist)
            self.assertEqual(job["ProcessType"], "Interactive")
            self.assertGreaterEqual(job["ExitTimeOut"], 2 * launcher.R1_CLEANUP_GRACE_S + 10)

    def _launch_at(self, root, seconds):
        # The harness pins time.time to 1000; plan the span at a real afternoon t0 instead.
        real_plan = launcher.cadence_plan
        with patch.object(launcher, "cadence_plan",
                          side_effect=lambda kit, legs, window: real_plan(kit, legs, window,
                                                                          t0=local("2026-11-15T13:20"))):
            return launch_files(root, seconds=seconds, kit=self.kit_file(root), legs="L001,L002,L003",
                                batch_window="02:00-02:35")

    def test_launch_refusals(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            plan = launcher.cadence_plan(self.kit_file(root), "L001,L002,L003", "02:00-02:35",
                                         t0=local("2026-11-15T13:20"))
            with self.assertRaisesRegex(ValueError, "deadline cannot fit"):
                self._launch_at(root, launcher.cadence_minimum_seconds(plan) - 1)
            self.assertFalse((root / "custody").exists())
        cases = (({"kit": Path("/nonexistent/kit.json")}, "existing --kit"),
                 ({"soak_reference": Path("/synthetic/soak")}, "own fresh soak"),
                 ({"legs": "L1;L2"}, "--legs"), ({"batch_window": "2-3"}, "--batch-window"))
        for extra, why in cases:
            with tempfile.TemporaryDirectory(dir=TMP) as td:
                root = Path(td)
                values = {"kit": self.kit_file(root), **extra}
                with self.assertRaisesRegex(ValueError, re.escape(why)):
                    launch_files(root, seconds=43000, **values)
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            root = Path(td)
            with self.assertRaisesRegex(ValueError, "cadence-legs-v1 only"):
                launch_files(root, kind="r1-smoke", seconds=43000, kit=self.kit_file(root),
                             soak_reference=root / "soak")

    def test_outer_run_treats_the_campaign_like_the_smoke(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            spec = Path(td) / "runner.json"
            spec.write_text(json.dumps({"kind": "cadence-legs-v1", "argv": ["fake-python", "fake-runner"]}))
            args = SimpleNamespace(deadline=__import__("time").time() + 7200, runner_spec=spec, pmset_bin="fake")
            with patch.object(launcher, "sleep_display") as display, patch.object(launcher.time, "sleep") as sleep, \
                 patch.object(launcher.signal, "signal"), patch.object(launcher.subprocess, "Popen") as popen:
                popen.return_value.wait.return_value = 0
                popen.return_value.poll.return_value = 0
                self.assertEqual(launcher.run_until_deadline(args), 0)
                display.assert_not_called()
                sleep.assert_not_called()


class CommittedKitTests(unittest.TestCase):
    """The dev-01 and dev-02 kits and the ledger rows that pin them (RL-149 section 2; section 5 item 6)."""
    KITS = ("cl-dev-01", "cl-dev-02")

    def load(self, name, window=kitmod.OS_BATCH_WINDOW):
        return kitmod.load_kit(runner.ROOT / f"docs/process/cadence/kits/{name}.json", batch_window=window)

    def test_kits_validate_under_both_blackouts_and_are_rl149_section2(self):
        for name in self.KITS:
            kit, _ = self.load(name)
            self.load(name, NEW_WINDOW[0])
            self.assertEqual(kit["ruling"], {"id": "RL-149 §2", "authorizes_spans": True})
            self.assertEqual(kit["runner"]["kind"], "cadence-legs-v1")
            self.assertEqual(len(kit["legs"]), 12)
            self.assertEqual({(leg["prefill_tokens"], leg["decode_tokens"], leg["start_band"]) for leg in kit["legs"]},
                             {(19458, 4096, "q0")})
            self.assertEqual(kitmod.deny_scan(kit), [])
            for path in ("scripts/cadence_legs_runner.py", "scripts/cadence_leg_runtime.py",
                         "joulewise/align/apple/cadence_leg.py", "joulewise/cadence/legs.py",
                         "joulewise/align/apple/r1_runtime.py", "configs/align/v4/r1_runtime.json"):
                self.assertIn(path, kit["frozen"]["paths"])
        self.assertIn("pilot_counted", [r["id"] for r in self.load("cl-dev-01")[0]["inclusion_rules"]])
        self.assertNotIn("pilot_counted", [r["id"] for r in self.load("cl-dev-02")[0]["inclusion_rules"]])

    def test_spans_plan_inside_the_launch_ceiling(self):
        kit, _ = self.load("cl-dev-01")
        for t0 in ("2026-11-15T13:20", "2026-11-16T02:40"):
            pilot = legsmod.plan_span(kit, t0_epoch=local(t0), windows=NEW_WINDOW, leg_ids=["L001", "L002", "L003"],
                                      max_span_s=runner.max_span_s())
            rest = legsmod.plan_span(kit, t0_epoch=local(t0), windows=NEW_WINDOW,
                                     leg_ids=[f"L{i:03d}" for i in range(4, 13)], max_span_s=runner.max_span_s())
            whole = legsmod.plan_span(self.load("cl-dev-02")[0], t0_epoch=local(t0), windows=NEW_WINDOW,
                                      max_span_s=runner.max_span_s())
            self.assertEqual([leg["leg_id"] for leg in pilot["legs"]], ["L001", "L002", "L003"])
            self.assertLess(pilot["expected_s"], 2 * 3600)
            self.assertLess(rest["expected_s"], whole["expected_s"])
            self.assertLessEqual(whole["expected_s"], 5.1 * 3600)

    def test_frozen_paths_hash_at_the_frozen_commit(self):
        kit, _ = self.load("cl-dev-01")
        have = subprocess.run(["git", "-C", str(runner.ROOT), "cat-file", "-e", kit["frozen"]["commit"] + "^{commit}"],
                              capture_output=True)
        if have.returncode:
            self.skipTest("frozen commit not in this clone")
        for name in self.KITS:
            self.assertEqual(kitmod.verify_frozen(self.load(name)[0], runner.ROOT), [])

    def test_ledger_pins_the_kits(self):
        from joulewise.cadence import blocks
        doc = blocks.load_ledger(runner.ROOT / blocks.LEDGER_PATH, runner.ROOT)
        rows = {b["design_id"]: b for b in doc["blocks"]}
        for design_id, name in (("dev-01", "cl-dev-01"), ("dev-02", "cl-dev-02")):
            _, sha = self.load(name)
            self.assertEqual(rows[design_id]["kit"]["sha256"], sha)
            self.assertEqual((rows[design_id]["status"], rows[design_id]["ruling"]), ("SPECIFIED", "RL-149 §2"))
        self.assertEqual((rows["hp-01"]["status"], rows["hp-01"]["kit"]), ("SPECIFIED", None))
        self.assertNotIn("pilot-01", rows)       # RL-149 2.3: the pilot is part of dev-01


if __name__ == "__main__":
    unittest.main()
