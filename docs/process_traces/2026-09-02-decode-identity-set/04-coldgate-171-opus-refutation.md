# Cold-gate packet — consult 171 (decode-unit identity; proposed D-131 amendment)

Mandatory trigger: proposed process/contract amendment (D-131 cl.2) + a
second attempt on the same defect signature (P-8 freeze refusal, fired twice).

Read-only. Repo: /Users/edr/code/JouleWise (main @ a63d45bd). Write NOTHING
under it; TMPDIR = a subdirectory you create under
<scratchpad>/.
Python: /Users/edr/code/JouleWise/.venv/bin/python. Do NOT launch any codex/
claude process. Do NOT run canonical `unittest discover`; targeted
`python -m unittest tests.test_identity_pins` is fine.

## Packet (read all, in this order)
1. The defect and bench-verified facts: this file, §Facts.
2. Seat reports: out/171-opus-decode-identity-consult.md,
   out/171-fable-decode-identity-consult.md, out/171-sol-decode-identity-consult.md
   (all under the scratchpad above).
3. Magistrate draft ruling: 171a-DRAFT-decode-identity.md (same directory).
4. Code: joulewise/identity_pins.py (scientific_config_identity :217-236;
   freeze_projection unit derivation :1400-1470; second compare site :1614;
   receipt derivation :1148-1210); configs/campaigns/d117_contrast_v5/generate_configs.py
   (:995-1001 token-count hard fail; :1334 DECODE_PROMPT_TOKENS; declared_identity
   assembly — grep `declared_identity`); scripts/mint_floor_artifact.py:_source_regime
   (~:755-805); scripts/mint_floor_artifact_generalized.py:2322-2344;
   joulewise/analysis_engine/inputs.py:2911-2950 and :3866-3918;
   docs/decision_log.md D-044 (:2465-2513) and D-131 (:8410-8436);
   docs/contracts/d165_dominance_closeout.md:60-63, 374-438;
   tests/test_d117_contrast_v5_pack.py:662-707 and :966-971.

## Facts (bench-verified by the magistrate; re-verify any you rely on)
- Generated `_v5` decode configs carry `suite_manifest_ref`/`suite_manifest_sha256`;
  decode blocks rotate over 8 prompt manifests (`decode_prompt_index(block)=(block-1)%8`);
  per decode unit 20 configs / 8 distinct `scientific_config_identity_sha256`,
  histogram 4/4/2/2/2/2/2/2; `freeze_projection` refuses (identity_pins.py:1452, :1461-1466).
- All 8 prompts of an arm render to 42 tokens (generator hard-fails otherwise).
- `mint_floor_artifact.py:_source_regime` raises MintError("component members
  do not share one scientific config identity"); `analysis_engine/inputs.py:~3866-3918`
  returns None unless all consumer rows share one identity. A freeze-only cure
  leaves the decode floor un-mintable and the analysis unbindable.
- Nine committed frozen receipts pin derivation identity; `d117_floor_*_v5`
  plans exist nowhere yet; `producer_plan_reference` is never machine-consumed.
- The dominance-criterion registration digest
  1c0a4a119fa06984ff38082781e06bc9bd90f07eae7165359718dfb063783a2b must not change.

## Your deliverable
You are the CONTRACT-LENS REFUTER paired with a cold Fable adjudicator. Your
job is to BREAK the draft ruling, not to improve it: find every place where
(d)+census contradicts or silently weakens an existing contract (D-044 hash
equality, D-131 cl.2/cl.3, D-165 fixed four-cell census, U8 four-ID contract,
the nine frozen receipts' derivation identity, publication_privacy allowlist,
replay/verify of already-frozen prefill packs), every consumer site the draft
missed (grep for `scientific_config_identity` and for the `one identity`
refusals across scripts/ joulewise/ tests/), and any way the proposed unit-set
hash can be satisfied by a pack that D-165/D-131 would reject (e.g. a member
with an unlisted manifest sha, a floor pack with a superset). Severity-tier
each finding BLOCKER / SHOULD-FIX / NIT with the counterfactual that
demonstrates it. Write to
<scratchpad>/out/183-opus-refute-171.md
(under 120 lines, file:line for every claim) and return a 10-line summary.
