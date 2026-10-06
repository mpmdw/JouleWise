"""The block-5 HAZARD_PACK chain: rendered from the committed stage graphs and
run under zsh against a fake measurement checkout (fakes only at the tools)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from joulewise import whole_window
from joulewise.b5 import chain as b5_chain
from joulewise.b5 import plan as b5_plan
from joulewise.night_gate import NightPlan
from tests.fixtures.b5_plan import fake_window

REPO_ROOT = Path(__file__).resolve().parents[1]


def tree(pack: str) -> dict:
    return json.loads((REPO_ROOT / "configs/campaigns" / fake_window.PACKS[pack] / "plan_tree.json").read_text())


class StagePlanTests(unittest.TestCase):
    def test_every_committed_v5_pack_walks_to_one_bracketed_chain(self):
        for pack, members in (("alpha", 119), ("beta", 119), ("gamma", 101)):
            with self.subTest(pack=pack):
                stages = b5_chain.stage_plan(tree(pack))
                chain = [stage for stage in stages if stage.in_chain]
                self.assertEqual("bracket_reservation", chain[0].kind)
                self.assertEqual(["pre", "post"], [stage.slot for stage in chain if stage.slot])
                self.assertEqual("post", chain[-1].slot)
                self.assertEqual(members, sum(stage.expected_count for stage in chain
                                              if stage.kind == "campaign_collection"))
                self.assertEqual({"whole_window_verdict", "backup"},
                                 {stage.kind for stage in stages if not stage.in_chain})

    def test_broken_graphs_refuse_to_render(self):
        cases = {
            "unknown kind": lambda t: t["stage_graph"][3].update(kind="mystery"),
            "unknown tool": lambda t: t["stage_graph"][2]["launch"]["commands"][0]["argv_template"].update(tool_id="rm"),
            "foreign interface": lambda t: t["stage_graph"][2]["launch"]["commands"][0]["argv_template"].update(
                interface_id="joulewise.run_campaign.cli.v0"),
            "broken chain": lambda t: t["stage_graph"][4].update(predecessor="nowhere"),
            "no pre slot": lambda t: [a.update(value="mid") for a in
                                      t["stage_graph"][1]["launch"]["commands"][0]["argv_template"]["arguments"]
                                      if a["value"] == "pre"],
            "cwd outside repo": lambda t: t["stage_graph"][5]["launch"]["commands"][0].update(
                cwd={"kind": "binding", "value": "claim_runs_root"}),
            "empty collection": lambda t: t["stage_graph"][5].update(expected_count=0),
        }
        for label, mutate in cases.items():
            with self.subTest(case=label):
                broken = tree("alpha")
                mutate(broken)
                with self.assertRaises(b5_chain.ChainRenderError):
                    b5_chain.stage_plan(broken)


class RenderedChainFixture(unittest.TestCase):
    pack = "alpha"
    behavior: dict = {}

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="b5-chain-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.measurement = fake_window.build_checkout(self.root, behavior=dict(self.behavior), git=False)
        t0 = (int(time.time()) // 60) * 60
        self.record = b5_plan.write_window_plan(
            fake_window.inputs(self.root, self.measurement, self.pack, plan_id=f"b5-{self.pack}-1", t0_epoch_s=t0),
            settle_s=0, pack_digest=lambda _root: "e" * 64)
        self.plan = NightPlan.from_mapping(json.loads(Path(self.record["plan"]["path"]).read_text()))
        self.night = self.root / "custody/night"
        self.night.mkdir()

    def run_chain(self, *, env: dict | None = None, timeout: float = 120):
        environment = {"PATH": "/usr/bin:/bin", "HOME": str(self.root), "NIGHT_DIR": str(self.night)}
        environment.update(env or {})
        return subprocess.run(["/bin/zsh", "-f", self.plan.chain_path], env=environment,
                              capture_output=True, text=True, timeout=timeout, check=False)

    def stages(self):
        return b5_chain.stage_journal(self.night)


class ChainRunTests(RenderedChainFixture):
    def test_chain_is_valid_zsh_and_runs_every_stage_in_graph_order(self):
        subprocess.run(["/bin/zsh", "-n", self.plan.chain_path], check=True)
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        expected = []
        for stage in b5_chain.stage_plan(tree("alpha")):
            if not stage.in_chain:
                continue
            expected.append(stage.stage_id)
            if stage.slot == "pre":
                expected.append(stage.stage_id + ".screen")
            if stage.kind == "bound_derivation":
                expected.insert(len(expected) - 1, stage.stage_id + ".corpus")
            if stage.slot == "post":
                expected.append(stage.stage_id + ".session-status")
        self.assertEqual(expected, [row["stage_id"] for row in self.stages()])
        self.assertTrue(all(row["rc"] == 0 for row in self.stages()))
        bundles = fake_window.expected_bundles(self.plan)
        roots = self.plan.hazard_window["runs_roots"]
        for name, run_ids in bundles.items():
            present = {path.name for path in Path(roots[name]).iterdir() if (path / "summary_metrics.json").is_file()}
            self.assertEqual(run_ids, present)
        self.assertTrue((Path(roots["bound"]) / "neg8-drift-bound.json").is_file())
        self.assertTrue((self.night / "transcript/post-bracket-terminal-boundary.json").is_file())
        # The calibration captures run the runbook protocol; collections pass
        # their stage size as --max-failures.
        calls = fake_window.calls(self.measurement)
        captures = [call for call in calls if call["tool"] == "fiducial"]
        self.assertEqual(["pre", "post"], [call["slot"] for call in captures])
        for call in captures:
            self.assertIn("--sleep-display-before-capture", call["argv"])
            self.assertEqual("20", call["argv"][call["argv"].index("--arm-countdown-s") + 1])
        sizes = {stage.stage_id: stage.expected_count for stage in b5_chain.stage_plan(tree("alpha"))}
        collects = [call for call in calls if call["tool"] == "collect"]
        self.assertEqual(10, len(collects))
        self.assertEqual(sorted(sizes[s] for s in sizes if s.split("-", 1)[1] in {
            "bound-collection", "reference-start", "science-absolute", "science-abba-01-05",
            "science-abba-06-10", "reference-midpoint", "science-prefill-p2048-absolute",
            "science-prefill-p2048-abba-01-05", "science-prefill-p2048-abba-06-10", "reference-end"}),
            sorted(call["max_failures"] for call in collects))

    def test_inspection_modes_run_nothing(self):
        for name in ("NIGHT_VERIFY_ONLY", "NIGHT_RESERVATION_ARGV_ONLY"):
            with self.subTest(mode=name):
                completed = self.run_chain(env={name: "1"})
                self.assertEqual(b5_chain.EXIT_INSPECTION_REFUSED, completed.returncode)
                self.assertEqual([], fake_window.calls(self.measurement))
                self.assertEqual([], self.stages())

    def test_chain_reads_nothing_but_night_dir_from_the_environment(self):
        text = Path(self.plan.chain_path).read_text()
        self.assertNotIn("MEASUREMENT_ROOT", text)
        self.assertNotIn("MEASUREMENT_HEAD", text)
        self.assertNotIn("launch_window", text)
        self.assertNotIn("jq", text)
        completed = self.run_chain(env={"PY": "/nonexistent/python", "REPO": "/nonexistent"})
        self.assertEqual(0, completed.returncode, completed.stderr)


class FailedMemberTests(RenderedChainFixture):
    """One failed member in a 20-member stage: the other 19 run."""

    def setUp(self):
        order = json.loads((REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/"
                                        "02_phase_decode_abba_blocks_01_05/order_manifest.json").read_text())
        self.victim = order["executed_order"][0]["run_id"]
        self.behavior = {"fail_run_ids": [self.victim]}
        super().setUp()

    def test_one_failed_member_costs_only_itself(self):
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        stage = next(call for call in fake_window.calls(self.measurement)
                     if call["tool"] == "collect" and call["config_dir"].endswith("02_phase_decode_abba_blocks_01_05"))
        self.assertEqual(20, stage["max_failures"])
        self.assertEqual(20, len(stage["attempted"]))
        self.assertEqual(self.victim, stage["attempted"][0])
        claim = Path(self.plan.hazard_window["runs_roots"]["claim"])
        statuses = {run_id: json.loads((claim / run_id / "summary_metrics.json").read_text())["status"]
                    for run_id in stage["attempted"]}
        self.assertEqual(19, sum(status == "succeeded" for status in statuses.values()))
        # The stage records its failure and the chain carries on to post-calibration.
        rows = {row["stage_id"]: row["rc"] for row in self.stages()}
        self.assertEqual(1, rows["alpha-science-abba-01-05"])
        self.assertEqual(0, rows["alpha-post-calibration"])

    def test_the_pack_literal_would_have_dropped_the_other_nineteen(self):
        # The same fake runner with the pack's own `--max-failures 1` stops at
        # the first failure, exactly as run_campaign's loop does.
        source = (REPO_ROOT / "scripts/run_campaign.py").read_text()
        self.assertIn("if failures >= args.max_failures", source)
        runs = self.root / "control-runs"
        runs.mkdir()
        completed = subprocess.run(
            [sys.executable, str(self.measurement / "scripts/run_campaign.py"),
             str(REPO_ROOT / "configs/campaigns/d117_floor_qwen3-1p7b_v5/02_phase_decode_abba_blocks_01_05"),
             "--runs-dir", str(runs), "--max-failures", "1"], capture_output=True, text=True, check=False)
        self.assertEqual(1, completed.returncode)
        control = fake_window.calls(self.measurement)[-1]
        self.assertEqual([self.victim], control["attempted"])


class Neg8CorpusTests(RenderedChainFixture):
    """A corpus with 11 collected members derives the bound."""

    def setUp(self):
        self.behavior = {"fail_run_ids": ["neg8-refcorpus-r05"],
                         "neg8_minimum_n": whole_window.NEG8_DRIFT_MINIMUM_N}
        super().setUp()

    def test_eleven_of_twelve_derive_the_bound(self):
        self.assertEqual(10, whole_window.NEG8_DRIFT_MINIMUM_N)
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        collected = json.loads((self.night / "transcript" / b5_chain.NEG8_COLLECTED_MANIFEST).read_text())
        self.assertEqual(11, len(collected["members"]))
        self.assertNotIn("neg8-refcorpus-r05", [member["bundle_id"] for member in collected["members"]])
        derive = next(call for call in fake_window.calls(self.measurement) if call["tool"] == "derive")
        self.assertTrue(derive["ok"])
        self.assertEqual(11, derive["members"])
        self.assertTrue((Path(self.plan.hazard_window["runs_roots"]["bound"]) / "neg8-drift-bound.json").is_file())
        # The committed manifest itself would have refused (its r05 bundle failed).
        committed = REPO_ROOT / "configs/campaigns/neg8_reference_corpus_v5/derivation/settled_corpus.json"
        refused = subprocess.run(
            [sys.executable, str(self.measurement / "scripts/run_campaign.py"), "--derive-neg8-drift-bound",
             str(committed), "--neg8-drift-bound-output", str(self.root / "control-bound.json"),
             "--runs-dir", self.plan.hazard_window["runs_roots"]["bound"]], capture_output=True, check=False)
        self.assertEqual(1, refused.returncode)

    def test_all_twelve_keep_the_committed_manifest_bytes(self):
        fake_window.set_behavior(self.measurement, {})
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        committed = REPO_ROOT / "configs/campaigns/neg8_reference_corpus_v5/derivation/settled_corpus.json"
        self.assertEqual(committed.read_bytes(),
                         (self.night / "transcript" / b5_chain.NEG8_COLLECTED_MANIFEST).read_bytes())

    def test_too_few_members_is_recorded_and_the_chain_continues(self):
        fake_window.set_behavior(self.measurement, {"fail_run_ids": ["neg8-refcorpus-r01", "neg8-refcorpus-r02",
                                                                     "neg8-refcorpus-r03"]})
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        rows = {row["stage_id"]: row["rc"] for row in self.stages()}
        self.assertNotEqual(0, rows["alpha-bound-derivation"])
        self.assertEqual(0, rows["alpha-post-calibration"])


class StopTests(RenderedChainFixture):
    """The only stops: reservation, pre-calibration capture, pre-calibration screen."""

    def assert_stopped(self, behavior, exit_code, reason, last_tool):
        fake_window.set_behavior(self.measurement, behavior)
        completed = self.run_chain()
        self.assertEqual(exit_code, completed.returncode, completed.stderr)
        rows = self.stages()
        self.assertEqual({"stage_id": "chain.stop", "kind": reason, "rc": exit_code},
                         {key: rows[-1][key] for key in ("stage_id", "kind", "rc")})
        tools = [call["tool"] for call in fake_window.calls(self.measurement)]
        self.assertEqual(last_tool, tools[-1])
        self.assertNotIn("collect", tools)

    def test_failed_reservation_stops_before_anything(self):
        self.assert_stopped({"reservation_rc": 2}, b5_chain.EXIT_RESERVATION_FAILED, "reservation_failed", "reserve")

    def test_failed_pre_capture_stops_before_member_one(self):
        self.assert_stopped({"capture_rc": {"pre": 1}}, b5_chain.EXIT_PRE_CAPTURE_FAILED,
                            "pre_calibration_capture_failed", "fiducial")

    def test_failed_pre_screen_stops_before_member_one(self):
        self.assert_stopped({"b_fiducial_s": 0.04}, b5_chain.EXIT_PRE_SCREEN_FAILED,
                            "pre_calibration_screen_failed", "fiducial")

    def test_failed_post_capture_does_not_stop(self):
        fake_window.set_behavior(self.measurement, {"capture_rc": {"post": 3}})
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        rows = {row["stage_id"]: row["rc"] for row in self.stages()}
        self.assertEqual(3, rows["alpha-post-calibration"])


class GammaRenderTests(RenderedChainFixture):
    pack = "gamma"

    def test_gamma_renders_every_graph_stage_and_exposes_the_interior_reference_collision(self):
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        calls = [call for call in fake_window.calls(self.measurement) if call["tool"] == "collect"]
        midpoint = [call for call in calls if call["config_dir"].endswith("window_references_v5/midpoint")]
        # GAMMA-INTERIOR-REFERENCES-01 (lane L10): three graph stages share one
        # midpoint config, so the second and third collect nothing new.
        self.assertEqual(3, len(midpoint))
        self.assertEqual([1, 0, 0], [len(call["attempted"]) for call in midpoint])
        bundles = fake_window.expected_bundles(self.plan)
        for name, run_ids in bundles.items():
            root = Path(self.plan.hazard_window["runs_roots"][name])
            self.assertEqual(run_ids, {path.name for path in root.iterdir() if (path / "summary_metrics.json").is_file()})


class HelperTests(unittest.TestCase):
    def run_helper(self, source, *args):
        return subprocess.run([sys.executable, "-B", "-c", source, *map(str, args)],
                              capture_output=True, text=True, check=False)

    def test_screen_passes_at_the_limit_and_refuses_above_it_or_when_missing(self):
        with tempfile.TemporaryDirectory() as directory:
            evidence = Path(directory) / "instrument_evidence.json"
            for value, code in ((0.036462861644980, 0), (0.0364628616449801, 1), (None, 1), ("0.01", 1), (True, 1)):
                with self.subTest(value=value):
                    evidence.write_text(json.dumps({"b_fiducial_s": value}))
                    result = self.run_helper(b5_chain.SCREEN_HELPER, evidence, b5_chain.PRE_CAL_FIDUCIAL_MAX_S)
                    self.assertEqual(code, result.returncode, result.stdout + result.stderr)
            evidence.unlink()
            self.assertEqual(1, self.run_helper(b5_chain.SCREEN_HELPER, evidence, "0.03").returncode)

    def test_prune_keeps_succeeded_members_and_never_follows_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = {"schema_version": "joulewise.neg8_reference_corpus.v1", "corpus_id": "c",
                        "freeze_status": "settled_reference", "condition_id": "x",
                        "members": [{"bundle_id": "a", "bundle_path": "a"}, {"bundle_id": "b", "bundle_path": "b"},
                                    {"bundle_id": "c", "bundle_path": "../c"}, {"bundle_id": "d", "bundle_path": "d"}]}
            (root / "manifest.json").write_text(json.dumps(manifest))
            runs = root / "runs"
            for name, status in (("a", "succeeded"), ("b", "failed")):
                (runs / name).mkdir(parents=True)
                (runs / name / "summary_metrics.json").write_text(json.dumps({"status": status}))
            (root / "c").mkdir()
            (root / "c/summary_metrics.json").write_text(json.dumps({"status": "succeeded"}))
            result = self.run_helper(b5_chain.PRUNE_HELPER, root / "manifest.json", runs, root / "out.json")
            self.assertEqual(0, result.returncode, result.stderr)
            pruned = json.loads((root / "out.json").read_text())
            self.assertEqual(set(manifest) , set(pruned))
            self.assertEqual([{"bundle_id": "a", "bundle_path": "a"}], pruned["members"])
            summary = json.loads(result.stdout)
            self.assertEqual({"b": "failed", "c": None, "d": None},
                             {item["bundle_id"]: item["status"] for item in summary["dropped"]})
            # Create-once: a second run never overwrites the window's copy.
            self.assertNotEqual(0, self.run_helper(b5_chain.PRUNE_HELPER, root / "manifest.json", runs,
                                                   root / "out.json").returncode)


if __name__ == "__main__":
    unittest.main()
