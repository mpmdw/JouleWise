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
               "--w1-prompts", w1_prompts, "--c1-prompts", c1_prompts]
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
                output = self.compare(self.commit(source, phases), 0)
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
                changes = self.compare(c1, 1)["protected_changes"]
                self.assertEqual(list(changes), [name])
                self.assertRegex(changes[name]["w1"], r"^[0-9a-f]{64}$")
                self.assertRegex(changes[name]["c1"], r"^[0-9a-f]{64}$")
                self.assertNotEqual(changes[name]["w1"], changes[name]["c1"])

    def test_line_endings_are_source_bytes(self):
        c1 = self.commit(self.SOURCE.replace(b"return item  # holm-a\n", b"return item  # holm-a\r\n"))
        self.assertEqual(list(self.compare(c1, 1)["protected_changes"]), ["_holm"])

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
                    self.assertEqual(self.compare(right, 1, w1=left)["protected_changes"], {
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
