"""Run the per-session analyses as a two-level DAG.

``docs/design/analysis_cadence_plan.md`` §2.3: the ALPHA and BETA sessions
are independent and run in parallel; each GAMMA session waits only on its
paired floor sessions (§6.2); the between-session lines run last, in the
caller.  ``workers=1`` runs every node serially in this process.  Results are
keyed by node and the caller assembles them in registered order, so serial and
parallel scheduling produce the same bytes.

Every adapter call runs with its Python and descriptor-level stdout and stderr
sent to restricted log files under the node's custody directory: no byte an L9
program prints reaches a public stream.
"""
from __future__ import annotations

import os
import sys
import traceback
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path

from joulewise.b6.analysis.adapter import COMPLETED, AdapterRefusal, SessionAnalysis, SessionRequest

FLOOR, GAMMA, BLOCK5 = "floor", "gamma", "block5"


@dataclass(frozen=True)
class Node:
    kind: str                        # FLOOR, GAMMA or BLOCK5
    request: SessionRequest
    depends: tuple[str, ...] = ()    # node ids: for GAMMA, (alpha floor, beta floor)
    sessions: tuple[str, ...] = ()   # block-6 sessions whose bytes the node reads (restored around it)

    @property
    def id(self) -> str:
        return node_id(self.kind, self.request.pack, self.request.session_id)


def node_id(kind: str, pack: str, session_id: str) -> str:
    return f"{kind}:{pack}:{session_id}"


def node_custody(custody: Path, node: Node) -> Path:
    return Path(custody) / "sessions" / node.request.pack / node.request.session_id


def _refused(node: Node, code: str, status: str = "tooling_refusal") -> SessionAnalysis:
    return SessionAnalysis(node.request.session_id, node.request.pack, status, code=code)


def run_node(adapter, node: Node, deps: tuple[SessionAnalysis, ...], custody: Path) -> SessionAnalysis:
    """Run one node with its streams in restricted custody.  Never raises."""
    directory = node_custody(custody, node)
    directory.mkdir(parents=True, exist_ok=True)
    logs = directory / "logs"
    logs.mkdir(exist_ok=True)
    sys.stdout.flush()
    sys.stderr.flush()
    with (logs / "stdout.log").open("a", encoding="utf-8", errors="backslashreplace") as out, \
         (logs / "stderr.log").open("a", encoding="utf-8", errors="backslashreplace") as err:
        saved = os.dup(1), os.dup(2)
        try:
            os.dup2(out.fileno(), 1)
            os.dup2(err.fileno(), 2)
            with redirect_stdout(out), redirect_stderr(err):
                try:
                    if node.kind == BLOCK5:
                        result = adapter.block5_session(node.request.pack, directory)
                    elif node.kind == FLOOR:
                        result = adapter.analyse_floor_session(node.request, directory)
                    else:
                        alpha, beta = deps
                        result = adapter.analyse_gamma_session(node.request, alpha, beta, directory)
                    if (not isinstance(result, SessionAnalysis) or result.session_id != node.request.session_id
                            or result.pack != node.request.pack):
                        result = _refused(node, "adapter_result_not_for_session")
                except AdapterRefusal as exc:
                    result = _refused(node, exc.code)
                except Exception:
                    traceback.print_exc()
                    result = _refused(node, "adapter_exception")
                finally:
                    out.flush()
                    err.flush()
        finally:
            try:
                os.dup2(saved[0], 1)
                os.dup2(saved[1], 2)
            finally:
                os.close(saved[0])
                os.close(saved[1])
    return result


def _ready(node: Node, results: dict) -> tuple[bool, SessionAnalysis | None]:
    """Whether a node can run, or the not-run result its failed inputs give it."""
    if any(d not in results for d in node.depends):
        return False, None
    if any(results[d].status not in COMPLETED for d in node.depends):
        return True, _refused(node, "paired_floor_not_analysed", "not_run")
    return True, None


def execute(adapter, nodes: tuple[Node, ...], custody: Path, *, workers: int = 1,
            lifecycle=None, initial: dict | None = None) -> dict[str, SessionAnalysis]:
    """Run every node once its dependencies finish; return results by node id.

    ``lifecycle`` (``restore.Lifecycle``) restores a node's sessions before it
    runs and re-compresses each session after its last node, in this process.
    """
    ids = [n.id for n in nodes]
    known = set(ids) | set(initial or {})
    if len(ids) != len(set(ids)) or set(ids) & set(initial or {}) or any(d not in known for n in nodes for d in n.depends):
        raise ValueError("analysis graph malformed")
    if type(workers) is not int or workers < 1:
        raise ValueError("workers must be a positive integer")
    pending = list(nodes)
    results: dict[str, SessionAnalysis] = dict(initial or {})

    def finish(node, result):
        results[node.id] = result
        if lifecycle is not None:
            lifecycle.release(node.sessions)

    def take_ready():
        ready = []
        for node in list(pending):
            runnable, stand_in = _ready(node, results)
            if not runnable:
                continue
            pending.remove(node)
            if stand_in is None and lifecycle is not None:
                code = lifecycle.acquire(node.sessions)
                if code is not None:
                    stand_in = _refused(node, code)
            if stand_in is not None:
                finish(node, stand_in)
            else:
                ready.append(node)
        return ready

    if workers == 1:
        while pending:
            settled = len(results)
            ready = take_ready()
            if not ready and len(results) == settled:
                raise ValueError("analysis graph has a cycle")
            for node in ready:
                finish(node, run_node(adapter, node, tuple(results[d] for d in node.depends), custody))
        return results

    with ProcessPoolExecutor(max_workers=workers) as pool:
        running = {}
        while pending or running:
            settled = len(results)
            for node in take_ready():
                future = pool.submit(run_node, adapter, node, tuple(results[d] for d in node.depends), custody)
                running[future] = node
            if not running:
                if pending and len(results) == settled:
                    raise ValueError("analysis graph has a cycle")
                # Stand-ins resolved without running anything; look again.
                continue
            done, _ = wait(running, return_when=FIRST_COMPLETED)
            for future in done:
                node = running.pop(future)
                try:
                    result = future.result()
                except Exception:
                    # A worker that died cannot report; its node is a refusal.
                    result = _refused(node, "worker_failed")
                finish(node, result)
    return results
