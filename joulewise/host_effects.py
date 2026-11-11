"""Read-only shadow view of host obligations (audit 8.2.3 and 8.3).

No writer imports this module. Live settings, lock liveness, loaded labels,
process liveness and the completeness of the plan census belong to the caller.
Historical OFF receipts and lock files never establish current live state.

Only observe_host_state_dir performs filesystem I/O. Its allowlist comes from
network_time_off.py and b5/driver.py on both supported refs, and powermode.py,
launch_align_r0.py and run_align_r0_launchagent.sh on the W1 line. Main has no
powermode.py. Embedded custody_root/plan_path values are compared as text only.
Ancestor aliases (e.g. macOS /var) are resolved; the supplied root itself and
all accessed descendants are opened without following symlinks. No directory
is enumerated, no lock is acquired, and no command is executed.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import enum
import json
import math
import os
from pathlib import Path
import stat
import time
from types import MappingProxyType

try:
    from joulewise.window_state import StateReport, WindowOutcome
except ModuleNotFoundError as exc:
    if exc.name != "joulewise.window_state":
        raise
    StateReport = WindowOutcome = None


class Effect(enum.Enum):
    NETWORK_TIME_OFF = "NETWORK_TIME_OFF"
    AC_HIGH_POWER = "AC_HIGH_POWER"
    HIGH_POWER_MARKERS = "HIGH_POWER_MARKERS"
    NIGHT_PLISTS = "NIGHT_PLISTS"
    NIGHT_LOCK = "NIGHT_LOCK"
    SPOTLIGHT_STOPPED = "SPOTLIGHT_STOPPED"
    KEEP_AWAKE_AGENT = "KEEP_AWAKE_AGENT"


EXIT_CODES = MappingProxyType({"clean": 0, "owed": 1, "usage": 2, "unknown": 3})
NIGHT_LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")
KEEP_AWAKE_LABEL = "local.jwbench.keepawake"
MARKER_NAMES = ("high-power.marker", ".align-r1-high-power")
RECEIPT_NAMES = ("network_time_off.json", "network_time_off.action.json")
W1_TAG = "ALIGN v4 W1 high-power restoration required"
R1_TAG = "high-power restoration required"
OUTCOME_WORDS = frozenset({"MEASURED_OK", "MEASURED_WITH_FLAGS", "CHAIN_FAILED",
                           "REFUSED_PRE_CHAIN", "ABORTED"})
MAX_RECORD_BYTES = 65536


def _tri(value):
    if value is not None and type(value) is not bool:
        raise TypeError("observations must be True, False or None")


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def _id(value):
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise TypeError("plan id must be a nonempty string or None")


@dataclass(frozen=True)
class MarkerFact:
    name: str
    exists: bool | None = None
    owner_plan_id: str | None = None
    tag: str | None = None
    # Paths are opaque record strings, never capabilities to read more files.
    owner_plan_path: str | None = None
    owner_custody_root: str | None = None

    def __post_init__(self):
        _tri(self.exists)
        _id(self.owner_plan_id)


@dataclass(frozen=True)
class LabelFact:
    label: str
    on_disk: bool | None = None
    loaded: bool | None = None
    owner_plan_id: str | None = None
    result_present: bool | None = None

    def __post_init__(self):
        for value in (self.on_disk, self.loaded, self.result_present):
            _tri(value)
        _id(self.owner_plan_id)
        if self.label not in NIGHT_LABELS:
            raise ValueError("unrecognized night label")


@dataclass(frozen=True)
class DeskFence:
    purpose: str
    pid: int
    deadline: float
    pid_alive: bool | None = None

    def __post_init__(self):
        _tri(self.pid_alive)
        if (not isinstance(self.purpose, str) or not self.purpose.strip()
                or type(self.pid) is not int or self.pid <= 1
                or not _number(self.deadline) or self.deadline <= 0):
            raise ValueError("invalid desk fence")


@dataclass(frozen=True)
class HostFacts:
    network_time_on: bool | None = None
    ac_powermode: int | None = None
    markers: tuple[MarkerFact, ...] | None = None
    night_lock_held: bool | None = None
    labels: tuple[LabelFact, ...] = tuple(LabelFact(label) for label in NIGHT_LABELS)
    # None is an unobserved census; () explicitly says no plan span is active.
    active_plan_spans: tuple[tuple[str, float, float], ...] | None = None
    desk_fence: DeskFence | None = None
    desk_fence_observed: bool = False
    spotlight_stopped: bool | None = None
    keep_awake_agent: bool | None = None
    # Audit 4.5: keep-awake was explicitly installed "for good". It is not
    # transient night debt. Callers can withdraw that standing authorization.
    keep_awake_expected: bool | None = True
    network_time_owner_plan_id: str | None = None
    night_lock_owner_plan_id: str | None = None
    result_present: bool | None = None
    now: float | None = None
    observation_issues: tuple[tuple[Effect, str, str], ...] = ()

    def __post_init__(self):
        for value in (self.network_time_on, self.night_lock_held, self.spotlight_stopped,
                      self.keep_awake_agent, self.keep_awake_expected, self.result_present):
            _tri(value)
        if self.ac_powermode is not None and (type(self.ac_powermode) is not int or self.ac_powermode < 0):
            raise ValueError("AC power mode must be a nonnegative integer or None")
        if self.now is not None and not _number(self.now):
            raise ValueError("now must be a finite epoch or None")
        _id(self.network_time_owner_plan_id)
        _id(self.night_lock_owner_plan_id)
        if type(self.desk_fence_observed) is not bool:
            raise TypeError("desk_fence_observed must be a boolean")
        if self.desk_fence is not None and not isinstance(self.desk_fence, DeskFence):
            raise TypeError("desk_fence must be DeskFence or None")
        if self.markers is not None:
            object.__setattr__(self, "markers", tuple(self.markers))
            if not all(isinstance(m, MarkerFact) for m in self.markers):
                raise TypeError("markers must contain MarkerFact observations")
        object.__setattr__(self, "labels", tuple(self.labels))
        if (not all(isinstance(p, LabelFact) for p in self.labels)
                or {p.label for p in self.labels} != set(NIGHT_LABELS) or len(self.labels) != 2):
            raise ValueError("supply each night label exactly once")
        if self.active_plan_spans is not None:
            spans = tuple(tuple(s) for s in self.active_plan_spans)
            for plan, start, end in spans:
                _id(plan)
                if plan is None or not _number(start) or not _number(end) or start >= end:
                    raise ValueError("invalid plan span")
            object.__setattr__(self, "active_plan_spans", spans)
        object.__setattr__(self, "observation_issues", tuple(self.observation_issues))


@dataclass(frozen=True)
class Owed:
    effect: Effect
    subject: str
    is_set: bool | None
    owner_plan_id: str | None
    explained_by: str | None
    owed: bool | None
    reason: str

    @property
    def status(self):
        return "unknown" if self.owed is None else "owed" if self.owed else "explained" if self.is_set else "clear"


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    reason: str


def _active(facts, owner=None):
    if facts.active_plan_spans is None:
        return None
    if not facts.active_plan_spans:
        return False
    if facts.now is None:
        return None
    return any(start <= facts.now < end and (owner is None or plan == owner)
               for plan, start, end in facts.active_plan_spans)


def invariant_network_time_on_without_active_span(facts: HostFacts) -> Check:
    """Network time is ON whenever no plan span is active."""
    active = _active(facts)
    if facts.network_time_on is True or active is True:
        return Check("network_time_on_without_active_span", "pass", "SATISFIED")
    if facts.network_time_on is None or active is None:
        return Check("network_time_on_without_active_span", "unknown", "NETWORK_TIME_OR_SPANS_UNKNOWN")
    return Check("network_time_on_without_active_span", "violated", "NETWORK_TIME_OFF_WITHOUT_ACTIVE_SPAN")


def invariant_ac_automatic_without_night_lock(facts: HostFacts) -> Check:
    """AC power mode is 0 whenever no process holds night.lock."""
    if facts.ac_powermode == 0 or facts.night_lock_held is True:
        return Check("ac_automatic_without_night_lock", "pass", "SATISFIED")
    if facts.ac_powermode is None or facts.night_lock_held is None:
        return Check("ac_automatic_without_night_lock", "unknown", "AC_MODE_OR_LOCK_UNKNOWN")
    return Check("ac_automatic_without_night_lock", "violated", "AC_NONZERO_WITHOUT_NIGHT_LOCK")


def _outcome_word(outcome):
    if outcome is None or isinstance(outcome, str):
        return outcome
    if StateReport is not None and isinstance(outcome, StateReport):
        nested = getattr(outcome.outcome, "outcome", None)
        return nested.value if isinstance(nested, WindowOutcome) else "UNKNOWN"
    if WindowOutcome is not None and isinstance(outcome, WindowOutcome):
        return outcome.value
    return "UNKNOWN"


def invariant_terminal_night_label_uninstalled(facts: HostFacts, label: LabelFact, outcome=None) -> Check:
    """A loaded label with a result and no active span is owed an uninstall."""
    active = _active(facts, label.owner_plan_id)
    word = _outcome_word(outcome)
    result = label.result_present if label.result_present is not None else facts.result_present
    if word is not None:
        result = True if word in OUTCOME_WORDS else None
    name = "terminal_night_label_uninstalled:" + label.label
    if label.loaded is False or active is True or result is False:
        return Check(name, "pass", "SATISFIED")
    if label.loaded is None or active is None or result is None:
        return Check(name, "unknown", "LABEL_SPANS_OR_RESULT_UNKNOWN")
    return Check(name, "violated", "NIGHT_LABEL_TERMINAL_WITHOUT_ACTIVE_SPAN")


def owed_effects(facts: HostFacts, outcome=None) -> list[Owed]:
    """Pure classification. Unknowns have owed=None; never treat them as clean.

    One row per label/marker preserves two independent uninstall obligations.
    An outcome word (or optional StateReport) is structural terminal evidence;
    UNKNOWN/unrecognized words cannot prove a terminal result. No clock, process,
    environment or file is consulted. Spans are half-open [start, end).
    """
    rows = []

    def row(effect, subject, state, owner=None, explained=None, reason=None):
        if state is None:
            debt, code = None, "EFFECT_UNOBSERVED"
        elif not state:
            debt, code = False, "NOT_SET"
        elif explained is None:
            debt, code = None, reason or "EXPLANATION_UNOBSERVED"
        elif explained:
            debt, code = False, reason or "ACTIVE_PLAN_SPAN"
        else:
            debt, code = True, reason or "NO_ACTIVE_PLAN_SPAN"
        rows.append(Owed(effect, subject, state, owner,
                         code if state and explained else None, debt, code))

    active = _active(facts)
    row(Effect.NETWORK_TIME_OFF, "network_time", None if facts.network_time_on is None else not facts.network_time_on,
        facts.network_time_owner_plan_id, active,
        "ACTIVE_PLAN_SPAN" if active else "NETWORK_TIME_OFF_WITHOUT_ACTIVE_SPAN" if active is False else None)
    mode = facts.ac_powermode
    power_owners = {m.owner_plan_id for m in facts.markers or ()
                    if m.exists is True and m.owner_plan_id is not None}
    power_owner = next(iter(power_owners)) if len(power_owners) == 1 else None
    row(Effect.AC_HIGH_POWER, "ac_powermode", None if mode is None else mode != 0,
        owner=power_owner, explained=facts.night_lock_held,
        reason="NIGHT_LOCK_HELD" if facts.night_lock_held else "AC_NONZERO_WITHOUT_NIGHT_LOCK"
        if facts.night_lock_held is False else None)
    if facts.markers is None:
        row(Effect.HIGH_POWER_MARKERS, "markers", None)
    else:
        # An empty, explicitly observed inventory is clean.
        if not facts.markers:
            row(Effect.HIGH_POWER_MARKERS, "markers", False)
        for marker in facts.markers:
            own_span = _active(facts, marker.owner_plan_id)
            explained = (True if facts.night_lock_held is True else
                         True if marker.owner_plan_id is not None and own_span is True else
                         False if facts.night_lock_held is False and own_span is False else None)
            row(Effect.HIGH_POWER_MARKERS, marker.name, marker.exists, marker.owner_plan_id, explained,
                "NIGHT_LOCK_HELD" if facts.night_lock_held is True else "OWNER_PLAN_SPAN" if explained else
                "HIGH_POWER_MARKER_ORPHANED" if explained is False else None)
    word = _outcome_word(outcome)
    if word is not None and word not in OUTCOME_WORDS:
        rows.append(Owed(Effect.NIGHT_PLISTS, "outcome", None, None, None, None, "OUTCOME_UNRECOGNIZED"))
    for label in facts.labels:
        state = True if label.loaded is True or label.on_disk is True else (
            False if label.loaded is False and label.on_disk is False else None)
        own_span = _active(facts, label.owner_plan_id)
        result = label.result_present if label.result_present is not None else facts.result_present
        if word is not None:
            # An unrecognized outcome cannot waive missing result evidence.
            result = True if word in OUTCOME_WORDS else None
        explained = True if own_span is True else False if own_span is False and result is True else None
        row(Effect.NIGHT_PLISTS, label.label, state, label.owner_plan_id, explained,
            "ACTIVE_PLAN_SPAN" if explained else "NIGHT_LABEL_TERMINAL_WITHOUT_ACTIVE_SPAN"
            if explained is False else "LABEL_SPANS_OR_RESULT_UNKNOWN")
        # A known disk presence must not hide unobserved launchd state.
        if state is True and label.loaded is None:
            row(Effect.NIGHT_PLISTS, label.label + ":loaded", None)
        if state is True and label.on_disk is None:
            row(Effect.NIGHT_PLISTS, label.label + ":on_disk", None)
    lock_active = _active(facts, facts.night_lock_owner_plan_id)
    row(Effect.NIGHT_LOCK, "night.lock", facts.night_lock_held, facts.night_lock_owner_plan_id, lock_active,
        "ACTIVE_PLAN_SPAN" if lock_active else "NIGHT_LOCK_WITHOUT_ACTIVE_SPAN" if lock_active is False else None)
    fence = facts.desk_fence
    fence_active = None
    if fence is not None:
        if fence.pid_alive is False or (facts.now is not None and facts.now >= fence.deadline):
            fence_active = False
        elif fence.pid_alive is True and facts.now is not None:
            fence_active = True
    elif facts.desk_fence_observed:
        fence_active = False
    row(Effect.SPOTLIGHT_STOPPED, "spotlight", facts.spotlight_stopped, explained=fence_active,
        reason="LIVE_DESK_FENCE" if fence_active else "SPOTLIGHT_WITHOUT_LIVE_DESK_FENCE"
        if fence_active is False else None)
    row(Effect.KEEP_AWAKE_AGENT, KEEP_AWAKE_LABEL, facts.keep_awake_agent,
        explained=facts.keep_awake_expected, reason="STANDING_KEEP_AWAKE_AUTHORIZATION"
        if facts.keep_awake_expected else "KEEP_AWAKE_AUTHORIZATION_WITHDRAWN"
        if facts.keep_awake_expected is False else None)
    for effect, subject, reason in facts.observation_issues:
        rows.append(Owed(effect, subject, None, None, None, None, reason))
    return rows


def observe_host_state_dir(directory, *, plan_dirs=()) -> HostFacts:
    """Read fixed structural names only; return partial facts, never live facts.

    plan_dirs are explicitly supplied custody/measurement/LaunchAgents/job roots.
    They are not discovered from marker strings. Their plan records help match
    marker owners but do not prove an exhaustive host plan census. Result files
    are tested for presence only. A surviving Spotlight PID receipt is historical,
    not proof of a currently stopped process. Errors remain unknown observations.
    """
    issues = []
    markers = []
    receipts = []
    plans = []
    disk = {label: [] for label in NIGHT_LABELS}
    fence = None
    fence_observed = False

    def issue(effect, subject, reason):
        issues.append((effect, subject, reason))

    def open_root(value):
        path = Path(value).absolute()
        # Resolve ancestors only: /var and /tmp may be aliases on macOS.
        path = path.parent.resolve(strict=True) / path.name
        return path, os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)

    def read(root_fd, relative, *, presence_only=False):
        """Descriptor-relative traversal prevents a symlink swap after checking."""
        fd = os.dup(root_fd)
        try:
            parts = relative.split("/")
            for part in parts[:-1]:
                new = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = new
            leaf = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            try:
                if not stat.S_ISREG(os.fstat(leaf).st_mode):
                    raise ValueError("allowlisted entry is not a regular file: " + relative)
                if presence_only:
                    return True
                with os.fdopen(leaf, "rb", closefd=False) as handle:
                    raw = handle.read(MAX_RECORD_BYTES + 1)
                if len(raw) > MAX_RECORD_BYTES:
                    raise ValueError("allowlisted entry exceeds size limit: " + relative)
                return raw.decode("utf-8")
            finally:
                os.close(leaf)
        except FileNotFoundError:
            return False if presence_only else None
        finally:
            os.close(fd)

    roots = (directory, *plan_dirs)
    for index, root in enumerate(roots):
        try:
            path, root_fd = open_root(root)
        except (FileNotFoundError, PermissionError):
            issue(Effect.HIGH_POWER_MARKERS, str(root), "DIRECTORY_UNOBSERVED")
            continue
        try:
            def get(name, effect, *, presence=False):
                try:
                    return read(root_fd, name, presence_only=presence)
                except OSError as exc:
                    # ELOOP and symlinked intermediate directories are refused,
                    # not followed. No failed read is an absence observation.
                    import errno
                    if exc.errno in (errno.ELOOP, errno.ENOTDIR):
                        raise ValueError("symlink or non-directory refused: " + name) from exc
                    issue(effect, str(path / name), "RECORD_UNREADABLE")
                    return None
                except (ValueError, UnicodeError):
                    issue(effect, str(path / name), "RECORD_UNREADABLE")
                    return None

            def document(name, effect):
                raw = get(name, effect)
                if raw is None:
                    return None
                try:
                    doc = json.loads(raw)
                    if not isinstance(doc, dict):
                        raise ValueError("not an object")
                    return doc
                except ValueError:
                    issue(effect, str(path / name), "RECORD_MALFORMED")
                    return None

            for name in MARKER_NAMES:
                raw = get(name, Effect.HIGH_POWER_MARKERS)
                exists = get(name, Effect.HIGH_POWER_MARKERS, presence=True)
                tag, owner = None, {}
                if raw is not None:
                    lines = raw.splitlines()
                    tag = lines[0] if lines else None
                    try:
                        owner = json.loads(lines[1]) if len(lines) > 1 else {}
                        if not isinstance(owner, dict):
                            raise ValueError("not an owner object")
                    except ValueError:
                        owner = {}
                        issue(Effect.HIGH_POWER_MARKERS, str(path / name), "MARKER_OWNER_MALFORMED")
                    if not (tag and (tag.startswith(W1_TAG) or tag == R1_TAG)):
                        issue(Effect.HIGH_POWER_MARKERS, str(path / name), "MARKER_TAG_UNRECOGNIZED")
                if any(key in owner and (not isinstance(owner[key], str) or not owner[key].strip())
                       for key in ("plan_id", "plan_path", "custody_root")):
                    issue(Effect.HIGH_POWER_MARKERS, str(path / name), "MARKER_OWNER_MALFORMED")
                def text(key):
                    value = owner.get(key)
                    return value if isinstance(value, str) and value.strip() else None
                markers.append(MarkerFact(str(path / name), exists, text("plan_id"), tag,
                                          text("plan_path"), text("custody_root")))
            # Never infer flock liveness from this (possibly stale) note.
            get("night.lock", Effect.NIGHT_LOCK, presence=True)
            plan = document("night_plan.json", Effect.NIGHT_PLISTS)
            result = get("night/result.json", Effect.NIGHT_PLISTS, presence=True)
            if plan is not None:
                plan_id = plan.get("plan_id")
                if isinstance(plan_id, str) and plan_id.strip():
                    plans.append((plan_id, str(path / "night_plan.json"), str(path), result))
                else:
                    issue(Effect.NIGHT_PLISTS, str(path / "night_plan.json"), "PLAN_ID_UNRECOGNIZED")
            for label in NIGHT_LABELS:
                disk[label].append(get(label + ".plist", Effect.NIGHT_PLISTS, presence=True))
            for prefix in ("", "night/"):
                for name in RECEIPT_NAMES:
                    receipt = document(prefix + name, Effect.NETWORK_TIME_OFF)
                    if receipt is not None:
                        legacy = name == "network_time_off.json"
                        code = receipt.get("exit_code" if legacy else "returncode")
                        schema = "joulewise.network_time_off.v1" if legacy else "joulewise.b5_network_time_off_action.v1"
                        if (receipt.get("schema") != schema or type(code) is not int or code != 0
                                or receipt.get("error") or receipt.get("timed_out")
                                or not isinstance(receipt.get("plan_id", ""), str)):
                            issue(Effect.NETWORK_TIME_OFF, str(path / (prefix + name)), "OFF_RECEIPT_UNCONFIRMED")
                        else:
                            receipts.append((receipt, plan.get("plan_id") if plan else None))
            if index == 0:
                record = document("desk_fence.json", Effect.SPOTLIGHT_STOPPED)
                fence_observed = not any(s == str(path / "desk_fence.json") for _, s, _ in issues)
                if record is not None:
                    try:
                        fence = DeskFence(record["purpose"], record["pid"], record["deadline"])
                    except (KeyError, ValueError, TypeError):
                        fence_observed = False
                        issue(Effect.SPOTLIGHT_STOPPED, "desk_fence.json", "DESK_FENCE_MALFORMED")
            get("spotlight-stopped", Effect.SPOTLIGHT_STOPPED, presence=True)
        finally:
            os.close(root_fd)
    matched = []
    for marker in markers:
        owners = {p for p, plan_path, custody, _ in plans
                  if (marker.owner_plan_path is not None and marker.owner_plan_path == plan_path)
                  or (marker.owner_custody_root is not None and marker.owner_custody_root == custody)}
        if marker.owner_plan_id is not None:
            owners.add(marker.owner_plan_id)
        if len(owners) > 1:
            issue(Effect.HIGH_POWER_MARKERS, marker.name, "MARKER_OWNER_CONFLICT")
        matched.append(replace(marker, owner_plan_id=next(iter(owners)) if len(owners) == 1 else None))
    owners = {doc.get("plan_id", plan_id) for doc, plan_id in receipts}
    owners = {owner for owner in owners if isinstance(owner, str) and owner.strip()}
    if len(owners) > 1:
        issue(Effect.NETWORK_TIME_OFF, "receipts", "NETWORK_TIME_OWNER_CONFLICT")
    # Missing roots mean the inventory is incomplete, even if another was read.
    if any(reason == "DIRECTORY_UNOBSERVED" for _, _, reason in issues):
        for label in NIGHT_LABELS:
            disk[label].append(None)
    unique_plans = {p for p, _, _, _ in plans}
    owner = next(iter(unique_plans)) if len(unique_plans) == 1 else None
    results = [r for _, _, _, r in plans]
    result = (True if True in results else False if results and all(r is False for r in results) else None)
    labels = tuple(LabelFact(label, True if True in disk[label] else
                             False if disk[label] and all(v is False for v in disk[label]) else None,
                             owner_plan_id=owner, result_present=result if owner else None)
                   for label in NIGHT_LABELS)
    return HostFacts(markers=tuple(matched) if matched else None, labels=labels,
                     desk_fence=fence, desk_fence_observed=fence_observed,
                     network_time_owner_plan_id=next(iter(owners)) if len(owners) == 1 else None,
                     observation_issues=tuple(issues))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", required=True)
    parser.add_argument("--plan-dir", action="append", default=[])
    parser.add_argument("--network-time", choices=("on", "off", "unknown"), default="unknown")
    parser.add_argument("--ac-powermode", type=int)
    parser.add_argument("--loaded-label", action="extend", nargs="+", choices=(*NIGHT_LABELS, KEEP_AWAKE_LABEL), default=None,
                        help="repeat for a COMPLETE loaded-label census; use --no-loaded-labels for empty")
    parser.add_argument("--no-loaded-labels", action="store_true")
    parser.add_argument("--night-lock", choices=("held", "free", "unknown"), default="unknown")
    parser.add_argument("--no-active-spans", action="store_true")
    parser.add_argument("--active-plan", nargs=3, action="append", default=[], metavar=("PLAN", "START", "END"))
    parser.add_argument("--spotlight", choices=("stopped", "running", "unknown"), default="unknown")
    parser.add_argument("--keep-awake", choices=("loaded", "unloaded", "unknown"), default="unknown")
    parser.add_argument("--keep-awake-expected", choices=("yes", "no", "unknown"), default="yes")
    parser.add_argument("--outcome", help="optional structural outcome word; unknown words remain unknown")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.no_active_spans and args.active_plan:
        parser.error("--no-active-spans conflicts with --active-plan")
    if args.no_loaded_labels and args.loaded_label:
        parser.error("--no-loaded-labels conflicts with --loaded-label")
    try:
        facts = observe_host_state_dir(args.state_dir, plan_dirs=args.plan_dir)
        loaded = set(args.loaded_label or ()) if args.loaded_label is not None or args.no_loaded_labels else None
        if loaded is not None and args.keep_awake != "unknown" and (
                (KEEP_AWAKE_LABEL in loaded) != (args.keep_awake == "loaded")):
            parser.error("--keep-awake conflicts with the loaded-label census")
        spans = tuple((p, float(s), float(e)) for p, s, e in args.active_plan) if args.active_plan else (
            () if args.no_active_spans else None)
        facts = replace(facts, network_time_on={"on": True, "off": False}.get(args.network_time),
                        ac_powermode=args.ac_powermode, night_lock_held={"held": True, "free": False}.get(args.night_lock),
                        active_plan_spans=spans, now=time.time(),
                        labels=tuple(replace(p, loaded=p.label in loaded) if loaded is not None else p for p in facts.labels),
                        spotlight_stopped={"stopped": True, "running": False}.get(args.spotlight),
                        keep_awake_agent=KEEP_AWAKE_LABEL in loaded if loaded is not None else
                        {"loaded": True, "unloaded": False}.get(args.keep_awake),
                        keep_awake_expected={"yes": True, "no": False}.get(args.keep_awake_expected))
    except (OSError, ValueError, TypeError) as exc:
        parser.error(str(exc))
    rows = owed_effects(facts, args.outcome)
    def data(row):
        return {"effect": row.effect.value, "subject": row.subject, "is_set": row.is_set,
                "owner_plan_id": row.owner_plan_id, "explained_by": row.explained_by,
                "owed": row.owed, "status": row.status, "reason": row.reason}
    owed = [data(r) for r in rows if r.owed is True]
    unknowns = [data(r) for r in rows if r.owed is None]
    if args.json:
        print(json.dumps({"owed": owed, "unknowns": unknowns, "effects": [data(r) for r in rows]}, sort_keys=True))
    else:
        for row in owed + unknowns:
            print(f"{row['status']} {row['effect']} {row['subject']}: {row['reason']}")
        if not owed and not unknowns:
            print("No owed effects or unknowns.")
    return EXIT_CODES["owed"] if owed else EXIT_CODES["unknown"] if unknowns else EXIT_CODES["clean"]


if __name__ == "__main__":
    raise SystemExit(main())
