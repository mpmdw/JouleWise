"""S3 synthetic windows, built once by the unchanged HEAD program.

The persistent scratch cache avoids rebuilding multi-minute windows in every
test. The child runs a git-archive of HEAD, including S0's real writer/harvest
fixture builder, so its program-hash fence remains active.
"""
import atexit
import contextlib
import copy
from dataclasses import replace
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
from unittest import mock

from joulewise import whole_window as ww
from tests.b5_analysis import fixtures as s0

ROOT = s0.ROOT
SCRATCH = ROOT / ".scratch-s3"
PYTHON = "/opt/homebrew/bin/python3.13"
_CACHE = {}
_WINDOW_CACHE = {}
_ENVIRONMENT_CACHE = {}


def cached(name="BETA_STD"):
    if name in _CACHE:
        return _CACHE[name]
    SCRATCH.mkdir(exist_ok=True)
    cache = SCRATCH / "windows"
    cache.mkdir(exist_ok=True)
    index = cache / (name + ".json")
    blob = cache / (name + ".tar")
    if not index.exists() or not blob.exists():
        export = SCRATCH / "base-tree"
        if not export.exists():
            export.mkdir()
            raw = subprocess.check_output(["git", "archive", "HEAD"], cwd=ROOT)
            with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
                archive.extractall(export, filter="data")
        script = '''import json, sys, tarfile
from pathlib import Path
from tests.b5_analysis import fixtures as fx
name, cache = sys.argv[1], Path(sys.argv[2])
with fx.build_named(name) as window:
    with tarfile.open(cache / (name + ".tar"), "w") as archive:
        archive.add(window.root, arcname=window.root.name)
    (cache / (name + ".json")).write_text(json.dumps(window.entry_data))
'''
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "TMPDIR": "/private/tmp"}
        subprocess.run([PYTHON, "-c", script, name, str(cache)], cwd=export, env=env, check=True)
    data = json.loads(index.read_text())
    root = Path(data["archive_root"]).parent
    if root.parent != Path("/private/tmp") or not root.name.startswith("b5-s0-") or root.exists():
        raise ValueError("synthetic original fixture root unavailable")
    with tarfile.open(blob) as archive:
        archive.extractall(root.parent, filter="data")
    atexit.register(shutil.rmtree, root, ignore_errors=True)
    row = json.loads((Path(data["claim_runs_root"]) / "whole-window-verdict.json").read_text())
    window = s0.BuiltWindow(root, Path(data["archive_root"]), Path(data["claim_runs_root"]),
        Path(data["bound_runs_root"]), Path(data["custody_root"]), Path(data["measurement_root"]),
        data, 1 if row["status"] == "failed" else 0, row, "pin2" if name.startswith("ALPHA") else "pin4", (), ())
    from joulewise.b5_analysis.archive import open_archive, open_attempt_record
    from joulewise.b5_analysis.windows import SealPins
    pins = SealPins.load()
    record = open_attempt_record(window.entry, seal_pins=pins, pack_table=s0.PACK_TABLE)
    open_archive(s0.selected_window(record, seal_pins=pins), seal_pins=pins, pack_table=s0.PACK_TABLE)
    _CACHE[name] = window
    return window


def context(window, **changes):
    archive = window.archive
    roster = json.loads((archive / "derived/roster.json").read_text())
    screen = json.loads((archive / "derived/neg8-screen.json").read_text())
    # S0's small mock plan labels these auxiliary runs by stage instead of
    # production's neg8_slot. Part A takes a hand-built context, so use the
    # fixture's explicit registered reference identities, never energy values.
    from tests import test_harvest_b5_window as hb
    refs = {bundle: role.rsplit("_", 1)[1] for bundle, role in hb.NEG8_REFERENCES}
    for path in (window.claim / "campaign_manifests").glob("*.json"):
        manifest = json.loads(path.read_text())
        for member in manifest.get("members", []):
            slot = ww._neg8_position(member.get("role"), member.get("sentinel_position"))
            if slot in ("start", "midpoint", "end"):
                refs.update({bundle: slot for bundle in member.get("bundle_ids", [])})
    for member in roster["members"]:
        slot = member.get("neg8_slot") or member.get("spare_slot")
        if slot in ("start", "midpoint", "end"):
            refs[member["run_id"]] = slot
    basis_ids = {m["bundle_id"] for m in window.writer_row["evaluation_basis"]["member_occurrences"]}
    losses = set(screen.get("harvest_reference_losses", {})) | {
        m["bundle_id"] for m in screen.get("rescreen", {}).get("survivors", {}).get("reference_losses", [])}
    excluded = json.loads((archive / "derived/exclusions.json").read_text())
    removed = {m["run_id"] for m in excluded["members_excluded"]}
    for cell in excluded.get("cells", []):
        for unit in cell.get("units", []):
            if not unit.get("kept", True):
                removed.update(unit.get("run_ids", []))
    wrapper = json.loads((archive / "withheld/bracket-evaluation.json").read_text())
    assessment = {**wrapper["assessment"], "reasons": wrapper["reasons"]}
    values = dict(neg8_harvest_archive=archive, window_bracket=assessment,
        governed_e3=not window.entry_data["pack"] == "alpha", removed_bundle_ids=frozenset(removed),
        roster_references=refs, survivor_bundle_ids=frozenset(refs.keys() & basis_ids - losses))
    values.update(changes)
    return ww.ArchiveContext(**values)


class Case:
    """Cheap authenticated archive copy; bundle bytes remain synthetic inputs."""
    def __init__(self, name="BETA_STD"):
        self.window = cached(name)
        self.tmp = tempfile.TemporaryDirectory(prefix="b5-s3-case-")
        self.archive = Path(self.tmp.name) / "archive"
        self.archive.mkdir()
        # Only validator inputs: copying the archived raw bundles (over a GB)
        # per counterfactual adds no evidence and exhausts the test disk.
        for relative in ("harvest.json", "derived/roster.json", "derived/exclusions.json", "derived/neg8-screen.json",
                ww.NEG8_HARVEST_ALLOWANCE_RECORD, ww.NEG8_HARVEST_CLEAN_CORPUS, ww.NEG8_HARVEST_CLEAN_BOUND,
                ww.NEG8_HARVEST_SURVIVOR_BRACKET, "withheld/bracket-evaluation.json"):
            target = self.archive / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.window.archive / relative, target)
        self.row = copy.deepcopy(self.window.writer_row)
        self.harvest = json.loads((self.archive / "harvest.json").read_text())
        self.context = replace(context(self.window), neg8_harvest_archive=self.archive)
        # S0's mock writer has no calibration candidate and emits the missing
        # bracket code. Model E3's sealed-writer stale condition explicitly;
        # ungoverned fixtures use their authenticated archived assessment.
        core = self.row["idle_admission_core"]
        conditions = set(core["conditions"])
        conditions.discard("instrument_calibration_bracket_missing")
        if self.context.governed_e3:
            conditions.add("calibration_acceptance_bound_stale")
        else:
            core["instrument_calibration_bracket"] = ww._archive_window_assessment(self.context)
            self.row["evaluation_basis"]["calibration_bracket_set"] = ww._calibration_bracket_basis(
                core["instrument_calibration_bracket"])
            self.rehash_basis()
        core["conditions"] = sorted(conditions)
        # S0 writer replaced admission metadata with a mock adapter projection
        # (two adapter observations/member); original bundles retain guards.
        # This hand-built S3 row authenticates the actual mock bundle record.
        self.rederive_continuity()
        self.bind_row()

    def read(self, relative):
        return json.loads((self.archive / relative).read_text())

    def write(self, relative, value, *, authenticate=True):
        s0.put(self.archive / relative, value)
        if authenticate:
            self.harvest["outputs"][relative] = s0.sha(self.archive / relative)
            s0.put(self.archive / "harvest.json", self.harvest)

    def bind_row(self):
        record = self.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
        record["verdict"]["row_sha256"] = ww.canonical_sha256(self.row)
        record["verdict"]["evaluation_basis_sha256"] = self.row["evaluation_basis"]["sha256"]
        self.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, record)

    def rehash_basis(self):
        basis = self.row["evaluation_basis"]
        basis["sha256"] = ww.canonical_sha256({key: value for key, value in basis.items() if key != "sha256"})

    def rederive_continuity(self):
        extension = ww.IdleAdmissionExtension.from_mapping(
            ww._registered_policy(self.row["campaign_policy"]["sha256"])["idle_admission_extension"], profile="production")
        observations = [observation for bundle in self.row["bundle_ids"]
            for observation in ww._adapter_observations(bundle,
                json.loads((self.window.claim / bundle / "metadata.json").read_text()))]
        self.row["idle_admission_core"]["adapter_wattage_continuity"] = ww.evaluate_adapter_wattage_continuity(
            observations, extension.adapter_wattage)
        core = self.row["idle_admission_core"]
        core["conditions"] = sorted(set(core["conditions"]) | set(core["adapter_wattage_continuity"]["conditions"]))

    def remove_science_member(self, bundle_id):
        from joulewise.flags.catalog import load_catalog
        from joulewise.flags.exclusions import compute
        roster = self.read("derived/roster.json")
        flag = {"flag_id": "s3-admission-failure", "code": "member.whole_window_member_failure",
            "scope": {"level": "member", "plan_id": roster["plan_id"], "attempt": roster["attempt"],
                "run_id": bundle_id, "bundle_id": None, "stage_id": None}, "interval": {"monotonic_ns": None}}
        doc = compute([flag], roster, {}, load_catalog(ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json"))
        self.write("derived/exclusions.json", doc)
        member = next(item for item in roster["members"] if item["run_id"] == bundle_id)
        removed_units = {(item["cell_id"], item["stratum"], item["unit_id"]) for item in member["units"]}
        removed = {item["run_id"] for item in doc["members_excluded"]}
        removed.update(item["run_id"] for item in roster["members"] if any(
            (unit["cell_id"], unit["stratum"], unit["unit_id"]) in removed_units for unit in item["units"]))
        self.context = replace(self.context, removed_bundle_ids=frozenset(removed))

    def lose_reference(self, bundle_id):
        from joulewise.b5 import harvest
        screen = self.read("derived/neg8-screen.json")
        losses = {**screen.get("harvest_reference_losses", {}), bundle_id: "contention.request_overlap"}
        wrapper = self.read(ww.NEG8_HARVEST_SURVIVOR_BRACKET)
        original = wrapper["bracket"]
        sources = harvest.verdict_neg8_sources(self.row, self.window.claim)
        if isinstance(sources, str):
            raise ValueError(sources)
        manifests, current, policy = sources
        with adapter_projection(self):
            bracket, problem = ww._derived_neg8_decision(manifests, self.window.claim, policy,
                current=current, point_drift=True, drift_bound_artifact=original["drift_bound_artifact"],
                return_bracket=True, freshness_evaluated_at_s=original["bound_freshness"]["evaluated_at_s"],
                exclude_bundle_ids=losses, unreadable_energy="lost")
        if problem is not None:
            raise ValueError(problem)
        wrapper["bracket"] = bracket
        self.write(ww.NEG8_HARVEST_SURVIVOR_BRACKET, wrapper)
        record = self.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
        record["survivor_bracket"]["sha256"] = s0.sha(self.archive / ww.NEG8_HARVEST_SURVIVOR_BRACKET)
        self.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, record)
        screen["harvest_reference_losses"] = losses
        screen["rescreen"]["survivors"] = {key: bracket[key] for key in ("endpoint_protocol", "reference_counts",
            "planned_reference_counts", "reference_losses", "midpoint_lost", "survivor_screen") if key in bracket}
        self.write("derived/neg8-screen.json", screen)
        self.context = replace(self.context, survivor_bundle_ids=self.context.survivor_bundle_ids - {bundle_id})

    def mutate_metadata(self, bundle_id, transform):
        """Change only owned synthetic bytes, restored when the case closes."""
        path = self.window.claim / bundle_id / "metadata.json"
        original = path.read_bytes()
        self._restore = getattr(self, "_restore", [])
        self._restore.append((path, original))
        value = json.loads(original)
        transform(value)
        s0.put(path, value)
        occurrence = next(item for item in self.row["evaluation_basis"]["member_occurrences"] if item["bundle_id"] == bundle_id)
        occurrence["metadata_sha256"] = s0.sha(path)
        self.rehash_basis()

    def mutate_config(self, bundle_id, transform):
        path = self.window.claim / bundle_id / "config.json"
        self._restore = getattr(self, "_restore", [])
        self._restore.append((path, path.read_bytes()))
        value = json.loads(path.read_text())
        transform(value)
        s0.put(path, value)
        digest = s0.sha(path)
        next(item for item in self.row["evaluation_basis"]["member_occurrences"] if item["bundle_id"] == bundle_id)["config_sha256"] = digest
        self.mutate_metadata(bundle_id, lambda metadata: metadata.update(config_sha256=digest))

    def admission_failure(self, bundle_id):
        # A succeeded member, included by the writer, whose CPU/environment
        # admission failed. Real algorithms consume these synthetic bytes.
        self.mutate_metadata(bundle_id, lambda value: value["environment_admission"].update(
            critical_environment_passed=False, decision="flagged"))
        from tests import test_run_campaign as tr
        from scripts import run_campaign as rc
        extension = ww.IdleAdmissionExtension.from_mapping(
            ww._registered_policy(self.row["campaign_policy"]["sha256"])["idle_admission_extension"], profile="production")
        cpu = ww.evaluate_cpu_idle_admission(tr._clean_idle_records(300), extension.cpu_criteria, gpu_admitted=False)
        core = self.row["idle_admission_core"]
        next(item for item in core["members"] if item["bundle_id"] == bundle_id)["cpu_admission"] = cpu
        codes = set(cpu["conditions"]) | {"environment_admission_failed"}
        self.row["member_failures"] = sorted([rc._member_failure_record(bundle_id, code, "synthetic included admission failure")
            for code in codes], key=lambda item: (item["member_id"], item["reason_code"], item["detail"]))
        core["conditions"] = sorted(set(core["conditions"]) | codes)
        self.bind_row()

    def session(self, context=None):
        from joulewise.calibration_ledger import CalibrationLedgerSnapshot, LEDGER_SCHEMA
        # No live ledger read. Validator-only tests use a named ready-session
        # double; session preparation and issuance are downstream stage work.
        snapshot = CalibrationLedgerSnapshot(LEDGER_SCHEMA, self.archive / "sources/ledger/calibration_observation_ledger.jsonl",
            0, "0" * 64, (), (), ())
        session = ww.AuthenticatedConsumptionSession(self.window.claim, set(self.row["bundle_ids"]),
            evaluation_basis_sha256=self.row["evaluation_basis"]["sha256"],
            calibration_ledger_snapshot=snapshot, archive_context=context or self.context)
        session._prepared = True
        session._preparation_identity = tuple(sorted((bundle, str((self.window.claim / bundle).resolve()))
            for bundle in self.row["bundle_ids"]))
        session.calibration_bracket = ww._archive_window_assessment(context or self.context)
        session.operative_fiducial_bound_s = (session.calibration_bracket.get("b_fiducial_s")
            if isinstance(session.calibration_bracket, dict) else None)
        return session

    def close(self):
        for path, raw in reversed(getattr(self, "_restore", [])):
            path.write_bytes(raw)
        self.tmp.cleanup()


@contextlib.contextmanager
def adapter_projection(case, *, metadata_edits=None):
    """S0 writer's mock admission projection, applied to real re-derivation.

    CPU/environment/adapter algorithms and validator execute; telemetry reads
    are the synthetic mock adapter's observations, as in fixtures.py.
    """
    from tests import test_run_campaign as rc_tests
    from tests import test_harvest_b5_window as hb
    real_window = ww.BundleReader.measured_window
    real_environment = ww.current_environment_refusals
    def measured(reader):
        # The fixtures change admission/lineage only; trace bytes never move.
        path = reader._path
        key = str(path)
        if key not in _WINDOW_CACHE:
            _WINDOW_CACHE[key] = real_window(reader)
        return _WINDOW_CACHE[key]
    def environment(metadata, **kwargs):
        # This real check scans the large synthetic raw powermetrics trace.
        # Reuse it only for identical metadata and boundary arguments. A
        # changed admission record always executes the real check afresh.
        key = (ww.canonical_sha256(metadata), tuple(sorted((name, str(value)) for name, value in kwargs.items())))
        if key not in _ENVIRONMENT_CACHE:
            _ENVIRONMENT_CACHE[key] = real_environment(metadata, **kwargs)
        return _ENVIRONMENT_CACHE[key]
    with contextlib.ExitStack() as stack:
        stack.enter_context(hb.neg8_reference_gates({bundle: 100.0 for bundle, _ in hb.NEG8_REFERENCES}))
        stack.enter_context(mock.patch.object(ww, "_load_idle_records", return_value=rc_tests._clean_idle_records(300)))
        stack.enter_context(mock.patch.object(ww.BundleReader, "measured_window", measured))
        stack.enter_context(mock.patch.object(ww, "current_environment_refusals", side_effect=environment))
        yield
