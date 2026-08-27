# Opus seat — pipeline smoke design (Opus 5, read-only, blind). Verbatim.

Design returned below.

---

# PIPELINE SMOKE — design

## 1. STAGE MAP

| # | Stage | Entry point | Validates | Blind to |
|---|---|---|---|---|
| S1 | Generate | `configs/campaigns/d117_.../generate_configs.py:2278-2295` (`--pack-id/--family-suffix/--no-preserve-current-frozen-bytes`) | family-ordinal downgrade guard, preserve/successor coherence (`GenerationIdentity.__init__:161-211`); emits `plan_tree.json(+.sha256)`, `calibration_plan.json`, `analysis_manifest_v3.json`, order manifests, condition families | **never runs `validate_prospective_analysis_manifest_v3` on its own output — the D-157 hole**; ships `EMPTY`/`TODO(` slots, no `families`, m=1 |
| S2 | Mint/freeze | `joulewise/arm_readiness.py` freeze receipt + plan-tree attachment; `_frozen_pack_identity:4934-4945` → `committed_pack_tree_sha256` | tree/plan digests, `resolve_frozen_plan:4965`, U11 projection, identity pins | manifest **bytes are pinned, never parsed**; no `families`/m/floor-dependency admission |
| S3 | Arm | `scripts/generate_arm_readiness.py`, `validate_arm_receipt` | freshness horizons, env fingerprint, quiet census, C→S confirmation pair | analysis semantics; `consume` lacks `--expected-confirmation-digest` (3f) |
| S4 | T-0 | `scripts/capture_t0_step.py` (twin trailer parser `:288-316`), `author_arm_evidence_t0.py` | POWERMETRICS_PROBE, clock/boot discipline | everything downstream |
| S5 | Launch | `scripts/launch_window.py:239/294` | one-shot capability, arm-receipt re-verify, lineage | **that its callee's required arguments are suppliable** (estate-6) |
| S6 | Collect | `run_campaign.py:7264` | cooldown, env preflight, prompt hashes, idle admission, strict bundle write; `load_analysis_manifest:1201` readiness reasons only | manifest semantics |
| S7 | Whole-window verdict | `run_whole_window_verdict:5505` | NEG-8 / idle admission over finalized bundles | manifest semantics |
| S8 | Finalize | `scripts/finalize_analysis_manifest.py` → `finalize_prospective_analysis_manifest_v3` | 4 required attachments; copies `families` verbatim; equal semantic hashes (`:3661`) | first look at manifest semantics — **post-window** |
| S9 | Claim edge | `python -m joulewise analyze-claims` → `analyze_claims` (`analysis_engine/__init__.py:1625`) → `evaluate_claim` (`claims.py:257`); `artifact.py:1574-1577` m == len(contrast_ids) | everything | — |

Second hole: no stage before S9 checks that a floor artifact exists for each declared floor dependency.

## 2. DESK REPLAY (CI, minutes)

**Smoke generation.** `generate_configs.py --pack-id ..._v9 --family-suffix _v9 --no-preserve-current-frozen-bytes --output-root $TMP`, with `fixed_n: 1` and decode+prefill contrasts. `--output-root` keeps it out of `configs/`; the downgrade guard already forbids touching `_v3`. **Internal consistency at tiny n is the load-bearing constraint**: the manifest must declare the n it will actually get, or `insufficient_complete_blocks`/`fixed_n_plan_incomplete` fire and the smoke fails for a contract reason it invented itself.

**Unarmable by construction — three independent fences, not one:** (a) configs declare `runtime_backend: mock`, `telemetry_backend: mock`, which stamps `mock_telemetry_claim_ineligible` (`analysis_engine/inputs.py:138`) into every bundle at the edge; (b) `--environment-override` marks members universally claim-ineligible; (c) the `_v9` ordinal is outside the D-117 published lineage and its runs root is `runs_..._v9`. Fence (a) is the one that cannot be forgotten, because it is a config byte, not an operator step.

**Run real / stub:** S1, S2, S3, S5, S6-orchestration, S7, S8, S9 run **for real**. Stubbed: the benchmark child and the sampler. Existing seams: `run_campaign.py --cli-cmd` (`:614`) plus `tests/test_run_campaign.py:1191 make_fake_cli`, which already synthesizes strict-valid bundles through the *real* `RunBundleWriter`/`reduce`; `cli.py:_select_clock:245` auto-binds `FakeClock` when both backends are mock, so wall time collapses. T-0/`prewindow_check.sh` are host-reading and are skipped in CI (covered by §3).

**Trace fidelity ladder.** Tier-1 (mock telemetry) proves plumbing only. Tier-2 replays a real trace: `PowermetricsTelemetryAdapter(executable=tests/fixtures/fake_powermetrics_process.py, privilege_prefix=(sys.executable,))` keeps the production parser, NUL framing, rail extraction and readiness bracket. **That constructor seam is not reachable from any CLI** — the one new seam this design needs.

**Pass predicate at S9.** `analyze_claims` **raising** (`AnalysisInputError`, `ClaimArtifactError`, `AnalysisManifestError`, `AnalysisManifestV3Error`, bare `ValueError`; CLI exit 2/3) = **CONTRACT → smoke FAIL**. `analyze_claims` **returning** = the derivation completed; outcome is then a data statement whatever it says. Refine with a checked-in explicit partition of `REASON_CODES`, because `_NOT_RESOLVABLE` (`claims.py:157-196`) deliberately mixes both kinds: DATA = `effect_not_above_floor`, `deterministic_bound_obscures_direction`, `interpolation_bound_exceeds_*`, `equivalence_*`, `multiplicity_not_rejected`, the `_SENSITIVITY` set, plus `outcome == "unresolved"` **with an empty reason list** (`claims.py:370` emits no code). CONTRACT = `bundle_*`, `config_hash_mismatch`, `floor_row_*`, `*_missing`, `*_mismatch`, `paired_block_incomplete`, `fixed_n_plan_incomplete`, `capture_pipeline_*`, `whole_window_*`. Do not key on `analysis_manifest_invalid`, `analysis_manifest_not_frozen`, `order_manifest_hash_mismatch`, `multiplicity_family_incomplete` — dead vocabulary, never emitted.

## 3. LIVE ~20-MINUTE VARIANT

Decode contrast only, `fixed_n = 1` → 4 bundles (a1,a2,b1,b2) + one reference pulse ≈ 17 min (the `_v4` pack's own budget is 310 min for 80 bundles + 3 pulses; the 168 h is D-150's *freeze horizon*, not collection time). Real MLX, real powermetrics, real `prewindow_check.sh`. Ed's hands per D-149: nothing needing cables/backlight/reboot/new sudo — the existing passwordless-powermetrics sudoers slice covers it, so T-0 auto-issues; Ed's remaining reserve is exact-byte confirmation, which the smoke never asks for.

**What replay cannot prove:** sudo/`powermetrics` spawn and termination against the real binary, the launch/readiness bracket against real rail energies, the CPU-admission and idle-daemon behaviour of a real quiet machine, and MLX load/decode timing. Those are exactly the seams that killed 2026-07-27.

**Quarantine:** same three fences as §2 minus (a) — a live smoke uses real telemetry, so it relies on (b) `--environment-override`, (c) the `_v9` ordinal and its own runs root, plus a fourth: the smoke pack is generated to `--output-root` outside `configs/` and never committed, so no freeze receipt binds it into the publishable family.

## 4. WHAT IT WOULD HAVE CAUGHT

- **D-157** — at S1 (the smoke generation's own manifest carries the same `EMPTY`/`TODO(`/m=1 defect) and, failing that, loudly at S9 as `not_estimable`/`ClaimArtifactError` "must equal frozen contrast count". Either way: minutes, not 168 h.
- **S0-O2** — S2/S3: the marker build needs a C→S digest that does not exist yet; the smoke traverses mint→marker→arm in one pass, so the ordering contradiction surfaces at the mint.
- **3e** (`generate_freeze_receipt` needs a table the CLI never passes) — S2, first freeze.
- **3f** / **launcher-argument gap** (estate 6: all three arms refused "no expected confirmation digest supplied") — S3/S5, because the smoke *executes* the consume/launch path rather than reasoning about it.

All four share one signature: **a contract-required input with no supply line**. The smoke is the general detector for that class, because it is the only thing that runs every producer against its real consumer.

## 5. COST & RISK

**Effort:** ~1.5–2 Sol days. (i) a `--telemetry-executable`/`--privilege-prefix` dev seam on the run verb, refuse-unless-config-declares-smoke, stamping a permanent claim-ineligible reason into the bundle; (ii) a `scripts/pipeline_smoke.py` driver chaining S1→S9 with the real scripts; (iii) the reason-code partition table + its test; (iv) one CI job.

**Must not touch:** frozen `_v3` bytes, any minted receipt, the `_v4` changed set, `.claude/settings.local.json`. The generator's downgrade guard already refuses `_v3`; `--output-root` keeps writes out of the tree. The new telemetry seam is the only production-code change and must be fail-closed: absent the smoke declaration, it refuses.

**Strongest counter-argument — "the shakedown already does this." It does not.** `--shakedown-gate production_uncertainty_v1` (`run_campaign.py:1599-1870`) is a **single-bundle** strict/reduce/evidence/backup gate that requires `powermetrics` and refuses mock runtime; D-139's shakedown is the quiet-state baseline and calibration-only runs ("minimal verifying runs… not polluted by any other signal"). Neither mints, freezes, finalizes, or invokes `analyze-claims`. The S-0 clone proof covers S1–S5 and stops at the mint. `tests/test_analysis_integration.py` covers S8–S9 over synthetic corpora but **stipulates** powermetrics telemetry identity (`:122-124`). The uncovered span is precisely S5→S8, and D-157 lived there.

**Second-strongest:** a mock-telemetry smoke can only ever prove plumbing, so it risks reading as instrument verification. Mitigation: the smoke's verdict artifact must carry `mock_telemetry_claim_ineligible` on its face, and the §3 live variant is not optional before the transaction.

## 6. RECOMMENDED CUT (next 48 h)

Build, in order: (1) the reason-code partition table + `assert_data_reason_only()` helper — hours, no production risk, and it is what makes any of the rest a pass/fail rather than a vibe; (2) `scripts/pipeline_smoke.py` at **tier-1** (mock backends, `--cli-cmd` fake collector, `_v9` output-root generation) chaining S1→S9, wired into CI; (3) fold R-2's admission check (`build_prospective_analysis_manifest_v3` on the freeze path) in as the smoke's first assertion, since W-10 is landing it anyway; (4) one **live 20-minute decode-only run** the night before the transaction, quarantined.

Waits: tier-2 replay (the `--telemetry-executable` seam), prefill arm, `prewindow_check.sh` stubbing, and any attempt to make the smoke's numbers mean anything physical. The 48-hour deliverable is one sentence: *every stage from generation to the claim edge was traversed and the edge answered for a data reason.*
