"""Independent C1 v3 acceptance. Only private TemporaryDirectory Git worlds are accepted.

Run under unittest with the composed public source checkout on PYTHONPATH. The
child executes the production file as __main__ without importing the fixtures.
C1_V3_EVIDENCE optionally names a directory for per-case synthetic observations.
"""
import collections
from contextlib import contextmanager
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
import math
import os
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
        Case(role + "_captured_candidate", role + "_candidate", cli="owner"),
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
        if case.cli == "owner":
            # The row-builder candidate is executable. Only its classification as
            # an admitted *positive* is the owner's. A refusal is recorded verbatim.
            self.assertEqual(world["candidate"]["rows"], 0)
            if result.returncode == 1:
                self.assertFalse(made)
                self.assertEqual(counts["_series_prints"], 0)
                self.assertEqual(counts["output_open"], 0)
        self.assertCountEqual([x for n,x in trace["events"] if n == "read_member"], runs)
        self.assertEqual(counts["rail_projection"], len(runs))
        self.assertEqual(counts["read_member_rows"], len(runs))
        self.assertEqual(counts["load_members_return"], 1)
        self.assertLess(names.index("load_members_return"), names.index("dc_lookup"))
        expected_benign = {run for run, _, _, condition in world["roster"] if condition == "benign"} & runs
        for name in ("bind_benign_dc", "benign_dc", "dc_lookup"):
            self.assertCountEqual([key for n,key in trace["events"] if n == name], expected_benign)
        self.assertCountEqual(trace["dc_opens"], world["allowed_dc"])
        if case.cli == "owner" and result.returncode == 1:
            self.skipTest("NEEDS_RULING: intact candidate refused; series owner must admit this input")
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
                self.skipTest("NEEDS_RULING: series owner must admit candidate and supply independent producer outputs")
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


if __name__ == "__main__":
    unittest.main()
