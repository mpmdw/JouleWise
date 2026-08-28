# Venv relock — measurement checkout, 2026-08-27 (magistrate under custody)

Checkout: /Users/edr/JouleWise-measurement-20260813 at 3c96b18f.
Ruled method (D-155 operator fix) steps 1–3 executed verbatim: `mv .venv
.venv.pre-v4`; `python3.13 -m venv .venv`; `pip install -c
env/mac-measurement-lock.txt -e ".[mac]"`.

## Deviation, recorded not silent
After step 3 the gate diff had THREE lines — lock packages nothing requires
(charset-normalizer==3.4.8, requests==2.34.2, urllib3==2.7.0), exactly the
constraints-file property the runbook states. Step 3b:
`pip install -c env/mac-measurement-lock.txt charset-normalizer requests urllib3`
— every version still comes from the lock; nothing unpinned was installed.

## Gate
want.txt = 37 lines; have.txt = 37 lines; `diff want have` EMPTY (exit 0).
Version smoke: python 3.13.1, mlx 0.31.2, mlx_lm 0.31.3, transformers 5.12.1.

## Residue and its disposition
- `.venv.pre-v4/` preserved (rollback = one `mv`).
- `joulewise.egg-info/` written at the checkout root by the editable
  install (untracked). Both excluded locally via `.git/info/exclude` so the
  tree reads clean (W-5 clean-tree condition holds); neither is a repo change.
- A custody directory was mistakenly created inside the measurement checkout
  by the magistrate's shell cwd and removed immediately (recorded here so the
  measurement tree's history is complete).
Transcript: relock.log.

## 2026-08-28 addendum — calibration observation ledger provisioned (B10)
The Opus seat of the live-proof consult found that `runs/calibration_observation_ledger.jsonl`
is gitignored while its pin `configs/calibration/calibration_ledger_head.json`
(sequence 76, head `08456d50…`) is tracked; W-5's fast-forward therefore never
carried the ledger into the measurement checkout, and the shakedown's first
calibration bracket would have refused `calibration_ledger_missing`
(`calibration_ledger.py:2019-2048`). Cure under custody: the dev ledger
(76 entries, byte sha256 `aa806848…4e3f`) copied to
`/Users/edr/JouleWise-measurement-20260813/runs/`; byte-identical; the
measurement tree still reads clean (the path is ignored there too). The
runbook §1.1 / W-5 checklist gains "provision the ledger and verify its
head against the pin" (G2 runsheet + preflight, stream G1).
