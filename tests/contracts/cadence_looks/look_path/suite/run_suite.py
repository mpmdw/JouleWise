"""Frozen synthetic acceptance. A driver adapts an installed candidate to the test bench."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
IDS = [f"L{i:03}" for i in range(1, 13)]
BASE = {"cpu_rail": 2, "gpu_rail": 3, "rail_sum": 6}
EXCESS = {"cpu_rail": 1, "gpu_rail": 2, "rail_sum": 3.5, "dc_in": 4}
HIDDEN = {"L002": 512, "L005": 128, "L008": 256, "L009": 512, "L011": 256, "L012": 128}
NS = 10**9


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_bytes())


def dump(path, doc):
    path.write_text(json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_freeze():
    lines = (HERE/"SUITE.sha256").read_text().splitlines()
    files = {p.name for p in HERE.iterdir() if p.name != "SUITE.sha256"}
    pins = {}
    for line in lines:
        checksum, name = line.split("  ", 1)
        require(name in files and name not in pins and sha(HERE/name) == checksum, "suite digest: "+name)
        pins[name] = checksum
    require(set(pins) == files, "suite inventory")


def unpack(out):
    with tarfile.open(HERE/"bundles.tar.xz") as archive:
        members = archive.getmembers()
        require(all(m.isfile() and not Path(m.name).is_absolute() and ".." not in Path(m.name).parts
                    for m in members), "unexpected archive member")
        require(len({m.name for m in members}) == len(members), "duplicate member")
        archive.extractall(out, members=members, filter="data")


def location(world, leg):
    span = world/"spans"/("ctl-01-s01" if int(leg[1:]) <= 3 else "ctl-01-s02")
    runtime = span/"legs"/leg/"runtime"
    return span, runtime, runtime/read(runtime/"runtime_result.json")["bundle"]


def meter(span):
    return span/"hazards/meter/stream-001.jsonl"


def reanchor(world, span):
    # Only for deliberate changes made at *synthetic close*, before the candidate's registration.
    checks = read(world/"authority/check.json")
    local = checks[span.name]
    for rel in list(local):
        path = span/rel
        if path.name == "runtime_custody.json":
            terminal = read(path)
            terminal["files"] = {n:sha(path.parent/n) for n in terminal["files"]}
            dump(path, terminal)
        if path.name == "runner_receipt.json":
            receipt = read(path)
            for entry in receipt["feeds"]["meter"]["files"]:
                entry["sha256"] = sha(span/entry["path"])
            dump(path, receipt)
        local[rel] = sha(path)
    dump(world/"authority/check.json", checks)


def mutate(world, env, name):
    if not name:
        return
    span, runtime, bundle = location(world, "L002")
    raw = meter(span)
    csv_path = bundle/"power_trace.csv"
    hold_path = world/"instrument/hold.json"
    if name in {"hold_null","hold_unknown","hold_mismatch","zero_sd"}:
        hold = read(hold_path)
        a, b = hold.values()
        b["reference_source_leg_id"] = "L001"
        if name == "hold_mismatch":
            hold["f2-inst-01/L001"] = {"value":None,"reason":"interval_ledger_mismatch"}
        elif name == "zero_sd":
            for member in (a,b):
                member["dc_in"]["sd10_w"] = 0
        else:
            reason = "meter_gap" if name == "hold_null" else "invented-unknown"
            a["dc_in"]["sd128_w"] = {"value":None,"reason":reason}
            a["dc_in"]["kept"][2], a["dc_in"]["dropped"][2] = 1, 3
            a["gpu_rail"]["sd10_w"] = {"value":None,"reason":"fewer_than_two"}
            a["gpu_rail"]["kept"][0], a["gpu_rail"]["dropped"][0] = 1, 59
        # A different surviving member makes inclusion of a substituted zero detectable.
        b["dc_in"]["sd128_w"] = 3
        b["gpu_rail"]["sd10_w"] = 2
        dump(hold_path, hold)
        return
    if name.startswith("remove_") or name == "replace_dc_with_csv":
        for stream in (world/"spans").glob("*/hazards/meter/stream-*.jsonl"):
            stream.unlink()
        if name == "remove_rails_and_dc":
            for path in (world/"spans").rglob("power_trace.csv"):
                path.unlink()
        if name == "replace_dc_with_csv":
            for leg in IDS:
                sp, _, b = location(world, leg)
                for path in (sp/"legs"/leg/"dc_points.csv", b/"dc_points.csv"):
                    path.write_text("epoch_s,watts\n1,17\n2,17\n")
        return
    if name in {"omit_ane","rail_gap","swap_rail_value","forge_runtime_map"}:
        start = read(runtime/"script-work.json")["steps"][0]["first_token_ns"] / NS + 18000
        with csv_path.open(newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        if name == "omit_ane":
            rows = [r for r in rows if r["rail"] != "ane_power"]
        elif name == "rail_gap":
            rows = [r for r in rows if not start+.2 < float(r["timestamp_s"]) <= start+1.5]
        else:
            rows[0]["power_w"] = "9"
        with csv_path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        if name == "forge_runtime_map":
            path = runtime/"runtime_custody.json"
            doc = read(path)
            doc["files"][csv_path.relative_to(runtime).as_posix()] = sha(csv_path)
            dump(path, doc)
        if name in {"omit_ane","rail_gap"}:
            reanchor(world, span)
        return
    if name == "tamper_dc_value":
        # The header and counters, number of polls, length, and allocation to legs all stay valid.
        import re
        data = bytearray(raw.read_bytes())
        payload = re.search(rb'"p":"([0-9a-f]{40,})"', data)
        require(payload is not None, "frozen batch payload")
        digit = payload.start(1)+8  # first sample, immediately after seq/marker
        data[digit] = ord("1") if data[digit] != ord("1") else ord("2")
        raw.write_bytes(data)
        return
    if name in {"wrong_span_points","dc_gap","overlap"}:
        if name == "wrong_span_points":
            raw.write_bytes(meter(world/"spans/ctl-01-s02").read_bytes())
        elif name == "overlap":
            path = bundle/"outputs/align_episode.json"
            doc = read(path)
            # Leave the first physical step strictly after the G0 end. This must
            # reach the frozen tiler instead of tripping the earlier step-order check.
            doc["start_ns"] -= 2
            for field in ("epoch_ns","monotonic_before_ns","monotonic_after_ns"):
                doc["hardware"]["paired_clock_stamps_ns"][0][field] -= 2
            doc["hardware"]["thermal"]["intervals"][0]["end_ns"] = doc["start_ns"]+1
            dump(path, doc)
        else:
            a = read(runtime/"script-work.json")["steps"][-1]["started_ns"] + 27*NS  # recovery + 20 s on RAW
            with raw.open() as stream:
                records = [json.loads(line) for line in stream]
            keep = [r for r in records if r["k"] != "b" or not a <= r["rx"] < a+2_500_000_000]
            keep[-1]["polls"] = sum(r["k"] == "b" for r in keep)
            with raw.open("w") as stream:
                for row in keep:
                    stream.write(json.dumps(row, separators=(",", ":"))+"\n")
        reanchor(world, span)
        return
    if name == "stale_stage1":
        with (env/"private/lm-ctl-01/stage1.json").open("ab") as stream:
            stream.write(b" ")
        return
    if name == "chmod_public":
        (env/"public/lm-ctl-01").chmod(0o555)
        return
    if name in {"empty_claim","orphan_streams"}:
        claim = env/"private/lm-ctl-01/RESTRICTED"
        claim.mkdir(mode=0o700)
        if name == "orphan_streams":
            for child in ("stdout","stderr"):
                (claim/child).touch(mode=0o600)
        return
    raise ValueError(name)


def check_stage1(parent,world):
    stage = read(parent/"stage1.json")
    inventory = parent/"inputs.v1.json"
    require(set(stage)=={"schema","n_legs","legs","input_inventory_sha256"} and
            stage["schema"]=="joulewise.cadence_ctl_stage1.v2" and stage["n_legs"]==12 and
            set(stage["legs"])==set(IDS) and stage["input_inventory_sha256"]==sha(inventory), "stage1 inventory pin")
    bound=read(inventory)
    require(set(bound)=={"schema","kit_sha256","runner_commit","spans","positions"} and
            set(bound["positions"])==set(IDS) and set(bound["spans"])=={"ctl-01-s01","ctl-01-s02"},
            "stage1 position and span inventory")
    for lid in IDS:
        _,rt,bundle=location(world,lid)
        spec=read(rt.parent/"leg_spec.json")
        row=stage["legs"][lid]
        number=1 if lid<="L003" else 2
        capture = "L001" if number==1 else "L004"
        _,_,source=location(world,capture)
        reference=read(source/"outputs/align_window_reference.json")["record_sha256"]
        require(row["identity"]==["cl-ctl-01",bound["kit_sha256"],bound["runner_commit"],number,lid,1] and
                row["role"]==spec["g0_role"] and row["reference"]==reference and
                row["kind"]==spec["script"]["kind"] and row["admitted"] is True and row["g0_released"] is True and
                row["episode_id"]==bundle.name and row["episode_sha256"]==sha(bundle/"outputs/align_episode.json")
                and row["script_sha"]==sha(rt/"script-work.json"),"stage1 original-byte identity for "+lid)


def numeric(actual, expected, field):
    require(type(actual) in (int,float) and math.isfinite(actual) and
            math.isclose(actual,expected,rel_tol=2e-7,abs_tol=2e-6), field)


def check_report(public, report, stage_digest, case):
    require(set(public) == {"look_id","commit","stage1_sha256","manifest_sha256","n_legs"} and
            public["look_id"] == "lm-ctl-01" and public["n_legs"] == 12 and
            public["stage1_sha256"] == stage_digest, "blind report")
    for key, length in (("commit",40),("manifest_sha256",64)):
        v = public[key]
        require(isinstance(v,str) and len(v)==length and all(c in "0123456789abcdef" for c in v), key)
    require([leg["leg_id"] for leg in report["legs"]] == IDS, "private roster")
    quality, floor = case.get("quality"), case.get("floor")
    alignment=report["aligned_power"]
    require(report["timing_edge_j"]==1 and alignment["cpu_burn_order"] is True, "registered timing edge and burn order")
    if quality!="rail_gap":
        expected_word = "no" if quality=="bad_leg" else "yes"
        require(alignment["qualified"]==expected_word and alignment["all_legs_close"]==(expected_word=="yes"),
                "rail qualifier")
    for leg in report["legs"]:
        lid = leg["leg_id"]
        if lid=="L002" and quality=="bad_leg":
            require(leg["disposition"]=="not_evaluable" and bool(leg["reason"]), "leg isolation")
            continue
        require(set(leg["channels"]) == set(EXCESS), "four channels")
        for channel, excess in EXCESS.items():
            c = leg["channels"][channel]
            base = 10+int(lid[1:]) if channel=="dc_in" else BASE[channel]
            if lid=="L002" and channel=="dc_in" and quality=="dc_gap":
                require(c["reason"]=="gap_over_u1" and "absolute" not in c, "DC gap")
                continue
            numeric(c["baseline_w"],base,lid+"/"+channel+"/baseline")
            numeric(c["absolute"]["phases"]["prefill"]["joules"],
                    c["absolute"]["phases"]["prefill"]["seconds"]*(base+excess),"absolute prefill")
            # A new rail-gap disposition needs a separately authorized freeze.
            if lid in HIDDEN:
                h = c["hidden"]
                numeric(h["call_j"], excess*(2 + HIDDEN[lid]*.01), "hidden excess")
                numeric(h["prefill_j"], excess*2, "hidden prefill")
                numeric(h["decode_j"], excess*HIDDEN[lid]*.01, "hidden decode")
                numeric(h["j_per_token"], excess*.01, "hidden rate")
                require(h["delivered_tokens"]==HIDDEN[lid] and h["tail_cut"]==(channel=="dc_in"), "hidden identity")
            if floor=="one_survivor" and channel in ("gpu_rail","dc_in"):
                f = c["phase_floors"]["prefill"] if channel=="gpu_rail" else c["other"]["recovery"]["floor"]
                seconds = c["absolute"]["phases"]["prefill"]["seconds"] if channel=="gpu_rail" else 600
                numeric(f["floor_j"], seconds*(2 if channel=="gpu_rail" else 3), "survivor pool")
            if floor=="zero" and channel=="dc_in":
                f = c["phase_floors"]["prefill"]
                require(f["floor_j"]==0 and f["units"] is None, "zero denominator")
            if channel=="cpu_rail":
                f = c["phase_floors"]["prefill"]
                require(f["units"] is None and f["reason"]=="no_matched_floor", "CPU floor")
    for channel, excess in EXCESS.items():
        fit=report["dose_response"][channel]
        ids = set(HIDDEN)
        if quality=="bad_leg" or (quality=="dc_gap" and channel=="dc_in"):
            ids.remove("L002")
        require(set(fit["legs"])==ids and len(fit["range"])==2, "fit membership")
        for value in [fit["slope"], *fit["range"]]:
            numeric(value, excess*.01, "dose slope")
        numeric(fit["intercept"], 2*excess, "dose intercept")


def run_case(driver, base, case):
    case_id = case["id"]
    world, env = base/"source", base/"bench"
    unpack(world)
    env.mkdir()
    for kind in ("public","private"):
        (env/kind/"lm-ctl-01").mkdir(parents=True,mode=0o700)
    public_dir = env/"public/lm-ctl-01"
    parent = env/"private/lm-ctl-01"
    claim, marker, output = parent/"RESTRICTED", parent/"read-started", public_dir/"PUBLIC.json"
    witness = env/"events.jsonl"
    witness.touch()
    fault = case.get("fault","none")
    def invoke(op, injected="none"):
        return subprocess.run([driver,op,str(world),str(env),injected],capture_output=True)
    def events():
        return [json.loads(line) for line in witness.read_text().splitlines()]
    def fresh():
        require(not any(p.exists() for p in (claim,marker,output)) and not events(), "fresh boundary")
        require(not any(public_dir.iterdir()), "public probe residue")
    def read_order(success):
        e = events()
        require(e.count("claim")==1 and e.count("start")==1 and e.index("claim") < e.index("start"), "claim order")
        if success:
            require(e.count("first_read")==1 and e.index("first_read") > e.index("start") and
                    "ctl_value_decode" in e and e.index("ctl_value_decode") > e.index("first_read"), "read order")
        require(all(i > e.index("start") for i,v in enumerate(e) if v in ("first_read","ctl_value_decode")), "early read")
    def success(r):
        require(r.returncode==0 and not r.stdout and not r.stderr and marker.is_file(), "look success")
        require({p.name for p in claim.iterdir()}=={"stdout","stderr","controls.json"} and
                {p.name for p in public_dir.iterdir()}=={"PUBLIC.json"}, "output inventory")
        public = read(output)
        require(public == read(env/"registered-public.json"), "public fields differ from independent ledger")
        check_report(public, read(claim/"controls.json"), sha(parent/"stage1.json"), case)
        read_order(True)
    try:
        mutate(world,env,case.get("before"))
        require(invoke("install", fault if fault in {"other_worktree_parent","tracked_hold_blob","sibling_ledger_only","kernel_matches_manifest_but_not_byte_pass"} else "none").returncode==0, "test registration")
        stage = invoke("stage1")
        if stage.returncode:
            require(case["expect"]=="fresh" and (case.get("before") or fault!="none") and not stage.stdout and
                    stage.returncode==2 and stage.stderr==f"REFUSE PREFLIGHT {case['token']}\n".encode(),
                    "unexpected stage1 refusal")
            fresh()
            return
        require(not events() and (parent/"stage1.json").is_file(), "stage1 performed value access/claim or no roster")
        check_stage1(parent,world)
        require(invoke("commit-stage1").returncode==0,"test registrar")
        mutate(world,env,case.get("after"))
        if case_id=="0555_public_dir":
            require(not os.access(public_dir, os.W_OK), "run link test as an unprivileged account")
        if case_id in ("bundle_ok","0555_public_dir"):
            for _ in range(2):
                probe = invoke("preflight")
                require(probe.returncode==(2 if case_id=="0555_public_dir" else 0) and
                        not probe.stdout and probe.stderr==(b"REFUSE PREFLIGHT PUBLIC_LINK\n"
                        if case_id=="0555_public_dir" else b""), "standalone preflight")
                fresh()
        r = invoke("stage2", fault)
        expected = case["expect"]
        if expected=="fresh":
            require(r.returncode==2 and not r.stdout and r.stderr==f"REFUSE PREFLIGHT {case['token']}\n".encode(),
                    "fresh diagnostic")
            fresh()
        elif expected=="success":
            success(r)
        elif expected=="half":
            require(r.returncode==4 and r.stderr==b"REFUSE HALF_MADE\n" and not r.stdout and not events() and
                    claim.is_dir() and not marker.exists() and not output.exists(), "half-made refusal")
            require({p.name for p in claim.iterdir()}==({"stdout","stderr"} if case["after"]=="orphan_streams" else set()),
                    "modified orphan claim")
        elif expected=="post_failure":
            require(r.returncode==1 and r.stderr==b"stage2_error\nOSError\n" and not r.stdout and
                    marker.is_file() and not output.exists(), "spent failure")
            read_order(False)
        elif expected=="rollback":
            require(r.returncode==2 and not r.stdout and r.stderr==b"REFUSE PREFLIGHT CLAIM_SETUP\n" and
                    not any(p.exists() for p in (claim,marker,output)) and events()==["claim"], "claim rollback")
            # New invocation has its own observer interval; preserve all filesystem state.
            witness.write_bytes(b"")
        else:
            raise ValueError(expected)
        if case.get("retry")=="spent":
            before = events()
            old = {p:sha(p) for p in [marker,output,*claim.iterdir()] if p.is_file()}
            r = invoke("stage2")
            require(r.returncode==3 and not r.stdout and r.stderr==b"REFUSE SPENT\n" and events()==before and
                    all(sha(p)==v for p,v in old.items()), "spent retry")
        elif case.get("retry")=="success":
            success(invoke("stage2"))
    finally:
        public_dir.chmod(0o700)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--driver",type=Path,required=True)
    p.add_argument("--case",action="append",help="limit to named cases")
    args=p.parse_args()
    verify_freeze()
    cases=read(HERE/"cases.json")
    require(not args.case or set(args.case)<={c["id"] for c in cases}, "unknown case")
    for case in cases:
        if not args.case or case["id"] in args.case:
            with tempfile.TemporaryDirectory(prefix="ctl-synth-") as folder:
                run_case(str(args.driver.resolve(strict=True)),Path(folder),case)
            print("PASS",case["id"])


if __name__ == "__main__":
    main()
