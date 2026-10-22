"""Validate projections against an external first-party app-server schema dir.

Adapted from t3code (MIT, T3 Tools Inc.), commit defb7e6e, packages/effect-codex-app-server/src/replay.ts
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tests.test_codex_mcp_server import validate


def annotations_removed(value):
    if isinstance(value, dict):
        return {k: annotations_removed(v) for k, v in value.items()
                if k not in ["description", "title", "default", "examples", "$schema"]}
    if isinstance(value, list):
        return [annotations_removed(v) for v in value]
    return value


def main():
    source = Path(sys.argv[1])
    fixtures = Path(__file__).resolve().parent
    roots = {n: annotations_removed(json.loads((source / f"{n}.json").read_text()))
             for n in ["ClientRequest", "ClientNotification", "ServerRequest", "ServerNotification"]}
    names = {
        "initialize": "InitializeResponse", "thread/start": "ThreadStartResponse",
        "thread/resume": "ThreadResumeResponse", "thread/unarchive": "ThreadUnarchiveResponse",
        "turn/start": "TurnStartResponse", "turn/interrupt": "TurnInterruptResponse",
        "item/commandExecution/requestApproval": "CommandExecutionRequestApprovalResponse",
        "item/fileChange/requestApproval": "FileChangeRequestApprovalResponse",
        "item/permissions/requestApproval": "PermissionsRequestApprovalResponse",
        "item/tool/requestUserInput": "ToolRequestUserInputResponse",
        "mcpServer/elicitation/request": "McpServerElicitationRequestResponse",
        "execCommandApproval": "ExecCommandApprovalResponse",
        "applyPatchApproval": "ApplyPatchApprovalResponse",
        "item/tool/call": "DynamicToolCallResponse",
    }
    responses = {method: annotations_removed(json.loads(next(source.rglob(f"{name}.json")).read_text()))
                 for method, name in names.items()}
    frames = 0
    for path in sorted(fixtures.rglob("*.ndjson")):
        pending = {}
        entries = [json.loads(line) for line in path.read_text().splitlines()]
        for entry in entries[1:]:
            if "frame" not in entry or entry.get("label") == "intentional malformed frame":
                continue
            frame = entry["frame"]
            direction = entry["type"]
            opposite = "emit_inbound" if direction == "expect_outbound" else "expect_outbound"
            try:
                if "method" in frame:
                    if "id" in frame:
                        name = "ClientRequest" if direction == "expect_outbound" else "ServerRequest"
                        pending[(direction, frame["id"])] = frame["method"]
                    else:
                        name = "ClientNotification" if direction == "expect_outbound" else "ServerNotification"
                    validate(frame, roots[name])
                else:
                    method = pending.pop((opposite, frame["id"]))
                    if "error" in frame:
                        assert isinstance(frame["error"]["code"], int)
                        assert isinstance(frame["error"]["message"], str)
                    else:
                        validate(frame["result"], responses[method])
            except (AssertionError, KeyError) as error:
                raise AssertionError(f"{path.name}: {entry.get('label', frame.get('id'))}: {error}") from error
            frames += 1
    print(f"PASS: {frames} kept frames validate against the original CLI 0.163.0 schemas; one deliberate malformed frame excluded")


if __name__ == "__main__":
    main()
