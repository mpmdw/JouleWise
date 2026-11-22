"""Audit 2 on 98fedf875: the executor takes no path. Every file is a fixed name under the one root the manifest
registers (``manifest.LookLayout``); staging is private; names are compared case-insensitively; the pin list is the
manifest's; a Check binds by span. Each audit reproduction is a test here or beside the code it is about. Every byte
is generated."""
from __future__ import annotations

import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

from joulewise.cadence_looks import custody_pins as P, manifest as M
from tests.cadence import custody_pin_fixture as PF

try:
    from scripts import cadence_look_run as R
    from tests.cadence import test_look_run as TLR
except ModuleNotFoundError as exc:                    # the executor imports numpy; the layout's own tests do not
    if exc.name != "numpy":
        raise
    R = TLR = None

REPO = Path(__file__).resolve().parents[2]
LOOK = M.INTERIM_LOOK_ID
FORMER_PATH_OPTIONS = ("--out", "--manifest", "--input", "--roster", "--custody", "--rules-3-4", "--span-dir",
                       "--write-input", "--staging-root", "--superseded-stage1", "--superseded-input",
                       "--custody-pins", "--run-state", "--stage1", "--energy", "--looks", "--twin",
                       "--verification-out")


def doc_with_root(root):
    doc = json.loads((REPO / M.INTERIM_MANIFEST_PATH).read_text(encoding="utf-8"))
    doc["custody"]["root"] = str(root)
    return doc


class Layout(unittest.TestCase):
    """The fixed places, and every check made before a path is used."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="look-layout-")
        self.addCleanup(tmp.cleanup)
        self.base = Path(os.path.realpath(tmp.name))
        self.root = self.base / "root"
        (self.root / LOOK).mkdir(parents=True)

    def layout(self, root=None):
        return M.LookLayout(REPO, doc_with_root(self.root if root is None else root))

    def test_every_path_is_the_registered_root_and_the_look_id(self):
        layout = self.layout()
        self.assertEqual((layout.root, layout.look), (self.root, self.root / LOOK))
        self.assertEqual(layout.span("dev-01-s01"), self.root / "dev-01-s01")
        self.assertEqual({key: layout.file(key).relative_to(self.root).as_posix() for key in M.LOOK_FILES},
                         {key: f"{LOOK}/{name}" for key, name in M.LOOK_FILES.items()})
        self.assertEqual(layout.create("stage1", b"{}\n"), PF.custody_pins.pin_list_sha256(b"{}\n"))
        self.assertEqual(layout.read("stage1"), b"{}\n")
        with self.assertRaisesRegex(M.ManifestError, "never replaced"):     # created once
            layout.create("stage1", b"other\n")
        self.assertEqual(layout.read("stage1"), b"{}\n")

    def test_the_root_is_registered_absolute_canonical_and_outside_the_repository(self):
        cases = {"no root": None, "a relative root": "relative/root", "an unnormalized root": str(self.root) + "/../root",
                 "the repository": str(REPO), "inside the repository": str(REPO / "docs"),
                 "a root that holds the repository": str(REPO.parent), "an absent root": str(self.base / "absent")}
        for label, root in cases.items():
            with self.subTest(label), self.assertRaises(M.ManifestError):
                M.LookLayout(REPO, doc_with_root(root) if root else dict(doc_with_root("x"), custody=dict(
                    doc_with_root("x")["custody"], root=None)))
        shutil.rmtree(self.root / LOOK)
        with self.assertRaisesRegex(M.ManifestError, "private directory"):
            self.layout()

    def test_a_symlink_anywhere_on_a_path_refuses(self):
        """Audit 2 (HIGH): stage 2 followed --span-dir paths through a linked parent, reserved the look and published.
        No path is supplied now, and every derived path is refused if any component is a link: the root, a parent
        of the root, the look's directory, a span, a fixed file."""
        alias = self.base / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(M.ManifestError, "symlink"):
            self.layout(alias)                                      # the root itself is a link
        parent = self.base / "parent-link"
        parent.symlink_to(self.base, target_is_directory=True)
        with self.assertRaisesRegex(M.ManifestError, "symlink"):
            self.layout(parent / "root")                            # a parent of the root is a link
        layout = self.layout()
        (self.base / "elsewhere").mkdir()
        (self.root / "dev-01-s01").symlink_to(self.base / "elsewhere", target_is_directory=True)
        with self.assertRaisesRegex(M.ManifestError, "symlink"):
            layout.span("dev-01-s01")
        (self.base / "roster-elsewhere.json").write_bytes(b"[]\n")
        (self.root / LOOK / "roster.json").symlink_to(self.base / "roster-elsewhere.json")
        with self.assertRaisesRegex(M.ManifestError, "symlink"):
            layout.read("roster")
        with self.assertRaisesRegex(M.ManifestError, "symlink"):
            layout.file("roster")
        moved = self.base / "look-elsewhere"
        (self.root / LOOK).rename(moved)
        (self.root / LOOK).symlink_to(moved, target_is_directory=True)
        with self.assertRaisesRegex(M.ManifestError, "symlink"):
            self.layout()

    def test_names_that_differ_only_in_case_collide(self):
        """Audit 2 (HIGH): on a case-insensitive volume ``--out public.json`` wrote the stage-1 census as the
        reserved PUBLIC.json. Stage 1 writes only fixed names in the look's private directory, and a name beside one
        of them that differs only in case refuses, on any volume."""
        layout = self.layout()
        (self.root / LOOK / "Stage1.JSON").write_bytes(b"x")
        with self.assertRaisesRegex(M.ManifestError, "differ only in case"):
            layout.create("stage1", b"{}\n")
        with self.assertRaisesRegex(M.ManifestError, "differ only in case"):
            layout.read("stage1")
        (self.root / "DEV-01-S01").mkdir()
        with self.assertRaisesRegex(M.ManifestError, "differ only in case"):
            layout.span("dev-01-s01")
        for name in ("public.json", "PUBLIC.json", "restricted", LOOK.upper()):
            with self.subTest(name), self.assertRaises(M.ManifestError):
                layout.span(name)                                   # the reservation's names are never a span's
        self.assertEqual(M.name_collision(self.root / LOOK, "stage1.json"), "Stage1.JSON")
        self.assertIsNone(M.name_collision(self.root / LOOK, "level_r.json"))

    def test_staging_is_private_and_outside_every_registered_root_and_the_repository(self):
        """Audit 2 (HIGH): with the registered public directory as --staging-root, stage 1 left a raw trace there.
        The staging directory is made fresh by the stage, outside the root and the repository (where the public
        roots are)."""
        layout = self.layout()
        made = layout.private_temp("jw-look-staging-test-")
        self.addCleanup(shutil.rmtree, made, True)
        self.assertEqual(Path(os.path.realpath(made)), made)
        for other in (self.root, REPO):
            self.assertFalse(made == other or made.is_relative_to(other) or other.is_relative_to(made))
        self.assertEqual(list(made.iterdir()), [])
        old = tempfile.tempdir
        tempfile.tempdir = str(self.root)                           # a temporary directory inside the root refuses
        try:
            with self.assertRaisesRegex(M.ManifestError, "inside a registered root"):
                layout.private_temp("jw-look-staging-test-")
        finally:
            tempfile.tempdir = old
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), [LOOK])


@unittest.skipIf(R is None, "numpy is not installed")
class CommandLine(unittest.TestCase):
    def help_options(self, command):
        done = subprocess.run([sys.executable, "-I", "-B", str(REPO / "scripts/cadence_look_run.py"), command, "--help"],
                              capture_output=True, text=True, timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        return set(re.findall(r"(?<![\w-])--[a-z0-9-]+", done.stdout)), done.stdout

    def test_no_command_takes_a_path(self):
        """Audit 2, lead ruling: the CLI accepts no path option. Every former one is unrecognized, and the options
        each command still takes carry a flag, a git ref, a sha256 or a leg key."""
        expected = {"stage1": {"--help", "--level-r", "--stage-archives", "--ruled-exclusion", "--ledger-ref",
                               "--allow-draft"},
                    "stage2": {"--help", "--stage1-sha256", "--level-e", "--ledger-ref", "--allow-draft"},
                    "post-no-maxima": {"--help"}, "host-id": {"--help"}}
        for command, options in expected.items():
            found, text = self.help_options(command)
            with self.subTest(command):
                self.assertEqual(found, options)
        # no former option is taken as an abbreviation of a remaining one (``--stage1`` is not ``--stage1-sha256``)
        for command in ("stage1", "stage2", "post-no-maxima"):
            for option in FORMER_PATH_OPTIONS:
                with self.subTest(command=command, option=option):
                    done = subprocess.run([sys.executable, "-I", "-B", str(REPO / "scripts/cadence_look_run.py"),
                                           command, option, "/tmp/x", "--stage1-sha256", "0" * 64],
                                          capture_output=True, text=True, timeout=300)
                    self.assertEqual(done.returncode, 2)
                    self.assertIn(f"unrecognized arguments: {option}", done.stderr)

    def test_the_reservation_s_names_refuse_a_differently_cased_file_beside_them(self):
        """Audit 2 (HIGH): a stage-1 file at public.json occupied PUBLIC.json on a case-insensitive volume and the
        next execution refused with no reservation taken. Stage 2 now refuses, before reserving, any file beside
        the reservation's names that differs from them only in case."""
        tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="look-names-")))
        self.addCleanup(shutil.rmtree, tmp, True)
        root, public_rel = tmp / "root", str(tmp / "public")        # an absolute public root: nothing in the repo
        (root / LOOK).mkdir(parents=True)
        layout = M.LookLayout(REPO, doc_with_root(root))
        public_dir = tmp / "public" / LOOK
        public_dir.mkdir(parents=True)
        row = {"look_id": LOOK, "execution_host": "hw1:" + "a" * 64, "custody_root": str(root),
               "public_root": public_rel, "holds_cleared": {}}
        stage1 = {flag.split(".")[0]: {} for flag in M.STAGE2_HOLD_FLAGS["interim"]}
        real_host = R.M.execution_host
        R.M.execution_host = lambda: "hw1:" + "a" * 64
        try:
            R.validate_execution_row(row, stage1, layout)                # nothing beside them: admitted
            for parent, name in ((public_dir, "public.json"), (root / LOOK, "restricted")):
                try:
                    (parent / name).write_bytes(b"x")
                except PermissionError:         # a host policy that forbids the reservation's name (see synthetic_
                    continue                    # reservation_name in look_minirepo) forbids its variants too
                with self.subTest(name), self.assertRaisesRegex(R.F.LookInputError, "differs from it only in case"):
                    R.validate_execution_row(row, stage1, layout)
                (parent / name).unlink()
            with self.assertRaisesRegex(R.F.LookInputError, "not the root the manifest registers"):
                R.validate_execution_row(dict(row, custody_root=str(tmp)), stage1, layout)
        finally:
            R.M.execution_host = real_host


@unittest.skipIf(R is None, "numpy is not installed")
class Stages(unittest.TestCase):
    """The reproductions at the command line, on generated custody."""

    def setUp(self):
        shared = TLR._Custody.get()
        tmp = tempfile.TemporaryDirectory(prefix="look-layout-cli-")
        self.addCleanup(tmp.cleanup)
        self.tmp = Path(os.path.realpath(tmp.name))
        self.root = self.tmp / "custody"
        shutil.copytree(shared.root, self.root)
        self.roster, self.rules = self.root / "roster.json", self.root / "rules_3_4.json"
        self.ids = [span["span_id"] for span in json.loads(self.roster.read_bytes())]

    def stage1(self, *extra, **kwargs):
        out = self.tmp / f"stage1-{len(list(self.tmp.iterdir()))}.json"
        rc, _, err = TLR.run_cli(["stage1", "--roster", self.roster, "--custody", self.root, "--rules-3-4", self.rules,
                                  "--out", out, *extra], **kwargs)
        return rc, err, out

    def test_stage_1_writes_only_its_two_fixed_files_in_the_look_s_private_directory(self):
        rc, err, out = self.stage1()
        self.assertEqual(rc, 0, err)
        from tests.cadence import look_layout_fixture as LF
        roots = [root for root in LF._ROOTS.values() if (root / LOOK / "stage1.json").is_file()]
        self.assertTrue(roots)
        written = sorted(path.name for path in (roots[-1] / LOOK).iterdir())
        self.assertEqual(written, ["level_r.json", "roster.json", "rules_3_4.json", "stage1.json"])
        self.assertEqual(out.read_bytes(), (roots[-1] / LOOK / "stage1.json").read_bytes())

    def test_a_check_that_names_another_span_s_manifest_or_contradicts_itself_holds_the_span(self):
        """Audit 2 (HIGH): check-inputs and committed stage 1 exited 0 when the only matching digest belonged to
        another named span, and when a readback of the same span's manifest differed by one hex digit."""
        doc = PF.synthetic_pins({sid: self.root / sid for sid in self.ids})
        span = doc["spans"][0]
        digest, sid = span["offload_manifest_sha256"], span["span_id"]
        wrong = digest[:-1] + ("a" if digest[-1] != "a" else "b")
        head = f"{span['check_item']}. **Check of {sid} (generated).** "
        cases = {
            "only another span's digest": "Copy complete, digest pending. Separate offload for f2-inst-01-s01: "
                                          f"manifest `{digest}`.",
            "a readback that differs": f"Offload manifest `{digest}`. Readback of the same offload manifest `{wrong}`.",
            "the wrong digest alone": f"Offload manifest `{wrong}`.",
        }
        original = PF.run_state(doc)
        line = next(text for text in original.splitlines() if text.startswith(head))
        for label, body in cases.items():
            state = self.tmp / f"RUN_STATE-{len(list(self.tmp.iterdir()))}.md"
            state.write_text(original.replace(line, head + body), encoding="utf-8")
            with self.subTest(label):
                self.assertTrue(any(problem.startswith(sid) and "held" in problem
                                    for problem in P.check_chain_problems(doc, state.read_text())))
                rc, err, out = self.stage1("--run-state", state)
                self.assertEqual(rc, 2, err)
                self.assertIn(f"custody pins: {sid}: Check item", err)
                self.assertFalse(out.exists())

    def test_archive_staging_leaves_nothing_in_any_registered_or_public_place(self):
        """Audit 2 (HIGH): the registered public look directory as --staging-root received a byte-identical raw
        trace. With no staging path the archive is expanded into a private directory that is gone when the stage
        ends; the registered root holds only the archive and the look's fixed files, and no trace is expanded."""
        box = self.tmp / "staging-inputs"
        box.mkdir()
        member = "legs/L001/runtime/run/power_trace.csv"
        sid, archive, manifest, marker = TLR.Staging().pack(box, {member: b"timestamp_s,power_w\n1,5.0\n",
                                                                   "runner_receipt.json": b"{}\n"})
        plan = box / "plan.json"
        plan.write_text(json.dumps([dict(span_id=sid, archive=str(archive), manifest=str(manifest), marker=str(marker))]))
        roster, rules = box / "roster.json", box / "rules.json"
        roster.write_text(json.dumps([{"span_id": sid}]))
        rules.write_text("{}")
        requested = self.tmp / "public" / LOOK                   # a former --staging-root; it is never made
        before = set(os.listdir(tempfile.gettempdir()))
        rc, _, err = TLR.run_cli(["stage1", "--custody", box / "copy", "--roster", roster, "--rules-3-4", rules,
                                  "--out", self.tmp / "staged-stage1.json", "--stage-archives", plan,
                                  "--staging-root", requested])
        self.assertFalse(requested.exists())
        leftovers = {name for name in set(os.listdir(tempfile.gettempdir())) - before
                     if name.startswith("jw-look-staging-")}
        self.assertEqual(leftovers, set())                        # the private staging directory is removed
        from tests.cadence import look_layout_fixture as LF
        root = next(root for key, root in LF._ROOTS.items() if key[1] == os.path.realpath(box / "copy"))
        self.assertFalse(list(root.rglob("power_trace.csv")), err)            # never expanded under the root
        self.assertFalse((root / sid).exists())
        self.assertEqual(sorted(path.name for path in (root / LOOK / "archives").iterdir()),
                         sorted(f"{sid}{suffix}" for suffix in M.ARCHIVE_SUFFIXES.values()))
        self.assertIn(rc, (0, 2), err)                            # admitted or refused by the generated receipt
        self.assertNotIn("staging:", err)


if __name__ == "__main__":
    unittest.main()
