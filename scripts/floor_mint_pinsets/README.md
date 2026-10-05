# Floor mint pin authoring

`emit_floor_mint_pinset.py` authors a final `joulewise.floor_mint_pinset.v2`
and a `joulewise.floor_mint_inputs.v2` manifest. It reads identities from each
pack's producer contract and plan, and postcollection pins from the extraction
report, bundles, bracket binding and terminal ledger. It authenticates those
inputs through the generalized mint before deriving component artifact hashes.
It does not issue a floor or substitute missing postcollection evidence.

Supply exactly two occurrences of each producer argument, ALPHA then BETA.
The default `--prefill-role prefill_p2048` selects the claim-bearing `_v5`
prefill role; the other prefill role remains in the shared extraction spec's
physical member inventory. Consumer allowlists come from the consumer pack's
prospective analysis manifest and condition-family files. All output parents
must exist; outputs are exclusive and a failed second write removes the first.

```sh
"$PY" -B scripts/emit_floor_mint_pinset.py \
  --producer-pack "$ALPHA_PACK" --producer-pack "$BETA_PACK" \
  --runs-root "$ALPHA_RUNS" --runs-root "$BETA_RUNS" \
  --extraction-report "$ALPHA_REPORT" --extraction-report "$BETA_REPORT" \
  --bracket-binding "$ALPHA_BRACKET" --bracket-binding "$BETA_BRACKET" \
  --plan-relative-path "alpha/calibration_plan.json" \
  --plan-relative-path "beta/calibration_plan.json" \
  --consumer-pack "$GAMMA_PACK" \
  --calibration-acceptance "$CALIBRATION_ACCEPTANCE" \
  --calibration-ledger "$CALIBRATION_LEDGER" \
  --calibration-ledger-head-pin "$CALIBRATION_LEDGER_HEAD_PIN" \
  --calibration-custody-store "$CALIBRATION_CUSTODY_STORE" \
  --project-commit "$MINT_COMMIT" \
  --pinset-out "$FINAL_PINSET" --input-manifest-out "$V2_INPUT_MANIFEST"
```

Retain the printed `pinset_sha256` as `FINAL_PINSET_SHA256`. Plan relative paths
describe copies of the exact producer plan bytes relative to the aggregate
floor artifact directory. The mint commit is part of each component byte hash:
mint at that same clean HEAD before changing the checkout. Registration of the
emitted pinset under this directory makes its family discoverable by the claim
reader. Keep one pinset per family identity; multiple matches refuse.

The existing mint CLI already accepts and requires the D-165 output flag when
the supplied spec registers a common-mode comparative estimator:

```sh
"$PY" -B scripts/mint_floor_artifact_generalized.py \
  --pinset "$FINAL_PINSET" --pinset-sha256 "$FINAL_PINSET_SHA256" \
  --v2-input-manifest "$V2_INPUT_MANIFEST" \
  --calibration-custody-store "$CALIBRATION_CUSTODY_STORE" \
  --out "$AGGREGATE_FLOOR_ARTIFACT" --single-count-out "$SINGLE_COUNT_STATEMENT" \
  --d165-replay-out "$DOMINANCE_REPLAY_SIDECAR" \
  --project-commit "$MINT_COMMIT" --project-tree-state clean \
  --consumption-semantics-id "$CONSUMPTION_SEMANTICS_ID"

"$PY" -B scripts/finalize_analysis_manifest.py \
  --prospective-manifest "$PACK_ROOT/analysis_manifest_v3.json" \
  --plan-tree "$PACK_ROOT/plan_tree.json" \
  --custody-root "$ANALYSIS_CUSTODY_ROOT" --runs-root "$RUNS_ROOT" \
  --whole-window-verdict "$RUNS_ROOT/whole-window-verdict.json" \
  --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
  --calibration-ledger "$CALIBRATION_LEDGER" \
  --aggregate-floor-artifact "$AGGREGATE_FLOOR_ARTIFACT" \
  --dominance-replay-sidecar "$DOMINANCE_REPLAY_SIDECAR" \
  --output-dir "$ANALYSIS_CUSTODY_ROOT"
```

Finalization stages an external sidecar's exact bytes as
`dominance-replay-<sha256>.json` under finalize custody. Identical restaging is
idempotent; differing occupied bytes refuse. A sidecar already inside custody
retains its path. Omitting it preserves the dominance attachment refusal.

## Outstanding `_v5` inventory ruling

The current v2 schema and mint bind one scientific config hash to every
component of a producer. The committed decode and p2048 configurations have
different scientific config hashes for both models. The emitter preserves the
existing `config-set inventory mismatch` refusal. The lead must rule on a
prospective identity contract that supports those distinct configurations
before this final pinset can be issued for the actual `_v5` pair. Selecting
p42 would not supply GAMMA's registered p2048 transport groups.

The fixture regression exercises the real pin author, mint, artifact validator
and claim loader without mocking those seams. It uses explicitly synthetic
authenticated producer objects. Full file-custody CLI verification also needs
the archived D117 calibration custody fixture, which is absent in this checkout.
