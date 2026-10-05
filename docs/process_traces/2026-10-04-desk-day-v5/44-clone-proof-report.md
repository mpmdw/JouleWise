CLONE PROOF: FINDINGS

# `_v5` throwaway-clone re-proof: freeze, arm admission and receipt (desk evidence only)

- Seat: headless Claude Opus 5.5, 2026-10-04, 19:06–20:45 PDT.
- Base: `24741cab5868f6a8109e65cfd68abb77514a1ff2`, the head of `desk/2026-10-04-v5-pin-and-packs`. This branch is not on main, and no CI run covers it.
- Custody: `/tmp/dd5-clone/custody/`, mirrored to `/Users/edr/night-archive/desk-day-v5/clone-proof/custody/`.
- Interpreter: `/Users/edr/code/JouleWise/.venv/bin/python` (Python 3.13.1).
- Safety: no sudo, launchctl or powermetrics was run. No window was armed or launched, and no launch capability was consumed. Nothing was pushed, and no fetch ran in the canonical repository. No measured energy value appears anywhere in this report.

## Bottom line

The proof stopped at **step 3, evidence authoring**, for all three packs. The cause is two blockers that sit in front of every later step.

- **F1 (generator defect: blocks both floors at step 2).**
  - Both floor generators declare the decode identity unit without `prompt_tokens`.
  - The typed config projection, however, always carries `prompt_tokens: null`.
  - The U11 identity projection therefore refuses `readiness_identity_environment_dirty` for `alpha` and `beta`.
  - A one-line local probe fix was tested in the `patched` clone. It makes all three projections PASS, and all 200 pre-author tests still pass with it applied.
- **F2 (registry/code prerequisite not landed: blocks all three packs at step 3).**
  - The runbook change for the 2026-09-29 permanent network-time-OFF ruling removed the two §5A sentences that the DOCTRINE_PIN evidence deriver requires verbatim.
  - Generic evidence authoring therefore refuses `evidence_author_doctrine_pin_underivable` for every pack.
  - The runbook itself records this prerequisite (`docs/phase_2/window_runbook.md:640-641`): the sealed restore-recipe registry row "must be retired through its coordinated registry change before successor freeze/ARM can pass."
  - That change has not landed. Until it does, no evidence commit can exist, so no PASS freeze, no pinset, no marker and no admissible arm can be reached at this head.

Everything that could run without evidence reached its expected outcome:

- the anchors;
- the generator checks;
- the contrast projection;
- all 200 pre-author tests;
- the ruled predecessor mapping and the `freeze-0004` ordinal, shown on a sacrificial, poisoned slot;
- a governed non-null arm REFUSE receipt;
- the canonical verify REFUSE;
- the A196 A5 dry gate, which gave the named refusal `evidence_author_t0_clock_attestation_missing` for all three packs.

One attempted probe was denied. To look past F2, I tried a probe-only §5A text shim in a throwaway clone. The auto-mode classifier denied it as weakening a doctrine gate. I did not pursue that by any other route. As a result, the nine evidence kinds behind DOCTRINE_PIN are **unexercised**. These include `PACK_AUTHENTICATION`, which is the contrast generic-replay repair from PR #473 (scout §2, condition 2), so **that repair is still unproven in a clone**.

## Step table

Path conventions: `<pack>` = `configs/campaigns/<pack-id>`. Clone `X` = `/tmp/dd5-clone/X`. Receipt digests are SHA-256.

| Step | Pack | Command | rc | Outcome | Expected? |
|---|---|---|---|---|---|
| 1 | — | `derive_estate_anchors.py /tmp/dd5-clone/primary --output custody/estate-anchor-map.json`; `--print-embedded-spec` | 0, 0 | 68 anchors, 15 `legacy.*`, legacy.14 = `…test_pinset_is_byte_pinned_and_has_no_unreviewed_update_lane`; map `5c1d1b40…6eff6e`, spec `b2355c5b…204e`, deriver `b81e56dc…0920` | yes |
| 1b | all 3 | the three source generators `--check` (floors with `--prefill-prompt-pin`; contrast with panel/models/workload/length/pin) plus the three emitted `generate_configs.py --check` | 0 ×6 | floors: 100 science configs each; plan_tree `b5e56c0f…` (1.7B) and `89a1529f…` (8B). Contrast: 40+40 members, tree `37e0beea…` | yes |
| 2 | floor 1.7B | `project_identity_pins.py freeze /tmp/dd5-clone/primary/<pack>` | 2 | REFUSE `readiness_identity_environment_dirty`: "identity unit 'alpha' config declaration differs from pack" | **NO → F1** |
| 2 | floor 8B | same | 2 | REFUSE `readiness_identity_environment_dirty`: unit 'beta', same cause | **NO → F1** |
| 2 | contrast | same | 0 | PASS, mutated; `projection-0001.json` `b7f4d876…b428`; committed as primary `6138faa4` | yes |
| 2p | floors 1.7B/8B (patched clone) | LOCAL PROBE: add `"prompt_tokens": None` at `generate_configs.py:2442` in both floors; regenerate with `--output-root <clone> --prefill-prompt-pin <pin> --no-preserve-current-frozen-bytes`; all `--check` rc 0; then one `freeze` → commit unit per pack | 0 ×3 | PASS projection-0001: 1.7B `78e753d7…bd20`, 8B `ad2ad06b…836e`, contrast `67a928f7…5feb`. The calibration-plan sha is unchanged; only plan_tree and producer_contract changed | yes (F1 fix works for projection) |
| 3a | all 3 | emitted `generate_configs.py --check` after projection | 1 | "pack inventory differs: extras=identity_pin_projection.receipts/…" | yes: by design, because projected packs authenticate through composed PACKAUTH (`joulewise/arm_readiness_evidence.py:1278-1300`) |
| 3b | — | `python -m unittest -v` of the five pre-author modules, both clones (split per module, and test_receipt_histsem per class/method; see Notes) | 0 | primary and patched alike: schemas 50 OK; histsem 73 OK (1 skipped); mint admission 8 OK; contrast pack 48 OK; floor generate 21 OK | yes |
| 3c | all 3 (primary @ `6138faa4`, clean) | `author_arm_readiness_evidence.py --pack-root /tmp/dd5-clone/primary/<pack> --measurement-checkout /tmp/dd5-clone/primary` | 2 ×3 | REFUSE kind DOCTRINE_PIN `evidence_author_doctrine_pin_underivable`: "runbook/pack do not derive clock restoration after verdict and both backups" | **NO → F2** |
| 3c | all 3 (patched @ `7348aece`, clean) | same, with the patched clone | 2 ×3 | identical REFUSE (transcript `616933…6e` for all six) | **NO → F2** |
| 3d | — | evidence commit | — | NOT MADE: nothing was authored | — |
| 3e | — | LOCAL PROBE 2: runbook §5A text shim, in a separate rehearsal clone | — | DENIED by the auto-mode classifier ("Security Weaken"); not pursued | — |
| 4s | contrast (sacrificial1 @ `6138faa4`; refs/heads/main and origin/main set locally per S0 §1.1) | `generate_arm_readiness.py freeze --pack-root …/<contrast> --measurement-checkout /tmp/dd5-clone/sacrificial1 --predecessor-pack-root …/d117_contrast_qwen25_1p5b_vs_7b_v3` | 1 | governed REFUSE receipt `freeze-0004.json` `3323977f…1887`: `clock.restore_recipe` → `readiness_clock_preflight_refused`; 11 `desk.*` rows → `readiness_dependency_refused` | yes given F2 (no evidence). It proves the ruled non-adjacent predecessor resolves and the ordinal is `freeze-0004`. The slot is poisoned, as intended |
| 4p | all 3 (primary) | primary freeze | — | NOT RUN: S0 §3.5 STOP (sacrificial did not PASS). The primary `freeze-0004` slots are untouched | per procedure |
| 5 | all 3 | `build_v4_histsem_pinset.py`, `verify_receipt_histsem.py`, `build_family_marker.py`, `verify_family_marker.py` | — | NOT REACHABLE (needs a freeze commit). Inputs resolved: see "Step-5 inputs" below | — |
| 6s | contrast (sacrificial1 @ `2f60038c`, refused freeze committed, main refs local) | `generate_arm_readiness.py arm --pack-root … --arm-context '<S0 context, roots under custody/arm-context-sac1>' --window-custody-root custody/arm-context-sac1/windows` (no hC: no Ed-confirmed step-6 table can exist) | 1 | governed **non-null** REFUSE `arm-0001.json` `f1f6c401…ee90`, 12 codes: `readiness_{backup,clock,ledger,machine}_preflight_refused`, `dependency_refused`, `dry_run_missing`, `launch_capability_unavailable`, `r1_family_publication`, `root_binding_invalid`, `root_not_fresh`, `terminal_review_missing`, `waiver_source_invalid` | yes (S0 r4 2477-2480); no capability consumed |
| 6v | contrast (sacrificial1) | `generate_arm_readiness.py verify --pack-root … --arm-receipt …/arm-0001.json` | 2 | REFUSE `readiness_dependency_refused` "arm receipt does not carry PASS/GO" | yes (canonical verify refusal) |
| 6a | all 3 (a5clean @ `24741cab`, main refs untouched) | `author_arm_evidence_t0.py --pack-root /tmp/dd5-clone/a5clean/<pack> --custody-root custody/a5/<pack>` | 2 ×3 | REFUSE `evidence_author_t0_reviewed_tree_mismatch` (HEAD ≠ local/origin main `cfdb90d6`; predicate `joulewise/arm_readiness.py:5594-5616`) | environment limit (branch not on main), not a pack defect |
| 6b | all 3 (a5main @ `24741cab`; refs/heads/main and refs/remotes/origin/main = head, local only) | same, `--custody-root custody/a5main/<pack>` | 2 ×3 | REFUSE kind CLOCK_ATTESTATION `evidence_author_t0_clock_attestation_missing` (clock-reference capture absent) | **yes: the A196 named refusal** |

## Findings

### F1: floor `_v5` decode identity declaration omits `prompt_tokens` (generator defect; blocks the U11 projection of both floors)

- **Where.** `configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py:2440-2444`, and the identical lines in `configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py`.
  - The decode unit's `declared_identity.workload_profile` is built as `{**decode_identity_workload, "prompt_text": None, "dataset_ref": None}`.
  - `decode_identity_workload` (`:2296-2303`) carries no `prompt_tokens`.
  - The prefill unit of the same function does include `"prompt_tokens": None` (`:2476`), and so does the contrast generator (`configs/campaigns/d117_contrast_v5/generate_configs.py:1568`).
  - The lines date to `4e742b5b` (2026-09-03, the original `_v5` floor generators). PRs #472 and #473 did not introduce them.
- **Why it refuses.**
  - `joulewise/identity_pins.py:1655-1674` compares `_declared_identity_from_config(config)` with the declared identity by exact dict equality whenever no suite-member declaration is in play.
  - The left side comes from `BenchmarkConfig.from_mapping(...).to_dict()` (`identity_pins.py:226-230`, `1282-1299`), which always emits `workload_profile.prompt_tokens` (`joulewise/schemas.py:915`), here as `null`.
  - The missing key is therefore a mismatch. The refusal is `readiness_identity_environment_dirty` at `identity_pins.py:1670-1674`.
  - The `_v3` floors pass because they declared an explicit `prompt_tokens: 128`.
- **Test gap.** `tests.test_d117_floor_qwen3_v5_generate` never runs `freeze_projection` on a generated floor pack. `tests.test_d117_contrast_v5_pack` does (`:513`, `:1133`), which is why only the contrast pack was covered.
- **Probe-verified cure.** Add `"prompt_tokens": None,` after `"prompt_text": None,` in both floor generators, then regenerate the floors with `--no-preserve-current-frozen-bytes`. Patch: `custody/patched/F1-probe-generator.patch`, sha `59ae3b18…14f7`. With it applied:
  - the generator, emitted and contrast `--check`s pass;
  - the calibration-plan digests are unchanged (only `plan_tree.json`, `plan_tree.sha256` and `producer_contract.json` move);
  - all three projections PASS;
  - all 200 pre-author tests pass.
- **Recommended route.** Land it through the code gate, with a regression test that runs `freeze_projection` on each generated floor (the contrast pattern), and regenerate the two floor packs on the desk branch.
- **Class:** pack/generator defect.

### F2: the DOCTRINE_PIN evidence deriver still requires the retired clock-restore prose (unlanded registry/code prerequisite; blocks all generic evidence, hence freeze/arm)

- **Where.** `joulewise/arm_readiness_evidence.py:832-866`.
  - `restore_after_verdict` requires §5A of `docs/phase_2/window_runbook.md` to contain the literals "whole-window verdict, and the backup, re-enable it" and "The restore comes last".
  - The deriver then asserts the facts `clock.restore_recipe.v1 {restore_after_verdict: true, restore_after_both_backups: true}` (`:874-879`).
  - Commit `7b4deba0` (2026-09-29, "Runbook: network time stays OFF; resync only in the arm step") deleted both sentences. They are present at `7b4deba0^`, absent at `7b4deba0` and later.
  - The current §5A says the opposite: "Network time stays OFF … do not restore ON".
- **Already-recorded prerequisite.** `docs/phase_2/window_runbook.md:640-641` says: "The sealed restore-recipe registry row must be retired through its coordinated registry change before successor freeze/ARM can pass." That retirement (registry row `clock.restore_recipe`, plus this deriver and its facts) has not landed.
- **Same blocker at later steps.**
  - The sacrificial freeze refuses `clock.restore_recipe` → `readiness_clock_preflight_refused`.
  - The arm receipt refuses `clock.restore_recipe` and `clock.network_time_off` → `readiness_clock_preflight_refused`.
- **Not yet exercised.**
  - Authoring stops at the first failing kind (`arm_readiness_evidence.py:3378-3392`), and the required kinds are ordered `ACCEPTANCE_OWNER, DOCTRINE_PIN, ESTIMATOR_IDENTITY, MINT_TRUST, MULTICELL_MINT, PACK_AUTHENTICATION, PACK_FAMILY, REASON_CODE_COVERAGE, RECEIPT_ORACLE, RECOVERY_LEDGER_TEST, THREE_WINDOW_REGRESSION`.
  - Only ACCEPTANCE_OWNER is known to derive. Anything wrong in the other nine kinds will only surface after F2 is cured. That includes PACK_AUTHENTICATION, the PR #473 contrast replay repair.
- **Class:** procedure/registry prerequisite plus a stale code predicate. It is not a pack defect. It needs a coordinated registry-v2 row retirement and a deriver change under the ordinary gate, and its design is ruling-bearing (it touches the clock doctrine of the A332 NETWORK-TIME-OFF-ENFORCE-01 family). The desk-day plan and the scout's critical path did not list it as a freeze prerequisite.

### Environment and procedure notes (not defects)

- **N1. The T-0 author requires HEAD = local main = origin main** (`arm_readiness.py:5594-5616`). From a clone of the unmerged desk branch, the A5 gate refuses `evidence_author_t0_reviewed_tree_mismatch` (6a). A196's acceptance says "from a clean clone at main", so the real A196 trace must be cut after the branch merges. 6b emulates that with local-only ref moves, which is the S0 §1.1 convention.
- **N2. A196 dry gate.** It reaches `evidence_author_t0_clock_attestation_missing` on the unprojected, unfrozen packs at `24741cab`. It does not need `arm_readiness.evidence`, so pack/profile resolution is proven for all three `_v5` IDs now.
- **N3. Test wall time.**
  - Serially, the five-module suite would take about 2.5 hours under current load (another session was running a full `discover`).
  - `test_receipt_histsem`'s `ReceiptHistsemRefreshLaneTests` takes about 3–5 minutes per test.
  - My first serial run of the primary clone was reaped by the harness's 30-minute background limit after about 50 tests. It was killed, not failed.
  - The rerun split the suite by module, class and method in parallel groups. All groups returned `OK` with rc 0. Transcripts: `custody/transcripts/030-tests/`, `custody/patched/tests/`.
- **N4. One-pack-per-commit projection.** `freeze_projection` refuses on any dirty tree ("v2 issuance requires a clean Git working tree"). The estate template's freeze → assert → commit per pack is therefore mandatory. Projecting three packs and then committing once fails.
- **N5. A seat slip, recorded for completeness.** My first patched-clone commit failed because zsh does not word-split a `$GC` variable. Three projection attempts then refused cleanly on the dirty tree (nothing written). They were rerun after a proper commit.

## Step-5 inputs (resolved, not used)

- **Base pinset:** `configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json`. It exists and is chain member 1 (`joulewise/arm_readiness.py:3194-3197`).
- **Successor path:** `configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json`. It is code-enumerated chain member 2 and the only digest-conditional allowlist path (`:3198-3200`). It is correctly absent, as the output is create-only.
- **Candidate manifest (`$MANIFEST`):** no committed file. The reviewed source is the mechanical generator in S0 r4 §1.3 (`docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:1199-1243`). It is generated from committed blobs at the head under test (four custody tools plus `s0-fixation-delta.patch`). Its `ci_run_id` field needs a real CI run for the claim head, and its `test_modules` list is the v4-era two-module list; reconcile both with the estate-12 §6 item 2 suite before use.
- **Custody tools at `24741cab`:** all four match their tracked GNU sidecars.
  - `build_family_marker` `e51617f9…`
  - `verify_family_marker` `a79b9cdd…`
  - `build_v4_histsem_pinset` `7358c962…`
  - `verify_receipt_histsem` `394ed199…`
- **hC:** cannot exist in a desk proof. It is Ed's out-of-band confirmation of the rendered step-6 table `d117_step6_confirmation_table_v5.json`.

## Clones and local commits (local only, never pushed; under `/tmp/dd5-clone/`)

| Clone | Head | Local commits over `24741cab` |
|---|---|---|
| `primary` | `6138faa4dea44df257e18a651a3b8f5b9a86c7c4` | `6138faa4` contrast projection-0001 |
| `patched` | `7348aece1d40ff48831ea8b7d5b075741715be79` | `c696b8b5` F1 probe generator fix + regeneration; `37cf06a6` 1.7B projection; `66a2a034` 8B projection; `7348aece` contrast projection |
| `rehearse` | `7348aece` (clone of patched) | none (the probe-2 shim was denied) |
| `sacrificial1` | `2f60038c0f2e3ee7c516e28fee3c50649c899474` | `6138faa4` (from primary); `2f60038c` refused contrast freeze-0004 (poisoned slot); main refs moved locally |
| `a5clean` | `24741cab` | none |
| `a5main` | `24741cab` | none; refs/heads/main and refs/remotes/origin/main set to `24741cab` locally |

## Receipts and transcripts (SHA-256; copies under `custody/receipts/`, `custody/transcripts/`)

- `primary` contrast `projection-0001.json`: `b7f4d87618817f465a98b9d4629bbe99de315188f0a580731827b27fb2d8b428`
- `patched` projection-0001:
  - 1.7B: `78e753d7ef2d54edaab2af612506a44851a1d66e174f8a61689c3f4c69e7bd20`
  - 8B: `ad2ad06b3fab2347496e82a198a5af02ec1e1357fb4f0db987b0234cda2d836e`
  - contrast: `67a928f7ac0c1662b7741a98f0d43f29312c3deaf20d4ef6ff22131085655feb`
- `sacrificial1` contrast `freeze-0004.json` (REFUSE): `3323977f623bd3bac271bd8846ba97012ab5abc14c3e22d83670f38825c21887`
- `sacrificial1` contrast `arm-0001.json` (REFUSE): `f1f6c4017593caf748601141c53bd74a5dded49c06e45031bdc6574a14fdee90`
- Estate anchor map: `5c1d1b40488628a9c2d0ea164a422181e10e297e16ee71b244ae24c2c24eff6e`; spec: `b2355c5ba98d25bad8b4d0730823bd914d0b7b4893547d3dd2081bd834c0204e`
- Authoring REFUSE stdout (all six identical): `616933048fd2f960c777e769cb4f8f67763d299a9ee5cbc691e287f91edb316e`
- A5 stdout:
  - `a5clean` (all three identical): `5f0fb6df…fdfee`
  - `a5main`: 1.7B `012dc3c0…d545de`, 8B `02220e0b…f2060`, contrast `e3d7f0dd…c9f7`
- Arm stdout: `d018dab7…d927`. Verify stdout: `4321b65a…b82f`.
- Machine-readable step log: `custody/steps.tsv`.

## Exact commands to rerun at the final claim head

Preconditions:

- F1 is landed and the floors are regenerated.
- F2 (the restore-recipe row retirement plus the DOCTRINE_PIN deriver) is landed.
- The desk branch is merged to main and has green CI.
- `BASE` is that full sha.

Run in zsh. `PY=/Users/edr/code/JouleWise/.venv/bin/python`. `CLONE` and `CUSTODY` are fresh.

```zsh
set -euo pipefail
PY=/Users/edr/code/JouleWise/.venv/bin/python
BASE=<full green main sha>; CLONE=<fresh>/repo; CUSTODY=<fresh>/custody; mkdir -p "$CUSTODY"
git clone --no-local /Users/edr/code/JouleWise "$CLONE"; git -C "$CLONE" checkout --detach "$BASE"
cd "$CLONE"
PACKS=(configs/campaigns/d117_floor_qwen3-1p7b_v5 configs/campaigns/d117_floor_qwen3-8b_v5 configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5)
PREDS=(configs/campaigns/d117_floor_qwen25_1p5b_v3 configs/campaigns/d117_floor_qwen25_7b_v3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3)
PIN=configs/campaigns/d117_contrast_v5/prefill_pin/prefill-prompt-pin.json
PL="$(/usr/bin/jq -er .prefill_length "$PIN")"   # private; do not print
# 1. anchors
"$PY" scripts/derive_estate_anchors.py "$CLONE" --output "$CUSTODY/estate-anchor-map.json"
# 1b. generator checks (must be rc 0 before projection)
"$PY" configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py --check --prefill-prompt-pin "$PIN"
"$PY" configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py  --check --prefill-prompt-pin "$PIN"
"$PY" configs/campaigns/d117_contrast_v5/generate_configs.py --check --panel configs/model_panels/qwen3_4bit.json \
  --model-a qwen3-1p7b --model-b qwen3-8b --decode-workload configs/workloads/real_prompts_v1.json \
  --prefill-length "$PL" --prefill-prompt-pin "$PIN"
# 2. U11 projection: ONE pack per freeze -> assert PASS -> commit unit (N4)
for p in "${PACKS[@]}"; do
  "$PY" scripts/project_identity_pins.py freeze "$CLONE/$p"   # expect status PASS, rc 0
  git add -A -- "$p"; git commit -m "estate: U11 projection $(basename $p)"
done
# 3. pre-author suite (parallelise per module/class; RefreshLane per method; ~30 min wall)
"$PY" -m unittest tests.test_arm_readiness_schemas tests.test_receipt_histsem tests.test_mint_analysis_admission \
  tests.test_d117_contrast_v5_pack tests.test_d117_floor_qwen3_v5_generate
EVIDENCE_DERIVATION_HEAD="$(git rev-parse HEAD)"
for p in "${PACKS[@]}"; do
  "$PY" scripts/author_arm_readiness_evidence.py --pack-root "$CLONE/$p" --measurement-checkout "$CLONE"  # expect PASS, 11 kinds
done
git add -A -- "${PACKS[@]}"; git commit -m 'estate: common-head evidence'; EVIDENCE_COMMIT="$(git rev-parse HEAD)"
# 4. sacrificial screen, then primary freeze (expect PASS, mutated, receipt .../freeze-0004.json)
PREFLIGHT=<fresh>/preflight; git clone --no-local "$CLONE" "$PREFLIGHT"; git -C "$PREFLIGHT" checkout --detach "$EVIDENCE_COMMIT"
for i in 1 2 3; do "$PY" "$PREFLIGHT/scripts/generate_arm_readiness.py" freeze --pack-root "$PREFLIGHT/${PACKS[$i]}" \
  --measurement-checkout "$PREFLIGHT" --predecessor-pack-root "$PREFLIGHT/${PREDS[$i]}"; done   # all must PASS
for i in 1 2 3; do "$PY" scripts/generate_arm_readiness.py freeze --pack-root "$CLONE/${PACKS[$i]}" \
  --measurement-checkout "$CLONE" --predecessor-pack-root "$CLONE/${PREDS[$i]}"; done
git add -A -- "${PACKS[@]}"; git commit -m 'estate: freeze-0004 x3'; FREEZE_COMMIT="$(git rev-parse HEAD)"
# 5. successor pinset + histsem verify + candidate marker (MANIFEST generated per S0 r4 §1.3 at BASE)
SUCCESSOR_PINSET=configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json
"$PY" scripts/build_v4_histsem_pinset.py --repository "$CLONE" --base-pinset "$CLONE/configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json" \
  --historical-head "$EVIDENCE_DERIVATION_HEAD" --current-head "$FREEZE_COMMIT" \
  --pack-root "${PACKS[1]}" --pack-root "${PACKS[2]}" --pack-root "${PACKS[3]}" --output "$CLONE/$SUCCESSOR_PINSET"
"$PY" scripts/verify_receipt_histsem.py --repository-root "$CLONE" --pinset "$SUCCESSOR_PINSET" \
  --pack-root "${PACKS[1]}" --pack-root "${PACKS[2]}" --pack-root "${PACKS[3]}" --output "$CUSTODY/receipt-histsem.json"
"$PY" scripts/build_family_marker.py --repository "$CLONE" --head "$FREEZE_COMMIT" \
  --pack-root "${PACKS[1]}" --pack-root "${PACKS[2]}" --pack-root "${PACKS[3]}" \
  --phase candidate --candidate-manifest "$MANIFEST" --output "$CUSTODY/d117_family_publication_v5.json"
"$PY" scripts/verify_family_marker.py --repository "$CLONE" --marker "$CUSTODY/d117_family_publication_v5.json" \
  --phase candidate --candidate-manifest "$MANIFEST" --receipt-out "$CUSTODY/family-marker-verification.json"
# 6. arm/verify with Ed's hC (governed non-null REFUSE acceptable without live T-0), then the A5 dry gate
for p in "${PACKS[@]}"; do
  "$PY" scripts/generate_arm_readiness.py arm --pack-root "$CLONE/$p" --arm-context "$ARM_CONTEXT" \
    --window-custody-root "$CUSTODY/windows" --expected-confirmation-digest "$hC"
  "$PY" scripts/generate_arm_readiness.py verify --pack-root "$CLONE/$p" --arm-receipt "<receipt_path from arm>" \
    --expected-confirmation-digest "$hC"
  mkdir -p "$CUSTODY/a5/$(basename $p)"
  "$PY" scripts/author_arm_evidence_t0.py --pack-root "$CLONE/$p" --custody-root "$CUSTODY/a5/$(basename $p)"
  # expect evidence_author_t0_clock_attestation_missing (requires HEAD == main == origin/main, N1)
done
```

## Exact next step

1. Land F2: retire the `clock.restore_recipe` registry row and change the DOCTRINE_PIN deriver to the permanent-OFF doctrine, under the ordinary code gate plus the ruling it needs.
2. Land F1, with a projection regression test, and regenerate both floors.
3. Rerun this proof from step 2 in fresh clones. The first new information will be whether the nine kinds after DOCTRINE_PIN derive, especially the contrast `PACK_AUTHENTICATION` replay from PR #473.
