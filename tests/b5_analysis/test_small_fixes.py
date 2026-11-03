"""D-188 SMALL-FIXES: in-program dedupes and step-0 I/O keep every decision.

Each change must give the same values, the same refusal code and the same
serial position of the first failure as the code it replaces. The references
below are the replaced code, copied verbatim where the change rewrote it.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from joulewise.analysis_engine import inputs
from joulewise.b5_analysis import archive
from joulewise.b5_analysis.archive import ArchiveHandle, CensusRow
from joulewise.b5_analysis.bracket import WindowBracket
from joulewise.b5_analysis.windows import AnalysisRefusal


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


# --------------------------------------------------------------------------
# archive.py: SHA256SUMS once per handle, bulk census, threaded runs-root
# --------------------------------------------------------------------------

def _reference_compare_runs_root(handle: ArchiveHandle):
    """compare_runs_root as it was before D-188 (serial), for comparison."""
    root = handle.window.claim_runs_root
    prefix = "claim-runs/"
    if root.is_relative_to(handle.window.custody_root):
        prefix = "night-custody/" + root.relative_to(handle.window.custody_root).as_posix() + "/"
    manifest = {name.removeprefix(prefix): digest for name, digest in handle._sources().items()
                if name.startswith(prefix)}
    if not manifest:
        raise AnalysisRefusal("runs_root_differs_from_archive")
    for name, digest in manifest.items():
        try:
            path = root / name
            if not path.resolve().is_relative_to(root.resolve()):
                raise OSError()
            raw = path.read_bytes()
        except OSError:
            raise AnalysisRefusal("runs_root_differs_from_archive") from None
        if hashlib.sha256(raw).hexdigest() != digest:
            raise AnalysisRefusal("runs_root_differs_from_archive")
        key = "original/claim-runs/" + name
        row = CensusRow(key, digest, "sources_sha256sums")
        if key in handle._census and handle._census[key] != row:
            raise AnalysisRefusal("archive_input_changed")
        handle._census[key] = row
    extra = sum(path.relative_to(root).as_posix() not in manifest for path in root.rglob("*") if path.is_file())
    return ({"code": "runs_root_has_unlisted_file", "count": extra},) if extra else ()


class _Tree:
    """A synthetic archive: sources/ inventory plus the original claim runs."""

    def __init__(self, base: Path, n: int = 24):
        self.base = base
        self.root = base / "archive"
        self.claim = base / "claim"
        self.custody = base / "custody"
        (self.root / "sources/claim-runs").mkdir(parents=True)
        (self.root / "sources/repo").mkdir(parents=True)
        self.claim.mkdir()
        self.custody.mkdir()
        self.lines: list[tuple[str, str]] = []
        for i in range(n):
            raw = (f"run {i}\n" * (i * 37 + 1)).encode()
            name = f"run-{i:03d}/metadata.json"
            for target in (self.root / "sources/claim-runs" / name, self.claim / name):
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            self.lines.append((_sha(raw), "claim-runs/" + name))
        for i in range(6):
            raw = f"repo file {i}\n".encode()
            (self.root / f"sources/repo/f{i}.json").write_bytes(raw)
            self.lines.append((_sha(raw), f"repo/f{i}.json"))
        self.write_sums()

    def write_sums(self, lines=None):
        text = "".join(f"{digest}  {name}\n" for digest, name in (lines or self.lines))
        (self.root / "sources/SHA256SUMS").write_bytes(text.encode())

    def handle(self) -> ArchiveHandle:
        window = SimpleNamespace(archive_root=self.root, claim_runs_root=self.claim, custody_root=self.custody,
                                 record=SimpleNamespace(record_shape="pin4"), pack_id="s0-synthetic")
        return ArchiveHandle(window, {"outputs": {}}, {})

    def names(self) -> list[str]:
        return [name for _digest, name in self.lines]


def _outcome(call):
    try:
        value = call()
    except AnalysisRefusal as exc:
        return ("refusal", exc.code)
    except Exception as exc:  # noqa: BLE001 - the type is the observable
        return ("exception", type(exc).__name__)
    return ("ok", value)


class SourcesManifestOncePerHandleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="d188-small-")
        self.addCleanup(self.tmp.cleanup)
        self.tree = _Tree(Path(self.tmp.name))

    def _sums_reads(self, handle, names):
        real = archive._read
        reads = []

        def counted(root, relative, *args, **kwargs):
            if relative == "sources/SHA256SUMS":
                reads.append(relative)
            return real(root, relative, *args, **kwargs)

        with mock.patch.object(archive, "_read", side_effect=counted):
            for name in names:
                handle.source_bytes("sources/" + name)
        return len(reads)

    def test_unchanged_inventory_is_read_once_per_handle(self):
        handle = self.tree.handle()
        self.assertEqual(self._sums_reads(handle, self.tree.names()), 1)
        row = next(r for r in handle.census() if r.path == "sources/SHA256SUMS")
        self.assertEqual(row.sha256, _sha((self.tree.root / "sources/SHA256SUMS").read_bytes()))
        # A second handle (another program scope) reads it again.
        self.assertEqual(self._sums_reads(self.tree.handle(), self.tree.names()[:2]), 1)

    def test_same_size_rewrite_with_restored_mtime_is_detected(self):
        """The critic's case: in-place same-size rewrite, then utime. ctime still moves."""
        handle = self.tree.handle()
        handle.source_bytes("sources/" + self.tree.names()[0])
        path = self.tree.root / "sources/SHA256SUMS"
        before = os.lstat(path)
        raw = path.read_bytes()
        changed = raw.replace(b"run-000", b"run-00X", 1)
        self.assertEqual(len(changed), len(raw))
        with path.open("r+b") as out:
            out.write(changed)
        os.utime(path, ns=(before.st_atime_ns, before.st_mtime_ns))
        self.assertEqual(os.lstat(path).st_mtime_ns, before.st_mtime_ns)
        with self.assertRaisesRegex(AnalysisRefusal, "^archive_input_changed$"):
            handle.source_bytes("sources/" + self.tree.names()[1])

    def test_rewrite_and_removal_refuse_as_before(self):
        for mutate, code in (
            (lambda p: p.write_bytes(p.read_bytes() + b"\n"), "archive_input_changed"),
            (lambda p: p.unlink(), "archive_source_unauthenticated"),
        ):
            with self.subTest(code=code):
                tree = _Tree(Path(tempfile.mkdtemp(dir=self.tmp.name)), n=3)
                handle = tree.handle()
                handle.source_bytes("sources/" + tree.names()[0])
                mutate(tree.root / "sources/SHA256SUMS")
                with self.assertRaisesRegex(AnalysisRefusal, "^" + code + "$"):
                    handle.source_bytes("sources/" + tree.names()[1])

    def test_symlinked_inventory_is_never_trusted_by_signature(self):
        path = self.tree.root / "sources/SHA256SUMS"
        moved = self.tree.root / "sources/real-sums"
        path.rename(moved)
        path.symlink_to("real-sums")
        handle = self.tree.handle()
        self.assertEqual(self._sums_reads(handle, self.tree.names()[:3]), 3)
        self.assertIsNone(handle._source_manifest_signature)

    def test_signature_has_every_lead_ruled_field(self):
        path = self.tree.root / "sources/SHA256SUMS"
        status = os.lstat(path)
        self.assertEqual(archive._lstat_signature(path),
                         (status.st_dev, status.st_ino, status.st_mode, status.st_size,
                          status.st_mtime_ns, status.st_ctime_ns))
        self.assertIsNone(archive._lstat_signature(self.tree.root / "sources"))
        self.assertIsNone(archive._lstat_signature(self.tree.root / "absent"))


class CensusSourcesTests(unittest.TestCase):
    """Bulk census == serial source_bytes loop: census rows, first code, position."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="d188-census-")
        self.addCleanup(self.tmp.cleanup)

    def _serial(self, tree, names):
        handle = tree.handle()

        def run():
            for name in names:
                handle.source_bytes("sources/" + name)
        return _outcome(run), handle.census()

    def _bulk(self, tree, names, threads):
        handle = tree.handle()
        return _outcome(lambda: handle.census_sources(names, threads=threads)), handle.census()

    def _tree(self, n=24):
        return _Tree(Path(tempfile.mkdtemp(dir=self.tmp.name)), n=n)

    def test_identical_sorted_census_without_failures(self):
        tree = self._tree()
        names = tree.names()
        serial = self._serial(tree, names)
        self.assertEqual(serial[0], ("ok", None))
        for threads in (1, 4, 6):
            with self.subTest(threads=threads):
                self.assertEqual(self._bulk(tree, names, threads), serial)
                self.assertEqual(list(serial[1]), sorted(serial[1]))

    def test_first_failure_code_and_position_are_serial(self):
        def corrupt(tree, k):
            (tree.root / "sources" / tree.names()[k]).write_bytes(b"corrupt")

        def remove(tree, k):
            (tree.root / "sources" / tree.names()[k]).unlink()

        def escape(tree, k):
            target = tree.root / "sources" / tree.names()[k]
            outside = tree.base / "outside.json"
            outside.write_bytes(target.read_bytes())
            target.unlink()
            target.symlink_to(outside)

        def directory(tree, k):
            target = tree.root / "sources" / tree.names()[k]
            target.unlink()
            target.mkdir()

        scenarios = {"corrupt": corrupt, "remove": remove, "escape": escape, "directory": directory}
        for first_name, first in scenarios.items():
            for second_name, second in scenarios.items():
                for k1, k2 in ((3, 17), (0, 1), (22, 23)):
                    with self.subTest(first=first_name, second=second_name, k1=k1, k2=k2):
                        tree = self._tree()
                        names = tree.names()
                        first(tree, k1)
                        second(tree, k2)
                        serial = self._serial(tree, names)
                        self.assertEqual(serial[0][0], "refusal")
                        for threads in (1, 4, 6):
                            self.assertEqual(self._bulk(tree, names, threads), serial)

    def test_names_failing_pure_checks_refuse_in_place(self):
        tree = self._tree(n=8)
        good = tree.names()
        for bad in ("../escape", "SHA256SUMS", "not-in-inventory.json", "", "a/../b", "/abs"):
            for position in (0, 3, len(good)):
                with self.subTest(bad=bad, position=position):
                    names = good[:position] + [bad] + good[position:]
                    serial = self._serial(tree, names)
                    self.assertEqual(serial[0][0], "refusal")
                    for threads in (1, 4):
                        self.assertEqual(self._bulk(tree, names, threads), serial)

    def test_inventory_failure_keeps_its_position(self):
        tree = self._tree(n=6)
        (tree.root / "sources/SHA256SUMS").write_bytes(b"not a manifest\n")
        for names in (tree.names(), ["../x"] + tree.names(), ["SHA256SUMS"] + tree.names()):
            with self.subTest(head=names[0]):
                serial = self._serial(tree, names)
                self.assertEqual(self._bulk(tree, names, 4), serial)

    def test_unexpected_exception_type_is_preserved(self):
        tree = self._tree(n=6)
        names = tree.names()
        real = Path.read_bytes

        def boom(path):
            if path.name == "metadata.json" and "run-002" in str(path):
                raise MemoryError()
            return real(path)

        with mock.patch.object(Path, "read_bytes", boom):
            serial = self._serial(tree, names)
            bulk = self._bulk(tree, names, 4)
        self.assertEqual(serial[0], ("exception", "MemoryError"))
        self.assertEqual(bulk, serial)


class ThreadedCompareRunsRootTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="d188-runs-")
        self.addCleanup(self.tmp.cleanup)

    def _both(self, tree):
        reference = tree.handle()
        threaded = tree.handle()
        return ((_outcome(lambda: _reference_compare_runs_root(reference)), reference.census()),
                (_outcome(lambda: tuple(dict(f) for f in threaded.compare_runs_root())), threaded.census()))

    def _tree(self, n=24):
        return _Tree(Path(tempfile.mkdtemp(dir=self.tmp.name)), n=n)

    def test_identical_census_and_flags(self):
        tree = self._tree()
        (tree.claim / "unlisted.txt").write_bytes(b"x")
        reference, threaded = self._both(tree)
        self.assertEqual(reference[0], ("ok", ({"code": "runs_root_has_unlisted_file", "count": 1},)))
        self.assertEqual(threaded, reference)

    def test_first_failure_position_under_injected_mismatches(self):
        def corrupt(tree, k):
            (tree.claim / tree.names()[k].removeprefix("claim-runs/")).write_bytes(b"corrupt")

        def remove(tree, k):
            (tree.claim / tree.names()[k].removeprefix("claim-runs/")).unlink()

        def escape(tree, k):
            target = tree.claim / tree.names()[k].removeprefix("claim-runs/")
            outside = tree.base / f"outside-{k}"
            outside.write_bytes(target.read_bytes())
            target.unlink()
            target.symlink_to(outside)

        def precensused(tree, k):
            # A conflicting row already in the census: archive_input_changed at k.
            tree.conflict = "original/claim-runs/" + tree.names()[k].removeprefix("claim-runs/")

        scenarios = {"corrupt": corrupt, "remove": remove, "escape": escape, "precensused": precensused}
        for first_name, first in scenarios.items():
            for second_name, second in scenarios.items():
                for k1, k2 in ((2, 19), (0, 23), (11, 12)):
                    with self.subTest(first=first_name, second=second_name, k1=k1, k2=k2):
                        tree = self._tree()
                        tree.conflict = None
                        first(tree, k1)
                        second(tree, k2)
                        reference, threaded_handle = tree.handle(), tree.handle()
                        for handle in (reference, threaded_handle):
                            if tree.conflict:
                                handle._census[tree.conflict] = CensusRow(tree.conflict, "0" * 64,
                                                                          "sources_sha256sums")
                        expected = (_outcome(lambda: _reference_compare_runs_root(reference)), reference.census())
                        actual = (_outcome(lambda: tuple(dict(f) for f in threaded_handle.compare_runs_root())),
                                  threaded_handle.census())
                        self.assertEqual(expected[0][0], "refusal")
                        self.assertEqual(actual, expected)

    def test_empty_runs_inventory_refuses(self):
        tree = self._tree(n=2)
        tree.write_sums([line for line in tree.lines if not line[1].startswith("claim-runs/")])
        reference, threaded = self._both(tree)
        self.assertEqual(reference[0], ("refusal", "runs_root_differs_from_archive"))
        self.assertEqual(threaded, reference)


# --------------------------------------------------------------------------
# inputs.py: recording keys once per config and once per row
# --------------------------------------------------------------------------

class RecordingKeyHoistTests(unittest.TestCase):
    @staticmethod
    def _config(i, notes="n"):
        return {"run_id": f"r{i}", "hardware_target": {"notes": notes, "telemetry_backend": "pm"},
                "run_metadata": {"project": "p", "operator": "o"}, "workload": {"n": i % 3}}

    def _reference(self, configs, rows):
        out = []
        for row in rows:
            out.append([c for c in configs
                        if inputs._consumer_recording_key(c) == inputs._consumer_recording_key(row)])
        return out

    def test_same_matches(self):
        configs = tuple(self._config(i, notes=str(i % 2)) for i in range(9))
        rows = [self._config(i, notes="other") for i in range(7)]
        keys: dict[int, str] = {}
        actual = [inputs._declared_recording_matches(configs, keys, row) for row in rows]
        self.assertEqual(actual, self._reference(configs, rows))
        self.assertTrue(all(actual))

    def test_each_key_once_and_first_exception_in_original_order(self):
        configs = tuple(self._config(i) for i in range(5))
        rows = [self._config(i) for i in range(3)]
        real = inputs._consumer_recording_key

        def trace(fail_on):
            calls = []

            def key(config):
                calls.append(config["run_id"] + ("/row" if any(config is row for row in rows) else "/cfg"))
                if config is fail_on:
                    raise ValueError(config["run_id"])
                return real(config)
            return calls, key

        # Order of first computations is the original comprehension's order with repeats removed.
        calls, key = trace(None)
        with mock.patch.object(inputs, "_consumer_recording_key", side_effect=key):
            keys: dict[int, str] = {}
            for row in rows:
                inputs._declared_recording_matches(configs, keys, row)
        self.assertEqual(calls, ["r0/cfg", "r0/row", "r1/cfg", "r2/cfg", "r3/cfg", "r4/cfg", "r1/row", "r2/row"])
        for fail_on in (configs[0], rows[0], configs[3], rows[2]):
            with self.subTest(fail_on=fail_on["run_id"]):
                for implementation in ("reference", "hoisted"):
                    calls, key = trace(fail_on)
                    with mock.patch.object(inputs, "_consumer_recording_key", side_effect=key):
                        try:
                            if implementation == "reference":
                                self._reference(configs, rows)
                            else:
                                keys = {}
                                for row in rows:
                                    inputs._declared_recording_matches(configs, keys, row)
                        except ValueError as exc:
                            raised = str(exc)
                        else:
                            raised = None
                    if implementation == "reference":
                        expected = raised
                    else:
                        self.assertEqual(raised, expected)

    def test_empty_declaration_never_computes_the_row_key(self):
        with mock.patch.object(inputs, "_consumer_recording_key", side_effect=AssertionError) as key:
            self.assertEqual(inputs._declared_recording_matches((), {}, self._config(0)), [])
        key.assert_not_called()


# --------------------------------------------------------------------------
# inputs.block5_claim_gate_inputs(_brackets=...): reuse only an identical window
# --------------------------------------------------------------------------

class _FakeArchive:
    def __init__(self, sums_sha256):
        self.sums = sums_sha256
        self.sources_calls = 0

    def _sources(self):
        self.sources_calls += 1
        return {}

    def census(self):
        return (CensusRow("sources/SHA256SUMS", self.sums, "input_census"),)


class BracketReuseTests(unittest.TestCase):
    def _bracket(self, window, sums):
        return WindowBracket(window, "sealed", {}, 0.01, 7, "c" * 64, "no_harvest_digest", sums)

    def test_reuse_only_for_same_window_and_inventory(self):
        window = SimpleNamespace(pack="alpha", id=1)
        other = SimpleNamespace(pack="alpha", id=2)
        archive_ = _FakeArchive("a" * 64)
        same = self._bracket(window, "a" * 64)
        self.assertIs(inputs._reusable_bracket({"alpha": same}, "alpha", window, archive_), same)
        for brackets, pack in (
            (None, "alpha"), ({}, "alpha"), ({"beta": same}, "alpha"),
            ({"alpha": self._bracket(other, "a" * 64)}, "alpha"),
            ({"alpha": self._bracket(window, "b" * 64)}, "alpha"),
            ({"alpha": SimpleNamespace(**same.__dict__)}, "alpha"),
        ):
            with self.subTest(brackets=brackets, pack=pack):
                self.assertIsNone(inputs._reusable_bracket(brackets, pack, window, archive_))

    def test_inventory_problem_falls_back_to_fresh_evaluation(self):
        window = SimpleNamespace(pack="alpha")
        archive_ = _FakeArchive("a" * 64)
        archive_._sources = mock.Mock(side_effect=AnalysisRefusal("archive_input_changed"))
        self.assertIsNone(inputs._reusable_bracket({"alpha": self._bracket(window, "a" * 64)}, "alpha",
                                                   window, archive_))

    def test_gate_evaluates_only_packs_without_a_reusable_bracket(self):
        import inspect
        source = inspect.getsource(inputs.block5_claim_gate_inputs)
        self.assertIn("bracket = _reusable_bracket(_brackets, pack, window, archive)", source)
        self.assertIn("if bracket is None:\n            bracket = evaluate_window_bracket(", source)
        self.assertIsNone(inspect.signature(inputs.block5_claim_gate_inputs).parameters["_brackets"].default)


# --------------------------------------------------------------------------
# D-165 close-out: the paper-source replay reuses the inputs built in-program
# --------------------------------------------------------------------------

class CloseoutBuiltReuseTests(unittest.TestCase):
    def setUp(self):
        from scripts import run_d165_closeout_from_custody as driver
        self.driver = driver
        self.tmp = tempfile.TemporaryDirectory(prefix="d188-closeout-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve() / "custody"
        (self.root / "finalized").mkdir(parents=True)
        self.runs = Path(self.tmp.name).resolve() / "runs"
        self.runs.mkdir()
        (self.root / "finalized/prospective.json").write_bytes(b"{}\n")
        self.binding = self.root / "finalized/bracket-binding.json"
        self.binding.write_bytes(json.dumps({"runs_root": str(self.runs)}).encode())
        self.index = Path(self.tmp.name) / "window-index.json"
        self.manifest = {"lineage": {"prospective_manifest_path": "finalized/prospective.json"},
                         "evidence": {"bracket_binding": {"path": "finalized/bracket-binding.json",
                                                          "sha256": _sha(self.binding.read_bytes())}}}

    def _sources(self, built, key):
        return self.driver.CloseoutSources(self.root, self.root / "m.json", "m", "m.json", "f", "s",
                                           json.dumps(self.manifest).encode(), b"", b"", self.index,
                                           built=built, built_key=key)

    def test_key_is_the_resolved_triple(self):
        key = self.driver._block5_inputs_key(self.root, self.manifest, self.index)
        self.assertEqual(key, (self.index, (self.root / "finalized/prospective.json").resolve(), self.runs.resolve()))
        self.assertIsNone(self.driver._block5_inputs_key(self.root, self.manifest, None))

    def test_reuse_only_while_the_triple_is_equal(self):
        built = {"marker": object()}
        key = self.driver._block5_inputs_key(self.root, self.manifest, self.index)
        self.assertIs(self.driver._reusable_block5_inputs(self._sources(built, key)), built)
        self.assertIsNone(self.driver._reusable_block5_inputs(self._sources(None, key)))
        self.assertIsNone(self.driver._reusable_block5_inputs(self._sources(built, None)))
        # A different index, a changed binding (digest), a retargeted runs root: fresh build.
        other = self._sources(built, key)
        object.__setattr__(other, "window_index", Path(self.tmp.name) / "other-index.json")
        self.assertIsNone(self.driver._reusable_block5_inputs(other))
        self.binding.write_bytes(json.dumps({"runs_root": str(self.runs) + "/."}).encode())
        self.assertIsNone(self.driver._reusable_block5_inputs(self._sources(built, key)))
        link = Path(self.tmp.name).resolve() / "runs-link"
        link.symlink_to(self.runs)
        self.binding.write_bytes(json.dumps({"runs_root": str(link)}).encode())
        self.manifest["evidence"]["bracket_binding"]["sha256"] = _sha(self.binding.read_bytes())
        key = self.driver._block5_inputs_key(self.root, self.manifest, self.index)
        self.assertIs(self.driver._reusable_block5_inputs(self._sources(built, key)), built)
        other_runs = Path(self.tmp.name).resolve() / "runs-2"
        other_runs.mkdir()
        link.unlink()
        link.symlink_to(other_runs)
        self.assertIsNone(self.driver._reusable_block5_inputs(self._sources(built, key)))

    def test_paper_sources_forward_only_a_given_input(self):
        from joulewise import dominance_closeout as core
        kwargs = dict(closeout={}, finalized_manifest_bytes=b"{}", finalized_manifest_path=Path("m.json"),
                      custody_root=Path("c"), floor_artifact_bytes=b"{}", replay_sidecar_bytes=b"{}",
                      window_index=Path("i"))
        built = {"marker": 1}
        for given in (None, built):
            with self.subTest(given=given), \
                 mock.patch.object(core, "validate_finalized_analysis_manifest_v3", return_value=()) as validator, \
                 mock.patch.object(core, "_authenticate_paper_floor"), \
                 mock.patch.object(core, "validate_d165_replay_sidecar", return_value=()), \
                 mock.patch.object(core, "validate_d165_closeout", return_value=()):
                extra = {} if given is None else {"_block5_inputs": given}
                self.assertEqual(core.validate_d165_paper_sources(**kwargs, **extra), ())
                if given is None:
                    self.assertNotIn("_block5_inputs", validator.call_args.kwargs)
                else:
                    self.assertIs(validator.call_args.kwargs["_block5_inputs"], built)


# --------------------------------------------------------------------------
# hazard_refusals: no raise site, count or guard changes
# --------------------------------------------------------------------------

class HazardCensusUnchangedTests(unittest.TestCase):
    def test_arm_readiness_sites_counts_and_guards_unchanged(self):
        from tests.hazards import refusal_census
        document = refusal_census.load_allowlist()
        differences = refusal_census.differences(document)
        touched = [row for rows in differences.values() for row in rows
                   if isinstance(row, dict) and row.get("file") == "joulewise/arm_readiness.py"]
        self.assertEqual(touched, [])
        listed = {(e["function"], e["detail"]): (e["count"], e["guard"]) for e in document["sites"]
                  if e["file"] == "joulewise/arm_readiness.py" and e["function"] == "committed_pack_tree_sha256"}
        self.assertEqual(sum(count for count, _guard in listed.values()), 16)
        self.assertFalse(any(e["file"] == "joulewise/arm_readiness.py" and e["function"] == "_pack_blob_batch"
                             for e in document["sites"]))


if __name__ == "__main__":
    unittest.main()
