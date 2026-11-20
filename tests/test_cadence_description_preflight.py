"""Exercise native-look dependency admission with invented ledger and source bytes."""

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
        self.row.update(status="stage1_committed", stage1_path=self.stage_name,
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
                eligible = set(world.good) - {key}
                rc, stdout, stderr, events = fixture.invoke(world, "stage1")
                self.assertEqual((rc, stdout, stderr), (0, b"", b""))
                self.assertFalse([event for event, _ in events if event == "open"])
                document = fixture.read(world.stage)
                position = document["positions"][key]
                self.assertIs(position["loaded_flag"], True)
                self.assertEqual(position["disposition"], "not_qualified:loaded")
                refs = next(row for row in world.rows if row["key"] == key)
                self.assertEqual(position["receipt"], refs["receipt"])
                self.assertEqual(document["counts"]["n_legs"], len(eligible))
                self.assertEqual(document["by_kit"][key.split("/")[0]]["not_qualified:loaded"], 1)
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
            self.assertEqual(counts, {"n_legs": len(last.good) - 1, "n_local_dates": 13})


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
                checks = fixture.Checks()
                checks.stage1(world)
                with patch.object(fixture, "PROBE", fixture.PROBE + spent):
                    rc, out, _, events = fixture.invoke(world, "stage2")
                self.assertEqual((rc, out), (2, b""))
                self.assertFalse(world.public.exists())
                self.assertFalse(any(kind in {"open", "descriptor", "write"}
                                     for kind, _ in events), events)


if __name__ == "__main__":
    unittest.main()
