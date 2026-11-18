#!/usr/bin/env python3
"""Release the registered ALIGN v4 series from finalized, admitted records."""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass, replace
from importlib.machinery import SourceFileLoader
from importlib.util import spec_from_file_location
import json
import os
from pathlib import Path
from stat import S_ISREG
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
_CALLER_CODE = sys._getframe().f_code
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from joulewise.align.apple import v4_registration


class ReleaseSourceLoader(SourceFileLoader):
    """Keep the digest of the source bytes used to create the loaded code."""

    def get_code(self, fullname):
        source = self.get_data(self.path)
        self.source_digest = v4_registration.digest(source)
        return self.source_to_code(source, self.path)


class ReleaseSourceFinder:
    paths = {
        path.removesuffix(".py").replace("/", "."): path
        for path in v4_registration.SERIES_RELEASE_ARTIFACTS
        if path.startswith("joulewise/")
    }

    def find_spec(self, fullname, path=None, target=None):
        if fullname in self.paths:
            origin = str(ROOT / self.paths[fullname])
            return spec_from_file_location(fullname, origin, loader=ReleaseSourceLoader(fullname, origin))
        return None


# A release subprocess imports these three pinned modules from source.
# A stale Python bytecode cache must never stand in for the receipt's bytes.
_release_finder = ReleaseSourceFinder()
sys.meta_path.insert(0, _release_finder)
try:
    from joulewise.align.apple import rl176, rl176_phases, s_rows
finally:
    sys.meta_path.remove(_release_finder)
    del _release_finder

from joulewise.align.apple import harvest_offload, light_triage, v4_contention, v4_desk_seal as seal
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


def named_bytes(root, relative):
    """Open exactly one regular file below a real root, with no symlink hops."""
    parts = Path(relative).parts
    packet.require(parts and not Path(relative).is_absolute()
                   and all(part not in (".", "..") for part in parts)
                   and Path(*parts).as_posix() == relative, "unsafe release input path")
    directory_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY
    directory = os.open(root, directory_flags)
    try:
        for part in parts[:-1]:
            child = os.open(part, directory_flags, dir_fd=directory)
            os.close(directory)
            directory = child
        file_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
        with os.fdopen(os.open(parts[-1], file_flags, dir_fd=directory), "rb") as source:
            packet.require(S_ISREG(os.fstat(source.fileno()).st_mode), "non-regular release input")
            return source.read()
    finally:
        os.close(directory)


def require_executing_bindings(receipt):
    origins = {
        "scripts/align_v4_series_release.py": Path(__file__),
        **{ReleaseSourceFinder.paths[module.__name__]: Path(module.__file__)
           for module in (s_rows, rl176, rl176_phases)},
    }
    for relative in v4_registration.SERIES_RELEASE_ARTIFACTS:
        packet.require(origins[relative].resolve() == ROOT / relative,
                       "release source was loaded from another checkout")
        expected = receipt["artifacts"][relative]
        raw = named_bytes(ROOT, relative)
        packet.require(packet.digest(raw) == expected, "executing release source differs from the receipt")
        if relative == "scripts/align_v4_series_release.py":
            code = compile(raw, _CALLER_CODE.co_filename, "exec", dont_inherit=True)
            packet.require(code == _CALLER_CODE, "loaded release caller differs from the receipt")
    for module in (s_rows, rl176, rl176_phases):
        loader = module.__loader__
        if isinstance(loader, ReleaseSourceLoader):
            relative = ReleaseSourceFinder.paths[module.__name__]
            packet.require(loader.source_digest == receipt["artifacts"][relative],
                           "loaded release source differs from the receipt")
        elif __name__ == "__main__":
            raise ValueError("release module was loaded outside the source loader")


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
    registration_bytes = evidence.read(tip, REGISTRATION_RECEIPT)
    packet.require(named_bytes(root, REGISTRATION_RECEIPT) == registration_bytes,
                   "registration receipt differs from committed authority")
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
        self.hazard_journal = layout["hazard_journal"]
        if self.hazard_journal is not None:
            packet.require(self.hazard_journal == "archive/align_s_hazard.jsonl",
                           "unexpected supplemental cut source")
        self._hazard = None

    def read(self, name, *, optional=False):
        if optional and name not in self.entries:
            return None
        row = self.entries[name]
        packet.require(set(row) == {"size", "sha256"}, "release input is not a bound regular file")
        raw = named_bytes(self.root, f"{self.prefix}/{name}")
        packet.require(len(raw) == row["size"] and packet.digest(raw) == row["sha256"],
                       "restored file differs from record manifest")
        return raw

    def bundle(self, run_id, name, *, optional=False):
        packet.require(Path(run_id).name == run_id and run_id not in ("", ".", ".."),
                       "unsafe run identity")
        return self.read(f"runs/{run_id}/{name}", optional=optional)

    def hazard(self):
        if self._hazard is None:
            self._hazard = (() if self.hazard_journal is None else
                            tuple(packet.decode(line) for line in self.read(self.hazard_journal).splitlines()
                                  if line.strip()))
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


def read_member(assignment, condition):
    files, run_id = assignment.files, assignment.run_id
    pm_rows = packet.decode(files.bundle(run_id, PM_ROWS))
    # Stage only named inputs already verified against the rail-only custody
    # layout. The row builder never sees the real bundle directory or DC file.
    with TemporaryDirectory(prefix="align-series-rows-") as tmp:
        project = Path(tmp)
        (project / "outputs").mkdir()
        for name in REQUIRED_BUNDLE_FILES + OPTIONAL_BUNDLE_FILES:
            raw = files.bundle(run_id, name, optional=name in OPTIONAL_BUNDLE_FILES)
            if raw is not None:
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
        self.members = None
        self.member_keys = {}

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
                member = read_member(assignment, self.condition(key))
                members.append(member)
                self.member_keys[member.episode.episode_id] = (key, member.episode, member.eligible)
        self.members = tuple(members)
        return self.members

    def benign_dc(self, key):
        packet.require(self.members is not None and self.condition(key) == "benign",
                       "DC identity is not an admitted benign ordinal")
        assignment = self.assignments[key]
        packet.require(assignment.files is not None and assignment.reason is None,
                       "DC identity is not eligible and captured")
        raw = assignment.files.bundle(assignment.run_id, DC_FILE, optional=True)
        if raw is None:
            return None
        data = packet.decode(raw)
        trace = from_json(PowerTrace, json.dumps(data["trace"]))
        mapping = from_json(ClockMapping, json.dumps(data["clock_mapping"])) if data.get("clock_mapping") else None
        packet.require((trace.source, trace.channel) == rl176.DC, "wrong separately bound DC channel")
        return trace, mapping

    def load_benign_dc(self, episode):
        # #813 accepts an Episode callback. Give the provider only the
        # authenticated identity of the exact eligible loaded object.
        key, bound, eligible = self.member_keys[episode.episode_id]
        packet.require(episode is bound and eligible, "unbound episode asked for DC")
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
    with TemporaryDirectory(prefix="align-series-authority-") as tmp:
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
            load_members=inputs.load_members if inputs is not None else None,
            load_benign_dc=inputs.load_benign_dc if inputs is not None else None,
            registration_receipt=inputs.registration_receipt if inputs is not None else None,
            q_words_frozen=True,
        )
        if inputs is not None:
            inputs.add_disclosures(report[seal.RL176])
        return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--measurement-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        write_json_once(args.output, build_report(args.measurement_root))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, IndexError):
        parser.exit(1, "series release refused: invalid or unverified release input or output\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
