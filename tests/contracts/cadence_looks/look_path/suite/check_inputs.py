"""Offline check of the frozen synthetic files against the actual runner readers."""
import argparse
from bisect import bisect_left, bisect_right
from pathlib import Path
import tempfile
from run_suite import HIDDEN, IDS, NS, location, meter, numeric, read, require, sha, unpack, verify_freeze


READER_PINS = {
    "joulewise.align.apple.sampler": "988e335f81613f19de904c29a83a073ebbfdaf2a4f213f05f218fa3ff2a4a233",
    "joulewise.align.apple.workload": "837b74be97616c48c26b0c1277fe2a605b575d5cfc4396dc05e1139079daf1ba",
    "joulewise.bundle_read": "dacba842582b2a70fecc3cb5c9502b9ebebc144d7c639657aace6c4a16cafb8d",
    "joulewise.clock": "410d75dbc2d9b3ef50f02dde79a1feb9645c9705faf0f17217bdb11416f85734",
    "joulewise.external.km003c_parse": "6b2e4f57776f03ba39ea644e395d4649d4e7a4ded27dd1e008eda77601fa6e0e"
}


def check(world):
    from importlib import import_module
    for name, pin in READER_PINS.items():
        require(sha(Path(import_module(name).__file__)) == pin, "unexpected source revision: " + name)
    from joulewise.align.apple.workload import read_episode_bundle
    from joulewise.external import km003c_parse as kp
    from joulewise.cadence import ctl
    checks = read(world/"authority/check.json")
    streams = {}
    for name, leaves in checks.items():
        root = world/"spans"/name
        for rel, pin in leaves.items():
            require(sha(root/rel)==pin, "Check entry")
        close = read(root/"runner_receipt.json")
        for item in close["feeds"]["meter"]["files"]:
            require(sha(root/item["path"])==item["sha256"], "span stream commitment")
        stream = kp.parse(meter(root))
        off = kp.raw_offset_ns(stream)
        require(stream.present and stream.aligned and off == 7*NS and not stream.errors, "decoder/RAW clock")
        times = [raw-off for raw in stream.host_ns]
        require(all(b-a==20_000_000 for a,b in zip(times,times[1:])), "50 Hz capture")
        streams[name] = times, stream.watts
    for lid in IDS:
        span, runtime, bundle = location(world,lid)
        terminal = read(runtime/"runtime_custody.json")
        require(all(sha(runtime/path)==pin for path,pin in terminal["files"].items()), "terminal file map")
        result=read(runtime/"runtime_result.json")
        work=read(runtime/"script-work.json")
        require(ctl.work_complete(work["steps"],work["script"]) and
                work["leg_spec_sha256"]==ctl.leg_spec_sha256(read(runtime.parent/"leg_spec.json")) and
                result["script_record_sha256"]==sha(runtime/"script-work.json"), "physical work")
        disk=read(bundle/"outputs/align_episode.json")
        require(disk["power_traces"]==disk["clock_mappings"]==[] and
                "power_trace_join_in_run_bundle" in disk["flags"] and len(disk["turns"])==1, "writer shape")
        ep=read_episode_bundle(bundle)
        require(ep.episode_id==bundle.name and len(ep.power_traces)==3 and
                {t.channel for t in ep.power_traces}=={"cpu_power","gpu_power","ane_power"} and
                all(t.source=="powermetrics" for t in ep.power_traces), "native rail reader")
        mapping, = ep.clock_mappings
        require(mapping.offset_ns==-18000*NS and mapping.episode_domain==ep.clock_domain, "rail clock")
        start, end = ep.start_ns, ep.end_ns
        last_recovery = work["steps"][-1]
        require(abs((last_recovery["ended_ns"]-last_recovery["started_ns"])/NS-600)<1e-7, "sampled recovery")
        for trace in ep.power_traces:
            a = bisect_left(trace.t_ns, start-mapping.offset_ns+NS)
            b = bisect_left(trace.t_ns, end-mapping.offset_ns-NS)
            plateau, idle = {"gpu_power":(5,3),"cpu_power":(3,2),"ane_power":(1.5,1)}[trace.channel]
            numeric(trace.values[a],plateau,"plateau")
            numeric(trace.values[b],idle,"baseline")
        times, watts = streams[span.name]
        a, b = bisect_right(times,start)-1, bisect_left(times,end)
        require(0<=a<b<len(times) and times[a]<=start<=end<=times[b], "DC bracket")
        idle=10+int(lid[1:])
        numeric(watts[a],idle+4,"DC plateau")
        numeric(watts[b],idle,"DC baseline")
        if lid in HIDDEN:
            hidden = work["steps"][0]
            lo,hi=hidden["started_ns"],hidden["ended_ns"]
            numeric((hi-lo)/NS,2+HIDDEN[lid]*.01,"duration oracle")
            numeric((hi-hidden["first_token_ns"])/NS,HIDDEN[lid]*.01,"decode oracle")
            require(all(w==idle+4 for w in watts[bisect_right(times,lo)-1:bisect_left(times,hi)+1]),
                    "hidden call DC plateau")
    print("PASS two receipt-bound raw streams, twelve trace-free episodes, 36 native rails and 12 DC slices")


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.parse_args()
    verify_freeze()
    with tempfile.TemporaryDirectory(prefix="ctl-fixture-") as td:
        world=Path(td)
        unpack(world)
        check(world)
