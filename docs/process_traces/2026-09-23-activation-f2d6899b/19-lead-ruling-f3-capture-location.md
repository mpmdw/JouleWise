# Lead ruling (magistrate f2d6899b, 2026-09-23 ~11:40 PDT): where the watchdog looks for "the capture writer ran"

This is an implementation resolution under cold ruling 16 Q1 F3. It is not a process rule. Ruling 16 told the seat to "resolve runs_root for the plan from the same code the gate uses". The seat found that `NightPlan` carries no runs root (record 18). Primary evidence read this session:

- Derivation (calibration-payload) chains pin the runs root as one shell literal, `export RUNS_ROOT='…'`. The generator writes it at `scripts/gen_derivation_night.py:284` and defaults it to `<custody_root>/runs` at `:557`. It can be overridden with `--runs-root`. Real example: `/Users/edr/night-custody/d079-epoch-25g83-derivation-n1-20260919/chain.zsh:46`. Captures land in `<RUNS_ROOT>/instrument_validation/<attempt>` (`:302`).
- Evidence (quiet_predicate_evidence) chains export no RUNS_ROOT. Their captures land in `<custody_root>/night/evidence/envelope-NN/`, with `night/evidence_envelopes.jsonl` beside them (observed in the 2026-09-23 07:00 pilot's custody root).
- The gate's own readers are `night_gate.probe_payload_kind(text)` (`joulewise/night_gate.py:147`) and `night_gate.chain_literal(text, name)` (`:135`). The sealed-candidate check in `joulewise/evidence_night.py` already uses `chain_literal` for `EVIDENCE_PLAN_PATH`.

Ruling. The watchdog reads the plan's pinned chain file (`plan.chain_path`) and classifies it with `probe_payload_kind`.
- Calibration payload: the capture-writer fact holds only if `chain_literal(text, "RUNS_ROOT")` resolves to an absolute path, and `<RUNS_ROOT>/instrument_validation` is absent or holds no files at any depth.
- quiet_predicate_evidence payload: the fact holds only if `<custody_root>/night/evidence` is absent or holds no files at any depth, and `<custody_root>/night/evidence_envelopes.jsonl` is absent or empty.
- In every other case there is no early release: the chain is unreadable, `probe_payload_kind` raises, `chain_literal` raises, or RUNS_ROOT is relative.
- The reservation fact checks for no `*.consumed.json` at any depth under the custody root, and, for a calibration payload, under RUNS_ROOT too.

Each disk fact gets a counterfactual test through `decide()` and a single-fact mutant that fails a test. The mutants are the three from ruling 16 plus the payload-kind branch.
