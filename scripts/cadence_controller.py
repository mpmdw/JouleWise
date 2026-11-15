#!/usr/bin/env python3
"""The standing-queue controller (RL-172 section (g); RL-149 section 2.8). A script, never a model.

    python3.13 -B scripts/cadence_controller.py loop   --config controller.json
    python3.13 -B scripts/cadence_controller.py tick   --config controller.json
    python3.13 -B scripts/cadence_controller.py status --config controller.json
    python3.13 -B scripts/cadence_controller.py ack PAGE_ID --config controller.json --by NAME --note TEXT
    python3.13 -B scripts/cadence_controller.py note-run --config controller.json --kind F0 --run-id ID \\
        --t0 EPOCH --closed EPOCH --restore-ok yes|no --evidence TEXT
    python3.13 -B scripts/cadence_controller.py accept-audit-tip --config controller.json --by NAME --note TEXT
    python3.13 -B scripts/cadence_controller.py check-heartbeat --config controller.json [--max-age 300]
    python3.13 -B scripts/cadence_controller.py ledger --config controller.json      (critical-path CSV)
    python3.13 -B scripts/cadence_controller.py synthetic --workdir DIR              (RL-172 (i) row 5)

It runs on the MBP under launchd as a KeepAlive loop (``configs/launchd/
com.joulewise.cadence-controller.plist.template``). Each tick derives every state from durable evidence,
so a crash or a restart repeats nothing. The order of a tick:

1. **A span is live** (its launch fence is held by a live PID): stat the fence and the receipt only. No
   network, no subprocess, no git. The loop sleeps on a kernel event on the custody directory, so the
   fence's removal is seen at once and nothing polls inside a leg.
2. **Its fence is gone**: take the standing fence at once, prove the runner's processes absent, then close.
   A deadline that passes while the fence and its PID live is an alarm, never a close.
3. **Another run holds a fence** (F0, a session): wait. When it goes, its close is recorded as observed with
   its restore UNPROVEN, which halts until ``note-run --restore-ok yes`` records the run's Check.
4. **A night agent is loaded** (a v4 window): wait, silent.
5. **An unacknowledged halt or v4 page**: silent (no network) until the magistrate acknowledges it.
6. Otherwise: fetch the audit branch, read the owner's issues and the host's receipt census, and ask
   ``joulewise.cadence.standing.select``. Arming prepares (kit copy by hash, a fresh worktree at the frozen
   commit, ``validate-kit --repo``, the pinned ``plan``), takes the arm proof, then **re-reads every authority**
   (audit branch, issues, watcher, expiry, dates, verdicts, the census and copy gate) and requires the same
   decision, checks the host clock against the server's, posts the span's line on the queue's standing notice
   issue (RL-149 section 2.8), closes the network, writes the arm intent once (O_EXCL) with a lease (queue
   expiry, watcher age, the end of the span's date), and hands the launch to a short-lived arm child.

**The arm child** runs under the measurement interpreter with the measurement checkout on its path. It plans at
its own clock with the pin's own ``launch_deadline``, refuses an expired lease, and calls the frozen
``launch_cadence_span.main`` in-process with its own PID as the handoff PID. The controller's standing fence is
**replaced atomically** by the launch's own (the launcher's ``write_fence`` is an ``os.replace``): the arm child
hides only the controller's own fence from the launcher's busy check, so the custody fence file names a live
owner at every instant.

**The close** packs the bundle with the desk's own ``desk_final.pack_bundle`` (FORMAT.md section 1: closed layout,
allowlisted basenames, symlinks refused before any read), judges it from the packed bytes, and pushes one
SSH-signed commit to ``refs/heads/desk-bundles/<plan_id>`` whose tree is ``bundle/`` and ``transition.json``
(the per-span transition record, carrying the manifest's sha256: the anchor). The Air verifies that signature,
judges with ``cadence_desk.py final`` and commits its signed ``desk_verdict.json`` to the audit branch, where
the controller reads it by FORMAT.md section 4.

**The magistrate wakes only on a page.** While the controller waits with nothing to report it holds a desk fence
of its own, which the magistrate watchdog honours. A page releases it. If the controller dies its fence expires
and the watchdog notices; the prompt line also runs ``check-heartbeat``.

Blinding: this script never opens an energy, power, meter-sample, powermetrics, transcript, slot or custody
file. It reads the runner's receipt, span plan and the desk bundle's projections, through the desk's packer.
Design: docs/process/cadence_queue_design.md section 15.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.cadence import desk as deskmod, desk_final, desk_transport, kit as kitmod, queue as q  # noqa: E402
from joulewise.cadence import standing as law  # noqa: E402
from joulewise.cadence import stops as stopsmod  # noqa: E402
from scripts import launch_align_r0 as fence  # noqa: E402  (fence helpers only; nothing launches from here)

CONFIG_SCHEMA = "joulewise.cadence_controller_config.v1"
RECORD_SCHEMA = "joulewise.cadence_controller_record.v1"
STANDING_FENCE_PREFIX = "cadence-controller:"
STANDING_FENCE_S = 900
LEASE_S = 120                  # the arm child must launch within this of the controller's last authority read
RECEIPT_GRACE_S = 120          # fence gone, receipt not yet visible
STRANDED_GRACE_S = 600
CLOCK_SKEW_LIMIT_S = 120
VETO_LIMIT = 1000
CANONICAL_ROOT = "/Users/edr/code/JouleWise"
RECEIPT = "runner_receipt.json"
OUT_REFUSED = re.compile(r"/restricted/|/night-|/jw-b5-|/configs/campaigns/align_v4")
NIGHT_LABEL = re.compile(r"\bcom\.joulewise\.(night|align-r0)")
CONFIG_KEYS = {
    "schema", "state_dir", "git_dir", "audit_ref", "records_dir", "worktrees_root", "output_root", "kits_dir",
    "custody_root", "measurement_python", "receipt_roots", "signing_key", "bundle_ref_prefix", "verdict_signers",
    "copy_marker_dir", "watcher_name", "owner_login", "repo_slug", "gh_argv", "measurement_mode_script",
    "high_power_marker", "poll_idle_s", "poll_live_s", "hold_standing_fence", "accept_mock_verdicts"}


class ConfigError(ValueError):
    pass


class NetworkClosed(RuntimeError):
    """Network work was attempted while a span is armed or after the arm's network phase ended."""


def load_config(path):
    cfg = json.loads(Path(path).read_text(encoding="utf-8"))
    problems = []
    if set(cfg) != CONFIG_KEYS:
        problems.append(f"keys: missing {sorted(CONFIG_KEYS - set(cfg))}, unknown {sorted(set(cfg) - CONFIG_KEYS)}")
    if cfg.get("schema") != CONFIG_SCHEMA:
        problems.append(f"schema: {CONFIG_SCHEMA}")
    for key in ("state_dir", "git_dir", "worktrees_root", "output_root", "kits_dir", "custody_root",
                "measurement_python", "signing_key", "verdict_signers", "copy_marker_dir",
                "measurement_mode_script", "high_power_marker"):
        if not (isinstance(cfg.get(key), str) and cfg[key].startswith("/")):
            problems.append(f"{key}: an absolute path")
    if cfg.get("git_dir") == CANONICAL_ROOT:
        problems.append("git_dir: the controller's own clone, never the canonical root (prompt line 13)")
    out = str(cfg.get("output_root", ""))
    if OUT_REFUSED.search(out + "/") or out.startswith(str(cfg.get("custody_root", "\0"))):
        problems.append("output_root: outside every v4 registration and custody root (RL-149 section 2.8 line 4)")
    if not (isinstance(cfg.get("receipt_roots"), list) and cfg["receipt_roots"]):
        problems.append("receipt_roots: a non-empty list")
    if not (isinstance(cfg.get("gh_argv"), list) and cfg["gh_argv"]):
        problems.append("gh_argv: a non-empty argv list")
    if not (isinstance(cfg.get("poll_idle_s"), (int, float)) and 0 < cfg["poll_idle_s"] <= 300):
        problems.append("poll_idle_s: seconds in (0, 300]")
    if not (isinstance(cfg.get("poll_live_s"), (int, float)) and 10 <= cfg["poll_live_s"] <= 300):
        problems.append("poll_live_s: seconds in [10, 300] (a kernel event wakes the loop on the fence's removal)")
    if not str(cfg.get("bundle_ref_prefix", "")).startswith("refs/"):
        problems.append("bundle_ref_prefix: refs/...")
    if not (isinstance(cfg.get("watcher_name"), str) and cfg["watcher_name"]):
        problems.append("watcher_name: the results watcher's launchd label")
    if type(cfg.get("hold_standing_fence")) is not bool:
        problems.append("hold_standing_fence: bool")
    if type(cfg.get("accept_mock_verdicts")) is not bool or (
            cfg.get("accept_mock_verdicts") and os.environ.get("JW_B5_SYNTHETIC_ONLY") != "1"):
        problems.append("accept_mock_verdicts: false (true only in a synthetic run, JW_B5_SYNTHETIC_ONLY=1)")
    if problems:
        raise ConfigError("; ".join(problems))
    return cfg


# --------------------------------------------------------------------------
# Small durable-file helpers
# --------------------------------------------------------------------------
def sha256_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_json(path, value, *, sync=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with open(tmp, "x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=1, sort_keys=True)
        handle.write("\n")
        if sync:
            handle.flush()
            os.fsync(handle.fileno())
    os.replace(tmp, path)
    if sync:
        _fsync_dir(path.parent)


def exclusive_json(path, value):
    """Create-once. Raises FileExistsError if the record already exists (the idempotence guard)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=1, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    _fsync_dir(path.parent)


def append_jsonl(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(value, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def iso(epoch):
    return datetime.fromtimestamp(epoch, law.ZONE).isoformat(timespec="seconds")


# --------------------------------------------------------------------------
# Environment: the clock and commands (production) — replaced wholesale in the synthetic run
# --------------------------------------------------------------------------
@dataclass
class Result:
    rc: int | None
    stdout: str
    stderr: str


class Env:
    """Production clock and commands. ``run`` never raises: rc None means the command could not run."""

    def now(self):
        return time.time()

    def sleep(self, seconds):
        time.sleep(seconds)

    def watch(self, directory):
        """A kqueue registration on ``directory`` made now, so a change between this call and ``wait`` is not lost
        (Sol R7). ``wait(timeout)`` returns on any change since registration, or after ``timeout``."""
        return _Watch(directory)

    def wait_for_change(self, directory, timeout):
        """Sleep until ``directory`` changes (an entry added, removed or replaced) or ``timeout`` passes. A
        kernel event (kqueue) where the platform has one, so a live span costs no polling."""
        try:
            import select
            kq = select.kqueue()
        except (ImportError, AttributeError, OSError):
            time.sleep(timeout)
            return
        try:
            fd = os.open(directory, os.O_RDONLY)
        except OSError:
            kq.close()
            time.sleep(timeout)
            return
        try:
            event = select.kevent(fd, filter=select.KQ_FILTER_VNODE, flags=select.KQ_EV_ADD | select.KQ_EV_CLEAR,
                                  fflags=select.KQ_NOTE_WRITE | select.KQ_NOTE_DELETE | select.KQ_NOTE_RENAME)
            kq.control([event], 1, timeout)
        finally:
            os.close(fd)
            kq.close()

    def run(self, argv, *, timeout=60, cwd=None, env=None, input_text=None):
        try:
            done = subprocess.run([str(a) for a in argv], capture_output=True, text=True, timeout=timeout,
                                  cwd=cwd, env=env, input=input_text)
            return Result(done.returncode, done.stdout, done.stderr)
        except (OSError, subprocess.SubprocessError) as exc:
            return Result(None, "", f"{type(exc).__name__}: {exc}")

    def kernel_frequency(self):
        from joulewise import kernel_clock
        return kernel_clock.validate_probe(kernel_clock.read_kernel_frequency())

    def pid_alive(self, pid):
        return fence.pid_alive(pid)


class _Watch:
    def __init__(self, directory):
        self.kq = self.fd = None
        try:
            import select
            self.select = select
            self.kq = select.kqueue()
            self.fd = os.open(directory, os.O_RDONLY)
            self.kq.control([select.kevent(self.fd, filter=select.KQ_FILTER_VNODE,
                                           flags=select.KQ_EV_ADD | select.KQ_EV_CLEAR,
                                           fflags=select.KQ_NOTE_WRITE | select.KQ_NOTE_DELETE | select.KQ_NOTE_RENAME)],
                            0, 0)
        except (ImportError, AttributeError, OSError):
            self.close()

    def wait(self, timeout):
        if self.kq is None:
            time.sleep(timeout)
            return
        self.kq.control(None, 1, timeout)

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
        if self.kq is not None:
            self.kq.close()
        self.kq = self.fd = None


# --------------------------------------------------------------------------
# Host proofs (RL-172 (g) 5): readback and process-group absence, each line typed
# --------------------------------------------------------------------------
def _pgrep(env, argv):
    """pgrep: rc 1 = none (ok), rc 0 = found (not ok), anything else = not observed."""
    res = env.run(argv, timeout=15)
    if res.rc == 1:
        return {"ok": True, "detail": "none", "argv": argv}
    if res.rc == 0:
        return {"ok": False, "detail": res.stdout.strip()[:300], "argv": argv}
    return {"ok": None, "detail": f"rc {res.rc}: {res.stderr.strip()[:200]}", "argv": argv}


SPAN_PROCESSES = ["/usr/bin/pgrep", "-fl", r"cadence_legs_runner\.py|cadence_leg_runtime\.py|run_align_r0_launchagent"]


def host_proof(cfg, env, kind, *, allowed_fence_purposes=()):
    """The typed readback and absence lines (``law.PROOF_LINES``) for ``kind`` ``arm`` or ``close``."""
    rows = {}
    res = env.run(["/usr/bin/pmset", "-g"], timeout=15)
    modes = re.findall(r"(?m)^\s*powermode\s+(\d+)\s*$", res.stdout) if res.rc == 0 else []
    rows["powermode"] = ({"ok": None, "detail": f"pmset -g rc {res.rc}, powermode lines {modes}"}
                         if len(modes) != 1 else {"ok": modes[0] == "0", "detail": f"powermode {modes[0]}"})
    res = env.run(["/usr/bin/pmset", "-g", "batt"], timeout=15)
    rows["ac_power"] = ({"ok": None, "detail": f"rc {res.rc}"} if res.rc != 0 else
                        {"ok": "Now drawing from 'AC Power'" in res.stdout.splitlines(), "detail": res.stdout[:120]})
    res = env.run(["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup", "-getusingnetworktime"], timeout=30)
    text = res.stdout.strip()
    rows["network_time"] = ({"ok": None, "detail": f"rc {res.rc}: {res.stderr.strip()[:120]}"} if res.rc != 0 else
                            {"ok": text == "Network Time: Off", "detail": text[:120]})
    try:
        probe = env.kernel_frequency()
        rows["kernel_frequency"] = {"ok": probe["raw_word"] == 0, "detail": f"raw_word {probe['raw_word']}",
                                    "probe": probe}
    except (OSError, ValueError) as exc:
        rows["kernel_frequency"] = {"ok": None, "detail": f"{type(exc).__name__}: {exc}"}
    marker = Path(cfg["high_power_marker"])
    try:
        present = os.path.lexists(marker)
        rows["high_power_marker"] = {"ok": not present, "detail": "present" if present else "absent"}
    except OSError as exc:
        rows["high_power_marker"] = {"ok": None, "detail": str(exc)}
    res = env.run(["/bin/launchctl", "list"], timeout=15)
    hits = [line for line in res.stdout.splitlines() if NIGHT_LABEL.search(line)] if res.rc == 0 else None
    rows["launchd_labels"] = ({"ok": None, "detail": f"rc {res.rc}"} if hits is None else
                              {"ok": not hits, "detail": "; ".join(hits)[:300] or "none"})
    if kind == "arm":
        res = env.run(["/usr/bin/sudo", "-n", "-l", "/bin/kill"], timeout=15)
        rows["sudo_kill"] = {"ok": None if res.rc is None else res.rc == 0, "detail": f"rc {res.rc}"}
    res = env.run(["/bin/zsh", cfg["measurement_mode_script"], "verify"], timeout=120)
    fails = [line for line in (res.stdout + res.stderr).splitlines() if "FAIL" in line]
    rows["measurement_mode"] = ({"ok": None, "detail": res.stderr.strip()[:200]} if res.rc is None else
                                {"ok": res.rc == 0, "detail": "; ".join(fails)[:300] or f"rc {res.rc}",
                                 "agent_only": bool(fails) and all("agent" in f.lower() for f in fails)})
    rows["monitors"] = _pgrep(env, ["/usr/bin/pgrep", "-fl", r"km003c_monitor\.py|hazard_monitor\.py"])
    rows["root_powermetrics"] = _pgrep(env, ["/usr/bin/pgrep", "-u", "root", "-x", "powermetrics"])
    rows["span_processes"] = _pgrep(env, SPAN_PROCESSES)
    try:
        current = fence.read_fence(Path(cfg["custody_root"]))
        ok = current is None or current["purpose"] in allowed_fence_purposes
        rows["launch_fence"] = {"ok": ok, "detail": "none" if current is None else json.dumps(current)}
    except (OSError, ValueError) as exc:
        rows["launch_fence"] = {"ok": None, "detail": str(exc)}
    if kind == "arm":
        found, unknown = [], []
        for argv in (["/usr/bin/pgrep", "-x", "claude"], ["/usr/bin/pgrep", "-x", "codex"],
                     ["/usr/bin/pgrep", "-fl", "mcp-server|mcp_server|modelcontextprotocol"]):
            row = _pgrep(env, argv)
            (found if row["ok"] is False else unknown if row["ok"] is None else []).append(row["detail"])
        rows["agents"] = {"ok": None if unknown else not found, "detail": "; ".join(found + unknown)[:300] or "none"}
    return {"kind": kind, "epoch": env.now(), "lines": rows}


def signing_check(cfg, env):
    """Mythos F11: before an arm, prove the bundle can be signed (sign a scratch blob with the key)."""
    key = cfg["signing_key"]
    if not os.path.isfile(key):
        return {"ok": False, "detail": f"no signing key at {key}"}
    with tempfile.TemporaryDirectory() as tmp:
        blob = Path(tmp) / "probe"
        blob.write_text("cadence-controller signing probe\n")
        res = env.run(["ssh-keygen", "-Y", "sign", "-f", key, "-n", "git", str(blob)], timeout=30)
        ok = res.rc == 0 and (Path(tmp) / "probe.sig").is_file()
    return {"ok": ok, "detail": "signed a probe" if ok else f"ssh-keygen -Y sign rc {res.rc}: {res.stderr[:120]}"}


def verdict_signers_check(cfg):
    """Mythos N14: the desk's allowed-signers file must name the ``cadence-desk`` key before an arm, or the span
    would run and its verdict could never be read."""
    path = Path(cfg["verdict_signers"])
    try:
        lines = [x for x in path.read_text().splitlines() if x.strip() and not x.startswith("#")]
    except OSError as exc:
        return {"ok": False, "detail": f"{path}: {exc}"}
    ok = bool(lines) and all(x.split()[0] == desk_transport.DESK_PRINCIPAL for x in lines)
    return {"ok": ok, "detail": f"{len(lines)} line(s), principals {sorted({x.split()[0] for x in lines})}"}


def proof_digest(proof):
    return law.digest(proof)


# --------------------------------------------------------------------------
# The audit branch: the standing index, queues, desk verdicts, sessions, the watcher stamp
# --------------------------------------------------------------------------
class Git:
    """The controller's own clone (never the canonical root). Network calls go through ``guard``."""

    def __init__(self, cfg, env, guard):
        self.cfg, self.env, self.guard = cfg, env, guard
        self.dir = cfg["git_dir"]
        self.ref = f"refs/remotes/origin/{cfg['audit_ref']}"

    def git(self, *args, timeout=120, input_text=None, env=None):
        return self.env.run(["git", "-C", self.dir, *args], timeout=timeout, input_text=input_text, env=env)

    VERDICTS = "refs/remotes/origin/cadence-desk-final/"

    def fetch_audit(self):
        """The audit branch and the desk's signed verdict refs (FORMAT.md section 3), in one fetch."""
        self.guard("git fetch audit and verdicts")
        res = self.git("fetch", "--quiet", "--no-tags", "origin",
                       f"+refs/heads/{self.cfg['audit_ref']}:{self.ref}",
                       f"+{desk_transport.VERDICT_REF_PREFIX}*:{self.VERDICTS}*", timeout=300)
        return res.rc == 0

    def verdict_refs(self):
        res = self.git("for-each-ref", "--format=%(refname)", self.VERDICTS)
        return [line[len(self.VERDICTS):] for line in res.stdout.splitlines() if line.startswith(self.VERDICTS)] \
            if res.rc == 0 else None

    def push_commit(self, sha, ref):
        """Push a local signed commit to ``ref`` once. An existing remote ref with the same tree is success (a
        retried close); a different tree is a refusal (FORMAT.md section 1: created once)."""
        self.guard(f"git push {ref}")
        tree = self.git("rev-parse", f"{sha}^{{tree}}").stdout.strip()
        remote = self.git("ls-remote", "origin", ref, timeout=120)
        if remote.rc != 0:
            return None, f"ls-remote: {remote.stderr.strip()[:200]}"
        if remote.stdout.strip():
            have = remote.stdout.split()[0]
            self.git("fetch", "--quiet", "origin", have, timeout=120)
            have_tree = self.git("rev-parse", f"{have}^{{tree}}")
            if have_tree.rc == 0 and have_tree.stdout.strip() == tree:
                return have, None
            return None, f"{ref} exists with another tree"
        push = self.git("push", "--quiet", "origin", f"{sha}:{ref}", timeout=300)
        return (sha, None) if push.rc == 0 else (None, f"push: {push.stderr.strip()[:200]}")

    def tip(self):
        res = self.git("rev-parse", self.ref)
        return res.stdout.strip() if res.rc == 0 else None

    def is_ancestor(self, old, new):
        return self.git("merge-base", "--is-ancestor", old, new).rc == 0

    def ensure_commit(self, sha):
        if self.git("cat-file", "-e", f"{sha}^{{commit}}").rc == 0:
            return True
        self.guard(f"git fetch {sha[:12]}")
        self.git("fetch", "--quiet", "--no-tags", "origin", sha, timeout=300)
        return self.git("cat-file", "-e", f"{sha}^{{commit}}").rc == 0

    def show_bytes(self, rev, path):
        try:
            done = subprocess.run(["git", "-C", self.dir, "show", f"{rev}:{path}"], capture_output=True, timeout=60)
        except (OSError, subprocess.SubprocessError):
            return None
        return done.stdout if done.returncode == 0 else None

    def commits(self, path):
        """[(sha, committer epoch)] of commits touching ``path`` on the audit ref, oldest first."""
        res = self.git("log", "--reverse", "--format=%H %ct", self.ref, "--", path)
        if res.rc != 0:
            return None
        return [(sha, int(ct)) for sha, ct in (line.split() for line in res.stdout.splitlines() if line.strip())]

    def list_dir(self, path):
        res = self.git("ls-tree", "--name-only", self.ref, path.rstrip("/") + "/")
        return [Path(x).name for x in res.stdout.split()] if res.rc == 0 else []

    def worktree_add(self, path, sha):
        return self.git("worktree", "add", "--detach", str(path), sha, timeout=300)


def load_kit_bytes(raw, sha, batch_window):
    if sha256_bytes(raw) != sha:
        raise kitmod.KitError([f"kit bytes hash {sha256_bytes(raw)[:12]}, pinned {sha[:12]}"])
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "kit.json"
        path.write_bytes(raw)
        kwargs = {}
        if batch_window not in law.BATCH_RULES:
            h0, m0, h1, m1 = (int(x) for x in batch_window.replace("-", ":").split(":"))
            kwargs["batch_window"] = ((h0, m0), (h1, m1))
        kit, _got = kitmod.load_kit(path, **kwargs)
    return kit


def read_audit(cfg, git, state):
    """Everything the decision needs from the audit branch, read fresh. Returns (inputs, reasons)."""
    reasons = []
    rd = cfg["records_dir"].rstrip("/")
    out = {"standing": None, "queues": [], "fallback_queues": [], "verdicts": {}, "ready": [], "done": set(),
           "watcher": None, "watcher_commit": None, "watcher_sha": None, "kit_bytes": {}, "tip": None, "kits": {},
           "record_epochs": {}, "verdict_tips": {}}
    if not git.fetch_audit():
        return out, [law.reason("FETCH_FAILED")]
    tip = git.tip()
    out["tip"] = tip
    seen = read_json(state / "audit-tip.json")
    if tip is None:
        return out, [law.reason("FETCH_FAILED", "no audit tip")]
    if seen and seen.get("tip") != tip and not git.is_ancestor(seen["tip"], tip):
        return out, [law.reason("AUDIT_REWRITTEN", f"{seen['tip'][:12]} is not an ancestor of {tip[:12]}")]
    raw = git.show_bytes(git.ref, f"{rd}/STANDING.json")
    if raw is None:
        return out, [law.reason("STANDING_MISSING")]
    try:
        standing = law.validate_standing(json.loads(raw))
    except (ValueError, law.StandingError) as error:
        return out, [law.reason("STANDING_INVALID", "; ".join(getattr(error, "problems", [str(error)]))[:400])]
    out["standing"] = standing
    # When each gate record first appeared: a release committed before its span closed is a contradiction (N14).
    for sha, epoch in git.commits(f"{rd}/STANDING.json") or []:
        try:
            version = json.loads(git.show_bytes(sha, f"{rd}/STANDING.json") or b"{}")
        except ValueError:
            continue
        for r in version.get("gate_records") or []:
            if isinstance(r, dict) and r.get("decision") == "release":
                out["record_epochs"].setdefault((r.get("plan_id"), r.get("gate")), epoch)
    kits = {}
    for sha, entry in standing["kits"].items():
        src = entry["source"]
        if not git.ensure_commit(src["commit"]):
            reasons.append(law.reason("KIT_UNREADABLE", f"{sha[:12]}: commit {src['commit'][:12]} not fetched"))
            continue
        kraw = git.show_bytes(src["commit"], src["path"])
        try:
            kits[sha] = load_kit_bytes(kraw or b"", sha, entry["batch_window"])
            out["kit_bytes"][sha] = kraw
        except (kitmod.KitError, ValueError) as error:
            reasons.append(law.reason("KIT_UNREADABLE", f"{sha[:12]}: {'; '.join(getattr(error, 'problems', [str(error)]))}"[:300]))
    out["kits"] = kits
    seen_queues = read_json(state / "queues-seen.json") or {}
    f2 = [{**x, "fallback": True} for f in standing["fallback"] if f["kind"] == "F2" for x in f["queues"]]
    for entry in [*standing["queues"], *f2]:
        view = read_queue(git, entry, kits, standing, seen_queues.get(entry["path"]))
        (out["fallback_queues"] if entry.get("fallback") else out["queues"]).append(view)
    plans = git.verdict_refs()
    if plans is None:
        reasons.append(law.reason("FETCH_FAILED", "the desk verdict refs could not be listed"))
        plans = []
    tips = read_json(state / "verdict-tips.json") or {}
    for pid in plans:   # FORMAT.md section 4 item 1: the desk's own reader verifies each signed verdict
        tip = git.git("rev-parse", f"{git.VERDICTS}{pid}").stdout.strip()
        if tips.get(pid) and tips[pid] != tip and not git.is_ancestor(tips[pid], tip):
            # Mythos N10: a verdict ref only moves forward; a rollback to an earlier signed judgment is refused.
            out["verdicts"][pid] = {"error": f"verdict ref rolled back from {tips[pid][:12]} to {tip[:12]}"}
            continue
        out["verdict_tips"][pid] = tip
        try:
            doc, _summary = desk_transport.read_verdict(git.dir, f"{git.VERDICTS}{pid}",
                                                        allowed_signers=cfg["verdict_signers"], plan_id=pid)
            out["verdicts"][pid] = {"doc": doc}
        except (desk_transport.TransportRefusal, ValueError, OSError) as error:
            out["verdicts"][pid] = {"error": f"{type(error).__name__}: {error}"}
    for name in git.list_dir(f"{rd}/sessions"):
        rec = git.show_bytes(git.ref, f"{rd}/sessions/{name}")
        try:
            doc = json.loads(rec)
        except (TypeError, ValueError):
            reasons.append(law.reason("SESSION_INVALID", name))
            continue
        if name.startswith("READY-"):
            out["ready"].append(doc)
        elif name.startswith("DONE-") and doc.get("schema") == law.SESSION_DONE_SCHEMA:
            out["done"].add(doc.get("session_id"))
    stamp = git.show_bytes(git.ref, f"{rd}/watcher-stamp.json")
    try:
        out["watcher"] = json.loads(stamp) if stamp is not None else None
    except ValueError:
        out["watcher"] = {"invalid": True}
    commits = git.commits(f"{rd}/watcher-stamp.json") if stamp is not None else None
    if commits:
        out["watcher_sha"], out["watcher_commit"] = commits[-1]
    return out, reasons


def read_queue(git, entry, kits, standing, seen):
    """One listed queue. Missing, invalid, not append-only, or not extending what the controller last read: each
    is a reason the selector raises before any candidate (Sol 5; Mythos F4)."""
    path = entry["path"]
    view = {"path": path, "role": entry["role"], "fallback": bool(entry.get("fallback")), "doc": None,
            "commit_epoch": None, "first_commit_epoch": None, "first_commit": None, "kits": {}, "reasons": [],
            "closed_ids": set(), "withdrawn_ids": set(standing["withdrawn"]), "digest": None, "tip_commit": None}
    raw = git.show_bytes(git.ref, path)
    if raw is None:
        view["reasons"].append(law.reason("QUEUE_MISSING", path))
        return view
    view["digest"] = sha256_bytes(raw)
    try:
        doc = json.loads(raw)
        span_kits = {}
        for span in doc.get("spans", []):
            k = span.get("kit") or {}
            if k.get("sha256") in kits and k.get("path") not in span_kits:
                span_kits[k["path"]] = (kits[k["sha256"]], k["sha256"])
        q.validate_queue(doc, span_kits)
        from scripts import cadence_queue as cq
        with tempfile.TemporaryDirectory() as tmp:
            for kpath, (kit, _sha) in span_kits.items():
                dest = Path(tmp) / kpath
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(json.dumps(kit))
            problems = cq.qual_roster_problems(doc, tmp)
        if problems:
            raise q.QueueError(problems)
    except (ValueError, q.QueueError, kitmod.KitError) as error:
        view["reasons"].append(law.reason("QUEUE_INVALID", f"{path}: {'; '.join(getattr(error, 'problems', [str(error)]))}"[:400]))
        return view
    view["doc"] = doc
    view["kits"] = {sha: kits[sha] for _p, (_k, sha) in span_kits.items()}
    commits = git.commits(path)
    if not commits:
        view["reasons"].append(law.reason("QUEUE_MISSING", f"{path}: no commit history"))
        return view
    view["first_commit"], view["first_commit_epoch"] = commits[0]
    view["tip_commit"], view["commit_epoch"] = commits[-1]
    docs = []
    for sha, _ct in commits:
        blob = git.show_bytes(sha, path)
        if blob is None:
            continue   # a commit that deleted the file is not a version
        try:
            docs.append(json.loads(blob))
        except ValueError:
            docs.append(None)
    problems = law.append_only_problems(docs)
    if problems:
        view["reasons"].append(law.reason("QUEUE_NOT_APPEND_ONLY", "; ".join(problems)[:300]))
    if seen:   # Mythos F4: a rewrite (amend, force-push) must still extend what this controller read and armed from
        if seen.get("first_commit") != view["first_commit"]:
            view["reasons"].append(law.reason("QUEUE_REWRITTEN", f"{path}: first commit changed "
                                                                 f"{str(seen.get('first_commit'))[:12]} -> "
                                                                 f"{view['first_commit'][:12]}"))
        if doc.get("spans", [])[:len(seen.get("spans", []))] != seen.get("spans", []):
            view["reasons"].append(law.reason("QUEUE_REWRITTEN", f"{path}: spans already read were changed"))
    return view


def read_issues(cfg, env, guard):
    guard("gh issue list")
    res = env.run([*cfg["gh_argv"], "issue", "list", "--repo", cfg["repo_slug"], "--state", "open", "--author",
                   cfg["owner_login"], "--limit", str(VETO_LIMIT), "--json", "number,title,body,author,labels,state"],
                  timeout=120)
    if res.rc != 0:
        return None
    try:
        doc = json.loads(res.stdout)
    except ValueError:
        return None
    if not isinstance(doc, list) or len(doc) >= VETO_LIMIT:   # a full page may hide a veto (Mythos F22)
        return None
    return doc


def server_time(cfg, env, guard):
    """The server's clock (the HTTP Date of an API reply), for the host-clock check (Mythos F23)."""
    guard("gh api date")
    res = env.run([*cfg["gh_argv"], "api", "-i", "rate_limit"], timeout=60)
    if res.rc != 0:
        return None
    for line in res.stdout.splitlines():
        if line.lower().startswith("date:"):
            with contextlib.suppress(TypeError, ValueError):
                return parsedate_to_datetime(line.split(":", 1)[1].strip()).timestamp()
    return None


def post_notice(cfg, env, guard, issue, text):
    guard("gh issue comment")
    res = env.run([*cfg["gh_argv"], "issue", "comment", str(issue), "--repo", cfg["repo_slug"], "--body", text],
                  timeout=120)
    return res.rc == 0


def receipt_census(roots, output_root):
    """Item 331's census, one pass: the newest ``runner_receipt.json`` at depth <= 4 under each root (mtime rounded
    up, with its path), and every campaign receipt under the output root. A missing root, a lookup error or no
    receipt at all raises: missing evidence is never 0."""
    newest, path, count, campaign = None, None, 0, []
    out_root = output_root.rstrip("/")

    def fail(error):
        raise error

    for root in roots:
        if not os.path.isdir(root):
            raise FileNotFoundError(f"receipt root missing: {root}")
        base = root.rstrip("/").count("/")
        for dirpath, dirnames, filenames in os.walk(root, onerror=fail):
            if dirpath.count("/") - base >= 3:
                dirnames[:] = []
            if RECEIPT in filenames:
                p = os.path.join(dirpath, RECEIPT)
                m = os.stat(p).st_mtime
                count += 1
                if newest is None or m > newest:
                    newest, path = m, p
                if p.startswith(out_root + "/") and p.count("/") - out_root.count("/") == 3:
                    campaign.append(p)
    if count == 0:
        raise FileNotFoundError("the receipt census found no runner_receipt.json")
    return {"newest": (math.ceil(newest), path), "campaign": sorted(set(campaign))}


# --------------------------------------------------------------------------
# Preparation and launch (production)
# --------------------------------------------------------------------------
ARM_CHILD = r'''
import json, os, sys, time
from pathlib import Path
req = json.loads(sys.argv[1])
sys.path.insert(0, req["repo"])
from scripts import launch_cadence_span as L
from scripts import launch_align_r0 as base
from scripts import cadence_legs_runner as R
# Plan at this clock with the pin's own launch deadline (worst + soak retry budget + reserves), so the time the
# controller spent preparing never shortens the launcher's own fit check (Mythos F10).
plan = L.cadence_plan(Path(req["kit"]), req["legs"], req["batch_window"])
deadline = R.launch_deadline(plan) + 60
root = Path(req["custody_root"])
real_read, real_write = base.read_fence, base.write_fence
state = {"transferred": False, "bootstrap_t": None}
def ours(cur):
    return cur is not None and cur["purpose"] == req["standing_purpose"] and cur["pid"] == req["controller_pid"]
with base.fence_lock(root):
    cur = real_read(root)
if cur is not None and not ours(cur):
    print(json.dumps({"arm_child_refused": "a fence other than the controller's standing fence is up", "fence": cur}),
          flush=True)
    sys.exit(3)
t0 = time.time()
if t0 > req["lease_until"]:
    print(json.dumps({"arm_child_refused": "the arm lease expired", "t0": t0, "lease_until": req["lease_until"]}),
          flush=True)
    sys.exit(4)
# The lease at the launch boundary itself (Sol R3): the frozen launcher's one bootstrap call is refused once the lease
# has expired, and the instant it is made is the span's recorded t0. The launcher's own except path then boots out and
# clears its fence, and main() returns 2. Every other subprocess call passes through unchanged.
import subprocess as _sp
_real_run = _sp.run
def _run(argv, *a, **k):
    if len(argv) > 1 and str(argv[1]) == "bootstrap":
        now = time.time()
        if now > req["lease_until"]:
            raise _sp.SubprocessError(f"the arm lease expired before bootstrap ({now:.3f} > {req['lease_until']:.3f})")
        state["bootstrap_t"] = now
    return _real_run(argv, *a, **k)
_sp.run = _run
# The atomic fence transfer: the launcher's busy check does not see the controller's own standing fence, and its
# write_fence (an os.replace under the fence lock) replaces it, so a live owner holds the fence at every instant.
def read_fence(r):
    cur = real_read(r)
    return None if (not state["transferred"] and ours(cur)) else cur
def write_fence(r, record):
    real_write(r, record)
    state["transferred"] = True
base.read_fence, base.write_fence = read_fence, write_fence
argv = ["launch", "--repo", req["repo"], "--python-bin", req["python"], "--kit", req["kit"], "--legs", req["legs"],
        *(["--batch-window", req["batch_window"]] if req["batch_window"] else []),
        "--output", req["output"], "--disk-path", req["repo"], "--custody-root", req["custody_root"],
        "--magistrate-pid", str(os.getpid()), "--deadline", repr(deadline),
        "--exit-wait-seconds", "180", "--start-wait-seconds", "30",
        *(["--launchctl-bin", req["launchctl_bin"]] if req.get("launchctl_bin") else [])]
rc = L.main(argv)
print(json.dumps({"arm_child_pid": os.getpid(), "launch_rc": rc, "t0": state.get("bootstrap_t"), "checked_at": t0,
                  "deadline": deadline, "transferred": state["transferred"]}), flush=True)
sys.exit(rc)
'''


class Preparer:
    """Kit copy by hash, a fresh detached worktree at the frozen commit, validate-kit and the pinned plan."""

    def __init__(self, cfg, env, git):
        self.cfg, self.env, self.git = cfg, env, git

    def materialize(self, plan_id, kit_sha, kit_raw, frozen_commit):
        """Network part: fetch the frozen commit and add the worktree. Returns (paths, problem)."""
        kits_dir = Path(self.cfg["kits_dir"])
        kits_dir.mkdir(parents=True, exist_ok=True)
        kit_path = kits_dir / f"{plan_id}-{kit_sha[:12]}.json"
        if kit_path.exists():
            if sha256_file(kit_path) != kit_sha:
                return None, f"{kit_path} exists with other bytes"
        else:
            with open(kit_path, "xb") as handle:
                handle.write(kit_raw)
        if not self.git.ensure_commit(frozen_commit):
            return None, f"frozen commit {frozen_commit[:12]} not fetched"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        wt = Path(self.cfg["worktrees_root"]) / f"cadence-{plan_id}-{stamp}"
        res = self.git.worktree_add(wt, frozen_commit)
        if res.rc != 0:
            return None, f"worktree add: {res.stderr.strip()[:200]}"
        return {"kit": str(kit_path), "repo": str(wt)}, None

    def check(self, paths, kit, kit_sha, legs, batch_rule, t0):
        """Local part (no network): HEAD, clean tree, validate-kit --repo, plan. Returns (plan_info, problem)."""
        wt, py = paths["repo"], self.cfg["measurement_python"]
        head = self.env.run(["git", "-C", wt, "rev-parse", "HEAD"], timeout=30).stdout.strip()
        if head != kit["frozen"]["commit"]:
            return None, f"HEAD {head[:12]} is not the frozen commit"
        if self.env.run(["git", "-C", wt, "status", "--porcelain"], timeout=60).stdout.strip():
            return None, "the measurement worktree is not clean"
        windows = [None] if batch_rule == "none" else (["02:00-02:35", "13:14-13:15"] if batch_rule == "rl172"
                                                       else [batch_rule])
        last = ""
        for window in windows:
            wargs = ["--batch-window", window] if window else []
            res = self.env.run([py, "-B", f"{wt}/scripts/cadence_queue.py", "validate-kit", paths["kit"], "--repo", wt,
                                *wargs], cwd=wt, timeout=120)
            try:
                vk = json.loads(res.stdout)
            except ValueError:
                vk = {}
            if not (res.rc == 0 and vk.get("ok") and vk.get("frozen_paths_verified") and vk.get("kit_sha256") == kit_sha
                    and vk.get("frozen_commit") == kit["frozen"]["commit"]):
                last = f"validate-kit rc {res.rc}: {(res.stdout + res.stderr).strip()[:200]}"
                continue
            res = self.env.run([py, "-B", f"{wt}/scripts/cadence_legs_runner.py", "plan", "--kit", paths["kit"],
                                "--legs", ",".join(legs), "--t0", repr(t0), *wargs], cwd=wt, timeout=120)
            try:
                plan = json.loads(res.stdout)
            except ValueError:
                plan = None
            if res.rc == 0 and plan and [x["leg_id"] for x in plan["legs"]] == legs:
                return {"plan": plan, "batch_window": window, "expected_windows": [window] if window else [],
                        "worst_case_s": plan["worst_case_s"]}, None
            last = f"plan rc {res.rc}: {res.stderr.strip()[:200]}"
        return None, "PLAN_REFUSED_AT_T0: " + last


class Launcher:
    """Spawn the arm child under the measurement interpreter; its PID is the launch's handoff PID."""

    def __init__(self, cfg, env):
        self.cfg, self.env = cfg, env

    def launch(self, request):
        res = self.env.run([self.cfg["measurement_python"], "-I", "-B", "-c", ARM_CHILD, json.dumps(request)],
                           cwd=request["repo"], timeout=180,
                           env={"PATH": "/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin", "LC_ALL": "C",
                                "HOME": os.environ.get("HOME", "/tmp")})
        launched, child = None, {}
        for line in res.stdout.splitlines():
            if not line.strip().startswith("{"):
                continue
            with contextlib.suppress(ValueError):
                doc = json.loads(line)
                if "fence" in doc and "next" in doc:
                    launched = doc
                if "arm_child_pid" in doc or "arm_child_refused" in doc:
                    child = doc
        return {"rc": res.rc, "launch": launched, "arm_child_pid": child.get("arm_child_pid"), "t0": child.get("t0"),
                "deadline": child.get("deadline"), "refused": child.get("arm_child_refused"),
                "stderr": res.stderr[-1500:]}


# --------------------------------------------------------------------------
# The controller
# --------------------------------------------------------------------------
class Controller:
    BLOCKING = ("HALT", "V4_SESSION")
    MAINTENANCE = ("dasd", "XProtect", "XprotectService", "XProtectPluginService", "mds", "mds_stores", "mdworker",
                   "mdworker_shared", "backupd", "softwareupdated", "mobileassetd")

    def __init__(self, cfg, *, env=None, git=None, preparer=None, launcher=None, issues=None, census=None,
                 proof=None, signing=None, clock=None, notice=None, pid=None):
        self.cfg = cfg
        self.env = env or Env()
        self.state = Path(cfg["state_dir"])
        self.custody = Path(cfg["custody_root"])
        self.pid = pid or os.getpid()
        self.git = git or Git(cfg, self.env, self.guard)
        self.preparer = preparer or Preparer(cfg, self.env, self.git)
        self.launcher = launcher or Launcher(cfg, self.env)
        self.issues = issues or (lambda: read_issues(cfg, self.env, self.guard))
        self.census = census or (lambda: receipt_census(cfg["receipt_roots"], cfg["output_root"]))
        self.proof = proof or (lambda kind, allowed=(): host_proof(cfg, self.env, kind, allowed_fence_purposes=allowed))
        self.signing = signing or (lambda: signing_check(cfg, self.env))
        self.clock = clock or (lambda: server_time(cfg, self.env, self.guard))
        self.notice = notice or (lambda issue, text: post_notice(cfg, self.env, self.guard, issue, text))
        self.token = (read_json(self.state / "token.json") or {}).get("token")
        if not self.token:
            self.token = uuid.uuid4().hex[:12]
            atomic_json(self.state / "token.json", {"token": self.token})
        self.network_open = True
        self.network_log = []
        self.raised = set()

    # -- network guard (RL-172 (g) 8: all network work ends before the next soak starts) -------------
    def guard(self, what):
        if not self.network_open:
            raise NetworkClosed(f"{what}: network is closed (a span is armed or the arm's network phase ended)")
        self.network_log.append({"what": what, "epoch": self.env.now()})

    # -- records ------------------------------------------------------------------------------------
    def span_dir(self, plan_id):
        return self.state / "spans" / plan_id

    def transition(self, plan_id, kind, body):
        row = {"schema": RECORD_SCHEMA, "plan_id": plan_id, "transition": kind, "epoch": self.env.now(),
               "at": iso(self.env.now()), **body}
        append_jsonl(self.state / "transitions.jsonl", row)
        if plan_id:
            append_jsonl(self.span_dir(plan_id) / "transitions.jsonl", row)
        return row

    def records(self):
        """Controller span records (arm.json merged with close.json and the intent's identities), and intents
        without an arm record."""
        out, orphans = [], []
        base = self.state / "spans"
        for d in sorted(base.iterdir()) if base.is_dir() else []:
            intent = read_json(d / "intent.json")
            if intent is None:
                continue
            arm = read_json(d / "arm.json")
            if arm is None:
                orphans.append(intent)
                continue
            rec = {**arm, "campaign_id": intent["kit"]["campaign_id"],
                   "armed": {"plan_id": intent["plan_id"], "queue_id": intent["queue"]["queue_id"],
                             "span_id": intent["span"]["span_id"], "attempt": intent["span"]["attempt"]}}
            close = read_json(d / "close.json")
            if close is not None:
                rec.update(status=close["status"], closed_epoch=close.get("closed_epoch") or close.get("receipt_epoch"),
                           bundle_sha256=close.get("manifest_sha256"), pushed=close.get("pushed"),
                           gates=close.get("gates", []), legs_finished=close.get("legs_finished"),
                           runner_t0=close.get("runner_t0"))
            out.append(rec)
        return out, orphans

    def externals(self):
        path = self.state / "external.jsonl"
        if not path.is_file():
            return []
        merged = {}
        for line in path.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                old = merged.get(row["run_id"], {})
                new = {**old, **row}
                if old.get("closed_epoch") is not None and row.get("closed_epoch") is not None:
                    new["closed_epoch"] = max(old["closed_epoch"], row["closed_epoch"])   # the floor never shortens
                merged[row["run_id"]] = new
        return list(merged.values())

    # -- fences --------------------------------------------------------------------------------------
    def standing_purpose(self):
        return f"{STANDING_FENCE_PREFIX}{self.token}"

    def hold_fence(self):
        if not self.cfg["hold_standing_fence"]:
            return "disabled"
        self.custody.mkdir(parents=True, exist_ok=True)
        with fence.fence_lock(self.custody):
            cur = fence.read_fence(self.custody)
            if cur is not None and not (cur["purpose"] == self.standing_purpose() and cur["pid"] == self.pid):
                if not (cur["purpose"].startswith(STANDING_FENCE_PREFIX) and not self.env.pid_alive(cur["pid"])):
                    return "foreign"
            fence.write_fence(self.custody, {"purpose": self.standing_purpose(), "pid": self.pid,
                                             "deadline": self.env.now() + STANDING_FENCE_S})
        return "held"

    def release_fence(self):
        with contextlib.suppress(FileNotFoundError):
            fence.clear_owned(self.custody, self.standing_purpose(), self.pid)

    # -- pages ---------------------------------------------------------------------------------------
    def unacked_pages(self):
        pages = self.state / "pages"
        out = []
        for p in sorted(pages.glob("*.json")) if pages.is_dir() else []:
            if not (self.state / "acks" / p.name).exists():
                out.append(read_json(p))
        return out

    def page(self, kind, reasons, context=None):
        """Page once per episode of a situation. The key is a digest of the kind, the codes, the spans and the context
        (not of free-text details, which may carry a countdown). An acknowledged page whose situation was absent on a
        later full evaluation is cleared; the situation's next occurrence is a new page (Mythos N4)."""
        body = {"kind": kind, "reasons": [{k: r.get(k) for k in ("code", "category", "detail", "span")}
                                          for r in reasons], "context": context or {}}
        key = {"kind": kind, "codes": sorted({(r["code"], str(r.get("span"))) for r in reasons}),
               "context": context or {}}
        base = f"{kind.lower().replace('_', '-')}-{law.digest(key)[:16]}"
        self.raised.add(base)
        pages = self.state / "pages"
        episodes = sorted(int(p.stem.rsplit("-e", 1)[1]) for p in pages.glob(f"{base}-e*.json")) if pages.is_dir() else []
        if episodes:
            last = f"{base}-e{episodes[-1]}"
            if not (self.state / "acks" / f"{last}.json").exists() or not (pages / f"{last}.cleared").exists():
                return last, False       # unacknowledged, or acknowledged and never seen absent since: same episode
        page_id = f"{base}-e{(episodes[-1] + 1) if episodes else 1}"
        exclusive_json(pages / f"{page_id}.json", {"page_id": page_id, "epoch": self.env.now(), "at": iso(self.env.now()),
                                                   **body})
        self.release_fence()
        self.transition(None, "page", {"page_id": page_id, "kind": kind, "codes": [r["code"] for r in reasons]})
        for r in reasons:
            if r.get("span"):
                self.critical_path_event(r["span"], refusal=f"{r['code']}: {r['detail']}"[:300])
        return page_id, True

    def settle_pages(self):
        """After a full evaluation: every acknowledged page whose situation was not raised this tick is cleared, so a
        recurrence pages again (Mythos N4)."""
        pages = self.state / "pages"
        for p in pages.glob("*-e*.json") if pages.is_dir() else []:
            base = p.stem.rsplit("-e", 1)[0]
            if base not in self.raised and (self.state / "acks" / p.name).exists():
                cleared = pages / f"{p.stem}.cleared"
                if not cleared.exists():
                    cleared.write_text(iso(self.env.now()) + "\n")

    # -- status --------------------------------------------------------------------------------------
    def write_status(self, state, detail, *, sync=True):
        status = {"schema": RECORD_SCHEMA, "state": state, "detail": detail, "epoch": self.env.now(),
                  "at": iso(self.env.now()), "pid": self.pid, "pages": [p["page_id"] for p in self.unacked_pages()],
                  "standing_fence": self.standing_purpose()}
        atomic_json(self.state / "STATUS.json", status, sync=sync)
        atomic_json(self.state / "heartbeat.json", {"pid": self.pid, "epoch": self.env.now(), "state": state},
                    sync=sync)
        return status

    def wait(self, codes, detail, *, quiet=False):
        """Every wait is bounded (Mythos F7): a wait whose codes persist past ``stall_bound`` pages WAIT_STALL once
        per episode. An unread informational page keeps the fence released so the magistrate can run. A ``quiet``
        wait (a v4 window, an unreadable night-agent census) writes nothing synced and holds no fence (Mythos N15)."""
        now = self.env.now()
        sig = sorted(set(codes))
        episode = read_json(self.state / "wait-episode.json") or {}
        if episode.get("sig") != sig:
            episode = {"sig": sig, "since": now}
            atomic_json(self.state / "wait-episode.json", episode, sync=not quiet)
        if now - episode["since"] > law.stall_bound(sig):
            self.page("WAIT_STALL", [law.reason("WAIT_STALL", f"{', '.join(sig)} since {iso(episode['since'])}: "
                                                              f"{detail}"[:400])],
                      {"sig": sig, "since": episode["since"]})
        if quiet or self.unacked_pages():
            self.release_fence()
            return self.write_status("PAGED" if self.unacked_pages() else "WAIT",
                                     {"codes": sig, "detail": detail, "quiet": quiet,
                                      "pages": [p["page_id"] for p in self.unacked_pages()]}, sync=not quiet)
        held = self.hold_fence()
        return self.write_status("WAIT", {"codes": sig, "detail": detail, "fence": held})

    # -- the tick ------------------------------------------------------------------------------------
    def tick(self):
        now = self.env.now()
        self.raised = set()
        records, orphans = self.records()
        live = [r for r in records if r["status"] == "LIVE"]
        if live:
            return self.monitor(live[0])
        for intent in orphans:
            status = self.adopt_or_halt(intent)
            if status is not None:
                return status
        # Another run's fence (a file read, no command): wait while its PID lives, even past its deadline (Sol R2).
        current = self._foreign_fence()
        seen = read_json(self.state / "foreign.json")
        if current is not None:
            if not seen or seen.get("purpose") != current.get("purpose"):
                atomic_json(self.state / "foreign.json", {"purpose": current.get("purpose"), "first_seen": now})
            return self.wait(["SPAN_LIVE"], f"another run holds the host: {current.get('purpose')}")
        if seen:
            # Sol 10: the fence's disappearance proves nothing about the restore. Record the close as observed, the
            # restore unproven; the selector halts until note-run records the run's Check.
            self.record_external(seen["purpose"], "other", seen["first_seen"], now)
            (self.state / "foreign.json").unlink()
        self.record_acked_sessions(now)
        blocking = [p for p in self.unacked_pages() if p["kind"] in self.BLOCKING]
        if blocking:   # silence: no network and no host command until the magistrate acknowledges (F5, N15)
            self.release_fence()
            return self.write_status("PAGED", {"pages": [p["page_id"] for p in blocking], "silent": True}, sync=False)
        labels, ok = self.night_agents()
        night = read_json(self.state / "night.json")
        if not ok:   # Sol R2: an unreadable census is not "no night agent": no network until it reads clean
            return self.wait(["NIGHT_UNKNOWN"], labels, quiet=True)
        if labels:
            if not night:
                atomic_json(self.state / "night.json", {"labels": labels, "first_seen": now}, sync=False)
            return self.wait(["NIGHT_AGENT"], ", ".join(labels), quiet=True)
        if night:
            # Mythos N5: a W1, C or T window holds no desk fence. Its end is a close: observed now, restore unproven
            # until note-run records its Check; the 1,200 s floor counts from here.
            self.record_external("night:" + ",".join(night["labels"]), "v4-window", night["first_seen"], now)
            (self.state / "night.json").unlink()
        self.network_open = True
        self.network_log = []
        for rec in records:
            if rec.get("pushed") is False:
                self.push_close(rec["plan_id"])
        records, _ = self.records()
        snap, extra = self.snapshot(now, records)
        decision = law.select(snap)
        self.critical_path(decision, now)
        status = self.act(decision, snap, extra, records)
        if status.get("state") not in ("LIVE",):
            self.settle_pages()
        return status

    def record_external(self, run_id, kind, t0, now):
        append_jsonl(self.state / "external.jsonl", {
            "run_id": run_id, "kind": kind, "t0_epoch": t0, "closed_epoch": math.ceil(now), "restore": "unproven",
            "observed_by_controller": True})

    def record_acked_sessions(self, now):
        """A V4_SESSION page acknowledged by the magistrate (after the session, by the prompt) records the session as a
        close observed at the acknowledgement, restore unproven until note-run (Mythos N5)."""
        acks = self.state / "acks"
        for p in sorted((self.state / "pages").glob("v4-session-*-e*.json")) if (self.state / "pages").is_dir() else []:
            ack = acks / p.name
            marker = p.with_suffix(".recorded")
            if ack.exists() and not marker.exists():
                page = read_json(p)
                self.record_external(f"session:{page['page_id']}", "v4-session", page["epoch"],
                                     (read_json(ack) or {}).get("epoch", now))
                marker.write_text(iso(now) + "\n")

    def act(self, decision, snap, extra, records, *, final=False):
        if decision.action in ("arm", "arm-fallback"):
            if final:
                return self.wait(["SPAN_LIVE"], "re-deciding")
            return self.arm(decision, snap, extra, records)
        last = law.last_close(snap["runs"]) if snap.get("runs") else None
        episode = {"last_close": None if last is None else last.plan_id}
        if decision.action in ("halt", "cede", "page"):
            kind = {"halt": "HALT", "cede": "V4_SESSION", "page": decision.reasons[0]["code"]}[decision.action]
            page_id, new = self.page(kind, decision.reasons, episode)
            self.release_fence()
            return self.write_status("PAGED" if new or kind != "HALT" else "HALTED",
                                     {"page": page_id, "codes": [r["code"] for r in decision.reasons]})
        return self.wait([r["code"] for r in decision.reasons],
                         "; ".join(f"{r['code']}: {r['detail']}" for r in decision.reasons)[:400])

    def _foreign_fence(self):
        """Another run's fence, while its PID lives, whatever its deadline (Sol R2: a passed deadline is the
        watchdog's alarm, not proof the run ended). A fence that cannot be read is held as foreign."""
        try:
            cur = fence.read_fence(self.custody)
        except (OSError, ValueError) as exc:
            return {"purpose": f"unreadable: {exc}"}
        if cur is None or cur["purpose"].startswith(STANDING_FENCE_PREFIX):
            return None
        if not self.env.pid_alive(cur["pid"]):
            return None    # its owner is gone: the watchdog removes it and notices; our arm proof still refuses it
        return cur

    def night_agents(self):
        """(labels, ok). ``ok`` False when ``launchctl list`` failed or printed nothing parseable (Sol R2)."""
        res = self.env.run(["/bin/launchctl", "list"], timeout=15)
        if res.rc != 0 or not res.stdout.strip():
            return f"launchctl list rc {res.rc}: {res.stderr.strip()[:120]}", False
        return [line.split()[-1] for line in res.stdout.splitlines() if NIGHT_LABEL.search(line)], True

    def snapshot(self, now, records):
        audit, reasons = read_audit(self.cfg, self.git, self.state)
        standing = audit["standing"]
        extra = {"audit": audit, "markers": {}}
        empty = {"now": now, "standing": None if any(r["code"] == "AUDIT_REWRITTEN" for r in reasons) else standing,
                 "input_reasons": reasons, "queues": [], "fallback_queues": [], "runs": [], "desk_halts": [],
                 "vetoes": [], "watcher": [], "sessions": [], "census_reasons": [], "census_epoch": None,
                 "fallback": [], "plan_worst": lambda c: None}
        if empty["standing"] is None:
            return empty, extra
        runs = law.build_runs(standing, records, self.externals(), kits=audit["kits"])
        desk_halts = law.apply_verdicts(runs, audit["verdicts"], accept_mock=self.cfg["accept_mock_verdicts"])
        ran = {r.plan_id for r in runs}
        for view in audit["queues"] + audit["fallback_queues"]:
            view["closed_ids"] = ran
        issues = self.issues()
        try:
            census = self.census()
        except OSError as exc:
            census = f"host receipt census: {exc}"
        markers, receipts = {}, {}
        if isinstance(census, dict):
            m = law.CAMPAIGN_RECEIPT.search(census["newest"][1])
            if m:
                marker = Path(self.cfg["copy_marker_dir"]) / f"{m.group('plan')}.ok"
                with contextlib.suppress(OSError):
                    if marker.is_file() and not marker.is_symlink() and marker.stat().st_size > 0:
                        markers[m.group("plan")] = marker.read_text(errors="replace")[:200].strip()
            prior_ids = {p["plan_id"] for p in standing["prior_spans"]}
            for path in census["campaign"]:   # a prior span's receipt: its roster and kit only (Mythos N2)
                m = law.CAMPAIGN_RECEIPT.search(path)
                if m and m.group("plan") in prior_ids:
                    try:
                        doc = json.loads(Path(path).read_text())
                        receipts[m.group("plan")] = {"roster": doc.get("roster"),
                                                     "kit_sha256": (doc.get("kit") or {}).get("sha256")}
                    except (OSError, ValueError):
                        receipts[m.group("plan")] = {"roster": None, "kit_sha256": None}
        unpushed = [r["plan_id"] for r in records if r.get("pushed") is False]
        if unpushed:
            reasons = reasons + [law.reason("BUNDLE_UNAUTHENTICATED", ", ".join(unpushed))]
        extra["markers"] = markers
        snap = {"now": now, "standing": standing, "input_reasons": reasons, "queues": audit["queues"], "runs": runs,
                "desk_halts": desk_halts, "vetoes": law.veto_reasons(issues, self.cfg["owner_login"]),
                "watcher": law.watcher_reasons(audit["watcher"], audit["watcher_commit"], now, self.cfg["watcher_name"]),
                "sessions": law.session_reasons(standing, audit["ready"], audit["done"]),
                "census_reasons": law.census_reasons(census, runs, self.cfg["output_root"], markers),
                "census_epoch": census["newest"][0] if isinstance(census, dict) else None,
                "fallback": standing["fallback"], "fallback_queues": audit["fallback_queues"],
                "receipts": receipts, "record_epochs": audit["record_epochs"],
                "plan_worst": lambda cand: self.plan_worst(cand, audit, now)}
        if law.category(reasons) != "halt":
            self.remember(audit)
        return snap, extra

    def remember(self, audit):
        """Store the audit tip, each queue's first commit and spans, and each verdict ref's tip, after a read with no
        halt in its inputs, so a later rewrite or rollback is seen (Mythos F4, N10)."""
        if audit["tip"]:
            atomic_json(self.state / "audit-tip.json", {"tip": audit["tip"]})
        seen = read_json(self.state / "queues-seen.json") or {}
        for view in audit["queues"] + audit["fallback_queues"]:
            if view["doc"] is not None and not view["reasons"]:
                seen[view["path"]] = {"first_commit": view["first_commit"], "spans": view["doc"]["spans"],
                                      "digest": view["digest"]}
        atomic_json(self.state / "queues-seen.json", seen)
        tips = read_json(self.state / "verdict-tips.json") or {}
        tips.update(audit["verdict_tips"])
        atomic_json(self.state / "verdict-tips.json", tips)

    def plan_worst(self, cand, audit, now):
        kit = next(v["kits"][cand["kit_sha"]] for v in audit["queues"] + audit["fallback_queues"]
                   if cand["kit_sha"] in v["kits"])
        from joulewise.cadence import legs as legsmod
        try:
            plan = legsmod.plan_span(kit, t0_epoch=now, windows=[], leg_ids=cand["span"]["legs"])
        except legsmod.PlanError:
            return None
        return plan["worst_case_s"] + plan["soak_s"] + 560

    # -- critical-path ledger (RL-172 (i) row 6; Sol 14) ----------------------------------------------
    def critical_path(self, decision, now):
        for sid, codes in decision.gates.items():
            self.prereqs(sid, now, blocking=codes)

    def prereqs(self, sid, now, *, blocking=(), passed=(), stage_failed=None):
        """``blocking``: the codes holding the span at this observation. ``passed``: stages observed to pass now.
        A code's ``ready_at`` is the first observation at which it no longer blocked, never an earlier guess."""
        path = self.state / "critical-path" / f"{sid}.json"
        doc = read_json(path) or {"span_id": sid, "first_considered": now, "prereqs": {}, "start": None, "end": None,
                                  "refusal": None, "ready_all": None}
        doc.setdefault("prereqs", {})
        for code in blocking:
            row = doc["prereqs"].setdefault(code, {"first_blocked": now, "last_blocked": now, "ready_at": None})
            row["last_blocked"], row["ready_at"] = now, None
            if row.get("first_blocked") is None:
                row["first_blocked"] = now
        if blocking == () and passed == ():
            pass
        for code in passed:
            row = doc["prereqs"].setdefault(code, {"first_blocked": None, "last_blocked": None, "ready_at": None})
            if row["ready_at"] is None:
                row["ready_at"] = now
        if not passed:   # a selection observation: what no longer blocks became ready now
            for code, row in doc["prereqs"].items():
                if code not in blocking and row["ready_at"] is None and row.get("last_blocked") is not None:
                    row["ready_at"] = now
        if stage_failed:
            doc["refusal"] = stage_failed
        atomic_json(path, doc)

    def critical_path_event(self, span_id, **fields):
        path = self.state / "critical-path" / f"{span_id}.json"
        doc = read_json(path) or {"span_id": span_id, "first_considered": None, "prereqs": {}, "start": None,
                                  "end": None, "refusal": None, "ready_all": None}
        doc.update(fields)
        atomic_json(path, doc)

    # -- arm -----------------------------------------------------------------------------------------
    def arm(self, decision, snap, extra, records):
        cand = decision.candidate
        span, sha = cand["span"], cand["kit_sha"]
        sid, plan_id = span["span_id"], q.plan_id(span)
        audit = extra["audit"]
        standing = snap["standing"]
        entry = standing["kits"][sha]
        if self.cfg["hold_standing_fence"] and self.hold_fence() != "held":
            # Sol R7: the arm child transfers the standing fence atomically; without it held there is nothing to
            # transfer and the watchdog could start an activation before the launch fence exists.
            return self.wait(["SPAN_LIVE"], "the standing fence is not held; no arm without it")
        kit = next(v["kits"][sha] for v in audit["queues"] + audit["fallback_queues"] if sha in v["kits"])
        # 1. preparation's network part (a worktree prepared on an earlier tick for this plan is reused)
        prepared = read_json(self.span_dir(plan_id) / "prepared.json")
        if prepared and Path(prepared["repo"]).is_dir() and Path(prepared["kit"]).is_file():
            paths, problem = prepared, None
        else:
            paths, problem = self.preparer.materialize(plan_id, sha, audit["kit_bytes"][sha], kit["frozen"]["commit"])
            if paths:
                atomic_json(self.span_dir(plan_id) / "prepared.json", paths)
        if problem:
            return self._prepare_failed(plan_id, sid, "PREPARE", problem)
        self.prereqs(sid, self.env.now(), passed=["PREPARE"])
        # 2. validate-kit and the pinned plan (local)
        info, problem = self.preparer.check(paths, kit, sha, list(span["legs"]), entry["batch_window"], self.env.now())
        if problem:
            if problem.startswith("PLAN_REFUSED_AT_T0"):
                self.prereqs(sid, self.env.now(), blocking=["PLAN_REFUSED_AT_T0"])
                return self.wait(["PLAN_REFUSED_AT_T0"], problem)
            return self._prepare_failed(plan_id, sid, "VALIDATE_PLAN", problem)
        self.prereqs(sid, self.env.now(), passed=["VALIDATE_PLAN"])
        out = Path(self.cfg["output_root"]) / kit["campaign_id"] / (
            f"{plan_id}-{datetime.fromtimestamp(self.env.now(), timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
        if out.exists() or OUT_REFUSED.search(str(out) + "/") or str(out).startswith(str(self.custody)):
            return self._prepare_failed(plan_id, sid, "VALIDATE_PLAN", f"output {out} exists or is inside a refused root")
        # 3. the arm proof: readback, absence, and the signing key (local)
        proof = self.proof("arm", (self.standing_purpose(),))
        proof["lines"]["signing"] = self.signing()
        proof["lines"]["verdict_signers"] = verdict_signers_check(self.cfg)
        rs = law.proof_reasons(proof["lines"], "arm")
        if rs:
            self.prereqs(sid, self.env.now(), blocking=[r["code"] for r in rs])
            if law.category(rs) == "wait":
                return self.wait([r["code"] for r in rs], "; ".join(r["detail"] for r in rs)[:300])
            self.page("HALT", [dict(r, span=sid) for r in rs], {"plan_id": plan_id, "proof": proof_digest(proof)})
            return self.write_status("HALTED", {"codes": [r["code"] for r in rs]})
        self.prereqs(sid, self.env.now(), passed=["HOST_PROOF"])
        # 4. every authority again, now (Sol 4): the same decision, or no arm. The lease counts from this read, and
        # everything after it (the clock check, the notice post, the launch) spends the same budget (Sol R3, N7).
        authority_read = self.env.now()
        snap2, extra2 = self.snapshot(authority_read, records)
        d2 = law.select(snap2)
        self.critical_path(d2, self.env.now())
        if not (d2.action == decision.action and d2.candidate and q.plan_id(d2.candidate["span"]) == plan_id):
            return self.act(d2, snap2, extra2, records, final=True)
        self.prereqs(sid, self.env.now(), passed=["AUTHORITY"])
        audit2 = extra2["audit"]
        view = next(v for v in audit2["queues"] + audit2["fallback_queues"] if v["path"] == cand["queue_path"])
        server = self.clock()
        if server is None or abs(server - self.env.now()) > CLOCK_SKEW_LIMIT_S:
            rs = [law.reason("CLOCK_SKEW", f"server {server}, host {self.env.now():.0f}", span=sid)]
            self.page("HALT", rs, {"plan_id": plan_id})
            return self.write_status("HALTED", {"codes": ["CLOCK_SKEW"]})
        self.prereqs(sid, self.env.now(), passed=["CLOCK"])
        if self.env.now() > authority_read + LEASE_S:
            return self.wait(["LEASE_EXPIRED"], f"the authority read is {self.env.now() - authority_read:.0f} s old")
        notice_issue = view["doc"]["standing_notice"]["issue"]
        line = (f"{plan_id}: arming now ({iso(self.env.now())}), kit {kit['campaign_id']} {sha[:12]}, legs "
                f"{','.join(span['legs'])}, queue {view['doc']['queue_id']} at {view['tip_commit'][:12]}. "
                "Ed's veto: a directive issue starting STOP/NO/HALT/VETO stops the next arm.")
        if not self.notice(notice_issue, line):
            self.prereqs(sid, self.env.now(), blocking=["NOTICE"])
            return self.wait(["ISSUES_UNREADABLE"], f"the standing notice line on #{notice_issue} did not post")
        self.prereqs(sid, self.env.now(), passed=["NOTICE"])
        # 5. the network phase ends here; nothing below may reach the network until the close
        self.network_open = False
        now = self.env.now()
        network_end = max([n["epoch"] for n in self.network_log] or [now])
        if now > authority_read + LEASE_S:
            return self.wait(["LEASE_EXPIRED"], f"the authority read is {now - authority_read:.0f} s old after the "
                                                "notice post")
        leases = {"authority_read": authority_read + LEASE_S,
                  "queue_expiry": law.queue_expiry(view["doc"], view["first_commit_epoch"]),
                  "watcher": law.watcher_lease(audit2["watcher"])}
        if cand["cls"]["dated"]:
            leases["date"] = law.date_end(span["not_before"]) - law.MIDNIGHT_MARGIN_S
        lease = min(leases.values())
        last = law.last_close(snap2["runs"])
        intent = {
            "schema": RECORD_SCHEMA, "plan_id": plan_id, "span": span, "queue": {
                "path": cand["queue_path"], "queue_id": view["doc"]["queue_id"], "sha256": view["digest"],
                "commit": view["tip_commit"], "first_commit": view["first_commit"],
                "audit_tip": audit2["tip"], "role": cand["role"]},
            "standing_sha256": law.digest(standing), "kit": {"sha256": sha, "campaign_id": kit["campaign_id"],
                                                           "frozen_commit": kit["frozen"]["commit"],
                                                           "source": entry["source"], "path": paths["kit"],
                                                           "queue_path": span["kit"]["path"]},
            "class": cand["cls"], "fallback": decision.action == "arm-fallback",
            "gates_expected": law.derived_gates(kit, span["legs"]),
            "repo": paths["repo"], "output": str(out), "batch_window": info["batch_window"],
            "expected_windows": info["expected_windows"], "plan_sha256": law.digest(info["plan"]),
            "worst_case_s": info["worst_case_s"], "network_end_epoch": network_end, "arm_proof": proof,
            "arm_proof_sha256": proof_digest(proof),
            "watcher": {"commit": audit2["watcher_sha"], "observed_live_at": audit2["watcher"]["observed_live_at"]},
            "notice": {"issue": notice_issue, "line": line}, "copy_marker": extra2.get("markers"),
            "server_time": server, "leases": leases, "lease_until": lease,
            "predecessor": None if last is None else {
                "plan_id": last.plan_id, "closed": last.closed, "status": last.status, "source": last.source,
                **({k: (read_json(self.span_dir(last.plan_id) / "close.json") or {}).get(k)
                    for k in ("close_proof_sha256", "manifest_sha256")} if last.source == "controller" else {})},
            "gates": d2.gates, "decided_epoch": now}
        try:
            exclusive_json(self.span_dir(plan_id) / "intent.json", intent)
        except FileExistsError:
            self.page("HALT", [law.reason("ARM_INDETERMINATE", f"{plan_id}: intent already exists", span=sid)])
            return self.write_status("HALTED", {"plan_id": plan_id})
        self.transition(plan_id, "arm_intent", {"queue_sha256": view["digest"], "plan_sha256": intent["plan_sha256"],
                                                "arm_proof_sha256": intent["arm_proof_sha256"],
                                                "network_end_epoch": network_end, "lease_until": lease})
        self.critical_path_event(sid, ready_all=now, plan_id=plan_id)
        request = {"repo": paths["repo"], "python": self.cfg["measurement_python"], "kit": paths["kit"],
                   "legs": ",".join(span["legs"]), "batch_window": info["batch_window"], "output": str(out),
                   "custody_root": str(self.custody), "lease_until": lease,
                   "standing_purpose": self.standing_purpose(), "controller_pid": self.pid}
        result = self.launcher.launch(request)
        return self.record_launch(plan_id, intent, result, kit)

    def _prepare_failed(self, plan_id, sid, stage, problem):
        self.prereqs(sid, self.env.now(), blocking=[stage], stage_failed=f"{stage}: {problem}"[:300])
        self.page("HALT", [law.reason("PREPARE_FAILED", f"{plan_id}: {problem}"[:400], span=sid)])
        return self.write_status("HALTED", {"plan_id": plan_id, "problem": problem})

    def _arm_record(self, plan_id, intent, status, **extra):
        return {"schema": RECORD_SCHEMA, "plan_id": plan_id, "status": status,
                "kind": "f2" if intent["fallback"] else "campaign", "phase": intent["class"]["phase"],
                "block_id": intent["span"]["block_id"], "legs": intent["span"]["legs"], "mixed": intent["class"]["mixed"],
                "kit_sha256": intent["kit"]["sha256"], "t0_epoch": intent["decided_epoch"], "output": intent["output"],
                "arm_proof_sha256": intent["arm_proof_sha256"], "queue_sha256": intent["queue"]["sha256"],
                "plan_sha256": intent["plan_sha256"], **extra}

    def record_launch(self, plan_id, intent, result, kit):
        launched = result.get("launch") or {}
        try:
            current = fence.read_fence(self.custody)
        except (OSError, ValueError):
            current = None
        problems = []
        if result.get("refused"):
            problems.append(f"arm child refused: {result['refused']}")
        if result.get("rc") != 0 or launched.get("next") != "exit the magistrate session now":
            problems.append(f"launch rc {result.get('rc')}: {result.get('stderr', '')[-300:]}")
        claimed = launched.get("fence") or {}
        fence_held = bool(current and claimed.get("purpose") and current.get("purpose") == claimed.get("purpose")
                          and current.get("pid") != result.get("arm_child_pid")
                          and self.env.pid_alive(current.get("pid", 0)))
        if not fence_held:
            problems.append(f"fence not claimed by the LaunchAgent: {current}")
        windows = (launched.get("plan") or {}).get("batch_windows")
        if windows is not None and windows != intent["expected_windows"]:
            problems.append(f"plan batch_windows {windows} != {intent['expected_windows']}")
        t0 = result.get("t0") or intent["decided_epoch"]
        if intent["class"]["dated"] and law.local_date(t0) != intent["span"]["not_before"]:
            problems.append(f"the launch t0 {iso(t0)} is not on the span's date {intent['span']['not_before']}")
        # It launched if the LaunchAgent holds the fence: monitor and close it, and halt after its close.
        status = "LIVE" if fence_held else "LAUNCH_REFUSED"
        arm = self._arm_record(plan_id, intent, status, launch_epoch=self.env.now(), deadline=result.get("deadline"),
                               fence_purpose=claimed.get("purpose"),
                               arm_command={"rc": result.get("rc"), "launch": launched,
                                            "arm_child_pid": result.get("arm_child_pid"), "t0": t0,
                                            "deadline": result.get("deadline"), "fence_after": current,
                                            "problems": problems})
        arm["t0_epoch"] = t0
        if problems:
            arm["launch_problems"] = problems
        arm["arm_command_sha256"] = law.digest(arm["arm_command"])
        atomic_json(self.span_dir(plan_id) / "arm.json", arm)
        self.transition(plan_id, "armed" if status == "LIVE" else "launch_refused",
                        {"queue_sha256": arm["queue_sha256"], "plan_sha256": arm["plan_sha256"],
                         "arm_proof_sha256": arm["arm_proof_sha256"], "arm_command_sha256": arm["arm_command_sha256"],
                         "decision": status, "t0": t0})
        self.critical_path_event(intent["span"]["span_id"], start=t0, plan_id=plan_id,
                                 refusal="; ".join(problems) or None)
        if problems:
            self.page("HALT", [law.reason("LAUNCH_REFUSED", "; ".join(problems)[:400], span=intent["span"]["span_id"])])
            if status != "LIVE":
                return self.write_status("HALTED", {"plan_id": plan_id})
        return self.write_status("LIVE", {"plan_id": plan_id, "deadline": arm["deadline"]})

    def adopt_or_halt(self, intent):
        """After a restart: an intent with no arm record. The runner creates the output at its start, so an output
        means the launch happened: adopt it as live (Mythos F21: a fence alone is not proof it is ours). A launch
        fence with no output yet is waited for. Neither: the outcome is unknown; halt, never relaunch."""
        plan_id = intent["plan_id"]
        try:
            cur = fence.read_fence(self.custody)
        except (OSError, ValueError):
            cur = None
        launch_fence = cur if cur is not None and cur["purpose"].startswith("align-r0:") else None
        if not Path(intent["output"]).exists() and launch_fence is not None and self.env.pid_alive(launch_fence["pid"]):
            return self.write_status("WAIT", {"codes": ["SPAN_LIVE"], "detail": f"{plan_id}: a launch fence and no "
                                                                               "output yet; not adopted"}, sync=False)
        adopted = Path(intent["output"]).exists()
        arm = self._arm_record(plan_id, intent, "LIVE" if adopted else "INDETERMINATE", launch_epoch=None,
                               deadline=None, fence_purpose=None if launch_fence is None else launch_fence["purpose"],
                               arm_command={"adopted_after_restart": True, "fence_after": cur})
        arm["arm_command_sha256"] = law.digest(arm["arm_command"])
        atomic_json(self.span_dir(plan_id) / "arm.json", arm)
        self.transition(plan_id, "adopted" if adopted else "indeterminate",
                        {"decision": arm["status"], "fence": cur, "output_exists": adopted})
        if not adopted:
            self.page("HALT", [law.reason("ARM_INDETERMINATE", plan_id, span=intent["span"]["span_id"])])
            return self.write_status("HALTED", {"plan_id": plan_id})
        return self.write_status("LIVE", {"plan_id": plan_id, "adopted": True})

    # -- live and close ------------------------------------------------------------------------------
    def monitor(self, rec):
        """A live span. While a launch fence is held by a live PID: stat only, nothing else (Sol 3). When it is
        gone: take the standing fence at once (Mythos F14), prove the runner's processes absent, then close."""
        self.network_open = False
        now = self.env.now()
        try:
            cur = fence.read_fence(self.custody)
        except (OSError, ValueError):
            cur = {"purpose": "align-r0:unreadable", "pid": self.pid, "deadline": now + 60}
        ours = rec.get("fence_purpose")
        if (cur is not None and cur["purpose"].startswith("align-r0:") and ours is not None and cur["purpose"] != ours
                and self.env.pid_alive(cur["pid"])):
            # Mythos N9: our span's fence is gone and another run holds the host. No close, no command, no network
            # while it lives; its own close is recorded (unproven) when it goes.
            if not read_json(self.state / "foreign.json"):
                atomic_json(self.state / "foreign.json", {"purpose": cur["purpose"], "first_seen": now}, sync=False)
            return self.write_status("CLOSING", {"plan_id": rec["plan_id"], "waiting": f"another run: {cur['purpose']}"},
                                     sync=False)
        if (cur is not None and cur["purpose"].startswith("align-r0:") and (ours is None or cur["purpose"] == ours)
                and self.env.pid_alive(cur["pid"])):
            deadline = rec.get("deadline") or cur.get("deadline")
            if deadline and now > deadline + STRANDED_GRACE_S:
                # An alarm, never a close: the PID still holds the fence. A page file only; no network, no command.
                self.page("HALT", [law.reason("STRANDED_ALARM", f"{rec['plan_id']} past its deadline")],
                          {"plan_id": rec["plan_id"]})
            return self.write_status("LIVE", {"plan_id": rec["plan_id"]}, sync=False)
        if read_json(self.state / "foreign.json"):
            self.record_external(read_json(self.state / "foreign.json")["purpose"], "other",
                                 read_json(self.state / "foreign.json")["first_seen"], now)
            (self.state / "foreign.json").unlink()
        self.hold_fence()
        span_dir = self.span_dir(rec["plan_id"])
        gone = read_json(span_dir / "fence-gone.json")
        if gone is None:
            gone = {"epoch": now}
            atomic_json(span_dir / "fence-gone.json", gone)
        procs = _pgrep(self.env, SPAN_PROCESSES)
        receipt = Path(rec["output"]) / RECEIPT
        if procs["ok"] is not True:
            if now - gone["epoch"] > STRANDED_GRACE_S:
                self.page("HALT", [law.reason("STRANDED_ALARM", f"{rec['plan_id']}: runner processes after the fence "
                                                                f"({str(procs['detail'])[:100]})")],
                          {"plan_id": rec["plan_id"]})
            return self.write_status("CLOSING", {"plan_id": rec["plan_id"], "waiting": "process absence"})
        if receipt.is_file():
            return self.close(rec)
        if now - gone["epoch"] > RECEIPT_GRACE_S:
            return self.close(rec, stranded="fence gone, processes absent, no receipt")
        return self.write_status("CLOSING", {"plan_id": rec["plan_id"], "waiting": "receipt"})

    def close(self, rec, stranded=None):
        plan_id = rec["plan_id"]
        self.hold_fence()
        intent = read_json(self.span_dir(plan_id) / "intent.json")
        out = Path(rec["output"])
        span, sha = intent["span"], intent["kit"]["sha256"]
        kit = json.loads(Path(intent["kit"]["path"]).read_text())
        sid = span["span_id"]
        reasons, receipt, summaries, meter, result, manifest_sha = [], {}, {}, {}, None, None
        publish = self.span_dir(plan_id) / "publish"
        if publish.exists():
            shutil.rmtree(publish)
        bundle = publish / "bundle"
        if stranded or not (out / RECEIPT).is_file():
            reasons.append(law.reason("RECEIPT_MISSING", stranded or "no receipt", span=sid))
        elif self.unsafe_inputs(out):
            # Sol R1: a symlinked output, desk-bundle root or receipt is refused before anything is read.
            reasons.append(law.reason("BUNDLE_REFUSED", f"{self.unsafe_inputs(out)}"[:300], span=sid))
        else:
            try:
                manifest_sha = desk_final.pack_bundle(
                    out, bundle, plan_id=plan_id, queue_id=intent["queue"]["queue_id"], span_id=sid,
                    attempt=span["attempt"], kit={"path": intent["kit"]["queue_path"], "sha256": sha,
                                                  "campaign_id": kit["campaign_id"],
                                                  "frozen_commit": kit["frozen"]["commit"]},
                    roster=list(span["legs"]),
                    producer={"controller": "cadence_controller", "token": self.token, "closed_at": iso(self.env.now())})
            except (deskmod.DeskRefusal, OSError) as exc:
                # Includes desk_final.DeniedContent (Mythos N1, Sol R1): pack_bundle runs the desk's own deny scan
                # (desk_final.refuse_denied_content) on every file it writes, so a denied key is never packed.
                reasons.append(law.reason("BUNDLE_REFUSED", f"{exc}"[:300], span=sid))
                if publish.exists():
                    shutil.rmtree(publish)   # Sol 2: a rejected input is never shipped
        if manifest_sha is not None:   # one set of bytes: parsed, hashed and pushed from the packed bundle
            receipt = json.loads((bundle / RECEIPT).read_bytes())
            try:
                for row in receipt.get("legs") or []:
                    f = bundle / "legs" / row["leg_id"] / "leg_summary.json"
                    if f.is_file():
                        summaries[row["leg_id"]] = deskmod._project(deskmod._json(f, "leg-summary-v1"),
                                                                    deskmod.LEG_SUMMARY_KEYS,
                                                                    f"legs/{row['leg_id']}", True)
                meter, result = deskmod._span_extras(bundle, "leg-summary-v1")
            except (deskmod.DeskRefusal, ValueError, OSError) as exc:
                reasons.append(law.reason("ROSTER_MISMATCH", f"desk bundle: {exc}"[:300], span=sid))
            plan = (json.loads((bundle / desk_final.PLAN_NAME).read_bytes())
                    if (bundle / desk_final.PLAN_NAME).is_file() else None)
            reasons += law.receipt_command_reasons(receipt, intent["expected_windows"])
            reasons += law.desk_input_reasons(span=span, kit_sha=sha, kit=kit, receipt=receipt, summaries=summaries,
                                              plan=plan)
            summary = {"result": result, "meter": meter, "feeds_proven_stopped": bool(meter.get("proven_stopped")),
                       "legs": list(summaries.values())}
            reasons += [law.reason("NAMED_STOP", f"{s['code']}: {s['detail']}"[:300], span=sid)
                        for s in stopsmod.evaluate_named_stops(kit["stop_rules"], summary)]
        proof = self.proof("close", (self.standing_purpose(),))
        reasons += law.proof_reasons(proof["lines"], "close")
        maintenance = self.maintenance_line(out, rec)
        codes = {r["code"] for r in reasons}
        status = ("CLOSED_OK" if not reasons else "STRANDED" if "RECEIPT_MISSING" in codes
                  else "REFUSED" if "RECEIPT_NOT_CLEAN" in codes else "CLOSE_UNPROVEN" if "CLOSE_UNPROVEN" in codes
                  else "STOPPED")
        gates = law.derived_gates(kit, span["legs"]) if receipt else []
        runner_t0 = (receipt.get("started") or {}).get("epoch_s") if receipt else None
        receipt_epoch = math.ceil(os.stat(out / RECEIPT).st_mtime) if (out / RECEIPT).is_file() else None
        transition = {
            "schema": law.TRANSITION_SCHEMA, "plan_id": plan_id, "queue_id": intent["queue"]["queue_id"],
            "span_id": sid, "attempt": span["attempt"],
            "queue": {"path": intent["queue"]["path"], "sha256": intent["queue"]["sha256"],
                      "commit": intent["queue"]["commit"]},
            "kit": {"path": intent["kit"]["queue_path"], "sha256": sha},
            "plan_sha256": (sha256_file(bundle / desk_final.PLAN_NAME) if manifest_sha is not None
                            and (bundle / desk_final.PLAN_NAME).is_file() else None),
            "armed_plan_sha256": intent["plan_sha256"],
            "arm_proof_sha256": intent["arm_proof_sha256"], "arm_command_sha256": rec.get("arm_command_sha256"),
            "close_proof_sha256": proof_digest(proof), "status": status, "manifest_sha256": manifest_sha,
            "t0_epoch": runner_t0 or rec["t0_epoch"], "receipt_epoch": receipt_epoch, "gates": gates,
            "soak_attempts": [{k: a.get(k) for k in ("attempt", "refused", "output_dir")}
                              for a in receipt.get("soak_attempts") or []],
            "codes": sorted(codes)}
        close = {"schema": RECORD_SCHEMA, "plan_id": plan_id, "status": status, "closed_epoch": None,
                 "close_proof": proof, "close_proof_sha256": transition["close_proof_sha256"], "reasons": reasons,
                 "transition": transition, "manifest_sha256": manifest_sha, "gates": gates, "pushed": False,
                 "legs_finished": receipt.get("legs_finished") if receipt else 0, "runner_t0": runner_t0,
                 "receipt_epoch": receipt_epoch, "maintenance_line": maintenance}
        atomic_json(self.span_dir(plan_id) / "close.json", close)
        self.transition(plan_id, "closed", {"decision": status, "close_proof_sha256": transition["close_proof_sha256"],
                                            "codes": sorted(codes), "queue_sha256": intent["queue"]["sha256"],
                                            "manifest_sha256": manifest_sha})
        self.critical_path_event(sid, end=receipt_epoch, refusal=None if status == "CLOSED_OK" else status)
        self.network_open = True
        self.push_close(plan_id)
        close = read_json(self.span_dir(plan_id) / "close.json")   # sign-time deny refusal rewrites the status
        status, reasons = close["status"], close["reasons"]
        launch_problems = (read_json(self.span_dir(plan_id) / "arm.json") or {}).get("launch_problems")
        if status != "CLOSED_OK" or launch_problems:
            self.page("HALT", reasons or [law.reason("LAUNCH_REFUSED", "; ".join(launch_problems or [status]))],
                      {"plan_id": plan_id})
            return self.write_status("HALTED", {"plan_id": plan_id, "status": status})
        return self.write_status("CLOSED", {"plan_id": plan_id})

    @staticmethod
    def unsafe_inputs(out):
        """Symlinks among the span's output root, its desk-bundle root and its receipt (Sol R1: the packer refuses
        leaf symlinks, not an ancestor)."""
        bad = []
        for path in (out, out / "desk-bundle", out / RECEIPT, out / desk_final.PLAN_NAME):
            if os.path.islink(path):
                bad.append(str(path))
        try:
            if (out / "desk-bundle").exists() and os.path.realpath(out / "desk-bundle") != os.path.join(
                    os.path.realpath(out), "desk-bundle"):
                bad.append(f"{out}/desk-bundle resolves elsewhere")
        except OSError as exc:
            bad.append(str(exc))
        return bad

    def maintenance_line(self, out, rec):
        """RL-171 section 5 item 1 (item 331's maintenance line): one read-only system-log query over the span,
        saved beside the journals as ``maintenance-log.txt``. Print only: it gates nothing and is not a stop."""
        if not out.is_dir() or not (out / RECEIPT).is_file():
            return {"rc": None, "detail": "no span output"}
        start = datetime.fromtimestamp(rec["t0_epoch"], law.ZONE).strftime("%Y-%m-%d %H:%M:%S")
        end = datetime.fromtimestamp(os.stat(out / RECEIPT).st_mtime, law.ZONE).strftime("%Y-%m-%d %H:%M:%S")
        names = ",".join(f'"{n}"' for n in self.MAINTENANCE)
        res = self.env.run(["/usr/bin/sudo", "-n", "/usr/bin/log", "show", "--style", "compact", "--start", start,
                            "--end", end, "--predicate", f"process IN {{{names}}}"], timeout=600)
        try:
            (out / "maintenance-log.txt").write_text(res.stdout)
        except OSError as exc:
            return {"rc": res.rc, "detail": f"not saved: {exc}"}
        return {"rc": res.rc, "lines": len(res.stdout.splitlines()), "window": [start, end]}

    def push_close(self, plan_id):
        """FORMAT.md section 1: the packed ``bundle/`` and ``transition.json`` (the per-span record carrying the anchor)
        as one SSH-signed parentless commit by ``cadence-controller`` (``desk_transport.sign_bundle``, which refuses
        any file outside the layout unread), pushed once to ``refs/heads/desk-bundles/<plan_id>``. A span whose
        files the packer refused, or that left no receipt, publishes nothing: its halt pages the lead."""
        close = read_json(self.span_dir(plan_id) / "close.json")
        if close["manifest_sha256"] is None:
            close.update(pushed=None, closed_epoch=math.ceil(self.env.now()), publish="nothing (no bundle)")
            atomic_json(self.span_dir(plan_id) / "close.json", close)
            return False
        bundle = self.span_dir(plan_id) / "publish" / "bundle"
        try:
            sha, anchor = desk_transport.sign_bundle(self.git.dir, bundle, close["transition"], plan_id=plan_id,
                                                     signing_key=self.cfg["signing_key"])
        except desk_final.DeniedContent as exc:
            # sign_bundle runs the desk's deny scan on every file it signs, transition.json included. A hit is not a
            # retry: nothing is signed or shipped, the span closes STOPPED and the lead is paged.
            shutil.rmtree(bundle.parent, ignore_errors=True)
            close.update(status="STOPPED", manifest_sha256=None, pushed=None, closed_epoch=math.ceil(self.env.now()),
                         publish="nothing (denied content)",
                         reasons=close["reasons"] + [law.reason("BUNDLE_REFUSED", f"sign: {exc}"[:300], span=close["transition"]["span_id"])])
            atomic_json(self.span_dir(plan_id) / "close.json", close)
            self.transition(plan_id, "bundle_refused", {"problem": f"sign: {exc}"[:300]})
            return False
        except (desk_transport.TransportRefusal, OSError) as exc:
            self.transition(plan_id, "push_failed", {"problem": f"sign: {exc}"[:300]})
            return False
        if anchor != close["manifest_sha256"]:
            self.transition(plan_id, "push_failed", {"problem": "the packed manifest changed since the close"})
            return False
        ref = f"{self.cfg['bundle_ref_prefix']}{plan_id}"
        try:
            pushed, problem = self.git.push_commit(sha, ref)
        except NetworkClosed as exc:
            pushed, problem = None, str(exc)
        if problem:
            self.transition(plan_id, "push_failed", {"problem": problem[:300]})
            return False
        close.update(pushed=True, bundle_commit=pushed, bundle_ref=ref, closed_epoch=math.ceil(self.env.now()))
        atomic_json(self.span_dir(plan_id) / "close.json", close)
        self.transition(plan_id, "bundle_pushed", {"manifest_sha256": anchor, "commit": pushed, "ref": ref})
        return True


# --------------------------------------------------------------------------
# The loop and the small commands
# --------------------------------------------------------------------------
@contextlib.contextmanager
def single_instance(state_dir):
    Path(state_dir).mkdir(parents=True, exist_ok=True)
    fd = os.open(Path(state_dir) / "controller.lock", os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(fd)
        raise SystemExit("another controller holds controller.lock")
    try:
        yield
    finally:
        os.close(fd)


def run_loop(ctl, *, max_ticks=None):
    ticks, status = 0, None
    while max_ticks is None or ticks < max_ticks:
        ticks += 1
        live = (status or {}).get("state") in ("LIVE", "CLOSING")
        # Sol R7: while a span is live the kqueue is registered BEFORE the tick looks at the fence, so a fence removed
        # after that look still wakes the loop at once (no lost edge, no 60 s wait).
        watch = ctl.env.watch(ctl.custody) if live else None
        try:
            status = ctl.tick()
        except Exception as exc:  # noqa: BLE001 - a crash in one tick is a halt with a page, never a silent loop
            ctl.network_open = False
            ctl.page("HALT", [law.reason("STATE_CORRUPT", f"{type(exc).__name__}: {exc}"[:400])])
            status = ctl.write_status("HALTED", {"exception": f"{type(exc).__name__}: {exc}"[:400]})
        try:
            if status.get("state") in ("LIVE", "CLOSING"):
                if watch is None:
                    watch = ctl.env.watch(ctl.custody)
                    status = ctl.tick()       # the first live tick: look again after registering
                if status.get("state") in ("LIVE", "CLOSING"):
                    watch.wait(ctl.cfg["poll_live_s"])
            elif (status.get("detail") or {}).get("quiet") or (status.get("detail") or {}).get("silent"):
                ctl.env.sleep(max(ctl.cfg["poll_idle_s"], 300))   # a v4 window: one look every five minutes (N15)
            else:
                ctl.env.sleep(ctl.cfg["poll_idle_s"])
        finally:
            if watch is not None:
                watch.close()


def cmd_ack(cfg, args):
    path = Path(cfg["state_dir"]) / "pages" / f"{args.page_id}.json"
    if not path.is_file():
        print(f"REFUSE no page {args.page_id}")
        return 1
    exclusive_json(Path(cfg["state_dir"]) / "acks" / f"{args.page_id}.json",
                   {"page_id": args.page_id, "by": args.by, "note": args.note, "epoch": time.time(), "at": iso(time.time())})
    print(json.dumps({"acked": args.page_id}))
    return 0


def cmd_note_run(cfg, args):
    if args.restore_ok == "yes" and not args.evidence.strip():
        print("REFUSE --restore-ok yes needs --evidence (the run's Check record)")
        return 1
    row = {"run_id": args.run_id, "kind": args.kind, "t0_epoch": args.t0, "closed_epoch": args.closed,
           "restore": "proven" if args.restore_ok == "yes" else "unproven", "evidence": args.evidence,
           "noted": time.time()}
    append_jsonl(Path(cfg["state_dir"]) / "external.jsonl", row)
    print(json.dumps(row))
    return 0


def cmd_accept_audit_tip(cfg, args):
    """After a reviewed rewrite of the audit branch: accept its current fetched tip (and forget the queue memory)."""
    git = Git(cfg, Env(), lambda what: None)
    if not git.fetch_audit() or git.tip() is None:
        print("REFUSE could not fetch the audit branch")
        return 1
    state = Path(cfg["state_dir"])
    atomic_json(state / "audit-tip.json", {"tip": git.tip(), "accepted_by": args.by, "note": args.note})
    atomic_json(state / "queues-seen.json", {})
    print(json.dumps({"accepted": git.tip()}))
    return 0


def cmd_check_heartbeat(cfg, args):
    hb = read_json(Path(cfg["state_dir"]) / "heartbeat.json")
    age = None if hb is None else time.time() - hb["epoch"]
    print(json.dumps({"heartbeat": hb, "age_s": age}))
    return 0 if age is not None and age <= args.max_age else 1


def cmd_ledger(cfg, _args):
    base = Path(cfg["state_dir"]) / "critical-path"
    writer = csv.writer(sys.stdout)
    writer.writerow(["span_id", "plan_id", "first_considered", "prerequisite", "first_blocked", "ready_at",
                     "ready_all", "start", "end", "refusal"])

    def t(v):
        return iso(v) if isinstance(v, (int, float)) else ""
    for path in sorted(base.glob("*.json")) if base.is_dir() else []:
        doc = read_json(path)
        for code, row in sorted(doc.get("prereqs", {}).items()) or [("-", {})]:
            writer.writerow([doc["span_id"], doc.get("plan_id"), t(doc.get("first_considered")), code,
                             t(row.get("first_blocked")), t(row.get("ready_at")), t(doc.get("ready_all")),
                             t(doc.get("start")), t(doc.get("end")), doc.get("refusal") or ""])
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("loop", "tick", "status", "ledger"):
        sub.add_parser(name).add_argument("--config", required=True)
    s = sub.add_parser("ack"); s.add_argument("page_id"); s.add_argument("--config", required=True)
    s.add_argument("--by", required=True); s.add_argument("--note", required=True)
    s = sub.add_parser("accept-audit-tip"); s.add_argument("--config", required=True)
    s.add_argument("--by", required=True); s.add_argument("--note", required=True)
    s = sub.add_parser("note-run"); s.add_argument("--config", required=True)
    s.add_argument("--kind", choices=("F0", "v4", "partc", "other"), required=True); s.add_argument("--run-id", required=True)
    s.add_argument("--t0", type=float, required=True); s.add_argument("--closed", type=float, required=True)
    s.add_argument("--restore-ok", choices=("yes", "no"), required=True); s.add_argument("--evidence", default="")
    s = sub.add_parser("check-heartbeat"); s.add_argument("--config", required=True)
    s.add_argument("--max-age", type=float, default=300)
    s = sub.add_parser("synthetic"); s.add_argument("--workdir", required=True)
    args = p.parse_args(argv)
    if args.cmd == "synthetic":
        from scripts import cadence_controller_synthetic as synth
        return synth.main(Path(args.workdir))
    try:
        cfg = load_config(args.config)
    except (ConfigError, OSError, ValueError) as exc:
        print(f"REFUSE config: {exc}")
        return 2
    if args.cmd == "status":
        print(json.dumps(read_json(Path(cfg["state_dir"]) / "STATUS.json"), indent=1, sort_keys=True))
        return 0
    commands = {"ack": cmd_ack, "note-run": cmd_note_run, "check-heartbeat": cmd_check_heartbeat, "ledger": cmd_ledger,
                "accept-audit-tip": cmd_accept_audit_tip}
    if args.cmd in commands:
        return commands[args.cmd](cfg, args)
    with single_instance(cfg["state_dir"]):
        ctl = Controller(cfg)
        if args.cmd == "tick":
            print(json.dumps(ctl.tick(), indent=1, sort_keys=True, default=str))
            return 0
        try:
            run_loop(ctl)
        finally:
            ctl.release_fence()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
