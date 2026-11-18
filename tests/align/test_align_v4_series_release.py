"""Synthetic tests for the C1 caller and its stored-bundle inputs."""

import ast
from contextlib import redirect_stderr
import csv
from dataclasses import replace
from datetime import datetime
import hashlib
from io import StringIO
import json
from pathlib import Path
import plistlib
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from joulewise.align.apple import harvest_offload, rl176, s_rows, v4_desk_seal as seal
from joulewise.align.apple import v4_registration as registration
from joulewise.align.apple.workload import read_episode_bundle
from joulewise.align.records import Episode, Turn, to_json
from scripts import align_v4_series as series
from scripts import align_v4_next_arm_packet as packet
from tests.align import v4_registration_fixtures
from tests.git_fixture import init_git_fixture


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
root = os.path.realpath(root)
directory_fds = {}
real_open, real_close = os.open, os.close

def check_open(path):
    relative = os.path.relpath(path, root)
    if relative not in (".", "..") and not relative.startswith("../") and relative not in allowed:
        raise AssertionError("protected read: " + relative)

def observed_open(path, flags, mode=0o777, *, dir_fd=None):
    absolute = os.path.abspath(os.path.join(directory_fds.get(dir_fd, ""), os.fsdecode(path)))
    if not flags & os.O_DIRECTORY:
        check_open(absolute)
    fd = real_open(path, flags, mode, dir_fd=dir_fd)
    if flags & os.O_DIRECTORY:
        directory_fds[fd] = absolute
    return fd

def observed_close(fd):
    directory_fds.pop(fd, None)
    real_close(fd)

def observe(event, args):
    if event == "subprocess.Popen":
        raise AssertionError("release tried to resolve a repository")
    if event != "open" or not isinstance(args[0], (str, bytes)) or args[2] & os.O_DIRECTORY:
        return
    check_open(os.path.abspath(os.fsdecode(args[0])))

os.open, os.close = observed_open, observed_close
sys.addaudithook(observe)
sys.argv = sys.argv[1:]
runpy.run_path(script, run_name="__main__")
"""


def write_json(path, value):
    path.write_text(json.dumps(value, allow_nan=False), encoding="utf-8")


def write_jsonl(path, values):
    path.write_text("".join(json.dumps(value) + "\n" for value in values), encoding="utf-8")


def write_release_context(root, *, commit="a" * 40, tests=("T1", "T2", "T3")):
    """Write the guard's public schemas, without asserting owner provenance."""
    manifest = root / seal.SERIES_MANIFEST
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_bytes(series.raw_json(series.candidate()))
    complete = root / seal.SERIES_COMPLETE
    write_json(complete, {
        "schema": seal.SERIES_COMPLETE_SCHEMA,
        "event": "series_complete",
        "last_admitted_test_window": tests[-1],
        "test_windows_final_eligibility": dict.fromkeys(tests, "final"),
        "series_manifest_sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
        "record_commit": commit,
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


def write_bundle(bundle, window, assignment, signal, *, stored_condition=None, no_rows=False,
                 hot=False, truncate=False, amount=None):
    """Use the public episode, controller trace, event and PM schemas."""
    outputs = bundle / "outputs"
    outputs.mkdir(parents=True)
    (bundle / "raw").mkdir()
    episode_id = assignment.get("run_id", f"synthetic-{window}-{assignment['ordinal']:02d}")
    turns = tuple(
        Turn(index, start * NS, (start + 7) * NS, context, prefill, decode,
             first_token_ns=(start + 1) * NS)
        for index, (start, context, prefill, decode) in enumerate((
            (10, 0, 50, 6), (20, 56, 15, 10), (30, 81, 45, 14),
        ))
    )[:2 if truncate else 3]
    # The local and controller clocks share an origin in these synthetic records.
    clock = [{
        "epoch_ns": t, "monotonic_before_ns": t, "monotonic_after_ns": t,
        "wall_resolution_ns": 1, "monotonic_resolution_ns": 1,
    } for t in (turns[0].start_ns, turns[-1].end_ns)]
    episode = Episode(
        episode_id, "shade/" + assignment["pair"], stored_condition or assignment["condition"],
        assignment["model_id"], "synthetic", assignment["episode_seed"],
        "synthetic-monotonic", turns[0].start_ns, turns[-1].end_ns, turns,
        flags=("episode.deadman:1",) if truncate else (),
        hardware={"paired_clock_stamps_ns": clock, **(
            {} if amount is None else {"task_diagnostics": {"evaluation_outputs": amount}}
        )},
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
    write_jsonl(bundle / "events.jsonl", [] if no_rows else events)
    write_jsonl(outputs / "align_turns.jsonl", (
        {"turn": turn.index, "generation": {"finish_reason": (
            "episode.deadman" if truncate and turn is turns[-1] else "stop"
        )}} for turn in turns
    ))
    times = range(5, 41)
    write_jsonl(outputs / "align_thermal.jsonl", (
        {"kind": "sample", "monotonic_ns": t * NS,
         "status": {"os_level": int(hot and 16 <= t <= 17), "pm_state": "Nominal", "pm_observed_ns": t * NS}}
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


def fixture_git(root, *args):
    return subprocess.check_output([
        "git", "-c", "user.name=Synthetic", "-c", "user.email=synthetic@example.invalid", *args,
    ], cwd=root, text=True).strip()


def commit_fixture(root, paths):
    fixture_git(root, "add", "--", *paths)
    fixture_git(root, "commit", "-qm", "synthetic release fixture")
    return fixture_git(root, "rev-parse", "HEAD")


def describe(root, relative, value, *, canonical=False):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
           if canonical else json.dumps(value).encode())
    path.write_bytes(raw)
    return {"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}


def registration_fixture(root, amount_field=None):
    for path in registration.ARTIFACTS:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("synthetic\n")
    for code in ("scripts/align_v4_series_release.py", "joulewise/align/apple/s_rows.py",
                 "joulewise/align/apple/rl176.py", "joulewise/align/apple/rl176_phases.py"):
        (root / code).write_bytes((ROOT / code).read_bytes())
    manifest = root / seal.SERIES_MANIFEST
    manifest.write_bytes(series.raw_json(series.candidate()))
    reg = registration.REGISTRATION
    gates = {stage: {"verdict": "ADMIT", **describe(root, f"docs/align/v4/{stage}.json", {"synthetic": True})}
             for stage in ("A", "B")}
    baseline = commit_fixture(root, ["configs", "scripts", "docs", "joulewise", "tests"])
    describe(root, reg + "r1_slots.json", {"executed_commit": baseline})
    export = v4_registration_fixtures.export()
    transfer = describe(root, "synthetic-transfer.json", {"transfer": "synthetic"})
    export["policy"]["transfer_justification_sha256"] = transfer["sha256"]
    source = describe(root, "synthetic-u3.json", export)
    bar = registration.derive_u3(export["pairs"], {d["path"]: d["sha256"] for d in (transfer, source)},
                                 policy=export["policy"])
    gate = {"verdict": "ADMIT", "derivation_sha256": bar["derivation_sha256"]}
    bar.update(status="registered", lead_signature="lead: synthetic 2026-11-18",
               independent_gate={**gate, **describe(root, "docs/align/v4/u3-gate.json", gate)})
    describe(root, reg + "u3_bar.json", bar)
    describe(root, reg + "battery_window_policy.json", v4_registration_fixtures.battery_policy())
    describe(root, reg + "wp19_receipt.json", {
        "schema": registration.WP19_SCHEMA, "verdict": "fail", "live_source_sha256": "a" * 64,
        "live_x_turns_compared": 0, "render_all_turns": {"X": False, "Y": False},
        "static_proof": True, "contrast_predeclared": "INCONCLUSIVE: identity broken",
    })
    signed = commit_fixture(root, ["configs", "docs", "synthetic-transfer.json", "synthetic-u3.json"])
    artifacts = {path: hashlib.sha256((root / path).read_bytes()).hexdigest()
                 for path in registration.ARTIFACTS}
    describe(root, reg + "registration_receipt.json", {
        "schema": registration.RECEIPT_SCHEMA, "status": "registered", "commit": signed,
        "lead_signature": "lead: synthetic 2026-11-18", "artifacts": artifacts, "gates": gates,
        "rulings": {str(rule): "installed" for rule in registration.RULINGS},
        **({"side_transfer_field": amount_field} if amount_field is not None else {}),
    })


def stored_series(root, *, wins=102, different=None, no_rows=False, spoof=False, history=False,
                  amount_fields=None, amount_field=None, defective_layout=False, omit_first_pm=False):
    """Synthetic committed arm history with a separate, untracked restored tree."""
    init_git_fixture(root, "-q")
    registration_fixture(root, amount_field)
    manifest = series.candidate()
    manifest_sha = hashlib.sha256(series.raw_json(manifest)).hexdigest()
    prior = None
    previous_final = None
    layouts = {}
    windows = ["W1", *WINDOWS]
    if history:
        windows[windows.index("C2"):windows.index("C3")] = ["C2", "C2#2"]
        windows.insert(windows.index("T1"), "C9")
    for window in windows:
        slot = window.split("#")[0]
        selected = series.selected(manifest, slot)
        benign_ordinals = [a["ordinal"] for a in selected["members"] if a["ordinal"] in series.FRESH_ORDINALS
                           and a["condition"] == "benign"]
        base = f"records/{window}"
        members, captures, thermal, excluded = [], {}, [], []
        empty = window in ("W1", "C2") and (history or window == "W1")
        barred = history and window == "C3"
        tests = tuple(w for w in WINDOWS if w.startswith("T"))
        window_root = root / "series/restored" / window
        window_root.mkdir(parents=True)
        if window != "W1":
            layout = "mixed" if defective_layout and window == "T3" else "powermetrics-rails-v1"
            layouts[window] = {"trace_layout": layout, "hazard_journal": None}
        signals = {}
        if slot in WINDOWS:
            i = 2 * WINDOWS.index(slot)
            targets = [7] * 14 + [0] * 7 + [wins - 98]
            signals = {pair: (targets[i+j], iter([s for s in range(8) if s != targets[i+j]]))
                       for j, pair in enumerate(series.PAIRS)}
        for assignment in selected["members"]:
            ordinal, pair, condition = (assignment[k] for k in ("ordinal", "pair", "condition"))
            run_id = f"synthetic-{window}-{ordinal:02d}"
            fresh = window != "W1" and ordinal in series.FRESH_ORDINALS
            change = fresh and (slot, pair, condition, ordinal) == different
            captured = fresh and not empty and (not change or no_rows)
            plan = {"run_id": run_id, "ordinal": ordinal, "role": "D" if fresh else "anchor",
                    "task_pair": pair, "condition": condition, "pool_role": assignment["pool"],
                    "model_id": assignment.get("model_id"), "seed_index": assignment.get("seed_index"),
                    "expected_episode_seed": assignment.get("episode_seed")}
            members.append(plan)
            ineligible = history and window == "C9" and ordinal == selected["sabotage_ordinals"][pair] if fresh else False
            codes = ["X5"] if ineligible else [] if captured else ["member.not_captured"]
            thermal.append({"id": run_id, "model": "synthetic", "gated": True, "excluded": bool(codes),
                            "calibration_exclusions": codes,
                            "flags": [], "tokens": 1 if captured else None})
            captures[run_id] = None
            if fresh and pair in signals:
                target, benign = signals[pair]
                signal = target if condition == "sabotage" else next(benign)
            else:
                signal = ordinal
            if captured:
                bundle = window_root / "runs" / run_id
                write_bundle(bundle, window, {**assignment, "run_id": run_id}, signal,
                             stored_condition="benign" if spoof and condition == "sabotage" else None,
                             no_rows=(change and no_rows) or (history and window == "C9" and ordinal == benign_ordinals[1]),
                             hot=history and window == "C9" and ordinal == benign_ordinals[2],
                             truncate=history and window == "C9" and ordinal == benign_ordinals[0],
                             amount=(amount_fields or {}).get((slot, pair, condition)))
                episode = read_episode_bundle(bundle)
                (bundle / "outputs/align_soc_rails.csv").write_bytes((bundle / "power_trace.csv").read_bytes())
                if not (omit_first_pm and window == "C1" and ordinal == series.FRESH_ORDINALS[0]):
                    write_json(bundle / "outputs/align_s_pm_rows.json", s_rows.pm_rows_with_states(bundle, episode))
                if spoof:
                    dc_file = bundle / "outputs/align_dc_in.json"
                    if condition == "sabotage":
                        dc_file.write_bytes(b"forbidden instructed fixture")
                    elif window == "C1" and ordinal == next(a["ordinal"] for a in selected["members"]
                            if a["ordinal"] in series.FRESH_ORDINALS and a["condition"] == "benign"):
                        dc = replace(episode.power_traces[0], source="wall_meter", channel="dc_in")
                        write_json(dc_file, {"trace": json.loads(to_json(dc)),
                                             "clock_mapping": json.loads(to_json(episode.clock_mappings[0]))})
                captures[run_id] = {"locator": str(bundle), "sha256": "b" * 64, "bytes": 1}
        unpacked = harvest_offload.finalized_manifest(window_root)
        frozen = describe(window_root, "finalized_manifest.json", unpacked, canonical=True)
        sources = {
            "plan": describe(root, f"{base}/plan.json", {"plan_id": window}),
            "collection_plan": describe(root, f"{base}/collection.json", {
                "members": members, "series_manifest_sha256": manifest_sha,
            }),
            "result": describe(root, f"{base}/result.json", {"verdict": "GO", "chain_exit_code": 0}),
        }
        if empty:
            sources["light_triage"] = describe(root, f"{base}/light.json", {
                "schema": packet.LIGHT_TRIAGE_SCHEMA, "window": window,
            })
        else:
            reports = {f"U{k}": {"status": "fail" if barred and k == 1 else "pass"} for k in range(1, 6)}
            sources.update({
                "desk": describe(root, f"{base}/desk.json", {"plan_id": window, "harvest_status": "ok"}),
                "pilot": describe(root, f"{base}/pilot.json", {
                    "plan_id": window, "status": "instrument_ok", "extra_checks": {"thermal": {
                        "schema": "joulewise.align.thermal_desk.v1", "members": thermal,
                        "model_windows": {f"synthetic/{window}": reports},
                    }},
                }),
                "exclusions": describe(root, f"{base}/exclusions.json", {
                    "members_excluded": excluded, "reasons": [], "claim_usable": True,
                }),
                "unpack_receipt": describe(root, f"{base}/unpack.json", {
                    "schema": "joulewise.align_v4.unpack_receipt.v1", "window": window,
                    "plan_id": window, "finalized_manifest_sha256": frozen["sha256"],
                }, canonical=True),
            })
        successor_final = previous_final
        previous_final = None
        if history and window == "C1":
            previous_final = {name: sources.pop(name) for name in packet.FINAL_SOURCES_WITH_RECEIPT}
        record = describe(root, f"{base}/record.json", {
            "schema": packet.RECORD_SCHEMA, "window": window,
            "role": "development" if window == "W1" else selected["role"],
            "previous_record": prior, "finalized_manifest": frozen["sha256"], "sources": sources,
            "captures": captures,
            **({"previous_final": {"record_sha256": prior["sha256"], "sources": successor_final}}
               if successor_final is not None else {}),
        })
        prior = {"commit": commit_fixture(root, [base]), **record}
    write_release_context(root, commit=prior["commit"], tests=tests)
    describe(root, packet.SERIES_PATH, {"schema": packet.SERIES_SCHEMA, "previous_record": prior,
                                        "release_layouts": layouts})
    tip = commit_fixture(root, [packet.SERIES_PATH, seal.SERIES_COMPLETE, seal.RELEASE_RECEIPT,
                                registration.REGISTRATION + "registration_receipt.json"])
    fixture_git(root, "update-ref", "refs/remotes/origin/align-v4-series-release", tip)
    return manifest


class SeriesReleaseTests(unittest.TestCase):
    def test_final_roster_emits_one_fresh_member_per_assignment_with_a9_and_unmodified_787_rows(self):
        from scripts import align_v4_series_release as caller

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stored_series(root, history=True)
            originals = []
            real = rl176.series_release_prints

            def observe(state, *, load_members, **kwargs):
                def load():
                    originals.extend(load_members())
                    return originals
                return real(state, load_members=load, **kwargs)

            with patch.object(rl176, "series_release_prints", side_effect=observe):
                report = caller.build_report(root)[seal.RL176]
            self.assertEqual(len(originals), 176)
            self.assertEqual(len({m.episode.episode_id for m in originals}), 176)
            self.assertNotIn("C3", {m.window for m in originals})
            self.assertIn("C9", {m.window for m in originals})
            self.assertEqual(sum(m.episode.episode_id.startswith("synthetic-C2#2-") for m in originals), 16)
            excluded = [m for m in originals if not m.eligible]
            self.assertEqual([(m.window, m.episode.condition, m.exclusion_reason) for m in excluded],
                             [("C9", "sabotage", "X5")] * 2)
            cut, empty, truncated = False, False, False
            for member in originals:
                run_id = member.episode.episode_id
                attempt = run_id.split("-")[1]
                bundle = root / "series/restored" / attempt / "runs" / run_id
                expected, _ = s_rows.read_member_rows(bundle, s_rows.REGISTERED)
                self.assertEqual(member.s_rows, expected.rows)
                cut |= any(row.cut for row in expected.rows)
                empty |= not expected.rows and member.eligible
                truncated |= expected.truncated and member.eligible
            self.assertTrue(cut and empty and truncated)
            self.assertEqual(sum(
                row["assigned"] for conditions in report["S"]["attrition"]["by_pair_and_condition"].values()
                for row in conditions.values()
            ), 176)

    def test_no_member_loader_opens_dc_and_provider_keys_on_manifest_benign_ordinals(self):
        from scripts import align_v4_series_release as caller

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = stored_series(root, spoof=True)
            trace_opens = []
            real = caller.named_bytes
            selected = series.selected(manifest, "C1")
            benign_ordinal = next(a["ordinal"] for a in selected["members"]
                                  if a["ordinal"] in series.FRESH_ORDINALS and a["condition"] == "benign")
            permitted = f"series/restored/C1/runs/synthetic-C1-{benign_ordinal:02d}/{caller.DC_FILE}"

            def observe(source_root, path):
                self.assertFalse(path.endswith("power_trace.csv"), "generic bundle trace read")
                if path.endswith(caller.DC_FILE):
                    self.assertEqual(path, permitted)
                    self.assertEqual(source_root, root.resolve())
                    trace_opens.append(path)
                return real(source_root, path)

            accepted = root / "report.json"
            with patch.object(caller, "named_bytes", side_effect=observe):
                self.assertEqual(caller.main(["--measurement-root", str(root), "--output", str(accepted)]), 0)
            self.assertEqual(len(trace_opens), 1)
            report = json.loads(accepted.read_bytes())[seal.RL176]
            self.assertIn("dc_in", report["aligned_power"]["profiles"])
            metadata = {path: (root / path).read_bytes() for path in caller.RELEASE_METADATA}
            inputs = caller.ReleasedInputs(root.resolve(), metadata)
            with patch.object(caller, "named_bytes", side_effect=observe):
                members = inputs.load_members()
            self.assertEqual(len(trace_opens), 1)
            instructed = next(m.episode for m in members if m.episode.condition == "sabotage")
            key = inputs.member_keys[instructed.episode_id][0]
            other_pair = next(pair for pair in series.PAIRS if pair != key[1])
            with patch.object(caller.RestoredFiles, "bundle", side_effect=AssertionError("unexpected resolution")):
                for bad in (key, (key[0], other_pair, key[2]), ("T5", key[1], key[2])):
                    with self.assertRaises((ValueError, KeyError)):
                        inputs.benign_dc(bad)
                for bad in (replace(instructed, condition="benign"), replace(instructed, episode_id="unknown")):
                    with self.assertRaises((ValueError, KeyError)):
                        inputs.load_benign_dc(bad)
            corrupted = root / "series/restored/C1/runs" / instructed.episode_id / caller.RAIL_FILE
            with corrupted.open("ab") as stored:
                stored.write(b"changed after finalization\n")
            partial = root / "partial.json"
            with patch.object(caller, "named_bytes", side_effect=observe), self.assertRaises(SystemExit) as refusal:
                caller.main(["--measurement-root", str(root), "--output", str(partial)])
            self.assertEqual(refusal.exception.code, 1)
            self.assertEqual(len(trace_opens), 1)
            self.assertFalse(partial.exists())

    def test_side_transfer_uses_only_named_frozen_numeric_evaluator_field(self):
        from scripts import align_v4_series_release as caller

        pair = series.PAIRS[0]
        fields = [{"amount": 0}, {"amount": 1.25}, {"amount": True}, {"amount": False},
                  {"wrong_key": 3}, None, {"amount": "4"}]
        amounts = {(window, pair, "sabotage"): field for window, field in zip(WINDOWS, fields)}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stored_series(root, amount_fields=amounts, amount_field="amount")
            original = caller.named_bytes

            def observe(source_root, path):
                self.assertNotIn("transcript", path)
                return original(source_root, path)

            with patch.object(caller, "named_bytes", side_effect=observe):
                panel = caller.build_report(root)[seal.RL176]["q"]["side_transfer"][pair]
            self.assertEqual(panel["interpretation"], "post-treatment")
            self.assertEqual([row["side_transfer_total"] for row in panel["rows"][:7]],
                             [0, 1.25, None, None, None, None, None])
            self.assertTrue(all(row["energy_excess_j"] is not None for row in panel["rows"]))

    def test_invalid_post_release_join_writes_no_report_or_member_reads(self):
        from scripts import align_v4_series_release as caller

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stored_series(root, defective_layout=True, omit_first_pm=True)
            output = root / "report.json"
            argv = ["--measurement-root", str(root), "--output", str(output)]
            with patch.object(caller.ReleasedInputs, "load_members",
                              side_effect=AssertionError("member loader invoked")), \
                    redirect_stderr(StringIO()), self.assertRaises(SystemExit) as refusal:
                caller.main(argv)
            self.assertEqual(refusal.exception.code, 1)
            self.assertFalse(output.exists())

            # Admit the separate layout while keeping the first PM projection
            # absent from the record's digest-bound restore manifest.
            ledger = json.loads((root / packet.SERIES_PATH).read_bytes())
            ledger["release_layouts"]["T3"]["trace_layout"] = caller.LAYOUT
            write_json(root / packet.SERIES_PATH, ledger)
            tip = commit_fixture(root, [packet.SERIES_PATH])
            fixture_git(root, "update-ref", caller.RELEASE_REF, tip)
            real = caller.named_bytes

            def observe(source_root, path):
                self.assertNotIn("/runs/", path, "opened a member file without its PM binding")
                return real(source_root, path)

            with patch.object(caller, "named_bytes", side_effect=observe), \
                    redirect_stderr(StringIO()), self.assertRaises(SystemExit) as refusal:
                caller.main(argv)
            self.assertEqual(refusal.exception.code, 1)
            self.assertFalse(output.exists())

    def test_post_release_terminal_authority_refuses_before_member_loading(self):
        from scripts import align_v4_series_release as caller

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stored_series(root)
            ledger = json.loads((root / packet.SERIES_PATH).read_bytes())
            terminal = ledger["previous_record"]
            terminal_record = json.loads((root / terminal["path"]).read_bytes())
            prior = terminal_record["previous_record"]
            output = root / "report.json"

            def point_authority_at(link, *, completion_commit=None):
                paths = [packet.SERIES_PATH]
                if completion_commit is not None:
                    write_release_context(root, commit=completion_commit)
                    paths.extend((seal.SERIES_COMPLETE, seal.RELEASE_RECEIPT))
                write_json(root / packet.SERIES_PATH, {**ledger, "previous_record": link})
                fixture_git(root, "update-ref", caller.RELEASE_REF, commit_fixture(root, paths))

            def assert_refusal(case):
                with self.subTest(case=case):
                    self.assertTrue(seal.released({"measurement_root": root}))
                    with patch.object(caller.ReleasedInputs, "load_members",
                                      side_effect=AssertionError("member loader invoked")), \
                            redirect_stderr(StringIO()), self.assertRaises(SystemExit) as refusal:
                        caller.main(["--measurement-root", str(root), "--output", str(output)])
                    self.assertEqual(refusal.exception.code, 1)
                    self.assertFalse(output.exists())

            fixture_git(root, "update-ref", "-d", caller.RELEASE_REF)
            assert_refusal("missing authority ref")

            point_authority_at(prior)
            assert_refusal("stale terminal binding")

            point_authority_at({**terminal, "sha256": "0" * 64})
            assert_refusal("wrong chained digest")

            tree = fixture_git(root, "rev-parse", terminal["commit"] + "^{tree}")
            other = fixture_git(root, "commit-tree", tree, "-m", "synthetic unreachable terminal")
            point_authority_at({**terminal, "commit": other}, completion_commit=other)
            assert_refusal("terminal outside authority history")

            prior_record = json.loads(fixture_git(root, "show", prior["commit"] + ":" + prior["path"]))
            duplicate_final = {"record_sha256": prior["sha256"],
                               "sources": {key: prior_record["sources"][key]
                                           for key in packet.FINAL_SOURCES_WITH_RECEIPT}}
            ambiguous = describe(root, terminal["path"], {**terminal_record, "previous_final": duplicate_final})
            new_terminal = commit_fixture(root, [terminal["path"]])
            point_authority_at({**ambiguous, "commit": new_terminal}, completion_commit=new_terminal)
            assert_refusal("direct and successor evidence both supplied")

    def test_restored_mount_refuses_ancestor_symlink(self):
        from scripts import align_v4_series_release as caller

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "input"
            root.mkdir()
            stored_series(root)
            restored = root / "series/restored"
            outside = Path(tmp) / "outside"
            restored.rename(outside)
            restored.symlink_to(outside, target_is_directory=True)
            output = root / "report.json"
            real_open = caller.os.open

            def observe(path, *args, **kwargs):
                self.assertNotEqual(path, "finalized_manifest.json", "opened an outside manifest")
                return real_open(path, *args, **kwargs)

            with patch.object(caller.os, "open", side_effect=observe), self.assertRaises(SystemExit) as refusal:
                caller.main(["--measurement-root", str(root), "--output", str(output)])
            self.assertEqual(refusal.exception.code, 1)
            self.assertFalse(output.exists())

    def test_stored_series_through_787_and_release_script_s_signature_at_102_not_101_of_154(self):
        for wins, tail in ((102, 0.0109278936864), (101, 0.0140103456299)):
            with self.subTest(wins=wins), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                stored_series(root, wins=wins)
                output = root / "report.json"
                result = invoke(root, output)
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(output.read_bytes())[seal.RL176]
                score = report["S"]
                self.assertEqual((score["strata"], score["windows"]), (22, 11))
                self.assertAlmostEqual(154 * score["theta"], wins, places=12)
                self.assertAlmostEqual(score["p_sup"], tail, places=12)
                self.assertEqual("S SIGNATURE" in score["words"], wins == 102)
                self.assertIs(report["q"]["words_frozen_before_c1"], True)

    def test_uncaptured_and_captured_without_s_rows_form_two_distinct_world_pairs(self):
        manifest = series.candidate()
        candidate = series.selected(manifest, "T3")
        pair = series.PAIRS[-1]
        for condition in ("benign", "sabotage"):
            changed = next(m for m in candidate["members"] if m["pair"] == pair
                           and m["condition"] == condition and m["ordinal"] in series.FRESH_ORDINALS)
            ordinal = changed["ordinal"]
            worlds = {}
            for no_rows in (False, True):
                with self.subTest(condition=condition, captured=no_rows), tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    stored_series(root, different=("T3", pair, condition, ordinal), no_rows=no_rows)
                    output = root / "report.json"
                    result = invoke(root, output)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    worlds[no_rows] = json.loads(output.read_bytes())[seal.RL176]
            absent, captured = worlds[False], worlds[True]
            self.assertEqual(absent["S"]["strata"], captured["S"]["strata"])
            self.assertEqual(absent["S"]["attrition"]["uncaptured_assignments"], [{
                "window": "T3", "pair": pair, "ordinal": ordinal,
                "decision": "excluded", "reason": "member.not_captured",
            }])
            self.assertEqual(captured["S"]["attrition"]["uncaptured_assignments"], [])
            tallies = captured["S"]["attrition"]["by_pair_and_condition"][pair][condition]
            self.assertEqual(tallies["eligible"] - tallies["with_score"], 1)
            absent_q, captured_q = (world["q"]["per_pair"][pair] for world in (absent, captured))
            absent_count, captured_count = (
                world["q"]["entering_members_by_stratum"].get("T3", {}).get(pair, 0)
                for world in (absent, captured)
            )
            self.assertNotEqual(absent_q["p_two_sided"], captured_q["p_two_sided"])
            if condition == "benign":
                self.assertEqual((absent_count, captured_count), (7, 8))
                self.assertEqual(absent_q["strata"], captured_q["strata"])
            else:
                self.assertEqual((absent_count, captured_count), (0, 8))
                self.assertEqual(captured_q["strata"] - absent_q["strata"], 1)

    def test_released_unbound_companion_prints_are_not_computed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            stored_series(root)
            output = root / "report.json"
            result = invoke(root, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(output.read_bytes())[seal.RL176]
            for key in ("S_a4", "S_w", "benign_slopes"):
                self.assertEqual(report[key], {"status": "not_computed", "reason": "producer_not_bound"})
            self.assertTrue(report["S"]["benign_turn0_context_slope"]["reason"])
            self.assertIn("S_pf", report)

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
