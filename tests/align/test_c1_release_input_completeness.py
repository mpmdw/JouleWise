"""Frozen C1 release acceptance matrix. Run with the release checkout on PYTHONPATH.

All measurement roots are new temporary Git fixtures. No capture locator is
followed. The observer runs the CLI as __main__ in a fresh interpreter and
only inspects arguments/yields of the registered S scorer.
"""

from collections import Counter
from dataclasses import dataclass
import bz2
import gzip
import hashlib
import json
import lzma
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


# Frozen scoring surface of the released layout, independent of the caller's
# current lookup table. Include optional files only in contexts that admit them.
CLASSES = {
    "config": "config.json",
    "metadata": "metadata.json",
    "episode": "outputs/align_episode.json",
    "rails": "outputs/align_soc_rails.csv",
    "pm_rows": "outputs/align_s_pm_rows.json",
    "events": "events.jsonl",
    "runtime": "outputs/align_runtime_events.jsonl",
    "thermal": "outputs/align_thermal.jsonl",
    "turns": "outputs/align_turns.jsonl",
    "benign_dc": "outputs/align_dc_in.json",
    "window_journal": "archive/align_s_hazard.jsonl",
}
CODECS = ("zst", "gz", "bz2", "xz")
MUTATIONS = (
    "delete", "delete_after_finalization", "case_listed_delete_after_finalization",
    "empty", "truncate", "unreadable", "chmod_000", "symlink", "hardlink",
    "case_listed", "case_rename_after_finalization",
    *("compressed_" + ext for ext in CODECS),
    *("case_compressed_" + ext for ext in CODECS),
    "digest_one_byte", "extra_unlisted", "zero_rows",
)


def read_json(path):
    return json.loads(path.read_bytes())


def flipped_name(path):
    return path.with_name(path.name[0].upper() + path.name[1:])


def rename_exact(path, dest):
    # Force an actual directory-entry spelling change on case-folding APFS.
    staging = path.with_name("rename-in-progress")
    path.rename(staging)
    staging.rename(dest)
    names = os.listdir(dest.parent)
    if dest.name not in names or path.name in names:
        raise AssertionError(f"case rename failed: {names}")


def compressed(raw, ext):
    if ext == "zst":
        # RFC 8878 single-segment frame, four-byte content size, one raw block.
        # This is a lossless .zst even on Python versions without compression.zstd.
        if len(raw) > 128 * 1024:
            raise ValueError("fixture exceeds the single raw block size")
        return (bytes.fromhex("28 b5 2f fd a0") + len(raw).to_bytes(4, "little")
                + (len(raw) * 8 + 1).to_bytes(3, "little") + raw)
    return {"gz": gzip.compress, "bz2": bz2.compress, "xz": lzma.compress}[ext](raw)


def zero_rows(kind, path):
    """Parseable zero observations, or an empty object for the two metadata inputs."""
    if kind in ("events", "runtime"):
        # Valid, nonempty journal with every prefill and no decode tokens.
        records = [json.loads(line) for line in path.read_bytes().splitlines()]
        prefill = [row for row in records if row.get("event_type") == "phase_end"]
        if not prefill or len(prefill) == len(records):
            raise AssertionError("token-bearing stream required")
        path.write_text("".join(json.dumps(row) + "\n" for row in prefill))
    elif kind == "episode":
        episode = read_json(path)
        episode["turns"] = []
        path.write_text(json.dumps(episode))
    elif kind == "benign_dc":
        dc = read_json(path)
        dc["trace"].update(t_ns=[], values=[])
        path.write_text(json.dumps(dc))
    elif kind == "rails":
        path.write_bytes(path.read_bytes().splitlines(keepends=True)[0])
    elif kind == "pm_rows":
        path.write_bytes(b"[]\n")
    elif kind in ("config", "metadata"):
        path.write_bytes(b"{}\n")
    else:
        path.write_bytes(b"\n\n")  # nonzero byte count, zero JSONL records


@dataclass
class Input:
    member: Path
    path: Path
    donor: Path


def populate(window, fixture_scratch):
    """Extend the stock C8 fixture before it is finalized, including both token sources."""
    plan = fx.series.selected(fx.series.candidate(), "C8")
    ordinals = [plan["sabotage_ordinals"][pair] for pair in fx.series.PAIRS]
    benign = [a["ordinal"] for a in plan["members"]
              if a["ordinal"] in fx.series.FRESH_ORDINALS and a["condition"] == "benign"]

    def member(ordinal):
        return window / "runs" / f"synthetic-C8-{ordinal:02d}"

    instructed, fallback, benign_member, donor = map(member, [*ordinals, *benign[:2]])
    runtime = fallback / CLASSES["runtime"]
    (fallback / CLASSES["events"]).rename(runtime)
    (fallback / CLASSES["events"]).write_text('{"event_type":"synthetic_start"}\n')
    fx.write_json(benign_member / CLASSES["benign_dc"], {"trace": {
        "source": "wall_meter", "channel": "dc_in", "clock_domain": "synthetic-monotonic",
        "t_ns": [t * fx.NS for t in range(5, 41)], "values": [2.0] * 36,
        "nominal_interval_ns": fx.NS, "unit": "W",
    }})
    journal = window / CLASSES["window_journal"]
    journal.parent.mkdir()
    fx.write_jsonl(journal, [{"kind": "reading", "finished": {"monotonic_ns": 12 * fx.NS},
                              "values": {"level": 0}}])

    owners = {"runtime": fallback, "benign_dc": benign_member, "window_journal": window}
    refs = donor / "synthetic-reference-copies"
    refs.mkdir()
    inputs = {}
    for kind, relative in CLASSES.items():
        owner = owners.get(kind, instructed)
        primary = owner / relative
        reference = (fixture_scratch if kind == "benign_dc" else refs) / kind
        # Independent inodes and equal bytes: link cases cannot pass merely by
        # detecting a size/digest mismatch.
        reference.write_bytes(primary.read_bytes())
        inputs[kind] = Input(owner, primary, reference)
    inputs["benign_events"] = Input(benign_member, benign_member / CLASSES["events"], refs / "events")
    return inputs


def before_inventory(kind, mutation, path):
    """Return the exact physical name that the real finalizer must record."""
    if mutation in ("case_listed", "case_listed_delete_after_finalization"):
        destination = flipped_name(path)
        rename_exact(path, destination)
        return destination
    if mutation.startswith(("compressed_", "case_compressed_")):
        ext = mutation.rsplit("_", 1)[1]
        base = flipped_name(path) if mutation.startswith("case_") else path
        destination = base.with_name(base.name + "." + ext)
        destination.write_bytes(compressed(path.read_bytes(), ext))
        path.unlink()
        return destination
    if mutation == "empty":
        path.write_bytes(b"")
    if mutation == "zero_rows":
        zero_rows(kind, path)
    return path


def after_publication(kind, mutation, item, listed):
    path = item.path
    if mutation in ("delete_after_finalization", "case_listed_delete_after_finalization"):
        listed.unlink()
    elif mutation == "case_rename_after_finalization":
        rename_exact(path, flipped_name(path))
    elif mutation == "truncate":
        data = path.read_bytes()
        path.write_bytes(data[:len(data) // 2])
    elif mutation == "digest_one_byte":
        data = bytearray(path.read_bytes())
        # Keep the grammar valid when possible (JSON whitespace, CSV numeral).
        space = data.find(b" ")
        if space >= 0:
            data[space] = 9
        else:
            index = next(i for i, b in enumerate(data) if 48 <= b <= 57)
            data[index] = 48 + (data[index] - 48 + 1) % 10
        path.write_bytes(data)
    elif mutation == "chmod_000":
        path.chmod(0)
    elif mutation in ("symlink", "hardlink"):
        path.unlink()
        if mutation == "symlink":
            path.symlink_to(item.donor)
        else:
            os.link(item.donor, path)
    elif mutation == "extra_unlisted":
        parent = path.parent if kind == "window_journal" else item.member
        (parent / ("unexpected-" + path.name)).write_bytes(path.read_bytes())


def build_world(root, kind, mutation):
    finalizer = fx.harvest_offload.finalized_manifest
    describe = fx.describe
    changed = []

    def finalize(directory):
        if directory.name != "C8":
            return finalizer(directory)
        item = populate(directory, root.parent)[kind]
        listed = before_inventory("events" if kind == "benign_events" else kind, mutation, item.path)
        inventory = finalizer(directory)
        key = listed.relative_to(directory).as_posix()
        raw = listed.read_bytes()
        expected = {"size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
        if inventory["entries"].get(key) != expected:
            raise AssertionError(f"fixture did not bind {key}")
        if listed != item.path and item.path.relative_to(directory).as_posix() in inventory["entries"]:
            raise AssertionError("both physical representations were listed")
        changed.append((item, listed))
        if mutation == "delete":
            # Loss during restoration: the inventory has the canonical digest;
            # the restored bytes are gone before the fixture publishes its history.
            listed.unlink()
        return inventory

    def describe_layout(base, relative, value, **kwargs):
        if relative == fx.packet.SERIES_PATH:
            value["release_layouts"]["C8"]["hazard_journal"] = CLASSES["window_journal"]
        return describe(base, relative, value, **kwargs)

    # Only the synthetic producer is customized. Its real digests, record chain,
    # receipt, release ref and CLI verification all remain in use.
    with patch.object(fx.harvest_offload, "finalized_manifest", finalize), \
            patch.object(fx, "describe", describe_layout):
        fx.stored_series(root, wins=101)
    (item, listed), = changed
    after_publication(kind, mutation, item, listed)
    return listed


def expected_roster(root):
    """Read the frozen assignments and their stored collection/capture identities."""
    expected = {}
    manifest = read_json(root / fx.seal.SERIES_MANIFEST)
    for window in manifest["windows"]:
        wid = window["id"]
        if wid not in fx.WINDOWS:
            continue
        record = read_json(root / "records" / wid / "record.json")
        plan = read_json(root / record["sources"]["collection_plan"]["path"])
        plan_ids = {m["ordinal"]: m["run_id"] for m in plan["members"]}
        for member in window["members"]:
            if member["ordinal"] in fx.series.FRESH_ORDINALS:
                run_id = plan_ids[member["ordinal"]]
                if not record["captures"][run_id] or run_id in expected:
                    raise AssertionError(f"invalid synthetic capture: {run_id}")
                expected[run_id] = (wid, member["pair"], member["condition"])
    return expected


def observe_cli(script, root, output, observation, denied_path):
    """Execute the real CLI and observe the pooled S rank and its contributing rows."""
    ranked = []
    entering = []
    errors = []
    denied = []

    def observe(frame, event, value):
        name = frame.f_code.co_name
        if name not in ("_tail_test", "_entering_members") or frame.f_globals["__name__"] != SCORER:
            return
        try:
            parent = frame.f_back
            if name == "_tail_test":
                if event == "call" and parent.f_code.co_name == "_s_rank" and parent.f_locals["decide"]:
                    ranked.append([1 + len(others) for _, others in frame.f_locals["strata"]])
            elif event == "return" and value is not None:
                # _entering_members is shared by Q, descriptive splits, and S.
                # Only yields used to form the decisive pooled S input count.
                while parent and parent.f_globals.get("__name__") == SCORER:
                    if parent.f_code.co_name == "splits" and parent.f_locals["decide"]:
                        instructed, benign = value
                        group = []
                        for obs, _ in [instructed, *benign]:
                            group.append([obs.episode.episode_id, obs.member.window, obs.pair,
                                          obs.episode.condition, len(obs.decode_rows)])
                        entering.append(group)
                        break
                    parent = parent.f_back
        except Exception as exc:
            errors.append(repr(exc))

    if denied_path:
        # Inject a real EACCES at the open boundary, also for a privileged test
        # user. All other opens (including equal basenames) proceed normally.
        target = Path(denied_path)
        identity = target.stat()
        real_open = os.open

        def fail_read():
            denied.append(True)
            raise PermissionError(13, "synthetic unreadable input", str(target))

        def open_at(path, flags, mode=0o777, *, dir_fd=None):
            if dir_fd is not None and os.fsdecode(path).rsplit("/", 1)[-1] == target.name:
                stat = os.stat(path, dir_fd=dir_fd, follow_symlinks=False)
                if os.path.samestat(identity, stat):
                    fail_read()
            return real_open(path, flags, mode, dir_fd=dir_fd)

        def audit(event, args):
            if event == "open" and isinstance(args[0], (str, bytes)):
                if os.path.abspath(os.fsdecode(args[0])) == str(target):
                    fail_read()

        os.open = open_at
        sys.addaudithook(audit)

    sys.argv = [script, "--measurement-root", root, "--output", output]
    sys.setprofile(observe)
    try:
        runpy.run_path(script, run_name="__main__")
    finally:
        sys.setprofile(None)
        Path(observation).write_text(json.dumps({
            "ranked": ranked, "entering": entering, "errors": errors, "denied": bool(denied),
        }))


SCORER = "joulewise.align.apple.rl176"

# Keep fixture imports out of the fresh CLI process (the CLI authenticates its
# import closure and rejects first-party modules preloaded by another loader).
if __name__ == "__main__" and sys.argv[1:2] == ["--observe-cli"]:
    observe_cli(*sys.argv[2:])
    sys.exit(0)

from tests.align import test_align_v4_series_release as fx


class C1ReleaseCompleteness(unittest.TestCase):
    def check_world(self, kind, mutation):
        with tempfile.TemporaryDirectory(prefix="c1-acceptance-") as tmp:
            directory = Path(tmp).resolve()
            root = directory / "synthetic"
            root.mkdir()
            listed = build_world(root, kind, mutation)
            expected = expected_roster(root)
            sizes = Counter((w, p) for w, p, _ in expected.values())
            self.assertEqual((len(sizes), len(expected), set(sizes.values())), (22, 176, {8}))
            output = directory / "release.json"
            witness = directory / "scorer-observation.json"
            result = subprocess.run(
                [sys.executable, "-B", str(Path(__file__).resolve()), "--observe-cli", str(fx.SCRIPT),
                 str(root), str(output), str(witness), str(listed) if mutation == "unreadable" else ""],
                cwd=fx.ROOT, capture_output=True, text=True,
            )
            self.assertTrue(witness.is_file(), result.stderr)
            observed = read_json(witness)
            self.assertEqual(observed["errors"], [])
            if mutation == "unreadable":
                self.assertTrue(observed["denied"], "targeted EACCES never occurred")

            written = os.path.lexists(output)
            failures = []
            if written:
                score = read_json(output)[fx.seal.RL176]["S"]
                ranks = observed["ranked"]
                groups = observed["entering"]
                members = {run: (w, p, condition) for group in groups
                           for run, w, p, condition, rows in group if rows > 0}
                paired = Counter((group[0][1], group[0][2]) for group in groups)
                exact_groups = all(
                    len({(w, p) for _, w, p, _, _ in group}) == 1
                    and Counter(row[3] for row in group) == {"sabotage": 1, "benign": 7}
                    for group in groups
                )
                if (len(ranks) != 1 or ranks[0] != [len(group) for group in groups]
                        or len(ranks[0]) != len(sizes) or score["strata"] != len(sizes)
                        or paired != Counter(sizes.keys()) or not exact_groups
                        or members != expected or sum(map(len, groups)) != len(expected)):
                    failures.append(f"rank invariant: ranked={list(map(len, ranks))}, "
                                    f"contributors={len(members)}/{len(expected)}, "
                                    f"missing={sorted(expected.keys() - members.keys())}")
                if mutation == "control":
                    self.assertEqual(score["words"], ["S INCONCLUSIVE"])
                    self.assertEqual(score["windows"], 11)
                    self.assertAlmostEqual(154 * score["theta"], 101, places=11)
                else:
                    failures.append(f"report written: {score['words']}, {score['strata']} strata")
            if mutation == "control":
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(written, "intact release did not write a report")
            elif result.returncode <= 0:
                failures.append(f"expected refusal, exit={result.returncode}")
            self.assertFalse(failures, " | ".join(failures))

    def test_intact_control(self):
        self.check_world("events", "control")

    def test_benign_zero_rows_with_all_strata_still_present(self):
        self.check_world("benign_events", "zero_rows")


def matrix_test(kind, mutation):
    def test(self):
        self.check_world(kind, mutation)
    test.__name__ = f"test_{kind}__{mutation}"
    return test


for _kind in CLASSES:
    for _mutation in MUTATIONS:
        _test = matrix_test(_kind, _mutation)
        setattr(C1ReleaseCompleteness, _test.__name__, _test)


if __name__ == "__main__":
    unittest.main()
