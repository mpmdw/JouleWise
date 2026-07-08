#!/usr/bin/env python3
"""Build docs/site/ — static HTML versions of the front-facing docs.

Renders Markdown via `npx --yes marked --gfm` (Node), wraps each page in a
shared template with light/dark styling and a nav sidebar. Docs-only
tooling; deliberately independent of the measurement venv.

Usage: python3 scripts/build_site.py
"""

from __future__ import annotations

import html
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "site"

# (source path, output name, nav title)
PAGES = [
    ("README.md", "readme.html", "README"),
    ("PROJECT_STATUS.md", "project_status.html", "Project Status (advisor)"),
    ("docs/orchestration.md", "orchestration.html", "Orchestration Process"),
    ("AGENT_PLAN.md", "agent_plan.html", "Agent Plan"),
    ("RUN_STATE.md", "run_state.html", "Run State"),
    ("TASK_QUEUE.md", "task_queue.html", "Task Queue"),
    ("docs/decision_log.md", "decision_log.html", "Decision Log"),
    ("docs/council_log.md", "council_log.html", "Council Log"),
    ("docs/milestones.md", "milestones.html", "Milestones"),
    ("docs/risk_register.md", "risk_register.html", "Risk Register"),
    (
        "docs/run_reports/2026-07-07-resume-merge-session.md",
        "latest_run_report.html",
        "Latest Run Report",
    ),
]

CSS = """
:root {
  --bg: #fdfdfc; --fg: #1a1d21; --muted: #5b6470; --accent: #7050c8;
  --border: #e3e2de; --code-bg: #f3f2ef; --nav-bg: #f8f7f5;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #16181d; --fg: #dfe2e8; --muted: #98a1ad; --accent: #a795e8;
    --border: #2c3038; --code-bg: #20242b; --nav-bg: #1b1e24;
  }
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--fg);
  font: 16px/1.65 -apple-system, "Segoe UI", Helvetica, Arial, sans-serif;
}
.layout { display: flex; min-height: 100vh; }
nav {
  width: 250px; flex-shrink: 0; background: var(--nav-bg);
  border-right: 1px solid var(--border); padding: 1.4rem 1rem;
  position: sticky; top: 0; height: 100vh; overflow-y: auto;
}
nav h2 { font-size: 1rem; margin: 0 0 .8rem; color: var(--accent); }
nav a {
  display: block; padding: .35rem .6rem; border-radius: 6px;
  color: var(--fg); text-decoration: none; font-size: .92rem;
}
nav a:hover { background: var(--code-bg); }
nav a.active { background: var(--accent); color: #fff; }
main { flex: 1; min-width: 0; padding: 2.2rem 3rem 4rem; }
article { max-width: 52rem; margin: 0 auto; }
h1, h2, h3 { line-height: 1.25; }
h1 { font-size: 1.75rem; border-bottom: 2px solid var(--border); padding-bottom: .4rem; }
h2 { font-size: 1.3rem; margin-top: 2.2rem; border-bottom: 1px solid var(--border); padding-bottom: .25rem; }
h3 { font-size: 1.08rem; margin-top: 1.6rem; }
a { color: var(--accent); }
code {
  background: var(--code-bg); padding: .12em .35em; border-radius: 4px;
  font: .88em ui-monospace, "SF Mono", Menlo, monospace;
}
pre { background: var(--code-bg); padding: .9rem 1rem; border-radius: 8px; overflow-x: auto; }
pre code { background: none; padding: 0; }
blockquote { margin: 1rem 0; padding: .1rem 1rem; border-left: 3px solid var(--accent); color: var(--muted); }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: .92rem; display: block; overflow-x: auto; }
th, td { border: 1px solid var(--border); padding: .45rem .6rem; text-align: left; vertical-align: top; }
th { background: var(--code-bg); }
tr:nth-child(even) td { background: color-mix(in srgb, var(--code-bg) 45%, transparent); }
hr { border: none; border-top: 1px solid var(--border); margin: 2rem 0; }
.pagemeta { color: var(--muted); font-size: .85rem; margin-bottom: 1.5rem; }
@media (max-width: 800px) {
  .layout { flex-direction: column; }
  nav { width: 100%; height: auto; position: static; display: flex; flex-wrap: wrap; gap: .2rem; }
  nav h2 { width: 100%; }
  main { padding: 1.2rem; }
}
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — JouleWise</title>
<style>{css}</style>
</head>
<body>
<div class="layout">
<nav>
<h2>JouleWise</h2>
{nav}
</nav>
<main><article>
<p class="pagemeta">Rendered from <code>{source}</code> · {stamp}</p>
{body}
</article></main>
</div>
</body>
</html>
"""

INDEX_INTRO = """<h1>JouleWise — Project Documents</h1>
<p>Static HTML renderings of the front-facing project documents.
Regenerate with <code>python3 scripts/build_site.py</code> after any doc
change. The Markdown files in the repository remain the source of
truth.</p>
<ul>
"""


def render_markdown(path: Path) -> str:
    result = subprocess.run(
        ["npx", "--yes", "marked", "--gfm"],
        input=path.read_text(encoding="utf-8"),
        capture_output=True,
        text=True,
        check=True,
        cwd=ROOT,
    )
    return result.stdout


def nav_html(active: str) -> str:
    items = ['<a href="index.html"{}>Index</a>'.format(
        ' class="active"' if active == "index.html" else "")]
    for _, out_name, title in PAGES:
        cls = ' class="active"' if out_name == active else ""
        items.append(f'<a href="{out_name}"{cls}>{html.escape(title)}</a>')
    return "\n".join(items)


def main() -> None:
    stamp = subprocess.run(
        ["git", "log", "-1", "--format=as of commit %h (%ad)", "--date=short"],
        capture_output=True, text=True, cwd=ROOT, check=True,
    ).stdout.strip()
    OUT.mkdir(parents=True, exist_ok=True)

    index_items = []
    for src, out_name, title in PAGES:
        src_path = ROOT / src
        body = render_markdown(src_path)
        page = TEMPLATE.format(
            title=html.escape(title), css=CSS, nav=nav_html(out_name),
            source=html.escape(src), stamp=html.escape(stamp), body=body,
        )
        (OUT / out_name).write_text(page, encoding="utf-8")
        index_items.append(
            f'<li><a href="{out_name}">{html.escape(title)}</a> '
            f"<small><code>{html.escape(src)}</code></small></li>"
        )
        print(f"built {out_name}")

    index_body = INDEX_INTRO + "\n".join(index_items) + "</ul>"
    index = TEMPLATE.format(
        title="Index", css=CSS, nav=nav_html("index.html"),
        source="scripts/build_site.py", stamp=html.escape(stamp),
        body=index_body,
    )
    (OUT / "index.html").write_text(index, encoding="utf-8")
    print(f"built index.html -> {OUT}")


if __name__ == "__main__":
    main()
