# Squeeze agreement synthesis — 2026-11-07

**DESK DRAFT completed for lead review. No registration, installed ruling, collection, or publication.**

Deliverable: [AGREEMENT.md](../align/squeeze/AGREEMENT.md).
Branch: `align/2026-11-07-squeeze-agreement`, already provisioned and clean at
intake. Starting commit: `32ba4928573ce1981f8a953ab700f00dda9e94d1`.
The local documentation commit containing this report is identified in the
session handoff; no push or merge is authorized or performed.

## Work and findings

Read the substantive documents on all **14 requested comparison branches**
from local remote-tracking refs. **Missing branches: none.** The agreement
contains a source register with immutable full commit IDs and document paths
for those branches and supporting protocol, residual, literature, W1-prearm
and research-program evidence (21 entries total). Relevant Fable/Opus appendix
passages were used to distinguish seat positions from the synthesizers' own
recommendations. No fresh agent or model consult was launched.

The report includes:

- Per-track finding/action tables for registration (16 rows), squeeze design
  (12), and hostile-review readiness (10), with seat attribution, k/4 support,
  conflicts, evidence and recommended dispositions. Syntheses are not extra
  votes; the additional reviewer2 branch is one session, not three reviewers.
- Separate dispositions for the analysis and kit executing reviews, retaining
  their reported fixes, skips and native limitations without calling them
  current-branch test results.
- One merged prioritized v4/squeeze action list, with cross-family agreement
  weighted highly and direct source evidence able to elevate a singleton.
- A comparison of the two Sol preregistration drafts, their different
  threats, feedback budgets, endpoints, sample totals, PC gates and reserves,
  plus a nine-part merged recommended addendum outline.
- Ed's corrections applied explicitly: absent/bypassed KM003C physical-path
  claims **refuted**; scoped sandboxed on-host agent permitted; frontier API
  monitor primary/off-box and local secondary; NeurIPS 2027 full-squeeze target
  with an earlier v4/limits route allowed.

The most important agreement is that v4 readiness and the adaptive squeeze are
different evidential gates. The biggest unresolved conflicts are the public-log
trust contract, readable monitor view, independent calibration construction,
powered semantic endpoint and affordable number of independent final trials.
The physical meter is inline; capture/custody and a qualified DC score still
need their own evidence. No native readiness conclusion follows from this report.

## Verification performed here

All execution was bounded desk work with Python 3.13 and local Git. No unit
suite was needed for this documentation-only change, and the full suite was
expressly prohibited. The running blinded job was not inspected or touched.

1. `python3.13 -B -` — AST-isolated probe of the pinned
   `e901eb2a480d51377a494be9d797733dfcd0220b:joulewise/align/apple/v4_estimands.py`
   source. Extracted only imports, `H_STAR_GRID`, `subturn_h_star`, `_quantile`,
   `_crossing`, and `benign_carrier_curve`; imported no repository data loader.
   **PASS:** reproduced Sol-2's finding that equality reaches H* and that
   shifting every carrier at a dose by +128 leaves its detection fraction at
   `1/21`. This confirms the pinned code behavior, not any real-data effect.
2. The same stdlib-only command checked exact rational ranks at m=20/21/39/40,
   sample-maximum and split-rank tails, realized-tail and zero-event bounds,
   preregistration totals and zero-survivor probabilities. **PASS:** rank 38
   at m=39/alpha=.05 gives .05, maximum gives .025; maximum realized-tail
   90% bound is .0573315; zero/59 95% upper is .0495076. P1=1,398 members,
   P2=1,118 core plus 144 optional; twelve-cell n=60 bounds are .0977796
   (P1's two-sided allocation) and .0872963 (P2's one-sided allocation).
3. `python3.13 -B -` — documentation/source integrity check. **PASS:** all
   14 branch refs represented; all 21 pinned blobs equal the reviewed text;
   local ref tips still equal the recorded commits; Markdown table widths and
   four-seat counts consistent; no source-register placeholder remains.
4. `git diff --check` and final staged whitespace/scope checks: **PASS**.
   Only the two documentation files below are included in the local commit.

Source-inspection command form: `git show <full-sha>:<repository-path>`.
No `git fetch origin` was attempted: the explicit no-network rule overrides
the fetch instruction. Remote freshness is therefore **unknown**. Source
reports' external quotations and venue dates were not independently rechecked.

## Files and protected scope

- Added `docs/align/squeeze/AGREEMENT.md`.
- Added `docs/run_reports/2026-11-07-squeeze-agreement.md` (this report).

No code, tests, registration, raw evidence, process state or advisor status was
changed. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` and
`tests/test_gen_state.py` remain unchanged. No kernel tasks were registered.
No path outside the allowed clone was followed for measurement data, and no
real restricted directory, model weights, measurement pipeline, network,
API, hardware sampler or process census was accessed. Only explicitly allowed
repository Git objects and this session's synthetic temporary files were read.

## Handoff and open questions

No further input is required to complete this desk deliverable. The report's
adjudications are recommendations, not scientific rulings installed by this
session. The lead must choose the logging permissions, monitor identity/view,
fusion rule, semantic margins, independent unit, capacity/caps, reserves and
U3/U5/U6/contrast/duty dispositions before a registration candidate can pass.

Next exact step: disposition the merged action list and request one reconciled,
costed preregistration candidate with synthetic operating-characteristic checks.
The compact composed Claude design and the larger Sol designs do not support
the same precision claim; no averaged budget is recommended.

Native work remains pending outside this sandbox: KR's
`python3.13 -B -m unittest tests.align.test_squeeze_native` with MLX/Metal and
tiny synthetic models, actual Apple/harness/cache/interruption integration,
and trusted external-meter/battery/clock/work-witness qualification. AR asks
for its five numerical modules with NumPy on Python 3.11 and 3.13. Those are
future lead checks on the integrated tooling tree, not tests of this docs branch
or permission to run during the current blinded job.
