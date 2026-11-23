"""Check vector consistency; optionally compare a future builder's synthetic decisions."""
import argparse
from datetime import datetime, timedelta
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo

here = Path(__file__).resolve().parent
seat = here.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--decisions", type=Path, help="JSON object mapping case id to the successor's actual decision")
args = parser.parse_args()
doc = json.loads((here/"item-cases.json").read_bytes())
cases = {row["id"]:row for row in doc["cases"]}
assert doc["synthetic_only"] and len(cases) == len(doc["cases"])
base = doc["base"]
clock = datetime.fromisoformat(base["clock"])
for id, seconds in (("pair-equality",0),("pair-plus-one",1)):
    spec = cases[id]["observations"]
    first = max(clock + timedelta(seconds=spec["hp_to_next_s"]),
                datetime.fromisoformat(spec["dated_pending"][0]["t0_floor"]))
    assert first.strftime("%H:%M:%S") == "18:16:50"
    second = first + timedelta(seconds=spec["dated_pending"][0]["first_to_second_s"])
    assert second == clock.replace(hour=23,minute=59,second=59) + timedelta(seconds=seconds)
    assert datetime.fromisoformat(spec["dated_pending"][0]["t0_floor"]) + timedelta(seconds=spec["dated_pending"][0]["first_to_second_s"]) < clock.replace(hour=23,minute=59,second=59)
assert datetime.fromisoformat(cases["queue-at-expiry"]["clock"]).timestamp() == 1795420800
sys.path.insert(0,str(seat/"tmp/pin"))
from joulewise.cadence.legs import interval_delay
from scripts.align_r1_rehearsal import OS_BATCH_WINDOW_LOCAL
from scripts.launch_cadence_span import cadence_plan
noon = datetime(2026,11,20,12,0,tzinfo=ZoneInfo("America/Los_Angeles")).timestamp()
plan = cadence_plan(seat/"tmp/drafts/hp-02/cl-hp-02.json","L001,L002,L003","02:00-02:35",t0=noon)
assert plan["blackout_clear"] and plan["worst_case_s"] == 16650
assert interval_delay(noon,1950,[OS_BATCH_WINDOW_LOCAL]) == 4500
print("Fixture integrity, pair boundary, queue epoch and pinned pure midday plan/soak-delay probes PASS")
if args.decisions:
    actual = json.loads(args.decisions.read_bytes())
    expected = {key:row["expected_successor"] for key,row in cases.items()}
    if actual != expected:
        raise SystemExit([(key,expected.get(key),actual.get(key)) for key in sorted(actual.keys()|expected.keys()) if expected.get(key)!=actual.get(key)])
    print(len(cases),"future builder decisions match")
else:
    print(len(cases),"successor decisions specified; no builder evaluated")
