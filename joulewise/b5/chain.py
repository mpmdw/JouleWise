"""Render a block-5 HAZARD_PACK window chain from a v5 pack's stage graph.

The chain is a zsh script the driver (``scripts/run_night.py``, HAZARD_PACK
branch) launches once, after the hazard arm returns GO. It runs the pack's
committed ``plan_tree.json`` stage graph in ordinal order, in the block-3
runbook protocol:

1. the bracket reservation;
2. a settle (``SETTLE_S``, 180 s: the runbook's ``SETTLE_S=180``, registration
   §0.6) before the pre slot;
3. the pre-calibration capture and its fiducial screen;
4. the NEG-8 reference corpus and its bound derivation;
5. the start references;
6. the science stages with their midpoint references;
7. the end references;
8. the post-calibration capture, then a record of the bracket session status.

Each collection stage is preceded by a settle, as in the runbook. The
whole-window verdict and the backups are desk steps and are not rendered.

The only stops, all before member 1, are a failed reservation (exit 10), a
failed pre-calibration capture (exit 11) and a failed pre-calibration screen
(exit 12). The driver stops the chain from outside on low disk. Every other
stage records its return code in ``$NIGHT_DIR/chain-stages.jsonl`` and the
chain continues; a chain that reaches its end exits 0 whatever its stages
returned. Collection stages pass ``--max-failures <expected_count>`` in place
of the pack's literal ``1``, so a failed member costs only itself.

The NEG-8 bound derivation reads a window-local copy of the settled-corpus
manifest that lists only the collected, succeeded members. With all 12 that
copy is byte-identical to the committed manifest. With 10 or 11 the derivation
runs, but its bound artifact names the pruned copy's SHA-256, and the core's
bound consumers (``whole_window.load_neg8_drift_bound_artifact``: the
whole-window verdict and the harvest) authenticate the corpus only against the
committed 12-member bytes. Such a window therefore still ends
``neg8.bound_not_derived`` (EXCLUDE_WINDOW) until a prospective erratum lets a
consumer authenticate against the custodied pruned bytes. The chain keeps those
bytes and a create-once summary (both paths and SHA-256) under
``$NIGHT_DIR/transcript/``; the driver copies the locator into
``night/hazard_result.json`` (``neg8_corpus``).

The rendered bytes carry every value as a literal. They read nothing from the
driver's environment except ``NIGHT_DIR``, and they refuse both inspection
modes (``NIGHT_VERIFY_ONLY``, ``NIGHT_RESERVATION_ARGV_ONLY``) without running
anything, so no legacy probe or installer path can start a capture by running
this file.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shlex
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

CHAIN_SCHEMA = "joulewise.b5_chain.v1"
CHAIN_INTERFACE = "b5-hazard-chain-v1"
# The registered settle: docs/phase_2/window_runbook.md `SETTLE_S=180`, the
# block-5 registration §0.6 and §5.2 ("180 s settle per stage").
SETTLE_S = 180
# The pre-calibration screen is not re-implemented here: the chain embeds the
# runbook's own D-079 clause 3 block (the literal bound and the
# screen_pre_calibration function every live window since block 3 ran),
# read from the measurement checkout's pinned runbook at render time.
RUNBOOK_RELATIVE = "docs/phase_2/window_runbook.md"
RUNBOOK_SCREEN_START = "# D-079 clause 3: pre-flight calibration screen."
RUNBOOK_SCREEN_FUNCTION = "screen_pre_calibration() {"

EXIT_COMPLETED = 0
EXIT_RESERVATION_FAILED = 10
EXIT_PRE_CAPTURE_FAILED = 11
EXIT_PRE_SCREEN_FAILED = 12
EXIT_INSPECTION_REFUSED = 64
STOP_EXITS = {
    "reservation_failed": EXIT_RESERVATION_FAILED,
    "pre_calibration_capture_failed": EXIT_PRE_CAPTURE_FAILED,
    "pre_calibration_screen_failed": EXIT_PRE_SCREEN_FAILED,
}

STAGE_JOURNAL = "chain-stages.jsonl"
NEG8_COLLECTED_MANIFEST = "neg8-settled-corpus.collected.json"
NEG8_COLLECTED_SUMMARY = "neg8-settled-corpus.collected.summary.json"
TERMINAL_BOUNDARY = "post-bracket-terminal-boundary.json"


@dataclasses.dataclass(frozen=True)
class Tool:
    interface_id: str
    runner: str  # "python" (the measurement venv) or "shell"
    program: str  # repository-relative


TOOLS = {
    "bracket_reserver": Tool("joulewise.calibration_window_bracket_reservation.cli.v1", "python",
                             "scripts/reserve_calibration_window_bracket.py"),
    "fiducial_capture": Tool("joulewise.powermetrics_fiducial.cli.v1", "python",
                             "scripts/validate_powermetrics_fiducial.py"),
    "campaign_runner": Tool("joulewise.run_campaign.cli.v1", "python", "scripts/run_campaign.py"),
    "backup_runs": Tool("joulewise.backup_runs.cli.v1", "shell", "scripts/backup_runs.sh"),
}
IN_CHAIN_KINDS = ("bracket_reservation", "calibration_capture", "campaign_collection", "bound_derivation")
DESK_KINDS = ("whole_window_verdict", "backup")
ARGUMENT_KINDS = ("literal", "binding", "binding_path", "repo_path", "tree_pointer")
# The runbook's calibrate_slot passes these two to every live capture since
# block 3; the pack's generated capture template predates that protocol.
CALIBRATION_RUNBOOK_FLAGS = ("--arm-countdown-s", "20", "--sleep-display-before-capture")

DEVIATIONS = (
    "campaign_collection stages pass --max-failures <stage expected_count> in place of the pack's "
    "literal 1, so a failed member costs only itself (gate-prune plan L2; registration edit 14)",
    "calibration_capture stages add --arm-countdown-s 20 --sleep-display-before-capture, the "
    "block-3 runbook calibrate_slot protocol every live window has used",
    "bound_derivation reads a window-local copy of the settled-corpus manifest listing only the "
    "collected, succeeded corpus members (byte-identical when all 12 succeeded). With 10 or 11 of 12 "
    "the derivation runs (whole_window.NEG8_DRIFT_MINIMUM_N = 10), but the bound names the pruned "
    "copy's SHA-256 and the core consumers (whole_window.load_neg8_drift_bound_artifact: the "
    "whole-window verdict, the harvest) authenticate only the committed 12-member bytes, so the "
    "window still ends neg8.bound_not_derived (EXCLUDE_WINDOW) until a prospective erratum lets a "
    "consumer authenticate the custodied pruned bytes (locator: night/hazard_result.json neg8_corpus)",
    "whole_window_verdict and backup stages are desk steps and are not in the chain",
)

_IDENTIFIER_RE = re.compile(r"[A-Za-z0-9._-]+")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


class ChainRenderError(ValueError):
    """The stage graph cannot be rendered into a chain; nothing was written."""


@dataclasses.dataclass(frozen=True)
class Command:
    command_id: str
    tool_id: str
    interface_id: str
    arguments: tuple[Mapping[str, Any], ...]
    cwd_binding: str
    success_exit_codes: tuple[int, ...]


@dataclasses.dataclass(frozen=True)
class Stage:
    stage_id: str
    ordinal: int
    kind: str
    expected_count: int
    commands: tuple[Command, ...]
    in_chain: bool
    slot: str | None  # "pre" / "post" for calibration captures

    def summary(self) -> dict[str, Any]:
        return {"stage_id": self.stage_id, "kind": self.kind, "ordinal": self.ordinal,
                "expected_count": self.expected_count, "in_chain": self.in_chain}


def _require(condition: bool, detail: str) -> None:
    if not condition:
        raise ChainRenderError(detail)


def _identifier(value: Any, where: str) -> str:
    _require(isinstance(value, str) and _IDENTIFIER_RE.fullmatch(value) is not None,
             f"{where} must match [A-Za-z0-9._-]+")
    return value


def _relative(value: Any, where: str) -> str:
    _require(isinstance(value, str) and value != "", f"{where} must be a non-empty string")
    path = PurePosixPath(value)
    _require(not path.is_absolute() and ".." not in path.parts and "\0" not in value,
             f"{where} must be a relative path without '..'")
    return value


def stage_plan(tree: Mapping[str, Any]) -> list[Stage]:
    """Walk a v5 plan tree's stage graph in ordinal order and validate its shape.

    The graph must be one predecessor/successor chain whose first stage is the
    bracket reservation, with exactly one pre and one post calibration capture
    bracketing every collection, and one bound derivation after the corpus.
    """

    graph = tree.get("stage_graph") if isinstance(tree, Mapping) else None
    _require(isinstance(graph, list) and bool(graph), "plan tree has no stage_graph")
    stages: list[Stage] = []
    for index, row in enumerate(graph):
        where = f"stage_graph[{index}]"
        _require(isinstance(row, Mapping), where + " must be an object")
        stage_id = _identifier(row.get("stage_id"), where + ".stage_id")
        kind = row.get("kind")
        _require(kind in IN_CHAIN_KINDS + DESK_KINDS, f"{stage_id}: unknown stage kind {kind!r}")
        ordinal = row.get("ordinal")
        _require(type(ordinal) is int and ordinal >= 1, f"{stage_id}: ordinal must be an integer >= 1")
        expected = row.get("expected_count")
        _require(type(expected) is int and expected >= 0, f"{stage_id}: expected_count must be an integer >= 0")
        launch = row.get("launch")
        _require(isinstance(launch, Mapping) and launch.get("schema_version") == "joulewise.stage_launch.v1",
                 f"{stage_id}: launch must be joulewise.stage_launch.v1")
        rows = launch.get("commands")
        _require(isinstance(rows, list) and bool(rows), f"{stage_id}: launch has no commands")
        commands = []
        for position, command in enumerate(rows):
            cwhere = f"{stage_id}.commands[{position}]"
            _require(isinstance(command, Mapping), cwhere + " must be an object")
            template = command.get("argv_template")
            _require(isinstance(template, Mapping), cwhere + " has no argv_template")
            tool_id = template.get("tool_id")
            _require(tool_id in TOOLS, f"{cwhere}: unknown tool {tool_id!r}")
            interface_id = template.get("interface_id")
            _require(interface_id == TOOLS[tool_id].interface_id,
                     f"{cwhere}: {tool_id} interface {interface_id!r} is not {TOOLS[tool_id].interface_id}")
            arguments = template.get("arguments")
            _require(isinstance(arguments, list), cwhere + " arguments must be a list")
            for argument in arguments:
                _require(isinstance(argument, Mapping) and argument.get("kind") in ARGUMENT_KINDS
                         and isinstance(argument.get("value"), str),
                         f"{cwhere}: argument {argument!r} has an unknown kind")
                expected_keys = {"kind", "value", "relative"} if argument["kind"] == "binding_path" else {"kind", "value"}
                _require(set(argument) == expected_keys, f"{cwhere}: argument {argument!r} keys are not exact")
            cwd = command.get("cwd")
            _require(isinstance(cwd, Mapping) and cwd.get("kind") == "binding" and cwd.get("value") == "repo_root",
                     f"{cwhere}: cwd must be the repo_root binding")
            codes = command.get("success_exit_codes")
            _require(isinstance(codes, list) and bool(codes) and all(type(code) is int for code in codes),
                     f"{cwhere}: success_exit_codes must be a non-empty integer list")
            commands.append(Command(
                command_id=_identifier(command.get("command_id"), cwhere + ".command_id"),
                tool_id=tool_id, interface_id=interface_id,
                arguments=tuple(dict(argument) for argument in arguments),
                cwd_binding="repo_root", success_exit_codes=tuple(codes)))
        slot = None
        if kind == "calibration_capture":
            values = [argument["value"] for argument in commands[0].arguments]
            _require(len(commands) == 1 and values.count("--slot") == 1,
                     f"{stage_id}: a calibration capture names exactly one --slot")
            slot = values[values.index("--slot") + 1] if values.index("--slot") + 1 < len(values) else None
            _require(slot in {"pre", "post"}, f"{stage_id}: calibration slot must be pre or post")
        if kind in IN_CHAIN_KINDS:
            _require(len(commands) == 1, f"{stage_id}: an in-chain stage has exactly one command")
        if kind == "campaign_collection":
            _require(expected >= 1, f"{stage_id}: a collection stage expects at least one member")
            _require(commands[0].tool_id == "campaign_runner", f"{stage_id}: collection must use campaign_runner")
        stages.append(Stage(stage_id, ordinal, kind, expected, tuple(commands),
                            kind in IN_CHAIN_KINDS, slot))
    stages.sort(key=lambda stage: stage.ordinal)
    _require([stage.ordinal for stage in stages] == list(range(1, len(stages) + 1)),
             "stage ordinals must be exactly 1..n")
    _require(len({stage.stage_id for stage in stages}) == len(stages), "stage ids must be unique")
    for index, stage in enumerate(stages):
        row = next(item for item in graph if item.get("stage_id") == stage.stage_id)
        predecessor = stages[index - 1].stage_id if index else None
        successor = stages[index + 1].stage_id if index + 1 < len(stages) else None
        _require(row.get("predecessor") == predecessor and row.get("successor") == successor,
                 f"{stage.stage_id}: predecessor/successor do not form one chain in ordinal order")
    chain = [stage for stage in stages if stage.in_chain]
    _require(bool(chain) and chain[0].kind == "bracket_reservation", "the first chain stage must be the reservation")
    _require(sum(stage.kind == "bracket_reservation" for stage in stages) == 1, "exactly one bracket reservation")
    pre = [i for i, stage in enumerate(chain) if stage.slot == "pre"]
    post = [i for i, stage in enumerate(chain) if stage.slot == "post"]
    _require(len(pre) == 1 and len(post) == 1, "exactly one pre and one post calibration capture")
    collections = [i for i, stage in enumerate(chain) if stage.kind == "campaign_collection"]
    _require(bool(collections) and pre[0] < min(collections) and post[0] > max(collections),
             "the pre and post calibration captures must bracket every collection")
    _require(post[0] == len(chain) - 1, "post-calibration must be the last chain stage")
    derivations = [i for i, stage in enumerate(chain) if stage.kind == "bound_derivation"]
    _require(len(derivations) == 1 and derivations[0] > min(collections),
             "exactly one bound derivation, after the corpus collection")
    return stages


def json_pointer(tree: Mapping[str, Any], pointer: str) -> Any:
    _require(isinstance(pointer, str) and pointer.startswith("/"), f"tree pointer {pointer!r} must start with /")
    value: Any = tree
    for part in pointer[1:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if isinstance(value, list):
            _require(part.isdigit() and int(part) < len(value), f"tree pointer {pointer!r} does not resolve")
            value = value[int(part)]
        else:
            _require(isinstance(value, Mapping) and part in value, f"tree pointer {pointer!r} does not resolve")
            value = value[part]
    _require(isinstance(value, (str, int, float)) and not isinstance(value, bool),
             f"tree pointer {pointer!r} must name a scalar")
    return value


def bind_argument(argument: Mapping[str, Any], bindings: Mapping[str, str],
                  tree: Mapping[str, Any], measurement_root: Path) -> str:
    kind, value = argument["kind"], argument["value"]
    if kind == "literal":
        return value
    if kind in ("binding", "binding_path"):
        _require(value in bindings, f"binding {value!r} is not bound")
        bound = bindings[value]
        if kind == "binding":
            return bound
        return str(Path(bound) / _relative(argument["relative"], f"binding_path {value} relative"))
    if kind == "repo_path":
        return str(Path(measurement_root) / _relative(value, "repo_path"))
    return str(json_pointer(tree, value))


def stage_argv(stage: Stage, bindings: Mapping[str, str], tree: Mapping[str, Any],
               measurement_root: Path) -> list[str]:
    """The exact argv the chain runs for one in-chain stage, deviations applied."""

    command = stage.commands[0]
    tool = TOOLS[command.tool_id]
    arguments = [bind_argument(argument, bindings, tree, measurement_root) for argument in command.arguments]
    if stage.kind == "campaign_collection":
        positions = [i for i, item in enumerate(arguments) if item == "--max-failures"]
        _require(len(positions) <= 1, f"{stage.stage_id}: --max-failures appears more than once")
        if positions:
            _require(positions[0] + 1 < len(arguments), f"{stage.stage_id}: --max-failures has no value")
            arguments[positions[0] + 1] = str(stage.expected_count)
        else:
            arguments += ["--max-failures", str(stage.expected_count)]
    if stage.kind == "calibration_capture":
        for flag in ("--arm-countdown-s", "--sleep-display-before-capture"):
            _require(flag not in arguments, f"{stage.stage_id}: template already carries {flag}")
        arguments += list(CALIBRATION_RUNBOOK_FLAGS)
    root = Path(measurement_root)
    if tool.runner == "python":
        return [str(root / ".venv/bin/python"), str(root / tool.program), *arguments]
    return ["/bin/zsh", str(root / tool.program), *arguments]


class Shell(str):
    """An argv item rendered verbatim: a double-quoted shell expansion the renderer built."""


def _literal(value: str) -> str:
    if isinstance(value, Shell):
        return str(value)
    _require(isinstance(value, str) and not any(c in value for c in "\0\n\r"),
             f"value {value!r} cannot be a shell literal")
    return shlex.quote(value)


def _argv_text(argv: Sequence[str]) -> str:
    """One shell word per argv item; a flag and the value after it share a line."""

    lines: list[list[str]] = []
    for item in argv:
        flag = isinstance(item, str) and not isinstance(item, Shell) and item.startswith("--")
        if not lines or flag or (lines[-1] and not lines[-1][0].startswith("--")) or len(lines[-1]) > 1:
            lines.append([])
        lines[-1].append(_literal(item))
    return " \\\n    ".join(" ".join(words) for words in lines)


# Stdlib-only helpers the chain runs with the measurement interpreter. They
# travel inside the chain bytes, so the chain's digest pins them.
PRUNE_HELPER = r"""
import hashlib, json, os, sys
manifest_path, runs_root, output, summary_path = sys.argv[1:5]
with open(manifest_path, "rb") as handle:
    raw = handle.read()
committed_sha256 = hashlib.sha256(raw).hexdigest()
manifest = json.loads(raw)
kept, dropped = [], []
for member in manifest["members"]:
    relative = member.get("bundle_path") if isinstance(member, dict) else None
    status = None
    if (isinstance(relative, str) and relative and not os.path.isabs(relative)
            and ".." not in relative.split("/")):
        try:
            with open(os.path.join(runs_root, relative, "summary_metrics.json"), "rb") as handle:
                status = json.loads(handle.read()).get("status")
        except (OSError, ValueError, AttributeError):
            status = None
    if status == "succeeded":
        kept.append(member)
    else:
        dropped.append({"bundle_id": member.get("bundle_id") if isinstance(member, dict) else None,
                        "status": status})
if dropped:
    pruned = dict(manifest)
    pruned["members"] = kept
    raw = (json.dumps(pruned, indent=2, sort_keys=True) + "\n").encode("utf-8")
def create_once(path, data):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
create_once(output, raw)
summary = {"schema": "joulewise.b5_neg8_corpus_collected.v1",
           "committed_manifest": {"path": os.path.abspath(manifest_path), "sha256": committed_sha256},
           "collected_manifest": {"path": os.path.abspath(output), "sha256": hashlib.sha256(raw).hexdigest()},
           "members_listed": len(manifest["members"]), "members_kept": len(kept),
           "kept_bundle_ids": [member.get("bundle_id") for member in kept],
           "dropped": dropped, "identical_to_committed": not dropped}
create_once(summary_path, (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode("utf-8"))
print(json.dumps(summary, sort_keys=True))
"""

def runbook_screen(runbook_text: str) -> str:
    """The runbook's D-079 pre-calibration screen block, verbatim.

    From the clause-3 comment through the closing brace of
    ``screen_pre_calibration``: the literal bound assignment and the function
    that reads the pre slot's ``instrument_evidence.json`` and fails above the
    bound. It needs ``timestamp`` and ``OPERATOR_LOG_ROOT``, which the chain
    defines.
    """

    _require(isinstance(runbook_text, str), "runbook text is required")
    _require(runbook_text.count(RUNBOOK_SCREEN_START) == 1 and runbook_text.count(RUNBOOK_SCREEN_FUNCTION) == 1,
             "the runbook must carry exactly one D-079 clause 3 screen block")
    block = runbook_text[runbook_text.index(RUNBOOK_SCREEN_START):]
    function = block.index(RUNBOOK_SCREEN_FUNCTION)
    closing = block.find("\n}\n", function)
    _require(closing > function, "the runbook screen function is not closed")
    block = block[:closing + 2]
    _require(re.search(r"(?m)^PRE_CAL_FIDUCIAL_MAX_S=[0-9]+\.[0-9]+$", block) is not None,
             "the runbook screen block must assign a literal PRE_CAL_FIDUCIAL_MAX_S")
    _require("$(" in block and "`" not in block and "<<" not in block,
             "the runbook screen block has an unexpected shape")
    return block


_PRELUDE_FUNCTIONS = r"""stamp() { TZ=UTC /bin/date '+%Y-%m-%dT%H:%M:%SZ'; }
timestamp() { stamp; }
note() { print -r -- "$(stamp) $*" >> "$CHAIN_LOG"; }
settle() { /bin/sleep "$SETTLE_S"; }
# journal STAGE_ID KIND RC STARTED: one JSON line per stage (identifiers are [A-Za-z0-9._-]).
journal() {
  print -r -- "{\"stage_id\":\"$1\",\"kind\":\"$2\",\"rc\":$3,\"started_epoch_s\":$4,\"ended_epoch_s\":$(/bin/date +%s)}" >> "$STAGE_JOURNAL"
}
# run_stage STAGE_ID KIND OUT LOG ARGV...: run one stage with stdout to OUT and
# stderr to LOG (the same file for ordinary stages); journal its return code.
run_stage() {
  local stage_id="$1" kind="$2" out="$3" log="$4" started rc
  shift 4
  started="$(/bin/date +%s)"
  note "stage_start=$stage_id"
  "$@" >> "$out" 2>> "$log"
  rc=$?
  journal "$stage_id" "$kind" "$rc" "$started"
  note "stage_end=$stage_id rc=$rc"
  return $rc
}
# stop_chain REASON EXIT: the only early exits, all before member 1.
stop_chain() {
  note "chain_stop=$1"
  journal chain.stop "$1" "$2" "$(/bin/date +%s)"
  exit $2
}"""


def render_chain(*, tree: Mapping[str, Any], tree_sha256: str, stages: Sequence[Stage],
                 bindings: Mapping[str, str], measurement_root: Path, pack_root: Path,
                 plan_id: str, runbook_text: str, settle_s: int | float = SETTLE_S) -> bytes:
    """Return the chain bytes. Every value is a literal; nothing is written.

    ``runbook_text`` is the measurement checkout's ``docs/phase_2/window_runbook.md``;
    its D-079 screen block is embedded verbatim.
    """

    _require(_SHA256_RE.fullmatch(tree_sha256 or "") is not None, "tree_sha256 must be a SHA-256 digest")
    _identifier(plan_id, "plan_id")
    _require(isinstance(settle_s, (int, float)) and not isinstance(settle_s, bool) and settle_s >= 0,
             "settle_s must be a non-negative number")
    settle_text = str(int(settle_s)) if float(settle_s).is_integer() else repr(float(settle_s))
    screen = runbook_screen(runbook_text)
    for name in ("operator_log_root", "claim_runs_root", "bound_runs_root", "pre_calibration_dir",
                 "bracket_session_id", "ledger_path"):
        _require(isinstance(bindings.get(name), str) and bool(bindings[name]), f"binding {name} is required")
    root = Path(measurement_root)
    python = str(root / ".venv/bin/python")
    chain = [stage for stage in stages if stage.in_chain]
    reservation = chain[0]
    pre = next(stage for stage in chain if stage.slot == "pre")
    post = next(stage for stage in chain if stage.slot == "post")
    reservation_argv = stage_argv(reservation, bindings, tree, root)

    def value_after(argv: Sequence[str], flag: str) -> str | None:
        return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else None

    frozen_plan = value_after(reservation_argv, "--plan")
    head_pin = value_after(reservation_argv, "--head-pin")

    lines = [
        "#!/bin/zsh -f",
        f"# {CHAIN_SCHEMA}: HAZARD_PACK window chain for plan {plan_id}.",
        f"# Rendered by joulewise/b5/chain.py from {pack_root}/plan_tree.json",
        f"# (sha256 {tree_sha256}). The driver hashes these bytes against the",
        "# sidecar at launch; a difference is recorded as code.executed_differs_from_sealed.",
        "#",
        "# Order (block-3 runbook): reservation, settle, pre-calibration and its screen,",
        "# NEG-8 corpus and bound, start references, science stages with their midpoint",
        "# references, end references, post-calibration. Desk steps are not here.",
        "#",
        "# Stops: reservation failed (exit 10), pre-calibration capture failed (11),",
        "# pre-calibration screen failed (12). The driver stops the chain on low disk.",
        "# Every other stage journals its return code and the chain continues; a chain",
        "# that reaches its end exits 0.",
        "#",
        "# Registered deviations from the pack's stage graph:",
        *[f"#   - {item}" for item in DEVIATIONS],
        "set -u",
        f"export B5_CHAIN_SCHEMA={CHAIN_SCHEMA}",
        f"export B5_CHAIN_INTERFACE={CHAIN_INTERFACE}",
        f"export B5_PLAN_ID={_literal(plan_id)}",
        f"export B5_PACK_ID={_literal(Path(pack_root).name)}",
        f"export B5_PLAN_TREE_SHA256={tree_sha256}",
        'if [[ -n "${NIGHT_VERIFY_ONLY:-}" || -n "${NIGHT_RESERVATION_ARGV_ONLY:-}" ]]; then',
        "  print -u2 -r -- 'b5 chain: inspection modes are not supported; nothing was run'",
        f"  exit {EXIT_INSPECTION_REFUSED}",
        "fi",
        ': "${NIGHT_DIR:?the HAZARD_PACK driver exports NIGHT_DIR}"',
        f"export REPO={_literal(str(root))}",
        f"export PY={_literal(python)}",
        'export PYTHONPATH="$REPO"',
        "export PYTHONDONTWRITEBYTECODE=1 GIT_OPTIONAL_LOCKS=0",
        f"export SETTLE_S={settle_text}",
        f"OPERATOR_LOG_ROOT={_literal(bindings['operator_log_root'])}",
        f"CLAIM_RUNS_ROOT={_literal(bindings['claim_runs_root'])}",
        f"BOUND_RUNS_ROOT={_literal(bindings['bound_runs_root'])}",
        'CHAIN_LOG="$OPERATOR_LOG_ROOT/window-chain.log"',
        f'STAGE_JOURNAL="$NIGHT_DIR/{STAGE_JOURNAL}"',
        'TRANSCRIPT_ROOT="$NIGHT_DIR/transcript"',
        "B5_PRUNE_PY=\"$(/bin/cat <<'B5_PY'",
        PRUNE_HELPER.strip("\n"),
        "B5_PY",
        ')"',
        '/bin/mkdir -p "$OPERATOR_LOG_ROOT" "$TRANSCRIPT_ROOT" "$CLAIM_RUNS_ROOT/instrument_validation" "$BOUND_RUNS_ROOT"',
        _PRELUDE_FUNCTIONS,
        "# The runbook's D-079 clause 3 screen, embedded verbatim from " + RUNBOOK_RELATIVE + ".",
        screen.rstrip("\n"),
        'cd "$REPO" || note "chdir_failed=$REPO"',
        'note "chain_start plan=$B5_PLAN_ID pack=$B5_PACK_ID"',
    ]

    def log_path(stage: Stage, suffix: str = "") -> Shell:
        return Shell(f'"$OPERATOR_LOG_ROOT/{stage.ordinal:02d}-{stage.stage_id}{suffix}.log"')

    def run(stage: Stage, argv: Sequence[str], *, label: str | None = None, kind: str | None = None,
            suffix: str = "", out: Shell | None = None) -> str:
        log = log_path(stage, suffix)
        head = [label or stage.stage_id, kind or stage.kind, out if out is not None else log, log]
        return "run_stage " + " ".join(_literal(item) for item in head) + " \\\n    " + _argv_text(argv)

    collected = Shell('"$TRANSCRIPT_ROOT/' + NEG8_COLLECTED_MANIFEST + '"')
    collected_summary = Shell('"$TRANSCRIPT_ROOT/' + NEG8_COLLECTED_SUMMARY + '"')
    lines.append("# 1. The bracket reservation. A failed reservation stops the chain.")
    lines.append(run(reservation, reservation_argv))
    lines.append(f"(( $? == 0 )) || stop_chain reservation_failed {EXIT_RESERVATION_FAILED}")
    lines.append("# 2. Chain-owned settle before the pre slot (runbook section 5C).")
    lines.append("settle")
    for stage in chain[1:]:
        argv = stage_argv(stage, bindings, tree, root)
        if stage is pre:
            lines.append("# 3. The pre-calibration capture and its D-079 screen; either failure stops the chain.")
            lines.append(run(stage, argv))
            lines.append(f"(( $? == 0 )) || stop_chain pre_calibration_capture_failed {EXIT_PRE_CAPTURE_FAILED}")
            lines.append(run(stage, ["screen_pre_calibration", bindings["pre_calibration_dir"]],
                             label=stage.stage_id + ".screen", kind="pre_calibration_screen", suffix=".screen"))
            lines.append(f"(( $? == 0 )) || stop_chain pre_calibration_screen_failed {EXIT_PRE_SCREEN_FAILED}")
        elif stage is post:
            lines.append("# 8. The post-calibration capture, then a record (never a check) of the session status.")
            lines.append(run(stage, argv))
            if frozen_plan is not None and head_pin is not None:
                status_argv = [python, str(root / "scripts/recover_calibration_ledger.py"),
                               "--ledger", bindings["ledger_path"], "--head-pin", head_pin, "session-status",
                               "--session-id", bindings["bracket_session_id"], "--plan", frozen_plan]
                lines.append(run(stage, status_argv, label=stage.stage_id + ".session-status",
                                 kind="session_status_record", suffix=".session-status",
                                 out=Shell('"$TRANSCRIPT_ROOT/' + TERMINAL_BOUNDARY + '"')))
        elif stage.kind == "campaign_collection":
            lines.append(f"# Collection stage {stage.stage_id}: {stage.expected_count} member(s).")
            lines.append("settle")
            lines.append(run(stage, argv))
        elif stage.kind == "bound_derivation":
            manifest = value_after(argv, "--derive-neg8-drift-bound")
            runs_dir = value_after(argv, "--runs-dir")
            _require(argv.count("--derive-neg8-drift-bound") == 1 and manifest is not None and runs_dir is not None,
                     f"{stage.stage_id}: bound derivation names one manifest and --runs-dir")
            lines.append("# 4b. The NEG-8 bound, from the collected and succeeded corpus members. A pruned")
            lines.append("# copy (10 or 11 of 12) derives, but the core consumers authenticate only the committed")
            lines.append("# 12-member bytes: such a window ends neg8.bound_not_derived until an erratum.")
            lines.append(run(stage, [python, "-B", "-c", Shell('"$B5_PRUNE_PY"'), manifest, runs_dir, collected,
                                     collected_summary],
                             label=stage.stage_id + ".corpus", kind="neg8_corpus_collected", suffix=".corpus"))
            derive = list(argv)
            derive[derive.index("--derive-neg8-drift-bound") + 1] = collected
            lines.append(run(stage, derive))
        elif stage.kind == "bracket_reservation":  # pragma: no cover - stage_plan admits exactly one
            raise ChainRenderError(f"{stage.stage_id}: a second reservation")
    lines += ['note "chain_end"', f"exit {EXIT_COMPLETED}", ""]
    return "\n".join(lines).encode("utf-8")


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sidecar_bytes(raw: bytes, name: str) -> bytes:
    """GNU ``shasum -a 256`` form, the form ``run_night._sidecar_digest`` reads."""

    return f"{sha256_bytes(raw)}  {name}\n".encode("utf-8")


def stage_journal(night_dir: Path) -> list[dict[str, Any]]:
    """Read ``chain-stages.jsonl``; a torn or foreign line is skipped, never fatal."""

    rows: list[dict[str, Any]] = []
    try:
        text = (Path(night_dir) / STAGE_JOURNAL).read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return rows
    for line in text.splitlines():
        try:
            value = json.loads(line)
        except ValueError:
            continue
        if isinstance(value, dict) and isinstance(value.get("stage_id"), str):
            rows.append(value)
    return rows


def neg8_corpus_record(night_dir: Path) -> dict[str, Any]:
    """Locate the NEG-8 corpus manifest the bound derivation read, for the harvest.

    Reads the window-local manifest copy and the prune helper's summary under
    ``$NIGHT_DIR/transcript/`` after the chain. Every SHA-256 here is
    recomputed from the bytes on disk, including the committed manifest the
    summary names. ``pruned`` is true when the copy differs from the committed
    bytes: the derivation then ran on 10 or 11 members, and the core consumers
    will not authenticate the bound against the committed manifest (see
    ``DEVIATIONS``). A missing or unreadable file is recorded, never fatal.
    """

    transcript = Path(night_dir) / "transcript"
    errors: list[str] = []

    def locate(path: Path | None, label: str) -> dict[str, str] | None:
        if path is None:
            return None
        try:
            raw = Path(path).read_bytes()
        except OSError as error:
            errors.append(f"{label}: {type(error).__name__}: {error}")
            return None
        return {"path": str(path), "sha256": sha256_bytes(raw)}

    collected_path = transcript / NEG8_COLLECTED_MANIFEST
    summary_path = transcript / NEG8_COLLECTED_SUMMARY
    summary: Any = None
    try:
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as error:
        errors.append(f"summary: {type(error).__name__}: {error}")
    if not isinstance(summary, dict):
        summary = {}
    named = summary.get("committed_manifest")
    named_path = named.get("path") if isinstance(named, dict) else None
    collected = locate(collected_path, "collected manifest")
    committed = locate(Path(named_path) if isinstance(named_path, str) and named_path else None,
                       "committed manifest")
    members_kept = None
    if collected is not None:
        try:
            members = json.loads(collected_path.read_bytes()).get("members")
            members_kept = len(members) if isinstance(members, list) else None
        except (OSError, ValueError, AttributeError) as error:
            errors.append(f"collected manifest members: {type(error).__name__}")
    pruned = None if collected is None or committed is None else collected["sha256"] != committed["sha256"]
    listed = summary.get("members_listed")
    return {"collected_manifest": collected, "committed_manifest": committed,
            "summary": locate(summary_path, "summary") if summary else None,
            "members_listed": listed if type(listed) is int else None, "members_kept": members_kept,
            "pruned": pruned, "errors": errors}


__all__ = [
    "CHAIN_SCHEMA", "CHAIN_INTERFACE", "SETTLE_S", "RUNBOOK_RELATIVE", "STOP_EXITS", "runbook_screen",
    "DEVIATIONS", "TOOLS", "ChainRenderError", "Stage", "Command", "stage_plan", "bind_argument",
    "stage_argv", "render_chain", "sha256_bytes", "sidecar_bytes", "stage_journal",
    "NEG8_COLLECTED_MANIFEST", "NEG8_COLLECTED_SUMMARY", "STAGE_JOURNAL", "TERMINAL_BOUNDARY",
    "neg8_corpus_record",
]
