# Opus consult: fold r1 into s1? (blind, one round, 2026-10-05)

**Recommendation: (C) = (B) with corrections.** Fold r1 into s1. Retire live G6/G7 rather than rebuild them. Re-rule G1's predicate and add a gate-subset harvest entry point. Keep evidence failures from failing s1's science. Replace r1's Q110 receipt.

## 1. What only r1 can catch, and the number each protects

r1 catches nothing that protects a claim number and that s1 plus desk tests would miss:

- **T0_REHEARSAL-branch defects:** the purpose predicate (`joulewise/arm_readiness.py:9937-9942`) and the disjoint-root census (`joulewise/t0_rehearsal.py:805-834`). Only r1 runs this code; no claim night does, so it protects no number.
- **Contained blast radius:** a pack-path defect that writes into production ARM, ledger or readiness custody. On r1 the disjoint roots hold the damage. The ledger cutoff fixes the calibration bracket, so this indirectly protects every ALPHA/BETA/GAMMA energy figure. But s1 writes the production ledger by design (registration §3.6), and custody is checked fail-closed (`verify_custody=True`). The defect costs a refusal and a repair, not a wrong number.
- **Ordering.** r1 finds pack-path bugs on a night that consumes nothing scarce. Its value is cost, not protection.

Conversely, **r1 is weaker than s1 on the gates that protect a number.** It runs no inference (§2): G8 censuses run without real load, G4 has no sampler stream, and G9's two backup stages (`t0_rehearsal.py:61-68`) copy stubs. On s1 the same gates face the real hazards.

## 2. What is lost under (B), and what (B) needs

**What is lost:**
1. **G6 has nothing to test.** The evaluator hard-fails any non-rehearsal bundle (`t0_rehearsal.py:805`, `:810`). Retire it rather than make it a desk control. s1 needs a different guarantee, that non-claim bytes cannot be promoted to a claim, and that is already enforced: the v3 consumption record binds purpose and `claim_eligible`, and A6/L10 read them (D-176 §2, `docs/decision_log.md:11515`). Exercise that refusal once at the desk on **s1's real consumption bytes**.
2. **Option B's G7 desk run fails as written.** `g7-control` refuses unless the production plan's authorization purpose is `CAMPAIGN_TRANSACTION` (`scripts/run_night.py:2181`). s1's purpose is `G2B_SHAKEDOWN`. The command also needs a real-shaped rehearsal source under `~/night-custody/rehearsal-t0-unattended-*` with `night/go_receipt.json` (`:2163-2166`). Making it pass would mean minting a `CAMPAIGN_TRANSACTION` authorization before G2-b. Kernel row E7 and D-176 §2 forbid that (`TASK_QUEUE.md:691`). See §4: retire live G7.
3. **Q110 drops from three to two real receipt bundles.** It needs ≥3, taken from r1, a1 and s1 (registration §8). Replace r1's with a second ARM-only, a1-style receipt (no launch, so cheap). Alternatively, a NULL'd s1 attempt's ARM receipt counts if one occurs.
4. **A pack-path failure lands on the GAMMA attempt instead of a throwaway pack.**

**Acceptable?** Mostly. A failure before `chain.started` is NULL (re-arm with a new plan ID), and the same-code-twice consult rule stops death loops. The purpose binding keeps production evidence safe. One cost is not yet cheap: a pack-path tooling failure *after* `chain.started` makes s1 RECOVER and uses up the only s2 (registration §7). Item 2 fixes that.

**What (B) needs so that s1 failure is cheap and can't contaminate claim evidence:**
1. **Two separate verdicts on s1:** structural G2-b and pack-path qualification. The G-evidence producers (lane B's custody, lifecycle, HID, lineage) only observe. A producer fault makes the *qualification* verdict REFUSED or FAIL; it never aborts the chain or makes G2-b RECOVER.
2. **No science bytes, no lost allowance.** A RECOVER with a named pack-path tooling cause, firing after `chain.started` but before the first science sampler starts, holds no science bytes. D-078's ban on pooling has nothing to act on, so it should not use up s2. This is a rule change for the erratum. The kernel fence "G2-b has one governed consuming launch" (`TASK_QUEUE.md:703`) already conflicts with the s2 allowance; settle both.
3. **A gate-subset harvest entry point** that runs the existing G1–G5 and G8–G10 evaluators unchanged and skips G6/G7 explicitly. The ten-gate loop (`t0_rehearsal.py:1232`) would FAIL s1 on G6. An R3 change, no predicate edited.
4. **s1's ARM/GO/consumption custody sits in its own shakedown root, apart from the claim roots** (the Q3 isolation fence, `TASK_QUEUE.md:703`). The post-s1 ledger-pin advance goes through the reviewed H′ route (§12(i)).

## 3. Minimal G gates that must PASS live before the first claim window

| Gate | Hazard / number protected | Satisfied by |
|---|---|---|
| G4 clock | Network-time steps or anchor drift would misalign every member's energy window. Bound: ≤5 ms anchor. | s1 |
| G10 | Shows the T-0 author *does* refuse when the RAW anchor moves >5 ms. Without it, a G4 PASS has no demonstrated ability to fail. | Ed's physical control before s1's T-0, plus software falsifiers |
| G8 zero-agent | Agent CPU/GPU load inside captured power | s1 (stronger than r1: real load) |
| G3 HID idle | Operator activity during T-0 | s1 |
| G2 T-0 namespace | Operator attestation substituted for a probe-sourced clock fact | s1 |
| G5 GO C1–C5 replay | Pre-registration drift (pack/chain sha256, confirmation hC); stale ARM/boot; double launch | s1. Evaluator is generic (`t0_rehearsal.py:717-779`) |
| G9 lifecycle | Evidence survives (two verified backups); network time restored OFF | s1, with real bundles |
| G1 execution | Liveness only: a prompt or hang causes a NULL or RECOVER, never a wrong number | s1, after re-ruling |

All of these except G10's physical record can be met on s1's own evidence.

**G1 re-ruling needed under either option.** The evaluator requires `exit_code == 0` for every process (`t0_rehearsal.py:461`), but the zero-agent fence defines a passing census as **pgrep exit exactly 1 with empty stdout** (`TASK_QUEUE.md:811`). G1 therefore fails by construction; fix it with a registered expected outcome per process. Retire exhaustive exec-descendant prompt/EOF tracing: fd0 is already `/dev/null` (D-176 §4, `decision_log.md:11529`), so a prompting descendant gets EOF, exits abnormally, and G9 and the s1 verdict catch it. That costs a night, not a number.

**(B) removes** lane B's F1 (registry profile, `arm_readiness.py:4488/4576`), F2 (genesis pin, `arm_readiness_evidence_t0.py:1572`), the rehearsal-clone cut (A161 blocker) and one [QUIET-MAC] night. All exist only for r1. Lane B's custody, lifecycle and assembly code carries over to s1.

## 4. D-161: which of G5/G6/G7 guard only against deliberate forgery

- **G5 — keep.** Its checks catch mistakes: wrong pack or boot, expired evidence, a re-ARM, two consumptions. The forged-receipt test reuses the same replay.
- **G6 — not forgery-only:** a misconfigured root is a mistake. **But with no rehearsal it has nothing to test, so it retires with r1.** If r1 ever returns, G6 returns with it.
- **G7 — forgery-only as a live gate. Retire it; keep the merged unit regression.** A rehearsal GO handed to the production launcher by mistake already fails the consumer's bindings: arm `receipt_id`/sha256, `pack_sha256`, launch sha256s, plan (D-176 §1, `decision_log.md:11506`). The class refusal adds protection only against an artifact built on purpose to bind a production pack and ARM while carrying rehearsal class. The unit test ("valid rehearsal receipt refused by class", D-176 replay list) stays as a cheap fence.

## Erratum shape (prospective cold gate; Ed may veto)

The decision-4 night becomes s1 (`G2B_SHAKEDOWN`). Live G6/G7 retire, with A161's G7 and clone-cut evidence. G1 gets per-process expected outcomes. The qualification verdict is separated from the G2-b verdict. A pack-path RECOVER that holds no science bytes does not use up s2. Q110 gets a replacement receipt. Kernel: A160 closes on s1's qualification harvest; Q3 drops its NIGHT-PACK-REHEARSAL-01 hard-start; A161 closes as superseded. a1 is unchanged and now comes directly before s1.
