"""Where the block-5 sealed inventory lands, checked from git objects.

The forcing problem.  The sealed inventory
(``configs/campaigns/v5_claim_25g83/sealed_inventory.json``) lists the SHA-256
of every file a block-5 window executes and names, as ``head``, the commit
those bytes come from: H_claim.  A file cannot name the commit that contains
it, because a commit's name is a hash of its content.  So the filled inventory
is committed one commit later, in the *seal commit*, the child of H_claim.

What this module proves, from the repository's own history and never from the
working tree (so it stays true after later commits change code on main):

1. ``head`` is a commit, and the seal commit (the last commit that changed the
   inventory file) is its direct child.
2. The seal commit changes nothing but the three seal documents
   (``joulewise.b5.harvest.SEAL_DOCUMENT_PATHS``): the inventory, the
   registration and the analysis plan.  So every window input has the same
   bytes in the seal commit as in H_claim.
3. The inventory lists exactly the tracked files of H_claim under the sealed
   roots (``joulewise/``, ``scripts/``, the three pack directories) plus the
   flag catalog, each with the SHA-256 of its bytes at H_claim.

Before the seal the file is a stub (``status`` ``STUB_NOT_SEALED``, ``head``
and ``files`` null); the stub is the registered state of the file at H_claim,
and the test of the real repository only confirms that shape.  The checker
itself is exercised on constructed repositories either way.

The same checker is the proof step of the landing procedure: at the seal
commit, ``python -m unittest tests.test_b5_seal_landing`` must pass.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from joulewise.b5 import harvest
from tests.git_fixture import init_git_fixture

ROOT = Path(__file__).resolve().parents[1]
SEALED_DIRECTORY = harvest.SEALED_DIRECTORY
INVENTORY = f"{SEALED_DIRECTORY}/sealed_inventory.json"
CATALOG = f"{SEALED_DIRECTORY}/flag_catalog.json"
SEALED_ROOTS = (
    "joulewise",
    "scripts",
    "configs/campaigns/d117_floor_qwen3-1p7b_v5",
    "configs/campaigns/d117_floor_qwen3-8b_v5",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5",
)
STUB_STATUS, SEALED_STATUS = "STUB_NOT_SEALED", "SEALED"


def _git(repo: Path, *argv: str, data: bytes | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(("git", "-C", str(repo), *argv), input=data, capture_output=True, check=False)


def files_at(repo: Path, commit: str, roots: tuple[str, ...], extra: tuple[str, ...]) -> dict[str, str]:
    """``{path: sha256 of the file's bytes}`` for every tracked file under ``roots`` at ``commit``, plus ``extra``."""
    listed = _git(repo, "ls-tree", "-r", "-z", "--name-only", commit, "--", *roots, *extra)
    if listed.returncode != 0:
        raise AssertionError(f"git ls-tree {commit} failed: {listed.stderr.decode(errors='replace')[:200]}")
    paths = sorted(item.decode("utf-8") for item in listed.stdout.split(b"\0") if item)
    batch = _git(repo, "cat-file", "--batch", data="".join(f"{commit}:{path}\n" for path in paths).encode("utf-8"))
    if batch.returncode != 0:
        raise AssertionError(f"git cat-file failed: {batch.stderr.decode(errors='replace')[:200]}")
    out, offset, result = batch.stdout, 0, {}
    for path in paths:
        end = out.index(b"\n", offset)
        header = out[offset:end].split()
        if len(header) != 3 or header[1] != b"blob":
            raise AssertionError(f"{commit}:{path} is not a file: {out[offset:end]!r}")
        size = int(header[2])
        result[path] = hashlib.sha256(out[end + 1:end + 1 + size]).hexdigest()
        offset = end + 1 + size + 1
    return result


def seal_landing_problems(repo: Path, *, inventory: str = INVENTORY, roots: tuple[str, ...] = SEALED_ROOTS,
                          extra: tuple[str, ...] = (CATALOG,), ref: str = "HEAD",
                          seal_documents: frozenset[str] = harvest.SEAL_DOCUMENT_PATHS) -> tuple[str, list[str]]:
    """``(state, problems)``; state is ``stub`` or ``sealed``, read from the inventory committed at ``ref``."""
    shown = _git(repo, "show", f"{ref}:{inventory}")
    if shown.returncode != 0:
        return "absent", [f"{inventory} is not tracked at {ref}"]
    document = json.loads(shown.stdout)
    status, head, files = document.get("status"), document.get("head"), document.get("files")
    if status == STUB_STATUS:
        return "stub", [] if head is None and files is None else ["a stub must carry head null and files null"]
    problems: list[str] = []
    if status != SEALED_STATUS:
        problems.append(f"status is {status!r}, expected {SEALED_STATUS!r}")
    if not (isinstance(head, str) and len(head) == 40 and set(head) <= set("0123456789abcdef")):
        return "sealed", problems + ["head is not a 40-character lowercase commit name"]
    if _git(repo, "cat-file", "-e", f"{head}^{{commit}}").returncode != 0:
        return "sealed", problems + [f"head {head} is not a commit in this repository"]
    seal = _git(repo, "log", "-1", "--format=%H %P", ref, "--", inventory).stdout.decode().split()
    if not seal:
        return "sealed", problems + ["no commit changes the inventory"]
    seal_commit, parents = seal[0], seal[1:]
    if parents != [head]:
        problems.append(f"the seal commit {seal_commit} has parents {parents}; its only parent must be head {head}")
    changed = sorted(item.decode("utf-8") for item in _git(
        repo, "diff", "--name-only", "--no-renames", "-z", head, seal_commit).stdout.split(b"\0") if item)
    if inventory not in changed:
        problems.append("the seal commit does not change the inventory relative to head")
    outside = [path for path in changed if path not in seal_documents]
    if outside:
        problems.append(f"the seal commit changes paths that are not seal documents: {outside[:8]}")
    expected = files_at(repo, head, roots, extra)
    if not isinstance(files, dict):
        return "sealed", problems + ["files is not an object"]
    for path in sorted(set(expected) | set(files)):
        if expected.get(path) != files.get(path):
            problems.append(f"{path}: inventory {files.get(path, 'absent')!s:.16}, at head {expected.get(path, 'absent')!s:.16}")
            if len(problems) > 12:
                problems.append("more differences not listed")
                break
    return "sealed", problems


class RepositorySealLandingTests(unittest.TestCase):
    def test_the_committed_inventory_is_the_stub_or_a_correct_landing(self):
        state, problems = seal_landing_problems(ROOT)
        self.assertIn(state, ("stub", "sealed"))
        self.assertEqual(problems, [])

    def test_the_sealed_roots_are_the_ones_the_generator_lists(self):
        # scripts/rehearse_b5_real.py sealed_inventory() is the generator the seal uses
        # (it reads a clean checkout's working tree; this module reads git objects).
        from scripts import rehearse_b5_real

        self.assertEqual(set(SEALED_ROOTS),
                         {"joulewise", "scripts", *(f"configs/campaigns/{pack}" for pack, _ in rehearse_b5_real.PACKS.values())})


class ConstructedLandingTests(unittest.TestCase):
    """The checker on small repositories: one correct landing, and each way a landing can be wrong."""

    ROOTS = ("joulewise", "scripts", "configs/campaigns/pack_a")
    SEAL_DOCUMENTS = frozenset(harvest.SEAL_DOCUMENT_PATHS)

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="b5-seal-landing-")
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name) / "repo"
        self.repo.mkdir()
        init_git_fixture(self.repo, "-q")
        for relative, text in (("joulewise/core.py", "VALUE = 1\n"), ("scripts/tool.py", "print(1)\n"),
                               ("configs/campaigns/pack_a/plan_tree.json", "{}\n"), (CATALOG, '{"codes": {}}\n'),
                               (f"{SEALED_DIRECTORY}/registration_block5.md", "draft\n"),
                               (f"{SEALED_DIRECTORY}/analysis_plan_block5.md", "draft\n"),
                               ("docs/phase_2/window_runbook.md", "screen\n")):
            self.write(relative, text)
        self.write_json(INVENTORY, {"status": STUB_STATUS, "head": None, "files": None})
        self.h_claim = self.commit("H_claim: the last code commit")

    def git(self, *argv: str) -> str:
        completed = subprocess.run(("git", "-C", str(self.repo), "-c", "user.name=t", "-c",
                                    "user.email=t@example.invalid", *argv), check=True, capture_output=True, text=True)
        return completed.stdout.strip()

    def write(self, relative: str, text: str) -> None:
        target = self.repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def write_json(self, relative: str, value) -> None:
        self.write(relative, json.dumps(value, indent=2, sort_keys=True) + "\n")

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def sealed_document(self, head: str | None = None) -> dict:
        head = head or self.h_claim
        return {"status": SEALED_STATUS, "head": head, "files": files_at(self.repo, head, self.ROOTS, (CATALOG,))}

    def problems(self) -> tuple[str, list[str]]:
        return seal_landing_problems(self.repo, roots=self.ROOTS)

    def seal(self, document: dict | None = None) -> str:
        self.write_json(INVENTORY, document or self.sealed_document())
        self.write(f"{SEALED_DIRECTORY}/registration_block5.md", f"sealed; H_claim is {self.h_claim}\n")
        return self.commit("the seal commit")

    def test_the_stub_at_h_claim(self):
        self.assertEqual(self.problems(), ("stub", []))

    def test_a_correct_landing_and_what_may_follow_it(self):
        self.seal()
        self.assertEqual(self.problems(), ("sealed", []))
        # Later commits do not change the verdict: it is read from H_claim and the seal commit.
        self.write("docs/process_traces/seal/52-seal-record.md", "record\n")
        self.commit("records only")
        self.write("joulewise/core.py", "VALUE = 2\n")
        self.commit("a later fix on main to code that does not run during collection")
        self.assertEqual(self.problems(), ("sealed", []))

    def test_an_inventory_committed_together_with_a_window_input(self):
        self.write("joulewise/core.py", "VALUE = 2\n")
        self.seal()
        state, problems = self.problems()
        self.assertEqual(state, "sealed")
        self.assertTrue(any("not seal documents" in problem and "joulewise/core.py" in problem for problem in problems),
                        problems)

    def test_a_seal_commit_that_is_not_the_child_of_head(self):
        self.write("scripts/tool.py", "print(2)\n")
        self.commit("a code commit after the named head")
        self.seal()
        state, problems = self.problems()
        self.assertTrue(any("its only parent must be head" in problem for problem in problems), problems)
        self.assertTrue(any("scripts/tool.py" in problem for problem in problems), problems)

    def test_a_wrong_digest_a_missing_file_and_an_extra_file(self):
        document = self.sealed_document()
        document["files"]["joulewise/core.py"] = "0" * 64
        del document["files"]["scripts/tool.py"]
        document["files"]["joulewise/ghost.py"] = "1" * 64
        self.seal(document)
        _state, problems = self.problems()
        for path in ("joulewise/core.py", "scripts/tool.py", "joulewise/ghost.py"):
            self.assertTrue(any(problem.startswith(path + ":") for problem in problems), (path, problems))

    def test_a_head_that_is_not_a_commit_and_a_candidate_status(self):
        document = self.sealed_document()
        document.update(status="SEALED_CANDIDATE", head="f" * 40)
        self.seal(document)
        _state, problems = self.problems()
        self.assertTrue(any("status is 'SEALED_CANDIDATE'" in problem for problem in problems), problems)
        self.assertTrue(any("is not a commit in this repository" in problem for problem in problems), problems)

    def test_an_inventory_changed_again_after_the_seal(self):
        self.seal()
        document = self.sealed_document()
        document["note"] = "edited after the seal"
        self.write_json(INVENTORY, document)
        self.commit("an edit to the sealed inventory")
        _state, problems = self.problems()
        self.assertTrue(any("its only parent must be head" in problem for problem in problems), problems)


if __name__ == "__main__":
    unittest.main()
