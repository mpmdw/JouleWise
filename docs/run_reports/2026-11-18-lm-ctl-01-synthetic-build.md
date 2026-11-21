# lm-ctl-01 synthetic print seam — 2026-11-18

**Disposition: synthetic contract PASS. Production freeze and acceptance pending.**

Mission M0 found no active stop card. This was an [AGENT] task scoped to the
controls print seam. The clean seat started detached at
`f1be75b21978da69fa20506640bcb76ec53f6df2`, equal to the remote `main` head.
There was no controls print PR head to advance to. PR #828's remote head
matched its interface pin and PR #808 remained the separate runner lane.
The build used the observed seat base pending Opus's implementation base.

The source-only freeze is `860eb6bb920c09bb85f484e4162082288d8d9a0a`.
The in-tree `synthetic_acceptance.py` has the same Git blob
`e782441f95db1d80b2b259d1c312f57024cf182d`. The pinned runner design, kit
draft and published instrument spec matched the supplied SHA-256s. The
adapter translates invented records into the print module's typed input
projections and maps typed refusals to the frozen test messages. The
reference oracle stays in the copied fixture. The print module checks exact
script-record bytes, physical ordering, visible count sums and pair parity.
Its public and private projection encoders cover the proposed synthetic
shapes. The committed freeze and receipt fields in these vectors represent
already authenticated facts.

| Finding | Regression | Result |
|---|---|---|
| Substituted identity or instrument binding | `test_wrong_identity`, `test_instrument_input_binding`, `test_zero_pin_refuses_even_if_committed` | PASS |
| Invalid roster, reference, hand PASS or freeze order | `test_layout_and_consumers`, `test_hand_read_and_freeze_order` | PASS |
| Changed work bytes, wrong visible envelope, or recovery outside sampling | `test_script_digest_and_visible_envelope`, `test_physical_order_and_sampled_recovery` | PASS |
| Unequal delivered counts, seed or prompt, or growing split context | `test_pair_count_seed_prompt_and_depth`, `test_pair_depth_from_fresh_calls` | PASS |
| Disclosure, closure edge, CPU dose tie, and qualifier privacy | `test_exact_disclosure`, `test_counted_layout_and_private_qualifier`, `test_closure_and_burn_order`, `test_unrun_qualifier_has_no_public_word`, both `test_public_projection_*` tests | PASS |

## Verification

- `python3 -I -B synthetic_acceptance.py` in the freeze seat passed all 11
  reference groups. The external `--builder` invocation first exited 1 for
  the absent adapter and passed all 11 groups after implementation. The
  in-tree copy also passed all 11 in builder mode and matched the freeze bytes.
- `python3 -B -m unittest -v tests.contracts.cadence_looks.test_ctl_print`
  and discovery rooted at `tests/contracts/cadence_looks` passed all 15 tests.
- The broader `unittest discover -s tests -p 'test_ctl_print.py'` attempt
  unexpectedly entered unrelated repository suites because package
  `load_tests` hooks ignore the pattern. It supplies no acceptance evidence.
  The session did not signal the process. Use the named module or the
  contract directory for local checks.
- Full-suite CI awaits the assigned integration head and off-Air execution.
  No controls print PR or CI run exists for this local build.

## NEEDS_SPEC and next step

- **Numerics (Fable and analyst).** Freeze the baseline and phase/whole
  limits, estimator and range, floor matching and units, short/null/censor
  handling and treatment of the missing CPU floor. Supply independent hand
  results and contributing identities. The integers in the closure vectors
  check the inclusive 1% boundary on tabulated values.
- **Release and read-dependent inputs (Fable and Opus).** Freeze the final
  public/private inventory, output wire shapes and applicable failure
  contract. Bind the final instrument manifest, authorized leaves, covered
  prompt, doses, recovery, gap and disclosure wording. Opus supplies kit
  issue, the native hand and close evidence, host and ledger authority.
- **Integration (Opus, then Sol).** Assign the base with the admitted release
  boundary and RL-176 B.1 phase entry point. Sol can then bind actual Git
  bytes and ancestry and exercise exclusive reservation, output writes,
  process descriptors and failure at the real entry point on invented roots.
  Review and the production freeze receipt follow those checks. Opus records
  the accepted code, schema, manifest and expected results before reservation
  or any first open. The synthetic PASS supplies no operational authority.
