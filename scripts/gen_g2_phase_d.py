#!/usr/bin/env python3
"""Generate G2-a/G2-b governed-chain regions from the pinned window runbook."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNBOOK_PATH = REPO_ROOT / "docs/phase_2/window_runbook.md"
RUNSHEET_PATH = (
    REPO_ROOT
    / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
)
BEGIN_MARKER = "<!-- BEGIN GENERATED: g2-phase-d-governed-chain -->"
END_MARKER = "<!-- END GENERATED: g2-phase-d-governed-chain -->"
G2A_BEGIN_MARKER = "<!-- BEGIN GENERATED: g2a-governed-bracket -->"
G2A_END_MARKER = "<!-- END GENERATED: g2a-governed-bracket -->"

# These are the magistrate-pinned source anchors.  Validation is deliberately
# line-and-byte exact; a moved or edited anchor must be reviewed and re-pinned.
PINNED_ANCHORS = {
    1407: ".venv/bin/python scripts/recover_calibration_ledger.py readiness \\",
    1412: ".venv/bin/python scripts/reserve_calibration_window_bracket.py \\",
    1428: "  --execute",
    1516: "# First executable action: consume the inherited one-use FD and mint start",
    1541: 'NEG8_DRIFT_BOUND="$BOUND_RUNS_ROOT/neg8-drift-bound.json"',
    1556: '  /bin/sleep "$SETTLE_S"',
    1636: "  settle",
    1653: "run_stage_list() {",
    1663: 'cd "$REPO"',
    1693: 'screen_pre_calibration "$PRE_CAL_CUSTODY"',
    1727: 'echo "$(timestamp) measurement_complete" >> "$OPERATOR_LOG_ROOT/window-chain.log"',
}

SOURCE_START = "```zsh\n#!/bin/zsh\nset -euo pipefail\n"
SOURCE_END = (
    'echo "$(timestamp) measurement_complete" '
    '>> "$OPERATOR_LOG_ROOT/window-chain.log"\n```\n'
)
RESERVATION_SOURCE_START = (
    ".venv/bin/python scripts/recover_calibration_ledger.py readiness \\\n"
)
RESERVATION_SOURCE_END = "  --execute\n"
HELPERS_SOURCE_START = "timestamp() {\n"
HELPERS_SOURCE_END = "run_stage_list() {\n"

G2A_PROBE_LOOP = (
    "# G2-a-only delta: the diagnostic probe ladder is not a runbook science stage.\n"
    "for role in small large; do\n"
    "for length in 512 1024 2048 4096; do\n"
    '  config_dir="$G2A_CONFIG_ROOT/$role-p$length"\n'
    '  test -f "$config_dir/order_manifest.json"\n'
    '  run_stage "$G2A_RUNS_ROOT" "$G2A_LOG" "$config_dir" \\\n'
    '    "$G2A_PRE_CAL_CUSTODY" "$role-p$length"\n'
    "done\n"
    "done\n"
)

G2A_INPUT_CHECK = (
    "# Authenticate every probe input before ledger readiness or reservation.\n"
    'PYTHONPATH="$REPO" "$PY" "$REPO/scripts/generate_g2a_probe_inputs.py" check \\\n'
    '  --root "$G2A_ROOT" \\\n'
    '  --panel "$REPO/configs/model_panels/qwen3_4bit.json" \\\n'
    '  --ledger "$CALIBRATION_LEDGER" \\\n'
    '  --head-pin "$LEDGER_HEAD_PIN" \\\n'
    '  --campaign-policy "$POLICY"\n'
)


def _section_bounds(source: str, heading: str) -> tuple[int, int]:
    """Return the character bounds for one level-two runsheet section."""

    start = source.index(heading)
    following = re.search(r"^## ", source[start + len(heading) :], re.MULTILINE)
    end = len(source) if following is None else start + len(heading) + following.start()
    return start, end


def _line_number(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def inventory_g2a_shell_blocks(runsheet: str) -> list[tuple[int, int, str]]:
    """Inventory shell fences in the fixed-variable and G2-a sections.

    The inclusive line numbers deliberately cover the markdown fence lines:
    they are the stable source anchors recorded in an emitted chain.
    """

    sections = (
        _section_bounds(runsheet, "## Tree and fixed variables"),
        _section_bounds(runsheet, "## G2-a — first machine evening"),
    )
    blocks: list[tuple[int, int, str]] = []
    pattern = re.compile(r"^```(?:sh|zsh)\n(?P<body>.*?)^```$", re.MULTILINE | re.DOTALL)
    for start, end in sections:
        section = runsheet[start:end]
        for match in pattern.finditer(section):
            absolute_start = start + match.start()
            absolute_end = start + match.end()
            blocks.append(
                (
                    _line_number(runsheet, absolute_start),
                    _line_number(runsheet, absolute_end),
                    match.group("body"),
                )
            )
    return blocks


def render_g2a_night_chain(runsheet: str, night_date: str) -> str:
    """Render the reviewed G2-a night chain without the desk-only producer."""

    if re.fullmatch(r"[0-9]{8}", night_date) is None:
        raise ValueError("--night-date must be YYYYMMDD")
    blocks = inventory_g2a_shell_blocks(runsheet)
    expected_ranges = [(252, 302), (326, 349), (372, 383), (387, 562), (573, 585)]
    observed_ranges = [(start, end) for start, end, _body in blocks]
    if observed_ranges != expected_ranges:
        raise ValueError(
            "runsheet shell-fence inventory drifted: "
            f"observed={observed_ranges!r} expected={expected_ranges!r}"
        )

    fixed, g2a_exports, _desk_producer, bracket, summarizer = blocks
    adjusted_exports = g2a_exports[2].replace("20260830", night_date)
    required_inputs = (
        "# The desk producer runs while agents are present; require its outputs here.\n"
        'test -f "$G2A_INPUT_INVENTORY"\n'
        'test -f "$G2A_FROZEN_PLAN"\n'
        'test -f "$G2A_PROMPT_LADDER"\n'
    )
    pieces = ["#!/bin/zsh\n", "set -euo pipefail\n"]
    for start, end, body in (fixed, (g2a_exports[0], g2a_exports[1], adjusted_exports)):
        pieces.extend((f"\n# runsheet L{start}-{end}\n", body))
    pieces.extend(("\n# arm-time input assertions\n", required_inputs))
    for start, end, body in (bracket, summarizer):
        pieces.extend((f"\n# runsheet L{start}-{end}\n", body))
    return "".join(pieces)


def emit_g2a_night_chain(output_path: Path, night_date: str) -> None:
    """Write an executable chain and its GNU-format SHA-256 sidecar."""

    chain = render_g2a_night_chain(RUNSHEET_PATH.read_text(encoding="utf-8"), night_date)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(chain, encoding="utf-8")
    output_path.chmod(0o755)
    digest = hashlib.sha256(chain.encode("utf-8")).hexdigest()
    sidecar = output_path.with_name(f"{output_path.name}.sha256")
    sidecar.write_text(f"{digest}  {output_path.name}\n", encoding="utf-8")


def _replace_once(source: str, old: str, new: str, *, label: str) -> str:
    if source.count(old) != 1:
        raise ValueError(
            f"runbook {label} source must occur exactly once; observed={source.count(old)}"
        )
    return source.replace(old, new, 1)


def validate_pinned_anchors(runbook: str) -> None:
    lines = runbook.splitlines()
    for line_number, symbol in PINNED_ANCHORS.items():
        if line_number > len(lines) or lines[line_number - 1] != symbol:
            observed = lines[line_number - 1] if line_number <= len(lines) else "<EOF>"
            raise ValueError(
                f"runbook pinned anchor {line_number} drifted: "
                f"observed={observed!r} expected={symbol!r}"
            )


def extract_runbook_chain(runbook: str) -> str:
    validate_pinned_anchors(runbook)
    start = runbook.index(SOURCE_START)
    end = runbook.index(SOURCE_END, start) + len(SOURCE_END)
    return runbook[start:end]


def extract_runbook_reservation(runbook: str) -> str:
    validate_pinned_anchors(runbook)
    start = runbook.index(RESERVATION_SOURCE_START)
    end = runbook.index(RESERVATION_SOURCE_END, start) + len(RESERVATION_SOURCE_END)
    return runbook[start:end]


def extract_runbook_helpers(runbook: str) -> str:
    chain = extract_runbook_chain(runbook)
    start = chain.index(HELPERS_SOURCE_START)
    end = chain.index(HELPERS_SOURCE_END, start)
    return chain[start:end]


def render_g2a_generated_region(runbook: str) -> str:
    """Render the G2-a bracket from runbook reservation/writer/stage bytes."""

    reservation = extract_runbook_reservation(runbook)
    for old, new in (
        (
            ".venv/bin/python scripts/recover_calibration_ledger.py",
            '"$PY" "$REPO/scripts/recover_calibration_ledger.py"',
        ),
        (
            ".venv/bin/python scripts/reserve_calibration_window_bracket.py",
            '"$PY" "$REPO/scripts/reserve_calibration_window_bracket.py"',
        ),
        ("$BRACKET_SESSION_ID", "$G2A_BRACKET_SESSION_ID"),
        ("$FROZEN_PLAN", "$G2A_FROZEN_PLAN"),
        ("$WINDOW_ID", "$G2A_WINDOW_ID"),
        ("$PLAN_ID", "$G2A_PLAN_ID"),
        (
            '"2afabe9854a8ac8c9d3d212bb0236fa787d660cf5ef452c66f2d84f97d4f227d"',
            '"$G2A_PLAN_SHA256"',
        ),
        ("$EVIDENCE_ROOT_ID", "$G2A_EVIDENCE_ROOT_ID"),
        ("$RUNS_ROOT", "$G2A_RUNS_ROOT"),
        ("$PRE_ATTEMPT_ID", "$G2A_PRE_ATTEMPT_ID"),
        ("$POST_ATTEMPT_ID", "$G2A_POST_ATTEMPT_ID"),
        ("$IDENTITY_EPOCH_JSON", "$G2A_IDENTITY_EPOCH_JSON"),
        ("$T1_BINDINGS_JSON", "$G2A_T1_BINDINGS_JSON"),
    ):
        reservation = reservation.replace(old, new)

    helpers = extract_runbook_helpers(runbook)
    for old, new in (
        ("$RUNS_ROOT", "$G2A_RUNS_ROOT"),
        ("$OPERATOR_LOG_ROOT", "$G2A_OPERATOR_LOG_ROOT"),
        ("$QUARANTINE_ROOT", "$G2A_QUARANTINE_ROOT"),
        ("$BRACKET_SESSION_ID", "$G2A_BRACKET_SESSION_ID"),
        ("$FROZEN_PLAN", "$G2A_FROZEN_PLAN"),
    ):
        helpers = helpers.replace(old, new)

    return (
        f"{G2A_BEGIN_MARKER}\n"
        "<!-- GENERATED by scripts/gen_g2_phase_d.py from the pinned runbook "
        "reservation and foreground-chain helpers. -->\n"
        "```zsh\n"
        "set -euo pipefail\n\n"
        'test -f "$G2A_FROZEN_PLAN"\n'
        'test -f "$G2A_IDENTITY_EPOCH_JSON"\n'
        'test -f "$G2A_T1_BINDINGS_JSON"\n'
        'G2A_PLAN_ID="$(/usr/bin/jq -er \'.plan_id\' "$G2A_FROZEN_PLAN")"\n'
        'G2A_PLAN_SHA256="$(/usr/bin/shasum -a 256 "$G2A_FROZEN_PLAN" | '
        "/usr/bin/awk '{print $1}')\"\n"
        '/bin/mkdir -p "$G2A_RUNS_ROOT/instrument_validation" '
        '"$G2A_OPERATOR_LOG_ROOT" "$G2A_TRANSCRIPT_ROOT" '
        '"$G2A_QUARANTINE_ROOT"\n\n'
        f"{helpers}"
        f"{G2A_INPUT_CHECK}\n"
        f"{reservation}\n"
        'cd "$REPO"\n'
        'echo "$(timestamp) g2a_chain_start" >> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"\n'
        "# Runbook §5C/§6 settle: operator activity ends before the pre slot.\n"
        "settle\n"
        'G2A_PRE_CAL_CUSTODY="$(calibrate_slot pre "$G2A_PRE_ATTEMPT_ID")"\n'
        'echo "$(timestamp) pre_calibration=$G2A_PRE_CAL_CUSTODY" '
        '>> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"\n'
        'screen_pre_calibration "$G2A_PRE_CAL_CUSTODY"\n\n'
        f"{G2A_PROBE_LOOP}\n"
        'G2A_POST_CAL_CUSTODY="$(calibrate_slot post "$G2A_POST_ATTEMPT_ID")"\n'
        'echo "$(timestamp) post_calibration=$G2A_POST_CAL_CUSTODY" '
        '>> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"\n'
        "# Ratified terminal boundary: preserve physical-ahead and its exact candidate.\n"
        '"$PY" "$REPO/scripts/recover_calibration_ledger.py" \\\n'
        '  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \\\n'
        '  session-status --session-id "$G2A_BRACKET_SESSION_ID" '
        '--plan "$G2A_FROZEN_PLAN" \\\n'
        '  > "$G2A_TRANSCRIPT_ROOT/g2a-post-bracket-terminal-boundary.json"\n'
        "/usr/bin/jq -e '\n"
        '  .session_state == "finalized"\n'
        '  and .pin_relation == "physical_ahead"\n'
        '  and .refusal_code == "calibration_ledger_head_mismatch"\n'
        '  and .terminal_head_pin_candidate != null\n'
        "' \"$G2A_TRANSCRIPT_ROOT/g2a-post-bracket-terminal-boundary.json\"\n"
        'echo "$(timestamp) g2a_boundary_stopped=physical_ahead" '
        '>> "$G2A_OPERATOR_LOG_ROOT/window-chain.log"\n'
        "```\n"
        f"{G2A_END_MARKER}\n"
    )


def render_generated_region(runbook: str) -> str:
    """Render the sole G2-b chain variant from the complete runbook chain bytes."""

    chain = extract_runbook_chain(runbook)
    chain = _replace_once(
        chain,
        '  --launch-manifest "$LAUNCH_MANIFEST" \\\n'
        "  --lifecycle-event start\n",
        '  --launch-manifest "$LAUNCH_MANIFEST" \\\n'
        "  --lifecycle-event start \\\n"
        '  --step6-confirmation-table "$STEP6_CONFIRMATION_TABLE" \\\n'
        '  --expected-confirmation-digest "$EXPECTED_CONFIRMATION_DIGEST"\n',
        label="start confirmation pair",
    )
    chain = _replace_once(
        chain,
        'run_stage_list "$WINDOW_PLAN_ROOT/before_midpoint_stages.txt"\n',
        "# G2-b delta: stop the authentic first stage after block 1, then preserve\n"
        "# the governed chain's post-science bracket path.  The second-terminal\n"
        "# signal card below supplies SIGINT immediately after b01 A2 succeeds.\n"
        "set +e\n"
        'run_stage_list "$WINDOW_PLAN_ROOT/before_midpoint_stages.txt"\n'
        "SCIENCE_RC=$?\n"
        "set -e\n"
        'test "$SCIENCE_RC" = 130\n',
        label="before-midpoint stage call",
    )
    chain = _replace_once(
        chain,
        'run_stage_list "$WINDOW_PLAN_ROOT/after_midpoint_stages.txt"\n',
        "# G2-b deliberately collects no after-midpoint science stage.\n",
        label="after-midpoint stage call",
    )
    chain = _replace_once(
        chain,
        '"$PY" "$REPO/scripts/launch_window.py" \\\n'
        '  --pack-root "$PACK_ROOT" \\\n'
        '  --arm-receipt "$ARM_RECEIPT" \\\n'
        '  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \\\n'
        '  --launch-manifest "$LAUNCH_MANIFEST" \\\n'
        "  --lifecycle-event completion\n"
        'echo "$(timestamp) measurement_complete" >> "$OPERATOR_LOG_ROOT/window-chain.log"\n',
        "# R-6 ratified boundary: post finalization emitted the physical terminal\n"
        "# candidate.  Record it and STOP; do not advance the tracked pin and do\n"
        "# not emit launch completion during this night.\n"
        '"$PY" "$REPO/scripts/recover_calibration_ledger.py" \\\n'
        '  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \\\n'
        '  session-status --session-id "$BRACKET_SESSION_ID" --plan "$FROZEN_PLAN" \\\n'
        '  > "$TRANSCRIPT_ROOT/post-bracket-terminal-boundary.json"\n'
        "/usr/bin/jq -e '\n"
        "  .session_state == \"finalized\"\n"
        "  and .pin_relation == \"physical_ahead\"\n"
        "  and .refusal_code == \"calibration_ledger_head_mismatch\"\n"
        "  and .terminal_head_pin_candidate != null\n"
        "' \"$TRANSCRIPT_ROOT/post-bracket-terminal-boundary.json\"\n"
        'echo "$(timestamp) g2_boundary_stopped=physical_ahead" >> "$OPERATOR_LOG_ROOT/window-chain.log"\n',
        label="post-bracket completion tail",
    )
    return (
        f"{BEGIN_MARKER}\n"
        "<!-- GENERATED by scripts/gen_g2_phase_d.py from the pinned runbook chain. -->\n"
        f"{chain}"
        f"{END_MARKER}\n"
    )


def replace_marked_region(
    runsheet: str, generated: str, *, begin_marker: str, end_marker: str
) -> str:
    start = runsheet.find(begin_marker)
    end = runsheet.find(end_marker)
    if start < 0 or end < 0 or end < start:
        raise ValueError("runsheet generated-region markers are missing or out of order")
    end += len(end_marker)
    if end < len(runsheet) and runsheet[end] == "\n":
        end += 1
    return runsheet[:start] + generated + runsheet[end:]


def replace_generated_region(runsheet: str, generated: str) -> str:
    return replace_marked_region(
        runsheet,
        generated,
        begin_marker=BEGIN_MARKER,
        end_marker=END_MARKER,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="refuse instead of updating on drift"
    )
    parser.add_argument(
        "--emit-chain", type=Path, metavar="OUT", help="write the G2-a night chain"
    )
    parser.add_argument(
        "--night-date", metavar="YYYYMMDD", help="date substituted into G2-a exports"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.emit_chain is not None:
        if args.night_date is None:
            raise SystemExit("--emit-chain requires --night-date YYYYMMDD")
        emit_g2a_night_chain(args.emit_chain, args.night_date)
        print(f"emitted {args.emit_chain}")
        return 0
    if args.night_date is not None:
        raise SystemExit("--night-date is only valid with --emit-chain")
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
    runsheet = RUNSHEET_PATH.read_text(encoding="utf-8")
    g2a_generated = render_g2a_generated_region(runbook)
    expected = replace_marked_region(
        runsheet,
        g2a_generated,
        begin_marker=G2A_BEGIN_MARKER,
        end_marker=G2A_END_MARKER,
    )
    expected = replace_generated_region(expected, render_generated_region(runbook))
    if args.check:
        if runsheet != expected:
            print(f"FAIL generated Phase D drift: {RUNSHEET_PATH.relative_to(REPO_ROOT)}")
            return 1
        print("PASS generated Phase D matches pinned runbook bytes")
        return 0
    if runsheet != expected:
        RUNSHEET_PATH.write_text(expected, encoding="utf-8")
        print(f"updated {RUNSHEET_PATH.relative_to(REPO_ROOT)}")
    else:
        print(f"unchanged {RUNSHEET_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
