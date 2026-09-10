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
repository root from its own path (the anchor line ``cd "${0:A:h:h:h}"``), so it
must run as ``$0`` at its in-clone path.

Every citation this file makes into the chain is an ANCHOR TEXT held in
``CHAIN_ANCHORS`` below, never a line number: the chain's line numbers move
whenever its header is edited, and ``tests/test_gen_derivation_night.py``
resolves every anchor against the chain's current bytes.
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

# A derivation night is DIAGNOSTIC_NO_PACK.  A TRANSACTION_PACK plan launches a
# pack launcher instead of the plan's chain (run_night.py:1612-1620) and a
# REHEARSAL_STUB never runs its chain at all (`sleep 2; echo REHEARSAL`,
# run_night.py:1572-1575), so emitting a wrapper for either is meaningless.
DERIVATION_RECEIPT_CLASS = "DIAGNOSTIC_NO_PACK"

# Chain defaults, quoted from the chain itself (see CHAIN_ANCHORS) and pinned
# explicitly by the wrapper: the driver hands the chain `os.environ.copy()`, so
# an inherited SETTLE_S, SLEEP or DATE from the arming operator's shell would
# silently retime the night.
DEFAULT_SETTLE_S = 600
DEFAULT_SLOT_CADENCE_S = 600
DEFAULT_SLOT_CAPTURE_BUDGET_S = 480

# The chain does its input preflight, the pre-reserve readiness check and the
# session reservation BEFORE the settle, and the driver does its own gate work
# before it starts the chain at all.  This is the allowance the window must hold
# on top of the programmed span; it is deliberately far smaller than runbook
# 99 §1.2's total 1320 s margin, which also covers per-capture overrun.
PRE_SETTLE_ALLOWANCE_S = 300

# Anchor texts, not line numbers: each is one exact line of the tracked chain.
# `tests/test_gen_derivation_night.py` resolves every one of them, so a chain
# edit that moves or rewrites a cited line fails a test instead of shipping a
# false citation into a night's artifact.
CHAIN_ANCHORS = {
    "repo_from_argv0": 'cd "${0:A:h:h:h}"',
    "first_required_guard": ': "${SESSION_ID:?required}"',
    "settle_default": 'SETTLE_S="${SETTLE_S:-600}"',
    "cadence_default": 'SLOT_CADENCE_S="${SLOT_CADENCE_S:-600}"',
    "budget_default": 'SLOT_CAPTURE_BUDGET_S="${SLOT_CAPTURE_BUDGET_S:-480}"',
    "slot_count_default": 'SLOT_COUNT="${SLOT_COUNT:-12}"',
    "integer_guard": '    if [[ "$_value" != <-> ]]; then',
    "forward_argv": '    "$@" \\',
    "window_exhausted_guard": (
        "    if (( next_start + SLOT_CAPTURE_BUDGET_S > WINDOW_END_EPOCH_S )); then"
    ),
}


def programmed_span_s(
    slot_count: int,
    settle_s: int = DEFAULT_SETTLE_S,
    slot_cadence_s: int = DEFAULT_SLOT_CADENCE_S,
    slot_capture_budget_s: int = DEFAULT_SLOT_CAPTURE_BUDGET_S,
) -> int:
    """Seconds from chain start to the end of the last slot's capture budget.

    The cadence is START-to-START, so N slots cost (N-1) gaps plus one budget:
    600 + 11 x 600 + 480 = 7680 s for the pre-registered twelve.
    """

    return settle_s + (slot_count - 1) * slot_cadence_s + slot_capture_budget_s


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
    identity_epoch_sha256: str
    t1_bindings_json: str
    t1_bindings_sha256: str
    window_end_epoch_s: int
    slot_count: int
    chain_source_sidecar: str
    chain_sha256: str
    settle_s: int = DEFAULT_SETTLE_S
    slot_cadence_s: int = DEFAULT_SLOT_CADENCE_S
    slot_capture_budget_s: int = DEFAULT_SLOT_CAPTURE_BUDGET_S
    slot_count_ruling: str | None = None


def render_wrapper(spec: WrapperSpec) -> str:
    """Render the wrapper deterministically: same spec, same bytes, always."""

    exports = [
        # The thirteen `:?required` variables of the tracked chain, in the order
        # the chain declares them from `: "${SESSION_ID:?required}"` onward.
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

    departure = (
        []
        if spec.slot_count == PRE_REGISTERED_SLOT_COUNT
        else [
            "#",
            f"# DEPARTURE FROM THE PRE-REGISTRATION: this night declares "
            f"{spec.slot_count} slots,",
            f"# not the pre-registered {PRE_REGISTERED_SLOT_COUNT}. Authorising "
            f"ruling: {spec.slot_count_ruling}.",
        ]
    )
    lines = [
        "#!/bin/zsh",
        "# GENERATED by scripts/gen_derivation_night.py — do not edit; re-emit.",
        f"# Derivation-night wrapper for night plan {spec.plan_id}.",
        *departure,
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
            "# Every refusal below prints FAIL <reason> to stderr: the driver",
            "# redirects this stream to a file, and an unattended night's only",
            "# forensic record of a 3 a.m. refusal is what is written here.",
            "sha256_of() { /usr/bin/shasum -a 256 \"$1\" | /usr/bin/awk '{print $1}'; }",
            "",
            "# Authenticate the desk-produced inputs before any window time is spent.",
            "[ -f \"$PLAN\" ] || route_refuse 'frozen calibration plan is missing'",
            "[ -f \"$IDENTITY_EPOCH_JSON\" ] || "
            "route_refuse 'identity epoch json is missing'",
            "[ -f \"$T1_BINDINGS_JSON\" ] || route_refuse 't1 bindings json is missing'",
            "# Re-derive the frozen plan's identity from its bytes, as the G2-a bracket",
            "# does (gen_g2_phase_d.py:250-252), and refuse a swapped plan file.",
            "observed_plan_id=\"$(/usr/bin/jq -er '.plan_id' \"$PLAN\")\"",
            '[ "$observed_plan_id" = "$PLAN_ID" ] || '
            "route_refuse 'frozen plan id does not equal the arm-time literal'",
            '[ "$(sha256_of "$PLAN")" = "$PLAN_SHA256" ] || '
            "route_refuse 'frozen plan bytes do not equal the arm-time digest'",
            "# The identity epoch and T1 bindings are copied VERBATIM into every",
            "# slot record by the reservation, so their bytes are pinned too.",
            f'[ "$(sha256_of "$IDENTITY_EPOCH_JSON")" = '
            f"{_quote(spec.identity_epoch_sha256)} ] || "
            "route_refuse 'identity epoch bytes do not equal the arm-time digest'",
            f'[ "$(sha256_of "$T1_BINDINGS_JSON")" = '
            f"{_quote(spec.t1_bindings_sha256)} ] || "
            "route_refuse 't1 bindings bytes do not equal the arm-time digest'",
            "",
            "# The plan pins THIS wrapper's digest, and the capturing chain's digest",
            "# is a LITERAL in these bytes, so the plan-pinned digest moves whenever",
            "# the capturing chain's bytes move: the coverage is transitive and needs",
            "# no second file.  (The night root also carries an advisory",
            "# <wrapper>.chain-source.sha256 for hand checks; nothing trusts it.)",
            f'[ "$(sha256_of "$REPO/{TRACKED_CHAIN_RELPATH}")" = '
            f"{_quote(spec.chain_sha256)} ] || "
            "route_refuse 'tracked derivation chain bytes do not match the arm-time digest'",
            "",
            "# exec, never source: the chain derives REPO from its own $0 with",
            f"#   {CHAIN_ANCHORS['repo_from_argv0']}",
            "# and its per-slot bindings are its own argv, forwarded verbatim to",
            "# the reservation by the chain's",
            f"#   {CHAIN_ANCHORS['forward_argv'].strip()}",
            f"exec /bin/zsh \"$REPO/{TRACKED_CHAIN_RELPATH}\" \\",
        ]
    )
    lines.extend(binding_lines)
    return "\n".join(lines) + "\n"


def _sidecar_text(digest: str, name: str) -> str:
    """GNU ``shasum`` form, the only form the driver accepts (run_night.py:97)."""

    return f"{digest}  {name}\n"


def emit(spec: WrapperSpec, out_path: Path, *, chain_bytes: bytes) -> str:
    """Write the wrapper, its plan-pinned sidecar, and one advisory sidecar.

    The third file (``<wrapper>.chain-source.sha256``) exists only so an
    operator can hand-check the tracked chain with ``shasum -a 256 -c`` from the
    clone.  Nothing at launch reads it: the chain's digest is a literal inside
    the wrapper's own — plan-pinned — bytes.
    """

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
    # An allow-list, not a pack-only refusal: TRANSACTION_PACK launches a pack
    # launcher instead of the plan's chain and REHEARSAL_STUB never runs the
    # chain at all, so a wrapper emitted for either would never execute.
    if plan.receipt_class != DERIVATION_RECEIPT_CLASS:
        raise GenerationRefusal(
            f"a derivation night is {DERIVATION_RECEIPT_CLASS}; this plan is "
            f"{plan.receipt_class}"
        )

    slot_count = args.slot_count
    if slot_count != PRE_REGISTERED_SLOT_COUNT and not args.allow_slot_count:
        raise GenerationRefusal(
            f"slot count {slot_count} is not the pre-registered "
            f"{PRE_REGISTERED_SLOT_COUNT}; pass --allow-slot-count with "
            "--slot-count-ruling <ref> to override"
        )
    if slot_count != PRE_REGISTERED_SLOT_COUNT and not args.slot_count_ruling:
        raise GenerationRefusal(
            "--allow-slot-count requires --slot-count-ruling <ref>: departing "
            f"from the pre-registered {PRE_REGISTERED_SLOT_COUNT} slots needs a "
            "named authority, and the reference is written into the wrapper"
        )
    if slot_count < 1:
        raise GenerationRefusal("slot count must be positive")

    # The window must hold the schedule the chain will actually run, or the
    # night opens its session and aborts part-way with window_exhausted.
    required_span = programmed_span_s(slot_count)
    required_window = required_span + PRE_SETTLE_ALLOWANCE_S
    if plan.window_max_s < required_window:
        raise GenerationRefusal(
            f"window_max_s {plan.window_max_s} < required {required_span} + "
            f"{PRE_SETTLE_ALLOWANCE_S} = {required_window} s: the programmed "
            f"span of {slot_count} slots is settle {DEFAULT_SETTLE_S} + "
            f"{slot_count - 1} x cadence {DEFAULT_SLOT_CADENCE_S} + budget "
            f"{DEFAULT_SLOT_CAPTURE_BUDGET_S}, plus the pre-settle allowance; "
            "lengthen the window rather than shortening the schedule"
        )

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

    identity_epoch_path = Path(args.identity_epoch_json).expanduser().absolute()
    t1_bindings_path = Path(args.t1_bindings_json).expanduser().absolute()

    # Digest the chain from the CLONE THE NIGHT RUNS, never from the checkout
    # this generator happens to be executed from: at arm time the magistrate's
    # worktree and the measurement clone are different trees, and a digest of
    # bytes the night will never run refuses at launch with the night burned.
    clone_chain_path = Path(measurement_root) / TRACKED_CHAIN_RELPATH
    try:
        chain_bytes = clone_chain_path.read_bytes()
        identity_epoch_bytes = identity_epoch_path.read_bytes()
        t1_bindings_bytes = t1_bindings_path.read_bytes()
    except OSError as error:
        raise GenerationRefusal(f"a pinned input is unreadable: {error}") from error
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
            "identity epoch json", str(identity_epoch_path)
        ),
        identity_epoch_sha256=hashlib.sha256(identity_epoch_bytes).hexdigest(),
        t1_bindings_json=_require_absolute("t1 bindings json", str(t1_bindings_path)),
        t1_bindings_sha256=hashlib.sha256(t1_bindings_bytes).hexdigest(),
        window_end_epoch_s=window_end_epoch_s,
        slot_count=slot_count,
        chain_source_sidecar=_require_absolute(
            "chain source sidecar", f"{out_path}.chain-source.sha256"
        ),
        chain_sha256=hashlib.sha256(chain_bytes).hexdigest(),
        slot_count_ruling=args.slot_count_ruling,
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
        identity_epoch_sha256="1" * 64,
        t1_bindings_json=f"{EXAMPLE_NIGHT_ROOT}/t1_bindings.json",
        t1_bindings_sha256="2" * 64,
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
        "One `DIAGNOSTIC_NO_PACK` derivation night is armed by pinning a\n"
        "**wrapper** — a generated zsh file, one per night, carrying that night's\n"
        "whole environment as literal `export` lines — rather than the tracked\n"
        "chain itself.  The reason: the night driver hands the file it launches\n"
        "exactly four variables (`NIGHT_PLAN_ID`, `MEASUREMENT_ROOT`,\n"
        "`MEASUREMENT_HEAD`, `PY`) and no command-line arguments, while the\n"
        f"tracked chain `{TRACKED_CHAIN_RELPATH}`\n"
        "needs thirteen more variables and twenty-four per-slot binding\n"
        "arguments.  The wrapper supplies both, then `exec`s the chain.\n"
        "\n"
        "### The three emitted files\n"
        "\n"
        "One generator run writes exactly three files into the night root (the\n"
        "custody directory the plan calls `custody_root`):\n"
        "\n"
        "| File | Role |\n"
        "|---|---|\n"
        "| `chain.zsh` | the wrapper; the plan's `chain_path` must be this path |\n"
        "| `chain.zsh.sha256` | its SHA-256 in `shasum` form; the plan's `chain_sha256_path` must be this path, and the driver refuses the night unless the wrapper's bytes still hash to it |\n"
        "| `chain.zsh.chain-source.sha256` | ADVISORY ONLY — the tracked chain's digest, for an operator's hand `shasum -a 256 -c` run from the clone. Nothing reads it at launch: the wrapper carries the same digest as a literal inside its own bytes, so deleting or rewriting this file changes nothing about what the night will accept. |\n"
        "\n"
        "### Arm order (each step depends on the one before it)\n"
        "\n"
        "1. **Cut the clone at H.** Create the measurement checkout the night will\n"
        "   run, at the commit `H` the plan names as `measurement_head`, and\n"
        "   record `git -C <CLONE> status --porcelain`; it must be empty, because\n"
        "   nothing downstream detects uncommitted edits outside the chain itself.\n"
        "2. **Author the night plan**, naming `t0_epoch_s`, `window_max_s`,\n"
        "   `custody_root`, `measurement_root`, `measurement_head` = `H`,\n"
        "   `chain_path` = `<NIGHT_ROOT>/chain.zsh`, and `chain_sha256_path` =\n"
        "   that path plus `.sha256`.  The plan must exist first: the generator\n"
        "   reads all of those from it, and refuses if `chain_path` is anything\n"
        "   else.\n"
        "3. **Generate the wrapper** with the command below.  The generator\n"
        "   digests the tracked chain **from the clone**, never from the checkout\n"
        "   it is run in, and bakes that digest — plus the frozen calibration\n"
        "   plan's, the identity epoch's and the T1 bindings' — into the wrapper\n"
        "   as literals.\n"
        "4. **Re-emit and assert byte equality** at arm time: emit a second copy\n"
        "   to a scratch path and require identical bytes.  Emission is\n"
        "   deterministic, so any difference means an input drifted — the chain,\n"
        "   the frozen plan, or the plan's own coordinates.\n"
        "5. **`/bin/zsh -n`** the emitted wrapper (a syntax check that runs\n"
        "   nothing), then install the plan.  From here the plan pins the\n"
        "   wrapper's digest and the wrapper pins the chain's, so the plan's\n"
        "   attestation reaches the bytes that actually capture.\n"
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
        "The generator refuses, before writing anything, when: the plan is not an\n"
        "exact `DIAGNOSTIC_NO_PACK` v2 plan; `window_max_s` cannot hold the\n"
        "programmed span (settle + (slots − 1) × cadence + one capture budget =\n"
        f"{programmed_span_s(PRE_REGISTERED_SLOT_COUNT)} s for twelve slots) plus "
        f"the {PRE_SETTLE_ALLOWANCE_S} s pre-settle allowance;\n"
        "`t0 + window_max_s + 300 s` is not before the next local 07:00 (the\n"
        "dead-man); any emitted literal contains `codex`, `claude` or `t3`, which\n"
        "the night's own 30-second agent census would match and kill the night\n"
        "for; or the slot count is not the pre-registered twelve without an\n"
        "explicit `--slot-count-ruling` reference.\n"
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
    parser.add_argument(
        "--allow-slot-count",
        action="store_true",
        help=(
            f"depart from the pre-registered {PRE_REGISTERED_SLOT_COUNT} slots; "
            "requires --slot-count-ruling and is announced on stderr and in the "
            "emitted wrapper's header"
        ),
    )
    parser.add_argument(
        "--slot-count-ruling",
        metavar="REF",
        help="the ruling or record that authorises a non-pre-registered slot count",
    )
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
        if spec.slot_count != PRE_REGISTERED_SLOT_COUNT:
            print(
                f"DEPARTURE this night declares {spec.slot_count} slots, NOT the "
                f"pre-registered {PRE_REGISTERED_SLOT_COUNT} (cold-gate ruling 46 "
                f"§R-c); authority: {spec.slot_count_ruling}",
                file=sys.stderr,
            )
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
