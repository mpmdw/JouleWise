"""Verify synthetic vectors using the pinned production decoder, without running a look."""
import argparse
import ast
from bisect import bisect_left, bisect_right
from hashlib import sha256
import inspect
import math
from fractions import Fraction
from pathlib import Path
import subprocess
import tempfile

from fixtures import CODES, EPOCH_OFFSET, LEG, NS, RAW_OFFSET, ROOT, STEP, expected_h, make, missing, original_bounds, v1


def hold_inventory(repo):
    spec = v1.read(ROOT / "lm-ctl-01.hold-reasons.v1.json")
    source = subprocess.check_output(["git", "-C", str(repo), "show",
                                     spec["instrument_commit"] + ":" + spec["writer"]["path"]])
    v1.require(sha256(source).hexdigest() == spec["writer"]["sha256"], "instrument source hash")
    tree = ast.parse(source)
    functions = {f.name:f for f in ast.walk(tree) if isinstance(f, ast.FunctionDef)}
    leaves = set()
    for name in ("_stream_refusal", "_interval_refusal"):
        for node in ast.walk(functions[name]):
            if isinstance(node, ast.Return) and node.value is not None:
                expr = node.value
                branches = [expr.body, expr.orelse] if isinstance(expr, ast.IfExp) else [expr]
                for branch in branches:
                    if isinstance(branch, ast.Constant) and isinstance(branch.value, str):
                        leaves.add(branch.value)
    for name in ("deviation", "_drift"):
        for node in ast.walk(functions[name]):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "missing":
                leaves.add(ast.literal_eval(node.args[0]))
    whole = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
                 and any(isinstance(t, ast.Name) and t.id=="INTERVAL_LEDGER_MISMATCH" for t in n.targets))
    v1.require(set(spec["leaf_reasons"]) == leaves and spec["whole_member_reasons"] == [whole], "hold inventory")
    v1.require("missing(INTERVAL_LEDGER_MISMATCH)" in ast.unparse(functions["_leg_values"]), "whole-member writer")


def inspect_stream(kp, path):
    stream = kp.parse(path)
    h, t = stream.header, stream.trailer
    lo = h["start_mono_ns"]
    if not stream.present:
        return lo, t["end_mono_ns"], "meter_absent", None, []
    off = kp.raw_offset_ns(stream, allow_unclosed=False)
    if t is None:
        return lo, stream.host_ns[-1]-RAW_OFFSET, "stream_unclosed", None, []
    hi = t["end_mono_ns"]
    if not stream.fit or off is None:
        return lo, hi, "anchor_unusable", None, []
    stats = stream.fit.stats
    r = kp.FIT_MAX_RTT_MS if stats["filtered"] else stats["request_rtt_ms_max"]
    fit_ns = 1_000_000 * (max(0, -Fraction(stats["excess_latency_ms_min"])) + Fraction(r))
    half = abs(t["end_raw_ns"]-hi-off) + 1_000_000 + kp.STEP_MS[h["rate_idx"]]*1_000_000 + math.ceil(fit_ns)
    v1.require(off == RAW_OFFSET, "signed RAW bridge")
    code = "ok"
    if half > 100_000_000:
        code = "half_width_over_cap"
    elif abs((h["start_real_ns"]-lo)-EPOCH_OFFSET) > 5*NS:
        code = "boot_mismatch"
    return lo, hi, code, half, [raw-off for raw in stream.host_ns]


def verify_profile(kp, world, profile):
    make(world, profile)
    checks = v1.read(world/"authority/check.json")
    for name, files in checks.items():
        span = world/"spans"/name
        v1.require(all(v1.sha(span/rel) == pin for rel, pin in files.items()), "synthetic Check")
        receipt = v1.read(span/"runner_receipt.json")
        decoded = []
        for row in receipt["feeds"]["meter"]["files"]:
            path = span/row["path"]
            v1.require(v1.sha(path) == row["sha256"], "stream receipt digest")
            decoded.append(inspect_stream(kp, path))
        for leg in receipt["roster"]:
            start, end = original_bounds(world, leg)
            containing = [r for r in decoded if r[0] <= start and end <= r[1]]
            if not containing:
                code = "not_bracketed"
            elif len(containing) > 1:
                v1.require(all(r[2]=="ok" and r[4][0]<=start<=end<=r[4][-1] for r in containing),
                           "isolated overlap case")
                code = "ambiguous_overlap"
            else:
                _, _, code, half, times = containing[0]
                if half is not None:
                    v1.require(half == expected_h(profile, leg), f"{leg} H {half}")
                if code == "ok":
                    lo, hi = bisect_right(times,start)-1, bisect_left(times,end)
                    v1.require(0<=lo<hi<len(times) and times[lo:hi+1] ==
                               list(range(start//STEP*STEP, -(-end//STEP)*STEP+1, STEP)), "full DC grid")
                if leg == LEG and profile == "restart_ok":
                    v1.require(containing[0] is decoded[1], "second stream")
            v1.require(code == missing(profile).get(leg, "ok"), f"{profile} {leg} {code}")
    if profile in {"three_left","two_levels"}:
        kept = {leg:level for leg,level in v1.HIDDEN.items() if leg not in missing(profile)}
        v1.require((len(kept),len(set(kept.values()))) == ((3,3) if profile=="three_left" else (4,2)),
                   "DC disposition lower bounds")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--repo", required=True, type=Path, help="public Git objects for the source inventory")
    args = p.parse_args()
    from joulewise.external import km003c_parse as kp
    from check_inputs import READER_PINS
    v1.require(v1.sha(Path(inspect.getfile(kp))) == READER_PINS[kp.__name__], "decoder source pin")
    hold_inventory(args.repo)
    cases = v1.read(ROOT/"suite-v2/cases.json")
    for profile in sorted({case["profile"] for case in cases}):
        with tempfile.TemporaryDirectory(prefix="ctl-v2-vectors-") as folder:
            world = Path(folder)
            v1.unpack(world)
            verify_profile(kp, world, profile)
        print("PASS", profile, flush=True)
