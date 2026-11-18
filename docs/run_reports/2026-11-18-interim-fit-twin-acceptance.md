# Independent interim-fit twin acceptance · 2026-11-18

Draft PR #816 carries the lead-approved import shim in `4c88b5cbe`. The shim
resolves two exact imports in the decoder's own namespace. Its reader checks
the path and digest of the single stream active in `parse(path)` and refuses
compressed streams or siblings. Its diagnostic helper always raises. The
decoder and initializer are both verified before the decoder executes from
the bytes that were hashed.

The pin for the tested `scripts/cadence_interim_twin.py` is
`aa041772d45bc955aba999721cfdea4b9776875ca635449fd0ff60593a5ba22a`.
The actual `python -I -B` child ran on a bound raw synthetic bundle with the
registered decoder at `6b2e4f57776f03ba39ea644e395d4649d4e7a4ded27dd1e008eda77601fa6e0e`
and initializer at `368cf26e48aa87f2bf0816009947df03bfaa75276c58e30e2cdbc84e3f14835c`.
The test checked both hashes and the exact script pin. The fixture's primary
targets were hand-derived. Its isolated parent captured both child streams
privately and derived the outer agreement word. The independent arithmetic
above the decoder is the scope of the agreement.

## Clause-to-test record

All tests below are in `tests.test_cadence_interim_twin`. All 21 passed in
the registered-decoder run. The bare-Python focused and state check ran 104
tests with five NumPy-dependent skips.

| Clause or finding | Commit | Regression | Result |
| --- | --- | --- | --- |
| RL-183a §1 and lead shim resolution, exact registered dependencies load in the actual isolated child | `4c88b5cbe` | `test_actual_child_argv_on_fully_bound_raw_bundle`, match and import audit | PASS. Parent derived `yes`. Neither helper module loaded. `sys.path` and the process-wide import hook matched their initial values. |
| RL-180 amendment 2, both channel references and tolerance | `4c88b5cbe` | `test_actual_child_argv_on_fully_bound_raw_bundle`, match and perturbation | PASS. Parent derived `yes` and `no` respectively. |
| RL-183a §1, one changed byte on either dependency and absent input | `4c88b5cbe` | `test_actual_child_argv_on_fully_bound_raw_bundle`, decoder and initializer pins, missing stream and coefficient | PASS. Parent derived `not_evaluable`. |
| Decoder-local import and diagnostic boundaries | `4c88b5cbe` | `test_meter_decoder_import_boundary`, `test_meter_shim_refuses_t_diagnostic` | PASS. Unexpected modules, extra imported names and any diagnostic call refused. |
| One verified raw stream per `parse` and RL-174 A.4 compression refusal | `4c88b5cbe` | `test_meter_shim_reads_only_the_active_verified_stream` | PASS. Other paths, changed bytes and a compressed sibling refused. |
| RL-181 §5 and F-12, private comparison, closed failure and outer byte scan | `4c88b5cbe` | `test_actual_child_argv_on_fully_bound_raw_bundle`, `test_isolated_child_private_capture_and_closed_failure` | PASS. The child left input and result-target files byte-identical. Outer stdout carried the word-only projection and outer stderr was empty. |
| RL-183a §§2–3 and TWIN-INTERFACE-2, tied samples, span period, identity bytes and Step 3 | `834d7bbe2` | `test_meter_ties_and_span_wide_period`, reader identity and Step 3 regressions | PASS on the final test run. |

Synthetic fixtures supplied all inputs. Only the decoder and initializer
were accessed from the revision cited by the lead. The primary look's code
was never opened. The host refused `ps` for the read-only fixture census and
the census remains unverified.

The lead can now bind the script path and tested SHA-256 in the manifest
and evaluate parent adoption at the integration gate.
