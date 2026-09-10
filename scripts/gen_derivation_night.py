#!/usr/bin/env python3
"""Emit the plan-pinned wrapper that launches one derivation night.

The night driver hands a chain exactly four variables and no argv
(``scripts/run_night.py:414-444``: ``NIGHT_PLAN_ID``, ``MEASUREMENT_ROOT``,
``MEASUREMENT_HEAD``, ``PY``), and it verifies the plan-pinned chain's bytes
against a ``shasum``-form sidecar before launching it
(``scripts/run_night.py:1576-1610``).  The tracked derivation chain
``scripts/night_chains/calibration_derivation_only.zsh`` needs thirteen more
variables and twenty-four per-slot binding arguments, so a night is armed by
pinning a *wrapper* emitted here: the wrapper carries the night's whole
environment as literal ``export`` lines, re-derives and cross-checks the frozen
calibration plan, verifies the tracked chain's bytes, and ``exec``s the tracked
chain with the per-slot bindings as argv.

``exec`` rather than ``source`` is load-bearing: the tracked chain derives its
repository root from its own path (``calibration_derivation_only.zsh:40-41``,
``cd "${0:A:h:h:h}"``), so it must run as ``$0`` at its in-clone path.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.night_gate import NightPlan, PlanError  # noqa: E402

RUNSHEET_PATH = (
    REPO_ROOT / "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md"
)
BEGIN_MARKER = "<!-- BEGIN GENERATED: derivation-night-wrapper -->"
END_MARKER = "<!-- END GENERATED: derivation-night-wrapper -->"

TRACKED_CHAIN_RELPATH = "scripts/night_chains/calibration_derivation_only.zsh"
TRACKED_CHAIN_PATH = REPO_ROOT / TRACKED_CHAIN_RELPATH

# joulewise/night_gate.py:42 censuses `pgrep -lf "codex|claude|t3"` every 30 s
# and aborts the night on any hit, so no literal this wrapper bakes into a
# command line may contain one of these substrings.
CENSUS_SUBSTRINGS = ("codex", "claude", "t3")

# scripts/run_night.py:51,54-55 — the courier allowance and the dead-man minute.
COURIER_DEADLINE_S = 300
DEADMAN_HOUR = 7
DEADMAN_MINUTE = 0

# The pre-registered derivation night is twelve slots (cold-gate ruling 46 §R-c).
PRE_REGISTERED_SLOT_COUNT = 12

# Chain defaults (calibration_derivation_only.zsh:60-65) pinned explicitly: the
# driver hands the chain `os.environ.copy()`, so an inherited SETTLE_S, SLEEP or
# DATE from the arming operator's shell would silently retime the night.
DEFAULT_SETTLE_S = 600
DEFAULT_SLOT_CADENCE_S = 600
DEFAULT_SLOT_CAPTURE_BUDGET_S = 480


class GenerationRefusal(Exception):
    """Refuse to emit a wrapper that could not run, or could run wrongly."""


def _quote(value: str) -> str:
    """Return a zsh single-quoted literal, refusing anything unquotable."""

    if "'" in value:
        raise GenerationRefusal(f"literal contains a single quote: {value!r}")
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in value):
        raise GenerationRefusal(f"literal contains a control character: {value!r}")
    return f"'{value}'"


def _census_clean(field: str, value: str) -> str:
    lowered = value.lower()
    for substring in CENSUS_SUBSTRINGS:
        if substring in lowered:
            raise GenerationRefusal(
                f"{field} contains the census substring {substring!r}: {value!r}; "
                "the night's own agent census would abort the night"
            )
    return value


def _next_deadman_epoch(t0_epoch_s: float) -> float:
    """Mirror ``scripts/run_night.py:947-955``: the next local 07:00 after t0."""

    t0 = datetime.fromtimestamp(t0_epoch_s)
    deadman = t0.replace(
        hour=DEADMAN_HOUR, minute=DEADMAN_MINUTE, second=0, microsecond=0
    )
    if deadman <= t0:
        deadman += timedelta(days=1)
    return deadman.timestamp()


def slot_names(slot_count: int) -> list[str]:
    return [f"d{index:02d}" for index in range(1, slot_count + 1)]


@dataclass(frozen=True)
class WrapperSpec:
    """Every literal the emitted wrapper carries.  Rendering is a pure function."""

    plan_id: str
    measurement_root: str
    measurement_head: str
    session_id: str
    window_id: str
    frozen_plan: str
    frozen_plan_id: str
    frozen_plan_sha256: str
    evidence_root_id: str
    runs_root: str
    window_custody_root: str
    calibration_ledger: str
    ledger_head_pin: str
    identity_epoch_json: str
    t1_bindings_json: str
    window_end_epoch_s: int
    slot_count: int
    chain_source_sidecar: str
    chain_sha256: str
    settle_s: int = DEFAULT_SETTLE_S
    slot_cadence_s: int = DEFAULT_SLOT_CADENCE_S
    slot_capture_budget_s: int = DEFAULT_SLOT_CAPTURE_BUDGET_S


def render_wrapper(spec: WrapperSpec) -> str:
    """Render the wrapper deterministically: same spec, same bytes, always."""

    exports = [
        # The thirteen `:?required` variables of the tracked chain
        # (calibration_derivation_only.zsh:43-55), in that order.
        ("SESSION_ID", spec.session_id),
        ("WINDOW_ID", spec.window_id),
        ("PLAN_ID", spec.frozen_plan_id),
        ("PLAN_SHA256", spec.frozen_plan_sha256),
        ("PLAN", spec.frozen_plan),
        ("EVIDENCE_ROOT_ID", spec.evidence_root_id),
        ("RUNS_ROOT", spec.runs_root),
        ("WINDOW_CUSTODY_ROOT", spec.window_custody_root),
        ("CALIBRATION_LEDGER", spec.calibration_ledger),
        ("LEDGER_HEAD_PIN", spec.ledger_head_pin),
        ("IDENTITY_EPOCH_JSON", spec.identity_epoch_json),
        ("T1_BINDINGS_JSON", spec.t1_bindings_json),
        ("WINDOW_END_EPOCH_S", str(spec.window_end_epoch_s)),
        # Chain knobs pinned rather than defaulted or inherited.
        ("SLOT_COUNT", str(spec.slot_count)),
        ("SETTLE_S", str(spec.settle_s)),
        ("SLOT_CADENCE_S", str(spec.slot_cadence_s)),
        ("SLOT_CAPTURE_BUDGET_S", str(spec.slot_capture_budget_s)),
        ("SLEEP", "/bin/sleep"),
        ("DATE", "/bin/date"),
    ]
    binding_lines: list[str] = []
    for slot in slot_names(spec.slot_count):
        attempt_id = f"{spec.session_id}-{slot}"
        locator = f"{spec.runs_root}/instrument_validation/{attempt_id}"
        binding_lines.append(f"  --slot-attempt-id {_quote(attempt_id)} \\")
        binding_lines.append(f"  --slot-custody-locator {_quote(locator)} \\")
    # The final binding closes the argv; nothing follows it.
    binding_lines[-1] = binding_lines[-1][: -len(" \\")]

    lines = [
        "#!/bin/zsh",
        "# GENERATED by scripts/gen_derivation_night.py — do not edit; re-emit.",
        f"# Derivation-night wrapper for night plan {spec.plan_id}.",
        "#",
        "# The driver supplies NIGHT_PLAN_ID, MEASUREMENT_ROOT, MEASUREMENT_HEAD and",
        "# PY and no argv (scripts/run_night.py:430-444).  This wrapper supplies the",
        "# thirteen chain variables as literals frozen with the plan, verifies the",
        "# tracked chain's bytes, and execs it with the per-slot bindings as argv.",
        "set -euo pipefail",
        "",
        "route_refuse() { printf 'FAIL %s\\n' \"$1\" >&2; exit 1; }",
        "",
        "# Routing preamble, mirroring the reviewed G2-a source",
        "# (SHAKEDOWN-G2-RUNSHEET.md 'Emitted routing and common variables').",
        "[ -n \"${MEASUREMENT_ROOT:-}\" ] || route_refuse 'measurement_root is required'",
        "case \"$MEASUREMENT_ROOT\" in",
        "  /*) ;;",
        "  *) route_refuse 'measurement_root must be an absolute path' ;;",
        "esac",
        "[[ ! \"$MEASUREMENT_ROOT\" =~ [[:cntrl:]] ]] || "
        "route_refuse 'measurement_root contains control characters'",
        "[[ \"${MEASUREMENT_HEAD:-}\" =~ ^[0-9a-f]{40}$ ]] || "
        "route_refuse 'measurement_head must be a full 40-character lowercase SHA-1'",
        "# This wrapper's literals were frozen against one plan; refuse any other.",
        f"[ \"${{NIGHT_PLAN_ID:-}}\" = {_quote(spec.plan_id)} ] || "
        "route_refuse 'night plan id does not match the wrapper'",
        f"[ \"$MEASUREMENT_ROOT\" = {_quote(spec.measurement_root)} ] || "
        "route_refuse 'measurement_root does not match the wrapper'",
        f"[ \"$MEASUREMENT_HEAD\" = {_quote(spec.measurement_head)} ] || "
        "route_refuse 'measurement_head does not match the wrapper'",
        "export GIT_OPTIONAL_LOCKS=0 PYTHONDONTWRITEBYTECODE=1",
        "observed_head=\"$(git -C \"$MEASUREMENT_ROOT\" rev-parse --verify HEAD 2>/dev/null)\" || "
        "route_refuse 'checkout HEAD cannot be read'",
        "[ \"$observed_head\" = \"$MEASUREMENT_HEAD\" ] || "
        "route_refuse 'checkout HEAD does not equal measurement_head'",
        "export MEASUREMENT_CHECKOUT=\"$MEASUREMENT_ROOT\"",
        "export REPO=\"$MEASUREMENT_ROOT\"",
        "export PY=\"$MEASUREMENT_ROOT/.venv/bin/python\"",
        "[ -x \"$PY\" ] || route_refuse 'measurement venv Python is missing or not executable'",
        "export PYTHONPATH=\"$MEASUREMENT_ROOT\"",
        "",
        "# The night's environment, frozen at arm time.",
    ]
    lines.extend(f"export {name}={_quote(value)}" for name, value in exports)
    lines.extend(
        [
            "",
            "# Authenticate the desk-produced inputs before any window time is spent.",
            'test -f "$PLAN"',
            'test -f "$IDENTITY_EPOCH_JSON"',
            'test -f "$T1_BINDINGS_JSON"',
            "# Re-derive the frozen plan's identity from its bytes, as the G2-a bracket",
            "# does (gen_g2_phase_d.py:250-252), and refuse a swapped plan file.",
            "observed_plan_id=\"$(/usr/bin/jq -er '.plan_id' \"$PLAN\")\"",
            '[ "$observed_plan_id" = "$PLAN_ID" ] || '
            "route_refuse 'frozen plan id does not equal the arm-time literal'",
            "observed_plan_sha256=\"$(/usr/bin/shasum -a 256 \"$PLAN\" | "
            "/usr/bin/awk '{print $1}')\"",
            '[ "$observed_plan_sha256" = "$PLAN_SHA256" ] || '
            "route_refuse 'frozen plan bytes do not equal the arm-time digest'",
            "",
            "# The plan pins THIS wrapper's digest; the wrapper pins the capturing",
            "# chain's, so the plan-pinned digest transitively covers the bytes that",
            "# actually capture.  The sidecar names the path relative to the clone.",
            f"( cd \"$REPO\" && /usr/bin/shasum -a 256 --status -c "
            f"{_quote(spec.chain_source_sidecar)} ) || "
            "route_refuse 'tracked derivation chain bytes do not match the arm-time digest'",
            "",
            "# exec, never source: the chain derives REPO from its own $0",
            "# (calibration_derivation_only.zsh:40-41), and its per-slot bindings are",
            '# its own "$@" (:155), forwarded verbatim to the reservation.',
            f"exec /bin/zsh \"$REPO/{TRACKED_CHAIN_RELPATH}\" \\",
        ]
    )
    lines.extend(binding_lines)
    return "\n".join(lines) + "\n"


def _sidecar_text(digest: str, name: str) -> str:
    """GNU ``shasum`` form, the only form the driver accepts (run_night.py:97)."""

    return f"{digest}  {name}\n"


def emit(spec: WrapperSpec, out_path: Path, *, chain_bytes: bytes) -> str:
    """Write the wrapper, its own sidecar, and the tracked-chain sidecar."""

    wrapper = render_wrapper(spec)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(wrapper, encoding="utf-8")
    out_path.chmod(0o755)
    digest = hashlib.sha256(wrapper.encode("utf-8")).hexdigest()
    out_path.with_name(f"{out_path.name}.sha256").write_text(
        _sidecar_text(digest, out_path.name), encoding="utf-8"
    )
    Path(spec.chain_source_sidecar).write_text(
        _sidecar_text(
            hashlib.sha256(chain_bytes).hexdigest(), TRACKED_CHAIN_RELPATH
        ),
        encoding="utf-8",
    )
    return digest


def _require_absolute(field: str, value: str) -> str:
    if not value.startswith("/"):
        raise GenerationRefusal(f"{field} must be an absolute path: {value!r}")
    return _census_clean(field, value)


def build_spec(args: argparse.Namespace) -> tuple[WrapperSpec, Path, bytes]:
    """Validate every input and resolve every literal, or refuse."""

    plan_path = Path(args.plan).expanduser()
    try:
        raw = json.loads(plan_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise GenerationRefusal(f"night plan is unreadable: {error}") from error
    try:
        plan = NightPlan.from_mapping(raw)
    except PlanError as error:
        raise GenerationRefusal(f"night plan is not an exact v2 plan: {error}") from error
    if plan.receipt_class == "TRANSACTION_PACK":
        raise GenerationRefusal(
            "a derivation night is DIAGNOSTIC_NO_PACK; this plan is a pack night"
        )

    slot_count = args.slot_count
    if slot_count != PRE_REGISTERED_SLOT_COUNT and not args.allow_slot_count:
        raise GenerationRefusal(
            f"slot count {slot_count} is not the pre-registered "
            f"{PRE_REGISTERED_SLOT_COUNT}; pass --allow-slot-count to override"
        )
    if slot_count < 1:
        raise GenerationRefusal("slot count must be positive")

    window_end_epoch_s = int(plan.t0_epoch_s + plan.window_max_s)
    deadman = _next_deadman_epoch(plan.t0_epoch_s)
    completion = plan.t0_epoch_s + plan.window_max_s + COURIER_DEADLINE_S
    if not completion < deadman:
        raise GenerationRefusal(
            "plan overruns the dead-man: t0 + window_max_s + "
            f"{COURIER_DEADLINE_S} = {completion:.0f} is not before the next "
            f"local 07:00 = {deadman:.0f}; move t0 earlier"
        )

    out_path = Path(args.out).expanduser() if args.out else Path(plan.chain_path)
    out_path = out_path.absolute()
    if str(out_path) != plan.chain_path:
        raise GenerationRefusal(
            f"--out {out_path} is not the plan's chain_path {plan.chain_path!r}"
        )
    expected_sidecar = f"{plan.chain_path}.sha256"
    if plan.chain_sha256_path != expected_sidecar:
        raise GenerationRefusal(
            f"plan chain_sha256_path {plan.chain_sha256_path!r} is not "
            f"{expected_sidecar!r}"
        )
    _require_absolute("out path", str(out_path))
    _census_clean("night custody root", plan.custody_root)
    _census_clean("session id", args.session_id)

    measurement_root = _require_absolute("measurement_root", plan.measurement_root)
    runs_root = args.runs_root or f"{plan.custody_root}/runs"
    ledger = args.ledger or f"{measurement_root}/runs/calibration_observation_ledger.jsonl"
    head_pin = (
        args.head_pin
        or f"{measurement_root}/configs/calibration/calibration_ledger_head.json"
    )

    frozen_plan_path = Path(args.calibration_plan).expanduser().absolute()
    try:
        frozen_bytes = frozen_plan_path.read_bytes()
        frozen_plan_id = json.loads(frozen_bytes.decode("utf-8"))["plan_id"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise GenerationRefusal(
            f"frozen calibration plan is unreadable or carries no plan_id: {error}"
        ) from error
    if not isinstance(frozen_plan_id, str) or not frozen_plan_id:
        raise GenerationRefusal("frozen calibration plan plan_id must be a non-empty string")

    chain_bytes = TRACKED_CHAIN_PATH.read_bytes()
    spec = WrapperSpec(
        plan_id=_census_clean("night plan id", plan.plan_id),
        measurement_root=measurement_root,
        measurement_head=plan.measurement_head,
        session_id=args.session_id,
        window_id=_census_clean("window id", args.window_id or plan.plan_id),
        frozen_plan=_require_absolute("frozen calibration plan", str(frozen_plan_path)),
        frozen_plan_id=_census_clean("frozen plan id", frozen_plan_id),
        frozen_plan_sha256=hashlib.sha256(frozen_bytes).hexdigest(),
        evidence_root_id=_census_clean("evidence root id", args.evidence_root_id),
        runs_root=_require_absolute("runs root", runs_root),
        window_custody_root=_require_absolute("window custody root", plan.custody_root),
        calibration_ledger=_require_absolute("calibration ledger", ledger),
        ledger_head_pin=_require_absolute("ledger head pin", head_pin),
        identity_epoch_json=_require_absolute(
            "identity epoch json",
            str(Path(args.identity_epoch_json).expanduser().absolute()),
        ),
        t1_bindings_json=_require_absolute(
            "t1 bindings json",
            str(Path(args.t1_bindings_json).expanduser().absolute()),
        ),
        window_end_epoch_s=window_end_epoch_s,
        slot_count=slot_count,
        chain_source_sidecar=_require_absolute(
            "chain source sidecar", f"{out_path}.chain-source.sha256"
        ),
        chain_sha256=hashlib.sha256(chain_bytes).hexdigest(),
    )
    return spec, out_path, chain_bytes


# --- The reviewed example region -------------------------------------------
#
# The region is documentation with a tripwire: it renders one canonical wrapper
# from fixed placeholder coordinates plus the LIVE digest of the tracked chain,
# so editing the chain without re-emitting a night's wrapper fails --check.

EXAMPLE_NIGHT_ROOT = "/Users/edr/night-custody/derivation-20260912"
EXAMPLE_MEASUREMENT_ROOT = "/private/tmp/joulewise-derivation-20260912-checkout"


def example_spec(chain_bytes: bytes) -> WrapperSpec:
    return WrapperSpec(
        plan_id="derivation-20260912",
        measurement_root=EXAMPLE_MEASUREMENT_ROOT,
        measurement_head="0" * 40,
        session_id="derivation-20260912-epoch",
        window_id="derivation-20260912",
        frozen_plan=f"{EXAMPLE_NIGHT_ROOT}/calibration_plan.json",
        frozen_plan_id="EXAMPLE-FROZEN-PLAN-ID",
        frozen_plan_sha256="0" * 64,
        evidence_root_id="EXAMPLE-EVIDENCE-ROOT-ID",
        runs_root=f"{EXAMPLE_NIGHT_ROOT}/runs",
        window_custody_root=EXAMPLE_NIGHT_ROOT,
        calibration_ledger=(
            f"{EXAMPLE_MEASUREMENT_ROOT}/runs/calibration_observation_ledger.jsonl"
        ),
        ledger_head_pin=(
            f"{EXAMPLE_MEASUREMENT_ROOT}/configs/calibration/"
            "calibration_ledger_head.json"
        ),
        identity_epoch_json=f"{EXAMPLE_NIGHT_ROOT}/identity_epoch.json",
        t1_bindings_json=f"{EXAMPLE_NIGHT_ROOT}/t1_bindings.json",
        window_end_epoch_s=1789215960,
        slot_count=PRE_REGISTERED_SLOT_COUNT,
        chain_source_sidecar=f"{EXAMPLE_NIGHT_ROOT}/chain.zsh.chain-source.sha256",
        chain_sha256=hashlib.sha256(chain_bytes).hexdigest(),
    )


def render_region(chain_bytes: bytes) -> str:
    spec = example_spec(chain_bytes)
    return (
        f"{BEGIN_MARKER}\n"
        "<!-- GENERATED by scripts/gen_derivation_night.py; run it to update. -->\n"
        "\n"
        "One `DIAGNOSTIC_NO_PACK` derivation night is armed by pinning a wrapper,\n"
        "not the tracked chain: the driver passes a chain four variables and no\n"
        "argv, and the tracked chain\n"
        f"`{TRACKED_CHAIN_RELPATH}` needs thirteen more variables and\n"
        "twenty-four per-slot binding arguments.  Emit the wrapper at the night\n"
        "root, then assert byte equality before publishing the plan:\n"
        "\n"
        "```sh\n"
        '"$PY" -B scripts/gen_derivation_night.py \\\n'
        '  --plan "$NIGHT_ROOT/night_plan.json" \\\n'
        '  --session-id "$SESSION_ID" \\\n'
        '  --evidence-root-id "$EVIDENCE_ROOT_ID" \\\n'
        '  --calibration-plan "$NIGHT_ROOT/calibration_plan.json" \\\n'
        '  --identity-epoch-json "$NIGHT_ROOT/identity_epoch.json" \\\n'
        '  --t1-bindings-json "$NIGHT_ROOT/t1_bindings.json"\n'
        '/bin/zsh -n "$NIGHT_ROOT/chain.zsh"\n'
        "```\n"
        "\n"
        "The emitted bytes, rendered here from placeholder coordinates and the\n"
        f"live digest of the tracked chain (`{spec.chain_sha256}`):\n"
        "\n"
        "```zsh\n"
        f"{render_wrapper(spec)}"
        "```\n"
        f"{END_MARKER}\n"
    )


def replace_region(runsheet: str, generated: str) -> str:
    start = runsheet.find(BEGIN_MARKER)
    end = runsheet.find(END_MARKER)
    if start < 0 or end < 0 or end < start:
        raise GenerationRefusal("runsheet generated-region markers are missing")
    end += len(END_MARKER)
    if end < len(runsheet) and runsheet[end] == "\n":
        end += 1
    return runsheet[:start] + generated + runsheet[end:]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", help="frozen v2 night plan JSON (emit mode)")
    parser.add_argument("--session-id", help="the ledger session this night opens")
    parser.add_argument("--window-id", help="default: the night plan's plan_id")
    parser.add_argument("--evidence-root-id")
    parser.add_argument("--calibration-plan", help="the frozen calibration plan bytes")
    parser.add_argument("--identity-epoch-json")
    parser.add_argument("--t1-bindings-json")
    parser.add_argument("--runs-root", help="default: <custody_root>/runs")
    parser.add_argument("--ledger", help="default: <measurement_root>/runs/…jsonl")
    parser.add_argument("--head-pin", help="default: <measurement_root>/configs/…json")
    parser.add_argument("--slot-count", type=int, default=PRE_REGISTERED_SLOT_COUNT)
    parser.add_argument("--allow-slot-count", action="store_true")
    parser.add_argument("--out", help="default: the plan's chain_path")
    parser.add_argument(
        "--check", action="store_true", help="region mode: refuse instead of updating"
    )
    return parser


REQUIRED_EMIT_ARGS = (
    "session_id",
    "evidence_root_id",
    "calibration_plan",
    "identity_epoch_json",
    "t1_bindings_json",
)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.plan is not None:
        missing = [
            f"--{name.replace('_', '-')}"
            for name in REQUIRED_EMIT_ARGS
            if getattr(args, name) is None
        ]
        if missing:
            print(f"FAIL emit mode requires {' '.join(missing)}", file=sys.stderr)
            return 2
        try:
            spec, out_path, chain_bytes = build_spec(args)
            digest = emit(spec, out_path, chain_bytes=chain_bytes)
        except GenerationRefusal as error:
            print(f"FAIL {error}", file=sys.stderr)
            return 2
        print(f"emitted {out_path} sha256={digest}")
        return 0
    chain_bytes = TRACKED_CHAIN_PATH.read_bytes()
    runsheet = RUNSHEET_PATH.read_text(encoding="utf-8")
    expected = replace_region(runsheet, render_region(chain_bytes))
    if args.check:
        if runsheet != expected:
            print(f"FAIL generated derivation-night wrapper region drifted: {RUNSHEET_PATH}")
            return 1
        print("PASS generated derivation-night wrapper region matches")
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
