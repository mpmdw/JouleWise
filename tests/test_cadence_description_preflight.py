"""Exercise native-look dependency admission with invented ledger and source bytes."""

from decimal import Decimal
from itertools import product
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from joulewise.cadence_looks import description as reader
from tests import test_desc_looks_acceptance as fixture
from tests.fixtures.description_worlds import DescriptionWorld


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
