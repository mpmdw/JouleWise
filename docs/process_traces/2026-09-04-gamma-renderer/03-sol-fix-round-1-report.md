# Gamma renderer — Sol fix round 1 report (2026-09-04)

## Status

`NEEDS_RULING`; implementation did not begin. HEAD was the required
`4043d8b9e527d27e59716c9d7abb40e1b43df541`, and the worktree was clean at
intake.

## Blocking ruling conflict

The contract refuter's S2 shows a direct conflict between R2 and registered
production contracts. The assignment requires an immediate `NEEDS_RULING`
return when a finding exposes such a conflict.

- R2 at
  `docs/process_traces/2026-09-04-paper-i/06-magistrate-contract-rulings.md:15`
  says: “required sibling `claim_side_bound` in
  `joulewise.claim_verdicts.v2`; v1 unchanged; the producer emits v2 from now
  on with a v1 compatibility path only for reading.”
- The claims-ladder contract at `docs/contracts/claims_ladder.md:21-25` says
  current rows are linked to “a governed `joulewise.claim_verdicts.v1`
  artifact” and rejects unknown or mixed authority fields.
- The registered production flow at `docs/process/v5-artifact-flow.md:23`
  declares the claim-gate output to be `joulewise.claim_verdicts.v1`, while
  line 32 says no v1 claim-verdict-to-results-fill adapter exists and assigns
  that edge to `RENDERER-V5-SUCCESSOR-01`.

Question: should this fix round (A) supersede the registered v1 production
contracts and connect v2 through the publication edge, with explicit expanded
write scope, or (B) keep gamma v2 explicitly non-production and amend R2's
“from now on” producer requirement to preserve the registered v1 production
path?

Options considered: A honors R2 as written but needs coordinated edits to the
registered contracts and executable consumer outside this seat's write scope;
B preserves the current registered production path but changes the adopted
ruling and leaves this seat as a fixture-only successor.

Recommendation: A, because it preserves Q-R2-2's adopted current-producer
semantics and removes the split authority before implementation.

Blocked work: every refuter cure and its required red-then-green regression.
The stop precedes implementation so no partial contract is introduced.

## Additional scope blocker

- Execution refuter B4 → cure: refresh the intentional producer golden pins →
  `tests/test_analysis_integration.py:1578`. That path is not in the exhaustive
  `WRITE_SCOPE`; if option A is chosen, the resumed assignment must add this
  exact path so B4 can be cured and its named producer tests can go red then
  green.

## Finding-to-cure disposition

- Execution B1 / Contract B1-B4 and S1 → cure not attempted → blocked by the
  authority conflict above before edits to the authorized implementation,
  validator, tests, registry, or guide.
- Execution B2-B3 and S1 → cure not attempted → same ruling stop.
- Execution B4 → golden-pin refresh not attempted → out-of-scope
  `tests/test_analysis_integration.py:1578`.
- Contract S2 → cure requires the ruling above and, for option A, scope for at
  least `docs/contracts/claims_ladder.md`,
  `docs/process/v5-artifact-flow.md`, and
  `scripts/render_results_fills.py` at the refuter-cited v1 refusal/entry
  points.

## Verification

No tests were run after detecting the mandatory ruling stop. Consequently no
red-then-green transcript exists; presenting the refuters' red evidence as a
completed regression would be misleading.
