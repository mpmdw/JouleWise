# L5 PACK/READINESS/CUSTODY — instrument-readiness audit report (xhigh seat)

**Charter:** docs/process/instrument-readiness-audit-charter.md (v2 RATIFIED). **Audit baseline:** docs/process/audit-baseline-manifest.json at HEAD `ac3fe1d2fb46ab02b2f70eba387165d63bc1de6b` (== origin/main at manifest commit). Audit worktree HEAD `8937dec`; the two post-manifest commits (`d279a7c`, `8937dec`) touch only README.md and RUN_STATE.md — **no artifact in L5 scope changed after the manifest; these results are not voided** (charter amendment 12 checked, not assumed). Boot session at audit time: `DA90818C-9C31-45D0-8813-DEAE65FBA143` — **unchanged since freeze night**; the frozen evidence receipts remain live.

## 1. Evidence universe (enumerated before findings)

| # | Artifact / behavior | Examined |
|---|---|---|
| U1 | ALPHA pack `configs/campaigns/d117_floor_qwen25_1p5b_v1` (154 committed files) | YES — every byte hashed |
| U2 | 7B pack `d117_floor_qwen25_7b_v1` (154 files) | YES |
| U3 | Contrast pack `d117_contrast_qwen25_1p5b_vs_7b_v1` (135 files) | YES |
| U4 | Three pack generators' freeze-aware behavior (preserve-current-bytes mode) | YES — executed + branch-read |
| U5 | D-134 freeze receipts ×3 + sidecars + plan-tree pins | YES — replayed twice (two heads) |
| U6 | U11 projection receipts ×3, `joulewise/identity_pins.py` freeze/verify | PARTIAL — bytes/pins verified, 25 tests green; internals not line-read |
| U7 | 33 evidence receipts + 33 sources + sidecars (freeze-side, #145-authored) | YES — every sha + fact source |
| U8 | `joulewise/arm_readiness.py` lifecycle (digest, freeze, dry-run, arm, verify, consume, namespace scan) | YES — key paths read + probed |
| U9 | Freeze-side evidence author (`arm_readiness_evidence.py` + CLI) as landed | YES |
| U10 | Arm-side t0 author (`arm_readiness_evidence_t0.py` + CLI) as landed | YES |
| U11 | `scripts/generate_arm_readiness.py` CLI (freeze/dry-run/arm/verify/consume) | YES |
| U12 | Row registry binding (`configs/arm_readiness/d117_row_registry_v1.json`) | YES — sha-verified everywhere |
| U13 | External custody layout `~/JouleWise-window-custody` + dry-run receipt | YES — inspected + authenticated |
| U14 | Measurement checkout `/Users/edr/JouleWise-measurement-20260813` | YES — head/clean verified, read-only replay executed |
| U15 | Runbook receipt-lifecycle sections (§5C, E-steps, t0 author, arm/verify/consume) | YES |
| U16 | Governing records: freeze log, M-1/M-2 rulings, alpha_arm_readiness.md, baseline manifest | YES |
| U17 | CI behavior of the pack-integrity plan tests | **NO — no network; see finding 1** |
| U18 | Live arm-night executions (t0 author, dry-run at final head, arm/verify/consume, U11 live verify) | **NO — T-0/lead work by design; covered by 58 landed tests** |

**Coverage: 16/18** universe classes examined; the two unexamined classes are listed plainly above and in §5.

## 2. Executed positive probes

1. **Digest re-verification (mechanical, production code):** `committed_pack_tree_sha256` over all three packs at the baseline bytes → exact match to the manifest's three `pack_digests`. The digest walk itself verifies disk==HEAD for every pack file and refuses untracked/symlink/mode anomalies.
2. **Independent integrity sweep (my own code — not the project's verifier):** all sidecars (15×3) authenticate exact bytes; plan_tree pins (freeze receipt, projection receipt `state: frozen`, 100/100/80 identity-unit config-inventory shas) match; all 33 evidence receipts match the freeze receipts' sha bindings with **exact** namespace inventories (no extra, no missing); all fact sources authenticate; registry sha `d248fdc5…` uniform across receipts/plan_trees/manifest; contrast downstream pins (analysis manifest `e3bc0e36…`, consumer declaration, prefill prompt vs plan-test literal) match. **ALL-PASS.**
3. **Generators `--check` ×3** at the baseline bytes: exit 0 — the freeze-aware generators preserve the frozen bytes (M-2 as implemented).
4. **Full freeze-reference replay, no patches, in the real measurement checkout** (read-only, its own code, frozen head `49dcc49`): PASS, 0 refusals, ×3; committed digests reproduce the freeze log exactly (`6246b618…`, `1ef189a8…`, `6a6865ae…`) — the freeze-night state is intact on disk today.
5. **Freeze-reference replay at the baseline bytes** (TMP clone, current code, only the absolute-checkout-path binding neutralized — that binding separately proven live in N1): PASS, 14 rows, 0 refusals, ×3 — the frozen evidence chain authenticates under the post-#149 head, including the **live boot-session check**.
6. **Test suites as landed:** pack_digest 6 OK; schemas+registry 17 OK; identity_pins 25 OK; lifecycle 12 OK; evidence_author + evidence_t0 + dry_run + integration 58 OK.
7. **External custody:** layout `<custody_root>/<pack_id>/arm_readiness.dry_run.receipts/` as contracted; `dry-run-0001.json` sha `94837218…` matches the freeze log; PASS with the four hash-bound checks and eight omitted live domains; no arm/consumption receipts pre-exist (correct — arming hasn't happened).

## 3. Executed negative probes / READY-falsification attempts

All tampers ran in a disposable clone of the audit tree; the worktree is byte-identical at exit.

| ID | Attack | Outcome |
|---|---|---|
| N1 | Replay from a different absolute checkout path | **REFUSED** `readiness_freeze_receipt_mismatch` — receipts bind the exact measurement-checkout path |
| N2 | Foreign file (`__pycache__`) inside a frozen pack | **REFUSED** `readiness_pack_not_committed` (untracked pack directory), .gitignore notwithstanding |
| F1 | Uncommitted one-byte member-config tamper | **REFUSED** `readiness_pack_digest_mismatch` |
| F2 | The same tamper **committed** | digest≠manifest **CATCH**; generator `--check` **REFUSED** ("generated file drifted"); plan-tree/U11 inventory pin **CATCH**; freeze-replay alone passes (documented residual, triple-covered) |
| F3 | Evidence receipt tamper, committed, **sidecar regenerated consistently** | **REFUSED** `readiness_evidence_digest_mismatch` (freeze receipt's own sha binding) |
| F4 | **Receipt replayed across packs** (7B freeze receipt into ALPHA, committed, sidecar consistent) | **REFUSED** `readiness_freeze_receipt_mismatch` ("plan freeze reference is not exact") |
| F5 | **Evidence replayed across packs** at the arm/custody binding layer | **REFUSED** `readiness_evidence_digest_mismatch` ("evidence item is stale for pack or HEAD") |
| F6 | Committed `plan_tree.json` science-row tamper + regenerated sidecar | freeze-replay **PASSES** and `--check` **PASSES**, printing the tampered sha as "verified" (**the echo hole — finding 2**); catches: baseline-manifest digest mismatch (executed) and the plan-test literal pin (executed FAIL on the tamper — but see finding 1) |

Both seat-mandated falsifiers (tampered pack byte per layer; receipt replayed across packs) were executed, with per-layer catch/no-catch recorded rather than asserted.

## 4. Findings (severity-tiered)

**F-1 SHOULD-FIX — Floor-pack plan tests self-pollute the frozen packs and fail deterministically from a clean tree; their CI-green status is unexplained.** `tests/test_d117_floor_qwen25_1p5b_plan.py:30-35` exec-imports the pack generator at module import, which writes `__pycache__/generate_configs.*.pyc` **into the frozen pack**; the inventory test (`:259-264`, unfiltered rglob) then fails. Reproduced from a byte-clean tree on python3.13 **and CI's python3.11**; same pattern in the 7B test; the contrast test already carries the fix (`test_d117_decode_contrast_plan.py:59-65`, commit `e286e75` — "passed fresh and failed every rerun"). Failure scenario: (a) the plan-test literal pin is the principal automated catch for committed plan_tree drift (F6) — if CI is red or red-masked on these modules, that catch layer is not real; (b) running these tests in the measurement checkout leaves `__pycache__` in the frozen pack, after which **every** `committed_pack_tree_sha256` caller (t0 author, arm, consume) refuses "untracked pack directory" until manual cleanup — an arm-night tripwire (refusal executed live). Fail-closed, but a falsely-green integrity test is exactly the charter's anti-ritual target.

**F-2 SHOULD-FIX — Preserve-mode `--check` echo hole.** In the current frozen state, all three generators **echo** `plan_tree.json`, `plan_tree.sha256`, and `producer_contract.json` from disk into the "generated" output (`d117_floor_qwen25_1p5b_v1/generate_configs.py:1803-1813,1987-1998`; 7B `:2185-2193`; contrast `:1683-1697`), so `--check` compares those files with themselves and reports "verified" (F6 executed: tampered sha printed as verified). The D-134 freeze receipt binds calibration_plan + registry + evidence but **not plan_tree bytes** — plan_tree is the in-pack authority root whose cross-commit integrity currently rests only on the plan-test literal (see F-1), the off-repo baseline manifest, and merge review. Work order: bind a plan_tree digest at freeze (attachment-excluded hash in the freeze or projection receipt) or restore genuine regeneration for these members.

**F-3 SHOULD-FIX — Pre-arm sequence unregistered; the §5C dry-run receipt is stale by binding.** The measurement checkout sits at `49dcc49`, which **does not contain the arm-critical t0 author** (#149). After it advances, `_latest_dry_run_binding` (`arm_readiness.py:3402-3425`) requires the dry-run to bind the current head + committed digest; `dry-run-0001` binds `49dcc49`/`6246b618…`, so any arm at the baseline head refuses `readiness_dry_run_stale`. Mechanically fail-closed — but no register (RUN_STATE ED-OWED, 70h plan, ED-QUALIFICATION script) carries the required steps: advance checkout → re-execute §5C dry-run at the final head under the night's custody root → E-steps/t0/arm. The freeze log's X-8 line ("the freeze + dry-run pair discharges the validator role") reads as if the existing receipt carries over; it does not.

**F-4 NIT** — `--check` prints "verified **unfrozen draft**" on frozen packs (`generate_configs.py:149-157,2168-2171`; M-2-acknowledged byte-preservation cosmetics).

**F-5 NIT** — decision-log M-2 remedy wording ("regenerates the sidecar-consistent text") vs the implemented preserve-bytes behavior; `alpha_arm_readiness.md:31-35` states the operative reading. Consistency-sweep material so a future session doesn't "fix" frozen bytes.

**Positive observation (for the sitting):** the sanctioned post-freeze pack delta `49dcc49→ac3fe1d` is exactly the three `generate_configs.py` files (verified by git diff); the manifest digests were taken after it; the freeze evidence chain deliberately binds plan+evidence+boot rather than head, so it survives that delta — and my P2 replay proves it does.

## 5. Unexecuted obligations

1. **CI log pull for the floor-pack plan-test shard** (no network here) — highest-value refuter follow-up for F-1.
2. **Live arm-night chain** (dry-run at final head, t0 author, arm/verify/consume, U11 `verify_frozen_projection` with real model bytes) — T-0/lead work by charter design; covered here by 58 landed tests + code read, not execution.
3. **`identity_pins.py` internals** — audited via tests, receipt bytes, and the F2 inventory-pin catch; not line-read.
4. **Arm-packet document content** (custody `t4-session-20260810/`) — located, not audited (seam seats' territory).

## 6. ED-QUALIFICATION rows

- **ED-QUAL-L5-1** (stable, any tap block): one non-window rehearsal of the t0 **clock-attestation input handshake** — Ed captures real `sudo systemsetup -getusingnetworktime` / `-setusingnetworktime off` outputs per runbook E-4/E-5 into a scratch `arm_readiness.t0.inputs`; validate them against `arm_readiness_evidence_t0.py:838-861`'s capture validators. Landed tests use synthetic captures only; the first real sudo-output shape mismatch must not surface at T-0.

## 7. Component verdict

**NOT-READY**, with three bounded work orders (WO-L5-1 fix + CI-truth determination for the floor plan tests; WO-L5-2 close the `--check` echo hole / bind plan_tree at freeze; WO-L5-3 register the pre-arm sequence). The core custody machinery itself verified strongly: every digest, sidecar, pin, receipt, and namespace re-verified mechanically from primary bytes; the full freeze chain replays PASS at both the frozen head and the baseline bytes; every executed falsifier was refused by at least one layer, with each layer's catch/no-catch honestly recorded. Nothing found arms falsely or consumes falsely — the NOT-READY is carried by a compromised audit layer (F-1: a pack-integrity test that fails clean while believed green) plus two closable gaps, not by the receipt lifecycle. Tree left byte-identical (git status + diff empty at exit; scratch clone destroyed).