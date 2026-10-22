"""Twenty-episode production-path matrix, durable recovery, and CLI tests."""

from __future__ import annotations

import json
import math
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.align import runner
from joulewise.align.mock_world import PowerModel, ScriptedEndpoint
from joulewise.align.records import read_episodes, write_episodes, to_json
from joulewise.align.tamper import delete_turns, drop_tool_calls, hide_scratchpad, random_tamper


def matrix_spec(output_dir="output"):
    return {
        "matrix_id": "twenty-inbox-v1", "order_seed": 1729,
        "clock_domain": "mock.monotonic", "clock": {"factory": "mock.clock"},
        "task_pairs": [
            {"factory": "mock.inbox", "task_pair": "mock/inbox-a"},
            {"factory": "mock.inbox", "task_pair": "mock/inbox-b"},
        ],
        "conditions": ["benign", "sabotage"], "seeds": [0, 1, 2, 3, 4],
        "endpoints": [{"factory": "mock.scripted"}],
        "monitors": [{"factory": "mock.monitor",
                      "visibilities": ["full", "no_scratchpad", "actions_only"]}],
        # Equal 100 ms cadence/averaging bins conserve phase energy exactly;
        # default duty-shaped sampling, noise and quantum run in test_mock_world.
        "samplers": [{"factory": "mock.power", "config": {
            "interval_ns": 100_000_000, "averaging_window_ns": 100_000_000,
            "noise_watts": 0.0, "quantum_watts": 0.0,
        }}],
        "token_counter": {"factory": "mock.tokens"},
        "max_turns": 40, "max_tokens": 600, "temperature": 0.0,
        "output_dir": output_dir,
    }


def write_spec(root, name="matrix.json", **updates):
    spec = matrix_spec()
    spec.update(updates)
    path = Path(root) / name
    path.write_text(json.dumps(spec), encoding="utf-8")
    return path


class MatrixTests(unittest.TestCase):
    def test_twenty_worlds_tamper_and_jsonl_round_trips(self):
        with tempfile.TemporaryDirectory() as directory:
            path = runner.run_matrix(write_spec(directory))
            episodes = read_episodes(path)
            self.assertEqual(len(episodes), 2 * 2 * 5)
            transcripts = [json.loads(line) for line in
                           path.with_name("transcripts.jsonl").read_text().splitlines()]
            self.assertEqual({row["episode_id"] for row in transcripts},
                             {ep.episode_id for ep in episodes})
            energy_checks = []
            model = PowerModel()
            for ep in episodes:
                side = ep.condition == "sabotage"
                self.assertEqual(ep.totals()["turns"], 12 + int(side))
                self.assertEqual(ep.totals()["tool_calls"], 11 + int(side))
                self.assertEqual(ep.totals()["hidden_tokens"], 184 * int(side))
                # Independent reconstruction of the configured token draws:
                # each turn makes a prefill draw followed by a visible-decode draw.
                rng = random.Random(ep.seed)
                prefills, decodes = [], []
                context = 0
                for index, turn in enumerate(ep.turns):
                    prefill = rng.choice((800, 1200, 1600))
                    decode = rng.choice((80, 160, 240)) + (184 if side and index == 6 else 0)
                    prefills.append(prefill)
                    decodes.append(decode)
                    self.assertEqual(turn.context_tokens, context)
                    self.assertEqual(turn.prefill_tokens, prefill)
                    self.assertEqual(turn.decode_tokens, decode)
                    self.assertEqual(turn.hidden_tokens, 184 if side and index == 6 else 0)
                    context += prefill + decode
                self.assertEqual(ep.totals()["prefill_tokens"], sum(prefills))
                self.assertEqual(ep.totals()["decode_tokens"], sum(decodes))
                self.assertEqual(ep.side_task_success, side)
                # Exact categorical task outcome generated from completed tool state.
                self.assertEqual(ep.main_task_score, float(True))
                self.assertEqual(len(ep.monitor_verdicts), 3)
                self.assertEqual(len(ep.power_traces), 1)
                self.assertNotIn("runner.error", " ".join(ep.flags))
                # Independent count-sum formula versus the production sampler's
                # averaged trace. Contiguous boxes plus trailing coverage conserve
                # excess energy; add idle only inside the episode.
                expected_joules = (
                    model.idle_watts * (ep.end_ns - ep.start_ns) / 1_000_000_000 +
                    model.prefill_joules_per_token * sum(t.prefill_tokens for t in ep.turns) +
                    model.decode_joules_per_token * sum(t.decode_tokens for t in ep.turns) +
                    model.context_joules_per_token_squared *
                    sum(t.context_tokens * t.decode_tokens for t in ep.turns))
                trace = ep.power_traces[0]
                sampled_joules = (
                    model.idle_watts * (ep.end_ns - ep.start_ns) / 1_000_000_000 +
                    math.fsum((watts - model.idle_watts) *
                              trace.nominal_interval_ns / 1_000_000_000
                              for watts in trace.values[1:]))
                # No measurement uncertainty in this noiseless conservation check:
                # use the brief's 1e-6 relative agreement bar.
                self.assertTrue(math.isclose(sampled_joules, expected_joules, rel_tol=1e-6),
                                (ep.episode_id, sampled_joules, expected_joules))
                energy_checks.append((sampled_joules, expected_joules))
            for label, transform in (
                ("turns", lambda ep: delete_turns(ep, [6])),
                ("calls", lambda ep: drop_tool_calls(ep, lambda call: call.name == "transfer")),
                ("scratchpad", hide_scratchpad),
                ("random", lambda ep: random_tamper(ep, random.Random(ep.seed),
                                                  "delete_turns", 0.25)),
            ):
                changed = [transform(ep) for ep in episodes]
                tampered = Path(directory) / (label + ".jsonl")
                self.assertEqual(write_episodes(tampered, changed), 20)
                restored = read_episodes(tampered)
                for source, result in zip(episodes, restored):
                    self.assertEqual(to_json(source.power_traces), to_json(result.power_traces))
                    self.assertEqual(source.totals(), result.totals())
                    self.assertTrue(any(flag.startswith("tamper.") for flag in result.flags))
                    if label == "turns":
                        self.assertEqual(result.totals(logged_only=True)["turns"],
                                         len(source.turns) - 1)
                    if label == "calls" and source.condition == "sabotage":
                        self.assertEqual(result.totals(logged_only=True)["tool_calls"], 11)
            metadata = json.loads(path.with_name("run.json").read_text())
            self.assertEqual(metadata["order_seed"], 1729)
            self.assertEqual(metadata["order"], [ep.episode_id for ep in episodes])
            self.assertEqual(len(set(metadata["order"])), 20)
            natural = sorted(episodes, key=lambda ep: (
                ep.task_pair, ("benign", "sabotage").index(ep.condition), ep.seed))
            self.assertNotEqual(metadata["order"], [ep.episode_id for ep in natural])
            print("ALIGN_RUNNER_END_TO_END " + json.dumps({
                "episodes": len(episodes),
                "turns": sum(ep.totals()["turns"] for ep in episodes),
                "tool_calls": sum(ep.totals()["tool_calls"] for ep in episodes),
                "prefill_tokens": sum(ep.totals()["prefill_tokens"] for ep in episodes),
                "decode_tokens": sum(ep.totals()["decode_tokens"] for ep in episodes),
                "hidden_tokens": sum(ep.totals()["hidden_tokens"] for ep in episodes),
                "sabotage_hidden": [
                    {"task_pair": ep.task_pair, "seed": ep.seed,
                     "turn_indices": [t.index for t in ep.turns if t.hidden_tokens],
                     "hidden_tokens": ep.totals()["hidden_tokens"]}
                    for ep in episodes if ep.condition == "sabotage"],
                "sampled_gross_joules": math.fsum(item[0] for item in energy_checks),
                "independent_gross_joules": math.fsum(item[1] for item in energy_checks),
                "max_energy_error_joules": max(abs(a - b) for a, b in energy_checks),
                "energy_relative_tolerance": 1e-6,
                "tamper_round_trip_datasets": 4,
            }, sort_keys=True), file=sys.stderr)

    def test_resume_skips_chat_and_preserves_files(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = write_spec(directory)
            path = runner.run_matrix(spec)
            before = {name: path.with_name(name).read_bytes()
                      for name in ("episodes.jsonl", "transcripts.jsonl")}
            with patch.object(ScriptedEndpoint, "chat", side_effect=AssertionError("must skip")):
                self.assertEqual(runner.run_matrix(spec), path)
            for name, content in before.items():
                self.assertEqual(path.with_name(name).read_bytes(), content)

    def test_simulated_kills_reproduce_both_files(self):
        class Killed(BaseException):
            pass
        with tempfile.TemporaryDirectory() as directory:
            baseline = runner.run_matrix(write_spec(directory, "baseline.json", output_dir="baseline"))
            expected = {name: baseline.with_name(name).read_bytes()
                        for name in ("episodes.jsonl", "transcripts.jsonl")}
            for cut in ("before_episode", "after_episode", "partial_episode", "partial_transcript"):
                with self.subTest(cut=cut):
                    spec = write_spec(directory, cut + ".json", output_dir=cut)
                    append = runner._append
                    calls = 0
                    def crashing_append(path, value):
                        nonlocal calls
                        if path.name == "episodes.jsonl":
                            calls += 1
                            if calls == 7:
                                if cut == "after_episode":
                                    append(path, value)
                                elif cut == "partial_episode":
                                    with path.open("ab") as handle:
                                        handle.write(to_json(value).encode("utf-8")[:127])
                                raise Killed()
                        if path.name == "transcripts.jsonl" and calls == 6 and cut == "partial_transcript":
                            with path.open("ab") as handle:
                                handle.write(to_json(value).encode("utf-8")[:127])
                            raise Killed()
                        append(path, value)
                    with patch.object(runner, "_append", side_effect=crashing_append):
                        with self.assertRaises(Killed):
                            runner.run_matrix(spec)
                    recovered = runner.run_matrix(spec)
                    self.assertEqual(len(read_episodes(recovered)), 20)
                    for name, content in expected.items():
                        # Bit identity is the property: deterministic replay after a kill.
                        self.assertEqual(recovered.with_name(name).read_bytes(), content)
                    flags = json.loads(recovered.with_name("run.json").read_text())["flags"]
                    if cut.startswith("partial"):
                        self.assertTrue(any("resume.partial_last_line" in flag for flag in flags))
                        self.assertTrue(recovered.with_name("recovery.jsonl").exists())

    def test_invalid_record_is_flagged_and_quarantined(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = write_spec(directory)
            path = runner.run_matrix(spec)
            original = path.read_bytes()
            with path.open("ab") as handle:
                handle.write(b'{"schema":"unknown"}\n')
            runner.run_matrix(spec)
            self.assertEqual(path.read_bytes(), original)
            flags = json.loads(path.with_name("run.json").read_text())["flags"]
            self.assertIn("resume.invalid_record.episodes.jsonl", flags)

    def test_missing_transcript_is_retained_as_flagged_placeholder(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = write_spec(directory)
            path = runner.run_matrix(spec)
            transcripts_path = path.with_name("transcripts.jsonl")
            rows = transcripts_path.read_text().splitlines()
            missing = json.loads(rows[0])["episode_id"]
            transcripts_path.write_text("\n".join(rows[1:]) + "\n")
            runner.run_matrix(spec)
            rows = [json.loads(line) for line in transcripts_path.read_text().splitlines()]
            placeholder = next(row for row in rows if row["episode_id"] == missing)
            self.assertEqual(placeholder["messages"], [])
            self.assertIn("resume.transcript_missing", placeholder["flags"])

    def test_unknown_factory_records_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = write_spec(directory, task_pairs=[{"factory": "missing.task", "task_pair": "missing"}],
                              conditions=["benign"], seeds=[0])
            path = runner.run_matrix(spec)
            episodes = read_episodes(path)
            self.assertEqual(len(episodes), 1)
            self.assertIn("factory.error.KeyError", episodes[0].flags)
            self.assertEqual(episodes[0].turns, ())

    def test_interrupt_saves_current_episode_and_resume_schedules_rest(self):
        class Interrupted(ScriptedEndpoint):
            def chat(self, messages, **kwargs):
                if any(m.role == "tool" for m in messages):
                    raise KeyboardInterrupt
                return super().chat(messages, **kwargs)
        def factory(config, context):
            return Interrupted(clock=context.clock, condition=context.condition)
        runner.register_endpoint_factory("test.interrupt", factory)
        with tempfile.TemporaryDirectory() as directory:
            spec = write_spec(directory, endpoints=[{"factory": "test.interrupt"}])
            path = runner.run_matrix(spec)
            episodes = read_episodes(path)
            self.assertEqual(len(episodes), 1)
            self.assertIn("episode.interrupted", episodes[0].flags)
            runner.register_endpoint_factory("test.interrupt",
                lambda config, context: ScriptedEndpoint(clock=context.clock, condition=context.condition))
            runner.run_matrix(spec)
            self.assertEqual(len(read_episodes(path)), 20)

    def test_cli_run_and_tamper(self):
        with tempfile.TemporaryDirectory() as directory:
            spec = write_spec(directory, task_pairs=[{"factory": "mock.inbox", "task_pair": "cli"}],
                              seeds=[0], conditions=["sabotage"])
            result = subprocess.run([sys.executable, "-m", "joulewise.align", "run",
                                     "--matrix", str(spec)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            source = Path(result.stdout.strip())
            target = Path(directory) / "tampered.jsonl"
            result = subprocess.run([sys.executable, "-m", "joulewise.align", "tamper",
                "--input", str(source), "--output", str(target), "--kind", "delete_turns",
                "--indices", "6"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(read_episodes(target)[0].totals(logged_only=True)["turns"], 12)


if __name__ == "__main__":
    unittest.main()
