# Consult S1-REGRESSION-01: how S1 closes its full-suite regression (G2 mock workflows; G9 paper receipt repin; the fixture-repair plan)

ROLE: blind consult seat, read-only, with explicit license to disagree with the scout, the lead, and every option offered. Do not read other seats' answers (files 1x-* in this directory other than your own).
WRITE_SCOPE: []
Write nothing in any repository; scratch only under /tmp/s1-consult-<seat>-77b1bee2/. No git fetch/pull/checkout/commit. Do not call other models. /opt/homebrew/bin/python3 only; macOS has no `timeout` (perl alarm).

**The facts (verify them):**
- BFG-S stream S1 is the battery-float gate on bundle readers, consumers and the controller. Its head `c7593edb` is on branch `feat/2026-09-26-bfgs-s1-bundles`, worktree `/Users/edr/code/JouleWise-wt-bfgs-s1-e6f06c96`. It passed every targeted check and a cold final pass (MERGE).
- **The full suite on its integration tree** (`/Users/edr/code/JouleWise-wt-s1-integ2-77b1bee2`, `42e2af3e`) gives **115 failures and 418 errors**. Main is green.
- The classification scout is `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-77b1bee2/35-s1-refuter/62-regression-scout-report.md`, with the inventory `62-regression-inventory.jsonl` beside it:
  - **Fixture/test scope:** G1 and G3–G8 plus G10.
  - **G2** (98 outcomes): mock `not_applicable` members now refuse at window scope, including campaign completion (`run_campaign.py:9032`, `bundle_read.py:345`).
  - **G9** (23): the paper supply-map receipt digests are stale because S1 changed pinned sources (`configs/paper_supply/supply_map.json`, the owners `inputs.py:3195` and `whole_window.py:3791`).
  - **G11** (36): secondary failures.
- **S1's ruling texts:** Final texts v1.1 (`/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md`), the SWEEPCLASS rulings (`…/2026-09-27-activation-3ba66eeb/30-sweepclass-samesig/`), the RETURNS rulings (`…/60-s1-fix3/`), and the final pass (`…/2026-09-27-activation-77b1bee2/35-s1-refuter/51-fable-finalpass-ruling.md`).

**Answer:**
1. **G2.** What should a mock (`not_applicable`) member do at window scope and in campaign completion? Should it refuse, as it does now, with the tests changed to expect refusal? Or should a ruled non-claim path let mock workflows complete while claim artifacts still refuse? Cite what Final texts v1.1 says about mock/`not_applicable`. Pick the answer that keeps the gate strict for anything claim-bearing and needs the least production change.
2. **G9.** Who may repin the paper supply-map receipts, and in what order relative to S1's merge? Must it be the same PR, since S1 changes the pinned sources? What review does a repin need, given that paper receipts are claim-adjacent?
3. **The fixture-repair plan** for G1, G3–G8, G10 and G11. Give the ordered steps, the WRITE_SCOPE (which test files and fixture builders), the defect-shaped checks, and how to avoid weakening any assertion. Size it: one seat, or several parallel seats split by module group?
4. **Process.** Every gate before row 9 ran only targeted suites. What single change to S1's remaining gate sequence prevents a repeat? For example, the full suite on every fix head.
5. Anything that makes you prefer NOT merging S1 at all in its current form. For example, splitting it.

Report: tier findings BLOCKER / SHOULD-FIX / NIT with file:line; end with `RECOMMEND: <one line>`.
