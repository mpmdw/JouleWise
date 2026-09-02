# Ruling 150a — luna causality refuter F1 on projection-02 ("no last-mile realization recheck after arm")

Magistrate: Fable (this session), 2026-09-02. Inputs: luna 150 (causality lens,
`out/150-luna-proj02-causal.md`), terra 149 (execution lens), Opus 151
(contract lens); bench reading of `joulewise/arm_readiness.py:9304-9462`,
`scripts/launch_window.py:250-274`, `scripts/gen_g2_phase_d.py:323`,
`joulewise/arm_readiness_evidence_t0.py:1764-1777`.

## The finding, restated

Freeze and arm both re-derive the realization rows and refuse on drift
(P-5/P-6, executed by all three refuters). But the night chain's launch step
(`launch_window.py` → `verify_consumed_launch` → `_replay_consumed_arm`)
REPLAYS the arm receipt; it does not re-derive the projection. A tokenizer
drift that lands between the arm receipt and the collection's
`RunBundleWriter.create` (`controller.py:331`) is therefore not refused
before sampling. `transformers_version` is recorded by prepare
(`mlx_runtime.py:298-300`) but filtered out of the frozen probe
(`identity_pins.py:1377-1388`).

## What is and is not true (bench-verified)

1. The interval is real for the G2 chain. `gen_g2_phase_d.py` emits
   `launch_window.py`; that script verifies the CONSUMED arm (replay), and
   nothing between it and collection calls `_derive_projection_units`.
2. The gap is NOT specific to prompt realization. `_replay_consumed_arm`
   replays the whole receipt, so every identity unit (model file pins,
   tokenizer file pins, runtime pins) has the same post-arm window. The
   projection-02 commit neither opened nor widened it.
3. A post-arm re-derivation already exists in the codebase, on the D-149
   T-0 evidence path: `arm_readiness_evidence_t0.py:1764-1777` re-runs
   `_derive_projection_units` and refuses
   `evidence_author_t0_offline_input_inventory_underivable` when the
   current `projection_input_sha256` differs from the frozen one. With the
   cure `01a94592` the realization rows are inside that digest, so the T-0
   author DOES catch a post-arm tokenizer drift — but only when T-0
   evidence authoring is part of the night, and it is not wired into the
   G2 chain today.
4. Post hoc, the bundle carries `target_tokenizer_artifact_files` +
   `tokenizer_artifact_sha256` (bundle_read.py:1212-1228 checks internal
   consistency, not receipt equality). A drift is desk-detectable after the
   fact against the arm receipt, and D-119 strict reading means no such
   bundle enters a claim silently — the cost of a drift is a wasted night,
   not a corrupted claim.

## Ruling

R-150-1. F1 is ACCEPTED as a true, PRE-EXISTING gap; it is NOT a blocker on
projection-02, whose contract (rulings 44c and 141a P-1..P-10) is the freeze
and arm gates, both of which are proven to bite. Severity for this PR:
recorded SHOULD-FIX, deferred to a follow-up row. Written dissent from
luna's BLOCKER label stands in the PR gate record for Ed to see.

R-150-2. Follow-up kernel row `V5-LAUNCH-REALIZATION-RECHECK-01` (agent
lane, queued; hard-start dependency: projection-02 merged): the launch step
that precedes collection (`scripts/launch_window.py`, immediately after
`verify_consumed_launch` succeeds) re-derives the projection exactly the way
`arm_readiness_evidence_t0.py:1764-1777` does and refuses
`readiness_identity_environment_dirty` on any digest or unit mismatch, BEFORE
the chain reaches `RunBundleWriter.create`. Regression named by luna and
adopted verbatim: a post-arm tokenizer mutation test asserting refusal
before `RunBundleWriter.create`. Second regression: the refusal is emitted
with the chain NOT started (no `chain.started` file). The recheck reuses the
existing helpers; no new identity-derivation code.

R-150-3. Until R-150-2 lands, no `_v5` night may be armed for CLAIM use
(the fence is the row's hard-start edge on the first `_v5` claim night —
see the kernel transaction). Rehearsal and DIAGNOSTIC_NO_PACK nights are
unaffected (no pack, no projection).

R-150-4. The `transformers_version` filter (`identity_pins.py:1377-1388`) is
left as is: library version is deliberately outside the frozen probe
(ruling 44c) because the realization rows bind the BEHAVIOUR of the
encoder, which is the thing that matters; adding the version would refuse
on harmless patch upgrades. Noted, not changed.
