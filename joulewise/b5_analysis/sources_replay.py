"""Erratum 2 items 0–7: authenticate and replay the catalog recovery.

This is a provenance replay of the recorded deciding screen. It never emits
an allowance or supplies an alternative screen to an analysis consumer.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any, Mapping

from joulewise import whole_window as ww
from joulewise.b5 import harvest
from joulewise.campaign_provenance import load_authenticated_campaign_catalog
from joulewise.neg8_survivors import neg8_reference_strict_invalid, neg8_reference_energy_unreadable
from .archive import ArchiveHandle, _read
from .context import checked_rebuilt_roster, read_output, read_screen_record, roster_references
from .kept_units import _strict_json
from .windows import AnalysisRefusal, freeze


@dataclass(frozen=True)
class SourcesReplay:
    problem: str | None
    catalog_manifests: tuple = ()
    projected_manifests: tuple = ()
    reference_losses: Mapping[str, str] | None = None
    survivor_bracket: Mapping[str, Any] | None = None


def _claim_source(archive: ArchiveHandle, root: Path, relative: str) -> bytes:
    """Authenticate the archived copy, then bind the original input to it."""
    prefix = "claim-runs/"
    if root.is_relative_to(archive.window.custody_root):
        prefix = "night-custody/" + root.relative_to(archive.window.custody_root).as_posix() + "/"
    raw = archive.source_bytes("sources/" + prefix + relative)
    path = ww._safe_source_path(root, relative)
    try:
        actual = path.read_bytes() if path is not None else None
    except OSError:
        actual = None
    if actual != raw:
        raise AnalysisRefusal("runs_root_differs_from_archive")
    return raw


def _bound(archive: ArchiveHandle, row: Mapping) -> tuple[Mapping, Mapping]:
    record = read_output(archive, ww.NEG8_HARVEST_ALLOWANCE_RECORD)
    if record.get("schema") != ww.NEG8_HARVEST_ALLOWANCE_SCHEMA:
        raise AnalysisRefusal("allowance_record_unauthenticated")
    verdict = record.get("verdict") or {}
    if (verdict.get("row_sha256") != ww.canonical_sha256(row)
            or verdict.get("evaluation_basis_sha256") != (row.get("evaluation_basis") or {}).get("sha256")):
        raise AnalysisRefusal("allowance_record_names_another_row")
    clean = record.get("clean_bound")
    if not isinstance(clean, Mapping) or clean.get("path") != ww.NEG8_HARVEST_CLEAN_BOUND:
        raise AnalysisRefusal("clean_bound_unavailable")
    try:
        raw = archive.withheld_bytes(ww.NEG8_HARVEST_CLEAN_BOUND)
    except AnalysisRefusal:
        raise AnalysisRefusal("clean_bound_unavailable") from None
    corpus = clean.get("corpus_manifest")
    if (hashlib.sha256(raw).hexdigest() != clean.get("sha256") or not isinstance(corpus, Mapping)
            or corpus.get("path") != ww.NEG8_HARVEST_CLEAN_CORPUS or not ww._sha256_text(corpus.get("sha256"))):
        raise AnalysisRefusal("clean_bound_unavailable")
    try:
        # The frozen producer writes this derived manifest without an
        # outputs entry. Its digest is the authenticated allowance's corpus
        # descriptor. Use S0's same checked reader/census as S2 does for its
        # descriptor-bound inputs; never read the archive by raw Path I/O.
        corpus_raw = _read(archive.window.archive_root, ww.NEG8_HARVEST_CLEAN_CORPUS,
            corpus.get("sha256"), "clean_bound_unavailable", "neg8_allowance_record", archive._census)
    except AnalysisRefusal:
        raise AnalysisRefusal("clean_bound_unavailable") from None
    artifact = _strict_json(raw, "clean_bound_unavailable").get("bound")
    if (hashlib.sha256(corpus_raw).hexdigest() != corpus.get("sha256")
            or not ww.validate_neg8_drift_bound_artifact(artifact, reference_corpus_bytes=corpus_raw,
                require_corpus_identity=True) or ww.canonical_sha256(artifact) != record.get("bound_artifact_sha256")):
        raise AnalysisRefusal("clean_bound_unavailable")
    descriptor = record.get("survivor_bracket")
    if not isinstance(descriptor, Mapping) or descriptor.get("path") != ww.NEG8_HARVEST_SURVIVOR_BRACKET:
        raise AnalysisRefusal("survivor_bracket_unauthenticated")
    try:
        raw = archive.withheld_bytes(ww.NEG8_HARVEST_SURVIVOR_BRACKET)
    except AnalysisRefusal:
        raise AnalysisRefusal("survivor_bracket_unauthenticated") from None
    bracket = _strict_json(raw, "survivor_bracket_unauthenticated").get("bracket")
    if hashlib.sha256(raw).hexdigest() != descriptor.get("sha256") or not isinstance(bracket, Mapping):
        raise AnalysisRefusal("survivor_bracket_unauthenticated")
    if record.get("source") != "survivor_rescreen" or bracket.get("decision") != "passed" or bracket.get("conditions") != []:
        raise AnalysisRefusal("screen_not_passed")
    if bracket.get("drift_bound_artifact") != artifact:
        raise AnalysisRefusal("survivor_bound_unauthenticated")
    return artifact, bracket


def _flags(archive: ArchiveHandle) -> list[Mapping]:
    raw = archive.output_bytes("derived/flags.jsonl")
    try:
        return [_strict_json(line, "sources_replay_flags_invalid") for line in raw.splitlines() if line.strip()]
    except AnalysisRefusal:
        raise AnalysisRefusal("sources_replay_flags_invalid") from None


def recompute_reference_losses(manifests, runs_root: Path, roster: Mapping, flags) -> tuple[dict, dict]:
    """Frozen harvest losses and complete item-4 losses, freshly recomputed.

    Harvest code precedence stays exactly pinned. The evaluator's summary,
    status and strict losses are kept separate for the recorded-list check.
    """
    references = set(roster_references(roster))
    invoked = set()
    for manifest in manifests:
        for member in manifest.get("members", []):
            if member.get("execution") == "invoked" and ww._neg8_position(
                    member.get("role"), member.get("sentinel_position")) in ("start", "midpoint", "end"):
                invoked.update(member["bundle_ids"])
    references.update(invoked)
    order = {code: index for index, code in enumerate(harvest.NEG8_REFERENCE_LOSS_CODES)}
    harvested = {}
    for flag in flags:
        scope = flag.get("scope") or {}
        run, code = scope.get("run_id"), flag.get("code")
        if (scope.get("level") == "member" and run in references and code in order
                and (run not in harvested or order[code] < order[harvested[run]])):
            harvested[run] = code
    paths = ww._manifest_bundle_paths(manifests, runs_root)
    if paths is None:
        raise AnalysisRefusal("source_manifest_members_invalid")
    complete = {}
    for run in sorted(references):
        path = Path(paths.get(run) or runs_root / run)
        if not path.is_dir():
            if harvested.get(run) == "member.bytes_missing":
                del harvested[run]
            if run in invoked:
                harvested[run] = "bundle_absent"
            if run in harvested:
                complete[run] = harvested[run]
            continue
        if run in harvested:
            complete[run] = harvested[run]
            continue  # no energy reader is called on an already-lost member
        summary = ww._read_json_object(path / "summary_metrics.json")
        status = summary.get("status") if isinstance(summary, Mapping) else None
        if not isinstance(status, str):
            complete[run] = "summary_unreadable"
        elif status != "succeeded":
            complete[run] = "status_not_succeeded"
        else:
            # RF-1 harvest selects stored energy-unreadable before the
            # evaluator's strict leg. No config-binding leg (J2.6).
            if neg8_reference_energy_unreadable(summary):
                harvested[run] = complete[run] = "energy_unreadable"
            elif neg8_reference_strict_invalid(path, summary=summary).invalid:
                complete[run] = "strict_invalid"
    return harvested, complete


def _basis_reference_check(basis: Mapping):
    occurrences = {item["bundle_id"]: item for item in basis["member_occurrences"]}
    def check(bundle_id: str, path: Path) -> str | None:
        occurrence = occurrences.get(bundle_id)
        if occurrence is None:
            return "reference_not_in_verdict_basis"
        for name, field in (("config.json", "config_sha256"), ("metadata.json", "metadata_sha256"),
                            ("summary_metrics.json", "summary_sha256")):
            try:
                if hashlib.sha256((path / name).read_bytes()).hexdigest() == occurrence[field]:
                    continue
            except (OSError, KeyError):
                pass
            return "reference_not_in_verdict_basis"
        return None
    return check


def replay_claim_sources(row: Mapping, runs_root: Path, *, archive: ArchiveHandle,
                         roster: Mapping) -> SourcesReplay:
    """Replay the frozen recovery, returning a closed problem or provenance."""
    try:
        return _replay_claim_sources(row, Path(runs_root), archive=archive, roster=roster)
    except AnalysisRefusal as exc:
        return SourcesReplay(exc.code)


def _replay_claim_sources(row, runs_root, *, archive, roster):
    if runs_root.resolve() != archive.window.claim_runs_root.resolve():
        return SourcesReplay("sources_replay_runs_root_differs")
    provenance = row.get("row_provenance") or {}
    if provenance.get("source_campaign_manifests") not in (None, []):
        return SourcesReplay("sources_replay_not_applicable")
    if not archive.window.governed_e2:
        return SourcesReplay("recovery_predates_erratum")
    roster = checked_rebuilt_roster(archive, row, roster)
    # Items 0–3 are the actual frozen function, not a locally weakened copy.
    sources = harvest.claim_neg8_sources(row, runs_root, roster=roster)
    if isinstance(sources, str):
        return SourcesReplay(sources)
    manifests, _current, policy = sources
    catalog = load_authenticated_campaign_catalog(runs_root, runs_root / "campaign_log.jsonl")
    if not catalog:
        return SourcesReplay("source_manifest_unauthenticated")
    _claim_source(archive, runs_root, "campaign_log.jsonl")
    verified = []
    for record in catalog:
        relative = "campaign_manifests/" + record.path.name
        raw = _claim_source(archive, runs_root, relative)
        if raw != record.raw_bytes:
            return SourcesReplay("source_manifest_unauthenticated")
        verified.append(({"path": relative, "sha256": hashlib.sha256(raw).hexdigest()}, record.value))
    basis = ww._validated_evaluation_basis(row, runs_root)
    if basis is None:
        return SourcesReplay("evaluation_basis_invalid")
    projected = ww._basis_source_manifests(basis=basis, verified_sources=verified, row=row, runs_root=runs_root)
    if not projected:
        return SourcesReplay("core_rederivation_sources_empty")
    paths = ww._manifest_bundle_paths(projected, runs_root)
    if paths is None or set(paths) != {item["bundle_id"] for item in basis["member_occurrences"]}:
        return SourcesReplay("evaluation_basis_projection_failed")
    screen = read_screen_record(archive)
    harvested, losses = recompute_reference_losses(manifests, runs_root, roster, _flags(archive))
    if harvested != screen.get("harvest_reference_losses"):
        return SourcesReplay("sources_replay_losses_differ")
    recorded = screen["rescreen"]["survivors"]
    recorded_losses = recorded.get("reference_losses", [])
    if (not isinstance(recorded_losses, list) or any(not isinstance(item, Mapping)
            or not isinstance(item.get("bundle_id"), str) or not isinstance(item.get("reason"), str) for item in recorded_losses)
            or len({item.get("bundle_id") for item in recorded_losses}) != len(recorded_losses)):
        return SourcesReplay("sources_replay_losses_differ")
    # A full (3,1,3) bracket keeps historical bytes and may omit its loss
    # fields, including an absent spare. Both deciding loss lists count.
    deciding_losses = {**harvested, **{item["bundle_id"]: item["reason"] for item in recorded_losses}}
    invoked_references = {bundle for manifest in manifests for member in manifest.get("members", [])
        if member.get("execution") == "invoked" and ww._neg8_position(member.get("role"),
            member.get("sentinel_position")) in ("start", "midpoint", "end") for bundle in member["bundle_ids"]}
    # The frozen selector also records known roster losses outside the
    # invoked catalog. They do not enter a screen count, but remain in H's
    # recorded list and must not be discarded from this comparison.
    expected_losses = {**harvested, **{run: reason for run, reason in losses.items() if run in invoked_references}}
    if deciding_losses != expected_losses:
        return SourcesReplay("sources_replay_losses_differ")
    artifact, withheld = _bound(archive, row)
    freshness = withheld.get("bound_freshness") or {}
    derived, problem = ww._derived_neg8_decision(manifests, runs_root, policy,
        point_drift=True, current=True, drift_bound_artifact=artifact, exclude_bundle_ids=losses,
        unreadable_energy="lost", require_replicated_endpoints=True,
        surviving_reference_check=_basis_reference_check(basis),
        required_reference_ids=frozenset(roster_references(roster)), return_bracket=True,
        strict_invalid=lambda _run, path: neg8_reference_strict_invalid(path).invalid,
        freshness_evaluated_at_s=freshness.get("evaluated_at_s"))
    if problem is not None:
        return SourcesReplay(problem)
    if not isinstance(derived, Mapping) or derived.get("decision") != "passed" or derived.get("conditions") != []:
        return SourcesReplay("sources_replay_screen_not_passed")
    unreadable = any(reason == "energy_unreadable" for reason in harvested.values())
    if not ww._neg8_reproduces(derived, withheld, energy_unreadable=unreadable):
        return SourcesReplay("whole_window_verdict_conflict")
    return SourcesReplay(None, freeze(verified), freeze(projected), freeze(losses), freeze(derived))
