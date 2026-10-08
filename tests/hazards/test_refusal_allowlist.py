"""No refusal lands on the HAZARD_PACK path without a reviewed allowlist entry.

Ed, 2026-10-05: physics refuses; everything else is a flag.  On 2026-10-06 a
fix round's "fail closed" lineage check refused every window over an
uppercase boot UUID; the gate prune had removed such refusals a day earlier.
This test makes that kind of change visible: ``tests/hazards/refusal_census.py``
finds every raise, nonzero exit, refusal call, refusal reason, signal and
shell stop in the HAZARD-path modules, and each one must be listed, with its
exact count, in ``configs/gates/hazard_refusals.json``.  A new entry must say
which physical quantity it measures (PHYSICS), which number it protects
(NUMBER_INTEGRITY), or why it never stops collection (INTERNAL).  Each entry
also carries a digest of the conditions leading to its sites, so widening an
existing refusal (``or x != y``) fails too.  The same holds for every flag
code whose catalog effect is EXCLUDE_WINDOW or EXCLUDE_MEMBER.

When this test fails on your change, run::

    /opt/homebrew/bin/python3.13 -m tests.hazards.refusal_census

and add or correct the entries it prints.  Do not mark a new or changed site
BASELINE: every BASELINE entry must match a line of
``tests/hazards/refusal_baseline_frozen.txt``, whose digest is pinned below.

What the guard cannot see (Sol 6.1 review, 2026-10-06, F2/F3): a refusal
expressed through a shape outside the census vocabulary (``return False`` from
an admission predicate, a ``continue`` that skips a member) and a new caller of
an existing raising helper.  The reviewer rule in every brief
(night-archive/gate-prune/REVIEW_BRIEF_RULE.md) covers those.
"""
from __future__ import annotations

import copy
import hashlib
import json
import textwrap
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

from tests.hazards import refusal_census as census

ROOT = census.ROOT
FIXTURE_CATALOG = ROOT / "tests" / "fixtures" / "b5_harvest" / "flag_catalog.json"
SEALED_CATALOG = ROOT / "configs" / "campaigns" / "v5_claim_25g83" / "flag_catalog.json"
DESIGN_BRANCH = "design/2026-10-05-v5-claim-block-draft"

FROZEN_BASELINE = Path(__file__).with_name("refusal_baseline_frozen.txt")
# The frozen BASELINE list (sites present at e6b6a0ce and unchanged at
# ba0e0c72e, with their guards).  Never add a line to it; this digest makes an
# edit to it a visible change of this file too.
FROZEN_BASELINE_SHA256 = "fba2978ac812883f0bad1094dce938ea410448188097c3a0ccf57c7a354a10f5"
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


def frozen_baseline() -> dict[str, int]:
    frozen = {}
    for line in FROZEN_BASELINE.read_text(encoding="utf-8").splitlines():
        if line and not line.startswith("#"):
            digest, count = line.split()
            frozen[digest] = int(count)
    return frozen


def baseline_digest(entry: dict) -> str:
    key = "|".join((entry["file"], entry["function"], entry["kind"], entry["detail"], entry.get("guard") or ""))
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:20]


def baseline_problems(document: dict, frozen: dict[str, int] | None = None) -> list[str]:
    """A BASELINE entry must be a frozen one, with its guard, at no higher count."""

    frozen = frozen_baseline() if frozen is None else frozen
    problems = []
    for entry in document["sites"]:
        if entry.get("category") != "BASELINE":
            continue
        digest = baseline_digest(entry)
        if digest not in frozen or entry.get("count", 0) > frozen[digest]:
            problems.append(
                f"{entry['file']}:{entry['function']}:{entry['kind']}:{entry['detail']} is BASELINE but is not "
                f"the frozen site (new, renamed, guard changed or count raised): review it into PHYSICS, "
                f"NUMBER_INTEGRITY or INTERNAL with a protects text")
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


def exclusion_codes(catalogs: list[dict], effect_name: str) -> set[str]:
    codes = set()
    for catalog in catalogs:
        for code, spec in catalog.items():
            effect = spec.get("effect") if isinstance(spec, dict) else getattr(spec, "effect", None)
            if effect == effect_name:
                codes.add(code)
    return codes


def current_catalogs() -> list[dict]:
    from joulewise.flags.catalog import DRAFT_CODES

    catalogs = [dict(DRAFT_CODES), json.loads(FIXTURE_CATALOG.read_bytes())["codes"]]
    if SEALED_CATALOG.is_file():
        catalogs.append(json.loads(SEALED_CATALOG.read_bytes())["codes"])
    return catalogs


EXCLUSION_SECTIONS = (("window_exclusions", "EXCLUDE_WINDOW"), ("member_exclusions", "EXCLUDE_MEMBER"))
# Codes classified BASELINE at the census; a new excluding code is never BASELINE.
BASELINE_EXCLUSIONS = frozenset({
    "calibration.ledger_snapshot_refused", "whole_window.verdict_absent", "member.admission_aborted",
    "member.cooldown_evidence_unverified", "member.strict_validation_failed",
    "member.target_phase_precheck_failed",
})


def window_exclusion_problems(document: dict, catalogs: list[dict]) -> list[str]:
    """Every excluding flag code is listed with what it protects (EXCLUDE_WINDOW and EXCLUDE_MEMBER)."""

    problems = []
    for section, effect in EXCLUSION_SECTIONS:
        listed = document[section]
        codes = exclusion_codes(catalogs, effect)
        if effect == "EXCLUDE_WINDOW":
            # Pack-scoped window reasons (ruling Q11): a DISCLOSE code that
            # removes the window on one pack only is listed like a code.
            from joulewise.flags.exclusions import PACK_SCOPED_WINDOW_REASONS
            codes |= {reason for reasons in PACK_SCOPED_WINDOW_REASONS.values() for reason in reasons.values()}
        problems += [f"{effect} code {code} is not in {section}: name the physical quantity or the number it "
                     f"protects, or make it DISCLOSE" for code in sorted(codes - set(listed))]
        problems += [f"{section} lists {code}, which no catalog makes {effect}"
                     for code in sorted(set(listed) - codes)]
        for code, entry in listed.items():
            category = entry.get("category")
            if category not in ("PHYSICS", "NUMBER_INTEGRITY", "DEFERRED_REPRESENTATION", "BASELINE"):
                problems.append(f"{section} {code}: category {category!r}")
            elif category == "BASELINE" and code not in BASELINE_EXCLUSIONS:
                problems.append(f"{section} {code}: a new excluding code is never BASELINE")
            elif category != "BASELINE" and len(str(entry.get("protects") or "").strip()) < MIN_PROTECTS:
                problems.append(f"{section} {code}: name what it protects")
            if category == "DEFERRED_REPRESENTATION" and not str(entry.get("owner") or "").strip():
                problems.append(f"{section} {code}: DEFERRED_REPRESENTATION needs an owner")
    return problems


class RefusalAllowlistTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = census.load_allowlist()

    def test_every_refusal_site_is_listed_with_its_exact_count(self):
        result = census.differences(self.document)
        self.assertEqual(result, {"unlisted": [], "stale": [], "miscounted": [], "guard_changed": []},
                         "refusal sites on the HAZARD path differ from configs/gates/hazard_refusals.json; "
                         "run python -m tests.hazards.refusal_census\n" + json.dumps(result, indent=1)[:6000])

    def test_every_entry_names_what_it_protects(self):
        self.assertEqual(entry_problems(self.document), [])

    def test_the_baseline_is_frozen(self):
        self.assertEqual(hashlib.sha256(FROZEN_BASELINE.read_bytes()).hexdigest(), FROZEN_BASELINE_SHA256,
                         "refusal_baseline_frozen.txt changed: it may never gain a line")
        self.assertEqual(baseline_problems(self.document), [])

    def test_the_scan_covers_every_module_the_hazard_path_imports(self):
        self.assertEqual(scope_problems(self.document), [])

    def test_every_window_exclusion_names_what_it_protects(self):
        self.assertEqual(window_exclusion_problems(self.document, current_catalogs()), [])

    def test_the_design_catalogs_exclusions_are_listed_before_the_seal(self):
        """Audit-fix batch 1 (item 7): the draft sealed catalog on the design branch makes
        roster.run_id_mismatch EXCLUDE_MEMBER; the seal would otherwise fail the test above."""
        import subprocess
        try:
            raw = subprocess.run(["git", "-C", str(ROOT), "show", f"{DESIGN_BRANCH}:{SEALED_CATALOG.relative_to(ROOT)}"],
                                 capture_output=True, check=False, timeout=60).stdout
            design = json.loads(raw)["codes"] if raw else None
        except (OSError, subprocess.SubprocessError, ValueError, KeyError):
            design = None
        if design is None:
            self.skipTest("the block-5 design branch is not in this clone")
        missing = [problem for problem in window_exclusion_problems(self.document, current_catalogs() + [design])
                   if " is not in " in problem]
        self.assertEqual(missing, [])
        self.assertEqual("NUMBER_INTEGRITY", self.document["member_exclusions"]["roster.run_id_mismatch"]["category"])

    # ---------------------------------------------------------- the guard fails

    def test_a_new_or_retargeted_or_widened_baseline_entry_fails(self):
        broken = copy.deepcopy(self.document)
        broken["sites"].append({"file": "joulewise/b5/driver.py", "function": "f", "kind": "raise",
                                "detail": "ValueError", "count": 1, "category": "BASELINE", "guard": "0"})
        self.assertEqual(len(baseline_problems(broken)), 1)
        broken = copy.deepcopy(self.document)
        entry = next(row for row in broken["sites"] if row["category"] == "BASELINE" and row["count"] == 1)
        entry["detail"] += " retargeted"
        self.assertEqual(len(baseline_problems(broken)), 1)
        entry = next(row for row in broken["sites"] if row["category"] == "BASELINE" and row is not entry)
        entry["guard"] = "f" * 16
        self.assertEqual(len(baseline_problems(broken)), 2)
        entry["guard"] = next(row for row in self.document["sites"] if row["file"] == entry["file"]
                              and row["function"] == entry["function"] and row["kind"] == entry["kind"]
                              and row["detail"] == entry["detail"])["guard"]
        entry["count"] += 1
        self.assertEqual(len(baseline_problems(broken)), 2)

    def test_removing_a_baseline_entry_needs_no_other_edit(self):
        broken = copy.deepcopy(self.document)
        broken["sites"] = [row for row in broken["sites"] if row["category"] != "BASELINE"][:5] + \
            [row for row in broken["sites"] if row["category"] == "BASELINE"][1:]
        self.assertEqual(baseline_problems(broken), [])

    def test_an_entry_without_a_quantity_fails(self):
        broken = copy.deepcopy(self.document)
        entry = next(row for row in broken["sites"] if row["category"] == "PHYSICS")
        entry["protects"] = "fail closed"
        self.assertTrue(any("must name" in problem for problem in entry_problems(broken)))
        entry["category"] = "REPRESENTATION"
        self.assertTrue(any("category" in problem for problem in entry_problems(broken)))

    def test_a_deferred_representation_without_an_owner_fails(self):
        # The live list may hold no deferred entry (the lineage lane cleared the last two in
        # 3a9327e51), so the test turns a reviewed entry into one.
        broken = copy.deepcopy(self.document)
        entry = next(row for row in broken["sites"] if row["category"] == "PHYSICS")
        entry.update(category="DEFERRED_REPRESENTATION", owner="a lane")
        self.assertEqual(entry_problems(broken), [])
        entry.pop("owner")
        self.assertTrue(any("owner" in problem for problem in entry_problems(broken)))

    def test_an_unclassified_window_or_member_exclusion_fails(self):
        for effect in ("EXCLUDE_WINDOW", "EXCLUDE_MEMBER"):
            catalogs = current_catalogs() + [{"records.new_fail_closed": {"effect": effect}}]
            problems = window_exclusion_problems(self.document, catalogs)
            self.assertTrue(any("records.new_fail_closed" in problem for problem in problems), problems)
        broken = copy.deepcopy(self.document)
        broken["member_exclusions"]["member.timeout"] = {"category": "BASELINE"}
        self.assertTrue(window_exclusion_problems(broken, current_catalogs()))

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

    def test_assert_check_true_and_verdict_fields_are_sites(self):
        found = self.keys("""
            def f(entry, record):
                assert record is not None, "record_missing"
                subprocess.run(["x"], check=True)
                entry["valid"] = False
                record.admitted = False
                return {"eligible": False, "valid": True}
            def g():
                return make(valid=False)
        """)
        self.assertIn(("m.py", "f", "raise", "AssertionError|record_missing"), found)
        self.assertIn(("m.py", "f", "raise", "CalledProcessError|run"), found)
        self.assertIn(("m.py", "f", "status", "valid=False"), found)
        self.assertIn(("m.py", "f", "status", "admitted=False"), found)
        self.assertIn(("m.py", "f", "status", "eligible=False"), found)
        self.assertIn(("m.py", "g", "status", "valid=False"), found)
        self.assertNotIn(("m.py", "f", "status", "valid=True"), found)

    def test_a_guard_digest_follows_the_condition_not_the_line(self):
        def guards(source):
            return census.site_guards(census.scan_source("m.py", textwrap.dedent(source)))

        one = guards("""
            def f():
                if a:
                    raise ValueError("bad thing here")
        """)
        moved = guards("""

            def f():
                x = 1

                if a:
                    raise ValueError("bad thing here: " + x)
        """)
        widened = guards("""
            def f():
                if a or b:
                    raise ValueError("bad thing here")
        """)
        self.assertEqual(one, moved)
        self.assertNotEqual(one, widened)
        caught = guards("""
            def f():
                try:
                    raise ValueError("bad thing here")
                except Exception:
                    pass
        """)
        narrowed = guards("""
            def f():
                try:
                    raise ValueError("bad thing here")
                except KeyError:
                    pass
        """)
        self.assertNotEqual(caught, narrowed)

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


class ReviewMutationTests(unittest.TestCase):
    """The Sol 6.1 review's bypasses (2026-10-06), applied in memory to the real sources."""

    @classmethod
    def setUpClass(cls):
        cls.document = census.load_allowlist()

    def mutated(self, file: str, old: str, new: str) -> dict:
        source = (ROOT / file).read_text(encoding="utf-8")
        self.assertIn(old, source, f"{file} no longer contains the mutation anchor; pick another")
        changed = new if old == source else source.replace(old, new, 1)
        real = Path.read_text

        def read_text(path, *args, **kwargs):
            return changed if Path(path) == ROOT / file else real(path, *args, **kwargs)

        with patch.object(Path, "read_text", read_text):
            result = census.differences(self.document)
            result["scope_gaps"] = list(census.iter_scope_gaps(self.document))
        return result

    def appended(self, file: str, text: str) -> dict:
        source = (ROOT / file).read_text(encoding="utf-8")
        return self.mutated(file, source, source + text)

    def test_widening_an_existing_refusal_condition_is_seen(self):
        result = self.mutated("joulewise/controller.py", 'or pre is None or pre.disposition != "valid"',
                              'or pre is None or pre.disposition != "valid" '
                              'or config.run_id != config.run_id.lower()')
        self.assertTrue(result["guard_changed"], result)

    def test_setting_a_verdict_field_false_is_seen(self):
        result = self.appended("joulewise/b5/driver.py",
                               "\n\ndef _census_probe(entry):\n    entry[\"valid\"] = False\n")
        self.assertTrue(any(row["detail"] == "valid=False" for row in result["unlisted"]), result)

    def test_a_plain_exit_in_rendered_chain_text_is_seen(self):
        result = self.mutated("joulewise/b5/chain.py", '    lines.append("settle")',
                              '    lines.append("exit 9")\n    lines.append("settle")')
        self.assertTrue(any(row["detail"] == "exit 9" for row in result["unlisted"]), result)

    def test_a_stop_in_the_runbook_screen_function_is_seen(self):
        result = self.mutated("docs/phase_2/window_runbook.md", "screen_pre_calibration() {",
                              "screen_pre_calibration() {\n  return 7")
        self.assertTrue(any(row["detail"] == "return 7" for row in result["unlisted"]), result)

    def test_a_new_script_run_by_name_and_a_computed_import_are_scope_gaps(self):
        result = self.appended("joulewise/b5/driver.py",
                               '\n\nCHECK_ARGV = ("python", "scripts/size_b5_window.py")\n\n\n'
                               'def _census_load(name):\n    return importlib.import_module(name)\n')
        gaps = "\n".join(result["scope_gaps"])
        self.assertIn("scripts/size_b5_window.py", gaps)
        self.assertIn("computed name", gaps)


if __name__ == "__main__":
    unittest.main()
