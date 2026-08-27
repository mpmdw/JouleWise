# Magistrate ruling — THREAT-MODEL-PRUNE-01 (D-161 addendum; T26, 2026-08-27)

Three blind seats (Sol xhigh, Opus 5, Fable 5) enumerated every refusal
from code. They converge on the A/B core, on the pinset as the week's
cost, and on "land only the refresh lane before `_v4`". They differ on the
operative test; the Opus reframe is adopted.

## The operative test (adopted)
Under a single-operator threat model every actor IS the trusted operator,
so "who is the adversary" retires the whole instrument. The test that
separates the classes is: **does the refusal catch a MISTAKE the operator
could plausibly make, or only a DELIBERATE act?** Fail-closed stays for
PHYSICS/EVIDENCE (A), PRE-REGISTRATION (B) and OPERATOR MISTAKES
(C-mistake: immutability of raw evidence, duplicate keys/slots/ids, output
landing inside an input bundle, digests before root execution, the tool's
own bugs). It goes for DELIBERATE-ONLY guards (C-deliberate).

## Rulings
R-1. **Histsem pinset — asymmetric.** The historical-side equality
(`historical_pack_tree_sha256` at `head_commit`;
`histsem_historical_digest_mismatch`, `_not_pre_authoring`) is B and stays
fail-closed. The current-side equality (`histsem_pinset_mismatch`) and the
post-authoring delta list (`histsem_post_authoring_delta_unexpected`)
become WARN-AND-RECORD **after the `_v4` transaction closes** (the frozen
runbook C10/E4 and estate 11 consume PASS today). Before the night the
only change is D-161 (1): the reviewed refresh lane (S14), and the
"no update lane" test becomes "no unreviewed update"; the fourth tripwire
the seats found — the four custody-tool `.sha256` sidecars
(`test_family_marker.py:788-794`, `arm_readiness.py:11019 tool_mismatch`)
— folds into the same lane.
R-2. **HISTPACK-PROMISOR-NOFETCH-01 is RETIRED unbuilt** (all three
seats: pure clone policing; the guard is already porous; largest saving
because the cost is unspent). HISTPACK-TEMP-CLEANUP-01 (a real leak on an
I/O-failure path, C-mistake) may land alone if small.
R-3. **Landing mechanism:** `DEAD_REASON_CODES` in `reason_kinds.py` is the
retirement lane; three meta-guards (partition totality, live-emitter,
executed-witness) mean a prune is a real change, not a deletion. RETIRE
is preferred to WARN wherever the finding has no consumer.
R-4. **Nothing else changes before the `_v4` night.** The pre-night code
surface stays at the reviewed head plus the lane. The post-transaction
prune waves, in order of cost saved: (a) quiet-guard PID-custody /
same-UID injection guards → WARN (D-148 (6) already accepted them as
limitations; the contamination CENSUS itself is A and stays);
(b) `authentication_io` forbidden-key / `input_changed` / AST direct-read
lint → retire; (c) exact live-ID oracle and `gen_state --check` hard fail
→ regenerate-and-diff in CI (keep the check, stop blocking);
(d) per-file pack digest tables, `FROZEN_GENERATOR_SHA256`, reducer source
pin, mint-core interface pin, callable-source hashes → retire (the
registry regeneration test proves the same fact); (e) CI timing/count
pins → derive; (f) doc↔code prose tripwires → retire, keeping the
launcher-argv regression (D-158 R-4) and the DATA/CONTRACT partition.
Every wave is one PR with a Sol audit; none touches A/B.
R-5. **The freed enforcement budget goes to the 122 unenforced ruled
clauses** (S9): the failure there is silent; the C tripwires' failure was
loud and cheap in CI and expensive only in operator round-trips.
R-6. **Paper §7 sentence** (item 60, adopted from the Opus seat, replaces
the opening of the operator-trust paragraph at fills time): "The
repository is tamper-evident for the operator's own benefit — a way to
catch one's own mistakes — not tamper-proof against anyone; it assumes a
single trusted operator, so every gate defends against error and post-hoc
choice, never against an adversary."
R-7. THREAT-MODEL-PRUNE-01 is registered as a kernel row (post-`_v4`,
p2, with R-4's waves as its acceptance) in the next kernel wave.

## Custody
`00-brief.md`, `01-sol-seat.md`, `02-opus-seat.md`, `03-fable-seat.md`.
