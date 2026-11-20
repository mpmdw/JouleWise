"""Fixture-only source projection. The coordinator never imports Torch."""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
import struct
from bisect import bisect_left
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from .core import IndexedCheckpoint, REFERENCE_VERSION, digest, file_stamp, sha256, text_config
from .stream_ple import BUFFER_SUFFIXES, is_table

MAX_HEADER = 1024**2
BLOCK = 8 * 1024**2
CHUNK = 256 * 1024**2
SMALL = ("config.json", "model.safetensors.index.json")
WORD = dict(BOOL=1, U8=1, I8=1, U16=2, I16=2, F16=2, BF16=2, U32=4, I32=4,
            F32=4, U64=8, I64=8, F64=8)
NP_TYPE = {"BF16": "<u2", "F16": "<f2", "F32": "<f4"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def unique(pairs):
    obj = dict(pairs)
    require(len(obj) == len(pairs), "duplicate JSON key")
    return obj


def decode(raw):
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique)


def basename(name):
    require(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]*", name)
            and name != "restricted", f"unsafe provider basename: {name!r}")
    return name


def positive(value):
    return type(value) is int and value > 0


def hex_sha(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def regular(path):
    return path.is_file() and not path.is_symlink()


def sync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def synced_write(path, raw):
    with path.open("xb") as output:
        output.write(raw)
        output.flush()
        os.fsync(output.fileno())


def replace_json(path, raw):
    temp = path.with_suffix(".tmp")
    synced_write(temp, raw)
    temp.replace(path)
    sync_dir(path.parent)


def parse_layout(prefix, size, names):
    require(len(prefix) >= 8 and int.from_bytes(prefix[:8], "little") == len(prefix)-8,
            "invalid header length")
    try:
        require(prefix[8:9] == b"{", "invalid header start")
        tensors = decode(prefix[8:])
    except (ValueError, RecursionError) as exc:
        raise ValueError("invalid header JSON") from exc
    require(isinstance(tensors, dict), "invalid header type")
    metadata = tensors.pop("__metadata__", {})
    require(isinstance(metadata, dict) and all(isinstance(v, str) for v in metadata.values()),
            "invalid header metadata")
    require(tensors.keys() == names, "header/index names differ")
    payload = size - len(prefix)
    spans = []
    for info in tensors.values():
        require(isinstance(info, dict) and info.keys() == {"dtype", "shape", "data_offsets"},
                "invalid header fields")
        offsets, shape, kind = info["data_offsets"], info["shape"], info["dtype"]
        require(isinstance(offsets, list) and len(offsets) == 2
                and all(type(n) is int for n in offsets), "invalid extent")
        lo, hi = offsets
        require(0 <= lo <= hi <= payload, "invalid extent")
        require(isinstance(kind, str) and kind in WORD and isinstance(shape, list)
                and all(type(n) is int and 0 <= n < 2**64 for n in shape), "invalid shape/extent")
        words = 0 if 0 in shape else 1
        for dim in shape:
            if words:
                require(words <= (hi-lo) // WORD[kind] // dim, "invalid shape/extent")
                words *= dim
        require(words * WORD[kind] == hi-lo, "invalid shape/extent")
        spans.append((lo, hi))
    end = 0
    for lo, hi in sorted(spans):
        require(lo == end, "overlapping or gapped extents")
        end = hi
    require(end == payload, "unindexed payload bytes")
    return tensors


@dataclass(frozen=True)
class Limits:
    """Injected fixture admission, including bounds for existing worker outputs."""
    quota: int
    selection_bytes: int
    planner_sizes: tuple[int, ...]
    planner_dirs: int
    unit_sizes: tuple[int, ...]
    unit_dirs: int
    block: int = BLOCK
    chunk: int = CHUNK
    header: int = MAX_HEADER


class Provider:
    """One journal per invocation. StreamDriver owns the exclusive writer lock.

    Inputs supply repo/revision, pins mapping basenames to (size, SHA-256),
    small files as (bytes, size, Git blob SHA), and fixture Limits. The
    opener yields a context-managed read(n). The budget broker accounts for
    the work volume, including independent incomplete files.
    """
    def __init__(self, root, inputs, open_object, budget):
        require(callable(open_object) and callable(getattr(budget, "admit", None)),
                "fixture source requires an object opener and allocation budget")
        require(isinstance(inputs, dict) and {"repo", "revision", "pins", "small", "limits"} <= inputs.keys(),
                "fixture source requires bound metadata")
        require(all(isinstance(inputs[k], str) and inputs[k] for k in ("repo", "revision")),
                "fixture source requires a pinned repo and revision")
        self.root = Path(root)
        self.open_object = open_object
        self.budget = budget
        self.limits = limits = inputs["limits"]
        require(isinstance(limits, Limits)
                and all(positive(n) for n in (limits.quota, limits.selection_bytes, limits.block,
                                              limits.chunk, limits.header))
                and limits.block <= BLOCK and limits.chunk <= CHUNK and limits.header <= MAX_HEADER
                and all(type(n) is int and n >= 0 for n in (limits.planner_dirs, limits.unit_dirs))
                and all(isinstance(group, tuple) and all(positive(n) for n in group)
                        for group in (limits.planner_sizes, limits.unit_sizes)), "invalid fixture limits")

        require(isinstance(inputs["small"], dict) and inputs["small"].keys() == set(SMALL),
                "fixture source requires both small files")
        self._small = {}
        for name, (raw, size, git_blob) in inputs["small"].items():
            require(isinstance(raw, bytes) and positive(size) and len(raw) == size <= 16 * 1024**2,
                    "small file size mismatch")
            actual = hashlib.sha1(b"blob " + str(size).encode() + b"\0" + raw).hexdigest()
            require(actual == git_blob, "small file git blob mismatch")
            self._small[name] = raw
        config = decode(self._small[SMALL[0]])
        require(isinstance(config, dict) and isinstance(text_config(config), dict), "invalid bound configuration")
        index = decode(self._small[SMALL[1]])["weight_map"]
        require(isinstance(index, dict) and index and "__metadata__" not in index, "invalid bound index")
        require(isinstance(inputs["pins"], dict), "fixture source requires an inventory")
        self._pins = {}
        for name, (size, checksum) in inputs["pins"].items():
            require(basename(name).endswith(".safetensors") and positive(size) and hex_sha(checksum),
                    "invalid inventory pin")
            self._pins[name] = (size, checksum)
        self._names = {name: set() for name in self._pins}
        for tensor, name in index.items():
            require(tensor and isinstance(name, str) and name in self._pins, "unbound index owner")
            self._names[name].add(tensor)
        require(all(self._names.values()), "inventory and index differ")
        prefixes = [k[:-len("embed_tokens.weight")] for k in index
                    if k.endswith("embed_tokens.weight") and not k.startswith("mtp.")]
        require(len(prefixes) == 1, "expected exactly one text embedding prefix")
        self._metadata = SimpleNamespace(config=config, text=text_config(config), weight_map=index, prefix=prefixes[0])
        self._source_info = {"repo": inputs["repo"], "revision": inputs["revision"],
                            "shards": {k: dict(size=n, sha256=h) for k, (n, h) in self._pins.items()},
                            "small_files": {name: sha(raw) for name, raw in self._small.items()}}
        self.identity = digest(["fixture-unit-source/v1", self._source_info, vars(limits)])
        self.pending = self.root / ".pending"
        self.worker = self.root / ".worker"
        self.journal = self.root / "journal.json"
        self.meter = self.root / "traffic.json"
        self.store = self.root / "store.json"

    @property
    def metadata(self):
        return deepcopy(self._metadata)

    @property
    def source_info(self):
        return deepcopy(self._source_info)

    def start(self, binding, prompts, reference_hash):
        """Open the journal under the caller's writer lock, before recovery."""
        require(hex_sha(reference_hash), "fixture provider requires bound reference source hash")
        self.binding = digest([self.identity, binding, prompts, reference_hash])
        self.reference_hash = reference_hash
        self.prompts = deepcopy(prompts)
        self.owner = self.binding.encode()
        self.records = {}
        if self.root.exists():
            require(self.root.is_dir() and not self.root.is_symlink(), "unsafe provider root")
        else:
            self.budget.admit("provider directory", dirs=1)
            self.root.mkdir()
            sync_dir(self.root.parent)
        marker = self.root / ".owner"
        if not marker.exists():
            require(not any(self.root.iterdir()), "fresh provider directory is not empty")
            self.budget.admit("provider owner", [len(self.owner)])
            synced_write(marker, self.owner)
            sync_dir(self.root)
        require(regular(marker) and marker.read_bytes() == self.owner, "provider invocation mismatch")
        if self.journal.exists():
            require(regular(self.journal), "unsafe provider journal")
            self.state = decode(self.journal.read_bytes())
            require(self.state["identity"] == self.binding, "provider invocation mismatch")
            for tag, checksum in self.state["objects"].items():
                self.records[tag] = self._receipt(tag, checksum)
            plan = self.state["plan"]
            if plan:
                require(plan["invocation"] == self.binding and plan["digest"] == digest(plan["response"])
                        and all(self.state["objects"].get(tag) == checksum
                                for tag, checksum in plan["buffers"].items()), "committed plan binding changed")
        else:
            require(all(path.name in {".owner", "journal.tmp"} and regular(path) for path in self.root.iterdir()),
                    "unowned provider files before journal")
            self.budget.admit("initial journal inventory")
            self.journal.with_suffix(".tmp").unlink(missing_ok=True)
            self._save(dict(identity=self.binding, objects={}, done=[], plan=None))
        self.budget.admit("restart inventory")

    def _receipt(self, tag, checksum):
        folder = self.root / basename(tag)
        path = folder / "receipt.json"
        require(not folder.is_symlink() and regular(path), "missing committed receipt")
        raw = path.read_bytes()
        require(sha(raw) == checksum, "committed receipt changed")
        row = decode(raw)
        require(row["invocation"] == self.binding and row["tag"] == tag
                and row["source"] == self._source(row["obj"]), "receipt source binding changed")
        return row

    def _save(self, state, event="old + candidate journal"):
        raw = encode(state)
        self.budget.admit(event, [len(raw)])
        replace_json(self.journal, raw)
        self.state = state

    def _owned(self, path):
        marker = path / ".owner"
        return path.is_dir() and not path.is_symlink() and regular(marker) and marker.read_bytes() == self.owner

    def recover(self):
        """Reconcile and reclaim only this invocation's unfinished files."""
        for name in ("journal.tmp", "traffic.tmp", "store.tmp"):
            path = self.root / name
            if regular(path):
                path.unlink()
        if self.meter.exists():
            charged = self._traffic()
            if charged["reserved"]:
                charged = dict(spent=charged["spent"] + charged["reserved"], reserved=0)
                self._settle_traffic(charged)
        for folder in self.root.iterdir():
            if folder.name not in self.records and self._owned(folder):
                shutil.rmtree(folder)
        for folder in (self.pending, self.worker):
            if folder.is_dir() and not folder.is_symlink() and not any(folder.iterdir()):
                folder.rmdir()
        sync_dir(self.root)
        self.release()

    def _source(self, obj):
        size, ordinary = self._pins[obj]
        return [self._source_info["revision"], obj, ordinary, size]

    def _traffic(self):
        if not self.meter.exists():
            return dict(spent=0, reserved=0)
        require(regular(self.meter), "unsafe provider traffic journal")
        row = decode(self.meter.read_bytes())
        require(row.pop("identity") == self.binding, "provider traffic identity changed")
        return row

    @property
    def bytes_charged(self):
        row = self._traffic()
        return row["spent"] + row["reserved"]

    def _traffic_bytes(self, row):
        return encode(dict(identity=self.binding, **row))

    def _settle_traffic(self, row):
        raw = self._traffic_bytes(row)
        self.budget.admit("traffic journal replacement", [len(raw)])
        replace_json(self.meter, raw)

    def _reservation(self, obj):
        row = self._traffic()
        size = self._pins[obj][0]
        require(not row["reserved"], "unreconciled source reservation")
        require(row["spent"] + size + 1 <= self.limits.quota, "source quota")
        return dict(spent=row["spent"], reserved=size+1, object=obj)

    def _stream(self, obj, visit, reservation):
        size, ordinary = self._pins[obj]
        whole, chunk, composite = hashlib.sha256(), hashlib.sha256(), hashlib.sha256()
        pos = received = 0
        eof = False
        self._settle_traffic(reservation)
        try:
            with self.open_object(obj) as src:
                while pos < size:
                    n = min(self.limits.block, size-pos, self.limits.chunk-pos % self.limits.chunk)
                    raw = src.read(n)
                    received += len(raw)
                    require(isinstance(raw, bytes) and 0 < len(raw) <= n, "short/oversize object")
                    whole.update(raw)
                    chunk.update(raw)
                    visit(pos, raw)
                    pos += len(raw)
                    if pos % self.limits.chunk == 0 or pos == size:
                        composite.update(chunk.digest())
                        chunk = hashlib.sha256()
                trailing = src.read(1)
                received += len(trailing)
                require(isinstance(trailing, bytes) and not trailing, "trailing object bytes")
                eof = True
        finally:
            self._settle_traffic(dict(spent=reservation["spent"]+received, reserved=0))
        require(eof, "source closed without verified EOF")
        require(whole.hexdigest() == ordinary, "ordinary object digest mismatch")
        return composite.hexdigest() if size > self.limits.chunk else ordinary

    def _begin(self):
        require(not self.pending.exists(), "unrecovered candidate")
        # The marker is the only file made before any other candidate writes.
        self.pending.mkdir()
        synced_write(self.pending / ".owner", self.owner)
        sync_dir(self.pending)
        sync_dir(self.root)

    def _preflight(self, obj, tag, row, sizes, event):
        require(not os.path.lexists(self.pending) and not os.path.lexists(self.root / tag), "unrecovered candidate")
        reservation = self._reservation(obj)
        state = {**self.state, "objects": {**self.state["objects"], tag: "0"*64}}
        outputs = [len(self.owner), *sizes]
        meter = max(len(self._traffic_bytes(reservation)),
                    len(self._traffic_bytes(dict(spent=reservation["spent"]+reservation["reserved"], reserved=0))))
        # Reservation and settlement journals can coexist after the outputs
        # have been filled. Publication reuses the same-volume candidate inode.
        self.budget.admit(event, [*outputs, meter, meter], dirs=1)
        self.budget.admit("publication batch", [*outputs, meter, len(encode(row)), len(encode(state))], dirs=1)
        return reservation

    def _publish(self, tag, row):
        for name, file in row["files"].items():
            path = self.pending / name
            require(path.stat().st_size == file["size"], "short output")
            file["sha256"] = sha256(path)
            with path.open("rb") as stream:
                os.fsync(stream.fileno())
        raw = encode(row)
        synced_write(self.pending / "receipt.json", raw)
        sync_dir(self.pending)
        self.pending.rename(self.root / tag)
        sync_dir(self.root)
        self._save({**self.state, "objects": {**self.state["objects"], tag: sha(raw)}})
        self.records[tag] = row

    def _file(self, tag, name):
        basename(name)
        file = self.records[tag]["files"][name]
        path = self.root / tag / name
        require(not path.parent.is_symlink() and regular(path) and path.stat().st_size == file["size"]
                and sha256(path) == file["sha256"], "committed file missing or changed")
        return path

    def _header(self, obj):
        tag = "h-" + obj
        require(tag in self.records, "missing bound header")
        rec = self.records[tag]
        require(rec["obj"] == obj and rec["role"] == "catalogue", "catalogue binding changed")
        prefix = self._file(tag, "header").read_bytes()
        layout = parse_layout(prefix, self._pins[obj][0], self._names[obj])
        require(rec["layout"] == digest(layout), "catalogue layout changed")
        return prefix, layout, rec

    def discover(self, obj):
        tag = "h-" + basename(obj)
        if tag in self.records:
            self._header(obj)
            return
        size, _ = self._pins[obj]
        maximum = min(size, self.limits.header + 8)
        row = dict(invocation=self.binding, tag=tag, obj=obj, source=self._source(obj), role="catalogue",
                   canonical="0"*64, layout="0"*64, files={"header": dict(size=maximum, sha256="0"*64, last=None)})
        reservation = self._preflight(obj, tag, row, [maximum], "bound header batch")
        prefix = bytearray()

        def collect(pos, raw):
            if pos < 8:
                count = min(8-pos, len(raw))
                prefix.extend(raw[:count])
                raw = raw[count:]
            if len(prefix) >= 8:
                length = int.from_bytes(prefix[:8], "little")
                require(0 < length <= min(self.limits.header, size-8), "invalid header length")
                prefix.extend(raw[:max(0, 8+length-len(prefix))])

        row["canonical"] = self._stream(obj, collect, reservation)
        layout = parse_layout(prefix, size, self._names[obj])
        row["layout"] = digest(layout)
        row["files"]["header"]["size"] = len(prefix)
        self._begin()
        synced_write(self.pending / "header", prefix)
        self._publish(tag, row)

    @property
    def plan_digest(self):
        return digest(self.state["plan"]) if self.state["plan"] else None

    def _dense(self, obj, layout, names, origin, outputs, spans):
        header, cursor = {}, 0
        for name in names:
            lo, hi = layout[name]["data_offsets"]
            header[name] = {**layout[name], "data_offsets": [cursor, cursor+hi-lo]}
            cursor += hi-lo
        raw = encode(header)
        raw += b" " * (-len(raw) % 8)
        raw = struct.pack("<Q", len(raw)) + raw
        outputs[obj] = (raw, len(raw)+cursor)
        for name in names:
            lo, hi = layout[name]["data_offsets"]
            if hi > lo:
                spans.append((origin+lo, origin+hi, obj, len(raw)+header[name]["data_offsets"][0]))

    def _sparse(self, obj, layout, origin, outputs, spans):
        import numpy as np
        entries = {}
        for plan in self.state["plan"]["response"]["plans"].values():
            for index, name in enumerate(plan["parts"]):
                if name not in layout:
                    continue
                rows, width = layout[name]["shape"]
                kind = layout[name]["dtype"]
                offset = index * plan["part_rows"]
                ids = plan["ids"]
                ids = ids[bisect_left(ids, offset):bisect_left(ids, offset+rows)]
                width_bytes = width * WORD[kind]
                filename = digest(name) + ".npy"
                buffer = io.BytesIO()
                np.lib.format.write_array_header_1_0(buffer, dict(descr=NP_TYPE[kind],
                    shape=(len(ids), width), fortran_order=False))
                raw = buffer.getvalue()
                outputs[filename] = (raw, len(raw)+len(ids)*width_bytes)
                entries[name] = dict(tensor=name, ids=ids, shape=[rows, width], storage=kind,
                                     file=filename, shard_sha256=self._pins[obj][1])
                lo = origin + layout[name]["data_offsets"][0]
                for j, row_id in enumerate(ids):
                    first = lo+(row_id-offset)*width_bytes
                    spans.append((first, first+width_bytes, filename, len(raw)+j*width_bytes))
        return entries

    def project(self, tag, obj, dense, last, sparse_last=None, *, role="regular"):
        basename(tag)
        prefix, layout, catalogue = self._header(obj)
        names = sorted(dense)
        require(len(set(names)) == len(names) and all(k in layout and not is_table(k) for k in names),
                "dense projection outside bound selection")
        if role == "planner":
            require(all(layout[name]["dtype"] == "I64" for name in names), "planner requires native I64 buffers")
        require(sparse_last is None or self.state["plan"], "missing official plan")
        selection = dict(role=role, dense=names, last=last, sparse_last=sparse_last,
                         catalogue=self.state["objects"][catalogue["tag"]],
                         plan=self.plan_digest if role != "planner" else None)
        old = self.records.get(tag)
        if old:
            require(old["selection"] == selection and old["obj"] == obj, "projection selection changed")
            live = [name for name, file in old["files"].items() if file["last"] not in self.state["done"]]
            require(live, "projection already released")
            try:
                for name in live:
                    self._file(tag, name)
            except ValueError:
                require(self._owned(self.root / tag), "unowned damaged projection")
                self._save({**self.state, "objects": {k: v for k, v in self.state["objects"].items() if k != tag}})
                del self.records[tag]
                shutil.rmtree(self.root / tag)
                sync_dir(self.root)
            else:
                return tag

        outputs, spans = {}, []
        if names:
            self._dense(obj, layout, names, len(prefix), outputs, spans)
        entries = self._sparse(obj, layout, len(prefix), outputs, spans) if sparse_last is not None else {}
        require(outputs, "empty projection")
        spans.sort()
        require(all(a[1] <= b[0] for a, b in zip(spans, spans[1:])), "overlapping output spans")
        row = dict(invocation=self.binding, tag=tag, obj=obj, source=self._source(obj), role=role,
                   canonical=catalogue["canonical"], selection=selection, spans=spans, entries=entries,
                   files={name: dict(size=size, sha256="0"*64, last=last if name == obj else sparse_last)
                          for name, (_, size) in outputs.items()})
        reservation = self._preflight(obj, tag, row, [n for _, n in outputs.values()], "simultaneous output partials")
        self._begin()
        for name, (raw, _) in outputs.items():
            (self.pending / name).write_bytes(raw)
        cursor = iter(spans)
        span = next(cursor, None)

        def capture(pos, raw):
            nonlocal span
            end = pos+len(raw)
            if pos < len(prefix):
                stop = min(end, len(prefix))
                require(raw[:stop-pos] == prefix[pos:stop], "replay header mismatch")
            while span and span[0] < end:
                lo, hi, name, dest = span
                first, stop = max(pos, lo), min(end, hi)
                if first < stop:
                    with (self.pending / name).open("r+b") as output:
                        output.seek(dest+first-lo)
                        output.write(raw[first-pos:stop-pos])
                if hi > end:
                    break
                span = next(cursor, None)

        require(self._stream(obj, capture, reservation) == catalogue["canonical"], "canonical replay digest changed")
        require(span is None, "incomplete projection")
        self._publish(tag, row)
        if old:
            self.release()
        return tag

    def planner_buffers(self):
        layers = self._metadata.text.get("ple_layer_ids") or []
        return [self._metadata.prefix + f"layers.{i-1}.ple.ple_embedding." + suffix
                for i in layers for suffix in BUFFER_SUFFIXES]

    def planner_bound(self, memory_bytes):
        config = self._metadata.text
        layers = config["ple_layer_ids"]
        require(layers and len(set(layers)) == len(layers)
                and all(positive(i) and i <= config["num_hidden_layers"] for i in layers)
                and positive(config["ngram_size"]-1) and positive(config["heads_per_ngram"])
                and positive(config["ple_embed_dim"]), "invalid planner configuration")
        tokens = [len(p["input_ids"]) for p in self.prompts]
        per_token = (config["ngram_size"]-1) * config["heads_per_ngram"]
        ids = sum(tokens) * per_token
        # Price Python IDs, partition/range records and JSON copies, and the
        # official recorder's largest prompt-local gathered floating tensor.
        coordinator = ids * len(layers) * 384 + len(self._metadata.weight_map) * 512
        worker = max(tokens) * per_token * (128 + 16 * config["ple_embed_dim"]) + coordinator
        require(coordinator <= self.limits.selection_bytes and worker <= memory_bytes,
                "planner selection exceeds memory budget")
        return ids

    def install_plan(self, response, buffer_tags, max_ids):
        require(response.get("transformers") == REFERENCE_VERSION
                and response.get("reference_source_sha256") == self.reference_hash, "planner identity changed")
        expected_buffers = set(self.planner_buffers())
        seen = set()
        for tag in buffer_tags:
            rec = self.records[tag]
            require(rec["role"] == "planner" and not (seen & set(rec["selection"]["dense"])),
                    "invalid planner buffer receipts")
            self._file(tag, rec["obj"])
            seen.update(rec["selection"]["dense"])
        require(seen == expected_buffers, "incomplete planner buffers")
        bases = {name.rsplit(".", 1)[0] + ".ngram_embedding" for name in expected_buffers}
        plans = response["plans"]
        require(plans.keys() == bases, "incomplete official plan")
        tables = set()
        for base, plan in plans.items():
            parts = IndexedCheckpoint.ngram_parts(self._metadata, base)
            require(plan["parts"] == parts, "table part order changed")
            shape = plan["shape"]
            require(isinstance(shape, list) and len(shape) == 2 and all(positive(n) for n in shape),
                    "invalid official table shape")
            rows, width = shape
            ids = plan["ids"]
            require(isinstance(ids, list) and 0 < len(ids) <= max_ids
                    and all(type(r) is int and 0 <= r < rows for r in ids)
                    and all(a < b for a, b in zip(ids, ids[1:])), "invalid official row IDs")
            stride = (rows+len(parts)-1)//len(parts)
            require(type(plan["part_rows"]) is int and plan["part_rows"] == stride, "invalid partition stride")
            for index, name in enumerate(parts):
                require(name in self._metadata.weight_map, "table part absent from index")
                _, layout, _ = self._header(self._metadata.weight_map[name])
                info = layout[name]
                require(0 <= index*stride < rows and info["shape"] == [min(stride, rows-index*stride), width]
                        and info["dtype"] in NP_TYPE, "partition shape/dtype mismatch")
                tables.add(name)
        require(tables == {k for k in self._metadata.weight_map if is_table(k)}, "incomplete table partitions")
        plan = dict(response=response, digest=digest(response), invocation=self.binding,
                    buffers={tag: self.state["objects"][tag] for tag in buffer_tags})
        self._save({**self.state, "plan": plan})
        self.finish({"planner"})

    def sparse_manifest(self, tags):
        plan = self.state["plan"]
        require(plan and plan["invocation"] == self.binding, "missing bound official plan")
        entries, sources = {}, {}
        for tag in tags:
            rec = self.records[tag]
            require(rec["selection"]["plan"] == self.plan_digest, "sparse plan binding changed")
            for name, info in rec["entries"].items():
                require(name not in entries, "duplicate sparse entry")
                self._file(tag, info["file"])
                entries[name] = {**info, "sha256": rec["files"][info["file"]]["sha256"]}
            sources[rec["obj"]] = self._pins[rec["obj"]][1]
        response = plan["response"]
        require(entries.keys() == {name for p in response["plans"].values() for name in p["parts"]},
                "incomplete sparse store")
        return {**response, "entries": entries, "source_shards": sources}

    @contextmanager
    def checkpoint(self, dense_tags, sparse_tags=()):
        """Construct guarded worker links and preserve the sparse manifest for evidence."""
        dense = {}
        for tag in dense_tags:
            rec = self.records[tag]
            obj = rec["obj"]
            require(obj not in dense, "multiple dense projections for one object")
            dense[obj] = self._file(tag, obj)
        sparse = self.sparse_manifest(sparse_tags) if sparse_tags else None
        raw = encode(sparse) if sparse is not None else None
        if raw is not None:
            if self.store.exists():
                require(regular(self.store) and self.store.read_bytes() == raw, "sparse store evidence changed")
            else:
                self.budget.admit("retained sparse manifest", [len(raw)])
                replace_json(self.store, raw)
        self.budget.admit("worker checkpoint", [len(self.owner), *map(len, self._small.values())],
                          dirs=1 + bool(sparse))
        require(not self.worker.exists(), "unrecovered worker checkpoint")
        self.worker.mkdir()
        synced_write(self.worker / ".owner", self.owner)
        try:
            for name, data in self._small.items():
                synced_write(self.worker / name, data)
            for name, path in dense.items():
                os.link(path, self.worker / name)
            guards = {name: file_stamp(self.worker / name) for name in dense}
            store = None
            if sparse:
                store = self.worker / "sparse"
                store.mkdir()
                for tag in sparse_tags:
                    for entry in self.records[tag]["entries"].values():
                        name = entry["file"]
                        os.link(self.root / tag / name, store / name)
                os.link(self.store, store / "store.json")
            self.budget.admit("worker links")
            yield IndexedCheckpoint(self.worker, guards), guards, store, sha(raw) if raw is not None else None
        finally:
            shutil.rmtree(self.worker)
            sync_dir(self.root)

    def finish(self, consumers):
        done = sorted(set(self.state["done"]) | set(consumers))
        if done != self.state["done"]:
            self._save({**self.state, "done": done})
        self.release()

    def release(self):
        done = set(self.state["done"])
        for tag, rec in self.records.items():
            touched = False
            for name, info in rec["files"].items():
                if info["last"] in done:
                    folder = self.root / tag
                    require(self._owned(folder), "unowned release directory")
                    path = folder / basename(name)
                    if path.exists() or path.is_symlink():
                        path.unlink()
                        touched = True
            if touched:
                sync_dir(self.root / tag)
