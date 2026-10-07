"""No refusal lands on the HAZARD_PACK path without a reviewed allowlist entry.

Ed, 2026-10-05: physics refuses; everything else is a flag.  On 2026-10-06 a
fix round's "fail closed" lineage check refused every window over an
uppercase boot UUID; the gate prune had removed such refusals a day earlier.
This test makes that kind of change visible: ``tests/hazards/refusal_census.py``
finds every raise, nonzero exit, refusal call, refusal reason, signal and
shell stop in the HAZARD-path modules, and each one must be listed, with its
exact count, in ``configs/gates/hazard_refusals.json``.  A new entry must say
which physical quantity it measures (PHYSICS), which number it protects
(NUMBER_INTEGRITY), or why it never stops collection (INTERNAL).  The same
holds for every flag code whose catalog effect is EXCLUDE_WINDOW.

When this test fails on your change, run::

    /opt/homebrew/bin/python3.13 -m tests.hazards.refusal_census

and add or correct the entries it prints.  Do not mark a new site BASELINE:
the BASELINE totals below are frozen and may only go down.
"""
from __future__ import annotations

import copy
import json
import textwrap
import unittest
from collections import Counter
from pathlib import Path

from tests.hazards import refusal_census as census

ROOT = census.ROOT
FIXTURE_CATALOG = ROOT / "tests" / "fixtures" / "b5_harvest" / "flag_catalog.json"
SEALED_CATALOG = ROOT / "configs" / "campaigns" / "v5_claim_25g83" / "flag_catalog.json"

# Frozen at the 2026-10-06 refusal census (sites present at e6b6a0ce and
# unchanged at ba0e0c72e).  Lower these when a BASELINE site is removed or
# reviewed into another category; never raise them.
BASELINE_ENTRIES = 2517
BASELINE_SITES = 3543
REVIEWED = ("PHYSICS", "NUMBER_INTEGRITY", "INTERNAL")
MIN_PROTECTS = 30


def entry_problems(document: dict) -> list[str]:
    """Every entry that does not say what it protects, or is malformed."""

    problems = []
    modules = set(document["scan"]["modules"])
    seen = set()
    for entry in document["sites"]:
        key = (entry.get("file"), entry.get("function"), entry.get("kind"), entry.get("detail"))
        label = ":".join(str(part) for part in key)
        if key in seen:
            problems.append(f"duplicate entry {label}")
        seen.add(key)
        if entry.get("file") not in modules:
            problems.append(f"{label}: file is not a scanned module")
        if entry.get("kind") not in census.KINDS:
            problems.append(f"{label}: unknown kind")
        if not isinstance(entry.get("count"), int) or entry["count"] < 1:
            problems.append(f"{label}: count must be a positive integer")
        category = entry.get("category")
        if category not in census.CATEGORIES:
            problems.append(f"{label}: category {category!r} is not one of {census.CATEGORIES}")
            continue
        if category == "BASELINE":
            continue
        protects = entry.get("protects")
        if not isinstance(protects, str) or len(protects.strip()) < MIN_PROTECTS:
            problems.append(f"{label}: {category} entry must name its physical quantity, the number it "
                            f"protects, or its catcher in 'protects' (at least {MIN_PROTECTS} characters)")
        if category == "DEFERRED_REPRESENTATION" and not str(entry.get("owner") or "").strip():
            problems.append(f"{label}: DEFERRED_REPRESENTATION needs the 'owner' lane converting it")
    return problems


def baseline_problems(document: dict) -> list[str]:
    rows = [entry for entry in document["sites"] if entry.get("category") == "BASELINE"]
    entries, sites = len(rows), sum(entry.get("count", 0) for entry in rows)
    problems = []
    if (entries, sites) != (BASELINE_ENTRIES, BASELINE_SITES):
        problems.append(
            f"BASELINE is frozen at {BASELINE_ENTRIES} entries / {BASELINE_SITES} sites; found "
            f"{entries} / {sites}.  A new site is never BASELINE: give it PHYSICS, NUMBER_INTEGRITY or "
            f"INTERNAL.  If you removed or reviewed a BASELINE site, lower the constants in this file.")
    recorded = document.get("baseline") or {}
    if (recorded.get("entries"), recorded.get("sites")) != (entries, sites):
        problems.append("the allowlist's own 'baseline' totals do not match its BASELINE entries")
    return problems


def scope_problems(document: dict, root: Path = ROOT) -> list[str]:
    scan = document["scan"]
    problems = list(census.iter_scope_gaps(document, root))
    reasons = scan["not_scanned_reasons"]
    for module, reason in scan["not_scanned"].items():
        if reason not in reasons:
            problems.append(f"not_scanned {module}: reason {reason!r} is not in not_scanned_reasons")
        if module in scan["modules"]:
            problems.append(f"{module} is both scanned and not_scanned")
        if not (root / module).is_file():
            problems.append(f"not_scanned {module} does not exist")
    for module in scan["modules"]:
        if not (root / module).is_file():
            problems.append(f"scanned module {module} does not exist")
    return problems


def window_exclusion_codes(catalogs: list[dict]) -> set[str]:
    codes = set()
    for catalog in catalogs:
        for code, spec in catalog.items():
            effect = spec.get("effect") if isinstance(spec, dict) else getattr(spec, "effect", None)
            if effect == "EXCLUDE_WINDOW":
                codes.add(code)
    return codes


def current_catalogs() -> list[dict]:
    from joulewise.flags.catalog import DRAFT_CODES

    catalogs = [dict(DRAFT_CODES), json.loads(FIXTURE_CATALOG.read_bytes())["codes"]]
    if SEALED_CATALOG.is_file():
        catalogs.append(json.loads(SEALED_CATALOG.read_bytes())["codes"])
    return catalogs


def window_exclusion_problems(document: dict, catalogs: list[dict]) -> list[str]:
    listed = document["window_exclusions"]
    codes = window_exclusion_codes(catalogs)
    problems = [f"EXCLUDE_WINDOW code {code} is not in window_exclusions: name the physical quantity or "
                f"the number it protects, or make it DISCLOSE" for code in sorted(codes - set(listed))]
    problems += [f"window_exclusions lists {code}, which no catalog makes EXCLUDE_WINDOW"
                 for code in sorted(set(listed) - codes)]
    for code, entry in listed.items():
        category = entry.get("category")
        if category not in ("PHYSICS", "NUMBER_INTEGRITY", "BASELINE"):
            problems.append(f"window_exclusions {code}: category {category!r}")
        elif category != "BASELINE" and len(str(entry.get("protects") or "").strip()) < MIN_PROTECTS:
            problems.append(f"window_exclusions {code}: name what it protects")
    return problems


class RefusalAllowlistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = census.load_allowlist()

    def test_every_refusal_site_is_listed_with_its_exact_count(self):
        result = census.differences(self.document)
        self.assertEqual(result, {"unlisted": [], "stale": [], "miscounted": []},
                         "refusal sites on the HAZARD path differ from configs/gates/hazard_refusals.json; "
                         "run python -m tests.hazards.refusal_census\n" + json.dumps(result, indent=1)[:6000])

    def test_every_entry_names_what_it_protects(self):
        self.assertEqual(entry_problems(self.document), [])

    def test_the_baseline_is_frozen(self):
        self.assertEqual(baseline_problems(self.document), [])

    def test_the_scan_covers_every_module_the_hazard_path_imports(self):
        self.assertEqual(scope_problems(self.document), [])

    def test_every_window_exclusion_names_what_it_protects(self):
        self.assertEqual(window_exclusion_problems(self.document, current_catalogs()), [])

    # ---------------------------------------------------------- the guard fails

    def test_a_new_entry_marked_baseline_fails(self):
        broken = copy.deepcopy(self.document)
        broken["sites"].append({"file": "joulewise/b5/driver.py", "function": "f", "kind": "raise",
                                "detail": "ValueError", "count": 1, "category": "BASELINE"})
        self.assertTrue(baseline_problems(broken))

    def test_an_entry_without_a_quantity_fails(self):
        broken = copy.deepcopy(self.document)
        entry = next(row for row in broken["sites"] if row["category"] == "PHYSICS")
        entry["protects"] = "fail closed"
        self.assertTrue(any("must name" in problem for problem in entry_problems(broken)))
        entry["category"] = "REPRESENTATION"
        self.assertTrue(any("category" in problem for problem in entry_problems(broken)))

    def test_a_deferred_representation_without_an_owner_fails(self):
        broken = copy.deepcopy(self.document)
        entry = next(row for row in broken["sites"] if row["category"] == "DEFERRED_REPRESENTATION")
        entry.pop("owner")
        self.assertTrue(any("owner" in problem for problem in entry_problems(broken)))

    def test_an_unclassified_window_exclusion_fails(self):
        catalogs = current_catalogs() + [{"records.new_fail_closed": {"effect": "EXCLUDE_WINDOW"}}]
        problems = window_exclusion_problems(self.document, catalogs)
        self.assertTrue(any("records.new_fail_closed" in problem for problem in problems), problems)

    def test_an_unscanned_import_fails(self):
        broken = copy.deepcopy(self.document)
        broken["scan"]["not_scanned"].pop("joulewise/t0_rehearsal.py")
        self.assertTrue(any("joulewise/t0_rehearsal.py" in problem for problem in scope_problems(broken)))


class CensusScannerTests(unittest.TestCase):
    """The scanner itself: each refusal shape is found, and keys ignore line moves."""

    def keys(self, source: str) -> Counter:
        return census.site_counts(census.scan_source("m.py", textwrap.dedent(source)))

    def test_the_2026_10_06_lineage_refusal_shape_is_found(self):
        # P2-DRV review F2: a raise inside a try whose except refuses the window.
        before = self.keys("""
            def _production_lineage_check(request):
                try:
                    context = authenticate(request)
                    entry = {"valid": True}
                except Exception as error:
                    entry = {"valid": False, "error": str(error)}
                return entry
        """)
        after = self.keys("""
            def _production_lineage_check(request):
                try:
                    context = authenticate(request)
                    if context["plan_id"] != request.plan_id:
                        raise ValueError(f"the locator names plan {context['plan_id']!r}")
                    entry = {"valid": True}
                except Exception as error:
                    entry = {"valid": False, "error": str(error)}
                return entry
        """)
        self.assertEqual(after - before,
                         Counter({("m.py", "_production_lineage_check", "raise", "ValueError|the locator names"): 1}))

    def test_every_kind_is_found(self):
        found = self.keys('''
            import os, sys
            HELPER_X_HELPER = "import sys\\nsys.exit(3)\\n"
            SHELL = "f() {\\n  (( $? == 0 )) || stop_chain reservation_failed 10\\n  return 1\\n}"
            class C:
                def m(self, process):
                    raise LaunchLineageError("launch_binding_mismatch", "x")
                def n(self):
                    process.kill()
                    os.killpg(1, signal.SIGTERM)
            def main():
                reasons = []
                reasons.append("quiet_state_violated")
                if bad:
                    return EXIT_REFUSED
                if worse:
                    return 2
                if blocked:
                    return "blocked", reasons
                refuse("lineage", CODE, "detail", None)
                finish(NULL, "identity", ["x"])
                Verdict(MODULE, UNMEASURED, ("x",), {})
                Decision("HOLD_UNSAFE", "x")
                sys.exit(4)
                raise
            sys.exit(main())
        ''')
        kinds = Counter(key[2] for key in found.elements())
        for kind in census.KINDS:
            self.assertIn(kind, kinds, kind)
        self.assertIn(("m.py", "C.m", "raise", "LaunchLineageError|launch_binding_mismatch"), found)
        self.assertIn(("m.py", "main", "refusal_call", "finish|NULL|identity"), found)
        self.assertIn(("m.py", "main", "refusal_call", "Decision|HOLD_UNSAFE"), found)
        self.assertIn(("m.py", "main", "reason", "quiet_state_violated"), found)
        self.assertIn(("m.py", "main", "status", "blocked"), found)
        self.assertIn(("m.py", "<HELPER_X_HELPER>", "exit", "3"), found)
        self.assertIn(("m.py", "<module>", "shell", "stop_chain reservation_failed"), found)
        self.assertIn(("m.py", "<module>", "shell", "return 1"), found)
        self.assertNotIn(("m.py", "main", "return_code", "0"), found)

    def test_moving_code_does_not_change_a_key_and_a_success_return_is_not_a_site(self):
        one = self.keys("""
            def f():
                if x:
                    raise ValueError("pack root is not here")
                return 0
        """)
        two = self.keys("""


            def f():
                y = 1
                if x and y:
                    raise ValueError("pack root is not here: " + str(y))
                sys.exit(0)
                return EXIT_GO
        """)
        self.assertEqual(one, two)

    def test_differences_reports_unlisted_stale_and_miscounted(self):
        document = {"scan": {"modules": ["joulewise/b5/driver.py"]}, "sites": []}
        result = census.differences(document)
        self.assertTrue(result["unlisted"])
        first = result["unlisted"][0]
        document["sites"] = [{**{key: first[key] for key in ("file", "function", "kind", "detail")},
                              "count": first["count"] + 1},
                             {"file": "joulewise/b5/driver.py", "function": "gone", "kind": "raise",
                              "detail": "ValueError", "count": 1}]
        result = census.differences(document)
        self.assertEqual([row["function"] for row in result["stale"]], ["gone"])
        self.assertEqual(result["miscounted"][0]["listed"], first["count"] + 1)


if __name__ == "__main__":
    unittest.main()
