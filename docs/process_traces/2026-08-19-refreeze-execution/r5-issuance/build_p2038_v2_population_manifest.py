#!/usr/bin/env python3
"""Enumerate stored p2-038.2 metadata records under a supplied tree."""

from __future__ import annotations

import json
import sys
from pathlib import Path


root = Path(sys.argv[1]).resolve(strict=True)
output = Path(sys.argv[2]).resolve()
members: list[dict[str, str]] = []
for path in root.rglob("metadata.json"):
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        continue
    evidence = value.get("uncertainty_evidence") if isinstance(value, dict) else None
    if not isinstance(evidence, dict) or evidence.get("schema_version") != "p2-038.2":
        continue
    anchor = evidence.get("clock_anchor")
    members.append(
        {
            "path": str(path.relative_to(root)),
            "method": str(anchor.get("method")) if isinstance(anchor, dict) else "<missing>",
        }
    )
payload = {"root": str(root), "schema_version": "p2-038.2", "count": len(members), "members": sorted(members, key=lambda row: row["path"])}
output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
print("P2038_V2_STORED_BUNDLES", len(members))
print("MANIFEST", output)
