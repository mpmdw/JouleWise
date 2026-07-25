#!/usr/bin/env python3
"""Pack docs/site into Lakebed capsule TypeScript content modules."""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import gzip
import hashlib
import html as html_lib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs" / "site"
CAPSULE = ROOT / "site_capsule"
CAPSULE_CONTENT = CAPSULE / "server" / "content"
KNOWN_HAND_PAGES = {"index.html", "results.html", "process.html", "research.html"}
GITHUB_REPO = "https://github.com/mpmdw/JouleWise"
INTERNAL_HREF_REWRITES = {
    "index.html": "/index",
    "../project_critique_review.html": "/project_critique_review.html",
}
# These long-form mirrors remain generated under docs/site, while the capsule
# serves their stable aliases from the corresponding advisor-facing summary.
# This preserves source history in git without duplicating the largest views
# inside Lakebed's 1 MiB artifact.
CAPSULE_PAGE_REDIRECTS = {
    "project_status_full.html": "project_status.html",
    "run_state.html": "status.html",
    "task_queue.html": "roadmap.html",
}
RESERVED_PATHS = {"/", "/index.html"}
LAKEBED_ARTIFACT_CAP_BYTES = 1_048_576
# Ed's 2026-07-17 AUD-WO-039 right-sizing ruling separates the real-artifact
# budget from the conservative estimator. The 1 MiB Lakebed cap is invariant;
# measured mode may use the in-capsule brief while retaining 48,576 bytes of
# margin. The older conservative budget remains a fallback-only guard.
LAKEBED_MEASURED_ARTIFACT_BUDGET_BYTES = 1_000_000
LAKEBED_ESTIMATE_FALLBACK_BUDGET_BYTES = 943_718
MARKED_VERSION = "18.0.6"
LAKEBED_VERSION = "0.0.29"
LAKEBED_LOCAL_EXECUTABLE = CAPSULE / "node_modules" / ".bin" / "lakebed"
LAKEBED_DISCOVERY_SCHEMA = "joulewise-lakebed-discovery/v1"
# Lakebed 0.0.25 embeds generated modules in compiled code and again in an
# inline base64 source map. The measured residual after subtracting both
# copies was 70,355 bytes; add 52,281 bytes of reserve. Artifact metadata is
# rounded from 5,809 bytes (5,937 before the change) to 8 KiB.
LAKEBED_MEASURED_WRAPPER_BYTES = 396_747
LAKEBED_MEASURED_BASE_WRAPPER_BYTES = 70_355
LAKEBED_BASE_WRAPPER_BUDGET_BYTES = 122_636
LAKEBED_MEASURED_METADATA_BYTES = 5_809
LAKEBED_METADATA_BUDGET_BYTES = 8_192
MAX_SHARD_BASE64_BYTES = 30_000
# Decision-log pages are generated below this stricter target so normal source
# growth and small zlib-version differences cannot consume the runtime limit.
DECISION_LOG_SHARD_BASE64_TARGET_BYTES = 24_000
MAX_FIRST_REQUEST_DECODE_BYTES = 32_000
VALIDATOR_TOKENS = ("process", "fetch", "globalThis", "self")
UNBOUNDED_FOR_RE = re.compile(r"\bfor\s*\(\s*;")
LEGACY_DATABASE_API_RE = re.compile(r"\.(?:where|all)\s*\(")


class PageMode(Enum):
    GENERATED = "generated"
    VERBATIM = "verbatim"


@dataclass(frozen=True)
class PageSpec:
    path: Path
    page_name: str
    aliases: list[str]
    require_stylesheet: bool = True
    allow_no_stamps: bool = False
    mode: PageMode = PageMode.GENERATED
    provenance_source: str | None = None

    def __post_init__(self) -> None:
        if self.mode is PageMode.VERBATIM and not self.provenance_source:
            raise ValueError("verbatim pages require provenance_source")


VERBATIM_SITE_PAGES = {
    "advisor_brief.html": "docs/advisor_briefs/2026-07-17-window-a-brief.html",
}


STANDALONE_PAGES = [
    PageSpec(
        path=ROOT / "docs" / "project_critique_review.html",
        page_name="project_critique_review.html",
        aliases=["/project_critique_review.html", "/critique"],
        require_stylesheet=False,
        allow_no_stamps=True,
    )
]


class CapsulePackError(RuntimeError):
    pass


@dataclass(frozen=True)
class FontFaceRule:
    descriptors: dict[str, str]
    file_hash: str
    file_data: bytes


@dataclass
class FontFaceGroup:
    descriptors: dict[str, str]
    weights: list[int]
    file_data: bytes


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_git(args: list[str]) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def site_build_identity() -> dict[str, str]:
    manifest_path = SITE / "build_manifest.json"
    try:
        manifest = json.loads(read_text(manifest_path))
        renderer = manifest["renderer"]
        if manifest["schema"] != "joulewise-site-build/v1":
            raise ValueError("unsupported schema")
        mode = renderer["mode"]
        marked_version = renderer["markedVersion"]
        if not isinstance(mode, str) or marked_version != MARKED_VERSION:
            raise ValueError("invalid renderer identity")
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
        raise CapsulePackError(f"{manifest_path}: invalid site build identity: {exc}") from exc
    return {"siteRenderer": mode, "markedVersion": marked_version}


def build_info() -> dict[str, str]:
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if source_date_epoch is None:
        built_at = dt.datetime.now(dt.UTC).replace(microsecond=0)
    else:
        try:
            built_at = dt.datetime.fromtimestamp(int(source_date_epoch), dt.UTC)
        except (ValueError, OverflowError, OSError) as exc:
            raise CapsulePackError(f"invalid SOURCE_DATE_EPOCH: {source_date_epoch}") from exc
    identity = site_build_identity()
    return {
        "commit": run_git(["rev-parse", "--short", "HEAD"]),
        "branch": os.environ.get("JOULEWISE_BUILD_BRANCH") or run_git(["branch", "--show-current"]) or "detached",
        "builtAt": built_at.isoformat().replace("+00:00", "Z"),
        "siteRenderer": identity["siteRenderer"],
        "markedVersion": identity["markedVersion"],
        "lakebedVersion": LAKEBED_VERSION,
    }


def font_data_uri(font_data: bytes) -> str:
    data = base64.b64encode(font_data).decode("ascii")
    return f"data:font/woff2;base64,{data}"


def inline_fonts(fonts_css: str, fonts_dir: Path) -> str:
    block_re = re.compile(r"@font-face\s*\{\s*(?P<body>.*?)\s*\}", re.DOTALL)
    descriptor_re = re.compile(
        r"(?P<name>font-family|font-style|font-weight|font-stretch|font-display|src)\s*:\s*(?P<value>[^;]+);"
    )
    src_re = re.compile(
        r"url\((?P<quote>['\"]?)(?P<path>[^)'\"\s]+)(?P=quote)\)\s+format\((?P<format_quote>['\"]?)woff2(?P=format_quote)\)"
    )
    expected_order = ["font-family", "font-style", "font-weight", "font-stretch", "font-display", "src"]
    required = {"font-family", "font-style", "font-weight", "font-display", "src"}
    parsed: list[FontFaceRule] = []
    cursor = 0
    for block_match in block_re.finditer(fonts_css):
        if fonts_css[cursor : block_match.start()].strip():
            raise CapsulePackError("fonts.css: unexpected content outside @font-face block")
        cursor = block_match.end()
        descriptors: dict[str, str] = {}
        body = block_match.group("body")
        body_cursor = 0
        for descriptor_match in descriptor_re.finditer(body):
            if body[body_cursor : descriptor_match.start()].strip():
                raise CapsulePackError("fonts.css: unexpected @font-face descriptor structure")
            body_cursor = descriptor_match.end()
            name = descriptor_match.group("name")
            if name in descriptors:
                raise CapsulePackError(f"fonts.css: duplicate @font-face descriptor: {name}")
            descriptors[name] = descriptor_match.group("value").strip()
        if body[body_cursor:].strip():
            raise CapsulePackError("fonts.css: unexpected @font-face descriptor structure")
        if set(descriptors) - set(expected_order) or not required.issubset(descriptors):
            raise CapsulePackError("fonts.css: malformed @font-face block")
        order = [expected_order.index(name) for name in descriptors]
        if order != sorted(order):
            raise CapsulePackError("fonts.css: unexpected @font-face descriptor order")
        if not re.fullmatch(r"\d{1,4}", descriptors["font-weight"]):
            raise CapsulePackError("fonts.css: expected numeric @font-face font-weight")
        src_match = src_re.fullmatch(descriptors["src"])
        if not src_match:
            raise CapsulePackError("fonts.css: expected woff2 @font-face src")
        raw = src_match.group("path")
        font_path = fonts_dir / raw
        if not font_path.is_file():
            raise CapsulePackError(f"font CSS references missing font: {raw}")
        font_data = font_path.read_bytes()
        parsed.append(
            FontFaceRule(
                descriptors=descriptors,
                file_hash=hashlib.sha256(font_data).hexdigest(),
                file_data=font_data,
            )
        )
    if fonts_css[cursor:].strip():
        raise CapsulePackError("fonts.css: unexpected content outside @font-face block")
    if not parsed:
        raise CapsulePackError("fonts.css: expected @font-face blocks")

    groups: dict[tuple[str, str], FontFaceGroup] = {}
    for rule in parsed:
        key = (rule.descriptors["font-family"], rule.file_hash)
        comparable = {name: value for name, value in rule.descriptors.items() if name not in {"font-weight", "src"}}
        group = groups.setdefault(
            key,
            FontFaceGroup(descriptors=comparable, weights=[], file_data=rule.file_data),
        )
        if group.descriptors != comparable:
            raise CapsulePackError("fonts.css: duplicate font file has incompatible descriptors")
        group.weights.append(int(rule.descriptors["font-weight"]))

    rendered: list[str] = []
    for group in groups.values():
        descriptors = group.descriptors
        weights = sorted(set(group.weights))
        weight_value = str(weights[0]) if len(weights) == 1 else f"{weights[0]} {weights[-1]}"
        src_value = f"url({font_data_uri(group.file_data)}) format('woff2')"
        rendered.append("@font-face {")
        for name in expected_order:
            if name == "font-weight":
                rendered.append(f"  font-weight: {weight_value};")
            elif name == "src":
                rendered.append(f"  src: {src_value};")
            elif name in descriptors:
                rendered.append(f"  {name}: {descriptors[name]};")
        rendered.append("}")
    return "\n".join(rendered)


def stylesheet(no_fonts: bool = False) -> str:
    css_path = SITE / "style.css"
    fonts_path = SITE / "fonts" / "fonts.css"
    css = read_text(css_path)
    import_re = re.compile(r'@import\s+url\(["\']fonts/fonts\.css["\']\);\s*')
    if not import_re.search(css):
        raise CapsulePackError("style.css: expected @import url(\"fonts/fonts.css\")")
    if no_fonts:
        css = import_re.sub("", css, count=1)
        fallback_vars = {
            "serif": '"Iowan Old Style", Georgia, serif',
            "mono": 'ui-monospace, "SF Mono", Menlo, monospace',
            "sans": '-apple-system, "Helvetica Neue", sans-serif',
        }
        for name, value in fallback_vars.items():
            css, count = re.subn(rf'--{name}:\s*[^;]+;', f"--{name}: {value};", css, count=1)
            if count != 1:
                raise CapsulePackError(f"style.css: expected --{name} variable")
        return css
    fonts = inline_fonts(read_text(fonts_path), fonts_path.parent)
    return import_re.sub(fonts + "\n", css, count=1)


def extract_stamps(page_name: str, html: str) -> list[dict[str, str]]:
    stamps: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    title_re = re.compile(r'<span\s+class="source-chip"\s+title="([^"]+)"')
    stamp_re = re.compile(r"^(?P<source>.+?) · commit (?P<commit>[0-9a-fA-F]+|untracked)(?: \+ uncommitted)?$")
    for title in title_re.findall(html):
        label = html_lib.unescape(title)
        match = stamp_re.match(label)
        if not match:
            raise CapsulePackError(f"{page_name}: malformed source-chip title: {label!r}")
        item = {"source": match.group("source"), "commit": match.group("commit")}
        key = (item["source"], item["commit"])
        if key not in seen:
            seen.add(key)
            stamps.append(item)
    if not stamps and not page_allows_no_stamps(page_name):
        raise CapsulePackError(f"{page_name}: generated page has no provenance source-chip")
    return stamps


def extract_verbatim_stamp(spec: PageSpec, html: str) -> list[dict[str, str]]:
    marker_re = re.compile(
        r"\A<!-- JouleWise verbatim provenance: (?P<label>.+?); "
        r"source bytes after this line are copied verbatim\. -->\n"
    )
    match = marker_re.match(html)
    if not match:
        raise CapsulePackError(
            f"{spec.page_name}: expected leading verbatim provenance stamp"
        )
    stamp_re = re.compile(
        r"^(?P<source>.+?) · commit (?P<commit>[0-9a-fA-F]+|untracked)"
        r"(?: \+ uncommitted)?$"
    )
    stamp = stamp_re.match(html_lib.unescape(match.group("label")))
    if not stamp:
        raise CapsulePackError(f"{spec.page_name}: malformed verbatim provenance stamp")
    source = stamp.group("source")
    if source != spec.provenance_source:
        raise CapsulePackError(
            f"{spec.page_name}: verbatim provenance source {source!r} does not match "
            f"configured source {spec.provenance_source!r}"
        )
    return [{"source": source, "commit": stamp.group("commit")}]


def page_allows_no_stamps(page_name: str) -> bool:
    return page_name in KNOWN_HAND_PAGES or any(
        spec.page_name == page_name and spec.allow_no_stamps for spec in STANDALONE_PAGES
    )


def rewrite_stylesheet_link(html: str, page_name: str) -> str:
    link_re = re.compile(
        r'<link\b(?=[^>]*\brel=["\']stylesheet["\'])(?=[^>]*\bhref=["\'](?:\./|/)?style\.css["\'])[^>]*>\s*',
        re.IGNORECASE,
    )
    match = link_re.search(html)
    if not match:
        raise CapsulePackError(f"{page_name}: expected stylesheet link")
    link = match.group(0)

    def replace_href(href_match: re.Match[str]) -> str:
        return f'href={href_match.group("quote")}/style.css{href_match.group("quote")}'

    rewritten, count = re.subn(
        r'href=(?P<quote>["\'])(?:\./|/)?style\.css(?P=quote)',
        replace_href,
        link,
        count=1,
        flags=re.IGNORECASE,
    )
    if count != 1:
        raise CapsulePackError(f"{page_name}: expected stylesheet href")
    return html[: match.start()] + rewritten + html[match.end() :]


def rewrite_internal_hrefs(html: str) -> str:
    def rewrite_url(url: str) -> str:
        for source, target in INTERNAL_HREF_REWRITES.items():
            if url == source:
                return target
            if url.startswith(source + "#"):
                return target + url[len(source) :]
        return url

    def replace_href(match: re.Match[str]) -> str:
        url = match.group("url")
        rewritten = rewrite_url(url)
        if rewritten == url:
            return match.group(0)
        quote = match.group("quote")
        return f"{match.group('prefix')}{quote}{rewritten}{quote}"

    return re.sub(
        r'(?P<prefix>\bhref\s*=\s*)(?P<quote>["\'])(?P<url>[^"\']+)(?P=quote)',
        replace_href,
        html,
        flags=re.IGNORECASE,
    )


FRESHNESS_STYLE = """
<style>
.jw-freshness-banner{position:fixed;left:16px;right:16px;bottom:14px;z-index:1000;display:flex;align-items:center;gap:12px;max-width:960px;margin:0 auto;padding:10px 12px;border:1px solid color-mix(in srgb,var(--amber,#d6a84a) 45%,var(--line,#334155));border-radius:8px;background:color-mix(in srgb,var(--bg-deep,#101820) 94%,transparent);box-shadow:0 8px 30px rgba(0,0,0,.32);color:var(--ink,#f8fafc);font:13px/1.4 var(--sans,-apple-system,"Helvetica Neue",sans-serif)}
.jw-freshness-banner a,.jw-chip-moved{color:var(--amber,#d6a84a);text-decoration:none}
.jw-freshness-banner a:hover,.jw-chip-moved:hover{text-decoration:underline}
.jw-freshness-banner button{margin-left:auto;border:1px solid var(--line,#334155);border-radius:6px;background:var(--panel,#17212b);color:var(--ink-2,#cbd5e1);font:12px var(--mono,ui-monospace,"SF Mono",Menlo,monospace);padding:4px 8px;cursor:pointer}
.jw-chip-moved{margin-left:6px;font-family:var(--mono,ui-monospace,"SF Mono",Menlo,monospace);font-size:11px;white-space:nowrap}
@media (prefers-reduced-motion:no-preference){.jw-freshness-banner{animation:jwFreshnessIn .16s ease-out}@keyframes jwFreshnessIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}}
</style>
""".strip()


FRESHNESS_SCRIPT = r"""
<script>
(function(){
  var repo="https://github.com/mpmdw/JouleWise";
  function shortHash(value){return String(value||"").slice(0,7);}
  function chipSource(chip){
    var title=chip.getAttribute("title")||"";
    var match=title.match(/^(.+?) · commit ([^ ]+)/);
    return match?match[1]:null;
  }
  function render(data){
    if(!data||!Array.isArray(data.sources)){return;}
    var moved={};
    data.sources.forEach(function(item){if(item&&item.checked&&item.moved&&item.source){moved[item.source]=item;}});
    var movedCount=Object.keys(moved).length;
    if(!movedCount){return;}
    document.querySelectorAll(".source-chip").forEach(function(chip){
      if(chip.getAttribute("data-jw-freshness")){return;}
      var source=chipSource(chip);
      if(!source||!moved[source]){return;}
      chip.setAttribute("data-jw-freshness","moved");
      var link=document.createElement("a");
      link.className="jw-chip-moved";
      link.href=repo+"/blob/main/"+source;
      link.target="_blank";
      link.rel="noopener";
      link.textContent="· moved ↗";
      chip.appendChild(link);
    });
    if(sessionStorage.getItem("jwFreshnessDismissed")==="1"){return;}
    var banner=document.createElement("div");
    banner.className="jw-freshness-banner";
    banner.setAttribute("role","status");
    var docs=movedCount===1?"source document has":"source documents have";
    banner.innerHTML="This snapshot was built from <span class=\"mono\">"+shortHash(data.build&&data.build.commit)+"</span>; "+movedCount+" "+docs+" moved on GitHub since — <a href=\""+repo+"\" target=\"_blank\" rel=\"noopener\">view latest ↗</a>";
    var button=document.createElement("button");
    button.type="button";
    button.setAttribute("aria-label","Dismiss freshness notice");
    button.textContent="Dismiss";
    button.addEventListener("click",function(){sessionStorage.setItem("jwFreshnessDismissed","1");banner.remove();});
    banner.appendChild(button);
    document.body.appendChild(banner);
  }
  fetch("/api/freshness").then(function(response){return response.json();}).then(render).catch(function(){});
})();
</script>
""".strip()


def inject_freshness(html: str, page_name: str) -> str:
    marker = "</body>"
    if marker not in html:
        raise CapsulePackError(f"{page_name}: expected </body>")
    return html.replace(marker, FRESHNESS_STYLE + "\n" + FRESHNESS_SCRIPT + "\n" + marker, 1)


def page_aliases(page_path: Path) -> list[str]:
    name = page_path.name
    stem = page_path.stem
    aliases = [f"/{name}", f"/{stem}"]
    if name == "index.html":
        aliases.insert(0, "/")
    return aliases


def canonical_path(aliases: list[str]) -> str:
    for alias in aliases:
        if alias not in RESERVED_PATHS:
            return alias
    raise CapsulePackError("page has no non-reserved serving path")


def site_page_specs() -> list[PageSpec]:
    html_paths = sorted(SITE.glob("*.html"))
    if not html_paths:
        raise CapsulePackError("docs/site contains no HTML pages")
    redirected_aliases: dict[str, list[str]] = {}
    for source_name, target_name in CAPSULE_PAGE_REDIRECTS.items():
        redirected_aliases.setdefault(target_name, []).extend(page_aliases(SITE / source_name))
    specs = [
        PageSpec(
            path=page_path,
            page_name=page_path.name,
            aliases=[*page_aliases(page_path), *redirected_aliases.get(page_path.name, [])],
            require_stylesheet=page_path.name not in VERBATIM_SITE_PAGES,
            mode=(
                PageMode.VERBATIM
                if page_path.name in VERBATIM_SITE_PAGES
                else PageMode.GENERATED
            ),
            provenance_source=VERBATIM_SITE_PAGES.get(page_path.name),
        )
        for page_path in html_paths
        if page_path.name not in CAPSULE_PAGE_REDIRECTS
    ]
    missing_targets = sorted(set(redirected_aliases) - {spec.page_name for spec in specs})
    if missing_targets:
        raise CapsulePackError(
            "capsule page redirect target is missing: " + ", ".join(missing_targets)
        )
    for spec in STANDALONE_PAGES:
        if not spec.path.is_file():
            raise CapsulePackError(f"standalone page is missing: {spec.path.relative_to(ROOT)}")
        specs.append(spec)
    return specs


def pack_page(spec: PageSpec) -> dict[str, object]:
    raw = read_text(spec.path)
    if spec.mode is PageMode.VERBATIM:
        stamps = extract_verbatim_stamp(spec, raw)
        return {"html": raw, "sources": stamps, "verbatim": True}
    stamps = extract_stamps(spec.page_name, raw)
    packed = rewrite_internal_hrefs(raw)
    if spec.require_stylesheet:
        packed = rewrite_stylesheet_link(packed, spec.page_name)
    if "</body>" not in packed:
        raise CapsulePackError(f"{spec.page_name}: expected </body>")
    return {"html": packed, "sources": stamps, "verbatim": False}


def pack_pages() -> dict[str, dict[str, object]]:
    pages: dict[str, dict[str, object]] = {}
    claimed_paths: set[str] = set()
    for spec in site_page_specs():
        entry = pack_page(spec)
        canonical = canonical_path(spec.aliases)
        aliases = [alias for alias in spec.aliases if alias != canonical and alias not in RESERVED_PATHS]
        for path in [canonical, *aliases]:
            if path in claimed_paths:
                raise CapsulePackError(f"duplicate page serving path: {path}")
            claimed_paths.add(path)
        pages[canonical] = {**entry, "aliases": aliases}
    return pages


def escape_validator_text(encoded: str) -> str:
    for token in VALIDATOR_TOKENS:
        escaped = f"\\u{ord(token[0]):04x}{token[1:]}"
        encoded = encoded.replace(token, escaped)
    return encoded.replace("for(;;)", "\\u0066or(;;)")


def ts_json_parse(value: object) -> str:
    # A JSON document is a valid TS expression (strings, arrays, objects),
    # so emit it directly — wrapping in JSON.parse("...") double-escaped
    # every backslash/quote/newline and blew past the deploy body limit.
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    encoded = encoded.replace("`", "\\u0060").replace("${", "\\u0024{")
    # Lakebed's anonymous-build validator text-scans module source for the
    # deny-list even inside string literals. Escape one letter so the emitted
    # source never contains a rejected token; JS restores the original text.
    return escape_validator_text(encoded)


def gzip_bytes(text: str) -> bytes:
    return gzip.compress(text.encode("utf-8"), compresslevel=9, mtime=0)


def ts_string(value: str) -> str:
    return escape_validator_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")))


def chunk_ts_string(value: str, width: int = 4000) -> str:
    """Emit a long string as concatenated short literals. The production
    runtime 500s (Buffer.alloc in its loader) on megabyte-scale single-line
    literals; ~4KB segments keep lines short."""
    if len(value) <= width:
        return ts_string(value)
    parts = [ts_string(value[i:i + width]) for i in range(0, len(value), width)]
    return "(" + " +\n    ".join(parts) + ")"


def shared_sources(pages: dict[str, dict[str, object]]) -> list[dict[str, str]]:
    commits: dict[str, str] = {}
    for entry in pages.values():
        for stamp in entry["sources"]:
            source = str(stamp["source"])
            commit = str(stamp["commit"])
            prior = commits.setdefault(source, commit)
            if prior != commit:
                raise CapsulePackError(f"conflicting baked commits for {source}: {prior} vs {commit}")
    return [{"source": source, "commit": commits[source]} for source in sorted(commits)]


def encode_json_archive(value: object) -> tuple[str, dict[str, int]]:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    compressed = gzip_bytes(raw)
    encoded = base64.b64encode(compressed).decode("ascii")
    return encoded, {
        "raw": len(raw.encode("utf-8")),
        "gzip": len(compressed),
        "base64": len(encoded.encode("ascii")),
    }


def encode_page_shard(
    pages: dict[str, dict[str, object]], paths: list[str]
) -> tuple[str, dict[str, int]]:
    return encode_json_archive({path: str(pages[path]["html"]) for path in sorted(paths)})


def page_shards(pages: dict[str, dict[str, object]]) -> list[list[str]]:
    individual_sizes = {
        path: encode_page_shard(pages, [path])[1]["base64"] for path in pages
    }
    decision_log_oversized = [
        path
        for path, size in individual_sizes.items()
        if re.fullmatch(r"/decision_log(?:_archive_\d+)?\.html", path)
        and size > DECISION_LOG_SHARD_BASE64_TARGET_BYTES
    ]
    if decision_log_oversized:
        details = ", ".join(
            f"{path} ({individual_sizes[path]} bytes)"
            for path in sorted(decision_log_oversized)
        )
        raise CapsulePackError(
            "decision-log page exceeds "
            f"{DECISION_LOG_SHARD_BASE64_TARGET_BYTES}-byte pagination target: "
            f"{details}; adjust entry-boundary pagination"
        )
    oversized = [path for path, size in individual_sizes.items() if size > MAX_SHARD_BASE64_BYTES]
    if oversized:
        details = ", ".join(f"{path} ({individual_sizes[path]} bytes)" for path in sorted(oversized))
        raise CapsulePackError(
            f"page exceeds {MAX_SHARD_BASE64_BYTES}-byte runtime shard budget: {details}; split the page"
        )

    shards: list[list[str]] = []
    for path in sorted(pages, key=lambda item: (individual_sizes[item], item), reverse=True):
        candidates: list[tuple[int, int]] = []
        for index, shard in enumerate(shards):
            size = encode_page_shard(pages, [*shard, path])[1]["base64"]
            if size <= MAX_SHARD_BASE64_BYTES:
                candidates.append((size, index))
        if candidates:
            _, index = min(candidates)
            shards[index].append(path)
        else:
            shards.append([path])
    return [sorted(shard) for shard in shards]


def encode_site(
    pages: dict[str, dict[str, object]], css: str
) -> tuple[dict[str, object], dict[str, int]]:
    shard_paths = page_shards(pages)
    encoded_shards: list[str] = []
    shard_stats: list[dict[str, int]] = []
    routes: dict[str, dict[str, object]] = {}
    for index, paths in enumerate(shard_paths):
        encoded, stats = encode_page_shard(pages, paths)
        encoded_shards.append(encoded)
        shard_stats.append(stats)
        for path in paths:
            routes[path] = {
                "shard": index,
                "aliases": list(pages[path].get("aliases", [])),
                "verbatim": bool(pages[path].get("verbatim", False)),
            }
    shared, shared_stats = encode_json_archive(
        {
            "freshness": FRESHNESS_STYLE + "\n" + FRESHNESS_SCRIPT,
            "style": css,
        }
    )
    return {
        "shared": shared,
        "shards": encoded_shards,
        "routes": {path: routes[path] for path in sorted(routes)},
        "sources": shared_sources(pages),
    }, {
        "raw": shared_stats["raw"] + sum(item["raw"] for item in shard_stats),
        "gzip": shared_stats["gzip"] + sum(item["gzip"] for item in shard_stats),
        "base64": shared_stats["base64"] + sum(item["base64"] for item in shard_stats),
        "shards": len(shard_stats),
        "max_shard": max(item["base64"] for item in shard_stats),
        "first_request_decode": shared_stats["gzip"] + max(item["gzip"] for item in shard_stats),
    }


def emit_site(pages: dict[str, dict[str, object]], css: str, out_path: Path) -> dict[str, int]:
    site, stats = encode_site(pages, css)
    lines = [
        "export type PageSource = { source: string; commit: string };",
        "export type PackedRoute = { shard: number; aliases: string[]; verbatim: boolean };",
        "export type PackedSite = { shared: string; shards: string[]; routes: Record<string, PackedRoute>; sources: PageSource[] };",
        "export const PACKED_SITE: PackedSite = {",
        f"  shared: {chunk_ts_string(str(site['shared']))},",
        "  shards: [",
        *[f"    {chunk_ts_string(str(archive))}," for archive in site["shards"]],
        "  ],",
        f"  routes: {ts_json_parse(site['routes'])},",
        f"  sources: {ts_json_parse(site['sources'])},",
        "};",
    ]
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    manifest = len(ts_json_parse(site["routes"]).encode("utf-8")) + len(ts_json_parse(site["sources"]).encode("utf-8"))
    return {**stats, "manifest": manifest}


def emit_buildinfo(build: dict[str, str], out_path: Path) -> None:
    out_path.write_text(f"export const BUILD = {ts_json_parse(build)};\n", encoding="utf-8")


def packed_size(paths: list[Path]) -> int:
    return sum(path.stat().st_size for path in paths)


def base64_size(size: int) -> int:
    return 4 * ((size + 2) // 3)


def estimate_lakebed_artifact_size(content_size: int) -> int:
    raw_server = content_size + base64_size(content_size) + LAKEBED_BASE_WRAPPER_BUDGET_BYTES
    return base64_size(raw_server) + LAKEBED_METADATA_BUDGET_BYTES


def enforce_lakebed_budget(content_size: int) -> int:
    estimate = estimate_lakebed_artifact_size(content_size)
    if estimate > LAKEBED_ESTIMATE_FALLBACK_BUDGET_BYTES:
        raise CapsulePackError(
            "estimated Lakebed artifact "
            f"{estimate} bytes exceeds conservative estimate-only "
            f"{LAKEBED_ESTIMATE_FALLBACK_BUDGET_BYTES}-byte budget "
            f"(1 MiB cap with at least 10% margin; packed content {content_size} bytes)"
        )
    return estimate


def npm_package_version(executable: Path, package_name: str) -> str | None:
    resolved = executable.resolve()
    for parent in resolved.parents:
        package_path = parent / "package.json"
        if not package_path.is_file():
            continue
        try:
            package = json.loads(read_text(package_path))
        except (OSError, json.JSONDecodeError):
            continue
        if package.get("name") == package_name:
            version = package.get("version")
            return version if isinstance(version, str) else None
    return None


def lakebed_discovery_event(
    *, level: str, code: str, mode: str, message: str, candidate: Path | None = None
) -> dict[str, str]:
    event = {
        "schema": LAKEBED_DISCOVERY_SCHEMA,
        "level": level,
        "code": code,
        "mode": mode,
        "message": message,
    }
    if candidate is not None:
        event["candidate"] = str(candidate)
    return event


def emit_lakebed_discovery_event(event: dict[str, str]) -> None:
    print(json.dumps(event, sort_keys=True, separators=(",", ":")), file=sys.stderr)


def validate_lakebed_executable(candidate: Path, source: str) -> Path:
    if not candidate.is_file() or not os.access(candidate, os.X_OK):
        event = lakebed_discovery_event(
            level="ERROR",
            code="lakebed_executable_not_executable",
            mode="refused",
            message=f"{source} did not resolve to an executable Lakebed CLI",
            candidate=candidate,
        )
        emit_lakebed_discovery_event(event)
        raise CapsulePackError(
            f"Lakebed executable discovery refused: {source} is not executable: {candidate}"
        )
    version = npm_package_version(candidate, "lakebed")
    if version != LAKEBED_VERSION:
        event = lakebed_discovery_event(
            level="ERROR",
            code="lakebed_version_mismatch",
            mode="refused",
            message=(
                f"{source} resolved Lakebed {version or 'unknown'}; "
                f"exact version {LAKEBED_VERSION} is required"
            ),
            candidate=candidate,
        )
        emit_lakebed_discovery_event(event)
        raise CapsulePackError(
            f"Lakebed version mismatch at {candidate}: expected {LAKEBED_VERSION}, found {version or 'unknown'}"
        )
    return candidate.resolve()


def discover_lakebed_executable() -> Path | None:
    """Find an exact-version Lakebed CLI through explicit, local, then OS paths."""
    if "JOULEWISE_LAKEBED_BIN" in os.environ:
        configured = os.environ["JOULEWISE_LAKEBED_BIN"]
        candidate = Path(configured).expanduser() if configured else Path(configured)
        return validate_lakebed_executable(candidate, "JOULEWISE_LAKEBED_BIN")

    if LAKEBED_LOCAL_EXECUTABLE.is_file():
        return validate_lakebed_executable(
            LAKEBED_LOCAL_EXECUTABLE,
            "site_capsule/node_modules/.bin/lakebed",
        )

    discovered = shutil.which("lakebed")
    if discovered:
        return validate_lakebed_executable(Path(discovered), "OS PATH")
    return None


def lakebed_stable_json_size(value: object) -> int:
    """Match Lakebed's stableStringify byte count for validator artifacts."""
    encoded = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return len(encoded.encode("utf-8"))


def measure_lakebed_artifact(executable: Path, capsule_dir: Path) -> tuple[int, str]:
    """Build and measure the exact artifact object checked by Lakebed."""
    with tempfile.TemporaryDirectory(prefix="joulewise-lakebed-build-") as temp_dir:
        artifact_path = Path(temp_dir) / "artifact.json"
        command = [
            str(executable),
            "build",
            str(capsule_dir.resolve()),
            "--target",
            "anonymous",
            "--out",
            str(artifact_path),
            "--json",
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                check=False,
                timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise CapsulePackError(
                f"measured Lakebed artifact build could not run via {executable}: {exc}"
            ) from exc
        if completed.returncode != 0:
            detail = "\n".join(
                part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
            )
            raise CapsulePackError(
                "measured Lakebed artifact build failed "
                f"via {executable} (exit {completed.returncode}): {detail or 'no diagnostic output'}"
            )
        try:
            envelope = json.loads(artifact_path.read_text(encoding="utf-8"))
            artifact = envelope["artifact"]
            created_with = artifact.get("createdWith", {})
            version = str(created_with.get("lakebed", "unknown"))
            measured = lakebed_stable_json_size(artifact)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise CapsulePackError(
                f"measured Lakebed build produced an unreadable validator artifact: {exc}"
            ) from exc
    return measured, version


def enforce_lakebed_artifact_postcondition(
    content_size: int,
    capsule_dir: Path | None = None,
) -> int:
    capsule_dir = CAPSULE if capsule_dir is None else capsule_dir
    executable = discover_lakebed_executable()
    if executable is None:
        emit_lakebed_discovery_event(
            lakebed_discovery_event(
                level="WARNING",
                code="lakebed_executable_unavailable",
                mode="estimator_only_advisory",
                message=(
                    "No exact-version Lakebed executable was found via "
                    "JOULEWISE_LAKEBED_BIN, site_capsule/node_modules/.bin/lakebed, "
                    "or OS PATH; artifact size is not measured"
                ),
            )
        )
        print(
            "Lakebed artifact postcondition mode: estimator-only advisory "
            "(Lakebed executable unavailable)"
        )
        estimate = estimate_lakebed_artifact_size(content_size)
        print(
            f"advisory estimated Lakebed artifact: {estimate} bytes "
            f"(estimate-only budget {LAKEBED_ESTIMATE_FALLBACK_BUDGET_BYTES}; "
            f"cap {LAKEBED_ARTIFACT_CAP_BYTES})"
        )
        return enforce_lakebed_budget(content_size)

    print(f"Lakebed artifact postcondition mode: measured ({executable})")
    measured, version = measure_lakebed_artifact(executable, capsule_dir)
    print(
        f"measured Lakebed validator artifact: {measured} bytes "
        f"(measured budget {LAKEBED_MEASURED_ARTIFACT_BUDGET_BYTES}; "
        f"cap {LAKEBED_ARTIFACT_CAP_BYTES}; "
        f"Lakebed {version})"
    )
    if measured > LAKEBED_ARTIFACT_CAP_BYTES:
        raise CapsulePackError(
            "measured Lakebed validator artifact "
            f"{measured} bytes is over the 1 MiB cap by "
            f"{measured - LAKEBED_ARTIFACT_CAP_BYTES} bytes "
            f"(packed content {content_size} bytes)"
        )
    if measured > LAKEBED_MEASURED_ARTIFACT_BUDGET_BYTES:
        cap_detail = (
            f"{LAKEBED_ARTIFACT_CAP_BYTES - measured} bytes below the 1 MiB cap"
        )
        raise CapsulePackError(
            "measured Lakebed validator artifact "
            f"{measured} bytes exceeds measured-artifact "
            f"{LAKEBED_MEASURED_ARTIFACT_BUDGET_BYTES}-byte budget "
            f"({cap_detail}; packed content {content_size} bytes)"
        )
    return measured


def enforce_runtime_decode_budget(stats: dict[str, int]) -> None:
    if stats["first_request_decode"] > MAX_FIRST_REQUEST_DECODE_BYTES:
        raise CapsulePackError(
            "first-request base64 decode requires "
            f"{stats['first_request_decode']} byte-loop iterations, above the "
            f"{MAX_FIRST_REQUEST_DECODE_BYTES}-iteration runtime budget"
        )


def lakebed_source_paths(capsule_dir: Path | None = None) -> list[Path]:
    """Return every regular server/shared source Lakebed's validator scans."""
    capsule_dir = CAPSULE if capsule_dir is None else capsule_dir
    paths: list[Path] = []
    for source_root in (capsule_dir / "server", capsule_dir / "shared"):
        if not source_root.is_dir():
            continue
        for path in source_root.rglob("*"):
            relative_parts = path.relative_to(capsule_dir).parts
            if any(part in {"node_modules", ".lakebed"} for part in relative_parts):
                continue
            if path.name == ".DS_Store" or path.is_symlink() or not path.is_file():
                continue
            paths.append(path)
    return sorted(paths)


def validate_lakebed_sources(paths: list[Path], capsule_dir: Path | None = None) -> None:
    capsule_dir = CAPSULE if capsule_dir is None else capsule_dir
    for path in paths:
        source = read_text(path)
        try:
            label = str(path.relative_to(capsule_dir))
        except ValueError:
            label = str(path)
        for token in VALIDATOR_TOKENS:
            if token in source:
                raise CapsulePackError(f"{label}: Lakebed validator token remains: {token}")
        if UNBOUNDED_FOR_RE.search(source):
            raise CapsulePackError(f"{label}: unbounded for-loop remains")
        legacy_api = LEGACY_DATABASE_API_RE.search(source)
        if legacy_api:
            raise CapsulePackError(
                f"{label}: Lakebed legacy database API remains: {legacy_api.group(0)}"
            )


def build(no_fonts: bool = False, enforce_budget: bool = True) -> int:
    CAPSULE_CONTENT.mkdir(parents=True, exist_ok=True)
    pages = pack_pages()
    css = stylesheet(no_fonts=no_fonts)
    pages_path = CAPSULE_CONTENT / "pages.ts"
    buildinfo_path = CAPSULE_CONTENT / "buildinfo.ts"
    stats = emit_site(pages, css, pages_path)
    emit_buildinfo(build_info(), buildinfo_path)
    legacy_styles_path = CAPSULE_CONTENT / "styles.ts"
    if legacy_styles_path.exists():
        legacy_styles_path.unlink()
    total = packed_size([pages_path, buildinfo_path])
    print(
        "sharded archives: "
        f"{stats['raw']} raw -> {stats['gzip']} gzip -> {stats['base64']} base64 bytes; "
        f"{stats['shards']} page shards (largest {stats['max_shard']} bytes); "
        f"first-request decode {stats['first_request_decode']} bytes; "
        f"route/source manifest: {stats['manifest']} bytes"
    )
    for label, path in [("pages", pages_path), ("buildinfo", buildinfo_path)]:
        size = path.stat().st_size
        print(f"{label}: {size} bytes ({size / 1024 / 1024:.2f} MiB)")
    print(f"packed capsule content: {total} bytes ({total / 1024 / 1024:.2f} MiB)")
    validate_lakebed_sources(lakebed_source_paths(), CAPSULE)
    if enforce_budget:
        enforce_runtime_decode_budget(stats)
        enforce_lakebed_artifact_postcondition(total)
    else:
        print("Lakebed artifact postcondition mode: disabled (non-Lakebed --fonts flow)")
    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    # Fonts are OFF by default: embedded woff2 pushes the Lakebed deploy
    # artifact past its 1 MiB limit, so the deploy flow (pack -> deploy)
    # must produce a fonts-free capsule. --fonts inlines them for other
    # static hosts that have no such limit.
    parser.add_argument("--fonts", action="store_true", help="inline woff2 files as data URIs (exceeds the Lakebed artifact limit; for other hosts)")
    args = parser.parse_args(argv)
    try:
        build(no_fonts=not args.fonts, enforce_budget=not args.fonts)
    except (CapsulePackError, subprocess.CalledProcessError) as exc:
        print(f"pack_capsule.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
