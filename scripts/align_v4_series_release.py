#!/usr/bin/env python3
"""Release the registered ALIGN v4 series from finalized, admitted records."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
from contextlib import contextmanager
import csv
from dataclasses import dataclass, replace
import hashlib
from importlib.machinery import PathFinder, SourceFileLoader
from io import StringIO
import json
import math
import os
from pathlib import Path
from stat import S_ISREG
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
_CALLER_CODE = sys._getframe().f_code
PROJECT_PACKAGES = ("joulewise", "scripts")
CALLER_PATH = "scripts/align_v4_series_release.py"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

class ReleaseSourceLoader(SourceFileLoader):
    """Keep the digest of the source bytes used to create the loaded code."""

    def __init__(self, fullname, path, *, source_check=None):
        super().__init__(fullname, path)
        self.source_check = source_check

    def get_code(self, fullname):
        source = self.get_data(self.path)
        self.source_digest = hashlib.sha256(source).hexdigest()
        if self.source_check is not None:
            self.source_check(self.path, self.source_digest)
        return self.source_to_code(source, self.path)


class ReleaseSourceFinder:
    def __init__(self):
        self.bindings = None
        self.binding_refused = False

    def find_spec(self, fullname, path=None, target=None):
        parts = fullname.split(".")
        if parts[0] not in PROJECT_PACKAGES:
            return None
        spec = PathFinder.find_spec(fullname, [str(ROOT.joinpath(*parts[:-1]))])
        if spec is None:
            raise ModuleNotFoundError(f"release source missing: {fullname}", name=fullname)
        if spec.origin is None:
            spec.submodule_search_locations = [str(ROOT.joinpath(*parts))]
        else:
            origin = Path(spec.origin)
            if not isinstance(spec.loader, SourceFileLoader) or origin.resolve() != origin:
                raise ImportError(f"release source outside its checkout: {fullname}", name=fullname)
            spec.loader = ReleaseSourceLoader(fullname, spec.origin, source_check=self.check_source)
        return spec

    def check_source(self, origin, digest):
        relative = Path(origin).relative_to(ROOT).as_posix()
        if self.bindings is not None and self.bindings.get(relative) != digest:
            self.binding_refused = True
            raise ValueError("loaded release dependency differs from the receipt")

    @contextmanager
    def installed(self):
        previous = self.bindings, self.binding_refused
        self.bindings = None
        self.binding_refused = False
        sys.meta_path.insert(0, self)
        try:
            yield
        finally:
            sys.meta_path.remove(self)
            self.bindings, self.binding_refused = previous


# Capture the actual source of the first-party import tree. Use the same
# finder while releasing so late imports cannot execute unsigned code.
_release_sources = ReleaseSourceFinder()
with _release_sources.installed():
    from joulewise.align.apple import harvest_offload, km003c, light_triage, rl176, s_rows
    from joulewise.align.apple import v4_contention, v4_desk_seal as seal, v4_registration
    from joulewise.align.apple.workload import read_episode_bundle
    from joulewise.align.records import ClockMapping, PowerTrace, from_json
    from joulewise.b5.harvest import write_json_once
    from scripts import align_v4_next_arm_packet as packet, align_v4_series as series
    from scripts.align_v4_session import HELD_WINDOW_REASONS


RELEASE_REF = "refs/remotes/origin/align-v4-series-release"
REGISTRATION_RECEIPT = v4_registration.REGISTRATION + "registration_receipt.json"
RELEASE_METADATA = (seal.SERIES_COMPLETE, seal.SERIES_MANIFEST, seal.RELEASE_RECEIPT)
LAYOUT = "powermetrics-rails-v1"
PM_ROWS = "outputs/align_s_pm_rows.json"
DC_FILE = "outputs/align_dc_in.json"
RAIL_FILE = "outputs/align_soc_rails.csv"
REQUIRED_BUNDLE_FILES = ("config.json", "metadata.json", "outputs/align_episode.json", RAIL_FILE)
OPTIONAL_BUNDLE_FILES = ("events.jsonl", "outputs/align_runtime_events.jsonl",
                         "outputs/align_thermal.jsonl", "outputs/align_turns.jsonl")
NO_ROW_CODES = frozenset({
    s_rows.START_OUT_OF_STATE, s_rows.START_STATE_UNOBSERVED, s_rows.CUT_IN_PREFILL,
    s_rows.CLOCK_REFERENCE_MISSING, s_rows.TOKEN_STAMPS_UNAVAILABLE, s_rows.AFTER_HOT_TURN,
    "deadman_before_first_token", "no_decode_token", "token_stamps_count_mismatch",
})
COMPANION_PRINTS = ("S_a4", "S_w", "benign_slopes")
SOC_RAILS = frozenset(("powermetrics", name) for name in ("cpu_power", "gpu_power", "ane_power"))
RAIL_COLUMNS = {"timestamp_s", "power_w", "source", "rail"}
RAIL_INTERVAL_COLUMNS = {"interval_start_s", "interval_end_s"}
METER_DIRECTORY = tuple(Path(km003c.REQUIREMENT["custody_directory"]).parts)
PROTECTED_INPUT_NAMES = {
    "align_dc_in", "dc_in", "benign_dc", "wall_meter", "km003c", "system_total",
    "power_trace", "align_power_trace", "transcript", "transcripts", "align_transcript", "align_transcripts",
    "restricted", "custody", "night_custody", "night_archive", "sealed",
}
ENCODED_SUFFIXES = {
    ".gz", ".gzip", ".zst", ".zstd", ".bz2", ".xz", ".lz", ".lz4", ".zip", ".7z", ".tar", ".tgz",
    ".b64", ".base64", ".uu", ".uue",
}


def protected_path(path):
    parts = Path(path.casefold()).parts
    native_meter = any(parts[i:i + len(METER_DIRECTORY)] == METER_DIRECTORY for i in range(len(parts)))
    return native_meter or any(part.partition(".")[0].replace("-", "_") in PROTECTED_INPUT_NAMES
                               for part in parts)


def input_parts(relative):
    parts = Path(relative).parts
    packet.require(parts and not Path(relative).is_absolute()
                   and all(part not in (".", "..") for part in parts)
                   and Path(*parts).as_posix() == relative, "unsafe release input path")
    return parts


@contextmanager
def named_directory(root, parts):
    """Walk real directories by their exact names, even on a case-folding filesystem."""
    directory_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
    directory = os.open(root, directory_flags)
    try:
        for part in parts:
            if part not in os.listdir(directory):
                raise FileNotFoundError("release directory spelling differs from the requested path")
            child = os.open(part, directory_flags, dir_fd=directory)
            os.close(directory)
            directory = child
        yield directory
    finally:
        os.close(directory)


def named_bytes(root, relative):
    packet.require(not protected_path(relative), "protected input requires the authorized benign provider")
    return open_named_bytes(root, relative)


def open_named_bytes(root, relative):
    """Open exactly one readable, unlinked regular file below a real root."""
    *parents, name = input_parts(relative)
    with named_directory(root, parents) as directory:
        if name not in os.listdir(directory):
            raise FileNotFoundError("release file spelling differs from the requested path")
        file_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        with os.fdopen(os.open(name, file_flags, dir_fd=directory), "rb") as source:
            info = os.fstat(source.fileno())
            packet.require(S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_mode & 0o444,
                           "unreadable or linked release input")
            return source.read()


def require_executing_bindings(receipt):
    bindings = {
        path: digest for path, digest in receipt["artifacts"].items()
        if path.partition("/")[0] in PROJECT_PACKAGES and path.endswith(".py")
    }
    packet.require(Path(__file__).resolve() == ROOT / CALLER_PATH,
                   "release caller was loaded from another checkout")
    # Check the signed source inventory before any member file is opened.
    # This includes registered lazy imports that have not executed yet.
    for relative, expected in bindings.items():
        raw = open_named_bytes(ROOT, relative)
        packet.require(packet.digest(raw) == expected, "executing release source differs from the receipt")
        if relative == CALLER_PATH:
            code = compile(raw, _CALLER_CODE.co_filename, "exec", dont_inherit=True)
            packet.require(code == _CALLER_CODE, "loaded release caller differs from the receipt")
    for name, module in list(sys.modules.items()):
        if name == __name__ or name.partition(".")[0] not in PROJECT_PACKAGES:
            continue
        origin = getattr(module, "__file__", None)
        if origin is None:
            continue  # Namespace packages have no executable source.
        stem = name.replace(".", "/")
        paths = (stem + ".py", stem + "/__init__.py")
        loader = getattr(module, "__loader__", None)
        if __name__ != "__main__" and not isinstance(loader, ReleaseSourceLoader) \
                and not any(path in bindings for path in paths):
            continue  # Unrelated modules imported by the in-process test harness.
        path = Path(origin).resolve().relative_to(ROOT).as_posix()
        packet.require(path in paths and path in bindings, "loaded release module is not bound")
        if isinstance(loader, ReleaseSourceLoader):
            packet.require(loader.source_digest == bindings[path],
                           "loaded release source differs from the receipt")
        elif __name__ == "__main__":
            raise ValueError("release module was loaded outside the source loader")
    if _release_sources in sys.meta_path:
        _release_sources.bindings = bindings


class SeriesEvidence(packet.GitEvidence):
    """Verify capture inventories without opening embedded capture bytes."""

    def git(self, *args):
        return super().git("--no-replace-objects", *args)

    def raw_evidence(self, commit, record_path, descriptor):
        packet.require(isinstance(descriptor, dict) and "locator" in descriptor,
                       "release requires digest-only capture inventory")
        return super().raw_evidence(commit, record_path, descriptor)


def bound_history(root, guarded_metadata):
    packet.require((root / ".git").exists(), "release record repository missing")
    evidence = SeriesEvidence(root)
    worktree = evidence.git("rev-parse", "--show-toplevel").decode().strip()
    packet.require(Path(worktree).resolve() == root, "release record repository differs from the root")
    tip = evidence.git("rev-parse", "--verify", RELEASE_REF + "^{commit}").decode().strip()
    for path in RELEASE_METADATA:
        packet.require(guarded_metadata[path] == evidence.read(tip, path),
                       "release metadata differs from committed authority")
    completion = packet.decode(evidence.read(tip, seal.SERIES_COMPLETE))
    ledger = packet.decode(evidence.read(tip, packet.SERIES_PATH))
    packet.require(ledger["schema"] == packet.SERIES_SCHEMA, "unexpected release ledger")
    terminal = ledger["previous_record"]
    packet.require(terminal["commit"] == completion["record_commit"],
                   "completion does not identify the terminal record")
    evidence.git("merge-base", "--is-ancestor", terminal["commit"], tip)
    chain = []
    link = terminal
    while link is not None:
        record = packet.WindowRecord(evidence, link["commit"], link["path"])
        packet.require(record.sha256 == link["sha256"], "record chain digest mismatch")
        if chain:
            successor = chain[-1]
            packet.require(record.commit != successor.commit, "record chain does not move backwards")
            evidence.git("merge-base", "--is-ancestor", record.commit, successor.commit)
            packet.require(not (record.has_final_sources() and successor.record.get("previous_final")),
                           "two final records for one assignment")
            record.bind_final(successor)
        chain.append(record)
        link = record.previous_link
    packet.require(chain[-1].window in ("R1", "W1"), "incomplete series history")
    first_c1, = (record for record in chain if record.window == "C1")
    packet.require(first_c1.previous_link is not None, "C1 has no bound predecessor")
    predecessor = first_c1.previous_link["commit"]
    registration_bytes = evidence.read(predecessor, REGISTRATION_RECEIPT)
    receipt_digest = packet.digest(registration_bytes)
    evidence.read(tip, REGISTRATION_RECEIPT, receipt_digest)
    packet.require(packet.digest(named_bytes(root, REGISTRATION_RECEIPT)) == receipt_digest,
                   "registration receipt differs from C1 predecessor")
    registered_commit = evidence.commit(packet.decode(registration_bytes)["commit"])
    evidence.git("merge-base", "--is-ancestor", registered_commit, predecessor)
    return completion, ledger, reversed(chain), registration_bytes


@dataclass(frozen=True)
class Assignment:
    window: str
    pair: str
    ordinal: int
    run_id: str
    seed_index: int
    episode_seed: int
    reason: str | None
    files: RestoredFiles | None

    @property
    def key(self):
        return self.window, self.pair, self.ordinal


@dataclass(frozen=True)
class BoundInput:
    path: str
    size: int | None
    sha256: str


def manifest_path(root, prefix, name):
    packet.require(isinstance(name, str), "manifest input path is missing")
    path = Path(name)
    if path.is_absolute():
        packet.require(path.as_posix() == name and path.is_relative_to(root),
                       "manifest input is outside the authenticated measurement root")
        relative = path.relative_to(root).as_posix()
    else:
        input_parts(name)
        relative = f"{prefix}/{name}"
    input_parts(relative)
    return relative


def manifest_inputs(manifest, root, prefix):
    """Collect keyed file tables and explicit descriptors at any depth."""
    bindings = {}

    def add(name, descriptor):
        relative = manifest_path(root, prefix, name)
        sha256 = descriptor.get("sha256", descriptor.get("digest"))
        size = descriptor.get("size")
        packet.require(v4_registration.is_digest(sha256) and descriptor.get("digest", sha256) == sha256
                       and (size is None or type(size) is int and size >= 0), "invalid manifest file binding")
        if relative in bindings:
            previous = bindings[relative]
            packet.require(previous.sha256 == sha256 and (size is None or previous.size in (None, size)),
                           "manifest file bindings disagree")
            size = previous.size if size is None else size
        bindings[relative] = BoundInput(relative, size, sha256)

    pending = [manifest]
    while pending:
        node = pending.pop()
        if isinstance(node, dict):
            if "path" in node and ("sha256" in node or "digest" in node):
                add(node["path"], node)
            for name, child in node.items():
                if (isinstance(child, dict) and "path" not in child
                        and ("sha256" in child or "digest" in child)):
                    add(name, child)
            pending.extend(node.values())
        elif isinstance(node, list):
            pending.extend(node)
    closure = manifest["closure"]
    for name, declared in closure["inputs"].items():
        packet.require(Path(name).is_absolute() and declared["real"] == name
                       and manifest_path(root, prefix, name) in bindings,
                       "declared input does not name a byte-bound regular path")
    return bindings


@dataclass(frozen=True)
class ClosureLink:
    hops: tuple[tuple[str, str], ...]
    target: str
    mirror_path: str | None = None
    directories: tuple[str, ...] = ()
    directory_target: bool = False
    ignored: tuple[str, ...] = ()


def internal_link(entries, root, prefix, name):
    """Resolve authenticated link text within the finalized directory inventory."""
    store = str(root / prefix)
    components = deque(input_parts(name))
    parts = []
    hops, directories = [], set()
    while components:
        component = components.popleft()
        if component in ("", "."):
            continue
        if component == "..":
            packet.require(parts, "internal link leaves the restore")
            parts.pop()
            continue
        parts.append(component)
        path = "/".join(parts)
        row = entries.get(path, {})
        if "link" in row:
            packet.require(len(hops) < harvest_offload.MAX_LINK_HOPS, "cyclic or excessive internal link chain")
            hop = row["link"]
            packet.require(isinstance(hop, str) and hop, "invalid internal link text")
            hops.append((f"{prefix}/{path}", hop))
            parts.pop()
            if hop.startswith("/"):
                packet.require(hop == store or hop.startswith(store + "/"), "internal link leaves the restore")
                parts.clear()
                hop = hop[len(store):]
            components.extendleft(reversed(hop.split("/")))
        elif components:
            packet.require(row == {"directory": True}, "internal link traverses an unbound directory")
            directories.add(f"{prefix}/{path}")
    path = "/".join(parts)
    target = entries.get(path, {"directory": True} if not path else {})
    directory = target == {"directory": True}
    packet.require(directory or "sha256" in target or "digest" in target, "unbound internal link target")
    return ClosureLink(tuple(hops), f"{prefix}/{path}" if path else prefix,
                       directories=tuple(sorted(directories)), directory_target=directory)


def manifest_links(manifest, root, prefix):
    """Plan the exact link hops from authenticated text, without resolving any file."""
    closure = manifest["closure"]
    entries = manifest["entries"]
    external = closure["links"]
    for name, row in external.items():
        path = manifest_path(root, prefix, name)
        hops = row["hops"]
        packet.require(isinstance(hops, list) and hops and len(hops) <= harvest_offload.MAX_LINK_HOPS
                       and entries.get(name) == {"link": hops[0]}, "unbound closure link")
        planned = []
        for hop in hops:
            packet.require(isinstance(hop, str) and hop and ".." not in Path(hop).parts, "unsafe closure hop")
            planned.append((path, hop))
            path = manifest_path(root, prefix, (root / path).parent.joinpath(hop).as_posix())
        packet.require(str(root / path) == row["target"], "closure link target disagrees with its hops")
        mirror_path, ignored = None, ()
        if row["class"] == "mirror":
            mirror_path = row["mirror_path"]
            if mirror_path != ".":
                input_parts(mirror_path)
            mirror_root = Path(closure["mirror"]["root"])
            packet.require(mirror_root.is_absolute() and str(mirror_root / mirror_path) == row["target"],
                           "closure target differs from its mirror path")
            ignored = tuple(entry["path"].removesuffix("/") for entry in row["ignored"])
            for name in ignored:
                input_parts(name)
        yield ClosureLink(tuple(planned), path, mirror_path, directory_target=row.get("kind") == "directory",
                          ignored=ignored)
    for name, row in entries.items():
        if "link" in row and name not in external:
            yield internal_link(entries, root, prefix, name)


@dataclass(frozen=True)
class BoundDirectory:
    path: str
    children: frozenset[str]


def directory_inventory(target, members, directories):
    """Build exact child sets from a finalized, flat recursive inventory."""
    packet.require(isinstance(members, list) and isinstance(directories, list),
                   "invalid finalized directory inventory")
    children = {name: set() for name in directories}
    packet.require("." in children and len(children) == len(directories)
                   and len(set(members)) == len(members) and not children.keys() & set(members),
                   "conflicting finalized directory membership")
    for path in (*members, *(name for name in directories if name != ".")):
        *parents, name = input_parts(path)
        parent = "/".join(parents) if parents else "."
        packet.require(parent in children, "inventory has an unbound parent directory")
        children[parent].add(name)
    return tuple(BoundDirectory((Path(target) / relative).as_posix(), frozenset(names))
                 for relative, names in children.items())


def manifest_directories(manifest, root, prefix, listed, links):
    members, directories = ["finalized_manifest.json"], ["."]
    aliases = {link.hops[0][0] for link in links}
    for name, entry in manifest["entries"].items():
        input_parts(name)
        if entry == {"directory": True}:
            directories.append(name)
        else:
            relative = f"{prefix}/{name}"
            packet.require(relative in listed or relative in aliases, "restored input lacks a manifest binding")
            members.append(name)
    yield from directory_inventory(prefix, members, directories)

    closure = manifest["closure"]
    for row in closure["links"].values():
        if row["class"] == "bytes" and row.get("kind") == "directory":
            target = manifest_path(root, prefix, row["target"])
            members = row["files"]
            inventory = directory_inventory(target, members, row["directories"])
            packet.require(all(f"{target}/{name}" in listed for name in members),
                           "directory member lacks a finalized digest")
            yield from inventory
        if row["class"] == "mirror":
            mirror_root = Path(closure["mirror"]["root"])
            for ignored in row["ignored"]:
                if "directories" not in ignored:
                    continue
                name = ignored["path"].removesuffix("/")
                input_parts(name)
                target = manifest_path(root, prefix, (mirror_root / name).as_posix())
                members = []
                for member, size in ignored["members"]:
                    input_parts(member)
                    binding = listed.get(f"{target}/{member}")
                    packet.require(binding is not None and (size is None or size == binding.size),
                                   "ignored directory member lacks a matching finalized digest")
                    members.append(member)
                yield from directory_inventory(target, members, ignored["directories"])


class InputLedger:
    def __init__(self):
        self.entries = {}
        self.verified = set()
        self.protected = set()

    def add_manifest(self, files, links, directories):
        for path, bound in files.items():
            previous = self.entries.get(path)
            if previous is not None:
                packet.require(isinstance(previous, BoundInput) and previous.sha256 == bound.sha256
                               and (bound.size is None or previous.size in (None, bound.size)),
                               "conflicting finalized input bindings")
            self.entries[path] = previous if bound.size is None and previous is not None else bound
        for link in links:
            path = link.hops[0][0]
            packet.require(path not in self.entries, "conflicting finalized link bindings")
            self.entries[path] = link
            if link.mirror_path is not None:
                self.entries.setdefault(link.target, None)
        for directory in directories:
            previous = self.entries.get(directory.path)
            packet.require(previous in (None, directory),
                           "conflicting finalized directory bindings")
            self.entries[directory.path] = directory

    def classify(self):
        chains = [({entry.target, *(path for path, _ in entry.hops)}, entry.directories)
                  for entry in self.entries.values() if isinstance(entry, ClosureLink)]
        paths = self.entries.keys() | set().union(*(chain for chain, _ in chains))
        self.protected = {path for path in paths if protected_path(path)}
        while True:
            expanded = self.protected.union(*(chain for chain, directories in chains
                                             if any(map(self.is_protected, chain))
                                             or any(map(self.is_protected, directories))))
            if expanded == self.protected:
                break
            self.protected = expanded
        for binding in self.entries.values():
            if isinstance(binding, ClosureLink) and self.is_protected(binding.target) and not binding.directory_target:
                packet.require(isinstance(self.entries.get(binding.target), BoundInput),
                               "protected link target lacks a manifest digest")

    def is_protected(self, path):
        return protected_path(path) or path in self.protected or any(
            parent.as_posix() in self.protected for parent in Path(path).parents)

    def require_complete(self):
        packet.require(self.entries.keys() == self.verified, "finalized release inputs remain unverified")


def bound_bytes(root, bound):
    require_plain_path(bound.path)
    return require_bound_bytes(named_bytes(root, bound.path), bound)


def require_plain_path(path):
    suffixes = set(Path(path.casefold()).suffixes)
    packet.require(not suffixes & ENCODED_SUFFIXES, "manifest lists an encoded or compressed input")


def require_bound_bytes(raw, bound):
    packet.require((bound.size is None or len(raw) == bound.size) and packet.digest(raw) == bound.sha256,
                   "restored file differs from record manifest")
    return raw


def verify_ancillary_input(root, bound):
    """Verify a listed ancillary input in an admitted plain representation."""
    text = bound_bytes(root, bound).decode("utf-8")
    packet.require(all(not (ord(char) < 32 or ord(char) == 127) or char in "\t\n\r" for char in text),
                   "manifest file has no admitted plain representation")


def plain_input(name, raw):
    """Accept the registered plain grammars at their canonical paths."""
    text = raw.decode("utf-8")
    if name.endswith(".jsonl"):
        rows = tuple(packet.decode(line) for line in raw.splitlines() if line.strip())
        packet.require(rows and all(isinstance(row, dict) for row in rows), "release journal needs records")
        return rows
    if name.endswith(".json"):
        value = packet.decode(text)
        required = list if name.endswith("/" + PM_ROWS) else dict
        packet.require(isinstance(value, required) and value, "release JSON has no records or has the wrong shape")
        return value

    packet.require(name.endswith("/" + RAIL_FILE), "unexpected release input format")
    reader = csv.DictReader(StringIO(text, newline=""), strict=True)
    columns = reader.fieldnames or ()
    packet.require(len(columns) == len(set(columns))
                   and set(columns) in (RAIL_COLUMNS, RAIL_COLUMNS | RAIL_INTERVAL_COLUMNS),
                   "unexpected rail projection header")
    channels = set()
    for row in reader:
        channel = row["source"], row["rail"]
        packet.require(None not in row and channel in SOC_RAILS, "rail projection contains an unbound channel")
        numbers = (row["timestamp_s"], row["power_w"],
                   *(row[name] for name in RAIL_INTERVAL_COLUMNS if row.get(name)))
        packet.require(all(math.isfinite(float(number)) for number in numbers), "invalid rail sample")
        channels.add(channel)
    packet.require(rl176.GPU in channels, "rail projection is missing the GPU trace")


class RestoredFiles:
    def __init__(self, root, record, layout, ledger=None):
        packet.require(layout["trace_layout"] == LAYOUT, "no admitted rail-only file layout")
        self.root = root
        self.prefix = f"series/restored/{record.window}"
        raw = named_bytes(root, f"{self.prefix}/finalized_manifest.json")
        packet.require(packet.digest(raw) == record.finalized_manifest_sha256,
                       "restored manifest differs from record digest")
        manifest = packet.decode(raw)
        harvest_offload._validate_finalized(manifest)
        self.entries = manifest["entries"]
        self.listed = manifest_inputs(manifest, root, self.prefix)
        self.closure = manifest["closure"]
        self.mirror = self.closure["mirror"]
        self.links = tuple(manifest_links(manifest, root, self.prefix))
        self.directories = tuple(manifest_directories(manifest, root, self.prefix, self.listed, self.links))
        self.ledger = InputLedger() if ledger is None else ledger
        self.ledger.add_manifest(self.listed, self.links, self.directories)
        self.stems = defaultdict(set)
        for name in self.entries:
            input_parts(name)
            self.stems[self.stem(name)].add(name)
        if ledger is None:
            self.ledger.classify()
            self.verify_finalized()
            self.verify_inventory()
        journal = layout["hazard_journal"]
        self.hazard_input = None
        if journal is not None:
            packet.require(journal == "archive/align_s_hazard.jsonl",
                           "unexpected supplemental cut source")
            self.hazard_input = self.bind(journal)
        self._hazard = None

    @staticmethod
    def stem(name):
        parent, _, filename = name.rpartition("/")
        return parent.casefold(), filename.partition(".")[0].casefold()

    def is_protected(self, path):
        return self.ledger.is_protected(path)

    def inspect_closure_path(self, path):
        relative = manifest_path(self.root, self.prefix, str(path))
        packet.require(not self.is_protected(relative), "finalized closure is outside the authorized release scope")
        return relative

    def closure_file_matches(self, path, row):
        relative = self.inspect_closure_path(path)
        bound_bytes(self.root, BoundInput(relative, row["size"], row["sha256"]))
        return True

    def verify_finalized(self):
        # The validator gets the original record-bound closure. It checks
        # links and identity first, and the authorized provider owns protected bytes.
        deferred = frozenset(name for group in ("files", "ignored") for name in self.closure[group]
                             if self.is_protected(manifest_path(self.root, self.prefix, name)))
        harvest_offload._verify_closure(
            self.closure, self.root / self.prefix, where="series release",
            mirror_identity=self.checkout_mirror_identity, transported=deferred,
            inspect_path=self.inspect_closure_path, file_matches=self.closure_file_matches,
        )

    @contextmanager
    def mirror_checkout(self):
        mirror_root = Path(self.mirror["root"])
        relative = mirror_root.relative_to(self.root)
        packet.require(not self.is_protected(relative.as_posix()), "protected mirror path cannot be opened")
        with named_directory(self.root, relative.parts):
            evidence = SeriesEvidence(mirror_root)
            packet.require(evidence.git("rev-parse", "--show-toplevel").decode().strip() == str(mirror_root),
                           "closure mirror does not bind the named Git worktree")
            yield evidence

    def checkout_mirror_identity(self):
        if self.mirror is None:
            return None
        with self.mirror_checkout() as evidence:
            prefix = evidence.repo.relative_to(self.root)
            protected = {Path(path).relative_to(prefix): binding for path, binding in self.ledger.entries.items()
                         if self.is_protected(path) and Path(path).is_relative_to(prefix)}
            scopes = tuple(Path(link.mirror_path) for link in self.links if link.mirror_path is not None)
            if protected or scopes:
                tracked = {Path(os.fsdecode(name)) for name in evidence.git("ls-files", "-z").split(b"\0") if name}
                for path in tracked:
                    if any(path.is_relative_to(scope) for scope in scopes):
                        packet.require(not self.is_protected((prefix / path).as_posix()),
                                       "mirror identity would inspect a protected input")
                for path, binding in protected.items():
                    packet.require(path not in tracked, "mirror identity would inspect a protected input")
                    if isinstance(binding, BoundDirectory):
                        packet.require(not any(child.is_relative_to(path) for child in tracked),
                                       "mirror identity would inspect a protected directory")
                        evidence.git("check-ignore", "--quiet", "--", path.as_posix())
            identity = harvest_offload.checkout_identity(evidence.repo)
        packet.require(harvest_offload._usable_identity(identity), "finalized mirror identity is unavailable")
        return identity

    def verify_inventory(self):
        # Compare names in real, manifest-listed directories. File bytes are
        # verified under their own bindings, with protected inputs left to the provider.
        for binding in self.directories:
            if self.is_protected(binding.path):
                continue
            self.verify_directory(binding)
            self.ledger.verified.add(binding.path)

    def verify_directory(self, binding):
        self.inspect_closure_path(self.root / binding.path)
        with named_directory(self.root, input_parts(binding.path)) as directory:
            packet.require(set(os.listdir(directory)) == binding.children,
                           "restored names differ from finalized inventory")

    def bind(self, name, *, optional=False):
        # Only the canonical representation belongs to this input. Compare
        # the whole namespace so an unknown encoding cannot look like absence.
        variants = self.stems.get(self.stem(name), set())
        packet.require(not variants.difference((name,)), "unapproved representation in the release manifest")
        if name not in self.entries:
            packet.require(optional, "required release input missing from the restored manifest")
            return None
        row = self.entries[name]
        packet.require(isinstance(row, dict) and set(row) == {"size", "sha256"}
                       and type(row["size"]) is int and row["size"] >= 0
                       and v4_registration.is_digest(row["sha256"]), "release input is not a bound regular file")
        return BoundInput(name, row["size"], row["sha256"])

    def read_bound(self, bound):
        relative = f"{self.prefix}/{bound.path}"
        packet.require(not self.is_protected(relative), "protected input requires the authorized benign provider")
        packet.require(relative in self.listed, "member input lacks a manifest binding")
        listed = self.ledger.entries[relative]
        raw = bound_bytes(self.root, listed)
        parsed = plain_input(bound.path, raw)
        self.ledger.verified.add(relative)
        return raw, parsed

    def verify_mirror_target(self, link):
        packet.require(not self.is_protected(link.target), "protected mirror target cannot be opened")
        with self.mirror_checkout() as evidence:
            commit = evidence.commit(self.mirror["identity"]["head"])
            scoped = () if link.mirror_path == "." else ("--", link.mirror_path)
            tree = {}
            for entry in evidence.git("ls-tree", "-rtz", "--full-tree", commit, *scoped).split(b"\0"):
                if entry:
                    header, name = entry.split(b"\t", 1)
                    tree[os.fsdecode(name)] = header.decode("ascii").split()
            entry = tree.get(link.mirror_path, ())
            if link.mirror_path == "." or entry[:2] == ["040000", "tree"]:
                self.verify_mirror_directory(link, tree, "sha1" if len(commit) == 40 else "sha256")
                return
            committed = evidence.read(commit, link.mirror_path) if entry else None
        if committed is None:
            self.verify_ignored_mirror_target(link)
            return
        reference = BoundInput(link.target, len(committed), packet.digest(committed))
        existing = self.ledger.entries[link.target]
        packet.require(existing is None or (isinstance(existing, BoundInput) and existing.sha256 == reference.sha256
                                            and existing.size in (None, reference.size)),
                       "closure mirror target conflicts with its listed digest")
        verify_ancillary_input(self.root, reference)
        self.ledger.entries[link.target] = reference
        self.ledger.verified.add(link.target)

    def verify_ignored_mirror_target(self, link):
        # The finalized closure binds ignored inputs by their working path and
        # bytes or directory inventory. Git has no blob for these inputs.
        packet.require(link.mirror_path in link.ignored, "mirror target has no finalized ignored binding")
        bound = self.ledger.entries[link.target]
        if isinstance(bound, BoundInput):
            verify_ancillary_input(self.root, bound)
            self.ledger.verified.add(link.target)
        else:
            packet.require(isinstance(bound, BoundDirectory) and link.target in self.ledger.verified,
                           "ignored mirror directory is not verified")

    def verify_mirror_directory(self, link, tree, algorithm):
        scope = Path(link.mirror_path)
        directories, leaves = ["."], {}
        for name, (mode, kind, oid) in tree.items():
            input_parts(name)
            if name == link.mirror_path:
                continue
            relative = Path(name).relative_to(scope).as_posix()
            if mode == "040000" and kind == "tree":
                directories.append(relative)
            else:
                packet.require(kind == "blob" and mode in ("100644", "100755", "120000"),
                               "unsupported committed mirror entry")
                leaves[relative] = (mode, oid)
        ignored = [Path(name).relative_to(scope).as_posix() for name in link.ignored]
        if scope == Path("."):
            ignored.append(".git")  # The validated checkout owns its Git administrative entry.
        inventory = directory_inventory(link.target, [*leaves, *ignored], directories)
        root = next(binding for binding in inventory if binding.path == link.target)
        existing = self.ledger.entries[link.target]
        packet.require(existing in (None, root), "closure mirror target conflicts with its listed inventory")
        for binding in inventory:
            self.verify_directory(binding)
        for relative, (mode, oid) in leaves.items():
            path = self.inspect_closure_path(self.root / link.target / relative)
            if mode == "120000":
                *parents, name = input_parts(path)
                with named_directory(self.root, parents) as directory:
                    raw = os.fsencode(os.readlink(name, dir_fd=directory))
            else:
                require_plain_path(path)
                raw = named_bytes(self.root, path)
            digest = hashlib.new(algorithm, f"blob {len(raw)}\0".encode("ascii"))
            digest.update(raw)
            packet.require(digest.hexdigest() == oid, "restored mirror file differs from its committed blob")
        self.ledger.entries[link.target] = root
        self.ledger.verified.add(link.target)

    def verify_link(self, link):
        for path in link.directories:
            with named_directory(self.root, input_parts(path)):
                pass
        for path, expected in link.hops:
            *parents, name = input_parts(path)
            with named_directory(self.root, parents) as directory:
                packet.require(name in os.listdir(directory) and os.readlink(name, dir_fd=directory) == expected,
                               "restored link differs from its manifest binding")
        if link.mirror_path is not None:
            self.verify_mirror_target(link)
        elif link.directory_target:
            packet.require(isinstance(self.ledger.entries.get(link.target), BoundDirectory)
                           and link.target in self.ledger.verified, "restored directory target is unverified")
        else:
            packet.require(isinstance(self.ledger.entries.get(link.target), BoundInput),
                           "restored link target lacks a manifest digest")
        self.ledger.verified.add(link.hops[0][0])

    def verify_listed_inputs(self, *, member_paths=()):
        for link in self.links:
            if self.is_protected(link.hops[0][0]):
                continue
            self.verify_link(link)
        for path in self.listed:
            if not self.is_protected(path) and path not in self.ledger.verified and path not in member_paths:
                verify_ancillary_input(self.root, self.ledger.entries[path])
                self.ledger.verified.add(path)

    def bind_bundle(self, run_id, name, *, optional=False):
        packet.require(Path(run_id).name == run_id and run_id not in ("", ".", ".."),
                       "unsafe run identity")
        return self.bind(f"runs/{run_id}/{name}", optional=optional)

    def member_inputs(self, run_id):
        names = REQUIRED_BUNDLE_FILES + OPTIONAL_BUNDLE_FILES + (PM_ROWS,)
        bindings = {name: self.bind_bundle(run_id, name, optional=name in OPTIONAL_BUNDLE_FILES) for name in names}
        return {name: binding for name, binding in bindings.items() if binding is not None}

    def hazard(self):
        if self._hazard is None:
            self._hazard = () if self.hazard_input is None else self.read_bound(self.hazard_input)[1]
        return self._hazard


def final_roster(root, manifest, completion, ledger, chain, input_ledger):
    history, admitted, layouts = [], [], ledger["release_layouts"]
    retries = set()
    for record in chain:
        if record.window in ("R1", "W1"):
            continue
        window = series.slot_of(record.window)
        selected = series.selected(manifest, window)
        packet.require(record.record["role"] == selected["role"], "window role disagrees with manifest")
        packet.require(record.final_evidence() is None, "no final eligibility for a series attempt")
        plan = record.source("collection_plan")
        packet.require(plan["series_manifest_sha256"] == completion["series_manifest_sha256"],
                       "collection plan names a different manifest")
        captured = record.counted_captures()
        packet.require(record.window == (f"{window}#2" if window in retries else window),
                       "unexpected retry identity in finalized history")
        if not captured:
            retries.add(window)
        counted = (record.eligibility(allow_provisional=False) if captured else
                   {"eligible_benign": dict.fromkeys(packet.cadence.CAL_PAIRS, 0), "status": "final"})
        barred = record.structural_bar(captured)
        history.append({"window_id": window, "attempt_id": record.window, "status": counted["status"],
                        "captured_members": captured, "eligible_benign": counted["eligible_benign"],
                        "barred": barred})
        if not captured or barred:
            continue
        exclusions = record.source("exclusions")
        reasons = exclusions["reasons"]
        packet.require(isinstance(reasons, list) and all(isinstance(reason, str) for reason in reasons),
                       "final harvest reasons malformed")
        if HELD_WINDOW_REASONS.intersection(reasons):
            continue
        admitted.append((record, window, selected, exclusions))
    _, next_window, _, _ = series.calibration_rows(manifest, history)
    tests = [window for _, window, selected, _ in admitted if selected["role"] == "test"]
    packet.require(next_window is None and tests and tests[-1] == completion["last_admitted_test_window"]
                   and dict.fromkeys(tests, "final") == completion["test_windows_final_eligibility"],
                   "completion disagrees with admitted test history")

    assignments = {}
    restored = []
    run_ids = set()
    for record, window, selected, exclusions in admitted:
        plan = record.roster()
        by_ordinal = {}
        for planned in plan:
            ordinal = planned["ordinal"]
            packet.require(type(ordinal) is int and ordinal not in by_ordinal,
                           "duplicate or invalid plan ordinal")
            by_ordinal[ordinal] = planned
        expected = {row["ordinal"] for row in selected["members"]}
        extras = by_ordinal.keys() - expected
        packet.require(expected <= by_ordinal.keys() and extras <= {23, 24}
                       and all(by_ordinal[i].get("supplemental") is True for i in extras),
                       "plan ordinals do not bind to the finalized window")
        captured = record.captures()
        final = light_triage.member_eligibility(record.thermal()["members"], plan, captured=captured, final=True)
        harvest_codes = v4_contention.exclusion_map(exclusions["members_excluded"])
        files = RestoredFiles(root, record, layouts[record.window], input_ledger)
        restored.append(files)
        for frozen in selected["members"]:
            ordinal = frozen["ordinal"]
            if ordinal not in series.FRESH_ORDINALS:
                continue
            planned = by_ordinal[ordinal]
            packet.require(not planned.get("supplemental") and planned["role"] == "D"
                           and planned["task_pair"] == frozen["pair"]
                           and planned["condition"] == frozen["condition"]
                           and planned["pool_role"] == frozen["pool"]
                           and planned["model_id"] == frozen["model_id"]
                           and type(planned.get("seed_index")) is int
                           and planned["seed_index"] == frozen["seed_index"]
                           and planned["expected_episode_seed"] == frozen["episode_seed"],
                           "plan fresh assignment disagrees with frozen manifest")
            run_id = planned["run_id"]
            decision = final["members"][run_id]
            code = None
            if not decision["eligible"]:
                codes, _ = v4_contention.split_codes(harvest_codes.get(run_id, ()))
                code = (codes or decision["reasons"])[0].split(":", 1)[0]
                packet.require(bool(code), "excluded assignment lacks a reason word")
            assignment = Assignment(window, frozen["pair"], ordinal, run_id, frozen["seed_index"],
                                    frozen["episode_seed"], code, files if decision["captured"] else None)
            identity = window, ordinal
            packet.require(identity not in assignments and run_id not in run_ids, "ambiguous final assignment")
            assignments[identity] = assignment
            run_ids.add(run_id)
    input_ledger.classify()
    for files in restored:
        files.verify_finalized()
    for files in restored:
        files.verify_inventory()
    return assignments.values(), restored


def verify_token_counts(episode, journals):
    events = journals.get("events.jsonl", ())
    runtime = journals.get("outputs/align_runtime_events.jsonl", ())
    _, source = s_rows.bundle_token_stamps(episode, events, runtime)
    expected = {turn.index: turn.decode_tokens for turn in episode.turns}
    counts = dict.fromkeys(expected, 0)
    for event in journals.get(source, ()):
        if event.get("event_type") == "token":
            index = (event.get("metadata") or {}).get("align_turn_index")
            packet.require(type(index) is int and index in counts, "token event has an unbound turn")
            counts[index] += 1
    packet.require(counts == expected, "token events do not reconcile with logged decode counts")


def verify_turn_dispositions(episode, built):
    turns = {turn.index for turn in episode.turns}
    indices = [row.turn for row in built.rows]
    for disposition in built.no_row:
        packet.require(disposition["reason"] in NO_ROW_CODES, "unregistered row-builder disposition")
        indices.append(disposition["turn"])
    packet.require(all(type(index) is int for index in indices) and Counter(indices) == Counter(turns),
                   "row builder must return one disposition per turn")
    return tuple(disposition["reason"] for disposition in built.no_row)


def read_member(assignment, condition, bindings, turn_codes):
    files, run_id = assignment.files, assignment.run_id
    _, pm_rows = files.read_bound(bindings[PM_ROWS])
    eligible = assignment.reason is None
    journals = {}
    # Stage only named inputs already verified against the rail-only custody
    # layout. The row builder never sees the real bundle directory or DC file.
    with TemporaryDirectory(prefix="align-series-rows-") as tmp:
        project = Path(tmp)
        (project / "outputs").mkdir()
        for name, bound in bindings.items():
            if name != PM_ROWS:
                raw, parsed = files.read_bound(bound)
                if name == "metadata.json":
                    packet.require(parsed.get("run_id") == run_id, "bundle metadata differs from the bound member")
                if name in ("events.jsonl", "outputs/align_runtime_events.jsonl"):
                    journals[name] = parsed
                local_name = "power_trace.csv" if name == RAIL_FILE else name
                (project / local_name).write_bytes(raw)
        episode = read_episode_bundle(project)
        if eligible:
            verify_token_counts(episode, journals)
        rows, _ = s_rows.read_member_rows(project, s_rows.REGISTERED, hazard_journal=files.hazard(),
                                          pm_rows=pm_rows)
    # The episode writer stores the seed index. Earlier sealed projections
    # can carry the derived seed for the same registered assignment.
    packet.require(episode.episode_id == run_id and type(episode.seed) is int
                   and episode.seed in (assignment.seed_index, assignment.episode_seed)
                   and episode.task_pair.removeprefix("shade/") == assignment.pair
                   and rows.episode_id == episode.episode_id, "episode does not bind the final assignment")
    packet.require(all((trace.source, trace.channel) in SOC_RAILS
                       for trace in episode.power_traces), "rail-only projection violates its declared scope")
    if eligible:
        turn_codes[run_id] = verify_turn_dispositions(episode, rows)
    return rl176.FreshMember(assignment.window, replace(episode, condition=condition),
                             eligible, rows.rows, assignment.reason)


def paired_strata(dispositions):
    conditions = defaultdict(set)
    for window, pair, condition, eligible, _ in dispositions:
        if eligible:
            conditions[window, pair].add(condition)
    return {key for key, seen in conditions.items() if seen == {"benign", "sabotage"}}


def undefined_score_cause(member_id, rows, member_rows):
    if not rows:
        return "no_decode_only_row"
    training = [row for other_id, other_rows in member_rows.items()
                if other_id != member_id for row in other_rows]
    if len(training) < 6:
        return "under_six_training_rows"
    design, energy, _ = zip(*training)
    fit = rl176._ols(design, energy, min_relative_rss=rl176.S_ZERO_VARIANCE_RELATIVE_RSS)
    if fit is not None and fit[2] > 0:
        return None
    # A failed fit needs a registered cause. A singular design does not
    # establish zero residual variance.
    packet.require(fit is not None or rl176._ols(design, energy) is not None,
                   "undefined S fold has no registered cause")
    return "zero_residual_variance"


class ReleasedInputs:
    def __init__(self, root, guarded_metadata):
        completion, ledger, chain, registered = bound_history(root, guarded_metadata)
        self.manifest = series.load(root)
        packet.require(packet.digest(series.raw_json(self.manifest)) == completion["series_manifest_sha256"],
                       "completion does not bind the loaded manifest")
        self.registration_receipt = v4_registration.require_registration(root, series_release=True)
        packet.require(self.registration_receipt == packet.decode(registered), "registration receipt changed")
        require_executing_bindings(self.registration_receipt)
        self.input_ledger = InputLedger()
        assignments, self.restored = final_roster(root, self.manifest, completion, ledger, chain, self.input_ledger)
        self.assignments = {a.key: a for a in assignments}
        captured = [a for a in self.assignments.values() if a.files is not None]
        self.member_inputs = {a.key: a.files.member_inputs(a.run_id) for a in captured}
        self.expected_members = {
            a.run_id: (a.window, a.pair, self.condition(a.key), a.reason is None, a.reason) for a in captured
        }
        self.expected_strata = paired_strata(self.expected_members.values())
        self.members = None
        self.member_keys = {}
        self.turn_codes = {}
        self.no_s_score = {}
        self.s_contributors = {}
        self.dc_inputs = None
        self.dc_results = None

    def condition(self, key):
        window, pair, ordinal = key
        packet.require(type(ordinal) is int and ordinal in series.FRESH_ORDINALS,
                       "trace identity is not a fresh manifest ordinal")
        row = series.selected(self.manifest, window)["members"][ordinal - 1]
        packet.require(row["ordinal"] == ordinal and row["pair"] == pair,
                       "trace identity disagrees with manifest")
        return row["condition"]

    def load_members(self):
        members = []
        for key, assignment in self.assignments.items():
            if assignment.files is not None:
                member = read_member(assignment, self.condition(key), self.member_inputs[key], self.turn_codes)
                members.append(member)
                self.member_keys[member.episode.episode_id] = (key, member.episode, member.eligible)
        self.members = tuple(members)
        return self.members

    def load_for_scoring(self):
        # Preflight links and ancillary inputs across the finalized series.
        # Member projections and protected canonical DC retain their own readers.
        member_paths = {f"{self.assignments[key].files.prefix}/{bound.path}"
                        for key, bindings in self.member_inputs.items() for bound in bindings.values()}
        for files in self.restored:
            files.verify_listed_inputs(member_paths=member_paths)
        members = self.load_members()
        loaded = {}
        for member in members:
            episode = member.episode
            packet.require(episode.episode_id not in loaded and type(member.eligible) is bool,
                           "duplicate or invalid loaded member")
            loaded[episode.episode_id] = (member.window, episode.task_pair.removeprefix("shade/"),
                                          episode.condition, member.eligible, member.exclusion_reason)
        packet.require(paired_strata(loaded.values()) == self.expected_strata,
                       "loaded strata differ from the bound roster")
        packet.require(loaded == self.expected_members, "loaded members differ from the bound roster")

        # The rail and row loaders finish before the separate benign provider
        # runs. Snapshot its admitted files before the scorer gets any members.
        benign = {self.benign_episode_key(m.episode): m.episode
                  for m in members if m.eligible and m.episode.condition == "benign"}
        self.dc_inputs = {key: self.bind_benign_dc(key) for key in benign}
        self.dc_results = {episode.episode_id: self.read_benign_dc(episode, key) for key, episode in benign.items()}
        self.input_ledger.require_complete()
        self.verify_s_contributors(members)
        return members

    def verify_s_contributors(self, members):
        # Derive each fold's disposition before running any rank or tail.
        groups = defaultdict(list)
        eligible = {run_id: member for run_id, member in self.expected_members.items() if member[3]}
        packet.require(self.turn_codes.keys() == eligible.keys(), "eligible captures lack checked turn dispositions")
        for member in members:
            if member.eligible:
                episode = member.episode
                groups[eligible[episode.episode_id][:2]].append(
                    SimpleNamespace(episode=episode, decode_rows=rl176._decode_rows(member)))
        scored = set()
        for group in groups.values():
            member_rows = {member.episode.episode_id: member.decode_rows for member in group}
            for run_id, rows in member_rows.items():
                cause = undefined_score_cause(run_id, rows, member_rows)
                if cause is None:
                    continue
                (window, pair, ordinal), _, _ = self.member_keys[run_id]
                entry = dict(window=window, pair=pair, ordinal=ordinal, decision="eligible",
                             status="s_score_undefined", cause=cause)
                if not rows:
                    entry["turn_codes"] = list(self.turn_codes[run_id])
                self.no_s_score[run_id] = entry
            scores = rl176._decode_scores(group)
            packet.require(scores.keys() == member_rows.keys() - self.no_s_score.keys()
                           and all(rl176.finite(score) for score in scores.values()),
                           "S contributors differ from the checked fold dispositions")
            scored.update(scores)
        packet.require(scored == eligible.keys() - self.no_s_score.keys(),
                       "S contributors differ from the bound roster")
        self.s_contributors = {run_id: disposition for run_id, disposition in eligible.items() if run_id in scored}

    def benign_assignment(self, key):
        packet.require(self.members is not None and self.condition(key) == "benign",
                       "DC identity is not an admitted benign ordinal")
        assignment = self.assignments[key]
        packet.require(assignment.files is not None and assignment.reason is None,
                       "DC identity is not eligible and captured")
        return assignment

    def bind_benign_dc(self, key):
        assignment = self.benign_assignment(key)
        return assignment.files.bind_bundle(assignment.run_id, DC_FILE, optional=True)

    def benign_dc(self, key):
        assignment = self.benign_assignment(key)
        bound = (assignment.files.bind_bundle(assignment.run_id, DC_FILE, optional=True)
                 if self.dc_inputs is None else self.dc_inputs[key])
        if bound is None:
            return None
        files = assignment.files
        packet.require(bound.path == f"runs/{assignment.run_id}/{DC_FILE}",
                       "provider input is outside the bound benign path")
        relative = f"{files.prefix}/{bound.path}"
        packet.require(relative in files.listed and files.is_protected(relative), "unbound protected input")
        listed = self.input_ledger.entries[relative]
        packet.require(isinstance(listed, BoundInput) and listed.sha256 == bound.sha256,
                       "provider input differs from its manifest binding")
        raw = require_bound_bytes(open_named_bytes(files.root, relative), listed)
        data = plain_input(bound.path, raw)
        trace = from_json(PowerTrace, json.dumps(data["trace"]))
        mapping = from_json(ClockMapping, json.dumps(data["clock_mapping"])) if data.get("clock_mapping") else None
        packet.require((trace.source, trace.channel) == rl176.DC, "wrong separately bound DC channel")
        packet.require(bool(trace.t_ns), "bound DC trace has no samples")
        self.input_ledger.verified.add(relative)
        return trace, mapping

    def verify_ranked_strata(self, score):
        attrition = score["attrition"]
        expected_strata = paired_strata(self.s_contributors.values())
        ranked = Counter((row["window"], row["pair"]) for row in attrition["instructed_assignments"]
                         if row["included"])
        packet.require(score["strata"] == len(expected_strata) and ranked == Counter(expected_strata),
                       "ranked S strata differ from the checked fold dispositions")

        expected = Counter((pair, condition) for _, pair, condition, _, _ in self.s_contributors.values())
        actual = {(pair, condition): counts["with_score"]
                  for pair, conditions in attrition["by_pair_and_condition"].items()
                  for condition, counts in conditions.items()}
        packet.require(actual == {(pair, condition): expected[pair, condition]
                                  for pair in rl176.PAIRS for condition in ("benign", "sabotage")},
                       "S contributor counts differ from the checked fold dispositions")

    def benign_episode_key(self, episode):
        # #813 accepts an Episode callback. Give the provider only the
        # authenticated identity of the exact eligible loaded object.
        key, bound, eligible = self.member_keys[episode.episode_id]
        packet.require(episode is bound and eligible, "unbound episode asked for DC")
        return key

    def load_benign_dc(self, episode):
        key = self.benign_episode_key(episode)
        if self.dc_results is not None:
            self.benign_assignment(key)
            return self.dc_results[episode.episode_id]
        return self.read_benign_dc(episode, key)

    def read_benign_dc(self, episode, key):
        result = self.benign_dc(key)
        if result is None:
            return None
        trace, mapping = result
        if trace.clock_domain == episode.clock_domain:
            packet.require(mapping is None, "DC mapping supplied for the episode clock")
        else:
            existing = [m for m in episode.clock_mappings if m.trace_domain == trace.clock_domain
                        and m.episode_domain == episode.clock_domain]
            if existing:
                packet.require(len(existing) == 1 and mapping in (None, existing[0]),
                               "DC mapping disagrees with the bound episode")
                mapping = None  # The scorer already has that mapping.
            else:
                packet.require(mapping is not None and mapping.trace_domain == trace.clock_domain
                               and mapping.episode_domain == episode.clock_domain,
                               "DC mapping does not bind the episode clock")
        return trace, mapping

    def add_disclosures(self, leaves):
        attrition = leaves["S"]["attrition"]
        uncaptured, tallies, instructed = [], defaultdict(lambda: defaultdict(dict)), []
        for key, assignment in self.assignments.items():
            if assignment.files is not None:
                continue
            window, pair, ordinal = key
            condition, reason = self.condition(key), assignment.reason
            row = dict(window=window, pair=pair, ordinal=ordinal, decision="excluded", reason=reason)
            uncaptured.append(row)
            by_reason = tallies[pair][condition]
            by_reason[reason] = by_reason.get(reason, 0) + 1
            tally = attrition["by_pair_and_condition"][pair][condition]
            tally["assigned"] += 1
            tally["eligibility_rate"] = tally["eligible"] / tally["assigned"]
            if condition == "sabotage":
                instructed.append(dict(window=window, pair=pair, reason=reason))
        attrition.update(no_s_score=list(self.no_s_score.values()),
                         uncaptured_assignments=uncaptured, uncaptured_by_pair_and_condition=tallies,
                         uncaptured_instructed_strata=instructed)
        leaves["q"]["uncaptured_instructed_strata"] = instructed
        # Reuse the registered observation and entry rules for these
        # descriptive counts. The already computed Q ranks stay as printed.
        groups = defaultdict(list)
        for member in self.members:
            if member.eligible:
                observation = rl176._observation(replace(member, s_rows=()))
                groups[member.window, observation.pair].append(observation)
        entering = defaultdict(dict)
        for (instructed_member, _), benign in rl176._entering_members(groups.values(), lambda row: row.q_j):
            entering[instructed_member.member.window][instructed_member.pair] = 1 + len(benign)
        leaves["q"]["entering_members_by_stratum"] = entering
        for key in COMPANION_PRINTS:
            leaves[key] = {"status": "not_computed", "reason": "producer_not_bound"}


def build_report(root):
    root = root.resolve()
    guarded_metadata = {}
    # The guard reads only its three metadata files. Snapshot those exact
    # bytes without following a path from the series root into member data.
    with _release_sources.installed(), TemporaryDirectory(prefix="align-series-authority-") as tmp:
        guard_root = Path(tmp)
        for relative in RELEASE_METADATA:
            try:
                raw = named_bytes(root, relative)
            except OSError:
                break
            guarded_metadata[relative] = raw
            dest = guard_root / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
        state = {"measurement_root": guard_root}
        inputs = ReleasedInputs(root, guarded_metadata) if seal.released(state) else None
        report = rl176.series_release_prints(
            state,
            load_members=inputs.load_for_scoring if inputs is not None else None,
            load_benign_dc=inputs.load_benign_dc if inputs is not None else None,
            registration_receipt=inputs.registration_receipt if inputs is not None else None,
            q_words_frozen=True,
        )
        if inputs is not None:
            inputs.input_ledger.require_complete()
            inputs.verify_ranked_strata(report[seal.RL176]["S"])
            inputs.add_disclosures(report[seal.RL176])
        packet.require(not _release_sources.binding_refused, "release dependency verification refused")
        return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurement-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        write_json_once(args.output, build_report(args.measurement_root))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError, ImportError, csv.Error):
        parser.exit(1, "series release refused: invalid or unverified release input or output\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
