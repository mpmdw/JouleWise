#!/usr/bin/env python3
"""Exercise sealed bundles and receipt exact/replay/ratio compatibility."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.corpus_compat_receipt import (  # noqa: E402
    GATE_NAMES,
    _artifact_directory_paths,
    _bundle_paths,
    evaluate_bundle,
)

SCHEMA = "joulewise.wo003_sealed_bundle_compatibility.v1"
ABSENT_BOUNDARY = "retained_runs_root_absent"
EMPTY_FAILURE = "empty_corpus"


def _selected_gates(value: str) -> tuple[str, ...]:
    gates = tuple(part.strip() for part in value.split(",") if part.strip())
    unknown = sorted(set(gates) - set(GATE_NAMES))
    if not gates or unknown:
        rendered = ", ".join(unknown) if unknown else "none"
        raise argparse.ArgumentTypeError(f"unknown or empty compatibility gates: {rendered}")
    return gates


def _summary(bundles: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for gate_name in GATE_NAMES:
        eligible = sum(
            1 for bundle in bundles if bundle["gates"][gate_name]["eligible"]
        )
        result[gate_name] = {
            "eligible": eligible,
            "revoked": len(bundles) - eligible,
        }
    return result


def build_receipt(runs_root: Path, verify_gates: Sequence[str]) -> dict[str, Any]:
    root = Path(runs_root)
    common = {
        "schema": SCHEMA,
        "work_order": "WO-003",
        "corpus": {
            "logical_root": "runs",
            "bundle_count": 0,
            "incomplete_directory_count": 0,
        },
        "incomplete_directories": [],
        "verified_gates": list(verify_gates),
        "bundles": [],
        "summary": {name: {"eligible": 0, "revoked": 0} for name in GATE_NAMES},
        "boundary": None,
        "failure_reasons": [],
    }
    if not root.exists():
        return {
            **common,
            "result": "boundary",
            "boundary": {
                "name": ABSENT_BOUNDARY,
                "disposition": (
                    "No retained runs directory is mounted in this checkout; "
                    "the lead must rerun this read-only gate where the sealed "
                    "corpus is available."
                ),
            },
        }
    if not root.is_dir():
        return {**common, "result": "fail", "failure_reasons": ["runs_root_not_directory"]}

    artifact_paths = _artifact_directory_paths(root)
    paths = _bundle_paths(root)
    complete = set(paths)
    incomplete_directories = [
        path.relative_to(root).as_posix()
        for path in artifact_paths
        if path not in complete
    ]
    if not paths:
        return {
            **common,
            "result": "fail",
            "corpus": {
                "logical_root": "runs",
                "bundle_count": 0,
                "incomplete_directory_count": len(incomplete_directories),
            },
            "incomplete_directories": incomplete_directories,
            "failure_reasons": [EMPTY_FAILURE],
        }
    bundles = [evaluate_bundle(path, root) for path in paths]
    return {
        **common,
        "result": "pass",
        "corpus": {
            "logical_root": "runs",
            "bundle_count": len(bundles),
            "incomplete_directory_count": len(incomplete_directories),
        },
        "incomplete_directories": incomplete_directories,
        "bundles": bundles,
        "summary": _summary(bundles),
    }


def _absolute_path_strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value] if value.startswith("/") else []
    if isinstance(value, Mapping):
        result: list[str] = []
        for child in value.values():
            result.extend(_absolute_path_strings(child))
        return result
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        result = []
        for child in value:
            result.extend(_absolute_path_strings(child))
        return result
    return []


def verify_receipt(receipt: Mapping[str, Any]) -> None:
    if _absolute_path_strings(receipt):
        raise ValueError("receipt contains a machine-local absolute path")
    if receipt.get("result") == "boundary":
        boundary = receipt.get("boundary")
        if not isinstance(boundary, Mapping) or boundary.get("name") != ABSENT_BOUNDARY:
            raise ValueError("absent corpus boundary is missing or unnamed")
        return
    bundle_count = receipt.get("corpus", {}).get("bundle_count")
    if not isinstance(bundle_count, int) or isinstance(bundle_count, bool) or bundle_count <= 0:
        raise ValueError(EMPTY_FAILURE)
    incomplete_count = receipt.get("corpus", {}).get("incomplete_directory_count")
    incomplete = receipt.get("incomplete_directories")
    if (
        not isinstance(incomplete_count, int)
        or isinstance(incomplete_count, bool)
        or incomplete_count < 0
        or not isinstance(incomplete, list)
        or incomplete_count != len(incomplete)
        or not all(isinstance(path, str) and path for path in incomplete)
    ):
        raise ValueError("incomplete directory inventory is malformed")
    if receipt.get("result") != "pass":
        reasons = receipt.get("failure_reasons")
        raise ValueError(str(reasons[0] if isinstance(reasons, list) and reasons else "gate_failed"))
    selected = receipt.get("verified_gates")
    bundles = receipt.get("bundles")
    if not isinstance(selected, list) or not isinstance(bundles, list):
        raise ValueError("receipt gate inventory is malformed")
    for bundle in bundles:
        if not isinstance(bundle, Mapping):
            raise ValueError("receipt bundle row is not an object")
        gates = bundle.get("gates")
        if not isinstance(gates, Mapping):
            raise ValueError("receipt bundle gates are missing")
        for gate_name in selected:
            gate = gates.get(gate_name)
            if not isinstance(gate, Mapping) or not isinstance(gate.get("eligible"), bool):
                raise ValueError(f"bundle gate {gate_name} is malformed")
            reasons = gate.get("revocation_reasons")
            if not isinstance(reasons, list) or not all(
                isinstance(reason, str) and reason for reason in reasons
            ):
                raise ValueError(f"bundle gate {gate_name} has malformed reasons")
            if gate["eligible"] == bool(reasons):
                raise ValueError(f"bundle gate {gate_name} eligibility/reasons disagree")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--verify",
        type=_selected_gates,
        default=tuple(GATE_NAMES),
        metavar="GATE[,GATE...]",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        receipt = build_receipt(args.runs_root, args.verify)
        verify_receipt(receipt)
    except (OSError, ValueError) as exc:
        if "receipt" not in locals():
            receipt = {
                "schema": SCHEMA,
                "work_order": "WO-003",
                "result": "fail",
                "corpus": {
                    "logical_root": "runs",
                    "bundle_count": 0,
                    "incomplete_directory_count": 0,
                },
                "incomplete_directories": [],
                "verified_gates": list(args.verify),
                "bundles": [],
                "summary": {},
                "boundary": None,
                "failure_reasons": [type(exc).__name__],
            }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        reason = receipt.get("failure_reasons") or [str(exc)]
        print(f"FAIL {reason[0]}", file=sys.stderr)
        return 2

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    if receipt["result"] == "boundary":
        print(f"BOUNDARY {ABSENT_BOUNDARY}: retained corpus not mounted", file=sys.stderr)
    else:
        print(f"PASS sealed bundles exercised: {receipt['corpus']['bundle_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
