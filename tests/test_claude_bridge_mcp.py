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
        self.assertTrue(result["isError"])
        self.assertIn("BRIDGE_ORIGIN: codex", result["content"][0]["text"])

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
        self.assertTrue(result["isError"])
        self.assertIn("Claude-originated", result["content"][0]["text"])

    def test_invokes_fable_with_no_write_or_delegation_tools(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fake_claude = tmp_path / "fake-claude"
            args_log = tmp_path / "args.json"
            fake_claude.write_text(
                f"#!{sys.executable}\n"
                "import json, os, pathlib, sys\n"
                "pathlib.Path(os.environ['CLAUDE_ARGS_LOG']).write_text(json.dumps(sys.argv[1:]))\n"
                "print('JOULEWISE_FAKE_FABLE_OK')\n",
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
            self.assertEqual(replies[0]["result"]["content"][0]["text"], "JOULEWISE_FAKE_FABLE_OK")
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
            self.assertIn("BRIDGE_HOPS_REMAINING: 0", args[-1])


if __name__ == "__main__":
    unittest.main()
