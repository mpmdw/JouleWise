SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py", "configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py", "tests/test_campaign_generator_core.py", "tests/test_d117_floor_qwen3_v5_generate.py", "tests/test_generator_head_pin_relation.py"]

# GENERATOR-HEAD-FILE-BYTE-PIN-01 (kernel 244) — implement B1 exactly as cold gate packet 09 ruled (ruling 10 + Opus refuter 11 → adjudication 09a)

Cwd is the linked worktree of branch `fix/2026-09-19-generator-head-pin-semantic` at main `b3abce08` (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; scratch under `/tmp`; no `sudo`, no `powermetrics`. Interpreter `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use). Do not commit. Do not end your turn before the report is complete.

## Read first (in THIS tree, on main since PR #361)

`docs/process_traces/2026-09-19-activation-d0b83820/09a-adjudication-generator-head-file-byte-pin.md` (the ruling you implement), `09-coldgate-packet-generator-head-file-byte-pin/10-coldgate-fable-ruling.md` (exact code shape, nine regressions), `11-opus-contract-refuter.md` (key-set shape check; the fence that is lost and must be STATED in the code comment: fork/divergence detection is evaluation-owned), `07a-adjudication-head-pin-drift.md`.

## Do (both live floor v5 generators, identical edit; `d117_contrast_v5` and every frozen generator UNTOUCHED)

1. Delete the constant `LEDGER_HEAD_FILE_SHA256`. Keep `LEDGER_HEAD_REL` and `LEDGER_HEAD_SHA256`.
2. Drift tuple: remove the `(LEDGER_HEAD_REL, LEDGER_HEAD_FILE_SHA256)` row; the other rows and the message `pinned input drifted: {path}` stay verbatim.
3. Immediately AFTER the drift loop add and call `verify_ledger_head_pin()` per ruling 10's text, folding in refuter 11's key-set check: refuse `ledger head pin shape invalid` (key set ≠ {sequence, head_digest, ledger_schema}, or `sequence` a bool / not an int); `acceptance ledger cutoff drifted: <acceptance rel>` if `cutoff["head_digest"] != LEDGER_HEAD_SHA256`; `ledger head pin schema mismatch: <pin rel>`; `ledger head pin behind the acceptance cutoff: <pin rel>` (`sequence < cutoff.sequence`); `ledger head pin diverged from the acceptance cutoff: <pin rel>` (equal sequence, different digest). The returned pin is NEVER written into an emitted byte. Comment (one paragraph, plain words): the committed head pin advances after every measurement night by design (D-109 append protocol); this check binds the pack to its acceptance's cutoff and refuses rollback; detection of a forked pin at a higher sequence is evaluation-owned (`joulewise/calibration_ledger.py` run-time loader, reached through `--head-pin` at run time) and is NOT attempted here.
4. Emitted manifest: `issued_ledger_head = {"path": LEDGER_HEAD_REL.as_posix(), "head_sha256": LEDGER_HEAD_SHA256}` — drop `file_sha256`. Grep the repository for `issued_ledger_head` and `file_sha256` consumers outside `configs/` and `docs/` and paste the (expected empty) result.
5. Tests: (a) `tests/test_campaign_generator_core.py` — remove the ALPHA/BETA head fixture and its "fixture fired" assertion for the LIVE generators (verify first which labels map to which generators via `GENERATOR_CASES`; if a label maps to a frozen generator, keep its fixture and say so); keep `GENERATION_LEDGER_HEAD_BYTES`/`_SHA256` and the shared `generation_repository()` helper (the frozen-path modules import them). (b) `tests/test_d117_floor_qwen3_v5_generate.py::generation_repository` — keep the clone and the working-tree generator copy, DROP the head-bytes write, so the live generators run against the real committed pin. (c) New module `tests/test_generator_head_pin_relation.py` with ruling 10's nine regressions plus the shape refusal, executed against BOTH live generators in disposable clones with a rewritten pin file: advanced pin → generate succeeds, emitted tree byte-identical to a generate at the cutoff; rolled back → refuses with the exact message and writes nothing; schema altered → refuses; equal sequence + different digest → refuses; `sequence` as `true` / `"176"` → shape refusal; acceptance bytes mutated → still `pinned input drifted: <acceptance path>` raised BEFORE the head check; emitted `issued_ledger_head == {path, head_sha256}` exactly and `head_sha256 == cutoff.head_digest`; preserve/echo mode unchanged for every frozen generator (run the existing frozen-path tests); the `--check` subprocess path passes with the real committed pin and no fixture.

## Bench acceptance (execute; paste tails)

- New module + the two changed modules + `tests.test_d117_v3_family` + `tests.test_arm_readiness_evidence_packauth`: OK.
- Negative oracles on `/tmp` copies: comment out the `sequence < cutoff` refusal → the rollback regression FAILS; restore the drift row → the advanced-pin regression FAILS with `pinned input drifted`.
- `python3 scripts/quick_suite.py --tier quick --workers 4`: summary (a blocked `/bin/ps` in your sandbox is environmental — say so).
- `git diff --stat`: only the five scoped paths; the frozen generators and their `plan_tree.json` files byte-identical (`git status` shows nothing else).

## Report

`claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes; commands with outcomes; NEEDS_RULING if any ruled shape cannot be implemented as written.
