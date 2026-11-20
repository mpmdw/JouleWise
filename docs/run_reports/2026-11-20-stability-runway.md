# Stability runway at RS483 — 2026-11-20

Tier 0 capacity planning for Opus. Every projected time is conditional and in
PST (America/Los_Angeles). The held-work forecast assumes that no higher rung
preempts the stability ladder and that all modeled starts close cleanly.
Prepare both successors by **Fri Nov 27** if the lead wants continuous
coverage across the speeds tested here. In the faster-close case the first
unfillable A dispatch is **Sat Nov 28 at 04:24:58** and the first unfillable B
dispatch is **Sat Nov 28 at 12:53:35**. The nominal case gives more time, as
shown below. The lead owns any successor, hold, or change in priority.

## Inventory at the handoff

| Roster | Committed positions | Completed at RS483 | Issued separately | Successors | Nominal successor work | Worst-case successor work |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| A · `2d347f721` · kits 01–14 | 168 | 3 | 1 | 164 | 751,282 s | 959,400 s |
| B · `6e9d42f1d` · kits 15–16 | 24 | 2 | 0 | 22 | 100,722 s | 128,700 s |
| Total | 192 | 5 | 1 | 186 | 852,004 s | 1,088,100 s |

RS483 starts the handoff with A's kit 01 L001–L003 complete and L004 issued.
RS444 and RS453 account for B's kit 15 L001–L002. The separate L004 plan
has 4,528 s expected work and 5,850 s worst-case work. Its modeled 07:03:00
launch yields 08:18:28 as the earliest modeled next dispatch, conditional on
a clean Check, a cleared fence, and copy completion. RS483 printed about
08:41 for its fence. A refusal or non-clean close takes RS483's refusal
branch and invalidates this runway for the affected kit. RS482 had finished
`f2-inst-01..03`. At RS483 there was no further rank-2 kit with a recorded
executing delta PASS, no issued `hp-02`, and no F0 after R1's close.
[RS483 and RS482](https://github.com/mpmdw/JouleWise/blob/c05bcfc45/RUN_STATE.md#L1055-L1109)
· [B L001](https://github.com/mpmdw/JouleWise/blob/c05bcfc45/RUN_STATE.md#L1966)
· [B L002](https://github.com/mpmdw/JouleWise/blob/c05bcfc45/RUN_STATE.md#L1757)
· [RS425](https://github.com/mpmdw/JouleWise/blob/c05bcfc45/RUN_STATE.md#L2374-L2394).

Each successor uses the next queue position in kit and leg order on its
pin. Pin A uses the first admitted batch argument under RS463. Pin B plans
with no batch window and enters at rank 4 only in the 10:50:01–13:14:59
local start band under RS464 and RL-190. A B span can finish after 13:15,
and A resumes at the next eligible dispatch. At midnight a prior leg keeps
its own t0-date. Rank 1 goes to the first eligible base start on the new
date, after the predecessor closes. The simulation uses immediate proven
closes at the modeled work times. Check and copy can add elapsed time,
with a live copy wait up to 600 s under RS422. There is no prescribed
inter-span cooldown. Every renewed stability queue expires at **Tue Dec 8
12:35:29 PST**. Unspent positions would require a lead-renewed queue for
starts after that time. Inventory runs out before expiry in all three
cases below.
[RS422](https://github.com/mpmdw/JouleWise/blob/c05bcfc45/RUN_STATE.md#L2428-L2448)
· [RS447](https://github.com/mpmdw/JouleWise/blob/c05bcfc45/RUN_STATE.md#L1923-L1936)
· [RS464 and RS463](https://github.com/mpmdw/JouleWise/blob/c05bcfc45/RUN_STATE.md#L1518-L1543)
· [RS473](https://github.com/mpmdw/JouleWise/blob/c05bcfc45/RUN_STATE.md#L1330-L1337).

## Conditional depletion and preparation dates

The last start uses the final position of its roster. The projected close is
the next dispatch at which that pin is eligible by the clock and has no
position. The last full prep date leaves the successor ready before that
dispatch. Opus can use the same-day time as the conditional latest boundary.

| Scenario | Pin | Last start | Close / first uncovered eligible dispatch | Last full prep date |
| --- | --- | --- | --- | --- |
| Uninterrupted fallback | A | Sun Nov 29 23:54:19 | Mon Nov 30 01:09:30 | Sun Nov 29 |
| Uninterrupted fallback | B | Tue Dec 1 10:50:01 | Tue Dec 1 12:05:12 | Mon Nov 30 |
| Fast-close sensitivity | A | Sat Nov 28 03:24:47 | Sat Nov 28 04:24:58 | Fri Nov 27 |
| Fast-close sensitivity | B | Sat Nov 28 11:53:24 | Sat Nov 28 12:53:35 | Fri Nov 27 |
| W1 and qualification preemption | A | Wed Dec 2 07:10:28 | Wed Dec 2 08:25:39 | Tue Dec 1 |
| W1 and qualification preemption | B | Fri Dec 4 10:50:01 | Fri Dec 4 12:05:12 | Thu Dec 3 |

The nominal Friday and Saturday dispatches are shared by the fallback and
preemption cases. All B starts are at rank 4 with no batch window.

| Local date | Last A dispatch before B | B dispatches | Next A dispatch |
| --- | --- | --- | --- |
| Fri Nov 20 | 09:33:39 · 01 L006 | 10:52:02 · 15 L003, 12:07:30 · 15 L004 | 13:22:58 · 01 L007 |
| Sat Nov 21 | 09:43:36 · 02 L011 | 11:01:59 · 15 L005, 12:17:10 · 15 L006 | 13:35:33 · 02 L012 |

Friday's 02 L003 starts at 23:34:36 and closes Saturday at 00:50:04.
Saturday's first dispatch is therefore **00:50:04 · 02 L004 · rank 1**
with `13:14-13:15`. The planner admits an A start at 00:00 with that
argument if the host is already free. In the fast-close sensitivity the
same L004 anchor is used and every successor closes 900 s sooner than its
own expected work time, with the original worst-case admission tests.
Saturday rank 1 then starts at 00:39:06 (02 L007), and a third B dispatch
fits at 12:55:14. The 900 s reduction is an invented sensitivity, so the
Nov 27 preparation date covers these scenarios and can move with new
operational information.

The separate W1/qualification scenario assumes newly eligible work and a
lead-issued qualification schedule. W1 becomes READY Sun Nov 22 at 20:00
and takes the first clean dispatch at 20:04:37 for its published **44,640 s**
planning maximum. The next three dates each take one qualification block
at the first clean dispatch at or after 03:00, an invented release time.
Each block occupies **54,520 s** (two spans with 24,750 s work, 1,950 s
soak retry and 560 s cleanup apiece). The block intervals are Nov 23
08:28:37–23:37:17, Nov 24 03:26:19–18:34:59, and Nov 25
03:28:14–18:36:54. Both starts in each pair fit their local date. The model
assumes the counted start gates, including the batch check, are satisfied,
the lead changes the draft dates and expiry as needed, and no other work
preempts. W1 wins a date conflict and cannot take effect between the two
qualification spans.
[W1 planning maximum](https://github.com/mpmdw/JouleWise/blob/b2e01464d/docs/align/v4/W1-SMOKE-AGREEMENT.md#L30)
· [Qualification bounds and draft dates](https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1118/ITEM-qual01-s01.md#L1-L18)
· [W1 priority ruling](https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L20155-L20170).

## Fourteen dates and the monthly read

**Wed Dec 2 is the earliest 14th base date**, counting Nov 19 through Dec 2
inclusive if each of those local t0-dates has a qualified A leg. Nov 20
already had its Friday base start under RS477. The two completed B
positions account for Nov 18 and Nov 19 in the wider population if they
qualify. Nov 18 supplies only a B date. The read is due at the first proven
close after stage 1 can count 14 base dates. A rank-4 A start can supply a
date if stage 1 qualifies it.

| Scenario | Possible base dates · last | Possible full-population dates · last | First later date with no A start | First later date with no A or B start |
| --- | --- | --- | --- | --- |
| Uninterrupted fallback | 11 · Nov 29 | 14 · Dec 1 | Nov 30 | Dec 2 |
| Fast-close sensitivity | 10 · Nov 28 | 11 · Nov 28 | Nov 29 | Nov 29 |
| W1 and qualification preemption | 14 · Dec 2 | 17 · Dec 4 | Dec 3 | Dec 5 |

Under uninterrupted fallback, the monthly read's 14 possible dates
include B-only Nov 18, Nov 30 and Dec 1. Its base table still lacks Nov 30,
Dec 1 and Dec 2. There is also no remaining full-population position for
Dec 2. Under the W1/qualification example, 14 base dates are possible at
the modeled Dec 2 02:02:46 close of kit 14 L007, if every date qualifies.
Five A and five B positions are then unstarted. The wider roster can
still cover Dec 3–4 via B alone, so its base table stops at Dec 2. These
counts assume each started date has a qualified leg by the read's
stage-1 cutoff.
[RS477](https://github.com/mpmdw/JouleWise/blob/c05bcfc45/RUN_STATE.md#L1214)
· [RL-190 populations and rank](https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22330-L22367).

- **Ordinary route.** `lm-stab-01` reads the fixed 14-kit A population at
  its due close once its preconditions hold. `lm-stab-02` follows the lead's
  committed `paper1_data_lock`. It uses every indexed kit and prints both
  the full-population and 14-kit tables. The first read does not direct a
  hold. RL-181 ties the end of daily rank to the second read.
  [RL-181 §2.6](https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19436-L19447)
  · [RL-190 §1.3](https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22340-L22356).
- **Early-lock route.** If the lead commits `paper1_data_lock` before
  `lm-stab-01` has run, `lm-stab-02` runs once on the full roster, even with
  fewer than 14 qualified base dates. It also prints the base tables.
  `lm-stab-01` is coalesced. Committed stage 1 records the actual counts.
  A third read requires a ruling.
  [RL-190 §1.5](https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L22369-L22382).

## Reproduce and verify

The [position ledger](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/filler-capacity-20261120.tsv)
lists all 192 positions, including five completed rows and the separate
issued row. Dashes mark those rows' lack of a successor projection. The
`pin` column uses the A/B mapping above. Every scenario column is
conditional. `worst_s` is the pure span work bound. The Pin A admission test
also applies the legacy 1,460 s fence tail and soak-window rule. The B
launcher has separate reserves that do not count as planned work or force
a clean span to occupy its full budget.

Run from this branch's repository root with Python 3 and the pinned Git
objects available. The command loads only public design/source blobs and
executes the pure planning functions extracted from both pinned
`legs.py` files. The assertion output goes to stderr. Remove the diff
pipeline to print the calculated ledger.

[Pin A](https://github.com/mpmdw/JouleWise/blob/2d347f721/joulewise/cadence/legs.py#L225-L367)
· [Pin B](https://github.com/mpmdw/JouleWise/blob/6e9d42f1d/joulewise/cadence/legs.py#L225-L367)
· [Pinned kit index](https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/f2-stab/KITS.json)
· [Pinned queues](https://github.com/mpmdw/JouleWise/tree/04d8aa778/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/fillers-w2/queues-1leg)
· [Protected clauses](https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L18906-L18925)
· [Cell equivalence and roster gates](https://github.com/mpmdw/JouleWise/blob/04d8aa778/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19223-L19229).

```sh
ledger=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/filler-capacity-20261120.tsv
python3 -B - <<'PY' | diff -u "$ledger" -
import ast
import csv
import hashlib
import json
import math
import re
import subprocess
import sys
from collections import Counter, deque
from datetime import date, datetime, time, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

audit = "04d8aa778fe6dc6ec544e86b4730a986020fd368"
campaign = "docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign"
pins = {"A": "2d347f721552fe03bdd19f113e7bad7a7c24908e",
        "B": "6e9d42f1dd3d308bc9239143d0d634ab965e50e1"}
zone = ZoneInfo("America/Los_Angeles")

def blob(ref, path):
    return subprocess.check_output(["git", "show", f"{ref}:{path}"])

def pure_source(ref, path, namespace, take):
    tree = ast.parse(blob(ref, path), filename=path)
    tree.body = [node for node in tree.body if take(node)]
    exec(compile(tree, path, "exec"), namespace)
    return SimpleNamespace(**{k: v for k, v in namespace.items() if k != "__builtins__"})

def planner(pin):
    kit_names = set("""LOCAL_ZONE_NAME CAMPAIGN_ID_RE LEG_ID_RE FREE_TEXT_KEYS
                      DENY_KEY_TOKENS DENY_KEY_SUBSTRINGS DENY_VALUE_RE""".split())
    kitmod = pure_source(pin, "joulewise/cadence/kit.py", {"re": re}, lambda n:
        (isinstance(n, ast.Assign) and n.targets[0].id in kit_names)
        or (isinstance(n, ast.FunctionDef) and n.name == "deny_scan"))
    return pure_source(pin, "joulewise/cadence/legs.py",
        dict(datetime=datetime, timedelta=timedelta, wall_time=time, ZoneInfo=ZoneInfo,
             math=math, re=re, kitmod=kitmod),
        lambda n: isinstance(n, (ast.Assign, ast.ClassDef, ast.FunctionDef)) and n.lineno <= 367)

def local(day, clock="00:00:00"):
    return int(datetime.fromisoformat(f"{day}T{clock}").replace(tzinfo=zone).timestamp())

def wall(epoch):
    return datetime.fromtimestamp(epoch, zone)

def stamp(epoch):
    return wall(epoch).isoformat()

plans = {label: planner(pin) for label, pin in pins.items()}
index = json.loads(blob(audit, f"{campaign}/f2-stab/KITS.json"))
base = [f"f2-stab-{n:02d}" for n in range(1, 15)]
kit_ids = base + ["f2-stab-15", "f2-stab-16"]
assert index["base_kits"] == base
assert [row["kit_id"] for row in index["rows"]] == kit_ids

def plan(pin, kit, leg, t0):
    native = plans[pin]
    args = ("02:00-02:35", "13:14-13:15") if pin == "A" else ("",)
    for arg in args:
        windows = [native.parse_window(arg)] if arg else []
        try:
            span = native.plan_span(kit, t0_epoch=t0, windows=windows, leg_ids=[leg])
        except native.PlanError:
            continue
        if pin == "A" and native.fence_problems(span, windows, [((11, 45), (13, 15))]):
            continue
        return span, arg or "none"
    return None, None

positions, kits, expires = {}, {}, {}
done = {(base[0], f"L{n:03d}") for n in range(1, 4)} | {
    ("f2-stab-15", "L001"), ("f2-stab-15", "L002")}
l004 = (base[0], "L004")
for row in index["rows"]:
    kit_id = row["kit_id"]
    pin = "A" if kit_id in base else "B"
    assert row["runner_pin"] == pins[pin][:9]
    raw = blob(audit, row["path"])
    assert hashlib.sha256(raw).hexdigest() == row["sha256"]
    kit = kits[kit_id] = json.loads(raw)
    queue = json.loads(blob(audit, f"{campaign}/fillers-w2/queues-1leg/{kit_id}.json"))
    assert queue["halt"] is None and queue["queue_id"] == "cq-" + kit_id
    assert queue["expires_at"] == "2026-12-08T12:35:29-08:00"
    expires[kit_id] = int(datetime.fromisoformat(queue["expires_at"]).timestamp())
    roster = [f"L{n:03d}" for n in range(1, 13)]
    assert kit["campaign_id"] == kit_id and [leg["leg_id"] for leg in kit["legs"]] == roster
    assert len(queue["spans"]) == len(roster)
    for seq, (entry, leg) in enumerate(zip(queue["spans"], roster), 1):
        assert (entry["seq"], entry["block_id"], entry["legs"], entry["attempt"]) == (seq, kit_id, [leg], 1)
        assert entry["span_id"] == f"{kit_id}-{leg.lower()}"
        assert entry["kit"] == {k: row[k] for k in ("path", "sha256")}
        assert entry["not_before"] == "2026-11-17" and (kit_id, leg) not in positions
        span, _ = plan(pin, kit, leg, local("2026-11-20", "07:03:00"))
        assert span["worst_case_s"] == 5850
        spec, = span["legs"]
        assert spec["budget_s"] == math.ceil(plans[pin].leg_expected_s(spec))
        rs483 = "completed" if (kit_id, leg) in done else "issued" if (kit_id, leg) == l004 else "remaining"
        positions[kit_id, leg] = (pin, seq, rs483, span["expected_s"], span["worst_case_s"])
assert len(positions) == 192
totals = (("A", 168, 769552, 164, 751282), ("B", 24, 109936, 22, 100722))
for pin, population, all_seconds, remaining, seconds in totals:
    rows = [r for r in positions.values() if r[0] == pin]
    unrun = [r for r in rows if r[2] == "remaining"]
    assert sum(r[3] for r in rows) == all_seconds
    assert (len(rows), len(unrun), sum(r[3] for r in unrun)) == (population, remaining, seconds)
assert positions[l004][3:] == (4528, 5850)
for clock, expected_arg in (("00:00:00", "13:14-13:15"), ("02:34:59", "13:14-13:15"),
                            ("02:35:00", "02:00-02:35"), ("10:50:00", "02:00-02:35"),
                            ("10:50:01", None), ("13:14:59", None),
                            ("13:15:00", "02:00-02:35"), ("23:48:10", "02:00-02:35"),
                            ("23:48:11", "13:14-13:15")):
    t0 = local("2026-11-21", clock)
    assert plan("A", kits[l004[0]], l004[1], t0)[1] == expected_arg
    assert plan("B", kits["f2-stab-15"], "L003", t0)[1] == "none"

past_base = {date(2026, 11, 19), date(2026, 11, 20)}
expiry = min(expires.values())
first = local("2026-11-20", "07:03:00") + positions[l004][3]
w1_ready = local("2026-11-22", "20:00:00")
qual_days = {date(2026, 11, day) for day in (23, 24, 25)}
w1_doc = blob("b2e01464d", "docs/align/v4/W1-SMOKE-AGREEMENT.md").decode()
assert "44,640 s" in next(line for line in w1_doc.splitlines() if line.startswith("| W1 plan "))
w1_span = 44640
qual_span = 24750 + 1950 + 560
for block in range(1, 4):
    for span_no in (1, 2):
        path = f"{campaign}/item-drafts-1118/ITEM-qual{block:02d}-s{span_no:02d}.md"
        heading = blob(audit, path).decode().splitlines()[0]
        assert "work worst case 24750 s" in heading
        assert "1,950 s soak retry and 560 s cleanup reserves" in heading

def replay(faster_by=0, preemption=False):
    available = {pin: deque(k for k, r in positions.items() if r[0] == pin and r[2] == "remaining")
                 for pin in pins}
    t0, starts, blocked = first, {}, []
    base_dates = set(past_base)
    qualified_blocks = set()
    w1_started = False
    while t0 <= expiry:
        day = wall(t0).date()
        gap_start, gap_end = local(day, "10:50:01"), local(day, "13:15:00")
        next_day = local(day + timedelta(days=1))
        if preemption and not w1_started and t0 >= w1_ready:
            blocked.append(("W1", t0, t0 + w1_span))
            t0 += w1_span
            w1_started = True
            continue
        qual_release = local(day, "03:00:00")
        qual_due = preemption and day in qual_days and day not in qualified_blocks
        if qual_due and t0 >= qual_release:
            assert t0 <= local(day, "16:32:00") and t0 + qual_span < next_day
            blocked.append(("qual", t0, t0 + 2 * qual_span))
            t0 += 2 * qual_span
            qualified_blocks.add(day)
            continue
        pin = "B" if gap_start <= t0 < gap_end else "A"
        if available[pin]:
            kit_id, leg = key = available[pin][0]
            assert t0 <= expires[kit_id]
            span, arg = plan(pin, kits[kit_id], leg, t0)
            assert span and arg
            rank = 1 if pin == "A" and day not in base_dates else 4
            close = t0 + span["expected_s"] - faster_by
            starts[key] = (t0, close, rank, arg)
            available[pin].popleft()
            if pin == "A":
                base_dates.add(day)
            t0 = close
        else:
            boundary = gap_start if t0 < gap_start else gap_end if t0 < gap_end else next_day
            t0 = min(boundary, qual_release) if qual_due else boundary
    if preemption:
        assert w1_started and qualified_blocks == qual_days
    return starts, blocked

scenarios = {
    "fallback": replay(),
    "fast": replay(faster_by=900),
    "w1_qual": replay(preemption=True),
}
writer = csv.writer(sys.stdout, delimiter="\t", lineterminator="\n")
fields = ["t0_pst", "close_pst", "rank", "batch_window"]
writer.writerow(["kit_id", "leg_id", "queue_seq", "pin", "rs483_status",
                 "expected_s", "worst_s", "expires_at"]
                + [f"{name}_{field}" for name in scenarios for field in fields])
for (kit, leg), (pin, seq, status, expected, worst) in positions.items():
    record = [kit, leg, seq, pin, status, expected, worst, stamp(expires[kit])]
    for starts, _ in scenarios.values():
        if (kit, leg) in starts:
            t0, close, rank, arg = starts[kit, leg]
            record.extend([stamp(t0), stamp(close), rank, arg])
        else:
            record.extend(["-"] * len(fields))
    writer.writerow(record)

checks = {
    "fallback": ("2026-11-29T23:54:19", "2026-12-01T10:50:01", 11, 14),
    "fast": ("2026-11-28T03:24:47", "2026-11-28T11:53:24", 10, 11),
    "w1_qual": ("2026-12-02T07:10:28", "2026-12-04T10:50:01", 14, 17),
}
for name, (starts, blocked) in scenarios.items():
    assert set(starts) == {key for key, row in positions.items() if row[2] == "remaining"}
    occupied = sorted([(start, end) for start, end, _, _ in starts.values()]
                      + [(start, end) for _, start, end in blocked])
    assert all(left[1] <= right[0] for left, right in zip(occupied, occupied[1:]))
    by_day = Counter((wall(row[0]).date(), positions[key][0]) for key, row in starts.items())
    dates = past_base | {day for day, pin in by_day if pin == "A"}
    monthly = dates | {date(2026, 11, 18)} | {day for day, pin in by_day if pin == "B"}
    rank_ones = [wall(start).date() for start, _, rank, _ in starts.values() if rank == 1]
    assert sorted(rank_ones) == sorted(dates - past_base)
    last_a, last_b, a_dates, monthly_dates = checks[name]
    assert (len(dates), len(monthly)) == (a_dates, monthly_dates)
    for pin, last_t0 in (("A", last_a), ("B", last_b)):
        key = (kit_ids[13 if pin == "A" else 15], "L012")
        assert stamp(starts[key][0]) == last_t0 + "-08:00"
        print(name, pin, "last", *map(stamp, starts[key][:2]), file=sys.stderr)
    print(name, "monthly", *(f"{day}:{by_day[day, 'A']}/{by_day[day, 'B']}"
                              for day in sorted(monthly)), file=sys.stderr)
    for kind, start, end in blocked:
        print(kind, stamp(start), stamp(end), file=sys.stderr)
fallback = scenarios["fallback"][0]
for kit, leg, day, clock, rank in (
    ("f2-stab-15", "L003", "2026-11-20", "10:52:02", 4),
    ("f2-stab-15", "L004", "2026-11-20", "12:07:30", 4),
    ("f2-stab-02", "L004", "2026-11-21", "00:50:04", 1),
    ("f2-stab-15", "L005", "2026-11-21", "11:01:59", 4),
    ("f2-stab-15", "L006", "2026-11-21", "12:17:10", 4),
):
    start, _, actual_rank, _ = fallback[kit, leg]
    assert (start, actual_rank) == (local(day, clock), rank)
assert (date(2026, 12, 2) - min(past_base)).days + 1 == 14
print("PASS: 192 positions, per-pin seconds, eligibility boundaries and scenario dates", file=sys.stderr)
PY
```

## Verification and owner handoff

The focused replay checks the 16 kit hashes and queue identities, all 192
unique positions, per-pin totals, the L004 exclusion, admissible start
boundaries, rank transitions, and the conditional exhaustion dates. Its
ledger reproduces byte for byte. The change consists of planning data and
this report, so local verification used the focused replay and diff checks.

**Opus owner inputs.** Choose whether continuous fallback is needed and
which successor to prepare before the applicable gap. Confirm actual
eligibility and the data-lock timing from the lead's records. The current
rulings settle the two read routes and their populations. Any proposal to
change what qualifies as a base date or what enters either population goes
to Fable through Opus before adoption. NEEDS_SPEC for the calculation is
empty.
