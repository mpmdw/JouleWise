"""Synthetic RL-183c transport and binding tests. No native inputs."""
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import hashlib
from io import StringIO
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import patch

import scripts
from scripts import align_r1_part_c as pc
from scripts import align_r1_part_c_evidence as evidence


MEMBERS = {
    "capture-predecessor-30b": "capture_predecessor_30b",
    "step-d": "step_D_prefill_10k_decode_4096",
    "d-bank-benign-s1": "D_bank_benign_s1_gated_held",
    "x-g": "X_G_contrast",
}
BUNDLE = "runs/synthetic-run"
RECEIPT = "runtime_result.json"
MANIFEST = "runtime_custody.json"
MARKER = 918273645672


def hashed(raw):
    return hashlib.sha256(raw).hexdigest()


def json_bytes(obj):
    return (json.dumps(obj, sort_keys=True) + "\n").encode("ascii")


def required_files(kind):
    files = [RECEIPT, *[f"{BUNDLE}/{name}" for name in (
        "config.json", "metadata.json", "summary_metrics.json", "events.jsonl", "outputs/align_episode.json",
        "outputs/align_turns.jsonl", "power_trace.csv",
    )]]
    if kind != "capture-predecessor-30b":
        files.append(f"{BUNDLE}/outputs/align_thermal.jsonl")
    if kind == "step-d":
        files.extend((f"{BUNDLE}/outputs/align_window_reference.json",
                      "recovery/align_thermal.jsonl", "inventory/r1_classification.json"))
    return files


class Attempt:
    def __init__(self, base):
        root = base / "synthetic-attempt"
        self.output = root / "part-c"
        self.output.mkdir(parents=True)
        self.config, self.soak = root / "synthetic-config.json", root / "synthetic-reference.json"
        self.config.write_bytes(b'{"backend":"production"}')
        self.soak.write_bytes(b'{}')
        self.revision = "b2e01464d"
        self.ledger = evidence.EvidenceLedger(self.output, self.revision, self.config, self.soak)

    def producer(self, kind, *, entry_edit=None, saved=None, stdout=None):
        segment = self.output / MEMBERS[kind]
        receipt = {"schema": "joulewise.align.r1_runtime_result.v1", "backend": "production",
                   "kind": kind, "config_sha256": hashed(self.config.read_bytes()), "bundle": BUNDLE,
                   "e_D_j_per_token": MARKER, "energy_j": MARKER, "battery_drain_pct_per_h": MARKER}
        files = {}
        for name in required_files(kind):
            path = segment / name
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = (saved if saved is not None else json_bytes(receipt)) if name == RECEIPT else json_bytes(
                {"synthetic_protected": MARKER})
            path.write_bytes(raw)
            files[name] = hashed(raw)
        if entry_edit is not None:
            entry_edit(files)
        index = list(MEMBERS).index(kind)
        manifest = {"schema": "joulewise.align.r1_runtime_custody.v1", "kind": kind, "status": "complete",
                    "config_sha256": hashed(self.config.read_bytes()), "started_epoch_s": index * 3 + 1,
                    "ended_epoch_s": index * 3 + 2, "files": files}
        (segment / MANIFEST).write_bytes(json_bytes(manifest))
        process = SimpleNamespace(returncode=0, stdout=json_bytes(receipt).decode() if stdout is None else stdout,
                                  stderr=f"synthetic diagnostic {MARKER}")
        return segment, process

    def member(self, kind, **kwargs):
        segment, process = self.producer(kind, **kwargs)
        self.ledger.member_return(kind, segment, ["runtime", kind], process=process)
        return segment, process

    def through(self, kind, **kwargs):
        for name in MEMBERS:
            subject = self.member(name, **(kwargs if name == kind else {}))
            if name == kind:
                return subject
        raise AssertionError(kind)

    def bind(self, kind):
        member = self.ledger.member(kind)
        receipt = json.loads(member.read(RECEIPT, RECEIPT))
        pc._bound_member_files(member, receipt)
        member.verify_reads()
        return member


@contextmanager
def rehearsal_double(attempt, transport):
    module = ModuleType("scripts.align_r1_rehearsal")
    module._CHILD_HOST_LOCK = None
    module.executed_commit = lambda _root: attempt.revision
    module.runtime_config_path = lambda _argv: attempt.config
    module._run = transport
    module.contract = SimpleNamespace(NEEDS_SOAK_REFERENCE=set(MEMBERS), missing_fields=lambda *a, **k: [])
    with patch.dict(sys.modules, {module.__name__: module}), \
            patch.object(scripts, "align_r1_rehearsal", module, create=True):
        yield module


class LedgerTests(unittest.TestCase):
    def test_ledger_starts_records_each_invocation_and_binds_final_copies(self):
        with TemporaryDirectory() as tmp:
            attempt = Attempt(Path(tmp))

            def transport(argv):
                kind = argv[argv.index("--r1-kind") + 1]
                return attempt.producer(kind)[1]

            with rehearsal_double(attempt, transport):
                for kind, name in MEMBERS.items():
                    pc.judged_invoke(["runtime"], kind, attempt.output / name,
                                     soak_reference=attempt.soak, ledger=attempt.ledger)
                    attempt.bind(kind)
            copies = {}
            for name in ("smoke_part_c.json", "smoke.json"):
                raw = b'{"synthetic":true}\n'
                (attempt.output / name).write_bytes(raw)
                copies[name] = hashed(raw)
            attempt.ledger.finish("other_failure", copies)
            attempt.ledger.verify_chain()
            rows = attempt.ledger.path.read_bytes().splitlines(keepends=True)
            parsed = [json.loads(row) for row in rows]
            self.assertEqual(len(rows), 6)
            self.assertEqual(set(parsed[0]), {"attempt", "mode", "producer_revision", "runtime_config",
                                               "soak_reference", "previous_sha256"})
            self.assertEqual(parsed[0]["attempt"]["run"], "synthetic-attempt")
            self.assertIsNone(parsed[0]["previous_sha256"])
            for index, kind in enumerate(MEMBERS, 1):
                self.assertEqual(parsed[index]["kind"], kind)
                self.assertEqual(parsed[index]["exit_status"], 0)
                self.assertIs(parsed[index]["spawned"], True)
                argv = ["runtime", "--r1-kind", kind, "--output", str(attempt.output / MEMBERS[kind]),
                        "--soak-reference", str(attempt.soak)]
                self.assertEqual(parsed[index]["argv_sha256"], hashed(evidence.canonical(argv)))
                self.assertEqual(parsed[index]["attempt"], parsed[0]["attempt"])
                self.assertEqual(parsed[index]["manifest"]["sha256"],
                                 hashed((attempt.output / MEMBERS[kind] / MANIFEST).read_bytes()))
            self.assertEqual(parsed[-1]["emitted_sha256"], copies)
            for index in range(1, 6):
                self.assertEqual(parsed[index]["previous_sha256"], hashed(rows[index - 1]))
            for index, row in enumerate(rows):
                four_edits = {
                    "delete": rows[:index] + rows[index + 1:],
                    "truncate": rows[:index] + [b'{'] + rows[index + 1:],
                    "duplicate": rows[:index] + [row] + rows[index:],
                    "reorder": rows[1:index + 1] + rows[:1] + rows[index + 1:] if index
                    else [rows[1], row, *rows[2:]],
                }
                for operation, mutated in four_edits.items():
                    with self.subTest(row=index, operation=operation):
                        attempt.ledger.path.write_bytes(b"".join(mutated))
                        with self.assertRaises(evidence.EvidenceFailure) as caught:
                            attempt.ledger.verify_chain()
                        self.assertEqual(caught.exception.reason, "source_integrity")
                        self.assertEqual(caught.exception.source, "evidence_ledger.jsonl")

    def test_post_return_file_mutation_matrix(self):
        # Manifest is the return witness, so rehashing it after a mutation
        # cannot make that mutation authoritative.
        operations = {
            "delete": lambda path: path.unlink(),
            "truncate": lambda path: path.write_bytes(b"{"),
            "one_byte": lambda path: path.write_bytes(b" " + path.read_bytes()[1:]),
            "substitute": lambda path: path.write_bytes(b'{"attempt":"other","kind":"idle"}\n'),
        }
        count = 0
        for kind in MEMBERS:
            for name in [MANIFEST, *required_files(kind)]:
                for operation, mutate in operations.items():
                    with self.subTest(kind=kind, source=name, operation=operation), TemporaryDirectory() as tmp:
                        attempt = Attempt(Path(tmp))
                        segment, _ = attempt.through(kind)
                        mutate(segment / name)
                        with self.assertRaises(evidence.EvidenceFailure) as caught:
                            attempt.bind(kind)
                        self.assertEqual(caught.exception.reason, "source_integrity")
                        self.assertEqual(caught.exception.role, kind)
                        if name in (MANIFEST, RECEIPT):
                            self.assertEqual(caught.exception.source, name)
                        count += 1
        self.assertEqual(count, 168)

    def test_mutation_after_last_read_fails_at_final_recheck(self):
        for kind in MEMBERS:
            with self.subTest(kind=kind), TemporaryDirectory() as tmp:
                attempt = Attempt(Path(tmp))
                segment, _ = attempt.through(kind)
                bound = attempt.bind(kind)
                for name in [MANIFEST, *required_files(kind)]:
                    with self.subTest(source=name):
                        path = segment / name
                        raw = path.read_bytes()
                        path.write_bytes(b" " + raw[1:])
                        with self.assertRaisesRegex(evidence.EvidenceFailure, "source_integrity"):
                            bound.verify_reads()
                        path.write_bytes(raw)

    def test_unbound_file_entries_fail_even_when_the_file_exists(self):
        for kind in MEMBERS:
            for name in required_files(kind):
                for value in (None, "unhashed", "unreadable", "unhashed: watchdog deadline"):
                    with self.subTest(kind=kind, source=name, entry=value), TemporaryDirectory() as tmp:
                        attempt = Attempt(Path(tmp))

                        def edit(files):
                            if value is None:
                                del files[name]
                            else:
                                files[name] = value

                        attempt.through(kind, entry_edit=edit)
                        with self.assertRaises(evidence.EvidenceFailure) as caught:
                            attempt.bind(kind)
                        self.assertEqual(caught.exception.reason, "evidence_unverifiable")
                        self.assertEqual(caught.exception.role, kind)

    def test_native_without_member_return_fails_and_archive_uses_its_named_binding(self):
        with TemporaryDirectory() as tmp:
            attempt = Attempt(Path(tmp))
            attempt.producer("capture-predecessor-30b")
            attempt.ledger.path.unlink()
            with self.assertRaisesRegex(evidence.EvidenceFailure, "evidence_unverifiable"):
                attempt.ledger.member("capture-predecessor-30b")
            record = pc.archived_custody_member(attempt.output, attempt.config, "capture-predecessor-30b")
            self.assertEqual(record, {"binding": "archived_custody"})
            self.assertFalse(attempt.ledger.path.exists())

    def test_genuinely_unrun_contrast_and_ambiguous_oserror(self):
        with TemporaryDirectory() as tmp:
            attempt = Attempt(Path(tmp))
            attempt.through("d-bank-benign-s1")
            segment = attempt.output / MEMBERS["x-g"]
            result = SimpleNamespace(returncode=2, stdout="", stderr=f"reason {MARKER}")
            with rehearsal_double(attempt, lambda _argv: result):
                with self.assertRaises(pc.RuntimeAdmissionRefusal):
                    pc.judged_invoke(["runtime"], "x-g", segment, soak_reference=attempt.soak, ledger=attempt.ledger)
            attempt.ledger.refusal("x-g")
            segment.mkdir()
            (segment / RECEIPT).write_bytes(b"{")
            with self.assertRaisesRegex(evidence.EvidenceFailure, "x_g_launch_conflict"):
                attempt.ledger.refusal("x-g")
        with TemporaryDirectory() as tmp:
            attempt = Attempt(Path(tmp))
            attempt.through("d-bank-benign-s1")
            segment = attempt.output / MEMBERS["x-g"]
            with rehearsal_double(attempt, lambda _argv: None) as transport:
                with patch.object(transport, "_run", side_effect=OSError(f"synthetic marker {MARKER}")):
                    with self.assertRaisesRegex(pc.RuntimeEvidenceError, "process_exit"):
                        pc.judged_invoke(["runtime"], "x-g", segment, soak_reference=attempt.soak, ledger=attempt.ledger)
            with self.assertRaisesRegex(evidence.EvidenceFailure, "x_g_unrun_unproven"):
                attempt.ledger.refusal("x-g")
            text = attempt.ledger.path.read_text()
            self.assertIn('"exception":"OSError"', text)
            self.assertNotIn(str(MARKER), text)

    def test_structural_release_hashes_both_copies_and_drops_values(self):
        with TemporaryDirectory() as tmp:
            attempt = Attempt(Path(tmp))
            attempt.through("x-g")
            marked_table = {
                "verdict": "other_failure",
                "lines": {name: {"pass": False, "private": MARKER} for name in pc.RELEASE_LINES},
                "evidence_failures": {"x_g_receipt": f"error {MARKER}"},
                "log": [str(MARKER)], "printed_not_judged": {"private": MARKER},
            }
            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr), self.assertRaisesRegex(ValueError, "other_failure"):
                pc._emit_part_c(attempt.output, 0, marked_table, ledger=attempt.ledger)
            files = [attempt.output / name for name in ("smoke_part_c.json", "smoke.json", evidence.LEDGER_NAME)]
            for text in [stdout.getvalue(), stderr.getvalue(), *[file.read_text() for file in files]]:
                self.assertNotIn(str(MARKER), text)
            for line in stdout.getvalue().splitlines():
                if line.startswith("{"):
                    self.assertEqual(set(json.loads(line)), {"verdict", "reason", "role", "file_or_stream",
                                                             "row_or_index", "field", "peer"})
            self.assertEqual(files[0].read_bytes(), files[1].read_bytes())
            self.assertIs(json.loads(files[0].read_bytes())["evaluation"]["pass"], False)
            final = json.loads(files[2].read_bytes().splitlines()[-1])
            self.assertEqual(final["verdict"], "other_failure")
            self.assertEqual(final["emitted_sha256"], {file.name: hashed(file.read_bytes()) for file in files[:2]})

    def test_native_refuses_unwitnessed_outer_evidence_before_launch(self):
        with TemporaryDirectory() as tmp:
            attempt = Attempt(Path(tmp))
            with rehearsal_double(attempt, lambda _argv: self.fail("must not launch member")):
                out, err = StringIO(), StringIO()
                with redirect_stdout(out), redirect_stderr(err), self.assertRaisesRegex(ValueError, "other_failure"):
                    pc.run_bound_part_c(attempt.output.parent / "native-attempt", [], soak_reference=attempt.soak)
                self.assertIn("evidence_unverifiable", out.getvalue())
                self.assertIn("soak/soak_row.json", out.getvalue())
                self.assertIn("soak/idle_soak/runtime_custody.json", out.getvalue())
                self.assertEqual(err.getvalue(), "")


class StdoutTests(unittest.TestCase):
    def test_shape_and_strict_object(self):
        kind = "step-d"
        self.assertEqual(evidence.stdout_payload('{"value":1}\n', kind), {"value": 1})
        self.assertIsNone(evidence.stdout_payload("", kind))
        for text in ('{"value":1}', '{"value":1}\n\n', '{}\n{}\n', '{\r}\n', '\ufeff{}\n',
                     '{"value":"é"}\n', '{"value":false,"value":true}\n', '{"n":1e9999}\n', '{\n', '[]\n'):
            with self.subTest(text=text), self.assertRaises(evidence.EvidenceFailure) as caught:
                evidence.stdout_payload(text, kind)
            self.assertEqual(caught.exception.reason, "stdout_receipt")
            self.assertEqual(caught.exception.field, "invalid")

    def test_frozen_run_observes_only_one_trailing_line_ending(self):
        try:
            from scripts import align_r1_rehearsal as r1
        except ImportError:
            self.skipTest("R1 driver is on the W1 software branch")
        cases = [(raw, {"value": 1}) for raw in (b'{"value":1}\n', b'{"value":1}\r\n', b'{"value":1}\r')]
        cases.extend((raw, "invalid") for raw in (b'{"value":\r1}\n', b'{}\n{}\n', b'{}',
                                                   '{"v":"é"}\n'.encode(), b'\xef\xbb\xbf{}\n'))
        cases.append((b"", None))
        for raw, expected in cases:
            with self.subTest(raw=raw), patch.object(r1, "_terminate", side_effect=AssertionError("no signals")):
                argv = [sys.executable, "-c", f"import sys; sys.stdout.buffer.write({raw!r})"]
                process = r1._run(argv)
                self.assertEqual(process.returncode, 0)
                if expected == "invalid":
                    with self.assertRaises(evidence.EvidenceFailure) as caught:
                        evidence.stdout_payload(process.stdout, "step-d")
                    self.assertEqual((caught.exception.reason, caught.exception.field), ("stdout_receipt", "invalid"))
                else:
                    self.assertEqual(evidence.stdout_payload(process.stdout, "step-d"), expected)
