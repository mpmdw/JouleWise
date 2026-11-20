# BYTES stage-1 attribution probe (RL-80), run by magistrate activation 00da75c9

Item 265's command, run on the MBP 2026-11-11 07:44 PST:

- probe: `53207bad3:scripts/bytes_stage1_attribution_probe.py`, copied to `$S1/attribution-probe.py`,
  sha256 `a0bc822e5051560d8fc1c97a5413c9a8face67bc2a89a3ee483cf0322eceb70e`
- `$W=/Users/edr/code/jw-wt/bytes-stage1` at `df4c73e55` (unchanged); `$S1=/Users/edr/night-archive/bytes-stage1-20261111`
- interpreter `/opt/homebrew/bin/python3.13 -I` (the one §3.8 used), `TMPDIR=/private/tmp/jwrl80-tmp`
- `--repo $W --run-root $S1/run --export $S1/export`; stderr captured apart: 0 bytes
- **rc=0**
- `probe.txt` = stdout verbatim (`cmp` against `$S1/attribution-probe.txt`), 666 lines,
  sha256 `6fb4c13044569d19afb698387ca4adb06b05ee37bff63b9d9a0c433af7f0f7e9`

Magistrate's typed-token check before committing (counts only): tags are #, Q, TOTAL, ABOVE, A, EXACT,
MULT, FLAG, FLAGQ, WITHHELD. Every decimal is either a MULT line's final non-negative multiple of a bar
(318 MULT lines, each with 4 fields) or part of the model name qwen3-1.7b (24 EXACT lines). There are
no exponents, no signed numbers, no units and no direction words.
