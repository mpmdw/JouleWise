"""Per-run harvest table; offsets are applied only at this export boundary."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from joulewise.b6 import blinding
from joulewise.b6.acceptance import _stage_roles, evidence_from_archive
from joulewise.b6.archive import (CLOCK_ANCHOR_STATUS, bundle_of, bundle_roots, ordered_roster, read_json,
                                plan_tree, unresolved_clock_anchor)
from joulewise.desk_compress import read_bytes
from joulewise.desk_restore import StorageStop

PHASES = ("tokenize", "generation_setup", "prefill", "decode")
BOUND_TERMS = ("E_clock_anchor_shift_bound", "E_drift_bound",
               "E_interpolation_edge_bound", "E_interpolation_joint_edge_bound")
ENERGIES = tuple("phase_" + phase + "_j" for phase in PHASES) + (
    "gross_energy_j", "idle_subtracted_energy_j", "energy_request_j",
) + tuple("bound_" + term + "_j" for term in BOUND_TERMS) + (
    "idle_power_w", "idle_variance_of_mean_w2",
)
REFERENCE_KEY = "neg8_reference"
REFERENCE_ROLES = ("corpus", "start", "midpoint", "end")
REFERENCE_UNAVAILABLE = "bytes.reference_request_unavailable"
REFERENCE_REQUEST_COLUMNS = ("reference_request_gross_j", "reference_request_idle_subtracted_j",
                             "reference_request_duration_s")
COLUMNS = (
    "pack_id", "session_id", "attempt", "run_id", "stage_id", "role", "order_index",
    "cell_ids", "strata", "unit_ids", "abba_block_id", "abba_label", "config_key",
    "model_name", "workload_name", "status", "excluded", "exclusion_codes", "flag_codes", "non_claim",
) + ENERGIES + ("prompt_tokens", "emitted_tokens", "requested_output_tokens") + tuple(
    "dur_" + phase + "_s" for phase in PHASES
) + ("idle_baseline_s", "ttft_s", "decode_latency_s", "run_start_utc")


@dataclass(frozen=True)
class ExportResult:
    csv_path: Path
    sidecar_path: Path
    row_count: int

    def structure(self) -> dict:
        return {"csv": str(self.csv_path), "session": str(self.sidecar_path), "rows": self.row_count}


def atomic_write(path: Path, writer) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            writer(stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


class _ReferenceInputs:
    """Authenticate reference inputs against the harvest's source inventory."""

    def __init__(self, root: Path):
        self.root = root
        self.digests = {}
        self.checked_bundles = set()
        path = root / "sources/SHA256SUMS"
        try:
            for line in read_bytes(path).decode("utf-8").splitlines():
                digest, relative = line.split("  ", 1)
                target = Path(os.path.abspath(root / "sources" / relative))
                if (len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)
                        or not target.is_relative_to(Path(os.path.abspath(root)))):
                    raise ValueError(f"invalid SHA256SUMS entry: {line!r}")
                if target in self.digests and self.digests[target] != digest:
                    raise ValueError(f"conflicting SHA256SUMS entry: {relative}")
                self.digests[target] = digest
            if not self.digests:
                raise ValueError("SHA256SUMS is empty")
        except Exception as exc:
            raise StorageStop(f"reference inventory {path}: {type(exc).__name__}: {exc}") from exc

    def read(self, path: Path, *, require_digest=False, equivalent: Path | None = None) -> bytes:
        try:
            raw = read_bytes(path)
            digest = self.digests.get(Path(os.path.abspath(path)))
            if digest is None and equivalent is not None:
                digest = self.digests.get(Path(os.path.abspath(equivalent)))
            if digest is None and require_digest:
                raise ValueError("input has no SHA256SUMS proof")
            if digest is not None and hashlib.sha256(raw).hexdigest() != digest:
                raise ValueError("SHA256SUMS digest mismatch")
            return raw
        except Exception as exc:
            raise StorageStop(f"reference bytes {path}: {type(exc).__name__}: {exc}") from exc

    def listed_bundle(self, run_id: str, plan: Mapping) -> bool:
        return any(path.is_relative_to(Path(os.path.abspath(base / run_id)))
                   for base in bundle_roots(self.root, plan, archive_only=True) for path in self.digests)

    def bundle(self, run_id: str, plan: Mapping) -> Path:
        # Collected references belong to the archive. Coexisting external
        # originals are never candidates, even when the archived copy is gone.
        candidates = {Path(os.path.abspath(base / run_id))
                      for base in bundle_roots(self.root, plan, archive_only=True)}
        listed = [candidate for candidate in sorted(candidates)
                  if any(path.is_relative_to(candidate) for path in self.digests)]
        stray = [candidate for candidate in sorted(candidates)
                 if candidate.is_dir() and candidate not in listed]
        if stray:
            raise StorageStop(f"reference bundle {run_id}: unlisted bundle directories: {stray}")
        if len(listed) != 1:
            raise StorageStop(f"reference bundle {run_id}: expected one listed bundle, found {len(listed)}: {listed}; "
                              f"collected bundle directory missing or ambiguous; tried {sorted(candidates)}")
        bundle = listed[0]
        if not bundle.is_dir():
            raise StorageStop(f"reference bundle {bundle}: collected bundle directory missing from archive")
        return bundle

    def check_membership(self, harvested: Mapping, projected: Mapping, plan: Mapping, pack_id: str,
                         excluded_ids: frozenset = frozenset()) -> None:
        # Both archived candidates influence the permissive reader's choice.
        # Missing/malformed listed control bytes must not change that choice
        # or erase reference roles through its empty-tree fallback.
        for path in (self.root / "sources/repo/configs/campaigns" / pack_id / "plan_tree.json",
                     self.root / "sources/pack/plan_tree.json"):
            if Path(os.path.abspath(path)) in self.digests:
                _reference_json(path, self)
        tree, directory = plan_tree(self.root, plan, pack_id)
        if directory is not None:
            tree = _reference_json(directory / "plan_tree.json", self)
        roles = _stage_roles(tree)[1]
        # Classify inventory bundles independently of the roster: the archived
        # plan still names a reference whose roster entry has disappeared.
        listed_ids = set()
        for base in bundle_roots(self.root, plan, archive_only=True):
            base = Path(os.path.abspath(base))
            listed_ids.update(path.relative_to(base).parts[0] for path in self.digests
                              if path.is_relative_to(base) and len(path.relative_to(base).parts) > 1)
        reference_ids = {run for run, role in roles.items() if role in REFERENCE_ROLES}
        sets = []
        for name, roster in (("harvest roster", harvested), ("acceptance", projected)):
            members = [m["run_id"] for m in roster.get("members", [])
                       if roles.get(m["run_id"], m.get("role")) in REFERENCE_ROLES]
            if len(members) != len(set(members)):
                raise StorageStop(f"reference membership {name}: duplicate reference run ids")
            sets.append((name, set(members)))
            reference_ids.update(members)
        inventory = listed_ids & reference_ids
        for name, members in sets:
            missing = sorted(inventory - members)
            # A planned reference that was never collected has a roster row, no
            # archived directory and no inventory entry. It stays a printed row
            # only when acceptance records its exclusion, so it cannot vanish
            # silently either way (#416 FIX-416-F ruling F2H; H's window-end r1-r3).
            uncollected = {run for run in members - inventory if run in excluded_ids
                           and not any((Path(os.path.abspath(base)) / run).exists()
                                       for base in bundle_roots(self.root, plan, archive_only=True))}
            unlisted = sorted(members - inventory - uncollected)
            if missing or unlisted:
                raise StorageStop(f"reference membership {name}: listed bundles missing from member set {missing}; "
                                  f"members without listed bundles {unlisted}")
        # Check even an excluded reference or a planned reference whose roster
        # and inventory entries are both gone: an existing unlisted directory
        # must not disappear from custody merely because the sets agree.
        for run_id in sorted(reference_ids):
            if run_id in listed_ids or any((base / run_id).is_dir()
                    for base in bundle_roots(self.root, plan, archive_only=True)):
                self.bundle(run_id, plan)

    def harvested_status(self, run_id: str, plan: Mapping) -> str:
        # Older seam archives lack member assessments. A listed source status
        # or original summary positively distinguishes a failed collection.
        bundle = self.bundle(run_id, plan)
        for name in ("status.json", "summary_metrics.json"):
            path = bundle / name
            if path not in self.digests and not path.exists() and not Path(str(path) + ".zst").exists():
                continue
            value = _reference_json(path, self).get("status")
            if isinstance(value, Mapping):
                value = value.get("state")
            if value is not None:
                if not isinstance(value, str) or not value:
                    raise StorageStop(f"reference bytes {path}: ValueError: status must name a state")
                return value
        raise StorageStop(f"reference status {bundle}: no verified source status in status.json or summary_metrics.json")

    def check_bundle(self, bundle: Path) -> None:
        # Include listed files that have disappeared, including whole subtrees.
        if bundle in self.checked_bundles:
            return
        listed = {path for path in self.digests if path.is_relative_to(Path(os.path.abspath(bundle)))}
        if not listed:
            raise StorageStop(f"reference bundle {bundle}: no inventory entries")
        # Verify vanished listed inputs as well as every present logical input.
        # The latter also covers raw/instrument files read indirectly by the reducer.
        present = set()
        for directory, _, names in os.walk(bundle, followlinks=True):
            resolved = Path(directory).resolve()
            parents = Path(directory).relative_to(bundle).parents
            if any((bundle / parent).resolve() == resolved for parent in parents):
                raise StorageStop(f"reference bundle {bundle}: directory cycle in input tree: {directory}")
            for name in names:
                path = Path(directory) / name
                present.add(Path(str(path)[:-4]) if path.suffix == ".zst" else path)
        for path in sorted(listed | present):
            self.read(path, require_digest=True)
        self.checked_bundles.add(bundle)


def _reference_json(path: Path, inputs: _ReferenceInputs | None = None, *, equivalent: Path | None = None):
    try:
        value = json.loads(inputs.read(path, require_digest=True, equivalent=equivalent) if inputs is not None else read_bytes(path))
        if not isinstance(value, dict):
            raise ValueError("JSON value must be an object")
        return value
    except Exception as exc:
        raise StorageStop(f"reference bytes {path}: {type(exc).__name__}: {exc}") from exc


def _verify_harvest_outputs(root: Path) -> None:
    """Use recorded harvest digests; acceptance is produced after the receipt."""
    receipt = root / "harvest.json"
    try:
        outputs = json.loads(read_bytes(receipt))["outputs"]
        if not isinstance(outputs, Mapping):
            raise ValueError("outputs must be an object")
        # These derived inputs are read by export or its evidence reader. The
        # post-harvest acceptance record has no digest; membership/status below
        # cross-check its decisions, and every exclusion keeps its printed code.
        for relative in ("derived/roster.json", "derived/flags.jsonl"):
            path = root / relative
            if (path.exists() or Path(str(path) + ".zst").exists()) and relative not in outputs:
                raise ValueError(f"{relative}: input has no harvest.json digest")
        for relative, digest in outputs.items():
            path = Path(os.path.abspath(root / relative))
            if not path.is_relative_to(Path(os.path.abspath(root))):
                raise ValueError(f"invalid harvest output path: {relative}")
            if not (relative.startswith("derived/") or relative == "withheld/member-assessments.json"):
                continue
            if (not isinstance(digest, str) or len(digest) != 64
                    or any(c not in "0123456789abcdef" for c in digest)):
                raise ValueError(f"{relative}: invalid recorded digest")
            try:
                if hashlib.sha256(read_bytes(path)).hexdigest() != digest:
                    raise ValueError("harvest.json digest mismatch")
            except Exception as exc:
                raise StorageStop(f"harvest output {path}: {type(exc).__name__}: {exc}") from exc
    except Exception as exc:
        raise StorageStop(f"harvest receipt {receipt}: {type(exc).__name__}: {exc}") from exc


def _events(bundle: Path | None, *, reference=False, inputs=None) -> list[dict]:
    if bundle is None:
        if reference:
            raise StorageStop("reference events: bundle directory missing")
        return []
    path = bundle / "events.jsonl"
    try:
        lines = (inputs.read(path, require_digest=True) if inputs is not None else read_bytes(path)).decode("utf-8").splitlines()
        events = [json.loads(line) for line in lines if line.strip()]
        if reference and any(not isinstance(event, dict) for event in events):
            raise ValueError("events.jsonl entries must be JSON objects")
        return events
    except Exception as exc:
        if reference:
            raise StorageStop(f"reference events {path}: {type(exc).__name__}: {exc}") from exc
        if isinstance(exc, FileNotFoundError):
            return []
        raise


def _event_fields(events: list[dict]) -> dict:
    result, starts = {}, {}
    for event in events:
        phase, kind = event.get("phase"), event.get("event_type")
        meta = event.get("metadata") or {}
        if kind == "phase_start":
            starts[phase] = event["timestamp_s"]
        elif kind == "phase_end":
            if phase in starts and phase in PHASES:
                result["dur_" + phase + "_s"] = event["timestamp_s"] - starts[phase]
            for key in ("prompt_tokens", "emitted_tokens", "requested_output_tokens"):
                if key in meta:
                    result[key] = meta[key]
            if phase == "decode" and "output_tokens" in meta:
                result["emitted_tokens"] = meta["output_tokens"]
        elif kind == "run_started":
            result["run_start_utc"] = event.get("timestamp_utc") or (
                datetime.fromtimestamp(event["timestamp_s"], timezone.utc).isoformat()
                if event.get("timestamp_s") is not None else None)
    return result


def _reference_request_fields(bundle, events, summary, record, archive_root, *, physics_cache=None, inputs=None):
    """Clock-free reference integrals on tokenize start through decode end.

    Use the reducer's native reconstructed curve, rather than a sum of phase
    energies: gaps between phases are part of the request too.
    """
    from joulewise.bundle_read import BundleReader, BundleReadError
    from joulewise.desk_restore import readable_run
    from joulewise.reduce import (REDUCER_VERSION, _derive_anchor_context,
                                  _assert_trace_matches_raw, _integrate)
    try:
        if bundle is None or not bundle.is_dir():
            raise FileNotFoundError(f"bundle directory missing: {bundle}")
        inputs = inputs or _ReferenceInputs(Path(archive_root))
        inputs.check_bundle(bundle)
        summary_path = Path(archive_root) / "withheld/reductions" / (bundle.name + ".summary_metrics.rereduced.json")
        if not isinstance(summary, dict):
            raise ValueError(f"{summary_path}: JSON value must be an object")
        for key in ("idle_baseline", "summary_provenance"):
            if key in summary and not (key == "idle_baseline" and summary[key] is None) and not isinstance(summary[key], dict):
                raise ValueError(f"{summary_path}: {key} must be an object")
        journal = Path(str(archive_root) + ".desk") / "compression.jsonl"
        with readable_run(bundle, compression_records=journal) as plain:
            reader = BundleReader(plain)
            curve = reader.summed_curve()
            bound = (record.get("calibration") or {}).get("operative_bound_s")
            version = (summary.get("summary_provenance") or {}).get("reducer_version", REDUCER_VERSION)
            context = _derive_anchor_context(reader, reader.metadata(), reducer_version=version,
                authenticated_fiducial_bound_override_s=float(bound) if bound is not None else None,
                instrument_calibration_physics_cache=physics_cache)
            if context.unresolved:
                raise ValueError(f"anchor context unresolved: {context.detail}")
            if context.telemetry_is_powermetrics:
                if context.curve is None:
                    raise ValueError(f"raw/powermetrics.plist: anchor context has no curve: {context.detail}")
                _assert_trace_matches_raw(curve, context.curve)
                curve = context.curve
            if not curve:
                raise BundleReadError("power_trace.csv has no usable curve")
            starts = [e["timestamp_s"] for e in events
                      if e.get("phase") == "tokenize" and e.get("event_type") == "phase_start"]
            ends = [e["timestamp_s"] for e in events
                    if e.get("phase") == "decode" and e.get("event_type") == "phase_end"]
            if len(starts) > 1 or len(ends) > 1:
                raise ValueError("events.jsonl: request markers must be unique")
            if any(type(v) not in (int, float) or not math.isfinite(v) for v in starts + ends):
                raise ValueError("events.jsonl: request endpoints must be finite numbers")
            if not starts or not ends:
                inputs.read(bundle / "events.jsonl", require_digest=True)
                return {}
            start, end = starts[0], ends[0]
            if end <= start:
                raise ValueError("events.jsonl: request interval must have increasing endpoints")
            if curve[0].support_start_s is not None:
                support_start, support_end = curve[0].support_start_s, curve[-1].support_end_s
                if not context.telemetry_is_powermetrics:
                    covered = start
                    for left, right in sorted((p.support_start_s, p.support_end_s) for p in curve):
                        # Near epoch 1.79e9 s, one ulp is 2.38e-7 s. Four ulp
                        # cover edge representation error (< 1% of the smallest
                        # printed duration precision, 1 ms); no physical gap bar.
                        if left - covered > 4 * math.ulp(left) and covered < end:
                            raise ValueError(f"power_trace.csv curve support has a gap at {covered}")
                        covered = max(covered, right)
                    support_end = covered
                # The reducer constructs native powermetrics intervals from
                # cumulative durations, so their interior is continuous without
                # treating epoch-float rounding at shared edges as missing data.
            else:
                support_start, support_end = curve[0].t, curve[-1].t
            if support_start > start or support_end is None or support_end < end:
                raise ValueError(f"power_trace.csv curve support [{support_start}, {support_end}) "
                                 f"does not cover request [{start}, {end})")
            gross = _integrate(curve, start, end)
        idle = (summary.get("idle_baseline") or {}).get("power_w_mean")
        if type(idle) not in (int, float) or not math.isfinite(idle):
            # Re-reduced summaries are outside sources/. An identical source
            # summary is a valid checksum witness; a changed re-reduction is not.
            inputs.read(summary_path, require_digest=True, equivalent=bundle / "summary_metrics.json")
            return {}
        values = (gross, gross - idle * (end - start), end - start)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("reference request integrals and duration must be finite")
        return dict(zip(REFERENCE_REQUEST_COLUMNS, values))
    except StorageStop as exc:
        raise StorageStop(f"reference request {bundle}: {type(exc).__name__}: {exc}") from exc
    except Exception as exc:
        raise StorageStop(f"reference request {bundle}: {type(exc).__name__}: {exc}") from exc


def export(archive_root: Path | str, plan: Mapping, registration_dir: Path | str,
           pack_records_root: Path | str, export_dir: Path | str, *, non_claim: bool = False,
           evidence=None, acceptance_record: Mapping | None = None,
           pack_registration: Mapping | None = None) -> ExportResult:
    root = Path(archive_root)
    _verify_harvest_outputs(root)
    record = acceptance_record or read_json(root / "derived/b6-acceptance.json")
    pack_id = record["pack_id"]
    if pack_registration is None:
        # Prefer the harvested registration to the desk checkout. The explicit
        # argument is for synthetic/seam callers; normal harvest needs no flag.
        candidates = (root / "sources/pack/registration.json",
                      root / "sources/repo/configs/b6/packs" / pack_id / "registration.json",
                      Path(registration_dir) / "registration.json",
                      Path(__file__).resolve().parents[2] / "configs/b6/packs" / pack_id / "registration.json")
        # Closed replication archives name their campaign (d117_...), while
        # their registrations are alpha/beta/gamma. Resolve the registered
        # plan reference rather than treating that known alias as unregistered.
        plan_ref = f"configs/campaigns/{pack_id}/plan_tree.json"
        for packs in (root / "sources/repo/configs/b6/packs",
                      Path(__file__).resolve().parents[2] / "configs/b6/packs"):
            candidates += tuple(path for path in sorted(packs.glob("*/registration.json"))
                                if isinstance(doc := read_json(path), Mapping)
                                and doc.get("plan_tree_ref") == plan_ref)
        pack_registration = next((doc for path in candidates
                                  if isinstance(doc := read_json(path), Mapping) and doc
                                  and (doc.get("pack_id", pack_id) == pack_id
                                       or doc.get("plan_tree_ref") == plan_ref)), None)
        if not isinstance(pack_registration, Mapping) or not pack_registration:
            raise ValueError(f"pack registration unresolved for {pack_id}: "
                             + ", ".join(str(path) for path in candidates))
    elif not isinstance(pack_registration, Mapping) or not pack_registration:
        raise ValueError(f"explicit pack registration empty or malformed for {pack_id}")
    bytes_request = (pack_registration.get("blinding_group") == "bytes" or pack_id == "bytes"
                     or pack_id.startswith("bytes-"))
    reference_inputs = _ReferenceInputs(root)
    try:
        evidence = evidence or evidence_from_archive(root, plan, registration_dir)
    except Exception as exc:
        if bytes_request:
            raise StorageStop(f"reference archive {root}: {type(exc).__name__}: {exc}") from exc
        raise
    harvested_roster = read_json(root / "derived/roster.json", {})
    roster = ordered_roster(harvested_roster, evidence)
    if bytes_request:
        excluded_members = frozenset(item.get("run_id") for item in record.get("excluding", [])
                                     if item.get("scope") == "member")
        reference_inputs.check_membership(harvested_roster, roster, plan, pack_id, excluded_members)
    session_id = record.get("session_id") or evidence.session_id or str(roster.get("plan_id") or root.name)
    key_dir = blinding.key_directory(pack_records_root, pack_id, pack_registration)
    excluded, codes = defaultdict(set), defaultdict(set)
    for item in record.get("excluding", []):
        if item.get("scope") == "member":
            excluded[item["run_id"]].add(item["code"])
    flags = [*evidence.runtime.get("_b6", {}).get("flags", []), *record.get("emitted_flags", [])]
    for flag in flags:
        run_id = flag["scope"].get("run_id")
        if run_id:
            codes[run_id].add(flag["code"])
    rows, withheld, key_names = [], [], set()
    group = pack_registration.get("blinding_group")
    grouped_blind = bool(group)
    # Every grouped table is offset, including non-claim smoke sessions. The
    # legacy row-level non_claim bit means "offsets not applied" to the existing
    # release reader, so grouped tables keep session provenance in the sidecar
    # and omit that bit. This lets _released_rows remain unchanged.
    columns = (tuple(c for c in COLUMNS if c not in ("run_start_utc", "non_claim")) + ("pass_id",)
               if grouped_blind else COLUMNS)
    if bytes_request:
        columns += REFERENCE_REQUEST_COLUMNS
    reference_physics_cache = {}
    # ordered_roster projects export-time acceptance. Keep the harvest's own
    # success evidence, so missing bytes cannot turn a collected run into failed.
    harvested_members = {m["run_id"]: m for m in harvested_roster.get("members", [])}
    assessments = (read_json(root / "withheld/member-assessments.json", {}) or {}).get("members", {})
    for index, member in enumerate(roster.get("members", [])):
        run_id = member["run_id"]
        reference_role = member["role"] in REFERENCE_ROLES
        harvested_status = (assessments.get(run_id) or {}).get("status", harvested_members.get(run_id, {}).get("status"))
        if isinstance(harvested_status, Mapping):
            harvested_status = harvested_status.get("state")
        if bytes_request and reference_role and reference_inputs.listed_bundle(run_id, plan):
            source_status = reference_inputs.harvested_status(run_id, plan)
            for reported in ((assessments.get(run_id) or {}).get("status"),
                             harvested_members.get(run_id, {}).get("status")):
                if isinstance(reported, Mapping):
                    reported = reported.get("state")
                if reported is not None and (not isinstance(reported, str) or not reported):
                    raise StorageStop(f"reference status {run_id}: malformed harvested status {reported!r}")
                if (reported is not None
                        and (reported == "succeeded") != (source_status == "succeeded")):
                    raise StorageStop(f"reference status {run_id}: harvested status {reported!r} "
                                      f"disagrees with verified source status {source_status!r}")
            if harvested_status is None:
                harvested_status = source_status
        collected = (harvested_status == "succeeded" or harvested_status is None
                     and (member["status"] == "succeeded"
                          or reference_inputs.listed_bundle(run_id, plan)))
        reference = bytes_request and reference_role and collected and not excluded[run_id]
        bundle = None
        try:
            bundle = bundle_of(root, plan, run_id, archive_only=bytes_request and reference_role)
            if reference:
                bundle = reference_inputs.bundle(run_id, plan)
                if bundle is None or not Path(os.path.abspath(bundle)).is_relative_to(Path(os.path.abspath(root))):
                    candidates = ", ".join(str(base / run_id) for base in bundle_roots(root, plan)
                                           if Path(os.path.abspath(base)).is_relative_to(Path(os.path.abspath(root))))
                    fallback = f"; external fallback refused: {bundle}" if bundle is not None else ""
                    raise FileNotFoundError(f"collected bundle directory missing from archive; tried {candidates}{fallback}")
                reference_inputs.check_bundle(bundle)
                reference_inputs.read(bundle / "power_trace.csv", require_digest=True)
                config = _reference_json(bundle / "config.json", reference_inputs)
                metadata = _reference_json(bundle / "metadata.json", reference_inputs)
                status_path = bundle / "status.json"
                if status_path.exists() or Path(str(status_path) + ".zst").exists():
                    status_record = _reference_json(status_path, reference_inputs)
                    status = status_record.get("status")
                    if isinstance(status, Mapping):
                        status = status.get("state")
                    if status != "succeeded":
                        raise ValueError(f"{status_path}: collected reference status is not succeeded: {status!r}")
            else:
                config = read_json(bundle / "config.json", {}) if bundle else {}
                metadata = read_json(bundle / "metadata.json", {}) if bundle else {}
            model, workload = config.get("model") or {}, config.get("workload_profile") or {}
            key = blinding.configuration_key(config)
            if member["role"] in ("corpus", "start", "midpoint", "end"):
                key = REFERENCE_KEY
            tags = dict(tag.split("=", 1) for tag in (config.get("run_metadata") or {}).get("tags", [])
                        if isinstance(tag, str) and "=" in tag)
            units = member.get("units", [])
            status = member["status"]
            if bytes_request and reference_role and harvested_status is not None:
                status = harvested_status
            if reference:
                status = "succeeded"
            row = {"pack_id": pack_id, "session_id": session_id, "attempt": roster.get("attempt"),
                   "run_id": run_id, "stage_id": member["stage_id"], "role": member["role"], "order_index": index,
                   "cell_ids": ";".join(u["cell_id"] for u in units),
                   "strata": ";".join(u["stratum"] for u in units),
                   "unit_ids": ";".join(str(u["unit_id"]) for u in units),
                   "abba_block_id": tags.get("calibration-abba-block-id"),
                   "abba_label": tags.get("calibration-abba-label"), "config_key": key,
                   "model_name": model.get("name"), "workload_name": workload.get("name"),
                   "status": status, "excluded": bool(excluded[run_id]),
                   "exclusion_codes": ";".join(sorted(excluded[run_id])),
                   "flag_codes": ";".join(sorted(codes[run_id])), "non_claim": non_claim}
            summary_path = root / "withheld/reductions" / (run_id + ".summary_metrics.rereduced.json")
            summary = (_reference_json(summary_path, reference_inputs, equivalent=bundle / "summary_metrics.json")
                       if reference else read_json(summary_path, {}))
            events = _events(bundle, reference=reference, inputs=reference_inputs if reference else None)
            if reference:
                for name in ("idle_baseline", "summary_provenance", "phase_energy_j", "energy_bound_terms_j", "idle_mean_uncertainty"):
                    if name in summary and not (name == "idle_baseline" and summary[name] is None) and not isinstance(summary[name], Mapping):
                        raise ValueError(f"{summary_path}: {name} must be an object")
            row.update(_event_fields(events))
            row["run_start_utc"] = row.get("run_start_utc") or summary.get("started_at")
            row.update({key: summary.get(key) for key in ("ttft_s", "decode_latency_s")})
            idle = summary.get("idle_baseline") or {}
            row["idle_baseline_s"] = idle.get("duration_s")
            row.update(dict.fromkeys(ENERGIES))
            unresolved = (summary.get("energy_status") == CLOCK_ANCHOR_STATUS
                          or unresolved_clock_anchor(metadata,
                                                     summary, codes[run_id]))
            if unresolved and reference:
                raise ValueError(f"{bundle / 'metadata.json'}: previously collected reference anchor is unresolved")
            if unresolved:
                row["status"] = CLOCK_ANCHOR_STATUS
            if row["status"] == "succeeded" and not unresolved:
                row.update({"phase_" + phase + "_j": (summary.get("phase_energy_j") or {}).get(phase) for phase in PHASES})
                row.update({key: summary.get(key) for key in ("gross_energy_j", "idle_subtracted_energy_j", "energy_request_j")})
                row.update({"bound_" + term + "_j": (summary.get("energy_bound_terms_j") or {}).get(term + "_j")
                            for term in BOUND_TERMS})
                row["idle_power_w"] = idle.get("power_w_mean")
                row["idle_variance_of_mean_w2"] = (summary.get("idle_mean_uncertainty") or {}).get("governed_variance_of_mean_w2")
                if reference:
                    fields = _reference_request_fields(bundle, events, summary, record, root,
                                                       physics_cache=reference_physics_cache, inputs=reference_inputs)
                    row.update(fields)
                    if not fields:
                        codes[run_id].add(REFERENCE_UNAVAILABLE)
                        row["flag_codes"] = ";".join(sorted(codes[run_id]))
        except Exception as exc:
            if reference:
                raise StorageStop(f"reference request {bundle or root / 'sources' / run_id}: "
                                  f"{type(exc).__name__}: {exc}") from exc
            raise
        if not non_claim or grouped_blind:
            row = blinding.apply(row, blinding.factor(key_dir, key, session_id=session_id))
            key_names.update(("pack.json", blinding._config_filename(key)))
        if grouped_blind:
            # The registered stage walk supplies order_index; no wall/monotonic
            # clock enters the pre-commit table. Durations remain observables.
            row.pop("run_start_utc", None)
            row.pop("non_claim", None)
            row["pass_id"] = pack_registration.get("bytes_pass")
            (rows if key == REFERENCE_KEY or blinding.configuration_stage(config) == "fit"
             else withheld).append(row)
        else:
            rows.append(row)
    destination = Path(export_dir) / pack_id
    csv_path = destination / (session_id + ".runs.csv")
    sidecar = destination / (session_id + ".session.json")

    def write_csv(stream):
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

    withheld_record = None
    if grouped_blind:
        key_sha256 = blinding.bind_session_keys(key_dir, session_id, key_names)
        store = blinding.withheld_path(key_dir, pack_id, session_id)
        def write_withheld(stream):
            writer = csv.DictWriter(stream, fieldnames=columns)
            writer.writeheader()
            writer.writerows(withheld)
        # Persist already offset rows before publishing their count-only locator.
        atomic_write(store, write_withheld)
        counts = defaultdict(int)
        for row in withheld:
            counts[hashlib.sha256(row["config_key"].encode("utf-8")).hexdigest()] += 1
        withheld_record = {"path": os.path.relpath(store, destination), "row_count": len(withheld),
                           "config_key_sha256": dict(sorted(counts.items()))}
    atomic_write(csv_path, write_csv)
    session = {"schema": "joulewise.b6_export_session.v1", "pack_id": pack_id, "session_id": session_id,
               **{key: record.get(key) for key in ("verdict", "counting", "flag_counts")},
               "operative_bound_s": record.get("calibration", {}).get("operative_bound_s"),
               "neg8": record.get("neg8"), "non_claim": non_claim,
               "blinding": {"applied": not non_claim or grouped_blind, "key_dir": os.path.relpath(key_dir, destination)}}
    unavailable = sum(REFERENCE_UNAVAILABLE in r["flag_codes"].split(";") for r in rows)
    if unavailable:
        session["flag_counts"] = {**(session.get("flag_counts") or {}), REFERENCE_UNAVAILABLE: unavailable}
    if grouped_blind:
        session["blinding"]["key_sha256"] = key_sha256
        session["blinding"].update(group=group, pass_id=pack_registration.get("bytes_pass"),
                                    withheld=withheld_record)
    atomic_write(sidecar, lambda stream: stream.write(json.dumps(session, sort_keys=True, indent=2) + "\n"))
    return ExportResult(csv_path, sidecar, len(rows))
