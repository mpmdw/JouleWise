# 17 — Bounded post-seal round (charter §5): charge on the items CARRIED from the A267 round-2 delta lenses

Assembled by the magistrate (activation 59857fe5), 12:45 PDT 2026-09-22. Sealed files untouched. Scope: ONE question set, ruled by a fresh cold Fable judge; the ruling lands as file 18. Trigger: item C1 amends the cure text this gate ruled for §Q5 item 2, and the escalation topology forbids a further bench round on that function without a ruling.

## Facts (executed; records 13a/13b in the activation directory)

- Round 2 landed the ruled cure for §Q5 item 2 verbatim: in `record_attestation`'s `except OSError` (feature head `56ea8ae0`, `joulewise/quiet_predicate_campaign.py:766`), `temporary.unlink(missing_ok=True)` is the FIRST statement, before `attestation["state"] = "asserted"` and the reason are set.
- Execution lens 13b SHOULD-FIX 2 (executed): with `os.replace` raising `OSError` and `Path.unlink` raising `PermissionError` (an immutable or read-only directory), the `PermissionError` escapes `record_attestation`; the single production call site in `execute` is unguarded, so the envelope loop unwinds and the night ends REFUSED — and the attestation is left at `authenticated`, never withdrawn. Contract lens 13a NIT 2 found the same path by reading. The path did not exist at `489b0953`; it is a defect introduced by the ruled cure text.
- Execution lens 13b SHOULD-FIX 1 (executed): with `CLEANUP_BUDGET_RESERVE_S == ATTESTATION_TIMEOUT_FLOOR_S == 5`, the ruled `max(ATTESTATION_TIMEOUT_FLOOR_S, gap − cleanup_budget_s(protocol))` returns 5 for EVERY gap (pitches 601…1999 probed), so replacing the body with `return ATTESTATION_TIMEOUT_FLOOR_S` survives the whole 108-test module: the ruled regressions R3.1–R3.4 cannot distinguish the derivation from the floor.
- Both are fail-closed in direction (a refused night; never a false claim) and neither blocks the D-138 transaction; the magistrate carried them to the replay-lane PR (record 10 addendum, items C1–C6) rather than re-open the sealed transaction head.

## Q1 — C1: amend the §Q5 item 2 cure text

Options. (a) In the `except OSError` handler: set `attestation["state"] = "asserted"` and `attestation["reason"] = f"session rewrite failed: …"` FIRST, then `try: temporary.unlink(missing_ok=True) except OSError: pass`, then `return False`; regression: `os.replace` raising AND `Path.unlink` raising `PermissionError` → state `asserted`, reason recorded, nothing escapes, the night continues (counterfactual at `56ea8ae0`: `PermissionError` escapes with state left `authenticated`). (b) Additionally guard the production call site in `execute` so that ANY exception from `record_attestation` becomes `asserted` for that envelope. (c) Keep the ruled text; document the residual.

Lead's disposition (argument, not evidence): (a). Reasons: the withdrawal must precede any further filesystem call in a handler whose stated contract is "one envelope's annotation must never refuse the night"; (b) is broader than the defect and would mask programming errors; (c) leaves a delta-introduced refusal path in place.

Deliver: the exact replacement handler text and the regression with its counterfactual.

## Q2 — C2: a regression that distinguishes the ruled bound from its floor

Options. (a) Test-only: `with patch.object(campaign, "CLEANUP_BUDGET_RESERVE_S", 10): assertEqual(attestation_timeout_s(PROTOCOL), 10)` (counterfactual: `return ATTESTATION_TIMEOUT_FLOOR_S` → red). (b) Change the constants so the two differ in production (rejected by the lead: the ruled numbers are 5 and 5 and there is no scientific reason to move them). (c) Rule that the derivation is decorative and delete it in favour of the floor (rejected by the lead: the derivation is what makes a future registration with a different reserve correct without a code change).

Lead's disposition: (a). Deliver: AFFIRM or a better pin.

## Q3 — C3–C6 (nits from records 13a/13b), lead adopts all as dictated items of the replay-lane fix round

C3: a regression executing a sub-6 s-gap protocol showing the overrun is DETECTED by the drift abort (13b NIT 4). C4: `…vanishes_before_the_annotation…` asserts the specific exclusion `network_time_unattested` (13b NIT 5). C5: the `timed_log_window_epoch_s` docstring drops the clause claiming `log show` resolves the fold the same way (13a NIT 1). C6: `tests/fixtures/qpe01_pilot_n1_20260922/SOURCES.md` gains the two syslog fixtures' provenance (13a NIT 4 / 13b NIT 6).

Deliver: AFFIRM / amend each.

## Constraints on the judge

Read-only; nothing armed; no systemsetup/sudo/powermetrics/real `log`; probes: `git show 56ea8ae0:<path>`, grep, sed -n, python3 over the two records 13a/13b (`docs/process_traces/2026-09-22-activation-59857fe5/13a-…`, `13b-…`) and the sealed ruling 10 §Q3/§Q5 in this directory; at most one run of `tests.test_quiet_predicate_campaign` in the detached checkout `/Users/edr/code/JouleWise-wt-a267-review2` ONLY IF it is at `56ea8ae0` (check `git -C … rev-parse --short HEAD`; if not, skip the run and say so). Under 8 KB. Tier findings BLOCKER / MATERIAL / NIT. Charter §9: this round amends this gate's own ruled cure text only; no prior gate's verdict is reinterpreted.
