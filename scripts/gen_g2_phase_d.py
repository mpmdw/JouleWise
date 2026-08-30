#!/usr/bin/env python3
"""Generate the G2-b governed-chain region from the pinned window runbook."""

from __future__ import annotations

import argparse
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

# These are the magistrate-pinned source anchors.  Validation is deliberately
# line-and-byte exact; a moved or edited anchor must be reviewed and re-pinned.
PINNED_ANCHORS = {
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


def replace_generated_region(runsheet: str, generated: str) -> str:
    start = runsheet.find(BEGIN_MARKER)
    end = runsheet.find(END_MARKER)
    if start < 0 or end < 0 or end < start:
        raise ValueError("runsheet generated-region markers are missing or out of order")
    end += len(END_MARKER)
    if end < len(runsheet) and runsheet[end] == "\n":
        end += 1
    return runsheet[:start] + generated + runsheet[end:]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="refuse instead of updating on drift"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    runbook = RUNBOOK_PATH.read_text(encoding="utf-8")
    runsheet = RUNSHEET_PATH.read_text(encoding="utf-8")
    generated = render_generated_region(runbook)
    expected = replace_generated_region(runsheet, generated)
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
