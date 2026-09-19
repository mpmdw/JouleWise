# Evidence extraction — the accepted-clean idle reference for lane QUIET-PREDICATE-EVIDENCE-01

Read-only. Cwd is a detached worktree at `bookkeeping/2026-09-18-activation-d8ca3a36` (main `422cdebb`). The evidence bundles live OUTSIDE this worktree under the canonical root and are read-only for you: `/Users/edr/code/JouleWise/<source_directory>` for each of the 17 members listed in `configs/calibration/calibration_acceptance_d079_v2_n17_r6.json` (`derivation_corpus.members[].source_directory`, e.g. `/Users/edr/code/JouleWise/runs_window_a_20260722/instrument_validation/20260722T145535-e941c821/` with `events.jsonl`, `instrument_evidence.json`, `manifest.json`, `power_trace.csv`, `raw/`). Never write there, never run git there, never touch any other worktree. Do not write files; report only in the envelope (under 8000 bytes; put the table first).

## What to establish

The night gate's busy-core cutoff must sit above the clean-machine floor. The lane needs the accepted-clean captures' idle CPU power and residency as the reference. Answer, with file paths and the exact commands you ran:

1. What instrument produced `power_trace.csv` (the external meter or macOS `powermetrics`)? What columns, units and sample rate? Is any `powermetrics` output (CPU package power, per-cluster active residency, per-core residency) recorded anywhere in the bundle (`raw/`, `events.jsonl`, `instrument_evidence.json`)? If yes, name the file and the field names; if no, say so plainly.
2. How are the idle (settle/baseline) segments delimited in a bundle (which events in `events.jsonl` or which fields in `instrument_evidence.json` bound them)? Cite the code in `joulewise/` that writes them.
3. For each of the 17 members: the idle-segment mean power in the instrument's units, its duration, and the capture-segment mean power (the A/B floor contrast if it is directly readable), plus the `b_fiducial_s` value from the acceptance file. One table row per member. Use decimal arithmetic or state the precision.
4. Whether any bundle carries a CPU-load or process-census observation taken during the capture (the sampler did not exist then; anything comparable counts). If none, say so.
5. The epoch caveat: the bundles predate macOS 25G83 (the acceptance-epoch lane); state what in the bundle identifies the OS build and the machine, and whether the idle reference is transferable to today's build on its face.
6. Anything malformed, missing or surprising (e.g., members whose `manifest_sha256` does not match `shasum -a 256 manifest.json`; verify all 17 and report).
