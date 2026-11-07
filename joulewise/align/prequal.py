"""Off-measurement-Mac pre-qualification for ALIGN v4 R0/R1/W1 (RUN_STATE item 183).

Scope rule (Ed, 2026-11-06): a check whose PURPOSE is to measure or validate the
measurement Mac itself (SMC/thermal, power, powermode, Metal memory, timing or
throughput, effort-rung selection by speed, decode budgets, peak memory, B7 timing)
stays on the Mac15,9. Only software, model, config and fixture checks run here.

Every check returns a row with a status in STATUSES. The report fails closed: any
``fail`` fails it; any required check that did not run makes it ``incomplete``.
Model-dependent checks take a pluggable backend (see ``SiblingBackend``), so a small
same-architecture model can exercise the production code path on a laptop. Results
from a sibling never qualify D's numerics.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import time
import traceback

REPO = Path(__file__).resolve().parents[2]
SCHEMA = "joulewise.align.v4.prequal.v1"
STATUSES = ("pass", "fail", "diagnostic", "not_run")
D_REPO = "mlx-community/Qwen3.8-27B-8bit"
STACK = {"mlx": "0.31.2", "mlx-lm": "0.31.3", "transformers": "5.12.1"}
PINS_PATH = REPO / "configs/align/v4/qwen38-27b-8bit-hf-pins.json"
REFERENCE_PATH = REPO / "configs/align/v4/prequal_r0_reference.json"
# The sibling's own R0 load NLL entry (mode reference, HF fp32 0.4669), in R0's table format.
SIBLING_NLL_REFERENCE_PATH = REPO / "configs/align/v4/prequal_sibling_nll_reference.json"
SIBLING_NLL_LABEL = "prequal-sibling"
R0_CONFIG_PATH = REPO / "configs/align/v4/r0_desk.json"
ANCHOR_REVISION = "d388dead1515f5e085ef7a0431dd8fadf0886c57"
WEIGHT_PREFIX = "model-"
MAX_DOWNLOAD_BYTES = 2_000_000_000
# Same mlx_lm class (qwen3_5), 8-bit affine gs64, same vocab_size and vocab.json
# blob as D; 24 layers instead of 64. Revision is pinned at first use.
SIBLING_REPO = "mlx-community/Qwen3.5-0.8B-8bit"
SIBLING_REVISION = "87e768fbfa03994095f3d14527c80c5ae70c5758"
TOKENIZER_FILES = ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja", "vocab.json",
                   "merges.txt", "generation_config.json")
EFFORTS = (None, "medium", "low")  # None = template default xhigh (R0 passes no kwarg)

# Checks that measure the Mac itself. Listed so every report states the boundary.
MAC_ONLY = {
    "r0.host": "pmset AC/powermode/thermal, iogpu.wired_limit_mb, hw.memsize on the Mac",
    "r0.host-identity": "hw.model == Mac15,9 and >=128 GiB",
    "r0.disk": "free bytes and D/anchor file hashes on the Mac's own disk",
    "r0.smc": "SMC key enumeration and GPU step response (S_fast/S_slow)",
    "r0.ladder": "effort-rung selection by decode cost on the M3 Max",
    "r0.long-decode": "40,960-position Metal memory growth",
    "r0.memory": "peak Metal memory and swap at the context cap",
    "r0.load (D numerics)": "teacher-forced NLL of the real D weights (needs the 29.5 GB artifact)",
    "r0.generated/checkpoint (D, B7)": "B7 verdict and timing with real D generation",
    "r0.model-load (D)": "loading the real D artifact into Metal memory",
    "launcher.preflight": "AC power and free disk on the Mac",
    "launcher.launch (live)": "LaunchAgent bootstrap, desk fence handoff, Spotlight pause on the Mac",
    "r1.*": "powermode A-B-A, soak, high-power adoption, thermal/deadman/OS-load measurement",
    "w1.w1_disk_gate": "80 GB free and offload re-hash on the Mac's disk (align_v4_session install --w1-disk-config)",
    "w1.install": "launchd census and agent installation on the Mac",
    "w1.disk_snapshot": "statvfs/important-capacity on the Mac",
    "magistrate.census/fence/span": "live process table, desk fence and plan span on the Mac",
}


def digest(ids):
    return hashlib.sha256(json.dumps(ids, separators=(",", ":")).encode()).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_blob_sha1(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


class NullGuard:
    """Prequal is not a measurement: there is no census to pass on this host."""

    receipts = []

    def check(self, *, force=False):
        return None


# --------------------------------------------------------------------------- context


class Context:
    """Shared, lazily-built inputs. Everything heavy is cached per run."""

    def __init__(self, *, repo=REPO, work=None, hf_cache=None, stage="r0", python_bin=None,
                 launcher=None, launcher_ref=None, model_backend="none", sibling_repo=SIBLING_REPO,
                 sibling_revision=SIBLING_REVISION, generated_transitions=12, offline=False,
                 r0_report=None, hf_api=None, stack=None):
        self.repo = Path(repo)
        self.work = Path(work or tempfile.mkdtemp(prefix="jwprequal-"))
        self.hf_cache = Path(hf_cache or self.work / "hf")
        self.stage = stage
        self.python_bin = python_bin or sys.executable
        self.launcher, self.launcher_ref = launcher, launcher_ref
        self.model_backend = model_backend
        self.sibling_repo, self.sibling_revision = sibling_repo, sibling_revision
        self.generated_transitions = generated_transitions
        self.offline = offline
        self.r0_report = r0_report
        self._hf_api = hf_api
        self.stack = dict(STACK if stack is None else stack)
        self._cache = {}

    def once(self, key, fn):
        """Build each shared input once; a failure is cached and re-raised, not retried."""
        if key not in self._cache:
            try:
                self._cache[key] = (True, fn())
            except Exception as exc:
                self._cache[key] = (False, exc)
        ok, value = self._cache[key]
        if not ok:
            raise RuntimeError(f"shared input {key!r} unavailable: {type(value).__name__}: {value}") from value
        return value

    def pins(self):
        return json.loads((self.repo / PINS_PATH.relative_to(REPO)).read_text())

    def reference(self):
        return json.loads((self.repo / REFERENCE_PATH.relative_to(REPO)).read_text())

    def sibling_nll_references(self):
        return json.loads((self.repo / SIBLING_NLL_REFERENCE_PATH.relative_to(REPO)).read_text())

    def hf_api(self):
        if self._hf_api is None:
            from huggingface_hub import HfApi
            self._hf_api = HfApi()
        return self._hf_api

    def tokenizer_dir(self):
        return self.once("tokenizer_dir", lambda: download_non_weights(self))

    def shade_cache(self):
        def fetch():
            from joulewise.align.shade.upstream import PinnedUpstream
            cache = self.work / "shade"
            upstream = PinnedUpstream(cache_dir=cache, allow_fetch=not self.offline)
            if upstream.prepare() is None:
                raise RuntimeError(f"pinned SHADE source unavailable: {upstream.flags}")
            return cache
        return self.once("shade", fetch)

    def tokenizer_backend(self):
        return self.once("tok_backend", lambda: TokenizerBackend(self.tokenizer_dir(), self.shade_cache()))


# --------------------------------------------------------------------------- backends


def _r0_mlx():
    from joulewise.align import r0_mlx
    return r0_mlx


class TokenizerBackend:
    """The production MlxBackend render/encode/task path with no weights.

    Instances are real ``MlxBackend`` objects built without ``__init__`` so that
    ``new_session``, ``render``, ``encode``, ``synthetic_completion`` and ``task``
    are the exact production methods. ``chat``/``nll`` are unavailable.
    """

    def __new__(cls, tokenizer_dir, shade_cache):
        from mlx_lm.tokenizer_utils import load as load_tokenizer
        from mlx_lm.utils import load_config
        from importlib.metadata import version
        from types import SimpleNamespace
        from joulewise.align.shade.upstream import PinnedUpstream
        from joulewise.clock import SystemClock
        r0_mlx = _r0_mlx()
        config = load_config(Path(tokenizer_dir))
        tokenizer = load_tokenizer(Path(tokenizer_dir), {}, eos_token_ids=config.get("eos_token_id"))
        backend = r0_mlx.MlxBackend.__new__(r0_mlx.MlxBackend)
        backend.tag, backend.guard, backend.clock = "D", NullGuard(), SystemClock()
        # Production uses allow_fetch=False against a verified cache; so do we.
        backend.upstream = PinnedUpstream(cache_dir=shade_cache, allow_fetch=False)
        backend.config = r0_mlx.backend_config("D", tokenizer_dir)
        backend.runtime = SimpleNamespace(_tokenizer=tokenizer, _model_config=config)
        backend.prepared = {"model_config_name": config.get("model_type"),
                            "mlx_version": version("mlx"), "mlx_lm_version": version("mlx-lm")}
        backend.tokenizer = tokenizer
        backend.new_session(None)
        return backend


def build_sibling_dir(ctx):
    """Sibling weights + D tokenizer/template, with D's EOS IDs in config.json."""
    from huggingface_hub import snapshot_download
    info = ctx.hf_api().model_info(ctx.sibling_repo, revision=ctx.sibling_revision, files_metadata=True)
    if info.sha != ctx.sibling_revision:
        raise ValueError(f"sibling revision {info.sha} != pinned {ctx.sibling_revision}")
    total = sum(s.size or 0 for s in info.siblings)
    if total > MAX_DOWNLOAD_BYTES:
        raise ValueError(f"sibling artifact {total} bytes exceeds the {MAX_DOWNLOAD_BYTES} byte cap")
    source = Path(snapshot_download(ctx.sibling_repo, revision=ctx.sibling_revision,
                                    cache_dir=str(ctx.hf_cache / "hub")))
    d_dir = ctx.tokenizer_dir()
    hybrid = ctx.work / "sibling-hybrid"
    if hybrid.exists():
        for child in hybrid.iterdir():
            child.unlink()
    hybrid.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.iterdir()):
        if path.name.endswith(".safetensors") or path.name == "model.safetensors.index.json":
            (hybrid / path.name).symlink_to(path.resolve())
    config = json.loads((source / "config.json").read_text())
    d_config = json.loads((d_dir / "config.json").read_text())
    for key in ("model_type",):
        if config.get(key) != d_config.get(key):
            raise ValueError(f"sibling {key} {config.get(key)} != D {d_config.get(key)}")
    for key in ("vocab_size", "model_type"):
        if config.get("text_config", {}).get(key) != d_config.get("text_config", {}).get(key):
            raise ValueError(f"sibling text_config.{key} differs from D")
    if config.get("quantization") != d_config.get("quantization"):
        raise ValueError("sibling quantization differs from D")
    config["eos_token_id"] = d_config.get("eos_token_id")
    (hybrid / "config.json").write_text(json.dumps(config, indent=2, sort_keys=True))
    for name in TOKENIZER_FILES:
        if (d_dir / name).is_file():
            (hybrid / name).symlink_to((d_dir / name).resolve())
    return {"dir": hybrid, "source": str(source), "revision": info.sha, "bytes": total,
            "substitutions": {"config.json:eos_token_id": d_config.get("eos_token_id"),
                              "tokenizer_and_template": "D @ " + ctx.pins()["revision"]},
            "layers": config.get("text_config", {}).get("num_hidden_layers")}


class SiblingBackend:
    """Production MlxBackend over a small same-family model (see build_sibling_dir)."""

    fidelity = ("sibling: exercises the production load/render/NLL/chat/parse/history code path "
                "with D's tokenizer and template; does not qualify D's weights or numerics")

    def __new__(cls, ctx):
        info = build_sibling_dir(ctx)
        backend = _r0_mlx().MlxBackend("D", str(info["dir"]), str(ctx.shade_cache()), NullGuard())
        backend.prequal_sibling = {k: (str(v) if isinstance(v, Path) else v) for k, v in info.items()}
        # The hybrid dir carries D's config revision; the NLL verdict must key on the
        # sibling's own artifact (r0.model_revision), never borrow D's 11.064 entry.
        backend.nll_reference_revision = info["revision"]
        return backend


BACKENDS = {"sibling": SiblingBackend}


# --------------------------------------------------------------------------- HF


def download_non_weights(ctx):
    """Fetch only D's non-weight files at the pinned revision and verify each pin."""
    from huggingface_hub import snapshot_download
    pins = ctx.pins()
    small = {p: v for p, v in pins["files"].items() if not p.startswith(WEIGHT_PREFIX)}
    if sum(v["size"] for v in small.values()) > MAX_DOWNLOAD_BYTES:
        raise ValueError("non-weight files exceed the download cap")
    path = Path(snapshot_download(pins["repo"], revision=pins["revision"], allow_patterns=sorted(small),
                                  cache_dir=str(ctx.hf_cache / "hub"), local_files_only=ctx.offline))
    problems = []
    for name, pin in sorted(small.items()):
        target = path / name
        if not target.is_file():
            problems.append(f"missing {name}")
            continue
        if target.stat().st_size != pin["size"]:
            problems.append(f"size {name}")
        elif pin.get("sha256") and sha256_file(target) != pin["sha256"]:
            problems.append(f"sha256 {name}")
        elif not pin.get("sha256") and git_blob_sha1(target) != pin["git_blob_sha1"]:
            problems.append(f"git blob {name}")
    if problems:
        raise ValueError("D non-weight files do not match pins: " + ", ".join(problems))
    return path


# --------------------------------------------------------------------------- checks


def check_stack(ctx):
    from importlib.metadata import version, PackageNotFoundError
    found = {}
    for dist in (*STACK, "tokenizers", "jinja2", "huggingface_hub"):
        try:
            found[dist] = version(dist)
        except PackageNotFoundError:
            found[dist] = None
    bad = {d: found[d] for d, v in STACK.items() if found[d] != v}
    return {"status": "fail" if bad else "pass", "interpreter": sys.executable, "versions": found,
            "required": STACK, "mismatch": bad,
            "note": "tokenizers is not pinned by the measurement venv contract; recorded only."}


def check_r0_config(ctx):
    from joulewise.align.r0_runner import validate_config
    from joulewise.align.r0_host import step_budget  # PR #692 D3: adaptive idle (idle_max_seconds)
    from scripts import align_v4_kit as kit
    from joulewise.align import r0
    raw = (ctx.repo / "configs/align/v4/r0_desk.json").read_bytes()
    config = validate_config(json.loads(raw))
    problems = []
    if config["models"]["D"]["source"] != kit.D_SOURCE:
        problems.append("D source differs from the kit's D_SOURCE")
    if config["measurement_hw_model"] != "Mac15,9":
        problems.append("measurement_hw_model is not Mac15,9")
    if Path(config["anchor_source"]).name != ANCHOR_REVISION:
        problems.append("anchor_source snapshot is not the revision disk_census records")
    if r0.PINS["D"]["revision"] != kit.D_REVISION:
        problems.append("r0.PINS D revision differs from the kit")
    if config.get("offloads"):
        problems.append("R0 config carries W1 offloads")
    budget = step_budget(config["smc_step"])
    return {"status": "fail" if problems else "pass", "problems": problems,
            "config_sha256": hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest(),
            "file_sha256": hashlib.sha256(raw).hexdigest(), "smc_step_budget": budget,
            "mac_paths_not_checked": [config["models"]["D"]["source"], config["anchor_source"],
                                      config["shade_cache"], config["disk_path"]],
            "note": "Schema, pins and cross-references only; the Mac's own paths are checked by R0."}


def _launcher_files(ctx):
    if ctx.launcher:
        launcher = Path(ctx.launcher)
        return launcher, {"source": str(launcher)}
    if ctx.launcher_ref:
        out = ctx.work / "launcher"
        out.mkdir(parents=True, exist_ok=True)
        blobs = {}
        for name in ("launch_align_r0.py", "run_align_r0_launchagent.sh"):
            spec = f"{ctx.launcher_ref}:scripts/{name}"
            data = subprocess.run(["git", "-C", str(ctx.repo), "show", spec], check=True,
                                  capture_output=True).stdout
            (out / name).write_bytes(data)
            blobs[name] = subprocess.run(["git", "-C", str(ctx.repo), "rev-parse", spec], check=True,
                                         capture_output=True, text=True).stdout.strip()
        return out / "launch_align_r0.py", {"source": ctx.launcher_ref, "blobs": blobs}
    launcher = ctx.repo / "scripts/launch_align_r0.py"
    if not launcher.is_file():
        raise FileNotFoundError("scripts/launch_align_r0.py is not in this checkout; pass --launcher-ref origin/main")
    return launcher, {"source": str(launcher)}


def _load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_launcher(ctx):
    """Run the real ``launch`` with launchd faked, then the real ``run`` with the spec's interpreter."""
    launcher_path, provenance = _launcher_files(ctx)
    module = _load_module(launcher_path, "prequal_launch_align_r0")
    root = ctx.work / "launcher-run"
    custody, output = root / "custody", root / "r0-output"
    custody.parent.mkdir(parents=True, exist_ok=True)
    claimer = []
    real_run = subprocess.run

    def fake_run(argv, *args, **kwargs):
        if argv and argv[0] == "/prequal/launchctl":
            if argv[1] == "bootstrap":
                child = subprocess.Popen(["/bin/sleep", "120"])
                claimer.append(child)
                with module.fence_lock(custody):
                    module.write_fence(custody, {**module.read_fence(custody), "pid": child.pid})
            return subprocess.CompletedProcess(argv, 0, b"", b"")
        return real_run(argv, *args, **kwargs)

    python_bin = Path(ctx.python_bin)
    argv = ["launch", "--repo", str(ctx.repo), "--config", str(ctx.repo / "configs/align/v4/r0_desk.json"),
            "--output", str(output), "--python-bin", str(python_bin), "--disk-path", str(root),
            "--custody-root", str(custody), "--launchctl-bin", "/prequal/launchctl",
            "--magistrate-pid", str(os.getpid()), "--deadline", str(time.time() + 900),
            "--start-wait-seconds", "10"]
    original = module.subprocess.run
    module.subprocess.run = fake_run
    import contextlib
    import io
    printed, errors = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(printed), contextlib.redirect_stderr(errors):
            code = module.main(argv)
    finally:
        module.subprocess.run = original
        for child in claimer:
            child.kill()
            child.wait()
    problems = []
    jobs = sorted((custody / "r0-launches").glob("*")) if (custody / "r0-launches").is_dir() else []
    if code != 0 or len(jobs) != 1:
        return {"status": "fail", "exit_code": code, "launcher": provenance, "stderr": errors.getvalue()[-800:],
                "problems": ["launch did not create exactly one job"]}
    job = jobs[0]
    runner = json.loads((job / "runner.json").read_text())
    import plistlib
    plist = plistlib.loads(next(job.glob("*.plist")).read_bytes())
    unresolved = os.path.abspath(python_bin)
    expected = [unresolved, str(ctx.repo.resolve() / "scripts/align_r0_checks.py"), "--config",
                str((ctx.repo / "configs/align/v4/r0_desk.json").resolve()), "--output", str(output.resolve())]
    if runner != expected:
        problems.append(f"runner.json {runner} != expected {expected}")
    if plist["ProgramArguments"][3] != unresolved:
        problems.append("plist interpreter argument is not the unresolved --python-bin")
    wrapper = Path(plist["ProgramArguments"][1])
    if not wrapper.is_file():
        problems.append(f"LaunchAgent wrapper missing: {wrapper}")
    if plist["WorkingDirectory"] != str(ctx.repo.resolve()):
        problems.append("WorkingDirectory is not the measurement checkout")
    if output.exists():
        problems.append("launch created the R0 output directory itself")
    # The interpreter the LaunchAgent will exec must see the pinned stack.
    probe = subprocess.run([runner[0], "-I", "-c", (
        "import json,sys\nfrom importlib.metadata import version, PackageNotFoundError\n"
        "def v(d):\n try: return version(d)\n except PackageNotFoundError: return None\n"
        "print(json.dumps({'prefix':sys.prefix,'base_prefix':sys.base_prefix,"
        "'versions':{d:v(d) for d in ('mlx','mlx-lm','transformers')}}))")],
        capture_output=True, text=True, timeout=120)
    interpreter = {"argv0": runner[0], "is_symlink": Path(runner[0]).is_symlink(),
                   "resolves_to": str(Path(runner[0]).resolve()), "exit_code": probe.returncode,
                   "stderr_tail": probe.stderr[-400:]}
    if probe.returncode:
        problems.append("runner interpreter cannot import the pinned stack")
    else:
        found = json.loads(probe.stdout)
        interpreter.update(found)
        wanted = {d: found["versions"].get(d) for d in ctx.stack}
        if wanted != ctx.stack:
            problems.append(f"runner interpreter stack {found['versions']} != {ctx.stack}")
        venv = Path(runner[0]).parent.parent
        if (venv / "pyvenv.cfg").is_file() and Path(found["prefix"]).resolve() != venv.resolve():
            problems.append(f"runner interpreter belongs to venv {venv} but runs with prefix {found['prefix']}")
    # The real `run` subcommand, bounded, with the same interpreter and runner but --help.
    spec = root / "runner-help.json"
    spec.write_text(json.dumps([*runner[:2], "--help"]))
    run = subprocess.run([sys.executable, "-B", str(launcher_path), "run", "--deadline", str(time.time() + 120),
                          "--runner-spec", str(spec)], capture_output=True, text=True, timeout=180,
                         cwd=str(ctx.repo))
    if run.returncode or "--checks" not in run.stdout:
        problems.append(f"launcher run of the runner --help exited {run.returncode}")
    return {"status": "fail" if problems else "pass", "problems": problems, "launcher": provenance,
            "runner_json": runner, "interpreter": interpreter, "run_help_exit": run.returncode,
            "launch_stdout": printed.getvalue().strip(),
            "substitutions": {"--repo": str(ctx.repo), "--python-bin": str(python_bin),
                              "--output/--disk-path/--custody-root": str(root),
                              "launchctl": "faked: bootstrap spawns a claimer that takes the fence"},
            "fidelity": ("Real launch()/run() code and the real config; Mac paths, launchd, preflight "
                         "(AC/disk) and Spotlight stay on the Mac.")}


def check_kit(ctx):
    from scripts import align_v4_kit as kit
    from scripts.align_pilot_kit import sha
    files = kit.build_files(ctx.repo)
    drift = [str(p) for p, raw in files.items()
             if not (ctx.repo / p).is_file() or (ctx.repo / p).read_bytes() != raw]
    problems = [f"drift {p}" for p in drift]
    tree = json.loads((ctx.repo / kit.KIT / "plan_tree.json").read_bytes())
    plan_raw = (ctx.repo / kit.KIT / "collection_plan.json").read_bytes()
    if tree["plan"]["actual_sha256"] != sha(plan_raw):
        problems.append("plan_tree.plan.actual_sha256 does not hash collection_plan.json")
    plan = json.loads(plan_raw)
    for member in plan["members"]:
        if sha((ctx.repo / member["config_path"]).read_bytes()) != member["config_sha256"]:
            problems.append(f"member {member['ordinal']} config sha")
    for stage in tree["stage_graph"]:
        ref = stage.get("input") or {}
        if ref.get("kind") == "manifest" and sha((ctx.repo / ref["path"]).read_bytes()) != ref["sha256"]:
            problems.append(f"manifest sha {stage['stage_id']}")
    pins = json.loads((ctx.repo / kit.KIT / "registration/identity_pins.json").read_bytes())
    if pins["derivation"]["tree_sha256"] != sha((ctx.repo / kit.KIT / "plan_tree.json").read_bytes()):
        problems.append("identity_pins derivation tree_sha256")
    inputs = kit.read_inputs(ctx.repo)
    pending = kit.pending_inputs(inputs)
    d_identity = "pending"
    if not any(p.startswith("WP11.") for p in pending):
        # A filled WP11 must bind the pinned shards at every stage, not only at W1.
        try:
            pins_raw = (ctx.repo / kit.D_PINS).read_bytes()
            d_identity = kit.validate_d_identity(inputs["WP11"], json.loads(pins_raw), pins_raw=pins_raw)
        except (ValueError, OSError, KeyError, TypeError) as exc:
            d_identity = f"{type(exc).__name__}: {exc}"
            problems.append("WP11 D identity: " + d_identity)
    readiness = None
    try:
        # Inputs, D identity and the R1-derived sizing_b5.json: what prepare/arm require.
        kit.require_w1_ready(ctx.repo)
        readiness = "ready"
    except (ValueError, OSError, KeyError, TypeError) as exc:
        readiness = f"{type(exc).__name__}: {exc}"
    if ctx.stage == "w1" and readiness != "ready":
        problems.append("W1 requires require_w1_ready to pass: " + readiness)
    return {"status": "fail" if problems else "pass", "problems": problems, "files_checked": len(files),
            "members": len(plan["members"]), "pending_inputs": pending, "require_ready": readiness,
            "d_identity_folded_sha256": d_identity, "stage": ctx.stage,
            "note": "Pending inputs are expected before R0/R1; only stage w1 requires readiness."}


def check_w1_plan(ctx):
    """R1 kit checks: the W1 plan template and validator, L1, the fit rule, and the filled plan."""
    from scripts import align_v4_kit as kit, validate_align_v4_w1_plan as validator
    plan = json.loads((ctx.repo / kit.KIT / "collection_plan.json").read_bytes())
    inputs, r1_slots = kit.read_inputs(ctx.repo), kit.read_r1_slots(ctx.repo)
    template_path = ctx.repo / kit.KIT / "night_plan.template.json"
    problems = []
    if template_path.read_bytes() != validator.template_bytes(plan):
        problems.append("night_plan.template.json drifted from collection_plan.json (--regenerate-template)")
    try:
        validator.validate(json.loads(template_path.read_bytes()), inputs, r1_slots, collection_plan=plan)
        problems.append("validator accepted the PENDING_R1 template")
    except ValueError as exc:
        template_refusal = str(exc)
        if "PENDING_R1" not in template_refusal:
            problems.append("template refused for a reason other than its placeholders: " + template_refusal)
    # Lead ruling L1 and the A1 fit rule on the planning costs (no measured values).
    l1 = {"t_dead_tail_20": kit.l1_t_dead(300.0, 20.0), "t_dead_tail_75": kit.l1_t_dead(300.0, 75.0)}
    if not math.isclose(l1["t_dead_tail_20"], (1750 - 300) / kit.DEADMAN_FACTOR) or not math.isclose(
            l1["t_dead_tail_75"], (1800 - 300 - 75 - 10) / kit.DEADMAN_FACTOR):
        problems.append("l1_t_dead does not implement lead ruling L1")
    kit.check_l1_member_fit(300.0, l1["t_dead_tail_75"], 75.0)
    def planning(ordinal, budget):
        role = kit.ROSTER[ordinal - 1][0]
        return 1800 if role == "D" else 3131.27 / 4 if role == "anchor" else 1150 if role.endswith("G") else 850
    fit = kit.fit_roster(8192, planning)
    if fit["programmed_span_s"] != 26927 or fit["actions"]:
        problems.append(f"fit_roster on the Amendment-1 planning costs: {fit}")
    filled, verdict = kit.read_w1_plan(ctx.repo), None
    if filled is None:
        verdict = f"pending: {kit.W1_PLAN} (the R1-filled template) is not committed"
        if ctx.stage == "w1":
            problems.append("W1 requires the R1-filled " + str(kit.W1_PLAN))
    else:
        try:
            verdict = {"status": "VALID", **validator.validate(filled, inputs, r1_slots, collection_plan=plan)}
        except ValueError as exc:
            verdict = f"REFUSED: {exc}"
            problems.append(f"{kit.W1_PLAN} refused: {exc}")
        if not (ctx.repo / kit.SIZING).is_file():
            problems.append(f"{kit.SIZING} missing beside {kit.W1_PLAN} (regenerate the kit)")
    return {"status": "fail" if problems else "pass", "problems": problems, "stage": ctx.stage,
            "w1_plan": verdict, "l1": l1, "fit_rule_planning_span_s": fit["programmed_span_s"],
            "note": "Validator, L1 and fit rule self-tests run at every stage; stage w1 requires the filled plan."}


def check_d_pins(ctx):
    from joulewise.align import r0
    from scripts import align_v4_kit as kit
    pins = ctx.pins()
    problems = []
    if not (pins["revision"] == r0.PINS["D"]["revision"] == kit.D_REVISION):
        problems.append("pins/r0.PINS/kit revisions disagree")
    total = sum(v["size"] for v in pins["files"].values())
    weights = sum(v["size"] for p, v in pins["files"].items() if p.startswith(WEIGHT_PREFIX))
    if total != r0.PINS["D"]["bytes"]:
        problems.append(f"pinned file bytes {total} != r0.PINS bytes {r0.PINS['D']['bytes']}")
    info = ctx.hf_api().model_info(pins["repo"], revision=pins["revision"], files_metadata=True)
    if info.sha != pins["revision"]:
        problems.append(f"HF resolved {info.sha}, pinned {pins['revision']}")
    remote = {s.rfilename: s for s in info.siblings}
    for name in sorted(set(remote) - set(pins["files"])):
        problems.append(f"remote file not pinned: {name}")
    for name, pin in sorted(pins["files"].items()):
        item = remote.get(name)
        if item is None:
            problems.append(f"pinned file absent remotely: {name}")
            continue
        lfs = getattr(item, "lfs", None)
        lfs_sha = getattr(lfs, "sha256", None) if lfs is not None else None
        if isinstance(lfs, dict):
            lfs_sha = lfs.get("sha256")
        if item.size != pin["size"]:
            problems.append(f"size {name}: remote {item.size} != {pin['size']}")
        if pin.get("sha256") and lfs_sha != pin["sha256"]:
            problems.append(f"lfs sha256 {name}")
        if pin.get("git_blob_sha1") and item.blob_id != pin["git_blob_sha1"]:
            problems.append(f"git blob {name}")
    return {"status": "fail" if problems else "pass", "problems": problems, "revision": info.sha,
            "files": len(pins["files"]), "lfs_pinned": sum(bool(v.get("sha256")) for v in pins["files"].values()),
            "weight_bytes": weights, "downloaded_weight_bytes": 0,
            "fidelity": "Remote listing only; the Mac's local copy is re-hashed by R0 disk + the verifier."}


def check_pin_verifier(ctx):
    from scripts import align_v4_verify_d_pins as verifier
    pins = ctx.pins()
    files = [{"path": p, "bytes": v["size"], "sha256": v.get("sha256") or "0" * 64}
             for p, v in pins["files"].items()]
    report = {"checks": [{"check": "disk", "models": {"D": {"revision": pins["revision"], "files": files}}}]}
    clean = verifier.verify(report, pins)
    bad = json.loads(json.dumps(report))
    bad["checks"][0]["models"]["D"]["files"][0]["bytes"] += 1
    tampered = verifier.verify(bad, pins)
    hub = json.loads(json.dumps(report))
    hub["checks"][0]["models"]["D"]["files"].append({"path": ".cache/huggingface/download/x.metadata",
                                                     "bytes": 1, "sha256": "0" * 64})
    bookkeeping = verifier.verify(hub, pins)
    # Only the exact top-level hf --local-dir prefix is exempt (PR #686, f1ae2d3be).
    nested = json.loads(json.dumps(report))
    nested["checks"][0]["models"]["D"]["files"].append({"path": "sub/.cache/huggingface/x.safetensors",
                                                        "bytes": 1, "sha256": "0" * 64})
    nested_result = verifier.verify(nested, pins)
    problems = []
    if clean:
        problems.append(f"verifier rejects an exact pinned inventory: {clean}")
    if not tampered:
        problems.append("verifier accepts a size mismatch")
    if bookkeeping:
        problems.append(f"verifier rejects .cache/huggingface/ bookkeeping: {bookkeeping}")
    if not nested_result:
        problems.append("verifier exempts a non-top-level .cache/huggingface/ path")
    row = {"status": "fail" if problems else "pass", "problems": problems,
           "hf_cache_bookkeeping_result": bookkeeping,
           "hf_cache_bookkeeping_counted": getattr(verifier, "bookkeeping", lambda r: None)(hub),
           "known_behavior": ("The verifier counts and reports top-level .cache/huggingface/ bookkeeping and "
                              "does not compare it (PR #686, f1ae2d3be; RUN_STATE item 179).")}
    if ctx.r0_report:
        found = verifier.verify(json.loads(Path(ctx.r0_report).read_text()), pins)
        row["r0_report"] = {"path": str(ctx.r0_report), "problems": found,
                            "only_hf_cache_bookkeeping": all(
                                p.startswith("unpinned local file .cache/huggingface/") for p in found)}
    return row


def check_tokenizer_files(ctx):
    path = ctx.tokenizer_dir()
    pins = ctx.pins()
    return {"status": "pass", "path": str(path), "revision": pins["revision"],
            "files": sorted(p for p in pins["files"] if not p.startswith(WEIGHT_PREFIX)),
            "bytes": sum(v["size"] for p, v in pins["files"].items() if not p.startswith(WEIGHT_PREFIX)),
            "verified": "size + LFS sha256 or git blob sha1 against configs/align/v4 pins"}


def _render_row(backend, messages, tools, effort, label):
    text = backend.endpoint._render_prompt(messages, tools)
    ids = backend.encode(text)
    problems = []
    if not text.endswith("<|im_start|>assistant\n<think>\n"):
        problems.append("generation prompt does not open reasoning")
    # The pinned template writes an instruction line for xhigh (default) and low only;
    # medium renders no effort line at all.
    if effort == "medium":
        if "Reasoning effort is set to" in text:
            problems.append("medium rendered an effort instruction line")
    elif f"Reasoning effort is set to {effort or 'xhigh'}." not in text:
        problems.append(f"missing 'Reasoning effort is set to {effort or 'xhigh'}.'")
    if len(ids) > 40960:
        problems.append("prompt exceeds the 40,960 context cap")
    if backend.encode(backend.tokenizer.decode(ids)) != ids:
        problems.append("encode(decode(ids)) is not canonical")
    return {"label": label, "effort": effort or "xhigh(default)", "tokens": len(ids),
            "ids_sha256": digest(ids), "text_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "problems": problems}


def check_template_render(ctx):
    from joulewise.align import r0
    from joulewise.align.interfaces import ChatMessage
    from scripts import align_v4_kit as kit
    backend = ctx.tokenizer_backend()
    ref = ctx.reference()
    rows = []
    for effort in EFFORTS:
        backend.new_session(effort)
        rows.append(_render_row(backend, [ChatMessage("user", r0.SHORT_PROMPT)], [], effort, "r0.short"))
        rows.append(_render_row(backend, [ChatMessage("user", r0.ECHO_PROMPT)], r0.ECHO_TOOLS, effort, "r0.echo"))
        for pair, seed in zip(r0.PAIRS, (91, 92)):
            task = backend.task(pair, seed)
            messages = [ChatMessage("system", task.system_prompt("benign")), ChatMessage("user", task.user_prompt())]
            rows.append(_render_row(backend, messages, task.tool_schemas(), effort, f"r0.ladder.{pair}.{seed}"))
    # W1 D members: effort from inputs when selected, otherwise every rung.
    inputs = kit.read_inputs(ctx.repo)
    selected = inputs.get("R0", {}).get("reasoning_effort")
    efforts = [selected] if selected in ("xhigh", "medium", "low") else ["xhigh", "medium", "low"]
    plan = json.loads((ctx.repo / kit.KIT / "collection_plan.json").read_bytes())
    seen = set()
    for member in plan["members"]:
        if member["role"] != "D":
            continue
        key = (member["task_pair"], member["condition"], member["seed_index"])
        if key in seen:
            continue
        seen.add(key)
        for effort in efforts:
            backend.new_session(None if effort == "xhigh" else effort)
            task = backend.task(member["task_pair"], member["seed_index"])
            messages = [ChatMessage("system", task.system_prompt(member["condition"])),
                        ChatMessage("user", task.user_prompt())]
            rows.append(_render_row(backend, messages, task.tool_schemas(), None if effort == "xhigh" else effort,
                                    "w1.D.{}.{}.{}".format(*key)))
    backend.new_session(None)
    problems = [f"{r['label']}[{r['effort']}]: {p}" for r in rows for p in r["problems"]]
    short = backend.render([ChatMessage("user", r0.SHORT_PROMPT)], [])
    echo = backend.render([ChatMessage("user", r0.ECHO_PROMPT)], r0.ECHO_TOOLS)
    equivalence = {"short_prompt_ids_match_mac": digest(short) == ref["short"]["prompt_token_ids_sha256"],
                   "echo_prompt_ids_match_mac": digest(echo) == ref["echo_first"]["prompt_token_ids_sha256"]}
    problems += [k for k, v in equivalence.items() if not v]
    return {"status": "fail" if problems else "pass", "problems": problems, "renders": rows,
            "mac_equivalence": equivalence, "reference": ref["source"],
            "note": ("R1 drives D through the same endpoint and W1 member specs; its prompts are covered by "
                     "the W1 rows. Effort 'xhigh' passes no kwarg, as R0 and the kit do.")}


def check_nll_fixture(ctx):
    from joulewise.align import r0
    from joulewise.align.interfaces import ChatMessage
    backend = ctx.tokenizer_backend()
    backend.new_session(None)
    ref = ctx.reference()["nll_prompt"]
    task = backend.task(r0.PAIRS[0], 91)
    messages = [ChatMessage("system", task.system_prompt("benign")), ChatMessage("user", task.user_prompt())]
    full = backend.render(messages, task.tool_schemas())
    ids = full[:2049]
    canonical = backend.encode(backend.tokenizer.decode(ids)) == ids
    problems = []
    if len(ids) != ref["tokens"]:
        problems.append(f"fixture has {len(ids)} ids, expected {ref['tokens']}")
    if digest(ids) != ref["sha256"]:
        problems.append("fixture ids differ from the measurement-Mac R0 ids")
    if not canonical:
        problems.append("fixture ids are not canonical under encode(decode())")
    return {"status": "fail" if problems else "pass", "problems": problems, "tokens": len(ids),
            "rendered_tokens": len(full), "sha256": digest(ids), "expected_sha256": ref["sha256"],
            "canonical_roundtrip": canonical, "max_id": max(ids),
            "fidelity": "IDs only; scoring them needs a model (see load under a model backend)."}


def check_template_rewrites(ctx):
    from joulewise.align import r0
    backend = ctx.tokenizer_backend()
    result = r0.template_rewrites(backend)
    problems = [] if len(result["transitions"]) == 12 else ["fewer than 12 synthetic transitions"]
    return {"status": "fail" if problems else "diagnostic", "problems": problems,
            "prefix_stable": result["prefix_stable"],
            "rewritten_prefix_tokens": [t["rewritten_prefix_tokens"] for t in result["transitions"]],
            "note": "R0's own synthetic template check, run here without a model. It cannot decide B7."}


def _parse(raw, tools):
    from joulewise.align import r0  # noqa: F401  (import order matches R0)
    from joulewise.align.apple.endpoint import parse_completion
    return parse_completion(raw, reasoning_open=True, model_family="qwen3_5", tools=tools)


def _example(schema, root, depth=0):
    """A schema-satisfying value; strings carry XML-hostile characters."""
    if depth > 8:
        raise ValueError("schema too deep for a synthetic example")
    if "$ref" in schema:
        node = root
        for part in schema["$ref"].removeprefix("#/").split("/"):
            node = node[part]
        return _example(node, root, depth + 1)
    if "const" in schema:
        return schema["const"]
    if schema.get("enum"):
        return schema["enum"][0]
    for key in ("anyOf", "oneOf"):
        if key in schema:
            options = [o for o in schema[key] if o.get("type") != "null"] or schema[key]
            return _example(options[0], root, depth + 1)
    if "allOf" in schema:
        return _example(schema["allOf"][0], root, depth + 1)
    kind = schema.get("type")
    if isinstance(kind, list):
        kind = next((k for k in kind if k != "null"), "null")
    if kind == "integer":
        return 3
    if kind == "number":
        return 1.5
    if kind == "boolean":
        return True
    if kind == "null":
        return None
    if kind == "array":
        return [_example(schema.get("items", {"type": "string"}), root, depth + 1)]
    if kind == "object" or "properties" in schema:
        props = schema.get("properties", {})
        return {k: _example(props[k], root, depth + 1) for k in schema.get("required", list(props))}
    return "x <y> & z"


def check_tool_roundtrip(ctx):
    """Canned D outputs (recorded on the Mac and synthetic) through parse -> tool -> history -> render."""
    from joulewise.align import r0
    from joulewise.align.interfaces import ChatMessage, ChatResult
    backend = ctx.tokenizer_backend()
    backend.new_session(None)
    ref = ctx.reference()
    problems, cases = [], []
    # 1. The Mac's real first echo turn reproduces the Mac's real second prompt.
    first = ref["echo_first"]
    visible, reasoning, calls, flags = _parse(first["raw_text"], r0.ECHO_TOOLS)
    prompt = backend.render([ChatMessage("user", r0.ECHO_PROMPT)], r0.ECHO_TOOLS)
    result = ChatResult(visible, reasoning, calls, len(prompt), 0, first["output_tokens"], 0, 0, 0, 0,
                        {"raw_text": first["raw_text"]})
    messages = [ChatMessage("user", r0.ECHO_PROMPT)]
    outputs = r0.append_result(backend, messages, result, r0.EchoTask(), strict=True)
    second = backend.render(messages, r0.ECHO_TOOLS)
    case = {"case": "mac_echo_turn_1_to_turn_2", "calls": len(calls), "flags": list(flags),
            "visible_matches_mac": visible == first["visible_text"], "tool_outputs": outputs,
            "second_prompt_tokens": len(second),
            "second_prompt_matches_mac": digest(second) == ref["echo_second"]["prompt_token_ids_sha256"]}
    cases.append(case)
    if len(calls) != 1 or outputs != ref["echo_tool_outputs"] or not case["second_prompt_matches_mac"]:
        problems.append("recorded echo round trip does not reproduce the Mac's second prompt")
    if not case["visible_matches_mac"]:
        problems.append("parse_completion visible text differs from the Mac's endpoint split")
    # 2. Every recorded turn parses with the Mac's call count.
    for key in ("short", "echo_first", "echo_second"):
        _, _, parsed, _ = _parse(ref[key]["raw_text"], r0.ECHO_TOOLS if key != "short" else [])
        ok = len(parsed) == ref[key]["tool_calls"]
        cases.append({"case": f"mac_{key}_call_count", "calls": len(parsed), "expected": ref[key]["tool_calls"], "ok": ok})
        if not ok:
            problems.append(f"{key} call count differs")
    # 3. Synthetic SHADE calls over the real tool schemas: every tool, typed parameters.
    task = backend.task(r0.PAIRS[0], 91)
    schemas = task.tool_schemas()
    shade_ok = 0
    for schema in schemas:
        fn = schema["function"]
        params = fn.get("parameters", {})
        props = params.get("properties", {})
        args = {name: _example(props.get(name, {}), params) for name in params.get("required", list(props))}
        body = "".join(f"<parameter={k}>\n{json.dumps(v) if not isinstance(v, str) else v}\n</parameter>\n"
                       for k, v in args.items())
        raw = f"Plan.\n</think>\n\n<tool_call>\n<function={fn['name']}>\n{body}</function>\n</tool_call>"
        _, _, parsed, pflags = _parse(raw, schemas)
        got = [(c.name, json.loads(c.arguments_json)) for c in parsed]
        if got == [(fn["name"], args)] and not [f for f in pflags if f.startswith("malformed")]:
            # History render and re-parse of the rendered assistant turn.
            hist = ChatResult("", "Plan.", parsed, 0, 0, 0, 0, 0, 0, 0, {"raw_text": raw})
            msgs = [ChatMessage("user", "go"), backend.endpoint.assistant_history_message(hist)]
            rendered = backend.endpoint._render_prompt(msgs, schemas, add_generation_prompt=False)
            if f"<function={fn['name']}>" in rendered:
                shade_ok += 1
                continue
        problems.append(f"SHADE tool {fn['name']} did not round trip: {got} {pflags}")
    cases.append({"case": "shade_tools_parse_and_history", "tools": len(schemas), "round_tripped": shade_ok})
    # 4. Malformed, truncated and unsupported envelopes are flagged, never parsed as calls.
    bad = {"truncated": "x\n</think>\n\n<tool_call>\n<function=r0_echo>\n<parameter=value>\ndesk",
           "unknown_tool": "x\n</think>\n\n<tool_call>\n<function=nope>\n</function>\n</tool_call>",
           "json_envelope": 'x\n</think>\n\n<tool_call>\n{"name":"r0_echo","arguments":{"value":"desk-check"}}\n</tool_call>'}
    for name, raw in bad.items():
        _, _, parsed, pflags = _parse(raw, r0.ECHO_TOOLS)
        flagged = any(f.startswith(("malformed_tool_call", "unsupported_tool_call")) for f in pflags)
        cases.append({"case": f"reject_{name}", "calls": len(parsed), "flags": list(pflags)})
        if parsed or not flagged:
            problems.append(f"{name} envelope was not rejected with a flag")
    # 5. R0's envelope accounting over canned rows.
    rows = [{"raw_text": ref[k]["raw_text"], "visible_text": ref[k]["visible_text"], "tool_calls": ref[k]["tool_calls"],
             "flags": ref[k]["flags"], "hit_cap": ref[k]["hit_cap"]} for k in ("short", "echo_first", "echo_second")]
    envelopes = r0.tool_envelopes({"turns": rows})
    cases.append({"case": "r0_tool_envelopes_on_mac_turns", **envelopes})
    if envelopes["status"] != "pass" or envelopes["attempted_envelopes"] != 2:
        problems.append("tool_envelopes accounting on the Mac's turns")
    return {"status": "fail" if problems else "pass", "problems": problems, "cases": cases}


def check_checkpoint_native(ctx):
    """Tiny random-weight hybrid-cache checkpoint exactness (not the --benchmark timing)."""
    script = ctx.repo / "scripts/align_cache_checkpoint_native.py"
    proc = subprocess.run([sys.executable, "-B", str(script)], capture_output=True, text=True, timeout=1800,
                          cwd=str(ctx.repo), env={**os.environ, "PYTHONPATH": str(ctx.repo)})
    lines = []
    for line in proc.stdout.splitlines():
        try:
            lines.append(json.loads(line))
        except ValueError:
            lines.append({"unparsed": line[-300:]})
    final = lines[-1] if lines else {}
    exact = [x["exactness"] for x in lines if "exactness" in x]
    # The script's own tolerances decide; bitwise agreement is recorded, not imposed.
    bitwise = sum(all(v.get("bitwise") for v in e.values() if isinstance(v, dict) and "bitwise" in v)
                  for e in exact)
    ok = proc.returncode == 0 and final.get("status") == "passed" and bool(exact)
    payload = {"final": final, "exactness_rows": len(exact), "bitwise_rows": bitwise,
               "families": sorted({e.get("family") for e in exact})}
    return {"status": "pass" if ok else "fail", "exit_code": proc.returncode,
            "result": payload, "stderr_tail": proc.stderr[-800:],
            "fidelity": ("Restore exactness on tiny qwen3_5/qwen3_next configs on any Metal GPU. W1 runs D "
                         "with hybrid_checkpoint_limit 0; B7 timing and the D verdict stay on the Mac.")}


# ---- model tier (pluggable backend) ------------------------------------------


def _model_backend(ctx):
    def make():
        factory = BACKENDS[ctx.model_backend]
        return factory(ctx)
    return ctx.once("model_backend", make)


def check_model_load(ctx):
    backend = _model_backend(ctx)
    info = backend.device_info()
    return {"status": "pass", "backend": ctx.model_backend, "sibling": getattr(backend, "prequal_sibling", None),
            "device": info.get("device_info"), "mlx_lm_version": info["load"].get("mlx_lm_version"),
            "model_config_name": info["load"].get("model_config_name"),
            "fidelity": SiblingBackend.fidelity}


def generation_ran_end_to_end(generation):
    """Problems if R0's generation check did not run render -> greedy decode -> parse ->
    tool_envelopes -> schema validation. Its pass/fail outcome is not judged here."""
    if not isinstance(generation, dict) or not generation.get("attempts"):
        return ["generation check did not run"]
    problems = []
    first = generation["attempts"][0]
    if first.get("decode") != "greedy":
        problems.append("first generation attempt was not greedy")
    for index, attempt in enumerate(generation["attempts"]):
        turn = attempt.get("turn") or {}
        if not turn.get("prompt_token_ids") or not isinstance(attempt.get("prompt_sha256"), str):
            problems.append(f"attempt {index}: no rendered prompt")
        if not isinstance(turn.get("tokens"), int) or turn["tokens"] <= 0:
            problems.append(f"attempt {index}: no decoded tokens")
        envelopes = attempt.get("envelopes")
        if not isinstance(envelopes, dict) or "attempted_envelopes" not in envelopes:
            problems.append(f"attempt {index}: tool_envelopes accounting missing")
        if attempt.get("status") not in ("pass", "fail") or not isinstance(attempt.get("problems"), list):
            problems.append(f"attempt {index}: no generation verdict")
        if any(str(p).startswith("schema_ref_unresolved") for p in attempt.get("problems") or ()):
            problems.append(f"attempt {index}: schema validation could not run")
    if generation.get("status") not in ("pass", "fail"):
        problems.append("generation check has no verdict")
    return problems


def check_load(ctx):
    from joulewise.align import r0
    backend = _model_backend(ctx)
    result = r0.load_coherence(backend, references=ctx.sibling_nll_references())
    ref = ctx.reference()
    problems = []
    if result["nll_prompt_sha256"] != ref["nll_prompt"]["sha256"]:
        problems.append("model-tier NLL ids differ from the Mac's")
    if result["nll_nats_per_token"] is None:
        problems.append("NLL is not finite")
    if result["short"]["prompt_token_ids"] and digest(result["short"]["prompt_token_ids"]) != ref["short"]["prompt_token_ids_sha256"]:
        problems.append("short prompt ids differ from the Mac's")
    verdict = result["nll_verdict"]
    if verdict.get("status") != "pass":
        problems.append(f"sibling NLL verdict {verdict.get('status')}: {verdict.get('reason')}")
    if verdict.get("entry") != SIBLING_NLL_LABEL or verdict.get("model_revision") != ctx.sibling_revision:
        problems.append("NLL verdict did not use the sibling's own reference entry")
    generation = result.get("generation")
    problems.extend(generation_ran_end_to_end(generation))
    trip = result["tool_round_trip"]
    return {"status": "fail" if problems else "pass", "problems": problems, "backend": ctx.model_backend,
            "nll_nats_per_token": result["nll_nats_per_token"],
            "nll_verdict": {k: verdict.get(k) for k in ("status", "reason", "mode", "entry", "model_revision",
                                                        "fixture_sha256", "reference_nll_nats_per_token",
                                                        "delta_nats_per_token", "max_abs_bin_delta")},
            "generation_outcome_is_diagnostic": True,
            "generation_outcome": ({k: generation.get(k) for k in ("status", "problems", "requested_tool",
                                                                   "retried", "decode", "tokens")}
                                   if isinstance(generation, dict) else None),
            "r0_load_status_is_diagnostic": True, "r0_load_status": result.get("status"),
            "coherent": result["coherent"],
            "echo_round_trip_succeeded": trip["succeeded"], "echo_error": trip["error"],
            "short_tokens": result["short"]["tokens"], "short_visible_tail": result["short"]["visible_text"][-80:],
            "fidelity": ("Code path only (load, render, chunked-cache NLL loop with the sibling's own HF fp32 "
                         "reference entry, chat, parse, tool reply, second turn, and R0's generation check end to "
                         "end). The verdict is the sibling's, not D's: R0 load stays on the Mac.")}


def check_generated(ctx):
    from joulewise.align import r0
    backend = _model_backend(ctx)
    result = r0.generated_rewrites(backend, transitions=ctx.generated_transitions)
    verdict = r0.checkpoint_verdict("D", result)
    problems = [] if result["transitions"] else ["no generated transition completed"]
    return {"status": "fail" if problems else "diagnostic", "problems": problems, "backend": ctx.model_backend,
            "transitions": len(result["transitions"]), "requested": ctx.generated_transitions,
            "rewritten_prefix_tokens": [t["rewritten_prefix_tokens"] for t in result["transitions"]],
            "closed_reasoning": [t["closed_reasoning"] for t in result["transitions"]],
            "off_spec_echo_turns": result["off_spec_echo_turns"], "sibling_checkpoint_verdict": verdict,
            "fidelity": "Generated-turn template re-render path with sibling output; B7 for D is decided on the Mac."}


AIR_CHECKS = (
    ("stack", check_stack), ("r0-config", check_r0_config), ("launcher", check_launcher),
    ("kit", check_kit), ("w1-plan", check_w1_plan), ("d-pins", check_d_pins), ("d-pin-verifier", check_pin_verifier),
    ("d-tokenizer-files", check_tokenizer_files), ("template-render", check_template_render),
    ("nll-fixture-ids", check_nll_fixture), ("template-rewrites", check_template_rewrites),
    ("tool-roundtrip", check_tool_roundtrip), ("checkpoint-native", check_checkpoint_native),
)
MODEL_CHECKS = (("model-load", check_model_load), ("load", check_load), ("generated", check_generated))
NETWORK_CHECKS = {"d-pins"}


def run(ctx, *, only=None, skip=()):
    started = time.monotonic()
    rows = []
    selected = [(n, f) for n, f in AIR_CHECKS + MODEL_CHECKS if (only is None or n in only) and n not in skip]
    for name, fn in selected:
        t0 = time.monotonic()
        if name in dict(MODEL_CHECKS) and ctx.model_backend == "none":
            row = {"status": "not_run", "reason": "no model backend selected (--model-backend sibling)"}
        elif name in NETWORK_CHECKS and ctx.offline:
            row = {"status": "not_run", "reason": "--offline"}
        elif name in dict(MODEL_CHECKS) and name != "model-load" and any(
                r["check"] == "model-load" and r["status"] != "pass" for r in rows):
            row = {"status": "not_run", "reason": "model-load prerequisite did not pass"}
        else:
            try:
                row = fn(ctx)
            except Exception as exc:  # fail closed: an error is a failure, never a skip
                row = {"status": "fail", "error": f"{type(exc).__name__}: {exc}",
                       "traceback_tail": traceback.format_exc()[-1500:]}
        row = {"check": name, **row, "seconds": round(time.monotonic() - t0, 3)}
        if row["status"] not in STATUSES:
            row = {**row, "status": "fail", "error": f"invalid status {row['status']!r}"}
        rows.append(row)
    failed = [r["check"] for r in rows if r["status"] == "fail"]
    missing = [r["check"] for r in rows if r["status"] == "not_run"]
    unselected = [n for n, _ in AIR_CHECKS + MODEL_CHECKS if n not in {r["check"] for r in rows}]
    status = "fail" if failed else "incomplete" if (missing or unselected) else "pass"
    return {"schema": SCHEMA, "status": status, "stage": ctx.stage, "failed": failed,
            "not_run": missing + unselected, "checks": rows, "mac_only": MAC_ONLY,
            "host": host_facts(), "checkout": checkout_facts(ctx.repo),
            "implementation_sha256": {p: hashlib.sha256((ctx.repo / p).read_bytes()).hexdigest() for p in (
                "joulewise/align/prequal.py", "scripts/align_v4_prequal.py", "joulewise/align/r0.py",
                "joulewise/align/r0_mlx.py", "joulewise/align/r0_runner.py", "scripts/align_v4_kit.py",
                "configs/align/v4/r0_desk.json", "configs/align/v4/qwen38-27b-8bit-hf-pins.json",
                "configs/align/v4/prequal_r0_reference.json", "configs/align/v4/r0_nll_reference.json",
                "configs/align/v4/prequal_sibling_nll_reference.json", "scripts/validate_align_v4_w1_plan.py",
                "configs/campaigns/align_v4/registration/inputs.json")
                if (ctx.repo / p).is_file()},
            "model_backend": ctx.model_backend, "total_seconds": round(time.monotonic() - started, 3),
            "authority": "RUN_STATE item 183 (no check pinned to the Mac if it can run elsewhere); "
                         "Ed 2026-11-06: checks that measure the Mac itself stay on the Mac.",
            "claims": "Software/model/config/fixture pre-qualification only. Grants no arm, R0 or R1 result."}


def host_facts():
    def sysctl(name):
        try:
            return subprocess.run(["/usr/sbin/sysctl", "-n", name], capture_output=True, text=True,
                                  timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return None
    return {"hw_model": sysctl("hw.model"), "hw_memsize": sysctl("hw.memsize"), "platform": platform.platform(),
            "python": sys.version.split()[0], "interpreter": sys.executable}


def checkout_facts(repo):
    def git(*args):
        result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    return {"head": git("rev-parse", "HEAD"), "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
            "dirty": bool(git("status", "--porcelain", "--untracked-files=no"))}


def markdown(report):
    lines = ["# ALIGN v4 off-Mac pre-qualification", "",
             f"Status: **{report['status']}** (stage {report['stage']}). {report['claims']}",
             f"Host: {report['host']['hw_model']}; checkout {report['checkout']['head']} "
             f"(dirty={report['checkout']['dirty']}); model backend: {report['model_backend']}.",
             f"Total wall time: {report['total_seconds']} s.", "",
             "| Check | Status | Seconds | Problems / reason |", "|---|---|---|---|"]
    for row in report["checks"]:
        why = "; ".join(row.get("problems") or []) or row.get("error") or row.get("reason") or ""
        lines.append(f"| {row['check']} | {row['status']} | {row['seconds']} | {why[:300]} |")
    lines += ["", "## Stays on the measurement Mac (measures the Mac itself)", ""]
    lines += [f"- `{k}`: {v}" for k, v in report["mac_only"].items()]
    lines += ["", "Full evidence (IDs hashes, renders, cases, provenance) is in the companion JSON.", ""]
    return "\n".join(lines)


def write(report, output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    (output / "prequal.json").write_text(json.dumps(report, indent=2, sort_keys=True, default=str) + "\n")
    (output / "prequal.md").write_text(markdown(report))
    return output
