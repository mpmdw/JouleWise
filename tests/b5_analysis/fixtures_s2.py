"""S2 variants of S0's windows; all inputs and captures are synthetic.

S0's capture files are adapter stubs and its bracket assessment describes a
different in-memory ledger. These variants give the archived chain, endpoint
stubs and frozen evaluator one consistent identity, binding and bound pair.
Capture physics and strict validation of the marked timing-only member stubs
are explicit mock adapter seams. Selection, custody and wrapper checks are real.
"""
from __future__ import annotations

import atexit
import contextlib
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from unittest import mock

from joulewise import calibration_bracketing as br, calibration_ledger as cl
from joulewise.b5_analysis.archive import open_archive, open_attempt_record
from joulewise.b5_analysis.windows import SealPins
from joulewise.bundle_read import BundleReader
from joulewise.powermetrics_fiducial import V2_BINDING_FIELDS, PROTOCOL_ID, PROTOCOL_V3_SHA256
from joulewise.schemas import CampaignPolicy
from joulewise.uncertainty_evidence import ACTIVE_CAPTURE_ANCHOR_METHOD
from tests.b5_analysis import fixtures as s0

_CACHE = {}
_ROOTS = set()
BOUNDS = {"alpha": ("0.027", "0.02950"), "beta": ("0.029", "0.03150"),
          "gamma": ("0.028", "0.03050")}


def toy_ledger(T=502, *, changed_at=None, bounds=None):
    """A complete valid legacy receipt chain with no capture-file dependency."""
    acceptance = br.load_calibration_acceptance_bound()
    epoch = acceptance["identity_epoch"]
    t1 = {key: f"toy-{key}" for key in cl.T1_FIELDS}
    t1.update({key: value for key, value in epoch.items() if key in t1})
    rows = []
    head = cl.GENESIS_DIGEST
    for sequence in range(1, T + 1):
        number = (sequence + 1) // 2
        final = sequence % 2 == 0
        disposition = "systematic-invalid" if sequence == 456 else "valid"
        if sequence in (458, 460):
            disposition = "ordinary-invalid" if sequence == 458 else "abandoned"
        artifacts = {key: hashlib.sha256(f"{number}-{key}".encode()).hexdigest()
                     for key in cl.GOVERNED_ARTIFACTS} if final else {}
        own_epoch = dict(epoch, os_build="different") if number == 231 else epoch
        bound = "0.040" if sequence == 456 else "0.9" if sequence in (376, 458, 460, 462, 502) else "0.025"
        if changed_at == sequence:
            bound = "0.041"
        bound = (bounds or {}).get(sequence, bound)
        row = cl._new_receipt(sequence=sequence, predecessor_digest=head,
            event="finalization" if final else "reservation", attempt_id=f"toy-{number}",
            content_id=cl.content_id_from_artifact_hashes(artifacts) if final else None,
            artifacts=artifacts, identity_epoch=own_epoch, t1_bindings=t1,
            capture_wall_time_s="100.0" if final else None,
            exact_bound_lexeme_s=bound if final else None, disposition=disposition if final else "pending",
            custody_locator=f"/synthetic-s2-unreadable/toy-{number}")
        rows.append(row)
        head = row["receipt_digest"]
    return b"".join(cl.canonical_json_bytes(row) + b"\n" for row in rows)


def pin_at(raw, sequence):
    row = json.loads(raw.splitlines()[sequence - 1])
    return {"sequence": sequence, "head_digest": row["receipt_digest"], "ledger_schema": cl.LEDGER_SCHEMA}


def toy_archive(directory, raw, sequence, *, pack="gamma"):
    entry = s0.structural_archive(directory, pack=pack)
    built = s0.BuiltWindow(Path(directory).parent, Path(directory), entry.claim_runs_root, entry.bound_runs_root,
                          entry.custody_root, entry.measurement_root,
                          {key: getattr(entry, key) for key in entry.__dataclass_fields__}, 0, None, "pin4", (), ())
    # BuiltWindow.entry expects the index wire representation.
    for key, value in list(built.entry_data.items()):
        if isinstance(value, Path):
            built.entry_data[key] = str(value)
    (built.archive / "sources/ledger").mkdir(parents=True)
    (built.archive / "sources/ledger/calibration_observation_ledger.jsonl").write_bytes(raw)
    (built.archive / "sources/inputs").mkdir(parents=True)
    (built.archive / "sources/inputs/acceptance.json").write_bytes(br.DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes())
    s0.put(built.archive / "derived/terminal-pin.json", pin_at(raw, sequence))
    record_path = built.archive / "harvest.json"
    record = json.loads(record_path.read_bytes())
    record["outputs"]["derived/terminal-pin.json"] = s0.sha(built.archive / "derived/terminal-pin.json")
    s0.put(record_path, record)
    refresh(built)
    return built


def handle(built):
    """Authenticate the synthetic target and open it through real selection."""
    pins = SealPins.load()
    record = open_attempt_record(built.entry, seal_pins=pins, pack_table=s0.PACK_TABLE)
    return open_archive(s0.selected_window(record, seal_pins=pins),
                        seal_pins=pins, pack_table=s0.PACK_TABLE)


def refresh(built):
    """Rebind a counterfactual archive; preserve S0's files on disk."""
    sources = built.archive / "sources"
    (sources / "SHA256SUMS").write_text("".join(
        f"{s0.sha(path)}  {path.relative_to(sources).as_posix()}\n"
        for path in sorted(sources.rglob("*")) if path.is_file() and path != sources / "SHA256SUMS"))
    record_path = built.archive / "harvest.json"
    record = json.loads(record_path.read_bytes())
    record["archive_root"] = str(built.archive)
    record["outputs"] = {name: s0.sha(built.archive / name) for name in record["outputs"]}
    s0.put(record_path, record)
    built.entry_data["archive_root"] = str(built.archive)
    built.entry_data["harvest_record_sha256"] = s0.sha(record_path)


def fork(built, directory):
    root = Path(directory)
    archive = root / "archive"
    shutil.copytree(built.archive, archive)
    cloned = replace(built, root=root, archive=archive, entry_data=dict(built.entry_data))
    cloned.entry_data["archive_root"] = str(archive)
    refresh(cloned)
    return cloned


def _decode_capture(path, *, runs_root, mode="issuing", **_):
    path = Path(path)
    if not any(path.is_relative_to(root) for root in _ROOTS):
        raise AssertionError("S2 attempted a capture outside its synthetic roots")
    manifest = path / "manifest.json"
    evidence_path = path / "instrument_evidence.json"
    evidence = json.loads(evidence_path.read_bytes())
    assert evidence["synthetic_s2"] is True
    return br.CalibrationCandidate(str(path), s0.sha(manifest), s0.sha(evidence_path), PROTOCOL_ID,
                                   evidence["capture_wall_time_s"], evidence["b_fiducial_s"], evidence["bindings"])


@contextlib.contextmanager
def capture_adapter():
    from joulewise import cli
    real_validate = cli.validate_bundle

    def strict_stub(path, strict=False, **kwargs):
        marker = (BundleReader(path).raw_metadata() or {}).get("synthetic_s2_member")
        if marker is None:
            return real_validate(path, strict=strict, **kwargs)
        assert marker["synthetic_s2"] is True
        return [] if marker["strict_valid"] else ["synthetic S2 strict-invalid member"]

    with mock.patch.object(br, "load_calibration_candidate", side_effect=_decode_capture), \
            mock.patch.object(cli, "validate_bundle", side_effect=strict_stub):
        yield


def build_named(name):
    if name in _CACHE:
        return _CACHE[name]
    original = s0.build_named(name)
    root = Path(tempfile.mkdtemp(prefix="b5-s2-"))
    atexit.register(shutil.rmtree, root, ignore_errors=True)
    _ROOTS.add(root)
    built = fork(original, root)
    original.close()  # pin2's deterministic restored root remains available to S0 tests.
    old_claim = built.entry.claim_runs_root
    built.claim = root / "claim-runs"
    built.entry_data["claim_runs_root"] = str(built.claim)
    archive = built.archive
    acceptance = br.load_calibration_acceptance_bound(archive / "sources/inputs/acceptance.json")
    assert acceptance is not None
    roster = json.loads((archive / "sources/repo/configs/campaigns" / built.entry_data["pack_id"] / "plan_tree.json").read_bytes())
    original_ledger = archive / "sources/ledger/calibration_observation_ledger.jsonl"
    prefix = b"".join(original_ledger.read_bytes().splitlines(keepends=True)[:376])
    ledger_path, pin_path = root / "ledger.jsonl", root / "pin.json"
    ledger_path.write_bytes(prefix)
    s0.put(pin_path, {key: acceptance["ledger_cutoff"][key] for key in ("sequence", "head_digest", "ledger_schema")})
    bindings = {key: f"value-{key}" for key in V2_BINDING_FIELDS}
    bindings.update(acceptance["identity_epoch"])
    bindings.update(protocol_sha256=PROTOCOL_V3_SHA256, anchor_method_version=ACTIVE_CAPTURE_ANCHOR_METHOD)
    epoch = acceptance["identity_epoch"]
    plan = roster["plan"]
    identity = roster["window_identity"]
    old_binding = json.loads((archive / "derived/bracket-binding.json").read_bytes())

    def session(session_id, *, systematic=False, extra_valid=False):
        slots = {}
        pre_bound, post_bound = BOUNDS[built.entry_data["pack"]]
        for slot, bound, wall in (("pre", "0.044" if systematic else pre_bound, 90.0 if systematic or extra_valid else 99.0),
                                  ("post", post_bound, 92.0 if extra_valid else 111.0)):
            capture = built.claim / "instrument_validation" / f"{session_id}-{slot}"
            s0.put(capture / "manifest.json", {"synthetic_s2": True, "slot": slot, "id": session_id})
            s0.put(capture / "instrument_evidence.json", {"synthetic_s2": True,
                    "capture_wall_time_s": wall, "b_fiducial_s": bound, "bindings": bindings})
            slots[slot] = {"attempt_id": f"{session_id}-{slot}", "custody_locator": str(capture),
                           "identity_epoch": epoch, "t1_bindings": bindings}
        cl.append_bracket_session_receipt(ledger_path, session_id=session_id,
            window_id="s2-other" if systematic or extra_valid else identity["window_id"],
            plan_id="s2-other" if systematic or extra_valid else plan["plan_id"], plan_sha256=old_binding["plan_sha256"],
            evidence_root_id="s2-other" if systematic or extra_valid else identity["evidence_root_id"],
            runs_root=built.entry.claim_runs_root, slots=slots, head_pin_path=pin_path, require_committed_pin=False)
        for slot in ("pre",) if systematic else ("pre", "post"):
            evidence = json.loads((Path(slots[slot]["custody_locator"]) / "instrument_evidence.json").read_bytes())
            cl.finalize_bracket_session_slot(ledger_path, session_id=session_id, slot=slot,
                disposition="systematic-invalid" if systematic else "valid", custody_locator=slots[slot]["custody_locator"],
                artifact_sha256=cl.artifact_hashes(Path(slots[slot]["custody_locator"])), identity_epoch=epoch,
                t1_bindings=bindings, capture_wall_time_s=str(evidence["capture_wall_time_s"]),
                exact_bound_lexeme_s=evidence["b_fiducial_s"])
        if systematic:
            cl.abort_bracket_session(ledger_path, session_id=session_id, reason="synthetic_s2_systematic")
        s0.put(pin_path, cl.terminal_head_pin_for_session(ledger_path, session_id=session_id))

    if built.entry_data["pack"] == "gamma":
        session("s2-other-session", systematic=True)
        session("s2-extra-valid", extra_valid=True)
    session(old_binding["session_id"])
    snapshot = cl.load_calibration_ledger_snapshot(ledger_path, pin_path, require_committed_pin=False,
        verify_custody=False, baseline_sequence=376, baseline_digest=acceptance["ledger_cutoff"]["head_digest"])
    assert snapshot.valid, snapshot.refusal_reasons
    binding = br.build_calibration_bracket_binding(snapshot, session_id=old_binding["session_id"],
        window_id=identity["window_id"], plan_id=plan["plan_id"], plan_sha256=old_binding["plan_sha256"],
        evidence_root_id=identity["evidence_root_id"], runs_root=built.entry.claim_runs_root)
    s0.put(archive / "derived/bracket-binding.json", binding)
    s0.put(archive / "derived/terminal-pin.json", json.loads(pin_path.read_bytes()))
    original_ledger.write_bytes(ledger_path.read_bytes())
    # All selected members carry the same mock window and the current T1 vector.
    # No summary/energy is used to define the bracket.
    assessments = json.loads((archive / "withheld/member-assessments.json").read_bytes())
    for member in assessments["members"].values():
        path = Path(member["bundle_path"])
        if not path.is_relative_to(old_claim):
            continue
        relative = path.relative_to(old_claim)
        member["bundle_path"] = str(built.claim / relative)
        source = archive / "sources/claim-runs" / relative
        if not source.is_dir():
            continue
        metadata = json.loads((source / "metadata.json").read_bytes())
        metadata.setdefault("instrument_calibration", {})["bindings"] = bindings
        metadata["synthetic_s2_member"] = {"synthetic_s2": True, "strict_valid": bool(member.get("strict_valid"))}
        s0.put(source / "metadata.json", metadata)
        (source / "events.jsonl").write_text("".join(json.dumps({"event_type": event, "phase": "measured_run",
            "timestamp_s": wall, "message": "synthetic S2 marker", "metadata": {}}) + "\n"
            for event, wall in (("sampling_started", 100.0), ("sampling_stopped", 110.0))))
        assert BundleReader(source).measured_window() is not None
    s0.put(archive / "withheld/member-assessments.json", assessments)
    policy = CampaignPolicy.from_mapping(json.loads((archive / "sources/repo" / roster["campaign_policy"]["path"]).read_bytes()))
    with capture_adapter():
        candidates = br.discover_calibration_candidates(snapshot)
        assessment, reasons = br.evaluate_calibration_bracket(candidates, window_start_s=100.0, window_end_s=110.0,
            bindings=bindings, policy=policy.calibration_bracketing, acceptance_bound=acceptance, ledger_snapshot=snapshot,
            bracket_binding=binding, bracket_window_id=identity["window_id"], bracket_plan_id=plan["plan_id"],
            bracket_plan_sha256=old_binding["plan_sha256"], bracket_evidence_root_id=identity["evidence_root_id"],
            bracket_runs_root=built.entry.claim_runs_root, trigger_scope="sealed" if built.shape == "pin2" else "window_evidence")
    assert assessment["status"] == "passed", reasons
    s0.put(archive / "withheld/bracket-evaluation.json", {"assessment": assessment, "reasons": list(reasons), "members": 50})
    record_path = archive / "harvest.json"
    record = json.loads(record_path.read_bytes())
    if "calibration_bracket" in record:
        prospective = assessment["acceptance"]["prospective_rederivation"]
        record["calibration_bracket"].update(status=assessment["status"], reasons=list(reasons),
            freshness=assessment["acceptance"]["freshness"]["status"],
            observed_triggers=prospective["observed_triggers"], recorded_only_triggers=prospective["recorded_only_triggers"],
            corpus_doubling=prospective["corpus_doubling"], other_session_systematic_sequences=prospective["other_session_systematic_sequences"])
        s0.put(record_path, record)
    refresh(built)
    _CACHE[name] = built
    return built
