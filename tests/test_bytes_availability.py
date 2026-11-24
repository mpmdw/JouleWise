"""Table-driven file-fault agreement on compact, production-shaped synthetic archives."""
from __future__ import annotations

from contextlib import chdir, contextmanager, redirect_stderr, redirect_stdout
import csv
import errno
from fnmatch import fnmatchcase
import hashlib
import io
import json
from pathlib import Path
import plistlib
import re
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from joulewise import environment_admission
from joulewise.axi_decode_config import RequestDescriptor, RequestRoster
from joulewise.bundle_read import BundleReader
from joulewise.desk_restore import RestoreRefused, StorageStop, readable_run
from joulewise.b6.acceptance import evidence_from_archive
from joulewise.b6.smoke import reduce_tree
from joulewise.reduce import _verify_instrument_calibration
from scripts import bytes_analyze, bytes_commitment, bytes_twin
from tests import test_bytes_agreement as agreement
from tests.bytes_commitment_support import commitment_fixture, commit_journal
from tests.desk_restore_support import compress_member

TABLE = agreement.FIXTURES / "availability_contract.json"
CONTRACT = {row["id"]: row for row in json.loads(TABLE.read_text())}
FAULTS = ("absent", "zero", "half", "garbage")
PHASES = ("before_export", "after_export")
MODEL = "Qwen3-8B-4bit"
SESSION = "bytes-s2-p1"


@contextmanager
def file_fault(path, fault):
    original = path.read_bytes() if path.is_file() else None
    if fault == "absent":
        path.unlink(missing_ok=True)
    else:
        damage = {"zero": b"", "half": (original or b"")[:len(original or b"") // 2],
                  "garbage": b"\xffbroken input\n"}
        path.write_bytes(damage[fault])
    try:
        yield
    finally:
        if original is None:
            path.unlink(missing_ok=True)
        else:
            path.write_bytes(original)


def traced_input(fixture, path):
    for archive in fixture.archives:
        if path.is_relative_to(archive):
            relative = path.relative_to(archive)
            if relative.parts[:2] in {("sources", "claim-runs"), ("sources", "bound-runs")}:
                return Path("bundle", *relative.parts[3:]).as_posix()
            return relative.as_posix()
        if path.is_relative_to(journal := Path(str(archive) + ".desk")):
            return Path("archive.desk", path.relative_to(journal)).as_posix()
    if path.is_relative_to(fixture.root):
        return path.relative_to(fixture.root).as_posix()
    if path.is_relative_to(agreement.ROOT / "configs"):
        return path.relative_to(agreement.ROOT).as_posix()
    return None


@contextmanager
def trace_primary_inputs(fixture, *, suppress=(), aliases=None):
    seen = set()
    original = Path.open
    aliases = aliases or {}

    def tracked(path, mode="r", *args, **kwargs):
        if mode.startswith("r"):
            key = aliases.get(path) or traced_input(fixture, path)
            if key is not None:
                seen.add(key)
            if path in suppress:
                raise FileNotFoundError("synthetic mirror read intercepted")
        return original(path, mode, *args, **kwargs)

    with patch.object(Path, "open", tracked):
        yield seen


class AvailabilityFixture:
    def __init__(self, root, timing, *, complete_fit=False):
        self.root = root
        self.manifest_path = root / "manifest.json"
        collected = {SESSION, "bytes-s1-p1"} if complete_fit else {SESSION}
        uncollected = tuple(f"bytes-s{subpack}-p{p}" for subpack in range(1, 7) for p in (1, 2)
                            if f"bytes-s{subpack}-p{p}" not in collected)
        with patch("os.fsync", return_value=None):
            self.manifest = agreement.archive_campaign(
                root, non_claim=False, release="fit" if complete_fit else "none", subpack_sessions=True,
                uncollected_sessions=uncollected, anchor_profile="narrow" if timing == "native" else None)
        agreement._write(self.manifest_path, self.manifest)
        self.archives = [Path(session["archive"]) for session in self.manifest["sessions"]]
        self.archive = next(archive for archive in self.archives if archive.name == SESSION)
        self.member = agreement._run_ids(self.archive, self.manifest["models"], MODEL)[20]
        self.bundle = self.archive / "sources/claim-runs" / self.member
        # The library selects dispatch by reading a finalized summary when one exists.
        agreement._write(self.bundle / "summary_metrics.json", {"summary_provenance": {"reducer_version": "0.5.2"}})
        roster = agreement.load(self.archive / "derived/roster.json")["members"]
        # The harvested roster has no role. The exporter takes roles from the plan walk.
        self.plan = {"plan_tree": agreement._campaign.plan_tree(roster)}
        self.evidence = SimpleNamespace(runtime={}, session_id=SESSION, stages=[SimpleNamespace(members=[
            SimpleNamespace(**member, role=agreement._campaign.plan_role(member), status="succeeded",
                            config_key="fixture") for member in roster])])
        self.private = root / "private-keys/bytes/blinding"
        self.keys = root / "released-keys/bytes/blinding"
        if not complete_fit:
            for path in self.private.glob("*.json"):
                shutil.copyfile(path, self.keys / path.name)
        self.export = self.export_path(root / "export")
        self.stream = self.archive / "sources/night-custody/hazards/meter/stream-001.jsonl"

    @staticmethod
    def export_path(output):
        return next(output.rglob(f"{SESSION}.runs.csv"))

    def targets(self, export, *, keys=None):
        keys = self.keys if keys is None else keys
        model = next(m for m in self.manifest["models"] if m["model"] == MODEL)
        sidecar = export.with_name(f"{SESSION}.session.json")
        withheld = agreement.load(sidecar)["blinding"]["withheld"]["path"]
        return {**{row_id: self.bundle / filename for row_id, filename in (
                    ("config", "config.json"), ("metadata", "metadata.json"), ("events", "events.jsonl"),
                    ("trace", "power_trace.csv"), ("status", "status.json"), ("summary", "summary_metrics.json"))},
                "reduction": self.archive / "withheld/reductions" / (self.member + ".summary_metrics.rereduced.json"),
                "roster": self.archive / "derived/roster.json", "acceptance": self.archive / "derived/b6-acceptance.json",
                "flags": self.archive / "derived/flags.jsonl", "meter": self.stream,
                "harvest_receipt": self.archive / "harvest.json", "source_inventory": self.archive / "sources/SHA256SUMS",
                "manifest": self.manifest_path, "export_csv": export, "export_sidecar": sidecar,
                "withheld_csv": export.parent / withheld, "pack_key": keys / "pack.json",
                "config_key": keys / agreement.blinding._config_filename(model["config_key"])}

    def export_again(self, destination, private, *, read_registration=False, grouped=True, read_evidence=False, plan=None):
        pack = {"blinding_group": "bytes", "bytes_pass": 1} if grouped else {"pack_id": SESSION}
        with patch("os.fsync", return_value=None):
            agreement.export_runs.export(self.archive, plan or self.plan, self.root / "registration", private, destination,
                                         evidence=None if read_evidence else self.evidence,
                                         pack_registration=None if read_registration else pack)
        return self.export_path(destination), private / ("bytes" if grouped else SESSION) / "blinding"

    def compare(self, test, export, keys, scratch, *, stage="fit", expect_kept=None, fit_cli=False, expect_exit=None):
        modes = {"fit": "1", "heldout": "2", "blinded": "blinded"}
        try:
            if fit_cli:
                primary_out = scratch / "primary"
                # This matrix exercises faults below the seal. The real entry
                # gates are exercised on the separate, committed seal fixture.
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()), \
                        patch.object(bytes_analyze, "_check_export"):
                    primary_status = bytes_analyze.main(["--export", str(export.parents[1]), "--manifest",
                        str(self.manifest_path), "--key-dir", str(keys), "--stage", "fit", "--out", str(primary_out)])
                passes = agreement.load(primary_out / "fit_pass_estimates.json")
            else:
                manifest = agreement.ba.validate_manifest(agreement.ba.read_json(self.manifest_path))
                passes, _ = bytes_analyze._reduce([export.parents[1]], manifest, stage, keys)
                primary_status = 0
        except (StorageStop, OSError, ValueError, KeyError, TypeError, AttributeError):
            primary_status = 1
        output = scratch / "twin.json"
        output.unlink(missing_ok=True)
        # The test checks the table-reader seam after synthetic key release. The end-to-end
        # agreement suite separately checks the CLI commitment gate.
        if stage == "heldout":
            twin_status, twin = self.heldout_twin(export, keys)
        else:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()), \
                    patch.object(bytes_twin, "_check_export"):
                twin_status = bytes_twin.main(["--export-dir", str(export.parents[1]), "--manifest", str(self.manifest_path),
                    *[arg for archive in self.archives for arg in ("--archive", str(archive))],
                    "--key-dir", str(keys), "--stage", modes[stage], "--out", str(output)])
            twin = agreement.load(output) if twin_status == 0 else None
        recorder = agreement.Recorder()
        recorder.exact(stage, "stage", "refusal", primary_status, twin_status)
        if expect_exit is not None:
            test.assertEqual((primary_status, twin_status), (expect_exit, expect_exit))
        if primary_status == twin_status == 0:
            if stage == "heldout":
                twin["cells"] = {model: block for model, block in twin["cells"].items() if model not in bytes_twin.FIT_SET}
            agreement.compare_cells(recorder, stage, passes, twin)
            agreement.compare_neg8(recorder, stage, passes, twin)
        counts = recorder.counts()
        test.assertEqual(counts["above_bar"], 0, [(row["group"], row["key"]) for row in recorder.above()[:14]])
        if expect_kept is not None:
            member_cells = [row for row in recorder.rows if row["key"] == "kept_runs"
                            and row["group"].startswith(f"cell/{bytes_twin.canon(MODEL)}/pass1/")]
            test.assertTrue(member_cells)
            for row in member_cells:
                test.assertEqual((self.member in row["a"], self.member in row["t"]), (expect_kept, expect_kept))
        return counts["compared"]

    def heldout_twin(self, export, keys):
        try:
            manifest = bytes_twin.read_manifest(self.manifest_path)
            sidecar = bytes_twin.read_sidecar(export)
            store = bytes_twin.load_withheld(export, sidecar, manifest)
            rows = (bytes_twin.read_export(export) if export.is_file() else []) + store["rows"]
            archive = bytes_twin.load_archive(self.archive)
            result = bytes_twin.analyse(rows, manifest, [archive], stage="2", key_dir=keys,
                sidecars={SESSION: sidecar}, listed={SESSION: self.manifest["sessions"][0]},
                withheld={SESSION: store}, synthetic=True)
            return 0, result
        except (bytes_twin.StorageStop, OSError, ValueError, KeyError, TypeError, AttributeError):
            return 1, None


def event_v2_inputs(fixture, *, sparse=False):
    roster = RequestRoster((RequestDescriptor(0, "synthetic", "prompt_text", "0" * 64, "synthetic", 512),))
    config = agreement.load(agreement.ROOT / "tests/fixtures/axi_ap_spec/draft_spec_on.json")
    config["model"]["name"], config["run_id"] = MODEL, fixture.member
    config["batch_policy"]["request_roster_sha256"] = roster.sha256
    agreement._write(fixture.bundle / "config.json", config)
    metadata_path = fixture.bundle / "metadata.json"
    metadata = agreement.load(metadata_path)
    agreement._write(metadata_path, {**metadata, "event_semantics_version": "joulewise.events.v2"})
    agreement._write(fixture.bundle / "summary_metrics.json", {"summary_provenance": {"reducer_version": "0.6.2"}})
    paths = {"request_roster": fixture.bundle / "request_roster.json",
             "request_rows": fixture.bundle / "outputs/requests.jsonl",
             "request_tokens": fixture.bundle / "outputs/request_tokens.jsonl",
             "response_mirror": fixture.bundle / "outputs/response.txt",
             "tokens_mirror": fixture.bundle / "outputs/tokens.jsonl"}
    paths["request_roster"].write_bytes(roster.to_bytes())
    paths["request_rows"].parent.mkdir(exist_ok=True)
    for key in ("request_rows", "request_tokens"):
        paths[key].write_bytes(b"" if sparse else b"{}\n")
    return paths


def optional_inventory_prefix(optional, target_bytes):
    """Select whole checksum rows to end an exact byte half at a newline."""
    mask = (1 << (target_bytes + 1)) - 1
    reachable = [1]
    for row in optional:
        previous = reachable[-1]
        reachable.append((previous | (previous << len(row))) & mask)
    if not ((reachable[-1] >> target_bytes) & 1):
        raise AssertionError("the fixture cannot put an inventory row boundary at the midpoint")
    chosen, remaining = [], []
    for row, before in zip(reversed(optional), reversed(reachable[:-1]), strict=True):
        if (before >> target_bytes) & 1:
            remaining.append(row)
        else:
            chosen.append(row)
            target_bytes -= len(row)
    return chosen, remaining


class BytesAvailabilityTests(unittest.TestCase):
    def assert_contract_covers_reads(self, actual, phase, *, restoring=False):
        patterns = {pattern for row in CONTRACT.values() if row["phase"] in {phase, "both"}
                    if restoring or not row.get("restore_only")
                    for pattern in row.get("read_paths", ())}
        uncovered = sorted(path for path in actual if not any(fnmatchcase(path, pattern) for pattern in patterns))
        self.assertEqual(uncovered, [])

    def test_contract_covers_primary_export_and_conditional_reducer_reads(self):
        with tempfile.TemporaryDirectory(prefix="bytes-contract-reads-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", "mock")
            registered = fixture.root / "registration/acceptance.json"
            registered.parent.mkdir(exist_ok=True)
            registered.touch()
            # Exercise the producer without the fixture's precomputed evidence.
            with patch("os.fsync", return_value=None), trace_primary_inputs(fixture) as opened:
                agreement.export_runs.export(fixture.archive, fixture.plan, registered.parent, fixture.root / "private-keys",
                    fixture.root / "read-trace-export", pack_registration={"blinding_group": "bytes", "bytes_pass": 1})
            self.assertIn("registration/acceptance.json", opened)
            self.assert_contract_covers_reads(opened, "export")
            reads = set(opened)

            def fit():
                passes, _ = bytes_analyze._reduce([fixture.export.parents[1]], fixture.manifest, "fit", fixture.keys)
                self.assertTrue(passes)
                return passes

            suite = fixture.bundle / "suite_manifest.json"
            suite.write_bytes(b"{")
            with trace_primary_inputs(fixture) as opened:
                passes = fit()
            self.assertIn("bundle/suite_manifest.json", opened)
            self.assert_contract_covers_reads(opened, "analysis")
            reads.update(opened)
            self.assertTrue(any(fixture.member in row.get("kept_runs", ()) for row in passes))
            fixture.compare(self, fixture.export, fixture.keys, root, expect_kept=True)
            suite.unlink()

            config_path = fixture.bundle / "config.json"
            metadata_path = fixture.bundle / "metadata.json"
            config = agreement.load(config_path)
            metadata = agreement.load(metadata_path)
            native_config = {**config, "hardware_target": {**config["hardware_target"], "telemetry_backend": "powermetrics"}}
            native_metadata = {**metadata, "adapters": {**metadata.get("adapters", {}), "telemetry": {"name": "powermetrics"}},
                               "environment_admission": {"attempts": [{"attempt": 1, "start_s": 0, "end_s": 1,
                                                                       "baseline": {"duration_s": 1}}]},
                               "campaign_policy": {"sha256": "0" * 64}}
            agreement._write(config_path, native_config)
            agreement._write(metadata_path, native_metadata)
            policies = fixture.root / "configs/campaign_policies"
            native_paths = {"bundle/rich_telemetry_idle.jsonl": fixture.bundle / "rich_telemetry_idle.jsonl",
                            "bundle/raw/powermetrics_idle.plist": fixture.bundle / "raw/powermetrics_idle.plist",
                            "configs/campaign_policies/test.json": policies / "test.json"}
            for path in native_paths.values():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()
            with patch.object(environment_admission, "REGISTERED_POLICY_DIR", policies), trace_primary_inputs(fixture) as opened:
                fit()
            self.assertTrue(native_paths.keys() <= opened)
            self.assert_contract_covers_reads(opened, "analysis")
            reads.update(opened)
            with patch.object(environment_admission, "REGISTERED_POLICY_DIR", policies):
                fixture.compare(self, fixture.export, fixture.keys, root, expect_kept=True)
            for path in native_paths.values():
                path.unlink()

            event_v2 = event_v2_inputs(fixture, sparse=True)
            (fixture.bundle / "events.jsonl").write_bytes(b"")
            mirrors = {event_v2[key] for key in ("response_mirror", "tokens_mirror")}
            for path in mirrors:
                path.touch()
            with trace_primary_inputs(fixture, suppress=mirrors) as opened:
                fit()
            event_v2_paths = {traced_input(fixture, path) for path in event_v2.values()}
            self.assertTrue(event_v2_paths <= opened)
            self.assert_contract_covers_reads(opened, "analysis")
            reads.update(opened)
            with trace_primary_inputs(fixture, suppress=mirrors):
                fixture.compare(self, fixture.export, fixture.keys, root, expect_kept=False)
            print(f"\nBYTES contract read trace: {len(reads)} normalized input paths covered", flush=True)

    def test_export_checks_all_authenticated_plan_candidates_before_fallback(self):
        with tempfile.TemporaryDirectory(prefix="bytes-export-plan-contract-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", "mock")
            with trace_primary_inputs(fixture) as reads:
                fixture.export_again(root / "fallback-export", root / "fallback-private", read_registration=True)
            self.assertIn(f"configs/b6/packs/{SESSION}/registration.json", reads)
            self.assert_contract_covers_reads(reads, "export")

            # The plan walk names the roles: the harvested roster has none.
            body = (json.dumps(fixture.plan["plan_tree"]) + "\n").encode()
            first = "pack/plan_tree.json"
            other = f"repo/configs/campaigns/{SESSION}/plan_tree.json"
            sources = fixture.archive / "sources"
            with (sources / "SHA256SUMS").open("a") as ledger:
                for name in (first, other):
                    candidate = sources / name
                    candidate.parent.mkdir(parents=True, exist_ok=True)
                    candidate.write_bytes(body)
                    ledger.write(f"{hashlib.sha256(body).hexdigest()}  {name}\n")

            def export(tag):
                with patch("os.fsync", return_value=None):
                    return agreement.export_runs.export(fixture.archive, {"plan_tree": json.loads(body)},
                        fixture.root / "registration", root / f"{tag}-private", root / f"{tag}-export",
                        evidence=fixture.evidence, pack_registration={"blinding_group": "bytes", "bytes_pass": 1})

            export("clean")
            for case in (first, other):
                for fault in CONTRACT["authenticated_plan_trees"]["faults"]:
                    with self.subTest(plan=case, fault=fault), file_fault(sources / case, fault):
                        with self.assertRaisesRegex(StorageStop, re.escape(case)):
                            export(f"{Path(case).parent.name}-{fault}")

    def test_run_report_matches_contract_rows(self):
        report = (agreement.ROOT / "docs/run_reports/2026-11-22-bytes-p1m1.md").read_text()
        documented = {line for line in report.splitlines() if line.startswith("| `")}
        for row in CONTRACT.values():
            fields = [f'`{row["path"]}`', row["phase"], row["primary"], *row["faults"].values(), row["flags"]]
            self.assertIn("| " + " | ".join(field.replace("|", r"\|") for field in fields) + " |", documented)

    def test_source_inventory_half_allows_export_when_required_proofs_survive(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-inventory-prefix-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                inventory = fixture.archive / "sources/SHA256SUMS"
                original = inventory.read_bytes()
                members = agreement.load(fixture.archive / "derived/roster.json")["members"]
                science = {member["run_id"] for member in members if member["units"]}
                reference = next(member["run_id"] for member in members if member["stage_id"] == "start_reference")
                reference_config = f"claim-runs/{reference}/config.json".encode()
                required, optional = [], []
                for row in original.splitlines(keepends=True):
                    path = Path(row.decode().strip().split("  ", 1)[1])
                    if len(path.parts) > 2 and path.parts[0] == "claim-runs" and path.parts[1] in science:
                        optional.append(row)
                    else:
                        required.append(row)
                target_bytes = len(original) // 2 - sum(map(len, required))
                self.assertGreaterEqual(target_bytes, 0)
                kept, lost = optional_inventory_prefix(optional, target_bytes)
                self.assertTrue(lost)
                prefix = b"".join(required + kept)
                reordered = prefix + b"".join(lost)
                self.assertCountEqual(reordered.splitlines(keepends=True), original.splitlines(keepends=True))
                self.assertEqual(len(prefix), len(reordered) // 2)
                inventory.write_bytes(reordered)
                fixture.export_again(root / "clean-export", root / "clean-private")
                with file_fault(inventory, "half"):
                    self.assertEqual(inventory.read_bytes(), prefix)
                    fixture.export_again(root / "half-export", root / "half-private")

                inventory.write_bytes(prefix + b"0123456789")
                with self.assertRaisesRegex(StorageStop, "reference inventory"):
                    fixture.export_again(root / "malformed-export", root / "malformed-private")
                without_proof = [row for row in required if row.rstrip().split(b"  ", 1)[1] != reference_config]
                self.assertEqual(len(without_proof), len(required) - 1)
                inventory.write_bytes(b"".join(without_proof + kept))
                with self.assertRaisesRegex(StorageStop, "config.json.*no SHA256SUMS proof"):
                    fixture.export_again(root / "missing-proof-export", root / "missing-proof-private")
                print(f"\nBYTES {timing} inventory: exact half omitted {len(lost)} optional science proofs", flush=True)

    def test_export_reads_chain_inputs_from_bound_custody_root(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-bound-chain-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                custody = root / "custom-controls"
                night = custody / "night"
                night.mkdir(parents=True)
                journal, result, hazard_result = (night / name for name in
                                                  ("chain-stages.jsonl", "result.json", "hazard_result.json"))
                journal.write_text('{"stage_id":"chain.complete","exit_code":0}\n')
                result.write_text('{"chain_exit_code":999999}\n')
                aliases = {path: f"custody_root/night/{path.name}" for path in (journal, result, hazard_result)}
                aliases[fixture.root / "registration"] = "registration_path"

                def export(tag):
                    reasons = []

                    def record_evidence(*args, **kwargs):
                        evidence = evidence_from_archive(*args, **kwargs)
                        reasons.append(evidence.stop_reason)
                        return evidence

                    with trace_primary_inputs(fixture, aliases=aliases) as reads, \
                            patch.object(agreement.export_runs, "evidence_from_archive", side_effect=record_evidence):
                        fixture.export_again(root / f"{tag}-export", root / f"{tag}-private", read_evidence=True,
                                             plan={**fixture.plan, "custody_root": str(custody)})
                    self.assert_contract_covers_reads(reads, "export")
                    reason, = reasons
                    return reads, reason

                reads, reason = export("bound-controls")
                self.assertEqual(reason, "chain_crashed")
                self.assertTrue(set(aliases.values()) <= reads)
                for fault in CONTRACT["chain_result"]["faults"]:
                    with self.subTest(result_fault=fault), file_fault(result, fault):
                        self.assertEqual(export(f"result-{fault}")[1], "completed")
                result.unlink()
                for fault in CONTRACT["chain_journal"]["faults"]:
                    with self.subTest(journal_fault=fault), file_fault(journal, fault):
                        self.assertEqual(export(f"journal-{fault}")[1], "chain_crashed")
                # The other terminal result filename is searched at the same bound root.
                journal.unlink()
                hazard_result.write_text('{"chain_exit_code":0}\n')
                self.assertEqual(export("hazard-result")[1], "completed")

    def test_bound_pack_plan_tree_is_authenticated_only_when_selected(self):
        with tempfile.TemporaryDirectory(prefix="bytes-bound-plan-contract-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", "mock")
            sources = fixture.archive / "sources"
            pack_root = sources / "custom-pack"
            pack_root.mkdir()
            candidate = pack_root / "plan_tree.json"
            # The plan walk names the roles: the harvested roster has none.
            body = (json.dumps(fixture.plan["plan_tree"]) + "\n").encode()
            candidate.write_bytes(body)
            ledger = sources / "SHA256SUMS"
            base = ledger.read_bytes()

            def bound_inventory(contents):
                return base + f"{hashlib.sha256(contents).hexdigest()}  {candidate.relative_to(sources)}\n".encode()

            ledger.write_bytes(bound_inventory(body))
            plan = {"pack_root": str(pack_root), "plan_tree": json.loads(body)}

            def export(tag):
                with patch("os.fsync", return_value=None), \
                        trace_primary_inputs(fixture, aliases={candidate: "pack_root/plan_tree.json"}) as reads:
                    agreement.export_runs.export(fixture.archive, plan, fixture.root / "registration",
                        root / f"{tag}-private", root / f"{tag}-export", evidence=fixture.evidence,
                        pack_registration={"blinding_group": "bytes", "bytes_pass": 1})
                self.assert_contract_covers_reads(reads, "export")
                return reads

            self.assertIn("pack_root/plan_tree.json", export("clean"))
            for fault in CONTRACT["bound_pack_plan_tree"]["faults"]:
                with self.subTest(fault=fault), file_fault(candidate, fault):
                    self.assertIn("pack_root/plan_tree.json", export(fault))

            # A truthy parse selects the bound candidate and requires authentication.
            non_object = b"[true]\n"
            for case, contents, inventory in (
                    ("digest-mismatch", b'{"stage_graph":[], "changed":true}\n', bound_inventory(body)),
                    ("no-proof", body, base),
                    ("non-object", non_object, bound_inventory(non_object))):
                with self.subTest(case=case):
                    candidate.write_bytes(contents)
                    ledger.write_bytes(inventory)
                    with self.assertRaisesRegex(StorageStop, r"custom-pack/plan_tree\.json"):
                        export(case)

            fixed = sources / "pack/plan_tree.json"
            fixed.parent.mkdir(exist_ok=True)
            fixed.write_bytes(body)
            ledger.write_bytes(base + f"{hashlib.sha256(body).hexdigest()}  pack/plan_tree.json\n".encode())
            self.assertNotIn("pack_root/plan_tree.json", export("fixed-first"))

    @unittest.skipUnless(shutil.which("zstd"), "compressed reference trace needs zstd")
    def test_export_restores_verified_reference_inventory(self):
        with tempfile.TemporaryDirectory(prefix="bytes-reference-restore-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", "mock")
            members = agreement.load(fixture.archive / "derived/roster.json")["members"]
            reference = next(member["run_id"] for member in members if member["stage_id"] == "start_reference")
            bundle = fixture.archive / "sources/claim-runs" / reference
            log = bundle / "logs/controller.log"
            log.parent.mkdir(exist_ok=True)
            body = b"synthetic reference controller note\n"
            log.write_bytes(body)
            sources = fixture.archive / "sources"
            with (sources / "SHA256SUMS").open("a") as ledger:
                ledger.write(f"{hashlib.sha256(body).hexdigest()}  {log.relative_to(sources)}\n")
            compress_member(bundle / "events.jsonl", fixture.archive)

            with trace_primary_inputs(fixture) as reads:
                fixture.export_again(root / "reference-export", root / "reference-private")
            self.assertTrue({"archive.desk/compression.jsonl", "bundle/logs/controller.log",
                             "bundle/status.json"} <= reads)
            self.assert_contract_covers_reads(reads, "export", restoring=True)

    def test_required_phase_pairs_follow_primary_marker_and_clock_rules(self):
        phases = ("idle_baseline", "tokenize", "decode")
        metadata = {"uncertainty_evidence": {"clock_anchor": {"clock_stamps": {"sampling_started": {
            "monotonic_before_s": 10, "epoch_s": 100}}}}}
        valid = [
            {"phase": phase, "event_type": kind, "timestamp_s": 100 + 2 * i + j, "metadata": {}}
            for i, phase in enumerate(phases)
            for j, kind in enumerate(("stage_started", "stage_completed") if i == 0 else ("phase_start", "phase_end"))
        ]
        valid[1]["metadata"] = {"monotonic_ns": 11_250_000_000}
        with tempfile.TemporaryDirectory(prefix="bytes-phase-pairing-") as directory:
            bundle = Path(directory)

            def spans(events, *, reference=True):
                (bundle / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))
                return bytes_twin.member_spans(bundle, metadata=metadata, reference=reference)

            expected = {phase: agreement.ba._event_span(valid, phase, metadata) for phase in phases}
            self.assertEqual(spans(valid), {"idle_ns": expected["idle_baseline"], "decode_ns": expected["decode"],
                                           "request_ns": [expected["tokenize"][0], expected["decode"][1]]})
            for i, phase in enumerate(phases):
                start, end = 2 * i, 2 * i + 1
                duplicate_alias = {**valid[end], "event_type": "phase_end" if i == 0 else "stage_completed"}
                variants = {"duplicate start": [*valid, valid[start]], "duplicate end": [*valid, valid[end]],
                            "duplicate alias": [*valid, duplicate_alias],
                            "missing start": valid[:start] + valid[start + 1:],
                            "missing end": valid[:end] + valid[end + 1:],
                            "nonpositive duration": valid[:end] + [{**valid[end], "metadata": {},
                                "timestamp_s": valid[start]["timestamp_s"]}] + valid[end + 1:]}
                for fault, events in variants.items():
                    with self.subTest(phase=phase, fault=fault):
                        with self.assertRaises(agreement.ba.AnalysisError):
                            agreement.ba._event_span(events, phase, metadata)
                        self.assertIsNone(spans(events))
                        science = spans(events, reference=False)
                        if phase == "tokenize":
                            self.assertEqual(science, {"idle_ns": expected["idle_baseline"],
                                                       "decode_ns": expected["decode"], "request_ns": None})
                        else:
                            self.assertIsNone(science)

    @unittest.skipUnless(shutil.which("zstd"), "compressed availability regression needs zstd")
    def test_plain_precedence_only_applies_outside_verified_restore(self):
        with tempfile.TemporaryDirectory(prefix="bytes-compressed-siblings-") as directory:
            archive = Path(directory) / "archive"
            bundle = archive / "sources/claim-runs/synthetic"
            bundle.mkdir(parents=True)
            config = bundle / "config.json"
            config.write_text("{}")
            (bundle / "metadata.json").write_text("{}")
            events = bundle / "events.jsonl"
            events.write_text("{}\n")
            journal = compress_member(config, archive)
            config.write_text("{}")
            with readable_run(bundle, compression_records=journal) as primary, bytes_twin._readable_bundle(bundle, journal) as twin:
                self.assertEqual((primary, twin), (bundle, bundle))
            compress_member(events, archive)
            for reader, refusal in ((lambda: readable_run(bundle, compression_records=journal), RestoreRefused),
                                     (lambda: bytes_twin._readable_bundle(bundle, journal), bytes_twin.StorageStop)):
                with self.assertRaisesRegex(refusal, "plain and compressed siblings are ambiguous"), reader():
                    self.fail("verified restore accepted duplicate logical inputs")

    def exercise(self, timing, rows, *, phases=PHASES, faults=FAULTS, expect_kept=None):
        compared = checked = export_stops = 0
        with tempfile.TemporaryDirectory(prefix=f"bytes-availability-{timing}-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", timing)
            targets = fixture.targets(fixture.export)
            for row_id in rows:
                self.assertEqual(tuple(CONTRACT[row_id]["faults"]), FAULTS)
                for fault in faults:
                    for phase in phases:
                        with self.subTest(timing=timing, file=row_id, fault=fault, phase=phase):
                            checked += 1
                            scratch = root / f"{row_id}-{fault}-{phase}"
                            scratch.mkdir()
                            heldout = row_id in {"export_sidecar", "withheld_csv"}
                            stage = "heldout" if heldout else "fit"
                            if phase == "after_export":
                                with file_fault(targets[row_id], fault):
                                    compared += fixture.compare(self, fixture.export, fixture.keys, scratch,
                                                                stage=stage, expect_kept=expect_kept)
                                continue
                            out = scratch / "export"
                            private = scratch / "private"
                            target = targets[row_id]
                            if row_id in {"export_csv", "export_sidecar", "withheld_csv"}:
                                target = out / target.relative_to(fixture.root / "export")
                                target.parent.mkdir(parents=True)
                            if row_id in {"pack_key", "config_key"}:
                                shutil.copytree(fixture.root / "private-keys", private)
                                target = private / "bytes/blinding" / target.name
                            with file_fault(target, fault):
                                if row_id == "export_sidecar" and fault != "absent":
                                    with self.assertRaisesRegex(ValueError, "BYTES export manifest: missing session binding"):
                                        fixture.export_again(out, private)
                                    export_stops += 1
                                    continue
                                try:
                                    export, keys = fixture.export_again(out, private)
                                except (StorageStop, OSError, ValueError, KeyError, TypeError) as exc:
                                    self.assertIn(row_id, {"events", "roster", "acceptance", "flags", "harvest_receipt",
                                                          "source_inventory", "pack_key", "config_key"}, type(exc).__name__)
                                    export_stops += 1
                                    continue
                                compared += fixture.compare(self, export, keys, scratch, stage=stage, expect_kept=expect_kept)
        print(f"\nBYTES {timing} availability: {checked} cases, {export_stops} export refusals, "
              f"{compared} comparisons", flush=True)

    def test_mock_timing_member_faults(self):
        self.exercise("mock", (row_id for row_id, row in CONTRACT.items() if row["scope"] == "member"))

    def test_native_timing_member_faults(self):
        self.exercise("native", (row_id for row_id, row in CONTRACT.items() if row["scope"] == "member"))

    def test_mock_timing_campaign_faults(self):
        self.exercise("mock", (row_id for row_id, row in CONTRACT.items() if row["scope"] == "campaign"))

    def test_native_timing_campaign_faults(self):
        self.exercise("native", (row_id for row_id, row in CONTRACT.items() if row["scope"] == "campaign"))

    def test_unreadable_reduction_drops_native_science_member(self):
        self.exercise("native", ["reduction"], phases=("after_export",), faults=("zero", "half"), expect_kept=False)

    def test_unavailable_native_trace_keeps_explicit_synthetic_summary(self):
        self.exercise("native", ["trace"], phases=("after_export",), faults=("absent", "half"), expect_kept=True)

    def test_duplicate_decode_end_drops_member_in_both_fit_clis(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-duplicate-phase-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing, complete_fit=True)
                clean = root / "clean"
                clean.mkdir()
                count = fixture.compare(self, fixture.export, fixture.keys, clean, expect_kept=True, fit_cli=True)
                path = fixture.bundle / "events.jsonl"
                lines = path.read_bytes().splitlines(keepends=True)
                index, = [i for i, line in enumerate(lines) if (event := json.loads(line)).get("phase") == "decode"
                          and event.get("event_type") == "phase_end"]
                lines.insert(index, lines[index])
                path.write_bytes(b"".join(lines))
                damaged = root / "duplicate"
                damaged.mkdir()
                count += fixture.compare(self, fixture.export, fixture.keys, damaged, expect_kept=False, fit_cli=True)
                print(f"\nBYTES {timing} duplicate decode end: {count} comparisons, zero above bar", flush=True)

    @unittest.skipUnless(shutil.which("zstd"), "compressed availability regression needs zstd")
    def test_absent_last_compressed_input_drops_member_without_refusing_fit(self):
        with tempfile.TemporaryDirectory(prefix="bytes-absent-compressed-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", "mock", complete_fit=True)
            path = fixture.bundle / "events.jsonl"
            journal = compress_member(path, fixture.archive)
            clean = root / "clean"
            clean.mkdir()
            count = fixture.compare(self, fixture.export, fixture.keys, clean, expect_kept=True, fit_cli=True)
            path.with_suffix(".jsonl.zst").unlink()
            self.assertTrue(journal.is_file())
            self.assertFalse(any(fixture.bundle.rglob("*.zst")))
            damaged = root / "missing"
            damaged.mkdir()
            count += fixture.compare(self, fixture.export, fixture.keys, damaged, expect_kept=False, fit_cli=True)
            print(f"\nBYTES last compressed input missing: {count} comparisons, zero above bar", flush=True)

    @unittest.skipUnless(shutil.which("zstd"), "compressed availability regression needs zstd")
    def test_compressed_restore_requires_metadata_and_copies_all_bundle_files(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-compressed-tree-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing, complete_fit=True)
                log = fixture.bundle / "logs/controller.log"
                log.parent.mkdir(exist_ok=True)
                log.write_bytes(b"synthetic controller note\n")
                journal = compress_member(fixture.bundle / "events.jsonl", fixture.archive)
                with trace_primary_inputs(fixture) as reads, readable_run(fixture.bundle, compression_records=journal):
                    pass
                self.assertTrue({"bundle/status.json", "bundle/logs/controller.log"} <= reads)
                self.assert_contract_covers_reads(reads, "analysis", restoring=True)
                control = root / "control"
                control.mkdir()
                count = fixture.compare(self, fixture.export, fixture.keys, control, fit_cli=True, expect_kept=True)
                original = Path.open

                def deny_log(path, mode="r", *args, **kwargs):
                    if path == log and mode.startswith("r"):
                        raise PermissionError(errno.EACCES, "fixture permission denied", str(path))
                    return original(path, mode, *args, **kwargs)

                denied = root / "denied"
                denied.mkdir()
                with patch.object(Path, "open", deny_log):
                    count += fixture.compare(self, fixture.export, fixture.keys, denied, fit_cli=True, expect_exit=1)

                missing = root / "missing"
                missing.mkdir()
                with file_fault(fixture.bundle / "metadata.json", "absent"):
                    count += fixture.compare(self, fixture.export, fixture.keys, missing, fit_cli=True, expect_exit=1)
                print(f"\nBYTES {timing} compressed tree: {count} comparisons; both faults refused", flush=True)

    def test_bad_utf8_in_v2_request_file_drops_member_in_both_fit_clis(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-v2-utf8-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing, complete_fit=True)
                requests = event_v2_inputs(fixture, sparse=True)["request_rows"]
                control = root / "control"
                control.mkdir()
                count = fixture.compare(self, fixture.export, fixture.keys, control, fit_cli=True, expect_kept=True)
                bad = root / "garbage"
                bad.mkdir()
                with file_fault(requests, "garbage"):
                    count += fixture.compare(self, fixture.export, fixture.keys, bad, fit_cli=True, expect_kept=False)
                print(f"\nBYTES {timing} v2 request UTF-8: {count} comparisons, zero above bar", flush=True)

    def test_required_phase_event_without_type_drops_member_in_both_fit_clis(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-phase-event-type-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing, complete_fit=True)
                control = root / "control"
                control.mkdir()
                count = fixture.compare(self, fixture.export, fixture.keys, control, fit_cli=True, expect_kept=True)
                with (fixture.bundle / "events.jsonl").open("ab") as events:
                    events.write(b'{"phase":"decode"}\n')
                bad = root / "missing-type"
                bad.mkdir()
                count += fixture.compare(self, fixture.export, fixture.keys, bad, fit_cli=True, expect_kept=False)
                print(f"\nBYTES {timing} missing event type: {count} comparisons, zero above bar", flush=True)

    def test_v2_summary_fields_drop_historical_member_in_both_fit_clis(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-summary-layout-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing, complete_fit=True)
                summary = fixture.bundle / "summary_metrics.json"
                historical = agreement.load(summary)
                control = root / "control"
                control.mkdir()
                count = fixture.compare(self, fixture.export, fixture.keys, control, fit_cli=True,
                                        expect_exit=0, expect_kept=True)
                fields = {"batch_group_gross_energy_j": {}, "decode_counter_rollup": None, "request_decode_metrics": []}
                for field, value in fields.items():
                    with self.subTest(field=field):
                        scratch = root / field
                        scratch.mkdir()
                        agreement._write(summary, {**historical, field: value})
                        count += fixture.compare(self, fixture.export, fixture.keys, scratch, fit_cli=True,
                                                 expect_exit=0, expect_kept=False)
                print(f"\nBYTES {timing} historical summary with event-v2 fields: {count} comparisons, zero above bar",
                      flush=True)

    @unittest.skipUnless(shutil.which("zstd"), "logical reduction regression needs zstd")
    def test_compressed_archive_reduction_faults_drop_only_the_member(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-logical-reduction-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing, complete_fit=True)
                reduction = fixture.targets(fixture.export)["reduction"]
                subprocess.run(["zstd", "-q", "--rm", str(reduction)], check=True)
                compressed = reduction.with_name(reduction.name + ".zst")
                self.assert_contract_covers_reads({compressed.relative_to(fixture.archive).as_posix()}, "analysis")
                control = root / "control"
                control.mkdir()
                compared = fixture.compare(self, fixture.export, fixture.keys, control, fit_cli=True,
                                           expect_exit=0, expect_kept=True)
                for fault in CONTRACT["reduction"]["faults"]:
                    with self.subTest(fault=fault), file_fault(compressed, fault):
                        scratch = root / fault
                        scratch.mkdir()
                        compared += fixture.compare(self, fixture.export, fixture.keys, scratch, fit_cli=True,
                                                    expect_exit=0, expect_kept=False)
                invalid_text = subprocess.run(["zstd", "-qc"], input=b"\xffbroken input\n",
                                              capture_output=True, check=True).stdout
                compressed.write_bytes(invalid_text)
                scratch = root / "decode"
                scratch.mkdir()
                compared += fixture.compare(self, fixture.export, fixture.keys, scratch, fit_cli=True,
                                            expect_exit=0, expect_kept=False)
                print(f"\nBYTES {timing} compressed reduction: {compared} comparisons, zero above bar", flush=True)

    def test_non_object_member_metadata_refuses_both_fit_clis(self):
        malformed_shapes = {"array": [], "null": None, "boolean": False, "number": 0, "string": "",
                            "nested_array": {"workload_observed": []}}
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-metadata-shape-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing, complete_fit=True)
                target = fixture.bundle / "metadata.json"
                control = root / "control"
                control.mkdir()
                compared = fixture.compare(self, fixture.export, fixture.keys, control, fit_cli=True,
                                           expect_exit=0, expect_kept=True)
                for shape, document in malformed_shapes.items():
                    with self.subTest(shape=shape):
                        agreement._write(target, document)
                        scratch = root / shape
                        scratch.mkdir()
                        compared += fixture.compare(self, fixture.export, fixture.keys, scratch, fit_cli=True,
                                                    expect_exit=1)
                        self.assertFalse((scratch / "primary").exists())
                        self.assertFalse((scratch / "twin.json").exists())
                agreement._write(target, {})
                scratch = root / "empty-object"
                scratch.mkdir()
                compared += fixture.compare(self, fixture.export, fixture.keys, scratch, fit_cli=True,
                                            expect_exit=0, expect_kept=False)
                print(f"\nBYTES {timing} metadata shape: {compared} comparisons, zero above bar", flush=True)

    def test_bundle_restored_after_export_supplies_unblinded_science_record(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-bundle-return-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                held = root / "temporarily-absent-bundle"
                fixture.bundle.rename(held)
                try:
                    export, keys = fixture.export_again(root / "export", root / "private", grouped=False)
                finally:
                    held.rename(fixture.bundle)
                exported, = [row for row in bytes_twin.read_export(export) if row["run_id"] == fixture.member]
                self.assertIsNone(exported["model_name"])
                self.assertEqual(exported["status"], "succeeded")
                self.assertGreater(fixture.compare(self, export, keys, root, expect_kept=True), 100)

    def test_export_absences_repaired_before_analysis(self):
        compared = checked = 0
        for timing in ("mock", "native"):
            with tempfile.TemporaryDirectory(prefix=f"bytes-repaired-files-{timing}-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                targets = fixture.targets(fixture.export)
                rows = [row_id for row_id, row in CONTRACT.items() if row["scope"] == "member"] + ["meter"]
                for row_id in rows:
                    with self.subTest(timing=timing, file=row_id):
                        scratch = root / row_id
                        scratch.mkdir()
                        with file_fault(targets[row_id], "absent"):
                            export, keys = fixture.export_again(scratch / "export", scratch / "private", grouped=False)
                        compared += fixture.compare(self, export, keys, scratch, expect_kept=True)
                        checked += 1
        print(f"\nBYTES restored export inputs: {checked} cases, {compared} comparisons", flush=True)

    def check_smoke_witness_faults(self, fixture, root):
        pack = fixture.archive / "sources/pack"
        pack.mkdir(parents=True, exist_ok=True)
        witness = pack / "smoke-registered-tree.json"
        # Reuse the registered graph shape with no registered member inputs.
        tree = agreement.load(agreement.ROOT / "configs/campaigns" / SESSION / "plan_tree.json")
        tree["external_inputs"] = []
        tree["science"] = []
        keep = {stage["stage_id"]: 1 for stage in tree["stage_graph"] if stage["kind"] == "campaign_collection"}
        plan = pack / "plan_tree.json"
        agreement._write(witness, tree)
        agreement._write(plan, reduce_tree(tree, keep))
        with (fixture.archive / "sources/SHA256SUMS").open("a") as inventory:
            for path in (plan, witness):
                inventory.write(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  pack/{path.name}\n")

        with trace_primary_inputs(fixture) as reads:
            export, keys = fixture.export_again(root / "smoke-control-export", root / "smoke-control-private")
        key = "sources/pack/smoke-registered-tree.json"
        self.assertIn(key, reads)
        self.assert_contract_covers_reads(reads, "export")
        cases = compared = 0
        for fault in CONTRACT["smoke_witness"]["faults"]:
            for phase in PHASES:
                with self.subTest(file="smoke_witness", fault=fault, phase=phase):
                    scratch = root / f"smoke-{fault}-{phase}"
                    scratch.mkdir()
                    with file_fault(witness, fault), trace_primary_inputs(fixture) as reads:
                        if phase == "before_export":
                            with self.assertRaisesRegex(StorageStop, r"smoke-registered-tree\.json"):
                                fixture.export_again(scratch / "export", scratch / "private")
                            self.assertIn(key, reads)
                            compared += 1
                        else:
                            compared += fixture.compare(self, export, keys, scratch)
                            self.assertNotIn(key, reads)
                    cases += 1
        return cases, compared

    def check_control_files(self, timing):
        with tempfile.TemporaryDirectory(prefix=f"bytes-availability-controls-{timing}-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", timing)
            archive = fixture.archive
            capture = archive / "sources/pre-calibration"
            controls = {
                "raw_powermetrics": (fixture.bundle / "raw/powermetrics.plist", b"synthetic inactive capture"),
                "cal_manifest": (fixture.bundle / "validation-manifest.json", b'{"artifacts": {}}'),
                "cal_evidence": (fixture.bundle / "instrument_evidence.json", b'{"status":"valid"}'),
                "cal_members": (fixture.bundle / "calibration/events.jsonl", b'{"fixture_event":true}\n'),
                "member_assessments": (archive / "withheld/member-assessments.json", b'{"members": {}}'),
                "export_registration": (archive / "sources/pack/registration.json",
                    json.dumps({"pack_id": SESSION, "blinding_group": "bytes", "bytes_pass": 1}).encode()),
                "export_key_binding": (fixture.private.parent / "blinding-sessions" / f"{SESSION}.json", None),
                "spans": (archive / "withheld/spans.json", b'{"spans": {}}'),
                "chain_journal": (archive / "night/chain-stages.jsonl", b'{"stage_id":"chain.complete","exit_code":0}\n'),
                "chain_result": (archive / "night/result.json", b'{"chain_exit_code":0}'),
                "neg8_screen": (archive / "withheld/b6-neg8.json", b'{"verdict":"synthetic"}'),
                "capture_evidence": (capture / "instrument_evidence.json", b'{"b_fiducial_s":0.04}'),
                "capture_raw": (capture / "raw/powermetrics.plist", b"synthetic optional capture"),
            }
            self.assertEqual(set(controls) | {"compression", "registered_manifest", "smoke_witness"}, {
                row_id for row_id, row in CONTRACT.items() if row["scope"].startswith("conditional_")})
            for file, seed in controls.values():
                if seed is not None:
                    file.parent.mkdir(parents=True, exist_ok=True)
                    file.write_bytes(seed)
            before_evidence = {"spans", "chain_journal", "chain_result", "neg8_screen", "capture_evidence", "capture_raw"}
            cases = compared = 0
            for row_id, (file, _) in controls.items():
                for fault in CONTRACT[row_id]["faults"]:
                    for phase in PHASES:
                        with self.subTest(timing=timing, file=row_id, fault=fault, phase=phase):
                            cases += 1
                            if phase == "before_export" and row_id in before_evidence:
                                # This is the producer's optional-evidence reader; the twin starts at its export.
                                with file_fault(file, fault):
                                    evidence = evidence_from_archive(archive, {"pre_calibration_dir": str(capture)}, root)
                                self.assertEqual(evidence.pack_id, SESSION)
                                compared += 1
                                continue
                            scratch = root / f"{row_id}-{fault}-{phase}"
                            scratch.mkdir()
                            if phase == "before_export" and row_id in {"member_assessments", "export_registration",
                                                                      "export_key_binding"}:
                                private = scratch / "private"
                                shutil.copytree(fixture.root / "private-keys", private)
                                target = (private / "bytes/blinding-sessions" / f"{SESSION}.json"
                                          if row_id == "export_key_binding" else file)
                                with file_fault(target, fault):
                                    if row_id == "export_key_binding":
                                        with self.assertRaises(ValueError):
                                            fixture.export_again(scratch / "export", private)
                                        compared += 1
                                        continue
                                    export, keys = fixture.export_again(scratch / "export", private,
                                                                          read_registration=row_id == "export_registration")
                                    compared += fixture.compare(self, export, keys, scratch)
                            else:
                                with file_fault(file, fault):
                                    if phase == "before_export":
                                        export, keys = fixture.export_again(scratch / "export", scratch / "private")
                                    else:
                                        export, keys = fixture.export, fixture.keys
                                    compared += fixture.compare(self, export, keys, scratch)
            smoke_cases, smoke_compared = self.check_smoke_witness_faults(fixture, root)
            print(f"\nBYTES {timing} optional controls: {cases + smoke_cases} cases, "
                  f"{compared + smoke_compared} comparisons", flush=True)

    def test_mock_timing_control_faults(self):
        self.check_control_files("mock")

    def test_native_timing_control_faults(self):
        self.check_control_files("native")

    def check_admission(self, timing):
        with tempfile.TemporaryDirectory(prefix=f"bytes-availability-admission-{timing}-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", timing)
            repo, prediction, receipt, commit = commitment_fixture(root)
            journal = repo / bytes_commitment.JOURNAL
            release = root / "release.json"
            release.write_text('{"stage":"fit"}')
            entry = {"event": "heldout_rows", "unblinded_utc": "2026-11-02T10:00:00+00:00", "stage1_commit": commit}
            journal.write_text((json.dumps(entry) + "\n") * 2)
            commit_journal(repo)
            source = repo / "joulewise/bytes_analysis.py"
            locator = {"prediction": (prediction, prediction.with_suffix(".sha256")), "push_receipt": (receipt,),
                       "journal": (journal,), "release_record": (release,), "source_digests": (source,)}
            self.assertEqual(set(locator), {row_id for row_id, row in CONTRACT.items() if row["scope"] == "commitment"})
            original_blob = bytes_commitment._blob

            def blob(tree, revision, path, **kwargs):
                if path == "joulewise/bytes_analysis.py":
                    return source.read_bytes()
                return original_blob(tree, revision, path, **kwargs)

            comparisons = 0
            for row_id, files in locator.items():
                for file in files:
                    for fault in CONTRACT[row_id]["faults"]:
                        for phase in PHASES:
                            with self.subTest(timing=timing, file=file.name, fault=fault, phase=phase):
                                expected = row_id == "release_record" and fault == "absent"
                                with file_fault(file, fault), patch.object(bytes_commitment, "ROOT", repo), patch.object(
                                        bytes_commitment, "_blob", side_effect=blob), patch.object(
                                        bytes_commitment.bytes_integrity, "verify"):
                                    if phase == "before_export":
                                        scratch = root / f"{file.name}-{fault}-{phase}"
                                        fixture.export_again(scratch / "export", scratch / "private")
                                    if expected:
                                        bytes_commitment.verify_commitment(commit, prediction, repo=repo,
                                                                                receipt=receipt, unblinding_records=(release,))
                                    else:
                                        with self.assertRaises((OSError, ValueError, KeyError, TypeError)):
                                            bytes_commitment.verify_commitment(commit, prediction, repo=repo,
                                                                                    receipt=receipt, unblinding_records=(release,))
                                comparisons += 1
            print(f"\nBYTES {timing} shared admission: {comparisons} file-fault comparisons", flush=True)

    def test_mock_timing_admission_faults(self):
        self.check_admission("mock")

    def test_native_timing_admission_faults(self):
        self.check_admission("native")

    def test_registered_manifest_file_faults(self):
        checked = 0
        for timing in ("mock", "native"):
            with tempfile.TemporaryDirectory(prefix="bytes-registered-manifest-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                registered = root / "configs/bytes/bytes_manifest.json"
                registered.parent.mkdir(parents=True)
                shutil.copyfile(agreement.ROOT / "configs/bytes/bytes_manifest.json", registered)
                for fault in CONTRACT["registered_manifest"]["faults"]:
                    for phase in PHASES:
                        with self.subTest(timing=timing, fault=fault, phase=phase):
                            scratch = root / f"{fault}-{phase}"
                            scratch.mkdir()
                            with file_fault(registered, fault):
                                export, keys = ((fixture.export, fixture.keys) if phase == "after_export" else
                                                fixture.export_again(scratch / "export", scratch / "private"))
                                agreement.ba._registered_predictors.cache_clear()
                                try:
                                    with chdir(root), patch.object(agreement.ba, "__file__", root / "joulewise/bytes_analysis.py"), \
                                            patch.object(bytes_twin, "__file__", root / "scripts/bytes_twin.py"):
                                        self.assertEqual(fixture.compare(self, export, keys, scratch), 1)
                                        checked += 1
                                finally:
                                    agreement.ba._registered_predictors.cache_clear()
        print(f"\nBYTES registered manifest: {checked} file-fault comparisons", flush=True)

    @unittest.skipUnless(shutil.which("zstd"), "compressed-file fault matrix needs zstd")
    def test_compressed_member_and_journal_faults(self):
        compared = checked = export_stops = 0
        for timing in ("mock", "native"):
            with tempfile.TemporaryDirectory(prefix="bytes-compression-faults-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                member = fixture.bundle / "events.jsonl"
                compress_member(member, fixture.archive)
                journal = Path(str(fixture.archive) + ".desk") / "compression.jsonl"
                for row, file in (("compression", journal), ("compressed_member", member.with_suffix(".jsonl.zst"))):
                    for fault in CONTRACT[row]["faults"]:
                        for phase in PHASES:
                            with self.subTest(timing=timing, file=file.name, fault=fault, phase=phase):
                                checked += 1
                                scratch = root / f"{file.name}-{fault}-{phase}"
                                scratch.mkdir()
                                with file_fault(file, fault):
                                    try:
                                        export, keys = ((fixture.export, fixture.keys) if phase == "after_export" else
                                                        fixture.export_again(scratch / "export", scratch / "private"))
                                    except OSError as exc:
                                        self.assertEqual(file.suffix, ".zst")
                                        self.assertEqual(exc.errno, errno.EIO)
                                        export_stops += 1
                                    else:
                                        compared += fixture.compare(self, export, keys, scratch)
        print(f"\nBYTES compressed inputs: {checked} cases, {export_stops} export refusals, {compared} comparisons", flush=True)

    def test_native_reader_authenticates_each_required_capture_input(self):
        with tempfile.TemporaryDirectory(prefix="bytes-native-availability-") as directory:
            bundle = Path(directory)
            calibration = bundle / "calibration"
            processor = {**{rail + "_power": 1000.0 for rail in ("cpu", "gpu", "ane")},
                         **{rail + "_energy": 1000 for rail in ("cpu", "gpu", "ane")}}
            frame = plistlib.dumps({"timestamp": "2026-11-01T10:00:00Z", "elapsed_ns": 1_000_000_000,
                                    "processor": processor})
            capture = frame + b"\0" + frame

            def artifact(path, raw):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
                return hashlib.sha256(raw).hexdigest()

            capture_file = bundle / "raw/powermetrics.plist"
            artifact(capture_file, capture)
            hashes = {"raw/powermetrics.plist": artifact(calibration / "raw/powermetrics.plist", capture),
                      "events.jsonl": artifact(calibration / "events.jsonl", b'{"event_type":"synthetic"}\n')}
            evidence = calibration / "instrument_evidence.json"
            evidence_sha = artifact(evidence, json.dumps({"artifact_sha256": hashes}).encode())
            manifest = calibration / "manifest.json"
            manifest_sha = artifact(manifest, json.dumps({
                "schema_version": "joulewise.instrument_validation_manifest.v1",
                "artifacts": {**hashes, evidence.name: evidence_sha},
            }).encode())
            metadata = {"device": {"telemetry": "powermetrics"}, "instrument_calibration": {
                "validation_manifest_path": "calibration/manifest.json", "validation_manifest_sha256": manifest_sha,
                "artifact_path": "calibration/instrument_evidence.json", "artifact_sha256": evidence_sha,
                "b_fiducial_s": 0.04}}
            calibration_metadata = metadata["instrument_calibration"]
            # This clean manifest passes the primary's custody check. Its
            # minimal evidence deliberately stops at the subsequent schema gate.
            self.assertEqual(_verify_instrument_calibration(BundleReader(bundle), metadata, calibration_metadata),
                             (None, "instrument_calibration_schema_mismatch"))
            trace = [(0.0, 1.0, 3.0), (1.0, 2.0, 3.0)]
            bytes_twin._verify_native_trace(trace, bytes_twin._native_science_inputs(bundle, metadata, "0.5.2"))
            files = {"raw_powermetrics": capture_file, "cal_manifest": manifest, "cal_evidence": evidence,
                     "cal_members": calibration / "events.jsonl"}
            resolved_manifest = manifest.resolve()
            manifest_opened = False
            original_open = Path.open

            def observe_manifest(path, mode="r", *args, **kwargs):
                nonlocal manifest_opened
                if path == resolved_manifest and mode.startswith("r"):
                    manifest_opened = True
                return original_open(path, mode, *args, **kwargs)

            for row_id, file in files.items():
                for fault in CONTRACT[row_id]["faults"]:
                    with self.subTest(file=row_id, fault=fault), file_fault(file, fault):
                        if row_id == "cal_manifest":
                            manifest_opened = False
                            with patch.object(Path, "open", observe_manifest):
                                result = _verify_instrument_calibration(BundleReader(bundle), metadata, calibration_metadata)
                            self.assertEqual(result, (None, "instrument_calibration_invalid"))
                            self.assertEqual(manifest_opened, fault != "absent")
                        with self.assertRaises((ValueError, OSError)):
                            inputs = bytes_twin._native_science_inputs(bundle, metadata, "0.5.2")
                            bytes_twin._verify_native_trace(trace, inputs)

    def test_reference_export_authenticates_calibration_manifest_faults(self):
        for timing in ("mock", "native"):
            with self.subTest(timing=timing), tempfile.TemporaryDirectory(prefix="bytes-calibration-inventory-") as directory:
                root = Path(directory)
                fixture = AvailabilityFixture(root / "base", timing)
                members = agreement.load(fixture.archive / "derived/roster.json")["members"]
                reference = next(member["run_id"] for member in members if member["stage_id"] == "start_reference")
                sources = fixture.archive / "sources"
                manifest = sources / "claim-runs" / reference / "calibration/manifest.json"
                manifest.parent.mkdir(exist_ok=True)
                body = b'{"schema_version":"joulewise.instrument_validation_manifest.v1","artifacts":{}}\n'
                manifest.write_bytes(body)
                with (sources / "SHA256SUMS").open("a") as ledger:
                    ledger.write(f"{hashlib.sha256(body).hexdigest()}  {manifest.relative_to(sources)}\n")

                key = "instrument_calibration.validation_manifest_path"
                with trace_primary_inputs(fixture, aliases={manifest: key}) as reads:
                    fixture.export_again(root / "clean-export", root / "clean-private")
                self.assertIn(key, reads)
                self.assert_contract_covers_reads(reads, "export")
                for fault in CONTRACT["cal_manifest"]["faults"]:
                    with self.subTest(fault=fault), file_fault(manifest, fault):
                        with self.assertRaisesRegex(StorageStop, r"calibration/manifest\.json"):
                            fixture.export_again(root / f"{fault}-export", root / f"{fault}-private")

    def test_planned_run_lost_from_withheld_rows_agrees_on_the_harvest_roster(self):
        # Cold review of #949: a withheld store loses a planned held-out row after export. The
        # harvest's roster names units and no role; both programs keep the run as unusable.
        with tempfile.TemporaryDirectory(prefix="bytes-lost-withheld-row-") as directory:
            root = Path(directory)
            fixture = AvailabilityFixture(root / "base", "mock")
            members = {member["run_id"]: member
                       for member in agreement.load(fixture.archive / "derived/roster.json")["members"]}
            self.assertEqual({key for member in members.values() for key in member},
                             {"run_id", "stage_id", "kind", "units"})
            store = fixture.targets(fixture.export)["withheld_csv"]
            lines = store.read_text().splitlines(keepends=True)
            lost = next(csv.DictReader(lines[:1] + lines[-1:]))["run_id"]
            self.assertTrue(members[lost]["units"])
            store.write_text("".join(lines[:-1]))
            scratch = root / "scratch"
            scratch.mkdir()
            self.assertGreater(fixture.compare(self, fixture.export, fixture.keys, scratch, stage="heldout"), 0)
