"""Deterministic pointer generation. All declarations and errors are synthetic."""

from __future__ import annotations

import contextlib
import io
import itertools
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from scripts import gen_current as gc


T0 = "2026-11-10T20:53:00-08:00"
END = "2026-11-11T19:03:00-08:00"
DEADLINE = "2026-11-11T19:33:00-08:00"


def fields() -> dict[str, str]:
    return {"owner": "magistrate", "armed": "synthetic-plan", "host": "synthetic-host",
            "t0": T0, "latest_end": END, "wait": "result_json_exists",
            "deadline": DEADLINE, "on_early_or_refused": "read verdict first; ask lead",
            "next_observable": "synthetic result.json: verdict"}


def block(values=None, item="262", heading="2026-11-11 Current", gap="\n") -> str:
    values = fields() if values is None else values
    return (f"{item}. **{heading}**\n" + gap + "```pointer\n"
            + "".join(f"{key}: {value}\n" for key, value in values.items()) + "```\n")


def unarmed() -> dict[str, str]:
    return {"owner": "lead", "wait": "none", "next_observable": "lead chooses"}


def expected() -> dict:
    return {"schema": "joulewise.current_pointer.v1", "source_item": "262",
            "source_item_heading_date": "2026-11-11", "owner": "magistrate",
            "armed": {"plan_id": "synthetic-plan", "host": "synthetic-host",
                      "t0_epoch_s": 1794372780, "latest_end_epoch_s": 1794452580},
            "wait": {"observable": "result_json_exists", "deadline_epoch_s": 1794454380,
                     "on_early_or_refused": "read verdict first; ask lead"},
            "next_observable": "synthetic result.json: verdict"}


class RenderTests(unittest.TestCase):
    def refused(self, text, code, line):
        with self.assertRaises(gc.PointerError) as caught:
            gc.render(text)
        self.assertIn(f"RUN_STATE line {line}: {code}:", str(caught.exception))

    def test_exact_schema_and_known_offset_epochs(self):
        self.assertEqual(json.loads(gc.render(block())), expected())
        self.assertEqual(gc.MIN_EPOCH, 1767225600)
        self.assertEqual(gc.MAX_EPOCH, 1893456000)
        gc.validate(expected())

    def test_no_pointer_document_without_any_headings(self):
        document = {"schema": "joulewise.current_pointer.v1", "source_item": None,
                    "source_item_heading_date": None, "owner": None, "armed": None,
                    "wait": None, "next_observable": None}
        for text in ("", "ordinary text\n", "261. **No declaration**\n"):
            self.assertEqual(json.loads(gc.render(text)), document)
        gc.validate(document)

    def test_deterministic_canonical_bytes_and_unicode(self):
        values = fields()
        values["owner"] = "léad ⚡"
        first = gc.render(block(values))
        self.assertEqual(first, gc.render(block(values)))
        self.assertEqual(first, (json.dumps(json.loads(first), indent=2, sort_keys=True,
                                           ensure_ascii=False) + "\n").encode("utf-8"))
        self.assertIn("léad ⚡".encode(), first)
        self.assertEqual(gc.render(block(values, gap="")), first)
        self.assertEqual(gc.render(block(values, gap="\n\n \t\n")), first)
        self.assertEqual(gc.render(block(values).replace("\n", "\r\n")), first)

    def test_newer_blockless_item_leaves_bytes_unchanged(self):
        old = block(item="256b")
        self.assertEqual(gc.render("999. **New ordinary item**\nSome prose.\n" + old), gc.render(old))

    def test_numeric_suffix_order_regardless_of_file_order(self):
        for items, winner in ((("256", "256a", "256b"), "256b"),
                              (("256b", "257", "255"), "257"), (("9", "10", "2"), "10")):
            for order in itertools.permutations(items):
                text = "\n".join(block(item=item, heading="No date") for item in order)
                pointer = json.loads(gc.render(text))
                self.assertEqual(pointer["source_item"], winner)
                self.assertIsNone(pointer["source_item_heading_date"])

    def test_older_block_below_newer_block_cannot_replace_it(self):
        newer = fields()
        newer["owner"] = "new owner"
        self.assertEqual(gc.render(block(newer, item="257") + block(item="256b")),
                         gc.render(block(newer, item="257")))

    def test_first_date_is_from_winning_heading_only(self):
        text = block(item="257", heading="2027-02-01 then 2028-03-02") + block(item="256b")
        self.assertEqual(json.loads(gc.render(text))["source_item_heading_date"], "2027-02-01")

    def test_all_old_blocks_are_validated(self):
        old = fields()
        old["wait"] = "chain_exited"
        text = block(old, item="256")
        self.refused(text + block(item="257"), "INVALID_WAIT", 9)

    def test_unknown_key(self):
        self.refused(block({**fields(), "surprise": "value"}), "UNKNOWN_KEY", 13)

    def test_duplicate_key(self):
        self.refused(block().replace("```\n", "owner: second\n```\n"), "DUPLICATE_KEY", 13)

    def test_empty_value_for_each_key(self):
        for index, key in enumerate(fields(), 4):
            for value in ("", " \t"):
                values = fields()
                values[key] = value
                with self.subTest(key=key, value=value):
                    self.refused(block(values), "EMPTY_VALUE", index)

    def test_invalid_entry_without_colon(self):
        self.refused(block().replace("owner: magistrate", "owner magistrate"), "INVALID_ENTRY", 4)

    def test_nonprintable_value(self):
        values = fields()
        values["owner"] = "lead\x00name"
        self.refused(block(values), "INVALID_VALUE", 4)

    def test_second_block_after_one_item(self):
        second = "```pointer\nowner: other\n```\n"
        self.refused(block() + "\nprose\n" + second, "SECOND_POINTER", 16)

    def test_nested_second_pointer_fence(self):
        self.refused(block().replace("owner: magistrate", "```pointer"), "SECOND_POINTER", 4)

    def test_unterminated_pointer(self):
        self.refused(block().removesuffix("```\n"), "UNTERMINATED_POINTER", 3)
        for closing in (" ```", "``` ", "````", "~~~"):
            self.refused(block().removesuffix("```\n") + closing + "\n",
                         "UNTERMINATED_POINTER", 3)

    def test_empty_body_and_blank_body_line(self):
        self.refused("262. **Empty**\n```pointer\n```\n", "MISSING_KEY", 2)
        self.refused(block().replace("owner: magistrate", ""), "INVALID_ENTRY", 4)

    def test_stripped_keys_values_and_first_colon_only(self):
        text = block().replace("owner: magistrate", " owner : magistrate \t")
        self.assertEqual(gc.render(text), gc.render(block()))

    def test_pointer_outside_item(self):
        self.refused("```pointer\nowner: lead\n```\n", "MISPLACED_POINTER", 1)

    def test_pointer_not_directly_under_heading(self):
        text = block(gap="\nSome prose\n")
        self.refused(text, "MISPLACED_POINTER", 4)
        for heading in ("0. **Zero**", "1. Plain list", " 1. **Indented**", "Text 1. **Mention**"):
            self.refused(heading + "\n```pointer\n```\n", "MISPLACED_POINTER", 2)

    def test_other_language_fences_ignore_pointer_and_fake_headings(self):
        for opener, closer in (("```python", "```"), ("````markdown", "`````"),
                               ("~~~text", "~~~~"), ("```", "```")):
            example = opener + "\n999. **Fake**\n```pointer\nunknown: ignored\n```\n" + closer + "\n"
            # Three-backtick outer fences close at the first matching triple;
            # the nested example therefore uses four backticks or tildes.
            if opener in ("```python", "```"):
                example = opener + "\n999. **Fake**\nowner: ignored\n" + closer + "\n"
            self.assertEqual(gc.render(example + block()), gc.render(block()))

    def test_quoted_and_indented_pointer_examples_are_ignored(self):
        text = block()
        for indent in ("> ", " ", "    ", "\t"):
            example = "\n".join(indent + line for line in text.splitlines()) + "\n"
            self.assertIsNone(json.loads(gc.render(example))["source_item"])
            self.assertEqual(gc.render(example + text), gc.render(text))
        # An indented opener directly below a real heading is still an example.
        self.assertIsNone(json.loads(gc.render("262. **Example**\n ```pointer\n owner: ignored\n ```\n"))["source_item"])

    def test_exact_pointer_opener_required(self):
        for opener in ("```pointer ", "```Pointer", "``` pointer", "````pointer"):
            self.assertIsNone(json.loads(gc.render("262. **Example**\n" + opener + "\nowner: ignored\n````\n"))["source_item"])

    def test_each_required_key(self):
        for key in ("owner", "wait", "next_observable", "deadline", "on_early_or_refused"):
            values = fields()
            del values[key]
            self.refused(block(values), "MISSING_KEY", 3)

    def test_all_or_none_arm_fields_each_partial_subset(self):
        arm = ("armed", "host", "t0", "latest_end")
        for count in (1, 2, 3):
            for subset in itertools.combinations(arm, count):
                values = {key: value for key, value in fields().items() if key not in arm or key in subset}
                self.refused(block(values), "PARTIAL_ARM", 3)
        values = {key: value for key, value in fields().items() if key not in arm}
        self.assertIsNone(json.loads(gc.render(block(values)))["armed"])

    def test_every_wait_observable_and_unknown_refusals(self):
        self.assertEqual(gc.OBSERVABLES, {"result_json_exists", "results_branch_exists",
                         "watchdog_status_state", "pr_merged", "ruling_recorded", "none"})
        for observable in gc.OBSERVABLES:
            values = fields()
            values["wait"] = observable
            self.assertEqual(json.loads(gc.render(block(values)))["wait"]["observable"], observable)
        for observable in ("chain_exited", "unknown", "GO", "None", "result_json_exist"):
            values = fields()
            values["wait"] = observable
            self.refused(block(values), "INVALID_WAIT", 9)

    def test_wait_none_optional_deadline_and_refusal_branch(self):
        pointer = json.loads(gc.render(block(unarmed())))
        self.assertIsNone(pointer["armed"])
        self.assertEqual(pointer["wait"], {"observable": "none", "deadline_epoch_s": None,
                                         "on_early_or_refused": None})
        gc.validate(pointer)
        values = {**unarmed(), "deadline": DEADLINE, "on_early_or_refused": "lead chooses"}
        pointer = json.loads(gc.render(block(values)))
        self.assertEqual(pointer["wait"]["deadline_epoch_s"], 1794454380)
        self.assertEqual(pointer["wait"]["on_early_or_refused"], "lead chooses")
        values = fields()
        values["wait"] = "none"
        del values["deadline"]
        self.refused(block(values), "MISSING_KEY", 3)

    def test_every_time_rejects_naive_epochs_bad_dates_and_bad_offsets(self):
        for key, line in (("t0", 7), ("latest_end", 8), ("deadline", 10)):
            # Source line numbers below account for t0 at line 7 and wait at 9.
            for value in ("2026-11-11", "2026-11-11T19:03:00", "1794454380", "1794454380000",
                          "2026-11-11 19:03:00-08:00", "2026-02-30T19:03:00-08:00",
                          "2026-11-11T24:00:00-08:00", "2026-11-11T19:03:00+24:00",
                          "2026-11-11T19:03:00+01:99", "2026-11-11T19:03:00+0800"):
                values = fields()
                values[key] = value
                self.refused(block(values), "INVALID_TIME", line)

    def test_each_time_refuses_outside_plausibility_bounds(self):
        for key, line in (("t0", 7), ("latest_end", 8), ("deadline", 10)):
            for value in ("2025-12-31T23:59:59Z", "2030-01-01T00:00:01Z",
                          "2026-01-01T00:00:00+00:01", "2030-01-01T00:00:00-00:01"):
                values = fields()
                values[key] = value
                self.refused(block(values), "IMPLAUSIBLE_TIME", line)

    def test_bounds_z_and_equivalent_offsets(self):
        values = fields()
        values.update(t0="2026-01-01T00:00:00Z", latest_end="2030-01-01T00:00:00Z",
                      deadline="2030-01-01T01:00:00+01:00")
        pointer = json.loads(gc.render(block(values)))
        self.assertEqual(pointer["armed"]["t0_epoch_s"], 1767225600)
        self.assertEqual(pointer["armed"]["latest_end_epoch_s"], 1893456000)
        self.assertEqual(pointer["wait"]["deadline_epoch_s"], 1893456000)
        values = fields()
        values["t0"] = "2026-11-11T04:53:00Z"
        self.assertEqual(gc.render(block(values)), gc.render(block()))
        values.update(t0="2026-11-11T04:53:00.5Z")
        self.assertEqual(json.loads(gc.render(block(values)))["armed"]["t0_epoch_s"], 1794372780.5)

    def test_strict_arm_order_and_inclusive_deadline(self):
        values = fields()
        values["latest_end"] = T0
        self.refused(block(values), "ARM_ORDER", 8)
        values["latest_end"] = "2026-11-10T20:52:59-08:00"
        self.refused(block(values), "ARM_ORDER", 8)
        values = fields()
        values["deadline"] = "2026-11-11T19:02:59-08:00"
        self.refused(block(values), "DEADLINE_ORDER", 10)
        values["deadline"] = END
        self.assertEqual(json.loads(gc.render(block(values)))["wait"]["deadline_epoch_s"], 1794452580)


class FileAndCliTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="gen-current-test-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / "RUN_STATE spaced.md"
        self.out = self.root / "CURRENT spaced.json"
        self.source.write_text(block(), encoding="utf-8")
        gc.generate(self.source, self.out)

    def call(self, *arguments):
        output, errors = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(errors):
            code = gc.main(["--run-state", str(self.source), "--out", str(self.out), *arguments])
        return code, output.getvalue(), errors.getvalue()

    def test_generate_and_check_are_read_only_on_source(self):
        before = self.source.read_bytes()
        self.assertEqual(self.out.read_bytes(), gc.render(block()))
        self.assertEqual(self.call("--check"), (0, "", ""))
        self.assertEqual(self.call(), (0, "", ""))
        self.assertEqual(self.source.read_bytes(), before)
        self.assertEqual(sorted(path.name for path in self.root.iterdir()), [self.out.name, self.source.name])

    def test_drift_is_one_read_only_with_regeneration_command(self):
        before = json.dumps(expected()).encode()
        self.out.write_bytes(before)
        code, output, errors = self.call("--check")
        self.assertEqual((code, output), (1, ""))
        self.assertIn("DRIFT:", errors)
        self.assertIn("python3 scripts/gen_state.py", errors)
        self.assertEqual(self.out.read_bytes(), before)
        self.assertEqual(self.call("--show")[0], 1)
        self.assertEqual(self.call()[0], 0)
        self.assertEqual(self.call("--check")[0], 0)

    def test_valid_but_stale_document_is_drift(self):
        self.out.write_bytes(gc.render(block(unarmed(), item="261")))
        self.assertEqual(self.call("--check")[0], 1)

    def test_invalid_source_leaves_output_unchanged(self):
        before = self.out.read_bytes()
        self.source.write_text("```pointer\n", encoding="utf-8")
        for flags in ((), ("--check",), ("--show",)):
            code, output, errors = self.call(*flags)
            self.assertEqual((code, output), (2, ""))
            self.assertIn("RUN_STATE line 1: MISPLACED_POINTER:", errors)
            self.assertEqual(self.out.read_bytes(), before)

    def test_missing_and_non_utf8_files(self):
        for path in (self.source, self.out):
            old = path.read_bytes()
            path.unlink()
            self.assertEqual(self.call("--check")[0], 2)
            path.write_bytes(b"\xff")
            self.assertEqual(self.call("--check")[0], 2)
            path.write_bytes(old)
        self.source.write_bytes(b"\xff")
        self.assertEqual(self.call()[0], 2)

    def test_invalid_json_duplicate_keys_and_nonfinite_numbers(self):
        for content in (b"{", b"null", b"[]", b"{}", b'NaN',
                        self.out.read_bytes().replace(b'"schema":', b'"schema": "duplicate", "schema":'),
                        self.out.read_bytes().replace(b"1794372780", b"NaN")):
            self.out.write_bytes(content)
            self.assertEqual(self.call("--check")[0], 2)
            gc.generate(self.source, self.out)

    def test_atomic_replace_and_cleanup_on_failure(self):
        before = self.out.read_bytes()
        with mock.patch.object(gc.os, "replace", side_effect=OSError("synthetic replace failure")) as replace:
            self.assertEqual(self.call()[0], 2)
        temporary, target = replace.call_args.args
        self.assertEqual(Path(temporary).parent, self.out.parent)
        self.assertEqual(Path(target), self.out)
        self.assertFalse(Path(temporary).exists())
        self.assertEqual(self.out.read_bytes(), before)

    def test_atomic_temp_creation_failure(self):
        self.out = self.root / "missing directory" / "CURRENT.json"
        self.assertEqual(self.call()[0], 2)

    def test_show_is_one_line_with_arm_wait_and_refusal(self):
        before = self.out.read_bytes()
        code, output, errors = self.call("--show")
        self.assertEqual((code, errors), (0, ""))
        self.assertEqual(len(output.splitlines()), 1)
        for fragment in ("item=262", "date=2026-11-11", "owner=magistrate", "synthetic-plan@synthetic-host",
                         "t0=1794372780", "end=1794452580", "result_json_exists deadline=1794454380",
                         "on_early_or_refused=read verdict first; ask lead", "next=synthetic result.json: verdict"):
            self.assertIn(fragment, output)
        self.assertEqual(self.out.read_bytes(), before)
        self.source.write_text(block(unarmed()), encoding="utf-8")
        gc.generate(self.source, self.out)
        self.assertIn("armed=none wait=none deadline=None", self.call("--show")[1])
        self.source.write_text("no pointer\n", encoding="utf-8")
        gc.generate(self.source, self.out)
        self.assertIn("item=None date=None owner=None armed=none wait=none next=None", self.call("--show")[1])

    def test_default_hooks_and_default_cli_paths(self):
        (self.root / "docs/process").mkdir(parents=True)
        default_source = self.root / "RUN_STATE.md"
        default_out = self.root / "docs/process/CURRENT.json"
        default_source.write_text(block(), encoding="utf-8")
        with mock.patch.object(gc, "ROOT", self.root):
            self.assertEqual(gc.generate_default(), 0)
            self.assertEqual(gc.check_default(), 0)
        self.assertEqual(default_out.read_bytes(), gc.render(block()))

    def test_real_repository_agrees(self):
        self.assertEqual(gc.check_default(), 0)


class SchemaTests(unittest.TestCase):
    def invalid(self, pointer, message):
        with self.assertRaisesRegex(ValueError, message):
            gc.validate(pointer)

    def test_top_keys_schema_item_and_date(self):
        for value in (None, [], "pointer", 1):
            self.invalid(value, "pointer must be an object")
        for key in expected():
            value = expected()
            del value[key]
            self.invalid(value, "pointer must be an object")
        self.invalid({**expected(), "extra": 1}, "pointer must be an object")
        for schema in (None, "joulewise.current_pointer.v2", 1):
            self.invalid({**expected(), "schema": schema}, "schema must be")
        for item in (0, True, "", "0", "262bb", "262B"):
            self.invalid({**expected(), "source_item": item}, "numbered item string")
        for date in (True, 20261111, "2026-1-1", "2026-11-11 extra"):
            self.invalid({**expected(), "source_item_heading_date": date}, "YYYY-MM-DD")
        self.invalid({**expected(), "source_item": None}, "all declaration fields null")

    def test_text_fields(self):
        for section, keys in ((None, ("owner", "next_observable")), ("armed", ("plan_id", "host")),
                              ("wait", ("on_early_or_refused",))):
            for key in keys:
                for text in (None, True, "", " ", "line\nline", "tab\t", "nul\x00"):
                    # null is allowed for a none wait only, tested separately.
                    pointer = expected()
                    (pointer if section is None else pointer[section])[key] = text
                    self.invalid(pointer, "single-line text|requires deadline and refusal")

    def test_nested_shapes_keys_and_wait_vocabulary(self):
        for section in ("armed", "wait"):
            for shape in (False, [], "value", 0):
                self.invalid({**expected(), section: shape}, section + " must be an object")
            for key in expected()[section]:
                pointer = expected()
                del pointer[section][key]
                self.invalid(pointer, section + " must be an object")
            pointer = expected()
            pointer[section]["extra"] = 1
            self.invalid(pointer, section + " must be an object")
        self.invalid({**expected(), "wait": None}, "wait must be an object")
        for observable in ([], None, "chain_exited", "GO"):
            pointer = expected()
            pointer["wait"]["observable"] = observable
            self.invalid(pointer, "closed vocabulary")
        for key in ("deadline_epoch_s", "on_early_or_refused"):
            pointer = expected()
            pointer["wait"][key] = None
            self.invalid(pointer, "requires deadline and refusal")

    def test_numeric_epochs_and_relations(self):
        for section, key in (("armed", "t0_epoch_s"), ("armed", "latest_end_epoch_s"),
                             ("wait", "deadline_epoch_s")):
            for value in (True, False, "1794372780", -1, 1767225599, 1893456001,
                          1794372780000, float("nan"), float("inf")):
                pointer = expected()
                pointer[section][key] = value
                self.invalid(pointer, "epoch seconds within")
        pointer = expected()
        pointer["armed"]["t0_epoch_s"] = pointer["armed"]["latest_end_epoch_s"]
        self.invalid(pointer, "t0 < latest_end")
        pointer = expected()
        pointer["wait"]["deadline_epoch_s"] = 1794452579
        self.invalid(pointer, "deadline >= latest_end")
        pointer["wait"]["observable"] = "none"
        pointer["wait"]["deadline_epoch_s"] = None
        self.invalid(pointer, "deadline >= latest_end")


if __name__ == "__main__":
    unittest.main()
