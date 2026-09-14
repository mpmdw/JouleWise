# Exhibit C — decision-log text at main 1421242633769e5a2ffa25eaf51d8da9a49273fe

## D-124 (registered candidate) lines 8395–8445: round-4 zero-shift contrast, the band, and the 'not load-bearing' sentence
```
referenced roots including Q8 p256 have none yet and are asserted
absent-by-name in the committed inventory; margins are a freeze-gate
checklist item at collection.

### D-124 amendment — 2026-08-10: FCM-R4 explicit zero point, third erratum, and input-surface tolerance audit (cold-gate FINAL)

FCM-R3-01 falsified the prior errata's unconditional upper-bound sentences:
an input admitted by every coded precondition emitted
`0.09999999950000743 J` against an exact required
`0.10000000050000024 J`, an understatement of approximately
`9.9999e-10 J`. The defect had been present since the original implementation:
the sweeps' structural zero-shift contrast was recovered by `isclose` against
the separately reduced ABBA delta, conflating tolerance with identity. Those
unconditional sentences are superseded.

Round 4 makes the zero-shift contrast `z` an explicit registered input. It must
be present by exact equality in both onset and offset sweeps. Extrema are
composed as signed excursions about `z`; the emitted shared half-width adds
`|z - delta|` outward exactly once, separately from the unchanged
`64u * S_env` member-envelope pad, whose floored scale set now includes
`|z|`. A mismatch outside the existing `isclose(rel_tol=1e-9,
abs_tol=1e-12)` band refuses with
`common_mode_zero_point_divergence_out_of_domain`; this is a pure provenance
guard and is not load-bearing for soundness. The intuitive round-3 arithmetic
plus `|z-delta|` candidate was tried and refuted: it fails the independent
about-zero exact bar on FCM-R3-01 and remains a named negative regression.
Real trimmed recompute fixtures for a5 decode blocks b02 (nonzero measured
divergence) and b01 (zero divergence) are committed under
`tests/fixtures/fcm_r4_real_blocks/` within the 256 KB cap.

The registered parameter hash is
`4d1c544fe3a52148c7d379f4c50ade4ac3b64211d817cd1438a2365973291981`.
All superseded hashes (`ea4aa669...`, `9d964cfb...`, and `977189cd...`) are
rejected by regression.

**FCM-R4 input-surface tolerance audit.** These are the complete tolerance
acceptances on the registered arithmetic path. The production caller
single-sourcing statements are assumptions of the upper-bound claim; direct
callers must preserve them.

| Accepted comparison | Coded tolerance | Production single source / caller assumption | Disposition |
|---|---:|---|---|
| Sweep bound vs authenticated operative bracket bound | `rel=0`, `abs=1e-12 s` | `extract_comparative_cell` obtains `common_mode_bound_s` once from `registered_common_mode_operative_bound` and passes that exact float unchanged to the sweep builder and estimator; the authenticated session alias is checked against the same value. | No discrepancy term: production is exactly single-sourced. Direct callers assume the same identity. |
| `b_fiducial_s` vs optional `operative_b_fiducial_s` alias | `rel=0`, `abs=1e-12 s` | When both exist, arithmetic selects `b_fiducial_s`; the optional alias is redundant provenance and never supplies sweep arithmetic. | No discrepancy term: the tolerated alias is non-operative. |
| Recorded allowance string vs passed `calibration_drift_allowance_s` | `rel=0`, `abs=1e-12 s` | Production bracket construction computes one Decimal allowance, then emits its exact decimal string and binary64 projection together; arithmetic uses the binary64 field. | No discrepancy term under the single-producing-value assumption. |
| Operative bound vs endpoint plus allowance | `rel=0`, `abs=1e-12 s` | Production bracket construction computes `operative_bound = endpoint_max_decimal + allowance` once in Decimal and emits its binary64 projection as `b_fiducial_s`; the separate endpoint/allowance fields are audit projections of the same derivation. | No discrepancy term under the production-constructor assumption; externally assembled brackets assume the same derivation. |

Claims-with-assumptions correction: **over inputs constructed by the registered
builder from authenticated bundle evidence, the emitted width bounds the exact
admissible width outward, up to the disclosed member-envelope pad and the
disclosed zero-point discrepancy term, under the documented single-sourcing
```

## D-161 (threat-model prune) lines 10684–10714
```
## D-161: threat-model prune (Ed, 2026-08-27)

Index row carries the operative detail. Trace: the prune consult under
`docs/process_traces/2026-08-27-t26/threat-model-prune/` — three blind seats
+ `04-MAGISTRATE-RULING.md` (ADDENDUM, 2026-08-27 PM): the operative test is
MISTAKE vs DELIBERATE (fail-closed for physics/evidence, pre-registration and
operator mistakes; deliberate-only guards retire); the histsem pin is cured
ASYMMETRICALLY (historical-side equality stays B; current-side equality and
the delta list → warn after `_v4`); HISTPACK-PROMISOR-NOFETCH-01 RETIRED
unbuilt; only the refresh lane lands before the night; the post-transaction
prune waves (a)–(f) are enumerated in the ruling; refresh lane: stream S14,
`feat/pinset-refresh-row-lane`.


## D-162: the live-proof gate, corrected (magistrate, 2026-08-28)

Index row carries the operative detail. Trace:
`docs/process_traces/2026-08-28-live-smoke/proof-consult/`.


## D-163: the week after `_v4` (magistrate, 2026-08-28)

Index row carries the operative detail. Trace:
`docs/process_traces/2026-08-28-ladder-consult/`.

**Ed 2026-08-28 evening: GO on both** — the inserted-gap fiducial owns the
first post-campaign window, and the 3-point decode-only ladder
(0.5B / 1.5B / 7B) is prepared at the desk during `_v4` (stream S15). Ed:
"keep in mind i had a list of research questions" — the registered RQs
(`docs/research_question_registry.md`, `docs/research_question_bank.md`)
are the target: the ladder answers C5-1.1 in its permitted pairwise form;
```

## D-165 (the falsifier) heading and first 25 lines (10728)
```
## D-165: the falsifier (magistrate + cold gate, 2026-08-28)

Index row carries the operative detail. Consult and cold-gate trace:
`docs/process_traces/2026-08-28-falsifier-consult/` (lands via PR #234;
cold-gate ruling `06-COLD-GATE-RULING.md`). Reverses paper-goal item 34
and amends item 28: the dominance RATIO **R ≥ 2** (per component, per
cell) is pre-registered into the `_v5` pack; the coded predicate survives
only as the cell label; common-mode R_cm is mandatory disclosure and
R_cm < 2 withdraws the dominance sentence.

**R-5 COMPLETED (magistrate, 2026-08-30):** the ruled pre-freeze bench
check ran as the PR #241 contract-lens refuter (Sol xhigh). Confirmed
with a derivation: the absolute estimator is deviations-from-mean, so a
uniform shared shift cancels exactly — an absolute R_cm is undefined
under the registered comparative replay. RULED: absolute
independent-corner R stays reportable and gated; absolute R_cm is
registered `not_applicable` with the cancellation reason; comparative
R_cm stays mandatory with the R_cm < 2 withdrawal. R-2(b)'s route choice
is (ii): a registered pre-mint replay reconstructing the shared/local
split from custodied block inputs (implemented and fixture-verified on
PR #241). Authority:
`docs/process_traces/2026-08-30-t28-v5-prep/REFUTER-ROUND-1-DISPOSITION.md`.

## D-166: the workload (magistrate, 2026-08-28)

Index row carries the operative detail. Consult trace:
```
