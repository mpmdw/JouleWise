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

function failedBridgeEnvelope(summary, flag) {
  const report = {
    status: "FAILED",
    summary,
    pathspec: [],
    verification: [],
    flags: [flag],
  };
  return `BRIDGE_REPORT_V1\n${JSON.stringify(report)}`;
}

function failedBridgeResult(summary, flag) {
  return resultText(failedBridgeEnvelope(summary, flag), true);
}

function protocolDeviationResult(output, status) {
  const failure = failedBridgeEnvelope(
    `Claude Fable returned status ${status}; a one-shot read-only consult may end only DISCUSSION or NEEDS_RULING`,
    "protocol_deviation",
  );
  return resultText(`${output.trim()}\n${failure}`, true);
}

function validateAndStripHeaders(prompt) {
  const lines = prompt.split(/\r?\n/);
  const originLines = lines.filter((line) => /^\s*BRIDGE_ORIGIN\s*:/.test(line));
  const hopLines = lines.filter((line) => /^\s*BRIDGE_HOPS_REMAINING\s*:/.test(line));

  if (originLines.length !== 1 || hopLines.length !== 1) {
    return {
      error:
        "reverse bridge requires exactly one BRIDGE_ORIGIN header and exactly one BRIDGE_HOPS_REMAINING header",
    };
  }
  if (originLines[0].trim() === "BRIDGE_ORIGIN: claude") {
    return { error: "a Claude-originated Sol session cannot call the reverse bridge" };
  }
  if (lines[0]?.trim() !== "BRIDGE_ORIGIN: codex") {
    return { error: "reverse bridge requires BRIDGE_ORIGIN: codex as the first line" };
  }
  if (lines[1]?.trim() !== "BRIDGE_HOPS_REMAINING: 0") {
    return { error: "reverse bridge requires BRIDGE_HOPS_REMAINING: 0 as the second line" };
  }
  return { body: lines.slice(2).join("\n") };
}

function bridgePrompt(body) {
  return [
    "BRIDGE_ORIGIN: codex",
    "BRIDGE_HOPS_REMAINING: 0",
    "You are a read-only Fable peer consultant to a top-level Codex lead.",
    "Do not edit files, invoke Codex or Sol, use MCP, run shell commands, start agents, or delegate.",
    "Return concise findings, reasoning, risks, and a recommendation. The caller owns the decision.",
    "Your response MUST end with exactly two nonempty lines: the literal sentinel " +
      "BRIDGE_REPORT_V1, then one minified JSON object line.",
    "That JSON object MUST contain exactly status, summary, pathspec, verification, and flags; " +
      "status must be DISCUSSION, or NEEDS_RULING for an advisory question, pathspec must be [], " +
      "and nothing may follow the JSON line.",
    "",
    body,
  ].join("\n");
}

function bridgeReportProblem(output) {
  const trimmed = output.trim();
  const lines = trimmed ? trimmed.split(/\r?\n/) : [];
  const sentinelIndexes = [];
  lines.forEach((line, index) => {
    if (line.trim() === "BRIDGE_REPORT_V1") sentinelIndexes.push(index);
  });
  if (sentinelIndexes.length !== 1 || sentinelIndexes[0] !== lines.length - 2) {
    return "the BRIDGE_REPORT_V1 sentinel must appear exactly once immediately before the final line";
  }
  const jsonLine = lines.at(-1);
  let report;
  try {
    report = JSON.parse(jsonLine);
  } catch {
    return "the final bridge report line is not valid JSON";
  }
  if (!report || Array.isArray(report) || typeof report !== "object") {
    return "the bridge report must be a JSON object";
  }
  let inString = false;
  let escaped = false;
  let insignificantWhitespace = false;
  for (const character of jsonLine) {
    if (escaped) {
      escaped = false;
    } else if (inString && character === "\\") {
      escaped = true;
    } else if (character === '"') {
      inString = !inString;
    } else if (!inString && /\s/.test(character)) {
      insignificantWhitespace = true;
      break;
    }
  }
  if (insignificantWhitespace) {
    return "the bridge report JSON line must be minified";
  }
  const requiredKeys = ["flags", "pathspec", "status", "summary", "verification"];
  if (Object.keys(report).sort().join(",") !== requiredKeys.join(",")) {
    return "the bridge report has missing or additional fields";
  }
  const statuses = new Set([
    "DONE",
    "PARTIAL",
    "DISCUSSION",
    "NEEDS_SCOPE",
    "NEEDS_RULING",
    "BLOCKED",
    "FAILED",
  ]);
  if (!statuses.has(report.status)) return "the bridge report has an invalid status";
  if (typeof report.summary !== "string" || !report.summary.trim()) {
    return "the bridge report summary must be nonempty";
  }
  if (![report.pathspec, report.verification, report.flags].every(Array.isArray)) {
    return "the bridge report pathspec, verification, and flags fields must be arrays";
  }
  if (report.pathspec.length !== 0) return "a read-only consult must return an empty pathspec";
  if (![report.verification, report.flags].every((items) => items.every((item) => typeof item === "string"))) {
    return "the bridge report verification and flags entries must be strings";
  }
  return null;
}

async function consultFable(prompt) {
  if (typeof prompt !== "string" || !prompt.trim()) {
    return failedBridgeResult("prompt must be a non-empty string", "protocol_failure");
  }
  if (prompt.length > 100_000) {
    return failedBridgeResult(
      "prompt exceeds the 100000-character bridge limit",
      "protocol_failure",
    );
  }
  const validated = validateAndStripHeaders(prompt);
  if (validated.error) return failedBridgeResult(validated.error, "protocol_failure");

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
    bridgePrompt(validated.body),
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

    // Bound both streams; stdout is validated, while stderr supplies bounded failure detail.
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
      finish(failedBridgeResult("Claude Fable transport could not be started", "transport_failure"));
    });
    child.on("close", (code, signal) => {
      if (code === 0) {
        const protocolProblem = bridgeReportProblem(stdout);
        if (protocolProblem) {
          finish(
            failedBridgeResult(
              `Claude Fable returned an invalid bridge-report/v1 envelope: ${protocolProblem}`,
              "protocol_failure",
            ),
          );
          return;
        }
        const report = JSON.parse(stdout.trim().split(/\r?\n/).at(-1));
        if (!["DISCUSSION", "NEEDS_RULING"].includes(report.status)) {
          finish(protocolDeviationResult(stdout, report.status));
          return;
        }
        finish(resultText(stdout.trim()));
        return;
      }
      const termination = signal ? `signal ${signal}` : `exit ${code}`;
      const detail = stderr.trim();
      const summary = detail
        ? `Claude Fable transport failed (${termination}): ${detail}`
        : `Claude Fable transport failed (${termination})`;
      finish(failedBridgeResult(summary, "transport_failure"));
    });

    timer = setTimeout(() => {
      child.kill("SIGTERM");
      finish(failedBridgeResult("Claude Fable transport timed out", "transport_failure"));
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
