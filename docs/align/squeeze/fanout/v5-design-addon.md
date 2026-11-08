# v5-design-addon — Sol-2 handoff

Brief: 2026-11-08; environment date: 2026-11-07. Independent seat, no other
seats or branches consulted. Branch `align/2026-11-08-v5design-addon-sol2`,
baseline `32ba4928573ce1981f8a953ab700f00dda9e94d1`.

Built [the ADD-ON design](../v5-design/addon-sol2.md): frozen v4 cell, two task
pairs, four attacker-policy arms, proposed A0–A13 coverage checklist, frontier
API monitor, whole-member DC-in, runtime-external controls, per-attempt escape
estimands, power/FPR arithmetic, blinding, cost and submission calendar.
Implementation commit: `5a00e7290` (`docs(align): design bounded add-on v5 squeeze
evaluation`). This handoff is committed separately on the same branch.

Key findings:

- T1–T3 must be batches: 32 windows, 192 primary attempts, 32 policy comparators,
  64 honest audits. Three literal test windows are insufficient.
- Seven compatible calibration windows supply 49 scheduled benign scores/pair.
  Reuse saves 113.28 reserved hours. Full base plan is 754.33 h; incremental
  after v4 calibration/qualification is 620.65 h, or 775.81 h with 25% reserve.
  Native reruns provisionally add 120 h before contingency. Test phase needs
  three near-16 h nights/week; 14 h access needs 76 test windows; 12 h cannot
  fit even the proposed support/audit skeleton at the transferred envelope.
- Max-score FPR requires exchangeability. Per-session LOO validity, conditional
  FPR uncertainty and within-window dependence cannot be wished away. The
  beta-binomial inference is explicitly model-based; rho <= .10 is an
  assumption, not established hardware evidence.
- Main-track-strength evidence forecast: subjective 20% (10–35% plausible
  range), dominated by capability and real complementarity beyond software
  replay/time. Includes a December 15 stop/go decision and cheap gate sequence.
- Amendment 1's calibration formula says `16 × 1,800` but its roster and
  35,531.27 s result require **18**. Correct maximum remains 58,260 s. Source
  documents and the R1 lane were preserved.

Verification, synthetic/standard-library only:

- `python3.13 -B /private/tmp/addon_sol2_design_check.py`: first run failed on
  the absent proposal (document acceptance baseline); final run **5 tests
  passed**, about 0.03 s. Checks parse the planning JSON, reconcile fitting/
  audit/attack slots, window caps and bills, exact binomial power, max-rank
  caveats, fourteen coverage rows, and relative source links. This temporary
  checker is local scratch, not a committed production regression test.
- Inline `python3.13 -B` exact beta-binomial convolution: homogeneous rho=0,
  .10, .25 gives critical escape counts 3, 2, 1 and power at q=.01 of .8722,
  .6948, .5330. These examples do not validate the future nuisance-profile
  implementation.
- `git diff --check` and staged diff checks passed; final changed-path check
  covers only the proposal and this report. No production code changed, so
  no production test module, compileall or full suite was appropriate.

Assumed rulings: KM003C in every power path and authority for small effects;
amended D-139 A1 permits the sandboxed agent adversary; API frontier monitor
primary/off-box; no v4 monitor scores before registration; m >= 39 per pair,
max thresholds and separate tests; real runtime-external controls; escape per
attempt primary. Explicit brief forbids coordination-state edits, overriding
normal M0 closeout writes. RUN_STATE, TASK_QUEUE, kernel and tests/test_gen_state
were not edited. No network, measurement pipeline, sealed data, model weights,
quiet-machine job, model download or external integration was accessed/run.

Open questions before an executable registration: exact frozen R1/R10 cell;
canonical A0–A13 crosswalk (the table is only this seat's proposal); SHADE scorer
digests; E*/DC-in fit and integration contract; LOO rank validity; defensible
dependence model; available API snapshot/cost cap; actual native replay bill;
and sufficiently long booked nights. No outcome or native validation is claimed.

Lead must run outside this sandbox, after the blinded job is clear: native MLX
checkpoint/restore and held-token identity tests for the admitted qwen3_5 path;
real XML/history round-trip with no closed-reasoning prefix rewrites; final-turn
admission/overshoot and deadman sizing with G0/G1/holds; full-model capability;
and side-generation/subprocess controls proving whole-member KM003C coverage,
trusted tool visibility and correct quiet-guard treatment. MLX has no Metal or
CPU fallback here; no MLX code/test changes were made. Do not infer these gates
from the synthetic arithmetic checks.

Next exact step: lead audits the final cell, score interfaces and taxonomy,
then conducts the budget/capability retirement gate in a lead-controlled quiet
session and secures the calendar before committing to the full add-on campaign.
