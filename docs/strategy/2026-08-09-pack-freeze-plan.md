# D-117 pack-freeze plan (T2, 2026-08-09) — magistrate rulings + Ed taps

## ⇒⇒ ED RULED BOTH TAPS (2026-08-09, in-thread) — GUIDING LIGHT: "decisions serve the BETTER PAPER"
- **Q1 = FREEZE the recommended p256 prompt** (35× "The plan remains easy to audit." + 1 "…and simple to review."; dual-tokenizer-identical 256 IDs, token-ID sha 83099a66). 
- **Q8 = FUND dedicated p256 prefill floor cells** for both stacks (makes the prefill energy contrast claim-capable = the better paper). No p128→p256 transport (Q2C).
- STANDING DECISION PRINCIPLE (Ed): when a call is discretionary, the tiebreaker is whichever choice makes the better paper.


Sol drafted a per-question decision packet (xhigh, read-only, custodied at
session scratchpad `packfreeze-packet-out.md`). The magistrate has ruled the
process/metrology/method questions. None of this lands measured numbers
without a quiet night, so freeze is gated on the work orders below — the two
Ed taps are RULED (banner above); the tap section below is retained as the
decision record only.

## ⇒ TWO ED TAPS — **BOTH RULED 2026-08-09 (see banner); historical record only**

- **Q1 — gamma p256 prompt text [ED-DECIDES].** Recommend FREEZE the
  constructed 256-token prompt (35× "The plan remains easy to audit." + one
  "The plan remains easy to audit and simple to review."). It encodes to the
  **same 256 token IDs on BOTH the 1.5B and 7B tokenizers**
  (token-ID sha `83099a66…`), so the contrast is tokenizer-matched, and the
  repetition makes it auditable. Claim must say "this fixed synthetic
  256-token prompt," not content-general prefill. YES → the arm's prompt bytes
  freeze; NO → gamma waits for replacement text passing the same dual-model
  exact-token proof.
- **Q8 — fund dedicated p256 prefill floor cells? [ED-DECIDES].** Because
  transport from the p128 floors is refused (Q2C), the only claim-capable path
  for a p256 prefill ENERGY contrast is dedicated exact-window p256 floor
  cells for both stacks — extra quiet-window budget. YES → gamma can carry an
  L2/L3 prefill energy claim; NO → the p256 arm publishes only as
  descriptive/prospective sizing evidence (no energy-contrast claim), or you
  narrow D-122 and drop the arm.

## MAGISTRATE RULINGS (decided; Sol-backed, adopt at freeze)

- **Q2A prefill inferential test — RULED:** decode-matched two-sided
  one-sample t-test over the 10 ABBA block estimates, D_i=(B1+B2)/2−(A1+A2)/2,
  B−A = 7B−1.5B, α=0.05, positive direction required for a positive claim.
- **Q2B multiplicity — RULED:** ONE gamma Holm family = {decode contrast,
  p256 prefill contrast}, α=0.05, **m=2**, both registered pre-collection. No
  third gamma contrast without prospective refreeze.
- **Q2C p128→p256 transport — RULED:** NONE. No scaling/transport formula; the
  `same_stack_componentwise_worst_case.v1` rule may evaluate only inside the
  measured source envelope, else `NOT RESOLVABLE` (fail-closed). (This is what
  makes Q8 load-bearing.)
- **Q3 reference cadence — RULED:** keep the 9-reference schedule (3 start +
  singles after members 20/40/60 + 3 end); 20 & 60 are the arm midpoints, 40
  is the decode/prefill boundary.
- **Q4 acceptance selection — RULED:** keep **issued-only** (issued D-116
  artifact, sha `31611396…`); a successor issuing before arm ⇒ pack
  regeneration. D-125's lineage envelope stays available but is not required
  per-pack.
- **Q7 D-124 estimator — RULED (a gate, not a choice):** packs may NOT freeze
  while the estimator is `candidate_pending_floor_commonmode_01`; D-125
  requires implementation first ⇒ **FLOOR-COMMONMODE-01 work order** (below)
  must land through the full D-118/D-121 gauntlet before pack regeneration.

## ENGINEERING WORK ORDERS (freeze-blocking; no Ed input needed)

1. **FLOOR-COMMONMODE-01** — implement the D-124 two-shared-edge common-mode
   estimator (two shared edges + bundle-specific adversarial terms, once-only
   allowance, transfer limitation, identical calibration/consumer covariance
   treatment) → D-118/D-121 gauntlet → pin its implementation identity in all
   affected packs. **The long pole for freeze.**
2. **D-123 byte-identity proof (Q5)** — strengthen both floor packs'
   `test_reporting_section_does_not_change_floor_output` to serialize extractor
   results through the production canonical output path and compare raw
   bytes+SHA with/without the reporting keys (7B currently proves object
   equality only; 1.5B proves validation+projection only).
3. **Receipt-oracle re-derivation (Q6)** — lead-owned arm-materialization from
   MERGED-MAIN cadence (10 physical receipts / 5 logical ops per session; the
   3-window production regression is the authoritative oracle). Derive from the
   authenticated live head; never hand-author receipt literals. Replaces the
   stale `impl/d117-ledger-recovery` TODO markers (surfaced by the T2
   post-merge integration review as CS1).
4. **Prefill phase-recording proof (Q9)** — **DISCHARGED 2026-08-09** (`2cd9bc3`,
   `docs/process_traces/2026-08-09-prefill-phase-proof/PROOF.md`): 7B PROVEN,
   1.5B PROVEN-WITH-CAVEATS (sampling-resolution label on 37/50 short windows,
   not boundary mislabeling — expect the same label pressure on the Q8 p256
   1.5B cells).

## Fastest path to a frozen, armable pack set

Ed taps Q1+Q8 RULED → land FLOOR-COMMONMODE-01 (gauntlet) → the two remaining
engineering proofs (2–3) → regenerate all three packs from the resulting head
→ generator `--check` + focused/canonical suites → issue readiness + identity
projections → materialize the first arm against the authenticated ledger head.
(Freeze also assumes the trust mint bar has landed.)

Note: Sol's V3/V4 `--check` "failures" in the packet were a read-only-sandbox
no-writable-tmpdir artifact (F3), not pack defects; beta regen passed.

## ADDENDUM 2026-08-10 (T4, from the FCM-01 cold-gate refuter) — lineage-monotone allowance vs short prefill windows [ED-VISIBILITY]

Both floor packs' extraction specs select the D-124 common-mode estimator for
the **prefill p128** comparative cells, not only decode. The estimator's
admitted domain is `window duration > 2×B_op`, and B_op is lineage-monotone
non-decreasing (D-125 cl.2): a successor calibration acceptance can only
strengthen (grow) the allowance. Measured 1.5B p128 prefill windows are
0.121–0.147 s against today's 0.0736 s collapse threshold — a 1.64–2.0×
margin. **If a successor bracket's allowance grows past ~64%, frozen prefill
comparative cells silently convert from estimated to refused after the packs
have frozen the estimator identity into their bytes.** Freeze-gate additions:
(1) record each registered comparative cell's minimum window-duration margin
at collection as a checklist item (the FCM-01 committed inventory test
supplies the mechanism); (2) at pack regeneration, evaluate whether the
p128 prefill cells should select the worst-case default estimator instead of
D-124 given the margin (a magistrate/Ed call at freeze, not now); (3) the
same margin math must be run for the Q8 p256 cells when their windows are
first measured (p256 windows are expected longer, but expected is not
evidence). Compounds the recorded zero-power-short-window over-refusal note.
