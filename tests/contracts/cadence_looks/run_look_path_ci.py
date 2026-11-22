"""Retain raw frozen bundle outcomes and decide the prospective cumulative gate."""

import argparse
import json
from pathlib import Path
import re
import runpy
import subprocess
import sys
from tempfile import TemporaryDirectory
from traceback import walk_tb
from unittest.mock import patch


HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "look_path"
DRIVER = HERE / "look_path_driver.py"
V2 = "suite-v2"
PAIRED = "h_byte_identity"
V2_ASSERTION = "wrong blind code or leg"
SUPERSEDED = {
    "meter_absent_fresh": ("L002",),
    "meter_absent_disposed": ("L002",),
    "dc_only_three_hidden": ("L002", "L005", "L008"),
    "dc_four_hidden_two_levels": ("L005", "L012"),
}


def cases():
    for suite, program in (("suite", "run_suite.py"), (V2, "run_cases.py")):
        for case in json.loads((FIXTURES / suite / "cases.json").read_bytes()):
            yield suite, program, case["id"]
    suite = "suite-v3"
    vectors = json.loads((FIXTURES / suite / "vectors.json").read_bytes())
    for case in vectors["cases"]:
        yield suite, "run_cases.py", case["id"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def _projection_evidence(failure, frozen, case, base):
    """Prove the exact changed predicate and recheck the complete v2 projection."""
    compare = frozen["check_certificates"]
    raw_require = frozen["v1"].require
    frames = [frame for frame, _ in walk_tb(failure.__traceback__)]
    require(str(failure) == V2_ASSERTION and
            [frame.f_code for frame in frames[-2:]] == [compare.__code__, raw_require.__code__],
            "failure is outside the superseded certificate assertion")

    affected = SUPERSEDED[case["id"]]
    profile = case["profile"]
    missing = frozen["missing"]
    require(missing(profile) == dict.fromkeys(affected, "meter_absent"),
            "the frozen affected leg set or original expected code changed")
    first = frames[-2].f_locals
    require(first["leg"] == affected[0] and first["code"] == "meter_absent"
            and first["cert"]["leg_id"] == affected[0] and first["cert"]["dc_code"] == "not_bracketed",
            "first raw mismatch is not the approved leg and code")

    world = base / "source"
    parent = base / "bench/private/lm-ctl-01"

    def expected_code(profile_name):
        expected = missing(profile_name)
        if profile_name == profile:
            return {**expected, **dict.fromkeys(affected, "not_bracketed")}
        return expected

    # The raw case has already failed. Replay only its certificate validator
    # against the same immutable observations, changing just the expected code.
    with patch.dict(compare.__globals__, {"missing": expected_code}):
        pins, _ = compare(world, parent, profile)

    evidence = []
    for leg in affected:
        cert = frozen["v1"].read(parent / "certificates" / f"{leg}.json")
        require(cert["candidates"] == [], f"{leg} has a stream candidate")
        evidence.append({
            "expected_leg_id": leg,
            "observed_leg_id": cert["leg_id"],
            "expected_dc_code": "meter_absent",
            "observed_dc_code": cert["dc_code"],
            "certificate_sha256": pins[leg],
        })
    return {"assertion": V2_ASSERTION, "complete_certificate_recheck": True, "affected": evidence}


def historical_case(name, proof_path):
    """Execute the original frozen callable and preserve its failing exit."""
    suite = FIXTURES / V2
    sys.path.insert(0, str(suite))
    frozen = runpy.run_path(str(suite / "run_cases.py"))
    case, = (row for row in json.loads((suite / "cases.json").read_bytes()) if row["id"] == name)
    with TemporaryDirectory(prefix="ctl-v2-raw-") as directory:
        base = Path(directory)
        try:
            frozen["run"](case, DRIVER, base)
        except ValueError as failure:
            try:
                evidence = _projection_evidence(failure, frozen, case, base)
            except Exception as error:
                evidence = {"unresolved": str(error)}
            proof_path.write_text(json.dumps(evidence, sort_keys=True), encoding="utf-8")
            raise
    print("PASS", name)


def case_verdict(row):
    """Allow only an actual pass or the four certified historical mismatches."""
    name = row["case"]
    proof = row["supersession"]
    require(type(row["returncode"]) is int and type(row["stdout"]) is str and type(row["stderr"]) is str,
            f"{name} has malformed raw output")
    if row["suite"] != V2 or name not in SUPERSEDED:
        require((row["returncode"], row["stdout"], row["stderr"], proof)
                == (0, f"PASS {name}\n", "", None),
                f"{row['suite']}/{name} did not pass the original oracle")
        return "PASS"

    require(row["returncode"] == 1 and row["stdout"] == ""
            and row["stderr"].endswith(f"\nValueError: {V2_ASSERTION}\n"),
            f"{name} did not fail exactly at the historical assertion")
    require(type(proof) is dict and proof.keys() == {"assertion", "complete_certificate_recheck", "affected"}
            and proof["assertion"] == V2_ASSERTION and proof["complete_certificate_recheck"] is True,
            f"{name} has no exact mismatch proof")
    affected = proof["affected"]
    require(type(affected) is list and len(affected) == len(SUPERSEDED[name]), f"{name} affected-leg count")
    for leg, observed in zip(SUPERSEDED[name], affected, strict=True):
        require(type(observed) is dict and observed.keys() ==
                {"expected_leg_id", "observed_leg_id", "expected_dc_code", "observed_dc_code", "certificate_sha256"}
                and (observed["expected_leg_id"], observed["observed_leg_id"],
                     observed["expected_dc_code"], observed["observed_dc_code"])
                == (leg, leg, "meter_absent", "not_bracketed")
                and re.fullmatch("[0-9a-f]{64}", observed["certificate_sha256"]) is not None,
                f"{name} is missing the approved code-only mismatch for {leg}")
    return "SUPERSEDED"


def run_case(suite, program, name, results):
    print(f"RUN {suite}/{name}", flush=True)
    with TemporaryDirectory(prefix="proof-", dir=results) as directory:
        proof = Path(directory) / "proof.json"
        if suite == V2 and name in SUPERSEDED:
            args = [str(Path(__file__).resolve()), "historical", name, str(proof)]
        else:
            args = [str(FIXTURES / suite / program), "--driver", str(DRIVER), "--case", name]
        raw = subprocess.run([sys.executable, "-B", *args], capture_output=True, check=False)
        try:
            evidence = json.loads(proof.read_bytes()) if proof.exists() else None
        except (OSError, ValueError) as error:
            evidence = {"unresolved": str(error)}
        row = {
            "suite": suite, "case": name, "returncode": raw.returncode,
            "stdout": raw.stdout.decode("utf-8", errors="surrogateescape"),
            "stderr": raw.stderr.decode("utf-8", errors="surrogateescape"),
            "supersession": evidence,
        }
    (results / f"{suite}.{name}.json").write_text(json.dumps(row, sort_keys=True) + "\n", encoding="utf-8")
    if raw.stdout:
        sys.stdout.buffer.write(raw.stdout)
        sys.stdout.flush()
    if raw.stderr:
        sys.stderr.buffer.write(raw.stderr)
        sys.stderr.flush()
    try:
        verdict = case_verdict(row)
    except (KeyError, TypeError, ValueError) as error:
        print(f"FAIL {suite}/{name}: {error}", flush=True)
        return False
    if verdict == "SUPERSEDED":
        print(f"SUPERSEDED {suite}/{name}: exact code-only mismatch", flush=True)
    return True


def check_cumulative(results):
    expected = {(suite, name) for suite, _, name in cases()}
    require(len(expected) == 79, "frozen case inventory differs")
    seen = set()
    raw_passes = 0
    for path in sorted(results.rglob("*.json")):
        row = json.loads(path.read_bytes())
        require(row.keys() == {"suite", "case", "returncode", "stdout", "stderr", "supersession"},
                f"invalid outcome record {path.name}")
        key = (row["suite"], row["case"])
        require(key in expected and key not in seen, f"unexpected or duplicate outcome {key}")
        seen.add(key)
        raw_passes += case_verdict(row) == "PASS"
    require(seen == expected, f"missing outcomes: {sorted(expected - seen)}")
    require(raw_passes == 75, "raw pass count differs")
    print("Cumulative bundle gate PASS. 75/79 raw, with four superseded assertions.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    run = commands.add_parser("run")
    run.add_argument("results", type=Path)
    run.add_argument("--shard", type=int, default=0)
    run.add_argument("--total", type=int, default=1)
    run.add_argument("--paired", action="store_true")
    check = commands.add_parser("check")
    check.add_argument("results", type=Path)
    historical = commands.add_parser("historical")
    historical.add_argument("name", choices=SUPERSEDED)
    historical.add_argument("proof", type=Path)
    args = parser.parse_args()
    if args.operation == "historical":
        historical_case(args.name, args.proof)
        return 0
    if args.operation == "check":
        check_cumulative(args.results)
        return 0

    if not 0 <= args.shard < args.total:
        parser.error("shard must be in [0, total)")
    args.results.mkdir(parents=True, exist_ok=True)
    ok = True
    for index, (suite, program, name) in enumerate(cases()):
        if (name == PAIRED) == args.paired and index % args.total == args.shard:
            ok = run_case(suite, program, name, args.results) and ok
    return int(not ok)


if __name__ == "__main__":
    raise SystemExit(main())
