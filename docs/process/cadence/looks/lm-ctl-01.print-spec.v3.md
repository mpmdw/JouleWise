# lm-ctl-01 synthetic print specification, revision 3

Round two returns PR #853 to spec under PIPELINE §3. Round one verified
three HIGHs and one MED. Round two verified two HIGHs and one MED. Three
exceeds the allowed two, and the suites named by the lead and the audit
disagree on an executable expectation. This revision freezes the next
build contract. It uses the existing RL-187 §3.5, RL-197 §3, and RL-197a
§§2 and 4 decisions.

## Instrument floor provenance

1. Before the controls look reservation or first controls read, the
   worker authenticates the exact `hold.json` bytes against the
   controls manifest's `hold` pin and the byte-pass receipt. The
   instrument's committed manifest and qualified stage-1 roster supply
   the instrument look, kit ID, issued kit digest and leg identity used
   for each contributing hold record. The final registered instrument
   output schema supplies the channel/window leaves and null-reason enum.
2. Use the authenticated per-leg window SD and retained count in the
   existing RL-187 pooling formula. Compute the worker's pool directly
   from those joined records. The operational worker accepts the bound
   inputs and resolves its own pool. A previously computed pool in the
   caller's process has no authority over the print.
3. A changed hold digest, missing binding, wrong kit or leg identity,
   duplicate contribution, or disallowed channel/window is a blind
   refusal. It must give the existing pre-read status and text with
   zero reservations, first reads and public writes. A permitted null
   or censored leaf follows RL-197 and RL-197a. CPU rail keeps
   `no_matched_floor`.
4. The test adapter uses a synthetic `rows` envelope and invented kit
   identities. The build binds the operational parser to the exact
   final instrument schema and stage-1 identity when the lead supplies
   them. The #868 draft describes the intended per-kit leaves. The
   final instrument pins and lead's receipt are production acceptance
   dependencies.

## Acceptance suite selection

The 2026-11-22 lead decision issued `d-ctl01-print-suite-v3.1` at
`c16c1c72157b18bc003dbddb6bdbacc0d3cdc034`. Use
`tests/contracts/cadence_looks/frozen_v3_1/SUITE-v3.1.sha256` for active
acceptance. Its SHA-256 is
`98ee283dd85b5da44dca7f730cef8e4bbfb4fdcdb5bf688a2420e791548a31c2`.
Use the replay in the [dated run report](../../../run_reports/2026-11-22-lm-ctl-01-suite-v3.md#engineering-freeze-d-ctl01-print-suite-v31)
to check and run all 846 cases.

The historical v3 inventory under `frozen_v3` authenticates the original
suite bytes. Its `A_06_incomplete_recovery` result records the pre-ruling
`incomplete_recovery` expectation. RL-197a §4 and independent V6 require
`recovery_incomplete`. The acceptance owner must bind the next audit to
the already approved v3.1 inventory so the historical case cannot choose
the active gate. Both fixture roots have independent checksums.

## Failed-first contract

Run from the checkout with one worker.

```sh
python3 -B -m unittest -v tests.contracts.cadence_looks.ctl_print_release_acceptance
```

| Case | Expected result |
| --- | --- |
| Invented kit A, leg L001, retained count 3, 0.5 W SD. Controls L002 GPU hidden-call energy is 14 J over 4 s, using the 10 s floor window. | One read. Floor energy 2.0 J, floor units 7.0. |
| Same committed kit A bytes with the old caller helper presenting kit B, leg L001, retained count 3 and 2.0 W SD. | One read, identical public bytes and the same 2.0 J and 7.0. The restarted worker derives kit A's pool from the pinned bytes. The blocked head prints 8.0 J and 1.75. |
| Frozen acceptance selector for `A_06_incomplete_recovery` and independent V6. | Inventory hashes verify. The archival result reproduces the pre-ruling token mismatch. The active A_06 and V6 both pass with exact `recovery_incomplete`. |

The new acceptance module stays explicit while the draft is blocked. At
restart, promote the floor case into discovered worker regressions and add
zero-open cases for changed hold bytes and roster/kit mismatches using the
final approved parser's wire. The shared dispatcher route remains a
separate integration follow-up under RL-187 §1.5.
