# 05 — Production v5 clone cut at main `078a13a4` (CLONE-READINESS-01 steps 1–2), 2026-09-10 04:34–04:37 PDT

Executed at the bench by headless activation `96bfeca7` (script `05-clone-cut.zsh`, transcript `05-clone-cut.log`).
The canonical checkout is fenced (armed plan rehearsal-20260911), so the clone was taken from the GitHub remote,
not from `/Users/edr/code/JouleWise`; the only canonical read was a byte copy of the ignored ledger file.

| Fact | Observed |
|---|---|
| Root | `/Users/edr/JouleWise-measurement-v5-20260910-078a13a` (fresh; did not exist before 04:34:39) |
| HEAD | `078a13a461abd124c29796798da5107fe00190a6` = origin/main at cut time (detached) |
| venv | `/opt/homebrew/bin/python3.13` → Python 3.13.1; `pip install -c env/mac-measurement-lock.txt -e ".[mac]"` + `charset-normalizer requests urllib3` per runsheet L1517–1519 |
| Lock gate | `LOCK_DIFF_EMPTY` (normalized `env/mac-measurement-lock.txt` vs `pip freeze --exclude-editable`, the preflight's own comparison) |
| Runtime | mlx 0.31.2, mlx_lm 0.31.3, transformers 5.12.1 (import probe in the venv) |
| Tree | `git status --porcelain=v1` → 0 lines before and after the ledger copy (`*.egg-info/` and `runs/` are ignored at this head) |
| Ledger | `runs/calibration_observation_ledger.jsonl` sha256 `aa806848…694e3f`, identical to the canonical file (76 records) |
| Authentication | `load_calibration_ledger_snapshot(..., repo_root=<clone>, verify_custody=False)` → no refusal; `verify_custody=True` (custody artifacts re-hashed at their absolute iCloud locators, 1.7 s) → no refusal; head_sequence 76, head_digest `08456d50…094d7` = committed pin |
| pip note | `charset-normalizer` 3.4.8 is a yanked release on PyPI ("no reason given"); the lock pins it and the lock-what-IS rule (env/README.md) keeps it. Recorded, not acted on. |

Not done here (owners unchanged): model-byte authentication against `configs/model_panels/qwen3_4bit.json`; the full
preflight (`docs/process_traces/2026-08-28-live-smoke/preflight.sh`), which imports MLX and runs an agent census that
refuses a live magistrate; any plan authoring. The head is provisional: if GATE-SENSIBILITY-SWEEP-01 changes capture-side
code before the first G2-a window, the clone is re-cut at the successor head by the same script (change `HEAD`/`ROOT`).
The older clone `/Users/edr/JouleWise-measurement-v5-20260910-1c83f2a` (1c83f2af, 199 commits behind, no `runs/`) was
left in place; it is not referenced by any plan.
