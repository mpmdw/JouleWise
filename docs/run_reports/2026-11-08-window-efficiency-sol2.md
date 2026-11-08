# window-efficiency-sol2 handoff

Branch: `perf/2026-11-08-window-efficiency-sol2`, supplied clean at intake.
Base: `4e7e878a151d919faf56bb9131af1fcca4b7be75`.
Deliverable: [WINDOW-EFFICIENCY-sol2.md](../perf/WINDOW-EFFICIENCY-sol2.md).
This is an independent design seat, not an implementation or registration.

## Work and findings

Read repository intake/stop-card/machine-lane instructions, targeted decision
authority, RUN_STATE items 160–213, the requested Git-backed v4 protocol,
thermal rules, kit roster, R1 runtime/phase/bound functions and lead rulings,
pilot-3 protocol/sizing evidence, energy residual contract, relevant ALIGN
implementation reports, and the requested v5 designs/judgments' thermal,
sampling, cost and inference discussions. Sources are pinned below and in
the deliverable. No other window-efficiency seat's branch was inspected.

The report provides disjoint W1/D reservation budgets; nested phase accounting
with explicit missing observations; overhead/confound/evidence/alternative
tables; two costed designs; and record-only R1 analyses. Principal findings:

- A default D roster has **18 D members plus four anchors**. The calculated
  maximum is 58,260 s, permitted ceiling 59,520 s, unrounded collection plan
  40,526.27 s. Reserved slack is not measured overhead or saved compute.
- v4-lean keeps the reference-state experiment and changes turnaround. Seven
  calibration windows supply 49 benign/pair, 42 after one whole-window loss.
  W1 + seven calibration + three small test windows cost 128.3025 cycle-hours
  (5.3459 continuous Mac-days) at planning values and 45 min turnaround. This
  is a sample-count bill, conditional on the admitted score law and fit roles;
  a five-calibrator/pair variant needs nine calibration windows for one-loss
  margin and 6.3465 cycle-days. It is not a completed registration-grade gate.
- v4-max is explicitly a **new thermal estimand/calibration**, conditional on
  a qualified 1,200 s all-in native D member. Four calibration + three test
  windows, with W1 allowance and two new qualification windows, cost 135.4670
  cycle-hours (5.6445 days). It buys more useful test attempts; qualification
  prevents claiming an immediate end-to-end time saving over lean.
- A source-level scheduler replay found the R1 table's +5,400 s “maximum
  batch wait” is not a universal bound. At synthetic 10:30 PST, a 5,763.9952 s
  segment waits **9,900 s** to 13:15. The actual forward-overlap policy can
  wait before the blackout starts. No R1 code or plan was changed.

## Files and custody

Only these files are intended changes:

- `docs/perf/WINDOW-EFFICIENCY-sol2.md`
- `docs/run_reports/2026-11-08-window-efficiency-sol2.md` (this handoff)

No coordination files, kernel tasks, production code, tests, run bundles or
hardware settings were edited. The user's explicit prohibition on editing
RUN_STATE/TASK_QUEUE/state-kernel overrides the ordinary end-of-work workflow.
Git-backed source text was extracted to a seat-created directory under
`/private/tmp/window-efficiency-sol2-sources`; no model or measurement path
quoted in it was followed. One initial extraction requested a pruned council
file on the kit ref and failed; the required governing material was available
in the requested protocol/rulings and main's existing council documents.

No network, model download, real measurement/data analysis, Block-5 pipeline,
process census, running-job inspection, quiet measurement, or subagent was
used. The armed R1 job and blinded analysis job were untouched.

## Source pins

Kit/R1: `d600baba029f70592bb8e792098338e4cd6811d3`, cached
`origin/lane/2026-11-07-w1-kit-r10`. Main text: base commit above.
R11's adopted cross-review agreement:
`4526de7d587a412073cf792c959090401e8d4797`,
`docs/align/squeeze/AGREEMENT-FINAL.md`.

All v5 paths are `docs/align/squeeze/v5-design/<file>` on the corresponding
cached `origin/align/2026-11-08-v5design-*` ref:

| File | Commit |
|---|---|
| `addon-opus.md` | `fa2c0a9865b13164ce339a379d4dc3903789fcc1` |
| `addon-sol1.md` | `6ad7a475aec66b2c1b06c8d9b2e378ab22281230` |
| `addon-sol2.md` | `e2e255a941bfaa81387ee6ac56909c25a17597dd` |
| `groundup-opus.md` | `cb54bc168ca0276c0d31d38c976224bb9266eb91` |
| `groundup-sol1.md` | `f63ca1aa5b7ec3673533f9631698a8370b932e93` |
| `groundup-sol2.md` | `23cb07a240ac1fdba6c2609561d195607ead3cd2` |
| `sol1-sol1.md` (judge-sol1) | `3fbcf3da4056f8fb952b6b3eb4d8160831afee93` |
| `sol2-sol2.md` (judge-sol2) | `0867a29a4e29b70a0ceb2bc01185ad3093065775` |

## Verification

Docs-only change. No full/sharded/quick suite, compileall, or native tests
were run: they add load to the active eight-worker job and do not validate
these proposed physical assumptions. No production behavior changed.

Executed standard-library arithmetic/source checks below with Python 3.13,
one process, no real sleeping or runtime imports. They validate source roster
counts/constants, window arithmetic, sample margins, campaign bills, and the
actual pure scheduling functions on synthetic time. `git diff --check` also
passes. The report was reviewed for reservation-versus-collection accounting,
double-counted subphases, calibration/test separation and claim changes.
Result: **36 checks passed**, synthetic scheduler wait **9,900 s**, under
one second. Both Markdown files pass trailing-whitespace and fence checks.

Command used (the Python block below is the checked program):

```sh
python3.13 -B - <<'PY'
from pathlib import Path
text = Path('docs/run_reports/2026-11-08-window-efficiency-sol2.md').read_text()
program = text.split('```python\n', 1)[1].split('\n```', 1)[0]
exec(compile(program, '<run-report arithmetic checks>', 'exec'))
PY
```

Reproduce from this clone's root by extracting/executing this single Python
block (it reads only the pinned repository objects):

```python
import ast
import datetime as dt
import json
import math
import subprocess
from zoneinfo import ZoneInfo

PIN = "d600baba029f70592bb8e792098338e4cd6811d3"
checks = 0

def source(path):
    return subprocess.check_output(["git", "show", f"{PIN}:{path}"], text=True)

def check(condition):
    global checks
    assert condition
    checks += 1

def near(actual, expected):
    check(abs(actual - expected) < 1e-6)

kit = ast.parse(source("scripts/align_v4_kit.py"))
names = {"ROSTER", "SCAFFOLD_S", "DEADMAN_FACTOR", "MEMBER_CAP_S"}
constants = {}
for node in kit.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                constants[target.id] = ast.literal_eval(node.value)
roster = constants["ROSTER"]
check(len(roster) == 18)
check(sum(row[0] == "D" for row in roster) == 6)
check(sum(row[0] == "anchor" for row in roster) == 4)
check(sum(row[0] in ("X-G", "Y-G", "X-S", "Y-S") for row in roster) == 8)
check(roster[16] == roster[4])
check(constants["SCAFFOLD_S"] == 4995)
near(constants["DEADMAN_FACTOR"], 1.13544)
check(constants["MEMBER_CAP_S"] == 1800)
sizing = json.loads(source("configs/campaigns/align_pilot_v3/registration/sizing_b5.json"))
near(sizing["packs"]["align-pilot-v3"]["scaffold_s"], 4995)

a, scaffold, reserve = 3131.27, 4995, 17700
w1 = a + 6*1800 + 4*850 + 4*1150 + scaffold
d = a + 18*1800 + scaffold
maximum = lambda span: 60*math.ceil((math.ceil(span)+reserve)/60)
near(w1, 26926.27)
near(d, 40526.27)
check(maximum(w1) == 44640)
check(maximum(d) == 58260)
near(58260-(d+reserve), 33.73)
check(math.ceil(39/7) == 6)
check(7*7-7 == 42)
check(math.ceil(39/16) == 3)
check(4*16-16 == 48)
check(math.ceil(39/5) == 8)
check(9*5-5 == 40)
near((10*d+w1)/3600+11*.75, 128.30249166666667)
near((12*d+w1)/3600+13*.75, 152.3170861111111)
b = 36*1200+scaffold
near(b/3600, 13.3875)
near(32/(b/3600), 2.3902894491129785)
near((7*b+w1)/3600+8*.75, 107.19201944444444)
near((7*b+w1)/3600+8*.75+2*(b/3600+.75), 135.46701944444444)
check(maximum(b) == 65940)
check(60*math.ceil((b+1800)/60) == 50040)
near(10240/11.9+40+10+60+40+30+30+129.49579831932772, 1200)

member = 1750+1.13544*1580+120
r1 = (1800 + member+1500 + 3*(665+member) + 4*1500
      + member+2100 + 3*(member+2100) + 4*1800)
near(r1, 56206.9616)
near(r1+5400, 61606.9616)
near(r1+4*(1500+member+2100)+5400, 90662.9424)

tree = ast.parse(source("scripts/align_r1_rehearsal.py"))
pure = [n for n in tree.body if isinstance(n, ast.FunctionDef)
        and n.name in ("_batch_windows", "wait_outside_os_batch")]
check(len(pure) == 2)
ns = {"datetime": dt.datetime, "timedelta": dt.timedelta,
      "wall_time": dt.time, "LOCAL_ZONE": ZoneInfo("America/Los_Angeles"),
      "OS_BATCH_WINDOW_LOCAL": ((11,45),(13,15))}
exec(compile(ast.Module(body=pure, type_ignores=[]), "<pure scheduler>", "exec"), ns)
clock = [dt.datetime(2026,11,8,10,30,tzinfo=ns["LOCAL_ZONE"])]
def advance(seconds):
    clock[0] += dt.timedelta(seconds=seconds)
waited = ns["wait_outside_os_batch"](5763.9952, now=lambda: clock[0], sleep=advance)
near(waited, 9900)
check((clock[0].hour, clock[0].minute) == (13,15))
near(r1+5763.9952+5400, 67370.9568)
print(f"PASS: {checks} arithmetic/source checks; synthetic wait={waited:.0f} s")
```

## Open questions, uncertainty and next exact step

No blocking question prevented this design report or local commit. The lead
still owns these scientific/operational decisions:

1. Whether retaining v4's reference-state claim is essential. Max is not
   claim-equivalent to lean and cannot share its calibration.
2. Actual R1 D phase costs, released/censored G0, duty/turn validity, tail fit,
   instrument/meter coverage and the R10 disposition. No R1 outcome is claimed.
3. Appropriate held-out test size and number of independent temporal windows.
   m≥39 is a calibration-count requirement, not evidence of power or an
   unconditional 5% FPR guarantee. Lean's small three-sabotage/pair test is
   specifically disclosed as weak.
4. Source scheduler wait underbudget and R1's unbounded bracket/harvest/redo
   additions. Compare the actual completed record; do not change armed R1.
5. Qualification of shorter baselines, resident workers and state-conditioned
   scores before max could be adopted. Their timing/bias benefits are unproven.

Next: after R1 closes, run the record-only analyses in deliverable §7 on an
exported copy off-Mac; apply R10, then register lean or commission max's new
native qualification. No quiet-machine work is authorized from this seat.

No MLX code was changed, so there is no newly written native test to run for
this docs commit. If max is implemented, the lead must run the kit's native
hold/identity/cache checks outside the sandbox (including
`tests.align.test_thermal_mlx` and `tests.align.test_cache_checkpoint_native`
where applicable), plus **new** resident-worker identity, long-run state/memory,
ungated predictive-null and injected-work sensitivity qualification. Existing
gated native tests alone cannot establish max's new scientific conditions.

The local commit hash is reported in the final handoff; no push is intended.
