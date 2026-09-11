#!/usr/bin/env python3
"""Apply Ed's fixed EPOCH-EQUIVALENCE rule to one closed derivation night.

WHAT THIS TOOL IS FOR.  A macOS point release changed one identity field of the
machine (`os_build`), and the question that change raises is an instrument one:
did the new build move the clock-anchor bound, or did it not?  Directive issue
316 fixes the answer's shape BEFORE any capture: run one ordinary derivation
night and compare its retained values against the envelope ALREADY IN FORCE.
This tool is that comparison, and nothing else.

THE VOCABULARY, BUILT BEFORE IT IS USED.

A DERIVATION NIGHT is one `derivation`-kind ledger session: a reservation that
declares an ordered list of capture slots (`d01 .. d12` for a twelve-slot
night), each of which either finalizes a row or does not.  The night is CLOSED,
or TERMINAL, when no further slot can be filled -- its last declared slot
finalized (`finalized`), or an explicit abort closed it early (`aborted`,
typically because the quiet window ran out: `window_exhausted`).

A capture is RETAINED when two things hold, and it is excluded otherwise: its
ledger row's classification disposition is `valid`, AND the anchor-v3 replay
STORED IN ITS OWN AUTHENTICATED BYTES resolved.  "Resolved" means the capture
recorded a real clock anchor rather than a refusal; a capture whose anchor was
recorded under any other method, or was recorded unresolved, is not an
anchor-v3 replay at all.  Both tests are read through the issuer's own
functions (`_read_member_evidence`, `anchor_v3_replay_outcome`), so a bundle
whose bytes moved after finalization refuses here rather than being retained.
Slots that never produced a finalized row -- the window ran out (`unused
(window_exhausted)`) or the runner refused the slot (`no row`, the chain log's
`slot_refused`) -- are not captures and are listed as such.  RETAINED m is how
many captures are retained.

The REFERENCE ENVELOPE is the acceptance artifact in force,
`d079_calibration_acceptance_v2_n17_r6`: the bound the project's measurements
are already judged against.  It carries two comparators this tool uses.

The LEVEL SCREEN (`preflight_level_screen_s`) is the absolute bound above which
a single capture is refused before a measurement window opens.  Every retained
value must sit at or below it.

The BRACKET SCREEN (`bracket_screen_s`) is the drift below which a measurement
window passes without spending any of its error budget.  The night's SPREAD --
the largest retained value minus the smallest -- must sit at or below it.

RAW STATISTIC VERSUS OPERATIVE COMPARATOR.  The envelope's raw corpus maximum
and range are the statistics of the seventeen captures r6 was derived from.
The OPERATIVES are the numbers the validator actually measures with, and they
are not always the raw statistics: the bracket screen is quantized upward from
the raw range under the never-zero floor rule, and the level screen is
quantized from the raw maximum.  Issue 316 rules that where they differ, THE
OPERATIVE VALUE IS THE ONE USED.  This tool therefore prints both, with each
number's source, and compares against the operatives.  It refuses if the
artifact's own `ratified_operatives` and the validator's registered generation
row disagree about any of them, because then there is no single operative value
to compare against.

EPOCH EQUIVALENCE is the verdict this comparison produces:

  PASS          every retained value <= the level screen AND the night's
                spread <= the bracket screen.  The new build did not move the
                bound out of the envelope in force.
  FAIL          anything else.
  INCONCLUSIVE  fewer than six retained captures (m < 6).  Too few values to
                judge a spread; issue 316 directs one more equivalence night.

WHAT THIS TOOL NEVER DOES.  It never issues an acceptance, never continues one
onto a new epoch, never writes an addendum, never appends to the ledger, and
never writes anywhere under `configs/calibration/`.  It reads, compares, prints
and writes ONE JSON record to the path the caller names.  Acting on a PASS is a
separate, reviewed act by a human-authorized transaction.

All arithmetic is Decimal on the stored lexemes.  No value passes through a
float at any point, because a float round trip changes the seventeenth digit of
numbers whose comparison turns on it.
"""

from __future__ import annotations

import argparse
from decimal import Decimal, localcontext
import json
from pathlib import Path
import sys
from typing import Any, Mapping

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from joulewise.calibration_bracketing import (  # noqa: E402
    _D102_GENERATION_DERIVATIONS,
    ANCHOR_V3_R6_ACCEPTANCE_ID,
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    acceptance_generation_operatives,
    load_calibration_acceptance_bound,
)
from joulewise.calibration_ledger import (  # noqa: E402
    DEFAULT_HEAD_PIN_PATH,
    DEFAULT_LEDGER_PATH,
    SESSION_KIND_DERIVATION,
    load_calibration_ledger_snapshot,
)
from scripts.issue_calibration_acceptance_generation import (  # noqa: E402
    DECIMAL_WORK_PRECISION,
    PrepareRefusal,
    TERMINAL_SESSION_STATES,
    _read_member_evidence,
    anchor_v3_replay_outcome,
)


# Exit codes.  3 is the issuer's refusal code and means the same thing here:
# the tool would not judge.  4 and 5 are VERDICTS -- the tool judged and the
# night did not pass -- and are deliberately distinct from 3 so a caller can
# tell "I could not run the rule" from "I ran it and it failed".
REFUSAL_EXIT = 3
FAIL_EXIT = 4
INCONCLUSIVE_EXIT = 5

# Issue 316: "If m < 6 the check is INCONCLUSIVE."  Six retained values is the
# floor at which a spread means anything; below it the night is re-run.
MINIMUM_RETAINED_M = 6

# The three operatives whose two sources must agree before any comparison runs.
CROSSCHECKED_OPERATIVES = (
    "preflight_level_screen_s",
    "bracket_screen_s",
    "maximum_budgetable_drift_s",
)

# A path whose resolved parts contain this pair in sequence lives in the
# acceptance directory of SOME checkout, not only this one, so the guard holds
# for a worktree, a clone or a copy.
FORBIDDEN_OUT_PARTS = ("configs", "calibration")
# Issue 316 names the reference envelope by generation: "the acceptance in
# force, d079_calibration_acceptance_v2_n17_r6".  Any other generation --
# however well it authenticates -- carries different screens, and a caller
# who points `--acceptance` at the n19 predecessor would turn a FAIL into a
# PASS.  The id is pinned here; the path may vary (a clone's copy of the same
# bytes is the same generation).
REQUIRED_ACCEPTANCE_ID = ANCHOR_V3_R6_ACCEPTANCE_ID

VERDICT_PASS = "PASS"
VERDICT_FAIL = "FAIL"
VERDICT_INCONCLUSIVE = "INCONCLUSIVE"


class EquivalenceRefusal(Exception):
    """The tool will not judge, and writes nothing."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


def _refuse_out_path(out: Path, force: bool) -> None:
    """Refuse a destination that would write into an acceptance directory."""

    resolved = out.expanduser().resolve()
    # Compared case-folded (Unicode-aware, so LONG S folds to s): on a
    # case-insensitive filesystem (the default on macOS) `CONFIGS/CALIBRATION`
    # is the same directory as the forbidden one.
    parts = tuple(part.casefold() for part in resolved.parts)
    for index in range(len(parts) - 1):
        if parts[index : index + 2] == FORBIDDEN_OUT_PARTS:
            raise EquivalenceRefusal(
                f"--out {out} lies under {'/'.join(FORBIDDEN_OUT_PARTS)}; this "
                "tool never writes into an acceptance directory"
            )
    # And by identity, whatever the spelling: the parent must not BE this
    # checkout's acceptance directory.
    acceptance_dir = REPO_ROOT / FORBIDDEN_OUT_PARTS[0] / FORBIDDEN_OUT_PARTS[1]
    parent = resolved.parent
    if acceptance_dir.exists() and parent.exists() and parent.samefile(acceptance_dir):
        raise EquivalenceRefusal(
            f"--out {out} resolves into {acceptance_dir}; this tool never writes "
            "into an acceptance directory"
        )
    if resolved.exists() and not force:
        raise EquivalenceRefusal(
            f"--out {out} already exists; pass --force to overwrite it"
        )


def reference_envelope(acceptance_path: Path) -> dict[str, Any]:
    """Read the envelope in force from BOTH of its sources, or refuse.

    The artifact is loaded through the production exact-byte loader, so an
    edited acceptance file does not authenticate and never reaches a
    comparison.  The operatives are then read from the validator's own
    registered generation row through `acceptance_generation_operatives`, which
    itself refuses a bracket-screen crosswire, and the remaining operatives are
    compared field by field.  Disagreement is a REFUSAL rather than a choice:
    if the artifact and the code that measures with it hold different numbers,
    there is no single operative value the rule can name.
    """

    acceptance = load_calibration_acceptance_bound(acceptance_path)
    if acceptance is None:
        raise EquivalenceRefusal(
            f"acceptance {acceptance_path} did not authenticate through the "
            "production loader"
        )
    if acceptance.get("artifact_role") != "issued":
        raise EquivalenceRefusal(
            f"acceptance {acceptance_path} is not an ISSUED acceptance "
            f"(artifact_role {acceptance.get('artifact_role')!r})"
        )
    acceptance_id = acceptance.get("acceptance_id")
    if not isinstance(acceptance_id, str):
        raise EquivalenceRefusal(f"acceptance {acceptance_path} names no acceptance_id")
    if acceptance_id != REQUIRED_ACCEPTANCE_ID:
        raise EquivalenceRefusal(
            f"acceptance {acceptance_path} is generation {acceptance_id!r}; issue "
            f"316 fixes the reference envelope as {REQUIRED_ACCEPTANCE_ID!r} and "
            "no other generation's screens may stand in for it"
        )
    derivation = acceptance.get("decimal_derivation")
    if not isinstance(derivation, Mapping):
        raise EquivalenceRefusal(f"acceptance {acceptance_id}: no decimal_derivation")
    ratified = derivation.get("ratified_operatives")
    statistics = derivation.get("source_statistics")
    if not isinstance(ratified, Mapping) or not isinstance(statistics, Mapping):
        raise EquivalenceRefusal(
            f"acceptance {acceptance_id}: no ratified_operatives or no "
            "source_statistics"
        )
    try:
        registered = acceptance_generation_operatives(
            acceptance_id, acceptance=acceptance
        )
    except ValueError as error:
        raise EquivalenceRefusal(
            f"acceptance {acceptance_id}: artifact and registered generation "
            f"disagree ({error})"
        ) from error
    if registered is None:
        raise EquivalenceRefusal(
            f"acceptance {acceptance_id}: the validator registers no generation "
            "row for it, so it has no operatives to compare against"
        )
    for name in CROSSCHECKED_OPERATIVES:
        artifact_value = ratified.get(name)
        registered_value = registered.get(name)
        if (
            not isinstance(artifact_value, str)
            or not isinstance(registered_value, str)
            or artifact_value != registered_value
        ):
            raise EquivalenceRefusal(
                f"acceptance {acceptance_id}: artifact and registered generation "
                f"disagree on {name} ({artifact_value!r} vs {registered_value!r})"
            )
    # The corpus size is stated twice for the same reason, and cross-checked
    # the same way: a mismatch means one of the two sources is describing a
    # different generation.
    registry_row = _D102_GENERATION_DERIVATIONS.get(acceptance_id, {})
    registry_n = registry_row.get("corpus_n")
    corpus = acceptance.get("derivation_corpus")
    artifact_n = corpus.get("n") if isinstance(corpus, Mapping) else None
    if not isinstance(artifact_n, int) or artifact_n != registry_n:
        raise EquivalenceRefusal(
            f"acceptance {acceptance_id}: artifact and registered generation "
            f"disagree on corpus n ({artifact_n!r} vs {registry_n!r})"
        )
    for name in ("maximum_s", "range_s"):
        if not isinstance(statistics.get(name), str):
            raise EquivalenceRefusal(
                f"acceptance {acceptance_id}: source_statistics has no {name}"
            )
    return {
        "acceptance_id": acceptance_id,
        "acceptance_path": str(acceptance_path),
        "corpus_n": artifact_n,
        "raw_corpus_maximum_s": statistics["maximum_s"],
        "raw_corpus_range_s": statistics["range_s"],
        "level_screen_s": registered["preflight_level_screen_s"],
        "bracket_screen_s": registered["bracket_screen_s"],
        "maximum_budgetable_drift_s": registered["maximum_budgetable_drift_s"],
    }


def envelope_lines(envelope: Mapping[str, Any]) -> list[str]:
    """The constants table, every number carrying the source it came from."""

    registry = "validator registry _D102_GENERATION_DERIVATIONS operatives"
    artifact = "artifact decimal_derivation.source_statistics"
    lines = [
        "Reference envelope (the acceptance in force; issue 316)",
        f"  acceptance_id: {envelope['acceptance_id']}",
        f"  artifact: {envelope['acceptance_path']}",
        "    loaded by joulewise.calibration_bracketing."
        "load_calibration_acceptance_bound",
        f"  corpus n = {envelope['corpus_n']} "
        "(artifact derivation_corpus.n; registry corpus_n; they agree)",
        f"  raw corpus maximum_s = {envelope['raw_corpus_maximum_s']}  [{artifact}]",
        f"  raw corpus range_s   = {envelope['raw_corpus_range_s']}  [{artifact}]",
        f"  OPERATIVE level screen   preflight_level_screen_s   = "
        f"{envelope['level_screen_s']}  [{registry}]",
        f"  OPERATIVE bracket screen bracket_screen_s           = "
        f"{envelope['bracket_screen_s']}  [{registry}]",
        f"  budget ceiling           maximum_budgetable_drift_s = "
        f"{envelope['maximum_budgetable_drift_s']}  [{registry}]",
        "    artifact decimal_derivation.ratified_operatives agrees with the "
        "registry on all three, or this tool refuses",
    ]
    level_differs = envelope["level_screen_s"] != envelope["raw_corpus_maximum_s"]
    bracket_differs = envelope["bracket_screen_s"] != envelope["raw_corpus_range_s"]
    if level_differs or bracket_differs:
        lines.append(
            "    NOTE: the operative comparators differ from the raw statistics "
            "(quantization / never-zero floor); issue 316 rules the OPERATIVE "
            "value is the one compared against."
        )
    else:
        lines.append(
            "    NOTE: the operative comparators equal the raw statistics for "
            "this generation."
        )
    return lines


def _slot_outcomes(session: Any) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """One outcome per DECLARED slot, in declared order, plus the retained set.

    Declared order, not finalized order, because a night's record must show the
    slots that produced nothing as well as the slots that did: a check that
    listed only the rows it found could not tell a twelve-slot night that
    retained seven from a seven-slot night.
    """

    outcomes: list[dict[str, Any]] = []
    retained: list[dict[str, str]] = []
    window_exhausted = (
        session.state == "aborted" and session.abort_reason == "window_exhausted"
    )
    for slot in session.declared_slots:
        observation = session.finalized_slots.get(slot)
        if observation is None:
            # No finalized row at all.  Either the window ran out before this
            # slot (the pre-registration's planned early close) or the runner
            # refused it; neither is a capture.
            outcomes.append(
                {
                    "slot": slot,
                    "outcome": "unused" if window_exhausted else "no_row",
                    "detail": "window_exhausted" if window_exhausted else None,
                    "b_fiducial_s": None,
                    "attempt_id": None,
                    "retained": False,
                }
            )
            continue
        entry: dict[str, Any] = {
            "slot": slot,
            "attempt_id": observation.attempt_id,
            "b_fiducial_s": None,
            "retained": False,
        }
        if observation.classification_disposition != "valid":
            entry["outcome"] = "disposition"
            entry["detail"] = observation.classification_disposition
            outcomes.append(entry)
            continue
        # The bytes are authenticated against the row before anything is read
        # from them, so a bundle edited after finalization refuses the whole
        # check instead of contributing a value.
        evidence, _manifest = _read_member_evidence(observation)
        resolved, detail = anchor_v3_replay_outcome(evidence)
        if not resolved:
            entry["outcome"] = "valid_unresolved"
            entry["detail"] = detail or "unknown"
            outcomes.append(entry)
            continue
        lexeme = evidence.get("b_fiducial_s")
        if not isinstance(lexeme, str) or observation.exact_bound_lexeme_s != lexeme:
            raise PrepareRefusal(
                f"slot {slot} ({observation.attempt_id}): primary b_fiducial_s "
                "does not match the ledger row's exact bound lexeme"
            )
        entry["outcome"] = "valid_resolved"
        entry["detail"] = None
        entry["b_fiducial_s"] = lexeme
        entry["retained"] = True
        outcomes.append(entry)
        retained.append({"slot": slot, "attempt_id": observation.attempt_id,
                         "b_fiducial_s": lexeme})
    return outcomes, retained


def _outcome_line(entry: Mapping[str, Any]) -> str:
    outcome = entry["outcome"]
    if outcome == "valid_resolved":
        return f"  {entry['slot']}: valid+resolved {entry['b_fiducial_s']}"
    if outcome == "valid_unresolved":
        return f"  {entry['slot']}: valid+unresolved {entry['detail']}"
    if outcome == "disposition":
        return f"  {entry['slot']}: {entry['detail']}"
    if outcome == "unused":
        return f"  {entry['slot']}: unused (window_exhausted)"
    return f"  {entry['slot']}: no row"


def resolve_session(snapshot: Any, session_id: str) -> Any:
    """The named night, or the refusal that says why it cannot be judged.

    This runs BEFORE the snapshot's own refusal reasons are consulted, because
    an OPEN derivation session is itself one of those reasons: judged in the
    other order, every mid-campaign run would report the generic ledger
    complaint instead of the specific, actionable "the night has not closed".
    """

    session = snapshot.bracket_session_by_id.get(session_id)
    if session is None:
        raise EquivalenceRefusal(f"session {session_id} is not in the ledger")
    if session.session_kind != SESSION_KIND_DERIVATION:
        raise EquivalenceRefusal(
            f"session {session_id} is kind {session.session_kind!r}, not "
            f"{SESSION_KIND_DERIVATION!r}; the equivalence rule is about a "
            "derivation night"
        )
    if session.state not in TERMINAL_SESSION_STATES:
        raise EquivalenceRefusal(
            f"session {session_id} is {session.state!r}, not terminal; the "
            "rule applies AFTER the night closes"
        )
    return session


def evaluate_session(
    session: Any, session_id: str, envelope: Mapping[str, Any]
) -> dict[str, Any]:
    """Apply the rule to one resolved, terminal derivation night."""

    outcomes, retained = _slot_outcomes(session)
    record: dict[str, Any] = {
        "schema_version": "joulewise.epoch_equivalence_check.v1",
        "reference_envelope": dict(envelope),
        "session": {
            "session_id": session_id,
            "session_kind": session.session_kind,
            "state": session.state,
            "abort_reason": session.abort_reason,
            "declared_slots": list(session.declared_slots),
        },
        "slot_outcomes": outcomes,
        "retained": retained,
        "m": len(retained),
    }
    if len(retained) < MINIMUM_RETAINED_M:
        record.update(
            {
                "maximum_s": None,
                "maximum_slot": None,
                "minimum_s": None,
                "minimum_slot": None,
                "range_s": None,
                "level_screen_comparison": None,
                "bracket_screen_comparison": None,
                "verdict": VERDICT_INCONCLUSIVE,
                "verdict_reason": (
                    f"m={len(retained)} is below the minimum {MINIMUM_RETAINED_M}; "
                    "issue 316 directs one more equivalence night"
                ),
            }
        )
        return record
    # Decimal from the stored lexemes at an explicit working precision: the
    # subtraction below decides a verdict at the fifteenth decimal place, and
    # a float would not survive it.
    with localcontext() as context:
        context.prec = DECIMAL_WORK_PRECISION
        values = [Decimal(item["b_fiducial_s"]) for item in retained]
        maximum = max(values)
        minimum = min(values)
        spread = maximum - minimum
        level_screen = Decimal(envelope["level_screen_s"])
        bracket_screen = Decimal(envelope["bracket_screen_s"])
        level_pass = maximum <= level_screen
        bracket_pass = spread <= bracket_screen
        maximum_slot = retained[values.index(maximum)]["slot"]
        minimum_slot = retained[values.index(minimum)]["slot"]
        record.update(
            {
                "maximum_s": str(maximum),
                "maximum_slot": maximum_slot,
                "minimum_s": str(minimum),
                "minimum_slot": minimum_slot,
                "range_s": str(spread),
                "level_screen_comparison": {
                    "left": str(maximum),
                    "left_source": f"retained maximum ({maximum_slot})",
                    "operator": "<=",
                    "right": envelope["level_screen_s"],
                    "right_source": "operative preflight_level_screen_s",
                    "holds": level_pass,
                },
                "bracket_screen_comparison": {
                    "left": str(spread),
                    "left_source": "retained range (max - min)",
                    "operator": "<=",
                    "right": envelope["bracket_screen_s"],
                    "right_source": "operative bracket_screen_s",
                    "holds": bracket_pass,
                },
                "verdict": VERDICT_PASS if (level_pass and bracket_pass) else VERDICT_FAIL,
                "verdict_reason": None,
            }
        )
    return record


def record_lines(record: Mapping[str, Any]) -> list[str]:
    """The fixed-format printed record; every printed number is in the JSON."""

    session = record["session"]
    lines = ["Epoch equivalence check (directive issue 316)"]
    lines.append(
        "  This tool judges one closed derivation night against the envelope in "
        "force."
    )
    lines.append(
        "  It issues nothing, continues nothing, and writes no addendum."
    )
    lines.append("")
    lines.extend(envelope_lines(record["reference_envelope"]))
    lines.append("")
    lines.append(
        f"Session: {session['session_id']}  kind={session['session_kind']} "
        f"state={session['state']} "
        f"abort_reason={session['abort_reason'] or 'none'} "
        f"declared={len(session['declared_slots'])}"
    )
    for entry in record["slot_outcomes"]:
        lines.append(_outcome_line(entry))
    lines.append("")
    lines.append(
        f"Retained m = {record['m']} "
        "(rows with disposition valid whose stored anchor-v3 replay resolved)"
    )
    if record["m"] < MINIMUM_RETAINED_M:
        lines.append(f"  {record['verdict_reason']}")
    else:
        lines.append(
            f"  maximum retained b_fiducial_s = {record['maximum_s']} "
            f"({record['maximum_slot']})"
        )
        lines.append(
            f"  minimum retained b_fiducial_s = {record['minimum_s']} "
            f"({record['minimum_slot']})"
        )
        lines.append(f"  retained range (max - min)    = {record['range_s']}")
        lines.append("")
        level = record["level_screen_comparison"]
        bracket = record["bracket_screen_comparison"]
        lines.append(
            f"  LEVEL screen:   {level['left']} ({level['left_source']}) "
            f"{level['operator']} {level['right']} ({level['right_source']}) "
            f"-> {'holds' if level['holds'] else 'VIOLATED'}"
        )
        lines.append(
            f"  BRACKET screen: {bracket['left']} ({bracket['left_source']}) "
            f"{bracket['operator']} {bracket['right']} ({bracket['right_source']}) "
            f"-> {'holds' if bracket['holds'] else 'VIOLATED'}"
        )
    lines.append("")
    lines.append(f"EPOCH_EQUIVALENCE: {record['verdict']} (m={record['m']})")
    return lines


VERDICT_EXITS = {
    VERDICT_PASS: 0,
    VERDICT_FAIL: FAIL_EXIT,
    VERDICT_INCONCLUSIVE: INCONCLUSIVE_EXIT,
}


def run(args: argparse.Namespace) -> int:
    if args.print_envelope_only:
        envelope = reference_envelope(args.acceptance)
        for line in envelope_lines(envelope):
            print(line)
        return 0
    if args.session_id is None:
        raise EquivalenceRefusal("--session-id is required without --print-envelope-only")
    if args.out is None:
        raise EquivalenceRefusal("--out is required without --print-envelope-only")
    # The destination is checked FIRST, before anything is read: a refusal that
    # only fired after the work was done would still have told the caller the
    # tool was willing to write there.
    _refuse_out_path(args.out, args.force)
    envelope = reference_envelope(args.acceptance)
    snapshot = load_calibration_ledger_snapshot(
        args.ledger,
        args.head_pin,
        require_committed_pin=True,
        verify_custody=False,
        mode="read_replay",
        repo_root=Path(args.repo_root),
    )
    session = resolve_session(snapshot, args.session_id)
    if snapshot.refusal_reasons:
        raise EquivalenceRefusal("ledger: " + ", ".join(snapshot.refusal_reasons))
    record = evaluate_session(session, args.session_id, envelope)
    for line in record_lines(record):
        print(line)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"record written: {args.out}")
    return VERDICT_EXITS[record["verdict"]]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="epoch_equivalence_check.py",
        description=(
            "Judge ONE closed derivation night against the acceptance envelope "
            "already in force, under the rule directive issue 316 fixed before "
            "any capture. A DERIVATION NIGHT is one derivation-kind ledger "
            "session of declared capture slots; it is judged only after it "
            "closes. A capture is RETAINED when its ledger row is `valid` and "
            "the anchor-v3 replay stored in its own authenticated bytes "
            "resolved. The REFERENCE ENVELOPE is the acceptance in force; its "
            "LEVEL SCREEN is the absolute bound above which a single capture is "
            "refused, and its BRACKET SCREEN is the drift below which a window "
            "spends no error budget. EPOCH EQUIVALENCE holds (PASS) when every "
            "retained value is at or below the level screen AND the night's "
            "spread (largest retained value minus smallest) is at or below the "
            "bracket screen; FAIL otherwise; INCONCLUSIVE with fewer than "
            f"{MINIMUM_RETAINED_M} retained captures."
        ),
        epilog=(
            "This tool NEVER issues an acceptance, never continues one onto a "
            "new epoch, never writes an addendum, never appends to the ledger, "
            "and never writes under configs/calibration. Acting on a PASS is a "
            "separate reviewed act. Exit codes: 0 PASS, "
            f"{FAIL_EXIT} FAIL, {INCONCLUSIVE_EXIT} INCONCLUSIVE, "
            f"{REFUSAL_EXIT} refusal (nothing written)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--session-id", default=None,
        help="the derivation-kind ledger session of the night to judge",
    )
    parser.add_argument(
        "--ledger", type=Path, default=DEFAULT_LEDGER_PATH,
        help="the append-only calibration observation ledger to read",
    )
    parser.add_argument(
        "--head-pin", type=Path, default=DEFAULT_HEAD_PIN_PATH,
        help=(
            "the committed file naming the ledger row count and last digest "
            "consumers trust; it must match both Git and the physical ledger"
        ),
    )
    parser.add_argument(
        "--acceptance", type=Path, default=DEFAULT_ACCEPTANCE_BOUND_PATH,
        help="the issued acceptance artifact that supplies the reference envelope",
    )
    parser.add_argument(
        "--repo-root", type=Path, default=REPO_ROOT,
        help="the checkout the ledger and the evidence bundles live in",
    )
    parser.add_argument(
        "--out", type=Path, default=None,
        help=(
            "where to write the JSON record; required unless "
            "--print-envelope-only, and refused under configs/calibration"
        ),
    )
    parser.add_argument(
        "--force", action="store_true",
        help="overwrite an existing --out (refused by default)",
    )
    parser.add_argument(
        "--print-envelope-only", action="store_true",
        help=(
            "print the reference-envelope constants table and stop; needs no "
            "session, reads no ledger and writes nothing"
        ),
    )
    return parser


def main_args(args: argparse.Namespace) -> int:
    """Run on already-parsed arguments; every refusal is a printed reason."""

    try:
        return run(args)
    except (EquivalenceRefusal, PrepareRefusal) as refusal:
        print(f"REFUSED: {refusal.reason}")
        return REFUSAL_EXIT


def main(argv: list[str] | None = None) -> int:
    return main_args(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
