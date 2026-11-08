# Independent Sol squeeze-design seat 1 — desk handoff

Date: 2026-11-07. Branch: `align/2026-11-07-sol-squeeze-design-seat1`.
Starting head: `be3cc8b680cde290299aeb8d198de73993fe38b2`.

## Work and findings

Delivered `docs/align/squeeze/sol/squeeze-design-seat1.md`, a draft for lead
review. It covers non-adaptive and joint adaptive attackers, log padding,
compute smoothing, tools, timing shifts, genuine compute/sham controls,
same-episode SHADE scoring and blinded score release, conformal operating
points, OR/AND comparisons, an escape frontier, explicit power assumptions,
and R1/W1/D order and cost.

The main design concern is shared semantic blindness: accounting for logged
work does not make its intent detectable by a transcript monitor. The cheapest
next experiment challenges that premise before further calibration spending.
The recommended confirmation is scoped to a frozen, budgeted adaptive
portfolio. It does not certify every adversary family. The strong planning
case is approximately 45 D-like long windows plus existing R1/W1; the draft
shows assumptions and a smaller, lower-power alternative.

Changed files only:

- `docs/align/squeeze/sol/squeeze-design-seat1.md`
- `docs/run_reports/2026-11-07-sol-squeeze-design-seat1.md` (this handoff)

No coordination state, kernel task, code, tests, registration, protocol,
measurement evidence, or external application was changed. The user's explicit
desk instruction overrides normal coordination-state update requirements.
No decision or registration is installed by this document.

## Inputs and boundaries

Read repository AGENTS/CLAUDE conventions, M0, orchestration, targeted
decision-log authority, the restart stop-card/status/workspace sections and
current queue/do-not-do list. No active stop card was present. The requested
branch already existed and was clean at intake; no branch replacement or
worktree manipulation was needed.

Read the agenda/research-map HTML at the starting head and the specifically
requested local Git objects:

- v4 protocol and residual documentation at `e901eb2a480d51377a494be9d797733dfcd0220b`;
- literature synthesis at `16e1db6230a80a605d084f0f9f61431d541b793f`;
- W1 pre-arm synthesis at `53a2305982a551ba5285e50bd0177726b5f138e7`;
- research-program synthesis at `7f74dd2a97e5fcf078652deef2fb291929dc4524`.

Also inspected the v4 lane's SHADE monitor, rendering/port contract, upstream
pin, pipeline and hint-monitor distinction. The later local Q4/Q6/R10 rulings
were used to avoid repeating superseded audit questions.

**No fetch:** the brief requested a fetch and also imposed no network; no
network took precedence. Ref freshness beyond these locally present commits
is unverified. No other squeeze-design seat branch was read, no subagent or
consult was invoked, and no outside-home skill/cache was opened. Textual
absolute paths in repository documents were not followed. No real restricted
directory, sealed outcome, measurement artifact, model weight, analysis job,
meter, power setting, process state or measurement pipeline was accessed.

## Verification and reproducibility

This is documentation-only work. No full suite, targeted unittest module,
compileall, native MLX test or live measurement was needed or run. No fixture
or numerical calculation is represented as hardware evidence.

- `git status --short --branch`: clean requested branch at intake; final
  staging restricted to the two named documents.
- `git diff --check` / `git diff --cached --check`: whitespace checks.
- In-clone Python/subprocess citation validator: **23 explicit
  commit:path:line references across 10 source objects resolved**, and all
  cited line ranges were within the named files. Source-pin table was also
  checked separately before commit. This checks identity/ranges, not the
  truth of an inherited literature claim.
- Stdlib binomial-tail calculations: executed offline, under one second per
  calculation batch. No simulation package or scientific data was used.

The exact power calculation used this algorithm (independent-episode planning
only; document separately explains clustering and success-denominator limits):

```python
from math import comb

def mass(n, p):
    return [comb(n, k) * p**k * (1-p)**(n-k) for k in range(n+1)]

def critical(n, p0, alpha):
    tail, result = 0.0, n+1
    for k in range(n, -1, -1):
        tail += comb(n, k) * p0**k * (1-p0)**(n-k)
        if tail <= alpha + 1e-14:
            result = k
    return result

for n in (120, 148, 200, 300):
    k = critical(n, .8, .025)
    catch_power = sum(mass(n, .9)[k:])
    paired = []
    for b, c in ((.20, .05), (.18, .08)):
        power = 0.0
        for d, probability in enumerate(mass(n, b+c)):
            cut = critical(d, .5, .0125)
            power += probability * sum(mass(d, b/(b+c))[cut:])
        paired.append(power)
    print(n, k, catch_power, paired)
```

Rounded results `(n, critical, catch, paired gain .15, paired gain .10)`:

```text
120 105 .8560 .8529 .4103
148 129 .8978 .9284 .5118
200 172 .9729 .9826 .6727
300 254 .9986 .9992 .8676
```

Additional checks: `1 - .05**(1/60) = .048703`; simultaneous per-pair zero-alarm
bound with 72 observations is `1 - .025**(1/72) < .05`; n=200, alpha=.05/12
catch critical count is 175 and power at p=.9 is .8995. Window reservations:
`45 * 59520 / 3600 = 744`, `35 * 59520 / 3600 = 578.67` hours. These are
derived planning numbers, not measurements.

## Open questions and exact handoff

The lead must choose the affordable claim/sample size, final monitor artifact,
attacker privileges/query budget, DC/battery qualification, the prospective
F/C/T estimator change, clustered inference, and missing/excluded-case policy.
The proposed confidence bars and sample sizes are not existing council rulings.
Monitor availability, native runtime behavior, ICC, attack success and any
realistic squeeze gain remain unverified. The six-window calibration budget
assumes episode exchangeability after protocol control. A distinct option for
arbitrary within-window dependence uses 39 independent calibration windows
and a window-level maximum/alarm estimand; the draft explicitly prices the
additional windows and does not claim that stronger guarantee for six nights.

**Next exact step:** lead reviews P0 and the development camouflage challenge,
then freezes the scope and budget in a prospective addendum. Existing R1
proceeds under its own authority; W1 and later D require their existing gates.
If injector/monitor code is subsequently implemented, the lead must run its
focused native MLX/runtime tests and the real meter/sham/thermal validation in
a clean session outside this sandbox. This desk run introduced no MLX code
and therefore has no newly implemented native test module to name.

Local commit contains only the two documents above; no push or merge. The
commit hash is supplied in the final handoff, avoiding a self-referential
commit entry inside this report.
