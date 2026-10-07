#!/usr/bin/env python3
"""Build the block-5 schematic figures B-S2, B-S4 and B-S5 of Paper B.

    python3 -B docs/paper/figures/b5/build_boundary_survivors_gate.py           # write the three SVGs
    python3 -B docs/paper/figures/b5/build_boundary_survivors_gate.py --check   # compare; exit 1 on a difference

- B-S2, ``figB_S2_measurement_boundary.svg``: where each instrument reads, the claim boundary and the
  whole-machine boundary of the meter cross-check (registration section 5.8).
- B-S4, ``figB_S4_reference_survivors.svg``: the reference drift check run on the reference members that
  survive, with the registration's synthetic worked example (registration section 0.12).
- B-S5, ``figB_S5_frequency_gate.svg``: the clock frequency gate, computed from the registered constants
  (registration sections 0.14, 4.2 and 4.3).

No figure reads a measurement file.  Every number drawn is either a registered design value listed in
``REGISTERED`` with the place it was read, or arithmetic done in this file on those values and on the
synthetic inputs in ``SYNTHETIC``.  The arithmetic is written out here from the registration's text and
does not import the project's code; ``tests/test_paper_b_figures_s2_s4_s5.py`` compares it with
the production functions and re-reads the registered values from the registration and from the code.

Every shape and every piece of text is drawn inside one named element, ``<g data-element="...">``; the
drawing helpers refuse to draw outside one.  ``captions-s2-s4-s5.md`` explains each name, and the test
checks that the two lists agree and that each name is printed in the figure itself.  The names follow the
paper's lexicon, ``docs/paper/paper-b/01-terms.md``.

The output depends only on this file: no clock, no random number, no environment.  Running it twice gives
the same bytes.
"""
from __future__ import annotations

import math
import sys
from contextlib import contextmanager
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
MINUS = "\N{MINUS SIGN}"

# ---------------------------------------------------------------------------------------------------------
# Registered design values.  name -> (value, where it was read).  "registration" is
# configs/campaigns/v5_claim_25g83/registration_block5.md, revision 9 DRAFT, at commit 9b0c680ed.  The line
# numbers are of that file at that commit and will move at the seal; the test finds each value by its
# content, not by its line number, so a changed value fails the test wherever the line has moved to.
# ---------------------------------------------------------------------------------------------------------
REGISTERED: dict[str, tuple[object, str]] = {
    # the clock frequency gate
    "clock.h_ms": (Fraction("3.7"), "registration §4.3 l.1338; §4.2 l.1199; joulewise/hazards/clock.py DEFAULT_THRESHOLDS"),
    "clock.h_observed_ms": (Fraction("3.6"), "registration §4.2 l.1200 (3.598 ms at §0.14 l.745)"),
    "clock.h_margin_ms": (Fraction("0.1"), "registration §4.2 l.1200"),
    "clock.frequency_margin_ppm": (Fraction("0.25"), "registration §4.3 l.1338; §4.2 l.1200"),
    "clock.t_stream_max_s": (Fraction(335), "registration §4.3 l.1338; §0.14 l.741"),
    "clock.limit_ms": (Fraction(5), "registration §4.3 l.1338; §0.14 l.730-731"),
    "clock.example_pass_f_ppm": (Fraction("-3.17"), "registration §4.2 l.1203; read on 2026-10-05, §0.14 l.736-737"),
    "clock.example_pass_date": ("2026-10-05", "registration §0.14 l.736"),
    "clock.example_refuse_abs_f_ppm": (Fraction("3.7"), "registration §4.2 l.1203"),
    # the measurement path of the meter cross-check
    "meter.adapter_w": (140, "registration §5.8 l.2012 and l.2021; §0.2 l.267"),
    "meter.cable_v": (28, "registration §5.8 l.2012 and l.2022"),
    "meter.samples_per_s": (50, "registration §5.8 l.2014 and l.2024"),
    "meter.battery_reads_per_s": (1, "registration §5.8 l.2018 and l.2028"),
    "sampler.requested_interval_ms": (100, "registration §0.2 l.270"),
    # the reference members of one window
    "reference.corpus_members": (12, "registration §0.12 l.490"),
    "reference.start_members": (3, "registration §0.12 l.491"),
    "reference.midpoint_members": (1, "registration §0.12 l.491-492"),
    "reference.end_members": (3, "registration §0.12 l.492"),
    "reference.start_spares": (3, "registration §0.12 l.497-498"),
    "reference.midpoint_spares": (1, "registration §0.12 l.498-499"),
    "reference.end_spares": (3, "registration §0.12 l.497-498"),
    "reference.min_endpoint_survivors": (2, "registration §0.12 l.615-616"),
    "reference.t_975_df11": (Fraction("2.201"), "registration §0.12 l.672; joulewise/aggregate.py _T_CRITICAL_95"),
}

# ---------------------------------------------------------------------------------------------------------
# Synthetic inputs of the two worked examples.  They are the registration's own invented numbers, copied so
# that the figures and the registration show one example.  None is a measurement.
# ---------------------------------------------------------------------------------------------------------
SYNTHETIC: dict[str, tuple[object, str]] = {
    "meter.idle_meter_w": (Fraction("9.0"), "registration §5.8 l.2062"),
    "meter.idle_battery_w": (Fraction(0), "registration §5.8 l.2062"),
    "meter.request_s": (Fraction("20.0"), "registration §5.8 l.2063"),
    "meter.request_meter_w": (Fraction("52.0"), "registration §5.8 l.2063"),
    "meter.request_battery_w": (Fraction("1.5"), "registration §5.8 l.2063"),
    "meter.rail_energy_j": (Fraction(712), "registration §5.8 l.2064"),
    "reference.corpus_j": (
        tuple(Fraction(v) for v in (
            "99.62", "99.71", "99.80", "99.88", "99.93", "99.97",
            "100.04", "100.09", "100.15", "100.22", "100.31", "100.38")),
        "registration §0.12 l.671"),
    # None marks the planned start member that was lost during the window (member 2, aborted).
    "reference.start_planned_j": ((Fraction("100.02"), None, Fraction("99.91")), "registration §0.12 l.673-674"),
    "reference.start_spare_j": (Fraction("99.95"), "registration §0.12 l.675"),
    "reference.midpoint_j": (Fraction("100.20"), "registration §0.12 l.676"),
    "reference.end_planned_j": ((Fraction("100.26"), Fraction("100.19"), Fraction("101.08")), "registration §0.12 l.676"),
    # index of the end member found lost after the window (the third)
    "reference.end_lost_index": (2, "registration §0.12 l.676-677"),
}


# Where the registered-values table of the paper (docs/paper/paper-b/registered-values.json) holds the same
# value, its id there.  The test compares the two; the table states the sampler's rate in Hz (1000 / ms).
REGISTERED_VALUE_IDS: dict[str, str] = {
    "clock.h_ms": "arm.clock.h_ms",
    "clock.frequency_margin_ppm": "arm.clock.frequency_margin_ppm",
    "clock.t_stream_max_s": "arm.clock.t_stream_max_s",
    "clock.limit_ms": "arm.clock.limit_ms",
    "sampler.requested_interval_ms": "member.sampler_rate_hz",
    "reference.corpus_members": "pack.ALPHA.reference_corpus_members",
    "reference.start_members": "reference.endpoint_references_planned",
    "reference.end_members": "reference.endpoint_references_planned",
    "reference.start_spares": "reference.spares.start",
    "reference.midpoint_spares": "reference.spares.midpoint",
    "reference.end_spares": "reference.spares.end",
    "reference.min_endpoint_survivors": "yield.min_valid.reference_endpoint",
}


def reg(name: str):
    return REGISTERED[name][0]


def syn(name: str):
    return SYNTHETIC[name][0]


def fmt(value, places: int) -> str:
    """A number as text with a fixed count of decimals, rounded half up from its exact value."""

    exact = value if isinstance(value, Fraction) else Fraction(value)
    quantum = Decimal(1).scaleb(-places)
    text = (Decimal(exact.numerator) / Decimal(exact.denominator)).quantize(quantum, rounding=ROUND_HALF_UP)
    return f"{text:f}".replace("-", MINUS)


def plain(value) -> str:
    """A value with exactly the decimals it has (3.7, 0.25, 335, 5)."""

    exact = Fraction(value)
    if exact.denominator == 1:
        return str(exact.numerator).replace("-", MINUS)
    return f"{Decimal(exact.numerator) / Decimal(exact.denominator):f}".replace("-", MINUS)


# ---------------------------------------------------------------------------------------------------------
# The three calculations, written out from the registration's text.
# ---------------------------------------------------------------------------------------------------------
def gate_bound_ms(abs_f_ppm) -> Fraction:
    """Predicted timing bound of the worst member: h + (|f| + margin) x T, in ms.

    A rate of 1 ppm held for 1 s moves a clock by 1 microsecond, so ppm x s is microseconds and dividing by
    1000 gives milliseconds (registration section 4.2, rule (i)).
    """

    rate = Fraction(abs_f_ppm) + reg("clock.frequency_margin_ppm")
    return reg("clock.h_ms") + rate * reg("clock.t_stream_max_s") / 1000


def gate_values() -> dict[str, Fraction]:
    slope = reg("clock.t_stream_max_s") / 1000  # ms of bound for each ppm of rate
    pass_f = abs(reg("clock.example_pass_f_ppm"))
    refuse_f = reg("clock.example_refuse_abs_f_ppm")
    return {
        "slope_ms_per_ppm": slope,
        "intercept_ms": gate_bound_ms(0),
        "pass_abs_f_ppm": pass_f,
        "pass_bound_ms": gate_bound_ms(pass_f),
        "refuse_abs_f_ppm": refuse_f,
        "refuse_bound_ms": gate_bound_ms(refuse_f),
        "max_abs_f_ppm": (reg("clock.limit_ms") - reg("clock.h_ms")) / slope - reg("clock.frequency_margin_ppm"),
    }


def meter_values() -> dict[str, Fraction]:
    """Registration section 5.8: machine energy above idle = meter term + battery term; the rail share."""

    seconds = syn("meter.request_s")
    meter_term = (syn("meter.request_meter_w") - syn("meter.idle_meter_w")) * seconds
    battery_term = (syn("meter.request_battery_w") - syn("meter.idle_battery_w")) * seconds
    machine = meter_term + battery_term
    rail = syn("meter.rail_energy_j")
    return {
        "meter_term_j": meter_term,
        "battery_term_j": battery_term,
        "machine_energy_j": machine,
        "rail_energy_j": rail,
        "rail_share": rail / machine,
        "rail_share_without_battery": rail / meter_term,
    }


def _mean(values) -> Fraction:
    values = list(values)
    return sum(values, Fraction(0)) / len(values)


def drift_bound(corpus, n_start: int, n_end: int) -> dict[str, object]:
    """The drift bound for n_start start survivors and n_end end survivors (registration section 0.12).

    gap term: the widest gap that a mean of n_start corpus members and a mean of n_end corpus members can
    show, max(U_ns - L_ne, U_ne - L_ns), where U_j is the mean of the j highest corpus energies and L_j
    the mean of the j lowest.  repeatability term: t x s x sqrt(1/n_start + 1/n_end), where s is the
    corpus's sample standard deviation and t the two-sided 95% Student-t value for n - 1 degrees of
    freedom.  The bound is the larger of the two terms.
    """

    ordered = sorted(corpus)
    count = len(ordered)
    if count != reg("reference.corpus_members"):
        raise ValueError("the t value registered here is for the full 12-member corpus")

    def upper(j: int) -> Fraction:
        return _mean(ordered[-j:])

    def lower(j: int) -> Fraction:
        return _mean(ordered[:j])

    gap_start_high = upper(n_start) - lower(n_end)
    gap_end_high = upper(n_end) - lower(n_start)
    gap = max(gap_start_high, gap_end_high)
    centre = _mean(ordered)
    stddev = math.sqrt(float(sum((value - centre) ** 2 for value in ordered) / (count - 1)))
    repeatability = float(reg("reference.t_975_df11")) * stddev * math.sqrt(1.0 / n_start + 1.0 / n_end)
    return {
        "upper_start": upper(n_start), "lower_end": lower(n_end),
        "upper_end": upper(n_end), "lower_start": lower(n_start),
        "gap_start_high": gap_start_high, "gap_end_high": gap_end_high, "gap_term": gap,
        "stddev": stddev, "repeatability_term": repeatability,
        "bound": max(float(gap), repeatability),
    }


def survivor_values() -> dict[str, object]:
    corpus = syn("reference.corpus_j")
    start_planned = syn("reference.start_planned_j")
    end_planned = syn("reference.end_planned_j")
    lost_end = syn("reference.end_lost_index")
    start_kept = [value for value in start_planned if value is not None]
    start = start_kept + [syn("reference.start_spare_j")]
    end = [value for index, value in enumerate(end_planned) if index != lost_end]
    midpoint = syn("reference.midpoint_j")
    bound = drift_bound(corpus, len(start), len(end))
    planned = drift_bound(corpus, reg("reference.start_members"), reg("reference.end_members"))
    start_mean, end_mean = _mean(start), _mean(end)
    difference = abs(end_mean - start_mean)
    trio = (start_mean, midpoint, end_mean)
    spread = max(trio) - min(trio)
    kept_all_end_mean = _mean(end_planned)
    return {
        "corpus": corpus, "start": start, "end": end, "midpoint": midpoint,
        "start_planned_kept": start_kept, "spare": syn("reference.start_spare_j"),
        "end_lost": end_planned[lost_end],
        "n_start": len(start), "n_mid": 1, "n_end": len(end),
        "start_mean": start_mean, "end_mean": end_mean, "difference": difference,
        "bound": bound, "planned_bound": planned,
        "passes": float(difference) <= bound["bound"],
        "spread": spread, "allowance": max(float(spread), bound["bound"]),
        "kept_all_end_mean": kept_all_end_mean,
        "kept_all_difference": abs(kept_all_end_mean - start_mean),
    }


def worked_values() -> dict[str, dict[str, str]]:
    """Figure key -> the computed numbers the figure prints, exactly as printed.

    The caption file must print every one of them as well (the test checks both places).
    """

    g, m, v = gate_values(), meter_values(), survivor_values()
    bound, planned = v["bound"], v["planned_bound"]
    return {
        "B-S2": {
            "meter_term_j": plain(m["meter_term_j"]),
            "battery_term_j": plain(m["battery_term_j"]),
            "machine_energy_j": plain(m["machine_energy_j"]),
            "rail_energy_j": plain(m["rail_energy_j"]),
            "rail_share": fmt(m["rail_share"], 2),
            "rail_share_without_battery": fmt(m["rail_share_without_battery"], 2),
        },
        "B-S4": {
            "lower_end_j": fmt(bound["lower_end"], 4),
            "upper_start_j": fmt(bound["upper_start"], 4),
            "gap_term_j": fmt(bound["gap_term"], 4),
            "stddev_j": fmt(Fraction(bound["stddev"]), 4),
            "repeatability_term_j": fmt(Fraction(bound["repeatability_term"]), 4),
            "bound_j": fmt(Fraction(bound["bound"]), 4),
            "planned_bound_j": fmt(Fraction(planned["bound"]), 4),
            "start_mean_j": fmt(v["start_mean"], 4),
            "end_mean_j": fmt(v["end_mean"], 4),
            "difference_j": fmt(v["difference"], 4),
        },
        "B-S5": {
            "slope_ms_per_ppm": plain(g["slope_ms_per_ppm"]),
            "intercept_ms": fmt(g["intercept_ms"], 3),
            "pass_bound_ms": fmt(g["pass_bound_ms"], 3),
            "refuse_bound_ms": fmt(g["refuse_bound_ms"], 3),
            "max_abs_f_ppm": fmt(g["max_abs_f_ppm"], 4),
        },
    }


def caption_values() -> dict[str, dict[str, str]]:
    """Figure key -> computed numbers that only the caption prints (the figure does not draw them)."""

    v = survivor_values()
    bound = v["bound"]
    return {
        "B-S2": {},
        "B-S4": {
            "upper_end_j": fmt(bound["upper_end"], 4),
            "lower_start_j": fmt(bound["lower_start"], 4),
            "gap_end_high_j": fmt(bound["gap_end_high"], 4),
            "spread_j": fmt(v["spread"], 4),
            "allowance_j": fmt(Fraction(v["allowance"]), 4),
            "kept_all_end_mean_j": fmt(v["kept_all_end_mean"], 4),
            "kept_all_difference_j": fmt(v["kept_all_difference"], 4),
        },
        "B-S5": {},
    }


# ---------------------------------------------------------------------------------------------------------
# A small SVG writer.  Ink and chrome are neutral.  Blue marks the claim path and the surviving references,
# orange the cross-check boundary.  Green and red mark PASS and REFUSE and always sit beside the word.
# ---------------------------------------------------------------------------------------------------------
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, PANEL, SURFACE = "#e1e0d9", "#c3c2b7", "#f4f3ef", "#ffffff"
BLUE, BLUE_WASH, ORANGE = "#2a78d6", "#e6f0fc", "#eb6834"
GOOD, CRITICAL, CRITICAL_WASH = "#0ca30c", "#d03b3b", "#fbeaea"
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"


def c(value: float) -> str:
    """A coordinate with at most two decimals and no trailing zeros."""

    text = f"{float(value):.2f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def text_width(text: str, size: float, bold: bool = False) -> float:
    """A cautious estimate of rendered width, used only to refuse a label that would overflow its place."""

    units = 0.0
    for char in text:
        if char in " .,:;|'!il":
            units += 0.28
        elif char in "jtfrI()[]-/":
            units += 0.36
        elif char in "mwMW":
            units += 0.88
        elif char.isupper() or char in "≤≥÷×+=→√" or char == MINUS:
            units += 0.68
        else:
            units += 0.56
    return units * size * (1.06 if bold else 1.0)


def _data(values: dict[str, object]) -> str:
    return "".join(f' data-{name.replace("_", "-")}="{escape(str(value))}"' for name, value in values.items())


class Figure:
    def __init__(self, key: str, filename: str, heading: str, subtitle: str, description: str,
                 width: int, height: int) -> None:
        self.key, self.filename, self.heading = key, filename, heading
        self.width, self.height = width, height
        self.labels: list[str] = []
        self._open: str | None = None
        for line, size, bold in ((heading, 20, True), (subtitle, 13.5, False)):
            if 30 + text_width(line, size, bold) > width - 16:
                raise ValueError(f"{key}: heading line too wide: {line!r}")
        self.body: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" font-family="{FONT}" data-figure="{key}">',
            f"<title>{escape(heading, quote=False)}</title>",
            f"<desc>{escape(description, quote=False)}</desc>",
            f'<rect data-role="background" width="{width}" height="{height}" fill="{SURFACE}"/>',
            '<g data-role="figure-title">',
            self._text(30, 34, heading, 20, weight="bold"),
            self._text(30, 56, subtitle, 13.5, fill=INK2),
            "</g>",
        ]

    # -- elements -----------------------------------------------------------------------------------------
    @contextmanager
    def element(self, label: str, **data: object):
        if self._open is not None:
            raise RuntimeError(f"element {label!r} opened inside {self._open!r}")
        if label not in self.labels:
            self.labels.append(label)
        self._open = label
        self.body.append(f'<g data-element="{escape(label)}"{_data(data)}><title>{escape(label, quote=False)}</title>')
        try:
            yield self
        finally:
            self.body.append("</g>")
            self._open = None

    def _draw(self, markup: str) -> None:
        if self._open is None:
            raise RuntimeError("every shape and every text belongs to a named element")
        self.body.append(markup)

    # -- primitives ---------------------------------------------------------------------------------------
    @staticmethod
    def _text(x, y, text, size=13, *, anchor="start", weight=None, fill=INK, rotate=None) -> str:
        attrs = f'x="{c(x)}" y="{c(y)}" font-size="{c(size)}" fill="{fill}"'
        if anchor != "start":
            attrs += f' text-anchor="{anchor}"'
        if weight:
            attrs += f' font-weight="{weight}"'
        if rotate is not None:
            attrs += f' transform="rotate({c(rotate)} {c(x)} {c(y)})"'
        return f"<text {attrs}>{escape(text, quote=False)}</text>"

    def text(self, x, y, text, size=13, *, anchor="start", weight=None, fill=INK, rotate=None,
             max_width: float | None = None) -> None:
        width = text_width(text, size, weight == "bold")
        if max_width is not None and width > max_width:
            raise ValueError(f"{self.key}: {text!r} is about {width:.0f} px wide, more than {max_width:.0f}")
        if rotate is None:
            left = {"start": x, "middle": x - width / 2, "end": x - width}[anchor]
            if left < 4 or left + width > self.width - 4:
                raise ValueError(f"{self.key}: {text!r} leaves the canvas ({left:.0f} to {left + width:.0f})")
        self._draw(self._text(x, y, text, size, anchor=anchor, weight=weight, fill=fill, rotate=rotate))

    def lines(self, x, y, rows, size=13, *, leading=None, anchor="start", weight=None, fill=INK,
              max_width: float | None = None) -> None:
        step = leading if leading is not None else round(size * 1.3, 1)
        for index, row in enumerate(rows):
            self.text(x, y + index * step, row, size, anchor=anchor, weight=weight, fill=fill, max_width=max_width)

    def rect(self, x, y, w, h, *, fill="none", stroke="none", width=1.0, dash=None, rx=0) -> None:
        attrs = f'x="{c(x)}" y="{c(y)}" width="{c(w)}" height="{c(h)}" fill="{fill}"'
        if stroke != "none":
            attrs += f' stroke="{stroke}" stroke-width="{c(width)}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if rx:
            attrs += f' rx="{c(rx)}"'
        self._draw(f"<rect {attrs}/>")

    def line(self, x1, y1, x2, y2, *, stroke=INK2, width=1.5, dash=None, cap="butt") -> None:
        attrs = f'x1="{c(x1)}" y1="{c(y1)}" x2="{c(x2)}" y2="{c(y2)}" stroke="{stroke}" stroke-width="{c(width)}"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        if cap != "butt":
            attrs += f' stroke-linecap="{cap}"'
        self._draw(f"<line {attrs}/>")

    def polyline(self, points, *, stroke=INK2, width=1.5) -> None:
        coords = " ".join(f"{c(x)},{c(y)}" for x, y in points)
        self._draw(f'<polyline points="{coords}" fill="none" stroke="{stroke}" stroke-width="{c(width)}" '
                   'stroke-linejoin="round" stroke-linecap="round"/>')

    def curve(self, start, control, end, *, stroke=INK2, width=1.6) -> None:
        self._draw(f'<path d="M {c(start[0])} {c(start[1])} Q {c(control[0])} {c(control[1])} {c(end[0])} {c(end[1])}" '
                   f'fill="none" stroke="{stroke}" stroke-width="{c(width)}"/>')

    def polygon(self, points, *, fill=INK2, stroke="none", width=1.0, dash=None) -> None:
        coords = " ".join(f"{c(x)},{c(y)}" for x, y in points)
        attrs = f'points="{coords}" fill="{fill}"'
        if stroke != "none":
            attrs += f' stroke="{stroke}" stroke-width="{c(width)}" stroke-linejoin="round"'
        if dash:
            attrs += f' stroke-dasharray="{dash}"'
        self._draw(f"<polygon {attrs}/>")

    def circle(self, x, y, r, *, fill=INK, stroke="none", width=1.0) -> None:
        attrs = f'cx="{c(x)}" cy="{c(y)}" r="{c(r)}" fill="{fill}"'
        if stroke != "none":
            attrs += f' stroke="{stroke}" stroke-width="{c(width)}"'
        self._draw(f"<circle {attrs}/>")

    # -- composites ---------------------------------------------------------------------------------------
    def head(self, x, y, ux, uy, *, fill=INK2, length=9.0, half=3.8) -> None:
        """An arrowhead whose tip is (x, y), pointing along the unit vector (ux, uy)."""

        bx, by = x - ux * length, y - uy * length
        self.polygon([(x, y), (bx - uy * half, by + ux * half), (bx + uy * half, by - ux * half)], fill=fill)

    def arrow(self, x1, y1, x2, y2, *, stroke=INK2, width=1.8, both=False) -> None:
        span = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / span, (y2 - y1) / span
        start = (x1 + ux * 8, y1 + uy * 8) if both else (x1, y1)
        self.line(start[0], start[1], x2 - ux * 8, y2 - uy * 8, stroke=stroke, width=width)
        self.head(x2, y2, ux, uy, fill=stroke)
        if both:
            self.head(x1, y1, -ux, -uy, fill=stroke)

    def box(self, x, y, w, h, rows, *, fill=PANEL, stroke=MUTED, width=1.2, size=13, rx=4) -> None:
        """A rounded box with its lines of text centred; refuses text wider than the box."""

        self.rect(x, y, w, h, fill=fill, stroke=stroke, width=width, rx=rx)
        step = round(size * 1.3, 1)
        first = y + h / 2 - (len(rows) - 1) * step / 2 + size * 0.35
        for index, row in enumerate(rows):
            self.text(x + w / 2, first + index * step, row, size, anchor="middle",
                      weight="bold" if index == 0 else None, fill=INK if index == 0 else INK2, max_width=w - 10)

    def disc(self, x, y, number: int, r=9.5) -> None:
        """A numbered disc: the place where an instrument reads."""

        self.circle(x, y, r, fill=INK, stroke=SURFACE, width=2)
        self._draw(self._text(x, y + 4.2, str(number), 12, anchor="middle", weight="bold", fill=SURFACE))

    def svg(self) -> str:
        if self._open is not None:
            raise RuntimeError("an element is still open")
        return "\n".join(self.body + ["</svg>"]) + "\n"


# ---------------------------------------------------------------------------------------------------------
# Figure B-S2: two measurement boundaries on one machine.
# ---------------------------------------------------------------------------------------------------------
def figure_boundary() -> Figure:
    m = meter_values()
    w = worked_values()["B-S2"]
    fig = Figure(
        "B-S2", "figB_S2_measurement_boundary.svg",
        "Figure B-S2. Two measurement boundaries on one machine",
        "Schematic, not to scale. The bottom strip is a SYNTHETIC worked example: its numbers are invented, not measured.",
        "Energy path from the wall outlet through the power adapter, an inline meter and the laptop's DC input "
        "to the processor rails and the rest of the machine, with the battery joining after the DC input; the "
        "sampler's measurement boundary around the processor rails, the wider measurement boundary of the "
        "whole-machine meter, the three places where instruments read, and a synthetic worked example of the "
        "rail share.",
        1000, 628)
    mid = 190  # height of the main energy path

    with fig.element("the Mac"):
        fig.rect(590, 76, 386, 296, fill="#faf9f6", stroke=MUTED, width=1.2, rx=10)
        fig.text(604, 98, "the Mac (M3 Max laptop)", 13, weight="bold")

    with fig.element("mains AC"):
        fig.box(30, mid - 30, 100, 60, ["mains AC", "wall outlet"])
    with fig.element("power adapter"):
        fig.box(160, mid - 40, 120, 80, ["power adapter", f"{reg('meter.adapter_w')} W"])
    with fig.element("conversion loss"):
        fig.line(220, mid + 40, 220, mid + 56, stroke=MUTED, width=1)
        fig.lines(220, mid + 71, ["conversion loss here", "is not measured"], 12, anchor="middle", fill=INK2)
    with fig.element("USB-C cable"):
        fig.text(342, mid - 11, f"USB-C cable, {reg('meter.cable_v')} V", 12.5, anchor="middle", max_width=122)
    with fig.element("whole-machine meter"):
        fig.box(404, mid - 40, 156, 80,
                ["whole-machine meter", "voltage × current", f"{reg('meter.samples_per_s')} samples/s"], size=12.5)
        fig.disc(560, mid - 40, 2)
    with fig.element("DC input"):
        fig.box(610, mid - 25, 72, 50, ["DC input"])

    with fig.element("meter's boundary"):
        fig.rect(744, 134, 218, 216, stroke=ORANGE, width=2.2, dash="7 4", rx=6)
        fig.text(748, 126, "meter's boundary", 12.5, weight="bold")
    with fig.element("sampler's boundary"):
        fig.rect(786, mid - 31, 164, 62, fill=BLUE_WASH, stroke=BLUE, width=2.6, rx=4)
        fig.text(790, mid - 38, "sampler's boundary", 12.5, weight="bold")
    with fig.element("processor rails"):
        fig.text(868, mid - 4, "processor rails", 13, anchor="middle", weight="bold")
        fig.text(868, mid + 13, "CPU + GPU + ANE", 13, anchor="middle", fill=INK2)
    rest_mid = 294
    with fig.element("rest of the machine"):
        fig.box(786, rest_mid - 36, 164, 72, ["rest of the machine", "memory, storage, fans,", "display (asleep)"], size=12.5)
    with fig.element("battery"):
        fig.box(610, 300, 90, 54, ["battery"])

    with fig.element("energy flow"):
        fig.arrow(130, mid, 160, mid)
        fig.arrow(280, mid, 404, mid)
        fig.arrow(560, mid, 610, mid)
        fig.line(682, mid, 768, mid, width=1.8)
        fig.circle(716, mid, 4, fill=INK2)
        fig.line(768, mid, 768, rest_mid, width=1.8)
        fig.arrow(767, mid, 786, mid)
        fig.arrow(767, rest_mid, 786, rest_mid)
        fig.polyline([(708, 327), (716, 327), (716, mid + 12)], width=1.8)
        fig.head(716, mid + 4, 0, -1)
        fig.head(700, 327, -1, 0)

    with fig.element("sampler"):
        fig.disc(950, mid - 31, 1)
    with fig.element("battery sensor"):
        fig.disc(716, 262, 3)

    if reg("meter.battery_reads_per_s") != 1:
        raise ValueError("the battery sensor's key says 'once a second'")
    with fig.element("instruments"):
        fig.text(30, 322, "Three instruments, numbered where they read", 13, weight="bold")
    keys = [
        ("sampler", 1, "sampler: average processor-rail power, one record requested every "
                       f"{reg('sampler.requested_interval_ms')} ms"),
        ("whole-machine meter", 2, "whole-machine meter: voltage and current in the USB-C cable, "
                                   f"{reg('meter.samples_per_s')} samples a second"),
        ("battery sensor", 3, "battery sensor: battery current and voltage, read once a second"),
    ]
    for index, (label, number, sentence) in enumerate(keys):
        with fig.element(label):
            y = 346 + index * 24
            fig.disc(40, y - 4.5, number, r=8.5)
            fig.text(58, y, sentence, 12.5, max_width=525)

    with fig.element("energy flow"):
        fig.arrow(604, 395.5, 640, 395.5)
        fig.text(650, 400, "energy flow (two heads: either direction)", 12.5, max_width=320)
    with fig.element("sampler's boundary"):
        fig.rect(606, 412, 32, 15, fill=BLUE_WASH, stroke=BLUE, width=2.6, rx=3)
        fig.text(650, 424, "sampler's boundary: every reported energy", 12.5, max_width=320)
    with fig.element("meter's boundary"):
        fig.rect(606, 436, 32, 15, stroke=ORANGE, width=2.2, dash="7 4", rx=3)
        fig.text(650, 448, "meter's boundary: cross-check only", 12.5, max_width=320)

    top = 468
    seconds = fmt(syn("meter.request_s"), 1)
    with fig.element("worked example"):
        fig.rect(30, top, 940, 148, fill=PANEL, rx=6)
        fig.text(44, top + 22, f"SYNTHETIC worked example: one measured request of {seconds} s. "
                 "Every energy is idle-subtracted.", 13, weight="bold", max_width=915)
        fig.text(44, top + 117, "Idle-subtracted means: less what the idle machine would have used in the same "
                 f"{seconds} s.", 12.5, fill=INK2, max_width=915)
    left, right = 62, 560
    with fig.element("meter term"):
        fig.disc(left - 8, top + 41.5, 2, r=8.5)
        fig.text(left + 8, top + 46, "meter term: "
                 f"({fmt(syn('meter.request_meter_w'), 1)} W {MINUS} {fmt(syn('meter.idle_meter_w'), 1)} W at idle) "
                 f"× {seconds} s = {w['meter_term_j']} J", 13, max_width=470)
    with fig.element("battery term"):
        fig.disc(left - 8, top + 65.5, 3, r=8.5)
        fig.text(left + 8, top + 70, "battery term: "
                 f"({fmt(syn('meter.request_battery_w'), 1)} W {MINUS} {plain(syn('meter.idle_battery_w'))} W at idle) "
                 f"× {seconds} s = {w['battery_term_j']} J", 13, max_width=470)
        fig.text(44, top + 135, "The battery term is battery current × battery voltage, positive during battery "
                 "assist (the battery helping to supply the machine).", 12.5, fill=INK2, max_width=915)
    with fig.element("idle-subtracted machine energy"):
        fig.text(left + 8, top + 94, "idle-subtracted machine energy = "
                 f"{w['meter_term_j']} J + {w['battery_term_j']} J = {w['machine_energy_j']} J",
                 13, weight="bold", max_width=470)
    with fig.element("idle-subtracted rail energy"):
        fig.disc(right - 8, top + 41.5, 1, r=8.5)
        fig.text(right + 8, top + 46, f"idle-subtracted rail energy: {w['rail_energy_j']} J", 13, max_width=390)
    with fig.element("rail share"):
        fig.text(right + 8, top + 70, f"rail share = {w['rail_energy_j']} J ÷ {w['machine_energy_j']} J"
                 f" = {w['rail_share']}", 13, weight="bold", max_width=390)
        fig.text(right + 8, top + 94, f"without the battery term: {w['rail_energy_j']} J ÷ "
                 f"{w['meter_term_j']} J = {w['rail_share_without_battery']}, too high", 13, fill=INK2, max_width=390)
    if m["rail_share_without_battery"] <= m["rail_share"]:
        raise ValueError("the strip says the share without the battery term is too high")
    return fig


# ---------------------------------------------------------------------------------------------------------
# Figure B-S4: the drift check on the reference members that survive.
# ---------------------------------------------------------------------------------------------------------
GLYPH_LABELS = {
    "corpus": "corpus member",
    "survives": "surviving reference",
    "spare_ran": "spare that ran",
    "lost": "lost reference",
    "spare_idle": "spare that did not run",
}


def _glyph(fig: Figure, kind: str, x: float, y: float) -> None:
    if kind == "corpus":
        fig.rect(x - 6, y - 6, 12, 12, fill=MUTED, rx=1.5)
    elif kind == "survives":
        fig.circle(x, y, 7, fill=BLUE, stroke=SURFACE, width=2)
    elif kind == "spare_ran":
        fig.polygon([(x, y - 9), (x + 9, y), (x, y + 9), (x - 9, y)], fill=BLUE, stroke=SURFACE, width=2)
    elif kind == "lost":
        fig.circle(x, y, 7, fill=SURFACE, stroke=MUTED, width=1.5)
        fig.line(x - 4.5, y - 4.5, x + 4.5, y + 4.5, stroke=CRITICAL, width=2.4, cap="round")
        fig.line(x - 4.5, y + 4.5, x + 4.5, y - 4.5, stroke=CRITICAL, width=2.4, cap="round")
    elif kind == "spare_idle":
        fig.polygon([(x, y - 8), (x + 8, y), (x, y + 8), (x - 8, y)], fill=SURFACE, stroke=MUTED, width=1.4, dash="3 2")
    else:
        raise ValueError(kind)


def figure_survivors() -> Figure:
    v = survivor_values()
    w = worked_values()["B-S4"]
    bound = v["bound"]
    n_start, n_end = v["n_start"], v["n_end"]
    if not v["passes"]:
        raise ValueError("the drawing's verdict line says the example passes")
    if not (float(bound["gap_term"]) >= bound["repeatability_term"] and bound["gap_start_high"] >= bound["gap_end_high"]):
        raise ValueError("the drawing shows the gap between the highest start-count mean and the lowest end-count mean as the bound")
    planned = (reg("reference.start_members"), reg("reference.midpoint_members"), reg("reference.end_members"))
    fig = Figure(
        "B-S4", "figB_S4_reference_survivors.svg",
        "Figure B-S4. Testing a window for drift when some reference members cannot be used",
        "SYNTHETIC worked example: every energy in this figure is invented for illustration; none is a measurement.",
        "Panel (a): one window's reference members in running order, with one start member lost and replaced "
        "by a spare and one end member lost with no replacement. Panel (b): the same members on an energy "
        "axis, the reference drift bound computed from the reference corpus, and the difference between the end "
        "and start means.",
        1000, 806)

    # ---- panel (a): the roster ---------------------------------------------------------------------------
    track = 176
    with fig.element("Panel (a)"):
        fig.text(30, 90, "Panel (a). One window's reference members (runs of one fixed workload), in running order, "
                 "left to right; not to scale", 14, weight="bold")

    corpus_x = [38 + index * 18 for index in range(reg("reference.corpus_members"))]
    start_x, start_spare_x = [286, 310, 334], [378, 402, 426]
    mid_x, mid_spare_x = [590], [646]
    end_x, end_spare_x = [818, 842, 866], [908, 932, 956]
    drawn = (len(start_x), len(mid_x), len(end_x), len(start_spare_x), len(mid_spare_x), len(end_spare_x))
    if drawn != planned + (reg("reference.start_spares"), reg("reference.midpoint_spares"), reg("reference.end_spares")):
        raise ValueError("the drawn slots differ from the registered counts")

    with fig.element("reference corpus"):
        fig.text(32, 132, "reference corpus", 12.5, weight="bold")
        fig.text(32, 148, f"{reg('reference.corpus_members')} members", 12, fill=INK2)
    with fig.element("corpus member"):
        for x in corpus_x:
            _glyph(fig, "corpus", x, track)

    with fig.element("start triplet"):
        fig.text(start_x[1], 140, "start triplet", 12.5, anchor="middle", weight="bold")
    with fig.element("midpoint reference"):
        fig.text(mid_x[0], 132, "midpoint", 12.5, anchor="middle", weight="bold")
        fig.text(mid_x[0], 147, "reference", 12.5, anchor="middle", weight="bold")
    with fig.element("end triplet"):
        fig.text(end_x[1], 140, "end triplet", 12.5, anchor="middle", weight="bold")
    with fig.element("spares"):
        fig.text(start_spare_x[1], 140, "spares", 12.5, anchor="middle", weight="bold")
        fig.text(mid_spare_x[0], 140, "spare", 12.5, anchor="middle", weight="bold")
        fig.text(end_spare_x[1], 140, "spares", 12.5, anchor="middle", weight="bold")
    with fig.element("science members"):
        for x, half in ((452, "first half"), (676, "second half")):
            fig.rect(x, track - 13, 118, 26, fill=PANEL, stroke=AXIS, rx=4)
            fig.text(x + 59, track + 4, "science members", 12, anchor="middle", fill=INK2, max_width=110)
            fig.text(x + 59, 140, half, 12, anchor="middle", fill=INK2)

    start_planned = syn("reference.start_planned_j")
    lost_start = [index for index, value in enumerate(start_planned) if value is None]
    lost_end = syn("reference.end_lost_index")
    if lost_start != [1] or lost_end != 2:
        raise ValueError("the notes under panel (a) name start member 2 and end member 3 as the lost ones")
    with fig.element("surviving reference"):
        for index, x in enumerate(start_x):
            if index not in lost_start:
                _glyph(fig, "survives", x, track)
        _glyph(fig, "survives", mid_x[0], track)
        for index, x in enumerate(end_x):
            if index != lost_end:
                _glyph(fig, "survives", x, track)
    with fig.element("lost reference"):
        _glyph(fig, "lost", start_x[lost_start[0]], track)
        _glyph(fig, "lost", end_x[lost_end], track)
    with fig.element("spare that ran"):
        _glyph(fig, "spare_ran", start_spare_x[0], track)
    with fig.element("spare that did not run"):
        for x in start_spare_x[1:] + mid_spare_x + end_spare_x:
            _glyph(fig, "spare_idle", x, track)

    with fig.element("one retry"):
        sx, tx = start_spare_x[0], start_x[lost_start[0]]
        fig.curve((sx - 4, track + 12), ((sx + tx) / 2, track + 40), (tx + 7, track + 14))
        fig.head(tx + 3, track + 10.5, -0.75, -0.66, length=8, half=3.4)
        fig.lines(356, track + 56, ["one retry: member 2 was lost during the", "window, so spare 1 ran and takes its place"],
                  12, anchor="middle", fill=INK2, leading=15)
    with fig.element("no retry"):
        fig.line(end_x[lost_end], track + 11, end_x[lost_end], track + 42, stroke=MUTED, width=1)
        fig.lines(968, track + 56, ["no retry: member 3's loss was found only",
                                     "after the window, when its records were checked"],
                  12, anchor="end", fill=INK2, leading=15)
    with fig.element("surviving references"):
        for x, kept, of in ((start_x[1] + 46, n_start, planned[0]), (mid_x[0] + 28, v["n_mid"], planned[1]),
                            (end_x[1] + 44, n_end, planned[2])):
            fig.text(x, track + 98, f"surviving references: {kept} of {of}", 12.5, anchor="middle", weight="bold")
    floor = reg("reference.min_endpoint_survivors")
    with fig.element("Minimum to run the check"):
        fig.text(30, track + 124, f"Minimum to run the check: {floor} surviving references in the start triplet and "
                 f"{floor} in the end triplet; the midpoint reference is not required.", 12.5)

    legend_y, cursor = track + 152, 36.0
    for kind in ("corpus", "survives", "spare_ran", "lost", "spare_idle"):
        label = GLYPH_LABELS[kind]
        with fig.element(label):
            _glyph(fig, kind, cursor, legend_y - 4.5)
            fig.text(cursor + 15, legend_y, label, 12.5)
        cursor += 15 + text_width(label, 12.5) + 34

    # ---- panel (b): the check on an energy axis ----------------------------------------------------------
    with fig.element("Panel (b)"):
        fig.text(30, 372, "Panel (b). The reference drift check, drawn on one energy axis", 14, weight="bold")

    x0, x1, e0, e1 = 200.0, 960.0, Fraction("99.5"), Fraction("101.2")
    scale = (x1 - x0) / float(e1 - e0)

    def X(energy) -> float:
        return x0 + (float(energy) - float(e0)) * scale

    rows = {"corpus": 410, "start": 566, "mid": 610, "end": 654}
    axis_y, diff_y = 724, 694

    with fig.element("energy axis"):
        tick = Fraction("99.6")
        while tick <= e1:
            fig.line(X(tick), 392, X(tick), axis_y, stroke=GRID, width=1)
            fig.line(X(tick), axis_y, X(tick), axis_y + 5, stroke=AXIS, width=1)
            fig.text(X(tick), axis_y + 20, fmt(tick, 1), 12, anchor="middle", fill=INK2)
            tick += Fraction("0.2")
        fig.line(x0, axis_y, x1, axis_y, stroke=AXIS, width=1)
        fig.text((x0 + x1) / 2, axis_y + 40, "energy axis: energy of one reference member, in joules (J)", 12.5,
                 anchor="middle", fill=INK2)

    with fig.element("reference corpus"):
        fig.text(186, rows["corpus"] + 4, "reference corpus", 12.5, anchor="end", weight="bold")
    with fig.element("corpus member"):
        for energy in v["corpus"]:
            _glyph(fig, "corpus", X(energy), rows["corpus"])

    ordered = sorted(v["corpus"])
    low, high = ordered[:n_end], ordered[-n_start:]
    by = rows["corpus"] + 16
    gap_y = by + 46
    for label, members, mean, value in (
            (f"mean of the {n_end} lowest", low, bound["lower_end"], w["lower_end_j"]),
            (f"mean of the {n_start} highest", high, bound["upper_start"], w["upper_start_j"])):
        with fig.element(label):
            fig.polyline([(X(members[0]) - 8, by - 4), (X(members[0]) - 8, by), (X(members[-1]) + 8, by),
                          (X(members[-1]) + 8, by - 4)], stroke=INK2, width=1.2)
            fig.line(X(mean), by, X(mean), gap_y, stroke=INK2, width=1.2)
            fig.text(X(mean) - 7, by + 17, label, 12, anchor="end", fill=INK2)
            fig.text(X(mean) - 7, by + 32, f"{value} J", 12, anchor="end", fill=INK2)
    with fig.element("gap term"):
        fig.arrow(X(bound["lower_end"]), gap_y, X(bound["upper_start"]), gap_y, stroke=INK, width=1.8, both=True)
        fig.text((X(bound["lower_end"]) + X(bound["upper_start"])) / 2, gap_y + 19,
                 f"gap term: {w['upper_start_j']} {MINUS} {w['lower_end_j']} = {w['gap_term_j']} J",
                 12.5, anchor="middle", weight="bold")

    bx = 636
    with fig.element("reference drift bound"):
        fig.rect(bx - 12, 394, 342, 146, fill=PANEL, rx=6)
        fig.text(bx, 414, "reference drift bound", 12.5, weight="bold", max_width=322)
        fig.lines(bx, 431, [
            f"for {n_start} surviving references at the start, {n_end} at the end",
            "= the larger of two terms:",
            f"gap term (drawn at left): {w['gap_term_j']} J",
            "repeatability term:",
            f"{plain(reg('reference.t_975_df11'))} × {w['stddev_j']} × √(1/{n_start} + 1/{n_end}) = {w['repeatability_term_j']} J",
        ], 12, fill=INK2, leading=15.5, max_width=322)
        fig.text(bx, 512, f"reference drift bound = {w['bound_j']} J", 12.5, weight="bold")
        fig.text(bx, 529, f"(with {planned[0]} and {planned[2]} surviving references: {w['planned_bound_j']} J)", 12,
                 fill=INK2, max_width=322)

    with fig.element("start triplet"):
        fig.text(186, rows["start"] + 4, "start triplet", 12.5, anchor="end", weight="bold")
    with fig.element("midpoint reference"):
        fig.text(186, rows["mid"] + 4, "midpoint reference", 12.5, anchor="end", weight="bold")
        fig.text(X(v["midpoint"]) + 14, rows["mid"] + 4, f"{fmt(v['midpoint'], 2)} J; not read by this check", 12, fill=INK2)
    with fig.element("end triplet"):
        fig.text(186, rows["end"] + 4, "end triplet", 12.5, anchor="end", weight="bold")
    with fig.element("surviving references"):
        fig.text(186, rows["start"] + 20, f"{n_start} surviving references", 12, anchor="end", fill=INK2)
        fig.text(186, rows["end"] + 20, f"{n_end} surviving references", 12, anchor="end", fill=INK2)
    with fig.element("surviving reference"):
        for energy in v["start_planned_kept"]:
            _glyph(fig, "survives", X(energy), rows["start"])
        _glyph(fig, "survives", X(v["midpoint"]), rows["mid"])
        for energy in v["end"]:
            _glyph(fig, "survives", X(energy), rows["end"])
    with fig.element("spare that ran"):
        _glyph(fig, "spare_ran", X(v["spare"]), rows["start"])
    with fig.element("lost reference"):
        _glyph(fig, "lost", X(v["end_lost"]), rows["end"])
        fig.text(X(v["end_lost"]) - 14, rows["end"] + 4, f"lost reference, {fmt(v['end_lost'], 2)} J: not read", 12,
                 anchor="end", fill=INK2)

    for label, mean, value, members, row in (("start mean", v["start_mean"], w["start_mean_j"], v["start"], rows["start"]),
                                             ("end mean", v["end_mean"], w["end_mean_j"], v["end"], rows["end"])):
        with fig.element(label):
            # the same idiom as under the corpus: a bracket under the members, a line dropped from their mean
            fig.polyline([(X(min(members)) - 10, row + 11), (X(min(members)) - 10, row + 15),
                          (X(max(members)) + 10, row + 15), (X(max(members)) + 10, row + 11)], stroke=INK, width=1.2)
            fig.line(X(mean), row + 15, X(mean), diff_y, stroke=INK, width=1.6)
            fig.text(X(max(members)) + 16, row + 4, f"{label} {value} J", 12, fill=INK2)
    with fig.element("difference of the means"):
        fig.arrow(X(v["start_mean"]), diff_y, X(v["end_mean"]), diff_y, stroke=BLUE, width=2.2, both=True)
        fig.text(X(v["end_mean"]) + 12, diff_y + 4.5,
                 f"difference of the means: {w['end_mean_j']} {MINUS} {w['start_mean_j']} = {w['difference_j']} J",
                 12.5, weight="bold")

    with fig.element("Verdict"):
        fig.circle(40, 788, 7, fill=GOOD)
        fig.polyline([(36.4, 788.2), (39, 791), (43.8, 785)], stroke=SURFACE, width=1.8)
        fig.text(56, 793, f"Verdict: {w['difference_j']} J ≤ {w['bound_j']} J, so the reference drift check passes.",
                 14, weight="bold")
    return fig


# ---------------------------------------------------------------------------------------------------------
# Figure B-S5: the clock frequency gate.
# ---------------------------------------------------------------------------------------------------------
GATE_PLOT = {"x0": 90.0, "x1": 960.0, "y_top": 268.0, "y_bottom": 538.0,
             "f_min": 0.0, "f_max": 5.0, "ms_min": 3.5, "ms_max": 5.5}


def gate_xy(abs_f_ppm, bound_ms) -> tuple[float, float]:
    """Where a rate and a bound land in the plot of Figure B-S5."""

    p = GATE_PLOT
    x = p["x0"] + (float(abs_f_ppm) - p["f_min"]) * (p["x1"] - p["x0"]) / (p["f_max"] - p["f_min"])
    y = p["y_bottom"] - (float(bound_ms) - p["ms_min"]) * (p["y_bottom"] - p["y_top"]) / (p["ms_max"] - p["ms_min"])
    return x, y


def figure_gate() -> Figure:
    g = gate_values()
    w = worked_values()["B-S5"]
    p = GATE_PLOT
    h, margin, stream, limit = (plain(reg("clock.h_ms")), plain(reg("clock.frequency_margin_ppm")),
                                plain(reg("clock.t_stream_max_s")), plain(reg("clock.limit_ms")))
    slope = w["slope_ms_per_ppm"]
    pass_f, refuse_f = plain(g["pass_abs_f_ppm"]), plain(g["refuse_abs_f_ppm"])
    pass_ms, refuse_ms, max_f = w["pass_bound_ms"], w["refuse_bound_ms"], w["max_abs_f_ppm"]
    if not (g["pass_bound_ms"] <= reg("clock.limit_ms") < g["refuse_bound_ms"]):
        raise ValueError("the drawing says point A passes and point B is refused")
    if reg("clock.h_observed_ms") + reg("clock.h_margin_ms") != reg("clock.h_ms"):
        raise ValueError("the first term's note says 3.6 ms + 0.1 ms gives the registered 3.7 ms")

    fig = Figure(
        "B-S5", "figB_S5_frequency_gate.svg",
        "Figure B-S5. The clock check before a window starts (the frequency gate)",
        f"Computed from the registered constants. The frequency word at point A was read on this machine on "
        f"{reg('clock.example_pass_date')}; point B is hypothetical.",
        "A straight line gives the largest member clock bound the gate predicts, as a function of the size of "
        "the frequency word; a dashed horizontal line marks the 5 ms limit; the gate passes only where the "
        "line is at or below the limit. Two worked points are marked, one that passes and one that is refused.",
        1000, 688)

    with fig.element("formula"):
        fig.text(30, 94, f"formula: predicted member clock bound = {h} ms + ( |f| + {margin} ppm ) × {stream} s", 17,
                 weight="bold")
        fig.text(30, 116, f"The gate passes only if the prediction is at most {limit} ms. "
                 "A rate of 1 ppm (part per million) held for 1 s moves a clock by 1 microsecond.", 13, fill=INK2)

    chips = [
        (f"{h} ms", ["largest h in the October probe",
                      f"({plain(reg('clock.h_observed_ms'))} ms) plus {plain(reg('clock.h_margin_ms'))} ms of margin;",
                      "h: half-width of the label fit"]),
        ("|f|", ["size of the frequency word f,", "the kernel's rate correction", "for the wall clock, in ppm"]),
        (f"{margin} ppm", ["allowance for the rate differing", "during a member's stream"]),
        (f"{stream} s", ["longest stream", "any member can have"]),
    ]
    for index, (label, rows) in enumerate(chips):
        x = 30 + index * 237
        with fig.element(label):
            fig.rect(x, 130, 229, 78, fill=PANEL, rx=6)
            fig.text(x + 12, 150, label, 14, weight="bold")
            fig.lines(x + 12, 168, rows, 12, fill=INK2, leading=15, max_width=208)

    cross_x, limit_y = gate_xy(g["max_abs_f_ppm"], reg("clock.limit_ms"))

    with fig.element("REFUSE"):
        fig.rect(cross_x, p["y_top"], p["x1"] - cross_x, p["y_bottom"] - p["y_top"], fill=CRITICAL_WASH)
        fig.rect(cross_x + 1.5, 252, p["x1"] - cross_x - 1.5, 5, fill=CRITICAL)
        fig.text((cross_x + p["x1"]) / 2, 244, "REFUSE: the window does not start", 12.5, anchor="middle",
                 weight="bold", max_width=p["x1"] - cross_x)
    with fig.element("PASS"):
        fig.rect(p["x0"], 252, cross_x - p["x0"] - 1.5, 5, fill=GOOD)
        fig.text((p["x0"] + cross_x) / 2, 244, "PASS: the arm goes on to its other checks", 12.5, anchor="middle",
                 weight="bold")

    with fig.element("vertical axis"):
        for step in range(5):
            value = p["ms_min"] + step * 0.5
            _, y = gate_xy(0, value)
            fig.line(p["x0"], y, p["x1"], y, stroke=GRID, width=1)
            fig.text(p["x0"] - 10, y + 4.5, f"{value:.1f}", 12, anchor="end", fill=INK2)
        fig.line(p["x0"], p["y_top"], p["x0"], p["y_bottom"], stroke=AXIS, width=1)
        fig.text(34, (p["y_top"] + p["y_bottom"]) / 2, "vertical axis: predicted member clock bound (ms)", 12.5,
                 anchor="middle", fill=INK2, rotate=-90)
    with fig.element("horizontal axis"):
        for step in range(6):
            x, _ = gate_xy(step, p["ms_min"])
            fig.line(x, p["y_bottom"], x, p["y_bottom"] + 5, stroke=AXIS, width=1)
            fig.text(x, p["y_bottom"] + 20, str(step), 12, anchor="middle", fill=INK2)
        fig.line(p["x0"], p["y_bottom"], p["x1"], p["y_bottom"], stroke=AXIS, width=1)
        fig.text((p["x0"] + p["x1"]) / 2, p["y_bottom"] + 42,
                 "horizontal axis: |f|, the size of the frequency word (ppm)", 12.5, anchor="middle", fill=INK2)

    with fig.element(f"{limit} ms limit"):
        fig.line(p["x0"], limit_y, p["x1"], limit_y, stroke=INK, width=1.6, dash="8 5")
        fig.text(p["x0"] + 10, limit_y - 8, f"{limit} ms limit", 13, weight="bold")

    with fig.element("largest passing rate"):
        fig.line(cross_x, p["y_top"], cross_x, p["y_bottom"], stroke=INK2, width=1.2)
        fig.lines(cross_x - 9, p["y_bottom"] - 34, ["largest passing rate", f"|f| = {max_f} ppm"], 12.5,
                  anchor="end", leading=16)

    start, end = gate_xy(p["f_min"], gate_bound_ms(0)), gate_xy(p["f_max"], gate_bound_ms(5))
    with fig.element("predicted bound"):
        fig.line(start[0], start[1], end[0], end[1], stroke=BLUE, width=2.4, cap="round")
        lx, ly = gate_xy(1.0, gate_bound_ms(1))
        fig.text(lx + 6, ly + 34, f"predicted bound: rises {slope} ms for each ppm of |f|", 13, weight="bold")
    with fig.element("starting value"):
        fig.circle(start[0], start[1], 5, fill=SURFACE, stroke=BLUE, width=2.2)
        fig.text(start[0] + 14, start[1] + 22,
                 f"starting value at |f| = 0: {h} ms + {margin} ppm × {stream} s = {w['intercept_ms']} ms", 12.5)

    ax, ay = gate_xy(g["pass_abs_f_ppm"], g["pass_bound_ms"])
    bxp, byp = gate_xy(g["refuse_abs_f_ppm"], g["refuse_bound_ms"])
    with fig.element("Point A", role="worked-point", abs_f_ppm=pass_f, bound_ms=pass_ms, verdict="PASS",
                     plot_x=c(ax), plot_y=c(ay)):
        fig.line(ax, ay + 8, ax, ay + 62, stroke=INK2, width=1)
        fig.circle(ax, ay, 6.5, fill=GOOD, stroke=SURFACE, width=2)
        fig.text(ax + 10, ay + 77, f"Point A: {pass_f} ppm → {pass_ms} ms, PASS", 12.5, anchor="end", weight="bold")
    with fig.element("Point B", role="worked-point", abs_f_ppm=refuse_f, bound_ms=refuse_ms, verdict="REFUSE",
                     plot_x=c(bxp), plot_y=c(byp)):
        fig.line(bxp + 5, byp + 6, bxp + 20, byp + 30, stroke=INK2, width=1)
        fig.polygon([(bxp, byp - 8), (bxp + 8, byp), (bxp, byp + 8), (bxp - 8, byp)], fill=CRITICAL, stroke=SURFACE, width=2)
        fig.text(p["x1"] - 6, byp + 46, f"Point B: {refuse_f} ppm → {refuse_ms} ms, REFUSE", 12.5, anchor="end",
                 weight="bold")

    top = 600
    cards = [
        ("Point A", 30, "circle",
         [f"Point A: f = {plain(reg('clock.example_pass_f_ppm'))} ppm, read {reg('clock.example_pass_date')}",
          f"{h} + ({pass_f} + {margin}) × {slope} = {pass_ms} ms",
          f"{pass_ms} ms ≤ {limit} ms: PASS"]),
        ("Point B", 347, "diamond",
         [f"Point B: a hypothetical |f| = {refuse_f} ppm",
          f"{h} + ({refuse_f} + {margin}) × {slope} = {refuse_ms} ms",
          f"{refuse_ms} ms > {limit} ms: REFUSE"]),
        ("largest passing rate", 664, None,
         ["largest passing rate",
          f"({limit} {MINUS} {h}) ÷ {slope} {MINUS} {margin} = {max_f} ppm",
          "(rounded to four decimals)"]),
    ]
    for label, x, shape, rows in cards:
        with fig.element(label):
            fig.rect(x, top, 306, 74, fill=PANEL, rx=6)
            if shape == "circle":
                fig.circle(x + 18, top + 19, 6.5, fill=GOOD)
            elif shape == "diamond":
                fig.polygon([(x + 18, top + 11), (x + 26, top + 19), (x + 18, top + 27), (x + 10, top + 19)], fill=CRITICAL)
            inset = 34 if shape else 14
            fig.text(x + inset, top + 23.5, rows[0], 12.5, weight="bold", max_width=300 - inset)
            fig.lines(x + 14, top + 44, rows[1:], 12.5, fill=INK2, leading=17, max_width=284)
    return fig


# ---------------------------------------------------------------------------------------------------------
FIGURES = (figure_boundary, figure_survivors, figure_gate)


def build() -> dict[str, str]:
    """File name -> SVG text for the three figures."""

    return {figure.filename: figure.svg() for figure in (make() for make in FIGURES)}


def element_labels() -> dict[str, list[str]]:
    """Figure key (B-S2, B-S4, B-S5) -> the labels of its drawn elements, in first-drawn order."""

    return {figure.key: list(figure.labels) for figure in (make() for make in FIGURES)}


def main(argv: list[str]) -> int:
    check = "--check" in argv
    stale = []
    for name, text in build().items():
        path = HERE / name
        if check:
            if not path.is_file() or path.read_bytes() != text.encode("utf-8"):
                stale.append(name)
        else:
            path.write_bytes(text.encode("utf-8"))
            print(f"wrote {path}")
    for name in stale:
        print(f"differs from the builder's output: {name}", file=sys.stderr)
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
