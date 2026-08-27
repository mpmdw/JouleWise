"""Deterministic reporting primitives for the T-0 clock reference.

This collector deliberately reports observations without applying evidence
policy.  The 0.5 s pin ceiling remains owned by ``MAX_OFFSET_S`` at
``scripts/quiet_window_clock.sh:30``; the separate 5 ms anchor ceiling remains
owned by that script at ``scripts/quiet_window_clock.sh:7,14,60-62``.  Quorum,
agreement, and refusal therefore belong to the evidence author and arm-side
predicate, not here.
"""

from __future__ import annotations

import ipaddress
import re
import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable, Protocol, Sequence


SCHEMA_VERSION = "joulewise.arm_readiness_t0_clock_reference.v1"
SAMPLE_POLICY_ID = "clock.machine_reference.apple_pool_nist_3x_t2_quorum2.v1"
SERVER_ROSTER = ("time.apple.com", "pool.ntp.org", "time.nist.gov")
SNTP_PATH = "/usr/bin/sntp"
SNTP_TIMEOUT_SECONDS = 2

_DECIMAL_PATTERN = r"[0-9]+\.[0-9]+"
_RESULT_PATTERN = re.compile(
    rf"(?P<offset>[+-]{_DECIMAL_PATTERN}) \+/- "
    rf"(?P<uncertainty>{_DECIMAL_PATTERN}) "
    r"(?P<server>\S+) (?P<peer_address>\S+)"
)
_CLOCK_SET_FLAGS = frozenset({"-s", "-S", "-a"})


class CompletedSample(Protocol):
    """The portion of ``subprocess.CompletedProcess`` consumed by the builder."""

    returncode: int
    stdout: bytes | str
    stderr: bytes | str


SampleRunner = Callable[[Sequence[str]], CompletedSample]
ClockGettimeNs = Callable[[int], int]


@dataclass(frozen=True)
class ParsedSntpLine:
    """One strictly parsed Darwin ``sntp`` result line."""

    offset_s: Decimal
    uncertainty_s: Decimal
    peer_address: str
    raw_line: str


@dataclass(frozen=True)
class ClockAnchor:
    """One RAW -> REALTIME -> RAW wall/hardware-counter anchor sample."""

    realtime_ns: int
    monotonic_raw_ns: int
    read_skew_ns: int


def assert_report_only_argv(argv: Sequence[str]) -> None:
    """Reject an SNTP observation that could request a clock adjustment."""

    if not _CLOCK_SET_FLAGS.isdisjoint(argv):
        raise ValueError("sntp clock-setting flag is forbidden")


def build_sntp_argv(server: str) -> list[str]:
    """Return the single ruled, report-only invocation for ``server``."""

    argv = [SNTP_PATH, "-t", str(SNTP_TIMEOUT_SECONDS), server]
    assert_report_only_argv(argv)
    return argv


def parse_sntp_stdout(stdout: str, *, server: str) -> ParsedSntpLine | None:
    """Parse the last non-empty stdout line when it has the ruled exact shape."""

    nonempty_lines = [line for line in stdout.splitlines() if line.strip()]
    if not nonempty_lines:
        return None
    raw_line = nonempty_lines[-1]
    matched = _RESULT_PATTERN.fullmatch(raw_line)
    if matched is None or matched.group("server") != server:
        return None
    peer_address = matched.group("peer_address")
    try:
        # ``ip_address`` is the standard-library syntax check used here to make
        # "malformed" precise while accepting both IPv4 and IPv6 literals.  We
        # retain the original spelling rather than normalizing evidence bytes.
        ipaddress.ip_address(peer_address)
    except ValueError:
        return None
    return ParsedSntpLine(
        # Decimal preserves the exact measured text for downstream arithmetic;
        # conversion to JSON's float representation happens only when emitted.
        offset_s=Decimal(matched.group("offset")),
        uncertainty_s=Decimal(matched.group("uncertainty")),
        peer_address=peer_address,
        raw_line=raw_line,
    )


def sample_anchor(
    clock_gettime_ns: ClockGettimeNs = time.clock_gettime_ns,
) -> ClockAnchor:
    """Sample the sleep-immune wall/counter anchor without applying its ceiling."""

    raw_before = clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    realtime_ns = clock_gettime_ns(time.CLOCK_REALTIME)
    raw_after = clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    return ClockAnchor(
        realtime_ns=realtime_ns,
        monotonic_raw_ns=(raw_before + raw_after) // 2,
        read_skew_ns=raw_after - raw_before,
    )


def _decode_output(value: bytes | str) -> str:
    return value if isinstance(value, str) else value.decode("utf-8", errors="replace")


def _sample_object(
    *,
    server: str,
    argv: list[str],
    result: CompletedSample,
    started_monotonic_raw_ns: int,
    finished_monotonic_raw_ns: int,
) -> dict[str, object]:
    stdout = _decode_output(result.stdout)
    stderr = _decode_output(result.stderr)
    parsed_line = (
        parse_sntp_stdout(stdout, server=server) if result.returncode == 0 else None
    )
    if parsed_line is None:
        offset_s = None
        uncertainty_s = None
        peer_address = None
        raw_line = None
    else:
        # Decimal parsing happens first so the only loss of precision is the
        # pinned JSON number representation at this emission boundary.
        offset_s = float(parsed_line.offset_s)
        uncertainty_s = float(parsed_line.uncertainty_s)
        peer_address = parsed_line.peer_address
        raw_line = parsed_line.raw_line
    return {
        "server": server,
        "argv": list(argv),
        "exit_code": int(result.returncode),
        "started_monotonic_raw_ns": started_monotonic_raw_ns,
        "finished_monotonic_raw_ns": finished_monotonic_raw_ns,
        "stdout": stdout,
        "stderr": stderr,
        "parsed": parsed_line is not None,
        "offset_s": offset_s,
        "uncertainty_s": uncertainty_s,
        "peer_address": peer_address,
        "raw_line": raw_line,
    }


def build_clock_reference(
    *,
    boot_session_id: str,
    runner: SampleRunner,
    clock_gettime_ns: ClockGettimeNs = time.clock_gettime_ns,
) -> dict[str, object]:
    """Collect the ruled roster and return the exact clock-reference object."""

    anchor = sample_anchor(clock_gettime_ns)
    batch_started = clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    samples: list[dict[str, object]] = []
    for server in SERVER_ROSTER:
        argv = build_sntp_argv(server)
        started = clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
        result = runner(argv)
        finished = clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
        samples.append(
            _sample_object(
                server=server,
                argv=argv,
                result=result,
                started_monotonic_raw_ns=started,
                finished_monotonic_raw_ns=finished,
            )
        )
    batch_finished = clock_gettime_ns(time.CLOCK_MONOTONIC_RAW)
    return {
        "schema_version": SCHEMA_VERSION,
        "sample_policy_id": SAMPLE_POLICY_ID,
        "boot_session_id": boot_session_id,
        "anchor_realtime_ns": anchor.realtime_ns,
        "anchor_monotonic_raw_ns": anchor.monotonic_raw_ns,
        "anchor_read_skew_ns": anchor.read_skew_ns,
        "batch_started_monotonic_raw_ns": batch_started,
        "batch_finished_monotonic_raw_ns": batch_finished,
        "samples": samples,
    }


__all__ = [
    "ClockAnchor",
    "ParsedSntpLine",
    "SAMPLE_POLICY_ID",
    "SCHEMA_VERSION",
    "SERVER_ROSTER",
    "SNTP_PATH",
    "SNTP_TIMEOUT_SECONDS",
    "assert_report_only_argv",
    "build_clock_reference",
    "build_sntp_argv",
    "parse_sntp_stdout",
    "sample_anchor",
]
