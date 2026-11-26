# hp-01 writer resolution in input review

The lead assigned this [AGENT] follow-up to the Opus MEDIUM finding on PR #972. Mission M0 found no active stop card. The branch starts at `e30794b1a` on `align/2026-11-14-look-manifest`.

`admission.writer_pin` resolves the A, B and C writers, including A for the hp-01 frozen revision. The template, review execution and record checker all use that resolver. Admission still requires the exact hp-01 kit tuple and gives the same refusal when another kit claims that revision. The draft's admission code pin and `LOOKS.json` manifest digest were refreshed to match the revised source.

## Verification and finding disposition

- The red commit `0ad6eb5cc` reproduced the finding with a generated hp-01 span. Admission accepted the span while the template and filled record showed `None`, and the checker refused the record. The unknown-runner control passed.
- `python3 -B -m unittest tests.cadence.test_input_review tests.cadence.test_interim_admission.HP01Admission tests.cadence.test_look_manifest.CommittedDraft.test_the_look_ledger_pins_the_manifest tests.cadence.test_look_manifest.CommittedDraft.test_the_committed_draft_validates_with_only_code_hashes_open` passed 23 tests. The hp-01 review now cites A and passes the checker. The unknown writer still resolves to `None` and is refused.
- Local checks used synthetic inputs and repository source and metadata. Hosted CI owns whole-suite verification under the builder test budget.

The PR ledger tracks hosted CI and the independent execution and cold Fable reviews for this head. The next step is to complete those gates on the PR against `align/2026-11-14-look-manifest`.
