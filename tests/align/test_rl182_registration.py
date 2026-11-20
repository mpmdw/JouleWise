"""Verify PR #813 against the verbatim RL-182 §1.3 and RL-176 §D excerpts."""

import ast
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

from tests.git_fixture import init_git_fixture


ROOT = Path(__file__).resolve().parents[2]
FIXTURES = Path(__file__).with_name("fixtures") / "rl182"
EVIDENCE = ROOT / "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign"
POWER_SCRIPT = EVIDENCE / "rl178-cells/power_table.py"


class RegistrationEditsTests(unittest.TestCase):
    def test_each_of_the_seventeen_edits_appears_once_at_each_ruled_location(self):
        # Edits copied from audit 7ec51b1d9, matched-control clauses from 61377dc45.
        chunks = re.split(r"(?m)^\*\*E(\d+)\. ", (FIXTURES / "edits.md").read_text())
        edits = dict(zip(map(int, chunks[1::2]), chunks[2::2]))
        self.assertEqual(list(edits), list(range(1, 18)))

        def quoted(number):
            return re.findall(r'"([^"\n]+)"', edits[number])

        def block(number):
            return "\n".join(line.removeprefix("> ").removeprefix(">") for line in
                             edits[number].splitlines() if line.startswith(">"))

        p4 = (ROOT / "docs/align/pilot_protocol_v4.md").read_text()
        am = (EVIDENCE / "r1-ready-1116/AMENDMENT-R1-DRAFT.md").read_text()
        dv = (ROOT / "docs/align/v4/DEVIATIONS.md").read_text()
        scorer = (ROOT / "joulewise/align/apple/rl176.py").read_text()

        b2, remainder = p4.split("**B2. S,", 1)[1].split("**B2a.", 1)
        b2 = "**B2. S," + b2
        b2a = remainder.split("\n\n", 1)[0]
        am_score = am.split("### S score\n", 1)[1].split("\n### RL-178", 1)[0]
        row = next(line for line in dv.splitlines() if line.startswith("| RL176-B-S-admit |"))
        transfer = next(line for line in am.splitlines() if line.startswith("| 14 |"))
        control_lines = (FIXTURES / "matched-control.md").read_text().strip().splitlines()
        trigger = control_lines[0].split("** Under a null", 1)[0] + "**"
        heading = re.search(r"headed (\*Matched control .*?\*)", edits[13])[1]
        control = f"{heading}\n\n{trigger}\n\n" + "\n".join(control_lines[3:7])
        digest = hashlib.sha256(POWER_SCRIPT.read_bytes()).hexdigest()

        checks = {
            1: [(b2, passage) for passage in quoted(1)],
            2: [(b2, block(2)), (am_score, block(2))],
            3: [(b2, "in rational arithmetic. " + block(3))],
            4: [(b2, quoted(4)[0].rstrip("…")), (b2, "to about 11 %" + quoted(4)[2])],
            5: [(b2, "`docs/align/v4/claim-b-power.json`. "
                 + quoted(5)[0].replace("‹the builder prints it›", digest))],
            6: [(b2a, block(6))],
            7: [(b2, block(7))],
            8: [(b2, quoted(8)[0])],
            9: [(b2, block(9)), (am, block(9)), (am, quoted(9)[0])],
            10: [(b2a, quoted(10)[0].lstrip("…") + quoted(10)[1].rstrip("…")),
                 (b2a, quoted(10)[2].lstrip("…") + "."),
                 (b2a, quoted(10)[3].lstrip("…") + quoted(10)[4])],
            11: [(p4.split("**B9.", 1)[1], quoted(11)[0].strip("…"))],
            12: [(p4, passage) for passage in quoted(12)],
            13: [(b2, control), (am, control)],
            14: [(am, quoted(14)[0] + "\n\n## G."),
                 (am, quoted(14)[1].lstrip("…")),
                 (am, f"({quoted(14)[4]})."),
                 (am, f"Amendment {quoted(14)[4]}."),
                 (am_score, block(2))],
            15: [(row, " | " + block(15) + " |")],
            16: [(scorer, 'raise ValueError("sabotage-instructed member carries a DC-in trace")')],
            17: [(transfer, quoted(17)[0])],
        }
        self.assertEqual(checks.keys(), edits.keys())
        for number, checks_for_edit in checks.items():
            for location, passage in checks_for_edit:
                with self.subTest(edit=f"E{number}", passage=passage):
                    self.assertEqual(location.count(passage), 1)
        self.assertNotIn("W1_PYDANTIC_VERSION", p4 + am)
        self.assertNotIn("B2a's Q planning reference uses the original", p4)
        self.assertNotIn("subject to cold review", am)
        self.assertNotIn("awaits the research lead's cold review", am.replace("\n", " "))
        self.assertEqual(row.strip("| ").split(" | ")[2], block(15))

    def test_rl182a_first_token_stamp_text_matches_in_protocol_and_amendment(self):
        source = (FIXTURES / "addendum.md").read_text()
        self.assertEqual(re.findall(r"(?m)^- \*\*([^*]+)\*\*", source), [
            "E2, first bullet (P4:1188).", "E10 (P4:1283).", "AM:47.",
        ])
        score, outcome, old_am, wording = re.findall(r'"([^"]+)"', source)
        p4 = (ROOT / "docs/align/pilot_protocol_v4.md").read_text()
        am = (EVIDENCE / "r1-ready-1116/AMENDMENT-R1-DRAFT.md").read_text()
        for doc in (p4, am):
            self.assertEqual(doc.count("- " + score), 1)
            self.assertEqual(doc.count(outcome.lstrip("…")), 1)
            self.assertNotIn("first stamped token", doc)
        self.assertEqual(am.count(wording), 1)
        self.assertNotIn(old_am, am)

    def test_rl185_e18_and_e19_each_match_once_in_their_ruled_section(self):
        # RL-185 §§2.1–2.2 copied from audit b9e46ef52.
        source = (FIXTURES / "rl185.md").read_text()
        p4 = (ROOT / "docs/align/pilot_protocol_v4.md").read_text()
        for edit, anchor, start, end in (
            ("E18", "Call it E18.**", "**B2a.", "**B3."),
            ("E19", "to P4 B7 item 9 after E12's sentence:**", "9. *Power aligned to logged times", "**B8."),
        ):
            with self.subTest(edit=edit):
                block = source.split(anchor, 1)[1].lstrip("\n").split("\n\n", 1)[0]
                lines = block.splitlines()
                self.assertTrue(all(line == ">" or line.startswith("> ") for line in lines))
                expected = "\n".join(line[2:] for line in lines)
                self.assertTrue(expected)
                self.assertEqual(p4.count(expected), 1)
                section = p4.split(start, 1)[1].split(end, 1)[0]
                self.assertEqual(section.count(expected), 1)

    def test_named_power_script_reproduces_both_columns(self):
        output = subprocess.check_output([sys.executable, "-B", POWER_SCRIPT], text=True)
        rows = {}
        for line in output.splitlines():
            count, levels = line.split(" ", 1)
            estimates = ast.literal_eval(levels)
            self.assertEqual([row[0] for row in estimates], [.025, .0125])
            rows[int(count)] = [
                " / ".join(f"{Decimal(str(power)):.2f}".lstrip("0") for power in row[3])
                for row in estimates
            ]
        self.assertEqual(list(rows), [22, 20, 16, 11, 6])
        amendment = (EVIDENCE / "r1-ready-1116/AMENDMENT-R1-DRAFT.md").read_text()
        for count, powers in rows.items():
            with self.subTest(strata=count):
                self.assertEqual(amendment.count(f"| {count} | {' | '.join(powers)} |"), 1)


class ProtectedSourceComparisonTests(unittest.TestCase):
    """B1's closure byte freeze on invented Git objects."""

    PACKAGE = "joulewise/align/apple"
    SCORER = PACKAGE + "/rl176.py"
    PHASES = PACKAGE + "/rl176_phases.py"
    ENTRY = "scripts/align_v4_series_release.py"
    RELEASE = b"from joulewise.align.apple import rl176, rl176_phases, wire\n"
    SOURCE = b"""S_SUPERIORITY_ALPHA = 'toy-level-a'

@(
    toy_decorator_a
)
def _tail_test(item):
    return item

def _holm(item):
    return item  # holm-a

def _decode_design(item):
    # design-a
    return item

def _decode_rows(item):
    return item
    # rows-a

def _residual_scores(item):
    return 'residual-a'

def _s_rank(item='rank-a'):
    return item

def _q_energies(item):
    return 'q-a'

def unrelated():
    _holm = 'local only'
    return 'other-a'
"""

    def setUp(self):
        self.scratch = Path(self.enterContext(tempfile.TemporaryDirectory()))
        self.repo = self.scratch / "repo"
        self.repo.mkdir()
        init_git_fixture(self.repo, "--quiet", "--object-format=sha1")
        self.w1 = self.commit()

    def git(self, *args, data=None):
        return subprocess.check_output([
            "git", "-C", self.repo, "-c", "user.name=Toy", "-c", "user.email=toy@example.invalid",
            "-c", "commit.gpgsign=false", *args,
        ], input=data).strip().decode("ascii")

    def commit(self, source=SOURCE, phases=b"TOY_PHASE = 1\n", *, parent=None, mode="100644", changes=None):
        files = {self.SCORER: source, self.PHASES: phases, self.ENTRY: self.RELEASE,
                 self.PACKAGE + "/wire.py": b"WIRE = 1\n"}
        files.update(changes or {})
        tree = {}
        for path, content in files.items():
            if content is None:
                continue
            *directories, filename = path.split("/")
            node = tree
            for directory in directories:
                node = node.setdefault(directory, {})
            file_mode = mode if path == self.SCORER else "100644"
            node[filename] = (file_mode, self.git("hash-object", "-w", "--stdin", data=content))

        def write_tree(node):
            entries = []
            for name, value in node.items():
                if isinstance(value, dict):
                    entries.append(f"040000 tree {write_tree(value)}\t{name}\n")
                else:
                    file_mode, oid = value
                    entries.append(f"{file_mode} blob {oid}\t{name}\n")
            return self.git("mktree", data="".join(entries).encode("ascii"))

        args = ["-p", parent] if parent is not None else []
        return self.git("commit-tree", write_tree(tree), *args, "-m", "invented commit")

    def compare(self, c1, status, *, w1=None):
        cmd = [sys.executable, "-B", ROOT / "scripts/compare_c1_protected_sources.py",
               "--repo", self.repo, "--w1-commit", w1 or self.w1, "--c1-commit", c1]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.scratch)
        self.assertEqual(result.returncode, status, (result.stdout, result.stderr))
        self.assertEqual(result.stderr, "")
        self.assertNotIn("toy-level-a", result.stdout)
        return json.loads(result.stdout)

    def assert_changed_files(self, c1, paths, *, w1=None):
        result = self.compare(c1, 2, w1=w1)
        self.assertEqual(result["files_for_review"], paths)
        self.assertEqual(list(result["closure_changes"]), paths)
        for record in result["closure_changes"].values():
            self.assertNotEqual(record["w1"], record["c1"])
        return result

    def test_same_commit_and_same_tree_at_distinct_commits(self):
        c1 = self.commit(parent=self.w1)
        self.assertNotEqual(c1, self.w1)
        for commit in (self.w1, c1):
            with self.subTest(commit=commit):
                output = self.compare(commit, 0)
                self.assertEqual(output, {
                    "revisions": {"w1": {"commit": self.w1}, "c1": {"commit": commit}},
                    "closure_changes": {}, "files_for_review": [],
                })

    def test_residual_inventory_includes_each_changed_module(self):
        unrelated = self.SOURCE.replace(b"other-a", b"other-b")
        for source, phases, expected in (
            (unrelated, b"TOY_PHASE = 1\n", [self.SCORER]),
            (self.SOURCE, b"TOY_PHASE = 2\n", [self.PHASES]),
            (unrelated, b"TOY_PHASE = 2\n", [self.SCORER, self.PHASES]),
        ):
            with self.subTest(files=expected):
                self.assert_changed_files(self.commit(source, phases), expected)

    def test_each_protected_binding_detects_a_one_byte_change(self):
        for name, before in (
            ("S_SUPERIORITY_ALPHA", b"toy-level-a"), ("_tail_test", b"toy_decorator_a"),
            ("_holm", b"holm-a"), ("_decode_design", b"design-a"), ("_decode_rows", b"rows-a"),
            ("_residual_scores", b"residual-a"), ("_s_rank", b"rank-a"), ("_q_energies", b"q-a"),
        ):
            with self.subTest(binding=name):
                self.assertEqual(self.SOURCE.count(before), 1)
                c1 = self.commit(self.SOURCE.replace(before, before[:-1] + b"b"))
                record = self.assert_changed_files(c1, [self.SCORER])["closure_changes"][self.SCORER]
                for side, commit in (("w1", self.w1), ("c1", c1)):
                    self.assertEqual(record[side], {
                        "blob": self.git("rev-parse", f"{commit}:{self.SCORER}"),
                        "mode": "100644", "kind": "blob",
                    })

    def test_line_endings_are_source_bytes(self):
        c1 = self.commit(self.SOURCE.replace(b"return item  # holm-a\n", b"return item  # holm-a\r\n"))
        self.assert_changed_files(c1, [self.SCORER])

    def test_decorator_after_form_feed_is_frozen(self):
        body = b"def _holm(item):\n    return item  # holm-a\n"
        helpers = b"def keep(f): return f\ndef twice(f): return lambda: 2 * f()\n"
        for prefix, continuation in (
            (b"\x0c", b"@keep\n"),
            (b" \t\x0c", b"@(\n    keep\n    @ keep\n)\n"),
        ):
            with self.subTest(prefix=prefix, continuation=continuation):
                old = prefix + b"@keep\n" + continuation + body
                new = prefix + b"@twice\n" + continuation + body
                w1 = self.commit(helpers + self.SOURCE.replace(body, old))
                c1 = self.commit(helpers + self.SOURCE.replace(body, new))
                for left, right in ((w1, c1), (c1, w1)):
                    self.assert_changed_files(right, [self.SCORER], w1=left)

    def test_indirect_namespace_rebinding_bytes_are_frozen(self):
        base = self.SOURCE.replace(b"S_SUPERIORITY_ALPHA = 'toy-level-a'", b"S_SUPERIORITY_ALPHA = 0.25")
        w1 = self.commit(base)
        for tail in (
            b"import sys\nsys.modules[__name__].S_SUPERIORITY_ALPHA = 0.75\n",
            b"import sys as system\nrefs = system.modules\nmodule = refs[__name__]\ndel module._holm\n",
            b"from sys import modules as registry\nmodule = registry[__name__]\n"
            b"module.__dict__['_' + 'holm'] = unrelated\n",
            b"from builtins import globals as namespace\ndef change():\n"
            b"    namespace()['_holm'] = unrelated\nchange()\n",
            b"def change():\n    _holm.__globals__.update(_holm=unrelated)\nchange()\n",
            b"import sys as system\nlookup = getattr\nput = setattr\n"
            b"put(lookup(system, 'mod' + 'ules')[__name__], '_' + 'holm', unrelated)\n",
        ):
            with self.subTest(tail=tail):
                rebound = self.commit(base + b"\n" + tail)
                for left, right in ((w1, rebound), (rebound, w1)):
                    self.assert_changed_files(right, [self.SCORER], w1=left)

    def test_callable_mutations_are_frozen_as_bytes(self):
        base = self.SOURCE.replace(
            b"def _holm(item):\n    return item  # holm-a\n",
            b"def _holm(item=1, *, shift=0):\n    return item + shift\n",
        ) + b"\ndef revised(): return 2\n"
        w1 = self.commit(base)
        residual = self.commit(base + b"\ndef ordinary(): return _holm() + revised()\n")
        self.assert_changed_files(residual, [self.SCORER], w1=w1)

        for tail in (
            b"_holm.__code__ = revised.__code__\n",
            b"alias = _holm\nalias.__defaults__ = (2,)\n",
            b"def change():\n    callbacks = [_holm]\n    callbacks[0].__kwdefaults__['shift'] = 2\nchange()\n",
            b"def change(fn):\n    fn.__defaults__ = (2,)\nchange(_holm)\n",
            b"del _holm.__defaults__\n",
            b"from .rl176 import _holm as alias\nalias.__defaults__ = (2,)\n",
            b"from . import rl176 as scorer\nscorer._holm.__defaults__ = (2,)\n",
            b"match scorer:\n    case ModuleType(_holm=fn):\n        fn.__defaults__ = (2,)\n",
        ):
            with self.subTest(tail=tail):
                invalid = self.commit(base + tail)
                for left, right in ((w1, invalid), (invalid, w1)):
                    self.assert_changed_files(right, [self.SCORER], w1=left)

    def test_missing_duplicate_and_rebound_binding_bytes_are_frozen(self):
        for source in (
            self.SOURCE.replace(b"def _holm(item):\n    return item  # holm-a\n", b""),
            self.SOURCE + b"\ndef _holm(item):\n    return item\n",
            self.SOURCE + b"\n_holm = unrelated\n",
            self.SOURCE + b"\nif False:\n    _holm = unrelated\n",
            self.SOURCE + b"\nimport invented as _holm\n",
            self.SOURCE + b"\nmatch object():\n    case _holm:\n        pass\n",
            self.SOURCE + b"\ndef wrapper():\n    global _holm\n    _holm = unrelated\n",
        ):
            with self.subTest(tail=source[-75:]):
                commit = self.commit(source)
                self.assert_changed_files(commit, [self.SCORER])

    def test_source_is_neither_parsed_nor_executed(self):
        content = b"pretend_prompt_should_stay_hidden = )\n"
        c1 = self.commit(self.SOURCE + b"\n" + content, changes={
            self.ENTRY: b"from pathlib import Path\nPath('invented-import-marker').touch()\n",
        })
        report = self.assert_changed_files(c1, [self.SCORER, self.ENTRY])
        self.assertNotIn(content.decode().strip(), json.dumps(report))
        self.assertEqual(self.compare(c1, 0, w1=c1)["files_for_review"], [])
        self.assertFalse((self.scratch / "invented-import-marker").exists())

    def test_unreadable_tree_invalid_commit_and_missing_modules(self):
        missing_oid = "f" * 40
        broken_commit = self.git("hash-object", "-w", "-t", "commit", "--stdin", data=(
            f"tree {missing_oid}\nauthor Toy <toy@example.invalid> 1 +0000\n"
            "committer Toy <toy@example.invalid> 1 +0000\n\ninvented broken tree\n"
        ).encode("ascii"))
        tree = self.git("rev-parse", f"{self.w1}^{{tree}}")
        for commit in (broken_commit, missing_oid, tree, "HEAD", self.w1[:12],
                       self.commit(None), self.commit(phases=None),
                       self.commit(b"invented symlink target", mode="120000")):
            with self.subTest(commit=commit):
                self.assertTrue(self.compare(commit, 2)["error"])

    def test_missing_release_entry_point_fails_closed_on_either_side(self):
        missing = self.commit(changes={self.ENTRY: None})
        for old, new in ((self.w1, missing), (missing, self.w1), (missing, missing)):
            self.assertIn(self.ENTRY, self.compare(new, 2, w1=old)["error"])

    def test_missing_release_entry_point_names_side_and_preserves_all_file_flags(self):
        missing = self.commit(self.SOURCE + b"# invented scorer edit\n",
                              b"from . import rl176\n# invented phase edit\n", changes={self.ENTRY: None})
        for label, old, new in (("W1", missing, self.w1), ("C1", self.w1, missing)):
            with self.subTest(missing_side=label):
                result = self.assert_changed_files(new, [self.SCORER, self.PHASES, self.ENTRY], w1=old)
                self.assertEqual(result["error"], f"{label} {self.ENTRY} is missing")
                self.assertIsNone(result["closure_changes"][self.ENTRY][label.lower()])

    def test_phase_rebinding_and_wiring_bytes_are_flagged_without_exceptions(self):
        phase = b"from . import rl176\n# invented wiring note A\n"
        w1 = self.commit(phases=phase)
        for changed in (phase.replace(b"note A", b"note B"), phase + b"# invented extra byte change\n",
                        b"from . import rl176\nrl176.S_SUPERIORITY_ALPHA = 0.75\n"):
            c1 = self.commit(phases=changed)
            self.assert_changed_files(c1, [self.PHASES], w1=w1)
            self.assert_changed_files(w1, [self.PHASES], w1=c1)
        altered = self.SOURCE.replace(b"'toy-level-a'", b"0.75")
        self.assert_changed_files(self.commit(altered), [self.SCORER])

    def test_audit_four_root_module_is_in_the_closure(self):
        path = self.PACKAGE + "/wire.py"
        source = b"""from joulewise.align.apple import rl176
try:
    from toy_release_options import ALPHA
except ModuleNotFoundError:
    ALPHA = 0.25
rl176.S_SUPERIORITY_ALPHA = ALPHA
"""
        root = "toy_release_options.py"
        w1 = self.commit(changes={path: source, root: b"ALPHA = 0.25\n"})
        c1 = self.commit(changes={path: source, root: b"ALPHA = 0.75\n"})
        self.assert_changed_files(c1, [root], w1=w1)
        self.assert_changed_files(w1, [root], w1=c1)

    def test_audit_four_changed_callable_dependency_is_in_the_closure(self):
        wire = self.PACKAGE + "/wire.py"
        source = b"""from joulewise.align.apple import rl176
missing = float('nan')
another = float('nan')
markers = (missing,)
def classify(value=missing, excluded=markers): return value in excluded
rl176._holm = classify
"""
        w1 = self.commit(changes={wire: source})
        c1 = self.commit(changes={wire: source.replace(b"markers = (missing,)", b"markers = (another,)")})
        self.assert_changed_files(c1, [wire], w1=w1)
        self.assert_changed_files(w1, [wire], w1=c1)

    def test_audit_four_deleted_phase_preserves_every_flagged_path(self):
        c1 = self.commit(self.SOURCE + b"# toy scorer note\n", phases=None)
        for side, old, new in (("c1", self.w1, c1), ("w1", c1, self.w1)):
            result = self.assert_changed_files(new, [self.SCORER, self.PHASES], w1=old)
            self.assertIsNone(result["closure_changes"][self.PHASES][side])

    def test_transitive_package_addition_and_import_time_file_are_flagged(self):
        wire = self.PACKAGE + "/wire.py"
        dep = self.PACKAGE + "/nested/helper.py"
        resource = "invented-import-note.txt"
        helper = b"""try:
    with open('invented-import-note.txt', encoding='ascii') as note:
        note.read()
except FileNotFoundError:
    pass
try:
    from .fresh import WIRE
except ModuleNotFoundError:
    pass
"""
        fresh = self.PACKAGE + "/nested/fresh.py"
        files = {wire: b"from .nested import helper\n", dep: helper, resource: b"old\n"}
        w1 = self.commit(changes=files)
        c1 = self.commit(changes=files | {resource: b"new\n", fresh: b"WIRE = 2\n"})
        for side, old, new in (("w1", w1, c1), ("c1", c1, w1)):
            result = self.assert_changed_files(new, [resource, fresh], w1=old)
            self.assertIsNone(result["closure_changes"][fresh][side])

    def test_reports_every_changed_file_in_both_directions(self):
        wire = self.PACKAGE + "/wire.py"
        w1 = self.commit(changes={"moved-from.txt": b"same bytes\0\n"})
        c1 = self.commit(self.SOURCE + b"# invented scorer comment\n",
                         b"from . import rl176\n# invented phase comment\n", changes={
                             wire: b"from . import rl176\nrl176._holm = lambda: 2\nrl176._tail_test = lambda: 3\n",
                             "moved-to.txt": b"same bytes\0\n", "unrelated.md": b"invented note\n",
                         })
        paths = [self.SCORER, self.PHASES, wire, "moved-from.txt", "moved-to.txt", "unrelated.md"]
        for old, new in ((w1, c1), (c1, w1)):
            result = self.assert_changed_files(new, paths, w1=old)
            self.assertEqual(self.git("diff", "--no-renames", "--name-only", old, new).splitlines(), paths)
            self.assertNotIn("invented note", json.dumps(result))

    def test_guarded_resource_is_frozen_in_both_directions(self):
        wire = self.PACKAGE + "/wire.py"
        source = b"""from pathlib import Path
flag = Path('invented-trigger.txt')
if flag.is_file():
    from joulewise.align.apple import rl176
    rl176.S_SUPERIORITY_ALPHA = float(flag.read_text())
"""
        path = "invented-trigger.txt"
        w1 = self.commit(changes={wire: source, path: b"0.25\n"})
        c1 = self.commit(changes={wire: source, path: b"0.75\n"})
        self.assert_changed_files(c1, [path], w1=w1)
        self.assert_changed_files(w1, [path], w1=c1)

    def test_file_mode_change_is_flagged_even_with_the_same_blob(self):
        c1 = self.commit(mode="100755")
        record = self.assert_changed_files(c1, [self.SCORER])["closure_changes"][self.SCORER]
        self.assertEqual(record["w1"]["blob"], record["c1"]["blob"])
        self.assertEqual((record["w1"]["mode"], record["c1"]["mode"]), ("100644", "100755"))

    def test_help_lists_only_byte_freeze_inputs(self):
        output = subprocess.check_output([
            sys.executable, "-B", ROOT / "scripts/compare_c1_protected_sources.py", "--help",
        ], text=True)
        self.assertIn("closure byte freeze", output)
        self.assertEqual(set(re.findall(r"--[a-z0-9]+(?:-[a-z0-9]+)*", output)), {
            "--help", "--repo", "--w1-commit", "--c1-commit",
        })
