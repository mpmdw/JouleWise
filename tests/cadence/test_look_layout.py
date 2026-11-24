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
from unittest import mock

from joulewise.cadence_looks import custody_pins as P, interim_release as release, manifest as M
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
                       "--verification-out", "--ledger-ref")          # audit 3, rule P3: no record source either


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


class PhysicalIdentity(unittest.TestCase):
    """Audit 3 on 4eaa14016, rule P1: paths are compared by physical identity, never by their spelling. Every
    registered root and destination refuses a symlink in any component (each one lstat'ed), and containment is
    decided by (st_dev, st_ino) ancestry. A case variant on a case-insensitive volume therefore cannot make custody,
    staging or publication overlap the repository, and custody and publication never share a physical directory.
    The repository here is a stand-in directory (``Tree``): only its place matters."""

    SID = "dev-01-s01"

    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="look-identity-")
        self.addCleanup(tmp.cleanup)
        self.base = Path(os.path.realpath(tmp.name))
        self.repo = self.base / "Tree"
        self.inside = self.repo / "Example"                 # a directory inside the repository
        (self.inside / LOOK).mkdir(parents=True)
        self.public = self.repo / "docs" / "public"         # the registered public root's place
        (self.public / LOOK).mkdir(parents=True)
        self.root = self.base / "Registered"                # a valid registered custody root
        (self.root / LOOK).mkdir(parents=True)
        self.variant = self.base / "tree"                   # the repository, spelled in another case
        self.case_insensitive = self.variant.is_dir()
        self._mini = None

    def need_case_insensitive(self):
        if not self.case_insensitive:
            self.skipTest("a case-sensitive volume: a case variant is another directory")

    def layout(self, root=None, repo=None):
        return M.LookLayout(self.repo if repo is None else repo, doc_with_root(self.root if root is None else root))

    def row(self, custody_root=None, public_root="docs/public"):
        return {"look_id": LOOK, "custody_root": str(self.root if custody_root is None else custody_root),
                "public_root": public_root}

    def fresh_root(self, name):
        made = self.base / name
        (made / LOOK).mkdir(parents=True)
        return made

    def staging_in(self, place):
        old = tempfile.tempdir
        tempfile.tempdir = str(place)
        try:
            return self.layout().private_temp("jw-identity-")
        finally:
            tempfile.tempdir = old

    def mini(self):
        """A copy of the repository with its manifest at the fixed path, draft and pinned (look_minirepo)."""
        if self._mini is None:
            from tests.cadence import look_minirepo as mr
            self._mini = mr.mini_repo(self)
        return self._mini

    def refuses(self, call, pattern, error=(M.ManifestError, ValueError)):
        with self.assertRaisesRegex(error, pattern):
            call()

    def pin_problems(self, mini):
        try:
            M.verify_pins(mini / M.INTERIM_MANIFEST_PATH, mini, allow_draft=True)
        except M.ManifestError as error:
            return error.problems
        return []

    # -- the audit's reproductions ----------------------------------------------------------------------------------

    def test_audit_3_a_case_variant_of_the_repository_is_not_a_registered_root(self):
        """Audit 3 (HIGH, directory_identity.py): LookLayout refused <repo>/Example and accepted <repo spelled in
        another case>/Example, the same physical directory."""
        self.need_case_insensitive()
        self.assertTrue(os.path.samefile(self.variant / "Example", self.inside))
        holder = self.base.with_name(self.base.name.upper())           # a case variant of a directory holding it
        (self.base / LOOK).mkdir()
        for label, root in (("the ordinary spelling", self.inside), ("the audit's case variant", self.variant / "Example"),
                            ("a case variant that holds the repository", holder)):
            with self.subTest(label):
                self.refuses(lambda: self.layout(root), "outside the repository and not hold it")
        self.refuses(lambda: self.layout(self.inside, repo=self.variant), "outside the repository")  # repo respelled
        self.assertEqual(self.layout().root, self.root)                                              # control

    def test_audit_3_custody_and_publication_never_share_a_physical_directory(self):
        """Audit 3 (HIGH, directory_identity.py): destinations() returned a RESTRICTED and a PUBLIC.json in one
        physical directory when the ledger's custody root was a case variant of the public root's directory."""
        self.need_case_insensitive()
        restricted, public = release.destinations(self.repo, self.row())                            # control
        self.assertEqual((restricted, public), (self.root / LOOK / "RESTRICTED", self.public / LOOK / "PUBLIC.json"))
        holder = self.base.with_name(self.base.name.upper())
        (self.base / LOOK).mkdir()
        for label, row in {
                "the audit's row": self.row(self.variant / "Example", "Example"),
                "custody at the public root, respelled": self.row(self.variant / "docs" / "public"),
                "custody holding the repository, respelled": self.row(holder)}.items():
            with self.subTest(label):
                self.refuses(lambda: release.destinations(self.repo, row),
                             "separate from the repository|share a physical directory")
        # physical identity decides, not the spelling: the public root spelled in another case is the repository's
        _, public = release.destinations(self.repo, self.row(public_root="DOCS/public"))
        self.assertTrue(os.path.samefile(public.parent, self.public / LOOK))

    def test_audit_3_staging_is_never_allocated_inside_the_repository(self):
        """Audit 3 (HIGH, directory_identity.py): with the temporary directory a case variant of one inside the
        repository, private_temp() returned a directory physically under the repository."""
        self.need_case_insensitive()
        for label, place in (("a directory inside the repository, respelled", self.variant / "Example"),
                             ("the registered root, respelled", self.root.with_name(self.root.name.upper()))):
            with self.subTest(label):
                self.refuses(lambda: self.staging_in(place), "inside a registered root or the repository")
        self.assertEqual(sorted(os.listdir(self.inside)), [LOOK])                 # nothing left behind
        self.assertEqual(sorted(os.listdir(self.root)), [LOOK])

    def test_audit_3_a_committed_manifest_is_never_read_through_a_link(self):
        """Audit 3 (HIGH, manifest_path_check.py): committed-mode verify_pins read the fixed manifest path through a
        symlink to identical bytes outside the repository. The manifest is now read only where it is: no link in
        any component, a regular file, and (committed) physically inside the repository."""
        from tests.cadence import look_minirepo as mr
        mini = self.mini()
        mr.commit(mini)
        registered = mini / M.INTERIM_MANIFEST_PATH
        self.assertEqual(M.verify_pins(registered, mini)["status"], "committed")                     # control
        holding = Path(tempfile.mkdtemp(dir=mini.parent))
        self.addCleanup(shutil.rmtree, holding, True)
        other = holding / "same-generated-manifest.json"
        registered.rename(other)
        registered.symlink_to(other)
        try:
            for draft in (False, True):
                with self.subTest(draft=draft):
                    self.refuses(lambda: M.verify_pins(registered, mini, allow_draft=draft),
                                 "the look manifest: a component is a symlink")
        finally:
            registered.unlink()
            other.rename(registered)
        looks = registered.parent                                     # a linked parent directory
        moved = holding / "looks"
        looks.rename(moved)
        looks.symlink_to(moved, target_is_directory=True)
        try:
            self.refuses(lambda: M.verify_pins(registered, mini), "the look manifest: a component is a symlink")
        finally:
            looks.unlink()
            moved.rename(looks)
        copy = holding / "copy.json"                                  # the same bytes outside the repository
        copy.write_bytes(registered.read_bytes())
        self.refuses(lambda: M.verify_pins(copy, mini), "the look manifest: a regular file in the repository")
        self.assertEqual(M.verify_pins(registered, mini)["status"], "committed")                     # restored

    # -- the sweep: every registered path x {symlink, case variant, inside the repository} --------------------------

    def test_sweep_a_symlink_on_any_registered_path_refuses(self):
        elsewhere = self.base / "elsewhere"
        (elsewhere / "archives").mkdir(parents=True)
        (elsewhere / "roster.json").write_bytes(b"[]\n")
        alias = self.base / "alias"
        alias.symlink_to(self.root, target_is_directory=True)

        def look_dir():
            root = self.fresh_root("linked-look")
            moved = self.base / "look-moved"
            (root / LOOK).rename(moved)
            (root / LOOK).symlink_to(moved, target_is_directory=True)
            self.layout(root)

        def span():
            (self.root / self.SID).symlink_to(elsewhere, target_is_directory=True)
            self.layout().span(self.SID)

        def fixed_file():
            (self.root / LOOK / "roster.json").symlink_to(elsewhere / "roster.json")
            self.layout().read("roster")

        def fixed_output():
            (self.root / LOOK / "stage1.json").symlink_to(elsewhere / "stage1-target.json")
            self.layout().create("stage1", b"{}\n")

        def archives():
            root = self.fresh_root("linked-archives")
            (root / LOOK / "archives").symlink_to(elsewhere / "archives", target_is_directory=True)
            for suffix in M.ARCHIVE_SUFFIXES.values():
                (elsewhere / "archives" / f"{self.SID}{suffix}").write_bytes(b"x")
            self.layout(root).archive(self.SID)

        def staging():
            link = self.base / "tmp-link"
            link.symlink_to(self.inside, target_is_directory=True)
            self.staging_in(link)

        def public_root():
            (self.repo / "docs" / "linked").symlink_to(self.public, target_is_directory=True)
            release.destinations(self.repo, self.row(public_root="docs/linked"))

        def manifest():
            mini = self.mini()
            registered = mini / M.INTERIM_MANIFEST_PATH
            target = mini.parent / (mini.name + "-manifest.json")
            self.addCleanup(lambda: target.unlink(missing_ok=True))
            registered.rename(target)
            registered.symlink_to(target)
            try:
                M.verify_pins(registered, mini, allow_draft=True)
            finally:
                registered.unlink()
                target.rename(registered)

        def pinned_code():
            mini = self.mini()
            self.assertEqual(self.pin_problems(mini), [])                                         # control
            pinned = mini / "joulewise/cadence_looks/custody_pins.py"
            target = mini.parent / (mini.name + "-pinned.py")
            self.addCleanup(lambda: target.unlink(missing_ok=True))
            pinned.rename(target)
            pinned.symlink_to(target)
            try:
                problems = self.pin_problems(mini)
            finally:
                pinned.unlink()
                target.rename(pinned)
            if any("custody_pins.py: a component is a symlink" in problem for problem in problems):
                raise ValueError("a component is a symlink")

        (self.base / "parent-link").symlink_to(self.base, target_is_directory=True)
        for label, call in {"the custody root": lambda: self.layout(alias),
                            "a parent of the custody root": lambda: self.layout(self.base / "parent-link" / "Registered"),
                            "the look's directory": look_dir, "a span directory": span,
                            "a fixed input": fixed_file, "a fixed output": fixed_output,
                            "the archives directory": archives, "the staging directory": staging,
                            "the ledger's custody root": lambda: release.destinations(self.repo, self.row(alias)),
                            "the public root": public_root, "the look manifest": manifest,
                            "a pinned code file": pinned_code}.items():
            with self.subTest(label):
                self.refuses(call, "symlink|inside a registered root or the repository")

    def test_sweep_a_case_variant_on_any_registered_path_is_decided_by_physical_identity(self):
        """Where a path must lie outside the repository, a case variant that lands inside it refuses; where a fixed
        name is meant, a differently-cased name refuses; where a path must lie inside the repository (the public
        root, the manifest), a case variant is the same physical place and is that place."""
        self.need_case_insensitive()
        from tests.cadence import look_minirepo as mr

        def look_dir():
            root = self.fresh_root("cased-look")
            (root / LOOK).rename(root / LOOK.upper())
            self.layout(root)

        def span():
            (self.root / self.SID.upper()).mkdir()
            self.layout().span(self.SID)

        def fixed_file():
            (self.root / LOOK / "Roster.JSON").write_bytes(b"[]\n")
            self.layout().read("roster")

        def archives():
            root = self.fresh_root("cased-archives")
            (root / LOOK / "ARCHIVES").mkdir()
            self.layout(root).archive(self.SID)

        for label, call in {
                "the custody root": lambda: self.layout(self.variant / "Example"),
                "the look's directory": look_dir, "a span directory": span, "a fixed input": fixed_file,
                "the archives directory": archives,
                "the staging directory": lambda: self.staging_in(self.variant / "Example"),
                "the ledger's custody root": lambda: release.destinations(self.repo, self.row(self.variant / "Example")),
                "the ledger's custody root at the public root": lambda: release.destinations(
                    self.repo, self.row(self.variant / "docs" / "public"))}.items():
            with self.subTest(label):
                self.refuses(call, "outside the repository|separate from the repository|share a physical directory|"
                                   "differ only in case|inside a registered root or the repository")
        # inside the repository by design: the respelled place is the place
        _, public = release.destinations(self.repo, self.row(public_root="DOCS/public"))
        self.assertTrue(os.path.samefile(public.parent, self.public / LOOK))
        mini = self.mini()
        mr.commit(mini)
        respelled = mini.with_name(mini.name.upper()) / M.INTERIM_MANIFEST_PATH
        self.assertTrue(os.path.samefile(respelled, mini / M.INTERIM_MANIFEST_PATH))
        self.assertEqual(M.verify_pins(respelled, mini), M.verify_pins(mini / M.INTERIM_MANIFEST_PATH, mini))

    def test_sweep_a_place_inside_the_repository_refuses_on_any_registered_path(self):
        """Every private path physically inside the repository refuses (or holding it), every path the repository
        must hold refuses outside it."""
        (self.base / LOOK).mkdir()
        repo_file = self.inside / "roster.json"
        repo_file.write_bytes(b"[]\n")

        def through_a_link(make):
            def call():
                root = self.fresh_root(f"into-repo-{len(os.listdir(self.base))}")
                make(root)
                layout = self.layout(root)
                if os.path.lexists(root / self.SID):
                    layout.span(self.SID)
                if os.path.lexists(root / LOOK / "roster.json"):
                    layout.read("roster")
                layout.archive(self.SID)
            return call

        def manifest():
            mini = self.mini()
            outside = mini.parent / (mini.name + "-outside.json")
            self.addCleanup(lambda: outside.unlink(missing_ok=True))
            outside.write_bytes((mini / M.INTERIM_MANIFEST_PATH).read_bytes())
            M.verify_pins(outside, mini)

        def pinned_code():
            mini = self.mini()
            registered = mini / M.INTERIM_MANIFEST_PATH
            kept = registered.read_bytes()
            doc = json.loads(kept)
            doc["fit"]["code"][0]["path"] = "../outside.py"
            registered.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            try:
                problems = self.pin_problems(mini)
            finally:
                registered.write_bytes(kept)
            if problems:
                raise ValueError("a pinned path outside the repository: " + "; ".join(problems))

        for label, call in {
                "the custody root": lambda: self.layout(self.inside),
                "a custody root holding the repository": lambda: self.layout(self.base),
                "the look's directory, reached into the repository": through_a_link(
                    lambda root: ((root / LOOK).rmdir(), (root / LOOK).symlink_to(self.inside / LOOK, True))),
                "a span directory, reached into the repository": through_a_link(
                    lambda root: (root / self.SID).symlink_to(self.inside, True)),
                "a fixed input, reached into the repository": through_a_link(
                    lambda root: (root / LOOK / "roster.json").symlink_to(repo_file)),
                "the archives directory, reached into the repository": through_a_link(
                    lambda root: (root / LOOK / "archives").symlink_to(self.inside, True)),
                "the staging directory": lambda: self.staging_in(self.inside),
                "the staging directory in the registered root": lambda: self.staging_in(self.root),
                "the ledger's custody root": lambda: release.destinations(self.repo, self.row(self.inside)),
                "a ledger custody root holding the repository": lambda: release.destinations(
                    self.repo, self.row(self.base)),
                "the public root outside the repository": lambda: release.destinations(
                    self.repo, self.row(public_root=str(self.base / "Registered"))),
                "the public root above the repository": lambda: release.destinations(
                    self.repo, self.row(public_root="../Registered")),
                "the look manifest outside the repository": manifest,
                "a pinned code file outside the repository": pinned_code}.items():
            with self.subTest(label):
                self.refuses(call, "symlink|outside the repository|separate from the repository|inside a registered "
                                   "root or the repository|canonical repository directory|a regular file in the "
                                   "repository|outside the repository|pinned path outside")


# Audit 3 (MED), rule P4: every key of stage1.json that may carry a float, from its schema (52 typed "number", two
# float constants). The file is private: it is written only at <registered root>/lm-interim-01/stage1.json, and
# only its sha256 is public. Whether RL-194a's "public census" means the file itself is a question for the research
# lead (NEEDS_SPEC in docs/run_reports/2026-11-21-pr795-audit-3.md); this list is what would have to change.
STAGE1_FLOAT_KEYS = (
    "active_readings.fan_rpm.tolerance", "active_readings.tf08_c.tolerance", "active_readings.tv0h_excess_c.tolerance",
    "calibrated_range.fan_rpm", "calibrated_range.tf08_c", "calibrated_range.tv0h_excess_c",
    "centring.fan_rpm", "centring.tf08_c", "centring.tv0h_excess_c",
    "legs.load_s", "legs.prefix_tails.first_token_s", "legs.prefix_tails.u_s", "legs.prefix_tails.v_s",
    "legs.prefix_tails.wall_end_s", "legs.prefix_tails.wall_start_s", "legs.segments.first_token_s",
    "legs.segments.u_s", "legs.segments.v_s", "legs.segments.wall_end_s", "legs.segments.wall_start_s",
    "legs.start.fan_rpm", "legs.start.tf08_c", "legs.start.tv0h_excess_c", "legs.start.z",
    "legs.state.censored_at_s", "legs.state.first_off_s", "legs.state.unobserved_at_s", "legs.t_p_s", "legs.tau_hat_s",
    "legs.trace_holes.dc_in.clock_fit_excess_s", "legs.trace_holes.dc_in.max_gap_s", "legs.trace_holes.gpu_rail.max_gap_s",
    "meter_clock.max_abs_s", "meter_clock.spans.*.end_minus_header_s", "meter_clock.threshold_s",
    "onset.coefficients.*", "onset.count_only_cut.fixed_s", "onset.count_only_cut.offset_s",
    "onset.lodo.per_day_rms_s.*", "onset.lodo.rms_s", "onset.sigma_s",
    "rates.per_cell.10000.r_d", "rates.per_cell.10000.r_p", "rates.per_cell.19458.r_d", "rates.per_cell.19458.r_p",
    "rates.per_cell.2000.r_d", "rates.per_cell.2000.r_p", "rates.r_d", "rates.r_p",
    "roster.spans.custody.meter_streams.clock_fit_excess_s", "roster.spans.custody.meter_streams.clock_rate_ppm",
    "roster.spans.soak_reference_tv0h_c", "roster.spans.t0_epoch_s", "tripwires.start_reading_invalid_over_10pct.value")


def schema_float_keys(schema):
    """Each property path of a JSON schema whose value may be a float: typed "number", or a float constant."""
    defs = {**schema.get("$defs", {}), **schema.get("definitions", {})}
    found = set()

    def walk(node, path, depth=0):
        if depth > 60 or not isinstance(node, dict):
            return
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith(("#/$defs/", "#/definitions/")):
            node = defs[ref.rsplit("/", 1)[1]]
        kinds = node.get("type") if isinstance(node.get("type"), list) else [node.get("type")]
        constants = [node["const"]] if "const" in node else list(node.get("enum") or [])
        if "number" in kinds or any(isinstance(value, float) for value in constants):
            found.add(path)
        for key in ("oneOf", "anyOf", "allOf"):
            for sub in node.get(key, []):
                walk(sub, path, depth + 1)
        for key, sub in node.get("properties", {}).items():
            walk(sub, f"{path}.{key}" if path else key, depth + 1)
        for sub in [node.get("additionalProperties"), *node.get("patternProperties", {}).values()]:
            if isinstance(sub, dict):
                walk(sub, f"{path}.*", depth + 1)
        if isinstance(node.get("items"), dict):
            walk(node["items"], path, depth + 1)
    walk(schema, "")
    return found


class PublicFiles(unittest.TestCase):
    """Audit 3 (MED), rule P4; RL-179 row 26: a public file of the look carries listed words, hashes, counts and
    identifiers, and no float."""

    LOOKS = REPO / "docs/process/cadence/looks"

    def test_the_public_report_s_schema_admits_no_float(self):
        schema = json.loads((self.LOOKS / "lm-interim-01.output.schema.json").read_text(encoding="utf-8"))
        self.assertIs(schema.get("additionalProperties"), False)                # closed: no field beside these
        self.assertEqual(schema_float_keys(schema), set())
        kinds = set()

        def walk(node):
            if isinstance(node, dict):
                kinds.update(node["type"] if isinstance(node.get("type"), list) else [node.get("type")])
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for value in node:
                    walk(value)
        walk(schema)
        self.assertLessEqual(kinds - {None}, {"object", "string", "integer"})

    def test_the_public_ledger_carries_no_float(self):
        def floats(node, path="$"):
            if isinstance(node, float):
                yield path
            elif isinstance(node, dict):
                for key, value in node.items():
                    yield from floats(value, f"{path}.{key}")
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    yield from floats(value, f"{path}[{index}]")
        ledger = json.loads((self.LOOKS / "LOOKS.json").read_text(encoding="utf-8"))
        self.assertEqual(list(floats(ledger)), [])
        for key in M.LOOK_ROW_HASHES:                    # what a later status adds to the row: sha256 hashes only
            self.assertTrue(key.endswith("sha256"), key)

    def test_stage_1_s_file_is_private_and_its_floats_are_listed(self):
        """stage1.json may carry floats (STAGE1_FLOAT_KEYS, from its schema); it is written only in the look's private
        directory under the registered root, physically outside the repository, and only its sha256 is public."""
        schema = json.loads((self.LOOKS / "lm-interim-01.stage1.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(sorted(schema_float_keys(schema)), sorted(STAGE1_FLOAT_KEYS))
        tmp = Path(os.path.realpath(tempfile.mkdtemp(prefix="look-public-")))
        self.addCleanup(shutil.rmtree, tmp, True)
        (tmp / LOOK).mkdir()
        layout = M.LookLayout(REPO, doc_with_root(tmp))
        for key in M.LOOK_FILES:                         # stage 1's file among every fixed file: private, outside
            path = layout.file(key)
            self.assertEqual(path.parent, layout.look)
            self.assertFalse(release.physically_within(path.parent, REPO))
        self.assertEqual(M.LOOK_FILES["stage1"], "stage1.json")


@unittest.skipIf(R is None, "numpy is not installed")
class CommandLine(unittest.TestCase):
    def help_options(self, command):
        done = subprocess.run([sys.executable, "-I", "-B", str(REPO / "scripts/cadence_look_run.py"), command, "--help"],
                              capture_output=True, text=True, timeout=300)
        self.assertEqual(done.returncode, 0, done.stderr)
        return set(re.findall(r"(?<![\w-])--[a-z0-9-]+", done.stdout)), done.stdout

    def test_no_command_takes_a_path(self):
        """Audit 2, lead ruling: the CLI accepts no path option. Every former one is unrecognized, and the options
        each command still takes carry a flag, a sha256 or a leg key. Audit 3, rule P3: nor a git ref (a committed
        run reads public records from origin/main after a fetch)."""
        expected = {"stage1": {"--help", "--level-r", "--stage-archives", "--ruled-exclusion", "--allow-draft"},
                    "stage2": {"--help", "--stage1-sha256", "--level-e", "--allow-draft"},
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
        root, repo = tmp / "root", tmp / "repo"
        (root / LOOK).mkdir(parents=True)
        public_dir = repo / M.LOOK_PUBLIC_ROOT / LOOK
        public_dir.mkdir(parents=True)
        layout = M.LookLayout(repo, doc_with_root(root))
        row = {"look_id": LOOK, "execution_host": "hw1:" + "a" * 64, "custody_root": str(root),
               "public_root": M.LOOK_PUBLIC_ROOT, "holds_cleared": {}}
        stage1 = {flag.split(".")[0]: {} for flag in M.STAGE2_HOLD_FLAGS["interim"]}
        with mock.patch.object(R, "ROOT", repo), mock.patch.object(R.M, "execution_host", return_value=row["execution_host"]):
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

    def test_stage2_execution_preflight_refuses_an_unlisted_root_before_probes(self):
        row = {"look_id": LOOK, "public_root": "docs/public"}
        with mock.patch.object(R.M, "execution_host", side_effect=AssertionError("unexpected host probe")):
            with self.assertRaisesRegex(R.F.LookInputError, "allowed public root.*docs/public"):
                R.validate_execution_row(row, None, None)


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
        another named span, and when a readback of the same span's manifest differed by one hex digit. Audit 3 (HIGH):
        and with the readback's label after the noun, or the pin printed only under another label."""
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
            # audit 3, rule P2: a contradicting readback in the other word order, a pending digest with the pin under
            # another label, and an abbreviation alone each hold the span at the stage too
            "audit 3: a readback labelled after the noun": f"Offload manifest `{digest}`. Offload manifest readback: "
                                                           f"`{wrong}`.",
            "audit 3: pending, the pin under the look manifest's label": f"Offload manifest pending. Look manifest: "
                                                                          f"`{digest}`.",
            "audit 3: only an abbreviation": f"Offload manifest `{digest[:8]}…{digest[-4:]}`.",
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
