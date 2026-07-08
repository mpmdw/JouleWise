import unittest

from scripts import build_site


SESSION_HEADING = "Session History (pointers only \u2014 run reports own the narrative)"


class BuildSiteParserTests(unittest.TestCase):
    def assert_fail_closed(self, func, *args):
        with self.assertRaises(build_site.SiteBuildError):
            func(*args)

    def test_parse_status_at_glance(self):
        md = """# X

## Status At A Glance

| Phase | Scope | Status |
|---|---|---|
| 1. One | work | **in progress** - active; setup COMPLETE |
| 2. Two | work | planned |
"""
        phases = build_site.parse_status_at_glance(md)
        self.assertEqual(["in progress", "planned"], [phase.state for phase in phases])
        self.assert_fail_closed(build_site.parse_status_at_glance, md.replace("Status", "State"))

    def test_parse_current_verification(self):
        md = """# X

## Current Verification

- Suite: `python3 -m unittest discover -s tests` -> `Ran 564
  tests, OK (skipped=10)`.
"""
        verification = build_site.parse_current_verification(md)
        self.assertEqual((564, 10), (verification.tests, verification.skips))
        self.assert_fail_closed(build_site.parse_current_verification, md.replace("Ran", "Executed"))

    def test_parse_bundle_count(self):
        self.assertEqual(6, build_site.parse_bundle_count("all 6 real corpus bundles"))
        self.assert_fail_closed(build_site.parse_bundle_count, "all 6 real corpus bundles", "all 7 real corpus bundles")

    def test_parse_project_now(self):
        project = "- Project phase: Phase 1 closing; Phase 2 in progress\n  continuation text\n"
        run = """# Run

## Current Project Status

**P2-013 is COMPLETE.** More detail follows.

## Next
"""
        now = build_site.parse_project_now(project, run)
        self.assertIn("Phase 2", now.phase_line)
        self.assertIn("continuation text", now.phase_line)
        self.assertIn("P2-013", now.first_status_sentence)
        self.assert_fail_closed(build_site.parse_project_now, project, run.replace("**", ""))

    def test_parse_project_now_trims_to_first_bolded_sentence(self):
        project = "- Project phase: Phase 1 closing; Phase 2 in progress\n"
        run = """# Run

## Current Project Status

**P2-013 is COMPLETE.** More detail follows in the source paragraph. **A later sentence is not the station summary.**

## Next
"""
        now = build_site.parse_project_now(project, run)
        self.assertEqual("**P2-013 is COMPLETE.**", now.first_status_sentence)
        self.assert_fail_closed(
            build_site.parse_project_now,
            project,
            run.replace("**P2-013 is COMPLETE.**", "**P2-013 is COMPLETE**").replace(
                "**A later sentence is not the station summary.**",
                "**A later sentence is not the station summary**",
            ),
        )

    def test_parse_session_history(self):
        md = f"""# Run

## {SESSION_HEADING}

- 2026-07-08 latest session title:
  `docs/run_reports/latest.md`
- 2026-07-07 older session title:
  `docs/run_reports/older.md`
- Older: see directory.
"""
        sessions = build_site.parse_session_history(md)
        self.assertEqual("docs/run_reports/latest.md", sessions[0].report)
        self.assert_fail_closed(build_site.parse_session_history, md.replace("`docs/run_reports/latest.md`", "docs/run_reports/latest.md"))
        self.assertEqual("docs/run_reports/latest.md", build_site.latest_report_source_from_sessions(sessions))

    def test_parse_current_queue(self):
        md = """# Queue

## Current Queue

| Rank | ID | Priority | Status | Task | Evidence / Acceptance |
|---:|---|---|---|---|---|
| 1 | P2-015 | P2 Next Slice | NEW [QUIET-MAC] | Calibrate | Bundle set |
| 2 | P2-006 | P2 Next Slice | OPEN [AGENT] | Build | Tests |
| 3 | P1-001 | P1 | waiting-user | Supervisor | Approval |
"""
        queue = build_site.parse_current_queue(md)
        self.assertEqual(("P2-015", "QUIET-MAC"), (queue[0].task_id, queue[0].lane))
        self.assertEqual(("P2-006", "AGENT"), (queue[1].task_id, queue[1].lane))
        self.assertEqual(("P1-001", None), (queue[2].task_id, queue[2].lane))
        self.assert_fail_closed(build_site.parse_current_queue, md.replace("Evidence / Acceptance", "Acceptance"))

    def test_parse_completed_queue(self):
        md = """# Queue

## Completed Queue Items

| ID | Priority | Completed | Task | Evidence |
|---|---|---|---|---|
| P2-011 | P2 | 2026-07-07 | Done | PR |
"""
        rows = build_site.parse_completed_queue(md)
        self.assertEqual("P2-011", rows[0]["ID"])
        self.assert_fail_closed(build_site.parse_completed_queue, md.replace("| ID | Priority | Completed | Task | Evidence |", "| ID | Task |"))

    def test_parse_do_not_do(self):
        md = """# Queue

## Current Do-Not-Do-Yet List

- Do not start live split.
  before replay exists.
- Do not close D-016.
"""
        items = build_site.parse_do_not_do(md)
        self.assertEqual(2, len(items))
        self.assertIn("before replay exists", items[0])
        self.assert_fail_closed(build_site.parse_do_not_do, "## Current Do-Not-Do-Yet List\n\nNo bullets")

    def test_parse_risk_summary(self):
        md = """# Risks

## Summary

| ID | Risk | Phase | Likelihood | Impact | Status |
|---|---|---|---|---|---|
| R-001 | Scope shift | 1 | medium | high | open |
"""
        risks = build_site.parse_risk_summary(md)
        self.assertEqual("high", risks[0].impact)
        self.assert_fail_closed(build_site.parse_risk_summary, md.replace("Likelihood", "Chance"))

    def test_parse_decision_index(self):
        md = """# Decisions

## Index

| ID | Title | Status |
|---|---|---|
| D-001 | Bundle layout | accepted |
"""
        rows = build_site.parse_decision_index(md)
        self.assertEqual("D-001", rows[0].decision_id)
        self.assert_fail_closed(build_site.parse_decision_index, md.replace("Status", "State"))

    def test_parse_council_index(self):
        md = """# Councils

## Index

| ID | Date | Topic | Outcome |
|---|---|---|---|
| C-001 | 2026-07-06 | Review | adopted |

## C-002: Added later (2026-07-07)

Text.
"""
        self.assert_fail_closed(build_site.parse_council_index, md)
        md = md.replace(
            "| C-001 | 2026-07-06 | Review | adopted |",
            "| C-001 | 2026-07-06 | Review | adopted |\n| C-002 | 2026-07-07 | Added later | accepted |",
        )
        rows = build_site.parse_council_index(md)
        self.assertEqual(["C-001", "C-002"], [row.council_id for row in rows])
        self.assertEqual("accepted", rows[1].outcome)
        self.assert_fail_closed(build_site.parse_council_index, md.replace("Outcome", "Result"))


if __name__ == "__main__":
    unittest.main()
