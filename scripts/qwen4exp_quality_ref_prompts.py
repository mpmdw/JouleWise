#!/usr/bin/env python3
"""Prompt set for the Flash-Next bf16 quality reference (lead ruling L3).

Writes the ``--prompts-json`` for the second gold pass
(``scripts/run_qwen4_gold_stream.py --reference-chain-only``): the 12 hosted-
reference prompts (configs/qwen4_exp_port/hosted_reference_prompts.json), each
rendered by the pinned official chat template (thinking off, generation prompt
on) and followed by a short, fixed natural-text continuation cut from the
sha256-pinned public-domain excerpts in configs/qwen4_exp_port/e2e_items.json.
Continuations are never model output (maxfit's greedy text would make the
reference grade the candidate on its own tokens).  Every prompt is at most
512 tokens, tokenized with the official tokenizer at the pinned revision.

Two commands, both CPU-only and small:

  fetch-tokenizer --dest DIR   downloads the tokenizer files at revision
                               de4b8e4d (HF metadata-verified) and writes
                               DIR/pins.json
  build --tokenizer-dir DIR --out FILE
                               verifies DIR against pins.json, renders,
                               tokenizes and writes FILE (the --prompts-json
                               list) plus FILE.provenance.json
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts import qwen4exp_e2e_eval as e2e  # noqa: E402

SCHEMA = "qwen4exp-quality-ref-prompts/v1"
REPO_ID = "Qwen/Qwen3.8-Flash-Next"
REVISION = "de4b8e4d43b917e7706784d8bb445c9af86a3540"
TRANSFORMERS_VERSION = "5.22.1"
PROMPTS_PATH = ROOT / "configs" / "qwen4_exp_port" / "hosted_reference_prompts.json"
REQUIRED_FILES = ("tokenizer.json", "tokenizer_config.json", "chat_template.jinja")
OPTIONAL_FILES = ("special_tokens_map.json", "vocab.json", "merges.txt", "added_tokens.json", "config.json")
MAX_TOKENS = 512
CONTINUATION_TOKENS = 128
MIN_CONTINUATION_TOKENS = 32
SOURCE_CHARS = 4000  # more than enough text for 128 tokens of any excerpt

# Fixed continuation for each hosted prompt: (e2e nll excerpt id, anchor).
# The continuation is the excerpt's text from the anchor's unique occurrence.
# Language is matched where the set allows (Chinese, code-adjacent prose);
# otherwise English public-domain prose. long_context_qsa continues with the
# passage the question is about (Darcy at the assembly, chapter 3).
CONTINUATIONS: dict[str, tuple[str, str]] = {
    "photosynthesis": ("origin_intro", "When on board H.M.S."),
    "primes": ("us_constitution", "We the people of the United States"),
    "haiku": ("pp_ch1", "It is a truth universally acknowledged"),
    "derivative": ("origin_intro", "My work is now nearly finished"),
    "german": ("pp_ch1_3_long", "Mr. Bennet was among the earliest"),
    "zh_great_wall": ("lunyu_xueer", "1. 子曰：「學而時習之"),
    "palindrome_code": ("pep20_zen", "Beautiful is better than ugly."),
    "ww1_bullets": ("us_constitution", "Article 1"),
    "json_output": ("pp_ch1_3_long", "Not all that Mrs. Bennet"),
    "multi_turn": ("pp_ch1", "“My dear Mr. Bennet,” replied his wife"),
    "tool_weather": ("pp_ch1_3_long", "In a few days Mr. Bingley"),
    "long_context_qsa": ("pp_ch1_3_long", "Mr. Darcy soon drew the attention"),
}


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def safe_dir(path: Path) -> Path:
    path = Path(path).absolute()
    if "restricted" in path.parts:
        raise ValueError("restricted paths are refused")
    return path


# --------------------------------------------------------------------------
# Continuations and prompt construction (pure; tokenizer injected)
# --------------------------------------------------------------------------

def continuation_text(texts: Mapping[str, str], source: str, anchor: str) -> str:
    text = texts[source]
    if text.count(anchor) != 1:
        raise ValueError(f"continuation anchor must occur exactly once in {source}: {anchor!r}")
    start = text.index(anchor)
    return text[start:start + SOURCE_CHARS]


def _paragraph_prefixes(context: str) -> list[str]:
    parts = context.split("\n\n")
    return ["\n\n".join(parts[:n]) for n in range(1, len(parts) + 1)]


def build_prompts(encode: Callable[[str], Sequence[int]], template: Any, spec: Mapping[str, Any],
                  items: Mapping[str, Any], *, max_tokens: int = MAX_TOKENS,
                  continuation_tokens: int = CONTINUATION_TOKENS,
                  min_continuation: int = MIN_CONTINUATION_TOKENS) -> tuple[list[dict], list[dict]]:
    """Return (``--prompts-json`` rows, per-prompt provenance)."""
    if not 0 < min_continuation <= continuation_tokens < max_tokens:
        raise ValueError("need 0 < min continuation <= continuation tokens < max tokens")
    natural = {e["id"]: e for e in items["nll"] if e.get("kind") == "natural"}
    texts = {k: v["text"] for k, v in natural.items()}
    ids = [p["id"] for p in spec["prompts"]]
    if sorted(ids) != sorted(CONTINUATIONS):
        raise ValueError(f"hosted prompts and continuation table differ: {sorted(set(ids) ^ set(CONTINUATIONS))}")
    rows, provenance = [], []
    for prompt in spec["prompts"]:
        source, anchor = CONTINUATIONS[prompt["id"]]
        if source not in texts:
            raise ValueError(f"unknown natural excerpt {source}")
        continuation = list(map(int, encode(continuation_text(texts, source, anchor))))
        context_note = None

        def render(messages):
            return template.render(messages, prompt.get("tools"), add_generation_prompt=True, enable_thinking=False)
        if "context_from" in prompt:
            # Fit the context to the budget at a paragraph boundary: the
            # largest whole-paragraph prefix leaving room for the full
            # continuation.
            context = texts[prompt["context_from"]]
            chosen = None
            for prefix in _paragraph_prefixes(context):
                messages = [dict(m, content=m["content"].replace("{context}", prefix)) for m in prompt["messages"]]
                if len(encode(render(messages))) + continuation_tokens > max_tokens:
                    break
                chosen = (prefix, messages)
            if chosen is None:
                raise ValueError(f"{prompt['id']}: no whole paragraph of context fits {max_tokens} tokens")
            prefix, messages = chosen
            context_note = {"context_from": prompt["context_from"],
                            "context_sha256": natural[prompt["context_from"]]["sha256"],
                            "context_chars": len(prefix), "context_paragraphs": prefix.count("\n\n") + 1,
                            "context_truncated": len(prefix) < len(context)}
        else:
            messages = prompt["messages"]
        rendered = render(messages)
        prompt_ids = list(map(int, encode(rendered)))
        budget = min(continuation_tokens, max_tokens - len(prompt_ids))
        if budget < min_continuation or len(continuation) < min_continuation:
            raise ValueError(f"{prompt['id']}: continuation shorter than {min_continuation} tokens")
        tail = continuation[:budget]
        input_ids = prompt_ids + tail
        if len(input_ids) > max_tokens:
            raise AssertionError("token budget violated")
        name = "hosted-" + prompt["id"]
        rows.append({"name": name, "input_ids": input_ids, "continuation_from": len(prompt_ids)})
        provenance.append({"name": name, "prompt_tokens": len(prompt_ids), "continuation_tokens": len(tail),
                           "total_tokens": len(input_ids), "rendered_sha256": sha256_bytes(rendered.encode()),
                           "continuation": {"source": source, "source_sha256": natural[source]["sha256"],
                                            "anchor": anchor},
                           **({"context": context_note} if context_note else {})})
    if len({r["name"] for r in rows}) != len(rows):
        raise ValueError("prompt names are not unique")
    return rows, provenance


# --------------------------------------------------------------------------
# Tokenizer files at the pinned revision
# --------------------------------------------------------------------------

def _verify_against(info: Any, raw: bytes) -> dict[str, Any]:
    if len(raw) != info.size:
        raise ValueError(f"size mismatch: {info.path}")
    if info.lfs is not None:
        if sha256_bytes(raw) != info.lfs.sha256:
            raise ValueError(f"LFS sha256 mismatch: {info.path}")
        return {"lfs_sha256": info.lfs.sha256}
    if git_blob_sha1(raw) != info.blob_id:
        raise ValueError(f"git blob mismatch: {info.path}")
    return {"git_blob_id": info.blob_id}


def fetch_tokenizer(dest: Path, api: Any = None, download: Callable[..., str] | None = None) -> dict[str, Any]:
    """Download the tokenizer files at REVISION and pin them by HF metadata."""
    dest = safe_dir(dest)
    dest.mkdir(parents=True, exist_ok=True)
    if api is None or download is None:
        from huggingface_hub import HfApi, hf_hub_download
        api, download = api or HfApi(), download or hf_hub_download
    infos = {i.path: i for i in api.get_paths_info(REPO_ID, list(REQUIRED_FILES + OPTIONAL_FILES), revision=REVISION)}
    missing = [f for f in REQUIRED_FILES if f not in infos]
    if missing:
        raise ValueError(f"pinned revision lacks {missing}")
    files = {}
    for name in sorted(infos):
        if infos[name].size > 64 * 2**20:
            raise ValueError(f"{name} exceeds 64 MiB")
        path = Path(download(REPO_ID, name, revision=REVISION, local_dir=str(dest)))
        if path.resolve() != (dest / name).resolve() or path.is_symlink():
            raise ValueError("hub must return a regular file in --dest")
        raw = path.read_bytes()
        files[name] = {"sha256": sha256_bytes(raw), "size": len(raw), **_verify_against(infos[name], raw)}
    pins = {"schema": SCHEMA + "#tokenizer-pins", "repo": REPO_ID, "revision": REVISION, "files": files}
    (dest / "pins.json").write_text(json.dumps(pins, indent=2, sort_keys=True) + "\n")
    return pins


def verify_tokenizer_dir(directory: Path) -> dict[str, Any]:
    directory = safe_dir(directory)
    pins_path = directory / "pins.json"
    if not pins_path.is_file():
        raise ValueError(f"{pins_path} missing: run fetch-tokenizer first")
    pins = json.loads(pins_path.read_text())
    if pins.get("repo") != REPO_ID or pins.get("revision") != REVISION:
        raise ValueError("tokenizer pins are not for the pinned Flash-Next revision")
    for name in REQUIRED_FILES:
        if name not in pins["files"]:
            raise ValueError(f"pins lack {name}")
    for name, row in pins["files"].items():
        path = directory / name
        if path.is_symlink() or not path.is_file() or sha256_file(path) != row["sha256"]:
            raise ValueError(f"tokenizer file changed since it was pinned: {name}")
    return pins


def load_tokenizer(directory: Path) -> Any:
    if importlib.metadata.version("transformers") != TRANSFORMERS_VERSION:
        raise ValueError(f"tokenization requires transformers {TRANSFORMERS_VERSION} (use venv-ref)")
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(str(directory), local_files_only=True, trust_remote_code=False)


class _Encoder:
    """The e2e adapters' tokenizer contract (no BOS; special text -> one id)."""
    def __init__(self, tokenizer: Any) -> None:
        self.tokenizer = tokenizer

    def encode(self, text: str) -> list[int]:
        return list(self.tokenizer.encode(text, add_special_tokens=False))

    def decode(self, ids: Sequence[int]) -> str:
        return self.tokenizer.decode(list(ids))


def build(args: argparse.Namespace, tokenizer: Any = None) -> dict[str, Any]:
    directory = safe_dir(args.tokenizer_dir)
    pins = verify_tokenizer_dir(directory)
    template = e2e.ChatTemplate(directory / "chat_template.jinja")  # refuses an unpinned template
    encoder = _Encoder(tokenizer if tokenizer is not None else load_tokenizer(directory))
    preflight = e2e.tokenizer_preflight(encoder)
    if not preflight["ok"]:
        raise ValueError(f"tokenizer preflight failed: {preflight['mismatches']}")
    raw_spec = PROMPTS_PATH.read_bytes()
    spec = json.loads(raw_spec)
    if spec.get("schema") != "qwen4exp-hosted-prompts/v1":
        raise ValueError("unexpected hosted prompts schema")
    items = e2e.load_items()  # re-verifies every excerpt sha256
    rows, provenance = build_prompts(encoder.encode, template, spec, items, max_tokens=args.max_tokens,
                                     continuation_tokens=args.continuation_tokens)
    out = safe_dir(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    temp = out.with_name(out.name + ".tmp")
    temp.write_text(json.dumps(rows, indent=1) + "\n")
    temp.replace(out)
    record = {"schema": SCHEMA, "prompts_json": str(out), "prompts_json_sha256": sha256_file(out),
              "ruling": "L3 (docs/align/council-2026-11-06-v4-review/LEAD-RULINGS-1.md)",
              "tokenizer": {"repo": REPO_ID, "revision": REVISION, "files": pins["files"],
                            "transformers": TRANSFORMERS_VERSION, "preflight": preflight},
              "template_sha256": template.sha256, "hosted_prompts_sha256": sha256_bytes(raw_spec),
              "items_sha256": items["_file_sha256"], "max_tokens": args.max_tokens,
              "continuation_tokens": args.continuation_tokens,
              "total_tokens": sum(len(r["input_ids"]) for r in rows), "prompts": provenance}
    out.with_name(out.name + ".provenance.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    return record


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = root.add_subparsers(dest="command", required=True)
    p = sub.add_parser("fetch-tokenizer")
    p.add_argument("--dest", type=Path, required=True)
    p = sub.add_parser("build")
    p.add_argument("--tokenizer-dir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--max-tokens", type=int, default=MAX_TOKENS)
    p.add_argument("--continuation-tokens", type=int, default=CONTINUATION_TOKENS)
    return root


def main(argv: Sequence[str] | None = None, *, tokenizer: Any = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "fetch-tokenizer":
        pins = fetch_tokenizer(args.dest)
        print(json.dumps({"dest": str(args.dest), "files": sorted(pins["files"])}, indent=1))
        return 0
    if args.max_tokens > MAX_TOKENS:
        raise ValueError(f"lead ruling L3 caps each prompt at {MAX_TOKENS} tokens")
    record = build(args, tokenizer)
    print(json.dumps({"out": record["prompts_json"], "sha256": record["prompts_json_sha256"],
                      "prompts": len(record["prompts"]), "total_tokens": record["total_tokens"],
                      "per_prompt": {p["name"]: p["total_tokens"] for p in record["prompts"]}}, indent=1))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2)
