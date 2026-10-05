"""Desk regression lenses for pre-mortem X1; none discharge a hardware gate."""
import copy
from dataclasses import replace
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest import mock

from tests.git_fixture import init_git_fixture

from joulewise import arm_readiness as readiness, arm_readiness_evidence_t0 as author, night_gate
from joulewise.dwell import final_clean_dwell
from joulewise import prewindow
from joulewise import t0_rehearsal as t0, v5_qualification as q
from scripts import capture_t0_step as capture, run_night, write_v5_qualification_plan as writer
from scripts.ed_session import capture_t0_anchor_positive_control as g10
from tests.test_arm_readiness_schemas import arm_context

ROOT = Path(__file__).resolve().parents[1]
CLEAN = "continuous clean dwell 0/600s (check 1)\ncontinuous clean dwell 600/600s (check 2)\nREADY after 11 min.\n"


class DwellTests(unittest.TestCase):
    def test_preserved_six_mac_dwells_admit_five_and_refuse_timeout(self):
        transcripts = ROOT / "tests/fixtures/v5_qualification/dwell"
        admitted = 0
        for path in sorted(transcripts.glob("*.txt")):
            text = path.read_text()
            expected = path.stem != "0526Z"
            self.assertEqual(final_clean_dwell(text), expected, path.name)
            if expected:
                capture._validate_result(None, "prewindow-check", text, "")
                admitted += 1
            else:
                with self.assertRaises(capture.CaptureT0Error):
                    capture._validate_result(None, "prewindow-check", text, "")
        self.assertEqual(admitted, 5)

    def test_recovered_dwell_and_both_consumers_share_the_final_run(self):
        text = "\033[31mBLOCK\033[0m daemon busy\nnot ready; re-checking in 30s\n" + CLEAN
        self.assertTrue(final_clean_dwell(text))
        capture._validate_result(None, "prewindow-check", text, "")
        context = SimpleNamespace(repository=ROOT)
        command = ["fixture"]
        module_raw = (ROOT / "joulewise/prewindow.py").read_bytes()
        module_identity = {"path": "joulewise/prewindow.py",
                           "sha256": readiness.sha256_bytes(module_raw)}
        with mock.patch.object(author, "_capture", return_value=(
                {"argv": command, "exit_code": 0, "stderr": "", "stdout": text,
                 "started_monotonic_ns": 0, "finished_monotonic_ns": 660_000_000_000}, {})), \
             mock.patch.object(author, "_launch_manifest", return_value=({"prewindow_command": command}, (), {})), \
             mock.patch.object(author, "_committed_artifact", return_value=(module_identity, module_raw)) as artifact:
            _capture, _identity, artifacts = author._prewindow_capture(context, kind="MAINTENANCE_CENSUS")
            artifact.assert_called_once_with(ROOT, "joulewise/prewindow.py", kind="MAINTENANCE_CENSUS")
            self.assertIn({**module_identity, "path": str(ROOT / module_identity["path"])}, artifacts)
        for bad in ("READY after 10 min.\n", CLEAN + "trailing\n", CLEAN.replace("600/600", "599/600"),
                    CLEAN + "TIMED OUT\n", CLEAN.replace("600/600", "BLOCK\n600/600"),
                    CLEAN.replace("check 2", "check 3")):
            self.assertFalse(final_clean_dwell(bad), bad)
            with self.assertRaises(capture.CaptureT0Error):
                capture._validate_result(None, "prewindow-check", bad, "")


class CensusTests(unittest.TestCase):
    def test_cpu_probe_timeout_stays_inside_the_existing_post_r1_budget(self):
        process = mock.Mock(returncode=0)
        def launched(argv, **kwargs):
            self.assertEqual(argv, list(prewindow.PS_ARGV))
            kwargs["stdout"].write(b"1 0.0 launchd\n")
            return process
        with mock.patch.object(run_night.t0_rehearsal, "observed_popen", side_effect=launched):
            probe = author._execute_probe(prewindow.PS_ARGV, cwd=ROOT)
        self.assertEqual(probe.exit_code, 0)
        self.assertEqual(process.wait.call_args_list, [mock.call(timeout=5), mock.call()])

    def test_cpu_probe_resident_zero_exact_limit_and_second_sample_busy(self):
        context = SimpleNamespace()
        def sample(cpu):
            return author._ProbeResult(prewindow.PS_ARGV, str(ROOT), 0, f"123 {cpu} /usr/libexec/backupd\n", "")
        pgrep = author._ProbeResult(("/usr/bin/pgrep",), str(ROOT), 0, "123 backupd\n", "")
        for second, admitted in ((5.0, True), (5.01, False)):
            with mock.patch.object(author, "_fresh_probe", side_effect=[pgrep, sample(0), sample(second)]), \
                 mock.patch.object(author._time, "sleep") as sleep:
                if admitted:
                    probes = author._maintenance_probe(context, kind="MAINTENANCE_CENSUS")
                    self.assertEqual(len(probes), 3)
                else:
                    with self.assertRaises(author.T0EvidenceAuthoringError):
                        author._maintenance_probe(context, kind="MAINTENANCE_CENSUS")
                sleep.assert_called_once_with(1)
        for failure in (author._ProbeResult(prewindow.PS_ARGV, str(ROOT), 1, "", ""),
                        author._ProbeResult(prewindow.PS_ARGV, str(ROOT), 0, "123 nan backupd", "")):
            with mock.patch.object(author, "_fresh_probe", side_effect=[pgrep, failure]):
                with self.assertRaises(author.T0EvidenceAuthoringError):
                    author._maintenance_probe(context, kind="MAINTENANCE_CENSUS")


class RootsTests(unittest.TestCase):
    def test_no_mock_root_admission_and_context_pin(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            custody = root / "plan"
            custody.mkdir()
            context = arm_context(root)
            for key in ("custody_root", "claim_runs_root", "bound_runs_root", "quarantine_root",
                        "claim_backup_destination", "bound_backup_destination"):
                Path(context[key]).mkdir(exist_ok=True)
            Path(context["waiver_path"]).write_bytes(b"[]\n")
            inputs = custody / "pack/arm_readiness.t0.inputs"
            inputs.mkdir(parents=True)
            path = inputs / "arm-context.json"
            path.write_bytes(readiness.render_json(context))
            chain = root / "chain.zsh"
            chain.write_text("export V5_QUALIFICATION_OCCURRENCE=s1\nexport NIGHT_ARM_CONTEXT_SHA256="
                             + readiness.sha256_bytes(path.read_bytes()) + "\n")
            plan = SimpleNamespace(custody_root=str(custody), chain_path=str(chain), pack_night={"pack_id": "pack"})
            self.assertEqual(night_gate.authenticate_arm_context(plan, context), context)
            refusals, _ = readiness._root_policy_refusals(context, [])
            self.assertFalse(refusals, refusals)
            tree = {"roots": {"claim_root_leaf": Path(context["claim_runs_root"]).name,
                              "bound_root_leaf": Path(context["bound_runs_root"]).name}}
            ctx = SimpleNamespace(tree=tree, values={"arm_context": (context, {})})
            author._root_observation(ctx, kind="ROOTS")
            for value in (str(custody), str(custody / "nested"), str(root), "relative"):
                changed = {**context, "custody_root": value}
                path.write_bytes(readiness.render_json(changed))
                chain.write_text("export V5_QUALIFICATION_OCCURRENCE=s1\nexport NIGHT_ARM_CONTEXT_SHA256="
                                 + readiness.sha256_bytes(path.read_bytes()) + "\n")
                with self.assertRaises(ValueError):
                    night_gate.authenticate_arm_context(plan, changed)
                with self.assertRaises(ValueError):
                    night_gate.authenticate_arm_context(plan, changed, legacy_rehearsal=True)
            path.write_bytes(readiness.render_json(context))
            with self.assertRaisesRegex(ValueError, "sha256 mismatch"):
                night_gate.authenticate_arm_context(plan, context)
            path.unlink()
            with self.assertRaisesRegex(ValueError, "arm_context"):
                night_gate.authenticate_arm_context(plan, context, legacy_rehearsal=True)
            chain.write_text("#!/bin/zsh\n")
            self.assertEqual(night_gate.authenticate_arm_context(plan, context, legacy_rehearsal=True), context)


@unittest.skipUnless(Path("/bin/zsh").is_file() and Path("/usr/bin/jq").is_file(),
                     "requires the reviewed zsh and jq shell tools")
class RenderedChainTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.repo = self.root / "measurement"
        self.pack = self.repo / "configs/campaigns" / writer.GAMMA
        shutil.copytree(ROOT / "configs/campaigns" / writer.GAMMA, self.pack)
        runbook = self.repo / "docs/phase_2/window_runbook.md"
        runbook.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / "docs/phase_2/window_runbook.md", runbook)
        init_git_fixture(self.repo, "-q")
        self.window = self.root / "plan/window-plan"
        self.window.mkdir(parents=True)
        self.context = arm_context(self.root)
        self.template = self.root / "template.zsh"
        self.template.write_text(writer.g2b_body(self.repo))
        self.sizing = json.loads((ROOT / "configs/campaigns/v5_qualification_25g83/sizing_allowances.json").read_bytes())
        self.chain = self.window / "window-chain.zsh"
        writer.render_qualification_chain("s1", self.template, self.sizing, self.pack,
                                         time.time(), self.chain, arm_context=self.context)
        # All real shell control flow is preserved. These executable tool
        # stand-ins produce structure only; they never import measurement code.
        python = self.repo / ".venv/bin/python"
        python.parent.mkdir(parents=True)
        python.write_text("#!" + sys.executable + "\n" + r'''
import json, os, pathlib, sys
args = sys.argv[1:]
name = pathlib.Path(args[0]).name
with open(os.environ["CALL_LOG"], "a") as f:
    f.write(json.dumps(args) + "\n")
def value(flag): return args[args.index(flag) + 1]
if name == "validate_powermetrics_fiducial.py":
    target = pathlib.Path(value("--output-root")) / value("--attempt-id")
    target.mkdir(parents=True, exist_ok=True)
    (target / "instrument_evidence.json").write_text('{"b_fiducial_s":0.001}')
elif name == "recover_calibration_ledger.py":
    if "--ledger" not in args or "--head-pin" not in args:
        sys.exit(2)
    base = pathlib.Path(os.environ["RUNS_ROOT"]) / "instrument_validation"
    print(json.dumps({"slots": {"pre":{"custody_locator":str(base / "pre")},
                                "post":{"custody_locator":str(base / "post")}},
                      "session_state":"finalized", "pin_relation":"physical_ahead",
                      "refusal_code":"calibration_ledger_head_mismatch",
                      "terminal_head_pin_candidate":{"fixture":True}}))
elif name == "run_campaign.py" and "--max-blocks" in args:
    sys.exit(3)
elif name not in {"launch_window.py", "run_campaign.py"}:
    sys.exit(2)
''')
        python.chmod(0o755)
        self.call_log = self.root / "calls.jsonl"
        self.values = {name: str(self.root / name.lower()) for name in author.WINDOW_ENV_KEYS}
        self.values.update(PACK_ROOT=str(self.pack), SETTLE_S="0", PRE_ATTEMPT_ID="pre", POST_ATTEMPT_ID="post",
                           WINDOW_CUSTODY_ROOT=str(self.root / "arm"), RUNS_ROOT=str(self.root / "runs"),
                           CALIBRATION_LEDGER=str(self.root / "selected-ledger.jsonl"),
                           LEDGER_HEAD_PIN=str(self.repo / "selected-pin.json"))
        (self.window / "window.env").write_text("".join(f"export {name}={shlex.quote(value)}\n"
                                                       for name, value in self.values.items()))
        plan = SimpleNamespace(plan_id="fixture", measurement_root=str(self.repo), measurement_head="0"*40,
                               receipt_class="TRANSACTION_PACK", pack_night={"pack_id": self.pack.name})
        with mock.patch.dict(os.environ, {"PATH":"/usr/bin:/bin:/usr/sbin:/sbin"}, clear=True):
            self.env = run_night._chain_environment(plan, self.root / "plan/night")
        self.env.update(ARM_RECEIPT=str(self.root / "arm.json"), LAUNCH_MANIFEST=str(self.root / "manifest.json"),
                        CALL_LOG=str(self.call_log))

    def run_chain(self):
        return subprocess.run(["/bin/zsh", str(self.chain), str(self.window)], env=self.env,
                              stdin=subprocess.DEVNULL, capture_output=True, text=True)

    def test_real_rendered_body_reaches_exact_terminal_stop_with_fresh_transcript_root(self):
        result = self.run_chain()
        self.assertEqual(result.returncode, 0, result.stderr)
        stops = list((self.root / "plan").rglob("post-bracket-terminal-boundary.json"))
        self.assertEqual(len(stops), 1)
        calls = [json.loads(line) for line in self.call_log.read_text().splitlines()]
        science = [args for args in calls if "--max-blocks" in args]
        self.assertEqual(len(science), 1)
        self.assertEqual(science[0][1], str(self.repo / (self.window / "before_midpoint_stages.txt").read_text().strip()))
        self.assertEqual(sum("g2_boundary_stopped=physical_ahead" in p.read_text()
                             for p in (self.root / "arm").rglob("window-chain.log")), 1)
        self.assertIn('REPO="' + str(self.repo) + '"', self.chain.read_text())

    def test_stage_mutation_or_absence_refuses_before_any_tool(self):
        stage = self.window / "before_midpoint_stages.txt"
        original = stage.read_bytes()
        for modified in (b"foreign/path\n", None):
            if modified is None:
                stage.unlink()
            else:
                stage.write_bytes(modified)
            result = self.run_chain()
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(self.call_log.exists())
        stage.write_bytes(original)
        self.assertEqual(self.run_chain().returncode, 0)

    def test_transcript_override_refused_at_render(self):
        self.template.write_text(self.template.read_text() + '\nexport TRANSCRIPT_ROOT="/foreign"\n')
        with self.assertRaisesRegex(ValueError, "transcript_root_override"):
            writer.render_qualification_chain("s1", self.template, self.sizing, self.pack, time.time(),
                                              self.window / "other.zsh", arm_context=self.context)


class RunnerTests(unittest.TestCase):
    def test_driver_stages_native_sequence_unattended_before_arm_and_refuses_partial_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            custody = root / "plan"
            (custody / "night").mkdir(parents=True)
            inputs = custody / "pack" / capture.INPUT_DIRECTORY
            inputs.mkdir(parents=True)
            context = arm_context(root)
            (inputs / "arm-context.json").write_bytes(readiness.render_json(context))
            window = custody / "window-plan"
            window.mkdir()
            chain = window / "window-chain.zsh"
            chain.write_text("export V5_QUALIFICATION_OCCURRENCE=s1\n"
                             "export NIGHT_ARM_CONTEXT_SHA256="
                             + readiness.sha256_bytes(readiness.render_json(context)) + "\n")
            plan = SimpleNamespace(custody_root=str(custody), chain_path=str(chain),
                measurement_root=str(root / "measurement"), measurement_head="0" * 40,
                plan_id="s1", receipt_class="TRANSACTION_PACK",
                pack_night={"pack_id": "pack", "pack_root": str(root / "measurement/pack")})
            def completed(argv, **kwargs):
                self.assertEqual(argv, [str(root / "measurement/.venv/bin/python"),
                    str(root / "measurement/scripts/capture_t0_step.py"), "sequence",
                    "--pack-root", plan.pack_night["pack_root"], "--custody-root", str(custody),
                    "--window-plan-root", str(window)])
                self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
                self.assertEqual(kwargs["cwd"], plan.measurement_root)
                self.assertEqual(kwargs["env"]["NIGHT_DIR"], str(custody / "night"))
                for name in capture.STEP_FILENAMES.values():
                    (inputs / name).write_bytes(b"{}\n")
                return SimpleNamespace(returncode=0, stdout=b"sequence complete\n", stderr=b"")
            with mock.patch.object(run_night.t0_rehearsal, "observed_run", side_effect=completed) as execute:
                run_night._capture_qualification_t0(plan)
                run_night._capture_qualification_t0(plan)
                execute.assert_called_once()
                self.assertEqual((custody / "night/t0-capture.stdout.json").read_bytes(),
                                 b"sequence complete\n")
                (inputs / capture.STEP_FILENAMES["clock-reference"]).unlink()
                with self.assertRaisesRegex(ValueError, "incomplete prior T-0"):
                    run_night._capture_qualification_t0(plan)
                execute.assert_called_once()

    def test_capture_timeout_preserves_partial_output_and_refuses_cleanly(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "night").mkdir()
            plan = SimpleNamespace(custody_root=str(root), chain_path=str(root / "chain"),
                measurement_root="/measurement", pack_night={"pack_id": "pack", "pack_root": "/pack"})
            error = subprocess.TimeoutExpired(["capture"], 3600, output=b"partial\n", stderr=b"deadline\n")
            with mock.patch.object(night_gate, "authenticate_arm_context"), \
                 mock.patch.object(run_night, "_chain_environment", return_value={}), \
                 mock.patch.object(run_night.t0_rehearsal, "observed_run", side_effect=error):
                with self.assertRaisesRegex(ValueError, "T-0 capture stage timed out"):
                    run_night._capture_qualification_t0(plan)
            self.assertEqual((root / "night/t0-capture.stdout.json").read_bytes(), b"partial\n")
            self.assertEqual((root / "night/t0-capture.stderr.txt").read_bytes(), b"deadline\n")

    def test_sequence_cli_runs_all_six_in_order_and_stops_on_error(self):
        args = ["sequence", "--pack-root", "/pack", "--custody-root", "/custody", "--window-plan-root", "/window"]
        import io
        with mock.patch.object(capture, "capture_step", side_effect=lambda step, *a: {"status":"PASS", "step_id":step}) as step, \
             mock.patch.object(capture.sys, "stdout", SimpleNamespace(buffer=io.BytesIO())):
            self.assertEqual(capture.main(args), 0)
            self.assertEqual([call.args[0] for call in step.call_args_list], list(capture.STEP_ORDER))
        with mock.patch.object(capture, "capture_step", side_effect=capture.CaptureT0Error("evidence_author_t0_capture_result_invalid", "failed")) as step, \
             mock.patch.object(capture.sys, "stdout", SimpleNamespace(buffer=io.BytesIO())):
            self.assertEqual(capture.main(args), 2)
            self.assertEqual(step.call_count, 1)

    def test_closed_stdin_g10_is_a_clean_refusal(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/ed_session/capture_t0_anchor_positive_control.py"),
                                 "run", "--pack-root", "/absent", "--author-inputs", "/absent",
                                 "--custody-root", "/absent"], stdin=subprocess.DEVNULL,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(json.loads(result.stdout),
                         {"status": "NOT-DISCHARGED", "reason": "outside_confirmation_missing"})


class G10CustodyTests(unittest.TestCase):
    def test_real_custody_replay_requires_a2_expiry_then_g10_then_s1_and_intact_support(self):
        from tests.test_t0_anchor_positive_control import PositiveControlTests
        from tests.test_t0_rehearsal import FixtureBuilder, fixture_bundle
        control = PositiveControlTests()
        control.setUp()
        self.addCleanup(control.doCleanups)
        self.assertEqual(control.run_control()["status"], "DISCHARGED")
        head = subprocess.check_output(["git", "-C", str(control.repository),
                                        "rev-parse", "HEAD"], text=True).strip()
        builder = FixtureBuilder(Path(control.temporary.name).resolve() / "qualification")
        root = builder.build()
        plan = root / "qualification-plan.json"
        q.write(plan, {"measurement_root": str(control.repository),
                       "pack_night": {"pack_id": builder.namespace.name}})
        boot = control.stamp()["boot_id"]
        base = control.base_ns
        refs = {}
        controls = {}
        for label, checked in (("a1", base - 4 * 10**9), ("a2", base - 2 * 10**9)):
            observation = root / (label + "-observation.json")
            q.write(observation, {"first_t0_boundary_monotonic_ns": checked - 10**9})
            path = root / (label + "-control.json")
            value = {"observation": q.reference(observation),
                     "checked_monotonic_ns": checked, "boot_session_id": boot}
            q.write(path, value)
            controls[label] = (path, value)
            refs[label + "_control"] = q.reference(path)
        refs.update(g10_control=q.reference(control.control / "positive-control.json"),
                    g10_artifacts=[q.reference(control.control / "custody-manifest.json")])
        record = root / "qualification-plan-record.json"
        def save_record():
            record.write_bytes(readiness.render_json({"head": head,
                "plan": q.reference(plan), "prerequisites": refs}))
        save_record()
        boundary = base + 2 * 10**9
        for index, name in enumerate(author._CAPTURE_FILES.values()):
            (builder.inputs / name).write_bytes(readiness.render_json({
                "started_monotonic_ns": boundary + index * 1000, "boot_session_id": boot}))
        shutil.copytree(control.control, root / "records/g10-custody" / control.control.name)
        shutil.copyfile(control.control / "positive-control.json", root / "records/positive-control.json")
        self.assertEqual(q.g10_sources(root), {"g10-custody": control.control})
        bundle = fixture_bundle(root)
        bundle = replace(bundle, manifest=replace(bundle.manifest,
            value={"schema_version": "joulewise.v5_s1_qualification_bundle.v1"}))
        self.assertEqual(t0.evaluate_g10(bundle).status, t0.GateStatus.PASS)
        positive = g10.read_json(control.control / "positive-control.json")

        # The old upper bound was a1's T-0. The replacement is a strict
        # a2-expiry lower bound and the earliest s1 capture upper bound.
        path, original = controls["a2"]
        for checked in (base, base + 1):
            with self.subTest(a2_expiry=checked):
                path.write_bytes(readiness.render_json({**original, "checked_monotonic_ns": checked}))
                refs["a2_control"] = q.reference(path)
                save_record()
                result = t0.evaluate_g10(bundle)
                self.assertEqual(result.status, t0.GateStatus.FAIL)
                self.assertIn("g10_boot_or_order", result.message)
        path.write_bytes(readiness.render_json(original))
        refs["a2_control"] = q.reference(path)
        save_record()
        first_capture = builder.inputs / "clock-reference.json"
        raw = first_capture.read_bytes()
        for at in (base, base - 1):
            with self.subTest(s1_boundary=at):
                first_capture.write_bytes(readiness.render_json({
                    "started_monotonic_ns": at, "boot_session_id": boot}))
                with self.assertRaisesRegex(ValueError, "g10_boot_or_order"):
                    q.replay_g10_custody(root, positive)
        first_capture.write_bytes(raw)
        self.assertEqual(t0.evaluate_g10(bundle).status, t0.GateStatus.PASS)
        support = control.control / "before.json"
        support.write_bytes(support.read_bytes() + b" ")
        result = t0.evaluate_g10(bundle)
        self.assertEqual(result.status, t0.GateStatus.FAIL)
        self.assertIn("g10_custody_hash_or_census", result.message)
