import base64
import contextlib
import gzip
import io
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import build_site, pack_capsule

# D-101 addendum II (2026-08-03, Ed-directed; widens the 2026-08-02
# addendum): the site observatory is a separate failure domain — NO
# site-lane test, synthetic-input or live-content, runs in the project's
# blocking suite. The whole module runs in the site workflow with this
# variable set.
SITE_CONTENT_TESTS = unittest.skipUnless(
    os.environ.get("JOULEWISE_SITE_CONTENT_TESTS"),
    "site-lane test (site workflow; set JOULEWISE_SITE_CONTENT_TESTS=1)",
)


SESSION_HEADING = "Session History (pointers only \u2014 run reports own the narrative)"


def gzip_decompress_base64(value: str) -> str:
    return gzip.decompress(base64.b64decode(value)).decode("utf-8")


@SITE_CONTENT_TESTS
class BuildSiteParserTests(unittest.TestCase):
    def assert_fail_closed(self, func, *args):
        with self.assertRaises(build_site.SiteBuildError):
            func(*args)

    def test_claim_surfaces_do_not_render_d078_voided_values(self):
        sources = {
            name: build_site.read_source(f"docs/site_src/{name}")
            for name in ("index.html", "research.html", "results.html")
        }
        for name, source in sources.items():
            with self.subTest(name=name):
                self.assertIn("D-078", source)
                self.assertNotRegex(
                    source, r"@@FLOOR_(?:REQUEST|PHASE|SUITE)_[A-Z0-9_]+@@"
                )

        stamp_sources = {
            "README.md",
            "docs/decision_log.md",
            "docs/contracts/measurement_methodology.md",
            "docs/contracts/claims_ladder.md",
            "docs/phase_2/detection_floor.md",
            "docs/site_src/index.html",
            "docs/site_src/research.html",
            "docs/site_src/results.html",
        }
        stamps = {
            source: build_site.SourceStamp(source, "fixture")
            for source in stamp_sources
        }
        rendered = {
            "index.html": build_site.render_project_page(stamps),
            "research.html": build_site.render_learning_page(stamps),
            "results.html": build_site.render_measurements_page(stamps),
        }
        for name, page in rendered.items():
            with self.subTest(rendered=name):
                self.assertIn("D-078", page)
                self.assertNotRegex(page, r"@@[A-Z0-9_]+@@")

        combined = "\n".join(rendered.values())
        self.assertNotIn("Verified Window-A floor extraction", combined)
        self.assertNotIn("≈47.2", combined)
        self.assertNotIn("≈44.4", combined)
        self.assertNotIn("86.8", combined)

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
- 2026-07-07 process trace title:
  `docs/process_traces/older.md`
- Older: see directory.
"""
        sessions = build_site.parse_session_history(md)
        self.assertEqual(
            [
                build_site.SessionPointer(
                    "2026-07-08",
                    "latest session title",
                    "docs/run_reports/latest.md",
                ),
                build_site.SessionPointer(
                    "2026-07-07",
                    "process trace title",
                    "docs/process_traces/older.md",
                ),
            ],
            sessions,
        )
        expected_pointer_error = re.escape(
            "docs/run_reports/...md or docs/process_traces/...md"
        )
        with self.assertRaisesRegex(build_site.SiteBuildError, expected_pointer_error):
            build_site.parse_session_history(
                md.replace(
                    "`docs/run_reports/latest.md`",
                    "docs/run_reports/latest.md",
                )
            )
        with self.assertRaisesRegex(build_site.SiteBuildError, expected_pointer_error):
            build_site.parse_session_history(
                md.replace(
                    "`docs/run_reports/latest.md`",
                    "`docs/reviews/latest.md`",
                )
            )
        self.assertEqual("docs/run_reports/latest.md", build_site.latest_report_source_from_sessions(sessions))
        process_trace = sessions[1]
        self.assertEqual(
            process_trace.report,
            build_site.latest_report_source_from_sessions([process_trace]),
        )
        self.assertEqual(
            "../process_traces/older.md",
            build_site.report_href(process_trace.report),
        )
        self.assertEqual(
            "latest_run_report.html",
            build_site.report_href(process_trace.report, process_trace.report),
        )

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

    def test_basic_markdown_preserves_nested_unordered_lists(self):
        report = (build_site.ROOT / "docs/run_reports/2026-07-09-advisor-status-site.md").read_text(encoding="utf-8")
        rendered = build_site.render_basic_markdown(report)

        self.assertIn("Counterreview dispositions:<ul>", rendered)
        self.assertIn("<li><strong>Accepted/P1:</strong> generated", rendered)
        self.assertNotIn("<li>Counterreview dispositions:</li><li><strong>Accepted/P1:", rendered)

    def test_offline_fallback_is_detectable_once_per_run(self):
        previous_unavailable = build_site.MARKED_UNAVAILABLE
        previous_warned = build_site.MARKED_FALLBACK_WARNED
        try:
            build_site.MARKED_UNAVAILABLE = True
            build_site.MARKED_FALLBACK_WARNED = False
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".md") as handle:
                handle.write("# Fallback\n\n- one\n")
                handle.flush()
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    first = build_site.render_markdown(build_site.Path(handle.name))
                    second = build_site.render_markdown(build_site.Path(handle.name))

            self.assertTrue(first.startswith("<!-- rendered: offline-fallback -->\n"))
            self.assertTrue(second.startswith("<!-- rendered: offline-fallback -->\n"))
            self.assertEqual(1, stderr.getvalue().count("offline fallback markdown renderer"))
        finally:
            build_site.MARKED_UNAVAILABLE = previous_unavailable
            build_site.MARKED_FALLBACK_WARNED = previous_warned

    def test_full_decision_and_council_bodies_reach_rendered_output(self):
        decision_md = (
            "# Decision Log\n\n## Index\n\n| ID | Title | Status |\n|---|---|---|\n"
            + "".join(
                f"| D-{index:03d} | Entry {index} | accepted |\n"
                for index in range(1, 9)
            )
            + "\n---\n\n"
            + "".join(
                f"## D-{index:03d}: Entry {index}\n\ndecision-body-{index}\n\n"
                for index in range(1, 9)
            )
        )
        stamp = build_site.SourceStamp(build_site.DECISION_LOG_SOURCE, "abc1234")
        with (
            mock.patch.object(build_site, "MARKED_UNAVAILABLE", True),
            mock.patch.object(build_site, "MARKED_FALLBACK_WARNED", True),
        ):
            decision_output = "".join(
                build_site.render_decision_log_pages(decision_md, False, stamp).values()
            )
        self.assertIn("decision-body-1", decision_output)
        self.assertIn("decision-body-8", decision_output)
        self.assertNotIn("older full entries are omitted", decision_output)

        council_md = "# Council Log\n\n" + "".join(
            f"## C-{index:03d}: Council {index}\n\ncouncil-body-{index}\n\n"
            for index in range(1, 9)
        )
        council_doc = next(
            doc
            for doc in build_site.doc_pages("docs/run_reports/example.md")
            if doc.source == "docs/council_log.md"
        )
        council_output = build_site.render_doc_page(
            council_doc,
            True,
            build_site.SourceStamp("docs/council_log.md", "abc1234"),
            council_md,
        )
        self.assertIn("council-body-1", council_output)
        self.assertIn("council-body-8", council_output)
        self.assertNotIn("older full entries are omitted", council_output)

    def test_decision_anchor_slugs_ignore_addendum_headings(self):
        # Regression: a "## D-100 addendum (...)" H2 rides inside a newer
        # entry's body; it must not mint the d-100 short anchor for D-100.
        md = (
            "## D-101: Entry\nbody\n\n"
            "## D-100 addendum (2026-08-01): later ruling\naddendum body\n\n"
            "## D-102: Entry\nbody\n"
        )
        self.assertEqual(
            set(build_site.decision_anchor_slugs(md)),
            {"D-101", "D-102"},
        )

    def test_full_log_body_is_escaped_by_offline_fallback_renderer(self):
        md = "# Log\n\n" + "".join(
            f"## D-{index:03d}: <Entry & {index}>\nbody\n\n"
            for index in range(1, 8)
        )
        rendered = build_site.render_basic_markdown(md)
        self.assertIn("&lt;Entry &amp; 1&gt;", rendered)
        self.assertIn("&lt;Entry &amp; 7&gt;", rendered)
        self.assertNotIn("<Entry & 1>", rendered)

    def test_build_fails_closed_without_project_status_page_marker(self):
        project_md = build_site.read_source("PROJECT_STATUS.md").replace(
            build_site.PROJECT_STATUS_PAGE_END_MARKER, ""
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                mock.patch.object(build_site, "OUT", Path(temp_dir) / "site"),
                mock.patch.object(build_site, "read_source", return_value=project_md),
                self.assertRaisesRegex(
                    build_site.SiteBuildError,
                    build_site.re.escape(build_site.PROJECT_STATUS_PAGE_END_MARKER),
                ),
            ):
                build_site.build(no_marked=True)

    def test_project_status_pages_are_emitted_and_cross_linked(self):
        project_md = build_site.read_source("PROJECT_STATUS.md")
        status_markdown = build_site.split_project_status_markdown(project_md)
        status_docs = {
            doc.out_name: doc
            for doc in build_site.doc_pages("docs/run_reports/example.md")
            if doc.source == "PROJECT_STATUS.md"
        }
        expected_outputs = {
            build_site.PROJECT_STATUS_SUMMARY_OUTPUT,
            build_site.PROJECT_STATUS_FULL_OUTPUT,
        }
        self.assertEqual(set(status_markdown), expected_outputs)
        self.assertEqual(set(status_docs), expected_outputs)

        stamp = build_site.SourceStamp("PROJECT_STATUS.md", "test")
        with (
            mock.patch.object(build_site, "MARKED_UNAVAILABLE", True),
            mock.patch.object(build_site, "MARKED_FALLBACK_WARNED", True),
        ):
            rendered = {
                out_name: build_site.render_doc_page(
                    status_docs[out_name], False, stamp, markdown
                )
                for out_name, markdown in status_markdown.items()
            }
        self.assertIn(
            f'href="{build_site.PROJECT_STATUS_FULL_OUTPUT}"',
            rendered[build_site.PROJECT_STATUS_SUMMARY_OUTPUT],
        )
        self.assertIn(
            f'href="{build_site.PROJECT_STATUS_SUMMARY_OUTPUT}"',
            rendered[build_site.PROJECT_STATUS_FULL_OUTPUT],
        )

    def test_oversized_divisible_decision_log_paginates_without_content_loss(self):
        generator = random.Random(20260724)
        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        entries = []
        for number in range(1, 7):
            payload = "".join(generator.choice(alphabet) for _ in range(9_000))
            body_marker = f"entry-body-marker-{number}"
            cross_link = (
                "\n\n[Jump to the oldest decision](#d-001-entry-1).\n"
                if number == 6
                else ""
            )
            entries.append(
                f"## D-{number:03d}: Entry {number}\n\n{body_marker} {payload}{cross_link}\n\n"
            )
        index = "\n".join(
            f"| D-{number:03d} | Entry {number} | accepted |"
            for number in range(1, 7)
        )
        markdown = (
            "# Decision Log\n\n"
            "Synthetic pagination fixture.\n\n"
            "## Index\n\n"
            "| ID | Title | Status |\n"
            "|---|---|---|\n"
            f"{index}\n\n---\n\n"
            + "".join(entries)
        )
        stamp = build_site.SourceStamp(build_site.DECISION_LOG_SOURCE, "abc1234")
        previous_unavailable = build_site.MARKED_UNAVAILABLE
        previous_warned = build_site.MARKED_FALLBACK_WARNED
        try:
            build_site.MARKED_UNAVAILABLE = True
            build_site.MARKED_FALLBACK_WARNED = True
            first = build_site.render_decision_log_pages(markdown, False, stamp)
            second = build_site.render_decision_log_pages(markdown, False, stamp)
        finally:
            build_site.MARKED_UNAVAILABLE = previous_unavailable
            build_site.MARKED_FALLBACK_WARNED = previous_warned

        self.assertEqual(first, second)
        self.assertGreater(len(first), 1)
        main_doc = next(
            doc
            for doc in build_site.doc_pages("docs/run_reports/example.md")
            if doc.out_name == build_site.DECISION_LOG_OUTPUT
        )
        with (
            mock.patch.object(build_site, "MARKED_UNAVAILABLE", True),
            mock.patch.object(build_site, "MARKED_FALLBACK_WARNED", True),
        ):
            unsplit = build_site.compact_generated_html(
                build_site.render_doc_page(
                    main_doc,
                    False,
                    stamp,
                    markdown,
                )
            )
        unsplit_pages = {
            "/decision_log.html": {
                "html": unsplit,
                "sources": [{"source": stamp.source, "commit": stamp.commit}],
                "aliases": [],
            }
        }
        self.assertGreater(
            pack_capsule.encode_page_shard(
                unsplit_pages, ["/decision_log.html"]
            )[1]["base64"],
            pack_capsule.MAX_SHARD_BASE64_BYTES,
        )

        packed_pages = {}
        for out_name, rendered in first.items():
            path = f"/{out_name}"
            packed_pages[path] = {
                "html": build_site.compact_generated_html(rendered),
                "sources": [{"source": stamp.source, "commit": stamp.commit}],
                "aliases": [],
            }
            self.assertGreater(
                pack_capsule.encode_page_shard(packed_pages, [path])[1]["base64"],
                0,
            )
            self.assertEqual(
                pack_capsule.extract_stamps(out_name, rendered),
                [{"source": build_site.DECISION_LOG_SOURCE, "commit": "abc1234"}],
            )
        pack_capsule.page_shards(packed_pages)

        oldest_page = next(
            out_name
            for out_name, rendered in first.items()
            if 'id="d-001"' in rendered
        )
        self.assertIn(
            f'href="{oldest_page}#d-001-entry-1"',
            first[build_site.DECISION_LOG_OUTPUT],
        )
        combined = "".join(first.values())
        for number in range(1, 7):
            self.assertEqual(combined.count(f'id="d-{number:03d}"'), 1)
            self.assertEqual(combined.count(f"entry-body-marker-{number}"), 1)

    def test_indivisible_decision_unit_raw_source_only_warns(self):
        markdown = (
            "# Decision Log\n\n"
            "## Index\n\n"
            "| ID | Title | Status |\n"
            "|---|---|---|\n"
            "| D-001 | Giant | accepted |\n\n"
            "---\n\n"
            "## D-001: Giant\n\n"
            + ("indivisible-body " * 80)
            + "\n"
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            parts = build_site.split_decision_log_markdown(
                markdown,
                max_part_markdown_bytes=300,
            )
        combined = "".join(part.markdown for part in parts)
        self.assertIn("indivisible-body", combined)
        self.assertIn("ADVISORY BUDGET EXCEEDED (D-135)", stderr.getvalue())
        self.assertIn("indivisible D-001 entry page", stderr.getvalue())

        # D-135: raw source bytes over the cap are a PROXY observation only —
        # they warn; the real validator's artifact measurement (pack_capsule)
        # is the sole size failure. Content still reaches the output.
        proxy_stderr = io.StringIO()
        with (
            mock.patch.object(build_site, "LAKEBED_PLATFORM_CAP_BYTES", 500),
            contextlib.redirect_stderr(proxy_stderr),
        ):
            proxy_parts = build_site.split_decision_log_markdown(
                markdown,
                max_part_markdown_bytes=300,
            )
        self.assertIn("indivisible-body", "".join(part.markdown for part in proxy_parts))
        self.assertIn("RAW-SOURCE PROXY", proxy_stderr.getvalue())
        self.assertIn("ADVISORY BUDGET EXCEEDED (D-135)", proxy_stderr.getvalue())

    def test_oversized_decision_entry_splits_at_subsections_with_one_anchor(self):
        generator = random.Random(20260811)
        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        subsections = []
        for number in range(1, 6):
            payload = "".join(generator.choice(alphabet) for _ in range(5_000))
            subsections.append(
                f"### Amendment {number}\n\nmarker-{number} {payload}\n\n"
            )
        markdown = (
            "# Decision Log\n\n"
            "## Index\n\n"
            "| ID | Title | Status |\n"
            "|---|---|---|\n"
            "| D-001 | Giant | accepted |\n\n"
            "---\n\n"
            "## D-001: Giant\n\nOpening text.\n\n"
            + "".join(subsections)
        )

        parts = build_site.split_decision_log_markdown(markdown)

        self.assertGreater(len(parts), 2)
        combined = "".join(part.markdown for part in parts)
        self.assertEqual(combined.count("## D-001: Giant"), 1)
        self.assertGreaterEqual(combined.count("## (D-001 continued)"), 1)
        self.assertEqual(
            sum("D-001" in part.decision_ids for part in parts),
            1,
        )
        self.assertEqual(
            sum("D-001" in build_site.decision_anchor_slugs(part.markdown) for part in parts),
            1,
        )
        for number in range(1, 6):
            self.assertEqual(combined.count(f"marker-{number}"), 1)
        for part in parts:
            self.assertTrue(part.markdown)

        stamp = build_site.SourceStamp(build_site.DECISION_LOG_SOURCE, "abc1234")
        with (
            mock.patch.object(build_site, "MARKED_UNAVAILABLE", True),
            mock.patch.object(build_site, "MARKED_FALLBACK_WARNED", True),
        ):
            rendered = build_site.render_decision_log_pages(markdown, False, stamp)
        rendered_combined = "".join(rendered.values())
        self.assertEqual(rendered_combined.count('id="d-001"'), 1)
        for out_name, page in rendered.items():
            path = f"/{out_name}"
            packed_page = {
                path: {
                    "html": build_site.compact_generated_html(page),
                    "sources": [{"source": stamp.source, "commit": stamp.commit}],
                    "aliases": [],
                }
            }
            self.assertGreater(
                pack_capsule.encode_page_shard(packed_page, [path])[1]["base64"],
                0,
            )

    def test_oversized_decision_index_splits_at_rows_and_repeats_header(self):
        generator = random.Random(20260812)
        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        rows = []
        for number in range(1, 13):
            payload = "".join(generator.choice(alphabet) for _ in range(180))
            rows.append(
                f"| D-{number:03d} | row-marker-{number} {payload} | accepted |\n"
            )
        header = "| ID | Title | Status |\n|---|---|---|\n"
        markdown = (
            "# Decision Log\n\nGuide.\n\n"
            "## Index\n\n"
            + header
            + "".join(rows)
            + "\n---\n\n"
            + "## D-012: Latest\n\nBody.\n"
        )

        parts = build_site.split_decision_log_markdown(
            markdown,
            max_part_markdown_bytes=1_000,
        )
        index_parts = [
            part
            for part in parts
            if "## Index" in part.markdown or "## (index continued)" in part.markdown
        ]

        self.assertGreater(len(index_parts), 1)
        self.assertEqual(index_parts[0].markdown.count("## Index"), 1)
        for part in index_parts[1:]:
            self.assertIn("## (index continued)", part.markdown)
        for part in index_parts:
            self.assertEqual(part.markdown.count(header), 1)
            self.assertTrue(part.markdown)
        combined = "".join(part.markdown for part in index_parts)
        for number in range(1, 13):
            self.assertEqual(combined.count(f"row-marker-{number} "), 1)

    def test_real_d078_entry_splits_at_subsections_without_losing_anchors(self):
        source = build_site.read_source(build_site.DECISION_LOG_SOURCE)
        matches = list(build_site.DECISION_LOG_ENTRY_RE.finditer(source))
        d078_index = next(
            index
            for index, match in enumerate(matches)
            if match.group("decision_id") == "D-078"
        )
        entry = source[
            matches[d078_index].start():matches[d078_index + 1].start()
        ]
        markdown = (
            "# Decision Log\n\n"
            "## Index\n\n"
            "| ID | Title | Status |\n"
            "|---|---|---|\n"
            "| D-078 | Soundness gate | accepted |\n\n"
            "---\n\n"
            + entry
        )
        self.assertGreater(
            len(entry.encode("utf-8")),
            build_site.DECISION_LOG_PART_MARKDOWN_BYTES,
        )

        stamp = build_site.SourceStamp(build_site.DECISION_LOG_SOURCE, "abc1234")
        with (
            mock.patch.object(build_site, "MARKED_UNAVAILABLE", True),
            mock.patch.object(build_site, "MARKED_FALLBACK_WARNED", True),
        ):
            rendered = build_site.render_decision_log_pages(markdown, False, stamp)

        combined = "".join(rendered.values())
        self.assertEqual(combined.count('id="d-078"'), 1)
        self.assertIn("(D-078 continued)", combined)
        for out_name, page in rendered.items():
            path = f"/{out_name}"
            packed_page = {
                path: {
                    "html": build_site.compact_generated_html(page),
                    "sources": [{"source": stamp.source, "commit": stamp.commit}],
                    "aliases": [],
                }
            }
            self.assertGreater(
                pack_capsule.encode_page_shard(packed_page, [path])[1]["base64"],
                0,
            )

    def _assert_production_build_output_packs_with_lakebed_size_reporting(
        self, *, force_offline_renderer: bool
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            site = temp_root / "site"
            capsule = temp_root / "capsule"
            content = capsule / "server" / "content"
            site.mkdir()
            for filename in build_site.HAND_PAGES:
                shutil.copy2(build_site.OUT / filename, site / filename)
            shutil.copy2(build_site.OUT / "style.css", site / "style.css")

            build_stdout = io.StringIO()
            build_stderr = io.StringIO()
            with (
                mock.patch.object(build_site, "OUT", site),
                mock.patch.object(
                    build_site,
                    "MARKED_UNAVAILABLE",
                    force_offline_renderer,
                ),
                mock.patch.object(build_site, "MARKED_FALLBACK_WARNED", False),
                contextlib.redirect_stdout(build_stdout),
                contextlib.redirect_stderr(build_stderr),
            ):
                build_site.build(no_marked=False)

            pack_stdout = io.StringIO()
            pack_stderr = io.StringIO()
            content.mkdir(parents=True)
            (content / "styles.ts").write_text("legacy", encoding="utf-8")
            with (
                mock.patch.object(pack_capsule, "SITE", site),
                mock.patch.object(pack_capsule, "CAPSULE", capsule),
                mock.patch.object(pack_capsule, "CAPSULE_CONTENT", content),
                mock.patch.object(
                    pack_capsule,
                    "discover_lakebed_executable",
                    return_value=Path("/fixture/lakebed"),
                ),
                mock.patch.object(
                    pack_capsule,
                    "measure_lakebed_artifact",
                    return_value=(960_030, pack_capsule.LAKEBED_VERSION),
                ),
                contextlib.redirect_stdout(pack_stdout),
                contextlib.redirect_stderr(pack_stderr),
            ):
                pages = pack_capsule.pack_pages()
                total = pack_capsule.build(no_fonts=True)
                packed_site, _ = pack_capsule.encode_site(pages, pack_capsule.stylesheet(no_fonts=True))
                measured_budget_stderr = io.StringIO()
                with mock.patch.object(
                    pack_capsule, "LAKEBED_MEASURED_ARTIFACT_BUDGET_BYTES", 0
                ), contextlib.redirect_stderr(measured_budget_stderr):
                    measured_budget_total = pack_capsule.build(no_fonts=True)
                self.assertEqual(measured_budget_total, total)
                self.assertIn(
                    "ADVISORY BUDGET EXCEEDED (D-135)",
                    measured_budget_stderr.getvalue(),
                )
                self.assertIn("exceeds measured-artifact", measured_budget_stderr.getvalue())
                decode_budget_stderr = io.StringIO()
                with (
                    mock.patch.object(pack_capsule, "MAX_FIRST_REQUEST_DECODE_BYTES", 0),
                    contextlib.redirect_stderr(decode_budget_stderr),
                ):
                    decode_budget_total = pack_capsule.build(no_fonts=True)
                self.assertEqual(decode_budget_total, total)
                self.assertIn(
                    "ADVISORY BUDGET EXCEEDED (D-135)",
                    decode_budget_stderr.getvalue(),
                )
                self.assertIn("byte-loop iterations", decode_budget_stderr.getvalue())

            shared = json.loads(gzip_decompress_base64(packed_site["shared"]))
            decoded_pages = {}
            decoded_shards = []
            for shard in packed_site["shards"]:
                decoded = json.loads(gzip_decompress_base64(shard))
                self.assertTrue(set(decoded_pages).isdisjoint(decoded))
                decoded_pages.update(decoded)
                decoded_shards.append(decoded)
            expected_names = {
                "adapter_contracts.html", "advisor_brief.html", "agent_plan.html", "claims_ladder.html",
                "council_log.html", "index.html",
                "latest_run_report.html", "library.html", "measurement_methodology.html",
                "milestones.html", "orchestration.html", "process.html",
                "project_status.html", "project_status_full.html", "readme.html", "record.html", "research.html",
                "results.html", "risk_register.html", "roadmap.html", "run_state.html",
                "status.html", "task_queue.html",
            }
            decision_names = {
                path.name
                for path in site.glob("decision_log*.html")
            }
            self.assertIn(build_site.DECISION_LOG_OUTPUT, decision_names)
            self.assertTrue(
                any(
                    name.startswith(build_site.DECISION_LOG_ARCHIVE_PREFIX)
                    for name in decision_names
                )
            )
            expected_names.update(decision_names)
            self.assertEqual({path.name for path in site.glob("*.html")}, expected_names)
            retained_decision_ids = {
                decision_id
                for part in build_site.split_decision_log_markdown(
                    build_site.read_source(build_site.DECISION_LOG_SOURCE)
                )
                for decision_id in part.decision_ids
            }
            rendered_decision_html = "".join(
                (site / name).read_text(encoding="utf-8")
                for name in sorted(decision_names)
            )
            self.assertEqual(
                {
                    decision_id.upper()
                    for decision_id in re.findall(
                        r'id="(d-\d{3})"',
                        rendered_decision_html,
                    )
                },
                retained_decision_ids,
            )
            for name in decision_names:
                decision_path = pack_capsule.canonical_path(
                    pack_capsule.page_aliases(site / name)
                )
                self.assertGreater(
                    pack_capsule.encode_page_shard(
                        pages, [decision_path]
                    )[1]["base64"],
                    0,
                )
                self.assertEqual(
                    [
                        stamp["source"]
                        for stamp in pages[decision_path]["sources"]
                    ],
                    [build_site.DECISION_LOG_SOURCE],
                )
            for status_name in (
                build_site.PROJECT_STATUS_SUMMARY_OUTPUT,
                build_site.PROJECT_STATUS_FULL_OUTPUT,
            ):
                status_path = pack_capsule.canonical_path(
                    pack_capsule.page_aliases(site / status_name)
                )
                status_pages = pages
                if status_path not in pages:
                    status_pages = {
                        status_path: {
                            **pack_capsule.pack_page(
                                pack_capsule.PageSpec(
                                    path=site / status_name,
                                    page_name=status_name,
                                    aliases=pack_capsule.page_aliases(
                                        site / status_name
                                    ),
                                )
                            ),
                            "aliases": [],
                        }
                    }
                status_size = pack_capsule.encode_page_shard(
                    status_pages, [status_path]
                )[1]["base64"]
                self.assertGreater(status_size, 0)
            brief_output = (site / build_site.ADVISOR_BRIEF_OUTPUT).read_text(
                encoding="utf-8"
            )
            provenance, separator, copied_brief = brief_output.partition("\n")
            self.assertEqual(separator, "\n")
            self.assertIn("JouleWise verbatim provenance:", provenance)
            self.assertIn(build_site.ADVISOR_BRIEF_SOURCE, provenance)
            self.assertEqual(
                copied_brief,
                (build_site.ROOT / build_site.ADVISOR_BRIEF_SOURCE).read_text(
                    encoding="utf-8"
                ),
            )
            for page_path in site.glob("*.html"):
                if page_path.name == build_site.ADVISOR_BRIEF_OUTPUT:
                    continue
                shell_html = page_path.read_text(encoding="utf-8")
                self.assertIn('href="advisor_brief.html"', shell_html)
                self.assertIn('href="project_status.html"', shell_html)
            self.assertEqual(
                pack_capsule.CAPSULE_PAGE_REDIRECTS,
                {
                    "council_log.html": "record.html",
                    "project_status_full.html": "project_status.html",
                    "run_state.html": "status.html",
                    "task_queue.html": "roadmap.html",
                },
            )
            redirected_source_expectations = {
                "council_log.html": "docs/council_log.md",
                "project_status_full.html": "PROJECT_STATUS.md",
                "run_state.html": "RUN_STATE.md",
                "task_queue.html": "TASK_QUEUE.md",
            }
            for source_name, target_name in pack_capsule.CAPSULE_PAGE_REDIRECTS.items():
                target_path = pack_capsule.canonical_path(
                    pack_capsule.page_aliases(site / target_name)
                )
                self.assertIn(
                    redirected_source_expectations[source_name],
                    {
                        stamp["source"]
                        for stamp in pages[target_path]["sources"]
                    },
                )
            capsule_names = expected_names - set(
                pack_capsule.CAPSULE_PAGE_REDIRECTS
            )
            expected_canonical = {
                pack_capsule.canonical_path(pack_capsule.page_aliases(site / name))
                for name in capsule_names
            } | {"/project_critique_review.html"}
            self.assertEqual(set(packed_site["routes"]), expected_canonical)
            for path, route in packed_site["routes"].items():
                self.assertIn(path, decoded_shards[route["shard"]])
                self.assertEqual(
                    route["verbatim"], path == "/advisor_brief.html"
                )
            for name in capsule_names:
                aliases = pack_capsule.page_aliases(site / name)
                aliases.extend(
                    alias
                    for source_name, target_name in pack_capsule.CAPSULE_PAGE_REDIRECTS.items()
                    if target_name == name
                    for alias in pack_capsule.page_aliases(site / source_name)
                )
                canonical = pack_capsule.canonical_path(aliases)
                expected_aliases = [
                    alias
                    for alias in aliases
                    if alias != canonical and alias not in pack_capsule.RESERVED_PATHS
                ]
                self.assertEqual(packed_site["routes"][canonical]["aliases"], expected_aliases)
            self.assertEqual(
                packed_site["routes"]["/project_critique_review.html"]["aliases"],
                ["/critique"],
            )
            expected_sources = {}
            for entry in pages.values():
                for stamp in entry["sources"]:
                    expected_sources[stamp["source"]] = stamp["commit"]
            self.assertEqual(
                packed_site["sources"],
                [{"source": source, "commit": expected_sources[source]} for source in sorted(expected_sources)],
            )
            self.assertEqual(set(decoded_pages), expected_canonical)
            for path, entry in pages.items():
                self.assertEqual(decoded_pages[path], entry["html"])
                if entry["verbatim"]:
                    self.assertEqual(decoded_pages[path], entry["html"])
                else:
                    response_html = decoded_pages[path].replace(
                        "</body>", shared["freshness"] + "\n</body>", 1
                    )
                    self.assertEqual(
                        response_html,
                        pack_capsule.inject_freshness(
                            entry["html"], Path(path).name or "index.html"
                        ),
                    )
            self.assertIn("built docs/site", build_stdout.getvalue())
            if force_offline_renderer:
                self.assertIn("offline fallback markdown renderer", build_stderr.getvalue())
                self.assertTrue(
                    any(
                        "<!-- rendered: offline-fallback -->" in path.read_text(encoding="utf-8")
                        for path in site.glob("*.html")
                    )
                )
            else:
                self.assertNotIn("offline fallback markdown renderer", build_stderr.getvalue())
                for path in site.glob("*.html"):
                    self.assertNotIn(
                        "<!-- rendered: offline-fallback -->",
                        path.read_text(encoding="utf-8"),
                    )
                readme_html = (site / "readme.html").read_text(encoding="utf-8")
                self.assertIn("<h1>JouleWise</h1>", readme_html)
                self.assertIn(
                    '<pre><code class="language-bash">python3 -m unittest discover -s tests',
                    readme_html,
                )
            self.assertIn("postcondition mode: measured", pack_stdout.getvalue())
            self.assertNotIn("estimator-only advisory", pack_stdout.getvalue())
            self.assertEqual(pack_stderr.getvalue(), "")
            estimated_artifact = pack_capsule.estimate_lakebed_artifact_size(total)
            # D-135: retain estimator coverage without turning it into a gate.
            self.assertGreater(estimated_artifact, 0)
            self.assertLessEqual(
                960_030, pack_capsule.LAKEBED_ARTIFACT_CAP_BYTES
            )
            self.assertTrue((content / "pages.ts").is_file())
            self.assertTrue((content / "buildinfo.ts").is_file())
            self.assertFalse((content / "styles.ts").exists())
            manifest = json.loads((site / "build_manifest.json").read_text(encoding="utf-8"))
            expected_mode = "offline-fallback" if force_offline_renderer else "marked"
            self.assertEqual(manifest["renderer"]["mode"], expected_mode)
            self.assertEqual(
                manifest["renderer"]["markedVersion"], build_site.MARKED_VERSION
            )

    @SITE_CONTENT_TESTS
    def test_production_build_output_packs_with_lakebed_size_reporting(self):
        self._assert_production_build_output_packs_with_lakebed_size_reporting(
            force_offline_renderer=True
        )

    @SITE_CONTENT_TESTS
    def test_connected_marked_build_output_packs_with_lakebed_size_reporting(self):
        try:
            executable = build_site.discover_marked_executable()
        except build_site.SiteBuildError as exc:
            self.fail(str(exc))
        if executable is None:
            message = (
                "WO-018 MARKED INTEGRATION GATE SKIP: pinned local Marked "
                "18.0.6 unavailable; run npm ci or set JOULEWISE_MARKED_BIN "
                "to an exact 18.0.6 package binary"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)
        try:
            probe = subprocess.run(
                [str(executable), "--gfm"],
                input="# Probe\n",
                capture_output=True,
                text=True,
                check=True,
                cwd=build_site.ROOT,
                timeout=12,
            )
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            if isinstance(exc, subprocess.CalledProcessError):
                detail = (exc.stderr or "").strip() or f"exit {exc.returncode}"
            else:
                detail = str(exc)
            message = (
                "WO-018 MARKED INTEGRATION GATE SKIP: pinned Marked unavailable "
                f"({detail})"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)
        if "<h1>Probe</h1>" not in probe.stdout:
            message = (
                "WO-018 MARKED INTEGRATION GATE SKIP: pinned Marked unavailable "
                "(probe did not return expected GFM HTML)"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)
        self._assert_production_build_output_packs_with_lakebed_size_reporting(
            force_offline_renderer=False
        )


if __name__ == "__main__":
    unittest.main()
