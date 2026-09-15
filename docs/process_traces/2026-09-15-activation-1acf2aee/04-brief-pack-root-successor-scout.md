# Scout brief — PACK-ROOT-SUCCESSOR-V5-01: what does it take for the three registry-named _v5 successor packs to resolve through the T-0 author from a clean clone at main? (read-only; xhigh; one seat)

SESSION_MODE: delegated
WRITE_SCOPE: []

Work read-only in `/Users/edr/code/JouleWise-wt-pack-root` at `3d5b7623` (= origin/main). Temp dirs under `/tmp` allowed (`/tmp/magistrate-1acf2aee/pack-scout/`); never touch `/Users/edr/code/JouleWise` (frozen canonical root), `/Users/edr/JouleWise-measurement-*`, `/Users/edr/JouleWise-desk-proof-*`, or `/Users/edr/night-custody`. No network. Single test modules and snippets only; no full suite.

## The row (kernel `PACK-ROOT-SUCCESSOR-V5-01`, agent lane, p1, READY)

Goal: "The live arm-readiness registry's successor_pack_ids name three _v5 Qwen3 packs whose directories hold no plan tree (two) or do not exist (one), so no committed pack root on main resolves through the T-0 author; the first TRANSACTION_PACK night cannot pass its T-0 until a real successor pack exists or the roster is ruled."
Acceptance: "The three successor packs the live arm-readiness registry installs (ALPHA/BETA/GAMMA, all _v5 Qwen3) exist as complete TRANSACTION_PACK pack roots on main — plan_tree.json with claim_root_leaf/bound_root_leaf, calibration_plan.json, arm_readiness.evidence — so scripts/author_arm_evidence_t0.py and the pack-night T-0 resolve a profile from a clean clone at main; or the registry names packs that do exist, by a ruling on the roster (a roster change is Ed's to decide on its own merits, cold gate 65 Q1). Proven by the A5 dry gate from a clean clone at main refusing with evidence_author_t0_clock_attestation_missing (not readiness_row_registry_mismatch or readiness_pack_unreadable), recorded in a trace. Lands under the twelve-row gate; sequenced before the first TRANSACTION_PACK arm."
Status note's design question: "build the ALPHA/BETA packs from their generate_configs.py under the freeze/registry contracts, or rule the roster." A roster ruling is Ed's; this scout maps the BUILD route and states honestly whether it is the right one.

## Facts already established (verify, do not re-derive)

- `configs/arm_readiness/d117_row_registry_v2.json:532-536` installs ALPHA `d117_floor_qwen3-1p7b_v5`, BETA `d117_floor_qwen3-8b_v5`, GAMMA `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5`.
- `configs/campaigns/d117_floor_qwen3-1p7b_v5/` and `…/d117_floor_qwen3-8b_v5/` hold ONLY `generate_configs.py`; `…/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/` does not exist; `configs/campaigns/d117_contrast_v5/` holds `generate_configs.py` plus two D-166 registration JSONs (`d166_dominance_criterion_registration.json` is the `registration_path` the derivation nights authenticate).
- Complete historical pack roots exist for comparison: `configs/campaigns/d117_floor_qwen25_1p5b_v{1,2,3}`, `d117_floor_qwen25_7b_v{1,2,3}`, `d117_contrast_qwen25_1p5b_vs_7b_v{1,2,3}` (each has `plan_tree.json` etc.).
- `joulewise/arm_readiness.py:4446-4472` `_plan_profile` resolves a pack through the registry's `successor_pack_ids`; record `docs/process_traces/2026-09-13-activation-24b9d3dd/66-r3-desk-proof-scaffolding-opus-report.md` §4 shows the dry-gate refusals `readiness_row_registry_mismatch` (for a v3 pack) and `readiness_pack_unreadable` (for the empty _v5 dir); cold gate 65 ruling `…/65-coldgate-packet-desk-proof/10-coldgate-fable-ruling.md` §3 and the pairing refuter `12-opus-pairing-refuter-on-ruling-10.md` carry the severity note and hygiene finding.
- The Qwen3 model pair, the _v5 ladder and its freeze contracts are ruled elsewhere: find the owning decisions (search `docs/decision_log.md` for `_v5`, `Qwen3`, D-166, D-167, D-173, D-176, `freeze`, `pack_sha256`, `plan_sha256`) and cite them; do not re-decide them.

## Questions

Q1. What EXACTLY is a complete TRANSACTION_PACK pack root: enumerate the files and the fields the T-0 author (`scripts/author_arm_evidence_t0.py`) and `joulewise/arm_readiness.py` read from it, with the validating code lines, and the digests (`pack_sha256`, `plan_sha256`, `pack_digest_algorithm`) — what is hashed, over what byte set, and where the expected values are pinned (registry rows? freeze evidence? the plan tree itself?).
Q2. What does each `generate_configs.py` produce when run, and is its output the complete pack root or only part of it? Run each one into a temp copy of the tree (never in place) and diff the result against a historical v3 pack root's file set; paste the file lists. Say what is missing and where it would come from (calibration_plan.json? arm_readiness.evidence? freeze evidence?).
Q3. The freeze/registry contract: which registry rows, freeze-evidence lifecycle fields, and decision-log clauses must be satisfied for a NEW pack root to be admissible (D-139 successor name shapes, R1 lifecycle, `readiness_row_registry_mismatch` paths), and which of those require a ruling (Ed/cold gate) versus mechanical generation.
Q4. GAMMA: the contrast pack's directory does not exist; is `d117_contrast_v5/generate_configs.py` its generator under a different directory name, and what does the registry expect the GAMMA pack path to be?
Q5. The proof: write the exact A5 dry-gate command sequence from a clean clone at main that the acceptance names ("refusing with evidence_author_t0_clock_attestation_missing, not readiness_row_registry_mismatch or readiness_pack_unreadable"), citing the code that emits each of those three refusals and the order they are checked in.
Q6. Honest assessment: is BUILD the right route, or does building the packs pre-empt a decision that is Ed's (pack contents = the pre-registered campaign; the roster)? If parts are mechanical and parts are ruling-bearing, separate them.
Q7. Parcel: the implementation seats (files per seat, WRITE_SCOPE, order), the tests that pin the result, and the twelve-row gate inputs.

## Deliverable

claude-codex-report/v1, genre scout, as your FINAL MESSAGE, under 8000 bytes: answers Q1–Q7 with grounded evidence (file:line, commands + short output), "what the lead should double-check", "where I disagree with the brief". Do not write any file inside the worktree.
