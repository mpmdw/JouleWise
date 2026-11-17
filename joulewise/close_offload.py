"""After-Check selection and supervision for the shared span-offload backend."""

from __future__ import annotations

import argparse
import contextlib
from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import time

from joulewise import span_offload as so

CAMPAIGN_ROOT = Path("/Users/edr/campaign-out")
WORK_ROOT = Path("/Users/edr/code/jw-wt")
FENCE = Path("/Users/edr/night-custody/magistrate/desk_fence.json")
RUNNERS = (r"(^|/|[[:space:]])(run_align_r1_smoke|cadence_legs_runner|launch_cadence_span|"
           r"align_r1_runtime|align_r0_checks|align_v4_session|align_r1_rehearsal)([.]py)?([[:space:]]|$)")
STAMPED = re.compile(r"(.+)-[0-9]{8}T[0-9]{6}Z")
AIR_FALLBACK = "AIR FALLBACK (item 388): verified iCloud copy; MBP archive retained for later SSD pull"


@dataclass(frozen=True)
class Span:
    kind: str
    path: Path
    plan: str
    receipt_mtime_ns: int | None  # None for an interrupted retirement


def real_directory(path):
    return stat.S_ISDIR(path.lstat().st_mode) if os.path.lexists(path) else False


def span_plan(kind, path):
    if kind == "partc":
        return so.check_id(path.name, "Part C output")
    match = STAMPED.fullmatch(path.name)
    if not match:
        raise so.refused("BAD_SPAN_NAME", "expected a timestamped campaign OUT")
    so.check_id(path.name, "campaign output")
    return so.check_id(match[1], "campaign plan")


def scan_spans(args, deadline):
    """Use receipt metadata only. Keep every newest-mtime tie within each kind."""
    found = []
    for kind, root in (("campaign", args.campaign_root), ("partc", args.work_root)):
        if not real_directory(root) or Path(root.resolve()) != root:
            raise so.refused("RECEIPT_ROOT", "a GAP receipt root is missing or linked")
        for tree in sorted(root.iterdir()):
            deadline.remaining()
            if not real_directory(tree):
                continue
            parent = tree if kind == "campaign" else tree / ".desk"
            if not real_directory(parent):
                continue
            for entry in sorted(parent.iterdir()):
                deadline.remaining()
                retiring = entry.name.startswith(so.RETIREMENT_PREFIX)
                path = entry.with_name(entry.name.removeprefix(so.RETIREMENT_PREFIX))
                if kind == "partc" and not path.name.startswith("r1-partc-"):
                    continue
                if retiring:
                    if not real_directory(entry) or os.path.lexists(path):
                        raise so.refused("RETIREMENT_CONFLICT", "invalid interrupted retirement")
                    found.append(Span(kind, path, span_plan(kind, path), None))
                elif real_directory(entry):
                    receipt = path / "runner_receipt.json"
                    if os.path.lexists(receipt):
                        info = receipt.lstat()
                        if not stat.S_ISREG(info.st_mode):
                            raise so.refused("NONREGULAR_RECEIPT", "a runner receipt is not a regular file")
                        found.append(Span(kind, path, span_plan(kind, path), info.st_mtime_ns))
    if len({span.plan.casefold() for span in found}) != len(found):
        raise so.refused("PLAN_COLLISION", "two outputs would share an offload plan")
    return found


class Guard:
    def __init__(self, args):
        self.fence = args.fence
        self.deadline = so.Deadline(args.deadline_epoch)
        self.pgrep = shutil.which("pgrep")
        if not self.pgrep or any(so._overlaps(root, self.pgrep) for root in (args.campaign_root, args.work_root)):
            raise so.refused("RUNNER_CENSUS_FAILED", "runner census executable is missing or inside a receipt root")

    def quiet(self):
        if os.path.lexists(self.fence):
            raise so.refused("DESK_FENCE_PRESENT", "close requires the desk fence to be down")
        try:
            probe = subprocess.run([self.pgrep, "-f", RUNNERS], stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL, timeout=self.deadline.remaining())
        except subprocess.TimeoutExpired:
            raise so.unverified("DEADLINE", "runner census timed out") from None
        if probe.returncode == 0:
            raise so.refused("RUNNER_PRESENT", "a measurement runner is present")
        if probe.returncode != 1:
            raise so.refused("RUNNER_CENSUS_FAILED", "runner absence could not be verified")

    @contextlib.contextmanager
    def lock(self):
        self.quiet()
        lock = self.fence.parent / ".desk-fence.lock"
        fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise so.refused("DESK_LOCK_BUSY", "the desk fence lock is held") from None
            self.quiet()
            yield
        finally:
            os.close(fd)


def outside_receipt_roots(args, paths):
    for root in (args.campaign_root, args.work_root):
        so.check_output_paths(root, paths)


def load_config(args):
    config = so.load_mbp_config(args.config)
    backend = so.make_backend(config.get("backend", {}))
    if not isinstance(backend, so.ICloudBackend):
        raise so.refused("ICLOUD_REQUIRED", "close requires observed iCloud readback")
    controls = {"stage root": config["stage_root"], "marker directory": config["marker_dir"],
                "public key": config["recipient_public_key"], "cloud root": backend.root}
    for name, executable in (("OpenSSL", config.get("openssl", "openssl")), ("brctl", backend.brctl)):
        resolved = shutil.which(executable)
        if resolved and any(so._overlaps(root, resolved) for root in (args.campaign_root, args.work_root)):
            raise so.refused("PATH_OVERLAPS_SPAN", f"{name} is inside a receipt root")
    if args.command == "reclaim":
        controls["SSD receipt"] = args.ssd_receipt
    outside_receipt_roots(args, controls)
    return config


def close_one(args, config, span, *, retain_original=False, ssd_receipt=None):
    record = so.close_offload(config, span.plan, span.path, retain_original=retain_original,
                              ssd_receipt=ssd_receipt, deadline_epoch=args.deadline_epoch,
                              partc_work_root=args.work_root if span.kind == "partc" else None)
    return {"plan": span.plan, "original_deleted": record["original_deleted"],
            "archive_evicted": record["archive_evicted"], "storage_mail_sent": record["storage_mail_sent"],
            "manifest_sha256": record["manifest_sha256"], "ciphertext_sha256": record["ciphertext"]["sha256"]}


def checked_close(args, config, guard, spans):
    checked = next((span for span in spans if span.path == args.span_dir and span.receipt_mtime_ns is not None), None)
    if checked is None:
        raise so.refused("CHECK_OUT_REQUIRED", "the exact Check OUT must have a regular runner receipt")
    newest = {}
    for span in spans:
        if span.receipt_mtime_ns is not None:
            newest[span.kind] = max(newest.get(span.kind, span.receipt_mtime_ns), span.receipt_mtime_ns)
    eligible = [span for span in spans if span != checked and
                (span.receipt_mtime_ns is None or span.receipt_mtime_ns < newest[span.kind])]

    # Resume interrupted removals and rotate the most recent eligible output of each kind.
    # Catch-up can also retire older receipt-bearing outputs in the same close interval.
    selected = set()
    guard.quiet()
    results = [close_one(args, config, checked, retain_original=True)]
    for span in sorted(eligible, key=lambda span: (span.receipt_mtime_ns is not None, -(span.receipt_mtime_ns or 0),
                                                    str(span.path))):
        if span.receipt_mtime_ns is not None:
            if span.kind in selected and not args.catch_up and not (
                Path(config["stage_root"]) / span.plan / ".retirement.json"
            ).exists():
                continue
            selected.add(span.kind)
        guard.quiet()
        results.append(close_one(args, config, span))
    return {"spans": results, "air_fallback": AIR_FALLBACK}


def reclaim(args, config, guard):
    path = args.span_dir
    if path.is_relative_to(args.campaign_root) and len(path.relative_to(args.campaign_root).parts) == 2:
        kind = "campaign"
    else:
        kind = "partc"
        so.check_close_source(path, args.work_root)
    if path.resolve() != path or os.path.lexists(path) or os.path.lexists(so.retirement_path(path)):
        raise so.refused("RAW_RETAINED", "reclaim needs an already retired OUT")
    plan = span_plan(kind, path)
    stage = Path(config["stage_root"]) / plan
    with so._directory_no_links(stage) as fd:
        # The marker names the span, and the stage binds it to its original absolute OUT.
        source = json.loads(so._read_in(fd, so.SOURCE_RECORD))
    if source != {"source": str(path)}:
        raise so.refused("STAGE_CONFLICT", "the stage belongs to another OUT")
    guard.quiet()
    return {"spans": [close_one(args, config, Span(kind, path, plan, None), ssd_receipt=args.ssd_receipt)]}


def run(args):
    outside_receipt_roots(args, {"config": args.config, "desk fence": args.fence})
    guard = Guard(args)
    with guard.lock():
        config = load_config(args)
        if args.command == "after-check":
            result = checked_close(args, config, guard, scan_spans(args, guard.deadline))
        else:
            result = reclaim(args, config, guard)
        guard.quiet()
        pending = so.pending_transfers(config)
        if not pending["clear"]:
            raise so.unverified("ICLOUD_PENDING", "pending or unknown CloudDocs state")
        guard.deadline.remaining()
    return dict(result, status="CLOSE_OK", pending=pending, holds_next_arm=False)


def parser():
    top = argparse.ArgumentParser(description=__doc__)
    commands = top.add_subparsers(dest="command", required=True)
    after = commands.add_parser("after-check", help="verify Check OUT, preserve GAP and rotate older outputs")
    after.add_argument("--catch-up", action="store_true", help="also process all older eligible outputs")
    cleanup = commands.add_parser("reclaim", help="later SSD-backed eviction of a retired OUT")
    cleanup.add_argument("--ssd-receipt", type=Path, required=True)
    for command in (after, cleanup):
        command.add_argument("--config", type=Path, required=True)
        command.add_argument("--span-dir", type=Path, required=True, help="absolute OUT from the Check")
        command.add_argument("--deadline-epoch", type=float, required=True)
        command.add_argument("--campaign-root", type=Path, default=CAMPAIGN_ROOT)
        command.add_argument("--work-root", type=Path, default=WORK_ROOT)
        command.add_argument("--fence", type=Path, default=FENCE)
        command.add_argument("--_worker", action="store_true", help=argparse.SUPPRESS)
    return top


def report(status, code, **details):
    print(json.dumps({"status": status, "holds_next_arm": code != 0, **details}, sort_keys=True), flush=True)
    return code


def worker(args):
    os.umask(0o077)
    try:
        result = run(args)
    except so.OffloadError as error:
        return report(error.code, so.EXIT[error.exit_kind])
    except Exception as error:
        # Report a fixed status and exception type without exposing payloads or provider output.
        return report("CLOSE_INTERNAL", so.EXIT["internal"], error=type(error).__name__)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    top = parser()
    args = top.parse_args(argv)
    left = args.deadline_epoch - time.time()
    if not so.number(left) or left > so.MAX_DEADLINE_AHEAD_S:
        top.error("deadline must be a finite epoch at most 24 hours ahead")
    if not all(path.is_absolute() and ".." not in path.parts
               for path in (args.span_dir, args.campaign_root, args.work_root, args.fence)):
        top.error("OUT, receipt roots and fence must be absolute paths without parent traversal")
    if left <= 0:
        return report("DEADLINE", so.EXIT["unverified"])
    if args._worker:
        return worker(args)
    script = Path(__file__).resolve().parents[1] / "scripts/close_offload.py"
    end = time.monotonic() + left
    child = None
    interrupted = False

    def interrupt(_signum, _frame):
        nonlocal interrupted
        interrupted = True
        if child is not None:
            raise KeyboardInterrupt

    previous = {sig: signal.signal(sig, interrupt) for sig in (signal.SIGINT, signal.SIGHUP, signal.SIGTERM)}
    try:
        child = subprocess.Popen([sys.executable, "-B", str(script), *argv, "--_worker"], start_new_session=True,
                                 stdout=subprocess.PIPE, text=True)
        if interrupted:
            raise KeyboardInterrupt
        output, _ = child.communicate(timeout=max(0, end - time.monotonic()))
    except subprocess.TimeoutExpired:
        return report("DEADLINE", so.EXIT["unverified"])
    except KeyboardInterrupt:
        return report("TERMINATED", so.EXIT["unverified"])
    except OSError:
        return report("CLOSE_SUPERVISOR", so.EXIT["internal"])
    finally:
        for sig in previous:
            signal.signal(sig, signal.SIG_IGN)
        if child is not None:
            # Clear the whole group even when a provider child outlived a normally exiting worker.
            with contextlib.suppress(ProcessLookupError):
                os.killpg(child.pid, signal.SIGKILL)
            child.wait()
            child.stdout.close()
        for sig, handler in previous.items():
            signal.signal(sig, handler)
    if time.monotonic() >= end or time.time() >= args.deadline_epoch:
        return report("DEADLINE", so.EXIT["unverified"])
    if child.returncode < 0 or not output:
        return report("CLOSE_WORKER_LOST", so.EXIT["unverified"])
    print(output, end="", flush=True)
    return child.returncode
