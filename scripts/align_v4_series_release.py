#!/usr/bin/env python3
"""Release the registered ALIGN v4 series from finalized, admitted records."""
from __future__ import annotations

import argparse
from collections import defaultdict
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
    from joulewise.align.apple import harvest_offload, light_triage, rl176, s_rows
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
COMPANION_PRINTS = ("S_a4", "S_w", "benign_slopes")
SOC_RAILS = frozenset(("powermetrics", name) for name in ("cpu_power", "gpu_power", "ane_power"))
RAIL_COLUMNS = {"timestamp_s", "power_w", "source", "rail"}
RAIL_INTERVAL_COLUMNS = {"interval_start_s", "interval_end_s"}


def input_parts(relative):
    parts = Path(relative).parts
    packet.require(parts and not Path(relative).is_absolute()
                   and all(part not in (".", "..") for part in parts)
                   and Path(*parts).as_posix() == relative, "unsafe release input path")
    return parts


def named_bytes(root, relative):
    """Open exactly one readable, unlinked regular file below a real root."""
    parts = input_parts(relative)
    directory_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
    directory = os.open(root, directory_flags)
    try:
        for part in parts[:-1]:
            child = os.open(part, directory_flags, dir_fd=directory)
            os.close(directory)
            directory = child
        file_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        with os.fdopen(os.open(parts[-1], file_flags, dir_fd=directory), "rb") as source:
            info = os.fstat(source.fileno())
            packet.require(S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_mode & 0o444,
                           "unreadable or linked release input")
            return source.read()
    finally:
        os.close(directory)


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
        raw = named_bytes(ROOT, relative)
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
    seed: int
    reason: str | None
    files: RestoredFiles | None

    @property
    def key(self):
        return self.window, self.pair, self.ordinal


@dataclass(frozen=True)
class BoundInput:
    path: str
    size: int
    sha256: str


def plain_input(name, raw):
    """Accept the registered plain grammars at their canonical paths."""
    text = raw.decode("utf-8")
    if name.endswith(".jsonl"):
        rows = tuple(packet.decode(line) for line in raw.splitlines() if line.strip())
        packet.require(all(isinstance(row, dict) for row in rows), "release journal must contain objects")
        return rows
    if name.endswith(".json"):
        value = packet.decode(text)
        required = list if name.endswith("/" + PM_ROWS) else dict
        packet.require(isinstance(value, required), "release JSON has the wrong shape")
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
    def __init__(self, root, record, layout):
        packet.require(layout["trace_layout"] == LAYOUT, "no admitted rail-only file layout")
        self.root = root
        self.prefix = f"series/restored/{record.window}"
        raw = named_bytes(root, f"{self.prefix}/finalized_manifest.json")
        packet.require(packet.digest(raw) == record.finalized_manifest_sha256,
                       "restored manifest differs from record digest")
        manifest = packet.decode(raw)
        harvest_offload._validate_finalized(manifest)
        self.entries = manifest["entries"]
        self.stems = defaultdict(set)
        for name in self.entries:
            input_parts(name)
            self.stems[self.stem(name)].add(name)
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
        return parent, filename.partition(".")[0]

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
        raw = named_bytes(self.root, f"{self.prefix}/{bound.path}")
        packet.require(len(raw) == bound.size and packet.digest(raw) == bound.sha256,
                       "restored file differs from record manifest")
        return raw, plain_input(bound.path, raw)

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


def final_roster(root, manifest, completion, ledger, chain):
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
        files = RestoredFiles(root, record, layouts[record.window])
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
                           and planned["expected_episode_seed"] == frozen["episode_seed"],
                           "plan fresh assignment disagrees with frozen manifest")
            run_id = planned["run_id"]
            decision = final["members"][run_id]
            code = None
            if not decision["eligible"]:
                codes, _ = v4_contention.split_codes(harvest_codes.get(run_id, ()))
                code = (codes or decision["reasons"])[0].split(":", 1)[0]
                packet.require(bool(code), "excluded assignment lacks a reason word")
            assignment = Assignment(window, frozen["pair"], ordinal, run_id, frozen["episode_seed"],
                                    code, files if decision["captured"] else None)
            identity = window, ordinal
            packet.require(identity not in assignments and run_id not in run_ids, "ambiguous final assignment")
            assignments[identity] = assignment
            run_ids.add(run_id)
    return assignments.values()


def read_member(assignment, condition, bindings):
    files, run_id = assignment.files, assignment.run_id
    _, pm_rows = files.read_bound(bindings[PM_ROWS])
    # Stage only named inputs already verified against the rail-only custody
    # layout. The row builder never sees the real bundle directory or DC file.
    with TemporaryDirectory(prefix="align-series-rows-") as tmp:
        project = Path(tmp)
        (project / "outputs").mkdir()
        for name, bound in bindings.items():
            if name != PM_ROWS:
                raw, _ = files.read_bound(bound)
                local_name = "power_trace.csv" if name == RAIL_FILE else name
                (project / local_name).write_bytes(raw)
        episode = read_episode_bundle(project)
        rows, _ = s_rows.read_member_rows(project, s_rows.REGISTERED, hazard_journal=files.hazard(),
                                          pm_rows=pm_rows)
    packet.require(episode.episode_id == run_id and episode.seed == assignment.seed
                   and episode.task_pair.removeprefix("shade/") == assignment.pair
                   and rows.episode_id == episode.episode_id, "episode does not bind the final assignment")
    packet.require(all((trace.source, trace.channel) in SOC_RAILS
                       for trace in episode.power_traces), "rail-only projection violates its declared scope")
    return rl176.FreshMember(assignment.window, replace(episode, condition=condition),
                             assignment.reason is None, rows.rows, assignment.reason)


def paired_strata(dispositions):
    conditions = defaultdict(set)
    for window, pair, condition, eligible, _ in dispositions:
        if eligible:
            conditions[window, pair].add(condition)
    return {key for key, seen in conditions.items() if seen == {"benign", "sabotage"}}


class ReleasedInputs:
    def __init__(self, root, guarded_metadata):
        completion, ledger, chain, registered = bound_history(root, guarded_metadata)
        self.manifest = series.load(root)
        packet.require(packet.digest(series.raw_json(self.manifest)) == completion["series_manifest_sha256"],
                       "completion does not bind the loaded manifest")
        self.registration_receipt = v4_registration.require_registration(root, series_release=True)
        packet.require(self.registration_receipt == packet.decode(registered), "registration receipt changed")
        require_executing_bindings(self.registration_receipt)
        self.assignments = {a.key: a for a in final_roster(root, self.manifest, completion, ledger, chain)}
        captured = [a for a in self.assignments.values() if a.files is not None]
        self.member_inputs = {a.key: a.files.member_inputs(a.run_id) for a in captured}
        self.expected_members = {
            a.run_id: (a.window, a.pair, self.condition(a.key), a.reason is None, a.reason) for a in captured
        }
        self.expected_strata = paired_strata(self.expected_members.values())
        self.members = None
        self.member_keys = {}
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
                member = read_member(assignment, self.condition(key), self.member_inputs[key])
                members.append(member)
                self.member_keys[member.episode.episode_id] = (key, member.episode, member.eligible)
        self.members = tuple(members)
        return self.members

    def load_for_scoring(self):
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
        return members

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
        _, data = assignment.files.read_bound(bound)
        trace = from_json(PowerTrace, json.dumps(data["trace"]))
        mapping = from_json(ClockMapping, json.dumps(data["clock_mapping"])) if data.get("clock_mapping") else None
        packet.require((trace.source, trace.channel) == rl176.DC, "wrong separately bound DC channel")
        return trace, mapping

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
        attrition.update(uncaptured_assignments=uncaptured, uncaptured_by_pair_and_condition=tallies,
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
