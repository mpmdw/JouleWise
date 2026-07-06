"""Static HTML report generator v1 (Slice 2J; decisions D-006, D-009, D-011).

``python3 -m joulewise report runs/ --output report/`` renders a read-only run
browser entirely from on-disk bundle artifacts:

- D-006: the dashboard is static HTML - an ``index.html`` table of runs plus a
  per-run page (metadata table, summary-metrics table, a power-trace chart with
  lifecycle/phase shading, and a failure box for failed/unsupported runs). No
  server, no JavaScript; open the files in a browser. Charts are rendered by
  matplotlib (Agg) to PNG.
- D-009: matplotlib is the first real dependency, isolated in the ``[analysis]``
  extra. The import is attempted up front; when it is missing the command fails
  with a :class:`ReportError` that names the extra and the install command,
  before any output is written (a lazy/late failure would leave a half-written
  report directory).
- D-011: a bundle directory is complete iff it has a parseable
  ``summary_metrics.json``. A directory without one means the harness died, not
  that a run failed; the report must surface it as ``incomplete`` rather than
  hide it, so such directories are listed in the index with that status and get
  no detail page.

The generator is pure over the on-disk artifacts and writes only under
``output_dir``. Its content is deterministic apart from the chart PNGs (whose
bytes matplotlib does not guarantee to be reproducible).

All bundle parsing and interpretation policy comes from
:class:`joulewise.bundle_read.BundleReader` (D-025, Slice 2N.7/2N.8): the
chart's summed curve is the reducer's summed curve (manifest rails only, D-027
alignment enforced), and the shaded measured window is the reducer's D-026
window - the chart can never display energy the summary excluded. When the
curve cannot be read (empty/missing manifest, rail misalignment, corrupt
trace), the run page notes the omission instead of inventing a fallback.
"""

from __future__ import annotations

import html
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from joulewise.bundle_read import BundleReader, BundleReadError
from joulewise.schemas import RunStatus

__all__ = ["ReportError", "generate_report"]

#: A chart needs at least this many points on the summed curve to draw a line.
_MIN_TRACE_ROWS = 2


class ReportError(Exception):
    """Raised when a report cannot be generated (e.g. matplotlib missing)."""


def _require_matplotlib() -> Any:
    """Import matplotlib with the Agg backend or raise a helpful ReportError.

    Attempted up front (D-009) so a missing ``[analysis]`` extra fails before
    any output is written. The Agg backend is selected explicitly *before*
    importing ``pyplot`` so the report never needs a display.
    """
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as pyplot
    except ImportError as exc:
        raise ReportError(
            "the report command requires matplotlib, which is part of the "
            "'[analysis]' extra. Install it with: "
            "pip install 'joulewise[analysis]'"
        ) from exc
    return pyplot


# ---------------------------------------------------------------------------
# Bundle model


@dataclass(frozen=True)
class _Bundle:
    """One discovered run directory and its parsed (or absent) summary."""

    run_id: str
    path: Path
    complete: bool
    config: dict[str, Any]
    metadata: dict[str, Any]
    summary: dict[str, Any]
    reader: BundleReader

    @property
    def status(self) -> str:
        if not self.complete:
            return "incomplete"
        return str(self.summary.get("status", "unknown"))

    @property
    def target(self) -> str:
        target = self.config.get("hardware_target")
        if isinstance(target, dict) and isinstance(target.get("id"), str):
            return target["id"]
        return "-"

    @property
    def model(self) -> str:
        model = self.config.get("model")
        if isinstance(model, dict) and isinstance(model.get("name"), str):
            return model["name"]
        return "-"

    @property
    def energy_token_j(self) -> float | None:
        return _as_float(self.summary.get("energy_token_j"))

    @property
    def ttft_s(self) -> float | None:
        return _as_float(self.summary.get("ttft_s"))

    @property
    def failure_reason(self) -> str | None:
        value = self.summary.get("failure_reason")
        return value if isinstance(value, str) else None

    @property
    def failure_message(self) -> str | None:
        value = self.summary.get("failure_message")
        return value if isinstance(value, str) else None

    @property
    def is_failure(self) -> bool:
        return self.status in {RunStatus.FAILED.value, RunStatus.UNSUPPORTED.value}


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _discover_bundles(runs_dir: Path) -> list[_Bundle]:
    """Return the run bundles under ``runs_dir`` sorted by run id (D-011).

    Bundle discovery is the immediate subdirectories of ``runs_dir``, EXCLUDING
    ``runs_dir/experiments`` (which holds manifests, not bundles). A directory
    with a parseable ``summary_metrics.json`` is a complete bundle; one without
    is ``incomplete`` (harness died) and still listed so it is never hidden.
    """
    bundles: list[_Bundle] = []
    for child in sorted(runs_dir.iterdir(), key=lambda p: p.name):
        if not child.is_dir() or child.name == "experiments":
            continue
        reader = BundleReader(child)
        bundles.append(
            _Bundle(
                run_id=child.name,
                path=child,
                complete=reader.is_complete(),
                config=reader.raw_config() or {},
                metadata=reader.raw_metadata() or {},
                summary=reader.raw_summary() or {},
                reader=reader,
            )
        )
    return bundles


# ---------------------------------------------------------------------------
# Power-trace chart

#: Phase-span shading colors keyed by phase name (others fall back to grey).
_PHASE_COLORS = {"prefill": "#f4a259", "decode": "#5b8e7d"}


def _render_chart(pyplot: Any, bundle: _Bundle, output_path: Path) -> bool:
    """Render the power-trace chart PNG for ``bundle``; return whether it drew.

    A line plot of the reader's summed power curve vs time - exactly the curve
    the reducer integrated (D-025/2N.7), so the chart never shows energy the
    summary excluded. The D-026 measured window and the ``prefill``/``decode``
    phase spans are shaded with labels. Returns ``False`` (drawing nothing)
    when the curve cannot be read (missing trace, empty manifest, D-027
    misalignment, corrupt rows/events) or has fewer than two summed points -
    the caller then notes the omission.
    """
    try:
        curve = bundle.reader.summed_curve()
    except BundleReadError:
        return False
    if len(curve) < _MIN_TRACE_ROWS:
        return False

    try:
        measured = bundle.reader.measured_window()
        phase_windows = bundle.reader.phase_windows()
    except BundleReadError:
        measured = None
        phase_windows = {}
    times = [point.t for point in curve]
    powers = [point.power_w for point in curve]

    figure, axes = pyplot.subplots(figsize=(9, 4))
    try:
        axes.plot(times, powers, color="#264653", linewidth=1.5, label="summed power")

        if measured is not None:
            axes.axvspan(
                measured.start_s,
                measured.end_s,
                color="#2a9d8f",
                alpha=0.10,
                label="measured_run",
            )

        seen_labels: set[str] = set()
        for phase, intervals in phase_windows.items():
            for interval in intervals:
                color = _PHASE_COLORS.get(phase, "#b0b0b0")
                label = phase if phase not in seen_labels else None
                seen_labels.add(phase)
                axes.axvspan(
                    interval.start_s, interval.end_s, color=color, alpha=0.25, label=label
                )

        axes.set_xlabel("time (s, epoch UTC)")
        axes.set_ylabel("summed power (W)")
        axes.set_title(f"power trace: {bundle.run_id}")
        axes.legend(loc="upper right", fontsize="small")
        figure.tight_layout()
        figure.savefig(output_path, dpi=100)
    finally:
        pyplot.close(figure)
    return True


# ---------------------------------------------------------------------------
# HTML rendering (inline CSS, no JavaScript)


_CSS = """
body { font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
       margin: 2rem; color: #222; }
h1, h2 { color: #1d3557; }
table { border-collapse: collapse; margin: 1rem 0; width: 100%; }
th, td { border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left;
         vertical-align: top; }
th { background: #f1f4f8; }
tr:nth-child(even) td { background: #fafbfc; }
code { font-family: SFMono-Regular, Consolas, monospace; }
a { color: #1d6fb8; }
.status-succeeded { color: #2a7d2a; font-weight: 600; }
.status-failed { color: #b00020; font-weight: 600; }
.status-unsupported { color: #b06a00; font-weight: 600; }
.status-incomplete { color: #777; font-weight: 600; font-style: italic; }
.failure-box { border: 2px solid #b00020; background: #fff0f1; border-radius: 6px;
               padding: 1rem 1.25rem; margin: 1rem 0; }
.failure-box h2 { color: #b00020; margin-top: 0; }
.note { color: #666; font-style: italic; }
img.chart { max-width: 100%; border: 1px solid #ddd; }
""".strip()


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value))


def _status_class(status: str) -> str:
    return f"status-{_esc(status)}"


def _format_number(value: float | None, digits: int = 6) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}g}"


def _page(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        f"<title>{_esc(title)}</title>\n"
        f"<style>\n{_CSS}\n</style>\n"
        "</head>\n<body>\n"
        f"{body}\n"
        "</body>\n</html>\n"
    )


def _render_index(bundles: list[_Bundle]) -> str:
    rows: list[str] = []
    for bundle in bundles:
        if bundle.complete:
            link = f'<a href="run/{_esc(bundle.run_id)}.html">{_esc(bundle.run_id)}</a>'
        else:
            link = _esc(bundle.run_id)
        rows.append(
            "<tr>"
            f"<td><code>{_esc(bundle.run_id)}</code></td>"
            f"<td>{_esc(bundle.target)}</td>"
            f"<td>{_esc(bundle.model)}</td>"
            f'<td class="{_status_class(bundle.status)}">{_esc(bundle.status)}</td>'
            f"<td>{_format_number(bundle.energy_token_j)}</td>"
            f"<td>{_format_number(bundle.ttft_s)}</td>"
            f"<td>{link}</td>"
            "</tr>"
        )
    table = (
        "<table>\n<thead><tr>"
        "<th>run id</th><th>target</th><th>model</th><th>status</th>"
        "<th>energy/token (J)</th><th>TTFT (s)</th><th>detail</th>"
        "</tr></thead>\n<tbody>\n"
        + "\n".join(rows)
        + "\n</tbody>\n</table>"
    )
    body = (
        "<h1>JouleWise run report</h1>\n"
        f"<p>{len(bundles)} run director"
        f"{'y' if len(bundles) == 1 else 'ies'} discovered.</p>\n"
        + table
    )
    return _page("JouleWise run report", body)


def _flatten(value: Any, prefix: str = "") -> list[tuple[str, str]]:
    """Flatten nested dicts/lists into ``(dotted.key, value)`` pairs, sorted."""
    pairs: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key in value:
            child_prefix = f"{prefix}.{key}" if prefix else str(key)
            pairs.extend(_flatten(value[key], child_prefix))
    elif isinstance(value, list):
        if not value:
            pairs.append((prefix, "[]"))
        for index, item in enumerate(value):
            pairs.extend(_flatten(item, f"{prefix}[{index}]"))
    else:
        pairs.append((prefix, "" if value is None else str(value)))
    return pairs


def _key_value_table(pairs: list[tuple[str, str]]) -> str:
    rows = "\n".join(
        f"<tr><td><code>{_esc(key)}</code></td><td>{_esc(val)}</td></tr>"
        for key, val in pairs
    )
    return (
        "<table>\n<thead><tr><th>key</th><th>value</th></tr></thead>\n"
        f"<tbody>\n{rows}\n</tbody>\n</table>"
    )


def _render_run_page(bundle: _Bundle, chart_rel: str | None) -> str:
    parts: list[str] = [f"<h1>Run <code>{_esc(bundle.run_id)}</code></h1>"]
    parts.append(
        f'<p>status: <span class="{_status_class(bundle.status)}">'
        f"{_esc(bundle.status)}</span></p>"
    )
    parts.append('<p><a href="../index.html">&larr; back to index</a></p>')

    if bundle.is_failure:
        parts.append(
            '<div class="failure-box">\n'
            "<h2>Run failure</h2>\n"
            f"<p><strong>reason:</strong> {_esc(bundle.failure_reason or '-')}</p>\n"
            f"<p><strong>message:</strong> {_esc(bundle.failure_message or '-')}</p>\n"
            "</div>"
        )

    parts.append("<h2>Power trace</h2>")
    if chart_rel is not None:
        parts.append(
            f'<img class="chart" src="{_esc(chart_rel)}" '
            f'alt="power trace for {_esc(bundle.run_id)}">'
        )
    else:
        parts.append(
            '<p class="note">No power-trace chart: this bundle has no readable '
            "summed power curve (missing power_trace.csv, fewer than two "
            "in-manifest samples, an empty rail manifest, or misaligned rail "
            "rows) - the chart only ever shows the curve the reducer "
            "integrated.</p>"
        )

    parts.append("<h2>Metadata</h2>")
    parts.append(_key_value_table(_flatten(bundle.metadata)))

    parts.append("<h2>Summary metrics</h2>")
    parts.append(_key_value_table(_flatten(bundle.summary)))

    return _page(f"Run {bundle.run_id}", "\n".join(parts))


# ---------------------------------------------------------------------------
# Top-level entry point


def generate_report(runs_dir: Path, output_dir: Path) -> Path:
    """Render the static run browser for ``runs_dir`` under ``output_dir``.

    Returns the path to the written ``index.html``. Raises :class:`ReportError`
    when ``runs_dir`` is not a directory or when matplotlib (the ``[analysis]``
    extra) is missing - the matplotlib check happens up front, before any output
    is written (D-006/D-009).
    """
    runs_dir = Path(runs_dir)
    output_dir = Path(output_dir)
    if not runs_dir.is_dir():
        raise ReportError(f"runs directory does not exist: {runs_dir}")

    # Fail before writing anything when the analysis extra is missing.
    pyplot = _require_matplotlib()

    bundles = _discover_bundles(runs_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    run_dir = output_dir / "run"
    run_dir.mkdir(parents=True, exist_ok=True)

    for bundle in bundles:
        if not bundle.complete:
            continue
        chart_name = f"{bundle.run_id}.png"
        drew_chart = _render_chart(pyplot, bundle, run_dir / chart_name)
        chart_rel = chart_name if drew_chart else None
        (run_dir / f"{bundle.run_id}.html").write_text(
            _render_run_page(bundle, chart_rel)
        )

    index_path = output_dir / "index.html"
    index_path.write_text(_render_index(bundles))
    return index_path
