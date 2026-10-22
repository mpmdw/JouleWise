#!/usr/bin/env node
// Connection/configuration checks spend no model turns unless --live is given.
import { spawn, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { resolve } from "node:path";
import readline from "node:readline";

// Match the adapter's control-RPC budget: three times T3's 10-second bound.
// The optional live turn gets 20 budgets (10 minutes); cleanup gets 1/10.
const CONTROL_MS = 30_000;
const LIVE_MS = CONTROL_MS * 20;
const REAP_MS = CONTROL_MS / 10;
const rootResult = spawnSync("git", ["rev-parse", "--show-toplevel"], { encoding: "utf8" });
if (rootResult.status !== 0) {
  process.stderr.write("FAIL: run this check inside the JouleWise Git repository\n");
  process.exit(1);
}
const repoRoot = rootResult.stdout.trim();
const codexServer = JSON.parse(readFileSync(resolve(repoRoot, ".mcp.json"), "utf8"))?.mcpServers?.codex;
const assert = (condition, message) => { if (!condition) throw new Error(message); };
const pass = (message) => process.stdout.write(`PASS: ${message}\n`);

function command(command, args) {
  const result = spawnSync(command, args, { cwd: repoRoot, encoding: "utf8", timeout: CONTROL_MS });
  if (result.error) throw new Error(`${command}: ${result.error.message}`);
  assert(result.status === 0, `${command} ${args.join(" ")} failed: ${(result.stderr || result.stdout).trim()}`);
  return result.stdout.trim();
}

function connect(commandName, args, { cwd = repoRoot, env = {} } = {}) {
  const child = spawn(commandName, args, { cwd, env: { ...process.env, NO_COLOR: "1", ...env }, stdio: ["pipe", "pipe", "pipe"] });
  let nextId = 1, stderr = "", closed = false, failure;
  const pending = new Map();
  function fail(error) {
    failure = error;
    for (const p of pending.values()) { clearTimeout(p.timer); p.reject(error); }
    pending.clear();
  }
  child.on("error", fail);
  child.stdin.on("error", fail);
  child.stderr.on("data", (chunk) => { stderr = (stderr + chunk).slice(-16_384); });
  const input = readline.createInterface({ input: child.stdout });
  input.on("line", (line) => {
    try {
      const frame = JSON.parse(line);
      if (!("id" in frame)) return;
      const p = pending.get(frame.id);
      if (!p) return;
      pending.delete(frame.id);
      clearTimeout(p.timer);
      if (frame.error) p.reject(new Error(frame.error.message));
      else p.resolve(frame.result);
    } catch (error) { fail(error); }
  });
  child.on("exit", (code, signal) => fail(new Error(`MCP exited ${signal ?? code}: ${stderr.trim()}`)));
  child.on("close", () => { closed = true; });
  function send(frame) { child.stdin.write(`${JSON.stringify({ jsonrpc: "2.0", ...frame })}\n`); }
  return {
    request(method, params = {}, timeout = CONTROL_MS) {
      return new Promise((res, rej) => {
        if (failure) { rej(failure); return; }
        const id = nextId++;
        const timer = setTimeout(() => { pending.delete(id); rej(new Error(`${method} timed out: ${stderr.trim()}`)); }, timeout);
        pending.set(id, { resolve: res, reject: rej, timer });
        send({ id, method, params });
      });
    },
    async initialize() {
      const result = await this.request("initialize", {
        protocolVersion: "2025-06-18", capabilities: {},
        clientInfo: { name: "joulewise-agent-bridge-check", version: "2.0.0" },
      });
      send({ method: "notifications/initialized" });
      return result;
    },
    async close() {
      const status = await new Promise((done) => {
        if (closed) { done(child.exitCode); return; }
        const kill = setTimeout(() => child.kill("SIGKILL"), REAP_MS);
        child.once("close", (code) => { clearTimeout(kill); done(code); });
        child.stdin.end();
      });
      assert(!stderr.includes("REPLAY ERROR"), stderr);
      assert(status === 0, `MCP teardown failed (${status}): ${stderr.trim()}`);
    },
  };
}

async function withClient(commandName, args, options, run) {
  const client = connect(commandName, args, options);
  try { return await run(client, await client.initialize()); }
  finally { await client.close(); }
}

function validateCodexTools(tools) {
  assert(tools.length === 2, "Codex MCP must expose exactly two tools");
  const byName = new Map(tools.map((tool) => [tool.name, tool]));
  const start = byName.get("codex"), reply = byName.get("codex-reply");
  assert(start && reply, "Codex MCP is missing codex or codex-reply");
  const expected = ["prompt", "cwd", "sandbox", "approval-policy", "model", "base-instructions", "compact-prompt", "developer-instructions", "config"];
  assert(JSON.stringify(Object.keys(start.inputSchema.properties).sort()) === JSON.stringify(expected.sort()), "codex start schema changed");
  assert(start.inputSchema.required.includes("prompt"), "codex must require prompt");
  assert(reply.inputSchema.properties.threadId && reply.inputSchema.properties.conversationId && reply.inputSchema.properties.prompt, "codex-reply schema changed");
}

function checkReverseConfig() {
  const config = readFileSync(resolve(repoRoot, ".codex/config.toml"), "utf8");
  for (const fragment of ["[mcp_servers.claude]", 'command = "node"', 'args = ["scripts/claude-bridge-mcp.mjs"]',
    'enabled_tools = ["consult_fable"]', 'default_tools_approval_mode = "prompt"',
    "[mcp_servers.claude.tools.consult_fable]", 'approval_mode = "approve"']) {
    assert(config.includes(fragment), `.codex/config.toml missing ${fragment}`);
  }
}

function checkClaudeApproval(claudeBin) {
  const output = command(claudeBin, ["mcp", "get", "codex"]);
  if (output.includes("Pending approval")) {
    throw Object.assign(new Error("Claude Code has not approved the project Codex server; approve the tracked server in Claude Code and rerun."), { exitCode: 2 });
  }
  assert(output.includes("Status:") && output.includes("Connected"), `Claude Code could not resolve codex: ${output}`);
}

let scratch;
try {
  assert(process.argv.slice(2).every((arg) => arg === "--live"), "usage: scripts/check-codex-mcp.mjs [--live]");
  assert(codexServer?.command === "node" && JSON.stringify(codexServer.args) === JSON.stringify(["scripts/codex-mcp-server.mjs"]), ".mcp.json must run node scripts/codex-mcp-server.mjs");
  assert(!codexServer.env?.CODEX_MCP_FRAME_LOG, "frame logging must be off in .mcp.json");
  const codexBin = process.env.CODEX_BIN || "codex";
  const claudeBin = process.env.CLAUDE_BIN || "claude";
  const nodeBin = process.env.NODE_BIN || "node";
  const codexVersion = command(codexBin, ["--version"]);
  const claudeVersion = command(claudeBin, ["--version"]);
  const nodeVersion = command(nodeBin, ["--version"]);
  const help = command(codexBin, ["app-server", "--help"]);
  assert(help.includes("generate-json-schema"), "installed Codex CLI does not have app-server");
  checkReverseConfig();
  pass(`CLI ${codexVersion} has app-server; Claude Code ${claudeVersion}; Node.js ${nodeVersion}`);
  await withClient(codexServer.command, codexServer.args, {}, async (client, initialized) => {
    assert(initialized.serverInfo.name === "codex", "wrong MCP server name");
    validateCodexTools((await client.request("tools/list")).tools);
    pass("project Codex MCP starts and exposes compatible codex / codex-reply schemas");
    for (const args of [{ model: "gpt-5.6-sol" }, { sandbox: "danger-full-access" }, { "approval-policy": "never" }]) {
      const result = await client.request("tools/call", { name: "codex", arguments: { prompt: "Refusal check; never run a turn.", ...args } });
      assert(result.isError && result.structuredContent.threadId === null, `unsafe input was not refused before thread start: ${JSON.stringify(args)}`);
    }
    pass("wrong model, danger-full-access, and removed approvals are refused before thread start");
    if (process.argv.includes("--live")) {
      const started = await client.request("tools/call", {
        name: "codex", arguments: { prompt: "Reply with exactly CODEX_MCP_LIVE_OK. Do not use tools.", cwd: repoRoot,
          model: "gpt-6.1-sol", sandbox: "read-only", "approval-policy": "on-request", config: { model_reasoning_effort: "high" } },
        _meta: { progressToken: "live-smoke" },
      }, LIVE_MS);
      assert(!started.isError && started.content[0]?.text.trim() === "CODEX_MCP_LIVE_OK", `live turn failed: ${JSON.stringify(started)}`);
      assert(started.structuredContent.model === "gpt-6.1-sol" && started.structuredContent.reasoningEffort === "high", "live readback differs from required selection");
      pass(`optional live round trip returned CODEX_MCP_LIVE_OK, thread ${started.structuredContent.threadId}`);
    }
  });
  // Verify real thread params against a transcript peer, spending no live turn.
  scratch = mkdtempSync(resolve(tmpdir(), "codex-mcp-check-"));
  const fixture = resolve(repoRoot, "tests/fixtures/codex_app_server/normal.ndjson");
  const header = JSON.parse(readFileSync(fixture, "utf8").split("\n")[0]);
  const frameLog = resolve(scratch, "frames.ndjson");
  await withClient(nodeBin, [resolve(repoRoot, "scripts/codex-mcp-server.mjs")], {
    cwd: scratch, env: { CODEX_BIN: resolve(repoRoot, "tests/fixtures/codex_app_server/replay_peer.mjs"),
      CODEX_REPLAY_TRANSCRIPT: fixture, CODEX_MCP_FRAME_LOG: frameLog },
  }, async (client) => {
    const result = await client.request("tools/call", { name: "codex", arguments: {
      ...header.metadata.arguments, config: { mcp_servers: { claude: { enabled: true } } },
    } });
    assert(!result.isError, `one-hop replay failed: ${JSON.stringify(result)}`);
    const frames = readFileSync(frameLog, "utf8").trim().split("\n").map(JSON.parse);
    const start = frames.find((e) => e.type === "expect_outbound" && e.frame.method === "thread/start");
    assert(start?.frame.params.config["mcp_servers.claude.enabled"] === false, "reverse Claude server was not forcibly disabled");
  });
  pass("recorded replay verifies forced one-hop config despite caller override");
  await withClient(nodeBin, [resolve(repoRoot, "scripts/claude-bridge-mcp.mjs")], {}, async (client) => {
    const tools = (await client.request("tools/list")).tools;
    assert(tools.length === 1 && tools[0].name === "consult_fable", "reverse bridge must expose only consult_fable");
    assert(tools[0].inputSchema.properties.prompt.description.includes("BRIDGE_HOPS_REMAINING: 0"), "reverse bridge is missing its one-hop guard");
  });
  pass("reverse bridge exposes only guarded consult_fable and config preapproves only that tool");
  checkClaudeApproval(claudeBin);
  pass(`Claude Code approved and connected the codex server for ${repoRoot}`);
  if (!process.argv.includes("--live")) process.stdout.write("SKIP: live model round trip (opt in with --live)\n");
} catch (error) {
  process.stderr.write(`FAIL: ${error.message}\n`);
  process.exitCode = error.exitCode || 1;
} finally {
  if (scratch) rmSync(scratch, { recursive: true, force: true });
}
