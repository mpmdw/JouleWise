# G2 checker — delta re-audit 1: magistrate disposition (Fable, 2026-08-30)

Auditor: fresh Sol xhigh; custodied as `G2-DELTA-AUDIT-1.md`. R-1/R-3/R-5
INSTALLED; R-2 DAMAGED, R-6 DAMAGED, R-8 PARTIAL; one new defect (F3).

## H-1. F1 (blocker) — R-2 becomes a GENERATED region; no third hand variant

The fix round's "mechanical extraction" filters runbook bytes through
hand-written `required_lines` — mutation-tested: neither runbook nor runsheet
drift is detected. This is the third failure of the D1 signature, so the cure
is now the maximally structural form: the runsheet's Phase D governed-chain
block becomes a MARKER-DELIMITED GENERATED REGION emitted by a small script
(`scripts/gen_g2_phase_d.py` or an extension of the checker) that reads
`window_runbook.md` at the pinned anchors and emits the chain verbatim; the
test REGENERATES the region and byte-compares it against the runsheet, and
separately asserts the runbook anchor lines still carry the pinned symbols.
Change either document and the test goes red — no interpretation layer, no
constant lists. If THIS form fails a further audit, a cold instance rules
before any further round (no discretion).

## H-2. F2 (blocker) — install the ratified R-6, don't append it

The runsheet keeps the ratified text but still runs the primary chain through
completion, retains the superseded NEEDS-RULING pin-advance section, and the
checker's F5-2/F5-3 require the in-night pin advance the ratification forbids.
FIX: (a) the runsheet's night chain STOPS at the post-bracket boundary — the
terminal head candidate is recorded, the pin is NOT advanced in-night; the
desk reviewed-refresh cycle section replaces the superseded pin-advance
section; (b) F5-2/F5-3 assert the RATIFIED expected state at the boundary
(candidate emitted; tracked pin unchanged; physical-ahead recorded as the
expected `calibration_ledger_head_mismatch` shape), refusing both a
prematurely-advanced pin and a missing candidate; regressions cover both.

## H-3. F3 (blocker) — exact-set membership

S11-A2 and F5-1..4 move from subset to EXACT-SET equality on collected
members: an extra member or extra block is a FAIL with a named reason.
Add the add-one-member regression alongside the existing delete-one.

## H-4. F4 (should-fix) — G2 splits into G2-a and G2-b; sequencing ruled

D-166 needs the prefill counts BEFORE the pack; D-162 G2's one-block proof
needs the pack. RULED: G2 splits into two evenings within the D-162 shape:
- **G2-a (first machine evening):** brackets + the prefill-resolvability
  probes (diagnostic, non-claim, own runs root; the probes need only the
  pinned Qwen3 models and the harness) at ALL FOUR lengths 512/1024/2048/4096
  — probe 4096 regardless of the pending ladder ratification; extra data
  costs seconds and discarding it is free — plus the G1 desk assertions.
- **Desk day:** prefill pin per the ruled selection rule (cold-gate
  ratification pending), `_v5` pack generation, estate 12.
- **G2-b (evening before the transaction):** the one-block proof on the real
  `_v5` pack + the ratified R-6 stop boundary + the finalize-refusal
  equality assertion.
The runsheet reorganizes under these names; the pack-existence gate applies
to G2-b only. CALENDAR NOTE for Ed: transaction slips to ≈ 09-02/03 unless
G2-a runs tonight (2026-08-30) with the desk day tomorrow.

## Round shape

Fix round 2 (Sol high) implements H-1..H-4; delta re-audit 2 (fresh Sol
xhigh) with the FIRST question a mutation test of the generated region in
both directions. Merge only after a clean delta-2 and green CI.
