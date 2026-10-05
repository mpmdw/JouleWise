# Executing review (Sol 6.1 high, non-author): PR #480, detokenizer outside the prefill window (head 33b68dfd)

Worktree: /Users/edr/code/JouleWise-wt-dd5-dtrev, detached at 33b68dfd (parent main b2ff2f36). Diff: `git diff b2ff2f36 33b68dfd`. Finding it fixes: `/Users/edr/night-archive/ia-0a40/MEMO.md` §3.1 (repros under `/Users/edr/night-archive/ia-0a40/premortem/scratch-*/`). Seat report: `/Users/edr/night-archive/desk-day-v5/sol-detok.md`.

Check by running code: (1) with the installed mlx-lm (in /Users/edr/code/JouleWise/.venv), no detokenizer construction happens between the adapter's `phase_start prefill` stamp and the first token (instrument the real class's constructor, not a stub of the adapter); (2) the shared vocabulary map is never mutated by a copy, and per-run state (offsets, unflushed bytes, tokens) is reset, so two consecutive generations and an interrupted generation produce the same text as fresh detokenizers; (3) the fallback path for another class is recorded in provenance and behaves like the old code; (4) nothing else in the measured window moved (diff the stamp order). Run `tests/test_mlx_runtime*.py tests/test_adapter*.py`. You have no Metal: use the real tokenizer wrapper with a local tokenizer where possible and say what you stubbed.

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity and evidence.

WRITE_SCOPE: []
Scratch: /tmp/dd5-dtrev/ only. No background processes. Finish in this turn.
