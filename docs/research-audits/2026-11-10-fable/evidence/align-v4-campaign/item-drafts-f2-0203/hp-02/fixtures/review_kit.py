"""Air-only replay against the seat's public inputs. Uses fake dependencies for all spans."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

SEAT = Path(__file__).resolve().parents[1]
TMP = SEAT / "tmp"
PIN = TMP / "pin"
DRAFTS = TMP / "drafts"
HP = DRAFTS / "hp-02"
KIT = HP / "cl-hp-02.json"
QUEUE = HP / "queue-a.json"
PIN_ID = "dd206025abb30fd5c07515cd4b34b3e653174810"
KIT_SHA = "7693b8293b42b8ba20cbd321e201974745b172dc53c4f1397d2c1494f38fbe66"
SOURCE_SHA = "7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965"
QUEUE_SHA = "6489297e89e0cf02fe8d0f4050fe6f0492e175724d4902173fd2d7e7b5d54286"
TZ = ZoneInfo("America/Los_Angeles")
ENV = {"PATH": "/opt/homebrew/bin:/usr/bin:/bin", "TZ": TZ.key, "TMPDIR": str(TMP),
       "JW_B5_SYNTHETIC_ONLY": "1", "PYTHONDONTWRITEBYTECODE": "1", "LC_ALL": "C"}

def stamp(local):
    return int(datetime.fromisoformat(local).replace(tzinfo=TZ).timestamp())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def leaves(obj, path=""):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield from leaves(value, f"{path}/{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            yield from leaves(value, f"{path}/{i}")
    else:
        yield path, obj

def call(script, command, *args, rc=0):
    allowed = {"cadence_queue.py": {"gen-legs", "validate-kit", "validate-queue", "next"},
               "cadence_legs_runner.py": {"plan", "mock"}}
    assert command in allowed[script]
    p = subprocess.run([sys.executable, "-B", PIN / "scripts" / script, command, *map(str, args)],
                       cwd=PIN, env=ENV, text=True, capture_output=True)
    assert p.returncode == rc, (command, args, p.returncode, p.stdout, p.stderr)
    return json.loads(p.stdout) if rc != 1 else p.stderr + p.stdout

def main():
    source = TMP / "cl-hp-01.json"
    assert [digest(p) for p in (source, KIT, QUEUE)] == [SOURCE_SHA, KIT_SHA, QUEUE_SHA]
    assert subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PIN, text=True).strip() == PIN_ID
    before, after = (json.loads(p.read_bytes()) for p in (source, KIT))
    left, right = dict(leaves(before)), dict(leaves(after))
    assert left.keys() == right.keys()
    differences = {k: (str(left[k]), str(right[k])) for k in left if left[k] != right[k]}
    table = (DRAFTS / "DELTA-CHECK.md").read_text().split("## cl-hp-02\n")[1].split("Layout by piece")[0]
    published = {k: (old, new) for k, old, new in re.findall(r"\| `(/.*?)` \| `(.*?)` \| `(.*?)` \|", table)}
    assert len(differences) == 15 and differences == published
    # Also compare the file bytes after reversing only the 15 identified value tokens.
    # These public documents put each nonempty JSON field on its own line.
    old_lines, new_lines = (p.read_bytes().splitlines(keepends=True) for p in (source, KIT))
    assert len(old_lines) == len(new_lines)
    edits = [(a, b) for a, b in zip(old_lines, new_lines) if a != b]
    assert len(edits) == 15
    for path, (old, new) in differences.items():
        def token(v):
            return json.dumps(v if path.endswith(("/campaign_id", "/ruling/id")) else int(v), ensure_ascii=False).encode()
        assert sum(token(old) in a and a.replace(token(old), token(new), 1) == b for a, b in edits) == 1
    assert before["frozen"] == after["frozen"] and after["frozen"]["commit"] == PIN_ID
    assert len(after["frozen"]["paths"]) == 37
    for path, sha in after["frozen"]["paths"].items():
        assert digest(PIN / path) == sha
    print("SHA-256 x3, 15 exact byte-line/leaf changes, 37/37 frozen path bytes PASS")
    for k, pair in differences.items():
        print(k, *pair)
    gen = call("cadence_queue.py", "gen-legs", "--campaign-id", "cl-hp-02", "--master-seed", 2026111601,
               "--n-legs", 12, "--bands", "q0", "--prefill-tokens", 19458, "--decode-tokens", 4096)
    assert gen["legs"] == after["legs"] and gen["seed_law"] == after["seed_law"]
    for window in ("02:00-02:35", "13:14-13:15"):
        result = call("cadence_queue.py", "validate-kit", KIT, "--repo", PIN, "--batch-window", window)
        assert result["frozen_paths_verified"] and result["kit_sha256"] == KIT_SHA
    q = json.loads(QUEUE.read_bytes())
    assert call("cadence_queue.py", "validate-queue", QUEUE, "--kits-root", DRAFTS)["spans"] == 3
    assert [len(s["legs"]) for s in q["spans"]] == [3,4,5]
    assert [leg for s in q["spans"] for leg in s["legs"]] == [f"L{i:03d}" for i in range(1,13)]
    assert all(s["attempt"] == 1 and s["rerun_of"] is None for s in q["spans"])
    old = json.loads((HP / "items.json").read_bytes())
    native = "cadence_legs_runner.py"
    with tempfile.TemporaryDirectory(dir=TMP / "runtime", prefix="kit-") as scratch:
        for i, (span, expected, worst) in enumerate(zip(q["spans"], [6903,8154,9405], [16650,19350,22050])):
            legs = ",".join(span["legs"])
            common = ["--kit", KIT, "--legs", legs]
            plans = [(t, w) for lo, hi, w in old[i]["bands"] for t in (lo,hi)]
            plans += [(stamp("2026-11-20T13:20"), "02:00-02:35"), (stamp("2026-11-20T23:30"), "13:14-13:15")]
            for t, w in plans:
                plan = call(native,"plan",*common,"--t0",t,"--batch-window",w)
                assert plan["blackout_clear"] and plan["batch_windows"] == [w]
                assert [leg["leg_id"] for leg in plan["legs"]] == span["legs"]
                assert (plan["expected_s"], plan["worst_case_s"]) == (expected,worst)
                assert plan["launch_deadline_epoch_s"] - t == worst + 560
            refusal = call(native,"plan",*common,"--t0",stamp("2026-11-20T23:30"),"--batch-window","02:00-02:35",rc=1)
            assert "batch blackout" in refusal
            scenarios = [("clean", [], 0)]
            if i == 0:
                scenarios += [("contaminated", ["--contaminate", "L001"], 0), ("G0-timeout", ["--g0-timeout", "L001"], 0),
                              ("restore-failure", ["--fail-close-restore"], 2)]
            for label, flags, rc in scenarios:
                out = Path(scratch) / f"{i+1}-{label}"
                r = call(native,"mock",*common,"--t0-local","2026-11-20T23:30:00","--batch-window","13:14-13:15",
                         "--output",out,*flags,rc=rc)
                assert r["rc"] == rc and r["legs"] == len(span["legs"])
                receipt = json.loads((out / "runner_receipt.json").read_bytes())
                assert receipt["mock"] is True and receipt["roster"] == span["legs"]
                assert receipt["kit"]["sha256"] == KIT_SHA and receipt["batch_windows"] == ["13:14-13:15"]
                proof = receipt["high_power"]["close_proof"]
                assert all(f["stop"]["proven_stopped"] is True for f in receipt["feeds"].values())
                if rc:
                    assert "RESTORE_UNPROVEN" in [s["code"] for s in r["stops"]]
                    assert proof["proven"] is False and proof["ac_powermode"] == 2 and proof["host_marker_present"]
                    assert receipt["high_power"]["restore"]["attempts"] == 3
                else:
                    assert not r["stops"] and proof["proven"] and proof["ac_powermode"] == 0 and not proof["host_marker_present"]
                print(span["span_id"], label, "rc", rc, "restore_proven", proof["proven"], "PASS")
            print(span["span_id"], legs, "expected/work worst/min fence/item fence",
                  expected, worst, worst+560, worst+1460, "8 positive plans, 1 negative plan PASS")
    expiry = stamp("2026-11-23T00:00")
    assert expiry == 1795420800
    for delta, expected in ((-1, "arm"), (0,"arm"), (1,"halt")):
        # Pure synthetic observation of the pinned comparator. The legacy item and stager are stricter.
        r = call("cadence_queue.py","next","--queue",QUEUE,"--now",expiry+delta)
        assert r["action"] == expected
        print("isolated pinned queue.next", expiry+delta, r["action"], "PASS")

if __name__ == "__main__":
    main()
