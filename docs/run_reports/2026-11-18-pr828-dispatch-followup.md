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
suite can access real measurement inputs. The live CI state and any review
evidence belong in the draft PR ledger. Independent review is pending at
handoff. RL-187 names an Astra seat, and the Tier 1 pipeline calls for a
cross-family reviewer. The lead owns review routing before readiness.
