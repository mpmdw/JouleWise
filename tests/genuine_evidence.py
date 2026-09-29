"""Attach replayable physical-telemetry evidence without changing gate functions.

The evidence is synthetic test data, never a live hardware validation. Summary
values remain owned by the caller; whole-window raw re-derivation is deliberately
free to reject a summary that disagrees with its primary trace.
"""
from __future__ import annotations

import copy
import csv
import contextlib
from contextvars import ContextVar
from unittest.mock import patch
from functools import lru_cache, wraps
import hashlib
import json
from pathlib import Path
import shutil

from joulewise.bundle_read import BundleReader
from joulewise.environment import evaluate_environment_policy
from joulewise.schemas import BenchmarkConfig, CampaignPolicy
from tests.bfgs_fixtures import rebind_config, write_passing_pair

FIXTURES = Path(__file__).parent / "fixtures"
SEED = FIXTURES / "d117_v2_production" / "strict_seed_bundle"
_BUILDERS_ACTIVE = ContextVar("genuine_evidence_builders_active", default=False)
_CHARGING = ContextVar("genuine_evidence_charging", default=False)
POLICY = Path(__file__).resolve().parents[1] / "configs/campaign_policies/quiet_mac_p2_production.json"


def _read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


@lru_cache(maxsize=1)
def _current_primary() -> tuple[bytes, dict]:
    """Generate the seed stream once; callers receive independent metadata."""
    import plistlib
    from tests.test_powermetrics import documents_to_stream, energy_consistent, rebased_documents
    from joulewise.adapters.powermetrics import parse_powermetrics_records, anchor_records_from_powermetrics
    from joulewise.uncertainty_evidence import derive_powermetrics_anchor_v3, stamp_from_mapping
    anchor = _read(SEED / "metadata.json")["uncertainty_evidence"]["clock_anchor"]
    raw_path = SEED / "raw/powermetrics.plist"
    source = [plistlib.loads(part) for part in raw_path.read_bytes().split(b"\0") if part.strip()]
    # Preserve the measured rails and native wire, omitting unrelated per-CPU
    # inventory. The production parser consumes these fields directly.
    documents = []
    for index, original in enumerate(source):
        row = {key: copy.deepcopy(original[key]) for key in
               ("elapsed_ns", "timestamp", "is_delta", "thermal_pressure")}
        row["processor"] = {key: original["processor"][key] for key in
                            ("cpu_power", "gpu_power", "ane_power",
                             "cpu_energy", "gpu_energy", "ane_energy")}
        # Keep record zero's causal duration. Split later averaging supports
        # into four energy-consistent observations for the short seed window.
        parts = 1 if index == 0 else 4
        duration, remainder = divmod(row["elapsed_ns"], parts)
        for part in range(parts):
            split = copy.deepcopy(row)
            split["elapsed_ns"] = duration + (part < remainder)
            documents.append(energy_consistent(split))
    # Current clock fitting requires a >=60 s native-stamp span; this tail is
    # outside the measured window and cannot add measured energy or samples.
    for _ in range(62):
        extension = copy.deepcopy(documents[-1])
        extension["elapsed_ns"] = 1_000_000_000
        documents.append(energy_consistent(extension))
    documents = rebased_documents(documents, first_endpoint_s=anchor["first_sample_end_point_epoch_s"])
    raw = documents_to_stream(documents)
    from dataclasses import asdict
    from joulewise.clock import ClockStamp
    endpoint = anchor["first_sample_end_point_epoch_s"]
    times = {
        "pre_spawn": endpoint - documents[0]["elapsed_ns"] / 1e9 - 0.001,
        "first_parse": endpoint + 0.001,
        "sampling_started": anchor["clock_stamps"]["sampling_started"]["epoch_s"],
        "sampling_stopped": anchor["clock_stamps"]["sampling_stopped"]["epoch_s"],
        "post_parse": endpoint + sum(row["elapsed_ns"] for row in documents[1:]) / 1e9 + 0.1,
    }
    stamps = {name: asdict(ClockStamp(t, t - endpoint, t - endpoint + 1e-6, 1e-6, 1e-6)) for name, t in times.items()}
    current_anchor = derive_powermetrics_anchor_v3(
        stamps={name: stamp_from_mapping(value) for name, value in stamps.items()},
        records=anchor_records_from_powermetrics(parse_powermetrics_records(raw)),
    )
    return raw, current_anchor


def write_genuine_evidence(bundle: Path | str) -> None:
    """Bind a bundle to a physical config, primary admission data and a pair.

    Existing configs and raw measured traces are preserved. Summary-only
    fixtures retain their numbers; controller summaries are freshly rederived.
    Missing primary surfaces come from the checked-in
    current-era strict seed. This helper never exempts a production predicate.
    Call it while building the fixture, before hashing manifests or bundles.
    """
    root = Path(bundle)
    seed_metadata = _read(SEED / "metadata.json")
    metadata_path = root / "metadata.json"
    metadata = _read(metadata_path) if metadata_path.exists() else {}
    config_path = root / "config.json"
    config = _read(config_path) if config_path.exists() else _read(FIXTURES / "d078_r01/config.json")
    config["run_id"] = metadata.get("run_id", root.name)
    config["hardware_target"]["telemetry_backend"] = "powermetrics"
    BenchmarkConfig.from_mapping(config).validate()
    _write(config_path, config)
    metadata["run_id"] = config["run_id"]
    metadata.setdefault("adapters", {}).setdefault("telemetry", {})["name"] = "powermetrics"
    copied_primary = not (root / "raw/powermetrics.plist").exists()
    # Keep primary measurement evidence intact when the controller wrote it.
    for name in ("events.jsonl", "power_trace.csv", "rich_telemetry.jsonl",
                 "rich_telemetry_idle.jsonl", "rich_telemetry_idle_post.jsonl",
                 "raw/powermetrics.plist", "raw/powermetrics_idle.plist",
                 "raw/powermetrics_idle_post.plist"):
        target = root / name
        if not target.exists() or (name == "events.jsonl" and not any(
            json.loads(line).get("event_type") == "sampling_started"
            for line in target.read_text().splitlines() if line.strip()
        )):
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SEED / name, target)
    for name in ("uncertainty_evidence", "environment", "environment_admission",
                 "campaign_policy", "campaign_environment_preflight", "idle_baseline", "device"):
        if name not in metadata or (name == "uncertainty_evidence" and
                                  "clock_stamps" not in metadata[name].get("clock_anchor", {})):
            metadata[name] = copy.deepcopy(seed_metadata[name])
    if copied_primary:
        raw, anchor = _current_primary()
        (root / "raw/powermetrics.plist").write_bytes(raw)
        metadata["uncertainty_evidence"]["clock_anchor"] = copy.deepcopy(anchor)
        from joulewise.adapters.powermetrics import samples_from_raw_powermetrics, rich_telemetry_jsonl
        endpoint = anchor["first_sample_end_point_epoch_s"]
        samples = samples_from_raw_powermetrics(raw, first_record_endpoint_s=endpoint)
        with (root / "power_trace.csv").open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(("timestamp_s", "power_w", "source", "rail", "interval_start_s", "interval_end_s"))
            writer.writerows((sample.timestamp_s, sample.power_w, sample.source, sample.rail,
                             sample.interval_start_s, sample.interval_end_s) for sample in samples)
        (root / "rich_telemetry.jsonl").write_text(
            rich_telemetry_jsonl(raw, first_record_endpoint_s=endpoint), encoding="utf-8",
        )
    policy = CampaignPolicy.from_mapping(_read(POLICY))
    metadata["campaign_policy"] = {"sha256": hashlib.sha256(POLICY.read_bytes()).hexdigest()}
    admission = metadata["environment_admission"]
    snapshot = copy.deepcopy(seed_metadata["environment_admission"]["per_run_environment_evaluation"]["snapshot"])
    evaluation = evaluate_environment_policy(snapshot, policy.environment_guard)
    evaluation["snapshot"] = snapshot
    if "snapshot" not in admission.get("per_run_environment_evaluation", {}):
        admission["per_run_environment_evaluation"] = evaluation
    # Old seed builds predate embedded snapshot re-evaluation. Always emit the
    # evaluator's result when copying its positive admission evidence.
    if admission == seed_metadata["environment_admission"]:
        admission["per_run_environment_evaluation"] = evaluation
    # The seed's top-level snapshot contains only external_connected; whole
    # window continuity also reads its adapter wattage and description.
    power = metadata["environment"].setdefault("power", {})
    power.setdefault("adapter_watts", 140.0)
    power.setdefault("adapter_description", "synthetic adapter")
    metadata["environment"].setdefault("post_run_observation", copy.deepcopy(seed_metadata["environment"]["post_run_observation"]))
    _write(metadata_path, metadata)
    for name in ("summary_metrics.json", "summary.json"):
        path = root / name
        if path.exists():
            summary = _read(path)
            summary.setdefault("summary_provenance", {}).setdefault("reducer_version", "0.5.2")
            summary.setdefault("measurement_quality", {})["telemetry_source"] = "powermetrics"
            summary.setdefault("energy_uncertainty_status", "bounded")
            _write(path, summary)
    events_path = root / "events.jsonl"
    events = [json.loads(line) for line in events_path.read_text().splitlines() if line.strip()]
    for event in events:
        if event.get("phase") in {"idle_baseline", "idle_drift_sentinel"}:
            event.setdefault("metadata", {}).setdefault("monotonic_ns", round(event["timestamp_s"] * 1e9))
    events_path.write_text("".join(json.dumps(event, sort_keys=True) + "\n" for event in events), encoding="utf-8")
    rebind_config(root)
    write_passing_pair(root)
    window = BundleReader(root).measured_window()
    metadata = _read(metadata_path)
    metadata["environment"]["post_run_observation"]["captured_at_s"] = window.end_s
    _write(metadata_path, metadata)
    if not copied_primary:
        from joulewise.reduce import reduce_bundle
        summary_path = root / "summary_metrics.json"
        summary = _read(summary_path)
        if "summary_schema_version" in summary.get("summary_provenance", {}):
            version = summary.get("summary_provenance", {}).get("reducer_version", "0.5.2")
            _write(summary_path, reduce_bundle(root, reducer_version=version).to_dict())


@contextlib.contextmanager
def genuine_evidence_builders(*, charging=False, extend_whole_window=True):
    """Replace test fixture builders, never production refusal functions."""
    if _BUILDERS_ACTIVE.get():
        if charging and not _CHARGING.get():
            raise ValueError("charging control must wrap the outer fixture context")
        yield
        return
    from tests import test_floor_extraction as floor, test_analysis_integration as analysis, test_analysis_finalizer as finalizer
    from tests.bfgs_fixtures import write_charging_pair

    def attach(bundle):
        write_genuine_evidence(bundle)
        if extend_whole_window and Path(bundle).name.endswith(("-neg8-reference-start", "-neg8-reference-end")):
            write_genuine_reference(bundle)
        if charging:
            write_charging_pair(bundle)

    charging = charging or _CHARGING.get()
    token = _CHARGING.set(charging)
    active_token = _BUILDERS_ACTIVE.set(True)
    original_pair = floor.write_passing_pair
    original_produce = analysis.produce_strict_bundle
    original_row = floor.CpuAndWholeWindowClaimBarrierTests._whole_window_row
    original_install = analysis.install_passing_analysis_whole_window
    original_finalization = analysis.install_synthetic_finalization_fixture

    def finalization(*args, **kwargs):
        fixture = original_finalization(*args, **kwargs)
        artifact = _read(fixture["floor_path"])
        member_ids = set()
        for cell in artifact["cells"]:
            member_ids.update(row["bundle_id"] for row in cell["absolute"]["bundle_observations"])
            member_ids.update(member["bundle_id"] for block in cell["comparative"]["blocks"] for member in block["members"])
        for bundle_id in sorted(member_ids):
            bundle = Path(fixture["runs_root"]) / bundle_id
            if not bundle.exists():
                bundle.mkdir()
                attach(bundle)
                write_genuine_reference(bundle)
                if charging:
                    write_charging_pair(bundle)
        return fixture

    def row(root, bundle_ids, **kwargs):
        value = original_row(root, bundle_ids, **kwargs)
        # Some callers evaluate the row argument before constructing members.
        # Leave the positive fixture shape intact until all data are present.
        if all((Path(root) / bundle_id / "metadata.json").exists() for bundle_id in bundle_ids):
            populate_whole_window_core(root, value)
        return value

    def install(root, *args, **kwargs):
        original_install(root, *args, **kwargs)
        from joulewise.whole_window import (
            _scientific_config_identity, build_row_provenance, source_manifest_descriptors,
        )
        source = Path(root) / "campaign_manifests" / (kwargs["source_name"] + ".json")
        manifest = _read(source)
        for member in manifest["members"]:
            if member.get("role") in {"neg8_daily_reference_start", "neg8_daily_reference_end"}:
                digest, canonical = _scientific_config_identity(Path(root) / member["bundle_ids"][0])
                member["canonical_neg8_workload"] = canonical
                member["scientific_config_sha256"] = digest
        _write(source, manifest)
        log = Path(root) / "campaign_log.jsonl"
        rows = [json.loads(line) for line in log.read_text().splitlines() if line.strip()]
        for index, value in enumerate(rows):
            if "campaign_provenance_manifest_sha256" in value:
                from joulewise.campaign_provenance import campaign_provenance_attestation
                rows[index] = campaign_provenance_attestation(
                    manifest_path=source, raw_manifest_bytes=source.read_bytes(),
                    manifest=manifest, timestamp=value["timestamp"],
                )
            if "idle_admission_core" in value:
                populate_whole_window_core(Path(root), value)
                value["row_provenance"] = build_row_provenance(
                    policy_sha256=value["campaign_policy"]["sha256"],
                    bundle_ids=value["bundle_ids"],
                    source_manifests=source_manifest_descriptors(Path(root), [source]),
                )
        log.write_text("".join(json.dumps(value, sort_keys=True) + "\n" for value in rows))

    def bind(root, bundle_id):
        # The helper subsumes the original positive config/battery builder.
        attach(root / bundle_id)

    def pair(bundle):
        original_pair(bundle)
        attach(bundle)

    def produce(*args, **kwargs):
        bundle = original_produce(*args, **kwargs)
        attach(bundle)
        return bundle

    with (
        patch.object(floor, "bind_passing_claim_bundle", bind),
        patch.object(floor, "write_passing_pair", pair),
        patch.object(analysis, "write_passing_pair", pair),
        patch.object(finalizer, "write_passing_pair", pair),
        patch.object(analysis, "produce_strict_bundle", produce),
        patch.object(analysis, "install_passing_analysis_whole_window", install if extend_whole_window else original_install),
        patch.object(analysis, "install_synthetic_finalization_fixture", finalization if extend_whole_window else original_finalization),
        patch.object(floor.CpuAndWholeWindowClaimBarrierTests, "_whole_window_row", staticmethod(row if extend_whole_window else original_row)),
    ):
        try:
            yield
        finally:
            _CHARGING.reset(token)
            _BUILDERS_ACTIVE.reset(active_token)



def populate_whole_window_core(root: Path, row: dict) -> dict:
    """Fill a test verdict's CPU/adapter ledger from its actual bundle bytes.

    Preserve negative decisions and NEG-8/calibration claims so real validators
    still reject disagreement or missing authority. This does not mint policy,
    calibration acceptance or a drift bound on behalf of the fixture.
    """
    from joulewise.idle_admission import (
        IdleAdmissionExtension, evaluate_cpu_idle_admission,
        evaluate_adapter_wattage_continuity,
    )
    from joulewise.whole_window import _adapter_observations, _load_idle_records

    policy = _read(POLICY)
    extension = IdleAdmissionExtension.from_mapping(
        policy["idle_admission_extension"], profile=policy["profile"],
    )
    core = row["idle_admission_core"]
    observations = []
    members = []
    for bundle_id in row["bundle_ids"]:
        bundle = root / bundle_id
        if not (bundle / "metadata.json").exists():
            continue  # A missing member is deliberate in several regression tests.
        metadata = _read(bundle / "metadata.json")
        admission = metadata.get("environment_admission", {})
        attempts = admission.get("attempts", [])
        final = attempts[-1] if attempts else {}
        cpu = evaluate_cpu_idle_admission(
            _load_idle_records(bundle, final.get("attempt", 1)),
            extension.cpu_criteria, gpu_admitted=admission.get("decision") == "admitted",
        )
        members.append({"bundle_id": bundle_id, "cpu_admission": cpu})
        observations.extend(_adapter_observations(bundle_id, metadata))
    core["members"] = members
    continuity = evaluate_adapter_wattage_continuity(observations, extension.adapter_wattage)
    if core.get("adapter_wattage_continuity", {}).get("decision") == "failed":
        continuity["decision"] = "failed"
    core["adapter_wattage_continuity"] = continuity
    return row


def write_genuine_reference(bundle: Path | str) -> None:
    """Produce a canonical NEG-8 reference with a freshly reduced summary.

    This supplies primary-energy and scientific-config evidence, not a drift
    bound, issuance record, or calibration acceptance. Those remain real gates.
    """
    from joulewise.reduce import reduce_bundle

    root = Path(bundle)
    config = _read(root / "config.json")
    config["workload_profile"].update(
        name="df_rq_mid", prompt_tokens=1024, output_tokens=256,
        dataset_ref=None, suite_manifest_ref=None,
    )
    _write(root / "config.json", config)
    rebind_config(root)
    write_passing_pair(root)
    _write(root / "summary_metrics.json", reduce_bundle(root, reducer_version="0.5.2").to_dict())


def genuine_evidence_is_active() -> bool:
    """Let a fixture finish its deferred row after constructing its members."""
    return _BUILDERS_ACTIVE.get()


def genuine_evidence_test(method):
    """Enter fixture construction before a method's first builder call."""
    @wraps(method)
    def run(*args, **kwargs):
        with genuine_evidence_builders():
            return method(*args, **kwargs)
    return run
