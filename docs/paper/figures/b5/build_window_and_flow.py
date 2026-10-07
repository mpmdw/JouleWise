#!/usr/bin/env python3
"""Build Figures B-S1 and B-S3 of the phase-energy capstone paper.

B-S1 draws one measurement window of the claim-bearing block in order of time:
the arm, the pre calibration, the reference corpus, the stages of members with
their settles and reference members, the post calibration and the tail. B-S3
draws what can stop a window, what is only recorded as a flag, what the flag
catalog does with a flag, and when a window may carry a claim.

Both are schematics of a registered design. They show no measurement.

Every number drawn is read at build time from a committed source:

* ``configs/campaigns/v5_claim_25g83/sizing_b5.json``: stage order, member
  counts, spares, window deadlines;
* ``configs/campaigns/v5_claim_25g83/flag_catalog.json``: codes by effect and
  the unit minimum;
* the JSON block of registration section 4.3: the hazard thresholds;
* ``configs/campaign_policies/quiet_mac_p2_b5.json``: the cooldown rule;
* literal constants of ``joulewise/b5/chain.py`` and ``joulewise/b5/driver.py``
  (read with ``ast``; the package is not imported).

A few values exist only in registration prose. Each is tied to an exact
fragment of the registration in ``PROSE_VALUES``; the builder refuses to build
when a fragment is no longer there, so a changed sentence cannot leave a stale
number in a figure. Some of these values are stated only in the caption file
(``captions-s1-s3.md``); they are kept here so that the same refusal guards
the captions.

Every drawn shape sits in a group that names it (``data-element``), and the
figure's own key lists every such name. ``tests/test_paper_b_figures_s1_s3.py``
checks both, and checks that the caption file names every element.

Usage, from the repository root::

    python3 -B docs/paper/figures/b5/build_window_and_flow.py            # write both SVGs
    python3 -B docs/paper/figures/b5/build_window_and_flow.py --check    # exit 1 if a file differs
    python3 -B docs/paper/figures/b5/build_window_and_flow.py --sources  # print every value and its source
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from html import escape
from pathlib import Path
from typing import Any, Mapping, Sequence

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]

REGISTRATION = "configs/campaigns/v5_claim_25g83/registration_block5.md"
SIZING = "configs/campaigns/v5_claim_25g83/sizing_b5.json"
CATALOG = "configs/campaigns/v5_claim_25g83/flag_catalog.json"
POLICY = "configs/campaign_policies/quiet_mac_p2_b5.json"
CHAIN = "joulewise/b5/chain.py"
DRIVER = "joulewise/b5/driver.py"

# The six physical hazards, as registration section 4.3 keys them. Figure B-S3 has one line for each.
HAZARDS = ("clock", "battery", "thermal", "contention", "disk", "instrument")

S1_NAME = "figB_S1_window_timeline.svg"
S3_NAME = "figB_S3_decision_flow.svg"

# The repository's labels for the three packs. The figures use the names of the
# paper's lexicon (docs/paper/paper-b/01-terms.md): ALPHA and BETA are the
# single-model windows (the 1.7B window and the 8B window), GAMMA the contrast
# window.
SINGLE_MODEL_PACKS = ("ALPHA", "BETA")
TWO_MODEL_PACK = "GAMMA"

# Values that exist only in registration prose: key, the number as drawn, the
# section it is read from, and an exact fragment of that section's text.
PROSE_VALUES: tuple[tuple[str, str, str, str], ...] = (
    ("arm_reads_s", "41", "4.1", "about 41 s of reads, collectors and cadence probe"),
    ("arm_span_min", "4 to 47", "4.1", "The chain therefore starts about 4–47 min after t0"),
    ("pre_screen_s", "0.036462861644980", "5.1", "a pre fiducial bound above the pre screen 0.036462861644980 s"),
    ("acceptance_captures", "24", "0.11", "derived from 24 captures"),
    ("calibration_pulses", "59", "0.11", "driven through 59 commanded on/off pulses"),
    ("decode_prompt_tokens", "42", "0.5", "42-token prompt (decode prompt manifest"),
    ("output_tokens", "512", "0.5", "Output is forced to exactly 512 tokens"),
    ("prefill_prompt_tokens", "2,048", "0.5", "A prompt of exactly L = 2048 tokens"),
    ("idle_baseline_s", "75", "0.3", "would have spanned 75.0–75.9 s (median 75.2 s)"),
    ("expected_chain_alpha_h", "5.4 to 8.8", "5.5",
     "| ALPHA | 119 / 0 | 98,826 s (27.5 h) | 102,180 s (28.4 h) | 31,584 s (8.8 h) | 19,460 s (5.4 h) |"),
    ("expected_chain_beta_h", "5.7 to 9.1", "5.5",
     "| BETA | 19 / 100 | 101,226 s (28.1 h) | 104,580 s (29.05 h) | 32,634 s (9.1 h) | 20,510 s (5.7 h) |"),
    ("expected_chain_gamma_h", "4.8 to 7.7", "5.5",
     "| GAMMA | 61 / 40 | 87,690 s (24.4 h) | 91,020 s (25.3 h) | 27,747 s (7.7 h) | 17,426 s (4.8 h) |"),
    ("abort_rate", "1/37", "6.6", "aborted by idle admission independently with probability 1/37"),
    ("p_usable_with_minimum", "0.85", "6.6", "at or above the minimum with probability about 0.85"),
    ("p_usable_all_members", "0.04", "6.6", "(36/37)¹¹⁹ ≈ 0.04"),
    ("clock_error_energy", "0.2 J at 40 W", "0.14", "moves at most 0.2 J per phase edge at 40 W"),
    ("block_duration_projected_h", "18 to 23", "5.5", "take about 18–23 h at the projected chains"),
    ("block_duration_earlier_basis_h", "28 to 33", "5.5", "and about 28–33 h at the block-3 basis"),
)

# Drawn shapes that carry no meaning of their own; every other element name must be written in its figure.
FURNITURE = ("background", "separator rule")


class SourceError(ValueError):
    """A committed source no longer has the shape or the text a figure was drawn from."""


# --------------------------------------------------------------------------- sources


def _literal_constants(path: Path, names: Sequence[str]) -> dict[str, Any]:
    """Module-level constants assigned a literal, read without importing the module."""

    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name in names:
                found[name] = ast.literal_eval(node.value)
    missing = [name for name in names if name not in found]
    if missing:
        raise SourceError(f"{path}: no literal constant {', '.join(missing)}")
    return found


def registered_thresholds(registration_text: str) -> dict[str, Any]:
    """The hazard thresholds: the JSON block of registration section 4.3."""

    start = registration_text.find("\n### 4.3 Registered thresholds")
    if start < 0:
        raise SourceError("registration: section 4.3 not found")
    end = registration_text.find("\n### ", start + 5)
    match = re.search(r"```json\n(.*?)\n```", registration_text[start:end], re.S)
    if match is None:
        raise SourceError("registration section 4.3: no JSON block")
    return json.loads(match.group(1))


def section_of_line(registration_text: str) -> list[str]:
    """For each line of the registration, the number of the section it is in ('4.1', '0.12', '3')."""

    current, sections = "", []
    for line in registration_text.split("\n"):
        match = re.match(r"#{2,3} (\d+(?:\.\d+)?)[. ]", line)
        if match:
            current = match.group(1)
        sections.append(current)
    return sections


def prose_values(registration_text: str) -> dict[str, dict[str, Any]]:
    """PROSE_VALUES with the line each fragment is on; refuses when a fragment is gone or moved section."""

    lines = registration_text.split("\n")
    sections = section_of_line(registration_text)
    out: dict[str, dict[str, Any]] = {}
    for key, value, section, fragment in PROSE_VALUES:
        hits = [index for index, line in enumerate(lines)
                if fragment in line and (sections[index] == section or sections[index].split(".")[0] == section)]
        if len(hits) != 1:
            raise SourceError(f"registration section {section}: expected the fragment {fragment!r} on exactly "
                              f"one line, found it on {len(hits)}; the value {key} must be re-read")
        out[key] = {"value": value, "section": section, "line": hits[0] + 1, "fragment": fragment}
    return out


def load_sources(repo: Path = REPO) -> dict[str, Any]:
    """Read every committed source the two figures draw from."""

    registration_text = (repo / REGISTRATION).read_text(encoding="utf-8")
    return {
        "sizing": json.loads((repo / SIZING).read_text(encoding="utf-8")),
        "catalog": json.loads((repo / CATALOG).read_text(encoding="utf-8")),
        "policy": json.loads((repo / POLICY).read_text(encoding="utf-8")),
        "thresholds": registered_thresholds(registration_text),
        "prose": prose_values(registration_text),
        "chain": _literal_constants(repo / CHAIN, ("SETTLE_S", "NEG8_RETRY_MINIMUM", "CALIBRATION_ARM_COUNTDOWN_S")),
        "driver": _literal_constants(repo / DRIVER, ("MONITOR_POST_CHAIN_HOLD_S", "MONITOR_OUTAGE_S")),
    }


# --------------------------------------------------------------------------- the window's shape

_SCIENCE_ID = re.compile(
    r"(?P<prefill>prefill-p(?P<tokens>\d+)-)?"
    r"(?:(?P<repeats>absolute)|(?:abba|contrast-blocks)-(?P<lo>\d\d)-(?P<hi>\d\d))$")


def window_shape(pack: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Classify one pack's chain stages, in order, from the sizing output."""

    shape: list[dict[str, Any]] = []
    calibrations = 0
    for stage in pack["stages"]:
        kind, stage_id = stage["kind"], stage["stage_id"]
        if kind == "bracket_reservation":
            shape.append({"role": "session"})
        elif kind == "calibration_capture":
            calibrations += 1
            shape.append({"role": "calibration", "slot": "pre" if calibrations == 1 else "post"})
        elif kind == "bound_derivation":
            shape.append({"role": "bound"})
        elif kind == "campaign_collection":
            members = stage["members"]
            if stage.get("neg8_corpus"):
                shape.append({"role": "corpus", "members": members})
            elif "spare_retry" in stage:
                spare = stage["spare_retry"]
                shape.append({"role": "reference", "slot": spare["slot"], "members": members,
                              "spares": spare["max_spares"]})
            elif stage.get("science"):
                match = _SCIENCE_ID.search(stage_id)
                if match is None:
                    raise SourceError(f"{stage_id}: a science stage this builder cannot classify")
                workload = "prefill" if match.group("prefill") else "decode"
                if match.group("repeats"):
                    shape.append({"role": "repeats", "members": members, "workload": workload})
                else:
                    lo, hi = int(match.group("lo")), int(match.group("hi"))
                    if members != 4 * (hi - lo + 1):
                        raise SourceError(f"{stage_id}: {members} members are not {hi - lo + 1} quads of four")
                    shape.append({"role": "quads", "members": members, "workload": workload, "lo": lo, "hi": hi})
                if match.group("tokens"):
                    shape[-1]["prompt_tokens"] = int(match.group("tokens"))
            else:
                if members != 1:
                    raise SourceError(f"{stage_id}: an auxiliary stage of {members} members has no drawing")
                shape.append({"role": "diagnostic", "members": members})
        else:
            raise SourceError(f"{stage_id}: stage kind {kind!r} has no drawing")
    return shape


def split_shape(shape: Sequence[Mapping[str, Any]]) -> tuple[list, list, list]:
    """Opening (through the start triplet), science part, closing (from the end triplet)."""

    roles = [(item["role"], item.get("slot")) for item in shape]
    try:
        start = roles.index(("reference", "start"))
        end = roles.index(("reference", "end"))
    except ValueError as error:
        raise SourceError("a pack without a start or an end reference stage") from error
    opening, middle, closing = list(shape[:start + 1]), list(shape[start + 1:end]), list(shape[end:])
    if [item["role"] for item in opening] != ["session", "calibration", "corpus", "bound", "reference"]:
        raise SourceError("the opening is no longer: session, calibration, corpus, bound, start references")
    if [item["role"] for item in closing] != ["reference", "calibration"]:
        raise SourceError("the closing is no longer: end references, calibration")
    if [item.get("slot") for item in middle if item["role"] == "reference"] != ["midpoint"]:
        raise SourceError("the science part no longer holds exactly one midpoint reference stage")
    return opening, middle, closing


def values(sources: Mapping[str, Any]) -> dict[str, Any]:
    """Every number the figures and their captions use, computed from the sources."""

    sizing, catalog, thresholds = sources["sizing"], sources["catalog"], sources["thresholds"]
    packs = sizing["packs"]
    if set(packs) != {*SINGLE_MODEL_PACKS, TWO_MODEL_PACK}:
        raise SourceError(f"the sizing output now holds the packs {sorted(packs)}; the figures draw three")
    if set(thresholds) != set(HAZARDS):
        raise SourceError(f"registration section 4.3 now lists {sorted(thresholds)}; Figure B-S3 draws six hazards")
    shapes = {label: window_shape(packs[label]) for label in (*SINGLE_MODEL_PACKS, TWO_MODEL_PACK)}
    parts = {label: split_shape(shape) for label, shape in shapes.items()}
    single, two = parts[SINGLE_MODEL_PACKS[0]], parts[TWO_MODEL_PACK]
    for label in SINGLE_MODEL_PACKS[1:]:
        if parts[label] != single:
            raise SourceError(f"{label} no longer has the shape of {SINGLE_MODEL_PACKS[0]}; one row cannot show both")
    if two[0] != single[0] or two[2] != single[2]:
        raise SourceError("the contrast window no longer shares the single-model opening and closing")
    members_single = {packs[label]["members"] for label in SINGLE_MODEL_PACKS}
    science_single = {packs[label]["science_members"] for label in SINGLE_MODEL_PACKS}
    stages_all = {packs[label]["collection_stages"] for label in packs}
    if len(members_single) != 1 or len(science_single) != 1 or len(stages_all) != 1:
        raise SourceError("the single-model windows no longer share one member count, or the stage counts differ")
    for label, shape in shapes.items():
        if sum(item.get("members", 0) for item in shape) != packs[label]["members"]:
            raise SourceError(f"{label}: the drawn members do not add up to the sizing output's total")

    opening, closing = single[0], single[2]
    midpoint = next(item for item in single[1] if item["role"] == "reference")
    repeats = {item["members"] for part in (single[1], two[1]) for item in part if item["role"] == "repeats"}
    quad_stage = {item["members"] for part in (single[1], two[1]) for item in part if item["role"] == "quads"}
    quads_per_workload = {sum(item["hi"] - item["lo"] + 1 for item in part
                              if item["role"] == "quads" and item["workload"] == workload)
                          for part in (single[1], two[1]) for workload in ("decode", "prefill")}
    prefill_tokens = {item["prompt_tokens"] for part in (single[1], two[1]) for item in part
                      if "prompt_tokens" in item}
    if len(repeats) != 1 or len(quad_stage) != 1 or len(quads_per_workload) != 1 or len(prefill_tokens) != 1:
        raise SourceError("repeats, quads per stage, quads per workload or the prefill prompt length are not uniform")
    prose = sources["prose"]
    if f"{prefill_tokens.copy().pop():,}" != prose["prefill_prompt_tokens"]["value"]:
        raise SourceError("the stage ids' prefill prompt length disagrees with registration section 0.5")

    effects: dict[str, int] = {}
    for entry in catalog["codes"].values():
        effects[entry["effect"]] = effects.get(entry["effect"], 0) + 1
    if set(effects) != {"DISCLOSE", "EXCLUDE_MEMBER", "EXCLUDE_WINDOW"}:
        raise SourceError(f"the flag catalog's effects are now {sorted(effects)}")

    def science_before(shape: Sequence[Mapping[str, Any]], role: str) -> list[int]:
        """How many science members have run when each stage of ``role`` starts."""

        done, out_ = 0, []
        for item in shape:
            if item["role"] == role:
                out_.append(done)
            elif item["role"] in ("repeats", "quads"):
                done += item["members"]
        return out_

    settle_s = sources["chain"]["SETTLE_S"]
    collection_stages = stages_all.copy().pop()
    cooldown = sources["policy"]["cooldown"]
    deadlines_h = [packs[label]["window_max_s"] / 3600 for label in packs]
    gib = 1024 ** 3
    out: dict[str, Any] = {
        "shape_opening": opening, "shape_closing": closing,
        "shape_single": single[1], "shape_two": two[1],
        "settle_s": settle_s,
        "collection_stages": collection_stages,
        "settles": 1 + collection_stages,
        "settles_total_s": (1 + collection_stages) * settle_s,
        "corpus_members": opening[2]["members"],
        "corpus_minimum": sources["chain"]["NEG8_RETRY_MINIMUM"],
        "start_members": opening[4]["members"], "start_spares": opening[4]["spares"],
        "midpoint_members": midpoint["members"], "midpoint_spares": midpoint["spares"],
        "end_members": closing[0]["members"], "end_spares": closing[0]["spares"],
        "repeats": repeats.pop(), "quad_stage_members": quad_stage.pop(),
        "quads": quads_per_workload.pop(),
        "members_single": members_single.pop(), "science_single": science_single.pop(),
        "members_two": packs[TWO_MODEL_PACK]["members"], "science_two": packs[TWO_MODEL_PACK]["science_members"],
        "midpoint_after_single": science_before(single[1], "reference")[0],
        "midpoint_after_two": science_before(two[1], "reference")[0],
        "diagnostic_after_two": " and ".join(str(n) for n in science_before(two[1], "diagnostic")),
        "window_interval_s": thresholds["contention"]["window_interval_s"],
        "post_countdown_s": sources["chain"]["CALIBRATION_ARM_COUNTDOWN_S"]["post"],
        "t_stream_max_s": thresholds["clock"]["t_stream_max_s"],
        "clock_limit_ms": thresholds["clock"]["limit_ms"],
        "clock_step_ms": thresholds["clock"]["residual_max_ns"] / 1e6,
        "battery_limit_ma": thresholds["battery"]["limit_ma"],
        "thermal_max_level": thresholds["thermal"]["max_level"],
        "cpu_limit": thresholds["contention"]["cpu_limit_s_per_s"],
        "dwell_interval_s": thresholds["contention"]["interval_s"],
        "dwell_clean_s": thresholds["contention"]["clean_s"],
        "dwell_cap_s": thresholds["contention"]["cap_s"],
        "disk_headroom_gib": thresholds["disk"]["headroom_bytes"] / gib,
        "disk_low_gib": thresholds["disk"]["low_bytes"] / gib,
        "sampler_frames": thresholds["instrument"]["frames"],
        "sampler_bound_s": thresholds["instrument"]["bound_s"],
        "sampler_median_ms": thresholds["instrument"]["median_ms_max"],
        "sampler_max_ms": thresholds["instrument"]["max_ms_max"],
        "cooldown_reading_s": cooldown["subwindow_s"],
        "cooldown_factor": 1 + cooldown["tolerance_fraction"],
        "cooldown_cap_s": cooldown["cap_s"],
        "monitor_hold_s": sources["driver"]["MONITOR_POST_CHAIN_HOLD_S"],
        "monitor_outage_min": sources["driver"]["MONITOR_OUTAGE_S"] / 60,
        "deadline_h_min": int(min(deadlines_h)), "deadline_h_max": int(max(deadlines_h)),
        "catalog_codes": len(catalog["codes"]),
        "catalog_disclose": effects["DISCLOSE"],
        "catalog_exclude_member": effects["EXCLUDE_MEMBER"],
        "catalog_exclude_window": effects["EXCLUDE_WINDOW"],
        "unit_minimum": catalog["rules"]["cell_unit_minimum"],
    }
    for key, entry in prose.items():
        out[key] = entry["value"]
    out["pre_screen_ms"] = f"{float(prose['pre_screen_s']['value']) * 1000:.1f}"
    return out


def num(value: Any) -> str:
    """A number as the figures print it: thousands separated by commas, no trailing '.0'."""

    if isinstance(value, str):
        return value
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if isinstance(value, int):
        return f"{value:,}"
    return f"{value:g}"


def unit(value: Any, name: str) -> str:
    """A number and its unit, joined so that a line never breaks between them."""

    return f"{num(value)}\u00a0{name}"


def member_sum(shape: Sequence[Mapping[str, Any]], opening: Sequence[Mapping[str, Any]],
               closing: Sequence[Mapping[str, Any]]) -> str:
    """One window's members written as a sum, stage by stage; a workload's consecutive stages share brackets."""

    terms = [num(item["members"]) for item in opening if "members" in item]
    group: list[str] = []
    workload = None

    def flush() -> None:
        if group:
            terms.append("(" + " + ".join(group) + ")" if len(group) > 1 else group[0])
            group.clear()

    for item in shape:
        if item["role"] in ("repeats", "quads"):
            if group and item["workload"] != workload:
                flush()
            group.append(num(item["members"]))
            workload = item["workload"]
        else:
            flush()
            terms.append(num(item["members"]))
    flush()
    terms += [num(item["members"]) for item in closing if "members" in item]
    return " + ".join(terms)


# --------------------------------------------------------------------------- drawing

INK, MUTED, LINE = "#1b1b1b", "#555555", "#333333"
PALE, RULE = "#f2f2f2", "#d9d9d9"
BLUE, RED = "#1b6ca8", "#a32a1f"
FONT = "sans-serif"

_NARROW, _MID, _WIDE = set("ijl.,:;|'!()[] \u00a0"), set("ftrI-–/\"“”‘’"), set("mwMW@%")


def text_width(text: str, size: float) -> float:
    """A cautious estimate of the drawn width of ``text`` in a common sans-serif face."""

    units = 0.0
    for char in text:
        if char in _NARROW:
            units += 0.30
        elif char in _MID:
            units += 0.36
        elif char in _WIDE:
            units += 0.90
        elif char.isupper() or char.isdigit():
            units += 0.66 if char.isupper() else 0.57
        else:
            units += 0.55
    return units * size


def wrap(text: str, width: float, size: float) -> list[str]:
    """Break ``text`` into lines no wider than ``width`` by the estimate above."""

    lines: list[str] = []
    current = ""
    for word in text.split(" "):
        if not word:
            continue
        candidate = word if not current else current + " " + word
        if current and text_width(candidate, size) > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _n(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".")


class Canvas:
    """One SVG. Shapes go in through ``element`` so that each is inside a group that names it."""

    def __init__(self, prefix: str, width: int, title: str, desc: str) -> None:
        self.prefix, self.width, self.title, self.desc = prefix, width, title, desc
        self.named: list[str] = ["background"]
        self.body: list[str] = []

    # shapes: each returns markup, to be handed to ``element``
    def rect(self, x: float, y: float, w: float, h: float, fill: str = "#ffffff", stroke: str = LINE,
             sw: float = 1.8, dash: str = "", rx: float = 0, opacity: float | None = None) -> str:
        extra = (f' stroke-dasharray="{dash}"' if dash else "") + (f' rx="{_n(rx)}"' if rx else "") \
            + (f' fill-opacity="{opacity:g}"' if opacity is not None else "")
        stroke_part = f' stroke="{stroke}" stroke-width="{_n(sw)}"' if stroke != "none" else ""
        return (f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}" fill="{fill}"'
                f"{stroke_part}{extra}/>")

    def line(self, x1: float, y1: float, x2: float, y2: float, stroke: str = LINE, sw: float = 1.8,
             dash: str = "", arrow: bool = False) -> str:
        extra = (f' stroke-dasharray="{dash}"' if dash else "") \
            + (f' marker-end="url(#{self.prefix}-arrow)"' if arrow else "")
        return (f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}" stroke="{stroke}" '
                f'stroke-width="{_n(sw)}"{extra}/>')

    def polygon(self, points: Sequence[tuple[float, float]], fill: str = "#ffffff", stroke: str = LINE,
                sw: float = 1.8, opacity: float | None = None) -> str:
        coordinates = " ".join(f"{_n(x)},{_n(y)}" for x, y in points)
        extra = f' fill-opacity="{opacity:g}"' if opacity is not None else ""
        return f'<polygon points="{coordinates}" fill="{fill}" stroke="{stroke}" stroke-width="{_n(sw)}"{extra}/>'

    def circle(self, cx: float, cy: float, r: float, fill: str, stroke: str = "none") -> str:
        stroke_part = f' stroke="{stroke}" stroke-width="1.5"' if stroke != "none" else ""
        return f'<circle cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(r)}" fill="{fill}"{stroke_part}/>'

    def element(self, name: str, shapes: Sequence[str], label: str | None = None) -> None:
        """Add shapes as one named element. ``label`` names this instance when the kind has several."""

        if name not in self.named:
            self.named.append(name)
        label_part = f' data-label="{escape(label, quote=True)}"' if label else ""
        self.body.append(f'<g data-element="{escape(name, quote=True)}"{label_part}>' + "".join(shapes) + "</g>")

    def text(self, x: float, y: float, text: str, size: float = 13, fill: str = INK, anchor: str = "start",
             bold: bool = False, italic: bool = False) -> None:
        extra = (' font-weight="bold"' if bold else "") + (' font-style="italic"' if italic else "") \
            + (f' text-anchor="{anchor}"' if anchor != "start" else "")
        self.body.append(f'<text x="{_n(x)}" y="{_n(y)}" font-family="{FONT}" font-size="{_n(size)}" '
                         f'fill="{fill}"{extra}>{escape(text)}</text>')

    def lines(self, x: float, y: float, lines: Sequence[str], size: float = 13, leading: float = 17,
              fill: str = INK, anchor: str = "start", bold_first: bool = False) -> float:
        """Draw lines of text from baseline ``y`` down; return the next free baseline."""

        for index, line in enumerate(lines):
            self.text(x, y + index * leading, line, size, fill, anchor, bold=bold_first and index == 0)
        return y + len(lines) * leading

    def paragraph(self, x: float, y: float, width: float, text: str, size: float = 13, leading: float = 17,
                  fill: str = INK) -> float:
        return self.lines(x, y, wrap(text, width, size), size, leading, fill)

    def centred(self, x: float, y: float, w: float, h: float, lines: Sequence[str], size: float = 12.5,
                leading: float = 15.5, bold_first: bool = False, fill: str = INK) -> None:
        """Centre lines of text in the box (x, y, w, h); refuse a line the box cannot hold."""

        for line in lines:
            if text_width(line, size) > w - 6:
                raise SourceError(f"label {line!r} does not fit a box {w:g} wide")
        first = y + h / 2 - (len(lines) - 1) * leading / 2 + size * 0.35
        self.lines(x + w / 2, first, lines, size, leading, fill, "middle", bold_first)

    def render(self, height: float) -> str:
        """The finished SVG, ``height`` user units tall."""

        prefix, width, tall = self.prefix, self.width, int(round(height))
        head = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{tall}" '
            f'viewBox="0 0 {width} {tall}" role="img" aria-labelledby="{prefix}-title {prefix}-desc">',
            f'<title id="{prefix}-title">{escape(self.title)}</title>',
            f'<desc id="{prefix}-desc">{escape(self.desc)}</desc>',
            "<defs>",
            f'<marker id="{prefix}-arrow" markerWidth="10" markerHeight="10" refX="9" refY="4.5" orient="auto" '
            f'markerUnits="userSpaceOnUse"><path d="M0,0 L9,4.5 L0,9 z" fill="{LINE}"/></marker>',
            f'<pattern id="{prefix}-hatch" width="6" height="6" patternUnits="userSpaceOnUse" '
            f'patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="{MUTED}" '
            'stroke-width="2"/></pattern>',
            "</defs>",
            '<g data-element="background">' + self.rect(0, 0, width, tall, "#ffffff", "none") + "</g>",
        ]
        return "\n".join(head + self.body + ["</svg>"]) + "\n"


# ---- Figure B-S1 ----------------------------------------------------------------------

S1_TITLE = "Figure B-S1. One measurement window, in order of time"
S1_SUBTITLE = ("Schematic of the registered design. Widths are not proportional to time. "
               "No measured data is shown.")

LEFT = 40          # left edge of every row
RIGHT = 1160       # right edge of the drawing
BOX_H = 58         # height of a box in a row
SQUARE = 16        # side of one reference-member square
SQUARE_GAP = 4
SETTLE_W = 12
STEP = 14          # gap that holds a time arrow
BAR_DROP = 34      # from the bottom of a row's boxes to its monitor-and-meter bar


class Row:
    """Lays one row of Figure B-S1 from left to right."""

    def __init__(self, canvas: Canvas, y: float) -> None:
        self.c, self.x, self.y = canvas, float(LEFT), y
        self.first = True

    @property
    def mid(self) -> float:
        return self.y + BOX_H / 2

    def arrow(self) -> None:
        """A time arrow into the next item (not before the row's first item)."""

        if not self.first:
            self.c.element("time arrow", [self.c.line(self.x + 1, self.mid, self.x + STEP - 1, self.mid, sw=1.6,
                                                      arrow=True)])
            self.x += STEP
        self.first = False

    def settle(self, seconds: int) -> None:
        """A settle: a hatched bar with its length in seconds above it."""

        self.arrow()
        c = self.c
        c.element("settle", [c.rect(self.x, self.y + 8, SETTLE_W, BOX_H - 16, f"url(#{c.prefix}-hatch)", MUTED, 1.2)])
        c.text(self.x + SETTLE_W / 2, self.y + 3, unit(seconds, "s"), 10, MUTED, "middle")
        self.x += SETTLE_W

    def box(self, element: str, label: str, lines: Sequence[str], width: float, fill: str = PALE,
            stroke: str = LINE, sw: float = 1.8, opacity: float | None = None, rx: float = 0) -> float:
        """A labelled box; returns its left edge."""

        self.arrow()
        c, x = self.c, self.x
        c.element(element, [c.rect(x, self.y, width, BOX_H, fill, stroke, sw, rx=rx, opacity=opacity)], label)
        c.centred(x, self.y, width, BOX_H, lines)
        self.x += width
        return x

    def squares(self, members: int, spares: int, label: str, caption: Sequence[str],
                diagnostic: bool = False) -> None:
        """Reference members as squares, then their spares; ``caption`` goes underneath."""

        self.arrow()
        c, x0 = self.c, self.x
        top = self.y + (BOX_H - SQUARE) / 2
        for _ in range(members):
            if diagnostic:
                c.element("interior reference",
                          [c.rect(self.x, top, SQUARE, SQUARE, "#ffffff", LINE, 1.6),
                           c.line(self.x, top + SQUARE, self.x + SQUARE, top, LINE, 1.2)], label)
            else:
                c.element("reference member", [c.rect(self.x, top, SQUARE, SQUARE, "#bdbdbd", LINE, 1.4)], label)
            self.x += SQUARE + SQUARE_GAP
        for _ in range(spares):
            c.element("spare", [c.rect(self.x, top, SQUARE, SQUARE, "#ffffff", LINE, 1.3, dash="3 2")],
                      label)
            self.x += SQUARE + SQUARE_GAP
        self.x -= SQUARE_GAP
        c.lines((x0 + self.x) / 2, self.y + BOX_H + 13, caption, 11, 13.5, INK, "middle")

    def marker(self, label: str) -> None:
        """An instant: a vertical tick with its name above."""

        self.arrow()
        c = self.c
        c.element("instant marker", [c.line(self.x + 3, self.y - 8, self.x + 3, self.y + BOX_H + 8, INK, 2.6)], label)
        c.text(self.x + 3, self.y - 14, label, 11.5, INK, "middle", bold=True)
        self.x += 6

    def diamond(self, label: str, caption: Sequence[str]) -> None:
        self.arrow()
        c, half = self.c, 22
        cx = self.x + half
        c.element("clock-step control",
                  [c.polygon([(cx, self.mid - half), (cx + half, self.mid), (cx, self.mid + half),
                              (cx - half, self.mid)], BLUE, BLUE, 2, opacity=0.12)], label)
        c.lines(cx, self.y + BOX_H + 13, caption, 11, 13.5, INK, "middle")
        self.x += 2 * half


def _science_row(row: Row, shape: Sequence[Mapping[str, Any]], v: Mapping[str, Any]) -> list[tuple[str, float, float]]:
    """Draw the science part of one window; return (workload, left, right) spans for the brackets."""

    spans: list[tuple[str, float, float]] = []
    current, left, right = None, 0.0, 0.0
    for item in shape:
        role = item["role"]
        before = row.x + (0 if row.first else STEP)
        if role == "reference" and current is not None:
            spans.append((current, left, right))
            current = None
        row.settle(v["settle_s"])
        if role in ("repeats", "quads"):
            if current is None:
                current, left = item["workload"], before
            elif item["workload"] != current:
                raise SourceError("two workloads follow one another with no midpoint reference between them")
            if role == "repeats":
                lines = [f"{num(item['members'])} absolute", "repeats"]
                label = f"{num(item['members'])} absolute repeats"
            else:
                lines = [f"quads {item['lo']}–{item['hi']}", f"{num(item['members'])} members"]
                label = f"quads {item['lo']}–{item['hi']}"
            row.box("science stage", label, lines, 88, "#ffffff", INK, 2.4)
        elif role == "reference":
            row.squares(item["members"], item["spares"], "midpoint reference", ["midpoint", "reference"])
        elif role == "diagnostic":
            row.squares(item["members"], 0, "interior reference", ["interior", "reference"], diagnostic=True)
        else:
            raise SourceError(f"a {role} stage inside the science part has no drawing")
        right = row.x
    if current is not None:
        spans.append((current, left, right))
    return spans


S1_KEY: tuple[tuple[str, str], ...] = (
    ("time arrow", "order in time: left to right, then the next row"),
    ("instant marker", "an instant: the scheduled start, GO, the chain's exit"),
    ("arm box", "the checks that decide whether the chain starts"),
    ("pulse calibration", "a timing recording: {calibration_pulses} on/off pulses of a GPU load"),
    ("computing or recording step", "a step in which no member runs"),
    ("settle", "a {settle} sleep that lets the machine return to idle"),
    ("reference member", "one run of the fixed reference workload"),
    ("spare", "runs, after one more settle, only if its stage lost a member"),
    ("interior reference", "recorded, but not read by the reference drift check"),
    ("science stage", "members whose energies feed the reported numbers"),
    ("chain stop", "a point at which the chain itself ends the window"),
    ("clock-step control", "a deliberate clock step, to test the clock check"),
    ("monitor and meter bar", "the monitor and the whole-machine meter are recording"),
    ("workload bracket", "the request that the stages under it run"),
)


def build_s1(v: Mapping[str, Any]) -> str:
    c = Canvas("bs1", 1200, S1_TITLE,
               "Schematic timeline of one measurement window, in four rows read top to bottom. Row 1: the "
               "scheduled start, the arm and GO. Row 2: the bracket reservation, a settle, the pre calibration "
               "with its screen, the reference corpus, the reference drift bound, and the start triplet of "
               "reference members with its spares. Row 3: the stages of science members, each "
               "preceded by a settle, with a midpoint reference between the decode workload and the prefill "
               "workload; one version for a single-model window and one for the contrast window. Row 4: the end "
               "triplet, the post calibration, the chain's exit, and the tail with the clock-step control. A "
               "bar under rows 2 to 4 shows the monitor and the whole-machine meter recording. An inset expands "
               "one stage into its settle, its members and the cooldowns between them. No measured data is shown.")
    c.text(LEFT, 32, S1_TITLE, 18, bold=True)
    c.text(LEFT, 54, S1_SUBTITLE, 13, MUTED)

    def header(y: float, text: str) -> None:
        c.text(LEFT, y, text, 13.5, INK, bold=True)

    def bar(y: float, x1: float, x2: float) -> None:
        c.element("monitor and meter bar", [c.rect(x1, y + BOX_H + BAR_DROP, x2 - x1, 5, "#9a9a9a", "none")])

    # Row 1: the start check.
    y1 = 124
    header(y1 - 42, "1   The arm: the checks that decide whether the window's chain starts")
    row = Row(c, y1)
    row.x += 50
    row.marker("scheduled start")
    row.box("arm box", "the arm",
            ["the arm: six physical hazards are measured directly (Figure B-S3)",
             f"about {unit(v['arm_reads_s'], 's')} of reads and probes, then the dwell:",
             f"a wait of {unit(v['dwell_clean_s'], 's')} to {unit(v['dwell_cap_s'], 's')} for a quiet machine"],
            540,
            "#ffffff", INK, 2.2, rx=14)
    row.marker("GO")
    c.lines(row.x + 20, y1 + 5,
            ["At GO the chain starts: the script that runs the stages of rows",
             f"2 to 4. That is about {v['arm_span_min']} minutes after the scheduled start.",
             "From GO to the tail, the monitor and the whole-machine meter",
             "record (grey bar under rows 2 to 4)."], 12, 15.5)

    # Row 2: the opening.
    y2 = 246
    header(y2 - 26, "2   Opening: the same in all three windows")
    row = Row(c, y2)
    session_x = row.box("computing or recording step", "bracket reservation", ["bracket", "reservation"], 100)
    row.settle(v["settle_s"])
    calibration_x = row.box("pulse calibration", "pre calibration",
                            ["pre calibration", "and its screen"], 116, BLUE, BLUE, 2.2, 0.12)
    for x, digit in ((session_x + 100 - 9, "1"), (calibration_x + 116 - 31, "2"), (calibration_x + 116 - 9, "3")):
        c.element("chain stop", [c.circle(x, y2, 9.5, RED)], f"chain stop {digit}")
        c.text(x, y2 + 4, digit, 11.5, "#ffffff", "middle", bold=True)
    row.settle(v["settle_s"])
    row.squares(v["corpus_members"], 0, "reference corpus",
                [f"reference corpus: {num(v['corpus_members'])} reference members"])
    row.box("computing or recording step", "reference drift bound computed",
            ["reference", "drift bound", "computed"], 100)
    row.settle(v["settle_s"])
    row.squares(v["start_members"], v["start_spares"], "start triplet",
                [f"start triplet, {num(v['start_spares'])} spares"])
    bar(y2, LEFT, row.x)
    c.lines(row.x + 28, y2 - 6, ["Chain stops 1, 2, 3: the only points at which",
                                 "the chain itself ends the window.",
                                 "1  the bracket reservation fails",
                                 "2  the pre calibration cannot be recorded",
                                 "3  its pulse timing bound is above the pre",
                                 f"    screen, {unit(v['pre_screen_ms'], 'ms')}",
                                 "All three come before the first member."], 12, 15.5)

    # Rows 3a and 3b: the science part, which differs between the two kinds of window.
    y3a, y3b = 414, 589
    header(y3a - 52, "3a   Science stages of a single-model window (the 1.7B window and the 8B window): "
                     f"{num(v['science_single'])} science members, {num(v['members_single'])} members in all")
    row = Row(c, y3a)
    spans_a = _science_row(row, v["shape_single"], v)
    bar(y3a, LEFT, row.x)
    c.lines(row.x + 24, y3a + 2,
            ["A window runs row 3a or row 3b,", "never both.",
             "Absolute repeat: one member", "on its own.",
             "Quad: four members in the order", "A, B, B, A."], 12, 15.5)
    header(y3b - 52, "3b   Science stages of the contrast window (side A the 1.7B model, side B the 8B model): "
                     f"{num(v['science_two'])} science members, {num(v['members_two'])} members in all")
    row = Row(c, y3b)
    spans_b = _science_row(row, v["shape_two"], v)
    bar(y3b, LEFT, row.x)
    row_3b_end = row.x

    labels = {"decode": f"decode workload: {v['decode_prompt_tokens']}-token prompt",
              "prefill": f"prefill workload: {v['prefill_prompt_tokens']}-token prompt"}
    for y, spans in ((y3a, spans_a), (y3b, spans_b)):
        for workload, x1, x2 in spans:
            top = y - 22
            c.element("workload bracket",
                      [c.line(x1, top, x2, top, MUTED, 1.4), c.line(x1, top, x1, top + 6, MUTED, 1.4),
                       c.line(x2, top, x2, top + 6, MUTED, 1.4)], labels[workload].split(":")[0])
            c.text((x1 + x2) / 2, top - 5, labels[workload], 11.5, MUTED, "middle")

    # Inset, in the free space right of row 3b: one stage of members, expanded.
    fx, fy, fw, fh = 826, y3b - 38, RIGHT - 826, 178
    if row_3b_end > fx - 16:
        raise SourceError("row 3b now runs into the inset")
    c.element("inset", [c.rect(fx, fy, fw, fh, "#ffffff", RULE, 1.5)])
    c.text(fx + 12, fy + 21, "Inset: inside one stage of members", 13, bold=True)
    x, yy = fx + 12, fy + 34
    c.element("settle", [c.rect(x, yy + 3, SETTLE_W, 26, f"url(#{c.prefix}-hatch)", MUTED, 1.2)])
    x += SETTLE_W + 5
    for index in range(3):
        c.element("member", [c.rect(x, yy, 62, 32, "#ffffff", INK, 1.8)])
        c.centred(x, yy, 62, 32, ["member"], 11.5)
        x += 62
        if index < 2:
            c.element("cooldown", [c.rect(x + 4, yy + 10, 34, 12, "#e3e3e3", MUTED, 1.2, dash="2 2")])
            x += 42
    c.text(x + 8, yy + 21, "…", 14, MUTED)
    inset_text = wrap(
        f"A member is one inference request run in its own process: about {unit(v['idle_baseline_s'], 's')} of "
        "idle baseline, one warm-up, then the measured request. The dashed bar between members is the cooldown. "
        f"It ends at the first {unit(v['cooldown_reading_s'], 's')} idle reading that is at most "
        f"{num(v['cooldown_factor'])} times the previous member's idle baseline, or after "
        f"{unit(v['cooldown_cap_s'], 's')}.", fw - 24, 11.5)
    if yy + 54 + (len(inset_text) - 1) * 15 > fy + fh - 8:
        raise SourceError("the inset's text runs past its frame")
    c.lines(fx + 12, yy + 54, inset_text, 11.5, 15)

    # Row 4: the closing and the tail.
    y4 = 754
    header(y4 - 42, "4   Closing and tail: the same in all three windows")
    row = Row(c, y4)
    row.settle(v["settle_s"])
    row.squares(v["end_members"], v["end_spares"], "end triplet", [f"end triplet, {num(v['end_spares'])} spares"])
    row.box("pulse calibration", "post calibration", ["post", "calibration"], 100, BLUE, BLUE, 2.2, 0.12)
    row.marker("chain exits")
    row.box("computing or recording step", "chain's processes confirmed gone; members counted",
            ["chain's processes", "confirmed gone;", "members counted"], 124)
    row.diamond("clock-step control", ["clock-step control", "(once per measurement block)"])
    stop_x = row.box("computing or recording step", "monitor and meter stopped",
                     ["monitor and", "meter stopped"], 108)
    row.box("computing or recording step", "final record written", ["final record", "written"], 100)
    bar(y4, LEFT, stop_x)
    c.lines(row.x + 24, y4 + 25,
            ["Once the final record is written, the harvest",
             "may begin (Figure B-S3)."], 12, 15.5)

    # Worked count.
    yw = y4 + BOX_H + BAR_DROP + 34
    c.text(LEFT, yw, "Worked count.", 12.5, bold=True)
    c.lines(LEFT + 100, yw,
            [f"Single-model window: {member_sum(v['shape_single'], v['shape_opening'], v['shape_closing'])} = "
             f"{num(v['members_single'])} members.   Contrast window: "
             f"{member_sum(v['shape_two'], v['shape_opening'], v['shape_closing'])} = {num(v['members_two'])} members.",
             f"Either way: 1 settle before the pre calibration + {num(v['collection_stages'])} before stages of "
             f"members = {num(v['settles'])} settles of {unit(v['settle_s'], 's')} = "
             f"{unit(v['settles_total_s'], 's')}."],
            12.5, 17)

    # Key.
    yk = yw + 52
    c.element("separator rule", [c.line(LEFT, yk - 14, RIGHT, yk - 14, RULE, 1.5)])
    c.text(LEFT, yk + 6, "Key", 13.5, bold=True)
    fills = {"calibration_pulses": v["calibration_pulses"], "settle": unit(v["settle_s"], "s")}
    bottom = _key(c, [(name, meaning.format(**fills)) for name, meaning in S1_KEY], yk + 20, columns=2,
                  name_w=204)
    return c.render(bottom + 14)


def _key(c: Canvas, entries: Sequence[tuple[str, str]], y0: float, *, columns: int, name_w: float) -> float:
    """The figure's key: a sample of each element kind, its name, and what it stands for. Returns its bottom."""

    column_w = (RIGHT - LEFT) / columns
    per_column = -(-len(entries) // columns)
    for index, (name, meaning) in enumerate(entries):
        column, line = divmod(index, per_column)
        x, y = LEFT + column * column_w, y0 + line * 21
        _swatch(c, name, x, y)
        if text_width(name, 12) * 1.06 > name_w - 8 or text_width(meaning, 11.5) > column_w - 32 - name_w - 8:
            raise SourceError(f"key entry {name!r} does not fit its line")
        c.text(x + 32, y + 12, name, 12, INK, bold=True)
        c.text(x + 32 + name_w, y + 12, meaning, 11.5, MUTED)
    return y0 + per_column * 21


def _swatch(c: Canvas, name: str, x: float, y: float) -> None:
    """The key's sample of one element kind, drawn in a 24 by 16 cell at (x, y)."""

    if name == "time arrow":
        c.element(name, [c.line(x, y + 8, x + 22, y + 8, sw=1.6, arrow=True)])
    elif name == "flow arrow":
        c.element(name, [c.line(x, y + 8, x + 22, y + 8, sw=1.8, arrow=True)])
    elif name == "instant marker":
        c.element(name, [c.line(x + 11, y, x + 11, y + 16, INK, 2.6)])
    elif name == "arm box":
        c.element(name, [c.rect(x, y + 1, 24, 14, "#ffffff", INK, 2.2, rx=5)])
    elif name == "pulse calibration":
        c.element(name, [c.rect(x, y + 1, 24, 14, BLUE, BLUE, 2.2, opacity=0.12)])
    elif name == "computing or recording step":
        c.element(name, [c.rect(x, y + 1, 24, 14, PALE, LINE, 1.8)])
    elif name == "settle":
        c.element(name, [c.rect(x + 6, y, SETTLE_W, 16, f"url(#{c.prefix}-hatch)", MUTED, 1.2)])
    elif name == "reference member":
        c.element(name, [c.rect(x + 4, y, SQUARE, SQUARE, "#bdbdbd", LINE, 1.4)])
    elif name == "spare":
        c.element(name, [c.rect(x + 4, y, SQUARE, SQUARE, "#ffffff", LINE, 1.3, dash="3 2")])
    elif name == "interior reference":
        c.element(name, [c.rect(x + 4, y, SQUARE, SQUARE, "#ffffff", LINE, 1.6),
                         c.line(x + 4, y + SQUARE, x + 4 + SQUARE, y, LINE, 1.2)])
    elif name == "science stage":
        c.element(name, [c.rect(x, y + 1, 24, 14, "#ffffff", INK, 2.4)])
    elif name == "chain stop":
        c.element(name, [c.circle(x + 12, y + 8, 8, RED)])
    elif name == "clock-step control":
        c.element(name, [c.polygon([(x + 12, y - 1), (x + 21, y + 8), (x + 12, y + 17), (x + 3, y + 8)], BLUE, BLUE,
                                   2, opacity=0.12)])
    elif name == "monitor and meter bar":
        c.element(name, [c.rect(x, y + 6, 24, 5, "#9a9a9a", "none")])
    elif name == "workload bracket":
        c.element(name, [c.line(x, y + 5, x + 24, y + 5, MUTED, 1.4), c.line(x, y + 5, x, y + 11, MUTED, 1.4),
                         c.line(x + 24, y + 5, x + 24, y + 11, MUTED, 1.4)])
    elif name == "stage band":
        c.element(name, [c.rect(x, y + 1, 24, 14, "#f7f7f7", RULE, 1.2)])
    elif name == "check box":
        c.element(name, [c.rect(x, y + 1, 24, 14, "#ffffff", LINE, 1.8)])
    elif name == "process box":
        c.element(name, [c.rect(x, y + 1, 24, 14, PALE, LINE, 1.8)])
    elif name == "stop box":
        c.element(name, [c.rect(x, y + 1, 24, 14, "#ffffff", RED, 2.2)])
    elif name == "note":
        c.element(name, [c.rect(x, y + 1, 24, 14, "#ffffff", MUTED, 1.4, dash="5 4")])
    elif name == "decision":
        c.element(name, [c.polygon([(x + 12, y - 1), (x + 24, y + 8), (x + 12, y + 17), (x, y + 8)], "#ffffff",
                                   INK, 2)])
    elif name == "consequence box":
        c.element(name, [c.rect(x, y + 1, 24, 14, BLUE, BLUE, 2, opacity=0.12)])
    elif name == "outcome":
        c.element(name, [c.rect(x, y + 1, 24, 14, "#ffffff", INK, 3)])
    else:
        raise SourceError(f"no key sample for {name!r}")


# ---- Figure B-S3 ----------------------------------------------------------------------

S3_TITLE = "Figure B-S3. What can stop a window, what is only recorded, and when a window may carry a claim"
S3_SUBTITLE = "Schematic decision flow of the registered design. No measured data is shown."

S3_KEY: tuple[tuple[str, str], ...] = (
    ("stage band", "one of three times: start, window, afterwards"),
    ("flow arrow", "what happens next"),
    ("check box", "conditions that are tested"),
    ("decision", "a yes-or-no question"),
    ("process box", "work that is done"),
    ("stop box", "the only events that end a running window"),
    ("consequence box", "what the flag catalog does with a flag"),
    ("note", "the rule for a missing reading or a missing code"),
    ("outcome", "how an attempt ends"),
)


def _box(c: Canvas, element: str, label: str, x: float, y: float, w: float, h: float, title: str,
         paragraphs: Sequence[str], *, fill: str = "#ffffff", stroke: str = LINE, sw: float = 1.8, dash: str = "",
         opacity: float | None = None, size: float = 12.5, leading: float = 16) -> None:
    """A titled box of wrapped text; refuses text that runs past the box."""

    c.element(element, [c.rect(x, y, w, h, fill, stroke, sw, dash, opacity=opacity)], label)
    baseline = y + 21
    if title:
        c.text(x + 12, baseline, title, 13, INK, bold=True)
        baseline += leading + 3
    last = baseline
    for paragraph in paragraphs:
        after = c.paragraph(x + 12, baseline, w - 24, paragraph, size, leading)
        last, baseline = after - leading, after + 4
    if last > y + h - 7:
        raise SourceError(f"the text of box {label!r} runs {last - (y + h - 7):.0f} px past its box")


def _arrow(c: Canvas, points: Sequence[tuple[float, float]], label: str | None = None) -> None:
    """A flow arrow along ``points``; the head is on the last segment."""

    shapes = [c.line(x1, y1, x2, y2, sw=1.8, arrow=index == len(points) - 2)
              for index, ((x1, y1), (x2, y2)) in enumerate(zip(points, points[1:]))]
    c.element("flow arrow", shapes, label)


def _diamond(c: Canvas, label: str, cx: float, cy: float, half_w: float, half_h: float, lines: Sequence[str]) -> None:
    c.element("decision", [c.polygon([(cx, cy - half_h), (cx + half_w, cy), (cx, cy + half_h), (cx - half_w, cy)],
                                     "#ffffff", INK, 2.2)], label)
    c.lines(cx, cy - (len(lines) - 1) * 8 + 4.5, lines, 12.5, 16, INK, "middle")


def build_s3(v: Mapping[str, Any]) -> str:
    c = Canvas("bs3", 1200, S3_TITLE,
               "Schematic decision flow in three bands, read top to bottom. Band 1, at the scheduled start: the "
               "arm measures six physical hazards directly and makes two further checks; if any check fails the "
               "attempt ends with nothing launched, otherwise the chain starts. Band 2, during the window: every "
               "other check writes a flag and nothing stops collection except seven named stops. Band 3, after "
               "the window: the harvest writes every flag, the sealed flag catalog gives each code one of three "
               "consequences, and a three-part test decides whether the window is claim-usable; if it is not, "
               "the same pack is re-armed. A worked example follows. No measured data is shown.")
    c.text(LEFT, 32, S3_TITLE, 18, bold=True)
    c.text(LEFT, 54, S3_SUBTITLE, 13, MUTED)

    def band(y: float, h: float, number: int, title: str) -> None:
        c.element("stage band", [c.rect(LEFT - 14, y, RIGHT - LEFT + 28, h, "#f7f7f7", RULE, 1.2)], f"band {number}")
        c.text(LEFT, y + 24, f"{number}   {title}", 14.5, INK, bold=True)

    # Band 1: the start check.
    b1, b1_h = 74, 352
    band(b1, b1_h, 1, "At the scheduled start: the arm")
    hx, hy, hw, hh = LEFT, b1 + 38, 620, 300
    hazards = [
        ("competing process", f"for {unit(v['dwell_clean_s'], 's')} in a row, no process outside the measurement "
                              f"uses more than {num(v['cpu_limit'])} CPU-seconds per second; the check waits up to "
                              f"{unit(v['dwell_cap_s'], 's')} for such a stretch (this wait is the dwell)"),
        ("clock", "the largest member clock bound the window could produce, predicted for the longest stream "
                  f"({unit(v['t_stream_max_s'], 's')}), is at most {unit(v['clock_limit_ms'], 'ms')}; during the "
                  f"dwell the wall clock stays within {unit(v['clock_step_ms'], 'ms')} of its steady course and "
                  "its rate correction does not change"),
        ("battery", "the adapter is connected, the battery is not charging, and its current is within "
                    f"±{unit(v['battery_limit_ma'], 'mA')}"),
        ("thermal", f"the operating system reports thermal-pressure level {num(v['thermal_max_level'])}"),
        ("disk", "every volume has room for each planned copy of the window's bytes plus "
                 f"{unit(v['disk_headroom_gib'], 'GiB')}"),
        ("sampler", f"a {num(v['sampler_frames'])}-record idle capture ends within "
                    f"{unit(v['sampler_bound_s'], 's')}, with a median record interval of at most "
                    f"{unit(v['sampler_median_ms'], 'ms')} and none above {unit(v['sampler_max_ms'], 'ms')}"),
    ]
    c.element("check box", [c.rect(hx, hy, hw, hh, "#ffffff", LINE, 1.8)], "six physical hazards")
    c.text(hx + 12, hy + 22, "Six physical hazards, each measured directly by its hazard check", 13, INK,
           bold=True)
    baseline, indent = hy + 46, 140
    for name, rule in hazards:
        c.text(hx + 12, baseline, name, 12.5, INK, bold=True)
        baseline = c.paragraph(hx + indent, baseline, hw - indent - 14, rule, 12.5, 16.5) + 9
    if baseline - 16.5 - 9 > hy + hh - 7:
        raise SourceError("the hazard list runs past its box")

    ox, ow = hx + hw + 20, RIGHT - (hx + hw + 20)
    _box(c, "check box", "two further checks", ox, hy, ow, 84, "Two further checks",
         ["The agent census is clean: no AI agent session is running on the machine.",
          "The OS build and Mac model are ones the calibration acceptance covers."], size=12, leading=15.5)
    dx, dy, dw, dh = ox + 80, hy + 84 + 22 + 46, 66, 46
    _diamond(c, "every check passes?", dx, dy, dw, dh, ["every check", "passes?"])
    _arrow(c, [(hx + hw, dy), (dx - dw, dy)])
    _arrow(c, [(dx, hy + 84), (dx, dy - dh)])
    nx = dx + dw + 44
    _box(c, "outcome", "NULL attempt", nx, dy - dh, RIGHT - nx, 2 * dh, "NULL attempt",
         ["Nothing is launched or collected. The pack (the window's plan) is re-armed, that is, scheduled "
          "again, once the cause is removed."],
         sw=3, stroke=INK, size=12, leading=15.5)
    _arrow(c, [(dx + dw, dy), (nx, dy)], "no")
    c.text(dx + dw + 21, dy - 7, "no", 12, INK, "middle")
    note_y = dy + dh + 14
    _box(c, "note", "unmeasured hazard check", nx - 34, note_y, RIGHT - nx + 34, hy + hh - note_y, "",
         ["A hazard check that cannot take its reading answers UNMEASURED. For the sampler that refuses: a "
          "sampler that cannot sample is the hazard. For the other five it is recorded as a flag (band 2) and "
          "the arm goes on; the monitor measures them during the window."],
         dash="5 4", stroke=MUTED, sw=1.4, size=11.5, leading=15)

    # Band 2: collection.
    b2, b2_h = b1 + b1_h + 26, 206
    band(b2, b2_h, 2, "During the window: collection")
    py, ph, pw = b2 + 38, 154, 520
    _box(c, "process box", "the chain runs the stages", LEFT, py, pw, ph, "The chain runs the stages of Figure B-S1",
         ["A failed member costs only itself. Every check other than the stops at right writes what it finds "
          "as a flag: one line holding a code, what it applies to (the window, a stage, a quad or a member), a "
          "time interval, the observed and expected values, and digests of the evidence. A flag never stops "
          "collection.",
          "A hazard that appears now is recorded by the monitor and becomes a flag on each member it overlaps."],
         fill=PALE)
    down_x = LEFT + 260
    _arrow(c, [(dx, dy + dh), (dx, b2 - 13), (down_x, b2 - 13), (down_x, py)], "yes: GO")
    c.text(dx + 12, dy + dh + 20, "yes: GO", 12, INK)
    c.text(down_x + 12, b2 - 19, "the monitor starts, then the chain", 12, MUTED)

    sx = LEFT + pw + 20
    stop_w = RIGHT - sx
    c.element("stop box", [c.rect(sx, py, stop_w, ph, "#ffffff", RED, 2.2)], "the only stops")
    c.text(sx + 12, py + 21, "The only stops", 13, INK, bold=True)
    second = sx + 12 + (stop_w - 24) / 2 + 8
    c.text(sx + 12, py + 42, "By the chain, before the first member", 12, INK, bold=True)
    c.lines(sx + 12, py + 59, ["1  the bracket reservation fails",
                               "2  the pre calibration cannot be recorded",
                               "3  its pulse timing bound is above the pre",
                               f"    screen, {unit(v['pre_screen_ms'], 'ms')}"], 12, 16)
    c.text(second, py + 42, "By the driver, at any time", 12, INK, bold=True)
    c.lines(second, py + 59,
            [f"free disk falls below {unit(v['disk_low_gib'], 'GiB')}",
             "the agent census finds an agent session",
             f"the monitor is silent for {num(v['monitor_outage_min'])} minutes",
             "the window's deadline passes"], 12, 16)
    c.paragraph(sx + 12, py + 128, stop_w - 24,
                "A stopped window is still harvested. With no member, or with no post calibration, it cannot "
                "be claim-usable.", 12, 16)

    # Band 3: the harvest.
    b3, b3_h = b2 + b2_h + 26, 378
    band(b3, b3_h, 3, "After the window: the harvest")
    gy, gh, gw = b3 + 38, 150, 350
    _box(c, "process box", "the harvest", LEFT, gy, gw, gh, "The harvest",
         ["The program run on the window's preserved bytes after the chain exits. It re-derives each check that "
          "protects a number, joins the monitor's readings to each member's time span, and writes every flag. "
          "The numbers are always emitted, together with the flags."], fill=PALE)
    _arrow(c, [(down_x, py + ph), (down_x, gy)], "the chain exits")
    c.text(down_x + 12, b3 - 9, "the chain exits", 12, MUTED)
    kx, kw = LEFT + gw + 30, 196
    _box(c, "process box", "sealed flag catalog", kx, gy, kw, gh, "Sealed flag catalog",
         [f"The harvest looks up each flag's code here: {num(v['catalog_codes'])} codes, each with exactly one "
          "of three consequences."], fill=PALE)
    _arrow(c, [(LEFT + gw, gy + gh / 2), (kx, gy + gh / 2)])
    ex = kx + kw + 30
    ew = RIGHT - ex
    effects = [
        ("disclose", "DISCLOSE", v["catalog_disclose"], "the flag is recorded and reported; it removes nothing"),
        ("remove the member", "EXCLUDE_MEMBER", v["catalog_exclude_member"],
         "the member leaves every number it feeds, and its unit goes with it: one absolute repeat, or the "
         "whole quad"),
        ("remove the window", "EXCLUDE_WINDOW", v["catalog_exclude_window"], "the window is not claim-usable"),
    ]
    ey = gy
    for (name, code, count, meaning), height in zip(effects, (42, 58, 42)):
        c.element("consequence box", [c.rect(ex, ey, ew, height, BLUE, BLUE, 2, opacity=0.12)], name)
        c.text(ex + 12, ey + 18, f"{name} ({code}): {num(count)} codes", 12.5, INK, bold=True)
        lines = wrap(meaning, ew - 24, 12)
        if 18 + len(lines) * 15.5 > height - 2:
            raise SourceError(f"the meaning of {name} does not fit its box")
        c.lines(ex + 12, ey + 34, lines, 12, 15.5)
        _arrow(c, [(kx + kw, gy + gh / 2), (kx + kw + 14, gy + gh / 2), (kx + kw + 14, ey + height / 2),
                   (ex, ey + height / 2)])
        ey += height + 4
    _box(c, "note", "unclassified code", kx, gy + gh + 12, RIGHT - kx, 34, "",
         ["A code missing from the catalog is unclassified: it holds back only the later release of energies, "
          "never collection."], dash="5 4", stroke=MUTED, sw=1.4, size=11.5, leading=15)

    ty, th, tw = gy + gh + 72, 106, 470
    c.element("check box", [c.rect(LEFT, ty, tw, th, "#ffffff", LINE, 1.8)], "claim-usable test")
    c.text(LEFT + 12, ty + 21, "Claim-usable when all three hold", 13, INK, bold=True)
    baseline = ty + 41
    for letter, condition in (
            ("a", "no flag with the consequence “remove the window” fired"),
            ("b", "in the contrast window, the midpoint reference is not a lost reference"),
            ("c", f"every paper cell keeps at least {num(v['unit_minimum'])} of its {num(v['repeats'])} absolute "
                  f"repeats and {num(v['unit_minimum'])} of its {num(v['quads'])} quads; each contrast keeps at "
                  f"least {num(v['unit_minimum'])} of its {num(v['quads'])} quads")):
        c.text(LEFT + 12, baseline, letter, 12, INK, bold=True)
        baseline = c.paragraph(LEFT + 30, baseline, tw - 42, condition, 12, 15.5) + 2
    if baseline - 15.5 - 2 > ty + th - 7:
        raise SourceError("the claim-usable conditions run past their box")
    apply_x = LEFT + 150
    _arrow(c, [(apply_x, gy + gh), (apply_x, ty)], "the consequences are applied to the flags")
    c.lines(apply_x + 12, gy + gh + 27, ["the consequences are", "applied to the flags"], 12, 15, MUTED)
    qx, qy, qw, qh = LEFT + tw + 84, ty + th / 2, 64, 40
    _diamond(c, "claim-usable?", qx, qy, qw, qh, ["claim-", "usable?"])
    _arrow(c, [(LEFT + tw, qy), (qx - qw, qy)])
    ux = qx + qw + 44
    uw = RIGHT - ux
    _box(c, "outcome", "claim-usable", ux, ty + 2, uw, 46, "",
         ["Yes: this attempt is its pack's analysed window. The next pack is armed."],
         sw=3, stroke=INK, size=12, leading=15.5)
    _box(c, "outcome", "not claim-usable", ux, ty + 58, uw, 46, "",
         ["No: the attempt feeds no number and its cause is listed. The same pack is re-armed."],
         sw=3, stroke=INK, size=12, leading=15.5)
    branch = qx + qw + 22
    _arrow(c, [(qx + qw, qy), (branch, qy), (branch, ty + 25), (ux, ty + 25)], "yes")
    _arrow(c, [(branch, qy), (branch, ty + 81), (ux, ty + 81)], "no")
    c.text(branch - 5, ty + 21, "yes", 11.5, INK, "end")
    c.text(branch - 5, ty + 94, "no", 11.5, INK, "end")

    # Worked example.
    wy = b3 + b3_h + 30
    c.text(LEFT, wy, "Worked example (synthetic).", 12.5, bold=True)
    after = c.paragraph(
        LEFT + 190, wy, RIGHT - LEFT - 190,
        "In a single-model window, one member of decode quad 4 is aborted because the machine was not quiet "
        "during its idle baseline, and a competing process overlaps a request in decode quad 7. Both flags have "
        "the consequence “remove the member”, so both quads are removed whole. "
        f"The decode paper cell keeps {num(v['repeats'])} of {num(v['repeats'])} absolute repeats and "
        f"{num(v['quads'] - 2)} of {num(v['quads'])} quads, which meets condition c. Had a third quad lost a "
        f"member, {num(v['quads'] - 3)} of {num(v['quads'])} would remain: condition c fails, the window is not "
        "claim-usable, and the same pack is re-armed.",
        12.5, 17)

    # Key.
    yk = after + 20
    c.element("separator rule", [c.line(LEFT, yk - 14, RIGHT, yk - 14, RULE, 1.5)])
    c.text(LEFT, yk + 6, "Key", 13.5, bold=True)
    bottom = _key(c, S3_KEY, yk + 20, columns=2, name_w=128)
    return c.render(bottom + 14)


# --------------------------------------------------------------------------- command line


def build(repo: Path = REPO) -> dict[str, str]:
    """Both figures, as {file name: SVG text}."""

    v = values(load_sources(repo))
    return {S1_NAME: build_s1(v), S3_NAME: build_s3(v)}


def source_report(repo: Path = REPO) -> str:
    """Every value and where it was read, for a later sync against the sealed registration."""

    sources = load_sources(repo)
    v = values(sources)
    rows = [f"{key} = {num(v[key]) if not isinstance(v[key], list) else '(stage list)'}"
            for key in sorted(v) if key not in sources["prose"]]
    rows.append("")
    rows += [f"{key} = {entry['value']}  <- registration section {entry['section']} line {entry['line']}: "
             f"{entry['fragment']!r}" for key, entry in sources["prose"].items()]
    return "\n".join(rows) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="compare with the committed files; write nothing")
    parser.add_argument("--sources", action="store_true", help="print every value and its source; write nothing")
    arguments = parser.parse_args(argv)
    if arguments.sources:
        sys.stdout.write(source_report())
        return 0
    stale = []
    for name, text in build().items():
        path = HERE / name
        if arguments.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                stale.append(name)
        else:
            path.write_text(text, encoding="utf-8")
    if stale:
        print("differs from a fresh build: " + ", ".join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
