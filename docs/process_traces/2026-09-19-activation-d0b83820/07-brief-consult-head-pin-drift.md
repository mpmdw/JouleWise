SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Design consult (read-only, one round, explicit licence to disagree) — committed ledger head pin vs. issued-acceptance cutoff vs. generator pinned inputs

Cwd is a clean linked worktree at main `2f79e633` (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; write nothing but `/tmp` scratch; no `sudo`, no `powermetrics`, no live capture. Run tests you need with `/Users/edr/code/JouleWise/.venv/bin/python -m unittest …` (read-only use of that venv). Do not end your turn before every question below has an answer or a named reason it has none.

## The facts (lead-verified this morning; cite file:line yourself before relying on them)

1. The repo-committed ledger head pin `configs/calibration/calibration_ledger_head.json` is the D-109 R1.4 anti-rollback trust anchor. It was issued at sequence 76 / `08456d50…` with the D-079 acceptance (D-116, `docs/decision_log.md` ~line 7982). Two derivation-kind ledger sessions ran on 2026-09-19 (equivalence nights n1 and n2 under directive issue 316; 12 slots each) and the runbook's documented desk step (`docs/phase_2/derivation_night_runbook.md` §3 item 4, `recover_calibration_ledger.py advance-head-pin`) advanced the pin to 126 (`e39b45e6`, 03:12) and then 176 (`1278b9f7`, 07:45). Both commits are on main. The pin MUST stay on main: the next measurement clone's §0.4 readiness check refuses a physical ledger ahead of the committed pin.
2. Hosted CI on main has been RED on the quick tier since `22b92ec7` (run 35436788888, 10:13Z) and again at `2f79e633` (run 35449733694). The green runs between them skipped the quick tier (docs-only change filter). Three tests fail, all on the pin value:
   - `tests/test_calibration_bracketing.py:635` `test_live_issued_anchor_authenticates_and_matches_committed_head_pin` asserts the ACTIVE acceptance artifact's `ledger_cutoff` (r6: sequence 76) EQUALS the committed pin (now 176).
   - `tests/test_campaign_generator_core.py:148` and `:185` (`test_counterfactual_local_write_boundary_cannot_bypass_shared_core`, `test_exact_alpha_local_validator_evasion_is_detected`) run every `configs/campaigns/d117_*/generate_configs.py` in regenerate mode; each generator pins `LEDGER_HEAD_REL` with a frozen `LEDGER_HEAD_FILE_SHA256` (e.g. `configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py:113` and the drift loop at `:1962-1969`) and raises `pinned input drifted: configs/calibration/calibration_ledger_head.json`. Twelve generators pin that file (`grep -ln calibration_ledger_head configs/campaigns/*/generate_configs.py`).
   - `tests/test_arm_readiness_evidence_packauth.py:587` shows the drift refusal is INTENDED behaviour for regenerate mode once any pinned input moves; `--preserve-current-frozen-bytes` (echo mode) is the sanctioned path for a frozen pack.
3. Context that bears on the answer: the acceptance in force (`d079_calibration_acceptance_v2_n17_r6`) binds identity epoch 25F84; the machine is on 25G83; the equivalence check FAILED this morning (`docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md`, on main), so no G2-a window can be generated or armed under r6 on this machine until a successor acceptance issues or Ed rules. The 100 appended rows are derivation-night observations that belong to no issued acceptance's corpus. D-161 (threat-model prune): the only adversary is the operator; fail-closed stays only for physics, evidence and pre-registration fences. Ed's sensible-gates directive: tolerances sized to the instrument, never microscopic; "no silly gates on accepting numbers".

## Questions

Q1. What invariant SHOULD hold between an issued acceptance's `ledger_cutoff` and the committed head pin once later sessions have legitimately appended? Candidates: (a) equality (the current test; implies the pin may never advance while an acceptance is in force, contradicting runbook §3 item 4 and D-109's own append protocol); (b) `cutoff.sequence <= pin.sequence` and the cutoff digest authenticates as the chain digest AT `cutoff.sequence` (a prefix relation; say how to verify it in CI, where the physical ledger is absent — is the pin file alone enough, or must the artifact carry a prefix witness?); (c) something else. Cite the contract text (`docs/contracts/calibration_ledger_append.md`, D-109 R1, D-116) that decides it, or say the contract is silent.

Q2. What should a campaign generator's `LEDGER_HEAD_FILE_SHA256` pin MEAN: the head at generation time (so any later append forces regeneration = a new family generation, per MIDCAMPAIGN-CURE-GENERATION-01's recorded limitation), or the acceptance's `ledger_cutoff` (so the pack binds to the acceptance that licenses it, not to unrelated later rows)? Which packs are frozen/historical (never regenerated; echo mode only) and which are live? For each class, what is the correct behaviour of `test_campaign_generator_core` — should it fixture-stub the head-pin input as it already stubs the prefill pin (`fixture_prefill_pin`, `configure_generator`), or run against the live file?

Q3. Propose the MINIMAL fix-forward that (i) keeps every soundness fence (D-109 anti-rollback: a pin ROLLED BACK below the cutoff must still refuse; drift refusal on regenerate of a frozen pack must still fire), (ii) turns the quick tier green on main, and (iii) needs no re-generation of any frozen pack. Give the exact diff shape per file, the defect-shaped regressions to add (pin advanced past cutoff → authenticates; pin rolled back / cutoff digest mismatched → refuses; frozen pack regenerate with a drifted NON-ledger input → still refuses), and the tests that become obsolete. State the false-failure surface of your proposal on the next pin advance (the next night appends again).

Q4. Is any part of your proposal a process-rule amendment or a contract change (rule 11: cold gate or Ed) rather than a test/code fix within lead authority? Name the boundary precisely.

Q5. The lead's own leaning is Q1 (b) + Q2 "acceptance cutoff" + fixture-stubbing the generator core test. Disagree wherever the evidence says so; the record shows the peer's design input wins often enough that not asking is the error.

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre review`; JSON header under 8000 bytes; every claim with file:line; commands you ran with their outcomes; recommendation first, alternatives with the reason each lost.
