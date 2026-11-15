"""Kit schema v1.1: the cell law, the v1.1 validator, the free t0, and how the runner plans a v1.1 kit
(design doc section 14; RL-155 section 5.1; RL-150 R1, R3, R5). No model, sensor, host or energy."""
from __future__ import annotations

import ast
import copy
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout

from joulewise.cadence import kit as kitmod, kit_v11, legs as legsmod
from scripts import cadence_legs_runner as runner, cadence_queue, launch_cadence_span as cadence_launch

TMP = os.environ.get("TMPDIR")
ZONE = legsmod.LOCAL_ZONE
NEW_WINDOW = ((2, 0), (2, 35))           # RL-149 section 2.9 item 4
OLD_WINDOW = ((11, 45), (13, 15))        # ruling 8 as on the base today
SIZES = [2000, 10000, legsmod.ANCHOR_PREFILL_TOKENS]
PILOT_COMMIT = "b4b6aeb192da60d895a7529311b06599efff5be4"   # dev-01 and dev-02 measure from it
KITS = runner.ROOT / "docs/process/cadence/kits"


def local(text):
    return datetime.fromisoformat(text).replace(tzinfo=ZONE).timestamp()


def law(**overrides):
    value = {"method": kit_v11.LAW, "master_seed": 2026111499, "n_legs": 12, "bands": ["q0"],
             "prompt_tokens": list(SIZES), "g0_shapes": ["own"]}
    value.update(overrides)
    return value


def v11_kit(validate=True, seed_law=None, **template):
    seed_law = seed_law or law()
    defaults = {"decode_tokens": 4096}
    tpl = {"timezone": "America/Los_Angeles", "t0_rule": "free", "legs_per_span": 12, "soak_s": 1950,
           "fixed_overhead_s": 1200, "leg_budget_s": 1260, "leg_worst_case_s": 2700, "redo_quota": 2}
    tpl.update(template)
    kit = {
        "schema": kit_v11.SCHEMA, "campaign_id": "cl-test-11", "title": "Synthetic v1.1 kit",
        "ruling": {"id": "RL-149 §2", "authorizes_spans": True},
        "frozen": {"commit": "a" * 40, "paths": {"scripts/cadence_legs_runner.py": "1" * 64}},
        "runner": {"kind": kit_v11.RUNNER_KIND, "entry": "scripts/cadence_legs_runner.py",
                   "stage_journal": "chain-stages.jsonl"},
        "model": "mlx-community/Qwen3.8-27B-8bit", "leg_defaults": defaults, "seed_law": seed_law,
        "legs": kit_v11.generate_legs("cl-test-11", seed_law, defaults),
        "inclusion_rules": [{"id": "g0_released", "text": "Its G0 released."}],
        "stop_rules": {"instrument_fault": True, "refusal": True, "contaminated_redos_max": 3,
                       "contaminated_redos_scope": "span", "band_unreachable_max": 2,
                       "band_unreachable_scope": "span", "leg_time_factor": 1.5},
        "span_template": tpl,
        "checklist": [{"id": k, "kind": k, **({"args": {"min_gb": 40}} if k == "disk_free_gb" else {})}
                      for k in kitmod.CHECK_KINDS],
        "looks": [], "desk": {"adapter": "leg-summary-v1"},
    }
    return kit_v11.validate_kit(kit, batch_window=NEW_WINDOW) if validate else kit


class CellLaw(unittest.TestCase):
    def test_sizes_by_permuted_blocks_and_seeds_are_v1s(self):
        legs = kit_v11.generate_legs("cl-test-11", law(), {"decode_tokens": 4096})
        self.assertEqual(legs, kit_v11.generate_legs("cl-test-11", law(), {"decode_tokens": 4096}))
        sizes = [leg["prefill_tokens"] for leg in legs]
        for block in range(4):   # each aligned block of three in kit order holds each size once
            self.assertEqual(sorted(sizes[3 * block:3 * block + 3]), sorted(SIZES))
        self.assertEqual(sorted(sizes[:3]), sorted(SIZES))   # a class A pilot covers every size
        self.assertEqual({leg["decode_tokens"] for leg in legs}, {4096})
        self.assertEqual({leg["g0_shape"] for leg in legs}, {"own"})
        v1_legs = kitmod.generate_legs("cl-test-11", {"method": "sha256-v1", "master_seed": 2026111499,
                                                      "n_legs": 12, "bands": ["q0"]})
        self.assertEqual([(x["leg_id"], x["seed"], x["start_band"]) for x in legs],
                         [(x["leg_id"], x["seed"], x["start_band"]) for x in v1_legs])
        # The permutation is drawn, not fixed: across master seeds the blocks differ.
        orders = {tuple(leg["prefill_tokens"] for leg in kit_v11.generate_legs("c-id", law(master_seed=s),
                                                                              {"decode_tokens": 1}))
                  for s in range(20)}
        self.assertGreater(len(orders), 10)

    def test_the_law_is_pinned(self):
        legs = kit_v11.generate_legs("cl-dev-03", law(master_seed=2026111403), {"decode_tokens": 4096})
        self.assertEqual([leg["prefill_tokens"] for leg in legs],
                         [2000, 19458, 10000, 10000, 2000, 19458, 10000, 2000, 19458, 2000, 19458, 10000])
        self.assertEqual(legs[0]["seed"], 4129284831)

    def test_law_refusals(self):
        with self.assertRaises(kitmod.KitError):
            kit_v11.generate_legs("c-id", law(n_legs=10), {"decode_tokens": 1})
        with self.assertRaises(kitmod.KitError):
            kit_v11.generate_legs("c-id", law(method="sha256-v1"), {"decode_tokens": 1})
        with self.assertRaises(kitmod.KitError):
            kit_v11.generate_legs("c-id", law(g0_shapes=["span"]), {"decode_tokens": 1})

    def test_prompt_range_is_the_leg_specs(self):
        self.assertEqual(kit_v11.PROMPT_TOKENS_RANGE, legsmod.PREFILL_TOKENS_RANGE)
        self.assertEqual(kit_v11.MAX_SPAN_S, legsmod.MAX_SPAN_S)


class Validator(unittest.TestCase):
    def refused(self, kit, fragment, window=NEW_WINDOW):
        with self.assertRaises(kitmod.KitError) as ctx:
            kit_v11.validate_kit(kit, batch_window=window)
        self.assertTrue(any(fragment in p for p in ctx.exception.problems), ctx.exception.problems)

    def test_valid_kit_passes_and_load_dispatches_on_schema(self):
        kit = v11_kit()
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            path = Path(td) / "kit.json"
            path.write_text(json.dumps(kit, indent=1))
            loaded, sha = kitmod.load_kit(path, batch_window=NEW_WINDOW)
            self.assertEqual(loaded, kit)
            self.assertEqual(sha, hashlib.sha256(path.read_bytes()).hexdigest())
        # v1's validator does not take a v1.1 kit, and v1.1's does not take a v1 kit.
        with self.assertRaises(kitmod.KitError):
            kitmod.validate_kit(kit)
        v1_kit, _ = kitmod.load_kit(KITS / "cl-dev-02.json")
        self.refused(copy.deepcopy(v1_kit), "schema: must be joulewise.cadence_campaign_kit.v1.1")

    def test_cells_are_regenerated(self):
        kit = v11_kit()
        i, j = next((i, j) for i in range(12) for j in range(12)
                    if kit["legs"][i]["prefill_tokens"] != kit["legs"][j]["prefill_tokens"])
        kit["legs"][i]["prefill_tokens"], kit["legs"][j]["prefill_tokens"] = (
            kit["legs"][j]["prefill_tokens"], kit["legs"][i]["prefill_tokens"])
        self.refused(kit, "not the cell law's list")
        kit = v11_kit()
        del kit["legs"][3]["g0_shape"]
        self.refused(kit, "legs[3]: missing key 'g0_shape'")
        kit = v11_kit()
        kit["legs"][0]["g0_shape"] = "span"
        self.refused(kit, "not the cell law's list (first difference at index 0")

    def test_law_field_refusals(self):
        for overrides, fragment in (({"n_legs": 10}, "multiple of the 3 prompt sizes"),
                                    ({"prompt_tokens": [2000, 2000, 19458]}, "seed_law.prompt_tokens"),
                                    ({"prompt_tokens": [100, 19458]}, "seed_law.prompt_tokens"),
                                    ({"g0_shapes": ["span", "own"]}, "seed_law.g0_shapes"),
                                    ({"g0_shapes": ["span"]}, "seed_law.g0_shapes"),
                                    ({"method": "sha256-v1"}, "seed_law.method")):
            kit = v11_kit(validate=False)
            kit["seed_law"].update(overrides)
            self.refused(kit, fragment)

    def test_v1_fields_and_kind_are_refused_in_v11(self):
        kit = v11_kit(validate=False)
        kit["leg_defaults"]["prefill_tokens"] = 19458
        self.refused(kit, "leg_defaults: unknown key 'prefill_tokens'")
        kit = v11_kit(validate=False)
        kit["span_template"]["t0_local"] = "13:20"
        self.refused(kit, "span_template: unknown key 't0_local'")
        kit = v11_kit(validate=False)
        kit["runner"]["kind"] = "cadence-legs-v1"
        self.refused(kit, "runner.kind: must be cadence-legs-v1.1")
        kit = v11_kit(validate=False)
        kit["span_template"]["t0_rule"] = "13:20"
        self.refused(kit, "span_template.t0_rule")

    def test_the_condition_and_slot_refusal_still_applies(self):
        kit = v11_kit(validate=False)
        kit["legs"][2]["condition"] = "x"
        self.refused(kit, "names a condition or slot")
        kit = v11_kit(validate=False)
        kit["model"] = "benign"
        self.refused(kit, "carries a condition label or slot")

    def test_free_t0_template_capacity(self):
        v11_kit(validate=True)
        kit_v11.validate_kit(v11_kit(validate=False), batch_window=OLD_WINDOW)
        self.refused(v11_kit(validate=False, legs_per_span=14), "launch ceiling")
        kit = v11_kit(validate=False, leg_worst_case_s=1000)
        self.refused(kit, "below leg_budget_s")


class FreeT0Checklist(unittest.TestCase):
    GOOD = {"measurement_head": "a" * 40, "frozen_path_sha256": {"scripts/cadence_legs_runner.py": "1" * 64},
            "kit_sha256": "f" * 64, "ac_power": True, "powermode": 0, "network_time": "off", "freq_word": 0,
            "stray_monitors": [], "other_agents": [], "night_labels_loaded": [], "high_power_marker": False,
            "sudo_kill_rc": 0, "km003c_ready": True, "disk_free_gb": 120.0, "previous_span": "none", "halts": []}

    def rows(self, t0, end, window=NEW_WINDOW):
        obs = {**self.GOOD, "t0_epoch_s": t0, "end_by_epoch_s": end}
        return {r["kind"]: r for r in kit_v11.evaluate_checklist(v11_kit(), obs, expected_kit_sha256="f" * 64,
                                                                 batch_window=window)}

    def test_dev03_slot_passes_and_a_blackout_crossing_fails(self):
        t0 = local("2026-11-17T02:40")
        rows = self.rows(t0, t0 + 40950 + runner.LAUNCH_RESERVE_S)
        self.assertTrue(all(r["ok"] for r in rows.values()), [r for r in rows.values() if not r["ok"]])
        self.assertEqual(list(rows), [line["kind"] for line in v11_kit()["checklist"]])
        evening = local("2026-11-16T20:00")
        self.assertFalse(self.rows(evening, evening + 8 * 3600)["span_window"]["ok"])
        self.assertTrue(self.rows(evening, evening + 5 * 3600)["span_window"]["ok"])
        self.assertFalse(self.rows(t0, t0)["span_window"]["ok"])
        self.assertFalse(self.rows(t0, t0 + 90000)["span_window"]["ok"])
        self.assertFalse(self.rows(t0, None)["span_window"]["ok"])
        # The other lines are v1's: one bad observation fails its own line only.
        obs = {**self.GOOD, "powermode": 2, "t0_epoch_s": t0, "end_by_epoch_s": t0 + 3600}
        bad = [r["kind"] for r in kit_v11.evaluate_checklist(v11_kit(), obs, expected_kit_sha256="f" * 64,
                                                             batch_window=NEW_WINDOW) if not r["ok"]]
        self.assertEqual(bad, ["powermode_zero"])

    def test_dst_night_keeps_the_wall_window(self):
        # 2026-11-01 01:00-02:00 PDT/PST repeats; the 02:00 blackout is a wall time on the local date.
        t0 = local("2026-11-01T02:36")
        self.assertTrue(self.rows(t0, t0 + 6 * 3600)["span_window"]["ok"])
        self.assertTrue(kit_v11.meets_window(local("2026-11-01T01:30"), local("2026-11-01T02:10"), NEW_WINDOW))

    def test_queue_cli_dispatches_the_v11_checklist(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            kit_path, obs_path = Path(td) / "kit.json", Path(td) / "obs.json"
            kit_path.write_text(json.dumps(v11_kit(), indent=1))
            t0 = local("2026-11-17T02:40")
            obs_path.write_text(json.dumps({**self.GOOD, "t0_epoch_s": t0, "end_by_epoch_s": t0 + 41000}))
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = cadence_queue.main(["checklist", "--kit", str(kit_path), "--kit-sha256", "f" * 64,
                                           "--observations", str(obs_path), "--batch-window", "02:00-02:35"])
            self.assertEqual(code, 0, buffer.getvalue())
            self.assertIn("CHECKLIST PASS", buffer.getvalue())


class RunnerConsumesTheCell(unittest.TestCase):
    def test_specs_and_budgets_follow_each_legs_size(self):
        kit = v11_kit()
        specs = legsmod.leg_specs(kit)
        self.assertEqual([s["prefill_tokens"] for s in specs], [leg["prefill_tokens"] for leg in kit["legs"]])
        self.assertEqual({s["prefill_tokens"]: s["prefill_chars"] for s in specs},
                         {2000: 4111, 10000: 20557, 19458: 40000})
        # v1.1a: the leg runtime reads v1 leg specs, the bytes dev-01 runs.
        self.assertEqual({s["schema"] for s in specs}, {legsmod.LEG_SPEC_SCHEMA})
        plan = legsmod.plan_span(kit, t0_epoch=local("2026-11-17T02:40"), windows=[NEW_WINDOW])
        self.assertEqual(plan["runner_kind"], kit_v11.RUNNER_KIND)
        budgets = {leg["prefill_tokens"]: leg["budget_s"] for leg in plan["legs"]}
        self.assertEqual(budgets, {2000: 1076, 10000: 1156, 19458: 1251})
        self.assertEqual(plan["worst_case_s"], 40950)
        with self.assertRaises(legsmod.PlanError):   # 02:00 inside the worst case
            legsmod.plan_span(kit, t0_epoch=local("2026-11-16T20:00"), windows=[NEW_WINDOW])

    def test_an_unknown_g0_shape_has_no_runtime(self):
        kit = v11_kit()
        kit["legs"][4]["g0_shape"] = "session"
        with self.assertRaises(legsmod.PlanError) as ctx:
            legsmod.leg_specs(kit)
        self.assertIn("no leg runtime", str(ctx.exception))

    def test_mock_span_runs_the_cells(self):
        kit = v11_kit()
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            out = Path(td) / "span"
            rc, summary, stops, deps = runner.run_mock(kit=kit, kit_sha256="f" * 64, output=out,
                                                       t0_epoch=local("2026-11-17T02:40"), windows=[NEW_WINDOW])
            receipt = json.loads((out / runner.RECEIPT_NAME).read_text())
            self.assertEqual((rc, stops), (0, []), receipt.get("error"))
            self.assertEqual(receipt["runner_kind"], kit_v11.RUNNER_KIND)
            self.assertTrue(all(leg["admitted"] for leg in summary["legs"]))
            for leg in kit["legs"]:
                record = json.loads((out / "legs" / leg["leg_id"] / "leg_record.json").read_text())
                self.assertEqual((record["spec"]["prefill_tokens"], record["result"]["prefill_chars"]),
                                 (leg["prefill_tokens"], legsmod.prefill_chars(leg["prefill_tokens"])))

    def test_launcher_plans_a_v11_kit(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            path = Path(td) / "kit.json"
            path.write_text(json.dumps(v11_kit(), indent=1))
            plan = cadence_launch.cadence_plan(path, "L001,L002,L003", "02:00-02:35", t0=local("2026-11-17T02:40"))
            self.assertEqual([leg["prefill_tokens"] for leg in plan["legs"]],
                             [leg["prefill_tokens"] for leg in v11_kit()["legs"][:3]])

    def test_gen_legs_cli_is_the_law(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = cadence_queue.main(["gen-legs", "--law", kit_v11.LAW, "--campaign-id", "cl-test-11",
                                       "--master-seed", "2026111499", "--n-legs", "12", "--bands", "q0",
                                       "--prompt-tokens", "2000,10000,19458", "--g0-shapes", "own",
                                       "--decode-tokens", "4096"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(buffer.getvalue())["legs"], v11_kit()["legs"])


class LaunchBounds(unittest.TestCase):
    """#788 F4: RL-155a section 3's two bounds in code, for every kit; the free t0 does not remove them."""
    SOAK = [OLD_WINDOW]          # the R1 driver's soak window on this base

    def plan(self, n_legs, t0):
        kit = v11_kit()
        ids = [leg["leg_id"] for leg in kit["legs"]][:n_legs]
        return legsmod.plan_span(kit, t0_epoch=local(t0), windows=[NEW_WINDOW], leg_ids=ids)

    def test_latest_t0_by_the_fence(self):
        # RL-158 section 3 and RL-155a: 20:48:10 for 3 legs, 18:33:10 for 6, 16:18:10 for 9, 14:03:10 for 12.
        for n, latest in ((3, "20:48:10"), (6, "18:33:10"), (9, "16:18:10"), (12, "14:03:10")):
            self.assertEqual(legsmod.fence_problems(self.plan(n, f"2026-11-17T{latest}"), [NEW_WINDOW], self.SOAK), [])
            later = datetime.fromisoformat(f"2026-11-17T{latest}") .replace(tzinfo=ZONE).timestamp() + 1
            plan = legsmod.plan_span(v11_kit(), t0_epoch=later, windows=[NEW_WINDOW],
                                     leg_ids=[leg["leg_id"] for leg in v11_kit()["legs"]][:n])
            problems = legsmod.fence_problems(plan, [NEW_WINDOW], self.SOAK)
            self.assertEqual(len(problems), 1, (n, problems))
            self.assertIn("passes 01:50:00", problems[0])

    def test_no_launch_between_1050_and_1315(self):
        for t0, ok in (("10:50:00", True), ("10:50:01", False), ("12:00:00", False), ("13:14:59", False),
                       ("13:15:00", True)):
            problems = legsmod.fence_problems(self.plan(3, f"2026-11-17T{t0}"), [NEW_WINDOW], self.SOAK)
            self.assertEqual(problems == [], ok, (t0, problems))
            if not ok:
                self.assertIn("no launch between 10:50 and 13:15", problems[0])

    def test_the_plan_alone_does_not_hold_the_fence(self):
        # 21:00 with three legs: the worst case ends 01:37:30, clear of 02:00, but the fence ends 02:01:50.
        plan = self.plan(3, "2026-11-17T21:00")
        self.assertTrue(plan["blackout_clear"])
        self.assertTrue(legsmod.fence_problems(plan, [NEW_WINDOW], self.SOAK))

    def test_launcher_and_plan_cli_refuse(self):
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            path = Path(td) / "kit.json"
            path.write_text(json.dumps(v11_kit(), indent=1))
            ok = cadence_launch.cadence_plan(path, "L001,L002,L003", "02:00-02:35", t0=local("2026-11-17T02:40"))
            self.assertEqual(ok["worst_case_s"], 16650)
            for t0, fragment in (("2026-11-17T21:00", "passes 01:50"), ("2026-11-17T11:00", "no launch between")):
                with self.assertRaises(ValueError) as ctx:
                    cadence_launch.cadence_plan(path, "L001,L002,L003", "02:00-02:35", t0=local(t0))
                self.assertIn(fragment, str(ctx.exception))
            with self.assertRaises(ValueError) as ctx:      # a v1.1 kit names its blackout
                cadence_launch.cadence_plan(path, "L001,L002,L003", None, t0=local("2026-11-17T02:40"))
            self.assertIn("needs --batch-window", str(ctx.exception))
            err = io.StringIO()
            from contextlib import redirect_stderr
            with redirect_stderr(err), redirect_stdout(io.StringIO()):
                code = runner.main(["plan", "--kit", str(path), "--legs", "L001,L002,L003", "--batch-window",
                                    "02:00-02:35", "--t0", str(local("2026-11-17T21:00"))])
            self.assertEqual(code, 1)
            self.assertIn("passes 01:50", err.getvalue())
            buffer = io.StringIO()
            with redirect_stderr(io.StringIO()), redirect_stdout(buffer):
                code = runner.main(["plan", "--kit", str(path), "--legs", "L001,L002,L003", "--batch-window",
                                    "02:00-02:35", "--t0", str(local("2026-11-17T02:40"))])
            self.assertEqual(code, 0)
            printed = json.loads(buffer.getvalue())
            self.assertEqual(printed["fence_end_epoch_s"], local("2026-11-17T02:40") + 16650 + 1460)
            err = io.StringIO()
            with redirect_stderr(err), redirect_stdout(io.StringIO()):
                code = runner.main(["mock", "--kit", str(path), "--output", str(Path(td) / "m"),
                                    "--t0-local", "2026-11-17T02:40"])
            self.assertEqual(code, 1)
            self.assertIn("needs --batch-window", err.getvalue())

    def test_constants_agree(self):
        self.assertEqual((kit_v11.FENCE_QUIET_LEAD_S, kit_v11.SOAK_LAUNCH_LEAD_S),
                         (legsmod.FENCE_QUIET_LEAD_S, legsmod.SOAK_LAUNCH_LEAD_S))

    def test_v11_checklist_holds_the_quiet_and_the_soak_bound(self):
        good = FreeT0Checklist.GOOD
        def ok(t0, end):
            obs = {**good, "t0_epoch_s": local(t0), "end_by_epoch_s": local(end)}
            rows = kit_v11.evaluate_checklist(v11_kit(), obs, expected_kit_sha256="f" * 64, batch_window=NEW_WINDOW,
                                              soak_window=OLD_WINDOW)
            return next(r for r in rows if r["kind"] == "span_window")["ok"]
        self.assertTrue(ok("2026-11-17T20:00", "2026-11-18T01:50"))
        self.assertFalse(ok("2026-11-17T20:00", "2026-11-18T01:55"))
        self.assertFalse(ok("2026-11-17T11:00", "2026-11-17T16:00"))
        self.assertTrue(ok("2026-11-17T13:15", "2026-11-17T18:00"))
        with tempfile.TemporaryDirectory(dir=TMP) as td:     # the CLI refuses a v1.1 checklist with no window
            kit_path, obs_path = Path(td) / "kit.json", Path(td) / "obs.json"
            kit_path.write_text(json.dumps(v11_kit(), indent=1))
            obs_path.write_text(json.dumps(good))
            with redirect_stdout(io.StringIO()):
                code = cadence_queue.main(["checklist", "--kit", str(kit_path), "--kit-sha256", "f" * 64,
                                           "--observations", str(obs_path)])
            self.assertEqual(code, 2)


class DeskAdmittedColumn(unittest.TestCase):
    """dev-01 F8 (RL-161 section 3): the journal table prints inclusion, for v1 spans too."""

    def test_admitted_column(self):
        from tests.cadence.test_legs_runner import campaign_kit
        with tempfile.TemporaryDirectory(dir=TMP) as td:
            out = Path(td) / "span"
            runner.run_mock(kit=campaign_kit(n_legs=3, legs_per_span=3), kit_sha256="f" * 64, output=out,
                            t0_epoch=local("2026-11-17T02:40"), windows=[NEW_WINDOW], g0_timeout=["L002"])
            table = (out / "desk/JOURNAL-TABLE.md").read_text()
            self.assertIn("| nominal | admitted |", table)
            rows = {line.split("|")[1].strip(): line.rstrip(" |").split("|")[-1].strip()
                    for line in table.splitlines() if line.startswith("| L00")}
            self.assertEqual(rows, {"L001": "True", "L002": "False", "L003": "True"})
            self.assertNotIn("Cells and G0 references", table)     # a v1 span has no cell section
            self.assertNotIn("span_reference", json.loads((out / "desk/desk_summary.json").read_text()))


def _top_level_sources(text, names):
    tree = ast.parse(text)
    out = {}
    for node in tree.body:
        targets = ([node.name] if isinstance(node, (ast.FunctionDef, ast.ClassDef))
                   else [t.id for t in getattr(node, "targets", []) if isinstance(t, ast.Name)])
        for name in targets:
            if name in names:
                out[name] = ast.get_source_segment(text, node)
    return out


class V1Untouched(unittest.TestCase):
    """dev-01 and dev-02 measure from b4b6aeb19. v1 keeps validating, and nothing a leg executes moves."""

    def at_commit(self, commit, path):
        shown = subprocess.run(["git", "-C", str(runner.ROOT), "show", f"{commit}:{path}"],
                               capture_output=True, text=True)
        if shown.returncode:
            self.skipTest(f"{commit[:12]} is not in this clone")
        return shown.stdout

    def test_committed_v1_kits_validate_unchanged(self):
        for name in ("cl-dev-01", "cl-dev-02"):
            kit, sha = kitmod.load_kit(KITS / f"{name}.json")
            self.assertEqual(kit["schema"], kitmod.SCHEMA)
            self.assertEqual(sha, hashlib.sha256((KITS / f"{name}.json").read_bytes()).hexdigest())
            self.assertIs(kitmod.validate_kit(kit), kit)
            self.assertEqual(kitmod.generate_legs(kit["campaign_id"], kit["seed_law"], kit["leg_defaults"]), kit["legs"])

    def test_the_v11a_pin_runs_the_pilot_commits_leg_bytes(self):
        """At the v1.1a kit's frozen commit, what a leg executes from legs.py and kit.py (spec validation
        and the projection guard) is the pilot commit's, byte for byte: the cell law is class B (RL-150 R5).
        The span-reference leg (a later commit) changes these bytes and is class A."""
        pin = json.loads((KITS / "cl-dev-03.v1.1a.json").read_text())["frozen"]["commit"]
        names = {"joulewise/cadence/legs.py": {"validate_leg_spec", "_int", "prefill_chars", "guard_projection",
                                               "_walk", "LEG_SPEC_KEYS", "LEG_SPEC_SCHEMA", "BAND_RECIPES",
                                               "PREFILL_TOKENS_RANGE", "DECODE_TOKENS_RANGE", "LEG_KIND",
                                               "ANCHOR_PREFILL_CHARS", "ANCHOR_PREFILL_TOKENS"},
                 "joulewise/cadence/kit.py": {"deny_scan", "DENY_VALUE_RE", "DENY_KEY_TOKENS", "DENY_KEY_SUBSTRINGS",
                                              "FREE_TEXT_KEYS", "LEG_ID_RE", "CAMPAIGN_ID_RE", "validate_kit",
                                              "generate_legs", "evaluate_checklist"},
                 # the leg child imports desk.py through legs.py for the projection guard's key rule
                 "joulewise/cadence/desk.py": {"DENIED_KEY_RE"}}
        for path, wanted in names.items():
            old = _top_level_sources(self.at_commit(PILOT_COMMIT, path), wanted)
            new = _top_level_sources(self.at_commit(pin, path), wanted)
            self.assertEqual(set(old), wanted, path)
            self.assertEqual(new, old, path)
        for path in ("joulewise/align/apple/cadence_leg.py", "scripts/cadence_leg_runtime.py",
                     "joulewise/align/apple/r1_runtime.py", "joulewise/align/apple/thermal_gates.py"):
            self.assertEqual(self.at_commit(pin, path), self.at_commit(PILOT_COMMIT, path), path)


class CommittedDev03Kit(unittest.TestCase):
    """The dev-03 draft on kit v1.1a (the cell law only; RL-155 section 5.1), the fallback if the
    span-reference leg misses the cut-off. The lead pins and commits the final bytes; this checks the
    draft's shape and that it changes no byte a leg executes."""
    NAME = "cl-dev-03.v1.1a.json"
    PLANNING_ONLY = {"joulewise/cadence/kit.py", "joulewise/cadence/kit_v11.py", "joulewise/cadence/legs.py",
                     "joulewise/cadence/desk.py", "scripts/cadence_legs_runner.py", "scripts/launch_cadence_span.py"}

    def load(self, window=NEW_WINDOW):
        return kitmod.load_kit(KITS / self.NAME, batch_window=window)

    def test_shape(self):
        kit, _ = self.load()
        self.load(OLD_WINDOW)
        self.assertEqual((kit["schema"], kit["runner"]["kind"], kit["campaign_id"]),
                         (kit_v11.SCHEMA, kit_v11.RUNNER_KIND, "cl-dev-03"))
        self.assertEqual(kit["ruling"], {"id": "RL-149 §2", "authorizes_spans": True})
        self.assertEqual(kit["seed_law"]["prompt_tokens"], SIZES)
        sizes = [leg["prefill_tokens"] for leg in kit["legs"]]
        self.assertEqual({s: sizes.count(s) for s in SIZES}, {s: 4 for s in SIZES})
        self.assertEqual({(leg["decode_tokens"], leg["start_band"]) for leg in kit["legs"]}, {(4096, "q0")})
        self.assertEqual(kitmod.deny_scan(kit), [])
        dev02, _ = kitmod.load_kit(KITS / "cl-dev-02.json")
        self.assertEqual(set(kit["frozen"]["paths"]), set(dev02["frozen"]["paths"]) | {"joulewise/cadence/kit_v11.py"})
        self.assertEqual(kit["looks"], [])
        rules = {r["id"]: r["text"] for r in kit["inclusion_rules"]}
        self.assertIn("whether or not a redo replaced it", rules["not_a_replaced_attempt"])   # RL-150 R7

    def test_class_b_no_executed_leg_byte_moves(self):
        kit, _ = self.load()
        dev01, _ = kitmod.load_kit(KITS / "cl-dev-01.json")
        changed = {p for p, h in kit["frozen"]["paths"].items() if dev01["frozen"]["paths"].get(p) != h}
        if kit["seed_law"]["g0_shapes"] == ["own"]:
            self.assertLessEqual(changed, self.PLANNING_ONLY)

    def test_frozen_paths_hash_at_the_frozen_commit_and_the_plan_fits(self):
        kit, _ = self.load()
        have = subprocess.run(["git", "-C", str(runner.ROOT), "cat-file", "-e", kit["frozen"]["commit"] + "^{commit}"],
                              capture_output=True)
        if have.returncode:
            self.skipTest("frozen commit not in this clone")
        self.assertEqual(kitmod.verify_frozen(kit, runner.ROOT), [])
        t0 = local("2026-11-17T02:40")
        pilot = legsmod.plan_span(kit, t0_epoch=t0, windows=[NEW_WINDOW], leg_ids=["L001", "L002", "L003"],
                                  max_span_s=runner.max_span_s())
        whole = legsmod.plan_span(kit, t0_epoch=t0, windows=[NEW_WINDOW], max_span_s=runner.max_span_s())
        self.assertEqual(sorted(leg["prefill_tokens"] for leg in pilot["legs"]), SIZES)
        self.assertLessEqual(whole["expected_s"], 5.0 * 3600)
        self.assertEqual(whole["worst_case_s"], 40950)


if __name__ == "__main__":
    unittest.main()
