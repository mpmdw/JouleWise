#!/usr/bin/env python3
"""Initialize the shared attempt ledger once, under RL-197c."""

import argparse
from contextlib import ExitStack
import fcntl
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
CTL_PIN = "f45e22e4efa6b48dd05f099f39eb62246e324177"
if __name__ == "__main__":
    sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
from scripts import launch_align_r0 as desk  # noqa: E402


def git(root, *args):
    return subprocess.check_output(["git", "--no-optional-locks", "-C", root, *args], text=True).strip()


def stage(cleanup, directory, payload):
    with tempfile.NamedTemporaryFile(dir=directory, delete=False) as handle:
        path = Path(handle.name)
        cleanup.callback(path.unlink, missing_ok=True)
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    return path


def initialize(args):
    ledger = args.ledger.absolute()
    sidecar = ledger.with_name(ledger.name + ".first-row.json")
    receipt = Path(args.close_receipt)
    ctl = args.ctl_checkout.resolve()
    # Pin B created the common lock at launch. Never create a lock in a new root.
    with os.fdopen(os.open(args.custody_root / ".desk-fence.lock", os.O_RDWR | os.O_NOFOLLOW)) as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if os.path.lexists(ledger) or os.path.lexists(sidecar):
            raise ValueError("ledger or first-row sidecar already exists")
        fence = desk.read_fence(args.custody_root)
        if fence and fence["deadline"] > time.time() and desk.pid_alive(fence["pid"]):
            raise ValueError("an active desk fence already exists")
        if (git(ctl, "rev-parse", "HEAD") != CTL_PIN or Path(git(ctl, "rev-parse", "--show-toplevel")) != ctl
                or git(ctl, "status", "--porcelain")):
            raise ValueError("ctl checkout must be clean and at the runner pin")
        if not receipt.is_absolute() or sha256(receipt.read_bytes()).hexdigest() != args.receipt_sha256:
            raise ValueError("close receipt must have an absolute path and match its SHA-256")
        row = {"span_id": args.span_id, "close_receipt": args.close_receipt, "sequence": 1}
        payload = (json.dumps({"attempts": [row]}) + "\n").encode()
        digest = sha256(payload).hexdigest()
        with ExitStack() as rollback, ExitStack() as cleanup:
            temporary = stage(cleanup, ledger.parent, payload)
            proof = subprocess.check_output([args.python_bin.absolute(), "-I", "-B",
                                             ctl / "scripts/launch_cadence_span.py", "close-proof",
                                             "--attempt-ledger", temporary], cwd=ctl)
            if proof != f"{args.span_id}\n{args.close_ns}\n{args.close_receipt}\n".encode():
                raise ValueError("close-proof output differs from the issued span, close ns or receipt path")
            if sha256(receipt.read_bytes()).hexdigest() != args.receipt_sha256:
                raise ValueError("close receipt SHA-256 changed during proof")
            rollback.callback(desk.sync_directory, ledger.parent)
            os.link(temporary, ledger)
            rollback.callback(ledger.unlink)
            desk.sync_directory(ledger.parent)
            temporary.unlink()
            record = dict(ruling="RL-197c", run_state_item=args.run_state_item, span_id=args.span_id,
                          close_receipt=args.close_receipt, receipt_sha256=args.receipt_sha256, close_ns=int(args.close_ns),
                          close_proof=proof.decode(), ledger_sha256=digest, initializer_commit=git(ROOT, "rev-parse", "HEAD"))
            os.link(stage(cleanup, ledger.parent, (json.dumps(record) + "\n").encode()), sidecar)
            rollback.callback(sidecar.unlink)
            cleanup.close()
            desk.sync_directory(ledger.parent)
            print(digest, flush=True)
            rollback.pop_all()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("ledger", "custody-root", "ctl-checkout", "python-bin"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    for name in ("span-id", "close-receipt", "receipt-sha256", "close-ns"):
        parser.add_argument(f"--{name}", required=True)
    parser.add_argument("--run-state-item", type=int, required=True)
    try:
        initialize(parser.parse_args(argv))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"attempt ledger initialization refused: {error}", file=sys.stderr)
        return 2
    return 0

if __name__ == "__main__":
    sys.exit(main())
