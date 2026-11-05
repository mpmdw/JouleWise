Tier: full

Impact statement:
(i) Raw-bundle byte or recorded timestamp: No; no raw evidence is read or changed.
(ii) Reduced energy, time, token count or correctness score: No; the producer and analysis arithmetic are unchanged.
(iii) Admit, refuse, select or exclude decision: Yes; five existing step-11 defects gain exact tooling classifications instead of unclassified failures. They still stop with exit 2. No scientific outcome is changed by this branch.
(iv) Unit or uncertainty: No; no unit or bound computation changes.
(v) Registration, prospective manifest, analysis plan or estimator constant: No; the tooling-code table is extended, but outcome classes and registrations are unchanged. The D-178 successor is an unadopted NEEDS-ED draft.
(vi) Published number or sentence in claim renderers: No; this branch does not regenerate results or change a renderer.

## Gate ledger

| # | Gate | Evidence |
| --- | --- | --- |
| 1 | Independent review by a non-author with an executing lens | NOT-RUN |
| 2 | Whole suite on the merged tree | NOT-RUN |
| 3 | CI green on the final head | NOT-RUN |
| 4 | Cold Fable final pass | NOT-RUN |
| 5 | Findings dispositioned | RUN POSTRELEASE_PLAN.md |

## Summary

**Draft; merge only after the block-5 release and the outstanding gates.**
Base is the cached `origin/main` at `92026c1849c0f053e56bdac6110c079211db2c31`.
Branch: `lane/2026-11-05-b5-post-release-fixes`.

- a: remove speculative step-4 files and reset the log counter when ordered consumption raises.
- b: NEEDS-LEAD proposal only. Consumption-based deadline accounting can change refusal ordering retained for D-188 equivalence; no accounting code changes.
- c: expire path-bound L3 entries when temporary bracket members disappear. L3 is not made path-free.
- d: normalize the temporary ledger parent only in the store key, preserving the original snapshot for every callable execution and fallback.
- e: G9 uses `is_sidecar_name` so malformed prefix lookalikes cannot hide writer outputs.
- f: explicitly register the five missing step-11 tooling codes. No wildcard or new outcome class.
- g: NEEDS-ED decision-log draft for future explicit non-issuable rows; no producer, wire or custody implementation.

The scientific exception boundaries and proposed tests are in `POSTRELEASE_PLAN.md`.
The D-178 proposal would need a prospective amendment to D-189's no-sidecar rule;
recording the draft supplies no authority to implement it.

## Verification

Pytest is absent from both installed Python versions. No dependency was downloaded.
Targeted stdlib unittest modules were used with `TMPDIR=/private/tmp` and
`JOULEWISE_B5_ANALYSIS_WORKERS=2`; the new tests spawn no worker pools.

| Module after `python3 -m unittest` | Result |
| --- | --- |
| `tests.b5_analysis.test_postrelease_step4 -q` | 5 passed |
| `tests.b5_analysis.test_postrelease_bracket_copies -q` | 2 passed |
| `tests.b5_analysis.test_postrelease_bracket_snapshot -q` | 5 passed |
| `tests.b5_analysis.test_postrelease_g9 -q` | 2 passed |
| `tests.b5_analysis.test_postrelease_step11_codes -q` | 7 passed |
| `tests.b5_analysis.test_leaf_bracket -q` | 20 passed, 320.250 s |
| `tests.b5_analysis.test_vdl_core -q` | 63 passed, 42.640 s |

The user prohibited a full suite and network access while the long analysis job
runs. Gate rows 1–4 are deliberately unclaimed. No real-data equivalence, live
hardware validation, release readiness or merge approval is asserted.

## Local delivery

The sandbox makes this checkout's `.git` read-only. The seven commits are created
using separate local Git metadata in `/private/tmp/jw-b5-postrelease-20261105.git`;
the checkout's original HEAD remains detached at the base. Import the delivered
bundle into a writable Git repository to install the branch. No push was made.

After the release, resolve item b with the lead and item g with Ed, then run the
remaining integration gates in an authorized environment before merging.
