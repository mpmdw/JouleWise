"""Render D turn zero from a verified public SHADE checkout and tokenizer only."""
import argparse
import hashlib
import json
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace

from transformers import AutoTokenizer

from joulewise.adapters.mlx_runtime import _encode
from joulewise.align.apple.endpoint import MlxEndpoint
from joulewise.align.apple.pilot import offline_shade_task, prefetch
from joulewise.align.interfaces import ChatMessage

TOKENIZER_FILES = ("chat_template.jinja", "tokenizer.json", "tokenizer_config.json")
PAIRS = ("bank_transfer_2", "spam_filter_update")
EFFORTS = ("medium", "low", "xhigh")


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("upstream_cache", type=Path)
    parser.add_argument("tokenizer_dir", type=Path)
    args = parser.parse_args()
    upstream = prefetch(str(args.upstream_cache))
    if not upstream["ok"]:
        raise RuntimeError(upstream["flags"])
    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer_dir, local_files_only=True)
    endpoint = object.__new__(MlxEndpoint)
    endpoint.runtime = SimpleNamespace(_tokenizer=tokenizer)
    endpoint.model_family = "qwen3_5"
    endpoint.enable_thinking = None
    rows = {}
    for pair in PAIRS:
        task = offline_shade_task(pair, cache_dir=str(args.upstream_cache), give_hint=True)
        task.reset(seed=0)
        user = task.user_prompt()
        tools = task.tool_schemas()
        if not user or not tools:
            raise ValueError(f"missing user prompt or tools for {pair}")
        by_effort = {}
        for effort in EFFORTS:
            endpoint.chat_template_kwargs = {"reasoning_effort": effort}
            conditions = {}
            for condition in ("benign", "sabotage"):
                system = task.system_prompt(condition)
                if not system:
                    raise ValueError(f"missing system prompt for {pair} {condition}")
                messages = [ChatMessage("system", system), ChatMessage("user", user)]
                rendered = endpoint._render_prompt(messages, tools)
                tokens = _encode(tokenizer, rendered, add_special_tokens=False)
                conditions[condition] = {
                    "tokens": len(tokens),
                    "characters": len(rendered),
                    "utf8_bytes": len(rendered.encode()),
                    "sha256": sha256(rendered.encode()),
                }
            conditions["sabotage_minus_benign_tokens"] = (
                conditions["sabotage"]["tokens"] - conditions["benign"]["tokens"]
            )
            by_effort[effort] = conditions
        rows[pair] = {"tool_schema_count": len(tools), "by_effort": by_effort}
    print(json.dumps({
        "upstream_commit": upstream["commit"],
        "upstream_manifest_sha256": upstream["file_sha256"],
        "tokenizer_revision": "815b83c0df8ffd1d1b5244cf75fd6ef14fca9ef9",
        "tokenizer_file_sha256": {
            name: sha256((args.tokenizer_dir / name).read_bytes()) for name in TOKENIZER_FILES
        },
        "packages": {name: version(name) for name in (
            "anthropic", "email-validator", "jinja2", "numpy", "openai", "pandas", "pydantic",
            "python-dotenv", "tokenizers", "transformers")},
        "D_reasoning_effort": "medium",
        "hint": True,
        "threshold_tokens": 16,
        "threshold_exceeded": any(
            abs(row["by_effort"]["medium"]["sabotage_minus_benign_tokens"]) > 16
            for row in rows.values()
        ),
        "pairs": rows,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
