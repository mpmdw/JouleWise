"""Resumable coordinator: never imports Torch or MLX; workers are serial."""
from __future__ import annotations

import argparse
import json
import math
import os
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .core import (GATE_AMENDMENTS, IndexedCheckpoint, SCHEMA, TOLERANCES, compare_arrays, compare_exact,
                   compare_norm, TraceFile, digest, file_stamp, norm_specs, required_traces, router_boundary_swaps,
                   sha256, text_config, write_json)

REPO = Path(__file__).resolve().parents[3]
PACKAGE = Path(__file__).resolve().parent
DEFAULT_PROMPTS = [
    {"name": "tokens-a", "input_ids": [5, 11, 17, 23, 29, 31, 37, 0, 41]},
    {"name": "tokens-b", "input_ids": [47, 53, 59, 61, 67, 71, 73, 79]},
]


def worker_env(hf_home=None):
    env = dict(os.environ)
    hf_home = Path(hf_home) if hf_home else REPO / ".cache/qwen4-gold-hf"
    for key in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS", "MLX_NUM_THREADS"):
        env[key] = "2"
    env.update(PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1", HF_HUB_OFFLINE="1",
               TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1", TOKENIZERS_PARALLELISM="false",
               HF_HOME=str(hf_home), HF_HUB_CACHE=str(hf_home / "hub"),
               HF_XET_CACHE=str(hf_home / "xet"), HF_HUB_DISABLE_XET="1",
               HF_XET_CHUNK_CACHE_SIZE_BYTES="0", HF_XET_SHARD_CACHE_SIZE_LIMIT="0")
    env["PYTHONPATH"] = str(REPO)
    return env


def runtime_identity(python):
    # Bind the installed distribution records and every file they enumerate,
    # rather than trusting mutable version strings or one modeling source.
    code = """import hashlib, importlib.metadata as m, json, pathlib, sys
versions = {}
for name in ['transformers', 'torch', 'mlx', 'mlx-lm', 'numpy', 'safetensors']:
    try:
        d=m.distribution(name); rows=[]
        for f in sorted(d.files or [], key=str):
            p=d.locate_file(f)
            if p.is_file(): rows.append([str(f), hashlib.sha256(p.read_bytes()).hexdigest()])
        versions[name]={'version':d.version,'distribution_sha256':hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),'files':len(rows)}
    except m.PackageNotFoundError: pass
if 'transformers' in versions:
    d=m.distribution('transformers')
    for n in ['modeling_qwen4_exp.py','configuration_qwen4_exp.py']:
        source=d.locate_file('transformers/models/qwen4_exp/'+n)
        versions[n+'_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
print(json.dumps(dict(versions, python=sys.version, python_executable_sha256=hashlib.sha256(pathlib.Path(sys.executable).read_bytes()).hexdigest())))"""
    result = subprocess.run([python, "-B", "-c", code], cwd=REPO, env=worker_env(),
                            capture_output=True, text=True, timeout=300, check=True)
    return json.loads(result.stdout)


def runtime_version(runtime, name):
    """Installed version of ``name`` from a runtime_identity record.

    Records bind each distribution as ``{"version", "distribution_sha256", ...}``;
    a bare version string is accepted for older/fixture records.
    """
    value = runtime.get(name)
    return value.get("version") if isinstance(value, dict) else value


def execute(python, request, directory, max_gb, timeout):
    """Guard actual child RSS; the caller keeps only one framework alive."""
    directory.mkdir(parents=True, exist_ok=True)
    parent_peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    parent_peak *= 1 if sys.platform == "darwin" else 1024
    child_limit = int(max_gb * 1024**3 - parent_peak - 256 * 1024**2)
    if child_limit <= 0:
        return {"error": "memory_guard_parent_budget"}
    request = dict(request, max_memory_bytes=child_limit)
    write_json(directory / "request.json", request)
    peak = 0
    can_inspect_rss = True
    reason = None
    start = time.monotonic()
    with (directory / "worker.log").open("w") as log:
        process = subprocess.Popen([python, "-B", "-m", "joulewise.align.qwen4_gold.worker",
                                    str(directory / "request.json"), str(directory)],
                                   cwd=REPO, env=worker_env(request.get("hf_home")), stdout=log, stderr=log)
        try:
            while process.poll() is None:
                if can_inspect_rss:
                    try:
                        rss = subprocess.run(["ps", "-o", "rss=", "-p", str(process.pid)], capture_output=True, text=True, check=False)
                        if rss.stdout.strip():
                            peak = max(peak, int(rss.stdout.strip()) * 1024)
                    except (OSError, ValueError):
                        can_inspect_rss = False  # Worker self-samples even when sandbox blocks ps.
                if peak > child_limit:
                    reason = "memory_guard"
                elif time.monotonic() - start > timeout:
                    reason = "worker_timeout"
                if reason:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill(); process.wait()
                    break
                time.sleep(0.2)
        except BaseException:
            process.kill(); process.wait()
            raise
    result = directory / "result.json"
    if process.returncode == 86:
        reason = "memory_guard"
    if process.returncode or reason or not result.exists():
        return {"error": reason or "worker_failed", "exit_code": process.returncode,
                "peak_rss_bytes": peak, "log": str(directory / "worker.log")}
    value = json.loads(result.read_text())
    metadata = value.get("metadata", {})
    if metadata.get("adapter_kind") == "mlx":
        allocation = metadata.get("peak_mlx_bytes")
        if type(allocation) not in (int, float) or not math.isfinite(allocation) or allocation < 0:
            return {"error": "invalid_mlx_memory_metadata"}
    peak = max(peak, metadata.get("peak_rss_bytes", 0) + metadata.get("peak_mlx_bytes", 0))
    if peak > child_limit:
        return {"error": "memory_guard", "peak_rss_bytes": peak}
    value["observed_peak_bytes"] = peak
    value["parent_peak_bytes"] = parent_peak
    value["child_budget_bytes"] = child_limit
    value["elapsed_seconds"] = time.monotonic() - start
    return value


def parse_layers(spec, count):
    if spec == "all":
        return list(range(count))
    values = sorted({int(i) for i in spec.split(",")})
    if not values or min(values) < 0 or max(values) >= count:
        raise ValueError("layer index out of range")
    return values


def load_prompts(path, config):
    prompts = json.loads(Path(path).read_text()) if path else DEFAULT_PROMPTS
    if not prompts:
        raise ValueError("empty prompt set")
    for prompt in prompts:
        ids = prompt["input_ids"]
        if not ids or any(type(i) is not int or i < 0 or i >= config["vocab_size"] for i in ids):
            raise ValueError("prompts must contain valid pretokenized input_ids")
        name = prompt["name"]
        if not name or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-" for c in name):
            raise ValueError("prompt name must be a safe identifier")
    if len({p["name"] for p in prompts}) != len(prompts):
        raise ValueError("duplicate prompt names")
    return prompts


def checkpoint_identity(checkpoint, layers, real, endpoints, progress):
    """Hash selected shard bytes once per invocation, including on resume.

    Missing files are recorded, not followed elsewhere or downloaded. A local
    sha256.txt is evidence only for entries it actually contains.
    """
    needed = set(layers)
    if real:
        needed |= set(range(max(layers) + 1))
        if endpoints:
            needed |= set(range(checkpoint.text["num_hidden_layers"]))
    keys = {k for k in checkpoint.weight_map if any(k.startswith(checkpoint.prefix + f"layers.{i}.") for i in needed)}
    if real or endpoints:
        keys.add(checkpoint.prefix + "embed_tokens.weight")
    if endpoints:
        keys |= {k for k in checkpoint.weight_map if k.startswith(checkpoint.prefix + "hyper_connection_mixer.") or k == "lm_head.weight"}
    files = sorted({checkpoint.weight_map[k] for k in keys})
    manifest = {}
    manifest_path = checkpoint.root / "sha256.txt"
    if manifest_path.exists():
        for line in manifest_path.read_text().splitlines():
            if not line.strip():
                continue
            checksum, name = line.split(maxsplit=1)
            name = name.lstrip("*")
            checkpoint.path(name)  # Reject traversal.
            if len(checksum) != 64 or any(c not in "0123456789abcdef" for c in checksum):
                raise ValueError("invalid sha256.txt entry")
            if name in manifest:
                raise ValueError("duplicate sha256.txt entry")
            manifest[name] = checksum
    hashes = {}
    stamps = {}
    for number, filename in enumerate(files):
        path = checkpoint.path(filename)
        if path.exists():
            progress(f"Hashing shard {number+1}/{len(files)}: {filename}")
            before = file_stamp(path)
            actual = sha256(path)
            stamps[filename] = file_stamp(path)
            if before != stamps[filename]:
                raise ValueError(f"checkpoint shard changed while hashing: {filename}")
            if filename in manifest and actual != manifest[filename]:
                raise ValueError(f"sha256.txt mismatch: {filename}")
            hashes[filename] = actual
        else:
            hashes[filename] = None
            stamps[filename] = None
    return {"stamps": stamps, "config": checkpoint.config, "weight_map": checkpoint.weight_map, "shards": hashes,
            "manifest_covered": sorted(set(manifest) & set(files)),
            "manifest_uncovered": sorted(set(files) - set(manifest)),
            "missing": sorted(k for k, v in hashes.items() if v is None)}


def artifacts(directory):
    """Verdict inputs: arrays plus the exact requests/results naming them."""
    files = list(directory.rglob("*.npy"))
    for side in ("reference", "mlx"):
        files += [directory / side / name for name in ("request.json", "result.json")]
    return {str(p.relative_to(directory)): sha256(p) for p in sorted(set(files)) if p.is_file()}


def reusable(path, fingerprint):
    """Authenticate reusable worker evidence only; never authenticate a verdict."""
    if not path.exists():
        return False
    value = json.loads(path.read_text())
    if value.get("fingerprint") != fingerprint:
        return False
    expected = value.get("artifacts", {})
    if value.get("evidence_digest") != digest({"fingerprint": fingerprint, "artifacts": expected}):
        return False
    sides = ("reference", "mlx") if any(name.startswith("mlx/") for name in expected) else ("reference",)
    required = {f"{side}/{name}" for side in sides for name in ("request.json", "result.json")}
    return required <= set(expected) and expected == artifacts(path.parent) and all(
        (path.parent / name).is_file() and sha256(path.parent / name) == h for name, h in expected.items())


def worker_peak(result):
    metadata = result.get("metadata", {})
    return max(result.get("observed_peak_bytes", 0),
               metadata.get("peak_rss_bytes", 0) + metadata.get("peak_mlx_bytes", 0))


def failure_summary(report):
    """Every non-PASS case of a unit report with its failing/missing traces."""
    failures = []
    for row in report["cases"]:
        if row["status"] == "PASS":
            continue
        failures.append({"case": row["case"], "status": row["status"],
                         "failing_traces": sorted(n for n, m in row.get("metrics", {}).items() if not m.get("pass")),
                         "missing_traces": row.get("missing_traces", []), "reason": row.get("reason")})
    return failures


def markdown_report(report):
    lines = [f"# Qwen4 gold: {report['unit']}", "", f"Status: **{report['status']}**. Scope: prefill, no cache.", "",
             f"Completed cases: {len(report['cases'])}/{report.get('expected_cases', len(report['cases']))}. "
             f"A2 admissible bf16 router boundary swaps: {report.get('a2_admissible_swaps', 0)}.", "",
             "| Case | Status | Max abs | Min cosine | Peak worker GiB |", "|---|---|---:|---:|---:|"]
    for row in report["cases"]:
        metrics = [m for m in row.get("metrics", {}).values() if "max_abs" in m]
        absolute = f"{max(m['max_abs'] for m in metrics):.6g}" if metrics else "—"
        cosine = f"{min(m['cosine'] for m in metrics):.9g}" if metrics else "—"
        lines.append(f"| {row['case']} | {row['status']} | {absolute} | {cosine} | {row.get('peak_bytes',0)/1024**3:.3f} |")
    reasons = sorted({row["reason"] for row in report["cases"] if row.get("reason")})
    if reasons:
        lines += ["", "Blocked case reasons: " + "; ".join(reasons), ""]
    lines += ["", "Tolerances (all required traces must pass elementwise and cosine gates):", "", json.dumps(TOLERANCES), "",
              "fp32: 1e-4 absolute/relative permits differing reduction order. bf16: 0.03125 absolute/relative",
              "allows eight bf16 representable steps at |reference|=1 (atol+rtol); cosine >= 0.999 constrains aggregate drift.",
              "These provisional engineering bounds are fixed before comparison and are never fitted to results.",
              "Gate amendment A1: normalization outputs are gated input-conditioned (each side's norm against the",
              "official float64 formula on its own input) plus a chained check whose atol adds the first-order",
              "propagated input error; see gold_parity.md. The plain chained result is reported, not gated.",
              "Router expert sets, PLE hash ids and QSA masks must agree exactly. See case JSON for metrics, missing traces and failures.", ""]
    return "\n".join(lines)


class Harness:
    def __init__(self, args, checkpoint, identity, prompts, runtimes):
        self.args, self.checkpoint, self.prompts = args, checkpoint, prompts
        self.out = Path(args.output).resolve()
        self.out.mkdir(parents=True, exist_ok=True)
        self.adapter_dependencies = {str(Path(p).resolve()): sha256(p) for p in args.adapter_dependency}
        self.fingerprint = digest({"schema": SCHEMA, "checkpoint": identity, "prompts": prompts,
                                   "dtype": args.dtypes, "modes": args.input_modes,
                                   "seed": args.seed, "random_scale": args.random_scale,
                                   "adapter": sha256(args.mlx_module),
                                   "adapter_dependencies": self.adapter_dependencies,
                                   "harness": {p.name: sha256(p) for p in PACKAGE.glob("*.py")}, "runtimes": runtimes,
                                   "ref_python": args.ref_python, "mlx_python": args.mlx_python,
                                   "max_gb": args.max_gb})
        self.rows = {}
        self.identity = identity
        previous = self.out / "provenance.json"
        if previous.exists():
            prior = json.loads(previous.read_text())
            if prior.get("fingerprint") != self.fingerprint:
                archived = self.out / ("provenance." + prior["fingerprint"] + ".json")
                if not archived.exists():
                    previous.replace(archived)
        write_json(self.out / "provenance.json", {"schema": SCHEMA, "fingerprint": self.fingerprint,
                   "checkpoint": identity, "prompts": prompts, "tolerances": TOLERANCES,
                   "gate_amendments": GATE_AMENDMENTS,
                   "adapter": str(args.mlx_module), "adapter_dependencies": self.adapter_dependencies,
                   "runtimes": runtimes, "scope": "prefill only"})

    def grade_saved(self, unit, dtype, directory, fp, mode, scale, reference=None, candidate=None):
        """Recompute a case verdict exclusively from worker evidence.

        A fresh case passes the results ``execute`` just returned; resume and
        offline re-grading load the authenticated ``result.json`` files.  The
        verdict depends only on the trace map and the saved arrays either way.
        """
        import numpy as np
        if reference is None:
            reference = json.loads((directory / "reference/result.json").read_text())
        if candidate is None:
            candidate = json.loads((directory / "mlx/result.json").read_text())
        report = {"schema": SCHEMA, "fingerprint": fp, "unit": unit, "case": directory.name,
                  "reference": reference, "mlx": candidate, "reference_valid": True,
                  "input_mode": mode, "random_scale": scale, "tolerances": TOLERANCES[dtype],
                  "gate_amendments": GATE_AMENDMENTS, "input_sha256": sha256(directory / "input.npy") if
                  (directory / "input.npy").is_file() else None, "status": "FAIL", "metrics": {}}
        required = required_traces(self.checkpoint.config, unit)
        missing_reference = required - reference.get("traces", {}).keys()
        if missing_reference:
            report.update(reference_valid=False, status="REFERENCE_ERROR",
                          missing_reference_traces=sorted(missing_reference))
            return report
        missing = required - candidate.get("traces", {}).keys()
        report["missing_traces"] = sorted(missing)
        report["metrics"] = self.trace_metrics(unit, dtype, directory, reference, candidate,
                                               required & candidate.get("traces", {}).keys())
        self.router_a2(unit, report, directory, reference, candidate, dtype)
        passed = not missing and all(m["pass"] for m in report["metrics"].values())
        report["status"] = "PASS" if passed else "FAIL"
        if candidate.get("metadata", {}).get("adapter_kind") == "stub":
            report["status"] = "STUB_NOT_VALIDATED"
        return report

    def trace_metrics(self, unit, dtype, directory, reference, candidate, names):
        """The per-trace comparators; ``candidate`` maps trace names to mlx/ files."""
        import numpy as np
        norms = norm_specs(self.checkpoint.config, unit) if unit == "final" or unit.isdigit() else {}
        load = lambda side, result, name: np.load(directory / side / result["traces"][name], allow_pickle=False)
        metrics = {}
        for name in sorted(names):
            a = TraceFile(directory / "reference" / reference["traces"][name])
            b = TraceFile(directory / "mlx" / candidate["traces"][name])
            if name in norms:
                metrics[name] = self.compare_norm(name, norms[name], directory, reference, candidate, dtype)
            elif name in {"ple.ngram_ids", "qsa.mask"}:
                exact = compare_exact(a, b)
                metrics[name] = {"pass": exact, "exact_agreement": exact}
            else:
                if name == "router.weights":
                    a, b = load("reference", reference, name), load("mlx", candidate, name)
                    if "router.experts" in reference["traces"] and "router.experts" in candidate["traces"]:
                        a_ids = load("reference", reference, "router.experts")
                        b_ids = load("mlx", candidate, "router.experts")
                        if a.shape == a_ids.shape and b.shape == b_ids.shape:
                            a = np.take_along_axis(a, np.argsort(a_ids, axis=-1), axis=-1)
                            b = np.take_along_axis(b, np.argsort(b_ids, axis=-1), axis=-1)
                metrics[name] = compare_arrays(a, b, dtype, exact=name == "router.experts")
        return metrics

    def router_a2(self, unit, report, directory, reference, candidate, dtype):
        """Gate amendment A2: bf16 router boundary swaps under a teacher-forced layer.

        When the bf16 expert sets differ only by admissible boundary swaps, every
        compared trace is re-gated on the candidate's ``<trace>.forced`` run: the
        same canonical layer on the same input with the reference's expert
        selection. The unforced metrics are kept as ``unforced`` (informative).
        """
        import numpy as np
        experts = report["metrics"].get("router.experts")
        names = ("router.experts", "router.logits")
        if (experts is None or experts["pass"] or dtype != "bf16" or "reason" in experts
                or any(n not in reference["traces"] or n not in candidate.get("traces", {}) for n in names)):
            return
        load = lambda side, result, name: np.load(directory / side / result["traces"][name], allow_pickle=False)
        a2 = router_boundary_swaps(load("reference", reference, "router.experts"), load("mlx", candidate, "router.experts"),
                                   load("reference", reference, "router.logits"), load("mlx", candidate, "router.logits"),
                                   dtype)
        report["metrics"]["router.experts"] = dict(a2, unforced=experts)
        report["a2_admissible_swaps"] = a2.get("admissible_swaps", 0)
        if not a2["pass"]:
            return
        graded = set(report["metrics"])
        forced = {"traces": {n: candidate["traces"][n + ".forced"] for n in graded if n + ".forced" in candidate["traces"]}}
        metrics = self.trace_metrics(unit, dtype, directory, reference, forced, forced["traces"].keys())
        # Under forcing the selection must be exactly the reference's.
        experts_forced = metrics.pop("router.experts", {"pass": False, "reason": "a2_forced_trace_missing"})
        report["metrics"]["router.experts"]["forced"] = experts_forced
        report["metrics"]["router.experts"]["pass"] = bool(a2["pass"] and experts_forced["pass"])
        for name in sorted(graded - {"router.experts"}):
            unforced = report["metrics"][name]
            if name in metrics:
                report["metrics"][name] = dict(metrics[name], gate="A2-teacher-forced",
                                               forced_rows=a2["admissible_rows"], unforced=unforced)
            else:
                report["metrics"][name] = {"pass": False, "gate": "A2-teacher-forced", "unforced": unforced,
                                           "reason": "a2_forced_trace_missing: re-run with the A2 worker"}

    def case(self, unit, dtype, prompt, mode, hidden, compare=True, scale=None):
        import numpy as np
        case = f"{prompt['name']}-{dtype}-{mode}"
        directory = self.out / (f"layer-{int(unit):03d}" if unit.isdigit() else unit) / case
        report_path = directory / "report.json"
        fp = digest([self.fingerprint, unit, case, sha256(hidden) if hidden else None, compare, scale,
                     getattr(self.args, "worker_extra", {})])
        if self.args.resume and reusable(report_path, fp):
            # report.json is deliberately ignored: it is mutable presentation,
            # not evidence.  Array/request/result hashes are fingerprint-bound
            # and the current comparator produces a fresh verdict.
            if compare:
                report = self.grade_saved(unit, dtype, directory, fp, mode, scale)
            else:
                reference = json.loads((directory / "reference/result.json").read_text())
                required = required_traces(self.checkpoint.config, unit)
                missing = required - reference.get("traces", {}).keys()
                report = {"schema": SCHEMA, "fingerprint": fp, "unit": unit, "case": case,
                          "reference": reference, "reference_valid": not missing, "input_mode": mode,
                          "random_scale": scale, "status": "REFERENCE_CHAIN_ONLY" if not missing else "REFERENCE_ERROR",
                          "metrics": {}, "missing_reference_traces": sorted(missing)}
            # Presentation only: the workers' self-sampled peaks from the
            # hash-bound result.json (coordinator RSS sampling is not saved).
            report["peak_bytes"] = max(worker_peak(report["reference"]), worker_peak(report.get("mlx", {})))
            report["artifacts"] = artifacts(directory)
            report["evidence_digest"] = digest({"fingerprint": fp, "artifacts": report["artifacts"]})
            write_json(report_path, report)
            print(f"Resume/re-gate {unit}/{case}: {report['status']}", flush=True)
        else:
            if directory.exists() and any(directory.iterdir()):
                # Preserve earlier attempts; never turn stale result.json into success.
                suffix = 1
                previous = directory.with_name(directory.name + f".attempt-{suffix}")
                while previous.exists():
                    suffix += 1; previous = directory.with_name(directory.name + f".attempt-{suffix}")
                directory.rename(previous)
            directory.mkdir(parents=True, exist_ok=True)
            case_input = None
            if hidden is not None:
                case_input = directory / "input.npy"
                shutil.copyfile(hidden, case_input)
            request = {"schema": SCHEMA, "checkpoint": str(self.checkpoint.root), "unit": unit,
                       "dtype": dtype, "input_ids": [prompt["input_ids"]], "hidden": str(case_input) if case_input else None,
                       "input_mode": mode, "random_scale": scale, "seed": self.args.seed,
                       "mlx_module": str(Path(self.args.mlx_module).resolve()),
                       "adapter_dependencies": self.adapter_dependencies, "backend": "reference",
                       "max_memory_bytes": int(self.args.max_gb*1024**3), "threads": 2,
                       "shard_guards": self.identity.get("stamps"),
                       "config_digest": digest(self.checkpoint.config),
                       "weight_map_digest": digest(self.checkpoint.weight_map)}
            request.update(getattr(self.args, "worker_extra", {}))
            print(f"Reference {unit}/{case}", flush=True)
            reference = execute(self.args.ref_python, request, directory / "reference", self.args.max_gb, self.args.timeout)
            candidate = {}
            report = {"schema": SCHEMA, "fingerprint": fp, "unit": unit, "case": case,
                      "reference": reference, "reference_valid": "error" not in reference,
                      "input_mode": mode, "random_scale": scale, "tolerances": TOLERANCES[dtype],
                      "gate_amendments": GATE_AMENDMENTS,
                      "input_sha256": sha256(case_input) if case_input else None,
                      "status": "REFERENCE_ERROR", "metrics": {}}
            if "error" not in reference:
                missing_reference = required_traces(self.checkpoint.config, unit) - reference["traces"].keys()
                if missing_reference:
                    report["reference_valid"] = False
                    report["missing_reference_traces"] = sorted(missing_reference)
                elif compare:
                    print(f"MLX {unit}/{case}", flush=True)
                    mlx_request = dict(request, backend="mlx")
                    if "router.experts" in reference["traces"]:
                        # A2: the candidate adds a teacher-forced MoE pass only
                        # if its expert sets differ from these.
                        forced = directory / "reference" / reference["traces"]["router.experts"]
                        mlx_request.update(forced_experts=str(forced), forced_experts_sha256=sha256(forced))
                    candidate = execute(self.args.mlx_python, mlx_request, directory / "mlx", self.args.max_gb, self.args.timeout)
                    report["mlx"] = candidate
                    if "error" in candidate:
                        report["status"] = "MLX_ERROR"
                    else:
                        report = self.grade_saved(unit, dtype, directory, fp, mode, scale, reference, candidate)
                else:
                    report["status"] = "REFERENCE_CHAIN_ONLY"
            report["peak_bytes"] = max(reference.get("observed_peak_bytes", reference.get("peak_rss_bytes", 0)),
                                       candidate.get("observed_peak_bytes", 0))
            report["artifacts"] = artifacts(directory)
            report["evidence_digest"] = digest({"fingerprint": fp, "artifacts": report["artifacts"]})
            write_json(report_path, report)
        if compare:
            self.rows.setdefault(unit, []).append(report)
            self.publish(unit)
        if report["reference_valid"]:
            return directory / "reference" / "output.npy"
        return None

    def compare_norm(self, name, spec, directory, reference, candidate, dtype):
        """Gate amendment A1; the weight comes from the checkpoint, never a worker."""
        traces = {}
        for side, result in (("reference", reference), ("mlx", candidate)):
            for key in ("input", "gate"):
                if key in spec:
                    trace = result["traces"].get(spec[key])
                    if trace is None:
                        return {"pass": False, "reason": f"missing_{side}_{key}", "gate": "A1-input-conditioned"}
                    traces[side, key] = TraceFile(directory / side / trace)
        try:
            weight = self.checkpoint.read(self.checkpoint.prefix + spec["weight"], framework="numpy", dtype="fp32")
        except (KeyError, OSError, ValueError) as error:
            return {"pass": False, "reason": f"norm_weight_unavailable: {error}", "gate": "A1-input-conditioned"}
        return compare_norm(TraceFile(directory / "reference" / reference["traces"][name]),
                            TraceFile(directory / "mlx" / candidate["traces"][name]),
                            traces["reference", "input"], traces["mlx", "input"], weight, spec, dtype,
                            traces.get(("reference", "gate")), traces.get(("mlx", "gate")))

    def blocked(self, unit, dtype, prompt, reason):
        self.rows.setdefault(unit, []).append({"unit": unit, "case": f"{prompt['name']}-{dtype}-real",
                                                "status": "BLOCKED_REAL_INPUT", "reason": reason})
        self.publish(unit)

    def publish(self, unit, finished=False):
        cases = self.rows[unit]
        expected = len(self.prompts)*len(set(self.args.dtypes.split(",")))
        if unit != "embed":
            expected *= len(set(self.args.input_modes.split(",")))
        complete = len(cases) == expected
        status = "PASS" if complete and all(row["status"] == "PASS" for row in cases) else (
            "INCOMPLETE_OR_FAILED" if finished or any(row["status"] != "PASS" for row in cases) else "IN_PROGRESS")
        report = {"schema": SCHEMA, "unit": unit, "status": status, "fingerprint": self.fingerprint,
                  "expected_cases": expected, "completed_cases": len(cases),
                  "a2_admissible_swaps": sum(row.get("a2_admissible_swaps", 0) for row in cases), "cases": cases}
        name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
        write_json(self.out / (name + ".json"), report)
        temp = self.out / (name + ".md.tmp")
        temp.write_text(markdown_report(report)); temp.replace(self.out / (name + ".md"))
        return report

    def run(self, layers):
        import numpy as np
        c = self.checkpoint.text
        endpoints = not self.args.no_endpoints
        modes = self.args.input_modes.split(",")
        units = [str(i) for i in layers] + (["final", "head"] if endpoints else [])
        for dtype in self.args.dtypes.split(","):
            for prompt in self.prompts:
                real_inputs = {}
                if "real" in modes:
                    current = self.case("embed", dtype, prompt, "real", None, compare=endpoints)
                    stop = c["num_hidden_layers"] if endpoints else max(layers)+1
                    for i in range(stop):
                        unit = str(i)
                        if current is None:
                            if i in layers:
                                self.blocked(unit, dtype, prompt, "missing or failed reference predecessor; no synthetic substitute")
                            continue
                        real_inputs[unit] = current
                        current = self.case(unit, dtype, prompt, "real", current, compare=i in layers)
                    if endpoints:
                        if current is not None:
                            real_inputs["final"] = current
                            current = self.case("final", dtype, prompt, "real", current)
                        else:
                            self.blocked("final", dtype, prompt, "reference chain incomplete")
                        if current is not None:
                            real_inputs["head"] = current
                            self.case("head", dtype, prompt, "real", current)
                        else:
                            self.blocked("head", dtype, prompt, "reference chain incomplete")
                if "random" in modes:
                    if endpoints and "real" not in modes:
                        self.case("embed", dtype, prompt, "tokens", None)
                    for unit in units:
                        width = c["hidden_size"] * (1 if unit == "head" else c["hc_count"])
                        scale = self.args.random_scale
                        if unit in real_inputs:
                            activation = TraceFile(real_inputs[unit])
                            square_sum = 0.0
                            for first in range(0, activation.size, 262144):
                                values = activation[first:first+262144].astype(np.float64)
                                square_sum += float(np.dot(values, values))
                            scale = math.sqrt(square_sum / activation.size)
                        shape = (1, len(prompt["input_ids"]), width)
                        if math.prod(shape)*4 > self.args.max_gb*1024**3/16:
                            self.rows.setdefault(unit, []).append({"unit": unit, "case": f"{prompt['name']}-{dtype}-random",
                                                                  "status": "INPUT_MEMORY_GUARD"})
                            self.publish(unit)
                            continue
                        rng = np.random.default_rng(int(digest([self.args.seed, unit, prompt["name"]])[:16], 16))
                        hidden = rng.standard_normal(shape, dtype=np.float32)
                        hidden *= scale
                        path = self.out / "inputs" / f"{unit}-{dtype}-{prompt['name']}.npy"
                        path.parent.mkdir(exist_ok=True)
                        if not path.exists() or not np.array_equal(np.load(path, allow_pickle=False), hidden):
                            np.save(path, hidden, allow_pickle=False)
                        self.case(unit, dtype, prompt, "random", path, scale=scale)
        reports = []
        for unit in self.rows:
            report = self.publish(unit, finished=True)
            reports.append({"unit": unit, "status": report["status"]})
        summary = {"schema": SCHEMA, "fingerprint": self.fingerprint, "units": reports,
                   "status": "PASS" if reports and all(r["status"] == "PASS" for r in reports) else "INCOMPLETE_OR_FAILED",
                   "coverage": {"layers": layers, "input_modes": modes, "dtypes": self.args.dtypes.split(","),
                                "endpoints": endpoints, "full_48_layer_gold": False}}
        summary["coverage"]["full_48_layer_gold"] = (summary["status"] == "PASS" and c["num_hidden_layers"] == 48 and layers == list(range(48)) and endpoints and
                                                            set(modes) == {"real", "random"} and set(self.args.dtypes.split(",")) == {"fp32", "bf16"})
        write_json(self.out / "summary.json", summary)
        return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--mlx-module", default=str(PACKAGE / "stub_adapter.py"), help="local adapter .py implementing gold/v1")
    parser.add_argument("--adapter-dependency", action="append", default=[], help="hash imported port sources for safe resume (repeatable)")
    parser.add_argument("--ref-python", default="/private/tmp/jwsol/venv-ref/bin/python")
    parser.add_argument("--mlx-python", default="/private/tmp/jwsol/venv-mlx/bin/python")
    parser.add_argument("--layers", default="all", help="zero-based comma-separated layer ids, or all")
    parser.add_argument("--no-endpoints", action="store_true")
    parser.add_argument("--input-modes", default="random,real")
    parser.add_argument("--dtypes", default="fp32,bf16")
    parser.add_argument("--prompts-json", help="list of {name, input_ids, optional text/tokenizer provenance}")
    parser.add_argument("--seed", type=int, default=20261105)
    parser.add_argument("--random-scale", type=float, default=1.0, help="fallback RMS when real layer activations unavailable")
    parser.add_argument("--max-gb", type=float, default=12)
    parser.add_argument("--timeout", type=float, default=900, help="seconds per single worker")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--make-tiny", action="store_true", help="create tiny random BF16 checkpoint via official save_pretrained first")
    args = parser.parse_args(argv)
    if not set(args.dtypes.split(",")) <= {"fp32", "bf16"} or not set(args.input_modes.split(",")) <= {"random", "real"}:
        parser.error("unknown dtype or input mode")
    if len(set(args.dtypes.split(","))) != len(args.dtypes.split(",")) or len(set(args.input_modes.split(","))) != len(args.input_modes.split(",")):
        parser.error("duplicate dtype or input mode")
    if not 0 < args.max_gb <= 110 or args.timeout <= 0 or not 0 < args.random_scale < 100:
        parser.error("invalid memory/timeout/scale")
    root, out = Path(args.checkpoint).resolve(), Path(args.output).resolve()
    if "restricted" in root.parts or "restricted" in out.parts:
        parser.error("restricted paths refused")
    if out.exists() and any(out.iterdir()) and not args.resume:
        parser.error("output exists: use --resume, or choose a fresh output directory")
    if args.make_tiny and not (root / "config.json").exists():
        request = {"backend": "tiny", "checkpoint": str(root)}
        result = execute(args.ref_python, request, out / "tiny-creation", args.max_gb, args.timeout)
        if "error" in result:
            print(json.dumps(result)); return 2
    runtimes = {"reference": runtime_identity(args.ref_python), "mlx": runtime_identity(args.mlx_python)}
    from .core import REFERENCE_VERSION
    if runtime_version(runtimes["reference"], "transformers") != REFERENCE_VERSION:
        parser.error(f"reference requires transformers {REFERENCE_VERSION}")
    checkpoint = IndexedCheckpoint(root)
    layers = parse_layers(args.layers, checkpoint.text["num_hidden_layers"])
    prompts = load_prompts(args.prompts_json, checkpoint.text)
    identity = checkpoint_identity(checkpoint, layers, "real" in args.input_modes.split(","), not args.no_endpoints,
                                   lambda s: print(s, flush=True))
    harness = Harness(args, checkpoint, identity, prompts, runtimes)
    summary = harness.run(layers)
    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] == "PASS" else 2
