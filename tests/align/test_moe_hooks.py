"""Optional tiny real-HF model integration; no model or tokenizer downloads."""

from __future__ import annotations

import importlib.util
import math
import unittest

from joulewise.align.moe.hooks import RouterRecorder
from joulewise.align.moe.stats import episode_stats

MODEL_LIBRARIES = (importlib.util.find_spec("torch") is not None
                   and importlib.util.find_spec("transformers") is not None)


@unittest.skipUnless(MODEL_LIBRARIES, "tiny HF MoE integration needs optional torch and transformers")
class RouterHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import torch
        cls.torch = torch
        torch.set_num_threads(1)
        try:
            from transformers import Qwen3MoeConfig, Qwen3MoeForCausalLM
        except ImportError as exc:
            raise unittest.SkipTest(f"installed transformers lacks usable Qwen3-MoE: {exc}") from exc
        torch.manual_seed(19)
        config = Qwen3MoeConfig(
            num_hidden_layers=2, num_experts=8, num_experts_per_tok=2,
            hidden_size=32, intermediate_size=64, moe_intermediate_size=32,
            num_attention_heads=4, num_key_value_heads=2, head_dim=8,
            vocab_size=96, max_position_embeddings=512, decoder_sparse_step=1,
            mlp_only_layers=[], eos_token_id=None, pad_token_id=0,
        )
        cls.model = Qwen3MoeForCausalLM(config).eval()

    def _prompt(self, text):
        # Local character vocabulary; a tokenizer/model download is unnecessary
        # for validating the actual forward and router paths.
        return self.torch.tensor([[ord(char) % 95 + 1 for char in text]], dtype=self.torch.long)

    def test_two_prompts_generate_router_logs_and_stats(self):
        torch = self.torch
        for text in ("Sort the local project files.", "Summarize the tool results."):
            prompt = self._prompt(text)
            with torch.inference_mode(), RouterRecorder(self.model) as recorder:
                self.model.generate(prompt, attention_mask=torch.ones_like(prompt),
                                    max_new_tokens=4, do_sample=False,
                                    eos_token_id=None, pad_token_id=0)
                log = recorder.log
                self.assertEqual(log.layers, (0, 1))
                self.assertEqual(log.num_experts, 8)
                self.assertEqual(log.top_k, 2)
                self.assertEqual(log.phase.count("prefill"), prompt.shape[1])
                # Autoregression forwards the prompt then all but the last new
                # sampled token: four generated tokens require three decode forwards.
                self.assertEqual(log.phase.count("decode"), 4 - 1)
                self.assertTrue(all(math.isfinite(value) for value in episode_stats(log).values()))
                self.assertFalse(recorder.flags)

    def test_routes_match_hf_logits_and_hooks_do_not_change_output(self):
        torch = self.torch
        prompt = self._prompt("Read the next file.")
        with torch.inference_mode():
            before = self.model(prompt, use_cache=False, output_router_logits=True)
            with RouterRecorder(self.model) as recorder:
                after = self.model(prompt, use_cache=False, output_router_logits=True)
                log = recorder.log
            # Identical model/code/inputs: hook transparency is a bit-identity property.
            self.assertTrue(torch.equal(before.logits, after.logits))
            for layer, logits in enumerate(after.router_logits):
                expected = torch.topk(torch.softmax(logits, dim=-1, dtype=torch.float32), 2, dim=-1).indices.tolist()
                self.assertEqual([list(row[layer]) for row in log.experts], expected)
            captured = len(recorder.log.experts)
            self.model(prompt, use_cache=False)
            self.assertEqual(len(recorder.log.experts), captured)

    def test_one_token_prefill_explicit_phase_and_snapshot(self):
        torch = self.torch
        with torch.inference_mode(), RouterRecorder(self.model) as recorder:
            first = self.model(torch.tensor([[3]]), use_cache=True)
            self.assertEqual(recorder.log.phase, ("prefill",))
            snapshot = recorder.log
            with recorder.phase("decode"):
                second = self.model(torch.tensor([[4]]), past_key_values=first.past_key_values,
                                    use_cache=True)
            with recorder.phase("prefill"):
                self.model(torch.tensor([[5]]), past_key_values=second.past_key_values, use_cache=True)
            self.assertEqual(recorder.log.phase, ("prefill", "decode", "prefill"))
            self.assertEqual(snapshot.phase, ("prefill",))
            recorder.reset()
            self.assertEqual(recorder.log.experts, ())

    def test_padding_and_batch_coverage_are_flags(self):
        torch = self.torch
        with torch.inference_mode(), RouterRecorder(self.model) as recorder:
            self.model(torch.tensor([[0, 0, 4, 5]]),
                       attention_mask=torch.tensor([[0, 0, 1, 1]]), use_cache=False)
            self.assertEqual(len(recorder.log.experts), 2)
            self.assertIn("padding_tokens_omitted", recorder.flags)
            recorder.reset()
            self.model(torch.tensor([[4, 5], [6, 7]]), use_cache=False)
            self.assertEqual(len(recorder.log.experts), 0)
            self.assertIn("single_sequence_capture_required", recorder.flags)

    def test_qwen2_and_mixtral_layouts(self):
        from transformers import (MixtralConfig, MixtralForCausalLM,
                                  Qwen2MoeConfig, Qwen2MoeForCausalLM)
        torch = self.torch
        configs = (
            (Qwen2MoeConfig, Qwen2MoeForCausalLM,
             {"num_experts": 8, "moe_intermediate_size": 32, "shared_expert_intermediate_size": 32}),
            (MixtralConfig, MixtralForCausalLM, {"num_local_experts": 8}),
        )
        for config_type, model_type, extra in configs:
            with self.subTest(model=model_type.__name__):
                config = config_type(
                    num_hidden_layers=2, num_experts_per_tok=2, hidden_size=32,
                    intermediate_size=64, num_attention_heads=4, num_key_value_heads=2,
                    vocab_size=96, max_position_embeddings=512, **extra)
                model = model_type(config).eval()
                with torch.inference_mode(), RouterRecorder(model) as recorder:
                    model(self._prompt("Use a tool."), use_cache=False)
                    self.assertEqual(recorder.log.layers, (0, 1))
                    self.assertEqual(recorder.log.top_k, 2)
                    self.assertTrue(all(math.isfinite(x) for key, x in episode_stats(recorder.log).items()
                                        if key.startswith("prefill_") or key.startswith("both_")))
                    self.assertFalse(recorder.flags)

    def test_sparse_layer_indices_follow_model(self):
        from transformers import Qwen3MoeConfig, Qwen3MoeForCausalLM
        config = Qwen3MoeConfig(
            num_hidden_layers=4, num_experts=8, num_experts_per_tok=2, hidden_size=32,
            intermediate_size=64, moe_intermediate_size=32, num_attention_heads=4,
            num_key_value_heads=2, head_dim=8, vocab_size=96, decoder_sparse_step=2)
        model = Qwen3MoeForCausalLM(config).eval()
        with self.torch.inference_mode(), RouterRecorder(model) as recorder:
            model(self._prompt("Read files."), use_cache=False)
            self.assertEqual(recorder.log.layers, (1, 3))
            self.assertEqual(len(recorder.log.experts), len("Read files."))


if __name__ == "__main__":
    unittest.main()
