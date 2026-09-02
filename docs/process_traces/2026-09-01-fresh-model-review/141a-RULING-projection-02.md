# V5-PREFILL-REALIZED-PROJECTION-02 — magistrate rulings after the four-seat design consult (2026-09-02)

Seats: Sol xhigh (report 138, NEEDS_RULING on F1), terra max (139,
NEEDS_RULING on the brief's byte-identity framing), Opus 5 (140,
DESIGN-READY), blind Fable (141, DESIGN-READY). All four converge on the
mechanism; the rulings below settle the divergences. Authority for the row:
`docs/process_traces/2026-09-01-fresh-model-review/44c-RULING-realized-prefill-check.md`.

P-1 (mechanism, convergent). The tokenizer is already loaded when the
projection probe runs (`joulewise/identity_pins.py:1251-1327` prepare →
probe → cleanup; `joulewise/adapters/mlx_runtime.py:273-295,315-324`). The
catcher realizes each expectation-bearing config's registered prompt with
the COLLECTION encoder — `_prompt_for_workload` → `_encode(...,
add_special_tokens=True)` (`mlx_runtime.py:931-937,1100-1105`) — and
`prompt_provenance` (`joulewise/provenance.py:318-324`), then compares
`(token_count, token_ids_sha256, token_hash_domain)` to
`workload_profile.prompt_token_expectation` inside
`_derive_projection_units` (`identity_pins.py:1364-1400`). No new load, no
schema-version change, nothing in the `_v5` generator or registration.

P-2 (emission gate — Sol/Opus over the Fable seat). The realization row is
attached to the probe metadata ONLY when the config carries a
`prompt_token_expectation`. Configs without one get the exact legacy
probe-metadata key set (the Fable seat's "gate on prompt_text" would add a
row to legacy decode/prefill configs and is rejected). Absence is not a
refusal here — row 01 owns absence at the bundle
(`joulewise/bundle_read.py:939-959`).

P-3 (per-config, not representative). `_derive_projection_units` today
probes `configs[0]` only; the catcher loops every expectation-bearing
config in the unit against ONE prepared runtime (prepare once, project
per config, clean up once — Sol spec item 3). The single-scientific-identity
invariant (`identity_pins.py:1375-1389`) is untouched; v5 units are already
per (arm, measurement arm) (`generate_configs.py:2567-2615`).

P-4 (refusal vocabulary — no new codes). Mismatch →
`readiness_identity_environment_dirty` with detail naming the config path
and EVERY differing field among `token_count`, `token_ids_sha256`,
`token_hash_domain`. Expectation present but unrealizable (no hook, no
tokenizer, projection exception, missing/ill-typed realization row) →
`readiness_identity_artifact_unreadable` with the config path. The
frozenset (`identity_pins.py:38-46`), `arm_readiness.py:233-246`, the
`len == 56` census and the D-078 closed-vocabulary test
(`tests/test_identity_pins.py:1169-1193`) stay byte-unchanged.

P-5 (check rows). One PASS check per expectation-bearing config in the
existing four-key check envelope; `check_id` MUST contain the substring
`shared_mint_projection` and `expected == observed` on PASS
(`tests/test_arm_readiness_evidence_t0.py:2693-2703` is a tripwire over
ALL checks). The ordered realization rows go into `probe_metadata` so
`projection_input_sha256` binds them (`identity_pins.py:1515-1534`). No
receipt or receipt-unit fields are added (`:97-145,711-717`).

P-6 (freeze vs arm). Freeze: the named refusal escapes before any write
(`identity_pins.py:1826-1837`). Arm: re-runs `_derive_projection_units`
(`:2001-2020`), catches the named refusal, and emits an authenticated REFUSE
arm receipt with the pack bytes unchanged (`:1938-2052`).

P-7 (F1 — legacy-receipt invariant restated; Sol/terra sustained). Because
`_derivation_record` hashes the whole of `identity_pins.py` and
`mlx_runtime.py` (`identity_pins.py:1143-1195`, compared exactly at arm
`:1999-2006`), NO edit to either file can leave a previously issued receipt
byte-identical, and the brief's "legacy packs must project identically" is
withdrawn as a byte claim. The binding invariant is: (a) configs without an
expectation gain no new probe/check payload — assert the exact legacy key
set; (b) no issued receipt is rewritten (D-131 `docs/decision_log.md:8423-8430`,
D-167); (c) all nine committed `_v1`–`_v3` receipts were already stale
since #241/#258 and the v3 lane is retired by D-167 — no reissue is owed;
(d) the first `_v5` freeze happens after this row lands, under the
magistrate's live control.

P-8 (gates). D-131 council trigger applies (44c: arm-critical
`identity_pins.py`). The PR runs the full D-118 gate
(`docs/decision_log.md:7769-7812`): implement (Sol xhigh, enforced scope) →
independent audit → execution refuter (terra) + contract refuter (Opus) +
causality lens (luna) → fix rounds with delta re-audits by a different model
→ Opus near-final counterreview → Fable apex pass → D-121 terminal review
(`:7892-7924`) retriggered by any later commit. Then the magistrate freezes
and arms a THROWAWAY generated `_v5` pack against the real Qwen tokenizers
before any night uses it (Sol residual risk; Fable seat item).

P-9 (WRITE_SCOPE for the implementer — exhaustive):
`joulewise/identity_pins.py`, `joulewise/adapters/mlx_runtime.py`,
`tests/test_identity_pins.py`, `tests/test_mlx_runtime.py`. Kernel, decision
log, council log, run reports, RUN_STATE/TASK_QUEUE stay magistrate-only.

P-10 (tests + mutants, from the seats' union). Tests:
`test_identity_projection_metadata_realizes_registered_prompt_with_collection_encoder`
(add_special_tokens=True; counterfactual = fake tokenizer's registered
prompt); `…_omits_realization_without_expectation` (exact legacy key set);
`test_freeze_checks_every_registered_config` (member 2 alone wrong →
its path in the reason); `test_freeze_mismatch_names_all_differing_fields`;
`test_arm_reverification_refuses_each_prompt_realization_drift` (REFUSE
receipt, pack bytes unchanged); `test_projection_refuses_unavailable_registered_realization`
(artifact-unreadable with config path); `test_projection_check_ids_carry_shared_mint_projection`.
Mutants (each must be killed, executed): `add_special_tokens=False`; check
`configs[0]` only; ignore `token_ids_sha256`; ignore `token_hash_domain`;
emit the realization row unconditionally; trust the frozen PASS at arm
without re-realizing.

Dissent recorded: the Fable seat's prompt_text gate (rejected, P-2); terra's
objection to the byte-identity framing (sustained, P-7).
