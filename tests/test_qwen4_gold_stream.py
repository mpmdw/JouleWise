"""Synthetic checkpoints only. No network, Metal, or study inputs required."""
import argparse
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from joulewise.align.qwen4_gold.core import IndexedCheckpoint, sha256, write_json
from joulewise.align.qwen4_gold.stream import (GIB, HubSource, StreamDriver, disk_guard,
                                             storage_plan, unit_plan)
from joulewise.align.qwen4_gold.stream_ple import (SparseCheckpoint, atomic_npy, extract_part,
                                                  official_plan)

HAS_ARRAYS = importlib.util.find_spec("numpy") is not None
HAS_SAFE = importlib.util.find_spec("safetensors") is not None
HAS_REF = importlib.util.find_spec("transformers") is not None and importlib.util.find_spec("torch") is not None
HAS_MLX = importlib.util.find_spec("mlx") is not None and importlib.util.find_spec("mlx.core") is not None


def options(work, resume=False):
    return argparse.Namespace(work=str(work), resume=resume, mlx_module=__file__, adapter_dependency=[],
                              ref_python=sys.executable, mlx_python=sys.executable, min_free_gb=0,
                              max_staging_gb=12, max_gb=12, timeout=60, prompts_json=None,
                              seed=20261105, random_scale=1., convert_out=None,
                              canonical_converter=None, canonical_module=None, shared_shards="retain")


RUNTIMES = {"reference": {"transformers": "5.22.1"}, "mlx": {"fixture": True}}


class LocalSource:
    """A local file-serving function in place of every hub download."""
    def __init__(self, fixture, work):
        self.fixture, self.root = Path(fixture), Path(work) / "staging/checkpoint"
        self.downloads = []

    def prepare(self):
        self.root.mkdir(parents=True, exist_ok=True)
        for name in ("config.json", "model.safetensors.index.json"):
            shutil.copyfile(self.fixture / name, self.root / name)
        index = json.loads((self.fixture / "model.safetensors.index.json").read_text())["weight_map"]
        return {"repo": "synthetic", "revision": "fixture", "shards": {
            f: {"sha256": sha256(self.fixture / f), "size": (self.fixture / f).stat().st_size}
            for f in set(index.values())}}

    def download(self, name):
        self.downloads.append(name)
        shutil.copyfile(self.fixture / name, self.root / name)
        return self.root / name


def synthetic(root):
    import numpy as np
    from safetensors.numpy import save_file
    root.mkdir(parents=True)
    groups = {
        "shared.safetensors": {"model.embed_tokens.weight": np.ones((128, 2), np.float32),
                               "model.layers.1.weight": np.ones((2, 2), np.float32)},
        "zero.safetensors": {"model.layers.0.weight": np.ones((2, 2), np.float32)},
        "final.safetensors": {"model.hyper_connection_mixer.hc_norm.weight": np.ones(4, np.float32)},
        "head.safetensors": {"lm_head.weight": np.ones((128, 2), np.float32)},
    }
    index = {}
    for filename, tensors in groups.items():
        save_file(tensors, root / filename)
        index.update(dict.fromkeys(tensors, filename))
    write_json(root / "model.safetensors.index.json", {"weight_map": index})
    write_json(root / "config.json", {"num_hidden_layers": 2, "hidden_size": 2, "hc_count": 2,
                                       "vocab_size": 128, "layer_types": ["linear_attention"]*2})


def fake_unit(driver, unit):
    """Lifecycle test double, explicitly not MLX evidence."""
    import numpy as np
    for filename in driver.plan["shards"][unit]:
        if not (driver.harness.checkpoint.root / filename).is_file():
            raise AssertionError("unit started without its weights")
    number = driver.plan["units"].index(unit)
    chain = {}
    for dtype in ("fp32", "bf16"):
        for prompt in driver.prompts:
            key = dtype + ":" + prompt["name"]
            value = 1.
            if number:
                prior = driver.plan["units"][number-1]
                value += float(np.load(driver.state["chain"][prior][key], allow_pickle=False)[0])
            path = driver.work / "fake" / unit / (key.replace(":", "-") + ".npy")
            atomic_npy(path, np.array([value], dtype=np.float32))
            chain[key] = str(path)
    report = driver.work / "fake" / (unit + ".json")
    write_json(report, {"unit": unit, "status": "PASS", "test_double": True})
    return {"state": "done", "status": "PASS", "result": str(report), "result_sha256": sha256(report),
            "chain": chain, "artifacts": {str(Path(p).relative_to(driver.work)): sha256(p) for p in chain.values()}}


class DiskPolicyTests(unittest.TestCase):
    def test_free_space_and_staging_refuse_before_downloading(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "bytes").write_bytes(b"abcd")
            with patch("shutil.disk_usage", return_value=argparse.Namespace(free=100)):
                with self.assertRaisesRegex(RuntimeError, "free-disk guard"):
                    disk_guard(root, root, 101, 0, 1)
                with self.assertRaisesRegex(RuntimeError, "staging guard"):
                    disk_guard(root, root, 3, 0, 6/GIB)

    def test_explicit_hub_cache_and_pins(self):
        with tempfile.TemporaryDirectory() as d:
            source = HubSource(Path(d))
            # No hub import required on a bare CI environment.
            import types
            fake = types.ModuleType("huggingface_hub")
            fake.constants = types.SimpleNamespace(HF_HUB_DISABLE_XET=False)
            calls = []
            def download(*a, **kw):
                calls.append((a, kw))
                path = Path(kw["local_dir"]) / a[1]
                path.write_bytes(b"test")
                return str(path)
            fake.hf_hub_download = download
            with patch.dict("sys.modules", {"huggingface_hub": fake}):
                source.download("part.safetensors")
            self.assertEqual(calls[0][1]["revision"], "de4b8e4d43b917e7706784d8bb445c9af86a3540")
            self.assertTrue(Path(calls[0][1]["cache_dir"]).is_relative_to(d))
            self.assertTrue(fake.constants.HF_HUB_DISABLE_XET)

    def test_hub_metadata_requires_lfs_sha256_at_the_pinned_revision(self):
        import hashlib
        import types
        from joulewise.align.qwen4_gold.stream import REVISION
        files = {"config.json": b"{}", "model.safetensors.index.json": json.dumps({
            "weight_map": {"model.embed_tokens.weight": "part.safetensors"}}).encode()}
        calls = []
        class API:
            valid = True
            def get_paths_info(self, repo, names, revision):
                calls.append(revision)
                result = []
                for name in names:
                    if name in files:
                        raw = files[name]
                        result.append(types.SimpleNamespace(path=name, size=len(raw), blob_id=hashlib.sha1(
                            b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()))
                    else:
                        result.append(types.SimpleNamespace(path=name, size=100, lfs=types.SimpleNamespace(
                            sha256="a"*64) if API.valid else None))
                return result
        fake = types.ModuleType("huggingface_hub")
        fake.HfApi, fake.constants = API, types.SimpleNamespace(HF_HUB_DISABLE_XET=False)
        def download(repo, filename, **kw):
            self.assertEqual(kw["revision"], REVISION)
            path = Path(kw["local_dir"]) / filename
            path.write_bytes(files[filename])
            return path
        fake.hf_hub_download = download
        with tempfile.TemporaryDirectory() as d, patch.dict("sys.modules", {"huggingface_hub": fake}):
            source = HubSource(Path(d) / "valid")
            source.min_free_gb, source.max_staging_gb = 0, 12
            saved = source.prepare()
            self.assertEqual(saved["shards"]["part.safetensors"]["sha256"], "a"*64)
            API.valid = False
            source = HubSource(Path(d) / "invalid")
            source.min_free_gb, source.max_staging_gb = 0, 12
            with self.assertRaisesRegex(ValueError, "missing LFS sha256"):
                source.prepare()
        self.assertTrue(all(c == REVISION for c in calls))


@unittest.skipUnless(HAS_ARRAYS and HAS_SAFE, "optional NumPy and safetensors")
class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.fixture = self.base / "fixture"
        self.work = self.base / "work"
        synthetic(self.fixture)

    def driver(self, resume=False):
        source = LocalSource(self.fixture, self.work)
        return StreamDriver(options(self.work, resume), source, RUNTIMES), source

    def test_order_shared_retention_and_reference_chain(self):
        driver, source = self.driver()
        events = []
        def run(unit):
            events.append("run:" + unit)
            if unit == "0":
                self.assertTrue((driver.root / "shared.safetensors").exists())
            if unit == "final":
                self.assertFalse((driver.root / "shared.safetensors").exists())
            return fake_unit(driver, unit)
        driver.run_unit = run
        result = driver.run()
        self.assertEqual(events, ["run:" + u for u in ["embed", "0", "1", "final", "head"]])
        self.assertEqual(source.downloads, ["shared.safetensors", "zero.safetensors", "final.safetensors", "head.safetensors"])
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["coverage"]["full_48_layer_gold"])
        import numpy as np
        self.assertEqual(float(np.load(driver.state["chain"]["head"]["fp32:tokens-a"])[0]), 5.)
        self.assertTrue(all(r["deleted"] and r["verified"] and r["consumed"] for r in driver.state["shards"].values()))

    def test_resume_mid_unit_and_after_done_before_delete(self):
        driver, source = self.driver()
        def kill(unit):
            if unit == "0":
                raise SystemExit("simulated kill inside unit")
            return fake_unit(driver, unit)
        driver.run_unit = kill
        with self.assertRaises(SystemExit):
            driver.run()
        resumed, next_source = self.driver(True)
        resumed.run_unit = lambda u: fake_unit(resumed, u)
        resumed.run()
        self.assertNotIn("shared.safetensors", next_source.downloads)
        self.assertNotIn("zero.safetensors", next_source.downloads)
        # A completed restart performs no weight I/O or unit work.
        final, final_source = self.driver(True)
        final.run_unit = lambda u: self.fail("completed unit reran")
        final.run()
        self.assertEqual(final_source.downloads, [])

    def test_keep_going_records_failures_and_continues(self):
        def failing(driver):
            def run(unit):
                row = fake_unit(driver, unit)
                if unit == "0":
                    row.update(status="FAIL", failures=[{"case": "tokens-a-fp32-real", "status": "FAIL",
                                                         "failing_traces": ["mlp.norm"], "missing_traces": [],
                                                         "reason": None}])
                return row
            return run
        driver, _ = self.driver()
        driver.run_unit = failing(driver)
        with self.assertRaisesRegex(RuntimeError, "parity did not pass at 0"):
            driver.run()
        self.assertNotIn("0", driver.state["units"])  # Default: stop, record nothing for the unit.
        args = options(self.work, resume=True)
        args.keep_going = True
        resumed = StreamDriver(args, LocalSource(self.fixture, self.work), RUNTIMES)
        resumed.run_unit = failing(resumed)
        summary = resumed.run()
        self.assertEqual(summary["status"], "FAIL")
        self.assertFalse(summary["coverage"]["full_48_layer_gold"])
        self.assertEqual([f["unit"] for f in summary["failures"]], ["0"])
        self.assertEqual(summary["failures"][0]["cases"][0]["failing_traces"], ["mlp.norm"])
        self.assertEqual(list(resumed.state["units"]), ["embed", "0", "1", "final", "head"])
        import numpy as np
        self.assertEqual(float(np.load(resumed.state["chain"]["head"]["fp32:tokens-a"])[0]), 5.)
        # A recorded FAIL is integrity-checked and kept, never silently rerun.
        again, _ = self.driver(True)
        again.run_unit = lambda u: self.fail("recorded unit reran")
        self.assertEqual(again.run()["status"], "FAIL")
        self.assertEqual(json.loads((self.work / "summary.json").read_text())["status"], "FAIL")

    def test_keep_going_real_inputs_are_reference_outputs_of_a_failed_unit(self):
        import numpy as np
        args = options(self.work)
        args.keep_going = True
        driver = StreamDriver(args, LocalSource(self.fixture, self.work), RUNTIMES)
        seen = []
        def case(unit, dtype, prompt, mode, hidden, compare=True, scale=None):
            seen.append((unit, mode, str(hidden) if hidden else None))
            name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
            out = driver.harness.out / name / f"{prompt['name']}-{dtype}-{mode}" / "reference" / "output.npy"
            out.parent.mkdir(parents=True, exist_ok=True)
            np.save(out, np.ones((1, len(prompt["input_ids"]), 4), np.float32))
            return out
        def publish(unit, finished=False):
            name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
            cases = [{"case": "tokens-a-fp32-real", "status": "FAIL", "missing_traces": [],
                      "metrics": {"mlp.norm": {"pass": False}, "output": {"pass": True}}}] if unit == "0" else []
            report = {"status": "INCOMPLETE_OR_FAILED" if cases else "PASS", "cases": cases}
            write_json(driver.harness.out / (name + ".json"), report)
            return report
        driver.harness.case, driver.harness.publish = case, publish
        summary = driver.run()
        self.assertEqual(summary["status"], "FAIL")
        self.assertEqual(summary["failures"][0]["unit"], "0")
        self.assertEqual(summary["failures"][0]["cases"][0]["failing_traces"], ["mlp.norm"])
        expected = {str(driver.harness.out / "layer-000" / f"{p}-{d}-real" / "reference/output.npy")
                    for p in ("tokens-a", "tokens-b") for d in ("fp32", "bf16")}
        self.assertEqual({h for u, m, h in seen if u == "1" and m == "real"}, expected)
        self.assertEqual(set(driver.state["chain"]["0"].values()), expected)

    def test_sha256_mismatch_refuses(self):
        driver, source = self.driver()
        original = source.download
        def corrupt(name):
            path = original(name)
            raw = bytearray(path.read_bytes())
            raw[-1] ^= 1
            path.write_bytes(raw)
            return path
        source.download = corrupt
        with self.assertRaisesRegex(ValueError, "HF LFS sha256"):
            driver.stage("shared.safetensors")
        self.assertFalse(driver.state["shards"]["shared.safetensors"].get("verified", False))

    def test_guard_happens_before_source_call(self):
        driver, source = self.driver()
        with patch("shutil.disk_usage", return_value=argparse.Namespace(free=1)):
            with self.assertRaisesRegex(RuntimeError, "free-disk guard"):
                driver.stage("shared.safetensors")
        self.assertEqual(source.downloads, [])

    def test_changed_completed_activation_and_invocation_refuse(self):
        driver, _ = self.driver()
        driver.run_unit = lambda u: fake_unit(driver, u)
        driver.run()
        Path(driver.state["chain"]["0"]["bf16:tokens-a"]).write_bytes(b"changed")
        resumed, _ = self.driver(True)
        with self.assertRaisesRegex(ValueError, "activation/trace changed"):
            resumed.run()
        args = options(self.work, True)
        args.seed += 1
        with self.assertRaisesRegex(ValueError, "invocation changed"):
            StreamDriver(args, LocalSource(self.fixture, self.work), RUNTIMES)

    def test_size_plan_refuses_impossible_retention(self):
        driver, source = self.driver()
        for metadata in driver.metadata.values():
            metadata["size"] = 8*GIB
        driver.storage = storage_plan(driver.plan, driver.metadata, driver.checkpoint.weight_map)
        with self.assertRaisesRegex(RuntimeError, "retaining shared shards requires"):
            driver.run()
        self.assertEqual(source.downloads, [])

    def test_opt_in_restage_preserves_exact_tensor_bytes_and_caps_staging(self):
        from safetensors import safe_open
        import numpy as np
        args = options(self.work)
        args.shared_shards = "restage"
        source = LocalSource(self.fixture, self.work)
        driver = StreamDriver(args, source, RUNTIMES)
        peaks = []
        def run(unit):
            for name in driver.plan["keys"][unit]:
                filename = driver.checkpoint.weight_map[name]
                with safe_open(self.fixture / filename, framework="np") as a, safe_open(
                        driver.harness.checkpoint.root / filename, framework="np") as b:
                    np.testing.assert_array_equal(a.get_tensor(name), b.get_tensor(name))
            from joulewise.align.qwen4_gold.stream import disk_bytes
            peaks.append(disk_bytes(driver.staging))
            return fake_unit(driver, unit)
        driver.run_unit = run
        driver.run()
        self.assertEqual(source.downloads.count("shared.safetensors"), 2)
        self.assertTrue(all(p <= args.max_staging_gb*GIB for p in peaks))
        self.assertTrue(driver.state["derived_shards"])
        self.assertFalse(any((driver.staging / "views").glob("*")))

    def test_restage_recovers_kill_after_subset_commit_before_original_delete(self):
        args = options(self.work)
        args.shared_shards = "restage"
        driver = StreamDriver(args, LocalSource(self.fixture, self.work), RUNTIMES)
        with patch.object(driver, "consume", side_effect=SystemExit("kill before original deletion")), self.assertRaises(SystemExit):
            driver.subset_checkpoint("embed", driver.plan["keys"]["embed"])
        self.assertTrue((driver.root / "shared.safetensors").exists())
        args.resume = True
        source = LocalSource(self.fixture, self.work)
        resumed = StreamDriver(args, source, RUNTIMES)
        resumed.subset_checkpoint("embed", resumed.plan["keys"]["embed"])
        self.assertFalse((resumed.root / "shared.safetensors").exists())
        self.assertEqual(source.downloads, [])

    def test_partial_download_reserves_only_remaining_bytes_and_reverifies(self):
        from joulewise.align.qwen4_gold.stream import disk_bytes
        driver, source = self.driver()
        name = "shared.safetensors"
        raw = (self.fixture / name).read_bytes()
        partial = driver.root / ".cache/huggingface/download" / (name + ".mock.incomplete")
        partial.parent.mkdir(parents=True)
        partial.write_bytes(raw[:-20])
        driver.args.max_staging_gb = (disk_bytes(driver.staging) + 21)/GIB
        def complete(filename):
            with partial.open("ab") as f:
                f.write(raw[-20:])
            partial.rename(driver.root / filename)
        source.download = complete
        driver.stage(name)
        self.assertTrue(driver.state["shards"][name]["verified"])
        self.assertEqual(sha256(driver.root / name), sha256(self.fixture / name))

    def test_restage_discards_uncommitted_subset_before_disk_reservation(self):
        args = options(self.work)
        args.shared_shards = "restage"
        driver = StreamDriver(args, LocalSource(self.fixture, self.work), RUNTIMES)
        save = driver.save
        def kill():
            if driver.state["derived_shards"]:
                raise SystemExit("kill between subset rename and manifest commit")
            save()
        driver.save = kill
        with self.assertRaises(SystemExit):
            driver.subset_checkpoint("embed", driver.plan["keys"]["embed"])
        path = driver.staging / "views/embed/shared.safetensors"
        self.assertTrue(path.exists())
        args.resume = True
        resumed = StreamDriver(args, LocalSource(self.fixture, self.work), RUNTIMES)
        stage = resumed.stage
        def check(name):
            self.assertFalse(path.exists(), "uncommitted file consumes disk reservation")
            return stage(name)
        resumed.stage = check
        resumed.subset_checkpoint("embed", resumed.plan["keys"]["embed"])
        self.assertTrue(path.exists())


@unittest.skipUnless(HAS_ARRAYS and HAS_SAFE and HAS_REF, "optional official reference stack")
class OfficialTinyPLETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import torch
        from safetensors.torch import load_file, save_file
        from joulewise.align.qwen4_gold.reference import make_tiny
        cls.temp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.temp.name)
        cls.full = cls.base / "full"
        cls.full.mkdir()
        make_tiny(cls.full)
        cls.fixture = cls.base / "split"
        cls.fixture.mkdir()
        shutil.copyfile(cls.full / "config.json", cls.fixture / "config.json")
        values = {}
        for file in cls.full.glob("*.safetensors"):
            values.update(load_file(file))  # bounded official tiny fixture only
        groups = {}
        for name, value in values.items():
            if name.endswith("ngram_embedding.weight"):
                for i, part in enumerate(torch.chunk(value, 4)):
                    key = name.removesuffix(".weight") + f".shard_{i}.weight"
                    groups[f"ple-{i}.safetensors"] = {key: part.contiguous()}
            elif ".ngram_embedding.shard_" in name:
                index = name.split(".shard_")[-1].split(".")[0]
                groups.setdefault(f"ple-{index}.safetensors", {})[name] = value
            else:
                group = "buffers.safetensors" if "ple_embedding." in name else "text.safetensors"
                groups.setdefault(group, {})[name] = value
        index = {}
        for filename, tensors in groups.items():
            save_file(tensors, cls.fixture / filename)
            index.update(dict.fromkeys(tensors, filename))
        write_json(cls.fixture / "model.safetensors.index.json", {"weight_map": index})

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def build(self, root):
        source = LocalSource(self.fixture, root)
        driver = StreamDriver(options(root), source, RUNTIMES)
        # Exercise exactly the worker's official planner in this process; no
        # second framework, network, or full reference model is started.
        def plan(python, request, directory, *args):
            return official_plan(request, IndexedCheckpoint(request["checkpoint"]))
        return driver, source, plan

    def test_sparse_equals_full_official_lookups_and_refuses_unknown(self):
        import numpy as np
        import torch
        from transformers.models.qwen4_exp.configuration_qwen4_exp import Qwen4ExpTextConfig
        from transformers.models.qwen4_exp.modeling_qwen4_exp import Qwen4ExpTextNGramEmbedding
        with tempfile.TemporaryDirectory() as d:
            driver, _, plan = self.build(Path(d))
            with patch("joulewise.align.qwen4_gold.stream.execute", plan):
                driver.prepare_ple()
            store = driver.work / "sparse-ple"
            cp = SparseCheckpoint(driver.root, None, store, sha256(store / "store.json"))
            full = IndexedCheckpoint(self.fixture)
            base, planned = next(iter(driver.state["ple"]["plans"].items()))
            ids = np.array(planned["ids"] + planned["ids"][:2])
            np.testing.assert_array_equal(cp.ngram_rows(base, ids), full.ngram_rows(base, ids))
            for dtype in ("fp32", "bf16"):
                self.assertTrue(torch.equal(cp.ngram_rows(base, ids, "torch", dtype), full.ngram_rows(base, ids, "torch", dtype)))
            missing = next(i for i in range(planned["shape"][0]) if i not in planned["ids"])
            with self.assertRaisesRegex(ValueError, "outside sparse store"):
                cp.ngram_rows(base, [missing])
            # Independent official forward using the full tiny table.
            config = Qwen4ExpTextConfig(**full.text)
            module = Qwen4ExpTextNGramEmbedding(config, config.ple_embed_dim, 1, 0)
            for suffix in ("layer_multipliers", "ngram_heads_vocab_sizes", "ngram_heads_offsets"):
                setattr(module, suffix, full.read(base.removesuffix("ngram_embedding") + suffix, framework="torch", dtype="native"))
            all_rows = full.ngram_rows(base, np.arange(planned["shape"][0]), "torch")
            module.ngram_embedding.weight = torch.nn.Parameter(all_rows)
            captured = []
            module.ngram_embedding.register_forward_pre_hook(lambda m, a: captured.append(a[0].numpy().copy()))
            for prompt in driver.prompts:
                with torch.inference_mode():
                    expected = module(torch.tensor([prompt["input_ids"]]), None)
                actual = cp.ngram_rows(base, captured[-1], "torch").flatten(-2)
                self.assertTrue(torch.equal(expected, actual))
            self.assertEqual(set(planned["ids"]), set(np.concatenate([i.flatten() for i in captured]).tolist()))

    def test_resume_mid_ple_uses_committed_rows(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            driver, source, plan = self.build(root)
            real_save = driver.save
            def kill():
                real_save()
                if driver.state["ple"]["entries"]:
                    raise SystemExit("kill after first PLE part commit")
            driver.save = kill
            with patch("joulewise.align.qwen4_gold.stream.execute", plan), self.assertRaises(SystemExit):
                driver.prepare_ple()
            tensor = next(iter(driver.state["ple"]["entries"]))
            first_shard = driver.checkpoint.weight_map[tensor]
            resumed_source = LocalSource(self.fixture, root)
            resumed = StreamDriver(options(root, True), resumed_source, RUNTIMES)
            with patch("joulewise.align.qwen4_gold.stream.execute", side_effect=AssertionError("planner reran")):
                resumed.prepare_ple()
            self.assertNotIn(first_shard, resumed_source.downloads)
            self.assertEqual(len(resumed.state["ple"]["entries"]), 4)
            self.assertFalse((resumed.root / first_shard).exists())

    def test_full_ple_conversion_resume_copies_all_rows_without_sparse_substitution(self):
        import numpy as np
        from joulewise.align.qwen4_gold.stream_convert import convert_unit
        with tempfile.TemporaryDirectory() as d:
            driver, _, plan = self.build(Path(d))
            with patch("joulewise.align.qwen4_gold.stream.execute", plan):
                driver.prepare_ple()
            driver.args.convert_out = str(Path(d) / "converted")
            driver.args.canonical_converter = __file__
            driver.args.canonical_module = __file__
            stage = driver.stage
            def kill(name):
                if name == "ple-1.safetensors":
                    raise SystemExit("kill after first converted table span")
                return stage(name)
            driver.stage = kill
            with patch("joulewise.align.qwen4_gold.stream_convert.execute", return_value={"files": {}}), self.assertRaises(SystemExit):
                convert_unit(driver, "1")
            driver.stage = stage
            table = Path(driver.args.convert_out) / "layer-001/ngram-L001.bf16.bin"
            # Simulate an uncommitted append from a killed write.
            with table.open("ab") as f:
                f.write(b"uncommitted")
            with patch("joulewise.align.qwen4_gold.stream_convert.execute", side_effect=AssertionError("dense conversion reran")):
                result = convert_unit(driver, "1")
            base, descriptor = next(iter(driver.state["ple"]["plans"].items()))
            bits = np.fromfile(table, dtype="<u2").reshape(descriptor["shape"])
            actual = (bits.astype(np.uint32) << 16).view(np.float32)
            expected = IndexedCheckpoint(self.fixture).ngram_rows(base, np.arange(descriptor["shape"][0]))
            np.testing.assert_array_equal(actual, expected)
            manifest = json.loads(Path(result["manifest"]).read_text())
            self.assertEqual(manifest["files"][table.name], sha256(table))
            self.assertFalse(manifest["complete_model"])

    def test_multiple_ple_parts_in_one_source_download_once_per_phase(self):
        from safetensors.torch import load_file, save_file
        from joulewise.align.qwen4_gold.stream_convert import convert_unit
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            fixture = root / "fixture"
            shutil.copytree(self.fixture, fixture)
            merged = {**load_file(fixture / "ple-0.safetensors"), **load_file(fixture / "ple-1.safetensors")}
            save_file(merged, fixture / "ple-01.safetensors")
            index = json.loads((fixture / "model.safetensors.index.json").read_text())
            for key in merged:
                index["weight_map"][key] = "ple-01.safetensors"
            write_json(fixture / "model.safetensors.index.json", index)
            args = options(root / "work")
            args.shared_shards = "restage"
            source = LocalSource(fixture, args.work)
            driver = StreamDriver(args, source, RUNTIMES)
            def plan(python, request, directory, *limits):
                return official_plan(request, IndexedCheckpoint(request["checkpoint"]))
            with patch("joulewise.align.qwen4_gold.stream.execute", plan):
                driver.prepare_ple()
            driver.args.convert_out = str(root / "converted")
            driver.args.canonical_converter = __file__
            driver.args.canonical_module = __file__
            with patch("joulewise.align.qwen4_gold.stream_convert.execute", return_value={"files": {}}):
                convert_unit(driver, "1")
            self.assertEqual(source.downloads.count("ple-01.safetensors"), 2)

    def test_real_reference_chain_matches_full_tiny_oracle_after_restart(self):
        """All official workers run; only the candidate is a trace-copy double.

        This tests coordinator plumbing and reference parity, and makes no MLX
        claim. The native gather and external gold adapter need native runs.
        """
        from joulewise.align.qwen4_gold.runner import execute
        from joulewise.align.qwen4_gold.tiny_oracle import verify
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            prompts = root / "prompts.json"
            write_json(prompts, [{"name": "one", "input_ids": [5, 11, 0, 17, 23, 29, 31, 37, 41]}])
            args = options(root)
            args.shared_shards = "restage"
            args.prompts_json = str(prompts)
            source = LocalSource(self.fixture, root)
            driver = StreamDriver(args, source, RUNTIMES)
            calls = []
            def worker(python, request, directory, *limits):
                if request["backend"] != "mlx":
                    calls.append((request.get("unit"), request["backend"], request.get("dtype"), request.get("input_mode")))
                    return execute(python, request, directory, *limits)
                directory.mkdir(parents=True, exist_ok=True)
                reference = directory.parent / "reference"
                result = json.loads((reference / "result.json").read_text())
                for filename in result["traces"].values():
                    shutil.copyfile(reference / filename, directory / filename)
                result["metadata"].update(adapter_kind="mlx", peak_mlx_bytes=0, test_double=True)
                return result
            original_case = driver.harness.case
            def kill_after_first_case(*a, **kw):
                output = original_case(*a, **kw)
                if a[:2] == ("0", "fp32"):
                    raise SystemExit("kill after durable reference/candidate case")
                return output
            driver.harness.case = kill_after_first_case
            with patch("joulewise.align.qwen4_gold.runner.execute", worker), self.assertRaises(SystemExit):
                driver.run()
            calls.clear()
            args.resume = True
            resumed = StreamDriver(args, LocalSource(self.fixture, root), RUNTIMES)
            with patch("joulewise.align.qwen4_gold.runner.execute", worker):
                resumed.run()
            self.assertNotIn(("embed", "reference", "fp32", "real"), calls)
            self.assertNotIn(("0", "reference", "fp32", "real"), calls)
            result = verify(self.full, root / "parity", json.loads(prompts.read_text()), ["fp32", "bf16"])
            self.assertEqual(result["status"], "PASS")
            # Input snapshots prove every real case used its reference
            # predecessor, including the residual streams and bf16 path.
            import numpy as np
            for dtype in ("fp32", "bf16"):
                for previous, unit in zip(resumed.plan["units"], resumed.plan["units"][1:]):
                    name = f"layer-{int(unit):03d}" if unit.isdigit() else unit
                    actual = np.load(root / "parity" / name / f"one-{dtype}-real/input.npy")
                    expected = np.load(resumed.state["chain"][previous][dtype + ":one"])
                    np.testing.assert_array_equal(actual, expected)

    @unittest.skipUnless(HAS_MLX and os.environ.get("JW_GOLD_CANONICAL_MODULE"),
                         "native Metal/MLX and explicit canonical path required; run on the lead's Mac")
    def test_native_mlx_sparse_gather(self):
        import numpy as np
        import mlx.core as mx
        with tempfile.TemporaryDirectory() as d:
            driver, _, plan = self.build(Path(d))
            with patch("joulewise.align.qwen4_gold.stream.execute", plan):
                driver.prepare_ple()
            store = driver.work / "sparse-ple"
            cp = SparseCheckpoint(driver.root, None, store, sha256(store / "store.json"))
            base, planned = next(iter(driver.state["ple"]["plans"].items()))
            for dtype in ("fp32", "bf16"):
                values = cp.ngram_rows(base, planned["ids"], "mlx", dtype)
                mx.eval(values)
                np.testing.assert_array_equal(np.array(values.astype(mx.float32)), cp.ngram_rows(base, planned["ids"]))


@unittest.skipUnless(HAS_MLX and HAS_ARRAYS and HAS_SAFE and os.environ.get("JW_GOLD_CANONICAL_CONVERTER")
                     and os.environ.get("JW_GOLD_CANONICAL_MODULE"), "native MLX and explicit canonical source paths required")
class NativeConversionTests(unittest.TestCase):
    def test_maxfit_uses_canonical_quantization_and_resumes_per_tensor(self):
        import numpy as np
        import mlx.core as mx
        from joulewise.align.qwen4_gold.core import digest
        from joulewise.align.qwen4_gold.stream_convert import write_unit
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            rng = np.random.default_rng(4)
            tensors = {"model.embed_tokens.weight": np.ones((128, 64), np.float32),
                       "model.layers.0.mlp.experts.gate_up_proj": rng.standard_normal((2, 128, 64)).astype(np.float32),
                       "model.layers.0.mlp.experts.down_proj": rng.standard_normal((2, 64, 64)).astype(np.float32),
                       "model.layers.0.norm.weight": rng.standard_normal(64).astype(np.float32)}
            mx.save_safetensors(str(root / "weights.safetensors"), {k: mx.array(v).astype(mx.bfloat16) for k, v in tensors.items()})
            write_json(root / "config.json", {"vocab_size": 128})
            write_json(root / "model.safetensors.index.json", {"weight_map": dict.fromkeys(tensors, "weights.safetensors")})
            cp = IndexedCheckpoint(root)
            request = {"unit": "0", "unit_keys": [k for k in tensors if ".layers.0." in k],
                       "canonical_converter": os.environ["JW_GOLD_CANONICAL_CONVERTER"],
                       "canonical_module": os.environ["JW_GOLD_CANONICAL_MODULE"],
                       "max_memory_bytes": 512*1024**2, "min_free_gb": 0,
                       "config_digest": digest(cp.config), "weight_map_digest": digest(cp.weight_map),
                       "convert_out": str(root / "out")}
            result = write_unit(request, cp)
            output = root / "out"
            index = json.loads((output / "model.safetensors.index.json").read_text())["weight_map"]
            for original, values in tensors.items():
                if original not in request["unit_keys"]:
                    continue
                key = "language_model." + original
                if ".experts." in original:
                    key = key.replace(".experts.", ".switch_mlp.") + ".weight"
                    data = mx.array(values).astype(mx.bfloat16)
                    expected = mx.quantize(data, group_size=64, bits=6)
                    mx.eval(expected)
                    actual = mx.load(str(output / index[key]))
                    for name, array in zip((key, key.removesuffix("weight") + "scales", key.removesuffix("weight") + "biases"), expected):
                        if array.dtype == mx.uint32:
                            np.testing.assert_array_equal(np.array(actual[name]), np.array(array))
                        else:
                            np.testing.assert_array_equal(np.array(actual[name].astype(mx.float32)), np.array(array.astype(mx.float32)))
                else:
                    actual = mx.load(str(output / index[key]))[key]
                    np.testing.assert_array_equal(np.array(actual.astype(mx.float32)), np.array(mx.array(values).astype(mx.bfloat16).astype(mx.float32)))
            with patch.object(mx, "quantize", side_effect=AssertionError("completed tensor quantized again")):
                resumed = write_unit(request, cp)
            self.assertEqual(result["files"], resumed["files"])


if __name__ == "__main__":
    unittest.main()
