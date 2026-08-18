#!/usr/bin/env python3
"""Authenticate and derive a non-issued D-079 successor candidate.

This command is preparation tooling only.  It never writes an issued artifact:
every output carries ``candidate_not_issued: true`` and remains inadmissible to
the production exact-byte acceptance loader.  A later, separately governed
issuance transaction must remove that marker, assign successor identity, and
establish the new external byte pin.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence

sys.dont_write_bytecode = True
REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from joulewise.authentication_io import read_authentication_input  # noqa: E402
from joulewise.calibration_bracketing import (  # noqa: E402
    DEFAULT_ACCEPTANCE_BOUND_PATH,
    ESTIMATOR_CODE_PATHS,
    _canonical_sha256,
    _current_estimator_code_sha256,
    _valid_acceptance_bound,
    load_calibration_acceptance_bound,
)
from joulewise.calibration_ledger import (  # noqa: E402
    content_id_from_artifact_hashes,
)
from joulewise.powermetrics_fiducial import (  # noqa: E402
    PROTOCOL_ID,
    protocol_sha256,
)


CANDIDATE_MARKER = "candidate_not_issued"
CORPUS_AUTHENTICATION_FAILURE_EXIT = 2
SCIENCE_DELTA_STOP_EXIT = 3


class ReissueCandidateError(ValueError):
    """The requested candidate could not be safely derived."""


@dataclass(frozen=True)
class CorpusAuthentication:
    """Complete per-member authentication result and recovered lexemes."""

    members: tuple[dict[str, Any], ...]

    @property
    def authenticated_count(self) -> int:
        return sum(member["authenticated"] is True for member in self.members)

    @property
    def all_authenticated(self) -> bool:
        return self.authenticated_count == len(self.members) and bool(self.members)

    @property
    def observed_b_fiducial_by_member(self) -> dict[str, str]:
        if not self.all_authenticated:
            raise ReissueCandidateError(
                "candidate derivation requires every corpus member to authenticate"
            )
        return {
            member["member_id"]: member["b_fiducial_s"]["observed"]
            for member in self.members
        }

    def summary(self) -> dict[str, Any]:
        return {
            "authenticated": self.authenticated_count,
            "total": len(self.members),
            "result": "PASS" if self.all_authenticated else "FAIL",
        }


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _strict_decimal_lexeme_json(raw: bytes, *, label: str) -> Mapping[str, Any]:
    """Parse evidence without losing its source decimal lexemes."""

    def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ReissueCandidateError(f"{label}: duplicate JSON key {key!r}")
            value[key] = item
        return value

    def reject_nonfinite(value: str) -> None:
        raise ReissueCandidateError(f"{label}: non-finite JSON number {value!r}")

    try:
        parsed = json.loads(
            raw,
            object_pairs_hook=reject_duplicate_pairs,
            parse_float=str,
            parse_int=str,
            parse_constant=reject_nonfinite,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReissueCandidateError(f"{label}: invalid UTF-8 JSON: {exc}") from exc
    if not isinstance(parsed, Mapping):
        raise ReissueCandidateError(f"{label}: expected a JSON object")
    return parsed


def _check(expected: Any, observed: Any) -> dict[str, Any]:
    return {
        "expected": expected,
        "observed": observed,
        "result": "PASS" if observed == expected else "FAIL",
    }


def authenticate_derivation_corpus(
    artifact: Mapping[str, Any], *, corpus_root: Path
) -> CorpusAuthentication:
    """Re-open and authenticate all issued derivation-corpus members."""

    try:
        members = artifact["derivation_corpus"]["members"]
        prior_rows = artifact["prior_observation_set"]["observations"]
    except (KeyError, TypeError) as exc:
        raise ReissueCandidateError(
            "acceptance artifact lacks its corpus tables"
        ) from exc
    if not isinstance(members, list) or not isinstance(prior_rows, list):
        raise ReissueCandidateError("acceptance artifact corpus tables are malformed")

    root = Path(corpus_root).resolve(strict=True)
    prior_by_content_id = {
        row.get("content_id"): row for row in prior_rows if isinstance(row, Mapping)
    }
    reports: list[dict[str, Any]] = []
    for member in members:
        if not isinstance(member, Mapping):
            raise ReissueCandidateError("derivation corpus member is not an object")
        member_id = member.get("member_id")
        source_directory = member.get("source_directory")
        report: dict[str, Any] = {
            "member_id": member_id,
            "source_directory": source_directory,
            "manifest_sha256": _check(member.get("manifest_sha256"), None),
            "instrument_evidence_sha256": _check(
                member.get("instrument_evidence_sha256"), None
            ),
            "b_fiducial_s": _check(member.get("b_fiducial_s"), None),
            "prior_observation": {
                "expected": "matching valid prior observation",
                "observed": None,
                "result": "FAIL",
            },
            "errors": [],
            "authenticated": False,
        }
        if not isinstance(member_id, str) or not isinstance(source_directory, str):
            report["errors"].append("invalid member_id or source_directory")
            reports.append(report)
            continue
        try:
            directory = (root / source_directory).resolve(strict=True)
            directory.relative_to(root)
            if directory.name != member_id:
                raise ReissueCandidateError(
                    "source directory basename does not equal member_id"
                )
            manifest_path = directory / "manifest.json"
            evidence_path = directory / "instrument_evidence.json"
            manifest_raw = read_authentication_input(
                manifest_path,
                grammar="json",
                label=f"D-079 corpus manifest {member_id}",
            )
            evidence_raw = read_authentication_input(
                evidence_path,
                grammar="json",
                label=f"D-079 corpus instrument evidence {member_id}",
            )
            evidence = _strict_decimal_lexeme_json(
                evidence_raw, label=f"{member_id}/instrument_evidence.json"
            )
            observed_manifest_sha256 = _sha256(manifest_raw)
            observed_evidence_sha256 = _sha256(evidence_raw)
            observed_b_fiducial_s = evidence.get("b_fiducial_s")
            report["manifest_sha256"] = _check(
                member.get("manifest_sha256"), observed_manifest_sha256
            )
            report["instrument_evidence_sha256"] = _check(
                member.get("instrument_evidence_sha256"),
                observed_evidence_sha256,
            )
            report["b_fiducial_s"] = _check(
                member.get("b_fiducial_s"), observed_b_fiducial_s
            )
            expected_hashes = {
                "manifest.json": member.get("manifest_sha256"),
                "instrument_evidence.json": member.get(
                    "instrument_evidence_sha256"
                ),
            }
            content_id = content_id_from_artifact_hashes(expected_hashes)
            prior = prior_by_content_id.get(content_id)
            prior_observed = (
                "matching valid prior observation"
                if isinstance(prior, Mapping)
                and prior.get("attempt_id") == member_id
                and prior.get("disposition") == "valid"
                else prior
            )
            report["prior_observation"] = _check(
                "matching valid prior observation", prior_observed
            )
        except (OSError, ValueError, TypeError) as exc:
            report["errors"].append(str(exc))

        check_names = (
            "manifest_sha256",
            "instrument_evidence_sha256",
            "b_fiducial_s",
            "prior_observation",
        )
        report["authenticated"] = not report["errors"] and all(
            report[name]["result"] == "PASS" for name in check_names
        )
        reports.append(report)
    return CorpusAuthentication(tuple(reports))


def _artifact_with_digest(artifact: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(artifact)
    result["derivation_sha256"] = _canonical_sha256(
        {key: value for key, value in result.items() if key != "derivation_sha256"}
    )
    return result


def derive_candidate_artifact(
    predecessor: Mapping[str, Any], authentication: CorpusAuthentication
) -> dict[str, Any]:
    """Reconstruct a candidate and prove it with production derivation logic."""

    observed = authentication.observed_b_fiducial_by_member
    candidate = deepcopy(dict(predecessor))
    candidate.pop(CANDIDATE_MARKER, None)
    try:
        candidate_members = candidate["derivation_corpus"]["members"]
        prospective = candidate["prospective_rederivation"]
    except (KeyError, TypeError) as exc:
        raise ReissueCandidateError("predecessor lacks reissue inputs") from exc
    candidate_ids = {member["member_id"] for member in candidate_members}
    if candidate_ids != set(observed):
        raise ReissueCandidateError("authenticated and candidate member sets differ")
    for member in candidate_members:
        member["b_fiducial_s"] = observed[member["member_id"]]

    estimator_pins = _current_estimator_code_sha256()
    if estimator_pins is None or set(estimator_pins) != set(ESTIMATOR_CODE_PATHS):
        raise ReissueCandidateError(
            "could not hash all four production estimator inputs"
        )
    prospective["estimator_code_sha256"] = estimator_pins
    prospective["protocol_sha256"] = protocol_sha256(PROTOCOL_ID)
    unmarked = _artifact_with_digest(candidate)

    # This is the production acceptance derivation/validation path.  It
    # reconstructs the decimal corpus statistics, comparator rounding, member
    # linkage, and registered D-102/D-109 operatives.  The reissue tool does not
    # carry a second arithmetic implementation.
    if not _valid_acceptance_bound(unmarked):
        raise ReissueCandidateError(
            "production D-079 derivation validation rejected the reconstructed "
            "candidate"
        )

    marked = {CANDIDATE_MARKER: True, **unmarked}
    return _artifact_with_digest(marked)


def candidate_artifact_bytes(candidate: Mapping[str, Any]) -> bytes:
    if candidate.get(CANDIDATE_MARKER) is not True:
        raise ReissueCandidateError("refusing to serialize an unmarked candidate")
    return (
        json.dumps(
            dict(candidate),
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ": "),
        )
        + "\n"
    ).encode("utf-8")


def write_candidate_artifact(path: Path, candidate: Mapping[str, Any]) -> bytes:
    payload = candidate_artifact_bytes(candidate)
    destination = Path(path)
    if destination.resolve() == DEFAULT_ACCEPTANCE_BOUND_PATH.resolve():
        raise ReissueCandidateError("refusing to overwrite the issued predecessor")
    try:
        with destination.open("xb") as handle:
            written = handle.write(payload)
    except FileExistsError as exc:
        raise ReissueCandidateError(
            f"candidate output already exists: {destination}"
        ) from exc
    if written != len(payload):
        raise OSError(f"short candidate write: {destination}")
    return payload


_PIN_PATHS = {
    ("prospective_rederivation", "protocol_sha256"),
    ("derivation_sha256",),
    (CANDIDATE_MARKER,),
}
_MISSING = object()
_THRESHOLD_PATHS = (
    (
        "decimal_derivation",
        "source_statistics",
        "prediction_95_two_draw_s",
    ),
    (
        "decimal_derivation",
        "source_statistics",
        "prediction_99_two_draw_s",
    ),
    ("decimal_derivation", "rounding"),
    ("decimal_derivation", "ratified_operatives"),
)


def _is_pin_path(path: tuple[str | int, ...]) -> bool:
    return path in _PIN_PATHS or path[:2] == (
        "prospective_rederivation",
        "estimator_code_sha256",
    )


def _json_path(path: Sequence[str | int]) -> str:
    value = "$"
    for item in path:
        value += f"[{item}]" if isinstance(item, int) else f".{item}"
    return value


def _value_at(value: Any, path: Sequence[str]) -> Any:
    current = value
    for item in path:
        if not isinstance(current, Mapping) or item not in current:
            return _MISSING
        current = current[item]
    return current


def _reported_value(value: Any) -> Any:
    return {"missing": True} if value is _MISSING else value


def _recursive_differences(
    issued: Any,
    candidate: Any,
    *,
    path: tuple[str | int, ...] = (),
) -> list[dict[str, Any]]:
    if _is_pin_path(path):
        return []
    if isinstance(issued, Mapping) and isinstance(candidate, Mapping):
        differences: list[dict[str, Any]] = []
        for key in sorted(set(issued) | set(candidate)):
            differences.extend(
                _recursive_differences(
                    issued[key] if key in issued else _MISSING,
                    candidate[key] if key in candidate else _MISSING,
                    path=(*path, key),
                )
            )
        return differences
    if isinstance(issued, list) and isinstance(candidate, list):
        differences = []
        for index in range(max(len(issued), len(candidate))):
            old = issued[index] if index < len(issued) else _MISSING
            new = candidate[index] if index < len(candidate) else _MISSING
            differences.extend(
                _recursive_differences(old, new, path=(*path, index))
            )
        return differences
    if issued == candidate:
        return []
    return [
        {
            "path": _json_path(path),
            "issued": _reported_value(issued),
            "candidate": _reported_value(candidate),
        }
    ]


def build_member_delta_report(
    issued: Mapping[str, Any], candidate: Mapping[str, Any]
) -> dict[str, Any]:
    """Classify every non-pin difference conservatively as science-facing."""

    issued_members = issued["derivation_corpus"]["members"]
    candidate_members = candidate["derivation_corpus"]["members"]
    issued_by_id = {member["member_id"]: member for member in issued_members}
    candidate_by_id = {member["member_id"]: member for member in candidate_members}
    issued_ids = set(issued_by_id)
    candidate_ids = set(candidate_by_id)
    member_values = []
    for member_id in sorted(issued_ids | candidate_ids):
        old = issued_by_id.get(member_id)
        new = candidate_by_id.get(member_id)
        member_values.append(
            {
                "member_id": member_id,
                "issued_b_fiducial_s": (
                    old.get("b_fiducial_s") if old is not None else None
                ),
                "candidate_b_fiducial_s": (
                    new.get("b_fiducial_s") if new is not None else None
                ),
                "identical": old == new,
            }
        )

    threshold_differences: list[dict[str, Any]] = []
    for path in _THRESHOLD_PATHS:
        old = _value_at(issued, path)
        new = _value_at(candidate, path)
        if old != new:
            threshold_differences.append(
                {
                    "path": _json_path(path),
                    "issued": _reported_value(old),
                    "candidate": _reported_value(new),
                }
            )

    pin_values = []
    issued_prospective = issued["prospective_rederivation"]
    candidate_prospective = candidate["prospective_rederivation"]
    pin_values.append(
        {
            "path": "$.prospective_rederivation.protocol_sha256",
            "issued": issued_prospective["protocol_sha256"],
            "candidate": candidate_prospective["protocol_sha256"],
            "changed": issued_prospective["protocol_sha256"]
            != candidate_prospective["protocol_sha256"],
        }
    )
    for relative in ESTIMATOR_CODE_PATHS:
        old = issued_prospective["estimator_code_sha256"][relative]
        new = candidate_prospective["estimator_code_sha256"][relative]
        pin_values.append(
            {
                "path": (
                    "$.prospective_rederivation.estimator_code_sha256."
                    + relative
                ),
                "issued": old,
                "candidate": new,
                "changed": old != new,
            }
        )

    science_differences = _recursive_differences(issued, candidate)
    reasons: list[str] = []
    if issued_ids != candidate_ids:
        reasons.append("member_set_changed")
    if threshold_differences:
        reasons.append("thresholds_changed")
    if science_differences:
        reasons.append("science_facing_values_changed")
    verdict = "STOP" if reasons else "PROCEED"
    return {
        "member_set": {
            "issued_count": len(issued_ids),
            "candidate_count": len(candidate_ids),
            "added": sorted(candidate_ids - issued_ids),
            "removed": sorted(issued_ids - candidate_ids),
            "identical": issued_ids == candidate_ids,
        },
        "member_values": member_values,
        "thresholds": {
            "identical": not threshold_differences,
            "differences": threshold_differences,
        },
        "science_facing": {
            "identical": not science_differences,
            "differences": science_differences,
        },
        "pin_values": pin_values,
        "changed_pin_count": sum(pin["changed"] for pin in pin_values),
        "verdict": verdict,
        "stop_reasons": reasons,
    }


def _print_authentication(authentication: CorpusAuthentication) -> None:
    for member in authentication.members:
        print(
            "CORPUS_MEMBER "
            f"member_id={member['member_id']} "
            f"manifest={member['manifest_sha256']['result']} "
            f"instrument_evidence={member['instrument_evidence_sha256']['result']} "
            f"b_fiducial={member['b_fiducial_s']['result']} "
            f"prior={member['prior_observation']['result']} "
            f"result={'PASS' if member['authenticated'] else 'FAIL'}"
        )
    summary = authentication.summary()
    print(
        "CORPUS_AUTHENTICATION="
        f"{summary['result']} authenticated={summary['authenticated']} "
        f"total={summary['total']}"
    )


def _print_delta(report: Mapping[str, Any]) -> None:
    print(
        "MEMBER_DELTA_REPORT="
        + json.dumps(report, sort_keys=True, separators=(",", ":"))
    )
    print(
        "MEMBER_DELTA_SUMMARY "
        f"issued={report['member_set']['issued_count']} "
        f"candidate={report['member_set']['candidate_count']} "
        f"member_set={'IDENTICAL' if report['member_set']['identical'] else 'CHANGED'} "
        f"thresholds={'IDENTICAL' if report['thresholds']['identical'] else 'CHANGED'} "
        "science_facing="
        f"{'IDENTICAL' if report['science_facing']['identical'] else 'CHANGED'} "
        f"changed_pins={report['changed_pin_count']}"
    )
    if report["verdict"] == "STOP":
        print("VERDICT=STOP reasons=" + ",".join(report["stop_reasons"]))
    else:
        print("VERDICT=PROCEED reason=only_code_or_protocol_pins_differ")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predecessor",
        type=Path,
        default=DEFAULT_ACCEPTANCE_BOUND_PATH,
        help="exact issued predecessor acceptance artifact",
    )
    parser.add_argument(
        "--corpus-root",
        "--repo-root",
        dest="corpus_root",
        type=Path,
        default=REPO_ROOT,
        help="root containing the predecessor's source_directory paths",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="new caller-named path for the marked candidate artifact",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    predecessor = load_calibration_acceptance_bound(args.predecessor)
    if predecessor is None or predecessor.get(CANDIDATE_MARKER) is True:
        print("VERDICT=STOP reason=predecessor_not_authenticated_issued_artifact")
        return CORPUS_AUTHENTICATION_FAILURE_EXIT
    try:
        authentication = authenticate_derivation_corpus(
            predecessor, corpus_root=args.corpus_root
        )
        _print_authentication(authentication)
        if not authentication.all_authenticated:
            print("VERDICT=STOP reason=corpus_authentication_failed")
            return CORPUS_AUTHENTICATION_FAILURE_EXIT
        candidate = derive_candidate_artifact(predecessor, authentication)
        report = build_member_delta_report(predecessor, candidate)
        payload = write_candidate_artifact(args.output, candidate)
    except (OSError, ReissueCandidateError) as exc:
        print(f"VERDICT=STOP reason=candidate_derivation_failed detail={exc}")
        return CORPUS_AUTHENTICATION_FAILURE_EXIT
    _print_delta(report)
    print(
        f"CANDIDATE_OUTPUT={args.output} sha256={_sha256(payload)} "
        f"{CANDIDATE_MARKER}=true"
    )
    return 0 if report["verdict"] == "PROCEED" else SCIENCE_DELTA_STOP_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
