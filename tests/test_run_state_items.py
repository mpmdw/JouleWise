"""Typed item parser, transition and CLI acceptance tests."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

from scripts import gen_current, gen_state, run_state_items as items
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
ARCHIVE = "docs/archive/RUN_STATE-legacy-2026-11-17.md"
CUT_FROM = "d934178b9bd836162122db941c64d185593fa554"


def doc(typed=(), cutover=21):
    return EARLY + TOP_MARKER + "\n\n" + "".join(typed) + LEGACY_MARKER.format(cutover) + "\n\n" + LATE


def archived_doc(typed=(), cutover=405, legacy_max=404, legacy=""):
    marker = f"<!-- RUN_STATE LEGACY ITEMS: archived in {ARCHIVE}; cutover {cutover}; legacy_max {legacy_max} -->"
    return "# Synthetic RUN_STATE\n\n" + TOP_MARKER + "\n\n" + "".join(typed) + marker + "\n" + legacy


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


def cutover_source():
    return subprocess.check_output(["git", "show", f"{CUT_FROM}:RUN_STATE.md"], cwd=gen_current.ROOT)


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

    def test_archived_legacy_range_reserves_numbers_and_resolves_references(self):
        live_legacy = "\n346. **Retained fixture**\n"
        parsed = items.parse(archived_doc([item(405, supersedes=["346"])], legacy=live_legacy))
        self.assertEqual((parsed.cutover, parsed.legacy_max), (405, 404))
        self.assertEqual(items.validate(parsed), [])
        self.assertEqual(items.replay(parsed), {405: "ISSUED"})
        self.assertIn("DUPLICATE_NUMBER", codes(archived_doc([item(404)])))
        self.assertEqual(codes(archived_doc([item(405, supersedes=["346z", "404"])], legacy=live_legacy)),
                         ["DANGLING_REF", "DANGLING_REF"])
        self.assertEqual(codes(archived_doc([item(406, supersedes=["405"])])), ["DANGLING_REF"])
        self.assertEqual(codes(archived_doc([item(405, sets=[change(346, "VOID")])], legacy=live_legacy)),
                         ["LEGACY_TARGET"])
        self.assertIn("MARKER", codes(archived_doc(legacy_max=405)))

    def test_kind_is_optional_and_restricted_to_the_enum(self):
        for kind in ("event", "decision", "incident"):
            with self.subTest(kind=kind):
                self.assertEqual(codes(doc([item(22, kind=kind), item(21)])), [])
        for kind in (None, "note"):
            with self.subTest(kind=kind):
                self.assertEqual(codes(doc([item(21, kind=kind)])), ["SCHEMA"])

    def test_archive_round_trips_cutover_snapshot(self):
        root = gen_current.ROOT
        full_source = cutover_source()
        top = (TOP_MARKER + "\n").encode()
        old_marker = (LEGACY_MARKER.format(405) + "\n").encode()
        plan = items.legacy_archive_plan(full_source.decode())
        lines = full_source.splitlines(keepends=True)
        top_index = lines.index(top)
        marker = lines.index(old_marker)
        old_typed = b"".join(lines[top_index + 1:marker])
        projection_start = lines.index((gen_state.RS_BEGIN + "\n").encode())
        projection_end = lines.index((gen_state.RS_END + "\n").encode()) + 1
        moved_lines = set(range(1, plan.prefix_start))
        for start, end in (*plan.spans, (projection_start, projection_end)):
            moved_lines.update(range(start, end))
        expected_payload = (b"".join(lines[i] for i in range(1, top_index) if i in moved_lines) + old_marker
                            + b"".join(lines[i] for i in range(marker + 1, len(lines)) if i in moved_lines))

        archive = (root / ARCHIVE).read_bytes()
        archive_title, archive_source, archive_order, moved = archive.split(b"\n", 3)
        self.assertTrue(archive_title.startswith(b"# "))
        self.assertIn(CUT_FROM.encode(), archive_source)
        self.assertIn(b"pre-item introduction", archive_order)
        self.assertEqual(sha256(moved).digest(), sha256(expected_payload).digest())

        current = (root / "RUN_STATE.md").read_bytes()
        self.assertEqual(current.splitlines(keepends=True)[0], lines[0])
        current_header, current_top, current_regions = current.partition(top)
        new_marker = f"<!-- RUN_STATE LEGACY ITEMS: archived in {ARCHIVE}; cutover 405; legacy_max 404 -->\n".encode()
        typed, found, rest = current_regions.partition(new_marker)
        self.assertEqual(found, new_marker)
        restored_header, restored_marker, archive_tail = moved.partition(old_marker)
        _, projection_end_marker, retained_prefix = current_header.partition((gen_state.RS_END + "\n\n").encode())
        self.assertTrue(projection_end_marker)
        retained = iter((retained_prefix + rest).splitlines(keepends=True))
        archived = iter((restored_header + archive_tail).splitlines(keepends=True))

        def restore(start, stop):
            return b"".join(next(archived if i in moved_lines else retained) for i in range(start, stop))

        # Later log entries can be prepended ahead of the cutover snapshot.
        kept = typed[-len(old_typed):]
        restored = (lines[0] + restore(1, top_index) + current_top + kept + restored_marker
                    + restore(marker + 1, len(lines)))
        self.assertIsNone(next(archived, None))
        self.assertIsNone(next(retained, None))
        self.assertEqual(sha256(restored).digest(), sha256(full_source).digest())

    def test_every_item_reachable_from_the_newest_remains_in_run_state(self):
        original = cutover_source().decode()
        newest = str(max(entry.number for entry in items.parse(original).items))
        plan = items.legacy_archive_plan(original)
        reachable = items.reachable_items(plan.references, {newest})
        self.assertTrue(reachable - {str(entry.number) for entry in items.parse(original).items})
        current = (gen_current.ROOT / "RUN_STATE.md").read_text(encoding="utf-8")
        present = {f"{number}{suffix}" for _, number, suffix in items.heading_lines(current)}
        self.assertEqual(reachable - present, set())
        self.assertEqual(plan.live - present, set())

    def test_issued_item_reaches_pre_typed_record_in_the_live_log(self):
        source = cutover_source().decode()
        parsed = items.parse(source)
        plan = items.legacy_archive_plan(source)
        chain = ("418", "346", "325", "29")
        self.assertEqual(items.replay(parsed)[int(chain[0])], "ISSUED")
        for parent, child in zip(chain, chain[1:]):
            self.assertIn(child, plan.references[parent])
        source_lines = {str(number): line for line, number, suffix in items.heading_lines(source) if not suffix}
        self.assertLess(source_lines[chain[-1]], parsed.top_line)
        self.assertTrue(set(chain) <= items.reachable_items(plan.references, {chain[0]}))
        current = (gen_current.ROOT / "RUN_STATE.md").read_text(encoding="utf-8")
        self.assertEqual(sum(str(number) == chain[-1] for _, number, _ in items.heading_lines(current)), 1)
        archive = (gen_current.ROOT / ARCHIVE).read_text(encoding="utf-8")
        self.assertFalse(any(str(number) == chain[-1] for _, number, _ in items.heading_lines(archive)))

    def test_archive_plan_traverses_adjacent_legacy_headings_before_the_typed_marker(self):
        prefix = ("# Synthetic RUN_STATE\n\n"
                  "11. **Fixture legacy**\n"
                  "10. **Fixture legacy refers to item 19**\n"
                  "9. **Fixture unreferenced superseded legacy**\n\n")
        typed = item(24, body="See item 20.", supersedes=["10", "9"])
        legacy = "20. **Fixture legacy**\n\nSee item 10.\n\n19. **Fixture legacy refers to item 11**\n"
        source = prefix + TOP_MARKER + "\n\n" + typed + LEGACY_MARKER.format(21) + "\n\n" + legacy
        plan = items.legacy_archive_plan(source)
        self.assertEqual(plan.live, {"24", "20", "19", "11", "10"})
        span, = plan.spans
        self.assertEqual("".join(source.splitlines(keepends=True)[slice(*span)]),
                         "9. **Fixture unreferenced superseded legacy**\n\n")

    def test_archive_plan_keeps_live_and_unknown_legacy_and_moves_unreferenced_superseded(self):
        typed = [item(24, body="Run items 19, 18 and 17 as issued.", supersedes=["19", "16", "14"]),
                 render_item(23, "Fixture (standing), see item 15", header(23, status="CLOSED"), "", None)
                 + "\n\n"]
        legacy = ("19. **Fixture legacy**\n\nSee item 16.\n\n"
                  "18. **Fixture legacy**\n\n17. **Fixture legacy**\n\n"
                  "16. **Fixture legacy**\n\n15. **Fixture referenced by a standing order**\n\n"
                  "13. **Fixture unknown status**\n\n"
                  "14. **Fixture superseded**\n\n")
        state = EARLY + TOP_MARKER + "\n\n" + "".join(typed) + LEGACY_MARKER.format(21) + "\n\n" + legacy
        plan = items.legacy_archive_plan(state)
        self.assertTrue({"24", "23", "19", "18", "17", "16", "15"} <= plan.live)
        self.assertEqual(len(plan.spans), 1)
        start, end = plan.spans[0]
        self.assertEqual("".join(state.splitlines(keepends=True)[start:end]), "14. **Fixture superseded**\n\n")

    def test_run_state_intro_paths_exist_in_tree(self):
        root = gen_current.ROOT
        intro = (root / "RUN_STATE.md").read_text(encoding="utf-8").split(gen_state.RS_BEGIN, 1)[0]
        paths = re.findall(r"(?<![\w.-])(?:[\w.-]+/)*[\w-]+(?:\.[\w-]+)+(?![\w.-])", intro)
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(path=path):
                self.assertTrue((root / path).is_file())
                self.assertEqual(subprocess.run(["git", "ls-files", "--error-unmatch", "--", path],
                                                cwd=root, capture_output=True).returncode, 0)

    def test_check_refuses_typed_item_hidden_by_its_own_closing_fence(self):
        hidden = doc([item(405, status="CLOSED", body="```\nunterminated"), item(404)], cutover=404)
        expected_line = hidden.splitlines().index("404. **Item 404**") + 1
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "RUN_STATE.md"
            path.write_text(hidden, encoding="utf-8")
            errors = StringIO()
            with redirect_stderr(errors):
                self.assertEqual(items.main(["check", "--run-state", str(path)]), 2)
            self.assertIn(f"RUN_STATE line {expected_line}: HIDDEN_ITEM:", errors.getvalue())
        with self.assertRaisesRegex(gen_current.PointerError, "HIDDEN_ITEM"):
            gen_current.render(hidden)
        unclosed = hidden.replace("```\nunterminated", "~~~\nunterminated")
        self.assertIn("UNCLOSED_FENCE", codes(unclosed))

        for opener, closer in (("````markdown", "````"), ("~~~markdown", "~~~")):
            with self.subTest(opener=opener):
                example = f"{opener}\n{item(404)}{closer}"
                valid = doc([item(405, status="CLOSED", body=example), item(404)], cutover=404)
                parsed = items.parse(valid)
                self.assertEqual(items.validate(parsed), [])
                self.assertEqual([entry.number for entry in parsed.items], [405, 404])

    def test_r26_schema_matches_runtime_enums_and_epoch_bounds(self):
        schema = json.loads((gen_current.ROOT / "docs/process/run_state_item.schema.json").read_text())
        properties = schema["properties"]
        self.assertEqual(tuple(properties["owner"]["enum"]), items.OWNERS)
        self.assertEqual(tuple(properties["status"]["enum"]), items.INITIAL)
        self.assertEqual(tuple(properties["kind"]["enum"]), items.KINDS)
        self.assertNotIn("kind", schema["required"])
        self.assertEqual(tuple(properties["sets"]["items"]["properties"]["status"]["enum"]), items.SETTABLE)
        epoch = schema["$defs"]["epoch"]
        self.assertEqual((epoch["minimum"], epoch["maximum"]), (gen_current.MIN_EPOCH, gen_current.MAX_EPOCH))


if __name__ == "__main__":
    unittest.main()
