"""Offline B0 differential runner (stdlib only).

Replay from the repository:
  python3 -B tests/parity/b0_runner.py --candidate . --output /tmp/278ebc9e/b0par-v3
  python3 -B tests/parity/b0_runner.py --candidate-ref 7647bb2e --output /tmp/278ebc9e/b0par-v2
  python3 -B tests/parity/b0_runner.py --self --output /tmp/278ebc9e/b0par-v1

Archives never register a worktree or write Git metadata. Both evaluators run
this exact harness in separate processes, sequentially at the SAME physical
fixture path per shard. Shards have disjoint paths, identical on both sides.
No path, refusal, exception, output, or call normalization occurs.
The immutable fixture comes from the oracle, not either side's test helpers.
Only external responses are fake: Git transport/status, interpreter/build,
syntax-only shell check, launchd, process cleanup, and probe worker bodies.
Kind parsing, chain/manifest authentication and receipt validation are real.
Embedded Python subprocess programs execute under the side's isolated module
universe; their exact argv (including source) is retained as an observation.
This intentionally reports changed dependency argv even with equal outcomes.

The diagnostic.custody_row surface did not exist at base. Its availability
diffs are retained separately and do not gate shared-surface parity; they are
NOT proof of a public cleanup bypass. The separately ruled 72b F4 invariant
does gate: a bare wrapper with no sidecar, source or C5 cannot select a row.
"""
from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import dataclasses
import datetime
from enum import Enum
import gzip
import hashlib
import io
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import time
import traceback
from types import SimpleNamespace
from unittest.mock import patch

# Import support by its physical path: candidate trees need not contain tests.
sys.path.insert(0, str(Path(__file__).absolute().parent))
from b0_corpus import AXES, BASE, DEFAULTS, IDLE, OPERATIONS, SEED, corpus, jobs

HERE = Path(__file__).absolute()
REPO = HERE.parents[2]
SCRATCH = Path("/tmp/278ebc9e")
SLOT = int(os.environ.get("B0_PARITY_SLOT", "0"))
FIXTURE = (SCRATCH / f"b0par-fixture-{SLOT}").resolve()
HEAD = "2ea6a7ec3d199908ad85d79e0f6a2a511bb25b4b"
NOW = 1790197200.0
T0 = 1790200800
CHAIN = "scripts/night_chains/quiet_predicate_evidence.zsh"
PROTOCOL = "configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v3.json"
STEP_NAMES = ("clone", "venv", "plan", "wrapper", "render", "complete")
_SNAPSHOT_CACHE = {}


class FrozenDatetime(datetime.datetime):
    @classmethod
    def now(cls, tz=None):
        return cls.fromtimestamp(NOW, tz)

    @classmethod
    def utcnow(cls):
        return cls.fromtimestamp(NOW, datetime.timezone.utc).replace(tzinfo=None)


class HarnessError(BaseException):
    """A broken adapter/fence must abort the run, never look like equal refusals."""


def encode(value):
    if isinstance(value, bytes):
        return {"bytes_base64": base64.b64encode(value).decode()}
    if isinstance(value, Path):
        return {"path": str(value)}
    if isinstance(value, Enum):
        return {"enum": type(value).__module__ + "." + type(value).__qualname__, "name": value.name}
    if dataclasses.is_dataclass(value):
        return {"dataclass": type(value).__module__ + "." + type(value).__qualname__,
                "fields": encode(dataclasses.asdict(value))}
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return {"tuple": [encode(v) for v in value]}
    if isinstance(value, list):
        return [encode(v) for v in value]
    if callable(value) and hasattr(value, "__qualname__"):
        return {"callable": value.__module__ + "." + value.__qualname__}
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise HarnessError(f"unsupported observation type: {type(value)}")


def dump(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2) + "\n")


def safe_scratch(path):
    p = Path(path).absolute()
    if p.parent.resolve() != SCRATCH.resolve() or not p.name.startswith("b0par-") or p.is_symlink():
        raise ValueError("scratch must be a direct /tmp/278ebc9e/b0par-* child")
    return p


def archive(ref, target):
    target = safe_scratch(target)
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    # Read-only Git; archive extraction is bounded to the explicitly named tmp tree.
    raw = subprocess.check_output(["git", "-C", str(REPO), "archive", ref])
    with tarfile.open(fileobj=io.BytesIO(raw)) as stream:
        for member in stream.getmembers():
            if Path(member.name).is_absolute() or ".." in Path(member.name).parts or member.issym() or member.islnk():
                raise ValueError("unsafe archive member: " + member.name)
        if sys.version_info >= (3, 12):
            stream.extractall(target, filter="data")
        else:
            stream.extractall(target)
    return target.resolve()


def snapshot(root):
    result = {}
    if not root.exists():
        return result
    for directory, dirs, files in os.walk(root, followlinks=False):
        for name in sorted(dirs + files):
            path = Path(directory) / name
            st = path.lstat()
            row = {"mode": stat.S_IMODE(st.st_mode)}
            if stat.S_ISLNK(st.st_mode):
                row.update(kind="symlink", target=os.readlink(path))
            elif stat.S_ISDIR(st.st_mode):
                row.update(kind="directory")
            elif stat.S_ISREG(st.st_mode):
                signature = (st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns, st.st_mode)
                cached = _SNAPSHOT_CACHE.get(str(path))
                if cached and cached[0] == signature:
                    result[str(path.relative_to(root))] = cached[1]
                    continue
                # Even permission-denied fixtures are snapshotable by the harness.
                if not row["mode"] & stat.S_IRUSR:
                    path.chmod(row["mode"] | stat.S_IRUSR)
                    raw = path.read_bytes()
                    path.chmod(row["mode"])
                else:
                    raw = path.read_bytes()
                row.update(kind="file", **encode(raw))
                _SNAPSHOT_CACHE[str(path)] = (signature, row)
            else:
                raise HarnessError("irregular fixture file: " + str(path))
            result[str(path.relative_to(root))] = row
    return result


def restore(root, tree, current=None):
    """Restore exact independent preconditions, including empty dirs and modes."""
    if current is None:
        current = snapshot(root)
    for name in sorted(current, key=lambda n: (n.count("/"), n), reverse=True):
        if name not in tree or current[name]["kind"] != tree[name]["kind"]:
            path = root / name
            if path.is_dir() and not path.is_symlink():
                path.rmdir()
            else:
                path.unlink()
    root.mkdir(parents=True, exist_ok=True)
    for name in sorted(tree, key=lambda n: (n.count("/"), n)):
        row, path = tree[name], root / name
        old = current.get(name)
        if row == old:
            continue
        if row["kind"] == "directory":
            path.mkdir(exist_ok=True)
        elif row != old:
            if path.is_symlink():
                path.unlink()
            if row["kind"] == "symlink":
                path.symlink_to(row["target"])
            else:
                if path.exists():
                    path.chmod(0o600)
                path.write_bytes(base64.b64decode(row["bytes_base64"]))
        if row["kind"] != "symlink" and row != old:
            path.chmod(row["mode"])
            os.utime(path, (NOW, NOW))


def file_delta(before, after):
    return {name: {"before": before.get(name), "after": after.get(name)}
            for name in sorted(before.keys() | after.keys()) if before.get(name) != after.get(name)}


def json_bytes(value, encoding="utf8"):
    return json.dumps(value, sort_keys=True).encode({"bom": "utf-8-sig", "utf16": "utf-16",
        "utf16le": "utf-16-le", "utf16be": "utf-16-be"}.get(encoding, "utf8"))


class World:
    def __init__(self, oracle):
        from joulewise import evidence_night, night_gate, night_agent_install, quiet_predicate_campaign
        from scripts import gen_evidence_night, run_night
        from joulewise.zero_capture_facts import zero_capture_facts
        self.en, self.ng, self.inst, self.campaign = evidence_night, night_gate, night_agent_install, quiet_predicate_campaign
        self.gen, self.rn, self.zero = gen_evidence_night, run_night, zero_capture_facts
        self.oracle = Path(oracle)
        self.roots, self.stages = FIXTURE / "roots", FIXTURE / "stages"
        self.fields = self.en.locations(self.roots, self.stages, T0, HEAD)
        self.root = Path(self.fields["measurement_root"])
        self.stage = Path(self.fields["staging"])
        self.custody = Path(self.fields["custody_root"])
        self.night = self.custody / "night"
        self.plan_path = self.stage / "night_plan.json"
        self.chain = self.custody / "chain.zsh"
        self.source = self.root / CHAIN
        self.calls = []
        self.values = dict(DEFAULTS)
        names = set(self.campaign.MANIFEST_PATHS) | {
            "env/mac-measurement-lock.txt", "configs/launchd/com.joulewise.night.plist.template",
            "configs/launchd/com.joulewise.night-probe.plist.template", "docs/process/NIGHT_COURIER_PROMPT.md"}
        self.tracked = {name: (self.oracle / name).read_bytes() for name in sorted(names)}
        self.real_read_bytes, self.real_read_text = Path.read_bytes, Path.read_text
        self.read_counts = Counter()
        self.before_cache = {}
        self.active = False
        self.temp_names = (f"p{n:07d}" for n in itertools.count())

    def record(self, name, *args, **kwargs):
        self.calls.append({"call": name, "args": encode(args), "kwargs": encode(kwargs)})

    def build(self, root):
        self.record("builder", root)
        (root / ".venv/bin").mkdir(parents=True, exist_ok=True)
        (root / ".venv/bin/python").write_text("fixture interpreter; never executable\n")

    def clone_files(self, root):
        for name, raw in self.tracked.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)

    def shell(self, argv, **kwargs):
        """Strict external-response table; unknown commands fail the HARNESS."""
        argv = list(map(str, argv))
        self.record("subprocess.run", argv, **kwargs)
        out, err, rc = b"", b"", 0
        if Path(argv[0]).name == "git":
            if "show" in argv:
                name = argv[-1].split(":", 1)[1]
                out = self.tracked[name]
            elif "rev-parse" in argv:
                out = ("HEAD" if "--abbrev-ref" in argv else
                       ("b" * 40 if self.values["clone"] == "wrong_head" else HEAD)).encode() + b"\n"
            elif "status" in argv:
                dirty = self.values["clone"] == "dirty" or self.values["source"] in ("modified", "moved", "absent", "nonutf8", "directory", "symlink")
                out = b" M scripts/night_chains/quiet_predicate_evidence.zsh\n" if dirty else b""
            elif "clone" in argv:
                if Path(argv[-1]).name == "results-clone":
                    Path(argv[-1]).mkdir(parents=True, exist_ok=True)
                else:
                    self.clone_files(Path(argv[-1]))
            elif "ls-remote" in argv:
                out = (HEAD + "\trefs/heads/main\n").encode()
            elif "remote" in argv:
                out = b"https://example.invalid/fixture\n"
            elif not any(x in argv for x in ("checkout", "fetch", "merge-base", "add", "commit", "push")):
                raise HarnessError("unhandled Git argv: " + repr(argv))
        elif "-c" in argv and Path(argv[0]).name.startswith("python"):
            code = argv[argv.index("-c") + 1]
            # Interpreter identity is an external response. All validators stay real.
            if "'version':'.'.join" in code:
                out = json_bytes({"path": argv[0], "version": "3.13.0", "sha256": "f" * 64})
            else:
                stdout, stderr = io.StringIO(), io.StringIO()
                with patch.object(sys, "argv", ["-c", *argv[argv.index("-c") + 2:]]), \
                     patch.object(sys, "stdin", io.StringIO(kwargs.get("input") or "")), \
                     patch.object(sys, "executable", argv[0]), redirect_stdout(stdout), redirect_stderr(stderr):
                    try:
                        exec(compile(code, "<string>", "exec"), {"__name__": "__main__"})
                    except SystemExit as exc:
                        rc = exc.code or 0
                    except Exception as exc:
                        # Reproduce a failed Python child, rather than leaking
                        # its exception through the subprocess adapter.
                        rc = 1
                        stderr.write("".join(traceback.format_exception(type(exc), exc, exc.__traceback__.tb_next)))
                out, err = stdout.getvalue().encode(), stderr.getvalue().encode()
        elif "pip" in argv and "freeze" in argv:
            out = self.tracked["env/mac-measurement-lock.txt"]
            out = ("\n".join(x.strip() for x in out.decode().splitlines() if x.strip() and not x.startswith("#")) + "\n").encode()
        elif "scripts/gen_evidence_night.py" in argv:
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                rc = self.gen.main(argv[argv.index("scripts/gen_evidence_night.py") + 1:])
            out = buffer.getvalue().encode()
        elif len(argv) > 3 and argv[2] == str(self.root / "scripts/run_night.py") and argv[3] == "preflight":
            pass  # deterministic external preflight response; render validation is real
        elif Path(argv[0]).name == "install_night_agent.sh":
            if "--render-only" in argv:
                target = Path(argv[argv.index("--render-only") + 1])
                target.mkdir(parents=True)
                prepared = self.prepared(self.ng.NightPlan.from_mapping(json.loads(Path(argv[argv.index("--plan") + 1]).read_bytes())))
                for label, data in prepared.render(self.inst.LABELS, require_published=False):
                    (target / (label + ".plist")).write_bytes(data)
            elif "--uninstall" not in argv:
                raise HarnessError("installer invocation is not render/uninstall")
        elif argv[:2] == ["/bin/zsh", "-n"]:
            pass  # syntax-only external response, never executes a wrapper
        elif Path(argv[0]).name == "gh":
            out = b"[]"
        elif argv[0] == str(FIXTURE / "fake-launchctl"):
            out = b"fixture loaded\n"
        else:
            raise HarnessError("unhandled external argv: " + repr(argv))
        result = subprocess.CompletedProcess(argv, rc, out.decode() if kwargs.get("text") else out,
                                             err.decode() if kwargs.get("text") else err)
        if kwargs.get("check") and rc:
            raise subprocess.CalledProcessError(rc, argv, result.stdout, result.stderr)
        return result

    def read(self, path, method, *args, **kwargs):
        path = Path(path)
        if not self.active:
            return (self.real_read_bytes if method == "bytes" else self.real_read_text)(path, *args, **kwargs)
        self.record("Path.read_" + method, path, *args, **kwargs)
        self.read_counts[str(path)] += 1
        schedule = self.values["read_schedule"]
        target = self.chain if schedule.startswith("wrapper") else self.source if schedule.startswith("source") else self.night / "receipt.json"
        if path == target and self.read_counts[str(path)] == 2 and schedule != "stable":
            self.record("scheduled_change", schedule, path)
            if schedule == "wrapper_removed_on_second_read":
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(b"changed between reads\n")
        if path.exists() and not path.stat().st_mode & stat.S_IRUSR:
            raise PermissionError(13, "Permission denied", str(path))
        return (self.real_read_bytes if method == "bytes" else self.real_read_text)(path, *args, **kwargs)

    def cleanup(self, path):
        self.record("cleanup_record", path)
        return {"cleanup_proven": self.values["cleanup"] == "proven"}

    def worker(self, *args):
        # Only test dispatch here: the evidence sampler is never executed.
        self.record("evidence_probe_worker", *args)
        return 0

    def patches(self):
        stack = ExitStack()
        stack.enter_context(patch.object(subprocess, "run", self.shell))
        stack.enter_context(patch.object(subprocess, "Popen", side_effect=HarnessError("Popen prohibited")))
        stack.enter_context(patch.object(time, "time", return_value=NOW))
        stack.enter_context(patch.object(time, "time_ns", return_value=int(NOW * 1e9)))
        stack.enter_context(patch.object(time, "monotonic", return_value=123.0))
        stack.enter_context(patch.object(time, "monotonic_ns", return_value=123000000000))
        for module in (self.en, self.rn, self.campaign, self.inst):
            if hasattr(module, "datetime"):
                stack.enter_context(patch.object(module, "datetime", FrozenDatetime))
        stack.enter_context(patch.object(time, "sleep", side_effect=HarnessError("real sleep prohibited")))
        stack.enter_context(patch.object(os, "getpid", return_value=4242))
        stack.enter_context(patch.object(os, "getuid", return_value=501))
        stack.enter_context(patch.object(os, "urandom", side_effect=lambda n: bytes(random.randrange(256) for _ in range(n))))
        stack.enter_context(patch.object(os, "kill", side_effect=HarnessError("real process signal prohibited")))
        stack.enter_context(patch.object(os, "killpg", side_effect=HarnessError("real group signal prohibited")))
        stack.enter_context(patch.object(tempfile, "_get_candidate_names", lambda: self.temp_names))
        original_which = shutil.which
        stack.enter_context(patch.object(shutil, "which", side_effect=lambda name, *a, **kw:
            str(FIXTURE / "courier") if name == "claude" else original_which(name, *a, **kw)))
        stack.enter_context(patch.object(self.campaign, "cleanup_record", self.cleanup))
        original_refusal = self.campaign.write_refusal
        def write_refusal(*args, **kwargs):
            self.record("write_refusal", *args, **kwargs)
            return original_refusal(*args, **kwargs)
        stack.enter_context(patch.object(self.campaign, "write_refusal", write_refusal))
        stack.enter_context(patch.object(self.rn, "_evidence_probe_worker", self.worker))
        stack.enter_context(patch.object(self.rn, "REPO_ROOT", self.root))
        stack.enter_context(patch.object(self.rn, "_watchdog_liveness_for_courier", side_effect=self.watchdog))
        stack.enter_context(patch.object(self.rn, "_refresh_courier_lock", side_effect=lambda fd: self.record("refresh_courier_lock", fd)))
        stack.enter_context(patch.object(Path, "read_bytes", lambda p: self.read(p, "bytes")))
        stack.enter_context(patch.object(Path, "read_text", lambda p, *a, **kw: self.read(p, "text", *a, **kw)))
        return stack

    def watchdog(self, plan):
        self.record("watchdog_liveness", plan)
        return FIXTURE / "watchdog.json", "0", "fixture"

    def prepared(self, plan):
        return self.inst.Prepared(plan, self.custody / "night_plan.json", self.root,
            str(self.root / ".venv/bin/python"), self.tracked["configs/launchd/com.joulewise.night.plist.template"].decode(),
            str(FIXTURE / "courier"), str(FIXTURE / "bin"), self.rn.schedule(plan), self.rn.install_spans_for_day)

    def make_seed(self):
        if FIXTURE.exists():
            shutil.rmtree(FIXTURE)
        self.stage.mkdir(parents=True)
        self.clone_files(self.root)
        self.build(self.root)
        plan = self.ng.NightPlan(plan_id=self.fields["plan_id"], receipt_class="DIAGNOSTIC_NO_PACK",
            t0_epoch_s=T0, window_max_s=9000, authored_epoch_s=int(NOW), repo_head=HEAD,
            measurement_root=str(self.root), measurement_head=HEAD, chain_path=str(self.chain),
            chain_sha256_path=str(self.chain) + ".sha256", custody_root=str(self.custody), registration_path=PROTOCOL)
        from joulewise.night_plan_writer import write_night_plan
        write_night_plan(self.plan_path, plan)
        with self.patches():
            self.gen.generate(self.plan_path)
            binding = self.en.sealed_candidate(self.root, self.plan_path)
            identity = self.en.interpreter(self.root)
            render = self.stage / "render"
            render.mkdir()
            for label, raw in self.prepared(plan).render(self.inst.LABELS, require_published=False):
                (render / (label + ".plist")).write_bytes(raw)
                installed = FIXTURE / "home/Library/LaunchAgents" / (label + ".plist")
                installed.parent.mkdir(parents=True, exist_ok=True)
                installed.write_bytes(raw)
        schedule = self.rn.schedule(plan)
        schedule["boundaries"] = {"REQUEST / exit BEFORE": T0 - 1800}
        state = dict(self.fields, schema=self.en.SCHEMA, kind=IDLE, roots_under=str(self.roots),
            t0=T0, head=HEAD, remote="fixture-remote", plan_path=str(self.plan_path),
            attempt=1, prior_candidates=[], steps=[{"step": x, "completed_epoch_s": NOW} for x in STEP_NAMES],
            bindings=binding, interpreter=identity, schedule=schedule, digests={})
        for p in [self.plan_path, self.root / "env/mac-measurement-lock.txt", *self.custody.iterdir(), *render.iterdir()]:
            if p.is_file():
                state["digests"][str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
        dump(self.stage / "prepare.json", state)
        (self.custody / "night_plan.json").write_bytes(self.plan_path.read_bytes())
        self.night.mkdir()
        receipt = dict(schema=self.ng.SCHEMA, receipt_class=plan.receipt_class, plan_id=plan.plan_id,
            verdict="GO", refusal=None, authored_monotonic_ns=1,
            conditions=[dict(condition_id=k, status=status, basis=basis, evidence=[],
                measured={"payload_kind": IDLE} if k == "C5" else {})
                for k, (status, basis) in self.ng.class_table()[plan.receipt_class].items()])
        if self.ng.validate_receipt(receipt):
            raise HarnessError("invalid seed gate receipt")
        dump(self.night / "receipt.json", receipt)
        dump(self.night / "chain.started", {})
        dump(self.night / "result.json", {"verdict": "REFUSED", "plan_id": plan.plan_id})
        (self.night / "courier.sent").write_text("fixture-delivery\n")
        (FIXTURE / "magistrate").mkdir()
        # This import runs ONLY in the oracle seed subprocess. Both evaluators
        # consume these bytes, never the candidate's test-helper definitions.
        from tests.test_night_gate import green_results, QUIET_OBSERVATION
        dump(FIXTURE / "probe-source.json", {"results": [dataclasses.asdict(r) for r in green_results().values()],
                                            "observation": QUIET_OBSERVATION})
        with self.patches():
            bindings = self.inst.evidence_probe_bindings(plan, self.custody / "night_plan.json", str(self.root / ".venv/bin/python"))
        probe = dict(bindings, schema=self.campaign.RECEIPT_SCHEMA, outcome="ok", refusal_code=None,
            started_epoch_s=NOW - 10, finished_epoch_s=NOW - 1, launchd_label=self.inst.probe_label(plan.plan_id),
            verify_only=True, collect_started=False, load_started=False, cleanup_proven=True,
            verify_stdout=["VERIFY_ONLY_OK manifest=" + bindings["manifest_sha256"]])
        dump(self.custody / "night_probe_receipt.json", probe)
        return snapshot(FIXTURE)

    def mutate(self, changes, operation):
        self.values = dict(DEFAULTS, **changes)
        v = self.values
        # Fresh preparation is truly empty. Resume fixtures retain their ledger.
        if operation == "evidence.prepare_fresh":
            for p in (self.roots, self.stages):
                shutil.rmtree(p)
            return
        plan = json.loads(self.plan_path.read_bytes())
        state = json.loads((self.stage / "prepare.json").read_bytes())
        kinds = {"idle": IDLE, "list": [], "object": {}, "integer": 1,
                 "null": None, "unknown": "unknown_kind", "calibration": "calibration"}
        if v["kind"] == "missing":
            state.pop("kind")
        else:
            state["kind"] = kinds[v["kind"]]
        if v["identity"] == "plan_id": plan["plan_id"] = "cal-fixture"
        if v["identity"] == "state_id": state["plan_id"] = "wrong-prefix-20260923-2200"
        if v["identity"] == "head": plan["measurement_head"] = "b" * 40
        if v["identity"] == "binding": state["bindings"]["chain_source_sha256"] = "0" * 64
        pstate = v["plan"]
        if pstate == "missing_keys": plan.pop("chain_path")
        if pstate == "wrong_types": plan["t0_epoch_s"] = []
        if pstate == "wrong_class": plan["receipt_class"] = "REHEARSAL_STUB"
        plan = {"list": [], "object": {}, "scalar": 1, "null": None}.get(pstate, plan)
        raw = (self.plan_path.read_bytes() if pstate == "valid" and v["identity"] not in ("plan_id", "head")
               else json_bytes(plan, pstate))
        if pstate == "nonutf8": raw = b"\xff"
        if pstate == "truncated": raw = b'{"plan_id":'
        for path in (self.plan_path, self.custody / "night_plan.json"):
            if pstate == "missing": path.unlink()
            else: path.write_bytes(raw)
        if pstate != "valid" or v["identity"] in ("plan_id", "head"):
            # Seal the mutated plan so shape/identity validation is reachable.
            state["digests"][str(self.plan_path)] = hashlib.sha256(raw).hexdigest()
        wrapper = self.chain.read_text()
        declaration = "export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\n"
        mutations = {
            "calibration": wrapper.replace(declaration, ""),
            "stripped": wrapper.replace(declaration, ""),
            "duplicate": wrapper + declaration,
            "coexport": wrapper + "export CALIBRATION_LEDGER=fixture\n",
            "unknown": wrapper.replace(declaration, "export NIGHT_PAYLOAD_KIND=unknown_kind\n"),
            "quoted": wrapper.replace(declaration, "export NIGHT_PAYLOAD_KIND='quiet_predicate_evidence'\n"),
            "literal_removed": "\n".join(x for x in wrapper.splitlines() if not x.startswith("export EVIDENCE_CHAIN_SOURCE_SHA256=")) + "\n",
            "literal_changed": wrapper.replace(hashlib.sha256(self.tracked[CHAIN]).hexdigest(), "0" * 64),
            "tampered": wrapper + "# changed bytes\n",
            "bare_idle": "export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence\n",
            "bare_stripped": "#!/bin/zsh\n",
        }
        wrapper = mutations.get(v["wrapper"], wrapper)
        encoding = v["wrapper_encoding"]
        raw = wrapper.encode({"bom": "utf-8-sig", "utf16": "utf-16", "utf16le": "utf-16-le", "utf16be": "utf-16-be"}.get(encoding, "utf8"))
        if encoding == "nonutf8": raw = b"\xff"
        if encoding == "truncated": raw = b"\xe2\x82"
        self.chain.write_bytes(raw)
        for axis, path in (("sidecar", Path(str(self.chain) + ".sha256")),
                           ("source_sidecar", Path(str(self.chain) + ".chain-source.sha256"))):
            value = v[axis]
            if value == "resealed": path.write_text(hashlib.sha256(raw).hexdigest() + "  chain.zsh\n")
            elif value == "mismatch": path.write_text("0" * 64 + "  " + ("chain.zsh" if axis == "sidecar" else Path(CHAIN).name) + "\n")
            elif value == "wrong_name": path.write_text(path.read_text().split()[0] + "  wrong.zsh\n")
            elif value == "malformed": path.write_text("not a digest extra tokens\n")
            elif value == "nonutf8": path.write_bytes(b"\xff")
            elif value in ("missing", "directory", "symlink", "unreadable"): self.file_state(path, value)
        self.file_state(self.chain, v["wrapper_file"])
        src = v["source"]
        if src == "modified": self.source.write_bytes(self.source.read_bytes() + b"# drift\n")
        elif src == "nonutf8": self.source.write_bytes(b"\xff")
        elif src == "moved": self.source.rename(self.source.with_suffix(".moved"))
        elif src in ("absent", "directory", "symlink", "unreadable"):
            self.file_state(self.source, "missing" if src == "absent" else src)
        if v["clone"] in ("absent", "archived"):
            shutil.rmtree(self.root)
        elif v["clone"] == "moved":
            self.root.rename(self.root.with_name(self.root.name + "-moved"))
        manifest = self.custody / "evidence_manifest.json"
        if v["manifest"] == "altered":
            m = json.loads(manifest.read_bytes()); m["measurement_head"] = "b" * 40; dump(manifest, m)
        elif v["manifest"] == "malformed": manifest.write_bytes(b"{")
        elif v["manifest"] == "nonutf8": manifest.write_bytes(b"\xff")
        elif v["manifest"] in ("missing", "directory", "symlink", "unreadable"): self.file_state(manifest, v["manifest"])
        receipt = json.loads((self.night / "receipt.json").read_bytes())
        c5 = next(r for r in receipt["conditions"] if r["condition_id"] == "C5")
        if v["c5"] == "fail":
            c5["status"] = "FAIL"; receipt["verdict"] = "REFUSED"
            receipt["refusal"] = {"reason": "night_chain_digest_mismatch", "detail": "fixture", "evidence": []}
        elif v["c5"] == "absent": receipt["conditions"].remove(c5)
        elif v["c5"] == "missing_kind": c5["measured"] = {}
        elif v["c5"] != "idle": c5["measured"]["payload_kind"] = {"none": None, "calibration": "calibration", "unknown": "unknown_kind", "conflict": "calibration"}[v["c5"]]
        if v["receipt"] == "invalid_schema": receipt["schema"] = "wrong"
        elif v["receipt"] == "plan_id": receipt["plan_id"] = "other-plan"
        elif v["receipt"] == "missing_fields": receipt.pop("verdict")
        elif v["receipt"] == "wrong_types": receipt["conditions"] = {}
        receipt = {"list": [], "object": {}, "scalar": 1, "null": None}.get(v["receipt"], receipt)
        enc = v["receipt_encoding"]
        for path, value in ((self.night / "receipt.json", receipt),
                            (self.custody / "night_probe_receipt.json", json.loads((self.custody / "night_probe_receipt.json").read_bytes()))):
            if path.name == "night_probe_receipt.json":
                if v["receipt"] == "invalid_schema": value["schema"] = "wrong"
                elif v["receipt"] == "plan_id": value["plan_id"] = "other-plan"
                elif v["receipt"] == "missing_fields": value.pop("outcome")
                elif v["receipt"] == "wrong_types": value["finished_epoch_s"] = []
                value = {"list": [], "object": {}, "scalar": 1, "null": None}.get(v["receipt"], value)
                if isinstance(value, dict): value["cleanup_proven"] = v["cleanup"] == "proven"
            if enc == "absent": path.unlink()
            else: path.write_bytes(b"\xff" if enc == "nonutf8" else b'{"a":' if enc == "truncated" else json_bytes(value, enc))
        if v["started"] == "absent": (self.night / "chain.started").unlink()
        if v["outcome"] != "absent":
            outcome = {"outcome": v["outcome"], "cleanup_proven": True, "error": "prior refusal"}
            outcome = {"list": [], "object": {}}.get(v["outcome"], outcome)
            (self.night / "evidence_outcome.json").write_bytes(b"\xff" if v["outcome"] == "nonutf8" else b"{" if v["outcome"] == "malformed" else json_bytes(outcome))
        if v["refusal"] == "present": dump(self.night / "refusal.json", {"fixture": "existing refusal"})
        prep = v["prepare"]
        if prep == "missing_digests": state["digests"] = {}
        elif prep == "no_steps": state["steps"] = []
        elif prep == "bad_steps": state["steps"] = [{"step": "unknown"}]
        elif prep in STEP_NAMES[:-1]: state["steps"] = state["steps"][:STEP_NAMES.index(prep) + 1]
        state = {"list": [], "object": {}, "scalar": 1}.get(prep, state)
        path = self.stage / "prepare.json"
        if prep == "missing": path.unlink()
        else: path.write_bytes(b"{" if prep == "malformed" else b"\xff" if prep == "nonutf8" else json_bytes(state, prep))
        # Generation starts with no generated outputs; altered existing wrapper
        # cases still test overwrite/refusal precedence.
        if operation == "generator.render_only" and all(v[a] == DEFAULTS[a] for a in ("wrapper", "wrapper_file", "wrapper_encoding", "sidecar", "source_sidecar", "manifest")):
            for path in (self.chain, Path(str(self.chain) + ".sha256"), Path(str(self.chain) + ".chain-source.sha256"), manifest):
                path.unlink()
        if operation == "driver.refusal_result": (self.night / "result.json").unlink()
        if operation == "installer.render":
            shutil.rmtree(self.night)
            self.night.mkdir()
        if operation == "evidence.prepare":
            # A completed resume must have unpublished custody and empty night.
            (self.custody / "night_plan.json").unlink(missing_ok=True)
            (self.custody / "night_probe_receipt.json").unlink(missing_ok=True)
            shutil.rmtree(self.night)
            self.night.mkdir()

    @staticmethod
    def file_state(path, value):
        if value in ("regular", "intact"): return
        if value == "unreadable": path.chmod(0); return
        raw = path.read_bytes()
        path.unlink()
        if value == "directory": path.mkdir()
        elif value == "symlink":
            target = path.with_name(path.name + ".target"); target.write_bytes(raw); path.symlink_to(target)
        elif value == "dangling": path.symlink_to(path.with_name(path.name + ".absent"))

    def gate(self, plan, operation):
        source = json.loads((FIXTURE / "probe-source.json").read_bytes())
        responses = {tuple(r["argv"]): self.ng.ProbeResult(**dict(r, argv=tuple(r["argv"]))) for r in source["results"]}
        def read(path):
            self.record("probe.read_text", path)
            return Path(path).read_text()
        def run(argv):
            self.record("probe.run", argv)
            if "show" in argv:
                return self.ng.ProbeResult(tuple(argv), 0, self.tracked[argv[-1].split(":", 1)[1]].decode(), "", 1)
            if tuple(argv) not in responses:
                raise HarnessError("no oracle response for probe: " + repr(argv))
            return responses[tuple(argv)]
        def observe():
            self.record("probe.observe_interval")
            return source["observation"]
        def fixed(name, value, *args):
            self.record("probe." + name, *args)
            return value
        probes = self.ng.Probes(run=run, read_text=read, now_epoch_s=lambda: fixed("now_epoch_s", T0),
            monotonic_ns=lambda: fixed("monotonic_ns", 99000), checkout_head=lambda: fixed("checkout_head", HEAD),
            measurement_head=lambda root: fixed("measurement_head", HEAD, root),
            observe_interval=observe)
        rows = self.ng._initial_conditions(plan.receipt_class)
        evidence = []
        result = self.ng._check_chain_identity(plan, probes, rows, evidence)
        if operation == "gate.C3" and result is None:
            c5 = self.values["c5"]
            if c5 in ("none", "missing_kind", "absent"):
                rows["C5"].measured.pop("payload_kind", None)
            elif c5 in ("calibration", "unknown", "conflict"):
                rows["C5"].measured["payload_kind"] = "unknown_kind" if c5 == "unknown" else "calibration"
            elif c5 == "fail": rows["C5"].status = "FAIL"
            result = self.ng._check_census(plan, probes, rows, evidence)
            if result is None: result = self.ng._check_machine(plan, probes, rows, evidence)
        return {"receipt": result, "conditions": self.ng._conditions_tuple(rows)}

    def invoke(self, op):
        en, rn, ng = self.en, self.rn, self.ng
        if op in ("evidence.prepare", "evidence.prepare_fresh"):
            kind = {"idle": IDLE, "list": [], "object": {}, "integer": 1, "null": None,
                    "unknown": "unknown_kind", "calibration": "calibration", "missing": None}[self.values["kind"]]
            return en.prepare(kind=kind, t0=str(T0), head=HEAD, remote="fixture-remote",
                roots_under=self.roots, staging_under=self.stages, builder=self.build)
        if op == "evidence.candidate_state": return en.candidate_state(self.stage)
        if op == "evidence.sealed_candidate": return en.sealed_candidate(self.root, self.plan_path)
        if op == "generator.render_only":
            args = ["--plan", str(self.plan_path), "--render-only"]
            if self.values["template"] == "alternate": args.extend(("--chain-template", "custom.zsh"))
            return self.gen.main(args)
        if op == "installer.uninstall":
            return en.uninstall(candidate=self.stage, launchctl_bin=str(FIXTURE / "fake-launchctl"), runner=self.text_runner)
        if op == "installer.veto": return en.veto(candidate=self.stage, runner=self.text_runner, magistrate=FIXTURE / "magistrate")
        if op == "installer.verify": return en.verify(candidate=self.stage, launchctl_bin=str(FIXTURE / "fake-launchctl"))
        if op.startswith("evidence."):
            state = json.loads((self.stage / "prepare.json").read_bytes())
            if op.startswith("evidence.sealed_state"):
                return en.sealed_state(state, published=op.endswith("published"))
            if op == "evidence.notice_subject": return en.notice_subject(state)
            if op == "evidence.render_notice": return en.render_notice(state)
            if op == "evidence.notice_unused": return en.notice_unused(state, "fixture-notice")
            if op == "evidence.clone_census": return en.clone_census(state, 4242, argv_only=True)
            if op == "evidence.candidate_payload_kind": return en.candidate_payload_kind(state)
        if op == "driver.probe_dispatch":
            # A calibration branch must stop at the external worker boundary too.
            def bindings(*args, **kwargs):
                self.record("calibration_probe_bindings", *args, **kwargs)
                raise RuntimeError("fixture calibration worker boundary")
            with patch.object(self.inst, "probe_bindings", bindings):
                return rn._probe_worker(self.plan_path, self.night / "probe.json", self.night / "progress.json", 723.0)
        plan = ng.NightPlan.from_mapping(json.loads(self.plan_path.read_bytes()))
        if op.startswith("gate."): return self.gate(plan, op)
        if op == "installer.render":
            args = SimpleNamespace(plan=self.plan_path, python=str(self.root / ".venv/bin/python"),
                render_only=FIXTURE / "installer-render", hour=None, minute=None)
            prepared = self.inst.validate_install(args, self.root)
            return list(prepared.render(self.inst.LABELS, require_published=False)) + [self.inst.render_probe(prepared)]
        if op == "installer.receipt_validation": return self.inst.validate_probe_receipt(self.prepared(plan))
        if op == "driver.artifact_list": return rn._artifact_list(self.custody, self.night)
        if op == "driver.refusal_result":
            return rn._write_standard_refusal_result(self.custody, self.night, plan,
                rn._CODES["chain_digest_mismatch"], "x", NOW - 10, 12345000)
        if op == "driver.cleanup": return rn._evidence_cleanup_error(plan, self.night)
        if op == "driver.courier_argv": return rn._courier_argv(self.custody, plan, FIXTURE / "courier")
        if op == "driver.durable_record": return rn._durable_record(self.custody, self.night, plan)
        if op == "driver.courier_cleanup":
            report = dict(prepared=False, diagnostics=[], facts={}, result_unavailable=False)
            argv = rn._courier_prelaunch(self.custody, plan, FIXTURE / "courier", 17, report)
            return {"argv": argv, "report": report}
        if op == "zero_capture_facts":
            facts = self.zero(plan)
            return {"facts": facts, "clean": facts.clean}
        if op == "diagnostic.custody_row":
            if not hasattr(rn, "_custody_row"): return {"api": "absent_at_base"}
            return {"api": "present", "kind": rn._custody_row(plan).kind}
        raise HarnessError("unknown operation " + op)

    def text_runner(self, argv, **kwargs):
        return self.shell(argv, text=True, **kwargs)

    def evaluate(self, job, seed):
        op = job["operation"]
        profile = op if op in ("evidence.prepare", "evidence.prepare_fresh", "generator.render_only", "driver.refusal_result", "installer.render") else "regular"
        key = profile, tuple(sorted(job["changes"].items()))
        self.values = dict(DEFAULTS, **job["changes"])
        before = self.before_cache.get(key)
        if before is None:
            restore(FIXTURE, seed, getattr(self, "last_tree", None))
            self.mutate(job["changes"], op)
            before = snapshot(FIXTURE)
            self.before_cache[key] = before
        else:
            restore(FIXTURE, before, getattr(self, "last_tree", None))
        self.calls, self.read_counts = [], Counter()
        random.seed(SEED)
        out, err = io.StringIO(), io.StringIO()
        result = {"id": job["id"], "operation": job["operation"], "changes": job["changes"], "fixture_root": str(FIXTURE)}
        self.temp_names = (f"p{n:07d}" for n in itertools.count())
        self.active = True
        with redirect_stdout(out), redirect_stderr(err):
            try:
                result["return"] = encode(self.invoke(job["operation"]))
                result["exception"] = None
            except (Exception, SystemExit) as exc:
                result["return"] = None
                result["exception"] = {"class": type(exc).__module__ + "." + type(exc).__qualname__,
                    "message": str(exc), "args": encode(exc.args),
                    "refusal_code": encode(getattr(exc, "refusal_code", getattr(exc, "reason", getattr(exc, "code", None)))),
                    "evidence": encode(getattr(exc, "evidence", None))}
            finally:
                self.active = False
        self.last_tree = snapshot(FIXTURE)
        result.update(stdout=out.getvalue(), stderr=err.getvalue(), calls=self.calls,
                      files=file_delta(before, self.last_tree))
        return result


def fence(event, args):
    if event in ("subprocess.Popen", "os.system", "os.fork", "os.posix_spawn", "os.kill", "os.killpg") or event.startswith("os.exec"):
        raise HarnessError("external execution prohibited: " + event)
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        path = os.fsdecode(args[0])
        if any(path.startswith(p) for p in ("/Users/edr/night-custody", "/Users/edr/JouleWise-measurement-", "/Users/edr/Library/LaunchAgents", "/Users/edr/code/JouleWise/")):
            raise HarnessError("forbidden read/write: " + path)
        mode, flags = args[1], args[2]
        writing = isinstance(mode, str) and any(c in mode for c in "wax+") or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)
        if writing and not str(Path(path).absolute()).startswith(str(SCRATCH) + "/b0par-") and not str(Path(path).absolute()).startswith(str(SCRATCH.resolve()) + "/b0par-"):
            raise HarnessError("write escaped scratch: " + path)


def worker(args):
    # Candidate tests cannot shadow this support module. Only oracle seeding
    # imports FakeProbeSource's fixture data; evaluators consume the saved bytes.
    sys.path.insert(0, str(Path(args.worker).resolve()))
    os.environ.update(TZ="UTC", PYTHONDONTWRITEBYTECODE="1")
    time.tzset() if hasattr(time, "tzset") else None
    os.umask(0o022)
    sys.addaudithook(fence)
    world = World(args.oracle)
    if args.make_seed:
        dump(args.make_seed, world.make_seed())
        return 0
    seed = json.loads(Path(args.seed_file).read_bytes())
    selected = json.loads(Path(args.jobs_file).read_bytes())
    with gzip.open(args.records, "wt", compresslevel=1) as stream, world.patches():
        for index, job in enumerate(selected):
            record = world.evaluate(job, seed)
            stream.write(json.dumps(record, sort_keys=True) + "\n")
            if (index + 1) % 1000 == 0:
                print(f"slot={SLOT} observations={index + 1}/{len(selected)}", flush=True)
    print(f"slot={SLOT} observations={len(selected)}/{len(selected)} DONE", flush=True)
    return 0


def differences(base, candidate, path=""):
    if type(base) is type(candidate) and base == candidate:
        return
    if type(base) is not type(candidate):
        yield path or "$", base, candidate
    elif isinstance(base, dict):
        for key in sorted(base.keys() | candidate.keys()):
            p = path + "." + key if path else key
            if key not in base or key not in candidate:
                yield p, {"present": key in base, "value": base.get(key)}, {"present": key in candidate, "value": candidate.get(key)}
            else:
                yield from differences(base[key], candidate[key], p)
    elif isinstance(base, list):
        # Compare the full ordered list; never sort or suppress calls.
        if base != candidate: yield path, base, candidate
    elif base != candidate:
        yield path, base, candidate


def compare(base_path, candidate_path, output):
    inventory, counts, refusal_sets = defaultdict(list), Counter(), [set(), set()]
    authority_failures = []
    mismatch_count = semantic_count = diagnostic_count = total = 0
    with gzip.open(base_path, "rt") as left, gzip.open(candidate_path, "rt") as right, \
            gzip.open(output / "diffs.jsonl.gz", "wt", compresslevel=1) as full:
        for a, b in itertools.zip_longest(left, right):
            if a is None or b is None: raise HarnessError("missing worker output")
            base, candidate = json.loads(a), json.loads(b)
            if (base["id"], base["operation"], base["changes"]) != (candidate["id"], candidate["operation"], candidate["changes"]):
                raise HarnessError("worker case alignment failure")
            total += 1; counts[base["operation"]] += 1
            for index, row in enumerate((base, candidate)):
                if row["exception"] and "Refused" in row["exception"]["class"]:
                    refusal_sets[index].add(row["exception"]["message"])
            delta = list(differences(base, candidate))
            if not delta: continue
            mismatch_count += 1
            fields = sorted({p.split(".")[0] for p, _, _ in delta})
            diagnostic = base["operation"].startswith("diagnostic.")
            changes = candidate["changes"]
            authority_failure = (diagnostic and changes.get("sidecar") == "missing"
                and changes.get("source") == "absent" and changes.get("receipt_encoding") == "absent"
                and isinstance(candidate["return"], dict) and "kind" in candidate["return"])
            if authority_failure:
                authority_failures.append(candidate["id"])
            semantic = fields != ["calls"] and not diagnostic
            diagnostic_count += diagnostic; semantic_count += semantic
            row = {"id": base["id"], "changes": base["changes"], "fields": fields,
                   "classification": "unauthenticated_selection" if authority_failure else "new_private_api" if diagnostic else "outcome" if semantic else "dependency_calls"}
            inventory[base["operation"]].append(row)
            full.write(json.dumps(dict(row, operation=base["operation"], differences=delta), sort_keys=True) + "\n")
    dump(output / "inventory.json", inventory)
    with (output / "inventory.md").open("w") as f:
        f.write("# Exact B0 differential inventory\n\nNo differences are suppressed. Exact values: diffs.jsonl.gz; full observations: base/candidate.jsonl.gz.\n")
        for op, rows in sorted(inventory.items()):
            f.write(f"\n## {op} ({len(rows)})\n\n")
            for row in rows:
                f.write(f"- `{row['id']}`: {', '.join(row['fields'])} ({row['classification']}); `{json.dumps(row['changes'], sort_keys=True)}`\n")
    summary = dict(seed=SEED, observations=total, mismatches=mismatch_count,
        parity_mismatches=mismatch_count - diagnostic_count,
        authority_failures=authority_failures,
        outcome_mismatches=semantic_count, new_private_api=diagnostic_count,
        coverage=dict(sorted(counts.items())), grouped_diffs={op: len(rows) for op, rows in sorted(inventory.items())},
        new_refusal_texts=sorted(refusal_sets[1] - refusal_sets[0]))
    return summary


def parity_failed(summary):
    """New-private-API diagnostics have no legacy entry point to compare."""
    return summary["mismatches"] > summary["new_private_api"] or bool(summary.get("authority_failures"))


def shrink_changes(changes, still_fails):
    """Deterministic deletion shrink to a 1-minimal cross-axis witness."""
    current, history = dict(changes), []
    again = True
    while again:
        again = False
        for axis in sorted(current):
            trial = {k: v for k, v in current.items() if k != axis}
            retained = still_fails(trial)
            history.append({"removed": axis, "still_fails": retained})
            if retained:
                current = trial
                again = True
                break
    return current, history


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", default=str(REPO))
    parser.add_argument("--candidate-ref")
    parser.add_argument("--self", action="store_true")
    parser.add_argument("--output", default=str(SCRATCH / "b0par-results"))
    parser.add_argument("--case", help="case-id substring (all by default)")
    parser.add_argument("--operation", help="exact operation (all by default)")
    parser.add_argument("--shrink", action="store_true", help="requires one exact case and operation; deletion-shrink its outcome difference")
    parser.add_argument("--workers", type=int, default=4, help="offline Python evaluators with disjoint fixture paths (default: 4)")
    parser.add_argument("--worker")
    parser.add_argument("--oracle")
    parser.add_argument("--make-seed")
    parser.add_argument("--seed-file")
    parser.add_argument("--jobs-file")
    parser.add_argument("--records")
    args = parser.parse_args(argv)
    if args.worker: return worker(args)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    # Serialize invocations: identical fixture paths are intentional and must
    # never be evaluated by two runner processes concurrently.
    import fcntl
    with (SCRATCH / "b0par-runner.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        started = time.perf_counter()
        output = safe_scratch(args.output); output.mkdir(exist_ok=True)
        # Immutable support snapshot: both sides use precisely the same source
        # even if a user edits the working tree while a long replay is running.
        support_hashes = {}
        for source in (HERE, HERE.with_name("b0_corpus.py")):
            raw = source.read_bytes()
            (output / source.name).write_bytes(raw)
            support_hashes[source.name] = hashlib.sha256(raw).hexdigest()
        oracle = archive(BASE, SCRATCH / "b0par-base")
        candidate = oracle if args.self else archive(args.candidate_ref, SCRATCH / "b0par-candidate") if args.candidate_ref else Path(args.candidate).resolve()
        selected = [j for j in jobs() if (not args.case or args.case in j["id"]) and (not args.operation or args.operation == j["operation"])]
        if not selected: raise ValueError("filter selected zero jobs")
        if args.shrink and len(selected) != 1:
            raise ValueError("--shrink requires exactly one case/operation")
        if not 1 <= args.workers <= 8: raise ValueError("workers must be between 1 and 8")
        workers = min(args.workers, len(selected))
        dump(output / "jobs.json", selected)
        env = dict(PATH="/usr/bin:/bin:/usr/sbin:/sbin", PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0", TZ="UTC",
                   LC_ALL="C", LANG="C")
        def run(tree, extra, slot=0):
            fixture = (SCRATCH / f"b0par-fixture-{slot}").resolve()
            subprocess.run([sys.executable, "-B", str(output / HERE.name), "--worker", str(tree), "--oracle", str(oracle), *extra],
                env=dict(env, PYTHONPATH=str(tree), B0_PARITY_SLOT=str(slot), TMPDIR=str(fixture), HOME=str(fixture / "home")), cwd=tree, check=True)
        def evaluate_slot(label, tree, slot):
            run(tree, ["--seed-file", str(output / f"seed-{slot}.json"), "--jobs-file", str(output / f"jobs-{slot}.json"),
                       "--records", str(output / f"{label}-{slot}.jsonl.gz")], slot)
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pending = []
            for slot in range(workers):
                dump(output / f"jobs-{slot}.json", selected[slot::workers])
                pending.append(pool.submit(run, oracle, ["--make-seed", str(output / f"seed-{slot}.json")], slot))
            for future in pending: future.result()
            for label, tree in (("base", oracle), ("candidate", candidate)):
                print("SIDE " + label, flush=True)
                pending = [pool.submit(evaluate_slot, label, tree, slot) for slot in range(workers)]
                for future in pending: future.result()
                # Reassemble original case order, never sorting observable calls.
                with ExitStack() as streams, gzip.open(output / f"{label}.jsonl.gz", "wt", compresslevel=1) as merged:
                    readers = [streams.enter_context(gzip.open(output / f"{label}-{slot}.jsonl.gz", "rt")) for slot in range(workers)]
                    for index in range(len(selected)):
                        line = readers[index % workers].readline()
                        if not line: raise HarnessError("missing shard observation")
                        merged.write(line)
                    if any(r.readline() for r in readers): raise HarnessError("extra shard observation")
        summary = compare(output / "base.jsonl.gz", output / "candidate.jsonl.gz", output)
        if args.shrink and summary["mismatches"]:
            def first(path):
                with gzip.open(path, "rt") as stream:
                    return json.loads(next(stream))
            original = list(differences(first(output / "base.jsonl.gz"), first(output / "candidate.jsonl.gz")))
            desired = {p.split(".")[0] for p, _, _ in original} - {"calls"}
            if not desired: desired = {"calls"}
            def still_fails(changes):
                trial = dict(selected[0], changes=changes)
                dump(output / "shrink-jobs.json", [trial])
                for label, tree in (("base", oracle), ("candidate", candidate)):
                    run(tree, ["--seed-file", str(output / "seed-0.json"), "--jobs-file", str(output / "shrink-jobs.json"),
                               "--records", str(output / ("shrink-" + label + ".jsonl.gz"))])
                delta = differences(first(output / "shrink-base.jsonl.gz"), first(output / "shrink-candidate.jsonl.gz"))
                return desired.issubset({p.split(".")[0] for p, _, _ in delta})
            minimal, history = shrink_changes(selected[0]["changes"], still_fails)
            still_fails(minimal)  # retain the final minimized observation pair
            dump(output / "minimized.json", dict(selected[0], changes=minimal, deletion_history=history, retained_fields=sorted(desired)))
        summary.update(runtime_seconds=round(time.perf_counter() - started, 3), oracle=str(oracle), candidate=str(candidate),
                       harness_sha256=support_hashes, corpus_cases=len(corpus()),
                       workers=workers,
                       isolated_pair_cases=sum(c["id"].startswith("pair.") for c in corpus()))
        dump(output / "summary.json", summary)
        for op, count in summary["grouped_diffs"].items(): print(f"DIFF {op}: {count}")
        print(f"seed={SEED} observations={summary['observations']} mismatches={summary['mismatches']}")
        print(f"outcome_mismatches={summary['outcome_mismatches']} new_private_api={summary['new_private_api']}")
        print(f"shared_surface_mismatches={summary['parity_mismatches']}")
        print(f"authority_failures={len(summary['authority_failures'])}")
        print("inventory=" + str(output / "inventory.md"))
        print(f"runtime_seconds={summary['runtime_seconds']:.3f}")
        print("PARITY FAIL" if parity_failed(summary) else "PARITY PASS")
        return int(parity_failed(summary))


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except HarnessError as error:
        print("HARNESS ERROR: " + str(error), file=sys.stderr)
        raise SystemExit(3)
