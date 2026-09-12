BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
BRIDGE_TASK_V1
{
  "TASK_SHAPE": "bounded",
  "GENRE": "discussion",
  "ROLE": "read-only design consultant (pre-decision, rule-2 consult; explicit license to disagree with the magistrate's framing and to propose unlisted options)",
  "OBJECTIVE": "Recommend the sound closure shape for calibration consumption of HISTORICAL measurement windows under the issued D-079 calibration anchor, given that live-receipt bracketing structurally excludes all pre-genesis windows.",
  "AUTHORITY": [
    "docs/contracts/bridge_protocol.md (bridge-protocol/v1.1)",
    "AGENTS.md",
    "Magistrate ruling: this is a READ-ONLY consult; WRITE_SCOPE is []; do not write, stage, or commit anything.",
    "Optimization target: P1 = A+ MVP capstone paper with Phase-3 measured data; advisor (Suzanne Rivoire, JouleSort co-author) sets a metrology-rigor bar; soundness above all (Ed standing directive).",
    "D-110 (mint #1 re-derivation order), D-113 (Window C fresh-collection precedent), D-078 (soundness gate; attribution-limited ~1 J), PR #109 (D-079 issuance, merged this morning)."
  ],
  "WRITE_SCOPE": [],
  "BASE_HEAD": "c5373862c488f7c8f20d9f42e7ae341f52f98fd5",
  "EARLY_RETURN": ["NEEDS_RULING"],
  "OUTPUT_PROTOCOL": "bridge-report/v1"
}
END_BRIDGE_TASK_V1

You are a read-only design consultant at reasoning effort xhigh. This is a
pre-decision consult under the lead's rule 2: you have explicit license to
disagree with the magistrate's framing below and to propose options not
listed. Do NOT write any files; return the full analysis as your final
message, ending with the required bridge-report/v1 envelope (status
DISCUSSION expected).

CONTEXT (verified live by the magistrate this session, all at main c537386):

- PR #109 (D-079 issuance, D-116) merged this morning: the calibration
  acceptance artifact is ISSUED
  (configs/calibration/calibration_acceptance_d079_v2.json, artifact_role
  "issued"), committed head-pin seq 76 / 08456d50..., ledger
  runs/calibration_observation_ledger.jsonl (76 receipts, git-ignored,
  backed up).
- D-110 orders the mint #1 re-derivation "under the landed selector with the
  computed allowance" -- all three conditions (a) PR #100, (b) PR #109,
  (c) PR #105 are now satisfied.
- FIRST CONSUMPTION ATTEMPT REFUSES. The magistrate ran the governed
  re-verdict (run_campaign.py --whole-window-verdict
  --consumption-semantics-id d078_authenticated_max_bracket_rederivation_v1)
  on runs_window_a10_20260725: exit 2, "authenticated survivor consumption
  refused: instrument_calibration_bracket_missing". Root cause chain, all
  verified by direct reproduction:
  1. joulewise/calibration_bracketing.py discover_calibration_candidates
     skips any observation with is_historical_import=True ("Enumerate valid
     endpoints from the sole ledger authority").
  2. The issued ledger's snapshot at cutoff 76 contains 38 observations,
     ALL is_historical_import=True (dispositions: 30 valid / 6
     ordinary-invalid / 2 systematic-invalid). Zero live (post-genesis)
     receipts exist.
  3. evaluate_calibration_bracket requires causal live candidates:
     causal_pre (capture <= window_start) and causal_post
     (capture >= window_end) within MAX_AGE_S. Zero candidates ->
     instrument_calibration_bracket_missing.
  4. The exclusion is deliberate and test-enshrined by PR #109 itself:
     tests/test_calibration_bracketing.py::test_import_marker_is_excluded_by_discovery_and_trigger_paths
     (line 716).
  5. Consequence: NO historical window (a10 2026-07-25, window C
     2026-07-26, 7B floor window 2026-07-29 -- all pre-genesis) can ever
     pass max-bracket consumption under merged semantics, because live
     receipts appended in the future cannot causally bracket a past window.
     The D-110 re-mint as a desk operation is structurally impossible at
     current main.
- Also relevant: the evaluator's anti-narrowing universe check
  (supplied_valid must equal registered_valid where registered_valid =
  non-import valid observations) -- any historical-candidacy design must
  generalize this check without weakening it.
- Separately known (scout F1): scripts/mint_floor_artifact.py:91
  EXPECTED_OPERATIVE_FLOOR_TEXT="7.377086" (D-084 hard literal) will refuse
  the corrected re-mint's widened floor; a per-plan literal re-supply is
  needed regardless of this fork's outcome.

You have full read access to the repository at
/Users/edr/code/JouleWise (HEAD c537386). Inspect the actual code and tests
cited above (joulewise/calibration_bracketing.py, whole_window.py,
tests/test_calibration_bracketing.py, the issued acceptance artifact,
scripts/mint_floor_artifact.py) before answering; do not take the
magistrate's characterizations on faith.

THE FORK -- the consult question: what is the SOUND closure shape for
calibration consumption of HISTORICAL windows under the issued anchor?

Option 1 -- role-aware historical candidacy: allow import-marked VALID
receipts as bracket candidates ONLY for windows entirely preceding the
ledger cutoff. The 38 imports were hash-authenticated and physics-replayed
(32 valid/6 invalid at verification; ledger dispositions 30/2/6 after the
lead's B1 ruling) precisely to authenticate these historical calibrations.
Requires: candidacy rule change, a historical variant of the universe check
(import-marked valid <= cutoff), causality conditions, regression vectors,
full gauntlet, and arguably a rule-11 cold gate since it amends a
just-cold-gated contract.

Option 2 -- declare historical re-mint closed; collect a fresh window
(Window D) under the live-receipt regime: pre/post calibrations append as
live ledger receipts, bracket derivation works as designed, floors +
contrast mint from pristine end-to-end-authenticated evidence. Costs a
quiet-mac night (Ed present for section 5A), delays Phase-3 measured data;
D-113 precedent ("Window C will be collected fresh"; Ed: soundness above
all, ample time). Arguably the STRONGER paper story (instrument
authenticated end-to-end, no historical-import caveat in the claims chain).

Option 3 -- any intermediate you can defend (e.g., per-bundle embedded
b_fiducial consumption -- the magistrate's prior is that this is
self-attested evidence, exactly what issuance replaced; presumed unsound,
but state your view).

DELIVERABLES (final message, structured; use the Positions /
Disagreements / Open questions / Recommendation discussion shape from the
bridge contract section 2, folding the numbered items below into it):

1. Recommended option with the soundness argument (the paper's claims chain
   is the optimization target: P1 = A+ MVP paper with Phase-3 measured
   data; advisor is a metrology-rigor domain expert).
2. If Option 1: precise semantics sketch -- candidacy predicate,
   universe-check generalization, causality/freshness conditions for
   historical windows, which tests/regressions are mandatory, estimated
   blast radius in calibration_bracketing.py/whole_window.py, and whether
   it weakens any security property the import marker was built for (state
   the property inventory).
3. If Option 2: what exactly Window D must collect (both floor cells +
   contrast in one window? two windows?), what desk work remains valuable
   meanwhile, and what the historical corpora remain good for (diagnostics,
   methods-section narrative).
4. The 7B-mint impact under each option (window_7bfloor_20260729 is also
   pre-genesis).
5. Risks/refutations of the magistrate's framing -- anything mis-stated
   above, anything the fork misses.

Constraints reminder: read-only; no file writes of any kind; bridge depth
is one hop (do not call Claude by any launcher); end with the
bridge-report/v1 envelope as the final two lines.
