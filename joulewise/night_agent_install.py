"""Transactional night-agent publication and recovery (system Python 3.9).

Only LaunchctlAdapter invokes launchctl. Liveness is a typed Outcome; only an
exact absence result can mint a directory/label/generation-bound Absent proof.
Plist publication, removal and restoration have separate, narrow capabilities.
The transaction's one finally dispatches on state, including after output fails.
Unexpected teardown errors return 1 with state RETAINED and the warning
"teardown failed; retained: <exception type>: <message>".

INT/TERM/HUP handlers only record the first signal; ordinary-code polls honor
it before the next mutation, at most one adapter call plus its timeout later
(or the validation subprocess runtime). The final poll follows the commit
clock predicate: a signal recorded during that read rolls back; one after the
latch cannot replace success. Teardown never polls and discards signals;
completion leaves these signals ignored until CLI process death. A stalled
pins-output pipe can therefore require SIGKILL. SIGKILL/SIGQUIT skip teardown;
remaining .prior sidecars make the next install refuse with exit 3.
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


class Shield:
    """Own three dispositions for one single-threaded invocation, never its mask."""
    def __init__(self):
        self.saved, self.signalled = {}, None

    def install(self):
        # main installs before parsing; run/uninstall also support direct callers.
        if self.saved:
            return

        def record(number, frame):
            if self.signalled is None:
                self.signalled = 128 + number

        for number in SIGNALS:
            self.saved[number] = signal.getsignal(number)
            signal.signal(number, record)

    def poll(self):
        if self.signalled is not None:
            raise Signalled(self.signalled)

    def quiesce(self):
        """Discard deferred delivery and ignore later signals through CLI exit."""
        for number in self.saved:
            signal.signal(number, signal.SIG_IGN)

    def release(self):
        """Restore exact saved dispositions; in-process callers only."""
        for number, handler in self.saved.items():
            signal.signal(number, handler)
        self.saved.clear()


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
    def __init__(self, adapter, validate, clock=None, stdout=None, stderr=None, shield=None):
        self.adapter, self.target = adapter, adapter.target
        if isinstance(self.target, RenderTarget) and type(adapter) is not NullAdapter:
            raise TypeError("render-only requires NullAdapter")
        self.validate = validate
        self.clock = clock or time.time
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr
        self.state = State.PARSED
        self.result = 1
        self.shield = shield or Shield()
        self.prepared = None
        self.selected_span_close = None

    def _say(self, message, error=False):
        print(message, file=self.stderr if error else self.stdout, flush=True)

    def _warn(self, message):
        try:
            self._say(message, error=True)
        except BaseException:
            pass

    def _poll(self):
        self.shield.poll()

    def _enter(self, state):
        self._poll()
        self.state = state

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
        try:
            self._teardown()
        except BaseException as exc:
            self.state, self.result = State.RETAINED, 1
            self._warn("teardown failed; retained: {}: {}".format(type(exc).__name__, exc))
        finally:
            self.shield.quiesce()

    def _commit(self):
        now = self.clock()
        if now >= min(self.selected_span_close, self.prepared.schedule["install_close_epoch_s"]):
            raise Refused(2, self.prepared.timing("install_span_closed", now,
                          "selected_span_close_epoch_s={}".format(self.selected_span_close)))
        self._poll()  # Commit latch: the final poll, after the clock predicate.
        self.state = State.COMMITTED

    def run(self):
        self.shield.install()
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
            require_published = isinstance(self.target, LaunchdTarget)
            self.selected_span_close = self.prepared.admit(
                self.clock(), require_published=require_published)
            self._enter(State.ADMITTED)
            self._enter(State.STAGED)
            self.target.stage()
            self.prepared.custody_night.mkdir(parents=True, exist_ok=True)
            for label, payload in self.prepared.render(
                    self.target.labels, require_published=require_published):
                self._poll()
                result = self.adapter.write_plist(label, payload)
                if result.kind is not Kind.SUCCEEDED:
                    raise Refused(1, result.stderr)
            self._enter(State.PUBLISHED)
            if isinstance(self.target, LaunchdTarget):
                for index, label in enumerate(self.target.labels):
                    self._enter(State.NIGHT_LOADED if index == 0 else State.DEADMAN_LOADED)
                    self._poll()
                    result = self.adapter.bootstrap(label)
                    if result.kind is not Kind.SUCCEEDED:
                        raise Refused(3, "failed to bootstrap {}".format(label))
                observed = []
                for label in self.target.labels:
                    self._poll()
                    observed.append(self.adapter.print(label))
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
        except BaseException as exc:
            self.result = 1
            self._warn("{}: {}".format(type(exc).__name__, exc))
        finally:
            self._unwind()
        return self.result


def uninstall(adapter, stderr=None, shield=None):
    """System-interpreter recovery: no plan, driver, pins or venv imports."""
    shield = shield or Shield()
    shield.install()
    if type(adapter) is NullAdapter:
        raise TypeError("render-only and uninstall are mutually exclusive")
    sink = stderr or sys.stderr
    machine = Transaction(adapter, None, stderr=sink, shield=shield)
    try:
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
        shield.quiesce()


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
    probe_timeout_s: float = 600

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

    def admit(self, now, require_published=True):
        if require_published and self.plan_path != (Path(self.plan.custody_root) / "night_plan.json").resolve():
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

    def render(self, labels, require_published=True):
        # Validate the future installed argv even when reading staged plan bytes.
        plan_path = (self.plan_path if require_published else
                     (Path(self.plan.custody_root) / "night_plan.json").resolve())
        for index, label in enumerate(labels):
            if label.startswith("com.joulewise.night-probe."):
                yield render_probe(self, self.probe_timeout_s)
                continue
            mode = "run" if index == 0 else "dead-man"
            calendar = self.schedule["night_calendar" if index == 0 else "deadman_calendar"]
            text = self.template
            if index:
                for field in ("Month", "Day"):
                    text = re.sub(r"    <key>" + field + r"</key>\n    <integer>@@[A-Z]+@@</integer>\n", "", text)
            values = {"com.joulewise.night": label, "@@PYTHON@@": self.python,
                      "@@MODE@@": mode, "@@REPO@@": str(self.repo), "@@PLAN@@": str(plan_path),
                      "@@CUSTODY_ROOT@@": self.plan.custody_root, "@@COURIER_BIN@@": self.courier,
                      "@@PATH@@": self.courier_path,
                      "@@LOG_STEM@@": "launchd.deadman" if index else "launchd.night"}
            values.update({"@@{}@@".format(key.upper()): str(value) for key, value in calendar.items()})
            yield label, re.sub(r"com\.joulewise\.night|@@[A-Z_]+@@",
                lambda match: escape(values.get(match.group(0), match.group(0))), text).encode("utf-8")


PROBE_RECEIPT_MAX_AGE_S = 6 * 60 * 60
# Every program of the measurement checkout whose bytes decide what the night
# reads under custody. The probe receipt is invalidated by a change to any of
# them, committed or not: a committed change also moves the measurement HEAD
# (night_gate pins plan.measurement_head), but an uncommitted edit in the clone
# moves nothing else. The reservation echoes digests only for the files it
# knows; probe_bindings binds this whole set and validate_probe_receipt
# recomputes it field by field at install time (see scripts/run_night.py
# _probe_worker for the echo-is-a-subset reconciliation).
PROBE_CODE_PATHS = (
    "scripts/reserve_calibration_window_bracket.py",
    "scripts/validate_powermetrics_fiducial.py",
    "scripts/run_night.py",
    "joulewise/calibration_ledger.py",
    "joulewise/calibration_custody_worker.py",
)
# How many whole-corpus custody passes the capture writer can pay for inside
# ONE budget. A pass is one sweep that opens and hashes every governed artifact
# of every custody-bearing observation. The writer makes four sweeps per slot
# -- the preflight snapshot before it holds the writer lease, one snapshot
# under the lease, the enforcing readiness gate and the slot validation -- and
# lane CUSTODY-PASS-MEMO-01 memoizes the verified set on the shared
# CustodyDeadline so the last two read no bytes while the lease is held and the
# physical ledger head digest is unchanged (see bounded_custody_reasons in
# joulewise/calibration_ledger.py). The memo is armed only after the lease is
# acquired, so the preflight pass never feeds a later one, and a HEALTHY slot
# reads the corpus twice.
#
# This constant is not that healthy count. It is the honest WORST CASE, which
# is THREE reads, reached two ways:
#   * the pre-capture repair actually mutates the ledger, so the head digest
#     moves between the under-lease pass and the readiness gate, the memo's key
#     no longer matches, and the writer pays one more honest read; or
#   * the corpus is CORRUPT. A refused pass is never memoized, so the preflight
#     pass, the refused under-lease pass and the refusing re-read are three
#     reads (tests/test_calibration_ledger_custody.py
#     test_a_pre_lease_pass_never_feeds_an_under_lease_pass pins exactly this).
# The corrupt case is why the count is 3 rather than 2 with the headroom factor
# standing in for the third pass: a slot that is going to refuse must have room
# to reach its typed calibration_ledger_custody_invalid rather than be cut off
# by a calibration_ledger_custody_timeout, which names the wrong cause.
#
# The arm-time probe runs the reservation, which makes exactly ONE pass, so the
# probe's measured custody_elapsed_s must be multiplied by this count before it
# can be compared with the budget the night will hand the writer. A capture
# writer's success receipt reports its own custody_passes (2 on a healthy
# slot), so a future change that adds a sweep back is visible in a real night's
# receipt and not only here.
WRITER_CUSTODY_PASSES = 3
# Margin on top of the multiplied passes, and nothing else: a night's corpus
# grows with every finalized slot and the passes are not identical in cost, so
# admission asks for half a pass of slack rather than an exact fit. It does not
# stand in for a pass -- the worst case above is counted, not absorbed here. At
# 3 x 1.5 against a 120 s budget the installer admits T <= 26.67 s.
CUSTODY_HEADROOM_FACTOR = 1.5


def _digest(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def interpreter_identity(python):
    """Identify the interpreter actually executed, including a venv's binary."""
    code = ("import hashlib,json,sys; from pathlib import Path; "
            "print(json.dumps({'path':sys.executable,"
            "'version':'.'.join(map(str,sys.version_info[:3])),"
            "'sha256':hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest()}))")
    result = subprocess.run([str(python), "-B", "-c", code], capture_output=True,
                            text=True, timeout=10, check=True)
    value = json.loads(result.stdout)
    if (set(value) != {"path", "version", "sha256"}
            or not Path(value["path"]).is_absolute()
            or not re.fullmatch(r"[0-9a-f]{64}", value["sha256"])):
        raise ValueError("interpreter identity invalid")
    return value


def reservation_input_digests(plan, plan_path):
    from scripts.run_night import reservation_input_paths
    return {str(path): "sha256:" + _digest(path)
            for path in reservation_input_paths(plan, plan_path)}


def chain_literal_paths(chain, names=("CALIBRATION_LEDGER", "LEDGER_HEAD_PIN")):
    """Read the pinned wrapper's own literal exports; never a parallel list."""
    import shlex
    text = Path(chain).read_text()
    paths = {}
    for name in names:
        matches = re.findall(r"^export " + name + r"=(.*)$", text, re.MULTILINE)
        if len(matches) != 1:
            raise ValueError(name + " must be one literal export in the pinned chain")
        words = shlex.split(matches[0])
        if len(words) != 1 or not Path(words[0]).is_absolute() or any(c in words[0] for c in "$`\n\r"):
            raise ValueError(name + " is not an absolute literal path")
        paths[name] = Path(words[0])
    return paths


def finalized_observation_rows(ledger_path):
    """Count ledger rows that finalize an attempt (an observation the night verifies)."""
    from joulewise.calibration_ledger import HISTORICAL_IMPORT_FINALIZATION_EVENT
    final_events = {"finalization", HISTORICAL_IMPORT_FINALIZATION_EVENT}
    rows = 0
    for line in Path(ledger_path).read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except ValueError:
            # A torn tail is the recovery tool's business, not this gate's.
            continue
        if isinstance(record, dict) and record.get("event") in final_events:
            rows += 1
    return rows


def probe_bindings(plan, plan_path, python):
    """Bind the actual reservation inputs and the effective interpreters."""
    chain = Path(plan.chain_path)
    digest = _digest(chain)
    sidecar = Path(plan.chain_sha256_path).read_text().split()
    if (not sidecar or sidecar[0] != digest or len(sidecar) > 2
            or (len(sidecar) == 2 and sidecar[1] != chain.name)):
        raise ValueError("chain_sha256 mismatch")
    paths = chain_literal_paths(chain)
    pin = json.loads(paths["LEDGER_HEAD_PIN"].read_text())
    head = pin["head_digest"]
    rows = paths["CALIBRATION_LEDGER"].read_text().splitlines()
    physical = json.loads(rows[-1])["receipt_digest"] if rows else "0" * 64
    if not re.fullmatch(r"[0-9a-f]{64}", head) or physical != head:
        raise ValueError("ledger_head_sha256 mismatch")
    root = Path(plan.measurement_root)
    source = root / "scripts/night_chains/calibration_derivation_only.zsh"
    if "NIGHT_VERIFY_ONLY" not in source.read_text() or "calibration_derivation_only.zsh" not in chain.read_text():
        raise ValueError("chain does not support reservation verify-only mode")
    if "NIGHT_RESERVATION_ARGV_ONLY" not in source.read_text():
        raise ValueError("input_digests: chain lacks reservation argument inspection")
    inputs = reservation_input_digests(plan, plan_path)
    return {"plan_id": plan.plan_id, "plan_sha256": _digest(plan_path),
            "input_digests": inputs,
            "measurement_head": plan.measurement_head, "ledger_head_sha256": head,
            "custody_budget_s": float(getattr(plan, "custody_budget_s", 120)),
            "code_digests": {name: "sha256:" + _digest(root / name) for name in PROBE_CODE_PATHS},
            "driver_python": interpreter_identity(python),
            "chain_python": interpreter_identity(root / ".venv/bin/python"),
            "chain_sha256": digest, "chain_source_sha256": _digest(source),
            # Bind ledger bytes as well as the head; never trust a copied tail.
            "ledger_sha256": _digest(paths["CALIBRATION_LEDGER"]),
            "ledger_pin_sha256": _digest(paths["LEDGER_HEAD_PIN"])}


def probe_label(plan_id):
    label = "com.joulewise.night-probe." + plan_id
    if not re.fullmatch(r"[A-Za-z0-9_.-]+", label):
        raise Refused(2, "probe plan_id is not a valid launchd label")
    return label


def validate_probe_receipt(prepared, max_age_s=PROBE_RECEIPT_MAX_AGE_S, receipt_path=None):
    import math
    from joulewise.night_gate import probe_payload_kind
    try:
        kind = probe_payload_kind(Path(prepared.plan.chain_path).read_text())
    except (OSError, ValueError) as exc:
        raise Refused(2, str(exc))
    if kind == "quiet_predicate_evidence":
        return validate_evidence_probe_receipt(prepared, max_age_s, receipt_path)
    path = receipt_path or prepared.plan_path.parent / "night_probe_receipt.json"
    try:
        receipt = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise Refused(2, "probe receipt missing or invalid: {}: {}".format(path, exc))
    if isinstance(receipt, dict) and receipt.get("schema") == "joulewise.night_evidence_probe_receipt.v1":
        raise Refused(2, "probe receipt kind does not match payload kind")
    if not isinstance(receipt, dict) or receipt.get("schema") != "joulewise.night_probe_receipt.v1":
        raise Refused(2, "probe receipt schema mismatch")
    if receipt.get("outcome") != "ok":
        raise Refused(2, "probe receipt outcome is not ok: {}".format(receipt.get("outcome")))
    now = time.time()
    if now - path.stat().st_mtime >= max_age_s:
        raise Refused(2, "probe receipt mtime stale (maximum age {} s)".format(max_age_s))
    finished = receipt.get("finished_epoch_s")
    # Allow a small forward step from clock resynchronisation between the
    # probe's wall-clock stamp and this read. In the 2026-09-16 machine move,
    # kern.boottime shifted by tens of milliseconds; NTP corrections are bounded
    # well under a minute. Larger future skew indicates a forged or mis-stamped
    # receipt, so retain the 60 s limit.
    if (isinstance(finished, bool) or not isinstance(finished, (int, float))
            or not math.isfinite(finished) or not -60 <= now - finished < max_age_s):
        raise Refused(2, "probe receipt finished_epoch_s stale or invalid (maximum age {} s)".format(max_age_s))
    started = receipt.get("started_epoch_s")
    elapsed = receipt.get("custody_elapsed_s")
    observations = receipt.get("observations")
    if (isinstance(started, bool) or not isinstance(started, (int, float))
            or not math.isfinite(started) or not 0 <= started <= finished):
        raise Refused(2, "probe receipt started_epoch_s invalid")
    if (isinstance(elapsed, bool) or not isinstance(elapsed, (int, float))
            or not math.isfinite(elapsed) or elapsed < 0):
        raise Refused(2, "probe receipt custody_elapsed_s invalid")
    if isinstance(observations, bool) or not isinstance(observations, int) or observations < 0:
        raise Refused(2, "probe receipt observations invalid")
    budget = receipt.get("custody_budget_s")
    if (isinstance(budget, bool) or not isinstance(budget, (int, float))
            or not math.isfinite(budget) or budget <= 0):
        raise Refused(2, "probe receipt custody_budget_s invalid")
    # The probe timed ONE custody pass; the writer makes WRITER_CUSTODY_PASSES
    # of them inside the same budget. Refuse the install here, at the desk,
    # rather than time the night out on its first slot.
    if elapsed * WRITER_CUSTODY_PASSES * CUSTODY_HEADROOM_FACTOR > budget:
        raise Refused(2, "probe receipt custody_elapsed_s {:g} s x WRITER_CUSTODY_PASSES"
            " {} x {:g} exceeds custody_budget_s {:g} s: the capture writer cannot"
            " finish its passes inside the night's budget".format(
                elapsed, WRITER_CUSTODY_PASSES, CUSTODY_HEADROOM_FACTOR, budget))
    if receipt.get("refusal_code") is not None:
        raise Refused(2, "probe receipt refusal_code contradicts success")
    if receipt.get("launchd_label") != probe_label(prepared.plan.plan_id):
        raise Refused(2, "probe receipt launchd_label mismatch")
    inputs = receipt.get("input_digests")
    if not isinstance(inputs, dict) or not inputs:
        raise Refused(2, "probe receipt input_digests missing or invalid")
    # Check recorded inputs before running the pinned wrapper's own input
    # authentication, so a changed or missing file is named precisely.
    for name, digest in inputs.items():
        if (not isinstance(name, str) or not Path(name).is_absolute()
                or not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest)):
            raise Refused(2, "probe receipt input_digests invalid: {}".format(name))
        try:
            actual = "sha256:" + _digest(Path(name))
        except OSError as exc:
            raise Refused(2, "probe receipt input_digests[{}] unavailable: {}".format(name, exc))
        if actual != digest:
            raise Refused(2, "probe receipt input_digests[{}] mismatch".format(name))
    try:
        expected = probe_bindings(prepared.plan, prepared.plan_path, prepared.python)
        finalized = finalized_observation_rows(
            chain_literal_paths(prepared.plan.chain_path)["CALIBRATION_LEDGER"])
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        raise Refused(2, "probe receipt current bindings invalid: {}".format(exc))
    # A pass over nothing certifies nothing: a probe that verified zero
    # observations while the ledger already holds finalized ones measured a
    # corpus the night will not read.
    if observations == 0 and finalized:
        raise Refused(2, "probe receipt observations is 0 while the ledger holds {}"
                         " finalized observation rows".format(finalized))
    for name in sorted(set(inputs) | set(expected["input_digests"])):
        if inputs.get(name) != expected["input_digests"].get(name):
            raise Refused(2, "probe receipt input_digests[{}] mismatch".format(name))
    for field, value in expected.items():
        if receipt.get(field) != value:
            raise Refused(2, "probe receipt {} mismatch".format(field))
    return receipt


def evidence_probe_bindings(plan, plan_path, python):
    from joulewise import night_gate
    from joulewise.quiet_predicate_campaign import verify_manifest, CHAIN_PATH, HARNESS_PATHS, PROTOCOL_PATH
    chain = Path(plan.chain_path)
    sha = _digest(chain)
    tokens = Path(plan.chain_sha256_path).read_text().split()
    if not tokens or tokens[0] != sha or len(tokens) > 2 or (len(tokens) == 2 and tokens[1] != chain.name):
        raise ValueError("chain_sha256 mismatch")
    manifest_path, manifest, manifest_sha = verify_manifest(plan, chain.read_text())
    # The sealed literal is content-derived (never resolved: wrapper bytes must
    # not depend on filesystem state); file IDENTITY is compared resolved, as
    # Prepared.admit does, so an aliased or symlinked custody root (/tmp vs
    # /private/tmp) cannot make the two guards mutually unsatisfiable (Opus 90
    # S1 / refuter 89 R1).
    published_plan_path = Path(plan.custody_root) / "night_plan.json"
    if Path(plan_path).resolve() != published_plan_path.resolve():
        raise ValueError("evidence plan not at its published path")
    if night_gate.chain_literal(chain.read_text(), "EVIDENCE_PLAN_PATH") != str(published_plan_path):
        raise ValueError("evidence plan path mismatch")
    registration_sha = manifest["files"][PROTOCOL_PATH]
    ruled = night_gate.RULED_REGISTRATIONS.get(registration_sha)
    if ruled is None or not ruled["binds_chain"]:
        raise ValueError("registration is not a chain-bound ruled registration")
    root = Path(plan.measurement_root)
    return {"plan_id": plan.plan_id, "plan_sha256": _digest(plan_path),
            "measurement_head": plan.measurement_head, "chain_sha256": sha,
            "chain_source_sha256": manifest["files"][CHAIN_PATH], "manifest_sha256": manifest_sha,
            "manifest_digests": manifest["files"],
            "harness_digests": {name: manifest["files"][name] for name in HARNESS_PATHS},
            "registration_sha256": registration_sha, "registration_label": ruled["label"],
            "input_digests": {str(Path(plan_path).absolute()): "sha256:" + _digest(plan_path),
                              str(manifest_path): "sha256:" + manifest_sha},
            "driver_python": interpreter_identity(python),
            "chain_python": interpreter_identity(root / ".venv/bin/python"),
            "powermetrics_path": "/usr/bin/powermetrics"}


def validate_evidence_probe_receipt(prepared, max_age_s=PROBE_RECEIPT_MAX_AGE_S, receipt_path=None):
    """Second receipt kind; no calibration custody arithmetic is applicable."""
    import math
    from joulewise.quiet_predicate_campaign import RECEIPT_SCHEMA
    path = receipt_path or prepared.plan_path.parent / "night_probe_receipt.json"
    try:
        receipt = json.loads(path.read_text())
        if not isinstance(receipt, dict) or receipt.get("schema") != RECEIPT_SCHEMA:
            raise ValueError("probe receipt kind does not match payload kind")
        if any(key in receipt for key in ("custody_budget_s", "custody_elapsed_s", "observations")):
            raise ValueError("evidence probe receipt contains calibration custody fields")
        if receipt.get("outcome") != "ok" or receipt.get("refusal_code") is not None:
            raise ValueError("probe receipt outcome is not ok")
        now = time.time()
        if now - path.stat().st_mtime >= max_age_s:
            raise ValueError("probe receipt mtime stale")
        finished, started = receipt.get("finished_epoch_s"), receipt.get("started_epoch_s")
        if (type(finished) not in (int, float) or not math.isfinite(finished) or
                not -60 <= now - finished < max_age_s):
            raise ValueError("probe receipt finished_epoch_s stale or invalid")
        if (type(started) not in (int, float) or not math.isfinite(started) or not 0 <= started <= finished):
            raise ValueError("probe receipt started_epoch_s invalid")
        if receipt.get("launchd_label") != probe_label(prepared.plan.plan_id):
            raise ValueError("probe receipt launchd_label mismatch")
        for field, expected in (("verify_only", True), ("collect_started", False), ("load_started", False)):
            if receipt.get(field) is not expected:
                raise ValueError("probe receipt " + field + " mismatch")
        if receipt.get("cleanup_proven") is not True:
            raise ValueError("probe receipt cleanup unproven")
        bindings = evidence_probe_bindings(prepared.plan, prepared.plan_path, prepared.python)
        for field, expected in bindings.items():
            if receipt.get(field) != expected:
                raise ValueError("probe receipt " + field + " mismatch")
        if receipt.get("verify_stdout") != ["VERIFY_ONLY_OK manifest=" + bindings["manifest_sha256"]]:
            raise ValueError("expected one matching VERIFY_ONLY_OK manifest line")
        return receipt
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        raise Refused(2, str(exc))


def render_probe(prepared, timeout_s=600):
    import plistlib
    template = prepared.repo / "configs/launchd/com.joulewise.night-probe.plist.template"
    values = {"@@LABEL@@": probe_label(prepared.plan.plan_id), "@@PYTHON@@": prepared.python,
              "@@REPO@@": str(prepared.repo), "@@PLAN@@": str(prepared.plan_path),
              "@@RECEIPT@@": str(prepared.plan_path.parent / "night_probe_receipt.pending.json"),
              "@@TIMEOUT@@": format(timeout_s, "g"), "@@PATH@@": prepared.courier_path,
              "@@PROBE_DIR@@": str(prepared.plan_path.parent)}
    text = re.sub(r"@@[A-Z_]+@@", lambda match: escape(values[match.group(0)]), template.read_text())
    value = plistlib.loads(text.encode())
    if "KeepAlive" in value:
        raise Refused(2, "probe template must not contain KeepAlive")
    return value["Label"], text.encode()


def probe_process_census(label, plan_path, process_record=None):
    """Prove label/argv and the independent chain group have no survivors."""
    pattern = re.escape(label) + "|run_night[.]py probe .*" + re.escape(str(plan_path))
    commands = [["/usr/bin/pgrep", "-lf", pattern]]
    if process_record is not None:
        pgid = process_record.get("chain_pgid")
        if not isinstance(pgid, int) or pgid <= 1:
            raise Refused(2, "probe process census invalid chain_pgid")
        commands.append(["/usr/bin/pgrep", "-lf", "-g", str(pgid), "."])
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
        if result.returncode != 1 or result.stdout.strip():
            raise Refused(2, "probe process census survivor or unknown: {} {}".format(result.stdout, result.stderr))


def launchd_probe(prepared, executable, shield, timeout_s=600, max_age_s=PROBE_RECEIPT_MAX_AGE_S):
    """Run a temporary job in the installation GUI domain, then prove cleanup."""
    label, payload = render_probe(prepared, timeout_s)
    published_path = prepared.plan_path.parent / "night_probe_receipt.json"
    receipt_path = prepared.plan_path.parent / "night_probe_receipt.pending.json"
    process_path = receipt_path.with_name(receipt_path.name + ".process.json")
    with tempfile.TemporaryDirectory(prefix="night-probe-job-", dir=prepared.plan_path.parent) as directory:
        target = Target.for_mode(directory, labels=(label,))
        adapter = LaunchctlAdapter(target, executable)
        try:
            adapter.require_absent(label)
        except NotAbsent as exc:
            raise Refused(2, "probe label is not absent: {}".format(exc))
        probe_process_census(label, prepared.plan_path)
        # Remove only non-authorizing prior probe outputs after proving no owner.
        published_path.unlink(missing_ok=True)
        receipt_path.unlink(missing_ok=True)
        process_path.unlink(missing_ok=True)
        result = adapter.write_plist(label, payload)
        if result.kind is not Kind.SUCCEEDED:
            raise Refused(2, "probe plist publication failed: " + result.stderr)
        in_flight = None
        try:
            shield.poll()
            result = adapter.bootstrap(label)
            if result.kind is not Kind.SUCCEEDED:
                raise Refused(2, "probe bootstrap failed: " + result.stderr)
            deadline = time.monotonic() + timeout_s + 10  # bounded driver cleanup/publication
            while not receipt_path.is_file():
                shield.poll()
                if time.monotonic() >= deadline:
                    raise Refused(2, "probe receipt timeout")
                time.sleep(0.05)
        except BaseException as exc:
            in_flight = exc
            raise
        finally:
            try:
                _proofs, unresolved = verified_bootout(adapter, (label,))
                if unresolved:
                    raise Refused(2, "probe bootout absence unproven: " + label)
                process_record = json.loads(process_path.read_text()) if process_path.is_file() else None
                if receipt_path.is_file() and process_record is None:
                    raise Refused(2, "probe process identity missing")
                # A killed driver may leave its separately-created chain group.
                if process_record is not None:
                    if process_record.get("launchd_label") != label:
                        raise Refused(2, "probe process label mismatch")
                    pgid = process_record.get("chain_pgid")
                    if not isinstance(pgid, int) or pgid <= 1:
                        raise Refused(2, "probe process chain_pgid invalid")
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    except PermissionError as exc:
                        # An absent group may also deny signals in a sandbox.
                        probe_process_census(label, prepared.plan_path, process_record)
                deadline = time.monotonic() + 5
                while True:
                    try:
                        probe_process_census(label, prepared.plan_path, process_record)
                        break
                    except Refused:
                        if time.monotonic() >= deadline:
                            raise
                        time.sleep(0.05)
            except Refused as cleanup:
                # Fail closed on the cleanup proof, but never lose the exception
                # it interrupted: an unproven bootout raised over a receipt
                # timeout must report both, and the traceback keeps the
                # interrupted failure as this refusal's cause.
                if in_flight is None:
                    raise
                raise Refused(cleanup.code, "{} (raised while handling {}: {})".format(
                    cleanup, type(in_flight).__name__, in_flight)) from in_flight
        receipt = validate_probe_receipt(prepared, max_age_s, receipt_path)
        if (receipt.get("chain_pgid") != process_record["chain_pgid"]
                or receipt.get("driver_pid") != process_record["driver_pid"]):
            raise Refused(2, "probe receipt process identity mismatch")
        # A driver success is only pending until bootout AND census succeed.
        # Interruption (including SIGKILL) before this point leaves no installable
        # success receipt. The publication is atomic in the same directory.
        os.replace(receipt_path, published_path)
        print("launchd probe ok; bootout and process census clear: " + label)
        return receipt


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
                        courier_path, schedule, run_night.install_spans_for_day,
                        getattr(args, "probe_timeout_s", 600))
    records = [name for name in ("receipt.json", "result.json", "refusal.json", "chain.started",
               "chain.exited", "courier.json", "courier.sent") if os.path.lexists(prepared.custody_night / name)]
    if records:
        raise Refused(3, "refusing install: existing night records: " + " ".join(records))
    # All read-only refusals precede admission and mkdir.
    prepared.admit(time.time(), require_published=args.render_only is None)
    for field in ("hour", "minute"):
        supplied = getattr(args, field, None)
        if supplied is not None and supplied != schedule["night_calendar"][field.capitalize()]:
            raise Refused(2, "--{} must match the plan calendar".format(field))
    if args.render_only is not None:
        from joulewise import night_gate
        chain = Path(plan.chain_path)
        try:
            chain_text = chain.read_text()
        except (OSError, UnicodeError):
            # Legacy render fixtures may name a binary or unavailable chain.
            chain_text = ""
        try:
            payload_kind = night_gate.probe_payload_kind(chain_text)
        except ValueError:
            # Unrecognized payloads retain the legacy render-only inspection.
            payload_kind = None
        if payload_kind == "quiet_predicate_evidence":
            from joulewise.quiet_predicate_campaign import verify_manifest, PROTOCOL_PATH
            sha = _digest(chain)
            tokens = Path(plan.chain_sha256_path).read_text().split()
            if not tokens or tokens[0] != sha or len(tokens) > 2 or (len(tokens) == 2 and tokens[1] != chain.name):
                raise ValueError("chain_sha256 mismatch")
            manifest_path, manifest, manifest_sha = verify_manifest(plan, chain_text)
            ruled = night_gate.RULED_REGISTRATIONS.get(manifest["files"][PROTOCOL_PATH])
            if ruled is None or not ruled["binds_chain"]:
                raise ValueError("registration is not a chain-bound ruled registration")
            # Hash the supplied plan bytes without executing the wrapper, whose
            # EVIDENCE_PLAN_PATH deliberately names the future published plan.
            print(json.dumps({"payload_kind": "quiet_predicate_evidence", "input_digests": {
                str(args.plan): "sha256:" + _digest(args.plan),
                str(chain): "sha256:" + sha,
                str(manifest_path): "sha256:" + manifest_sha}}, sort_keys=True))
        else:
            source = Path(plan.measurement_root) / "scripts/night_chains/calibration_derivation_only.zsh"
            if source.is_file() and "NIGHT_RESERVATION_ARGV_ONLY" in source.read_text():
                print(json.dumps({"input_digests": reservation_input_digests(plan, args.plan)}, sort_keys=True))
            else:
                print(json.dumps({"input_digests": None, "detail": "no reservation inspection surface"}))
    if args.render_only is None and not getattr(args, "launchd_probe", False):
        validate_probe_receipt(prepared, getattr(args, "probe_max_age_s", PROBE_RECEIPT_MAX_AGE_S))
    return prepared


def main(argv=None):
    shield = Shield()
    shield.install()
    def render_directory(value):
        if not value:
            raise argparse.ArgumentTypeError("--render-only requires a non-empty value")
        return Path(value)

    class UsageParser(argparse.ArgumentParser):
        def error(self, message):
            self.print_usage(sys.stderr)
            self.exit(2)

    parser = UsageParser(add_help=False, allow_abbrev=False,
        usage="%(prog)s --plan PLAN.json [--python ABS_PATH] "
              "[--launchd-probe] [--probe-timeout-s S] [--probe-max-age-s S] "
              "[--hour H] [--minute M] [--uninstall] "
              "[--render-only DIR] [--launchctl-bin PATH]")
    parser.add_argument("--plan", required=True, type=Path)
    parser.add_argument("--python")
    parser.add_argument("--launchd-probe", action="store_true")
    parser.add_argument("--probe-timeout-s", type=float, default=600)
    parser.add_argument("--probe-max-age-s", type=float, default=PROBE_RECEIPT_MAX_AGE_S)
    parser.add_argument("--hour", type=int)
    parser.add_argument("--minute", type=int)
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--render-only", type=render_directory)
    parser.add_argument("--launchctl-bin", default="launchctl")
    try:
        args = parser.parse_args(argv)
        import math
        if any(not math.isfinite(v) or v <= 0 for v in (args.probe_timeout_s, args.probe_max_age_s)):
            raise Refused(2, "probe timeout and receipt age must be finite and positive")
        if args.launchd_probe and (args.uninstall or args.render_only is not None):
            raise Refused(2, "--launchd-probe is a separate step from install/render/uninstall")
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
            # Uninstall remains usable with malformed/retired plans and Python 3.9.
            result = uninstall(adapter, shield=shield)
            if result == 0:
                try:
                    plan_id = json.loads(args.plan.read_text()).get("plan_id")
                    if isinstance(plan_id, str):
                        label = probe_label(plan_id)
                        probe_target = Target.for_mode(args.plan.parent, labels=(label,))
                        probe_adapter = LaunchctlAdapter(probe_target, adapter.executable)
                        observed = probe_adapter.print(label)
                        if observed.kind is not Kind.ABSENT:
                            _, unresolved = verified_bootout(probe_adapter, (label,))
                            if unresolved:
                                raise Refused(2, "leftover probe label absence unproven")
                            probe_process_census(label, args.plan)
                except (ValueError, AttributeError):
                    pass
            return result
        repo = Path(__file__).resolve().parents[1]
        if args.launchd_probe:
            prepared = validate_install(args, repo)
            launchd_probe(prepared, adapter.executable, shield, args.probe_timeout_s, args.probe_max_age_s)
            return 0
        def validate():
            prepared = validate_install(args, repo)
            if isinstance(target, RenderTarget):
                target.labels += (probe_label(prepared.plan.plan_id),)
            return prepared
        return Transaction(adapter, validate, shield=shield).run()
    except Signalled as exc:
        return exc.code
    except (Refused, OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return exc.code if isinstance(exc, Refused) else 1
    finally:
        shield.quiesce()


if __name__ == "__main__":
    sys.exit(main())
