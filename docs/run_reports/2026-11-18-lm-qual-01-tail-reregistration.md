# lm-qual-01 tail re-registration, 2026-11-18

Lane [AGENT]. The task began at `origin/main` commit
`c0ff28b7c75ec53cc7ecb016f4e8b2713071ce84`. Item 434 identifies the six
qualification items as pending issuance. A targeted search of `RUN_STATE.md`
found no qualification span launch or receipt for `qual-01`, `qual-02` or
`qual-03`.

[RL-188 A1 and §1](https://github.com/mpmdw/JouleWise/blob/9a5a9be30027d90a5ec69f1820b3f8a081d664de/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L21886-L21914)
authorize a free re-registration under RL-181 §1.0 before qualification starts.
The corrected `scoring.tail_rule` gives R-3's produced-token midpoint as
`c = P + (first_stamp + 1 + last_stamp) / 2`. The `lm-qual-01` row in
`docs/process/cadence/looks/LOOKS.json` binds the corrected bytes.

| Manifest revision | SHA-256 |
| --- | --- |
| Prior registration | `d6fde6918023ea69051da45a6b0e3c06ffcfdafd8975a1773989324fa7c9bdab` |
| RL-188 re-registration | `82a8da3deadbc43fb61d213b748b57c6c29dab101e3c06ac4e36b9e69a83c3a0` |

## Findings and verification

| Finding | Disposition | Regression |
| --- | --- | --- |
| RL-188 A1, the tail formula omitted the first produced token | Corrected the formula and the ledger binding | `test_rl188_reregistration_changes_only_tail_rule_and_ledger_digest` reverses the two edits and checks the prior digests. It failed on the prior registration and passed on the corrected one. |
| PR #821 finalization must bind the corrected registration | The existing byte comparison accepts synthetic code hashes in the registered placeholders | `test_registered_hash_slots_and_complete_synthetic_final` and `test_final_rejects_changes_outside_hash_slots` passed, including a candidate with the old formula. |
| PR #828 pinned the old digest in its regression | Updated the test pin and exercised dispatch with the corrected registration | `test_registered_bytes_unchanged` and `test_qualification_final_uses_rl188_registration` passed. Dispatch rejects the old formula and an extra newline in a final candidate. |

Python 3.13 passed all 14 focused tests. Both validator CLIs accepted the
registration, and `git diff --check` passed. The hosted PR workflow runs the
full suite on the prospective merge tree. Gate ledger rows track hosted CI
and independent review in the draft PR.

Before landing, the lead checks `origin/main` for a qualification launch or
receipt again. If qualification has started, RL-188 §1 directs the lead to
keep the original registration and record the disposition in the public
deviation log.
