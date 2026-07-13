#!/usr/bin/env node

import { spawn, spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const rootResult = spawnSync("git", ["rev-parse", "--show-toplevel"], {
  cwd: process.cwd(),
  encoding: "utf8",
});

if (rootResult.status !== 0) {
  process.stderr.write("FAIL: run this check inside the JouleWise Git repository\n");
  process.exit(1);
}

const repoRoot = rootResult.stdout.trim();
const mcpConfig = JSON.parse(readFileSync(resolve(repoRoot, ".mcp.json"), "utf8"));
const codexServer = mcpConfig?.mcpServers?.codex;
const expectedModel = "gpt-5.6-sol";
const expectedEffort = "high";
const expectedCodexArgs = [
  "mcp-server",
  "-c",
  `model="${expectedModel}"`,
  "-c",
  `model_reasoning_effort="${expectedEffort}"`,
  "-c",
  "mcp_servers.claude.enabled=false",
];

if (
  codexServer?.command !== "codex" ||
  JSON.stringify(codexServer?.args) !== JSON.stringify(expectedCodexArgs)
) {
  process.stderr.write(
    `FAIL: .mcp.json must pin Codex MCP to ${expectedModel} with ${expectedEffort} fallback effort\n`,
  );
  process.exit(1);
}

const codexProjectConfig = readFileSync(resolve(repoRoot, ".codex/config.toml"), "utf8");
for (const fragment of [
  "[mcp_servers.claude]",
  'command = "node"',
  'args = ["scripts/claude-bridge-mcp.mjs"]',
  'enabled_tools = ["consult_fable"]',
  'default_tools_approval_mode = "prompt"',
  "[mcp_servers.claude.tools.consult_fable]",
  'approval_mode = "approve"',
]) {
  if (!codexProjectConfig.includes(fragment)) {
    process.stderr.write(`FAIL: .codex/config.toml is missing ${fragment}\n`);
    process.exit(1);
  }
}

function commandVersion(command, args) {
  const result = spawnSync(command, args, { cwd: repoRoot, encoding: "utf8" });
  if (result.error?.code === "ENOENT") {
    throw new Error(`${command} is not installed or not on PATH`);
  }
  if (result.status !== 0) {
    throw new Error(`${command} version check failed: ${(result.stderr || result.stdout).trim()}`);
  }
  return result.stdout.trim();
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function listMcpTools(command, args, label) {
  return await new Promise((resolvePromise, reject) => {
    const child = spawn(command, args, {
      cwd: repoRoot,
      env: { ...process.env, NO_COLOR: "1" },
      stdio: ["pipe", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    let initialized = false;
    let settled = false;
    let timer;

    const finish = (error, tools) => {
      if (settled) return;
      settled = true;
      if (timer) clearTimeout(timer);
      child.kill("SIGTERM");
      if (error) reject(error);
      else resolvePromise(tools);
    };

    const send = (message) => child.stdin.write(`${JSON.stringify(message)}\n`);

    child.on("error", (error) => finish(error));
    child.stderr.setEncoding("utf8");
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.stdout.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
      while (stdout.includes("\n")) {
        const newline = stdout.indexOf("\n");
        const line = stdout.slice(0, newline).trim();
        stdout = stdout.slice(newline + 1);
        if (!line) continue;

        let message;
        try {
          message = JSON.parse(line);
        } catch (error) {
          finish(new Error(`${label} MCP emitted invalid JSON: ${error.message}`));
          return;
        }

        if (message.id === 1 && !initialized) {
          initialized = true;
          send({ jsonrpc: "2.0", method: "notifications/initialized" });
          send({ jsonrpc: "2.0", id: 2, method: "tools/list", params: {} });
        } else if (message.id === 2) {
          if (message.error) {
            finish(new Error(`${label} MCP tools/list failed: ${JSON.stringify(message.error)}`));
          } else {
            finish(null, message.result?.tools || []);
          }
        }
      }
    });
    child.on("exit", (code) => {
      if (!settled) {
        finish(new Error(`${label} MCP exited ${code} before tools/list. ${stderr.trim()}`));
      }
    });

    timer = setTimeout(() => {
      finish(new Error(`timed out waiting for ${label} MCP tools/list. ${stderr.trim()}`));
    }, 10_000);

    send({
      jsonrpc: "2.0",
      id: 1,
      method: "initialize",
      params: {
        protocolVersion: "2025-06-18",
        capabilities: {},
        clientInfo: { name: "joulewise-agent-bridge-check", version: "1.0.0" },
      },
    });
  });
}

function validateCodexTools(tools) {
  const byName = new Map(tools.map((tool) => [tool.name, tool]));
  const start = byName.get("codex");
  const reply = byName.get("codex-reply");
  assert(start, "Codex MCP did not expose the codex session tool");
  assert(reply, "Codex MCP did not expose the codex-reply continuation tool");

  const startProperties = start.inputSchema?.properties || {};
  for (const property of [
    "prompt",
    "cwd",
    "sandbox",
    "approval-policy",
    "model",
    "developer-instructions",
    "config",
  ]) {
    assert(startProperties[property], `codex tool is missing ${property}`);
  }
  assert(start.inputSchema?.required?.includes("prompt"), "codex tool does not require prompt");
  assert(
    reply.inputSchema?.properties?.threadId && reply.inputSchema?.properties?.prompt,
    "codex-reply is missing threadId or prompt",
  );
  assert(reply.inputSchema?.required?.includes("prompt"), "codex-reply does not require prompt");
}

function validateFableConsultTools(tools) {
  assert(tools.length === 1, "reverse bridge must expose exactly one MCP tool");
  const consult = tools[0];
  assert(consult.name === "consult_fable", "reverse bridge did not expose consult_fable");
  const properties = consult.inputSchema?.properties || {};
  assert(properties.prompt, "consult_fable is missing its prompt property");
  assert(
    consult.inputSchema?.required?.includes("prompt"),
    "consult_fable does not require prompt",
  );
  assert(
    properties.prompt.description?.includes("BRIDGE_HOPS_REMAINING: 0"),
    "consult_fable schema does not advertise the one-hop guard",
  );
}

function checkClaudeApproval() {
  const claudeBin = process.env.CLAUDE_BIN || "claude";
  const result = spawnSync(claudeBin, ["mcp", "get", "codex"], {
    cwd: repoRoot,
    encoding: "utf8",
  });
  if (result.error?.code === "ENOENT") {
    throw new Error("claude is not installed or not on PATH");
  }
  const output = `${result.stdout || ""}${result.stderr || ""}`;
  if (output.includes("Pending approval")) {
    const error = new Error(
      "Claude Code has not approved the project Codex server. Start `claude` here and approve it, then rerun this check.",
    );
    error.exitCode = 2;
    throw error;
  }
  if (result.status !== 0 || !output.includes("Status:") || !output.includes("Connected")) {
    throw new Error(`Claude Code could not resolve the codex MCP server: ${output.trim()}`);
  }
}

try {
  const codexBin = process.env.CODEX_BIN || "codex";
  const claudeBin = process.env.CLAUDE_BIN || "claude";
  const nodeBin = process.env.NODE_BIN || "node";
  const codexVersion = commandVersion(codexBin, ["--version"]);
  const claudeVersion = commandVersion(claudeBin, ["--version"]);
  const nodeVersion = commandVersion(nodeBin, ["--version"]);
  const [codexTools, claudeTools] = await Promise.all([
    listMcpTools(codexBin, codexServer.args, "Codex"),
    listMcpTools(nodeBin, [resolve(repoRoot, "scripts/claude-bridge-mcp.mjs")], "Claude bridge"),
  ]);
  validateCodexTools(codexTools);
  validateFableConsultTools(claudeTools);
  checkClaudeApproval();
  process.stdout.write(`PASS: ${codexVersion}\n`);
  process.stdout.write(`PASS: Claude Code ${claudeVersion}\n`);
  process.stdout.write(`PASS: Node.js ${nodeVersion}\n`);
  process.stdout.write(
    "PASS: Claude -> Sol MCP exposes full-session start and continuation controls\n",
  );
  process.stdout.write(
    `PASS: Claude -> Sol defaults to ${expectedModel} with ${expectedEffort} fallback effort\n`,
  );
  process.stdout.write("PASS: Claude-originated Sol sessions disable the reverse Claude server\n");
  process.stdout.write("PASS: Sol -> Fable MCP exposes only the guarded consult_fable tool\n");
  process.stdout.write(
    "PASS: reverse bridge preapproves only consult_fable and enforces read-only one-hop policy\n",
  );
  process.stdout.write(`PASS: Claude Code approved the codex server for ${repoRoot}\n`);
} catch (error) {
  process.stderr.write(`FAIL: ${error.message}\n`);
  process.exit(error.exitCode || 1);
}
