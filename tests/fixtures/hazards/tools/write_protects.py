"""Write each hazard module's PROTECTS and SUPERSEDES from configs/gates/physics_rows.json
(provenance tool, not a test).  tests/hazards/test_physics_coverage.py checks the two agree."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MARK = "PROTECTS: tuple[tuple[str, str, str, int], ...] = "


def literal(entries):
    if not entries:
        return "()"
    lines = ["("]
    for entry in entries:
        key = entry["key"]
        checks = " ".join(entry["checks"].split())
        if len(checks) > 84:
            checks = checks[:81].rstrip() + "..."
        lines.append(f"    # base line {entry['line_at_base']}: {checks}")
        lines.append(f"    row({json.dumps(key['file'])}, {json.dumps(key['function'])},\n"
                     f"        {json.dumps(key['code'])}, {key['occurrence']}),")
    lines.append(")")
    return "\n".join(lines)


def main():
    rows = json.loads((ROOT / "configs/gates/physics_rows.json").read_text())["rows"]
    for module in ("clock", "battery", "thermal", "contention", "disk", "instrument", "arm"):
        path = ROOT / "joulewise" / "hazards" / f"{module}.py"
        text = path.read_text()
        head, _sep, _tail = text.partition(MARK)
        protects = [e for e in rows if e["disposition"] == "protects" and e.get("module") == module]
        supersedes = [e for e in rows if e["disposition"] == "retired_proxy" and e.get("module") == module]
        body = (MARK + literal(protects) + "\n\n"
                "# Proxy rows on paths block 5 no longer runs that this module's direct\n"
                "# measurement replaces (configs/gates/physics_rows.json, \"retired_proxy\").\n"
                "SUPERSEDES: tuple[tuple[str, str, str, int], ...] = " + literal(supersedes) + "\n")
        if "from joulewise.hazards.base import" in head and re.search(r"\brow\b", head.split("from joulewise.hazards.base import", 1)[1].split(")", 1)[0]) is None:
            head = head.replace("from joulewise.hazards.base import (", "from joulewise.hazards.base import (\n    row,", 1)
        path.write_text(head + body)
        print(module, len(protects), len(supersedes))


if __name__ == "__main__":
    main()
