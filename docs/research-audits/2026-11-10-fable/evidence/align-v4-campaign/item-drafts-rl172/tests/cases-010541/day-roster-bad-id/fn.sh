DAY_MIXED=yes      # mixed-size development block (dev-03, dev-04, dev-05)
day_gate() {
  DAY_ROSTER_N="$(printf '%s\n' "$LEGS" | tr ',' '\n' | grep -c .)"
  "$PY" -I -B - /Volumes/JW-EXT/scratch/items-rl171/tests/cases-010541/day-roster-bad-id/campaign-out "$(date +%s)" "$DAY_ROSTER_N" "$DAY_MIXED" <<'PY'
import json, os, re, sys, datetime as dt, zoneinfo
TZ = zoneinfo.ZoneInfo("America/Los_Angeles")
root, now, n, mixed = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), sys.argv[4] == "yes"
day = dt.datetime.fromtimestamp(now, TZ).date()
DEV = {"cl-dev-01", "cl-dev-02", "cl-dev-03", "cl-dev-04", "cl-dev-05"}
MIX = {"cl-dev-03", "cl-dev-04", "cl-dev-05"}
LEG = re.compile(r"L\d{3}")
dev = mix = 0; seen = []
def started_of(p):
    try:
        r = json.load(open(p))
    except (OSError, ValueError):
        sys.exit(f"STOP: receipt unreadable: {p}; mail the lead")
    if not isinstance(r, dict):
        sys.exit(f"STOP: receipt unreadable: {p}; mail the lead")
    started = r.get("started")
    t0 = started.get("epoch_s") if isinstance(started, dict) else None
    if isinstance(t0, bool) or not isinstance(t0, (int, float)):
        sys.exit(f"STOP: receipt started.epoch_s unreadable: {p}; mail the lead")
    return r, t0
# RL-172 (a) rule 3: a qualification t0-date holds no development span
for camp in sorted(os.listdir(root)):
    if camp.startswith("cl-qual-") and os.path.isdir(os.path.join(root, camp)):
        for d in sorted(os.listdir(os.path.join(root, camp))):
            p = os.path.join(root, camp, d, "runner_receipt.json")
            if os.path.isfile(p) and dt.datetime.fromtimestamp(started_of(p)[1], TZ).date() == day:
                sys.exit(f"STOP: RL-172 (a): {day} is a qualification t0-date ({p}); no development span arms on it")
for camp in sorted(os.listdir(root)):
    if camp not in DEV:
        continue
    for d in sorted(os.listdir(os.path.join(root, camp))):
        p = os.path.join(root, camp, d, "runner_receipt.json")
        if not os.path.isfile(p):
            continue
        r, t0 = started_of(p)
        if dt.datetime.fromtimestamp(t0, TZ).date() != day:
            continue
        roster = r.get("roster")
        if not (isinstance(roster, list) and roster and all(isinstance(x, str) and LEG.fullmatch(x) for x in roster)
                and len(set(roster)) == len(roster)):
            sys.exit(f"STOP: receipt roster unreadable: {p}; mail the lead")
        k = len(roster)
        dev += k; mix += k if camp in MIX else 0; seen.append((d, k))
print(f"t0-date {day}: development legs already launched {dev} (mixed-size {mix}) {seen}; this span {n}, mixed {mixed}")
if dev + n > 24:
    sys.exit("STOP: RL-172 (a): more than 24 development legs on this t0-date; the lead re-dates this span (never doubled up)")
if mixed and mix + n > 12:
    sys.exit("STOP: RL-172 (a): more than 12 mixed-size development legs on this t0-date; the lead re-dates this span (never doubled up)")
PY
}
