# Design consult D138-25G83-DESIGN-01: how the epoch-25G83 calibration candidate becomes the issued, active D-079 acceptance

You are ONE of several blind, independent design seats (decision log D-144 co-design; D-184 four-model council). Do not read `docs/process_traces/2026-09-27-activation-d528efb2/` (another seat's design lives there) or `/tmp/d138-*` other than your own scratch. Disagreement is useful. You advise; a cold Fable judge rules.

Repository: the working tree named in your preamble (main `e7c8bcc6` plus the 2026-09-27 records). Read-only.

## Facts (verify what you rely on; cite file:line)

- **The candidate:** `docs/process_traces/2026-09-27-activation-77b1bee2/60-prepare-record/30-run1/candidate_acceptance_25g83.json` (sha256 `dbad7cc7…b5b2`), n = 12 members from sessions W1/W2 of epoch 25G83, S = 0.013701 s, C = 0.019021 s, marked `candidate_not_issued`. It was written by `scripts/issue_calibration_acceptance_generation.py prepare-candidate` (which has no `issue` verb). It passed a cold science gate (`…/70-science-gate/21-science-gate-ruling.md`: PROCEED TO ISSUANCE, disclosures D1–D6 §7) and addendum A1 (`…/31-addendum-ruling.md`: B1–B4 — the four D-138 estimator files stay byte-identical, no cap change, no staged estimator branch; D7 and the H1 HOLD — no claim-bearing 25G83 window until the cell-cap question is ruled; H1 "goes in the issuing record and every 25G83 arm material").
- **The active acceptance today** is `d079_calibration_acceptance_v2_n17_r7` (epoch 25F84), registered in `joulewise/calibration_bracketing.py` (issued registry, generation derivations, ACTIVE/DEFAULT). The R7 precedent for moving live pins is commits `1b8a076b` and `ddfb25e9` (2026-09-22); D-142 (decision log) and commit `3e780a1` are older precedents.
- **Observed defect (reproduce it):** if the candidate is converted in memory to issued form (role/status flipped, `derivation_sha256` recomputed, its generation row registered), `_valid_acceptance_bound` in `joulewise/calibration_bracketing.py` still returns False (around line 989): eleven earlier 25G83 ledger rows marked `valid` — disposed of under decision D-126 in `configs/calibration/observation_dispositions.json` and correctly kept in the candidate's prior-observation set — are treated as unregistered members. The issuer authenticates that disposition registry; the loader does not.
- Revision 5 preparation code asserts its historical R7 predecessor equals `ACTIVE_ACCEPTANCE_ID`, and `scripts/epoch_equivalence_check.py` inherits the moving default path — both would break when the default moves.
- Decision log D-138 (atomic transaction), D-139 A3 (acceptance-artifact identity and judgment-bearing publication are Ed-reserved; the magistrate will ask Ed for the name), D-150b (mechanical exact-byte comparisons delegated), D-144 (co-design). Owner directive #421: anything that can change whether a number is true is mandatory.

## Questions

1. **Loader repair.** Design the change that lets a generation's member-completeness check exclude D-126-disposed rows. It must authenticate the disposition registry (by what pin?), bind to the candidate's recorded disposing decision ids, keep those rows in the prior set, and still refuse any undisposed foreign `valid` row. Where does the shared authentication code live so issuer and loader cannot diverge? Give the defect-shaped tests with their counterfactuals.
2. **Issued bytes.** Exactly which fields change from candidate to issued artifact, which seals are recomputed and how (production recipe), and what must stay byte-identical (members, prior set, estimator pins, statistics, operatives). Should the prepared candidate be re-run instead? Why or why not.
3. **Pin swap.** Every place that must change atomically (find them by grep), what stays (R7 must still authenticate and judge 25F84), and how R7-specific consumers are frozen to R7.
4. **Disclosures and the HOLD.** Where do D1–D7 and H1 live so they travel with the artifact: issuing record only, or also inside the artifact? The loader currently requires `claim_eligible = true` for an issued artifact — what should that bit mean relative to H1, and how is H1 enforced mechanically at window arm (or is procedural enough for now)?
5. **Verification and gate.** Pre-issue re-hash list, independent replay, what the full suite must show, and the review/gate sequence for this one PR.
6. **Name** (advice to Ed only): the issuer's prospective id is `d079_calibration_acceptance_v2_n12_25g83_r1`. Any reason to prefer another?
7. Anything that should stop or re-order the transaction.

## Output

≤ 1,800 words, plain language, every claim cited or marked as inference, first line `SEAT: <model> — D138-25G83-DESIGN-01`. Run read-only commands and in-memory probes only; modify no repository file; scratch under your own `/tmp/d138-design-d528efb2/<seat>/`.
