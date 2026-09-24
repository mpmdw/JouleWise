# CONTRACT lens (Opus 5.5): acceptance v4 + Revision 4, `53e6d23d`

**Verdict:** no BLOCKER. Three should_fix and three nits. Every clause I was asked to check is present. Two go beyond the ruling. The seat's claim that "every remaining failure is a pin" skipped one test class.

## Findings

| # | Sev | Finding | Executed witness | Cure |
|---|---|---|---|---|
| F1 | should_fix | **Historical validation changed.** `_registered_protocol_pin_matches` (`calibration_bracketing.py:291-300`) now accepts the v4 protocol pin for *every* artifact whose identity says v3, so all seven issued generations (r1–r7) accept it, not just the ruled r8. The brief asked that no historical generation's validation change. | P1: each of r1 (`_n19`), r6 and r7, with only `prospective_rederivation.protocol_sha256` set to the v4 digest and `derivation_sha256` recomputed. **Head:** `v4pin True` for all three. **Base `bce0d7df`:** `v4pin False` for all three. Unmodified artifacts are `True` at both. | Accept the v4 pin only for the r8 acceptance id, keyed on `acceptance_id` when r8 is registered. Keep v3 identity with v3 pin as the only historical path. Add a test: r6 with a v4 pin must refuse. |
| F2 | should_fix | **The futility rule is stricter than ruled.** Ruling 2(d) says "if W1's dry run reports fewer than 8 of 12 **valid**, stop". Rev 4 (prose, "Sample, stopping") and the issuer (`issue_…generation.py` +1342-1353) both count "valid **and not excluded under `affine_clock_fit_empty`**". The issuer also enforces futility at issuance, after W2 has already run; the ruling places it as a stop before W2. | Case: W1 has 8 valid, one of them later excluded under `affine_clock_fit_empty`. The ruling says run W2. The issuer then refuses the whole corpus: `W1 futility: 7 of 12`. The code path is visible in the diff; I did not execute it. | Change the text and code back to "valid", or take the stricter reading to the council for a dated ruling. The W3 criterion already uses "not excluded", which matches its own ruled text. |
| F3 | should_fix | **The pin-only failure account is incomplete.** The seat's V1 ran only the `GenerationKeyedIssuanceValidationTests` and `RevisionFourEnvelopeValidatorTests` classes of `test_calibration_bracketing`. `CalibrationBracketingTests` was never run. At head it fails 31 tests with 2 errors (unittest); pytest shows 28 failures. At base it passes (91/91). None of these are in the seat's 41-test list. Every message I sampled is `calibration_acceptance_bound_stale` or its downstream effect (`drift_s` None, empty trigger list), which is consistent with the r7 pin going stale. But these are the claim-bracket gates (missing post-bracket, drift budget, off-ledger, systematic preflight, byte-change staleness), and they stay hidden until r8. | P3 and P4 below. | Add `CalibrationBracketingTests` to the r8 re-pin verification list. Require it green after r8 and before any G2-a arm. |
| F4 | nit | The issuer detects Rev 4 by substring: `"# Revision 4 (2026-09-24" in text and "…v4" in text`. The registration digest pin (B-3) is the real seal, so this is advisory only. | Code read. | Key the check on the sealed digest, or leave it and record that it is advisory. |
| F5 | nit | Historical-epoch issuer output gains new `rule_outcomes` keys: `headroom_status: "positive_headroom"`, `excursion_member_count`, `excursion_label: null` and `estimator_lane_…: false`. This is additive, but it changes the historical output shape, which the ruling does not ask for. | Code read. | Emit these keys only when `revision_four` is true. |
| F6 | nit | Rev 4's authority line cites 2(a)–(j) and (l) but not 2(k). Rev 4 does not state that a non-zero false-claim admission in the 2(k) simulation reverts it to n ≥ 19 and three windows. | Text read. | Add one sentence carrying the 2(k) fallback. |

## Accepted clauses

- **1(a):** `protocol_v4.json` equals `protocol_definition(v4)` exactly (P5). v3 JSON also equals its own definition. `PULSE_DURATION_S = 2.0` with 1.8–2.2 s authentication. v3 authentication stays 0.8–1.2 s, routed through `authenticate_protocol_schedule(…, protocol_id)`. `SUPPORTED_PROTOCOL_IDS` includes v4. `run_bundle_layout.md:614-616` now reads "v3 or v4 59-pulse protocol". `arm_readiness.py:8138` updated. The fiducial contract doc is amended. The N2 gap note is added to v4 only.
- **2(a):** the epoch tuple and the powermetrics sha `b762e5bf…30c5` are restated. Clause 7's seal is in the "Registered epoch and seal" section.
- **2(b):** W1/W2, ≥ 6 h apart, 600 s settle, 12 slots, `window_max_s` 9000, chain re-pin all present.
- **2(c):** the issuer floor is 12, but only for the exact 25G83/v4 tuple. Historical registrations keep 19, or 17 with `--ed-ruling`, and Rev 4 refuses any other value. The validator floor is 12 only when `_is_revision_four_epoch` holds.
- **2(d):** W3 is refused if the first two windows already hold ≥ 12. Session order is enforced. The futility deviation is F2.
- **2(e):** blindness text unchanged and restated.
- **2(f):** disclosed inputs listed, plus the §3.2 anchor-failure sentence, which matches the ruling's text word for word.
- **2(g):** the screen-challenge refusal is gated `not revision_four`. The challenged count is still recorded as a diagnostic.
- **2(h):** members with B > 0.075 s are counted. A count ≥ 2 sets the `excursion_limited` label and the estimator-lane flag. B > 0.25 s refuses and names the mechanism ("exceeds one native sample interval"). Both apply to Rev 4 only, and no member is excluded on B.
- **2(i):** issuer `ceiling = max(ceiling, screen)`, and the strict S < C refusal applies only to historical epochs. `zero_headroom` is recorded. The validator's `expected_ceiling` adds S as an operand for Rev 4 only; historical rows keep strict `screen >= drift → refuse`.
- **2(j):** the audit (file 37) covers all five listed constants and adds the r6 max-plus-range diagnostic.
- **2(l):** the "Barrier basis" section matches.
- **Addenda:** the D-126 cl. 2 addendum quotes 2(c) exactly. The D-125 addendum quotes 2(i) exactly except for dropped backticks. Both are scoped to "25G83/v4 under Revision 4".
- **Revision 4 append:** the first 39,738 bytes of the new prereg are byte-identical to the base file (P6), so Revisions 1–3 are unchanged.
- **3(c):** `native_frame_cadence` is written into the window precheck dict only. It has no refusal path; the flag test covers this. The corpus reference is hash-checked and falls back to null.

## Probes (all under `/tmp/278ebc9e/v4lens-opus/`)

```
P1  PYTHONPATH=. python3 p_pin3.py        # head, then base
    head: e_v2_n19 orig True v4pin True v2pin False | …r6 … v4pin True | …r7 … v4pin True
    base: e_v2_n19 orig True v4pin False v2pin False | …r6 … v4pin False | …r7 … v4pin False
P2  registered artifacts at head: all 7 are 25F84 / v3 identity with pin 9eaf92f8…; _valid_acceptance_bound True
P3  pytest (8 touched test files) at head: "56 failed, 449 passed, 1 skipped"
    (54 on a serial re-run of the failures). 28 of the distinct failing tests are
    CalibrationBracketingTests, none of them in the 48b list.
    base: test_calibration_bracketing "91 passed, 1 skipped"
    unittest tests.test_calibration_bracketing at head: "FAILED (failures=31, errors=2, skipped=1)"
P4  test_missing_post_bracket_refuses_claim:
    ('calibration_acceptance_bound_stale',) != ('instrument_calibration_bracket_missing',)
    test_estimator_module_byte_change_stales_artifact_at_load:
    'protocol_or_estimator_byte_change' not found in []   (refused as stale before triggers are computed)
P5  protocol_definition(v4) == protocol_v4.json: True, no differing keys; v3 likewise True
P6  head -c 39738 new.md | cmp - old.md → PREFIX_BYTE_IDENTICAL
```

- **Clusters in the remaining failures:** `acceptance_artifact_stale` (derivation-only writer), `calibration_frozen_protocol_invalid / acceptance_artifact_underivable` (exits), and the D-138 E-pin tests. All are consistent with the ruled 1(c) r8 re-pin. I found no failure pointing to a different mechanism, but F3's class stays unproven until r8.
- **Mutation probes:** assigned to the EXECUTION lens, not run here. The existing tests covering those clauses are `test_twelve_does_not_issue_under_historical_v3_epoch`, `test_n12_zero_headroom_issues_and_n11_refuses`, `test_excursion_label_and_over_interval_refusal` and `test_revision_four_full_artifact_admits_twelve_and_zero_headroom`.

**Disclosure:** to get the base comparison I ran `git worktree add --detach /tmp/278ebc9e/v4lens-opus/base bce0d7df`. That wrote an entry into the shared `.git/worktrees` metadata, which is outside `WRITE_SCOPE []`. I removed it (`git worktree remove --force` plus `prune`, confirmed). Nothing in the repo was edited, and nothing under the forbidden paths was touched.
