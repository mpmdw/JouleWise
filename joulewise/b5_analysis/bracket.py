"""Per-window calibration brackets and ledger-only block sensitivity bounds.

The archived ledger is the decision authority. Historical capture custody is
handled by the frozen evaluator (and by finalization), never by B_max.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

from joulewise import calibration_bracketing as calibration
from joulewise import calibration_ledger as ledger
from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS
from joulewise.schemas import CampaignPolicy

from .archive import ArchiveHandle, _read
from .windows import AnalysisRefusal, AnalysedWindow, freeze

LEDGER_COPY = "sources/ledger/calibration_observation_ledger.jsonl"
TERMINAL_PIN = "derived/terminal-pin.json"
COMPARED_FIELDS = (
    "status", "pre", "post", "endpoint_max_b_fiducial_s", "drift_s",
    "calibration_drift_allowance_s", "b_fiducial_s", "bracket_binding",
)
COMPARED_ACCEPTANCE_FIELDS = (
    "freshness", "preflight", "drift", "allowance", "prospective_rederivation",
)


@dataclass(frozen=True)
class WindowBracket:
    window: AnalysedWindow
    trigger_scope: str
    evaluation: Mapping[str, Any]
    b_fiducial_s: float
    terminal_sequence: int
    ledger_copy_sha256: str
    compared_with_harvest: str
    sources_sha256sums_sha256: str


@dataclass(frozen=True)
class BMax:
    value_s: float
    attained_by_sequence: int | None
    T: int


class _Inputs:
    """One authenticated source inventory per operation, including its census pin.

    Reuse S0's checked manifest/parser and census reader. Its public source_bytes
    deliberately re-reads the inventory on every access; J7 requires one read.
    """

    def __init__(self, archive: ArchiveHandle):
        self.archive = archive
        self.manifest = archive._sources()
        self.manifest_sha256 = next(row.sha256 for row in archive.census()
                                    if row.path == "sources/SHA256SUMS")

    def source(self, relative: str, *, code="archive_source_unauthenticated") -> bytes:
        digest = self.manifest.get(relative.removeprefix("sources/"))
        if not relative.startswith("sources/") or digest is None:
            raise AnalysisRefusal(code)
        return _read(self.archive.window.archive_root, relative, digest, code,
                     "sources_sha256sums", self.archive._census)


def _json(raw: bytes, code: str) -> dict:
    try:
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (ValueError, UnicodeError):
        raise AnalysisRefusal(code) from None


def _snapshot(raw: bytes, pin: Mapping[str, Any], *, repo_root: Path,
              cutoff: Mapping[str, Any] | None = None):
    # The frozen loader accepts paths only. Materialize exactly the authenticated
    # bytes, rather than allowing it to reopen a longer or changed archive copy.
    with tempfile.TemporaryDirectory(prefix="l9-bracket-") as directory:
        root = Path(directory)
        ledger_path, pin_path = root / "ledger.jsonl", root / "pin.json"
        ledger_path.write_bytes(raw)
        pin_path.write_text(json.dumps(dict(pin)))
        baseline = {} if cutoff is None else {
            "baseline_sequence": cutoff.get("sequence"),
            "baseline_digest": cutoff.get("head_digest"),
        }
        return ledger.load_calibration_ledger_snapshot(
            ledger_path, pin_path, require_committed_pin=False,
            verify_custody=False, mode="issuing", repo_root=repo_root, **baseline)


def ledger_prefix(ledger_bytes: bytes, terminal_pin: Mapping) -> bytes:
    """Keep the original bytes through the authenticated terminal receipt."""
    code = "ledger_prefix_not_at_terminal_pin"
    pin = ledger._head_pin(terminal_pin)
    if pin is None or pin[0] <= 0:
        raise AnalysisRefusal(code)
    kept = []
    try:
        for line in ledger_bytes.splitlines(keepends=True):
            kept.append(line)
            row = json.loads(line)
            if row.get("sequence") == pin[0]:
                if row.get("receipt_digest") != pin[1]:
                    raise AnalysisRefusal(code)
                prefix = b"".join(kept)
                snapshot = _snapshot(prefix, terminal_pin, repo_root=Path("."))
                if not snapshot.valid:
                    raise AnalysisRefusal(code)
                return prefix
    except (ValueError, UnicodeError, AttributeError, TypeError):
        raise AnalysisRefusal(code) from None
    raise AnalysisRefusal(code)


def _copy(inputs: _Inputs):
    raw = inputs.source(LEDGER_COPY, code="ledger_copy_digest_mismatch")
    pin = _json(inputs.archive.output_bytes(TERMINAL_PIN), "ledger_prefix_not_at_terminal_pin")
    return raw, ledger_prefix(raw, pin), pin


def _window_inputs(archive: ArchiveHandle, inputs: _Inputs):
    """Repeat the harvest's strict/succeeded/bounded selection and bundle reads."""
    assessments = _json(archive.withheld_bytes("withheld/member-assessments.json"),
                        "window_bracket_not_passed")
    windows, bindings = [], []
    claim = archive.window.claim_runs_root
    source_root = "sources/claim-runs"
    if claim.is_relative_to(archive.window.custody_root):
        source_root = "sources/night-custody/" + claim.relative_to(archive.window.custody_root).as_posix()
    try:
        members = assessments["members"]
        with tempfile.TemporaryDirectory(prefix="l9-bracket-members-") as directory:
            for ordinal, (_, member) in enumerate(sorted(members.items())):
                path = Path(member["bundle_path"])
                if not (member.get("strict_valid") and member.get("status") == "succeeded"
                        and member.get("anchor_recorded") == "bounded" and path.is_relative_to(claim)):
                    continue
                relative = path.relative_to(claim).as_posix()
                target = Path(directory) / str(ordinal)
                target.mkdir()
                for name in ("events.jsonl", "metadata.json"):
                    (target / name).write_bytes(inputs.source(f"{source_root}/{relative}/{name}"))
                reader = BundleReader(target)
                window = reader.measured_window()
                binding = reader.metadata().get("instrument_calibration", {}).get("bindings")
                if window is None or not isinstance(binding, Mapping):
                    raise ValueError()
                windows.append(window)
                bindings.append(binding)
        if not windows or any(any(item.get(key) != bindings[0].get(key) for key in V2_BINDING_FIELDS)
                              for item in bindings[1:]):
            raise ValueError()
    except (KeyError, ValueError, TypeError, AttributeError, BundleReadError):
        raise AnalysisRefusal("window_bracket_not_passed") from None
    return min(row.start_s for row in windows), max(row.end_s for row in windows), bindings[0]


def evaluate_window_bracket(archive: ArchiveHandle, *, repo_root: Path) -> WindowBracket:
    """Evaluate this archive only, using the frozen harvest evaluator."""
    inputs = _Inputs(archive)
    raw, prefix, pin = _copy(inputs)
    acceptance_raw = inputs.source("sources/inputs/acceptance.json")
    acceptance = calibration._acceptance_bound_from_authenticated_bytes(acceptance_raw)
    if acceptance is None:
        raise AnalysisRefusal("window_bracket_not_passed")
    snapshot = _snapshot(prefix, pin, repo_root=repo_root, cutoff=acceptance["ledger_cutoff"])
    if not snapshot.valid:
        raise AnalysisRefusal("ledger_prefix_not_at_terminal_pin")
    # The persisted roster is the exclusion roster, not the harvest's richer
    # in-memory roster. The archived plan tree owns these calibration inputs.
    pack_source = "sources/repo/configs/campaigns/" + archive.window.pack_id
    roster = _json(inputs.source(pack_source + "/plan_tree.json"), "window_bracket_not_passed")
    try:
        policy_record = roster["campaign_policy"]
        policy_raw = inputs.source("sources/repo/" + policy_record["path"])
        if hashlib.sha256(policy_raw).hexdigest() != policy_record["sha256"]:
            raise ValueError()
        policy = CampaignPolicy.from_mapping(json.loads(policy_raw)).calibration_bracketing
        acceptance_policy = roster["acceptance_policy"]
        issued = acceptance_policy.get("issued_acceptance", {})
        acceptance_pin = issued.get("artifact_sha256", acceptance_policy.get("issued_artifact_sha256"))
        if hashlib.sha256(acceptance_raw).hexdigest() != acceptance_pin:
            raise ValueError()
    except (KeyError, ValueError, TypeError, AttributeError):
        raise AnalysisRefusal("window_bracket_not_passed") from None
    binding = _json(archive.output_bytes("derived/bracket-binding.json"), "window_bracket_not_passed")
    plan_sha256 = hashlib.sha256(inputs.source(pack_source + "/" + roster["plan"]["path"])).hexdigest()
    start, end, bindings = _window_inputs(archive, inputs)
    scope = "window_evidence" if archive.window.governed_e3 else "sealed"
    candidates = calibration.discover_calibration_candidates(snapshot, mode="issuing")
    assessment, reasons = calibration.evaluate_calibration_bracket(
        candidates, window_start_s=start, window_end_s=end, bindings=bindings, policy=policy,
        acceptance_bound=acceptance, ledger_snapshot=snapshot, bracket_binding=binding,
        bracket_window_id=roster["window_identity"]["window_id"],
        bracket_plan_id=roster["plan"]["plan_id"], bracket_plan_sha256=plan_sha256,
        bracket_evidence_root_id=roster["window_identity"]["evidence_root_id"],
        bracket_runs_root=archive.window.claim_runs_root, trigger_scope=scope)
    # Scope matters before comparison: a sealed-scope replay of a governed
    # window is a failed bracket, not merely a disagreement with the harvest.
    bound = assessment.get("b_fiducial_s")
    if (assessment.get("status") != "passed" or reasons or type(bound) not in (int, float)
            or not math.isfinite(bound) or bound < 0):
        raise AnalysisRefusal("window_bracket_not_passed")
    compared = "no_harvest_digest"
    if archive.window.governed_e3:
        harvested = _json(archive.output_bytes("withheld/bracket-evaluation.json"),
                          "window_bracket_differs_from_harvest")
        prior = harvested.get("assessment", {})
        if (any(assessment.get(key) != prior.get(key) for key in COMPARED_FIELDS)
                or list(reasons) != harvested.get("reasons")
                or any((assessment.get("acceptance") or {}).get(key)
                       != (prior.get("acceptance") or {}).get(key) for key in COMPARED_ACCEPTANCE_FIELDS)):
            raise AnalysisRefusal("window_bracket_differs_from_harvest")
        compared = "equal"
    elif (assessment.get("acceptance") or {}).get("freshness", {}).get("status") != "fresh":
        raise AnalysisRefusal("window_bracket_not_passed")
    return WindowBracket(archive.window, scope, freeze(assessment), float(bound), pin["sequence"],
                         hashlib.sha256(raw).hexdigest(), compared, inputs.manifest_sha256)


def require_ledger_copies_are_prefixes(archives: Sequence[ArchiveHandle], live_ledger: Path) -> None:
    """Release-event custody check on the WHOLE copies, including their tails."""
    try:
        live = Path(live_ledger).read_bytes()
    except OSError:
        raise AnalysisRefusal("ledger_copy_not_prefix_of_live") from None
    for archive in archives:
        raw = _Inputs(archive).source(LEDGER_COPY, code="ledger_copy_digest_mismatch")
        if not live.startswith(raw):
            raise AnalysisRefusal("ledger_copy_not_prefix_of_live")


def _bound(value: Any) -> Decimal:
    try:
        if isinstance(value, bool):
            raise ValueError()
        number = Decimal(str(value))
        if not number.is_finite() or number < 0 or not math.isfinite(float(number)):
            raise ValueError()
        return number
    except (InvalidOperation, ValueError):
        raise AnalysisRefusal("block_b_max_invalid") from None


def block_b_max(acceptance: Mapping, ledger_prefix_at_T: bytes, *, cutoff_sequence=376) -> BMax:
    """Compute B_max from acceptance members and ledger observations, never files."""
    receipts, reasons = ledger._parse_ledger(ledger_prefix_at_T)
    observations, _, state_reasons = ledger._attempts_and_observations(receipts)
    if reasons or state_reasons or not receipts:
        raise AnalysisRefusal("ledger_prefix_not_at_terminal_pin")
    try:
        members = acceptance["derivation_corpus"]["members"]
        if not members:
            raise ValueError()
        maximum = max(_bound(row["b_fiducial_s"]) for row in members)
        epoch = dict(acceptance["identity_epoch"])
    except (KeyError, TypeError, ValueError):
        raise AnalysisRefusal("block_b_max_invalid") from None
    # An acceptance member can itself attain B_max. Its member_id identifies
    # the ledger observation; this lookup needs no historical capture bytes.
    member_ids_at_max = {row.get("member_id") for row in members
                         if _bound(row["b_fiducial_s"]) == maximum and row.get("member_id")}
    attained = next((row.sequence for row in observations
                     if row.sequence <= cutoff_sequence and row.attempt_id in member_ids_at_max
                     and _bound(row.exact_bound_lexeme_s) == maximum), None)
    T = receipts[-1]["sequence"]
    for observation in observations:
        if (cutoff_sequence < observation.sequence <= T
                and observation.disposition in ("valid", "systematic-invalid")
                and dict(observation.identity_epoch) == epoch):
            value = _bound(observation.exact_bound_lexeme_s)
            if value > maximum or value == maximum and attained is None:
                maximum, attained = value, observation.sequence
    return BMax(float(maximum), attained, T)


def block_b_max_for_archives(archives: Sequence[ArchiveHandle]) -> BMax:
    """Choose T from the archives, then require every cut copy to extend to it."""
    if not archives:
        raise AnalysisRefusal("block_b_max_invalid")
    copies = []
    for archive in archives:
        inputs = _Inputs(archive)
        _, prefix, pin = _copy(inputs)
        copies.append((pin["sequence"], prefix, inputs))
    T, longest, inputs_at_T = max(copies, key=lambda item: item[0])
    if any(not longest.startswith(prefix) for _, prefix, _ in copies):
        raise AnalysisRefusal("ledger_copies_disagree_below_T")
    acceptance = _json(inputs_at_T.source("sources/inputs/acceptance.json"), "block_b_max_invalid")
    return block_b_max(acceptance, longest, cutoff_sequence=acceptance["ledger_cutoff"]["sequence"])


def b_sens(window_bracket: WindowBracket | float, b_max: BMax) -> float:
    """J6: each window retains its own operative bound in the sensitivity pass."""
    operative = window_bracket.b_fiducial_s if isinstance(window_bracket, WindowBracket) else window_bracket
    return float(max(_bound(operative), _bound(b_max.value_s)))


def require_member_bound_is_window_bracket(provenance: Mapping, window_bracket: WindowBracket | Mapping) -> None:
    """B1's single operative-bound check, shared by later claim consumers."""
    value = provenance.get("operative_fiducial_bound_s") if isinstance(provenance, Mapping) else None
    expected = (window_bracket.b_fiducial_s if isinstance(window_bracket, WindowBracket)
                else window_bracket.get("b_fiducial_s"))
    if (type(value) not in (int, float) or not math.isfinite(value)
            or type(expected) not in (int, float) or not math.isfinite(expected) or expected < 0
            or value != expected):
        raise AnalysisRefusal("operative_bound_not_the_window_bracket")
