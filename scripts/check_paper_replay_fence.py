#!/usr/bin/env python3
"""Replay fence for the two Section 4 worked examples in ``docs/paper/draft-v2-skeleton.md``.

WHAT THIS GUARDS.  Section 4 of the draft carries two worked examples that
quote numbers from one retained diagnostic capture, member
``20260722T145535-e941c821``:

  1. the *worked current-capture arithmetic* paragraph (pulse-edge detection:
     the pulse count, the evaluated-rectangle count, the local clock-anchor
     bound, the capture bound, and every value describing pulse index 9 --
     the tenth commanded pulse of the capture); and
  2. the *five paired clock readings* table (the wall value, the two
     bracketing monotonic values, and the resolution of each of the five
     stamps the anchor estimator requires).

Until PR #171 those two sites were holes: the only mechanical guard over them
was an assertion that they were still empty.  Filling them retired that guard,
and this script is what replaces it.  It re-derives both substitutions from the
capture's primary custody artifacts and requires the re-derived values to agree
with the literals printed in the draft.

WHAT "AGREE" MEANS HERE.  Every numeric literal in the draft is read back with
``float()`` and must be *the same double* as the re-derived value -- equality of
IEEE-754 values, not a tolerance.  A literal that dropped or altered a digit no
longer reads back as the same double and fails.  Counts are compared as exact
integers.  Two derived quantities are stated in the draft in rounded form and
are compared against an explicitly stated rounding rule instead: the best-fit
lag pair (three decimals, signed) and the subtraction result (exact decimal
arithmetic on the two literals, via ``decimal.Decimal``).

HOW THE VALUES ARE RE-DERIVED.  The read path mirrors
``docs/process_traces/2026-08-19-refreeze-execution/r6-issuance/prove_r6_neutrality.py``:
the retained ``instrument_evidence.json`` supplies the recorded clock-stamp
block and the artifact hashes; ``raw/powermetrics.plist`` and ``events.jsonl``
are located, hash-verified against that block, and handed to
``derive_powermetrics_anchor_v3`` (clock anchor) and to
``rederive_detection_from_artifacts`` (pulse fits, capture bound, evaluated-cell
count) under the v3 anchor method.  The stored pulse rows and the stored bound
are never inputs to the comparison; only the primary bytes are.

THE PRIMARY ARTIFACTS ARE NOT IN THE REPOSITORY.  ``raw/powermetrics.plist`` is
about 88 MB and lives in the working checkout (or in the iCloud backup root),
not in git.  When it cannot be found the script exits 3 -- a distinct code from
both success and mismatch, so an absent corpus can never be read as a pass.

USAGE
    python3 scripts/check_paper_replay_fence.py [--repository-root DIR]
        [--corpus-root DIR] [--draft PATH] [--literals-only] [--json OUT]

EXIT CODES
    0  every fenced value re-derived and matched (or, with --literals-only,
       every literal was extracted and the draft-internal identities held)
    2  at least one mismatch, or a literal could not be extracted
    3  the primary artifacts could not be located or failed their hash check
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

# The capture the two Section 4 worked examples quote, and the pulse they
# single out.  Both are stated in the draft's own evidence comments.
MEMBER_ID = "20260722T145535-e941c821"
SOURCE_DIRECTORY = Path("runs_window_a_20260722") / "instrument_validation" / MEMBER_ID
PULSE_INDEX = 9

# Additional roots searched for the raw plist, mirroring prove_r6_neutrality.py.
BACKUP_ROOTS = (
    Path("/Users/edr/Library/Mobile Documents/com~apple~CloudDocs/JouleWise-backup"),
)

ORDINAL_WORDS = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth",
    5: "fifth",
    6: "sixth",
    7: "seventh",
    8: "eighth",
    9: "ninth",
    10: "tenth",
    11: "eleventh",
    12: "twelfth",
}


class FenceError(RuntimeError):
    """A literal could not be extracted, or the draft contradicts itself."""


class ArtifactsUnavailable(RuntimeError):
    """The primary custody artifacts are not present on this machine."""


# --------------------------------------------------------------------------
# Draft side: extract the literals, anchored so a moved sentence fails closed.
# --------------------------------------------------------------------------


def _search(pattern: str, text: str, label: str) -> re.Match[str]:
    matches = list(re.finditer(pattern, text))
    if len(matches) != 1:
        raise FenceError(f"{label}: expected exactly one anchor match, found {len(matches)}")
    return matches[0]


def _paragraph(text: str, opening: str, label: str) -> str:
    index = text.find(opening)
    if index < 0 or text.find(opening, index + 1) >= 0:
        raise FenceError(f"{label}: opening anchor is missing or not unique")
    end = text.find("\n", index)
    return text[index : end if end >= 0 else len(text)]


def _number(raw: str) -> str:
    """Strip the LaTeX thousands separator so ``122{,}859`` reads as a number."""

    return raw.replace("{,}", "").replace(",", "")


def extract_draft_literals(draft_text: str) -> dict[str, Any]:
    """Return every fenced literal, keyed by the name of the value it states."""

    literals: dict[str, Any] = {}

    # Historical submission and the frozen v1 prose are both supported, but
    # exactly one heading across both forms is required.
    heading = _search(
        r"(?m)^([*]{1,2}Worked (?:historical|current)-capture arithmetic\.[*]{1,2}) ",
        draft_text,
        "worked-arithmetic heading",
    ).group(1)
    arithmetic = _paragraph(draft_text, heading, "worked-arithmetic paragraph")

    literals["pulse_count"] = _number(
        _search(r"reports all \\\(([0-9{},]+)\\\) pulses detected", arithmetic, "pulse count")
        .group(1)
    )
    literals["cell_count"] = _number(
        _search(
            r"\\\(([0-9{},]+)\\\) evaluated rectangles", arithmetic, "evaluated-rectangle count"
        ).group(1)
    )
    literals["anchor_bound_s"] = _search(
        r"a local clock-anchor bound of \\\(([0-9.eE+-]+)\\\) s",
        arithmetic,
        "clock-anchor bound",
    ).group(1)
    literals["b_fiducial_s"] = _search(
        r"a final capture bound of \\\(([0-9.eE+-]+)\\\) s", arithmetic, "capture bound"
    ).group(1)

    difference = _search(
        r"largest pulse residual before the anchor term is "
        r"\\\(([0-9.eE+-]+)-([0-9.eE+-]+)=([0-9.eE+-]+)\\\) s",
        arithmetic,
        "residual subtraction",
    )
    literals["subtraction_minuend"] = difference.group(1)
    literals["subtraction_subtrahend"] = difference.group(2)
    literals["subtraction_result"] = difference.group(3)

    literals["pulse_ordinal_word"] = _search(
        r"the pulse attaining the maximum: the ([a-z]+) commanded pulse",
        arithmetic,
        "maximal-pulse ordinal",
    ).group(1)

    planned = _search(
        r"scheduled to switch on \\\(([0-9.]+)\\\) s and off \\\(([0-9.]+)\\\) s",
        arithmetic,
        "planned pulse offsets",
    )
    literals["planned_on_offset_s"] = planned.group(1)
    literals["planned_off_offset_s"] = planned.group(2)

    commanded = _search(
        r"commands were stamped at \\\(([0-9.]+)\\\) s and \\\(([0-9.]+)\\\) s of wall time",
        arithmetic,
        "commanded epochs",
    )
    literals["command_on_epoch_s"] = commanded.group(1)
    literals["command_off_epoch_s"] = commanded.group(2)

    onset = _search(
        r"onset lag anywhere in \\\(\[([0-9.eE+-]+),\\,([0-9.eE+-]+)\]\\\) s",
        arithmetic,
        "onset residual interval",
    )
    literals["onset_residual_lower_s"] = onset.group(1)
    literals["onset_residual_upper_s"] = onset.group(2)

    offset = _search(
        r"offset lag anywhere in \\\(\[([0-9.eE+-]+),\\,([0-9.eE+-]+)\]\\\) s",
        arithmetic,
        "offset residual interval",
    )
    literals["offset_residual_lower_s"] = offset.group(1)
    literals["offset_residual_upper_s"] = offset.group(2)

    best_fit = _search(
        r"about a best-fit pair of \\\(([+-][0-9.]+)\\\) s and \\\(([+-][0-9.]+)\\\) s",
        arithmetic,
        "best-fit lag pair",
    )
    literals["best_fit_delta_on_s"] = best_fit.group(1)
    literals["best_fit_delta_off_s"] = best_fit.group(2)

    literals["retained_residual_bound_s"] = _search(
        r"those four endpoints allow — \\\(([0-9.eE+-]+)\\\) s, the upper end of the onset interval",
        arithmetic,
        "retained residual bound",
    ).group(1)

    literals["clock_stamps"] = _extract_stamp_table(draft_text)

    caption = _search(
        r"the wall clock's \\\(([0-9.]+)\\times10\^\{(-?[0-9]+)\}\\\) s against the monotonic "
        r"clock's \\\(([0-9.]+)\\times10\^\{(-?[0-9]+)\}\\\) s",
        draft_text,
        "stamp-resolution caption",
    )
    literals["wall_resolution_s"] = f"{caption.group(1)}e{caption.group(2)}"
    literals["monotonic_resolution_s"] = f"{caption.group(3)}e{caption.group(4)}"

    return literals


def _extract_stamp_table(draft_text: str) -> list[dict[str, str]]:
    """Return the five clock-stamp rows in the order the table prints them."""

    header = r"\| Stamp \\\(s\\\) \| \\\(W_s\\\) \(s\) \| \\\(M_s\^-\\\) \(s\) \| \\\(M_s\^\+\\\) \(s\) \| \\\(R_s\\\) \(s\) \|"
    start = _search(header, draft_text, "clock-stamp table header").end()
    lines = draft_text[start:].split("\n")
    if not lines or not lines[0].strip():
        lines = lines[1:]
    rows: list[dict[str, str]] = []
    for line in lines[1:]:  # skip the markdown separator row
        stripped = line.strip()
        if not stripped.startswith("|"):
            break
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 5:
            raise FenceError(f"clock-stamp table: row has {len(cells)} cells, expected 5")
        name = cells[0]
        if not (name.startswith("`") and name.endswith("`")):
            raise FenceError(f"clock-stamp table: row label {name!r} is not a code-span stamp name")
        rows.append(
            {
                "stamp": name.strip("`"),
                "epoch_s": cells[1],
                "monotonic_before_s": cells[2],
                "monotonic_after_s": cells[3],
                "resolution_s": cells[4],
            }
        )
    if len(rows) != 5:
        raise FenceError(f"clock-stamp table: found {len(rows)} rows, expected 5")
    return rows


def check_draft_internal_identities(literals: dict[str, Any]) -> list[str]:
    """Check the identities the draft asserts about its own numbers.

    These need no artifacts.  The paragraph states a subtraction and names its
    two operands, so the printed difference must be the exact decimal
    difference of the two printed operands.  It also repeats the capture bound
    and the clock-anchor bound inside that subtraction, so the repeats must be
    character-identical to the first statement of each.
    """

    failures: list[str] = []
    if literals["subtraction_minuend"] != literals["b_fiducial_s"]:
        failures.append(
            "subtraction minuend {0!r} differs from the stated capture bound {1!r}".format(
                literals["subtraction_minuend"], literals["b_fiducial_s"]
            )
        )
    if literals["subtraction_subtrahend"] != literals["anchor_bound_s"]:
        failures.append(
            "subtraction subtrahend {0!r} differs from the stated clock-anchor bound {1!r}".format(
                literals["subtraction_subtrahend"], literals["anchor_bound_s"]
            )
        )
    exact = Decimal(literals["subtraction_minuend"]) - Decimal(literals["subtraction_subtrahend"])
    if exact != Decimal(literals["subtraction_result"]):
        failures.append(
            "printed difference {0!r} is not the exact decimal difference {1}".format(
                literals["subtraction_result"], exact
            )
        )
    return failures


# --------------------------------------------------------------------------
# Artifact side: re-derive both substitutions from the primary custody bytes.
# --------------------------------------------------------------------------


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def locate_raw_powermetrics(corpus_root: Path, expected_sha256: str) -> bytes:
    """Return the retained raw plist bytes, hash-verified against the evidence."""

    candidates: list[Path] = [corpus_root / SOURCE_DIRECTORY / "raw" / "powermetrics.plist"]
    for root in BACKUP_ROOTS:
        if root.is_dir():
            candidates.extend(root.glob(f"*/instrument_validation/{MEMBER_ID}/raw/powermetrics.plist"))
            candidates.extend(
                root.glob(f"*/*/instrument_validation/{MEMBER_ID}/raw/powermetrics.plist")
            )
    seen: list[str] = []
    for candidate in candidates:
        if not candidate.is_file():
            continue
        raw = candidate.read_bytes()
        if _sha256(raw) == expected_sha256:
            return raw
        seen.append(f"{candidate} (sha256 {_sha256(raw)})")
    raise ArtifactsUnavailable(
        "raw/powermetrics.plist matching sha256 "
        f"{expected_sha256} not found; inspected: {seen or 'no candidate paths existed'}"
    )


def derive_from_artifacts(repository_root: Path, corpus_root: Path) -> dict[str, Any]:
    """Re-derive every fenced value from the capture's primary bytes."""

    sys.path.insert(0, str(repository_root))
    sys.dont_write_bytecode = True

    from joulewise.adapters.powermetrics import (  # noqa: PLC0415
        anchor_records_from_powermetrics,
        parse_powermetrics_records,
    )
    from joulewise.powermetrics_fiducial import (  # noqa: PLC0415
        rederive_detection_from_artifacts,
    )
    from joulewise.uncertainty_evidence import (  # noqa: PLC0415
        CLOCK_METHOD_V3,
        STAMP_ORDER,
        derive_powermetrics_anchor_v3,
        stamp_from_mapping,
    )

    directory = corpus_root / SOURCE_DIRECTORY
    evidence_path = directory / "instrument_evidence.json"
    if not evidence_path.is_file():
        raise ArtifactsUnavailable(f"{evidence_path} is not present")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    hashes = evidence["artifact_sha256"]

    events_raw = (directory / "events.jsonl").read_bytes()
    if _sha256(events_raw) != hashes["events.jsonl"]:
        raise ArtifactsUnavailable("events.jsonl does not match its retained sha256")
    raw = locate_raw_powermetrics(corpus_root, hashes["raw/powermetrics.plist"])

    anchor_block = evidence["clock_anchor"]
    stamps = {
        name: stamp_from_mapping(row)
        for name, row in anchor_block["clock_stamps"].items()
        if isinstance(row, dict)
    }
    derived_anchor = derive_powermetrics_anchor_v3(
        stamps=stamps,
        records=anchor_records_from_powermetrics(parse_powermetrics_records(raw)),
    )
    if derived_anchor.get("status") != "bounded":
        raise FenceError(f"re-derived clock anchor is not bounded: {derived_anchor.get('status')!r}")

    detection = rederive_detection_from_artifacts(
        raw, events_raw, anchor_block, anchor_method=CLOCK_METHOD_V3
    )
    if not detection.all_pulses_detected:
        raise FenceError("re-derived detection did not detect every commanded pulse")

    fit = detection.fits[PULSE_INDEX]
    if fit.pulse_index != PULSE_INDEX:
        raise FenceError(f"fit at position {PULSE_INDEX} carries pulse_index {fit.pulse_index}")

    # The draft claims this pulse ATTAINS the maximum residual.  A pulse's
    # retained residual is the largest absolute value its four allowed edge
    # endpoints permit; the claim holds only if index 9 is the unique argmax.
    residuals = [
        max(
            abs(candidate.onset_residual_lower_s),
            abs(candidate.onset_residual_upper_s),
            abs(candidate.offset_residual_lower_s),
            abs(candidate.offset_residual_upper_s),
        )
        for candidate in detection.fits
    ]
    largest = max(residuals)
    if residuals.count(largest) != 1 or residuals.index(largest) != PULSE_INDEX:
        raise FenceError(
            "pulse {0} is not the unique maximal-residual pulse (argmax {1}, ties {2})".format(
                PULSE_INDEX, residuals.index(largest), residuals.count(largest)
            )
        )

    events = [json.loads(line) for line in events_raw.decode("utf-8").splitlines() if line.strip()]
    commanded_on = [row for row in events if row.get("event_type") == "pulse_command_on"]
    commanded_off = [row for row in events if row.get("event_type") == "pulse_command_off"]
    if len(commanded_on) != len(commanded_off):
        raise FenceError("events.jsonl has unequal pulse_command_on and pulse_command_off counts")
    on_event = commanded_on[PULSE_INDEX]["metadata"]
    off_event = commanded_off[PULSE_INDEX]["metadata"]

    stamp_rows = []
    for name in STAMP_ORDER:
        row = anchor_block["clock_stamps"][name]
        stamp_rows.append(
            {
                "stamp": name,
                "epoch_s": float(row["epoch_s"]),
                "monotonic_before_s": float(row["monotonic_before_s"]),
                "monotonic_after_s": float(row["monotonic_after_s"]),
                # R_s is the coarser of the two resolutions recorded with the
                # stamp, which is what the solver charges for the pair.
                "resolution_s": max(
                    float(row["wall_resolution_s"]), float(row["monotonic_resolution_s"])
                ),
            }
        )
    wall_resolutions = {
        float(anchor_block["clock_stamps"][name]["wall_resolution_s"]) for name in STAMP_ORDER
    }
    monotonic_resolutions = {
        float(anchor_block["clock_stamps"][name]["monotonic_resolution_s"]) for name in STAMP_ORDER
    }
    if len(wall_resolutions) != 1 or len(monotonic_resolutions) != 1:
        raise FenceError("the five stamps do not share one wall and one monotonic resolution")

    return {
        "pulse_count": len(commanded_on),
        "cell_count": detection.projection_evaluated_cell_count,
        "anchor_bound_s": derived_anchor["effective_clock_anchor_bound_s"],
        "b_fiducial_s": detection.b_fiducial_s,
        "planned_on_offset_s": float(on_event["planned_on_offset_s"]),
        "planned_off_offset_s": float(off_event["planned_off_offset_s"]),
        "command_on_epoch_s": float(on_event["clock_stamp"]["epoch_s"]),
        "command_off_epoch_s": float(off_event["clock_stamp"]["epoch_s"]),
        "onset_residual_lower_s": fit.onset_residual_lower_s,
        "onset_residual_upper_s": fit.onset_residual_upper_s,
        "offset_residual_lower_s": fit.offset_residual_lower_s,
        "offset_residual_upper_s": fit.offset_residual_upper_s,
        "best_fit_delta_on_s": fit.delta_on_s,
        "best_fit_delta_off_s": fit.delta_off_s,
        "retained_residual_bound_s": largest,
        "clock_stamps": stamp_rows,
        "wall_resolution_s": next(iter(wall_resolutions)),
        "monotonic_resolution_s": next(iter(monotonic_resolutions)),
    }


# --------------------------------------------------------------------------
# Comparison.
# --------------------------------------------------------------------------


def compare(literals: dict[str, Any], derived: dict[str, Any]) -> list[dict[str, Any]]:
    """Return one comparison row per fenced value, each carrying its verdict."""

    rows: list[dict[str, Any]] = []

    def add(label: str, literal: str, value: Any, ok: bool) -> None:
        rows.append({"value": label, "draft": literal, "derived": repr(value), "match": ok})

    def add_exact_float(key: str) -> None:
        literal = literals[key]
        value = derived[key]
        add(key, literal, value, float(literal) == value)

    def add_exact_int(key: str) -> None:
        literal = literals[key]
        value = derived[key]
        add(key, literal, value, int(literal) == int(value))

    add_exact_int("pulse_count")
    add_exact_int("cell_count")
    for key in (
        "anchor_bound_s",
        "b_fiducial_s",
        "planned_on_offset_s",
        "planned_off_offset_s",
        "command_on_epoch_s",
        "command_off_epoch_s",
        "onset_residual_lower_s",
        "onset_residual_upper_s",
        "offset_residual_lower_s",
        "offset_residual_upper_s",
        "retained_residual_bound_s",
        "wall_resolution_s",
        "monotonic_resolution_s",
    ):
        add_exact_float(key)

    # The draft states the best-fit pair as "about" three signed decimals.
    for key in ("best_fit_delta_on_s", "best_fit_delta_off_s"):
        literal = literals[key]
        value = derived[key]
        add(key, literal, value, f"{value:+.3f}" == literal)

    ordinal = ORDINAL_WORDS.get(PULSE_INDEX + 1)
    add(
        "pulse_ordinal_word",
        literals["pulse_ordinal_word"],
        ordinal,
        ordinal is not None and literals["pulse_ordinal_word"] == ordinal,
    )

    # strict=True so a table that gained or lost a row cannot be compared
    # against a truncated pairing and reported as agreement.
    for index, (printed, computed) in enumerate(
        zip(literals["clock_stamps"], derived["clock_stamps"], strict=True)
    ):
        label = f"clock_stamps[{index}]"
        add(f"{label}.stamp", printed["stamp"], computed["stamp"], printed["stamp"] == computed["stamp"])
        for field in ("epoch_s", "monotonic_before_s", "monotonic_after_s", "resolution_s"):
            add(
                f"{label}.{field}",
                printed[field],
                computed[field],
                float(printed[field]) == computed[field],
            )

    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    here = Path(__file__).resolve().parent.parent
    parser.add_argument("--repository-root", type=Path, default=here)
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=None,
        help="root holding runs_window_a_20260722/ (default: the repository root)",
    )
    parser.add_argument("--draft", type=Path, default=None)
    parser.add_argument(
        "--literals-only",
        action="store_true",
        help="extract the draft literals and check the draft's internal identities only",
    )
    parser.add_argument("--json", type=Path, default=None, help="write the comparison rows here")
    args = parser.parse_args(argv)

    repository_root = args.repository_root.resolve()
    corpus_root = (args.corpus_root or repository_root).resolve()
    draft = args.draft or repository_root / "docs" / "paper" / "draft-v2-skeleton.md"

    try:
        literals = extract_draft_literals(draft.read_text(encoding="utf-8"))
        internal = check_draft_internal_identities(literals)
    except FenceError as exc:
        print(f"FENCE EXTRACTION FAILED: {exc}")
        return 2
    for failure in internal:
        print(f"DRAFT-INTERNAL MISMATCH: {failure}")

    if args.literals_only:
        print(f"LITERALS {len(literals)} extracted from {draft}")
        print(f"INTERNAL MISMATCHES {len(internal)}")
        return 0 if not internal else 2

    try:
        derived = derive_from_artifacts(repository_root, corpus_root)
    except ArtifactsUnavailable as exc:
        print(f"PRIMARY ARTIFACTS UNAVAILABLE: {exc}")
        return 3
    except FenceError as exc:
        print(f"RE-DERIVATION FAILED: {exc}")
        return 2

    rows = compare(literals, derived)
    for row in rows:
        flag = "ok  " if row["match"] else "FAIL"
        print(f"{flag} {row['value']}: draft={row['draft']} derived={row['derived']}")
    mismatches = [row for row in rows if not row["match"]]
    print(f"MEMBER {MEMBER_ID}")
    print(f"COMPARED {len(rows)}")
    print(f"MISMATCHES {len(mismatches) + len(internal)}")
    if args.json is not None:
        args.json.write_text(
            json.dumps(
                {
                    "member_id": MEMBER_ID,
                    "pulse_index": PULSE_INDEX,
                    "draft": str(draft),
                    "comparisons": rows,
                    "draft_internal_mismatches": internal,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return 0 if not mismatches and not internal else 2


if __name__ == "__main__":
    raise SystemExit(main())
