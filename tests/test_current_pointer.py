"""Head-pointer checks use synthetic files; the CI case selects only real headings."""

from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts import current_pointer as cp


STAMP = "2026-11-11T03:30:00-08:00"
NEW_STAMP = "2026-11-11T04:00:00-08:00"
T0 = 1794350000
END = T0 + 3600


def seed() -> dict:
    return {"schema": "joulewise.current_pointer.v1", "run_state_top_item": 261,
            "updated": STAMP, "owner": "lead", "armed": None, "wait": None,
            "next_observable": "Lead chooses the next action."}


def waiting() -> dict:
    value = seed()
    value["armed"] = {"plan_id": "synthetic-plan", "t0_epoch_s": T0,
                      "latest_end_epoch_s": END, "host": "synthetic-host"}
    value["wait"] = {"observable": "result_json_exists", "deadline_epoch_s": END,
                     "on_early_or_refused": "Read verdict first; report refusal to lead."}
    return value


class CurrentPointerTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory(prefix="pointer-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.pointer = self.root / "CURRENT spaced.json"
        self.run_state = self.root / "RUN_STATE spaced.md"
        self.run_state.write_text(
            "Current pointer: highest number, newest first from 168.\n"
            "9. **Old history**\n261. **Current**\n256b. **Earlier supplement**\n"
            "168. **Older**\n99. **Old, numerically below 261**\n"
            "Mention 999. **This is prose**\n999. Not a bold heading\n"
            " 999. **Indented list**\n", encoding="utf-8")
        self.write(seed())

    def write(self, value: object) -> None:
        self.pointer.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def cli(self, command: str = "check") -> tuple[int, str, str]:
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = cp.main([command, "--pointer", str(self.pointer),
                            "--run-state", str(self.run_state)])
        return code, output.getvalue(), errors.getvalue()

    def refused(self, value: object, message: str) -> None:
        self.write(value)
        before = self.pointer.read_bytes()
        code, output, errors = self.cli()
        self.assertEqual(code, 1, errors)
        self.assertEqual(output, "")
        self.assertIn(message, errors)
        self.assertEqual(self.pointer.read_bytes(), before)
        expected = [sys.executable, "-B", str(Path(cp.__file__).resolve()), "bump",
                    "--pointer", str(self.pointer), "--run-state", str(self.run_state)]
        self.assertEqual(shlex.split(errors.split("Bump command: ", 1)[1]), expected)

    def test_unarmed_and_armed_acceptance(self) -> None:
        for pointer in (seed(), waiting()):
            with self.subTest(pointer=pointer):
                self.write(pointer)
                self.assertEqual(cp.check(self.pointer, self.run_state), pointer)
                self.assertEqual(self.cli()[0], 0)

    def test_highest_number_instead_of_first_last_or_lexical_order(self) -> None:
        self.assertEqual(cp.top_item(self.run_state), (261, ""))
        self.run_state.write_text("256. **Old**\n256b. **New**\n256a. **Middle**\n")
        self.assertEqual(cp.top_item(self.run_state), (256, "b"))

    def test_missing_numbered_headings_is_not_success(self) -> None:
        self.run_state.write_text("No heading\n261. ordinary list\n")
        self.refused(seed(), "no numbered item headings")

    def test_stale_or_ahead_pointer_refused(self) -> None:
        for number in (260, 262):
            with self.subTest(number=number):
                pointer = seed()
                pointer["run_state_top_item"] = number
                self.refused(pointer, "RUN_STATE highest item is 261")

    def test_item_must_be_positive_integer(self) -> None:
        for value in (True, False, 0, -1, 261.0, "261", None):
            with self.subTest(value=value):
                pointer = seed()
                pointer["run_state_top_item"] = value
                self.refused(pointer, "positive integer")

    def test_optional_suffix_checked_and_absence_allowed(self) -> None:
        self.run_state.write_text("261. **Base**\n261b. **Supplement**\n261a. **Older**\n")
        self.assertEqual(self.cli()[0], 0)
        pointer = seed()
        pointer["run_state_top_item_suffix"] = "b"
        self.write(pointer)
        self.assertEqual(self.cli()[0], 0)
        self.assertIn("item=261b", self.cli("show")[1])
        pointer["run_state_top_item_suffix"] = "a"
        self.refused(pointer, "suffix differs")
        self.run_state.write_text("261. **Base only**\n")
        self.refused(pointer, "suffix differs")

    def test_malformed_suffixes_refused(self) -> None:
        for suffix in (None, True, 1, "", "bb", "B", "1"):
            with self.subTest(suffix=suffix):
                pointer = seed()
                pointer["run_state_top_item_suffix"] = suffix
                self.refused(pointer, "one lowercase letter")

    def test_schema_and_top_level_shapes(self) -> None:
        for value in (None, [], "pointer", 1):
            self.refused(value, "pointer must be an object")
        for version in (None, "joulewise.current_pointer.v2", 1):
            pointer = seed()
            pointer["schema"] = version
            self.refused(pointer, "schema must be joulewise.current_pointer.v1")
        for field in seed():
            with self.subTest(missing=field):
                pointer = seed()
                del pointer[field]
                self.refused(pointer, "missing keys")
        pointer = seed()
        pointer["unexpected"] = "ignored?"
        self.refused(pointer, "unknown keys ['unexpected']")

    def test_updated_requires_valid_iso_time_with_offset(self) -> None:
        for value in (None, 1, "", "2026-11-11", "2026-11-11T03:30:00",
                      "2026-11-11 03:30:00-08:00", "2026-02-30T03:30:00-08:00",
                      "2026-11-11T25:00:00-08:00", "2026-11-11T03:30:00+24:00",
                      "2026-11-11T03:30:00+01:99"):
            with self.subTest(value=value):
                pointer = seed()
                pointer["updated"] = value
                self.refused(pointer, "CURRENT check failed:")
        for value in (STAMP, "2026-11-11T03:30:00Z", "2026-11-11T03:30:00.123+05:30"):
            pointer = seed()
            pointer["updated"] = value
            cp.validate(pointer)

    def test_text_fields_refuse_empty_nontext_and_line_breaks(self) -> None:
        for section, fields in ((None, ("owner", "next_observable")),
                                ("armed", ("plan_id", "host")),
                                ("wait", ("on_early_or_refused",))):
            for field in fields:
                for bad in (None, 5, "", "  ", "line\nline", "tab\t", "nul\x00", "x\u2028y"):
                    with self.subTest(section=section, field=field, bad=bad):
                        pointer = waiting()
                        (pointer if section is None else pointer[section])[field] = bad
                        self.refused(pointer, "single-line text")
        pointer = seed()
        pointer["next_observable"] = "x" * 241
        self.refused(pointer, "at most 240")
        pointer["next_observable"] = "x" * 240
        cp.validate(pointer)

    def test_armed_and_wait_shapes_and_exact_keys(self) -> None:
        for section, required in (("armed", ("plan_id", "t0_epoch_s", "latest_end_epoch_s", "host")),
                                  ("wait", ("observable", "deadline_epoch_s", "on_early_or_refused"))):
            for value in (False, [], "unknown", 0):
                pointer = waiting()
                pointer[section] = value
                self.refused(pointer, section + " must be an object")
            for field in required:
                pointer = waiting()
                del pointer[section][field]
                self.refused(pointer, "missing keys")
            pointer = waiting()
            pointer[section]["extra"] = None
            self.refused(pointer, "unknown keys ['extra']")

    def test_every_epoch_refuses_digit_soup_and_bounds(self) -> None:
        # Explicit independent bounds catch a mutated module constant as well.
        self.assertEqual(cp.MIN_EPOCH, 1767225600)
        self.assertEqual(cp.MAX_EPOCH, 1893456000)
        for section, field in (("armed", "t0_epoch_s"), ("armed", "latest_end_epoch_s"),
                               ("wait", "deadline_epoch_s")):
            for value in (None, True, False, 0, -1, T0 * 1000, 12345678901234567890,
                          1767225599, 1767225600, 1893456000, 1893456001,
                          float(T0), str(T0), "until 2026-11-11 1794350000"):
                with self.subTest(field=field, value=value):
                    pointer = waiting()
                    pointer[section][field] = value
                    self.refused(pointer, "integer epoch seconds")
        for value in (1767225601, 1893455999):
            pointer = waiting()
            pointer["armed"]["t0_epoch_s"] = value
            pointer["armed"]["latest_end_epoch_s"] = value
            pointer["wait"]["deadline_epoch_s"] = value
            cp.validate(pointer)

    def test_end_not_before_t0_and_deadline_not_before_end(self) -> None:
        pointer = waiting()
        pointer["armed"]["latest_end_epoch_s"] = T0 - 1
        self.refused(pointer, "must be >= t0_epoch_s")
        pointer = waiting()
        pointer["wait"]["deadline_epoch_s"] = END - 1
        self.refused(pointer, "must be >= armed.latest_end_epoch_s")
        for deadline in (END, END + 1):
            pointer["wait"]["deadline_epoch_s"] = deadline
            cp.validate(pointer)

    def test_armed_requires_wait_and_non_none_observable(self) -> None:
        pointer = waiting()
        pointer["wait"] = None
        self.refused(pointer, "armed requires wait with a deadline")
        pointer = waiting()
        pointer["wait"]["observable"] = "none"
        self.refused(pointer, "checkable wait, not none")

    def test_closed_observable_vocabulary_all_cases(self) -> None:
        expected = {"result_json_exists", "results_branch_exists", "watchdog_status_state",
                    "pr_merged", "none"}
        self.assertEqual(cp.OBSERVABLES, expected)
        for observable in expected:
            pointer = waiting()
            pointer["armed"] = None
            pointer["wait"]["observable"] = observable
            self.write(pointer)
            self.assertEqual(self.cli()[0], 0)
        for value in (None, [], {}, True, 1, "", "chain_exited", "chain.exited",
                      "RESULT_JSON_EXISTS", "unrecognised", "sleep", "courier_sent"):
            pointer = waiting()
            pointer["wait"]["observable"] = value
            self.refused(pointer, "use result_json_exists instead of chain_exited")

    def test_wait_without_arm_still_validated(self) -> None:
        pointer = waiting()
        pointer["armed"] = None
        pointer["wait"]["deadline_epoch_s"] = "digit soup"
        self.refused(pointer, "integer epoch seconds")

    def test_malformed_json_duplicate_keys_and_nonfinite_constants(self) -> None:
        sources = ["{", "{} trailing", "[" * 1200 + "0" + "]" * 1200,
                   "{\"owner\": 1, \"owner\": 2}",
                   json.dumps(waiting()).replace('"host": "synthetic-host"',
                                                 '"host": "a", "host": "b"')]
        for constant in ("NaN", "Infinity", "-Infinity"):
            sources.append(json.dumps(seed()).replace("261", constant))
        for source in sources:
            with self.subTest(source=source):
                self.pointer.write_text(source)
                self.assertEqual(self.cli()[0], 1)
                before = self.pointer.read_bytes()
                self.assertEqual(self.cli("bump")[0], 1)
                self.assertEqual(self.pointer.read_bytes(), before)

    def test_invalid_utf8_and_missing_or_unreadable_files(self) -> None:
        self.pointer.write_bytes(b"\xff")
        self.assertEqual(self.cli()[0], 1)
        self.pointer.unlink()
        self.assertEqual(self.cli()[0], 1)
        self.write(seed())
        self.run_state.unlink()
        self.assertEqual(self.cli()[0], 1)
        with mock.patch.object(Path, "read_bytes", side_effect=PermissionError("denied")):
            self.assertEqual(self.cli()[0], 1)

    def test_bump_preserves_every_other_byte_key_order_and_value(self) -> None:
        pointer = waiting()
        pointer["run_state_top_item"] = 9
        pointer["owner"] = 'lead says "updated": 249, café'
        pointer["next_observable"] = "updated 249"
        # Deliberately noncanonical formatting, order, escapes, CRLF and nested
        # occurrences of update-key words. Only the two value tokens may move.
        pointer = dict(reversed(list(pointer.items())))
        source = " \r\n" + json.dumps(pointer, ensure_ascii=True, indent="\t").replace("\n", "\r\n") + "\r\n \t"
        self.pointer.write_bytes(source.encode())
        longer_stamp = "2026-11-11T12:00:00.123456+00:00"
        cp.bump(self.pointer, self.run_state, updated=longer_stamp)
        expected = source.replace('"run_state_top_item": 9', '"run_state_top_item": 261').replace(
            '"updated": "' + STAMP + '"', '"updated": "' + longer_stamp + '"')
        self.assertEqual(self.pointer.read_bytes(), expected.encode())
        actual = cp.check(self.pointer, self.run_state)
        self.assertEqual(list(actual), list(pointer))
        for field in pointer.keys() - {"run_state_top_item", "updated"}:
            self.assertEqual(actual[field], pointer[field])

    def test_bump_compact_json_and_default_timestamp(self) -> None:
        self.pointer.write_text(json.dumps(seed(), separators=(",", ":")))
        self.run_state.write_text("262. **Next**\n")
        self.assertEqual(self.cli("bump")[0], 0)
        pointer = cp.check(self.pointer, self.run_state)
        self.assertEqual(pointer["run_state_top_item"], 262)
        self.assertIsNotNone(cp.datetime.fromisoformat(pointer["updated"]).utcoffset())
        self.assertEqual(pointer["armed"], None)
        self.assertEqual(pointer["wait"], None)

    def test_bump_preserves_matching_suffix_and_refuses_suffix_change(self) -> None:
        pointer = seed()
        pointer["run_state_top_item_suffix"] = "b"
        self.write(pointer)
        before = self.pointer.read_bytes()
        self.assertEqual(self.cli("bump")[0], 1)
        self.assertEqual(self.pointer.read_bytes(), before)
        self.run_state.write_text("262b. **Next supplement**\n")
        cp.bump(self.pointer, self.run_state, updated=NEW_STAMP)
        self.assertEqual(cp.check(self.pointer, self.run_state)["run_state_top_item_suffix"], "b")

    def test_bump_refuses_other_invalid_fields_and_invalid_replacement(self) -> None:
        pointer = waiting()
        pointer["wait"]["deadline_epoch_s"] = END - 1
        self.write(pointer)
        before = self.pointer.read_bytes()
        self.assertEqual(self.cli("bump")[0], 1)
        self.assertEqual(self.pointer.read_bytes(), before)
        self.write(seed())
        before = self.pointer.read_bytes()
        with self.assertRaises(ValueError):
            cp.bump(self.pointer, self.run_state, updated="not a timestamp")
        self.assertEqual(self.pointer.read_bytes(), before)

    def test_failed_write_is_failure_and_no_headings_never_writes(self) -> None:
        with mock.patch.object(Path, "write_bytes", side_effect=OSError("read only")):
            self.assertEqual(self.cli("bump")[0], 1)
        before = self.pointer.read_bytes()
        self.run_state.write_text("no headings")
        self.assertEqual(self.cli("bump")[0], 1)
        self.assertEqual(self.pointer.read_bytes(), before)

    def test_show_one_line_and_refuses_stale_or_invalid_pointer(self) -> None:
        for pointer in (seed(), waiting()):
            self.write(pointer)
            code, output, errors = self.cli("show")
            self.assertEqual((code, errors), (0, ""))
            self.assertEqual(len(output.splitlines()), 1)
            self.assertIn("item=261 owner=lead", output)
            self.assertIn("next=" + pointer["next_observable"], output)
            if pointer["armed"] is None:
                self.assertIn("armed=none wait=none", output)
            else:
                self.assertIn("armed=synthetic-plan@synthetic-host", output)
                self.assertIn(f"t0={T0} end={END}", output)
                self.assertIn(f"wait=result_json_exists deadline={END}", output)
        self.run_state.write_text("262. **Next**\n")
        self.assertEqual(self.cli("show")[:2], (1, ""))
        self.write({"unknown": "not a success"})
        self.assertEqual(self.cli("show")[:2], (1, ""))

    def test_usage_errors_are_exit_two_and_help_is_zero(self) -> None:
        for argv in ([], ["unknown"], ["check", "--unknown"], ["bump", "--pointer"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as raised:
                cp.main(argv)
            self.assertEqual(raised.exception.code, 2)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as raised:
            cp.main(["--help"])
        self.assertEqual(raised.exception.code, 0)

    def test_entrypoint_exit_codes_and_failure_command_is_executable(self) -> None:
        script = Path(cp.__file__).resolve()
        self.run_state.write_text("262. **Next**\n")
        result = subprocess.run([sys.executable, "-B", str(script), "check",
                                 "--pointer", str(self.pointer), "--run-state", str(self.run_state)],
                                capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1)
        command = shlex.split(result.stderr.split("Bump command: ", 1)[1])
        bumped = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(bumped.returncode, 0, bumped.stderr)
        self.assertEqual(cp.check(self.pointer, self.run_state)["run_state_top_item"], 262)


class RepositoryPointerTests(unittest.TestCase):
    def test_repository_pointer_matches_real_numbered_headings(self) -> None:
        # check/top_item select only heading numbers and optional letters.
        # No RUN_STATE prose, armed plan inference, custody or result read.
        pointer = cp.check(cp.ROOT / "docs/process/CURRENT.json", cp.ROOT / "RUN_STATE.md")
        self.assertEqual(pointer["schema"], "joulewise.current_pointer.v1")


if __name__ == "__main__":
    unittest.main()
