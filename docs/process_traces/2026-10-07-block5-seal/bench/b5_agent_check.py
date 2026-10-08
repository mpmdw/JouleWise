#!/usr/bin/env python3
"""Which agent processes would make the next window's census refuse, seen from inside or outside a session.

Desk helper for the post-seal runbook (step A9) and the magistrate brief (sections 5.1, 5.5 and 5.7); it is
not part of the repository and it signals nothing. Feed it the output of the window's own census command:

    cd "$MEASUREMENT_ROOT" && /usr/bin/pgrep -a -lf '[c]odex|[c]laude' | "$PY" -B "$BENCH/b5_agent_check.py"

It decides each listed process with the repository's own matcher (joulewise.agent_identity), the code the
driver's census uses at t0, and sorts the agent hits into three groups:

* own_session_pid: the Claude session this command runs inside (the nearest ancestor the matcher calls an
  agent), or null when it is run from a plain terminal. That session and its MCP servers end with it.
* foreign_agents: agent hits outside that session's process tree and process group: another session, an
  application's helper, or a seat that was started in its own session. Each is still alive after this session
  exits, and the window refuses on it.
* own_seats_still_running: agent hits inside the tree or its process group, other than the session and its MCP
  servers (a Codex or Claude seat this session started, including one whose launching shell has exited). They
  outlive the session's exit as orphans, so they must be stopped first.

Exit 0 when both lists are empty, 1 otherwise. A process that exits between the listing and the reading is
reported as foreign with executable null; run the command again.

Tested 2026-10-07 at int5 9395cecfb with stand-ins (/bin/sleep started under the name codex-standin-*): a child
of the calling shell and an orphan that kept the session's process group are listed under
own_seats_still_running; one started in its own session with launchd as parent is listed under foreign_agents;
exit 1 in each case and exit 0 once they are gone.
"""
from __future__ import annotations

import json
import os
import sys

try:
    from joulewise import agent_identity as a
except ModuleNotFoundError:  # run with a bare interpreter from the checkout's directory
    sys.path.insert(0, os.getcwd())
    from joulewise import agent_identity as a


def own_session() -> int | None:
    pid = os.getppid()
    while pid and pid > 1:
        info = a.inspect(pid)
        if info is None:
            return None
        if a.identify(info.executable, info.argv) == "agent":
            return pid
        pid = info.ppid
    return None


def main() -> int:
    root = own_session()
    kept = a.filter_census(sys.stdin.read()).kept

    def inside(row: dict) -> bool:
        return root is not None and bool(row["pid"]) and a.in_tree(row["pid"], root)

    def command(row: dict) -> str:
        info = a.inspect(row["pid"]) if row["pid"] else None
        return " ".join(getattr(info, "argv", None) or ())

    foreign = [row for row in kept if not inside(row)]
    seats = [row for row in kept if inside(row) and row["pid"] != root and "mcp-server" not in command(row)]
    print(json.dumps({"own_session_pid": root, "foreign_agents": foreign, "own_seats_still_running": seats},
                     indent=1))
    return 1 if foreign or seats else 0


if __name__ == "__main__":
    sys.exit(main())
