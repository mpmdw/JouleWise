# PR #828 dispatcher follow-up

Tier 1 implementation of RL-187 §1.4. The clean, detached seat at
`a205cf402` and the PR #828 merge commit both passed the ancestry checks
against freshly fetched `origin/main`. The new branch started at
`44c58650ed75c2d9db22349c663261c748244e39`, the fetched main tip. [RL-187 §1.4](https://github.com/mpmdw/JouleWise/blob/9fffb6014/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21577)

| Finding | Commit | Regression | Result |
| --- | --- | --- | --- |
| Decoder notices exposed details of a misnamed input | `6322d591b` | `test_cli_candidate_decode_refusal_is_fixed`, `test_cli_registration_decode_refusal_is_fixed` | PASS |
| Manifest and registration paths could reach a read through `RESTRICTED` | `f5a8c737d` | `test_restricted_cli_paths_refuse_before_either_file_is_opened` | PASS |
| Missing interim inputs need visible unittest skip reasons | `f8569cff5` | `test_missing_interim_inputs_are_reported_as_skips` | PASS |

The decoder regression checks a fixed stderr line, empty stdout, and exit
status 2 for invalid UTF-8, malformed JSON, duplicate keys, and a non-JSON
constant. It covers the candidate and both final registration routes. The
path regression covers the literal argument, a symlink into the restricted
component, a `..` spelling, and the component at the end of the path. A
read spy verifies that both arguments are checked before either input opens.
The allowed-registration tests still check that the registration is read only
after the candidate passes its earlier validation.

The interim comparison now skips if its Git commit is missing. The v1 digest
test already skipped and now identifies the missing schema by look. Both
missing inputs are exercised by the skip regression. The qualification pin
checks run independently of interim availability. The actual v1 schema
digest remains gated on the interim schema being present, as ruled for PR #795.

The pre-change focused baseline ran 54 tests with one expected skip. Each
new regression failed against the pre-fix behavior, then passed on its fix.
The whole-suite gate uses hosted GitHub CI because the unfiltered local
suite can access real measurement inputs. PR #854 records CI and the cold
verdict against the exact candidate head. [Draft PR #854](https://github.com/mpmdw/JouleWise/pull/854)

## Astra 6.2 independent executing review

Round one reviewed `ae89fcc13f8069b1006bedf388f35ab970eed916` against base
`44c58650ed75c2d9db22349c663261c748244e39`. Astra confirmed the checkout SHA
and ran five focused regressions with Python 3.13. All five passed. The
independent probes also passed six decoder refusal cases and four uppercase
path refusal cases with zero reads. A forced-missing-input unittest run
reported two reasoned skips and passed the qualification byte check.

| Finding | Disposition | Regression |
| --- | --- | --- |
| VERIFIED MED. `Path.resolve()` preserved an alternate spelling accepted by the case-insensitive worktree volume. Astra reproduced this with a neutral directory name. | Fixed in `0209067082245e731098adab184c1d47deef7c75` by folding case on each supplied and resolved component. | `test_restricted_cli_paths_refuse_before_either_file_is_opened` failed four new synthetic cases before the fix and passed after it. |

Round two reviewed `0209067082245e731098adab184c1d47deef7c75` against the
round-one head. Astra verified the MED fix and passed the repository
regression and eight independent synthetic probes. The probes used lower
and mixed case in direct arguments and dangling symlink destinations, for
both the manifest and `--registration`. Every case returned status 2 and
the fixed notice with zero calls to `Path.read_bytes`. No VERIFIED HIGH
remained. Both rounds used synthetic inputs and public source metadata.

## Cold audit round one

The cold audit blocked `7fccc17790d67f98a195d21e6b4c1a2ae6723c5b` on one
VERIFIED HIGH. Valid JSON with an extra key exposed that key on stderr when
the dispatcher refused either a candidate or a registration. Sol reproduced
the leak with top-level and nested keys across the v2 routes and with a
synthetic v1 validator that emitted a refused key on both streams. The three
regressions failed all 13 cases before the fix.

Commit `69dd859f3a828c8f9046584c2fce9adac350f648` makes the CLI emit one
fixed notice for untrusted validation exceptions and delegated v1 failures.
Dispatcher guards can emit their fixed notices. The final placeholder guard
uses fixed text for both placeholder forms, and the outer failure path uses
the same refusal policy. Qualification validator bytes remain pinned. The
success paths and exit status 2 on refusal are preserved. Return the final
head to the cold reviewer for execution and a recorded verdict.

## Exact-head cold pass

The Fable 5.2 seat executes the following synthetic checks on the final PR
head in a private scratch directory. Record the reviewed SHA,
execution results, and verdict in the PR body to keep the evidence bound
to that head.

```sh
python3.13 -B -m unittest -v \
  tests.test_cadence_manifest_dispatch.VariantContractTests.test_cli_candidate_decode_refusal_is_fixed \
  tests.test_cadence_manifest_dispatch.VariantContractTests.test_cli_registration_decode_refusal_is_fixed \
  tests.test_cadence_manifest_dispatch.VariantContractTests.test_cli_candidate_schema_refusal_is_fixed \
  tests.test_cadence_manifest_dispatch.VariantContractTests.test_cli_registration_schema_refusal_is_fixed \
  tests.test_cadence_manifest_dispatch.VariantContractTests.test_cli_legacy_schema_refusal_is_fixed \
  tests.test_cadence_manifest_dispatch.VariantContractTests.test_restricted_cli_paths_refuse_before_either_file_is_opened \
  tests.test_cadence_manifest_dispatch.VariantContractTests.test_qualification_bytes_unchanged \
  tests.test_cadence_manifest_dispatch.TransferManifestTests.test_missing_interim_inputs_are_reported_as_skips
```
