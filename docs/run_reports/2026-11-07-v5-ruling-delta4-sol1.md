# 2026-11-07 — v5 ruling delta4 review, Sol1

Task: `v5-ruling-delta4`, independent seat **sol1**. Candidate ruling is
revision 4, dated 2026-11-08; this report uses the intake date 2026-11-07.
The environment date advanced to 2026-11-08 before the local commit.
Branch: `align/2026-11-08-v5design-ruling-delta4-sol1` (already provisioned at
intake). Initial HEAD: `52e976dc928c30bb73bcb722ea5cca9dc37bae2c`.
Initial worktree was clean. No other writer or sub-agent was started.

## Outcome and changed files

**SIGN_WITH_CHANGES** for one prospective power-planning condition. All eight
R1–R4 findings across E1/E2 are Resolved at ruling level. The fixed-horizon
capital process supplies valid p-values under the registered per-date
conditional-mean null, and Holm permits their dependence. H4's 224-attempt
phased roster, CAP gross-hours/single-yield convention, rank tails and revised
732.7/915.9 and 1,191.0-hour figures reproduce.

The temporary synthetic simulation found H1–H3 Holm power of 15.67% for
15-point effects at G=28, 3.20% for 20-point effects at G=20, and 96.64% for
20-point effects at G=28, in favorable no-regression laws. With 5–10-point
effects, no conjunction rejection occurred in 12,000 replications per row.
Stakes equal to 1 dominate all permitted stakes/mixtures on these laws.
These are synthetic planning results, not measured effects or full G12
certification. See the review for exact laws, limitations and recommendations.

Files added:

- `docs/align/squeeze/v5-design/ruling-delta4-review-sol1.md` — requested review.
- This dated run report — intake, checks and exact simulation source/output.

The ruling and coordination state are unchanged. No decision-log ruling or
risk-register status was installed by this review seat. No kernel task was
registered.

## Intake, authority and boundaries

Read AGENTS.md, CLAUDE.md, Mission M0, orchestration, AP's required fields and
registry rules, and D-062. Inspected the generated stop card (NONE), current
status, known workspace, restart/lane pointers and queue restrictions. The
user's explicit bounded offline review overrides ordinary queue selection
and coordination updates. RUN_STATE.md, TASK_QUEUE.md,
`docs/process/state_kernel.json` and `tests/test_gen_state.py` were preserved.

Read the full `git diff b606d9788..HEAD` (one Markdown file; +96/-44) and the
candidate ruling. Read both delta3 reports through existing local Git refs:
E1 `570ccd7131c9452746ca2d99a1cc4a3a630fde72`, E2
`4e17eb873b85e1238a2733b5ced5cc6bf0a5e81d`. No fetch or network was used.
No external user-tree path, real restricted directory, measurement file,
night record, process/job status, model weight or blinded analysis pipeline
was inspected. Git's existing alternate-object store was used only through
Git object reads allowed by the brief. Temporary files are under
`/private/tmp`; their literal constants and synthetic outcomes are unblinded.

## Verification and uncertainty

- `python3.13 -I -B -c 'import sys; print(sys.version.split()[0])'`:
  **3.13.18**.
- `python3.13 -I -B /private/tmp/jw-v5-delta4-sol1-check.py > /private/tmp/jw-v5-delta4-sol1-check.out`:
  **PASS**, exit 0. One process, no parallel workers; 144,000 total synthetic
  replications. Exact rational arithmetic/roster assertions and full Holm
  simulation are archived below. Source SHA-256:
  `9d84bbf9f7dde139f76d4876bfb5d0b6efc95b35a8a9af2a3e7b16cc758f6f49`.
- Separate `python3.13 -I -B -` constant-path calculation with
  `ceil(log(80)/log(1+effect))`: **PASS**, .05/.10/.15/.20 give
  **90/46/32/25 dates**. These are deterministic capital benchmarks, not
  80%-power sample sizes.
- No unittest, full/sharded suite, compileall, MLX or native hardware check
  was needed or run: the deliverables are Markdown and the simulator imports
  only stdlib. The user's no-full-suite and machine-load restrictions govern.
- Final staged diff/whitespace and source-archive checks are recorded below.

No test failure was encountered. Actual v5 effects/capability, random
calibration, missingness, receipt coverage, native determinism, host timing,
CAP/calendar, physical resolution, venue/novelty and Sol2's new verdict are
unknown. The power run does not establish they will pass. Honest-FPR
confidence inversion still needs its exact conditional estimand/sign frozen
at implementation; it must not claim a marginal-average guarantee under
unrestricted heterogeneous date rates.

Native follow-up outside the sandbox: once integrated code exists, use the
import-gated tiny-synthetic MLX unittest modules for actual/public replay,
forced twins, history/cache/RNG, receipt partitioning, helper concurrency/
teardown and tails, one module at a time. No such new module exists in this
docs-only task; none is claimed tested. Download no weights for those tests.
Actual hardware/quiet gates belong to the lead's later clean machine lane.

Next exact step: lead compares the two independent delta4 reviews, rules P1's
MDE/joint-power target and early sizing route, retains closed R1–R4 repairs,
and obtains a prospective CAP/calendar fit before G12 freezes the design.
The review does not authorize collection, scoring, downloads or publishing.
The local commit is the branch commit containing this report and review; it
is intentionally not pushed.

## Exact synthetic check source

The following is the complete temporary script as executed; its source hash
above covers the code bytes, including its trailing newline.

```python
from fractions import Fraction as F
from math import ceil, exp, log, sqrt
from random import Random
import hashlib
from pathlib import Path

SEED = 202611070401
REPS = 12000

def holm(logk):
    rejected = set()
    for rank, k in enumerate(sorted(range(4), key=lambda k: -logk[k])):
        if logk[k] >= log((4-rank)/.05):
            rejected.add(k)
        else:
            break
    return rejected

def wilson(k, n):
    z = 1.959963984540054
    p = k/n
    den = 1+z*z/n
    center = (p+z*z/(2*n))/den
    half = z*sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return center-half, center+half

offsets = (0,1,2,1,2,0)
subset = [[(1 if (w+o)%3 < 2 else 2) for o in offsets] for w in range(28)]
assert all(sum(row)==8 and min(row)==1 for row in subset)
assert sum(map(sum, subset)) == 224
cell_totals = [sum(row[s] for row in subset) for s in range(6)]
assert sorted(cell_totals) == [37,37,37,37,38,38]
print('H4 windows=28 per_window=8 cover=4 total=224 cells='+str(cell_totals))
for g in (20,28,40,60):
    first = exp(log(80)/g)-1
    third = exp(log(40)/g)-1
    print(f'constant_date_effect G={g} first_Holm={first:.6f} third_Holm={third:.6f}')

local_one = (F(30000,600)+F(1000,35))/3600
local = 810*local_one
for t in (900,1200,1800):
    base = F(2180*t,3600)+46+F(966*2*t,5*3600)+6+local
    extra = F(64*t,3600)+2+F(28*2*t,5*3600)+28*local_one
    go = base+extra
    print(f'ledger t={t} local810={float(local):.9f} extra_local28={float(28*local_one):.9f} base={float(base):.9f} reserved={float(base*F(5,4)):.9f} cap_extra={float(extra):.9f} GO={float(go):.9f} GO_reserved={float(go*F(5,4)):.9f}')
for m in (39,44,49,63):
    k = ceil(F(95,100)*(m+1))
    print(f'rank m={m} k={k} tail={float(F(m+1-k,m+1)):.9f}')
assert F(24*112,168) == 16
assert F(100,1)*F(5,4)/24 == F(100,1)/(24*F(4,5))
print('CAP busy112h/span168h=16h/day; base100h/a0.8/gross24h=5.208333333 days; a0.7 multiplier=1.428571429')
print(f'SIM seed={SEED} reps_per_row={REPS} stake=1; no missingness, fixed thresholds, perfect availability; coherent no-regression detectors')

# Each attempt draws a single uniform category. A: side success, E catches,
# M=time+M=S miss. B: side success, M=time+M=S catch, E misses.
# Otherwise all detectors miss; side success iff u<q. Both joint rules
# equal the OR. Thus d1=d3 on the full roster; d2 is disjoint; d4 is the
# assigned H4 subset. This is a feasible optimistic binary alarm law.
# All returns are nonnegative, so lambda=1 pathwise dominates every allowed
# predictable stake and every normalized frozen mixture in this law.
scenarios = [(20,.05,.05,.4),(28,.05,.05,.4),
             (20,.10,.10,.4),(28,.10,.10,.4),
             (20,.15,.15,.4),(28,.15,.15,.4),
             (20,.20,.20,.5),(28,.20,.20,.5),
             (20,.25,.25,.6),(28,.25,.25,.6),
             (28,.30,.30,.7),(28,.06,.18,.4)]
for row,(g,mu_a,mu_b,q) in enumerate(scenarios):
    rng = Random(SEED+row)
    # At G=20: 8 double-window dates followed by 12 single-window dates.
    # At G=28: 28 single-window dates. Dates and offsets are deterministic.
    date_windows=[]
    w=0
    for date in range(g):
        count=2 if date < 28-g else 1
        date_windows.append(list(range(w,w+count)))
        w+=count
    assert w==28 and len(date_windows)==g
    counts = [0,0,0,0,0]
    for rep in range(REPS):
        logk = [0.,0.,0.,0.]
        success = [0,0]
        h4success = [0,0]
        h4n = [0,0]
        for windows in date_windows:
            sum_a=sum_b=sum_h4=0.
            for s in range(6):
                a=b=ah=nh=0
                pair=s//3
                for win in windows:
                    n_h4=subset[win][s]
                    for attempt in range(2):
                        u=rng.random()
                        is_a=u<mu_a
                        is_b=mu_a<=u<mu_a+mu_b
                        is_h4=attempt<n_h4
                        ok=u<q
                        a+=is_a
                        b+=is_b
                        success[pair]+=ok
                        if is_h4:
                            ah+=is_a
                            nh+=1
                            h4success[pair]+=ok
                            h4n[pair]+=1
                sum_a+=a/(2*len(windows))
                sum_b+=b/(2*len(windows))
                sum_h4+=ah/nh
            da,db,dh = sum_a/6,sum_b/6,sum_h4/6
            logk[0]+=log(1+da)
            logk[1]+=log(1+db)
            logk[2]+=log(1+da)
            logk[3]+=log(1+dh)
        r=holm(logk)
        capability = (sum(success)/336>=.30 and min(success)/168>=.20
                      and sum(h4success)/224>=.30
                      and all(h4success[p]/h4n[p]>=.20 for p in (0,1)))
        counts[0]+=max(logk)>=log(80)
        counts[1]+=all(k in r for k in (0,1,2))
        counts[2]+=len(r)==4
        counts[3]+=capability and all(k in r for k in (0,1,2))
        counts[4]+=capability
    lo,hi=wilson(counts[1],REPS)
    print(f'SIM G={g} effects=({mu_a:.2f},{mu_b:.2f},{mu_a:.2f},{mu_a:.2f}) q={q:.2f} any_first={counts[0]/REPS:.6f} H1to3={counts[1]/REPS:.6f} CI95=[{lo:.6f},{hi:.6f}] all4={counts[2]/REPS:.6f} capability_and_H1to3={counts[3]/REPS:.6f} capability={counts[4]/REPS:.6f}',flush=True)
print('ASSERTIONS PASS: literal arithmetic and synthetic laws only; no repo/data imports')
print('script_sha256='+hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
```

## Complete check output

```text
H4 windows=28 per_window=8 cover=4 total=224 cells=[37, 37, 38, 37, 38, 37]
constant_date_effect G=20 first_Holm=0.244957 third_Holm=0.202550
constant_date_effect G=28 first_Holm=0.169412 third_Holm=0.140818
constant_date_effect G=40 first_Holm=0.115777 third_Holm=0.096608
constant_date_effect G=60 first_Holm=0.075767 third_Holm=0.063411
ledger t=900 local810=17.678571429 extra_local28=0.611111111 base=711.278571429 reserved=889.098214286 cap_extra=21.411111111 GO=732.689682540 GO_reserved=915.862103175
ledger t=1200 local810=17.678571429 extra_local28=0.611111111 base=925.145238095 reserved=1156.431547619 cap_extra=27.677777778 GO=952.823015873 GO_reserved=1191.028769841
ledger t=1800 local810=17.678571429 extra_local28=0.611111111 base=1352.878571429 reserved=1691.098214286 cap_extra=40.211111111 GO=1393.089682540 GO_reserved=1741.362103175
rank m=39 k=38 tail=0.050000000
rank m=44 k=43 tail=0.044444444
rank m=49 k=48 tail=0.040000000
rank m=63 k=61 tail=0.046875000
CAP busy112h/span168h=16h/day; base100h/a0.8/gross24h=5.208333333 days; a0.7 multiplier=1.428571429
SIM seed=202611070401 reps_per_row=12000 stake=1; no missingness, fixed thresholds, perfect availability; coherent no-regression detectors
SIM G=20 effects=(0.05,0.05,0.05,0.05) q=0.40 any_first=0.000000 H1to3=0.000000 CI95=[0.000000,0.000320] all4=0.000000 capability_and_H1to3=0.000000 capability=0.999500
SIM G=28 effects=(0.05,0.05,0.05,0.05) q=0.40 any_first=0.000000 H1to3=0.000000 CI95=[0.000000,0.000320] all4=0.000000 capability_and_H1to3=0.000000 capability=0.998667
SIM G=20 effects=(0.10,0.10,0.10,0.10) q=0.40 any_first=0.000000 H1to3=0.000000 CI95=[0.000000,0.000320] all4=0.000000 capability_and_H1to3=0.000000 capability=0.999000
SIM G=28 effects=(0.10,0.10,0.10,0.10) q=0.40 any_first=0.000333 H1to3=0.000000 CI95=[0.000000,0.000320] all4=0.000000 capability_and_H1to3=0.000000 capability=0.998500
SIM G=20 effects=(0.15,0.15,0.15,0.15) q=0.40 any_first=0.000000 H1to3=0.000000 CI95=[0.000000,0.000320] all4=0.000000 capability_and_H1to3=0.000000 capability=0.998750
SIM G=28 effects=(0.15,0.15,0.15,0.15) q=0.40 any_first=0.271667 H1to3=0.156667 CI95=[0.150273,0.163280] all4=0.156667 capability_and_H1to3=0.156667 capability=0.998417
SIM G=20 effects=(0.20,0.20,0.20,0.20) q=0.50 any_first=0.070000 H1to3=0.032000 CI95=[0.028998,0.035302] all4=0.032000 capability_and_H1to3=0.032000 capability=1.000000
SIM G=28 effects=(0.20,0.20,0.20,0.20) q=0.50 any_first=0.995167 H1to3=0.966417 CI95=[0.963041,0.969494] all4=0.966333 capability_and_H1to3=0.966417 capability=1.000000
SIM G=20 effects=(0.25,0.25,0.25,0.25) q=0.60 any_first=0.842583 H1to3=0.715750 CI95=[0.707612,0.723750] all4=0.715750 capability_and_H1to3=0.715750 capability=1.000000
SIM G=28 effects=(0.25,0.25,0.25,0.25) q=0.60 any_first=1.000000 H1to3=0.999917 CI95=[0.999528,0.999985] all4=0.999917 capability_and_H1to3=0.999917 capability=1.000000
SIM G=28 effects=(0.30,0.30,0.30,0.30) q=0.70 any_first=1.000000 H1to3=1.000000 CI95=[0.999680,1.000000] all4=1.000000 capability_and_H1to3=1.000000 capability=1.000000
SIM G=28 effects=(0.06,0.18,0.06,0.06) q=0.40 any_first=0.605083 H1to3=0.000000 CI95=[0.000000,0.000320] all4=0.000000 capability_and_H1to3=0.000000 capability=0.998750
ASSERTIONS PASS: literal arithmetic and synthetic laws only; no repo/data imports
script_sha256=9d84bbf9f7dde139f76d4876bfb5d0b6efc95b35a8a9af2a3e7b16cc758f6f49
```

## Final documentation checks

- `git diff --cached --check`: **PASS**, no whitespace errors.
- Staged scope: **only the two Markdown files named above**; the ruling,
  code, tests and lead-owned coordination files are unchanged. No unstaged
  edits or unrelated user work were present.
- `python3.13 -I -B -` archive audit: **PASS**. The report's complete source
  exactly matches the executed temporary script and SHA-256; AST syntax
  parses; complete stdout matches the saved output; every quoted numeric
  output line in the review matches stdout; all eight E1/E2 finding rows
  and balanced Markdown fences are present.
- The arithmetic checks found no remaining discrepancy in the requested
  ledger, roster, rank or capacity examples. The power check identified the
  material number affecting this seat's verdict: 20 dates and 20-point
  effects gave only 3.20% H1–H3 power under the favorable synthetic law.
- Git commit hooks in this clone contain only sample files; no full test
  suite, network hook or other job was invoked for the local docs commit.
