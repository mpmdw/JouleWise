# lm-qual-01 registration

The [registration manifest](../research-audits/2026-11-10-fable/evidence/align-v4-campaign/looks/lm-qual-01.manifest.json)
and [ledger row](../process/cadence/looks/LOOKS.json)
are on `align/2026-11-18-lm-qual-01-registered` for Tier 2 review. The
original registration artifact commit was
`f3b2d79c67c30e56ce23094a329fb5a9f2eb778e`. The corrected manifest's
SHA-256 after audit round 1 is
`57ee6b131cf680a1a4bf76866e3d764961510c0b4d26254c5adaaad716d8b795`.
The branch started at `origin/main` `2bb70e14379b7b82b02019674be4f1bf82f5b193`.

The location is the dispatch's fallback. PR #793 was open and main had no
look directory. RL-181 refers to the draft layout and specifies the
sibling schema name. The v2 file and the shared ledger sit under
`docs/process/cadence/looks/`, where the draft names the ledger.
Validation is in a new qualification module.
Authority is [RL-181 at the pinned audit revision](https://github.com/mpmdw/JouleWise/blob/e964c97d8278c023319b8ef748e75f0101011ca1/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L19235).

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

The original five tests in `tests.test_qualification_manifest` verify registration
and ledger binding, 32 deferred code or schema digests and three final
kit digests, a synthetic complete finalization, and rejection of
malformed hashes or mutations beyond the registered slots. The validator
compares exact bytes, including whitespace, number spelling, key order
and escaping. The registration, pointer and state checks passed 101
tests locally. A Draft 2020-12 validator accepted the schema, the
registration and the synthetic final. The PR's CI runs the repository
shards. This [AGENT] lane used public specifications and synthetic
substitutions.

The first quick CI run refused the missing module timing. The test
map now records the 0.066 s local Python 3.13 observation from
`scripts.shard_tests.run_shard`. The shard inventory regression checks
the entry.

## Audit round 1

The audit classified one HIGH and one MED as verified on
`6ffcb3c3d`. The HIGH traced to copying the superseded kit pins
from the draft and validating their format without an independent
kit commitment check. All three replacement hashes were verified
against the pinned public table and exact prospective kit Git blobs.
The validator checks the block set, identities and digests against the
[source record](../process/cadence/looks/qualification-kit-commitments.json)
before it accepts a registration or uses it as the baseline for
finalization. The
[audit repro fixture](2026-11-18-lm-qual-01-audit-1-obsolete-kit-pins.json)
records all three old hashes. The regressions fail each stale hash during
registration and finalization, and cover a duplicate block, an unexpected
block and a digest copied from the wrong block.
[Pinned audit kit table](https://github.com/mpmdw/JouleWise/blob/d7c436930ec1a3a29b262990837e6154058b5add/docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/item-drafts-1118/STATUS.md#L23-L29)

The MED traced to shortening the §4(a) hand-read in the manifest. The
field now specifies G0, each consumer's release and wait, each leg's cap,
the requirement for a hand-read from a qualifying prior run, and the
rule for re-dating s02. The regression checks the formerly omitted
clauses.

The 151 focused qualification, quick selection, state and documentation
tests passed. The normal CLI accepted the corrected registration and a
synthetic final, and refused all three reproduced stale registrations
and their synthetic finals. The external Draft 2020-12 schema check
passed for both accepted documents.

The lead's next gate is Tier 2 review and admission to main before the
first qualification receipt. Before the eventual stage-2 reservation,
validate the final manifest against the registered bytes from the
registration commit. The scorer build owes the cross-family oracle and
any required predictor-equivalence record.
