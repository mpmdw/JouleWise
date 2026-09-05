# Sol fix round 4 — PAPER-CUSTODY-SEAM-01

Date: 2026-09-04. Implementation seat: Sol, xhigh. Start HEAD:
`a443f61823c58a1758f713f18f5e1741403ac01f`. Branch:
`feat/2026-09-04-paper-custody-seam`. No commit, push, hardware run, or
quiet-machine measurement was performed.

## Outcome

G1/G2 and C-02 through C-06 from `08-opus-counter-review.md` are cured.
The D-165 producer derives refusal causes from operands, funnels every emitted
`refusal_reason` through the closed enumeration, validates membership, and
uses the cause-neutral `closeout_input_malformed` only for an unknown
independent-record stop. A counterfactual rewording of the zero-denominator
exception still produces `dominance_ratio_zero_denominator` in both the real
record and close-out global field.

The authentication AST surface now names the custody seam and all seven
supplier/analysis modules, including the two modules missed by ruling 16.1. All 12
direct reads in `analysis_engine/inputs.py` and 22 of 25 in
`analysis_manifest_v3.py` route through the active authentication session. The
remaining three manifest sites are lint-recorded exemptions with individual
reasons: append-only output idempotence, the locked repeat of that writer-state
check, and a parent-directory fsync descriptor. The enforced census is now 34
routed + 3 explicit exemptions, not 37 unlinted reads.

`CustodyEvidence` and every `Verified*` type are slotted, frozen capabilities.
Direct constructors refuse; access to an `object.__new__` forgery refuses; and
the only mint functions require a token captured inside the private seam
closure. Each authentic evidence value now carries the authorizing
`anchor_head` and exact `supply_map_sha256`.

The paper release call requests strict `origin/main` containment; false or
unknown containment refuses. Generic identity-pin callers retain their
existing non-release behavior. The seam exposes no containment or fixture
override. Fixture tests replace the private anchor only for map-pinned,
non-issuing fixture inventories.

The full-reseal test now coherently reseals the selected runs-root input,
receipt, and inventory, then re-pins only the fixture inventory envelope in a
new synthetic anchor commit. That reaches the inventory-row-versus-map binding
check and returns `paper_custody_anchor_mismatch`. The redundant post-read
digest comparison formerly at `paper_custody.py:1117-1126` was deleted as
unreachable.

The normative contract now enumerates all 16 reachable refusal codes and their
conditions. The unused `paper_custody_derivation_mismatch` and
`paper_custody_identity_not_v5` declarations were deleted. A test requires the
code set, contract backtick registry, and raise-site reachability census to
agree.

## Trace-code correction for 01/02

The claims in `01-seat-landing-report.md` rows 26–30 and
`02-refuter-execution.md` line 72 must not be read as evidence of what their
original reseal test executed. At their audited head, that test changed
runs-root bytes while leaving the Git-map inventory pin unchanged, so the
observed code was `paper_custody_digest_mismatch`, not their claimed
`paper_custody_anchor_mismatch`. Round 4 did not edit those historical traces.
It changed the test construction described above; the new execution now
actually observes `paper_custody_anchor_mismatch` at the inventory-versus-map
gate. Thus the claimed code is the correct intended/resulting code, but only
this report and the round-4 test are valid execution evidence for it.

## N-2 ruling

Untracked non-governed files are **not ignored**. Paper supply is a release
operation, so the fixed checkout must be wholly clean; an operator must commit,
ignore, or remove scratch material before issuance. This avoids a second,
policy-sensitive definition of “governed path” that could drift from the Git
supply map. `test_real_anchor_refuses_untracked_nongoverned_file_without_mocking`
creates an untracked markdown-adjacent probe in this trace directory, invokes
the real fixed-checkout anchor without mocking, observes
`readiness_identity_environment_dirty`, and removes the probe in `finally`.

## Red-then-green evidence

| Item | Red | Green |
|---|---|---|
| G1/C-01 | Focused counterfactual failed: `the denominator wording changed != dominance_ratio_zero_denominator`. | Focused counterfactual passed; full D-165 module: 51 tests OK. |
| C-02 | AST guard failed with exactly 37 additional direct-read findings. | Full authentication module: 21 tests OK; zero unclassified findings. |
| C-03 | Direct `CustodyEvidence(...)` did not raise. | Capability/forgery test and full custody module passed. |
| C-04 | Evidence lacked `anchor_head`; strict-containment test accepted `False`. | Both focused tests passed; identity-pins module: 42 tests OK. |
| G2/C-05 | Dead-code assertion found the post-pin comparison. | Dead-code assertion and five-family coherent-reseal census passed. |
| C-06 | Code exposed 18 codes while the expected reachable set was 16. | Exact code/contract/reachability equality passed. |

## Verification

Commands were run one test module at a time as required by the preflight rule:

- `python3 -m unittest tests.test_paper_custody` — 15 tests, OK.
- `python3 -m unittest tests.test_authentication_io` — 21 tests, OK after
  final exemption-line refresh.
- `python3 -m unittest tests.test_d165_dominance_closeout` — 51 tests, OK.
- `python3 -m unittest tests.test_dominance_closeout` — 3 tests, OK.
- `python3 -m unittest tests.test_analysis_inputs` — 19 tests, OK.
- `python3 -m unittest tests.test_analysis_manifest_v3` — 19 tests, OK.
- `python3 -m unittest tests.test_identity_pins` — 42 tests, OK.

The repository-wide suite was intentionally not run because the prompt limits
this seat to the named modules and module tests for other touched files.
