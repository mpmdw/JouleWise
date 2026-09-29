# Consult HOLD-BY-CONSTRUCTION-01: close the 25G83 claim hold so that no route exists, instead of closing routes one by one

You are ONE of several blind, independent design seats (a cold Fable judge rules afterwards). Disagreement is useful. You advise; you do not decide.

## Facts (verify; cite file:line). Candidate: `feat/2026-09-27-d138-25g83-issuance` at `8458f797` (your read-only worktree).

- **H1** (science addendum SCI-25G83-CANDIDATE-01-A1 §5.3): no claim-bearing result at macOS epoch **25G83** until the estimator cell-cap question is closed. The D-138 transaction issues the 25G83 calibration file `d079_calibration_acceptance_v2_n12_25g83_r1` but must keep H1.
- **Round 1** (design ruling `…/11-d138-design/21-coldgate-fable-ruling.md` §7.3): H1 = the file id in an arm admission list; the default moved to the new file. **Two refuters found routes** (packs declaring R7 judged by the moved default; a manual no-pack campaign): `…/50-d138-issuance-seat/refuters/hold-refuter-astra.md`, `contract-refuter-opus.md`.
- **Round 2** (design addendum `…/11-d138-design/31-addendum-ruling.md` §3): R7 stays the default; the loader returns the held file only to a caller passing `allow_claim_held=True`; a held file can never be the default; the admission list still refuses packs naming it. **A fresh refuter found another route** (`…/refuters/hold-refuter-2-opus.md`): B-1, a pack with `issued`=R7 and `issued_acceptance`=held is admitted (`_issued_d079` stops at the first key) and the arm evidence author certifies the held bytes via `_acceptance_bound_from_authenticated_bytes`, which skips the loader's hold. S-1 the loader is not the single gate; S-2 the keyword census misses non-literal forms; S-3 the registered operatives table returns held numbers by id; **S-4 the hold is keyed by FILE while H1 is keyed by EPOCH** (the planned interim re-issue or an R7 continuation to 25G83 would bypass it). No route reaches a NUMBER today, but an armed claim window counts.
- Same-signature escalation: two rounds each ended with a newly found route. Round 3 of route-by-route patching is not allowed; this consult is the next spend.
- Other open questions for the same final ruling (answer briefly): the promotion tool accepts deleted citation fields and a bare `{"id":"H1"}` hold list (`…/refuters/contract-refuter-2-astra.md`); four R7-freeze mutants stay GREEN because the default is R7 again (`…/mutation2/report.md`) — equivalent mutants or a real test gap?; the addendum's replay item (vi) expects the held file "loaded by path with the keyword" to evaluate fresh, but bracket evaluation re-authenticates without the keyword (`calibration_bracketing.py:1337`) (`…/replay2/report.md`).
(All `…/` paths are under `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/`.)

## Questions

1. **A design that makes "no route" true by construction**, not by enumeration. For example: an epoch-keyed hold (every acceptance whose `identity_epoch` is a held epoch, and every continuation into it, is held) enforced at the ONE primitive that turns calibration bytes into authority (`_acceptance_bound_from_authenticated_bytes` and anything equivalent), with the loader, the admission list, the evidence author and the operatives table all reduced to callers of it; plus a census test that fails if any new code path reads `configs/calibration/*.json` or constructs authority without going through the primitive. Evaluate that and alternatives; say what "a non-claim purpose" caller is, how it is authorised, and how the route-R non-claim captures (the cap plan) stay possible.
2. The minimal diff (files, functions) and the tests that make each known route (round 1 ×2, round 2 B-1, S-1..S-4) a RED-then-GREEN counterfactual, and one test that would catch an UNKNOWN route (the census).
3. Brief answers on the three other open questions above.
4. The risk that a third refuter still finds a route, and how the design bounds it.

## Output

≤ 1,500 words, plain language, every claim cited or marked as inference; first line `SEAT: <model> — HOLD-BY-CONSTRUCTION-01`. Read-only: modify no repository file; no git writes; no capture, powermetrics or battery read; do not call other models.
