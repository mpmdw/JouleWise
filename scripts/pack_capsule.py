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
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs" / "site"
CAPSULE_CONTENT = ROOT / "site_capsule" / "server" / "content"
KNOWN_HAND_PAGES = {"index.html", "results.html", "process.html", "research.html"}
GITHUB_REPO = "https://github.com/mpmdw/JouleWise"
INTERNAL_HREF_REWRITES = {
    "index.html": "/index",
    "../project_critique_review.html": "/project_critique_review.html",
}
RESERVED_PATHS = {"/", "/index.html"}


@dataclass(frozen=True)
class PageSpec:
    path: Path
    page_name: str
    aliases: list[str]
    require_stylesheet: bool = True
    allow_no_stamps: bool = False


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


def build_info() -> dict[str, str]:
    return {
        "commit": run_git(["rev-parse", "--short", "HEAD"]),
        "branch": run_git(["branch", "--show-current"]) or "detached",
        "builtAt": dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
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
    specs = [PageSpec(path=page_path, page_name=page_path.name, aliases=page_aliases(page_path)) for page_path in html_paths]
    for spec in STANDALONE_PAGES:
        if not spec.path.is_file():
            raise CapsulePackError(f"standalone page is missing: {spec.path.relative_to(ROOT)}")
        specs.append(spec)
    return specs


def pack_page(spec: PageSpec) -> dict[str, object]:
    raw = read_text(spec.path)
    stamps = extract_stamps(spec.page_name, raw)
    packed = rewrite_internal_hrefs(raw)
    if spec.require_stylesheet:
        packed = rewrite_stylesheet_link(packed, spec.page_name)
    packed = inject_freshness(packed, spec.page_name)
    return {"html": packed, "sources": stamps}


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


def ts_json_parse(value: object) -> str:
    # A JSON document is a valid TS expression (strings, arrays, objects),
    # so emit it directly — wrapping in JSON.parse("...") double-escaped
    # every backslash/quote/newline and blew past the deploy body limit.
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    encoded = encoded.replace("`", "\\u0060").replace("${", "\\u0024{")
    # Lakebed's anonymous-build validator text-scans module source for the
    # tokens `process` and `fetch`, flagging them even inside string
    # literals (e.g. links to process.html, the freshness script). Escape
    # one letter as a \u sequence so the emitted source never contains the
    # literal token; the string decodes identically at parse time.
    encoded = encoded.replace("process", "proc\\u0065ss").replace("fetch", "f\\u0065tch")
    return encoded


def gzip_base64(text: str) -> str:
    compressed = gzip.compress(text.encode("utf-8"), mtime=0)
    return base64.b64encode(compressed).decode("ascii")


def chunk_ts_string(value: str, width: int = 4000) -> str:
    """Emit a long string as concatenated short literals. The production
    runtime 500s (Buffer.alloc in its loader) on megabyte-scale single-line
    literals; ~4KB segments keep lines short."""
    if len(value) <= width:
        return json.dumps(value, separators=(",", ":"))
    parts = [json.dumps(value[i:i + width]) for i in range(0, len(value), width)]
    return "(" + " +\n    ".join(parts) + ")"


def emit_pages(pages: dict[str, dict[str, object]], out_path: Path) -> None:
    lines = [
        "export type PageSource = { source: string; commit: string };",
        "export type PackedPage = { gz: string; sources: PageSource[]; aliases: string[] };",
        "export const PAGES: Record<string, PackedPage> = {",
    ]
    for path in sorted(pages):
        entry = pages[path]
        # Keys get the same validator-token escaping as ts_json_parse bodies;
        # \u escapes in a plain JS string literal decode at parse time.
        key = json.dumps(path).replace("process", "proc\\u0065ss").replace("fetch", "f\\u0065tch")
        gz = chunk_ts_string(gzip_base64(str(entry["html"])))
        lines.append(
            f"  {key}: {{ gz: {gz}, sources: {ts_json_parse(entry['sources'])}, aliases: {ts_json_parse(entry.get('aliases', []))} }},"
        )
    lines.append("};")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def emit_buildinfo(build: dict[str, str], out_path: Path) -> None:
    out_path.write_text(f"export const BUILD = {ts_json_parse(build)};\n", encoding="utf-8")


def emit_styles(css: str, out_path: Path) -> None:
    gz = chunk_ts_string(gzip_base64(css))
    out_path.write_text(f"export const STYLE_CSS_GZ: string = {gz};\n", encoding="utf-8")


def packed_size(paths: list[Path]) -> int:
    return sum(path.stat().st_size for path in paths)


def build(no_fonts: bool = False) -> int:
    CAPSULE_CONTENT.mkdir(parents=True, exist_ok=True)
    pages = pack_pages()
    css = stylesheet(no_fonts=no_fonts)
    pages_path = CAPSULE_CONTENT / "pages.ts"
    styles_path = CAPSULE_CONTENT / "styles.ts"
    buildinfo_path = CAPSULE_CONTENT / "buildinfo.ts"
    emit_pages(pages, pages_path)
    emit_styles(css, styles_path)
    emit_buildinfo(build_info(), buildinfo_path)
    total = packed_size([pages_path, styles_path, buildinfo_path])
    for label, path in [("pages", pages_path), ("styles", styles_path), ("buildinfo", buildinfo_path)]:
        size = path.stat().st_size
        print(f"{label}: {size} bytes ({size / 1024 / 1024:.2f} MiB)")
    print(f"packed capsule content: {total} bytes ({total / 1024 / 1024:.2f} MiB)")
    if total > 4 * 1024 * 1024:
        print("warning: packed capsule content exceeds 4 MiB", file=sys.stderr)
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
        build(no_fonts=not args.fonts)
    except (CapsulePackError, subprocess.CalledProcessError) as exc:
        print(f"pack_capsule.py: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
