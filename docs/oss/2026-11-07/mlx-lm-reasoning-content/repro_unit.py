#!/usr/bin/env python3
# UNRUN. Written 2026-11-07 by an agent; never executed.
#
# What it shows: mlx_lm.server.process_message_content (the step that prepares
# request messages for the chat template) does not copy an echoed "reasoning"
# field to "reasoning_content". No model weights, no network.
#
# Needs: a throwaway venv with mlx-lm installed, either
#   - PyPI:   pip install "mlx-lm==0.32.2" requests
#   - pinned: pip install -e <mlx-lm clone at 56230fa> requests
#
# Run (from any directory that is NOT an mlx-lm checkout, so -I + cwd cannot
# shadow the installed package):
#   python -I /private/tmp/jwoss-ro/mlx-lm-reasoning-content/kit/repro_unit.py
#
# Exit code: 1 = bug present (expected on 0.32.2 and on main 56230fa),
#            0 = fixed (expected after 02-fix.patch).

import copy
import json
import sys

import mlx_lm
from mlx_lm.server import process_message_content

REASONING = "The user wants the weather in Paris. I will call get_weather."

# Shape of choices[0].message in a non-streaming mlx_lm.server response
# (server.py generate_response: "content", then "reasoning", then "tool_calls").
ASSISTANT_AS_RETURNED = {
    "role": "assistant",
    "content": None,
    "reasoning": REASONING,
    "tool_calls": [
        {
            "function": {"name": "get_weather", "arguments": '{"city": "Paris"}'},
            "type": "function",
            "id": "call_0",
        }
    ],
}

# What an agent loop sends back on the next turn: the returned message, unchanged.
MESSAGES = [
    {"role": "user", "content": "What is the weather in Paris?"},
    ASSISTANT_AS_RETURNED,
    {"role": "tool", "tool_call_id": "call_0", "content": "18 C, cloudy"},
]


def main():
    print(f"mlx_lm version: {getattr(mlx_lm, '__version__', '?')}")
    print(f"mlx_lm file:    {mlx_lm.__file__}")

    messages = copy.deepcopy(MESSAGES)
    process_message_content(messages)
    assistant = messages[1]

    print("\nAssistant message after process_message_content:")
    print(json.dumps(assistant, indent=2, ensure_ascii=False))

    got = assistant.get("reasoning_content")
    if got == REASONING:
        print("\nFIXED: 'reasoning' was copied to 'reasoning_content'.")
        return 0
    print(
        "\nBUG: 'reasoning_content' is "
        f"{got!r}. A chat template that reads only message.reasoning_content "
        "gets no reasoning for this turn."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
