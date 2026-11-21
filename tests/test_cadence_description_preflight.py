"""Exercise native-look dependency admission with invented ledger and source bytes."""

import csv
from decimal import Decimal
from itertools import product
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import description as reader
from joulewise.cadence_looks import description_worker
from joulewise.cadence_looks.custody_pins import PinRefusal, offload_manifest_bytes_sha256
from tests import test_desc_looks_acceptance as fixture
from tests.fixtures.description_worlds import DescriptionWorld


def setUpModule():
    # These tests exercise admission gates beyond the pre-integration host check.
    # Keep the frozen suite's independent hardware observations in its own tests.
    unittest.enterModuleContext(patch.object(socket, "gethostname", return_value=fixture.FIXTURE_BOARD))
    unittest.enterModuleContext(patch.dict(os.environ, R190_NODENAME=fixture.FIXTURE_BOARD))


def _native_path(name):
    if name.startswith("kits/"):
        return f"{reader.CAMPAIGN}/{name}"
    if name.startswith("manifests/"):
        return f"{reader.CAMPAIGN}/looks/{Path(name).stem}.manifest.json"
    return name


class NativeStep3PreflightTests(unittest.TestCase):
    def setUp(self):
        temporary = self.enterContext(TemporaryDirectory())
        self.root = Path(temporary).resolve()
        self.look = fixture.IDS[0]
        self.world = DescriptionWorld(self.root / "projection", self.look)
        self.book = fixture.Book(self.root / "native-book")
        self.ledger = self.book.path / reader.CONTROL / "LOOKS.json"
        self.stage_name = f"{reader.CONTROL}/stage1/{self.look}.json"
        public = self.root / "native-public"
        (public / self.look).mkdir(parents=True)

        # Reproduce the audit's native ledger with the same registration,
        # receipt and prerequisite order as the invented projection.
        for commit in (self.world.reg, self.world.receipts):
            self._copy_snapshot(commit)
            if commit == self.world.reg:
                registration = self.book.seal("native registration")
            else:
                receipts = self.book.seal("native receipts")
        self._copy_snapshot(self.world.book.head)
        for name in ("authority/copy.json", "roster.json"):
            path = self.book.path / name
            fixture.put(path, dict(fixture.read(path), receipt_commit=receipts))
        hashes = {_native_path(name): fixture.sha((self.book.path / _native_path(name)).read_bytes())
                  for name in self.world.row["input_hashes"]}
        self.row = dict(self.world.row, manifest_path=_native_path(f"manifests/{self.look}.json"),
                        public_root=str(public), registration_commit=registration, input_hashes=hashes)
        self._bind_ledger("native prerequisites")

        self.loader = self.root / "step3.py"
        self.source = b"reader_identity = 'invented pin'\n"
        self.enterContext(patch.multiple(reader, STEP3_PATH=str(self.loader),
                                         STEP3_SHA256=fixture.sha(self.source)))
        fallback_ref = f"{reader.STEP3_COMMIT}:{self.loader}"
        self.fallback_calls = []
        check_output = subprocess.check_output

        def with_fixture_git_object(argv, *args, **kwargs):
            if argv[-2:] == ["show", fallback_ref]:
                self.fallback_calls.append(fallback_ref)
                return self.source
            return check_output(argv, *args, **kwargs)

        self.enterContext(patch.object(reader.subprocess, "check_output",
                                        side_effect=with_fixture_git_object))

    def _copy_snapshot(self, commit):
        paths = subprocess.check_output(
            ["git", "-C", str(self.world.repo), "ls-tree", "-rz", "--name-only", commit],
        ).split(b"\0")
        for path in paths:
            name = path.decode()
            if name and name != "LOOKS.json":
                fixture.put(self.book.path / _native_path(name), (self.world.repo / name).read_bytes())

    def _bind_ledger(self, label):
        fixture.put(self.ledger, {"schema": reader.LEDGER_SCHEMA, "looks": [self.row]})
        self.book.seal(label)

    def test_native_admission_refuses_missing_reader_even_when_git_object_exists(self):
        with self.assertRaises(FileNotFoundError) as failure:
            reader.Snapshot(self.book.path, self.look, "stage1")
        self.assertEqual(Path(failure.exception.filename), self.loader)
        self.assertEqual(self.fallback_calls, [])
        self.assertFalse((self.book.path / self.stage_name).exists())

        # The same immutable fallback is usable for normalized development.
        self.assertEqual(reader.step3_reader().reader_identity, "invented pin")
        self.assertEqual(len(self.fallback_calls), 1)

    def test_native_refuses_changed_and_symlinked_reader(self):
        with self.subTest(kind="byte drift"):
            self.loader.write_bytes(self.source + b"\n")
            with self.assertRaisesRegex(reader.Refusal, "different bytes"):
                reader.Snapshot(self.book.path, self.look, "stage1")
        self.loader.unlink()
        original = self.root / "verified-bytes.py"
        original.write_bytes(self.source)
        with self.subTest(kind="symlink"):
            self.loader.symlink_to(original)
            with self.assertRaisesRegex(reader.Refusal, "unexpected path type"):
                reader.Snapshot(self.book.path, self.look, "stage1")
        self.assertEqual(self.fallback_calls, [])

    def test_scoring_uses_step3_verified_before_reservation(self):
        self.loader.write_bytes(self.source)
        stage1 = reader.Snapshot(self.book.path, self.look, "stage1")
        census, _ = reader.census(stage1)
        stage_bytes = reader.canonical(census)
        fixture.put(self.book.path / self.stage_name, stage_bytes)
        artifact = self.book.seal("native stage-1 artifact")
        self.row.update(status="stage1_committed", stage1_commit=artifact, stage1_path=self.stage_name,
                        stage1_sha256=fixture.sha(stage_bytes))
        self._bind_ledger("native stage 1 committed")

        stage2 = reader.Snapshot(self.book.path, self.look, "stage2")
        census, qualified = reader.census(stage2)
        paths = reader.verify_gates(stage2, qualified)
        stage2.check_stage1(census)
        self.loader.unlink()

        def describe(signal, _detail, _instrument):
            return {"hold": signal.pinned.reader_identity}

        with patch.object(reader, "_leg_values", side_effect=describe):
            result = reader.score(stage2, paths, qualified, lambda: self.fail("scoring input opened"))
        self.assertEqual(len(qualified), 3)
        self.assertEqual(result["hold"], dict.fromkeys(qualified, "invented pin"))
        self.assertEqual(self.fallback_calls, [])


class LoadedLegAdmissionTests(unittest.TestCase):
    def test_loaded_leg_is_accounted_for_and_never_read_or_printed(self):
        class LoadedFirstMember(DescriptionWorld):
            loaded_keys = {"f2-inst-01/L001", "f2-stab-01/L001"}

        for look in fixture.IDS:
            with self.subTest(look=look), TemporaryDirectory() as temporary:
                root = Path(temporary).resolve()
                instrument = look == fixture.IDS[0]
                world = LoadedFirstMember(root / "world", look, None if instrument else "same_work")
                key = "f2-inst-01/L001" if instrument else "f2-stab-01/L001"
                eligible = set(world.good)
                rc, stdout, stderr, events = fixture.invoke(world, "stage1")
                self.assertEqual((rc, stdout, stderr), (0, b"", b""))
                self.assertFalse([event for event, _ in events if event == "open"])
                document = fixture.read(world.stage)
                position = document["positions"][key]
                self.assertIs(position["loaded_flag"], True)
                self.assertEqual(position["disposition"], "not_qualified:loaded")
                self.assertEqual(position["reasons"], ["loaded"])
                refs = next(row for row in world.rows if row["key"] == key)
                self.assertEqual(position["receipt"], refs["receipt"])
                self.assertEqual(document["counts"]["n_legs"], len(eligible))
                summary = document["by_kit"][key.split("/")[0]]
                self.assertEqual(summary["reasons"]["not_qualified"]["loaded"], 1)
                if not instrument:
                    token = next(row for row in document["token_table"]
                                 if f'{row["kit_id"]}/{row["leg_id"]}' == key)
                    original = world.records[key][0]
                    self.assertEqual(token["realised_prefill_tokens"], original["prefill_tokens"])
                    self.assertEqual(token["realised_decode_tokens"], original["decode_tokens"])
                    self.assertEqual(token["missing_count_reason"], "loaded")
                    self.assertIs(token["loaded_flag"], True)
                    self.assertEqual(document["paper_wording"], "the same cell of work")
                    self.assertEqual(document["counts"]["n_local_dates"], 14)

                world.bind()
                snapshot = reader.Snapshot(world.repo, look, "stage2")
                census, qualified = reader.census(snapshot)
                snapshot.check_stage1(census)
                self.assertEqual(snapshot.public_record(census)["n_legs"], len(eligible))
                sources = reader.verify_gates(snapshot, qualified)
                self.assertEqual(set(sources), eligible)
                opened = []
                open_path = Path.open

                def watch(path, *args, **kwargs):
                    if path.is_relative_to(world.copy):
                        opened.append(path)
                    return open_path(path, *args, **kwargs)

                with patch.object(Path, "open", watch):
                    prints = reader.score(snapshot, sources, qualified, lambda: None)
                prints = world.full_roster_prints(prints)
                self.assertTrue(opened)
                self.assertFalse(any(path.is_relative_to(world.copy / key) for path in opened))
                for name in ("hold", "turn", "gain", "edges") if instrument else ("hold", "turn"):
                    self.assertEqual(set(prints[name]), eligible)
                if not instrument:
                    self.assertTrue(all(key not in cell for cell in prints["context"].values()))

    def test_loaded_leg_does_not_supply_the_fourteenth_date(self):
        class LoadedLastDate(DescriptionWorld):
            loaded_keys = {"f2-stab-13/L002"}

        with TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            first = LoadedLastDate(root / "first", fixture.IDS[1])
            fixture.Checks().refused(first, "stage1")
            self.assertFalse(first.stage.exists())
            last = LoadedLastDate(root / "last", fixture.IDS[2])
            rc, stdout, stderr, _ = fixture.invoke(last, "stage1")
            self.assertEqual((rc, stdout, stderr), (0, b"", b""))
            counts = fixture.read(last.stage)["counts"]
            self.assertEqual(counts, {"n_legs": len(last.good), "n_local_dates": 13})


class Stage1ReasonOrderTests(unittest.TestCase):
    def test_every_subset_of_operational_failures_keeps_the_lifecycle_order(self):
        qualified = {
            "leg_status": "complete", "g0_outcome": "released", "loaded_flag": False,
            "quiet_spans_ns": [[0, 600_000_000_000]], "decode_tokens": 512, "decode_cap_reached": True,
        }
        failures = (
            ("incomplete", "leg_status", "incomplete"),
            ("wrong_mode", "power_mode", "High Power"),
            ("unreleased", "g0_outcome", "timeout"),
            ("short_hold", "quiet_spans_ns", [[0, 599_999_999_999]]),
            ("loaded", "loaded_flag", True),
            ("short", "decode_tokens", 511),
            ("cap_not_reached", "decode_cap_reached", False),
        )
        for selected in product((False, True), repeat=len(failures)):
            failed = [(reason, field, value) for (reason, field, value), enabled in zip(failures, selected)
                      if enabled]
            expected = [reason for reason, _, _ in failed]
            with self.subTest(reasons=expected):
                op = qualified.copy()
                op.update((field, value) for _, field, value in failed)
                receipt = {"power_mode": op.pop("power_mode", "Automatic")}
                self.assertEqual(reader._eligibility_reasons(op, receipt, 512), expected)

    def test_census_binds_first_reason_and_all_failures_before_scoring(self):
        class FailedMember(DescriptionWorld):
            loaded_keys = {"f2-inst-01/L001", "f2-stab-01/L001"}

            def leg(self, kit, pos, v, day, ordinal, status):
                refs = super().leg(kit, pos, v, day, ordinal, status)
                if refs["key"] in self.loaded_keys:
                    op, receipt, _, _ = self.records[refs["key"]]
                    op.update(leg_status="incomplete", g0_outcome="timeout",
                              quiet_spans_ns=[], decode_tokens=0, decode_cap_reached=False)
                    receipt["power_mode"] = "High Power"
                    fixture.put(self.repo / refs["leg_record"], op)
                    fixture.put(self.repo / refs["receipt"], receipt)
                return refs

        for look in fixture.IDS:
            with self.subTest(look=look), TemporaryDirectory() as directory:
                world = FailedMember(Path(directory).resolve() / "world", look)
                key = f"f2-{world.family}-01/L001"
                rc, stdout, stderr, events = fixture.invoke(world, "stage1")
                self.assertEqual((rc, stdout, stderr), (0, b"", b""))
                self.assertFalse([path for event, path in events if event == "open"])
                document = fixture.read(world.stage)
                row = document["positions"][key]
                self.assertEqual(row["disposition"], "not_qualified:incomplete")
                self.assertEqual(row["reasons"], ["incomplete", "wrong_mode", "unreleased",
                                                  "short_hold", "loaded", "short", "cap_not_reached"])
                self.assertTrue(row["loaded_flag"])
                admitted_key = next(iter(world.good))
                self.assertEqual(document["positions"][admitted_key]["reasons"], [])
                self.assertEqual(document["counts"]["n_legs"], len(world.good))
                if not world.inst:
                    token = next(row for row in document["token_table"]
                                 if f'{row["kit_id"]}/{row["leg_id"]}' == key)
                    self.assertEqual(token["disposition"], "not_qualified:incomplete")
                    self.assertEqual(token["missing_count_reason"], "short")
                world.bind()

                snapshot = reader.Snapshot(world.repo, look, "stage2")
                census, qualified = reader.census(snapshot)
                snapshot.check_stage1(census)
                self.assertEqual(set(qualified), set(world.good))
                self.assertNotIn(key, reader.verify_gates(snapshot, qualified))


class Stage1OperationalEvidenceTests(unittest.TestCase):
    def test_canonical_empty_span_close_admits_drop_and_rejects_concealed_member(self):
        class ClosedSpan(DescriptionWorld):
            def project_drops(self):
                super().project_drops()
                row = next(row for row in self.rows if "drop" in row)
                key = row["key"]
                kit, leg_id = key.split("/")
                self.dropped_key = key
                path = "ops/invented-empty-span/runner_receipt.json"
                witness = {
                    "span_id": "invented-empty-span", "kit_id": kit, "closed": True, "member_legs": [],
                    "kit_sha256": fixture.sha((self.repo / "kits" / f"{kit}.json").read_bytes()),
                    "unrun": [key],
                }
                fixture.put(self.repo / path, witness)
                declaration = fixture.read(self.repo / row["drop"])
                queue = declaration.pop("queue")
                declaration.update(reason="ended_without_member", receipt=path)
                fixture.put(self.repo / row["drop"], declaration)
                run_state = self.repo / "RUN_STATE.md"
                before = f"The lead declares {key} dropped:queue_retired. No member exists or will exist. "
                before += f"Evidence {queue} sha256={fixture.sha((self.repo / queue).read_bytes())}."
                after = f"The lead declares {key} dropped:ended_without_member. No member exists or will exist. "
                after += f"Evidence {path} sha256={fixture.sha(fixture.wire(witness))}."
                fixture.put(run_state, run_state.read_bytes().replace(before.encode(), after.encode(), 1))
                if self.concealed:
                    fixture.put(self.repo / "ops/invented-empty-span/legs" / leg_id / "leg_record.json",
                                {"leg_id": leg_id})

        for concealed in (False, True):
            with self.subTest(concealed=concealed), TemporaryDirectory() as directory:
                ClosedSpan.concealed = concealed
                world = ClosedSpan(Path(directory).resolve() / "world", fixture.IDS[0])
                if concealed:
                    fixture.Checks().refused(world, "stage1")
                else:
                    world.commit_stage1(self)
                    row = fixture.read(world.stage)["positions"][world.dropped_key]
                    self.assertEqual(row["disposition"], "dropped:ended_without_member")

    def test_wall_budget_uses_exact_equality_and_requires_all_evidence(self):
        kit = {"span_template": {"leg_budget_s": 600}}
        for wall, over in ((Decimal("599.999999999"), False), (600, False),
                           (Decimal("600.000000001"), True)):
            with self.subTest(wall=wall):
                record = {"wall_s": wall, "leg_budget_s": 600, "over_time_budget": over}
                self.assertEqual(reader._time_budget(record, kit), {"over_time_budget": over})
        record = {"wall_s": 600, "leg_budget_s": 600, "over_time_budget": False}
        for field in record:
            with self.subTest(missing=field), self.assertRaises(reader.Refusal):
                reader._time_budget({key: value for key, value in record.items() if key != field}, kit)
        for fields in ({"wall_s": True}, {"wall_s": Decimal("NaN")}, {"wall_s": -1},
                       {"leg_budget_s": 601}, {"leg_budget_s": Decimal(600)},
                       {"over_time_budget": 0}, {"over_time_budget": True}):
            with self.subTest(invalid=fields), self.assertRaises(reader.Refusal):
                reader._time_budget(dict(record, **fields), kit)

    def test_signed_member_without_wall_evidence_refuses_stage1(self):
        class MissingEvidence(DescriptionWorld):
            def leg(self, kit, pos, v, day, ordinal, status):
                refs = super().leg(kit, pos, v, day, ordinal, status)
                if ordinal == 0:
                    op = self.records[refs["key"]][0]
                    op.pop("over_time_budget")
                    fixture.put(self.repo / refs["leg_record"], op)
                return refs

        for look in fixture.IDS:
            with self.subTest(look=look), TemporaryDirectory() as directory:
                world = MissingEvidence(Path(directory).resolve() / "world", look)
                fixture.Checks().refused(world, "stage1")
                self.assertFalse(world.stage.exists())

    def test_typed_drop_requires_an_active_visible_lead_claim_of_exact_witness(self):
        class ChangedProof(DescriptionWorld):
            def project_drops(self):
                super().project_drops()
                path = self.repo / "RUN_STATE.md"
                text = path.read_text()
                if self.defect == "witness":
                    queue = self.repo / "ops/drop-evidence/retired-queue.json"
                    fixture.put(queue, dict(fixture.read(queue), queue_id="different-invented-queue"))
                elif self.defect == "owner":
                    fixture.put(path, text.replace('"owner": "lead"', '"owner": "ed"').encode())
                elif self.defect == "unissued":
                    fixture.put(path, text.replace('"status": "ISSUED"', '"status": "DRAFT"').encode())
                elif self.defect == "fenced":
                    text = text.replace("The lead declares", "~~~\nThe lead declares", 1)
                    text = text.replace("\n\n<!-- RUN_STATE LEGACY", "\n~~~\n\n<!-- RUN_STATE LEGACY")
                    fixture.put(path, text.encode())

        for defect in ("witness", "owner", "unissued", "fenced"):
            with self.subTest(defect=defect), TemporaryDirectory() as directory:
                ChangedProof.defect = defect
                world = ChangedProof(Path(directory).resolve() / "world", fixture.IDS[0])
                fixture.Checks().refused(world, "stage1")
                self.assertFalse(world.stage.exists())


class EarlyDataLockTests(unittest.TestCase):
    def test_early_lock_refuses_the_narrower_look(self):
        with TemporaryDirectory() as directory:
            world = DescriptionWorld(Path(directory).resolve() / "world", fixture.IDS[1], "lock_first")
            self.assertEqual(len(world.qualified_dates()), 1)
            fixture.Checks().refused(world, "stage1")
            self.assertFalse(world.stage.exists())

    def test_early_lock_admits_the_full_later_look_even_below_the_date_gate(self):
        class EarlyLock(DescriptionWorld):
            def named(self, name, rel, doc):
                if name == "event":
                    doc.update(previous_read=None, previous_status=None, coalesced=[fixture.IDS[1]])
                super().named(name, rel, doc)

            def save_row(self):
                for row in self.events_ledger:
                    if row.get("look_id") == fixture.IDS[1]:
                        row["status"] = "coalesced"
                super().save_row()

        for change, dates in (("thirteen", 13), ("all_terminal", 0)):
            with self.subTest(dates=dates), TemporaryDirectory() as directory:
                world = EarlyLock(Path(directory).resolve() / "world", fixture.IDS[2], change)
                rc, out, err, events = fixture.invoke(world, "stage1")
                self.assertEqual((rc, out, err), (0, b"", b""))
                self.assertFalse([path for event, path in events if event == "open"])
                self.assertEqual(fixture.reservation_boundary(self, world), [])
                world.bind()
                self.assertEqual(fixture.reservation_boundary(self, world), [str(world.private)])
                snapshot = reader.Snapshot(world.repo, world.look, "stage2")
                census, qualified = reader.census(snapshot)
                snapshot.check_stage1(census)
                self.assertEqual(census["counts"]["n_local_dates"], dates)
                self.assertEqual(set(qualified), set(world.good))
                self.assertEqual(set(reader.verify_gates(snapshot, qualified)), set(world.good))
                if dates:
                    self.assertIn("f2-stab-15/L001", qualified)

    def test_one_date_early_lock_binds_both_views_before_reservation(self):
        look = fixture.IDS[2]
        roster = fixture.layout(look)
        one_day = [(kit, pos, value, 0) for kit, pos, value, _ in (*roster[:3], roster[-1])]
        with TemporaryDirectory() as directory:
            with patch.object(fixture, "layout", return_value=one_day):
                world = fixture.EarlyLockWorld(Path(directory).resolve() / "world", look)
            rc, out, err, events = fixture.invoke(world, "stage1")
            self.assertEqual((rc, out, err), (0, b"", b""))
            self.assertFalse(any(kind == "open" for kind, _ in events))
            self.assertEqual(fixture.reservation_boundary(self, world), [])
            world.bind()
            self.assertEqual(fixture.reservation_boundary(self, world), [str(world.private)])

            snapshot = reader.Snapshot(world.repo, look, "stage2")
            census, qualified = reader.census(snapshot)
            snapshot.check_stage1(census)
            self.assertEqual(census["counts"], {"n_legs": 3, "n_local_dates": 1})
            sources = reader.verify_gates(snapshot, qualified)
            tables = reader.score(snapshot, sources, qualified, lambda: None)
            for view, legs in (("all", 3), ("base14", 2)):
                with self.subTest(view=view):
                    count = census["by_kit_set"][view]
                    self.assertEqual((count["n_legs"], count["n_local_dates"]), (legs, 1))
                    self.assertEqual(len(tables["hold"][view]), legs)
                    cells = [cell for cell in tables["date_spreads"][view].values() if cell["dates"]]
                    self.assertTrue(cells)
                    for cell in cells:
                        self.assertEqual(len(cell["dates"]), 1)
                        self.assertEqual(cell["sd_date_means"], fixture.null("fewer_than_two"))


class LaterStabilityPopulationTests(unittest.TestCase):
    def _score(self, world):
        world.commit_stage1(self)
        snapshot = reader.Snapshot(world.repo, world.look, "stage2")
        census, qualified = reader.census(snapshot)
        snapshot.check_stage1(census)
        self.assertEqual(snapshot.public_record(census), world.public_truth())
        sources = reader.verify_gates(snapshot, qualified)
        read_started = []
        opened = []
        open_path = Path.open

        def observe(path, *args, **kwargs):
            if path.is_relative_to(world.copy):
                opened.append(path)
            return open_path(path, *args, **kwargs)

        with patch.object(Path, "open", observe), patch.object(reader, "_leg_values", wraps=reader._leg_values) as leg:
            prints = reader.score(snapshot, sources, qualified, lambda: read_started.append(True))
        self.assertEqual(leg.call_count, len(qualified))
        self.assertEqual({path.parent.relative_to(world.copy).as_posix() for path in opened}, set(qualified))
        self.assertEqual(bool(read_started), bool(qualified))
        if qualified:
            full = world.full_roster_prints(prints)
            for name in ("hold", "turn"):
                self.assertEqual({key: row["runner_pin"] for key, row in full[name].items()},
                                 {key: world.records[key][1]["runner_pin"] for key in qualified})
            for cell in full["context"].values():
                for key, row in cell.items():
                    self.assertEqual(row["runner_pin"], world.records[key][1]["runner_pin"])
        return census, prints

    def test_committed_index_can_follow_the_later_receipt_and_binds_pin_counts(self):
        with TemporaryDirectory() as directory:
            world = DescriptionWorld(Path(directory).resolve() / "world", fixture.IDS[2], "late_index")
            index_path = "f2-stab/KITS.json"
            book = reader.Book(world.repo)
            self.assertNotIn(index_path, book.tree(world.receipts))
            world.commit_stage1(self)
            census = fixture.read(world.stage)
            index = fixture.read(world.repo / index_path)
            self.assertEqual(census["source_snapshot"]["kit_index_sha256"],
                             fixture.sha((world.repo / index_path).read_bytes()))
            self.assertEqual((world.repo / index_path).read_bytes(), fixture.committed_index())
            self.assertEqual({row["kit_id"] for row in index["rows"]}, {f"f2-stab-{i:02}" for i in range(1, 17)})
            base_rows = [row for row in index["rows"] if row["kit_id"] in index["base_kits"]]
            expected = {}
            for name, included in (("all", index["rows"]), ("base14", base_rows)):
                by_pin = {fixture.read(world.repo / row["path"])["frozen"]["commit"]: [] for row in included}
                kit_ids = {row["kit_id"] for row in included}
                dates = set()
                for key in world.good:
                    if key.split("/")[0] in kit_ids:
                        receipt = world.records[key][1]
                        date = fixture.datetime.fromtimestamp(receipt["t0_epoch_s"], fixture.LA).date()
                        by_pin[receipt["runner_pin"]].append(date)
                        dates.add(date)
                expected[name] = {"n_legs": sum(map(len, by_pin.values())), "n_local_dates": len(dates),
                                  "by_runner_pin": {pin: {"n_legs": len(days), "n_local_dates": len(set(days))}
                                                    for pin, days in by_pin.items()}}
            self.assertEqual(census["by_kit_set"], expected)
            for row in census["token_table"]:
                key = f'{row["kit_id"]}/{row["leg_id"]}'
                self.assertEqual(row["runner_pin"], world.records[key][1]["runner_pin"])
                self.assertEqual(census["positions"][key]["runner_pin"], row["runner_pin"])

    def test_later_index_refuses_missing_rows_and_mismatched_receipts(self):
        class BadIndex(DescriptionWorld):
            def named(self, name, rel, doc):
                if name == "kit_index":
                    index = json.loads(doc)
                    missing = {"base": "f2-stab-14", "unindexed": "f2-stab-15",
                               "hidden": "f2-stab-15"}.get(self.defect)
                    index["rows"] = [row for row in index["rows"] if row["kit_id"] != missing]
                    if self.defect == "duplicate":
                        index["rows"].append(index["rows"][0].copy())
                    if self.defect == "schema":
                        index["schema"] += ".unknown"
                    if self.defect == "base_kits":
                        index["base_kits"][-1] = "f2-stab-15"
                    if self.defect == "index_pin":
                        index["rows"][0]["runner_pin"] = "6e9d42f1d"
                    if self.defect == "path":
                        index["rows"][0]["path"] = "kits/f2-stab-01.json"
                    doc = fixture.wire(index)
                if name == "roster" and self.defect == "hidden":
                    doc = dict(doc, rows=[row for row in doc["rows"] if not row["key"].startswith("f2-stab-15/")])
                super().named(name, rel, doc)

            def leg(self, kit, pos, v, day, ordinal, status):
                refs = super().leg(kit, pos, v, day, ordinal, status)
                if kit == 15 and self.defect in ("digest", "pin"):
                    receipt = self.records[refs["key"]][1]
                    field, changed = {"digest": ("kit_sha256", "7" * 64),
                                      "pin": ("runner_pin", "7" * 40)}[self.defect]
                    receipt[field] = changed
                    fixture.put(self.repo / refs["receipt"], receipt)
                    issue = fixture.read(self.repo / refs["issue"])
                    fixture.put(self.repo / refs["issue"], dict(issue, **{field: changed}))
                return refs

        for defect in ("base", "unindexed", "hidden", "digest", "pin",
                       "duplicate", "schema", "base_kits", "index_pin", "path"):
            with self.subTest(defect=defect), TemporaryDirectory() as directory:
                BadIndex.defect = defect
                world = BadIndex(Path(directory).resolve() / "world", fixture.IDS[2], "late_index")
                fixture.Checks().refused(world, "stage1")
                self.assertFalse(world.stage.exists())

    def test_base14_matches_first_look_and_ignores_a_later_value_perturbation(self):
        later_key = "f2-stab-15/L001"
        with TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            _, first = self._score(DescriptionWorld(root / "first", fixture.IDS[1]))
            _, second = self._score(DescriptionWorld(root / "second", fixture.IDS[2]))
            changed = DescriptionWorld(root / "changed", fixture.IDS[2])
            v, ordinal = changed.good[later_key]
            fixture.traces(changed.copy / later_key, v, ordinal, delta=1.005)
            fixture.copy_attestation(changed)
            _, perturbed = self._score(changed)
            for name in first:
                self.assertEqual(set(second[name]), {"all", "base14"})
                self.assertEqual(second[name]["base14"], first[name])
                self.assertEqual(perturbed[name]["base14"], first[name])
                self.assertNotEqual(perturbed[name]["all"], second[name]["all"])
            for name in ("hold", "turn"):
                self.assertEqual({k for k, row in second[name]["all"].items() if row != perturbed[name]["all"][k]},
                                 {later_key})
            for cell, rows in second["context"]["all"].items():
                updated = perturbed["context"]["all"][cell]
                self.assertEqual({key for key, row in rows.items() if row != updated[key]},
                                 {later_key} if later_key in rows else set())
                if later_key not in rows:
                    self.assertEqual(perturbed["date_spreads"]["all"][cell], second["date_spreads"]["all"][cell])

    def test_empty_base_and_empty_full_population_print_exact_missing_values(self):
        later_key = "f2-stab-15/L001"
        null = {"value": None, "reason": "no_qualified_leg"}
        for layout in ([(15, 1, 8, 2)], []):
            with self.subTest(n=len(layout)), TemporaryDirectory() as directory:
                with patch.object(fixture, "layout", return_value=layout):
                    world = DescriptionWorld(Path(directory).resolve() / "world", fixture.IDS[2], "late_index")
                census, prints = self._score(world)
                self.assertEqual(census["counts"], {"n_legs": len(layout), "n_local_dates": len(layout)})
                self.assertEqual(census["by_kit_set"]["base14"]["n_legs"], 0)
                self.assertEqual(census["by_kit_set"]["base14"]["n_local_dates"], 0)
                self.assertTrue(all(value == {"n_legs": 0, "n_local_dates": 0}
                                    for value in census["by_kit_set"]["base14"]["by_runner_pin"].values()))
                for views in prints.values():
                    self.assertEqual(views["base14"], null)
                    if not layout:
                        self.assertEqual(views["all"], null)
                if layout:
                    self.assertEqual(set(prints["turn"]["all"]), {later_key})
                    cell = f'{world.records[later_key][2]["prefill_tokens"]}/gpu_rail/mean_w'
                    spread = prints["date_spreads"]["all"][cell]
                    self.assertEqual(len(spread["dates"]), 1)
                    self.assertEqual(spread["sd_date_means"], {"value": None, "reason": "fewer_than_two"})


class Stage1BindingHistoryTests(unittest.TestCase):
    def _check_binding_history(self, look):
        temporary = self.enterContext(TemporaryDirectory())
        world = fixture.World(Path(temporary).resolve() / "world", look)
        rc, out, err, events = fixture.invoke(world, "stage1")
        self.assertEqual((rc, out, err), (0, b"", b""))
        self.assertFalse([path for kind, path in events if kind == "open"])

        def git(*args):
            return subprocess.check_output(["git", "-C", str(world.repo), *args])

        prior_commit = world.book.head
        prior_row = world.row.copy()
        prior_ledger = world.ledger.read_bytes()
        self.assertEqual(git("show", ":LOOKS.json"), prior_ledger)
        stage_path = world.stage.relative_to(world.repo).as_posix()
        census = world.stage.read_bytes()
        staged_row = dict(prior_row, status="stage1_committed", stage1_path=stage_path,
                          stage1_sha256=fixture.sha(census))
        world.row = staged_row.copy()
        world.save_row()
        staged_ledger = world.ledger.read_bytes()
        git("add", "--", "LOOKS.json", stage_path)
        self.assertEqual(git("show", ":LOOKS.json"), staged_ledger)
        self.assertEqual(git("show", f":{stage_path}"), census)
        self.assertFalse(fixture.git_ok(world.repo, "cat-file", "-e", f"HEAD:{stage_path}"))
        self.assertEqual(fixture.reservation_boundary(self, world), [])

        # Restore the prior ledger before committing the retained census.
        world.row = prior_row
        world.ledger.write_bytes(prior_ledger)
        git("add", "--", "LOOKS.json")
        self.assertEqual(git("show", ":LOOKS.json"), prior_ledger)
        self.assertEqual(git("show", f":{stage_path}"), census)
        world.bind()
        book = reader.Book(world.repo)
        self.assertNotEqual(world.reg, world.artifact_commit)
        self.assertTrue(book.ancestor(world.reg, world.artifact_commit))
        self.assertEqual(book.blob(world.artifact_commit, "LOOKS.json"), prior_ledger)
        self.assertEqual(book.blob(world.artifact_commit, stage_path), census)
        self.assertNotEqual(world.artifact_commit, world.stage1_commit)
        self.assertTrue(book.ancestor(world.artifact_commit, world.stage1_commit))
        self.assertEqual(world.row["stage1_commit"], world.artifact_commit)
        self.assertEqual(reader._binding_commit(book, "LOOKS.json", world.row), world.stage1_commit)
        self.assertEqual(fixture.reservation_boundary(self, world), [str(world.private)])

        # The same bytes and ancestry cannot repair an incomplete committed binding.
        world.book.head = prior_commit
        world.row = staged_row
        world.ledger.write_bytes(staged_ledger)
        world.bind()
        book = reader.Book(world.repo)
        self.assertEqual(book.blob(world.artifact_commit, "LOOKS.json"), staged_ledger)
        self.assertEqual(book.blob(world.artifact_commit, stage_path), census)
        with self.assertRaisesRegex(reader.Refusal, "stage-1 binding changed after commitment"):
            reader._binding_commit(book, "LOOKS.json", world.row)
        self.assertEqual(fixture.reservation_boundary(self, world), [])

    def test_lm_inst_01_stage1_commit_before_reservation(self):
        self._check_binding_history("lm-inst-01")

    def test_lm_stab_01_stage1_commit_before_reservation(self):
        self._check_binding_history("lm-stab-01")

    def test_lm_stab_02_stage1_commit_before_reservation(self):
        self._check_binding_history("lm-stab-02")


class InstrumentWithEmptySpan(fixture.World):
    span_id = "invented-closed-empty"

    def declare_unrun_positions(self):
        super().declare_unrun_positions()
        key = self.closed_position = min(self.dropped)
        kit_id = key.split("/")[0]
        kit = self.repo / "kits" / f"{kit_id}.json"
        prefix = f"ops/{self.span_id}"
        receipt = f"{prefix}/runner_receipt.json"
        issue = {"kit_id": kit_id, "kit_sha256": fixture.sha(kit.read_bytes()), "span_id": self.span_id}
        close = dict(issue, runner_pin=fixture.read(kit)["frozen"]["commit"], closed=True,
                     member_legs=[], unrun=[key])
        fixture.put(self.repo / f"{prefix}/issue.json", issue)
        fixture.put(self.repo / receipt, close)
        drop = self.repo / "drops" / f"{key}.json"
        declaration = fixture.read(drop)
        queue = declaration.pop("queue")
        self.dropped[key] = "ended_without_member"
        fixture.put(drop, dict(declaration, reason=self.dropped[key], receipt=receipt))
        old = (f"The lead declares {key} dropped:queue_retired. No member exists or will exist. "
               f"Evidence {queue} sha256={fixture.sha((self.repo / queue).read_bytes())}.")
        new = (f"The lead declares {key} dropped:ended_without_member. No member exists or will exist. "
               f"Evidence {receipt} sha256={fixture.sha(fixture.wire(close))}.")
        state = self.repo / "RUN_STATE.md"
        fixture.put(state, state.read_bytes().replace(old.encode(), new.encode(), 1))


class ContentAddressedInstrumentTests(unittest.TestCase):
    def test_verifier_hashes_native_bytes_without_decoding(self):
        temporary = self.enterContext(TemporaryDirectory())
        folder = Path(temporary).resolve()
        root = folder / "copy"
        name = "sample.km003c"
        payload = b"\x00\xff\x80\r\n"
        fixture.put(root / "invented-span" / name, payload)
        entry = {"path": name, "sha256": fixture.sha(payload), "size": len(payload)}
        span = {"span_id": "invented-span", "runner_commit": "a" * 40,
                "close_item": 1, "check_item": 2, "files": [entry]}
        span["offload_manifest_sha256"] = offload_manifest_bytes_sha256(span)
        pins = {"schema": "joulewise.cadence_look_input_pins.v1", "spans": [span]}
        verifier = reader.CODE_ROOT / "joulewise/cadence_looks/description_inputs.py"
        report = folder / "verification.json"
        result = subprocess.run([sys.executable, "-I", "-B", str(verifier), str(root), str(report)],
                                input=fixture.wire(pins), capture_output=True, check=False)
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, b"", b""))
        self.assertEqual(fixture.read(report), {"status": "pass", "digests": {
            f"invented-span/{name}": {"pinned_sha256": entry["sha256"], "observed_sha256": entry["sha256"]},
        }})

    def _pinned_world(self, *, world_type=fixture.World, empty_span_files=(), dc_omission=False,
                      first_check=None, edit_signals=None):
        temporary = self.enterContext(TemporaryDirectory())
        world = world_type(Path(temporary).resolve() / "world", fixture.IDS[0])
        witness = sorted(world.good)[0]
        support_path = world.copy / witness / "support.json"
        support = fixture.read(support_path)
        support["rail_intervals"].remove([50, 51])
        fixture.put(support_path, support)
        other, = set(world.good) - {witness}
        if edit_signals is None:
            # The other leg has nominal rail intervals without recordings.
            trace = world.copy / other / fixture.RAIL_FILE
            with trace.open(newline="") as stream:
                rows = csv.reader(stream)
                header = next(rows)
                retained = [row for row in rows if not 50 <= Decimal(row[0]) < 57]
            fixture.put(trace, fixture.csvbytes([header, *retained]))
        else:
            edit_signals(world, witness, other)
        if dc_omission:
            point_support = world.copy / other / "support.json"
            meta = fixture.read(point_support)
            meta["meter_times"].remove(50)
            meta["meter_counts"]["decoded"] = len(meta["meter_times"])
            fixture.put(point_support, meta)

        custody = world.base / "pinned-copy"
        spans = []
        witness_stream = None
        records = [(key, op, receipt) for key, (op, receipt, _, _) in world.records.items()]
        if empty_span_files:
            receipt = fixture.read(world.repo / "ops" / world.span_id / "runner_receipt.json")
            records.append((None, None, receipt))
        for number, (key, op, receipt) in enumerate(records, start=1000):
            span = receipt["span_id"]
            operational = world.repo / "ops" / span
            if key is None:
                inputs = {name: (operational / name).read_bytes() for name in empty_span_files}
            else:
                leg = f"legs/{op['leg_id']}"
                inputs = {str(path.relative_to(operational)): path.read_bytes()
                          for path in operational.rglob("*") if path.is_file()}
                inputs.update({f"{leg}/{name}": (world.copy / key / name).read_bytes()
                               for name in reader.VALUE_FILES})
            for name, data in inputs.items():
                fixture.put(custody / span / name, data)
            if key == witness:
                witness_stream = custody / span / leg / "support.json"
            row = {"span_id": span, "runner_commit": receipt["runner_pin"],
                   "close_item": number, "check_item": number,
                   "files": [{"path": name, "sha256": fixture.sha(data), "size": len(data)}
                             for name, data in sorted(inputs.items())]}
            row["offload_manifest_sha256"] = offload_manifest_bytes_sha256(row)
            spans.append(row)
        self.assertIsNotNone(witness_stream)

        schema_path = reader._pin_paths(world.look)["manifest_schema"]
        schema = (reader.CODE_ROOT / schema_path).read_bytes()
        fixture.put(world.repo / schema_path, schema)
        manifest = fixture.read(world.man)
        manifest["code_pins"]["manifest_schema"]["sha256"] = fixture.sha(schema)
        pin_name = "instrument.inputs.json"
        pins = {"schema": "joulewise.cadence_look_input_pins.v1", "spans": spans}
        fixture.put(world.repo / pin_name, pins)
        manifest["inputs"] = {"pins": {"path": pin_name, "sha256": fixture.sha(fixture.wire(pins))}}
        fixture.put(world.man, manifest)
        state = world.repo / "RUN_STATE.md"
        checks = []
        for index, row in enumerate(spans):
            sha = row["offload_manifest_sha256"]
            claim = first_check(sha) if index == 0 and first_check else f"Offload manifest sha256 {sha}."
            checks.append(f"\n{row['check_item']}. **Invented Check of {row['span_id']}.**\n\n{claim}\n")
        fixture.put(state, state.read_bytes() + "".join(checks).encode())
        world.reg = world.book.seal("register the Check-bound instrument manifest")

        world.copy = custody
        copy = world.targets["copy"]
        proof = fixture.read(copy)
        proof.update(root=str(custody), files={f"{row['span_id']}/{entry['path']}": entry["sha256"]
                                              for row in spans for entry in row["files"]})
        fixture.put(copy, proof)
        manifest_sha = fixture.sha(world.man.read_bytes())
        cold = world.targets["cold"]
        fixture.put(cold, dict(fixture.read(cold), manifest_sha256=manifest_sha))
        for path in (world.man, state, world.repo / pin_name, world.repo / schema_path, cold, copy):
            world.row["input_hashes"][str(path.relative_to(world.repo))] = fixture.sha(path.read_bytes())
        world.row.update(sha256=manifest_sha, registration_commit=world.reg)
        world.save_row()
        world.book.seal("bind cold and copy authority after final registration")
        return world, witness, witness_stream, pins

    def test_closed_empty_span_requires_check_pins_for_every_witness_file(self):
        for names in ((), ("runner_receipt.json",), ("issue.json", "runner_receipt.json")):
            with self.subTest(pinned_files=names):
                world, _, _, _ = self._pinned_world(world_type=InstrumentWithEmptySpan, empty_span_files=names)
                if len(names) == 2:
                    fixture.Checks().stage1(world)
                    self.assertEqual(fixture.read(world.stage)["positions"][world.closed_position]["disposition"],
                                     "dropped:ended_without_member")
                    self.assertEqual(fixture.reservation_boundary(self, world), [str(world.private)])
                else:
                    rc, out, _, events = fixture.invoke(world, "stage1")
                    self.assertEqual((rc, out), (2, b""))
                    self.assertFalse(any(kind == "open" for kind, _ in events))
                    # The isolated hash verifier may create its scratch report.
                    destinations = (world.stage.parent, world.private.parent, world.public.parent)
                    self.assertFalse(any(kind == "write" and any(Path(path).is_relative_to(root)
                                                               for root in destinations)
                                         for kind, path in events), events)
                    self.assertFalse(world.stage.exists() or world.public.exists() or world.private.exists())

    def test_check_offload_digest_cannot_be_replaced_by_a_planning_digest(self):
        wrong_digest = fixture.sha(b"an earlier invented offload plan")

        def forged_check(expected):
            return f"Offload manifest sha256 {wrong_digest}.\nSuperseded planning digest {expected}."

        world, _, _, _ = self._pinned_world(first_check=forged_check)
        fixture.Checks().refused(world, "stage1")
        self.assertFalse(world.stage.exists() or world.public.exists() or world.private.exists())

    def test_check_offload_digest_matches_all_printed_characters_and_is_unambiguous(self):
        sha = "a" * 8 + "b" * 53 + "c" * 3
        correct = f"Offload manifest sha256 {sha}."
        doc = {"spans": [{"check_item": 12, "offload_manifest_sha256": sha}]}
        cases = {
            "full": (correct, True),
            "abbreviated": ("- **Offload manifest SHA-256:** `aaaaaaaa…ccc`.", True),
            "wrong_prefix": ("Offload manifest sha256 aaaaaaab...ccc.", False),
            "wrong_suffix": ("Offload manifest sha256 aaaaaaaa...ccd.", False),
            "duplicate": (f"{correct}\n{correct}", False),
            "fenced": (f"~~~\n{correct}\n~~~", False),
            "quoted": (f"> {correct}", False),
        }
        for case, (claim, admits) in cases.items():
            with self.subTest(case=case):
                text = f"12. **Invented span Check.**\n\n{claim}\n"
                if admits:
                    reader._require_input_checks(doc, text)
                else:
                    with self.assertRaises(reader.Refusal):
                        reader._require_input_checks(doc, text)

    def test_dc_ledger_omission_is_counted_before_any_value_parse(self):
        world, _, _, _ = self._pinned_world(dc_omission=True)
        fixture.Checks().stage1(world)
        snapshot = reader.Snapshot(world.repo, world.look, "stage2")
        census, qualified = reader.census(snapshot)
        snapshot.check_stage1(census)
        sources = reader.verify_gates(snapshot, qualified)
        with patch.object(reader, "_sample", side_effect=AssertionError("value parsed before reconciliation")):
            tables = reader.score(snapshot, sources, qualified, lambda: None)
        mismatch_rows = dict.fromkeys(qualified, fixture.null("interval_ledger_mismatch"))
        self.assertEqual(tables, dict.fromkeys(("hold", "turn", "gain", "edges"), mismatch_rows))
        expected = snapshot.public_record(census)
        prebound = snapshot.validate_public(expected, expected)
        public = json.loads(description_worker._public_after_scoring(snapshot, expected, prebound, tables))
        self.assertEqual((public["n_legs"], public["n_interval_ledger_mismatch"]), (2, 2))

    def _pinned_reports(self, world):
        fixture.Checks().stage1(world)
        snapshot = reader.Snapshot(world.repo, world.look, "stage2")
        census, qualified = reader.census(snapshot)
        snapshot.check_stage1(census)
        sources = reader.verify_gates(snapshot, qualified)
        expected = snapshot.public_record(census)
        prebound = snapshot.validate_public(expected, expected)
        tables = reader.score(snapshot, sources, qualified, lambda: None)
        public = description_worker._public_after_scoring(snapshot, expected, prebound, tables)
        return tables, json.loads(public)

    def test_pinned_nominal_dc_slots_are_coverage_with_593_of_600_samples(self):
        missing = {50, 100, 150, 200, 250, 300, 350}

        def sparse(world, _, other):
            folder = world.copy / other
            trace = folder / fixture.DC_FILE
            with trace.open(newline="") as stream:
                header, *samples = csv.reader(stream)
            retained = [sample for sample in samples if Decimal(sample[0]) not in missing]
            self.assertEqual(sum(0 <= Decimal(sample[0]) < 600 for sample in retained), 593)
            fixture.put(trace, fixture.csvbytes([header, *retained]))
            meta_path = folder / "support.json"
            meta = fixture.read(meta_path)
            if not nominal:
                meta["meter_times"] = [stamp for stamp in meta["meter_times"] if stamp not in missing]
            self.assertEqual(sum(0 <= stamp < 600 for stamp in meta["meter_times"]), 600 if nominal else 593)
            meta["meter_counts"]["decoded"] = len(retained)
            fixture.put(meta_path, meta)

        outcomes = []
        for nominal in (True, False):
            with self.subTest(nominal_ledger=nominal):
                world, witness, _, _ = self._pinned_world(edit_signals=sparse)
                other, = set(world.good) - {witness}
                tables, public = self._pinned_reports(world)
                hold = tables["hold"][other]
                self.assertEqual(hold["dc_in"]["mean_w"], fixture.null("coverage"))
                self.assertIsInstance(hold["gpu_rail"]["mean_w"], float)
                self.assertIsInstance(hold["rail_sum"]["mean_w"], float)
                self.assertEqual((public["n_legs"], public["n_interval_ledger_mismatch"]), (2, 1))
                outcomes.append(tables)
        self.assertEqual(len(outcomes), 2)
        self.assertEqual(*outcomes)

    def test_pinned_dc_omission_outranks_contamination_and_absence(self):
        def edit(world, _, other):
            folder = world.copy / other
            meta_path = folder / "support.json"
            meta = fixture.read(meta_path)
            meta[flag] = False
            if omitted:
                meta["meter_times"].remove(50)
                meta["meter_counts"]["decoded"] = len(meta["meter_times"])
            fixture.put(meta_path, meta)
            trace = folder / fixture.DC_FILE
            with trace.open(newline="") as stream:
                header, *samples = csv.reader(stream)
            self.assertEqual(sum(0 <= Decimal(sample[0]) < 600 for sample in samples), 600)
            fixture.put(trace, fixture.csvbytes([header, *((stamp, "DO_NOT_PARSE") for stamp, _ in samples)]))

        for flag, omitted in (("meter_clean", True), ("meter_clean", False), ("meter_present", True)):
            with self.subTest(flag=flag, omitted=omitted):
                world, witness, _, _ = self._pinned_world(edit_signals=edit)
                other, = set(world.good) - {witness}
                tables, public = self._pinned_reports(world)
                for table in tables.values():
                    self.assertEqual(table[witness], fixture.null("interval_ledger_mismatch"))
                if omitted:
                    self.assertTrue(all(table[other] == fixture.null("interval_ledger_mismatch")
                                        for table in tables.values()))
                else:
                    hold = tables["hold"][other]
                    self.assertEqual(hold["dc_in"]["mean_w"], fixture.null("meter_contaminated"))
                    self.assertIsInstance(hold["gpu_rail"]["mean_w"], float)
                self.assertEqual((public["n_legs"], public["n_interval_ledger_mismatch"]), (2, 1 + omitted))

    def test_pinned_recovery_anchor_uses_recorded_dc_start_with_contamination(self):
        recordings = []
        outcomes = []

        def edit(world, witness, _):
            folder = world.copy / witness
            rail = folder / fixture.RAIL_FILE
            with rail.open(newline="") as stream:
                header, *rows = csv.reader(stream)
            fixture.put(rail, fixture.csvbytes([header, *(row for row in rows if Decimal(row[0]) != 50)]))
            dc = folder / fixture.DC_FILE
            with dc.open(newline="") as stream:
                header, *rows = csv.reader(stream)
            retained = [row for row in rows if Decimal(row[0]) >= -10]
            self.assertEqual(Decimal(retained[0][0]), -10)
            fixture.put(dc, fixture.csvbytes([header, *retained]))
            recordings.append((rail.read_bytes(), dc.read_bytes()))
            path = folder / "support.json"
            meta = fixture.read(path)
            meta["meter_clean"] = False
            meta["meter_counts"]["decoded"] = len(retained)
            if not nominal:
                meta["meter_times"] = [stamp for stamp in meta["meter_times"] if stamp >= -10]
            self.assertEqual(meta["meter_times"][0], -20 if nominal else -10)
            fixture.put(path, meta)

        for nominal in (True, False):
            with self.subTest(nominal_ledger=nominal):
                world, witness, _, _ = self._pinned_world(edit_signals=edit)
                tables, public = self._pinned_reports(world)
                edges = tables["edges"][witness]
                self.assertEqual(edges["unobserved_s"], 19.0)
                for rail in ("gpu_rail", "rail_sum"):
                    self.assertEqual(edges["recovery_s"][rail], fixture.null("under", bound_s=19.0))
                self.assertEqual((public["n_legs"], public["n_interval_ledger_mismatch"]), (2, 0))
                outcomes.append(tables)
        self.assertEqual(len(outcomes), 2)
        self.assertEqual(*recordings)
        self.assertEqual(*outcomes)

    def test_unlisted_identity_requires_check_pin_comparison_before_decode(self):
        for role in ("issue.json", "runner_receipt.json"):
            with self.subTest(role=role), TemporaryDirectory() as temporary:
                root = Path(temporary).resolve() / "book"
                book = fixture.Book(root)
                name = f"ops/invented-unlisted-span/{role}"
                blob = fixture.wire({"kit_id": "f2-inst-99", "invented": role})
                fixture.put(root / name, blob)
                commit = book.seal("invented closed unrelated span")
                snapshot = reader.Snapshot.__new__(reader.Snapshot)
                snapshot.book = reader.Book(root)
                snapshot.commit = snapshot.receipts = commit
                snapshot.look = fixture.IDS[0]
                snapshot.hashes = {name: fixture.sha(blob)}
                snapshot.cache = {}
                pin_name = name.removeprefix("ops/")
                for pins, refusal in (
                    ({}, "absent from its Check-time pins"),
                    ({pin_name: {"size": len(blob), "sha256": "0" * 64}}, "differ from their Check-time pin"),
                    ({pin_name: {"size": len(blob), "sha256": fixture.sha(blob)}}, None),
                ):
                    with self.subTest(pin=refusal), patch.object(reader, "decode", wraps=reader.decode) as decoded:
                        snapshot.input_files = pins
                        if refusal:
                            with self.assertRaisesRegex(reader.Refusal, refusal):
                                reader._reconcile_member_bundles(snapshot, {}, {}, {})
                            decoded.assert_not_called()
                        else:
                            reader._reconcile_member_bundles(snapshot, {}, {}, {})
                            decoded.assert_called_once_with(blob)

    def _check_pinned_public_gate(self, world):
        trace = """
def record_public_gate(frame, event, result):
    if event == "return" and frame.f_code.co_name == "public_record" and isinstance(result, dict):
        log("public_record", result)
    if event == "return" and frame.f_code.co_name == "validate_public" and isinstance(result, bytes):
        log("public_bytes", result.hex())
sys.setprofile(record_public_gate)
"""
        reserve = """
def observe_reservation(event, args):
    if event == "os.mkdir" and args[0] == os.environ["DESC_RESERVATION"]:
        log("reservation_attempt", args[0])
        raise PermissionError("synthetic boundary")
sys.addaudithook(observe_reservation)
"""
        truth = world.public_truth()
        self.assertEqual(truth["n_legs"], 2)
        self.assertEqual(set(truth), {"look_id", "commit", "manifest_sha256", "stage1_sha256", "n_legs"})
        probe = fixture.PROBE + trace + reserve
        with patch.object(fixture, "PROBE", probe):
            rc, out, _, events = fixture.invoke(world, "stage2")
        self.assertEqual((rc, out), (2, b""))
        boundary = events.index(["reservation_attempt", str(world.private)])
        self.assertIn(["public_bytes", fixture.wire(truth).hex()], events[:boundary])
        self.assertFalse(any(kind == "open" for kind, _ in events))

        candidate = world.base / "pinned-candidate.json"
        for count in (0, 1):
            with self.subTest(standalone_count=count):
                fixture.put(candidate, dict(truth, n_interval_ledger_mismatch=count))
                with patch.object(fixture, "PROBE", probe):
                    rc, out, _, events = fixture.invoke(world, "validate-public", "--candidate", str(candidate))
                self.assertEqual((rc, out), (2, b""))
                self.assertIn(["public_record", truth], events)
                forbidden = {"open", "reservation_attempt", "public_bytes"}
                self.assertFalse(any(kind in forbidden for kind, _ in events), events)
                self.assertFalse(world.private.exists() or world.public.exists())

        spent_reservation = """
_real_lexists = os.path.lexists
def _with_reservation(path):
    return os.fsdecode(path) == os.environ["DESC_RESERVATION"] or _real_lexists(path)
os.path.lexists = _with_reservation
"""
        prior_public = fixture.wire(dict(truth, n_interval_ledger_mismatch=1))
        for marker in ("reservation", "publication"):
            with self.subTest(spent=marker):
                if marker == "publication":
                    fixture.put(world.public, prior_public)
                with patch.object(fixture, "PROBE", probe + (spent_reservation if marker == "reservation" else "")):
                    rc, out, _, events = fixture.invoke(world, "validate-public", "--candidate", str(candidate))
                self.assertEqual((rc, out), (2, b""))
                forbidden = {"open", "descriptor", "write", "reservation_attempt", "public_record", "public_bytes"}
                self.assertFalse(any(kind in forbidden for kind, _ in events), events)
                self.assertFalse(world.private.exists())
                if marker == "publication":
                    self.assertEqual(world.public.read_bytes(), prior_public)
                    world.public.unlink()

    def test_hash_only_verifier_and_confined_leg_nulls(self):
        world, witness, stream, pins = self._pinned_world()
        verifier = reader.CODE_ROOT / "joulewise/cadence_looks/description_inputs.py"
        command = [sys.executable, "-I", "-B", str(verifier), str(world.copy)]
        expected = fixture.sha(stream.read_bytes())
        path = str(stream.relative_to(world.copy))
        source = stream.read_bytes()
        for fault in ("clean", "missing", "extra", "changed", "symlink"):
            with self.subTest(fault=fault):
                extra = stream.with_name("unexpected.json")
                if fault == "missing":
                    stream.unlink()
                elif fault == "extra":
                    extra.write_bytes(b"invented")
                elif fault == "changed":
                    stream.write_bytes(b"x" + source[1:])
                elif fault == "symlink":
                    stream.unlink()
                    stream.symlink_to(stream.with_name(fixture.RAIL_FILE))
                receipt = world.base / f"verify-{fault}.json"
                result = subprocess.run([*command, str(receipt)], input=fixture.wire(pins),
                                        capture_output=True, check=False)
                self.assertEqual((result.stdout, result.stderr), (b"", b""))
                report = fixture.read(receipt)
                self.assertEqual(report.keys(), {"status", "digests"})
                self.assertEqual(report["digests"][path]["pinned_sha256"], expected)
                passed = fault == "clean"
                self.assertEqual((result.returncode, report["status"]), (0, "pass") if passed else (2, "fail"))
                if not passed:
                    rc, out, _, events = fixture.invoke(world, "stage1")
                    self.assertEqual((rc, out), (2, b""))
                    self.assertFalse(any(kind == "open" for kind, _ in events))
                    self.assertFalse(world.stage.exists() or world.private.exists())
                extra.unlink(missing_ok=True)
                stream.unlink(missing_ok=True)
                stream.write_bytes(source)

        fixture.Checks().stage1(world)
        stream.write_bytes(b"x" + source[1:])
        self.assertEqual(fixture.reservation_boundary(self, world), [])
        stream.write_bytes(source)
        self._check_pinned_public_gate(world)
        snapshot = reader.Snapshot(world.repo, world.look, "stage2")
        census, qualified = reader.census(snapshot)
        snapshot.check_stage1(census)
        sources = reader.verify_gates(snapshot, qualified)
        stream.write_bytes(b"x" + source[1:])
        with self.assertRaisesRegex(PinRefusal, "stage-2 bytes differ"):
            reader.score(snapshot, sources, qualified, lambda: None)
        stream.write_bytes(source)
        tables = reader.score(snapshot, sources, qualified, lambda: None)
        for table in tables.values():
            self.assertEqual(table[witness], fixture.null("interval_ledger_mismatch"))
        other, = set(qualified) - {witness}
        self.assertEqual(tables["hold"][other]["gpu_rail"]["mean_w"], fixture.null("coverage"))
        self.assertIsInstance(tables["hold"][other]["dc_in"]["mean_w"], (int, float))
        expected_public = snapshot.public_record(census)
        prebound = snapshot.validate_public(expected_public, expected_public)
        released = json.loads(description_worker._public_after_scoring(snapshot, expected_public, prebound, tables))
        self.assertEqual(released, dict(expected_public, n_interval_ledger_mismatch=1))
        self.assertEqual(released["n_legs"], 2)
        self.assertIs(type(released["n_interval_ledger_mismatch"]), int)
        for wrong in (True, 1.0, 0, len(world.good) + 1):
            with self.subTest(public_count=wrong), self.assertRaises(reader.Refusal):
                snapshot.validate_public(dict(released, n_interval_ledger_mismatch=wrong), released)


class SpentDescriptionLookTests(unittest.TestCase):
    def test_spent_look_refuses_before_launching_final_validator(self):
        # Simulate the existing reservation for the worker and its observer.
        # The test host may deny actually creating the reservation directory.
        spent = """
_real_lexists = os.path.lexists
def _with_reservation(path):
    return os.fsdecode(path) == os.environ["DESC_RESERVATION"] or _real_lexists(path)
os.path.lexists = _with_reservation
"""
        for look in fixture.IDS:
            with self.subTest(look=look), TemporaryDirectory() as temporary:
                world = DescriptionWorld(Path(temporary).resolve() / "world", look)
                world.commit_stage1(self)
                with patch.object(fixture, "PROBE", fixture.PROBE + spent):
                    rc, out, _, events = fixture.invoke(world, "stage2")
                self.assertEqual((rc, out), (2, b""))
                self.assertFalse(world.public.exists())
                self.assertFalse(any(kind in {"open", "descriptor", "write"}
                                     for kind, _ in events), events)


if __name__ == "__main__":
    unittest.main()
