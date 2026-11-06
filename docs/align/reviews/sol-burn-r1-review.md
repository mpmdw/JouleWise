# Adversarial review — ALIGN v4 R1 High Power rehearsal

Date: 2026-11-06. Reviewed head: `a2193446`. Scope: synthetic/code review
only; no hardware was run and no external experiment/custody paths were read.

## Verdict

**ADMIT WITH THE FIXES IN THIS CHANGE.** Four executable defects were found.
The signal-burst repair already on the branch is sound: the first signal
installs `SIG_IGN` for all three handled signals before raising, so later
signals cannot interrupt the restoring child (`scripts/align_r1_rehearsal.py:592-601`).
The desk thermal exclusion is also internally consistent: X1–X4 are removed
from value checks, collector loss is X4, and U1 still counts the removed member
(`joulewise/align/apple/thermal_desk.py:541-565,568-605`).

## Findings and fixes

### F1 — BLOCKER: a zero exit falsely discharged crash restoration

`PowerModeGuard.restore` formerly cleared the persistent marker whenever the
`pmset` command returned zero. A command can return zero without the queried AC
profile becoming Automatic; the next rehearsal would then have no durable
restoration obligation. The fix reads `pmset -g custom`, requires the AC
`powermode` key to equal 0, and only then clears the marker
(`scripts/align_r1_rehearsal.py:112-128`). The regression simulates a
successful no-op command and proves that entry refuses while the marker and
High Power state remain (`tests/align/test_r1_rehearsal.py:178-188`).

### F2 — HIGH: sudo admission was a substring test

The old check accepted `/usr/bin/pmset -c powermode 20` as evidence for the
required mode-2 command. That could admit hours of pre-A-B-A work before the
first High Power command was denied. Admission now recognizes complete
newline/comma-delimited `sudo -l` commands (`scripts/align_r1_rehearsal.py:130-143`).
The adversarial `powermode 20` listing is refused by the regression
(`tests/align/test_r1_rehearsal.py:211-216`).

### F3 — HIGH: deadman accounting admitted negative durations

The seam required finite phase durations but did not require non-negative
ones. A negative G0/G1/H value shrank the reported hold fraction and could
falsely pass the duty bar; negative tail also inflated predicted turns. Every
phase is now required to be non-negative before either calculation
(`scripts/align_r1_rehearsal.py:369-390`). The failing synthetic H=-1 case is
pinned at `tests/align/test_r1_rehearsal.py:276-282`.

### F4 — HIGH: the sole measurement record was crash-truncatable and collidable

`r1_result.json` and registration were written directly. Process or host death
during `write_text` could leave malformed bytes; SIGKILL before the finalizer
left no top-level status record. Worse, `--registration <output>/r1_result.json`
allowed the registration and measurement record to overwrite one another.
The driver now writes canonical bytes to a same-directory exclusive temporary,
fsyncs, atomically replaces, and fsyncs the directory
(`scripts/align_r1_rehearsal.py:347-366`). It creates a durable `running`
checkpoint before sudo/model work and advances it after accepted phases
(`scripts/align_r1_rehearsal.py:573-590,608-651`). Registration collision is
an admission refusal before runtime work (`scripts/align_r1_rehearsal.py:573-606`).
Tests prove byte identity with the former successful serialization, retention
of the prior record when replacement fails, and collision refusal
(`tests/align/test_r1_rehearsal.py:284-305`).

## Thermal exclusion and custody conclusions

- Thermal exclusions were not broadened. The existing desk separates
  `observed` from `included`, excludes X1–X4 from value calculations, and
  computes coverage on observable members (`joulewise/align/apple/thermal_desk.py:568-605`).
- Successful final JSON bytes remain identical: the atomic writer uses exactly
  `json.dumps(..., indent=2, sort_keys=True) + "\\n"`; the equivalence test
  compares bytes (`scripts/align_r1_rehearsal.py:347-350` and
  `tests/align/test_r1_rehearsal.py:284-290`). Intermediate checkpoints are
  operational custody only and do not alter the final analysis object.
- The harvest remains a runtime seam and is recorded verbatim. This review did
  not invent a second authentication policy; WP15/runtime must continue to own
  that authenticated harvest as documented (`scripts/align_r1_rehearsal.py:647-651`).

## Verification

- `python3 -m unittest tests.align.test_r1_rehearsal`: 36 tests pass; the one
  shell integration test cannot start because this Linux container has no
  `/bin/zsh`.
- `python3 -m unittest` with that environment-only test omitted: 36/36 pass.
- `python3 -m unittest discover -s tests`: required whole-suite result recorded
  in the accompanying run report.
