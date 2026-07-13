"""Focused checks for the read-only Codex -> Claude Fable MCP bridge."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[1]
BRIDGE = REPO_ROOT / "scripts" / "claude-bridge-mcp.mjs"


class ClaudeBridgeMcpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.node = shutil.which("node")
        if cls.node is None:
            raise unittest.SkipTest("node is required for the Claude bridge MCP checks")

    def exchange(self, messages: list[dict], env: dict[str, str] | None = None) -> list[dict]:
        payload = "".join(json.dumps(message) + "\n" for message in messages)
        result = subprocess.run(
            [self.node, str(BRIDGE)],
            cwd=REPO_ROOT,
            env={**os.environ, **(env or {})},
            input=payload,
            text=True,
            capture_output=True,
            timeout=15,
            check=True,
        )
        return [json.loads(line) for line in result.stdout.splitlines() if line.strip()]

    def assert_failed_envelope(
        self,
        result: dict,
        flag: str = "protocol_failure",
        effort: str | None = None,
    ) -> dict:
        self.assertTrue(result["isError"])
        lines = result["content"][0]["text"].splitlines()
        if effort is not None:
            self.assertEqual(lines.pop(0), f"[consult effort: {effort}]")
        self.assertEqual(lines[0], "BRIDGE_REPORT_V1")
        self.assertEqual(len(lines), 2)
        report = json.loads(lines[1])
        self.assertEqual(report["status"], "FAILED")
        self.assertEqual(report["flags"], [flag])
        return report

    def test_exposes_only_guarded_fable_consult(self) -> None:
        replies = self.exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "1"},
                    },
                },
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            ]
        )
        tools = next(reply["result"]["tools"] for reply in replies if reply.get("id") == 2)
        self.assertEqual([tool["name"] for tool in tools], ["consult_fable"])
        self.assertEqual(tools[0]["inputSchema"]["required"], ["prompt"])
        self.assertEqual(tools[0]["inputSchema"]["properties"]["effort"]["enum"], ["high", "xhigh"])

    def test_rejects_missing_one_hop_guard_without_starting_claude(self) -> None:
        replies = self.exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {"name": "consult_fable", "arguments": {"prompt": "review this"}},
                }
            ],
            {"CLAUDE_BIN": "/definitely/not/claude"},
        )
        result = replies[0]["result"]
        report = self.assert_failed_envelope(result)
        self.assertIn("exactly one BRIDGE_ORIGIN", report["summary"])

    def test_rejects_claude_origin_without_starting_claude(self) -> None:
        prompt = "BRIDGE_ORIGIN: claude\nBRIDGE_HOPS_REMAINING: 0\nreview this"
        replies = self.exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 5,
                    "method": "tools/call",
                    "params": {"name": "consult_fable", "arguments": {"prompt": prompt}},
                }
            ],
            {"CLAUDE_BIN": "/definitely/not/claude"},
        )
        result = replies[0]["result"]
        report = self.assert_failed_envelope(result)
        self.assertIn("Claude-originated", report["summary"])

    def test_rejects_duplicate_bridge_headers_without_starting_claude(self) -> None:
        prompt = (
            "BRIDGE_ORIGIN: codex\n"
            "BRIDGE_HOPS_REMAINING: 0\n"
            "BRIDGE_ORIGIN: codex\n"
            "review this"
        )
        replies = self.exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 6,
                    "method": "tools/call",
                    "params": {"name": "consult_fable", "arguments": {"prompt": prompt}},
                }
            ],
            {"CLAUDE_BIN": "/definitely/not/claude"},
        )
        result = replies[0]["result"]
        report = self.assert_failed_envelope(result)
        self.assertIn("exactly one", report["summary"])

    def test_rejects_nonzero_hops_with_failed_envelope(self) -> None:
        prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 1\nreview this"
        replies = self.exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 9,
                    "method": "tools/call",
                    "params": {"name": "consult_fable", "arguments": {"prompt": prompt}},
                }
            ],
            {"CLAUDE_BIN": "/definitely/not/claude"},
        )
        report = self.assert_failed_envelope(replies[0]["result"])
        self.assertIn("BRIDGE_HOPS_REMAINING: 0", report["summary"])

    def test_strips_caller_headers_and_injects_one_canonical_guarded_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_claude = tmp_path / "fake-claude"
            args_log = tmp_path / "args.json"
            fake_claude.write_text(
                f"#!{sys.executable}\n"
                "import json, os, pathlib, sys\n"
                "pathlib.Path(os.environ['CLAUDE_ARGS_LOG']).write_text(json.dumps(sys.argv[1:]))\n"
                "print('JOULEWISE_FAKE_FABLE_OK')\n"
                "print('BRIDGE_REPORT_V1')\n"
                "print(json.dumps({'status':'DISCUSSION','summary':'reviewed','pathspec':[],"
                "'verification':[],'flags':[]}, separators=(',', ':')))\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            prompt = (
                "BRIDGE_ORIGIN: codex\n"
                "BRIDGE_HOPS_REMAINING: 0\n"
                "Return the bridge token."
            )
            replies = self.exchange(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 4,
                        "method": "tools/call",
                        "params": {"name": "consult_fable", "arguments": {"prompt": prompt}},
                    }
                ],
                {
                    "CLAUDE_BIN": str(fake_claude),
                    "CLAUDE_ARGS_LOG": str(args_log),
                    "CLAUDE_BRIDGE_TIMEOUT_MS": "5000",
                },
            )
            output = replies[0]["result"]["content"][0]["text"]
            self.assertTrue(output.startswith("[consult effort: high]\nJOULEWISE_FAKE_FABLE_OK\n"))
            self.assertTrue(output.endswith('"verification":[],"flags":[]}'))
            args = json.loads(args_log.read_text(encoding="utf-8"))
            self.assertIn("fable", args)
            self.assertIn("high", args)
            self.assertIn("plan", args)
            self.assertIn("Read,Grep,Glob", args)
            self.assertIn("--disable-slash-commands", args)
            self.assertIn("--strict-mcp-config", args)
            self.assertIn('{"mcpServers":{}}', args)
            self.assertIn("--no-session-persistence", args)
            self.assertNotIn("Agent", args)
            spawned_prompt = args[-1]
            self.assertTrue(
                spawned_prompt.startswith("BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\n")
            )
            self.assertEqual(spawned_prompt.count("BRIDGE_ORIGIN: codex"), 1)
            self.assertEqual(spawned_prompt.count("BRIDGE_HOPS_REMAINING: 0"), 1)
            self.assertIn("Return the bridge token.", spawned_prompt)

    def test_explicit_xhigh_effort_is_honored_and_echoed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_claude = tmp_path / "fake-claude"
            args_log = tmp_path / "args.json"
            fake_claude.write_text(
                f"#!{sys.executable}\n"
                "import json, os, pathlib, sys\n"
                "pathlib.Path(os.environ['CLAUDE_ARGS_LOG']).write_text(json.dumps(sys.argv[1:]))\n"
                "print('BRIDGE_REPORT_V1')\n"
                "print(json.dumps({'status':'DISCUSSION','summary':'reviewed','pathspec':[],"
                "'verification':[],'flags':[]}))\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
            replies = self.exchange(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 13,
                        "method": "tools/call",
                        "params": {
                            "name": "consult_fable",
                            "arguments": {"prompt": prompt, "effort": "xhigh"},
                        },
                    }
                ],
                {"CLAUDE_BIN": str(fake_claude), "CLAUDE_ARGS_LOG": str(args_log)},
            )
            result = replies[0]["result"]
            self.assertNotIn("isError", result)
            self.assertTrue(result["content"][0]["text"].startswith("[consult effort: xhigh]\n"))
            args = json.loads(args_log.read_text(encoding="utf-8"))
            self.assertEqual(args[args.index("--effort") + 1], "xhigh")

    def test_validated_environment_effort_default_is_respected(self) -> None:
        for configured, expected in (("xhigh", "xhigh"), ("invalid", "high")):
            with self.subTest(configured=configured), tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                fake_claude = tmp_path / "fake-claude"
                args_log = tmp_path / "args.json"
                fake_claude.write_text(
                    f"#!{sys.executable}\n"
                    "import json, os, pathlib, sys\n"
                    "pathlib.Path(os.environ['CLAUDE_ARGS_LOG']).write_text(json.dumps(sys.argv[1:]))\n"
                    "print('BRIDGE_REPORT_V1')\n"
                    "print(json.dumps({'status':'DISCUSSION','summary':'reviewed','pathspec':[],"
                    "'verification':[],'flags':[]}))\n",
                    encoding="utf-8",
                )
                fake_claude.chmod(0o755)
                prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
                replies = self.exchange(
                    [
                        {
                            "jsonrpc": "2.0",
                            "id": 14,
                            "method": "tools/call",
                            "params": {
                                "name": "consult_fable",
                                "arguments": {"prompt": prompt},
                            },
                        }
                    ],
                    {
                        "CLAUDE_BIN": str(fake_claude),
                        "CLAUDE_ARGS_LOG": str(args_log),
                        "CLAUDE_BRIDGE_EFFORT": configured,
                    },
                )
                output = replies[0]["result"]["content"][0]["text"]
                self.assertTrue(output.startswith(f"[consult effort: {expected}]\n"))
                args = json.loads(args_log.read_text(encoding="utf-8"))
                self.assertEqual(args[args.index("--effort") + 1], expected)

    def test_invalid_effort_is_protocol_failure_without_starting_claude(self) -> None:
        prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
        replies = self.exchange(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 15,
                    "method": "tools/call",
                    "params": {
                        "name": "consult_fable",
                        "arguments": {"prompt": prompt, "effort": "ultra"},
                    },
                }
            ],
            {"CLAUDE_BIN": "/definitely/not/claude"},
        )
        report = self.assert_failed_envelope(replies[0]["result"])
        self.assertIn("high, xhigh", report["summary"])

    def test_accepts_spaced_single_line_envelope_with_additional_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_claude = Path(tmp) / "fake-claude"
            fake_claude.write_text(
                f"#!{sys.executable}\n"
                "print('advice')\n"
                "print('BRIDGE_REPORT_V1')\n"
                "print('{\"status\": \"DISCUSSION\", \"summary\": \"reviewed\", "
                "\"pathspec\": [], \"verification\": [], \"flags\": [], \"future\": 1}')\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
            replies = self.exchange(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 16,
                        "method": "tools/call",
                        "params": {"name": "consult_fable", "arguments": {"prompt": prompt}},
                    }
                ],
                {"CLAUDE_BIN": str(fake_claude)},
            )
            result = replies[0]["result"]
            self.assertNotIn("isError", result)
            self.assertIn('"future": 1', result["content"][0]["text"])

    def test_rejects_malformed_or_nonfinal_child_envelopes(self) -> None:
        valid = json.dumps(
            {
                "status": "DISCUSSION",
                "summary": "reviewed",
                "pathspec": [],
                "verification": [],
                "flags": [],
            }
        )
        cases = {
            "missing_required": "BRIDGE_REPORT_V1\n"
            + json.dumps(
                {
                    "status": "DISCUSSION",
                    "summary": "reviewed",
                    "pathspec": [],
                    "verification": [],
                }
            )
            + "\n",
            "bad_status": "BRIDGE_REPORT_V1\n"
            + json.dumps(
                {
                    "status": "BOGUS",
                    "summary": "reviewed",
                    "pathspec": [],
                    "verification": [],
                    "flags": [],
                }
            )
            + "\n",
            "nonempty_pathspec": "BRIDGE_REPORT_V1\n"
            + json.dumps(
                {
                    "status": "DISCUSSION",
                    "summary": "reviewed",
                    "pathspec": ["file.txt"],
                    "verification": [],
                    "flags": [],
                }
            )
            + "\n",
            "sentinel_not_final": f"BRIDGE_REPORT_V1\n{valid}\ntrailing\n",
            "duplicated_sentinel": f"BRIDGE_REPORT_V1\n{valid}\nBRIDGE_REPORT_V1\n{valid}\n",
        }
        for name, child_output in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                fake_claude = Path(tmp) / "fake-claude"
                fake_claude.write_text(
                    f"#!{sys.executable}\nimport sys\nsys.stdout.write({child_output!r})\n",
                    encoding="utf-8",
                )
                fake_claude.chmod(0o755)
                prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
                replies = self.exchange(
                    [
                        {
                            "jsonrpc": "2.0",
                            "id": 17,
                            "method": "tools/call",
                            "params": {
                                "name": "consult_fable",
                                "arguments": {"prompt": prompt},
                            },
                        }
                    ],
                    {"CLAUDE_BIN": str(fake_claude)},
                )
                self.assert_failed_envelope(replies[0]["result"], effort="high")

    def test_nonzero_claude_exit_synthesizes_failed_bridge_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_claude = Path(tmp) / "fake-claude"
            fake_claude.write_text(
                f"#!{sys.executable}\n"
                "import sys\n"
                "print('raw child failure must not escape', file=sys.stderr)\n"
                "raise SystemExit(7)\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
            replies = self.exchange(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 7,
                        "method": "tools/call",
                        "params": {"name": "consult_fable", "arguments": {"prompt": prompt}},
                    }
                ],
                {"CLAUDE_BIN": str(fake_claude)},
            )
            result = replies[0]["result"]
            report = self.assert_failed_envelope(result, "transport_failure", "high")
            self.assertEqual(report["status"], "FAILED")
            self.assertIn("raw child failure must not escape", report["summary"])

    def test_missing_worker_envelope_synthesizes_protocol_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_claude = Path(tmp) / "fake-claude"
            fake_claude.write_text(
                f"#!{sys.executable}\nprint('advice without envelope')\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
            replies = self.exchange(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 8,
                        "method": "tools/call",
                        "params": {"name": "consult_fable", "arguments": {"prompt": prompt}},
                    }
                ],
                {"CLAUDE_BIN": str(fake_claude)},
            )
            self.assert_failed_envelope(replies[0]["result"], effort="high")

    def test_empty_worker_output_synthesizes_protocol_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_claude = Path(tmp) / "fake-claude"
            fake_claude.write_text(f"#!{sys.executable}\n", encoding="utf-8")
            fake_claude.chmod(0o755)
            prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
            replies = self.exchange(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 10,
                        "method": "tools/call",
                        "params": {"name": "consult_fable", "arguments": {"prompt": prompt}},
                    }
                ],
                {"CLAUDE_BIN": str(fake_claude)},
            )
            self.assert_failed_envelope(replies[0]["result"], effort="high")

    def test_needs_ruling_worker_status_is_accepted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake_claude = Path(tmp) / "fake-claude"
            fake_claude.write_text(
                f"#!{sys.executable}\n"
                "import json\n"
                "print('Question: choose A or B')\n"
                "print('BRIDGE_REPORT_V1')\n"
                "print(json.dumps({'status':'NEEDS_RULING','summary':'choice needed',"
                "'pathspec':[],'verification':[],'flags':[]}, separators=(',', ':')))\n",
                encoding="utf-8",
            )
            fake_claude.chmod(0o755)
            prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
            replies = self.exchange(
                [
                    {
                        "jsonrpc": "2.0",
                        "id": 11,
                        "method": "tools/call",
                        "params": {"name": "consult_fable", "arguments": {"prompt": prompt}},
                    }
                ],
                {"CLAUDE_BIN": str(fake_claude)},
            )
            result = replies[0]["result"]
            self.assertNotIn("isError", result)
            self.assertTrue(result["content"][0]["text"].startswith("[consult effort: high]\n"))
            self.assertIn('"status":"NEEDS_RULING"', result["content"][0]["text"])

    def test_other_successful_worker_statuses_synthesize_one_deviation_envelope(self) -> None:
        for status in ("DONE", "PARTIAL", "NEEDS_SCOPE", "BLOCKED", "FAILED"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as tmp:
                fake_claude = Path(tmp) / "fake-claude"
                fake_claude.write_text(
                    f"#!{sys.executable}\n"
                    "import json\n"
                    "print('bounded advisory text')\n"
                    "print('BRIDGE_REPORT_V1')\n"
                    f"print(json.dumps({{'status':'{status}','summary':'child status',"
                    "'pathspec':[],'verification':[],'flags':[]}, separators=(',', ':')))\n",
                    encoding="utf-8",
                )
                fake_claude.chmod(0o755)
                prompt = "BRIDGE_ORIGIN: codex\nBRIDGE_HOPS_REMAINING: 0\nReview this."
                replies = self.exchange(
                    [
                        {
                            "jsonrpc": "2.0",
                            "id": 12,
                            "method": "tools/call",
                            "params": {
                                "name": "consult_fable",
                                "arguments": {"prompt": prompt},
                            },
                        }
                    ],
                    {"CLAUDE_BIN": str(fake_claude)},
                )
                result = replies[0]["result"]
                self.assertTrue(result["isError"])
                output = result["content"][0]["text"]
                self.assertTrue(
                    output.startswith("[consult effort: high]\nbounded advisory text\n")
                )
                self.assertEqual(output.count("BRIDGE_REPORT_V1"), 1)
                self.assertIn(f"child claimed status {status}", output)
                failed = json.loads(output.splitlines()[-1])
                self.assertEqual(failed["status"], "FAILED")
                self.assertEqual(failed["flags"], ["protocol_deviation"])


if __name__ == "__main__":
    unittest.main()
