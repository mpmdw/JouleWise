#!/usr/bin/env python3
"""Desk tools for the D-079 calibration epoch: watch it, and prepare a candidate.

Neither subcommand authorizes a capture, issues anything, or writes into
`configs/calibration/`.

`check` is READ-ONLY. It authenticates the ACTIVE issued acceptance artifact and
the ledger, then prints how the machine's identity today compares with the epoch
that artifact binds; it does not evaluate a trigger observation and does not
change the D-102 prior-artifact rule. Given `--session-ids`, it additionally
prints a REGISTRATION DRY RUN: for each named ledger session, its kind, its
state and whether that state is terminal, how many slots it declared and how
many are filled, and how many captures are excluded under each named mechanism;
then how many prior-set prefix rows are pending or unresolved, and whether the
registration would be admissible. Every field is a count, a state name or a
mechanism name. The dry run reports no measured value of any kind, because the
pre-registration forbids examining one before the registration's last session is
terminal, and this is the tool one runs BETWEEN capture nights.

`prepare-candidate` WRITES EXACTLY ONE FILE, to the path the caller names with
`--out`; there is no default destination, so this tool cannot write into
`configs/calibration/` by omission. That file is a CANDIDATE, marked
`candidate_not_issued: true`, which the production acceptance loader refuses.
Issuing it is the act of the D-138 transaction -- the single reviewed commit
that swaps the live acceptance and every pin that names it -- and happens only
after the COLD SCIENCE GATE, the fresh-eyes review of the exclusions and the
per-night diagnostics that no one involved in the capture may sit on.

The command derives the successor acceptance from the ledger: it selects corpus
members by the registration (the ledger sessions the capture nights were
reserved under), computes the Decimal statistics, and sets the OPERATIVES --
the three numbers the acceptance actually governs measurement with. They are
the BRACKET SCREEN, the drift below which a measurement window passes without
spending any of its error budget; the BUDGET CEILING, the largest drift the
generation will ever budget for; and the LEVEL SCREEN, the absolute bound above
which a single capture is refused before a window opens. Two more inputs are
named on the command line. The PRIOR-SET PREFIX is the run of ledger rows at or
below the cutoff, which the candidate must account for exactly. The QUANTILE
PROOF is the record showing that the Student-t quantile for this corpus's
realized degrees of freedom was computed correctly, checked two independent
ways, before any threshold derived from it was written down. The quantiles
themselves are computed in 80-digit decimal, but the two-draw PREDICTIONS the
operatives rest on are then evaluated in BINARY64 and recorded as the shortest
decimal that reads back as the same double -- r6's sealed rule string, kept
verbatim so this generation's arithmetic is the predecessor's arithmetic.

Decision ids appear in the artifact and in refusals: D-102 is the acceptance
artifact's own contract (how a generation is derived and what may judge it);
D-109 is the raw-physics and artifact-hash verification the member table rests
on; D-125 fixes the envelope rule that carries operatives from one generation to
the next; D-126 fixes the minimum corpus size and the strict screen-below-ceiling
rule. A TRIGGER OBSERVATION is a later capture whose result would oblige the
generation to be re-derived; the candidate lists the conditions, and this tool
never evaluates one.

`prepare-candidate` REFUSES, printing its reason and writing nothing, when: any
registration session is not yet terminal; the `--d125-ruling` reference is
absent; the retained corpus is below the required size (19, or 17 with
`--ed-ruling`); a prior-set row is pending or unresolved; a valid same-epoch
observation lies outside the registration; a member's stored bytes disagree with
its ledger row; the realized degrees of freedom fail the quantile proof; the
bracket screen is not strictly below the budget ceiling; or two or more retained
members exceed the predecessor's level screen.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_HALF_EVEN, getcontext, localcontext
import hashlib
import importlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Iterable, Mapping, Sequence

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_bracketing import (  # noqa: E402
    ACTIVE_ACCEPTANCE_ID,
    ACCEPTANCE_BOUND_SCHEMA,
    BRACKET_SCREEN_QUANTUM_S,
    D125_SCREEN_FLOOR_S,
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    ESTIMATOR_CODE_PATHS,
    PREFLIGHT_LEVEL_SCREEN_QUANTUM_S,
    PROTOCOL_ID,
    REGISTERED_CORPUS_EXCLUSION_REASONS,
    SCREEN_RULE_FLOORED_RANGE_ENVELOPE,
    load_calibration_acceptance_bound,
    protocol_sha256,
)
from joulewise.calibration_bracketing import _canonical_sha256  # noqa: E402
from joulewise.calibration_ledger import (  # noqa: E402
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    LedgerObservation,
    SESSION_KIND_DERIVATION,
    artifact_hashes,
    content_id_from_artifact_hashes,
    load_calibration_ledger_snapshot,
)
from joulewise.uncertainty_evidence import (  # noqa: E402
    CLOCK_ANCHOR_UNRESOLVED,
    CLOCK_METHOD_V3,
)


WATCH_FIELDS = ("os_build", "hardware_model", "powermetrics_sha256", "mlx_version")
POWERMETRICS_PATH = Path("/usr/bin/powermetrics")
# Absolute, like every other governed invocation: a PATH-resolved probe could
# report an identity this machine does not have.
SYSCTL_PATH = Path("/usr/sbin/sysctl")


def observe_machine() -> dict[str, str | None]:
    """Read identity only: the sampler binary is hashed, never executed."""
    observed: dict[str, str | None] = {}
    for field, key in (("os_build", "kern.osversion"), ("hardware_model", "hw.model")):
        try:
            observed[field] = subprocess.run(
                [str(SYSCTL_PATH), "-n", key], check=True, capture_output=True,
                text=True, timeout=10,
            ).stdout.strip() or None
        except (OSError, subprocess.SubprocessError):
            observed[field] = None
    try:
        observed["powermetrics_sha256"] = hashlib.sha256(
            POWERMETRICS_PATH.read_bytes()
        ).hexdigest()
    except OSError:
        observed["powermetrics_sha256"] = None
    try:
        # Use the same module/version surface as the live writer's T1 vector.
        version = getattr(importlib.import_module("mlx.core"), "__version__", None)
        observed["mlx_version"] = version if isinstance(version, str) and version else None
    except Exception:
        # Optional native dependency: import/link/initialization failure means
        # unavailable, never an assertion that the registered version matches.
        observed["mlx_version"] = None
    return observed


def mismatched_fields(
    expected: Mapping[str, Any], observed: Mapping[str, Any],
) -> tuple[str, ...]:
    """Unknown on either side is a mismatch, including unknown == unknown."""
    return tuple(
        field for field in WATCH_FIELDS
        if not isinstance(expected.get(field), str) or not expected[field]
        or not isinstance(observed.get(field), str) or not observed[field]
        or expected[field] != observed[field]
    )


DRY_RUN_HEADER = "Registration dry run (counts and states only; no measured value)"
# Exit code for `check` when a named registration is NOT admissible.  Distinct
# from the epoch watch's 3 so a caller can tell "the machine has drifted" from
# "the registration is not ready".
DRY_RUN_INADMISSIBLE_EXIT = 5


def registration_dry_run(
    snapshot: Any, session_ids: Sequence[str]
) -> tuple[int, list[str]]:
    """Report whether a registration WOULD be admissible, naming no value.

    CG46 V5 defines `check` as the desk epoch watch AND a registration dry run.
    Blindness binds here exactly as it binds `prepare-candidate`, because this
    is the tool one runs BETWEEN capture nights: every line below is a count, a
    state name or a mechanism name, and no line can carry a bound, a screen, a
    statistic or a member's value.  The slot counts come from the session
    record's own `declared_slots` and `finalized_slots` -- the LENGTH of each,
    never the slot objects -- so an open session reports its progress without
    anything reading a captured value.
    """

    lines = ["", DRY_RUN_HEADER]
    blockers: list[str] = []
    by_id = snapshot.bracket_session_by_id
    for session_id in session_ids:
        session = by_id.get(session_id)
        if session is None:
            blockers.append(f"session {session_id} is not in the ledger")
            lines.append(f"{session_id}: absent")
            continue
        terminal = session.state in TERMINAL_SESSION_STATES
        if session.session_kind != SESSION_KIND_DERIVATION:
            blockers.append(
                f"session {session_id} is kind {session.session_kind!r}, not derivation"
            )
        if not terminal:
            blockers.append(f"session {session_id} is {session.state!r}, not terminal")
        excluded: dict[str, int] = {}
        # The bundle reads that classify exclusions live ONLY inside this
        # branch.  Not because reading is itself a leak -- nothing read here is
        # printed -- but because a gate that no path can go around is a
        # guarantee, while a reviewed one is a promise.  `finalized_slots` is
        # non-empty for an open session too, so removing this `if` really does
        # open bundles mid-campaign.
        if terminal:
            for observation in session.finalized_slots.values():
                if observation.classification_disposition != "valid":
                    continue
                try:
                    evidence, _ = _read_member_evidence(observation)
                except PrepareRefusal as refusal:
                    blockers.append(refusal.reason)
                    continue
                resolved, detail = anchor_v3_replay_outcome(evidence)
                if not resolved:
                    mechanism = detail or "unknown"
                    excluded[mechanism] = excluded.get(mechanism, 0) + 1
                    if detail not in REGISTERED_CORPUS_EXCLUSION_REASONS:
                        blockers.append(
                            f"session {session_id}: unregistered exclusion "
                            f"mechanism {detail!r}"
                        )
        lines.append(
            f"{session_id}: kind={session.session_kind} state={session.state} "
            f"terminal={'yes' if terminal else 'no'} "
            f"declared={len(session.declared_slots)} "
            f"filled={len(session.finalized_slots)} "
            f"excluded={_excluded_summary(excluded)}"
        )
    unresolved = sum(
        1
        for observation in snapshot.observations
        if observation.content_id is None
        or observation.classification_disposition not in PRIOR_SET_DISPOSITIONS
    )
    # A COUNT, not the attempt ids: naming rows invites reading them, and the
    # count is all a desk decision needs.
    lines.append(f"prefix pending or unresolved rows: {unresolved}")
    if unresolved:
        blockers.append("prior set holds pending or unresolved attempts")
    lines.append(
        "registration admissible for prepare-candidate: "
        + ("yes" if not blockers else "no")
    )
    for blocker in blockers:
        lines.append(f"  blocker: {blocker}")
    return (0 if not blockers else DRY_RUN_INADMISSIBLE_EXIT), lines


def _excluded_summary(excluded: Mapping[str, int]) -> str:
    """Exclusion mechanisms and their counts, in a fixed order."""

    if not excluded:
        return "none"
    return ",".join(f"{name}:{count}" for name, count in sorted(excluded.items()))


def check(args: argparse.Namespace) -> int:
    errors: list[str] = []
    expected: dict[str, Any] = {}
    acceptance = load_calibration_acceptance_bound(args.acceptance)
    if (
        acceptance is None or acceptance.get("artifact_role") != "issued"
        or acceptance.get("acceptance_id") != ACTIVE_ACCEPTANCE_ID
        or not isinstance(acceptance.get("identity_epoch"), Mapping)
    ):
        errors.append("acceptance: invalid or not ACTIVE issued acceptance")
    else:
        epoch = acceptance["identity_epoch"]
        expected.update({field: epoch.get(field) for field in WATCH_FIELDS[:2]})

    snapshot = load_calibration_ledger_snapshot(
        args.ledger, args.head_pin, require_committed_pin=True,
        verify_custody=True, mode="read_replay", repo_root=REPO_ROOT,
    )
    if snapshot.refusal_reasons:
        errors.append("ledger: " + ", ".join(snapshot.refusal_reasons))
    elif not snapshot.receipts:
        errors.append("ledger: no last row with T1 bindings")
    else:
        # Do not silently substitute an older row if the physical last row
        # lacks T1 (e.g. an abort/control receipt); report unavailable instead.
        t1 = snapshot.receipts[-1].get("t1_bindings")
        if not isinstance(t1, Mapping):
            errors.append("ledger: last row has no T1 bindings")
        else:
            expected.update({field: t1.get(field) for field in WATCH_FIELDS[2:]})

    observed = observe_machine()
    mismatches = mismatched_fields(expected, observed)
    preregistration_lines: list[str] = []
    if args.preregistration is not None:
        try:
            text = Path(args.preregistration).read_text(encoding="utf-8")
            _, registered_powermetrics = preregistration_epoch_pins(text)
        except (OSError, PrepareRefusal) as error:
            preregistration_lines.append(f"pre-registration: unusable ({error})")
        else:
            agrees = observed.get("powermetrics_sha256") == registered_powermetrics
            preregistration_lines.append(
                f"pre-registered powermetrics sha256 {registered_powermetrics}: "
                + ("match" if agrees else "MISMATCH — the registration is void")
            )
            if not agrees:
                errors.append("pre-registration: powermetrics sha256 differs")
    print("Desk epoch watch (identity comparison only; no capture authorization)")
    print(f"ACTIVE acceptance: {ACTIVE_ACCEPTANCE_ID}")
    print(f"{'field':<22} {'expected':<64} {'observed':<64} status")
    for field in WATCH_FIELDS:
        baseline = expected.get(field) or "unavailable"
        current = observed.get(field) or "unavailable"
        status = "MISMATCH" if field in mismatches else "match"
        print(f"{field:<22} {baseline:<64} {current:<64} {status}")
    for error in errors:
        print(error)
    if mismatches:
        print("mismatched fields: " + ", ".join(mismatches))
    # Appended only when --preregistration is given, so the watch's own output
    # stays byte-identical without it.
    for line in preregistration_lines:
        print(line)
    # The epoch-watch output above is byte-identical whether or not a
    # registration was named; the dry run only ever APPENDS.
    # An empty `--session-ids` value names no session, so it is not a request
    # for a dry run; it must leave the watch output byte-identical.
    named = [session_id for session_id in args.session_ids if session_id]
    if not named:
        return 3 if errors or mismatches else 0
    dry_run_code, lines = registration_dry_run(snapshot, named)
    for line in lines:
        print(line)
    # When a registration is named, the ANSWER is the registration's: the epoch
    # watch above still prints in full, but an epoch that has drifted is the
    # whole reason a new corpus is being captured, so it must not mask the
    # question the caller actually asked.
    return dry_run_code


# ---------------------------------------------------------------------------
# prepare-candidate (ruling 46 R-a A3 / R-b V5 / V7; addendum A-2, A-3, A-4, A-7)
# ---------------------------------------------------------------------------
# The pre-registration's operative rules.  The screen floor, the two quanta and
# the screen-rule NAME are imported from `joulewise.calibration_bracketing`,
# which is their ONE home: the issuer that emits a row and the validator that
# admits it must not carry two copies of the same number.
#
# The predecessor's maximum plus its range: the second recorded diagnostic, a
# RULED literal (CG46 addendum A-4 corrected the last digits), so it is stated
# here rather than derived -- and then checked at run time against the
# predecessor's own statistics, so the literal cannot outlive the artifact it
# describes.  The level-screen threshold is NOT restated: it is read from the
# authenticated predecessor, which is its one home.
R6_MAXIMUM_PLUS_RANGE_S = Decimal("0.04262208300415633")
SCREEN_CHALLENGE_MEMBER_LIMIT = 2
# D-126 cl.2's SUCCESSOR_MINIMUM_CORPUS_SIZE, a corpus-SIZE floor (addendum A-2).
SUCCESSOR_MINIMUM_CORPUS_SIZE = 19
# The dispositions an ISSUED artifact's prior set may carry (the validator's
# `allowed_prior_dispositions` for role `issued`).
PRIOR_SET_DISPOSITIONS = ("valid", "systematic-invalid", "ordinary-invalid")
# The one alternative floor the pre-registration and CG46 A-2 name, and the only
# value `--ed-ruling` licenses.
RULED_ALTERNATIVE_CORPUS_SIZE = 17
# The pre-registered schedule: three agent-free nights of twelve declared slots.
PREREGISTERED_NIGHT_COUNT = 3
PREREGISTERED_SLOTS_PER_NIGHT = 12
# What the emitted bytes authorize, said in words rather than as a boolean.
CANDIDATE_LICENCE = (
    "These bytes license nothing: no measurement window, no claim, no "
    "threshold. No tool may load them as authority; the production loader "
    "refuses them by artifact_role."
)
PRESENTATION_QUANTUM_S = Decimal("0.000000000000000001")
DECIMAL_WORK_PRECISION = 80
# The screen rule this generation is DERIVED under is a property of the RULE,
# not of which arm of the `max` happened to win: every generation derived under
# the pre-registration's D-125 envelope
# `S = max(range quantized 1e-6 ROUND_HALF_EVEN, 0.010818)` registers
# `SCREEN_RULE_FLOORED_RANGE_ENVELOPE`, whether the range or the floor won.
# Naming the rule by the realized branch would make the registered rule a
# function of the data, which is exactly what a pre-registration forbids -- and
# it would put the ordinary case in the wrong bucket, because a corpus at the
# n = 19 floor has a range just BELOW 0.010818 and takes the floor arm.
# 100 significant digits of pi, used only by the Student-t quantile's Beta
# normalizer for ODD degrees of freedom (Gamma(1/2) = sqrt(pi) cancels for even
# df and does not for odd).  The digits beyond `DECIMAL_WORK_PRECISION` are
# INERT, not spare accuracy: Decimal rounds this literal into the working
# context the first time it takes part in an operation, so 80 of them are used
# and the rest are guard digits that keep the constant correct if the working
# precision is ever raised.  They are kept for that reason and for none other.
# The proof route computes pi by Machin's formula instead of reading this
# constant, so a mistyped digit here surfaces as a quantile-proof failure.
_PI = Decimal(
    "3.14159265358979323846264338327950288419716939937510"
    "58209749445923078164062862089986280348253421170680"
)
QUANTILE_METHOD = (
    "regularized incomplete beta (Lentz continued fraction) inverted by "
    "bisection in 80-digit decimal; exact for both even and odd degrees of "
    "freedom"
)
# Copied verbatim from r6's artifact: this string sits inside the sealed
# derivation set, so a paraphrase would change the digest of an identical
# derivation.
TWO_DRAW_PREDICTION_RULE = (
    "prediction_p_two_draw_s = t(p, n-1) * sample_sd_presentation_s * sqrt(2), "
    "evaluated in binary64 and recorded as its shortest round-tripping decimal"
)
# The pre-registration (`~:131-134`) forbids issuing on a df whose quantile is
# not PROVEN in the artifact's own record.  Two independent bounds, both
# checked for the realized df before anything is written.
QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS = 30
QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL = Decimal(1).scaleb(-30)
QUANTILE_PROOF_PROBABILITIES = ("0.975", "0.995")


def _half_integer_gamma(twice_argument: int) -> tuple[Decimal, int]:
    """Gamma(twice_argument / 2) as (rational factor, power of sqrt(pi)).

    Splitting the sqrt(pi) out keeps the Beta normalizer exact: for even df the
    powers cancel to zero and no transcendental enters at all, and for odd df
    exactly one factor of pi survives.
    """

    if twice_argument <= 0:
        raise ValueError("gamma argument must be positive")
    if twice_argument % 2 == 0:
        return Decimal(math.factorial(twice_argument // 2 - 1)), 0
    half = (twice_argument - 1) // 2
    numerator = Decimal(math.factorial(2 * half))
    denominator = Decimal(4) ** half * Decimal(math.factorial(half))
    return numerator / denominator, 1


def _half_integer_beta(twice_a: int, twice_b: int) -> Decimal:
    """B(twice_a/2, twice_b/2) for half-integer arguments."""

    gamma_a, power_a = _half_integer_gamma(twice_a)
    gamma_b, power_b = _half_integer_gamma(twice_b)
    gamma_ab, power_ab = _half_integer_gamma(twice_a + twice_b)
    power = power_a + power_b - power_ab
    value = gamma_a * gamma_b / gamma_ab
    if power == 0:
        return value
    if power == 1:
        return value * _PI.sqrt()
    if power == 2:
        return value * _PI
    raise ValueError(f"unsupported sqrt(pi) power {power}")


def _beta_continued_fraction(x: Decimal, a: Decimal, b: Decimal) -> Decimal:
    """Lentz evaluation of the incomplete-beta continued fraction."""

    tiny = Decimal(1).scaleb(-60)
    tolerance = Decimal(1).scaleb(-55)
    qab, qap, qam = a + b, a + 1, a - 1
    c = Decimal(1)
    d = 1 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1 / d
    result = d
    for step in range(1, 500):
        step_d = Decimal(step)
        step2 = 2 * step_d
        numerator = step_d * (b - step_d) * x / ((qam + step2) * (a + step2))
        d = 1 + numerator * d
        if abs(d) < tiny:
            d = tiny
        c = 1 + numerator / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        result *= d * c
        numerator = -(a + step_d) * (qab + step_d) * x / ((a + step2) * (qap + step2))
        d = 1 + numerator * d
        if abs(d) < tiny:
            d = tiny
        c = 1 + numerator / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        delta = d * c
        result *= delta
        if abs(delta - 1) < tolerance:
            return result
    raise ArithmeticError("incomplete beta continued fraction did not converge")


def regularized_incomplete_beta(x: Decimal, twice_a: int, twice_b: int) -> Decimal:
    """I_x(twice_a/2, twice_b/2) for half-integer parameters."""

    if x <= 0:
        return Decimal(0)
    if x >= 1:
        return Decimal(1)
    a = Decimal(twice_a) / 2
    b = Decimal(twice_b) / 2
    front = (a * x.ln() + b * (1 - x).ln()).exp() / _half_integer_beta(twice_a, twice_b)
    if x < (a + 1) / (a + b + 2):
        return front * _beta_continued_fraction(x, a, b) / a
    return 1 - front * _beta_continued_fraction(1 - x, b, a) / b


def student_t_survival(t: Decimal, degrees_of_freedom: int) -> Decimal:
    """P(T > t) for Student's t with the given (even OR odd) df, t >= 0."""

    df = Decimal(degrees_of_freedom)
    return regularized_incomplete_beta(df / (df + t * t), degrees_of_freedom, 1) / 2


def student_t_quantile(probability: str, degrees_of_freedom: int) -> Decimal:
    """The two-sided upper quantile t(p, df), bisected to full precision.

    r6's recorded quantiles came from an EVEN-degree-of-freedom closed form
    (Abramowitz & Stegun 26.7.4).  A successor corpus of retained n = 20 has
    df = 19, so that path cannot be reused; this one is exercised on both
    parities by the tests and reproduces r6's df = 16 pins to 20 places.
    """

    if degrees_of_freedom < 1:
        raise ValueError("degrees of freedom must be at least 1")
    # The accuracy of a claim-bearing quantile must not follow whatever Decimal
    # context the CALLER happens to be in: a bare call at the interpreter
    # default (prec 28) silently loses the last digits.  Pin it here.
    with localcontext() as context:
        context.prec = DECIMAL_WORK_PRECISION
        target = Decimal(1) - Decimal(probability)
        low, high = Decimal(0), Decimal(100)
        for _ in range(300):
            middle = (low + high) / 2
            if student_t_survival(middle, degrees_of_freedom) > target:
                low = middle
            else:
                high = middle
        return +((low + high) / 2)


def _decimal_arctan(x: Decimal) -> Decimal:
    """arctan(x) by Euler's series, which converges for every real x.

    Euler's form `sum_n (2^2n (n!)^2 / (2n+1)!) * x^(2n+1) / (1+x^2)^(n+1)` is
    used instead of the Gregory series precisely because it does not diverge
    for |x| > 1, and the quantile bisection walks t over (0, 100).
    """

    # Euler's terms decay like (x^2/(1+x^2))^n, which crawls for large |x|
    # (at x = 22 the ratio is 0.998).  Reflect into |x| <= 1 first, where the
    # ratio is at most 1/2, so the series is fast for every argument the
    # quantile bisection produces.  `_machin_pi` only ever asks for arctan(1/5)
    # and arctan(1/239), so this branch cannot recurse into it.
    if x < 0:
        return -_decimal_arctan(-x)
    if x > 1:
        return _machin_pi() / 2 - _decimal_arctan(1 / x)
    x_squared = x * x
    denominator = 1 + x_squared
    term = x / denominator
    total = term
    tolerance = Decimal(1).scaleb(-(DECIMAL_WORK_PRECISION + 10))
    for n in range(1, 4000):
        term *= Decimal(2 * n) * x_squared / (Decimal(2 * n + 1) * denominator)
        total += term
        if abs(term) < tolerance:
            return total
    raise ArithmeticError("arctan series did not converge")


_MACHIN_PI_BY_PRECISION: dict[int, Decimal] = {}


def _machin_pi() -> Decimal:
    """pi = 16 arctan(1/5) - 4 arctan(1/239), computed, never transcribed.

    The proof route must share NOTHING with the quantile route, and the
    quantile's Beta normalizer uses the transcribed `_PI`.  Computing pi here
    means a mistyped digit in that constant shows up as a proof failure.
    """

    precision = getcontext().prec
    cached = _MACHIN_PI_BY_PRECISION.get(precision)
    if cached is None:
        cached = 16 * _decimal_arctan(Decimal(1) / 5) - 4 * _decimal_arctan(
            Decimal(1) / 239
        )
        _MACHIN_PI_BY_PRECISION[precision] = cached
    return cached


def student_t_absolute_cdf_closed_form(t: Decimal, degrees_of_freedom: int) -> Decimal:
    """P(|T| <= t) by the exact Abramowitz & Stegun finite forms.

    26.7.3 (odd df) and 26.7.4 (even df) are FINITE sums, exact for every
    integer df, and they share no code with the incomplete-beta continued
    fraction that `student_t_quantile` inverts.  `theta = arctan(t / sqrt(df))`,
    so `cos^2(theta) = df / (df + t^2)` and `sin(theta) = t / sqrt(df + t^2)`
    are algebraic; only the odd-df `theta` term needs a transcendental.
    """

    df = degrees_of_freedom
    df_decimal = Decimal(df)
    cos_squared = df_decimal / (df_decimal + t * t)
    cos_theta = cos_squared.sqrt()
    sin_theta = t / (df_decimal + t * t).sqrt()
    if df % 2 == 0:
        # 26.7.4: sin(theta) * [1 + (1/2)cos^2 + (1*3)/(2*4) cos^4 + ...]
        total = Decimal(1)
        coefficient = Decimal(1)
        power = Decimal(1)
        for k in range(1, df // 2):
            coefficient *= Decimal(2 * k - 1) / Decimal(2 * k)
            power *= cos_squared
            total += coefficient * power
        return sin_theta * total
    theta = _decimal_arctan(t / df_decimal.sqrt())
    if df == 1:
        return 2 * theta / _machin_pi()
    # 26.7.3: (2/pi) * [theta + sin(theta) * (cos + (2/3)cos^3 + ...)]
    coefficient = Decimal(1)
    power = cos_theta
    inner = power
    for k in range(1, (df - 1) // 2):
        coefficient *= Decimal(2 * k) / Decimal(2 * k + 1)
        power *= cos_squared
        inner += coefficient * power
    return 2 * (theta + sin_theta * inner) / _machin_pi()


def student_t_quantile_closed_form(probability: str, degrees_of_freedom: int) -> Decimal:
    """The same quantile, inverted from the A&S closed form instead."""

    with localcontext() as context:
        context.prec = DECIMAL_WORK_PRECISION
        target = 2 * Decimal(probability) - 1
        low, high = Decimal(0), Decimal(100)
        for _ in range(300):
            middle = (low + high) / 2
            if student_t_absolute_cdf_closed_form(middle, degrees_of_freedom) < target:
                low = middle
            else:
                high = middle
        return +((low + high) / 2)


def _agreement_digits(left: Decimal, right: Decimal) -> int:
    """Significant decimal digits on which two positive values agree."""

    if left == right:
        return DECIMAL_WORK_PRECISION
    with localcontext() as context:
        context.prec = DECIMAL_WORK_PRECISION
        relative = abs(left - right) / abs(left)
        return int(-relative.log10())


def build_quantile_proof(degrees_of_freedom: int) -> dict[str, Any]:
    """Prove the REALIZED df's quantiles two ways, or refuse (pre-registration).

    (i) forward check: the survival function evaluated AT the returned quantile
    reproduces `1 - p`; (ii) independent route: the A&S closed form, inverted by
    its own bisection, agrees with the continued-fraction quantile.  Neither
    check can pass on a quantile the other route would not produce.
    """

    quantiles: dict[str, str] = {}
    residuals: dict[str, str] = {}
    agreement: dict[str, int] = {}
    for probability in QUANTILE_PROOF_PROBABILITIES:
        value = student_t_quantile(probability, degrees_of_freedom)
        with localcontext() as context:
            context.prec = DECIMAL_WORK_PRECISION
            residual = abs(
                student_t_survival(value, degrees_of_freedom)
                - (Decimal(1) - Decimal(probability))
            )
        independent = student_t_quantile_closed_form(probability, degrees_of_freedom)
        digits = _agreement_digits(value, independent)
        if residual > QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL:
            raise PrepareRefusal(
                f"quantile_proof_failed: df {degrees_of_freedom} p {probability} "
                f"forward residual {residual} exceeds "
                f"{QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL}"
            )
        if digits < QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS:
            raise PrepareRefusal(
                f"quantile_proof_failed: df {degrees_of_freedom} p {probability} "
                f"closed-form agreement {digits} digits is below "
                f"{QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS}"
            )
        quantiles[probability] = str(
            +value.quantize(Decimal(1).scaleb(-20), rounding=ROUND_HALF_EVEN)
        )
        residuals[probability] = f"{residual:.3E}"
        agreement[probability] = digits
    return {
        "degrees_of_freedom": degrees_of_freedom,
        "probabilities": list(QUANTILE_PROOF_PROBABILITIES),
        "quantiles": quantiles,
        "forward_residuals": residuals,
        "forward_residual_bound": str(QUANTILE_PROOF_MAXIMUM_FORWARD_RESIDUAL),
        "closed_form_agreement_digits": agreement,
        "closed_form_agreement_bound": QUANTILE_PROOF_MINIMUM_AGREEMENT_DIGITS,
        "closed_form_method": (
            "Abramowitz & Stegun 26.7.3 (odd df) / 26.7.4 (even df) finite "
            "closed form, inverted by bisection; pi by Machin's formula"
        ),
        "precision": DECIMAL_WORK_PRECISION,
        "bounds_origin": (
            "issuer-declared bounds, stated in the pre-registration's "
            "quantile-proof clause and recorded here in the candidate: a "
            "forward residual of at most 1e-30 and agreement of at least 30 "
            "significant digits between the two routes, each chosen tighter "
            "than the 20 published digits the artifact records and looser than "
            "the agreement the implementation realizes"
        ),
    }


def two_draw_prediction_lexeme(quantile: Decimal, sample_sd_lexeme: str) -> str:
    """r6's rule verbatim: the binary64 product's shortest round-tripping decimal.

    Python's `repr` of a float IS that shortest round-tripping decimal; the
    sealed rule string states the property, and this docstring must not drift
    from it.
    """

    return repr(float(quantile) * float(sample_sd_lexeme) * math.sqrt(2))


def _repo_relative_custody(custody_locator: str, attempt_id: str, repo_root: Path) -> str:
    """The member's evidence directory as r6 stores it: relative to the repo.

    Both consumers join it back with `repo_root / member["source_directory"]`
    (`tests/verify_calibration_acceptance_corpus.py`,
    `scripts/reissue_calibration_acceptance.py`), and `pathlib` DISCARDS the
    root when the right operand is absolute -- so an absolute path here would
    verify on this machine and on no other, silently.
    """

    try:
        return Path(custody_locator).resolve().relative_to(Path(repo_root).resolve()).as_posix()
    except ValueError as error:
        raise PrepareRefusal(
            f"member {attempt_id}: custody {custody_locator} lies outside the "
            "repository, so no repo-relative source_directory exists"
        ) from error


def _plain(value: Decimal) -> str:
    """A Decimal in plain notation; `str` would give "1E-15" for a quantum."""

    return format(value, "f")


def envelope_screen(quantized_range: Decimal, floor: Decimal) -> Decimal:
    """D-125's screen arm: `S = max(quantized range, floor)`.

    A pure function so BOTH operands can be exercised: with the real corpus the
    floor arm is the norm, and a collapse to either operand alone is a screen
    that either falls below the D-125 floor or ignores the corpus entirely.
    """

    return max(quantized_range, floor)


def envelope_ceiling(predecessor_ceiling: Decimal, own_q99: Decimal) -> Decimal:
    """D-125 cl.2's ceiling arm: `C = max(predecessor ceiling, own Q99)`.

    Pure for the same reason, and here it is the only way to exercise the
    predecessor arm at all: r6's ceiling (0.010164834757777545) sits below the
    0.010818 screen floor, so through the CLI the predecessor can never win the
    max without failing strict `S < C` first.  A successor generation's
    predecessor will not have that property.
    """

    return max(predecessor_ceiling, own_q99)


# The pre-registration states the two machine facts a change to which VOIDS the
# registration.  They are parsed out of the file the caller names, by strict
# patterns, so the campaign's own text is the authority rather than a constant
# restated here.  Exactly one match each: absent or ambiguous refuses.
_PREREGISTRATION_OS_BUILD = re.compile(r"os_build:\s*([A-Za-z0-9._-]+)")
_PREREGISTRATION_POWERMETRICS = re.compile(
    r"/usr/bin/powermetrics sha256 in force is\s+([0-9a-f]{64})"
)


def preregistration_epoch_pins(text: str) -> tuple[str, str]:
    """The `os_build` and `powermetrics` sha256 the campaign is registered under."""

    pins: list[str] = []
    for label, pattern in (
        ("os_build", _PREREGISTRATION_OS_BUILD),
        ("powermetrics sha256", _PREREGISTRATION_POWERMETRICS),
    ):
        found = set(pattern.findall(text))
        if len(found) != 1:
            raise PrepareRefusal(
                f"pre-registration: {label} is "
                + ("absent" if not found else f"ambiguous ({len(found)} values)")
                + "; the registration's machine identity cannot be established"
            )
        pins.append(found.pop())
    return pins[0], pins[1]


def rederivation_triggers(corpus_doubling_trigger: str) -> set[str]:
    """The trigger set the production validator demands for a given row.

    One home for the rule, so the artifact's list and the validator's expected
    set cannot drift: `calibration_bracketing._valid_acceptance_bound` builds
    the same five names around the registered row's own
    `corpus_doubling_trigger`.
    """

    return {
        "identity_field_change",
        "protocol_or_estimator_byte_change",
        "new_valid_same_identity_capture_expands_observed_range",
        corpus_doubling_trigger,
        "new_systematic_failure_challenges_preflight_screen",
    }


def default_acceptance_id(corpus_n: int, identity_epoch: Mapping[str, Any]) -> str:
    """Name the artifact after the corpus and the REALIZED epoch.

    Interpolating the corpus size while hardcoding the OS build would mislabel
    every run under any other epoch, which is the one fact the artifact exists
    to bind.
    """

    os_build = identity_epoch.get("os_build")
    if not isinstance(os_build, str) or not os_build:
        raise PrepareRefusal("identity epoch carries no os_build to name the artifact")
    return f"d079_calibration_acceptance_v2_n{corpus_n}_{os_build.lower()}_r1"


# The generation-row fields the registry stores as TUPLES.  JSON has no tuple,
# so the emitted artifact serialises them as arrays; anything that hands the row
# to `_registered_generation_row_is_complete` -- the future registration in
# `_D102_GENERATION_DERIVATIONS`, and the tests -- must convert first, or S3's
# `isinstance(..., tuple)` fences refuse the row silently.  This function is
# that conversion's ONE home, on the emitting side, so the transaction seat
# inherits it instead of reinventing it.
GENERATION_ROW_TUPLE_FIELDS = ("epoch_catalog_ids", "registration_session_ids")


def generation_row_for_registry(row: Mapping[str, Any]) -> dict[str, Any]:
    """The emitted row in the exact shape `_D102_GENERATION_DERIVATIONS` takes."""

    converted = dict(row)
    for field in GENERATION_ROW_TUPLE_FIELDS:
        converted[field] = tuple(converted[field])
    return converted


class PrepareRefusal(Exception):
    """A fail-closed refusal: nothing is written and the reason is printed."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def _read_member_evidence(observation: LedgerObservation) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Read a member's primary bytes and authenticate them against its row.

    The ledger row is the custody authority: its `artifact_sha256` was written
    at finalization, so a bundle whose bytes moved afterwards refuses here
    rather than becoming a corpus member.
    """

    custody = Path(observation.custody_locator)
    try:
        observed = artifact_hashes(custody)
    except OSError as error:
        raise PrepareRefusal(
            f"member {observation.attempt_id}: custody unreadable ({error})"
        ) from error
    registered = dict(observation.artifact_sha256)
    for name in ("manifest.json", "instrument_evidence.json"):
        if name not in registered or observed.get(name) != registered.get(name):
            raise PrepareRefusal(
                f"member {observation.attempt_id}: {name} does not match the ledger row"
            )
    try:
        evidence = json.loads(
            (custody / "instrument_evidence.json").read_text(encoding="utf-8"),
            parse_float=str,
            parse_int=str,
        )
        manifest = json.loads(
            (custody / "manifest.json").read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as error:
        raise PrepareRefusal(
            f"member {observation.attempt_id}: primary bytes unparseable ({error})"
        ) from error
    if not isinstance(evidence, Mapping) or not isinstance(manifest, Mapping):
        raise PrepareRefusal(
            f"member {observation.attempt_id}: primary bytes are not JSON objects"
        )
    return evidence, manifest


def anchor_v3_replay_outcome(evidence: Mapping[str, Any]) -> tuple[bool, str | None]:
    """Whether the recorded anchor-v3 replay RESOLVED, and its refusal detail.

    A derivation-only capture stores its own anchor-v3 record in the hashed
    `instrument_evidence.json` (ruling 46 R-d: a fresh v3 capture stores its own
    value), so the replay outcome is read from primary bytes rather than
    recomputed from the trace.  An anchor recorded under any other method is not
    an anchor-v3 replay at all and refuses rather than counting as resolved.
    """

    anchor = evidence.get("clock_anchor")
    if not isinstance(anchor, Mapping) or anchor.get("method") != CLOCK_METHOD_V3:
        return False, "anchor_method_not_v3"
    if anchor.get("reason") == CLOCK_ANCHOR_UNRESOLVED or anchor.get("status") == "unknown":
        detail = anchor.get("detail")
        return False, detail if isinstance(detail, str) else "clock_anchor_unresolved"
    if evidence.get("clock_anchor_resolved") is not True:
        return False, "clock_anchor_not_marked_resolved"
    return True, None



def _authenticated_predecessor(path: Path) -> Mapping[str, Any]:
    """Load r6 through the production exact-byte loader, or refuse."""

    acceptance = load_calibration_acceptance_bound(path)
    if acceptance is None or acceptance.get("artifact_role") != "issued":
        raise PrepareRefusal(f"predecessor: {path} is not an authenticated issued acceptance")
    operatives = acceptance.get("decimal_derivation", {}).get("ratified_operatives")
    if not isinstance(operatives, Mapping) or not isinstance(
        operatives.get("maximum_budgetable_drift_s"), str
    ):
        raise PrepareRefusal("predecessor: no ratified maximum_budgetable_drift_s")
    return acceptance


# A ledger session is TERMINAL when no further slot can be filled: its last
# declared slot finalized, or an explicit abort closed it.  While a session is
# open the corpus is still being captured, and the pre-registration forbids
# examining any member value, screen or statistic until every session of the
# registration is terminal.
TERMINAL_SESSION_STATES = frozenset({"finalized", "aborted"})


def refuse_open_registration(snapshot: Any, session_ids: Sequence[str]) -> None:
    """BLINDNESS: refuse while any registration session is still open.

    This runs BEFORE the generic ledger-refusal check and before any row is
    read, because an open derivation session is exactly the mid-campaign state
    every snapshot consumer tolerates as the physical/pin gap (CG46 A7) -- so
    without this gate the tool would happily compute and PRINT the corpus size,
    the screen and the ceiling between capture nights, and the remaining nights
    could no longer honestly be said to have run "regardless of interim values".
    Reporting the open session by name also beats the ledger's opaque
    `calibration_ledger_bracket_session_open`, which is why it precedes it.
    """

    for session_id in session_ids:
        session = snapshot.bracket_session_by_id.get(session_id)
        if session is not None and session.state not in TERMINAL_SESSION_STATES:
            raise PrepareRefusal(
                f"registration: session {session_id} is {session.state!r}, not "
                "terminal; nothing is computed or reported before every session "
                "of the registration is terminal (pre-registration, Blindness)"
            )


def _registration_observations(
    snapshot: Any, session_ids: Sequence[str]
) -> tuple[LedgerObservation, ...]:
    """Every observation of the registration's derivation-kind sessions."""

    if not session_ids:
        raise PrepareRefusal("registration: no --registration-session-id given")
    by_id = snapshot.bracket_session_by_id
    for session_id in session_ids:
        session = by_id.get(session_id)
        if session is None:
            raise PrepareRefusal(f"registration: session {session_id} is not in the ledger")
        if session.session_kind != SESSION_KIND_DERIVATION:
            raise PrepareRefusal(
                f"registration: session {session_id} is kind {session.session_kind!r}, "
                "not a derivation session"
            )
    registration = set(session_ids)
    return tuple(
        observation
        for observation in snapshot.observations
        if observation.bracket_session_id in registration
    )


def _select_members(
    observations: Iterable[LedgerObservation],
    repo_root: Path,
    level_screen_threshold: Decimal,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], list[dict[str, Any]]]:
    """Split the registration's VALID rows into members and named exclusions.

    Membership turns on the replay outcome and nothing else: no value is
    consulted, so the corpus cannot be fitted to the screen it will set.
    """

    members: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    comparisons: list[dict[str, Any]] = []
    for observation in sorted(observations, key=lambda row: row.sequence):
        if observation.classification_disposition != "valid":
            continue
        evidence, _manifest = _read_member_evidence(observation)
        resolved, detail = anchor_v3_replay_outcome(evidence)
        entry = {
            "member_id": observation.attempt_id,
            "manifest_sha256": observation.artifact_sha256["manifest.json"],
            "instrument_evidence_sha256": observation.artifact_sha256[
                "instrument_evidence.json"
            ],
        }
        if not resolved:
            if detail not in REGISTERED_CORPUS_EXCLUSION_REASONS:
                raise PrepareRefusal(
                    f"member {observation.attempt_id}: unregistered exclusion "
                    f"mechanism {detail!r}"
                )
            excluded.append({**entry, "reason": detail})
            continue
        lexeme = evidence.get("b_fiducial_s")
        if not isinstance(lexeme, str) or observation.exact_bound_lexeme_s != lexeme:
            raise PrepareRefusal(
                f"member {observation.attempt_id}: primary b_fiducial_s does not "
                "match the ledger row's exact bound lexeme"
            )
        members.append({**entry, "b_fiducial_s": lexeme,
                        "source_directory": _repo_relative_custody(
                            observation.custody_locator, observation.attempt_id,
                            repo_root,
                        ),
                        "content_id": observation.content_id})
        comparisons.append(
            {
                "member_id": observation.attempt_id,
                "b_fiducial_s": lexeme,
                "exceeds_prior_level_screen": Decimal(lexeme)
                > level_screen_threshold,
            }
        )
    return members, excluded, comparisons


def _corpus_statistics(members: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Decimal statistics exactly as r6, at an explicit working precision."""

    values = [Decimal(member["b_fiducial_s"]) for member in members]
    ids = [member["member_id"] for member in members]
    with localcontext() as context:
        context.prec = DECIMAL_WORK_PRECISION
        count = Decimal(len(values))
        mean = sum(values, Decimal(0)) / count
        sample_sd = (
            sum((value - mean) ** 2 for value in values) / (count - 1)
        ).sqrt()
        return {
            "minimum_s": str(min(values)),
            "minimum_member_id": ids[values.index(min(values))],
            "maximum_s": str(max(values)),
            "maximum_member_id": ids[values.index(max(values))],
            "range_s": str(max(values) - min(values)),
            "mean_presentation_s": {
                "value": str(mean.quantize(PRESENTATION_QUANTUM_S, rounding=ROUND_HALF_EVEN)),
                "label": "rounded_presentation",
                "rounding_rule": "ROUND_HALF_EVEN to quantum 0.000000000000000001 s",
            },
            "sample_sd_presentation_s": {
                "value": str(sample_sd.quantize(PRESENTATION_QUANTUM_S, rounding=ROUND_HALF_EVEN)),
                "label": "rounded_presentation",
                "rounding_rule": "ROUND_HALF_EVEN to quantum 0.000000000000000001 s",
            },
        }


def prepare_candidate(args: argparse.Namespace) -> int:
    try:
        payload = _prepare_candidate(args)
    except PrepareRefusal as refusal:
        print(f"REFUSED: {refusal.reason}")
        return 3
    out = Path(args.out)
    out.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"candidate written (NOT ISSUED): {out}")
    print(f"corpus n: {payload['derivation_corpus']['n']}")
    print(f"screen_rule: {payload['registered_generation_row']['screen_rule']}")
    return 0


def _prepare_candidate(args: argparse.Namespace) -> dict[str, Any]:
    # The D-125 reference is a PRE-condition, not a field to backfill: without
    # it the successor derivation would settle D-125 implicitly (ruling 46 V7).
    if not args.d125_ruling:
        raise PrepareRefusal("d125_ruling reference absent; refusing to emit (ruling 46 V7)")
    minimum = args.minimum_corpus_size
    # The pre-registration names exactly ONE alternative floor, and CG46 A-2
    # names the same one: "Ed may instead rule in writing that n = 17 is
    # acceptable".  A ruling reference is therefore not a licence to pick any
    # number -- it licenses 17 and nothing else, or an n = 3 corpus would issue
    # behind a one-word string.
    if minimum != SUCCESSOR_MINIMUM_CORPUS_SIZE:
        if minimum != RULED_ALTERNATIVE_CORPUS_SIZE:
            raise PrepareRefusal(
                f"--minimum-corpus-size {minimum} is not a ruled floor: the only "
                f"values are {SUCCESSOR_MINIMUM_CORPUS_SIZE} (default) and "
                f"{RULED_ALTERNATIVE_CORPUS_SIZE} with --ed-ruling "
                "(pre-registration Stopping; CG46 addendum A-2)"
            )
        if not args.ed_ruling:
            raise PrepareRefusal(
                f"corpus-size floor departure to {minimum} requires --ed-ruling "
                f"(D-126 cl.2 SUCCESSOR_MINIMUM_CORPUS_SIZE = {SUCCESSOR_MINIMUM_CORPUS_SIZE})"
            )
    preregistration = Path(args.preregistration)
    try:
        preregistration_bytes = preregistration.read_bytes()
    except OSError as error:
        raise PrepareRefusal(f"pre-registration unreadable: {error}") from error
    preregistration_sha256 = hashlib.sha256(preregistration_bytes).hexdigest()
    # B-3: the arm materials carry the digest of the text the campaign was armed
    # under.  Without this pin the tool would derive against whatever the file
    # says TODAY, which is exactly the edit a pre-registration exists to forbid.
    if preregistration_sha256 != args.preregistration_sha256:
        raise PrepareRefusal(
            f"pre-registration sha256 {preregistration_sha256} does not match the "
            f"pinned {args.preregistration_sha256}; not issued"
        )
    registered_os_build, registered_powermetrics = preregistration_epoch_pins(
        preregistration_bytes.decode("utf-8", errors="replace")
    )

    snapshot = load_calibration_ledger_snapshot(
        args.ledger,
        args.head_pin,
        require_committed_pin=True,
        verify_custody=False,
        mode="read_replay",
        repo_root=Path(args.repo_root),
    )
    session_ids = tuple(args.registration_session_id)
    refuse_open_registration(snapshot, session_ids)
    if snapshot.refusal_reasons:
        raise PrepareRefusal("ledger: " + ", ".join(snapshot.refusal_reasons))
    predecessor = _authenticated_predecessor(Path(args.predecessor_acceptance))
    predecessor_statistics = predecessor["decimal_derivation"]["source_statistics"]
    level_screen_threshold = Decimal(
        predecessor["decimal_derivation"]["ratified_operatives"][
            "preflight_level_screen_s"
        ]
    )
    # The A-4 literal describes THIS predecessor's corpus; if it ever stops
    # doing so, the diagnostic it feeds is meaningless and the run refuses
    # rather than reporting against a number from another generation.
    with localcontext() as context:
        context.prec = DECIMAL_WORK_PRECISION
        recomputed = Decimal(predecessor_statistics["maximum_s"]) + Decimal(
            predecessor_statistics["range_s"]
        )
    if recomputed != R6_MAXIMUM_PLUS_RANGE_S:
        raise PrepareRefusal(
            f"predecessor maximum plus range {recomputed} does not equal the "
            f"ruled diagnostic {R6_MAXIMUM_PLUS_RANGE_S} (CG46 addendum A-4); "
            "not issued"
        )

    observations = _registration_observations(snapshot, session_ids)
    # The TARGET epoch is the registration's own, read from its rows before any
    # value is looked at, and it must be unanimous.
    if not observations:
        raise PrepareRefusal("registration: its sessions hold no observations")
    target_epoch = dict(observations[0].identity_epoch)
    for observation in observations:
        if dict(observation.identity_epoch) != target_epoch:
            raise PrepareRefusal("registration: rows disagree on the identity epoch")
    # B-2: the corpus is bound to the pre-registered SHAPE -- three nights of
    # twelve declared slots -- because a corpus assembled from a different
    # schedule is a different experiment, whatever its statistics say.
    if len(session_ids) != PREREGISTERED_NIGHT_COUNT and not args.nights_ruling:
        raise PrepareRefusal(
            f"registration names {len(session_ids)} sessions, not the "
            f"pre-registered {PREREGISTERED_NIGHT_COUNT}; --nights-ruling must "
            "name a written ruling to depart"
        )
    if not args.slot_count_ruling:
        for session_id in session_ids:
            declared = len(snapshot.bracket_session_by_id[session_id].declared_slots)
            if declared != PREREGISTERED_SLOTS_PER_NIGHT:
                raise PrepareRefusal(
                    f"session {session_id} declared {declared} slots, not the "
                    f"pre-registered {PREREGISTERED_SLOTS_PER_NIGHT}; "
                    "--slot-count-ruling must name a written ruling to depart"
                )
    # B-1: a change to either machine fact VOIDS the registration, so the rows
    # this corpus is built from must carry the identity the campaign was
    # registered under -- read from the text, not from a constant here.
    observed_powermetrics = {
        observation.t1_bindings.get("powermetrics_sha256")
        for observation in observations
    }
    if target_epoch.get("os_build") != registered_os_build:
        raise PrepareRefusal(
            f"registration os_build {target_epoch.get('os_build')!r} is not the "
            f"pre-registered {registered_os_build!r}; the registration is void"
        )
    if observed_powermetrics != {registered_powermetrics}:
        raise PrepareRefusal(
            "registration powermetrics sha256 "
            + ", ".join(sorted(str(item) for item in observed_powermetrics))
            + f" is not the pre-registered {registered_powermetrics}; the "
            "registration is void"
        )
    members, excluded, comparisons = _select_members(
        observations, Path(args.repo_root), level_screen_threshold
    )
    n = len(members)
    # Addendum A-7: a valid row carrying the TARGET epoch that belongs to no
    # session of this registration is not silently left out of the corpus --
    # issuance refuses, because absorbing it would enlarge the corpus past the
    # pre-registration and ignoring it would hide a capture the successor's own
    # epoch produced.  Either way it is Ed's call, not the issuer's.
    registration = set(session_ids)
    foreign = [
        observation.attempt_id
        for observation in snapshot.observations
        if observation.classification_disposition == "valid"
        and observation.bracket_session_id not in registration
        and dict(observation.identity_epoch) == target_epoch
    ]
    if foreign:
        raise PrepareRefusal(
            "valid same-epoch observations outside this registration: "
            + ", ".join(sorted(foreign))
            + "; not issued (ruling 46 addendum A-7)"
        )
    if n < minimum:
        raise PrepareRefusal(
            f"retained corpus n = {n} is below the required floor {minimum}; not issued"
        )

    challenged = [row for row in comparisons if row["exceeds_prior_level_screen"]]
    statistics = _corpus_statistics(members)
    if len(challenged) >= SCREEN_CHALLENGE_MEMBER_LIMIT:
        raise PrepareRefusal(
            f"screen challenge: {len(challenged)} retained members exceed "
            f"{level_screen_threshold}; not issued, Ed rules in writing"
        )

    degrees_of_freedom = n - 1
    with localcontext() as context:
        context.prec = DECIMAL_WORK_PRECISION
    # The pre-registration refuses to issue on a df whose quantile is not
    # proven in the artifact's own record, so the proof is computed BEFORE the
    # predictions that depend on it, and its failure is a refusal.
    quantile_proof = build_quantile_proof(degrees_of_freedom)
    with localcontext() as context:
        context.prec = DECIMAL_WORK_PRECISION
        t975 = student_t_quantile("0.975", degrees_of_freedom)
        t995 = student_t_quantile("0.995", degrees_of_freedom)
    sample_sd_lexeme = statistics["sample_sd_presentation_s"]["value"]
    prediction_95 = two_draw_prediction_lexeme(t975, sample_sd_lexeme)
    prediction_99 = two_draw_prediction_lexeme(t995, sample_sd_lexeme)

    quantized_range = Decimal(statistics["range_s"]).quantize(
        BRACKET_SCREEN_QUANTUM_S, rounding=ROUND_HALF_EVEN
    )
    screen = envelope_screen(quantized_range, D125_SCREEN_FLOOR_S)
    floor_bound = screen != quantized_range
    # The NAME is the pre-registered rule, not the arm of the `max` that won.
    screen_rule = SCREEN_RULE_FLOORED_RANGE_ENVELOPE
    predecessor_operatives = predecessor["decimal_derivation"]["ratified_operatives"]
    predecessor_ceiling = Decimal(predecessor_operatives["maximum_budgetable_drift_s"])
    ceiling = envelope_ceiling(predecessor_ceiling, Decimal(prediction_99))
    # D-125 / D-126 cl.3: the screen must sit STRICTLY below the ceiling, and
    # the refusal is never cured by lowering the screen (the floor binds it).
    if not screen < ceiling:
        raise PrepareRefusal(
            "successor_screen_exceeds_budget_ceiling: screen "
            f"{screen} is not strictly below the budget ceiling {ceiling}; "
            "not issued, Ed rules in writing"
        )
    level_screen = Decimal(statistics["maximum_s"]).quantize(
        PREFLIGHT_LEVEL_SCREEN_QUANTUM_S, rounding=ROUND_HALF_EVEN
    )
    operatives = {
        "bracket_screen_s": str(screen),
        "preflight_level_screen_s": str(level_screen),
        "max_budgetable_excess_s": str(ceiling - screen),
        "maximum_budgetable_drift_s": str(ceiling),
    }

    identity_epoch = target_epoch
    predecessor_epoch = dict(predecessor["identity_epoch"])
    if predecessor_epoch == identity_epoch:
        raise PrepareRefusal(
            "registration: the target epoch equals the predecessor's; a successor "
            "generation would be a re-derivation, not an epoch bootstrap"
        )
    predecessor_catalog_id = next(
        (
            key
            for key, epoch in predecessor["prior_observation_set"]["epoch_catalog"].items()
            if dict(epoch) == predecessor_epoch
        ),
        None,
    )
    if predecessor_catalog_id is None:
        raise PrepareRefusal("predecessor: its epoch is not in its own catalog")
    target_catalog_id = args.epoch_catalog_id
    epoch_catalog = {
        predecessor_catalog_id: predecessor_epoch,
        target_catalog_id: identity_epoch,
    }
    if len(epoch_catalog) != 2:
        raise PrepareRefusal("epoch catalog: the target id collides with the predecessor's")

    # The pre-registration says a pending or unresolved attempt in the prefix
    # REFUSES issuance.  Dropping it instead would present a prior set that
    # silently disagrees with the ledger it claims to be the complete history
    # of, and hand the transaction an opaque validator refusal later.
    unresolved = [
        observation.attempt_id
        for observation in snapshot.observations
        if observation.content_id is None
        or observation.classification_disposition not in PRIOR_SET_DISPOSITIONS
    ]
    if unresolved:
        raise PrepareRefusal(
            "prior set holds pending or unresolved attempts: "
            + ", ".join(sorted(unresolved))
            + "; not issued (pre-registration, Prospective use)"
        )
    # The catalog has exactly two entries, so `epoch_id` is a two-way choice --
    # and a two-way choice made with `else` silently LABELS anything it does not
    # recognise.  A row captured under a third identity epoch (a further OS
    # update mid-campaign, or a corrupted row) would enter the prior set wearing
    # the predecessor's catalog id, and every downstream check would agree with
    # the lie.  Refuse instead, before the labelling happens.
    foreign_epoch = [
        observation.attempt_id
        for observation in snapshot.observations
        if observation.content_id is not None
        and dict(observation.identity_epoch) not in (identity_epoch, predecessor_epoch)
    ]
    if foreign_epoch:
        raise PrepareRefusal(
            "prior set: attempt "
            + ", ".join(sorted(foreign_epoch))
            + " carries an identity epoch that is neither the target's nor the "
            "predecessor's; not issued"
        )
    prior_observations = [
        {
            "content_id": observation.content_id,
            "epoch_id": (
                target_catalog_id
                if dict(observation.identity_epoch) == identity_epoch
                else predecessor_catalog_id
            ),
            "disposition": observation.classification_disposition,
            "attempt_id": observation.attempt_id,
            "session_id": observation.bracket_session_id,
        }
        for observation in snapshot.observations
        if observation.content_id is not None
    ]
    # The production validator recomputes this inventory over the WHOLE prior
    # set, one entry per admissible disposition INCLUDING the zeros, and
    # compares for equality; a count over the registration alone, or with the
    # empty dispositions omitted, refuses.
    inventory = {
        disposition: sum(
            row["disposition"] == disposition for row in prior_observations
        )
        for disposition in sorted(PRIOR_SET_DISPOSITIONS)
    }
    cutoff = {
        "sequence": snapshot.head_sequence,
        "head_digest": snapshot.head_digest,
        "ledger_schema": snapshot.ledger_schema,
        "role": "issued_acceptance_baseline",
    }
    # The validator demands `member_ids == sorted(member_ids)`.
    member_table = [
        {
            "member_id": member["member_id"],
            "source_directory": member["source_directory"],
            "b_fiducial_s": member["b_fiducial_s"],
            "manifest_sha256": member["manifest_sha256"],
            "instrument_evidence_sha256": member["instrument_evidence_sha256"],
        }
        for member in sorted(members, key=lambda item: item["member_id"])
    ]
    generation_row = {
        "corpus_n": n,
        "corpus_doubling_trigger": f"corpus_doubles_from_{n}_to_{2 * n}",
        "prediction_95_two_draw_s": prediction_95,
        "prediction_99_two_draw_s": prediction_99,
        "operatives": operatives,
        "epoch_catalog_ids": sorted(epoch_catalog),
        "prior_prefix_mode": "import_plus_live",
        "prior_observation_count": len(prior_observations),
        "cutoff_sequence": snapshot.head_sequence,
        "screen_rule": screen_rule,
        "predecessor_ceiling_s": str(predecessor_ceiling),
        "predecessor_acceptance_id": predecessor["acceptance_id"],
        "registration_session_ids": list(session_ids),
        "d125_ruling": args.d125_ruling,
    }
    decimal_derivation = {
        "numeric_semantics": "decimal_source_lexemes",
        "source_statistics": {
            **statistics,
            "prediction_95_two_draw_s": prediction_95,
            "prediction_99_two_draw_s": prediction_99,
        },
        "rounding": {
            "mode": "ROUND_HALF_EVEN",
            "operative_bracket_screen": {
                "source": "decimal_derivation.source_statistics.range_s",
                # Plain decimal notation, not Decimal's scientific `str`:
                # the validator compares these against literal strings, and
                # `str(Decimal("0.000000000000001"))` is "1E-15".
                "quantum_s": _plain(BRACKET_SCREEN_QUANTUM_S),
                "value_s": operatives["bracket_screen_s"],
                "numeric_role": "operative_comparator",
                "floor_s": _plain(D125_SCREEN_FLOOR_S),
                "floor_bound": floor_bound,
            },
            "preflight_level_screen": {
                "source": "decimal_derivation.source_statistics.maximum_s",
                "quantum_s": _plain(PREFLIGHT_LEVEL_SCREEN_QUANTUM_S),
                "value_s": operatives["preflight_level_screen_s"],
                "numeric_role": "operative_comparator",
            },
        },
        "two_draw_prediction_derivation": {
            "rule": TWO_DRAW_PREDICTION_RULE,
            "degrees_of_freedom": degrees_of_freedom,
            "t_975_quantile": str(+t975.quantize(Decimal(1).scaleb(-20), rounding=ROUND_HALF_EVEN)),
            "t_995_quantile": str(+t995.quantize(Decimal(1).scaleb(-20), rounding=ROUND_HALF_EVEN)),
            "quantile_method": QUANTILE_METHOD,
        },
        "quantile_proof": quantile_proof,
        "ratified_operatives": {
            **operatives,
            "allowance_rule": "max(observed_drift_s,bracket_screen_s)",
            "operative_bound_rule": (
                "max(pre_b_fiducial_s,post_b_fiducial_s)+calibration_drift_allowance_s"
            ),
            "embedding_count": 1,
        },
    }
    derivation_notes = {
        "generation": (
            "D-079 epoch bootstrap: the first generation derived from live "
            "derivation-only captures under a new identity epoch."
        ),
        "predecessor": {
            "acceptance_id": predecessor["acceptance_id"],
            "relative_path": str(Path(args.predecessor_acceptance)),
            # Restated so the note identifies the predecessor by its BYTES, not
            # by a path that means nothing on another checkout.
            "file_sha256": hashlib.sha256(
                Path(args.predecessor_acceptance).read_bytes()
            ).hexdigest(),
            "derivation_sha256": predecessor.get("derivation_sha256"),
            "maximum_budgetable_drift_s": str(predecessor_ceiling),
            "relationship": (
                "envelope predecessor under D-125 cl.2: the successor ceiling is "
                "max(predecessor ceiling, own Q99) and can never fall"
            ),
        },
        "excluded_members": excluded,
        "prior_screen_comparison": comparisons,
        "rule_outcomes": {
            "d125_ruling": args.d125_ruling,
            "ed_ruling": args.ed_ruling,
            "minimum_corpus_size": minimum,
            "retained_n": n,
            "quantized_range_s": str(quantized_range),
            "screen_floor_bound": floor_bound,
            "screen_rule": screen_rule,
            "screen_challenge_member_count": len(challenged),
            "screen_challenge_threshold_s": str(level_screen_threshold),
            "new_maximum_exceeds_prior_maximum_plus_range": (
                Decimal(statistics["maximum_s"]) > R6_MAXIMUM_PLUS_RANGE_S
            ),
            "prior_maximum_plus_range_s": str(R6_MAXIMUM_PLUS_RANGE_S),
        },
        "preregistration": {
            "relative_path": str(preregistration),
            "file_sha256": preregistration_sha256,
        },
    }
    payload: dict[str, Any] = {
        "schema_version": ACCEPTANCE_BOUND_SCHEMA,
        "acceptance_id": args.acceptance_id or default_acceptance_id(n, identity_epoch),
        # The production validator demands exactly this pair; the D-079,
        # D-125 and D-126 provenance travels in `derivation_notes` and in the
        # row's `d125_ruling`, where it is machine-checked rather than decorative.
        "decision_ids": ["D-102", "D-109"],
        # NOT an issued artifact: the exact-byte production loader authenticates
        # `artifact_role` and a registry pin, so these bytes can never be loaded
        # as authority.  The flag says so in words as well.
        "candidate_not_issued": True,
        "artifact_role": "candidate",
        "issuance": {
            "status": "candidate_not_issued",
            "claim_eligible": False,
            "reason": (
                "prepared by scripts/issue_calibration_acceptance_generation.py "
                "prepare-candidate; issuance is the D-138 transaction's, after the "
                "cold science gate"
            ),
            # A reader must be able to act on the label without knowing which
            # boolean means what.  `licence` is a CANDIDATE-LABEL field: the
            # D-138 transaction rewrites the whole `issuance` block when it
            # issues, so this sentence cannot survive into an issued artifact
            # and quietly contradict it.
            "licence": CANDIDATE_LICENCE,
        },
        "ledger_cutoff": cutoff,
        "identity_epoch": identity_epoch,
        "prospective_rederivation": {
            "calendar_expiry": None,
            "trigger_observation_rule": "judge_under_prior_artifact_never_self_fit",
            # DERIVED from this generation's own row, never copied: the
            # corpus-doubling trigger is corpus-indexed, and a copied one names
            # the predecessor's corpus while the row names this one -- which the
            # production validator refuses on set equality, and which is a
            # self-contradictory scientific record besides.
            "triggers": sorted(
                rederivation_triggers(generation_row["corpus_doubling_trigger"])
            ),
            "protocol_sha256": protocol_sha256(PROTOCOL_ID),
            "estimator_code_sha256": {
                path: hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest()
                for path in ESTIMATOR_CODE_PATHS
            },
        },
        "derivation_corpus": {
            "selection": (
                "every observation of the registration's derivation-kind "
                "sessions whose ledger disposition is valid and whose stored "
                "anchor-v3 record, read from primary evidence bytes "
                "authenticated against its ledger row, reports a RESOLVED "
                "clock anchor; the member value is that bundle's own "
                "b_fiducial_s lexeme, cross-checked against the row's exact "
                "bound lexeme, and no value is re-derived here"
            ),
            "n": n,
            "members": member_table,
        },
        "prior_observation_set": {
            "cutoff": {key: cutoff[key] for key in ("sequence", "head_digest", "ledger_schema")},
            "content_identity_method": (
                "sha256(canonical_json({instrument_evidence.json,manifest.json} "
                "byte sha256s))"
            ),
            "epoch_catalog": epoch_catalog,
            "observations": prior_observations,
        },
        "decimal_derivation": decimal_derivation,
        "backfill_candidate": {
            "status": "candidate_not_issued",
            "candidate_inventory": inventory,
            "production_issuance_blocked": True,
            "required_verification": (
                "pending: cold science gate over exclusions, per-night "
                "diagnostics, the screen-challenge outcome and the D-125 default"
            ),
        },
        "derivation_notes": derivation_notes,
        "registered_generation_row": generation_row,
    }
    # Order matters: the input seal is part of the artifact, so it must be
    # present before the whole-artifact digest closes over it.
    payload["derivation_input_sha256"] = derivation_input_sha256(payload)
    payload["derivation_sha256"] = derivation_sha256(payload)
    return payload


def derivation_sha256(payload: Mapping[str, Any]) -> str:
    """The PRODUCTION recipe: canonical sha256 of the artifact minus this key.

    `calibration_bracketing._valid_acceptance_bound` builds the same `core`
    mapping and compares it through `_canonical_sha256`, so a curated digest of
    a chosen subset could never authenticate however sensible the subset.  The curated seal that IS
    useful -- stable under prose and label edits, moving on every derivation
    input -- is `derivation_input_sha256` below, emitted alongside it.
    """

    core = {key: item for key, item in payload.items() if key != "derivation_sha256"}
    return _canonical_sha256(core)


def derivation_input_sha256(payload: Mapping[str, Any]) -> str:
    """Digest every INPUT the derivation depends on, and nothing else.

    Prose, file paths and the candidate label stay out, so two preparations of
    the same corpus under the same rules digest equal.  Everything the
    derivation actually consumed stays IN -- the member lexemes, the statistics,
    the rounding rules, the quantile proof, the identity epoch, the ledger
    cutoff, the predecessor's identity and ceiling, and the D-125 reference --
    because the point of the digest is that a replay from different inputs
    cannot present itself as the same derivation.
    """

    derivation = payload["decimal_derivation"]
    row = payload["registered_generation_row"]
    sealed = {
        "acceptance_id": payload["acceptance_id"],
        "identity_epoch": payload["identity_epoch"],
        "ledger_cutoff": {
            "sequence": payload["ledger_cutoff"]["sequence"],
            "head_digest": payload["ledger_cutoff"]["head_digest"],
            "ledger_schema": payload["ledger_cutoff"]["ledger_schema"],
        },
        "corpus_member_values": [
            [member["member_id"], member["b_fiducial_s"]]
            for member in payload["derivation_corpus"]["members"]
        ],
        "source_statistics": derivation["source_statistics"],
        "rounding": derivation["rounding"],
        "two_draw_prediction_derivation": derivation["two_draw_prediction_derivation"],
        "quantile_proof": derivation["quantile_proof"],
        "ratified_operatives": derivation["ratified_operatives"],
        "screen_rule": row["screen_rule"],
        "predecessor_acceptance_id": row["predecessor_acceptance_id"],
        "predecessor_ceiling_s": row["predecessor_ceiling_s"],
        "d125_ruling": row["d125_ruling"],
    }
    return hashlib.sha256(
        json.dumps(sealed, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    ).hexdigest()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    watch = commands.add_parser(
        "check",
        help=(
            "read-only desk epoch watch, plus a blind registration dry run when "
            "--session-ids names one"
        ),
    )
    watch.add_argument(
        "--ledger", type=Path, default=DEFAULT_LEDGER_PATH,
        help="the append-only calibration observation ledger to read",
    )
    watch.add_argument(
        "--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH,
        help=(
            "the committed file naming the ledger row count and last digest "
            "consumers trust; it must match both Git and the physical ledger"
        ),
    )
    watch.add_argument(
        "--acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,
        help="the ACTIVE issued acceptance artifact whose epoch is compared",
    )
    watch.add_argument(
        "--preregistration", type=Path, default=None,
        help=(
            "compare the machine's observed powermetrics sha256 against the one "
            "this pre-registration is registered under; omitted, the watch "
            "output is unchanged"
        ),
    )
    watch.add_argument(
        "--session-ids", action="append", default=[],
        help=(
            "a derivation-kind ledger session to dry-run (repeatable); reports "
            "kinds, states and counts only, never a measured value"
        ),
    )
    prepare = commands.add_parser(
        "prepare-candidate",
        help="derive a NOT-ISSUED successor acceptance candidate from the ledger",
    )
    prepare.add_argument(
        "--ledger", type=Path, default=DEFAULT_LEDGER_PATH,
        help="the append-only calibration observation ledger to derive from",
    )
    prepare.add_argument(
        "--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH,
        help=(
            "the committed head pin; the whole history through it becomes the "
            "candidate's prior set, and its head becomes the ledger cutoff"
        ),
    )
    prepare.add_argument(
        "--repo-root", type=Path, default=REPO_ROOT,
        help=(
            "the checkout the ledger and the evidence bundles live in; member "
            "paths are recorded relative to it"
        ),
    )
    prepare.add_argument(
        "--preregistration", type=Path, required=True,
        help="the pre-registration this corpus was captured under",
    )
    prepare.add_argument(
        "--predecessor-acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,
        help="the predecessor issued acceptance whose ceiling the successor inherits",
    )
    prepare.add_argument(
        "--registration-session-id", action="append", default=[],
        help="a derivation-kind ledger session of this registration (repeatable)",
    )
    # Deliberately NOT `required=True`: an absent D-125 reference must produce
    # the ruled REFUSAL with its reason, not an argparse usage error.
    prepare.add_argument(
        "--d125-ruling", default=None,
        help=(
            "reference to the ruling that fixes the D-125 envelope rule for "
            "this generation; without it the derivation would settle D-125 by "
            "accident, so the command refuses"
        ),
    )
    prepare.add_argument(
        "--ed-ruling", default=None,
        help=(
            "reference to Ed's written ruling that a 17-member corpus is "
            f"acceptable; required with --minimum-corpus-size "
            f"{RULED_ALTERNATIVE_CORPUS_SIZE}, and licenses no other value"
        ),
    )
    prepare.add_argument(
        "--minimum-corpus-size", type=int, default=SUCCESSOR_MINIMUM_CORPUS_SIZE,
        help=(
            f"how many members the retained corpus must hold: "
            f"{SUCCESSOR_MINIMUM_CORPUS_SIZE} (the ratified floor) or "
            f"{RULED_ALTERNATIVE_CORPUS_SIZE} with --ed-ruling; no other value"
        ),
    )
    prepare.add_argument(
        "--preregistration-sha256", required=True,
        help=(
            "the sha256 of the pre-registration text the campaign was ARMED "
            "under; the run refuses if the file has changed since"
        ),
    )
    prepare.add_argument(
        "--nights-ruling", default=None,
        help=(
            "reference to a written ruling departing from the pre-registered "
            f"{PREREGISTERED_NIGHT_COUNT} capture nights"
        ),
    )
    prepare.add_argument(
        "--slot-count-ruling", default=None,
        help=(
            "reference to a written ruling departing from the pre-registered "
            f"{PREREGISTERED_SLOTS_PER_NIGHT} declared slots per night"
        ),
    )
    prepare.add_argument(
        "--epoch-catalog-id", default="d079_epoch_25g83",
        help=(
            "the name the candidate's epoch catalog gives the NEW identity "
            "epoch; it must not collide with the predecessor's entry"
        ),
    )
    prepare.add_argument(
        "--acceptance-id", default=None,
        help=(
            "override the artifact's id; the default names the corpus size and "
            "the realized OS build"
        ),
    )
    # No default: writing into configs/calibration is the D-138 transaction's
    # act, never this tool's, so the caller always names the destination.
    prepare.add_argument(
        "--out", type=Path, required=True,
        help=(
            "where to write the single candidate file; REQUIRED and without a "
            "default, so this tool cannot write into configs/calibration by "
            "omission"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "prepare-candidate":
        return prepare_candidate(args)
    return check(args)


if __name__ == "__main__":
    raise SystemExit(main())
