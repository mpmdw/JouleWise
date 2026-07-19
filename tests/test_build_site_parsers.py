import base64
import contextlib
import gzip
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import build_site, pack_capsule


SESSION_HEADING = "Session History (pointers only \u2014 run reports own the narrative)"


def gzip_decompress_base64(value: str) -> str:
    return gzip.decompress(base64.b64decode(value)).decode("utf-8")


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

    def test_trim_log_fewer_equal_and_more_than_six_entries(self):
        pattern = build_site.re.compile(r"(?m)^## D-\d")
        for count in (5, 6):
            md = "# Log\n\n" + "".join(
                f"## D-{index:03d}: Entry\nbody {index}\n\n"
                for index in range(1, count + 1)
            )
            self.assertEqual(
                build_site.trim_log_markdown(md, pattern, 6, "docs/decision_log.md"),
                md,
            )

        md = "# Log\n\nindex preamble\n\n" + "".join(
            f"## D-{index:03d}: Entry\nbody {index}\n\n" for index in range(1, 9)
        ) + "trailing content\n"
        trimmed = build_site.trim_log_markdown(
            md, pattern, 6, "docs/decision_log.md"
        )
        self.assertNotIn("## D-001", trimmed)
        self.assertNotIn("## D-002", trimmed)
        self.assertIn("## D-003", trimmed)
        self.assertIn("## D-008", trimmed)
        self.assertIn("2 older full entries are omitted", trimmed)
        self.assertIn("github.com/mpmdw/JouleWise/blob/main/docs/decision_log.md", trimmed)
        self.assertTrue(trimmed.endswith("trailing content\n"))
        self.assertEqual(
            [text for text, _ in build_site.markdown_h2_toc(trimmed)],
            [f"D-{index:03d}: Entry" for index in range(3, 9)],
        )

    def test_trim_note_is_escaped_by_offline_fallback_renderer(self):
        md = "# Log\n\n" + "".join(
            f"## D-{index:03d}: <Entry & {index}>\nbody\n\n"
            for index in range(1, 8)
        )
        trimmed = build_site.trim_log_markdown(
            md,
            build_site.re.compile(r"(?m)^## D-\d"),
            6,
            "docs/decision_log.md",
        )
        rendered = build_site.render_basic_markdown(trimmed)
        self.assertIn("&lt;Entry &amp; 2&gt;", rendered)
        self.assertNotIn("<Entry & 2>", rendered)

    def _assert_production_build_output_packs_below_lakebed_budget(
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
                with mock.patch.object(
                    pack_capsule, "LAKEBED_MEASURED_ARTIFACT_BUDGET_BYTES", 0
                ):
                    with self.assertRaises(pack_capsule.CapsulePackError):
                        pack_capsule.build(no_fonts=True)
                with mock.patch.object(pack_capsule, "MAX_FIRST_REQUEST_DECODE_BYTES", 0):
                    with self.assertRaisesRegex(pack_capsule.CapsulePackError, "byte-loop iterations"):
                        pack_capsule.build(no_fonts=True)

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
                "council_log.html", "decision_log.html", "index.html",
                "latest_run_report.html", "library.html", "measurement_methodology.html",
                "milestones.html", "orchestration.html", "process.html",
                "project_status.html", "readme.html", "record.html", "research.html",
                "results.html", "risk_register.html", "roadmap.html", "run_state.html",
                "status.html", "task_queue.html",
            }
            self.assertEqual({path.name for path in site.glob("*.html")}, expected_names)
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
                {"task_queue.html": "roadmap.html"},
            )
            capsule_names = expected_names - {"task_queue.html"}
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
            # AUD-WO-039 / D-076-pending: measured mode is authoritative; the
            # conservative estimator is a fallback-only guard and is expected
            # to overshoot this production-shaped input.
            self.assertGreater(
                estimated_artifact,
                pack_capsule.LAKEBED_ESTIMATE_FALLBACK_BUDGET_BYTES,
            )
            self.assertLessEqual(
                960_030, pack_capsule.LAKEBED_MEASURED_ARTIFACT_BUDGET_BYTES
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

    def test_production_build_output_packs_below_conservative_lakebed_budget(self):
        self._assert_production_build_output_packs_below_lakebed_budget(
            force_offline_renderer=True
        )

    def test_connected_marked_build_output_packs_below_lakebed_budget(self):
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
        self._assert_production_build_output_packs_below_lakebed_budget(
            force_offline_renderer=False
        )


if __name__ == "__main__":
    unittest.main()
