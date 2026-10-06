"""The append-only flag sink: fsync per line, dedup, never rewrites."""

from __future__ import annotations

import json
import multiprocessing
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from joulewise.flags import sink as sink_module
from joulewise.flags.schema import FlagSchemaError, make_flag, make_interval, make_scope, make_source
from joulewise.flags.sink import FlagSink, append_json_line, read_flags

EMITTED = {"wall_s": 1.0, "monotonic_ns": 1, "boot_session_uuid": None}


def flag(run_id: str, value: int = 1):
    return make_flag(
        code="clock.step_overlap",
        family="PHYSICS_IN_SPAN",
        klass="PHYSICS",
        scope=make_scope("member", run_id=run_id),
        source=make_source("harvest", "test"),
        observed={"value": value},
        interval=make_interval(monotonic_ns=(1, 2)),
        emitted=EMITTED,
    )


def _append_many(path: str, start: int) -> None:
    target = FlagSink(path)
    for index in range(start, start + 20):
        target.append(flag(f"r{index % 25:02d}"))


class FlagSinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.path = Path(self.directory.name) / "custody" / "flags" / "window.jsonl"

    def tearDown(self) -> None:
        self.directory.cleanup()

    def test_append_writes_one_canonical_line_and_fsyncs_each(self) -> None:
        target = FlagSink(self.path)
        with mock.patch.object(sink_module.os, "fsync", wraps=os.fsync) as fsync:
            self.assertTrue(target.append(flag("r01")))
            self.assertTrue(target.append(flag("r02")))
        self.assertGreaterEqual(fsync.call_count, 2)
        lines = self.path.read_bytes().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["scope"]["run_id"], "r01")

    def test_duplicate_flag_id_is_not_written_again_even_by_a_new_sink(self) -> None:
        FlagSink(self.path).append(flag("r01"))
        second = FlagSink(self.path)
        self.assertFalse(second.append(flag("r01")))
        self.assertTrue(second.append(flag("r01", value=2)))
        self.assertEqual(len(self.path.read_bytes().splitlines()), 2)

    def test_existing_bytes_are_never_rewritten(self) -> None:
        target = FlagSink(self.path)
        target.append(flag("r01"))
        before = self.path.read_bytes()
        target.append(flag("r02"))
        self.assertTrue(self.path.read_bytes().startswith(before))

    def test_torn_last_line_is_terminated_and_reported_not_fatal(self) -> None:
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(json.dumps(flag("r01")).encode() + b"\n" + b'{"torn": ')
        target = FlagSink(self.path)
        self.assertTrue(target.append(flag("r02")))
        flags, problems = read_flags(self.path)
        self.assertEqual([f["scope"]["run_id"] for f in flags], ["r01", "r02"])
        self.assertEqual(len(problems), 1)

    def test_truncation_is_detected(self) -> None:
        target = FlagSink(self.path)
        target.append(flag("r01"))
        target.append(flag("r02"))
        self.path.write_bytes(b"")
        with self.assertRaises(OSError):
            target.append(flag("r03"))

    def test_malformed_flag_is_refused_before_any_write(self) -> None:
        bad = flag("r01")
        bad["code"] = "Not A Code"
        with self.assertRaises(FlagSchemaError):
            FlagSink(self.path).append(bad)
        self.assertFalse(self.path.exists())

    def test_concurrent_writers_deduplicate(self) -> None:
        context = multiprocessing.get_context("spawn")
        workers = [context.Process(target=_append_many, args=(str(self.path), start)) for start in (0, 5, 10)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(60)
            self.assertEqual(worker.exitcode, 0)
        flags, problems = read_flags(self.path)
        self.assertEqual(problems, [])
        ids = [f["flag_id"] for f in flags]
        self.assertEqual(len(ids), len(set(ids)))
        raw_lines = self.path.read_bytes().splitlines()
        self.assertEqual(len(raw_lines), len(ids))
        self.assertEqual(len(ids), 25)

    def test_read_flags_skips_bad_lines_and_duplicates(self) -> None:
        self.path.parent.mkdir(parents=True)
        good = json.dumps(flag("r01")).encode()
        self.path.write_bytes(good + b"\nnot json\n" + good + b"\n" + b'{"code": "x"}\n')
        flags, problems = read_flags(self.path)
        self.assertEqual(len(flags), 1)
        self.assertEqual(len(problems), 2)
        self.assertEqual(read_flags(self.path.parent / "absent.jsonl"), ([], []))

    def test_append_json_line_appends_with_newline(self) -> None:
        log = Path(self.directory.name) / "runs.jsonl"
        append_json_line(log, {"a": 1})
        log.write_bytes(log.read_bytes() + b'{"torn":')
        append_json_line(log, {"b": 2})
        lines = log.read_bytes().splitlines()
        self.assertEqual(json.loads(lines[0]), {"a": 1})
        self.assertEqual(json.loads(lines[-1]), {"b": 2})


if __name__ == "__main__":
    unittest.main()
