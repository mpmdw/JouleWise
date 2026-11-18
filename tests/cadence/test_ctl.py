"""SYNTHETIC ONLY. Real launch-to-close orchestration; no hardware or process signalling."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from joulewise.cadence import ctl, kit as kits, legs, desk
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
            if s["cpu_s"] == 90:
                s["cpu_s"] = 120
        altered["legs"] = ctl.generate_legs(altered["campaign_id"], altered["seed_law"], altered["leg_defaults"])
        ctl.validate_kit(altered)  # no runner hardcoding of a dose that lm-inst-01 may change

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

    def test_issued_ctl_refuses_before_clock_anchor_fence_and_bootstrap(self):
        # An issued-shaped fixture exercises the unresolved authority independently of the draft gate.
        kit = draft()
        kit.update(status="issued", frozen={"commit": "a" * 40, "paths": {kit["runner"]["entry"]: "b" * 64}})
        kit["ruling"]["authorizes_spans"] = True
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        path = root / "synthetic-issued.json"
        path.write_text(json.dumps(kit))
        argv = ["launch", "--repo", str(root), "--kit", str(path), "--output", str(root / "out"),
                "--python-bin", sys.executable, "--disk-path", str(root), "--custody-root", str(root / "fence"),
                "--magistrate-pid", "234", "--deadline", "2000"]
        self.assertEqual(kits.load_kit(path)[0]["status"], "issued")
        authority = ["--attempt-ledger", str(root / "ledger.json"), "--previous-close-receipt",
                     str(root / "close.json"), "--span-id", "ctl-01-s01", "--authorized-t0-date", "2026-11-19",
                     "--t0-not-before", "1000", "--t0-before", "2000", "--t0-not-before-ns", "1000000000000"]
        with (patch.object(runner.RealClock, "arm_anchor_ns", side_effect=AssertionError("clock anchor")),
              patch.object(launcher.base, "pid_alive", side_effect=AssertionError("host probe")),
              patch.object(launcher.subprocess, "run", side_effect=AssertionError("host command"))):
            for extra in ([], authority):
                with self.subTest(extra=extra), redirect_stderr(io.StringIO()) as stderr:
                    self.assertEqual(launcher.main(argv + extra), 2)
                    self.assertIn("NEEDS_SPEC: ctl launch authority", stderr.getvalue())
        self.assertFalse((root / "fence").exists())
        with self.assertRaisesRegex(runner.SpanRefusal, "NEEDS_SPEC"):
            runner.verify_frozen_production(kit)

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
                                 "--leg-spec", str(path)], capture_output=True, text=True, timeout=30)
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

    def call(self, spec, name, source=None, backend_factory=None):
        path = self.root/(name+".json")
        path.write_text(json.dumps(spec))
        out = self.root/"span"/"legs"/name/"runtime"
        out.parent.mkdir(parents=True)
        args = ["--config",str(self.config),"--leg-spec",str(path),"--r1-kind","cadence-leg",
                "--output",str(out),"--soak-reference",str(self.soak)]
        if source:
            args += ["--span-reference",str(source)]
        original = workload.MlxEndpoint
        code = cadence_ctl.main(args,backend_factory=backend_factory,stdout=io.StringIO())
        self.assertIs(workload.MlxEndpoint,original)
        result = runner.accepted_result(out) if code == 0 else None
        return code,out,result

    def test_every_script_runs_physical_doses_and_sampled_recovery(self):
        kit = draft()
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
            self.assertAlmostEqual((recovery["ended_ns"]-recovery["started_ns"])/rt.NS,600)
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

    def test_consumer_authenticates_capture(self):
        pair = specs()[:2]
        c,source,_ = self.call(pair[0],"L001")
        self.assertEqual(c,0)
        c,out,result = self.call(pair[1],"L002",source)
        self.assertEqual(c,0,(out/rt.CUSTODY_NAME).read_text())
        self.assertEqual(result["g0_role"],"consume")
        self.assertTrue(result["g0_reference_record_sha256"])

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
        for name,ids in (("pilot",["L001","L002","L003"]),("rest",[f"L{i:03d}" for i in range(4,13)]),
                         ("short",["L001","L002","L003"])):
            out = self.root/name
            clock = runner.FakeClock(local("2026-11-17T02:40"))
            deps = runner.mock_deps(out,clock)
            deps.max_span_s = runner.max_span_s()
            def soak(path,*a):
                Path(path).mkdir(parents=True)
                return write_soak(Path(path)/"soak_reference.json")
            def run_leg(path,spec_path,soak_reference,cap_s,feeds,remaining,span_reference=None):
                args = ["--config",str(self.config),"--leg-spec",str(spec_path),"--r1-kind","cadence-leg",
                        "--output",str(path),"--soak-reference",str(soak_reference)]
                if span_reference:
                    args += ["--span-reference",str(span_reference)]
                if cadence_ctl.main(args,stdout=io.StringIO()):
                    raise runner.LegRuntimeError("synthetic ctl runtime refused")
                result = runner.accepted_result(path)
                if name=="short" and result["leg_id"]=="L001":
                    # A scripted dose cut, like the real short-dose test above, is operationally
                    # incomplete. It must not abort the span; consumers retain the exclusion mark.
                    result.update(leg_status="incomplete",decode_cap_reached=False,script_complete=False)
                return result
            deps.run_soak,deps.run_leg = soak,run_leg
            p = legs.plan_span(kit,t0_epoch=clock.time(),windows=NEW_WINDOW,leg_ids=ids)
            with patch.object(runner.signal,"signal",wraps=runner.signal.signal):
                rc = runner.run_span(kit=kit,kit_sha256="f"*64,output=out,deadline=runner.launch_deadline(p),
                                     windows=NEW_WINDOW,deps=deps,leg_ids=ids)
            receipt = json.loads((out/runner.RECEIPT_NAME).read_text())
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
