"""Synthetic-only checks for RL-53 W-8. No study data or model imports."""

from __future__ import annotations

import copy
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from joulewise import unseal_record as unseal
from scripts import show_outcomes_guard as guard


def record() -> dict:
    return {
        "schema": "joulewise.unseal_record.v1", "given_by": "Synthetic owner",
        "given_at": "2026-11-11T08:00:00-08:00", "words": "  Open these paths.\nÉ  ",
        "block": "block6", "verdict_sha256": "ab" * 32,
        "verdict_path": "never-open/verdict.json",
        "paths_opened": ["outcomes/*.json", "summary.txt"],
        "stays_sealed": ["outcomes/held-*.json"],
        "seats_may_read": ["research-lead"], "recorded_by": "Synthetic recorder",
        "recorded_at": "2026-11-11T16:01:00Z",
    }


class ValidationTests(unittest.TestCase):
    def refuses(self, value, code):
        with self.assertRaises(unseal.UnsealRecordError) as caught:
            unseal.validate(value)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(str(caught.exception), code)

    def test_valid_exact_fields_and_no_mutation(self):
        value = record()
        before = copy.deepcopy(value)
        self.assertIsNone(unseal.validate(value))
        self.assertEqual(value, before)
        value["stays_sealed"] = []
        value["verdict_sha256"] = value["verdict_sha256"].upper()
        self.assertIsNone(unseal.validate(value))

    def test_every_required_field(self):
        expected = {"schema", "given_by", "given_at", "words", "block", "verdict_sha256",
                    "verdict_path", "paths_opened", "stays_sealed", "seats_may_read",
                    "recorded_by", "recorded_at"}
        self.assertEqual(set(record()), expected)
        for field in expected:
            with self.subTest(field=field):
                value = record()
                del value[field]
                self.refuses(value, "missing_field")

    def test_nonmapping_unknown_and_schema(self):
        for value in (None, [], "record", 1):
            with self.subTest(value=value):
                self.refuses(value, "not_mapping")
        for key in ("extra", "signature", "schema_version", 3):
            with self.subTest(key=key):
                self.refuses(dict(record(), **{key: True}) if isinstance(key, str)
                             else {**record(), key: True}, "unknown_key")
        for value in (None, True, 1, [], "joulewise.unseal_record.v2"):
            with self.subTest(schema=value):
                self.refuses({**record(), "schema": value}, "schema_invalid")

    def test_each_text_field(self):
        for field in ("given_by", "words", "recorded_by"):
            for value in (None, True, 2, [], {}, "", " \n\t", "\ud800"):
                with self.subTest(field=field, value=value):
                    self.refuses({**record(), field: value}, field + "_invalid")

    def test_each_time_field(self):
        for field in ("given_at", "recorded_at"):
            for value in (None, 1, "", "2026-11-11", "2026-11-11T12:00:00",
                          "2026-11-11T12:00:00+24:00", "2026-11-11T12:00:00+00:60",
                          "2026-02-30T12:00:00+00:00", "2026-11-11T25:00:00Z"):
                with self.subTest(field=field, value=value):
                    self.refuses({**record(), field: value}, field + "_invalid")
            for value in ("2026-11-11T12:00:00Z", "2026-11-11T12:00:00.123+05:30"):
                with self.subTest(field=field, valid=value):
                    self.assertIsNone(unseal.validate({**record(), field: value}))

    def test_block_and_digest(self):
        for value in (None, 6, "", "..", "../block6", "/block6", "block 6", "block6\n"):
            with self.subTest(block=value):
                self.refuses({**record(), "block": value}, "block_invalid")
        self.assertIsNone(unseal.validate({**record(), "block": "align-v4-W1"}))
        for value in (None, 1, "a" * 63, "a" * 65, "z" * 64, "ab" * 32 + "\n"):
            with self.subTest(digest=value):
                self.refuses({**record(), "verdict_sha256": value}, "verdict_sha256_invalid")

    def test_every_list_field(self):
        for field in ("paths_opened", "stays_sealed", "seats_may_read"):
            for value in (None, "path", {}, (), ["ok", None], [1], [""], ["  "]):
                with self.subTest(field=field, value=value):
                    code = field + "_invalid" if not isinstance(value, list) or field == "seats_may_read" else "path_invalid"
                    self.refuses({**record(), field: value}, code)
        for field in ("paths_opened", "seats_may_read"):
            with self.subTest(empty=field):
                self.refuses({**record(), field: []}, field + "_invalid")
        self.refuses({**record(), "seats_may_read": ["\ud800"]}, "seats_may_read_invalid")

    def test_all_path_fields_reject_escapes_and_empty_patterns(self):
        bad = (None, 1, "", " ", ".", "./", "../x", "a/../x", "a/..", "/x", "//host/x",
               "C:/x", "C:x", "./C:/x", ".\\C:\\x", "C:\\x", "\\host\\x", "a\\..\\x", "a\0b", "a\nb", "\ud800")
        for field in ("verdict_path", "paths_opened", "stays_sealed"):
            for path in bad:
                with self.subTest(field=field, path=path):
                    value = path if field == "verdict_path" else [path]
                    self.refuses({**record(), field: value}, "path_invalid")

    def test_canonical_bytes_and_digest_independent_oracle(self):
        value = record()
        expected = json.dumps(value, sort_keys=True, ensure_ascii=False,
                              separators=(",", ":")).encode("utf-8")
        self.assertEqual(unseal.canonical_bytes(dict(reversed(list(value.items())))), expected)
        self.assertEqual(unseal.record_sha256(value), hashlib.sha256(expected).hexdigest())
        self.assertEqual(json.loads(expected)["words"], value["words"])
        changed = {**value, "words": value["words"].strip()}
        self.assertNotEqual(unseal.record_sha256(value), unseal.record_sha256(changed))
        for operation in (unseal.canonical_bytes, unseal.record_sha256):
            with self.assertRaises(unseal.UnsealRecordError):
                operation({**value, "unexpected": True})

    def test_load_and_duplicate_keys_and_malformed_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "record.json"
            path.write_bytes(unseal.canonical_bytes(record()))
            self.assertEqual(unseal.load(path), record())
            for raw, code in ((b'{"schema":1,"schema":2}', "duplicate_key"),
                              (b"{", "record_unreadable"), (b"\xff", "record_unreadable"),
                              (b"[]", "not_mapping"), (b"{}", "missing_field")):
                with self.subTest(raw=raw):
                    path.write_bytes(raw)
                    with self.assertRaises(unseal.UnsealRecordError) as caught:
                        unseal.load(path)
                    self.assertEqual(caught.exception.code, code)
            path.unlink()
            with self.assertRaises(unseal.UnsealRecordError) as caught:
                unseal.load(path)
            self.assertEqual(caught.exception.code, "record_unreadable")


class CommittedTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.records = self.root / "docs" / "unseals"
        self.records.mkdir(parents=True)
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        self.git("init", "--quiet")
        for key, value in (("user.name", "Synthetic test"), ("user.email", "test@example.invalid"),
                           ("commit.gpgsign", "false"), ("core.hooksPath", os.devnull)):
            self.git("config", key, value)
        self.git("commit", "--quiet", "--allow-empty", "-m", "Synthetic root")

    def git(self, *args):
        return subprocess.run(["git", "-C", str(self.root), *args], env=self.env,
                              check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

    def write(self, value=None, name="block6-20261111.json", *, commit=True):
        path = self.records / name
        path.write_text(json.dumps(record() if value is None else value), encoding="utf-8")
        if commit:
            self.git("add", "docs/unseals")
            self.git("commit", "--quiet", "-m", "Synthetic unseal")
        return path

    def require(self, **kw):
        return unseal.require_unseal(self.records, **{"block": "block6", "verdict_sha256": "ab" * 32, **kw})

    def refuses(self, code, **kw):
        with self.assertRaises(unseal.UnsealRefused) as caught:
            self.require(**kw)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(str(caught.exception), code)

    def test_empty_directory_and_missing_directory(self):
        self.refuses("no_record")
        self.records.rmdir()
        self.refuses("no_record")

    def test_unreadable_directory(self):
        with mock.patch.object(Path, "iterdir", side_effect=PermissionError):
            self.refuses("records_unreadable")

    def test_block_and_digest_mismatch_and_invalid_requests(self):
        self.write()
        self.refuses("block_mismatch", block="align-v4-W1")
        self.refuses("digest_mismatch", verdict_sha256="cd" * 32)
        for value in ("", "../block6", None):
            self.refuses("block_invalid", block=value)
        for value in ("", "0" * 63, "g" * 64, None):
            self.refuses("verdict_sha256_invalid", verdict_sha256=value)
        self.assertEqual(self.require(verdict_sha256=("AB" * 32)), record())

    def test_no_path_check_and_unrelated_files(self):
        self.write()
        (self.records / "README.md").write_text("Not JSON.")
        self.assertEqual(self.require(), record())

    def test_new_verdict_requires_new_record(self):
        self.write()
        self.refuses("digest_mismatch", verdict_sha256="cd" * 32)
        fresh = {**record(), "verdict_sha256": "cd" * 32}
        self.write(fresh, "block6-20261112.json")
        self.assertEqual(self.require(verdict_sha256="cd" * 32), fresh)
        self.assertEqual(self.require(), record())

    def test_untracked_staged_edited_and_committed_bytes(self):
        path = self.write(commit=False)
        self.refuses("record_not_committed")
        self.git("add", "docs/unseals")
        self.refuses("record_not_committed")
        self.git("commit", "--quiet", "-m", "Synthetic unseal")
        self.assertEqual(self.require(), record())
        path.write_text(json.dumps(record()) + "\n")
        self.refuses("record_not_committed")
        self.git("add", "docs/unseals")
        self.refuses("record_not_committed")
        self.git("commit", "--quiet", "-m", "Synthetic byte change")
        self.assertEqual(self.require(), record())

    def test_nonrepository_and_git_failure(self):
        self.write()
        for failure in (OSError, subprocess.TimeoutExpired("git", 10)):
            with self.subTest(failure=failure), mock.patch.object(unseal.subprocess, "run", side_effect=failure):
                self.refuses("commit_unverifiable")
        with mock.patch.object(unseal.subprocess, "run", return_value=mock.Mock(returncode=1)):
            self.refuses("commit_unverifiable")
        with tempfile.TemporaryDirectory() as temp:
            other = Path(temp)
            (other / "block6-20261111.json").write_text(json.dumps(record()))
            with self.assertRaises(unseal.UnsealRefused) as caught:
                unseal.require_unseal(other, block="block6", verdict_sha256="ab" * 32)
            self.assertEqual(caught.exception.code, "commit_unverifiable")

    def test_ambiguous_matching_records(self):
        self.write()
        self.write(name="block6-20261112.json")
        self.refuses("ambiguous_record")

    def test_git_metadata_is_fail_closed_and_local_only(self):
        path = self.records / "block6-20261111.json"
        prefix = [os.fsencode(self.root), b"a" * 40]
        for entry, code in (
            (b"120000 blob abc\tdocs/unseals/block6-20261111.json\0", "record_not_committed"),
            (b"100644 tree abc\tdocs/unseals/block6-20261111.json\0", "record_not_committed"),
            (b"100644 blob abc\tother.json\0", "record_not_committed"),
            (b"malformed", "commit_unverifiable"),
            (b"100644 blob\tdocs/unseals/block6-20261111.json\0", "commit_unverifiable"),
        ):
            with self.subTest(entry=entry), mock.patch.object(unseal, "_git", side_effect=prefix + [entry]):
                with self.assertRaises(unseal.UnsealRefused) as caught:
                    unseal._committed(path, b"record")
                self.assertEqual(caught.exception.code, code)
        for mode in (b"100644", b"100755"):
            entry = mode + b" blob abc\tdocs/unseals/block6-20261111.json\0"
            with mock.patch.object(unseal, "_git", side_effect=prefix + [entry, b"record"]):
                self.assertIsNone(unseal._committed(path, b"record"))
        with mock.patch.object(unseal, "_git", return_value=os.fsencode(self.root / "unrelated")):
            with self.assertRaises(unseal.UnsealRefused) as caught:
                unseal._committed(path, b"record")
            self.assertEqual(caught.exception.code, "commit_unverifiable")
        for failure in (PermissionError, RuntimeError):
            with self.subTest(resolve_failure=failure), mock.patch.object(Path, "resolve", side_effect=failure):
                with self.assertRaises(unseal.UnsealRefused) as caught:
                    unseal._committed(path, b"record")
                self.assertEqual(caught.exception.code, "commit_unverifiable")
        with mock.patch.dict(os.environ, {"GIT_DIR": "/must-not-use", "GIT_CONFIG_COUNT": "1"}), \
                mock.patch.object(unseal.subprocess, "run", return_value=mock.Mock(returncode=0, stdout=b"ok")) as run:
            self.assertEqual(unseal._git(self.root, "rev-parse", "HEAD"), b"ok")
        command = run.call_args.args[0]
        env = run.call_args.kwargs["env"]
        self.assertNotIn("GIT_DIR", env)
        self.assertNotIn("GIT_CONFIG_COUNT", env)
        self.assertEqual(env["GIT_CONFIG_GLOBAL"], os.devnull)
        self.assertEqual(env["GIT_CONFIG_NOSYSTEM"], "1")
        self.assertEqual(env["GIT_NO_LAZY_FETCH"], "1")
        self.assertIn("core.fsmonitor=false", command)
        self.assertEqual(command[-2:], ["rev-parse", "HEAD"])
        self.assertEqual(run.call_args.kwargs["timeout"], 10)

    def test_invalid_record_never_allows(self):
        path = self.write()
        for raw in ("{}", "[]", "not-json", '{"x":1,"x":2}', json.dumps({**record(), "extra": True})):
            with self.subTest(raw=raw):
                path.write_text(raw)
                self.refuses("record_invalid")
        path.unlink()
        path.mkdir()
        self.refuses("record_invalid")

    def test_invalid_filename_and_calendar_date(self):
        for name in ("wrong-20261111.json", "block6-20260230.json", "block6-2026111.json"):
            with self.subTest(name=name):
                path = self.write(name=name, commit=False)
                self.refuses("record_invalid")
                path.unlink()

    def test_symlink_record_never_followed(self):
        target = self.root / "unopened.json"
        target.write_text(json.dumps(record()))
        (self.records / "block6-20261111.json").symlink_to(target)
        with mock.patch("builtins.open", side_effect=AssertionError("must not open")):
            self.refuses("record_invalid")

    def test_paths_exact_globs_normalization_and_case(self):
        self.write()
        for path in ("summary.txt", "outcomes/value.json", "outcomes/nested/value.json",
                     "./outcomes//value.json", "outcomes\\value.json"):
            with self.subTest(allowed=path):
                self.assertEqual(self.require(path=path), record())
        for path in ("summary.txt.bak", "other/value.json", "OUTCOMES/value.json"):
            with self.subTest(refused=path):
                self.refuses("path_not_opened", path=path)

    def test_pattern_normalization_and_stays_sealed_precedence(self):
        value = {**record(), "paths_opened": ["./outcomes//*.json", "outcomes\\*"],
                 "stays_sealed": ["./outcomes//held-?.json", "outcomes\\secret.json"]}
        self.write(value)
        self.assertEqual(self.require(path="outcomes/a.json"), value)
        for path in ("outcomes/held-1.json", "./outcomes//held-1.json", "outcomes\\secret.json"):
            with self.subTest(path=path):
                self.refuses("stays_sealed", path=path)
        # Denial wins even if no opened pattern covers the requested path.
        self.refuses("path_not_opened", path="elsewhere/x.json")

    def test_stays_sealed_without_open_match_and_empty_sealed(self):
        value = {**record(), "stays_sealed": ["elsewhere/*"]}
        path = self.write(value)
        self.refuses("stays_sealed", path="elsewhere/x.json")
        path.unlink()
        self.write({**record(), "stays_sealed": []})
        self.assertEqual(self.require(path="outcomes/held-1.json")["stays_sealed"], [])

    def test_requested_path_escapes_even_with_wildcard_permission(self):
        self.write({**record(), "paths_opened": ["*"]})
        for path in ("", ".", "../x", "a/../x", "/x", "//host/x", "C:/x", "./C:/x", "C:x", "a\\..\\x", "a\0b"):
            with self.subTest(path=path):
                self.refuses("path_invalid", path=path)

    def invoke(self, argv):
        with mock.patch.object(guard, "RECORDS_DIR", self.records), \
                contextlib.redirect_stdout(io.StringIO()) as stdout, \
                contextlib.redirect_stderr(io.StringIO()) as stderr:
            try:
                code = guard.main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, stdout.getvalue(), stderr.getvalue()

    def test_guard_three_exits_and_no_contents_printed(self):
        verdict = self.root / "explicit-verdict.bin"
        verdict.write_bytes(b"synthetic private bytes\x00\xff" * 60000)
        value = {**record(), "verdict_sha256": hashlib.sha256(verdict.read_bytes()).hexdigest()}
        self.write(value)
        argv = ["check", "--block", "block6", "--verdict", str(verdict), "--path", "summary.txt"]
        self.assertEqual(self.invoke(argv), (0, "", ""))
        verdict.write_bytes(b"a different verdict")
        self.assertEqual(self.invoke(argv), (1, "", "digest_mismatch\n"))
        for args in ([], ["check"], ["unknown"], argv + ["--unknown"]):
            with self.subTest(usage=args):
                code, stdout, stderr = self.invoke(args)
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertIn("usage:", stderr)
        verdict.unlink()
        self.assertEqual(self.invoke(argv), (1, "", "verdict_unreadable\n"))

    def test_guard_propagates_path_refusal_and_does_not_cache(self):
        verdict = self.root / "verdict.bin"
        verdict.write_bytes(b"synthetic")
        self.write({**record(), "verdict_sha256": hashlib.sha256(b"synthetic").hexdigest()})
        argv = ["check", "--block", "block6", "--verdict", str(verdict)]
        self.assertEqual(self.invoke(argv + ["--path", "outcomes/held-1.json"]), (1, "", "stays_sealed\n"))
        self.assertEqual(self.invoke(argv), (0, "", ""))
        self.git("rm", "--quiet", "docs/unseals/block6-20261111.json")
        self.git("commit", "--quiet", "-m", "Synthetic removal")
        self.assertEqual(self.invoke(argv), (1, "", "no_record\n"))

    def test_guard_script_entrypoint(self):
        verdict = self.root / "synthetic.bin"
        verdict.write_bytes(b"never print this")
        # Run the real entry point against a disposable repo, including exit 0.
        for source in ("joulewise/unseal_record.py", "scripts/show_outcomes_guard.py"):
            destination = self.root / source
            destination.parent.mkdir(exist_ok=True)
            destination.write_bytes((guard.ROOT / source).read_bytes())
        self.write({**record(), "verdict_sha256": hashlib.sha256(verdict.read_bytes()).hexdigest()})
        command = [sys.executable, "-B", str(self.root / "scripts/show_outcomes_guard.py")]
        allowed = subprocess.run(command + ["check", "--block", "block6", "--verdict", str(verdict)],
                                 capture_output=True, check=False, timeout=10)
        self.assertEqual((allowed.returncode, allowed.stdout, allowed.stderr), (0, b"", b""))
        result = subprocess.run(command + ["check", "--block", "synthetic-nonexistent", "--verdict", str(verdict)],
                                capture_output=True, check=False, timeout=10)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertEqual(result.stderr, b"block_mismatch\n")
        usage = subprocess.run(command, capture_output=True, check=False, timeout=10)
        self.assertEqual(usage.returncode, 2)

    def test_no_record_named_path_is_ever_opened_or_statted(self):
        verdict = self.root / "explicit.bin"
        verdict.write_bytes(b"synthetic")
        value = {**record(), "verdict_sha256": hashlib.sha256(b"synthetic").hexdigest()}
        record_path = self.write(value)
        forbidden = {value["verdict_path"], *value["paths_opened"], *value["stays_sealed"], "outcomes/a.json"}
        calls = []

        def track(operation, original):
            def wrapped(path, *args, **kwargs):
                if not isinstance(path, int):
                    name = os.fspath(path)
                    for item in forbidden:
                        self.assertFalse(name == item or name.endswith("/" + item), name)
                    calls.append((operation, name))
                return original(path, *args, **kwargs)
            return wrapped

        import builtins
        with mock.patch("builtins.open", track("open", builtins.open)), \
                mock.patch("io.open", track("io.open", io.open)), \
                mock.patch("os.open", track("os.open", os.open)), \
                mock.patch("os.stat", track("stat", os.stat)), \
                mock.patch("os.lstat", track("lstat", os.lstat)):
            self.assertEqual(unseal.load(record_path), value)
            self.assertIsNone(unseal.validate(value))
            unseal.canonical_bytes(value)
            unseal.record_sha256(value)
            self.assertEqual(self.require(path="outcomes/a.json", verdict_sha256=value["verdict_sha256"]), value)
            self.assertEqual(self.invoke(["check", "--block", "block6", "--verdict", str(verdict),
                                          "--path", "outcomes/a.json"]), (0, "", ""))
        opened = [name for operation, name in calls if operation in ("open", "io.open", "os.open")]
        self.assertEqual(set(opened), {str(record_path), str(verdict)})
        self.assertGreaterEqual(opened.count(str(record_path)), 3)
        self.assertEqual(opened.count(str(verdict)), 1)


class RepositoryRecordsTests(unittest.TestCase):
    def test_all_repository_records_validate_including_empty_directory(self):
        directory = Path(__file__).resolve().parents[1] / "docs" / "unseals"
        self.assertTrue(directory.is_dir())
        for path in sorted(directory.glob("*.json")):
            with self.subTest(record=path.name):
                value = unseal.load(path)
                self.assertRegex(path.name, r"^" + value["block"] + r"-[0-9]{8}\.json$")
                self.assertEqual(unseal.require_unseal(directory, block=value["block"],
                                                      verdict_sha256=value["verdict_sha256"]), value)


if __name__ == "__main__":
    unittest.main()
