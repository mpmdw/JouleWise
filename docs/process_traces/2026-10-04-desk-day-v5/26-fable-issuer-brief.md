You are giving a cold final pass on one change before merge. You have no prior context. Your working directory is a detached checkout of `c783f0ee` (branch feat/2026-10-04-g2a-issuer-harvest-bound, PR #471); its parent on main is `8fa002f7`. Read `git diff 8fa002f7..c783f0ee` and the surrounding code. You may run read-only commands and unit tests with `/Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider <files>` from this directory (e.g. `tests/test_issue_g2a_prefill_prompt_pin.py tests/test_summarize_g2a_prefill_probe.py`).

Rules:
- Scratch: /tmp/dd5-fable-is/ only. Do not edit files in the checkout, and do not run git commands that write.
- Never run powermetrics, sudo, launchctl or a model. Never write under /Users/edr/night-archive, /Users/edr/night-g2a or /Users/edr/night-custody (reading the archive below is allowed).
- Do not read RUN_STATE.md, CLAUDE*.md, memory or skill files, and do not read GitHub pull-request bodies.
- One non-interactive session, every command in the foreground, no background task or subagent. Budget 50 minutes. Ending before your ruling file exists is a protocol failure.
- Write your ruling to /Users/edr/night-archive/desk-day-v5/fable-issuer.md; its first line is `FINAL PASS: PASS` or `FINAL PASS: FAIL`, then findings with severity (BLOCKER/MAJOR/MINOR/NIT), file:line and evidence. Do not print the issued pin's prefill length or any count.

What the change is for:
- JouleWise measures LLM inference energy. Decision D-166 fixes the `_v5` campaign's prefill prompt length from a pre-registered diagnostic probe (G2-a): the shortest of 512/1024/2048/4096 tokens at which every small-model member's prefill shows at least 5 overlapping power records. Measurement block 3 (registration `configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md`, sealed by `docs/process_traces/2026-10-03-design-block3/52-seal-record.md`) ran and its harvest (`scripts/harvest_g2a_window.py`) returned SELECT. Archive: `/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/`; its records are committed under `docs/process_traces/2026-10-03-design-block3/windows/`.
- `scripts/issue_g2a_prefill_prompt_pin.py` turns that record into the prompt pin every `_v5` pack generator consumes (`configs/campaigns/d117_contrast_v5/generate_configs.py::_load_prefill_prompt_pin`). The seal record's open obligation: (a) accept a selection record only when its sha256 equals `selection.sha256` in a block-3 `harvest.json` with verdict SELECT; (b) under the registration §7 end state, accept exactly the registration sha256 and the block's RECOVER `harvest.json` records and emit 4096, with no selection record and no "no rung qualifies" condition. Also: read the harvest archive, never the live runs root.
- Orchestrator rulings applied: the end-state pin keeps D-166's static `exhausted_ladder_branch` declaration (a constant in every pin), with a closed end-state record as authority; provenance is anchored to records committed on main plus the archive's SHA256SUMS, since the threat model is mistakes and stale or hallucinated paths, not a multi-file forger.

Judge as the last reviewer before merge on code that decides which measured record fixes a protocol parameter:
1. Can any record other than the block-3 SELECT harvest's own selection produce a pin? Can a superseded or non-block-3 record count toward the end state?
2. Does the issuer read only the archive and committed records (never `/Users/edr/night-g2a`)?
3. Does the re-derivation (summary → selector rule → selection) still bind, including with invalid members excluded as registration §8 requires?
4. Is the §7 end-state trigger implemented exactly as the registration text says?
5. Do the tests kill the regressions they claim?
