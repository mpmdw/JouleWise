"""Independent C1 v3.1 acceptance. Only private TemporaryDirectory Git worlds are accepted.

Run under unittest with the composed public source checkout on PYTHONPATH. The
child executes the production file as __main__ without importing the fixtures.
C1_V3_EVIDENCE optionally names a directory for per-case synthetic observations.
"""
import collections
from contextlib import contextmanager
from dataclasses import dataclass, replace
from fractions import Fraction
import hashlib
import json
import math
import os
import re
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


META = tuple("configs/campaigns/align_v4/series/" + stem + ".json"
             for stem in ("series_complete", "series_manifest", "release_receipt"))
WITHHELD = {"rl176": dict.fromkeys(("S", "S_pf", "q", "aligned_power"), "withheld_until_series_complete")}
WINDOWS = tuple(f"C{i}" for i in range(1, 9)) + ("T1", "T2", "T3")
PAIR = "bank_transfer_2"
ROLE = {"benign": 7, "instructed": 19}
DC = "outputs/align_dc_in.json"
TOKEN = b"invented violet\n"
SCRIPT = "align_v4_series_release.py"
WATCH = {
    SCRIPT: {"verify_inventory", "read_member", "load_members", "bind_benign_dc", "benign_dc",
             "verify_listed_inputs", "require_complete", "bind_bundle", "read_bound"},
    "harvest_offload.py": {"_verify_closure", "checkout_identity"},
    "workload.py": {"read_episode_bundle"},
    "light_triage.py": {"member_eligibility"},
    "s_rows.py": {"read_member_rows"},
    "rl176.py": {"_series_prints", "_s_rank", "_tail_test", "_decode_scores", "_entering_members"},
    "harvest.py": {"write_json_once"},
}
WATCH_NAMES = set().union(*WATCH.values())


def cli_witness(script, root, output, config, witness):
    """Passive call observer plus a fail-closed tripwire on actual fixture opens."""
    policy = json.loads(Path(config).read_text())
    events, groups, denied, dc, validators = [], [], [], [], []
    protected = set(policy["protected"])
    blessed = set(policy["allowed_dc"])
    instructed = set(policy["instructed"])
    prefix = root + "/"
    counts = collections.Counter()
    fd_paths = {}
    real_open, real_close = os.open, os.close
    open_depth = 0
    lookup_errors = []
    decisions = []
    projected = []
    deferrals = {}
    observer_errors = []

    def record(name, detail=None):
        counts[name] += 1
        events.append((name, detail))

    def frames(frame):
        while frame:
            yield frame
            frame = frame.f_back

    def check(path, flags):
        path = os.path.abspath(path)
        if path == output and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT):
            record("output_open")
        if not path.startswith(prefix):
            return
        rel = path[len(prefix):]
        if flags & os.O_DIRECTORY:
            return
        # Check both the spelled and terminal names for synthetic aliases.
        terminal = os.path.relpath(os.path.realpath(path), root)
        if policy["prefix"] and rel not in META:
            denied.append(rel)
        elif (rel in protected or terminal in protected or rel.endswith("/" + DC)
              or "/hazards/meter/" in "/" + rel or "/dc_in/" in "/" + rel):
            if rel in blessed and terminal == rel and any(
                    f.f_code.co_name == "benign_dc" and f.f_code.co_filename == script
                    for f in frames(sys._getframe(1))):
                dc.append(rel)
                record("authorized_open", rel)
                return
            denied.append(rel)
        else:
            return
        raise AssertionError("forbidden synthetic read: " + rel)

    def open_at(path, flags, mode=0o777, *, dir_fd=None):
        nonlocal open_depth
        base = fd_paths[dir_fd] if dir_fd is not None else os.getcwd()
        name = os.path.abspath(os.path.join(base, os.fsdecode(path)))
        check(name, flags)
        open_depth += 1
        try:
            fd = real_open(path, flags, mode, dir_fd=dir_fd)
        finally:
            open_depth -= 1
        fd_paths[fd] = name
        return fd

    def close(fd):
        fd_paths.pop(fd, None)
        return real_close(fd)

    def audit(event, args):
        if event == "open" and not open_depth and isinstance(args[0], (str, bytes)):
            check(os.fsdecode(args[0]), args[2])
        if event == "subprocess.Popen":
            argv = [os.fsdecode(x) for x in args[1]]
            if policy["prefix"]:
                denied.append("prefix subprocess")
                raise AssertionError("withheld CLI launched a child")
            if policy["protected_mirror"] and str(Path(root) / "toy-checkout") in argv and (
                    any(x in argv for x in ("status", "diff", "diff-files", "hash-object"))
                    or any("/dc_in/" in "/" + x for x in argv if ":" in x)):
                denied.append("Git would inspect tracked protected input")
                raise AssertionError(denied[-1])

    def profile(frame, event, value):
        name = frame.f_code.co_name
        if name not in WATCH_NAMES or event not in ("call", "return"):
            return
        source = frame.f_code.co_filename.rsplit("/", 1)[-1]
        if name not in WATCH.get(source, ()):
            return
        data = frame.f_locals
        if name == "_entering_members":
            if event == "return" and value is not None and any(
                    f.f_code.co_name == "splits" and f.f_locals.get("decide")
                    for f in frames(frame.f_back)):
                first, others = value
                groups.append([m.episode.episode_id for m, _ in [first, *others]])
            return
        if name == "member_eligibility":
            if event == "return" and value and value.get("stage") == "final":
                focus = policy["target_run"]
                if focus in value["members"]:
                    decisions.append(value["members"][focus])
            return
        if event == "return":
            if name == "read_member" and value and value.episode.episode_id == policy["target_run"]:
                projected.append({"eligible": value.eligible, "rows": len(value.s_rows),
                                  "condition": value.episode.condition})
            if name in ("load_members", "require_complete"):
                record(name + "_return")
            return
        detail = None
        if name == "_verify_closure":
            detail = Path(data["root"]).name
            validators.append([detail, digest(data["closure"])])
            deferrals[detail] = sorted(os.path.relpath(path, root) for path in data["transported"])
        elif name == "_s_rank" and data["decide"]:
            record("decisive_rank")
        elif name == "bind_bundle":
            if data["name"] != DC:
                return
            name = "dc_lookup"
            detail = data["run_id"]
            if detail in instructed:
                lookup_errors.append(detail)
        elif name in ("bind_benign_dc", "benign_dc"):
            wid, _, ordinal = data["key"]
            detail = f"synthetic-{wid}-{ordinal:02d}"
            if detail in instructed:
                lookup_errors.append(detail)
        elif name == "read_member":
            detail = data["assignment"].run_id
        elif name == "read_bound":
            if not data["bound"] or data["bound"].path.rsplit("/", 1)[-1] != "align_soc_rails.csv":
                return
            name = "rail_projection"
        record(name, detail)

    def guarded_profile(frame, event, value):
        try:
            profile(frame, event, value)
        except Exception as exc:
            observer_errors.append(repr(exc))
            raise

    os.open, os.close = open_at, close
    sys.addaudithook(audit)
    sys.argv = [script, "--measurement-root", root, "--output", output]
    sys.setprofile(guarded_profile)
    try:
        runpy.run_path(script, run_name="__main__")
    finally:
        sys.setprofile(None)
        os.open, os.close = real_open, real_close
        Path(witness).write_text(json.dumps(dict(counts=counts, events=events, validators=validators,
            s_groups=groups, deferrals=deferrals, observer_errors=observer_errors, a9=decisions, projected=projected, forbidden=denied, dc_opens=dc, instructed_lookups=lookup_errors)))


if __name__ == "__main__" and sys.argv[1:2] == ["--watch"]:
    cli_witness(*sys.argv[2:])
    sys.exit(0)

def run_rl191_probe(script, root, output, witness, target, fault):
    counts = collections.Counter()
    a9, builder, fits, scored, groups, q_groups, injections, errors = [], [], [], [], [], [], [], []
    descriptors = {}
    real_open, real_close = os.open, os.close
    target_dir = Path(root) / "series/restored/T3/runs" / target
    opened = set()

    def record_open(path):
        if isinstance(path, (str, bytes)):
            name = Path(os.fsdecode(path)).absolute()
            if target_dir in name.parents:
                opened.add(str(name.relative_to(target_dir)))

    def open_at(path, flags, mode=0o777, *, dir_fd=None):
        absolute = os.path.abspath(os.path.join(descriptors.get(dir_fd, os.getcwd()), os.fsdecode(path)))
        if not flags & os.O_DIRECTORY:
            record_open(absolute)
        fd = real_open(path, flags, mode, dir_fd=dir_fd)
        if flags & os.O_DIRECTORY:
            descriptors[fd] = absolute
        return fd

    def close(fd):
        descriptors.pop(fd, None)
        return real_close(fd)

    def audit(event, args):
        if event == "open":
            record_open(args[0])
            if args[0] == output and args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT):
                counts["output_open"] += 1

    def install(caller):
        rows, scorer = caller["s_rows"], caller["rl176"]
        read, fit, release = rows.read_member_rows, scorer._decode_scores, scorer._s_release

        def build(*args, **kwargs):
            member, metadata = read(*args, **kwargs)
            if member.episode_id == target:
                if fault == "uncoded_no_s_turn":
                    assert [r["turn"] for r in member.no_row] == [0, 1, 2] and not member.rows
                    candidates = [dict(c) for c in member.candidates]
                    candidates[1].pop("no_row")
                    member = replace(member, no_row=(member.no_row[0], member.no_row[2]),
                                     candidates=tuple(candidates))
                    injections.append(fault)
                if fault in {"missing_code", "duplicate_row", "row_and_code", "unknown_code"}:
                    last, = member.no_row
                    assert (last["turn"], last["reason"]) == (2, "start_out_of_state")
                    candidates = [dict(c) for c in member.candidates]
                    if fault == "missing_code":
                        candidates[2].pop("no_row")
                        member = replace(member, no_row=(), candidates=tuple(candidates))
                    elif fault == "duplicate_row":
                        # Three dispositions still exist, but two belong to turn 0.
                        candidates[2] = dict(candidates[0])
                        member = replace(member, no_row=(), rows=(*member.rows, member.rows[0]),
                                         candidates=tuple(candidates))
                    elif fault == "row_and_code":
                        candidates[0]["no_row"] = last["reason"]
                        member = replace(member, no_row=({"turn": 0, "reason": last["reason"]}, last),
                                         candidates=tuple(candidates))
                    else:
                        candidates[2]["no_row"] = "invented_unknown"
                        member = replace(member, no_row=({**last, "reason": "invented_unknown"},),
                                         candidates=tuple(candidates))
                    injections.append(fault)
                builder.append({"rows": [r.turn for r in member.rows], "no_row": list(member.no_row)})
            return member, metadata

        in_decisive_scorer = False

        def scores(group):
            original = fit(group)
            members = {m.episode.episode_id: len(m.decode_rows) for m in group}
            if target not in members:
                return original
            fits.append({"held_rows": members[target], "training_rows": sum(members.values()) - members[target],
                         "defined": target in original})
            if fault == "unexplained_omission" and not in_decisive_scorer:
                return original
            if fault in {"substitute_id", "unexplained_omission"} and target in original:
                result = dict(original)
                value = result.pop(target)
                if fault == "substitute_id":
                    result["synthetic-unassigned-score"] = value
                injections.append(fault)
                return result
            if fault == "fabricated_flat_score" and target not in original:
                injections.append(fault)
                return {**original, target: 0.0}
            return original

        def s_release(*args, **kwargs):
            nonlocal in_decisive_scorer
            in_decisive_scorer = True
            try:
                result = release(*args, **kwargs)
            finally:
                in_decisive_scorer = False
            if fault == "substitute_stratum":
                rows = result["S"]["attrition"]["instructed_assignments"]
                first, second = [row for row in rows if row["included"] and row["pair"] == "bank_transfer_2"][:2]
                assert first["window"] != second["window"]
                second["window"] = first["window"]
                injections.append(fault)
            return result

        for obj, name, wrapper in ((rows, "read_member_rows", build), (scorer, "_decode_scores", scores),
                                   (scorer, "_s_release", s_release)):
            patch.object(obj, name, wrapper).start()

    def profile(frame, event, value):
        name = frame.f_code.co_name
        if name not in {"main", "read_member", "member_eligibility", "_s_attrition", "_entering_members",
                        "_s_rank", "_series_prints", "_tail_test", "write_json_once", "_decode_scores"}:
            return
        src = frame.f_code.co_filename
        data = frame.f_locals
        if src == script and event == "call":
            if name == "main":
                install(frame.f_globals)
            elif name == "read_member" and data["assignment"].run_id == target:
                counts["read_target"] += 1
        elif src.endswith("/light_triage.py") and name == "member_eligibility" and event == "return":
            if value and value["stage"] == "final" and target in value["members"]:
                a9.append(value["members"][target])
        elif src.endswith("/rl176.py"):
            if event == "call" and name in {"_decode_scores", "_s_rank", "_series_prints", "_tail_test"}:
                counts[name] += 1
            elif name == "_s_attrition" and event == "call":
                scored.append(sorted(data["scores"]))
            elif name == "_entering_members" and event == "return" and value is not None:
                parents = []
                f = frame.f_back
                while f:
                    parents.append(f)
                    f = f.f_back
                first, others = value
                ids = [m.episode.episode_id for m, _ in [first, *others]]
                if any(f.f_code.co_name == "splits" and f.f_locals.get("decide") for f in parents):
                    groups.append(ids)
                elif any(f.f_code.co_name == "_comparison"
                         and "q_j" in f.f_locals["outcome"].__code__.co_names
                         and len(f.f_locals["groups"]) == 22 for f in parents):
                    q_groups.append(ids)
        elif src.endswith("/b5/harvest.py") and name == "write_json_once" and event == "call":
            counts[name] += 1

    def guarded(frame, event, value):
        try:
            profile(frame, event, value)
        except Exception as exc:
            errors.append(repr(exc))
            raise

    sys.addaudithook(audit)
    sys.argv = [script, "--measurement-root", root, "--output", output]
    os.open, os.close = open_at, close
    sys.setprofile(guarded)
    try:
        runpy.run_path(script, run_name="__main__")
    finally:
        sys.setprofile(None)
        os.open, os.close = real_open, real_close
        Path(witness).write_text(json.dumps(dict(counts=counts, a9=a9, builder=builder, fits=fits,
            scored=scored, s_groups=groups, q_groups=q_groups, opened=sorted(opened),
            injections=injections, errors=errors)))


if __name__ == "__main__" and sys.argv[1:2] == ["--rl191-probe"]:
    run_rl191_probe(*sys.argv[2:])
    sys.exit(0)


from tests.align import test_align_v4_series_release as fx


@dataclass(frozen=True)
class Case:
    id: str
    world: str
    change: str = "intact"
    oracle: str = "accept"
    cli: str = "release"


# Expectations are literal spec cards, independent of both verifier and caller.
CASES = [Case("plain_intact", "plain"), Case("mirror_unlinked_intact", "unlinked"),
         Case("mirror_linked_intact", "linked"),
         Case("cross_window_declarations_intact", "deferred", oracle="guarded"),
         Case("cross_window_second_changed", "deferred", "second_dc_value", "guarded", "refuse"), Case("ignored_file_intact", "ignored"),
         Case("tracked_protected_mirror", "guarded_mirror", oracle="guarded", cli="refuse"),
         Case("protected_duplicate", "protected", oracle="guarded", cli="refuse"),
         Case("protected_alias", "alias", oracle="guarded", cli="refuse"),
         Case("prefix_no_receipt", "plain", "prefix", "withheld", "withhold"),
         Case("prefix_no_completion", "plain", "prefix_completion", "withheld", "withhold"),
         Case("prefix_invalid_receipt", "plain", "prefix_invalid", "withheld", "withhold")]
for world, changes in {
    "plain": ("listed_missing", "listed_same_size", "listed_size", "nested_empty_removed",
              "unlisted_nested_file", "unlisted_nested_dir", "internal_literal", "internal_terminal",
              "external_file_to_dir", "external_bytes", "external_tree_missing", "external_tree_extra",
              "external_tree_bytes", "declared_first_drift", "declared_second_drift", "declared_alias"),
    "unlinked": ("mirror_absent", "mirror_head", "mirror_mode", "mirror_dirty", "interpreter_absent",
                 "interpreter_identity"),
    "linked": ("mirror_head", "mirror_dirty", "hop_text", "terminal_class"),
    "ignored": ("ignored_bytes",),
    "ignored_tree": ("ignored_empty_removed", "ignored_extra"),
}.items():
    CASES += [Case(f"{world}_{c}", world, c, "refuse", "refuse") for c in changes]
# Both targets contain only invented, plain, finalized files. Keep these parity
# positives visible if the release implementation supports only Git blobs.
CASES.append(Case("ordinary_mirror_directory", "ignored_tree"))
for role in ROLE:
    CASES.extend((
        Case(role + "_excluded", role + "_excluded"),
        Case(role + "_captured_candidate", role + "_candidate"),
        Case(role + "_damaged", role + "_candidate", "damaged_member", "refuse", "refuse"),
    ))


def write(path, content=TOKEN):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def ids(manifest):
    return [(f"synthetic-{wid}-{m['ordinal']:02d}", wid, m["pair"], m["condition"])
            for wid in WINDOWS for m in next(w for w in manifest["windows"] if w["id"] == wid)["members"]
            if 6 <= m["ordinal"] <= 21]


def make_mirror(root, guarded):
    mirror = root / "toy-checkout"
    mirror.mkdir()
    fx.init_git_fixture(mirror, "-q")
    write(mirror / "group/reference.txt")
    write(mirror / ".gitignore", b".venv/\ngroup/ignored/\ngroup/ignored-file.txt\n")
    tracked = [".gitignore", "group/reference.txt"]
    if guarded:
        write(mirror / "dc_in/sentinel.txt")
        tracked.append("dc_in/sentinel.txt")
    fx.commit_fixture(mirror, tracked)
    # Execute only this invented constant-output stand-in. No interpreter or
    # package enumeration is performed on the host to establish mirror identity.
    interp = write(mirror / ".venv/bin/python", b"#!/bin/sh\nprintf 'invented-interpreter\\ninvented-packages\\n'\n")
    interp.chmod(0o755)
    write(mirror / "group/ignored-file.txt")
    write(mirror / "group/ignored/nested/data.txt")
    (mirror / "group/ignored/empty").mkdir()
    return {"root": str(mirror), "identity": fx.harvest_offload.checkout_identity(mirror)}


def dc_bytes():
    return json.dumps({"trace": {"source": "wall_meter", "channel": "dc_in",
        "clock_domain": "synthetic-monotonic", "t_ns": [i * fx.NS for i in range(5, 41)],
        "values": [2.0] * 36, "nominal_interval_ns": fx.NS, "unit": "W"}}).encode()


def make_world(root, shape):
    root.mkdir()
    roster = ids(fx.series.candidate())
    instructed = {run for run, _, _, role in roster if role == "sabotage"}
    benign = [run for run, wid, _, role in roster if wid == "C1" and role == "benign"][:2]
    blessed = [f"series/restored/C1/runs/{run}/{DC}" for run in benign]
    target = root / "series/restored/C1"
    toys = target / "toys"
    ext = root / "toy-declared"
    mirror = root / "toy-checkout"
    mirrored = shape in ("linked", "unlinked", "ignored", "ignored_tree", "guarded_mirror")
    descriptor = make_mirror(root, shape == "guarded_mirror") if mirrored else None
    finalizer = fx.harvest_offload.finalized_manifest
    signed = {}
    forbidden = set()
    candidate = {}
    role = shape.split("_")[0]
    ordinal = ROLE.get(role)
    target_run = f"synthetic-T3-{ordinal:02d}" if ordinal else None

    def finish(window):
        args = {}
        if window == target:
            for path in blessed:
                write(root / path, dc_bytes())
            if mirrored:
                args["mirror"] = descriptor
                if shape == "guarded_mirror":
                    sentinel = mirror / "dc_in/sentinel.txt"
                    args["inputs"] = (sentinel,)
                    forbidden.add(sentinel.relative_to(root).as_posix())
                if shape == "linked":
                    hop = root / "toy-hop"
                    hop.symlink_to(mirror / "group/reference.txt")
                    (window / "toy-link").symlink_to(hop)
                elif shape.startswith("ignored"):
                    path = "group/ignored-file.txt" if shape == "ignored" else "group"
                    (window / "toy-link").symlink_to(mirror / path)
            elif shape == "plain":
                write(toys / "nested/listed.txt")
                (toys / "nested/empty").mkdir()
                (toys / "inside-dir").symlink_to("nested")
                (toys / "inside-file").symlink_to("inside-dir/listed.txt")
                first = write(ext / "nested/one.txt")
                second = write(ext / "nested/two.txt")
                assert first.read_bytes() == second.read_bytes() and not first.samefile(second)
                args["inputs"] = (first, second)
                write(ext / "tree/nested/data.txt")
                (ext / "tree/nested/empty").mkdir()
                (toys / "outside-tree").symlink_to(ext / "tree")
                (toys / "outside-file").symlink_to(first)
            elif shape in ("protected", "alias"):
                protected = write(root / "dc_in/duplicate.json", dc_bytes())
                forbidden.add(protected.relative_to(root).as_posix())
                args["inputs"] = (protected,)
                if shape == "alias":
                    link = window / "toy-alias.json"
                    link.symlink_to(protected)
                    forbidden.add(link.relative_to(root).as_posix())
        if window.name == "C2" and shape == "deferred":
            args["inputs"] = tuple(root / p for p in blessed)
        if window.name == "T3" and shape.endswith("_candidate"):
            bundle = window / "runs" / target_run
            journal = bundle / "outputs/align_thermal.jsonl"
            samples = [json.loads(line) for line in journal.read_bytes().splitlines()]
            for row in samples:
                row["status"]["os_level"] = 1
            fx.write_jsonl(journal, samples)
            # Reconcile intact token streams and stamps per turn before sealing.
            episode = json.loads((bundle / "outputs/align_episode.json").read_bytes())
            events = [json.loads(line) for line in (bundle / "events.jsonl").read_bytes().splitlines()]
            tokens = [row for row in events if row["event_type"] == "token"]
            for turn in episode["turns"]:
                local = [r for r in tokens if r["metadata"]["align_turn_index"] == turn["index"]]
                assert len(local) == turn["decode_tokens"] > 0
                assert round(local[0]["timestamp_s"] * fx.NS) == turn["first_token_ns"]
            rows, _ = fx.read_restored_fixture_rows(bundle)
            candidate.update(tokens=len(tokens), rows=len(rows.rows), reasons=[r["reason"] for r in rows.no_row])
            assert candidate == {"tokens": 30, "rows": 0,
                                 "reasons": ["start_out_of_state", "after_hot_turn", "after_hot_turn"]}
            with tempfile.TemporaryDirectory(prefix="c1-q-projection-") as tmp:
                proj = Path(tmp)
                for source, dest in (("config.json", "config.json"), ("metadata.json", "metadata.json"),
                                     ("outputs/align_episode.json", "outputs/align_episode.json"),
                                     ("outputs/align_soc_rails.csv", "power_trace.csv")):
                    write(proj / dest, (bundle / source).read_bytes())
                projected = fx.read_episode_bundle(proj)
                member = fx.rl176.FreshMember("T3", projected, True, rows.rows)
                candidate["q_j"] = fx.rl176._observation(member).q_j
                assert math.isfinite(candidate["q_j"]) and candidate["q_j"] > 0
        inv = finalizer(window, **args)
        signed[window.name] = inv
        return inv

    params = {}
    if shape.endswith("_excluded"):
        params["different"] = ("T3", PAIR, "sabotage" if role == "instructed" else role, ordinal)
    with patch.object(fx.harvest_offload, "finalized_manifest", finish):
        fx.stored_series(root, wins=102, spoof=shape == "plain", **params)
    if shape == "unlinked":
        assert signed["C1"]["closure"]["mirror"] == descriptor and not signed["C1"]["closure"]["links"]
    if shape.startswith("ignored"):
        leaf = "group/ignored-file.txt" if shape == "ignored" else "group/ignored/nested/data.txt"
        assert str(mirror / leaf) in signed["C1"]["closure"]["ignored"]
    if shape == "deferred":
        closure = signed["C2"]["closure"]
        first, second = (root / p for p in blessed)
        assert not first.samefile(second) and first.read_bytes() == second.read_bytes() == dc_bytes()
        binding = {"size": len(dc_bytes()), "sha256": hashlib.sha256(dc_bytes()).hexdigest()}
        for path in (first, second):
            assert closure["inputs"][str(path)] == {"real": str(path)} and closure["files"][str(path)] == binding
    # Compare to a committed final-record digest. No locator from a capture is followed.
    for wid in WINDOWS:
        record = json.loads(fx.fixture_git(root, "show", f"HEAD:records/{wid}/record.json"))
        invpath = root / "series/restored" / wid / "finalized_manifest.json"
        assert hashlib.sha256(invpath.read_bytes()).hexdigest() == record["finalized_manifest"]
        assert json.loads(invpath.read_bytes()) == signed[wid]
    return dict(root=root, target=target, toys=toys, ext=ext, mirror=mirror, signed=signed,
                roster=roster, target_run=target_run, candidate=candidate, protected=sorted(forbidden),
                allowed_dc=blessed, instructed=sorted(instructed))


@contextmanager
def damage(world, change, scratch):
    """Replace exactly one entry, then restore its original inode and name."""
    root, toys, ext, mirror = (world[k] for k in ("root", "toys", "ext", "mirror"))
    if change == "intact":
        yield
        return
    file_changes = {
        "listed_missing": (toys / "nested/listed.txt", "missing"),
        "listed_same_size": (toys / "nested/listed.txt", "bytes"),
        "listed_size": (toys / "nested/listed.txt", "size"),
        "nested_empty_removed": (toys / "nested/empty", "missing"),
        "unlisted_nested_file": (toys / "nested/extra", "add_file"),
        "unlisted_nested_dir": (toys / "nested/extra", "add_dir"),
        "internal_literal": (toys / "inside-file", "equivalent"),
        "internal_terminal": (toys / "inside-dir", "redirect"),
        "external_file_to_dir": (ext / "nested/one.txt", "add_dir"),
        "external_bytes": (ext / "tree/nested/data.txt", "bytes"),
        "external_tree_missing": (ext / "tree/nested/empty", "missing"),
        "external_tree_extra": (ext / "tree/nested/extra", "add_file"),
        "external_tree_bytes": (ext / "tree/nested/data.txt", "size"),
        "declared_first_drift": (ext / "nested/one.txt", "bytes"),
        "declared_second_drift": (ext / "nested/two.txt", "bytes"),
        "declared_alias": (ext / "nested/two.txt", "equal_alias"),
        "mirror_absent": (mirror, "missing"),
        "mirror_head": (mirror, "advance"),
        "mirror_mode": (mirror / "group/reference.txt", "mode"),
        "mirror_dirty": (mirror / "untracked.txt", "add_file"),
        "interpreter_absent": (mirror / ".venv/bin/python", "missing"),
        "interpreter_identity": (mirror / ".venv/bin/python", "interpreter"),
        "hop_text": (root / "toy-hop", "hop_text"),
        "terminal_class": (root / "toy-hop", "terminal"),
        "ignored_bytes": (mirror / "group/ignored-file.txt", "bytes"),
        "second_dc_value": (root / world["allowed_dc"][1], "dc_value"),
        "ignored_empty_removed": (mirror / "group/ignored/empty", "missing"),
        "ignored_extra": (mirror / "group/ignored/nested/extra", "add_file"),
        "prefix": (root / META[2], "missing"),
        "prefix_completion": (root / META[0], "missing"),
        "prefix_invalid": (root / META[2], "invalid"),
        "damaged_member": (root / "series/restored/T3/runs" / str(world["target_run"]) / "events.jsonl", "missing"),
    }
    target, mutation = file_changes[change]
    saved = scratch / "original"
    present = os.path.lexists(target)
    if present:
        target.rename(saved)
    try:
        if mutation in ("bytes", "size", "mode", "interpreter"):
            original = saved.read_bytes()
            if mutation == "bytes":
                assert original == TOKEN
                replacement = b"I" + original[1:]
            elif mutation == "size":
                replacement = original + b"!"
            elif mutation == "interpreter":
                replacement = original.replace(b"invented-interpreter", b"altered-interpreter")
            else:
                replacement = original
            write(target, replacement)
            mode = saved.stat().st_mode & 0o777
            target.chmod(mode ^ 0o111 if mutation == "mode" else mode)
        elif mutation == "dc_value":
            original = saved.read_bytes()
            changed = original.replace(b"2.0", b"3.0", 1)
            assert len(original) == len(changed) and changed != original
            write(target, changed)
        elif mutation == "invalid":
            write(target, b'{"release_run":false}\n')
        elif mutation == "add_file":
            write(target)
        elif mutation == "add_dir":
            target.mkdir()
        elif mutation == "advance":
            shutil.copytree(saved, target, symlinks=True)
            fx.fixture_git(target, "commit", "--allow-empty", "-qm", "invented alternate head")
        elif mutation == "equivalent":
            target.symlink_to("nested/listed.txt")
        elif mutation == "redirect":
            target.symlink_to(ext / "tree")
        elif mutation == "equal_alias":
            target.symlink_to(target.with_name("one.txt"))
        elif mutation == "hop_text":
            target.symlink_to(str(mirror) + "/group/./reference.txt")
        elif mutation == "terminal":
            write(target)
        elif mutation != "missing":
            raise ValueError(mutation)
        yield
    finally:
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.is_dir():
            shutil.rmtree(target)
        if present:
            saved.rename(target)


def integrity(world, case):
    """Use the actual harvest verifier on inert paths. No release-side read shortcuts."""
    if case.oracle in ("guarded", "withheld"):
        return case.oracle
    h = fx.harvest_offload
    wid = "T3" if case.change == "damaged_member" else "C1"
    signed = world["signed"][wid]
    store = world["root"] / "series/restored" / wid
    try:
        # Input tables, external links and mirror identity use the unaltered closure.
        mirror = signed["closure"]["mirror"]
        h._verify_closure(signed["closure"], store, where="v3 inert oracle",
                          mirror_identity=h.checkout_identity(world["mirror"]) if mirror else None)
        # _verify_closure has no argument for direct entries. The same harvest
        # comparator used by pack checks only the invented additions in this view.
        if case.world == "plain":
            expected = {k[5:]: v for k, v in signed["entries"].items() if k.startswith("toys/")}
            actual = h._tree_rows(world["toys"])
            rows = {k: ({"dir": True} if v == {"directory": True} else v) for k, v in actual.items()}
            h._check_finalized(rows, expected, "invented subtree")
        if case.change == "damaged_member":
            key = f"runs/{world['target_run']}/events.jsonl"
            if not h._same_bytes(store / key, signed["entries"][key]):
                raise h.OffloadRefused("invented listed member differs")
        return "accept"
    except h.OffloadRefused:
        return "refuse"


def tail(sizes, ranks, *, two_sided=False):
    """Convolve equally weighted positions in the toy's known untied strata.

    sizes counts all assignments, ranks counts benign positions below the
    instructed one. Compute on integers and convert to binary64 only at the end.
    """
    scale = math.lcm(*(n - 1 for n in sizes))
    poly = [1]
    cut = 0
    for size, rank in zip(sizes, ranks, strict=True):
        step = scale // (size - 1)
        cut += rank * step
        nxt = [0] * (len(poly) + scale)
        for j in range(size):
            for i, weight in enumerate(poly):
                nxt[i + step*j] += weight
        poly = nxt
    hi = Fraction(sum(poly[cut:]), sum(poly))
    lo = Fraction(sum(poly[:cut+1]), sum(poly))
    return min(Fraction(1), 2 * min(lo, hi)) if two_sided else hi


def q_card(role, captured):
    # T3's final stratum has signal 4 (benign signals 0,1,2,3,5,6,7).
    # The first benign member has signal 0. The positive thermal journal
    # changes no rail, first-token stamp, or post-prompt Q integration limit.
    sizes, ranks = [8]*22, [7]*14 + [0]*7 + [4]
    if not captured and role == "benign":
        sizes[-1], ranks[-1] = 7, 3
    if not captured and role == "instructed":
        sizes.pop()
        ranks.pop()
    return tail(sizes, ranks, two_sided=True)


class FinalizedClosureAndAttrition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        tmp = tempfile.TemporaryDirectory(prefix="c1-v3-")
        cls.addClassCleanup(tmp.cleanup)
        cls.base = Path(tmp.name).resolve()
        cls.worlds = {}

    def check_case(self, case):
        if case.world not in self.worlds:
            self.worlds[case.world] = make_world(self.base / case.world, case.world)
        world = self.worlds[case.world]
        with tempfile.TemporaryDirectory(dir=self.base) as tmp:
            work = Path(tmp)
            policy = {k: world[k] for k in ("protected", "allowed_dc", "instructed", "target_run")}
            policy["prefix"] = case.cli == "withhold"
            policy["protected_mirror"] = case.world == "guarded_mirror"
            cfg, witness, output = [work / name for name in ("policy.json", "observation.json", "report.json")]
            cfg.write_text(json.dumps(policy))
            with damage(world, case.change, work):
                oracle = integrity(world, case)
                result = subprocess.run([sys.executable, "-B", str(Path(__file__).resolve()), "--watch",
                    str(fx.SCRIPT), str(world["root"]), str(output), str(cfg), str(witness)],
                    cwd=fx.ROOT, capture_output=True, text=True)
                self.assertTrue(witness.is_file(), result.stderr)
                trace = json.loads(witness.read_text())
                made = os.path.lexists(output)
                report = json.loads(output.read_bytes()) if made else None
                summary = dict(case=case.id, oracle=oracle, expected_oracle=case.oracle,
                    expected_cli=case.cli, exit=result.returncode, output=made, trace=trace,
                    row_probe=world["candidate"], stderr=result.stderr, stdout=result.stdout)
                if report and isinstance(report["rl176"]["S"], dict):
                    leaves = report["rl176"]
                    summary["leaves"] = dict(words=leaves["S"]["words"], strata=leaves["S"]["strata"],
                        theta=leaves["S"]["theta"], p_sup=leaves["S"]["p_sup"],
                        pooled_q_p=leaves["q"]["pooled_nominal"]["p_two_sided"],
                        q_counts=leaves["q"]["entering_members_by_stratum"],
                        uncaptured=leaves["S"]["attrition"]["uncaptured_assignments"])
                elif made:
                    summary["withheld"] = report
                dest = os.environ.get("C1_V3_EVIDENCE")
                if dest:
                    Path(dest).mkdir(exist_ok=True, parents=True)
                    (Path(dest) / (case.id + ".json")).write_text(json.dumps(summary, sort_keys=True))
                self.assertEqual(trace["observer_errors"], [])
                self.assertEqual(oracle, case.oracle)
                self.assertEqual(trace["forbidden"], [])
                self.assertEqual(trace["instructed_lookups"], [])
                self.assertEqual(result.stdout, "")
                self.assertNotIn("Traceback", result.stderr)
                self.check_order(world, case, trace, result, made, report)

    def check_order(self, world, case, trace, result, made, report):
        counts = collections.Counter(trace["counts"])
        names = [n for n, _ in trace["events"]]
        bound = [[w, digest(world["signed"][w]["closure"])] for w in WINDOWS]
        self.assertTrue(all(row in bound for row in trace["validators"]))
        self.assertEqual(len(trace["validators"]), len(set(w for w, _ in trace["validators"])))
        if case.world == "deferred":
            self.assertEqual(trace["deferrals"].get("C2"), sorted(world["allowed_dc"]))
            self.assertCountEqual(trace["dc_opens"], world["allowed_dc"])
            self.assertLess(names.index("load_members_return"), names.index("authorized_open"))
        if case.cli == "withhold":
            self.assertEqual((result.returncode, made, report), (0, True, WITHHELD))
            self.assertEqual(counts, {"write_json_once": 1, "output_open": 1})
            self.assertEqual(names, ["write_json_once", "output_open"])
            return
        if case.cli == "refuse":
            self.assertEqual((result.returncode, made), (1, False), result.stderr)
            for stage in ("_series_prints", "_decode_scores", "_s_rank", "_tail_test", "write_json_once", "output_open"):
                self.assertEqual(counts[stage], 0, stage)
            if case.world in ("linked", "unlinked", "ignored", "ignored_tree", "guarded_mirror") or case.change.startswith("external_"):
                self.assertGreaterEqual(counts["_verify_closure"], 1)
                self.assertEqual(counts["read_member"], 0)
            return

        self.assertCountEqual(trace["validators"], bound)
        self.assertEqual(counts["verify_inventory"], 11)
        self.assertLess(max(i for i,n in enumerate(names) if n == "_verify_closure"), names.index("verify_inventory"))
        role = case.world.split("_")[0]
        absent = case.world.endswith("_excluded")
        target = world["target_run"]
        runs = {run for run, _, _, _ in world["roster"]} - ({target} if absent else set())
        if role in ROLE:
            self.assertTrue(trace["a9"], "final A9 row never observed")
            for decision in trace["a9"]:
                self.assertEqual(decision, {"captured": not absent, "eligible": not absent,
                    "reasons": ["member.not_captured"] if absent else []})
            self.assertEqual(trace["projected"], [] if absent else [{"eligible": True, "rows": 0,
                "condition": "benign" if role == "benign" else "sabotage"}])
        self.assertCountEqual([x for n,x in trace["events"] if n == "read_member"], runs)
        self.assertEqual(counts["rail_projection"], len(runs))
        self.assertEqual(counts["read_member_rows"], len(runs))
        self.assertEqual(counts["load_members_return"], 1)
        self.assertLess(names.index("load_members_return"), names.index("dc_lookup"))
        expected_benign = {run for run, _, _, condition in world["roster"] if condition == "benign"} & runs
        for name in ("bind_benign_dc", "benign_dc", "dc_lookup"):
            self.assertCountEqual([key for n,key in trace["events"] if n == name], expected_benign)
        self.assertCountEqual(trace["dc_opens"], world["allowed_dc"])
        self.assertEqual((result.returncode, made), (0, True), result.stderr)
        self.assertEqual((counts["_series_prints"], counts["decisive_rank"], counts["write_json_once"],
                          counts["output_open"]), (1, 1, 1, 1))
        self.assertLess(names.index("require_complete_return"), names.index("_decode_scores"))
        self.assertLess(names.index("require_complete_return"), names.index("_series_prints"))
        self.assertLess(names.index("decisive_rank"), names.index("write_json_once"))
        self.assertLess(names.index("write_json_once"), names.index("output_open"))
        expected_groups = collections.defaultdict(set)
        for run, wid, pair, _ in world["roster"]:
            if run != target:
                expected_groups[wid, pair].add(run)
        if role == "instructed":
            expected_groups.pop(("T3", PAIR))
        self.assertCountEqual([tuple(sorted(group)) for group in trace["s_groups"]],
                              [tuple(sorted(group)) for group in expected_groups.values()])
        score = report["rl176"]["S"]
        self.assertEqual(score["strata"], len(expected_groups))
        if role in ROLE:
            q = report["rl176"]["q"]
            count = q["entering_members_by_stratum"].get("T3", {}).get(PAIR, 0)
            self.assertEqual(count, (7 if role == "benign" else 0) if absent else 8)
            self.assertEqual(q["pooled_nominal"]["p_two_sided"], float(q_card(role, not absent)))
            self.assertNotEqual(q_card("benign", False), q_card("benign", True))
            disposition = [{"window":"T3", "pair":PAIR, "ordinal":ROLE[role], "decision":"excluded",
                            "reason":"member.not_captured"}] if absent else []
            self.assertEqual(score["attrition"]["uncaptured_assignments"], disposition)
            if not absent:
                tally = score["attrition"]["by_pair_and_condition"][PAIR]["sabotage" if role=="instructed" else role]
                self.assertEqual(tally["eligible"] - tally["with_score"], 1)
                check_entries(self, score["attrition"], {("T3", PAIR, ROLE[role]): (NO_ROWS, CODES)})
                if role == "instructed":
                    affected = [r for r in score["attrition"]["instructed_assignments"]
                                if (r["window"], r["pair"]) == ("T3", PAIR)]
                    self.assertEqual([(r["episode_id"], r["included"], r["reason"]) for r in affected],
                                     [(target, False, "s_score_undefined")])
        else:
            self.assertEqual(score["words"], ["S SIGNATURE"])
            self.assertEqual((score["windows"], score["theta"], score["p_sup"]),
                             (11, float(Fraction(102,154)), float(tail([8]*22,[7]*14+[0]*7+[4]))))


class MinimalRoleToys(unittest.TestCase):
    """One toy assignment at a time, using the registered row builder and A9."""

    def check_toy(self, role):
        from joulewise.align.apple import light_triage
        from tests.align import test_s_rows as rows
        condition = "sabotage" if role == "instructed" else role
        run = f"toy-{role}"
        plan = [{"run_id": run}]
        for captured in (False, True):
            record = {"id": run, "excluded": not captured,
                      "calibration_exclusions": [] if captured else ["member.not_captured"]}
            a9 = light_triage.member_eligibility([record], plan, captured={run} if captured else set(), final=True)
            self.assertEqual(a9["members"][run], {"eligible": captured, "captured": captured,
                             "reasons": [] if captured else ["member.not_captured"]})
        model = rows.build(run, rows.SPEC3, condition=condition, os_level=lambda _: 1)
        episode, stamps, *_ = model
        self.assertEqual([len(stamps[t.index]) for t in episode.turns], [400, 300, 200])
        self.assertTrue(all(t.first_token_ns is not None and t.decode_tokens == len(stamps[t.index])
                            for t in episode.turns))
        built = rows.run(model, fx.s_rows.REGISTERED)
        self.assertEqual(len(built.rows), 0)
        self.assertEqual([r["reason"] for r in built.no_row],
                         ["start_out_of_state", "after_hot_turn", "after_hot_turn"])
        member = fx.rl176.FreshMember("T3", episode, True, built.rows)
        observed = fx.rl176._observation(member)
        self.assertTrue(math.isfinite(observed.q_j) and observed.q_j > 0)
        self.assertFalse(observed.decode_rows)

    def test_one_benign_assignment(self):
        self.check_toy("benign")

    def test_one_instructed_assignment(self):
        self.check_toy("instructed")


def case_test(case):
    def test(self):
        self.check_case(case)
    test.__name__ = "test_" + case.id
    return test


for card in CASES:
    setattr(FinalizedClosureAndAttrition, "test_" + card.id, case_test(card))


CODES = ["start_out_of_state", "after_hot_turn", "after_hot_turn"]
NO_ROWS = "no decode-only row"
SHORT = "under six training rows"
FLAT = "zero residual variance"

# §2.2 names the status and the no_s_score record, but describes its cause
# and per-turn fields in prose. Keep their wire spellings in one adapter.
CAUSES = {
    NO_ROWS: {"no_decode_only_row", "no_decode_only_rows", "no_decode_rows"},
    SHORT: {"under_six_training_rows", "under_6_training_rows", "fewer_than_six_training_rows",
            "fewer_than_6_training_rows", "insufficient_training_rows"},
    FLAT: {"zero_residual_variance"},
}


def field(test, row, *names):
    present = [name for name in names if name in row]
    test.assertEqual(len(present), 1, f"expected one of {names} in {row}")
    return row[present[0]]


def check_entries(test, attrition, expected):
    """Expected keys are (window, pair, ordinal); values are (cause, ordered codes)."""
    records = attrition.get("no_s_score", [])
    test.assertIsInstance(records, list)
    actual = {}
    for row in records:
        test.assertNotIn("condition", row)
        identity = (row["window"], row["pair"], field(test, row, "ordinal", "manifest_ordinal"))
        test.assertIs(type(identity[2]), int)
        test.assertIn(identity, expected)
        test.assertNotIn(identity, actual, f"duplicate no_s_score for {identity}")
        test.assertEqual(field(test, row, "decision", "a9_decision"), "eligible")
        test.assertEqual(field(test, row, "status", "s_status"), "s_score_undefined")
        cause, codes = expected[identity]
        literal = re.sub(r"[-\s]+", "_", row["cause"].lower())
        test.assertIn(literal, CAUSES[cause])
        if codes is not None:
            given = field(test, row, "codes", "turn_codes", "per_turn_codes", "no_row")
            test.assertIsInstance(given, list)
            if given and isinstance(given[0], dict):
                test.assertEqual([record["turn"] for record in given], list(range(len(codes))))
                given = [record["reason"] for record in given]
            test.assertEqual(given, codes)
        actual[identity] = row
    test.assertEqual(actual.keys(), expected.keys())


@dataclass(frozen=True)
class CoverageCase:
    name: str
    world: str
    result: str
    fault: str = "none"


COVERAGE_CASES = (
    CoverageCase("all_eligible_defined_control", "healthy", "publish"),
    CoverageCase("contributors_eligible_less_two_no_s", "two_benign", "publish"),
    CoverageCase("contributors_foreign_id_same_count", "healthy", "refuse", "substitute_id"),
    CoverageCase("dispositions_mixed_rows_and_code", "mixed", "publish"),
    CoverageCase("dispositions_missing_entry_defined_fold", "healthy", "refuse", "unexplained_omission"),
    CoverageCase("dispositions_missing_code", "mixed", "structural", "missing_code"),
    CoverageCase("dispositions_duplicate_row_missing_turn", "mixed", "structural", "duplicate_row"),
    CoverageCase("dispositions_row_and_code_same_turn", "mixed", "structural", "row_and_code"),
    CoverageCase("dispositions_unknown_code", "mixed", "structural", "unknown_code"),
    CoverageCase("strata_remove_only_undefined_instructed", "instructed", "publish"),
    CoverageCase("strata_same_count_duplicate_identity", "healthy", "refuse", "substitute_stratum"),
    CoverageCase("fold_under_six_training_rows", "short", "publish"),
    CoverageCase("fold_zero_residual_variance", "flat", "publish"),
    CoverageCase("fold_spurious_score_zero_variance", "flat", "refuse", "fabricated_flat_score"),
    CoverageCase("absent_final_a9_earlier_exclusion", "absent", "publish"),
    CoverageCase("incomplete_reconciled_uncoded_turn", "eligible", "structural", "uncoded_no_s_turn"),
    CoverageCase("incomplete_hot_same_codes", "hot_unbalanced", "structural"),
    CoverageCase("eligible_reconciled_no_s", "eligible", "publish"),
    CoverageCase("incomplete_per_turn_token_counts", "unbalanced", "structural"),
)


def prepare(root, kind):
    manifest = fx.series.candidate()
    roster = ids(manifest)
    members = {int(run[-2:]): cond for run, window, pair, cond in roster if (window, pair) == ("T3", PAIR)}
    benign = sorted(o for o, cond in members.items() if cond == "benign")
    target = ROLE["instructed" if kind == "instructed" else "benign"]
    assert (len(members), benign[0]) == (8, ROLE["benign"])
    missing = {}
    if kind in {"eligible", "instructed", "two_benign", "short", "hot_unbalanced"}:
        hot = {"eligible": [target], "hot_unbalanced": [target], "instructed": [target], "two_benign": benign[:2],
               "short": benign[1:]}[kind]
        missing.update({i: (NO_ROWS, CODES) for i in hot})
    if kind == "short":
        missing.update({o: (SHORT, None) for o in (target, ROLE["instructed"])})
    if kind == "flat":
        missing[target] = (FLAT, None)

    write_bundle, describe = fx.write_bundle, fx.describe

    def bundle(path, window, assignment, signal, **kwargs):
        ordinal = assignment["ordinal"]
        affected = (window, assignment["pair"]) == ("T3", PAIR)
        if kind == "flat" and affected:
            # All seven training members have exactly the same three energies
            # at three linearly independent designs. Held target differs.
            signal = 4 if ordinal == target else 1
        run = write_bundle(path, window, assignment, signal, **kwargs)
        if not affected:
            return run
        if missing.get(ordinal, (None,))[0] == NO_ROWS or (kind == "mixed" and ordinal == target):
            journal = path / "outputs/align_thermal.jsonl"
            records = [json.loads(s) for s in journal.read_text().splitlines()]
            for row in records:
                if kind != "mixed" or row["monotonic_ns"] >= 30 * fx.NS:
                    row["status"]["os_level"] = 1
            fx.write_jsonl(journal, records)
        if kind in {"unbalanced", "hot_unbalanced"} and ordinal == target:
            # Move one event between turns before signing. The total is still
            # 30 and each turn still has decode events and a first-token stamp.
            events = path / "events.jsonl"
            records = [json.loads(s) for s in events.read_text().splitlines()]
            origin = 1 if kind == "hot_unbalanced" else 0
            row = next(r for r in reversed(records) if r["event_type"] == "token"
                       and r["metadata"]["align_turn_index"] == origin)
            row["metadata"]["align_turn_index"] = origin + 1
            row["timestamp_s"] = 26.99 + 10 * origin
            fx.write_jsonl(events, records)
        return run

    def record(path, relative, value, **kwargs):
        if kind == "absent" and relative == "records/T3/pilot.json":
            # Keep the required full thermal roster. Only the earlier A9
            # exclusion on the uncaptured target changes before signing.
            rows = value["extra_checks"]["thermal"]["members"]
            target_row, = [m for m in rows if m["id"] == f"synthetic-T3-{target:02d}"]
            assert target_row["excluded"] and target_row["calibration_exclusions"] == ["member.not_captured"]
            target_row["calibration_exclusions"] = ["X5"]
        return describe(path, relative, value, **kwargs)

    with patch.object(fx, "write_bundle", bundle), patch.object(fx, "describe", record):
        world = make_world(root, "benign_excluded" if kind == "absent" else "benign_ordinary")
    directory = root / "series/restored/T3/runs"
    observations = {}
    for ordinal in members:
        path = directory / f"synthetic-T3-{ordinal:02d}"
        if kind == "absent" and ordinal == target:
            assert not path.exists()
            continue
        turns = json.loads((path / "outputs/align_episode.json").read_text())["turns"]
        tokens = collections.Counter(r["metadata"]["align_turn_index"]
            for line in (path / "events.jsonl").read_text().splitlines()
            if (r := json.loads(line))["event_type"] == "token")
        logged = [t["decode_tokens"] for t in turns]
        actual = [tokens[t["index"]] for t in turns]
        assert logged == [6, 10, 14] and all(t["first_token_ns"] is not None for t in turns)
        expected_tokens = logged
        if ordinal == target:
            expected_tokens = {"unbalanced": [5, 11, 14], "hot_unbalanced": [6, 9, 15]}.get(kind, logged)
        assert actual == expected_tokens
        built, _ = fx.read_restored_fixture_rows(path)
        codes = [dict(r) for r in built.no_row]
        row_turns = [row.turn for row in built.rows]
        assert sorted(row_turns + [r["turn"] for r in codes]) == [0, 1, 2]
        if missing.get(ordinal, (None,))[0] == NO_ROWS:
            assert [r["reason"] for r in codes] == CODES and not row_turns
        elif kind == "mixed" and ordinal == target:
            assert row_turns == [0, 1] and codes == [{"turn": 2, "reason": "start_out_of_state"}]
        elif not (kind == "unbalanced" and ordinal == target):
            assert row_turns == [0, 1, 2] and not codes
        observations[ordinal] = dict(tokens=actual, logged=logged, rows=row_turns, no_row=codes)
    world.update(target=f"synthetic-T3-{target:02d}", missing=missing, projections=observations)
    return world


class Coverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        work = tempfile.TemporaryDirectory(prefix="c1-rl191-")
        cls.addClassCleanup(work.cleanup)
        cls.base = Path(work.name).resolve()
        cls.worlds = {}

    def check_case(self, case):
        if case.world not in self.worlds:
            self.worlds[case.world] = prepare(self.base / case.world, case.world)
        world = self.worlds[case.world]
        with tempfile.TemporaryDirectory(dir=self.base) as tmp:
            output, witness = [Path(tmp) / p for p in ("report.json", "trace.json")]
            cmd = [sys.executable, "-B", str(Path(__file__).resolve()), "--rl191-probe",
                   str(fx.SCRIPT), str(world["root"]), str(output), str(witness), world["target"], case.fault]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=fx.ROOT)
            self.assertTrue(witness.is_file(), result.stderr)
            trace = json.loads(witness.read_text())
            made = os.path.lexists(output)
            report = json.loads(output.read_text())["rl176"] if made else None
            evidence = os.environ.get("C1_V3_EVIDENCE")
            if evidence:
                dest = Path(evidence)
                dest.mkdir(exist_ok=True, parents=True)
                (dest / (case.name + ".json")).write_text(json.dumps(dict(case=case.name,
                    expected=case.result, exit=result.returncode, report=made, trace=trace,
                    projections=world["projections"], stdout=result.stdout, stderr=result.stderr,
                    S=report["S"]["attrition"] if report else None,
                    Q=report["q"]["entering_members_by_stratum"] if report else None), sort_keys=True))
            self.assertEqual(trace["errors"], [])
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(result.stdout, "")
            if case.fault != "none":
                self.assertTrue(trace["injections"], f"{case.fault} was never delivered to the caller")
                self.assertEqual(set(trace["injections"]), {case.fault})
            absent = case.world == "absent"
            self.assertTrue(trace["a9"])
            self.assertTrue(all(a9 == dict(captured=not absent, eligible=not absent,
                reasons=["X5"] if absent else []) for a9 in trace["a9"]), trace["a9"])
            counts = collections.Counter(trace["counts"])
            if case.result != "publish":
                self.assertEqual((result.returncode, made, counts["output_open"], counts["write_json_once"]),
                                 (1, False, 0, 0), f"release accepted {case.name}")
                if case.result == "structural":
                    self.assertEqual([counts[k] for k in ("_series_prints", "_decode_scores", "_s_rank",
                                                          "_tail_test")], [0, 0, 0, 0])
                return
            self.assertEqual((result.returncode, made), (0, True), result.stderr)
            self.assertEqual((counts["output_open"], counts["write_json_once"]), (1, 1))
            if absent:
                self.assertEqual((counts["read_target"], trace["builder"], trace["opened"]), (0, [], []))
            else:
                self.assertEqual(counts["read_target"], 1)
                projection = world["projections"][int(world["target"][-2:])]
                self.assertEqual(trace["builder"], [dict(rows=projection["rows"], no_row=projection["no_row"])])
            self.check_population(world, case, trace, report)

    def check_population(self, world, case, trace, report):
        attr = report["S"]["attrition"]
        missing = {("T3", PAIR, o): value for o, value in world["missing"].items()}
        check_entries(self, attr, missing)
        absent = case.world == "absent"
        excluded = [{"window": "T3", "pair": PAIR, "ordinal": ROLE["benign"],
                     "decision": "excluded", "reason": "X5"}] if absent else []
        self.assertEqual(attr["uncaptured_assignments"], excluded)
        scores, q_groups, s_groups = set(), collections.defaultdict(set), collections.defaultdict(set)
        eligible_tally, score_tally = collections.Counter(), collections.Counter()
        for run, window, pair, condition in world["roster"]:
            if absent and run == world["target"]:
                continue
            key = window, pair
            q_groups[key].add(run)
            eligible_tally[pair, condition] += 1
            if (window, pair, int(run[-2:])) not in missing:
                s_groups[key].add(run)
                scores.add(run)
                score_tally[pair, condition] += 1
        included = set()
        for run, window, pair, condition in world["roster"]:
            if condition == "sabotage" and run in scores and len(s_groups[window, pair]) > 1:
                included.add((window, pair))
        self.assertEqual(trace["scored"], [sorted(scores)])
        for key in eligible_tally:
            tally = attr["by_pair_and_condition"][key[0]][key[1]]
            self.assertEqual((tally["eligible"], tally["with_score"]), (eligible_tally[key], score_tally[key]))
        self.assertCountEqual([sorted(g) for g in trace["s_groups"]], [sorted(s_groups[k]) for k in included])
        self.assertCountEqual([sorted(g) for g in trace["q_groups"]], [sorted(g) for g in q_groups.values()])
        self.assertEqual(report["S"]["strata"], len(included))
        decisions = attr["instructed_assignments"]
        self.assertCountEqual([(r["window"], r["pair"]) for r in decisions if r["included"]], included)
        for row in decisions:
            if (row["window"], row["pair"]) not in included:
                self.assertEqual(row["reason"], "s_score_undefined")
        q = report["q"]
        counts = {(w, p): n for w, pairs in q["entering_members_by_stratum"].items() for p, n in pairs.items()}
        self.assertEqual(counts, {k: len(group) for k, group in q_groups.items()})
        if case.world != "flat":
            self.assertEqual(q["pooled_nominal"]["p_two_sided"], float(q_card("benign", not absent)))
        if case.world in {"flat", "short"}:
            training = 21 if case.world == "flat" else 3
            self.assertTrue(trace["fits"])
            self.assertTrue(all(f == dict(held_rows=3, training_rows=training, defined=False)
                                for f in trace["fits"]))


def bind(case):
    def test(self):
        self.check_case(case)
    return test


for case in COVERAGE_CASES:
    setattr(Coverage, "test_" + case.name, bind(case))


if __name__ == "__main__":
    unittest.main()
