#!/usr/bin/env python3
"""Generate number-free result-figure SKELETONS for the JouleWise MVP paper.

Reads docs/paper/figures-plan.md at the audited head and emits one SVG skeleton
per planned result figure (A-E) into figures-skeletons/.

Conventions follow docs/paper/figures/*.svg: 1020-wide white canvas, sans-serif,
title at y=32 + subtitle at y=54, #333333 axes, #ececec grid, #1b6ca8 accent,
role="img" with <title>/<desc>, non-ASCII emitted as numeric character refs.

Hard rules honoured here:
  * NUMBER-FREE. No numeric axis tick label, no data value, no threshold value
    appears in any emitted skeleton. (SVG geometry coordinates are layout, not
    content.)
  * Caption stub and the mandatory D-119 disclosure line are lifted VERBATIM
    from figures-plan.md by parse, never retyped.
  * Every panel carries a STOP_FILL badge and every canvas carries a STOP_FILL
    watermark, per the plan's own rule that every panel stays STOP_FILL.
  * Mark placeholders are keyed by registry row tokens, printed literally.
"""

from __future__ import annotations

import html
import re
import textwrap
from pathlib import Path

WT = Path(
    "/private/tmp/claude-501/-Users-edr-code-JouleWise/"
    "cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS0"
)
PLAN = WT / "docs/paper/figures-plan.md"
OUT = Path(__file__).resolve().parent / "figures-skeletons"

INK = "#1b1b1b"
BODY = "#333333"
MUTE = "#555555"
AXIS = "#333333"
GRID = "#ececec"
RULE = "#9a9a9a"
ACCENT = "#1b6ca8"
STOPC = "#a33"

W = 1020


# --------------------------------------------------------------------------
# verbatim caption extraction
# --------------------------------------------------------------------------
def parse_plan() -> dict[str, dict[str, str]]:
    text = PLAN.read_text(encoding="utf-8")
    blocks: dict[str, dict[str, str]] = {}
    # split on the figure headings
    parts = re.split(r"^## (Figure [A-E]) [^\n]*$", text, flags=re.M)
    # parts = [pre, 'Figure A', body, 'Figure B', body, ...]
    for i in range(1, len(parts), 2):
        key = parts[i].split()[-1]  # A..E
        body = parts[i + 1]
        out = {}
        for label, field in (
            ("Number-free caption stub.", "caption"),
            ("Mandatory D-119 disclosure line.", "d119"),
        ):
            m = re.search(
                r"\*\*" + re.escape(label) + r"\*\*\s*(.*?)(?=\n\n)", body, re.S
            )
            if not m:
                raise SystemExit(f"missing {label} for Figure {key}")
            # unwrap the markdown hard-wrap; join hyphen-broken words
            raw = m.group(1)
            raw = re.sub(r"-\n\s*", "-", raw)
            raw = re.sub(r"\s*\n\s*", " ", raw).strip()
            out[field] = raw
        blocks[key] = out
    return blocks


# --------------------------------------------------------------------------
# emit helpers
# --------------------------------------------------------------------------
def esc(s: str) -> str:
    s = html.escape(s, quote=False)
    return "".join(c if ord(c) < 128 else f"&#{ord(c)};" for c in s)


def txt(x, y, s, size=12.5, fill=BODY, weight=None, anchor=None,
        family="sans-serif", extra="") -> str:
    a = f' font-family="{family}" font-size="{size}" fill="{fill}"'
    if weight:
        a += f' font-weight="{weight}"'
    if anchor:
        a += f' text-anchor="{anchor}"'
    if extra:
        a += " " + extra
    return f'  <text x="{x}" y="{y}"{a}>{esc(s)}</text>'


def wrapped(x, y, s, width=128, size=12.5, fill=BODY, lh=17, family="sans-serif",
            weight=None) -> tuple[list[str], float]:
    out = []
    yy = y
    for line in textwrap.wrap(s, width=width):
        out.append(txt(x, yy, line, size=size, fill=fill, family=family,
                       weight=weight))
        yy += lh
    return out, yy


def token(x, y, tok, size=9.5, fill=ACCENT, anchor="middle") -> str:
    return txt(x, y, tok, size=size, fill=fill, anchor=anchor,
               family="monospace")


def stop_badge(x, y, w=104, h=20, label="STOP_FILL") -> list[str]:
    return [
        f'  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#ffffff"'
        f' stroke="{STOPC}" stroke-width="1.8" stroke-dasharray="5 3"/>',
        txt(x + w / 2, y + 14, label, size=11.5, fill=STOPC, weight="bold",
            anchor="middle", extra='letter-spacing="0.8"'),
    ]


def watermark(cx, cy, size=118) -> list[str]:
    return [
        f'  <g opacity="0.085" transform="rotate(-24 {cx} {cy})">',
        txt(cx, cy, "STOP_FILL", size=size, fill=STOPC, weight="bold",
            anchor="middle", extra='letter-spacing="10"'),
        "  </g>",
    ]


def slot(x, ytop, ybot, w=34, dash="6 4") -> list[str]:
    """An 'unissued value' vertical slot: no magnitude is implied."""
    return [
        f'  <rect x="{x - w / 2}" y="{ytop}" width="{w}" height="{ybot - ytop}"'
        f' fill="{ACCENT}" fill-opacity="0.045" stroke="{ACCENT}"'
        f' stroke-width="1.5" stroke-dasharray="{dash}"/>',
        txt(x, (ytop + ybot) / 2 + 6, "?", size=17, fill=ACCENT, weight="bold",
            anchor="middle"),
    ]


def hollow(cx, cy, kind="circle", r=7, color=ACCENT) -> str:
    if kind == "circle":
        return (f'  <circle cx="{cx}" cy="{cy}" r="{r}" fill="#ffffff"'
                f' stroke="{color}" stroke-width="2.2"/>')
    if kind == "square":
        return (f'  <rect x="{cx - r}" y="{cy - r}" width="{2 * r}"'
                f' height="{2 * r}" fill="#ffffff" stroke="{color}"'
                f' stroke-width="2.2"/>')
    if kind == "diamond":
        return (f'  <path d="M{cx},{cy - r - 1} L{cx + r + 1},{cy}'
                f' L{cx},{cy + r + 1} L{cx - r - 1},{cy} z" fill="#ffffff"'
                f' stroke="{color}" stroke-width="2.4"/>')
    if kind == "triangle":
        return (f'  <path d="M{cx},{cy - r - 1} L{cx + r + 1},{cy + r}'
                f' L{cx - r - 1},{cy + r} z" fill="#ffffff" stroke="{color}"'
                f' stroke-width="2.2"/>')
    raise ValueError(kind)


def yaxis(x, ytop, ybot, label, note) -> list[str]:
    mid = (ytop + ybot) / 2
    return [
        f'  <line x1="{x}" y1="{ytop}" x2="{x}" y2="{ybot}" stroke="{AXIS}"'
        f' stroke-width="1.8"/>',
        txt(x - 40, mid, label, size=12.5, fill=INK, anchor="middle",
            extra=f'transform="rotate(-90 {x - 40} {mid})"'),
        txt(x - 24, mid, note, size=10, fill=MUTE, anchor="middle",
            extra=f'transform="rotate(-90 {x - 24} {mid})"'),
    ]


def xaxis(x0, x1, y, label) -> list[str]:
    return [
        f'  <line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{AXIS}"'
        f' stroke-width="1.8"/>',
        txt((x0 + x1) / 2, y + 999, ""),  # placeholder removed below
    ][:1] + [txt((x0 + x1) / 2, y + 0, "")][:0] + [
        txt((x0 + x1) / 2, y + 34, label, size=12.5, fill=INK, anchor="middle")
    ]


def gridlines(x0, x1, ys) -> list[str]:
    out = [f'  <g stroke="{GRID}" stroke-width="1.5">']
    for y in ys:
        out.append(f'    <line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}"/>')
    out.append("  </g>")
    return out


def caption_block(y, cap, d119, rows_note) -> tuple[list[str], float]:
    out = [f'  <line x1="40" y1="{y}" x2="{W - 40}" y2="{y}" stroke="#e2e2e2"'
           f' stroke-width="1.5"/>']
    yy = y + 24
    out.append(txt(40, yy, "Number-free caption stub (verbatim from "
                           "docs/paper/figures-plan.md):", size=12,
                   fill=MUTE, weight="bold"))
    yy += 19
    lines, yy = wrapped(40, yy, cap, width=132, size=12.5, fill=INK)
    out += lines
    yy += 9
    out.append(txt(40, yy, "Mandatory D-119 disclosure line (verbatim; may be "
                           "replaced only by weaker wording):", size=12,
                   fill=MUTE, weight="bold"))
    yy += 19
    lines, yy = wrapped(40, yy, d119, width=132, size=12.5, fill=INK)
    out += lines
    yy += 9
    lines, yy = wrapped(40, yy, rows_note, width=150, size=11, fill=MUTE)
    out += lines
    return out, yy


def head(fid, title, subtitle, desc, height, gate) -> list[str]:
    t = f"fig{fid}title"
    d = f"fig{fid}desc"
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}"'
        f' viewBox="0 0 {W} {height}" role="img" aria-labelledby="{t} {d}">',
        f'  <title id="{t}">{esc(title)}</title>',
        f'  <desc id="{d}">{esc(desc)}</desc>',
        f'  <rect x="0" y="0" width="{W}" height="{height}" fill="#ffffff"/>',
        txt(40, 32, title, size=18, fill=INK, weight="bold"),
        txt(40, 54, subtitle, size=13, fill=MUTE),
    ]
    out += stop_badge(W - 40 - 190, 16, w=190, h=26,
                      label="STOP_FILL - NO PANEL RENDERS")
    lines, _ = wrapped(40, 74, gate, width=150, size=11, fill=STOPC)
    out += lines
    return out


def tail() -> list[str]:
    return ["</svg>", ""]


def finalize(svg: str) -> str:
    """Size the canvas to the content it actually holds.

    Figures are emitted with a __H__ placeholder so the caption block, whose
    height depends on the verbatim wrap of the plan text, can never be clipped.
    """
    maxy = 0.0
    for m in re.finditer(r'\sy="(-?[\d.]+)"', svg):
        maxy = max(maxy, float(m.group(1)))
    for m in re.finditer(r'\sy1="(-?[\d.]+)"', svg):
        maxy = max(maxy, float(m.group(1)))
    for m in re.finditer(r'\sy2="(-?[\d.]+)"', svg):
        maxy = max(maxy, float(m.group(1)))
    for m in re.finditer(r'\sy="(-?[\d.]+)"\s+width="[\d.]+"\s+height="([\d.]+)"',
                         svg):
        maxy = max(maxy, float(m.group(1)) + float(m.group(2)))
    h = int(maxy) + 30
    return svg.replace("__H__", str(h))


def legend(x, y, items) -> list[str]:
    """items: list of (kind|'slot'|'band', label)"""
    out = []
    cx = x
    for kind, label in items:
        if kind == "slot":
            out.append(f'  <rect x="{cx}" y="{y - 9}" width="20" height="18"'
                       f' fill="{ACCENT}" fill-opacity="0.045"'
                       f' stroke="{ACCENT}" stroke-width="1.5"'
                       f' stroke-dasharray="6 4"/>')
        elif kind == "band":
            out.append(f'  <rect x="{cx}" y="{y - 7}" width="20" height="14"'
                       f' fill="#bbbbbb" fill-opacity="0.25" stroke="#888888"'
                       f' stroke-width="1.3" stroke-dasharray="4 3"/>')
        else:
            out.append(hollow(cx + 10, y, kind))
        out.append(txt(cx + 26, y + 4, label, size=11.5, fill=BODY))
        cx += 26 + 6.3 * len(label) + 26
    return out


# --------------------------------------------------------------------------
# Figure A - phase-floor composition
# --------------------------------------------------------------------------
def fig_a(cap) -> str:
    H = "__H__"
    PX0, PX1, PY0, PY1 = 130, 970, 120, 400
    cells = [
        ("1.5B / prompt processing", "F_1p5B_prompt"),
        ("1.5B / token generation", "F_1p5B_decode"),
        ("7B / prompt processing", "F_7B_prompt"),
        ("7B / token generation", "F_7B_decode"),
    ]
    o = head(
        "A",
        "Figure A (skeleton). Phase-floor composition",
        "Number-free skeleton. No value, scale, or ordering is implied; every "
        "mark below is an unissued placeholder.",
        "Skeleton for the phase-floor composition figure. Four model-and-phase "
        "cells on the horizontal axis; energy in joules on the vertical axis "
        "with no numeric scale. Each cell carries three unfilled mark "
        "placeholders - absolute component, comparative component, and "
        "operative component maximum - keyed by their results-fill-registry "
        "row tokens. Components are never stacked. The whole figure is marked "
        "STOP_FILL and contains no measured data and no numbers.",
        H,
        "Render gate (plan): every cited component must be exact and "
        "authenticated, each cell must select its licensed publication branch, "
        "and the derived maximum must match the artifact's floor_gate_j; "
        "otherwise omit or refuse the affected cell exactly as the registry directs.",
    )
    o += watermark((PX0 + PX1) / 2, (PY0 + PY1) / 2, 122)
    o += gridlines(PX0, PX1, [400, 344, 288, 232, 176, 120])
    o += yaxis(PX0, PY0, PY1, "energy (joules)", "no numeric scale: values unissued")

    step = (PX1 - PX0) / len(cells)
    for i, (label, stem) in enumerate(cells):
        gc = PX0 + step * (i + 0.5)
        if i:
            o.append(f'  <line x1="{PX0 + step * i}" y1="{PY0 - 8}"'
                     f' x2="{PX0 + step * i}" y2="{PY1 + 8}" stroke="#dddddd"'
                     f' stroke-width="1.2" stroke-dasharray="3 4"/>')
        for j, (dx, kind, suffix) in enumerate((
            (-58, "circle", "abs_J"),
            (0, "square", "cmp_J"),
            (58, "diamond", "operative_J"),
        )):
            x = gc + dx
            o += slot(x, PY0 + 20, PY1 - 20)
            o.append(hollow(x, (PY0 + PY1) / 2 - 34, kind))
        o.append(txt(gc, PY1 + 24, label, size=12.5, fill=INK, anchor="middle",
                     weight="bold"))
        for k, suffix in enumerate(("abs_J", "cmp_J", "operative_J")):
            o.append(token(gc, PY1 + 44 + 14 * k, f"[{stem}_{suffix}]"))
        o += stop_badge(gc - 42, PY1 + 92, w=84, h=18)

    o += xaxis(PX0, PX1, PY1, "")
    o.append(txt((PX0 + PX1) / 2, PY1 + 132, "model-and-phase cell",
                 size=12.5, fill=INK, anchor="middle"))
    o += legend(130, PY1 + 162, [
        ("circle", "absolute component (placeholder)"),
        ("square", "comparative component (placeholder)"),
        ("diamond", "operative component maximum (placeholder)"),
    ])
    o.append(txt(130, PY1 + 186,
                 "Components are NOT stacked: the operative floor is the "
                 "larger authenticated component, never their sum.",
                 size=11.5, fill=BODY))

    blk, _ = caption_block(
        PY1 + 206, cap["caption"], cap["d119"],
        "Registry rows consumed: the twelve alpha/beta floor-cell tokens "
        "[F_1p5B_prompt_abs_J] [F_1p5B_prompt_cmp_J] [F_1p5B_prompt_operative_J] "
        "[F_1p5B_decode_abs_J] [F_1p5B_decode_cmp_J] [F_1p5B_decode_operative_J] "
        "[F_7B_prompt_abs_J] [F_7B_prompt_cmp_J] [F_7B_prompt_operative_J] "
        "[F_7B_decode_abs_J] [F_7B_decode_cmp_J] [F_7B_decode_operative_J]. "
        "Freeze status at audit: KEY_FROZEN / VALUE_UNISSUED (MEASURED components) "
        "and DERIVATION_FROZEN / VALUE_UNISSUED (operative maxima). Branch text "
        "for a refused or no-exact-floor cell comes from the TERMINAL_REFUSAL_REASON_*, "
        "NO_EXACT_FLOOR_REASON_*, AVAILABLE_DIAGNOSTIC_CLAUSE_* and "
        "POINT_DIAGNOSTIC_CLAUSE_* rows, never from this figure.")
    o += blk
    return finalize("\n".join(o + tail()))


# --------------------------------------------------------------------------
# Figure B - phase-energy means and composed intervals
# --------------------------------------------------------------------------
def fig_b(cap) -> str:
    H = "__H__"
    PX0, PX1, PY0, PY1 = 130, 970, 120, 410
    groups = [
        ("1.5B", [("prompt processing", "1p5B_prompt", "J_per_token"),
                  ("token generation", "1p5B_decode", "J_per_token")]),
        ("7B", [("prompt processing", "7B_prompt", "J_per_token"),
                ("token generation", "7B_decode", "J_per_token")]),
    ]
    o = head(
        "B",
        "Figure B (skeleton). Phase-energy means and fully composed intervals",
        "Number-free skeleton. Mean marks, interval placeholders, and floor "
        "references are unfilled; no scale or ordering is implied.",
        "Skeleton for the phase-energy mean figure. Phase grouped by model on "
        "the horizontal axis; gross energy per request in joules on the "
        "vertical axis with no numeric scale. Each phase carries an unfilled "
        "reported-mean mark, an unfilled fully composed interval placeholder, "
        "and a visually distinct operative-floor reference glyph that is not "
        "an error bar. Independent valid-bundle counts and token-normalized "
        "companions are annotation placeholders. The whole figure is marked "
        "STOP_FILL; every D-123 supplier is unknown.",
        H,
        "Render gate (plan): currently STOP_FILL - the registry marks every "
        "D-123 mean, interval, companion, and count supplier UNKNOWN. Do not "
        "substitute the absolute floor component's internal mean or count.",
    )
    o += watermark((PX0 + PX1) / 2, (PY0 + PY1) / 2, 122)
    o += gridlines(PX0, PX1, [410, 352, 294, 236, 178, 120])
    o += yaxis(PX0, PY0, PY1, "gross energy per request (joules)",
               "no numeric scale: values unissued")

    gstep = (PX1 - PX0) / len(groups)
    for gi, (model, phases) in enumerate(groups):
        gx0 = PX0 + gstep * gi
        if gi:
            o.append(f'  <line x1="{gx0}" y1="{PY0 - 8}" x2="{gx0}"'
                     f' y2="{PY1 + 118}" stroke="#cccccc" stroke-width="1.4"/>')
        pstep = gstep / len(phases)
        for pi, (phase, stem, _) in enumerate(phases):
            cx = gx0 + pstep * (pi + 0.5)
            ix = cx - 26
            # composed interval placeholder
            o.append(f'  <line x1="{ix}" y1="{PY0 + 34}" x2="{ix}"'
                     f' y2="{PY1 - 34}" stroke="{ACCENT}" stroke-width="2.2"'
                     f' stroke-dasharray="7 5"/>')
            for cy in (PY0 + 34, PY1 - 34):
                o.append(f'  <line x1="{ix - 11}" y1="{cy}" x2="{ix + 11}"'
                         f' y2="{cy}" stroke="{ACCENT}" stroke-width="2.2"/>')
            o.append(hollow(ix, (PY0 + PY1) / 2, "circle", r=8))
            o.append(txt(ix, (PY0 + PY1) / 2 - 16, "?", size=14, fill=ACCENT,
                         weight="bold", anchor="middle"))
            # distinct floor reference glyph, deliberately offset
            o.append(hollow(cx + 34, (PY0 + PY1) / 2 + 40, "triangle", r=8,
                            color="#6a6a6a"))
            o.append(txt(cx + 34, (PY0 + PY1) / 2 + 66, "floor ref.", size=10,
                         fill="#6a6a6a", anchor="middle"))
            o.append(txt(cx + 34, (PY0 + PY1) / 2 + 78, "(not an error bar)",
                         size=9, fill="#6a6a6a", anchor="middle"))

            o.append(txt(cx, PY1 + 24, phase, size=12, fill=INK,
                         anchor="middle", weight="bold"))
            toks = [
                f"[E_{stem}_J_per_request]",
                f"[E_{stem}_lower_J]",
                f"[E_{stem}_upper_J]",
                f"[E_{stem}_J_per_token]",
                f"[N_bundles_{stem}]",
                f"[F_{stem}_operative_J]",
            ]
            for k, t in enumerate(toks):
                col = "#6a6a6a" if k == 5 else ACCENT
                o.append(token(cx, PY1 + 42 + 13 * k, t, fill=col))
            o += stop_badge(cx - 42, PY1 + 124, w=84, h=18)
        o.append(txt(gx0 + gstep / 2, PY1 + 160, f"model: {model}", size=13,
                     fill=INK, anchor="middle", weight="bold"))

    o += xaxis(PX0, PX1, PY1, "")
    o.append(txt((PX0 + PX1) / 2, PY1 + 184, "phase, grouped by model",
                 size=12.5, fill=INK, anchor="middle"))
    o += legend(130, PY1 + 212, [
        ("circle", "reported mean (placeholder)"),
        ("triangle", "operative floor reference (distinct glyph, never an error bar)"),
    ])
    o.append(txt(130, PY1 + 236,
                 "The dashed vertical rule at each phase is the fully composed "
                 "lower-to-upper interval placeholder; per-token companions "
                 "stay table annotations.", size=11.5, fill=BODY))

    blk, _ = caption_block(
        PY1 + 256, cap["caption"], cap["d119"],
        "Registry rows consumed: sixteen D-123 mean/interval/companion tokens "
        "[E_*_J_per_request] [E_*_lower_J] [E_*_upper_J] [E_*_J_per_token], four "
        "count tokens [N_bundles_*], and the four operative-floor tokens from "
        "Figure A used only as clearly distinct floor references. Freeze status "
        "at audit: all twenty D-123 rows are STOP_FILL / SUPPLIER_UNKNOWN - the "
        "reported-mean artifact field, its admitted member basis, its composed "
        "interval endpoints, and its runtime-observed per-token companions are "
        "undefined in the repository.")
    o += blk
    return finalize("\n".join(o + tail()))


# --------------------------------------------------------------------------
# Figure C - registered model-size contrasts and separate gates
# --------------------------------------------------------------------------
def fig_c(cap) -> str:
    H = "__H__"
    PX0, PX1, PY0, PY1 = 150, 700, 120, 420
    ZERO = (PY0 + PY1) / 2
    o = head(
        "C",
        "Figure C (skeleton). Registered model-size contrasts, with floor and "
        "direction kept separate",
        "Number-free skeleton. Signed axis is oriented larger model minus "
        "smaller model; no magnitude, sign, or threshold is implied.",
        "Skeleton for the model-size contrast figure. Registered phase "
        "contrasts on the horizontal axis; signed model-size difference in "
        "joules per request on the vertical axis, oriented larger model minus "
        "smaller model, with an unlabelled zero rule. The token-generation "
        "contrast carries an unfilled point estimate and an unfilled fully "
        "composed interval, plus a symmetric armwise floor-magnitude reference "
        "drawn about zero. The prompt-processing contrast is drawn as a missing "
        "token family, not as a value. Floor-plus-claim-bound disclosure is "
        "caption-only and is never drawn as a decision threshold. The whole "
        "figure is marked STOP_FILL.",
        H,
        "Render gate (plan): decode remains blocked on the unknown "
        "claim-side-bound binding where that disclosure is used. Prompt "
        "processing remains STOP_FILL until the lead-owned draft/template train "
        "adds the D-122 token family and gamma supplies the corresponding "
        "issued contrast row.",
    )
    o += watermark((PX0 + PX1) / 2, ZERO, 108)
    o += gridlines(PX0, PX1, [PY0, PY0 + 60, ZERO, PY1 - 60, PY1])
    o += yaxis(PX0, PY0, PY1,
               "signed difference (joules per request), larger minus smaller",
               "no numeric scale: values unissued")

    # zero rule (unlabelled numerically)
    o.append(f'  <line x1="{PX0}" y1="{ZERO}" x2="{PX1}" y2="{ZERO}"'
             f' stroke="{AXIS}" stroke-width="2"/>')
    o.append(txt(PX0 - 8, ZERO + 4, "zero", size=11, fill=MUTE, anchor="end"))

    # symmetric armwise floor reference about zero
    for sgn in (-1, 1):
        y = ZERO + sgn * 62
        o.append(f'  <line x1="{PX0}" y1="{y}" x2="{PX1}" y2="{y}"'
                 f' stroke="#6a6a6a" stroke-width="1.6" stroke-dasharray="9 6"/>')
    o.append(f'  <rect x="{PX0}" y="{ZERO - 62}" width="{PX1 - PX0}"'
             f' height="124" fill="#bbbbbb" fill-opacity="0.16"/>')
    o.append(txt(PX1 - 8, ZERO - 68, "armwise floor magnitude, drawn "
                 "symmetrically about zero (reference only)", size=10.5,
                 fill="#5a5a5a", anchor="end"))
    o.append(token(PX1 - 8, ZERO + 80, "[F_claim_decode_armwise_max_J]",
                   fill="#5a5a5a", anchor="end"))

    # decode contrast slot
    dx = PX0 + (PX1 - PX0) * 0.30
    o.append(f'  <line x1="{dx}" y1="{PY0 + 26}" x2="{dx}" y2="{PY1 - 26}"'
             f' stroke="{ACCENT}" stroke-width="2.4" stroke-dasharray="7 5"/>')
    for cy in (PY0 + 26, PY1 - 26):
        o.append(f'  <line x1="{dx - 13}" y1="{cy}" x2="{dx + 13}" y2="{cy}"'
                 f' stroke="{ACCENT}" stroke-width="2.4"/>')
    o.append(hollow(dx, ZERO - 6, "circle", r=8))
    o.append(txt(dx, ZERO - 26, "?", size=15, fill=ACCENT, weight="bold",
                 anchor="middle"))
    o.append(txt(dx, PY1 + 24, "token generation", size=12.5, fill=INK,
                 anchor="middle", weight="bold"))
    for k, t in enumerate((
        "[E_decode_contrast_signed_J_per_request]",
        "[E_decode_contrast_lower_J]",
        "[E_decode_contrast_upper_J]",
        "[M_decode_contrast_abs_J_per_request]",
    )):
        o.append(token(dx, PY1 + 42 + 13 * k, t))
    o += stop_badge(dx - 42, PY1 + 100, w=84, h=18)

    # prompt contrast: token family missing
    px = PX0 + (PX1 - PX0) * 0.74
    o.append(f'  <rect x="{px - 88}" y="{PY0 + 26}" width="176"'
             f' height="{PY1 - 26 - (PY0 + 26)}" fill="#ffffff"'
             f' stroke="{STOPC}" stroke-width="2" stroke-dasharray="8 5"/>')
    o.append(txt(px, ZERO - 22, "NO TOKEN FAMILY", size=13, fill=STOPC,
                 weight="bold", anchor="middle"))
    o.append(txt(px, ZERO - 2, "D-122 prompt contrast arm is", size=11,
                 fill=STOPC, anchor="middle"))
    o.append(txt(px, ZERO + 14, "required but unregistered in the", size=11,
                 fill=STOPC, anchor="middle"))
    o.append(txt(px, ZERO + 30, "binding template vocabulary", size=11,
                 fill=STOPC, anchor="middle"))
    o.append(txt(px, PY1 + 24, "prompt processing (256-token)", size=12.5,
                 fill=INK, anchor="middle", weight="bold"))
    o.append(token(px, PY1 + 42, 'registry discrepancy row:'))
    o.append(token(px, PY1 + 55, '"Gamma prompt-processing contrast"'))
    o += stop_badge(px - 42, PY1 + 100, w=84, h=18)

    o += xaxis(PX0, PX1, PY1, "")
    o.append(txt((PX0 + PX1) / 2, PY1 + 136, "registered phase contrast",
                 size=12.5, fill=INK, anchor="middle"))

    # caption-only disclosure box, deliberately off the plot
    bx, by = 730, 120
    o.append(f'  <rect x="{bx}" y="{by}" width="240" height="300" rx="4"'
             f' fill="#fafafa" stroke="#999999" stroke-width="1.6"'
             f' stroke-dasharray="6 4"/>')
    o.append(txt(bx + 120, by + 24, "CAPTION-ONLY DISCLOSURE", size=11.5,
                 fill=INK, weight="bold", anchor="middle"))
    o.append(txt(bx + 120, by + 40, "never plotted, never a threshold",
                 size=10.5, fill=MUTE, anchor="middle"))
    for k, t in enumerate(("[B_decode_claim_J]", "[S_decode_joint_J]")):
        o.append(token(bx + 120, by + 64 + 15 * k, t))
    lines, yy = wrapped(bx + 12, by + 106,
                        "The claim-side bound and the floor-plus-claim-bound "
                        "sum are sizing disclosures. They are reported beside "
                        "the figure and are never drawn as an acceptance "
                        "threshold; the decision interval is never compared "
                        "with the sum.", width=34, size=10.5, fill=BODY, lh=14)
    o += lines
    o.append(txt(bx + 120, yy + 12, "DERIVED ANNOTATIONS", size=11,
                 fill=INK, weight="bold", anchor="middle"))
    for k, t in enumerate((
        "[C_decode_floor_clearance_J]",
        "[S_decode_floor_shortfall_J]",
        "[R_decode_effect_x_floor]",
        "[CELL_NONPUBLICATION_SUMMARY]",
    )):
        o.append(token(bx + 120, yy + 32 + 14 * k, t))
    o += stop_badge(bx + 78, yy + 96, w=84, h=18)

    lines, _ = wrapped(150, PY1 + 168,
                       "Floor clearance is evaluated on magnitude; direction is "
                       "evaluated separately from the fully composed interval "
                       "and the registered direction. The two gates are never "
                       "merged.", width=124, size=11.5, fill=BODY, lh=16)
    o += lines
    o += legend(150, PY1 + 194, [
        ("circle", "signed point estimate (placeholder)"),
        ("band", "armwise floor magnitude reference"),
    ])

    blk, _ = caption_block(
        PY1 + 214, cap["caption"], cap["d119"],
        "Registry rows consumed: [E_decode_contrast_signed_J_per_request] "
        "[E_decode_contrast_lower_J] [E_decode_contrast_upper_J] "
        "[M_decode_contrast_abs_J_per_request] [F_claim_decode_armwise_max_J] "
        "[C_decode_floor_clearance_J] [S_decode_floor_shortfall_J] "
        "[R_decode_effect_x_floor]; [B_decode_claim_J] and [S_decode_joint_J] "
        "for caption disclosure only; plus the registry's Gamma "
        "prompt-processing contrast discrepancy row pending a D-122-compliant "
        "prompt token family. Freeze status at audit: MEASURED gamma rows are "
        "KEY_FROZEN / VALUE_UNISSUED, the derived rows are DERIVATION_FROZEN / "
        "VALUE_UNISSUED, and [B_decode_claim_J] is STOP_FILL / SUPPLIER_UNKNOWN, "
        "which also blocks [S_decode_joint_J]. Per D-124 the common-mode "
        "estimator identity and its block-timescale stationarity/transfer "
        "assumption must be disclosed beside this figure, together with the "
        "statement that historical evidence bounded the errors but did not "
        "observe realized member-level edge errors.")
    o += blk
    return finalize("\n".join(o + tail()))


# --------------------------------------------------------------------------
# Figure D - known-signal characterization (three panels)
# --------------------------------------------------------------------------
def fig_d(cap) -> str:
    H = "__H__"
    PY0, PY1 = 130, 400
    panels = [
        dict(
            x0=110, x1=390,
            title="D1  linearity",
            ylab="energy (joules)",
            xlab="runtime-observed output tokens",
            zero=False,
            toks=["[S_C_linearity_request_J_per_token]",
                  "[S_C_linearity_decode_J_per_token]",
                  "[R_C_linearity_limit_J]",
                  "[PLAIN_LANGUAGE_RESULT_linearity]",
                  "[D_C_linearity_diagnostic_J_per_token]"],
            note="fitted slope annotated in joules per token; any acceptance "
                 "band drawn only from a frozen criterion",
        ),
        dict(
            x0=430, x1=680,
            title="D2  null response",
            ylab="signed ABBA difference (joules)",
            xlab="registered output-magnitude condition",
            zero=True,
            toks=["[D_C_null_max_abs_J]",
                  "[PLAIN_LANGUAGE_RESULT_null]",
                  "[D_C_null_diagnostic_J]"],
            note="short, medium, and long registered magnitudes; a null result "
                 "is read against the floor, never as no difference",
        ),
        dict(
            x0=720, x1=970,
            title="D3  empirical floor",
            ylab="effect divided by operative floor (dimensionless)",
            xlab="registered micro-difference condition",
            zero=False,
            toks=["[R_C_micro_min_x_floor]",
                  "[R_C_micro_max_x_floor]",
                  "[PLAIN_LANGUAGE_RESULT_floor]",
                  "[D_C_micro_diagnostic_x_floor]"],
            note="dimensionless ratio; the draft row this serves was rewritten "
                 "to an internal decision-path challenge - see registry audit "
                 "row DS-04",
        ),
    ]
    o = head(
        "D",
        "Figure D (skeleton). Known-signal characterization",
        "Number-free skeleton, three panels. No slope, band, ratio, or "
        "condition value is drawn; the characterization schema does not exist.",
        "Skeleton for the known-signal characterization figure. Three panels: "
        "linearity with output tokens against energy and an unfilled slope "
        "annotation; null response with registered output-magnitude conditions "
        "against signed A/B/B/A difference about an unlabelled zero rule; and "
        "empirical floor with registered micro-difference conditions against a "
        "dimensionless effect-to-floor ratio. Every mark is an unissued "
        "placeholder keyed by its registry row token. All three panels are "
        "marked STOP_FILL because the characterization report schema and every "
        "cited output field are supplier-unknown.",
        H,
        "Render gate (plan): currently STOP_FILL - the characterization report "
        "schema and all cited output fields are SUPPLIER_UNKNOWN in the registry.",
    )
    o += watermark(540, (PY0 + PY1) / 2, 122)

    for p in panels:
        x0, x1 = p["x0"], p["x1"]
        mid = (x0 + x1) / 2
        o += gridlines(x0, x1, [PY1, PY1 - 54, PY1 - 108, PY1 - 162, PY0])
        o += yaxis(x0, PY0, PY1, p["ylab"], "no numeric scale")
        o.append(f'  <line x1="{x0}" y1="{PY1}" x2="{x1}" y2="{PY1}"'
                 f' stroke="{AXIS}" stroke-width="1.8"/>')
        o.append(txt(mid, PY0 - 22, p["title"], size=13, fill=INK,
                     weight="bold", anchor="middle"))

        if p["zero"]:
            zy = (PY0 + PY1) / 2
            o.append(f'  <line x1="{x0}" y1="{zy}" x2="{x1}" y2="{zy}"'
                     f' stroke="{AXIS}" stroke-width="1.8"/>')
            o.append(txt(x0 - 8, zy + 4, "zero", size=10, fill=MUTE,
                         anchor="end"))
            for k in range(3):
                cx = x0 + (x1 - x0) * (0.22 + 0.28 * k)
                o.append(f'  <line x1="{cx}" y1="{zy - 46}" x2="{cx}"'
                         f' y2="{zy + 46}" stroke="{ACCENT}" stroke-width="2"'
                         f' stroke-dasharray="6 4"/>')
                o.append(hollow(cx, zy, "square", r=6))
                o.append(f'  <line x1="{cx}" y1="{PY1}" x2="{cx}"'
                         f' y2="{PY1 + 6}" stroke="{AXIS}" stroke-width="1.5"/>')
        elif p["title"].startswith("D1"):
            # unfilled trend placeholder + acceptance-band placeholder
            o.append(f'  <rect x="{x0 + 12}" y="{PY0 + 18}"'
                     f' width="{x1 - x0 - 24}" height="{PY1 - PY0 - 36}"'
                     f' fill="{ACCENT}" fill-opacity="0.045" stroke="{ACCENT}"'
                     f' stroke-width="1.5" stroke-dasharray="6 4"/>')
            o.append(f'  <line x1="{x0 + 26}" y1="{PY1 - 26}"'
                     f' x2="{x1 - 26}" y2="{PY0 + 34}" stroke="{ACCENT}"'
                     f' stroke-width="2" stroke-dasharray="10 7"/>')
            for t in (0.25, 0.5, 0.75):
                cx = x0 + 26 + (x1 - 52 - x0) * t
                cy = PY1 - 26 - (PY1 - 60 - PY0) * t
                o.append(hollow(cx, cy, "circle", r=6))
            o.append(txt(mid, PY0 + 6, "slope placeholder (J per token)",
                         size=10.5, fill=ACCENT, anchor="middle"))
            o.append(txt(mid, PY1 - 8, "residual acceptance band: unissued "
                         "criterion", size=10, fill=MUTE, anchor="middle"))
        else:
            for k, ky in enumerate(("triangle", "triangle")):
                cx = x0 + (x1 - x0) * (0.32 + 0.36 * k)
                o.append(f'  <line x1="{cx}" y1="{PY0 + 28}" x2="{cx}"'
                         f' y2="{PY1 - 28}" stroke="{ACCENT}" stroke-width="2"'
                         f' stroke-dasharray="6 4"/>')
                o.append(hollow(cx, (PY0 + PY1) / 2, ky, r=7))
                o.append(f'  <line x1="{cx}" y1="{PY1}" x2="{cx}"'
                         f' y2="{PY1 + 6}" stroke="{AXIS}" stroke-width="1.5"/>')
            o.append(txt(x0 + (x1 - x0) * 0.32, (PY0 + PY1) / 2 - 22, "min",
                         size=10, fill=ACCENT, anchor="middle"))
            o.append(txt(x0 + (x1 - x0) * 0.68, (PY0 + PY1) / 2 - 22, "max",
                         size=10, fill=ACCENT, anchor="middle"))

        o.append(txt(mid, PY1 + 26, p["xlab"], size=11.5, fill=INK,
                     anchor="middle"))
        for k, t in enumerate(p["toks"]):
            o.append(token(mid, PY1 + 48 + 13 * k, t, size=9))
        lines, _ = wrapped(x0, PY1 + 56 + 13 * len(p["toks"]), p["note"],
                           width=int((x1 - x0) / 5.6), size=10, fill=MUTE,
                           lh=13)
        o += lines
        o += stop_badge(mid - 42, PY0 - 18 - 24, w=84, h=18)

    blk, _ = caption_block(
        620, cap["caption"], cap["d119"],
        "Registry rows consumed: linearity [S_C_linearity_request_J_per_token] "
        "[S_C_linearity_decode_J_per_token] [R_C_linearity_limit_J]; null "
        "response [D_C_null_max_abs_J]; empirical floor [R_C_micro_min_x_floor] "
        "[R_C_micro_max_x_floor]; mixed/refused branches "
        "[PLAIN_LANGUAGE_RESULT_linearity] [PLAIN_LANGUAGE_RESULT_null] "
        "[PLAIN_LANGUAGE_RESULT_floor] [D_C_linearity_diagnostic_J_per_token] "
        "[D_C_null_diagnostic_J] [D_C_micro_diagnostic_x_floor]. Freeze status "
        "at audit: every one of these rows is STOP_FILL / SUPPLIER_UNKNOWN; no "
        "repository file in the authority set defines a characterization result "
        "schema. A whole-window refusal renders through [REFUSAL_REASON_window_C] "
        "with [PRESENT_DIAGNOSTIC_LIST] and [ABSENT_DIAGNOSTIC_ROW_LIST].")
    o += blk
    return finalize("\n".join(o + tail()))


# --------------------------------------------------------------------------
# Figure E - phase consistency, drift, and settling (four panels)
# --------------------------------------------------------------------------
def fig_e(cap) -> str:
    H = "__H__"
    PY0, PY1 = 130, 380
    panels = [
        dict(x0=110, x1=320, title="E1  phase additivity",
             ylab="additivity residual (joules)", zero=True,
             xlab="registered phase-accounting diagnostic",
             toks=["[D_C_additivity_J]", "[PLAIN_LANGUAGE_RESULT_phase]",
                   "[D_C_phase_diagnostic_J]"],
             band=False),
        dict(x0=365, x1=575, title="E2  prompt invariance",
             ylab="prompt-invariance slope (joules per token)", zero=True,
             xlab="registered phase-accounting diagnostic",
             toks=["[S_C_prompt_invariance_J_per_token]",
                   "[B_C_prompt_invariance_J_per_token]"],
             band=True),
        dict(x0=620, x1=790, title="E3  reference excursion",
             ylab="reference excursion (joules)", zero=False,
             xlab="registered reference diagnostic",
             toks=["[D_C_reference_excursion_J]",
                   "[PLAIN_LANGUAGE_RESULT_drift]",
                   "[D_C_drift_diagnostic_J]"],
             band=False),
        dict(x0=835, x1=970, title="E4  recovery time",
             ylab="recovery time (seconds)", zero=False,
             xlab="registered recovery diagnostic",
             toks=["[T_C_recovery_s]"],
             band=False),
    ]
    o = head(
        "E",
        "Figure E (skeleton). Phase consistency, drift, and settling",
        "Number-free skeleton, four separately scaled panels. Joules, joules "
        "per token, and seconds never share an axis; no dual-scale overlay.",
        "Skeleton for the phase-consistency and temporal-behaviour figure. Four "
        "panels, each with its own vertical scale: additivity residual in "
        "joules about an unlabelled zero rule; prompt-invariance slope in joules "
        "per token with an unissued frozen acceptance band; reference excursion "
        "in joules; and recovery time in seconds. Between-session eligibility is "
        "caption context, not an axis. Every mark is an unissued placeholder "
        "keyed by its registry row token, and all four panels are marked "
        "STOP_FILL.",
        H,
        "Render gate (plan): currently STOP_FILL - the characterization schema, "
        "row outcomes, presence flags, and numeric fields are all unresolved "
        "suppliers.",
    )
    o += watermark(540, (PY0 + PY1) / 2, 118)

    for p in panels:
        x0, x1 = p["x0"], p["x1"]
        mid = (x0 + x1) / 2
        o += gridlines(x0, x1, [PY1, PY1 - 50, PY1 - 100, PY1 - 150, PY0])
        o += yaxis(x0, PY0, PY1, p["ylab"], "no numeric scale")
        o.append(f'  <line x1="{x0}" y1="{PY1}" x2="{x1}" y2="{PY1}"'
                 f' stroke="{AXIS}" stroke-width="1.8"/>')
        o.append(txt(mid, PY0 - 22, p["title"], size=12.5, fill=INK,
                     weight="bold", anchor="middle"))
        cy = (PY0 + PY1) / 2
        if p["zero"]:
            o.append(f'  <line x1="{x0}" y1="{cy}" x2="{x1}" y2="{cy}"'
                     f' stroke="{AXIS}" stroke-width="1.8"/>')
            o.append(txt(x0 - 8, cy + 4, "zero", size=10, fill=MUTE,
                         anchor="end"))
        if p["band"]:
            o.append(f'  <rect x="{x0}" y="{cy - 40}" width="{x1 - x0}"'
                     f' height="80" fill="#bbbbbb" fill-opacity="0.22"'
                     f' stroke="#888888" stroke-width="1.3"'
                     f' stroke-dasharray="5 4"/>')
            o.append(txt(mid, cy - 48, "frozen acceptance band (unissued)",
                         size=10, fill="#5a5a5a", anchor="middle"))
        cx = mid
        o.append(f'  <line x1="{cx}" y1="{PY0 + 24}" x2="{cx}"'
                 f' y2="{PY1 - 24}" stroke="{ACCENT}" stroke-width="2"'
                 f' stroke-dasharray="6 4"/>')
        o.append(hollow(cx, cy, "diamond", r=7))
        o.append(txt(cx, cy - 20, "?", size=13, fill=ACCENT, weight="bold",
                     anchor="middle"))
        o.append(f'  <line x1="{cx}" y1="{PY1}" x2="{cx}" y2="{PY1 + 6}"'
                 f' stroke="{AXIS}" stroke-width="1.5"/>')
        lines, yy = wrapped(x0, PY1 + 26, p["xlab"],
                            width=max(14, int((x1 - x0) / 5.6)), size=11,
                            fill=INK, lh=14)
        o += lines
        for k, t in enumerate(p["toks"]):
            o.append(token(mid, yy + 8 + 13 * k, t, size=9))
        o += stop_badge(mid - 42, PY0 - 66, w=84, h=18)

    o.append(txt(110, 520, "Between-session eligibility is caption context, "
                 "not a continuous numeric axis:", size=11.5, fill=INK,
                 weight="bold"))
    o.append(token(110, 538, "[PLAIN_LANGUAGE_RESULT_between_sessions]",
                   anchor="start"))
    o.append(token(420, 538, "[N_C_eligible_sessions]", anchor="start"))
    o += stop_badge(660, 524, w=84, h=18)
    o.append(txt(110, 560, "Joules, joules per token, and seconds are never "
                 "overlaid on one dual scale; each panel keeps its own vertical "
                 "axis.", size=11.5, fill=BODY))

    blk, _ = caption_block(
        578, cap["caption"], cap["d119"],
        "Registry rows consumed: phase consistency [D_C_additivity_J] "
        "[S_C_prompt_invariance_J_per_token] [B_C_prompt_invariance_J_per_token]; "
        "drift and settling [D_C_reference_excursion_J] [T_C_recovery_s]; row "
        "outcomes and refused-window diagnostics [PLAIN_LANGUAGE_RESULT_phase] "
        "[PLAIN_LANGUAGE_RESULT_drift] [D_C_phase_diagnostic_J] "
        "[D_C_drift_diagnostic_J]; between-session context "
        "[PLAIN_LANGUAGE_RESULT_between_sessions] [N_C_eligible_sessions]. "
        "Freeze status at audit: every one of these rows is STOP_FILL / "
        "SUPPLIER_UNKNOWN. [B_C_prompt_invariance_J_per_token] must be "
        "pre-registered before any band is drawn.")
    o += blk
    return finalize("\n".join(o + tail()))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    caps = parse_plan()
    files = {
        "figA_phase_floor_composition.skeleton.svg": fig_a(caps["A"]),
        "figB_phase_energy_means.skeleton.svg": fig_b(caps["B"]),
        "figC_model_size_contrasts.skeleton.svg": fig_c(caps["C"]),
        "figD_known_signal_characterization.skeleton.svg": fig_d(caps["D"]),
        "figE_phase_consistency_drift_settling.skeleton.svg": fig_e(caps["E"]),
    }
    for name, body in files.items():
        (OUT / name).write_text(body, encoding="utf-8")
        print("wrote", name, len(body), "bytes")


if __name__ == "__main__":
    main()
