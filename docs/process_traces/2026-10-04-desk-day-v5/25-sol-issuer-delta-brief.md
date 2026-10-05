# Delta check: issuer review F1/F2 fixes (PR #471, a1126009 → c783f0ee)

Worktree: /Users/edr/code/JouleWise-wt-dd5-isdelta, detached at c783f0ee. Diff to check: `git diff a1126009 c783f0ee`. Your previous review (FAIL, F1 and F2) is /Users/edr/night-archive/desk-day-v5/sol-isreview.md; its replay scripts are under /tmp/dd5-isreview/. Dispositions: F1 fixed by anchoring the supplied `harvest.json` and selection bytes to the records committed on main under `docs/process_traces/2026-10-03-design-block3/windows/<plan_id>/`, verifying the archive's own `SHA256SUMS` and `outputs`, and requiring the frozen plan to name the block-3 policy; coordinated multi-file forgery beyond that is outside the threat model (D-161). F2 fixed by deriving the selected rung's valid receipt members with the summarizer's own `_run_provenance` and accepting zero large members.

Executing: re-run your V4/V5/V6 counterexamples and the real dry issue (report exit code, pin sha256, `g2a_record_sha256` only; must be `c694c488…8222`); confirm the superseded `harvest-r1-recover.json` cannot count toward an end state; check the committed-record anchor reads git HEAD of the issuer's own repository and refuses cleanly when run outside a git checkout or when the record is absent; check nothing in the delta weakens a round-1/2 check. Run `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_issue_g2a_prefill_prompt_pin.py tests/test_summarize_g2a_prefill_probe.py tests/test_select_g2a_prefill_length.py tests/test_d117_contrast_v5_pack.py` (drop absent files).

Verdict line first: `DELTA: PASS` or `DELTA: FAIL`, then findings with severity and evidence.

WRITE_SCOPE: []
Scratch: /tmp/dd5-isdelta/ only. Never write under /Users/edr/night-archive, /Users/edr/night-g2a, /Users/edr/night-custody. Finish in this turn.
