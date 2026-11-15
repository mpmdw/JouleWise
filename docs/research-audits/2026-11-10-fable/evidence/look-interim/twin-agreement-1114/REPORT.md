# Twin agreement, RL-166c section 4 (synthetic only)
Analyst: PR #795 head fdf1ec47b (scripts/cadence_look_run.py). Twin: sandbox/fit_twin.py (unmodified; run as a byte-identical copy fit_twin_copy.py in this directory because the twin refuses I/O outside its own folder; inputs copied to <set>/inputs/).
Runner run_all.sh, comparator compare.py, machine-readable compare_result.json.

| set | D | O | note |
|---|---|---|---|
| exact | PASS | PASS | |
| exact-c | PASS | PASS | level R/E files were present; used them (custody dir not used) |
| few_hot_days | FAIL | PASS | F2 |
| no_heat | PASS | PASS | |
| noisy | PASS | PASS | |
| onset_not_estimable | FAIL | PASS | F2 |
| baseline | FAIL | PASS | F1 |
| constant_start | FAIL | PASS | F1 |
| single_cell_onsets | FAIL | PASS | F1 |

Item 7 does NOT pass as written: 5 of 9 sets fail on D, all on two strings/nulls. Every O (energy fit, covariance, folds, P prints) agrees on all nine sets. No refusal on either side, so the analyst's extra refusal (leg hot-stretch energy <= 0) never fired.

## F1: state.first_off_kind order (baseline, constant_start, single_cell_onsets; 16-17 legs each)
Path /legs/N/state/first_off_kind. Analyst 'journal_pm_state_off+os_level_above_0', Sol 'os_level_above_0+journal_pm_state_off' (legs where both fire at the same instant).
Judgement: analyst looks wrong. INTERFACE.md line 250 lists the kinds as os_level_above_0 | journal_pm_state_off | native_pm_state_off "(joined by +)"; Sol joins in that order, the analyst uses sorted() (alphabetical), which puts journal before os_level. No ruling states alphabetical. Strictly the page does not say the join order, so a one-line ruling is cleanest; listed order is the better reading. Fix: fit_interim.py first_off return line (~l.321).

## F2: leg tau_hat_s for start_out_of_state legs when onset is not_estimable (few_hot_days, onset_not_estimable; legs 33 and 52)
Analyst null, Sol 0.0.
Judgement: analyst looks wrong. INTERFACE.md l.258: "0 for start_out_of_state; null when not_estimable"; the analyst's own tau_hat docstring says "0 for a leg whose start is out of state" and RL-166 Q4 gives 0 for those legs, but its code returns None when the model is None before reaching that test (fit_interim.py ~l.563-567, and l.769). Sol's reading (0 for out-of-state, null for other legs when not_estimable) applies both clauses. Not ruling-explicit for the not-estimable case, so it is also fair to send to the research lead; downstream O is unaffected on all sets. (single_cell_onsets is also not_estimable but did not trip F2.)

Other criteria checks: single_cell_onsets prints not_estimable, converged null, P-4 total 16, to_research_lead true on both sides (D agrees apart from F1).
