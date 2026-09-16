"""Transactional night-agent publication and recovery (system Python 3.9).

Only LaunchctlAdapter invokes launchctl. Liveness is a typed Outcome; only an
exact absence result can mint a directory/label/generation-bound Absent proof.
Plist publication, removal and restoration have separate, narrow capabilities.
The transaction's one finally dispatches on state, including after output fails.
"""

import argparse
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
from typing import Optional
from xml.sax.saxutils import escape


LABELS = ("com.joulewise.night", "com.joulewise.night.deadman")
SIGNALS = (signal.SIGINT, signal.SIGTERM, signal.SIGHUP)


class Kind(Enum):
    SUCCEEDED = auto()
    FAILED = auto()
    LOADED = auto()
    ABSENT = auto()
    UNKNOWN = auto()


@dataclass(frozen=True)
class Outcome:
    kind: Kind
    rc: Optional[int] = None
    stdout: str = ""
    stderr: str = ""

    def __bool__(self):
        raise TypeError("Outcome requires an explicit kind comparison")


@dataclass(frozen=True)
class Liveness(Outcome):
    def __post_init__(self):
        if self.kind not in (Kind.LOADED, Kind.ABSENT, Kind.UNKNOWN):
            raise TypeError("not a liveness outcome")


class Refused(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


class Signalled(BaseException):
    def __init__(self, code):
        self.code = code


class NotAbsent(Exception):
    def __init__(self, label, liveness):
        self.label, self.liveness = label, liveness
        super().__init__("{} state={}".format(label, liveness.kind.name.lower()))


_PROOF_KEY = object()
_TARGET_KEY = object()


@dataclass(frozen=True)
class Absent:
    """Minted only by require_absent; invalid after any subsequent mutation."""
    target: object
    label: str
    generation: int
    key: object

    def __post_init__(self):
        if self.key is not _PROOF_KEY:
            raise TypeError("Absent requires require_absent")


class Target:
    def __init__(self, directory, labels, key):
        if key is not _TARGET_KEY:
            raise TypeError("construct targets with Target.for_mode")
        self.directory = Path(directory).resolve()
        self.labels = tuple(labels)
        if not self.labels or len(set(self.labels)) != len(self.labels):
            raise ValueError("labels must be nonempty and unique")
        if any(not re.fullmatch(r"[A-Za-z0-9_.-]+", label) for label in self.labels):
            raise ValueError("invalid label")
        self.generation = 0
        self.priors = {}

    @staticmethod
    def for_mode(launch_dir, render_dir=None, labels=LABELS):
        launch_dir = Path(launch_dir).resolve()
        if render_dir is None:
            return LaunchdTarget(launch_dir, labels, _TARGET_KEY)
        render_dir = Path(render_dir).resolve()
        if render_dir == launch_dir:
            raise Refused(2, "--render-only directory must differ from launch_dir")
        return RenderTarget(render_dir, labels, _TARGET_KEY)

    def path(self, label):
        if label not in self.labels:
            raise TypeError("label outside target")
        return self.directory / (label + ".plist")

    def sidecar(self, label):
        return self.path(label).with_suffix(".plist.prior")

    def validate(self):
        for label in self.labels:
            for path in (self.path(label), self.sidecar(label)):
                try:
                    mode = path.lstat().st_mode
                except FileNotFoundError:
                    continue
                if not stat.S_ISREG(mode):
                    raise Refused(2, "unsupported plist destination: {}".format(path))
            # A previous interrupted transaction's journal must not be clobbered.
            if self.sidecar(label).exists():
                raise Refused(3, "retained prior plist: {}; re-run --uninstall".format(self.sidecar(label)))

    def stage(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        for label in self.labels:
            path, prior = self.path(label), self.sidecar(label)
            if path.exists():
                # Register only a complete snapshot. No publication occurs until
                # every snapshot succeeds, so an interrupted copy is harmless.
                shutil.copy2(path, prior)
                self.priors[label] = prior
            else:
                self.priors[label] = None

    def _authorize(self, label, proof):
        self.path(label)
        if isinstance(self, LaunchdTarget):
            if (not isinstance(proof, Absent) or proof.key is not _PROOF_KEY
                    or proof.target is not self or proof.label != label
                    or proof.generation != self.generation):
                raise TypeError("plist deletion/restoration requires current Absent proof")
        elif not isinstance(self, RenderTarget) or proof is not None:
            raise TypeError("invalid render proof")

    def remove_plist(self, label, proof: Absent):
        self._authorize(label, proof)
        self.path(label).unlink(missing_ok=True)

    def restore_prior(self, label, proof: Absent):
        self._authorize(label, proof)
        prior = self.priors[label]
        if prior is None:
            self.remove_plist(label, proof)
        else:
            # Same-directory atomic restoration; keep the journal until every
            # restore succeeds. copy2 preserves bytes, mode and nanosecond mtime.
            temporary = self._temporary(label)
            try:
                shutil.copy2(prior, temporary)
                os.replace(temporary, self.path(label))
            except BaseException:
                temporary.unlink(missing_ok=True)
                raise

    def _temporary(self, label):
        fd, name = tempfile.mkstemp(prefix=self.path(label).name + ".", suffix=".tmp",
                                    dir=str(self.directory))
        os.close(fd)
        return Path(name)

    def discard_priors(self):
        for label in self.labels:
            self.sidecar(label).unlink(missing_ok=True)


class LaunchdTarget(Target):
    pass


class RenderTarget(Target):
    pass


class LaunchctlAdapter:
    def __init__(self, target, executable="launchctl", uid=None, timeout=5):
        if type(target) is not LaunchdTarget:
            raise TypeError("LaunchctlAdapter requires LaunchdTarget")
        self.target = target
        self.executable = executable
        self.uid = os.getuid() if uid is None else uid
        self.timeout = timeout
        self.outcomes = []

    def _invoke(self, verb, label):
        path = self.target.path(label)
        domain = "gui/{}".format(self.uid)
        args = ([domain, str(path)] if verb == "bootstrap" else [domain + "/" + label])
        try:
            result = subprocess.run([self.executable, verb] + args, capture_output=True,
                                    text=True, timeout=self.timeout, check=False)
            outcome = Outcome(Kind.SUCCEEDED if result.returncode == 0 else Kind.FAILED,
                              result.returncode, result.stdout, result.stderr)
        except subprocess.TimeoutExpired as exc:
            # Preserve partial diagnostics without trusting a truncated query.
            def decoded(value):
                return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else (value or "")
            outcome = Outcome(Kind.UNKNOWN, None, decoded(exc.stdout),
                              decoded(exc.stderr) + "\nTimeoutExpired: {}".format(exc))
        except (OSError, UnicodeError) as exc:
            outcome = Outcome(Kind.UNKNOWN, None, "", "{}: {}".format(type(exc).__name__, exc))
        self.outcomes.append((verb, label, outcome))
        return outcome

    def print(self, label) -> Liveness:
        result = self._invoke("print", label)
        signature = 'Could not find service "{}" in domain for user gui: {}'.format(label, self.uid)
        if result.rc == 0:
            kind = Kind.LOADED
        elif result.rc == 113 and signature in result.stderr.splitlines():
            kind = Kind.ABSENT
        else:
            kind = Kind.UNKNOWN
        return Liveness(kind, result.rc, result.stdout, result.stderr)

    def require_absent(self, label) -> Absent:
        observed = self.print(label)
        if observed.kind is not Kind.ABSENT:
            raise NotAbsent(label, observed)
        return Absent(self.target, label, self.target.generation, _PROOF_KEY)

    def write_plist(self, label, payload) -> Outcome:
        """The sole publisher. Publication is not deletion (ruling R2)."""
        temporary = None
        try:
            temporary = self.target._temporary(label)
            temporary.write_bytes(payload)
            temporary.chmod(0o644)
            os.replace(temporary, self.target.path(label))
        except OSError as exc:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            return Outcome(Kind.FAILED, exc.errno, "", "{}: {}".format(type(exc).__name__, exc))
        except BaseException:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            raise
        return Outcome(Kind.SUCCEEDED, 0)

    def bootstrap(self, label) -> Outcome:
        if not all(self.target.path(item).is_file() for item in self.target.labels):
            raise TypeError("bootstrap requires both published plists")
        self.target.generation += 1
        return self._invoke("bootstrap", label)

    def bootout(self, label) -> Outcome:
        self.target.generation += 1
        return self._invoke("bootout", label)


class NullAdapter(LaunchctlAdapter):
    def __init__(self, target):
        if type(target) is not RenderTarget:
            raise TypeError("NullAdapter requires RenderTarget")
        self.target = target
        self.outcomes = []

    def _invoke(self, verb, label):
        raise TypeError("render-only called launchctl")

    def print(self, label):
        raise TypeError("render-only called launchctl")

    def bootstrap(self, label):
        raise TypeError("render-only called launchctl")

    def bootout(self, label):
        raise TypeError("render-only called launchctl")


def verified_bootout(adapter, labels):
    """Mutator results are evidence, never absence proofs; query the whole set."""
    for label in labels:
        adapter.bootout(label)
    proofs, unresolved = {}, {}
    for label in labels:
        try:
            proofs[label] = adapter.require_absent(label)
        except NotAbsent as exc:
            unresolved[label] = exc.liveness
    return proofs, unresolved


class State(Enum):
    PARSED = auto()
    VALIDATED = auto()
    ADMITTED = auto()
    STAGED = auto()
    PUBLISHED = auto()
    NIGHT_LOADED = auto()
    DEADMAN_LOADED = auto()
    VERIFIED = auto()
    COMMITTED = auto()
    SUCCESS = auto()
    REFUSED = auto()
    ROLLED_BACK = auto()
    RETAINED = auto()


class Transaction:
    def __init__(self, adapter, validate, clock=None, stdout=None, stderr=None):
        self.adapter, self.target = adapter, adapter.target
        if isinstance(self.target, RenderTarget) and type(adapter) is not NullAdapter:
            raise TypeError("render-only requires NullAdapter")
        self.validate = validate
        self.clock = clock or time.time
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.state = State.PARSED
        self.result = 1
        self.handlers = {}
        self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
        self.prepared = None
        self.selected_span_close = None

    def _say(self, message, error=False):
        print(message, file=self.stderr if error else self.stdout, flush=True)

    def _warn(self, message):
        try:
            self._say(message, error=True)
        except BaseException:
            pass

    def _enter(self, state):
        self.state = state

    def _install_handlers(self):
        def raised(number, frame):
            signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
            raise Signalled(128 + number)
        for number in SIGNALS:
            self.handlers[number] = signal.getsignal(number)
            signal.signal(number, raised)

    def _unknowns(self, unresolved):
        for label, observed in unresolved.items():
            if observed.kind is Kind.UNKNOWN:
                first = observed.stderr.splitlines()
                self._warn("liveness_unknown: {} rc={} stderr={}".format(
                    label, observed.rc, first[0] if first else ""))

    def _paths(self):
        return " ".join(str(self.target.path(label)) for label in self.target.labels)

    def _restore(self, proofs):
        for label in self.target.priors:
            self.target.restore_prior(label, proofs.get(label))
        self.target.discard_priors()

    def _teardown(self):
        # Positive state dispatch: exceptions (including stdout failure) do not
        # choose rollback. COMMITTED is irrevocable and has no launchctl calls.
        if self.state is State.COMMITTED:
            try:
                self.target.discard_priors()
            except BaseException as exc:
                self._warn("warning: prior sidecars not removed: {}".format(exc))
            self.state, self.result = State.SUCCESS, 0
        elif self.state in (State.PARSED, State.VALIDATED, State.ADMITTED):
            self.state = State.REFUSED
        elif self.state in (State.STAGED, State.PUBLISHED, State.NIGHT_LOADED,
                            State.DEADMAN_LOADED, State.VERIFIED):
            proofs, unresolved = {}, {}
            if isinstance(self.target, LaunchdTarget):
                if self.state in (State.NIGHT_LOADED, State.DEADMAN_LOADED, State.VERIFIED):
                    proofs, unresolved = verified_bootout(self.adapter, self.target.labels)
                else:
                    for label in self.target.labels:
                        try:
                            proofs[label] = self.adapter.require_absent(label)
                        except NotAbsent as exc:
                            unresolved[label] = exc.liveness
            if unresolved:
                self.state, self.result = State.RETAINED, 4
                statuses = ["{} loaded={}".format(label, int(label in unresolved))
                            for label in self.target.labels]
                self._warn("teardown: {}; retained plists: {}".format("; ".join(statuses), self._paths()))
                self._unknowns(unresolved)
            else:
                try:
                    self._restore(proofs)
                    self.state = State.ROLLED_BACK
                except BaseException as exc:
                    self.state, self.result = State.RETAINED, 1
                    self._warn("restore failed; retained prior sidecars: {}: {}".format(type(exc).__name__, exc))

    def _unwind(self):
        for _ in range(2):
            try:
                signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
                break
            except Signalled:
                # The handler already blocked SIGNALS. Retry without replacing
                # the original failure or a completed transaction's result.
                continue
        self._teardown()
        # Discard queued repetitions while blocked. They must not re-enter the
        # transaction or replace its result after the unwind has completed.
        for number in self.handlers:
            signal.signal(number, signal.SIG_IGN)
        signal.pthread_sigmask(signal.SIG_SETMASK, self.entry_mask)
        for number, handler in self.handlers.items():
            signal.signal(number, handler)

    def _commit(self):
        now = self.clock()
        if now >= min(self.selected_span_close, self.prepared.schedule["install_close_epoch_s"]):
            raise Refused(2, self.prepared.timing("install_span_closed", now,
                          "selected_span_close_epoch_s={}".format(self.selected_span_close)))
        self._enter(State.COMMITTED)

    def run(self):
        self.entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
        try:
            self.prepared = self.validate()
            self.target.validate()
            self._enter(State.VALIDATED)
            if isinstance(self.target, LaunchdTarget):
                for label in self.target.labels:
                    try:
                        self.adapter.require_absent(label)
                    except NotAbsent as exc:
                        detail = "label={}".format(label)
                        if exc.liveness.kind is Kind.UNKNOWN:
                            detail += " state=unknown rc={} stderr={}".format(exc.liveness.rc, exc.liveness.stderr)
                        raise Refused(3, self.prepared.timing("night_agent_already_loaded", self.clock(), detail))
            self.selected_span_close = self.prepared.admit(self.clock())
            self._enter(State.ADMITTED)
            self._install_handlers()
            self._enter(State.STAGED)
            self.target.stage()
            self.prepared.custody_night.mkdir(parents=True, exist_ok=True)
            for label, payload in self.prepared.render(self.target.labels):
                result = self.adapter.write_plist(label, payload)
                if result.kind is not Kind.SUCCEEDED:
                    raise Refused(1, result.stderr)
            self._enter(State.PUBLISHED)
            if isinstance(self.target, LaunchdTarget):
                for index, label in enumerate(self.target.labels):
                    self._enter(State.NIGHT_LOADED if index == 0 else State.DEADMAN_LOADED)
                    result = self.adapter.bootstrap(label)
                    if result.kind is not Kind.SUCCEEDED:
                        raise Refused(3, "failed to bootstrap {}".format(label))
                observed = [self.adapter.print(label) for label in self.target.labels]
                if any(value.kind is not Kind.LOADED for value in observed):
                    raise Refused(3, "launch agent verification failed")
            self._enter(State.VERIFIED)
            self._commit()
            try:
                self._say(self.prepared.pins)
            except BrokenPipeError:
                # COMMITTED must report success even when the reader closes.
                # A failed flush leaves buffered bytes for Python's shutdown
                # flush, which would otherwise replace exit 0 with exit 120.
                with open(os.devnull, "wb") as sink:
                    os.dup2(sink.fileno(), 1)
        except Refused as exc:
            self.result = exc.code
            self._warn(str(exc))
        except Signalled as exc:
            self.result = exc.code
        except KeyboardInterrupt:
            self.result = 130
        except BaseException as exc:
            self.result = 1
            self._warn("{}: {}".format(type(exc).__name__, exc))
        finally:
            self._unwind()
        return self.result


def uninstall(adapter, stderr=None):
    """System-interpreter recovery: no plan, driver, pins or venv imports."""
    entry_mask = signal.pthread_sigmask(signal.SIG_BLOCK, ())
    if type(adapter) is NullAdapter:
        raise TypeError("render-only and uninstall are mutually exclusive")
    sink = stderr or sys.stderr
    machine = Transaction(adapter, None, stderr=sink)
    machine.entry_mask = entry_mask
    # Nothing has mutated yet. Block before installing our raising handlers,
    # so no handler-to-block sliver exists; handlers serve only drain/restore.
    signal.pthread_sigmask(signal.SIG_BLOCK, SIGNALS)
    try:
        machine._install_handlers()
        proofs, unresolved = verified_bootout(adapter, adapter.target.labels)
        if unresolved:
            machine._warn("uninstall: still loaded after bootout: {}; retained plists: {}".format(
                " ".join(unresolved), machine._paths()))
            machine._unknowns(unresolved)
            return 4
        for label in adapter.target.labels:
            adapter.target.remove_plist(label, proofs[label])
        adapter.target.discard_priors()
        return 0
    except BaseException as exc:
        machine._warn("uninstall failed: {}: {}".format(type(exc).__name__, exc))
        return 1
    finally:
        for number in machine.handlers:
            signal.signal(number, signal.SIG_IGN)
        signal.pthread_sigmask(signal.SIG_SETMASK, machine.entry_mask)
        for number, handler in machine.handlers.items():
            signal.signal(number, handler)


@dataclass
class Prepared:
    plan: object
    plan_path: Path
    repo: Path
    python: str
    template: str
    courier: str
    courier_path: str
    schedule: dict
    spans_for_day: object

    @property
    def custody_night(self):
        return Path(self.plan.custody_root) / "night"

    @property
    def pins(self):
        return "validated pins: repo_head={} measurement_root={} measurement_head={}".format(
            self.plan.repo_head, self.plan.measurement_root, self.plan.measurement_head)

    def timing(self, reason, now, detail=""):
        epochs = [("now_epoch_s", now)] + [(name, self.schedule[name]) for name in
                  ("t0_epoch_s", "install_close_epoch_s", "deadman_epoch_s")]
        summary = "; ".join("{}={} ({})".format(name, epoch,
                    datetime.fromtimestamp(epoch).astimezone().isoformat()) for name, epoch in epochs)
        return "{}: {}; {}".format(reason, summary, detail)

    def admit(self, now):
        if self.plan_path != (Path(self.plan.custody_root) / "night_plan.json").resolve():
            raise Refused(2, self.timing("plan_outside_custody_root", now,
                          "plan={}; expected={}".format(self.plan_path,
                          (Path(self.plan.custody_root) / "night_plan.json").resolve())))
        if self.schedule["t0_epoch_s"] < now:
            raise Refused(2, self.timing("plan_t0_in_the_past", now))
        if now >= self.schedule["install_close_epoch_s"]:
            raise Refused(2, self.timing("install_span_closed", now))
        # Re-resolve on the admission date, not the earlier schedule subprocess date.
        try:
            spans = self.spans_for_day(datetime.fromtimestamp(now).astimezone().date())
        except ValueError as exc:
            raise Refused(2, "{}: {}".format(getattr(exc, "reason", "plan_schedule_unrepresentable"), exc))
        selected = next((closing for opening, closing in spans if opening <= now < closing), None)
        if selected is None:
            raise Refused(2, self.timing("install_outside_span", now, "install_spans_today=" + repr([
                tuple("{} ({})".format(epoch, datetime.fromtimestamp(epoch).astimezone().isoformat())
                      for epoch in span) for span in spans])))
        return selected

    def render(self, labels):
        for index, label in enumerate(labels):
            mode = "run" if index == 0 else "dead-man"
            calendar = self.schedule["night_calendar" if index == 0 else "deadman_calendar"]
            text = self.template
            if index:
                for field in ("Month", "Day"):
                    text = re.sub(r"    <key>" + field + r"</key>\n    <integer>@@[A-Z]+@@</integer>\n", "", text)
            values = {"com.joulewise.night": label, "@@PYTHON@@": self.python,
                      "@@MODE@@": mode, "@@REPO@@": str(self.repo), "@@PLAN@@": str(self.plan_path),
                      "@@CUSTODY_ROOT@@": self.plan.custody_root, "@@COURIER_BIN@@": self.courier,
                      "@@PATH@@": self.courier_path,
                      "@@LOG_STEM@@": "launchd.deadman" if index else "launchd.night"}
            values.update({"@@{}@@".format(key.upper()): str(value) for key, value in calendar.items()})
            yield label, re.sub(r"com\.joulewise\.night|@@[A-Z_]+@@",
                lambda match: escape(values.get(match.group(0), match.group(0))), text).encode("utf-8")


def validate_install(args, repo):
    # Import only on the install path, after the shell's MIN_PYTHON probe.
    from joulewise.night_gate import NightPlan, PLAN_MAX_AGE_S, PlanError

    template_path = repo / "configs/launchd/com.joulewise.night.plist.template"
    if not template_path.is_file():
        raise Refused(2, "template not found: {}".format(template_path))
    template = template_path.read_text(encoding="utf-8")
    if "KeepAlive" in template:
        raise Refused(3, "template must not contain KeepAlive")
    try:
        plan = NightPlan.from_mapping(json.loads(args.plan.read_text(encoding="utf-8")))
        if plan.measurement_root != plan.measurement_root.strip():
            raise PlanError("night_plan_malformed", "measurement_root must be an absolute path with no surrounding whitespace")
        now = time.time()
        if plan.authored_epoch_s > now:
            raise PlanError("night_plan_malformed", "plan authored_epoch_s is in the future")
        if now - plan.authored_epoch_s > PLAN_MAX_AGE_S:
            raise PlanError("night_plan_stale", "plan is older than 36 hours")
    except (PlanError, ValueError) as exc:
        raise Refused(3, "{}: {}".format(getattr(exc, "reason", "night_plan_malformed"), exc))
    for name, root, expected in (("repo_head", repo, plan.repo_head),
                                 ("measurement_head", plan.measurement_root, plan.measurement_head)):
        result = subprocess.run(["/usr/bin/git", "-C", str(root), "rev-parse", "HEAD"],
                                capture_output=True, text=True, check=False)
        checkout = "driver" if name == "repo_head" else "measurement"
        if result.returncode:
            raise Refused(3, "unable to read {} from {} checkout".format(name, checkout))
        if result.stdout.strip() != expected:
            raise Refused(3, "plan {} does not match {} checkout HEAD".format(name, checkout))
    courier = shutil.which("claude")
    if not courier:
        raise Refused(2, "courier unavailable: command -v claude found no executable")
    courier_path = str(Path(courier).parent) + ":/usr/bin:/bin:/usr/sbin:/sbin"
    python = args.python or sys.executable
    result = subprocess.run([python, "-B", str(repo / "scripts/run_night.py"), "preflight", "--plan", str(args.plan)],
                            env={"PATH": courier_path, "HOME": str(Path.home())}, check=False)
    if result.returncode:
        raise Refused(2, "night driver preflight failed")
    from scripts import run_night
    try:
        schedule = run_night.schedule(plan)
    except (ValueError, OverflowError, OSError) as exc:
        raise Refused(2, "{}: {}".format(getattr(exc, "reason", "plan_schedule_unrepresentable"), exc))
    prepared = Prepared(plan, args.plan, repo, python, template, str(Path(courier).resolve()),
                        courier_path, schedule, run_night.install_spans_for_day)
    records = [name for name in ("receipt.json", "result.json", "refusal.json", "chain.started",
               "chain.exited", "courier.json", "courier.sent") if os.path.lexists(prepared.custody_night / name)]
    if records:
        raise Refused(3, "refusing install: existing night records: " + " ".join(records))
    prepared.admit(time.time())  # All read-only refusals precede admission and mkdir.
    return prepared


def main(argv=None):
    def render_directory(value):
        if not value:
            raise argparse.ArgumentTypeError("--render-only requires a non-empty value")
        return Path(value)

    class UsageParser(argparse.ArgumentParser):
        def error(self, message):
            self.print_usage(sys.stderr)
            self.exit(2)

    parser = UsageParser(add_help=False, allow_abbrev=False,
        usage="%(prog)s --plan PLAN.json [--python ABS_PATH] [--uninstall] "
              "[--render-only DIR] [--launchctl-bin PATH]")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--python")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--render-only", type=render_directory)
    parser.add_argument("--launchctl-bin", default="launchctl")
    args = parser.parse_args(argv)
    try:
        if args.uninstall and args.render_only is not None:
            raise Refused(2, "--render-only and --uninstall are mutually exclusive")
        if not args.plan.is_file():
            raise Refused(2, "plan not found: {}".format(args.plan))
        args.plan = args.plan.resolve()
        target = Target.for_mode(Path.home() / "Library/LaunchAgents", args.render_only)
        if isinstance(target, RenderTarget):
            adapter = NullAdapter(target)
        else:
            executable = shutil.which(args.launchctl_bin)
            if not executable:
                raise Refused(2, "launchctl executable not found")
            adapter = LaunchctlAdapter(target, str(Path(executable).resolve()))
        if args.uninstall:
            if args.python:
                print("--python ignored on uninstall", file=sys.stderr)
            return uninstall(adapter)
        return Transaction(adapter, lambda: validate_install(args, Path(__file__).resolve().parents[1])).run()
    except (Refused, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return exc.code if isinstance(exc, Refused) else 1


if __name__ == "__main__":
    sys.exit(main())
