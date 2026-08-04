```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "blocked",
  "completion": "complete",
  "summary": "F1 is D-102-determined; F2 has a four-module direct estimator boundary requiring ratification; F3 needs a ruling on the authoritative cross-root observation scope.",
  "workspace": {
    "base_requested": "a14d1fe",
    "base_mode": "exact",
    "head_start": "a14d1fe189734a9a58035736becb75612a85a157",
    "head_end": "a14d1fe189734a9a58035736becb75612a85a157",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [],
  "unowned_dirty": [
    "joulewise/analysis_engine/claims.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/whole_window.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_reduce.py",
    "tests/test_whole_window_selection.py",
    "configs/calibration/calibration_acceptance_d079_v2.json",
    "tests/verify_calibration_acceptance_corpus.py"
  ],
  "verdict": {
    "overall": "two implementation corrections identified; two design boundaries require lead ratification",
    "rows": [
      {
        "id": "F1",
        "action": "start_now",
        "wait_for": "",
        "collision_surface": "Separate six-field freshness-trigger candidates from full-T1 bracket-selection candidates in calibration_bracketing.py."
      },
      {
        "id": "F2",
        "action": "needs_ruling",
        "wait_for": "Lead ratification of the four-file semantic estimator bundle.",
        "collision_surface": "ESTIMATOR_CODE_PATHS, acceptance artifact estimator_code_sha256, derivation digest, and outer artifact pin."
      },
      {
        "id": "F3",
        "action": "needs_ruling",
        "wait_for": "Lead chooses the authoritative observation scope and authenticated completeness mechanism.",
        "collision_surface": "Candidate discovery API, every production caller, acceptance artifact schema, and prospective-trigger evidence."
      },
      {
        "id": "PIN",
        "action": "wait_for",
        "wait_for": "F2/F3 artifact-schema decisions.",
        "collision_surface": "Atomic reviewed update of artifact bytes, derivation_sha256, estimator digests, and DEFAULT_ACCEPTANCE_BOUND_SHA256."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "nl -ba /Users/edr/code/JouleWise/docs/decision_log.md | sed -n '6295,6305p'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "6295 2. Freshness = exact identity epoch, no calendar hard expiry",
          "6299 Mandatory prospective re-derivation triggers: any identity-field change; protocol/estimator byte change; a new valid same-identity calibration expanding the observed range; corpus doubling (19→38); a new systematic failure challenging the pre-flight screen.",
          "6302 A trigger observation is judged under the PRIOR artifact — never incorporated into a threshold that judges itself."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Freshness = exact identity epoch.*Mandatory prospective.*PRIOR artifact"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B - <<'PY'\nfrom tests.test_calibration_bracketing import CalibrationBracketingTests as T\nfrom joulewise.calibration_bracketing import ACCEPTANCE_IDENTITY_FIELDS,evaluate_calibration_bracket\nt=T();t.setUp();other=dict(t.bindings);other['mlx_version']='same-epoch-different-t1';cs=[t.candidate('same-epoch-range-expander',99,'0.022',bindings=other),t.candidate('current-pre',199,'0.025'),t.candidate('current-post',211,'0.026')];r,x=evaluate_calibration_bracket(cs,window_start_s=200,window_end_s=210,bindings=t.bindings,policy=t.policy);print(r['status'],x,r['acceptance']['freshness']['status'],r['acceptance']['prospective_rederivation']['observed_triggers']);print(all(other[k]==t.bindings[k] for k in ACCEPTANCE_IDENTITY_FIELDS))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "passed () fresh []",
          "True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "passed \\(\\) fresh \\[\\].*True"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "shasum -a 256 joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py configs/calibration/calibration_acceptance_d079_v2.json; git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "21ec17c7b2119e5971e6bcf39d9291d907db347ab6aa63996b13a83630e437a3  joulewise/powermetrics_fiducial.py",
          "77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7  joulewise/uncertainty_evidence.py",
          "7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca  joulewise/adapters/powermetrics.py",
          "5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615  joulewise/reduce.py",
          "9a03e5810862a96544b9051926f7b80c02c7a197523d3f758cfe29c28e19050e  configs/calibration/calibration_acceptance_d079_v2.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "powermetrics_fiducial.py.*uncertainty_evidence.py.*adapters/powermetrics.py.*reduce.py.*calibration_acceptance_d079_v2.json"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/cal-bracket-d079",
          "M joulewise/analysis_engine/claims.py",
          "M joulewise/calibration_bracketing.py",
          "M joulewise/whole_window.py",
          "M tests/test_calibration_bracketing.py",
          "M tests/test_reduce.py",
          "M tests/test_whole_window_selection.py",
          "?? configs/calibration/calibration_acceptance_d079_v2.json",
          "?? tests/verify_calibration_acceptance_corpus.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "impl/cal-bracket-d079"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "D-102 mandates estimator-byte freshness but does not enumerate or define the estimator dependency boundary.",
      "needs": "Ratify the recommended four-module semantic bundle."
    },
    {
      "id": "R2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "D-102 does not define the authoritative candidate universe, observation roots, registry, or completeness proof.",
      "needs": "Adopt an authenticated observation registry/snapshot contract or explicitly narrow D-102 in a new decision."
    },
    {
      "id": "R3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A caller boolean, an unauthenticated list, or a recorded single-root scope does not prove that no cross-root trigger exists.",
      "needs": "Bind completeness to authenticated evidence and fail closed when it cannot be established."
    }
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| F1 | start_now | — | Freshness/selection predicates and collision-safe corpus membership |
| F2 | needs_ruling | Ratify four-module bundle | Artifact estimator map, derivation digest, outer SHA pin |
| F3 | needs_ruling | Choose observation authority/scope | Discovery API and every production caller |
| PIN | wait_for | F2/F3 schema settled | Atomic artifact-and-code-pin rotation |

## Critical path

F1 is independent and can be corrected immediately. F2 requires one narrow boundary ratification before regenerating the artifact. F3 is the controlling blocker: the artifact schema and production API should not be finalized until the observation authority is ruled. The byte pin rotates last, atomically with all accepted artifact changes.

## F1 — six-field freshness identity versus full-T1 selection

### What D-102 determines

> “Freshness = exact identity epoch” and the artifact binds `{os_build, hardware_model, power_policy, sampling_interval_ms, estimator_revision, pulse_protocol_id}`.

It then names “a new valid same-identity calibration expanding the observed range.” In that clause, “same-identity” refers to the immediately defined six-field identity epoch. The proposed interpretation is therefore confirmed.

Full-T1 selection remains separately governed by the registered transfer contract:

> “A claim-bearing collection requires two independently authenticated, T1-matching artifacts.”

T1 includes hardware, OS, powermetrics binary, MLX version, sampling policy, anchor method, pulse protocol, power policy, estimator revision, and protocol digest.

### Where D-102 is silent

D-102 does not restate T1 endpoint-selection eligibility or prescribe code layout. That is not an unresolved policy choice because the existing fiducial contract settles it. No F1 ruling is required.

D-102 also does not prescribe how a “new” calibration is keyed. The current basename-only comparison at `calibration_bracketing.py:658-677` is unsound: a different authenticated capture that reuses a member ID must not disappear. Use a content identity, not a directory basename.

### Minimal design

Create two explicitly named sets after candidate authentication:

- `same_epoch_candidates`: protocol-v3 candidates matching exactly `ACCEPTANCE_IDENTITY_FIELDS`. Use this set only for prospective range expansion, corpus doubling, and relevant systematic-trigger observation.
- `t1_selectable_candidates`: the subset matching every `V2_BINDING_FIELDS` field. Use this set for 24-hour causal filtering and latest-pre/earliest-post selection.

Concretely:

- Replace the single `matching` comprehension at `calibration_bracketing.py:643-651` with the two predicates.
- Move corpus-doubling and range-expansion checks at lines 658-681 onto `same_epoch_candidates`.
- Keep causal/horizon/endpoint selection at lines 682-708 on `t1_selectable_candidates`.
- Represent baseline membership with at least `(member_id, manifest_sha256, evidence_sha256, b_fiducial_decimal_s)`. An authenticated candidate with the same basename but different content is new; identical copied content is not double-counted.

### Fix-round acceptance predicate

The fix passes only if all are true:

1. A range expander matching the six epoch fields but differing only in `mlx_version` returns `calibration_acceptance_bound_stale` with `new_valid_same_identity_capture_expands_observed_range`.
2. The different-MLX expander is never selected as `pre` or `post`; the ordinary full-T1 pair remains the endpoint pair recorded in the failed result.
3. A same-epoch, non-expanding, different-T1 candidate neither becomes an endpoint nor independently stales the artifact before the doubling threshold.
4. Candidates differing in a six-field epoch value do not enter that artifact’s same-epoch range/doubling set.
5. A range expander reusing a pinned member basename but carrying different authenticated hashes/value is treated as new and stales.
6. Corpus doubling counts unique content identities from the six-field epoch set, not full-T1 eligibility or basename aliases.

## F2 — estimator byte-digest boundary

### What D-102 determines

> “protocol/estimator byte change” is a mandatory prospective re-derivation trigger.

Thus the check must bind actual source bytes, not merely `estimator_revision`.

### Where D-102 is silent

D-102 does not enumerate modules or say whether “estimator” means a semantic ownership boundary or every transitive helper/import.

**NEEDS_RULING:** ratify the semantic boundary below. The factual direct call graph yields an exact four-module closure; adopting that boundary as policy is the small new design choice.

### Definitive minimal module set

| Module | Why it is in |
|---|---|
| `joulewise/powermetrics_fiducial.py` | `rederive_detection_from_artifacts` parses primary evidence and calls the anchor estimator and pulse detector (`931-1085`); `detect_pulses` computes `max(residual edges) + trace_anchor_bound_s` (`825-884`); `verify_stored_evidence_physics` returns `max(stored, freshly rederived)` (`1088-1164`). |
| `joulewise/uncertainty_evidence.py` | `derive_powermetrics_anchor_v2` computes the admissible anchor and `effective_clock_anchor_bound_s` (`292-438`), which is the additive term supplied to `detect_pulses`. |
| `joulewise/adapters/powermetrics.py` | `parse_powermetrics_records` and `_parse_powermetrics_records` derive interval endpoints, elapsed durations, and rail powers from raw plist bytes (`1695-1823`); `anchor_records_from_powermetrics` projects those records into the anchor estimator (`1826-1847`). |
| `joulewise/reduce.py` | Authenticates/rederives member calibration, accepts the governed wider override, composes bundle/fiducial/edge bounds (`1171-1695`, `1698-1718`, `1721-1845`), and reruns the anchor-energy envelopes through `_rederive_summary_for_authenticated_fiducial_bound` (`2695-2726`, `3171-3215`). |

The complete recommended tuple is therefore:

`joulewise/powermetrics_fiducial.py`  
`joulewise/uncertainty_evidence.py`  
`joulewise/adapters/powermetrics.py`  
`joulewise/reduce.py`

Current hashes for the two missing leaves are:

- `uncertainty_evidence.py`: `77412d194bb43c7ffc37339131591e12170371d83d60449ecbd1a3e879c988c7`
- `adapters/powermetrics.py`: `7380eea85fed2c51034acdbf71bdaa474c8dc4053fc2a1b86a84c05b301947ca`

### Boundary: why adjacent modules are out

- `calibration_bracketing.py` owns D-102 acceptance policy, trigger evaluation, and allowance composition, not the physical fiducial estimator or anchor-envelope reducer. Its ratified decimal constants and artifact arithmetic are validated separately.
- `whole_window.py` orchestrates selection and invokes the reducer seam; it does not implement pulse fitting, trace-anchor derivation, raw parsing, or envelope math.
- Protocol JSON is already bound separately through `protocol_sha256`.
- Capture scripts author evidence but are not used by claim-time primary-byte rederivation.
- Generic representations and admission helpers such as `clock.py`, `validation.py`, `bundle_read.py`, schemas, and environment checks lie outside the recommended semantic estimator ownership boundary. Treating every transitive helper as “estimator bytes” would require a broader dependency-lock policy that D-102 did not adopt.

### Fix-round acceptance predicate

1. `ESTIMATOR_CODE_PATHS` and artifact `estimator_code_sha256` have exactly the four keys above.
2. A one-byte change to each module independently causes artifact loading/evaluation to fail closed as `calibration_acceptance_bound_stale`.
3. Restoring all four exact bytes makes the artifact load.
4. Tests vary each leaf independently; a single mocked mapping containing all wrong hashes is insufficient.
5. The regenerated artifact recomputes `derivation_sha256` over the four-entry map and then recomputes the outer file SHA pin.
6. The selector-to-real-reducer regression still proves exactly one allowance embedding and real anchor-envelope re-reduction.

## F3 — cross-root trigger observation

### What D-102 determines

> Mandatory triggers include “a new valid same-identity calibration expanding the observed range; corpus doubling (19→38); [and] a new systematic failure challenging the pre-flight screen.”

> “A trigger observation is judged under the PRIOR artifact — never incorporated into a threshold that judges itself.”

These requirements do not become optional because a production caller happens to inspect one directory. The artifact itself demonstrates cross-root provenance: its 19 members span `runs_window_a_20260722` through `runs_window_a10_20260725`, while current discovery scans only `runs_root/instrument_validation` at `calibration_bracketing.py:508-519`.

Therefore:

- D-102 requires observation over an authoritative universe sufficient to establish whether mandatory triggers occurred.
- It does not specifically mandate a global filesystem scan.
- A within-window-only pass is not defensible unless a new decision explicitly declares that window root to be the complete authoritative universe. That would narrow D-102.

### Where D-102 is silent

**NEEDS_RULING:** D-102 does not define:

- the authoritative calibration universe;
- which roots or custody stores belong to it;
- how completeness is proved;
- whether attempts/failures must be registered;
- the registry or snapshot authentication mechanism;
- retention and high-water semantics.

No such calibration registry exists in the inspected implementation. The acceptance artifact is a pinned baseline corpus, not an append-only observation authority.

### Recommended minimal sound design

Adopt an authenticated calibration-observation registry/snapshot contract rather than a global filesystem sweep.

The registry should contain every authenticated protocol-v3 observation in the declared scope, including valid captures and authenticated systematic failures. Each entry should bind:

- six-field identity epoch;
- full T1 bindings;
- capture time;
- member/content identity;
- manifest and evidence hashes;
- exact bound lexeme when derivable;
- validity/systematic disposition;
- source locator;
- monotonic registry sequence or hash-chain predecessor.

The acceptance artifact should bind:

- `observation_scope_id`;
- its baseline registry generation/high-water mark;
- the exact baseline content-fingerprint set or registry root digest.

At evaluation:

1. Authenticate the current registry snapshot.
2. Require the artifact baseline set `A` to be a subset of current snapshot `O`.
3. Refuse stale/incomplete if `A ⊄ O`, the snapshot is unauthenticated, the scope differs, the history is non-prefix, or completeness is not established.
4. Judge every entry in `O − A` under the prior artifact.
5. Stale on range expansion, corpus doubling, or systematic-screen challenge.
6. Permit an in-range addition below doubling only if the authoritative snapshot is complete.

This is fail-closed without a global scan.

A bare artifact-universe comparison is insufficient by itself. Equality or `A ⊆ supplied_candidates` cannot prove that another root was omitted. It becomes sound only when the supplied set is an authenticated, completeness-attested registry snapshot. A boolean such as `candidate_set_complete=True` is not evidence.

This requires new infrastructure, although it can be small: one versioned registry artifact, one authenticator/reader, capture-workflow append discipline, and one mandatory registry argument or internal load path shared by every production caller.

### Fix-round acceptance predicate

1. Register an expander in root A; evaluating a normal pair in root B must stale under the prior artifact.
2. Reaching 38 unique same-epoch content identities across roots must stale.
3. A registered systematic failure must trigger re-derivation even when it is not endpoint-selectable.
4. Missing, truncated, non-prefix, wrong-scope, or tampered registry snapshots must refuse.
5. A snapshot missing any pinned baseline member must refuse.
6. A complete authenticated snapshot equal to the baseline may pass.
7. A complete authenticated superset with only in-range additions and total count below 38 may pass.
8. Basename reuse with changed authenticated content is a new entry.
9. `whole_window.py`, its secondary verifier path, and `scripts/run_campaign.py` must consume the same authenticated snapshot; no production caller may silently fall back to local-root discovery.
10. Calling the claim-bearing path without a registry/completeness proof must return `calibration_acceptance_bound_stale`.

## File-based byte pin and legitimate re-derivation

FIX-3 option (a) is compatible with all three repairs.

The current trust path is:

- hard-coded checked-in file SHA at `calibration_bracketing.py:43-45`;
- byte comparison at `300-319`;
- explicit mappings must equal the authenticated pinned document at `323-331`.

A legitimate re-derivation is intentionally a reviewed repository update, not runtime self-authorization. Its atomic update sequence is:

1. Judge new observations under the prior artifact.
2. Rebuild the corpus/registry-derived fields.
3. Update the four estimator digests and protocol digest as applicable.
4. Recompute `derivation_sha256`.
5. Serialize the checked-in artifact.
6. Compute its file SHA-256 and update `DEFAULT_ACCEPTANCE_BOUND_SHA256`.
7. Update fixed corpus-verifier expectations where the corpus changed.
8. Run the artifact validator and trigger regressions at the same final head.

During any partial update, loading fails closed. Once artifact bytes and the checked-in SHA are updated together, `load_calibration_acceptance_bound()` has a valid authorization path. The pin therefore prevents self-rekeying without preventing legitimate reviewed rotation.