"""Production-scale cost and reviewer-world regressions for MoE Stage A.

Timing is reported, never used as an acceptance bar. Sizes are the review's
verified Qwen3 topology and SHADE-shaped episode scenarios.
"""

from __future__ import annotations

import math
import random
import subprocess
import sys
from pathlib import Path
import time
import tracemalloc
import unittest
from dataclasses import replace

from joulewise.align.records import RouterLog
from joulewise.align.moe import stats as S
from joulewise.align.moe.stage_a import analyze_stage_a, mann_whitney_auc
from tests.align.test_moe_calibration import make_world
from tests.align.test_moe_stats import assert_close


def original_episode_stats(log):
    """Pre-fix aggregate path, using unchanged validating public computations."""
    functions = (S.usage_entropy, S.load_imbalance, S.reuse_fraction, S.mean_reuse_distance)
    return {f"{phase}_{name}": function(log, phase=None if phase == "both" else phase)
            for phase in S.PHASES for name, function in zip(S.METRICS, functions)}


class CostTests(unittest.TestCase):
    def compare_paths(self, log):
        start = time.perf_counter()
        before = original_episode_stats(log)
        before_seconds = time.perf_counter() - start
        start = time.perf_counter()
        after = S.episode_stats(log)
        after_seconds = time.perf_counter() - start
        for name, value in after.items():
            assert_close(self, value, before[name])
        print("MOE_COST", {"tokens": len(log.experts), "layers": len(log.layers),
                           "top_k": log.top_k, "before_seconds": before_seconds,
                           "after_seconds": after_seconds}, flush=True)

    def test_qwen_log_memory_and_ten_thousand_tokens(self):
        E, K, L, T = 128, 8, 48, 10000  # r11's verified topology and token-count fixture.
        rng = random.Random(1)
        tracemalloc.start()
        rows = tuple(tuple(tuple(rng.sample(range(E), K)) for _ in range(L)) for _ in range(T))
        log = RouterLog("m", E, K, tuple(range(L)), ("prefill",) * (T // 2)
                        + ("decode",) * (T - T // 2), rows)
        current, _ = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        start = time.perf_counter()
        S.routing_flags(log)
        validation_seconds = time.perf_counter() - start
        print("MOE_ROUTER_MEMORY", {"bytes": current, "bytes_per_token": current / T,
                                    "validation_seconds": validation_seconds}, flush=True)
        self.compare_paths(log)

    def test_shade_sized_episode(self):
        E, K, L = 128, 8, 48  # Verified published model configuration.
        # r1 section 6: 30 turns x (1500 prefill + 250 decode) = 52,500 rows.
        rng = random.Random(1)
        phases, rows = [], []
        for _ in range(30):
            for phase, count in (("prefill", 1500), ("decode", 250)):
                for _ in range(count):
                    phases.append(phase)
                    rows.append(tuple(tuple(rng.sample(range(E), K)) for _ in range(L)))
        log = RouterLog("rev", E, K, tuple(range(L)), tuple(phases), tuple(rows))
        self.compare_paths(log)
        # Analytic uniform-independent reuse is K/E. r1 prints three decimals;
        # this fixture checks the same rounded production quantity, not a new
        # numerical agreement tolerance on the random sampling realization.
        result = S.episode_stats(log)
        assert_close(self, round(result["both_reuse_fraction"], 3), round(K / E, 3))


class ReviewerWorldTests(unittest.TestCase):
    def test_independent_twin_from_local_review_ref(self):
        # Full-history CI checkout fetches public branches. Read the reviewer's
        # files from that local ref; tests make no network requests and do not
        # commit the fetched twin. The brief authorizes these untracked paths.
        root = Path(__file__).resolve().parents[2]
        ref = "origin/lane/2026-10-21-align-moe-twin"
        revision = subprocess.run(["git", "rev-parse", ref], cwd=root,
                                  check=True, capture_output=True, text=True).stdout.strip()
        paths = ("tests/align/twins/moe_twin.py",
                 "tests/align/twins/test_moe_twin_selfcheck.py",
                 "tests/align/test_twin_moe.py")
        target = root / "tests/align/twins"
        target.mkdir(exist_ok=True)
        (target / "__init__.py").touch()
        for path in paths:
            blob = subprocess.run(["git", "show", f"{ref}:{path}"], cwd=root,
                                  check=True, capture_output=True, text=True).stdout
            (root / path).write_text(blob, encoding="utf-8")
        process = subprocess.run([sys.executable, "-m", "unittest", "tests.align.test_twin_moe", "-v"],
                                 cwd=root, capture_output=True, text=True)
        print("MOE_TWIN_REVIEW_REF", revision, process.stdout, process.stderr, flush=True)
        self.assertEqual(process.returncode, 0)  # Every independent agreement test must pass.

    def test_review_r3_complete_missing_and_empty_decode(self):
        world = make_world(seed=11, f=0.25, count_ratio=1.3, L=8, E=64, K=6)
        result = analyze_stage_a(world, n_bootstrap=400, seed=3)
        labels = result.labels
        features = [S.episode_stats(e.router_log) for e in world]
        for name, stat in result.statistics.items():
            values = [row[name] for row in features]
            effect, p, n = S.grouped_permutation_test(values, labels, result.groups, seed=3)
            assert_close(self, stat.effect, effect)
            # Identical permutation code/inputs/seed: p and draw count are bit-identical.
            self.assertEqual(stat.p_value, p)
            self.assertEqual(stat.n_perm_used, n)
            self.assertLessEqual(stat.interval[0], stat.effect)
            self.assertGreaterEqual(stat.interval[1], stat.effect)
        ordered = sorted(result.statistics, key=lambda name: result.statistics[name].p_value)
        running = 0.0
        for rank, name in enumerate(ordered):
            running = max(running, min(1.0, (12 - rank) * result.statistics[name].p_value))
            assert_close(self, result.statistics[name].p_holm, running)
        for name, auc in result.aucs.items():
            positive = [s for s, y in zip(result.predictions[name], labels) if y]
            negative = [s for s, y in zip(result.predictions[name], labels) if not y]
            brute = sum((1 if a > b else 0.5 if a == b else 0)
                        for a in positive for b in negative) / (len(positive) * len(negative))
            assert_close(self, auc, brute)
        print("MOE_REVIEW_R3_GAIN", {"gain": result.auc_gain, "refit": result.auc_gain_interval,
                                    "fixed": result.auc_gain_fixed_prediction_interval}, flush=True)
        for kind in ("missing", "empty_decode"):
            changed = list(world)
            index = 5 if kind == "missing" else 7  # Reviewer's chosen capture-gap episodes.
            if kind == "missing":
                changed[index] = replace(changed[index], router_log=None)
            else:
                log = changed[index].router_log
                keep = [i for i, phase in enumerate(log.phase) if phase == "prefill"]
                changed[index] = replace(changed[index], router_log=replace(
                    log, phase=tuple(log.phase[i] for i in keep),
                    experts=tuple(log.experts[i] for i in keep)))
            actual = analyze_stage_a(changed, n_bootstrap=100, seed=3)
            self.assertFalse([name for name, stat in actual.statistics.items()
                              if not math.isfinite(stat.p_value) or not math.isfinite(stat.effect)])
            for name, stat in actual.statistics.items():
                if kind == "missing" or name.startswith("decode_"):
                    self.assertIn("dropped_nonfinite_episodes:1", stat.flags)
                    self.assertIn(f"dropped_nonfinite_episode:{changed[index].episode_id}", stat.flags)
            print("MOE_REVIEW_R3", kind, {
                name: {"effect": stat.effect, "delta_from_complete": stat.effect - result.statistics[name].effect,
                       "p": stat.p_value, "holm": stat.p_holm, "interval": stat.interval}
                for name, stat in actual.statistics.items()}, flush=True)


if __name__ == "__main__":
    unittest.main()
