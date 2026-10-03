<!-- verbatim extract: registration lines 262-278 of 1-registration-and-arms/preregistration_d079_epoch_25g83_rev1.md -->
## Known conditions (recorded, not rules)

**Display state at t0 is not constrained by the night gate.** The gate
(`joulewise/night_gate.py`, condition C3) requires the screensaver's
`idleTime` preference to read exactly `0` — meaning the screensaver never
engages, refusal reason `night_refused_hid_idle` — and for the display it only
requires that `pmset -g` yield a parseable `displaysleep` setting, recording
that value as evidence without demanding any particular one; it never probes
whether a panel is awake, dimmed, or asleep when the window opens, and the
derivation chain deliberately omits the writer flag
`--sleep-display-before-capture` that the G2-a chain passes, because no
operator is present to schedule a display action. These captures may therefore
differ systematically in display state from the G2-a corpus the resulting
acceptance will judge. That is recorded here as a known condition of this
corpus, not a rule: it edits no membership, moves no threshold, and licenses
no re-capture.

