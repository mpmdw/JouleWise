import base64
import contextlib
import gzip
import io
import json
import re
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

from scripts import pack_capsule


TS_STRING_RE = r'"(?:\\.|[^"\\])*"'


def decode_gzip_base64(value):
    return gzip.decompress(base64.b64decode(value)).decode("utf-8")


def decode_ts_string_expression(expression):
    return "".join(json.loads(item) for item in re.findall(TS_STRING_RE, expression))


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
        original = "`tick` ${notTemplate} \\ slash process.html fetch( globalThis self for(;;)"
        emitted = pack_capsule.ts_json_parse(original)
        self.assertTrue(emitted.startswith('"'))
        self.assertNotIn("JSON.parse", emitted)
        self.assertIn("\\u0024{notTemplate}", emitted)
        self.assertIn("\\u0060tick\\u0060", emitted)
        self.assertEqual(pack_capsule.VALIDATOR_TOKENS, ("process", "fetch", "globalThis", "self"))
        for token in ("process", "fetch", "globalThis", "self"):
            self.assertNotIn(token, emitted)
        self.assertNotIn("for(;;)", emitted)
        self.assertIn("\\u0070rocess.html", emitted)
        self.assertIn("\\u0066etch(", emitted)
        self.assertEqual(json.loads(emitted), original)

    def test_chunked_string_roundtrips_while_breaking_validator_text(self):
        original = "start-process-fetch-globalThis-self-for(;;)-end"
        emitted = pack_capsule.chunk_ts_string(original, width=8)
        literals = re.findall(r'"(?:\\.|[^"\\])*"', emitted)
        self.assertGreater(len(literals), 1)
        self.assertEqual("".join(json.loads(item) for item in literals), original)
        for token in ("process", "fetch", "globalThis", "self"):
            self.assertNotIn(token, emitted)
        self.assertNotIn("for(;;)", emitted)

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
        self.assertNotIn("/api/freshness", entry["html"])
        rendered = pack_capsule.inject_freshness(entry["html"], "project_critique_review.html")
        self.assertIn("fetch(\"/api/freshness\")", rendered)
        self.assertIn("</body>", entry["html"])

    def test_emit_site_exports_bounded_shards_with_routes_and_sources(self):
        class Sink:
            text = ""

            def write_text(self, text, encoding):
                self.text = text

        original = "<html><body>`tick` ${notTemplate} process.html fetch(</body></html>"
        css = "body{color:#111}"
        pages = {
            "/process-fetch.html": {
                "html": original,
                "sources": [{"source": "docs/process-fetch.md", "commit": "2254570"}],
                "aliases": ["/process-fetch"],
            }
        }
        sink = Sink()
        stats = pack_capsule.emit_site(pages, css, sink)
        site, expected_stats = pack_capsule.encode_site(pages, css)

        shared_expr = sink.text.split("  shared: ", 1)[1].split(",\n  shards:", 1)[0]
        emitted_shared = decode_ts_string_expression(shared_expr)
        shard_block = sink.text.split("  shards: [\n", 1)[1].split("  ],\n  routes:", 1)[0]
        expression_re = re.compile(rf"    (?P<expr>{TS_STRING_RE}|\((?:{TS_STRING_RE})(?: \+\n    {TS_STRING_RE})*\)),\n")
        emitted_shards = [decode_ts_string_expression(match.group("expr")) for match in expression_re.finditer(shard_block)]
        routes_expr = sink.text.split("  routes: ", 1)[1].split(",\n  sources:", 1)[0]
        sources_expr = sink.text.split("  sources: ", 1)[1].split(",\n};", 1)[0]
        self.assertEqual(emitted_shared, site["shared"])
        self.assertEqual(emitted_shards, site["shards"])
        self.assertEqual(json.loads(routes_expr), site["routes"])
        self.assertEqual(json.loads(sources_expr), site["sources"])

        shared = json.loads(decode_gzip_base64(emitted_shared))
        decoded_pages = {}
        for shard in emitted_shards:
            decoded_pages.update(json.loads(decode_gzip_base64(shard)))
        self.assertEqual(decoded_pages, {"/process-fetch.html": original})
        self.assertEqual(shared["style"], css)
        self.assertEqual(shared["freshness"], pack_capsule.FRESHNESS_STYLE + "\n" + pack_capsule.FRESHNESS_SCRIPT)
        reconstructed = decoded_pages["/process-fetch.html"].replace(
            "</body>", shared["freshness"] + "\n</body>", 1
        )
        self.assertEqual(reconstructed, pack_capsule.inject_freshness(original, "process-fetch.html"))
        self.assertEqual(stats["base64"], expected_stats["base64"])
        self.assertEqual(stats["shards"], 1)
        self.assertLessEqual(stats["max_shard"], pack_capsule.MAX_SHARD_BASE64_BYTES)
        self.assertLessEqual(stats["first_request_decode"], pack_capsule.MAX_FIRST_REQUEST_DECODE_BYTES)
        self.assertEqual(sink.text.count("\n  shared:"), 1)
        self.assertEqual(sink.text.count("/api/freshness"), 0)
        self.assertIn("export const PACKED_SITE", sink.text)
        self.assertNotIn("JSON.parse", sink.text)
        for token in ("process", "fetch", "globalThis", "self"):
            self.assertNotIn(token, sink.text)
        self.assertNotIn("for(;;)", sink.text)
        self.assertIn("/\\u0070rocess-\\u0066etch.html", sink.text)
        self.assertIn("docs/\\u0070rocess-\\u0066etch.md", sink.text)

    def test_real_server_decoder_roundtrips_emitted_shard_and_rejects_corruption(self):
        node = shutil.which("node")
        if node is None:
            message = (
                "SITE-01 NODE DECODE GATE SKIP: compatible node/tsx runtime "
                "unavailable (node executable not found)"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)
        try:
            probe = subprocess.run(
                [
                    node,
                    "-e",
                    "const names=['atob','btoa','ReadableStream','DecompressionStream','TextDecoder'];"
                    "const missing=names.filter((name)=>typeof globalThis[name]==='undefined');"
                    "if(missing.length){console.error(missing.join(','));process.exit(2);}",
                ],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            message = (
                "SITE-01 NODE DECODE GATE SKIP: compatible node/tsx runtime "
                f"unavailable ({exc})"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)
        if probe.returncode != 0:
            reason = probe.stderr.strip() or f"probe exit {probe.returncode}"
            message = (
                "SITE-01 NODE DECODE GATE SKIP: compatible node/tsx runtime "
                f"unavailable (missing required web APIs: {reason})"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)

        known_html = "<!doctype html><html><body>Known UTF-8 page: π ⚡</body></html>"
        pages = {
            "/known.html": {
                "html": known_html,
                "sources": [],
                "aliases": ["/known"],
            }
        }
        with TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            pages_path = temp_path / "pages.ts"
            harness_path = temp_path / "decode-harness.mjs"
            pack_capsule.emit_site(pages, "body{color:#111}", pages_path)

            module_source = pages_path.read_text(encoding="utf-8")
            module_source, type_count = re.subn(
                r"^export type [^\n]+\n", "", module_source, flags=re.MULTILINE
            )
            self.assertEqual(type_count, 3)
            binding_count = module_source.count("export const PACKED_SITE: PackedSite =")
            module_source = module_source.replace(
                "export const PACKED_SITE: PackedSite =",
                "const PACKED_SITE =",
            )
            self.assertEqual(binding_count, 1)

            server_source = (pack_capsule.CAPSULE / "server" / "index.ts").read_text(
                encoding="utf-8"
            )
            decoder_start = server_source.index("function base64ToBytes")
            decoder_end = server_source.index("\nlet decodedShared", decoder_start)
            decoder_source = server_source[decoder_start:decoder_end]
            cache_match = re.search(
                r"^const decodedShards = .+;$", server_source, flags=re.MULTILINE
            )
            self.assertIsNotNone(cache_match)
            load_shard_start = server_source.index("async function loadShard")
            load_shard_end = server_source.index(
                "\nfunction pageWithFreshness", load_shard_start
            )
            shard_source = (
                cache_match.group(0)
                + "\n"
                + server_source[load_shard_start:load_shard_end]
            )
            replacements = {
                "(value: string): Uint8Array": "(value)",
                "(value: string): Promise<string>": "(value)",
                "new ReadableStream<Uint8Array>": "new ReadableStream",
                "const chunks: Uint8Array[] = []": "const chunks = []",
            }
            for typed, javascript in replacements.items():
                self.assertEqual(decoder_source.count(typed), 1)
                decoder_source = decoder_source.replace(typed, javascript)
            shard_replacements = {
                "const decodedShards = new Map<number, Promise<Record<string, string>>>();":
                    "const decodedShards = new Map();",
                "(index: number): Promise<Record<string, string>>": "(index)",
                " as Record<string, unknown>": "",
                " as Record<string, string>": "",
            }
            for typed, javascript in shard_replacements.items():
                self.assertEqual(shard_source.count(typed), 1)
                shard_source = shard_source.replace(typed, javascript)

            harness = (
                module_source
                + "\nconst SITE = PACKED_SITE;\n"
                + decoder_source
                + "\n"
                + shard_source
                + r'''
const route = PACKED_SITE.routes["/known.html"];
if (!route) throw new Error("known route missing from emitted module");
const encoded = PACKED_SITE.shards[route.shard];
const decoded = await loadShard(route.shard);
const page = decoded["/known.html"];
if (typeof page !== "string") throw new Error("known page missing after decode");

const corruptBytes = Uint8Array.from(atob(encoded), (character) => character.charCodeAt(0));
corruptBytes[0] ^= 0xff;
let corruptBinary = "";
for (const byte of corruptBytes) corruptBinary += String.fromCharCode(byte);
SITE.shards[route.shard] = btoa(corruptBinary);
decodedShards.clear();
let corruptRaised = false;
try {
  await loadShard(route.shard);
} catch (error) {
  corruptRaised = true;
}
if (!corruptRaised) throw new Error("corrupted shard decoded without error");
if (decodedShards.has(route.shard)) throw new Error("failed shard remained cached");
console.log(JSON.stringify({
  pageBase64: Buffer.from(page, "utf8").toString("base64"),
  corruptRaised,
}));
'''
            )
            harness_path.write_text(harness, encoding="utf-8")
            completed = subprocess.run(
                [node, str(harness_path)],
                capture_output=True,
                text=True,
                check=False,
                timeout=20,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(
            result["pageBase64"],
            base64.b64encode(known_html.encode("utf-8")).decode("ascii"),
        )
        self.assertTrue(result["corruptRaised"])

    def test_page_shard_refuses_an_individually_oversized_page(self):
        pages = {
            "/large": {
                "html": "".join(chr(33 + (index * 37) % 90) for index in range(80_000)),
                "sources": [],
                "aliases": [],
            }
        }
        with mock.patch.object(pack_capsule, "MAX_SHARD_BASE64_BYTES", 100):
            with self.assertRaisesRegex(pack_capsule.CapsulePackError, "split the page"):
                pack_capsule.page_shards(pages)

    def test_runtime_decode_budget_fails_closed(self):
        pack_capsule.enforce_runtime_decode_budget(
            {"first_request_decode": pack_capsule.MAX_FIRST_REQUEST_DECODE_BYTES}
        )
        with self.assertRaisesRegex(pack_capsule.CapsulePackError, "byte-loop iterations"):
            pack_capsule.enforce_runtime_decode_budget(
                {"first_request_decode": pack_capsule.MAX_FIRST_REQUEST_DECODE_BYTES + 1}
            )

    def test_shared_sources_deduplicates_and_rejects_conflicting_commits(self):
        pages = {
            "/one": {"html": "one", "sources": [{"source": "A.md", "commit": "abc"}], "aliases": []},
            "/two": {"html": "two", "sources": [{"source": "A.md", "commit": "abc"}], "aliases": []},
        }
        self.assertEqual(pack_capsule.shared_sources(pages), [{"source": "A.md", "commit": "abc"}])
        pages["/two"]["sources"][0]["commit"] = "def"
        with self.assertRaises(pack_capsule.CapsulePackError):
            pack_capsule.shared_sources(pages)

    def test_lakebed_estimate_enforces_exact_conservative_boundary(self):
        self.assertLessEqual(
            pack_capsule.LAKEBED_TARGET_ARTIFACT_BYTES,
            int(pack_capsule.LAKEBED_ARTIFACT_CAP_BYTES * 0.9),
        )
        self.assertGreaterEqual(
            pack_capsule.LAKEBED_BASE_WRAPPER_BUDGET_BYTES,
            pack_capsule.LAKEBED_MEASURED_BASE_WRAPPER_BYTES,
        )
        self.assertGreaterEqual(
            pack_capsule.LAKEBED_METADATA_BUDGET_BYTES,
            pack_capsule.LAKEBED_MEASURED_METADATA_BYTES,
        )
        maximum_content = 0
        for candidate in range(200_000, 300_000):
            if pack_capsule.estimate_lakebed_artifact_size(candidate) <= pack_capsule.LAKEBED_TARGET_ARTIFACT_BYTES:
                maximum_content = candidate
        estimate = pack_capsule.enforce_lakebed_budget(maximum_content)
        self.assertLessEqual(estimate, pack_capsule.LAKEBED_TARGET_ARTIFACT_BYTES)
        with self.assertRaisesRegex(pack_capsule.CapsulePackError, "at least 10% margin"):
            pack_capsule.enforce_lakebed_budget(maximum_content + 1)

    def test_estimator_only_postcondition_is_clearly_advisory(self):
        stdout = io.StringIO()
        content_size = 200_000
        with (
            mock.patch.object(pack_capsule, "discover_lakebed_executable", return_value=None),
            contextlib.redirect_stdout(stdout),
        ):
            observed = pack_capsule.enforce_lakebed_artifact_postcondition(content_size)
        self.assertEqual(observed, pack_capsule.estimate_lakebed_artifact_size(content_size))
        self.assertIn("postcondition mode: estimator-only advisory", stdout.getvalue())
        self.assertIn("Lakebed executable unavailable", stdout.getvalue())

    def test_discovered_lakebed_build_failure_does_not_fall_back_to_estimator(self):
        stdout = io.StringIO()
        executable = Path("/cached/lakebed")
        with (
            mock.patch.object(
                pack_capsule,
                "discover_lakebed_executable",
                return_value=executable,
            ),
            mock.patch.object(
                pack_capsule,
                "measure_lakebed_artifact",
                side_effect=pack_capsule.CapsulePackError("real build failed"),
            ),
            contextlib.redirect_stdout(stdout),
            self.assertRaisesRegex(pack_capsule.CapsulePackError, "real build failed"),
        ):
            pack_capsule.enforce_lakebed_artifact_postcondition(200_000)
        self.assertIn("postcondition mode: measured", stdout.getvalue())
        self.assertNotIn("estimator-only advisory", stdout.getvalue())

    def test_measured_postcondition_catches_large_unestimated_server_payload(self):
        executable = pack_capsule.discover_lakebed_executable()
        if executable is None:
            message = (
                "SITE-01 LAKEBED MEASUREMENT GATE SKIP: cached Lakebed executable "
                "unavailable; real validator artifact was not built"
            )
            print(message, file=sys.stderr)
            self.skipTest(message)

        with TemporaryDirectory() as temp_dir:
            capsule = Path(temp_dir) / "capsule"
            shutil.copytree(
                pack_capsule.CAPSULE,
                capsule,
                ignore=shutil.ignore_patterns(".lakebed"),
            )
            content = capsule / "server" / "content"
            with (
                mock.patch.object(pack_capsule, "CAPSULE", capsule),
                mock.patch.object(pack_capsule, "CAPSULE_CONTENT", content),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                total = pack_capsule.build(no_fonts=True, enforce_budget=False)

            # Reconstruct the reviewed lens's freshly-rendered content size.
            # The tracked docs/site snapshot is slightly smaller, while the
            # omitted server/index.ts payload is identical in either case.
            lens_content_size = 246_302
            self.assertLess(total, lens_content_size)
            padding_size = lens_content_size - total
            pages_path = content / "pages.ts"
            pages_source = pages_path.read_text(encoding="utf-8")
            shared_prefix = '  shared: ("'
            self.assertEqual(pages_source.count(shared_prefix), 1)
            pages_path.write_text(
                pages_source.replace(
                    shared_prefix,
                    shared_prefix + "x" * padding_size,
                    1,
                ),
                encoding="utf-8",
            )
            total = pack_capsule.packed_size(
                [content / "pages.ts", content / "buildinfo.ts"]
            )
            self.assertEqual(total, lens_content_size)
            estimate = pack_capsule.estimate_lakebed_artifact_size(total)
            self.assertEqual(estimate, 937_984)
            self.assertLessEqual(estimate, pack_capsule.LAKEBED_TARGET_ARTIFACT_BYTES)
            index_path = capsule / "server" / "index.ts"
            with index_path.open("a", encoding="utf-8") as stream:
                stream.write("\n//" + "x" * (105_000 - 3))
            self.assertEqual(
                pack_capsule.packed_size(
                    [content / "pages.ts", content / "buildinfo.ts"]
                ),
                total,
            )
            self.assertEqual(pack_capsule.estimate_lakebed_artifact_size(total), estimate)

            stdout = io.StringIO()
            with (
                mock.patch.object(
                    pack_capsule,
                    "discover_lakebed_executable",
                    return_value=executable,
                ),
                contextlib.redirect_stdout(stdout),
                self.assertRaisesRegex(
                    pack_capsule.CapsulePackError,
                    "measured Lakebed validator artifact.*over the 1 MiB cap",
                ),
            ):
                pack_capsule.enforce_lakebed_artifact_postcondition(total, capsule)

        output = stdout.getvalue()
        self.assertIn("postcondition mode: measured", output)
        match = re.search(r"measured Lakebed validator artifact: (\d+) bytes", output)
        self.assertIsNotNone(match)
        self.assertGreater(int(match.group(1)), pack_capsule.LAKEBED_ARTIFACT_CAP_BYTES)

    def test_lakebed_source_discovery_scans_unimported_server_helper(self):
        with TemporaryDirectory() as temp_dir:
            capsule = Path(temp_dir) / "capsule"
            server = capsule / "server"
            shared = capsule / "shared"
            server.mkdir(parents=True)
            shared.mkdir()
            (server / "index.ts").write_text("export default {};", encoding="utf-8")
            helper = server / "helper.ts"
            helper.write_text('export const rejected = "fetch";', encoding="utf-8")
            (shared / "safe.ts").write_text("export const safe = 1;", encoding="utf-8")

            paths = pack_capsule.lakebed_source_paths(capsule)
            self.assertEqual(
                [str(path.relative_to(capsule)) for path in paths],
                ["server/helper.ts", "server/index.ts", "shared/safe.ts"],
            )
            pages = {
                "/known.html": {
                    "html": "<!doctype html><html><body>known</body></html>",
                    "sources": [],
                    "aliases": [],
                }
            }
            with (
                mock.patch.object(pack_capsule, "CAPSULE", capsule),
                mock.patch.object(
                    pack_capsule,
                    "CAPSULE_CONTENT",
                    capsule / "server" / "content",
                ),
                mock.patch.object(pack_capsule, "pack_pages", return_value=pages),
                mock.patch.object(pack_capsule, "stylesheet", return_value="body{}"),
                mock.patch.object(
                    pack_capsule,
                    "build_info",
                    return_value={
                        "commit": "abc1234",
                        "branch": "test",
                        "builtAt": "2026-07-11T00:00:00Z",
                    },
                ),
                contextlib.redirect_stdout(io.StringIO()),
                self.assertRaisesRegex(
                    pack_capsule.CapsulePackError,
                    r"server/helper\.ts: Lakebed validator token remains: fetch",
                ),
            ):
                pack_capsule.build(no_fonts=True, enforce_budget=False)

    def test_lakebed_source_scan_rejects_textual_tokens_and_unbounded_loop(self):
        with TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "module.ts"
            for token in ["process", "fetch", "globalThis", "self"]:
                with self.subTest(token=token):
                    source.write_text(f"const value = {json.dumps(token)};", encoding="utf-8")
                    with self.assertRaises(pack_capsule.CapsulePackError):
                        pack_capsule.validate_lakebed_sources([source])
            rejected_loops = {
                "omitted_initializer": "for (; i < 10; i += 1) {}",
                "omitted_condition_after_omitted_initializer": "for (; ; i += 1) {}",
                "omitted_all": "for (;;) {}",
            }
            for variant, loop in rejected_loops.items():
                with self.subTest(variant=variant):
                    source.write_text(loop, encoding="utf-8")
                    with self.assertRaisesRegex(
                        pack_capsule.CapsulePackError, "unbounded for-loop remains"
                    ):
                        pack_capsule.validate_lakebed_sources([source])
            accepted_loops = {
                # Lakebed 0.0.25's textual rule checks only an omitted initializer.
                "omitted_condition_only": "for (let i = 0; ; i += 1) { break; }",
                "bounded": "for (let i = 0; i < 2; i += 1) {}",
            }
            for variant, loop in accepted_loops.items():
                with self.subTest(variant=variant):
                    source.write_text('const value = "f\\u0065tch";\n' + loop, encoding="utf-8")
                    pack_capsule.validate_lakebed_sources([source])

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
        self.assertIn("for (const alias of [path, ...route.aliases])", server)
        self.assertIn("if (RESERVED_PATHS.has(alias)) continue;", server)

    def test_server_decodes_bounded_shards_and_reinserts_shared_freshness(self):
        server = (pack_capsule.ROOT / "site_capsule" / "server" / "index.ts").read_text(encoding="utf-8")
        self.assertIn("const SITE = PACKED_SITE;", server)
        self.assertIn("function base64ToBytes", server)
        self.assertIn("async function loadShared", server)
        self.assertIn("async function loadShard", server)
        self.assertIn("function pageWithFreshness", server)
        self.assertIn("loadShard(route.shard)", server)
        for token in ("process", "fetch", "globalThis", "self"):
            self.assertNotIn(token, server)
        self.assertIsNone(pack_capsule.UNBOUNDED_FOR_RE.search(server))

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
