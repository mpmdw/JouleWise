# Implementation seat: the G2-a prompt-pin issuer accepts only harvest-bound block-3 records and reads the harvest archive

Repository worktree: /Users/edr/code/JouleWise-wt-dd5-issuer (branch feat/2026-10-04-g2a-issuer-harvest-bound, based on main 8fa002f7). Commit on this branch if your sandbox allows it; if git metadata is unwritable, leave the changes in the working tree and say so. Do not push.

## Why

`scripts/issue_g2a_prefill_prompt_pin.py` issues the `_v5` prefill prompt pin (`joulewise.prefill_prompt_pin.v2`) that `configs/campaigns/d117_contrast_v5/generate_configs.py` (`_load_prefill_prompt_pin`, ~693-900) consumes. Measurement block 3 (registration `configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md`, sha256 `84dd04268a2aed17118bd98b87c10ebe38e5f1bce2ea330a02048537b0342476`) is complete. Its seal record `docs/process_traces/2026-10-03-design-block3/52-seal-record.md`, section "Open obligations", binds this change (read it, and registration §§7-9). Today the issuer:

1. accepts any selection record that matches a summary under the selector rule; nothing ties it to a harvested block-3 window with verdict SELECT;
2. has no end-state path (registration §7: if the block stops in its END STATE, `_v5`'s prefill length is 4096 with no selection record);
3. reads the LIVE runs root: the counts receipt's `runs_root` (e.g. `/Users/edr/night-g2a/<plan_id>/runs`) and the inventory's `config_root` (`/Users/edr/night-g2a/<plan_id>/prefill-probe-configs`), not the immutable harvest archive (Fable finding 4 on PR #463).

## The harvest archive (real, read-only)

`/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2/`:
- `harvest.json` (schema `joulewise.harvest_g2a_window.v1`; keys `archive_root`, `plan_id`, `plan_sha256`, `verdict`, `cause_codes`, `capture_made`, `selection{path,sha256}`, `outputs{name: sha256}`, `chain_summary_copy`, `members`, `pin_advance`); written by `scripts/harvest_g2a_window.py` (read it: how it copies the live tree into `g2a-root/`, how it names files, how `selection` and `outputs` are computed);
- `derived/selection.json`, `derived/summary.json`, `derived/counts.json`, ...;
- `g2a-root/window-plan/` (`d166-prefill-resolvability-summary.json`, `d166-prefill-counts-receipt.json`, `g2a-input-inventory.json`, `prefill-prompt-ladder.json`, `calibration_plan.json`, ...), `g2a-root/runs/<run_id>/`, `g2a-root/prefill-probe-configs/<stage>/`;
- `night-custody/night_plan.json` (its sha256 is `harvest.json` `plan_sha256`).

The block-3 RECOVER record of the same window (first harvest, before the #467 fix) is `/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z/harvest.json`; the block-3 NULL window is `/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T0526Z/harvest.json`. Block-2 archives (`...-20261003T0820Z-r2`, `...-20261003T1748Z-r2`) are NOT block 3 and must be refused.

## What to build

A. **Harvest binding (seal obligation (a)).** Replace the free-standing `--selection-record/--summary/--prompt-ladder/--input-inventory/--counts-receipt` inputs with a `--harvest <path to harvest.json>` input (keep `--ruling-trace` and `--output`). The issuer:
   - loads `harvest.json` strictly (duplicate keys refused), requires its schema, `verdict == "SELECT"`, empty `cause_codes`, and that `archive_root` is the directory containing the given `harvest.json` (resolved);
   - proves the window belongs to block 3: find what in the archive binds the block (the inventory's `campaign_policy` naming `configs/campaign_policies/quiet_mac_p2_g2a_b3.json` with sha256 `04bdbec45cf3b609b33886c1487e9982f030564b3212e636f8cf4631b5d4edc7`, the plan, anything the harvest itself checks) and require it; also take `--registration <path>` and require its bytes to sha256 to the block-3 registration sha above (a module constant). Say in your report which archive bytes establish "block 3" and why a block-2 archive cannot pass;
   - requires `night-custody/night_plan.json` sha256 == `plan_sha256`;
   - reads the selection record from the archive (`selection.path`, which must lie inside the archive) and requires sha256(bytes) == `harvest.json` `selection.sha256` == `outputs["selection.json"]`;
   - reads summary, counts receipt, inventory and ladder from the archive's `g2a-root/window-plan/`, and requires the derived copies the harvest compared (`chain_summary_copy`) to be byte-equal where the harvest says `equal`;
   - keeps every existing check (`_selection_from_inputs` re-derivation with the selector, `_validate_ladder`, `_validate_receipt`, runtime tokenizer re-encode, ruling-trace paths, closed pin schema).

B. **Archive re-rooting (Fable 4).** Every path the receipt or inventory records under the live window root (`/Users/edr/night-g2a/<plan_id>/...`: `runs_root`, `config_root`, `prompt_ladder.path`, ...) is mapped to the archive's `g2a-root/...` by the SAME mapping the harvest uses when it copies (reuse its helper if one exists; do not invent a second mapping). A recorded path that is not under that live root refuses. The issuer never opens anything under `/Users/edr/night-g2a`. Add a test that fails if the live root is read (e.g. the live root absent in the fixture while the archive copy is present).

C. **End state (seal obligation (b)).** A second mode, `--end-state`, with `--registration` and one or two `--recover-harvest <harvest.json>` records. It accepts exactly: the registration sha above; each record a block-3 harvest (same block proof as A) with `verdict == "RECOVER"` and `capture_made == true`; and the registration §7 trigger satisfied mechanically by those records (read §7: either two such RECOVER windows, `b3w1` then `b3w2`, or the first one's `members` meeting the clock-anchor condition; implement exactly the text, citing the lines). It emits prefill length 4096, with no selection record and no "no rung qualifies" condition. Because the pin schema and `generate_configs.py` require a `selection_record` file whose sha256 is `g2a_record_sha256` (they check only bytes and hash), the end-state path writes a small closed-schema end-state record (registration sha256, each RECOVER `harvest.json` path and sha256, the trigger branch that fired) into the bundle in that slot. Do NOT change `generate_configs.py`. The end-state path must still read the ladder's 4096 rung from an archive and re-encode it with the runtime tokenizer. Tests: synthetic RECOVER records that do and do not satisfy §7 (one RECOVER without the clock condition must refuse).

D. **Refusals** are specific `PromptPinError` codes; tests cover each new code: a non-SELECT harvest, a selection record whose sha differs from `selection.sha256`, a block-2 archive, a registration with the wrong sha, a plan sha mismatch, a live-root path outside the mapping, a missing archive file.

E. **Real-archive dry issue (mandatory).** With the new code, issue a pin from the real archive above into `/tmp/dd5-issuer-dry/` (the only place you write outside the repository). Report ONLY: the exit code, the refusal code if any, the sha256 of the written pin, and the pin's `g2a_record_sha256` (it must equal `c694c4884ff7f31b677b5ade1ab9710a4797c4529eaad61fba85fea080a88222`). Do not print the prefill length, counts or summary contents. Also run the issuer against the block-3 RECOVER record in `--end-state` mode and report the refusal code (one RECOVER whose members are all `bounded` must refuse). Never write under `/Users/edr/night-archive`, `/Users/edr/night-g2a` or `/Users/edr/night-custody`.

## Tests to run
`python3 -m pytest -q tests/test_issue_g2a_prefill_prompt_pin.py` plus every test module that imports the issuer or reads `generate_configs._load_prefill_prompt_pin` (find them with grep). If you touch a file in `tests/fixtures/custody_read_replay_allowlist.json`'s domain, update it and run its consuming test.

## Write scope (exhaustive)
WRITE_SCOPE: ["scripts/issue_g2a_prefill_prompt_pin.py", "tests/test_issue_g2a_prefill_prompt_pin.py", "tests/fixtures/custody_read_replay_allowlist.json"]
Scratch outside the repository: `/tmp/dd5-issuer-dry/` only.
Do not edit `generate_configs.py`, `scripts/harvest_g2a_window.py`, the selector, the summarizer, `joulewise/`, configs, registrations or any of the four pinned estimator files (`joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`). If the right fix needs one, stop and say why.

## Report
The files changed; the commit sha (or "uncommitted"); test commands with pass counts; the block-3 proof and why block 2 fails; the dry-issue result (exit code, pin sha256, g2a_record_sha256 only); the end-state refusal code; any finding outside scope with file:line. Finish the whole task in this turn; do not end with a plan.
