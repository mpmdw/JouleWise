"""DESK ONLY: committed-GAMMA preparation and the block-4 joined replay.

Before GAMMA is frozen (main), the joined acceptance cases SKIP at the D-134
freeze stop: the real writer and ARM issuer refuse an unfrozen pack.

On a frozen GAMMA (a throwaway clone after freeze-0004), each joined case runs
ONE desk occurrence chain -- a1, a2, the G10 control, then s1 -- through the
real writer, ARM-only path, driver, closeout and both harvesters. Only the
physical seams in ``PHYSICAL_SEAMS`` are replaced, each by a labelled method
of ``PhysicalSeams``. A step that reaches any other physical command, or an
authority a desk cannot hold, STOPS there with a FLAG naming file:line; it is
never stubbed. No ARM, plan loader, pack authenticator, census, evaluator or
harvester is replaced. The started-occurrence controls below are component
controls; they do not certify a completed joined occurrence.
"""
import inspect
import io
import shlex
import shutil
from pathlib import Path
from types import SimpleNamespace
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from joulewise import arm_readiness as ar, night_gate, t0_rehearsal
from joulewise import arm_readiness_evidence_t0 as t0_author
from joulewise import v5_qualification as q
from joulewise.night_plan_writer import write_night_plan
from scripts import harvest_v5_g2b_window as g2b, run_night as driver
from scripts import harvest_v5_qualification as qualification
from scripts import write_v5_qualification_plan as writer
from scripts import capture_t0_step as capture, check_v5_arm_abort as checker
from tests.test_kernel_clock import frequency_probe


SCRATCH = (Path(tempfile.gettempdir()) / "v5-block4-replay").resolve()
PACK_RELATIVE = "configs/campaigns/" + writer.GAMMA
# The GAMMA pack's reviewed source: bda1c180 until the block-5 timing lane regenerated the
# _v5 packs (idle_seconds 57.6, block-5 policy file) at f4cf9047; lane L10's distinct interior
# reference run ids (GAMMA-INTERIOR-REFERENCES-01) regenerated it again (c6309e1a); the NEG-8
# survivors lane's spare-slot retry (2026-10-07) regenerated it with its own generator, and that
# commit is now the source.
PACK_SOURCE_COMMIT = "2011ec285ce6e4e22a3056ebbc806cf218a3b805"


def put(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(ar.render_json(value))
    return q.reference(path)


# The only seams this replay may replace (addendum C item 6).
PHYSICAL_SEAMS = ("sudo/systemsetup", "powermetrics sampler", "model inference", "ioreg battery read",
                  "HID idle read", "sntp collector", "wall/monotonic clocks", "launchctl")


def source_line(function, needle):
    """file:line of the first source line of ``function`` containing ``needle``."""
    lines, start = inspect.getsourcelines(function)
    path = Path(inspect.getsourcefile(function)).resolve().relative_to(writer.REPO_ROOT.resolve()).as_posix()
    return f"{path}:{start + next(i for i, value in enumerate(lines) if needle in value)}"


def capture_flags():
    """FLAGs for the native T-0 stage commands outside PHYSICAL_SEAMS."""
    quiet = source_line(capture._command_for_step, "quiet_mac_prep.sh")
    prewindow = source_line(capture._command_for_step, "return context.prewindow_command")
    return {
        "quiet-mac-prep": (f"FLAG {quiet}: T-0 step quiet-mac-prep runs scripts/quiet_mac_prep.sh, whose "
                           "physical commands are outside the authorised seams: osascript (quits every "
                           "foreground app), pmset -g batt / displaysleepnow / -g systemstate, defaults "
                           "-currentHost read com.apple.screensaver, ps/pgrep process census. Not stubbed."),
        "prewindow-check": (f"FLAG {prewindow}: T-0 step prewindow-check runs joulewise/prewindow.py --t0-wait, "
                            "whose ps CPU census, uptime and pmset -g batt probes are outside the "
                            "authorised seams. Not stubbed."),
    }


def changed_set_flag(detail):
    """FLAG for a pack frozen at a head older than this checkout's reviewed HEAD."""
    where = source_line(ar.validate_r1_evidence_lifecycle, "reviewed HEAD changed relevant path(s)")
    return (f"FLAG {where}: GAMMA was frozen before this checkout's reviewed HEAD ({detail}). "
            "Procedure stop, not a seam: freeze at a head that already contains these bytes.")


class UnlistedPhysicalSeam(Exception):
    """A physical command outside PHYSICAL_SEAMS was reached; the step stops."""

    def __init__(self, argv, flag):
        super().__init__(flag)
        self.argv = list(argv)
        self.flag = flag


class PhysicalSeams:
    """Each branch replaces exactly one physical seam and says which.

    Any other command raises UnlistedPhysicalSeam before executing, so this
    replay can never run a real privileged, network or machine-state command.
    """

    PEERS = {"time.apple.com": "17.253.4.45", "pool.ntp.org": "192.0.2.20", "time.nist.gov": "129.6.15.28"}

    def __init__(self):
        self.calls = []
        self.flags = capture_flags()

    def sntp(self, argv):
        # SEAM sntp collector: one report-only /usr/bin/sntp leg; no network.
        argv = list(argv)
        self.calls.append(("sntp collector", argv))
        server = argv[-1]
        return subprocess.CompletedProcess(argv, 0, f"+0.010000 +/- 0.020000 {server} {self.PEERS[server]}\n".encode(), b"")

    def execute(self, argv, *, cwd=None, **_):
        argv = list(argv)
        name = Path(argv[1]).name if len(argv) > 1 else ""
        if argv[:3] == ["/usr/bin/sudo", "-n", "/usr/sbin/systemsetup"] and argv[3] == "-setusingnetworktime":
            # SEAM sudo/systemsetup: the network-time setter; machine state is untouched.
            self.calls.append(("sudo/systemsetup", argv))
            return subprocess.CompletedProcess(argv, 0, f"setUsingNetworkTime: {argv[4].capitalize()}\n".encode(), b"")
        if name == "collect_clock_reference.py" and argv[2:] == []:
            # PROCESS BOUNDARY, not a seam: the same collector main() runs in-process
            # so that its one physical seam, the sntp collector, is all that is replaced.
            from scripts import collect_clock_reference as collector
            stream = io.BytesIO()
            code = collector.main([], runner=self.sntp, stdout=stream)
            return subprocess.CompletedProcess(argv, code, stream.getvalue(), b"")
        if name == "quiet_mac_prep.sh":
            raise UnlistedPhysicalSeam(argv, self.flags["quiet-mac-prep"])
        if name == "prewindow.py":
            raise UnlistedPhysicalSeam(argv, self.flags["prewindow-check"])
        raise UnlistedPhysicalSeam(argv, "FLAG unclassified command reached: " + shlex.join(argv))

    def observed_run(self, argv, *args, **kwargs):
        argv = list(argv)
        if len(argv) > 2 and Path(argv[1]).name == "capture_t0_step.py" and argv[2] == "sequence":
            # PROCESS BOUNDARY, not a seam: scripts/capture_t0_step.py main() runs with the
            # identical argv in-process; every command it issues goes through execute().
            stream = SimpleNamespace(buffer=io.BytesIO())
            with mock.patch.object(capture, "_execute", self.execute), mock.patch.object(sys, "stdout", stream):
                code = capture.main(argv[2:])
            return subprocess.CompletedProcess(argv, code, stream.buffer.getvalue(), b"")
        raise UnlistedPhysicalSeam(argv, "FLAG unclassified process reached: " + shlex.join(argv))

    def installed(self):
        return mock.patch.object(t0_rehearsal, "observed_run", self.observed_run)


class JoinedDesk:
    """Desk inputs for one occurrence: fresh roots, window.env, rendered chain.

    Everything here is operator-authored input that the real tools then read;
    nothing replaces a validator. The confirmation table is the committed
    test's schema-only diagnostic input and must NEVER authorize a launch.
    """

    def __init__(self, root, pack):
        self.root, self.pack = root, pack
        self.head = subprocess.check_output(["git", "-C", str(writer.REPO_ROOT), "rev-parse", "HEAD"], text=True).strip()
        self.digest = ar.committed_pack_tree_sha256(pack)
        self.sizing = writer.read_object(writer.REPO_ROOT / "configs/campaigns/v5_qualification_25g83/sizing_allowances.json")
        self.template = root / "reviewed-chain.zsh"
        self.template.write_text(writer.g2b_body(writer.REPO_ROOT))
        self.tree, _ = ar._plan_tree(pack)
        self.frozen_plan, _, self.plan_id, _ = ar.resolve_frozen_plan(pack, self.tree)

    def confirmation(self, occurrence):
        from tests.test_family_marker import confirmation
        table = self.root / (occurrence + "-schema-only-confirmation.json")
        put(table, confirmation())
        table.with_name(table.name + ".sha256").write_bytes(ar.gnu_sidecar(q.sha(table), table.name))
        transcript = self.root / (occurrence + "-schema-only-transcript.txt")
        transcript.write_text("DESK SCHEMA INPUT ONLY " + q.sha(table) + "\n")
        record = self.root / (occurrence + "-confirmation-record.json")
        put(record, {"table_path": str(table), "table_sha256": q.sha(table), "transcript_sha256": q.sha(transcript),
            "confirmed_at": {"epoch_s": 0.0, "iso8601_utc": "1970-01-01T00:00:00.000000Z"}})
        return {"record": q.reference(record), "transcript": q.reference(transcript),
                "expected_confirmation_digest": q.sha(table)}

    def stage(self, occurrence, t0_epoch_s):
        from tests.test_arm_readiness_schemas import arm_context
        custody = self.root / occurrence
        window = custody / "window"
        window.mkdir(parents=True)
        arm_base = self.root / (occurrence + "-arm")
        arm_base.mkdir()
        context = arm_context(arm_base)
        for name in ("custody_root", "claim_runs_root", "bound_runs_root", "quarantine_root"):
            Path(context[name]).mkdir()  # Operator-prepared fresh, empty roots.
        chain = window / "window-chain.zsh"
        rendered = writer.render_qualification_chain("s1", self.template, self.sizing, self.pack, t0_epoch_s,
                                                     chain, arm_context=context)
        environment = {
            "MEASUREMENT_REPO": str(writer.REPO_ROOT), "PACK_ROOT": str(self.pack), "PACK_ID": self.pack.name,
            "PLAN_ID": self.plan_id, "FROZEN_PLAN": str(self.frozen_plan),
            "WINDOW_ID": self.tree["window_identity"]["window_id"],
            "EVIDENCE_ROOT_ID": self.tree["window_identity"]["evidence_root_id"],
            "BRACKET_SESSION_ID": context["bracket_session_id"], "PRE_ATTEMPT_ID": context["pre_attempt_id"],
            "POST_ATTEMPT_ID": context["post_attempt_id"], "RUNS_ROOT": context["claim_runs_root"],
            "BOUND_RUNS_ROOT": context["bound_runs_root"], "QUARANTINE_ROOT": context["quarantine_root"],
            "CUSTODY_ROOT": context["custody_root"], "WINDOW_CUSTODY_ROOT": context["custody_root"],
            "ARM_READINESS_CUSTODY_ROOT": str(custody), "CLAIM_BACKUP_DEST": context["claim_backup_destination"],
            "BOUND_BACKUP_DEST": context["bound_backup_destination"], "WAIVER_PATH": context["waiver_path"],
            "IDENTITY_EPOCH_JSON": str(arm_base / "identity_epoch.json"),
            "T1_BINDINGS_JSON": str(arm_base / "t1_bindings.json"),
            "CALIBRATION_LEDGER": str(arm_base / "calibration_observation_ledger.jsonl"),
            "LEDGER_HEAD_PIN": str(arm_base / "calibration_ledger_head.json"),
            "SETTLE_S": "180", "POWER_POLICY": "ac_high_power"}
        assert set(environment) == t0_author.WINDOW_ENV_KEYS
        (window / "window.env").write_text("".join(f"{key}={shlex.quote(value)}\n"
                                                   for key, value in sorted(environment.items())))
        roster = writer.pack_roster(self.pack, "s1")
        sized = writer.size_window("s1", self.sizing, roster=roster[0], auxiliary=roster[1],
                                   brackets=roster[2], nonsampling=roster[3])
        end = t0_epoch_s + sized["window_max_s"]
        binding = {"schema": night_gate.PACK_PLAN_SCHEMA, "schema_version": 3, "plan_id": self.plan_id,
            "receipt_class": "TRANSACTION_PACK", "t0_epoch_s": t0_epoch_s, "window_max_s": sized["window_max_s"],
            "authored_epoch_s": 0.0, "repo_head": self.head, "measurement_root": str(writer.REPO_ROOT),
            "measurement_head": self.head, "chain_path": str(chain), "chain_sha256_path": rendered["sidecar"]["path"],
            "custody_root": str(custody), "registration_path": None}
        prospective = night_gate.NightPlan.from_mapping({**binding, "pack_night": {
            "pack_id": self.pack.name, "pack_root": str(self.pack), "pack_sha256": self.digest, "attempt_ordinal": 1,
            "authorization_record": {"path": str(custody / "authorization_record.json"), "sha256": "0" * 64},
            "confirmation_record": {"path": str(custody / "step6_confirmation_record.json"), "sha256": "0" * 64}}})
        inputs = {"schema_version": writer.INPUT_SCHEMA, "head": self.head, "plan": binding,
            "kernel_frequency": frequency_probe(),
            "pack": {"root": str(self.pack), "sha256": self.digest, "attempt_ordinal": 1},
            "authorization": {"purpose": "G2B_SHAKEDOWN", "attempt_id": self.plan_id + "/1", "claim_eligible": False,
                "permitted_blocks": 1, "pack_sha256": self.digest, "permitted_chain_sha256": q.sha(chain),
                "authority": "D-171 §3; DESK DIAGNOSTIC ONLY"},
            "confirmation": self.confirmation(occurrence), "sizing": self.sizing,
            "deadlines": {"latest_chain_start_epoch_s": rendered["latest_chain_start_epoch_s"],
                "shutdown_epoch_s": end + driver.WINDOW_SHUTDOWN_GRACE_S,
                "courier_epoch_s": end + driver.WINDOW_SHUTDOWN_GRACE_S + driver.COURIER_DEADLINE_S,
                "deadman_epoch_s": driver.deadman_epoch(prospective)},
            "other_custody_roots": [], "arm_context": context, "prerequisites": {}}
        return SimpleNamespace(custody=custody, inputs=inputs, plan=custody / "plan.json", context=context)


class CommittedGammaJoinedReplayTests(unittest.TestCase):
    """Run preparation without semantic mocks, stopping at missing authority."""

    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="joined-", dir=SCRATCH)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.pack = writer.REPO_ROOT / PACK_RELATIVE
        self.head = subprocess.check_output(
            ["git", "-C", str(writer.REPO_ROOT), "rev-parse", "HEAD"], text=True).strip()
        # Real committed pack bytes, including all configs and sidecars; no
        # two-file pack stand-in and no replacement digest authenticator.
        self.digest = ar.committed_pack_tree_sha256(self.pack)
        self.roster, self.auxiliary, self.brackets, self.nonsampling = writer.pack_roster(self.pack, "s1")
        self.sizing = writer.read_object(writer.REPO_ROOT /
            "configs/campaigns/v5_qualification_25g83/sizing_allowances.json")
        self.sized = writer.size_window("s1", self.sizing, roster=self.roster,
            auxiliary=self.auxiliary, brackets=self.brackets, nonsampling=self.nonsampling)
        self.template = self.root / "reviewed-chain.zsh"
        self.template.write_text(writer.g2b_body(writer.REPO_ROOT))
        self.chain = self.root / "chain.zsh"
        self.t0 = 1000.0  # Authored desk input, not an observed clock assertion.
        self.rendered = writer.render_qualification_chain("s1", self.template, self.sizing,
            self.pack, self.t0, self.chain)
        tree, _ = ar._plan_tree(self.pack)
        self.frozen = tree["arm_attachments"]["arm_readiness"]["freeze_receipt"] is not None

    def test_complete_pack_bytes_roster_and_reviewed_chain_are_real(self):
        def tree_at(commit):
            return subprocess.check_output(["git", "-C", str(writer.REPO_ROOT),
                "ls-tree", "-r", commit, "--", PACK_RELATIVE]).decode().splitlines()
        if not self.frozen:
            # The 2026-10-09 corpus erratum (18 NEG-8 corpus members) changed one literal in
            # the generator and re-pinned plan_tree; every other committed source byte,
            # including all science configs and sidecars, is unchanged, and no file was added.
            erratum = {PACK_RELATIVE + "/plan_tree.json", PACK_RELATIVE + "/plan_tree.sha256",
                       PACK_RELATIVE + "/generate_configs.py"}
            source, head = tree_at(PACK_SOURCE_COMMIT), tree_at(self.head)
            self.assertEqual([line.split("\t")[1] for line in source], [line.split("\t")[1] for line in head])
            self.assertEqual([line for line in source if line.split("\t")[1] not in erratum],
                             [line for line in head if line.split("\t")[1] not in erratum])
        else:
            # U11 projection, evidence and freeze-0004 only add receipts and
            # re-pin plan_tree; every other committed source byte is unchanged.
            mutable = {PACK_RELATIVE + "/plan_tree.json", PACK_RELATIVE + "/plan_tree.sha256"}
            source = {line for line in tree_at(PACK_SOURCE_COMMIT) if line.split("\t")[1] not in mutable}
            self.assertLessEqual(source, set(tree_at(self.head)))
        self.assertEqual(len(ar._plan_tree(self.pack)[0]["science"]), 80)
        self.assertEqual([r["position"] for r in self.roster], ["A1", "B1", "B2", "A2"])
        self.assertEqual((len(self.auxiliary), len(self.brackets), len(self.nonsampling)), (5, 2, 1))
        self.assertIn(writer.g2b_body(writer.REPO_ROOT), self.chain.read_text())
        self.assertEqual(self.rendered["chain"], writer.locator(self.chain))
        self.assertEqual(self.rendered["window_max_s"], self.sized["window_max_s"])
        # Parse only: executing this chain would invoke physical tools.
        result = subprocess.run(["/bin/zsh", "-n", str(self.chain)], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def inputs(self, occurrence):
        from tests.test_arm_readiness_schemas import arm_context
        from tests.test_family_marker import confirmation
        custody = self.root / occurrence
        custody.mkdir()
        # Schema-only diagnostic input. These fixture table hashes are not
        # publication evidence, and this table must NEVER authorize a launch.
        # It permits reaching the real freeze authenticator; no table validator
        # or freeze/ARM semantic function is mocked to get past it.
        table = self.root / (occurrence + "-schema-only-confirmation.json")
        put(table, confirmation())
        table.with_name(table.name + ".sha256").write_bytes(ar.gnu_sidecar(q.sha(table), table.name))
        ar._authenticate_confirmation_table(table, q.sha(table))
        transcript = self.root / (occurrence + "-schema-only-transcript.txt")
        transcript.write_text("DESK SCHEMA INPUT ONLY " + q.sha(table) + "\n")
        confirm = self.root / (occurrence + "-confirmation-record.json")
        put(confirm, {"table_path": str(table), "table_sha256": q.sha(table),
            "transcript_sha256": q.sha(transcript),
            "confirmed_at": {"epoch_s": 0.0, "iso8601_utc": "1970-01-01T00:00:00.000000Z"}})
        context = arm_context(custody)
        context["custody_root"] = str(custody)
        plan_id = ar._pack_record(self.pack)["plan_id"]
        end = self.t0 + self.sized["window_max_s"]
        binding = {"schema": night_gate.PACK_PLAN_SCHEMA, "schema_version": 3,
            "plan_id": plan_id, "receipt_class": "TRANSACTION_PACK", "t0_epoch_s": self.t0,
            "window_max_s": self.sized["window_max_s"], "authored_epoch_s": 0.0,
            "repo_head": self.head, "measurement_root": str(writer.REPO_ROOT),
            "measurement_head": self.head, "chain_path": str(self.chain),
            "chain_sha256_path": self.rendered["sidecar"]["path"], "custody_root": str(custody),
            "registration_path": None}
        prospective = night_gate.NightPlan.from_mapping({**binding,
            "pack_night": {"pack_id": self.pack.name, "pack_root": str(self.pack),
                "pack_sha256": self.digest, "attempt_ordinal": 1,
                "authorization_record": {"path": str(custody / "authorization_record.json"), "sha256": "0" * 64},
                "confirmation_record": {"path": str(custody / "step6_confirmation_record.json"), "sha256": "0" * 64}}})
        archive_root = self.root / (occurrence + "-block-archive"); archive_root.mkdir()
        history = {"previous_attempt": {"none": True}, "block_archive_root": str(archive_root)} if occurrence == "s1" else {}
        return {**history, "schema_version": writer.INPUT_SCHEMA, "head": self.head, "plan": binding,
            "kernel_frequency": frequency_probe(),
            "pack": {"root": str(self.pack), "sha256": self.digest, "attempt_ordinal": 1},
            "authorization": {"purpose": "G2B_SHAKEDOWN", "attempt_id": plan_id + "/1",
                "claim_eligible": False, "permitted_blocks": 1, "pack_sha256": self.digest,
                "permitted_chain_sha256": q.sha(self.chain), "authority": "D-171 §3; DESK DIAGNOSTIC ONLY"},
            "confirmation": {"record": q.reference(confirm), "transcript": q.reference(transcript),
                "expected_confirmation_digest": q.sha(table)}, "sizing": self.sizing,
            "deadlines": {"latest_chain_start_epoch_s": self.rendered["latest_chain_start_epoch_s"],
                "shutdown_epoch_s": end + driver.WINDOW_SHUTDOWN_GRACE_S,
                "courier_epoch_s": end + driver.WINDOW_SHUTDOWN_GRACE_S + driver.COURIER_DEADLINE_S,
                "deadman_epoch_s": driver.deadman_epoch(prospective)},
            "other_custody_roots": [], "arm_context": context, "prerequisites": {}}

    def test_a1_a2_s1_real_writers_stop_at_unfrozen_pack_without_publishing(self):
        if self.frozen:
            self.skipTest("GAMMA is frozen: the joined chains run the real a1 writer to STAGED instead")
        before = self.digest
        for occurrence in ("a1", "a2", "s1"):
            with self.subTest(occurrence=occurrence):
                inputs = self.inputs(occurrence)
                output = Path(inputs["plan"]["custody_root"]) / "plan.json"
                with self.assertRaises(ar.ArmReadinessError) as caught:
                    writer.write_qualification(occurrence, inputs, output)
                self.assertEqual(caught.exception.reason_code, "readiness_freeze_receipt_unreadable")
                self.assertFalse(output.exists())
                self.assertEqual(list(output.parent.iterdir()), [])
        self.assertEqual(ar.committed_pack_tree_sha256(self.pack), before)

    def test_earlier_registry_refusal_remains_a_negative_control(self):
        registry = q.read(writer.REPO_ROOT / ar.ROW_REGISTRY_RELATIVE_PATH)
        registry["freeze_evidence_lifecycle"]["schema_version"] = "unregistered.fixture.schema"
        with self.assertRaises(ar.ArmReadinessError) as caught:
            ar.validate_registry(registry)
        self.assertEqual(caught.exception.reason_code, "readiness_row_registry_mismatch")

    def test_real_arm_issuer_also_stops_before_authorizing(self):
        from tests.test_arm_readiness_schemas import arm_context
        inputs = self.inputs("arm-diagnostic")
        confirmation = q.read(Path(inputs["confirmation"]["record"]["path"]))
        if not self.frozen:
            with self.assertRaises(ar.ArmReadinessError) as caught:
                ar.generate_arm_receipt(self.pack, arm_context(self.root),
                    inputs["plan"]["custody_root"], step6_confirmation_table=confirmation["table_path"],
                    expected_confirmation_digest=inputs["confirmation"]["expected_confirmation_digest"])
            self.assertEqual(caught.exception.reason_code, "readiness_freeze_receipt_unreadable")
            self.assertFalse(list(self.root.rglob("arm_readiness.receipts/arm-*.json")))
            return
        context_root = self.root / "arm-diagnostic-context"
        context_root.mkdir()
        result = ar.generate_arm_receipt(self.pack, arm_context(context_root),
            inputs["plan"]["custody_root"], step6_confirmation_table=confirmation["table_path"],
            expected_confirmation_digest=inputs["confirmation"]["expected_confirmation_digest"])
        if result["receipt_path"] is None:
            self.assertEqual(result["reason_codes"], ["readiness_r1_dependency_changed_set"])
            self.skipTest(changed_set_flag(result["detail"]))
        # Frozen: the real issuer writes a governed NO_GO receipt. Every
        # FREEZE_AND_ARM row authenticates from the frozen evidence; only
        # ARM-time rows refuse, and the family-publication gate still holds.
        self.assertEqual((result["status"], result["arm_disposition"]), ("REFUSE", "NO_GO"))
        rows = q.read(Path(result["receipt_path"]))["rows"]
        for row in rows:
            if row["evaluation_phase"] == "FREEZE_AND_ARM":
                self.assertIn(row["verdict"], {"PASS", "NOT_APPLICABLE"}, row["row_id"])
        refused = [row for row in rows if row["verdict"] == "REFUSE"]
        self.assertTrue(refused)
        self.assertEqual({row["evaluation_phase"] for row in refused}, {"ARM_ONLY"})
        self.assertIn("readiness_r1_family_publication", result["reason_codes"])
        self.assertNotIn("readiness_freeze_receipt_unreadable", result["reason_codes"])

    JOINED_VARIANTS = {
        "success": "qualification and structural verdicts PASS; G1, G3, G5, G8 and G9 PASS on native output",
        "observation_exception": "an observation producer raises: chain rc unchanged, qualification FAIL or "
                                 "REFUSED, structural verdict unchanged",
        "recover_no_science": "a launch tooling crash after chain.started and before the first science "
                              "sampler: recover_no_science",
        "agent_present": "an agent in the capture census: qualification FAIL as a genuine live-gate failure "
                         "(END STATE)",
        "null_restore": "a NULL s1 refused before chain.started, the NULL restore, then a fresh s1 whose "
                        "history chain and census pass",
        "admission_abort": "one admission abort, a fresh s1, the allowance spent; a second abort refuses as "
                           "the same refusal twice",
    }

    def joined_stop(self):
        lines, start = inspect.getsourcelines(ar._load_freeze_reference)
        line = start + next(i for i, value in enumerate(lines) if '"readiness_freeze_receipt_unreadable"' in value)
        self.skipTest(f"FLAG joulewise/arm_readiness.py:{line}: committed GAMMA lacks freeze authority; "
            "writer/ARM cannot continue. No nonphysical semantic shortcut is allowed.")

    def joined_chain(self, variant):
        """ONE desk occurrence chain: a1, a2, the G10 control, then s1.

        Each leg runs the real tool as installed. The chain stops, with a
        FLAG, at the first step that needs a physical seam outside
        PHYSICAL_SEAMS or an authority the desk cannot hold.
        """
        if not self.frozen:
            self.joined_stop()
        desk = JoinedDesk(self.root, self.pack)
        # a1: the real writer (ARM_ONLY_NO_LAUNCH) on the frozen pack.
        a1 = desk.stage("a1", time.time() + 3600)  # Authored T0 input, one hour ahead.
        try:
            staged = writer.write_qualification("a1", a1.inputs, a1.plan)
        except ar.EvidenceLifecycleError as error:
            if "changed relevant path" not in str(error):
                raise
            self.assertFalse(a1.plan.exists())
            self.skipTest(changed_set_flag(error))
        self.assertEqual(staged["status"], "STAGED")
        record = q.read(a1.plan)
        self.assertEqual((record["mode"], record["occurrence"]), ("ARM_ONLY_NO_LAUNCH", "a1"))
        tree, _ = ar._plan_tree(self.pack)
        freeze = tree["arm_attachments"]["arm_readiness"]["freeze_receipt"]
        self.assertEqual(record["freeze_receipt"], writer.locator(self.pack / freeze["path"]))
        # desk.under_lease_rehearsal: the real dry run (real reservation CLI and
        # ledger writer lifecycle against a synthetic ledger).
        dry = ar.generate_dry_run_receipt(self.pack, a1.custody, "a1", self.root / "a1-dry-run")
        self.assertEqual((dry["status"], dry["reason_codes"]), ("PASS", []))
        # a1 ARM-only exactly as the record's recipe invokes it.
        self.assertEqual(record["recipe"]["arm_argv"][-4:], [str(writer.REPO_ROOT / "scripts/check_v5_arm_abort.py"),
                                                            "arm", "--context", str(a1.plan)])
        seams = PhysicalSeams()
        stdout = SimpleNamespace(buffer=io.BytesIO())
        with seams.installed(), mock.patch.object(sys, "stdout", stdout):
            code = checker.main(record["recipe"]["arm_argv"][2:])
        if code == 0:
            self.fail("a1 ARM-only PASS reached: implement the a1 expiry, a2, G10 and s1 legs; do not keep this stop")
        self.assertEqual((code, ar.parse_json_bytes(stdout.buffer.getvalue())),
                         (2, {"status": "REFUSED", "reason_code": "arm_abort_control_invalid"}))
        # The native T-0 stage ran under the driver's stage cap. The listed seams
        # carried clock-reference (R0) and clock-disable (OFF) to real captures.
        self.assertEqual([seam for seam, _ in seams.calls], ["sntp collector"] * 3 + ["sudo/systemsetup"])
        inputs = a1.custody / self.pack.name / capture.INPUT_DIRECTORY
        for name in ("clock-reference.json", "clock-disable.json", "network_time_off.json", "launch-manifest.json"):
            self.assertTrue((inputs / name).is_file(), name)
        self.assertFalse((inputs / "quiet-mac-prep.json").exists())
        stage = q.read(a1.custody / "night/t0-capture.stdout.json")
        flag = seams.flags["quiet-mac-prep"]
        self.assertEqual((stage["status"], stage["detail"]), ("REFUSE", flag))
        # Nothing was launched, consumed or armed.
        context, plan, _ = checker.context_at(a1.plan)
        self.assertTrue(all(checker.absence(plan, context["arm_context"]).values()))
        self.assertFalse(list(self.root.rglob("arm_readiness.receipts/arm-*.json")))
        self.assertFalse((a1.custody / "night/arm-only.json").exists())
        self.skipTest(f"{flag} Joined variant '{variant}' ({self.JOINED_VARIANTS[variant]}) is not reached: "
                      "the a1 expiry, a2, G10, s1 driver, closeout and both harvests all depend on this ARM.")

    def test_joined_success_qualification_and_structural_pass(self):
        self.joined_chain("success")

    def test_joined_observation_exception_preserves_chain_rc_and_structural_verdict(self):
        self.joined_chain("observation_exception")

    def test_joined_launch_crash_recovers_no_science(self):
        self.joined_chain("recover_no_science")

    def test_joined_agent_capture_is_live_gate_fail_end_state(self):
        self.joined_chain("agent_present")

    def test_joined_null_s1_restore_then_fresh_s1_history_and_census(self):
        self.joined_chain("null_restore")

    def test_joined_admission_abort_then_fresh_s1_allowance_spent(self):
        self.joined_chain("admission_abort")


class StartedOccurrenceReplayTests(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="started-", dir=SCRATCH)
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.pack = writer.REPO_ROOT / PACK_RELATIVE
        # Component input: an already-started occurrence, not a writer/ARM
        # success fixture. Authenticate the COMPLETE actual committed pack.
        head = subprocess.check_output(["git", "-C", str(writer.REPO_ROOT), "rev-parse", "HEAD"], text=True).strip()
        digest = ar.committed_pack_tree_sha256(self.pack)
        self.night_custody = self.root / "night-custody"; self.night = self.night_custody / "night"
        self.night.mkdir(parents=True)
        self.custody = self.root / "g2b-custody"; self.runs = self.custody / "runs"; self.runs.mkdir(parents=True)
        self.bound = self.root / "bound"; self.bound.mkdir()
        chain = self.root / "chain.zsh"; chain.write_text("#!/bin/zsh\nexport V5_QUALIFICATION_OCCURRENCE=s1\nexit 0\n")
        sidecar = self.root / "chain.sha256"; sidecar.write_bytes(ar.gnu_sidecar(q.sha(chain), chain.name))
        table = self.root / "table.json"; put(table, {})
        self.archive = self.root / "block-archive"; self.archive.mkdir()
        auth = put(self.night_custody / "authorization_record.json", {"purpose": "G2B_SHAKEDOWN",
            "previous_attempt": {"none": True}, "block_archive_root": str(self.archive),
            "attempt_id": "s1-synthetic/1", "claim_eligible": False, "permitted_blocks": 1,
            "pack_sha256": digest, "permitted_chain_sha256": q.sha(chain), "authority": "D-171 §3"})
        confirmation = put(self.night_custody / "confirmation.json", {"table_path": str(table),
            "table_sha256": q.sha(table), "transcript_sha256": "b" * 64,
            "confirmed_at": {"epoch_s": 0., "iso8601_utc": "1970-01-01T00:00:00.000000Z"}})
        self.plan = night_gate.NightPlan.from_mapping({"schema": night_gate.PACK_PLAN_SCHEMA, "schema_version": 3,
            "plan_id": "s1-synthetic", "receipt_class": "TRANSACTION_PACK", "t0_epoch_s": 0.,
            "window_max_s": 3600, "authored_epoch_s": 0., "repo_head": head, "measurement_root": str(g2b.ROOT),
            "measurement_head": head, "chain_path": str(chain), "chain_sha256_path": str(sidecar),
            "custody_root": str(self.night_custody), "registration_path": None,
            "previous_attempt": {"none": True}, "block_archive_root": str(self.archive),
            "pack_night": {"pack_id": self.pack.name, "pack_root": str(self.pack), "pack_sha256": digest,
                "attempt_ordinal": 1, "authorization_record": auth, "confirmation_record": confirmation}})
        plan_path = write_night_plan(self.night_custody / "night_plan.json", self.plan, create_once=True)
        # Retained component input only: not proof of real courier delivery.
        put(self.night / "courier.sent", {"desk_fixture_delivery_ack": True})
        process = subprocess.Popen([sys.executable, "-B", "-c",
            "import sys; sys.stdin.read(); sys.exit(9)"], stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            # Real OS child and driver record writers. No PID/start-time or
            # process-group semantic mock; no science/privileged command.
            driver._write_launch_pending(process, self.night, self.plan)
            descriptor = driver._claim_chain_start(self.night)
            self.assertIsNotNone(descriptor)
            driver._complete_chain_start(descriptor, process, self.night)
            process.communicate(timeout=10)
            self.assertEqual(process.returncode, 9)
            driver._record_chain_exit(self.night, process.returncode)
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=10)
            if process.stdin is not None:
                process.stdin.close()
        self.inputs = {"schema": g2b.INPUT_SCHEMA, "occurrence": "s1", "plan": q.reference(plan_path),
            "custody_root": str(self.custody), "policy": put(self.root / "policy.json", {}),
            "acceptance": put(self.root / "acceptance.json", {}), "bound_runs_root": str(self.bound),
            "auxiliary_bundle_ids": [], "bound_bundle_ids": []}
        self.input_path = self.root / "inputs.json"
        self.args = SimpleNamespace(inputs=self.input_path, inputs_sha256=None, archive_root=self.archive / "attempts" / self.plan.plan_id,
            scratch_root=self.root, prepare_desk=False, previous_harvest=None)

    def harvest(self):
        if not self.input_path.exists():
            put(self.input_path, self.inputs)
        self.args.inputs_sha256 = q.sha(self.input_path)
        return g2b.harvest(self.args, now=lambda: 999999.)  # Mock seam: elapsed completion boundary.

    def test_started_crash_archives_and_recovers_without_success_only_records(self):
        before = q.tree_hash(self.night_custody)
        record = self.harvest()
        self.assertEqual(record["verdict"], "RECOVER")
        self.assertIn("started_chain_crashed", record["cause_codes"])
        self.assertIn("terminal_boundary_missing", record["cause_codes"])
        self.assertEqual(q.tree_hash(self.night_custody), before)
        self.assertTrue((self.args.archive_root / "withheld/sources/night-custody/night/chain.started").exists())

    def test_named_pre_science_crash_and_partial_science_have_distinct_dispositions(self):
        started = q.read(self.night / "chain.started")["monotonic_ns"]
        self.inputs["pre_science_tooling_failure"] = put(self.root / "failure.json", {
            "schema": "joulewise.v5_pre_science_tooling_failure.v1", "plan_id": self.plan.plan_id,
            "cause_code": "night_chain_launch_failed", "cause_class": "tooling", "monotonic_ns": started + 1,
            "seam": "launch"})
        record = self.harvest()
        self.assertEqual(record["recovery_classification"], "recover_no_science")
        self.assertFalse(record["consumes_s2"])
        self.assertFalse(record["s2_eligible"])
        self.assertFalse(record["end_state"])
        # Independent retained-input variant, not an R3 identical-byte replay.
        shutil.rmtree(self.args.archive_root)
        (self.runs / q.read(self.pack / "plan_tree.json")["science"][0]["run_id"]).mkdir()
        record = self.harvest()
        self.assertEqual(record["verdict"], "RECOVER")
        self.assertNotIn("recovery_classification", record)
        self.assertIn("started_chain_incomplete", record["cause_codes"])

    def test_external_event_source_is_retained_on_identical_byte_reharvest(self):
        for name in ("terminal_boundary", "go", "consumption", "battery_boundaries"):
            # Deliberately invalid success artifacts: this is a REFUSED replay
            # custody control, not fabricated positive producer evidence.
            self.inputs[name] = put(self.root / (name + ".json"), {})
        put(self.runs / "bracket-binding.json", {})
        (self.runs / "whole-window-verdict.json").write_text("{}\n")
        self.inputs["desk_producer_events"] = put(self.root / "desk-events.json", {"schema": g2b.ORDER_SCHEMA})
        first = self.harvest()
        self.assertEqual(first["verdict"], "REFUSED")
        self.args.previous_harvest = self.args.archive_root
        self.args.archive_root = self.args.previous_harvest / "reharvest-1"
        second = self.harvest()
        self.assertEqual(second["verdict"], "REFUSED")
        a, b = [q.read(root / "replay-locators.json") for root in (self.args.previous_harvest, self.args.archive_root)]
        self.assertEqual([(r["name"], r["original_path"], r["inventory"]) for r in a["sources"]],
                         [(r["name"], r["original_path"], r["inventory"]) for r in b["sources"]])
        self.assertIn("desk-producer-events", {r["name"] for r in b["sources"]})
        self.args.archive_root = self.args.previous_harvest / "reharvest-2"
        (self.root / "desk-events.json").write_text("changed")
        with self.assertRaisesRegex(q.HarvestRefusal, "digest_mismatch"):
            self.harvest()

    def test_observation_fault_fails_only_qualification_without_end_state_or_g2b_cause(self):
        from joulewise import battery_float
        from tests.test_battery_float import raw, UPDATE
        retained_rc = q.read(self.night / "chain.exited")["exit_code"]
        structural_before = self.harvest()
        structural_root = self.args.archive_root
        observations = {}
        for site in ("arm", "publication", "t0"):
            raw_path = self.root / (site + ".ioreg"); raw_path.write_bytes(raw())
            # Physical seams: ioreg battery read, wall and monotonic clocks.
            value, _ = battery_float.observe(phase=site, plan_id=self.plan.plan_id, wall_time_s=UPDATE + 1,
                monotonic_ns=lambda: 1, runner=lambda argv: subprocess.CompletedProcess(argv, 0, raw_path.read_bytes(), b""))
            observations[site] = {"record": put(self.root / (site + ".json"), value), "raw": q.reference(raw_path)}
        boundary = self.root / "boundaries.json"
        put(boundary, {"schema": "joulewise.v5_qualification_battery_boundaries.v1", "plan_id": self.plan.plan_id,
                       "observations": observations})
        driver._qualification_observe(self.night, "hid", lambda: (_ for _ in ()).throw(OSError("synthetic producer fault")))
        args = SimpleNamespace(plan=self.night_custody / "night_plan.json", archive_root=structural_root / "qualification",
            battery_evidence=boundary, battery_evidence_sha256=q.sha(boundary), replay_source=[], previous_harvest=None)
        # Mock seam: wall clock after the completion/harvest boundary.
        verdict = qualification.harvest(args, now=lambda: 999999.)
        self.assertEqual(verdict["verdict"], "FAIL")
        self.assertEqual(verdict["cause_codes"], ["qualification_observation_producer_fault"])
        self.assertFalse(verdict["end_state"])
        # Another independent snapshot includes the later observation fault.
        shutil.rmtree(structural_root)
        structural = self.harvest()
        self.assertEqual(q.read(self.night / "chain.exited")["exit_code"], retained_rc)
        for field in ("verdict", "cause_codes", "cause_classes"):
            self.assertEqual(structural[field], structural_before[field])
        self.assertNotIn("qualification_observation_producer_fault", structural["cause_codes"])
        self.assertIn("started_chain_crashed", structural["cause_codes"])



if __name__ == "__main__":
    unittest.main()
