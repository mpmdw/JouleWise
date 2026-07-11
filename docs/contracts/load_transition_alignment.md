# PROVISIONAL load-transition marker/sample alignment

Status: frozen P2-046A fixture harness and P2-046B operator handoff. Part B
has **not** been executed. No fixture result in this contract validates,
tightens, widens, or replaces a P2-038 physical interval-support bound.

Authority: hardening adjudication C6, the P2-046 queue row, and
`docs/specs/c027/p2-038_production_uncertainty_evidence.md` §5. P2-038’s
per-run first/last interval-support bounds remain authoritative unless a later
lead-controlled P2-046B run is reviewed and adjudicated.

## Frozen design

The manifest is
`configs/calibration/p2_046_load_transition/manifest.json` with schema
`joulewise.load_transition_manifest.v1`. It freezes four two-transition
blocks. Blocks 1 and 3 use idle→load then load→idle; blocks 2 and 4 reverse
that order. Every transition is an independently stabilized cell with the
manifest’s named precondition. Missing, extra, reordered, or direction-changed
transition identities are refused.

For transition `i`, the observation contains a controller marker `M_i`,
powermetrics-derived averaging supports `[S_i,start, S_i,end]`, and declared
stable-state plateau samples. The analyzer derives:

```text
low_i       = median(declared stable low-state samples)
high_i      = median(declared stable high-state samples)
threshold_i = (low_i + high_i) / 2
```

At least two plateau samples are required for each state. A response is the
first sample of two consecutive samples on the target side of the threshold,
with a real baseline-state sample ending no later than the marker. For
idle→load the target is `power >= threshold`; for load→idle it is
`power <= threshold`.

Let `a_i = S_i,start - M_i` and `b_i = S_i,end - M_i`. The frozen artifact
arithmetic is:

```text
offset_i                 = (a_i + b_i) / 2
center_direction         = median(offset_i within direction)
residual_i               = offset_i - center_direction
transition_bound_i       = max(abs(a_i), abs(b_i))
direction_bound          = max(transition_bound_i within direction)
conservative_bound       = max(direction_bound)
```

“Conservative” is limited to the observed response-sample support endpoints.
It is not a confidence interval, tolerance interval, scheduler bound, or
reusable production constant. Directional residuals are descriptive
diagnostics only.

## Observation schema

`joulewise.load_transition_observations.v1` has these exact top-level fields:

| Field | Rule |
|---|---|
| `schema_version` | Exact schema identifier above. |
| `observation_set_id` | Non-empty stable identifier. |
| `manifest_id` | Must exactly match the frozen manifest. |
| `evidence_status` | `PROVISIONAL_FIXTURE_ONLY` or `PROVISIONAL_REAL_MAC_UNADJUDICATED`. |
| `source` | Exact `capture_class`, `raw_samples_sha256`, and `markers_sha256` record. Fixture hashes are null; real-Mac hashes are required lowercase SHA-256 values. |
| `transitions` | Exactly the eight planned transition IDs, with no duplicates or extras. |

Each transition repeats its frozen `transition_id`, `block_id`,
`execution_index`, `position_in_block`, and `direction`; adds finite
`marker_epoch_s`; supplies `low_plateau_samples_w` and
`high_plateau_samples_w`; and supplies ordered, non-overlapping, positive-width
sample records with `interval_start_s`, `interval_end_s`, and
`mean_power_w`. Power must be finite and nonnegative.

The `source` hash record binds the normalized observation file to the retained
raw sample and marker evidence. It does not make the normalization correct by
itself; Part-B review must recheck it against those immutable inputs.

## Artifact schema

The analyzer emits
`joulewise.load_transition_alignment_artifact.v1`. The module validator
enforces exact top-level and transition keys, finite arithmetic, plateau
midpoint, support midpoint, residual, per-direction medians/maxima, global
maximum, source hashes, and the content-addressed `artifact_id`.

| Block | Contents |
|---|---|
| Identity/status | `artifact_id`, `schema_version`, provisional `evidence_status`, and `claim_disposition`. |
| Provenance | Frozen manifest ID and byte SHA-256; observation schema, ID, byte SHA-256, and raw/marker source hashes. |
| Method | The complete frozen analysis block copied from the manifest. |
| `transitions[]` | Marker, derived low/high plateau medians and threshold, selected response sample, support endpoints relative to marker, offset, direction center, residual, and per-transition conservative support bound. |
| `direction_summaries[]` | Direction, `n`, median center offset, maximum absolute residual, and direction bound. |
| `conservative_bound` | Overall value, exact definition, fixture-support coverage scope, and P2-038 disposition `UNASSESSED_PENDING_P2_046B_QUIET_MAC`. |
| `limitations[]` | Mandatory fixture/coverage/non-replacement warnings. |

Fixture artifacts must say `PROVISIONAL_FIXTURE_ONLY` and
`NO_PHYSICAL_BOUND_CONCLUSION_PART_B_NOT_EXECUTED`. Real-Mac inputs remain
`PROVISIONAL_REAL_MAC_UNADJUDICATED`; their artifacts say
`PROVISIONAL_PHYSICAL_BOUND_REVIEW_REQUIRED`. The analyzer has no state that
can emit an adjudicated physical conclusion.

Stable refusal codes are:

| Code | Meaning |
|---|---|
| `manifest_schema_invalid` | Frozen manifest shape or method changed. |
| `observations_schema_invalid` | Observation/header/source schema invalid. |
| `manifest_mismatch` | Observation names another manifest. |
| `transition_set_mismatch` | Planned transition is missing or an extra is present. |
| `transition_malformed` | Identity, plateau, sample number, ordering, interval, or value invalid. |
| `transition_not_observed` | No baseline bracket or no persistent target response. |
| `artifact_schema_invalid` | Output shape, arithmetic, provenance, or identity fails re-derivation. |

Rendering uses UTF-8, sorted JSON keys, two-space indentation, forbidden NaN,
one terminal LF, no timestamps, and no output paths. Writes are atomic.

## Part-B operator runbook — `[QUIET-MAC]`, not executed

This section is a future handoff, not permission to run Part B from an agent
bridge.

1. The lead must open a clean, lead-controlled quiet-machine session with no
   Codex, Claude, build, indexing, or unrelated workload activity. Recheck the
   active stop card, P0-003 backup readiness, P2-038 landing state, thermal
   readiness, and free space. If those gates are not satisfied, stop.
2. Record the frozen manifest’s byte SHA-256 before collection. Do not edit the
   execution order, analysis fields, transition count, threshold rule, or
   persistence rule after observing data. A necessary design change requires a
   new manifest/schema version and a fresh run.
3. Using the lead-approved real powermetrics capture path and controlled load
   transition process, execute the eight standalone rows in exact manifest
   order. Stabilize the named precondition before each row. Retain the raw
   sample stream and a separate marker log immutably. This is the only step
   that may launch powermetrics or generate load, and it belongs exclusively
   to P2-046B.
4. Normalize the retained data into the observation schema. Sample endpoints
   must use the P2-038 current-era reconstruction; marker epochs must come from
   the captured controller markers. For each transition, declare at least two
   uncontaminated stable samples from each state for the plateau arrays. Record
   byte SHA-256 values for both retained raw sources. Set status to
   `PROVISIONAL_REAL_MAC_UNADJUDICATED`.
5. Review the normalized JSON against both raw sources before analysis. Reject
   contamination, reordered cells, missing transitions, missing plateau
   support, ambiguous ownership of a marker, or any sample interval not
   reproducible from the retained capture.
6. Run the offline analyzer twice into different output paths:

   ```sh
   python3 scripts/characterize_load_transition.py \
     --manifest configs/calibration/p2_046_load_transition/manifest.json \
     --observations /path/to/provisional-real-mac-observations.json \
     --output /path/to/provisional-alignment-1.json
   python3 scripts/characterize_load_transition.py \
     --manifest configs/calibration/p2_046_load_transition/manifest.json \
     --observations /path/to/provisional-real-mac-observations.json \
     --output /path/to/provisional-alignment-2.json
   cmp /path/to/provisional-alignment-1.json /path/to/provisional-alignment-2.json
   ```

7. Require byte identity, a valid content-addressed artifact ID, all eight
   transitions, both direction summaries, immutable source hashes, and no
   refusal. Back up the raw sources, normalized observations, frozen manifest,
   artifact, command log, and verification log before interpretation.
8. Lead review compares every response support and the overall provisional
   bound with the matched P2-038 per-run first/last interval-support evidence.
   The review must explicitly choose one of: P2-038 conservative support is
   provisionally supported for the tested stack; evidence requires widening;
   or the characterization is inconclusive. Direction/sequence dependence,
   threshold sensitivity, contamination, missing brackets, or a bound near the
   decision boundary force the inconclusive outcome.
9. Only an adjudicated follow-up may amend P2-038. Never copy the fixture’s
   `4 s` hand-math value into production metadata or physical claims.

## Part-A fixture verification

`tests/fixtures/p2046/README.md` contains the hand arithmetic. The fixture
analyzer yields direction centers `2 s` and `1 s`, maximum absolute residual
`1 s` for each direction, direction bounds `4 s` and `3 s`, and overall
fixture-only bound `4 s`. Two identical invocations must produce byte-identical
artifacts. These numbers prove the implementation arithmetic only.
