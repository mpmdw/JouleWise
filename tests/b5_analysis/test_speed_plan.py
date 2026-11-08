"""Post-release engineering changes: synthetic bytes and serial refusals."""
from __future__ import annotations

import hashlib
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch

from joulewise.b5_analysis import bracket as br
from joulewise.b5_analysis.windows import AnalysisRefusal
from tests.b5_analysis import fixtures_s2 as fx
from scripts import benchmark_b5_speed_plan as bench


def scan(inventory, relative):
    """The previous copy loop's complete sorted-prefix scan."""
    return (name for name in sorted(inventory) if name.startswith(relative + "/"))


class BundleInventoryTests(unittest.TestCase):
    def test_nested_and_neighboring_bundle_names_keep_exact_copy_order(self):
        names = sorted({"a/metadata.json", "a/z", "a/child/metadata.json", "a/child/x",
                        "a-/metadata.json", "aa/metadata.json", "a0/x", "empty", "z/x"})
        for bundle in ("", "a", "a/child", "a-", "aa", "missing", "z"):
            with self.subTest(bundle=bundle):
                self.assertEqual(list(bench._bundle_files(names, bundle)), list(scan(names, bundle)))

    def test_full_window_inventory_matches_previous_filter(self):
        rng = random.Random(188)
        bundles = [f"cell-{cell}/member-{member}" for cell in range(8) for member in range(60)]
        names = [bundle + f"/d{rng.randrange(8)}/file-{n}" for bundle in bundles for n in range(24)]
        names += [bundle + "/metadata.json" for bundle in bundles]
        names = sorted(set(names))
        for bundle in bundles:
            self.assertEqual(list(bench._bundle_files(names, bundle)), list(scan(names, bundle)))

    def test_prefix_checks_do_not_rescan_unrelated_members(self):
        class Counted(str):
            calls = 0

            def startswith(self, *args):
                type(self).calls += 1
                return super().startswith(*args)

        names = [Counted(f"member-{i:04d}/metadata.json") for i in range(480)]
        self.assertEqual(list(bench._bundle_files(names, "member-0240")), [names[240]])
        self.assertEqual(Counted.calls, 2)  # matching file, then the next prefix


class BracketCopyEqualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = fx.build_named("ALPHA_STD")

    def copied(self, reference):
        handle = fx.handle(self.built)
        inputs = br._Inputs(handle)
        with tempfile.TemporaryDirectory(prefix="speed-copy-") as tmp, fx.capture_adapter():
            root = Path(tmp)
            function = br._window_inputs if reference else bench.indexed_candidate(br._window_inputs)
            try:
                paths = function(handle, inputs, root)
                decision = ("ok", tuple(p.relative_to(root).as_posix() for p in paths))
            except AnalysisRefusal as exc:
                decision = ("refused", exc.code)
            digests = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in root.rglob("*") if p.is_file()}
        return decision, digests, handle.census()

    def test_every_copied_byte_selection_and_census_is_identical(self):
        before, after = self.copied(True), self.copied(False)
        self.assertEqual(before[0][0], "ok")
        self.assertTrue(before[1])
        self.assertEqual(before, after)

    def test_two_bad_sources_keep_first_refusal_and_partial_census(self):
        handle = fx.handle(self.built)
        names = sorted(name for name in handle.source_names()
                       if name.startswith("claim-runs/") and name.endswith("/metadata.json"))
        self.assertGreaterEqual(len(names), 2)
        targets = [self.built.archive / "sources" / name for name in (names[1], names[-1])]
        originals = [target.read_bytes() for target in targets]
        try:
            for target in targets:
                target.write_bytes(b"changed synthetic bytes")
            before, after = self.copied(True), self.copied(False)
            self.assertEqual(before[0], ("refused", "archive_source_unauthenticated"))
            self.assertEqual(before, after)
        finally:
            for target, raw in zip(targets, originals):
                target.write_bytes(raw)


class JoinedStep0EqualityTests(unittest.TestCase):
    def test_all_step0_output_bytes_and_records_match_serial_reader(self):
        from joulewise.b5_analysis import dry_run as d
        from joulewise.b5_analysis.archive import ArchiveHandle
        current = d.RunState.prepare_initial

        def serial_sources(handle, names):
            for name in names:
                handle.source_bytes("sources/" + name)

        def prepare_initial(state, argv):
            with patch.object(ArchiveHandle, "census_sources", serial_sources):
                return current(state, argv)

        with patch.object(bench, "baseline_function", return_value=prepare_initial):
            pair, = bench.joined_step0("synthetic-reference", 1)
        for field in ("outputs_sha256", "records_sha256"):
            self.assertEqual(pair["before"][field], pair["after"][field])
        self.assertGreater(pair["after"]["source_files"], 3000)


if __name__ == "__main__":
    unittest.main()
