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
from .runner import Harness, execute, failure_summary, load_prompts, runtime_identity, runtime_version
from .stream_ple import BUFFER_SUFFIXES, copy_tensors, extract_part, header, is_table, valid_entry

REPO_ID = "Qwen/Qwen3.8-Flash-Next"
REVISION = "de4b8e4d43b917e7706784d8bb445c9af86a3540"
STREAM_SCHEMA = "qwen4-gold-stream/v1"
GIB = 1024**3
# --reference-chain-only (lead ruling L3): the official reference forward only,
# real inputs, every unit; per-case traces pruned to the chain output, and a
# unit's chain released once its successor has committed. Only the head unit's
# outputs (the bf16 quality reference) and the live chain stay on disk.
CHAIN_ONLY = "REFERENCE_CHAIN_ONLY"


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
        if runtime_version(self.runtimes["reference"], "transformers") != REFERENCE_VERSION:
            raise ValueError(f"requires transformers {REFERENCE_VERSION}")
        identity = {"source": self.source_info, "config": self.checkpoint.config,
                    "weight_map": self.checkpoint.weight_map, "stamps": {}}
        args.output = str(self.work / "parity")
        self.chain_only = bool(getattr(args, "reference_chain_only", False))
        args.dtypes, args.input_modes = "fp32,bf16", ("real" if self.chain_only else "random,real")
        args.worker_extra = {"hf_home": str(self.staging / "hf")}
        self.harness = Harness(args, self.checkpoint, identity, self.prompts, self.runtimes)
        self.path = self.work / "manifest.json"
        self._verified = {}
        rerun = self.rerun_identity() if getattr(args, "rerun_from", None) else None
        fp = digest([STREAM_SCHEMA, self.harness.fingerprint, args.min_free_gb, args.max_staging_gb,
                     str(Path(args.convert_out).resolve()) if args.convert_out else None,
                     {p: sha256(p) for p in (args.canonical_converter, args.canonical_module) if p},
                     args.shared_shards] + ([rerun["identity"]] if rerun else [])
                    + ([{"mode": CHAIN_ONLY}] if self.chain_only else []))
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
            if rerun:
                self.adopt_rerun(rerun)
            self.save()
        self.selected = set(self.state["rerun"]["units"]) if "rerun" in self.state else None

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
        if self.selected is not None:
            done |= set(self.plan["units"]) - self.selected  # never run here
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
        # Canonical checkpoint identities against which every sparse entry is
        # semantically revalidated by both workers.
        ple["source_shards"] = {name: self.metadata[name]["sha256"] for name in sorted(
            {self.checkpoint.weight_map[k] for k in self.plan["tables"]})}
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

    def rerun_identity(self):
        """Selected units of a finished/in-progress run, re-run on its reference chain.

        The source work directory is only read. Its recorded predecessor
        outputs (the official reference chain) are byte-checked against its
        manifest's unit artifact hashes and copied here; nothing is trusted
        from its verdicts except the FAIL list used by --rerun-failed.
        """
        old_work = Path(self.args.rerun_from).resolve()
        if old_work == self.work or old_work in self.work.parents or self.work in old_work.parents:
            raise ValueError("--rerun-from must be a different, non-nested work directory")
        old = json.loads((old_work / "manifest.json").read_text())
        if old.get("schema") != STREAM_SCHEMA:
            raise ValueError("--rerun-from is not a streaming work directory")
        if (old["source"]["repo"], old["source"]["revision"], old["source"]["shards"]) != (
                self.source_info["repo"], self.source_info["revision"], self.metadata):
            raise ValueError("--rerun-from used a different pinned checkpoint")
        units = list(getattr(self.args, "units", None) or [])
        if getattr(self.args, "rerun_failed", False):
            units += [u for u, row in old["units"].items() if row.get("status") != "PASS"]
        unknown = set(units) - set(self.plan["units"])
        if unknown:
            raise ValueError(f"unknown units: {sorted(unknown)}")
        units = [u for u in self.plan["units"] if u in set(units)]
        if not units:
            raise ValueError("no units selected to re-run (--units and/or --rerun-failed)")
        keys = [dtype + ":" + prompt["name"] for dtype in ("fp32", "bf16") for prompt in self.prompts]
        inputs = {}
        for unit in units:
            index = self.plan["units"].index(unit)
            previous = self.plan["units"][index - 1] if index else None
            if previous is None or previous in units:
                continue  # embed needs no input; a re-run predecessor supplies its own.
            row, chain = old["units"].get(previous), old.get("chain", {}).get(previous)
            if row is None or chain is None:
                raise ValueError(f"--rerun-from has no completed reference chain at {previous}")
            for key in keys:
                source = Path(chain[key]) if key in chain else None
                relative = str(source.relative_to(old_work)) if source else None
                if source is None or row["artifacts"].get(relative) != sha256(source):
                    raise ValueError(f"reference chain input missing or changed: {previous}/{key}")
                inputs.setdefault(previous, {})[key] = {"source": str(source), "sha256": row["artifacts"][relative]}
        return {"old_work": old_work, "old": old, "units": units, "inputs": inputs,
                "identity": {"source_fingerprint": old["fingerprint"], "units": units, "inputs": inputs}}

    def adopt_rerun(self, rerun):
        directory = self.work / "rerun-inputs"
        for previous, keys in rerun["inputs"].items():
            for key, row in keys.items():
                target = directory / previous / (key.replace(":", "-") + ".npy")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(row["source"], target)
                if sha256(target) != row["sha256"]:
                    raise ValueError("reference chain input changed while copying")
                row["path"] = str(target)
        old_ple = rerun["old"].get("ple", {})
        if "plans" in old_ple:
            # The official sparse PLE rows already extracted for these prompts:
            # copied byte-checked; prepare_ple re-binds them to the pinned shards.
            store = self.work / "sparse-ple"
            store.mkdir(exist_ok=True)
            for tensor, entry in old_ple["entries"].items():
                if not valid_entry(rerun["old_work"] / "sparse-ple", entry):
                    raise ValueError(f"--rerun-from sparse PLE rows changed: {tensor}")
                shutil.copyfile(rerun["old_work"] / "sparse-ple" / entry["file"], store / entry["file"])
            self.state["ple"] = {k: v for k, v in old_ple.items() if k != "source_shards"}
        self.state["rerun"] = {"source_work": str(rerun["old_work"]), "source_fingerprint": rerun["old"]["fingerprint"],
                               "units": rerun["units"], "inputs": rerun["inputs"]}

    def chain_input(self, previous, key):
        if previous in self.state["chain"]:
            return Path(self.state["chain"][previous][key])
        row = self.state.get("rerun", {}).get("inputs", {}).get(previous, {}).get(key)
        if row is None or sha256(row["path"]) != row["sha256"]:
            raise ValueError(f"reference chain input missing or changed: {previous}/{key}")
        return Path(row["path"])

    def run_unit(self, unit):
        if self.chain_only:
            return self.run_reference_unit(unit)
        import numpy as np
        chain = {}
        previous = self.plan["units"][self.plan["units"].index(unit) - 1] if unit != "embed" else None
        for dtype in ("fp32", "bf16"):
            for prompt in self.prompts:
                key = dtype + ":" + prompt["name"]
                hidden = self.chain_input(previous, key) if previous else None
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
        # chain holds only the official reference outputs (Harness.case returns
        # reference/output.npy), so the next unit's real input never depends on
        # this unit's MLX verdict. --keep-going relies on this.
        report = self.harness.publish(unit, finished=True)
        name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
        result = self.harness.out / (name + ".json")
        row = {"state": "done", "status": "PASS" if report["status"] == "PASS" else "FAIL",
               "result": str(result), "result_sha256": sha256(result),
               "artifacts": {str(p.relative_to(self.work)): sha256(p) for p in (self.harness.out / name).rglob("*.npy")},
               "chain": chain}
        if self.args.worker_extra.get("sparse_digest"):
            row["sparse_digest"] = self.args.worker_extra["sparse_digest"]
        if row["status"] != "PASS":
            row["failures"] = failure_summary(report)
        return row

    def prune_case(self, output):
        """Keep only a reference case's chain output (and its request/result).

        Traces and the input snapshot are deleted; the case report is
        re-pinned to what remains so --resume can reuse the case.
        """
        from .core import digest as _digest
        from .runner import artifacts
        directory = output.parent.parent
        for path in directory.rglob("*.npy"):
            if path != output:
                path.unlink()
        report_path = directory / "report.json"
        report = json.loads(report_path.read_text())
        report["artifacts"] = artifacts(directory)
        report["evidence_digest"] = _digest({"fingerprint": report["fingerprint"], "artifacts": report["artifacts"]})
        report["pruned"] = "traces and input snapshot (reference-chain-only)"
        write_json(report_path, report)

    def run_reference_unit(self, unit):
        """The official reference on real inputs only; no MLX, no random cases."""
        chain, cases = {}, []
        previous = self.plan["units"][self.plan["units"].index(unit) - 1] if unit != "embed" else None
        for dtype in ("fp32", "bf16"):
            for prompt in self.prompts:
                key = dtype + ":" + prompt["name"]
                hidden = self.chain_input(previous, key) if previous else None
                output = self.harness.case(unit, dtype, prompt, "real", hidden, compare=False)
                if output is None:
                    raise RuntimeError(f"reference chain incomplete at {unit}/{key}")
                self.prune_case(output)
                chain[key] = str(output)
                cases.append({"case": output.parent.parent.name, "status": CHAIN_ONLY,
                              "output": str(output.relative_to(self.work)), "output_sha256": sha256(output)})
        name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
        result = self.harness.out / (name + ".json")
        write_json(result, {"schema": STREAM_SCHEMA, "unit": unit, "status": CHAIN_ONLY,
                            "fingerprint": self.harness.fingerprint, "cases": cases,
                            "scope": "official reference forward only (real inputs); no MLX parity verdict"})
        row = {"state": "done", "status": CHAIN_ONLY, "result": str(result), "result_sha256": sha256(result),
               "artifacts": {c["output"]: c["output_sha256"] for c in cases}, "chain": chain}
        if self.args.worker_extra.get("sparse_digest"):
            row["sparse_digest"] = self.args.worker_extra["sparse_digest"]
        return row

    def release_chain(self):
        """Delete chain outputs no unit still needs (reference-chain-only).

        A unit's outputs feed only its successor; once that successor has
        committed they are released. The head unit is the deliverable and is
        never released. The release is recorded before files are deleted, so
        a kill in between leaves only harmless extra bytes.
        """
        units = self.plan["units"]
        for unit in list(self.state["units"]):
            row = self.state["units"][unit]
            if unit == "head" or row.get("chain_released"):
                continue
            successor = units[units.index(unit) + 1]
            if successor not in self.state["units"]:
                continue
            row["chain_released"] = True
            self.save()
            for path in self.state["chain"][unit].values():
                directory = Path(path).parent.parent
                if directory.is_dir() and self.work in directory.resolve().parents:
                    shutil.rmtree(directory)

    def validate_done(self):
        allowed = (CHAIN_ONLY,) if self.chain_only else ("PASS", "FAIL")
        for unit, row in self.state["units"].items():
            # FAIL rows exist only from --keep-going: recorded, never retried.
            if row["status"] not in allowed or sha256(row["result"]) != row["result_sha256"]:
                raise ValueError(f"completed unit result changed: {unit}")
            if row.get("chain_released"):
                continue  # Consumed by its committed successor and deleted by design.
            if row.get("sparse_digest") and sha256(self.work / "sparse-ple/store.json") != row["sparse_digest"]:
                raise ValueError(f"completed unit sparse PLE contract changed: {unit}")
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
        if self.chain_only:
            self.release_chain()  # Recovers a kill between a unit commit and its predecessor's release.
        if self.args.shared_shards == "restage":
            for unit in self.state["units"]:
                path = self.staging / "views" / unit
                if path.exists():
                    shutil.rmtree(path)
        for unit in self.plan["units"]:
            if unit in self.state["units"] or (self.selected is not None and unit not in self.selected):
                continue
            print(f"Unit {unit}", flush=True)
            ple_ids = self.checkpoint.text.get("ple_layer_ids") or []
            first_ple = str(min(ple_ids) - 1) if ple_ids else None
            if ple_ids and unit == first_ple:
                self.prepare_ple()
            elif (self.selected is not None and first_ple is not None and "source_shards" not in self.state["ple"]
                  and self.plan["units"].index(unit) > self.plan["units"].index(first_ple)):
                self.prepare_ple()  # Re-run: rows adopted from --rerun-from, or extracted now.
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
            if self.chain_only:
                pass  # No parity verdict exists in this mode.
            elif row["status"] != "PASS":
                if not getattr(self.args, "keep_going", False):
                    raise RuntimeError(f"parity did not pass at {unit}; see {self.harness.out}")
                print(f"Unit {unit} FAIL (recorded; --keep-going continues on the reference chain): "
                      + json.dumps(row["failures"]), flush=True)
            elif self.args.convert_out:
                row["conversion"] = self.convert_unit(unit)  # Only parity-passing units are exported.
            self.state["chain"][unit] = row.pop("chain")
            self.state["units"][unit] = row
            self.state.pop("current_unit", None)
            self.save()
            for filename in self.plan["shards"][unit]:
                self.consume(filename, unit)
            self.release()
            if self.chain_only:
                self.release_chain()
            if self.args.shared_shards == "restage":
                shutil.rmtree(active.root)
        failures = [{"unit": unit, "result": row["result"], "cases": row["failures"]}
                    for unit, row in self.state["units"].items() if row["status"] not in ("PASS", CHAIN_ONLY)]
        status = "FAIL" if failures else (CHAIN_ONLY if self.chain_only else "PASS")
        summary = {"schema": STREAM_SCHEMA, "status": status,
                   "fingerprint": self.state["fingerprint"],
                   "coverage": {"layers": list(range(self.checkpoint.text["num_hidden_layers"])),
                                "dtypes": ["fp32", "bf16"], "input_modes": args_modes(self.args), "endpoints": True,
                                "reference_chain_only": self.chain_only,
                                "full_48_layer_gold": (not failures and self.selected is None and not self.chain_only
                                                       and self.checkpoint.text["num_hidden_layers"] == 48),
                                "rerun": self.state.get("rerun")},
                   "failures": failures, "units": self.state["units"], "skipped_keys": self.plan["skipped_keys"]}
        write_json(self.work / "summary.json", summary)
        if failures:
            print(f"Stream FAIL: {len(failures)} unit(s) failed", flush=True)
            for failure in failures:
                for case in failure["cases"]:
                    print(f"  unit {failure['unit']} {case['case']}: {case['status']} "
                          f"failing={case['failing_traces']} missing={case['missing_traces']}"
                          + (f" reason={case['reason']}" if case.get("reason") else ""), flush=True)
        return summary

    def convert_unit(self, unit):
        from .stream_convert import convert_unit
        return convert_unit(self, unit)


def args_modes(args):
    return [m for m in ("random", "real") if m in args.input_modes.split(",")]


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
    parser.add_argument("--keep-going", action="store_true",
                        help="record a unit's parity FAIL and continue on the official reference chain; "
                             "final status stays FAIL (reference/worker-chain errors still stop)")
    parser.add_argument("--plan-only", action="store_true", help="save pinned metadata and disk estimates; download no weight shards")
    parser.add_argument("--shared-shards", choices=("retain", "restage"), default="retain",
                        help="retain: original shards through last user; restage: opt-in byte-exact unit subsets and repeat downloads")
    parser.add_argument("--convert-out")
    parser.add_argument("--canonical-converter", help="canonical scripts/align_convert_qwen4_exp.py (not merged by this lane)")
    parser.add_argument("--canonical-module", help="canonical joulewise/align/models/qwen4_exp.py")
    parser.add_argument("--rerun-from", help="re-run selected units of this (read-only) streaming work directory "
                        "into a fresh --work, on its recorded official reference chain inputs")
    parser.add_argument("--units", type=lambda v: [u for u in v.split(",") if u],
                        help="with --rerun-from: comma-separated units (embed, 0..N-1, final, head)")
    parser.add_argument("--rerun-failed", action="store_true", help="with --rerun-from: add every non-PASS unit")
    parser.add_argument("--reference-chain-only", action="store_true",
                        help="quality-reference pass (lead ruling L3): official reference forward only on real "
                             "inputs, traces pruned, chain released after use; keeps the head unit outputs. "
                             "Requires --prompts-json; no MLX parity verdict")
    args = parser.parse_args(argv)
    if args.reference_chain_only and (not args.prompts_json or args.rerun_from or args.convert_out):
        parser.error("--reference-chain-only requires --prompts-json and excludes --rerun-from/--convert-out")
    if (args.units or args.rerun_failed) and not args.rerun_from:
        parser.error("--units/--rerun-failed require --rerun-from")
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
    return 0 if result["status"] in ("PASS", CHAIN_ONLY) else 2
