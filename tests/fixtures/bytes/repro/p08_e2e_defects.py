# Adapted from JouleWise-data 6039fff; exercised by ReviewerProbeTests.
"""P08: production-shaped end-to-end with planted defects, through the real CLI in two stages.

Truth: bytes world (e = 0.01 * b J per step), seed 1100, two passes, 50 runs per model per pass.
Each defect is planted in a copy of the same baseline archive, so differences are due to it alone.

cd /tmp/jw && JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/jwtmp \
  python3.13 <repro>/p08_e2e_defects.py /tmp/jwtmp/p08
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness as H  # noqa: E402
from harness import ba, kp  # noqa: E402

work = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/jwtmp/p08")
if work.exists():
    shutil.rmtree(work)
base = work / "base"
manifest = H.build(base, "bytes", 1100)


def clone(name):
    dest = work / name
    shutil.copytree(base, dest, symlinks=True)
    m = json.loads((dest / "manifest.json").read_text())
    for s in m["sessions"]:
        s["archive"] = s["archive"].replace(str(base), str(dest))
    H.save_manifest(dest, m)
    return dest, m


def cell_rows(out_dir, name, model, **match):
    rows = [r for r in H.table(out_dir, name) if r["model"] == model]
    return [r for r in rows if all(r.get(k) == v for k, v in match.items())]


def summarize(label, root, m, model, pass_id, run_id=None):
    codes, err, out = H.run(root)
    print(f"\n=== {label}: exit codes {codes}" + (f"; stderr: {err}" if err else ""))
    if codes != [0, 0]:
        return None
    fit_or_held = "fit_pass_estimates" if any(x["model"] == model and x["role"] == "fit" for x in m["models"]) else "heldout_pass_estimates"
    src = out.parent / "out-fit" if fit_or_held == "fit_pass_estimates" else out
    for sel in ("primary", "flagged-inclusive"):
        for r in cell_rows(src, fit_or_held, model, pass_id=pass_id, selection=sel, basis="gross primary"):
            extra = ""
            if run_id:
                extra = f" run in kept={run_id in r.get('kept_runs', [])} removed={run_id in r.get('removed_runs', [])}"
            print(f"  {sel:17s} {r['boundary']:8s} status={r['status']} n_r/n_b={r.get('n_r')}/{r.get('n_b')} "
                  f"mean={r.get('mean_j', float('nan')):.4f} B={r.get('B_j', float('nan')):.4f} flags={r.get('flags')}{extra}")
    return out


codes, err, base_out = H.run(base)
assert codes == [0, 0], (codes, err)
base_words = H.words(base_out)
print("BASELINE words (primary, gross):")
for k, v in sorted(base_words.items()):
    print(f"  {k[0]:8s} {k[1]:34s} {v}")
base_moe = {(r["selection"], r["basis"], r["boundary"]): r["answer"] for r in H.table(base_out, "moe")}
print("BASELINE active-or-resident:", {k[2]: v for k, v in base_moe.items() if k[:2] == ("primary", "gross primary")})


def word_diff(out):
    if out is None:
        return
    w = H.words(out)
    diff = {k: (base_words[k], w[k]) for k in w if w[k] != base_words[k]}
    print("  word changes vs baseline:", diff or "none")


# A. Lost quad member (held-out 14B, pass 1, ordinal 15): bundle and stored reduction gone, harvest excluded it.
root, m = clone("A_lost_member")
rid = H.run_ids(m, 1, "Qwen3-14B-4bit")[15]
shutil.rmtree(H.bundle(m, 1, rid))
H.stored_summary(m, 1, rid).unlink()
H.exclude(m, 1, rid, "member.bytes_missing")
word_diff(summarize("A lost quad member (14B p1 #15, member.bytes_missing)", root, m, "Qwen3-14B-4bit", 1, rid))

# B. Token-count mismatch on a fit model member, excluded by the harvest.
root, m = clone("B_token_mismatch")
rid = H.run_ids(m, 1, "Qwen3-4B-4bit")[3]
H.edit_json(H.bundle(m, 1, rid) / "metadata.json", lambda md: md["workload_observed"].update(output_token_count=511))
H.exclude(m, 1, rid, "member.token_count_mismatch")
word_diff(summarize("B token-count mismatch (4B p1 #3, member.token_count_mismatch)", root, m, "Qwen3-4B-4bit", 1, rid))

# C. Thermal exclusion (fit 8B, pass 2, repeat #2).
root, m = clone("C_thermal")
rid = H.run_ids(m, 2, "Qwen3-8B-4bit")[2]
H.exclude(m, 2, rid, "thermal.os_level_nonzero")
word_diff(summarize("C thermal exclusion (8B p2 #2)", root, m, "Qwen3-8B-4bit", 2, rid))

# D. Cooldown cap (NUMBER-class member exclusion; run has a valid energy record).
root, m = clone("D_cooldown")
rid = H.run_ids(m, 1, "Qwen3-8B-4bit")[20]
H.exclude(m, 1, rid, "member.cooldown_cap_hit")
word_diff(summarize("D cooldown cap (8B p1 #20, valid energy; A3 item 8 says restore in inclusive)", root, m, "Qwen3-8B-4bit", 1, rid))


# E. Battery assist during a held-out MoE run's decode: meter (DC input) reads half; battery covers the rest.
def assist(m, pass_id, rid, emit_flag):
    md = ba.read_json(H.bundle(m, pass_id, rid) / "metadata.json")
    events = [json.loads(s) for s in (H.bundle(m, pass_id, rid) / "events.jsonl").read_text().splitlines() if s.strip()]
    t0, t1 = ba._event_span(events, "decode", md)
    path = H.archive(m, pass_id) / "sources/night-custody/hazards/meter/stream-001.jsonl"
    lines = [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
    changed = 0
    for b in lines[1:-1]:
        raw = bytes.fromhex(b["p"])
        out = []
        for i in range(b["n"]):
            f = list(kp.SAMPLE.unpack(raw[i * kp.SAMPLE.size:(i + 1) * kp.SAMPLE.size]))
            tick = b["rx"] // 100_000_000 - (b["n"] - 1 - i)
            if t0 <= tick * 100_000_000 < t1:
                f[3] = f[3] // 2
                changed += 1
                b["smc"] = {"B0AC": -3000, "B0AV": 12000}
            out.append(kp.SAMPLE.pack(*f))
        b["p"] = b"".join(out).hex()
    path.write_text("".join(json.dumps(x) + "\n" for x in lines))
    if emit_flag:
        H.flag(m, pass_id, rid, "battery.assist")
    return changed


for emit in (True, False):
    root, m = clone("E_battery_" + ("flagged" if emit else "unflagged"))
    rid = H.run_ids(m, 1, "Qwen3-30B-A3B-4bit")[0]
    n = assist(m, 1, rid, emit)
    out = summarize(f"E battery assist on 30B-A3B p1 #0, {n} meter samples halved, harvest flag={emit}", root, m,
                    "Qwen3-30B-A3B-4bit", 1, rid)
    word_diff(out)

# F. Nonzero CLOCK_MONOTONIC_RAW - monotonic offset (+5 s) on pass 2's meter stream: DC must not change.
root, m = clone("F_raw_offset")
path = H.archive(m, 2) / "sources/night-custody/hazards/meter/stream-001.jsonl"
lines = [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
off = 5_000_000_000
lines[0]["start_raw_ns"] += off
lines[-1]["end_raw_ns"] += off
for b in lines[1:-1]:
    b["tx"] += off
    b["rx"] += off
path.write_text("".join(json.dumps(x) + "\n" for x in lines))
codes, err, out = H.run(root)
print(f"\n=== F raw offset +5 s on pass-2 stream: exit {codes} {err}")
a = {(r["model"], r["boundary"], r["selection"], r["basis"]): r["mean_j"] for r in H.table(out, "model_estimates") if r["status"] == "computed"}
b = {(r["model"], r["boundary"], r["selection"], r["basis"]): r["mean_j"] for r in H.table(base_out, "model_estimates") if r["status"] == "computed"}
print("  max |DC/rest mean change| vs baseline (J):", max(abs(a[k] - b[k]) for k in a))
