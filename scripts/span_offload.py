#!/usr/bin/env python3
"""Span cloud offload CLI (RL-173 A). Library and key scheme: ``joulewise/span_offload.py``;
runbook: ``docs/ops/SPAN-OFFLOAD.md``.

MBP (after a span's Check, before the next soak; bytes only, no journal is parsed):
    python3.13 -B scripts/span_offload.py offload --config CONFIG.json --plan PLAN --span-dir OUT \\
        [--require-file runner_receipt.json] [--deadline-epoch EPOCH]
    python3.13 -B scripts/span_offload.py evidence --config CONFIG.json --plan PLAN --span-dir OUT
Air (later; verifies against the marker's hashes and decrypts read-only):
    python3.13 -B scripts/span_offload.py pull --config AIR.json --plan PLAN --kit KIT \\
        --dest-root /Volumes/JW-EXT/cadence-desk (--marker MARKER.ok | --expect-manifest-sha256 H \\
        --expect-ciphertext-sha256 H)
    python3.13 -B scripts/span_offload.py keygen --out-dir DIR [--openssl PATH]

Output is one line of operational codes and hashes. Exit codes: 0 ok, 1 internal, 2 usage, 3 marker
legacy marker exists / marker writer raced, 4 input or stability refused, 5 upload, provider access or
publication I/O failed, the deadline passed or the tool was terminated, 6 readback or pull integrity failure, 7 pull destination
exists (or an interrupted landing), 8 offload without observed iCloud readback (no copy-gate marker).
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import signal
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from joulewise import span_offload as so  # noqa: E402


def parser():
    top = argparse.ArgumentParser(prog="span_offload.py", description=__doc__.split("\n\n")[0])
    sub = top.add_subparsers(dest="command", required=True)
    off = sub.add_parser("offload", help="MBP: verified cloud copy with the original retained")
    off.add_argument("--config", required=True)
    off.add_argument("--plan", required=True)
    off.add_argument("--span-dir", required=True)
    off.add_argument("--require-file", action="append", default=None,
                     help="a basename that must exist directly under the span (existence only; not read); "
                          "default runner_receipt.json")
    off.add_argument("--deadline-epoch", type=float,
                     help="give up (no marker) if the offload cannot finish by this epoch (the next soak)")
    off.add_argument("--allow-local-backend", action="store_true",
                     help="tests and the interim sync folder only: the marker says provider_confirmed false")
    evidence = sub.add_parser("evidence", help="read-only verdict on the published copy marker")
    evidence.add_argument("--config", required=True)
    evidence.add_argument("--plan", required=True)
    evidence.add_argument("--span-dir", required=True, type=Path)
    pending = sub.add_parser("pending", help="GUI domain: read pending iCloud transfers before every arm")
    pending.add_argument("--config", required=True)
    ssd = sub.add_parser("ssd-copy", help="Air: retain ciphertext on the external SSD and issue a readback receipt")
    ssd.add_argument("--config", required=True)
    ssd.add_argument("--plan", required=True)
    ssd.add_argument("--marker", required=True)
    ssd.add_argument("--ssd-root", required=True)
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
    if args.command == "pending":
        result = so.pending_transfers(so.load_mbp_config(args.config))
        if not result["clear"]:
            raise so.unverified("ICLOUD_PENDING", "pending or unknown CloudDocs state; hold the arm")
        return f"ICLOUD_CLEAR scope={result['scope']} observed_epoch_s={result['observed_epoch_s']}"
    if args.command == "ssd-copy":
        receipt = so.ssd_copy(so.load_air_config(args.config), args.plan, so.read_record(args.marker), args.ssd_root)
        return f"SSD_COPY_OK plan={args.plan} receipt={receipt}"
    if args.command == "offload":
        # The config is a control file: it must not be read from inside OUT (A.4), so check before reading.
        if so._overlaps(args.config, args.span_dir):
            raise so.refused("PATH_OVERLAPS_SPAN", "the config file is inside the span directory")
        config = so.load_mbp_config(args.config)
        required = args.require_file if args.require_file is not None else ["runner_receipt.json"]
        record = so.offload(config, args.plan, args.span_dir, require_files=required,
                           allow_local=args.allow_local_backend, deadline_epoch=args.deadline_epoch)
        label = "OFFLOAD_OK" if record["provider_confirmed"] else "OFFLOAD_OK_UNCONFIRMED"
        marker = so.marker_path(config["marker_dir"], record["plan"], record["provider_confirmed"])
        return (f"{label} plan={record['plan']} backend={record['backend']['kind']} "
                f"provider_confirmed={str(record['provider_confirmed']).lower()} files={record['manifest_files']} "
                f"manifest_sha256={record['manifest_sha256']} ciphertext_sha256={record['ciphertext']['sha256']} "
                f"ciphertext_size={record['ciphertext']['size']} stage_reused={str(record['stage_reused']).lower()} "
                f"marker={marker}")
    if args.command == "pull":
        config = so.load_air_config(args.config)
        marker = None
        if args.marker:
            try:
                with so.open_regular(args.marker, "the marker", single_link=True) as handle:
                    marker = json.loads(handle.read(1 << 20))
            except (so.OffloadError, OSError, ValueError, RecursionError):
                raise so.refused("MARKER_SCHEMA", "the marker file is missing, not a regular file or not JSON") from None
        expect = so.expectations(marker, args.expect_manifest_sha256, args.expect_ciphertext_sha256)
        result = so.pull(config, args.plan, args.kit, args.dest_root, expect,
                         allow_local=args.allow_local_backend, deadline_epoch=args.deadline_epoch)
        return (f"PULL_OK plan={result['plan']} kit={result['kit']} files={result['files']} "
                f"manifest_sha256={result['manifest_sha256']} dest={result['dest']}")
    fingerprint = so.keygen(args.openssl, args.out_dir, args.bits)
    return f"KEYGEN_OK recipient_sha256={fingerprint} out_dir={args.out_dir}"


class Terminated(BaseException):
    """SIGTERM, SIGHUP or SIGINT: unwinding kills every child (openssl, brctl, rclone) before the tool exits."""


def _terminate(signum, _frame):
    so.kill_children()  # first, so no unwinding step waits on a stalled openssl
    raise Terminated(signum)


def main(argv=None):
    args = parser().parse_args(argv)
    if args.command == "evidence":
        try:
            if so._overlaps(args.config, args.span_dir):
                raise so.refused("PATH_OVERLAPS_SPAN")
            evidence = so.copy_evidence(so.load_mbp_config(args.config), args.plan, out_path=args.span_dir)
        except so.OffloadError as error:
            evidence = so.CopyEvidence("INVALID", error.code)
        print(json.dumps(asdict(evidence), sort_keys=True))
        if evidence.status == "CLEAR":
            return so.EXIT["ok"]
        return so.EXIT["refused"] if evidence.status == "INVALID" else so.EXIT["unverified"]
    previous = {sig: signal.signal(sig, _terminate) for sig in (signal.SIGTERM, signal.SIGHUP, signal.SIGINT)}
    try:
        line = run(args)
        print(line)
        return so.EXIT["unconfirmed"] if line.startswith("OFFLOAD_OK_UNCONFIRMED") else so.EXIT["ok"]
    except Terminated as stop:
        print(f"{args.command.upper()}_UNVERIFIED TERMINATED signal={stop.args[0]}", file=sys.stderr)
        return so.EXIT["unverified"]
    except so.OffloadError as error:
        print(f"{args.command.upper()}_{error.exit_kind.upper()} {error.code} {error.detail}".rstrip(), file=sys.stderr)
        return so.EXIT[error.exit_kind]
    except Exception as error:  # noqa: BLE001 - one line, no traceback text from the span
        print(f"{args.command.upper()}_INTERNAL {type(error).__name__}", file=sys.stderr)
        return so.EXIT["internal"]
    finally:
        for sig, handler in previous.items():
            signal.signal(sig, handler)


if __name__ == "__main__":
    sys.exit(main())
