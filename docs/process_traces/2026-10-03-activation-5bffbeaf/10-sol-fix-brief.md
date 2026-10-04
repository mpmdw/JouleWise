# R3 fix seat: G2-a summary run-config provenance (w2 harvest REFUSED)

Repository worktree: /Users/edr/code/JouleWise-wt-5bffbeaf-fix (branch fix/2026-10-03-g2a-w2-summary-config-provenance, based on main e256ac28). Commit your work on this branch (do not push; the lead pushes).

## The fault
The block-2 recovery window w2 (plan d117-g2a-prefill-probe-20261003T1748Z) produced 12 completed member runs. Its harvest (`scripts/harvest_g2a_window.py`) REFUSED with `summary_regeneration_failed`. The underlying error is `run_provenance_mismatch: g2a-small-p0512-r01: config_sha256` from `scripts/summarize_g2a_prefill_probe.py::_run_provenance`.

That function requires `runs/<run_id>/config.json` to be byte-identical (sha256) to the input config in `prefill-probe-configs/<stage>/<run_id>.json` (the inventory's `config_sha256`). The runner, however, writes `runs/<id>/config.json` as its own re-serialization of the parsed config, with schema defaults filled in. Here are the real differences, from a sorted-key diff:
- `host: null` was added;
- `link_speed_mbps: null` and `notes: null` were added in the network block;
- `ambient_temp_c: null` and `notes: null` were added;
- `dataset_ref: null` and `prompt_tokens: null` were added.

So the input file has sha `e99d78a4…f8` and the run copy has `3ed56079…49`, and `metadata.json` `.config_sha256` also records the run copy's sha. Window w1 produced no runs, so this path never met real data before.

## What to do
1. Find the code that writes `runs/<id>/config.json` and computes `metadata.config_sha256` (the runner and config model under `joulewise/`).
2. Fix the summarizer's provenance binding so that it stays at least as strong as intended. It must prove that the run executed exactly the inventory's input config. Do this by deriving the run-config bytes the runner WOULD write from the input config, using the runner's OWN parse and serialize code path (import it; do not re-implement it).
   Then require all three of the following:
   - the derived bytes' sha equals the observed `runs/<id>/config.json` sha;
   - the input file's sha still equals the inventory's `config_sha256`;
   - `metadata.json` `config_sha256` equals the observed run-config sha.

   Do NOT weaken the check to "ignore null fields" or to a loose semantic compare. If the runner's serialization cannot be called deterministically, stop and report that instead of improvising.
3. Audit EVERY other consumer that compares a run directory's config to the inventory or input config, and give each the same treatment where it has the same defect. At least check `scripts/issue_g2a_prefill_prompt_pin.py` (`counts_receipt_run_provenance_mismatch`), `scripts/harvest_g2a_window.py`, and `scripts/select_g2a_prefill_length.py`.
4. Tests: add regression tests in which the fixture's run `config.json` is the runner's real normalized serialization, not a byte copy of the input. The existing fixtures evidently copy bytes, which is why CI never caught this. Also add a negative test: a run config whose content differs from the input in a non-default field must still refuse.
   Run the touched test files plus `tests/test_harvest_g2a_window.py` and `tests/test_summarize_g2a_prefill_probe.py`. If you add or change any file read by the custody replay, update `tests/fixtures/custody_read_replay_allowlist.json` the same way commit 9e2b1004 did, and run the test that consumes it.
5. **Real-data replay (mandatory; this is how we avoid a third serial REFUSED).**
   - Copy, read-only from the sources, the real w2 tree `/Users/edr/night-g2a/d117-g2a-prefill-probe-20261003T1748Z/` and whatever else the harvester's summary and selection steps read, into a scratch dir under `/tmp/g2a-w2-replay-5bffbeaf/`.
   - Run the summarizer, and the downstream selection step if the summary succeeds, on that copy with this branch's code, using the same arguments `harvest_g2a_window.py` passes (see its lines ~190-255).
   - Report the outcome verbatim: success, or the NEXT refusal reason. If a next refusal is another tooling defect of the same kind, fix it too, within scope. If it is a measurement outcome (for example members failed or missing, so the verdict is RECOVER or NULL), that is correct behaviour; report it and do not change it.
   - NEVER write under `/Users/edr/night-g2a`, `/Users/edr/night-custody`, or `/Users/edr/night-archive`.

## Write scope (exhaustive)
WRITE_SCOPE: ["scripts/summarize_g2a_prefill_probe.py", "scripts/issue_g2a_prefill_prompt_pin.py", "scripts/harvest_g2a_window.py", "scripts/select_g2a_prefill_length.py", "tests/test_summarize_g2a_prefill_probe.py", "tests/test_issue_g2a_prefill_prompt_pin.py", "tests/test_harvest_g2a_window.py", "tests/test_select_g2a_prefill_length.py", "tests/fixtures/custody_read_replay_allowlist.json"]
Scratch outside the repository: the lead authorizes writes under /tmp/g2a-w2-replay-5bffbeaf/ for the real-data replay copy only (not a repository write).
Do not touch the runner, `joulewise/` package code, configs, registrations, or the calibration ledger. If the right fix needs one of those, stop and report why.

## Report
End with: the files changed; the commit sha; test commands with pass counts; the real-data replay command and its verbatim result; and any finding outside scope.
