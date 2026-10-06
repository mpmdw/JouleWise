"""Render a block-5 HAZARD_PACK window chain from a v5 pack's stage graph.

The chain is a zsh script the driver (``scripts/run_night.py``, HAZARD_PACK
branch) launches once, after the hazard arm returns GO. It runs the pack's
committed ``plan_tree.json`` stage graph in ordinal order, in the block-3
runbook protocol:

1. the bracket reservation;
2. a settle (``SETTLE_S``, 60 s: registration §0.6, block-5 timing ruling of
   2026-10-06) before the pre slot;
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

Gate-prune round 2 (PLAN2) adds, each listed in ``DEVIATIONS``:

* S3: the operator countdown is 0 s on the pre slot and on every collection
  stage, 20 s on the post slot (no settle precedes it);
* J1: right after the pre-calibration screen, one synchronous refit of the
  pre slot writes the create-once ``window_calibration_verdict.json`` beside
  the pre-slot directory (``scripts/b5_window_calibration_verdict.py``);
* row 8: every non-member stage except the post-calibration capture runs
  under a wall budget (``BUDGET_HELPER``; rc 124 on expiry);
* row 17: a collection stage (or the bound derivation) launches only if it
  can end before the calibration's 24 h horizon less the post-capture
  reserve; otherwise the chain skips to the post capture (rc 75 in the
  journal) and flags ``roster.horizon_truncated``;
* row 13: when fewer than 10 NEG-8 corpus members succeeded, the corpus
  stage runs once more; each member it measures is flagged
  ``member.retried``. There is no drain.

The chain's own flags go through ``joulewise.flags.core`` (writer
``b5-chain``); a flag that cannot be written lands in the chain log behind
the core's unwritten-flag marker.

The NEG-8 bound derivation reads a window-local copy of the settled-corpus
manifest that lists only the collected members that succeeded and, on a HAZARD
bound root, that the core's NEG-8 mint would not drop
(``whole_window.neg8_corpus_mint_drops``, when the core provides it: a member
failing one of the mint's per-member predicates, or outside the majority
condition). The copy is then exactly the manifest the HAZARD mint binds its
bound to. With all 12 kept that copy is byte-identical to the committed
manifest. With 10 or 11 the derivation runs on the custodied copy, and its
bound artifact names that copy's SHA-256. The core reader
(``whole_window.load_neg8_drift_bound_artifact``) still authenticates the corpus
only against the committed 12-member bytes, but the harvest validates the bound
against the custodied collected subset (registration 5.3,
``harvest._collected_corpus_bytes``), so such a window is not excluded for that
reason alone. ``neg8.bound_not_derived`` (EXCLUDE_WINDOW) follows when fewer
than 10 are kept, when the custodied bytes or the bound do not validate, or
when a member that succeeded was left out for any reason other than a mint
drop for a registered member-validity reason (a selected corpus; the harvest's
``NEG8_ACCEPTED_DROP_REASONS``). The chain keeps those bytes and a
create-once summary (both paths and SHA-256, and each dropped member with its
reason) under ``$NIGHT_DIR/transcript/``; the driver copies the locator into
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
# The registered settle, 60 s before the pre slot and before every collection
# stage: block-5 registration §0.6 and §5.2, and the block-5 timing ruling of
# 2026-10-06 (all eleven settles cut from the runbook's 180 s to 60 s; the
# machine is at idle within about 15 s of a decode ending, and each first
# member measures its own idle baseline).
SETTLE_S = 60
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
# Gate-prune 2 S3 (PLAN2 1.2, findings t1-05, t2-04, t3-7): the operator
# countdown is 0 s on the pre slot (a settle precedes it) and on every
# collection stage (each follows a settle); the post slot keeps 20 s, because
# no settle separates it from the end references.
CALIBRATION_ARM_COUNTDOWN_S = {"pre": 0, "post": 20}
COLLECTION_ARM_COUNTDOWN_S = 0


def calibration_runbook_flags(slot: str | None) -> tuple[str, ...]:
    """The runbook capture flags for one calibration slot, countdown deviation applied."""

    return ("--arm-countdown-s", str(CALIBRATION_ARM_COUNTDOWN_S[slot]), "--sleep-display-before-capture")


CALIBRATION_RUNBOOK_FLAGS = {slot: calibration_runbook_flags(slot) for slot in CALIBRATION_ARM_COUNTDOWN_S}

# Gate-prune 2 row 8 (findings s2-03, s3-hang): a wall budget on every
# non-member stage except the post-calibration capture, enforced by a small
# Python wrapper (macOS has no coreutils timeout). On expiry the wrapper sends
# SIGTERM to the stage's process tree, waits BUDGET_GRACE_S, sends SIGKILL to
# what is left and exits BUDGET_EXPIRED_RC; the journal records that code and
# the chain goes on as it would after any failure of that stage. Collection
# stages run members and are not budgeted here (their cap is run_campaign's).
# The pre-calibration screen is an in-shell jq read of one small local file
# and is not wrapped.
BUDGET_EXPIRED_RC = 124
BUDGET_GRACE_S = 30
STAGE_WALL_BUDGET_S = {
    "bracket_reservation": 900,
    "pre_calibration_capture": 1800,
    "window_calibration_verdict": 600,
    "neg8_corpus_retry_decision": 300,
    "neg8_corpus_collected": 1800,
    "bound_derivation": 1800,
    "session_status_record": 600,
    "flag_record": 120,
}

# Interface J1 (PLAN2 3.2): the window calibration verdict. One synchronous
# refit of the pre slot, right after its screen and before the first settle;
# create-once next to the pre-slot capture directory. Members read it
# (controller, lane P2-CTL); the harvest never does.
WINDOW_CALIBRATION_VERDICT_BASENAME = "window_calibration_verdict.json"
WINDOW_CALIBRATION_VERDICT_PROGRAM = "scripts/b5_window_calibration_verdict.py"


def window_calibration_verdict_path(pre_calibration_dir: Path | str) -> Path:
    """Where J1 lives for a pre-slot capture directory: beside it, in ``instrument_validation``."""

    return Path(pre_calibration_dir).parent / WINDOW_CALIBRATION_VERDICT_BASENAME


# Gate-prune 2 row 17 (finding t1-08): the collection deadline. The window's
# calibration is fresh for CALIBRATION_HORIZON_S from the pre capture, so the
# chain stops launching collection work once a stage could not finish and
# still leave room for the post capture: a stage launches only when
#   now + its allowance <= pre capture start + CALIBRATION_HORIZON_S - HORIZON_POST_RESERVE_S.
# A collection stage's allowance is SETTLE_S + HORIZON_STAGE_OVERHEAD_S +
# expected_count * HORIZON_MEMBER_ALLOWANCE_S (at least block 4's larger member
# allowance, 619 s, with the cooldown at its 300 s cap and both idle attempts).
# The reserve is the settle, the whole calibration pair allowance (770 s) and
# 600 s of margin. Once one stage is refused every later one is, the chain
# goes to the post capture, and roster.horizon_truncated is flagged once.
# window_max_s is never lowered (it is the driver's kill timeout).
CALIBRATION_HORIZON_S = 86400
HORIZON_MEMBER_ALLOWANCE_S = 620
HORIZON_STAGE_OVERHEAD_S = 180
HORIZON_POST_RESERVE_S = SETTLE_S + 770 + 600
HORIZON_SKIPPED_RC = 75
COLLECTION_DEADLINE_RECORD = "collection-deadline.json"

# Gate-prune 2 row 13 (finding s1-09): one retry of the NEG-8 corpus stage
# when fewer than NEG8_RETRY_MINIMUM of its members succeeded (equal to
# whole_window.NEG8_DRIFT_MINIMUM_N). The retry re-runs the same stage into
# the same bound root: run_campaign skips a member whose bundle succeeded,
# refuses (never re-measures, never moves) one whose bundle exists and
# failed, and measures one that has no bundle, so it recovers exactly the
# members refused before their bundle existed. Each member it measures is
# flagged member.retried. Its log and journal labels carry ".retry"; the
# prune helper still runs once, after it. There is no drain.
NEG8_RETRY_MINIMUM = 10
NEG8_RETRY_SNAPSHOT = "neg8-corpus-before-retry.json"

# The chain's own flag writer (joulewise.flags.core; custody/flags/<writer>.jsonl).
CHAIN_FLAG_WRITER = "b5-chain"

DEVIATIONS = (
    "campaign_collection stages pass --max-failures <stage expected_count> in place of the pack's "
    "literal 1, so a failed member costs only itself (gate-prune plan L2; registration edit 14)",
    "calibration_capture stages add --arm-countdown-s <N> --sleep-display-before-capture, the "
    "block-3 runbook calibrate_slot protocol every live window has used, with N = 0 s for the pre slot "
    "(a settle precedes it) and 20 s for the post slot (no settle precedes it)",
    "campaign_collection stages pass --arm-countdown-s 0 in place of the pack's literal 20: each "
    "collection stage follows a settle, so the operator countdown waits for nothing (gate-prune 2 S3)",
    "after the pre-calibration screen the chain refits the pre slot once and writes the create-once "
    "window calibration verdict (instrument_validation/window_calibration_verdict.json, interface J1); "
    "a failed or missing verdict changes nothing (members refit, as before)",
    "every non-member stage except the post-calibration capture runs under a wall budget; on expiry "
    "the stage's process tree is stopped and the stage records rc 124 (gate-prune 2 row 8)",
    "a collection stage (and the bound derivation) launches only if it can end before the "
    "calibration's 24 h horizon less the post-capture reserve; otherwise it and every later stage "
    "are skipped (rc 75), the chain goes to the post capture and flags roster.horizon_truncated "
    "(gate-prune 2 row 17)",
    "when fewer than 10 NEG-8 corpus members succeeded, the corpus stage runs once more into the same "
    "bound root; it measures only members with no bundle, each flagged member.retried (gate-prune 2 "
    "row 13; no drain)",
    "bound_derivation reads a window-local copy of the settled-corpus manifest listing only the "
    "collected corpus members that succeeded and, on a HAZARD bound root, that the core's NEG-8 "
    "mint would not drop (whole_window.neg8_corpus_mint_drops, when present), so the copy is the "
    "manifest the mint binds its bound to (byte-identical when all 12 are kept). With 10 or 11 of 12 the "
    "derivation runs on that custodied copy (whole_window.NEG8_DRIFT_MINIMUM_N = 10). The core "
    "reader (whole_window.load_neg8_drift_bound_artifact) authenticates only the committed "
    "12-member bytes, but the harvest validates the bound against the custodied collected subset "
    "(registration 5.3), so such a window is not excluded for that reason alone: "
    "neg8.bound_not_derived (EXCLUDE_WINDOW) follows only when fewer than 10 are kept, when the "
    "custodied bytes or the bound do not validate, or when a member that succeeded was left out "
    "for any reason but a mint drop for a registered member-validity reason, a selected corpus "
    "(locator: "
    "night/hazard_result.json neg8_corpus)",
    "whole_window_verdict and backup stages are desk steps and are not in the chain",
    "every settle (before the pre slot and before each collection stage) is SETTLE_S = 60 s, not the "
    "runbook's SETTLE_S=180 (block-5 timing ruling of 2026-10-06; registration sections 0.6 and 5.1)",
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
        positions = [i for i, item in enumerate(arguments) if item == "--arm-countdown-s"]
        _require(len(positions) <= 1, f"{stage.stage_id}: --arm-countdown-s appears more than once")
        if positions:
            _require(positions[0] + 1 < len(arguments), f"{stage.stage_id}: --arm-countdown-s has no value")
            arguments[positions[0] + 1] = str(COLLECTION_ARM_COUNTDOWN_S)
        elif "--arm-quiet-mode" in arguments:
            # run_campaign's own default with --arm-quiet-mode is 5 s.
            arguments += ["--arm-countdown-s", str(COLLECTION_ARM_COUNTDOWN_S)]
    if stage.kind == "calibration_capture":
        for flag in ("--arm-countdown-s", "--sleep-display-before-capture"):
            _require(flag not in arguments, f"{stage.stage_id}: template already carries {flag}")
        arguments += list(calibration_runbook_flags(stage.slot))
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


# Helpers the chain runs with the measurement interpreter. They travel inside
# the chain bytes, so the chain's digest pins them.
PRUNE_HELPER = r"""
import hashlib, json, os, pathlib, sys, tempfile
manifest_path, runs_root, output, summary_path = sys.argv[1:5]
def render(value):
    # The rendering the HAZARD NEG-8 mint gives a pruned manifest (whole_window).
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
with open(manifest_path, "rb") as handle:
    raw = handle.read()
committed_sha256 = hashlib.sha256(raw).hexdigest()
manifest = json.loads(raw)
statuses = []
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
    statuses.append(status)
succeeded = [member for member, status in zip(manifest["members"], statuses) if status == "succeeded"]
# On a HAZARD bound root the core's NEG-8 mint drops a member that fails one of
# its per-member predicates (or sits outside the majority condition) and binds
# the bound to the manifest without it, rendered as render() renders it
# (core-prune A3).  This helper drops the same members, named by the core's own
# whole_window.neg8_corpus_mint_drops over the members that succeeded, so the
# copy it writes is the manifest the mint binds to; the harvest accepts exactly
# these drops (N2).  It is therefore not stdlib-only: the chain exports
# PYTHONPATH=$REPO and the executed-file inventory pins whole_window.py.  A
# root that is not HAZARD (the mint is then all-or-nothing), a core without
# the function, or a call that raises leaves the registered status-only rule,
# and the mint decides as it does.
mint_reasons, mint_rule = {}, "not_hazard"
try:
    import joulewise.window_lineage as window_lineage
    import joulewise.whole_window as whole_window
    hazard = window_lineage.is_hazard_runs_root(runs_root)
    mint_drops = getattr(whole_window, "neg8_corpus_mint_drops", None)
except Exception as error:
    hazard, mint_drops, mint_rule = False, None, "unavailable: " + type(error).__name__
if hazard and mint_drops is None:
    mint_rule = "unavailable: whole_window.neg8_corpus_mint_drops"
elif hazard:
    try:
        if len(succeeded) == len(manifest["members"]):
            rows = mint_drops(pathlib.Path(runs_root), pathlib.Path(manifest_path))
        else:
            with tempfile.TemporaryDirectory() as scratch:
                staged = pathlib.Path(scratch) / "succeeded-members.json"
                staged.write_bytes(render(dict(manifest, members=succeeded)))
                rows = mint_drops(pathlib.Path(runs_root), staged)
        mint_reasons = {row["bundle_id"]: row["reason"] for row in rows}
        mint_rule = "joulewise.whole_window.neg8_corpus_mint_drops"
    except Exception as error:
        mint_reasons, mint_rule = {}, "raised: " + type(error).__name__
kept, dropped = [], []
for member, status in zip(manifest["members"], statuses):
    bundle_id = member.get("bundle_id") if isinstance(member, dict) else None
    if status != "succeeded":
        dropped.append({"bundle_id": bundle_id, "status": status})
    elif bundle_id in mint_reasons:
        dropped.append({"bundle_id": bundle_id, "status": status, "mint_drop": mint_reasons[bundle_id]})
    else:
        kept.append(member)
if dropped:
    raw = render(dict(manifest, members=kept))
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
           "dropped": dropped, "identical_to_committed": not dropped, "mint_rule": mint_rule}
create_once(summary_path, (json.dumps(summary, indent=2, sort_keys=True) + "\n").encode("utf-8"))
print(json.dumps(summary, sort_keys=True))
"""

# Row 8: run argv under a wall budget (stdlib only). The child stays in the
# chain's process group, so the driver's group stop and census still reach it.
# On expiry the tree (the child and every descendant, listed before any
# signal, since descendants are re-parented once the child exits) gets
# SIGTERM, then SIGKILL after the grace; a process the chain may not signal
# (a root-owned sampler) is named on stderr. Exit: the child's code (128+N for
# signal N), or BUDGET_EXPIRED_RC.
BUDGET_HELPER = r"""
import os, signal, subprocess, sys, time
budget, grace, expired_rc = float(sys.argv[1]), float(sys.argv[2]), int(sys.argv[3])
if sys.argv[4] != "--" or len(sys.argv) < 6:
    print("b5 chain budget: usage SECONDS GRACE RC -- ARGV...", file=sys.stderr)
    sys.exit(2)
argv = sys.argv[5:]
def code(rc):
    return rc if rc >= 0 else 128 - rc
try:
    child = subprocess.Popen(argv)
except OSError as error:
    print("b5 chain budget: cannot start " + argv[0] + ": " + type(error).__name__, file=sys.stderr)
    sys.exit(127)
try:
    sys.exit(code(child.wait(timeout=budget)))
except subprocess.TimeoutExpired:
    pass
def tree(root):
    try:
        text = subprocess.run(["/bin/ps", "-A", "-o", "pid=,ppid="], capture_output=True, text=True,
                              timeout=10).stdout
    except Exception:
        return [root]
    children = {}
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            children.setdefault(int(parts[1]), []).append(int(parts[0]))
    found, stack = [root], [root]
    while stack:
        for pid in children.get(stack.pop(), []):
            if pid not in found and pid != os.getpid():
                found.append(pid)
                stack.append(pid)
    return found
def alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
members = tree(child.pid)
print("b5 chain budget: wall budget %g s expired; SIGTERM to %d process(es)" % (budget, len(members)),
      file=sys.stderr, flush=True)
for pid in members:
    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
deadline = time.monotonic() + grace
while time.monotonic() < deadline and child.poll() is None:
    time.sleep(0.2)
for pid in members:
    if pid == child.pid and child.poll() is not None:
        continue
    try:
        os.kill(pid, signal.SIGKILL)
    except OSError:
        pass
try:
    child.wait(timeout=10)
except subprocess.TimeoutExpired:
    pass
time.sleep(0.2)
left = [pid for pid in members if pid != child.pid and alive(pid)]
if child.poll() is None:
    left.insert(0, child.pid)
print("b5 chain budget: stopped; survivors " + (",".join(map(str, left)) or "none"), file=sys.stderr, flush=True)
sys.exit(expired_rc)
"""

# The chain's flags (rows 13 and 17): joulewise.flags.core from the measurement
# checkout, writer CHAIN_FLAG_WRITER, the window plan's scope bindings. A flag
# that cannot be written is printed behind the core's marker to stderr, which
# the chain sends to its operator log (core-prune N8 recovers it).
FLAG_HELPER = r"""
import json, sys
runs_root, writer, code, level, run_id, observed, detail = sys.argv[1:8]
marker = "JOULEWISE_UNWRITTEN_FLAG "
def unwritten(reason):
    print(marker + json.dumps({"code": code, "level": level, "run_id": run_id or None,
                               "observed": json.loads(observed), "unbuilt": reason}, sort_keys=True),
          file=sys.stderr, flush=True)
    sys.exit(1)
try:
    from joulewise.flags import core as flags_core
except Exception as error:
    unwritten("flags core unavailable: " + type(error).__name__)
context = flags_core.hazard_flag_context(runs_root, writer=writer, stage="window")
if context is None:
    unwritten("runs root carries no HAZARD locator: " + runs_root)
written = flags_core.emit(context, code, level=level, run_id=run_id or None, observed=json.loads(observed),
                          detail=detail)
sys.exit(0 if written else 1)
"""

# Row 13: the NEG-8 corpus retry (stdlib only). "count" writes a create-once
# snapshot of each listed member's summary and prints "retry" when fewer than
# the minimum succeeded, else "no_retry". "retried" prints, one per line, the
# bundle directory of each member that had no summary in the snapshot and has
# one now: the members the retry measured.
CORPUS_RETRY_HELPER = r"""
import json, os, sys
mode, manifest_path, runs_root, snapshot_path = sys.argv[1:5]
with open(manifest_path, "rb") as handle:
    members = json.loads(handle.read())["members"]
def state(member):
    relative = member.get("bundle_path") if isinstance(member, dict) else None
    if not (isinstance(relative, str) and relative and not os.path.isabs(relative)
            and ".." not in relative.split("/")):
        return None, False, None
    path = os.path.join(runs_root, relative, "summary_metrics.json")
    present = os.path.isfile(path)
    status = None
    if present:
        try:
            with open(path, "rb") as handle:
                status = json.loads(handle.read()).get("status")
        except (OSError, ValueError, AttributeError):
            status = None
    return relative, present, status
if mode == "count":
    minimum = int(sys.argv[5])
    rows = []
    for member in members:
        relative, present, status = state(member)
        rows.append({"bundle_id": member.get("bundle_id") if isinstance(member, dict) else None,
                     "bundle_path": relative, "summary_present": present, "status": status})
    succeeded = sum(row["status"] == "succeeded" for row in rows)
    decision = "retry" if succeeded < minimum else "no_retry"
    record = {"schema": "joulewise.b5_neg8_corpus_retry.v1", "decision": decision, "succeeded": succeeded,
              "minimum": minimum, "members_listed": len(rows), "members": rows}
    descriptor = os.open(snapshot_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(descriptor, "wb") as handle:
        handle.write((json.dumps(record, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        handle.flush()
        os.fsync(handle.fileno())
    print(decision)
elif mode == "retried":
    with open(snapshot_path, "rb") as handle:
        before = json.loads(handle.read())["members"]
    for row in before:
        if row["bundle_path"] is None or row["summary_present"]:
            continue
        if os.path.isfile(os.path.join(runs_root, row["bundle_path"], "summary_metrics.json")):
            print(row["bundle_path"].rstrip("/").split("/")[-1])
else:
    sys.exit(2)
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

# Gate-prune 2 rows 13 and 17: the chain's flag writer, and the collection
# deadline. HORIZON_DEADLINE is set when the pre capture starts; until then no
# collection stage can be reached (stage_plan puts the pre slot first).
_PRELUDE_GATE_PRUNE_2 = r"""# flag CODE LEVEL RUN_ID OBSERVED_JSON RUNS_ROOT DETAIL: one chain flag
# (joulewise.flags.core); stdout and stderr go to the chain log.
flag() {
  "$PY" -B -c "$B5_BUDGET_PY" @FLAG_BUDGET@ @GRACE@ @EXPIRED@ -- \
    "$PY" -B -c "$B5_FLAG_PY" "$5" @WRITER@ "$1" "$2" "$3" "$4" "$6" >> "$CHAIN_LOG" 2>&1
}
HORIZON_TRUNCATED=0
HORIZON_DEADLINE=0
# horizon_allows STAGE_ID ALLOWANCE_S MEMBERS_REMAINING: 0 when the stage can
# end before the collection deadline. The first refusal flags
# roster.horizon_truncated once; every later stage is refused too.
horizon_allows() {
  local now
  (( HORIZON_TRUNCATED )) && return 1
  now="$(/bin/date +%s)"
  (( now + $2 <= HORIZON_DEADLINE )) && return 0
  HORIZON_TRUNCATED=1
  note "horizon_truncated first_stage=$1 deadline_epoch_s=$HORIZON_DEADLINE"
  flag roster.horizon_truncated window "" \
    "{\"first_stage_skipped\":\"$1\",\"members_not_launched\":$3,\"deadline_epoch_s\":$HORIZON_DEADLINE,\"stage_allowance_s\":$2,\"horizon_s\":@HORIZON@,\"post_reserve_s\":@RESERVE@}" \
    "$CLAIM_RUNS_ROOT" "the chain stopped launching collection work at the calibration horizon and went to the post capture"
  return 1
}
# horizon_skip STAGE_ID: journal a stage the deadline skipped.
horizon_skip() {
  journal "$1" horizon_skipped @SKIPPED@ "$(/bin/date +%s)"
  note "stage_skipped=$1 reason=collection_deadline"
}"""


def render_chain(*, tree: Mapping[str, Any], tree_sha256: str, stages: Sequence[Stage],
                 bindings: Mapping[str, str], measurement_root: Path, pack_root: Path,
                 plan_id: str, runbook_text: str, settle_s: int | float = SETTLE_S,
                 horizon_s: int = CALIBRATION_HORIZON_S) -> bytes:
    """Return the chain bytes. Every value is a literal; nothing is written.

    ``runbook_text`` is the measurement checkout's ``docs/phase_2/window_runbook.md``;
    its D-079 screen block is embedded verbatim. ``horizon_s`` is a keyword for
    the mock-runtime render only (the command line renders the registered 24 h).
    """

    _require(_SHA256_RE.fullmatch(tree_sha256 or "") is not None, "tree_sha256 must be a SHA-256 digest")
    _identifier(plan_id, "plan_id")
    _require(isinstance(settle_s, (int, float)) and not isinstance(settle_s, bool) and settle_s >= 0,
             "settle_s must be a non-negative number")
    _require(type(horizon_s) is int and horizon_s >= 0, "horizon_s must be a non-negative integer")
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
    # The NEG-8 corpus stage (row 13): the last collection before the bound
    # derivation that collects into the derivation's --runs-dir.
    derivation = next(stage for stage in chain if stage.kind == "bound_derivation")
    derivation_argv = stage_argv(derivation, bindings, tree, root)
    corpus_manifest = value_after(derivation_argv, "--derive-neg8-drift-bound")
    corpus_runs_dir = value_after(derivation_argv, "--runs-dir")
    corpus_stage = None
    for stage in chain[:chain.index(derivation)]:
        if stage.kind == "campaign_collection" and corpus_runs_dir is not None \
                and value_after(stage_argv(stage, bindings, tree, root), "--runs-dir") == corpus_runs_dir:
            corpus_stage = stage
    prelude_gate_prune_2 = (_PRELUDE_GATE_PRUNE_2
                            .replace("@FLAG_BUDGET@", str(STAGE_WALL_BUDGET_S["flag_record"]))
                            .replace("@GRACE@", str(BUDGET_GRACE_S))
                            .replace("@EXPIRED@", str(BUDGET_EXPIRED_RC))
                            .replace("@WRITER@", CHAIN_FLAG_WRITER)
                            .replace("@HORIZON@", str(horizon_s))
                            .replace("@RESERVE@", str(HORIZON_POST_RESERVE_S))
                            .replace("@SKIPPED@", str(HORIZON_SKIPPED_RC)))

    def heredoc(name: str, source: str) -> list[str]:
        return [f"{name}=\"$(/bin/cat <<'B5_PY'", source.strip("\n"), "B5_PY", ')"']

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
        *heredoc("B5_PRUNE_PY", PRUNE_HELPER),
        *heredoc("B5_BUDGET_PY", BUDGET_HELPER),
        *heredoc("B5_FLAG_PY", FLAG_HELPER),
        *heredoc("B5_CORPUS_PY", CORPUS_RETRY_HELPER),
        '/bin/mkdir -p "$OPERATOR_LOG_ROOT" "$TRANSCRIPT_ROOT" "$CLAIM_RUNS_ROOT/instrument_validation" "$BOUND_RUNS_ROOT"',
        _PRELUDE_FUNCTIONS,
        prelude_gate_prune_2,
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

    def budgeted(budget_kind: str, argv: Sequence[str]) -> list[str]:
        """Row 8: argv under its stage's wall budget."""
        return [python, "-B", "-c", Shell('"$B5_BUDGET_PY"'), str(STAGE_WALL_BUDGET_S[budget_kind]),
                str(BUDGET_GRACE_S), str(BUDGET_EXPIRED_RC), "--", *argv]

    collection_members = [stage.expected_count if stage.kind == "campaign_collection" else 0 for stage in chain]

    def remaining(stage: Stage) -> int:
        return sum(collection_members[chain.index(stage):])

    def collection_allowance(stage: Stage) -> int:
        return SETTLE_S + HORIZON_STAGE_OVERHEAD_S + stage.expected_count * HORIZON_MEMBER_ALLOWANCE_S

    collected = Shell('"$TRANSCRIPT_ROOT/' + NEG8_COLLECTED_MANIFEST + '"')
    collected_summary = Shell('"$TRANSCRIPT_ROOT/' + NEG8_COLLECTED_SUMMARY + '"')
    lines.append("# 1. The bracket reservation. A failed reservation stops the chain.")
    lines.append(run(reservation, budgeted("bracket_reservation", reservation_argv)))
    lines.append(f"(( $? == 0 )) || stop_chain reservation_failed {EXIT_RESERVATION_FAILED}")
    lines.append("# 2. Chain-owned settle before the pre slot (runbook section 5C).")
    lines.append("settle")
    for stage in chain[1:]:
        argv = stage_argv(stage, bindings, tree, root)
        if stage is pre:
            lines.append("# 3. The pre-calibration capture and its D-079 screen; either failure stops the chain.")
            lines.append("# The collection deadline (row 17) counts from the start of this capture.")
            lines.append('PRE_CAPTURE_STARTED_EPOCH_S="$(/bin/date +%s)"')
            lines.append(f"HORIZON_DEADLINE=$(( PRE_CAPTURE_STARTED_EPOCH_S + {horizon_s} - {HORIZON_POST_RESERVE_S} ))")
            lines.append(f'[[ -e "$TRANSCRIPT_ROOT/{COLLECTION_DEADLINE_RECORD}" ]] || print -r -- '
                         '"{\\"schema\\":\\"joulewise.b5_collection_deadline.v1\\",'
                         '\\"pre_capture_started_epoch_s\\":$PRE_CAPTURE_STARTED_EPOCH_S,'
                         f'\\"horizon_s\\":{horizon_s},\\"post_reserve_s\\":{HORIZON_POST_RESERVE_S},'
                         f'\\"member_allowance_s\\":{HORIZON_MEMBER_ALLOWANCE_S},'
                         f'\\"stage_overhead_s\\":{HORIZON_STAGE_OVERHEAD_S},'
                         '\\"deadline_epoch_s\\":$HORIZON_DEADLINE}" '
                         f'> "$TRANSCRIPT_ROOT/{COLLECTION_DEADLINE_RECORD}"')
            lines.append(run(stage, budgeted("pre_calibration_capture", argv)))
            lines.append(f"(( $? == 0 )) || stop_chain pre_calibration_capture_failed {EXIT_PRE_CAPTURE_FAILED}")
            lines.append(run(stage, ["screen_pre_calibration", bindings["pre_calibration_dir"]],
                             label=stage.stage_id + ".screen", kind="pre_calibration_screen", suffix=".screen"))
            lines.append(f"(( $? == 0 )) || stop_chain pre_calibration_screen_failed {EXIT_PRE_SCREEN_FAILED}")
            lines.append("# 3b. The window calibration verdict (J1): one refit of the pre slot, synchronously,")
            lines.append("# before the first settle. Not a stop: without it every member refits, as before.")
            lines.append(run(stage, budgeted("window_calibration_verdict", [
                python, "-B", str(root / WINDOW_CALIBRATION_VERDICT_PROGRAM),
                "--pre-calibration-dir", bindings["pre_calibration_dir"]]),
                label=stage.stage_id + ".window-calibration-verdict", kind="window_calibration_verdict",
                suffix=".verdict"))
        elif stage is post:
            lines.append("# 8. The post-calibration capture (never budgeted, never skipped), then a record")
            lines.append("# (never a check) of the session status.")
            lines.append(run(stage, argv))
            if frozen_plan is not None and head_pin is not None:
                status_argv = [python, str(root / "scripts/recover_calibration_ledger.py"),
                               "--ledger", bindings["ledger_path"], "--head-pin", head_pin, "session-status",
                               "--session-id", bindings["bracket_session_id"], "--plan", frozen_plan]
                lines.append(run(stage, budgeted("session_status_record", status_argv),
                                 label=stage.stage_id + ".session-status",
                                 kind="session_status_record", suffix=".session-status",
                                 out=Shell('"$TRANSCRIPT_ROOT/' + TERMINAL_BOUNDARY + '"')))
        elif stage.kind == "campaign_collection":
            lines.append(f"# Collection stage {stage.stage_id}: {stage.expected_count} member(s).")
            lines.append(f"if horizon_allows {stage.stage_id} {collection_allowance(stage)} {remaining(stage)}; then")
            lines.append("settle")
            lines.append(run(stage, argv))
            if stage is corpus_stage and corpus_manifest is not None:
                lines += corpus_retry_lines(stage, argv, corpus_manifest, corpus_runs_dir, python,
                                            log_path, run, budgeted, collection_allowance(stage), remaining(stage))
            lines.append(f"else horizon_skip {stage.stage_id}; fi")
        elif stage.kind == "bound_derivation":
            manifest = value_after(argv, "--derive-neg8-drift-bound")
            runs_dir = value_after(argv, "--runs-dir")
            _require(argv.count("--derive-neg8-drift-bound") == 1 and manifest is not None and runs_dir is not None,
                     f"{stage.stage_id}: bound derivation names one manifest and --runs-dir")
            allowance = STAGE_WALL_BUDGET_S["neg8_corpus_collected"] + STAGE_WALL_BUDGET_S["bound_derivation"]
            lines.append("# 4b. The NEG-8 bound, from the collected corpus members that succeeded and that the")
            lines.append("# core's HAZARD mint does not drop. A pruned copy (10 or 11 of 12) derives; the")
            lines.append("# harvest validates the bound against these custodied bytes (registration 5.3).")
            lines.append(f"if horizon_allows {stage.stage_id} {allowance} {remaining(stage)}; then")
            lines.append(run(stage, budgeted("neg8_corpus_collected", [
                python, "-B", "-c", Shell('"$B5_PRUNE_PY"'), manifest, runs_dir, collected, collected_summary]),
                label=stage.stage_id + ".corpus", kind="neg8_corpus_collected", suffix=".corpus"))
            derive = list(argv)
            derive[derive.index("--derive-neg8-drift-bound") + 1] = collected
            lines.append(run(stage, budgeted("bound_derivation", derive)))
            lines.append(f"else horizon_skip {stage.stage_id}; fi")
        elif stage.kind == "bracket_reservation":  # pragma: no cover - stage_plan admits exactly one
            raise ChainRenderError(f"{stage.stage_id}: a second reservation")
    lines += ['note "chain_end"', f"exit {EXIT_COMPLETED}", ""]
    return "\n".join(lines).encode("utf-8")


def corpus_retry_lines(stage: Stage, argv: Sequence[str], manifest: str, runs_dir: str, python: str,
                       log_path: Any, run: Any, budgeted: Any, allowance: int, members_remaining: int) -> list[str]:
    """Row 13: one retry of the corpus stage when fewer than NEG8_RETRY_MINIMUM succeeded (no drain)."""

    snapshot = Shell('"$TRANSCRIPT_ROOT/' + NEG8_RETRY_SNAPSHOT + '"')
    decision_log = log_path(stage, ".retry-decision")
    retry_id = stage.stage_id + ".retry"
    count = budgeted("neg8_corpus_retry_decision", [
        python, "-B", "-c", Shell('"$B5_CORPUS_PY"'), "count", manifest, runs_dir, snapshot, str(NEG8_RETRY_MINIMUM)])
    retried = budgeted("neg8_corpus_retry_decision", [
        python, "-B", "-c", Shell('"$B5_CORPUS_PY"'), "retried", manifest, runs_dir, snapshot])
    observed = '{\\"stage_id\\":\\"' + stage.stage_id + '\\",\\"attempt\\":2}'
    return [
        f"# Row 13: one retry of the NEG-8 corpus when fewer than {NEG8_RETRY_MINIMUM} of its members succeeded.",
        'NEG8_RETRY_STARTED="$(/bin/date +%s)"',
        "NEG8_RETRY_DECISION=\"$(" + " ".join(_literal(item) for item in count) + f" 2>> {decision_log})\"",
        f'journal {retry_id}-decision neg8_corpus_retry_decision $? "$NEG8_RETRY_STARTED"',
        'note "neg8_corpus_retry decision=$NEG8_RETRY_DECISION"',
        'if [[ "$NEG8_RETRY_DECISION" == retry ]]; then',
        f"if horizon_allows {retry_id} {allowance} {members_remaining}; then",
        "settle",
        run(stage, argv, label=retry_id, suffix=".retry"),
        " ".join(_literal(item) for item in retried) + f" 2>> {decision_log} | while IFS= read -r NEG8_RETRIED; do",
        f'  flag member.retried member "$NEG8_RETRIED" "{observed}" {_literal(runs_dir)} '
        '"measured by the one corpus retry after its first attempt left no bundle"',
        "done",
        f"else horizon_skip {retry_id}; fi",
        "fi",
    ]


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
    "neg8_corpus_record", "calibration_runbook_flags", "CALIBRATION_ARM_COUNTDOWN_S", "COLLECTION_ARM_COUNTDOWN_S",
    "BUDGET_HELPER", "BUDGET_EXPIRED_RC", "STAGE_WALL_BUDGET_S", "FLAG_HELPER", "CORPUS_RETRY_HELPER",
    "WINDOW_CALIBRATION_VERDICT_BASENAME", "WINDOW_CALIBRATION_VERDICT_PROGRAM", "window_calibration_verdict_path",
    "CALIBRATION_HORIZON_S", "HORIZON_MEMBER_ALLOWANCE_S", "HORIZON_POST_RESERVE_S", "HORIZON_SKIPPED_RC",
    "COLLECTION_DEADLINE_RECORD", "NEG8_RETRY_MINIMUM", "NEG8_RETRY_SNAPSHOT", "CHAIN_FLAG_WRITER",
]
