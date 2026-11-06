import json
import importlib.util
import tempfile
import unittest
from pathlib import Path

import hashlib
import sys

from joulewise.align.qwen4_quant_quality import capture, main, score

HAS_NUMPY = importlib.util.find_spec("numpy") is not None

@unittest.skipUnless(HAS_NUMPY, "optional NumPy")
class QuantQualityTests(unittest.TestCase):
    prompts = [{"name": "tiny", "input_ids": [1, 2, 3, 4]}]

    def test_identical_logits_are_acceptable(self):
        import numpy as np
        rng = np.random.default_rng(7)
        logits = {"tiny": rng.normal(size=(4, 16)).astype(np.float32)}
        with tempfile.TemporaryDirectory() as directory:
            ref = Path(directory) / "ref.npz"
            capture(logits, self.prompts, ref, top_k=5)
            result = score(ref, logits)
        self.assertEqual(result["classification"], "acceptable")
        self.assertAlmostEqual(result["summary"]["mean_projected_kl"], 0, places=6)
        self.assertAlmostEqual(result["summary"]["mean_nll_delta"], 0, places=6)

    def test_bad_variant_rejects_and_reports_per_token(self):
        import numpy as np
        teacher = np.tile(np.arange(16, dtype=np.float32), (4, 1))
        student = -teacher
        with tempfile.TemporaryDirectory() as directory:
            ref = Path(directory) / "ref.npz"
            capture({"tiny": teacher}, self.prompts, ref, top_k=5)
            result = score(ref, {"tiny": student})
        self.assertEqual(result["classification"], "reject")
        self.assertEqual(len(result["tokens"]), 4)
        self.assertEqual(sum("nll_delta" in x for x in result["tokens"]), 3)

    def test_integrity_and_shape_fail_closed(self):
        import numpy as np
        logits = {"tiny": np.zeros((4, 16), np.float32)}
        with tempfile.TemporaryDirectory() as directory:
            ref = Path(directory) / "ref.npz"
            capture(logits, self.prompts, ref, top_k=5)
            ref.write_bytes(ref.read_bytes() + b"x")
            with self.assertRaises(ValueError): score(ref, logits)

    def test_compact_reference_omits_full_logits(self):
        import numpy as np
        logits = {"tiny": np.zeros((4, 100), np.float32)}
        with tempfile.TemporaryDirectory() as directory:
            ref = Path(directory) / "ref.npz"
            capture(logits, self.prompts, ref, top_k=5)
            with np.load(ref) as data:
                self.assertLess(sum(x.nbytes for x in data.values()), logits["tiny"].nbytes)
            self.assertEqual(json.loads(Path(str(ref)+".json").read_text())["top_k"], 5)


FAKE_ADAPTER = """
import numpy as np
LOADS = []
CALLS = []
def load(model_path, manifest_sha256=None):
    LOADS.append((model_path, manifest_sha256))
    return {"handle": model_path}
def teacher_forced_logits(model, input_ids):
    CALLS.append((model, list(input_ids)))
    return np.tile(np.arange(16, dtype=np.float32), (len(input_ids), 1))
"""


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@unittest.skipUnless(HAS_NUMPY, "optional NumPy")
class GoldStreamAndAdapterTests(unittest.TestCase):
    prompts = [{"name": "tiny", "input_ids": [1, 2, 3, 4]}]

    def make_work(self, root):
        """Minimal qwen4-gold-stream/v1 work folder with a completed head unit."""
        import numpy as np
        work = Path(root) / "work"
        head = work / "parity" / "head" / "tiny-bf16-real" / "reference"
        head.mkdir(parents=True)
        logits = np.random.default_rng(3).normal(size=(1, 4, 16)).astype(np.float32)
        np.save(head / "output.npy", logits)
        rel = "parity/head/tiny-bf16-real/reference/output.npy"
        (work / "parity" / "provenance.json").write_text(json.dumps(
            {"schema": "qwen4-gold/v1", "fingerprint": "p" * 64, "prompts": self.prompts}))
        (work / "manifest.json").write_text(json.dumps({
            "schema": "qwen4-gold-stream/v1", "fingerprint": "f" * 64,
            "units": {"head": {"state": "done", "status": "PASS", "result_sha256": "r" * 64,
                               "artifacts": {rel: _sha(work / rel)}}},
            "chain": {"head": {"bf16:tiny": str(work / rel)}}}))
        return work, logits, rel

    def test_capture_reads_stream_work_folder_and_pins_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            work, logits, rel = self.make_work(directory)
            ref = Path(directory) / "ref.npz"
            self.assertEqual(main(["capture", "--gold-root", str(work), "--top-k", "5",
                                   "--output", str(ref)]), 0)
            sidecar = json.loads(Path(str(ref) + ".json").read_text())
            self.assertEqual(sidecar["source"]["head_outputs"]["tiny"]["sha256"], _sha(work / rel))
            self.assertEqual(sidecar["source"]["gold_fingerprint"], "f" * 64)
            self.assertEqual(sidecar["prompts"][0]["input_ids"], [1, 2, 3, 4])
            self.assertEqual(score(ref, {"tiny": logits})["classification"], "acceptable")
            with self.assertRaises(ValueError):  # gold prompts are authoritative
                bad = Path(directory) / "p.json"
                bad.write_text(json.dumps([{"name": "tiny", "input_ids": [1, 2, 3, 5]}]))
                main(["capture", "--gold-root", str(work), "--prompts-json", str(bad),
                      "--top-k", "5", "--output", str(ref)])
            (work / rel).write_bytes((work / rel).read_bytes()[:-4] + b"\0\0\0\0")
            with self.assertRaises(ValueError):  # changed head output fails closed
                main(["capture", "--gold-root", str(work), "--top-k", "5", "--output", str(ref)])

    def test_capture_refuses_incomplete_head_unit(self):
        with tempfile.TemporaryDirectory() as directory:
            work, _, _ = self.make_work(directory)
            manifest = json.loads((work / "manifest.json").read_text())
            del manifest["units"]["head"]
            manifest["current_unit"] = {"unit": "head", "state": "running"}
            (work / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                main(["capture", "--gold-root", str(work), "--top-k", "5",
                      "--output", str(Path(directory) / "ref.npz")])

    def test_score_uses_reference_prompts_and_loads_model_once(self):
        import numpy as np
        custom = [{"name": "custom-a", "input_ids": [3, 1, 2]}, {"name": "custom-b", "input_ids": [4, 5]}]
        with tempfile.TemporaryDirectory() as directory:
            d = Path(directory)
            (d / "prompts.json").write_text(json.dumps(custom))
            np.savez(d / "logits.npz", **{p["name"]: np.tile(np.arange(16, dtype=np.float32),
                                                              (len(p["input_ids"]), 1)) for p in custom})
            ref = d / "ref.npz"
            main(["capture", "--prompts-json", str(d / "prompts.json"), "--logits-npz", str(d / "logits.npz"),
                  "--top-k", "5", "--output", str(ref)])
            (d / "qq_fake_adapter.py").write_text(FAKE_ADAPTER)
            sys.path.insert(0, directory)
            try:
                out = d / "score.json"
                # No --prompts-json: the reference's pinned prompts must be scored.
                main(["score", "--reference", str(ref), "--adapter", "qq_fake_adapter",
                      "--model", "/models/x", "--manifest-sha256", "a" * 64,
                      "--variant-name", "fake", "--output", str(out)])
                fake = sys.modules["qq_fake_adapter"]
                self.assertEqual(fake.LOADS, [("/models/x", "a" * 64)])
                self.assertEqual([c[1] for c in fake.CALLS], [[3, 1, 2], [4, 5]])
                self.assertTrue(all(c[0] == {"handle": "/models/x"} for c in fake.CALLS))
                result = json.loads(out.read_text())
                self.assertEqual(result["classification"], "acceptable")
                self.assertEqual(result["variant"]["manifest_sha256"], "a" * 64)
                self.assertIn("reference_manifest_sha256", result)
            finally:
                sys.path.remove(directory)
                sys.modules.pop("qq_fake_adapter", None)


class PassRuleTests(unittest.TestCase):
    def test_e2e_report_records_exactly_this_policy(self):
        from joulewise.align import qwen4_quant_quality as qq
        from scripts import qwen4exp_e2e_eval as e2e
        record = e2e.quality_policy_record()
        self.assertEqual({k: record[k] for k in qq.policy_record()}, qq.policy_record())

    def test_classify_labels(self):
        from joulewise.align.qwen4_quant_quality import classify
        good = {"mean_projected_kl": .01, "p99_projected_kl": .05, "top1_agreement": .95,
                "top5_overlap": .95, "mean_nll_delta": .01}
        self.assertEqual(classify(good), "acceptable")
        self.assertEqual(classify({**good, "p99_projected_kl": .2}), "marginal")
        self.assertEqual(classify({**good, "top1_agreement": .5}), "reject")


class RunnerScriptTests(unittest.TestCase):
    def test_documented_command_imports_from_any_directory(self):
        """``python3 -B scripts/run_qwen4_quant_quality.py`` puts scripts/ on sys.path, not the root."""
        import subprocess
        script = Path(__file__).resolve().parents[1] / "scripts" / "run_qwen4_quant_quality.py"
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, "-B", str(script), "capture", "--help"], cwd=directory,
                                    capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--gold-root", result.stdout)


@unittest.skipUnless(HAS_NUMPY, "optional NumPy")
class GoldWorkFolderStreamingTests(unittest.TestCase):
    prompts = [{"name": "a", "input_ids": [1, 2, 3, 4, 5]}, {"name": "b", "input_ids": [6, 7, 8]}]

    def make_work(self, root):
        import numpy as np
        work = Path(root) / "work"
        artifacts, chain, logits = {}, {}, {}
        rng = np.random.default_rng(5)
        for p in self.prompts:
            rel = f"parity/head/{p['name']}-bf16-real/reference/output.npy"
            (work / rel).parent.mkdir(parents=True)
            value = rng.normal(size=(1, len(p["input_ids"]), 32)).astype(np.float32)
            np.save(work / rel, value)
            artifacts[rel], chain["bf16:" + p["name"]], logits[p["name"]] = _sha(work / rel), str(work / rel), value[0]
        (work / "parity" / "provenance.json").write_text(json.dumps({"fingerprint": "p" * 64, "prompts": self.prompts}))
        (work / "manifest.json").write_text(json.dumps({
            "schema": "qwen4-gold-stream/v1", "fingerprint": "f" * 64,
            "units": {"head": {"state": "done", "status": "REFERENCE_CHAIN_ONLY", "artifacts": artifacts}},
            "chain": {"head": chain}}))
        return work, logits

    def test_moved_work_folder_resolves_chain_against_its_manifest(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            work, logits = self.make_work(directory)
            moved = Path(directory) / "elsewhere" / "copied-work"
            moved.parent.mkdir()
            shutil.move(str(work), str(moved))  # chain still names the old absolute folder
            ref = Path(directory) / "ref.npz"
            self.assertEqual(main(["capture", "--gold-root", str(moved), "--top-k", "5", "--output", str(ref)]), 0)
            self.assertEqual(score(ref, logits)["classification"], "acceptable")
            # A recorded path that is not a pinned artifact is refused, moved or not.
            manifest = json.loads((moved / "manifest.json").read_text())
            manifest["chain"]["head"]["bf16:a"] = "/elsewhere/parity/head/zzz/reference/output.npy"
            (moved / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                main(["capture", "--gold-root", str(moved), "--top-k", "5", "--output", str(ref)])

    def test_manifest_relative_rules(self):
        from joulewise.align.qwen4_quant_quality import manifest_relative
        pinned = {"parity/head/a-bf16-real/reference/output.npy": "x"}
        rel = "parity/head/a-bf16-real/reference/output.npy"
        self.assertEqual(manifest_relative(Path("/new/work"), "/old/run/work/" + rel, pinned), rel)
        self.assertEqual(manifest_relative(Path("/new/work"), rel, pinned), rel)
        for bad in ("../" + rel, "/old/run/work/parity/head/b-bf16-real/reference/output.npy"):
            with self.assertRaises(ValueError):
                manifest_relative(Path("/new/work"), bad, pinned)

    def test_load_gold_streams_one_prompt_at_a_time_through_mmap(self):
        import numpy as np
        from unittest import mock
        from joulewise.align import qwen4_quant_quality as qq
        with tempfile.TemporaryDirectory() as directory:
            work, _ = self.make_work(directory)
            real_load, opened = np.load, []
            def counting_load(path, *a, **kw):
                opened.append((Path(path).parent.parent.name, kw.get("mmap_mode")))
                return real_load(path, *a, **kw)
            with mock.patch.object(np, "load", counting_load):
                logits, prompts, _ = qq.load_gold(work)
                self.assertEqual(opened, [])  # nothing is read up front
                self.assertEqual(len(logits), 2)
                first = logits["a"]
                self.assertIsInstance(first, np.memmap)
                self.assertEqual(opened, [("a-bf16-real", "r")])
            # Hash is re-checked when a prompt is opened, not only at listing time.
            target = work / "parity/head/b-bf16-real/reference/output.npy"
            target.write_bytes(target.read_bytes()[:-4] + b"\0\0\0\0")
            with self.assertRaises(ValueError):
                logits["b"]

    def test_chunked_capture_and_score_equal_whole_array_results(self):
        import numpy as np
        from unittest import mock
        from joulewise.align import qwen4_quant_quality as qq
        rng = np.random.default_rng(9)
        teacher = {p["name"]: rng.normal(size=(len(p["input_ids"]), 32)).astype(np.float32) for p in self.prompts}
        student = {k: v + rng.normal(scale=.3, size=v.shape).astype(np.float32) for k, v in teacher.items()}
        with tempfile.TemporaryDirectory() as directory:
            outputs = {}
            for rows in (2, 10_000):
                ref = Path(directory) / f"ref-{rows}.npz"
                with mock.patch.object(qq, "CHUNK_ROWS", rows):
                    capture(teacher, self.prompts, ref, top_k=5)
                    result = score(ref, student)
                with np.load(ref) as data:
                    outputs[rows] = ({k: data[k].copy() for k in data.files}, result["summary"], result["tokens"])
        (a, sa, ta), (b, sb, tb) = outputs[2], outputs[10_000]
        self.assertEqual(sorted(a), sorted(b))
        for key in a:
            np.testing.assert_array_equal(a[key], b[key])
        self.assertEqual(sa, sb)
        self.assertEqual(ta, tb)
        self.assertEqual(sum("nll_delta" in t for t in ta), 4 + 2)

    def test_score_reads_adapter_logits_lazily(self):
        import numpy as np
        from joulewise.align import qwen4_quant_quality as qq
        calls = []
        module = type(sys)("qq_lazy_adapter")
        module.teacher_forced_logits = lambda handle, ids: calls.append(list(ids)) or np.zeros((len(ids), 32), np.float32)
        sys.modules["qq_lazy_adapter"] = module
        try:
            logits = qq.load_adapter("qq_lazy_adapter", "/m", self.prompts)
            self.assertEqual(calls, [])
            logits["b"]
            self.assertEqual(calls, [[6, 7, 8]])
        finally:
            sys.modules.pop("qq_lazy_adapter", None)


class MlxAdapterContractTests(unittest.TestCase):
    def test_load_requires_pinned_manifest(self):
        from joulewise.align import qwen4_quant_mlx_adapter as adapter
        for pin in (None, "", "A" * 64, "a" * 63):
            with self.assertRaises(ValueError):
                adapter.load("/nonexistent", manifest_sha256=pin)

    def fakes(self, order, resident=0, device=200 * 10**9):
        """Fake mx and converter modules plus patched live-kit guards."""
        import types
        from unittest import mock
        from joulewise.align import qwen4_quant_mlx_adapter as adapter
        live = adapter._live()
        mx = types.ModuleType("mlx.core")
        mx.device_info = lambda: {"max_recommended_working_set_size": device}
        mx.set_cache_limit = lambda v: order.append(("cache", v))
        mx.set_memory_limit = lambda v: order.append(("limit", v))
        mx.reset_peak_memory = lambda: None
        mx.get_peak_memory = lambda: 0
        mlx = types.ModuleType("mlx"); mlx.core = mx
        converter = types.ModuleType("align_convert_qwen4_exp")
        model = types.SimpleNamespace(eval=lambda: None)
        converter.load_verified_model = lambda path, pin, lazy: order.append(("load", str(path), lazy)) or (model, {})
        stats = {"0": {"path": "/Volumes/JW-EXT/flashnext/ple.bin", "resident_bytes": resident}}
        patches = [mock.patch.dict(sys.modules, {"mlx": mlx, "mlx.core": mx, "align_convert_qwen4_exp": converter}),
                   mock.patch.object(live, "measurement_agents_loaded", return_value=[]),
                   mock.patch.object(live, "table_stats", lambda m: order.append(("tables",)) or stats),
                   mock.patch.object(live, "external", lambda p: order.append(("external", str(p))) or Path(p))]
        return adapter, live, patches

    def test_load_applies_kit_guards_before_any_weight(self):
        order = []
        adapter, live, patches = self.fakes(order)
        for p in patches: p.start()
        try:
            handle = adapter.load("/Volumes/JW-EXT/flashnext/maxfit", "a" * 64)
        finally:
            for p in reversed(patches): p.stop()
        kinds = [o[0] for o in order]
        self.assertEqual(order[0], ("external", "/Volumes/JW-EXT/flashnext/maxfit"))
        self.assertLess(kinds.index("cache"), kinds.index("load"))
        self.assertLess(kinds.index("limit"), kinds.index("load"))
        self.assertEqual(("limit", int(live.METAL_CAP)), order[kinds.index("limit")])  # min(kit cap, device)
        self.assertEqual(kinds[-2:], ["tables", "external"])  # PLE pages from JW-EXT, checked after load
        self.assertEqual(handle.metal_cap_bytes, int(live.METAL_CAP))
        order.clear()  # A smaller device working set clamps the cap.
        adapter, live, patches = self.fakes(order, device=64 * 10**9)
        for p in patches: p.start()
        try:
            self.assertEqual(adapter.load("/Volumes/JW-EXT/flashnext/maxfit", "a" * 64).metal_cap_bytes, 64 * 10**9)
        finally:
            for p in reversed(patches): p.stop()
        self.assertIn(("limit", 64 * 10**9), order)

    def test_load_refuses_agents_internal_disk_and_ple_over_cap(self):
        from unittest import mock
        order = []
        adapter, live, patches = self.fakes(order)
        for p in patches: p.start()
        try:
            with mock.patch.object(live, "measurement_agents_loaded", return_value=["com.joulewise.night.chain"]):
                with self.assertRaisesRegex(ValueError, "measurement agents"):
                    adapter.load("/Volumes/JW-EXT/flashnext/maxfit", "a" * 64)
            self.assertEqual(order, [])  # refused before touching the artifact
        finally:
            for p in reversed(patches): p.stop()
        # The real kit guard: anything outside /Volumes/JW-EXT is refused.
        adapter, live, patches = self.fakes(order)
        patches = [p for p in patches if getattr(p, "attribute", None) != "external"]
        for p in patches: p.start()
        try:
            with self.assertRaisesRegex(ValueError, "JW-EXT"):
                adapter.load("/private/tmp/maxfit", "a" * 64)
            self.assertNotIn("load", [o[0] for o in order])
        finally:
            for p in reversed(patches): p.stop()
        order.clear()
        adapter, live, patches = self.fakes(order, resident=int(live.PLE_CAP) + 1)
        for p in patches: p.start()
        try:
            with self.assertRaisesRegex(ValueError, "21.5 GB"):
                adapter.load("/Volumes/JW-EXT/flashnext/maxfit", "a" * 64)
        finally:
            for p in reversed(patches): p.stop()

    @unittest.skipUnless(importlib.util.find_spec("mlx") is not None, "native MLX only")
    def test_teacher_forced_logits_rechecks_guards_per_prompt(self):
        import mlx.core as mx
        from unittest import mock
        from joulewise.align import qwen4_quant_mlx_adapter as adapter
        live = adapter._live()
        tiny = lambda ids: mx.ones((1, ids.shape[1], 8), dtype=mx.bfloat16)  # synthetic, no weights
        checks = []
        with mock.patch.object(live, "table_stats", lambda m: checks.append(1) or {}):
            handle = adapter.Handle(model=tiny, metal_cap_bytes=10**12, artifact=Path("/Volumes/JW-EXT/x"))
            out = adapter.teacher_forced_logits(handle, [1, 2, 3])
            self.assertEqual(out.shape, (1, 3, 8))
            self.assertEqual(str(out.dtype), "float32")
            self.assertEqual(checks, [1])
            handle.metal_cap_bytes = 0  # any Metal use now exceeds the cap
            with self.assertRaisesRegex(ValueError, "Metal peak"):
                adapter.teacher_forced_logits(handle, [1, 2])


if __name__ == "__main__": unittest.main()
