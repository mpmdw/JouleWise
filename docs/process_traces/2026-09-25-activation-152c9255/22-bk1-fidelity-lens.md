# Fidelity lens report: `docs/2026-09-25-152c9255-bk1` at `b41ccd57` vs `origin/main` `c034a56f`

**Verdict: FIX-FIRST (0 BLOCKER, 3 SHOULD-FIX, 3 NIT).** The two hard checks pass: the diff contains no MATH problem text, and it changes no file outside the allowed paths. The shas, hashes, paths and numbers all check out. Every defect is a statement that is stale or overstated compared with record 00 items 46–51, or with the ruling files.

## Hard checks

| Check | Result |
|---|---|
| (1) No MATH problem text | **PASS.** I searched for `\frac`, `boxed`, `Problem:`, `Solution:`, inline `$…$` LaTeX, MATH-dataset phrasings ("Find the", "How many", "common fraction", subject names), `test/<subject>/N.json` ids, and gold-answer or problem-text fields. The only LaTeX hits are statistical formulas for the estimator and floor: the `u_{ce}`, `f_c^J`, `F_{θ,L}` and `g(k)` expressions in the J/correct packets. "Problem" appears only as a count or id ("per-problem score records", "problem ids"), never as a statement or solution. This matches Ed's E1 answer (ids and hashes only). |
| (3) Tests | `python3 scripts/gen_state.py --check` returns rc 0. `python3 -m unittest tests.test_gen_state` ran 44 tests, all OK. |
| (4) Secrets and personal data | **PASS.** No token, key or password patterns. The only emails are the owner's passmail address (in search-query text), `noreply@anthropic.com`, and `edr@Eds-MacBook-Pro.local` in pasted git `Author:` lines, which main already has in 42 files. |
| (5) Files changed | **PASS.** 191 files: 187 under `docs/process_traces/` (2026-09-24-activation-278ebc9e and 2026-09-25-activation-152c9255), plus `docs/process/state_kernel.json`, `RUN_STATE.md`, `TASK_QUEUE.md` and `tests/test_gen_state.py`. Nothing else. |

## Spot-checks (about 45 claims, all match unless listed under Findings)

- **Shas (25):** all resolve. `75d04e9e` is the PR #409 merge and `c034a56f` is the PR #410 merge. The other 22 commits resolve too, and `72148bfe` is a blob. The branch heads match record 00: PR-L `26c52306`, PR-R `62db28b7`, PR-0 `576f3989`, harness `4bcddb49`, reducer `8d06633e`.
- **Cold-gate packet sha256 (11 of 11):** all match record 00 items 12, 13, 15, 17, 21, 24, 32, 33, 36, 49 and 50.
- **Record 00 relative links:** every one exists.
- **Numbers that match their sources:**
  - Interactive 131.6 ms (max 143.9) and default 46 % of intervals over 0.25 s: 05/20:26,52.
  - "9 of 11" B values outside r7's range: 05/21:18.
  - ×2.07 frames gave ×1.57 median B, so about +6 %: 05/30/21:46–47.
  - Probe criterion 300 frames, 55 s, median ≤ 150 ms, max ≤ 200 ms: 05/30/21:36,72.
  - Positive control median 125.6 ms, p95 128.6, max 132.8, 38.6 s, QoS `0x15`: `11-prl-bench-smoke/interactive-positive-control.json`.
  - 25–89 % false admission: 0.250–0.890 in 13/20.
  - Synthesis 0.39–0.81: 10/30.
  - Power 0.20–0.37 at n = 128 and 0.36–0.63 at n = 200, SD(ln p̂) = 0.39: 13/30/21:15–20,39.
  - Census 368/720/911/953/1,022 and power 0.51: 18/01:7,54.
  - Astra min(600, available): 18/02.
  - Census with floor 128: 18/10.
  - 54 tests in 1,243 s: 16/01:8.
  - 484 tests and the 25.9 % refusal rate: 17/02:52,139.
  - 387 tests, 17 tests, `211ed076…`: 15/05.
  - 7 of 9 survivors: 12/03. 7 of 10: 12/06:11. KeyError at `paper_custody.py:632`: 12/06:32.
  - 1,112 / 271 / 1 / 840: 19/01:41,99.
  - Survivor breakdown: I recomputed it from 20/ex-01. By operator: if→False 361, or-delete 235, and-delete 165. By file: 770 in `artifact.py`, 38 in `multiplicity.py`, 11 in `paper_custody.py`.
- **Epoch and code citations:**
  - The custody cutoff `1790340000` is 05:40:00 PDT on 09-25.
  - The tokenizer prefix `aeb13307a71acd8f` is in `configs/model_panels/qwen3_4bit.json`.
  - `paper_custody.py:632` and `:1345-1347` say what the record says.
- **Kernel:**
  - Task counts: 244 + 7 − 1 + 5 = 255, which equals the actual count. The quiet_mac count is 16.
  - Lanes: 12 added and 1 removed (HEADLINE-PACKER-RECUT-01). Four were updated: ACCEPTANCE-EPOCH-25G83-01, A282, A283 and A292.
  - Every repo path cited in the added or updated lanes exists.
  - The JCORRECT-NULL, V1-ISSUANCE, GOLDEN-SWEEP-OPERATORS (refuter B-2, 14/21:35–41), A292 and ACCEPTANCE summaries are faithful to their sources.

## Findings

### SHOULD-FIX

**S1 — `RUN_STATE.md:13`: the scorecard claim is overstated.**
The text says: "**All four first cold rulings missed at least one BLOCKER that the paired Opus refuter caught.**" The primary sources support that for two of the four gates:
- Acceptance: B1 and B2 were affirmed as BLOCKERs (05/30/21).
- Claim-gate wiring: C-1 was affirmed as a BLOCKER (06/30/21).

They do not support it for the other two:
- A292: the addendum downgraded refuter B1 and B2 to MATERIAL (`09-coldgate-packet-a292/30-addendum/21-…:185`; record item 28).
- J/correct: the refuter only affirmed the P-0 BLOCKER that was already known, and added MATERIAL findings (13/21:5–7,145; record item 36).

This line feeds the Opus-vs-Fable scorecard that Ed's evaluation directive depends on.
**Fix:** "In two of the four gates (acceptance and claim-gate wiring), the first cold Fable ruling missed a BLOCKER that the paired Opus refuter caught and the addendum affirmed. At A292 the refuter's two BLOCKERs were ruled MATERIAL. At J/correct the refuter added MATERIAL findings only."

**S2 — `RUN_STATE.md:20,23` and `:24-25`: the top block is stale against record items 47–51, which this branch carries.**
- Line 20 says PR-0 "one round is running". Item 47 says the ruled round **FAILED** R-6 with 840 unlisted survivors, and item 49 opened re-scope cold gate 20.
- Line 23 says HEADLINE-POWER-01 "has Opus and Astra rulings running". Items 48 and 50 say both rulings returned. The magistrate decided a census with a floor of 128 (18/10), and the Fable final pass is packet 21.
- The PR-L entry does not mention item 51's FIX-FIRST B1: `measurement_root_outside_custody` is missing from `arm_retry.COLD_GATE_CODES`.

**Fix:** update those three bullets. For example: "PR-0 ruled round failed R-6 (840/1,112 unlisted survivors); re-scope cold gate [20] pending." / "HEADLINE-POWER-01: magistrate decision census, floor 128, Holm m = 5 ([18/10]); Fable final pass [21] pending." / "PR-L: Opus lens FIX-FIRST (B1 arm_retry code, S1 rehearsal reading); fix round 1 dispatched." Then insert the re-scope gate into the successor order.

**S3 — `docs/process/state_kernel.json:3879` (HEADLINE-POWER-01), with its regenerated row at `TASK_QUEUE.md` (A303), plus `state_kernel.json:1667` (CLAIMGATE-V2-IMPL-01):**
- HEADLINE-POWER-01's `status_note` says "no n_acc decision recorded yet". The decision is recorded at 18/10.
  **Fix:** "Magistrate decision 18/10: census, floor 128, Holm m = 5, SESOI Δ_L = 0.3. Opus df rule and FPC on V_acc routed to Fable final pass packet 21 (sha 59aefd07…)." Then regenerate.
- CLAIMGATE-V2-IMPL-01 still has its `CLAIMGATE-WIRING-01` event dependency in `state: pending, evidence: null`, while its own note says the design is ruled (WR-0..WR-10).
  **Fix:** set that dependency to `satisfied` with evidence `docs/process_traces/2026-09-25-activation-152c9255/06-coldgate-packet-cgw/30-addendum/21-coldgate-fable-cgw-addendum-ruling.md`, and add a pending dependency on PR-0 merging, which is the real blocker the note names.

### NIT

**N1 — `RUN_STATE.md:27`:** "Record 00 items 1–121". The 278ebc9e record runs to item 122 (the exit email `1a0d849df1458977`). **Fix:** "items 1–122".

**N2 — `RUN_STATE.md:16`:** "bench-proven both ways". Only the positive control has a committed artifact (`11-prl-bench-smoke/interactive-positive-control.json`). The negative control (173.2 ms, max 262.3 ms, REFUSED) appears only in record item 26 and in 17/02's citation of it. **Fix:** commit the negative-control capture summary as `11-prl-bench-smoke/default-context-negative-control.json`, or reword to "positive control committed; negative control recorded in item 26".

**N3 — `RUN_STATE.md:23`:** "power 0.20–0.37 at Δ_L = 0.3 with n_acc = 128" leaves out the ≈0 power at a hard level with a cell near p = 0.05 (13/30/21:39). That qualifier matters, because the census decision exists largely to fix it (18/01:54). **Fix:** add "(≈0 at a hard level with a cell near p = 0.05)".

The Claude.ai "Anthropic Economic Index" connector still needs authorisation in the claude.ai connector settings. I did not need it for this review.
