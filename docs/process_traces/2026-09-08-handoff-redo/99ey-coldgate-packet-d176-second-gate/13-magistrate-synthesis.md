# Magistrate synthesis — D-176 second gate (interactive magistrate, 2026-09-08 ~17:00 PDT)

Inputs: cold Fable ruling (10) and Opus refutation (11) on packet sha eea056b2… at the integrated head 4d72e524. Both
say: the head may LAND; it may NOT run a pack-bound night until the census self-collision is cured. They differ on the
cure's shape; the synthesis adopts the by-construction form and keeps the judge's additional fences.

## Ruling of record (installed as contract §10.4; a bounded seat on the integration branch)
1. **No census member may be derived from the running process** (Opus Q1.1/Q1.2 governs): delete the `CLONE_DERIVED`
   kind and the `repo_runs` spec; `PRODUCTION_CUSTODY_ROOTS` admits only LITERAL, HOME_RELATIVE, INVENTORY. The runs,
   custody and ledger roots of every retained deployment come from the reviewed inventory:
   `deployment_runs` = INVENTORY `measurement_root/runs`, `deployment_custody` = INVENTORY `custody_root`,
   `deployment_ledger` = INVENTORY `ledger_path` (null locators skipped; the resolver expands `key/suffix`). The
   inventory entries gain the real values for the canonical checkout (runs root + ledger path) — today they are null
   and silently dropped (Opus bench).
2. **Launcher identity** (judge Q1.2-1 = Opus Q1.4): before the census loop the consumer (and the gate) require
   `Path(arm_readiness.__file__).resolve().parents[1] == resolve(strict=True)(plan.measurement_root)`, else refuse
   `launch_go_receipt_invalid` detail `measurement_root: launcher is not the planned clone`.
3. **Rehearsal clone is un-inventoried and reviewed-named** (judge Q1.1 (c) + Q1.3): for a T0_REHEARSAL the running
   checkout must not equal, contain, or be contained by any `deployment_measurement_root` entry (refuse
   `rehearsal_roots_not_disjoint: measurement_root`), AND its basename must start with the reviewed literal
   `JouleWise-rehearsal-` (constant beside the census) — the clause that survives inventory neglect.
4. **Inventory pin** (Opus Q2.2 governs over the judge's "sound"): the inventory bytes read at ARM and at consumption
   must equal `git show <plan.repo_head>:configs/production_custody_inventory.json` in the driver checkout (never
   `HEAD:`), with the measurement clone checked out at exactly `plan.measurement_head`; a local commit that deletes an
   entry cannot un-fence a deployment.
5. **Regressions** (Opus Q1.5 + judge Q1.2-4): with the REAL resolver and the shipped inventory, `measurement_root =
   Path(arm_readiness.__file__).parents[1]` passes when un-inventoried and its runs/ exists, refuses when inventoried;
   an invariant that no spec kind is CLONE_DERIVED; an invariant that every non-null inventory `custody_root`/
   `ledger_path` appears in the resolved census; the launcher-identity refusal; the reviewed-prefix refusal.
6. **Nits folded** (judge Q1.4): one home for the rehearsal prefix; missing pack_root → `launch_go_receipt_missing` in
   gate and consumer alike (already in the contract-map fix seat's scope).

## Fitness for the first pack-bound night
7. MUST close before it: items 1–5; **seat 4 (rehearsal purpose + G7)** — the judge's argument governs (the ARM receipt
   is single-use at O_EXCL, so a rehearsal without seat 4 cannot discharge G7 afterwards and forces a second rehearsal;
   Opus's "observational" reading is rejected); the contract-map bookkeeping (Opus A-2/A-3/A-4) before the head is
   called final. The four stubbed seams (real ARM mint, real `_verify_arm_receipt` with the confirmation keywords, real
   T-0 authoring, real Popen/execve) close only in the live rehearsal.
8. **Minimal live rehearsal** (both seats, identical shape): one rehearsal-class pack night on a fresh
   `JouleWise-rehearsal-<date>-<sha>` clone at the reviewed head carrying items 1–6 and seat 4, not inventoried;
   window id prefixed `rehearsal-t0-unattended-`; `custody_root = ~/night-custody/<window_id>`; real T-0 author, real
   `generate_arm_receipt`, both real verify calls, real O_EXCL GO, real Popen (`stdin=DEVNULL`) into that clone's
   eight-flag launcher, real consumption, live `verify_consumed_launch`; then present the rehearsal GO to a
   production-plan launcher and record the class refusal as the first G7 evidence. No narrower shape.
9. The delta-F1 note (exhibit E) stands: the two ruled GO codes in the registries are not a defect.

Disposition: land the integrated head after the contract-map fixes; then seat "2b" (items 1–6) and seat 4 on the
integration branch under the gauntlet; CLONE-READINESS-01 is amended: the rehearsal clone is a `JouleWise-rehearsal-`
clone cut AFTER these land, un-inventoried; the production v5 clone stays inventoried and is never used for a
rehearsal.
