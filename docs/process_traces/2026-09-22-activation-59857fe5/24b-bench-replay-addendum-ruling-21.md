# 24b — Tracked addendum to artifact 24 (cold ruling 21 condition C1), 2026-09-22 20:00 PDT

Artifact 24 (`24-bench-replay-start-drift.md`, raw `24-bench-replay.json`) is the full bench replay executed at the merged head `4f8bc36d39b71a06d0502016df0ff26f452b7a63` (transaction merge 7eb53effc78b8c90995ca8206df67c0e10ff18e5 is an ancestor — P7.3). This addendum carries what the cold ruling `docs/process_traces/2026-09-22-activation-59857fe5/08-coldgate-packet-a267-merge-transaction/21-coldgate-fable-replay-verdict-ruling.md` requires beside it; nothing in artifact 24 is edited or relabelled.

## Ruled admissibility text (verbatim from ruling 21 §Q2)

> Admissibility (cold ruling 21, 2026-09-22). This artifact meets ruling 10 §Q7 / P7.1 when ALL hold: (1) 12 of 12 slots recorded at the merged head; (2) every slot `collector_exit == 0`, `cleanup_proven == True`, `attestation_state ∈ {authenticated, slew_attested}`; (3) every chain-level `start_drift_s` ≤ 0.5 s, and `max ≤ 0.5 s` is stated; (4) the fidelity table against the archived v3.1 class {02,05,06,08,09,11,12} is printed with its tally; no slot resolves (`bounded`) where the archive did not — one such slot VOIDS the run; slots refusing where the archive resolved are admissible; (5) at least one slot is `bounded` with `interior_complete_support == True`; (6) max `tail_s` + 2.3 s (F8 worst skipped tail) < the 20 s gap, stated with the figures. Session-level `start_drift_s` is reported per slot and assessed only against the night's 2 s rule (A269 A1); the driver's 0.5 s session bar and its `bounded`-on-every-slot requirement are lead conventions, not ruled bars. Driver output: status FAIL, statement quoted verbatim above, retained as issued.

## Per-slot fidelity table (replay anchor class vs the archived v3.1 class; refusing-direction mismatches are admissible, an admitting-direction one voids the run)

| slot | chain start_drift_s | session start_drift_s | exit | cleanup | attestation | replay anchor (detail) | archived class | fidelity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0.352 | 0.6078682499937713 | 0 | True | slew_attested | unknown (wall_minus_monotonic_span_exceed) | unresolved | MATCH |
| 2 | 0.150 | 0.4040190000087023 | 0 | True | authenticated | bounded () | bounded | MATCH |
| 3 | 0.150 | 0.4037062500137836 | 0 | True | authenticated | unknown (affine_clock_residual_exceeded) | unresolved | MATCH |
| 4 | 0.150 | 0.4075586250401102 | 0 | True | slew_attested | unknown (affine_clock_fit_empty) | unresolved | MATCH |
| 5 | 0.150 | 0.40788495901506394 | 0 | True | slew_attested | bounded () | bounded | MATCH |
| 6 | 0.149 | 0.4105639170156792 | 0 | True | authenticated | bounded () | bounded | MATCH |
| 7 | 0.150 | 0.40275679202750325 | 0 | True | slew_attested | unknown (rate_aware_native_set_empty) | unresolved | MATCH |
| 8 | 0.150 | 0.4036535419872962 | 0 | True | authenticated | unknown (affine_clock_residual_exceeded) | bounded | MISMATCH (refusing) |
| 9 | 0.150 | 0.40581804199609905 | 0 | True | authenticated | unknown (affine_clock_residual_exceeded) | bounded | MISMATCH (refusing) |
| 10 | 0.150 | 0.4076725000049919 | 0 | True | slew_attested | unknown (affine_clock_fit_empty) | unresolved | MATCH |
| 11 | 0.150 | 0.3992427919874899 | 0 | True | slew_attested | bounded () | bounded | MATCH |
| 12 | 0.150 | 0.40311966702574864 | 0 | True | slew_attested | bounded () | bounded | MATCH |

Tally: 10 MATCH, 2 MISMATCH refusing-direction, 0 MISMATCH admitting-direction (a non-zero admitting count would VOID the run).

## The driver's own status, verbatim and unrelabelled

status: `FAIL`
statement: `7/12 slots NOT admissible, so their drift figures are not a measurement of the finalisation tail: slot 1 anchor_status='unknown' (required 'bounded'); slot 1 interior_complete_support=False (required True); slot 3 anchor_status='unknown' (required 'bounded'); … and 11 more; the chain figures themselves are under the bar (max 0.352 s <= 0.5 s); the session-level bar is exceeded too (max 0.608 s > 0.5 s on slots [1])`
max_chain_start_drift_s: 0.3523999589961022 | slots_over_bar: [] | max_session_start_drift_s: 0.6078682499937713 | session_slots_over_bar: [1]

Disposition under ruling 21: the driver's FAIL is a lead-authored bench convention (anchor `bounded` on all twelve), not a governed verdict; read against ruling 10 §Q7 the rows meet the ruled bar (max chain-level start drift 0.352 s ≤ 0.5 s on every slot). Slot 1's session-level 0.608 s is assessed only against the night's ruled 2 s rule (A269 amendment A1): margin 1.39 s. The driver's X1 ESCALATE convention (session bar 0.5 s) is likewise disposed here (ruling 21 M1): it does not bear on the ruled bench bar. The driver amendment (fidelity rule replacing the bounded-on-all requirement; session bar reported at 2 s) follows the arm in its own PR, which must show `verdict()` re-run on this very JSON producing PASS (ruling 21 C3).
