#!/usr/bin/env python3
"""Desk and CI pre-check of a block-5 HAZARD_PACK chain, before any window spends its slot.

Gate-prune core prune, row A21 (lane NONCORE, N6).  Several refusals inside the
chain's tools fire on committed bytes and argv alone, so they decide the same
way at the desk as in the window.  In the window they cost the slot (the arm and
its dwell) or a whole collection stage.  This script runs those decisions on
the rendered chain's own argv, without running any stage:

* ``frozen_protocol``: the fiducial writer's frozen-protocol self-check
  (``validate_powermetrics_fiducial.verify_frozen_protocol``, writer R7);
* ``argv_parses``: every in-chain stage's argv parses under its tool's own
  parser (reservation, fiducial writer R9, ``run_campaign``);
* ``capture_dir_absent``: the pre and post capture directories do not exist
  yet (the writer creates each with ``exist_ok=False``, writer R8; only
  meaningful with ``--plan``, whose bindings are real);
* per collection stage, as ``run_campaign`` decides them before member 1:
  ``config_selection`` (the analysis manifest and order manifest resolve),
  ``lineage_tags_all_or_none`` (``authenticate_campaign_writer_preflight``),
  ``doctor_config_gate`` (``config_warning_gate``) and ``duplicate_run_id``;
* ``acceptance_code_identity``: the issued acceptance's
  ``prospective_rederivation`` digests equal this checkout's protocol and
  estimator code (core-prune A15);
* ``pack_root_location``: the pack root is ``<repo>/configs/campaigns/<pack>``
  (core-prune A5: the controller derives the repository from that shape);
* ``desk_identity_power_policy``: the desk identity-epoch JSON's
  ``power_policy`` equals the plan tree's ``--power-policy`` literal (with
  ``--plan``, or ``--identity-epoch-json``);
* ``desk_identity_machine`` (warning only): its ``os_build`` and
  ``hardware_model`` equal live ``sysctl`` (skipped with ``--no-live-identity``).

Input: a window plan (``--plan <custody>/night_plan.json``, the bindings the
chain was rendered with), or a pack root (``--pack-root``) with synthetic
bindings under a path that does not exist.  Code-identity checks evaluate the
checkout this script runs from; a plan whose measurement root is another
checkout gets a warning.

Output: one JSON report on stdout.  Exit 0 when no check found an error
(warnings do not count), 1 on any error finding, 2 when the input cannot be
read.  Never imports ``mlx``, never writes a file, never runs a stage.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

sys.dont_write_bytecode = True  # never writes, not even bytecode caches
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.b5 import chain as b5_chain  # noqa: E402

REPORT_SCHEMA = "joulewise.b5_chain_static_check.v1"
ERROR, WARNING = "error", "warning"
SYNTHETIC_PREFIX = Path("/nonexistent/joulewise-b5-chain-check")
SYSCTL = "/usr/sbin/sysctl"
SYSCTL_TIMEOUT_S = 5
TOOL_BY_KIND = {"bracket_reservation": "bracket_reserver", "calibration_capture": "fiducial_capture",
                "campaign_collection": "campaign_runner", "bound_derivation": "campaign_runner"}


class InputError(ValueError):
    """The plan or pack cannot be read; nothing was checked."""


class _Parsed(Exception):
    def __init__(self, namespace: argparse.Namespace) -> None:
        super().__init__("parsed")
        self.namespace = namespace


def _read_json(path: Path) -> Any:
    try:
        return json.loads(Path(path).read_bytes())
    except (OSError, ValueError) as exc:
        raise InputError(f"{path}: {type(exc).__name__}: {exc}") from exc


def synthetic_bindings(measurement_root: Path, pack_root: Path) -> dict[str, str]:
    """Bindings of the plan writer's shape under a path that does not exist (pack mode)."""

    base = SYNTHETIC_PREFIX / pack_root.name
    claim, bound = base / "runs_claim", base / "runs_bound"
    return {
        "repo_root": str(measurement_root),
        "ledger_path": str(measurement_root / "runs/calibration_observation_ledger.jsonl"),
        "claim_runs_root": str(claim), "bound_runs_root": str(bound),
        "operator_log_root": str(base / "custody/operator-logs"),
        "pre_calibration_dir": str(claim / "instrument_validation/static-check-pre"),
        "post_calibration_dir": str(claim / "instrument_validation/static-check-post"),
        "claim_backup_destination": str(base / "backup_claim"),
        "bound_backup_destination": str(base / "backup_bound"),
        "bracket_session_id": "static-check-session",
        "pre_attempt_id": "static-check-pre", "post_attempt_id": "static-check-post",
        "identity_epoch_json": str(base / "identity_epoch.json"),
        "t1_bindings_json": str(base / "t1_bindings.json"),
    }


def _parse_quietly(function: Callable[[], Any]) -> tuple[Any, str | None]:
    """Run an argparse parse; (namespace, None) or (None, the parser's message)."""

    stderr = io.StringIO()
    try:
        with contextlib.redirect_stderr(stderr), contextlib.redirect_stdout(io.StringIO()):
            return function(), None
    except _Parsed as parsed:
        return parsed.namespace, None
    except SystemExit as exc:
        lines = [line.strip() for line in stderr.getvalue().splitlines() if line.strip()]
        return None, lines[-1][:300] if lines else f"parser exited {exc.code}"
    except Exception as exc:  # noqa: BLE001 - a parse that raises is a finding, not a crash
        return None, f"{type(exc).__name__}: {exc}"[:300]


def _parse_fiducial(arguments: Sequence[str]) -> tuple[Any, str | None]:
    """The fiducial writer builds its parser inside ``main``; stop ``main`` right after parsing."""

    from scripts import validate_powermetrics_fiducial as writer

    original = argparse.ArgumentParser.parse_args

    def capture(self, args=None, namespace=None):
        raise _Parsed(original(self, args, namespace))

    argparse.ArgumentParser.parse_args = capture
    try:
        return _parse_quietly(lambda: writer.main(list(arguments)))
    finally:
        argparse.ArgumentParser.parse_args = original


def parse_stage_argv(stage: b5_chain.Stage, argv: Sequence[str]) -> tuple[Any, str | None]:
    arguments = list(argv[2:])  # the interpreter and the tool's program
    tool = TOOL_BY_KIND[stage.kind]
    if tool == "bracket_reserver":
        from scripts import reserve_calibration_window_bracket as reserver
        return _parse_quietly(lambda: reserver._parser().parse_args(arguments))
    if tool == "fiducial_capture":
        return _parse_fiducial(arguments)
    from scripts import run_campaign
    return _parse_quietly(lambda: run_campaign.parse_args(arguments))


def collection_findings(stage: b5_chain.Stage, args: argparse.Namespace) -> list[dict[str, Any]]:
    """What ``run_campaign.run_campaign`` decides on committed bytes before member 1."""

    from scripts import run_campaign as rc

    findings: list[dict[str, Any]] = []

    def finding(check: str, detail: str) -> None:
        findings.append({"check": check, "stage_id": stage.stage_id, "severity": ERROR, "detail": detail[:500]})

    config_dir = Path(args.config_dir)
    quiet = contextlib.redirect_stdout(io.StringIO())
    try:
        with quiet, contextlib.redirect_stderr(io.StringIO()):
            analysis_manifest = rc.load_analysis_manifest(config_dir)
            rc.resolve_prospective_analysis_manifest_v3(config_dir)
            if analysis_manifest is not None and analysis_manifest.is_axi_v2:
                order_entries: list[Any] = []
                configs = rc._axi_entry_config_paths(analysis_manifest)
            else:
                order_entries, _warning = rc.load_order_entries(config_dir)
                configs = rc.apply_order_manifest(rc.discover_configs(config_dir), order_entries)
    except Exception as exc:  # noqa: BLE001
        finding("config_selection", f"{type(exc).__name__}: {exc}")
        return findings
    if not configs:
        finding("config_selection", f"{config_dir} selects no configs")
        return findings
    markers = [rc._config_requires_launch_lineage(path) for path in configs]
    if any(markers) and not all(markers):
        finding("lineage_tags_all_or_none",
                f"{sum(markers)} of {len(markers)} configs carry the launch-lineage tag")
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            gate = rc.config_warning_gate(configs, acknowledge=args.ack_config_warnings, mode="campaign")
    except Exception as exc:  # noqa: BLE001
        finding("doctor_config_gate", f"{type(exc).__name__}: {exc}")
    else:
        errors = gate.get("details", {}).get("errors") or []
        if errors:
            finding("doctor_config_gate", "; ".join(f"{error.get('config')}: {error.get('message')}"
                                                    for error in errors[:4]))
        elif gate.get("status") == "fail":
            finding("doctor_config_gate", "config warnings are not acknowledged")
    try:
        items = rc.read_config_infos(configs, rc.order_entry_by_config(order_entries))
    except Exception as exc:  # noqa: BLE001
        finding("config_selection", f"{type(exc).__name__}: {exc}")
        return findings
    config_errors = [item for item in items if isinstance(item, rc.ConfigError)]
    for item in config_errors[:4]:
        finding("config_selection", item.message)
    if not config_errors:
        duplicate = rc.duplicate_run_id_error(items)
        if duplicate is not None:
            finding("duplicate_run_id", duplicate)
    return findings


def _sysctl(name: str) -> str | None:
    try:
        result = subprocess.run([SYSCTL, "-n", name], capture_output=True, text=True, check=False,
                                timeout=SYSCTL_TIMEOUT_S)
    except (OSError, subprocess.SubprocessError):
        return None
    value = result.stdout.strip()
    return value if result.returncode == 0 and value else None


def check(tree: Mapping[str, Any], *, pack_root: Path, measurement_root: Path, bindings: Mapping[str, str],
          plan_mode: bool, identity_epoch_path: Path | None = None, live_identity: bool = True,
          sysctl: Callable[[str], str | None] | None = None) -> dict[str, Any]:
    """Every check over one rendered chain; the report (never raises on a finding)."""

    sysctl = sysctl if sysctl is not None else _sysctl
    from scripts import validate_powermetrics_fiducial as writer

    findings: list[dict[str, Any]] = []
    checks: list[str] = []

    def finding(check_name: str, detail: str, *, stage_id: str | None = None, severity: str = ERROR) -> None:
        findings.append({"check": check_name, "stage_id": stage_id, "severity": severity, "detail": detail[:500]})

    checks.append("pack_root_location")
    resolved_pack, resolved_repo = Path(os.path.abspath(pack_root)), Path(os.path.abspath(measurement_root))
    if not (resolved_pack.parent.name == "campaigns" and resolved_pack.parent.parent.name == "configs"
            and resolved_pack.parents[2] == resolved_repo):
        finding("pack_root_location", f"{resolved_pack} is not {resolved_repo}/configs/campaigns/<pack>")
    if resolved_repo != REPO_ROOT:
        finding("checkout", f"code identity was checked in {REPO_ROOT}, not the plan's {resolved_repo}",
                severity=WARNING)

    checks.append("frozen_protocol")
    try:
        if not writer.verify_frozen_protocol():
            finding("frozen_protocol", "the fiducial writer's frozen protocol does not verify (FROZEN_PROTOCOL_INVALID)")
    except Exception as exc:  # noqa: BLE001
        finding("frozen_protocol", f"{type(exc).__name__}: {exc}")

    checks.append("acceptance_code_identity")
    try:
        acceptance = writer.load_calibration_acceptance_bound(writer.DEFAULT_ACCEPTANCE_BOUND_PATH)
        prospective = (acceptance or {}).get("prospective_rederivation")
        if not isinstance(prospective, Mapping):
            finding("acceptance_code_identity", "the issued acceptance has no prospective_rederivation")
        else:
            executed = {"protocol_sha256": writer.protocol_sha256(writer.PROTOCOL_ID),
                        "estimator_code_sha256": writer._current_estimator_code_sha256()}
            differing = sorted(key for key, value in executed.items() if prospective.get(key) != value)
            if differing:
                finding("acceptance_code_identity",
                        f"acceptance_artifact_stale: {differing} differ from this checkout "
                        f"(recorded {[prospective.get(key) for key in differing]}, "
                        f"executed {[executed[key] for key in differing]})")
    except Exception as exc:  # noqa: BLE001
        finding("acceptance_code_identity", f"{type(exc).__name__}: {exc}")

    try:
        stages = b5_chain.stage_plan(tree)
    except b5_chain.ChainRenderError as exc:
        finding("stage_plan", str(exc))
        stages = []
    policies: set[str] = set()
    checks += ["argv_parses", "capture_dir_absent", "config_selection", "lineage_tags_all_or_none",
               "doctor_config_gate", "duplicate_run_id"]
    for stage in (stage for stage in stages if stage.in_chain):
        try:
            argv = b5_chain.stage_argv(stage, bindings, tree, measurement_root)
        except b5_chain.ChainRenderError as exc:
            finding("argv_parses", f"cannot bind: {exc}", stage_id=stage.stage_id)
            continue
        namespace, problem = parse_stage_argv(stage, argv)
        if problem is None and not isinstance(namespace, argparse.Namespace):
            problem = "the tool's parser was not reached"
        if problem is not None:
            finding("argv_parses", problem, stage_id=stage.stage_id)
            continue
        if stage.kind == "calibration_capture":
            if getattr(namespace, "power_policy", None) is not None:
                policies.add(namespace.power_policy)
            directory = bindings.get("pre_calibration_dir" if stage.slot == "pre" else "post_calibration_dir")
            if plan_mode and directory is not None and os.path.lexists(directory):
                finding("capture_dir_absent", f"{directory} already exists (the writer creates it exist_ok=False)",
                        stage_id=stage.stage_id)
        elif stage.kind == "campaign_collection":
            findings.extend(collection_findings(stage, namespace))

    identity_path = identity_epoch_path
    if identity_path is None and plan_mode and isinstance(bindings.get("identity_epoch_json"), str):
        identity_path = Path(bindings["identity_epoch_json"])
    if identity_path is not None:
        checks.append("desk_identity_power_policy")
        try:
            identity = _read_json(identity_path)
        except InputError as exc:
            finding("desk_identity_power_policy", str(exc))
            identity = None
        if isinstance(identity, Mapping):
            desk = identity.get("power_policy")
            if len(policies) != 1 or desk not in policies:
                finding("desk_identity_power_policy",
                        f"desk identity power_policy {desk!r}; plan tree --power-policy {sorted(policies)}")
            if live_identity:
                checks.append("desk_identity_machine")
                for field, name in (("os_build", "kern.osversion"), ("hardware_model", "hw.model")):
                    live = sysctl(name)
                    if live is None:
                        finding("desk_identity_machine", f"sysctl {name} unreadable", severity=WARNING)
                    elif identity.get(field) != live:
                        finding("desk_identity_machine",
                                f"desk {field} {identity.get(field)!r} differs from live {name} {live!r}",
                                severity=WARNING)
        elif identity is not None:
            finding("desk_identity_power_policy", f"{identity_path} is not a JSON object")

    errors = [item for item in findings if item["severity"] == ERROR]
    return {"schema": REPORT_SCHEMA, "mode": "plan" if plan_mode else "pack", "pack_root": str(pack_root),
            "measurement_root": str(measurement_root), "checkout_root": str(REPO_ROOT),
            "checks": checks, "findings": findings, "errors": len(errors), "clean": not errors}


def _from_plan(path: Path) -> tuple[Mapping[str, Any], Path, Path, dict[str, str]]:
    plan = _read_json(path)
    window = plan.get("hazard_window") if isinstance(plan, Mapping) else None
    pack = window.get("pack") if isinstance(window, Mapping) else None
    bindings = window.get("bindings") if isinstance(window, Mapping) else None
    measurement = plan.get("measurement_root") if isinstance(plan, Mapping) else None
    pack_root = pack.get("pack_root") if isinstance(pack, Mapping) else None
    if not (isinstance(bindings, Mapping) and isinstance(measurement, str) and isinstance(pack_root, str)):
        raise InputError(f"{path} is not a HAZARD_PACK window plan (hazard_window.pack, bindings, measurement_root)")
    tree = _read_json(Path(pack_root) / "plan_tree.json")
    return tree, Path(pack_root), Path(measurement), {str(key): str(value) for key, value in bindings.items()}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--plan", type=Path, help="a window plan (<custody>/night_plan.json)")
    source.add_argument("--pack-root", type=Path, help="a v5 pack root; bindings are synthetic")
    parser.add_argument("--measurement-root", type=Path, default=None,
                        help="with --pack-root: the checkout (default: the pack root's <repo>)")
    parser.add_argument("--identity-epoch-json", type=Path, default=None,
                        help="the desk identity-epoch JSON (default with --plan: its binding)")
    parser.add_argument("--no-live-identity", action="store_true", help="do not read sysctl")
    args = parser.parse_args(argv)
    try:
        if args.plan is not None:
            tree, pack_root, measurement, bindings = _from_plan(args.plan)
            plan_mode = True
        else:
            pack_root = Path(os.path.abspath(args.pack_root))
            measurement = Path(os.path.abspath(args.measurement_root)) if args.measurement_root is not None \
                else pack_root.parents[2]
            tree = _read_json(pack_root / "plan_tree.json")
            bindings = synthetic_bindings(measurement, pack_root)
            plan_mode = False
    except (InputError, IndexError) as exc:
        print(json.dumps({"schema": REPORT_SCHEMA, "input_error": str(exc)}, sort_keys=True))
        return 2
    report = check(tree, pack_root=pack_root, measurement_root=measurement, bindings=bindings, plan_mode=plan_mode,
                   identity_epoch_path=args.identity_epoch_json, live_identity=not args.no_live_identity)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["clean"] else 1


if __name__ == "__main__":
    sys.exit(main())
