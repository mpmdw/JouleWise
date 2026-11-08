# Sol cross-review of Claude v4 registration — 2026-11-07

Desk-only independent review on `align/2026-11-07-sol-review-claude-v4-registration`, starting at `eea648b09933bce93d49cef3a8e7da11ab88e18b`. The requested branch was already checked out and clean. User authorized a local commit, no push. Direct task authority supersedes stale queue selection; intake found no active stop card. Read AGENTS/CLAUDE, Mission M0, orchestration, targeted state/queue and D-050/D-139 authority. No coordination-state edits or kernel registration were performed.

## Deliverable and findings

Review: `docs/align/squeeze/sol/review-of-claude-v4-registration.md`.

Conditional endorsement: the registration repair program improves v4, but must not be adopted unchanged. Concrete source findings include the wrong battery-current field, a same-dose moving threshold in the benign-carrier helper, inconsistent rank/tie/fitting conventions, insufficient replay-defense evidence, omitted latest owner decisions, incomplete joint yield arithmetic, and missing contrast/sentinel/gate cases. The review inventories all 26 prioritized actions, all 38 gate checklist items, all 28 reconciled subsections, appendix exceptions and nine external-source claims. Repeated claims share dispositions; mixed factual/proposal claims are separated in the inventory.

Only two documentation files changed: the review and this record. No implementation, generated configuration, measurement evidence, protected coordination state or tests changed. No new agents or Claude consults were launched; independent review remained with the assigned Sol seat.

## Verification performed

* Read pinned protocol and energy-residual spec with `git show e901eb2a4:<path>`, R10 code/rulings at `d600baba0`, and the local literature, pre-arm, budget and research-program audit branches. All reads were explicit repository files or Git objects. No fetch/network access. Shared Git object reads were within the user's exception.
* Ran `python3.13 -B` source-level synthetic probes below. They finished in under one second; no unittest suite, pipeline, model, native backend or hardware process was invoked. Results are synthetic mathematical/source evidence only.
* Documentation citation check and `git diff --check` are recorded at closeout below. No full suite, compileall or native tests were needed for a docs-only change; full suites are expressly forbidden by this task. Test runtime was zero (the short Python source probes are not unittest runs).

Reproducible source/mathematical probe, run from the clone:

```sh
python3.13 -B - <<'PY'
import ast, math, random, subprocess
from collections import defaultdict

def survive(n, k, p):
    return sum(math.comb(n, i)*p**i*(1-p)**(n-i) for i in range(k, n+1))

for w in (6, 7, 8):
    for excluded in (.05, .10, .14):
        b = survive(7*w, 39, 1-excluded)
        s = survive(w, 6, 1-excluded)
        print('yield', w, excluded, round(b, 6), round((b*s)**2, 6))

for m in (39, 40, 78, 79):
    k = math.ceil(.975*(m+1))
    print('rank', m, k, 'marginal_bound', (m+1-k)/(m+1))
assert math.ceil(.975*39) > 38  # 39 carriers leave only 38 other carriers
print('contrast_deadman_rounded_intercept', (1750-516.58)/1.13544)
print('normal_tail_known_scale_k3', math.erfc(3/math.sqrt(2)))

source = subprocess.check_output([
    'git', 'show', 'd600baba0:joulewise/align/apple/v4_estimands.py'], text=True)
selected = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)
            and n.name in ('_quantile', '_crossing', 'benign_carrier_curve')]
namespace = dict(math=math, random=random, defaultdict=defaultdict)
exec(compile(ast.Module(body=selected, type_ignores=[]),
             'git:d600baba0:v4_estimands.py', 'exec'), namespace)
rows = [dict(pair='spam', window=str(i//7), carrier=str(i), h=h, score=i+h/10)
        for h in (0, 128, 256, 512, 1024, 2048) for i in range(39)]
result = namespace['benign_carrier_curve'](rows, bootstrap_replicates=0)['pairs']['spam']
assert all(abs(rate-1/39) < 1e-12 for _, rate in result['curve'])
assert result['H50'] is None and result['H90'] is None
print('same_H_reference', result)
base = list(range(39))
for h in (0, 128, 256, 512, 1024, 2048):
    detections = []
    for i in range(39):
        others = [value for j, value in enumerate(base) if j != i]
        rank = math.ceil(.95*(len(others)+1))
        detections.append(i+h/10 > others[rank-1])
    rate = sum(detections)/39
    if h >= 512:
        assert rate == 1
    print('untampered_H0_reference', h, rate)
PY
```

Observed: one-pair benign probabilities at six windows were .843107/.383646/.142233; seven windows .999976/.991995/.926871. Joint two-pair benign+sabotage completion at seven windows was .913164/.711490/.476053, and at eight .988457/.925258/.829070. Rank .975 is m through m=78 but rank 78 at m=79. Rounded-intercept contrast deadman 1086.292539 s; known-scale normal k=3 tail .002699796. Carrier helper stayed at 1/39 through H=2048; untouched-H0 reference reached 1 at H=512. All probe assertions passed.

## Native verification owed to the lead

No MLX import/device test was attempted; this sandbox cannot execute MLX. On the eventual corrected implementation, the lead must run applicable focused modules one at a time, including `tests.align.test_v4_estimands`, `tests.align.test_v4_kit`, `tests.align.test_w1_kit_r10`, `tests.align.test_protocol_v4_doc` and the focused Ruling76 regression, plus the new battery/contrast/registration oracle modules actually added by the builder. Existing tests do not replace the missing positive-signal carrier oracle.

Separately, on the production pinned MLX stack with no conflicting agent/measurement load: native full-token WP19 X/Y identity including warmup/cache/reseed behavior; final-policy D replay and three-turn/capability checks; MBP battery/OBC/top-up evidence; KM003C startup, clock alignment, gross-span integration, battery assist, coverage and custody; mount-event qualification over the full window; and the actual physical positive controls on the claimed configuration. These are pending gates, not results of this desk review. No new measurements are requested from this session and the existing blinded job was untouched.

## Limits, questions and next step

External paper full texts, previous seats' invocation receipts, the claimed Air OBC probe and live R0/R1/read chronology remain unverified. No forbidden path was opened/listed/searched. Data-path strings in source documents were treated only as text. No weights were downloaded. Source snapshots were copied only into `/private/tmp/jwsol-review-v4-registration` for line-oriented reading.

Lead decisions remain: the precise fit/calibration/rank/tie policy; honest handling of incomplete contrast/sentinel evidence; bounded replay/log-forgery threat model; final API monitor/budget; U3 predictive assumptions; full calibration/test/adversary time reservation. This review does not choose those scientific policies or modify registrations. Next: disposition F1-F9, amend the builder brief, implement bounded fixes and execute the scoped independent gates.

Closeout: the exact recorded synthetic probe was executed successfully, including all assertions. A `python3.13 -B` documentation checker resolved **98 commit:path:line citations across 25 source snapshots**, checked complete action coverage 1–26 and gate coverage 1–38, and checked balanced code fences. `git diff --check` passed. Final staging/diff review is limited to the two new documentation files; protected coordination state is unchanged.

Local commit subject: `docs(align): independently review Claude v4 registration`. Resolve its immutable ID with `git log -1 --format=%H -- docs/align/squeeze/sol/review-of-claude-v4-registration.md`; the handoff response records the ID after committing. No push is authorized or performed.
