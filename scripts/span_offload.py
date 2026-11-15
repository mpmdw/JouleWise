#!/usr/bin/env python3
"""Span cloud offload CLI (RL-173 A). Library and key scheme: ``joulewise/span_offload.py``;
runbook: ``docs/ops/SPAN-OFFLOAD.md``.

MBP (after a span's close, before the next soak; bytes only, no journal is parsed):
    python3.13 -B scripts/span_offload.py offload --config CONFIG.json --plan PLAN --span-dir OUT \\
        [--require-file runner_receipt.json] [--deadline-epoch EPOCH]
Air (later; verifies against the marker's hashes and decrypts read-only):
    python3.13 -B scripts/span_offload.py pull --config AIR.json --plan PLAN --kit KIT \\
        --dest-root /Volumes/JW-EXT/cadence-desk (--marker MARKER.ok | --expect-manifest-sha256 H \\
        --expect-ciphertext-sha256 H)
    python3.13 -B scripts/span_offload.py keygen --out-dir DIR [--openssl PATH]

Output is one line of operational codes and hashes. Exit codes: 0 ok, 1 internal, 2 usage, 3 marker
already exists (nothing done), 4 refused before upload, 5 upload or provider read-back failed (no marker),
6 pull integrity failure, 7 pull destination exists.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise import span_offload as so  # noqa: E402


def parser():
    top = argparse.ArgumentParser(prog="span_offload.py", description=__doc__.split("\n\n")[0])
    sub = top.add_subparsers(dest="command", required=True)
    off = sub.add_parser("offload", help="MBP: archive, encrypt, upload, read back, write the marker")
    off.add_argument("--config", required=True)
    off.add_argument("--plan", required=True)
    off.add_argument("--span-dir", required=True)
    off.add_argument("--require-file", action="append", default=[],
                     help="a basename that must exist directly under the span (existence only; not read)")
    off.add_argument("--deadline-epoch", type=float,
                     help="give up (no marker) if the offload cannot finish by this epoch (the next soak)")
    off.add_argument("--allow-local-backend", action="store_true",
                     help="tests and the interim sync folder only: the marker says provider_confirmed false")
    pl = sub.add_parser("pull", help="Air: fetch, verify against the marker, decrypt read-only")
    pl.add_argument("--config", required=True)
    pl.add_argument("--plan", required=True)
    pl.add_argument("--kit", required=True)
    pl.add_argument("--dest-root", required=True)
    pl.add_argument("--marker", help="a copy of the MBP's <plan>.ok marker")
    pl.add_argument("--expect-manifest-sha256")
    pl.add_argument("--expect-ciphertext-sha256")
    pl.add_argument("--deadline-epoch", type=float)
    pl.add_argument("--allow-local-backend", action="store_true")
    kg = sub.add_parser("keygen", help="Air: make the recipient key pair (the private key never goes to the MBP)")
    kg.add_argument("--out-dir", required=True)
    kg.add_argument("--openssl", default="openssl")
    kg.add_argument("--bits", type=int, default=4096)
    return top


def run(args):
    if args.command == "offload":
        config = so.load_mbp_config(args.config)
        record = so.offload(config, args.plan, args.span_dir, require_files=args.require_file,
                            allow_local=args.allow_local_backend, deadline_epoch=args.deadline_epoch)
        return (f"OFFLOAD_OK plan={record['plan']} backend={record['backend']['kind']} "
                f"provider_confirmed={str(record['provider_confirmed']).lower()} files={record['manifest_files']} "
                f"manifest_sha256={record['manifest_sha256']} ciphertext_sha256={record['ciphertext']['sha256']} "
                f"ciphertext_size={record['ciphertext']['size']} stage_reused={str(record['stage_reused']).lower()} "
                f"marker={Path(config['marker_dir']) / (record['plan'] + '.ok')}")
    if args.command == "pull":
        config = so.load_air_config(args.config)
        marker = None
        if args.marker:
            try:
                marker = json.loads(Path(args.marker).read_bytes())
            except (OSError, ValueError):
                raise so.refused("MARKER_SCHEMA", "the marker file is missing or not JSON") from None
        expect = so.expectations(marker, args.expect_manifest_sha256, args.expect_ciphertext_sha256)
        result = so.pull(config, args.plan, args.kit, args.dest_root, expect,
                         allow_local=args.allow_local_backend, deadline_epoch=args.deadline_epoch)
        return (f"PULL_OK plan={result['plan']} kit={result['kit']} files={result['files']} "
                f"manifest_sha256={result['manifest_sha256']} dest={result['dest']}")
    fingerprint = so.keygen(args.openssl, args.out_dir, args.bits)
    return f"KEYGEN_OK recipient_sha256={fingerprint} out_dir={args.out_dir}"


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        print(run(args))
        return so.EXIT["ok"]
    except so.OffloadError as error:
        print(f"{args.command.upper()}_{error.exit_kind.upper()} {error.code} {error.detail}".rstrip(), file=sys.stderr)
        return so.EXIT[error.exit_kind]
    except Exception as error:  # noqa: BLE001 - one line, no traceback text from the span
        print(f"{args.command.upper()}_INTERNAL {type(error).__name__}", file=sys.stderr)
        return so.EXIT["internal"]


if __name__ == "__main__":
    sys.exit(main())
