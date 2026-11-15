#!/usr/bin/env python3
"""The standing-queue controller (RL-172 section (g); RL-149 section 2.8). A script, never a model.

    python3.13 -B scripts/cadence_controller.py loop   --config controller.json
    python3.13 -B scripts/cadence_controller.py tick   --config controller.json
    python3.13 -B scripts/cadence_controller.py status --config controller.json
    python3.13 -B scripts/cadence_controller.py ack PAGE_ID --config controller.json --by NAME --note TEXT
    python3.13 -B scripts/cadence_controller.py note-run --config controller.json --kind F0 --run-id ID \\
        --t0 EPOCH --closed EPOCH --restore-ok yes|no
    python3.13 -B scripts/cadence_controller.py check-heartbeat --config controller.json [--max-age 300]
    python3.13 -B scripts/cadence_controller.py ledger --config controller.json      (critical-path CSV)
    python3.13 -B scripts/cadence_controller.py synthetic --workdir DIR              (RL-172 (i) row 5)

It runs on the MBP under launchd as a KeepAlive loop (``configs/launchd/
com.joulewise.cadence-controller.plist.template``). Each tick derives every state from durable evidence,
so a crash or a restart repeats nothing:

1. **A span is live** (its launch fence is held): the controller only stats the fence and the receipt.
   No network, no subprocess, no git.
2. **The span exited** (fence gone, receipt present): the close. The typed close proof is the receipt's
   own restore and feed stops (command result), an independent host readback (pmset powermode and AC,
   network time, the kernel frequency word, the High Power marker, launchd labels, measurement_mode
   verify) and process-group absence (monitors, root powermetrics, runner and leg processes, the
   fence). The desk-final inputs of RL-172 (c) are checked against the queue entry; the bundle (manifest,
   receipt, plan, desk bundle) is committed with an SSH signature and pushed to
   ``refs/heads/cadence-desk/<plan_id>`` for the Air desk.
3. **Otherwise** it fetches the audit branch and the owner's open issues fresh, asks
   ``joulewise.cadence.standing.select`` what to do, and either arms, waits, cedes to a READY v4 session,
   or pages. Arming: prepare (kit copy by hash, a fresh detached worktree at the frozen commit,
   ``validate-kit --repo``, the pinned ``plan``), end all network work, take the arm proof (the same
   readback and absence lines plus no agent process), write the arm intent once (O_EXCL), then hand the
   launch to a short-lived arm child that clears the controller's standing fence and calls the frozen
   ``launch_cadence_span.py launch`` in-process with its own PID as the handoff PID. The launch result,
   the claimed fence and the plan's batch windows are the arm's command result.

**The magistrate wakes only on a page.** While the controller waits with nothing to report it holds a
desk fence of its own (``cadence-controller:<token>``, refreshed every tick, 15 min deadline), which the
magistrate watchdog already honours (``desk_fence_active``): no activation is launched. A page (a halt,
a refusal, an empty queue, a due F0, a stalled wait, a READY v4 session) releases that fence, so the
watchdog's next tick launches the magistrate, which reads ``STATUS.json`` and acknowledges with ``ack``.
If the controller dies, its fence's deadline passes and the watchdog removes it with a
``desk_fence_stale`` notice: the heartbeat alarm needs nothing new on the MBP.

Blinding: this script never opens an energy, power, meter-sample, powermetrics, transcript, slot or
custody file. It reads the runner's receipt, span plan and desk bundle (operational projections) and
hashes the soak reference without parsing it. Design: docs/process/cadence_queue_design.md section 15.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import hashlib
import io
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

from joulewise.cadence import desk as deskmod, kit as kitmod, kit_v11, queue as q, standing as law  # noqa: E402
from joulewise.cadence import stops as stopsmod  # noqa: E402
from scripts import launch_align_r0 as fence  # noqa: E402  (fence helpers only; nothing launches from here)

CONFIG_SCHEMA = "joulewise.cadence_controller_config.v1"
RECORD_SCHEMA = "joulewise.cadence_controller_record.v1"
STANDING_FENCE_PREFIX = "cadence-controller:"
STANDING_FENCE_S = 900
LAUNCH_GRACE_S = 120          # added to the plan's launch deadline for the seconds between plan and launch
RECEIPT_GRACE_S = 120         # fence gone, receipt not yet visible
STRANDED_GRACE_S = 600
CANONICAL_ROOT = "/Users/edr/code/JouleWise"
RECEIPT = "runner_receipt.json"
OUT_REFUSED = re.compile(r"/restricted/|/night-|/jw-b5-|/configs/campaigns/align_v4")
CONFIG_KEYS = {
    "schema", "state_dir", "git_dir", "audit_ref", "records_dir", "worktrees_root", "output_root", "kits_dir",
    "custody_root", "measurement_python", "receipt_roots", "signing_key", "bundle_ref_prefix", "owner_login",
    "repo_slug", "gh_argv", "measurement_mode_script", "high_power_marker", "poll_idle_s", "poll_live_s",
    "hold_standing_fence"}


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
                "measurement_python", "signing_key", "measurement_mode_script", "high_power_marker"):
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
    for key in ("poll_idle_s", "poll_live_s"):
        if not (isinstance(cfg.get(key), (int, float)) and 0 < cfg[key] <= 300):
            problems.append(f"{key}: seconds in (0, 300]")
    if not str(cfg.get("bundle_ref_prefix", "")).startswith("refs/"):
        problems.append("bundle_ref_prefix: refs/...")
    if type(cfg.get("hold_standing_fence")) is not bool:
        problems.append("hold_standing_fence: bool")
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


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    with open(tmp, "x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=1, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
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


# --------------------------------------------------------------------------
# Host proofs (RL-172 (g) 5): readback and process-group absence, each line typed
# --------------------------------------------------------------------------
NIGHT_LABEL = re.compile(r"\bcom\.joulewise\.(night|align-r0)")


def _pgrep(env, argv):
    """pgrep: rc 1 = none (ok), rc 0 = found (not ok), anything else = not observed."""
    res = env.run(argv, timeout=15)
    if res.rc == 1:
        return {"ok": True, "detail": "none", "argv": argv}
    if res.rc == 0:
        return {"ok": False, "detail": res.stdout.strip()[:300], "argv": argv}
    return {"ok": None, "detail": f"rc {res.rc}: {res.stderr.strip()[:200]}", "argv": argv}


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
    rows["span_processes"] = _pgrep(env, ["/usr/bin/pgrep", "-fl",
                                          r"cadence_legs_runner\.py|cadence_leg_runtime\.py|run_align_r0_launchagent"])
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


def proof_digest(proof):
    return law.digest(proof)


# --------------------------------------------------------------------------
# The audit branch: the standing index, queues, desk-final and session records, the watcher stamp
# --------------------------------------------------------------------------
class Git:
    """The controller's own clone (never the canonical root). Network calls go through ``guard``."""

    def __init__(self, cfg, env, guard):
        self.cfg, self.env, self.guard = cfg, env, guard
        self.dir = cfg["git_dir"]
        self.ref = f"refs/remotes/origin/{cfg['audit_ref']}"

    def git(self, *args, timeout=120, input_text=None, env=None):
        return self.env.run(["git", "-C", self.dir, *args], timeout=timeout, input_text=input_text, env=env)

    def fetch_audit(self):
        self.guard("git fetch audit")
        res = self.git("fetch", "--quiet", "--no-tags", "origin",
                       f"+refs/heads/{self.cfg['audit_ref']}:{self.ref}", timeout=300)
        return res.rc == 0

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

    def commit_epoch(self, path):
        res = self.git("log", "-1", "--format=%ct", self.ref, "--", path)
        return int(res.stdout.strip()) if res.rc == 0 and res.stdout.strip().isdigit() else None

    def history(self, path):
        res = self.git("log", "--reverse", "--format=%H", self.ref, "--", path)
        if res.rc != 0:
            return None
        out = []
        for sha in res.stdout.split():
            raw = self.show_bytes(sha, path)
            if raw is not None:
                out.append(raw)
        return out

    def list_dir(self, path):
        res = self.git("ls-tree", "--name-only", self.ref, path.rstrip("/") + "/")
        return [Path(x).name for x in res.stdout.split()] if res.rc == 0 else []

    def worktree_add(self, path, sha):
        return self.git("worktree", "add", "--detach", str(path), sha, timeout=300)

    def push_bundle(self, ref, files, message):
        """Commit ``files`` ({relative path: bytes}) as one signed commit with no parent and push it to ``ref``.
        Idempotent: an existing remote ref with the same tree is success; a different tree is a refusal."""
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(self.dir) / f".git-cadence-index-{uuid.uuid4().hex}"),
               "LC_ALL": "C"}
        try:
            for rel, raw in sorted(files.items()):
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    tmp.write(raw)
                blob = self.git("hash-object", "-w", tmp.name, env=env)
                os.unlink(tmp.name)
                if blob.rc != 0:
                    return None, f"hash-object: {blob.stderr.strip()}"
                upd = self.git("update-index", "--add", "--cacheinfo", f"100644,{blob.stdout.strip()},{rel}", env=env)
                if upd.rc != 0:
                    return None, f"update-index: {upd.stderr.strip()}"
            tree = self.git("write-tree", env=env)
            if tree.rc != 0:
                return None, f"write-tree: {tree.stderr.strip()}"
            tree = tree.stdout.strip()
        finally:
            with contextlib.suppress(FileNotFoundError):
                os.unlink(env["GIT_INDEX_FILE"])
        stamp = "2000000000 +0000"
        commit = self.env.run(["git", "-C", self.dir, "-c", "gpg.format=ssh", "-c",
                               f"user.signingkey={self.cfg['signing_key']}", "commit-tree", "-S", tree],
                              timeout=60, input_text=message + "\n",
                              env={**os.environ, "GIT_AUTHOR_NAME": "cadence-controller",
                                   "GIT_AUTHOR_EMAIL": "cadence-controller@localhost", "GIT_AUTHOR_DATE": stamp,
                                   "GIT_COMMITTER_NAME": "cadence-controller",
                                   "GIT_COMMITTER_EMAIL": "cadence-controller@localhost",
                                   "GIT_COMMITTER_DATE": stamp})
        if commit.rc != 0:
            return None, f"commit-tree -S: {commit.stderr.strip()[:200]}"
        sha = commit.stdout.strip()
        self.guard(f"git push {ref}")
        remote = self.git("ls-remote", "origin", ref, timeout=120)
        if remote.rc == 0 and remote.stdout.strip():
            have = remote.stdout.split()[0]
            self.git("fetch", "--quiet", "origin", have, timeout=120)
            have_tree = self.git("rev-parse", f"{have}^{{tree}}")
            if have_tree.rc == 0 and have_tree.stdout.strip() == tree:
                return have, None
            return None, f"{ref} exists with another tree"
        push = self.git("push", "--quiet", "origin", f"{sha}:{ref}", timeout=300)
        return (sha, None) if push.rc == 0 else (None, f"push: {push.stderr.strip()[:200]}")


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
        kit, got = kitmod.load_kit(path, **kwargs)
    return kit


def read_audit(cfg, git, now):
    """Everything the decision needs from the audit branch, read fresh. Returns (inputs, reasons)."""
    reasons = []
    rd = cfg["records_dir"].rstrip("/")
    out = {"standing": None, "queues": [], "fallback_queues": [], "desk_finals": {}, "ready": [], "done": set(),
           "watcher": None, "watcher_commit": None, "kit_bytes": {}}
    if not git.fetch_audit():
        return out, [law.reason("FETCH_FAILED")]
    raw = git.show_bytes(git.ref, f"{rd}/STANDING.json")
    if raw is None:
        return out, [law.reason("STANDING_MISSING")]
    try:
        standing = law.validate_standing(json.loads(raw))
    except (ValueError, law.StandingError) as error:
        return out, [law.reason("STANDING_INVALID", "; ".join(getattr(error, "problems", [str(error)]))[:400])]
    out["standing"] = standing
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
    f2 = [{**x, "fallback": True} for f in standing["fallback"] if f["kind"] == "F2" for x in f["queues"]]
    for entry in [*standing["queues"], *f2]:
        view = read_queue(git, entry, kits, standing)
        (out["fallback_queues"] if entry.get("fallback") else out["queues"]).append(view)
    for name in git.list_dir(f"{rd}/desk-final"):
        rec = git.show_bytes(git.ref, f"{rd}/desk-final/{name}")
        try:
            doc = json.loads(rec)
            out["desk_finals"][doc["plan_id"]] = doc
        except (TypeError, ValueError, KeyError):
            reasons.append(law.reason("DESK_FINAL_INVALID", name))
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
    out["watcher_commit"] = git.commit_epoch(f"{rd}/watcher-stamp.json") if stamp is not None else None
    return out, reasons


def read_queue(git, entry, kits, standing):
    path = entry["path"]
    view = {"path": path, "role": entry["role"], "fallback": bool(entry.get("fallback")), "doc": None,
            "commit_epoch": None, "kits": {}, "reasons": [], "closed_ids": set(), "withdrawn_ids": set(standing["withdrawn"]),
            "digest": None}
    raw = git.show_bytes(git.ref, path)
    if raw is None:
        view["reasons"].append(law.reason("QUEUE_MISSING", path))
        view["doc"] = {"queue_id": path, "spans": [], "expires_at": "1970-01-01T00:00:00+00:00", "halt": None}
        view["commit_epoch"] = 0
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
            for kpath, (kit, sha) in span_kits.items():
                dest = Path(tmp) / kpath
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(json.dumps(kit))
            problems = cq.qual_roster_problems(doc, tmp)
        if problems:
            raise q.QueueError(problems)
        view["doc"] = doc
    except (ValueError, q.QueueError, kitmod.KitError) as error:
        view["reasons"].append(law.reason("QUEUE_INVALID", f"{path}: {'; '.join(getattr(error, 'problems', [str(error)]))}"[:400]))
        view["doc"] = {"queue_id": path, "spans": [], "expires_at": "1970-01-01T00:00:00+00:00", "halt": None}
        view["commit_epoch"] = 0
        return view
    view["commit_epoch"] = git.commit_epoch(path)
    if view["commit_epoch"] is None:
        view["reasons"].append(law.reason("QUEUE_MISSING", f"{path}: no commit time"))
        view["commit_epoch"] = 0
    history = git.history(path)
    if history is None:
        view["reasons"].append(law.reason("QUEUE_MISSING", f"{path}: history unreadable"))
    else:
        docs = []
        for blob in history:
            try:
                docs.append(json.loads(blob))
            except ValueError:
                docs.append(None)
        problems = law.append_only_problems(docs)
        if problems:
            view["reasons"].append(law.reason("QUEUE_NOT_APPEND_ONLY", "; ".join(problems)[:300]))
    view["kits"] = {sha: kits[sha] for _p, (_k, sha) in span_kits.items()}
    return view


def read_issues(cfg, env, guard):
    guard("gh issue list")
    res = env.run([*cfg["gh_argv"], "issue", "list", "--repo", cfg["repo_slug"], "--state", "open", "--author",
                   cfg["owner_login"], "--limit", "200", "--json", "number,title,body,author,labels,state"], timeout=120)
    if res.rc != 0:
        return None
    try:
        doc = json.loads(res.stdout)
    except ValueError:
        return None
    return doc if isinstance(doc, list) else None


def receipt_census(roots):
    """The newest ``runner_receipt.json`` at depth <= 4 under each root, mtime rounded up (item 331's census).
    A missing root, a lookup error or no receipt at all raises: missing evidence is never 0."""
    newest, count = None, 0

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
                m = os.stat(os.path.join(dirpath, RECEIPT)).st_mtime
                count += 1
                newest = m if newest is None or m > newest else newest
    if count == 0:
        raise FileNotFoundError("the receipt census found no runner_receipt.json")
    return math.ceil(newest)


# --------------------------------------------------------------------------
# Preparation and launch (production)
# --------------------------------------------------------------------------
ARM_CHILD = r'''
import json, os, sys
from pathlib import Path
req = json.loads(sys.argv[1])
sys.path.insert(0, req["repo"])
from scripts import launch_cadence_span as L
from scripts import launch_align_r0 as base
L.cadence_plan(Path(req["kit"]), req["legs"], req["batch_window"])     # warm: imports and the plan, before the fence moves
root = Path(req["custody_root"])
with base.fence_lock(root):
    cur = base.read_fence(root)
    if cur is not None:
        if cur["purpose"] != req["standing_purpose"] or cur["pid"] != req["controller_pid"]:
            print(json.dumps({"arm_child_refused": "a fence other than the controller's standing fence is up",
                              "fence": cur}), flush=True)
            sys.exit(3)
        (root / base.FENCE_NAME).unlink()
        base.sync_directory(root)
argv = ["launch", "--repo", req["repo"], "--python-bin", req["python"], "--kit", req["kit"], "--legs", req["legs"],
        "--output", req["output"], "--disk-path", req["repo"], "--custody-root", req["custody_root"],
        "--magistrate-pid", str(os.getpid()), "--deadline", repr(req["deadline"]),
        "--exit-wait-seconds", "180", "--start-wait-seconds", "30"]
if req["batch_window"]:
    argv[argv.index("--legs") + 2:argv.index("--legs") + 2] = ["--batch-window", req["batch_window"]]
rc = L.main(argv)
print(json.dumps({"arm_child_pid": os.getpid(), "launch_rc": rc}), flush=True)
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
                return {"plan": plan, "batch_window": window,
                        "expected_windows": [window] if window else [],
                        "deadline": plan["launch_deadline_epoch_s"] + LAUNCH_GRACE_S,
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
        lines = [line for line in res.stdout.splitlines() if line.strip().startswith("{")]
        launched, child = None, None
        for line in lines:
            with contextlib.suppress(ValueError):
                doc = json.loads(line)
                if "fence" in doc and "next" in doc:
                    launched = doc
                if "arm_child_pid" in doc:
                    child = doc["arm_child_pid"]
        return {"rc": res.rc, "launch": launched, "arm_child_pid": child, "stderr": res.stderr[-1500:]}


# --------------------------------------------------------------------------
# The controller
# --------------------------------------------------------------------------
class Controller:
    def __init__(self, cfg, *, env=None, git=None, preparer=None, launcher=None, issues=None, census=None,
                 proof=None, pid=None):
        self.cfg = cfg
        self.env = env or Env()
        self.state = Path(cfg["state_dir"])
        self.custody = Path(cfg["custody_root"])
        self.pid = pid or os.getpid()
        self.git = git or Git(cfg, self.env, self.guard)
        self.preparer = preparer or Preparer(cfg, self.env, self.git)
        self.launcher = launcher or Launcher(cfg, self.env)
        self.issues = issues or (lambda: read_issues(cfg, self.env, self.guard))
        self.census = census or (lambda: receipt_census(cfg["receipt_roots"]))
        self.proof = proof or (lambda kind, allowed=(): host_proof(cfg, self.env, kind, allowed_fence_purposes=allowed))
        self.token = (read_json(self.state / "token.json") or {}).get("token")
        if not self.token:
            self.token = uuid.uuid4().hex[:12]
            atomic_json(self.state / "token.json", {"token": self.token})
        self.network_open = True
        self.network_log = []
        self.last_status = None

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
        """Controller span records (arm.json merged with close.json), and intents without a result."""
        out, orphans = [], []
        base = self.state / "spans"
        for d in sorted(base.iterdir()) if base.is_dir() else []:
            intent = read_json(d / "intent.json")
            arm = read_json(d / "arm.json")
            close = read_json(d / "close.json")
            if intent is None:
                continue
            if arm is None:
                orphans.append(intent)
                continue
            rec = {**arm}
            if close is not None:
                rec.update(status=close["status"], closed_epoch=close["closed_epoch"],
                           bundle_sha256=close.get("bundle_sha256"), pushed=close.get("pushed"))
            out.append(rec)
        return out, orphans

    def externals(self):
        path = self.state / "external.jsonl"
        if not path.is_file():
            return []
        return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

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
                if cur["purpose"].startswith(STANDING_FENCE_PREFIX) and not self.env.pid_alive(cur["pid"]):
                    pass   # our own stale fence from before a restart: replace it
                else:
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
        """Page once per situation: the id is a digest of the kind, the codes, the spans and the context (not of
        free-text details, which may carry a countdown), so a persisting halt is paged once."""
        body = {"kind": kind, "reasons": [{k: r[k] for k in ("code", "category", "detail", "span")} for r in reasons],
                "context": context or {}}
        key = {"kind": kind, "codes": sorted({(r["code"], str(r["span"])) for r in reasons}), "context": context or {}}
        page_id = f"{kind.lower().replace('_', '-')}-{law.digest(key)[:16]}"
        path = self.state / "pages" / f"{page_id}.json"
        if path.exists():
            return page_id, False          # this exact situation was paged already (acked or not)
        exclusive_json(path, {"page_id": page_id, "epoch": self.env.now(), "at": iso(self.env.now()), **body})
        self.release_fence()
        self.transition(None, "page", {"page_id": page_id, "kind": kind, "codes": [r["code"] for r in reasons]})
        return page_id, True

    # -- status --------------------------------------------------------------------------------------
    def write_status(self, state, detail):
        status = {"schema": RECORD_SCHEMA, "state": state, "detail": detail, "epoch": self.env.now(),
                  "at": iso(self.env.now()), "pid": self.pid, "pages": [p["page_id"] for p in self.unacked_pages()],
                  "standing_fence": self.standing_purpose()}
        atomic_json(self.state / "STATUS.json", status)
        atomic_json(self.state / "heartbeat.json", {"pid": self.pid, "epoch": self.env.now(), "state": state})
        self.last_status = status
        return status

    # -- the tick ------------------------------------------------------------------------------------
    def tick(self):
        now = self.env.now()
        records, orphans = self.records()
        live = [r for r in records if r["status"] == "LIVE"]
        if live:
            return self.monitor(live[0])
        for intent in orphans:
            if not self.adopt_or_halt(intent):
                return self.write_status("HALTED", "arm intent without result")
            return self.write_status("LIVE", {"plan_id": intent["plan_id"], "adopted": True})
        unpushed = [r for r in records if r.get("pushed") is False]
        for rec in unpushed:
            self.network_open = True
            self.push_close(rec["plan_id"])
        pages = self.unacked_pages()
        if any(p["kind"] == "HALT" for p in pages):     # a halt waits for its acknowledgement
            self.release_fence()
            return self.write_status("PAGED", {"pages": [p["page_id"] for p in pages]})
        current = self._foreign_fence()
        seen = read_json(self.state / "foreign.json")
        if current is not None:
            if not seen or seen.get("purpose") != current.get("purpose"):
                atomic_json(self.state / "foreign.json", {"purpose": current.get("purpose"), "first_seen": now})
            return self.write_status("WAIT", {"reason": "SPAN_LIVE", "fence": current})
        if seen:
            # Another run (F0, a v4 session, a smoke) held the host: record its close as observed now, so the
            # 1,200 s floor after a non-campaign close holds even if nobody notes the run (note-run refines it).
            append_jsonl(self.state / "external.jsonl", {
                "run_id": seen["purpose"], "kind": "other", "t0_epoch": seen["first_seen"],
                "closed_epoch": math.ceil(now), "restore_ok": True, "observed_by_controller": True})
            (self.state / "foreign.json").unlink()
        self.network_open = True
        self.network_log = []
        snap, extra = self.snapshot(now, records)
        decision = law.select(snap)
        self.critical_path(decision, now)
        if decision.action in ("arm", "arm-fallback"):
            return self.arm(decision, snap, extra)
        last = law.last_close(snap["runs"])
        episode = {"last_close": None if last is None else last.plan_id}   # one page per situation per close
        if decision.action in ("halt", "cede", "page"):
            kind = {"halt": "HALT", "cede": "V4_SESSION", "page": decision.reasons[0]["code"]}[decision.action]
            page_id, new = self.page(kind, decision.reasons, episode)
            self.release_fence()
            return self.write_status("PAGED" if new or kind != "HALT" else "HALTED",
                                     {"page": page_id, "codes": [r["code"] for r in decision.reasons]})
        # wait: a long wait pages once per close (it also lets the magistrate run F0 on its standing item)
        if last is not None and now - last.closed > law.STALL_S:
            self.page("WAIT_STALL", [law.reason("WAIT_STALL", "; ".join(
                f"{r['code']}: {r['detail']}" for r in decision.reasons)[:400])], episode)
        if self.unacked_pages():     # an informational page is unread: the magistrate must be able to run
            self.release_fence()
            return self.write_status("PAGED", {"codes": [r["code"] for r in decision.reasons],
                                               "pages": [p["page_id"] for p in self.unacked_pages()]})
        held = self.hold_fence()
        return self.write_status("WAIT", {"codes": [r["code"] for r in decision.reasons], "fence": held,
                                          "etas": [r["eta"] for r in decision.reasons if r["eta"]]})

    def _foreign_fence(self):
        try:
            cur = fence.read_fence(self.custody)
        except (OSError, ValueError) as exc:
            return {"unreadable": str(exc)}
        if cur is None or cur["purpose"].startswith(STANDING_FENCE_PREFIX):
            return None
        if cur["deadline"] <= self.env.now() or not self.env.pid_alive(cur["pid"]):
            return None    # stale: the watchdog removes it and notices; our arm proof still refuses it
        return cur

    def snapshot(self, now, records):
        audit, reasons = read_audit(self.cfg, self.git, now)
        standing = audit["standing"]
        extra = {"audit": audit}
        empty = {"now": now, "standing": standing, "input_reasons": reasons, "queues": [], "runs": [],
                 "desk_halts": [], "vetoes": [], "watcher": [], "sessions": [], "census_epoch": None,
                 "fallback": [], "fallback_queues": [], "plan_worst": lambda c: None}
        if standing is None:
            return empty, extra
        runs = law.build_runs(standing, records, self.externals())
        desk_halts = law.apply_desk_finals(runs, audit["desk_finals"])
        ran = {r.plan_id for r in runs}
        for view in audit["queues"] + audit["fallback_queues"]:
            view["closed_ids"] = ran
        issues = self.issues()
        try:
            census = self.census()
        except OSError as exc:
            census = None
            reasons = reasons + [law.reason("RECEIPT_MISSING", f"host receipt census: {exc}")]
        unpushed = [r["plan_id"] for r in records if r.get("pushed") is False]
        if unpushed:
            reasons = reasons + [law.reason("BUNDLE_UNAUTHENTICATED", ", ".join(unpushed))]
        snap = {"now": now, "standing": standing, "input_reasons": reasons, "queues": audit["queues"], "runs": runs,
                "desk_halts": desk_halts, "vetoes": law.veto_reasons(issues, self.cfg["owner_login"]),
                "watcher": law.watcher_reasons(audit["watcher"], audit["watcher_commit"], now),
                "sessions": law.session_reasons(standing, audit["ready"], audit["done"]),
                "census_epoch": census, "fallback": standing["fallback"], "fallback_queues": audit["fallback_queues"],
                "plan_worst": lambda cand: self.plan_worst(cand, audit, now)}
        return snap, extra

    def plan_worst(self, cand, audit, now):
        kit = next(v["kits"][cand["kit_sha"]] for v in audit["queues"] + audit["fallback_queues"]
                   if cand["kit_sha"] in v["kits"])
        from joulewise.cadence import legs as legsmod
        try:
            plan = legsmod.plan_span(kit, t0_epoch=now, windows=[], leg_ids=cand["span"]["legs"])
        except legsmod.PlanError:
            return None
        return plan["worst_case_s"] + plan["soak_s"] + 560

    # -- critical-path ledger (RL-172 (i) row 6) -----------------------------------------------------
    def critical_path(self, decision, now):
        for sid, codes in decision.gates.items():
            path = self.state / "critical-path" / f"{sid}.json"
            doc = read_json(path) or {"span_id": sid, "first_considered": now, "blocking": {}, "cleared": {},
                                      "start": None, "end": None, "refusal": None}
            for code in codes:
                row = doc["blocking"].setdefault(code, {"first": now, "last": now})
                row["last"] = now
                doc["cleared"].pop(code, None)
            for code, row in doc["blocking"].items():
                if code not in codes and code not in doc["cleared"]:
                    doc["cleared"][code] = now        # the prerequisite became ready (first tick it held)
            doc["ready_all"] = now if not codes and doc.get("ready_all") is None else doc.get("ready_all")
            atomic_json(path, doc)

    def critical_path_event(self, span_id, **fields):
        path = self.state / "critical-path" / f"{span_id}.json"
        doc = read_json(path) or {"span_id": span_id, "blocking": {}, "cleared": {}}
        doc.update(fields)
        atomic_json(path, doc)

    # -- arm -----------------------------------------------------------------------------------------
    def arm(self, decision, snap, extra):
        cand = decision.candidate
        span, sha = cand["span"], cand["kit_sha"]
        plan_id = q.plan_id(span)
        audit = extra["audit"]
        standing = snap["standing"]
        entry = standing["kits"][sha]
        kit = next(v["kits"][sha] for v in audit["queues"] + audit["fallback_queues"] if sha in v["kits"])
        queue_view = next(v for v in audit["queues"] + audit["fallback_queues"] if v["path"] == cand["queue_path"])
        now = self.env.now()
        # 1. network part of the preparation (a worktree prepared on an earlier tick for this plan is reused)
        prepared = read_json(self.span_dir(plan_id) / "prepared.json")
        if prepared and Path(prepared["repo"]).is_dir() and Path(prepared["kit"]).is_file():
            paths, problem = prepared, None
        else:
            paths, problem = self.preparer.materialize(plan_id, sha, audit["kit_bytes"][sha], kit["frozen"]["commit"])
            if paths:
                atomic_json(self.span_dir(plan_id) / "prepared.json", paths)
        # 2. the network phase ends here; nothing below may reach the network until the close
        self.network_open = False
        network_end = max([n["epoch"] for n in self.network_log] or [now])
        if problem:
            return self._prepare_failed(plan_id, span, problem)
        info, problem = self.preparer.check(paths, kit, sha, list(span["legs"]), entry["batch_window"], now)
        if problem:
            if problem.startswith("PLAN_REFUSED_AT_T0"):
                self.hold_fence()
                return self.write_status("WAIT", {"codes": ["PLAN_REFUSED_AT_T0"], "detail": problem})
            return self._prepare_failed(plan_id, span, problem)
        out = Path(self.cfg["output_root"]) / kit["campaign_id"] / (
            f"{plan_id}-{datetime.fromtimestamp(now, timezone.utc).strftime('%Y%m%dT%H%M%SZ')}")
        if out.exists() or OUT_REFUSED.search(str(out) + "/") or str(out).startswith(str(self.custody)):
            return self._prepare_failed(plan_id, span, f"output {out} exists or is inside a refused root")
        # 3. the arm proof: readback and absence, now, with the network closed
        proof = self.proof("arm", (self.standing_purpose(),))
        rs = law.proof_reasons(proof["lines"], "arm")
        if rs:
            if law.category(rs) == "wait":
                self.hold_fence()
                return self.write_status("WAIT", {"codes": [r["code"] for r in rs]})
            self.page("HALT", rs, {"plan_id": plan_id, "proof": proof_digest(proof)})
            return self.write_status("HALTED", {"codes": [r["code"] for r in rs]})
        # 4. last re-checks: same date, floor still clear
        t0 = self.env.now()
        recheck = law.gap_reasons(snap["runs"], t0, snap.get("census_epoch"))
        if cand["cls"]["dated"]:
            recheck += law.date_reasons(span, cand["cls"], t0, snap["runs"], [], standing)
        if law.category(recheck):
            self.hold_fence()
            return self.write_status("WAIT", {"codes": [r["code"] for r in recheck]})
        last = law.last_close(snap["runs"])
        intent = {
            "schema": RECORD_SCHEMA, "plan_id": plan_id, "span": span, "queue": {
                "path": cand["queue_path"], "queue_id": queue_view["doc"]["queue_id"], "sha256": queue_view["digest"],
                "commit_epoch": queue_view["commit_epoch"], "role": cand["role"]},
            "standing_sha256": law.digest(standing), "kit": {"sha256": sha, "campaign_id": kit["campaign_id"],
                                                           "frozen_commit": kit["frozen"]["commit"],
                                                           "source": entry["source"], "path": paths["kit"]},
            "class": cand["cls"], "fallback": decision.action == "arm-fallback",
            "repo": paths["repo"], "output": str(out), "deadline": info["deadline"],
            "batch_window": info["batch_window"], "expected_windows": info["expected_windows"],
            "plan_sha256": law.digest(info["plan"]), "worst_case_s": info["worst_case_s"],
            "network_end_epoch": network_end, "arm_proof": proof, "arm_proof_sha256": proof_digest(proof),
            "predecessor": None if last is None else {
                "plan_id": last.plan_id, "closed": last.closed, "status": last.status, "source": last.source,
                **({k: (read_json(self.span_dir(last.plan_id) / "close.json") or {}).get(k)
                    for k in ("close_proof_sha256", "bundle_sha256")} if last.source == "controller" else {})},
            "gates": decision.gates, "t0_epoch": t0}
        try:
            exclusive_json(self.span_dir(plan_id) / "intent.json", intent)
        except FileExistsError:
            self.page("HALT", [law.reason("ARM_INDETERMINATE", f"{plan_id}: intent already exists")])
            return self.write_status("HALTED", {"plan_id": plan_id})
        self.transition(plan_id, "arm_intent", {"queue_sha256": queue_view["digest"], "plan_sha256": intent["plan_sha256"],
                                                "arm_proof_sha256": intent["arm_proof_sha256"],
                                                "network_end_epoch": network_end})
        request = {"repo": paths["repo"], "python": self.cfg["measurement_python"], "kit": paths["kit"],
                   "legs": ",".join(span["legs"]), "batch_window": info["batch_window"], "output": str(out),
                   "custody_root": str(self.custody), "deadline": info["deadline"],
                   "standing_purpose": self.standing_purpose(), "controller_pid": self.pid}
        result = self.launcher.launch(request)
        return self.record_launch(plan_id, intent, result, kit, cand)

    def _prepare_failed(self, plan_id, span, problem):
        self.page("HALT", [law.reason("PREPARE_FAILED", f"{plan_id}: {problem}"[:400], span=span["span_id"])])
        return self.write_status("HALTED", {"plan_id": plan_id, "problem": problem})

    def record_launch(self, plan_id, intent, result, kit, cand):
        launched = result.get("launch") or {}
        try:
            current = fence.read_fence(self.custody)
        except (OSError, ValueError):
            current = None
        problems = []
        if result.get("rc") != 0 or launched.get("next") != "exit the magistrate session now":
            problems.append(f"launch rc {result.get('rc')}: {result.get('stderr', '')[-300:]}")
        claimed = launched.get("fence") or {}
        if not (current and current.get("purpose") == claimed.get("purpose")
                and current.get("pid") != result.get("arm_child_pid") and self.env.pid_alive(current.get("pid", 0))):
            problems.append(f"fence not claimed by the LaunchAgent: {current}")
        windows = (launched.get("plan") or {}).get("batch_windows")
        if windows is not None and windows != intent["expected_windows"]:
            problems.append(f"plan batch_windows {windows} != {intent['expected_windows']}")
        arm = {"schema": RECORD_SCHEMA, "plan_id": plan_id, "status": "LIVE" if not problems else "LAUNCH_REFUSED",
               "kind": "f2" if intent["fallback"] else "campaign", "phase": cand["cls"]["phase"],
               "block_id": intent["span"]["block_id"], "legs": intent["span"]["legs"], "mixed": cand["cls"]["mixed"],
               "kit_sha256": intent["kit"]["sha256"], "needs_print": kit["schema"] == kit_v11.SCHEMA,
               "t0_epoch": intent["t0_epoch"], "launch_epoch": self.env.now(), "output": intent["output"],
               "deadline": intent["deadline"], "fence_purpose": claimed.get("purpose"),
               "arm_command": {"rc": result.get("rc"), "launch": launched, "arm_child_pid": result.get("arm_child_pid"),
                               "fence_after": current, "problems": problems},
               "arm_proof_sha256": intent["arm_proof_sha256"], "queue_sha256": intent["queue"]["sha256"],
               "plan_sha256": intent["plan_sha256"]}
        arm["arm_command_sha256"] = law.digest(arm["arm_command"])
        atomic_json(self.span_dir(plan_id) / "arm.json", arm)
        self.transition(plan_id, "armed" if not problems else "launch_refused",
                        {"queue_sha256": arm["queue_sha256"], "plan_sha256": arm["plan_sha256"],
                         "arm_proof_sha256": arm["arm_proof_sha256"], "arm_command_sha256": arm["arm_command_sha256"],
                         "decision": arm["status"]})
        self.critical_path_event(intent["span"]["span_id"], start=arm["launch_epoch"], plan_id=plan_id,
                                 refusal="; ".join(problems) or None)
        if problems:
            self.page("HALT", [law.reason("LAUNCH_REFUSED", "; ".join(problems)[:400], span=intent["span"]["span_id"])])
            return self.write_status("HALTED", {"plan_id": plan_id})
        return self.write_status("LIVE", {"plan_id": plan_id, "deadline": arm["deadline"]})

    def adopt_or_halt(self, intent):
        """After a restart: an intent with no arm record. The launch happened if its output or a launch fence
        exists; adopt it as live (the monitor then waits for the fence and closes on the receipt). Otherwise
        the outcome is unknown: halt, never re-launch."""
        plan_id = intent["plan_id"]
        try:
            cur = fence.read_fence(self.custody)
        except (OSError, ValueError):
            cur = None
        launch_fence = cur if cur is not None and cur["purpose"].startswith("align-r0:") else None
        adopted = Path(intent["output"]).exists() or launch_fence is not None
        kit = json.loads(Path(intent["kit"]["path"]).read_text())
        arm = {"schema": RECORD_SCHEMA, "plan_id": plan_id, "status": "LIVE" if adopted else "INDETERMINATE",
               "kind": "f2" if intent["fallback"] else "campaign", "phase": intent["class"]["phase"],
               "block_id": intent["span"]["block_id"], "legs": intent["span"]["legs"], "mixed": intent["class"]["mixed"],
               "kit_sha256": intent["kit"]["sha256"], "needs_print": kit["schema"] == kit_v11.SCHEMA,
               "t0_epoch": intent["t0_epoch"], "launch_epoch": None, "output": intent["output"],
               "deadline": intent["deadline"], "fence_purpose": None if launch_fence is None else launch_fence["purpose"],
               "arm_command": {"adopted_after_restart": True, "fence_after": cur},
               "arm_proof_sha256": intent["arm_proof_sha256"], "queue_sha256": intent["queue"]["sha256"],
               "plan_sha256": intent["plan_sha256"]}
        arm["arm_command_sha256"] = law.digest(arm["arm_command"])
        atomic_json(self.span_dir(plan_id) / "arm.json", arm)
        self.transition(plan_id, "adopted" if adopted else "indeterminate",
                        {"decision": arm["status"], "fence": cur, "output_exists": Path(intent["output"]).exists()})
        if not adopted:
            self.page("HALT", [law.reason("ARM_INDETERMINATE", plan_id, span=intent["span"]["span_id"])])
        return adopted

    # -- live and close ------------------------------------------------------------------------------
    def monitor(self, rec):
        """A live span: stat the fence and the receipt only."""
        self.network_open = False
        now = self.env.now()
        try:
            cur = fence.read_fence(self.custody)
        except (OSError, ValueError):
            cur = {"purpose": "unreadable", "pid": 0, "deadline": now + 60}
        held = cur is not None and cur["purpose"] == rec.get("fence_purpose") and self.env.pid_alive(cur["pid"])
        receipt = Path(rec["output"]) / RECEIPT
        if held:
            if now > rec["deadline"] + STRANDED_GRACE_S:
                return self.close(rec, stranded="fence held past its deadline")
            atomic_json(self.state / "heartbeat.json", {"pid": self.pid, "epoch": now, "state": "LIVE"})
            return {"state": "LIVE", "plan_id": rec["plan_id"]}
        if receipt.is_file():
            return self.close(rec)
        if now > (read_json(self.span_dir(rec["plan_id"]) / "fence-gone.json") or {}).get("epoch", now) + RECEIPT_GRACE_S:
            return self.close(rec, stranded="fence gone and no receipt")
        if not (self.span_dir(rec["plan_id"]) / "fence-gone.json").exists():
            atomic_json(self.span_dir(rec["plan_id"]) / "fence-gone.json", {"epoch": now})
        return self.write_status("CLOSING", {"plan_id": rec["plan_id"], "waiting": "receipt"})

    def close(self, rec, stranded=None):
        plan_id = rec["plan_id"]
        intent = read_json(self.span_dir(plan_id) / "intent.json")
        out = Path(rec["output"])
        span, sha = intent["span"], intent["kit"]["sha256"]
        kit = json.loads(Path(intent["kit"]["path"]).read_text())
        reasons = []
        receipt_raw = (out / RECEIPT).read_bytes() if (out / RECEIPT).is_file() else None
        receipt = json.loads(receipt_raw) if receipt_raw else None
        if stranded or receipt is None:
            reasons.append(law.reason("RECEIPT_MISSING", stranded or "no receipt", span=span["span_id"]))
            receipt = {}
        else:
            reasons += law.receipt_command_reasons(receipt, intent["expected_windows"])
        bundle_root = out / "desk-bundle"
        files = sorted(p.relative_to(bundle_root).as_posix() for p in bundle_root.rglob("*") if p.is_file()) \
            if bundle_root.is_dir() else []
        summaries, legs_rows = {}, []
        try:
            for row in receipt.get("legs") or []:
                f = bundle_root / "legs" / row["leg_id"] / "leg_summary.json"
                if f.is_file():
                    summaries[row["leg_id"]] = deskmod._project(deskmod._json(f, "leg-summary-v1"),
                                                                deskmod.LEG_SUMMARY_KEYS, f"legs/{row['leg_id']}", True)
            meter, result = deskmod._span_extras(bundle_root, "leg-summary-v1") if bundle_root.is_dir() else ({}, None)
        except (deskmod.DeskRefusal, ValueError, OSError) as exc:
            reasons.append(law.reason("ROSTER_MISMATCH", f"desk bundle: {exc}"[:300], span=span["span_id"]))
            meter, result = {}, None
        plan = read_json(out / "span_plan.json")
        if receipt:
            reasons += law.desk_input_reasons(span=span, kit_sha=sha, kit=kit, receipt=receipt, bundle_files=files,
                                              summaries=summaries, plan=plan)
            summary = {"result": result, "meter": meter, "feeds_proven_stopped": bool(meter.get("proven_stopped")),
                       "legs": list(summaries.values())}
            reasons += [law.reason("NAMED_STOP", f"{s['code']}: {s['detail']}"[:300], span=span["span_id"])
                        for s in stopsmod.evaluate_named_stops(kit["stop_rules"], summary)]
        proof = self.proof("close", (self.standing_purpose(),))
        reasons += law.proof_reasons(proof["lines"], "close")
        maintenance = self.maintenance_line(out, rec)
        closed = math.ceil(os.stat(out / RECEIPT).st_mtime) if (out / RECEIPT).is_file() else math.ceil(self.env.now())
        codes = {r["code"] for r in reasons}
        status = ("CLOSED_OK" if not reasons else "STRANDED" if "RECEIPT_MISSING" in codes
                  else "REFUSED" if "RECEIPT_NOT_CLEAN" in codes else "CLOSE_UNPROVEN" if "CLOSE_UNPROVEN" in codes
                  else "STOPPED")
        manifest = {
            "schema": law.BUNDLE_SCHEMA, "plan_id": plan_id, "span": span, "queue": intent["queue"],
            "kit": {"sha256": sha, "campaign_id": kit["campaign_id"], "frozen_commit": kit["frozen"]["commit"],
                    "source": intent["kit"]["source"]},
            "roster": span["legs"], "attempts": {lid: s.get("attempts") for lid, s in summaries.items()},
            "receipt_sha256": sha256_bytes(receipt_raw) if receipt_raw else None,
            "plan_sha256": sha256_file(out / "span_plan.json") if (out / "span_plan.json").is_file() else None,
            "soak_reference_sha256": (sha256_file(out / "soak" / "soak_reference.json")
                                      if (out / "soak" / "soak_reference.json").is_file() else None),
            "files": {f: sha256_file(bundle_root / f) for f in files},
            "soak_attempts": [{k: a.get(k) for k in ("attempt", "refused", "output_dir")}
                              for a in receipt.get("soak_attempts") or []],
            "status": status, "reasons": [{k: r[k] for k in ("code", "detail")} for r in reasons],
            "maintenance_line": maintenance,
            "close_proof_sha256": proof_digest(proof), "arm_proof_sha256": intent["arm_proof_sha256"],
            "arm_command_sha256": rec.get("arm_command_sha256"), "closed_epoch": closed, "t0_epoch": rec["t0_epoch"],
            "controller": {"pid": self.pid, "token": self.token}}
        close = {"schema": RECORD_SCHEMA, "plan_id": plan_id, "status": status, "closed_epoch": closed,
                 "close_proof": proof, "close_proof_sha256": manifest["close_proof_sha256"], "reasons": reasons,
                 "manifest": manifest, "bundle_sha256": None, "pushed": False}
        atomic_json(self.span_dir(plan_id) / "close.json", close)
        self.transition(plan_id, "closed", {"decision": status, "close_proof_sha256": manifest["close_proof_sha256"],
                                            "codes": sorted(codes), "queue_sha256": intent["queue"]["sha256"]})
        self.critical_path_event(span["span_id"], end=closed, refusal=None if status == "CLOSED_OK" else status)
        self.network_open = True
        self.push_close(plan_id)
        if status != "CLOSED_OK":
            self.page("HALT", reasons or [law.reason("SPAN_BAD_TERMINAL", status)], {"plan_id": plan_id})
            return self.write_status("HALTED", {"plan_id": plan_id, "status": status})
        return self.write_status("CLOSED", {"plan_id": plan_id})

    MAINTENANCE = ("dasd", "XProtect", "XprotectService", "XProtectPluginService", "mds", "mds_stores", "mdworker",
                   "mdworker_shared", "backupd", "softwareupdated", "mobileassetd")

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
        close = read_json(self.span_dir(plan_id) / "close.json")
        intent = read_json(self.span_dir(plan_id) / "intent.json")
        out = Path(intent["output"])
        manifest_raw = (json.dumps(close["manifest"], indent=1, sort_keys=True) + "\n").encode()
        files = {"manifest.json": manifest_raw}
        for name in (RECEIPT, "span_plan.json"):
            if (out / name).is_file():
                files[name] = (out / name).read_bytes()
        for rel in close["manifest"]["files"]:
            files[f"desk-bundle/{rel}"] = (out / "desk-bundle" / rel).read_bytes()
        bad = [k for name, raw in files.items() for k in _json_keys(raw) if deskmod.DENIED_KEY_RE.search(k)]
        if bad:
            self.page("HALT", [law.reason("BUNDLE_UNAUTHENTICATED", f"denied keys in the bundle: {sorted(set(bad))[:5]}")])
            return False
        ref = f"{self.cfg['bundle_ref_prefix']}{plan_id}"
        try:
            sha, problem = self.git.push_bundle(ref, files, f"cadence close bundle {plan_id}")
        except NetworkClosed as exc:
            sha, problem = None, str(exc)
        if problem:
            self.transition(plan_id, "push_failed", {"problem": problem[:300]})
            return False
        close.update(pushed=True, bundle_sha256=sha256_bytes(manifest_raw), bundle_commit=sha, bundle_ref=ref)
        atomic_json(self.span_dir(plan_id) / "close.json", close)
        self.transition(plan_id, "bundle_pushed", {"bundle_sha256": close["bundle_sha256"], "commit": sha, "ref": ref})
        return True


def _json_keys(raw):
    try:
        doc = json.loads(raw)
    except ValueError:
        return []
    return list(deskmod._keys(doc))


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
    ticks = 0
    while max_ticks is None or ticks < max_ticks:
        ticks += 1
        try:
            status = ctl.tick()
        except Exception as exc:  # noqa: BLE001 - a crash in one tick is a halt with a page, never a silent loop
            ctl.network_open = False
            ctl.page("HALT", [law.reason("STATE_CORRUPT", f"{type(exc).__name__}: {exc}"[:400])])
            status = ctl.write_status("HALTED", {"exception": f"{type(exc).__name__}: {exc}"[:400]})
        live = (status or {}).get("state") in ("LIVE", "CLOSING")
        ctl.env.sleep(ctl.cfg["poll_live_s"] if live else ctl.cfg["poll_idle_s"])


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
    row = {"run_id": args.run_id, "kind": args.kind, "t0_epoch": args.t0, "closed_epoch": args.closed,
           "restore_ok": args.restore_ok == "yes", "noted": time.time()}
    append_jsonl(Path(cfg["state_dir"]) / "external.jsonl", row)
    print(json.dumps(row))
    return 0


def cmd_check_heartbeat(cfg, args):
    hb = read_json(Path(cfg["state_dir"]) / "heartbeat.json")
    age = None if hb is None else time.time() - hb["epoch"]
    print(json.dumps({"heartbeat": hb, "age_s": age}))
    return 0 if age is not None and age <= args.max_age else 1


def cmd_ledger(cfg, _args):
    base = Path(cfg["state_dir"]) / "critical-path"
    writer = csv.writer(sys.stdout)
    writer.writerow(["span_id", "plan_id", "first_considered", "prerequisite", "blocked_first", "ready_at", "start",
                     "end", "refusal"])
    for path in sorted(base.glob("*.json")) if base.is_dir() else []:
        doc = read_json(path)
        for code, row in sorted(doc.get("blocking", {}).items()) or [("-", {})]:
            writer.writerow([doc["span_id"], doc.get("plan_id"), iso(doc["first_considered"]) if doc.get("first_considered") else "",
                             code, iso(row["first"]) if row.get("first") else "",
                             iso(doc["cleared"][code]) if code in doc.get("cleared", {}) else "",
                             iso(doc["start"]) if doc.get("start") else "", iso(doc["end"]) if doc.get("end") else "",
                             doc.get("refusal") or ""])
    return 0


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("loop", "tick", "status", "ledger"):
        sub.add_parser(name).add_argument("--config", required=True)
    s = sub.add_parser("ack"); s.add_argument("page_id"); s.add_argument("--config", required=True)
    s.add_argument("--by", required=True); s.add_argument("--note", required=True)
    s = sub.add_parser("note-run"); s.add_argument("--config", required=True)
    s.add_argument("--kind", choices=("F0", "v4", "partc", "other"), required=True); s.add_argument("--run-id", required=True)
    s.add_argument("--t0", type=float, required=True); s.add_argument("--closed", type=float, required=True)
    s.add_argument("--restore-ok", choices=("yes", "no"), required=True)
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
    if args.cmd == "ack":
        return cmd_ack(cfg, args)
    if args.cmd == "note-run":
        return cmd_note_run(cfg, args)
    if args.cmd == "check-heartbeat":
        return cmd_check_heartbeat(cfg, args)
    if args.cmd == "ledger":
        return cmd_ledger(cfg, args)
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
