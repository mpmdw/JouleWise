FINAL PASS: PASS

The four test modules pass (87 tests). Two limits on this review: I could not read the real w2 bundles (access to `~/night-archive` was denied), and an inline selector probe was also denied, so finding 2 rests on reading the code and the existing tests.

**1. Provenance binding: sound, no finding.**
- **Input bytes:** they are bound to the inventory and manifest hashes (`scripts/summarize_g2a_prefill_probe.py:498-502`, again at `:338`).
- **Expected run hash:** it is `_config_sha256(BenchmarkConfig.from_mapping(config))` (`:341`), the same serialization the bundle writer uses (`joulewise/bundle.py:950-954`, `joulewise/controller.py:3378-3388`). The CLI loads configs through the same `from_mapping` (`joulewise/cli.py:292`).
- **Observed side:** `config.json` must hash to the expected value (`:345-349`) and `metadata.config_sha256` must equal it (`:350`).
- **Different config passing:** a run passes only if its `config.json` is the normalized form of the pinned input, so I found no path for a different config. The `power_hz + 1` tests with rebound metadata refuse in the summarizer, harvest and issuer.
- **Fixtures:** they now use real `RunBundleWriter.create` bytes, not a re-implementation.

**2. MINOR — null `small_minimum_count` leaves the harvest unchanged but removes an accidental standalone refusal** (`scripts/summarize_g2a_prefill_probe.py:554-568`).
- **Harvest:** any rung with `small_members < 5` is a RECOVER cause (`scripts/harvest_g2a_window.py:235-236`), and the selector runs only when there are no causes (`:249-251`). `all_small_count_ge_5` stays false for an empty rung. So no refusal becomes a selection under §7, and nothing new is printed under §10.
- **Standalone:** the selector rejects an integer minimum on a zero-member rung (`scripts/select_g2a_prefill_length.py:79-81`). The old `0` therefore made it refuse as malformed; the new `null` lets another qualifying rung be selected.
- **Why only MINOR:** the same was already true for a rung with 1–4 members (`:70-78`). The issuer does not bind the harvest verdict (`scripts/issue_g2a_prefill_prompt_pin.py:163-192`), so "all four rungs evaluable" is enforced only at `harvest_g2a_window.py:235`.

**3. MAJOR, outside the diff — this fix probably yields RECOVER, not SELECT, on the w2 re-harvest.**
- **Evidence:** the chain runs the summarizer itself under `set -euo pipefail` (`scripts/gen_g2_phase_d.py:276-281`; runsheet block L575-587). RUN_STATE records w2's arm head as `1d6b5668`, which has the pre-fix summarizer.
- **Consequence:** if that in-chain step refused on the same byte mismatch, `chain.exited` is non-zero. The harvest then adds `chain_nonzero_or_missing_exit` (`harvest_g2a_window.py:237-239`) and the verdict is RECOVER, as §7 requires ("the chain exited 0").
- **Status:** this is the registration applied as written, not a defect in this commit, so it does not block the merge. But w2 was the one recovery window, so check `night/chain.exited` before re-harvesting.

**4. MINOR — the issuer now depends on the live runs root** (`scripts/issue_g2a_prefill_prompt_pin.py:391-400`).
- It reads `metadata.json` and `config.json` from `receipt["runs_root"]`, which is the source path the harvest passed (`summarize_g2a_prefill_probe.py:652`), not the archive copy.
- If that root is moved or offloaded before the desk day, the issuer refuses with `counts_receipt_run_provenance_mismatch`. This fails closed.

**5. NIT — only `SchemaError` is caught around `from_mapping`** (`scripts/summarize_g2a_prefill_probe.py:340-343`).
- Any other exception escapes as a traceback: the harvest maps it to REFUSED `archive_or_authentication_fault`, and the issuer crashes. Both fail closed.

**6. NIT — small redundancies.**
- The input hash is checked twice (`summarize_g2a_prefill_probe.py:501` and `:338`).
- The issuer recomputes `config_root` for every run inside the loop (`issue_g2a_prefill_prompt_pin.py:386`).
