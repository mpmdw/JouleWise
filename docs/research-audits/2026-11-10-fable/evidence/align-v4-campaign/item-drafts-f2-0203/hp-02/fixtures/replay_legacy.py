"""Replay only the two published shell functions with synthetic variables and an invented date."""
from datetime import datetime
from pathlib import Path
import json
import os
import shlex
import subprocess
import sys

SEAT = Path(__file__).resolve().parents[1]
DRAFT = SEAT / "tmp/drafts/hp-02"
FIXTURE = Path(__file__).with_name("item-cases.json")
env = {"PATH": "/opt/homebrew/bin:/usr/bin:/bin", "LC_ALL":"C", "TZ":"America/Los_Angeles",
       "TMPDIR":str(SEAT/"tmp/runtime"), "ZDOTDIR":str(SEAT/"tmp/runtime"),
       "JW_B5_SYNTHETIC_ONLY":"1", "PYTHONDONTWRITEBYTECODE":"1"}
public_gate = (DRAFT/"gates.sh").read_text()
doc = json.loads(FIXTURE.read_bytes())
assert doc["synthetic_only"]
assert len({row["id"] for row in doc["cases"]}) == len(doc["cases"])

def defaults(now, date):
    yes = "HP_DELTA_OK HP01_SMOKE_PASS LINE2_OK LINE9_OK CHECKLIST_OK STOPS_CLEAR HOST_STATE_RECORDED COPY_TYPED_OK HOST_RESTORE_OK GROUPS_ABSENT QUAL_CLEAN PREDECESSOR_CLEAN"
    records = "HP_LOOK_RECORD HP01_DATES_RECORD COPY_EVIDENCE QUAL_RECORD LATEST_CLOSE_RECORD PREDECESSOR_RECORD PRIORITY_RECORD"
    return {**dict.fromkeys(yes.split(), "yes"), **dict.fromkeys(records.split(), "invented-record"),
            **dict.fromkeys("SESSION_READY COUNTED_READY F2_READY F0_ELIGIBLE HP_LOOK_RUN".split(), "no"),
            "F0_REASON":"daily_cap","LAST_CLOSE_KIND":"other","HP01_T0_DATES":"2026-11-15",
            "ISSUED_EPOCH":now-100,"KIT_ISSUED_EPOCH":now-1000,"WATCH_UNTIL_EPOCH":now+1000,
            "QUAL_DATE":date,"QUAL_CLOSE_EPOCH":now-2000,"LATEST_CLOSE_EPOCH":now-1200,
            "PRIOR_CLOSE_EPOCH":now-2000,"NEXT_COUNTED_EPOCH":0}

for item in sorted(DRAFT.glob("ITEM-hp-02-s*.md")):
    md = item.read_text()
    assert md.count("hp_gate || exit 1") == 2
    funcs = md.split("# BEGIN TESTABLE GATES\n")[1].split("# END TESTABLE GATES")[0]
    assert funcs.endswith(public_gate)
    protected = int(md.split("; PROTECTED_S=")[1].splitlines()[0])
    for shell, flags in (("/bin/bash", ["--noprofile", "--norc"]), ("/bin/zsh", ["-f"])):
        # One isolated subshell per specimen so a variable cannot leak into the next example.
        program = [f"PY={shlex.quote(sys.executable)}", f"PROTECTED_S={protected}", funcs]
        for row in doc["cases"]:
            clock = datetime.fromisoformat(row.get("clock", doc["base"]["clock"]))
            now = int(clock.timestamp())
            obs = {**defaults(now, clock.date().isoformat()), **row["legacy_env"]}
            program.extend(["(", f"date() {{ echo {now}; }}"])
            for k, v in obs.items():
                program.append("unset "+k if v is None else k+"="+shlex.quote(str(v)))
            program.extend([f"ARG=$(pick_arg {now})","hp_gate","exit $? ",")",
                            "echo legacy_rc=$?"])
        p = subprocess.run([shell,*flags], input="\n".join(program)+"\n", text=True,
                           env=env, cwd=SEAT/"tmp/runtime", capture_output=True)
        assert p.returncode == 0 and not p.stderr, (shell,p.returncode,p.stderr)
        lines = p.stdout.splitlines()
        assert len(lines) == 2 * len(doc["cases"])
        for row, message, status in zip(doc["cases"], lines[::2], lines[1::2]):
            want = row["legacy_stdout_prefix"]
            assert message.startswith(want), (item.name,shell,row["id"],want,message)
            assert status == "legacy_rc="+("0" if want.startswith("HP02 GATES PASS") else "1")
            print(item.stem, shell, row["id"], status, message)
print(len(doc["cases"]), "cases x 3 items x 2 shells PASS (legacy only)")
