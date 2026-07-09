#!/usr/bin/env python3
"""DOC-008 Stage-1 state-kernel generator (docs/specs/c027/doc-008_state_kernel.md).

Stdlib-only. Validates docs/process/state_kernel.json, canonicalizes it,
and renders the RUN_STATE intake/restart region and the TASK_QUEUE current
queue region between marker fences.

Modes:
  python3 scripts/gen_state.py                 generate (replace marker interiors)
  python3 scripts/gen_state.py --check         read-only drift/validity check
  python3 scripts/gen_state.py --stdout NAME   render one fragment (run-state|queue)

Exit codes: 0 exact agreement / success; 1 drift; 2 invalid input or markers.

NOTE (Stage-1 tooling landing): the live RUN_STATE.md / TASK_QUEUE.md have
NOT yet been converted to marker fences — that migration is adjudication
gated. Until then, run --check with explicit --run-state/--queue paths
(tests do this against generator-produced fixtures).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

KERNEL_REL = "docs/process/state_kernel.json"
SCHEMA_REL = "docs/process/state_kernel.schema.json"

RS_BEGIN = "<!-- BEGIN GENERATED: state-kernel run-state-intake -->"
RS_END = "<!-- END GENERATED: state-kernel run-state-intake -->"
Q_BEGIN = "<!-- BEGIN GENERATED: state-kernel current-queue -->"
Q_END = "<!-- END GENERATED: state-kernel current-queue -->"

LANES = ("ed_external", "quiet_mac", "agent")
LANE_LABEL = {"ed_external": "[ED-EXTERNAL]", "quiet_mac": "[QUIET-MAC]", "agent": "[AGENT]"}
LANE_PREFIX = {"ed_external": "E", "quiet_mac": "Q", "agent": "A"}
PRIORITIES = {
    "p0_safety": "P0 Safety",
    "p1_phase_gate": "P1 Phase Gate",
    "p2_next_slice": "P2 Next Slice",
    "p3_research_expansion": "P3 Research Expansion",
    "p4_polish": "P4 Polish",
}
STATUSES = ("queued", "active", "partial", "blocked", "shelved")
FLAGS = (
    "blocked_post_2m",
    "lead_only",
    "migration_inferred_lane",
    "mixed_lane_migrated",
    "pre_window_a_gate",
    "provisional_until_live",
)
DEP_KINDS = ("task", "artifact", "decision", "external", "event")
DEP_STATES = ("pending", "satisfied")
DEP_STRENGTHS = ("hard", "advisory")
DEP_SCOPES = ("start", "retain_evidence", "interpret", "close", "live_promotion")

ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.-]*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class KernelError(Exception):
    """Fatal validation error (exit 2)."""


def fail(msg: str) -> None:
    raise KernelError(msg)


# ---------------------------------------------------------------------------
# Canonical bytes
# ---------------------------------------------------------------------------

def canonical_bytes(obj) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _check_keys(obj: dict, required: set, optional: set, where: str) -> None:
    if not isinstance(obj, dict):
        fail(f"{where}: expected object")
    keys = set(obj)
    missing = required - keys
    unknown = keys - required - optional
    if missing:
        fail(f"{where}: missing fields {sorted(missing)}")
    if unknown:
        fail(f"{where}: unknown fields {sorted(unknown)}")


def _check_cell_text(value: str, where: str) -> None:
    if not isinstance(value, str) or not value.strip():
        fail(f"{where}: must be a nonempty string")
    if "\n" in value or "|" in value:
        fail(f"{where}: table-rendered strings may not contain newlines or '|'")


def _gfm_slug(heading: str) -> str:
    text = heading.strip().lstrip("#").strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def _resolve_json_pointer(doc, pointer: str, where: str) -> None:
    node = doc
    for raw in pointer.lstrip("/").split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, dict):
            if token not in node:
                fail(f"{where}: json_pointer {pointer!r} does not resolve")
            node = node[token]
        elif isinstance(node, list):
            try:
                node = node[int(token)]
            except (ValueError, IndexError):
                fail(f"{where}: json_pointer {pointer!r} does not resolve")
        else:
            fail(f"{where}: json_pointer {pointer!r} does not resolve")


def _check_pointer(ptr, where: str, kernel_obj) -> None:
    _check_keys(ptr, {"path", "label"}, {"anchor", "json_pointer"}, where)
    path = ptr["path"]
    if not isinstance(path, str) or not path:
        fail(f"{where}: path must be a nonempty string")
    if path.startswith("/") or path.startswith("~") or ".." in path.split("/") or "://" in path:
        fail(f"{where}: path must be repo-relative POSIX without escapes: {path!r}")
    target = os.path.join(ROOT, *path.split("/"))
    if not os.path.isfile(target):
        fail(f"{where}: pointer target does not exist: {path!r}")
    _check_cell_text(ptr["label"], f"{where}.label")
    if "anchor" in ptr and "json_pointer" in ptr:
        fail(f"{where}: anchor and json_pointer are mutually exclusive")
    if "anchor" in ptr:
        anchor = ptr["anchor"]
        if not isinstance(anchor, str) or not anchor or anchor.startswith("#"):
            fail(f"{where}: anchor must be a GFM fragment without '#'")
        with open(target, encoding="utf-8") as fh:
            slugs = {_gfm_slug(line) for line in fh if line.startswith("#")}
        if anchor not in slugs:
            fail(f"{where}: anchor {anchor!r} not found in {path!r}")
    if "json_pointer" in ptr:
        jp = ptr["json_pointer"]
        if not isinstance(jp, str) or not jp.startswith("/"):
            fail(f"{where}: json_pointer must begin with '/'")
        if path == KERNEL_REL:
            doc = kernel_obj
        else:
            try:
                with open(target, encoding="utf-8") as fh:
                    doc = json.load(fh)
            except (OSError, ValueError):
                fail(f"{where}: json_pointer target {path!r} is not readable JSON")
        _resolve_json_pointer(doc, jp, where)


def _check_dependency(dep, where: str, kernel) -> None:
    _check_keys(
        dep,
        {"kind", "target", "required", "state", "strength", "scope", "evidence"},
        {"note"},
        where,
    )
    if dep["kind"] not in DEP_KINDS:
        fail(f"{where}: bad kind {dep['kind']!r}")
    if not isinstance(dep["target"], str) or not dep["target"]:
        fail(f"{where}: target must be a nonempty string")
    _check_cell_text(dep["required"], f"{where}.required")
    if dep["state"] not in DEP_STATES:
        fail(f"{where}: bad state {dep['state']!r}")
    if dep["strength"] not in DEP_STRENGTHS:
        fail(f"{where}: bad strength {dep['strength']!r}")
    if dep["scope"] not in DEP_SCOPES:
        fail(f"{where}: bad scope {dep['scope']!r}")
    if dep["state"] == "satisfied":
        if dep["evidence"] is None:
            fail(f"{where}: satisfied dependency requires evidence")
        _check_pointer(dep["evidence"], f"{where}.evidence", kernel)
    else:
        if dep["evidence"] is not None:
            fail(f"{where}: pending dependency must have null evidence")
    if "note" in dep:
        _check_cell_text(dep["note"], f"{where}.note")


DEP_SORT_KEY = lambda d: (d["scope"], d["strength"], d["kind"], d["target"], d["required"])
FENCE_SORT_KEY = lambda f: (f["rule"], f["authority"]["path"], f["authority"]["label"])


def validate(kernel) -> None:
    _check_keys(
        kernel,
        {"schema", "schema_version", "updated", "latest_report", "active_stop_card", "tasks"},
        set(),
        "kernel",
    )
    if kernel["schema"] != SCHEMA_REL:
        fail(f"kernel.schema must be {SCHEMA_REL!r}")
    if kernel["schema_version"] != 1:
        fail("kernel.schema_version must be 1")
    if not isinstance(kernel["updated"], str) or not DATE_RE.match(kernel["updated"]):
        fail("kernel.updated must be YYYY-MM-DD")
    _check_pointer(kernel["latest_report"], "kernel.latest_report", kernel)
    if kernel["active_stop_card"] is not None:
        _check_pointer(kernel["active_stop_card"], "kernel.active_stop_card", kernel)
        card_path = kernel["active_stop_card"]["path"]
        if not card_path.startswith("docs/stop_cards/"):
            fail("kernel.active_stop_card must point into docs/stop_cards/")
    tasks = kernel["tasks"]
    if not isinstance(tasks, dict):
        fail("kernel.tasks must be an object keyed by task ID")

    lane_ranks: dict = {}
    for tid, task in tasks.items():
        where = f"tasks[{tid}]"
        _check_keys(
            task,
            {
                "id", "lane", "rank", "priority", "status", "goal", "dependencies",
                "authority", "acceptance", "fences", "fallback", "flags", "stop_card",
            },
            {"status_note"},
            where,
        )
        if task["id"] != tid:
            fail(f"{where}: id {task['id']!r} does not match object key")
        if not ID_RE.match(tid):
            fail(f"{where}: invalid id pattern")
        if task["lane"] not in LANES:
            fail(f"{where}: bad lane {task['lane']!r}")
        rank = task["rank"]
        if not isinstance(rank, int) or isinstance(rank, bool) or rank < 0:
            fail(f"{where}: rank must be a nonnegative integer")
        key = (task["lane"], rank)
        if key in lane_ranks:
            fail(f"{where}: duplicate lane rank {rank} (also {lane_ranks[key]})")
        lane_ranks[key] = tid
        if task["priority"] not in PRIORITIES:
            fail(f"{where}: bad priority {task['priority']!r}")
        if task["status"] not in STATUSES:
            fail(f"{where}: bad status {task['status']!r} (terminal statuses are not live)")
        _check_cell_text(task["goal"], f"{where}.goal")
        if "status_note" in task:
            _check_cell_text(task["status_note"], f"{where}.status_note")
        deps = task["dependencies"]
        if not isinstance(deps, list):
            fail(f"{where}.dependencies: must be an array")
        for i, dep in enumerate(deps):
            _check_dependency(dep, f"{where}.dependencies[{i}]", kernel)
            if dep["kind"] == "task" and dep["target"] == tid:
                fail(f"{where}: self-dependency")
            if dep["kind"] == "task" and dep["state"] == "pending" and dep["target"] not in tasks:
                fail(f"{where}: pending task dependency names non-live task {dep['target']!r}")
        if [DEP_SORT_KEY(d) for d in deps] != sorted(DEP_SORT_KEY(d) for d in deps):
            fail(f"{where}.dependencies: not in canonical sort order")
        _check_pointer(task["authority"], f"{where}.authority", kernel)
        acc = task["acceptance"]
        _check_keys(acc, {"summary", "pointer", "evidence"}, set(), f"{where}.acceptance")
        _check_cell_text(acc["summary"], f"{where}.acceptance.summary")
        _check_pointer(acc["pointer"], f"{where}.acceptance.pointer", kernel)
        if not isinstance(acc["evidence"], list) or not acc["evidence"]:
            fail(f"{where}.acceptance.evidence: must be a nonempty string array")
        for i, item in enumerate(acc["evidence"]):
            _check_cell_text(item, f"{where}.acceptance.evidence[{i}]")
        fences = task["fences"]
        if not isinstance(fences, list):
            fail(f"{where}.fences: must be an array")
        for i, fence in enumerate(fences):
            _check_keys(fence, {"rule", "authority"}, set(), f"{where}.fences[{i}]")
            _check_cell_text(fence["rule"], f"{where}.fences[{i}].rule")
            _check_pointer(fence["authority"], f"{where}.fences[{i}].authority", kernel)
        if [FENCE_SORT_KEY(f) for f in fences] != sorted(FENCE_SORT_KEY(f) for f in fences):
            fail(f"{where}.fences: not in canonical sort order")
        fb = task["fallback"]
        if fb is not None:
            _check_keys(fb, {"condition", "action", "pointer"}, set(), f"{where}.fallback")
            _check_cell_text(fb["condition"], f"{where}.fallback.condition")
            _check_cell_text(fb["action"], f"{where}.fallback.action")
            _check_pointer(fb["pointer"], f"{where}.fallback.pointer", kernel)
        flags = task["flags"]
        if not isinstance(flags, list):
            fail(f"{where}.flags: must be an array")
        for flag in flags:
            if flag not in FLAGS:
                fail(f"{where}.flags: unknown flag {flag!r}")
        if flags != sorted(set(flags)):
            fail(f"{where}.flags: must be unique and lexically sorted")
        if task["stop_card"] is not None:
            _check_pointer(task["stop_card"], f"{where}.stop_card", kernel)
            if kernel["active_stop_card"] is None or task["stop_card"] != kernel["active_stop_card"]:
                fail(f"{where}.stop_card: must equal top-level active_stop_card")

        # Invariant 3: blocked iff a pending hard start dependency exists (non-shelved).
        hard_start_pending = any(
            d["scope"] == "start" and d["strength"] == "hard" and d["state"] == "pending"
            for d in deps
        )
        if task["status"] != "shelved":
            if task["status"] == "blocked" and not hard_start_pending:
                fail(f"{where}: blocked without a pending hard start dependency")
            if task["status"] != "blocked" and hard_start_pending:
                fail(f"{where}: pending hard start dependency requires status=blocked")

        # Invariant 8: blocked_post_2m needs a P2-006 dependency; P2-022/P2-023 cite D-041.
        if "blocked_post_2m" in flags:
            if not any(d["kind"] == "task" and d["target"] == "P2-006" for d in deps):
                fail(f"{where}: blocked_post_2m requires a P2-006 dependency")
            if tid in ("P2-022", "P2-023") and "D-041" not in task["authority"]["label"]:
                fail(f"{where}: post-2M authority must resolve to D-041")

        # Invariant 9: quiet_mac tasks are labeled lead-controlled.
        if task["lane"] == "quiet_mac" and "lead_only" not in flags:
            fail(f"{where}: quiet_mac tasks must carry the lead_only flag")

    # Invariant 7: active stop card must be referenced by an active/blocked task.
    if kernel["active_stop_card"] is not None:
        if not any(
            t["stop_card"] is not None and t["status"] in ("active", "blocked")
            for t in tasks.values()
        ):
            fail("active_stop_card set but no active/blocked task points to it")

    # Invariant 4: pending hard task edges are acyclic across all scopes.
    edges = {
        tid: [
            d["target"]
            for d in task["dependencies"]
            if d["kind"] == "task" and d["state"] == "pending" and d["strength"] == "hard"
            and d["target"] in tasks
        ]
        for tid, task in tasks.items()
    }
    state: dict = {}

    def visit(node: str, stack: tuple) -> None:
        if state.get(node) == "done":
            return
        if state.get(node) == "in":
            fail(f"dependency cycle: {' -> '.join(stack + (node,))}")
        state[node] = "in"
        for nxt in edges[node]:
            visit(nxt, stack + (node,))
        state[node] = "done"

    for tid in tasks:
        visit(tid, ())


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def _link(ptr) -> str:
    path = ptr["path"]
    if "anchor" in ptr:
        return f"[{ptr['label']}]({path}#{ptr['anchor']})"
    return f"[{ptr['label']}]({path})"


def _lane_tasks(kernel, lane: str):
    return sorted(
        (t for t in kernel["tasks"].values() if t["lane"] == lane),
        key=lambda t: (t["rank"], t["id"]),
    )


def _hard_start_blockers(task):
    return [
        d for d in task["dependencies"]
        if d["scope"] == "start" and d["strength"] == "hard" and d["state"] == "pending"
    ]


def _later_scope_gates(task):
    return [
        d for d in task["dependencies"]
        if d["scope"] != "start" and d["state"] == "pending"
    ]


def render_run_state(kernel) -> str:
    lines = [RS_BEGIN, "## ACTIVE_STOP_CARD", ""]
    card = kernel["active_stop_card"]
    if card is None:
        lines.append(
            "Status: NONE — no stop card is active. Stop-card authority: D-050 / D-063"
            " ([decision log](docs/decision_log.md))."
        )
    else:
        affected = sorted(
            t["id"] for t in kernel["tasks"].values() if t["stop_card"] is not None
        )
        lines.append(f"Status: ACTIVE — {_link(card)}.")
        lines.append("")
        lines.append(f"Affected tasks: {', '.join(affected)}.")
        lines.append("")
        lines.append("Normal lane selection is SUSPENDED; follow only the card.")
    lines += ["", "## Restart By Machine-State Lane", ""]
    lines.append(
        f"Source of truth: [state kernel]({KERNEL_REL}) (updated {kernel['updated']})."
        f" Latest report: {_link(kernel['latest_report'])}."
    )
    if card is None:
        for lane in LANES:
            lines += ["", f"### {LANE_LABEL[lane]}", ""]
            tasks = [t for t in _lane_tasks(kernel, lane) if t["status"] != "shelved"]
            if not tasks:
                lines.append("- NONE — no live task in this lane.")
                continue
            active = [t for t in tasks if t["status"] == "active"]
            if active:
                for t in active:
                    lines.append(
                        f"- CONTINUE — {LANE_PREFIX[lane]}{t['rank']} `{t['id']}`: {t['goal']}"
                    )
                continue
            ready = [
                t for t in tasks
                if t["status"] in ("queued", "partial") and not _hard_start_blockers(t)
            ]
            if ready:
                t = ready[0]
                lines.append(
                    f"- READY — {LANE_PREFIX[lane]}{t['rank']} `{t['id']}`: {t['goal']}"
                )
                continue
            blocked = [t for t in tasks if t["status"] == "blocked"]
            if blocked:
                t = blocked[0]
                blockers = ", ".join(d["target"] for d in _hard_start_blockers(t))
                lines.append(
                    f"- BLOCKED — {LANE_PREFIX[lane]}{t['rank']} `{t['id']}`"
                    f" (blocked on: {blockers}): {t['goal']}"
                )
            else:
                lines.append("- NONE — no live task in this lane.")
    lines += ["", RS_END]
    return "\n".join(lines) + "\n"


def _queue_state_cell(task) -> str:
    status = task["status"]
    if status == "active":
        base = "ACTIVE"
    elif status == "queued":
        base = "READY"
    elif status == "partial":
        base = "PARTIAL; READY"
    elif status == "blocked":
        blockers = ", ".join(
            f"{d['target']} ({d['required']})" for d in _hard_start_blockers(task)
        )
        base = f"BLOCKED — {blockers}"
    else:  # shelved
        triggers = ", ".join(
            f"{d['target']} ({d['required']})" for d in task["dependencies"]
            if d["state"] == "pending"
        )
        base = f"SHELVED — trigger: {triggers}" if triggers else "SHELVED"
    gates = _later_scope_gates(task)
    if gates and status != "blocked":
        gate_bits = "; ".join(
            f"GATES {d['scope']}: {d['target']}" for d in gates
        )
        base = f"{base}; {gate_bits}"
    return base


def _evidence_cell(task) -> str:
    acc = task["acceptance"]
    bits = [acc["summary"]]
    bits.append(f"Evidence: {'; '.join(acc['evidence'])}.")
    bits.append(f"Authority: {_link(task['authority'])}.")
    bits.append(f"Acceptance: {_link(acc['pointer'])}.")
    for fence in task["fences"]:
        bits.append(f"Fence: {fence['rule']} ({fence['authority']['label']}).")
    if task["fallback"] is not None:
        fb = task["fallback"]
        bits.append(f"Fallback: if {fb['condition']}, {fb['action']} ({_link(fb['pointer'])}).")
    if task.get("status_note"):
        bits.append(f"Note: {task['status_note']}")
    return " ".join(bits)


def render_queue(kernel) -> str:
    lines = [
        Q_BEGIN,
        "<!-- GENERATED from docs/process/state_kernel.json by scripts/gen_state.py."
        " Do NOT hand-edit between the markers; edit the kernel and regenerate. -->",
        "",
    ]
    header = "| Rank | ID | Priority | Queue state | Task | Evidence / Acceptance |"
    divider = "|---|---|---|---|---|---|"
    for lane in LANES:
        live = [t for t in _lane_tasks(kernel, lane) if t["status"] != "shelved"]
        lines += [f"### {LANE_LABEL[lane]} lane", ""]
        if live:
            lines += [header, divider]
            for t in live:
                lines.append(
                    f"| {LANE_PREFIX[lane]}{t['rank']} | {t['id']} |"
                    f" {PRIORITIES[t['priority']]} | {_queue_state_cell(t)} |"
                    f" {t['goal']} | {_evidence_cell(t)} |"
                )
        else:
            lines.append("(no live tasks)")
        lines.append("")
    shelved = sorted(
        (t for t in kernel["tasks"].values() if t["status"] == "shelved"),
        key=lambda t: (t["lane"], t["rank"], t["id"]),
    )
    lines += ["### Shelved task records", ""]
    if shelved:
        lines += [header, divider]
        for t in shelved:
            lines.append(
                f"| {LANE_PREFIX[t['lane']]}{t['rank']} | {t['id']} |"
                f" {PRIORITIES[t['priority']]} | {_queue_state_cell(t)} |"
                f" {t['goal']} | {_evidence_cell(t)} |"
            )
    else:
        lines.append("(none)")
    lines += ["", Q_END]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Marker replacement
# ---------------------------------------------------------------------------

def _find_region(text: str, begin: str, end: str, path: str):
    starts = [m.start() for m in re.finditer(re.escape(begin), text)]
    ends = [m.start() for m in re.finditer(re.escape(end), text)]
    if len(starts) != 1 or len(ends) != 1:
        fail(f"{path}: expected exactly one {begin!r}/{end!r} marker pair"
             f" (found {len(starts)}/{len(ends)})")
    if ends[0] < starts[0]:
        fail(f"{path}: reversed markers")
    region_end = ends[0] + len(end)
    if text[region_end:region_end + 1] not in ("", "\n"):
        fail(f"{path}: end marker must terminate its line")
    return starts[0], region_end


def replace_region(text: str, rendered: str, begin: str, end: str, path: str) -> str:
    start, stop = _find_region(text, begin, end, path)
    return text[:start] + rendered.rstrip("\n") + text[stop:]


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except OSError as exc:
        fail(f"cannot read {path}: {exc}")


def _atomic_write(path: str, data: bytes) -> None:
    directory = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=directory, prefix=".gen_state.")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def load_kernel(path: str):
    raw = _read(path)
    try:
        kernel = json.loads(raw)
    except ValueError as exc:
        fail(f"{path}: invalid JSON: {exc}")
    validate(kernel)
    return kernel, raw.encode("utf-8")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--stdout", choices=("run-state", "queue"))
    parser.add_argument("--kernel", default=os.path.join(ROOT, *KERNEL_REL.split("/")))
    parser.add_argument("--run-state", default=os.path.join(ROOT, "RUN_STATE.md"))
    parser.add_argument("--queue", default=os.path.join(ROOT, "TASK_QUEUE.md"))
    args = parser.parse_args(argv)

    try:
        kernel, raw = load_kernel(args.kernel)
        canonical = canonical_bytes(kernel)

        if args.stdout:
            fragment = render_run_state(kernel) if args.stdout == "run-state" else render_queue(kernel)
            sys.stdout.write(fragment)
            return 0

        targets = (
            (args.run_state, render_run_state(kernel), RS_BEGIN, RS_END),
            (args.queue, render_queue(kernel), Q_BEGIN, Q_END),
        )

        if args.check:
            drift = False
            if raw != canonical:
                fail(f"{args.kernel}: kernel bytes are not canonical")
            for path, rendered, begin, end in targets:
                text = _read(path)
                if replace_region(text, rendered, begin, end, path) != text:
                    print(f"DRIFT: {path} generated region differs", file=sys.stderr)
                    drift = True
            return 1 if drift else 0

        if raw != canonical:
            _atomic_write(args.kernel, canonical)
        for path, rendered, begin, end in targets:
            text = _read(path)
            updated = replace_region(text, rendered, begin, end, path)
            if updated != text:
                _atomic_write(path, updated.encode("utf-8"))
        return 0
    except KernelError as exc:
        print(f"gen_state: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
