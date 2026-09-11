# THREE-PACK FREEZE EXECUTION LOG — 2026-08-13 (T6 magistrate, lead-run)

Authority: the freeze-execution checklist (T6 mechanic, 9 contradictions
pre-flagged), D-134's critical path, D-131, the evauth cold-gate synthesis.
All commands run personally by the magistrate in the clean measurement
checkout /Users/edr/JouleWise-measurement-20260813 (full clone, not shallow).

## Sequence as executed (deviations from the checklist recorded inline)

1. Reviewed head selected: bc7e255 (post-#145; HEAD == main == origin/main,
   clean). .venv built; editable-install egg-info artifacts REFUSED by the
   whole-tree gate (fail-closed working) — cured by uninstalling (scripts
   self-insert sys.path; only mlx needed in the venv).
2. One-shot regeneration byte-check: all three generators --check PASS at the
   reviewed head (shas matching #144's regeneration transcript).
3. U11 freeze attempted first per the checklist — ALPHA PASS, then 7B/GAMMA
   REFUSED on the TREE-WIDE cleanliness gate (each freeze's uncommitted
   mutations block the next): per-pack commit+push cycles required.
   **DEVIATION 1 (X-2 one level deeper):** the evidence author's
   PACK_AUTHENTICATION deriver runs generator --check, which post-U11-freeze
   refuses on projection-receipt inventory extras. The three U11 freeze
   commits were REVERTED (custody-honest revert commit), evidence was
   authored on the unfrozen tree, then U11 re-froze. Corrected net order:
   --check -> AUTHOR EVIDENCE x3 (+commit each) -> U11 freeze x3 (+commit
   each) -> D-134 freeze x3 (+commit each).
4. Evidence authoring (lead-run, #145 tool): ALPHA/7B/GAMMA each PASS with
   11 receipts (ACCEPTANCE_SUCCESSOR NOT_APPLICABLE under issued D-079).
   Boot session at authoring: DA90818C-9C31-45D0-8813-DEAE65FBA143 (live
   sysctl check). **SYNTHESIS AMENDMENT (recorded):** the cold-gate
   adjudicator's condition 8 (author-then-reauthenticate returning PASS
   mutated:false) is STRUCTURALLY UNSATISFIABLE as written — pre-commit the
   untracked evidence makes the committed-pack digest uncomputable; post-
   commit the HEAD moves and the head binding refuses evidence_author_
   existing_stale (exactly the refuter's NEW-FINDING D; the refuter's
   minimum set never included condition 8). Its substance is held by the
   lead-run fresh derivation, the D-134 freeze re-validation, and the
   head/boot-session anti-drift binding — whose refusal was WITNESSED live
   during this execution, proving the mechanism. The magistrate's original
   synthesis adopted an impossible condition; the amendment adopts the
   refuter's position. One process error recorded: the first ALPHA commit
   ran on a compound whose parse step swallowed the reauthenticate REFUSE
   exit — the commit stood only because the refusal was then diagnosed as
   the anti-drift mechanism (not bad evidence); later packs used a real
   exit-code gate.
5. U11 freeze x3: ALL PASS (GAMMA with its four ordered identity units per
   D-131 cl.2). ALPHA's re-frozen projection receipt sha (98584bbb...)
   differs from the reverted first freeze (c40a25bb...) — expected: byte-
   idempotency applies to re-freezing an already-frozen pack; a fresh
   freeze binds a fresh live-probe inventory. Informational.
6. D-134 freeze receipts x3: ALL PASS, arm_disposition NOT_APPLICABLE,
   receipts pinned into plan_tree. Frozen head: **49dcc49**.
   Committed-pack digests (joulewise.committed_pack_tree_sha256.v1):
   - d117_floor_qwen25_1p5b_v1: 6246b61858820da7f9349459cce194bf994edd70b24fc0ab44509d6d821523f1
   - d117_floor_qwen25_7b_v1:  1ef189a86156d42b11b5aab123abbb21 (prefix; full in receipt)
   - d117_contrast_qwen25_1p5b_vs_7b_v1: 6a6865aebd7030ea52a855ae5420a0a4 (prefix)
7. §5C LEAD LIVE VERIFICATION (rule 1, personally): under-lease synthetic
   rehearsal on ALPHA — receipt dry-run-0001 (sha 94837218...), status PASS,
   all four hash-bound checks PASS (real_reservation_cli_execute,
   real_writer_entry_pre, real_writer_entry_post, same_head_pack_binding),
   all eight omitted live domains enumerated, pack digest binding verified
   against the magistrate's independent digest computation.
   **X-8 RULING (recorded):** the D-134 freeze + dry-run pair discharges the
   runbook's "frozen readiness-validator command" role; prewindow_check.sh
   --wait executes at arm time, where its wait IS the mandated idle (D-5).

## Standing constraints for tonight (Window ALPHA)

- NO REBOOT between freeze and T-0 (boot session DA90818C...; a reboot voids
  all twelve evidence receipts per pack — recovery: git rm -r the pack's
  arm_readiness.sources + arm_readiness.evidence, re-author, re-freeze).
- Collection close-out gates on the WO-COLLECTION-MARGIN-01 receipt
  (record_window_duration_margins after post-calibration, before
  backup/extraction).
- Quiet lock from arm onward: no agent fleets, no Sol sessions, no monitors
  during measurement.
