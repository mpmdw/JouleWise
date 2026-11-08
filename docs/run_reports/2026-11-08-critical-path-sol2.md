# Critical-path lookahead — Sol-2 handoff

2026-11-08. Branch `perf/2026-11-08-critical-path-sol2`, initially clean at
`origin/main` `e7203f0ad`. Documentation only; no coordination-state changes,
network, measurement-directory access, weights, hardware commands, production
pipeline or full test suite.

Deliverable: [critical-path report](../perf/2026-11-08-critical-path-sol2.md).
It inventories R1 through v4 release, the first v5 development gates, per-step
prerequisites and implementation status, a conditional back-to-back calendar,
owners/readiness deadlines, ranked idle exposure, refusal risks and physical waits.
Source references are pinned local Git objects, with branch/file/line citations.

Findings most likely to idle the MBP:

* R1 arm build/review is announced in RUN_STATE 218–219 but its branch is not
  available in this clone. Driver/runtime existence does not prove arm readiness.
* V4 U3 validation unconditionally refuses. The battery window consequence
  remains unset, and the full desk treats that unset verdict as failing. Neither
  is solved by filling registration JSON.
* The kit generates W1 only. D/C/T role manifests, generated launch kits, the
  final calibrated scorer and cumulative desk/triage producer are incomplete.
* Permanent SSD hooks are provisional; shared-lease integration, final event
  policy and native qualification remain. Draft SSD-P1 requires full R1-S.
* Full raw export/portable desk, per-window triage and independent v4 recompute/
  release need explicit routes. Existing engineering branches help but carry
  synthetic evidence, not production timing guarantees.

Two nomenclature/authority issues are left for the lead: mapping D1–D3 into the
fixed C1–C8 series versus explicitly funding separate development/fit windows;
and M item 216's from-six pending-eligibility fence versus V's updated from-eight
predicate. Scorer/F/C/T/test shape, U3/B/U5, SSD configuration and physical
receipts also remain prospective decisions or unavailable native evidence.

Verification, run sequentially:

* `python3 -B` repository-only citation/static-witness here-document: initially
  **97 distinct citations across 37 source files**, all files and line numbers
  valid. AST checks confirmed unconditional U3 raise and battery `bar_pass=None`.
  Six source-isolated pure `calibration_stop` cases passed: seven continue,
  eight complete, provisional six continue, provisional eight hold, insufficient
  counts, and two zero-capture escalation. No repository imports or data reads.
* `python3 -B` independent datetime arithmetic: reproduced each report calendar
  row from 16/19 h R1, 26,927/40,527-s spans, 30/45-min turnaround and the initial
  98/103-min full desk. Three extra cycles = 35.2725/36.0225 h; eight C captures
  = 90.06 h. These are conditional schedule arithmetic, not measured throughput.
* Markdown table column check caught an unescaped absolute-current expression;
  corrected it. Final `python3 -B` citation/table/link check: **99 distinct
  branch/file/line citations across 39 source files PASS**; both Markdown table
  structures PASS; relative deliverable link and regular-file checks PASS.
* `git diff --cached --check`: PASS on the two staged documentation additions.
* No unittest modules or compileall run: no code changed, and the machine is
  reserved for a blinded job. Source-isolated cadence checks are synthetic only.

Native checks the lead must run outside the sandbox are listed in the report:
opt-in tiny MLX stream tests, tiny checkpoint exactness, native night-driver
process-group tests, plus the new arm route/native smoke and actual physical
gates. MLX/Metal, D timing/identity/capability, actual storage/charge/meter state,
and live end-to-end readiness were not validated here.

Changed files: this run report and `docs/perf/2026-11-08-critical-path-sol2.md`.
No commits pushed. Commit subject: `docs: audit v4 critical path and next-arm gaps (Sol-2)`.

Next exact step: lead obtains/replays R1-ARM-1, assigns U3/B and D/C/T route
completion before R1 closes, freezes the role/scoring/storage decisions before
W1, and schedules Ed's physical card. The audit does not install those rulings.
