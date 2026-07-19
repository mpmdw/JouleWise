#!/usr/bin/env node

import fs from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import { randomUUID } from "node:crypto";

const args = new Map();
for (let index = 2; index < process.argv.length; index += 2) {
  const key = process.argv[index];
  const value = process.argv[index + 1];
  if (!key?.startsWith("--") || value == null) {
    throw new Error(`invalid argument near ${key ?? "<end>"}`);
  }
  args.set(key.slice(2), value);
}

function required(name) {
  const value = args.get(name);
  if (!value) throw new Error(`missing --${name}`);
  return value;
}

const threadId = required("thread-id");
const promptFile = required("prompt-file");
const outputFile = required("output-file");
const cwd = required("cwd");
const model = args.get("model") ?? "gpt-5.6-sol";
const effort = args.get("effort") ?? "high";
const sandbox = args.get("sandbox") ?? "workspace-write";
const timeoutMs = Number(args.get("timeout-ms") ?? process.env.CODEX_APP_BRIDGE_TIMEOUT_MS ?? 3_600_000);
const codexHome = process.env.CODEX_HOME ?? path.join(os.homedir(), ".codex");
const socketPath = process.env.CODEX_DESKTOP_IPC_SOCKET ?? path.join(codexHome, "ipc", "ipc.sock");
const lockFile = args.get("lock-file") ?? `${outputFile}.app-thread.lock`;
const prompt = fs.readFileSync(promptFile, "utf8");

if (!Number.isFinite(timeoutMs) || timeoutMs < 1_000) throw new Error("invalid timeout");
if (!fs.existsSync(socketPath)) throw new Error(`Codex desktop IPC socket not found: ${socketPath}`);
const socketStat = fs.statSync(socketPath);
const socketDirectoryStat = fs.statSync(path.dirname(socketPath));
const currentUid = process.getuid?.();
if (!socketStat.isSocket()) throw new Error(`Codex desktop IPC path is not a socket: ${socketPath}`);
if (currentUid != null && (socketStat.uid !== currentUid || socketDirectoryStat.uid !== currentUid)) {
  throw new Error("Codex desktop IPC socket is not owned by the current user");
}
if ((socketDirectoryStat.mode & 0o022) !== 0) {
  throw new Error("Codex desktop IPC directory is group- or world-writable");
}

let lockOwned = false;
async function acquireLock() {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    try {
      const fd = fs.openSync(lockFile, "wx", 0o600);
      fs.writeFileSync(fd, `${process.pid}\n`);
      fs.closeSync(fd);
      lockOwned = true;
      return;
    } catch (error) {
      if (error?.code !== "EEXIST") throw error;
      let ownerPid = 0;
      try {
        ownerPid = Number(fs.readFileSync(lockFile, "utf8").trim());
        if (!Number.isInteger(ownerPid) || ownerPid < 1) throw new Error("invalid lock owner");
        process.kill(ownerPid, 0);
      } catch (ownerError) {
        if (ownerError?.code !== "EPERM") {
          try {
            fs.unlinkSync(lockFile);
          } catch (unlinkError) {
            if (unlinkError?.code !== "ENOENT") throw unlinkError;
          }
          continue;
        }
      }
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
  }
  throw new Error(`timed out waiting for app thread lock: ${lockFile}`);
}

function releaseLock() {
  if (!lockOwned) return;
  lockOwned = false;
  try {
    fs.unlinkSync(lockFile);
  } catch (error) {
    if (error?.code !== "ENOENT") throw error;
  }
}

await acquireLock();
process.on("exit", releaseLock);

const socket = net.createConnection(socketPath);
const pending = new Map();
let clientId = "initializing-client";
let readBuffer = Buffer.alloc(0);
let activeTurn = false;
let shuttingDown = false;

function encode(message) {
  const payload = Buffer.from(JSON.stringify(message));
  const frame = Buffer.allocUnsafe(payload.length + 4);
  frame.writeUInt32LE(payload.length, 0);
  payload.copy(frame, 4);
  return frame;
}

function send(message) {
  socket.write(encode(message));
}

function request(method, params, { timeout = 30_000, version = 0 } = {}) {
  const requestId = randomUUID();
  const message = {
    type: "request",
    requestId,
    sourceClientId: clientId,
    version,
    method,
    params,
    timeoutMs: timeout,
  };
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => {
      pending.delete(requestId);
      reject(new Error(`${method} timed out`));
    }, timeout + 1_000);
    pending.set(requestId, { resolve, reject, timer });
    send(message);
  });
}

function handleMessage(message) {
  if (message.type === "client-discovery-request") {
    send({
      type: "client-discovery-response",
      requestId: message.requestId,
      response: { canHandle: false },
    });
    return;
  }
  if (message.type !== "response") return;
  const waiter = pending.get(message.requestId);
  if (!waiter) return;
  clearTimeout(waiter.timer);
  pending.delete(message.requestId);
  if (message.resultType === "error") waiter.reject(new Error(message.error ?? "IPC request failed"));
  else waiter.resolve(message);
}

socket.on("data", (chunk) => {
  readBuffer = Buffer.concat([readBuffer, chunk]);
  while (readBuffer.length >= 4) {
    const length = readBuffer.readUInt32LE(0);
    if (length < 1 || length > 256 * 1024 * 1024) throw new Error(`invalid IPC frame length: ${length}`);
    if (readBuffer.length < length + 4) return;
    const payload = readBuffer.subarray(4, length + 4);
    readBuffer = readBuffer.subarray(length + 4);
    handleMessage(JSON.parse(payload.toString("utf8")));
  }
});
socket.on("error", (error) => {
  for (const [requestId, waiter] of pending) {
    clearTimeout(waiter.timer);
    waiter.reject(error);
    pending.delete(requestId);
  }
});

const connected = new Promise((resolve, reject) => {
  socket.once("connect", resolve);
  socket.once("error", reject);
});

function findRollout(root, id) {
  if (!fs.existsSync(root)) return null;
  const stack = [root];
  while (stack.length > 0) {
    const directory = stack.pop();
    for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
      const candidate = path.join(directory, entry.name);
      if (entry.isDirectory()) stack.push(candidate);
      else if (entry.isFile() && entry.name.includes(id) && entry.name.endsWith(".jsonl")) return candidate;
    }
  }
  return null;
}

function taskCompleteSince(rolloutFile, startOffset, expectedTurnId) {
  const fd = fs.openSync(rolloutFile, "r");
  try {
    const size = fs.fstatSync(fd).size;
    if (size <= startOffset) return null;
    const buffer = Buffer.alloc(size - startOffset);
    fs.readSync(fd, buffer, 0, buffer.length, startOffset);
    for (const line of buffer.toString("utf8").split("\n")) {
      if (!line.trim()) continue;
      let record;
      try {
        record = JSON.parse(line);
      } catch {
        continue;
      }
      const payload = record?.type === "event_msg" ? record.payload : null;
      if (payload?.type !== "task_complete") continue;
      if (expectedTurnId && payload.turn_id !== expectedTurnId) continue;
      return payload;
    }
  } finally {
    fs.closeSync(fd);
  }
  return null;
}

function findTurnId(value) {
  if (!value || typeof value !== "object") return null;
  if (typeof value.turnId === "string") return value.turnId;
  if (typeof value.turn_id === "string") return value.turn_id;
  if (typeof value.id === "string" && value.id.startsWith("019")) return value.id;
  for (const child of Object.values(value)) {
    const found = findTurnId(child);
    if (found) return found;
  }
  return null;
}

async function interruptAndExit(signal) {
  if (shuttingDown) return;
  shuttingDown = true;
  if (activeTurn) {
    try {
      await request(
        "thread-follower-interrupt-turn",
        { conversationId: threadId },
        { timeout: 5_000, version: 2 },
      );
    } catch {
      // The wrapper is exiting; failure to deliver an interrupt is reported by its status record.
    }
  }
  socket.destroy();
  releaseLock();
  process.exit(signal === "SIGINT" ? 130 : 143);
}

process.on("SIGINT", () => void interruptAndExit("SIGINT"));
process.on("SIGTERM", () => void interruptAndExit("SIGTERM"));

await connected;
const initialized = await request("initialize", { clientType: "claude-code-bridge" }, { timeout: 10_000 });
clientId = initialized?.result?.clientId ?? initialized?.handledByClientId ?? clientId;

let rolloutFile = findRollout(path.join(codexHome, "sessions"), threadId);
if (!rolloutFile) throw new Error(`rollout not found for app thread ${threadId}`);
const startOffset = fs.statSync(rolloutFile).size;
const sandboxPolicy = sandbox === "read-only"
  ? { type: "readOnly", networkAccess: false }
  : { type: "workspaceWrite", writableRoots: [cwd], networkAccess: false };
const turnStartParams = {
  threadId,
  input: [{ type: "text", text: prompt }],
  cwd,
  model,
  effort,
  approvalPolicy: "on-request",
  approvalsReviewer: "auto_review",
  sandboxPolicy,
};

let started;
try {
  started = await request(
    "thread-follower-start-turn",
    { conversationId: threadId, turnStartParams },
    { timeout: 120_000, version: 1 },
  );
} catch (error) {
  if (String(error?.message).includes("no-client-found")) {
    throw new Error(
      `Codex desktop is not hosting bridge task ${threadId}; open that task once in the app, then retry`,
    );
  }
  throw error;
}
activeTurn = true;
const turnId = findTurnId(started?.result);
process.stdout.write(`session id: ${threadId}\n`);
if (turnId) process.stdout.write(`turn id: ${turnId}\n`);

const deadline = Date.now() + timeoutMs;
let complete = null;
while (Date.now() < deadline) {
  rolloutFile ??= findRollout(path.join(codexHome, "sessions"), threadId);
  complete = taskCompleteSince(rolloutFile, startOffset, turnId);
  if (complete) break;
  await new Promise((resolve) => setTimeout(resolve, 250));
}

if (!complete) {
  await interruptAndExit("SIGTERM");
  throw new Error(`app turn timed out after ${timeoutMs} ms`);
}

activeTurn = false;
const answer = complete.last_agent_message ?? "";
fs.writeFileSync(outputFile, answer.endsWith("\n") ? answer : `${answer}\n`);
process.stdout.write(answer.endsWith("\n") ? answer : `${answer}\n`);
socket.end();
releaseLock();
