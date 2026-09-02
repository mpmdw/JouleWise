# Ruling 48b — G2-a producers round-2 delta re-audit (luna max, report 48: REFUTE)

Magistrate ruling, 2026-09-01, on `feat/2026-09-01-g2a-probe` @ `97c0c809` (terra round 2,
report 41, under ruling 39b). Delta seat: luna (`48-luna-delta-g2a2.md`). Two of the four
claimed blockers were bench-confirmed and are honest chain breaks; one is downgraded on the
ruled text; one is out of the threat model.

## Dispositions

| Finding | Claimed | Ruling |
|---|---|---|
| A2 — issuer's closed ladder schema (five keys, `issue_g2a_prefill_prompt_pin.py:165`) rejects the generator's ruled ladder (adds `rendering_mode`, `chat_template_applied`, `thinking_policy`, `generate_g2a_probe_inputs.py:83-86`) with `prompt_ladder_closed_schema_mismatch` | blocker | **ACCEPTED as blocker (honest chain break).** Bench-read both key sets. Cure: ONE ladder key set, defined once and imported by both scripts (or, if the scripts cannot import each other, duplicated with an equality test); and an INTEGRATION test that feeds the generator's actual emitted ladder through the issuer. |
| B1 — summarizer requires `run_id` + `workload_provenance` in `summary_metrics.json` (`summarize_g2a_prefill_probe.py:329`); production writes them in `metadata.json` (`joulewise/bundle.py:1099`, `controller.py:2197`); fixture injects them artificially | blocker | **ACCEPTED as blocker (honest chain break).** Bench-verified on a retained bundle (`runs_window_metrologyA_20260731_bound/neg8-refcorpus-r12`): `summary_metrics.json` has neither key; `metadata.json` has both. Cure: read `metadata.json` for provenance and `summary_metrics.json` for metrics; the fixture bundle must carry the RETAINED artifact key shape (copy the key layout from a real bundle, values synthetic) — no injected keys. |
| A1 — probe workload name `g2a_prefill_p{n}_diagnostic` ≠ `_v5` `df_ph_prefill_p{n}_candidate` | blocker | **DOWNGRADED to should-fix, no rename.** R4 (16b) requires the workload SHAPE to be identical (`repetitions`, `warmup_runs`, `output_tokens`, `prompt_text`) so the phase window is `_v5`-shaped; the name is a label, and `_diagnostic` is the honest one (diagnostic bundles must stay distinguishable from claim bundles). Cure: an equality test on the shape fields (everything except `name`) between the producer's member workload and `workload_for("prefill")`. |
| B2 — issuer receipt validation never opens `runs_root`; a fabricated self-consistent inventory + receipt + summary yields a pin | blocker | **OUT OF THREAT MODEL (D-161), no change.** A coordinated forge of three authenticated artifacts is the operator-only adversary. The honest-drift case is already covered: the summarizer opens `runs_root` and checks each run's `config.json` digest (`:331`). Recorded. |
| A3 — pin lacks `special_token_policy` | should-fix | **ACCEPTED** (44c already ruled it): closed-schema field `special_token_policy: "add_special_tokens=true"`, validated by the loader and the issuer. |
| B3 — most named loader refusals lack exact-reason mutation tests (table in report 48) | should-fix | **ACCEPTED.** One exact-reason test per row of luna's mutation table that reads "None". |
| B4 — unknown receipt `run_id` → `KeyError` | should-fix | **ACCEPTED.** Membership check → named refusal `receipt_run_id_unknown: <id>`; exact-reason test. |
| C1 — runsheet promises `overlap_margin_above_three`; receipt emits `in_window_sample_count` | should-fix | **ACCEPTED.** Prose follows the emitted schema. |
| C2 — runsheet has no executable `_v5` generation command | should-fix | **ACCEPTED.** The exact `generate_configs.py` invocation for all three packs including `--prefill-prompt-pin`, verified against the parser. |

## Structural note

Rounds 1 and 2 each certified UNIT tests on fixtures the round itself shaped; the delta found
the chain broken at two producer→consumer seams. That is the dependence-stream pattern (45b cold
gate) in code form. Round 3 therefore carries the rule: **the desk chain is the fixture** — one
end-to-end test runs generator → (synthetic bundles in the retained key shape) → summarizer →
selector → issuer → `_v5` loader on the actual emitted artifacts, and the fixer verifies the
runsheet's commands by executing them (`sed -n 'Np' | bash`), not by re-typing.

Cold-gate trigger: not fired by the letter (A2/B1 are new defects, not re-fixes); recorded so
Ed can see the reading. Fixer: Sol xhigh (round 1 Sol, round 2 terra, delta luna). Delta: Opus 5
(contract lens, fourth family) re-running the mutation table.
