#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const scriptRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
let repository = scriptRoot;

if (process.argv.length > 2) {
  if (process.argv.length !== 4 || process.argv[2] !== "--root") {
    process.stderr.write("usage: node scripts/check-bridge-docs.mjs [--root REPOSITORY]\n");
    process.exit(2);
  }
  repository = path.resolve(process.argv[3]);
}

const contractRelative = "docs/contracts/bridge_protocol.md";
const beginMarker = "<!-- BEGIN BRIDGE CONSUMER DRIFT MANIFEST -->";
const endMarker = "<!-- END BRIDGE CONSUMER DRIFT MANIFEST -->";
const requiredSnippetIds = [
  "scope_authority",
  "quiet_mac",
  "no_bypass",
  "one_hop",
  "envelope_failure",
];
const requiredConsumers = [
  "CLAUDE.md",
  "AGENTS.md",
  ".claude/agents/codex.md",
  ".claude/commands/codex.md",
  ".claude/skills/codex/SKILL.md",
];
const errors = [];

function read(relative) {
  const absolute = path.join(repository, relative);
  try {
    return fs.readFileSync(absolute, "utf8");
  } catch (error) {
    errors.push(`${relative}: cannot read: ${error.code ?? error.message}`);
    return null;
  }
}

function occurrenceCount(text, needle) {
  let count = 0;
  let offset = 0;
  while (true) {
    const found = text.indexOf(needle, offset);
    if (found < 0) return count;
    count += 1;
    offset = found + needle.length;
  }
}

function sameMembers(actual, expected) {
  return actual.length === expected.length
    && new Set(actual).size === actual.length
    && actual.every((item) => expected.includes(item));
}

const contract = read(contractRelative);
let manifest = null;
if (contract !== null) {
  const begin = contract.indexOf(beginMarker);
  const end = contract.indexOf(endMarker);
  if (begin < 0 || end < 0 || end <= begin) {
    errors.push(`${contractRelative}: bridge consumer drift manifest markers are missing or out of order`);
  } else if (contract.indexOf(beginMarker, begin + beginMarker.length) >= 0) {
    errors.push(`${contractRelative}: bridge consumer drift manifest begin marker is duplicated`);
  } else {
    const body = contract.slice(begin + beginMarker.length, end);
    const fenced = body.match(/^\s*```json\s*\n([\s\S]*?)\n```\s*$/);
    if (fenced === null) {
      errors.push(`${contractRelative}: drift manifest must be one fenced JSON object`);
    } else {
      try {
        manifest = JSON.parse(fenced[1]);
      } catch (error) {
        errors.push(`${contractRelative}: drift manifest is not valid JSON: ${error.message}`);
      }
    }
  }
}

if (manifest !== null) {
  if (manifest.schema !== "bridge-consumer-drift/v1") {
    errors.push(`${contractRelative}: unexpected drift manifest schema ${JSON.stringify(manifest.schema)}`);
  }
  if (manifest.snippets === null || typeof manifest.snippets !== "object" || Array.isArray(manifest.snippets)) {
    errors.push(`${contractRelative}: snippets must be an object`);
  }
  if (manifest.consumers === null || typeof manifest.consumers !== "object" || Array.isArray(manifest.consumers)) {
    errors.push(`${contractRelative}: consumers must be an object`);
  }

  if (errors.length === 0) {
    const snippetIds = Object.keys(manifest.snippets);
    if (!sameMembers(snippetIds, requiredSnippetIds)) {
      errors.push(`${contractRelative}: snippet IDs must be exactly ${requiredSnippetIds.join(", ")}`);
    }
    const consumers = Object.keys(manifest.consumers);
    if (!sameMembers(consumers, requiredConsumers)) {
      errors.push(`${contractRelative}: consumers must be exactly ${requiredConsumers.join(", ")}`);
    }
    for (const relative of requiredConsumers) {
      const snippetIdsForConsumer = manifest.consumers[relative];
      if (!Array.isArray(snippetIdsForConsumer)
          || !sameMembers(snippetIdsForConsumer, requiredSnippetIds)) {
        errors.push(
          `${relative}: manifest snippet IDs must be exactly ${requiredSnippetIds.join(", ")}`,
        );
      }
    }
  }

  if (errors.length === 0) {
    for (const [relative, snippetIds] of Object.entries(manifest.consumers)) {
      const consumer = read(relative);
      if (!Array.isArray(snippetIds) || snippetIds.length === 0) {
        errors.push(`${relative}: manifest snippet list must be non-empty`);
        continue;
      }
      if (consumer === null) continue;
      if (!consumer.includes(contractRelative)) {
        errors.push(`${relative}: missing pointer to ${contractRelative}`);
      }
      for (const snippetId of snippetIds) {
        const snippet = manifest.snippets[snippetId];
        if (typeof snippet !== "string" || snippet.length === 0) {
          errors.push(`${relative}: unknown or empty snippet ${JSON.stringify(snippetId)}`);
          continue;
        }
        const count = occurrenceCount(consumer, snippet);
        if (count !== 1) {
          errors.push(`${relative}: canonical snippet ${snippetId} occurs ${count} times; expected 1`);
        }
      }
    }
  }
}

if (errors.length > 0) {
  for (const error of errors) process.stderr.write(`bridge docs check: ${error}\n`);
  process.exit(1);
}

process.stdout.write(
  `bridge docs check OK (${Object.keys(manifest.consumers).length} consumers, `
    + `${Object.keys(manifest.snippets).length} snippets)\n`,
);
