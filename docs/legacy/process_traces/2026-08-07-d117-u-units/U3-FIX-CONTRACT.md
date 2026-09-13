WRITE_SCOPE: ["scripts/mint_floor_artifact_generalized.py","scripts/floor_mint_pinsets/schema_v2.json","joulewise/detection_floor.py","tests/test_mint_floor_artifact_generalized.py"]

FIX ROUND — U3 pinset v2 / multi-cell mint. Close ALL findings from the two audits
custodied in this worktree's session (the reports are supplied below by reference:
the contract-lens findings 1-6 and the execution-lens findings). No scope creep; if a
fix genuinely needs another file, early-return NEEDS_SCOPE. Do NOT commit. Named
decisions (D-082/D-084/D-095/D-102/D-110/D-117) and the DESIGN-MEMO win over this
prompt; report conflicts rather than forcing.

FIX-1 (contract F1 CRITICAL + exec P0 — lead-dictated shape): postcollection pins
become AUTHENTICATED, not self-attested. The mint must take the actual evidence
artifacts (ledger snapshot, bracket-binding record, extraction report) as inputs and
COMPARE every pinned receipt id/content digest, binding hash, terminal head,
extraction-report hash, observed_drift_s, and applied_allowance_s against them;
any mismatch refuses with a named reason. Regression: reproduce the auditor's exact
fabrication scenario (all hashes replaced + drift/allowance tampered + self-hashes
repaired) and assert refusal.

FIX-2 (contract F2 HIGH): remove internal six-decimal literal DERIVATION from the v2
path — no format(value, ".6f") on computed maxima anywhere in the v2 mint. The
comparison targets come from the authenticated extraction report's recorded values;
the pinset-supplied literal is compared to those by exact string equality. The v1
core stays byte-untouched (parity). Regression: a v2 mint where the supplied literal
disagrees with the extraction-recorded value at the last decimal must refuse, and no
code path in the v2 mint may produce the expected literal itself (add a test that
monkeypatch-poisons format/round in the mint module namespace during a v2 mint and
proves success does not depend on them, or an equivalent structural assertion).

FIX-3 (contract F3): add the D-082 per-component consumption-semantics pin to
schema_v2 (both stages as appropriate) and enforce it at mint.

FIX-4 (contract F4): every desk-frozen inventory field that is parsed must be BOUND
(compared against evidence or against the final pinset's corresponding value);
fields intentionally informational must be explicitly marked so in the schema
description AND excluded from the mintable-requirements claim.

FIX-5 (contract F5): aggregate transport allowlists must be verified consistent with
each component cell's allowlist (condition-family hashes included); contradiction
refuses. Regression: the auditor's aggregate-vs-cell mismatch scenario.

FIX-6 (contract F6): add full-precision absolute/comparative/operative value pins
(exact decimal strings) alongside the six-decimal literals, per the memo's
postcollection list; mint verifies mutual consistency (six-decimal is the .6f
rendering of the full-precision pin — comparison by string, computed by the PINSET
AUTHOR not the mint; the mint checks consistency against the extraction report's
recorded renderings).

FIX-7 (exec lens): (a) the allowance-count declarative field must not be bypassable
with True/truthy values — strict type+value validation; (b) replace the synthetic
hash-freezing helper in tests with an independent golden fixture whose expected
hashes are literal constants in the test file (hand-derived), so the happy path has
an oracle independent of the implementation; (c) extend the aggregate/component
mismatch tests to cover contradictory aggregate allowlists and false evidence hashes.

Evidence: run the focused suite + the shared-caller regression set
(test_detection_floor, test_analysis_claims, test_analysis_integration) + the FULL
suite unpiped; report exact tails + exit codes. Report per-FIX status, deviations,
and lead double-checks as your FINAL MESSAGE.
