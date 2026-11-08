"""Synthetic v4 release rehearsal: both builds at their pinned commits, one common series. No real data.

The two builds live on their own branches. They are extracted from this repository's object store with
``git archive`` at the pinned commits (``ENGINE_COMMIT``, ``RECOMPUTE_COMMIT``) into a private temporary
tree, and run as subprocesses; nothing here imports either build. When the objects are absent (a shallow
clone), the dependent tests skip.

``rehearsal(plan)`` writes the common series (``common_series.write_series``), runs the recompute and the
engine (calibration-only, freeze, then the full run against the freeze, as ENGINE-sol.md prescribes) and
writes the engine run record. Results are cached per process and, read-only, across processes under the
system temporary folder, keyed by the commits, the generator bytes and the plan.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import common_series  # noqa: E402

ENGINE_COMMIT = "a2e36bc19e7e46de1c21890e884393d6bd06154f"      # origin/engine-r23d (R21 + A37 + R23 + R23c/d contract)
RECOMPUTE_COMMIT = "fdd02a96bbe1b90817c6c738190c1816e89a06b3"   # align/2026-11-08-v4-recompute-opus (R23 + R23c/d contract)
PY = sys.executable
_TREES = {}


def have_commits():
    for c in (ENGINE_COMMIT, RECOMPUTE_COMMIT):
        r = subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", c + "^{commit}"], capture_output=True)
        if r.returncode:
            return False
    return True


def tree(commit):
    """The build tree at a pinned commit, extracted once per process."""
    if commit not in _TREES:
        base = Path(tempfile.mkdtemp(prefix="jw-v4-tree-"))
        archive = subprocess.run(["git", "-C", str(REPO), "archive", commit], capture_output=True, check=True).stdout
        subprocess.run(["tar", "-x", "-C", str(base)], input=archive, check=True)
        _TREES[commit] = base
    return _TREES[commit]


def synth_module():
    path = tree(RECOMPUTE_COMMIT) / "tests" / "independent_recompute_v4" / "synth.py"
    spec = importlib.util.spec_from_file_location("v4_recompute_synth", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def run_engine(root, *, input_name="engine-input.json", out="engine-out", tree_dir=None, workers=1):
    """Engine calibration-only, then the full run against that freeze. Returns (exit, verdict)."""
    eng = tree_dir or tree(ENGINE_COMMIT)
    cli = str(eng / "scripts" / "analyze_align_v4.py")
    cal, full = root / (out + "-cal"), root / out
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([PY, "-B", cli, "--input", input_name, "--output", cal.name, "--calibration-only",
                        "--workers", str(workers)], cwd=root, capture_output=True, env=env)
    if r.returncode:
        return r.returncode, json.loads(r.stdout or b"{}")
    r = subprocess.run([PY, "-B", cli, "--input", input_name, "--output", full.name, "--thresholds",
                        str(cal / "thresholds.json"), "--workers", str(workers)], cwd=root, capture_output=True, env=env)
    return r.returncode, json.loads(r.stdout or b"{}")


def write_record(root, out="engine-out", input_name="engine-input.json", commit=ENGINE_COMMIT):
    full = root / out
    record = dict(schema="joulewise.v4_engine_run_record.v1", engine_commit=commit,
                  input_sha256=sha256(root / input_name), fill_sha256=sha256(full / "fill.json"),
                  verdict_sha256=sha256(full / "verdict.json"), thresholds_sha256=sha256(full / "thresholds.json"))
    (root / "engine-run-record.json").write_text(json.dumps(record, sort_keys=True) + "\n")
    return root / "engine-run-record.json"


def run_recompute(root, out="recompute-out.json", tree_dir=None, workers=4):
    rec = tree_dir or tree(RECOMPUTE_COMMIT)
    r = subprocess.run([PY, "-B", "-I", str(rec / "scripts" / "independent_recompute_v4.py"), "--root",
                        str(root / "recompute"), "--out", str(root / out), "--workers", str(workers)],
                       capture_output=True)
    return r.returncode


def _key(plan_name):
    h = hashlib.sha256()
    for part in (ENGINE_COMMIT, RECOMPUTE_COMMIT, plan_name, (HERE / "common_series.py").read_bytes(),
                 Path(__file__).read_bytes()):
        h.update(part if isinstance(part, bytes) else part.encode())
    return h.hexdigest()[:16]


PLANS = {"full": dict(zero_capture=True, escalated=True, a37=True),
         "probes": dict(zero_capture=True, escalated=True, a37=True, probes=True)}


def rehearsal(plan_name):
    """A finished rehearsal folder (read-only; copy before mutating). Timings in ``timings.json``."""
    cache = Path(tempfile.gettempdir()) / f"jw-v4-rehearsal-{plan_name}-{_key(plan_name)}"
    if (cache / "DONE").exists():
        return cache
    work = Path(tempfile.mkdtemp(prefix=f"jw-v4-rehearsal-{plan_name}-"))
    timings = {}
    t = time.monotonic()
    common_series.write_series(work, synth_module(), plan=common_series.default_plan(**PLANS[plan_name]))
    timings["generate_s"] = time.monotonic() - t
    t = time.monotonic()
    code, verdict = run_engine(work)
    timings["engine_s"] = time.monotonic() - t
    (work / "engine-exit.json").write_text(json.dumps(dict(exit=code, verdict=verdict)) + "\n")
    if code == 0:
        write_record(work)
    t = time.monotonic()
    timings["recompute_exit"] = run_recompute(work)
    timings["recompute_s"] = time.monotonic() - t
    (work / "timings.json").write_text(json.dumps(timings) + "\n")
    (work / "DONE").write_text("")
    try:
        work.rename(cache)
        return cache
    except OSError:      # another process won the race; use its copy
        shutil.rmtree(work, ignore_errors=True)
        return cache


def release_checkout(dest):
    """A clean disposable git checkout holding the release programs and bars (as a release would)."""
    sys.path.insert(0, str(REPO / "tests"))
    from git_fixture import init_git_fixture
    dest = Path(dest)
    for rel in ("scripts/compare_v4_recompute.py", "scripts/release_v4.py", "configs/analysis/v4/recompute_bars.json"):
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / rel, dest / rel)
    init_git_fixture(dest)
    for args in (["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "release"]):
        subprocess.run(["git", "-C", str(dest), *args], check=True, capture_output=True)
    return dest


def run_release(checkout, rehearsal_dir, restricted, *, engine_commit=ENGINE_COMMIT,
                recompute_commit=RECOMPUTE_COMMIT, workers=4, extra=()):
    r = rehearsal_dir
    cmd = [PY, "-B", str(Path(checkout) / "scripts" / "release_v4.py"), "--engine-input", str(r / "engine-input.json"),
           "--engine-out", str(r / "engine-out"), "--engine-record", str(r / "engine-run-record.json"),
           "--engine-commit", engine_commit, "--recompute-root", str(r / "recompute"),
           "--recompute-commit", recompute_commit, "--crosswalk", str(r / "crosswalk.json"),
           "--restricted-out", str(restricted), "--programs-repo", str(REPO), "--workers", str(workers), *extra]
    t = time.monotonic()
    p = subprocess.run(cmd, capture_output=True)
    wall = time.monotonic() - t
    return p.returncode, json.loads(p.stdout or b"{}"), wall


def compare(rehearsal_dir, out, *, fill=None, verdict=None, recompute=None, crosswalk=None, bars=None):
    r = rehearsal_dir
    cmd = [PY, "-B", str(REPO / "scripts" / "compare_v4_recompute.py"),
           "--fill", str(fill or r / "engine-out" / "fill.json"),
           "--verdict", str(verdict or r / "engine-out" / "verdict.json"),
           "--recompute", str(recompute or r / "recompute-out.json"),
           "--crosswalk", str(crosswalk or r / "crosswalk.json"),
           "--bars", str(bars or REPO / "configs" / "analysis" / "v4" / "recompute_bars.json"), "--out", str(out)]
    p = subprocess.run(cmd, capture_output=True)
    return p.returncode, json.loads(p.stdout or b"{}"), (json.loads(Path(out).read_text()) if Path(out).exists() else None)
