"""Cached unmodified synthetic writer/harvest archives for S3B replay."""
import atexit
import contextlib
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
from unittest import mock

from joulewise import whole_window as ww
from joulewise.b5 import harvest
from joulewise.b5_analysis.archive import open_archive, open_attempt_record
from joulewise.b5_analysis import context as context_module
from joulewise.b5_analysis.kept_units import load_kept_units
from joulewise.b5_analysis.windows import SealPins
from joulewise.flags.catalog import load_catalog
from joulewise.flags.exclusions import compute
from tests.b5_analysis import fixtures as s0, fixtures_s3 as s3
from tests.b5_analysis.fixtures_s1 import s0_planned

ROOT = s0.ROOT
_CACHE = {}
PINS = SealPins.load()
CATALOG = load_catalog(ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json")


def cached(name="BETA_STD"):
    if name not in _CACHE:
        window = s0.build_named(name + "_S3B_ROSTER")
        atexit.register(window.close)
        _CACHE[name] = window
    return _CACHE[name]


def original_handle(window):
    """Open the indexed pinned-harvest archive without a copied-row rebind."""
    record = open_attempt_record(window.entry, seal_pins=PINS, pack_table=s0.PACK_TABLE)
    digest = s0.sha(window.archive / f"sources/repo/configs/campaigns/{window.entry.pack_id}/plan_tree.json")
    return open_archive(s0.selected_window(record, seal_pins=PINS), seal_pins=PINS,
        pack_table=s0.PACK_TABLE, synthetic_plan_tree_sha256=digest)


class Case(s3.Case):
    def __init__(self, name="BETA_STD"):
        self.window = cached(name)
        self.tmp = tempfile.TemporaryDirectory(prefix="b5-s3b-case-")
        self.archive = Path(self.tmp.name) / "archive"
        shutil.copytree(self.window.archive / "derived", self.archive / "derived")
        (self.archive / "withheld").mkdir()
        shutil.copyfile(self.window.archive / "harvest.json", self.archive / "harvest.json")
        for relative in (ww.NEG8_HARVEST_CLEAN_CORPUS, ww.NEG8_HARVEST_CLEAN_BOUND,
                ww.NEG8_HARVEST_SURVIVOR_BRACKET, "withheld/bracket-evaluation.json"):
            shutil.copyfile(self.window.archive / relative, self.archive / relative)
        # Only source bytes this stage actually opens; the inventory is complete.
        (self.archive / "sources").mkdir()
        inventory = self.window.archive / "sources/SHA256SUMS"
        shutil.copyfile(inventory, self.archive / "sources/SHA256SUMS")
        for line in inventory.read_text().splitlines():
            relative = line.split("  ", 1)[1]
            if relative.startswith("repo/") or relative.endswith("campaign_log.jsonl") or "/campaign_manifests/" in relative:
                target = self.archive / "sources" / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.window.archive / "sources" / relative, target)
        self.row = copy.deepcopy(self.window.writer_row)
        self.harvest = self.read("harvest.json")
        self.harvest["archive_root"] = str(self.archive)
        self.entry_data = {**self.window.entry_data, "archive_root": str(self.archive)}
        wrapper = self.read("withheld/bracket-evaluation.json")
        self.assessment = {**wrapper["assessment"], "reasons": wrapper["reasons"]}
        self.context = ww.ArchiveContext(self.archive, window_bracket=self.assessment, governed_e3=True)
        core = self.row["idle_admission_core"]
        core["conditions"] = sorted(set(core["conditions"]) - {"instrument_calibration_bracket_missing"}
                                     | {"calibration_acceptance_bound_stale"})
        self.rederive_continuity()
        self.bind_row()
        self.plan_tree_digest = s0.sha(self.window.archive / self.plan_tree_path())
        self.refresh()

    def plan_tree_path(self):
        return f"sources/repo/configs/campaigns/{self.entry_data['pack_id']}/plan_tree.json"

    def roster(self, archive=None):
        return context_module.rebuilt_roster(archive or self.handle(), self.row)

    def write_source(self, relative, raw):
        """Explicit authenticated-input counterfactual; seal stays independent."""
        path = self.archive / "sources" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        manifest = self.archive / "sources/SHA256SUMS"
        lines = [line for line in manifest.read_text().splitlines() if line.split("  ", 1)[1] != relative]
        lines.append(hashlib.sha256(raw).hexdigest() + "  " + relative)
        manifest.write_text("\n".join(lines) + "\n")

    def refresh(self):
        s0.put(self.archive / "harvest.json", self.harvest)
        self.entry_data["harvest_record_sha256"] = s0.sha(self.archive / "harvest.json")

    def write(self, relative, value, *, authenticate=True):
        if relative.endswith(".jsonl"):
            path = self.archive / relative
            path.write_text("".join(json.dumps(item) + "\n" for item in value))
        else:
            s0.put(self.archive / relative, value)
        if authenticate:
            self.harvest["outputs"][relative] = s0.sha(self.archive / relative)
            self.refresh()

    def handle(self):
        from joulewise.b5_analysis.windows import IndexEntry
        record = open_attempt_record(IndexEntry.from_mapping(self.entry_data, pack_table=s0.PACK_TABLE),
            seal_pins=PINS, pack_table=s0.PACK_TABLE)
        return open_archive(s0.selected_window(record, seal_pins=PINS), seal_pins=PINS, pack_table=s0.PACK_TABLE,
            synthetic_plan_tree_sha256=self.plan_tree_digest)

    def inputs(self):
        archive = self.handle()
        units = load_kept_units(archive, sealed_catalog_sha256=PINS.sealed["catalog_sha256"], planned_units=s0_planned())
        return archive, units

    def build(self, *, bracket=None):
        archive, units = self.inputs()
        self.context = context_module.build_context(archive.window, archive, units,
            self.assessment if bracket is None else bracket, self.row)
        return self.context

    def flags(self):
        return [json.loads(line) for line in (self.archive / "derived/flags.jsonl").read_bytes().splitlines() if line.strip()]

    def exclude(self, run, code):
        roster = self.read("derived/roster.json")
        flag = {"flag_id": "s3b-" + code, "code": code,
            "scope": {"level": "member", "plan_id": roster["plan_id"], "attempt": roster["attempt"],
                "run_id": run, "bundle_id": None, "stage_id": None}, "interval": {"monotonic_ns": None}}
        flags = self.flags() + [flag]
        self.write("derived/flags.jsonl", flags)
        document = compute(flags, roster, {}, CATALOG)
        document["harvest_checkout"] = self.harvest["harvest_checkout"]
        self.write("derived/exclusions.json", document)
        # Maintain S0's exact structural wrappers when adding a synthetic flag.
        window_flags = self.read("derived/window_flags.json")
        window_flags["flags"]["total"] += 1
        family = CATALOG.entry(code)["family"]
        for key, value in (("by_family", family), ("by_code", code)):
            counts = window_flags["flags"][key]
            counts[value] = counts.get(value, 0) + 1
        self.harvest["flags"] += 1
        self.write("derived/window_flags.json", window_flags)
        return flag

    def pinned_rescreen(self, *, row=None):
        """Real frozen loss selector and two-pass screen over these bundles."""
        run = object.__new__(harvest._Harvest)
        run.inputs = SimpleNamespace(claim_runs_root=self.window.claim, plan={"t0_epoch_s": self.entry_data["t0_epoch_s"]})
        run.roster = ww._archive_thaw(self.roster())
        run.flags = SimpleNamespace(records=self.flags())
        run.members = {item["run_id"]: {"strict_valid": True} for item in run.roster["members"]}
        run.neg8_reference_source = {}
        run.neg8 = {"derived_from": "collected_subset"}
        run.neg8_clean_bound = self.read(ww.NEG8_HARVEST_CLEAN_BOUND)["bound"]
        run.neg8_clean_bound_required = True
        run.neg8_corpus_physics_dropped = True
        run.neg8_clean_bound_record = self.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)["clean_bound"]
        destination = Path(self.tmp.name) / ("pinned-screen-" + str(len(list(Path(self.tmp.name).glob("pinned-screen-*")))))
        run.derived, run.withheld = destination / "derived", destination / "withheld"
        run.derived.mkdir(parents=True)
        run.withheld.mkdir()
        run.outputs = {}
        run._neg8_disclose = lambda *_args, **_kwargs: None
        run.emit = lambda *_args, **_kwargs: None
        read_ids = []
        with adapter_projection(self):
            real_energy = ww._reference_energy_evidence
            def evidence(path, **kwargs):
                read_ids.append(Path(path).name)
                return real_energy(path, **kwargs)
            with mock.patch.object(ww, "_reference_energy_evidence", side_effect=evidence):
                source = run.neg8_screen(self.row if row is None else row, authentic=True)
        screen = json.loads((run.derived / "neg8-screen.json").read_bytes())
        wrapper = json.loads((run.withheld / "neg8-rescreen-bracket.json").read_bytes())
        # For recorded sources both passes occur; the last count entries are
        # exactly the exclusion pass's aggregated reference energies.
        count = sum(screen["rescreen"]["survivors"].get("reference_counts", {"start": 3, "midpoint": 1, "end": 3}).values())
        actual_survivors = frozenset(read_ids[-count:])
        return source, screen, wrapper, actual_survivors

    def install_rescreen(self, screen, wrapper):
        self.write(ww.NEG8_HARVEST_SURVIVOR_BRACKET, wrapper)
        descriptor = {"path": ww.NEG8_HARVEST_SURVIVOR_BRACKET,
                      "sha256": s0.sha(self.archive / ww.NEG8_HARVEST_SURVIVOR_BRACKET)}
        screen["survivor_bracket"] = descriptor
        self.write("derived/neg8-screen.json", screen)
        allowance = self.read(ww.NEG8_HARVEST_ALLOWANCE_RECORD)
        allowance["survivor_bracket"] = descriptor
        self.write(ww.NEG8_HARVEST_ALLOWANCE_RECORD, allowance)


@contextlib.contextmanager
def adapter_projection(case):
    # Same mock telemetry projection as the real S0 writer. Hazard identity is
    # a named synthetic seam; authentication, loss tests and arithmetic run.
    with s3.adapter_projection(case), mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True), \
            mock.patch.object(ww, "_is_hazard_runs_root", return_value=False):
        yield
