#!/usr/bin/env node
// Adapted from t3code (MIT, T3 Tools Inc.), commit defb7e6e, packages/effect-codex-app-server/src/replay.ts
// A transcript peer, never an LLM. CODEX_BIN selects this executable in tests.
import { readFileSync, writeFileSync } from "node:fs";
import readline from "node:readline";

if (process.argv[2] !== "app-server") throw new Error("replay peer expects app-server");
const entries = readFileSync(process.env.CODEX_REPLAY_TRANSCRIPT, "utf8").trim().split("\n").map(JSON.parse);
const header = entries.shift();
if (header.type !== "transcript_start") throw new Error("missing transcript_start");
if (process.env.CODEX_REPLAY_PID) writeFileSync(process.env.CODEX_REPLAY_PID, String(process.pid));
let cursor = 0;
const clientIds = new Map();
const input = readline.createInterface({ input: process.stdin });
const frames = [];
let wake;
let ended = false;
input.on("line", (line) => { frames.push(JSON.parse(line)); wake?.(); });
input.on("close", () => { ended = true; wake?.(); });

function subset(actual, expected, path = "frame") {
  if (Array.isArray(expected)) {
    if (!Array.isArray(actual) || actual.length !== expected.length) throw new Error(`${path}: array mismatch`);
    expected.forEach((v, i) => subset(actual[i], v, `${path}[${i}]`));
  } else if (expected !== null && typeof expected === "object") {
    if (actual === null || typeof actual !== "object") throw new Error(`${path}: expected object`);
    for (const [k, v] of Object.entries(expected)) {
      if (path === "frame" && k === "id") continue;
      // Wall-clock fields are provenance, not replay expectations.
      if (["emittedAtMs", "startedAtMs", "createdAt", "updatedAt"].includes(k)) continue;
      subset(actual[k], v, `${path}.${k}`);
    }
  } else if (actual !== expected) throw new Error(`${path}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
}

async function take() {
  while (!frames.length && !ended) await new Promise((res) => { wake = res; });
  if (!frames.length) throw new Error(`EOF before replay cursor ${cursor}`);
  return frames.shift();
}

function finish() {
  if (cursor !== entries.length || frames.length) throw new Error(`incomplete replay at ${cursor}/${entries.length}, extra frames ${frames.length}`);
  process.stderr.write(`REPLAY OK ${header.scenario}\n`);
}

// SIGTERM is the adapter's normal teardown. Report an unconsumed expectation
// even on that path so tests cannot hide a missing policy/interrupt frame.
process.on("SIGTERM", () => {
  try { finish(); process.exit(0); }
  catch (error) { process.stderr.write(`REPLAY ERROR ${error.message}\n`); process.exit(1); }
});

try {
  while (cursor < entries.length) {
    const entry = entries[cursor++];
    if (entry.type === "expect_outbound") {
      const actual = await take();
      subset(actual, entry.frame);
      if (entry.frame.method && "id" in entry.frame) clientIds.set(entry.frame.id, actual.id);
      // Responses must still correlate to the peer's request id.
      if (!entry.frame.method && "id" in entry.frame && actual.id !== entry.frame.id) throw new Error("server-request response id mismatch");
    } else if (entry.type === "emit_inbound") {
      // afterMs comes directly from the scripted transcript, not an idle bound.
      if (entry.afterMs) await new Promise((res) => setTimeout(res, entry.afterMs));
      const frame = structuredClone(entry.frame);
      if (frame && !frame.method && clientIds.has(frame.id)) frame.id = clientIds.get(frame.id);
      process.stdout.write(`${JSON.stringify(frame)}\n`);
    } else if (entry.type === "runtime_exit") {
      process.stderr.write(`REPLAY EXIT ${entry.status}\n`);
      process.exit(entry.status === "success" ? 0 : 7);
    } else throw new Error(`unknown replay entry ${entry.type}`);
  }
  // Successful transcripts omit runtime_exit so the peer stays present until
  // transport teardown, like the real persistent app-server.
  while (!ended) await new Promise((res) => { wake = res; });
  finish();
} catch (error) {
  process.stderr.write(`REPLAY ERROR ${header.scenario} cursor ${cursor}: ${error.message}\n`);
  process.exitCode = 1;
  input.close();
  process.stdin.destroy();
}
