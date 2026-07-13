#!/usr/bin/env node

import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
import readline from "node:readline";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const claudeBin = process.env.CLAUDE_BIN || "claude";
const requestedTimeoutMs = Number.parseInt(
  process.env.CLAUDE_BRIDGE_TIMEOUT_MS || "600000",
  10,
);
const timeoutMs = Number.isFinite(requestedTimeoutMs) && requestedTimeoutMs > 0
  ? requestedTimeoutMs
  : 600_000;
const maxOutputCharacters = 1_000_000;

const consultTool = {
  name: "consult_fable",
  description:
    "Ask Claude Fable for one bounded, read-only peer judgment. The caller remains lead.",
  inputSchema: {
    $schema: "https://json-schema.org/draft/2020-12/schema",
    type: "object",
    properties: {
      prompt: {
        type: "string",
        minLength: 1,
        maxLength: 100_000,
        description:
          "A self-contained consult prompt beginning with BRIDGE_ORIGIN: codex and BRIDGE_HOPS_REMAINING: 0.",
      },
    },
    required: ["prompt"],
    additionalProperties: false,
  },
};

function send(message) {
  process.stdout.write(`${JSON.stringify(message)}\n`);
}

function resultText(text, isError = false) {
  return { content: [{ type: "text", text }], ...(isError ? { isError: true } : {}) };
}

function bridgePrompt(prompt) {
  return [
    "BRIDGE_ORIGIN: codex",
    "BRIDGE_HOPS_REMAINING: 0",
    "You are a read-only Fable peer consultant to a top-level Codex lead.",
    "Do not edit files, invoke Codex or Sol, use MCP, run shell commands, start agents, or delegate.",
    "Return concise findings, reasoning, risks, and a recommendation. The caller owns the decision.",
    "",
    prompt,
  ].join("\n");
}

async function consultFable(prompt) {
  if (typeof prompt !== "string" || !prompt.trim()) {
    return resultText("prompt must be a non-empty string", true);
  }
  if (prompt.length > 100_000) {
    return resultText("prompt exceeds the 100000-character bridge limit", true);
  }
  if (/^BRIDGE_ORIGIN:\s*claude\s*$/m.test(prompt)) {
    return resultText("a Claude-originated Sol session cannot call the reverse bridge", true);
  }
  if (!/^BRIDGE_ORIGIN:\s*codex\s*$/m.test(prompt)) {
    return resultText("reverse bridge requires BRIDGE_ORIGIN: codex", true);
  }
  if (!/^BRIDGE_HOPS_REMAINING:\s*0\s*$/m.test(prompt)) {
    return resultText("reverse bridge requires BRIDGE_HOPS_REMAINING: 0", true);
  }

  const emptyMcpConfig = '{"mcpServers":{}}';
  const args = [
    "-p",
    "--model",
    "fable",
    "--effort",
    "high",
    "--permission-mode",
    "plan",
    "--tools",
    "Read,Grep,Glob",
    "--disable-slash-commands",
    "--strict-mcp-config",
    "--mcp-config",
    emptyMcpConfig,
    "--no-session-persistence",
    "--output-format",
    "text",
    bridgePrompt(prompt),
  ];

  return await new Promise((resolvePromise) => {
    const child = spawn(claudeBin, args, {
      cwd: repoRoot,
      env: { ...process.env, NO_COLOR: "1" },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    let settled = false;
    let timer;

    const finish = (result) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolvePromise(result);
    };

    const appendBounded = (current, chunk) => {
      const combined = current + chunk;
      return combined.length > maxOutputCharacters
        ? combined.slice(combined.length - maxOutputCharacters)
        : combined;
    };

    child.stdout.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      stdout = appendBounded(stdout, chunk);
    });
    child.stderr.setEncoding("utf8");
    child.stderr.on("data", (chunk) => {
      stderr = appendBounded(stderr, chunk);
    });
    child.on("error", (error) => {
      finish(resultText(`could not start Claude Code: ${error.message}`, true));
    });
    child.on("close", (code, signal) => {
      if (code === 0 && stdout.trim()) {
        finish(resultText(stdout.trim()));
        return;
      }
      const detail = stderr.trim() || stdout.trim() || `signal ${signal || "unknown"}`;
      finish(resultText(`Claude Fable consult failed (exit ${code}): ${detail}`, true));
    });

    timer = setTimeout(() => {
      child.kill("SIGTERM");
      finish(resultText(`Claude Fable consult timed out after ${timeoutMs} ms`, true));
    }, timeoutMs);
  });
}

async function handle(message) {
  if (!message || message.jsonrpc !== "2.0") return;
  if (message.method === "notifications/initialized") return;
  if (message.method === "notifications/cancelled") return;

  if (message.method === "initialize") {
    send({
      jsonrpc: "2.0",
      id: message.id,
      result: {
        protocolVersion: message.params?.protocolVersion || "2025-06-18",
        capabilities: { tools: { listChanged: false } },
        serverInfo: { name: "joulewise-claude-bridge", version: "1.0.0" },
      },
    });
    return;
  }

  if (message.method === "tools/list") {
    send({ jsonrpc: "2.0", id: message.id, result: { tools: [consultTool] } });
    return;
  }

  if (message.method === "tools/call") {
    if (message.params?.name !== consultTool.name) {
      send({
        jsonrpc: "2.0",
        id: message.id,
        error: { code: -32601, message: `unknown tool: ${message.params?.name || ""}` },
      });
      return;
    }
    const result = await consultFable(message.params?.arguments?.prompt);
    send({ jsonrpc: "2.0", id: message.id, result });
    return;
  }

  if (message.method === "ping") {
    send({ jsonrpc: "2.0", id: message.id, result: {} });
    return;
  }

  if (message.id !== undefined) {
    send({
      jsonrpc: "2.0",
      id: message.id,
      error: { code: -32601, message: `method not found: ${message.method || ""}` },
    });
  }
}

const input = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
input.on("line", (line) => {
  if (!line.trim()) return;
  try {
    void handle(JSON.parse(line));
  } catch (error) {
    send({ jsonrpc: "2.0", id: null, error: { code: -32700, message: error.message } });
  }
});
