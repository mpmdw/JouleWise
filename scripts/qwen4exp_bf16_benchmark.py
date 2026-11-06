#!/usr/bin/env python3
"""Run PR671's SAME fixed items via a separately operated BF16 completions host.

No model weights load on the Mac. --dry-run makes no requests/imports/writes.
This does not provision or rent a host. The operator supplies its identity
receipt; server configuration and checkpoint hashes must be independently
verified. An API model name alone is not evidence of BF16 or weight identity.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qwen4exp_e2e_eval as e2e
import qwen4exp_mbp_live as live


def validate_identity(identity):
    expected = {"repo": live.REPO_ID, "revision": live.REVISION, "dtype": "bfloat16",
                "quantization": None, "kv_cache_dtype": "auto", "mtp": False,
                "transformers": "5.22.1", "template_sha256": e2e.TEMPLATE_SHA256}
    if any(identity.get(k) != v for k, v in expected.items()) or not all(k in identity for k in expected):
        raise ValueError("reference identity receipt does not match pinned unquantized BF16 setup")
    for key in ("server_command", "server_version", "checkpoint_sha256_manifest"):
        if not identity.get(key):
            raise ValueError(f"reference identity receipt needs {key}")
    return identity


class HostedAdapter:
    def __init__(self, tokenizer, endpoint, identity, *, poster=None):
        self.tokenizer, self.endpoint = tokenizer, endpoint.rstrip("/")
        self.identity = "operator-attested-bf16:" + live.REVISION
        self.receipt = validate_identity(identity)
        self.poster = poster or self._post

    def encode(self, text):
        return list(self.tokenizer.encode(text, add_special_tokens=False))

    def decode(self, ids):
        return self.tokenizer.decode(list(ids), skip_special_tokens=False)

    def _post(self, body):
        headers = {"Content-Type": "application/json"}
        if key := os.environ.get("VLLM_API_KEY"):
            headers["Authorization"] = "Bearer " + key
        req = Request(self.endpoint + "/completions", json.dumps(body).encode(), headers)
        with urlopen(req, timeout=900) as response:
            return json.load(response)

    def generate(self, prompt_ids, *, max_tokens, stop_ids=e2e.EOS_IDS, top_k=0):
        # Sending token IDs avoids decode/re-encode changes on the server.
        body = {"model": live.REPO_ID, "prompt": list(prompt_ids), "temperature": 0,
                "top_p": 1, "max_tokens": max_tokens, "seed": 0,
                "presence_penalty": 0, "frequency_penalty": 0, "repetition_penalty": 1,
                "stop_token_ids": list(stop_ids), "skip_special_tokens": False}
        started = time.perf_counter()
        response = self.poster(body)
        if response["usage"]["prompt_tokens"] != len(prompt_ids):
            raise ValueError("hosted prompt-token count mismatch")
        choice = response["choices"][0]
        text = choice["text"]
        ids = self.encode(text)
        # Scores use text + exact same harness/checkers, not token logprobs.
        return e2e.Generation(ids, text, choice["finish_reason"], prompt_tokens=len(prompt_ids),
                              seconds=time.perf_counter() - started)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--validation-only", action="store_true")
    p.add_argument("--endpoint", help="separately operated BF16 vLLM /v1 URL")
    p.add_argument("--tokenizer", type=Path, help="verified local HF source snapshot")
    p.add_argument("--identity", type=Path, help="operator's hosted BF16 identity receipt")
    p.add_argument("--out", type=Path)
    args = p.parse_args(argv)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "requests_sent": 0,
                          "stages": "coherence,toolcall,math,ifeval", "revision": live.REVISION,
                          "needs": "separately verified BF16 host; no infrastructure is provisioned"}))
        return 0
    if not args.validation_only or not all((args.endpoint, args.tokenizer, args.identity, args.out)):
        p.error("live collection requires --validation-only, --endpoint, --tokenizer, --identity, --out")
    args.out = live.external(args.out)
    if args.out.exists():
        raise ValueError("preserve existing evidence; use a new output")
    identity = validate_identity(json.loads(live.external(args.identity).read_text()))
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(live.external(args.tokenizer), local_files_only=True,
                                              trust_remote_code=False)
    adapter = HostedAdapter(tokenizer, args.endpoint, identity)
    opts = e2e.parse_args(["--quant-profile", "bf16", "--stages", "coherence,toolcall,math,ifeval",
                           "--chat-template", str(live.external(args.tokenizer) / "chat_template.jinja")])
    report = e2e.run(opts, adapter=adapter)
    report["hosted_identity"] = identity
    report["identity_evidence"] = "operator attestation; independently verify server logs and checkpoint hashes"
    live.write_json(args.out, report)
    return 1 if report["verdict"] == "fail" else 0


if __name__ == "__main__":
    sys.exit(main())
