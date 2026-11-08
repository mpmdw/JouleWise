# v5 ruling draft adversarial review — Sol1

Session date: 2026-11-07, as supplied by the environment. The reviewed source
draft and branch names are dated 2026-11-08; no timestamp reconciliation or
external freshness check was attempted.

Completed the requested independent, docs-only Sol1 review of
`docs/align/squeeze/v5-design/RULING-DRAFT.md` at
`18f35ae066270cc44de52830a97f6004d4eee6ec`. The prepared local review branch is
`align/2026-11-08-v5design-ruling-review-sol1`; it began clean at that draft
commit. The review's evidence register pins the six proposal seats, two
judges, AGREEMENT-FINAL, origin/main's items 210/212/213 and PR #703's text.
All were read through local Git objects, with temporary text snapshots under
`/private/tmp/jw-v5-ruling-review-sol1/`.

Verdict: **SIGN_WITH_CHANGES**, with five HIGH findings: the utility-qualified
primary silently narrows R11; S and its external-opportunity subset need an
operational information/assignment contract; 44/pair does not establish
whole-window-loss margin or future-window FPR; the bill/calendar has missing
allocations and unmeasured capacity; and the constituent testing/missingness/
freeze rules need to be made binding. The review conditionally endorses
capability-first and keeping the desktop exploratory. The four-test fixed
sequence is valid in principle, not four unadjusted parallel claims. Local
post-collection scoring is sound with score quarantine and frozen inputs, but
does not establish a causal strength axis or another agent architecture.

Independent arithmetic reproduces 1,980 measured members and
768.000/1,003.167/1,473.500 reserved hours at 900/1,200/1,800 seconds. It also
finds the stale 694 reruns (704 needed for the new calibration target; 824 if
all adaptive queries receive full software reruns), the original 172-member allocation's explicit
reuse of 20 screening benigns, and the lack of a funded third full model screen.
At 16 h/day plus 40 genuinely non-overlapping gate days, the printed totals
need 88.00/102.70/132.09 days; scheduled Dec 7 access leaves 84. The review
explicitly treats this as conditional because some gate days include measured
work. A real resource/critical-path schedule is still required.

Changed files:

- `docs/align/squeeze/v5-design/ruling-review-sol1.md`
- `docs/run_reports/2026-11-07-v5-ruling-review-sol1.md`

Verification:

- `python3.13 -B /private/tmp/jw-v5-ruling-review-sol1/check_arithmetic.py` —
  PASS, integer rosters, nominal ranks, hours/reserves, calendar dates,
  independent-cluster zero-event bounds, local-scoring load and storage only.
  The script imports only stdlib `datetime` and `math`; no repository modules,
  measurement loaders or real data. Output/formulas are quoted in the review.
- Source/line checks used `git show`, `nl`, `sed` and targeted `rg` over local
  repository text and temporary snapshots. A lookup for `tests/align` reported
  that it is absent here; this is documented rather than treating the source
  report's native unittest command as runnable on this tree.
- Unit tests, compileall and full/sharded suites were not run: only two new
  Markdown documents changed, and the binding brief forbids the full suite
  while the blinded job runs. No native MLX, hardware or pipeline was invoked.
- Evidence-register check (`python3.13 -B -`, stdlib text parsing and local Git)
  — PASS: all 12 refs resolve to the printed exact commits, and each cited
  repository document exists at that commit.
- `git diff --cached --check` — PASS. Staged-file scope is exactly the two
  Markdown paths above. Final diff reviewed directly; no scientific
  verification is delegated by this review.

Safety/authority: read AGENTS.md/CLAUDE.md, Mission M0, targeted state/queue and
decision-log context, and orchestration. No active stop card applied. The
explicit user task overrides stale queue pointers; coordination state remains
lead-owned. No edits to RUN_STATE.md, TASK_QUEUE.md, the kernel or state tests;
no tasks registered. No real restricted directory, sealed Block-5 path,
measurement data, other checkout, home-directory tool/skill file, model
download, network, process census or existing analysis-job inspection occurred.
Git's allowed local/shared object access was used only to read source objects.
No push, merge, publication, integration, API call or hardware scheduling.

Process evidence: this is one independent seat's review, with no subagents,
cross-model consult or claim to supply the other Sol review/agreement report.
The lead owns adjudication and the eventual exact-candidate sign-off.

Uncertainty/open rulings: S's deployable access, the 336-attempt subset and
optimizer weights, the exact missingness/test contract, actual usable capacity,
which gate days overlap, Flash/NVMe qualification and API/runtime availability
remain unresolved. Source model/throughput/literature claims were not verified
online or on hardware. Native tiny-model and full configuration qualifications
must run on the lead's integrated MLX tree and clean machine-state lane, as
specified in the review; they are not completed here.

Next exact step: lead dispositions F1–F5/M1–M2, reconciles the independent Sol2
review and writes the required agreement report on a revised ruling before
signature. No question blocks completion of this read-only design assessment.
The requested two-document change is committed locally with a review-specific
message; the final handoff supplies its commit hash. Nothing is pushed.
