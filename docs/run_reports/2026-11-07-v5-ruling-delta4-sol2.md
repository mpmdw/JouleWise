# v5 ruling delta4 — Sol2 session report

Date: 2026-11-07 (local session date; the candidate/branch is labelled 11-08).
Task: `v5-ruling-delta4`, independent seat **sol2**.
Branch: `align/2026-11-08-v5design-ruling-delta4-sol2` (already created for
this clone at intake; used as supplied).
Candidate reviewed: `52e976dc928c30bb73bcb722ea5cca9dc37bae2c`.
Baseline: `b606d9788cd0cb25e0c85903ba7c75116edad894`.

## Result and scope

**SIGN_WITH_CHANGES.** Both prior seats' R1–R4 close at ruling level. The
conditional-mean wealth test and Holm are valid as specified; the H4 roster,
CAP units/single yield, local cap scoring, rank-tail and ledger reproduce.
New P1 asks the lead to settle power feasibility before expensive G4–G11
work. Even the pathwise-best allowed bets on nonnegative outcomes have
poor power for modest reductions at 20–28 dates. The .10 effect scenario
almost never rejects in the optimistic simulation; .20 can work at 28
dates. Actual effect sizes and the final stake rule are unknown. The
review also records the exact honest-rate interval target as a G12 item.

Deliverables:

- `docs/align/squeeze/v5-design/ruling-delta4-review-sol2.md` — quotes and
  statuses for both seats, proof, power assessment, independent arithmetic,
  signature condition, cosmetic notes and native-check handoff.
- This dated run report — reproducible synthetic source/output and process
  evidence. No implementation or production test changed.

Intake read the repository AGENTS/CLAUDE conventions, AGENT_PLAN map,
Mission M0, applicable orchestration sections, generated stop/restart and
queue/do-not-do views, AP, D-050/D-062/D-186, both delta3 review objects
and the entire requested candidate diff. Stop card and global work-selection
gates were NONE. This explicitly assigned docs review is the authorized
[AGENT] work; the user forbade queue/kernel registration and coordination
writes, so none were made. No phase exit item or live gate is being closed.
The working tree was clean at intake on the supplied sol2 branch. No other
agent or cross-model consult was launched; independent companion review
and final lead adjudication remain external to this seat.

No path under the external user tree, real restricted directory, sealed
measurement corpus, job/process state or blinded analysis output was read.
Absolute data locations encountered in repository prose were treated as
text. Git read only this clone and permitted shared object storage. No
network, model download, pipeline, native MLX, measurement or quiet-machine
operation occurred. No commit is pushed, and no publication is authorized.

## Reproducible check

Executed once, in a single process:

```text
python3.13 -I -B /private/tmp/jw-v5-ruling-delta4-sol2-check.py > /private/tmp/jw-v5-ruling-delta4-sol2-check.out
```

Exit **0**, all assertions passed. These are temporary artifacts created
by this session, containing only design constants and synthetic values.
The source is preserved verbatim below so the temporary path is not the
only evidence. It imports no project code, MLX, Torch or measurement reader.
The final line fingerprints the source; a changed filename does not affect
its byte hash. There are 16 settings × 10,000 repetitions. Seed offsets,
class phases, date grouping, delta law, stakes and full Holm logic are
explicit in the source. The joint table is one correlated synthetic family,
not G12 power certification. The review states its favorable omissions and
Monte Carlo uncertainty. Regression-law rows are one stake strategy rather
than a power ceiling; monotone rows bound every allowed stake rule on those
same paths.

```python
import hashlib
import math
import random
from fractions import Fraction as Q
from pathlib import Path

REPS = 10000
SEED = 20261108
PHASES = (('C', 'E'), ('C', 'U'), ('E', 'U'))
OFFSETS = (0, 0, 1, 1, 2, 2)
WINDOWS = tuple(tuple(PHASES[(w + s) % 3] for s in OFFSETS) for w in range(28))
assert all(sum(x != 'C' for cell in w for x in cell) == 8 for w in WINDOWS)
assert all(all(any(x != 'C' for x in cell) for cell in w) for w in WINDOWS)
cell_totals = [sum(x != 'C' for w in WINDOWS for x in w[s]) for s in range(6)]
assert cell_totals == [37, 37, 37, 37, 38, 38]
print('H4 windows=28 each_H4=8 each_cover=4 H4_total=224 cover_total=112 cells=' + str(cell_totals))
print('classes_total=' + str({c: sum(x == c for w in WINDOWS for cell in w for x in cell) for c in 'CEU'}))
L = Q(810) * (Q(30000,600) + Q(1000,35)) / 3600
LC = Q(28) * (Q(30000,600) + Q(1000,35)) / 3600
for t in (900,1200,1800):
    b = Q(2180*t,3600) + 46 + Q(966*2*t,5*3600) + 6 + L
    extra = Q(64*t,3600) + 2 + Q(28*2*t,5*3600) + LC
    print(f'ledger t={t} base={float(b):.6f} reserved={float(b*Q(5,4)):.6f} cap_extra={float(extra):.6f} GO_base={float(b+extra):.6f} GO_reserved={float((b+extra)*Q(5,4)):.6f}')
print(f'local base_h={float(L):.9f} cap_add_h={float(LC):.9f}')
for m in (39,42,44,46,49,63):
    k = (95*(m+1)+99)//100
    print(f'rank m={m} k={k} tail={float(Q(m+1-k,m+1)):.6f}')
assert Q(24*112,168) == 16
assert Q(100)*Q(5,4)/16 == Q(100)/(Q(16)*Q(4,5))
print(f'CAP gross112h/168h={24*112/168:.6f}h/day transfer={.85*16:.6f} yield80_days={125/16:.6f} yield70_multiplier={1/.7:.6f}')
for g in (20,28):
    print(f'constant_date G={g} first_Holm_min_d={math.expm1(math.log(80)/g):.6f} if_H4_first_min_d={math.expm1(math.log(60)/g):.6f}')
for mu in (.05,.10,.15,.20,.25,.30):
    print(f'constant_effect mu={mu:.2f} G_needed_for_K80={math.ceil(math.log(80)/math.log1p(mu))}')

def make_dates(g):
    # G=20: first 8 dates have two windows, next 12 dates one. G=28: all one.
    ns = [2]*(28-g) + [1]*(2*g-28)
    dates, w = [], 0
    for n in ns:
        dates.append(WINDOWS[w:w+n])
        w += n
    assert w == 28 and len(dates) == g
    return dates

def holm(ps):
    rejected = [False]*4
    for j, k in enumerate(sorted(range(4), key=ps.__getitem__)):
        if ps[k] > .05/(4-j):
            break
        rejected[k] = True
    return rejected

print(f'POWER reps={REPS} seed={SEED} lambda=1 no_missing no_threshold_noise common_attempt_deltas H1=H2=H3; H4=subset')
print('G mu regression H1_first H4_first Holm_H1to3 Holm_all4')
for g in (20,28):
    dates = make_dates(g)
    for mu, regression in [(v,0.0) for v in (.05,.10,.15,.20,.25,.30)] + [(.10,.05),(.20,.05)]:
        rng = random.Random(SEED + 100000*g + round(mu*10000) + round(regression*1000))
        counts = [0]*4
        for rep in range(REPS):
            log_full = log_sub = 0.0
            for date in dates:
                df = ds = 0.0
                for s in range(6):
                    sf = ss = nf = ns = 0
                    for window in date:
                        for cls in window[s]:
                            u = rng.random()
                            delta = 1 if u < mu+regression else (-1 if u < mu+2*regression else 0)
                            sf += delta
                            nf += 1
                            if cls != 'C':
                                ss += delta
                                ns += 1
                    df += sf/nf/6
                    ds += ss/ns/6
                log_full += math.log1p(df) if df > -1 else -math.inf
                log_sub += math.log1p(ds) if ds > -1 else -math.inf
            pf = math.exp(-log_full) if log_full > 0 else 1.0
            ps = math.exp(-log_sub) if log_sub > 0 else 1.0
            rejects = holm([pf,pf,pf,ps])
            counts[0] += pf <= .0125
            counts[1] += ps <= .0125
            counts[2] += all(rejects[:3])
            counts[3] += all(rejects)
        print(f'{g} {mu:.2f} {regression:.2f} ' + ' '.join(f'{c/REPS:.4f}' for c in counts), flush=True)
# The full H0 permits rarer -1 dates. A data-snooping early final-horizon
# choice is absent: all runs use every sealed synthetic date.
assert holm([.001,.01,.02,1]) == [True,True,True,False]
assert holm([.013,.013,.013,.013]) == [False]*4
print('ASSERTIONS PASS: roster, arithmetic, Holm examples; synthetic power only')
print('script_sha256=' + hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
```

Complete **verbatim output**:

```text
H4 windows=28 each_H4=8 each_cover=4 H4_total=224 cover_total=112 cells=[37, 37, 37, 37, 38, 38]
classes_total={'C': 112, 'E': 112, 'U': 112}
ledger t=900 base=711.278571 reserved=889.098214 cap_extra=21.411111 GO_base=732.689683 GO_reserved=915.862103
ledger t=1200 base=925.145238 reserved=1156.431548 cap_extra=27.677778 GO_base=952.823016 GO_reserved=1191.028770
ledger t=1800 base=1352.878571 reserved=1691.098214 cap_extra=40.211111 GO_base=1393.089683 GO_reserved=1741.362103
local base_h=17.678571429 cap_add_h=0.611111111
rank m=39 k=38 tail=0.050000
rank m=42 k=41 tail=0.046512
rank m=44 k=43 tail=0.044444
rank m=46 k=45 tail=0.042553
rank m=49 k=48 tail=0.040000
rank m=63 k=61 tail=0.046875
CAP gross112h/168h=16.000000h/day transfer=13.600000 yield80_days=7.812500 yield70_multiplier=1.428571
constant_date G=20 first_Holm_min_d=0.244957 if_H4_first_min_d=0.227178
constant_date G=28 first_Holm_min_d=0.169412 if_H4_first_min_d=0.157458
constant_effect mu=0.05 G_needed_for_K80=90
constant_effect mu=0.10 G_needed_for_K80=46
constant_effect mu=0.15 G_needed_for_K80=32
constant_effect mu=0.20 G_needed_for_K80=25
constant_effect mu=0.25 G_needed_for_K80=20
constant_effect mu=0.30 G_needed_for_K80=17
POWER reps=10000 seed=20261108 lambda=1 no_missing no_threshold_noise common_attempt_deltas H1=H2=H3; H4=subset
G mu regression H1_first H4_first Holm_H1to3 Holm_all4
20 0.05 0.00 0.0000 0.0000 0.0000 0.0000
20 0.10 0.00 0.0000 0.0000 0.0000 0.0000
20 0.15 0.00 0.0000 0.0001 0.0000 0.0000
20 0.20 0.00 0.0189 0.0363 0.0334 0.0334
20 0.25 0.00 0.5033 0.4641 0.5806 0.5806
20 0.30 0.00 0.9729 0.9179 0.9805 0.9805
20 0.10 0.05 0.0000 0.0000 0.0000 0.0000
20 0.20 0.05 0.0430 0.0747 0.0691 0.0691
28 0.05 0.00 0.0000 0.0000 0.0000 0.0000
28 0.10 0.00 0.0001 0.0004 0.0001 0.0001
28 0.15 0.00 0.1062 0.1396 0.1512 0.1512
28 0.20 0.00 0.8833 0.7806 0.9069 0.9069
28 0.25 0.00 0.9993 0.9945 0.9995 0.9995
28 0.30 0.00 1.0000 1.0000 1.0000 1.0000
28 0.10 0.05 0.0010 0.0045 0.0014 0.0014
28 0.20 0.05 0.7798 0.6614 0.8108 0.8096
ASSERTIONS PASS: roster, arithmetic, Holm examples; synthetic power only
script_sha256=e05fe87cec4071a2ae602b89fa59fb780caef7801ed00b2456aa18d384a271a0
```

## Verification, catches and handoff

- Exact Fraction arithmetic and phase enumeration: PASS. Reproduces
  732.689683/915.862103 h at 900 s and 952.823016/1191.028770 h at 1200 s;
  224 H4 attempts, all six cells present on every assigned date, and the
  corrected exchangeable-score rank tail.
- Proof/diff review: the requested validity defects are repaired. The
  power computation catches a scientific feasibility risk that would
  affect the required claim/roster: 5–15-point effects rarely satisfy Holm
  even under favorable assumptions. It does not measure actual v5 power.
- Markdown scope and whitespace check: `git diff --check`, PASS. The final
  staged diff contains only the review and this report. The named
  coordination files and RULING-DRAFT are unchanged.
- An isolated inline `python3.13 -I -B` check also passed: the preserved
  source/output equal their temporary originals, the SHA-256 matches,
  every quoted simulation/ledger row matches the output, Markdown fences
  are balanced, exactly the two intended paths are staged, and the five
  protected coordination/ruling paths have no diff from HEAD.
- Unit tests, compileall, full suite, quick/sharded suite and production
  analysis: NOT RUN. Two Markdown additions do not warrant code tests;
  the user's no-full-suite rule also applies. No existing test failure
  or native result is claimed.

Next exact step: the lead dispositions P1, freezes a meaningful effect
vector/numerical power target and feasible date/cost plan, then reconciles
both independent seat verdicts. If modest effects are the scientific target,
revise the roster, justified inference assumptions, or prospective claims
now. A favorable .20-effect simulation is not evidence those effects exist.
Finalize the honest-rate bound's target/inversion at G12. Venue/novelty,
physical capacity, capability and all live gates remain unverified.

Lead-only native verification after implementation: execute integrated,
import-gated tiny-synthetic MLX unittest modules one at a time for actual/
public and declared replay, history/cache/RNG, receipt partitioning,
helpers/concurrency/teardown and tails. This docs-only seat adds no such
module and cannot claim a native pass. Actual timing, capacity, capability
and DC-in closure must use the later authorized clean-machine lane.

The review and this report are committed together with a clear docs message.
The local commit ID is reported in the final handoff; there is no push.
