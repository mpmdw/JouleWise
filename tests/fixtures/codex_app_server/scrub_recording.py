"""Deterministic privacy projection of the lead's immutable live recording.

Usage: python3 -B scrub_recording.py <frames.ndjson> <smoke.json> <output>
Only private payloads/paths change; protocol ordering, ids, timestamps, tool
requests and message text remain recorded evidence. Empty account/rate-limit
objects are fixed, schema-valid placeholders, not recorded account facts.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import re
import sys


def project(entries, smoke):
    entries = copy.deepcopy(entries)
    cwd = next(e["frame"]["params"]["cwd"] for e in entries
               if e.get("frame", {}).get("method") == "thread/start")
    private = {}
    for e in entries:
        f = e.get("frame", {})
        if f.get("method") == "remoteControl/status/changed":
            private[f["params"]["serverName"]] = "scrubbed-host"
            private[f["params"]["installationId"]] = "scrubbed-installation"

    def scrub(value, key=""):
        if isinstance(value, dict):
            return {k: scrub(v, k) for k, v in value.items()}
        if isinstance(value, list):
            return [scrub(v) for v in value]
        if isinstance(value, str):
            if key == "userAgent":
                return value.split(" (", 1)[0] + " (scrubbed; unix)"
            for old, new in private.items():
                value = value.replace(old, new)
            value = value.replace(cwd, "{{CWD}}")
            return re.sub(r"/Users/[^/\s\"']+", "/home/replay-user", value)
        return value

    calls = []
    started = set()
    for e in entries:
        f = e.get("frame", {})
        if f.get("method") == "turn/start" and e["type"] == "expect_outbound":
            p = f["params"]
            thread = p["threadId"]
            args = {"prompt": p["input"][0]["text"]}
            if thread in started:
                name = "codex-reply"
                args["threadId"] = thread
            else:
                name = "codex"
                args.update(cwd=cwd, sandbox="read-only")
                started.add(thread)
            calls.append({"name": name, "arguments": args,
                          "expected": smoke[f"turn{len(calls) + 1}"]["result"]})
        if f.get("method") == "account/updated":
            f["params"] = {}
        elif f.get("method") == "account/rateLimits/updated":
            f["params"] = {"rateLimits": {}}
    entries[0]["metadata"]["calls"] = calls
    entries[0]["metadata"]["projection"] = (
        "scrub_recording.py: fixed host/installation/account/rate-limit/OS/home "
        "placeholders and {{CWD}}; calls reconstructed from live_smoke.py's "
        "recorded turn inputs, with results from smoke.json. No protocol frames removed."
    )
    return scrub(entries)


if __name__ == "__main__":
    source, results, target = map(Path, sys.argv[1:])
    entries = [json.loads(line) for line in source.read_text().splitlines()]
    output = project(entries, json.loads(results.read_text()))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("".join(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n" for e in output))
