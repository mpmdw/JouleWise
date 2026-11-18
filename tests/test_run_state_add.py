"""RUN_STATE writer acceptance against fixture files and temporary Git repos."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

from scripts import gen_current, run_state_add as add, run_state_items as items
from tests.git_fixture import clone_git_fixture, init_git_fixture
from tests.test_run_state_items import ARCHIVE, EXPIRY, ISSUED, LEGACY, archived_doc, doc, item


ISSUED_ISO = "2026-11-18T11:33:20Z"


def request(**updates):
    return {"heading": "A new item", "body": "An ordinary body.\n", "pointer": None,
            "owner": "lead", "status": "ISSUED", "kind": "event", "issued_epoch_s": ISSUED,
            "expires_epoch_s": None, "sets": [], "supersedes": [], "with": [],
            "message": None, "trailers": [], **updates}


def cli(*arguments):
    output, errors = StringIO(), StringIO()
    with redirect_stdout(output), redirect_stderr(errors):
        code = add.main(list(arguments))
    return code, output.getvalue(), errors.getvalue()


class LocalTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="typed-run-state-fixture-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.run_state, self.current = self.directory / "RUN_STATE.md", self.directory / "CURRENT.json"
        self.run_state.write_text(doc([item(23), item(22), item(21)]), encoding="utf-8")
        gen_current.generate(self.run_state, self.current)
        self.body = self.directory / "body.md"

    def flags(self, *flags, kind="event"):
        kind_flags = ("--kind", kind) if kind is not None else ()
        return ("add", "--run-state", str(self.run_state), "--current", str(self.current), "--no-git",
                "--heading", "Fixture", "--owner", "lead", "--status", "CLOSED",
                "--body", str(self.body), "--issued", ISSUED_ISO, *kind_flags, *flags)

    def test_a01_add_allocates_and_rebuilds_current(self):
        self.assertEqual(add.add_local(self.run_state, self.current, request(expires_epoch_s=EXPIRY)), 24)
        text = self.run_state.read_text(encoding="utf-8")
        self.assertTrue(text.split(add.TOP_MARKER, 1)[1].startswith("\n\n24. **A new item**\n"))
        parsed = items.parse(text)
        self.assertEqual(items.validate(parsed), [])
        self.assertEqual(parsed.items[0].header["kind"], "event")
        self.assertEqual(self.current.read_bytes(), gen_current.render(text))
        self.assertEqual(json.loads(self.current.read_bytes())["open_items"][0],
                         {"item": 24, "status": "ISSUED", "owner": "lead", "expires_epoch_s": EXPIRY})

    def test_a02_self_replacement(self):
        self.assertEqual(add.add_local(self.run_state, self.current,
                                       request(heading="Record {{self}}", body="This is {{self}}.\n")), 24)
        text = self.run_state.read_text(encoding="utf-8")
        self.assertIn("24. **Record 24**", text)
        self.assertIn("This is 24.", text)
        self.assertNotIn("{{self}}", text)

    def test_a03_body_refusals_leave_both_files_unchanged(self):
        before = self.run_state.read_bytes(), self.current.read_bytes()
        for line in ("```item", "```pointer", "30. **x**"):
            with self.subTest(line=line):
                self.body.write_text(f"Body\n\n{line}\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "body cannot contain"):
                    add.add_local(self.run_state, self.current, request(body=self.body.read_text()))
                code, _, error = cli(*self.flags())
                self.assertEqual(code, 2)
                self.assertIn("body cannot contain", error)
                self.assertEqual((self.run_state.read_bytes(), self.current.read_bytes()), before)

    def test_a04_init_uses_maximum_heading_and_refuses_second_init(self):
        updated, cutover = add.init_text(LEGACY)
        self.assertEqual(cutover, 21)
        self.assertEqual(updated, doc())
        with self.assertRaisesRegex(ValueError, "already initialized"):
            add.init_text(updated)

    def test_archived_log_allocates_above_legacy_max_and_accepts_supersedes(self):
        self.run_state.write_text(archived_doc(legacy="\n346. **Retained fixture**\n"), encoding="utf-8")
        self.body.write_text("Fixture body.\n", encoding="utf-8")
        self.assertEqual(cli(*self.flags("--supersedes", "346")), (0, "405\n", ""))
        new, = items.parse(self.run_state.read_text()).items
        self.assertEqual(new.header["supersedes"], ["346"])

    def test_pre_cutover_add_call_defaults_to_event(self):
        self.run_state.write_text(archived_doc(legacy="\n346. **Retained fixture**\n"), encoding="utf-8")
        self.body.write_text("Synthetic review item.\n", encoding="utf-8")
        code, output, error = cli(
            "add", "--no-git", "--run-state", str(self.run_state), "--current", str(self.current),
            "--body", str(self.body), "--heading", "Review probe", "--owner", "magistrate",
            "--status", "ISSUED", "--issued", ISSUED_ISO, "--supersedes", "346")
        self.assertEqual((code, output, error), (0, "405\n", ""))
        self.assertEqual(items.parse(self.run_state.read_text()).items[0].header["kind"], "event")
        self.assertEqual(gen_current.check(self.run_state, self.current), 0)

    def test_explicit_invalid_kind_is_refused(self):
        self.body.write_text("Fixture body.\n", encoding="utf-8")
        before = self.run_state.read_bytes(), self.current.read_bytes()
        errors = StringIO()
        with redirect_stderr(errors), self.assertRaises(SystemExit) as caught:
            add.main(self.flags(kind="note"))
        self.assertEqual(caught.exception.code, 2)
        self.assertIn("invalid choice: 'note'", errors.getvalue())
        self.assertEqual((self.run_state.read_bytes(), self.current.read_bytes()), before)

    def test_supersedes_requires_an_exact_live_or_archived_heading(self):
        self.run_state.write_text(archived_doc(legacy="\n346. **Retained fixture**\n"), encoding="utf-8")
        self.body.write_text("Synthetic review item.\n", encoding="utf-8")
        archive = self.directory / ARCHIVE
        archive.parent.mkdir(parents=True)
        archive.write_text("# Fixture archive\n\n256b. **Archived fixture**\n\n"
                           "```markdown\n404. **Example only**\n```\n", encoding="utf-8")
        before = self.run_state.read_bytes(), self.current.read_bytes()
        for missing in ("346z", "256", "404"):
            with self.subTest(target=missing):
                code, output, error = cli(*self.flags("--supersedes", missing))
                self.assertEqual((code, output), (2, ""))
                self.assertIn(f"DANGLING_REF: item {missing}", error)
                self.assertEqual((self.run_state.read_bytes(), self.current.read_bytes()), before)
        self.assertEqual(cli(*self.flags("--supersedes", "256b")), (0, "405\n", ""))
        self.assertEqual(gen_current.check(self.run_state, self.current), 0)
        self.assertEqual(items.main(["check", "--run-state", str(self.run_state)]), 0)

    def test_program_fence_limits(self):
        before = self.run_state.read_bytes(), self.current.read_bytes()
        for opener in ("```sh", "```zsh", "```bash", "```python", "```", "~~~ sh  "):
            with self.subTest(opener=opener):
                body = f"{opener}\nline one\n\nline three\nline four\nline five\n{opener[:3]}\n"
                self.body.write_text(body, encoding="utf-8")
                code, output, error = cli(*self.flags(kind="incident"))
                self.assertEqual((code, output), (2, ""))
                self.assertIn("body holds a program; put it in the repository and cite its path", error)
                self.assertEqual((self.run_state.read_bytes(), self.current.read_bytes()), before)
        self.body.write_text("```sh\nexample\nexample\n```\n", encoding="utf-8")
        self.assertEqual(cli(*self.flags()), (0, "24\n", ""))
        self.body.write_text("````markdown\n```sh\none\ntwo\nthree\nfour\n```\n````\n", encoding="utf-8")
        self.assertEqual(cli(*self.flags()), (0, "25\n", ""))

    def test_body_line_limits_by_kind(self):
        for kind, limit in (("event", 40), ("decision", 40), ("incident", 120)):
            with self.subTest(kind=kind):
                before = self.run_state.read_bytes(), self.current.read_bytes()
                self.body.write_text("line\n" * (limit + 1), encoding="utf-8")
                code, output, error = cli(*self.flags(kind=kind))
                self.assertEqual((code, output), (2, ""))
                self.assertIn(f"{limit} lines", error)
                self.assertEqual((self.run_state.read_bytes(), self.current.read_bytes()), before)
                self.body.write_text("line\n" * limit, encoding="utf-8")
                self.assertEqual(cli(*self.flags(kind=kind))[0], 0)
        self.body.write_text("line\n" * 41, encoding="utf-8")
        self.assertEqual(cli(*self.flags(kind="incident"))[0], 0)

    def test_unclosed_body_fence_refuses_add_and_preserves_item_404(self):
        initialized, cutover = add.init_text(LEGACY.replace("20. **", "403. **"))
        self.assertEqual(cutover, 404)
        self.run_state.write_text(initialized, encoding="utf-8")
        self.assertEqual(add.add_local(self.run_state, self.current, request()), 404)
        before = self.run_state.read_bytes(), self.current.read_bytes()
        for body in ("```\nunterminated", "~~~markdown\nunterminated", "````\n```\n"):
            with self.subTest(body=body):
                self.body.write_text(body, encoding="utf-8")
                code, _, error = cli(*self.flags())
                self.assertEqual(code, 2)
                self.assertIn("body line 1: unclosed code fence", error)
                self.assertEqual((self.run_state.read_bytes(), self.current.read_bytes()), before)
        self.assertEqual(json.loads(self.current.read_bytes())["open_items"][0]["item"], 404)
        self.assertEqual(add.add_local(self.run_state, self.current, request(body="```\nexample\n```")), 405)

    def test_insertion_rejects_a_lost_or_changed_previous_item(self):
        insert = add._insert_at
        before = self.run_state.read_bytes(), self.current.read_bytes()
        for replacement in ("", item(23, owner="ed")):
            with self.subTest(replacement=replacement):
                def damaged_insertion(text, top_line, rendered):
                    return insert(text, top_line, rendered).replace(item(23), replacement, 1)

                with mock.patch.object(add, "_insert_at", side_effect=damaged_insertion):
                    with self.assertRaisesRegex(ValueError, "preserve .*previous typed item"):
                        add.add_local(self.run_state, self.current, request())
                self.assertEqual((self.run_state.read_bytes(), self.current.read_bytes()), before)


class GitTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="typed-run-state-git-")
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name).resolve()
        self.remote, self.a, self.b = (self.directory / name for name in ("remote.git", "a", "b"))
        self.spool = self.directory / "spool"

        env = mock.patch.dict(os.environ, {
            "JW_RUN_STATE_SPOOL": str(self.spool),
            "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Typed Fixture", "GIT_AUTHOR_EMAIL": "typed@example.invalid",
            "GIT_COMMITTER_NAME": "Typed Fixture", "GIT_COMMITTER_EMAIL": "typed@example.invalid",
        })
        env.start()
        self.addCleanup(env.stop)
        self.remote.mkdir()
        init_git_fixture(self.remote, "--bare", "--initial-branch=main")
        self.assertEqual(self.git(self.remote, "rev-parse", "--is-bare-repository").strip(), "true")
        clone_git_fixture(self.remote, self.a)
        self.assertEqual(self.git(self.a, "symbolic-ref", "--short", "HEAD").strip(), "main")
        self.write_state(doc([item(24, status="CLOSED"), item(23), item(22), item(21)]))
        self.git(self.a, "push", "origin", "HEAD:refs/heads/main")
        self.base = self.remote_head()
        self.assertEqual(self.base, self.git(self.a, "rev-parse", "HEAD").strip())
        clone_git_fixture(self.remote, self.b)
        self.assertEqual(self.git(self.b, "rev-parse", "HEAD").strip(), self.base)

    def git(self, repo, *args, input=None):
        return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True,
                              text=True, encoding="utf-8", input=input).stdout

    def remote_head(self):
        return self.git(self.remote, "rev-parse", "refs/heads/main").strip()

    def write_state(self, text):
        source, current = self.a / add.RUN_STATE, self.a / add.CURRENT
        current.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(text, encoding="utf-8")
        current.write_bytes(gen_current.render(text, source_path=source))
        self.git(self.a, "add", "--", str(add.RUN_STATE), str(add.CURRENT))
        self.assertIn(str(add.RUN_STATE), self.git(self.a, "diff", "--cached", "--name-only").splitlines())
        self.git(self.a, "commit", "-m", "Synthetic state fixture")
        self.assertEqual(self.git(self.a, "show", "-s", "--format=%s").strip(), "Synthetic state fixture")

    def remote_items(self):
        parsed = items.parse(self.git(self.remote, "show", f"refs/heads/main:{add.RUN_STATE}"))
        self.assertEqual(items.validate(parsed), [])
        return [entry.number for entry in parsed.items]

    def call_in(self, repo, *flags):
        original = Path.cwd()
        try:
            os.chdir(repo)
            return cli(*flags)
        finally:
            os.chdir(original)

    def add_flags(self, *extra):
        body = self.directory / "input.md"
        body.write_text("Synthetic CLI body.", encoding="utf-8")
        return ("add", "--heading", "Fixture CLI", "--body", str(body), "--owner", "lead",
                "--status", "ISSUED", "--kind", "decision", "--issued", ISSUED_ISO, *extra)

    def test_a05_illegal_set_aborts_before_write_or_commit(self):
        caller_head = self.git(self.a, "rev-parse", "HEAD")
        source = (self.a / add.RUN_STATE).read_bytes()
        current = (self.a / add.CURRENT).read_bytes()
        with mock.patch.object(add, "_commit", side_effect=AssertionError("invalid add cannot commit")):
            code, _, err = self.call_in(self.a, *self.add_flags("--set", f"24=ARMED@{ISSUED_ISO}"))
        self.assertEqual(code, 2)
        self.assertIn("ILLEGAL_TRANSITION", err)
        self.assertEqual((self.a / add.RUN_STATE).read_bytes(), source)
        self.assertEqual((self.a / add.CURRENT).read_bytes(), current)
        self.assertEqual(self.git(self.a, "rev-parse", "HEAD"), caller_head)
        self.assertEqual(self.remote_head(), self.base)
        self.assertEqual(list(self.spool.glob("*.json")), [])

    def test_a06_collision_retries_against_the_new_remote_head(self):
        landed_a, rejections = [], []
        git = add._git

        def interleave(repo, *args):
            if args[0] == "push" and not landed_a:
                # B took its number from the common head. A lands before B
                # advertises its push. A has its own spool lock like a remote host.
                with mock.patch.object(add, "_git", git), mock.patch.dict(
                        os.environ, {"JW_RUN_STATE_SPOOL": str(self.directory / "writer-a-spool")}):
                    landed_a.append(add.add_git(self.a, request(heading="Writer A")))
                self.assertEqual(self.remote_head(), landed_a[0][1])
            try:
                return git(repo, *args)
            except subprocess.CalledProcessError as error:
                if args[0] == "push":
                    rejections.append(error.stdout)
                raise

        with mock.patch.object(add, "_git", side_effect=interleave):
            number_b, head_b = add.add_git(self.b, request(heading="Writer B"))
        self.assertEqual(len(rejections), 1)
        self.assertIn("[rejected] (fetch first)", rejections[0])
        self.assertEqual(number_b, landed_a[0][0] + 1)
        self.assertEqual(self.remote_head(), head_b)
        self.assertEqual(self.remote_items(), [26, 25, 24, 23, 22, 21])

    def test_a07_network_failure_spools_original_request_then_flush_lands_it(self):
        data = request(issued_epoch_s=ISSUED + 10)
        invalid_remote = self.directory / "absent.git"
        self.git(self.a, "remote", "set-url", "origin", str(invalid_remote))
        self.assertEqual(self.git(self.a, "remote", "get-url", "origin").strip(), str(invalid_remote))
        with self.assertRaises(add.GitFailure) as caught:
            add.add_git(self.a, data)
        self.assertEqual(caught.exception.code, 3)
        spooled, = self.spool.glob("*.json")
        self.assertEqual(json.loads(spooled.read_bytes()), data)
        self.assertEqual(self.remote_head(), self.base)
        self.git(self.a, "remote", "set-url", "origin", str(self.remote))
        self.assertEqual(self.git(self.a, "remote", "get-url", "origin").strip(), str(self.remote))
        code, output, error = self.call_in(self.a, "flush-spool")
        self.assertEqual((code, output.strip(), error), (0, f"25 {self.remote_head()}", ""))
        self.assertEqual(list(self.spool.glob("*.json")), [])
        text = self.git(self.remote, "show", f"refs/heads/main:{add.RUN_STATE}")
        self.assertEqual(items.parse(text).items[0].header["issued_epoch_s"], data["issued_epoch_s"])

    def test_a08_five_stale_pushes_are_spooled(self):
        # Install a bare receive hook that advances main using five preloaded
        # commits, simulating a competing writer after each advertisement.
        tree = self.git(self.remote, "rev-parse", "refs/heads/main^{tree}").strip()
        parent = self.base
        for attempt in range(1, 6):
            head = self.git(self.remote, "commit-tree", tree, "-p", parent, input=f"Race {attempt}\n").strip()
            ref = f"refs/fixture/race/{parent}"
            self.git(self.remote, "update-ref", ref, head)
            self.assertEqual(self.git(self.remote, "rev-parse", ref).strip(), head)
            parent = head
        hook = self.remote / "hooks/pre-receive"
        hook.parent.mkdir(exist_ok=True)
        hook.write_text("""#!/bin/sh
set -eu
read old new ref
unset GIT_QUARANTINE_PATH GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES
next=$(git rev-parse --verify "refs/fixture/race/$old")
git update-ref "$ref" "$next" "$old"
git rev-parse --verify "$ref" >> fixture-raced-heads
""", encoding="utf-8")
        hook.chmod(0o700)
        with self.assertRaises(add.RetriesExhausted) as caught:
            add.add_git(self.a, request())
        self.assertEqual(caught.exception.code, 4)
        self.assertEqual(len((self.remote / "fixture-raced-heads").read_text().splitlines()), 5)
        self.assertEqual(self.remote_head(), parent)
        self.assertEqual(self.remote_items(), [24, 23, 22, 21])
        spooled, = self.spool.glob("*.json")
        self.assertEqual(json.loads(spooled.read_bytes()), request())

    def test_flush_lands_pre_cutover_41_line_request_and_following_request(self):
        data = request(body="Synthetic review line.\n" * 41)
        del data["kind"]
        self.spool.mkdir()
        spooled = self.spool / "01-legacy.json"
        spooled.write_text(json.dumps(data), encoding="utf-8")
        following = self.spool / "02-following.json"
        following.write_text(json.dumps({**data, "heading": "Following", "body": "Short.\n"}), encoding="utf-8")
        code, output, error = self.call_in(self.a, "flush-spool")
        self.assertEqual((code, error), (0, ""))
        self.assertEqual([row.split()[0] for row in output.splitlines()], ["25", "26"])
        self.assertEqual(list(self.spool.glob("*.json")), [])
        text = self.git(self.remote, "show", f"main:{add.RUN_STATE}")
        self.assertNotIn("kind", items.parse(text).items[1].header)
        self.assertEqual(text.count("Synthetic review line.\n"), 41)

    def test_flush_reports_bad_entries_and_lands_later_pre_cutover_program(self):
        self.spool.mkdir()
        bad = {"01-json.json": "{", "02-shape.json": json.dumps(request(body=42)),
               "03-ref.json": json.dumps(request(supersedes=["19z"]))}
        for name, contents in bad.items():
            (self.spool / name).write_text(contents, encoding="utf-8")
        program = "```sh\n" + "fixture example\n" * 5 + "```\n"
        (self.spool / "04-valid.json").write_text(json.dumps(request(body=program)), encoding="utf-8")
        code, output, error = self.call_in(self.a, "flush-spool")
        self.assertEqual((code, output.strip()), (2, f"25 {self.remote_head()}"))
        for name in bad:
            self.assertIn(f"skipped {name}", error)
        self.assertEqual({p.name: p.read_text() for p in self.spool.glob("*.json")}, bad)
        self.assertIn(program, self.git(self.remote, "show", f"main:{add.RUN_STATE}"))

    def test_git_writer_resolves_archive_refs_from_the_fetched_head(self):
        archive = self.a / ARCHIVE
        archive.parent.mkdir(parents=True)
        archive.write_text("# Fixture archive\n\n256b. **Archived fixture**\n", encoding="utf-8")
        self.git(self.a, "add", "--", ARCHIVE)
        self.write_state(archived_doc([item(405, supersedes=["256b"])]))
        self.git(self.a, "push", "origin", "HEAD:refs/heads/main")
        self.assertFalse((self.b / ARCHIVE).exists())
        self.assertEqual(self.call_in(self.b, "flush-spool"), (0, "", ""))
        code, output, error = self.call_in(self.b, *self.add_flags("--supersedes", "256b"))
        self.assertEqual((code, output.strip(), error), (0, f"406 {self.remote_head()}", ""))

    def test_a09_dirty_callers_branch_and_worktrees_are_preserved(self):
        self.git(self.b, "switch", "-c", "fixture-local")
        (self.b / add.RUN_STATE).write_text("Dirty tracked file.", encoding="utf-8")
        (self.b / "dirty.txt").write_text("Untracked file.", encoding="utf-8")

        def caller():
            return tuple(self.git(self.b, *args) for args in (
                ("rev-parse", "HEAD"), ("symbolic-ref", "--short", "HEAD"),
                ("status", "--porcelain"), ("worktree", "list", "--porcelain"),
                ("for-each-ref", "refs/joulewise/run-state-add/"),
            ))

        before = caller()
        self.assertEqual(before[1].strip(), "fixture-local")
        self.assertIn("?? dirty.txt", before[2])
        self.assertIn(" M RUN_STATE.md", before[2])
        number, head = add.add_git(self.b, request())
        self.assertEqual((number, head), (25, self.remote_head()))
        self.assertEqual(caller(), before)
        self.assertEqual((self.b / add.RUN_STATE).read_text(), "Dirty tracked file.")

    def test_a10_with_file_subject_and_trailers_land_in_one_commit(self):
        extra = self.a / "docs/x.md"
        extra.write_text("Attached file.\n", encoding="utf-8")
        trailers = ["Co-Authored-By: Fixture <typed@example.invalid>", "Signed-off-by: Fixture <typed@example.invalid>"]
        code, output, err = self.call_in(
            self.a, *self.add_flags("--with", "docs/x.md", "--message", "Explicit message",
                                    "--trailer", trailers[0], "--trailer", trailers[1]))
        self.assertEqual((code, output.strip(), err), (0, f"25 {self.remote_head()}", ""))
        self.assertEqual(self.git(self.remote, "rev-list", f"{self.base}..main").splitlines(), [self.remote_head()])
        changed = self.git(self.remote, "diff-tree", "--no-commit-id", "--name-only", "-r", "main").splitlines()
        self.assertEqual(set(changed), {str(add.RUN_STATE), str(add.CURRENT), "docs/x.md"})
        self.assertEqual(self.git(self.remote, "show", "main:docs/x.md"), extra.read_text())
        message = self.git(self.remote, "show", "-s", "--format=%B", "main").strip()
        self.assertEqual(message, "RUN_STATE 25: Explicit message\n\n" + "\n".join(trailers))

    def test_a11_legacy_remote_refuses_add(self):
        self.write_state(LEGACY)
        self.git(self.a, "push", "origin", "HEAD:refs/heads/main")
        head = self.remote_head()
        self.assertNotEqual(head, self.base)
        for flags in (self.add_flags(), ("flush-spool",)):
            with self.subTest(command=flags[0]):
                code, output, error = self.call_in(self.b, *flags)
                self.assertEqual((code, output), (2, ""))
                self.assertIn("run init first", error)
        self.assertEqual(self.remote_head(), head)
        self.assertEqual(list(self.spool.glob("*.json")), [])


if __name__ == "__main__":
    unittest.main()
