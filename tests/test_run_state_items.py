"""Typed item parser, transition and CLI acceptance tests."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts import gen_current, run_state_items as items
from scripts.run_state_add import LEGACY_MARKER, TOP_MARKER, render_item


ISSUED = 1795000000
EXPIRY = ISSUED + 100
LEGACY = """# Synthetic RUN_STATE

9. **Old nine**
10. **Old ten**
11. **Old eleven**
12. **Old twelve**

20. **Legacy twenty**

19. **Legacy nineteen**

1. **Desks**
2. **Notes**

18. **Legacy eighteen**
"""
EARLY, LATE = LEGACY.split("20. **", 1)
LATE = "20. **" + LATE
POINTER = "owner: lead\nwait: none\nnext_observable: fixture observable"


def doc(typed=(), cutover=21):
    return EARLY + TOP_MARKER + "\n\n" + "".join(typed) + LEGACY_MARKER.format(cutover) + "\n\n" + LATE


def header(number, **changes):
    return {"schema": items.SCHEMA, "number": number, "owner": "lead", "status": "ISSUED",
            "issued_epoch_s": ISSUED, "expires_epoch_s": None, "sets": [], "supersedes": [],
            **changes}


def item(number, *, body="", pointer=None, **changes):
    return render_item(number, f"Item {number}", header(number, **changes), body, pointer) + "\n\n"


def change(target, status, at=ISSUED):
    return {"item": target, "status": status, "at_epoch_s": at}


def codes(text):
    return [error.code for error in items.validate(items.parse(text))]


class RunStateItemsTests(unittest.TestCase):
    def test_r01_legacy_accepts_prose(self):
        parsed = items.parse(LEGACY)
        self.assertIsNone(parsed.cutover)
        self.assertEqual(items.validate(parsed), [])

    def test_r02_item_block_without_markers(self):
        self.assertEqual(codes(LEGACY + item(21)), ["ITEM_BEFORE_CUTOVER"])
        self.assertEqual(codes(LEGACY + "````markdown\n" + item(999) + "````\n"), [])

    def test_r03_valid_reversed_items(self):
        parsed = items.parse(doc([item(23), item(22, status="CLOSED"), item(21, status="DRAFT")]))
        self.assertEqual([entry.number for entry in parsed.items], [23, 22, 21])
        self.assertEqual(items.validate(parsed), [])
        self.assertEqual(items.replay(parsed), {21: "DRAFT", 22: "CLOSED", 23: "ISSUED"})

    def test_r04_duplicate_names_both_lines(self):
        parsed = items.parse(doc([item(22), item(22)]))
        first, second = (entry.line for entry in parsed.items)
        error, = items.validate(parsed)
        self.assertEqual(error.code, "DUPLICATE_NUMBER")
        self.assertIn(f"lines {first} and {second}", error.detail)
        self.assertIn("DUPLICATE_NUMBER", codes(doc([item(20)])))

    def test_r05_header_number_disagrees_with_heading(self):
        self.assertEqual(codes(doc([item(22).replace("22. **", "23. **")])), ["NUMBER_MISMATCH"])

    def test_r06_typed_items_must_descend(self):
        self.assertEqual(codes(doc([item(21), item(22)])), ["ORDER"])

    def test_r07_first_item_immediately_follows_marker(self):
        self.assertEqual(codes(doc(["prose\n", item(21)])), ["ORDER"])

    def test_r08_high_number_headings_need_blocks(self):
        self.assertEqual(codes(doc([item(23), "24. **x**\n"])), ["UNTYPED_ITEM"])

    def test_r09_low_number_body_headings_and_fences(self):
        body = "1. **Desks**\n2. **Notes**\n\n````markdown\n999. **Example**\n```item\n````"
        self.assertEqual(codes(doc([item(21, body=body)])), [])

    def test_r10_pointer_before_item_keeps_selection(self):
        typed = doc([item(22), item(21, pointer=POINTER)])
        self.assertEqual(codes(typed), [])
        legacy = LEGACY + f"\n21. **Item 21**\n\n```pointer\n{POINTER}\n```\n"
        actual = json.loads(gen_current.render(typed))
        self.assertEqual(actual.pop("open_items"), items.open_items(items.parse(typed)))
        self.assertEqual({**actual, "open_items": []}, json.loads(gen_current.render(legacy)))

    def test_r11_invalid_placement_and_second_block(self):
        valid = item(21)
        for broken, code in (
            (valid.replace("```item", "prose\n```item"), "MISPLACED_ITEM_BLOCK"),
            (valid.removesuffix("```\n\n"), "MISPLACED_ITEM_BLOCK"),
            (valid + valid.split("\n\n", 1)[1], "SECOND_ITEM_BLOCK"),
        ):
            with self.subTest(code=code, broken=broken):
                self.assertIn(code, codes(doc([broken])))

    def test_r12_json_and_canonical_format(self):
        original = item(21)
        for raw, code in (
            ("{", "BAD_JSON"),
            ('{"number": 21, "number": 21}', "BAD_JSON"),
            ('{"number": NaN}', "BAD_JSON"),
            ('{"number": Infinity}', "BAD_JSON"),
            ('{"number": 1e999}', "BAD_JSON"),
            (json.dumps(header(21), sort_keys=True, separators=(",", ":")), "NONCANONICAL"),
            (json.dumps(header(21)), "NONCANONICAL"),
        ):
            with self.subTest(raw=raw):
                self.assertIn(code, codes(doc([original.replace(items.canonical(header(21)), raw)])))

    def test_r13_exact_keys_and_closed_enums(self):
        valid = header(21)
        variations = [{k: v for k, v in valid.items() if k != removed} for removed in valid]
        variations += [{**valid, **bad} for bad in (
            {"unknown": False}, {"status": "ARMED"}, {"owner": "builder"},
            {"sets": [change(19, "SUPERSEDED")]},
            {"sets": [{**change(19, "VOID"), "extra": 1}]},
            {"supersedes": ["19", "19"]},
        )]
        for variation in variations:
            with self.subTest(header=variation):
                self.assertEqual(codes(doc([render_item(21, "Item", variation, "", None) + "\n"])), ["SCHEMA"])

    def test_r14_epoch_type_and_bounds(self):
        for value in (float(ISSUED), True, gen_current.MIN_EPOCH - 1, 1924992000):
            for fields in ({"issued_epoch_s": value}, {"expires_epoch_s": value},
                           {"sets": [change(19, "ISSUED", value)]}):
                with self.subTest(fields=fields):
                    self.assertEqual(codes(doc([item(21, **fields)])), ["BAD_TIME"])

    def test_r15_expiry_order_and_closed_expiry(self):
        for expiry in (ISSUED, ISSUED - 1):
            self.assertEqual(codes(doc([item(21, expires_epoch_s=expiry)])), ["EXPIRY_ORDER"])
        self.assertEqual(codes(doc([item(21, status="CLOSED", expires_epoch_s=EXPIRY)])), ["SCHEMA"])

    def test_r16_letter_suffix(self):
        self.assertEqual(codes(doc([item(23).replace("23.", "23b.")])), ["LETTER_SUFFIX"])

    def test_r17_markers(self):
        valid = doc()
        legacy = LEGACY_MARKER.format(21)
        for broken in (valid.replace(TOP_MARKER, ""), valid.replace(legacy, ""),
                       valid.replace(TOP_MARKER, TOP_MARKER + "\n" + TOP_MARKER),
                       valid.replace(legacy, legacy + "\n" + legacy),
                       EARLY + legacy + "\n" + TOP_MARKER + "\n" + LATE,
                       doc(cutover="x"), doc(cutover=20)):
            with self.subTest(text=broken):
                self.assertIn("MARKER", codes(broken))

    def test_r18_exhaustive_transition_matrix(self):
        def transition(number, to):
            fields = ({"supersedes": ["21"]} if to == "SUPERSEDED"
                      else {"sets": [change(21, to, EXPIRY)]})
            return item(number, status="CLOSED", issued_epoch_s=EXPIRY, **fields)

        for start, legal in items.LEGAL.items():
            initial = start if start in items.INITIAL else "ISSUED"
            # The transition matrix tests legality at the expiry boundary.
            # A fixture that reaches ARMED must do so before that boundary.
            history = [item(21, status=initial, expires_epoch_s=None if initial == "CLOSED" else EXPIRY)]
            if start == "ARMED":
                history.insert(0, item(22, status="CLOSED", sets=[change(21, "ARMED")]))
            elif start != initial:
                history.insert(0, transition(22, start))
            for target in items.LEGAL:
                with self.subTest(start=start, target=target):
                    attempt = transition(23, target)
                    if target == "DRAFT":
                        # DRAFT is impossible to encode as an action. Exercise
                        # the replay guard directly, using a parsed typed item.
                        parsed = items.parse(doc([attempt, *history]))
                        errors = []
                        items._replay(parsed, list(parsed.items), errors)
                        self.assertEqual([e.code for e in errors], ["ILLEGAL_TRANSITION"])
                        self.assertEqual(items.validate(parsed)[0].code, "SCHEMA")
                    elif start == "ISSUED" and target == "ARMED":
                        self.assertEqual(codes(doc([item(23, sets=[change(21, target)]), *history])), [])
                    else:
                        self.assertEqual(codes(doc([attempt, *history])), [] if target in legal else ["ILLEGAL_TRANSITION"])

    def test_r19_supersedes_typed_legacy_missing_and_terminal(self):
        for target, expected in (("21", []), ("19", []), ("999", ["DANGLING_REF"])):
            parsed = items.parse(doc([item(23, supersedes=[target]), item(21)]))
            self.assertEqual([e.code for e in items.validate(parsed)], expected)
            if not expected:
                recorded = items.replay(parsed)
                self.assertEqual(recorded[21], "SUPERSEDED" if target == "21" else "ISSUED")
                self.assertNotIn(19, recorded)
        self.assertEqual(codes(doc([item(23, supersedes=["21"]), item(22, sets=[change(21, "VOID")]),
                                    item(21)])), ["ILLEGAL_TRANSITION"])

    def test_r20_set_targets(self):
        for target, code in ((19, "LEGACY_TARGET"), (22, "FORWARD_REF"), (23, "FORWARD_REF"),
                             (999, "DANGLING_REF")):
            with self.subTest(target=target):
                self.assertEqual(codes(doc([item(23), item(22, sets=[change(target, "VOID")]),
                                            item(21)])), [code])

    def test_r21_arm_expiry_boundary(self):
        for at, expected in ((EXPIRY - 1, []), (EXPIRY, ["ARM_AFTER_EXPIRY"])):
            self.assertEqual(codes(doc([item(22, issued_epoch_s=EXPIRY, sets=[change(21, "ARMED", at)]),
                                        item(21, expires_epoch_s=EXPIRY)])), expected)

    def test_r22_expire_needs_reached_expiry(self):
        for expiry in (None, EXPIRY):
            self.assertEqual(codes(doc([item(22, issued_epoch_s=EXPIRY, sets=[change(21, "EXPIRED", EXPIRY - 1)]),
                                        item(21, expires_epoch_s=expiry)])), ["EARLY_EXPIRY"])

    def test_r23_change_time_bounds(self):
        for issued, at, prior in ((EXPIRY, ISSUED - 1, []), (EXPIRY, ISSUED, [change(21, "ARMED", ISSUED + 1)]),
                                  (ISSUED, EXPIRY, [])):
            transition = "CLOSED" if prior else "ARMED"
            self.assertEqual(codes(doc([item(22, issued_epoch_s=issued, sets=[*prior, change(21, transition, at)]),
                                        item(21)])), ["TIME_ORDER"])
        self.assertEqual(codes(doc([item(22, issued_epoch_s=ISSUED - 1, supersedes=["21"]), item(21)])), ["TIME_ORDER"])

    def test_r24_derivation_and_cli(self):
        text = doc([item(26, status="CLOSED", sets=[change(22, "ARMED")], supersedes=["21"]),
                    item(24, expires_epoch_s=EXPIRY), item(23, status="DRAFT", expires_epoch_s=EXPIRY),
                    item(22, expires_epoch_s=EXPIRY), item(21)])
        parsed = items.parse(text)
        self.assertEqual(items.derive(parsed, EXPIRY - 1), items.replay(parsed))
        self.assertEqual(items.derive(parsed, EXPIRY), {21: "SUPERSEDED", 22: "ARMED", 23: "EXPIRED",
                                                       24: "EXPIRED", 26: "CLOSED"})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "RUN_STATE.md"
            path.write_text(text, encoding="utf-8")

            def cli(command, *args):
                return items.main([command, "--run-state", str(path), *args])

            output, errors = StringIO(), StringIO()
            with redirect_stdout(output), redirect_stderr(errors):
                self.assertEqual(cli("check"), 0)
                self.assertEqual(cli("status", "--as-of-epoch", str(EXPIRY)), 0)
                path.write_text(doc([item(22), item(22)]), encoding="utf-8")
                self.assertEqual(cli("check"), 2)
            self.assertEqual(output.getvalue().splitlines(), [
                "26 CLOSED owner=lead expires=none", f"24 EXPIRED owner=lead expires={EXPIRY}",
                f"23 EXPIRED owner=lead expires={EXPIRY}", f"22 ARMED owner=lead expires={EXPIRY}",
                "21 SUPERSEDED owner=lead expires=none superseded_by=26",
            ])
            self.assertRegex(errors.getvalue(), r"^RUN_STATE line \d+: DUPLICATE_NUMBER: .+")

    def test_r25_live_repository(self):
        self.assertEqual(items.main(["check"]), 0)

    def test_r26_schema_matches_runtime_enums_and_epoch_bounds(self):
        schema = json.loads((gen_current.ROOT / "docs/process/run_state_item.schema.json").read_text())
        properties = schema["properties"]
        self.assertEqual(tuple(properties["owner"]["enum"]), items.OWNERS)
        self.assertEqual(tuple(properties["status"]["enum"]), items.INITIAL)
        self.assertEqual(tuple(properties["sets"]["items"]["properties"]["status"]["enum"]), items.SETTABLE)
        epoch = schema["$defs"]["epoch"]
        self.assertEqual((epoch["minimum"], epoch["maximum"]), (gen_current.MIN_EPOCH, gen_current.MAX_EPOCH))


if __name__ == "__main__":
    unittest.main()
