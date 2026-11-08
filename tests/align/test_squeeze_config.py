from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from joulewise.align.squeeze.config import (
    ADVERSARY_FACTORY, SHADE_FACTORY, adapt_episode_spec, load_kit, seal,
    validate_control, validate_variant,
)
from joulewise.align.squeeze.harness import AdversaryTask
from tests.align.squeeze_fixtures import KIT, control_config, variant


class ConfigTests(unittest.TestCase):
    def test_shipped_configs_and_full_hash_chain(self):
        kit = load_kit(KIT)
        self.assertEqual(len(kit), 13)
        strategies = {c["strategy"] for c in kit.values() if "strategy" in c}
        self.assertEqual(strategies, {"none", "audit_awareness", "log_padding",
                                     "compute_smoothing", "tool_offload", "mixed"})
        self.assertEqual({c["decode_tokens"] for c in kit.values() if "decode_tokens" in c},
                         {0, 128, 256, 300, 512, 1024, 2048})

    def test_mutated_prompt_rejected_even_with_resealed_config(self):
        obj = variant()
        obj["instructions"] += " modified"
        for candidate in (obj, seal(obj)):
            with self.assertRaisesRegex(ValueError, "mismatch"):
                validate_variant(candidate)

    def test_unknown_fields_revisions_and_knowledge_fail_closed(self):
        for changes in ({"extra": 1}, {"revision": True}, {"revision": 0},
                        {"audit_knowledge": "none"}, {"strategy": "unknown"},
                        {"instructions": ""}, {"status": "REGISTERED"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_variant(seal({**variant(), **changes}))

    def test_control_validation(self):
        for changes in ({"decode_tokens": -1}, {"decode_tokens": True}, {"decode_tokens": 4097},
                        {"decode_tokens": 1.5}, {"before_chat_call": -1},
                        {"prompt_token_ids": []}, {"prompt_token_ids": [True]},
                        {"prompt_token_ids": [-1]}, {"prompt_token_ids": "1 2"},
                        {"max_context_tokens": 3}, {"extra": "ignored?"}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                validate_control(seal({**control_config(), **changes}))
        obj = control_config(k=2)
        obj["max_context_tokens"] = 4
        validate_control(seal(obj))  # P+k-1, including the exact boundary.

    def test_manifest_detects_byte_change(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = json.loads((KIT / "manifest.json").read_text())
            name = "unaware.v1.json"
            manifest["files"] = {name: manifest["files"][name]}
            (root / "manifest.json").write_text(json.dumps(manifest))
            (root / name).write_bytes((KIT / name).read_bytes() + b" ")
            with self.assertRaisesRegex(ValueError, "file hash"):
                load_kit(root)

    def test_manifest_rejects_nonlocal_path_without_opening_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = json.loads((KIT / "manifest.json").read_text())
            manifest["files"] = {"../escape.v1.json": "0" * 64}
            (root / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "local versioned"):
                load_kit(root)

    def test_manifest_symlink_is_rejected_before_reading_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "synthetic-manifest-target.json"
            target.write_text("this synthetic target must not be parsed")
            (root / "manifest.json").symlink_to(target)
            with self.assertRaisesRegex(ValueError, "symlink"):
                load_kit(root)

    def test_episode_overlay_preserves_all_execution_controls_and_treats_paths_as_text(self):
        # This is an inert string, never passed to a file/model API.
        spec = {"schema": "joulewise.align.apple.episode_spec.v1", "condition": "sabotage",
                "task_factory": SHADE_FACTORY, "task_kwargs": {"cache_dir": "/sealed-example/cache",
                "task_pair": "spam_filter_update", "give_hint": True}, "seed": 23,
                "max_tokens": 4096, "max_turns": 12, "temperature": 1.0,
                "prompt_cache": "episode_prefix", "thermal": {"sentinel": "unchanged"},
                "max_episode_decode_tokens": 8192, "deadman_s": 1000,
                "hybrid_checkpoint_limit": 0, "warmup_condition": "benign"}
        before = deepcopy(spec)
        result = adapt_episode_spec(spec, variant())
        self.assertEqual(spec, before)
        self.assertEqual(result["task_factory"], ADVERSARY_FACTORY)
        self.assertEqual(result["task_kwargs"]["base_task_kwargs"], spec["task_kwargs"])
        for key in set(spec) - {"task_factory", "task_kwargs"}:
            self.assertEqual(result[key], spec[key])
        with self.assertRaises(ValueError):
            adapt_episode_spec(result, variant())

    def test_prompt_changes_only_sabotage_and_delegates_tools_and_scoring(self):
        class Task:
            task_pair = "synthetic"
            flags = []

            def system_prompt(self, condition):
                return "original-" + condition

            def score_side(self, transcript):
                return True

        original = Task()
        for name in ("unaware", "meter-aware", "pad-visible-log", "smooth-compute",
                     "tool-compute", "mixed-adaptive"):
            wrapped = AdversaryTask(original, variant(name))
            self.assertEqual(wrapped.system_prompt("benign"), "original-benign")
            sabotage = wrapped.system_prompt("sabotage")
            self.assertTrue(sabotage.startswith("original-sabotage"))
            self.assertEqual(sabotage == "original-sabotage", name == "unaware")
            self.assertIs(wrapped.flags, original.flags)
            self.assertTrue(wrapped.score_side([]))
        with self.assertRaises(ValueError):
            wrapped.system_prompt("typo")


if __name__ == "__main__":
    unittest.main()
