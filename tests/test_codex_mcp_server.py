"""Replay-based tests; no test invokes a real Codex model turn.

Adapted from t3code (MIT, T3 Tools Inc.), commit defb7e6e, packages/effect-codex-app-server/src/replay.ts
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import queue
import re
import shutil
import signal
import subprocess
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "scripts/codex-mcp-server.mjs"
FIXTURES = ROOT / "tests/fixtures/codex_app_server"
PEER = FIXTURES / "replay_peer.mjs"
# Three adapter heartbeat intervals cover interpreter startup and scripted IO.
# Polling is 1/100 of a heartbeat; tests never wait for a real model.
HEARTBEAT = 5
WAIT = HEARTBEAT * 3
POLL = HEARTBEAT / 100
MODEL = "gpt-6.1-sol"


def transcript(name):
    return [json.loads(line) for line in (FIXTURES / f"{name}.ndjson").read_text().splitlines()]


def validate(value, schema, root=None):
    """Validate the keywords used by the pinned generated schema, without deps.

    This is deliberately not a general JSON Schema implementation. Fail closed
    when a future schema introduces an unsupported validation keyword. Formats
    here are integer-width annotations, not additional JSON Schema assertions.
    """
    root = schema if root is None else root
    if schema is True:
        return
    if schema is False:
        raise AssertionError("false schema")
    allowed = {"type", "properties", "required", "enum", "$ref", "anyOf", "oneOf",
               "items", "format", "additionalProperties", "minimum", "allOf",
               "definitions", "minLength"}
    assert not set(schema) - allowed, set(schema) - allowed
    if "$ref" in schema:
        target = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            target = target[part]
        validate(value, target, root)
    for key in ("oneOf", "anyOf", "allOf"):
        if key in schema:
            matches = 0
            for branch in schema[key]:
                try:
                    validate(value, branch, root)
                    matches += 1
                except AssertionError:
                    pass
            assert matches == 1 if key == "oneOf" else matches > 0 if key == "anyOf" else matches == len(schema[key]), (key, value)
    types = {"object": lambda: isinstance(value, dict), "array": lambda: isinstance(value, list),
             "string": lambda: isinstance(value, str), "null": lambda: value is None,
             "boolean": lambda: isinstance(value, bool),
             "integer": lambda: isinstance(value, int) and not isinstance(value, bool),
             "number": lambda: isinstance(value, (int, float)) and not isinstance(value, bool)}
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        assert any(types[name]() for name in names), (names, value)
    if "enum" in schema:
        assert value in schema["enum"], (value, schema["enum"])
    if "minLength" in schema and isinstance(value, str):
        assert len(value) >= schema["minLength"]
    if "minimum" in schema and isinstance(value, (int, float)):
        assert value >= schema["minimum"]
    if isinstance(value, dict):
        assert set(schema.get("required", [])) <= value.keys(), (schema.get("required"), value.keys())
        props = schema.get("properties", {})
        for key, entry in value.items():
            validate(entry, props.get(key, schema.get("additionalProperties", True)), root)
    if isinstance(value, list) and "items" in schema:
        for entry in value:
            validate(entry, schema["items"], root)


class Session:
    def __init__(self, case, scenario, entries=None, env=None, directory=None):
        self.case = case
        self.tmp = tempfile.TemporaryDirectory(prefix="codex-mcp-test-") if directory is None else None
        self.directory = Path(self.tmp.name) if self.tmp else directory
        self.frames = self.directory / f"{scenario}-frames.ndjson"
        self.pidfile = self.directory / f"{scenario}-peer.pid"
        path = FIXTURES / f"{scenario}.ndjson"
        if entries is not None:
            path = self.directory / f"{scenario}.ndjson"
            path.write_text("".join(json.dumps(e) + "\n" for e in entries))
        self.entries = entries or transcript(scenario)
        self.messages = []
        self.errors = []
        self.output = queue.Queue()
        self.proc = subprocess.Popen(
            [shutil.which("node"), str(SERVER)], cwd=self.directory,
            env={**os.environ, "CODEX_BIN": str(PEER), "CODEX_REPLAY_TRANSCRIPT": str(path),
                 "CODEX_REPLAY_PID": str(self.pidfile), "CODEX_MCP_FRAME_LOG": str(self.frames), **(env or {})},
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        def read_stdout():
            for line in self.proc.stdout:
                self.output.put(json.loads(line))
            self.output.put(None)
        def read_stderr():
            self.errors.extend(self.proc.stderr)
        self.readers = [threading.Thread(target=read_stdout), threading.Thread(target=read_stderr)]
        for reader in self.readers:
            reader.start()
        case.addCleanup(self.cleanup)

    def send(self, method, params=None, id=None):
        frame = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            frame["params"] = params
        if id is not None:
            frame["id"] = id
        self.proc.stdin.write(json.dumps(frame) + "\n")
        self.proc.stdin.flush()

    def receive(self, id):
        deadline = time.monotonic() + WAIT
        while True:
            message = self.output.get(timeout=max(POLL, deadline - time.monotonic()))
            if message is None:
                raise AssertionError("adapter EOF: " + "".join(self.errors))
            self.messages.append(message)
            if message.get("id") == id:
                return message

    def initialize(self):
        self.send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                 "clientInfo": {"name": "test", "version": "1"}}, id=1)
        result = self.receive(1)["result"]
        self.case.assertEqual(result["serverInfo"]["name"], "codex")
        self.case.assertEqual(result["protocolVersion"], "2025-06-18")
        self.send("notifications/initialized")

    def call(self, args=None, name=None, id=3, token=None):
        meta = self.entries[0]["metadata"]
        params = {"name": name or meta["tool"], "arguments": args if args is not None else meta["arguments"]}
        if token is not None:
            params["_meta"] = {"progressToken": token}
        self.send("tools/call", params, id)

    def log(self):
        return [json.loads(l) for l in (self.directory / ".codex-bridge/mcp-calls.jsonl").read_text().splitlines()]

    def wait_frame(self, method):
        deadline = time.monotonic() + WAIT
        while time.monotonic() < deadline:
            if self.frames.exists():
                for line in self.frames.read_text().splitlines():
                    if json.loads(line).get("frame", {}).get("method") == method:
                        return
            if self.proc.poll() is not None:
                break
            time.sleep(POLL)
        raise AssertionError(f"no frame {method}: {''.join(self.errors)}")

    def stop(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
        self.proc.wait(timeout=WAIT)
        for reader in self.readers:
            reader.join(timeout=WAIT)
        self.case.assertNotIn("REPLAY ERROR", "".join(self.errors))

    def cleanup(self):
        if self.proc.poll() is None:
            self.proc.terminate()
        try:
            self.proc.wait(timeout=WAIT)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=WAIT)
        for reader in self.readers:
            reader.join(timeout=WAIT)
        for stream in [self.proc.stdin, self.proc.stdout, self.proc.stderr]:
            if stream and not stream.closed:
                stream.close()
        if self.tmp:
            self.tmp.cleanup()


@unittest.skipUnless(shutil.which("node"), "Node is required")
class CodexMcpTests(unittest.TestCase):
    def session(self, scenario="normal", **kwargs):
        session = Session(self, scenario, **kwargs)
        session.initialize()
        return session

    def test_child_is_spawned_before_any_mcp_request(self):
        session = Session(self, "initialize_only")
        deadline = time.monotonic() + WAIT
        while not session.pidfile.exists() and time.monotonic() < deadline:
            time.sleep(POLL)
        self.assertTrue(session.pidfile.exists(), "adapter did not spawn its peer until MCP input")
        os.kill(int(session.pidfile.read_text()), 0)
        session.initialize()
        session.stop()

    def test_tool_schema_compatibility_and_no_model_turn_for_listing(self):
        session = self.session("initialize_only")
        session.send("tools/list", {}, id=2)
        tools = session.receive(2)["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["codex", "codex-reply"])
        self.assertEqual(set(tools[0]["inputSchema"]["properties"]), {
            "prompt", "approval-policy", "base-instructions", "compact-prompt", "config", "cwd",
            "developer-instructions", "model", "sandbox"})
        self.assertEqual(tools[0]["inputSchema"]["required"], ["prompt"])
        self.assertIn("conversationId", tools[1]["inputSchema"]["properties"])
        session.stop()

    def test_normal_turn_and_private_pending_and_final_log(self):
        session = self.session()
        session.call()
        result = session.receive(3)["result"]
        self.assertNotIn("isError", result)
        self.assertEqual(result["content"][0]["text"], "fixture simple ok")
        metadata = result["structuredContent"]
        self.assertEqual(metadata["model"], MODEL)
        self.assertEqual(metadata["reasoningEffort"], "high")
        self.assertEqual(metadata["turnStatus"], "completed")
        logs = session.log()
        self.assertEqual([e["status"] for e in logs], ["pending", "completed"])
        self.assertEqual(logs[0]["threadId"], metadata["threadId"])
        self.assertEqual(logs[0]["callId"], logs[1]["callId"])
        self.assertEqual(logs[1]["finalMessageSha256"], hashlib.sha256(b"fixture simple ok").hexdigest())
        prompt = session.entries[0]["metadata"]["arguments"]["prompt"]
        self.assertEqual(logs[0]["promptSha256"], hashlib.sha256(prompt.encode()).hexdigest())
        self.assertNotIn(prompt, json.dumps(logs))
        self.assertEqual((session.directory / ".codex-bridge/mcp-calls.jsonl").stat().st_mode & 0o777, 0o600)
        session.stop()

    def test_readback_effort_and_instruction_mapping_are_used(self):
        entries = transcript("normal")
        # Request xhigh, but report high from the peer: the actual turn and
        # output must use the confirmed high value, not echo the request.
        for e in entries:
            f = e.get("frame", {})
            if f.get("method") == "thread/start":
                f["params"]["config"].update(model_reasoning_effort="xhigh", compact_prompt="Compact fixture")
                f["params"].update(baseInstructions="Base fixture", developerInstructions="Developer fixture")
        session = self.session("normal", entries=entries)
        args = {**entries[0]["metadata"]["arguments"], "config": {"model_reasoning_effort": "xhigh"},
                "base-instructions": "Base fixture", "developer-instructions": "Developer fixture", "compact-prompt": "Compact fixture"}
        session.call(args)
        result = session.receive(3)["result"]
        self.assertNotIn("isError", result)
        self.assertEqual(result["structuredContent"]["reasoningEffort"], "high")
        self.assertEqual(session.log()[-1]["reasoningEffort"], "high")
        session.stop()

    def test_xhigh_workspace_turn_uses_explicit_policy(self):
        entries = transcript("normal")
        def update(value):
            if isinstance(value, dict):
                for key, entry in value.items():
                    if key in ["effort", "model_reasoning_effort", "reasoningEffort", "reasoning_effort"] and entry == "high":
                        value[key] = "xhigh"
                    elif key == "sandbox" and entry == "read-only":
                        value[key] = "workspace-write"
                    elif key == "type" and entry == "readOnly":
                        value[key] = "workspaceWrite"
                    else:
                        update(entry)
            elif isinstance(value, list):
                for entry in value:
                    update(entry)
        update(entries)
        session = self.session("normal", entries=entries)
        session.call({**entries[0]["metadata"]["arguments"], "config": {"model_reasoning_effort": "xhigh"}, "sandbox": "workspace-write"})
        result = session.receive(3)["result"]
        self.assertNotIn("isError", result)
        self.assertEqual(result["structuredContent"]["reasoningEffort"], "xhigh")
        self.assertEqual(session.log()[-1]["sandbox"]["type"], "workspaceWrite")
        session.stop()

    def test_already_initialized_is_success_and_initialization_is_not_repeated(self):
        entries = transcript("normal")
        entries[2]["frame"] = {"id": 1, "error": {"code": -32600, "message": "Already initialized"}}
        session = self.session("normal", entries=entries)
        session.send("initialize", {"protocolVersion": "2025-06-18"}, id=2)
        self.assertIn("result", session.receive(2))
        session.call()
        self.assertNotIn("isError", session.receive(3)["result"])
        session.stop()

    def test_frame_log_is_off_unless_explicitly_enabled(self):
        session = self.session("normal", env={"CODEX_MCP_FRAME_LOG": ""})
        session.call()
        self.assertNotIn("isError", session.receive(3)["result"])
        session.stop()
        self.assertFalse(session.frames.exists())

    def test_missing_or_unsafe_readback_refuses_before_turn_start(self):
        for field, value, reason in [
            ("reasoningEffort", None, "readback required"),
            ("model", "other-model", "selected model"),
            ("sandbox", {"type": "dangerFullAccess"}, "sandbox"),
            ("approvalPolicy", "never", "removed approvals"),
            ("approvalsReviewer", "auto_review", "automatic approval"),
        ]:
            with self.subTest(field=field):
                entries = transcript("normal")
                index = next(i for i, e in enumerate(entries) if "thread" in e.get("frame", {}).get("result", {}))
                entries = entries[:index + 1]
                entries[-1]["frame"]["result"][field] = value
                session = self.session("normal", entries=entries)
                session.call()
                result = session.receive(3)["result"]
                self.assertTrue(result["isError"])
                if field == "reasoningEffort":
                    self.assertIsNone(result["structuredContent"]["reasoningEffort"])
                self.assertIn(reason, result["content"][0]["text"])
                session.stop()

    def test_completion_without_final_message_is_error(self):
        entries = [e for e in transcript("normal") if e.get("frame", {}).get("method") not in ["item/completed", "item/agentMessage/delta"]]
        entries[-1]["frame"]["params"]["turn"]["items"] = []
        session = self.session("normal", entries=entries)
        session.call()
        result = session.receive(3)["result"]
        self.assertTrue(result["isError"])
        self.assertIn("without a final agent message", result["content"][0]["text"])
        session.stop()

    def test_one_hop_is_forced_for_nested_dotted_and_parent_overrides(self):
        for config in [{"mcp_servers": {"claude": {"enabled": True}}},
                       {"mcp_servers.claude.enabled": True},
                       {"mcp_servers.claude": True},
                       {"mcp_servers.claude.enabled.child": True}]:
            with self.subTest(config=config):
                session = self.session()
                args = {**session.entries[0]["metadata"]["arguments"], "config": config}
                session.call(args)
                self.assertNotIn("isError", session.receive(3)["result"])
                session.stop()  # Peer checks forced config in actual thread/start.

    def test_refusals_do_not_start_or_resume_a_thread(self):
        session = self.session("initialize_only")
        bad = [
            {"model": "gpt-5.6-sol"}, {"model": ""}, {"sandbox": "danger-full-access"},
            {"sandbox": "external-sandbox"}, {"approval-policy": "never"},
            {"config": {"model": "other"}}, {"config": {"model_reasoning_effort": "low"}},
            {"config": {"model_reasoning_effort": "ultra"}}, {"config": {"model_reasoning_effort": None}},
            {"config": {"sandbox_mode": "danger-full-access"}}, {"config": {"approval_policy": "never"}},
            {"config": {"approval_policy": {"granular": {"sandbox_approval": False}}}},
            {"config": {"approvals_reviewer": "auto_review"}},
            {"config": {"profiles": {"unsafe": {"approval_policy": "never"}}}},
            {"config": {"profiles.unsafe.model": "other"}}, {"config": []}, {"config": {"model'": "other"}},
            {"effort": "high"}, {"prompt": ""}, {"prompt": 7},
        ]
        for number, override in enumerate(bad, 10):
            with self.subTest(override=override):
                session.call({"prompt": "refusal probe", **override}, id=number)
                self.assertTrue(session.receive(number)["result"]["isError"])
        self.assertEqual(len(session.log()), len(bad))
        self.assertTrue(all(e["threadId"] is None for e in session.log()))
        session.stop()

    def test_resume_after_restart_and_deprecated_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            first = self.session("restart_start", directory=directory)
            first.call()
            thread_id = first.receive(3)["result"]["structuredContent"]["threadId"]
            first.stop()
            second = self.session("resume", directory=directory)
            args = copy.deepcopy(second.entries[0]["metadata"]["arguments"])
            self.assertEqual(args.pop("threadId"), thread_id)
            args["conversationId"] = thread_id
            second.call(args)
            result = second.receive(3)["result"]
            self.assertNotIn("isError", result)
            self.assertEqual(result["structuredContent"]["threadId"], thread_id)
            second.stop()

    def test_same_process_reply_uses_loaded_thread_without_resume(self):
        entries = transcript("restart_start")
        resumed = transcript("resume")
        offset = next(i for i, e in enumerate(resumed) if e.get("frame", {}).get("method") == "turn/start")
        entries += resumed[offset:]
        session = self.session("restart_start", entries=entries)
        session.call()
        first = session.receive(3)["result"]
        self.assertNotIn("isError", first)
        session.call(resumed[0]["metadata"]["arguments"], name="codex-reply", id=4)
        second = session.receive(4)["result"]
        self.assertNotIn("isError", second)
        self.assertEqual(first["structuredContent"]["threadId"], second["structuredContent"]["threadId"])
        session.stop()

    def test_archived_thread_is_unarchived_before_retry(self):
        session = self.session("archived_resume")
        session.call()
        self.assertNotIn("isError", session.receive(3)["result"])
        session.stop()

    def test_all_five_server_request_types_are_declined_and_reported(self):
        expected = {"command_declined": ["item/commandExecution/requestApproval"],
                    "file_declined": ["item/fileChange/requestApproval"],
                    "other_declined": ["item/permissions/requestApproval", "item/tool/requestUserInput", "mcpServer/elicitation/request"]}
        for scenario, methods in expected.items():
            with self.subTest(scenario=scenario):
                session = self.session(scenario)
                session.call()
                result = session.receive(3)["result"]
                self.assertNotIn("isError", result)
                refused = result["structuredContent"]["declinedRequests"]
                self.assertEqual([e["method"] for e in refused], methods)
                self.assertTrue(result["content"][0]["text"].startswith("Declined requests:"))
                self.assertEqual(session.log()[-1]["declinedRequests"], refused)
                session.stop()  # Transcript checks exact schema decline responses.

    def test_decline_notice_keeps_agent_bridge_envelope_final(self):
        entries = transcript("command_declined")
        envelope = 'BRIDGE_REPORT_V1\n{"status":"DISCUSSION","summary":"fixture","pathspec":[],"verification":[],"flags":[]}'
        def replace_final(value):
            if isinstance(value, dict):
                if value.get("type") == "agentMessage" and value.get("phase") == "final_answer":
                    value["text"] = envelope
                for entry in value.values():
                    replace_final(entry)
            elif isinstance(value, list):
                for entry in value:
                    replace_final(entry)
        replace_final(entries)
        session = self.session("command_declined", entries=entries)
        session.call()
        result = session.receive(3)["result"]
        self.assertNotIn("isError", result)
        self.assertEqual("\n".join(result["content"][0]["text"].splitlines()[-2:]), envelope)
        self.assertEqual(session.log()[-1]["finalMessageSha256"], hashlib.sha256(envelope.encode()).hexdigest())
        session.stop()

    def test_reroute_and_failed_turn_are_tool_errors(self):
        for scenario, reason in [("rerouted", "model/rerouted"), ("failed", "scripted provider failure")]:
            with self.subTest(scenario=scenario):
                session = self.session(scenario)
                session.call()
                result = session.receive(3)["result"]
                self.assertTrue(result["isError"])
                self.assertIn(reason, result["content"][0]["text"])
                if scenario == "rerouted":
                    self.assertEqual(result["structuredContent"]["model"], "gpt-6-luna")
                session.stop()

    def test_child_exit_and_malformed_message_fail_call_then_exit(self):
        for scenario in ["crash", "malformed"]:
            with self.subTest(scenario=scenario):
                session = self.session(scenario)
                session.call()
                self.assertTrue(session.receive(3)["result"]["isError"])
                session.proc.wait(timeout=WAIT)
                self.assertNotEqual(session.proc.returncode, 0)
                self.assertEqual(session.log()[-1]["status"], "error")

    def test_external_child_kill_fails_call_then_exits_adapter(self):
        session = self.session("cancel")
        session.call()
        session.wait_frame("turn/started")
        os.kill(int(session.pidfile.read_text()), signal.SIGKILL)
        result = session.receive(3)["result"]
        self.assertTrue(result["isError"])
        self.assertRegex(result["content"][0]["text"], "app-server (exited|output ended)")
        session.proc.wait(timeout=WAIT)
        self.assertNotEqual(session.proc.returncode, 0)

    def test_missing_binary_exits_before_initialization(self):
        session = Session(self, "initialize_only", env={"CODEX_BIN": "/definitely/missing/codex"})
        # Spawn can fail before stdin is read; no initialization success may
        # escape in either ordering. There need not be an in-flight call yet.
        session.proc.wait(timeout=WAIT)
        self.assertNotEqual(session.proc.returncode, 0)
        for reader in session.readers:
            reader.join(timeout=WAIT)
        self.assertIn("Could not spawn app-server", "".join(session.errors))

    def test_caller_cancel_sends_interrupt_and_preserves_server(self):
        session = self.session("cancel")
        session.call(id="call", token="progress")
        session.wait_frame("turn/started")
        logs = session.log()
        self.assertEqual([e["status"] for e in logs], ["pending"])
        self.assertTrue(logs[0]["threadId"])
        session.call({"prompt": "concurrent reply", "threadId": logs[0]["threadId"]}, name="codex-reply", id=9)
        self.assertIn("already has an active", session.receive(9)["result"]["content"][0]["text"])
        session.send("notifications/cancelled", {"requestId": "call", "reason": "test"})
        result = session.receive("call")["result"]
        self.assertTrue(result["isError"])
        self.assertEqual(result["structuredContent"]["turnStatus"], "interrupted")
        self.assertEqual(session.log()[-1]["status"], "cancelled")
        session.send("ping", {}, id=8)
        self.assertEqual(session.receive(8)["result"], {})
        session.stop()

    def test_eof_and_signals_reap_idle_child(self):
        for action in ["eof", signal.SIGTERM, signal.SIGINT]:
            with self.subTest(action=action):
                # No turn is needed to exercise teardown with a live native peer.
                session = self.session("initialize_only")
                pid = int(session.pidfile.read_text())
                if action == "eof":
                    session.proc.stdin.close()
                else:
                    session.proc.send_signal(action)
                session.proc.wait(timeout=WAIT)
                with self.assertRaises(ProcessLookupError):
                    os.kill(pid, 0)

    def test_eof_returns_inflight_error_before_exit(self):
        entries = transcript("cancel")
        offset = next(i for i, e in enumerate(entries) if e.get("frame", {}).get("method") == "turn/interrupt")
        session = self.session("cancel", entries=entries[:offset])
        session.call()
        session.wait_frame("turn/started")
        session.proc.stdin.close()
        self.assertTrue(session.receive(3)["result"]["isError"])
        session.stop()

    def test_progress_repeats_during_long_turn_and_frame_log_has_cli_version(self):
        entries = transcript("normal")
        # Delay completion by one heartbeat plus two polling quanta so a second
        # heartbeat must be sent while the scripted turn is still running.
        entries[-1]["afterMs"] = int((HEARTBEAT + POLL * 2) * 1000)
        session = self.session("normal", entries=entries)
        session.call(token=0)
        self.assertNotIn("isError", session.receive(3)["result"])
        progress = [m["params"] for m in session.messages if m.get("method") == "notifications/progress"]
        self.assertGreaterEqual(len(progress), 2)
        self.assertTrue(all(m["progressToken"] == 0 for m in progress))
        self.assertEqual([m["progress"] for m in progress], list(range(1, len(progress) + 1)))
        session.stop()
        frames = [json.loads(line) for line in session.frames.read_text().splitlines()]
        self.assertEqual(frames[0]["type"], "transcript_start")
        self.assertEqual(frames[0]["version"], "0.163.0")
        self.assertIn("expect_outbound", {e["type"] for e in frames})
        self.assertIn("emit_inbound", {e["type"] for e in frames})


class FixtureSchemaTests(unittest.TestCase):
    def test_every_kept_frame_matches_cli_01630_schema(self):
        catalog = json.loads((FIXTURES / "schema-catalog.json").read_text())["schemas"]
        results = dict(zip(
            ["initialize", "thread/start", "thread/resume", "thread/unarchive", "turn/start", "turn/interrupt",
             "item/commandExecution/requestApproval", "item/fileChange/requestApproval",
             "item/permissions/requestApproval", "item/tool/requestUserInput", "mcpServer/elicitation/request"],
            ["InitializeResponse", "ThreadStartResponse", "ThreadResumeResponse", "ThreadUnarchiveResponse", "TurnStartResponse", "TurnInterruptResponse",
             "CommandExecutionRequestApprovalResponse", "FileChangeRequestApprovalResponse", "PermissionsRequestApprovalResponse", "ToolRequestUserInputResponse", "McpServerElicitationRequestResponse"]))
        for path in sorted(FIXTURES.glob("*.ndjson")):
            pending = {}
            entries = transcript(path.stem)
            self.assertIn("Adapted from t3code (MIT, T3 Tools Inc.), commit defb7e6e,", entries[0]["metadata"]["attribution"])
            for number, e in enumerate(entries[1:], 2):
                with self.subTest(fixture=path.name, line=number):
                    if "frame" not in e:
                        continue
                    f = e["frame"]
                    if e.get("label") == "intentional malformed frame":
                        self.assertNotIsInstance(f, dict)
                        continue
                    direction = e["type"]
                    if "method" in f:
                        if "id" in f:
                            prefix = "client:" if direction == "expect_outbound" else "server:"
                            pending[(direction, f["id"])] = f["method"]
                        else:
                            prefix = "notification:"
                        validate(f, catalog[prefix + f["method"]])
                    elif "error" in f:
                        opposite = "emit_inbound" if direction == "expect_outbound" else "expect_outbound"
                        self.assertIn((opposite, f["id"]), pending)
                        pending.pop((opposite, f["id"]))
                        self.assertIsInstance(f["error"]["code"], int)
                        self.assertIsInstance(f["error"]["message"], str)
                    else:
                        opposite = "emit_inbound" if direction == "expect_outbound" else "expect_outbound"
                        method = pending.pop((opposite, f["id"]))
                        validate(f["result"], catalog["result:" + results[method]])


if __name__ == "__main__":
    unittest.main()
