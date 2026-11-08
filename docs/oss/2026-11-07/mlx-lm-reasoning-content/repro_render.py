#!/usr/bin/env python3
# UNRUN. Written 2026-11-07 by an agent; never executed.
#
# What it shows: the prompt mlx_lm.server would build for turn 2 of a tool
# chain, when the client echoes turn 1's assistant message unchanged ("echo")
# versus when the client renames "reasoning" to "reasoning_content" ("rename").
# It runs the same two steps as ResponseGenerator._tokenize:
#   process_message_content(messages) -> tokenizer.apply_chat_template(...)
#
# Downloads: tokenizer and config files only (mlx_lm.utils.load_tokenizer uses
# allow_patterns *.json *.py tokenizer.model *.tiktoken *.txt *.jsonl *.jinja).
# No *.safetensors. trust_remote_code is not set, so any *.py is not executed.
#
# Needs: the same throwaway venv as repro_unit.py.
#
# Run (outside any mlx-lm checkout):
#   python -I /private/tmp/jwoss-ro/mlx-lm-reasoning-content/kit/repro_render.py \
#       --tokenizer mlx-community/Qwen3.5-0.8B-4bit
# A local directory with the tokenizer files also works for --tokenizer.
#
# Expected, NOT verified:
#   unpatched mlx-lm: echo -> reasoning NOT in prompt; rename -> reasoning in prompt
#   with 02-fix.patch: both modes -> reasoning in prompt, same token ids
# If "rename" also lacks the reasoning, this template does not render
# reasoning at this position; the issue must then name a template that does.

import argparse
import copy
import sys

import mlx_lm
from mlx_lm.server import process_message_content
from mlx_lm.utils import load_tokenizer

REASONING = "The user wants 17 + 25. I will call the add tool."

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two integers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "integer"},
                    "b": {"type": "integer"},
                },
                "required": ["a", "b"],
            },
        },
    }
]

# Turn 1 assistant message in the shape mlx_lm.server returns it.
ASSISTANT_AS_RETURNED = {
    "role": "assistant",
    "content": None,
    "reasoning": REASONING,
    "tool_calls": [
        {
            "function": {"name": "add", "arguments": '{"a": 17, "b": 25}'},
            "type": "function",
            "id": "call_0",
        }
    ],
}


def build_messages(mode):
    assistant = copy.deepcopy(ASSISTANT_AS_RETURNED)
    if mode == "rename":
        assistant["reasoning_content"] = assistant.pop("reasoning")
    return [
        {"role": "user", "content": "Use the add tool to compute 17 + 25."},
        assistant,
        {"role": "tool", "tool_call_id": "call_0", "content": "42"},
    ]


def render(tokenizer, mode):
    messages = build_messages(mode)
    process_message_content(messages)
    kwargs = dict(tools=TOOLS, add_generation_prompt=True)
    text = tokenizer.apply_chat_template(messages, tokenize=False, **kwargs)
    ids = tokenizer.apply_chat_template(messages, tokenize=True, **kwargs)
    return text, list(ids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tokenizer", default="mlx-community/Qwen3.5-0.8B-4bit")
    args = ap.parse_args()

    print(f"mlx_lm version: {getattr(mlx_lm, '__version__', '?')}")
    print(f"mlx_lm file:    {mlx_lm.__file__}")
    tokenizer = load_tokenizer(args.tokenizer)
    print(f"tokenizer:      {args.tokenizer}")
    print(f"has_thinking:   {tokenizer.has_thinking}")

    results = {}
    for mode in ("echo", "rename"):
        text, ids = render(tokenizer, mode)
        results[mode] = (text, ids)
        print(f"\n===== mode={mode}  prompt_tokens={len(ids)}")
        print(f"reasoning in rendered prompt: {REASONING in text}")
        print("----- rendered prompt (tail, 900 chars) -----")
        print(text[-900:])

    (echo_text, echo_ids), (ren_text, ren_ids) = results["echo"], results["rename"]
    common = 0
    for a, b in zip(echo_ids, ren_ids):
        if a != b:
            break
        common += 1
    print("\n===== summary")
    print(f"echo:   reasoning rendered={REASONING in echo_text}, tokens={len(echo_ids)}")
    print(f"rename: reasoning rendered={REASONING in ren_text}, tokens={len(ren_ids)}")
    print(f"token ids identical: {echo_ids == ren_ids}; common prefix: {common}")

    if REASONING in echo_text:
        print("RESULT: FIXED (echoed 'reasoning' reaches the template)")
        return 0
    if REASONING in ren_text:
        print("RESULT: BUG (echo drops the reasoning; rename keeps it)")
        return 1
    print("RESULT: INCONCLUSIVE (this template renders no reasoning here)")
    return 2


if __name__ == "__main__":
    sys.exit(main())
