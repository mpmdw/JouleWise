#!/usr/bin/env python3
"""Saturday Flash-Next validation. Nothing here is an energy measurement.

All commands support --dry-run (no imports of MLX/HF, filesystem reads, writes,
or network). Live commands require --validation-only, and all large artifacts
must be on /Volumes/JW-EXT. See docs/align/qwen4_exp_port/mbp_live.md.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import plistlib
import re
import resource
import stat
import subprocess
import sys
import time
import shutil
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
REPO_ID = "Qwen/Qwen3.8-Flash-Next"
REVISION = "de4b8e4d43b917e7706784d8bb445c9af86a3540"
VOLUME = Path("/Volumes/JW-EXT")
CONTEXTS = (4096, 16384, 40960)
EFFORTS = ("low", "medium", "xhigh")  # The official template's supported values.
PREDICTED_PEAK = {"maxfit": 112.7e9, "maxfit5": 97.6e9}
PLE_CAP = 21.5e9
METAL_CAP = 115.4e9
SMALL_FILES = ("config.json", "model.safetensors.index.json", "tokenizer.json",
               "tokenizer_config.json", "special_tokens_map.json", "generation_config.json",
               "chat_template.jinja", "vocab.json", "merges.txt")
NATIVE = ("memory", "quality", "benchmark", "hosted", "performance", "paging")


def utc_now():
    return datetime.now(timezone.utc)


def timing(started, finished, total_bytes):
    elapsed = max(0.0, (finished - started).total_seconds())
    return {"started_utc": started.isoformat(), "finished_utc": finished.isoformat(),
            "elapsed_seconds": elapsed, "total_bytes": int(total_bytes),
            "mean_MBps": (int(total_bytes) / 1e6 / elapsed) if elapsed else None}


def write_json(path, data):
    with Path(path).open("x") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, allow_nan=False)
        f.write("\n")


def raw_sha256(path):
    # F_NOCACHE avoids warming the 102.4 GB PLE table during verification.
    import fcntl
    with Path(path).open("rb") as f:
        if sys.platform == "darwin":
            fcntl.fcntl(f.fileno(), 48, 1)  # Darwin F_NOCACHE
        h = hashlib.sha256()
        while block := f.read(8 * 2**20):
            h.update(block)
    return h.hexdigest()


def external(path):
    path = Path(path)
    # Reject the lexical restricted component before following any links.
    if "restricted" in path.parts:
        raise ValueError("restricted paths are forbidden")
    resolved = path.resolve()
    if VOLUME not in resolved.parents or "restricted" in resolved.parts:
        raise ValueError(f"live artifact must be inside {VOLUME}: {path}")
    return resolved


def volume_info():
    info = plistlib.loads(subprocess.check_output(["diskutil", "info", "-plist", str(VOLUME)]))
    if info.get("MountPoint") != str(VOLUME) or "apfs" not in str(info.get("FilesystemType", "")).lower():
        raise ValueError("JW-EXT must be the mounted APFS volume")
    return info


# Night chain, dead-man and night probes (com.joulewise.night*), plus the
# block-6 collection loop and its wake jobs, which arm/collect measurements.
MEASUREMENT_AGENT_PREFIXES = ("com.joulewise.night", "com.joulewise.b6loop", "com.joulewise.b6wake")


def measurement_agents_loaded():
    """Loaded launchd measurement agents (night chain, b6 loop, probes).

    A validation day that overruns must never share the Mac with a scheduled
    measurement window, so a loaded night agent refuses every live command.
    Unload per the lead's procedure before validation; restore after eject.
    """
    listing = subprocess.run(["launchctl", "list"], capture_output=True, text=True, timeout=10)
    if listing.returncode != 0:
        raise ValueError("cannot list launchd agents to rule out a measurement window")
    labels = [line.split("\t")[-1].strip() for line in listing.stdout.splitlines()[1:]]
    return sorted(label for label in labels if label.startswith(MEASUREMENT_AGENT_PREFIXES))


def cache_environment():
    base = VOLUME / "flashnext"
    values = {"HF_HOME": str(base / "hf"), "HF_HUB_CACHE": str(base / "hf/hub"),
              "HF_XET_CACHE": str(base / "hf/xet"), "HF_XET_CHUNK_CACHE_SIZE_BYTES": "0",
              "HF_XET_SHARD_CACHE_SIZE_LIMIT": str(2**30),
              "TMPDIR": str(base / "tmp"), "TOKENIZERS_PARALLELISM": "false"}
    os.environ.update(values)
    for key in ("HF_HOME", "HF_HUB_CACHE", "HF_XET_CACHE", "TMPDIR"):
        external(values[key]).mkdir(parents=True, exist_ok=True)
    return values


def verify_source(snapshot, metadata, *, expected_shards=131):
    """Bind all source bytes to pinned HF metadata, not just a local checksum.

    LFS files have ordinary SHA-256; small Git files have git-blob SHA-1.
    The receipt records ordinary SHA-256 for both. Metadata comes from the
    pinned model_info response and is preserved in the download receipt.
    """
    snapshot = Path(snapshot)
    index = json.loads((snapshot / "model.safetensors.index.json").read_text())
    shards = sorted(set(index["weight_map"].values()))
    if len(shards) != expected_shards or any(Path(n).name != n for n in shards):
        raise ValueError("source shard inventory mismatch")
    needed = set(shards) | {"config.json", "model.safetensors.index.json", "tokenizer.json",
                            "tokenizer_config.json", "chat_template.jinja"}
    if not needed <= set(metadata):
        raise ValueError("missing pinned source metadata")
    result = {}
    for name, meta in sorted(metadata.items()):
        if Path(name).name != name or name in (".", ".."):
            raise ValueError("non-flat source name")
        path = snapshot / name
        if path.stat().st_size != meta["size"]:
            raise ValueError(f"source size mismatch: {name}")
        digest = raw_sha256(path)
        if meta.get("sha256"):
            matches = digest == meta["sha256"]
        else:
            if path.stat().st_size > 32 * 2**20:
                raise ValueError("large source requires an LFS SHA-256")
            blob = path.read_bytes()  # Only small Git-backed files, never weight shards.
            matches = hashlib.sha1(f"blob {len(blob)}\0".encode() + blob).hexdigest() == meta["blob_id"]
        if not matches:
            raise ValueError(f"source digest mismatch: {name}")
        result[name] = digest
    return result


def verify_source_all(snapshot, metadata, *, expected_shards=131):
    """Return all per-file failures without weakening ``verify_source``."""
    snapshot = Path(snapshot)
    failures, digests = [], {}
    try:
        index = json.loads((snapshot / "model.safetensors.index.json").read_text())
        shards = sorted(set(index["weight_map"].values()))
        if len(shards) != expected_shards or any(Path(n).name != n for n in shards):
            failures.append({"file": "model.safetensors.index.json", "reason": "source shard inventory mismatch"})
    except (OSError, ValueError, KeyError, TypeError) as exc:
        failures.append({"file": "model.safetensors.index.json", "reason": str(exc)})
    for name, meta in sorted(metadata.items()):
        try:
            if Path(name).name != name or name in (".", ".."):
                raise ValueError("non-flat source name")
            path = snapshot / name
            if path.stat().st_size != int(meta["size"]):
                raise ValueError("source size mismatch")
            digest = raw_sha256(path)
            if meta.get("sha256"):
                matches = digest == meta["sha256"]
            else:
                if path.stat().st_size > 32 * 2**20:
                    raise ValueError("large source requires an LFS SHA-256")
                blob = path.read_bytes()
                matches = hashlib.sha1(f"blob {len(blob)}\0".encode() + blob).hexdigest() == meta["blob_id"]
            if not matches:
                raise ValueError("source digest mismatch")
            digests[name] = digest
        except (OSError, ValueError, KeyError) as exc:
            failures.append({"file": name, "reason": str(exc)})
    return digests, failures


SOURCE_BUDGET = 650e9  # source ~360 + maxfit ~211 + hashing/conversion headroom


def download_free_space_need(metadata, blobs):
    """Free bytes the download requires: 650 GB, less allocated cached blobs.

    An interrupted 3-5 h transfer must be able to resume: its partial blobs
    already occupy part of the 650 GB budget. Credit is allocated blocks of
    regular files in this repo's external blob store (sparse or partial files
    count only what they hold), capped at the pinned source size.
    """
    total = sum(int(m["size"]) for m in metadata.values())
    held = 0
    if blobs.is_dir():
        for path in blobs.iterdir():
            info = path.lstat()
            if stat.S_ISREG(info.st_mode):
                held += info.st_blocks * 512
    return SOURCE_BUDGET - min(held, total)


def download(args):
    from huggingface_hub import HfApi, snapshot_download
    info = HfApi().model_info(REPO_ID, revision=REVISION, files_metadata=True)
    if info.sha != REVISION:
        raise ValueError("HF resolved a different revision")
    metadata = {}
    for item in info.siblings:
        name = item.rfilename
        if name in SMALL_FILES or re.fullmatch(r"model-\d{5}-of-00131\.safetensors", name):
            metadata[name] = {"size": item.size, "blob_id": item.blob_id,
                              "sha256": item.lfs.sha256 if item.lfs else None}
    if getattr(args, "plan_only", False):
        return {"schema": "qwen4exp-source-plan/v1", "repo": REPO_ID, "revision": REVISION,
                "metadata": metadata, "total_bytes": sum(int(m["size"]) for m in metadata.values())}
    # Keep checkpoint + one ~211 GB build + hashing/conversion headroom. A
    # resumed transfer is credited the source bytes already in the cache.
    blobs = Path(os.environ["HF_HUB_CACHE"]) / ("models--" + REPO_ID.replace("/", "--")) / "blobs"
    need = download_free_space_need(metadata, external(blobs))
    st = os.statvfs(VOLUME)
    if st.f_bavail * st.f_frsize < need:
        raise ValueError(f"need >={need / 1e9:.1f} GB free on JW-EXT for source + maxfit + headroom "
                         f"({SOURCE_BUDGET / 1e9:.0f} GB on a fresh start, less source bytes already cached)")
    snapshot = external(snapshot_download(REPO_ID, revision=REVISION, allow_patterns=list(metadata),
                                          cache_dir=os.environ["HF_HUB_CACHE"], max_workers=getattr(args, "max_workers", 2)))
    for name in metadata:
        external(snapshot / name)  # HF symlinks must stay on this external cache.
    digests = verify_source(snapshot, metadata)
    return {"schema": "qwen4exp-source/v1", "repo": REPO_ID, "revision": REVISION,
            "snapshot": str(snapshot), "metadata": metadata, "sha256": digests,
            "max_workers": getattr(args, "max_workers", 2)}


def convert(args):
    import align_convert_qwen4_exp as converter
    receipt = json.loads(external(args.source_receipt).read_text())
    if receipt["revision"] != REVISION or receipt["repo"] != REPO_ID:
        raise ValueError("wrong source identity")
    source = external(receipt["snapshot"])
    for name in receipt["metadata"]:
        external(source / name)
    if verify_source(source, receipt["metadata"]) != receipt["sha256"]:
        raise ValueError("source differs from download receipt")
    artifact = external(args.artifact)
    if artifact.exists():
        raise ValueError("conversion output must be new; preserve failed attempts")
    need = 240e9 if args.profile == "maxfit" else 225e9
    st = os.statvfs(VOLUME)
    if st.f_bavail * st.f_frsize < need:
        raise ValueError("insufficient free external disk space for this build")
    progress_path = args.out.parent / "convert.progress.jsonl"
    converter.convert(source, artifact, profile=args.profile, group_size=64, ple_storage="bf16",
                      progress_path=progress_path)
    # Plain sha256 sidecar lives OUTSIDE strict converter inventory. Converter
    # manifest v2 uses SHA256(concat(chunk SHA256s)) for files >256 MiB.
    sums = Path(str(args.out) + ".SHA256SUMS")
    with sums.open("x") as f:
        for path in sorted(artifact.iterdir()):
            if path.is_file():
                f.write(f"{raw_sha256(path)}  {path.name}\n")
    return {"artifact": str(artifact), "profile": args.profile,
            "source_receipt_sha256": raw_sha256(args.source_receipt),
            "manifest_sha256": raw_sha256(artifact / "manifest.json"),
            "module_sha256": converter.MODULE_SHA256, "plain_sha256s": str(sums)}


def tree_bytes(path):
    total = 0
    if Path(path).is_dir():
        for root, _, files in os.walk(path):
            for name in files:
                try:
                    total += (Path(root) / name).stat().st_size
                except FileNotFoundError:
                    pass
    return total


def progress(args):
    plan = json.loads(Path(args.metadata).read_text())
    expected = int(plan.get("total_bytes") or sum(int(v["size"]) for v in plan["metadata"].values()))
    hub = Path(os.environ["HF_HUB_CACHE"])
    blobs = hub / ("models--" + REPO_ID.replace("/", "--")) / "blobs"
    xet = Path(os.environ.get("HF_XET_CACHE", ""))
    output = args.progress_path or (args.run_dir / "download.progress.jsonl")
    samples = []
    while True:
        now = utc_now()
        downloaded = tree_bytes(blobs) + tree_bytes(xet)
        samples.append((now.timestamp(), downloaded))
        rates = {}
        for minutes in (1, 5, 15):
            prior = next((s for s in samples if s[0] >= now.timestamp() - minutes * 60), samples[0])
            dt = now.timestamp() - prior[0]
            rates[f"MBps_{minutes}m"] = max(0, downloaded - prior[1]) / 1e6 / dt if dt else None
        rate = next((rates[k] for k in ("MBps_15m", "MBps_5m", "MBps_1m") if rates[k]), None)
        eta = max(0, expected - downloaded) / 1e6 / rate if rate else None
        row = {"utc_time": now.isoformat(), "bytes_present": downloaded, "total_bytes": expected,
               **rates, "eta_seconds": eta, "jw_ext_free_bytes": shutil.disk_usage(args.volume).free,
               "phase": "download"}
        convert_file = args.run_dir / "convert.progress.jsonl"
        if convert_file.exists():
            lines = convert_file.read_text().splitlines()
            if lines:
                latest = json.loads(lines[-1]); elapsed = latest.get("monotonic_elapsed", 0)
                done, total = latest.get("bytes_written", 0), latest.get("bytes_total_expected", 0)
                eta = (total - done) * elapsed / done if done else None
                row.update(phase="convert", convert=latest, eta_seconds=eta)
        past = False
        if args.cutoff and eta is not None:
            cutoff = datetime.fromisoformat(args.cutoff.replace("Z", "+00:00"))
            past = now.timestamp() + eta + args.convert_budget_h * 3600 + 3600 > cutoff.timestamp()
        row["eta_past_cutoff"] = past
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("a") as stream:
            stream.write(json.dumps(row, separators=(",", ":")) + "\n")
        print(json.dumps(row), flush=True)
        if past:
            print("ETA_PAST_CUTOFF", flush=True)
        if args.once:
            return row
        time.sleep(args.interval)


def quarantine_bad(snapshot, failures, base):
    destination = Path(base) / "quarantine" / utc_now().strftime("%Y%m%dT%H%M%SZ")
    moved = []
    for failure in failures:
        link = Path(snapshot) / failure["file"]
        if not link.is_symlink():
            continue
        target = link.resolve()
        destination.mkdir(parents=True, exist_ok=True)
        dest = destination / target.name
        if target.exists() and not dest.exists():
            shutil.move(str(target), dest)
            moved.append(str(dest))
        link.unlink()
    return moved


def parse_vm_stat(text):
    page = re.search(r"page size of (\d+) bytes", text)
    if not page:
        raise ValueError("vm_stat page size missing")
    fields = {k.strip(): int(v) for k, v in re.findall(r"^([^:\n]+):\s+(\d+)\.?$", text, re.M)}
    if "Swapouts" not in fields or "Pages occupied by compressor" not in fields:
        raise ValueError("vm_stat counters missing")
    return {"page_bytes": int(page[1]), "swapouts": fields["Swapouts"],
            "compressor_bytes": fields["Pages occupied by compressor"] * int(page[1]),
            "file_backed_bytes": fields.get("File-backed pages", 0) * int(page[1])}


def sample_system(pid=None):
    def output(argv):
        return subprocess.check_output(argv, text=True, timeout=10)
    vm = output(["vm_stat"])
    pressure = output(["memory_pressure", "-Q"])
    free = re.search(r"System-wide memory free percentage:\s*(\d+)%", pressure)
    swap = output(["sysctl", "-n", "vm.swapusage"])
    used = re.search(r"used\s*=\s*([\d.]+)([MG])", swap)
    if not free or not used:
        raise ValueError("cannot parse memory_pressure/vm.swapusage")
    result = {**parse_vm_stat(vm), "time": time.time(), "memory_pressure_raw": pressure,
              "vm_stat_raw": vm, "swapusage_raw": swap,
              "free_percent": int(free[1]),
              "pressure_level": int(output(["sysctl", "-n", "kern.memorystatus_vm_pressure_level"])),
              "swap_used_bytes": float(used[1]) * (2**20 if used[2] == "M" else 2**30)}
    if pid is not None:
        # ps can lose a race to a normally exiting child.
        ps = subprocess.run(["ps", "-o", "rss=", "-p", str(pid)], capture_output=True, text=True)
        result["rss_bytes"] = int(ps.stdout.strip() or 0) * 1024
    return result


def unsafe_memory(before, now):
    if now["swap_used_bytes"] > 0 or now["swapouts"] != before["swapouts"]:
        return "swap present or swapouts changed"
    # Separate reasons: a free-percentage-only stop (no swap, normal kernel
    # pressure) is a headroom margin, which the lead must distinguish from
    # real pressure before ruling maxfit unfit.
    if now["pressure_level"] != 1:
        return f"kernel memory pressure level {now['pressure_level']} (not normal 1)"
    if now["free_percent"] < 10:
        return f"memory_pressure free percentage {now['free_percent']} below 10"
    if now["compressor_bytes"] - before["compressor_bytes"] > 2e9:
        return "compressor grew by more than 2 GB"
    return None


def terminate(child):
    child.terminate()
    try:
        child.wait(timeout=5)
    except subprocess.TimeoutExpired:
        child.kill()
        child.wait()


def supervise(args):
    """Watch loading AND execution from a separate process; fail closed.

    No signal-handler abort waits for the next Python callback from Metal.
    System pressure/swap checks remain active during a long native eval.
    """
    before = sample_system()
    if reason := unsafe_memory(before, before):
        raise ValueError("preflight: " + reason)
    worker_out = Path(str(args.out) + ".worker.json")
    log_path = Path(str(args.out) + ".worker.log")
    monitor_path = Path(str(args.out) + ".monitor.jsonl")
    if any(p.exists() for p in (worker_out, log_path, monitor_path,
                                Path(str(args.out) + ".rungs.jsonl"),
                                Path(str(args.out) + ".hosted.json"))):
        raise ValueError("use a fresh output basename")
    argv = [sys.executable, "-B", str(Path(__file__).resolve()), *sys.argv[1:], "--worker"]
    samples, reason, child = [], None, None
    with log_path.open("x") as log, monitor_path.open("x") as monitor:
        def record(sample):
            samples.append(sample)
            monitor.write(json.dumps(sample) + "\n")
            monitor.flush()
        record(before)
        try:
            child = subprocess.Popen(argv, stdout=log, stderr=subprocess.STDOUT)
            while child.poll() is None:
                sample = sample_system(child.pid)
                record(sample)
                if reason := unsafe_memory(before, sample):
                    terminate(child)
                    break
                time.sleep(args.poll_seconds)
            record(sample_system())
            reason = reason or unsafe_memory(before, samples[-1])
        except BaseException:
            if child is not None and child.poll() is None:
                terminate(child)
            raise
    result = {"schema": "qwen4exp-mbp-live/v1", "command": args.command,
              "validation_only": True, "profile": args.profile, "monitor": str(monitor_path),
              "worker_log": str(log_path), "swapouts_delta": samples[-1]["swapouts"] - before["swapouts"],
              "initial_swap_used_bytes": before["swap_used_bytes"],
              "min_free_percent": min(s["free_percent"] for s in samples),
              "pressure_levels": sorted(set(s["pressure_level"] for s in samples)),
              "max_compressor_growth_bytes": max(s["compressor_bytes"] - before["compressor_bytes"] for s in samples),
              "max_rss_bytes": max(s.get("rss_bytes", 0) for s in samples),
              "abort": reason, "worker_returncode": child.returncode,
              "verdict": "aborted" if reason or child.returncode else "completed"}
    if worker_out.exists():
        result["results"] = json.loads(worker_out.read_text())
        if result["results"].get("verdict") in ("fail", "incomplete"):
            result["verdict"] = result["results"]["verdict"]
    else:
        result["verdict"] = "aborted"
    return result


def record_disk(args, label):
    info = volume_info()
    device = args.disk_device
    if not device or not re.fullmatch(r"disk\d+", device):
        raise ValueError("paging requires --disk-device diskN (external PHYSICAL whole disk)")
    disk_info = plistlib.loads(subprocess.check_output(["diskutil", "info", "-plist", device]))
    apfs = plistlib.loads(subprocess.check_output(["diskutil", "apfs", "list", "-plist"]))
    stores = physical_stores(apfs, info["DeviceIdentifier"])
    if (disk_info.get("Internal", True) or not disk_info.get("Whole", False)
            or disk_info.get("VirtualOrPhysical") != "Physical" or stores != {device}):
        raise ValueError("iostat device must be JW-EXT's single external physical whole disk")
    # First iostat -I report is cumulative since boot; retain both raw outputs.
    raw = subprocess.check_output(["iostat", "-Id", device], text=True, timeout=10)
    path = str(args.out) + f".iostat-{label}.json"
    write_json(path,
               {"time": time.time(), "device": device, "diskutil_volume": info,
                "diskutil_device": disk_info, "iostat_raw": raw})
    return path


def physical_stores(apfs, volume_device):
    for container in apfs.get("Containers", []):
        if any(v.get("DeviceIdentifier") == volume_device for v in container.get("Volumes", [])):
            stores = {s.get("DeviceIdentifier", "") for s in container.get("PhysicalStores", [])}
            if not stores or any(not re.fullmatch(r"disk\d+s\d+", s) for s in stores):
                raise ValueError("cannot identify APFS physical-store ancestry")
            return {re.sub(r"s\d+$", "", s) for s in stores}
    raise ValueError("JW-EXT volume absent from diskutil APFS ancestry")


def resident_pages(table):
    """Darwin mincore: file-page residency, without faulting table bytes in.

    This includes shared OS cache pages. It is NOT private/wired GPU memory
    and is NOT summed with process RSS or Metal allocations.
    """
    import mmap
    mm = table._mm
    if mm is None:
        raise ValueError("Saturday recipe requires mmap PLE")
    page = mmap.PAGESIZE
    start = int(mm.ctypes.data)
    base = start - start % page
    count = math.ceil((start - base + mm.nbytes) / page)
    vec = (ctypes.c_ubyte * count)()
    libc = ctypes.CDLL(None, use_errno=True)
    libc.mincore.argtypes = (ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p)
    libc.mincore.restype = ctypes.c_int
    if libc.mincore(base, count * page, vec) != 0:
        raise OSError(ctypes.get_errno(), "mincore failed")
    # Vectorized: a Python loop over the real table's ~6.25M page flags costs
    # ~0.44 s per call, and the memory probe calls this at every prefill chunk
    # and decode forward inside its timed region.
    # ``bytes`` executes the scan in C and keeps this utility importable on a
    # bare Python used by non-MLX fixture tests.
    resident = bytes(vec).translate(bytes((i & 1) for i in range(256))).count(1)
    return {"resident_bytes": resident * page, "mapped_bytes": mm.nbytes}


def table_stats(model):
    return {str(k): {**resident_pages(t), "path": str(t.path), "lookups": t.lookups, "unique_rows": t.unique_rows,
                     "major_faults": t.major_faults, "gather_seconds": t.seconds,
                     "record_bytes": t.record_bytes, "io": t.io, "format": t.fmt}
            for k, t in model.ngram_tables().items()}


def check_tables(stats):
    if sum(t["resident_bytes"] for t in stats.values()) > PLE_CAP:
        raise ValueError("PLE resident file pages exceed operational 21.5 GB cap")


def load_adapter(args):
    import align_convert_qwen4_exp as converter
    import qwen4exp_e2e_eval as e2e
    from transformers import AutoTokenizer
    if importlib.metadata.version("transformers") != "5.22.1":
        raise ValueError("validation tokenizer requires transformers 5.22.1")
    artifact = external(args.artifact)
    # Validate the recipe before any weight allocation. load_verified_model
    # subsequently re-verifies every byte and pins module+stack before exec.
    converter._lstat_regular(artifact / "manifest.json")
    raw = (artifact / "manifest.json").read_bytes()
    if hashlib.sha256(raw).hexdigest() != args.manifest_sha256:
        raise ValueError("manifest pin mismatch")
    manifest = json.loads(raw)
    if (manifest["profile"] != args.profile or manifest["group_size"] != 64
            or manifest["ngram_storage"] != "bf16"):
        raise ValueError("artifact is not the selected maxfit recipe")
    converter._lstat_regular(artifact / "config.json")
    raw_config = (artifact / "config.json").read_bytes()
    if hashlib.sha256(raw_config).hexdigest() != manifest["files"]["config.json"]:
        raise ValueError("config digest mismatch")
    config = json.loads(raw_config)
    if config["ngram_tables"]["io"] != "mmap":
        raise ValueError("PLE must use mmap")
    model, _ = converter.load_verified_model(artifact, args.manifest_sha256)
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(artifact, local_files_only=True, trust_remote_code=False)
    return e2e.MlxAdapter(model, tokenizer, identity=f"canonical:{args.manifest_sha256}",
                          prefill_step=args.prefill_step, score_chunk=64)


def validate_reference(report, stages):
    from dataclasses import asdict
    import qwen4exp_e2e_eval as e2e
    from qwen4exp_bf16_benchmark import validate_identity
    items = e2e.load_items()
    if (report.get("items_sha256") != items["_file_sha256"] or report.get("quant_profile") != "bf16"
            or report.get("template", {}).get("sha256") != e2e.TEMPLATE_SHA256
            or report.get("harness") != e2e.HARNESS_VERSION):
        raise ValueError("reference item/template/profile/harness identity mismatch")
    validate_identity(report.get("hosted_identity", {}))
    for stage in stages:
        rows = report.get("stages", {}).get(stage, {}).get("items", [])
        if [r["id"] for r in rows] != [r["id"] for r in items[stage]]:
            raise ValueError(f"reference {stage} item coverage mismatch")
    expected_config = asdict(e2e.RunConfig(profile="bf16"))
    if any(report.get("config", {}).get(k) != v for k, v in expected_config.items()):
        raise ValueError("reference generation config mismatch (thinking/effort/budgets/limit)")


def context_ids(adapter, template, length, effort):
    import qwen4exp_e2e_eval as e2e
    text = e2e.load_items()["nll"][0]["text"]
    # Render the actual template and preserve its suffix. Repeated fixed prose
    # fills the middle to an EXACT token count, avoiding tokenize-length drift.
    marker = "JW_CONTEXT_INSERT"
    rendered = template.render([{"role": "user", "content": marker + "\nSummarize the passage."}],
                               enable_thinking=effort != "none",
                               reasoning_effort=None if effort == "none" else effort)
    head, tail = rendered.split(marker)
    left, right = adapter.encode(head), adapter.encode(tail)
    fill = adapter.encode(text + "\n")
    n = length - len(left) - len(right)
    if n <= 0 or not fill:
        raise ValueError("context too short or empty fixture")
    return left + (fill * math.ceil(n / len(fill)))[:n] + right


def timed_tokens(adapter, ids, decode_tokens, checkpoint=lambda: None):
    """Batch 1, full precision KV; bounded prefill, last-row logits only.

    Prefill includes selecting its first generated token. Decode times the
    next N forwards, with EOS deliberately ignored to hold work constant.
    Every boundary synchronizes MLX; no async launch-only timings.
    """
    import mlx.core as mx
    from mlx_lm.models.cache import make_prompt_cache
    cache = make_prompt_cache(adapter.model)
    started = time.perf_counter()
    # Do NOT retain [chunk, vocab] logits for a 40k prompt.
    for start in range(0, len(ids) - 1, adapter.prefill_step):
        chunk = ids[start:min(start + adapter.prefill_step, len(ids) - 1)]
        logits = adapter.model(mx.array(chunk)[None], cache=cache)
        mx.eval([c.state for c in cache])
        del logits
        mx.clear_cache()
        checkpoint()
    logits = adapter.model(mx.array([ids[-1]])[None], cache=cache)
    token = mx.argmax(logits[:, -1, :], axis=-1)
    mx.eval(token, [c.state for c in cache])
    prefill_seconds = time.perf_counter() - started
    generated = [int(token.item())]
    checkpoint()
    started = time.perf_counter()
    for _ in range(decode_tokens):
        logits = adapter.model(token[:, None], cache=cache)
        token = mx.argmax(logits[:, -1, :], axis=-1)
        mx.eval(token, [c.state for c in cache])
        generated.append(int(token.item()))
        checkpoint()
    decode_seconds = time.perf_counter() - started
    del logits, cache
    mx.clear_cache()
    return {"prompt_tokens": len(ids), "decode_forwards": decode_tokens,
            "prefill_seconds": prefill_seconds, "decode_seconds": decode_seconds,
            "prefill_tps": len(ids) / prefill_seconds, "decode_tps": decode_tokens / decode_seconds,
            "generated_ids": generated, "generated_text": adapter.decode(generated),
            "eos_ignored_for_fixed_work": True}


def metal_stats(mx):
    return {"active_bytes": mx.get_active_memory(), "peak_bytes": mx.get_peak_memory(),
            "cache_bytes": mx.get_cache_memory()}


def native_worker(args):
    import mlx.core as mx
    import qwen4exp_e2e_eval as e2e
    device = mx.device_info() if hasattr(mx, "device_info") else mx.metal.device_info()
    recommended = int(device["max_recommended_working_set_size"])
    args.metal_cap_gb = min(args.metal_cap_gb, recommended / 1e9)
    mx.set_cache_limit(256 * 2**20)
    mx.set_memory_limit(int(args.metal_cap_gb * 1e9))
    mx.reset_peak_memory()
    adapter = load_adapter(args)
    template = e2e.ChatTemplate(external(args.artifact) / "chat_template.jinja")
    preflight = e2e.tokenizer_preflight(adapter)
    if not preflight["ok"]:
        raise ValueError("tokenizer preflight failed")
    initial = table_stats(adapter.model)
    for stats in initial.values():
        external(stats["path"])  # PLE must page from JW-EXT, never an internal copy.
    check_tables(initial)
    def checkpoint():
        if mx.get_peak_memory() > args.metal_cap_gb * 1e9:
            raise ValueError("Metal peak exceeds default working-set cap")
        if args.command == "memory":
            check_tables(table_stats(adapter.model))
    result = {"verdict": "completed", "manifest_sha256": args.manifest_sha256,
              "module_sha256": __import__("align_convert_qwen4_exp").MODULE_SHA256,
              "environment": {p: importlib.metadata.version(p) for p in ("mlx", "mlx-lm", "transformers")},
              "ple_before": initial, "tokenizer_preflight": preflight, "load_metal": metal_stats(mx),
              "device": device, "effective_metal_cap_bytes": int(args.metal_cap_gb * 1e9)}
    checkpoint()
    if args.command in ("memory", "performance", "paging"):
        runs = []
        efforts = EFFORTS if args.command == "performance" else ("none",)
        contexts = args.contexts if args.command != "paging" else [4096]
        for length in contexts:
            for effort in efforts:
                # Final consumed context includes decode; never exceed 40,960.
                ids = context_ids(adapter, template, length - args.decode_tokens, effort)
                # One warmup + three reported repeats for speed; two identical
                # passes for paging, labelled cache-state-unknown then warm.
                count = args.repeats + 1 if args.command == "performance" else (2 if args.command == "paging" else 1)
                for repeat in range(count):
                    mx.reset_peak_memory()
                    before = table_stats(adapter.model)
                    disk_before = record_disk(args, f"r{repeat}-before") if args.command == "paging" else None
                    usage0 = resource.getrusage(resource.RUSAGE_SELF)
                    run = timed_tokens(adapter, ids, args.decode_tokens, checkpoint)
                    usage = resource.getrusage(resource.RUSAGE_SELF)
                    disk_after = record_disk(args, f"r{repeat}-after") if args.command == "paging" else None
                    after = table_stats(adapter.model)
                    check_tables(after)
                    run.update(context=length, reasoning_effort=effort, repeat=repeat,
                               warmup=args.command == "performance" and repeat == 0,
                               ple_before=before, ple_after=after, metal=metal_stats(mx),
                               major_faults=usage.ru_majflt - usage0.ru_majflt,
                               minor_faults=usage.ru_minflt - usage0.ru_minflt,
                               input_blocks=usage.ru_inblock - usage0.ru_inblock)
                    if args.command == "paging":
                        run.update(disk_before=disk_before, disk_after=disk_after,
                                   cache_state="unknown" if repeat == 0 else "warm repeat")
                    if args.command == "memory" and length == 40960:
                        expected = PREDICTED_PEAK[args.profile]
                        run["prediction"] = {"peak_bytes": expected,
                                             "relative_error": abs(run["metal"]["peak_bytes"] - expected) / expected,
                                             "scope": "Metal allocation proxy; PLE file residency reported separately"}
                        if run["prediction"]["relative_error"] > 0.10:
                            result["verdict"] = "fail"
                    runs.append(run)
                    # Write an incremental journal before attempting the next rung.
                    with Path(str(args.out) + ".rungs.jsonl").open("a") as f:
                        f.write(json.dumps(run) + "\n")
        result["runs"] = runs
        if args.command == "memory" and args.contexts != list(CONTEXTS):
            result["verdict"] = "incomplete"
        if args.command == "performance":
            import statistics
            result["medians"] = [{"context": c, "reasoning_effort": e,
                                   **{k: statistics.median(r[k] for r in runs if r["context"] == c
                                                          and r["reasoning_effort"] == e and not r["warmup"])
                                      for k in ("prefill_tps", "decode_tps")}}
                                  for c in contexts for e in efforts]
            result["p5_targets"] = {"prefill_512_tps": 400, "prefill_2048_tps": 550,
                                     "decode_tps": 30, "decode_stretch_tps": 40,
                                     "scope": "PR670 extrapolated e3 recipe targets, advisory for maxfit"}
    elif args.command in ("quality", "benchmark"):
        stages = "consistency,nll,coherence,toolcall" if args.command == "quality" else "math,ifeval"
        opts = ["--items", str(e2e.ITEMS_PATH), "--chat-template", str(template.path),
                "--quant-profile", args.profile, "--stages", stages, "--reasoning-effort", "low"]
        if args.reference:
            compare_stages = ["coherence", "toolcall"] if args.command == "quality" else ["math", "ifeval"]
            validate_reference(json.loads(external(args.reference).read_text()), compare_stages)
            opts += ["--reference", str(external(args.reference))]
        report = e2e.run(e2e.parse_args(opts), adapter=adapter)
        result.update(verdict=report["verdict"], e2e=report)
        result["reference_status"] = "supplied; verify provenance manually" if args.reference else "missing; comparison gate OPEN"
    else:
        import qwen4exp_hosted_reference as hosted
        if args.provider == "vllm-selfhost":
            if not args.reference:
                raise ValueError("BF16 trace comparison needs --reference hosted BF16 benchmark identity report")
            validate_reference(json.loads(external(args.reference).read_text()), ["math", "ifeval"])
            result["reference_status"] = "operator-attested BF16; confirm traces came from this same host"
        else:
            result["reference_status"] = "advisory: precision/weight identity not established as BF16"
        opts = ["compare", "--provider", args.provider, "--traces", str(external(args.traces)),
                "--quant-profile", args.profile, "--chat-template", str(template.path),
                "--out", str(args.out) + ".hosted.json"]
        code = hosted.main(opts, adapter=adapter)
        result.update(verdict="fail" if code else "completed",
                      hosted=json.loads(Path(str(args.out) + ".hosted.json").read_text()))
    checkpoint()
    result.update(metal=metal_stats(mx), ple_after=table_stats(adapter.model))
    check_tables(result["ple_after"])
    return result


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=("download", "convert", "progress", "verify-source", *NATIVE))
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--validation-only", action="store_true", help="operator asserts no measurement/analysis job is running")
    p.add_argument("--out", type=Path)
    p.add_argument("--artifact", type=Path)
    p.add_argument("--manifest-sha256")
    p.add_argument("--source-receipt", type=Path)
    p.add_argument("--profile", choices=("maxfit", "maxfit5"), default="maxfit")
    p.add_argument("--contexts", type=int, nargs="+", default=list(CONTEXTS))
    p.add_argument("--decode-tokens", type=int, default=64)
    p.add_argument("--prefill-step", type=int, choices=(512, 2048), default=512)
    p.add_argument("--repeats", type=int, default=3)
    p.add_argument("--poll-seconds", type=float, default=2)
    p.add_argument("--metal-cap-gb", type=float, default=115.4)
    p.add_argument("--reference", type=Path, help="same-item bf16 e2e report from separately hosted reference")
    p.add_argument("--traces", type=Path, help="PR671 hosted-reference JSONL, collected separately")
    p.add_argument("--disk-device", help="paging: diskN of the external physical whole disk, from diskutil list")
    p.add_argument("--provider", default="vllm-selfhost")
    p.add_argument("--max-workers", type=int, choices=range(2, 9), default=2)
    p.add_argument("--plan-only", action="store_true")
    p.add_argument("--metadata", type=Path)
    p.add_argument("--snapshot", type=Path)
    p.add_argument("--quarantine", action="store_true")
    p.add_argument("--interval", type=float, default=60)
    p.add_argument("--cutoff")
    p.add_argument("--convert-budget-h", type=float, default=4)
    p.add_argument("--run-dir", type=Path)
    p.add_argument("--progress-path", type=Path)
    p.add_argument("--volume", type=Path, default=VOLUME, help=argparse.SUPPRESS)
    p.add_argument("--once", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args(argv)
    if (args.decode_tokens < 1 or args.repeats < 1 or not 0.1 <= args.poll_seconds <= 10
            or not 1 <= args.metal_cap_gb <= 115.4 or args.contexts != sorted(set(args.contexts))
            or any(c not in CONTEXTS for c in args.contexts) or args.interval <= 0
            or args.convert_budget_h < 0):
        p.error("invalid token/repeat/monitor limit or staged contexts")
    return args


def main(argv=None):
    args = parse_args(argv)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "command": args.command, "revision": REVISION,
                          "profile": args.profile, "contexts": args.contexts,
                          "reasoning_efforts": EFFORTS, "no_weights_loaded": True,
                          "steps": {"download": "pinned HF metadata -> external cache -> source sha256 receipt",
                                    "convert": "verify source -> streaming converter -> manifest pin + raw SHA256SUMS",
                                    "progress": "read cache byte counts and append rate/ETA JSONL",
                                    "verify-source": "check every pinned source file and optionally quarantine bad blobs",
                                    "memory": "supervise load -> 4k/16k/40960 -> 64 decode forwards -> memory prediction",
                                    "quality": "PR671 consistency + NLL + coherence + XML tool round trips",
                                    "benchmark": "PR671 fixed GSM8K30 + IFEval25, optional same-item bf16 report",
                                    "hosted": "PR671 offline teacher-forced top-k comparison (no requests)",
                                    "performance": "3 efforts x staged contexts x (warmup + 3 timed repeats)",
                                    "paging": "two identical 4k passes; mincore + faults + table counters; external iostat"}[args.command]}))
        return 0
    if args.command == "progress":
        if not args.metadata or not args.run_dir:
            raise ValueError("progress requires --metadata PLAN and --run-dir")
        progress(args)
        return 0
    if not args.validation_only or sys.platform != "darwin":
        raise ValueError("live runs require macOS and --validation-only; exit agents and stop other jobs first")
    if args.command == "verify-source":
        if not args.snapshot or not args.metadata:
            raise ValueError("verify-source requires --snapshot and --metadata PLAN|RECEIPT")
        document = json.loads(args.metadata.read_text())
        digests, failures = verify_source_all(args.snapshot, document["metadata"])
        moved = quarantine_bad(args.snapshot, failures, VOLUME / "flashnext") if args.quarantine else []
        print(json.dumps({"verified": len(digests), "mismatches": failures, "quarantined": moved}))
        return 1 if failures else 0
    if args.out is None:
        raise ValueError("--out is required")
    if agents := measurement_agents_loaded():
        raise ValueError("measurement launchd agent(s) loaded; unload before validation: " + ", ".join(agents))
    args.out = external(args.out)
    if args.out.exists():
        raise ValueError("preserve existing evidence; choose a new --out")
    volume_info()
    cache_environment()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if args.command in NATIVE:
        if not args.artifact or not re.fullmatch(r"[0-9a-f]{64}", args.manifest_sha256 or ""):
            raise ValueError("native probes require --artifact and externally recorded --manifest-sha256")
        if args.command == "hosted" and not args.traces:
            raise ValueError("hosted comparison requires previously collected --traces")
        if args.worker:
            result = native_worker(args)
            write_json(str(args.out) + ".worker.json", result)
            return 1 if result["verdict"] in ("fail", "incomplete") else 0
        result = supervise(args)
    else:
        if args.command == "convert" and (not args.source_receipt or not args.artifact):
            raise ValueError("convert requires --source-receipt and --artifact")
        started = utc_now()
        try:
            result = download(args) if args.command == "download" else convert(args)
        except BaseException as exc:
            finished = utc_now()
            attempt = {"schema": "qwen4exp-attempt/v1", "command": args.command,
                       "error": f"{type(exc).__name__}: {exc}",
                       **timing(started, finished, 0)}
            write_json(str(args.out) + ".attempt.json", attempt)
            raise
        finished = utc_now()
        total = result.get("total_bytes")
        if total is None:
            total = sum(p.stat().st_size for p in Path(result["artifact"]).iterdir() if p.is_file())
        result.update(timing(started, finished, total))
    write_json(args.out, result)
    print(json.dumps({"out": str(args.out), "verdict": result.get("verdict", "completed")}))
    return 1 if result.get("verdict") in ("aborted", "fail", "incomplete") else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        sys.exit(2)
