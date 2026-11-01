"""Production-scale cost and reviewer-world regressions for MoE Stage A.

Timing is reported, never used as an acceptance bar. Sizes are the review's
verified Qwen3 topology and SHADE-shaped episode scenarios.
"""

from __future__ import annotations

import math
import os
import random
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile
import time
import tracemalloc
import unittest
from dataclasses import replace
from unittest.mock import patch

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
        # Port E4's six seeds unchanged; cost comparison needs only seed 1.
        for seed in range(1, 7):
            with self.subTest(seed=seed):
                rng = random.Random(seed)
                phases, rows = [], []
                for _ in range(30):
                    for phase, count in (("prefill", 1500), ("decode", 250)):
                        for _ in range(count):
                            phases.append(phase)
                            rows.append(tuple(tuple(rng.sample(range(E), K)) for _ in range(L)))
                log = RouterLog("rev", E, K, tuple(range(L)), tuple(phases), tuple(rows))
                if seed == 1:
                    self.compare_paths(log)
                value = S.reuse_fraction(log)
                # Uniform top-K overlap is hypergeometric (E population,
                # K marked, K drawn). Dividing by K gives mean K/E and
                # variance sigma_squared below. Adjacent overlaps are
                # conditionally independent with a common-set-independent
                # law, so SE = sigma/sqrt(L*(T-1)).
                # Five SE gives normal-tail false failure below 6e-7;
                # for this fixture the derived bar is about 2.62e-4.
                T = len(log.experts)
                sigma_squared = (1 / E) * ((E - K) / E) * ((E - K) / (E - 1))
                bar = 5 * math.sqrt(sigma_squared / (L * (T - 1)))
                self.assertLessEqual(abs(value - K / E), bar)
                print("MOE_REVIEW_R2_E4", {"seed": seed, "reuse": value,
                                          "expectation": K / E, "bar": bar}, flush=True)
                del log, rows, phases  # Keep production-sized seeds sequential in memory.



def run_twin_from_local_ref(root: Path) -> tuple[str, subprocess.CompletedProcess[str]]:
    """Run locally available independent tests without changing the checkout."""
    git = shutil.which("git")
    if git is None:
        raise unittest.SkipTest("independent MoE twin needs git")
    ref = "origin/lane/2026-10-21-align-moe-twin"
    resolved = subprocess.run([git, "rev-parse", "--verify", ref], cwd=root,
                              capture_output=True, text=True)
    if resolved.returncode:
        raise unittest.SkipTest(f"independent MoE twin local ref unavailable: {ref}")
    revision = resolved.stdout.strip()
    paths = ("tests/align/twins/moe_twin.py",
             "tests/align/twins/test_moe_twin_selfcheck.py",
             "tests/align/test_twin_moe.py")
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory)
        for package in ("tests", "tests/align", "tests/align/twins"):
            (target / package).mkdir(exist_ok=True)
            (target / package / "__init__.py").touch()
        # At the round-2 twin revision, imports use only stdlib, joulewise,
        # and these twin modules; no checkout test helpers need copying.
        for path in paths:
            blob = subprocess.run([git, "show", f"{revision}:{path}"], cwd=root,
                                  check=True, capture_output=True, text=True).stdout
            (target / path).write_text(blob, encoding="utf-8")
        env = dict(os.environ, PYTHONPATH=os.pathsep.join((directory, str(root))),
                   PYTHONDONTWRITEBYTECODE="1")
        process = subprocess.run(
            [sys.executable, "-m", "unittest", "tests.align.test_twin_moe",
             "tests.align.twins.test_moe_twin_selfcheck", "-v"],
            cwd=target, env=env, capture_output=True, text=True)
    return revision, process


class ReviewerWorldTests(unittest.TestCase):
    def test_independent_twin_from_local_review_ref(self):
        # CI checkout supplies the public ref; the test never fetches network data.
        root = Path(__file__).resolve().parents[2]
        revision, process = run_twin_from_local_ref(root)
        print("MOE_TWIN_REVIEW_REF", revision, process.stdout, process.stderr, flush=True)
        self.assertEqual(process.returncode, 0)  # Every independent agreement test must pass.

    def test_independent_twin_missing_git_or_ref_skips(self):
        root = Path(__file__).resolve().parents[2]
        with patch("shutil.which", return_value=None):
            with self.assertRaisesRegex(unittest.SkipTest, "needs git"):
                run_twin_from_local_ref(root)
        missing = subprocess.CompletedProcess(["git"], 128, "", "unknown revision")
        with patch("shutil.which", return_value="git"), patch("subprocess.run", return_value=missing):
            with self.assertRaisesRegex(unittest.SkipTest, "local ref unavailable"):
                run_twin_from_local_ref(root)

    def test_independent_twin_preserves_checkout_files(self):
        # Port the reviewer's local-edit repro into an isolated fake checkout.
        # Only local git reads are mocked; the real Python subprocess imports
        # the temporary twin package and the checkout's production package.
        checkout = Path(__file__).resolve().parents[2]
        real_run = subprocess.run
        captured = []
        fixture = (
            "import unittest\n"
            "from joulewise.align.moe.stats import episode_stats\n"
            "class ImportTest(unittest.TestCase):\n"
            "    def test_import(self):\n"
            "        self.assertTrue(callable(episode_stats))\n"
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "joulewise").symlink_to(checkout / "joulewise", target_is_directory=True)
            local = root / "tests/align/test_twin_moe.py"
            local.parent.mkdir(parents=True)
            local.write_text("# local edit\n", encoding="utf-8")
            before = sorted(str(p.relative_to(root)) for p in root.rglob("*"))

            def run(args, **kwargs):
                if args[0] == "git":
                    blob = "local-fixture-revision\n" if args[1] == "rev-parse" else fixture
                    return subprocess.CompletedProcess(args, 0, blob, "")
                captured.append(Path(kwargs["cwd"]))
                self.assertNotEqual(Path(kwargs["cwd"]), root)
                return real_run(args, **kwargs)

            with patch("shutil.which", return_value="git"), patch("subprocess.run", side_effect=run):
                _, process = run_twin_from_local_ref(root)
            self.assertEqual(process.returncode, 0, process.stdout + process.stderr)
            self.assertEqual(local.read_text(encoding="utf-8"), "# local edit\n")
            self.assertEqual(sorted(str(p.relative_to(root)) for p in root.rglob("*")), before)
            self.assertTrue(captured)
            self.assertTrue(all(not p.exists() for p in captured))  # Temporary tests were removed.

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
