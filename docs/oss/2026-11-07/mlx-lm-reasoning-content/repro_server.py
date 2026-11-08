#!/usr/bin/env python3
# UNRUN. Written 2026-11-07 by an agent; never executed.
#
# Live check against a running, stock mlx_lm.server. Standard library only;
# this script imports nothing from mlx-lm. It runs one tool-call chain and
# records usage per request: prompt_tokens, completion_tokens and
# usage.prompt_tokens_details.cached_tokens.
#
#   --mode echo    the client appends each returned assistant message unchanged
#                  (it carries "reasoning")
#   --mode rename  the client renames "reasoning" to "reasoning_content" first
#
# The server holds a prompt cache across requests. Restart the server before
# each mode, or the second mode reads the first mode's cache entries.
#
# Server (separate terminal, throwaway venv; this downloads the model weights,
# which Ed does himself):
#   mlx_lm.server --model mlx-community/Qwen3.5-0.8B-4bit --port 8080
# Run:
#   python -I /private/tmp/jwoss-ro/mlx-lm-reasoning-content/kit/repro_server.py \
#       --mode echo --out echo.jsonl
#   (restart the server)
#   python -I /private/tmp/jwoss-ro/mlx-lm-reasoning-content/kit/repro_server.py \
#       --mode rename --out rename.jsonl
#
# Thinking stays enabled (no chat_template_kwargs), so this isolates the field
# name from the separate enable_thinking=false drift.
#
# How to read the table: for turn k >= 2, "prev_ctx" is the previous request's
# prompt_tokens + completion_tokens, i.e. about what the server stored in its
# cache after that request. cached_tokens near prev_ctx = the cache was
# extended. cached_tokens far below prev_ctx = the server fell back to a shorter
# entry and prefilled the rest again. Expected, NOT verified: echo stays flat,
# rename grows (only if the template re-renders the tool call exactly as the
# model wrote it; if not, both stay flat and the cache claim is dropped).

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add",
            "description": "Add two integers and return the sum.",
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

PROMPT = (
    "Compute ((17 + 25) + 9) + 30. Use the add tool for every addition, one "
    "call at a time, and wait for each result before the next call. Then give "
    "the final number."
)


def post(base_url, body, timeout):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def run_tool(call):
    fn = call.get("function", {})
    args = fn.get("arguments")
    if isinstance(args, str):
        args = json.loads(args)
    if fn.get("name") != "add":
        return f"error: unknown tool {fn.get('name')!r}"
    return str(int(args["a"]) + int(args["b"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["echo", "rename"], required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    ap.add_argument("--max-requests", type=int, default=5)
    ap.add_argument("--max-tokens", type=int, default=4096)
    ap.add_argument("--timeout", type=float, default=900)
    ap.add_argument("--out", default=None, help="JSONL file for raw records")
    args = ap.parse_args()

    messages = [{"role": "user", "content": PROMPT}]
    rows = []
    out = open(args.out, "w") if args.out else None
    for turn in range(1, args.max_requests + 1):
        body = {
            "messages": messages,
            "tools": TOOLS,
            "temperature": 0.0,
            "max_tokens": args.max_tokens,
        }
        t0 = time.time()
        try:
            resp = post(args.base_url, body, args.timeout)
        except urllib.error.URLError as e:
            print(f"request {turn} failed: {e}", file=sys.stderr)
            return 2
        dt = time.time() - t0

        usage = resp.get("usage", {})
        cached = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
        choice = resp["choices"][0]
        msg = choice["message"]
        row = {
            "mode": args.mode,
            "turn": turn,
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "cached_tokens": cached,
            "finish_reason": choice.get("finish_reason"),
            "has_reasoning": bool(msg.get("reasoning")),
            "reasoning_chars": len(msg.get("reasoning") or ""),
            "n_tool_calls": len(msg.get("tool_calls") or []),
            "seconds": round(dt, 2),
        }
        rows.append(row)
        if out:
            out.write(json.dumps({"row": row, "request": body, "response": resp}))
            out.write("\n")
            out.flush()

        if turn == 1 and cached:
            print(
                f"WARNING: turn 1 cached_tokens={cached}. The server cache is "
                "warm; restart the server and run again.",
                file=sys.stderr,
            )

        # The client step under test: what goes back into the history.
        returned = dict(msg)
        if args.mode == "rename" and "reasoning" in returned:
            returned["reasoning_content"] = returned.pop("reasoning")
        messages.append(returned)

        tool_calls = msg.get("tool_calls") or []
        if not tool_calls:
            break
        for call in tool_calls:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "content": run_tool(call),
                }
            )

    if out:
        out.close()

    print(f"\nmode={args.mode}")
    hdr = "turn  prompt  completion  cached  prev_ctx  reasoning  tools  finish"
    print(hdr)
    prev_ctx = None
    for r in rows:
        print(
            f"{r['turn']:>4}  {r['prompt_tokens']!s:>6}  {r['completion_tokens']!s:>10}"
            f"  {r['cached_tokens']!s:>6}  {prev_ctx!s:>8}"
            f"  {r['reasoning_chars']:>9}  {r['n_tool_calls']:>5}  {r['finish_reason']}"
        )
        if r["prompt_tokens"] is not None and r["completion_tokens"] is not None:
            prev_ctx = r["prompt_tokens"] + r["completion_tokens"]
    if len(rows) < 2 or not any(r["n_tool_calls"] for r in rows):
        print(
            "\nNOTE: the model made no tool call chain, so this run says nothing "
            "about turn-2 caching. Try a larger --max-tokens or another prompt."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
