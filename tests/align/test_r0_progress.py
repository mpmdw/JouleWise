"""Deadline and exception receipts must retain completed and in-flight work."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align import r0
from joulewise.align.r0_runner import DeadlineExpired, execute
from tests.align.test_r0_checks import FakeBackend, FakeGuard, config_at


class ProgressTest(unittest.TestCase):
    def setUp(self):
        gate = patch("joulewise.align.r0_runner.host_identity", return_value={"status": "pass", "fake": True})
        gate.start()
        self.addCleanup(gate.stop)
    def test_second_attempt_timeout_keeps_first_and_incremental_samples(self):
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            class Backend(FakeBackend):
                def long_decode(self, *, eval_metadata):
                    calls.append(eval_metadata)
                    if not eval_metadata:
                        return {**super().long_decode(eval_metadata=False), "errors": ["Resource limit"]}
                    self.probe_progress({"positions": 2049, "memory_samples": [{"position": 2049, "active_bytes": 42}]})
                    on_disk = json.loads((root / "report.json").read_text())
                    self.saved_attempts = on_disk["checks"][-1]["attempts"]
                    raise DeadlineExpired("second attempt")
            with patch("joulewise.align.r0_runner.deadline", wraps=__import__(
                    "joulewise.align.r0_runner", fromlist=["deadline"]).deadline) as timer:
                result = execute(config_at(root), root, ["long-decode"], ["D"],
                                 guard=FakeGuard(), backend_factory=Backend)
            row = result["checks"][-1]
            self.assertEqual(calls, [False, True])
            self.assertEqual(row["attempts"][0]["errors"], ["Resource limit"])
            self.assertEqual(row["attempts"][1]["memory_samples"][0]["active_bytes"], 42)
            self.assertIn("DeadlineExpired", row["error"])
            self.assertGreaterEqual(timer.call_count, 3)  # load + one per attempt

    def test_generated_error_keeps_prior_transition_and_current_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            class Backend(FakeBackend):
                def chat(self, *args, **kwargs):
                    result = super().chat(*args, **kwargs)
                    if len(args[0]) > 1:
                        from dataclasses import replace
                        from joulewise.align.interfaces import ToolCallRequest
                        result = replace(result, tool_calls=(ToolCallRequest("bad", "bad", "{}"),))
                    return result
            result = execute(config_at(root), root, ["generated"], ["D"],
                             guard=FakeGuard(), backend_factory=Backend)
            row = next(r for r in result["checks"] if r["check"] == "generated")
            self.assertEqual(row["status"], "fail")
            self.assertEqual(len(row["transitions"]), 1)
            self.assertEqual(len(row["turns"]), 2)

    def test_rung_exception_keeps_completed_rung_and_episode(self):
        ep = {"turns": [{"hit_cap": True, "closed_reasoning": False, "reasoning_tokens": 3000}]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.object(r0, "screen_episode", side_effect=[ep, ep, ep, ValueError("rung 2")]):
                result = execute(config_at(root), root, ["ladder"], ["D"],
                                 guard=FakeGuard(), backend_factory=FakeBackend)
            row = next(r for r in result["checks"] if r["check"] == "ladder")
            self.assertEqual(len(row["rungs"]), 2)
            self.assertEqual(len(row["rungs"][0]["episodes"]), 2)
            self.assertEqual(len(row["rungs"][1]["episodes"]), 2)
            self.assertEqual(row["rungs"][1]["episodes"][0]["status"], "complete")
            self.assertEqual(row["rungs"][1]["episodes"][1]["status"], "interrupted")


if __name__ == "__main__":
    unittest.main()
