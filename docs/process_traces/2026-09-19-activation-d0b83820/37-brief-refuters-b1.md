SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: []

# Refuter (read-only, LENS: __LENS__) — GENERATOR-HEAD-FILE-BYTE-PIN-01 implementation, branch `fix/2026-09-19-generator-head-pin-semantic` at `842e5b39997f53ac8fcec96ec6fe2add6d9df496` (base main `b3abce08`)

Cwd is a detached read-only worktree at `842e5b39997f53ac8fcec96ec6fe2add6d9df496` (`git log -1`). Never touch /Users/edr/code/JouleWise (canonical root) or any other worktree; write nothing but /tmp scratch; no sudo, no powermetrics. Interpreter /Users/edr/code/JouleWise/.venv/bin/python (read-only use). Do not end your turn before every item has an answer.

What you refute: `git diff b3abce08 HEAD` — two live floor v5 generators (`configs/campaigns/d117_floor_qwen3-{1p7b,8b}_v5/generate_configs.py`), two test modules changed, one new (`tests/test_generator_head_pin_relation.py`). The ruling it implements is in THIS tree: `docs/process_traces/2026-09-19-activation-d0b83820/09a-adjudication-generator-head-file-byte-pin.md` with `09-coldgate-packet-generator-head-file-byte-pin/{10-coldgate-fable-ruling.md,11-opus-contract-refuter.md}`. The seat's report: `/tmp/magistrate-d0b83820/35-b1-generator-head-pin-astra.md` (read as a file).

## CONTRACT lens (answer if your LENS is contract)
C1. Is `verify_ledger_head_pin()` exactly ruling 10's shape with refuter 11's key-set check folded in — five distinct refusals with the ruled messages, called AFTER the drift loop (so acceptance bytes are verified first), returned pin never written into an emitted byte? Diff both generators against each other: identical edit?
C2. Does the comment state, in plain words, that fork/divergence detection at a higher sequence is evaluation-owned (run-time loader through `--head-pin`) and not attempted here? Is that statement TRUE (cite `joulewise/calibration_ledger.py` lines and the generator's `--head-pin` argv line)?
C3. `issued_ledger_head` shrinks to `{path, head_sha256}`: grep every consumer of `issued_ledger_head` / `file_sha256` outside `configs/` and `docs/`; are the committed historical `plan_tree.json` files untouched? Does any frozen generator or `d117_contrast_v5` change? (Must be byte-identical.)
C4. Fences: D-109 anti-rollback at generation time (pin below cutoff refuses); the other pinned inputs still drift-refuse BEFORE the head check; preserve/echo mode unchanged; frozen-path test fixtures retained; the live-generator fixture removed from `tests/test_campaign_generator_core.py` (verify the label → generator mapping the seat relied on).
C5. Anything in the new regression module that asserts LESS than ruling 10's nine items + the shape refusal? Any assertion that would pass if the head check were deleted entirely (vacuous)?

## EXECUTION lens (answer if your LENS is execution)
X1. Run `tests.test_generator_head_pin_relation`, `tests.test_campaign_generator_core`, `tests.test_d117_floor_qwen3_v5_generate`, `tests.test_d117_v3_family`, `tests.test_arm_readiness_evidence_packauth`; paste tails. Quick tier: `python3 scripts/quick_suite.py --tier quick --workers 4` (a blocked /bin/ps in your sandbox is environmental — say so).
X2. Negative oracles on /tmp copies of the tree: (i) delete the `sequence < cutoff` refusal → the rollback regression FAILS; (ii) restore the byte-pin row in the drift tuple → the advanced-pin regression FAILS with `pinned input drifted`; (iii) emit `file_sha256` again → the manifest regression FAILS; (iv) delete the whole `verify_ledger_head_pin()` call → name every regression that fails (must be ≥ 5).
X3. Real generation: in a disposable clone, run each live generator's real CLI regenerate against the REAL committed pin (176) — succeeds? — and against a pin rewritten to sequence 75 — refuses with the exact message and writes NOTHING under the output root (list it).
X4. Byte identity: emitted pack tree at pin 176 vs at pin 76/cutoff digest → identical? (paste the two tree digests). Custody: every frozen generator, `d117_contrast_v5`, and every committed `plan_tree.json` byte-identical to `b3abce08`.
X5. Same-signature: "pack bytes depend on the advancing pin" and "a regenerate-mode test still runs a live generator against fixture head bytes" — none found, or the surviving site.

Report: claude-codex-report/v1 envelope for --genre review; verdict = {counts, findings}; JSON header under 8000 bytes; counterfactual + call site per finding.
