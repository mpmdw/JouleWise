# Ruling 42b — TRANSFER-FIDUCIAL-01 delta re-audit (terra xhigh, report 42: REFUTE)

Magistrate ruling, 2026-09-01, on `feat/transfer-fiducial-01` @ `aa2a7d89` (PR #239, HOLD
MERGE). Delta seat: terra (report `42-terra-delta-fiducial.md`); fixer was Sol (report 28).
Refuters of record: report 23. This is the SECOND fix round on F2/F3/F6, which is a mandatory
cold-gate trigger (CLAUDE.local rule 11) — a cold Fable seat adjudicates this packet before
round 2 launches; its verdict is appended below.

## Dispositions

| Finding | Severity claimed | Ruling |
|---|---|---|
| A1 — forged rule-shaped pin still admissible; no ladder/issuer provenance | blocker | **DOWNGRADED to should-fix, and SHARED with ruling 39b.** The `_v5` generator's loader was ruled to the same design on the same day (`39b-RULING-g2a-loader-binding.md`): the pin becomes a hash-bound bundle (`prompt_ladder: {path, sha256}`, `selection_record: {path, sha256}`), the loader checks the pin field-for-field against the ladder rung whose `prefill_tokens` matches, and never opens a tokenizer. The fiducial plan generator is the pin's second consumer and MUST apply the identical check, ideally by importing the loader rather than re-implementing it. A coordinated forge of pin + ladder + selection record with every hash recomputed is the operator-only adversary and is NOT refused (D-161, 39b §6). The fiducial generator already re-tokenizes at run time (`prefill_prompt_pin_runtime_token_ids_mismatch`), which is stronger than 39b's loader on that axis; keep it. **Sequencing:** the shared loader lands with the probe stream (`feat/2026-09-01-g2a-probe`, terra round 41 in flight); round 2 here adopts it AFTER that branch merges. |
| A2 — receipt omits `uncertainty_evidence.py`, `schemas.py` | blocker | **ACCEPTED as should-fix (evidence fence, honest drift).** The receipt's purpose is to freeze the program version that fit the data; a verdict-relevant module outside the digest defeats it without any adversary. Cure: a CLOSED inventory `RECEIPT_SOURCE_MODULES` in `joulewise/transfer_fiducial.py` listing every `joulewise/` module the V2 fitter imports transitively (enumerate by walking the import graph from `transfer_fiducial` and `powermetrics_fiducial`, restricted to the `joulewise` package), each digested into the receipt; a test that recomputes the transitive import set at test time and fails with the missing names if the inventory drifts (so a future import cannot silently escape the receipt); one mutation test per newly added module. Severity is should-fix, not blocker, because no data exists yet — the fence must be closed before the first V2 fit, not before merge. |
| C1 — contract invokes `scripts/summarize_g2a_prefill_probe.py` and `scripts/issue_g2a_prefill_prompt_pin.py`, absent at HEAD; D-167 absent | blocker | **RECLASSIFIED as a sequencing dependency, not a defect.** Both scripts exist at `feat/2026-09-01-g2a-probe` @ `82e7519d` (`git -C wt-probe ls-files scripts`), and D-167 is on main (`docs/decision_log.md:10407`). PR #239 stays HOLD MERGE until the probe PR merges; round 2 then merges main into the branch and the delta seat re-checks that every contract flag matches the landed parsers. No contract text change now. |
| B1 — runtime-ids mismatch test asserts exit status only | should-fix | **ACCEPTED.** Assert the named stderr reason. |
| C2 — receipt tests run ~15 full ten-bundle production captures (~355 s) | should-fix | **ACCEPTED.** Keep exactly one end-to-end detector test; the receipt-only source/hash mutation tests use a fixture `fit_run` (monkeypatched or a cached capture). Target: suite under 60 s. |
| A3 — report 28's "only `build_capture` changed" audit note is inaccurate | nit | **ACCEPTED as a record correction**: `TransferFiducialRunFit`, `fit_run`, `_run_binding_reasons`, `_parser`, `main` also changed; V1 behaviour equals `cb9371aa`. Recorded here; the trace file is not rewritten. |

## Round-2 shape

One fixer (not Sol, not terra — luna, `--effort max`), WRITE_SCOPE `joulewise/transfer_fiducial.py`,
`tests/test_transfer_fiducial.py`, `tests/test_transfer_fiducial_v2_plan.py`,
`docs/contracts/transfer_fiducial.md` (contract: add the source-inventory paragraph only).
Items: A2, B1, C2. A1 and C1 are deferred to the post-probe-merge round and recorded as such in
the contract's "Sequencing" note. Delta re-audit by a fourth seat (Sol xhigh) with the mutation
table re-run on the new inventory.

## Cold-gate verdict

(appended when the cold seat returns)
