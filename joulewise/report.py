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
"""

from __future__ import annotations

import csv
import html
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from joulewise.schemas import RunStatus

__all__ = ["ReportError", "generate_report"]

#: The exact ``power_trace.csv`` header (D-018); the chart reader pins it.
_RAIL_COLUMN = "rail"
_TIMESTAMP_COLUMN = "timestamp_s"
_POWER_COLUMN = "power_w"

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


def _load_json_or_none(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None


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
        summary = _load_json_or_none(child / "summary_metrics.json")
        complete = isinstance(summary, dict)
        config = _load_json_or_none(child / "config.json")
        metadata = _load_json_or_none(child / "metadata.json")
        bundles.append(
            _Bundle(
                run_id=child.name,
                path=child,
                complete=complete,
                config=config if isinstance(config, dict) else {},
                metadata=metadata if isinstance(metadata, dict) else {},
                summary=summary if isinstance(summary, dict) else {},
            )
        )
    return bundles


# ---------------------------------------------------------------------------
# Power-trace chart


def _rail_manifest(metadata: dict[str, Any]) -> list[str]:
    device = metadata.get("device")
    if isinstance(device, dict):
        manifest = device.get("rail_manifest")
        if isinstance(manifest, list):
            return [str(rail) for rail in manifest]
    return []


def _summed_trace(rows: list[dict[str, str]], rail_manifest: list[str]) -> list[tuple[float, float]]:
    """Sum ``power_w`` per timestamp over the manifest rails (D-018).

    When the manifest is empty (or no row matches it) every present rail is
    summed instead, so a chart still renders rather than collapsing to nothing.
    """
    manifest = set(rail_manifest)
    totals: dict[float, float] = {}
    matched = False
    for row in rows:
        rail = row.get(_RAIL_COLUMN) or ""
        if manifest and rail not in manifest:
            continue
        try:
            timestamp_s = float(row[_TIMESTAMP_COLUMN])
            power_w = float(row[_POWER_COLUMN])
        except (KeyError, ValueError, TypeError):
            continue
        totals[timestamp_s] = totals.get(timestamp_s, 0.0) + power_w
        matched = True
    if not matched and manifest:
        return _summed_trace(rows, [])
    return [(t, totals[t]) for t in sorted(totals)]


def _load_trace_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    try:
        with path.open(newline="") as handle:
            return list(csv.DictReader(handle))
    except OSError:
        return []


def _stage_span(events: list[dict[str, Any]], phase: str) -> tuple[float, float] | None:
    """First ``stage_started`` / last ``stage_completed`` timestamps for ``phase``."""
    start: float | None = None
    end: float | None = None
    for event in events:
        if event.get("phase") != phase:
            continue
        event_type = event.get("event_type")
        timestamp = _as_float(event.get("timestamp_s"))
        if timestamp is None:
            continue
        if event_type == "stage_started" and start is None:
            start = timestamp
        elif event_type == "stage_completed":
            end = timestamp
    if start is None or end is None:
        return None
    return (start, end)


def _phase_spans(events: list[dict[str, Any]]) -> list[tuple[str, float, float]]:
    """Pair ``phase_start``/``phase_end`` events by phase name, in order."""
    open_starts: dict[str, list[float]] = {}
    spans: list[tuple[str, float, float]] = []
    for event in events:
        phase = event.get("phase")
        if not isinstance(phase, str):
            continue
        timestamp = _as_float(event.get("timestamp_s"))
        if timestamp is None:
            continue
        event_type = event.get("event_type")
        if event_type == "phase_start":
            open_starts.setdefault(phase, []).append(timestamp)
        elif event_type == "phase_end":
            starts = open_starts.get(phase)
            if starts:
                spans.append((phase, starts.pop(0), timestamp))
    return spans


def _load_events(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    events: list[dict[str, Any]] = []
    try:
        text = path.read_text()
    except OSError:
        return []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            events.append(record)
    return events


#: Phase-span shading colors keyed by phase name (others fall back to grey).
_PHASE_COLORS = {"prefill": "#f4a259", "decode": "#5b8e7d"}


def _render_chart(pyplot: Any, bundle: _Bundle, output_path: Path) -> bool:
    """Render the power-trace chart PNG for ``bundle``; return whether it drew.

    A line plot of summed power vs time. The ``measured_run`` stage span and the
    ``prefill``/``decode`` phase spans (from ``events.jsonl``) are shaded with
    labels. Returns ``False`` (drawing nothing) when no trace exists or it has
    fewer than two summed points - the caller then notes the omission.
    """
    rows = _load_trace_rows(bundle.path / "power_trace.csv")
    curve = _summed_trace(rows, _rail_manifest(bundle.metadata))
    if len(curve) < _MIN_TRACE_ROWS:
        return False

    events = _load_events(bundle.path / "events.jsonl")
    times = [point[0] for point in curve]
    powers = [point[1] for point in curve]

    figure, axes = pyplot.subplots(figsize=(9, 4))
    try:
        axes.plot(times, powers, color="#264653", linewidth=1.5, label="summed power")

        measured = _stage_span(events, "measured_run")
        if measured is not None:
            axes.axvspan(
                measured[0],
                measured[1],
                color="#2a9d8f",
                alpha=0.10,
                label="measured_run",
            )

        seen_labels: set[str] = set()
        for phase, start_s, end_s in _phase_spans(events):
            color = _PHASE_COLORS.get(phase, "#b0b0b0")
            label = phase if phase not in seen_labels else None
            seen_labels.add(phase)
            axes.axvspan(start_s, end_s, color=color, alpha=0.25, label=label)

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
            '<p class="note">No power-trace chart: this bundle has no '
            "power_trace.csv with at least two samples.</p>"
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
