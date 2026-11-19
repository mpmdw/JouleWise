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
    if kind in ("capture-predecessor-30b", "step-d"):
        files.append("load_journal.json")
    if kind == "step-d":
        files.extend((f"{BUNDLE}/outputs/align_window_reference.json",
                      f"{BUNDLE}/rich_telemetry.jsonl", f"{BUNDLE}/raw/powermetrics.plist",
                      "recovery/align_thermal.jsonl", "inventory/r1_classification.json",
                      "inventory/inventory_journal.jsonl"))
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
    def test_unadjudicated_pass_cannot_be_published(self):
        for has_ledger in (False, True):
            with self.subTest(ledger=has_ledger), TemporaryDirectory() as tmp, redirect_stdout(StringIO()) as stdout:
                attempt = Attempt(Path(tmp))
                table = {"verdict": "pass", "lines": dict.fromkeys(pc.RELEASE_LINES), "evidence_failures": {}}
                with self.assertRaisesRegex(ValueError, "verdict_binding"):
                    pc._emit_part_c(attempt.output, 0, table, ledger=attempt.ledger if has_ledger else None)
                copies = [json.loads((attempt.output / name).read_bytes()) for name in pc.RELEASE_COPIES]
                self.assertEqual(copies[0], copies[1])
                self.assertEqual(copies[0]["evaluation"]["verdict"], "other_failure")
                self.assertIn("Part C verdict: other_failure", stdout.getvalue())

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
        self.assertEqual(count, 188)

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
                self.assertIn("evidence_ledger.jsonl", out.getvalue())
                self.assertFalse((attempt.output.parent / "native-attempt" / evidence.LEDGER_NAME).exists())
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


SOAK_FILES = ("runtime_result.json", "sensors/align_thermal.jsonl", "load_journal.json", "battery.jsonl")


def write_terminal(segment, kind, receipt, config_sha):
    (segment / RECEIPT).write_bytes(json_bytes(receipt))
    captured = {path.relative_to(segment).as_posix(): hashed(path.read_bytes())
                for path in segment.rglob("*") if path.is_file() and path.name != MANIFEST}
    order = ("idle", *MEMBERS).index(kind)
    manifest = {"schema": "joulewise.align.r1_runtime_custody.v1", "kind": kind, "status": "complete",
                "config_sha256": config_sha, "started_epoch_s": order * 2000,
                "ended_epoch_s": order * 2000 + 1800, "files": captured}
    (segment / MANIFEST).write_bytes(json_bytes(manifest))
    # Frozen stdout uses the default separators, ASCII escapes and a single newline.
    return SimpleNamespace(returncode=0, stdout=json.dumps(receipt, sort_keys=True, allow_nan=False) + "\n",
                           stderr=f"synthetic private {MARKER}")


class SoakAttempt:
    def __init__(self, directory):
        self.root = directory / "synthetic-run"
        self.output = self.root / "part-c"
        self.directory = self.root / "soak"
        self.segment = self.directory / "idle_soak"
        self.reference = self.directory / "soak_reference.json"
        self.ledger = self.directory / "evidence_ledger.jsonl"
        self.row = self.directory / "soak_row.json"
        self.revision = "b2e01464d"
        self.config = directory / "runtime.json"
        self.config.write_bytes(b'{"synthetic":"config"}')
        self.config_sha = hashed(self.config.read_bytes())

    def receipt(self, **extra):
        return {"schema": "joulewise.align.r1_runtime_result.v1", "backend": "production", "kind": "idle",
                "config_sha256": self.config_sha, "synthetic_private": MARKER, **extra}

    def produce(self, receipt, **files):
        self.segment.mkdir(parents=True, exist_ok=True)
        for source in SOAK_FILES[1:]:
            path = self.segment / source
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(files.get(source, json_bytes({"synthetic_private": MARKER})))
        return write_terminal(self.segment, "idle", receipt, self.config_sha)

    def close(self, *, process=None, outer_receipt=None, stdout=None):
        self.directory.mkdir(parents=True, exist_ok=True)
        writer = evidence.EvidenceLedger(self.directory, self.revision, self.config, mode="soak")
        receipt = self.receipt()
        process = self.produce(receipt) if process is None else process
        if stdout is not None:
            process.stdout = stdout
        writer.member_return("idle", self.segment, ["runtime", "--r1-kind", "idle"], process=process)
        path = str(self.segment)
        self.row.write_bytes(json_bytes({"name": "idle_soak", "attempt": 0, "output_dir": path,
                                        "result": receipt if outer_receipt is None else outer_receipt}))
        self.reference.write_bytes(json_bytes({"source_segment": "idle_soak", "source_output": path, "attempt": 0}))
        writer.finish_soak("accepted")
        return hashed(self.ledger.read_bytes())

    def binding(self, handoff, *, reference=None, revision=None, config=None, output=None):
        return evidence.BoundSoak(output or self.output, reference or self.reference, handoff,
                                  revision or self.revision, config or self.config)

    def reseal(self, change):
        rows = [json.loads(line) for line in self.ledger.read_bytes().splitlines()]
        change(rows)
        previous = None
        with self.ledger.open("wb") as sink:
            for row in rows:
                raw = json_bytes({**row, "previous_sha256": previous})
                sink.write(raw)
                previous = hashed(raw)
        return hashed(self.ledger.read_bytes())


class SoakLedgerTests(unittest.TestCase):
    def test_post_child_soak_files_and_ledger_rows_cannot_be_edited(self):
        with TemporaryDirectory() as tmp:
            attempt = SoakAttempt(Path(tmp))
            handoff = attempt.close()
            attempt.binding(handoff)
            paths = [attempt.row, attempt.reference, attempt.ledger, attempt.segment / MANIFEST,
                     *[attempt.segment / name for name in SOAK_FILES]]
            for path in paths:
                with self.subTest(source=path.name):
                    good = path.read_bytes()
                    path.write_bytes(b" " + good[1:])
                    with self.assertRaises(evidence.EvidenceFailure) as caught:
                        attempt.binding(handoff)
                    self.assertEqual((caught.exception.reason, caught.exception.role), ("source_integrity", "idle"))
                    path.write_bytes(good)
            rows = attempt.ledger.read_bytes().splitlines(keepends=True)
            for index in range(3):
                reordered = rows.copy()
                peer = (index + 1) % 3
                reordered[peer], reordered[index] = reordered[index], reordered[peer]
                for operation, raw in {
                    "drop": b"".join(rows[:index] + rows[index + 1:]),
                    "reorder": b"".join(reordered),
                    "edit": b"".join([*rows[:index], b" " + rows[index][1:], *rows[index + 1:]]),
                }.items():
                    with self.subTest(index=index, operation=operation):
                        attempt.ledger.write_bytes(raw)
                        with self.assertRaisesRegex(evidence.EvidenceFailure, "source_integrity"):
                            attempt.binding(handoff)
                        if operation != "edit" or index != 2:
                            with self.assertRaises(evidence.EvidenceFailure):
                                attempt.binding(hashed(raw))
            dropped = b"".join(rows[:2])
            attempt.ledger.write_bytes(dropped)
            with self.assertRaisesRegex(evidence.EvidenceFailure, "evidence_unverifiable"):
                attempt.binding(hashed(dropped))

    def test_same_attempt_configuration_revision_and_reference_are_required(self):
        for version in ("run", "runtime_config", "producer_revision", "reference"):
            with self.subTest(version=version), TemporaryDirectory() as tmp:
                attempt = SoakAttempt(Path(tmp))
                handoff = attempt.close()

                def change(rows):
                    if version == "run":
                        for row in rows[:2]:
                            row["attempt"]["run"] = "another-attempt"
                    elif version == "runtime_config":
                        rows[0]["runtime_config"]["sha256"] = "a" * 64
                    else:
                        rows[0]["producer_revision"] = "another-revision"

                kwargs = {}
                if version == "reference":
                    alternate = attempt.directory / "other.json"
                    alternate.write_bytes(attempt.reference.read_bytes())
                    kwargs["reference"] = alternate
                else:
                    handoff = attempt.reseal(change)
                with self.assertRaises(evidence.EvidenceFailure) as caught:
                    attempt.binding(handoff, **kwargs)
                self.assertEqual((caught.exception.reason, caught.exception.role), ("fresh_soak", "idle"))

    def test_outer_receipt_and_native_stdout_line_are_reconciled_independently(self):
        for peer in ("runtime_result.json", "stdout"):
            with self.subTest(peer=peer), TemporaryDirectory() as tmp:
                attempt = SoakAttempt(Path(tmp))
                changed = attempt.receipt(synthetic_private=MARKER + 1)
                if peer == "stdout":
                    handoff = attempt.close(stdout=json.dumps(changed, sort_keys=True) + "\n")
                else:
                    handoff = attempt.close(outer_receipt=changed)
                with self.assertRaises(evidence.EvidenceFailure) as caught:
                    attempt.binding(handoff)
                self.assertEqual((caught.exception.reason, caught.exception.peer), ("receipt_pair", peer))

    def test_archive_idle_binding_and_native_missing_handoff(self):
        with TemporaryDirectory() as tmp:
            attempt = SoakAttempt(Path(tmp))
            handoff = attempt.close()
            attempt.ledger.unlink()
            self.assertEqual(pc.archived_custody_member(attempt.output, attempt.config, "idle"),
                             {"binding": "archived_custody"})
            self.assertFalse(attempt.ledger.exists())
            with self.assertRaisesRegex(evidence.EvidenceFailure, "evidence_unverifiable"):
                attempt.binding(handoff)
            with self.assertRaisesRegex(evidence.EvidenceFailure, "evidence_unverifiable"):
                attempt.binding(None)


class PublicationTests(unittest.TestCase):
    def test_successful_exit_is_tied_to_the_chain_both_copies_and_stdout(self):
        with TemporaryDirectory() as tmp:
            attempt = SoakAttempt(Path(tmp))
            soak_sha = attempt.close()
            soak = attempt.binding(soak_sha)
            reference_sha = hashed(attempt.reference.read_bytes())
            attempt.output.mkdir()
            writer = evidence.EvidenceLedger(attempt.output, attempt.revision, attempt.config,
                                             attempt.reference, soak=soak)
            for kind, name in MEMBERS.items():
                segment = attempt.output / name
                segment.mkdir()
                process = write_terminal(segment, kind, {"kind": kind}, attempt.config_sha)
                writer.member_return(kind, segment, ["runtime"], process=process)
            table = {"part": "C", "slots_entered": False,
                     "evaluation": {"schema": "joulewise.align.r1_part_c.v1", "verdict": "pass", "pass": True,
                                    "evidence_failures": {}, "slots_entered": False}}
            files = [attempt.output / name for name in ("smoke_part_c.json", "smoke.json")]
            published = json_bytes(table)
            for path in files:
                path.write_bytes(published)
            writer.finish("pass", {path.name: hashed(published) for path in files})
            stdout = attempt.root / "part-c.stdout.log"
            stdout.write_text("Part C verdict: pass (pass: True)\n")
            evidence.verify_part_c_publication(attempt.root, soak_sha, reference_sha)
            for path in [*files, writer.path, stdout, attempt.ledger, attempt.reference]:
                with self.subTest(source=path.name):
                    original = path.read_bytes()
                    path.write_bytes(b"{")
                    with self.assertRaisesRegex(evidence.EvidenceFailure, "verdict_binding"):
                        evidence.verify_part_c_publication(attempt.root, soak_sha, reference_sha)
                    path.write_bytes(original)
