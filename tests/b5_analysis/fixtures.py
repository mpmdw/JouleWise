"""Synthetic mock-adapter windows, written by the real writer and pinned harvest.

Collection-only observers (cooldown, monitor and capture battery coverage) are
explicit synthetic seams. The exclusions function, NEG-8 arithmetic, writer
record construction and harvest record construction run their real code. This
is fixture evidence, never hardware validation.
"""
from __future__ import annotations

import contextlib
from dataclasses import dataclass, replace
from decimal import Decimal
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import tarfile
import atexit
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
PINS_PATH = ROOT / "configs/analysis/b5/seal_pins.json"
FIXTURES = ROOT / "tests/fixtures/b5_analysis"
_TEMPLATES = {}
_REFERENCE_TEMPLATES = {}

# Explicit test-only identities. Production readers never infer these from an
# entry, a file-name prefix, or an environment variable.
PACK_TABLE = {pack: {f"s0_{pack}_mock_v5": f"s0-{pack}-plan", f"s0-fast-{pack}": f"s0-fast-{pack}"}
              for pack in ("alpha", "beta", "gamma")}

# Exact synthetic seconds. Both the archived ledger and bracket candidates use
# this pair; the real evaluator adds the registered bracket drift allowance.
POST_CAPTURE_BOUND_MARKER_S = Decimal("0.001")
PRE_CAPTURE_BOUNDS_S = {"alpha": Decimal("0.025"), "beta": Decimal("0.026"), "gamma": Decimal("0.027")}


def capture_bounds(pack):
    pre = PRE_CAPTURE_BOUNDS_S[pack]
    return pre, pre + POST_CAPTURE_BOUND_MARKER_S

NAMED_FIXTURES = {"ALPHA_STD": ("alpha", "pin2", ()), "BETA_STD": ("beta", "pin4", ()),
                  "GAMMA_STD": ("gamma", "pin4", ())}
for _pack in ("ALPHA", "BETA", "GAMMA"):
    for _variant in ("REPEAT6_REMOVED", "QUAD_MEMBER_REMOVED", "SIX_QUADS_REMOVED", "FIVE_QUADS_REMOVED",
                     "WRITER_DROPPED_SCIENCE_MEMBER", "WRITER_DROPPED_REFERENCE", "STORED_NEG8_PASSED"):
        NAMED_FIXTURES[f"{_pack}_{_variant}"] = (_pack.lower(), "pin2" if _pack == "ALPHA" else "pin4", (_variant,))
NAMED_FIXTURES["GAMMA_MIDPOINT_LOST"] = ("gamma", "pin4", ("MIDPOINT_LOST",))
NAMED_FIXTURES["BETA_SOURCES_RECOVERED"] = ("beta", "pin4", ("SOURCES_RECOVERED",))

# Only full producer windows used by S0–S3. Counterfactuals derived by editing
# loaded bytes remain in their stage's helpers and need no additional archive.
PIN4_CASES = {
    "BETA_STD": ("beta", ()),
    **{f"BETA_{variant}": ("beta", (variant,)) for variant in (
        "REPEAT6_REMOVED", "QUAD_MEMBER_REMOVED", "SIX_QUADS_REMOVED", "FIVE_QUADS_REMOVED",
        "WRITER_DROPPED_SCIENCE_MEMBER", "WRITER_DROPPED_REFERENCE", "STORED_NEG8_PASSED",
        "SOURCES_RECOVERED")},
    "BETA_SOURCES_RECOVERED_REFERENCES_INSUFFICIENT":
        ("beta", ("SOURCES_RECOVERED", "REFERENCES_INSUFFICIENT")),
    "GAMMA_STD": ("gamma", ()),
    "GAMMA_MIDPOINT_LOST": ("gamma", ("MIDPOINT_LOST",)),
}


def exported_case(pack, shape, variants):
    if shape == "pin4":
        for name, (case_pack, case_variants) in PIN4_CASES.items():
            if pack == case_pack and set(variants) == set(case_variants) and len(variants) == len(case_variants):
                return name
        raise ValueError("this exported pack/variant combination was not built")
    if len(variants) > 1:
        raise ValueError("this exported variant combination was not built")
    return variants[0] if variants else "STD"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


@dataclass
class BuiltWindow:
    root: Path
    archive: Path
    claim: Path
    bound: Path
    custody: Path
    measurement: Path
    entry_data: dict
    writer_exit: int
    writer_row: dict | None
    shape: str
    variants: tuple[str, ...]
    science: tuple
    _release: object = None
    _closed: bool = False

    @property
    def entry(self):
        from joulewise.b5_analysis.windows import IndexEntry
        return IndexEntry.from_mapping(self.entry_data, pack_table=PACK_TABLE)

    def close(self):
        if self._closed:
            return
        if self._release is None:
            shutil.rmtree(self.root)
        else:
            self._release()
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


_SUPPORT_LOADED = False


def _load_export_support():
    """Keep the git-archive's tracked files byte-identical to its commit.

    Current synthetic helpers live in NEW support files. Their virtual file
    locations resolve fixture data in the pinned export; all joulewise and
    scripts imports continue to resolve to the pinned program on disk.
    """
    global _SUPPORT_LOADED
    if _SUPPORT_LOADED:
        return
    import sys, types, importlib
    package = importlib.import_module("tests")
    for name in ("test_harvest_b5_window", "test_harvest_b5_sources"):
        source = ROOT / "tests/b5_analysis/support" / (name + ".py")
        module = types.ModuleType("tests." + name)
        module.__file__ = str(ROOT / "tests" / (name + ".py"))
        sys.modules[module.__name__] = module
        setattr(package, name, module)
        exec(compile(source.read_bytes(), module.__file__, "exec"), module.__dict__)
    _SUPPORT_LOADED = True


def build_window(pack, *, shape="pin4", variants=()):
    """Load committed producer bytes, or build in the exact pin's export.

    Normal tests never execute the current tree's writer or invoke git. Set
    B5_S0_EXPORT_PIN only inside the pinned git-archive export to regenerate;
    the three/four-file hash fence still precedes every producer build.
    """
    variants = (variants,) if isinstance(variants, str) else tuple(variants)
    if pack not in ("alpha", "beta", "gamma"):
        raise ValueError("unknown synthetic pack")
    pin = json.loads(PINS_PATH.read_bytes())["pins"][shape]
    exported = os.environ.get("B5_S0_EXPORT_PIN")
    if shape in ("pin2", "pin4") and exported is None:
        return load_exported_window(pack, shape=shape, variants=variants)
    if exported != pin["head"]:
        raise ValueError("fixtures must be built by their exact git-archive export")
    for path, expected in pin["files"].items():
        if sha(ROOT / path) != expected:
            raise ValueError(f"exported program hash differs: {path}")
    from joulewise import whole_window as ww, calibration_bracketing as br
    from joulewise.calibration_ledger import terminal_head_pin_for_session
    from joulewise.b5 import harvest as h
    from scripts import run_campaign as rc
    if os.environ.get("B5_S0_EXPORT_PIN"):
        _load_export_support()
    from tests import test_harvest_b5_window as hb
    # Older programs have no Erratum-3 constant. Load only the synthetic
    # calibration helper, not the later harvest test classes' default args.
    import types
    trigger = types.ModuleType("s0_synthetic_calibration")
    support = ROOT / "tests/b5_analysis/support/test_harvest_b5_trigger_scope.py"
    source_path = support if support.is_file() else ROOT / "tests/test_harvest_b5_trigger_scope.py"
    source = source_path.read_text().split("class HarvestScopeTests(", 1)[0]
    trigger.__file__ = str(ROOT / "tests/test_harvest_b5_trigger_scope.py")
    exec(compile(source, trigger.__file__, "exec"), trigger.__dict__)
    from tests import test_run_campaign as campaign_tests
    variants = (variants,) if isinstance(variants, str) else tuple(variants)
    allowed = {"REPEAT6_REMOVED", "QUAD_MEMBER_REMOVED", "SIX_QUADS_REMOVED", "FIVE_QUADS_REMOVED",
               "MIDPOINT_LOST", "SOURCES_RECOVERED", "WRITER_DROPPED_SCIENCE_MEMBER", "WRITER_DROPPED_REFERENCE",
               "STORED_NEG8_PASSED", "NOT_USABLE", "NULL", "NO_COLLECTION", "UNAVAILABLE", "REFERENCES_INSUFFICIENT"}
    if set(variants) - allowed:
        raise ValueError("unknown synthetic variant")
    root = Path(tempfile.mkdtemp(prefix=f"b5-s0-{pack}-{shape}-"))
    pre_bound, post_bound = capture_bounds(pack)
    atexit.register(shutil.rmtree, root, ignore_errors=True)
    members = tuple((f"s0-mock-r{i:02d}", "absolute_repeat", None, None, None, "01_abs") for i in range(1, 11))
    members += tuple((f"s0-mock-b{i:02d}-{pos.lower()}", "comparative_abba_member", f"s0-mock-b{i:02d}",
                      pos, pos[0], "02_abba") for i in range(1, 11) for pos in ("A1", "B1", "B2", "A2"))
    if shape in ("pin1", "pin3"):
        members = tuple(row for row in members if row[2] == f"s0-mock-b01" or row[2] is None and row[0].endswith(("r01", "r02")))
    shifts = {row[0]: 100.0 * (i + 1) for i, row in enumerate(members)}

    class SyntheticWindow(hb.Window):
        def _build_runs(self):
            self.claim, self.bound = self.root / "claim-runs", self.root / "bound-runs"
            super()._build_runs()

        def _build_ledger(self, prefix_ledger):
            # Patch only the harness's synthetic capture call; do not rewrite
            # an append-only ledger after it has been finalized.
            finalize = hb.finalize_bracket_session_slot
            def finalize_capture(*args, **kwargs):
                kwargs["exact_bound_lexeme_s"] = str(pre_bound if kwargs["slot"] == "pre" else post_bound)
                return finalize(*args, **kwargs)
            with mock.patch.object(hb, "finalize_bracket_session_slot", finalize_capture):
                super()._build_ledger(prefix_ledger)
            if pack != "gamma" or shape != "pin4":
                return
            from joulewise import calibration_ledger as cl
            import base64, zlib
            receipts = [json.loads(line) for line in self.ledger.read_text().splitlines()]
            own = receipts[-1]
            epoch, bindings = own["identity_epoch"], own["t1_bindings"]
            self.ledger.write_bytes(zlib.decompress(base64.b85decode(hb.PREFIX.read_bytes())))
            cutoff = br.load_calibration_acceptance_bound(ROOT / hb.ACCEPTANCE)["ledger_cutoff"]
            put(self.pin, {"sequence": cutoff["sequence"], "head_digest": cutoff["head_digest"], "ledger_schema": cl.LEDGER_SCHEMA})
            capture = self.root / "instrument_validation" / "s0-other-systematic"
            put(capture / "manifest.json", {"synthetic": True})
            put(capture / "instrument_evidence.json", {"synthetic": True})
            other_slots = {slot: {"attempt_id": "s0-other-systematic" if slot == "pre" else "s0-other-post",
                "custody_locator": str(capture if slot == "pre" else capture / "post"),
                "identity_epoch": epoch, "t1_bindings": bindings} for slot in ("pre", "post")}
            cl.append_bracket_session_receipt(self.ledger, session_id="s0-other-session", window_id="s0-other-window",
                plan_id="s0-other-plan", plan_sha256=sha(self.pack / "calibration_plan.json"),
                evidence_root_id="s0-other-evidence", runs_root=self.root, slots=other_slots,
                head_pin_path=self.pin, require_committed_pin=False)
            cl.finalize_bracket_session_slot(self.ledger, session_id="s0-other-session", slot="pre",
                disposition="systematic-invalid", custody_locator=str(capture), artifact_sha256=cl.artifact_hashes(capture),
                identity_epoch=epoch, t1_bindings=bindings, capture_wall_time_s="90.0",
                exact_bound_lexeme_s="0.04437677892168357")
            receipt = cl.abort_bracket_session(self.ledger, session_id="s0-other-session", reason="synthetic_pre_systematic")
            put(self.pin, cl.terminal_head_pin_for_session(self.ledger, session_id="s0-other-session"))
            slots = {slot: {"attempt_id": f"{hb.SESSION_ID}-{slot}", "custody_locator": str(
                self.claim / "instrument_validation" / f"{hb.SESSION_ID}-{slot}"), "identity_epoch": epoch,
                "t1_bindings": bindings} for slot in ("pre", "post")}
            cl.append_bracket_session_receipt(self.ledger, session_id=hb.SESSION_ID, window_id=hb.PLAN_ID,
                plan_id=hb.PLAN_ID, plan_sha256=sha(self.pack / "calibration_plan.json"), evidence_root_id=hb.EVIDENCE_ROOT_ID,
                runs_root=self.claim, slots=slots, head_pin_path=self.pin, require_committed_pin=False)
            for slot in ("pre", "post"):
                capture = Path(slots[slot]["custody_locator"])
                cl.finalize_bracket_session_slot(self.ledger, session_id=hb.SESSION_ID, slot=slot, disposition="valid",
                    custody_locator=str(capture), artifact_sha256=cl.artifact_hashes(capture), identity_epoch=epoch,
                    t1_bindings=bindings, capture_wall_time_s="99.0" if slot == "pre" else "111.0",
                    exact_bound_lexeme_s=str(pre_bound if slot == "pre" else post_bound))

        def _build_catalog(self, _overrides):
            target = self.measurement / "configs/campaigns/v5_claim_25g83/flag_catalog.json"
            shutil.copyfile(ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json", target)

    key = (shape, members, tuple(shifts.items()))
    if key not in _TEMPLATES:
        template = Path(tempfile.mkdtemp(prefix="b5-s0-template-"))
        atexit.register(shutil.rmtree, template, ignore_errors=True)
        for item in members:
            hb.make_member(template / item[0], item[0], shifts[item[0]])
        _TEMPLATES[key] = template
    template = _TEMPLATES[key]
    try:
        with mock.patch.multiple(hb, MEMBERS=members, SHIFT_S=shifts, _TEMPLATE=template,
                                 PACK_ID=f"s0_{pack}_mock_v5", PLAN_ID=f"s0-{pack}-plan"):
            window = SyntheticWindow(root, prefix_ledger=True)
        tree_path = window.pack / "plan_tree.json"
        tree = h.read_json(tree_path)
        for row in tree["science"]:
            if row["block_id"]:
                row["block_index"] = int(row["block_id"].rsplit("b", 1)[1])
        spec_path = window.pack / "extraction_spec.json"
        spec = h.read_json(spec_path)
        spec["cells"][0]["expected_n"] = sum(row[2] is None for row in members)
        spec["cells"][1]["expected_n"] = len({row[2] for row in members if row[2]})
        spec["cells"][1]["blocks"] = [{"block_id": f"s0-mock-b{i:02d}", "members": {
            row[3]: row[0] for row in members if row[2] == f"s0-mock-b{i:02d}"}} for i in range(1, spec["cells"][1]["expected_n"] + 1)]
        put(spec_path, spec)
        tree["downstream_contract"]["extraction_spec"]["sha256"] = sha(spec_path)
        points = {bundle: 100.0 for bundle, _role in hb.NEG8_REFERENCES}
        references = []
        for i, (bundle, role) in enumerate(hb.NEG8_REFERENCES):
            refkey = (shape, bundle)
            if refkey not in _REFERENCE_TEMPLATES:
                refroot = Path(tempfile.mkdtemp(prefix="b5-s0-ref-template-"))
                atexit.register(shutil.rmtree, refroot, ignore_errors=True)
                hb.make_member(refroot / bundle, bundle, 6000.0 + i * 100)
                _REFERENCE_TEMPLATES[refkey] = refroot / bundle
            hb.copy_member(_REFERENCE_TEMPLATES[refkey], window.claim / bundle)
            # Canonical reference point bundles: mock adapter summary values.
            # Keep the strict-valid mock reduction; writer adapter projection supplies the reference point.
            references.append({"config": bundle + ".json", "run_id": bundle, "execution": "invoked",
                               "bundle_ids": [bundle], "role": rc.NEG8_REFERENCE_ROLE,
                               "sentinel_position": role.rsplit("_", 1)[1], "canonical_neg8_workload": True,
                               "scientific_config_sha256": "d" * 64})
        # Pin the reference configs in the same external-input shape as the harvest harness.
        tree["external_inputs"]["manifests"].extend({"input_id": f"{slot}_reference", "members": [
            {"run_id": item["run_id"], "path": f"configs/campaigns/{window.pack.name}/refs/{item['run_id']}.json",
             "sha256": sha(window.claim / item["run_id"] / "config.json")}
            for item in references if item["sentinel_position"] == slot]} for slot in ("start", "midpoint", "end"))
        for item in references:
            target = window.pack / "refs" / (item["run_id"] + ".json")
            target.parent.mkdir(exist_ok=True)
            shutil.copyfile(window.claim / item["run_id"] / "config.json", target)
        put(tree_path, tree)
        (window.pack / "plan_tree.sha256").write_text(f"{sha(tree_path)}  plan_tree.json\n")
        # Refresh only this synthetic measurement checkout's sealed/executed map.
        inventory = {path.relative_to(window.measurement).as_posix(): sha(path) for path in window.measurement.rglob("*")
                     if path.is_file() and "runs" not in path.relative_to(window.measurement).parts
                     and path.name != "sealed_inventory.json"}
        put(window.measurement / "configs/campaigns/v5_claim_25g83/sealed_inventory.json", {"head": hb.H_CLAIM, "files": inventory})
        executed = h.read_json(window.custody / "night/executed_inventory.json")
        executed["measurement_checkout"]["files"] = inventory
        executed["driver_checkout"] = {"root": str(root / "synthetic-driver"), "head": hb.H_CLAIM,
            "status_porcelain": "", "status_clean": True, "errors": [], "files": {
                path: digest for path, digest in inventory.items() if path.startswith(("joulewise/", "scripts/"))}}
        put(window.custody / "night/executed_inventory.json", executed)
        plan = h.read_json(window.plan_path)
        t0 = {"pin1": 1791500000, "pin2": 1791649800, "pin3": 1791649801, "pin4": 1791738001}[shape]
        plan["t0_epoch_s"] = t0
        plan["hazard_window"]["attempt"] = (6 if pack == "beta" and shape == "pin4" else
            {"NOT_USABLE": 2, "NO_COLLECTION": 3, "NULL": 4, "UNAVAILABLE": 5}.get(variants[0], 2)
            if shape == "pin3" and variants else 1)
        put(window.plan_path, plan)
        terminal = terminal_head_pin_for_session(window.ledger, session_id=hb.SESSION_ID)
        put(window.pin, terminal)
        if hb.neg8_corpus(window) is not None:
            raise ValueError("synthetic corpus mint failed")
        policy = {"sha256": sha(window.measurement / hb.POLICY)}
        science = [{"config": row[0] + ".json", "run_id": row[0], "execution": "invoked", "bundle_ids": [row[0]],
                    "role": row[1]} for row in members]
        if "SOURCES_RECOVERED" in variants:
            spare = "s0-start-spare-absent"
            config = h.read_json(window.claim / references[0]["run_id"] / "config.json")
            config["run_id"] = spare
            put(window.pack / "refs" / (spare + ".json"), config)
            references.append({"config": spare + ".json", "run_id": spare, "execution": "invoked", "bundle_ids": [spare],
                "role": rc.NEG8_REFERENCE_ROLE, "sentinel_position": "start", "canonical_neg8_workload": True,
                "scientific_config_sha256": "d" * 64})
            for slot in ("start", "midpoint", "end"):
                tree["stage_graph"].append({"stage_id": "s0-" + slot, "ordinal": 10 + len(tree["stage_graph"]),
                    "kind": "campaign_collection", "input_ref": {"kind": "external_input", "input_id": slot + "_reference"},
                    "spare_retry": {"slot": slot, "members": [{"run_id": spare,
                        "path": f"configs/campaigns/{window.pack.name}/refs/{spare}.json",
                        "sha256": sha(window.pack / "refs" / (spare + ".json"))}] if slot == "start" else []}})
            put(tree_path, tree)
            (window.pack / "plan_tree.sha256").write_text(f"{sha(tree_path)}  plan_tree.json\n")
            for path in (tree_path, window.pack / "plan_tree.sha256", window.pack / "refs" / (spare + ".json")):
                inventory[path.relative_to(window.measurement).as_posix()] = sha(path)
            put(window.measurement / "configs/campaigns/v5_claim_25g83/sealed_inventory.json", {"head": hb.H_CLAIM, "files": inventory})
            executed["measurement_checkout"]["files"] = inventory
            put(window.custody / "night/executed_inventory.json", executed)
        writer_bound_path = window.bound / "neg8-drift-bound.json"
        if "STORED_NEG8_PASSED" in variants:
            legacy = ROOT / "configs/campaigns/neg8_reference_corpus/derivation/settled_corpus.json"
            corpus = h.read_json(legacy)
            artifact = ww.build_neg8_drift_bound_artifact(corpus_id=corpus["corpus_id"], condition_id=corpus["condition_id"],
                manifest_sha256=sha(legacy), scientific_config_sha256="d" * 64, members=[{
                    "bundle_id": item["bundle_id"], "point_gross_j": 30 + i / 100,
                    "point_idle_subtracted_j": 10 + i / 100, "bundle_evidence_sha256": hashlib.sha256(item["bundle_id"].encode()).hexdigest()}
                    for i, item in enumerate(corpus["members"])], derivation_timestamp_s=h.time.time(),
                freshness_bindings=hb.NEG8_FRESHNESS)
            writer_bound_path = root / "writer-bound.json"
            put(writer_bound_path, artifact)
        token = rc.acquire_campaign_lock(window.claim) if "SOURCES_RECOVERED" in variants else None
        try:
            for name, rows in (("science", science), ("references", references)):
                manifest = {"schema_version": "joulewise.campaign_provenance.v2" if token else "joulewise.campaign_provenance.v1",
                    "session_id": "s0-" + name, "analysis_manifest_id": None if token else "s0-mock-analysis",
                    "campaign_policy": policy, "members": rows}
                path = window.claim / "campaign_manifests" / (name + ".json")
                if token:
                    rc.write_campaign_provenance(path, manifest)
                else:
                    put(path, manifest)
        finally:
            if token:
                rc.release_campaign_lock(token)
        # The mock adapter supplies clean admission observations. Their format is
        # the writer suite's synthetic observation format, not live telemetry.
        real_validate = rc.validate_bundle
        dropped = set()
        if "WRITER_DROPPED_SCIENCE_MEMBER" in variants:
            dropped.add(members[5][0])
        if "WRITER_DROPPED_REFERENCE" in variants:
            dropped.add(references[-1]["run_id"])
        def validate(path, **kwargs):
            if Path(path).name in dropped:
                return ["synthetic adapter invalid member"]
            return [] if Path(path).name in points else real_validate(path, **kwargs)
        original_member = rc._whole_window_member
        def mock_adapter_member(source, waivers, **kwargs):
            evaluated = original_member(source, waivers, **kwargs)
            metadata = dict(evaluated.metadata or {})
            metadata["adapters"] = {"telemetry": {"name": "mock"}}
            metadata["environment"] = {"power_source": "AC Power", "power": {
                "adapter_watts": 140, "adapter_description": "140W USB-C Power Adapter"},
                "post_run_observation": {"capture_skipped": False, "power_source": "AC Power", "power": {
                    "adapter_watts": 140, "adapter_description": "140W USB-C Power Adapter"}}}
            metadata["environment_admission"] = {"decision": "admitted", "attempts": [{"attempt": 1, "admitted": True}]}
            summary = dict(evaluated.summary or {})
            summary.pop("summary_provenance", None)
            if evaluated.bundle_id in points:
                summary = hb.neg8_reference_summary(points[evaluated.bundle_id])
            return replace(evaluated, metadata=metadata, summary=summary)
        writer_args = ["--whole-window-verdict", "--whole-window-verdict-output", str(window.claim / "whole-window-verdict.json"),
                       "--runs-dir", str(window.claim), "--campaign-policy", str(window.measurement / hb.POLICY),
                       "--neg8-drift-bound", str(writer_bound_path),
                       "--calibration-ledger", str(window.ledger), "--head-pin", str(window.pin)]
        with hb.neg8_member_gates(), hb.neg8_reference_gates(points), mock.patch.object(rc, "validate_bundle", validate), \
                mock.patch.object(rc, "_whole_window_member", mock_adapter_member), \
                mock.patch.object(rc, "_load_idle_rich_telemetry", return_value=campaign_tests._clean_idle_records(300)), \
                mock.patch.object(rc, "_neg8_reference_scientific_config_sha256", return_value="d" * 64), \
                mock.patch.object(rc, "build_neg8_freshness_observation", side_effect=lambda _rows, **call: {
                    "binding_status": "resolved", "bindings": hb.NEG8_FRESHNESS, "evaluated_at_s": call["evaluated_at_s"]}), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            writer_exit = rc.main(writer_args)
        row_path = window.claim / "whole-window-verdict.json"
        row = h.read_json(row_path)
        injected = []
        if "REPEAT6_REMOVED" in variants:
            injected.append((members[5][0], "thermal.os_level_nonzero"))
        if "QUAD_MEMBER_REMOVED" in variants:
            injected.append((members[10][0], "thermal.os_level_nonzero"))
        n = 6 if "SIX_QUADS_REMOVED" in variants else 5 if "FIVE_QUADS_REMOVED" in variants else 0
        injected += [(f"s0-mock-b{i:02d}-a1", "thermal.os_level_nonzero") for i in range(1, n + 1)]
        if "REFERENCES_INSUFFICIENT" in variants:
            injected += [(item["run_id"], "thermal.os_level_nonzero") for item in references
                         if item["sentinel_position"] == "midpoint" or item["sentinel_position"] == "end" and item["run_id"].endswith(("1", "2"))]
        if "MIDPOINT_LOST" in variants:
            injected.append((next(item["run_id"] for item in references if item["sentinel_position"] == "midpoint"),
                             "thermal.os_level_nonzero"))
        # The invalid mock-adapter observation reaches both real consumers:
        # the writer's strictness seam and the harvest's collector flag seam.
        injected += [(bundle_id, "member.strict_validation_failed") for bundle_id in sorted(dropped)]
        # A corpus physics loss is a real synthetic loss, so the stored
        # underived-bound conditions may be cleared by the registered re-screen.
        injected.append((hb.CORPUS_IDS[0], "thermal.os_level_nonzero"))
        if "NOT_USABLE" in variants:
            injected.append((None, "calibration.binding_failed"))
        def meter(run):
            for bundle, code in injected:
                run.emit(code, level="member" if bundle else "window", run_id=bundle, collector="monitor",
                         observed={"synthetic_fixture": True})
        # Synthetic calibration adapter: real registered bracket arithmetic over
        # the calibration test's synthetic snapshot/candidates (no hardware reads).
        evaluator = trigger.WindowEvidenceTests()
        evaluator.setUp()
        fixture = evaluator.fixture(p=str(pre_bound), q=str(post_bound),
                                    systematics=(456,) if pack == "gamma" and shape == "pin4" else ())
        def evaluate(*args, **kwargs):
            snapshot, candidates, binding = fixture
            call = evaluator.kwargs(snapshot, binding)
            if shape == "pin4":
                call["trigger_scope"] = kwargs.get("trigger_scope", "sealed")
            return br.evaluate_calibration_bracket(candidates, **call)
        def checkout():
            def runner(argv, **kwargs):
                # git archive has no .git; the program hashes remain actual reads.
                return SimpleNamespace(returncode=0, stdout=pin["head"] + "\n" if "rev-parse" in argv else "", stderr="")
            return h.harvest_checkout(runner=runner)
        def unavailable(*_args):
            raise RuntimeError("synthetic exclusion-function fault")
        seams = h.Seams(group_alive=lambda _pgid: False, boot_session_uuid=lambda: "B5-S0-MOCK-BOOT",
                        harvest_checkout=checkout, exclusions_compute=unavailable if "UNAVAILABLE" in variants else hb.EXCLUSIONS)
        if "NULL" in variants:
            (window.custody / "night/chain.started").unlink()
        if "NO_COLLECTION" in variants:
            (window.custody / "night/chain-stages.jsonl").write_text(json.dumps({
                "stage_id": "s0-pre-collection-stop", "kind": "calibration_capture", "rc": 1}) + "\n")
            for name in [item[0] for item in members] + list(points):
                shutil.rmtree(window.claim / name)
        with contextlib.ExitStack() as stack:
            if "SOURCES_RECOVERED" in variants:
                original_sources = h.claim_neg8_sources
                def mock_hazard_source(*args, **kwargs):
                    # The L2 root classification is the synthetic driver seam.
                    # Catalog hashes, attestation, membership and basis remain real.
                    with mock.patch("joulewise.window_lineage.is_hazard_runs_root", return_value=True), \
                            mock.patch.object(ww, "_is_hazard_runs_root", return_value=False):
                        return original_sources(*args, **kwargs)
                stack.enter_context(mock.patch.object(h, "claim_neg8_sources", mock_hazard_source))
            stack.enter_context(hb.neg8_member_gates())
            stack.enter_context(hb.neg8_reference_gates(points))
            # The admission observations above are an adapter projection. A
            # fixture validator authenticates that projection at this boundary;
            # no production or analysis reader is patched.
            stack.enter_context(mock.patch.object(ww, "validate_whole_window_verdict_row",
                                                  return_value=SimpleNamespace(authentic=True)))
            for method in ("cooldown", "monitor_joins"):
                stack.enter_context(mock.patch.object(h._Harvest, method, lambda _self: None))
            stack.enter_context(mock.patch.object(h._Harvest, "meter_joins", meter))
            stack.enter_context(mock.patch.object(h._Harvest, "_capture_battery_joins", lambda *_: None))
            stack.enter_context(mock.patch.object(h, "assess_member", hb.cached_assess))
            stack.enter_context(mock.patch.object(br, "calibration_bracket_for_bundles", evaluate))
            record = window.harvest(seams=seams, run_g3=False)
        entry = {"pack": pack, "pack_id": record["pack_id"], "attempt": record["attempt"], "plan_id": record["plan_id"],
                 "t0_epoch_s": t0, "seal": "first" if shape == "pin1" else "second", "entry_kind": "harvested",
                 "archive_root": str(window.archive), "harvest_record_sha256": sha(window.archive / "harvest.json"),
                 "superseded_archive_roots": [], "claim_runs_root": str(window.claim), "bound_runs_root": str(window.bound),
                 "custody_root": str(window.custody), "measurement_root": str(window.measurement), "harvest_pin": pin["head"],
                 "verdict": record["verdict"], "claim_usable": record["claim_usable"], "cause_key": None}
        return BuiltWindow(root, window.archive, window.claim, window.bound, window.custody, window.measurement,
                           entry, writer_exit, row, shape, variants, members)
    except BaseException:
        shutil.rmtree(root)
        raise


def build_named(name):
    return build_window(NAMED_FIXTURES[name][0], shape=NAMED_FIXTURES[name][1], variants=NAMED_FIXTURES[name][2])


def export_fixtures(shape, destination, *, case=None):
    """Run inside the pin export; preserve archive bytes, never transform a shape."""
    from joulewise.b5 import harvest
    destination = Path(destination)
    put(destination / "PROGRAM_STRUCTURE.json", {
        "harvest_pin": os.environ["B5_S0_EXPORT_PIN"],
        "neg8_reference_loss_codes": sorted(harvest.NEG8_REFERENCE_LOSS_CODES)})
    if shape == "pin4":
        cases = tuple((name, pack, variants) for name, (pack, variants) in PIN4_CASES.items())
    else:
        old_cases = (("STD", ()), ("REPEAT6_REMOVED", ("REPEAT6_REMOVED",)), ("QUAD_MEMBER_REMOVED", ("QUAD_MEMBER_REMOVED",)),
                     ("NOT_USABLE", ("NOT_USABLE",)),
                     *((name, (name,)) for name in ("SIX_QUADS_REMOVED", "FIVE_QUADS_REMOVED", "WRITER_DROPPED_SCIENCE_MEMBER",
                                                    "WRITER_DROPPED_REFERENCE", "STORED_NEG8_PASSED", "REFERENCES_INSUFFICIENT"))) \
            if shape == "pin2" else tuple((name, (name,)) for name in ("NOT_USABLE", "NULL", "NO_COLLECTION", "UNAVAILABLE"))
        cases = tuple((name, "alpha" if shape == "pin1" or shape == "pin2" and name != "NOT_USABLE" else "beta", variants)
                      for name, variants in old_cases)
    for name, pack, variants in cases:
        if case is not None and name not in case.split(","):
            continue
        with build_window(pack, shape=shape, variants=variants) as built:
            target = destination / name
            target.mkdir(parents=True, exist_ok=True)
            if shape in ("pin2", "pin4"):
                # Complete archives, including mock raw streams, are compressed
                # to keep commit-ready fixtures small. No byte is rewritten.
                with tarfile.open(target / "archive.tar.xz", "w:xz", preset=3) as archive:
                    archive.add(built.archive, arcname="archive")
            else:
                for relative in ("harvest.json", "derived/exclusions.json", "derived/window_flags.json", "derived/neg8-screen.json"):
                    source = built.archive / relative
                    if source.exists():
                        output = target / "archive" / relative
                        output.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(source, output)
            put(target / "INDEX_ENTRY.json", built.entry_data)
            put(target / "WRITER_STRUCTURE.json", {"status": built.writer_row["status"],
                "claim_licensing": built.writer_row["claim_licensing"], "conditions": built.writer_row["idle_admission_core"]["conditions"],
                "member_failures": built.writer_row["member_failures"], "excluded_bundles": built.writer_row["excluded_bundles"]})
            print(shape, name, built.entry_data["verdict"], built.entry_data["claim_usable"], flush=True)


_EXTRACTED = {}
_RESTORED = {}


def archived_entry(shape, name, *, archive_root=None, **overrides):
    from joulewise.b5_analysis.windows import IndexEntry
    directory = FIXTURES / shape / name
    entry = json.loads((directory / "INDEX_ENTRY.json").read_bytes())
    if archive_root is None and (directory / "archive.tar.xz").is_file():
        key = (shape, name)
        if key not in _EXTRACTED:
            tmp = tempfile.TemporaryDirectory(prefix="s0-archived-fixture-")
            atexit.register(tmp.cleanup)
            with tarfile.open(directory / "archive.tar.xz") as archive:
                archive.extractall(tmp.name, filter="data")
            _EXTRACTED[key] = tmp
        archive_root = Path(_EXTRACTED[key].name) / "archive"
    entry["archive_root"] = str(archive_root or directory / "archive")
    entry.update(overrides)
    return IndexEntry.from_mapping(entry, pack_table=PACK_TABLE)


def load_exported_window(pack, *, shape, variants=()):
    """Restore the original synthetic roots so recorded absolute paths still bind.

    Only the builder's /private/tmp/b5-s0-* roots are restorable. Existing
    unowned roots are preserved and refused. Concurrent handles to one base
    share its original bindings; the last handle removes our restored root.
    """
    variants = (variants,) if isinstance(variants, str) else tuple(variants)
    case = exported_case(pack, shape, variants)
    directory = FIXTURES / shape / case
    data = json.loads((directory / "INDEX_ENTRY.json").read_bytes())
    if shape == "pin4" and data["pack"] != pack:
        raise ValueError("exported fixture pack differs")
    entry = archived_entry(shape, case)
    root = Path(data["archive_root"]).parent
    key = (shape, case)
    if root.parent != Path("/private/tmp") or not root.name.startswith("b5-s0-"):
        raise ValueError("synthetic original fixture root unavailable")
    owned = _RESTORED.get(root)
    if root.exists() and (owned is None or owned[0] != key):
        raise ValueError("synthetic original fixture root unavailable")
    if owned is not None and not root.exists():
        raise ValueError("synthetic restored fixture root disappeared")
    if owned is None:
        from joulewise.b5 import harvest
        root.mkdir()
        try:
            archive = root / "archive"
            harvest.clone_tree(entry.archive_root, archive)
            for label, field in (("claim-runs", "claim_runs_root"), ("bound-runs", "bound_runs_root"),
                                 ("night-custody", "custody_root"), ("repo", "measurement_root")):
                target = Path(data[field])
                if not target.is_relative_to(root):
                    raise ValueError("exported fixture escapes its synthetic root")
                harvest.clone_tree(archive / "sources" / label, target)
            for label, target in (("calibration_observation_ledger.jsonl", Path(data["measurement_root"]) / "runs/calibration_observation_ledger.jsonl"),
                                  ("calibration_ledger_head.json", Path(data["measurement_root"]) / "configs/calibration/calibration_ledger_head.json")):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(archive / "sources/ledger" / label, target)
        except BaseException:
            shutil.rmtree(root)
            raise
        _RESTORED[root] = [key, 0]
        atexit.register(shutil.rmtree, root, ignore_errors=True)
    data["pack"] = pack
    row = json.loads((Path(data["claim_runs_root"]) / "whole-window-verdict.json").read_bytes())
    _RESTORED[root][1] += 1
    def release():
        _RESTORED[root][1] -= 1
        if _RESTORED[root][1] == 0:
            shutil.rmtree(root)
            del _RESTORED[root]
    return BuiltWindow(root, root / "archive", Path(data["claim_runs_root"]), Path(data["bound_runs_root"]),
                       Path(data["custody_root"]), Path(data["measurement_root"]), data,
                       1 if row["status"] == "failed" else 0, row, shape, variants, (), _release=release)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("shape", choices=("pin1", "pin2", "pin3", "pin4"))
    parser.add_argument("destination", type=Path)
    parser.add_argument("--case")
    args = parser.parse_args()
    export_fixtures(args.shape, args.destination, case=args.case)


def structural_archive(root, *, pack="beta", usable=True, release_blocked=False, verdict="COLLECTED", attempt=1):
    """Fast pin4 reader input made by the real harvest's finish method.

    The checkout observation comes from the committed pin4 base. No bundles,
    estimation or hardware assertions; full-window integration is tested on
    producer archives separately. Other pins also use export-produced fixtures.
    """
    from joulewise.b5 import harvest as h
    from joulewise.b5_analysis.windows import SealPins, IndexEntry
    pins = SealPins.load()
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    # This is a structural counterfactual, not a new producer window. Reuse
    # the actual pinned checkout observation from the committed base rather
    # than combining a synthetic pinned HEAD with current-tree file hashes.
    base = archived_entry("pin4", "BETA_STD")
    checkout = json.loads((base.archive_root / "harvest.json").read_bytes())["harvest_checkout"]
    document = {"schema_version": "joulewise.exclusions.v1", "claim_usable": usable,
                "release_blocked": release_blocked, "catalog_sha256": pins.sealed["catalog_sha256"],
                "members_excluded": [], "cells": [], "reasons": [] if usable else ["cell.below_minimum"],
                "unclassified": ["s0.unknown"] if release_blocked else []}
    inputs = SimpleNamespace(plan_id="s0-fast-" + pack, pack_id="s0-fast-" + pack, attempt=attempt,
                             plan={"t0_epoch_s": pins.erratum_3_epoch_s + 1}, h_claim="a" * 40,
                             catalog_path=ROOT / "configs/campaigns/v5_claim_25g83/flag_catalog.json", custody_root=root)
    run = h._Harvest(inputs, root, h.Seams(harvest_checkout=lambda: checkout,
        boot_session_uuid=lambda: "S0-STRUCTURAL", exclusions_compute=lambda *_: document), prepare_desk=False, run_g3=False)
    run.exclusion_roster = {"members": [], "cells": []}
    run.exclusion_spans = {}
    if release_blocked:
        run.emit("s0.unknown", level="window", collector="s0-fixture", spec=h.CODES["records.collector_failed"])
    run.finish(verdict)
    (root / "derived/roster.json").write_text('{"synthetic":true}\n')
    record = h.read_json(root / "harvest.json")
    record["outputs"]["derived/roster.json"] = sha(root / "derived/roster.json")
    put(root / "harvest.json", record)
    return IndexEntry.from_mapping({"pack": pack, "pack_id": inputs.pack_id, "plan_id": inputs.plan_id, "attempt": attempt,
        "seal": "second", "entry_kind": "harvested", "t0_epoch_s": inputs.plan["t0_epoch_s"],
        "archive_root": str(root), "harvest_record_sha256": sha(root / "harvest.json"), "harvest_pin": pins.pins["pin4"]["head"],
        "claim_runs_root": str(root / "original"), "bound_runs_root": str(root / "bound"),
        "measurement_root": str(root / "measurement"), "custody_root": str(root / "custody"),
        "verdict": verdict, "claim_usable": usable and verdict == "COLLECTED", "superseded_archive_roots": []},
        pack_table=PACK_TABLE)


def selected_window(record, *, seal_pins=None):
    """Test-only complete block around a target record, through real selection."""
    from joulewise.b5_analysis.windows import SealPins, select_analysed_attempts
    pins = seal_pins or SealPins.load()
    # Selection uses structure only. Fill unrelated packs with independent mock
    # identities; open_archive still authenticates the target's unchanged bytes.
    records = [record]
    for attempt in range(1, record.entry.attempt):
        entry = replace(record.entry, attempt=attempt, entry_kind="no_archive", archive_root=None,
                        harvest_record_sha256=None, verdict="NO_COLLECTION", claim_usable=False,
                        record_citation="synthetic-selection.md:1")
        records.append(replace(record, entry=entry, kind="no_archive", verdict="NO_COLLECTION", claim_usable=False,
                               release_blocked=None))
    for pack in ("alpha", "beta", "gamma"):
        if pack != record.entry.pack:
            entry = replace(record.entry, pack=pack, pack_id=f"s0-fast-{pack}", plan_id=f"s0-fast-{pack}",
                            attempt=1, seal="second", t0_epoch_s=pins.erratum_3_epoch_s + 1,
                            harvest_pin=pins.pins["pin4"]["head"], verdict="COLLECTED", claim_usable=True)
            records.append(replace(record, entry=entry, verdict="COLLECTED", claim_usable=True, release_blocked=False))
    return select_analysed_attempts([row.entry for row in records], records, seal_pins=pins)[record.entry.pack]
