#!/usr/bin/env python3
"""Build the library half of docs/site/ — styled HTML renderings of the
front-facing Markdown docs, matching the hand-designed site pages.

The designed pages (index/results/process/research.html + style.css +
fonts/) are hand-authored and NOT touched by this script; it generates
library.html and one page per source doc, all wrapped in the shared
"instrument" design system (style.css).

Renders Markdown via `npx --yes marked --gfm` (Node). Docs-only tooling;
deliberately independent of the measurement venv.

Usage: python3 scripts/build_site.py
"""

from __future__ import annotations

import html
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "site"

# (source path, output name, card title, one-line description)
PAGES = [
    ("README.md", "readme.html", "README",
     "What the repo is and how to run the mock path end to end."),
    ("PROJECT_STATUS.md", "project_status.html", "Project Status",
     "The advisor-facing monitoring document — thesis, status, plan, process."),
    ("docs/orchestration.md", "orchestration.html", "The Orchestration Process",
     "The multi-model loop, the artifact system, and how the topology evolved."),
    ("AGENT_PLAN.md", "agent_plan.html", "Agent Plan",
     "Phase index and per-phase implementation plans."),
    ("RUN_STATE.md", "run_state.html", "Run State",
     "The live intake pointer: current state, next action."),
    ("TASK_QUEUE.md", "task_queue.html", "Task Queue",
     "Ranked live queue with machine-state lanes."),
    ("docs/decision_log.md", "decision_log.html", "Decision Log",
     "36 binding design decisions with alternatives and revisit conditions."),
    ("docs/council_log.md", "council_log.html", "Council Log",
     "Deliberation record C-001…C-010: positions, dissents, adjudications."),
    ("docs/milestones.md", "milestones.html", "Milestones",
     "Dates, heartbeats, and the academic calendar mapping."),
    ("docs/risk_register.md", "risk_register.html", "Risk Register",
     "Live risks with triggers and mitigation states."),
    ("docs/run_reports/2026-07-07-resume-merge-session.md",
     "latest_run_report.html", "Latest Run Report",
     "The resume+merge session: outcomes, catch record, calibration ledger."),
]

NAV = """<header class="site">
  <nav class="nav">
    <a class="brand" href="index.html"><span class="dot"></span>JOULEWISE</a>
    <div class="links">
      <a href="index.html">Story</a>
      <a href="results.html">Results</a>
      <a href="process.html">Process</a>
      <a href="research.html">Research</a>
      <a href="library.html"{lib_active}>Library</a>
    </div>
  </nav>
</header>"""

FOOTER = """<footer class="site">
  <div class="inner">
    <span>JouleWise · github.com/mpmdw/JouleWise</span>
    <span>{stamp} · regenerate: <span class="mono">python3 scripts/build_site.py</span></span>
  </div>
</footer>"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — JouleWise</title>
<link rel="stylesheet" href="style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
</head>
<body>
{nav}
<main>
<div class="doc-wrap">
<p class="doc-meta"><a href="library.html">← library</a> · rendered from <code>{source}</code> · {stamp}</p>
{body}
</div>
</main>
{footer}
</body>
</html>
"""

LIBRARY_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Library — JouleWise</title>
<link rel="stylesheet" href="style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>⚡</text></svg>">
</head>
<body>
{nav}
<main>
<div class="hero" style="padding-bottom:6px">
  <div class="kicker">Primary sources</div>
  <h1 style="font-size:clamp(36px,5vw,56px)">The library.</h1>
  <p class="lede">Every claim on this site traces back to these documents —
  rendered here for reading, canonical as Markdown in the repository.</p>
</div>
<section class="band tight">
  <div class="lib-grid">
{cards}
  </div>
</section>
</main>
{footer}
</body>
</html>
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


def main() -> None:
    stamp = subprocess.run(
        ["git", "log", "-1", "--format=as of commit %h (%ad)", "--date=short"],
        capture_output=True, text=True, cwd=ROOT, check=True,
    ).stdout.strip()
    OUT.mkdir(parents=True, exist_ok=True)
    footer = FOOTER.format(stamp=html.escape(stamp))

    cards = []
    for src, out_name, title, desc in PAGES:
        body = render_markdown(ROOT / src)
        page = PAGE_TEMPLATE.format(
            title=html.escape(title),
            nav=NAV.format(lib_active=' class="active"'),
            source=html.escape(src), stamp=html.escape(stamp),
            body=body, footer=footer,
        )
        (OUT / out_name).write_text(page, encoding="utf-8")
        cards.append(
            f'    <a class="lib-card" href="{out_name}">'
            f'<div class="t">{html.escape(title)}</div>'
            f'<div class="d">{html.escape(desc)}</div></a>'
        )
        print(f"built {out_name}")

    library = LIBRARY_TEMPLATE.format(
        nav=NAV.format(lib_active=' class="active"'),
        cards="\n".join(cards), footer=footer,
    )
    (OUT / "library.html").write_text(library, encoding="utf-8")
    print(f"built library.html -> {OUT}")


if __name__ == "__main__":
    main()
