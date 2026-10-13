#!/usr/bin/env python3
"""Issue D-165 close-out files from finalized custody; release structure only."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import sys
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise import analysis_manifest_v3, dominance_closeout  # noqa: E402
from joulewise.authentication_io import read_authentication_input_nofollow  # noqa: E402
from joulewise.b5_analysis import steps  # noqa: E402
from scripts.build_d165_dominance_closeout import build_d165_dominance_closeout  # noqa: E402


STEP = "6"
RATIO_LABEL = "point diagnostic; no interval"
RATIO_TABLE_SCHEMA = "joulewise.b5_d165_ratio_table.v1"
DRIVER_REFUSAL_CODES = frozenset({
    "d165_closeout_driver_manifest_unreadable",
    "d165_closeout_driver_manifest_not_finalized",
    "d165_closeout_driver_manifest_invalid",
    "d165_closeout_driver_attachment_unreadable",
    "d165_closeout_driver_paper_sources_invalid",
    "d165_closeout_driver_output_conflict",
})
OUTCOME_CLASS_CODES = frozenset({"dominance_ratio_zero_denominator"})
STRUCTURAL_BUILDER_CODES = frozenset({
    "cell_not_common_mode",
    "closeout_input_malformed",
    "closeout_input_malformed: replay.block_ids",
    "closeout_input_malformed: closeout.comparative_common_mode_ratios",
    "closeout_input_malformed: closeout.independent_ratios",
    "closeout_input_malformed: source.census_or_block_membership",
    "common_mode_replay_block_count_invalid",
    "finalized_manifest_id_mismatch",
    "floor_artifact_source_hash_mismatch",
    "floor_cell_unresolved",
    "floor_member_census_mismatch",
    "manifest_lacks_replay_sidecar",
    "replay_sidecar_digest_mismatch",
    "replay_sidecar_identity_mismatch",
})
TOOLING_REFUSAL_CODES = DRIVER_REFUSAL_CODES | STRUCTURAL_BUILDER_CODES


class CloseoutDriverRefusal(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


@dataclass(frozen=True)
class CloseoutSources:
    custody_root: Path
    manifest_path: Path
    manifest_id: str
    manifest_relative_path: str
    floor_relative_path: str
    sidecar_relative_path: str
    manifest_bytes: bytes
    floor_bytes: bytes
    sidecar_bytes: bytes


def _read_attachment(root: Path, record: object) -> tuple[str, bytes]:
    try:
        if not isinstance(record, dict):
            raise ValueError
        relative = record["path"]
        if (not isinstance(relative, str) or not relative
                or Path(relative).is_absolute()
                or any(part in {"", ".", ".."} for part in relative.split("/"))):
            raise ValueError
        raw = read_authentication_input_nofollow(
            root, relative, grammar="json", label="D-165 attachment"
        )
    except (KeyError, OSError, RuntimeError, TypeError, ValueError):
        raise CloseoutDriverRefusal("d165_closeout_driver_attachment_unreadable") from None
    return relative, raw


def _check_attachment_digest(raw: bytes, record: dict, code: str) -> None:
    if hashlib.sha256(raw).hexdigest() != record.get("sha256"):
        raise CloseoutDriverRefusal(code)


def resolve_closeout_sources(finalized_manifest_path, custody_root) -> CloseoutSources:
    """Check a, b, c's location/id, d/e, then c's full custody replay."""
    manifest_path = Path(finalized_manifest_path).absolute()
    try:
        manifest_bytes = read_authentication_input_nofollow(
            manifest_path.parent, manifest_path.name, grammar="json", label="D-165 manifest"
        )
        manifest = analysis_manifest_v3._strict_json_bytes(manifest_bytes, "D-165 manifest")
    except (OSError, RuntimeError, TypeError, ValueError, UnicodeError,
            analysis_manifest_v3.AnalysisManifestFinalizationError):
        raise CloseoutDriverRefusal("d165_closeout_driver_manifest_unreadable") from None
    if (manifest.get("schema_version") != dominance_closeout.FINALIZED_MANIFEST_SCHEMA_VERSION
            or manifest.get("freeze_status") != "finalized"):
        raise CloseoutDriverRefusal("d165_closeout_driver_manifest_not_finalized")
    try:
        root = Path(custody_root).absolute().resolve(strict=True)
        manifest_path, manifest_relative = analysis_manifest_v3._path_under_root(
            manifest_path, Path(custody_root), "D-165 manifest"
        )
        manifest_id = manifest.get("manifest_id")
        if not isinstance(manifest_id, str) or re.fullmatch(r"[A-Za-z0-9._-]+", manifest_id) is None:
            raise ValueError
    except (OSError, RuntimeError, TypeError, ValueError, analysis_manifest_v3.AnalysisManifestFinalizationError):
        raise CloseoutDriverRefusal("d165_closeout_driver_manifest_invalid") from None
    evidence = manifest.get("evidence")
    if not isinstance(evidence, dict):
        raise CloseoutDriverRefusal("d165_closeout_driver_attachment_unreadable")
    floor_record = evidence.get("aggregate_floor_artifact")
    sidecar_record = evidence.get("dominance_replay_sidecar")
    floor_relative, floor_bytes = _read_attachment(root, floor_record)
    sidecar_relative, sidecar_bytes = _read_attachment(root, sidecar_record)
    _check_attachment_digest(floor_bytes, floor_record, "floor_artifact_source_hash_mismatch")
    _check_attachment_digest(sidecar_bytes, sidecar_record, "replay_sidecar_digest_mismatch")
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        invalid = analysis_manifest_v3.validate_finalized_analysis_manifest_v3(
            manifest, manifest_path=manifest_path, custody_root=root
        )
    if invalid:
        raise CloseoutDriverRefusal("d165_closeout_driver_manifest_invalid")
    return CloseoutSources(root, manifest_path, manifest_id, manifest_relative,
                           floor_relative, sidecar_relative, manifest_bytes, floor_bytes, sidecar_bytes)


def default_output_path(sources) -> Path:
    return sources.custody_root / f"d165-closeout-{sources.manifest_id}.json"


def build_ratio_table(closeout, floor_artifact, *, closeout_sha256, floor_artifact_sha256) -> dict:
    cells, errors = dominance_closeout._floor_cell_map(floor_artifact)
    if errors:
        raise CloseoutDriverRefusal("closeout_input_malformed")
    rows = []
    groups = (
        (closeout["independent_ratios"], "attribution_dominance_ratio.v1",
         "corner_widened_unguarded_floor_j"),
        (closeout["comparative_common_mode_ratios"], "attribution_dominance_ratio_common_mode.v1",
         "common_mode_corner_widened_unguarded_floor_j"),
    )
    for records, ratio_id, numerator_field in groups:
        for record in records:
            component = record.get("component", "comparative")
            n_field = "absolute.n" if component == "absolute" else "comparative.n_blocks"
            try:
                cell = cells[record["cell_id"]]
                n = cell[component]["n" if component == "absolute" else "n_blocks"]
            except (KeyError, TypeError):
                raise CloseoutDriverRefusal("closeout_input_malformed") from None
            if type(n) is not int or n < 1:
                raise CloseoutDriverRefusal("closeout_input_malformed")
            rows.append({
                "ratio_id": ratio_id, "cell_id": record["cell_id"], "component": component,
                "numerator_field": numerator_field, "numerator_j": record[numerator_field],
                "denominator_field": "point_unguarded_floor_j",
                "denominator_j": record["point_unguarded_floor_j"],
                "n": n, "n_field": n_field, "status": record["status"], "ratio": record["ratio"],
                "label": RATIO_LABEL,
            })
    return {"schema_version": RATIO_TABLE_SCHEMA, "closeout_sha256": closeout_sha256,
            "floor_artifact_sha256": floor_artifact_sha256, "ratios": rows}


def _file_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True)
            + "\n").encode("utf-8")


def _step_record(exit_status: int, code: str | None, outputs=()) -> dict:
    return steps.step_record(
        STEP, exit_status=exit_status, refusal_code=code,
        classes={"tooling": TOOLING_REFUSAL_CODES, "outcome": OUTCOME_CLASS_CODES},
        schema_valid=True if outputs else None, outputs=outputs,
    ).as_dict()


def _step_bytes(record: dict) -> bytes:
    return (json.dumps(record, ensure_ascii=False, allow_nan=False, sort_keys=True) + "\n").encode("utf-8")


def _replace_step(output: Path, record: dict) -> None:
    path = output.with_suffix(".step.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(_step_bytes(record))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _preflight_outputs(files: tuple[tuple[Path, bytes], ...]) -> None:
    for path, raw in files:
        if path.is_symlink() or (path.exists() and (not path.is_file() or path.read_bytes() != raw)):
            raise CloseoutDriverRefusal("d165_closeout_driver_output_conflict")


def _write_outputs(files: tuple[tuple[Path, bytes], ...]) -> tuple:
    """Preflight the whole pair, then link staged bytes; roll back our new links on failure."""
    _preflight_outputs(files)
    staged = []
    created = []
    try:
        for path, raw in files:
            path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("wb", dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
                temporary = Path(handle.name)
                staged.append((path, temporary, raw))
                handle.write(raw)
                handle.flush()
                os.fsync(handle.fileno())
        for path, temporary, raw in staged:
            try:
                os.link(temporary, path)
                created.append((path, temporary))
            except FileExistsError:
                _preflight_outputs(((path, raw),))
        for parent in {path.parent for path, _ in files}:
            descriptor = os.open(parent, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        return tuple((path, temporary.stat().st_dev, temporary.stat().st_ino)
                     for path, temporary in created)
    except BaseException:
        for path, temporary in reversed(created):
            if not path.is_symlink() and path.exists() and path.samefile(temporary):
                path.unlink()
        raise
    finally:
        for _, temporary, _ in staged:
            temporary.unlink(missing_ok=True)


def _rollback_created_outputs(created) -> None:
    """Remove only our new regular files, never a previous or replaced output."""
    for path, device, inode in reversed(created):
        try:
            current = path.lstat()
        except FileNotFoundError:
            continue
        if not path.is_symlink() and (current.st_dev, current.st_ino) == (device, inode):
            path.unlink()


def _exit_for(code: str | None) -> int:
    if code is None:
        return 0
    if code in OUTCOME_CLASS_CODES:
        return 3
    return 2


def run_closeout(sources, *, output: Path) -> int:
    output = Path(output)
    code = None
    outputs = []
    created_outputs = ()
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        try:
            try:
                closeout = build_d165_dominance_closeout(
                    sources.manifest_bytes, sources.floor_bytes, sources.sidecar_bytes
                )
            except (ValueError, TypeError) as exc:
                raise CloseoutDriverRefusal(dominance_closeout._closed_refusal_code(str(exc))) from None
            code = closeout["refusal_reason"]
            exit_status = _exit_for(code)
            if exit_status in {0, 3}:
                if dominance_closeout.validate_d165_paper_sources(
                    closeout=closeout, finalized_manifest_bytes=sources.manifest_bytes,
                    finalized_manifest_path=sources.manifest_path, custody_root=sources.custody_root,
                    floor_artifact_bytes=sources.floor_bytes, replay_sidecar_bytes=sources.sidecar_bytes,
                ) != ():
                    raise CloseoutDriverRefusal("d165_closeout_driver_paper_sources_invalid")
                raw = _file_bytes(closeout)
                table = build_ratio_table(
                    closeout, json.loads(sources.floor_bytes), closeout_sha256=hashlib.sha256(raw).hexdigest(),
                    floor_artifact_sha256=hashlib.sha256(sources.floor_bytes).hexdigest(),
                )
                files = ((output, raw), (output.with_suffix(".ratio-table.json"), _file_bytes(table)))
                created_outputs = _write_outputs(files)
                outputs = [{"name": path.name, "sha256": hashlib.sha256(value).hexdigest()}
                           for path, value in files]
        except CloseoutDriverRefusal as exc:
            code, exit_status = exc.code, _exit_for(exc.code)
        except Exception:
            code, exit_status = "unclassified", 2
        try:
            _replace_step(output, _step_record(exit_status, code, outputs))
        except Exception:
            _rollback_created_outputs(created_outputs)
            raise
    return exit_status


class _QuietParser(argparse.ArgumentParser):
    def error(self, message):
        # A usage error is still exit 2, but its message is not an unrestricted record.
        raise ValueError


def _parser() -> argparse.ArgumentParser:
    parser = _QuietParser(description=__doc__)
    parser.add_argument("--finalized-manifest", required=True, type=Path)
    parser.add_argument("--custody-root", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def _output_under_root(output: Path, root: Path) -> bool:
    try:
        # Resolve parents only: an occupied final symlink is an output conflict.
        output.absolute().parent.resolve().relative_to(root.absolute().resolve())
        return output.name not in {"", ".", ".."}
    except (OSError, RuntimeError, ValueError):
        return False


def main(argv=None) -> int:
    output = None
    record = None
    record_needs_write = True
    with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
        try:
            parser = _parser()
            args = parser.parse_args(argv)
            if args.output is not None:
                if not _output_under_root(args.output, args.custody_root):
                    parser.error("output must be under custody root")
                output = args.output
            sources = resolve_closeout_sources(args.finalized_manifest, args.custody_root)
            output = output if output is not None else default_output_path(sources)
            exit_status = run_closeout(sources, output=output)
            record = json.loads(output.with_suffix(".step.json").read_bytes())
            record_needs_write = False
        except CloseoutDriverRefusal as exc:
            exit_status = _exit_for(exc.code)
            record = _step_record(exit_status, exc.code)
        except (Exception, SystemExit):
            exit_status = 2
            record = _step_record(exit_status, "unclassified")
        if record is not None and output is not None and record_needs_write:
            try:
                _replace_step(output, record)
            except Exception:
                exit_status, record = 2, _step_record(2, "unclassified")
    sys.stdout.write(_step_bytes(record).decode("utf-8"))
    return exit_status


if __name__ == "__main__":
    raise SystemExit(main())
