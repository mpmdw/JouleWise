#!/usr/bin/env python3
"""Run the record-only flag collectors for the desk or the arm.

Writes every flag to ``<custody>/flags/<stage>.jsonl`` (append-only, fsync per
line, deduplicated) and one run record, with any ``collector_errors``, to
``<custody>/flags/collector_runs.jsonl``. Each collector runs in its own
subprocess with a timeout. The exit status is 0 whatever the collectors find
or however they fail: this program records, it never refuses. Only a usage
error (exit 2) is reported as a failure, and the driver ignores even that.

Example (desk, before scheduling ALPHA-1)::

    python scripts/collect_window_flags.py --stage desk --custody <custody> \\
        --repo <measurement checkout> --pack configs/campaigns/d117_floor_qwen3-1p7b_v5 \\
        --plan-id <plan_id> --attempt 1 --h-claim <sha> \\
        --sealed-inventory configs/campaigns/v5_claim_25g83/sealed_inventory.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.flags.catalog import CatalogError, load_catalog  # noqa: E402
from joulewise.flags.collect import COLLECTORS, run_collectors  # noqa: E402
from joulewise.flags.sink import FlagSink  # noqa: E402

DEFAULT_COLLECTORS = ("pack_identity", "checkout_identity", "executed_code", "model_identity", "ledger_readiness")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stage", choices=("desk", "arm"), required=True)
    parser.add_argument("--custody", type=Path, required=True, help="custody root; flags go to <custody>/flags/")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT, help="measurement checkout")
    parser.add_argument("--pack", type=Path, help="pack root (directory holding plan_tree.json)")
    parser.add_argument("--plan-id")
    parser.add_argument("--attempt")
    parser.add_argument("--h-claim", help="the sealed claim commit")
    parser.add_argument("--pin-only-path", action="append", default=None,
                        help="a path whose change keeps H_claim's code identity (repeatable)")
    parser.add_argument("--expected-pack-tree-sha256")
    parser.add_argument("--sealed-inventory", type=Path)
    parser.add_argument("--chain", type=Path, help="the chain file the driver will launch")
    parser.add_argument("--chain-sidecar", type=Path)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--head-pin", type=Path)
    parser.add_argument("--calibration-plan", type=Path)
    parser.add_argument("--session-id")
    parser.add_argument("--expected-model-artifact", action="append", default=[],
                        metavar="UNIT=SHA256", help="model artifact pin for an identity unit")
    parser.add_argument("--expected-runtime-versions-sha256",
                        help="sealed digest of the measurement interpreter's runtime package versions")
    parser.add_argument("--runtime-python", type=Path,
                        help="measurement interpreter (default <repo>/.venv/bin/python)")
    parser.add_argument("--verify-frozen-projection", action="store_true",
                        help="also run identity_pins.verify_frozen_projection when frozen (loads the runtime)")
    parser.add_argument("--catalog", type=Path, help="sealed flag catalog; its sha256 is stamped on each flag")
    parser.add_argument("--collector", action="append", choices=sorted(COLLECTORS), default=None)
    parser.add_argument("--timeout-s", type=float, help="override every collector's timeout")
    return parser


def build_specs(args: argparse.Namespace, catalog_sha256: str | None) -> list[tuple[str, dict]]:
    common = {
        "plan_id": args.plan_id,
        "attempt": args.attempt,
        "catalog_sha256": catalog_sha256,
        "repo_root": str(args.repo),
        "custody_root": str(args.custody),
    }
    expected_models = {}
    for item in args.expected_model_artifact:
        unit, _, digest = item.partition("=")
        expected_models[unit] = digest
    params = {
        "pack_identity": {"pack_root": str(args.pack) if args.pack else None,
                          "expected_pack_tree_sha256": args.expected_pack_tree_sha256},
        "checkout_identity": {"h_claim": args.h_claim,
                              "pin_only_paths": args.pin_only_path},
        "executed_code": {"pack_root": str(args.pack) if args.pack else None,
                          "sealed_inventory": str(args.sealed_inventory) if args.sealed_inventory else None,
                          "chain_path": str(args.chain) if args.chain else None,
                          "chain_sidecar": str(args.chain_sidecar) if args.chain_sidecar else None},
        "model_identity": {"pack_root": str(args.pack) if args.pack else None,
                           "expected_model_artifact_sha256": expected_models,
                           "expected_runtime_versions_sha256": args.expected_runtime_versions_sha256,
                           "runtime_python": str(args.runtime_python) if args.runtime_python else None,
                           "verify_frozen_projection": bool(args.verify_frozen_projection),
                           "bracket_session_id": args.session_id},
        "ledger_readiness": {"ledger_path": str(args.ledger) if args.ledger else None,
                             "head_pin_path": str(args.head_pin) if args.head_pin else None,
                             "calibration_plan": str(args.calibration_plan) if args.calibration_plan else None,
                             "session_id": args.session_id},
    }
    # The identity collectors always run: one whose input is missing records
    # an "*.identity_unmeasured" flag instead of being skipped silently.
    names = args.collector or [
        name for name in DEFAULT_COLLECTORS
        if not (name == "ledger_readiness" and (args.calibration_plan is None or args.session_id is None))
    ]
    return [(name, {**common, **params[name]}) for name in names]


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    catalog_sha256 = None
    catalog_error = None
    if args.catalog is not None:
        try:
            catalog_sha256 = load_catalog(args.catalog).sha256
        except CatalogError as exc:
            catalog_error = str(exc)
    flags_dir = args.custody / "flags"
    sink = FlagSink(flags_dir / f"{args.stage}.jsonl")
    timeouts = None
    specs = build_specs(args, catalog_sha256)
    if args.timeout_s is not None:
        timeouts = {name: args.timeout_s for name, _ in specs}
    outcomes = run_collectors(
        specs, stage=args.stage, sink=sink, runs_log=flags_dir / "collector_runs.jsonl", timeout_s=timeouts
    )
    summary = {
        "stage": args.stage,
        "flags_file": str(sink.path),
        "catalog_error": catalog_error,
        "collectors": {o.name: {"status": o.status, "flags": len(o.flags), "error": o.error} for o in outcomes},
    }
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
