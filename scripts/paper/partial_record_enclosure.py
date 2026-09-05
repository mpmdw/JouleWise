#!/usr/bin/env python3
"""Derive a desk-only partial-record enclosure from one run bundle.

The phase windows are fixed by the authenticated bundle; this command has no
window-selection argument and never composes its diagnostic into any bound.
It uses the reducer's shared trace/window
read path (`joulewise/bundle_read.py:352` and `joulewise/bundle_read.py:576`)
and recomputes each point with the reducer's own integration function
(`joulewise/reduce.py:167`).

Usage:
    python3 scripts/paper/partial_record_enclosure.py RUN_BUNDLE
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import stat
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.authentication_io import (  # noqa: E402
    V2AuthenticationInputError,
    V2AuthenticationReadSession,
    active_v2_authentication_session,
    sha256_authentication_input,
)
from joulewise.bundle_read import (  # noqa: E402
    BundleReadError,
    BundleReader,
    TracePoint,
    Window,
)
from joulewise.cli import validate_bundle  # noqa: E402
from joulewise.reduce import _integrate  # noqa: E402


BASIS = "nonnegative_partial_record_enclosure.v1"
FIXED_WINDOW_SCOPE = "fixed_phase_windows_from_authenticated_bundle.v1"


class EnclosureRefusal(ValueError):
    """Fail-closed refusal carrying a stable machine-readable reason."""

    def __init__(self, reason: str, detail: str) -> None:
        self.reason = reason
        self.detail = detail
        super().__init__(f"{reason}: {detail}")


def _union_windows(windows: Iterable[Window]) -> list[Window]:
    ordered = sorted(windows, key=lambda item: (item.start_s, item.end_s))
    union: list[Window] = []
    for window in ordered:
        if not union or window.start_s > union[-1].end_s:
            union.append(window)
            continue
        union[-1] = Window(
            start_s=union[-1].start_s,
            end_s=max(union[-1].end_s, window.end_s),
        )
    return union


def _validate_interval_curve(curve: list[TracePoint]) -> None:
    if not curve:
        raise EnclosureRefusal("power_records_unavailable", "power curve is empty")
    if any(
        point.support_start_s is None or point.support_end_s is None
        for point in curve
    ):
        raise EnclosureRefusal(
            "point_supported_records_unsupported",
            "every power record must carry interval_start_s and interval_end_s",
        )
    for point in curve:
        if not math.isfinite(point.power_w):
            raise EnclosureRefusal(
                "nonfinite_reported_power",
                "an interval record carries non-finite reported power",
            )
        if point.power_w < 0.0:
            raise EnclosureRefusal(
                "negative_reported_power",
                "an interval record carries negative reported power",
            )


def enclose_phase(
    phase: str,
    contributions: Iterable[tuple[list[TracePoint], list[Window]]],
    *,
    inputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Enclose one fixed phase, counting each overlapping record once."""

    point_terms: list[float] = []
    inside_terms: list[float] = []
    straddling_terms: list[float] = []
    straddling_record_count = 0
    contribution_count = 0
    for curve, raw_windows in contributions:
        contribution_count += 1
        _validate_interval_curve(curve)
        windows = _union_windows(raw_windows)
        point_terms.extend(
            _integrate(curve, window.start_s, window.end_s)
            for window in windows
        )
        for point in curve:
            start_s = float(point.support_start_s)  # validated above
            end_s = float(point.support_end_s)  # validated above
            record_energy_j = point.power_w * (end_s - start_s)
            fully_inside = any(
                window.start_s <= start_s and end_s <= window.end_s
                for window in windows
            )
            if fully_inside:
                inside_terms.append(record_energy_j)
                continue
            overlaps = any(
                min(end_s, window.end_s) > max(start_s, window.start_s)
                for window in windows
            )
            if overlaps:
                straddling_terms.append(record_energy_j)
                straddling_record_count += 1
    if contribution_count == 0:
        raise EnclosureRefusal(
            "phase_windows_unrecorded", f"phase {phase!r} has no fixed windows"
        )
    lower_j = math.fsum(inside_terms)
    straddling_energy_j = math.fsum(straddling_terms)
    return {
        "point_j": math.fsum(point_terms),
        "lower_j": lower_j,
        "upper_j": math.fsum((lower_j, straddling_energy_j)),
        "straddling_record_count": straddling_record_count,
        "straddling_energy_j": straddling_energy_j,
        "basis": BASIS,
        "scope": FIXED_WINDOW_SCOPE,
        "inputs": inputs or {},
    }


def _bundle_sha256_census(bundle: Path) -> list[dict[str, Any]]:
    if bundle.is_symlink() or not bundle.is_dir():
        raise EnclosureRefusal(
            "bundle_not_real_directory", "bundle must be a non-symlink directory"
        )
    census: list[dict[str, Any]] = []
    try:
        candidates = sorted(
            bundle.rglob("*"), key=lambda item: item.relative_to(bundle).as_posix()
        )
    except OSError as exc:
        raise EnclosureRefusal("bundle_census_failed", str(exc)) from exc
    for candidate in candidates:
        relative = candidate.relative_to(bundle).as_posix()
        try:
            mode = candidate.lstat().st_mode
        except OSError as exc:
            raise EnclosureRefusal("bundle_census_failed", f"{relative}: {exc}") from exc
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise EnclosureRefusal(
                "bundle_census_nonregular_member", relative
            )
        try:
            digest = sha256_authentication_input(
                candidate, label=f"partial-record enclosure input {relative}"
            )
        except OSError as exc:
            raise EnclosureRefusal("bundle_census_failed", f"{relative}: {exc}") from exc
        census.append(
            {
                "path": relative,
                "sha256": digest,
                "size_bytes": candidate.stat().st_size,
            }
        )
    if not census:
        raise EnclosureRefusal("bundle_census_empty", "bundle has no regular files")
    return census


def _load_contributions(
    reader: BundleReader,
) -> dict[str, list[tuple[list[TracePoint], list[Window]]]]:
    contributions: dict[str, list[tuple[list[TracePoint], list[Window]]]] = {}
    if reader.is_event_v2():
        grouped: dict[tuple[str, str], list[Window]] = {}
        for (source, _request, phase, _ordinal), window in (
            reader.request_phase_windows().items()
        ):
            grouped.setdefault((source, phase), []).append(window)
        for (source, phase), windows in sorted(grouped.items()):
            contributions.setdefault(phase, []).append(
                (reader.source_curve(source), _union_windows(windows))
            )
        return contributions

    curve = reader.summed_curve()
    for phase, windows in sorted(reader.phase_windows().items()):
        contributions[phase] = [(curve, _union_windows(windows))]
    return contributions


def _derive_bundle_authenticated(bundle: Path) -> dict[str, dict[str, Any]]:
    """Strict-validate and derive diagnostics without writing bundle bytes."""

    bundle = Path(bundle)
    reader = BundleReader(bundle)
    try:
        # Force the same typed config, metadata, event, trace, and window reads
        # used by reduction before accepting this bundle as an input.
        reader.config()
        reader.metadata()
        reader.events()
        contributions = _load_contributions(reader)
        for groups in contributions.values():
            for curve, _windows in groups:
                _validate_interval_curve(curve)
    except BundleReadError as exc:
        # BundleReadError exposes no structured reason attribute; retain the
        # nonfinite-power classification from its current diagnostic text.
        detail = str(exc)
        if "power_w" in detail and "finite" in detail:
            reason = "nonfinite_reported_power"
        else:
            reason = "bundle_read_failed"
        raise EnclosureRefusal(reason, detail) from exc

    problems = validate_bundle(bundle, strict=True)
    if problems:
        raise EnclosureRefusal(
            "bundle_strict_validation_failed", "; ".join(problems)
        )
    summary = reader.raw_summary()
    recorded = summary.get("phase_energy_j") if isinstance(summary, dict) else None
    if not isinstance(recorded, dict) or set(recorded) != set(contributions):
        raise EnclosureRefusal(
            "phase_summary_window_mismatch",
            "summary phase_energy_j keys do not equal fixed phase-window keys",
        )

    inputs = {"bundle_sha256_census": _bundle_sha256_census(bundle)}
    return {
        phase: enclose_phase(phase, contributions[phase], inputs=inputs)
        for phase in sorted(contributions)
    }


def derive_bundle(bundle: Path) -> dict[str, dict[str, Any]]:
    """Run the complete read and census in one digest-stable auth session."""

    if active_v2_authentication_session() is not None:
        return _derive_bundle_authenticated(bundle)
    try:
        with V2AuthenticationReadSession():
            return _derive_bundle_authenticated(bundle)
    except V2AuthenticationInputError as exc:
        raise EnclosureRefusal(exc.reason, exc.detail) from exc


def derive_synthetic_p1() -> dict[str, Any]:
    """Reproduce the labelled P1 illustration, without authenticating a bundle.

    This separate entry never supplies a measured result. Each endpoint moves
    independently by up to 10 ms for the held-average timing envelope; the
    nonnegative enclosure uses only the original, fixed window.
    """
    records = [
        {"start_s": (5 + i) / 10, "end_s": (6 + i) / 10, "power_w": 10.0}
        for i in range(10)
    ]
    curve = [
        TracePoint(t=r["end_s"], power_w=r["power_w"],
                   support_start_s=r["start_s"], support_end_s=r["end_s"])
        for r in records
    ]
    inputs = {
        "records": records,
        "window_s": [0.55, 1.45],
        "independent_edge_shift_s": [-0.01, 0.01],
    }
    result = enclose_phase("SYNTHETIC P1", [(curve, [Window(0.55, 1.45)])])
    # Do not inherit the authenticated-bundle scope label from enclose_phase.
    result["scope"] = "synthetic_p1_fixed_window.v1"
    result.pop("inputs")
    corners = [
        {"window_s": [start, end], "point_j": _integrate(curve, start, end)}
        for start in (0.54, 0.56) for end in (1.44, 1.46)
    ]
    result["timing_corners"] = corners
    result["timing_envelope_j"] = [
        min(c["point_j"] for c in corners), max(c["point_j"] for c in corners)
    ]
    script = Path(__file__).read_bytes()
    return {
        "schema": "synthetic_p1_partial_record_figure.v1",
        "label": "SYNTHETIC P1",
        "claim_bearing": False,
        "inputs": inputs,
        "outputs": result,
        "producer": {
            "path": "scripts/paper/partial_record_enclosure.py",
            "entry": "derive_synthetic_p1",
            "sha256": hashlib.sha256(script).hexdigest(),
            "size_bytes": len(script),
        },
    }


def synthetic_p1_svg(data: dict[str, Any]) -> str:
    """Draw P1 from its derived records and energies (stdlib-only SVG)."""
    result = data["outputs"]
    time_x = lambda t: 130 + (t - 0.5) * 800
    energy_x = lambda j: 330 + (j - 8) * 250
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="560" '
        'viewBox="0 0 1060 560" role="img" aria-labelledby="title desc">',
        '<title id="title">Figure A1. SYNTHETIC P1 partial-record enclosure</title>',
        '<desc id="desc">Ten 100 ms records reporting 10 W, window 0.55 to '
        '1.45 s. Point 9.0 J; timing envelope 8.8 to 9.2 J; nonnegative '
        'fixed-window enclosure 8 to 10 J. Not measured evidence.</desc>',
        '<rect width="1060" height="560" fill="white"/>',
        '<g font-family="Arial, sans-serif" font-size="17" fill="#17232d">',
        '<text x="40" y="36" font-size="23" font-weight="bold">'
        'Figure A1 · SYNTHETIC P1</text>',
        '<text x="40" y="67">A · Reported intervals: 100 ms × 10 W = 1 J each</text>',
    ]
    start, end = data["inputs"]["window_s"]
    for i, record in enumerate(data["inputs"]["records"], 1):
        inside = start <= record["start_s"] and record["end_s"] <= end
        color = "#c5dfeb" if inside else "#f4d09b"
        x = time_x(record["start_s"])
        width = time_x(record["end_s"]) - x
        parts += [
            f'<rect x="{x:g}" y="100" width="{width:g}" height="70" '
            f'fill="{color}" stroke="#17232d"/>',
            f'<text x="{x + width / 2:g}" y="142" text-anchor="middle">R{i}</text>',
        ]
    for edge in (start, end):
        x = time_x(edge)
        parts += [
            f'<line x1="{x:g}" y1="85" x2="{x:g}" y2="210" '
            'stroke="#653b86" stroke-width="2" stroke-dasharray="6 4"/>',
            f'<text x="{x:g}" y="235" text-anchor="middle" fill="#653b86">{edge:g}</text>',
        ]
    parts += [
        f'<line x1="{time_x(start):g}" y1="88" x2="{time_x(end):g}" y2="88" '
        'stroke="#653b86" stroke-width="4"/>',
        '<text x="530" y="205" text-anchor="middle" fill="#653b86">'
        'Fixed window [0.55, 1.45] s</text>',
        '<line x1="130" y1="255" x2="930" y2="255" stroke="#17232d"/>',
    ]
    for i in range(11):
        t = (5 + i) / 10
        x = time_x(t)
        parts += [f'<line x1="{x:g}" y1="250" x2="{x:g}" y2="260" stroke="#17232d"/>',
                  f'<text x="{x:g}" y="280" text-anchor="middle">{t:.1f}</text>']
    parts += [
        '<text x="970" y="260">Time (s)</text>',
        '<text x="40" y="324">B · Energy assigned to the window</text>',
    ]
    lo, hi = result["lower_j"], result["upper_j"]
    tlo, thi = result["timing_envelope_j"]
    for y, label, left, right, color in (
        (365, f'Nonnegative [{lo:g}, {hi:g}] J', lo, hi, '#b56b13'),
        (410, f'Timing [{tlo:.1f}, {thi:.1f}] J', tlo, thi, '#187295'),
    ):
        parts.append(f'<text x="40" y="{y + 6}">{label}</text>')
        parts.append(f'<line x1="{energy_x(left):g}" y1="{y}" x2="{energy_x(right):g}" '
                     f'y2="{y}" stroke="{color}" stroke-width="7"/>')
        for value in (left, right):
            x = energy_x(value)
            parts.append(f'<line x1="{x:g}" y1="{y-10}" x2="{x:g}" y2="{y+10}" '
                         f'stroke="{color}" stroke-width="2"/>')
    point = result["point_j"]
    parts += [
        f'<text x="40" y="461">Point {point:.1f} J</text>',
        f'<circle cx="{energy_x(point):g}" cy="455" r="7" fill="#17232d"/>',
        '<line x1="305" y1="490" x2="855" y2="490" stroke="#17232d"/>',
    ]
    for value in (8, 8.8, 9, 9.2, 10):
        x = energy_x(value)
        parts += [f'<line x1="{x:g}" y1="485" x2="{x:g}" y2="495" stroke="#17232d"/>',
                  f'<text x="{x:g}" y="517" text-anchor="middle">{value:g}</text>']
    parts += ['<text x="890" y="497">Energy (J)</text>',
              '<text x="40" y="549" font-size="15">SYNTHETIC · Fixed-window allocation diagnostic; never composed into any bound.</text>',
              '</g></svg>']
    return "\n".join(parts) + "\n"


def write_synthetic_p1_figure(svg_path: Path, json_path: Path) -> None:
    """Write the appendix illustration and exact floating-point replay inputs."""
    data = derive_synthetic_p1()
    svg = synthetic_p1_svg(data)
    data["figure"] = {"sha256": hashlib.sha256(svg.encode("utf-8")).hexdigest()}
    svg_path.write_text(svg, encoding="utf-8")
    json_path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + "\n",
                         encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path, help="strict-valid run bundle")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = derive_bundle(args.bundle)
    except EnclosureRefusal as exc:
        print(
            json.dumps(
                {"status": "refused", "reason": exc.reason, "detail": exc.detail},
                sort_keys=True,
                ensure_ascii=False,
                allow_nan=False,
            ),
            file=sys.stderr,
        )
        return 2
    print(
        json.dumps(
            result,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
