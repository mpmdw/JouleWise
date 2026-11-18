# lm-qual-01 registration

The [registration manifest](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks/lm-qual-01.manifest.json)
and [ledger row](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks/LOOKS.json)
are on `align/2026-11-18-lm-qual-01-registered` for Tier 2 review. The
registration commit is `50ffe953dc3e339c3e4f84a9b3e0960adda90911` and
the manifest's SHA-256 is
`2ca269bb0b59e29aed29a12f13dfb5d02adef1d5b615b8e1833b5ee4650f9096`.
The branch started at `origin/main` `2bb70e14379b7b82b02019674be4f1bf82f5b193`.

The location is the dispatch's fallback. PR #793 was open and main had no
look directory. RL-181 refers to the draft layout and specifies the
sibling schema name. The v2 file sits with the other schema paths under
`docs/process/cadence/looks/`. Validation is in a new qualification
module. Authority is [RL-181 at the pinned audit revision](https://github.com/mpmdw/JouleWise/blob/e964c97d8278c023319b8ef748e75f0101011ca1/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19235).

| RL-181 clause | Fields |
| --- | --- |
| §1.0, two commits and receipt order | `status`, `registration`, `reads.blocks`, `pins`, `inclusion.rules[].code`, ledger row |
| §1.1, decision series and scale | `decision.series`, `decision.scale` |
| §1.1, day-weighted interval and inclusive word | `reads.day_rule`, `decision.interval`, `decision.support`, `decision.containment`, `decision.mapping` |
| §1.1, paper wording | `paper_sentences` |
| §1.2, terminal segments and scorer equivalence | `scoring.tail_segments`, `scoring.tail_rule`, `scoring.native_short_legs`, `pins.scorer`, `scoring.equivalence` |
| §1.3, private pair description | `pair_description`, `outputs.destinations` |
| §1.4, public fields, two counted words and restrictions | `outputs.fields`, `outputs.words`, `outputs.energy_dependent_words`, `outputs.destinations` |
| §1.5, oracle, no twin and closed custody names | `oracle`, `release.twin`, `release.custody_names`, `freeze2` |
| §2.1, qualification sibling | `schema`, `look_kind`, `freeze2`, `pins.schemas.manifest` |
| §4(a), qualification hand-read | `reads.first_span_hand_read` |

Five tests in `tests.test_qualification_manifest` verify registration
and ledger binding, 32 deferred code or schema digests and three final
kit digests, a synthetic complete finalization, and rejection of
malformed hashes or mutations beyond the registered slots. The validator
compares exact bytes, including whitespace, number spelling, key order
and escaping. The registration, pointer and state checks passed 101
tests locally. A Draft 2020-12 validator accepted the schema, the
registration and the synthetic final. The PR's CI runs the repository
shards. This [AGENT] lane used public specifications and synthetic
substitutions.

The lead's next gate is Tier 2 review and admission to main before the
first qualification receipt. Before the eventual stage-2 reservation,
validate the final manifest against the registered bytes from the
registration commit. The scorer build owes the cross-family oracle and
any required predictor-equivalence record.
