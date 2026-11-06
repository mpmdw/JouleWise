"""Per-window calibration brackets and ledger-only block sensitivity bounds.

The archived ledger is the decision authority. Historical capture custody is
handled by the frozen evaluator (and by finalization), never by B_max.
"""
from __future__ import annotations

import dataclasses
from contextlib import contextmanager
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import hashlib
import json
import math
import os
from pathlib import Path, PurePath
import pickle
import tempfile
from typing import Any, Mapping, Sequence

from joulewise import analysis_verified_store as vdl
from joulewise import calibration_bracketing as calibration
from joulewise import calibration_ledger as ledger
from joulewise.bundle_read import BundleReadError, BundleReader
from joulewise.authentication_io import V2AuthenticationInputError
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


def _strict_problems(path_text: str) -> list[str]:
    """Member-pool entry point (L9-SPEEDUP-R2): one copied-out bundle's strict problems.

    The selection loop's own call, with a fresh call-local physics cache (the
    run store is shared by the worker, as in the driver).
    """
    from joulewise.cli import validate_bundle

    return list(validate_bundle(Path(path_text), strict=True, physics_cache={}))


def _scheduled_candidate(target: Path) -> bool:
    """Scheduling only: whether the selection will strict-validate this copy.

    It authenticates nothing and decides nothing: the serial loop re-reads both
    documents through the bundle reader at the member's own position, and a
    wrong guess only costs a serial validation or an unused worker result.
    """
    try:
        metadata = json.loads((target / "metadata.json").read_bytes())
        summary = json.loads((target / "summary_metrics.json").read_bytes())
        uncertainty = metadata.get("uncertainty_evidence")
        anchor = uncertainty.get("clock_anchor") if isinstance(uncertainty, Mapping) else None
        return (summary.get("status") == "succeeded" and isinstance(anchor, Mapping)
                and anchor.get("status") == "bounded")
    except (OSError, ValueError, AttributeError, TypeError):
        return False


L4 = "L4_calibration_bracket"


def _seed_copy(target: Path, digests: Mapping[str, str]) -> None:
    """D-188 L4/L1: hand the store this copy's authenticated digests (no re-hash).

    Only digests the copy-out just authenticated against SHA256SUMS are
    seeded, as the content-only (path-free) form both bracket leaves use. The
    seed is lstat-guarded; a copy that changes afterwards is simply re-hashed.
    A seed the store does not take changes nothing but the hashing cost.
    """
    try:
        vdl.seed_verified(target, digests, content_only=True)
    except Exception:  # noqa: BLE001 - a seed is only a hashing shortcut, never a decision input
        pass


@contextmanager
def _temporary_members():
    """Keep path-bound reductions no longer than the copies they describe."""
    with tempfile.TemporaryDirectory(prefix="l9-bracket-members-") as directory:
        root = Path(os.path.realpath(directory))
        store = vdl.active_store()
        try:
            yield root
        finally:
            if store is not None:
                store.discard_entries(lambda _key, entry: entry.leaf_id == "L3_reduce_dict" and any(
                    Path(identity.rsplit("\0", 1)[-1]).is_relative_to(root) for identity, _ in entry.trees))


def _servable(assessment: Any, reasons: Any) -> bool:
    """Whether a stored L4 value may be served: exactly the outcome this caller accepts.

    Sol #5 (D-188 detail critique): the frozen discovery probes every
    candidate locator with probe_custody (calibration_ledger.py:5476-5566), a
    daemon-thread exists/is_dir check bounded by a two-second timeout. Absence,
    a probe exception and a timeout all return "absent" without opening
    anything, so the fill's read set cannot bind them. Discovery is all or
    nothing (calibration_bracketing.py:1986-1988: one absent candidate returns
    no candidates), and no bracket passes without candidates. So a passed,
    reason-free assessment implies that every probe was positive and every
    candidate's manifest and artifacts were read (and are re-verified on a hit
    as recorded extras), while any other outcome may rest on an unrecorded
    negative or timed-out probe. Only the former is ever served; every other
    outcome is recomputed here, live, by the frozen code, so a timeout or
    absence decision is always the serial one at the serial position.
    """
    bound = assessment.get("b_fiducial_s") if isinstance(assessment, Mapping) else None
    return (isinstance(assessment, Mapping) and assessment.get("status") == "passed"
            and isinstance(reasons, tuple) and not reasons
            and type(bound) in (int, float) and math.isfinite(bound) and bound >= 0)


def _storable_value(value: Any) -> bool:
    """Whether an L4 return value is the servable shape (a LeafSpec value predicate).

    Today a non-servable fill is still stored (and exported), only never
    served. The store has no per-leaf value predicate yet; this is the one the
    L4 spec should reference (review of PR #634, finding 1: deferred to
    AUTH-IO-2, which owns analysis_verified_store.py) so that a fill resting on
    a negative or timed-out custody probe is never stored, exported or merged.
    """
    return isinstance(value, tuple) and len(value) == 2 and _servable(*value)


def _located_as_recorded(entry: Any) -> bool:
    """Whether every out-of-tree path a stored L4 value read still resolves to itself.

    The store records extras and listings at their realpaths and re-verifies
    them with lstat on the full path, which follows a symlink in any ancestor.
    A candidate directory moved out of the claim runs root and replaced by a
    symlink keeps its inodes, so the hit would verify, while the frozen loader
    (calibration_bracketing.py:1678-1682) resolves the locator and refuses it
    as outside the runs root. A recorded path whose realpath is no longer
    itself is never served (review of PR #634, finding 2); the frozen code
    then runs live. Anything unreadable falls closed.
    """
    try:
        paths = [path for path, _ in entry.extras] + [path for path, _ in entry.listings]
        return all(isinstance(path, str) and os.path.realpath(path) == path for path in paths)
    except Exception:  # noqa: BLE001 - an unreadable entry is never served
        return False


def _calibration_assessment(runs_root: Path, paths: Sequence[Path], policy: Any, *, mode: Any,
                           ledger_snapshot: Any, bracket_binding: Any, bracket_window_id: Any,
                           bracket_plan_id: Any, bracket_plan_sha256: Any,
                           bracket_evidence_root_id: Any, trigger_scope: Any):
    """Leaf L4 (D-188): the frozen calibration_bracket_for_bundles, served from the VDL store.

    Outside an analysis run with a store, for a relative runs root (Sol #6:
    the frozen evaluator spells it with Path.absolute(), which a relative
    spelling would make depend on the working directory, which no key
    carries), or without a ledger snapshot, this is exactly the frozen call. Otherwise the store keys the
    runs root as given (a scalar), every other argument, and the copies by
    content only (path-free: each evaluation copies into a fresh temporary
    root; the store relocates in-tree reads, Sol #4). A stored value is served
    only when it is the passed, reason-free outcome (``_servable``) and every
    out-of-tree path it read still resolves to itself (``_located_as_recorded``); a probe is
    side-effect free, so a non-servable entry costs one key computation and the
    call then runs the frozen code directly, never through the store.

    The keyword parameters are exactly the ones the one caller passes (the r1
    call at this site), each forwarded by name: the custody-mode census
    (tests/test_custody_mode_inventory.py) then sees ``mode`` as this wrapper's
    own scalar parameter, censused at the issuing caller, never as forwarded
    ``**kwargs``. Every direct frozen call (each bypass) passes the caller's
    own arguments; the renamed ledger snapshot below is handed only to the
    store (which keys on it and, on a miss, fills with it).
    """
    fn = calibration.calibration_bracket_for_bundles
    store = vdl.active_store()
    if store is None or not isinstance(runs_root, (str, PurePath)) or not Path(runs_root).is_absolute():
        return fn(runs_root, paths, policy, mode=mode, ledger_snapshot=ledger_snapshot,
                  bracket_binding=bracket_binding, bracket_window_id=bracket_window_id,
                  bracket_plan_id=bracket_plan_id, bracket_plan_sha256=bracket_plan_sha256,
                  bracket_evidence_root_id=bracket_evidence_root_id, trigger_scope=trigger_scope)
    if (not isinstance(ledger_snapshot, ledger.CalibrationLedgerSnapshot)
            or not isinstance(ledger_snapshot.ledger_path, PurePath)):
        return fn(runs_root, paths, policy, mode=mode, ledger_snapshot=ledger_snapshot,
                  bracket_binding=bracket_binding, bracket_window_id=bracket_window_id,
                  bracket_plan_id=bracket_plan_id, bracket_plan_sha256=bracket_plan_sha256,
                  bracket_evidence_root_id=bracket_evidence_root_id, trigger_scope=trigger_scope)
    # _snapshot loads the authenticated prefix from a per-evaluation temporary
    # file, deleted before this call, so the snapshot's ledger_path would make
    # every evaluation's key distinct. Nothing reads that field
    # (calibration_bracketing.py never names it, and no snapshot method does;
    # test_leaf_bracket checks both): key and pass its final name only, like
    # the path-free copies.
    keyed = dataclasses.replace(ledger_snapshot, ledger_path=Path(ledger_snapshot.ledger_path.name))
    hit = store.probe(L4, fn, runs_root, paths, policy, mode=mode, ledger_snapshot=keyed,
                      bracket_binding=bracket_binding, bracket_window_id=bracket_window_id,
                      bracket_plan_id=bracket_plan_id, bracket_plan_sha256=bracket_plan_sha256,
                      bracket_evidence_root_id=bracket_evidence_root_id, trigger_scope=trigger_scope)
    if hit is not None:
        try:
            servable = _storable_value(pickle.loads(hit.entry.value)) and _located_as_recorded(hit.entry)
        except Exception:  # noqa: BLE001 - an unreadable entry is never served
            servable = False
        if not servable:
            return fn(runs_root, paths, policy, mode=mode, ledger_snapshot=ledger_snapshot,
                      bracket_binding=bracket_binding, bracket_window_id=bracket_window_id,
                      bracket_plan_id=bracket_plan_id, bracket_plan_sha256=bracket_plan_sha256,
                      bracket_evidence_root_id=bracket_evidence_root_id, trigger_scope=trigger_scope)
    return store.call(L4, fn, runs_root, paths, policy, mode=mode, ledger_snapshot=keyed,
                      bracket_binding=bracket_binding, bracket_window_id=bracket_window_id,
                      bracket_plan_id=bracket_plan_id, bracket_plan_sha256=bracket_plan_sha256,
                      bracket_evidence_root_id=bracket_evidence_root_id, trigger_scope=trigger_scope)


def _window_inputs(archive: ArchiveHandle, inputs: _Inputs, directory: Path):
    """Recompute the harvest's selection from authenticated complete bundles.

    Neither pin always records a digest for member-assessments.json. Its
    selection is therefore checked against bundle bytes, never trusted as the
    authority for which members determine the window span.

    L9-SPEEDUP-R2: every rostered bundle is first copied out, serially and in
    roster order; inside an analysis run with workers the strict validations of
    the copies then run in the ordered member pool. The selection itself stays
    serial: at each bundle's roster position its documents are read, its
    candidacy is decided and its validation is consumed (a task that raised is
    recomputed there). A loop that stops at a bundle leaves the archive census
    as the serial loop left it (later copy-outs are rolled back), and a copy-out
    that failed is raised after the bundles before it.
    """
    from joulewise.analysis_member_pool import (consume, is_genuine, member_map, pool_active,
                                                single_bound_per_calibration)
    from joulewise.cli import validate_bundle

    assessments = _json(archive.withheld_bytes("withheld/member-assessments.json"),
                        "window_bracket_not_passed")
    claim = archive.window.claim_runs_root
    source_root = "sources/claim-runs"
    if claim.is_relative_to(archive.window.custody_root):
        source_root = "sources/night-custody/" + claim.relative_to(archive.window.custody_root).as_posix()
    census = archive._census
    try:
        recorded = set()
        for member in assessments["members"].values():
            path = Path(member["bundle_path"])
            if (member.get("strict_valid") and member.get("status") == "succeeded"
                    and member.get("anchor_recorded") == "bounded" and path.is_relative_to(claim)):
                recorded.add(path.relative_to(claim).as_posix())
        inventory = {name.removeprefix(source_root.removeprefix("sources/") + "/")
                     for name in inputs.manifest
                     if name.startswith(source_root.removeprefix("sources/") + "/")}
        roster = _json(archive.output_bytes("derived/roster.json"), "window_bracket_not_passed")
        registered_ids = {row["run_id"] for row in roster["members"]}
        # The authenticated exclusion roster retains all assessed members,
        # including present spares. Enumerate their bundles from the inventory,
        # not the unpinned assessments; ignore unrostered directories exactly
        # as the harvest's assess() does.
        bundles = sorted({str(Path(name).parent) for name in inventory
                          if name.endswith("/metadata.json")
                          and str(Path(name).parent) in registered_ids})
        copies, failed = [], None
        seeding = vdl.active_store() is not None
        for relative in bundles:
            try:
                target = directory / relative
                target.mkdir()
                digests = {}
                for name in sorted(inventory):
                    if not name.startswith(relative + "/"):
                        continue
                    output = target / Path(name).relative_to(relative)
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(inputs.source(f"{source_root}/{name}"))
                    # inputs.source returned exactly these bytes only after
                    # checking them against this SHA256SUMS digest.
                    digests[Path(name).relative_to(relative).as_posix()] = inputs.manifest[
                        f"{source_root}/{name}".removeprefix("sources/")]
            except Exception as exc:  # noqa: BLE001 - raised after the bundles before it
                failed = exc
                break
            if seeding:
                _seed_copy(target, digests)
            copies.append((relative, target, len(census)))
        pooled = pool_active() and is_genuine(validate_bundle, "joulewise.cli:validate_bundle")
        scheduled = [target for _, target, _ in copies if pooled and _scheduled_candidate(target)]
        if not single_bound_per_calibration(scheduled):
            scheduled = []
        outcomes = member_map(_strict_problems, [((str(target),), {}) for target in scheduled], account=False)
        prepared = dict(zip(scheduled, outcomes or ()))
        selected, selected_paths, cache = set(), [], {}
        for relative, target, mark in copies:
            try:
                reader = BundleReader(target)
                try:
                    metadata, summary = reader.raw_metadata() or {}, reader.raw_summary() or {}
                except BundleReadError:
                    # The frozen harvest excludes an unreadable member from this
                    # selection. Its authenticated bytes still remain inventoried;
                    # the complete selected set is checked against that harvest.
                    continue
                except V2AuthenticationInputError as exc:
                    if exc.reason != "v2_authentication_invalid_json":
                        raise
                    # The enclosing v2 reader rejects malformed JSON before the
                    # tolerant bundle reader can classify this archived member.
                    continue
                uncertainty = metadata.get("uncertainty_evidence")
                anchor = uncertainty.get("clock_anchor") if isinstance(uncertainty, Mapping) else None
                if (summary.get("status") == "succeeded" and isinstance(anchor, Mapping) and anchor.get("status") == "bounded"
                        and not consume(prepared.pop(target, None),
                                        lambda target=target: validate_bundle(target, strict=True, physics_cache=cache),
                                        account=True)):
                    selected.add(relative)
                    selected_paths.append(target)
            except BaseException:
                # The serial loop stopped here, before copying out any later bundle.
                for key in list(census)[mark:]:
                    del census[key]
                raise
        if failed is not None:
            raise failed
        if not selected_paths or selected != recorded:
            raise ValueError()
    except AnalysisRefusal:
        raise
    except (KeyError, ValueError, TypeError, AttributeError, BundleReadError):
        raise AnalysisRefusal("window_bracket_not_passed") from None
    return selected_paths


def evaluate_window_bracket(archive: ArchiveHandle, *, repo_root: Path) -> WindowBracket:
    """Evaluate this archive only, using the frozen harvest evaluator."""
    inputs = _Inputs(archive)
    raw, prefix, pin = _copy(inputs)
    acceptance_raw = inputs.source("sources/inputs/acceptance.json")
    acceptance = calibration._acceptance_bound_from_authenticated_bytes(acceptance_raw)
    if acceptance is None:
        raise AnalysisRefusal("window_bracket_not_passed")
    try:
        cutoff = acceptance["ledger_cutoff"]
        if not isinstance(cutoff, Mapping) or type(cutoff["sequence"]) is not int:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise AnalysisRefusal("window_bracket_not_passed") from None
    snapshot = _snapshot(prefix, pin, repo_root=repo_root, cutoff=cutoff)
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
        plan = roster["plan"]
        identity = roster["window_identity"]
        plan_sha256 = hashlib.sha256(inputs.source(pack_source + "/" + plan["path"])).hexdigest()
        window_id, plan_id, evidence_root_id = identity["window_id"], plan["plan_id"], identity["evidence_root_id"]
    except AnalysisRefusal:
        raise
    except (KeyError, ValueError, TypeError, AttributeError):
        raise AnalysisRefusal("window_bracket_not_passed") from None
    binding = _json(archive.output_bytes("derived/bracket-binding.json"), "window_bracket_not_passed")
    scope = "window_evidence" if archive.window.governed_e3 else "sealed"
    # The frozen wrapper reads the registered default acceptance internally.
    # Require that it is exactly the archive's authenticated acceptance before
    # using the wrapper, including its registered-valid anti-withholding check.
    if acceptance != calibration.load_calibration_acceptance_bound():
        raise AnalysisRefusal("window_bracket_not_passed")
    with _temporary_members() as directory:
        paths = _window_inputs(archive, inputs, directory)
        assessment, reasons = _calibration_assessment(
            archive.window.claim_runs_root, paths, policy, mode="issuing",
            ledger_snapshot=snapshot, bracket_binding=binding,
            bracket_window_id=window_id, bracket_plan_id=plan_id, bracket_plan_sha256=plan_sha256,
            bracket_evidence_root_id=evidence_root_id, trigger_scope=scope)
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
    if archive.shape == "pin4":
        harvested_scope = archive.record.get("calibration_bracket") or {}
        if (not isinstance(harvested_scope, Mapping)
                or harvested_scope.get("trigger_scope") != scope
                or harvested_scope.get("erratum_3_governed") is not archive.window.governed_e3
                or harvested_scope.get("evaluated") is not True
                or harvested_scope.get("status") != assessment.get("status")
                or not isinstance(harvested_scope.get("reasons"), (tuple, list))
                or tuple(harvested_scope["reasons"]) != tuple(sorted(map(str, reasons)))):
            raise AnalysisRefusal("window_bracket_differs_from_harvest")
    return WindowBracket(archive.window, scope, freeze(assessment), float(bound), pin["sequence"],
                         hashlib.sha256(raw).hexdigest(), compared, inputs.manifest_sha256)


def require_ledger_copies_are_prefixes(archives: Sequence[ArchiveHandle], live_ledger: Path) -> None:
    """Release-event custody check on the WHOLE copies, including their tails."""
    if not archives:
        raise AnalysisRefusal("ledger_copy_not_prefix_of_live")
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
    if calibration.EPOCH_CONTINUATION_REGISTRY:
        raise AnalysisRefusal("block_b_max_invalid")
    receipts, reasons = ledger._parse_ledger(ledger_prefix_at_T)
    observations, _, state_reasons = ledger._attempts_and_observations(receipts)
    if reasons or state_reasons or not receipts:
        raise AnalysisRefusal("ledger_prefix_not_at_terminal_pin")
    try:
        members = acceptance["derivation_corpus"]["members"]
        if acceptance["artifact_role"] != "issued" or len(members) != 24:
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
    if (len(archives) != 3 or {archive.window.pack for archive in archives} != {"alpha", "beta", "gamma"}
            or len({archive.window.archive_root for archive in archives}) != 3):
        raise AnalysisRefusal("block_b_max_invalid")
    copies = []
    acceptance_bytes = []
    for archive in archives:
        inputs = _Inputs(archive)
        _, prefix, pin = _copy(inputs)
        copies.append((pin["sequence"], prefix, inputs))
        acceptance_bytes.append(inputs.source("sources/inputs/acceptance.json", code="block_b_max_invalid"))
    T, longest, inputs_at_T = max(copies, key=lambda item: item[0])
    if any(not longest.startswith(prefix) for _, prefix, _ in copies):
        raise AnalysisRefusal("ledger_copies_disagree_below_T")
    if any(raw != acceptance_bytes[0] for raw in acceptance_bytes[1:]):
        raise AnalysisRefusal("block_b_max_invalid")
    acceptance = calibration._acceptance_bound_from_authenticated_bytes(acceptance_bytes[0])
    try:
        if acceptance is None or acceptance["artifact_role"] != "issued" or len(acceptance["derivation_corpus"]["members"]) != 24:
            raise ValueError()
        cutoff = acceptance["ledger_cutoff"]["sequence"]
        if type(cutoff) is not int or cutoff != 376:
            raise ValueError()
    except (KeyError, TypeError, ValueError):
        raise AnalysisRefusal("block_b_max_invalid") from None
    return block_b_max(acceptance, longest, cutoff_sequence=cutoff)


def b_sens(window_bracket: WindowBracket | float, b_max: BMax) -> float:
    """J6: each window retains its own operative bound in the sensitivity pass."""
    operative = window_bracket.b_fiducial_s if isinstance(window_bracket, WindowBracket) else window_bracket
    return float(max(_bound(operative), _bound(b_max.value_s)))


def require_member_bound_is_window_bracket(provenance: Mapping, window_bracket: WindowBracket) -> None:
    """B1's single operative-bound check, shared by later claim consumers."""
    value = provenance.get("operative_fiducial_bound_s") if isinstance(provenance, Mapping) else None
    if not isinstance(window_bracket, WindowBracket):
        raise AnalysisRefusal("operative_bound_not_the_window_bracket")
    expected = window_bracket.b_fiducial_s
    if (type(value) not in (int, float) or not math.isfinite(value)
            or type(expected) not in (int, float) or not math.isfinite(expected) or expected < 0
            or value != expected):
        raise AnalysisRefusal("operative_bound_not_the_window_bracket")
