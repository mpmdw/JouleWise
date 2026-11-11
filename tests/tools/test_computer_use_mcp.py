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
    "type_text": {"text": "hello \U0001f642"}, "key": {"combo": "cmd+a"},
    "open_app": {"name": "com.apple.systempreferences"}, "frontmost_app": {}, "wait": {"seconds": 0},
    "permissions_status": {},
}


class FakeExecutor:
    def __init__(self, home):
        self.home = home
        self.calls = []
        self.labels = []
        self.app = "com.apple.finder"
        self.app_name = "Finder"
        self.pid = 42
        self.target = None
        self.permissions = {"screen_recording": True, "accessibility": True}
        self.launch_error = None
        self.launch_output = None
        self.system_labels = []
        self.domain_errors = {}
        self.caller_session = "Aqua"
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
            # A caller-relative list in SSH/Background deliberately hides GUI jobs.
            if argv[1:] == ["list"]:
                labels = self.labels if self.caller_session == "Aqua" else []
                return "PID\tStatus\tLabel\n" + "".join(f"-\t0\t{label}\n" for label in labels)
            assert argv[1] == "print" and argv[2] in (f"gui/{cu.os.getuid()}", "system")
            domain = argv[2]
            if domain in self.domain_errors:
                raise self.domain_errors[domain]
            labels = self.system_labels if domain == "system" else self.labels
            return self.launch_output if self.launch_output is not None else (
                f"{domain} = {{\n\ttype = synthetic\n\tservices = {{\n" +
                "".join(f"\t\t0\t-\t{label}\n" for label in labels) + "\t}\n}\n")
        if argv[0] == "/fake/swiftc":
            Path(argv[-1]).write_bytes(b"fake compiled helper; NEVER execute")
            return ""
        if Path(argv[0]).name.startswith("cu_input-"):
            if self.bad_helper:
                return "not json"
            operation = argv[1]
            if operation == "frontmost_app":
                return json.dumps({"name": self.app_name, "bundle_id": self.app, "pid": self.pid})
            if operation == "window_at_point":
                return json.dumps(self.target if self.target is not None else
                                  {"bundle_id": self.app, "pid": self.pid, "layer": 0})
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
        self.allowlist.write_text(json.dumps({"apps": ["com.apple.systempreferences", "com.apple.Settings", "com.apple.finder"]}))
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

    def config(self, **updates):
        value = json.loads(self.allowlist.read_text())
        value.update(updates)
        self.allowlist.write_text(json.dumps(value))

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
        self.assertError(self.computer.call("click", SAMPLES["click"]), "unreadable launchctl domain")
        self.executor.launch_error = None
        for output in ("", "unrecognized output", "PID Status Label\nwrong row\n",
                       "wrong/domain = {\n\tservices = {\n\t}\n}\n",
                       f"gui/{cu.os.getuid()} = {{\n\tservices = {{\nwrong row\n\t}}\n}}\n",
                       f"gui/{cu.os.getuid()} = {{\n\tservices = {{\nhello world label\n\t}}\n}}\n"):
            self.executor.launch_output = output
            self.assertError(self.computer.call("wait", {"seconds": 0}), "malformed launchctl")

    def test_permissions_preflight_armed_never_compiles_or_probes_even_with_warm_cache(self):
        self.executor.labels = ["com.joulewise.night.test"]
        self.marker("1001")
        self.executor.app = "Not Allowed"
        for warm in (False, True):
            with self.subTest(warm=warm):
                if warm:
                    self.backend.binary = self.home / "synthetic-cache"
                result = self.computer.call("permissions_status", {})
                self.assertFalse(result["isError"])
                status = json.loads(result["content"][0]["text"])
                self.assertTrue(status["armed"])
                for permission in ("screen_recording", "accessibility"):
                    self.assertEqual(status[permission], "unknown (armed; not compiled)")
        self.assertTrue(all(argv[0] == "/bin/launchctl" for argv, _ in self.executor.calls))
        self.assertFalse((self.home / "Library/Caches").exists())
        source = (cu.HERE / "cu_input.swift").read_text()
        self.assertIn("CGPreflightScreenCaptureAccess()", source)
        self.assertIn("AXIsProcessTrusted()", source)
        self.assertNotIn("CGRequestScreenCaptureAccess", source)
        self.assertNotIn("AXIsProcessTrustedWithOptions", source)

    def test_explicit_gui_domain_catches_night_from_ssh_and_background(self):
        for session in ("SSH", "Background"):
            for label in ("com.joulewise.night", "com.joulewise.night.synthetic"):
                with self.subTest(session=session, label=label):
                    self.executor.caller_session = session
                    self.executor.labels = [label]
                    self.assertError(self.computer.call("click", SAMPLES["click"]), "loaded launchd label")
        self.assertTrue(all(argv == ["/bin/launchctl", "print", f"gui/{cu.os.getuid()}"]
                            for argv, _ in self.executor.calls))

    def test_unreadable_gui_or_system_domain_refuses_even_permissions_compile(self):
        for domain in (f"gui/{cu.os.getuid()}", "system"):
            for failure in (cu.ToolError("no domain"), TimeoutError("timeout"), RuntimeError("probe failed")):
                with self.subTest(domain=domain, failure=type(failure).__name__):
                    self.executor.domain_errors = {domain: failure}
                    for name in ("wait", "open_app", "permissions_status"):
                        self.assertError(self.computer.call(name, SAMPLES[name]), f"unreadable launchctl domain {domain}")
        self.assertTrue(all(argv[0] == "/bin/launchctl" for argv, _ in self.executor.calls))

    def test_system_domain_night_is_also_refused(self):
        self.executor.system_labels = ["com.joulewise.night.system-fixture"]
        self.assertError(self.computer.call("open_app", SAMPLES["open_app"]), "in system")

    def test_missing_duplicate_or_truncated_services_section_fails_closed(self):
        domain = f"gui/{cu.os.getuid()}"
        for output in (f"{domain} = {{\n}}\n", f"{domain} = {{\n\tservices = {{\n\t}}\n",
                       f"{domain} = {{\n\tservices = {{\n\t}}\n\tservices = {{\n\t}}\n}}\n"):
            with self.subTest(output=output):
                self.executor.launch_output = output
                self.assertError(self.computer.call("wait", SAMPLES["wait"]), "malformed launchctl")

    def test_permissions_marker_armed_returns_unknown_without_helper(self):
        self.marker("1001")
        result = self.computer.call("permissions_status", {})
        self.assertFalse(result["isError"])
        self.assertTrue(json.loads(result["content"][0]["text"])["armed"])
        self.assertTrue(all(argv[0] == "/bin/launchctl" for argv, _ in self.executor.calls))

    def test_permissions_unarmed_compiles_and_reports_booleans(self):
        status = json.loads(self.computer.call("permissions_status", {})["content"][0]["text"])
        self.assertEqual(status, {"armed": False, "screen_recording": True, "accessibility": True})
        self.assertEqual(sum(argv[0] == "/fake/swiftc" for argv, _ in self.executor.calls), 1)

    def test_configurable_remote_markers_missing_then_future_and_reloaded_switch(self):
        alternate = self.home / "synthetic-remote-marker"
        self.config(armed_marker_paths=["~/missing-marker", str(alternate)])
        self.marker("2000")  # Default location is no longer selected.
        self.assertFalse(self.computer.call("wait", SAMPLES["wait"])["isError"])
        alternate.write_text("1001")
        self.assertError(self.computer.call("wait", SAMPLES["wait"]), "armed_until epoch")
        self.config(respect_remote_armed=False)
        self.assertFalse(self.computer.call("wait", SAMPLES["wait"])["isError"])
        self.executor.labels = ["com.joulewise.night.local"]
        self.assertError(self.computer.call("wait", SAMPLES["wait"]), "loaded launchd label")
        self.config(respect_remote_armed=True)
        self.executor.labels = []
        self.assertError(self.computer.call("wait", SAMPLES["wait"]), "armed_until epoch")

    def test_invalid_marker_configuration_fails_closed(self):
        for updates in ({"respect_remote_armed": "false"}, {"respect_remote_armed": 0},
                        {"armed_marker_paths": []}, {"armed_marker_paths": "~/marker"},
                        {"armed_marker_paths": ["relative"]}, {"armed_marker_paths": [3]}):
            with self.subTest(updates=updates):
                self.config(respect_remote_armed=True, armed_marker_paths=["~/valid"])
                self.config(**updates)
                self.assertError(self.computer.call("wait", SAMPLES["wait"]), "valid app allowlist")

    def test_default_bundle_allowlist_excludes_terminal_and_has_display_comments(self):
        config = json.loads((cu.HERE / "allowlist.json").read_text())
        self.assertEqual(set(config["apps"]), {"com.apple.systempreferences", "com.apple.Settings", "com.apple.finder"})
        self.assertEqual(set(config["_comments"]), set(config["apps"]))
        self.assertTrue(config["respect_remote_armed"])

    def test_bundle_ids_allow_localized_names_and_refuse_name_spoofs(self):
        self.executor.app_name = "Réglages Système"
        for bundle in ("com.apple.systempreferences", "com.apple.Settings", "com.apple.finder"):
            self.executor.app = bundle
            self.assertFalse(self.computer.call("frontmost_app", {})["isError"])
        self.executor.app_name = "Finder"
        self.executor.app = "org.example.spoof"
        self.assertError(self.computer.call("frontmost_app", {}), "not allowlisted")

    def test_terminal_requires_explicit_bundle_opt_in(self):
        self.executor.app = "com.apple.Terminal"
        self.assertError(self.computer.call("type_text", SAMPLES["type_text"]), "not allowlisted")
        self.config(apps=["com.apple.Terminal"])
        self.assertFalse(self.computer.call("type_text", SAMPLES["type_text"])["isError"])

    def test_missing_frontmost_bundle_or_pid_refuses(self):
        for app, pid in (("", 42), ("com.apple.finder", 0), ("com.apple.finder", True)):
            with self.subTest(app=app, pid=pid):
                self.executor.app, self.executor.pid = app, pid
                self.assertError(self.computer.call("click", SAMPLES["click"]), "Cannot determine frontmost app")

    def test_switcher_launcher_combos_aliases_order_and_extra_modifiers_blocked(self):
        for combo in ("cmd+tab", "cmd+space", "cmd+shift+tab", "ctrl+up", "ctrl+down", "cmd+opt+esc",
                      " Command + TAB ", "shift+command+tab", "control+down", "alt+cmd+escape",
                      "command+option+shift+escape", "cmd+shift+space", "fn+control+up"):
            with self.subTest(combo=combo):
                self.assertError(self.computer.call("key", {"combo": combo}), "combos are blocked")
        self.assertEqual(self.executor.calls, [])

    def test_click_requires_frontmost_pid_bundle_and_normal_window_layer(self):
        for target in ({"bundle_id": "org.example.other", "pid": 99, "layer": 0},
                       {"bundle_id": "com.apple.finder", "pid": 99, "layer": 0},
                       {"bundle_id": "com.apple.finder", "pid": 42, "layer": 25},
                       {"bundle_id": "com.apple.dock", "pid": 42, "layer": 0},
                       {"bundle_id": "com.apple.finder", "pid": 42, "layer": -1}, {},
                       {"bundle_id": "com.apple.finder", "pid": 42, "layer": False}):
            with self.subTest(target=target):
                self.tick += 1
                self.executor.target = target
                self.assertError(self.computer.call("click", SAMPLES["click"]), "Click refusal")
        self.assertFalse(any(len(argv) > 1 and argv[1] == "click" for argv, _ in self.executor.calls))

    def test_click_passes_expected_identity_to_native_posting_recheck(self):
        self.assertFalse(self.computer.call("click", {**SAMPLES["click"], "count": 2})["isError"])
        operations = [argv[1] for argv, _ in self.executor.calls if len(argv) > 1]
        self.assertLess(operations.index("window_at_point"), operations.index("click"))
        arguments = next(json.loads(stdin) for argv, stdin in self.executor.calls if argv[-1] == "click")
        self.assertEqual(arguments["expected_pid"], 42)
        self.assertEqual(arguments["expected_bundle_id"], "com.apple.finder")
        source = (cu.HERE / "cu_input.swift").read_text()
        self.assertIn("CGWindowListCopyWindowInfo(.optionOnScreenOnly", source)
        self.assertNotIn("excludeDesktopElements", source)
        self.assertIn('try checkClickTarget(args, p)\n            try mouse(right ?', source)
        self.assertIn('flags.contains(.maskCommand) && ["tab", "space"].contains(last)', source)

    def test_window_inspection_failure_refuses_click_and_logs_after(self):
        helper = self.backend.helper
        def fail_window(operation, arguments=None):
            if operation == "window_at_point":
                raise cu.ToolError("no owning window")
            return helper(operation, arguments)
        with patch.object(self.backend, "helper", side_effect=fail_window):
            self.assertError(self.computer.call("click", SAMPLES["click"]), "no owning window")
        self.assertEqual(self.records()[-1]["phase"], "after")
        self.assertFalse(any(len(argv) > 1 and argv[1] == "click" for argv, _ in self.executor.calls))

    def test_armed_after_window_inspection_refuses_click(self):
        def arm_at_target(argv):
            if len(argv) > 1 and argv[1] == "window_at_point":
                self.executor.labels = ["com.joulewise.night.just-armed"]
        self.executor.on_call = arm_at_target
        self.assertError(self.computer.call("click", SAMPLES["click"]), "just-armed")
        self.assertFalse(any(len(argv) > 1 and argv[1] == "click" for argv, _ in self.executor.calls))

    def test_open_app_rechecks_armed_after_cold_preflight_compile(self):
        def arm_during_compile(argv):
            if argv[0] == "/fake/swiftc":
                self.executor.labels = ["com.joulewise.night.just-armed"]
        self.executor.on_call = arm_during_compile
        self.assertError(self.computer.call("open_app", SAMPLES["open_app"]), "just-armed")
        self.assertFalse(any(argv[0] == "/usr/bin/open" for argv, _ in self.executor.calls))

    def test_allowlist_enforced_for_all_non_exempt_tools(self):
        self.executor.app = "org.example.other"
        for name, arguments in SAMPLES.items():
            if name not in ("screenshot", "permissions_status", "open_app"):
                with self.subTest(name=name):
                    self.assertError(self.computer.call(name, arguments), "frontmost app 'org.example.other'")
        self.assertFalse(self.computer.call("screenshot", {})["isError"])

    def test_open_app_checks_target_and_recovers_focus_without_shell(self):
        self.executor.app = "org.example.other"
        self.assertError(self.computer.call("open_app", {"name": "Other App"}), "requested app")
        self.assertFalse(self.computer.call("open_app", {"name": "com.apple.systempreferences"})["isError"])
        self.assertIn((["/usr/bin/open", "-b", "com.apple.systempreferences"], None), self.executor.calls)
        self.assertFalse(any(len(argv) > 1 and argv[1] == "frontmost_app" for argv, _ in self.executor.calls))

    def test_allowlist_is_reloaded_and_corruption_fails_closed(self):
        self.assertFalse(self.computer.call("frontmost_app", {})["isError"])
        self.allowlist.write_text('{"apps":["com.apple.systempreferences"]}')
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

    def test_dry_run_ambiguous_values_are_safe_and_only_empty_or_zero_are_live(self):
        for value in ("true", "yes", "01", "false", "no", " 0", "0 ", "garbage", "\n"):
            self.env["JW_CU_DRY_RUN"] = value
            with self.subTest(value=value):
                result = self.computer.call("wait", SAMPLES["wait"])
                self.assertFalse(result["isError"])
                self.assertTrue(json.loads(result["content"][0]["text"])["dry_run"])
        self.assertFalse(self.executor.calls)
        self.assertFalse(self.sleeps)
        for value in (None, "", "0"):
            if value is None:
                self.env.pop("JW_CU_DRY_RUN", None)
            else:
                self.env["JW_CU_DRY_RUN"] = value
            result = self.computer.call("wait", SAMPLES["wait"])
            self.assertFalse(result["isError"])
            self.assertEqual(json.loads(result["content"][0]["text"]), {"waited_seconds": 0})
        self.assertEqual(self.sleeps, [0, 0, 0])

    def test_unexpected_tool_exceptions_get_after_error_and_server_continues(self):
        for failure in (RuntimeError("synthetic runtime"), TypeError("synthetic type"),
                        KeyError("synthetic key"), AssertionError("synthetic assert")):
            with self.subTest(failure=type(failure).__name__):
                with patch.object(self.computer, "execute", side_effect=failure):
                    self.assertError(self.computer.call("wait", SAMPLES["wait"]), type(failure).__name__)
                after = self.records()[-1]
                self.assertEqual(after["phase"], "after")
                self.assertTrue(after["result"]["isError"])
                self.assertIn(type(failure).__name__, after["result"]["content"][0]["text"])
                self.assertFalse(self.computer.call("wait", SAMPLES["wait"])["isError"])

    def test_unexpected_probe_result_shape_and_completion_exceptions_are_contained(self):
        with patch.object(self.backend, "frontmost", side_effect=RuntimeError("probe")):
            self.assertError(self.computer.call("wait", SAMPLES["wait"]), "RuntimeError")
        with patch.object(self.computer, "execute", return_value={"wrong": "shape"}):
            self.assertError(self.computer.call("wait", SAMPLES["wait"]), "KeyError")
        with patch.object(self.computer, "execute", return_value={"content": [], "extra": object()}):
            self.assertError(self.computer.call("wait", SAMPLES["wait"]), "TypeError")
        # Fail after the rate reservation and native operation have completed.
        with patch.object(self.computer, "monotonic", side_effect=[10.0, RuntimeError("clock")]):
            self.assertError(self.computer.call("move", SAMPLES["move"]), "clock")
        self.assertEqual(self.records()[-1]["phase"], "after")

    def test_unexpected_log_errors_at_every_phase_are_contained(self):
        original = self.computer.log
        for phase in ("before", "execute", "after"):
            phases = []
            def log(*args):
                phases.append(args[1])
                if args[1] == phase:
                    raise RuntimeError("synthetic log failure")
                return original(*args)
            with self.subTest(phase=phase), patch.object(self.computer, "log", side_effect=log):
                self.executor.calls.clear()
                result = self.computer.call("wait", SAMPLES["wait"])
                self.assertTrue(result["isError"])
                self.assertIn("after", phases)
                if phase == "before":
                    self.assertFalse(self.executor.calls)
                elif phase == "execute":
                    self.assertEqual(self.records()[-1]["phase"], "after")
                else:
                    self.assertIn("may have executed", result["content"][0]["text"])

    def test_stdio_continues_with_next_tool_call_after_unexpected_error(self):
        frames = [
            {"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": {
                "protocolVersion": "2025-11-25", "capabilities": {},
                "clientInfo": {"name": "synthetic", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            *[{"jsonrpc": "2.0", "id": n, "method": "tools/call", "params": {
                "name": "wait", "arguments": SAMPLES["wait"]}} for n in (1, 2)],
            {"jsonrpc": "2.0", "id": 3, "method": "ping"},
        ]
        stream = io.BytesIO(b"\n".join(json.dumps(frame).encode() for frame in frames) + b"\n")
        output = io.BytesIO()
        with patch.object(self.computer, "execute", side_effect=[RuntimeError("synthetic failure"),
                                                               cu.text_result({"waited_seconds": 0})]):
            cu.serve(stream, output, self.computer)
        responses = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual([r["id"] for r in responses], [0, 1, 2, 3])
        self.assertTrue(responses[1]["result"]["isError"])
        self.assertFalse(responses[2]["result"]["isError"])
        self.assertEqual(responses[3]["result"], {})

    def test_log_is_append_only_and_records_before_execution_and_result(self):
        self.assertFalse(self.computer.call("move", SAMPLES["move"])["isError"])
        original = self.computer.log_path.read_bytes()
        records = self.records()
        self.assertEqual([r["phase"] for r in records], ["before", "execute", "after"])
        self.assertEqual(len({r["call_id"] for r in records}), 1)
        self.assertEqual(records[1]["frontmost_app"]["bundle_id"], "com.apple.finder")
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
            self.computer.call("open_app", {"name": "com.apple.finder"})
        self.assertError(self.computer.call("open_app", {"name": "com.apple.finder"}), "Rate limit")

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
                if len(checks) == 3:
                    self.allowlist.write_text('{"apps":["com.apple.finder"]}')
        self.executor.on_call = change_allowlist
        self.assertError(self.computer.call("open_app", {"name": "com.apple.systempreferences"}), "requested app")
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
                if len(checks) == 3:
                    self.executor.app = "org.example.other"
        self.executor.on_call = switch_app
        self.assertError(self.computer.call("move", SAMPLES["move"]), "org.example.other")

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
