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

from joulewise import receipt_readers as readiness; from joulewise import physical_checks as author; from joulewise import night_gate
from joulewise.hazards.dwell import final_clean_dwell
from joulewise import prewindow
from joulewise import rehearsal_readers as t0; from joulewise import qualification_readers as q
from types import SimpleNamespace; from joulewise.hazards import dwell as capture; from scripts import run_night; from tests import qualification_plan_factory as writer
pass
from tests.test_arm_readiness_schemas import arm_context

ROOT = Path(__file__).resolve().parents[1]
CLEAN = "continuous clean dwell 0/600s (check 1)\ncontinuous clean dwell 600/600s (check 2)\nREADY after 11 min.\n"


class DwellTests(unittest.TestCase):
    pass
    def test_preserved_six_mac_dwells_admit_five_and_refuse_timeout(self):
        transcripts = ROOT / "tests/fixtures/v5_qualification/dwell"
        admitted = 0
        for path in sorted(transcripts.glob("*.txt")):
            text = path.read_text()
            expected = path.stem != "0526Z"
            self.assertEqual(final_clean_dwell(text), expected, path.name)
            if expected:
                admitted += 1
        self.assertEqual(admitted, 5)

    def test_recovered_dwell_and_both_consumers_share_the_final_run(self):
        text = "\033[31mBLOCK\033[0m daemon busy\nnot ready; re-checking in 30s\n" + CLEAN
        self.assertTrue(final_clean_dwell(text))
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


class CensusTests(unittest.TestCase):
    pass



class RootsTests(unittest.TestCase):
    pass


@unittest.skipUnless(Path("/bin/zsh").is_file() and Path("/usr/bin/jq").is_file(),
                     "requires the reviewed zsh and jq shell tools")
class RenderedChainTests(unittest.TestCase):
    pass
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





class RunnerTests(unittest.TestCase):
    pass
    def capture_fixture(self):
        from tests.test_v5_qualification_plan import PlanWriterTests
        fixture = PlanWriterTests()
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        fixture.write()
        (fixture.custody / "night").mkdir()
        plan = night_gate.NightPlan.from_mapping(writer.read_object(fixture.output))
        return fixture, plan






class G10CustodyTests(unittest.TestCase):
    pass
