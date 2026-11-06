# 2026-11-06 ALIGN v4 R1 adversarial review

Reviewed the High Power rehearsal at `a2193446` using synthetic data only.
Fixed verified-restore, exact sudo admission, non-negative deadman accounting,
and atomic/checkpointed measurement-record custody. The complete finding and
file/line map is `docs/align/reviews/sol-burn-r1-review.md`.

Focused Python tests pass except the pre-existing zsh integration test cannot
start in this Linux container (`/bin/zsh` absent). The whole-suite command was
started, produced 17 passing marks, and was interrupted after 42 seconds in
the known-slow `test_analysis_budget_pilot` module; it had emitted no failure
or error before interruption. This is an environment/time limitation, not a
green whole-suite claim.
