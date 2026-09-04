# D123-REPORTED-MEAN-SUPPLIER-01 — seat landing report

Date: 2026-09-04

Start/head: `61887b48decc6a303a471c6a4c3dd14d51579ad5` on
`feat/2026-09-04-d123-reported-mean`

Authority: paper-supplier magistrate ruling R1.

Evidence class: synthetic fixtures only; this seat issues no measurement value
and makes no scientific claim.

## Landed contract

`joulewise.reported_phase_energy.v1` is one content-addressed artifact per
`campaign_role` (`alpha` or `beta`). Each cell consumes the generator-frozen,
ordered 50-member universe and admits no post-data shrinkage. The default
interval rule is `composed_member_envelope_mean.v1`; the separately registered
`composed_member_envelope_mean_t95_window.v1` rule is also implemented behind
`interval.composition_rule` with its authenticated t95 and one-window-allowance
terms. The second rule remains proposed for pre-collection cold-gate use; this
fixture exercise does not authorize live use.

Per-token values use
`ratio_of_sums_over_same_fixed_members.v1`. Only `runtime_observed` and
`server_usage` sources are accepted. Prefill requires the four observed count
surfaces to agree and join the authenticated G2-a/prompt pin; decode requires
512 observed output tokens per member. Artifact identity/authentication defects
refuse the role artifact, energy/envelope/member defects refuse the owning cell,
and denominator-only defects refuse only the per-token companion.

## Field → row → string mapping

The projection function validates the content-addressed artifact before
producing these strings. Each bracketed item below is the exact registered token
string; any unavailable parent projects the literal `STOP_FILL`.

| Authenticated artifact field(s) | Registry row | Projected string |
|---|---|---|
| alpha selected-prefill `mean_j_per_request`, `interval.lower_j`, `interval.upper_j` | DS-09 | `[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_request]` + ` (` + `[E_1p7B_prefill_p[PREFILL_LENGTH]_lower_J]` + `, ` + `[E_1p7B_prefill_p[PREFILL_LENGTH]_upper_J]` + `)` |
| alpha selected-prefill `per_token.value_j_per_token` | DS-10 | `[E_1p7B_prefill_p[PREFILL_LENGTH]_J_per_token]` |
| alpha selected-prefill `admitted_independent_bundle_count` | DS-12 | `[N_bundles_1p7B_prefill_p[PREFILL_LENGTH]]` |
| beta selected-prefill `mean_j_per_request`, `interval.lower_j`, `interval.upper_j` | DS-13 | `[E_8B_prefill_p[PREFILL_LENGTH]_J_per_request]` + ` (` + `[E_8B_prefill_p[PREFILL_LENGTH]_lower_J]` + `, ` + `[E_8B_prefill_p[PREFILL_LENGTH]_upper_J]` + `)` |
| beta selected-prefill `per_token.value_j_per_token` | DS-14 | `[E_8B_prefill_p[PREFILL_LENGTH]_J_per_token]` |
| beta selected-prefill `admitted_independent_bundle_count` | DS-16 | `[N_bundles_8B_prefill_p[PREFILL_LENGTH]]` |
| alpha decode `mean_j_per_request`, `interval.lower_j`, `interval.upper_j` | DS-17 | `[E_1p7B_decode_J_per_request]` + ` (` + `[E_1p7B_decode_lower_J]` + `, ` + `[E_1p7B_decode_upper_J]` + `)` |
| alpha decode `per_token.value_j_per_token` | DS-18 | `[E_1p7B_decode_J_per_token]` |
| alpha decode `admitted_independent_bundle_count` | DS-20 | `[N_bundles_1p7B_decode]` |
| beta decode `mean_j_per_request`, `interval.lower_j`, `interval.upper_j` | DS-21 | `[E_8B_decode_J_per_request]` + ` (` + `[E_8B_decode_lower_J]` + `, ` + `[E_8B_decode_upper_J]` + `)` |
| beta decode `per_token.value_j_per_token` | DS-22 | `[E_8B_decode_J_per_token]` |
| beta decode `admitted_independent_bundle_count` | DS-24 | `[N_bundles_8B_decode]` |

The registry edits are confined to those twelve DS rows. Existing values,
digests, and all other row statuses are unchanged.

## Detection-floor noninterference

The fixture copies the preexisting synthetic floor output byte-for-byte. SHA-256
before and after supplier construction was
`79e346d1171a05f5b17eaa86d27964393d49b9aee7849906c69f32630a12365f` in both
cases. The acceptance test also compares the copy directly with its preexisting
source bytes. Production code has no detection-floor write path.

## Red → green and test tails

Red, before the supplier module existed:

```text
ImportError: cannot import name 'reported_phase_energy' from 'joulewise'
Ran 1 test in 0.000s
FAILED (errors=1)
```

Green, final D123 acceptance:

```text
.
Ran 1 test in 8.555s
OK
```

The single table-driven method covers all 20 exact tokens; both composition
rules; both allowed denominator sources; artifact-, cell-, and per-token-level
refusals; CLI creation/refusal; and mutation of every emitted digest, census,
status/admission, ordinal, and observed-count field to `STOP_FILL`.

Required registry census/lint:

```text
.............
Ran 13 tests in 2.717s
OK
```

Replay commands:

```sh
python3 -m unittest tests.test_reported_phase_energy
R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint
```

No whole-suite run was attempted; the seat preflight rule expressly prohibited
it. No commit was created.
