"""Verify PR #813 against the verbatim RL-182 §1.3 and RL-176 §D excerpts."""

import ast
from decimal import Decimal
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shlex
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
    """Row 10's CLI contract on invented Git objects and prompt maps."""

    SCORER = "joulewise/align/apple/rl176.py"
    PHASES = "joulewise/align/apple/rl176_phases.py"
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
    PROMPTS = {"invented-A": "a" * 64, "invented-B": "b" * 64}

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

    def commit(self, source=SOURCE, phases=b"TOY_PHASE = 1\n", *, parent=None, mode="100644"):
        entries = []
        for name, blob, file_mode in (("rl176.py", source, mode), ("rl176_phases.py", phases, "100644")):
            if blob is not None:
                oid = self.git("hash-object", "-w", "--stdin", data=blob)
                entries.append(f"{file_mode} blob {oid}\t{name}\n")
        tree = self.git("mktree", data="".join(entries).encode("ascii"))
        for directory in ("apple", "align", "joulewise"):
            tree = self.git("mktree", data=f"040000 tree {tree}\t{directory}\n".encode("ascii"))
        args = ["-p", parent] if parent is not None else []
        return self.git("commit-tree", tree, *args, "-m", "invented commit")

    def compare(self, c1, status, *, w1=None, w1_map=None, c1_map=None):
        w1_prompts = self.scratch / "w1.json"
        c1_prompts = self.scratch / "c1.json"
        for path, payload in ((w1_prompts, w1_map), (c1_prompts, c1_map)):
            if payload is False:
                path.unlink(missing_ok=True)
                continue
            if not isinstance(payload, bytes):
                payload = json.dumps(self.PROMPTS if payload is None else payload).encode("utf-8")
            path.write_bytes(payload)
        cmd = [sys.executable, "-B", ROOT / "scripts/compare_c1_protected_sources.py",
               "--repo", self.repo, "--w1-commit", w1 or self.w1, "--c1-commit", c1,
               "--w1-prompts", w1_prompts, "--c1-prompts", c1_prompts, "--static-only"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, status, (result.stdout, result.stderr))
        self.assertEqual(result.stderr, "")
        output = json.loads(result.stdout)
        self.assertNotIn("toy-level-a", result.stdout)
        return output

    def test_same_commit_and_same_tree_at_distinct_commits(self):
        c1 = self.commit(parent=self.w1)
        self.assertNotEqual(c1, self.w1)
        for commit in (self.w1, c1):
            with self.subTest(commit=commit):
                output = self.compare(commit, 0)
                self.assertEqual(output["protected_changes"], {})
                self.assertEqual(output["prompt_changes"], {})
                self.assertEqual(output["files_for_review"], [])
                self.assertEqual(output["revisions"]["w1"]["commit"], self.w1)
                self.assertEqual(output["revisions"]["c1"]["commit"], commit)

    def test_residual_inventory_includes_each_changed_module(self):
        unrelated = self.SOURCE.replace(b"other-a", b"other-b")
        for source, phases, expected in (
            (unrelated, b"TOY_PHASE = 1\n", [self.SCORER]),
            (self.SOURCE, b"TOY_PHASE = 2\n", [self.PHASES]),
            (unrelated, b"TOY_PHASE = 2\n", [self.SCORER, self.PHASES]),
        ):
            with self.subTest(files=expected):
                output = self.compare(self.commit(source, phases), 2)
                self.assertEqual(output["protected_changes"], {})
                self.assertEqual(output["files_for_review"], expected)
                modules = output["revisions"]
                for path in expected:
                    self.assertNotEqual(modules["w1"]["modules"][path], modules["c1"]["modules"][path])

    def test_each_protected_binding_detects_a_one_byte_change(self):
        for name, before in (
            ("S_SUPERIORITY_ALPHA", b"toy-level-a"), ("_tail_test", b"toy_decorator_a"),
            ("_holm", b"holm-a"), ("_decode_design", b"design-a"), ("_decode_rows", b"rows-a"),
            ("_residual_scores", b"residual-a"), ("_s_rank", b"rank-a"), ("_q_energies", b"q-a"),
        ):
            with self.subTest(binding=name):
                self.assertEqual(self.SOURCE.count(before), 1)
                c1 = self.commit(self.SOURCE.replace(before, before[:-1] + b"b"))
                changes = self.compare(c1, 2)["protected_changes"]
                self.assertEqual(list(changes), [name])
                self.assertRegex(changes[name]["w1"], r"^[0-9a-f]{64}$")
                self.assertRegex(changes[name]["c1"], r"^[0-9a-f]{64}$")
                self.assertNotEqual(changes[name]["w1"], changes[name]["c1"])

    def test_line_endings_are_source_bytes(self):
        c1 = self.commit(self.SOURCE.replace(b"return item  # holm-a\n", b"return item  # holm-a\r\n"))
        self.assertEqual(list(self.compare(c1, 2)["protected_changes"]), ["_holm"])

    def test_first_decorator_is_hashed_after_form_feed_indentation_reset(self):
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
                for left, right, before, after in ((w1, c1, old, new), (c1, w1, new, old)):
                    self.assertEqual(self.compare(right, 2, w1=left)["protected_changes"], {
                        "_holm": {"w1": hashlib.sha256(before).hexdigest(),
                                  "c1": hashlib.sha256(after).hexdigest()},
                    })

    def test_indirect_module_namespace_rebindings_fail_closed(self):
        base = self.SOURCE.replace(b"S_SUPERIORITY_ALPHA = 'toy-level-a'", b"S_SUPERIORITY_ALPHA = 0.25")
        w1 = self.commit(base)
        for tail, name in (
            (b"import sys\nsys.modules[__name__].S_SUPERIORITY_ALPHA = 0.75\n", "S_SUPERIORITY_ALPHA"),
            (b"import sys as system\nrefs = system.modules\nmodule = refs[__name__]\ndel module._holm\n", "_holm"),
            (b"from sys import modules as registry\nmodule = registry[__name__]\n"
             b"module.__dict__['_' + 'holm'] = unrelated\n", None),
            (b"from builtins import globals as namespace\ndef change():\n"
             b"    namespace()['_holm'] = unrelated\nchange()\n", None),
            (b"def change():\n    _holm.__globals__.update(_holm=unrelated)\nchange()\n", None),
            (b"import sys as system\nlookup = getattr\nput = setattr\n"
             b"put(lookup(system, 'mod' + 'ules')[__name__], '_' + 'holm', unrelated)\n", None),
        ):
            with self.subTest(tail=tail):
                rebound = self.commit(base + b"\n" + tail)
                for left, right in ((w1, rebound), (rebound, w1), (rebound, rebound)):
                    error = self.compare(right, 2, w1=left)["error"]
                    self.assertIn(name or "namespace", error)

    def test_mutating_or_exporting_protected_callable_objects_fails_closed(self):
        base = self.SOURCE.replace(
            b"def _holm(item):\n    return item  # holm-a\n",
            b"def _holm(item=1, *, shift=0):\n    return item + shift\n",
        ) + b"\ndef revised(): return 2\n"
        w1 = self.commit(base)
        residual = self.commit(base + b"\ndef ordinary(): return _holm() + revised()\n")
        output = self.compare(residual, 2, w1=w1)
        self.assertEqual(output["protected_changes"], {})
        self.assertEqual(output["files_for_review"], [self.SCORER])

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
                for left, right in ((w1, invalid), (invalid, w1), (invalid, invalid)):
                    self.assertIn("_holm", self.compare(right, 2, w1=left)["error"])

    def test_missing_duplicate_and_rebound_bindings_fail_closed(self):
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
                self.assertIn("_holm", self.compare(commit, 2)["error"])
                self.assertIn("_holm", self.compare(commit, 2, w1=commit)["error"])

    def test_syntax_error_omits_source(self):
        c1 = self.commit(self.SOURCE + b"\npretend_prompt_should_stay_hidden = )\n")
        error = self.compare(c1, 2)["error"]
        self.assertNotIn("pretend_prompt_should_stay_hidden", error)

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

    def test_malformed_duplicate_empty_and_missing_projections(self):
        duplicate = ('{"invented-A":"' + "a" * 64 + '","invented-\\u0041":"' + "a" * 64 + '"}')
        for prompts in (b"{", duplicate.encode("ascii"), {}, [], {"": "a" * 64},
                        {"invented-A": "g" * 64}, {"invented-A": {"sha256": "a" * 64}}, False):
            with self.subTest(projection=prompts):
                self.assertTrue(self.compare(self.w1, 2, c1_map=prompts)["error"])
                self.assertTrue(self.compare(self.w1, 2, w1_map=prompts)["error"])

    def test_prompt_changes_compare_exact_key_set_and_each_digest(self):
        changed_key = {"invented-C": "a" * 64, "invented-B": "b" * 64}
        changes = self.compare(self.w1, 1, c1_map=changed_key)["prompt_changes"]
        self.assertEqual(changes, {
            "invented-A": {"w1": "a" * 64, "c1": None},
            "invented-C": {"w1": None, "c1": "a" * 64},
        })
        changed_hash = self.PROMPTS | {"invented-B": "c" * 64}
        self.assertEqual(self.compare(self.w1, 1, c1_map=changed_hash)["prompt_changes"], {
            "invented-B": {"w1": "b" * 64, "c1": "c" * 64},
        })


class ProtectedRuntimeComparisonTests(unittest.TestCase):
    """Runtime evidence on invented source through a test-only worker transport."""

    PACKAGE = "joulewise/align/apple"
    SCORER = PACKAGE + "/rl176.py"
    PHASES = PACKAGE + "/rl176_phases.py"
    ENTRY = "scripts/align_v4_series_release.py"
    LEVEL = "S_SUPERIORITY_ALPHA"
    FUNCTIONS = ("_decode_design", "_decode_rows", "_residual_scores", "_tail_test",
                 "_s_rank", "_holm", "_q_energies")
    FIXED_CASES = {
        "_decode_design": ("zero", "one", "nan", "infinity"),
        "_decode_rows": ("no-trace", "stamp-at-end"),
        "_residual_scores": ("empty", "five-training", "six-training"),
        "_tail_test": ("empty", "tie", "infinity"),
        "_s_rank": ("empty", "tie", "above-level", "below-level"),
        "_holm": ("empty", "boundary"),
        "_q_energies": ("empty", "no-trace-with-stamp", "stamp-at-segment-start"),
    }
    SIBLINGS = ("rl176_phases", "wire", "nested.helper")
    SOURCE = ("S_SUPERIORITY_ALPHA = 0.25\n" + "".join(
        f"def {name}(): return 1\n" for name in FUNCTIONS
    ) + "from . import rl176_phases\n").encode("ascii")
    RELEASE = b"""from joulewise.align.apple import rl176, rl176_phases, wire
from joulewise.align.apple.nested import helper
if __name__ == '__main__':
    raise AssertionError('production main must stay closed')
"""
    IMAGE = "sha256:" + "a" * 64

    def setUp(self):
        self.scratch = Path(self.enterContext(tempfile.TemporaryDirectory())).resolve()
        self.repo = self.scratch / "git"
        self.repo.mkdir()
        init_git_fixture(self.repo, "--quiet", "--object-format=sha1")
        self.prompt_map = self.scratch / "prompts.json"
        self.prompt_map.write_text(json.dumps({"invented-A": "a" * 64}), encoding="ascii")
        self.bin = self.scratch / "bin"
        self.bin.mkdir()
        transport = self.bin / "docker"
        transport.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} -IBS -c {shlex.quote(self.TRANSPORT)} \"$@\"\n",
                             encoding="utf-8")
        transport.chmod(0o700)
        self.env = os.environ | {"PATH": str(self.bin) + os.pathsep + os.environ["PATH"]}

    # The fixture transport runs only the test's invented modules. Assert the
    # production sandbox arguments and exercise the real worker in a new child.
    TRANSPORT = """
import os, pathlib, sys
args = sys.argv[1:]
assert args[0:2] == ['--host', 'unix:///var/run/docker.sock']
for flag in ('--pull=never', '--network=none', '--read-only', '--cap-drop=ALL',
             '--security-opt=no-new-privileges', '--user=65534:65534', '--entrypoint=/usr/bin/timeout'):
    assert flag in args, flag
mounts = {}
for index, arg in enumerate(args):
    if arg == '--mount':
        mode, source, target, access = args[index + 1].split(',')
        assert mode == 'type=bind' and access == 'readonly'
        mounts[target.removeprefix('dst=')] = source.removeprefix('src=')
assert set(mounts) == {'/source', '/row10_worker.py'}
assert all(not path.is_file() or path.suffix == '.py' for path in pathlib.Path(mounts['/source']).rglob('*'))
index = args.index('sha256:' + 'a' * 64)
assert args[index + 1:index + 4] == ['--kill-after=2s', '30s', '/usr/local/bin/python3']
python_args = [mounts.get(arg, arg) for arg in args[index + 4:]]
assert '-I' in python_args and '-B' in python_args and '-S' in python_args
os.chdir(mounts['/source'])
os.execve(sys.executable, [sys.executable, *python_args], {'PATH': os.defpath})
"""

    def git(self, *args, data=None):
        return subprocess.check_output([
            "git", "-C", self.repo, "-c", "user.name=Toy", "-c", "user.email=toy@example.invalid",
            "-c", "commit.gpgsign=false", *args,
        ], input=data).strip().decode("ascii")

    def commit(self, changes=None):
        files = {self.SCORER: self.SOURCE, self.ENTRY: self.RELEASE,
                 self.PHASES: b"from . import rl176\n",
                 self.PACKAGE + "/wire.py": b"WIRE = 1\n",
                 self.PACKAGE + "/nested/helper.py": b"WIRE = 1\n",
                 self.PACKAGE + "/ignored.txt": b"invented non-source control\n"}
        files.update(changes or {})
        tree = {}
        for path, content in files.items():
            if content is None:
                continue
            *directories, filename = path.split("/")
            node = tree
            for directory in directories:
                node = node.setdefault(directory, {})
            node[filename] = self.git("hash-object", "-w", "--stdin", data=content)

        def write_tree(node):
            entries = []
            for name, value in node.items():
                if isinstance(value, dict):
                    entries.append(f"040000 tree {write_tree(value)}\t{name}\n")
                else:
                    entries.append(f"100644 blob {value}\t{name}\n")
            return self.git("mktree", data="".join(entries).encode("ascii"))

        return self.git("commit-tree", write_tree(tree), "-m", "invented runtime inputs")

    def compare(self, w1, c1, expected, *extra, runtime=True):
        command = [sys.executable, "-B", ROOT / "scripts/compare_c1_protected_sources.py",
                   "--repo", self.repo, "--w1-commit", w1, "--c1-commit", c1,
                   "--w1-prompts", self.prompt_map, "--c1-prompts", self.prompt_map, *extra]
        if runtime:
            command.extend(("--runtime-image", self.IMAGE))
        output = subprocess.run(command, capture_output=True, env=self.env, text=True)
        if expected is not None:
            self.assertEqual(output.returncode, expected, (output.stdout, output.stderr))
        self.assertEqual(output.stderr, "")
        return json.loads(output.stdout)

    def test_audit_three_phase_only_rebinding_requires_refusal(self):
        # Both sides carry an invented release entry point so this replays
        # Astra's circular import in the revised production-import contract.
        w1 = self.commit()
        c1 = self.commit({self.PHASES: b"from . import rl176\nrl176.S_SUPERIORITY_ALPHA = 0.75\n"})
        for old, new in ((w1, c1), (c1, w1)):
            result = self.compare(old, new, 2)
            self.assertEqual(list(result["runtime_changes"]), [self.LEVEL])
            self.assertEqual(result["protected_changes"], {})
            self.assertEqual(result["research_lead_review"], [self.PHASES])

    def test_reassignment_sweep_reaches_each_protected_name_from_every_toy_sibling(self):
        w1 = self.commit()
        for module in self.SIBLINGS:
            path = self.PACKAGE + "/" + module.replace(".", "/") + ".py"
            for name in (self.LEVEL, *self.FUNCTIONS):
                expression = "0.75" if name == self.LEVEL else "replacement"
                for label, action in (
                    ("assignment", f"rl176.{name} = {expression}\n"),
                    ("setattr", f"setattr(rl176, {name!r}, {expression})\n"),
                    ("registry", f"sys.modules[rl176.__name__].{name} = {expression}\n"),
                    ("import hook", f"class OnImport:\n    rl176.{name} = {expression}\n"),
                ):
                    with self.subTest(module=module, name=name, via=label):
                        source = ("import sys\nfrom joulewise.align.apple import rl176\n"
                                  "def replacement(): return 2\n" + action).encode("ascii")
                        c1 = self.commit({path: source})
                        result = self.compare(w1, c1, 2)
                        self.assertEqual(list(result["runtime_changes"]), [name])
                        self.assertEqual(result["protected_changes"], {})

    def test_runtime_identity_covers_nested_code_defaults_closures_and_decorators(self):
        wrapper = """from functools import wraps
from joulewise.align.apple import rl176
original = rl176._holm
def decorate(captured):
    @wraps(original)
    def wrapped(item=DEFAULT, *, shift=KEYWORD):
        def inner(): return NESTED
        return item + shift + captured + inner()
    return wrapped
rl176._holm = decorate(CAPTURED)
"""
        fields = ("DEFAULT", "KEYWORD", "NESTED", "CAPTURED")

        def variant(changed=None):
            source = wrapper
            for field in fields:
                source = source.replace(field, "2" if field == changed else "1")
            if changed == "decorator":
                source += "rl176._holm.__wrapped__ = lambda: 2\n"
            return source.encode("ascii")

        path = self.PACKAGE + "/wire.py"
        w1 = self.commit({path: variant()})
        self.assertEqual(self.compare(w1, w1, 0)["runtime_changes"], {})
        for changed in (*fields, "decorator"):
            with self.subTest(changed=changed):
                self.assertEqual(list(self.compare(w1, self.commit({path: variant(changed)}), 2)
                                      ["runtime_changes"]), ["_holm"])

    def test_outside_wiring_review_is_independent_of_equal_runtime_identity(self):
        w1 = self.commit()
        c1 = self.commit({self.SCORER: self.SOURCE + b"\n# invented unapproved byte change\n"})
        result = self.compare(w1, c1, 2)
        self.assertEqual(result["runtime_changes"], {})
        self.assertNotIn("oracle_changes", result)
        self.assertEqual(result["protected_changes"], {})
        self.assertEqual(list(result["closure_changes"]), [self.SCORER])
        self.assertEqual(result["research_lead_review"], [self.SCORER])

    def test_runtime_identity_distinguishes_shared_mutable_defaults(self):
        module = b"""from joulewise.align.apple import rl176
left = [1]
twin = [1]
def replacement(a=left, b=left): return a is b
rl176._holm = replacement
"""
        path = self.PACKAGE + "/wire.py"
        w1 = self.commit({path: module})
        c1 = self.commit({path: module.replace(b"b=left", b"b=twin")})
        self.assertEqual(list(self.compare(w1, c1, 2)["runtime_changes"]), ["_holm"])

    def test_default_comparison_applies_byte_gate_without_runtime(self):
        w1 = self.commit()
        result = self.compare(w1, w1, 0, runtime=False)
        self.assertNotIn("error", result)
        self.assertNotIn("oracle_changes", result)
        self.assertEqual(result["oracle_coverage"]["summary"], "evaluated 0 of 21 fixed cases")
        self.assertEqual(set(result["runtime_unread"]), {self.LEVEL, *self.FUNCTIONS})

    def test_missing_release_entry_point_fails_closed_on_either_side(self):
        with_release = self.commit()
        missing = self.commit({self.ENTRY: None})
        for old, new in ((with_release, missing), (missing, with_release)):
            self.assertIn("entry point", self.compare(old, new, 2)["error"])

    def test_missing_release_entry_point_names_side_and_preserves_all_file_flags(self):
        complete = self.commit()
        missing = self.commit({
            self.ENTRY: None,
            self.SCORER: self.SOURCE + b"# invented scorer edit\n",
            self.PHASES: b"from . import rl176\n# invented phase edit\n",
        })
        for label, w1, c1 in (("W1", missing, complete), ("C1", complete, missing)):
            with self.subTest(missing_side=label):
                result = self.compare(w1, c1, 2)
                self.assertEqual(result["error"], f"{label} runtime release entry point is missing")
                flags = [self.SCORER, self.PHASES, self.ENTRY]
                self.assertEqual(result["files_for_review"], flags)
                self.assertEqual(list(result["closure_changes"]), flags)
                self.assertIsNone(result["closure_changes"][self.ENTRY][label.lower()])

    def test_wiring_bytes_are_flagged_without_exceptions(self):
        phase = b"from . import rl176\n# invented wiring note A\n"
        c1_phase = phase.replace(b"note A", b"note B")
        w1, c1 = self.commit({self.PHASES: phase}), self.commit({self.PHASES: c1_phase})
        for old, new in ((w1, c1), (c1, w1)):
            result = self.compare(old, new, 2)
            self.assertEqual(list(result["closure_changes"]), [self.PHASES])
            self.assertEqual(result["files_for_review"], [self.PHASES])
            self.assertNotIn("oracle_changes", result)
        other = self.commit({self.PHASES: c1_phase + b"# invented extra byte change\n"})
        self.assertEqual(self.compare(w1, other, 2)["files_for_review"], [self.PHASES])
        altered = self.SOURCE.replace(b"0.25", b"0.75")
        self.assertEqual(self.compare(self.commit(), self.commit({self.SCORER: altered}), 2)
                         ["files_for_review"], [self.SCORER])

    def test_audit_four_nan_alias_changes_default_oracle(self):
        path = self.PACKAGE + "/wire.py"
        source = b"""from joulewise.align.apple import rl176
missing = float('nan')
another = float('nan')
markers = (missing,)
def classify(value=missing, excluded=markers): return value in excluded
rl176._holm = classify
"""
        w1 = self.commit({path: source})
        c1 = self.commit({path: source.replace(b"markers = (missing,)", b"markers = (another,)")})
        for old, new in ((w1, c1), (c1, w1)):
            result = self.compare(old, new, 2)
            self.assertEqual(list(result["closure_changes"]), [path])
            self.assertEqual(list(result["oracle_changes"]["_holm"]), ["defaults"])

    def test_audit_four_root_module_is_projected_and_in_the_closure(self):
        path = self.PACKAGE + "/wire.py"
        source = b"""from joulewise.align.apple import rl176
try:
    from toy_release_options import ALPHA
except ModuleNotFoundError:
    ALPHA = 0.25
rl176.S_SUPERIORITY_ALPHA = ALPHA
"""
        root = "toy_release_options.py"
        w1 = self.commit({path: source, root: b"ALPHA = 0.25\n"})
        c1 = self.commit({path: source, root: b"ALPHA = 0.75\n"})
        for old, new in ((w1, c1), (c1, w1)):
            result = self.compare(old, new, 2)
            self.assertEqual(list(result["closure_changes"]), [root])
            self.assertEqual(list(result["runtime_changes"]), [self.LEVEL])
            self.assertEqual(list(result["oracle_changes"][self.LEVEL]), ["value"])

    def test_audit_four_deleted_phase_preserves_every_flagged_path(self):
        w1 = self.commit()
        c1 = self.commit({self.SCORER: self.SOURCE + b"# toy scorer note\n", self.PHASES: None})
        for old, new in ((w1, c1), (c1, w1)):
            result = self.compare(old, new, 2)
            self.assertEqual(result["files_for_review"], [self.SCORER, self.PHASES])
            self.assertEqual(list(result["closure_changes"]), [self.SCORER, self.PHASES])
            missing_side = "c1" if old == w1 else "w1"
            self.assertIsNone(result["closure_changes"][self.PHASES][missing_side])

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
        w1 = self.commit({wire: b"from .nested import helper\n", dep: helper, resource: b"old\n"})
        c1 = self.commit({wire: b"from .nested import helper\n", dep: helper,
                          resource: b"new\n", fresh: b"WIRE = 2\n"})
        for old, new in ((w1, c1), (c1, w1)):
            result = self.compare(old, new, 2)
            self.assertEqual(list(result["closure_changes"]), [resource, fresh])
            self.assertIn(resource, result["runtime_unread"][self.LEVEL]["w1"])
            self.assertNotIn("oracle_changes", result)

    def test_reports_all_oracle_differences_alongside_all_changed_files(self):
        w1 = self.commit()
        wire = self.PACKAGE + "/wire.py"
        c1 = self.commit({
            wire: b"from . import rl176\nrl176._holm = lambda: 2\nrl176._tail_test = lambda: 3\n",
            self.SCORER: self.SOURCE + b"# invented scorer comment\n",
            self.PHASES: b"from . import rl176\n# invented phase comment\n",
        })
        result = self.compare(w1, c1, 2)
        self.assertEqual(result["files_for_review"], [self.SCORER, self.PHASES, wire])
        self.assertEqual({name: list(cases) for name, cases in result["oracle_changes"].items()}, {
            "_holm": ["defaults"], "_tail_test": ["defaults"],
        })

    def test_absent_projected_resource_cannot_make_its_byte_change_pass(self):
        # The source-only worker cannot see this path, so neither side takes
        # the branch. The full Git tree still contains the potential input.
        wire = self.PACKAGE + "/wire.py"
        source = b"""from pathlib import Path
flag = Path('invented-trigger.txt')
if flag.is_file():
    from joulewise.align.apple import rl176
    rl176.S_SUPERIORITY_ALPHA = float(flag.read_text())
"""
        path = "invented-trigger.txt"
        w1 = self.commit({wire: source, path: b"0.25\n"})
        c1 = self.commit({wire: source, path: b"0.75\n"})
        result = self.compare(w1, c1, 2)
        self.assertEqual(list(result["closure_changes"]), [path])
        self.assertNotIn("oracle_changes", result)

    def test_audit_five_reports_every_skipped_fixed_case(self):
        w1 = self.commit()
        tree = self.git("rev-parse", w1 + "^{tree}")
        c1 = self.git("commit-tree", tree, "-p", w1, "-m", "invented equal tree")
        skipped = {f"{name}/{label}": {"w1": "signature does not accept input", "c1": "signature does not accept input"}
                   for name, labels in self.FIXED_CASES.items() for label in labels}
        for old, new in ((w1, c1), (c1, w1)):
            result = self.compare(old, new, None)
            self.assertNotIn("oracle_changes", result)
            self.assertEqual(result["oracle_coverage"]["summary"], "evaluated 0 of 21 fixed cases")
            self.assertEqual(result["oracle_coverage"]["not_evaluated"], skipped)
            self.assertEqual(result["oracle_coverage"]["unread_level"], {})

    def test_audit_five_reports_level_unread_when_a_guarded_resource_is_unprojected(self):
        wire = self.PACKAGE + "/wire.py"
        resource = "invented-trigger.txt"
        source = b"""from pathlib import Path
flag = Path('invented-trigger.txt')
if flag.is_file():
    from joulewise.align.apple import rl176
    rl176.S_SUPERIORITY_ALPHA = float(flag.read_text())
"""
        w1 = self.commit({wire: source, resource: b"0.25\n"})
        c1 = self.commit({wire: source, resource: b"0.75\n"})
        for old, new in ((w1, c1), (c1, w1)):
            result = self.compare(old, new, None)
            self.assertEqual(result["files_for_review"], [resource])
            self.assertNotIn("oracle_changes", result)
            report = result["oracle_coverage"]
            self.assertEqual(report["summary"], "evaluated 0 of 21 fixed cases")
            self.assertEqual(set(report["not_evaluated"]),
                             {f"{name}/{label}" for name, labels in self.FIXED_CASES.items() for label in labels})
            self.assertEqual(report["unread_level"], result["runtime_unread"][self.LEVEL])
            self.assertEqual(set(result["runtime_unread"]), {self.LEVEL, *self.FUNCTIONS})
            for side in ("w1", "c1"):
                self.assertIn(resource, report["unread_level"][side])

    def test_oracle_coverage_counts_all_fixed_cases_for_compatible_signatures(self):
        source = ("S_SUPERIORITY_ALPHA = 0.25\n" + "".join(
            f"def {name}(*args, **kwargs): return 1\n" for name in self.FUNCTIONS
        ) + "from . import rl176_phases\n").encode("ascii")
        w1 = self.commit({self.SCORER: source})
        result = self.compare(w1, w1, 0)
        self.assertEqual(result["oracle_coverage"]["summary"], "evaluated 21 of 21 fixed cases")
        self.assertEqual(result["oracle_coverage"]["not_evaluated"], {})
        self.assertEqual(result["oracle_coverage"]["unread_level"], {})
        self.assertEqual(result["runtime_unread"], {})

    def test_frozen_public_scorer_outputs(self):
        from fractions import Fraction
        from joulewise.align.apple import rl176

        worker = runpy.run_path(str(ROOT / "scripts/compare_c1_protected_sources.py"))
        table = worker["oracle_outputs"](vars(rl176))
        self.assertEqual(table["_decode_design"]["zero"], (1.0, 0, 0.0))
        self.assertEqual(table["_decode_design"]["one"], (1.0, 1, 5.5))
        self.assertTrue(all(value != value for value in table["_decode_design"]["nan"][1:]))
        self.assertEqual(table["_decode_design"]["infinity"][1:], (float("inf"), float("inf")))
        self.assertEqual(table["_decode_rows"]["no-trace"], ())
        self.assertEqual(table["_decode_rows"]["stamp-at-end"], (((1.0, 1, 5.5), 0.0, 0.0),))
        self.assertEqual(table["_residual_scores"]["empty"], {})
        self.assertEqual(table["_residual_scores"]["five-training"], {})
        self.assertEqual(table["_tail_test"]["empty"],
                         ({"strata": 0, "theta": None, "p_sup": None, "p_inf": None}, None))
        self.assertEqual(table["_tail_test"]["tie"], ({"strata": 1, "theta": 0.5, "p_sup": 1.0, "p_inf": 1.0}, 1))
        self.assertEqual(table["_tail_test"]["infinity"][0]["theta"], 1.0)
        self.assertEqual(table["_s_rank"]["empty"]["words"], ["S NOT EVALUABLE"])
        self.assertEqual(table["_s_rank"]["above-level"]["words"], ["S INCONCLUSIVE"])
        self.assertEqual(table["_s_rank"]["below-level"]["words"], ["S SIGNATURE"])
        self.assertEqual(table["_holm"]["boundary"], (None, {
            "a": ({"strata": 8, "word": "Q SHIFT"}, Fraction(1, 40)),
            "b": ({"strata": 8, "word": "Q SHIFT"}, Fraction(1, 20)),
        }))
        self.assertEqual(table["_q_energies"]["empty"], (0.0, None, None))
        self.assertEqual(table["_q_energies"]["no-trace-with-stamp"], (None, None, None))
        self.assertEqual(table["_q_energies"]["stamp-at-segment-start"], (2.0, 2.0, 0.0))
        self.assertEqual(table[self.LEVEL]["value"], Fraction(1, 80))
