"""Gate-prune round 2, lane P2-CHAIN: the block-5 chain, plan writer and CI lint.

PLAN2 items, each tested on the production render run under zsh against the
fake measurement checkout (fakes only at the tools), or on the unit itself:

* S3: operator countdowns 0 s on the pre slot and on collection stages; the
  post slot keeps 20 s;
* J1: the window calibration verdict, written once after the pre-slot screen
  (``scripts/b5_window_calibration_verdict.py``);
* J3 and row 14: the stage dispatch resolver, the desk refusal and the lint;
* row 8: the wall budget on non-member stages;
* row 17: the collection deadline;
* row 13: one retry of the NEG-8 corpus stage (no drain).
"""

from __future__ import annotations

import contextlib
import copy
import hashlib
import importlib.util
import io
import json
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from joulewise import whole_window
from joulewise.b5 import chain as b5_chain
from joulewise.b5 import plan as b5_plan
from joulewise.flags import core as flags_core
from joulewise.flags.schema import validate_flag
from joulewise.night_gate import NightPlan
from tests.fixtures.b5_plan import fake_window
from tests.flags.test_flags_core import hazard_root

REPO_ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("b5_window_calibration_verdict",
                                               REPO_ROOT / "scripts/b5_window_calibration_verdict.py")
verdict_script = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(verdict_script)
_spec = importlib.util.spec_from_file_location("check_b5_chain_prune2", REPO_ROOT / "scripts/check_b5_chain.py")
check_b5_chain = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_b5_chain)

PACKS = {name: REPO_ROOT / "configs/campaigns" / directory for name, directory in fake_window.PACKS.items()}


def tree(pack: str) -> dict:
    return json.loads((PACKS[pack] / "plan_tree.json").read_text())


class ChainFixture(unittest.TestCase):
    pack = "alpha"
    behavior: dict = {}
    horizon_s: int | None = None

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="b5-p2chain-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.measurement = fake_window.build_checkout(self.root, behavior=dict(self.behavior))
        t0 = (int(time.time()) // 60) * 60
        keywords = {} if self.horizon_s is None else {"horizon_s": self.horizon_s}
        self.record = b5_plan.write_window_plan(
            fake_window.inputs(self.root, self.measurement, self.pack, plan_id=f"b5-{self.pack}-1", t0_epoch_s=t0),
            settle_s=0, pack_digest=lambda _root: "e" * 64, threshold_defaults=fake_window.threshold_defaults,
            **keywords)
        self.plan = NightPlan.from_mapping(json.loads(Path(self.record["plan"]["path"]).read_text()))
        self.night = self.root / "custody/night"
        self.night.mkdir()

    def run_chain(self):
        environment = {"PATH": "/usr/bin:/bin", "HOME": str(self.root), "NIGHT_DIR": str(self.night)}
        return subprocess.run(["/bin/zsh", "-f", self.plan.chain_path], env=environment, capture_output=True,
                              text=True, timeout=300, check=False)

    def journal(self) -> list[dict]:
        return b5_chain.stage_journal(self.night)

    def chain_log(self) -> str:
        path = Path(self.plan.hazard_window["bindings"]["operator_log_root"]) / "window-chain.log"
        return path.read_text() if path.exists() else ""

    def unwritten_flags(self) -> list[dict]:
        return [json.loads(line[len(flags_core.UNWRITTEN_MARKER):]) for line in self.chain_log().splitlines()
                if line.startswith(flags_core.UNWRITTEN_MARKER)]


# ---------------------------------------------------------------------------
# S3: countdowns
# ---------------------------------------------------------------------------

class CountdownTests(ChainFixture):
    def test_collection_and_pre_slot_countdowns_are_zero_and_the_post_slot_keeps_twenty(self):
        """Before: every collection stage passed the pack's --arm-countdown-s 20 and both slots 20."""
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        calls = fake_window.calls(self.measurement)
        captures = {call["slot"]: call["argv"] for call in calls if call["tool"] == "fiducial"}
        self.assertEqual("0", captures["pre"][captures["pre"].index("--arm-countdown-s") + 1])
        self.assertEqual("20", captures["post"][captures["post"].index("--arm-countdown-s") + 1])
        for argv in captures.values():
            self.assertEqual(1, argv.count("--arm-countdown-s"))
            self.assertIn("--sleep-display-before-capture", argv)
        collects = [call for call in calls if call["tool"] == "collect"]
        self.assertEqual(10, len(collects))
        self.assertEqual({"0"}, {call["arm_countdown_s"] for call in collects})

    def test_every_committed_pack_rewrites_the_literal_once(self):
        bindings = check_b5_chain.synthetic_bindings(REPO_ROOT, PACKS["alpha"])
        for pack in PACKS:
            for stage in b5_chain.stage_plan(tree(pack)):
                if stage.kind != "campaign_collection":
                    continue
                with self.subTest(pack=pack, stage=stage.stage_id):
                    argv = b5_chain.stage_argv(stage, bindings, tree(pack), REPO_ROOT)
                    self.assertEqual(1, argv.count("--arm-countdown-s"))
                    self.assertEqual("0", argv[argv.index("--arm-countdown-s") + 1])
                    self.assertIn("--arm-quiet-mode", argv)

    def test_a_template_without_the_literal_gets_zero_not_the_runners_five_second_default(self):
        broken = tree("alpha")
        stage_row = next(row for row in broken["stage_graph"] if row["kind"] == "campaign_collection")
        arguments = stage_row["launch"]["commands"][0]["argv_template"]["arguments"]
        position = next(i for i, item in enumerate(arguments) if item["value"] == "--arm-countdown-s")
        del arguments[position:position + 2]
        stage = next(item for item in b5_chain.stage_plan(broken) if item.stage_id == stage_row["stage_id"])
        argv = b5_chain.stage_argv(stage, check_b5_chain.synthetic_bindings(REPO_ROOT, PACKS["alpha"]), broken,
                                   REPO_ROOT)
        self.assertEqual("0", argv[argv.index("--arm-countdown-s") + 1])
        self.assertTrue(any(item.startswith("campaign_collection stages pass --arm-countdown-s 0")
                            for item in b5_chain.DEVIATIONS))


# ---------------------------------------------------------------------------
# J1: the window calibration verdict
# ---------------------------------------------------------------------------

class VerdictChainTests(ChainFixture):
    def test_the_verdict_is_written_once_after_the_screen_and_before_the_first_collection(self):
        """Before: no verdict step; every member refit the pre slot itself."""
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        ids = [row["stage_id"] for row in self.journal()]
        verdict = "alpha-pre-calibration.window-calibration-verdict"
        self.assertEqual(ids.index("alpha-pre-calibration.screen") + 1, ids.index(verdict))
        self.assertLess(ids.index(verdict), ids.index("alpha-bound-collection"))
        row = next(row for row in self.journal() if row["stage_id"] == verdict)
        self.assertEqual(("window_calibration_verdict", 0), (row["kind"], row["rc"]))
        calls = [call for call in fake_window.calls(self.measurement) if call["tool"] == "verdict"]
        self.assertEqual(1, len(calls))
        pre = self.plan.hazard_window["bindings"]["pre_calibration_dir"]
        self.assertEqual(["--pre-calibration-dir", pre], calls[0]["argv"])
        self.assertTrue(calls[0]["pre_dir_exists"])
        self.assertTrue(b5_chain.window_calibration_verdict_path(pre).is_file())
        tools = [call["tool"] for call in fake_window.calls(self.measurement)]
        self.assertLess(tools.index("verdict"), tools.index("collect"))


class VerdictFailureTests(ChainFixture):
    behavior = {"verdict_rc": 1}

    def test_a_verdict_that_is_not_verified_never_stops_the_chain(self):
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        rows = {row["stage_id"]: row["rc"] for row in self.journal()}
        self.assertEqual(1, rows["alpha-pre-calibration.window-calibration-verdict"])
        self.assertEqual(10, sum(call["tool"] == "collect" for call in fake_window.calls(self.measurement)))
        self.assertEqual(0, rows["alpha-post-calibration"])


def calibration_dir(base: Path, *, evidence: dict | None = None) -> Path:
    """A pre-slot capture directory of the writer's shape: manifest.json binding its artifacts by SHA-256."""

    directory = base / "instrument_validation" / "pre-attempt"
    (directory / "raw").mkdir(parents=True)
    files = {
        "instrument_evidence.json": json.dumps(evidence if evidence is not None else
                                               {"status": "valid", "b_fiducial_s": 0.031}).encode(),
        "raw/powermetrics.plist": b"<plist>raw samples</plist>\n",
        "events.jsonl": b'{"event": "pulse"}\n',
    }
    for relative, raw in files.items():
        (directory / relative).write_bytes(raw)
    manifest = {"schema_version": verdict_script.MANIFEST_SCHEMA,
                "artifacts": {relative: hashlib.sha256(raw).hexdigest() for relative, raw in files.items()}}
    (directory / "manifest.json").write_text(json.dumps(manifest))
    return directory


class VerdictWriterTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = Path(self._tmp.name).resolve()
        self.directory = calibration_dir(self.base)
        self.seen: list = []
        self.estimator = {"joulewise/powermetrics_fiducial.py": "f" * 64}

    def verifier(self, result=0.0335):
        def verify(evidence, raw, events):
            self.seen.append((evidence, raw, events))
            if isinstance(result, Exception):
                raise result
            return result
        return verify

    def run_main(self, *extra, verifier=None, estimator=None):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = verdict_script.main(["--pre-calibration-dir", str(self.directory), *extra],
                                       verifier=verifier or self.verifier(),
                                       estimator_digests=estimator or (lambda: dict(self.estimator)))
        return code, stdout.getvalue(), stderr.getvalue()

    def output(self) -> Path:
        return b5_chain.window_calibration_verdict_path(self.directory)

    def test_a_reproduced_capture_writes_the_digests_members_match_and_the_effective_bound(self):
        code, stdout, _ = self.run_main()
        self.assertEqual(verdict_script.EXIT_VERIFIED, code)
        self.assertEqual(self.directory.parent / "window_calibration_verdict.json", self.output())
        verdict = json.loads(self.output().read_text())
        digest = lambda relative: hashlib.sha256((self.directory / relative).read_bytes()).hexdigest()  # noqa: E731
        self.assertEqual({"schema": verdict_script.SCHEMA, "status": "verified",
                          "evidence_sha256": digest("instrument_evidence.json"),
                          "manifest_sha256": digest("manifest.json"),
                          "raw_plist_sha256": digest("raw/powermetrics.plist"),
                          "events_sha256": digest("events.jsonl"), "estimator_files_sha256": self.estimator,
                          "effective_b_fiducial_s": 0.0335, "stored_b_fiducial_s": 0.031, "flags": []},
                         {key: verdict[key] for key in ("schema", "status", "evidence_sha256", "manifest_sha256",
                                                        "raw_plist_sha256", "events_sha256",
                                                        "estimator_files_sha256", "effective_b_fiducial_s",
                                                        "stored_b_fiducial_s", "flags")})
        # The refit ran once, on the stored evidence and the raw bytes the manifest binds.
        self.assertEqual(1, len(self.seen))
        evidence, raw, events = self.seen[0]
        self.assertEqual({"status": "valid", "b_fiducial_s": 0.031}, evidence)
        self.assertEqual(((self.directory / "raw/powermetrics.plist").read_bytes(),
                          (self.directory / "events.jsonl").read_bytes()), (raw, events))
        self.assertEqual("verified", json.loads(stdout)["status"])

    def test_create_once(self):
        self.assertEqual(verdict_script.EXIT_VERIFIED, self.run_main()[0])
        before = self.output().read_bytes()
        code, _, stderr = self.run_main(verifier=self.verifier(0.05))
        self.assertEqual(verdict_script.EXIT_EXISTS, code)
        self.assertIn("never overwritten", stderr)
        self.assertEqual(before, self.output().read_bytes())

    def test_the_write_itself_is_exclusive(self):
        """Review E2: a verdict that appears between the existence check and the write is never replaced."""
        self.output().write_bytes(b"first\n")
        with self.assertRaises(FileExistsError):
            verdict_script.write_create_once(self.output(), {"status": "verified"})
        self.assertEqual(b"first\n", self.output().read_bytes())

    def test_bytes_that_differ_from_the_manifest_are_not_refit(self):
        (self.directory / "raw/powermetrics.plist").write_bytes(b"<plist>changed</plist>\n")
        code, _, _ = self.run_main()
        self.assertEqual(verdict_script.EXIT_NOT_VERIFIED, code)
        verdict = json.loads(self.output().read_text())
        self.assertEqual(("not_verified", None, ["artifact_hash_mismatch: raw/powermetrics.plist"]),
                         (verdict["status"], verdict["effective_b_fiducial_s"], verdict["flags"]))
        self.assertEqual([], self.seen)

    def test_physics_that_does_not_reproduce_is_recorded_not_verified(self):
        code, _, _ = self.run_main(verifier=self.verifier(ValueError("instrument physics does not satisfy")))
        self.assertEqual(verdict_script.EXIT_NOT_VERIFIED, code)
        verdict = json.loads(self.output().read_text())
        self.assertEqual("not_verified", verdict["status"])
        self.assertIsNone(verdict["effective_b_fiducial_s"])
        self.assertTrue(verdict["flags"][0].startswith("physics_not_reproduced: ValueError"))
        # The digests are still recorded, so the miss is attributable.
        self.assertIsNotNone(verdict["raw_plist_sha256"])

    def test_without_the_estimator_digests_the_verdict_is_not_a_usable_key(self):
        code, _, _ = self.run_main(estimator=lambda: None)
        self.assertEqual(verdict_script.EXIT_NOT_VERIFIED, code)
        verdict = json.loads(self.output().read_text())
        self.assertEqual(("not_verified", 0.0335, ["estimator_code_unreadable"]),
                         (verdict["status"], verdict["effective_b_fiducial_s"], verdict["flags"]))

    def test_an_artifact_outside_the_directory_or_a_missing_one_is_refused(self):
        manifest = json.loads((self.directory / "manifest.json").read_text())
        del manifest["artifacts"]["events.jsonl"]
        (self.directory / "manifest.json").write_text(json.dumps(manifest))
        self.assertEqual(verdict_script.EXIT_NOT_VERIFIED, self.run_main()[0])
        self.assertEqual(["manifest_omits: events.jsonl"], json.loads(self.output().read_text())["flags"])
        self.output().unlink()
        manifest["artifacts"]["../escape.json"] = "0" * 64
        (self.directory / "manifest.json").write_text(json.dumps(manifest))
        self.assertEqual(verdict_script.EXIT_NOT_VERIFIED, self.run_main()[0])
        self.assertEqual(["artifact_descriptor_invalid"], json.loads(self.output().read_text())["flags"])
        self.assertEqual([], self.seen)

    def test_the_real_verifier_is_the_pinned_estimators(self):
        from joulewise.powermetrics_fiducial import verify_stored_evidence_physics
        self.assertIs(verify_stored_evidence_physics, verdict_script._default_verifier())
        code, _, _ = self.run_main(verifier=verdict_script._default_verifier())
        self.assertEqual(verdict_script.EXIT_NOT_VERIFIED, code)  # synthetic bytes do not reproduce
        self.assertTrue(json.loads(self.output().read_text())["flags"][0].startswith("physics_not_reproduced"))
        digests = verdict_script._default_estimator_digests()
        self.assertTrue(digests and all(len(value) == 64 for value in digests.values()))


# ---------------------------------------------------------------------------
# J3 and row 14: dispatch resolver, desk refusal, lint
# ---------------------------------------------------------------------------

class DispatchResolverTests(unittest.TestCase):
    def test_floor_packs_resolve_every_stage_from_its_own_argv(self):
        """The floor packs carry input_ref null, so the harvest's old resolver saw no members at all."""
        for pack, members in (("alpha", 125), ("beta", 125)):
            with self.subTest(pack=pack):
                self.assertTrue(all(row.get("input_ref") is None for row in tree(pack)["stage_graph"]))
                dispatches = b5_plan.resolve_stage_dispatches(tree(pack), REPO_ROOT)
                self.assertEqual(10, len(dispatches))
                self.assertEqual(members, sum(len(dispatch.run_ids) for dispatch in dispatches))
                self.assertEqual(["bound_runs_root"] + ["claim_runs_root"] * 9,
                                 [dispatch.runs_root_binding for dispatch in dispatches])
                self.assertEqual([], b5_plan.duplicate_dispatches(dispatches))
                self.assertIsNone(b5_plan.dispatch_refusal(dispatches))
                corpus = dispatches[0]
                self.assertEqual("configs/campaigns/neg8_reference_corpus_v5", corpus.config_dir)
                self.assertEqual(tuple(f"neg8-refcorpus-r{index:02d}" for index in range(1, 19)), corpus.run_ids)

    def test_gamma_launches_each_interior_reference_once_after_l10(self):
        # Before L10 the three GAMMA reference stages all launched
        # neg8-window-midpoint into claim_runs_root. L10 gives the two arm
        # midpoints their own diagnostic configs: no duplicate, no refusal.
        dispatches = b5_plan.resolve_stage_dispatches(tree("gamma"), REPO_ROOT)
        self.assertEqual([], b5_plan.duplicate_dispatches(dispatches))
        self.assertIsNone(b5_plan.dispatch_refusal(dispatches))
        interior = {dispatch.stage_id: dispatch.run_ids for dispatch in dispatches
                    if dispatch.stage_id in ("gamma-reference-decode-midpoint", "gamma-reference-arm-boundary",
                                             "gamma-reference-prefill-midpoint")}
        self.assertEqual(3, len(interior))
        self.assertEqual(("neg8-window-midpoint",), interior["gamma-reference-arm-boundary"])
        self.assertEqual(3, len({run_id for run_ids in interior.values() for run_id in run_ids}))

    def test_a_synthetic_duplicate_midpoint_is_still_refused(self):
        # The refusal itself stays: GAMMA's pre-L10 shape (the arm-boundary
        # launch copied onto both arm midpoints) is refused as before.
        graph = copy.deepcopy(tree("gamma"))
        rows = {row["stage_id"]: row for row in graph["stage_graph"]}
        for stage_id in ("gamma-reference-decode-midpoint", "gamma-reference-prefill-midpoint"):
            rows[stage_id]["launch"] = copy.deepcopy(rows["gamma-reference-arm-boundary"]["launch"])
        dispatches = b5_plan.resolve_stage_dispatches(graph, REPO_ROOT)
        self.assertEqual([{"runs_root_binding": "claim_runs_root", "run_id": "neg8-window-midpoint",
                           "stages": ["gamma-reference-decode-midpoint", "gamma-reference-arm-boundary",
                                      "gamma-reference-prefill-midpoint"]}],
                         b5_plan.duplicate_dispatches(dispatches))
        self.assertIn("neg8-window-midpoint into claim_runs_root", b5_plan.dispatch_refusal(dispatches))

    def test_bindings_give_paths_and_run_ids_are_the_runners_bundle_directory_names(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            config = repo / "configs/campaigns/x"
            config.mkdir(parents=True)
            (config / "order_manifest.json").write_text(json.dumps(
                {"executed_order": [{"run_id": "Ref Start.R1"}, {"run_id": "ref-start-r2"}]}))
            graph = copy.deepcopy(tree("alpha"))
            row = next(item for item in graph["stage_graph"] if item["kind"] == "campaign_collection")
            row["launch"]["commands"][0]["argv_template"]["arguments"][0]["value"] = "configs/campaigns/x"
            dispatch = b5_plan.resolve_stage_dispatches({"stage_graph": [row]}, repo,
                                                        bindings={"bound_runs_root": "/runs/bound"})[0]
            self.assertEqual((("ref-start-r1", "ref-start-r2"), "/runs/bound", None),
                             (dispatch.run_ids, dispatch.runs_root, dispatch.error))

    def test_an_unreadable_stage_is_unresolved_never_raised(self):
        graph = copy.deepcopy(tree("alpha"))
        rows = [row for row in graph["stage_graph"] if row["kind"] == "campaign_collection"]
        rows[0]["launch"]["commands"][0]["argv_template"]["arguments"][0]["value"] = "configs/campaigns/absent"
        rows[1]["launch"] = None
        dispatches = b5_plan.resolve_stage_dispatches(graph, REPO_ROOT)
        self.assertIn("order manifest", dispatches[0].error)
        self.assertIsNone(dispatches[0].run_ids)
        self.assertIn("no single campaign command", dispatches[1].error)
        self.assertIn("cannot be resolved", b5_plan.dispatch_refusal(dispatches))
        self.assertEqual([], b5_plan.resolve_stage_dispatches({"stage_graph": "nonsense"}, REPO_ROOT))


class DeskDispatchTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="b5-p2chain-desk-")
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve()
        self.measurement = fake_window.build_checkout(self.root)

    def write(self, pack):
        return b5_plan.write_window_plan(
            fake_window.inputs(self.root, self.measurement, pack, plan_id=f"b5-{pack}-1",
                               t0_epoch_s=(int(time.time()) // 60 + 60) * 60),
            pack_digest=lambda _root: "e" * 64, threshold_defaults=fake_window.threshold_defaults)

    def test_gamma_plans_cleanly_at_the_desk_after_l10(self):
        """L10 gave GAMMA's arm midpoints their own configs, so its plan is written with no duplicate dispatch."""
        record = self.write("gamma")
        self.assertTrue(Path(record["plan"]["path"]).is_file())
        dispatches = record["stage_dispatches"]
        pairs = [(row["runs_root_binding"], run_id) for row in dispatches for run_id in row["run_ids"]]
        self.assertEqual(len(pairs), len(set(pairs)))

    def test_a_duplicate_dispatch_is_refused_at_the_desk_and_nothing_is_written(self):
        """Before: a plan of GAMMA's pre-L10 shape was written and its window would lose two midpoint positions."""
        real = b5_plan.resolve_stage_dispatches

        def pre_l10(tree_, repo_root, **keywords):
            graph = copy.deepcopy(tree_)
            rows = {row["stage_id"]: row for row in graph["stage_graph"]}
            for stage_id in ("gamma-reference-decode-midpoint", "gamma-reference-prefill-midpoint"):
                rows[stage_id]["launch"] = copy.deepcopy(rows["gamma-reference-arm-boundary"]["launch"])
            return real(graph, repo_root, **keywords)

        with mock.patch.object(b5_plan, "resolve_stage_dispatches", side_effect=pre_l10), \
                self.assertRaises(b5_plan.WindowPlanError) as raised:
            self.write("gamma")
        self.assertIn("neg8-window-midpoint into claim_runs_root by gamma-reference-decode-midpoint, "
                      "gamma-reference-arm-boundary, gamma-reference-prefill-midpoint", str(raised.exception))
        self.assertFalse((self.root / "custody").exists())
        self.assertEqual([], list((self.root / "runs").iterdir()))

    def test_the_record_carries_the_dispatch_plan_and_the_collection_deadline(self):
        record = self.write("alpha")
        dispatches = record["stage_dispatches"]
        self.assertEqual(10, len(dispatches))
        self.assertEqual(125, sum(len(row["run_ids"]) for row in dispatches))
        self.assertEqual({"horizon_s": 86400, "post_reserve_s": 1430, "member_allowance_s": 620,
                          "stage_overhead_s": 180, "programmed_span_s": 3600, "margin_s": 86400 - 1430 - 3600,
                          "record": "$NIGHT_DIR/transcript/collection-deadline.json"},
                         record["collection_deadline"])
        plan = json.loads(Path(record["plan"]["path"]).read_text())
        self.assertNotIn("stage_dispatches", plan["hazard_window"])
        self.assertNotIn("collection_deadline", plan["hazard_window"])


class LintTests(unittest.TestCase):
    def run_main(self, *argv):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = check_b5_chain.main(list(argv))
        return code, json.loads(stdout.getvalue())

    def test_the_lint_passes_gamma_after_l10(self):
        # Before L10 the lint failed GAMMA on one duplicate_dispatch (the
        # midpoint launched by 3 stages); L10 removes it and GAMMA checks clean.
        code, report = self.run_main("--pack-root", str(PACKS["gamma"]), "--no-live-identity")
        self.assertEqual((0, []), (code, report["findings"]))
        self.assertIn("duplicate_dispatch", report["checks"])

    def test_a_duplicate_across_two_floor_stages_is_a_finding(self):
        graph = copy.deepcopy(tree("alpha"))
        rows = {row["stage_id"]: row for row in graph["stage_graph"]}
        rows["alpha-reference-end"]["launch"] = copy.deepcopy(rows["alpha-reference-start"]["launch"])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve() / "measurement"
            campaigns = root / "configs/campaigns"
            campaigns.mkdir(parents=True)
            for entry in (REPO_ROOT / "configs").iterdir():
                if entry.name != "campaigns":
                    (root / "configs" / entry.name).symlink_to(entry)
            for entry in (REPO_ROOT / "configs/campaigns").iterdir():
                (campaigns / entry.name).symlink_to(entry)
            pack = campaigns / "b5_dup_dispatch_v5"
            pack.mkdir()
            (pack / "plan_tree.json").write_text(json.dumps(graph))
            report = check_b5_chain.check(graph, pack_root=pack, measurement_root=root,
                                          bindings=check_b5_chain.synthetic_bindings(root, pack), plan_mode=False,
                                          live_identity=False)
        errors = [(item["check"], item["stage_id"]) for item in report["findings"] if item["severity"] == "error"]
        self.assertEqual([("duplicate_dispatch", "alpha-reference-end")] * 3, errors)


# ---------------------------------------------------------------------------
# Row 8: the wall budget
# ---------------------------------------------------------------------------

class BudgetHelperTests(unittest.TestCase):
    def run_helper(self, budget, *argv, grace=1):
        return subprocess.run([sys.executable, "-B", "-c", b5_chain.BUDGET_HELPER, str(budget), str(grace),
                               str(b5_chain.BUDGET_EXPIRED_RC), "--", *argv],
                              capture_output=True, text=True, timeout=120, check=False)

    def test_a_stage_inside_its_budget_keeps_its_exit_code_and_output(self):
        completed = self.run_helper(30, "/bin/sh", "-c", "echo out; echo err >&2; exit 3")
        self.assertEqual((3, "out\n", "err\n"), (completed.returncode, completed.stdout, completed.stderr))
        self.assertEqual(128 + signal.SIGTERM, self.run_helper(30, "/bin/sh", "-c", "kill -TERM $$").returncode)

    def test_an_expired_stage_loses_its_whole_process_tree_and_records_124(self):
        """Before: no budget; a hung reservation or derivation held the chain until the driver's deadline."""
        with tempfile.TemporaryDirectory() as directory:
            pids = Path(directory) / "pids"
            # A child that ignores SIGTERM and a grandchild: both must be gone.
            script = (f"trap '' TERM; /bin/sleep 300 & echo $! > {pids}; echo $$ >> {pids}; wait")
            started = time.monotonic()
            completed = self.run_helper(1, "/bin/sh", "-c", script, grace=1)
            elapsed = time.monotonic() - started
            self.assertEqual(b5_chain.BUDGET_EXPIRED_RC, completed.returncode, completed.stderr)
            self.assertLess(elapsed, 30)
            self.assertIn("wall budget 1 s expired", completed.stderr)
            self.assertIn("survivors none", completed.stderr)
            for pid in map(int, pids.read_text().split()):
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)

    def test_a_missing_program_is_127(self):
        self.assertEqual(127, self.run_helper(5, "/nonexistent/program").returncode)

    def test_the_helper_never_wakes_while_the_stage_runs(self):
        """Review F1: Popen.wait(timeout=...) polls waitpid every 50 ms on Python 3.13, so the helper woke 20
        times a second through the pre-calibration capture it wraps. Now: one blocking waitpid, no sleeps."""
        counting = (
            "import atexit, os, sys, time\n"
            "calls = {'sleep': 0, 'waitpid': 0}\n"
            "_sleep, _waitpid = time.sleep, os.waitpid\n"
            "def sleep(seconds):\n"
            "    calls['sleep'] += 1\n"
            "    return _sleep(seconds)\n"
            "def waitpid(*args):\n"
            "    calls['waitpid'] += 1\n"
            "    return _waitpid(*args)\n"
            "time.sleep, os.waitpid = sleep, waitpid\n"
            "atexit.register(lambda: print('CALLS %d %d' % (calls['sleep'], calls['waitpid']), file=sys.stderr))\n"
            "exec(compile(sys.argv.pop(1), '<budget>', 'exec'))\n")
        completed = subprocess.run([sys.executable, "-B", "-c", counting, b5_chain.BUDGET_HELPER, "60", "1",
                                    str(b5_chain.BUDGET_EXPIRED_RC), "--", "/bin/sleep", "2"],
                                   capture_output=True, text=True, timeout=120, check=False)
        self.assertEqual(0, completed.returncode, completed.stderr)
        sleeps, waits = map(int, completed.stderr.split("CALLS ")[1].split())
        self.assertEqual((0, 1), (sleeps, waits))

    @staticmethod
    def _reap(path):
        for pid in map(int, path.read_text().split()) if path.exists() else ():
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass

    def test_a_descendant_started_after_expiry_is_stopped_too(self):
        """Review F2: one census at expiry missed a descendant started after it (here by the leader's TERM
        handler), which outlived the stage; the census is now re-read through the grace."""
        with tempfile.TemporaryDirectory() as directory:
            late = Path(directory) / "late"
            script = (f"trap '/bin/sleep 300 & echo $! > {late}' TERM; "
                      "while :; do /bin/sleep 0.1; done")
            try:
                completed = self.run_helper(1, "/bin/sh", "-c", script, grace=3)
                self.assertEqual(b5_chain.BUDGET_EXPIRED_RC, completed.returncode, completed.stderr)
                self.assertTrue(late.exists(), completed.stderr)
                time.sleep(0.3)
                with self.assertRaises(ProcessLookupError):
                    os.kill(int(late.read_text()), 0)
                self.assertIn("survivors none", completed.stderr)
            finally:
                self._reap(late)

    def test_an_unreadable_census_never_reports_no_survivors(self):
        """Review F2: when the process census failed the helper still printed "survivors none"."""
        helper = b5_chain.BUDGET_HELPER.replace('"/bin/ps"', '"/usr/bin/false"')
        self.assertNotEqual(helper, b5_chain.BUDGET_HELPER)
        with tempfile.TemporaryDirectory() as directory:
            pids = Path(directory) / "pids"
            try:
                completed = subprocess.run(
                    [sys.executable, "-B", "-c", helper, "1", "1", str(b5_chain.BUDGET_EXPIRED_RC), "--",
                     "/bin/sh", "-c", f"/bin/sleep 300 >/dev/null 2>&1 & echo $! > {pids}; wait"],
                    capture_output=True, text=True, timeout=120, check=False)
                self.assertEqual(b5_chain.BUDGET_EXPIRED_RC, completed.returncode, completed.stderr)
                self.assertNotIn("survivors none", completed.stderr)
                self.assertIn("survivors unknown (process census unavailable)", completed.stderr)
            finally:
                self._reap(pids)

    def test_descendants_keep_the_whole_grace_after_the_leader_exits(self):
        """Review F3: the grace ended as soon as the leader exited, so a worker still saving state on SIGTERM
        was killed at once; now the grace runs until every known process is gone or it has elapsed."""
        with tempfile.TemporaryDirectory() as directory:
            saved, pids = Path(directory) / "saved", Path(directory) / "pids"
            worker = (f"trap '/bin/sleep 1; echo saved > {saved}; exit 0' TERM; "
                      "while :; do /bin/sleep 0.1; done")
            script = (f"/bin/sh -c {shlex.quote(worker)} & echo $! > {pids}; "
                      "trap 'exit 0' TERM; while :; do /bin/sleep 0.1; done")
            try:
                completed = self.run_helper(1, "/bin/sh", "-c", script, grace=10)
                self.assertEqual(b5_chain.BUDGET_EXPIRED_RC, completed.returncode, completed.stderr)
                self.assertEqual("saved\n", saved.read_text() if saved.exists() else None, completed.stderr)
                self.assertIn("survivors none", completed.stderr)
            finally:
                self._reap(pids)


class BudgetRenderTests(ChainFixture):
    def test_every_non_member_stage_but_the_post_capture_and_the_in_shell_screen_is_budgeted(self):
        text = Path(self.plan.chain_path).read_text()
        seen, command = {}, None
        for line in text.splitlines():
            if command is None and line.startswith("run_stage "):
                command = [line]
            elif command is not None:
                command.append(line)
            if command is not None and not line.endswith("\\"):
                words = command[0].split()
                seen[words[1].strip("'")] = (words[2].strip("'"), '"$B5_BUDGET_PY"' in "\n".join(command))
                command = None
        expected_unbudgeted = {"alpha-post-calibration", "alpha-pre-calibration.screen"}
        for label, (kind, budgeted) in seen.items():
            with self.subTest(label=label):
                if kind == "campaign_collection" or label in expected_unbudgeted:
                    self.assertFalse(budgeted)
                else:
                    self.assertTrue(budgeted)
        self.assertIn("alpha-bracket-reservation", seen)
        self.assertIn("alpha-bound-derivation", seen)
        self.assertIn("alpha-post-calibration.session-status", seen)
        # The reservation's budget, the grace and the expiry code, then the stage argv.
        self.assertIn("\n    900 \\\n    30 \\\n    124 \\\n    -- ", text)
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(all(row["rc"] == 0 for row in self.journal()))


# ---------------------------------------------------------------------------
# Row 17: the collection deadline
# ---------------------------------------------------------------------------

class HorizonPassedTests(ChainFixture):
    horizon_s = 0

    def test_past_the_deadline_every_collection_is_skipped_and_the_post_capture_still_runs(self):
        """Before: the chain launched every stage whatever the horizon (render_chain had no deadline)."""
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        rows = self.journal()
        skipped = [row["stage_id"] for row in rows if row["kind"] == "horizon_skipped"]
        collections = [stage.stage_id for stage in b5_chain.stage_plan(tree("alpha"))
                       if stage.kind in ("campaign_collection", "bound_derivation")]
        self.assertEqual(collections, skipped)
        self.assertTrue(all(row["rc"] == b5_chain.HORIZON_SKIPPED_RC for row in rows
                            if row["kind"] == "horizon_skipped"))
        tools = [call["tool"] for call in fake_window.calls(self.measurement)]
        self.assertEqual(["reserve", "fiducial", "verdict", "fiducial", "session_status"], tools)
        status = {row["stage_id"]: row["rc"] for row in rows}
        self.assertEqual(0, status["alpha-post-calibration"])
        # One flag, at the first skip (the fake checkout has no flags core, so it is in the log).
        flags = self.unwritten_flags()
        self.assertEqual(["roster.horizon_truncated"], [flag["code"] for flag in flags])
        self.assertEqual(("alpha-bound-collection", 125), (flags[0]["observed"]["first_stage_skipped"],
                                                           flags[0]["observed"]["members_not_launched"]))
        deadline = json.loads((self.night / "transcript" / b5_chain.COLLECTION_DEADLINE_RECORD).read_text())
        self.assertEqual(deadline["pre_capture_started_epoch_s"] - b5_chain.HORIZON_POST_RESERVE_S,
                         deadline["deadline_epoch_s"])
        self.assertEqual(flags[0]["observed"]["deadline_epoch_s"], deadline["deadline_epoch_s"])


class HorizonMidChainTests(ChainFixture):
    # Room for the corpus (18 members), the derivation, the start references and the
    # 10-member absolute stage, but not for a 20-member stage.
    horizon_s = property(lambda self: b5_chain.HORIZON_POST_RESERVE_S
                         + 18 * b5_chain.HORIZON_MEMBER_ALLOWANCE_S + 240 + 600)

    def test_the_first_stage_that_cannot_finish_ends_collection_even_for_later_small_stages(self):
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        rows = self.journal()
        ran = [row["stage_id"] for row in rows if row["kind"] == "campaign_collection"]
        self.assertEqual(["alpha-bound-collection", "alpha-reference-start", "alpha-science-absolute"], ran)
        skipped = [row["stage_id"] for row in rows if row["kind"] == "horizon_skipped"]
        self.assertEqual(["alpha-science-abba-01-05", "alpha-science-abba-06-10", "alpha-reference-midpoint",
                          "alpha-science-prefill-p2048-absolute", "alpha-science-prefill-p2048-abba-01-05",
                          "alpha-science-prefill-p2048-abba-06-10", "alpha-reference-end"], skipped)
        self.assertEqual(0, {row["stage_id"]: row["rc"] for row in rows}["alpha-post-calibration"])
        flags = self.unwritten_flags()
        self.assertEqual(1, len(flags))
        self.assertEqual(("alpha-science-abba-01-05", 94), (flags[0]["observed"]["first_stage_skipped"],
                                                            flags[0]["observed"]["members_not_launched"]))

    def test_the_command_line_horizon_is_24_hours(self):
        self.assertEqual(86400, b5_chain.CALIBRATION_HORIZON_S)
        self.assertGreaterEqual(b5_chain.HORIZON_MEMBER_ALLOWANCE_S, 619)  # block 4's larger member allowance


class FlagHelperTests(unittest.TestCase):
    def run_helper(self, runs_root, code="roster.horizon_truncated", level="window", run_id="",
                   observed='{"first_stage_skipped": "x"}'):
        stderr = io.StringIO()
        argv = ["-c", str(runs_root), b5_chain.CHAIN_FLAG_WRITER, code, level, run_id, observed, "detail"]
        exit_code = 0
        handler = signal.getsignal(signal.SIGALRM)
        try:
            with mock.patch.object(sys, "argv", argv), contextlib.redirect_stderr(stderr):
                try:
                    exec(compile(b5_chain.FLAG_HELPER, "<b5-flag-helper>", "exec"), {"__name__": "__main__"})
                except SystemExit as exc:
                    exit_code = exc.code
            # The helper disarms its own deadline on every exit (it runs in-process here).
            self.assertEqual((0.0, 0.0), signal.getitimer(signal.ITIMER_REAL))
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, handler)
        return exit_code, stderr.getvalue()

    def test_a_chain_flag_lands_in_the_custody_flag_file_with_the_window_plans_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            custody = base / "custody"
            runs = hazard_root(base, custody, plan={"plan_id": "b5-alpha-1", "hazard_window": {"attempt": 2}})
            self.assertEqual(0, self.run_helper(runs)[0])
            self.assertEqual(0, self.run_helper(runs, code="member.retried", level="member",
                                                run_id="neg8-refcorpus-r03", observed='{"attempt": 2}')[0])
            lines = (custody / "flags" / f"{b5_chain.CHAIN_FLAG_WRITER}.jsonl").read_text().splitlines()
            flags = [json.loads(line) for line in lines]
            for flag in flags:
                self.assertEqual([], validate_flag(flag))
                self.assertEqual(("ROSTER", "REPRESENTATION", "b5-alpha-1"),
                                 (flag["family"], flag["klass"], flag["scope"]["plan_id"]))
            self.assertEqual(["roster.horizon_truncated", "member.retried"], [flag["code"] for flag in flags])
            self.assertEqual(("member", "neg8-refcorpus-r03"),
                             (flags[1]["scope"]["level"], flags[1]["scope"]["run_id"]))

    def test_a_root_without_the_hazard_locator_prints_the_whole_flag_behind_the_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            code, stderr = self.run_helper(directory)
        self.assertEqual(1, code)
        self.assertTrue(stderr.startswith(flags_core.UNWRITTEN_MARKER))
        self.assertEqual("roster.horizon_truncated", json.loads(stderr[len(flags_core.UNWRITTEN_MARKER):])["code"])

    def test_the_chain_codes_are_classified_in_the_core_table(self):
        for code in ("roster.horizon_truncated", "member.retried"):
            self.assertEqual(("ROSTER", "REPRESENTATION"), flags_core.CORE_FLAG_CODES[code])

    def test_a_write_blocked_past_its_deadline_prints_the_flag_behind_the_marker(self):
        """Review F4: a writer blocked on the flag-file lock was killed by its wall budget before core.emit
        could print the marker, so the flag vanished. The writer now has its own deadline inside the budget."""
        self.assertLess(b5_chain.FLAG_WRITE_DEADLINE_S + b5_chain.BUDGET_GRACE_S,
                        b5_chain.STAGE_WALL_BUDGET_S["flag_record"])
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            custody = base / "custody"
            runs = hazard_root(base, custody, plan={"plan_id": "b5-alpha-1", "hazard_window": {"attempt": 2}})
            path = custody / "flags" / f"{b5_chain.CHAIN_FLAG_WRITER}.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            import fcntl

            with open(path, "ab") as held:
                fcntl.flock(held.fileno(), fcntl.LOCK_EX)
                try:
                    completed = subprocess.run(
                        [sys.executable, "-B", "-c", b5_chain.FLAG_HELPER, str(runs), b5_chain.CHAIN_FLAG_WRITER,
                         "member.retried", "member", "neg8-refcorpus-r03", '{"attempt": 2}', "detail", "1"],
                        capture_output=True, text=True, timeout=60, check=False, cwd=REPO_ROOT,
                        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)})
                finally:
                    fcntl.flock(held.fileno(), fcntl.LOCK_UN)
        self.assertEqual(1, completed.returncode, completed.stderr)
        self.assertTrue(completed.stderr.startswith(flags_core.UNWRITTEN_MARKER), completed.stderr)
        value = json.loads(completed.stderr[len(flags_core.UNWRITTEN_MARKER):].splitlines()[0])
        self.assertEqual(("member.retried", "member", "neg8-refcorpus-r03", {"attempt": 2}),
                         (value["code"], value["level"], value["run_id"], value["observed"]))

    def test_a_writer_the_budget_kills_still_leaves_the_marker_in_the_chain_log(self):
        """Review F4: when the wall budget stops the writer, the chain prints the marker itself."""
        prelude = (b5_chain._PRELUDE_GATE_PRUNE_2.replace("@FLAG_BUDGET@", "1").replace("@GRACE@", "1")
                   .replace("@EXPIRED@", str(b5_chain.BUDGET_EXPIRED_RC)).replace("@WRITER@", "b5-chain")
                   .replace("@HORIZON@", "86400").replace("@RESERVE@", "1430").replace("@SKIPPED@", "75"))
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "chain.log"
            script = "\n".join([
                f"PY={shlex.quote(sys.executable)}", f"CHAIN_LOG={shlex.quote(str(log))}",
                f"B5_BUDGET_PY={shlex.quote(b5_chain.BUDGET_HELPER)}",
                "B5_FLAG_PY='import time; time.sleep(60)'",  # a writer that never reaches its marker
                prelude,
                'flag member.retried member neg8-refcorpus-r03 \'{"attempt":2}\' /nonexistent "detail"',
                "print -r -- rc=$?"])
            completed = subprocess.run(["/bin/zsh", "-f", "-c", script], capture_output=True, text=True,
                                       timeout=60, check=False)
            self.assertIn(f"rc={b5_chain.BUDGET_EXPIRED_RC}", completed.stdout, completed.stderr)
            lines = [line for line in log.read_text().splitlines() if line.startswith(flags_core.UNWRITTEN_MARKER)]
        self.assertEqual(1, len(lines), log)
        value = json.loads(lines[0][len(flags_core.UNWRITTEN_MARKER):])
        self.assertEqual(("member.retried", "member", "neg8-refcorpus-r03", {"attempt": 2}),
                         (value["code"], value["level"], value["run_id"], value["observed"]))


# ---------------------------------------------------------------------------
# Row 13: one corpus retry (no drain)
# ---------------------------------------------------------------------------

CORPUS = [f"neg8-refcorpus-r{index:02d}" for index in range(1, 19)]


class CorpusRetrySnapshotTests(unittest.TestCase):
    def test_the_snapshot_before_the_retry_is_written_once(self):
        """Review E2: a second count never replaces the snapshot that says which members the retry measured."""
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            manifest = base / "manifest.json"
            manifest.write_text(json.dumps({"members": [{"bundle_id": "m1", "bundle_path": "m1"}]}))
            snapshot = base / "snapshot.json"
            argv = [sys.executable, "-B", "-c", b5_chain.CORPUS_RETRY_HELPER, "count", str(manifest), str(base),
                    str(snapshot), "10"]
            first = subprocess.run(argv, capture_output=True, text=True, timeout=60, check=False)
            self.assertEqual((0, "retry\n"), (first.returncode, first.stdout), first.stderr)
            before = snapshot.read_bytes()
            (base / "m1").mkdir()
            (base / "m1/summary_metrics.json").write_text(json.dumps({"status": "succeeded"}))
            second = subprocess.run(argv, capture_output=True, text=True, timeout=60, check=False)
            self.assertNotEqual(0, second.returncode)
            self.assertIn("FileExistsError", second.stderr)
            self.assertEqual(before, snapshot.read_bytes())


class CorpusRetryTests(ChainFixture):
    behavior = {"refuse_once_run_ids": CORPUS[2:11], "neg8_minimum_n": whole_window.NEG8_DRIFT_MINIMUM_N}

    def test_nine_pre_bundle_refusals_are_measured_by_one_retry_and_flagged(self):
        """Before: 9 of 18 left the bound underived (neg8.bound_not_derived, the whole window excluded)."""
        self.assertEqual(whole_window.NEG8_DRIFT_MINIMUM_N, b5_chain.NEG8_RETRY_MINIMUM)
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        rows = [row for row in self.journal() if row["stage_id"].startswith("alpha-bound-")]
        self.assertEqual([("alpha-bound-collection", "campaign_collection", 1),
                          ("alpha-bound-collection.retry-decision", "neg8_corpus_retry_decision", 0),
                          ("alpha-bound-collection.retry", "campaign_collection", 0),
                          ("alpha-bound-derivation.corpus", "neg8_corpus_collected", 0),
                          ("alpha-bound-derivation", "bound_derivation", 0)],
                         [(row["stage_id"], row["kind"], row["rc"]) for row in rows])
        corpus_calls = [call for call in fake_window.calls(self.measurement)
                        if call["tool"] == "collect" and call["config_dir"].endswith("neg8_reference_corpus_v5")]
        self.assertEqual(2, len(corpus_calls))
        self.assertEqual(CORPUS[2:11], corpus_calls[0]["refused_before_bundle"])
        self.assertEqual(CORPUS[2:11], corpus_calls[1]["attempted"])
        # The retry re-ran the same stage argv into the same bound root.
        self.assertEqual(corpus_calls[0]["max_failures"], corpus_calls[1]["max_failures"])
        derive = next(call for call in fake_window.calls(self.measurement) if call["tool"] == "derive")
        self.assertEqual((18, True), (derive["members"], derive["ok"]))
        snapshot = json.loads((self.night / "transcript" / b5_chain.NEG8_RETRY_SNAPSHOT).read_text())
        self.assertEqual(("retry", 9, 10), (snapshot["decision"], snapshot["succeeded"], snapshot["minimum"]))
        flags = self.unwritten_flags()
        self.assertEqual([("member.retried", run_id) for run_id in CORPUS[2:11]],
                         [(flag["code"], flag["run_id"]) for flag in flags])
        log = Path(self.plan.hazard_window["bindings"]["operator_log_root"]) / "03-alpha-bound-collection.retry.log"
        self.assertTrue(log.is_file())

    def test_the_retry_decision_counts_only_members_that_succeeded(self):
        fake_window.set_behavior(self.measurement, {"refuse_once_run_ids": CORPUS[:8]})
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        ids = [row["stage_id"] for row in self.journal()]
        self.assertIn("alpha-bound-collection.retry-decision", ids)
        self.assertNotIn("alpha-bound-collection.retry", ids)  # 10 succeeded: no retry
        self.assertEqual([], self.unwritten_flags())
        derive = next(call for call in fake_window.calls(self.measurement) if call["tool"] == "derive")
        self.assertEqual(10, derive["members"])

    def test_a_failed_bundle_is_never_re_measured_and_nothing_is_flagged(self):
        fake_window.set_behavior(self.measurement, {"fail_run_ids": CORPUS[:9]})
        completed = self.run_chain()
        self.assertEqual(0, completed.returncode, completed.stderr)
        corpus_calls = [call for call in fake_window.calls(self.measurement)
                        if call["tool"] == "collect" and call["config_dir"].endswith("neg8_reference_corpus_v5")]
        self.assertEqual(2, len(corpus_calls))
        self.assertEqual([], corpus_calls[1]["attempted"])
        self.assertEqual([], self.unwritten_flags())
        bound = Path(self.plan.hazard_window["runs_roots"]["bound"])
        for run_id in CORPUS[:9]:
            self.assertEqual("failed", json.loads((bound / run_id / "summary_metrics.json").read_text())["status"])
        rows = {row["stage_id"]: row["rc"] for row in self.journal()}
        self.assertNotEqual(0, rows["alpha-bound-derivation"])
        self.assertEqual(0, rows["alpha-post-calibration"])


class SizingCrossCheckTests(unittest.TestCase):
    """The chain's deadline and budgets against the committed block-5 sizing they must cover."""

    def test_the_chain_allowances_cover_the_sizing_terms(self):
        sizing = json.loads((REPO_ROOT / "configs/campaigns/v5_claim_25g83/sizing_b5.json").read_text())
        terms = sizing["terms"]
        self.assertGreaterEqual(b5_chain.HORIZON_MEMBER_ALLOWANCE_S, max(terms["member_allowance_s"].values()))
        self.assertEqual(b5_chain.SETTLE_S + terms["pre_post_calibration"]["seconds"] + 600,
                         b5_chain.HORIZON_POST_RESERVE_S)
        self.assertEqual(terms["stage_custody_formula"]["stage_overhead_s"], b5_chain.HORIZON_STAGE_OVERHEAD_S)
        for budget, term in (("bound_derivation", "bound_derivation"), ("neg8_corpus_collected", "corpus_prune"),
                             ("window_calibration_verdict", "window_calibration_verdict")):
            self.assertGreaterEqual(b5_chain.STAGE_WALL_BUDGET_S[budget], terms[term]["seconds"])
        self.assertEqual(b5_chain.COLLECTION_ARM_COUNTDOWN_S, terms["collection_arm_countdown_s"]["seconds"])


if __name__ == "__main__":
    unittest.main()
