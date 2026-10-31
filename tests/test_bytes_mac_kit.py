"""R8.6 non-claim kit: real config parser, fixed-tree reader and fake MLX."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from joulewise.b5 import chain
from joulewise.b6 import compose, queue
from joulewise.b6.pack_registration import Registration
from joulewise.schemas import BenchmarkConfig
from scripts import bytes_mac_kit as kit, bytes_stream_test as probe
from tests.test_bytes_stream_capture import Array, Buffer, Clock

ROOT = Path(__file__).resolve().parents[1]


class MacKitTests(unittest.TestCase):
    def test_generated_tree_and_configs_validate_without_a_pack_registration(self):
        # R8: all committed products must agree with the generator, including
        # the README and the generator digest in plan_tree.json.
        files = kit.build_files(ROOT)
        for path, raw in files.items():
            self.assertEqual((ROOT/path).read_bytes(),raw,str(path))
        tree = json.loads(files[kit.KIT / "plan_tree.json"])
        self.assertTrue(tree["non_claim"])
        self.assertEqual(len(chain.stage_plan(tree)), len(tree["stage_graph"]))
        self.assertNotIn("bytes-mac-check", json.loads((ROOT / "configs/b6/loop.json").read_bytes())["base_order"])
        self.assertFalse((ROOT / "configs/b6/packs/bytes-mac-check").exists())
        reg = Registration({"pack_id": "bytes-mac-check", "session_shape": "fixed", "corpus": {},
                            "plan_tree_ref": str(kit.KIT / "plan_tree.json")})
        layout = compose.layout(queue.Selection((reg.pack_id,), 1), {reg.pack_id: reg}, ROOT)
        self.assertEqual(compose.render(layout)[1]["plan_tree.json"], files[kit.KIT / "plan_tree.json"])
        self.assertEqual(compose.smoke_keep(layout), json.loads(files[Path("configs/b6/smoke_keep.json")])["bytes_mac_check"])
        plan = json.loads(files[kit.KIT / "collection_plan.json"])
        counts = Counter((m["model_id"], m["purpose"]) for m in plan["members"])
        roster = json.loads((ROOT / "configs/campaigns/bytes_v1/roster.json").read_bytes())["models"]
        # Integer counts come directly from R8.6: 10*5 checks + 2*12 soaks
        # + 3 regimes * 2 ends * 2 alternating large/reference pairs = 98.
        self.assertEqual(len(plan["members"]), 98)
        for m in roster:
            self.assertEqual(counts[m["model_id"], "check"], 5)
        for mid in kit.LONG[:2]:
            self.assertEqual(counts[mid, "soak"], 12)
        for stage in tree["stage_graph"]:
            ref = stage.get("input", {})
            if ref.get("kind") != "manifest":
                continue
            raw = (ROOT / ref["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), ref["sha256"])
            manifest = json.loads(raw)
            self.assertEqual(stage["expected_count"], len(manifest["executed_order"]))
            for row in manifest["executed_order"]:
                path = ROOT / ref["path"]
                raw_config = (path.parent / row["config"]).read_bytes()
                if "config_sha256" in row:  # Inherited NEG-8 manifests predate per-config hashes.
                    self.assertEqual(hashlib.sha256(raw_config).hexdigest(), row["config_sha256"])
                parsed = BenchmarkConfig.from_mapping(json.loads(raw_config))
                self.assertFalse(parsed.config_warnings)
        for member in plan["members"]:
            cfg = json.loads((ROOT / member["config_path"]).read_bytes())
            self.assertIn("non-claim", cfg["run_metadata"]["tags"])
            if member["model_id"] != "reference":
                self.assertEqual(cfg["workload_profile"]["prompt_tokens"], 2048)
                self.assertEqual(cfg["workload_profile"]["output_tokens"], 512)
        for mid in kit.LONG:
            for end in ("start", "end"):
                rows = [m for m in plan["members"] if m["stage_id"] == f"bytes-mac-check-test7-{mid}-{end}"]
                self.assertEqual([m["model_id"] for m in rows], [mid, "reference"] * 2)

    def test_readme_uses_absolute_python_and_current_probe_contract(self):
        self.assertIn('/opt/homebrew/bin/python3.13 scripts/bytes_stream_test.py',kit.README)
        self.assertIn('--device DEVICE --idle-s 57.6 --settle-s 3',kit.README)
        self.assertIn('three 3 s settle gaps',kit.README)
        self.assertIn('6731d5249',kit.README)
        self.assertIn('physical_differences',kit.README)
        self.assertNotIn('Run `python3.13',kit.README)
        for command in ('scan SCAN.json','read INPUT.json'):
            self.assertIn('/opt/homebrew/bin/python3.13 scripts/bytes_stream_test.py '+command,kit.README)
            self.assertNotIn('`scripts/bytes_stream_test.py '+command,kit.README)
        self.assertIn('/opt/homebrew/bin/python3.13 scripts/bytes_mac_kit.py --check',kit.README)
        self.assertIn('measurement_boundary_label.rails',kit.README)

    def test_generator_reproduces_in_scratch_and_only_writes_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            files = kit.generate(tmp)
            for path, raw in files.items():
                self.assertTrue(path.is_relative_to(kit.KIT) or path == Path("configs/b6/smoke_keep.json"))
                self.assertEqual((Path(tmp) / path).read_bytes(), raw)
        result = subprocess.run([sys.executable, str(ROOT / "scripts/bytes_stream_test.py"), "--help"],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_stream_cli_runs_with_fake_mlx_and_writes_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "mlx").mkdir()
            (root / "mlx/__init__.py").write_text("")
            (root / "mlx/core.py").write_text(
                "__version__ = '0.31.2'\n"
                "uint8 = 'uint8'\n"
                "from tests.test_bytes_stream_capture import Buffer\n"
                "def ones(shape, dtype):\n"
                "    if any(n > 2**31-1 for n in shape): raise TypeError('axis limit')\n"
                "    return Buffer(shape)\n"
                "def reshape(data,shape): return Buffer(shape,data.storage,data.offset)\n"
                "def sum(data): return object()\n"
                "def eval(*values): pass\n"
                "def synchronize(): pass\n")
            receipt = root / "stream.json"
            env = {**os.environ, "PYTHONPATH": str(root)}
            result = subprocess.run([sys.executable, str(ROOT / "scripts/bytes_stream_test.py"),
                "--bytes", str(probe.GEOMETRY_BYTES), "--repeats", str(probe.RING_BYTES//probe.GEOMETRY_BYTES), "--arm", "R", "--device", "macbook_m3_max",
                "--idle-s", "0", "--settle-s", "0", "--out", str(receipt)],
                env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(receipt.read_bytes())
            self.assertEqual(data["schema_version"], probe.SCHEMA)
            self.assertEqual(data["stack"]["hardware_unit"]["device"], "macbook_m3_max")
            self.assertEqual(data["stack"]["runtime_version"]["version"], "0.31.2")
            self.assertEqual(data["bytes_read"], probe.RING_BYTES)
            self.assertEqual(data["clock"], "CLOCK_MONOTONIC_RAW")
            self.assertTrue(data["non_claim"])
            # A completed kernel must have a positive span, directly from
            # the ordering of its own monotonic stamps; no timing cutoff.
            self.assertGreater(data["end_ns"], data["start_ns"])
            spans = [data[key] for key in ("idle_pre_start_ns", "idle_pre_end_ns",
                "start_ns", "end_ns", "idle_post_start_ns", "idle_post_end_ns")]
            self.assertTrue(all(type(stamp) is int for stamp in spans))
            self.assertEqual(spans, sorted(spans))

    def test_stream_evaluates_each_read_and_records_own_span(self):
        class FakeMLX(Array):
            def __init__(self):
                super().__init__(Clock());self.sums=0;self.evaluations=0
            def sum(self,value):
                self.sums+=1
                return object()
            def eval(self,*values):
                self.evaluations+=1
        mx=FakeMLX()
        # Integer timestamps/counts are bit-exact properties. One second is
        # exactly 10^9 ns; no assertion compares measured hardware timings.
        span_keys = ("idle_pre_start_ns", "idle_pre_end_ns", "start_ns", "end_ns",
                     "idle_post_start_ns", "idle_post_end_ns")
        span_values = (1_000_000_000, 2_000_000_000, 4_000_000_000, 5_000_000_000,
                       7_000_000_000, 8_000_000_000)
        stamps = iter(span_values)
        sleeps = []
        result = probe.stream(probe.GEOMETRY_BYTES, probe.RING_BYTES//probe.GEOMETRY_BYTES, arm="R", device="macbook_m3_max", idle_s=1, settle_s=2,
                              mx=mx, clock_ns=lambda: next(stamps), sleep=sleeps.append)
        self.assertEqual([result[key] for key in span_keys], list(span_values))
        self.assertEqual(sleeps, [2, 1, 2, 2, 1])
        self.assertEqual(result["schema_version"], probe.SCHEMA)
        self.assertEqual(result["bytes_read"], probe.RING_BYTES)
        # Integer 10^9 ns divided by 10^9 is the bit-exact value 1.0.
        self.assertEqual(result["duration_s"], 1.0)
        self.assertEqual(mx.sums,1+probe.RING_BYTES//probe.GEOMETRY_BYTES)  # Warm + one sweep.
        self.assertEqual(mx.evaluations,2+mx.sums)  # Ring, all views, every fresh sum.
        for args in ((0, 3), (1024, 0), (True, 1)):
            with self.assertRaises(ValueError):
                probe.stream(*args, device="macbook_m3_max", mx=mx)
