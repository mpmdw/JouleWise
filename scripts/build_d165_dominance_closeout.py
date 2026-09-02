#!/usr/bin/env python3
"""Build the D-165 ratio close-out from its three governed JSON sources."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any, NoReturn


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.dominance_closeout import (  # noqa: E402
    CLOSEOUT_SCHEMA_VERSION,
    CLOSEOUT_INPUT_MALFORMED,
    CLOSEOUT_INPUT_MALFORMED_SOURCE,
    FINALIZED_MANIFEST_SCHEMA_VERSION,
    FLOOR_ARTIFACT_SCHEMA_VERSION,
    REPLAY_SCHEMA_VERSION,
    _build_independent_record,
    _decode_json_object_bytes,
    _expected_closeout_common_record,
    _expected_global_fields,
    _floor_cell_map,
    _point_unguarded_floor_from_component,
    _refused_closeout_common_record,
    _sidecar_cell_map,
    _source_precondition_errors,
    canonical_json_sha256,
    validate_d165_closeout,
)


def _source_reference(
    source: Mapping[str, Any], *, identity_key: str, expected_schema: str
) -> dict[str, str]:
    identity = source.get(identity_key)
    if source.get("schema_version") != expected_schema:
        raise ValueError(f"{identity_key}: source schema mismatch")
    if not isinstance(identity, str) or not identity:
        raise ValueError(f"{identity_key}: source identity is missing")
    return {
        "schema_version": expected_schema,
        "identity": identity,
        "canonical_json_sha256": canonical_json_sha256(source),
    }


def build_d165_dominance_closeout(
    finalized_manifest_bytes: bytes,
    floor_artifact_bytes: bytes,
    replay_sidecar_bytes: bytes,
) -> dict[str, Any]:
    """Decode three exact source files and apply the registered A/B/stop rule."""

    finalized_manifest = _decode_json_object_bytes(
        finalized_manifest_bytes, label="finalized_manifest"
    )
    floor_artifact = _decode_json_object_bytes(
        floor_artifact_bytes, label="floor_artifact"
    )
    replay_sidecar = _decode_json_object_bytes(
        replay_sidecar_bytes, label="replay_sidecar"
    )

    try:
        source_errors = _source_precondition_errors(
            finalized_manifest,
            floor_artifact,
            replay_sidecar,
            floor_artifact_bytes=floor_artifact_bytes,
            replay_sidecar_bytes=replay_sidecar_bytes,
        )
    except TypeError:
        source_errors = [CLOSEOUT_INPUT_MALFORMED_SOURCE]

    def _stop(fallback: str) -> NoReturn:
        raise ValueError(source_errors[0] if source_errors else fallback)

    floor_cells, floor_errors = _floor_cell_map(floor_artifact)
    if floor_errors:
        _stop(CLOSEOUT_INPUT_MALFORMED)

    independent_ratios: list[dict[str, Any]] = []
    for cell_id, cell in floor_cells.items():
        for component, parent_key in (
            ("absolute", "max_abs_residual_j"),
            ("comparative", "max_abs_delta_j"),
        ):
            component_record = cell.get(component)
            if not isinstance(component_record, Mapping):
                _stop(
                    f"floor_artifact.cells[{cell_id!r}].{component}: missing component"
                )
            try:
                point = _point_unguarded_floor_from_component(
                    component_record,
                    parent_key=parent_key,
                )
            except ValueError as exc:
                _stop(str(exc))
            corner = component_record.get("corner_widened_unguarded_floor_j")
            if isinstance(corner, bool) or not isinstance(corner, (int, float)):
                _stop(
                    f"floor_artifact.cells[{cell_id!r}].{component}."
                    "corner_widened_unguarded_floor_j: invalid"
                )
            independent_ratios.append(
                {
                    "cell_id": cell_id,
                    "component": component,
                    **_build_independent_record(
                        point_unguarded_floor_j=point,
                        corner_widened_unguarded_floor_j=corner,
                    ),
                }
            )

    sidecar_cells = _sidecar_cell_map(replay_sidecar)
    common_mode_ratios: list[dict[str, Any]] = []
    for cell_id in floor_cells:
        sidecar_cell = sidecar_cells.get(cell_id)
        if sidecar_cell is None:
            common_mode_ratios.append(
                _refused_closeout_common_record(
                    cell_id, f"d165_replay_sidecar_cell_missing:{cell_id}"
                )
            )
            continue
        try:
            result = sidecar_cell["comparative"]["common_mode_replay"]["result"]
        except (KeyError, TypeError):
            common_mode_ratios.append(
                _refused_closeout_common_record(
                    cell_id, f"d165_replay_sidecar_result_missing:{cell_id}"
                )
            )
            continue
        if not isinstance(result, Mapping):
            common_mode_ratios.append(
                _refused_closeout_common_record(
                    cell_id, f"d165_replay_sidecar_result_invalid:{cell_id}"
                )
            )
            continue
        try:
            common_mode_ratios.append(
                _expected_closeout_common_record(cell_id=cell_id, result=result)
            )
        except KeyError:
            common_mode_ratios.append(
                _refused_closeout_common_record(
                    cell_id, f"d165_replay_sidecar_result_invalid:{cell_id}"
                )
            )

    global_fields = _expected_global_fields(
        independent_ratios,
        common_mode_ratios,
        source_errors,
    )
    try:
        source_references = {
            "finalized_manifest": _source_reference(
                finalized_manifest,
                identity_key="manifest_id",
                expected_schema=FINALIZED_MANIFEST_SCHEMA_VERSION,
            ),
            "floor_artifact": _source_reference(
                floor_artifact,
                identity_key="artifact_id",
                expected_schema=FLOOR_ARTIFACT_SCHEMA_VERSION,
            ),
            "replay_sidecar": _source_reference(
                replay_sidecar,
                identity_key="sidecar_id",
                expected_schema=REPLAY_SCHEMA_VERSION,
            ),
        }
    except ValueError as exc:
        _stop(str(exc))
    closeout = {
        "schema_version": CLOSEOUT_SCHEMA_VERSION,
        "sources": source_references,
        "finalized_manifest_sha256": hashlib.sha256(
            finalized_manifest_bytes
        ).hexdigest(),
        "replay_sidecar_sha256": hashlib.sha256(replay_sidecar_bytes).hexdigest(),
        "independent_ratios": independent_ratios,
        "comparative_common_mode_ratios": common_mode_ratios,
        **global_fields,
    }
    errors = validate_d165_closeout(
        closeout,
        finalized_manifest_bytes=finalized_manifest_bytes,
        floor_artifact_bytes=floor_artifact_bytes,
        replay_sidecar_bytes=replay_sidecar_bytes,
    )
    if errors:
        raise ValueError("built D-165 close-out is invalid: " + "; ".join(errors))
    return closeout


def _read_source_bytes(path: Path, label: str) -> bytes:
    try:
        return path.read_bytes()
    except OSError as exc:
        raise ValueError(f"{label} is unreadable: {exc}") from exc


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--finalized-manifest", required=True, type=Path)
    parser.add_argument("--floor-artifact", required=True, type=Path)
    parser.add_argument("--replay-sidecar", required=True, type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help="write the close-out here; stdout is used when omitted",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        finalized_manifest_bytes = _read_source_bytes(
            args.finalized_manifest, "finalized manifest"
        )
        floor_artifact_bytes = _read_source_bytes(
            args.floor_artifact, "floor artifact"
        )
        replay_sidecar_bytes = _read_source_bytes(
            args.replay_sidecar, "replay sidecar"
        )
        closeout = build_d165_dominance_closeout(
            finalized_manifest_bytes,
            floor_artifact_bytes,
            replay_sidecar_bytes,
        )
    except (TypeError, ValueError) as exc:
        print(f"d165_dominance_closeout_refused: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(
        closeout,
        ensure_ascii=False,
        allow_nan=False,
        indent=2,
        sort_keys=True,
    ) + "\n"
    if args.output is None:
        sys.stdout.write(rendered)
    else:
        try:
            with args.output.open("x", encoding="utf-8") as output_handle:
                output_handle.write(rendered)
        except FileExistsError:
            print(
                "d165_dominance_closeout_refused: output_already_exists",
                file=sys.stderr,
            )
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
