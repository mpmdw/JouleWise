#!/usr/bin/env python3
"""Generate G2-a/G2-b governed-chain regions from the pinned window runbook."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shlex
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNBOOK_PATH = REPO_ROOT / "docs/phase_2/window_runbook.md"
RUNSHEET_PATH = (
    REPO_ROOT
    / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

G2A_CAMPAIGN_POLICY_PATH = Path("configs/campaign_policies/quiet_mac_p2_g2a_b3.json")

# Code-defined fixed work: 9 settles, 8 stage countdowns, 24 captures at
# idle=75, warmup dwell=5, post dwell=1 (producer + block-3 policy), two
# 59-pulse captures (3*BASELINE_S + 3*(1+1.5) + pulse_schedule(59)[-1][1]
# = 196.703125), and two calibration display/countdown pauses (20+5).
# Variable work (model load, warmup, prefill, 512-token decode, cooldown,
# admission, reduction, custody) is sized from the runsheet's documented
# historical cadence, never from bundle timing: about 148 s per member at the
# then idle of 30 s ("preparation budget" in SHAKEDOWN-G2-RUNSHEET.md), so
# about 148 - 30 - 5 - 1 = 112 s of non-idle work per member. Allowance:
# small member 240 s (2 x 112, rounded up), large member 300 s (bigger load,
# slower decode). Per stage 180 s (input/admission/order/census 120 + final
# reduction/logging 60). Shared 1440 s: reservation 120 + two writers' custody
# passes 2*(WRITER_CUSTODY_PASSES+1)*120 + terminal custody, input
# authentication and summary 3*120. Calibration readiness, allocation,
# overshoot and pin custody 420 s.
# Delayed retries: 4*(300 + 75 + 30) = 1620 s (backoff + member idle + guards
# and slice overhead). Block-3 ruling budgets four retries: the two rejected
# first attempts among 13 block-2 members, scaled to 24 and rounded up. Why
# 300 s: one sampler runs from attempt 1 through the measured window, and the
# active v3 clock anchor caps its effective bound (anchor half-width + wall-
# minus-monotonic span) at 5 ms. Block-2 members drifted about 3.2 ppm with
# half-widths up to 2.31 ms, and an idle attempt took about 104 s. The
# estimated longest retried stream (Qwen3-8B at 4096 tokens, decode assumed
# >= 5 tokens/s, guards near their timeouts; an estimate, not an enforced
# bound) is 2*104 + 300 + 45 + 20 + 103.2 + 6 = 683 s, bound about 4.5 ms; a
# 600 s wait (983 s) would exceed 5 ms. Drift tolerance at 300 s: about 3.9
# ppm. A voided member is refused, never admitted
# (tests/test_controller_retry_backoff.py).
# ceil(7947.40625 + 20*240 + 4*300 + 8*180 + 1440 + 420 + 1620) = 18868 seconds.
# Orchestrator ruling (block-2 design record 00, item 7): a first sizing from
# code worst cases (10 and 5 tokens/s decode, the 300 s cooldown cap and an idle
# retry on EVERY member) gave 33556 s and would have held the machine about
# nine hours for a chain of about three. An overrun is still refused by the
# driver's window expiry; the harvest then returns RECOVER.
SMALL_MEMBER_ALLOWANCE_S = 240
LARGE_MEMBER_ALLOWANCE_S = 300
IDLE_RETRY_ALLOWANCE_COUNT = 4


def programmed_span_s():
    """Size from prospective producer/policy/protocol code, without telemetry."""
    from scripts import generate_g2a_probe_inputs as producer
    from joulewise.powermetrics_fiducial import (
        BASELINE_S, WARMUP_PULSE_COUNT, PULSE_DURATION_S, PULSE_COUNT, pulse_schedule,
    )
    from joulewise.night_agent_install import WRITER_CUSTODY_PASSES

    panel = producer.load_model_panel(REPO_ROOT / "configs/model_panels/qwen3_4bit.json")
    rung = {"prefill_tokens": max(producer.PREFILL_LENGTHS), "prompt_text": "sizing only",
            "prompt_token_ids": [0], "prompt_token_ids_sha256": "0" * 64,
            "prompt_text_utf8_sha256": "0" * 64}
    configs = {role: producer._config_for(role=role, entry=panel.get(producer.EXPECTED_MODEL_IDS[role]),
        rung=rung, run_id="sizing", panel_sha="0" * 64) for role in producer.MODEL_ROLES}
    policy = json.loads((REPO_ROOT / G2A_CAMPAIGN_POLICY_PATH).read_bytes())
    rungs = len(producer.PREFILL_LENGTHS)
    capture = 3 * BASELINE_S + WARMUP_PULSE_COUNT * (PULSE_DURATION_S + 1.5) + pulse_schedule(PULSE_COUNT)[-1][1]
    member_dwells = sum(count * (configs[role]["sampling"]["idle_seconds"]
        + configs[role]["sampling"]["warmup_seconds"] + policy["post_window_sampling_dwell_s"])
        for role, count in (("small", 5), ("large", 1)))
    fixed = (1 + 2 * rungs) * 600 + 2 * rungs * 20 + rungs * member_dwells + 2 * capture + 2 * (20 + 5)
    retry_allowance = IDLE_RETRY_ALLOWANCE_COUNT * (
        policy["idle_admission"].get("retry_backoff_s", 0)
        + max(config["sampling"]["idle_seconds"] for config in configs.values()) + 30
    )
    return math.ceil(fixed + 5*rungs*SMALL_MEMBER_ALLOWANCE_S + rungs*LARGE_MEMBER_ALLOWANCE_S + 2*rungs*180
                     + 120 + 2*(WRITER_CUSTODY_PASSES+1)*120 + 3*120 + 420 + retry_allowance)


NIGHT_PROGRAMMED_SPAN_S = programmed_span_s()


def integrated_g2a_chain(chain: str, *, measurement_root: Path, g2a_root: Path,
                         night_root: Path, plan_id: str) -> str:
    """Specialize reviewed shell bytes and put inspection before mutation."""
    # Rename the runsheet window id first, then pin the explicit paths: a real
    # window root contains the plan id, which begins with the runsheet id, so
    # renaming after pinning would rewrite the root a second time.
    old_id = re.search(r"^export G2A_WINDOW_ID=(.+)$", chain, re.MULTILINE)[1]
    chain = re.sub(r"^export (G2A_[A-Z_]+)=(.*)$",
        lambda row: ('export ' + row[1] + '=' + shlex.quote(row[2].replace(old_id, plan_id))
                     if old_id in row[2] else row[0]), chain, flags=re.MULTILINE)
    values = {"CALIBRATION_LEDGER": measurement_root / "runs/calibration_observation_ledger.jsonl",
              "LEDGER_HEAD_PIN": measurement_root / "configs/calibration/calibration_ledger_head.json",
              "POLICY": measurement_root / G2A_CAMPAIGN_POLICY_PATH,
              "G2A_ROOT": g2a_root}
    for name, value in values.items():
        chain, count = re.subn(r"^export " + name + r"=.*$",
                              lambda _: "export " + name + "=" + shlex.quote(str(value)),
                              chain, flags=re.MULTILINE)
        if count != 1:
            raise ValueError(f"{name}: expected one source export")
    # The array is the single reservation argv used by inspection and execution.
    start = chain.index('"$PY" "$REPO/scripts/reserve_calibration_window_bracket.py" \\\n')
    end = chain.index("  --execute\n", start) + len("  --execute\n")
    argv = chain[start:end].removesuffix("  --execute\n")
    header = (
        f"export NIGHT_PROGRAMMED_SPAN_S={NIGHT_PROGRAMMED_SPAN_S}\n"
        "export NIGHT_CHAIN_INTERFACE=g2a-reservation-v1\n"
        f"export JOULEWISE_NIGHT_PLAN_ID={shlex.quote(plan_id)}\n"
        f"export JOULEWISE_CALIBRATION_REFUSAL_PATH={shlex.quote(str(night_root / 'night/calibration-refusal.json'))}\n"
        "export JOULEWISE_NIGHT_CUSTODY_BUDGET_S=120\n"
        # Opt in only this diagnostic chain to the authenticated ordinary pre
        # slot attachment. Legacy/derivation callers retain the C-2 refusal.
        'export JOULEWISE_G2A_PRE_BRACKET_PLAN="$G2A_FROZEN_PLAN"\n'
        f"export G2A_PLAN_ID={shlex.quote('plan-' + plan_id + '-g2a-probe-v1')}\n"
        'G2A_PLAN_SHA256="$(/usr/bin/shasum -a 256 "$G2A_FROZEN_PLAN" | /usr/bin/awk \'{print $1}\')"\n'
        "reservation_argv=(\n" + argv + "  --custody-budget-s 120 --pre-reserve-strict\n)\n"
        'if [[ "${NIGHT_RESERVATION_ARGV_ONLY:-0}" = 1 ]]; then\n'
        '  printf \'%s\\0\' "${reservation_argv[@]}" --verify-only\n  exit 0\nfi\n'
        'if [[ "${NIGHT_VERIFY_ONLY:-0}" = 1 ]]; then\n'
        '  exec "${reservation_argv[@]}" --verify-only\nfi\n'
    )
    chain = chain[:start] + '"${reservation_argv[@]}" --execute\n' + chain[end:]
    chain = re.sub(r"^G2A_PLAN_(?:ID|SHA256)=.*\n", "", chain, flags=re.MULTILINE)
    # All exports are non-mutating; the first mkdir remains after both branches.
    first_mutation = chain.index('/bin/mkdir -p "$G2A_RUNS_ROOT"')
    return chain[:first_mutation] + header + chain[first_mutation:]


def authenticated_screen_source(source: str) -> str:
    """Refresh source literals through the writer's authenticated derivation.

    Used on both source documents before rendering, so --check detects a stale
    source even when its generated copy agrees with it.
    """
    from scripts.validate_powermetrics_fiducial import (
        DEFAULT_ACCEPTANCE_BOUND_PATH,
        _derive_preflight_systematic_screen_s,
    )

    record: dict = {}
    screen = _derive_preflight_systematic_screen_s(preflight_record=record)
    source, count = re.subn(
        r"^((?:export )?PRE_CAL_FIDUCIAL_MAX_S=)[^\n]+$",
        lambda match: match[1] + str(screen), source, flags=re.MULTILINE,
    )
    if count == 0:
        raise ValueError("pre-calibration screen source literal is missing")
    acceptance_sha = hashlib.sha256(DEFAULT_ACCEPTANCE_BOUND_PATH.read_bytes()).hexdigest()
    source = re.sub(
        r"^# acceptance artifact [^\n]+$",
        f"# acceptance artifact {record['acceptance_id']} (sha {acceptance_sha[:8]}...).",
        source, flags=re.MULTILINE,
    )
    return source
BEGIN_MARKER = "<!-- BEGIN GENERATED: g2-phase-d-governed-chain -->"
END_MARKER = "<!-- END GENERATED: g2-phase-d-governed-chain -->"
G2A_BEGIN_MARKER = "<!-- BEGIN GENERATED: g2a-governed-bracket -->"
G2A_END_MARKER = "<!-- END GENERATED: g2a-governed-bracket -->"

# These are the magistrate-pinned source anchors.  Validation is deliberately
# line-and-byte exact; a moved or edited anchor must be reviewed and re-pinned.
PINNED_ANCHORS = {
    1367: ".venv/bin/python scripts/recover_calibration_ledger.py readiness \\",
    1372: ".venv/bin/python scripts/reserve_calibration_window_bracket.py \\",
    1388: "  --execute",
    1476: "# First executable action: consume the inherited one-use FD and mint start",
    1501: 'NEG8_DRIFT_BOUND="$BOUND_RUNS_ROOT/neg8-drift-bound.json"',
    1516: '  /bin/sleep "$SETTLE_S"',
    1596: "  settle || return $?",
    1613: "run_stage_list() {",
    1623: 'cd "$REPO"',
    1653: 'screen_pre_calibration "$PRE_CAL_CUSTODY"',
    1687: 'echo "$(timestamp) measurement_complete" >> "$OPERATOR_LOG_ROOT/window-chain.log"',
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

    if heading not in source:
        raise ValueError(f"runsheet section is missing: {heading}")
    start = source.index(heading)
    following = re.search(r"^## ", source[start + len(heading) :], re.MULTILINE)
    end = len(source) if following is None else start + len(heading) + following.start()
    return start, end


def _line_number(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def inventory_g2a_shell_blocks(runsheet: str) -> list[tuple[int, int, str]]:
    """Inventory shell fences in the plan-derived-variable and G2-a sections.

    The inclusive line numbers deliberately cover the markdown fence lines:
    they are the stable source anchors recorded in an emitted chain.
    """

    sections = (
        _section_bounds(runsheet, "## Plan-derived measurement variables"),
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
    runsheet = authenticated_screen_source(runsheet)
    blocks = inventory_g2a_shell_blocks(runsheet)
    expected_ranges = [(1550, 1614), (328, 351), (374, 385), (389, 564), (575, 587)]
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


def emit_g2a_night_chain(output_path: Path, night_date: str, *, measurement_root: Path | None = None,
                         g2a_root: Path | None = None, night_root: Path | None = None,
                         plan_id: str | None = None) -> None:
    """Write an executable chain and its GNU-format SHA-256 sidecar."""

    chain = render_g2a_night_chain(RUNSHEET_PATH.read_text(encoding="utf-8"), night_date)
    chain = integrated_g2a_chain(chain,
        measurement_root=(measurement_root or Path(f"/Users/edr/night-custody/measurement/JouleWise-measurement-g2a-{night_date}")).resolve(),
        g2a_root=(g2a_root or Path(f"/Users/edr/JouleWise-shakedown-g2/g2-a-{night_date}")).resolve(),
        night_root=(night_root or output_path.absolute().parent).resolve(),
        plan_id=plan_id or f"d117-g2a-prefill-probe-{night_date}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(chain, encoding="utf-8")
    output_path.chmod(0o755)
    digest = hashlib.sha256(chain.encode("utf-8")).hexdigest()
    sidecar = output_path.with_name(f"{output_path.name}.sha256")
    sidecar.write_text(f"{digest}  {output_path.name}\n", encoding="utf-8")


def author_g2a_window(args, *, now=time.time):
    from joulewise.night_gate import NightPlan, D166_REGISTRATION_PATH
    from joulewise.night_plan_writer import write_night_plan
    from scripts.run_night import schedule

    for name in ("t0_epoch_s", "window_max_s", "plan_id", "measurement_root",
                 "measurement_head", "night_root", "g2a_root"):
        if getattr(args, name) is None:
            raise ValueError(f"--new-g2a-window requires --{name.replace('_', '-')}")
    roots = [args.measurement_root, args.night_root, args.g2a_root, args.new_g2a_window]
    if any(re.search(r"codex|claude|t3", str(value), re.IGNORECASE)
           for value in [args.plan_id, *roots]):
        raise ValueError("plan id and paths must not contain codex, claude or t3")
    if any(not path.is_absolute() for path in roots):
        raise ValueError("window paths must be absolute")
    if any(re.search(r"codex|claude|t3", str(path.resolve()), re.IGNORECASE) for path in roots):
        raise ValueError("resolved paths must not contain codex, claude or t3")
    measurement = args.measurement_root.resolve()
    parent = Path("/Users/edr/night-custody/measurement")
    if parent not in measurement.parents:
        raise ValueError("measurement root must be inside /Users/edr/night-custody/measurement/")
    authored = now()
    if args.t0_epoch_s % 60 or args.t0_epoch_s < authored + 2400:
        raise ValueError("t0 must be minute-aligned and at least 2400 s ahead")
    if args.window_max_s < NIGHT_PROGRAMMED_SPAN_S + 900:
        raise ValueError("window_max_s must cover NIGHT_PROGRAMMED_SPAN_S + 900")
    night = args.night_root.resolve()
    output = args.new_g2a_window.resolve()
    # The plan may be staged outside the night root: the arm recipe publishes it
    # into custody (os.replace to <night root>/night_plan.json) only after the
    # arm notice is accepted, as the Revision 6 arm does.
    if output.name != "night_plan.json":
        raise ValueError("plan output must be named night_plan.json")
    chain = night / "chain.zsh"
    sidecar = night / "chain.zsh.sha256"
    if any(path.exists() for path in (output, chain, sidecar)):
        raise ValueError("window outputs already exist")
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
                          check=True, capture_output=True, text=True).stdout.strip()
    plan = NightPlan(plan_id=args.plan_id, receipt_class="DIAGNOSTIC_NO_PACK",
        t0_epoch_s=args.t0_epoch_s, window_max_s=args.window_max_s, authored_epoch_s=authored,
        repo_head=head, measurement_root=str(measurement), measurement_head=args.measurement_head,
        chain_path=str(chain), chain_sha256_path=str(sidecar), custody_root=str(night),
        registration_path=D166_REGISTRATION_PATH)
    result = schedule(plan)
    result.update(stand_down_epoch_s=plan.t0_epoch_s - 480,
        latest_chain_start_epoch_s=plan.t0_epoch_s + plan.window_max_s - NIGHT_PROGRAMMED_SPAN_S,
        window_end_epoch_s=plan.t0_epoch_s + plan.window_max_s,
        harvest_open_epoch_s=plan.t0_epoch_s + plan.window_max_s + 300)
    # Validate all coordinates and scheduling before publishing any output.
    from joulewise.night_plan_writer import night_plan_json_bytes
    night_plan_json_bytes(plan)
    date = datetime.fromtimestamp(plan.t0_epoch_s, timezone.utc).strftime("%Y%m%d")
    emit_g2a_night_chain(chain, date, measurement_root=measurement,
                         g2a_root=args.g2a_root.resolve(), night_root=night, plan_id=args.plan_id)
    write_night_plan(output, plan)
    print(json.dumps(result, sort_keys=True))
    print(f"plan={output} chain={chain} sha256={sidecar}")
    return plan


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


def render_generated_region(runbook: str, *, v5_references: bool = False) -> str:
    """Render G2-b, retaining the historical projection unless v5 is requested.

    Prospective v5 callers must opt in: pinned Markdown and historical chains
    continue to authenticate the original 30-second reference paths.
    """

    from scripts.run_campaign import MAX_BLOCKS_REACHED_RC

    chain = extract_runbook_chain(runbook)
    if v5_references:
        for name, directory in (
            ("REF_ROOT", "window_references"),
            ("BOUND_CONFIG_ROOT", "neg8_reference_corpus"),
        ):
            chain = _replace_once(
                chain,
                f'{name}="$REPO/configs/campaigns/{directory}"\n',
                f'{name}="$REPO/configs/campaigns/{directory}_v5"\n',
                label=f"v5 {name}",
            )
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
        "# G2-b: one complete A/B/B/A block, stopped by the controller between\n"
        "# members. G2B_SHAKEDOWN authorization requires --max-blocks and binds\n"
        "# permitted_blocks=1; no operator signal.\n"
        "# Dispatch only the first frozen science stage, preserving the bracket tail.\n"
        "SCIENCE_RC=2\n"
        "while IFS= read -r stage; do\n"
        '  [ -z "$stage" ] && continue\n'
        '  [[ "$stage" = \\#* ]] && continue\n'
        "  set +e\n"
        '  run_stage "$RUNS_ROOT" "$CLAIM_LOG" "$REPO/$stage" "$PRE_CAL_CUSTODY" "$stage" --max-blocks 1\n'
        "  SCIENCE_RC=$?\n"
        "  set -e\n"
        "  break\n"
        'done < "$WINDOW_PLAN_ROOT/before_midpoint_stages.txt"\n'
        f'test "$SCIENCE_RC" = {MAX_BLOCKS_REACHED_RC}\n',
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
    parser.add_argument("--new-g2a-window", type=Path, metavar="PLAN")
    parser.add_argument("--t0-epoch-s", type=int)
    parser.add_argument("--window-max-s", type=int)
    parser.add_argument("--plan-id")
    parser.add_argument("--measurement-root", type=Path)
    parser.add_argument("--measurement-head")
    parser.add_argument("--night-root", type=Path)
    parser.add_argument("--g2a-root", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.new_g2a_window is not None:
        if args.emit_chain is not None or args.check or args.night_date is not None:
            raise SystemExit("--new-g2a-window cannot combine with --emit-chain, --check or --night-date")
        try:
            author_g2a_window(args)
        except (ValueError, OSError, subprocess.SubprocessError) as error:
            print(f"FAIL {error}", file=sys.stderr)
            return 1
        return 0
    if args.emit_chain is not None:
        if args.night_date is None:
            raise SystemExit("--emit-chain requires --night-date YYYYMMDD")
        emit_g2a_night_chain(args.emit_chain, args.night_date,
            measurement_root=args.measurement_root, g2a_root=args.g2a_root,
            night_root=args.night_root, plan_id=args.plan_id)
        print(f"emitted {args.emit_chain}")
        return 0
    if args.night_date is not None:
        raise SystemExit("--night-date is only valid with --emit-chain")
    runbook_original = RUNBOOK_PATH.read_text(encoding="utf-8")
    runbook = authenticated_screen_source(runbook_original)
    runsheet = RUNSHEET_PATH.read_text(encoding="utf-8")
    refreshed_runsheet = authenticated_screen_source(runsheet)
    g2a_generated = render_g2a_generated_region(runbook)
    expected = replace_marked_region(
        refreshed_runsheet,
        g2a_generated,
        begin_marker=G2A_BEGIN_MARKER,
        end_marker=G2A_END_MARKER,
    )
    expected = replace_generated_region(expected, render_generated_region(runbook))
    if args.check:
        if runbook != runbook_original:
            print(f"FAIL acceptance-derived screen drift: {RUNBOOK_PATH.relative_to(REPO_ROOT)}")
            return 1
        # Check executable source fences as well as the generated bracket bytes.
        try:
            render_g2a_night_chain(runsheet, "20260830")
        except ValueError as exc:
            print(f"FAIL {exc}")
            return 1
        if runsheet != expected:
            print(f"FAIL generated Phase D drift: {RUNSHEET_PATH.relative_to(REPO_ROOT)}")
            return 1
        print("PASS generated Phase D matches pinned runbook bytes")
        return 0
    if runbook != runbook_original:
        RUNBOOK_PATH.write_text(runbook, encoding="utf-8")
        print(f"updated {RUNBOOK_PATH.relative_to(REPO_ROOT)}")
    if runsheet != expected:
        RUNSHEET_PATH.write_text(expected, encoding="utf-8")
        print(f"updated {RUNSHEET_PATH.relative_to(REPO_ROOT)}")
    else:
        print(f"unchanged {RUNSHEET_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    raise SystemExit(main())
