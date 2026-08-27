# Blind Fable seat — pipeline smoke design (Fable 5, read-only). Verbatim.

**PIPELINE SMOKE — design (T26 seat, read-only)**

**1. STAGE MAP** (entry → validates → does NOT validate)

| # | Stage | Entry | Validates | Hole |
|---|---|---|---|---|
| S1 | Generate | `configs/campaigns/…_v3/generate_configs.py` (~:948-986, :1521-1554) | plan-tree digests, cadence, prompt hashes | Emits the analysis manifest **unvalidated** (m=1, EMPTY prefill, no `families`) — D-157 root |
| S2 | Mint/freeze | `generate_arm_readiness.py freeze` → `arm_readiness.generate_freeze_receipt` `:6749`; U11 `_identity_projection_pseudo_receipt` `:5101` | plan-tree SHA, predecessor chain, pinset R1, histsem | `arm_readiness.py` has **zero** occurrences of `analysis_manifest`; `validate_prospective_analysis_manifest_v3` (`analysis_manifest_v3.py:2777`) has no caller outside its module + tests. The manifest SHA is pinned by bytes it never reads |
| S3 | Arm | `generate_arm_receipt` `:7525`, `validate_arm_context` `:7548`, T-0 recipe binding `:8401-8603` | receipt custody, horizons, GO/NO_GO, launch-input digests | Same manifest blindness; `window_kind ∈ {ALPHA,BETA,GAMMA}` only (`:245`) — no non-claim kind exists |
| S4 | T-0 launch | `scripts/launch_window.py:294` → `capture_t0_step.py::_parse_window_environment` | arm receipt, manifest canonical form, FD-198 handoff, env keys | 25-key exact allowlist refuses `ARM_RECEIPT`/`LAUNCH_MANIFEST` the runbook tells Ed to bind (PR #205 defect) — chain cannot run as documented |
| S5 | Collect | `run_campaign.run_campaign` `:7457-7481`, per-run `finalize_dispatch_receipt` `:6818`, `validate_bundle(strict)` `:6832` | bundles, idle admission, whole-window verdict (`:5505`) | `load_analysis_manifest` `:1201` routes **v1/v2 only** — the collector never opens the v3 manifest it is collecting for |
| S6 | Finalize | `scripts/finalize_analysis_manifest.py` → `finalize_prospective_analysis_manifest_v3` `:3722` (re-validates prospective `:3760`, semantic-hash equality `:3671`) | first place the prospective manifest is validated | Script is referenced by **no runbook phase, no script, no config** — orphan; S-0 stopped at S2 |
| S7 | Claim edge | `joulewise analyze-claims` (`cli.py:2284`) → `analysis_engine.analyze_claims` `:1625` → `load_analysis_inputs` (`inputs.py:3001`), `_validated_family` (`multiplicity.py:29`: `len(p_values)==m`) | everything; refuses prospective (`inputs.py:604`) | Only reachable after S6 — 168 h late |
| S8 | Verdict | `evaluate_claim` (`claims.py:257`) → `finalize_claim_verdicts` (`artifact.py:3491`) | outcome precedence | — |

**2. DESK REPLAY VARIANT** (no hardware, CI, ~3–5 min)

- **Smoke generation:** call the *production* generator with `--family smoke` producing pack id `d117_smoke_<sha8>_v0`, `window_kind: GAMMA` profile but `pack_root` under `tmp`. Everything downstream is real code on throwaway bytes.
- **Unarmable by construction (three independent locks, any one suffices):** (i) S2/S3 run through `generate_dry_run_receipt` `:7204` (`mode: synthetic_dry_run`), and `readiness_dry_run_used_as_arm_record` (`:165`) already refuses such a receipt as an arm; (ii) the telemetry backend is the fixture process, so `mock_telemetry_claim_ineligible` is minted in every reduction — but see predicate below; (iii) the smoke pack id is absent from `d117_row_registry_v2.json` and from any family marker, so marker verify refuses it at `arm/freeze/verification/marker-replay` (`R1_DIGEST_CONDITIONAL_ENTRY_POINTS` `:2873`). Receipts stay honest because nothing is forged — dry-run receipts are the receipts.
- **Run for real:** S1, S2-as-dry-run, S3-as-dry-run + `_parse_window_environment` over the generated `window.env`, S5 via `run_benchmark(...)` with `RateFitFixtureClock` and `reducer=reduce_bundle` exactly as `tests/test_p2038_production_path.py:401-445` does (existing seam: `P2038_FAKE_POWERMETRICS_MODE/STATE`, `tests/fixtures/fake_powermetrics_process.py` replays `powermetrics_sample.plist` through the real parser, NUL framing, D-078 causal constraint), S6 real, S7 real.
- **Stub:** the MLX model call (canned token/event stream — the `RateFitFixtureClock` profile is the existing MLX-events surrogate), `collect_environment_guard_observation` (patched dict, as `:437`), calibration via `install_complete_calibration`.
- **Feeding the collector:** three-window shape, 2 blocks/condition (minimum for `paired_block_incomplete` not to fire), pulses from `calibration_live_three_window` fixture.
- **Pass predicate at S7:** `analyze_claims` returns an artifact (no `AnalysisInputError`) AND `ordered_reason_codes` ∩ CONTRACT = ∅, where CONTRACT = `{analysis_manifest_*, *_hash_mismatch, bundle_missing, bundle_strict_invalid, floor_row_*, floor_artifact_invalid, multiplicity_family_incomplete, fixed_n_plan_incomplete, paired_block_incomplete, *_missing, *_required, calibration_ledger_*, capture_pipeline_*}` ∪ `registry.py:59-66`. DATA codes (`effect_not_above_floor`, `multiplicity_not_rejected`, `insufficient_complete_blocks`, sensitivity set) are PASS. `mock_telemetry_claim_ineligible` is the one deliberate exception: expected exactly once, asserted present (it is the lock), excluded from the predicate. Also assert `_validated_family` was reached with m == number of contrasts.

**3. LIVE ~20-MINUTE VARIANT**

Real generator, real freeze (Ed's D-150(1) prompts — three MLX U11 freezes ≈10 min, as estate-11 already needs), real arm, real `launch_window.py` execve, real powermetrics under `sudo -n` (already granted per runbook §5:399; network-time toggle needs the sudoers rule §5A — **skip** the toggle: drift screen is not what this proves). Window: 1 pre-pulse + 1 post-pulse bracket, 1 block/condition (2 runs × 2 conditions ≈ 6 min with 1.5B/7B), then S6+S7 at the desk. Proves the hardware seam the replay cannot: powermetrics binary sha binding (`powermetrics_fiducial.py:1501`), boot-session/clock at T-0, FD-198 handoff across a real execve, `window.env` allowlist against the real chain. Quarantine: pack id `d117_smoke_live_*`, `quarantine_root` set (`arm_readiness.py:346`), never enters `d117_row_registry_v2`, never marker-signed, bundles written under `/Users/edr/JouleWise-smoke/` outside any measurement checkout — D-139's diagnostic/nonclaim license (D-142 reading) covers it, as the 08-18 shakedown was.

**4. WHAT IT WOULD HAVE CAUGHT**

- **D-157:** S6 refuses `analysis_finalization_prospective_invalid` (families missing/m≠2) before any window; in the replay this is minute 2.
- **S0-O2** (marker C→S with no supply): S3 marker verify at the replay's `verification` entry point — the deferral disclosure assertion fails loudly.
- **3e/3f** (hC consume-side supply line): S4 — `launch_window.py` leg-F refusal (`test_launch_window.py:1166`) fires in the replay because no confirmation pair is produced by S2/S3.
- **Launcher-argument gap:** S4 — `_parse_window_environment` refuses `evidence_author_t0_capture_environment_invalid` on the generated `window.env`.
- Also new: `run_campaign` never reading the v3 manifest (S5 hole) surfaces the moment the smoke asserts the collector saw the pinned manifest SHA.

**5. COST & RISK**

Desk replay: ~1.5 Sol days (generator `--family smoke` flag 0.5, driver script + predicate 0.5, CI wiring/regressions 0.5). Live variant: 0.5 Sol day + 20 min Ed. Must NOT touch: the `_v3` frozen pack bytes, `plan_tree.sha256`, the `_v4` 112-entry changed set, any file in the D-151 conditions, `d117_row_registry_v2.json`, marker code. Strongest counter: "the 08-18 shakedown already does this" — **it does not**: its scout (`01-protocol-scout.md`) scoped calibration bundles + a 600 s idle baseline; it never generated, froze, finalized, or consumed. S-0 goes further but stops at S2 by design. Real risk: the smoke's `--family smoke` branch touching the generator is itself a generator change pre-`_v4` — keep it a separate module that imports the generator's functions rather than editing the file the W-10 resolver is editing.

**6. RECOMMENDED CUT (48 h)**

Build only the desk replay's **S6+S7 tail** as a CI test: generate (post-W-10 generator) → `finalize_analysis_manifest.py` on a canned collection (fixtures `d117_postcollection_trust`, `p2038_v3_production`) → `analyze-claims` → contract-code-free predicate. That is the D-157 shape in ~0.5 Sol day, runs in estate 11, and is the artifact R-2 lacks. Add the `window.env` allowlist assertion (10 lines). Defer: full replay of S3–S5 through the fixture powermetrics process, and the live 20-minute variant, to after the `_v4` night — the live variant's hardware seam is already exercised by estate 11's real freezes plus the first `_v4` window's own T-0.
