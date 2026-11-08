# Independent ALIGN squeeze review, Sol seat 1

Date: 2026-11-07. Status: **DRAFT / UNADJUDICATED / LOCAL_ONLY**. This is a desk review, not registration, collection, native validation or a publication claim.

## Scope and intake

- User-selected task: act as three hostile but fair reviewers of successful ALIGN v4 plus an adaptive red team; produce the seat's independent critique, prioritized pre-collection actions, costs, gates, confidence and venue fit.
- Tree: this clone, `/Users/edr/code/CapstoneProject/jw-wt/sol-sol-reviewer2-seat1`.
- Branch already existed and was clean at intake: `align/2026-11-07-sol-reviewer2-seat1`, starting at `be3cc8b680cde290299aeb8d198de73993fe38b2`.
- M0: read AGENTS/CLAUDE, generated stop card and machine lanes, current status/workspace/next-work context, Current Queue and Do-Not-Do-Yet, playbook M0, orchestration, source map, relevant analysis/claim contracts and targeted D-161/D-174/D-070 authority. Generated stop card was NONE. The explicit user desk brief selected this work instead of the older generated queue head.
- The user's prohibition on coordination writes overrides normal bookkeeping. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, `tests/test_gen_state.py` and advisor-facing state remain untouched; no task was registered.
- Read the requested agenda/research page and locally available V4, literature, W1-prearm and research-program Git objects. Full pins are in the review. No other squeeze seat's branch was read; no agents or consult peers were launched.
- The no-network rule overrides the requested fetch. No fetch, browsing, model download, push or external integration occurred. Absolute data pointers were treated as text. No real measurement data or sealed outcomes were read, and no pipeline, quiet-Mac collection or model execution was started.

## Deliverable and principal findings

`docs/align/squeeze/sol/reviewer2-seat1.md` contains three reviewer perspectives, twelve prioritized actions with proposed owners/lanes/costs/R1-W1-D timing, an adaptive attack matrix, statistical planning arithmetic, novelty comparisons, discussion-only limits, venue fit and a concrete lead handoff.

The principal findings are:

1. Complementary observations do not prove an unavoidable squeeze. Test successful same-token sabotage, fabricated plausible counts, energy matching, mixed hiding/padding and boundary relocation.
2. Resolve the external-DC versus same-host GPU-rail claim and qualify the actual metered power/acquisition path. The research page and D-series agenda describe different readiness states.
3. Freeze a joint alarm budget, success/usefulness denominator and independent final evaluation. LOTO calibration versus full-fit scoring does not automatically inherit a sample-maximum FPR guarantee.
4. Price precision honestly. The default D roster cannot yield a tight evasion bound in a few windows merely because its outcomes are favorable. Cohort sizes in the review are illustrative arithmetic, not new requirements.
5. One local production model, two task pairs and one unit support a bounded demonstration. Broad model, domain and datacenter claims need additional evidence or narrower wording.

The review's recommendations are not installed rulings. The lead owns scientific adjudication and native/hardware gates. Earlier audit findings and literature checks are attributed to their source commits, not claimed as fresh execution by this seat.

## Verification

No unittest modules or compileall were run: only two Markdown documents changed, with no implementation, configuration, test or measured artifact changes. The full suite was explicitly prohibited and unnecessary for this desk deliverable. No test workers were launched.

| Command/check | Result |
|---|---|
| `git status --short --branch` at intake | Clean, correct task branch. |
| Inline `python3.13 -B` citation/arithmetic/document checks | PASS: 55 pinned citations across 11 commit/path pairs; all ranges exist; FPR/rank/sample arithmetic and A1–A12/deadline labels pass. Under one second. |
| `git diff --check` and `git diff --cached --check` | PASS, exit 0. |
| `python3.13 -B scripts/fixture_orphan_census.py --fail-on-orphans` | Exit 2: `PermissionError: [Errno 1] Operation not permitted: 'ps'`. Observation unavailable; not a clean census. No escalation or process signaling attempted. |
| Final diff/scope review | Only the requested review and this run report; no coordination/code/data changes. |

The first citation check caught one out-of-range claims-ladder citation. It was corrected to the actual ladder table before the passing rerun and review commit. Arithmetic checks independently confirmed: rank 38 at m=39/alpha=.05; maximum marginal 2.5%; 90% maximum-tail upper bounds 10.87%/5.73% at m=20/39; all-three detection lower bound 36.8%; all-29 lower bound above 90%; zero-in-59 upper bound below 5% at one-sided 95% confidence. Their iid/exchangeability assumptions are explicit in the draft.

The compact citation/arithmetic portion can be reproduced without data access:

```bash
python3.13 -B - <<'PY'
from pathlib import Path
import math
import re
import subprocess
s = Path('docs/align/squeeze/sol/reviewer2-seat1.md').read_text()
refs = re.findall(r'`([0-9a-f]{9,40}):([^`\s]+?):(\d+)(?:-(\d+))?`', s)
blobs = {}
for rev, path, lo, hi in refs:
    assert not path.startswith('/') and 'restricted' not in Path(path).parts
    if (rev, path) not in blobs:
        blobs[rev, path] = subprocess.check_output(
            ['git', 'show', f'{rev}:{path}'], text=True).splitlines()
    assert 1 <= int(lo) <= int(hi or lo) <= len(blobs[rev, path])
assert len(refs) == 55 and len(blobs) == 11
assert math.ceil(.95 * 40) == 38
assert abs(1 / 40 - .025) < 1e-14
assert round(100 * (1 - .1**(1/20)), 2) == 10.87
assert round(100 * (1 - .1**(1/39)), 2) == 5.73
assert round(100 * .05**(1/3), 1) == 36.8
assert .05**(1/29) > .9
assert 1 - .05**(1/59) < .05
assert math.ceil(math.log(.05) / math.log(.95)) == 59
for i in range(1, 13):
    assert f'A{i} |' in s
assert s.count('UNVERIFIED offline') >= 6
print('PASS: pinned citations, planning arithmetic, action rows and deadline caveats')
PY
```

These checks validate document references and arithmetic; they do not validate the physical model, attack competence, claimed detector coverage or hardware. No MLX code/tests changed, so there is no new native MLX test obligation from this patch. The lead's existing native R0/R1/W1 and registration checks remain outstanding wherever their own authority says so.

## Commits, uncertainty and next exact step

- Review commit: `2e39bc42cf9901339c1578f9f3adb5758f7fb643` — `docs: draft independent ALIGN squeeze reviewer seat 1`.
- This report is a separate local closeout commit on the same branch. Neither commit is pushed; local-only custody is intentional under the brief.
- Official 2027/2028 venue deadlines and current remote integration status are **unverified**. The report supplies official-site pointers and clearly labeled internal planning cuts; these are not CFP dates. Literature priority, venue fit and engineering costs retain stated uncertainty.
- Fixture census remains unavailable because of sandbox process-observation permissions. No fixture, measurement or analysis process was launched by this seat.
- No binding decision-log, risk-register or coordination-state changes were made. No additional work is required to deliver the independent draft; its proposed experiments and rulings remain the lead's decisions.

**Next exact step:** the integration lead reads the review at the pinned commit, dispositions A1–A12, resolves the primary metering/trust boundary and score/calibration/joint-FPR construction, and verifies venue calendars through an authorized networked session before choosing a submission route. No measurement step is authorized from this agent session.
