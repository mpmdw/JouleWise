"""End-to-end topic worlds through shared records and the real Stage A analysis."""

from __future__ import annotations

import io
import json
import math
import statistics
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path

from joulewise.align.records import Episode, RouterLog, from_json, to_json, write_episodes
from joulewise.align.moe.stage_a import analyze_stage_a, main, mann_whitney_auc
from joulewise.align.moe.stats import episode_stats, load_imbalance
from joulewise.align.moe.synthetic import TopicWorld, expected_topic_statistics, topic_episodes
from tests.align.test_moe_stats import assert_close


class StageAWorldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = TopicWorld()
        cls.shift = 0.4  # Fixture parameter: 40% of decode tokens switch to side-task affinity.
        cls.world = topic_episodes(cls.shift, design=cls.design, seed=731)
        # Bootstrap budget is an exposed analysis parameter, not an agreement bar.
        cls.result = analyze_stage_a(cls.world, n_bootstrap=256, seed=83)
        print("MOE_STAGE_A_SHIFT", json.dumps({
            "episodes": len(cls.world),
            "groups": cls.design.groups,
            "turns_per_episode": cls.design.turns,
            "decode_tokens": sum(e.totals()["decode_tokens"] for e in cls.world),
            "prefill_tokens": sum(e.totals()["prefill_tokens"] for e in cls.world),
            "tool_calls": sum(e.totals()["tool_calls"] for e in cls.world),
            "side_fraction": cls.shift,
            "aucs": cls.result.aucs,
            "auc_gain": cls.result.auc_gain,
            "auc_gain_interval": cls.result.auc_gain_interval,
            "decode_effects": {name: {"effect": stat.effect, "interval": stat.interval,
                                     "p_holm": stat.p_holm}
                               for name, stat in cls.result.statistics.items()
                               if name.startswith("decode_")},
        }, sort_keys=True))

    def test_world_is_multiturn_and_round_trips_exactly(self):
        episode = self.world[0]
        self.assertEqual(from_json(Episode, to_json(episode)), episode)
        self.assertEqual(len(episode.turns), self.design.turns)
        self.assertEqual(episode.totals()["tool_calls"], self.design.turns - 1)
        self.assertEqual(len(episode.router_log.experts),
                         episode.totals()["prefill_tokens"] + episode.totals()["decode_tokens"])
        for benign, sabotage in zip(self.world[::2], self.world[1::2]):
            self.assertEqual(benign.totals(), sabotage.totals())  # Matched integer design.
            self.assertEqual(benign.router_log.layers, sabotage.router_log.layers)

    def test_shift_separates_beyond_counts(self):
        result = self.result
        # Conventional familywise level .05, specified in the brief; the 40%
        # fixture shift must clear it after Holm over all 12 planned tests.
        self.assertLess(result.statistics["decode_load_imbalance"].p_holm, 0.05)
        self.assertGreater(result.statistics["decode_load_imbalance"].interval[0], 0.0)
        assert_close(self, result.aucs["metadata"], 0.5)  # Matched counts imply all tied scores.
        self.assertGreater(result.auc_gain_interval[0], 0.0)  # Gain's CI excludes no improvement.
        self.assertGreater(result.aucs["routing"], result.aucs["metadata"])
        for name in ("metadata", "routing", "combined"):
            self.assertEqual(len(result.predictions[name]), len(self.world))
        for name, statistic in result.statistics.items():
            self.assertEqual(statistic.n_perm_used, 2**self.design.groups)
            if name.startswith("prefill_"):
                assert_close(self, statistic.effect, 0.0)  # Prefill topic is identical by design.

    def test_expected_reuse_effect_with_grouped_interval(self):
        expected = expected_topic_statistics(self.design.num_experts, self.design.top_k, self.shift)
        benign = expected_topic_statistics(self.design.num_experts, self.design.top_k, 0.0)
        effect = expected["reuse_fraction"] - benign["reuse_fraction"]
        interval = self.result.statistics["decode_reuse_fraction"].interval
        # This is a coverage check against an analytic generative expectation,
        # using the report's conventional 95% grouped-bootstrap interval.
        self.assertLessEqual(interval[0], effect)
        self.assertGreaterEqual(interval[1], effect)

    def test_finite_token_imbalance_matches_marginal_count_law(self):
        residuals = []
        e, k, f = self.design.num_experts, self.design.top_k, self.shift
        for episode in self.world[1::2]:
            log = episode.router_log
            n = log.phase.count("decode")
            p_core, p_other = f + (1 - f) * k / e, (1 - f) * k / e
            expected_cv_squared = f * f * (e / k - 1) + e / (n * k * k) * (
                k * p_core * (1 - p_core) + (e - k) * p_other * (1 - p_other))
            observed = []
            for layer in range(len(log.layers)):
                single = RouterLog(log.model, e, k, (log.layers[layer],), log.phase,
                                   tuple((row[layer],) for row in log.experts))
                observed.append(load_imbalance(single, phase="decode")**2)
            residuals.append(statistics.mean(observed) - expected_cv_squared)
        # Independent task groups supply the SE. The normal 95% half-width is
        # derived from their observed variance; no arbitrary numerical tolerance.
        half_width = statistics.NormalDist().inv_cdf(0.975) * statistics.stdev(residuals) / math.sqrt(len(residuals))
        self.assertLessEqual(abs(statistics.mean(residuals)), half_width)

    def test_zero_shift_removes_separation(self):
        null = topic_episodes(0.0, design=self.design, seed=731)
        result = analyze_stage_a(null, n_bootstrap=128, seed=83)
        print("MOE_STAGE_A_PAIRED_NULL", json.dumps(
            {"aucs": result.aucs, "auc_gain": result.auc_gain,
             "minimum_holm_p": min(s.p_holm for s in result.statistics.values())},
            sort_keys=True))
        for statistic in result.statistics.values():
            assert_close(self, statistic.effect, 0.0)
            assert_close(self, statistic.p_holm, 1.0)
        for auc in result.aucs.values():
            assert_close(self, auc, 0.5)
        assert_close(self, result.auc_gain, 0.0)

    def test_independent_noise_zero_shift_is_exchangeable(self):
        null = topic_episodes(0.0, design=self.design, seed=731, independent_noise=True)
        result = analyze_stage_a(null, n_bootstrap=128, seed=83)
        print("MOE_STAGE_A_INDEPENDENT_NULL", json.dumps(
            {"aucs": result.aucs, "auc_gain": result.auc_gain,
             "auc_gain_interval": result.auc_gain_interval,
             "minimum_holm_p": min(s.p_holm for s in result.statistics.values())},
            sort_keys=True))
        # No-shift data must not cross the brief's conventional .05 Holm level.
        self.assertTrue(all(statistic.p_holm >= 0.05 for statistic in result.statistics.values()))
        self.assertLessEqual(result.auc_gain_interval[0], 0.0)
        self.assertGreaterEqual(result.auc_gain_interval[1], 0.0)

    def test_missing_capture_keeps_episodes_and_metadata(self):
        missing = tuple(replace(e, router_log=None) for e in self.world)
        result = analyze_stage_a(missing, n_bootstrap=32, seed=83)
        self.assertEqual(len(result.episode_ids), len(missing))
        assert_close(self, result.aucs["metadata"], 0.5)
        self.assertTrue(math.isnan(result.statistics["decode_usage_entropy"].p_value))
        self.assertTrue(any("router_log_missing" in flag for flag in result.flags))

    def test_jsonl_cli_production_path(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "episodes.jsonl"
            self.assertEqual(write_episodes(path, self.world), len(self.world))
            output = io.StringIO()
            with redirect_stdout(output):
                code = main([str(path), "--n-bootstrap", "32", "--seed", "83"])
            report = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(report["episode_ids"], list(self.result.episode_ids))
            assert_close(self, report["aucs"]["metadata"], 0.5)
            self.assertGreater(report["auc_gain"], 0.0)

    def test_full_qwen_shape_is_a_parameter(self):
        design = replace(self.design, groups=1, layers=48, num_experts=128, top_k=8, turns=2)
        for episode in topic_episodes(self.shift, design=design, seed=3):
            log = episode.router_log
            self.assertEqual(len(log.layers), 48)  # Verified published config.
            self.assertEqual(log.num_experts, 128)
            self.assertEqual(log.top_k, 8)
            self.assertTrue(all(math.isfinite(x) for x in episode_stats(log).values()))


class ClassificationTests(unittest.TestCase):
    def test_auc_ties_and_direction(self):
        assert_close(self, mann_whitney_auc([0, 0, 1, 1], [0, 1, 0, 1]), 0.5)
        assert_close(self, mann_whitney_auc([0, 1, 2, 3], [0, 0, 1, 1]), 1.0)
        assert_close(self, mann_whitney_auc([3, 2, 1, 0], [0, 0, 1, 1]), 0.0)

    def test_held_out_labels_do_not_affect_their_predictions(self):
        world = topic_episodes(0.4, design=TopicWorld(groups=4, turns=2), seed=42)
        first = analyze_stage_a(world, n_bootstrap=16)
        changed = tuple(replace(e, condition="sabotage" if e.condition == "benign" else "benign")
                        if e.task_pair == world[0].task_pair else e for e in world)
        second = analyze_stage_a(changed, n_bootstrap=16)
        for name in first.predictions:
            # Same code and identical training inputs must give bit-identical
            # predictions for the held-out task even when its labels change.
            self.assertEqual(first.predictions[name][:2], second.predictions[name][:2])

    def test_counts_only_work_is_detected_by_metadata_baseline(self):
        # A second production-shaped control repeats benign decode work, adding
        # forwarded tokens and elapsed decode time without a side-task topic.
        original = topic_episodes(0.0, design=TopicWorld(), seed=71)
        world = []
        for episode in original:
            if episode.condition == "benign":
                world.append(episode)
                continue
            log = episode.router_log
            offset = extra_context = row_index = 0
            turns, phases, rows = [], [], []
            for turn in episode.turns:
                prefill = log.experts[row_index:row_index + turn.prefill_tokens]
                row_index += turn.prefill_tokens
                decode = log.experts[row_index:row_index + turn.decode_tokens]
                row_index += turn.decode_tokens
                rows.extend(prefill + decode + decode)
                phases.extend(("prefill",) * len(prefill) + ("decode",) * (2 * len(decode)))
                extra_ns = turn.decode_tokens * TopicWorld().decode_ns_per_token
                calls = tuple(replace(call, start_ns=call.start_ns + offset + extra_ns,
                                      end_ns=call.end_ns + offset + extra_ns)
                              for call in turn.tool_calls)
                turns.append(replace(turn, start_ns=turn.start_ns + offset,
                                     end_ns=turn.end_ns + offset + extra_ns,
                                     first_token_ns=turn.first_token_ns + offset,
                                     context_tokens=turn.context_tokens + extra_context,
                                     decode_tokens=2 * turn.decode_tokens, tool_calls=calls))
                offset += extra_ns
                extra_context += turn.decode_tokens
            world.append(replace(episode, turns=tuple(turns), end_ns=episode.end_ns + offset,
                                 router_log=replace(log, phase=tuple(phases), experts=tuple(rows))))
        result = analyze_stage_a(world, n_bootstrap=32)
        # Decode ranges do not overlap: sabotage repeats every decode forward,
        # so the metadata classifier must rank all conditions correctly.
        assert_close(self, result.aucs["metadata"], 1.0)

    def test_unreadable_input_cli_is_a_flagged_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = io.StringIO()
            with redirect_stdout(output):
                code = main([str(Path(directory) / "missing.jsonl"), "--n-bootstrap", "16"])
            result = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertTrue(any("episode_input_unreadable" in flag for flag in result["flags"]))
            self.assertIsNone(result["aucs"]["metadata"])

    def test_empty_or_unpaired_inputs_are_flagged(self):
        result = analyze_stage_a((), n_bootstrap=0)
        self.assertIn("no_episodes", result.flags)
        self.assertTrue(math.isnan(result.aucs["metadata"]))
        one = topic_episodes(0.4, design=TopicWorld(groups=1, turns=2), seed=2)
        result = analyze_stage_a(one[:1], n_bootstrap=16)
        self.assertTrue(any("group_has_no_label_exchangeability" in flag for flag in result.flags))
        self.assertEqual(len(result.episode_ids), 1)


if __name__ == "__main__":
    unittest.main()
