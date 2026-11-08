# v5-ruling-delta3 — Sol1 review run

Date: 2026-11-07 (session date; task/draft label 2026-11-08).
Branch: `align/2026-11-08-v5design-ruling-delta3-sol1`, provisioned clean at
`b606d9788cd0cb25e0c85903ba7c75116edad894` when work began.

Reviewed `7d2e43464..b606d9788`: one design Markdown file, 273 additions /
187 deletions. Both prior delta reports were read from locally cached refs
at `8c2c6c1ce` (DS1) and `94acc5b81` (DS2). Authority/intake checks included
AGENTS/CLAUDE, M0, no active stop card, the queue fences, orchestration, AP,
D-062 and the pinned R11/R12 object at `319f6a51d`. The explicit user brief
selected this docs review and prohibited coordination-state edits; no kernel
task was registered and RUN_STATE/TASK_QUEUE were preserved.

Delivered `docs/align/squeeze/v5-design/ruling-delta3-review-sol1.md` with
**SIGN_WITH_CHANGES**, a quoted disposition for all thirteen numbered findings
of both round-2 seats and their carried prose requirements. Two HIGH issues
remain: the marginal/conditional-null mismatch in the betting fallback, and
the 1.2× simulated-size gate's inability to certify nominal 5% Holm control.
Two MED repairs concern H4's per-date support and CAP units/yield accounting.
Fairness, adverse point bounds, degenerate calibration and quarantine are
repaired at contract level. Main ledger/cuts reproduce; two LOW notes cover
additional cap local scoring and the general rank-tail formula.

Changed repository paths only:

- `docs/align/squeeze/v5-design/ruling-delta3-review-sol1.md`
- `docs/run_reports/2026-11-07-v5-ruling-delta3-sol1.md`

Verification:

- `python3.13 -B /private/tmp/jw-v5-delta3-sol1-check.py` — PASS. Stdlib-only
  arithmetic, 27 exhaustive binary partial-observation bounds, compliant H4
  counterexample and feasible repair, analytic null/capacity examples. No
  project/data imports, simulation of real outcomes or native execution.
- Main recomputation: 711.278571 / 889.098214 base/reserved h at 900 s;
  cap-inclusive 732.078571 / 915.098214; 1,200-s cap reserved 1,190.264881 h.
  Script output and formulae are quoted in the review. This check caught the
  permitted H4 roster with only 19 nonempty windows, .058663449 all-null Holm
  error allowed by 1.2× size, and the CAP hours/hours units/yield mismatch.
- `git diff --check` and staged whitespace/path review — PASS before commit.
- No unit, full, sharded, compileall or MLX run: Markdown-only scope, with
  arithmetic checked directly; the full suite is explicitly prohibited.

No subagents/consults, network, model weights, measurement data, real
restricted directory, external user-tree read, analysis pipeline, job/process
inspection, live/native probes or coordination writes were used. Git object
reads used the allowed repository store. No native/hardware or source-freshness
claim is made. MLX tiny-synthetic checks and later clean-machine gates are
listed for the lead in the review; no code/test module was created here.

Local commit: this report and the review are committed together with message
`docs(align v5): review ruling revision 3 from Sol1`. Resolve the exact commit
with `git log -1` on the named branch. No push was requested or performed.
Hooks are disabled for the local commit to avoid unrequested suite/network
activity in this docs-only, no-network session.

Next exact step: the lead adjudicates R1–R4 and L1–L2, edits the draft and §9,
then obtains the companion independent review of that exact candidate before
signature. The experiment is not yet qualified or registered. The dependence
model, native receipt coverage, measured capacity and venue/novelty remain
unverified. The other Sol seat and final authority remain outside this seat.
