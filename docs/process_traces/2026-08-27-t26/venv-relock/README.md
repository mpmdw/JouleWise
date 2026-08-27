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
