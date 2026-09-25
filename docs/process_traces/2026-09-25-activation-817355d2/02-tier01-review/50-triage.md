# TIER01-GATE-01 triage (magistrate, activation 817355d2)

The reviews: the cold Fable final pass (40) ruled FIX-FIRST, text only, then MERGE. The Opus contract lens (41) ruled FIX-FIRST, text only. The Sol execution lens (42) ruled FIX-FIRST. None found a BLOCKER. All three found the checker correct and fail-closed on the ruled branches.

Applied in one commit, using the texts the Fable judge dictated:
- **F1 (MATERIAL, Fable; M2 Opus):** the rule header now cites COUNCIL-407-01 §G5 and Ed's #415 endorsement.
- **F2 (MATERIAL, Fable; M2 Opus):** installation is dated at the merge of PR #419, and the day-30 review is 2026-10-25. The change is in both `docs/orchestration.md` and `docs/process/tier01_defect_log.md`.
- **F5 (NIT, Fable; MATERIAL M1, Opus):** the dated D-170 addendum in `docs/decision_log.md`, with Fable's exact text. **Opus dissent recorded:** M1 also asked for an "AMENDED by TIER-01" line under D-118 and a new D-185 index row. Fable rated the reconciliation a NIT, and its verdict prevails. The magistrate may not author a new decision-log entry alone (rule 11), so the D-118 line and D-185 are not added. Lane TIER01-D118-RECONCILE-01 carries Opus's M1 to the next cold gate.
- **F6 (NIT, Fable):** the attribution wording in the `gate-ledger.yml` header and the `docs/orchestration.md` §5 sentence.
- **F3 (NIT, Fable; N1 Opus):** `main()` now uses `check()`'s Tier predicate for the success line. The defect-shaped regression `test_indented_light_tier_line_reports_full_twelve_rows` is RED on the old checker (`'4/4 RUN; 8/8 N/A (light tier)' != '12/12 RUN'`) and GREEN on the fix.

Not applied, as follow-ups:
- **Sol SF-2, #415 path validation:** Fable and Opus both ruled it a follow-up, not a merge condition. Lane TIER01-PATH-GUARD-01 takes Opus's design (41 §T3) and must land before the day-30 review.
- **Sol SF-1, a fenced or commented `Tier: light`** (Fable F4 NIT, Opus N2 NIT): this path needs deliberate action, so it is outside D-161's mistake-class threat model. Recorded only.
- **Opus N3** (`enforce_admins` false): a note for the next doc touch.

Bench: `tests.test_check_gate_ledger tests.test_gen_state` ran 83 tests OK. `gen_state --check` OK.
