"""Synthetic tests for the C1 caller and its stored-bundle inputs."""

import ast
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import unittest

from joulewise.align.apple import rl176, s_rows, v4_desk_seal as seal
from joulewise.align.apple.workload import read_episode_bundle
from joulewise.align.records import Episode, Turn, to_json
from scripts import align_v4_series as series


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/align_v4_series_release.py"
NS = 1_000_000_000
WINDOWS = [f"C{i}" for i in range(1, 9)] + [f"T{i}" for i in range(1, 4)]

# Capture reads under the measurement root from before the script's imports.
# The output is a sibling of that root.
OBSERVE_OPENS = """
import os
import runpy
import sys

allowed = set(sys.argv.pop(1).split(os.pathsep))
script, _, root, _, _ = sys.argv[1:]

def observe(event, args):
    if event == "subprocess.Popen":
        raise AssertionError("release tried to resolve a repository")
    if event != "open" or not isinstance(args[0], (str, bytes)):
        return
    path = os.path.abspath(os.fsdecode(args[0]))
    relative = os.path.relpath(path, root)
    if relative != ".." and not relative.startswith("../") and relative not in allowed:
        raise AssertionError("protected read: " + relative)

sys.addaudithook(observe)
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
"""


def write_json(path, value):
    path.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")


def write_jsonl(path, values):
    path.write_text("".join(json.dumps(value) + "\n" for value in values), encoding="utf-8")


def write_release_context(root):
    """Write the guard's public schemas, without asserting owner provenance."""
    manifest = root / seal.SERIES_MANIFEST
    manifest.parent.mkdir(parents=True)
    manifest.write_bytes(series.raw_json(series.candidate()))
    complete = root / seal.SERIES_COMPLETE
    write_json(complete, {
        "schema": seal.SERIES_COMPLETE_SCHEMA,
        "event": "series_complete",
        "last_admitted_test_window": "T3",
        "test_windows_final_eligibility": dict.fromkeys(("T1", "T2", "T3"), "final"),
        "series_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "record_commit": "a" * 40,
    })
    write_json(root / seal.RELEASE_RECEIPT, {
        "schema": seal.RELEASE_RECEIPT_SCHEMA,
        "release_run": True,
        "series_complete_sha256": hashlib.sha256(complete.read_bytes()).hexdigest(),
        "ruling": "RL-999 synthetic guard fixture",
        "lead_signature": "lead: synthetic 2026-11-18",
    })


def invoke(root, output, *, observe=False):
    command = [sys.executable, "-B", str(SCRIPT), "--measurement-root", str(root), "--output", str(output)]
    if observe:
        allowed = ":".join((seal.SERIES_MANIFEST, seal.SERIES_COMPLETE, seal.RELEASE_RECEIPT))
        command[2:2] = ["-c", OBSERVE_OPENS, allowed]
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)


def write_bundle(bundle, window, assignment, signal):
    """Use the public episode, controller trace, event and PM schemas."""
    outputs = bundle / "outputs"
    outputs.mkdir(parents=True)
    (bundle / "raw").mkdir()
    episode_id = f"synthetic-{window}-{assignment['ordinal']:02d}"
    turns = tuple(
        Turn(index, start * NS, (start + 7) * NS, context, prefill, decode,
             first_token_ns=(start + 1) * NS)
        for index, (start, context, prefill, decode) in enumerate((
            (10, 0, 50, 6), (20, 56, 15, 10), (30, 81, 45, 14),
        ))
    )
    # The local and controller clocks share an origin in these synthetic records.
    clock = [{
        "epoch_ns": t, "monotonic_before_ns": t, "monotonic_after_ns": t,
        "wall_resolution_ns": 1, "monotonic_resolution_ns": 1,
    } for t in (turns[0].start_ns, turns[-1].end_ns)]
    episode = Episode(
        episode_id, "shade/" + assignment["pair"], assignment["condition"],
        assignment["model_id"], "synthetic", assignment["episode_seed"],
        "synthetic-monotonic", turns[0].start_ns, turns[-1].end_ns, turns,
        hardware={"paired_clock_stamps_ns": clock},
    )
    (outputs / "align_episode.json").write_text(to_json(episode), encoding="utf-8")
    (bundle / "config.json").write_bytes((ROOT / "configs/examples/mock_local.json").read_bytes())
    write_json(bundle / "metadata.json", {"run_id": episode_id})
    events = []
    for turn in turns:
        first_s = turn.first_token_ns / NS
        tag = {"align_turn_index": turn.index}
        events.append({"event_type": "phase_end", "phase": "prefill", "timestamp_s": first_s, "metadata": tag})
        events.extend(
            {"event_type": "token", "phase": "decode", "timestamp_s": first_s + 6 * i / turn.decode_tokens,
             "metadata": tag}
            for i in range(turn.decode_tokens)
        )
    write_jsonl(bundle / "events.jsonl", events)
    write_jsonl(outputs / "align_turns.jsonl", (
        {"turn": turn.index, "generation": {"finish_reason": "stop"}} for turn in turns
    ))
    times = range(5, 41)
    write_jsonl(outputs / "align_thermal.jsonl", (
        {"kind": "sample", "monotonic_ns": t * NS,
         "status": {"os_level": 0, "pm_state": "Nominal", "pm_observed_ns": t * NS}}
        for t in times
    ))
    write_jsonl(bundle / "rich_telemetry.jsonl", (
        {"timestamp_s": t, "gpu": {"dvfm_states": [{"freq": 1400, "used_ns": NS}]}}
        for t in times
    ))
    plist = plistlib.dumps({
        "timestamp": datetime(2000, 1, 1), "elapsed_ns": NS, "thermal_pressure": "Nominal",
        "processor": {"cpu_power": 1000, "gpu_power": 1000, "ane_power": 1000,
                      "cpu_energy": 1000, "gpu_energy": 1000, "ane_energy": 1000},
    })
    (bundle / "raw/powermetrics.plist").write_bytes(b"\0".join(plist for _ in times))
    with (bundle / "power_trace.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(("timestamp_s", "power_w", "source", "rail", "interval_start_s", "interval_end_s"))
        for t in times:
            # Only decode varies across members. All three turn designs are
            # repeated across a stratum, so signal order gives the rank target.
            decode_turn = next((turn for turn in turns if turn.first_token_ns < t * NS <= turn.end_ns), None)
            watts = 2 if decode_turn is None else 10 + decode_turn.index + signal
            writer.writerow((t, watts, "powermetrics", "gpu_power", t - 1, t))
    return episode_id


def write_boundary_bundles(root, wins):
    """Keep assignment and design fixed while exchanging the last adjacent signals."""
    write_release_context(root)
    manifest = series.load(root)
    targets = [7] * 14 + [0] * 7 + [wins - 98]
    for window_index, window in enumerate(WINDOWS):
        selected = series.selected(manifest, window)
        for pair_index, pair in enumerate(series.PAIRS):
            choices = [a for a in selected["members"]
                       if a["ordinal"] in series.FRESH_ORDINALS and a["pair"] == pair]
            target = targets[2 * window_index + pair_index]
            benign_signals = iter(s for s in range(8) if s != target)
            for assignment in choices:
                signal = target if assignment["condition"] == "sabotage" else next(benign_signals)
                bundle = root / "bundles" / window / str(assignment["ordinal"])
                episode_id = write_bundle(bundle, window, assignment, signal)
                yield window, bundle, episode_id


class SeriesReleaseTests(unittest.TestCase):
    def test_script_passes_literal_q_words_frozen_true(self):
        tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
        calls = [
            node for node in ast.walk(tree) if isinstance(node, ast.Call) and (
                isinstance(node.func, ast.Attribute) and node.func.attr == "series_release_prints"
                or isinstance(node.func, ast.Name) and node.func.id == "series_release_prints"
            )
        ]
        self.assertEqual(len(calls), 1)
        keyword, = (kw for kw in calls[0].keywords if kw.arg == "q_words_frozen")
        self.assertIsInstance(keyword.value, ast.Constant)
        self.assertIs(keyword.value.value, True)

    def test_unreleased_or_invalid_series_opens_no_loader_and_writes_no_outcome(self):
        withheld = {seal.RL176: dict.fromkeys(rl176.RELEASE_LEAVES, seal.WITHHELD)}
        cases = {
            "missing completion": (seal.SERIES_COMPLETE, None),
            "stale completion": (seal.SERIES_COMPLETE, {"record_commit": "b" * 40}),
            "malformed completion": (seal.SERIES_COMPLETE, {}),
            "missing receipt": (seal.RELEASE_RECEIPT, None),
            "tampered receipt": (seal.RELEASE_RECEIPT, {"release_run": False}),
            "missing manifest": (seal.SERIES_MANIFEST, None),
            "tampered manifest": (seal.SERIES_MANIFEST, {}),
            "format-only authorization for nonexistent commit": (None, None),
        }
        for name, (path, replacement) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "series"
                output = Path(tmp) / "report.json"
                write_release_context(root)
                if path and replacement is None:
                    (root / path).unlink()
                elif replacement:
                    before = json.loads((root / path).read_bytes())
                    write_json(root / path, {**before, **replacement})
                elif path:
                    write_json(root / path, replacement)
                result = invoke(root, output, observe=True)
                self.assertNotIn("protected read", result.stderr)
                self.assertNotIn("tried to resolve a repository", result.stderr)
                if path is None:
                    self.assertIsNone(seal.release_error(root))
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertFalse(output.exists())
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(json.loads(output.read_bytes()), withheld)
                self.assertEqual(result.stdout, "")

    def test_unreleased_cli_creates_only_a_new_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "series"
            root.mkdir()
            output = Path(tmp) / "report.json"
            created = invoke(root, output)
            self.assertEqual(created.returncode, 0, created.stderr)
            withheld = {seal.RL176: dict.fromkeys(rl176.RELEASE_LEAVES, seal.WITHHELD)}
            self.assertEqual(json.loads(output.read_bytes()), withheld)
            original = output.read_bytes()
            refused = invoke(root, output)
            self.assertNotEqual(refused.returncode, 0, refused.stdout)
            self.assertEqual(output.read_bytes(), original)

    def test_synthetic_stored_bundle_worlds_reproduce_the_s_boundary(self):
        """Validate the stored inputs against both producers before the roster join exists."""
        for wins, tail in ((102, 0.0109278936864), (101, 0.0140103456299)):
            with self.subTest(wins=wins), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                members = []
                for window, bundle, episode_id in write_boundary_bundles(root, wins):
                    member_rows, _ = s_rows.read_member_rows(bundle, s_rows.REGISTERED)
                    self.assertEqual(member_rows.episode_id, episode_id)
                    self.assertEqual([row.decode_tokens for row in member_rows.rows], [6, 10, 14])
                    episode = read_episode_bundle(bundle)
                    members.append(rl176.FreshMember(window, episode, True, member_rows.rows))
                self.assertEqual(len(members), 176)
                report = rl176.series_release_prints(
                    {"measurement_root": root}, load_members=lambda: members, q_words_frozen=True,
                )[seal.RL176]
                score = report["S"]
                self.assertEqual((score["strata"], score["windows"]), (22, 11))
                self.assertAlmostEqual(154 * score["theta"], wins, places=12)
                self.assertAlmostEqual(score["p_sup"], tail, places=12)
                self.assertEqual("S SIGNATURE" in score["words"], wins == 102)


if __name__ == "__main__":
    unittest.main()
