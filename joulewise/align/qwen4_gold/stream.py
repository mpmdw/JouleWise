"""Pinned HF shard lifecycle and unit-major gold parity. No framework imports."""
from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
import re
import shutil
import sys
from pathlib import Path

from .core import (IndexedCheckpoint, REFERENCE_VERSION, TraceFile, digest,
                   file_stamp, sha256, write_json)
from .runner import Harness, execute, load_prompts, runtime_identity
from .stream_ple import BUFFER_SUFFIXES, copy_tensors, extract_part, header, is_table, valid_entry

REPO_ID = "Qwen/Qwen3.8-Flash-Next"
REVISION = "de4b8e4d43b917e7706784d8bb445c9af86a3540"
STREAM_SCHEMA = "qwen4-gold-stream/v1"
GIB = 1024**3


def safe_name(name):
    if not isinstance(name, str) or Path(name).name != name or name in {"", ".", "..", "restricted"}:
        raise ValueError(f"unsafe shard filename: {name}")
    return name


def disk_bytes(root):
    return sum(p.stat().st_size for p in Path(root).rglob("*") if p.is_file())


def disk_guard(work, staging, incoming, min_free_gb, max_staging_gb):
    if incoming < 0 or shutil.disk_usage(staging).free - incoming < min_free_gb * GIB:
        raise RuntimeError(f"free-disk guard: need {incoming} bytes plus {min_free_gb:g} GiB reserve")
    if disk_bytes(staging) + incoming > max_staging_gb * GIB:
        raise RuntimeError(f"staging guard: download would exceed {max_staging_gb:g} GiB")


class HubSource:
    """Only online component; all HF storage is explicitly below work/staging.

    local_dir avoids a second blob copy. Xet is disabled before importing the
    hub package (and explicitly in its constants for already-imported callers).
    Incomplete local_dir downloads are retried by hf_hub_download on resume.
    """
    def __init__(self, work):
        self.work = Path(work)
        self.staging = self.work / "staging"
        self.root = self.staging / "checkpoint"
        self.cache = self.staging / "hf"
        self.root.mkdir(parents=True, exist_ok=True)
        os.environ.update(HF_HOME=str(self.cache), HF_HUB_CACHE=str(self.cache / "hub"),
                          HF_XET_CACHE=str(self.cache / "xet"), HF_HUB_DISABLE_XET="1",
                          HF_XET_CHUNK_CACHE_SIZE_BYTES="0", HF_XET_SHARD_CACHE_SIZE_LIMIT="0")

    def download(self, name):
        from huggingface_hub import hf_hub_download, constants
        constants.HF_HUB_DISABLE_XET = True
        path = Path(hf_hub_download(REPO_ID, safe_name(name), revision=REVISION,
                                   cache_dir=str(self.cache / "hub"), local_dir=str(self.root)))
        if path != self.root / name or path.is_symlink():
            raise ValueError("hub must return a regular file in the explicit local_dir")
        return path

    def prepare(self):
        path = self.work / "source.json"
        if path.exists():
            saved = json.loads(path.read_text())
            if saved["repo"] != REPO_ID or saved["revision"] != REVISION:
                raise ValueError("source pin changed")
            for name, checksum in saved["small_files"].items():
                if sha256(self.root / name) != checksum:
                    raise ValueError("cached config/index changed")
            return saved
        from huggingface_hub import HfApi
        api = HfApi()
        # Fetch sizes before even the small downloads; shard hashes MUST be LFS
        # SHA256, never etag/git SHA1 or a locally generated checksum.
        small = api.get_paths_info(REPO_ID, ["config.json", "model.safetensors.index.json"], revision=REVISION)
        small_hashes = {}
        for info in small:
            if info.size > 16 * 1024**2:
                raise ValueError("config/index exceeds 16 MiB")
            disk_guard(self.work, self.staging, info.size, self.min_free_gb, self.max_staging_gb)
            file = self.download(info.path)
            import hashlib
            raw = file.read_bytes()
            git_hash = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
            if len(raw) != info.size or git_hash != info.blob_id:
                raise ValueError("pinned config/index git blob mismatch")
            small_hashes[info.path] = sha256(file)
        if set(small_hashes) != {"config.json", "model.safetensors.index.json"}:
            raise ValueError("missing config/index metadata")
        weight_map = json.loads((self.root / "model.safetensors.index.json").read_text())["weight_map"]
        names = sorted({safe_name(n) for n in weight_map.values()})
        metadata = {}
        for first in range(0, len(names), 100):
            for info in api.get_paths_info(REPO_ID, names[first:first+100], revision=REVISION):
                checksum = info.lfs.sha256 if info.lfs is not None else None
                if not isinstance(checksum, str) or not re.fullmatch(r"[0-9a-f]{64}", checksum) or info.size <= 0:
                    raise ValueError(f"missing LFS sha256/size: {info.path}")
                metadata[info.path] = {"size": info.size, "sha256": checksum}
        if set(metadata) != set(names):
            raise ValueError("incomplete HF file metadata")
        saved = {"repo": REPO_ID, "revision": REVISION, "small_files": small_hashes, "shards": metadata}
        write_json(path, saved)
        return saved


def unit_plan(checkpoint):
    """Use text namespaces only; report all omitted vision/MTP keys explicitly."""
    units = ["embed", *map(str, range(checkpoint.text["num_hidden_layers"])), "final", "head"]
    keys = {u: [] for u in units}
    skipped, tables = [], []
    for name in checkpoint.weight_map:
        if is_table(name) and name.startswith(checkpoint.prefix + "layers."):
            tables.append(name)
        elif name == checkpoint.prefix + "embed_tokens.weight":
            keys["embed"].append(name)
        elif name.startswith(checkpoint.prefix + "layers."):
            unit = name[len(checkpoint.prefix + "layers."):].split(".")[0]
            keys[unit].append(name)
        elif name.startswith(checkpoint.prefix + "hyper_connection_mixer."):
            keys["final"].append(name)
        elif name == "lm_head.weight":
            keys["head"].append(name)
        else:
            skipped.append(name)
    if not keys["head"] and checkpoint.text.get("tie_word_embeddings"):
        keys["head"] = list(keys["embed"])
    if any(not names for names in keys.values()):
        raise ValueError("missing text unit tensors")
    shards = {u: sorted({checkpoint.weight_map[k] for k in names}) for u, names in keys.items()}
    users = {}
    for u in units:
        for name in shards[u]:
            users.setdefault(name, []).append(u)
    return {"units": units, "keys": keys, "shards": shards, "users": users,
            "tables": sorted(tables), "skipped_keys": sorted(skipped)}


def storage_plan(plan, metadata, weight_map):
    """Exact whole-shard retention estimate from pinned HF sizes, no downloads."""
    active, peak, peak_unit = set(), 0, None
    tables = {weight_map[k] for k in plan["tables"]}
    used = set(tables)
    for unit in plan["units"]:
        active.update(plan["shards"][unit])
        used.update(active)
        incoming = tables - active if unit == next((u for u in plan["units"] if any(
            k.startswith(f"model.language_model.layers.{u}.ple.") or k.startswith(f"model.layers.{u}.ple.")
            for k in plan["tables"])), None) else set()
        size = sum(metadata[f]["size"] for f in active) + max((metadata[f]["size"] for f in incoming), default=0)
        if size > peak:
            peak, peak_unit = size, unit
        active = {f for f in active if plan["users"][f][-1] != unit}
    buffer_shards = {weight_map[k] for names in plan["keys"].values() for k in names
                     if k.endswith(tuple("ple.ple_embedding." + s for s in BUFFER_SUFFIXES))}
    restage_bytes = sum(metadata[f]["size"] for u in plan["units"] for f in plan["shards"][u])
    restage_bytes += sum(metadata[f]["size"] for f in tables)
    restage_bytes += sum(metadata[f]["size"] for f in buffer_shards)
    return {"download_bytes": sum(metadata[f]["size"] for f in used), "restage_download_bytes": restage_bytes,
            "peak_shard_bytes": peak,
            "peak_unit": peak_unit, "note": "excludes traces, sparse rows, metadata and optional conversion output"}


class StreamDriver:
    def __init__(self, args, source=None, runtimes=None):
        self.args = args
        self.work = Path(args.work).resolve()
        self.work.mkdir(parents=True, exist_ok=True)
        self.staging = self.work / "staging"
        self.root = self.staging / "checkpoint"
        self.root.mkdir(parents=True, exist_ok=True)
        self.source = source or HubSource(self.work)
        self.source.min_free_gb, self.source.max_staging_gb = args.min_free_gb, args.max_staging_gb
        self.source_info = self.source.prepare()
        self.metadata = self.source_info["shards"]
        self.checkpoint = IndexedCheckpoint(self.root)
        self.plan = unit_plan(self.checkpoint)
        self.storage = storage_plan(self.plan, self.metadata, self.checkpoint.weight_map)
        self.prompts = load_prompts(args.prompts_json, self.checkpoint.text)
        self.runtimes = runtimes if runtimes is not None else {
            "reference": runtime_identity(args.ref_python), "mlx": runtime_identity(args.mlx_python)}
        if self.runtimes["reference"].get("transformers") != REFERENCE_VERSION:
            raise ValueError(f"requires transformers {REFERENCE_VERSION}")
        identity = {"source": self.source_info, "config": self.checkpoint.config,
                    "weight_map": self.checkpoint.weight_map, "stamps": {}}
        args.output = str(self.work / "parity")
        args.dtypes, args.input_modes = "fp32,bf16", "random,real"
        args.worker_extra = {"hf_home": str(self.staging / "hf")}
        self.harness = Harness(args, self.checkpoint, identity, self.prompts, self.runtimes)
        self.path = self.work / "manifest.json"
        self._verified = {}
        fp = digest([STREAM_SCHEMA, self.harness.fingerprint, args.min_free_gb, args.max_staging_gb,
                     str(Path(args.convert_out).resolve()) if args.convert_out else None,
                     {p: sha256(p) for p in (args.canonical_converter, args.canonical_module) if p},
                     args.shared_shards])
        if self.path.exists():
            self.state = json.loads(self.path.read_text())
            if not args.resume:
                raise ValueError("work already exists; repeat the same command with --resume")
            if self.state["fingerprint"] != fp:
                raise ValueError("stream invocation changed; use a fresh work directory")
        else:
            self.state = {"schema": STREAM_SCHEMA, "fingerprint": fp, "source": self.source_info,
                          "plan": self.plan, "storage": self.storage, "shards": {}, "derived_shards": {},
                          "units": {}, "chain": {}, "ple": {"entries": {}}}
            self.save()

    def save(self):
        write_json(self.path, self.state)

    def stage(self, filename):
        filename = safe_name(filename)
        path = self.root / filename
        expected = self.metadata[filename]
        row = self.state["shards"].setdefault(filename, {})
        if path.is_symlink():
            raise ValueError("shard symlinks refused")
        if path.exists() and self._verified.get(filename) == file_stamp(path):
            return path  # Already fully hashed in this invocation; stamps guard subsequent reads.
        if not path.exists():
            # HF resumes this exact local_dir partial in place. Existing bytes
            # already count toward staging; reserve only its remaining size.
            partial_dir = self.root / ".cache/huggingface/download"
            partial_bytes = sum(p.stat().st_size for p in partial_dir.glob(filename + ".*.incomplete"))
            incoming = max(0, expected["size"] - partial_bytes)
            disk_guard(self.work, self.staging, incoming, self.args.min_free_gb, self.args.max_staging_gb)
            row.update(state="downloading", deleted=False, downloaded=False, verified=False, consumed=False)
            self.save()
            print(f"Download {filename}", flush=True)
            self.source.download(filename)
        row.update(state="downloaded", downloaded=True)
        self.save()
        before = file_stamp(path)
        if path.stat().st_size != expected["size"] or sha256(path) != expected["sha256"]:
            raise ValueError(f"HF LFS sha256/size mismatch: {filename}; remove the bad local file before retrying")
        if before != file_stamp(path):
            raise ValueError("shard changed during verification")
        row.update(state="verified", verified=True, sha256=expected["sha256"])
        self._verified[filename] = before
        self.save()
        return path

    def delete(self, filename):
        path = self.root / safe_name(filename)
        path.unlink(missing_ok=True)
        row = self.state["shards"].setdefault(filename, {})
        row.update(state="deleted", deleted=True)
        self.save()
        print(f"Delete {filename}", flush=True)

    def consume(self, filename, unit):
        row = self.state["shards"][filename]
        row.setdefault("consumed_by", [])
        if unit in row["consumed_by"] and row.get("consumed"):
            return
        if unit not in row["consumed_by"]:
            row["consumed_by"].append(unit)
        row.update(state="consumed", consumed=True)
        self.save()

    def release(self):
        done = set(self.state["units"])
        for filename in self.state["shards"]:
            for unit in set(self.plan["users"].get(filename, [])) & done:
                self.consume(filename, unit)
            if set(self.plan["users"].get(filename, [])) <= done:
                if filename in {self.checkpoint.weight_map[k] for k in self.plan["tables"]}:
                    tensors = [k for k in self.plan["tables"] if self.checkpoint.weight_map[k] == filename]
                    if any(k not in self.state["ple"]["entries"] for k in tensors):
                        continue
                if (self.root / filename).exists():
                    self.delete(filename)

    def guards(self):
        return {p.name: file_stamp(p) for p in self.root.glob("*.safetensors")}

    def subset(self, filename, names, root):
        """Opt-in restaging view. Originals are retained by the default policy."""
        root.mkdir(parents=True, exist_ok=True)
        path = root / filename
        key = str(path.relative_to(self.work))
        row = self.state["derived_shards"].get(key)
        if row and path.exists():
            if row["tensors"] != sorted(names) or sha256(path) != row["sha256"]:
                raise ValueError("retained tensor subset changed")
            self.consume(filename, "subset:" + root.name)
            if (self.root / filename).exists():
                self.delete(filename)
            return path
        if row is None:
            # A rename may complete just before the manifest commit. This is
            # generated, uncommitted storage; release it before reserving space.
            path.unlink(missing_ok=True)
        source = self.stage(filename)
        before = file_stamp(source)
        tensors, _ = header(source)
        size = sum(tensors[k]["data_offsets"][1] - tensors[k]["data_offsets"][0] for k in names)
        path.with_suffix(".tmp").unlink(missing_ok=True)
        # Header overhead is bounded before writing, and included in the cap.
        disk_guard(self.work, self.staging, size + len(json.dumps({k: tensors[k] for k in names}).encode()) + 32,
                   self.args.min_free_gb, self.args.max_staging_gb)
        copy_tensors(source, names, path)
        if before != file_stamp(source):
            raise ValueError("source changed while copying tensor subset")
        self.state["derived_shards"][key] = {"source": filename, "source_sha256": self.metadata[filename]["sha256"],
                                             "tensors": sorted(names), "sha256": sha256(path)}
        self.save()
        self.consume(filename, "subset:" + root.name)
        self.delete(filename)
        return path

    def subset_checkpoint(self, label, names):
        root = self.staging / "views" / label
        root.mkdir(parents=True, exist_ok=True)
        for small in ("config.json", "model.safetensors.index.json"):
            shutil.copyfile(self.root / small, root / small)
        for filename in sorted({self.checkpoint.weight_map[k] for k in names}):
            self.subset(filename, [k for k in names if self.checkpoint.weight_map[k] == filename], root)
        return IndexedCheckpoint(root)

    def prepare_ple(self):
        if not self.plan["tables"]:
            return
        ple = self.state["ple"]
        store = self.work / "sparse-ple"
        store.mkdir(exist_ok=True)
        if "plans" not in ple:
            buffers = [k for k in self.checkpoint.weight_map if k.endswith(tuple("ple.ple_embedding." + s for s in BUFFER_SUFFIXES))]
            if self.args.shared_shards == "restage":
                checkpoint = self.subset_checkpoint("ple-buffers", buffers)
            else:
                checkpoint = self.checkpoint
                for filename in sorted({self.checkpoint.weight_map[k] for k in buffers}):
                    self.stage(filename)
            request = {"backend": "ple_plan", "checkpoint": str(checkpoint.root), "prompts": self.prompts,
                       "hf_home": str(self.staging / "hf"),
                       "shard_guards": {p.name: file_stamp(p) for p in checkpoint.root.glob("*.safetensors")}, "config_digest": digest(self.checkpoint.config),
                       "weight_map_digest": digest(self.checkpoint.weight_map)}
            result = execute(self.args.ref_python, request, self.work / "ple-plan", self.args.max_gb, self.args.timeout)
            if "error" in result:
                raise RuntimeError(f"official PLE plan failed: {result}")
            ple.update(result)
            self.save()
            if self.args.shared_shards == "restage":
                shutil.rmtree(checkpoint.root)
        for filename in sorted({self.checkpoint.weight_map[k] for k in self.plan["tables"]}):
            tensors = [k for k in self.plan["tables"] if self.checkpoint.weight_map[k] == filename]
            todo = [k for k in tensors if k not in ple["entries"] or not valid_entry(store, ple["entries"][k])]
            if todo:
                path = self.stage(filename)
                for tensor in todo:
                    base = tensor.split(".shard_")[0] if ".shard_" in tensor else tensor[:-len(".weight")]
                    ple["entries"][tensor] = extract_part(path, tensor, ple["plans"][base], store,
                                                         self.metadata[filename]["sha256"])
                    self.save()  # Commit rows before source deletion; restart skips only valid entries.
                self.consume(filename, "sparse-ple")
            if self.args.shared_shards == "restage":
                self.delete(filename)
            else:
                self.release()
        write_json(store / "store.json", ple)
        self.args.worker_extra.update(sparse_store=str(store), sparse_digest=sha256(store / "store.json"))

    def run_unit(self, unit):
        import numpy as np
        chain = {}
        previous = self.plan["units"][self.plan["units"].index(unit) - 1] if unit != "embed" else None
        for dtype in ("fp32", "bf16"):
            for prompt in self.prompts:
                key = dtype + ":" + prompt["name"]
                hidden = Path(self.state["chain"][previous][key]) if previous else None
                output = self.harness.case(unit, dtype, prompt, "real", hidden)
                if output is None:
                    raise RuntimeError(f"reference chain incomplete at {unit}/{key}")
                chain[key] = str(output)
                if unit != "embed":
                    activation = TraceFile(hidden)
                    square = 0.0
                    for first in range(0, activation.size, 262144):
                        v = activation[first:first+262144].astype(np.float64)
                        square += float(np.dot(v, v))
                    scale = math.sqrt(square / activation.size)
                    width = self.checkpoint.text["hidden_size"] * (1 if unit == "head" else self.checkpoint.text["hc_count"])
                    shape = (1, len(prompt["input_ids"]), width)
                    if math.prod(shape)*4 > self.args.max_gb*GIB/16:
                        raise RuntimeError("random input exceeds memory guard")
                    rng = np.random.default_rng(int(digest([self.args.seed, unit, prompt["name"]])[:16], 16))
                    values = rng.standard_normal(shape, dtype=np.float32) * scale
                    from .stream_ple import atomic_npy
                    path = self.work / "parity/inputs" / f"{unit}-{dtype}-{prompt['name']}.npy"
                    atomic_npy(path, values)
                    self.harness.case(unit, dtype, prompt, "random", path, scale=scale)
        report = self.harness.publish(unit, finished=True)
        if report["status"] != "PASS":
            raise RuntimeError(f"parity did not pass at {unit}; see {self.harness.out}")
        name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
        result = self.harness.out / (name + ".json")
        return {"state": "done", "status": "PASS", "result": str(result), "result_sha256": sha256(result),
                "artifacts": {str(p.relative_to(self.work)): sha256(p) for p in (self.harness.out / name).rglob("*.npy")},
                "chain": chain}

    def validate_done(self):
        for unit, row in self.state["units"].items():
            if row["status"] != "PASS" or sha256(row["result"]) != row["result_sha256"]:
                raise ValueError(f"completed unit result changed: {unit}")
            for name, checksum in row["artifacts"].items():
                if sha256(self.work / name) != checksum:
                    raise ValueError(f"completed unit activation/trace changed: {unit}/{name}")
            for key, path in self.state["chain"][unit].items():
                relative = str(Path(path).relative_to(self.work))
                if relative not in row["artifacts"]:
                    raise ValueError(f"chain points outside completed unit artifacts: {unit}/{key}")
            if "conversion" in row:
                manifest = Path(row["conversion"]["manifest"])
                if sha256(manifest) != row["conversion"]["sha256"]:
                    raise ValueError("converted unit manifest changed")
                for name, checksum in json.loads(manifest.read_text())["files"].items():
                    if sha256(manifest.parent / name) != checksum:
                        raise ValueError("converted unit payload changed")

    def run(self):
        print(json.dumps(self.storage, indent=2), flush=True)
        if self.args.shared_shards == "retain" and self.storage["peak_shard_bytes"] > self.args.max_staging_gb * GIB:
            raise RuntimeError(f"retaining shared shards requires at least {self.storage['peak_shard_bytes']/GIB:.3f} GiB "
                               f"at unit {self.storage['peak_unit']}; staging cap is {self.args.max_staging_gb:g} GiB")
        self.validate_done()
        self.release()  # Recovers a kill between committing a unit and unlinking its last shard.
        if self.args.shared_shards == "restage":
            for unit in self.state["units"]:
                path = self.staging / "views" / unit
                if path.exists():
                    shutil.rmtree(path)
        for unit in self.plan["units"]:
            if unit in self.state["units"]:
                continue
            print(f"Unit {unit}", flush=True)
            ple_ids = self.checkpoint.text.get("ple_layer_ids") or []
            if ple_ids and unit == str(min(ple_ids) - 1):
                self.prepare_ple()
            elif "plans" in self.state["ple"]:
                store = self.work / "sparse-ple"
                self.args.worker_extra.update(sparse_store=str(store), sparse_digest=sha256(store / "store.json"))
            if self.args.shared_shards == "restage":
                active = self.subset_checkpoint(unit, self.plan["keys"][unit])
            else:
                active = self.checkpoint
                for filename in self.plan["shards"][unit]:
                    self.stage(filename)
            self.harness.checkpoint = active
            self.harness.identity["stamps"] = {p.name: file_stamp(p) for p in active.root.glob("*.safetensors")}
            self.state["current_unit"] = {"unit": unit, "state": "running"}
            self.save()
            row = self.run_unit(unit)
            if self.args.convert_out:
                row["conversion"] = self.convert_unit(unit)
            self.state["chain"][unit] = row.pop("chain")
            self.state["units"][unit] = row
            self.state.pop("current_unit", None)
            self.save()
            for filename in self.plan["shards"][unit]:
                self.consume(filename, unit)
            self.release()
            if self.args.shared_shards == "restage":
                shutil.rmtree(active.root)
        summary = {"schema": STREAM_SCHEMA, "status": "PASS", "fingerprint": self.state["fingerprint"],
                   "coverage": {"layers": list(range(self.checkpoint.text["num_hidden_layers"])),
                                "dtypes": ["fp32", "bf16"], "input_modes": ["random", "real"], "endpoints": True,
                                "full_48_layer_gold": self.checkpoint.text["num_hidden_layers"] == 48},
                   "units": self.state["units"], "skipped_keys": self.plan["skipped_keys"]}
        write_json(self.work / "summary.json", summary)
        return summary

    def convert_unit(self, unit):
        from .stream_convert import convert_unit
        return convert_unit(self, unit)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", required=True)
    parser.add_argument("--mlx-module", required=True)
    parser.add_argument("--adapter-dependency", action="append", default=[])
    parser.add_argument("--ref-python", default="/private/tmp/jwsol/venv-ref/bin/python")
    parser.add_argument("--mlx-python", default="/private/tmp/jwsol/venv-mlx/bin/python")
    parser.add_argument("--prompts-json")
    parser.add_argument("--min-free-gb", type=float, default=25)
    parser.add_argument("--max-staging-gb", type=float, default=12)
    parser.add_argument("--max-gb", type=float, default=12)
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--seed", type=int, default=20261105)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--plan-only", action="store_true", help="save pinned metadata and disk estimates; download no weight shards")
    parser.add_argument("--shared-shards", choices=("retain", "restage"), default="retain",
                        help="retain: original shards through last user; restage: opt-in byte-exact unit subsets and repeat downloads")
    parser.add_argument("--convert-out")
    parser.add_argument("--canonical-converter", help="canonical scripts/align_convert_qwen4_exp.py (not merged by this lane)")
    parser.add_argument("--canonical-module", help="canonical joulewise/align/models/qwen4_exp.py")
    args = parser.parse_args(argv)
    args.random_scale = 1.0
    if args.convert_out and (not args.canonical_converter or not args.canonical_module):
        parser.error("--convert-out requires --canonical-converter and --canonical-module from the canonical branch")
    if any(not math.isfinite(v) for v in (args.min_free_gb, args.max_staging_gb, args.max_gb, args.timeout)) or not (
            args.min_free_gb >= 0 and args.max_staging_gb > 0 and 0 < args.max_gb <= 110 and args.timeout > 0):
        parser.error("invalid disk/memory/timeout budget")
    for path in [args.work, args.convert_out, args.mlx_module, args.canonical_converter, args.canonical_module]:
        if path and "restricted" in Path(path).absolute().parts:
            parser.error("restricted paths refused")
    work = Path(args.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    with (work / "driver.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            parser.error("another streaming driver owns this work directory")
        try:
            driver = StreamDriver(args)
            if args.plan_only:
                print(json.dumps(driver.storage, indent=2))
                return 0
            result = driver.run()
        except Exception as error:
            print(f"Stream stopped: {error}", file=sys.stderr)
            return 2
    print(json.dumps({"status": result["status"], "summary": str(work / "summary.json")}))
    return 0
