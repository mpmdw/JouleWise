"""SYNTHETIC ONLY. Real launch-to-close orchestration; no hardware or process signalling."""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from copy import deepcopy
from dataclasses import replace
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, call, patch

from joulewise.cadence import ctl, kit as kits, legs, desk, queue
from joulewise.align.apple import cadence_ctl, r1_runtime as rt, workload
from scripts import cadence_legs_runner as runner, cadence_queue, launch_cadence_span as launcher
from tests.cadence import test_kit_v11 as v11_tests
from tests.cadence.test_legs_runner import local, NEW_WINDOW

KIT = runner.ROOT / "docs/process/cadence/kits/cl-ctl-01.draft.json"


def draft():
    return kits.load_kit(KIT, batch_window=NEW_WINDOW[0])[0]


def specs(kit=None):
    kit = kit or draft()
    return [s for ids in kit["layout"] for s in legs.leg_specs(kit,ids)]


class KitTests(unittest.TestCase):
    def test_draft_is_unfrozen_and_doses_are_data(self):
        kit = draft()
        self.assertEqual(kit["status"], "draft")
        self.assertFalse(kit["ruling"]["authorizes_spans"])
        self.assertEqual(sorted(s["hidden_tokens"] for s in kit["seed_law"]["scripts"] if s["kind"] == "hidden"),
                         [128,128,256,256,512,512])
        altered = deepcopy(kit)
        for s in altered["seed_law"]["scripts"]:
            if s["hidden_tokens"] == 128:
                s["hidden_tokens"] = 192
        altered["legs"] = ctl.generate_legs(altered["campaign_id"], altered["seed_law"], altered["leg_defaults"])
        ctl.validate_kit(altered)  # no runner hardcoding of a dose that lm-inst-01 may change

    def test_rl186_parameters_remain_draft_and_follow_the_read(self):
        kit = draft()
        original = deepcopy(kit)
        for gpu, dc_in, dose, recovery, lag, gap, prompt_sizes, prefill in (
            (True, False, (128, 256, 512), 120, 2, 10, [2048, 2000], 2000),
            (False, True, (128, 256, 512), 600, 2.01, 11, [2016, 2048], 2016),
            (True, True, (192, 384, 768), 126.25, 2.2, 11, [1872, 2048], 2048),
        ):
            with self.subTest(gpu=gpu, dc_in=dc_in):
                return_time = {120: 20, 600: 140, 126.25: 25.25}[recovery]
                updated = ctl.apply_instrument_read(
                    kit, below_gpu_floor=gpu, below_dc_in_floor=dc_in, return_time_s=return_time,
                    decode_end_lag_s=lag, prompt_sizes=prompt_sizes, raised_doses=dose if gpu and dc_in else None)
                scripts = updated["seed_law"]["scripts"]
                self.assertEqual(sorted(s["hidden_tokens"] for s in scripts if s["kind"] == "hidden"),
                                 sorted(dose * 2))
                self.assertEqual({s["recovery_s"] for s in scripts}, {recovery})
                self.assertEqual(next(s["gap_s"] for s in scripts if s["kind"] == "split"), gap)
                self.assertEqual(updated["leg_defaults"]["prefill_tokens"], prefill)
                self.assertEqual(updated["status"], "draft")
                self.assertFalse(updated["ruling"]["authorizes_spans"])
                self.assertEqual(updated["frozen"], kit["frozen"])
                self.assertEqual(updated["layout"], kit["layout"])
                self.assertEqual([leg["seed"] for leg in updated["legs"]], [leg["seed"] for leg in kit["legs"]])
        self.assertEqual(kit, original)

    def test_rl186_read_refuses_to_choose_raised_doses_or_break_a_prompt_tie(self):
        facts = dict(below_gpu_floor=True, below_dc_in_floor=True, return_time_s=60,
                     decode_end_lag_s=2, prompt_sizes=[2000])
        with self.assertRaisesRegex(kits.KitError, "three raised doses from the research lead"):
            ctl.apply_instrument_read(draft(), **facts)
        with self.assertRaisesRegex(kits.KitError, "only when both floors"):
            ctl.apply_instrument_read(draft(), **{**facts, "below_gpu_floor": False}, raised_doses=(192, 384, 768))
        with self.assertRaisesRegex(kits.KitError, "tie for nearest prompt size"):
            ctl.apply_instrument_read(draft(), **{**facts, "below_gpu_floor": False, "prompt_sizes": [1900, 2100]})

    def test_rl186_rejects_changes_to_the_ruled_shape_and_master_seed(self):
        kit = draft()
        kit["seed_law"]["master_seed"] += 1
        with self.assertRaisesRegex(kits.KitError, "master_seed"):
            ctl.validate_kit(kit)
        kit = draft()
        next(s for s in kit["seed_law"]["scripts"] if s["cpu_s"] == 90)["cpu_s"] = 120
        with self.assertRaisesRegex(kits.KitError, "RL-186 CPU doses"):
            ctl.validate_kit(kit)

    def test_seed_law_refuses_reorder_and_bad_scripts(self):
        kit = draft()
        kit["legs"].reverse()
        with self.assertRaisesRegex(kits.KitError, "seed law"):
            ctl.validate_kit(kit)
        for change in ({"cpu_s": -1}, {"hidden_tokens": True}, {"turn_tokens": []}, {"unknown": 1}):
            s = {**draft()["seed_law"]["scripts"][0], **change}
            with self.assertRaises(kits.KitError):
                ctl.validate_script(s)

    def test_nine_leg_ceiling_and_total_script_budget(self):
        kit = draft()
        for ids in (["L001","L002","L003"], [f"L{i:03d}" for i in range(4,13)]):
            p = legs.plan_span(kit,t0_epoch=local("2026-11-17T02:40"),windows=NEW_WINDOW,leg_ids=ids,
                               max_span_s=runner.max_span_s())
            self.assertLessEqual(p["worst_case_s"],runner.max_span_s())
            self.assertEqual(p["legs"][0]["g0_role"], "capture")
            self.assertTrue(all(s["g0_role"] == "consume" for s in p["legs"][1:]))
            for s in p["legs"]:
                no_tail = deepcopy(s)
                no_tail["script"]["recovery_s"] = 0
                self.assertAlmostEqual(legs.leg_expected_s(s)-legs.leg_expected_s(no_tail),600)
        with self.assertRaisesRegex(legs.PlanError,"legs_per_span"):
            legs.plan_span(kit,t0_epoch=local("2026-11-17T02:40"),windows=NEW_WINDOW)

    def test_production_refuses_draft_before_a_git_or_host_command(self):
        with patch.object(runner.subprocess,"run",side_effect=AssertionError("host command")):
            with self.assertRaisesRegex(runner.SpanRefusal,"DRAFT"):
                runner.verify_frozen_production(draft())

    def test_spec_requires_exact_logged_total_and_closed_keys(self):
        spec = specs()[0]
        for change in ({"decode_tokens":1},{"extra":False}):
            with self.assertRaises(legs.PlanError):
                legs.validate_leg_spec({**spec,**change})

    def test_layout_keeps_doses_and_pair_on_consumer_references(self):
        kit = draft()
        all_specs = specs(kit)
        self.assertEqual([s["script"]["kind"] for s in all_specs if s["g0_role"]=="capture"],
                         ["extra-turn","cpu"])
        self.assertTrue(all(s["g0_role"]=="consume" for s in all_specs
                            if s["script"]["kind"] in {"hidden","plain","split"}))
        pair = [i for i,s in enumerate(all_specs) if s["script"]["kind"] in {"plain","split"}]
        self.assertEqual(pair[1]-pair[0],1)
        for field in ("seed", "prefill_chars", "decode_tokens"):
            self.assertEqual(all_specs[pair[0]][field], all_specs[pair[1]][field])
        kit["legs"][pair[1]]["seed"] += 1
        with self.assertRaisesRegex(kits.KitError, "script seed law"):
            ctl.validate_kit(kit)
        kit["legs"][pair[1]]["seed"] -= 1
        for ids in (["L001"],["L006","L007"],["L003","L004"]):
            with self.assertRaisesRegex(legs.PlanError,"layout"):
                legs.leg_specs(kit,ids)

    def test_malformed_ctl_documents_refuse_as_kit_errors(self):
        for field,value in (("runner",[]),("status",[]),("seed_law",None),("span_template",False)):
            with self.assertRaises(kits.KitError):
                ctl.validate_kit({**draft(),field:value})
        with self.assertRaises(kits.KitError):
            ctl.validate_script({**draft()["seed_law"]["scripts"][0],"kind":[]})

    def test_a_script_beyond_the_shared_deadman_limit_refuses_at_validation(self):
        spec = deepcopy(specs()[0])
        spec.update(prefill_tokens=32768,prefill_chars=legs.prefill_chars(32768),decode_tokens=4096)
        spec["script"].update(turn_tokens=[2048,2048],recovery_s=600)
        # Additive budget must fit; a large split with long gaps cannot be silently truncated.
        spec["script"].update(kind="split",turn_tokens=[1366,1365,1365],gap_s=600)
        with self.assertRaisesRegex(legs.PlanError,"deadman limit"):
            legs.validate_leg_spec(spec)

    def test_launch_refuses_draft_before_publishing_a_fence(self):
        from types import SimpleNamespace
        import time
        args = SimpleNamespace(magistrate_pid=999,deadline=time.time()+40000,output=Path("/nonexistent/ctl-out"),
                               kit=KIT,legs="L001,L002,L003",batch_window="02:00-02:35")
        with patch.object(launcher.base,"pid_alive",side_effect=AssertionError("host probe")), \
             patch.object(launcher,"cadence_plan",side_effect=AssertionError("plan")), \
             patch.object(launcher.base,"write_fence",side_effect=AssertionError("fence")):
            with self.assertRaisesRegex(kits.KitError,"DRAFT"):
                launcher.launch(args)


class LaunchAuthorityTests(unittest.TestCase):
    now = int(local("2026-11-19T00:00"))
    ns = runner.NS_PER_SECOND
    span_id = "ctl-01-s01"

    def setUp(self):
        kit = draft()
        kit.update(status="issued", frozen={"commit": "a" * 40, "paths": {kit["runner"]["entry"]: "1" * 64}})
        kit["ruling"]["authorizes_spans"] = True
        self.root = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.kit_path = self.root / "synthetic-issued.json"
        self.kit_path.write_text(json.dumps(kit))
        self.approved_sha = hashlib.sha256(self.kit_path.read_bytes()).hexdigest()
        self.output = self.root / "out"
        self.fence_root = self.root / "fence"
        self.ledger = self.root / "ledger.json"
        self.receipt = self.root / "close.json"
        self.enterContext(patch.dict(os.environ, {"CLOSE_PROOF_RECEIPT": str(self.receipt), "HOST_RESTORE_OK": "1",
                                                 "FEEDS_STOPPED": "1", "GROUPS_ABSENT": "1",
                                                 "FOREIGN_PROCESSES_ABSENT": "1"}))
        self.close_ns = self.now * self.ns
        self.prior = {"sequence": 1, "span_id": "previous", "close_receipt": str(self.receipt)}
        self.ledger.write_text(json.dumps({"attempts": [self.prior]}))
        self.write_close(self.close_ns)
        self.argv = ["launch", "--repo", str(runner.ROOT), "--kit", str(self.kit_path), "--output", str(self.output),
                     "--legs", "L001,L002,L003", "--python-bin", sys.executable, "--disk-path", str(self.root),
                     "--custody-root", str(self.fence_root), "--magistrate-pid", "234",
                     "--deadline", str(self.now + 40000), "--launchctl-bin", "synthetic-launchctl",
                     "--kit-sha256", self.approved_sha]
        self.proof = [("--attempt-ledger", str(self.ledger)), ("--previous-close-receipt", str(self.receipt)),
                      ("--span-id", self.span_id), ("--t0-not-before-ns", str(self.close_ns))]

    def write_close(self, epoch_ns):
        self.receipt.write_text(json.dumps({"span_id": "previous", "ended": {"epoch_ns": epoch_ns},
                                           "restore_readbacks": {"synthetic": True}}))

    def launch(self, pairs, *extra):
        with redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(launcher.main(self.argv + [item for pair in pairs for item in pair] + list(extra)), 2)
        return stderr.getvalue()

    def test_ctl_requires_full_close_authority_without_calendar_arguments(self):
        with (patch.object(runner.RealClock, "arm_anchor_ns", side_effect=AssertionError("clock anchor")),
              patch.object(launcher.base, "pid_alive", side_effect=AssertionError("host probe"))):
            for i, (flag, _) in enumerate(self.proof):
                with self.subTest(omitted=flag):
                    self.assertIn("ledger-backed launch requires", self.launch(self.proof[:i] + self.proof[i + 1:]))
            self.assertIn("ledger-backed launch requires", self.launch(self.proof[2:]))
            refusal = self.launch(self.proof, "--authorized-t0-date", "2026-11-19")
            self.assertIn("ctl has free t0", refusal)
        self.assertFalse(self.fence_root.exists())

    def test_ctl_reproves_close_and_records_attempt_before_bootstrap(self):
        actual_lock = launcher.base.fence_lock

        @contextmanager
        def change_close_under_lock(root):
            with actual_lock(root):
                self.write_close(self.close_ns + 1)
                yield

        pending = {"sequence": 2, "span_id": self.span_id,
                   "close_receipt": str(self.output / runner.RECEIPT_NAME)}
        anchor = (self.close_ns, 1000 * self.ns, 1000 * self.ns)
        child = []

        def synthetic_service(command, **_kwargs):
            self.assertEqual(command[0], "synthetic-launchctl")
            if command[1] == "bootstrap":
                self.assertEqual(json.loads(self.ledger.read_text())["attempts"], [self.prior, pending])
                child.extend(json.loads(Path(command[3]).with_name("runner.json").read_text())["argv"])
                raise subprocess.CalledProcessError(19, command)
            self.assertEqual(command[1], "bootout")
            return subprocess.CompletedProcess(command, 0, b"", b"")

        with (patch.object(launcher.base, "pid_alive", return_value=True),
              patch.object(launcher.time, "time", return_value=self.now),
              patch.object(runner.RealClock, "arm_anchor_ns", return_value=anchor),
              patch.object(launcher.subprocess, "run", side_effect=synthetic_service) as service):
            with patch.object(launcher.base, "fence_lock", side_effect=change_close_under_lock):
                self.assertIn("close proof changed before launch", self.launch(self.proof))
            service.assert_not_called()
            self.assertEqual(json.loads(self.ledger.read_text())["attempts"], [self.prior])
            self.write_close(self.close_ns)
            self.assertIn("returned non-zero exit status 19", self.launch(self.proof))
            self.assertEqual([call.args[0][1] for call in service.call_args_list], ["bootstrap", "bootout"])
        self.assertIsNone(launcher.base.read_fence(self.fence_root))
        self.assertEqual(json.loads(self.ledger.read_text())["attempts"], [self.prior, pending])
        self.assertNotIn("--authorized-t0-date", child)
        self.assertEqual(child[child.index("--t0-anchor") + 1], ":".join(map(str, anchor)))
        self.assertEqual(child[child.index("--t0-not-before-ns") + 1], str(self.close_ns))
        self.check_child_close_bound(child[2:])

    def revised_dose_kit(self):
        old = json.loads(self.kit_path.read_bytes())
        revised = ctl.apply_instrument_read(draft(), below_gpu_floor=True, below_dc_in_floor=True,
                                            raised_doses=(192, 384, 768), return_time_s=120,
                                            decode_end_lag_s=2, prompt_sizes=[2000])
        revised.update(status=old["status"], frozen=old["frozen"], ruling=old["ruling"])
        self.assertEqual((specs(old)[1]["script"]["hidden_tokens"], specs(revised)[1]["script"]["hidden_tokens"]),
                         (512, 768))
        return ctl.validate_kit(revised)

    def test_ctl_refuses_kit_revision_between_queue_and_launch(self):
        queue_file = self.root / "queue.json"
        queue_file.write_text(json.dumps({
            "schema": queue.SCHEMA, "queue_id": "cq-ctl-audit", "expires_at": "2026-11-20T00:00:00Z",
            "halt": None, "standing_notice": None, "spans": [
                {"seq": 1, "span_id": self.span_id, "block_id": "cl-ctl-01",
                 "kit": {"path": self.kit_path.name, "sha256": self.approved_sha},
                 "legs": ["L001", "L002", "L003"], "attempt": 1, "not_before": "2026-11-19"},
            ],
        }))
        obs = self.root / "observations.json"
        obs.write_text(json.dumps({**v11_tests.FreeT0Checklist.GOOD, "kit_sha256": self.approved_sha,
                                   "t0_epoch_s": self.now, "end_by_epoch_s": self.now + 40000}))
        validate = ["validate-queue", str(queue_file), "--kits-root", str(self.root)]
        check = ["checklist", "--kit", str(self.kit_path), "--observations", str(obs),
                 "--kit-sha256", self.approved_sha]
        with redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(cadence_queue.main(validate), 0, stdout.getvalue())
            self.assertEqual(cadence_queue.main(check), 0, stdout.getvalue())

        with (patch.object(launcher.base, "pid_alive") as host,
              patch.object(runner.RealClock, "arm_anchor_ns") as arm,
              patch.object(launcher.subprocess, "run") as service):
            approved_argv = self.argv[:]
            self.argv = approved_argv[:-2]
            self.assertIn("requires --kit-sha256", self.launch(self.proof))
            self.assertIn("requires --kit-sha256", self.launch(self.proof, "--kit-sha256", "bad"))
            self.argv = approved_argv
            self.kit_path.write_text(json.dumps(self.revised_dose_kit()))
            with redirect_stdout(io.StringIO()) as stdout:
                self.assertEqual(cadence_queue.main(validate), 1)
                self.assertEqual(cadence_queue.main(check), 1)
                self.assertIn("kit hash differs from the queue-approved kit", stdout.getvalue())
            self.assertIn("kit hash differs from the queue-approved kit", self.launch(self.proof))
            self.kit_path.write_text(json.dumps(v11_tests.v11_kit()))
            self.assertIn("different runner kind", self.launch(self.proof))
            host.assert_not_called()
            arm.assert_not_called()
            service.assert_not_called()
        self.assertFalse(self.fence_root.exists())
        self.assertFalse(self.output.exists())
        self.assertEqual(json.loads(self.ledger.read_text())["attempts"], [self.prior])

    def test_ctl_refuses_kit_revision_between_launch_and_child(self):
        child = []

        def bootstrap(command, **_kwargs):
            self.assertEqual(command[:2], ["synthetic-launchctl", "bootstrap"])
            child.extend(json.loads(Path(command[3]).with_name("runner.json").read_text())["argv"])
            fence = launcher.base.read_fence(self.fence_root)
            launcher.base.write_fence(self.fence_root, {**fence, "pid": 345})
            return subprocess.CompletedProcess(command, 0)

        with (patch.object(launcher.base, "pid_alive", return_value=True),
              patch.object(launcher.time, "time", return_value=self.now),
              patch.object(runner.RealClock, "arm_anchor_ns", return_value=(self.close_ns, self.ns, self.ns)),
              patch.object(launcher.subprocess, "run", side_effect=bootstrap), redirect_stdout(io.StringIO())):
            self.assertEqual(launcher.main(self.argv + [item for pair in self.proof for item in pair]), 0)
        self.assertEqual(child[child.index("--kit-sha256") + 1], self.approved_sha)
        revised = self.revised_dose_kit()
        for replacement, message in ((revised, "kit hash differs"), (v11_tests.v11_kit(), "different runner kind")):
            self.kit_path.write_text(json.dumps(replacement))
            with (self.subTest(message=message), patch.object(runner, "production_deps") as work,
                  redirect_stderr(io.StringIO()) as stderr, self.assertRaises(SystemExit) as error):
                runner.main(child[2:])
            self.assertEqual(error.exception.code, 2)
            self.assertIn(message, stderr.getvalue())
            work.assert_not_called()
            self.assertFalse(self.output.exists())

    def native_close(self):
        return {"schema": runner.RECEIPT_SCHEMA, "span_id": "previous",
                "ended": {"epoch_ns": self.close_ns}, "rc": 2,
                "steps": [{"name": "restore", "rc": 0, "result": {"ok": True, "rc": 0, "exit_code": 0, "observed": 0}},
                          *[{"name": f"stop-{feed}", "rc": 0, "result": {"proven_stopped": True}}
                            for feed in ("meter", "agents", "volumes")]],
                "feeds": {feed: {"stop": {"rc": 0, "proven_stopped": True}}
                          for feed in ("meter", "agents", "volumes")}}

    def test_workload_group_replay_refuses_failed_stop_despite_attestation(self):
        from scripts import run_align_r1_smoke, run_night

        predecessor = self.root / "previous-span"
        clock = runner.FakeClock(self.now - 8000)
        deps = runner.mock_deps(predecessor, clock)
        deps.workload_groups = []
        deps.host.restore_power = lambda _: {"rc": 0, "exit_code": 0, "observed": 0, "ok": True}
        worker = Mock(pid=12345)
        worker.poll.return_value = worker.wait.return_value = 0
        deadline = Mock()
        deadline.expired.return_value = False
        deadline.cancel.return_value = None

        def reap(process, *, evidence):
            self.assertIs(process, worker)
            evidence.update(reaped=True, group_census=["synthetic leg worker"])
            return False

        def run_leg(attempt_dir, *_args, **_kwargs):
            runner.run_child(name="L001.a1", argv=["synthetic-no-process"], cap_s=10,
                             log_dir=attempt_dir.parent, feeds=[], work_remaining=lambda: 1000,
                             workload_groups=deps.workload_groups)
            self.fail("leg continued after its group failed to stop")

        deps.run_leg = run_leg
        kit = v11_tests.v11_kit()
        plan = legs.plan_span(kit, t0_epoch=clock.time(), windows=[], leg_ids=["L001"])
        with (patch.object(runner.subprocess, "Popen", return_value=worker),
              patch.object(run_align_r1_smoke, "PartDeadline", return_value=deadline),
              patch.object(run_night, "_terminate_process_group", side_effect=reap)):
            self.assertEqual(runner.run_span(
                kit=kit, kit_sha256="a" * 64, output=predecessor, deadline=runner.launch_deadline(plan),
                windows=[], deps=deps, leg_ids=["L001"], span_id="previous"), 2)
        receipt = json.loads((predecessor / runner.RECEIPT_NAME).read_text())
        failure = next(row for row in receipt["steps"] if row["name"] == "L001.a1")
        self.assertIn("L001.a1 process group not proven stopped", failure["error"])
        self.assertEqual(receipt["workload_groups"], [{"name": "L001.a1", "pgid": 12345, "proven_stopped": False}])
        self.assertTrue(receipt["feeds"]["meter"]["stop"]["proven_stopped"])
        self.proof[-1] = ("--t0-not-before-ns", str(receipt["ended"]["epoch_ns"]))
        proof = ["close-proof", "--attempt-ledger", str(self.ledger)]
        legacy = {key: value for key, value in receipt.items() if key not in {"workload_groups", "error"}}
        with (patch.object(run_night, "_group_census", return_value=(True, [])) as census,
              patch.object(launcher.base, "pid_alive", return_value=True),
              patch.object(launcher.time, "time", return_value=self.now),
              patch.object(runner.RealClock, "arm_anchor_ns", return_value=(self.close_ns, self.ns, self.ns)),
              patch.object(launcher.subprocess, "run") as service):
            for record in (receipt, legacy):
                self.receipt.write_text(json.dumps(record))
                with self.subTest(legacy=record is legacy), redirect_stderr(io.StringIO()) as stderr:
                    self.assertEqual(launcher.main(proof), 2)
                    self.assertIn("L001.a1 process group not proven stopped", stderr.getvalue())
                    self.assertIn("L001.a1 process group not proven stopped", self.launch(self.proof))
            census.assert_not_called()
            service.assert_not_called()
        self.assertIsNone(launcher.base.read_fence(self.fence_root))
        self.assertEqual(json.loads(self.ledger.read_text())["attempts"], [self.prior])

    def test_close_requires_attestation_and_fresh_census_under_launch_lock(self):
        from scripts import run_night

        receipt = self.native_close()
        receipt["workload_groups"] = [{"name": "soak", "pgid": 12345, "proven_stopped": True},
                                      {"name": "L001.a1", "pgid": 12346, "proven_stopped": True}]
        self.receipt.write_text(json.dumps(receipt))
        proof = ["close-proof", "--attempt-ledger", str(self.ledger)]
        with (patch.object(run_night, "_group_census") as census,
              patch.object(launcher.base, "pid_alive", return_value=True),
              patch.object(launcher.time, "time", return_value=self.now),
              patch.object(runner.RealClock, "arm_anchor_ns", return_value=(self.close_ns, self.ns, self.ns)),
              patch.object(launcher.subprocess, "run") as service,
              redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO())):
            census.return_value = (True, [])
            with patch.dict(os.environ, {"GROUPS_ABSENT": "0"}):
                self.assertEqual(launcher.main(proof), 2)
                self.assertIn("receipt-bound", self.launch(self.proof))
            census.assert_not_called()
            self.assertEqual(launcher.main(proof), 0)
            self.assertEqual(census.call_args_list, [call(12345), call(12346)])
            for outcome in ((False, []), (False, ["synthetic leg worker"]), (True, ["synthetic leg worker"])):
                # The prior successful CLI census cannot authorize the locked launch.
                census.reset_mock()
                census.side_effect = [(True, []), outcome, (True, []), outcome]
                with self.subTest(outcome=outcome):
                    self.assertIn("fresh census did not prove process group 12346 empty", self.launch(self.proof))
                    self.assertEqual(launcher.main(proof), 2)
                    self.assertEqual(census.call_args_list, [call(12345), call(12346)] * 2)
            service.assert_not_called()
        self.assertIsNone(launcher.base.read_fence(self.fence_root))
        self.assertEqual(json.loads(self.ledger.read_text())["attempts"], [self.prior])

    def test_close_freshly_censuses_retired_collector_group(self):
        from scripts import run_align_r1_smoke as smoke, run_night

        pgid = 43210
        process = Mock(pid=pgid)
        process.poll.return_value = 1
        feed = smoke.MeterFeed(self.root)
        feed.supervisor = smoke.driver.MonitorSupervisor(
            ["synthetic-no-device"], night_dir=self.root, popen=Mock(return_value=process), name="synthetic")
        with patch.object(smoke.driver.time, "monotonic", return_value=1000):
            self.assertTrue(feed.supervisor.start())
            feed.poll()
        self.assertIsNone(feed.supervisor.process)
        stop = feed.stop()
        self.assertTrue(stop["proven_stopped"])
        self.assertEqual(stop["supervisor"]["exits"][0]["pid"], pgid)
        receipt = self.native_close()
        receipt["feeds"]["meter"]["stop"] = stop
        next(row for row in receipt["steps"] if row["name"] == "stop-meter")["result"] = stop
        self.receipt.write_text(json.dumps(receipt))
        proof = ["close-proof", "--attempt-ledger", str(self.ledger)]
        with (patch.object(run_night, "_group_census") as census,
              patch.object(launcher.base, "pid_alive", return_value=True),
              patch.object(launcher.time, "time", return_value=self.now),
              patch.object(runner.RealClock, "arm_anchor_ns", return_value=(self.close_ns, self.ns, self.ns)),
              patch.object(launcher.subprocess, "run") as service,
              redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO())):
            census.return_value = (True, [])
            self.assertEqual(launcher.main(proof), 0)
            census.assert_called_once_with(pgid)
            census.reset_mock()
            census.return_value = (False, ["synthetic remaining member"])
            self.assertEqual(launcher.main(proof), 2)
            self.assertIn(f"fresh census did not prove process group {pgid} empty", self.launch(self.proof))
            self.assertEqual(census.call_args_list, [call(pgid), call(pgid)])
            service.assert_not_called()
        self.assertIsNone(launcher.base.read_fence(self.fence_root))
        self.assertEqual(json.loads(self.ledger.read_text())["attempts"], [self.prior])

    def test_runner_records_final_collector_group_for_fresh_census(self):
        predecessor = self.root / "previous-span"
        clock = runner.FakeClock(self.now - 8000)
        deps = runner.mock_deps(predecessor, clock)
        meter = next(feed for feed in deps.feeds if feed.name == "meter")
        meter.supervisor = Mock(process=Mock(pid=43211))
        original_stop = meter.stop
        meter.stop = lambda: {**original_stop(), "group": {"reaped": True, "group_census": []}}
        kit = v11_tests.v11_kit()
        roster = ["L001"]
        plan = legs.plan_span(kit, t0_epoch=clock.time(), windows=[], leg_ids=roster)
        self.assertEqual(runner.run_span(
            kit=kit, kit_sha256="a" * 64, output=predecessor, deadline=runner.launch_deadline(plan),
            windows=[], deps=deps, leg_ids=roster, span_id="previous"), 0)
        receipt = json.loads((predecessor / runner.RECEIPT_NAME).read_bytes())
        stop = receipt["feeds"]["meter"]["stop"]
        self.assertEqual(stop["group"]["pgid"], 43211)
        self.assertEqual(next(row["result"] for row in receipt["steps"] if row["name"] == "stop-meter"), stop)

    def test_contradictory_restore_readback_refuses_cli_and_ctl_bootstrap(self):
        clean = self.native_close()
        argv = ["close-proof", "--attempt-ledger", str(self.ledger)]
        self.receipt.write_text(json.dumps(clean))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(launcher.main(argv), 0)
        discrepancies = ({"observed": 2}, {"observed": False}, {"observed": "0"}, {"observed": None},
                         {"exit_code": 1}, {"rc": False}, {"read": {"value": 2}},
                         {"read": {"value": 0, "error": "synthetic read failure"}})
        with (patch.object(launcher.base, "pid_alive", return_value=True),
              patch.object(launcher.time, "time", return_value=self.now),
              patch.object(runner.RealClock, "arm_anchor_ns", return_value=(self.close_ns, self.ns, self.ns)),
              patch.object(launcher.subprocess, "run") as service):
            for result, summary in (({"observed": 2}, False),
                                    *((result, True) for result in (*discrepancies, {}))):
                receipt = deepcopy(clean)
                if summary:
                    receipt["restore_readbacks"] = {"automatic": True}
                restore = receipt["steps"][0]["result"]
                if result:
                    restore.update(result)
                else:
                    del restore["observed"]
                self.receipt.write_text(json.dumps(receipt))
                with self.subTest(result=result, summary=summary), redirect_stderr(io.StringIO()):
                    self.assertEqual(launcher.main(argv), 2)
                    self.assertIn("restore", self.launch(self.proof))
            service.assert_not_called()
        self.assertIsNone(launcher.base.read_fence(self.fence_root))
        self.assertEqual(json.loads(self.ledger.read_text())["attempts"], [self.prior])

    def test_incomplete_close_refuses_cli_and_ctl_bootstrap(self):
        clean = self.native_close()
        fixtures = (
            ({"rc": 2, "result": {"proven_stopped": False}}, {"rc": 2, "proven_stopped": False}),
            ({"rc": 0, "result": {"proven_stopped": False}}, {"rc": 0, "proven_stopped": True}),
            ({"rc": 0, "result": {"proven_stopped": True}}, {"rc": 0, "proven_stopped": False}),
            ({"rc": 0, "result": {"proven_stopped": True, "group": {"reaped": True, "group_census": ["fixture"]}}},
             {"rc": 0, "proven_stopped": True}),
        )
        argv = ["close-proof", "--attempt-ledger", str(self.ledger)]
        self.receipt.write_text(json.dumps(clean))
        with redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(launcher.main(argv), 0)
        self.assertEqual(stdout.getvalue().splitlines(), ["previous", str(self.close_ns), str(self.receipt)])
        with (patch.object(launcher.base, "pid_alive", return_value=True),
              patch.object(launcher.time, "time", return_value=self.now),
              patch.object(runner.RealClock, "arm_anchor_ns", return_value=(self.close_ns, self.ns, self.ns)),
              patch.object(launcher.subprocess, "run") as service):
            for step, stop in fixtures:
                receipt = deepcopy(clean)
                receipt["steps"][1].update(step)
                receipt["feeds"]["meter"]["stop"] = stop
                self.receipt.write_text(json.dumps(receipt))
                with self.subTest(step=step, stop=stop), redirect_stderr(io.StringIO()):
                    self.assertEqual(launcher.main(argv), 2)
                    self.assertIn("stop", self.launch(self.proof))
            missing = deepcopy(clean)
            missing["steps"].pop()
            del missing["feeds"]["volumes"]
            self.receipt.write_text(json.dumps(missing))
            with redirect_stderr(io.StringIO()):
                self.assertEqual(launcher.main(argv), 2)
                self.assertIn("every feed stopped", self.launch(self.proof))
            self.receipt.write_text(json.dumps(clean))
            for key in ("HOST_RESTORE_OK", "FEEDS_STOPPED", "GROUPS_ABSENT", "FOREIGN_PROCESSES_ABSENT",
                        "CLOSE_PROOF_RECEIPT"):
                with self.subTest(missing=key), patch.dict(os.environ, {key: ""}), redirect_stderr(io.StringIO()):
                    self.assertEqual(launcher.main(argv), 2)
                    self.assertIn("receipt-bound", self.launch(self.proof))
            service.assert_not_called()
        self.assertIsNone(launcher.base.read_fence(self.fence_root))
        self.assertEqual(json.loads(self.ledger.read_text())["attempts"], [self.prior])

    def check_child_close_bound(self, argv):
        clock = runner.FakeClock(self.now)
        deps = runner.mock_deps(self.output, clock)
        with patch.object(runner, "production_deps", return_value=deps):
            for wall_ns, continuous_ns in ((self.close_ns - 1, 1000 * self.ns),
                                           (self.close_ns, 1000 * self.ns - 1)):
                with (self.subTest(wall_ns=wall_ns, continuous_ns=continuous_ns),
                      patch.object(clock, "epoch_and_monotonic_ns", return_value=(wall_ns, continuous_ns)),
                      redirect_stderr(io.StringIO()) as stderr):
                    self.assertEqual(runner.main(argv), 3)
                    self.assertIn("exact close bound", stderr.getvalue())
                self.assertFalse(self.output.exists())
                self.assertEqual(deps.host.calls, [])
            with patch.object(clock, "epoch_and_monotonic_ns", return_value=(self.close_ns, 1000 * self.ns)):
                self.assertEqual(runner.main(argv), 0)
        result = json.loads((self.output / runner.RECEIPT_NAME).read_text())
        self.assertEqual(result["started"]["epoch_ns"], self.close_ns)
        self.assertEqual(result["span_id"], self.span_id)
        self.assertEqual(result["t0_authority"], {"t0_not_before_ns": self.close_ns})

    def test_ctl_checklist_refuses_draft_without_requiring_batch_window(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        observations = root / "observations.json"
        observations.write_text(json.dumps({**v11_tests.FreeT0Checklist.GOOD,
                                             "t0_epoch_s": local("2026-11-19T00:30")}))
        with redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(cadence_queue.main(["checklist", "--kit", str(KIT), "--observations", str(observations),
                                                "--kit-sha256", "f" * 64]), 1)
        self.assertIn("DRAFT / UNFROZEN", stdout.getvalue())

    def test_scripted_child_dispatch_refuses_non_ctl_leg_spec(self):
        spec = {k: v for k, v in specs()[0].items() if k != "script"}
        spec["schema"] = legs.LEG_SPEC_SCHEMA_V11
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        path = root / "non-ctl-spec.json"
        path.write_text(json.dumps(spec))
        result = subprocess.run([sys.executable, "-B", str(runner.ROOT / runner.LEG_RUNTIME), "--scripted-ctl",
                                 "--leg-spec", str(path), "--leg-spec-sha256", ctl.leg_spec_sha256(spec)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, rt.EXIT_REFUSED)
        self.assertIn("cadence-ctl-v1 needs a ctl leg spec", result.stderr)


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        from tests.align import r1_synthetic as rs
        from tests.align.test_r1_runtime import write_soak
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.config = rs.synthetic_config(self.root/"cfg",battery={"drain_pct_per_h":0})
        self.soak = write_soak(self.root/"soak.json")

    def call(self, spec, name, source=None, backend_factory=None, expected=None):
        path = self.root/(name+".json")
        path.write_text(json.dumps(spec))
        out = self.root/"span"/"legs"/name/"runtime"
        out.parent.mkdir(parents=True)
        args = ["--config",str(self.config),"--leg-spec",str(path),
                "--leg-spec-sha256",ctl.leg_spec_sha256(expected or spec),"--r1-kind","cadence-leg",
                "--output",str(out),"--soak-reference",str(self.soak)]
        if source:
            args += ["--span-reference",str(source)]
        original = workload.MlxEndpoint
        code = cadence_ctl.main(args,backend_factory=backend_factory,stdout=io.StringIO())
        self.assertIs(workload.MlxEndpoint,original)
        result = runner.accepted_result(out) if code == 0 else None
        return code,out,result

    def test_every_script_runs_physical_doses_and_sampled_recovery(self):
        kit = ctl.apply_instrument_read(draft(), below_gpu_floor=True, below_dc_in_floor=True,
                                        return_time_s=25.25, decode_end_lag_s=2.01, prompt_sizes=[2048],
                                        raised_doses=(192, 384, 768))
        pair_contexts = {}
        for raw in specs(kit):
            spec = {**raw,"g0_role":"capture"}
            # Independent captures here; the integration test below exercises consumers.
            code,out,result = self.call(spec,spec["leg_id"])
            self.assertEqual(code,0,(out/rt.CUSTODY_NAME).read_text())
            audit = json.loads((out/cadence_ctl.AUDIT_NAME).read_text())
            script = spec["script"]
            self.assertTrue(audit["complete"])
            turns = [s for s in audit["steps"] if s["kind"] == "turn"]
            self.assertEqual([s["actual_tokens"] for s in turns],script["turn_tokens"])
            self.assertEqual(result["decode_tokens"],sum(script["turn_tokens"]))
            hidden = [s["actual_tokens"] for s in audit["steps"] if s["kind"] == "hidden"]
            self.assertEqual(hidden,[script["hidden_tokens"]] if script["hidden_tokens"] else [])
            recovery = audit["steps"][-1]
            self.assertEqual(recovery["kind"],"recovery")
            self.assertAlmostEqual((recovery["ended_ns"]-recovery["started_ns"])/rt.NS, script["recovery_s"])
            if script["kind"] in {"split", "plain"}:
                pair_contexts[script["kind"]] = [s["context_tokens"] for s in turns]
            if script["kind"] == "split":
                gaps = [s for s in audit["steps"] if s["kind"] == "gap"]
                self.assertEqual(len(gaps), 2)
                for gap in gaps:
                    self.assertAlmostEqual((gap["ended_ns"] - gap["started_ns"]) / rt.NS, script["gap_s"])
            if script["cpu_s"]:
                cpu = next(s for s in audit["steps"] if s["kind"] == "cpu")
                self.assertEqual((cpu["ended_ns"]-cpu["started_ns"])/rt.NS,script["cpu_s"])
            custody = json.loads((out/rt.CUSTODY_NAME).read_text())
            self.assertEqual(custody["files"][cadence_ctl.AUDIT_NAME],result["script_record_sha256"])
            # Stage timestamps only; no synthetic rail samples are parsed.
            events = [json.loads(l) for l in (out/result["bundle"]/"events.jsonl").read_text().splitlines()]
            stops = [r for r in events if r.get("event_type")=="sampling_stopped"]
            self.assertTrue(stops)
            self.assertGreaterEqual(stops[-1]["timestamp_s"],recovery["ended_epoch_s"])
            legs.guard_projection(result,"ctl result",values=False)
        self.assertGreater(pair_contexts["plain"][0], 0)
        self.assertEqual(pair_contexts["split"], pair_contexts["plain"] * 3)

    def test_consumer_authenticates_capture(self):
        pair = specs()[:2]
        c,source,_ = self.call(pair[0],"L001")
        self.assertEqual(c,0)
        c,out,result = self.call(pair[1],"L002",source)
        self.assertEqual(c,0,(out/rt.CUSTODY_NAME).read_text())
        self.assertEqual(result["g0_role"],"consume")
        self.assertTrue(result["g0_reference_record_sha256"])

    def test_split_and_plain_use_same_prompt_and_physical_rng_seed(self):
        from joulewise.align.apple import endpoint
        from tests.align import w1_synthetic

        roster = specs()
        capture = roster[3]
        code, source, _ = self.call(capture, capture["leg_id"])
        self.assertEqual(code, 0)
        seed_rng = w1_synthetic.FakeRandom.seed
        generate_turn = endpoint.generate_turn
        seeds, calls = [], []

        def record_seed(rng, seed):
            seeds.append(seed)
            return seed_rng(rng, seed)

        def record_call(*args, **kwargs):
            before = len(seeds)
            result = generate_turn(*args, **kwargs)
            self.assertEqual(len(seeds), before + 1)
            calls.append((result.output_tokens, seeds[-1], result.prompt_token_ids))
            return result

        pair = {}
        with (patch.object(w1_synthetic.FakeRandom, "seed", record_seed),
              patch.object(endpoint, "generate_turn", record_call)):
            for spec in roster:
                kind = spec["script"]["kind"]
                if kind in {"split", "plain"}:
                    calls.clear()
                    code, _, result = self.call(spec, spec["leg_id"], source=source)
                    self.assertEqual(code, 0)
                    self.assertTrue(legs.leg_admitted(result, contaminated=False))
                    pair[kind] = (spec["seed"], list(calls))
        plain_seed, [(plain_tokens, physical_seed, prompt)] = pair["plain"]
        split_seed, split_calls = pair["split"]
        self.assertEqual(plain_seed, split_seed)
        self.assertEqual([tokens for tokens, _, _ in split_calls], [342, 341, 341])
        self.assertEqual(sum(tokens for tokens, _, _ in split_calls), plain_tokens)
        self.assertTrue(prompt)
        self.assertEqual([(seed, ids) for _, seed, ids in split_calls], [(physical_seed, prompt)] * 3)

    @contextmanager
    def count_physical_start_reads(self):
        from joulewise.align.apple.sampler import monotonic_ns
        from tests.align.w1_synthetic import WorldClock

        native_stamp = WorldClock.stamp
        chat_code = workload.MlxEndpoint.chat.__code__
        reads = []

        def stamp(clock):
            clock._now += 1e-6
            value = native_stamp(clock)
            frame = sys._getframe(1)
            while frame is not None:
                if frame.f_code is chat_code:
                    if "start_stamp" not in frame.f_locals:
                        reads.append(monotonic_ns(value))
                    break
                if frame.f_code.co_filename == cadence_ctl.__file__ and frame.f_code.co_name == "physical_call":
                    # Any wrapper-side read here is extra. The endpoint owns both boundaries.
                    reads.append(monotonic_ns(value))
                    break
                frame = frame.f_back
            return value

        with patch.object(WorldClock, "stamp", stamp):
            yield reads

    def test_physical_call_boundaries_match_envelope_with_nonzero_clock_reads(self):
        native_chat = workload.MlxEndpoint.chat
        physical_calls = []

        def chat(endpoint, *args, **kwargs):
            result = native_chat(endpoint, *args, **kwargs)
            physical_calls.append(result)
            return result

        source = None
        count = 0
        with self.count_physical_start_reads() as reads, patch.object(workload.MlxEndpoint, "chat", chat):
            for spec in specs():
                with self.subTest(leg=spec["leg_id"]):
                    physical_calls.clear()
                    reads.clear()
                    if spec["g0_role"] == "capture":
                        source = None
                    code, out, _ = self.call(spec, spec["leg_id"], source=source)
                    self.assertEqual(code, 0)
                    if source is None:
                        source = out
                    work = json.loads((out / ctl.WORK_NAME).read_bytes())
                    calls = [row for row in work["steps"] if row["kind"] in {"hidden", "turn"}]
                    self.assertEqual(reads, [row["started_ns"] for row in calls])
                    count += len(reads)
                    self.assertEqual(
                        [(row["started_ns"], row["first_token_ns"], row["ended_ns"]) for row in calls],
                        [(r.start_ns, r.first_token_ns, r.end_ns) for r in physical_calls],
                    )
                    self.assertEqual(
                        [(row["context_tokens"], row["cached_prompt_tokens"]) for row in calls],
                        [(r.prompt_tokens, r.cached_prompt_tokens) for r in physical_calls],
                    )
                    visible = [row for row in calls if row["kind"] == "turn"]
                    result = runner.accepted_result(out, ctl_spec=spec)
                    self.assertTrue(legs.leg_admitted(result, contaminated=False))
                    self.assertEqual(result["turn_start_ns"], visible[0]["started_ns"])
                    self.assertEqual(result["first_token_ns"], visible[0]["first_token_ns"])
                    self.assertEqual(result["turn_end_ns"], visible[-1]["ended_ns"])
                    self.assertEqual(result["decode_tokens"], sum(row["actual_tokens"] for row in visible))
                    self.assertEqual(result["prefill_tokens"],
                                     sum(row["context_tokens"] - row["cached_prompt_tokens"] for row in visible))
        self.assertEqual(count, 24)

    def test_failed_physical_call_preserves_single_start_read_for_envelope(self):
        from joulewise.align.apple import endpoint

        spec = specs()[0]
        parse_completion = endpoint.parse_completion
        for failed_call in (1, 2):
            with self.subTest(failed_call=failed_call):
                completed = 0
                failure = RuntimeError("synthetic finalize failure")

                def parse(*args, **kwargs):
                    nonlocal completed
                    completed += 1
                    if completed == failed_call:
                        raise failure
                    return parse_completion(*args, **kwargs)

                with (self.count_physical_start_reads() as reads,
                      patch.object(endpoint, "parse_completion", side_effect=parse)):
                    code, out, result = self.call(spec, f"failed-visible-{failed_call}")
                self.assertEqual(code, rt.EXIT_FAILED)
                self.assertIsNone(result)
                raw = (out / ctl.WORK_NAME).read_bytes()
                work = json.loads(raw)
                calls = [row for row in work["steps"] if row["kind"] == "turn"]
                self.assertEqual(len(reads), failed_call)
                self.assertEqual([row["started_ns"] for row in calls], reads)
                self.assertEqual(failure.started_ns, reads[-1])
                self.assertFalse(calls[-1]["complete"])
                self.assertFalse(work["complete"])
                self.assertEqual(work["failed_envelope"]["start_ns"], reads[0])
                self.assertEqual(work["failed_envelope"]["end_ns"], failure.ended_ns)
                custody = json.loads((out / rt.CUSTODY_NAME).read_bytes())
                self.assertEqual(custody["status"], "failed")
                self.assertEqual(custody["files"][ctl.WORK_NAME], hashlib.sha256(raw).hexdigest())

    def test_authenticated_ctl_envelope_cannot_disagree_with_physical_work(self):
        spec = specs()[0]
        code, out, result = self.call(spec, spec["leg_id"])
        self.assertEqual(code, 0)
        custody_path = out / rt.CUSTODY_NAME
        custody = json.loads(custody_path.read_bytes())
        for field in ("turn_start_ns", "first_token_ns", "turn_end_ns", "prefill_tokens", "decode_tokens"):
            with self.subTest(field=field):
                changed = {**result, field: result[field] + 1}
                raw = json.dumps(changed).encode()
                (out / rt.RESULT_NAME).write_bytes(raw)
                custody["files"][rt.RESULT_NAME] = hashlib.sha256(raw).hexdigest()
                custody_path.write_text(json.dumps(custody))
                with self.assertRaisesRegex(runner.LegRuntimeError, f"disagrees with physical calls on {field}"):
                    runner.accepted_result(out, ctl_spec=spec)

    def test_missing_reference_fails_without_running_a_script(self):
        spec = specs()[1]
        code,out,_ = self.call(spec,"L002")
        self.assertEqual(code,rt.EXIT_REFUSED)
        self.assertFalse((out/cadence_ctl.AUDIT_NAME).exists())

    def test_short_physical_dose_is_unadmitted_and_restores_endpoint(self):
        original = workload.MlxEndpoint
        native_chat = original.chat
        from dataclasses import replace
        def short(endpoint,*args,**kwargs):
            return replace(native_chat(endpoint,*args,**kwargs),completion_tokens=1)
        with patch.object(original,"chat",short):
            code,out,result = self.call(specs()[0],"short")
        self.assertEqual(code,0,(out/rt.CUSTODY_NAME).read_text())
        self.assertEqual(result["leg_status"],"incomplete")
        self.assertFalse(result["decode_cap_reached"])
        self.assertFalse(legs.leg_admitted(result,contaminated=False))
        audit = json.loads((out/cadence_ctl.AUDIT_NAME).read_text())
        self.assertFalse(audit["complete"])
        self.assertEqual(audit["steps"][0]["actual_tokens"],1)
        self.assertEqual(json.loads((out/rt.CUSTODY_NAME).read_text())["status"],"complete")

    def test_cpu_failure_keeps_partial_ground_truth_and_refuses(self):
        spec = next(s for s in specs() if s["script"]["kind"]=="cpu")
        spec = {**spec,"g0_role":"capture"}
        with patch.object(cadence_ctl,"cpu_burn",side_effect=RuntimeError("stubbed CPU failure")):
            code,out,_ = self.call(spec,"burn-failed")
        self.assertEqual(code,rt.EXIT_FAILED)
        audit = json.loads((out/cadence_ctl.AUDIT_NAME).read_text())
        self.assertFalse(audit["complete"])
        self.assertEqual([s["kind"] for s in audit["steps"]],["turn","cpu"])
        self.assertFalse(audit["steps"][-1]["complete"])
        self.assertIn("ended_ns",audit["steps"][-1])

    def test_normal_early_cpu_return_stays_unadmitted(self):
        spec = specs()[3]
        self.assertEqual(spec["script"]["cpu_s"], 90)
        with patch.object(cadence_ctl, "cpu_burn", return_value=None):
            code, out, result = self.call(spec, spec["leg_id"])
        self.assertEqual(code, 0)
        work = json.loads((out / cadence_ctl.AUDIT_NAME).read_bytes())
        cpu = next(row for row in work["steps"] if row["kind"] == "cpu")
        self.assertEqual(cpu["ended_ns"] - cpu["started_ns"], 0)
        self.assertFalse(cpu["complete"])
        self.assertFalse(result["script_complete"])
        self.assertFalse(legs.leg_admitted(runner.accepted_result(out, ctl_spec=spec), contaminated=False))

    def test_stale_dose_spec_refused_by_child_and_by_span_evidence_check(self):
        stale = next(spec for spec in specs() if spec["leg_id"] == "L002")
        stale = {**stale, "g0_role": "capture"}
        planned = deepcopy(stale)
        planned["script"]["hidden_tokens"] = 768
        self.assertEqual(stale["script"]["hidden_tokens"], 512)
        code, out, _ = self.call(stale, "stale-refusal", expected=planned)
        self.assertEqual(code, rt.EXIT_REFUSED)
        self.assertFalse(out.exists())
        # Reproduce an internally consistent child result from the stale spec.
        code, out, result = self.call(stale, "stale-result")
        self.assertEqual(code, 0)
        self.assertTrue(result["script_complete"])
        with self.assertRaisesRegex(runner.LegRuntimeError, "does not bind the planned leg spec"):
            runner.accepted_result(out, ctl_spec=planned)

    def test_missing_scripted_flag_refuses_a_ctl_spec_without_work(self):
        spec = specs()[0]
        path = self.root / "pilot-spec.json"
        path.write_text(json.dumps(spec))
        out = self.root / "ordinary-result"
        argv = [sys.executable, "-B", str(runner.ROOT / runner.LEG_RUNTIME), "--leg-spec", str(path),
                "--config", str(self.config), "--r1-kind", "cadence-leg",
                "--output", str(out), "--soak-reference", str(self.soak)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, rt.EXIT_REFUSED)
        self.assertIn("ctl leg spec requires the scripted runtime", result.stderr)
        self.assertFalse(out.exists())

    def test_short_hidden_dose_is_unadmitted_even_with_a_complete_visible_call(self):
        original = workload.MlxEndpoint
        native_chat = original.chat
        from dataclasses import replace
        def short_hidden(endpoint,*args,**kwargs):
            result = native_chat(endpoint,*args,**kwargs)
            return replace(result,completion_tokens=1) if type(endpoint) is original else result
        spec = next(s for s in specs() if s["script"]["kind"]=="hidden")
        spec = {**spec,"g0_role":"capture"}
        with patch.object(original,"chat",short_hidden):
            code,out,result = self.call(spec,"short-hidden")
        self.assertEqual(code,0,(out/rt.CUSTODY_NAME).read_text())
        self.assertEqual(result["decode_tokens"],sum(spec["script"]["turn_tokens"]))
        self.assertFalse(result["script_complete"])
        self.assertFalse(legs.leg_admitted(result,contaminated=False))

    def test_g0_timeout_never_runs_the_script(self):
        from tests.align.test_r1_runtime import IncompleteMemberTests
        spec = specs()[0]
        code,out,result = self.call(spec,"timeout",backend_factory=IncompleteMemberTests.NoReleaseBackend)
        self.assertEqual(code,0,(out/rt.CUSTODY_NAME).read_text())
        self.assertFalse(result["g0_released"])
        self.assertFalse(result["script_complete"])
        self.assertEqual(json.loads((out/cadence_ctl.AUDIT_NAME).read_text())["steps"],[])

    def test_span_driver_runs_real_scripts_to_close_and_desk(self):
        # Full 3 + 9 release-candidate rehearsal, every script, both capture and consumer references.
        from tests.align.test_r1_runtime import write_soak
        kit = draft()
        revised = ctl.apply_instrument_read(kit, below_gpu_floor=True, below_dc_in_floor=True,
                                            raised_doses=(192, 384, 768), return_time_s=120,
                                            decode_end_lag_s=2, prompt_sizes=[2000])
        for name,ids in (("pilot",["L001","L002","L003"]),("rest",[f"L{i:03d}" for i in range(4,13)]),
                         ("short",["L001","L002","L003"]),("stale",["L001","L002","L003"])):
            planned_kit = revised if name == "stale" else kit
            out = self.root/name
            clock = runner.FakeClock(local("2026-11-17T02:40"))
            deps = runner.mock_deps(out,clock)
            deps.max_span_s = runner.max_span_s()
            def soak(path,*a):
                Path(path).mkdir(parents=True)
                return write_soak(Path(path)/"soak_reference.json")
            def run_leg(path,spec_path,soak_reference,cap_s,feeds,remaining,span_reference=None,
                        *, ctl_spec_sha256):
                stale_attempt = name == "stale" and path.parent.name == "L002"
                if stale_attempt:
                    stale = specs(kit)[1]
                    spec_path = self.root / "stale-L002.json"
                    spec_path.write_text(json.dumps(stale))
                    ctl_spec_sha256 = ctl.leg_spec_sha256(stale)
                args = ["--config",str(self.config),"--leg-spec",str(spec_path),"--r1-kind","cadence-leg",
                        "--leg-spec-sha256",ctl_spec_sha256,"--output",str(path),
                        "--soak-reference",str(soak_reference)]
                if span_reference:
                    args += ["--span-reference",str(span_reference)]
                if name == "short" and path.parent.name == "L001":
                    chat = workload.MlxEndpoint.chat

                    def short(endpoint, *args, **kwargs):
                        return replace(chat(endpoint, *args, **kwargs), completion_tokens=1)

                    with patch.object(workload.MlxEndpoint, "chat", short):
                        rc = cadence_ctl.main(args, stdout=io.StringIO())
                else:
                    rc = cadence_ctl.main(args, stdout=io.StringIO())
                if rc:
                    raise runner.LegRuntimeError("synthetic ctl runtime refused")
                if stale_attempt:
                    self.assertTrue(runner.accepted_result(path)["script_complete"])
            deps.run_soak,deps.run_leg = soak,run_leg
            p = legs.plan_span(planned_kit,t0_epoch=clock.time(),windows=NEW_WINDOW,leg_ids=ids)
            with patch.object(runner.signal,"signal",wraps=runner.signal.signal):
                rc = runner.run_span(kit=planned_kit,kit_sha256="f"*64,output=out,deadline=runner.launch_deadline(p),
                                     windows=NEW_WINDOW,deps=deps,leg_ids=ids)
            receipt = json.loads((out/runner.RECEIPT_NAME).read_text())
            if name == "stale":
                self.assertEqual(rc, 2)
                self.assertIn("does not bind the planned leg spec", receipt["error"])
                self.assertEqual(receipt["legs_finished"], 1)
                self.assertFalse((out / "legs/L002/leg_summary.json").exists())
                continue
            self.assertEqual(rc,0,receipt.get("error"))
            summary,stops = desk.build_desk(plan_id=name,input_dir=out/runner.DESK_BUNDLE,out_dir=out/"desk",
                                             adapter=kit["desk"]["adapter"],stop_rules=kit["stop_rules"],now=clock.time())
            self.assertEqual(stops,[])
            self.assertEqual([s["leg_id"] for s in summary["legs"]],ids)
            self.assertEqual([s["admitted"] for s in summary["legs"]],
                             [False,True,True] if name=="short" else [True]*len(ids))
            if name=="short":
                self.assertTrue(summary["legs"][1]["span_reference"]["excluded"])
            self.assertNotIn("script",json.dumps(summary))


if __name__ == "__main__":
    unittest.main()
