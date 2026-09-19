SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/test_calibration_bracketing.py", "tests/test_campaign_generator_core.py", "tests/test_calibration_ledger.py", "tests/test_arm_readiness_evidence_packauth.py", "tests/test_d117_floor_qwen3_v5_generate.py"]

# Test repair — committed ledger head pin advanced 76 → 176; tests that assumed pin == acceptance cutoff (lead adjudication 07a)

Cwd is the linked worktree of branch `fix/2026-09-19-head-pin-test-drift` at main `2f79e633` (`git log -1`). Never touch `/Users/edr/code/JouleWise` (canonical root) or any other worktree; scratch under `/tmp` only; no `sudo`, no `powermetrics`, no capture. Interpreter: `/Users/edr/code/JouleWise/.venv/bin/python` (read-only use). Do not commit; the lead commits by pathspec. Do not end your turn before the report is complete.

## Read first (absolute paths; they live in another worktree, read them as files)

- `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/07a-adjudication-head-pin-drift.md` — the ruling you implement.
- `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/07-consult-head-pin-drift-astra.md` — Q3 file-by-file shape (your predecessor's design; its `/tmp/pinfix-focused-probe.py` and `/tmp/pinfix-design-probe.py` may still exist and may be reused).
- `/Users/edr/code/JouleWise-wt-mag-e82f29ac/docs/process_traces/2026-09-19-activation-d0b83820/07-opus-contract-refuter.md` — A1/A2 detail and the file:line evidence.

## Do, in this order

1. **`tests/test_calibration_bracketing.py` ~597–646** — rewrite `test_live_issued_anchor_authenticates_and_matches_committed_head_pin`: rename to state what it proves (ordering + schema only; digest-in-chain is loader-enforced, say so in a docstring); replace the `cutoff == pin` assertion with `cutoff["ledger_schema"] == pin["ledger_schema"]`, `cutoff["sequence"] <= pin["sequence"]`, `pin["head_digest"]` a 64-hex string, and digest equality ONLY when sequences are equal; move the fixed `76` / `08456d50…` expectations onto the r6 artifact's `ledger_cutoff`; keep every artifact byte-pin, identity, derivation and eligibility assertion.
2. **`tests/test_calibration_ledger.py`** — add non-genesis physical-chain regressions with temporary ledger/custody files and a temporary Git repository carrying committed pins (existing helpers ~169–217): (a) advanced pin — finalize baseline A, append/finalize B, commit B's pin, load with A as cutoff → authenticates; (b) wrong cutoff digest on the same ledger → `calibration_ledger_baseline_missing`; (c) **pin below cutoff** (baseline_sequence > pinned_sequence; the branch at `joulewise/calibration_ledger.py:~2630` that no test currently executes) → refuses, and ALSO a self-consistent shortened ledger + pin so the refusal cannot rely on physical-head mismatch alone; keep the existing rollback test (~563).
3. **`tests/test_campaign_generator_core.py` ~103** — inside `assert_generation_uses_shared_write_boundary`, supply the generation-time head-file input for ALPHA/BETA by intercepting ONLY `sha256_file(REPO_ROOT / LEDGER_HEAD_REL)` (delegate every other path to the real function) with fixed fixture bytes whose independently checked SHA-256 is the generators' pinned `6bbe2625…` (reconstruct those bytes from git history: `git log -p -- configs/calibration/calibration_ledger_head.json` at `a816036f`, verify the digest, and record where you got them); apply to normal and mutated source paths; leave GAMMA and the write-boundary observer unchanged. Add a comment naming lane GENERATOR-HEAD-FILE-BYTE-PIN-01 (the byte pin on an append-advancing file is registered for the cold gate; this fixture tests the generator as a function of its declared inputs and does not change production).
4. **`tests/test_arm_readiness_evidence_packauth.py` ~541–592** — before emitting the temporary successor, install and commit the generation-time head fixture ONLY inside the test's disposable clone; preserve the acceptance-file newline mutation; strengthen the refusal assertion to name the acceptance path so ledger drift cannot satisfy the negative oracle by accident.
5. **`tests/test_d117_floor_qwen3_v5_generate.py` ~592, ~774** — the subprocess path: give it a disposable repository containing the historical head-file bytes and run the generator there. If this is larger than a fixture, finish 1–4, and return NEEDS_RULING naming the size.

Do NOT: touch production code, any `configs/campaigns/*/generate_configs.py`, `configs/calibration/*`, the committed pin, frozen packs, or `scripts/`. Do NOT weaken any drift refusal, delete the drift loop, roll back the pin, or add sequence-only assertions labelled as "authentication".

## Bench acceptance (execute; paste tails)

- Each changed module run individually (`python -B -m unittest tests.<module> -v`), expect OK.
- Quick tier: `python3 scripts/quick_suite.py --tier quick --workers 4` — paste the summary; if a failure is unrelated to this lane, name it and its cause.
- Negative oracles executed: (i) temporarily set the fixture digest wrong in a `/tmp` copy → the generator-core test must FAIL with `pinned input drifted`; (ii) the anti-rollback regression fails if the `> pinned_sequence` refusal is commented out in a `/tmp` copy of `calibration_ledger.py` (mutation on a copy, never on the worktree file).
- `git status --short` and `git diff --stat`: only the five scoped files.

## Report

Final message in the `claude-codex-report/v1` envelope for `--genre implementation`; JSON header under 8000 bytes; every executed command with its outcome; findings with severity and counterfactual + call site; state the false-failure surface of the repaired tests on the NEXT pin advance (it must be none).
