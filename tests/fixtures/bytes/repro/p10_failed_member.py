# Adapted from JouleWise-data 6039fff; exercised by ReviewerProbeTests.
"""P10: a member that ran but failed (status not succeeded, no decode energy), excluded by the harvest
with member.status_not_succeeded. Spec: its unit is removed; the cell keeps >= 5 units per stratum.
Also: the same member with status failed but an energy present.

cd /tmp/jw && JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp \
  python3.13 <repro>/p10_failed_member.py /tmp/jwtmp/p08
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402

work = Path(sys.argv[1])
base = work / "base"


def clone(name):
    dest = work / name
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(base, dest, symlinks=True)
    m = json.loads((dest / "manifest.json").read_text())
    for s in m["sessions"]:
        s["archive"] = s["archive"].replace(str(base), str(dest))
    H.save_manifest(dest, m)
    return dest, m


for label, energy in (("failed, decode energy null", None), ("failed, decode energy present", "keep")):
    root, m = clone("H_failed_" + ("null" if energy is None else "present"))
    rid = H.run_ids(m, 1, "Qwen3-32B-4bit")[30]

    def fn(s):
        s["status"] = "failed"
        if energy is None:
            s["phase_energy_j"]["decode"] = None
    H.edit_json(H.stored_summary(m, 1, rid), fn)
    H.exclude(m, 1, rid, "member.status_not_succeeded")
    codes, err, out = H.run(root)
    print(f"{label}: exit {codes} {err}")
    if codes == [0, 0]:
        rows = [r for r in H.table(out, "heldout_pass_estimates") if r["model"] == "Qwen3-32B-4bit" and r["pass_id"] == 1
                and r["basis"] == "gross primary"]
        for r in rows:
            print(f"   {r['selection']:17s} {r['boundary']:8s} n_r/n_b={r['n_r']}/{r['n_b']} removed={rid in r['removed_runs']}")
