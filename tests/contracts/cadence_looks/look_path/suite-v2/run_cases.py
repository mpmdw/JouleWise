"""Freeze-2 normal-entry acceptance. Requires an independent installed candidate driver."""
import argparse
import builtins
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from fixtures import LEG, RAW_OFFSET, ROOT, STEP, expected_h, make, missing, original_bounds, v1

HERE = Path(__file__).resolve().parent
VOCAB = ROOT/"lm-ctl-01.hold-reasons.v1.json"


def sha_grid(lo, hi):
    first, last = lo//STEP*STEP, -(-hi//STEP)*STEP
    return hashlib.sha256(b"".join(i.to_bytes(8, "big", signed=True)
                                   for i in range(first,last+1,STEP))).hexdigest()


def ledger_proof(parent, certificate_pins, disposition_pin):
    inventory = v1.read(parent/"inputs.v1.json")
    for leg, pin in certificate_pins.items():
        row = inventory["positions"][leg]
        v1.require(row["certificate"]["sha256"] == pin, "private certificate absent from stage1")
        v1.require(row["disposition_sha256"] == disposition_pin, "private disposition commitment")


def check_certificates(world, parent, profile):
    pins, certified = {}, {}
    for leg in v1.IDS:
        path = parent/"certificates"/(leg+".json")
        cert = v1.read(path)
        pins[leg] = v1.sha(path)
        code = missing(profile).get(leg, "ok")
        v1.require(cert["leg_id"] == leg and cert["dc_code"] == code, "wrong blind code or leg")
        if code == "ok":
            span, _, _ = v1.location(world,leg)
            receipts = v1.read(span/"runner_receipt.json")["feeds"]["meter"]["files"]
            member = cert["stream"]
            v1.require(any(r["path"] == member for r in receipts), "unlisted stream")
            if leg == LEG and profile == "restart_ok":
                v1.require(member.endswith("/stream-002.jsonl"), "second stream required")
            digest = sha_grid(*original_bounds(world,leg))
            mapping = {"method":"km003c_raw_monotonic_pairs.v1", "offset_ns":-RAW_OFFSET,
                       "uncertainty_ns":expected_h(profile,leg), "dc_times_sha256":digest}
            v1.require(cert["H_ns"] == mapping["uncertainty_ns"] and cert["dc_times_sha256"] == digest,
                       "certificate half-width or stamps")
            certified[leg] = mapping
        elif code == "half_width_over_cap":
            v1.require(cert["H_ns"] == 101_000_000, "over-cap width")
    return pins, certified


def disposition(world, case, pins):
    action = case.get("disposition")
    if not action:
        return None
    codes = missing(case["profile"])
    if action == "wrong_code":
        codes = {LEG:"meter_absent"}
    elif action == "on_ok":
        codes = {LEG:"meter_absent"}
    else:
        v1.require(action in {"all_affected","match"}, "unknown disposition")
    path = world/"authority/disposition.json"
    v1.dump(path, {"schema":"joulewise.cadence_ctl_dc_disposition.v1",
                   "legs":[{"leg_id":leg,"code":code,"certificate_sha256":pins[leg]}
                           for leg,code in sorted(codes.items())]})
    return v1.sha(path)


def check_private(report, public, stage_pin, case):
    profile = case["profile"]
    rows = {r["leg_id"]:r for r in report["legs"]}
    v1.require(list(rows) == v1.IDS and len(report["legs"]) == 12, "twelve ordered positions")
    affected = set(missing(profile))
    if not affected and profile != "baseline_gap":
        extra = {"bad_leg":{"quality":"bad_leg"}, "rail_gap":{"quality":"rail_gap"},
                 "zero_sd":{"floor":"zero"}, "hold_null":{"floor":"one_survivor"}}
        v1.check_report(public,report,stage_pin,extra.get(profile,{}))
    if affected:
        v1.require(report["aligned_power"]["qualified"]=="yes", "DC exception changed rail qualifier")
        for leg,row in rows.items():
            for channel,c in row["channels"].items():
                if leg in affected and channel=="dc_in":
                    v1.require(c["reason"]=="trace_or_clock_unavailable" and c["baseline_w"] is None and
                               "absolute" not in c, "disposition should null only that leg's DC")
                else:
                    base = 10+int(leg[1:]) if channel=="dc_in" else v1.BASE[channel]
                    v1.numeric(c["baseline_w"],base,leg+"/"+channel)
                    v1.require(c["absolute"]["phases"]["prefill"]["joules"] > 0, "missing absolute phase")
            v1.require(set(row["channels"]) == set(v1.EXCESS), "missing channel")
        for channel, excess in v1.EXCESS.items():
            fit = report["dose_response"][channel]
            kept = set(v1.HIDDEN) - (affected if channel=="dc_in" else set())
            v1.require(set(fit["legs"]) == kept, "admission changed outside disposed DC leg")
            v1.numeric(fit["slope"],excess*.01,"surviving slope")
    if profile == "bad_leg":
        row = rows[LEG]
        v1.require(row["reason"]=="leg_record_invalid" and row["disposition"]=="not_evaluable"
                   and "channels" not in row, "local frozen-call exception")
    if profile == "rail_gap":
        marks = [{"leg_id":LEG, "channel":c, "part":"hidden_decode"} for c in ("cpu_rail","gpu_rail","rail_sum")]
        v1.require(report.get("rail_gap_marks") == marks, "one sorted mark per affected printed channel")
        v1.require(report["aligned_power"]["qualified"]=="yes" and report["aligned_power"]["all_legs_close"]
                   and all(rows[LEG]["channels"][c]["absolute"]["closes"] is True for c in v1.BASE),
                   "mark changed the frozen closure or qualifier")
    elif profile != "baseline_gap":
        v1.require("rail_gap_marks" not in report, "empty marks must be omitted")
    if profile in {"zero_sd","original","baseline_gap"}:
        for lid,row in rows.items():
            floor = row["channels"]["gpu_rail"]["phase_floors"]["tool"]
            expected = "gap_over_u1" if profile=="baseline_gap" and lid==LEG else None
            v1.require(floor["duration_s"] == 0 and floor["floor_j"] == 0 and floor["units"] is None
                       and floor["reason"] == expected, "zero-duration floor or baseline precedence")
            if profile=="zero_sd":
                f = row["channels"]["dc_in"]["phase_floors"]["prefill"]
                v1.require(f["duration_s"]>0 and f["floor_j"]==0 and f["units"] is None and f["reason"] is None,
                           "zero pooled SD")


def run(case, driver, base):
    world, bench = base/"source", base/"bench"
    v1.unpack(world)
    make(world,case["profile"])
    parent, public = bench/"private/lm-ctl-01", bench/"public/lm-ctl-01"
    for directory in (parent,public):
        directory.mkdir(parents=True,mode=0o700)
    witness = bench/"events.jsonl"
    witness.touch()

    def invoke(op, fault="none"):
        return subprocess.run([str(driver),op,str(world),str(bench),fault],capture_output=True)

    def clean(proc):
        v1.require(proc.returncode==0 and not proc.stdout and not proc.stderr, "blind successful operation")

    def events():
        return [json.loads(line) for line in witness.read_text().splitlines()]

    def fresh():
        v1.require(not events() and not (parent/"RESTRICTED").exists() and
                   not (parent/"read-started").exists() and not list(public.iterdir()), "fresh state")

    def refused(proc, token):
        v1.require(proc.returncode==2 and not proc.stdout and proc.stderr==
                   f"REFUSE PREFLIGHT {token}\n".encode(), "wrong preflight refusal")
        fresh()

    # install-v2 takes the byte-pinned fallback with the original open instrument schema.
    clean(invoke("install-v2"))
    clean(invoke("project"))
    fresh()
    pins, supported = check_certificates(world,parent,case["profile"])
    disp = disposition(world,case,pins)
    if disp:
        clean(invoke("attest-disposition"))
    want = case.get("expect","success")
    stage = invoke("stage1")
    if stage.returncode:
        v1.require(want in {"INPUT_CHANNELS","INSTRUMENT_HOLD_BINDING"}, "unexpected stage1 refusal")
        refused(stage,want)
        return
    clean(stage)
    fresh()
    v1.check_stage1(parent,world)
    ledger_proof(parent,pins,disp)
    clean(invoke("commit-stage1"))
    probe = invoke("preflight")
    if want in {"INPUT_CHANNELS","INSTRUMENT_HOLD_BINDING"}:
        refused(probe,want)
        refused(invoke("stage2"),want)
        return
    clean(probe)
    fresh()
    proc = invoke("stage2",case.get("fault","none"))
    trace = events()
    v1.require(trace[:3] == ["claim","start","first_read"] and trace.count("claim")==trace.count("start")==
               trace.count("first_read")==1 and (parent/"read-started").is_file(), "read boundary")
    if want == "spent_failure":
        names = {name for name,cls in vars(builtins).items() if isinstance(cls,type) and
                 issubclass(cls,BaseException) and cls.__name__==name} | {"OtherError","JSONDecodeError","LinAlgError"}
        v1.require(proc.returncode==1 and not proc.stdout and proc.stderr in
                   {f"stage2_error\n{name}\n".encode() for name in names} and not list(public.iterdir()),
                   "post-start integrity fault")
        if case["fault"]=="decoder_one_stamp":
            v1.require("ctl_value_decode" in trace, "must reach the actual decoder")
        retry = invoke("stage2")
        v1.require(retry.returncode==3 and not retry.stdout and retry.stderr==b"REFUSE SPENT\n"
                   and events()==trace and not list(public.iterdir()), "failed read remained spent")
        return
    clean(proc)
    v1.require("ctl_value_decode" in trace[3:] and {p.name for p in public.iterdir()}=={"PUBLIC.json"}
               and {p.name for p in (parent/"RESTRICTED").iterdir()}=={"controls.json","stdout","stderr"},
               "success inventory")
    observed = v1.read(bench/"joined-observed.json")
    v1.require(observed == supported, "actual per-leg DC mappings differ from certificate")
    result = v1.read(public/"PUBLIC.json")
    stage_pin = v1.sha(parent/"stage1.json")
    v1.require(result==v1.read(bench/"registered-public.json") and
               set(result)=={"look_id","manifest_sha256","commit","stage1_sha256","n_legs"} and
               result["stage1_sha256"]==stage_pin and result["look_id"]=="lm-ctl-01" and result["n_legs"]==12,
               "public output or commitment")
    check_private(v1.read(parent/"RESTRICTED/controls.json"),result,stage_pin,case)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", required=True, type=Path)
    parser.add_argument("--case", action="append")
    args = parser.parse_args()
    v1.verify_freeze()
    for line in (ROOT/"SUITE-v2.sha256").read_text().splitlines():
        pin, name = line.split("  ",1)
        v1.require(v1.sha(ROOT/name)==pin, "freeze-2 manifest entry")
    cases = v1.read(HERE/"cases.json")
    v1.require(not args.case or set(args.case)<={c["id"] for c in cases}, "unknown case")
    for case in cases:
        if not args.case or case["id"] in args.case:
            with tempfile.TemporaryDirectory(prefix="ctl-v2-") as folder:
                run(case,args.driver.resolve(strict=True),Path(folder))
            print("PASS",case["id"],flush=True)
