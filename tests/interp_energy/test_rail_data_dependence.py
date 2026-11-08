from contextlib import contextmanager
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from joulewise.clock import FakeClock
from joulewise.interp_energy.rail_data_dependence import (
    CONDITIONS, DTYPES, NumpyDryBackend, Settings, abba_schedule,
    execute_plan, main, make_plan, packed_hamming_word, synthetic_weight,
)

HAS_NUMPY = importlib.util.find_spec("numpy") is not None
ROOT = Path(__file__).resolve().parents[2]


class PlanTests(unittest.TestCase):
    def test_default_plan_fits_ninety_minutes_and_ring_exceeds_one_gib(self):
        plan = make_plan(Settings())
        self.assertEqual(plan["slot_count"], 384)
        self.assertAlmostEqual(plan["estimated_seconds"], 4872)
        for block in plan["blocks"]:
            m, n, k = block["shape_mnk"]
            self.assertEqual(block["dense_equivalent_flops_per_dispatch"], 2 * m * n * k)
            self.assertEqual(block["activation_dtype"], "bf16" if block["dtype"] == "bf16" else "fp16")
            if block["geometry"] == "gemv-ring":
                self.assertGreaterEqual(block["weight_bytes_per_condition"], 1 << 30)

    def test_abba_has_balanced_positions_counts_and_linear_drift(self):
        schedule = abba_schedule(rounds=3)
        self.assertEqual(schedule, abba_schedule(rounds=3))
        self.assertNotEqual(schedule, abba_schedule(rounds=3, seed=4))
        for i in range(0, len(schedule), 4):
            quad = schedule[i:i+4]
            a = [j for j, slot in enumerate(quad) if slot["arm"] == "A"]
            b = [j for j, slot in enumerate(quad) if slot["arm"] == "B"]
            self.assertEqual(len(a), 2)
            self.assertEqual(sum(a), sum(b))
            self.assertEqual(quad[0]["condition"], quad[3]["condition"])
            self.assertEqual(quad[1]["condition"], quad[2]["condition"])
        self.assertEqual({s["comparator"] for s in schedule}, set(CONDITIONS) - {"normal"})

    def test_invalid_plans_rejected_before_optional_backend_imports(self):
        for settings in (Settings(conditions=("zeros",)), Settings(rounds=0),
                         Settings(dtypes=("fp32",)), Settings(slot_seconds=float("nan")),
                         Settings(ring_bytes=128), Settings(window_seconds=1),
                         Settings(dtypes=("fp16", "fp16"))):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                make_plan(settings)

    def test_packed_patterns_have_expected_exact_bit_counts(self):
        self.assertEqual(packed_hamming_word(4, high=False).bit_count(), 8)
        self.assertEqual(packed_hamming_word(4, high=True).bit_count(), 24)
        self.assertEqual(packed_hamming_word(8, high=False).bit_count(), 4)
        self.assertEqual(packed_hamming_word(8, high=True).bit_count(), 28)
        with self.assertRaises(ValueError):
            packed_hamming_word(3, high=True)

    def test_import_and_help_without_numpy_or_mlx(self):
        code = """
import sys
class BlockOptional:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in ('numpy', 'mlx'):
            raise ImportError('optional dependency deliberately blocked')
sys.meta_path.insert(0, BlockOptional())
from joulewise.interp_energy import operand_stats, capture_hooks, rail_data_dependence
assert rail_data_dependence.make_plan(rail_data_dependence.Settings())['slot_count'] == 384
"""
        result = subprocess.run([sys.executable, "-B", "-c", code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, "-B", "scripts/interp_energy/rail_data_dependence.py", "--help"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--plan-only", result.stdout)

    def test_cli_plan_only_and_explicit_capture_gates(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary, redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            output = Path(temporary) / "plan"
            self.assertEqual(main(["--plan-only", "--out", str(output)]), 0)
            self.assertEqual(list(p.name for p in output.iterdir()), ["plan.json"])
            self.assertEqual(main(["--plan-only", "--out", str(output)]), 2)
            with self.assertRaises(SystemExit):
                main(["--execute", "--out", str(output)])
            with self.assertRaises(SystemExit):
                main(["--dry", "--powermetrics", "--out", str(output)])


@unittest.skipUnless(HAS_NUMPY, "optional NumPy is not installed")
class SyntheticTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np

    def test_related_fills_are_deterministic_and_shape_preserving(self):
        np = self.np
        for dtype in DTYPES:
            make = lambda c: synthetic_weight(c, (64, 64), seed=17, dtype=dtype)
            normal = make("normal")
            np.testing.assert_array_equal(normal, make("normal_copy"))
            np.testing.assert_array_equal(-normal, make("sign_flipped"))
            np.testing.assert_array_equal(normal * 4, make("scaled_4"))
            np.testing.assert_array_equal(np.sort(normal, axis=-1), make("sorted_rows"))
            for condition in CONDITIONS:
                values = make(condition)
                self.assertEqual(values.shape, (64, 64))
                self.assertTrue(np.isfinite(values).all())
            self.assertEqual((make("zeros_50") == 0).sum(), 2048)
            self.assertEqual((make("zeros_90") == 0).sum(), 3686)

    def test_dry_cli_runs_tiny_surrogate_only_and_retains_all_slots(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            output = Path(temporary) / "dry"
            result = subprocess.run([sys.executable, "-B", "scripts/interp_energy/rail_data_dependence.py", "--dry", "--out", str(output)],
                                    cwd=ROOT, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p.name for p in output.iterdir()}, {"plan.json", "timings.jsonl"})
            plan = json.loads((output / "plan.json").read_text())
            records = [json.loads(line) for line in (output / "timings.jsonl").read_text().splitlines()]
            timings = [r for r in records if r["kind"] == "timing"]
            self.assertEqual(len(timings), 384)
            self.assertEqual(records[-1]["kind"], "complete")
            for block in plan["blocks"]:
                members = [r for r in timings if r["block"] == block["id"]]
                self.assertEqual(len({r["dispatches"] for r in members}), 1)
                for r in members:
                    self.assertEqual(r["dense_equivalent_flops"], r["dispatches"] * block["dense_equivalent_flops_per_dispatch"])
                    self.assertGreater(r["elapsed_ns"], 0)
                    self.assertEqual(r["backend"], "numpy-float32-surrogate")

    def test_dry_rejects_capture_factory_and_preserves_failed_run(self):
        plan = make_plan(Settings(dry=True, dtypes=("fp16",), geometries=("gemm",), conditions=("normal", "zeros")))
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            with self.assertRaises(ValueError):
                execute_plan(plan, Path(temporary) / "forbidden", capture_factory=lambda *_: None)
            self.assertFalse((Path(temporary) / "forbidden").exists())
            backend = NumpyDryBackend()
            with patch.object(backend, "cycle", side_effect=RuntimeError("synthetic failure")):
                with self.assertRaisesRegex(RuntimeError, "synthetic failure"):
                    execute_plan(plan, Path(temporary) / "partial", backend=backend)
            records = [json.loads(line) for line in (Path(temporary) / "partial/timings.jsonl").read_text().splitlines()]
            self.assertEqual(records[-1]["kind"], "aborted")

    def test_native_runner_seam_brackets_after_preparation_and_equal_dispatches(self):
        # Exercise orchestration without MLX, hardware, sleep, or collectors.
        plan = make_plan(Settings(dtypes=("fp16",), geometries=("gemm",), conditions=("normal", "zeros")))
        plan["blocks"][0]["shape_mnk"] = [8, 64, 64]
        plan["settings"]["slot_seconds"] = 0.000001
        events = []
        @contextmanager
        def capture(path, clock):
            events.append("capture_start")
            yield {"synthetic": True}
            events.append("capture_stop")
        class Tiny(NumpyDryBackend):
            def prepare(self, *args):
                events.append("prepare")
                return super().prepare(*args)
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            execute_plan(plan, Path(temporary) / "native-seam", backend=Tiny(), capture_factory=capture, clock=FakeClock())
        self.assertEqual(events, ["prepare", "capture_start", "capture_stop"])

    def test_calibrated_budget_refusal_keeps_partial_evidence_without_capture(self):
        plan = make_plan(Settings(dtypes=("fp16",), geometries=("gemm",), conditions=("normal", "zeros")))
        plan["blocks"][0]["shape_mnk"] = [8, 64, 64]
        plan["settings"]["slot_seconds"] = 0.000001
        capture = unittest.mock.Mock()
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            output = Path(temporary) / "aborted-budget"
            with patch("joulewise.interp_energy.rail_data_dependence.time.perf_counter", side_effect=[0, 10000]):
                with self.assertRaisesRegex(RuntimeError, "exceeds remaining window"):
                    execute_plan(plan, output, backend=NumpyDryBackend(), capture_factory=capture, clock=FakeClock())
            capture.assert_not_called()
            records = [json.loads(line) for line in (output / "timings.jsonl").read_text().splitlines()]
            self.assertEqual([r["kind"] for r in records], ["setup", "aborted"])


if __name__ == "__main__":
    unittest.main()
