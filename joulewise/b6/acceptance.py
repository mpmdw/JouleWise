"""One structure-only acceptance function for harvest, precheck and smoke."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping, Sequence

from joulewise.b6 import calibration, capture_list, code_check, model_files, registration, survivor_screen
from joulewise.b6.archive import bindings as _bindings, bundle_of, plan_tree as read_plan_tree
from joulewise.b6.acceptance_interface import (
    AcceptanceResult, CaptureEvidence, MemberEvidence, SessionEvidence, StageEvidence,
)
from joulewise.flags.catalog import Catalog, EXCLUDE_WINDOW, load_catalog
from joulewise.flags.exclusions import _same, compute
from joulewise.flags.schema import make_flag, make_scope, make_source, render_line, validate_flag
from joulewise.session_structure import PHYSICAL_STOP_CODES

ROOT = Path(__file__).resolve().parents[2]
PHYSICS_STOP_REASONS = frozenset(PHYSICAL_STOP_CODES)
CALIBRATION_STOPS = frozenset({"pre_calibration_capture_failed", "pre_calibration_screen_failed"})
SCHEMA = "joulewise.b6_acceptance.v1"
COUNT_REASONS = frozenset({"cell.below_minimum", "neg8.survivor_screen_undefined"})


def recorded_idle_skip(member: MemberEvidence) -> bool:
    """A physical pre-measurement loss needs both the flag and admission record."""
    admission = member.runtime.get("environment_admission")
    return (member.runtime.get("bundle_present", True) is not False
            and isinstance(admission, Mapping)
            and any(flag in member.flags and admission.get("skip_reason") == reason
                    for flag, reason in (("idle.wait_cap_skip", "wait_cap_reached"),
                                         ("idle.wait_budget_skip", "wait_budget_exhausted"))))


@dataclass(frozen=True)
class Prepared:
    registration: Mapping
    expected_model: Mapping
    catalog: Catalog
    code: Mapping
    capture_rows: tuple[Mapping, ...]
    preparation_flags: tuple[str, ...]
    plan_tree: Mapping
    roster: Mapping


def _json(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _flag(code: str, catalog: Catalog, *, run_id: str | None = None,
          stage_id: str | None = None, observed: Any = None) -> dict:
    entry = catalog.entry(code)
    return make_flag(code=code, family=entry["family"] or "RECORDS",
                     klass=entry["klass"] or "REPRESENTATION",
                     scope=make_scope("member" if run_id else "window", run_id=run_id, stage_id=stage_id),
                     source=make_source("harvest", "b6.acceptance"), observed=observed,
                     catalog_sha256=catalog.sha256,
                     emitted={"wall_s": 0, "monotonic_ns": 0, "boot_session_uuid": None})


def _stage_roles(tree: Mapping) -> tuple[dict, dict]:
    """Map manifest member ids to collection stages and reference roles."""
    stages, roles = {}, {}
    external = tree.get("external_inputs") or {}
    manifests = external.get("manifests", []) if isinstance(external, Mapping) else external
    for stage in tree.get("stage_graph", []):
        ref = stage.get("input_ref") or {}
        source = stage.get("input") or {}
        for manifest in manifests:
            inner = manifest.get("manifest") or {}
            input_id = manifest.get("external_input_id", manifest.get("input_id"))
            if not ((ref.get("input_id") and ref["input_id"] == input_id)
                    or (source.get("path") and source["path"] == inner.get("path", manifest.get("manifest_path")))):
                continue
            role = {"neg8_bound": "corpus", "neg8_bound_corpus": "corpus",
                    "neg8_settled_corpus": "corpus", "start_references": "start", "end_references": "end",
                    "start_reference": "start",
                    "midpoint_reference": "midpoint", "end_reference": "end",
                    "decode_midpoint_reference": "diagnostic_reference",
                    "prefill_midpoint_reference": "diagnostic_reference"}.get(input_id, "science")
            for member in manifest.get("members", []):
                stages[member["run_id"]] = stage["stage_id"]
                roles[member["run_id"]] = role
    for member in tree.get("science", []):
        roles[member["run_id"]] = "science"
        stages[member["run_id"]] = member.get("stage_id")
        # Science stage ids in the roster are config directories; the graph's
        # input_ref names that directory on contrast packs.
        for stage in tree.get("stage_graph", []):
            ref = stage.get("input_ref") or {}
            source = stage.get("input") or {}
            if (ref.get("stage_id") == member.get("stage_id")
                    or str(ref.get("path", "")).startswith(str(member.get("stage_id")) + "/")
                    or str(source.get("path", "")).endswith("/" + str(member.get("stage_id")) + "/order_manifest.json")):
                stages[member["run_id"]] = stage["stage_id"]
    return stages, roles


class BlockSixAcceptance:
    def prepare(self, *, ledger_path: Path, plan_tree: Mapping,
                registration_dir: Path, code_identity: Mapping,
                pack_root: Path | None = None, ledger_rows: Sequence | None = None) -> Prepared:
        reg = registration.load(registration_dir)
        problems = []
        try:
            pins = registration.load_identity_pins(registration_dir)
        except (OSError, ValueError, TypeError):
            pins = {}
            problems.append("model.identity_unpinned")
        repo = Path(code_identity.get("repo_root", code_identity.get("repo", ROOT)))
        pack_id = (plan_tree.get("window_identity") or {}).get("window_id", reg["pack_id"])
        pack_candidates = ([Path(pack_root) / "registration.json"] if pack_root else []) + [
            repo / "configs/b6/packs" / pack_id / "registration.json"]
        pack_registration = next((doc for path in pack_candidates
                                  if isinstance(doc := _json(path), Mapping)
                                  and doc.get("pack_id") == pack_id), {})
        reg["pack_registration"] = pack_registration
        catalog = load_catalog(repo / reg["catalog"])
        if reg["cell_unit_minimum"] != catalog.cell_unit_minimum:
            catalog = Catalog(catalog.codes, catalog.sha256, catalog.path,
                              {**catalog.rules, "cell_unit_minimum": reg["cell_unit_minimum"]})
        reviewed = _json(repo / reg["reviewed_commits_path"])
        if not isinstance(reviewed, list):
            reviewed = []
            problems.append("code.identity_unmeasured")
        code = code_check.check(repo, reg["registered_commit"], code_identity.get("executed_head"),
                                reg["number_bearing_paths"], reviewed, code_identity.get("status_porcelain"))
        if ledger_rows is not None:
            rows = list(ledger_rows)
        else:
            # The plain list replaces the legacy list, not the capture bytes.
            first = None
            try:
                first = json.loads(next(line for line in Path(ledger_path).read_bytes().splitlines() if line.strip()))
            except (OSError, ValueError, StopIteration):
                pass
            if isinstance(first, Mapping) and str(first.get("schema_version", "")).startswith("joulewise.calibration_"):
                rows = capture_list.import_custody_ledger(ledger_path)
            else:
                rows, problems = capture_list.read(ledger_path)
        if reg["defaults_used"]:
            problems.append("registration.default_used")
        roster = {}
        candidate = Path(pack_root) if pack_root else repo / "configs/campaigns" / reg["pack_id"]
        if (candidate / "plan_tree.json").is_file():
            from joulewise.b5.harvest import build_roster, l4_exclusion_inputs

            roster, _ = l4_exclusion_inputs(build_roster(candidate, repo), {}, plan_id=None, attempt=None)
        return Prepared(reg, model_files.expected(pins), catalog, code, tuple(rows),
                        tuple(sorted(set(p.split(":", 1)[0] for p in problems))), plan_tree, roster)

    def evaluate(self, prepared: Prepared, evidence: SessionEvidence) -> AcceptanceResult:
        """Deterministic: no file reads, clock or energy quantities."""
        catalog, reg = prepared.catalog, prepared.registration
        pack_registration = reg.get("pack_registration", {})
        cell_minimum_disclosed = (pack_registration.get("pack_id") == evidence.pack_id
            and pack_registration.get("blinding_group") == "bytes"
            and pack_registration.get("bytes_pass") in (1, 2)
            and pack_registration.get("flag_effects", {}).get("cell.below_minimum") == "DISCLOSE")
        if cell_minimum_disclosed:
            catalog = Catalog({**catalog.codes, "cell.below_minimum": {
                **catalog.codes["cell.below_minimum"], "effect": "DISCLOSE"}},
                catalog.sha256, catalog.path, catalog.rules)
        internal = evidence.runtime.get("_b6", {})
        mode = "synthetic" if evidence.synthetic else "smoke" if internal.get("smoke") else "archive"
        members = [member for stage in evidence.stages for member in stage.members]
        emitted: list[dict] = []

        def emit(code: str, member: MemberEvidence | None = None, observed: Any = None) -> None:
            emitted.append(_flag(code, catalog, run_id=member.run_id if member else None,
                                 stage_id=member.stage_id if member else None, observed=observed))

        flags = list(internal.get("flags", ()))
        registered_digest = pack_registration.get("flag_catalog_sha256")
        if registered_digest is not None and registered_digest != catalog.sha256:
            emit("catalog.digest_mismatch", observed={"registered": registered_digest,
                                                      "running": catalog.sha256})
        existing = {(row["code"], row["scope"].get("run_id")) for row in flags}
        for code in evidence.window_flags:
            if (code, None) not in existing:
                flags.append(_flag(code, catalog))
        for member in members:
            for code in member.flags:
                if (code, member.run_id) not in existing:
                    flags.append(_flag(code, catalog, run_id=member.run_id, stage_id=member.stage_id))
            if member.status != "succeeded":
                emit("member.status_not_succeeded", member)
        for code in prepared.preparation_flags:
            emit(code, observed={"keys": reg["defaults_used"]} if code == "registration.default_used" else None)
        if internal.get("spare_retries") is True or any(m.role == "spare" for m in members):
            emit("plan.spare_retry_present")
        structural_failures = []
        physics_stop = evidence.stop_reason in PHYSICS_STOP_REASONS
        calibration_stop = evidence.stop_reason in CALIBRATION_STOPS
        if evidence.stop_reason not in (None, "completed") and not physics_stop and not calibration_stop:
            structural_failures.append("structure.chain_crashed")
        if not evidence.captures and not (physics_stop or calibration_stop):
            structural_failures.append("structure.no_capture_records")
        if not members:
            structural_failures.append("structure.no_roster")
        for i, stage in enumerate(evidence.stages):
            absent = not stage.members or all(
                m.runtime.get("bundle_present", True) is False
                or "member.bytes_missing" in m.flags for m in stage.members)
            idle_skipped = (bool(stage.members) and len(stage.members) == stage.expected_count
                            and all(recorded_idle_skip(m) for m in stage.members))
            later_ran = any(m.runtime.get("bundle_present", True) and m.status == "succeeded"
                            for later in evidence.stages[i + 1:] for m in later.members)
            # §1.8/§8.2 govern reference losses, including a wholly absent
            # midpoint. They are judged by survivor counts, not by S1.
            references_only = bool(stage.members) and all(m.role in {
                "corpus", "start", "midpoint", "end", "diagnostic_reference"} for m in stage.members)
            if (stage.expected_count and stage.kind == "campaign_collection" and absent and later_ran
                    and not references_only and not idle_skipped):
                structural_failures.append("structure.missing_stage_bundles")
        for code in sorted(set(structural_failures)):
            emit(code)
        blueprints = {member["run_id"]: member for member in prepared.roster.get("members", [])}
        duplicates = {run_id for run_id, n in Counter(m.run_id for m in members).items() if n > 1}
        roster_members = []
        seen = set()
        for member in members:
            if member.run_id in seen:
                continue
            seen.add(member.run_id)
            units = [{"cell_id": cell, "stratum": stratum, "unit_id": unit}
                     for cell, stratum, unit in member.units]
            if not units:
                units = blueprints.get(member.run_id, {}).get("units", [])
            roster_members.append({"run_id": member.run_id, "stage_id": member.stage_id, "units": units})
        for run_id in sorted(duplicates):
            emit("roster.duplicate_run_id", observed={"run_id": run_id})
            # Every unit fed by an ambiguous planned position is lost, while
            # the duplicate-record flag itself only discloses (CA-13).
            emit("member.bytes_ambiguous", next(m for m in members if m.run_id == run_id))
        cell_specs = internal.get("cells", prepared.roster.get("cells", []))
        if not cell_specs:
            strata = defaultdict(set)
            for member in roster_members:
                for unit in member["units"]:
                    strata[unit["cell_id"]].add(unit["stratum"])
            cell_specs = [{"cell_id": cell, "strata": sorted(values)} for cell, values in sorted(strata.items())]
        roster = {"pack_id": evidence.pack_id, "plan_id": internal.get("plan_id"),
                  "attempt": internal.get("attempt"), "members": roster_members, "cells": cell_specs}
        applied = compute(flags + emitted, roster, internal.get("spans", {}), catalog, pack_scoped=False)
        # BYTES §6: the cell is unavailable; the session still counts. Closed
        # replication packs keep the global catalog's window-level minimum.
        if cell_minimum_disclosed and any(not c["resolvable"] for c in applied["cells"]):
            emit("cell.below_minimum", observed={"scope": "cell", "cells": [
                c["cell_id"] for c in applied["cells"] if not c["resolvable"]]})
        for code in sorted({row["code"] for row in flags + emitted if row["code"] not in catalog.codes}):
            emit("catalog.code_unclassified", observed={"code": code})
        excluding = [{"code": code, "scope": "window", "why": catalog.codes.get(code, {}).get("note", code)}
                     for code in applied["reasons"]]
        member_excluding = [{"code": code, "scope": "member", "run_id": item["run_id"], "why": code}
                            for item in applied["members_excluded"] for code in item["codes"]]

        def capture(slot: str) -> calibration.Capture:
            exact = internal.get("captures", {}).get(slot)
            if exact is not None:
                return calibration.Capture(None if exact["value_s"] is None else Decimal(exact["value_s"]), exact["status"])
            item = next((c for c in evidence.captures if c.slot == slot), None)
            if item is None or item.bound_ms is None:
                return calibration.Capture(None, "absent")
            return calibration.Capture(Decimal(str(item.bound_ms)) / Decimal(1000), item.status)

        own_ids = tuple(internal.get("own_session_ids", ())) + ((evidence.session_id,) if evidence.session_id else ())
        cal = calibration.evaluate(capture("pre"), capture("post"), reg, prepared.capture_rows, own_ids,
                                   bool(internal.get("estimator_changed")), pack_id=evidence.pack_id)
        for item in cal["flags"]:
            emit(item["code"], observed={k: v for k, v in item.items() if k != "code"})
        # S-11 has no issued per-pack/phase T_phase in this branch's
        # acceptance registration. Do not substitute a science duration or
        # another pack's rehearsal: P* = F_min/(4*T_phase) is unsized.
        emit("power.pstar_unsized", observed={"pack_id": evidence.pack_id,
                                              "phases": ["prefill", "decode"],
                                              "reason": "registered_T_phase_absent"})
        excluding.extend({"code": code, "scope": "window", "why": code} for code in cal.pop("excluding"))
        if calibration_stop:
            excluding.append({"code": "calibration.bracket_incomplete", "scope": "window",
                              "why": evidence.stop_reason})
        if evidence.stop_reason == "operative_bound_above_stop":
            excluding.append({"code": "calibration.operative_bound_above_stop", "scope": "window",
                              "why": evidence.stop_reason})
        if "calibration.operative_bound_above_stop" in {item["code"] for item in excluding}:
            physics_stop = True
        neg8 = {"planned": dict(reg["neg8"]["planned"])}
        if evidence.synthetic:
            roles = _stage_roles(prepared.plan_tree)[1]
            population = {"members": [{"run_id": m.run_id, "role": roles.get(m.run_id, m.role),
                                       "status": m.status} for m in members]}
            screen = survivor_screen.screen(population, applied, None, reg, counts_only=True).acceptance_evidence()
        else:
            screen = internal.get("neg8") or {"verdict": "undefined", "reason": "bound_absent",
                                             "survivors": {}, "corpus_clean_n": 0}
        # Only named structural projections may leave withheld.
        neg8.update({key: screen.get(key) for key in ("survivors", "corpus_clean_n", "verdict", "reason")})
        for code in screen.get("flags", []):
            emit(code)
        code = "neg8.survivor_screen_" + str(screen["verdict"])
        if screen["verdict"] != "pending" and code not in screen.get("flags", []):
            emit(code)
        if screen["verdict"] in ("failed", "undefined"):
            excluding.append({"code": code, "scope": "window", "why": screen.get("reason") or "screen_failed"})
        mismatches = []
        for row in flags:
            if not all(_same(roster.get(key), row["scope"].get(key)) for key in ("plan_id", "attempt")):
                continue
            observed, expected = row.get("observed") or {}, row.get("expected") or {}
            if not isinstance(observed, Mapping) or not isinstance(expected, Mapping):
                continue
            bytes_differ = False
            if row["code"] == "model.identity_mismatch":
                actual, pinned = observed.get("model_artifact_sha256"), expected.get("model_artifact_sha256")
                bytes_differ = bool(actual and pinned and actual != pinned)
            elif row["code"] == "model.identity_inconsistent_in_window":
                digests = {pair[0] for pair in observed.get("distinct", [])
                           if isinstance(pair, (list, tuple)) and len(pair) == 2 and pair[0]}
                bytes_differ = len(digests) > 1
            if bytes_differ:
                run_id = row["scope"].get("run_id")
                code = "model.files_differ_from_registered"
                mismatches.append({"code": code, "fields": ["model_artifact_sha256"], "run_id": run_id})
                emitted.append(_flag(code, catalog, run_id=run_id, stage_id=row["scope"].get("stage_id"),
                                     observed={"fields": ["model_artifact_sha256"], "harvest_flag_id": row["flag_id"]}))
                excluding.append({"code": code, "scope": "window", "run_id": run_id,
                                  "why": "model_artifact_sha256"})
        for member in members:
            observed = member.runtime or evidence.runtime
            for mismatch in model_files.compare(prepared.expected_model, model_files.run_identity(observed)):
                item = {**mismatch, "run_id": member.run_id}
                if any(previous["code"] == item["code"] and previous["run_id"] == member.run_id
                       for previous in mismatches):
                    continue
                mismatches.append(item)
                emit(item["code"], member, {"fields": item["fields"]})
                if catalog.entry(item["code"])["effect"] == EXCLUDE_WINDOW:
                    excluding.append({"code": item["code"], "scope": "window", "run_id": member.run_id,
                                      "why": ",".join(item["fields"])})
        for code in prepared.code["flags"]:
            emit(code, observed={"paths": prepared.code["changed"]} if code == "code.changed_since_registration" else None)
            if catalog.entry(code)["effect"] == EXCLUDE_WINDOW:
                excluding.append({"code": code, "scope": "window", "why": "unreviewed_number_bearing_change"})
        # Calibration excluding codes also get standard flag records.
        all_codes = {row["code"] for row in flags + emitted}
        for item in excluding:
            if item["code"] not in all_codes:
                emit(item["code"])
                all_codes.add(item["code"])
        expected_smoke = []
        if mode == "smoke":
            expected_smoke = [item for item in excluding if item["code"] == "cell.below_minimum"
                              or (item["code"] == "neg8.survivor_screen_undefined"
                                  and item["why"] in ("bound_absent", "references_insufficient"))]
            excluding = [item for item in excluding if item not in expected_smoke]
        unique = {row["flag_id"]: row for row in flags + emitted}
        counts = dict(sorted(Counter(row["code"] for row in unique.values()).items()))
        reasons = tuple(sorted({item["code"] for item in excluding}))
        verdict = "EXCLUDE" if reasons or physics_stop else "ACCEPT"
        if "records.source_changed_during_harvest" in counts:
            verdict = "HARVEST_RERUN"
        if mode == "smoke" and any(catalog.entry(item["code"])["klass"] == "PHYSICS"
                                    for item in excluding + member_excluding):
            physics_stop = True
            if verdict == "ACCEPT":
                verdict = "EXCLUDE"
        structural = bool(structural_failures) or (mode == "smoke" and any(
            catalog.entry(item["code"])["klass"] != "PHYSICS" for item in excluding))
        record = {"schema": SCHEMA, "mode": mode, "pack_id": evidence.pack_id,
                  "session_id": evidence.session_id, "verdict": verdict,
                  "counting": verdict == "ACCEPT" and not physics_stop, "physics_stop": physics_stop,
                  "physical_stop_kind": PHYSICAL_STOP_CODES.get(evidence.stop_reason,
                      "calibration.operative_bound_above_stop"
                      if "calibration.operative_bound_above_stop" in reasons else None),
                  "stop_reason": evidence.stop_reason,
                  "structural_failures": sorted(set(structural_failures)), "excluding": excluding + member_excluding,
                  "flag_counts": counts, "cells": {c["cell_id"]: c["n_kept"] for c in applied["cells"]},
                  "calibration": cal, "neg8": neg8, "model": {"mismatches": mismatches},
                  "code": {key: prepared.code[key] for key in
                           ("registered", "executed", "number_bearing_changed", "unreviewed")},
                  "emitted_flags": list({row["flag_id"]: row for row in emitted}.values())}
        if evidence.synthetic:
            record["pending"] = list(evidence.pending)
        if mode == "smoke":
            record["expected_in_smoke"] = expected_smoke
        return AcceptanceResult(verdict, reasons, tuple(counts), structural, record["counting"], record)


ACCEPTANCE = BlockSixAcceptance()


def write_result(archive: Path, result) -> None:
    derived = archive / "derived"
    derived.mkdir(parents=True, exist_ok=True)
    rows = result.record["emitted_flags"]
    for row in rows:
        if validate_flag(row):
            raise ValueError("acceptance emitted an invalid flag")
    with (derived / "b6-acceptance.json").open("x", encoding="utf-8") as record_stream:
        with (derived / "b6-flags.jsonl").open("xb") as flags_stream:
            json.dump(result.record, record_stream, sort_keys=True, indent=2, allow_nan=False)
            record_stream.write("\n")
            for row in rows:
                flags_stream.write(render_line(row))


def evidence_from_archive(archive_root: Path | str, plan: Mapping | Path | str,
                          registration_dir: Path | str) -> SessionEvidence:
    """Read structure, raw flags and metadata; never read a summary energy.

    The b_fiducial_s decode and refit live in calibration.read_own_capture.
    """
    root = Path(archive_root)
    if not isinstance(plan, Mapping):
        plan = json.loads(Path(plan).read_text(encoding="utf-8"))
    bindings = _bindings(plan)
    roster = _json(root / "derived/roster.json", {})
    pack_id = roster.get("pack_id", bindings.get("pack_id"))
    if not pack_id:
        pack_id = registration.load(registration_dir)["pack_id"]
    tree, _ = read_plan_tree(root, plan, pack_id)
    stages_for, roles = _stage_roles(tree)
    external = tree.get("external_inputs") or {}
    manifests = external.get("manifests", []) if isinstance(external, Mapping) else external
    plan_members = [m for manifest in manifests for m in manifest.get("members", [])] + tree.get("science", [])
    order = {m["run_id"]: i for i, m in enumerate(plan_members)}
    flags = []
    try:
        lines = (root / "derived/flags.jsonl").read_bytes().splitlines()
    except FileNotFoundError:
        lines = []
    for line in lines:
        try:
            row = json.loads(line)
            projection = {key: row[key] for key in ("code", "scope", "interval", "flag_id")}
            if row["code"] in ("model.identity_mismatch", "model.identity_inconsistent_in_window", "member.bytes_missing"):
                projection.update(observed=row.get("observed"), expected=row.get("expected"))
            flags.append(projection)
        except (ValueError, TypeError, KeyError):
            flags.append(_flag("records.malformed_flag_exclusion_possible", load_catalog(ROOT / "configs/b6/flag_catalog_b6.json")))
    by_run = defaultdict(list)
    missing_by_run = defaultdict(set)
    for row in flags:
        if row["scope"].get("run_id"):
            by_run[row["scope"]["run_id"]].append(row["code"])
            if row["code"] == "member.bytes_missing":
                observed = row.get("observed")
                files = observed.get("files_missing") if isinstance(observed, Mapping) else None
                if isinstance(files, list):
                    missing_by_run[row["scope"]["run_id"]].update(item for item in files if isinstance(item, str))
    grouped = defaultdict(list)
    assessments = _json(root / "withheld/member-assessments.json", {}).get("members", {})
    for member in roster.get("members", []):
        run_id = member["run_id"]
        bundle = bundle_of(root, plan, run_id)
        spare = run_id not in stages_for and str(member.get("stage_id", "")).endswith(".spares")
        # Sealed block-5 trees retain reserve slots. They are not planned block-6
        # observations, even if stray spare bytes were collected.
        if spare and bundle is None:
            continue
        metadata = _json(bundle / "metadata.json", {}) if bundle else {}
        metadata = metadata if isinstance(metadata, Mapping) else {}
        assessment = assessments.get(run_id) or {}
        status_record = _json(bundle / "status.json", {}) if bundle else {}
        status_record = status_record if isinstance(status_record, Mapping) else {}
        recorded_status = assessment.get("status", status_record.get("status", metadata.get("status"))) or {}
        status = recorded_status.get("state") if isinstance(recorded_status, Mapping) else recorded_status
        if status is None:
            status = "succeeded" if bundle else "failed"
        units = tuple((u["cell_id"], u["stratum"], str(u["unit_id"])) for u in member.get("units", []))
        stage = stages_for.get(run_id, member.get("stage_id") or "unplaced")
        role = "spare" if spare else roles.get(run_id, member.get("role", "science"))
        if spare:
            units = ()
        runtime = {**metadata, "bundle_present": bundle is not None,
                   "files_missing": tuple(sorted(missing_by_run[run_id]))}
        grouped[stage].append(MemberEvidence(stage, run_id, status, tuple(by_run[run_id]), units, role,
                                             member.get("config_key"), runtime))
    stages = []
    smoke_tree = (tree.get("smoke_reduction") or {}).get("schema") == "joulewise.b6_smoke_reduction.v1"
    for stage in tree.get("stage_graph", []):
        if stage.get("kind") != "campaign_collection":
            continue
        stage_id = stage["stage_id"]
        rows = tuple(sorted(grouped.pop(stage_id, ()), key=lambda m: order.get(m.run_id, len(order))))
        if smoke_tree:
            rows = rows[:stage["expected_count"]]
        stages.append(StageEvidence(stage_id, stage["kind"], stage["expected_count"], rows))
    if not smoke_tree:
        stages.extend(StageEvidence(stage_id, "unplanned_collection", len(rows), tuple(rows))
                      for stage_id, rows in grouped.items())
    captures, exact_captures, capture_meta = [], {}, []
    for slot, key in (("pre", "pre_calibration_dir"), ("post", "post_calibration_dir")):
        if not bindings.get(key):
            continue
        directory = Path(bindings[key])
        # Prefer the clone of the bound capture when present.
        clones = [root / "sources" / (slot + "-calibration")]
        for runs_key, name in (("claim_runs_root", "claim-runs"), ("bound_runs_root", "bound-runs"),
                               ("custody_root", "night-custody")):
            if bindings.get(runs_key):
                try:
                    clones.append(root / "sources" / name / directory.relative_to(Path(bindings[runs_key])))
                except ValueError:
                    pass
        cloned = next((path for path in clones if path.is_dir()), directory)
        capture = calibration.read_own_capture(cloned)
        if capture.status != "absent":
            captures.append(CaptureEvidence(slot, None if capture.value_s is None else float(capture.value_s * 1000),
                                            capture.status, False))
        exact_captures[slot] = {"value_s": None if capture.value_s is None else str(capture.value_s), "status": capture.status}
        capture_meta.append(capture.metadata)
    raw_spans = _json(root / "withheld/spans.json", {})
    raw_spans = raw_spans.get("spans", raw_spans)
    spans = {run_id: {"monotonic_ns": span.get("monotonic_ns", span.get("member"))}
             for run_id, span in raw_spans.items() if isinstance(span, Mapping)}
    journal = []
    for base in (root / "night", root / "sources/night-custody/night", root / "sources/night",
                 Path(bindings.get("custody_root", root)) / "night"):
        path = base / "chain-stages.jsonl"
        if path.is_file():
            for line in path.read_bytes().splitlines():
                try:
                    journal.append(json.loads(line))
                except ValueError:
                    pass
            break
    stop = next((row.get("reason", row.get("kind")) for row in reversed(journal)
                 if row.get("event", row.get("stage_id")) == "chain.stop"), None)
    if stop is None:
        results = [_json(base / name, {}) for base in
                   (root / "night", root / "sources/night-custody/night", root / "sources/night",
                    Path(bindings.get("custody_root", root)) / "night")
                   for name in ("hazard_result.json", "result.json")]
        def terminal_exit(row):
            return row.get("chain_exit_code", (row.get("chain") or {}).get("exit_code"))

        result = next((row for row in results if row.get("aborted_reason") in PHYSICS_STOP_REASONS),
                      next((row for row in results if terminal_exit(row) is not None), {}))
        completed = next((row.get("exit_code", row.get("rc")) for row in reversed(journal)
                          if row.get("stage_id") == "chain.complete"), None)
        exit_code = bindings.get("chain_exit_code", result.get("chain_exit_code", result.get("chain", {}).get("exit_code", completed)))
        if result.get("aborted_reason") in PHYSICS_STOP_REASONS:
            stop = result["aborted_reason"]
        elif exit_code == 0:
            stop = "completed"
        else:
            from joulewise.session_structure import CHAIN_STOP_EXITS
            stop = CHAIN_STOP_EXITS.get(exit_code, "chain_crashed")
    screen = _json(root / "withheld/b6-neg8.json", {})
    neg8 = {key: screen[key] for key in ("verdict", "survivors", "corpus_clean_n", "reason", "flags") if key in screen}
    try:
        reg_cal = registration.load(registration_dir)["calibration"]
    except (OSError, ValueError):
        # Evidence and exports do not depend on quiet-machine acceptance values.
        reg_cal = {}
    estimator_changed = any(reg_cal.get(key) is not None and meta.get(key) != reg_cal[key]
                            for meta in capture_meta for key in ("protocol_sha256", "estimator_sha256"))
    included = {m.run_id for stage in stages for m in stage.members}
    flags = [row for row in flags if not row["scope"].get("run_id") or row["scope"]["run_id"] in included]
    runtime = {"_b6": {"flags": flags, "cells": roster.get("cells", []), "spans": spans, "smoke": smoke_tree,
                       "spare_retries": bindings.get("spare_retries"), "capture_screen": bindings.get("capture_screen"),
                       "captures": exact_captures, "neg8": neg8, "estimator_changed": estimator_changed,
                       "own_session_ids": [bindings[key] for key in ("session_id", "bracket_session_id") if bindings.get(key)],
                       "plan_id": roster.get("plan_id"), "attempt": roster.get("attempt")}}
    return SessionEvidence(pack_id, tuple(stages), tuple(captures), runtime, False, (),
                           bindings.get("session_id", bindings.get("bracket_session_id")), stop,
                           tuple(sorted({row["code"] for row in flags if not row["scope"].get("run_id")})))
