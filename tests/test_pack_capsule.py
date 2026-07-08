import base64
import gzip
import json
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts import pack_capsule


def decode_gzip_base64(value):
    return gzip.decompress(base64.b64decode(value)).decode("utf-8")


class PackCapsuleTests(unittest.TestCase):
    def test_extracts_source_chip_stamps_once(self):
        page = (
            '<span class="source-chip" title="docs/contracts/adapter_contracts.md · commit 2254570">'
            '<span class="source-file">docs/<wbr>contracts/<wbr>adapter_contracts.md</span>'
            '<span class="source-commit">commit 2254570</span></span>'
            '<span class="source-chip" title="docs/contracts/adapter_contracts.md · commit 2254570"></span>'
            '<span class="source-chip" title="TASK_QUEUE.md · commit 4af29a9 + uncommitted"></span>'
        )
        self.assertEqual(
            pack_capsule.extract_stamps("status.html", page),
            [
                {"source": "docs/contracts/adapter_contracts.md", "commit": "2254570"},
                {"source": "TASK_QUEUE.md", "commit": "4af29a9"},
            ],
        )

    def test_string_emission_escapes_template_and_validator_tokens(self):
        emitted = pack_capsule.ts_json_parse("`tick` ${notTemplate} \\ slash process.html fetch(")
        self.assertTrue(emitted.startswith('"'))
        self.assertNotIn("JSON.parse", emitted)
        self.assertIn("\\u0024{notTemplate}", emitted)
        self.assertIn("\\u0060tick\\u0060", emitted)
        self.assertNotIn("process", emitted)
        self.assertNotIn("fetch", emitted)
        self.assertIn("proc\\u0065ss.html", emitted)
        self.assertIn("f\\u0065tch(", emitted)
        self.assertEqual(json.loads(emitted), "`tick` ${notTemplate} \\ slash process.html fetch(")

    def test_alias_generation_includes_clean_and_root_index(self):
        self.assertEqual(
            pack_capsule.page_aliases(pack_capsule.SITE / "index.html"),
            ["/", "/index.html", "/index"],
        )
        self.assertEqual(
            pack_capsule.page_aliases(pack_capsule.SITE / "status.html"),
            ["/status.html", "/status"],
        )

    def test_pack_pages_uses_one_canonical_key_and_non_reserved_aliases(self):
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            index_path = temp_path / "index.html"
            status_path = temp_path / "status.html"
            index_path.write_text(
                '<!doctype html><html><head><link rel="stylesheet" href="style.css"></head>'
                "<body>Index</body></html>",
                encoding="utf-8",
            )
            status_path.write_text(
                '<!doctype html><html><head><link rel="stylesheet" href="style.css"></head>'
                '<body><span class="source-chip" title="TASK_QUEUE.md · commit 4af29a9"></span></body></html>',
                encoding="utf-8",
            )
            specs = [
                pack_capsule.PageSpec(
                    path=index_path,
                    page_name="index.html",
                    aliases=pack_capsule.page_aliases(index_path),
                ),
                pack_capsule.PageSpec(
                    path=status_path,
                    page_name="status.html",
                    aliases=pack_capsule.page_aliases(status_path),
                ),
            ]
            original_specs = pack_capsule.site_page_specs
            try:
                pack_capsule.site_page_specs = lambda: specs
                pages = pack_capsule.pack_pages()
            finally:
                pack_capsule.site_page_specs = original_specs

        self.assertEqual(sorted(pages), ["/index", "/status.html"])
        self.assertEqual(pages["/index"]["aliases"], [])
        self.assertEqual(pages["/status.html"]["aliases"], ["/status"])
        all_aliases = [alias for entry in pages.values() for alias in entry["aliases"]]
        self.assertNotIn("/", pages)
        self.assertNotIn("/index.html", pages)
        self.assertNotIn("/", all_aliases)
        self.assertNotIn("/index.html", all_aliases)

    def test_known_hand_page_can_have_no_stamp(self):
        self.assertEqual(pack_capsule.extract_stamps("index.html", "<html></html>"), [])

    def test_standalone_critique_page_can_have_no_stamp(self):
        self.assertEqual(pack_capsule.extract_stamps("project_critique_review.html", "<html></html>"), [])

    def test_generated_page_without_stamp_fails_closed(self):
        with self.assertRaises(pack_capsule.CapsulePackError):
            pack_capsule.extract_stamps("status.html", "<html></html>")

    def test_rewrites_internal_hrefs_preserving_anchors(self):
        html = (
            '<a href="index.html">Story</a>'
            '<a href="index.html#methods">Methods</a>'
            '<a href="../project_critique_review.html">Critique</a>'
            '<a href="../project_critique_review.html#evidence">Critique evidence</a>'
            '<a href="status.html">Status</a>'
            "<a href='index.html#single'>Single</a>"
        )
        rewritten = pack_capsule.rewrite_internal_hrefs(html)
        self.assertIn('href="/index"', rewritten)
        self.assertIn('href="/index#methods"', rewritten)
        self.assertIn('href="/project_critique_review.html"', rewritten)
        self.assertIn('href="/project_critique_review.html#evidence"', rewritten)
        self.assertIn('href="status.html"', rewritten)
        self.assertIn("href='/index#single'", rewritten)
        self.assertNotIn('href="index.html"', rewritten)
        self.assertNotIn('href="../project_critique_review.html"', rewritten)

    def test_rewrites_stylesheet_link_to_absolute_href(self):
        html = '<head><link rel="stylesheet" href="style.css">\n</head><body></body>'
        rewritten = pack_capsule.rewrite_stylesheet_link(html, "status.html")
        self.assertIn('<link rel="stylesheet" href="/style.css">', rewritten)
        self.assertNotIn("<style>", rewritten)

    def test_rewrite_stylesheet_link_fails_closed(self):
        with self.assertRaises(pack_capsule.CapsulePackError):
            pack_capsule.rewrite_stylesheet_link("<head></head>", "status.html")

    def test_critique_standalone_page_is_configured_with_aliases(self):
        critique_specs = [
            spec for spec in pack_capsule.STANDALONE_PAGES if spec.page_name == "project_critique_review.html"
        ]
        self.assertEqual(len(critique_specs), 1)
        critique = critique_specs[0]
        self.assertEqual(critique.path, pack_capsule.ROOT / "docs" / "project_critique_review.html")
        self.assertEqual(critique.aliases, ["/project_critique_review.html", "/critique"])
        self.assertFalse(critique.require_stylesheet)
        self.assertTrue(critique.allow_no_stamps)

    def test_packs_standalone_critique_without_stylesheet_link_or_stamps(self):
        with TemporaryDirectory() as temp_dir:
            original = (
                '<!doctype html><html><head><style>body{color:#111}</style></head>'
                '<body><a href="../project_critique_review.html#top">Critique</a></body></html>'
            )
            page_path = Path(temp_dir) / "project_critique_review.html"
            page_path.write_text(original, encoding="utf-8")
            entry = pack_capsule.pack_page(
                pack_capsule.PageSpec(
                    path=page_path,
                    page_name="project_critique_review.html",
                    aliases=["/project_critique_review.html", "/critique"],
                    require_stylesheet=False,
                    allow_no_stamps=True,
                )
            )
        self.assertEqual(entry["sources"], [])
        self.assertIn('href="/project_critique_review.html#top"', entry["html"])
        self.assertIn("fetch(\"/api/freshness\")", entry["html"])
        self.assertIn("</body>", entry["html"])

    def test_emit_pages_exports_gzip_payload_once_with_aliases_and_escaped_metadata(self):
        class Sink:
            text = ""

            def write_text(self, text, encoding):
                self.text = text

        original = "<html><body>`tick` ${notTemplate} process.html fetch(</body></html>"
        sink = Sink()
        pack_capsule.emit_pages(
            {
                "/process-fetch.html": {
                    "html": original,
                    "sources": [{"source": "docs/process-fetch.md", "commit": "2254570"}],
                    "aliases": ["/process-fetch"],
                }
            },
            sink,
        )
        match = re.search(r'gz: "([^"]+)"', sink.text)
        self.assertIsNotNone(match)
        self.assertEqual(decode_gzip_base64(match.group(1)), original)
        self.assertEqual(sink.text.count(match.group(1)), 1)
        self.assertIn('aliases: ["/proc\\u0065ss-f\\u0065tch"]', sink.text)
        emitted_without_payload = re.sub(r'gz: "[^"]+"', 'gz: ""', sink.text)
        self.assertNotIn("process", emitted_without_payload)
        self.assertNotIn("fetch", emitted_without_payload)
        self.assertIn("/proc\\u0065ss-f\\u0065tch.html", emitted_without_payload)
        self.assertIn("docs/proc\\u0065ss-f\\u0065tch.md", emitted_without_payload)

    def test_emit_styles_module_exports_css_once(self):
        class Sink:
            text = ""

            def write_text(self, text, encoding):
                self.text = text

        sink = Sink()
        original = "body{font-family:${notTemplate};}`"
        pack_capsule.emit_styles(original, sink)
        self.assertIn('export const STYLE_CSS_GZ: string = "', sink.text)
        self.assertNotIn("JSON.parse", sink.text)
        match = re.search(r'STYLE_CSS_GZ: string = "([^"]+)";', sink.text)
        self.assertIsNotNone(match)
        self.assertEqual(decode_gzip_base64(match.group(1)), original)

    def test_inline_fonts_merges_identical_family_and_file_hash(self):
        with TemporaryDirectory() as temp_dir:
            fonts_dir = Path(temp_dir)
            (fonts_dir / "Example-400.woff2").write_bytes(b"same-font")
            (fonts_dir / "Example-600.woff2").write_bytes(b"same-font")
            css = """
@font-face {
  font-family: 'Example';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url(Example-400.woff2) format('woff2');
}
@font-face {
  font-family: 'Example';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url(Example-600.woff2) format('woff2');
}
"""
            inlined = pack_capsule.inline_fonts(css, fonts_dir)

        self.assertEqual(inlined.count("@font-face"), 1)
        self.assertIn("font-weight: 400 600;", inlined)
        self.assertEqual(inlined.count("data:font/woff2;base64,"), 1)
        self.assertEqual(inlined.count(base64.b64encode(b"same-font").decode("ascii")), 1)

    def test_inline_fonts_keeps_distinct_files_separate(self):
        with TemporaryDirectory() as temp_dir:
            fonts_dir = Path(temp_dir)
            (fonts_dir / "Example-400.woff2").write_bytes(b"regular-font")
            (fonts_dir / "Example-600.woff2").write_bytes(b"bold-font")
            css = """
@font-face {
  font-family: 'Example';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url(Example-400.woff2) format('woff2');
}
@font-face {
  font-family: 'Example';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url(Example-600.woff2) format('woff2');
}
"""
            inlined = pack_capsule.inline_fonts(css, fonts_dir)

        self.assertEqual(inlined.count("@font-face"), 2)
        self.assertIn("font-weight: 400;", inlined)
        self.assertIn("font-weight: 600;", inlined)
        self.assertEqual(inlined.count("data:font/woff2;base64,"), 2)

    def test_inline_fonts_fails_closed_on_malformed_block(self):
        with TemporaryDirectory() as temp_dir:
            fonts_dir = Path(temp_dir)
            (fonts_dir / "Example-400.woff2").write_bytes(b"font-data")
            css = """
@font-face {
  font-family: 'Example';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url(Example-400.woff2);
}
"""
            with self.assertRaises(pack_capsule.CapsulePackError):
                pack_capsule.inline_fonts(css, fonts_dir)

    def test_freshness_injection_only_marks_checked_moved_sources(self):
        script = pack_capsule.FRESHNESS_SCRIPT
        self.assertIn("if(!data||!Array.isArray(data.sources)){return;}", script)
        self.assertIn("item&&item.checked&&item.moved&&item.source", script)
        self.assertNotIn("!data.moved", script)

    def test_server_keeps_reserved_path_exclusion_when_registering_aliases(self):
        server = (pack_capsule.ROOT / "site_capsule" / "server" / "index.ts").read_text(encoding="utf-8")
        self.assertIn('const RESERVED_PATHS = new Set(["/", "/index.html"]);', server)
        self.assertIn("for (const route of [path, ...page.aliases])", server)
        self.assertIn("if (RESERVED_PATHS.has(route)) continue;", server)

    def test_server_freshness_contract_is_observation_based_and_fail_soft(self):
        server = (pack_capsule.ROOT / "site_capsule" / "server" / "index.ts").read_text(encoding="utf-8")
        self.assertIn("live: string | null;", server)
        self.assertIn("checked: boolean;", server)
        self.assertIn("checkedAt: string | null;", server)
        self.assertIn("moved: Boolean(checked && live !== baked)", server)
        self.assertIn("const unchecked = sources.filter((source) => !source.checked).length;", server)
        self.assertIn("return softFreshness(checkedAt, rateLimited);", server)
        self.assertIn("return json(softFreshness(new Date().toISOString()));", server)
        self.assertIn('throw new Error("gzip decode read bound reached");', server)


if __name__ == "__main__":
    unittest.main()
