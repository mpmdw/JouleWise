#!/usr/bin/env node
// Adapted from t3code (MIT, T3 Tools Inc.), commit defb7e6e, packages/effect-codex-app-server/src/protocol.ts and apps/server/src/orchestration-v2/Adapters/CodexAdapterV2.ts
// Node-builtins MCP -> Codex app-server adapter; protocol shapes: CLI 0.163.0.
// Census invariant: spawn the native codex child BEFORE answering initialize;
// never live without it. Child exit/spawn failure fails in-flight calls first,
// then exits nonzero. EOF/SIGTERM/SIGINT terminate the child as well.
// Turns have no adapter deadline. The caller's MCP tool timeout still limits
// the call: Claude Code's MCP_TOOL_TIMEOUT controls that caller-side budget.
// Progress is a heartbeat, not a promise to extend a hard timeout. Configure
// that budget at the caller or use the audited CLI for long work; no settings
// are changed here. CODEX_MCP_FRAME_LOG explicitly records full sensitive frames.

import { spawn } from "node:child_process";
import { createHash, randomUUID } from "node:crypto";
import { appendFileSync, mkdirSync, writeFileSync } from "node:fs";
import { dirname, resolve } from "node:path";

const MODEL = "gpt-6.1-sol";
const EFFORTS = new Set(["high", "xhigh"]);
// Three times T3's 10-second control-operation budget allows local startup
// contention. This bounds RPC acknowledgements, NEVER the duration of a turn.
const CONTROL_MS = 30_000;
// Six heartbeats per control budget, well within a typical 60-second MCP wait.
const PROGRESS_MS = CONTROL_MS / 6;
// A tenth of the control budget lets SIGTERM reap before escalating to SIGKILL.
const REAP_MS = CONTROL_MS / 10;
// T3's per-line transport bound; avoids unbounded unterminated JSONL input.
const MAX_FRAME_BYTES = 128 * 1024 * 1024;
const object = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const idLike = (v) => typeof v === "string" || (typeof v === "number" && Number.isFinite(v));
const hash = (s) => createHash("sha256").update(s).digest("hex");
const check = (ok, why) => { if (!ok) throw new Error(why); };

const tools = [
  {
    name: "codex", title: "Codex",
    description: "Run a Codex session with gpt-6.1-sol; effort high or xhigh via config.model_reasoning_effort.",
    inputSchema: {
      type: "object", additionalProperties: false, required: ["prompt"],
      properties: {
        prompt: { type: "string", description: "The initial user prompt." },
        "approval-policy": { type: "string", enum: ["on-request", "never"], description: "on-request only; never is retained for compatibility and refused." },
        "base-instructions": { type: "string", description: "Replace default base instructions." },
        "compact-prompt": { type: "string", description: "Prompt used when compacting the conversation." },
        config: { type: "object", additionalProperties: true, description: "Config overrides; model_reasoning_effort high (default) or xhigh. Reverse Claude MCP is always disabled." },
        cwd: { type: "string", description: "Working directory, relative to the MCP server cwd if not absolute." },
        "developer-instructions": { type: "string", description: "Developer role instructions." },
        model: { type: "string", description: "Only gpt-6.1-sol is permitted." },
        sandbox: { type: "string", enum: ["read-only", "workspace-write", "danger-full-access"], description: "Defaults to read-only; danger-full-access is refused." },
      },
    },
  },
  {
    name: "codex-reply", title: "Codex Reply",
    description: "Continue a Codex thread, resuming it after adapter restarts when necessary.",
    inputSchema: {
      type: "object", required: ["prompt"], properties: {
        prompt: { type: "string", description: "The next user prompt." },
        threadId: { type: "string", description: "Thread id; required unless conversationId is supplied." },
        conversationId: { type: "string", description: "DEPRECATED: use threadId instead." },
      },
    },
  },
];

const pending = new Map();
const calls = new Map();
const threads = new Map();
const activeThreads = new Map();
const work = new Set();
let nextId = 1;
let failure;
let closing = false;
let shutdownPromise;
let child;
let childClosed = false;
let initializePromise;
let frameVersion;
let frameBuffer = [];
const framePath = process.env.CODEX_MCP_FRAME_LOG;
let recordingStarted = false;

function record(entry) {
  if (!framePath) return;
  if (!recordingStarted) { frameBuffer.push(entry); return; }
  appendFileSync(framePath, `${JSON.stringify(entry)}\n`, { mode: 0o600 });
}

function startRecording(userAgent) {
  if (!framePath || recordingStarted) return;
  frameVersion = userAgent?.match(/\/(\d+\.\d+\.\d+(?:[-+][\w.-]+)?)/)?.[1] ?? "unknown";
  mkdirSync(dirname(resolve(framePath)), { recursive: true });
  writeFileSync(framePath, `${JSON.stringify({
    type: "transcript_start", provider: "codex", protocol: "codex.app-server",
    version: frameVersion, scenario: "codex-mcp-live",
    metadata: { source: "codex-mcp-server", userAgent: userAgent ?? null },
  })}\n`, { mode: 0o600 });
  recordingStarted = true;
  for (const entry of frameBuffer) record(entry);
  frameBuffer = [];
}

function mcp(message) {
  if (!process.stdout.destroyed) process.stdout.write(`${JSON.stringify({ jsonrpc: "2.0", ...message })}\n`);
}

function appSend(frame) {
  if (failure) throw failure;
  check(child?.stdin.writable, "app-server input is closed");
  record({ type: "expect_outbound", frame });
  child.stdin.write(`${JSON.stringify(frame)}\n`);
}

function rpc(method, params, onResult) {
  return new Promise((resolvePromise, reject) => {
    if (failure) { reject(failure); return; }
    const id = nextId++;
    const timer = setTimeout(() => {
      pending.delete(id);
      const error = new Error(`app-server ${method} acknowledgement timed out`);
      reject(error);
      fatal(error);
    }, CONTROL_MS);
    pending.set(id, { method, resolve: resolvePromise, reject, timer, onResult });
    try { appSend({ id, method, ...(params === undefined ? {} : { params }) }); }
    catch (error) { clearTimeout(timer); pending.delete(id); reject(error); }
  });
}

function ensureInitialized() {
  initializePromise ??= (async () => {
    let result;
    try {
      result = await rpc("initialize", {
        clientInfo: { name: "joulewise-codex-mcp", version: "1.0.0" },
        capabilities: { experimentalApi: true },
      });
      check(object(result) && typeof result.userAgent === "string", "malformed initialize response");
    } catch (error) {
      if (error.code !== -32600 || error.message !== "Already initialized") throw error;
    }
    startRecording(result?.userAgent);
    appSend({ method: "initialized" });
  })();
  return initializePromise;
}

// Normalize nested and dotted TOML overrides into one representation before
// checking policy or forcing a leaf. This removes parent/child shadowing.
function flattenConfig(value, prefix = "", result = {}) {
  for (const [key, entry] of Object.entries(value)) {
    check(key.length > 0 && !/["'\[\]\s]/.test(key), "config keys must be plain dotted TOML paths");
    const name = prefix ? `${prefix}.${key}` : key;
    if (object(entry) && Object.keys(entry).length) flattenConfig(entry, name, result);
    else {
      check(!Object.hasOwn(result, name), `conflicting config path: ${name}`);
      Object.defineProperty(result, name, { value: entry, enumerable: true, writable: true, configurable: true });
    }
  }
  return result;
}

function argumentsFor(name, args) {
  check(object(args), "tool arguments must be an object");
  check(typeof args.prompt === "string" && args.prompt.trim(), "prompt must be a non-empty string");
  const properties = tools.find((t) => t.name === name).inputSchema.properties;
  for (const key of Object.keys(args)) {
    check(Object.hasOwn(properties, key), `unsupported argument: ${key}`);
    if (key !== "config") check(typeof args[key] === "string", `${key} must be a string`);
  }
  if (name === "codex-reply") {
    check(!(args.threadId && args.conversationId && args.threadId !== args.conversationId), "threadId and conversationId disagree");
    const threadId = args.threadId ?? args.conversationId;
    check(typeof threadId === "string" && threadId.trim(), "threadId is required (conversationId is a deprecated alias)");
    return { threadId };
  }
  check(args.config === undefined || object(args.config), "config must be an object");
  const config = flattenConfig(args.config ?? {});
  for (const [key, value] of Object.entries(config)) {
    // Profiles can override these same settings: validate those too, even when
    // an explicit thread/turn parameter would otherwise take precedence.
    if (key === "model" || /^profiles\.[^.]+\.model$/.test(key)) check(value === MODEL, `model must be ${MODEL}`);
    if (key === "model_reasoning_effort" || /^profiles\.[^.]+\.model_reasoning_effort$/.test(key)) check(EFFORTS.has(value), "reasoning effort must be high or xhigh");
    if (key === "sandbox_mode" || /^profiles\.[^.]+\.sandbox_mode$/.test(key)) check(["read-only", "workspace-write"].includes(value), "sandbox must be read-only or workspace-write; danger-full-access is forbidden");
    if (key === "approval_policy" || /^profiles\.[^.]+\.approval_policy(?:\.|$)/.test(key) || key.startsWith("approval_policy.")) check(["on-request", "untrusted"].includes(value), "approval policy must retain approvals (on-request or untrusted)");
    if (key === "approvals_reviewer" || /^profiles\.[^.]+\.approvals_reviewer$/.test(key)) check(value === "user", "approvals_reviewer must be user; auto approvals are unavailable");
  }
  const model = args.model ?? config.model ?? MODEL;
  const effort = config.model_reasoning_effort ?? "high";
  const sandbox = args.sandbox ?? config.sandbox_mode ?? "read-only";
  const approvalPolicy = args["approval-policy"] ?? config.approval_policy ?? "on-request";
  check(model === MODEL, `model must be ${MODEL}`);
  check(EFFORTS.has(effort), "reasoning effort must be high or xhigh");
  check(["read-only", "workspace-write"].includes(sandbox), "sandbox must be read-only or workspace-write; danger-full-access is forbidden");
  check(["on-request", "untrusted"].includes(approvalPolicy), "approval policy must retain approvals (on-request or untrusted)");
  // Remove every conflicting ancestor/descendant, then install the forced leaf.
  for (const key of Object.keys(config)) {
    if (["mcp_servers", "mcp_servers.claude"].includes(key) || key === "mcp_servers.claude.enabled" || key.startsWith("mcp_servers.claude.enabled.")) delete config[key];
  }
  Object.assign(config, { "mcp_servers.claude.enabled": false, model_reasoning_effort: effort });
  if (args["compact-prompt"] !== undefined) config.compact_prompt = args["compact-prompt"];
  return {
    cwd: resolve(args.cwd ?? process.cwd()), model, sandbox, approvalPolicy,
    approvalsReviewer: "user", config,
    ...(args["base-instructions"] !== undefined ? { baseInstructions: args["base-instructions"] } : {}),
    ...(args["developer-instructions"] !== undefined ? { developerInstructions: args["developer-instructions"] } : {}),
  };
}

function selection(response, ctx) {
  check(object(response) && object(response.thread) && typeof response.thread.id === "string", "malformed thread response");
  ctx.threadId = response.thread.id;
  ctx.model = response.model ?? null;
  ctx.reasoningEffort = response.reasoningEffort ?? null;
  ctx.sandbox = response.sandbox ?? null;
  return { model: ctx.model, reasoningEffort: ctx.reasoningEffort, sandbox: ctx.sandbox,
    approvalPolicy: response.approvalPolicy, approvalsReviewer: response.approvalsReviewer, cwd: response.cwd };
}

function checkSelection(state) {
  check(state.model === MODEL, `app-server selected model ${state.model}; required ${MODEL}`);
  check(EFFORTS.has(state.reasoningEffort), `app-server reasoning effort is ${state.reasoningEffort}; high or xhigh readback required`);
  check(["readOnly", "workspaceWrite"].includes(state.sandbox?.type), "app-server returned an unsafe or missing sandbox");
  check(["on-request", "untrusted"].includes(state.approvalPolicy), "app-server removed approvals");
  check(state.approvalsReviewer === "user", "app-server enabled automatic approval review");
}

function callLog(ctx, status) {
  const directory = resolve(".codex-bridge");
  mkdirSync(directory, { recursive: true });
  appendFileSync(resolve(directory, "mcp-calls.jsonl"), `${JSON.stringify({
    time: new Date().toISOString(), callId: ctx.callId, threadId: ctx.threadId,
    model: ctx.model, reasoningEffort: ctx.reasoningEffort, sandbox: ctx.sandbox,
    promptSha256: ctx.promptHash, finalMessageSha256: hash(ctx.finalMessage),
    declinedRequests: ctx.declined, status,
  })}\n`, { mode: 0o600 });
}

function interrupt(ctx) {
  if (!ctx.turnId || ctx.interruptSent || ctx.terminal || failure) return;
  ctx.interruptSent = true;
  ctx.interruptTimer = setTimeout(() => fatal(new Error("turn/interrupt did not end the turn within the control budget")), CONTROL_MS);
  void rpc("turn/interrupt", { threadId: ctx.threadId, turnId: ctx.turnId }).catch(fatal);
}

function acceptTurn(ctx, turn, completed = false) {
  check(object(turn) && typeof turn.id === "string" && Array.isArray(turn.items) && ["inProgress", "completed", "failed", "interrupted"].includes(turn.status), "malformed turn payload");
  check(turn.error == null || (object(turn.error) && typeof turn.error.message === "string"), "malformed turn error");
  check(!ctx.turnId || ctx.turnId === turn.id, "app-server changed the active turn id");
  ctx.turnId = turn.id;
  for (const item of turn.items) acceptItem(ctx, item);
  if (completed || turn.status !== "inProgress") {
    check(turn.status !== "inProgress", "turn/completed carried inProgress status");
    ctx.terminal = turn;
    clearTimeout(ctx.interruptTimer);
    ctx.finishTurn();
  }
  if (ctx.cancelled || ctx.policyError) interrupt(ctx);
}

function acceptItem(ctx, item) {
  check(object(item) && typeof item.type === "string" && typeof item.id === "string", "malformed item payload");
  if (item.type !== "agentMessage") return;
  check(typeof item.text === "string", "malformed agent message");
  ctx.messages.set(item.id, item);
}

function notification(method, params) {
  const known = new Set(["thread/settings/updated", "model/rerouted", "turn/started", "turn/completed", "item/completed", "item/agentMessage/delta"]);
  if (!known.has(method)) return; // Forward-compatible unrelated telemetry.
  check(object(params) && typeof params.threadId === "string", `malformed ${method} notification`);
  const ctx = activeThreads.get(params.threadId);
  if (method === "thread/settings/updated") {
    const s = params.threadSettings;
    check(object(s) && typeof s.model === "string", "malformed thread settings");
    const state = { model: s.model,
      reasoningEffort: Object.hasOwn(s, "effort") ? s.effort : (threads.get(params.threadId)?.reasoningEffort ?? null), sandbox: s.sandboxPolicy,
      approvalPolicy: s.approvalPolicy, approvalsReviewer: s.approvalsReviewer, cwd: s.cwd };
    threads.set(params.threadId, state);
    if (ctx) {
      Object.assign(ctx, { model: state.model, reasoningEffort: state.reasoningEffort, sandbox: state.sandbox });
      try { checkSelection(state); } catch (error) { ctx.policyError ??= error.message; interrupt(ctx); }
    }
    return;
  }
  if (!ctx) return;
  if (method === "model/rerouted") {
    check(["fromModel", "toModel", "turnId", "reason"].every((key) => typeof params[key] === "string"), "malformed model/rerouted notification");
    ctx.model = params.toModel;
    const state = threads.get(params.threadId);
    if (state) state.model = params.toModel;
    if (params.toModel !== MODEL) { ctx.policyError = `model/rerouted away from ${MODEL} to ${params.toModel}`; interrupt(ctx); }
  } else if (method === "turn/started" || method === "turn/completed") {
    acceptTurn(ctx, params.turn, method === "turn/completed");
  } else {
    check(typeof params.turnId === "string", `malformed ${method} turnId`);
    if (ctx.turnId && ctx.turnId !== params.turnId) return;
    if (method === "item/completed") acceptItem(ctx, params.item);
    else {
      check(typeof params.itemId === "string" && typeof params.delta === "string", "malformed agent message delta");
      const previous = ctx.messages.get(params.itemId);
      ctx.messages.set(params.itemId, { type: "agentMessage", id: params.itemId,
        text: (previous?.text ?? "") + params.delta, phase: previous?.phase ?? null });
    }
  }
}

function serverRequest(frame) {
  const p = frame.params;
  check(object(p), `malformed ${frame.method} server request`);
  let result;
  const requiredStrings = (keys) => check(keys.every((key) => typeof p[key] === "string"), `malformed ${frame.method} request fields`);
  if (frame.method.startsWith("item/")) requiredStrings(["threadId", "turnId", "itemId"]);
  if (["item/commandExecution/requestApproval", "item/fileChange/requestApproval", "item/permissions/requestApproval"].includes(frame.method)) {
    check(Number.isInteger(p.startedAtMs), `malformed ${frame.method} startedAtMs`);
  }
  switch (frame.method) {
    case "item/commandExecution/requestApproval":
    case "item/fileChange/requestApproval": result = { decision: "decline" }; break;
    // An empty grant is the schema's denial representation; no permissions added.
    case "item/permissions/requestApproval":
      requiredStrings(["cwd"]);
      check(object(p.permissions), "malformed permissions request");
      result = { permissions: {}, scope: "turn" }; break;
    // No cancel enum exists for requestUserInput: an empty answers map is a skip.
    case "item/tool/requestUserInput":
      check(typeof p.isBlocking === "boolean" && Array.isArray(p.questions), "malformed user-input request");
      result = { answers: {} }; break;
    case "mcpServer/elicitation/request":
      requiredStrings(["serverName", "threadId"]);
      result = { action: "decline" }; break;
    default:
      appSend({ id: frame.id, error: { code: -32601, message: `Unsupported server request: ${frame.method}` } });
  }
  const declined = { method: frame.method, requestId: frame.id, itemId: p.itemId ?? null, response: result ?? "method-not-found" };
  const ctx = activeThreads.get(p.threadId);
  if (ctx) ctx.declined.push(declined);
  else process.stderr.write(`codex-mcp: declined unassociated request ${frame.method}\n`);
  if (result) appSend({ id: frame.id, result });
}

function appFrame(frame) {
  check(object(frame), "malformed app-server message: expected object");
  record({ type: "emit_inbound", frame });
  if (typeof frame.method === "string") {
    check(!("result" in frame) && !("error" in frame), "malformed app-server request/notification");
    if ("id" in frame) { check(idLike(frame.id), "malformed server request id"); serverRequest(frame); }
    else notification(frame.method, frame.params);
    return;
  }
  check(idLike(frame.id) && (("result" in frame) !== ("error" in frame)), "malformed app-server response envelope");
  const waiter = pending.get(frame.id);
  check(waiter, `app-server response has unknown id ${frame.id}`);
  if ("error" in frame) {
    check(object(frame.error) && Number.isInteger(frame.error.code) && typeof frame.error.message === "string", "malformed app-server error");
  }
  pending.delete(frame.id);
  clearTimeout(waiter.timer);
  if ("error" in frame) {
    waiter.reject(Object.assign(new Error(frame.error.message), { code: frame.error.code }));
  } else {
    try { waiter.onResult?.(frame.result); waiter.resolve(frame.result); }
    catch (error) { waiter.reject(error); }
  }
}

function lines(stream, onLine, onError) {
  let buffer = "";
  stream.setEncoding("utf8");
  stream.on("data", (chunk) => {
    try {
      buffer += chunk;
      let end;
      while ((end = buffer.indexOf("\n")) !== -1) {
        const line = buffer.slice(0, end);
        buffer = buffer.slice(end + 1);
        check(Buffer.byteLength(line) <= MAX_FRAME_BYTES, "JSONL frame exceeds transport bound");
        if (line.trim()) onLine(line);
      }
      check(Buffer.byteLength(buffer) <= MAX_FRAME_BYTES, "JSONL frame exceeds transport bound");
    } catch (error) { onError(error); }
  });
  stream.on("end", () => {
    if (buffer.trim()) {
      try { onLine(buffer); } catch (error) { onError(error); }
    }
  });
  stream.on("error", onError);
}

async function invoke(message, ctx) {
  let status = "error";
  let errorText;
  let progressTimer;
  try {
    const name = message.params.name;
    const args = message.params.arguments ?? {};
    const params = argumentsFor(name, args); // Refuse before ANY thread RPC.
    if (name === "codex-reply") {
      ctx.threadId = params.threadId;
      check(!activeThreads.has(ctx.threadId), "thread already has an active MCP call");
      activeThreads.set(ctx.threadId, ctx); // Reserve before resume/initialize awaits.
    }
    await ensureInitialized();
    if (ctx.cancelled) throw new Error("MCP caller cancelled before thread start");
    let state;
    const bind = (response) => {
      const expectedId = name === "codex-reply" ? ctx.threadId : null;
      check(!expectedId || expectedId === response?.thread?.id, "thread/resume returned a different thread id");
      state = selection(response, ctx);
      check(!activeThreads.has(ctx.threadId) || activeThreads.get(ctx.threadId) === ctx, "thread already has an active MCP call");
      threads.set(ctx.threadId, state);
      activeThreads.set(ctx.threadId, ctx);
      // Bind synchronously while routing the response, before later frames in
      // the same stdio chunk can update selection or report a reroute.
      callLog(ctx, "pending");
    };
    if (name === "codex") {
      await rpc("thread/start", params, bind);
      state = threads.get(ctx.threadId);
      const expectedSandbox = params.sandbox === "read-only" ? "readOnly" : "workspaceWrite";
      check(state.sandbox?.type === expectedSandbox, "app-server changed the requested sandbox mode");
    } else {
      state = threads.get(ctx.threadId);
      if (!state) {
        const resumeParams = {
          threadId: ctx.threadId, excludeTurns: true, model: MODEL,
          sandbox: "read-only", approvalPolicy: "on-request", approvalsReviewer: "user",
          config: { "mcp_servers.claude.enabled": false, model_reasoning_effort: "high" },
        };
        try { await rpc("thread/resume", resumeParams, bind); }
        catch (error) {
          if (!/\bsession \S+ is archived\b|\bcodex unarchive\b/i.test(error.message)) throw error;
          await rpc("thread/unarchive", { threadId: ctx.threadId });
          await rpc("thread/resume", resumeParams, bind);
        }
        state = threads.get(ctx.threadId);
        check(state.sandbox?.type === "readOnly", "app-server changed the resumed read-only sandbox");
      } else {
        Object.assign(ctx, { model: state.model, reasoningEffort: state.reasoningEffort, sandbox: state.sandbox });
        callLog(ctx, "pending");
      }
    }
    checkSelection(state);
    if (ctx.policyError) throw new Error(ctx.policyError);
    if (ctx.cancelled) throw new Error("MCP caller cancelled before turn start");
    activeThreads.set(ctx.threadId, ctx);
    const token = message.params._meta?.progressToken;
    let progress = 0;
    const heartbeat = () => mcp({ method: "notifications/progress", params: {
      progressToken: token, progress: ++progress, message: `Codex turn running (${ctx.threadId})`,
    } });
    if (idLike(token)) { heartbeat(); progressTimer = setInterval(heartbeat, PROGRESS_MS); }
    const response = await rpc("turn/start", {
      threadId: ctx.threadId, input: [{ type: "text", text: args.prompt }],
      model: MODEL, effort: state.reasoningEffort, cwd: state.cwd,
      approvalPolicy: state.approvalPolicy, approvalsReviewer: "user", sandboxPolicy: state.sandbox,
    });
    acceptTurn(ctx, response?.turn);
    await ctx.turnDone;
    const candidates = [...ctx.messages.values()];
    ctx.finalMessage = (candidates.filter((item) => item.phase === "final_answer").at(-1)
      ?? candidates.filter((item) => item.phase == null).at(-1))?.text ?? "";
    if (ctx.policyError) throw new Error(ctx.policyError);
    if (ctx.cancelled) throw new Error("MCP caller cancelled the turn");
    check(ctx.terminal.status === "completed", `Codex turn ${ctx.terminal.status}: ${ctx.terminal.error?.message ?? "no further detail"}`);
    check(ctx.finalMessage.trim(), "Codex completed without a final agent message");
    status = "completed";
  } catch (error) {
    status = ctx.cancelled ? "cancelled" : "error";
    errorText = error.message;
  } finally {
    clearInterval(progressTimer);
    clearTimeout(ctx.interruptTimer);
    if (activeThreads.get(ctx.threadId) === ctx) activeThreads.delete(ctx.threadId);
    try { callLog(ctx, status); }
    catch (error) { status = "error"; errorText = `Could not persist MCP call log: ${error.message}`; }
    const structuredContent = {
      threadId: ctx.threadId, model: ctx.model, reasoningEffort: ctx.reasoningEffort,
      turnStatus: ctx.terminal?.status ?? status, declinedRequests: ctx.declined,
    };
    // Prefix adapter notices so the agent's required final bridge envelope
    // remains final even for clients that concatenate MCP text blocks.
    const text = [ctx.declined.length ? `Declined requests: ${JSON.stringify(ctx.declined)}` : "",
      status === "completed" ? ctx.finalMessage : `Codex MCP error: ${errorText}`].filter(Boolean).join("\n\n");
    mcp({ id: message.id, result: {
      content: [{ type: "text", text }], structuredContent,
      ...(status === "completed" ? {} : { isError: true }),
    } });
    calls.delete(message.id);
  }
}

async function handle(message) {
  check(object(message) && message.jsonrpc === "2.0", "expected MCP JSON-RPC 2.0 object");
  if (message.method === "notifications/cancelled") {
    const ctx = calls.get(message.params?.requestId);
    if (ctx) { ctx.cancelled = true; interrupt(ctx); }
    return;
  }
  if (!("id" in message)) return;
  if (closing) { mcp({ id: message.id, error: { code: -32603, message: failure?.message ?? "server closing" } }); return; }
  if (message.method === "initialize") {
    await ensureInitialized();
    mcp({ id: message.id, result: {
      protocolVersion: message.params?.protocolVersion || "2025-06-18",
      capabilities: { tools: { listChanged: false } }, serverInfo: { name: "codex", version: "1.0.0" },
    } });
  } else if (message.method === "tools/list") mcp({ id: message.id, result: { tools } });
  else if (message.method === "ping") mcp({ id: message.id, result: {} });
  else if (message.method === "tools/call") {
    if (!tools.some((t) => t.name === message.params?.name)) {
      mcp({ id: message.id, error: { code: -32601, message: `unknown tool: ${message.params?.name}` } }); return;
    }
    check(!calls.has(message.id), "duplicate in-flight MCP request id");
    let finishTurn, failTurn;
    const turnDone = new Promise((res, rej) => { finishTurn = res; failTurn = rej; });
    // A child can die before invoke reaches the await; attach a handler now.
    turnDone.catch(() => {});
    const prompt = message.params.arguments?.prompt;
    const ctx = { callId: randomUUID(), threadId: null, model: null, reasoningEffort: null, sandbox: null,
      promptHash: hash(typeof prompt === "string" ? prompt : ""), finalMessage: "", declined: [],
      messages: new Map(), turnDone, finishTurn, failTurn };
    calls.set(message.id, ctx);
    await invoke(message, ctx);
  } else mcp({ id: message.id, error: { code: -32601, message: `method not found: ${message.method}` } });
}

function fatal(error) {
  if (closing) return;
  failure = error instanceof Error ? error : new Error(String(error));
  process.stderr.write(`codex-mcp: ${failure.message}\n`);
  void shutdown(1);
}

function shutdown(code) {
  if (shutdownPromise) return shutdownPromise;
  closing = true;
  failure ??= new Error("MCP transport closed");
  for (const waiter of pending.values()) { clearTimeout(waiter.timer); waiter.reject(failure); }
  pending.clear();
  for (const ctx of calls.values()) ctx.failTurn(failure);
  shutdownPromise = (async () => {
    const reaped = new Promise((done) => {
      if (!child || childClosed || !child.pid) { done(); return; }
      child.once("close", done);
      child.kill("SIGTERM");
      const killTimer = setTimeout(() => {
        child.kill("SIGKILL");
        // Descendants must not keep inherited pipes (and this adapter) alive
        // after the native child has exited. The reap budget bounds that case.
        child.stdin.destroy(); child.stdout.destroy(); child.stderr.destroy();
        done();
      }, REAP_MS);
      child.once("close", () => clearTimeout(killTimer));
    });
    await Promise.allSettled([...work]); // Flush tool errors before process exit.
    await reaped;
    try { startRecording(); record({ type: "runtime_exit", status: code ? "error" : "success" }); }
    catch (error) { process.stderr.write(`codex-mcp frame log: ${error.message}\n`); code = 1; }
    process.stdout.write("", () => process.exit(code));
  })();
  return shutdownPromise;
}

// No lazy spawning: name-only prewindow checks depend on this native child.
child = spawn(process.env.CODEX_BIN || "codex", ["app-server"], { stdio: ["pipe", "pipe", "pipe"] });
child.on("error", (error) => fatal(new Error(`Could not spawn app-server: ${error.message}`)));
child.on("exit", (code, signal) => fatal(new Error(`app-server exited (${signal ?? code})`)));
child.on("close", () => { childClosed = true; });
child.stdin.on("error", fatal);
child.stderr.on("data", (chunk) => process.stderr.write(chunk));
lines(child.stdout, (line) => appFrame(JSON.parse(line)), fatal);
child.stdout.on("end", () => fatal(new Error("app-server output ended (child exited or closed its transport)")));
lines(process.stdin, (line) => {
  let message;
  try { message = JSON.parse(line); }
  catch (error) { mcp({ id: null, error: { code: -32700, message: error.message } }); return; }
  const task = handle(message).catch((error) => {
    mcp({ id: message?.id ?? null, error: { code: -32603, message: error.message } });
  });
  work.add(task);
  void task.finally(() => work.delete(task));
}, fatal);
process.stdin.on("end", () => { void shutdown(0); });
process.on("SIGTERM", () => { void shutdown(0); });
process.on("SIGINT", () => { void shutdown(0); });
process.stdout.on("error", () => { void shutdown(1); });
