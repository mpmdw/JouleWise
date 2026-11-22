"""Freeze-3 acceptance through an independently installed launcher and test registrar."""
import argparse
from pathlib import Path
import subprocess
import tempfile

from bundle_cases import ROOT, TARGET, catalog, expected_candidates, leg_codes, materialize, source_number, v1
from run_cases_v3_support import check_outputs, inspect_pair


def invoke(driver, op, world, bench, fault="none"):
    return subprocess.run([str(driver), op, str(world), str(bench), fault], capture_output=True)


def success(proc):
    v1.require((proc.returncode, proc.stdout, proc.stderr) == (0, b"", b""), "blind operation failed")


def private(bench):
    return bench / "private/lm-ctl-01"


def fresh(bench):
    parent = private(bench)
    v1.require((bench / "events.jsonl").read_bytes() == b"" and
               not (parent / "RESTRICTED").exists() and not (parent / "read-started").exists()
               and not list((bench / "public/lm-ctl-01").iterdir()), "expected fresh reservation")


def refuse(proc, bench):
    v1.require((proc.returncode, proc.stdout, proc.stderr) ==
               (2, b"", b"REFUSE PREFLIGHT INPUT_CHANNELS\n"), "wrong fresh refusal")
    fresh(bench)


def check_certs(bench, world, profile, codes):
    pins = {}
    for leg in v1.IDS:
        path = private(bench) / "certificates" / (leg + ".json")
        cert = v1.read(path)
        v1.require(cert["leg_id"] == leg and cert["dc_code"] == codes.get(leg, "ok"), "leg code " + leg)
        span, _, _ = v1.location(world, leg)
        receipt = v1.read(span / "runner_receipt.json")
        sources = {row["path"] for row in receipt["feeds"]["meter"]["files"]}
        candidates = {}
        for row in cert["candidates"]:
            member, failures = row["stream"], row["failures"]
            v1.require(member in sources and member not in candidates and type(failures) is list and
                       len(set(failures)) == len(failures), "invalid candidate list")
            candidates[member] = sorted(failures)
        if leg == TARGET:
            v1.require(candidates == expected_candidates(profile), "full private list of candidate failures")
        passing = [name for name, failures in candidates.items() if not failures]
        if cert["dc_code"] == "ok":
            v1.require(passing == [cert["stream"]], "sole selected receipt member")
            if leg == TARGET and "selected" in profile:
                v1.require(cert["stream"] == source_number(profile["selected"]), "selected wrong stream")
        else:
            v1.require(not passing, "failed code on a passing stream")
        pins[leg] = v1.sha(path)
    return pins


def run(case, profile, driver, base):
    world, bench = base / "source", base / "bench"
    v1.unpack(world)
    name = case["profile"]
    materialize(world, name, profile)
    for parent in (private(bench), bench / "public/lm-ctl-01"):
        parent.mkdir(mode=0o700, parents=True)
    (bench / "events.jsonl").touch()
    success(invoke(driver, "install-v2", world, bench))
    success(invoke(driver, "project", world, bench))
    fresh(bench)
    codes = leg_codes(name, profile)
    pins = check_certs(bench, world, profile, codes)
    disposition_pin = None
    if "disposition" in case:
        path = world / "authority/disposition.json"
        v1.dump(path, {"schema": "joulewise.cadence_ctl_dc_disposition.v1",
                       "legs": [{"leg_id": leg, "code": case["disposition"], "certificate_sha256": pins[leg]}
                                for leg in sorted(codes)]})
        disposition_pin = v1.sha(path)
        success(invoke(driver, "attest-disposition", world, bench))
    stage = invoke(driver, "stage1", world, bench)
    if stage.returncode:
        v1.require(case["outcome"] == "fresh", "eligible stage 1 refused")
        refuse(stage, bench)
        return
    success(stage)
    fresh(bench)
    parent = private(bench)
    v1.check_stage1(parent, world)
    inventory = v1.read(parent / "inputs.v1.json")["positions"]
    for leg, pin in pins.items():
        v1.require(inventory[leg]["certificate"]["sha256"] == pin and
                   inventory[leg]["disposition_sha256"] == disposition_pin, "stage-1 proof " + leg)
    success(invoke(driver, "commit-stage1", world, bench))
    probe = invoke(driver, "preflight", world, bench)
    if case["outcome"] == "fresh":
        refuse(probe, bench)
        refuse(invoke(driver, "stage2", world, bench), bench)
        return
    success(probe)
    fresh(bench)
    if case["outcome"] == "paired":
        # Clone the still-fresh synthetic registration, including host-visible paths and file identities.
        success(invoke(driver, "clone-fresh", world, bench))
        branches = [(bench, "observe_ruled_h"), (base / "clone", "observe_zero_h")]
    else:
        branches = [(bench, "none")]
    stage_pin = v1.sha(parent / "stage1.json")
    for target, fault in branches:
        fresh(target)
        v1.require(v1.sha(private(target) / "stage1.json") == stage_pin, "changed stage 1")
        success(invoke(driver, "stage2", world, target, fault))
        check_outputs(target, stage_pin, codes)
    if case["outcome"] == "paired":
        inspect_pair(world, branches[0][0], branches[1][0])


def main():
    opts = argparse.ArgumentParser(description=__doc__)
    opts.add_argument("--driver", type=Path, required=True)
    opts.add_argument("--case", action="append")
    args = opts.parse_args()
    driver = args.driver.resolve(strict=True)
    v1.verify_freeze()
    for line in (ROOT / "SUITE-v3.sha256").read_text().splitlines():
        digest, rel = line.split("  ", 1)
        v1.require(v1.sha(ROOT / rel) == digest, "frozen file " + rel)
    data = catalog()
    ids = [c["id"] for c in data["cases"]]
    v1.require(len(ids) == len(set(ids)) and set(args.case or ()) <= set(ids), "case selection")
    for case in data["cases"]:
        if not args.case or case["id"] in args.case:
            with tempfile.TemporaryDirectory(prefix="ctl3-accept-") as folder:
                run(case, data["profiles"][case["profile"]], driver, Path(folder))
            print("PASS", case["id"], flush=True)


if __name__ == "__main__":
    main()
