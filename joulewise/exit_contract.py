"""Read-only exit vocabularies; no existing tool adopts this module.

This is a snapshot of declarations, not proof that a payload exists or that a
release is authorised. In particular, night ``GO`` describes admission, harvest
0 can mean NO_COLLECTION, and block-5 75 is a *stage* code. The block-5 table is
the union of main and W1 declarations; its W1-only 13 is labelled below.

Source citations use local remote-tracking refs, inspected without executing the
tools. Their commit IDs are recorded in the seat's 2026-11-11 run report.
"""
from __future__ import annotations

import enum
import re
from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


class ExitClass(enum.Enum):
    """Shared semantics, while retaining each tool's original word.

    SUCCESS is a declared normal completion (GO, complete, agree, pass or ok).
    REFUSED covers rejected inputs/admission and tooling refusals. FAILED covers
    execution/integrity faults and missing planned harvest members. STOPPED covers
    aborts, signal encodings, deadlines and skipped stages. USAGE is PREQUAL's
    argument error. HOLD covers release disagreement, dry-run outcome_class and
    incomplete/not-ready work. UNDECLARED covers everything outside a vocabulary,
    including invalid returncode types and subprocess-style negative signals;
    it has failure semantics and can never be success. No extra class is needed.
    """

    SUCCESS = "success"
    REFUSED = "refused"
    FAILED = "failed"
    STOPPED = "stopped"
    USAGE = "usage"
    HOLD = "hold"
    UNDECLARED = "undeclared"


@dataclass(frozen=True)
class ExitCode:
    """An exact code or a half-open range, with code-derived provenance.

    ``word`` preserves the tool vocabulary, including ambiguity. ``sources``
    contains ref:path:line citations. Plan declarations have no code provenance.
    """

    code: int | range
    word: str
    exit_class: ExitClass
    sources: tuple[str, ...] = ()
    note: str = ""


@dataclass(frozen=True)
class Contract:
    entries: tuple[ExitCode, ...]
    verified: bool = True
    # Highest precedence first. Empty means that no combination rule is declared.
    precedence: tuple[int, ...] = ()


@dataclass(frozen=True)
class Classified:
    exit_class: ExitClass
    word: str
    declared: bool

    @property
    def is_success(self) -> bool:
        return self.declared and self.exit_class is ExitClass.SUCCESS


_MAIN = "origin/main"
_W1 = "origin/align/2026-11-08-v4-r11"
_OFFLOAD = "origin/ops/2026-11-08-air-offload-merged"
_RELEASE = "origin/align/2026-11-08-v4-release-tools"


def _sources(path: str, *locations: tuple[str, int]) -> tuple[str, ...]:
    return tuple(f"{ref}:{path}:{line}" for ref, line in locations)


CONTRACTS: Mapping[str, Contract] = MappingProxyType({
    "night_driver": Contract((
        ExitCode(0, "GO", ExitClass.SUCCESS,
                 _sources("scripts/run_night.py", (_MAIN, 127), (_W1, 129)),
                 "Admission only; says nothing about payload completeness."),
        ExitCode(3, "REFUSED", ExitClass.REFUSED,
                 _sources("scripts/run_night.py", (_MAIN, 128), (_W1, 130))),
        ExitCode(4, "ABORTED", ExitClass.STOPPED,
                 _sources("scripts/run_night.py", (_MAIN, 129), (_W1, 131))),
        ExitCode(5, "CHAIN_FAILED", ExitClass.FAILED,
                 _sources("scripts/run_night.py", (_MAIN, 130), (_W1, 132))),
        ExitCode(6, "COURIER_FAILED", ExitClass.FAILED,
                 _sources("scripts/run_night.py", (_MAIN, 131), (_W1, 133))),
    )),
    "r1_driver": Contract((
        ExitCode(0, "complete", ExitClass.SUCCESS,
                 _sources("scripts/align_r1_rehearsal.py", (_W1, 1855))),
        ExitCode(3, "refused", ExitClass.REFUSED,
                 _sources("scripts/align_r1_rehearsal.py", (_W1, 1860))),
        ExitCode(4, "aborted", ExitClass.STOPPED,
                 _sources("scripts/align_r1_rehearsal.py", (_W1, 1860))),
    )),
    "r1_runtime": Contract((
        ExitCode(0, "complete", ExitClass.SUCCESS,
                 _sources("joulewise/align/apple/r1_runtime.py", (_W1, 2052))),
        ExitCode(2, "refused", ExitClass.REFUSED,
                 _sources("joulewise/align/apple/r1_runtime.py", (_W1, 87), (_W1, 2057))),
        ExitCode(3, "failed", ExitClass.FAILED,
                 _sources("joulewise/align/apple/r1_runtime.py", (_W1, 87), (_W1, 2060))),
        ExitCode(range(129, 256), "aborted", ExitClass.STOPPED,
                 _sources("joulewise/align/apple/r1_runtime.py", (_W1, 1004), (_W1, 2054)),
                 "128+n signal encoding, n=1..127 within an exit byte. The runtime "
                 "installs HUP/INT/TERM handlers; the range does not assert that "
                 "every n is an installed signal. Negative subprocess codes are undeclared."),
    )),
    "b5_chain": Contract((
        ExitCode(0, "completed", ExitClass.SUCCESS,
                 _sources("joulewise/b5/chain.py", (_MAIN, 114), (_W1, 114))),
        ExitCode(10, "reservation_failed", ExitClass.STOPPED,
                 _sources("joulewise/b5/chain.py", (_MAIN, 115), (_W1, 115))),
        ExitCode(11, "pre_calibration_capture_failed", ExitClass.STOPPED,
                 _sources("joulewise/b5/chain.py", (_MAIN, 116), (_W1, 116))),
        ExitCode(12, "pre_calibration_screen_failed", ExitClass.STOPPED,
                 _sources("joulewise/b5/chain.py", (_MAIN, 117), (_W1, 117))),
        ExitCode(13, "operative_bound_above_stop", ExitClass.STOPPED,
                 _sources("joulewise/b5/chain.py", (_W1, 118)),
                 "W1-only declaration; absent on origin/main at intake."),
        ExitCode(64, "inspection_refused", ExitClass.REFUSED,
                 _sources("joulewise/b5/chain.py", (_MAIN, 118), (_W1, 119))),
        ExitCode(75, "horizon_skipped", ExitClass.STOPPED,
                 _sources("joulewise/b5/chain.py", (_MAIN, 223), (_W1, 225)),
                 "Stage-journal code, not a terminal chain exit; the chain continues to post capture."),
    )),
    "dry_run": Contract((
        ExitCode(0, "completed_without_tooling_refusal", ExitClass.SUCCESS,
                 _sources("joulewise/b5_analysis/dry_run.py", (_MAIN, 1958)),
                 "No outcome_class step; code 3 also completed without tooling refusal."),
        ExitCode(2, "tooling_refusal", ExitClass.REFUSED,
                 _sources("joulewise/b5_analysis/dry_run.py", (_MAIN, 1957))),
        ExitCode(3, "outcome_class", ExitClass.HOLD,
                 _sources("joulewise/b5_analysis/dry_run.py", (_MAIN, 1958))),
    ), precedence=(2, 3, 0)),
    "release_check": Contract((
        ExitCode(0, "agree", ExitClass.SUCCESS,
                 _sources("scripts/release_b5.py", (_MAIN, 471)) +
                 _sources("scripts/release_v4.py", (_RELEASE, 60))),
        ExitCode(1, "hold", ExitClass.HOLD,
                 _sources("scripts/release_b5.py", (_MAIN, 470)) +
                 _sources("scripts/release_v4.py", (_RELEASE, 60))),
        ExitCode(2, "refused", ExitClass.REFUSED,
                 _sources("scripts/release_b5.py", (_MAIN, 457)) +
                 _sources("scripts/release_v4.py", (_RELEASE, 60)),
                 "Block-5 prints hold on a refusal; v4 calls it refused. "
                 "A status code alone cannot distinguish an uncaught exit-1 crash from hold."),
    ), precedence=(2, 1, 0)),
    "harvest": Contract((
        ExitCode(0, "COLLECTED/NO_COLLECTION/NULL", ExitClass.SUCCESS,
                 _sources("scripts/harvest_b5_window.py", (_MAIN, 110), (_W1, 109)),
                 "Process completion only; claim_usable must be read separately."),
        ExitCode(2, "HARVEST_FAULT", ExitClass.FAILED,
                 _sources("scripts/harvest_b5_window.py", (_MAIN, 106), (_W1, 105))),
        ExitCode(3, "unresolvable_input", ExitClass.REFUSED,
                 _sources("scripts/harvest_b5_window.py", (_MAIN, 88), (_W1, 84)),
                 "Also unusable archive; W1 adds StorageStop refusal. "
                 "The ordinary exception branch prints HARVEST_FAULT without writing a record."),
        ExitCode(4, "NOT_READY", ExitClass.HOLD,
                 _sources("scripts/harvest_b5_window.py", (_MAIN, 85), (_W1, 87))),
        ExitCode(6, "none_present", ExitClass.FAILED,
                 _sources("scripts/harvest_b5_window.py", (_MAIN, 108), (_W1, 107)),
                 "COLLECTED or NO_COLLECTION with members planned and none present."),
    )),
    "offload": Contract((
        ExitCode(0, "ok", ExitClass.SUCCESS,
                 _sources("scripts/offload_window.py", (_OFFLOAD, 1726), (_W1, 1726)),
                 "May include held release; not proof of two copies or deletion."),
        ExitCode(2, "Refusal", ExitClass.REFUSED,
                 _sources("scripts/offload_window.py", (_OFFLOAD, 113), (_W1, 113))),
        ExitCode(3, "Mismatch", ExitClass.FAILED,
                 _sources("scripts/offload_window.py", (_OFFLOAD, 118), (_W1, 118))),
        ExitCode(4, "DeadlineStop", ExitClass.STOPPED,
                 _sources("scripts/offload_window.py", (_OFFLOAD, 123), (_W1, 123)),
                 "Also Interrupted (SIGTERM); resumable."),
        ExitCode(5, "TransportError", ExitClass.FAILED,
                 _sources("scripts/offload_window.py", (_OFFLOAD, 131), (_W1, 131))),
        ExitCode(6, "io_error", ExitClass.FAILED,
                 _sources("scripts/offload_window.py", (_OFFLOAD, 1790), (_W1, 1790))),
    )),
    "prequal": Contract((
        ExitCode(0, "pass", ExitClass.SUCCESS,
                 _sources("scripts/align_v4_prequal.py", (_W1, 22))),
        ExitCode(1, "fail", ExitClass.FAILED,
                 _sources("scripts/align_v4_prequal.py", (_W1, 22))),
        ExitCode(3, "incomplete", ExitClass.HOLD,
                 _sources("scripts/align_v4_prequal.py", (_W1, 22))),
        ExitCode(2, "usage", ExitClass.USAGE,
                 _sources("scripts/align_v4_prequal.py", (_W1, 31), (_W1, 51))),
    )),
})


def classify(tool: str | Contract, returncode: object) -> Classified:
    """Classify without coercion; unknown tool keys raise KeyError even for bad codes.

    A parsed plan Contract may be passed directly. Only an exact Python int can
    match a declaration: bool, floats, int subclasses and negative signals fail
    closed. An unverified vocabulary also fails closed, including its zero.
    """
    contract = tool if isinstance(tool, Contract) else CONTRACTS[tool]
    if contract.verified and type(returncode) is int and 0 <= returncode <= 255:
        for entry in contract.entries:
            matches = returncode in entry.code if isinstance(entry.code, range) else returncode == entry.code
            if matches:
                return Classified(entry.exit_class, entry.word, True)
    return Classified(ExitClass.UNDECLARED, "undeclared", False)


class PlanContractError(ValueError):
    """Invalid future plan declaration; ``reason`` is a stable error identifier."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


# Deliberately small, exact and case-sensitive. Existing tools retain their own
# vocabularies above; new plans use these shared words. No fallback success word.
PLAN_WORDS: Mapping[str, ExitClass] = MappingProxyType({
    "complete": ExitClass.SUCCESS,
    "refused": ExitClass.REFUSED,
    "failed": ExitClass.FAILED,
    "stopped": ExitClass.STOPPED,
    "usage": ExitClass.USAGE,
    "hold": ExitClass.HOLD,
})
_DECIMAL = re.compile(r"(?:0|[1-9][0-9]{0,2})\Z")


def parse_plan_contract(mapping: object) -> Contract:
    """Validate the value of a future ``exit_contract`` plan key, without I/O.

    Accept integer keys or canonical ASCII decimal string keys in 0..255 (JSON
    object keys). Aliases such as 00, +0 and whitespace are refused, as are
    duplicate normalized keys. Zero must be declared; at least one code must
    say ``complete``. Zero need not itself be that success code. The returned
    immutable snapshot is verified by validation, not by live tool execution.
    """
    if not isinstance(mapping, Mapping):
        raise PlanContractError("not_a_mapping")
    entries: dict[int, ExitCode] = {}
    for key, word in mapping.items():
        if type(key) is int:
            code = key
        elif type(key) is str and _DECIMAL.fullmatch(key):
            code = int(key)
        else:
            raise PlanContractError("invalid_code")
        if not 0 <= code <= 255:
            raise PlanContractError("code_out_of_range")
        if code in entries:
            raise PlanContractError("duplicate_code")
        if type(word) is not str or word not in PLAN_WORDS:
            raise PlanContractError("invalid_word")
        entries[code] = ExitCode(code, word, PLAN_WORDS[word])
    if 0 not in entries:
        raise PlanContractError("zero_required")
    if not any(entry.exit_class is ExitClass.SUCCESS for entry in entries.values()):
        raise PlanContractError("success_required")
    return Contract(tuple(entries[code] for code in sorted(entries)))


def as_outcome_map(contract: Contract) -> dict[int, str]:
    """Return a fresh plain code-to-original-word map, expanding ranges.

    Unverified vocabularies have no consumable declarations. This function does
    not import window_state or read a plan. Callers must fail closed on missing
    keys rather than interpreting a missing key as success.
    """
    if not contract.verified:
        return {}
    return {code: entry.word for entry in contract.entries
            for code in (entry.code if isinstance(entry.code, range) else (entry.code,))}
