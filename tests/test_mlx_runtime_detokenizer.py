"""CI-safe detokenizer regressions; faithful mlx-lm 0.31.3 wrapper stub.

No Metal or optional dependencies are imported. The wrapper property and
attribute forwarding mirror mlx-lm; the small BPE stand-in models its shared
vocabulary map and replace-on-reset stream state. This is fixture evidence,
not live hardware validation.
"""

from __future__ import annotations

import json
import unittest
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

from joulewise.adapters.mlx_runtime import MlxRuntimeAdapter
from joulewise.clock import FakeClock
from test_mlx_runtime import make_config, make_suite_manifest, suite_item


class BPEStreamingDetokenizer:
    """Faithful state/cost stub, with a deliberately small vocabulary map."""

    constructions: list[str] = []
    stage = "prepare"

    def __init__(self, tokenizer):
        BPEStreamingDetokenizer.constructions.append(self.stage)
        self.tokenmap = [None] * len(tokenizer.vocab)
        for text, token_id in tokenizer.vocab.items():
            self.tokenmap[token_id] = text
        self.reset()

    def reset(self):
        self.offset = 0
        self._unflushed = ""
        self.text = ""
        self.tokens = []

    def add_token(self, token):
        self.tokens.append(token)
        self._unflushed += self.tokenmap[token]
        # Keep spaces buffered until the next token or finalize.
        if self.tokenmap[token] != " ":
            self.text += self._unflushed
            self._unflushed = ""

    def finalize(self):
        self.text += self._unflushed
        self._unflushed = ""

    @property
    def last_segment(self):
        segment = self.text[self.offset:]
        self.offset = len(self.text)
        return segment


class UnknownDetokenizer(BPEStreamingDetokenizer):
    """Even a BPE subclass is outside the exact-class safety guard."""


class TokenizerWrapper:
    """Faithful detokenizer property and forwarding from mlx-lm 0.31.3."""

    def __init__(self, tokenizer, detokenizer_class=BPEStreamingDetokenizer):
        self._tokenizer = tokenizer
        self._detokenizer_class = detokenizer_class
        self._eos_token_ids = {99}
        self._chat_template = "retained template"

    @property
    def detokenizer(self):
        return self._detokenizer_class(self)

    def __getattr__(self, attr):
        if attr == "detokenizer":
            return self._detokenizer
        if attr == "eos_token_ids":
            return self._eos_token_ids
        if attr.startswith("_"):
            return self.__getattribute__(attr)
        return getattr(self._tokenizer, attr)

    def __setattr__(self, attr, value):
        if attr == "detokenizer":
            raise AttributeError("Cannot set the detokenizer.")
        if attr == "eos_token_ids":
            self._eos_token_ids = set(value) if value is not None else set()
        elif attr.startswith("_"):
            super().__setattr__(attr, value)
        else:
            setattr(self._tokenizer, attr, value)


class LocalTokenizer:
    vocab = {"A": 0, " ": 1, "B": 2}
    vocab_size = 3
    name_or_path = "fixture-local-tokenizer"
    bos_token_id = None

    def encode(self, text, *, add_special_tokens=True):
        return [0, 2]


class StubMlxLm:
    __version__ = "0.31.3-fixture"

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer
        self.detokenizers = []
        self.eos_during_generation = []
        self.fail_next = False

    def load(self, source, *, revision, return_config):
        return object(), self.tokenizer, {"model_type": "fixture"}

    def make_sampler(self, **kwargs):
        return kwargs

    def stream_generate(self, model, tokenizer, prompt, *, max_tokens, **kwargs):
        # mlx-lm checks isinstance on first next(), then reads this property.
        if not isinstance(tokenizer, TokenizerWrapper):
            tokenizer = TokenizerWrapper(tokenizer)
        detokenizer = tokenizer.detokenizer
        self.detokenizers.append(detokenizer)
        self.eos_during_generation.append(set(tokenizer.eos_token_ids))
        for index, token in enumerate([0, 1, 2, 1][:max_tokens]):
            detokenizer.add_token(token)
            if self.fail_next:
                self.fail_next = False
                raise RuntimeError("fixture stream interrupted")
            if index + 1 == max_tokens:
                break
            yield SimpleNamespace(text=detokenizer.last_segment, token=token)
        detokenizer.finalize()
        yield SimpleNamespace(text=detokenizer.last_segment, token=token)


class MlxRuntimeDetokenizerTests(unittest.TestCase):
    def setUp(self):
        BPEStreamingDetokenizer.constructions = []
        BPEStreamingDetokenizer.stage = "prepare"
        module = ModuleType("mlx_lm.tokenizer_utils")
        module.TokenizerWrapper = TokenizerWrapper
        module.BPEStreamingDetokenizer = BPEStreamingDetokenizer
        self.module_patch = patch.dict("sys.modules", {module.__name__: module})
        self.module_patch.start()
        self.addCleanup(self.module_patch.stop)

    def prepare_adapter(self, detokenizer_class=BPEStreamingDetokenizer):
        tokenizer = TokenizerWrapper(LocalTokenizer(), detokenizer_class)
        backend = StubMlxLm(tokenizer)
        adapter = MlxRuntimeAdapter(FakeClock(start=1000.0))
        adapter._import_mlx_lm = lambda: backend
        with patch.object(adapter, "_memory_snapshot", return_value={}):
            prepared = adapter.prepare(make_config())
        self.assertTrue(prepared.ok)
        return adapter, backend, prepared

    def test_no_construction_between_prefill_start_and_first_token(self):
        adapter, backend, prepared = self.prepare_adapter()
        original_event = adapter._event

        def event(event_type, phase, *args, **kwargs):
            if event_type == "phase_start" and phase == "prefill":
                BPEStreamingDetokenizer.stage = "prefill"
            if event_type == "phase_end" and phase == "prefill":
                self.assertEqual(BPEStreamingDetokenizer.constructions, ["prepare"])
                BPEStreamingDetokenizer.stage = "decode"
            return original_event(event_type, phase, *args, **kwargs)

        with patch.object(adapter, "_event", side_effect=event):
            result = adapter.run_workload(make_config())
        self.assertEqual(BPEStreamingDetokenizer.constructions, ["prepare"])
        self.assertEqual(result.output_token_count, 3)
        self.assertEqual(result.output_artifacts["response.txt"], "A B")
        self.assertIsInstance(adapter._tokenizer, TokenizerWrapper)
        self.assertIs(adapter._tokenizer._tokenizer, backend.tokenizer._tokenizer)
        self.assertEqual(adapter._tokenizer._chat_template, "retained template")
        provenance = result.workload_provenance["generator"]["detokenizer"]
        self.assertEqual(provenance["path"], "prepared_bpe_shallow_copy")
        self.assertEqual(prepared.metadata["detokenizer"], provenance)
        self.assertEqual(backend.eos_during_generation, [set()])
        self.assertEqual(adapter._tokenizer.eos_token_ids, {99})

    def test_reset_between_warmup_and_repeated_runs(self):
        adapter, backend, _ = self.prepare_adapter()
        self.assertTrue(adapter.warmup(make_config()).ok)
        config = make_config(workload_profile={"output_tokens": 4})
        first = adapter.run_workload(config)
        second = adapter.run_workload(config)
        self.assertEqual(first.output_artifacts["response.txt"], "A B ")
        self.assertEqual(first.output_artifacts["response.txt"], second.output_artifacts["response.txt"])
        self.assertEqual(first.workload_provenance["response"], second.workload_provenance["response"])
        self.assertEqual(BPEStreamingDetokenizer.constructions, ["prepare"])
        self.assertEqual(len({id(d) for d in backend.detokenizers}), 3)
        template = adapter._tokenizer._joulewise_detokenizer_template
        for detokenizer in backend.detokenizers:
            self.assertIs(detokenizer.tokenmap, template.tokenmap)
            self.assertIsNot(detokenizer.tokens, template.tokens)
            self.assertEqual(detokenizer.tokens, [0, 1, 2, 1])
        self.assertEqual(template.tokens, [])
        self.assertEqual(template.text, "")
        # Explicitly poison every stream-state field in the template: reset on
        # each access must replace them, including buffered text and offset.
        template.tokens.append(2)
        template.text = "carried"
        template.offset = 7
        template._unflushed = "pending"
        reset = adapter._tokenizer.detokenizer
        self.assertEqual((reset.tokens, reset.text, reset.offset, reset._unflushed), ([], "", 0, ""))

    def test_unknown_class_falls_back_and_records_path_with_identical_output(self):
        optimized, _, _ = self.prepare_adapter()
        fallback, backend, prepared = self.prepare_adapter(UnknownDetokenizer)
        self.assertIs(fallback._tokenizer, backend.tokenizer)
        BPEStreamingDetokenizer.stage = "generation"
        expected = optimized.run_workload(make_config())
        observed = fallback.run_workload(make_config())
        self.assertEqual(expected.output_artifacts["response.txt"], observed.output_artifacts["response.txt"])
        self.assertEqual(expected.workload_provenance["response"], observed.workload_provenance["response"])
        provenance = observed.workload_provenance["generator"]["detokenizer"]
        self.assertEqual(provenance["path"], "fallback")
        self.assertEqual(provenance["reason"], "unsupported_detokenizer_class")
        self.assertTrue(provenance["class"].endswith("UnknownDetokenizer"))
        self.assertEqual(prepared.metadata["detokenizer"], provenance)
        self.assertEqual(BPEStreamingDetokenizer.constructions, ["prepare", "prepare", "generation"])

    def test_suite_reuses_map_and_records_provenance(self):
        for detokenizer_class, path in [(BPEStreamingDetokenizer, "prepared_bpe_shallow_copy"), (UnknownDetokenizer, "fallback")]:
            with self.subTest(path=path):
                adapter, backend, _ = self.prepare_adapter(detokenizer_class)
                manifest = make_suite_manifest([
                    suite_item("first", prompt_tokens=2, output_tokens=3),
                    suite_item("second", prompt_tokens=2, output_tokens=3),
                ])
                result = adapter.run_suite(make_config(), manifest, order_seed="fixture")
                self.assertEqual(result.workload_provenance["generator"]["detokenizer"]["path"], path)
                records = [json.loads(line) for line in result.output_artifacts["suite_items.jsonl"].splitlines()]
                self.assertEqual([record["response_text"] for record in records], ["A B", "A B"])
                self.assertEqual([d.tokens for d in backend.detokenizers], [[0, 1, 2], [0, 1, 2]])

    def test_interrupted_stream_does_not_contaminate_next_run(self):
        adapter, backend, _ = self.prepare_adapter()
        backend.fail_next = True
        with self.assertRaisesRegex(RuntimeError, "fixture stream interrupted"):
            adapter.run_workload(make_config())
        self.assertEqual(adapter._tokenizer.eos_token_ids, {99})
        result = adapter.run_workload(make_config())
        self.assertEqual(result.output_artifacts["response.txt"], "A B")
        self.assertEqual(backend.detokenizers[-1].tokens, [0, 1, 2])
        self.assertEqual(BPEStreamingDetokenizer.constructions, ["prepare"])

    def test_cleanup_releases_template_and_reprepare_builds_once(self):
        adapter, backend, _ = self.prepare_adapter()
        old_wrapper = adapter._tokenizer
        with patch.object(adapter, "_memory_snapshot", return_value={}):
            self.assertTrue(adapter.cleanup(make_config()).ok)
            self.assertIsNone(adapter._tokenizer)
            self.assertTrue(adapter.prepare(make_config()).ok)
        self.assertIsNot(adapter._tokenizer, old_wrapper)
        self.assertEqual(BPEStreamingDetokenizer.constructions, ["prepare", "prepare"])
        self.assertIs(adapter._tokenizer._tokenizer, backend.tokenizer._tokenizer)


if __name__ == "__main__":
    unittest.main()
