"""Synthetic-only tests: never run launchctl, swiftc, sips, or GUI operations."""

import base64
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("jw_computer_use_server", ROOT / "tools/computer_use_mcp/server.py")
cu = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cu)

SAMPLES = {
    "screenshot": {}, "click": {"x": 10, "y": 20}, "move": {"x": 30, "y": 40},
    "drag": {"x": 0, "y": 0, "to_x": 100, "to_y": 100}, "scroll": {"dy": 10},
    "type_text": {"text": "hello \U0001f642"}, "key": {"combo": "cmd+space"},
    "open_app": {"name": "System Settings"}, "frontmost_app": {}, "wait": {"seconds": 0},
    "permissions_status": {},
}


class FakeExecutor:
    def __init__(self, home):
        self.home = home
        self.calls = []
        self.labels = []
        self.app = "Terminal"
        self.permissions = {"screen_recording": True, "accessibility": True}
        self.launch_error = None
        self.launch_output = None
        self.on_call = None
        self.bad_helper = False

    def run(self, argv, *, input=None, timeout=15):
        # The first record must be durable before *any* subprocess boundary.
        log = self.home / "Library/Logs/joulewise-cu/actions.jsonl"
        records = [json.loads(line) for line in log.read_text().splitlines()]
        assert records and records[-1]["phase"] in ("before", "execute")
        self.calls.append((list(argv), input))
        if self.on_call:
            self.on_call(argv)
        if argv[0] == "/bin/launchctl":
            if self.launch_error:
                raise self.launch_error
            return self.launch_output if self.launch_output is not None else (
                "PID\tStatus\tLabel\n" + "".join(f"-\t0\t{label}\n" for label in self.labels))
        if argv[0] == "/fake/swiftc":
            Path(argv[-1]).write_bytes(b"fake compiled helper; NEVER execute")
            return ""
        if Path(argv[0]).name.startswith("cu_input-"):
            if self.bad_helper:
                return "not json"
            operation = argv[1]
            if operation == "frontmost_app":
                return json.dumps({"name": self.app, "bundle_id": "test.synthetic"})
            if operation == "permissions_status":
                return json.dumps(self.permissions)
            if operation == "display_info":
                return json.dumps({"x": 0, "y": 0, "width": 1440, "height": 900})
            assert records[-1]["phase"] == "execute"
            return '{"ok":true}'
        if argv[0] == "/usr/sbin/screencapture":
            assert records[-1]["phase"] == "execute"
            Path(argv[-1]).write_bytes(b"synthetic PNG placeholder")
            return ""
        if argv[0] == "/usr/bin/sips":
            if "--out" in argv:
                Path(argv[-1]).write_bytes(b"synthetic JPEG placeholder")
                return ""
            dimensions = (1280, 800) if argv[-1].endswith(".jpg") else (2880, 1800)
            return f"  pixelWidth: {dimensions[0]}\n  pixelHeight: {dimensions[1]}\n"
        if argv[0] == "/usr/bin/open":
            assert records[-1]["phase"] == "execute"
            self.app = argv[-1]
            return ""
        raise AssertionError(f"Unexpected fake command: {argv}")


class ComputerUseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="jw-cu-tests-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.executor = FakeExecutor(self.home)
        self.backend = cu.MacBackend(self.home, self.executor, swiftc="/fake/swiftc")
        self.env = {}
        self.now = 1000.0
        self.tick = 10.0
        self.sleeps = []
        self.allowlist = self.home / "allowlist.json"
        self.allowlist.write_text(json.dumps({"apps": ["System Settings", "Finder", "Terminal"]}))
        self.computer = cu.ComputerUse(home=self.home, env=self.env, backend=self.backend,
                                      clock=lambda: self.now, monotonic=lambda: self.tick,
                                      sleeper=self.sleeps.append, allowlist_path=self.allowlist)

    def marker(self, value):
        path = self.home / "Library/Logs/jw-hostlink/armed_until"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
        return path

    def records(self):
        return [json.loads(line) for line in self.computer.log_path.read_text().splitlines()]

    def assertError(self, result, phrase):
        self.assertTrue(result["isError"], result)
        self.assertIn(phrase, result["content"][0]["text"])

    def test_loaded_launchd_label_refuses_every_action_even_if_not_running(self):
        self.executor.labels = ["com.joulewise.night.synthetic"]
        for name, arguments in SAMPLES.items():
            if name != "permissions_status":
                with self.subTest(name=name):
                    self.assertError(self.computer.call(name, arguments), "loaded launchd label com.joulewise.night.synthetic")
        self.assertTrue(all(call[0][0] == "/bin/launchctl" for call in self.executor.calls))
        self.assertFalse(self.sleeps)

    def test_future_marker_refuses_every_action(self):
        self.marker("1001\n")
        for name, arguments in SAMPLES.items():
            if name != "permissions_status":
                with self.subTest(name=name):
                    self.assertError(self.computer.call(name, arguments), "armed_until epoch 1001.0")
        self.assertTrue(all(call[0][0] == "/bin/launchctl" for call in self.executor.calls))

    def test_expired_marker_and_non_night_labels_allow_action(self):
        self.marker("999")
        self.executor.labels = ["com.joulewise.other", "org.example.com.joulewise.night"]
        self.assertFalse(self.computer.call("click", SAMPLES["click"])["isError"])

    def test_malformed_or_unreadable_marker_fails_closed(self):
        for value in ("", "oops", "nan", "inf"):
            with self.subTest(value=value):
                self.marker(value)
                self.assertError(self.computer.call("screenshot", {}), "invalid armed_until")
        path = self.marker("1000")
        path.unlink()
        path.mkdir()
        self.assertError(self.computer.call("wait", {"seconds": 0}), "unreadable armed_until")

    def test_unavailable_or_malformed_launchctl_fails_closed(self):
        self.executor.launch_error = cu.ToolError("launchctl failed")
        self.assertError(self.computer.call("click", SAMPLES["click"]), "launchctl failed")
        self.executor.launch_error = None
        for output in ("", "unrecognized output", "PID Status Label\nwrong row\n",
                       "PID Status Label\nhello world label\n"):
            self.executor.launch_output = output
            self.assertError(self.computer.call("wait", {"seconds": 0}), "malformed launchctl")

    def test_permissions_preflight_exempt_and_contains_no_prompt_api(self):
        self.executor.labels = ["com.joulewise.night.test"]
        self.marker("1001")
        self.executor.app = "Not Allowed"
        self.assertFalse(self.computer.call("permissions_status", {})["isError"])
        self.assertFalse(any(argv[0] == "/bin/launchctl" for argv, _ in self.executor.calls))
        source = (cu.HERE / "cu_input.swift").read_text()
        self.assertIn("CGPreflightScreenCaptureAccess()", source)
        self.assertIn("AXIsProcessTrusted()", source)
        self.assertNotIn("CGRequestScreenCaptureAccess", source)
        self.assertNotIn("AXIsProcessTrustedWithOptions", source)

    def test_allowlist_enforced_for_all_non_exempt_tools(self):
        self.executor.app = "Other App"
        for name, arguments in SAMPLES.items():
            if name not in ("screenshot", "permissions_status"):
                with self.subTest(name=name):
                    self.assertError(self.computer.call(name, arguments), "frontmost app 'Other App'")
        self.assertFalse(self.computer.call("screenshot", {})["isError"])

    def test_open_app_checks_both_target_and_frontmost_without_shell(self):
        self.assertError(self.computer.call("open_app", {"name": "Other App"}), "requested app")
        self.assertFalse(self.computer.call("open_app", {"name": "System Settings"})["isError"])
        self.assertIn((["/usr/bin/open", "-a", "System Settings"], None), self.executor.calls)

    def test_allowlist_is_reloaded_and_corruption_fails_closed(self):
        self.assertFalse(self.computer.call("frontmost_app", {})["isError"])
        self.allowlist.write_text('{"apps":["Finder"]}')
        self.assertError(self.computer.call("frontmost_app", {}), "not allowlisted")
        for value in ('{}', '{"apps":[]}', '{"apps":"Terminal"}', 'invalid'):
            self.allowlist.write_text(value)
            self.assertError(self.computer.call("frontmost_app", {}), "valid app allowlist")

    def test_dry_run_logs_only_with_no_probes_compile_input_or_sleep(self):
        self.env["JW_CU_DRY_RUN"] = "1"
        self.env["JW_CU_REDACT"] = "1"
        for name, arguments in SAMPLES.items():
            with self.subTest(name=name):
                result = self.computer.call(name, arguments)
                self.assertFalse(result["isError"])
                self.assertTrue(json.loads(result["content"][0]["text"])["dry_run"])
        self.assertEqual(self.executor.calls, [])
        self.assertEqual(self.sleeps, [])
        self.assertEqual(len(self.records()), len(SAMPLES) * 2)
        self.assertFalse((self.home / "Library/Caches").exists())

    def test_log_is_append_only_and_records_before_execution_and_result(self):
        self.assertFalse(self.computer.call("move", SAMPLES["move"])["isError"])
        original = self.computer.log_path.read_bytes()
        records = self.records()
        self.assertEqual([r["phase"] for r in records], ["before", "execute", "after"])
        self.assertEqual(len({r["call_id"] for r in records}), 1)
        self.assertEqual(records[1]["frontmost_app"]["name"], "Terminal")
        for field in ("timestamp", "tool", "arguments", "frontmost_app", "result"):
            self.assertIn(field, records[0])
        self.computer.call("wait", {"seconds": 0})
        self.assertTrue(self.computer.log_path.read_bytes().startswith(original))

    def test_log_failure_prevents_all_execution(self):
        with patch.object(self.computer, "log", side_effect=OSError("disk full")):
            self.assertError(self.computer.call("click", SAMPLES["click"]), "nothing executed")
        self.assertEqual(self.executor.calls, [])

    def test_result_log_failure_warns_against_blind_retry(self):
        original = self.computer.log
        def log(*args):
            if args[1] == "after":
                raise OSError("full")
            original(*args)
        with patch.object(self.computer, "log", side_effect=log):
            self.assertError(self.computer.call("move", SAMPLES["move"]), "may have executed")

    def test_redaction_applies_before_and_after_even_for_invalid_text_requests(self):
        self.env["JW_CU_REDACT"] = "1"
        secret = "synthetic secret \U0001f512"
        self.computer.call("type_text", {"text": secret})
        self.computer.call("type_text", {"text": secret, "unknown": secret})
        self.assertNotIn(secret, self.computer.log_path.read_text())
        self.assertTrue(all(r["arguments"] == {"text": "[REDACTED]"} for r in self.records()))
        self.assertTrue(any(json.loads(stdin or "{}").get("text") == secret for _, stdin in self.executor.calls))

    def test_rate_limit_five_input_actions_in_sliding_second(self):
        for _ in range(5):
            self.assertFalse(self.computer.call("move", SAMPLES["move"])["isError"])
        self.tick += 0.999
        self.assertError(self.computer.call("key", {"combo": "cmd+a"}), "at most 5")
        self.tick += 0.001
        self.assertFalse(self.computer.call("key", {"combo": "cmd+a"})["isError"])
        self.assertFalse(self.computer.call("frontmost_app", {})["isError"])

    def test_open_app_also_consumes_rate_budget(self):
        for _ in range(5):
            self.computer.call("open_app", {"name": "Terminal"})
        self.assertError(self.computer.call("open_app", {"name": "Terminal"}), "Rate limit")

    def test_slow_input_retains_budget_until_completion(self):
        delayed = []
        def delay_first_input(argv):
            if len(argv) > 1 and argv[1] == "move" and not delayed:
                delayed.append(True)
                self.tick += 1.1
        self.executor.on_call = delay_first_input
        for _ in range(5):
            self.assertFalse(self.computer.call("move", SAMPLES["move"])["isError"])
        self.assertError(self.computer.call("move", SAMPLES["move"]), "Rate limit")

    def test_open_app_rechecks_target_if_allowlist_changes_during_probes(self):
        checks = []
        def change_allowlist(argv):
            if argv[0] == "/bin/launchctl":
                checks.append(True)
                if len(checks) == 2:
                    self.allowlist.write_text('{"apps":["Terminal"]}')
        self.executor.on_call = change_allowlist
        self.assertError(self.computer.call("open_app", {"name": "System Settings"}), "requested app")
        self.assertFalse(any(argv[0] == "/usr/bin/open" for argv, _ in self.executor.calls))

    def test_rechecks_armed_after_first_helper_compile(self):
        def arm_during_compile(argv):
            if argv[0] == "/fake/swiftc":
                self.executor.labels = ["com.joulewise.night.just-armed"]
        self.executor.on_call = arm_during_compile
        self.assertError(self.computer.call("click", SAMPLES["click"]), "just-armed")
        self.assertFalse(any(len(argv) > 1 and argv[1] == "click" for argv, _ in self.executor.calls))

    def test_screenshot_rechecks_armed_immediately_before_capture(self):
        def arm_during_compile(argv):
            if argv[0] == "/fake/swiftc":
                self.marker("1001")
        self.executor.on_call = arm_during_compile
        self.assertError(self.computer.call("screenshot", {}), "armed_until")
        self.assertFalse(any(argv[0] == "/usr/sbin/screencapture" for argv, _ in self.executor.calls))

    def test_screenshot_can_diagnose_absent_foreground_app(self):
        with patch.object(self.backend, "frontmost", side_effect=cu.ToolError("no app")):
            self.assertFalse(self.computer.call("screenshot", {})["isError"])
        self.assertIsNone(self.records()[-1]["frontmost_app"])

    def test_log_execute_failure_prevents_actual_input(self):
        original = self.computer.log
        def log(*args):
            if args[1] == "execute":
                raise OSError("full")
            original(*args)
        with patch.object(self.computer, "log", side_effect=log):
            self.assertError(self.computer.call("move", SAMPLES["move"]), "full")
        self.assertFalse(any(len(argv) > 1 and argv[1] == "move" for argv, _ in self.executor.calls))

    def test_log_symlink_is_refused_without_execution(self):
        target = self.home / "sentinel"
        target.write_text("preserve")
        self.computer.log_path.parent.mkdir(parents=True)
        self.computer.log_path.symlink_to(target)
        self.assertError(self.computer.call("permissions_status", {}), "nothing executed")
        self.assertEqual(target.read_text(), "preserve")
        self.assertEqual(self.executor.calls, [])

    def test_rechecks_frontmost_before_input(self):
        checks = []
        def switch_app(argv):
            if argv[0] == "/bin/launchctl":
                checks.append(True)
                if len(checks) == 2:
                    self.executor.app = "Other App"
        self.executor.on_call = switch_app
        self.assertError(self.computer.call("click", SAMPLES["click"]), "Other App")

    def test_missing_swiftc_is_clear_error_without_real_compiler(self):
        self.backend.swiftc = None
        with patch.object(cu.shutil, "which", return_value=None):
            self.assertError(self.computer.call("permissions_status", {}), "swiftc is missing")

    def test_compile_is_first_use_only_and_helper_response_failures_are_errors(self):
        self.assertFalse(self.computer.call("permissions_status", {})["isError"])
        self.assertFalse(self.computer.call("permissions_status", {})["isError"])
        self.assertEqual(sum(argv[0] == "/fake/swiftc" for argv, _ in self.executor.calls), 1)
        self.executor.bad_helper = True
        self.assertError(self.computer.call("permissions_status", {}), "Invalid Swift helper")

    def test_missing_permissions_prevent_capture_or_input(self):
        self.executor.permissions = {"screen_recording": False, "accessibility": False}
        self.assertError(self.computer.call("screenshot", {}), "Screen Recording permission")
        self.assertError(self.computer.call("click", SAMPLES["click"]), "Accessibility permission")
        self.assertFalse(any(argv[0] == "/usr/sbin/screencapture" or argv[-1] == "click"
                             for argv, _ in self.executor.calls))

    def test_jpeg_mcp_content_scaling_and_temporary_cleanup(self):
        result = self.computer.call("screenshot", {})
        self.assertFalse(result["isError"])
        metadata = json.loads(result["content"][0]["text"])
        self.assertEqual(metadata["capture_pixels_per_point"], {"x": 2, "y": 2})
        self.assertAlmostEqual(metadata["scale_factor"], 1280 / 1440)
        self.assertAlmostEqual(640 / metadata["scale_x"], 720)
        self.assertEqual(result["content"][1], {"type": "image", "mimeType": "image/jpeg",
                                              "data": base64.b64encode(b"synthetic JPEG placeholder").decode()})
        capture = next(argv for argv, _ in self.executor.calls if argv[0] == "/usr/sbin/screencapture")
        self.assertEqual(capture[1:5], ["-x", "-m", "-t", "png"])
        self.assertFalse(Path(capture[-1]).parent.exists())
        self.assertNotIn("synthetic JPEG placeholder", self.computer.log_path.read_text())

    def test_nonretina_negative_origin_and_rounding_mapping(self):
        mapping = cu.coordinate_mapping({"x": -1440, "y": 10, "width": 1440, "height": 900},
                                        (1440, 900), (1280, 800))
        self.assertEqual(mapping["capture_pixels_per_point"]["x"], 1)
        self.assertAlmostEqual(-1440 + 1280 / mapping["scale_x"], 0)
        rounded = cu.coordinate_mapping({"x": 0, "y": 0, "width": 1512, "height": 982},
                                        (3024, 1964), (1280, 831))
        self.assertNotEqual(rounded["scale_x"], rounded["scale_y"])
        for size in ((0, 1), (1281, 800)):
            with self.assertRaises(cu.ToolError):
                cu.coordinate_mapping({"x": 0, "y": 0, "width": 1440, "height": 900}, (2880, 1800), size)

    def test_tool_schemas_and_runtime_validation(self):
        self.assertEqual(set(SAMPLES), {tool["name"] for tool in cu.TOOLS})
        for tool in cu.TOOLS:
            spec = tool["inputSchema"]
            self.assertEqual(spec["type"], "object")
            self.assertFalse(spec["additionalProperties"])
            self.assertTrue(set(spec["required"]) <= set(spec["properties"]))
            cu.validate(tool["name"], SAMPLES[tool["name"]])
        for name, args in (("wait", {"seconds": 10.01}), ("wait", {"seconds": -1}),
                           ("click", {"x": True, "y": 1}), ("click", {"x": float("nan"), "y": 1}),
                           ("click", {"x": 1, "y": 1, "count": 3}), ("scroll", {"dy": 0.1}),
                           ("type_text", {"text": "\ud800"}), ("move", {}), ("screenshot", {"extra": 1})):
            with self.subTest(name=name, args=repr(args)), self.assertRaises(cu.ToolError):
                cu.validate(name, args)

    def test_protocol_stdio_round_trip_and_notifications(self):
        self.env["JW_CU_DRY_RUN"] = "1"
        frames = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
                "protocolVersion": "2025-11-25", "capabilities": {},
                "clientInfo": {"name": "synthetic", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": "list", "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "click", "arguments": SAMPLES["click"]}},
            {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 3}},
            {"jsonrpc": "2.0", "method": "unknown/notification"},
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call", "params": {"name": "unknown"}},
            {"jsonrpc": "2.0", "id": 5, "method": "ping"},
        ]
        stream = io.BytesIO(b"\n".join(json.dumps(frame).encode() for frame in frames) + b"\n")
        output = io.BytesIO()
        cu.serve(stream, output, self.computer)
        responses = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([r["id"] for r in responses], [1, "list", 3, 4, 5])
        self.assertEqual(responses[0]["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(responses[1]["result"]["tools"], cu.TOOLS)
        self.assertFalse(responses[2]["result"]["isError"])
        self.assertTrue(responses[3]["result"]["isError"])
        self.assertEqual(responses[4]["result"], {})
        self.assertEqual(self.executor.calls, [])

    def test_protocol_errors_lifecycle_negotiation_and_frame_limits(self):
        protocol = cu.Protocol(self.computer)
        self.assertEqual(protocol.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["error"]["code"], -32000)
        init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": "future", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}}
        self.assertEqual(protocol.handle(init)["result"]["protocolVersion"], cu.PROTOCOL_VERSIONS[0])
        self.assertEqual(protocol.handle(init)["error"]["code"], -32600)
        protocol.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self.assertEqual(protocol.handle({"jsonrpc": "2.0", "id": 1, "method": "missing"})["error"]["code"], -32601)
        self.assertEqual(protocol.handle({"jsonrpc": "2.0", "id": True, "method": "ping"})["error"]["code"], -32600)
        self.assertEqual(protocol.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": []})["error"]["code"], -32602)
        output = io.BytesIO()
        cu.serve(io.BytesIO(b"invalid\n[]\n{\"x\":NaN}\n" + b"x" * (cu.MAX_FRAME_BYTES + 1) +
                           b'\n{"jsonrpc":"2.0","id":7,"method":"ping"}\n'), output, self.computer)
        responses = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([r["error"]["code"] for r in responses[:-1]], [-32700, -32600, -32700, -32700])
        self.assertEqual(responses[-1]["id"], 7)


if __name__ == "__main__":
    unittest.main()
