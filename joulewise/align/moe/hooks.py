"""Forward-hook capture of HF Qwen3-MoE, Qwen2-MoE, and Mixtral routing.

Capture is for a single episode/sequence at a time in eager inference. The
recorder records coverage conditions in flags and never refuses a model call.
Torch and transformers are loaded only when a recorder is constructed.
"""

from __future__ import annotations

import importlib
import re
from contextlib import contextmanager
from typing import Any, Iterator

from joulewise.align.records import RouterLog


class RouterRecorder:
    """Attach gate hooks immediately; close() or a context manager removes them.

    log/to_log() returns an immutable snapshot. Explicit phase("prefill") or
    phase("decode") overrides cache-based inference, including one-token prompts,
    speculative multi-token decode, and cached tool-response prefills.
    """

    def __init__(self, model: Any):
        self.model = model
        config = getattr(model, "config", None)
        self.model_name = getattr(config, "_name_or_path", "") or type(model).__name__
        self.num_experts = getattr(config, "num_experts", getattr(config, "num_local_experts", 0))
        self.top_k = getattr(config, "num_experts_per_tok", 0)
        self.layers: tuple[int, ...] = ()
        self.flags: list[str] = []
        self._handles: list[Any] = []
        self._phase: str | None = None
        self._phases: list[str] = []
        self._experts: list[tuple[tuple[int, ...], ...]] = []
        self._active: dict[str, Any] | None = None
        self._attach()

    def _flag(self, flag: str) -> None:
        if flag not in self.flags:
            self.flags.append(flag)

    def _attach(self) -> None:
        try:
            import torch
        except ImportError:
            self._flag("torch_unavailable")
            return
        layouts = (
            ("transformers.models.qwen3_moe.modeling_qwen3_moe", "Qwen3MoeSparseMoeBlock"),
            ("transformers.models.qwen2_moe.modeling_qwen2_moe", "Qwen2MoeSparseMoeBlock"),
            ("transformers.models.mixtral.modeling_mixtral", "MixtralSparseMoeBlock"),
        )
        classes = []
        for module, name in layouts:
            try:
                classes.append(getattr(importlib.import_module(module), name))
            except (ImportError, AttributeError):
                continue
        if not classes:
            self._flag("supported_transformers_classes_unavailable")
            return
        blocks = []
        for name, block in self.model.named_modules():
            if isinstance(block, tuple(classes)):
                match = re.search(r"(?:^|\.)layers\.(\d+)(?:\.|$)", name)
                layer = int(match.group(1)) if match else len(blocks)
                if not match:
                    self._flag("layer_index_inferred_from_module_order")
                gate = getattr(block, "gate", None)
                experts = getattr(block, "num_experts", self.num_experts)
                top_k = getattr(block, "top_k", self.top_k)
                if gate is None or not 0 < top_k <= experts:
                    self._flag("unsupported_router_topology")
                    continue
                blocks.append((layer, gate, experts, top_k))
        if not blocks:
            self._flag("no_supported_moe_blocks")
            return
        blocks.sort(key=lambda item: item[0])
        self.layers = tuple(item[0] for item in blocks)
        self.num_experts, self.top_k = blocks[0][2:]
        if (len(set(self.layers)) != len(self.layers)
                or any(item[2:] != (self.num_experts, self.top_k) for item in blocks)):
            # RouterLog has one expert count and top-k for every layer.
            self._flag("heterogeneous_router_topology_not_representable")
            return
        self._torch = torch
        try:
            self._handles.append(self.model.register_forward_pre_hook(self._begin, with_kwargs=True))
            for layer, gate, _, _ in blocks:
                self._handles.append(gate.register_forward_hook(self._gate_hook(layer)))
            self._handles.append(self.model.register_forward_hook(
                self._finish, with_kwargs=True, always_call=True))
        except (TypeError, AttributeError):
            self._flag("forward_hook_api_unavailable")
            self.close()

    def _begin(self, module: Any, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        self._active = None
        inputs = kwargs.get("input_ids")
        if inputs is None and args:
            inputs = args[0]
        if inputs is None:
            inputs = kwargs.get("inputs_embeds")
        if inputs is None or inputs.ndim not in (2, 3) or inputs.shape[0] != 1:
            self._flag("single_sequence_capture_required")
            return
        length = inputs.shape[1]
        phase = self._phase
        if phase is None:
            cached = False
            past = kwargs.get("past_key_values")
            try:
                if past is not None:
                    cached = (past.get_seq_length() > 0 if hasattr(past, "get_seq_length")
                              else len(past) > 0 and past[0][0].shape[-2] > 0)
                position = kwargs.get("cache_position")
                if position is not None and position.numel():
                    cached = cached or int(position.reshape(-1)[0]) > 0
            except (AttributeError, IndexError, TypeError):
                self._flag("cache_phase_inference_unavailable")
            phase = "decode" if length == 1 and cached else "prefill"
            if cached and length > 1:
                self._flag("cached_multitoken_phase_inferred_prefill")
        if getattr(module, "training", False):
            self._flag("training_mode_capture")
        valid = list(range(length))
        mask = kwargs.get("attention_mask")
        if mask is not None:
            if mask.ndim == 2 and mask.shape[0] == 1 and mask.shape[1] >= length:
                valid = [i for i, value in enumerate(mask[0, -length:].detach().cpu().tolist())
                         if value != 0]
                if len(valid) != length:
                    self._flag("padding_tokens_omitted")
            else:
                self._flag("attention_mask_layout_unrecognized")
        self._active = {"length": length, "phase": phase, "valid": valid, "rows": {}, "bad": False}

    def _gate_hook(self, layer: int):
        def hook(module: Any, args: tuple[Any, ...], output: Any) -> None:
            active = self._active
            if active is None:
                return
            try:
                torch = self._torch
                # New router modules can return actual selected IDs alongside
                # logits/weights. Older sparse blocks expose only gate logits.
                outputs = output if isinstance(output, tuple) else (output,)
                ids = next((part for part in outputs
                            if torch.is_tensor(part) and not torch.is_floating_point(part)
                            and part.ndim >= 2 and part.shape[-1] == self.top_k), None)
                if ids is None:
                    logits = next((part for part in outputs if torch.is_tensor(part)
                                   and part.ndim >= 2 and part.shape[-1] == self.num_experts), None)
                    if logits is None:
                        self._flag("gate_output_layout_unrecognized")
                        active["bad"] = True
                        return
                    # Same float32 softmax and top-k operation as these HF blocks,
                    # including their tie handling; logits alone can round ties
                    # differently in low precision.
                    probabilities = torch.nn.functional.softmax(logits, dim=-1, dtype=torch.float32)
                    ids = torch.topk(probabilities, self.top_k, dim=-1).indices
                rows = ids.detach().reshape(-1, self.top_k).cpu().tolist()
                if (layer in active["rows"] or len(rows) != active["length"]
                        or any(len(set(row)) != self.top_k
                               or any(not 0 <= e < self.num_experts for e in row) for row in rows)):
                    self._flag("router_forward_shape_or_reentry_mismatch")
                    active["bad"] = True
                active["rows"][layer] = rows
            except (RuntimeError, TypeError, AttributeError, ValueError):
                self._flag("router_capture_failed")
                active["bad"] = True
        return hook

    def _finish(self, module: Any, args: tuple[Any, ...], kwargs: dict[str, Any], output: Any) -> None:
        active, self._active = self._active, None
        if active is None:
            return
        if output is None or active["bad"] or set(active["rows"]) != set(self.layers):
            self._flag("incomplete_router_forward")
            return
        for token in active["valid"]:
            self._phases.append(active["phase"])
            self._experts.append(tuple(tuple(active["rows"][layer][token]) for layer in self.layers))

    @property
    def log(self) -> RouterLog:
        """An immutable snapshot; later forwards cannot mutate it."""
        return RouterLog(self.model_name, self.num_experts, self.top_k, self.layers,
                         tuple(self._phases), tuple(self._experts))

    def to_log(self) -> RouterLog:
        return self.log

    def reset(self) -> None:
        """Begin another episode while keeping hooks and persistent diagnostics."""
        self._phases.clear()
        self._experts.clear()
        self._active = None

    @contextmanager
    def phase(self, phase: str) -> Iterator[RouterRecorder]:
        """Tag forwards explicitly; invalid phase requests are flagged and inferred."""
        previous = self._phase
        if phase in ("prefill", "decode"):
            self._phase = phase
        else:
            self._flag("unknown_requested_phase")
            self._phase = None
        try:
            yield self
        finally:
            self._phase = previous

    def close(self) -> None:
        """Remove only this recorder's hooks, idempotently."""
        for handle in self._handles:
            handle.remove()
        self._handles.clear()
        self._active = None

    def __enter__(self) -> RouterRecorder:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


__all__ = ["RouterRecorder"]
