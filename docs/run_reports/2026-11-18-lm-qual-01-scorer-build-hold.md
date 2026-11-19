# lm-qual-01 scorer build hold

## NEEDS_SPEC

**Which context midpoint governs the native L terminal prediction?** The registered
manifest at `59557d6e8` defines `scoring.tail_rule` using
`P + (first_stamp + last_stamp) / 2`. Its adjacent records identify
`first_stamp` as 3,583 or 3,071. SCORER-SPEC.md line 34 and the frozen
acceptance fixture's `base_j` use the midpoint of the produced tokens,
`P + (edge_lo + 1 + edge_hi) / 2`. The produced-token context is 0.5
higher for each terminal. With a nonzero context coefficient, the two
definitions give different native L predictions. The affected acceptance
case is `test_qual_l_partial_blocks_same_scorer`.

RL-166a R-3 (RLD 15990) defines the context by produced tokens. RL-181 §1.2
(RLD 19338–19340) explicitly points back to that definition. Ask Fable to
rule whether R-3 governs the implementation under the current registration,
or whether the manifest needs a formal disposition. Applying the literal
manifest alternative would require a reconciled scorer specification and
acceptance contract. The builder stopped without choosing between them.
The separate row-3 PUBLIC comparison question in FOR-FABLE.md remains open.

## Evidence and handoff

- Fetched `origin/main` was `ed5f5fb5a6fed1f6639f9f7a061f1e7144131951`.
  Registration commit `59557d6e8e00fcba6a2bdb2bfa4189bd6d7aee98` is an
  ancestor. Its manifest SHA-256 is
  `d6fde6918023ea69051da45a6b0e3c06ffcfdafd8975a1773989324fa7c9bdab`.
  Its qualification validator is still Git blob
  `35bbd6b2f5f2db62e401038afa4290491c5fc282`.
- The separately identified local integration base
  `cc7faa536a0eb3348626319a91f4ca2b47f026de` installs dependency paths
  missing on main from audited PR #795 at
  `eb449af6404ad302fd8e659fa733f97665044c5f`. The interim manifest there
  is a draft. The predictor at that head rejects native L, and its
  prediction entry point still opens coefficients itself. The predictor
  owner result and the shared authorizing reader are pending.
- All three public issued design files at the independent kit source
  `6f32db2af5be1b8b719658b92adfc4698372b056` hash to the registered
  commitments. This check used Git blob bytes. Signing-head pin and
  freeze-2 caller-census checks remain pending.
- `tests/cadence/test_qual_score_acceptance.py` was copied unchanged.
  SHA-256
  `1adbc0f5f9872a08e18f2c1edc56c7f05d2bbeadb7df0eecaed63d3c1431c51d`
  and 697 discovered methods passed intake. The suite was not executed
  against an implementation. The independent Opus expected file, author,
  and commit remain pending. The builder generated no oracle values.
  The upstream test file ends in a blank line, which is flagged by the
  default `git diff --check`. Its byte hash requires keeping that line.
- `python3 -B -m unittest tests.test_qualification_manifest` passed all
  10 tests. The local v1 schema blob matches the audited PR #795 blob.
  The paired manifest/dispatcher and predictor/release baselines started
  before the hold and had no final result at handoff.
- Scorer, schemas, final manifest, ledger transition, full suite, and CI
  are pending. No campaign input or coefficient was opened. No measurement,
  reservation, push, or merge occurred.

Next action for the lead is to obtain the terminal-context disposition
from Fable, record it in FOR-FABLE.md, and supply the admitted predictor
and reader revisions. The build can then resume against that authority.
