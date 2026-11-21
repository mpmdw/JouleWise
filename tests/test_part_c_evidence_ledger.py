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
FIELD = evidence.DESCRIPTOR_FIELD


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
    def __init__(self, base, config=b'{"backend":"production"}'):
        root = base / "synthetic-attempt"
        self.output = root / "part-c"
        self.output.mkdir(parents=True)
        self.config, self.soak = root / "synthetic-config.json", root / "synthetic-reference.json"
        self.config.write_bytes(config)
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
                writer.member_return(kind, segment, ["runtime"], process=process, model_descriptor="a" * 64)
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


# ---- RL-189 section 1: the descriptor witness and checks D1 to D6 ---------------------------------

@contextmanager
def runtime_double():
    """Stand-ins for the pinned producer calls the RL-189 checks make. No R1 runtime is on main.

    ``load_config`` and ``read_template`` keep the frozen contracts (a parsed
    config with its sha256; a template with its parsed prompt). The sampler and
    gate helpers accept only this module's clean synthetic turn.
    """
    runtime = ModuleType("joulewise.align.apple.r1_runtime")

    def load_config(path):
        raw = Path(path).read_bytes()
        return json.loads(raw), hashed(raw)

    def read_template(path):
        config = json.loads(Path(path).read_text())
        return config, json.loads(config["workload_profile"]["prompt_text"])

    runtime.load_config, runtime.read_template = load_config, read_template
    sampler = ModuleType("joulewise.align.apple.sampler")
    sampler.seconds_ns = lambda seconds: round(seconds * 10**9)
    sampler.monotonic_ns = lambda stamp: round(
        (stamp.monotonic_before_s + (stamp.monotonic_after_s - stamp.monotonic_before_s) / 2) * 10**9)
    sampler.stamp_mapping = lambda stamps, *, episode_domain, evidence=None: (
        SimpleNamespace(offset_ns=0, episode_domain=episode_domain), [])
    gates = ModuleType("joulewise.align.apple.thermal_gates")
    gates.split_decode_events = lambda events, holds: list(events)
    apple = ModuleType("joulewise.align.apple")
    apple.r1_runtime, apple.sampler, apple.thermal_gates = runtime, sampler, gates
    align = ModuleType("joulewise.align")
    align.apple = apple
    with patch.dict(sys.modules, {module.__name__: module for module in (align, apple, runtime, sampler, gates)}):
        yield runtime


class MirrorAttempt(Attempt):
    """An attempt whose issued config names one synthetic mirror through its four templates."""

    def __init__(self, base, limit=40960):
        # The marker in the path and in the limit shows that neither leaves the process.
        self.mirror = base / f"mirror-{MARKER}"
        self.mirror.mkdir()
        self.descriptor = self.mirror / "config.json"
        self.descriptor.write_bytes(json_bytes({"max_position_embeddings": limit}))
        self.templates = {}
        for key in pc.TEMPLATE_KEYS.values():
            path = base / f"template-{key}.json"
            path.write_bytes(json_bytes({"model": {"source": str(self.mirror)},
                                         "workload_profile": {"prompt_text": "{}"}}))
            self.templates[key] = path
        super().__init__(base, json_bytes({"backend": "production", "templates": {
            key: str(path) for key, path in self.templates.items()}}))

    @property
    def configured(self):
        return json.loads(self.config.read_bytes())

    def launch(self, kinds=tuple(MEMBERS), **kwargs):
        seen = []

        def transport(argv):
            seen.append(list(argv))
            return self.producer(argv[argv.index("--r1-kind") + 1])[1]

        with rehearsal_double(self, transport):
            for kind in kinds:
                pc.judged_invoke(["runtime"], kind, self.output / MEMBERS[kind],
                                 soak_reference=self.soak, ledger=self.ledger, **kwargs)
        return seen

    def rows(self):
        return [json.loads(line) for line in self.ledger.path.read_bytes().splitlines()]


FIRST = "capture-predecessor-30b"


class DescriptorWitnessTests(unittest.TestCase):
    """RL-189 1.2: the judged invoker binds <model.source>/config.json in each launched member's row."""

    def test_each_launched_member_row_binds_the_issued_mirror_and_the_argv_is_unchanged(self):
        with TemporaryDirectory() as tmp, runtime_double():
            attempt = MirrorAttempt(Path(tmp))
            seen = attempt.launch()
            rows = attempt.rows()
            expected = hashed(attempt.descriptor.read_bytes())
            self.assertEqual([row.get(FIELD) for row in rows], [None, *[expected] * 4])
            for kind, argv, row in zip(MEMBERS, seen, rows[1:]):
                frozen = ["runtime", "--r1-kind", kind, "--output", str(attempt.output / MEMBERS[kind]),
                          "--soak-reference", str(attempt.soak)]
                self.assertEqual(argv, frozen)
                self.assertEqual(row["argv_sha256"], hashed(evidence.canonical(frozen)))
                # One field joins the RL-183c row and nothing else does.
                self.assertEqual(set(row), {"attempt", "kind", "argv_sha256", "spawned", "exit_status",
                                            "stdout_sha256", "stderr_sha256", "segment", "manifest",
                                            "previous_sha256", FIELD})
            attempt.ledger.verify_chain()
            self.assertNotIn(str(MARKER), attempt.ledger.path.read_text())

    def test_a_raising_transport_still_binds_and_a_member_never_launched_does_not(self):
        with TemporaryDirectory() as tmp, runtime_double():
            attempt = MirrorAttempt(Path(tmp))
            segment = attempt.output / MEMBERS[FIRST]
            with rehearsal_double(attempt, lambda _argv: None) as transport:
                with patch.object(transport, "_run", side_effect=OSError(f"synthetic marker {MARKER}")):
                    with self.assertRaisesRegex(pc.RuntimeEvidenceError, "process_exit"):
                        pc.judged_invoke(["runtime"], FIRST, segment, soak_reference=attempt.soak,
                                         ledger=attempt.ledger)
            row = attempt.rows()[-1]
            self.assertEqual((row["exception"], row[FIELD]), ("OSError", hashed(attempt.descriptor.read_bytes())))
        with TemporaryDirectory() as tmp, runtime_double():
            attempt = MirrorAttempt(Path(tmp))
            with rehearsal_double(attempt, lambda _argv: self.fail("must not launch")):
                with self.assertRaises(pc.RuntimeAdmissionRefusal):
                    pc.judged_invoke(["runtime"], FIRST, attempt.output / MEMBERS[FIRST], ledger=attempt.ledger)
            row = attempt.rows()[-1]
            self.assertIs(row["spawned"], False)
            self.assertNotIn(FIELD, row)

    def test_the_soak_ledger_and_the_idle_member_gain_no_field(self):
        with TemporaryDirectory() as tmp, runtime_double():
            native = MirrorAttempt(Path(tmp))
            self.assertEqual(pc._descriptor_witness(FIRST, native.ledger), hashed(native.descriptor.read_bytes()))
            self.assertIsNone(pc._descriptor_witness("idle", native.ledger))
            self.assertIsNone(pc._descriptor_witness(FIRST, None))
        with TemporaryDirectory() as tmp, runtime_double():
            soak = SoakAttempt(Path(tmp))
            soak.directory.mkdir(parents=True)
            writer = evidence.EvidenceLedger(soak.directory, soak.revision, soak.config, mode="soak")
            self.assertIsNone(pc._descriptor_witness(FIRST, writer))
            with rehearsal_double(soak, lambda _argv: soak.produce(soak.receipt())):
                pc.judged_invoke(["runtime"], "idle", soak.segment, 1800, quiet=True, contract_key="idle_soak",
                                 ledger=writer)
            row = json.loads(soak.ledger.read_bytes().splitlines()[-1])
            # The idle row keeps the exact RL-185 shape that BoundSoak requires.
            self.assertEqual(set(row), {"attempt", "kind", "argv_sha256", "spawned", "exit_status", "stdout_sha256",
                                        "stderr_sha256", "segment", "manifest", "previous_sha256"})
        with TemporaryDirectory() as tmp:
            soak = SoakAttempt(Path(tmp))
            soak.binding(soak.close())

    def test_an_observation_that_cannot_be_made_is_a_word_never_an_exception(self):
        def no_file(attempt):
            attempt.descriptor.unlink()

        def no_mirror(attempt):
            attempt.descriptor.unlink()
            attempt.mirror.rmdir()

        def mirror_is_a_file(attempt):
            no_mirror(attempt)
            attempt.mirror.write_bytes(b"{}")

        def descriptor_is_a_directory(attempt):
            attempt.descriptor.unlink()
            attempt.descriptor.mkdir()

        def template_names_no_source(attempt):
            for path in attempt.templates.values():
                path.write_bytes(json_bytes({"model": {"source": None}, "workload_profile": {"prompt_text": "{}"}}))

        def template_is_missing(attempt):
            for path in attempt.templates.values():
                path.unlink()

        def issued_config_changed(attempt):
            attempt.config.write_bytes(attempt.config.read_bytes() + b" ")

        cases = ((no_file, "absent"), (no_mirror, "absent"), (mirror_is_a_file, "absent"),
                 (descriptor_is_a_directory, "unreadable"), (template_names_no_source, "unreadable"),
                 (template_is_missing, "unreadable"), (issued_config_changed, "unreadable"))
        for damage, word in cases:
            with self.subTest(damage=damage.__name__), TemporaryDirectory() as tmp, runtime_double():
                attempt = MirrorAttempt(Path(tmp))
                damage(attempt)
                try:
                    attempt.launch((FIRST,))
                except evidence.EvidenceFailure:
                    # The changed config also fails the member's own binding, after its row is written.
                    self.assertIs(damage, issued_config_changed)
                self.assertEqual(attempt.rows()[-1][FIELD], word)
        with TemporaryDirectory() as tmp:
            # Without the runtime module no path exists, and the row says so.
            attempt = MirrorAttempt(Path(tmp))
            with patch.dict(sys.modules, {"joulewise.align.apple.r1_runtime": None}):
                attempt.launch((FIRST,))
            self.assertEqual(attempt.rows()[-1][FIELD], "unreadable")

    def test_observation_follows_links_as_the_frozen_read_does(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "blob").write_bytes(json_bytes({"max_position_embeddings": 40960}))
            (base / "mirror").mkdir()
            (base / "mirror/config.json").symlink_to(base / "blob")
            (base / "linked").symlink_to(base / "mirror", target_is_directory=True)
            for source in (base / "mirror", base / "linked"):
                witness, raw = evidence.observe_descriptor(str(source))
                self.assertEqual((witness, evidence.native_limit(raw)),
                                 (hashed((base / "blob").read_bytes()), 40960))
            for source in (None, "", 7, str(base / "missing")):
                self.assertIn(evidence.observe_descriptor(source)[0], evidence.DESCRIPTOR_WORDS)

    def test_native_limit_is_the_frozen_read_of_the_same_bytes(self):
        def frozen(path):
            # workload.py:268-272 at b2e01464d, transcribed for the comparison only.
            try:
                native_limit = json.loads(path.read_text()).get("max_position_embeddings")
                if type(native_limit) is not int or native_limit <= 0:
                    raise ValueError("max_position_embeddings must be a positive integer")
            except (OSError, ValueError, AttributeError):
                native_limit = None
            return native_limit

        samples = [b'{"max_position_embeddings":40960}', b'{"max_position_embeddings": 1}\n',
                   b'{"max_position_embeddings":0}', b'{"max_position_embeddings":-4}',
                   b'{"max_position_embeddings":true}', b'{"max_position_embeddings":40960.0}',
                   b'{"max_position_embeddings":"40960"}', b'{"max_position_embeddings":null}',
                   b'{"max_position_embeddings":[40960]}', b'{}', b'[]', b'40960', b'null', b'',
                   b'{"max_position_embeddings":40960', b'{"max_position_embeddings":40960}{}',
                   b'{"max_position_embeddings":1,"max_position_embeddings":2}',
                   b'{"max_position_embeddings":NaN}', b'{"max_position_embeddings":1e3}',
                   b'{"max_position_embeddings":' + b"9" * 40 + b'}', b'\xff\xfe{}',
                   b'\xef\xbb\xbf{"max_position_embeddings":40960}', b'{"max_position_embeddings":40960}\r\n',
                   b' {\n "max_position_embeddings" : 40961 }']
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.json"
            seen = set()
            for raw in samples:
                with self.subTest(raw=raw):
                    path.write_bytes(raw)
                    self.assertEqual(evidence.native_limit(raw), frozen(path))
                    seen.add(evidence.native_limit(raw))
            self.assertEqual(evidence.native_limit(None), None)
            self.assertLessEqual({None, 1, 2, 40960, 40961, int("9" * 40)}, seen)


class DescriptorBindingTests(unittest.TestCase):
    """RL-189 1.3, D1 and D2: attestation by the row, never by the file's mere existence."""

    def returned(self, attempt, kind=FIRST, **row):
        segment, process = attempt.producer(kind)
        attempt.ledger.member_return(kind, segment, ["runtime", kind], process=process, **row)

    def refused(self, call, reason, source, field=None):
        with self.assertRaises(evidence.EvidenceFailure) as caught:
            call()
        failure = caught.exception
        self.assertEqual((failure.reason, failure.role, failure.source, failure.field),
                         (reason, FIRST, source, field))
        return failure

    def test_d1_a_row_with_no_valid_binding_is_evidence_unverifiable(self):
        missing = object()
        for value in (missing, "", "ABSENT", "unhashed", "a" * 63, "A" * 64, "a" * 65, 7, ["absent"], {"sha256": "a" * 64}):
            with self.subTest(value=value), TemporaryDirectory() as tmp:
                attempt = MirrorAttempt(Path(tmp))
                self.returned(attempt, **({} if value is missing else {"model_descriptor": value}))
                self.refused(lambda: attempt.ledger.model_descriptor(FIRST, str(attempt.mirror)),
                             "evidence_unverifiable", evidence.LEDGER_NAME, FIELD)
        with TemporaryDirectory() as tmp:
            attempt = MirrorAttempt(Path(tmp))   # no member row at all
            self.refused(lambda: attempt.ledger.model_descriptor(FIRST, str(attempt.mirror)),
                         "evidence_unverifiable", evidence.LEDGER_NAME, FIELD)

    def test_d1_suite_reproduction_the_binding_dropped_before_the_row_is_chained(self):
        # Frozen suite v2, <member>/descriptor/no-binding: the retained row and the chain agree.
        append = evidence.EvidenceLedger._append

        def drop(ledger, row):
            return append(ledger, {key: value for key, value in row.items() if key != FIELD})

        with TemporaryDirectory() as tmp, runtime_double():
            attempt = MirrorAttempt(Path(tmp))
            with patch.object(evidence.EvidenceLedger, "_append", drop):
                attempt.launch((FIRST,))
            attempt.ledger.verify_chain()
            self.assertNotIn(FIELD, attempt.rows()[-1])
            self.refused(lambda: pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured),
                         "evidence_unverifiable", evidence.LEDGER_NAME, FIELD)

    def test_d2_bytes_must_equal_the_row_before_the_parse_after_it_and_at_the_verdict(self):
        changed = json_bytes({"max_position_embeddings": 40961})
        with TemporaryDirectory() as tmp, runtime_double():
            attempt = MirrorAttempt(Path(tmp))
            attempt.launch((FIRST,))
            clean = attempt.descriptor.read_bytes()
            bound = pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured)
            self.assertEqual((bound.limit, bound.source), (40960, str(attempt.mirror)))
            attempt.ledger.verify_final_sources()

            # Frozen suite v2, <member>/descriptor/rewritten-after-return.
            attempt.descriptor.write_bytes(changed)
            source = evidence.DESCRIPTOR_SOURCE
            self.refused(lambda: pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured),
                         "source_integrity", source)
            self.refused(attempt.ledger.verify_final_sources, "source_integrity", source)
            attempt.descriptor.unlink()
            self.refused(lambda: pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured),
                         "source_integrity", source)
            self.refused(attempt.ledger.verify_final_sources, "source_integrity", source)
            attempt.descriptor.write_bytes(clean)
            attempt.ledger.verify_final_sources()

            def parse_then_rewrite(raw):
                attempt.descriptor.write_bytes(changed)
                return evidence.native_limit(raw)

            with patch.object(pc, "native_limit", parse_then_rewrite):
                self.refused(lambda: pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured),
                             "source_integrity", source)

    def test_d2_a_bound_word_is_held_to_the_same_observation(self):
        for damage, word in ((lambda a: a.descriptor.unlink(), "absent"),
                             (lambda a: (a.descriptor.unlink(), a.descriptor.mkdir()), "unreadable")):
            with self.subTest(word=word), TemporaryDirectory() as tmp, runtime_double():
                attempt = MirrorAttempt(Path(tmp))
                damage(attempt)
                attempt.launch((FIRST,))
                self.assertEqual(attempt.rows()[-1][FIELD], word)
                self.assertIsNone(pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured).limit)
                if attempt.descriptor.is_dir():
                    attempt.descriptor.rmdir()
                attempt.descriptor.write_bytes(json_bytes({"max_position_embeddings": 40960}))
                self.refused(lambda: pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured),
                             "source_integrity", evidence.DESCRIPTOR_SOURCE)

    def test_the_issued_path_is_required(self):
        with TemporaryDirectory() as tmp, runtime_double():
            attempt = MirrorAttempt(Path(tmp))
            attempt.launch((FIRST,))
            for path in attempt.templates.values():
                path.unlink()
            self.refused(lambda: pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured),
                         "execution_limits_recompute", "config.json", "model.source")

    def test_a_published_pass_needs_a_witness_in_every_judged_row(self):
        for witness, accepted in (("a" * 64, True), ("absent", True), ("unreadable", True),
                                  (None, False), ("A" * 64, False), ("", False)):
            with self.subTest(witness=witness), TemporaryDirectory() as tmp:
                attempt = SoakAttempt(Path(tmp))
                soak_sha = attempt.close()
                reference_sha = hashed(attempt.reference.read_bytes())
                attempt.output.mkdir()
                writer = evidence.EvidenceLedger(attempt.output, attempt.revision, attempt.config,
                                                 attempt.reference, soak=attempt.binding(soak_sha))
                for kind, name in MEMBERS.items():
                    segment = attempt.output / name
                    segment.mkdir()
                    process = write_terminal(segment, kind, {"kind": kind}, attempt.config_sha)
                    writer.member_return(kind, segment, ["runtime"], process=process,
                                         model_descriptor=witness if kind == "step-d" else "a" * 64)
                published = json_bytes({"part": "C", "slots_entered": False, "evaluation": {
                    "schema": "joulewise.align.r1_part_c.v1", "verdict": "pass", "pass": True,
                    "evidence_failures": {}, "slots_entered": False}})
                for name in pc.RELEASE_COPIES:
                    (attempt.output / name).write_bytes(published)
                writer.finish("pass", {name: hashed(published) for name in pc.RELEASE_COPIES})
                (attempt.root / "part-c.stdout.log").write_text("Part C verdict: pass (pass: True)\n")
                if accepted:
                    evidence.verify_part_c_publication(attempt.root, soak_sha, reference_sha)
                else:
                    with self.assertRaisesRegex(evidence.EvidenceFailure, "verdict_binding"):
                        evidence.verify_part_c_publication(attempt.root, soak_sha, reference_sha)


def execution(**limits):
    spec = {"max_context_tokens": 40960, "deadman_s": None, "max_episode_decode_tokens": None,
            "max_turns": 4, "max_tokens": 4096, "max_episode_seconds": None}
    return SimpleNamespace(**{**spec, **limits})


class NativeLimitDecisionTests(unittest.TestCase):
    """RL-189 1.3, D4 to D6, and 1.4: a native claim is attested and a replayed one only exists."""

    UNREAD = pc.UNREAD_LIMIT_FLAG

    def judge(self, limits, *, attested="replay", flags=(), **spec):
        descriptor = None if attested == "replay" else pc._AttestedDescriptor("synthetic-mirror", attested)
        episode = SimpleNamespace(turns=(), start_ns=0, end_ns=0)
        return pc._recompute_admissions("step-d", execution(**spec), episode, [], limits, {"deadline_ns": 1},
                                        [], list(flags), descriptor)

    def refused(self, reason, field, limits, **kwargs):
        with self.assertRaises(evidence.EvidenceFailure) as caught:
            self.judge(limits, **kwargs)
        failure = caught.exception
        self.assertEqual((failure.reason, failure.role, failure.source, failure.field),
                         (reason, "step-d", "outputs/align_episode.json", field))
        self.assertNotIn(str(MARKER), json.dumps(failure.finding()))
        return failure

    @staticmethod
    def limits(native, cap=40960):
        return {"max_context_tokens": cap, "max_position_embeddings": native}

    def test_d4_the_claim_must_equal_the_attested_limit_by_type_and_value(self):
        field = "context_limits.max_position_embeddings"
        self.assertEqual(self.judge(self.limits(40960), attested=40960), 40960)
        # Frozen suite v2: the four native-limit shifts (mirror 40,960, claim 40,961) ...
        failure = self.refused("admission_recompute", field, self.limits(40961), attested=40960)
        self.assertEqual(failure.peer, evidence.DESCRIPTOR_SOURCE)
        # ... and <member>/descriptor/mirror-40961-claim-40960 and consistent-40961.
        self.refused("admission_recompute", field, self.limits(40960), attested=40961)
        self.assertEqual(self.judge(self.limits(40961), attested=40961), 40960)
        for claim in (None, True, 40960.0, "40960", [40960], 0, -40960, 40959, MARKER):
            with self.subTest(claim=claim):
                self.refused("admission_recompute", field, self.limits(claim), attested=40960)
        self.refused("admission_recompute", field, {"max_context_tokens": 40960}, attested=40960)
        self.refused("admission_recompute", field, None, attested=40960)
        # An unread limit is claimed as null and as nothing else.
        for claim in (40960, 0, False, "", MARKER):
            with self.subTest(unread_claim=claim):
                self.refused("admission_recompute", field, self.limits(claim), attested=None, flags=[self.UNREAD])
        self.refused("admission_recompute", field, {"max_context_tokens": 40960}, attested=None,
                     flags=[self.UNREAD])

    def test_d5_the_limit_is_unread_exactly_when_the_episode_flags_say_so(self):
        self.assertEqual(self.judge(self.limits(None), attested=None, flags=[self.UNREAD]), 40960)
        self.refused("flag_source", self.UNREAD, self.limits(None), attested=None)
        self.refused("flag_source", self.UNREAD, self.limits(None), attested=None, flags=["other.flag"])
        self.refused("flag_source", self.UNREAD, self.limits(40960), attested=40960, flags=[self.UNREAD])
        # The replay keeps D5 on the recorded claim.
        self.assertEqual(self.judge(self.limits(None), flags=[self.UNREAD]), 40960)
        self.refused("flag_source", self.UNREAD, self.limits(None))
        self.refused("flag_source", self.UNREAD, self.limits(40960), flags=[self.UNREAD])

    def test_d6_the_recorded_cap_is_the_frozen_function_of_the_limit_and_the_issued_configuration(self):
        def frozen(native_limit, spec):
            # workload.py:283-289 at b2e01464d, transcribed for the comparison only.
            cap = min(
                x for x in (native_limit, spec.max_context_tokens) if x is not None
            ) if native_limit is not None or spec.max_context_tokens is not None else None
            if spec.max_episode_decode_tokens is not None or spec.deadman_s is not None:
                cap = min(40960, cap or 40960)
            return cap

        field = "context_limits.max_context_tokens"
        count = 0
        for native in (None, 1024, 40959, 40960, 40961, 131072):
            for configured in (None, 2048, 40960, 65536):
                for deadman in (None, 1000.0):
                    for budget in (None, 6144):
                        spec = {"max_context_tokens": configured, "deadman_s": deadman,
                                "max_episode_decode_tokens": budget}
                        cap = frozen(native, execution(**spec))
                        flags = [self.UNREAD] if native is None else []
                        with self.subTest(native=native, **spec):
                            self.assertEqual(pc.frozen_context_cap(native, execution(**spec)), cap)
                            self.assertEqual(self.judge(self.limits(native, cap), attested=native, flags=flags,
                                                        **spec), cap)
                            for wrong in ((cap or 0) + 1, None if cap is not None else 40960, float(cap or 1), True):
                                self.refused("admission_recompute", field, self.limits(native, wrong),
                                             attested=native, flags=flags, **spec)
                            self.refused("admission_recompute", field, {"max_position_embeddings": native},
                                         attested=native, flags=flags, **spec)
                            count += 1
        self.assertEqual(count, 96)

    def test_the_replay_judges_the_claim_by_existence_and_a_native_run_never_does(self):
        field = "context_limits.max_position_embeddings"
        # RL-189 1.4: any positive integer that reproduces the recorded cap is admissible in a replay.
        for claim in (40960, 40961, 131072):
            self.assertEqual(self.judge(self.limits(claim)), 40960)
            if claim != 40960:
                self.refused("admission_recompute", field, self.limits(claim), attested=40960)
        self.refused("admission_recompute", "context_limits.max_context_tokens", self.limits(1024))
        for claim in (0, -1, True, 1.5, "40960", [1]):
            with self.subTest(claim=claim):
                self.refused("admission_recompute", field, self.limits(claim))
        self.refused("admission_recompute", field, {"max_context_tokens": 40960})

    def test_the_replay_record_says_the_native_limit_is_unattested(self):
        runtime = ModuleType("joulewise.align.apple.r1_runtime")
        runtime.load_config = lambda _path: (_ for _ in ()).throw(ValueError(f"private {MARKER}"))
        gates = ModuleType("joulewise.align.apple.thermal_gates")
        apple = ModuleType("joulewise.align.apple")
        apple.r1_runtime, apple.thermal_gates = runtime, gates
        align = ModuleType("joulewise.align")
        align.apple = apple
        doubles = {module.__name__: module for module in (align, apple, runtime, gates)}
        with TemporaryDirectory() as tmp, patch.dict(sys.modules, doubles):
            attempt = Attempt(Path(tmp))
            with rehearsal_double(attempt, lambda _argv: self.fail("a replay launches nothing")):
                record = pc.replay_archived(attempt.output, attempt.config)
        self.assertEqual(record["native_limit"], dict.fromkeys(MEMBERS, "unattested"))
        self.assertEqual((record["binding"], record["verdict"], record["failing_checks"]),
                         ("archived_custody", "other_failure", ["evidence_unverifiable"]))
        self.assertNotIn(str(MARKER), json.dumps(record))


class PrefillStartWitnessTests(unittest.TestCase):
    """The prefill start is delayed past the endpoint's start stamp only by recorded producer phases."""

    @staticmethod
    def event(kind, phase, at, **metadata):
        return {"event_type": kind, "phase": phase, "timestamp_s": at, "message": "synthetic",
                "metadata": {"align_turn_index": 0, **metadata}}

    def judge(self, prefill_start, lead=()):
        stamp = lambda at: {"epoch_s": at, "monotonic_before_s": at, "monotonic_after_s": at,
                            "wall_resolution_s": 1e-9, "monotonic_resolution_s": 1e-9}
        turn = SimpleNamespace(index=0, start_ns=10 * 10**9, first_token_ns=12 * 10**9, end_ns=13 * 10**9,
                               decode_tokens=1)
        episode = SimpleNamespace(turns=[turn], clock_domain="synthetic")
        record = {"start_stamp": stamp(10.0), "end_stamp": stamp(13.0),
                  "clock_mapping": {"offset_ns": 0, "episode_domain": "synthetic"}}
        events = [*lead, self.event("phase_start", "prefill", prefill_start),
                  self.event("phase_end", "prefill", 12.0),
                  self.event("phase_start", "decode", 12.0, max_tokens=4096),
                  self.event("token", "decode", 12.5, index=0),
                  self.event("phase_end", "decode", 13.0, emitted_tokens=1, requested_output_tokens=4096)]
        with runtime_double():
            pc._recompute_turn_boundaries("step-d", episode, [record], events, (), 4096)

    def refused(self, field, *args, **kwargs):
        with self.assertRaises(evidence.EvidenceFailure) as caught:
            self.judge(*args, **kwargs)
        failure = caught.exception
        self.assertEqual((failure.reason, failure.source, failure.field, failure.index),
                         ("turn_boundary_recompute", "events.jsonl", field, 0))

    def phases(self, *times, phases=("tokenize", "tokenize", "generation_setup", "generation_setup"), **metadata):
        kinds = ("phase_start", "phase_end") * 2
        return [self.event(kind, phase, at, **metadata) for kind, phase, at in zip(kinds, phases, times)]

    def test_with_no_recorded_phase_the_prefill_start_is_the_start_stamp(self):
        self.judge(10.0)
        # Frozen suite v2: <member>/.../events.jsonl/<prefill start>.timestamp_s/shift in four members.
        for at in (11.0, 12.0, 10.000001):
            with self.subTest(at=at):
                self.refused("prefill_start", at)
        self.refused("phase_order", 9.0)

    def test_only_the_whole_recorded_sequence_witnesses_a_delay(self):
        self.judge(11.0, self.phases(10.2, 10.6, 10.6, 10.9))
        self.judge(11.0, self.phases(10.0, 10.0, 11.0, 11.0))
        self.judge(10.0, self.phases(10.0, 10.0, 10.0, 10.0))
        whole = self.phases(10.2, 10.6, 10.6, 10.9)
        damaged = {
            "after the prefill start": self.phases(10.2, 10.6, 10.6, 11.5),
            "before the start stamp": self.phases(9.9, 10.6, 10.6, 10.9),
            "out of order in time": self.phases(10.6, 10.2, 10.7, 10.9),
            "one event": whole[:1], "no generation setup": whole[:2], "no setup end": whole[:3],
            "no tokenize start": whole[1:], "repeated": [*whole, *whole], "reordered": [whole[2], whole[3], *whole[:2]],
            "a start for an end": [whole[0], {**whole[1], "event_type": "phase_start"}, *whole[2:]],
            "a stage event": [{**whole[0], "event_type": "stage_started"}, *whole[1:]],
        }
        for name, lead in damaged.items():
            with self.subTest(lead=name):
                self.refused("prefill_start", 11.0, lead)
        for name, lead in (("another turn", self.phases(10.2, 10.6, 10.6, 10.9, align_turn_index=1)),
                           ("no turn", [{**mark, "metadata": {}} for mark in whole]),
                           ("a turn that is not an integer", self.phases(10.2, 10.6, 10.6, 10.9, align_turn_index="0"))):
            with self.subTest(orphan=name), self.assertRaises(evidence.EvidenceFailure) as caught:
                self.judge(11.0, lead)
            self.assertEqual((caught.exception.reason, caught.exception.field),
                             ("turn_boundary_recompute", "prefill_start"))

    def test_audit_reproduction_an_orphan_tokenize_end_witnesses_nothing(self):
        # Audit round 1, `orphan-tokenize`: a lone tokenize end at the old stamp, the prefill start one microsecond on.
        orphan = self.event("phase_end", "tokenize", 10.0)
        self.refused("prefill_start", 10.000001, [orphan])
        self.refused("prefill_start", 10.0, [orphan])

    def test_a_pre_prefill_phase_recorded_after_the_prefill_start_is_an_orphan(self):
        stamp = lambda at: {"epoch_s": at, "monotonic_before_s": at, "monotonic_after_s": at,
                            "wall_resolution_s": 1e-9, "monotonic_resolution_s": 1e-9}
        turn = SimpleNamespace(index=0, start_ns=10 * 10**9, first_token_ns=12 * 10**9, end_ns=13 * 10**9,
                               decode_tokens=1)
        episode = SimpleNamespace(turns=[turn], clock_domain="synthetic")
        record = {"start_stamp": stamp(10.0), "end_stamp": stamp(13.0),
                  "clock_mapping": {"offset_ns": 0, "episode_domain": "synthetic"}}
        for at in (10.0, 11.0):
            events = [self.event("phase_start", "prefill", at), *self.phases(10.2, 10.6, 10.6, 10.9),
                      self.event("phase_end", "prefill", 12.0),
                      self.event("phase_start", "decode", 12.0, max_tokens=4096),
                      self.event("token", "decode", 12.5, index=0),
                      self.event("phase_end", "decode", 13.0, emitted_tokens=1, requested_output_tokens=4096)]
            with self.subTest(at=at), runtime_double(), self.assertRaises(evidence.EvidenceFailure) as caught:
                pc._recompute_turn_boundaries("step-d", episode, [record], events, (), 4096)
            self.assertEqual((caught.exception.reason, caught.exception.field),
                             ("turn_boundary_recompute", "prefill_start"))


class DescriptorMarkerTests(unittest.TestCase):
    """RL-183c test 3 over the RL-189 checks: names leave the process, no planted value or path does."""

    def test_no_descriptor_finding_or_emitted_line_carries_a_value_or_a_path(self):
        with TemporaryDirectory() as tmp, runtime_double():
            attempt = MirrorAttempt(Path(tmp), limit=MARKER)
            attempt.launch((FIRST, "step-d"))
            bound = pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured)
            self.assertEqual(bound.limit, MARKER)
            failures = []

            def collect(call):
                with self.assertRaises(evidence.EvidenceFailure) as caught:
                    call()
                failures.append(caught.exception)

            judge = NativeLimitDecisionTests()
            collect(lambda: judge.judge({"max_context_tokens": 40960, "max_position_embeddings": MARKER + 1},
                                        attested=MARKER))                                             # D4
            collect(lambda: judge.judge({"max_context_tokens": 40960, "max_position_embeddings": MARKER},
                                        attested=MARKER, flags=[pc.UNREAD_LIMIT_FLAG]))               # D5
            collect(lambda: judge.judge({"max_context_tokens": MARKER, "max_position_embeddings": MARKER},
                                        attested=MARKER))                                             # D6
            collect(lambda: PrefillStartWitnessTests().judge(10.0 + MARKER))
            attempt.descriptor.write_bytes(json_bytes({"max_position_embeddings": MARKER + 1}))
            collect(lambda: pc._attested_descriptor(attempt.ledger, FIRST, attempt.configured))       # D2
            append = evidence.EvidenceLedger._append
            with patch.object(evidence.EvidenceLedger, "_append", lambda ledger, row: append(
                    ledger, {key: value for key, value in row.items() if key != FIELD})):
                attempt.launch(("d-bank-benign-s1",))
            collect(lambda: pc._attested_descriptor(attempt.ledger, "d-bank-benign-s1", attempt.configured))  # D1
            self.assertEqual([failure.reason for failure in failures],
                             ["admission_recompute", "flag_source", "admission_recompute",
                              "turn_boundary_recompute", "source_integrity", "evidence_unverifiable"])

            stdout, stderr = StringIO(), StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr), self.assertRaises(ValueError) as raised:
                pc._emit_part_c(attempt.output, 0, None, failures=tuple(failures), ledger=attempt.ledger)
            files = [attempt.output / name for name in (*pc.RELEASE_COPIES, evidence.LEDGER_NAME)]
            released = [stdout.getvalue(), stderr.getvalue(), str(raised.exception),
                        *[file.read_text() for file in files]]
            for text in released:
                self.assertNotIn(str(MARKER), text)
                self.assertNotIn(str(attempt.mirror), text)
                self.assertNotIn("mirror-", text)
            findings = [json.loads(line) for line in stdout.getvalue().splitlines() if line.startswith("{")]
            self.assertEqual(len(findings), len(failures))
            for finding in findings:
                self.assertEqual(set(finding), {"verdict", "reason", "role", "file_or_stream", "row_or_index",
                                                "field", "peer"})
                self.assertEqual(finding["verdict"], "other_failure")
            for row in attempt.rows():
                if FIELD in row:
                    self.assertTrue(evidence.is_descriptor_witness(row[FIELD]))


# ---- Audit round 1: invalid raw evidence and the frozen driver's decisions -------------------------

class RawEvidenceTests(unittest.TestCase):
    """A trace, an event stream and a journal each parse as the producer wrote them."""

    WINDOW = (2000.0, 3800.0)

    def trace(self, raw, window=None):
        pc._check_power_trace(FIRST, raw, *(window or self.WINDOW))

    def refused(self, call, field):
        with self.assertRaises(evidence.EvidenceFailure) as caught:
            call()
        failure = caught.exception
        self.assertEqual((failure.reason, failure.role, failure.field), ("bundle_binding", FIRST, field))
        self.assertNotIn(str(MARKER), json.dumps(failure.finding()))
        return failure

    def test_the_power_trace_is_the_producers_csv(self):
        d018 = b"timestamp_s,power_w,source,rail\n"
        interval = b"timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
        self.trace(d018)
        self.trace(d018 + b"2001.5,0.002,powermetrics,gpu_power\n2002.5,0.002,powermetrics,cpu_power\n")
        self.trace(interval + b"2001,0.002,powermetrics,gpu_power,2000,2001\n3800,0.5,powermetrics,gpu_power,,\n")
        # Audit round 1, `one-byte-predecessor-trace` and the file sweep's truncation.
        self.refused(lambda: self.trace(b"{"), "header")
        self.refused(lambda: self.trace(b""), "header")
        for header in (b"timestamp_s,power_w,source\n",   # v2's header-only trace: not a D-018 header (RL-193 1)
                       b"timestamp_s,power_w\n", b"power_w,timestamp_s,source\n", b"timestamp_s,power_w,source,rail,x\n",
                       b"timestamp_s,power_w,source,rail,interval_start_s\n", b'{"attempt":"foreign"}\n'):
            with self.subTest(header=header):
                self.refused(lambda: self.trace(header), "header")
        self.refused(lambda: self.trace(b"\xff\xfe"), "invalid")
        for row in (b"2001.5,0.002\n", b"2001.5,0.002,powermetrics,gpu_power,extra\n", b"x,0.002,powermetrics,gpu_power\n",
                    b"2001.5,nan,powermetrics,gpu_power\n", b"inf,0.002,powermetrics,gpu_power\n",
                    f"2001.5,{MARKER}x,powermetrics,gpu_power\n".encode()):
            with self.subTest(row=row):
                self.refused(lambda: self.trace(d018 + row), "row")
        for row in (b"2001,0.002,powermetrics,gpu_power,2000,\n", b"2001,0.002,powermetrics,gpu_power,2001.5,2001\n"):
            with self.subTest(row=row):
                self.refused(lambda: self.trace(interval + row), "row")

    def test_a_trace_from_outside_the_members_terminal_bracket_is_another_members(self):
        # Audit round 1, the file sweep's `swap`: D bank's trace in the predecessor's bundle.
        interval = b"timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"
        foreign = interval + b"6134,0.002,powermetrics,gpu_power,6133,6134\n"
        self.trace(foreign, (6000.0, 7800.0))
        failure = self.refused(lambda: self.trace(foreign), "window")
        self.assertEqual((failure.source, failure.index, failure.peer), ("power_trace.csv", 0, MANIFEST))
        d018 = b"timestamp_s,power_w,source,rail\n"
        self.trace(d018 + b"2000,1,p,gpu_power\n3800,1,p,gpu_power\n")
        for row in (b"1999.999,1,p,gpu_power\n", b"3800.001,1,p,gpu_power\n"):
            self.refused(lambda: self.trace(d018 + b"2001,1,p,gpu_power\n" + row), "window")
        self.refused(lambda: self.trace(interval + b"2000.5,1,p,gpu_power,1999.5,2000.5\n"), "window")

    def events(self, **last):
        final = {"timestamp_s": 4.0, **pc.FINAL_EVENT, **last}
        return [{"timestamp_s": 1.0, "event_type": "phase_start", "phase": "prefill", "message": "", "metadata": {}},
                final]

    def test_each_event_is_typed_and_the_stream_ends_with_the_producers_finalization(self):
        pc._check_event_rows(FIRST, self.events())
        # Audit round 1, `empty-phase`.
        self.refused(lambda: pc._check_event_rows(FIRST, self.events(phase="")), None)
        for change in ({"phase": "stage"}, {"message": "finalized"}, {"metadata": {"private": MARKER}},
                       {"event_type": "run_finalised"}, {"timestamp_s": 0.5}):
            with self.subTest(change=change):
                self.refused(lambda: pc._check_event_rows(FIRST, self.events(**change)), "run_finalized")
        for key, value in (("phase", ""), ("phase", None), ("event_type", ""), ("event_type", 7), ("message", None),
                           ("metadata", []), ("timestamp_s", float("nan")), ("timestamp_s", "1")):
            rows = self.events()
            rows[0][key] = value
            with self.subTest(key=key, value=value):
                failure = self.refused(lambda: pc._check_event_rows(FIRST, rows), None)
                self.assertEqual(failure.index, 0)
        twice = self.events()
        self.refused(lambda: pc._check_event_rows(FIRST, [twice[1], *twice]), "run_finalized")

    @staticmethod
    def journal():
        sensors = {"s_fast": "TV0h", "s_slow": "TV1h"}

        def stamp(at):
            return {"wall_ns": 10**9 + at, "monotonic_ns": at, "monotonic_raw_ns": 5 * 10**8 + at}

        def row(seq, kind, begin, finish, values):
            return {"schema": "joulewise.align_thermal.v1", "module": "temperature", "session": "synthetic",
                    "seq": seq, "kind": kind, "started": stamp(begin), "finished": stamp(finish), "values": values,
                    "raw": [], "error": None}

        def reading(seq, at):
            temps = {key: 35.0 for key in sensors.values()}
            return row(seq, "reading", at, at + 10, {
                "source": "smc", "units": {key: "degC" for key in temps}, "sensors": temps, "errors": {},
                "readings": {key: {"value": value, "error": None} for key, value in temps.items()},
                "status": {"os_level": 0, "pm_state": "Nominal", "pm_observed_ns": at, "monotonic_ns": at + 10}})

        gate = {"kind": "G0", "turn": 0, "token_count": None}
        rows = [row(1, "session_start", 0, 0, {"thermal": sensors}), reading(2, 100),
                row(3, "align_thermal_gate", 200, 200, {"state": "begin", "gate_kind": "G0", "turn": 0}),
                reading(4, 300), reading(5, 400),
                row(6, "align_thermal_gate", 500, 500, {"state": "end", "gate": gate}), reading(7, 600),
                row(8, "session_end", 700, 700, {"collector_error": None, "coverage": {"span_ns": [0, 650]}})]
        return sensors, rows

    @staticmethod
    @contextmanager
    def thermal_double():
        thermal = ModuleType("joulewise.align.apple.thermal")
        thermal.keys = lambda sensors: (sensors["s_fast"], sensors["s_slow"])
        thermal.valid_value = lambda key, value: type(value) in (int, float)
        thermal.Coverage = lambda begin, selected: SimpleNamespace(
            observe=lambda *args: None, report=lambda end: {"span_ns": [begin, end]})
        apple = ModuleType("joulewise.align.apple")
        apple.thermal = thermal
        align = ModuleType("joulewise.align")
        align.apple = apple
        with patch.dict(sys.modules, {module.__name__: module for module in (align, apple, thermal)}):
            yield

    def test_no_journal_row_starts_before_the_row_above_it_finished_on_any_clock(self):
        def validate(rows):
            pc._validate_sidecar(rows, sensors, "d-bank-benign-s1", pc.THERMAL_SOURCE, gated=True)

        def out_of_order(rows, index):
            with self.assertRaises(evidence.EvidenceFailure) as caught:
                validate(rows)
            failure = caught.exception
            self.assertEqual((failure.reason, failure.field, failure.index), ("reading_record", "stamp_order", index))

        with self.thermal_double():
            sensors, rows = self.journal()
            validate(rows)
            # Audit round 1, `G0-begin-after-end`: the begin row stamped at the session's newest time.
            sensors, rows = self.journal()
            rows[2]["started"]["monotonic_ns"] = rows[2]["finished"]["monotonic_ns"] = rows[-1]["finished"]["monotonic_ns"]
            out_of_order(rows, 3)
            # Audit round 1, `reading-out-of-order-wall_ns` and `-monotonic_raw_ns`.
            for clock in pc.JOURNAL_CLOCKS:
                sensors, rows = self.journal()
                rows[4]["started"][clock] = rows[3]["started"][clock] - 1
                with self.subTest(clock=clock):
                    out_of_order(rows, 4)
            for index in range(1, 8):
                for clock in pc.JOURNAL_CLOCKS:
                    sensors, rows = self.journal()
                    rows[index]["started"][clock] = rows[index - 1]["finished"][clock] - 1
                    with self.subTest(row=index, clock=clock), self.assertRaises(evidence.EvidenceFailure):
                        validate(rows)


DRIVER_DOUBLE = '''
"""A stand-in shaped like the pinned align_r1_rehearsal.run, for trees without the R1 driver."""
STEP_D_NAME = "step_D"
GATED = ("D_bank",)
PLAN = [("pre", "calibration-pre"), ("idle_soak", "idle"), ("P", "capture-predecessor-30b"), (STEP_D_NAME, "step-d"),
        ("D_bank", "d-bank-benign-s1"), ("D_other", "d-spam-benign-s1-a"), ("X_G", "x-g")]


class Refusal(RuntimeError):
    pass


def phase_plan(include_4bit=False, precool_cap_s=None):
    return [(name, kind, None, "heavy") for name, kind in PLAN]


def runtime_precool_cap_s(runtime):
    return 600.0


def admission_units(runtime=None):
    return [[row, *([phase_plan()[index + 1]] if row[1] == "capture-predecessor-30b" else [])]
            for index, row in enumerate(phase_plan()) if row[1] != "step-d"]


def _admission_unit(args, output, unit, record, *, soak_reference=None, extra=None):
    raise AssertionError("the double never launches")


def write_soak_reference(output, row):
    raise AssertionError("the double never writes")


def thermometry_record(name, result):
    block = result.get("thermometry")
    if not isinstance(block, dict):
        raise Refusal("no classification")
    return dict(block)


def _check_member_powermode(name, result, mode):
    if (result.get("ac_powermode") or {}).get("value") != mode:
        raise Refusal("powermode")


def deadman_summary(name, result):
    if "deadman" not in result:
        raise Refusal("no deadman block")
    return {"duty_bar": {"verdict": "pass" if result["deadman"]["share"] <= 0.4 else "fail"}}


def run(args):
    results, record = {}, {"phases": []}
    guard = open(__file__)
    try:
        with guard:
            soak_reference = None
            inconclusive, skipped, pending = {}, {}, {}
            units = {unit[0][0]: unit for unit in admission_units(args.runtime)}
            last_d_turn = None
            for name, kind, duration, workload_class in phase_plan(args.include_4bit, precool_cap_s=precool_cap):
                if kind != "idle" and kind != "capture-predecessor-30b" and kind != "step-d" and results.get(
                        STEP_D_NAME, {}).get("reference_unobserved"):
                    skipped[name] = inconclusive[name] = "reference unobserved"
                    continue
                if name not in pending:
                    pending.update(_admission_unit(args, output, units[name], record, soak_reference=soak_reference))
                results[name], row = pending.pop(name)
                if results[name].get("segment_status") == "inconclusive":
                    if results[name].get("g0_released") is not False:
                        raise Refusal("an INCONCLUSIVE segment must report g0_released false")
                    inconclusive[name] = "G0 unreleased"
                if name == "idle_soak":
                    soak_reference = write_soak_reference(output, row)
                if kind == "x-g" and last_d_turn is None:
                    inconclusive[name] = "the preceding member dispatched no D turn"
                if kind in ("step-d", "d-bank-benign-s1"):
                    last_d_turn = None if results[name].get("reference_unobserved") else name
        thermometry_d = thermometry_record(STEP_D_NAME, results[STEP_D_NAME])
        thermometry = {"D": thermometry_d}
        thermometry["bar"] = thermometry_d["status"]
        if thermometry["bar"] != "pass":
            inconclusive["thermometry.D"] = "thermometry failed"
        ac_powermode = None
        for name, result in results.items():
            if any(proc["comm"].startswith("claude") for census in result.get("census", [])
                   for proc in census["processes"]):
                inconclusive[name] = "agent feed overlap"
    finally:
        pass
    return inconclusive
'''


@contextmanager
def driver_double(source=DRIVER_DOUBLE):
    import importlib.util

    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "align_r1_rehearsal.py"
        path.write_text(source)
        spec = importlib.util.spec_from_file_location("scripts.align_r1_rehearsal", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.dict(sys.modules, {module.__name__: module}), \
                patch.object(scripts, "align_r1_rehearsal", module, create=True):
            yield module


class IssuedDriverTests(unittest.TestCase):
    """The frozen rehearsal's own loop statements decide admission, skips and INCONCLUSIVE segments."""

    D, X = "d-bank-benign-s1", "x-g"

    @staticmethod
    def receipts(*, contrast=True):
        mode = {"value": 0}
        receipts = {FIRST: {"ac_powermode": mode}, "step-d": {
            "ac_powermode": mode, "g0_released": True, "thermometry": {"status": "pass"},
            "census": [{"processes": [{"comm": "synthetic-worker"}]}]},
            "d-bank-benign-s1": {"ac_powermode": mode, "deadman": {"share": 0.4}}}
        if contrast:
            receipts["x-g"] = {"ac_powermode": mode}
        return receipts

    def replay(self, receipts, soak=None):
        pc._check_issued_driver(["runtime"], {}, {"private": MARKER} if soak is None else soak, "reference", receipts)

    def refused(self, field, role, receipts, **kwargs):
        with self.assertRaises(evidence.EvidenceFailure) as caught:
            self.replay(receipts, **kwargs)
        failure = caught.exception
        self.assertEqual((failure.reason, failure.field, failure.role, failure.source),
                         (pc.ISSUED_DRIVER, field, role, RECEIPT))
        self.assertNotIn(str(MARKER), json.dumps(failure.finding()))

    def test_the_drivers_statements_run_over_the_bound_receipts(self):
        with driver_double() as driver:
            receipts = self.receipts()
            before = json.dumps(receipts, sort_keys=True)
            self.replay(receipts)
            self.replay(self.receipts(contrast=False))   # a proven X_G refusal leaves X_G out of the plan
            self.assertEqual(json.dumps(receipts, sort_keys=True), before)
            loop_code, close_code = pc._issued_driver_program()
            self.assertEqual({loop_code.co_filename, close_code.co_filename}, {driver.__file__})
            self.assertIn("pending", loop_code.co_names)
            self.assertIn("thermometry", close_code.co_names)

    def test_audit_reproductions_a_status_or_reference_field_the_driver_reads(self):
        with driver_double():
            # Audit round 1, `S-status`: an INCONCLUSIVE Step D that also reports a released G0.
            receipts = self.receipts()
            receipts["step-d"]["segment_status"] = "inconclusive"
            self.refused("refused", "attempt", receipts)
            receipts["step-d"]["g0_released"] = False
            self.refused("inconclusive", "step-d", receipts)
            # Audit round 1, `S-reference`: the driver skips every member after Step D.
            receipts = self.receipts()
            receipts["step-d"]["reference_unobserved"] = True
            self.refused("skipped", self.D, receipts)
            # Audit round 1, `D-reference`: X_G then follows no D turn.
            receipts = self.receipts()
            receipts[self.D]["reference_unobserved"] = True
            self.refused("inconclusive", self.X, receipts)
            self.replay({kind: row for kind, row in receipts.items() if kind != self.X})

    def test_every_other_decision_of_the_loop_and_close_binds(self):
        with driver_double():
            receipts = self.receipts()
            receipts["step-d"]["thermometry"]["status"] = "fail"
            self.refused("inconclusive", "step-d", receipts)
            receipts = self.receipts()
            del receipts["step-d"]["thermometry"]
            self.refused("refused", "attempt", receipts)
            receipts = self.receipts()
            receipts[self.X]["census"] = [{"processes": [{"comm": "claude"}]}]
            self.refused("inconclusive", self.X, receipts)
            self.refused("inconclusive", "idle", self.receipts(), soak={"census": [{"processes": [{"comm": "claude"}]}]})
            receipts = self.receipts()
            receipts[self.D]["ac_powermode"] = {"value": 2}
            self.refused("refused", "attempt", receipts)
            receipts = self.receipts()
            receipts[self.X]["census"] = [{"processes": [{}]}]
            self.refused("unavailable", "attempt", receipts)

    def test_a_plan_or_source_that_cannot_be_replayed_is_never_a_pass(self):
        with driver_double():
            receipts = self.receipts()
            self.refused("phase_plan", "attempt", {kind: receipts[kind] for kind in (FIRST, self.D, "step-d", self.X)})
            self.refused("phase_plan", "attempt", {**receipts, "d-spam-benign-s1-b": {}})
        for damage in (("with guard:", "with open(__file__):"), ("in phase_plan(", "in list("),
                       ('thermometry["bar"] = ', 'thermometry["bars"] = '), ("ac_powermode = None", "mode = None"),
                       ("in results.items():", "in list(results.items()):"), ("def run(args):", "def ran(args):")):
            with self.subTest(damage=damage), driver_double(DRIVER_DOUBLE.replace(*damage)):
                self.refused("unavailable", "attempt", self.receipts())
        with rehearsal_double(Attempt.__new__(Attempt), None):   # a driver with no source file
            self.refused("unavailable", "attempt", self.receipts())

    def test_a_passing_mechanics_line_is_also_the_frozen_duty_bar(self):
        with driver_double():
            pc._check_issued_duty_bar({"deadman": {"share": 0.4}})
            for receipt in ({"deadman": {"share": 0.400001}}, {}, {"deadman": {}}):
                with self.subTest(receipt=receipt), self.assertRaises(evidence.EvidenceFailure) as caught:
                    pc._check_issued_duty_bar(receipt)
                failure = caught.exception
                self.assertEqual((failure.reason, failure.role, failure.field, failure.peer),
                                 ("duty_budget", self.D, "duty_bar", pc.ISSUED_DRIVER))


class SoakArgvTests(unittest.TestCase):
    """EVIDENCE-SPEC row 23: the soak row's argv digest is the issued soak's argument list."""

    RUNTIME = ["synthetic-runtime", "--config", "runtime.json"]

    def bound(self, tmp, argv):
        attempt = SoakAttempt(Path(tmp))
        attempt.directory.mkdir(parents=True)
        writer = evidence.EvidenceLedger(attempt.directory, attempt.revision, attempt.config, mode="soak")
        receipt = attempt.receipt()
        writer.member_return("idle", attempt.segment, argv(str(attempt.segment)), process=attempt.produce(receipt))
        attempt.row.write_bytes(json_bytes({"name": "idle_soak", "attempt": 0, "output_dir": str(attempt.segment),
                                            "result": receipt}))
        attempt.reference.write_bytes(json_bytes({"source_segment": "idle_soak", "source_output": str(attempt.segment),
                                                  "attempt": 0}))
        writer.finish_soak("accepted")
        return attempt.binding(hashed(attempt.ledger.read_bytes()))

    def idle(self, *tail, runtime=None, kind="idle"):
        return lambda segment: [*(runtime or self.RUNTIME), "--r1-kind", kind, "--output", segment, *tail]

    def test_the_frozen_invokers_lists_for_the_issued_soak_are_accepted(self):
        for tail in (("--duration-s", "1800"), ("--duration-s", "1800.0"),
                     ("--host-lock-fd", "0", "--duration-s", "1800.0"), ("--host-lock-fd", "16", "--duration-s", "1800"),
                     ("--host-lock-fd", str(evidence.LOCK_FD_LIMIT - 1), "--duration-s", "1800.0")):
            with self.subTest(tail=tail), TemporaryDirectory() as tmp:
                self.bound(tmp, self.idle(*tail)).verify_argv(self.RUNTIME, 1800)
        with TemporaryDirectory() as tmp:
            self.bound(tmp, self.idle("--duration-s", "0.5")).verify_argv(self.RUNTIME, 0.5)

    def test_any_other_list_is_refused(self):
        damaged = {
            # Audit round 1, `wrong-soak-argv-duration-1-receipt-1800`.
            "one second": self.idle("--duration-s", "1"),
            "no duration": self.idle(), "another spelling": self.idle("--duration-s", "1800.00"),
            "a soak reference": self.idle("--duration-s", "1800", "--soak-reference", "reference.json"),
            "duration before the lock": self.idle("--duration-s", "1800", "--host-lock-fd", "16"),
            "a lock that is no descriptor": self.idle("--host-lock-fd", "-1", "--duration-s", "1800"),
            "a lock beyond the limit": self.idle("--host-lock-fd", str(evidence.LOCK_FD_LIMIT), "--duration-s", "1800"),
            "another runtime": self.idle("--duration-s", "1800", runtime=["other-runtime", "--config", "runtime.json"]),
            "another kind": self.idle("--duration-s", "1800", kind="idle-until-soak"),
            "another output": lambda segment: [*self.RUNTIME, "--r1-kind", "idle", "--output", segment + "-other",
                                               "--duration-s", "1800"],
            "an extra argument": self.idle("--duration-s", "1800", "--smoke-part", "A"),
        }
        for name, argv in damaged.items():
            with self.subTest(argv=name), TemporaryDirectory() as tmp:
                bound = self.bound(tmp, argv)
                with self.assertRaises(evidence.EvidenceFailure) as caught:
                    bound.verify_argv(self.RUNTIME, 1800)
                failure = caught.exception
                self.assertEqual((failure.reason, failure.role, failure.source, failure.field),
                                 ("sequence", "idle", evidence.LEDGER_NAME, "argv_sha256"))
        with TemporaryDirectory() as tmp:
            with self.assertRaises(evidence.EvidenceFailure):
                self.bound(tmp, self.idle("--duration-s", "1800")).verify_argv(self.RUNTIME, 1801)


# ---- Audit round 2: the pinned validators, bracket and order rules, and the planned run id ---------------

class PredecessorTraceD018Tests(unittest.TestCase):
    """RL-193 section 1: the whole pinned D-018 check judges the predecessor's bound trace bytes."""

    D018 = b"timestamp_s,power_w,source,rail\n"
    INTERVAL = b"timestamp_s,power_w,source,rail,interval_start_s,interval_end_s\n"

    def judge(self, raw, *, summary=b'{"status":"succeeded"}', metadata=b"{}", on_disk=None):
        """``raw`` is the bound trace. ``on_disk`` is what the member's directory holds by then, if anything."""
        from scripts.align_r1_part_c import _check_pinned_trace

        with TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "align-pilot-v3-episodes-a-e01"
            bundle.mkdir()
            if on_disk is not None:
                (bundle / "power_trace.csv").write_bytes(on_disk)
            _check_pinned_trace(FIRST, bundle, {"summary_metrics.json": summary, "metadata.json": metadata,
                                                "power_trace.csv": raw})

    def refused(self, raw, **kwargs):
        with self.assertRaises(evidence.EvidenceFailure) as caught:
            self.judge(raw, **kwargs)
        failure = caught.exception
        self.assertEqual((failure.reason, failure.role, failure.source, failure.peer),
                         ("bundle_binding", FIRST, "power_trace.csv", "bundle_read"))
        self.assertIn(failure.field, ("D-018", "invalid"))
        self.assertNotIn(str(MARKER), json.dumps(failure.finding()))

    def test_the_issued_headers_pass_and_every_other_form_is_refused(self):
        self.judge(self.D018)
        self.judge(self.INTERVAL)       # RL-193 1: either header the pinned check accepts, zero rows included
        self.judge(self.D018 + b"2001.5,0.002,powermetrics,gpu_power\n")
        self.judge(self.INTERVAL + b"2001.5,0.002,powermetrics,gpu_power,2001.0,2002.0\n")
        # Audit round 1 `audit-one-byte-predecessor-csv` and the v3 `three-column-header` case.
        for raw in (b"{", b"", b"timestamp_s,power_w,source\n", b"[]\n", b'"unclosed\xff\n',
                    b"timestamp_s,power_w,source,rail,x\n", b"power_w,timestamp_s,source,rail\n",
                    b"timestamp_s,power_w,source,rail,interval_start_s\n",
                    self.D018 + b"x,0.002,powermetrics,gpu_power\n"):
            with self.subTest(raw=raw):
                self.refused(raw)

    def test_a_validator_that_cannot_run_or_a_summary_that_cannot_be_read_is_never_a_pass(self):
        with TemporaryDirectory() as tmp:
            bundle = Path(tmp)
            for damage, source in ((dict(summary=b"{"), "summary_metrics.json"), (dict(metadata=b"[]"), "metadata.json")):
                with self.subTest(damage=damage), self.assertRaises(evidence.EvidenceFailure) as caught:
                    self.judge(self.D018, **damage)
                self.assertEqual((caught.exception.reason, caught.exception.source), ("bundle_binding", source))
            from scripts.align_r1_part_c import _check_pinned_trace

            bound = {"summary_metrics.json": b"{}", "metadata.json": b"{}", "power_trace.csv": self.D018}
            _check_pinned_trace(FIRST, bundle, bound)
            for broken in (None, SimpleNamespace(_check_power_trace=lambda *args: 1 / 0),
                           SimpleNamespace(_check_power_trace=lambda *args: None),
                           SimpleNamespace(_check_power_trace=lambda *args: ()),
                           SimpleNamespace(_check_power_trace=lambda *args: ["a problem"])):
                with self.subTest(validator=broken), patch.dict(sys.modules, {"joulewise.bundle_read": broken}), \
                        self.assertRaises(evidence.EvidenceFailure) as caught:
                    _check_pinned_trace(FIRST, bundle, bound)
                self.assertEqual((caught.exception.reason, caught.exception.field, caught.exception.peer),
                                 ("bundle_binding", "D-018", "bundle_read"))

    def test_the_bound_bytes_are_judged_whatever_the_directory_holds(self):
        # The function reads a path. It must read the bytes the manifest binds, not the member's directory.
        self.judge(self.D018, on_disk=b"{")
        self.judge(self.INTERVAL, on_disk=b"timestamp_s,power_w,source\n")
        for bound in (b"{", b"", b"timestamp_s,power_w,source\n"):
            for on_disk in (self.D018, self.INTERVAL, None):
                with self.subTest(bound=bound, on_disk=on_disk):
                    self.refused(bound, on_disk=on_disk)

    def test_the_rail_manifest_rule_after_the_header_is_part_of_the_check(self):
        declared = json.dumps({"device": {"rail_manifest": ["gpu_power"]}}).encode()
        row = b"2001.5,0.002,powermetrics,%s\n"
        self.judge(self.D018 + row % b"gpu_power", metadata=declared)
        self.judge(self.D018 + row % b"gpu_power" + row % b"another_rail", metadata=declared)
        self.refused(self.D018 + row % b"gpu_power" * 2, metadata=declared)      # one rail twice at one stamp
        self.refused(self.INTERVAL + b"2001.5,0.002,powermetrics,gpu_power,2001.0,2002.0\n", metadata=declared)
        self.refused(self.D018, metadata=json.dumps({"device": {"rail_manifest": "gpu_power"}}).encode())

    def test_a_trace_that_was_never_bound_is_not_a_trace(self):
        from scripts.align_r1_part_c import _check_pinned_trace

        with TemporaryDirectory() as tmp:
            (Path(tmp) / "power_trace.csv").write_bytes(self.D018)       # on disk, but never bound
            with self.assertRaises(evidence.EvidenceFailure) as caught:
                _check_pinned_trace(FIRST, Path(tmp), {"summary_metrics.json": b'{"status":"succeeded"}',
                                                       "metadata.json": b"{}"})
        self.assertEqual((caught.exception.reason, caught.exception.field), ("bundle_binding", "D-018"))


class MemberBracketTests(unittest.TestCase):
    """Audit 2 `finalized-after-close`: an event stamped after the member's own terminal close is impossible."""

    @staticmethod
    def events(*stamps):
        return {"events.jsonl": b"".join(json_bytes({
            "timestamp_s": stamp, "event_type": "phase_start", "phase": "run", "message": "", "metadata": {}})
            for stamp in stamps)}

    def judge(self, *stamps, bracket=(2000.0, 3800.0)):
        pc._check_events_inside(FIRST, self.events(*stamps), *bracket)

    def refused(self, *stamps, index):
        with self.assertRaises(evidence.EvidenceFailure) as caught:
            self.judge(*stamps)
        failure = caught.exception
        self.assertEqual((failure.reason, failure.role, failure.source, failure.index, failure.field, failure.peer),
                         ("member_order", FIRST, "events.jsonl", index, "timestamp_s", MANIFEST))

    def test_every_event_lies_inside_the_terminal_bracket(self):
        self.judge(2000.0, 2001.5, 3800.0)
        self.refused(2000.0, 3801.0, index=1)        # the audit's finalization one second after the close
        self.refused(2000.0, 3800.000001, index=1)
        self.refused(1999.999999, 2001.0, index=0)
        for bad in (float("nan"), float("inf"), "2001", None, True):
            with self.subTest(stamp=bad), self.assertRaises(evidence.EvidenceFailure):
                self.judge(2000.5, bad)


class SegmentInventoryTests(unittest.TestCase):
    """Audit 2 `duplicate-predecessor`: a second complete segment beside the issued ones."""

    ALLOWED = set(MEMBERS.values())

    def test_only_the_issued_segments_may_be_directories_of_the_part_c_root(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in self.ALLOWED:
                (root / name).mkdir()
            (root / evidence.LEDGER_NAME).write_bytes(b"")
            pc._check_segment_inventory(root, self.ALLOWED, source=evidence.LEDGER_NAME)
            (root / "smoke.json").write_bytes(b"{}")        # a plain file is not a segment
            pc._check_segment_inventory(root, self.ALLOWED, source=evidence.LEDGER_NAME)
            for extra in ("capture_predecessor_30b.rejected1", "idle_until_soak", "calibration.precool",
                          "X_G_contrast.retry", "any_directory"):
                with self.subTest(extra=extra):
                    (root / extra).mkdir()
                    with self.assertRaises(evidence.EvidenceFailure) as caught:
                        pc._check_segment_inventory(root, self.ALLOWED, source=evidence.LEDGER_NAME)
                    failure = caught.exception
                    self.assertEqual((failure.reason, failure.role, failure.source, failure.field),
                                     ("sequence", "attempt", evidence.LEDGER_NAME, "segments"))
                    self.assertNotIn(extra, json.dumps(failure.finding()))
                    (root / extra).rmdir()
            (root / "capture_predecessor_30b.rejected2").write_bytes(b"")   # a retry's name, even as a file
            with self.assertRaises(evidence.EvidenceFailure):
                pc._check_segment_inventory(root, self.ALLOWED, source=evidence.LEDGER_NAME)
        with self.assertRaises(evidence.EvidenceFailure):
            pc._check_segment_inventory(Path("/nonexistent/part-c"), self.ALLOWED, source=evidence.LEDGER_NAME)

    def test_the_soak_root_holds_one_segment_too(self):
        with TemporaryDirectory() as tmp:
            attempt = SoakAttempt(Path(tmp))
            handoff = attempt.close()
            attempt.binding(handoff)
            for extra in ("idle_soak.rejected1", "idle_soak.precool", "another_directory"):
                with self.subTest(extra=extra):
                    (attempt.directory / extra).mkdir()
                    with self.assertRaises(evidence.EvidenceFailure) as caught:
                        attempt.binding(handoff)
                    self.assertEqual((caught.exception.reason, caught.exception.role, caught.exception.field),
                                     ("sequence", "idle", "segments"))
                    (attempt.directory / extra).rmdir()
            attempt.binding(handoff)


class GateRowOrderTests(unittest.TestCase):
    """Audit 2 `gate-before-entry`: the frozen _wait takes its stamp, then writes the row that contains it."""

    START, END = 10 * 10**9, 20 * 10**9

    @staticmethod
    def paired(ns):
        return {"epoch_ns": ns, "monotonic_before_ns": ns, "monotonic_after_ns": ns, "wall_resolution_ns": 1,
                "monotonic_resolution_ns": 1}

    def fixture(self, begin_at, end_at):
        interval = {"kind": "G0", "turn": 0, "token_count": None, "outcome": "released", "start_ns": self.START,
                    "end_ns": self.END, "duration_s": 10.0, "clock": "episode_monotonic_ns", "entry_sensors": {},
                    "reference": {"fast_c": 35.0, "slow_c": 35.0}, "release": {"fast_c": 35.0, "slow_c": 35.0},
                    "slope_c_per_min": 0.0, "entry_slope_c_per_min": 0.0, "exit_sample_ns": self.END - 1,
                    "entry_stamp": self.paired(self.START), "exit_stamp": self.paired(self.END),
                    "entry_epoch_s": 10.0, "exit_epoch_s": 20.0}
        journal = [{"kind": "align_thermal_gate", "started": {"monotonic_ns": begin_at},
                    "values": {"state": "begin", "gate_kind": "G0", "turn": 0, "token_count": None,
                               "entry_stamp": interval["entry_stamp"]}},
                   {"kind": "align_thermal_gate", "started": {"monotonic_ns": end_at},
                    "values": {"state": "end", "gate": interval}}]
        events = [{"phase": "align_thermal_gate", "event_type": kind, "message": "G0", "timestamp_s": seconds,
                   "metadata": interval} for kind, seconds in (("phase_start", 10.0), ("phase_end", 20.0))]
        return [interval], journal, events

    def judge(self, begin_at, end_at):
        sampler = ModuleType("joulewise.align.apple.sampler")
        sampler.seconds_ns = lambda seconds: round(seconds * 10**9)
        apple = ModuleType("joulewise.align.apple")
        apple.sampler = sampler
        align = ModuleType("joulewise.align")
        align.apple = apple
        with patch.dict(sys.modules, {m.__name__: m for m in (align, apple, sampler)}):
            pc._check_gate_boundaries(*self.fixture(begin_at, end_at), "d-bank-benign-s1")

    def refused(self, begin_at, end_at, field):
        with self.assertRaises(evidence.EvidenceFailure) as caught:
            self.judge(begin_at, end_at)
        failure = caught.exception
        self.assertEqual((failure.reason, failure.field, failure.source), ("gate_journal_disagreement", field,
                                                                           pc.THERMAL_SOURCE))

    def test_a_row_is_written_at_or_after_the_stamp_it_contains(self):
        self.judge(self.START, self.END)
        self.judge(self.START + 1, self.END + 5)
        self.refused(self.START - 1_000_000, self.END, "entry_stamp")     # the audit's one millisecond early
        self.refused(self.START - 1, self.END, "entry_stamp")
        self.refused(self.START, self.END - 1, "exit_stamp")
        self.refused(self.START, 0, "exit_stamp")


class PlannedRunIdTests(unittest.TestCase):
    """Audit 2 `other-run-id`: the run id is the one the frozen dispatch issues, never the bundle's own."""

    @contextmanager
    def dispatch_double(self, body):
        runtime = ModuleType("joulewise.align.apple.r1_runtime")

        class Segment:
            def dispatch(self):
                body(self)

        runtime.Segment = Segment
        apple = ModuleType("joulewise.align.apple")
        apple.r1_runtime = runtime
        align = ModuleType("joulewise.align")
        align.apple = apple
        with patch.dict(sys.modules, {m.__name__: m for m in (align, apple, runtime)}):
            yield

    def test_the_id_is_taken_from_the_dispatch_for_each_member(self):
        seen = []

        def body(segment):
            seen.append((segment.kind, segment.config))
            segment.run_member({"run_id": f"align-v4-r1-{segment.kind}"})

        with self.dispatch_double(body):
            for kind in MEMBERS:
                self.assertEqual(pc.planned_run_id(kind, {"issued": True}), f"align-v4-r1-{kind}")
        self.assertEqual(seen, [(kind, {"issued": True}) for kind in MEMBERS])

    def test_a_dispatch_that_issues_no_id_is_an_error_never_a_default(self):
        with self.dispatch_double(lambda segment: None), self.assertRaises(ValueError):
            pc.planned_run_id("x-g", {})
        with self.dispatch_double(lambda segment: 1 / 0), self.assertRaises(ZeroDivisionError):
            pc.planned_run_id("x-g", {})


class FrozenDifferentialNamedCasesTests(unittest.TestCase):
    """The frozen differential suite's audit-named cases, run from this checkout against its own evaluator.

    The suite materializes the issued R1 sources from Git, so it needs the two pinned commits in the local
    object database. A shallow checkout lacks them and this test skips. The full 25,083-case matrix is run by
    hand. These cases are the regressions of audits 1 and 2 that need the frozen workload, driver and D-018
    validator: the five named audit reproductions, the eight predecessor CSV cases, the orphan tokenize event,
    the empty final phase, and the turn-flag classes the frozen workload decides. The eight CSV cases are the
    seven RL-193 section 1 confirmed and its supplement, the six-column header with zero rows, which passes.
    """

    SUITE = Path(__file__).resolve().parent / "align" / "test_partc_frozen_differential.py"
    SELECTOR = (r"audit-|predecessor-30b/v3/raw/runs/[^/]+/power_trace\.csv/file/|orphan-tokenize|empty-final-phase"
                r"|runner\.error|0\.flags/set-turn_budget_reached")
    PINS = ("b2e01464d6d4fbf2901ff4d4154df9455104a12a", "2d02a6f0e42b7ac7a51ea5d5830867eea9ff2911")

    def test_named_audit_cases_have_no_false_pass_and_the_clean_control_passes(self):
        import os
        import subprocess

        root = Path(__file__).resolve().parents[1]
        if not self.SUITE.is_file() or any(
                subprocess.run(["git", "-C", str(root), "cat-file", "-e", pin + "^{commit}"],
                               capture_output=True).returncode for pin in self.PINS):
            self.skipTest("the pinned R1 commits are not in this object database")
        env = {**os.environ, "JW_PARTC_CASE": self.SELECTOR, "JW_PARTC_WORKERS": "1", "JW_PARTC_REPO": str(root),
               "PYTHONDONTWRITEBYTECODE": "1"}
        with TemporaryDirectory() as tmp:
            proc = subprocess.run([sys.executable, "-IB", str(self.SUITE)], cwd=tmp, env={**env, "TMPDIR": tmp},
                                  capture_output=True, text=True)
        output = proc.stdout + proc.stderr
        self.assertEqual(proc.returncode, 0, output[-3000:])
        self.assertIn("descriptor rows PASS (4/4)", output)
        self.assertNotRegex(output, r"(?m)^(FALSE_PASS|WRONG_VERDICT|HARNESS_ERROR)")

    PROBE = Path(__file__).resolve().parent / "align" / "partc_audit_probe.py"
    EXPECTED = {"control": "pass -", "interval-header-zero-rows": "pass -",
                "raw-runner-fault": "other_failure workload_replay",
                "raw-turn-budget-flag": "other_failure workload_replay",
                "last-turn-unclosed": "other_failure workload_replay",
                "other-run-id": "other_failure execution_config", "duplicate-predecessor": "other_failure sequence",
                "predecessor-timeout": "other_failure gate_cardinality",
                "extra-stop-flag": "other_failure flag_source",
                "gate-before-entry": "other_failure gate_journal_disagreement",
                "finalized-after-close": "other_failure member_order"}

    def test_audit_two_reproductions_are_each_refused_for_their_own_reason(self):
        """Audit 2's nine damaged attempts through the synthetic launcher, and the two positives that pass.

        The positives are the clean control and RL-193 section 1's supplement: a predecessor trace that is the
        six-column D-018 interval header with zero rows.
        """
        import os
        import subprocess

        root = Path(__file__).resolve().parents[1]
        if not self.PROBE.is_file() or any(
                subprocess.run(["git", "-C", str(root), "cat-file", "-e", pin + "^{commit}"],
                               capture_output=True).returncode for pin in self.PINS):
            self.skipTest("the pinned R1 commits are not in this object database")
        with TemporaryDirectory() as tmp:
            proc = subprocess.run([sys.executable, "-IB", str(self.PROBE)], cwd=tmp, capture_output=True, text=True,
                                  env={**os.environ, "JW_PARTC_REPO": str(root), "TMPDIR": tmp,
                                       "PYTHONDONTWRITEBYTECODE": "1"})
        output = proc.stdout + proc.stderr
        seen = {line.split()[1]: " ".join(line.split()[2:]) for line in proc.stdout.splitlines()
                if line.startswith("RESULT ")}
        self.assertEqual(seen, self.EXPECTED, output[-3000:])
        self.assertEqual(proc.returncode, 0, output[-3000:])
