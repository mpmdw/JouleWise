# TIER01-GATE-01 delta triage (magistrate, activation ed17a643)

Sol delta re-audit of fix commit `3fdbbd13` (43; relaunched after 817355d2's seat was killed): FIX-FIRST, no BLOCKER. The regression was mutation-checked: RED on the pre-fix predicate, GREEN at `3fdbbd13`.

- **F1 (MATERIAL, as filed): dictated text not byte-exact because "#419" was inserted.** Dispositioned as no change. Fable's dictated text contains the instruction "(set the PR number here at merge)", and filling in the number is that instruction carried out. The date stays tied to the merge; the magistrate's row-12 read checks it against the actual merge date and moves both dates if the merge slips past 2026-09-25.
- **F2 (MATERIAL): the two deferred lanes existed only in the triage.** Fixed. TIER01-PATH-GUARD-01 and TIER01-D118-RECONCILE-01 are now registered in `docs/process/state_kernel.json`, and `gen_state` has regenerated TASK_QUEUE (`--check` = 0).
- **F3 (NIT): the F6 attribution is paraphrased across comment lines.** No change; the meaning matches Fable's text.
- **F4 (NIT): D-118 wording survives.** This is the known deferral, carried by TIER01-D118-RECONCILE-01.
