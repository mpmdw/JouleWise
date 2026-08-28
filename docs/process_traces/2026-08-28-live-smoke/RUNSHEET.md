# PIPELINE-SMOKE-LIVE-01 — executable operator runsheet

**Purpose.** Execute one real, tiny, quarantined generation through generate →
U11 identity pin → primary freeze → arm → T-0 → launch/collect → bracket binding
→ whole-window verdict → floor extraction/mint → finalization → claim edge. This
document is desk preparation only. No command below may be run while an agent
session is active.

**Authority.** D-158 R-3 and its 2026-08-27 A-1..A-5 and 2026-08-28 hard-gate
addenda; D-160 R-2, F-5 and R-3′; the estate-11 A1..A5 assertions; state-kernel
acceptance at `/tasks/PIPELINE-SMOKE-LIVE-01`; the Phase A..H vocabulary and
U11/primary-freeze/arm/T-0/launch/H6 forms in
`docs/process_traces/2026-08-22-t20/real-transaction-runbook.md`; and the
operator chain in `docs/phase_2/window_runbook.md`.

**PASS.** The produced `claim_verdicts.json` is schema-valid and
`assert_data_reason_only(claim, expect_lock=None)` returns normally; S11 A1..A5
all pass; every D-160 F-5 join passes; and no command refused. A DATA result may
be an `unresolved` evaluation with an empty reason list. Any CONTRACT reason,
exception, missing artifact, skipped predecessor, nonzero exit, or retry is not
PASS. The authoritative partition and helper are
`joulewise.analysis_engine.reason_kinds.DATA_REASON_CODES` and
`assert_data_reason_only` (`reason_kinds.py:36-50,71-131`).

## BLOCKERS — resolve before machine execution

1. **B1 — quarantine identity cannot use a smoke prefix.** The gamma generator
   accepts only `_v<positive integer>` and requires the pack ID to equal its
   production base plus that suffix (`generate_configs.py:171-180`). The two
   floor generators use the same successor identity contract. The rendered
   candidate below is `_v9`, so the quarantine assertion is exact identity plus
   containment under `/Users/edr/JouleWise-smoke/`, not a textual smoke prefix.
   This deviates from D-158 R-3's “smoke pack id.” **Smallest cure if the ordinal
   is rejected:** add `--identity-prefix` (or a ruled `--diagnostic-pack-id`)
   beside `--pack-id`/`--family-suffix` in all three `generate_configs.py`
   parsers and thread the authenticated value through every emitted identity.

2. **B2 — the generators cannot emit the ruled tiny family.** Gamma hard-codes
   `N_BLOCKS = 10`, emits decode and prefill, and serializes `fixed_n` from that
   constant (`gamma generate_configs.py:92-95,906-924,1581`). The current parser
   has only `--check`, `--output-root`, `--pack-id`, `--family-suffix`, and the
   preserve boolean (`:2276-2306`). The floor generators likewise emit their
   full decode+prefill populations. **Smallest cure:** add `--n-blocks 1
   --measurement-arm decode` to the gamma and both floor generators; derive and
   assert `fixed_n` from the block count, thread those values through plans,
   manifests, counts, stage graphs, extraction specs, and output inventories,
   and retain exactly one A/B/B/A block. Add a separate fixed-n flag only if a
   ruling establishes independent semantics. The B1 generation commands below
   are **BLOCKED-UNTIL-CURE** and deliberately show those future flags.

3. **B3 — production admission has no authenticated quarantine lane.
   BLOCKED-UNTIL-CURE; NEEDS-RULING on admission shape.**
   `_plan_profile` refuses any successor ID not installed by the R1 registry as
   `readiness_row_registry_mismatch` (`arm_readiness.py:4097-4145`). Installing
   `_v9` in `configs/arm_readiness/d117_row_registry_v2.json` contradicts the
   ruling that the smoke never enters that registry. The only admissible cure
   is an authenticated diagnostic admission outside
   `d117_row_registry_v2.json`, threaded through primary freeze, T-0 capture,
   arm, and launch replay. The admission must authenticate this reviewed head,
   exact pack IDs, exact quarantine root, and one attempt. Its shape still
   needs a ruling. Admission alone is insufficient: `_v9` is generation 9, and
   without `--predecessor-pack-root` the freeze then refuses
   `readiness_successor_chain_invalid` (`arm_readiness.py:7360-7363`). An
   invented `_v8` is forbidden. Therefore the smallest cure must also define a
   diagnostic **GENESIS** rule: this quarantined family is admitted as
   generation-1-equivalent and carries no predecessor. The smallest parser
   change is
   beside freeze/arm in `scripts/generate_arm_readiness.py:36-73`, threaded to
   `joulewise/arm_readiness.py:7263-7271` and the arm entry point. The registry
   must remain byte-identical and the diagnostic family marker-ineligible. Do
   not implement the admission at the bench.

4. **B4 — `generation_kind` and the ruled class refusal do not exist.** A tree
   search finds no `generation_kind` in `joulewise/` or `scripts/`; therefore
   this live family must not carry `generation_kind: pipeline_smoke`, and no
   step relies on Unit B's not-yet-landed class refusal. Quarantine, exact IDs,
   registry non-membership, no marker, and final assertions are the available
   fences. If class refusal is still required, its smallest cure is a
   prospective top-level field emitted by the three generators plus production
   freeze/arm refusal; that cure would describe the desk smoke, not D-160 R-2's
   real non-smoke-scoped family.

5. **B5 — gamma is the only current profile, but the external runs-root check is
   blind.** `prewindow_check.sh` accepts only alpha/beta/gamma and hard-codes
   gamma's checkout-local `_v2` runs prefix (`:49-57`); T-0 obtains the profile
   from `_plan_profile` (`capture_t0_step.py:438-477`). This is a gamma contrast
   family, so `--window gamma` is semantically correct once B3 admits it.
   However the real smoke runs root is outside the checkout, so the checker's
   checkout-local occupancy test is vacuous. **Smallest cure:** make the shared
   T-0 parser pass the exact frozen `RUNS_ROOT`/`BOUND_RUNS_ROOT` to
   `prewindow_check.sh` (two explicit absolute-path flags), while retaining the
   gamma policy selection. The cure must also make `preflight.sh` and
   `prewindow_check.sh` invoke one shared, case-sensitive `ps aux` census helper
   with the exact governed vocabulary plus `caffeinate`; probe failure is a
   refusal, never an empty PASS. The private helper in this packet's
   `preflight.sh` is interim and does not discharge that shared-helper cure.

6. **B6 — no launchable frozen-chain supply. BLOCKED-UNTIL-CURE.** Before D2,
   produce the complete reviewed `window-chain.zsh`,
   `before_midpoint_stages.txt`, and `after_midpoint_stages.txt`; record
   `shasum -a 256 "$WINDOW_PLAN_ROOT/window-chain.zsh" >
   "$TRANSCRIPT_ROOT/window-chain.sha256"`. T0-ENV-PARSER-UNIFY-01 must also
   cure the authenticated arm/launch/step-6 inputs. E2 prose is not a producer.
   The current T-0 environment cannot launch the frozen chain:
   `_ENV_KEYS` excludes `ARM_RECEIPT` and `LAUNCH_MANIFEST`
   (`capture_t0_step.py:84-112`), although the runbook chain dereferences both.
   Bind either and T-0 refuses; omit either and `set -u` aborts the chain. The
   six T-0 commands below use only the keys the current parser accepts and are
   **BLOCKED-UNTIL-CURE**. **Smallest cure:** T0-ENV-PARSER-UNIFY-01—a shared
   parser used by capture and chain that admits the two generated paths and the
   authenticated step-6 supply line. Do not add ad hoc environment variables.

7. **B7 — aggregate-floor CLI exists, but the tiny-family supply artifacts do
   not.** The producer is `scripts/mint_floor_artifact_generalized.py`; its
   current v2 route requires `--pinset`, exact `--pinset-sha256`,
   `--v2-input-manifest`, `--out`, `--single-count-out`, `--project-commit`, and
   `--project-tree-state` (`:4031-4064`). Neither generator emits a final v2
   smoke-ordinal pinset or a `joulewise.floor_mint_inputs.v2` manifest, and the
   only checked-in pinset is the unrelated v1 `mint1.json`. **Smallest cure:**
   have the cured floor-family generation emit an outcome-blind final v2 pinset
   and a postcollection input-manifest builder whose paths bind the two tiny
   floor packs, their extraction reports, the finalized bracket session and
   binding. The mint command below is fully rendered but
   **BLOCKED-UNTIL-CURE** on those two named inputs.

8. **B8 — the pack must be committed in the declared measurement checkout.** The
   generator can write under an arbitrary `--output-root` (`gamma parser
   :2279,2297-2306`), but readiness derives a repository-relative committed pack
   and refuses a root outside a Git worktree as `readiness_pack_not_committed`
   (`arm_readiness.py:2723-2733`). The mint additionally requires the owning
   repository to equal `--measurement-checkout` (`:4202-4231`) and a successor
   requires an authenticated predecessor (`:7281-7284,7360-7363`). Thus the
   original off-repository pack layout cannot freeze `_v9`. The procedural
   resolution is a fresh smoke-dedicated checkout at
   `/Users/edr/JouleWise-smoke/checkout` and `$REVIEWED_HEAD`; generate below a
   repository path outside top-level `configs/`, then commit the generated pack
   bytes on a throwaway local branch that is never pushed. With that containment
   cure, B8 may need no code change. This satisfies only
   `_repository_and_pack_relative()` (`arm_readiness.py:2723-2733`) and
   `_gate_measurement_checkout()` (`:4202-4231`): `_v9` still refuses first as
   `readiness_row_registry_mismatch` (`:4130-4133`) and, even under diagnostic
   admission, as `readiness_successor_chain_invalid` (`:7360-7363`) because the
   C2 commands have no predecessor. Inventing `_v8` is forbidden and would
   additionally require historical-semantics authentication and the
   publication-marker gate. The B3 authenticated admission and diagnostic
   GENESIS rule remain mandatory.
   Copying into top-level `configs/`, creating fake `_v4.._v8` predecessors, or
   marker-signing is forbidden.

9. **B9 — “never marker-signed” conflicts with successor arm replay unless the
   quarantine admission owns the exception.** Current successor arm/freeze
   paths gate family publication and use `readiness_r1_family_publication`
   (`arm_readiness.py:7335-7358`; marker vocabulary begins at `:71`). The B3
   mechanism must explicitly make a quarantined diagnostic pack admissible
   without a publication marker while keeping production claims closed. No
   `build_family_marker` step appears below. The marker roster additionally
   pins `pack_path == configs/campaigns/<pack_id>`
   (`arm_readiness.py:10735`), which this smoke never meets and never needs to
   meet because it is never marker-signed; the B3 admission must not route
   through the marker gate.

## NEEDS-RULING

1. **Identity:** Is an exact `_v9` ordinal plus quarantine-root containment an
   acceptable “smoke pack id,” or must a smoke-prefix identity option land?
   Recommendation: add the diagnostic identity option; `_v9` falsely occupies
   production succession and lacks `_v8` ancestry.
2. **Admission:** What exact authenticated diagnostic-admission artifact and
   parser shape should primary freeze, T-0 capture, arm, and launch replay share?
   Recommendation: one content-addressed, one-attempt diagnostic license bound
   to the reviewed head, exact pack IDs, quarantine root, and local commit. It
   must live outside `d117_row_registry_v2.json`; the registry remains
   byte-identical, and the admitted family remains claim- and marker-ineligible.
   It must also declare a diagnostic **GENESIS** rule: the quarantined family is
   generation-1-equivalent and therefore has no predecessor. This is required
   because registry admission otherwise refuses at `arm_readiness.py:4130`,
   and a diagnostic bypass then still refuses `_v9` without
   `--predecessor-pack-root` at `:7360`; inventing `_v8` is forbidden.
3. **Checkout:** Use a fresh smoke-dedicated checkout at
   `/Users/edr/JouleWise-smoke/checkout` and `$REVIEWED_HEAD`. Generate the pack
   beneath that worktree on a throwaway local branch under a path outside
   top-level `configs/`, commit it locally, and never push it. Recommendation:
   adopt this procedural resolution because `arm_readiness.py:2723-2733`
   requires the pack below a Git worktree and `_gate_measurement_checkout`
   (`:4202-4231`) requires its minting repository to equal the declared
   measurement checkout. Those are the only two gates this procedure cures;
   the B3 registry and diagnostic-GENESIS rulings remain mandatory. Before A3,
   `$SMOKE_ROOT` may contain only `checkout/`.
4. **B5:** Is gamma admission with explicit external-root checking sufficient,
   or does the smoke need a distinct governed profile? Recommendation: gamma;
   it is the actual decode contrast family, not a new scientific profile.

No machine command below is authorized until every BLOCKER is cured at a new
reviewed head and every ruling above is recorded.

## Timeline estimate

| Phase | Activity | Desk time | Quiet-machine time |
|---|---|---:|---:|
| A | variables, preflight, quarantine layout | 5 min | 0 |
| B | generate three tiny packs and inspect | 3 min | 0 |
| C | three U11 projections + three primary freezes | 3 min + prompts | 2–4 min |
| D | arm authoring, T-0, 10-minute clean dwell | 3 min + prompts | 10–12 min |
| E | launch, two protocol-v3 calibrations, reference/bound stages, 14 tiny science runs | — | ≈20 min target; stop if rehearsal budget exceeds it |
| F | binding, verdict, extraction, floor mint | 5–10 min | 0 |
| G | finalize, claim edge, assertions | 5 min | 0 |
| H | seal/preserve and handoff | 3 min | 0 |
| **Total** | | **≈20–30 min desk** | **≈20 min machine target + T-0 dwell** |

The ≈20-minute machine figure is a target, not permission to omit reference,
calibration, or settle stages. Before arm, use observed per-member durations to
show the plan fits; if not, stop and return for a ruling.

## Quarantine tree and fixed variables

The final layout is:

```text
/Users/edr/JouleWise-smoke/
├── checkout/                         # fresh worktree at REVIEWED_HEAD
│   └── diagnostic/pipeline-smoke-live-01/packs/
│       ├── configs/campaigns/
│       │   ├── d117_contrast_qwen25_1p5b_vs_7b_v9/
│       │   ├── d117_floor_qwen25_1p5b_v9/
│       │   └── d117_floor_qwen25_7b_v9/
│       └── configs/floor_mint/
│           ├── d117_qwen25_1p5b_v9_extraction_spec.json
│           └── d117_qwen25_7b_v9_extraction_spec.json
├── analysis/                         # DISTINCT ANALYSIS ROOT
│   ├── runs/                         # exact ledger/binding runs_root
│   │   └── bracket-binding.json
│   ├── bound-runs/
│   ├── calibration/
│   ├── prospective/
│   ├── floor/
│   ├── whole-window-verdict.json
│   ├── am-….finalized.json
│   └── claim_verdicts.json
├── custody/
│   ├── readiness/window-plan/
│   ├── window/
│   ├── quarantine/
│   ├── transcripts/
│   └── refusals/
└── preserved/                        # post-run immutable TIER2 source
```

`$RUNS_ROOT` is nested below `$ANALYSIS_ROOT` because
`build_bracket_binding.py:478-483` requires it to be a canonical descendant of
the binding custody root. `$WINDOW_CUSTODY_ROOT` is separate from
`$ANALYSIS_ROOT`, satisfying D-160's distinct-analysis-root ruling.

### Phase A — desk preflight and declarations

**Freshness invariant.** Before the smoke checkout is provisioned,
`$SMOKE_ROOT` must not exist. Once it exists and before A2/A3, its exact and only
entry must be `checkout/`; that path must be a clean Git checkout at
`$REVIEWED_HEAD` with exactly one local branch, the checked-out branch. Any
other state is reuse and must refuse. Provisioning the fresh checkout is a
lead-owned prerequisite, not a command in this runsheet.

**A1 — export reviewed coordinates.** CWD: the terminal's current directory.
Timing: <1 min. Expected artifact: shell variables only. The selected
`$REVIEWED_HEAD` is the post-PR head that contains this `RUNSHEET.md`,
`preflight.sh`, and `00-verification-notes.md`; all three are part of the
reviewed head because they land via this PR. Expected refusal: `preflight.sh` prints `FAIL REVIEWED_HEAD is
required` or checkout mismatch.

```sh
export REVIEWED_HEAD='<paste full reviewed 40-hex SHA>'
export SMOKE_ROOT='/Users/edr/JouleWise-smoke'
export SMOKE_CHECKOUT="$SMOKE_ROOT/checkout"
export PACK_OUTPUT_RELATIVE='diagnostic/pipeline-smoke-live-01/packs'
export PACK_OUTPUT_ROOT="$SMOKE_CHECKOUT/$PACK_OUTPUT_RELATIVE"
export ANALYSIS_ROOT="$SMOKE_ROOT/analysis"
export RUNS_ROOT="$ANALYSIS_ROOT/runs"
export BOUND_RUNS_ROOT="$ANALYSIS_ROOT/bound-runs"
export WINDOW_CUSTODY_ROOT="$SMOKE_ROOT/custody/window"
export ARM_READINESS_CUSTODY_ROOT="$SMOKE_ROOT/custody/readiness"
export WINDOW_PLAN_ROOT="$ARM_READINESS_CUSTODY_ROOT/window-plan"
export QUARANTINE_ROOT="$SMOKE_ROOT/custody/quarantine"
export TRANSCRIPT_ROOT="$SMOKE_ROOT/custody/transcripts"
export REFUSAL_ROOT="$SMOKE_ROOT/custody/refusals"
export CALIBRATION_LEDGER="$ANALYSIS_ROOT/calibration/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$ANALYSIS_ROOT/calibration/calibration_ledger_head.json"
export IDENTITY_EPOCH_JSON="$SMOKE_ROOT/custody/identity-epoch.json"
export T1_BINDINGS_JSON="$SMOKE_ROOT/custody/t1-bindings.json"
export SMOKE_SUFFIX='_v9'
export GAMMA_PACK_ID='d117_contrast_qwen25_1p5b_vs_7b_v9'
export FLOOR_15_PACK_ID='d117_floor_qwen25_1p5b_v9'
export FLOOR_7_PACK_ID='d117_floor_qwen25_7b_v9'
export GAMMA_PACK_ROOT="$PACK_OUTPUT_ROOT/configs/campaigns/$GAMMA_PACK_ID"
export FLOOR_15_PACK_ROOT="$PACK_OUTPUT_ROOT/configs/campaigns/$FLOOR_15_PACK_ID"
export FLOOR_7_PACK_ROOT="$PACK_OUTPUT_ROOT/configs/campaigns/$FLOOR_7_PACK_ID"
export PY='/Users/edr/code/JouleWise/.venv/bin/python'
export PYTHONPATH="$SMOKE_CHECKOUT"
export POLICY="$SMOKE_CHECKOUT/configs/campaign_policies/quiet_mac_p2_production.json"
export WINDOW_ID='pipeline-smoke-live-01-v9'
export BRACKET_SESSION_ID='pipeline-smoke-live-01-v9-bracket'
export PRE_ATTEMPT_ID='pipeline-smoke-live-01-v9-pre'
export POST_ATTEMPT_ID='pipeline-smoke-live-01-v9-post'
export POWER_POLICY='ac_high_power'
```

**A2 — run the read-only preflight.** CWD:
`$SMOKE_CHECKOUT`. Timing: <1 min. Expected output: stdout containing only
`PASS …` lines; the script creates no intentional project or measurement
artifacts. Expected refusal: any `FAIL …`, exit 1. The source venv is required
because the fresh checkout has no tracked `.venv` (`.gitignore:6`). Every
Python command inherits `PYTHONPATH=$SMOKE_CHECKOUT`; preflight verifies with
the same import probe that `joulewise.__file__` begins with `$SMOKE_CHECKOUT`.
If the source venv's editable install resolves `joulewise` from
`/Users/edr/code/JouleWise` instead, this gate FAILS; the cure is the exported
`PYTHONPATH=$SMOKE_CHECKOUT` for every command, followed by the same probe.
The operator must close this and every other agent session before invoking it.

```sh
cd "$SMOKE_CHECKOUT"
/bin/bash "$SMOKE_CHECKOUT/docs/process_traces/2026-08-28-live-smoke/preflight.sh"
```

**A3 — materialize quarantine only after A2 PASS.** CWD: `$SMOKE_CHECKOUT`.
Timing: <1 min. Expected artifacts: the tree above. Expected refusal: anything
except the fresh `checkout/` already exists below `$SMOKE_ROOT`; stop, never
reuse. Quarantine assertion: every created path resolves below `$SMOKE_ROOT`.

```sh
test -d "$SMOKE_CHECKOUT"
test "$(/usr/bin/find "$SMOKE_ROOT" -mindepth 1 -maxdepth 1 -print | /usr/bin/wc -l | tr -d ' ')" = 1
test "$(/usr/bin/find "$SMOKE_ROOT" -mindepth 1 -maxdepth 1 -print)" = "$SMOKE_CHECKOUT"
test "$(git -C "$SMOKE_CHECKOUT" rev-parse --verify HEAD)" = "$REVIEWED_HEAD"
test -z "$(git -C "$SMOKE_CHECKOUT" status --porcelain=v1 --untracked-files=all)"
test "$(git -C "$SMOKE_CHECKOUT" branch --list | /usr/bin/wc -l | tr -d ' ')" = 1
test "$(git -C "$SMOKE_CHECKOUT" branch --show-current)" = "$(git -C "$SMOKE_CHECKOUT" branch --format='%(refname:short)')"
/bin/mkdir -p "$RUNS_ROOT" "$BOUND_RUNS_ROOT" \
  "$ANALYSIS_ROOT/calibration" "$ANALYSIS_ROOT/prospective" "$ANALYSIS_ROOT/floor" \
  "$WINDOW_CUSTODY_ROOT" "$WINDOW_PLAN_ROOT" "$QUARANTINE_ROOT" \
  "$TRANSCRIPT_ROOT" "$REFUSAL_ROOT"
case "$(cd "$SMOKE_ROOT" && pwd -P)" in /Users/edr/JouleWise-smoke) ;; *) exit 1;; esac
git -C "$SMOKE_CHECKOUT" status --porcelain=v1 --untracked-files=all > "$TRANSCRIPT_ROOT/git-status-before.txt"
shasum -a 256 "$SMOKE_CHECKOUT/configs/arm_readiness/d117_row_registry_v2.json" > "$TRANSCRIPT_ROOT/registry-before.sha256"
```

**A4 — seed the append-only calibration ledger and derive its two identity
inputs.** CWD: `$SMOKE_CHECKOUT`. Timing: <1 min. Expected artifacts:
`$CALIBRATION_LEDGER`, `$LEDGER_HEAD_PIN`, `$IDENTITY_EPOCH_JSON`, and
`$T1_BINDINGS_JSON`, all below `$SMOKE_ROOT`. Expected refusal: source
ledger/head absent, empty, or the last admitted row does not carry the closed
identity schemas. This reuses the runbook's canonical ledger source
(`window_runbook.md:204-205`) and the extraction form in
`scripts/ed_session/build_rehearsal_env.sh:95-107`, but uses the real ledger,
not its fixture.

```sh
/bin/cp -p /Users/edr/code/JouleWise/runs/calibration_observation_ledger.jsonl "$CALIBRATION_LEDGER"
/bin/cp -p "$SMOKE_CHECKOUT/configs/calibration/calibration_ledger_head.json" "$LEDGER_HEAD_PIN"
"$PY" - "$CALIBRATION_LEDGER" "$IDENTITY_EPOCH_JSON" "$T1_BINDINGS_JSON" <<'PY'
import json,sys
from pathlib import Path
from joulewise.calibration_ledger import IDENTITY_EPOCH_FIELDS,T1_FIELDS,canonical_json_bytes
ledger,epoch_path,t1_path=map(Path,sys.argv[1:])
rows=[json.loads(x) for x in ledger.read_text().splitlines() if x]
assert rows
epoch=dict(rows[-1]['identity_epoch']); t1=dict(rows[-1]['t1_bindings'])
assert set(epoch)==set(IDENTITY_EPOCH_FIELDS)
assert set(t1)==set(T1_FIELDS)
epoch_path.write_bytes(canonical_json_bytes(epoch)+b'\n')
t1_path.write_bytes(canonical_json_bytes(t1)+b'\n')
print('PASS calibration identity inputs')
PY
```

### Phase B — emit the one tiny family

**B1 — generate gamma and both floor packs. BLOCKED-UNTIL-CURE (B1/B2).**
CWD: `$SMOKE_CHECKOUT`. Timing: 1–3 min. Expected artifacts: the three pack
roots, each with `calibration_plan.json`, `plan_tree.json`, root order manifest,
and generator-owned manifests/specs; gamma has a prospective
`analysis_manifest_v3.json`. Expected refusal if flags are absent:
`argparse: unrecognized arguments`. The generated tree is later committed on a
throwaway local branch before primary freeze; it is never pushed.

```sh
cd "$SMOKE_CHECKOUT"
"$PY" configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py \
  --output-root "$PACK_OUTPUT_ROOT" --pack-id "$GAMMA_PACK_ID" \
  --family-suffix "$SMOKE_SUFFIX" --no-preserve-current-frozen-bytes \
  --n-blocks 1 --measurement-arm decode \
  > "$TRANSCRIPT_ROOT/generate-gamma.stdout" 2> "$TRANSCRIPT_ROOT/generate-gamma.stderr"
"$PY" configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py \
  --output-root "$PACK_OUTPUT_ROOT" --pack-id "$FLOOR_15_PACK_ID" \
  --family-suffix "$SMOKE_SUFFIX" --no-preserve-current-frozen-bytes \
  --n-blocks 1 --measurement-arm decode \
  > "$TRANSCRIPT_ROOT/generate-floor-15.stdout" 2> "$TRANSCRIPT_ROOT/generate-floor-15.stderr"
"$PY" configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py \
  --output-root "$PACK_OUTPUT_ROOT" --pack-id "$FLOOR_7_PACK_ID" \
  --family-suffix "$SMOKE_SUFFIX" --no-preserve-current-frozen-bytes \
  --n-blocks 1 --measurement-arm decode \
  > "$TRANSCRIPT_ROOT/generate-floor-7.stdout" 2> "$TRANSCRIPT_ROOT/generate-floor-7.stderr"
```

**B2 — assert real, non-smoke-scoped, tiny bytes, then commit them locally.**
CWD: `$SMOKE_CHECKOUT`.
Timing: <1 min. Expected output: `PASS generated family shape`. Expected
refusal: any missing/extra arm, block, `calibration_scope == smoke`,
`generation_kind`, or wrong identity. This is the pack-id check required by
D-158 A-1, adapted under B1.

```sh
"$PY" - "$GAMMA_PACK_ROOT" "$FLOOR_15_PACK_ROOT" "$FLOOR_7_PACK_ROOT" <<'PY'
import hashlib, json, pathlib, sys
roots=[pathlib.Path(x).resolve() for x in sys.argv[1:]]
expected=['d117_contrast_qwen25_1p5b_vs_7b_v9','d117_floor_qwen25_1p5b_v9','d117_floor_qwen25_7b_v9']
for root,name in zip(roots,expected):
    assert root.name == name
    assert root.is_relative_to(pathlib.Path('/Users/edr/JouleWise-smoke').resolve())
    values=[json.loads(p.read_text()) for p in root.rglob('*.json')]
    assert all(v.get('calibration_scope') != 'smoke' for v in values if isinstance(v,dict))
    def reject_generation_kind(value):
        if isinstance(value,dict):
            assert 'generation_kind' not in value
            for child in value.values(): reject_generation_kind(child)
        elif isinstance(value,list):
            for child in value: reject_generation_kind(child)
    for value in values: reject_generation_kind(value)
plans=[json.loads((root/'calibration_plan.json').read_text()) for root in roots]
assert all(plan['fixed_n'] == 1 for plan in plans)
gamma_manifest_raw=(roots[0]/'analysis_manifest_v3.json').read_bytes()
gamma_manifest=json.loads(gamma_manifest_raw)
gamma_tree=json.loads((roots[0]/'plan_tree.json').read_text())
assert hashlib.sha256(gamma_manifest_raw).hexdigest()==gamma_tree['downstream_contract']['analysis_manifest_sha256']
assert set(plans[0]['stack_scope']['measurement_arms']) == {'decode'}
assert [c['measurement_arm'] for c in gamma_manifest['contrasts']] == ['decode']
assert len(gamma_manifest['contrasts'][0]['block_ids']) == 1
gamma_members=gamma_manifest['contrasts'][0]['members']
assert len(gamma_members) == 4
assert [m['arm'] for m in gamma_members] == ['A','B','B','A']
assert [m['position'] for m in gamma_members] == ['A1','B1','B2','A2']
assert {m['block_id'] for m in gamma_members} == set(gamma_manifest['contrasts'][0]['block_ids'])
for root,plan in zip(roots[1:],plans[1:]):
    tree=json.loads((root/'plan_tree.json').read_text())
    spec_ref=tree['downstream_contract']['extraction_spec']
    spec_path=pathlib.Path('/Users/edr/JouleWise-smoke/checkout/diagnostic/pipeline-smoke-live-01/packs')/spec_ref['path']
    spec_raw=spec_path.read_bytes()
    assert hashlib.sha256(spec_raw).hexdigest() == spec_ref['sha256']
    spec=json.loads(spec_raw)
    reject_generation_kind(spec)
    order=json.loads((root/'order_manifest.json').read_text())
    assert order['calibration_plan_sha256']==hashlib.sha256((root/'calibration_plan.json').read_bytes()).hexdigest()
    cells=plan['floor_cells']
    assert len(cells) == 2 and all(c['metric']=='phase_energy_j.decode' for c in cells)
    absolute=[c for c in cells if c['kind']=='absolute']
    abba=[c for c in cells if c['kind']=='comparative_abba']
    assert len(absolute)==1 and len(absolute[0]['ordered_bundle_ids'])==1
    assert len(abba)==1 and len(abba[0]['ordered_blocks'])==1
    assert [m['position'] for m in abba[0]['ordered_blocks'][0]['members']]==['A1','B1','B2','A2']
    assert order['planned_n_bundles']==5 and len(order['executed_order'])==5
    assert len(spec['cells'])==2 and all(c['metric']=='phase_energy_j.decode' for c in spec['cells'])
print('PASS generated family shape')
PY
git -C "$SMOKE_CHECKOUT" switch -c pipeline-smoke-live-01-local
git -C "$SMOKE_CHECKOUT" add -- "$PACK_OUTPUT_RELATIVE"
git -C "$SMOKE_CHECKOUT" commit -m 'quarantine: pipeline smoke live pack'
export SMOKE_PACK_COMMIT="$(git -C "$SMOKE_CHECKOUT" rev-parse HEAD)"
test "$(git -C "$SMOKE_CHECKOUT" rev-parse HEAD^)" = "$REVIEWED_HEAD"
test -z "$(git -C "$SMOKE_CHECKOUT" status --porcelain=v1 --untracked-files=all)"
```

### Phase C — U11 identity pin and primary freeze

**C1 — U11 identity-pin projection ×3 — ED PROMPT.**
CWD: `$SMOKE_CHECKOUT`. Timing: model hashing dominates, ≈1–3 min for the tiny
pack metadata. Expected artifact per pack:
`identity_pin_projection.receipts/projection-0001.json` plus sidecar. Initial
`freeze_projection()` derives and writes an unfrozen pack without committed-
freeze containment authentication; its Git anchor authenticates the tool
repository. B3/B8 still gate the later primary readiness freeze/T-0 path. Run
one command, inspect PASS, then the next; never concatenate.

```sh
"$PY" scripts/project_identity_pins.py freeze "$GAMMA_PACK_ROOT" > "$TRANSCRIPT_ROOT/u11-gamma.json"
git -C "$SMOKE_CHECKOUT" add -- "$PACK_OUTPUT_RELATIVE"
git -C "$SMOKE_CHECKOUT" commit -m 'quarantine: project gamma identity pins'
"$PY" scripts/project_identity_pins.py freeze "$FLOOR_15_PACK_ROOT" > "$TRANSCRIPT_ROOT/u11-floor-15.json"
git -C "$SMOKE_CHECKOUT" add -- "$PACK_OUTPUT_RELATIVE"
git -C "$SMOKE_CHECKOUT" commit -m 'quarantine: project 1.5B floor identity pins'
"$PY" scripts/project_identity_pins.py freeze "$FLOOR_7_PACK_ROOT" > "$TRANSCRIPT_ROOT/u11-floor-7.json"
git -C "$SMOKE_CHECKOUT" add -- "$PACK_OUTPUT_RELATIVE"
git -C "$SMOKE_CHECKOUT" commit -m 'quarantine: project 7B floor identity pins'
export SMOKE_PACK_COMMIT="$(git -C "$SMOKE_CHECKOUT" rev-parse HEAD)"
```

**C2 — primary readiness freeze ×3 — ED PROMPT. BLOCKED-UNTIL-CURE
B1/B3/B8/B9.** CWD: `$SMOKE_CHECKOUT`. Timing: 1–3 min. Expected artifact per
pack: one create-only `arm_readiness.freeze.receipts/freeze-NNNN.json` and
sidecar, with PASS and no reason codes. Expected refusal if predecessor or
quarantine admission is absent: `readiness_successor_chain_invalid` or
`readiness_row_registry_mismatch`; if marker enforcement is reached:
`readiness_r1_family_publication`. `$DIAGNOSTIC_ADMISSION` below names the
future ruled B3 input. Its exact shape is NEEDS-RULING; the only admissible
route is outside the byte-identical row registry and binds `$REVIEWED_HEAD`,
`$SMOKE_PACK_COMMIT`, the three exact pack IDs, `$SMOKE_ROOT`, and one attempt.
It must declare the B3 diagnostic GENESIS semantics (generation-1-equivalent,
no predecessor). It is not a current parser flag.

```sh
export DIAGNOSTIC_ADMISSION='--quarantine-admission /Users/edr/JouleWise-smoke/analysis/prospective/quarantine-admission.json'
"$PY" scripts/generate_arm_readiness.py freeze --pack-root "$GAMMA_PACK_ROOT" \
  --measurement-checkout "$SMOKE_CHECKOUT" $DIAGNOSTIC_ADMISSION \
  > "$TRANSCRIPT_ROOT/freeze-gamma.json"
git -C "$SMOKE_CHECKOUT" add -- "$PACK_OUTPUT_RELATIVE"
git -C "$SMOKE_CHECKOUT" commit -m 'quarantine: record gamma readiness freeze'
"$PY" scripts/generate_arm_readiness.py freeze --pack-root "$FLOOR_15_PACK_ROOT" \
  --measurement-checkout "$SMOKE_CHECKOUT" $DIAGNOSTIC_ADMISSION \
  > "$TRANSCRIPT_ROOT/freeze-floor-15.json"
git -C "$SMOKE_CHECKOUT" add -- "$PACK_OUTPUT_RELATIVE"
git -C "$SMOKE_CHECKOUT" commit -m 'quarantine: record 1.5B floor readiness freeze'
"$PY" scripts/generate_arm_readiness.py freeze --pack-root "$FLOOR_7_PACK_ROOT" \
  --measurement-checkout "$SMOKE_CHECKOUT" $DIAGNOSTIC_ADMISSION \
  > "$TRANSCRIPT_ROOT/freeze-floor-7.json"
git -C "$SMOKE_CHECKOUT" add -- "$PACK_OUTPUT_RELATIVE"
git -C "$SMOKE_CHECKOUT" commit -m 'quarantine: record 7B floor readiness freeze'
export MINT_HEAD="$(git -C "$SMOKE_CHECKOUT" rev-parse --verify HEAD)"
test -z "$(git -C "$SMOKE_CHECKOUT" status --porcelain=v1 --untracked-files=all)"
```

No `build_family_marker`, marker verify, or marker promotion occurs. If any
marker file appears, ABORT. A marker builder against these bytes must refuse
because the quarantine lifecycle is marker-ineligible; if the B3 cure does not
enforce that, it is incomplete.

### Phase D — window plan, arm receipt, and T-0

**D1 — freeze `window.env` using only current `_ENV_KEYS`.
BLOCKED-UNTIL-CURE B6.** CWD: `$SMOKE_CHECKOUT`. Timing: 2 min. Expected
artifact: `$WINDOW_PLAN_ROOT/window.env`. Expected refusal if either ruled
missing key is added today: `evidence_author_t0_capture_environment_invalid`.
   The B6 cure must produce the complete reviewed chain and add the generated
   `ARM_RECEIPT`, `LAUNCH_MANIFEST`, and authenticated step-6 supply without
   changing values by hand.

```sh
export PLAN_ID="$(/usr/bin/jq -er '.plan_id' "$GAMMA_PACK_ROOT/calibration_plan.json")"
export PLAN_SHA256="$(shasum -a 256 "$GAMMA_PACK_ROOT/calibration_plan.json" | awk '{print $1}')"
export EVIDENCE_ROOT_ID="$(/usr/bin/jq -er '.evidence_root_id' "$GAMMA_PACK_ROOT/analysis_manifest_v3.json")"
export IDENTITY_EPOCH_JSON="$SMOKE_ROOT/custody/identity-epoch.json"
export T1_BINDINGS_JSON="$SMOKE_ROOT/custody/t1-bindings.json"
export CALIBRATION_LEDGER="$ANALYSIS_ROOT/calibration/calibration_observation_ledger.jsonl"
export LEDGER_HEAD_PIN="$ANALYSIS_ROOT/calibration/calibration_ledger_head.json"
export CLAIM_BACKUP_DEST="$SMOKE_ROOT/preserved/claim"
export BOUND_BACKUP_DEST="$SMOKE_ROOT/preserved/bound"
export WAIVER_PATH="$WINDOW_PLAN_ROOT/waivers.json"
/usr/bin/printf '[]\n' > "$WAIVER_PATH"
/usr/bin/printf '%s\n' \
  "MEASUREMENT_REPO=$SMOKE_CHECKOUT" \
  "WINDOW_ID=$WINDOW_ID" \
  "BRACKET_SESSION_ID=$BRACKET_SESSION_ID" \
  "FROZEN_PLAN=$GAMMA_PACK_ROOT/calibration_plan.json" \
  "PACK_ROOT=$GAMMA_PACK_ROOT" \
  "PACK_ID=$GAMMA_PACK_ID" \
  "PLAN_ID=$PLAN_ID" \
  "EVIDENCE_ROOT_ID=$EVIDENCE_ROOT_ID" \
  "IDENTITY_EPOCH_JSON=$IDENTITY_EPOCH_JSON" \
  "T1_BINDINGS_JSON=$T1_BINDINGS_JSON" \
  "PRE_ATTEMPT_ID=$PRE_ATTEMPT_ID" \
  "POST_ATTEMPT_ID=$POST_ATTEMPT_ID" \
  "RUNS_ROOT=$RUNS_ROOT" \
  "BOUND_RUNS_ROOT=$BOUND_RUNS_ROOT" \
  "CALIBRATION_LEDGER=$CALIBRATION_LEDGER" \
  "LEDGER_HEAD_PIN=$LEDGER_HEAD_PIN" \
  "ARM_READINESS_CUSTODY_ROOT=$ARM_READINESS_CUSTODY_ROOT" \
  "CUSTODY_ROOT=$WINDOW_CUSTODY_ROOT" \
  "WINDOW_CUSTODY_ROOT=$WINDOW_CUSTODY_ROOT" \
  "QUARANTINE_ROOT=$QUARANTINE_ROOT" \
  "CLAIM_BACKUP_DEST=$CLAIM_BACKUP_DEST" \
  "BOUND_BACKUP_DEST=$BOUND_BACKUP_DEST" \
  "WAIVER_PATH=$WAIVER_PATH" \
  "POWER_POLICY=$POWER_POLICY" \
  'SETTLE_S=180' > "$WINDOW_PLAN_ROOT/window.env"
test "$(/usr/bin/wc -l < "$WINDOW_PLAN_ROOT/window.env" | tr -d ' ')" = 25
/usr/bin/printf '%s\n' \
  "$PACK_OUTPUT_RELATIVE/configs/campaigns/$FLOOR_15_PACK_ID" \
  "$PACK_OUTPUT_RELATIVE/configs/campaigns/$FLOOR_7_PACK_ID" \
  > "$WINDOW_PLAN_ROOT/before_midpoint_stages.txt"
/usr/bin/printf '%s\n' \
  "$PACK_OUTPUT_RELATIVE/configs/campaigns/$GAMMA_PACK_ID" \
  > "$WINDOW_PLAN_ROOT/after_midpoint_stages.txt"
test -s "$WINDOW_PLAN_ROOT/window-chain.zsh"
shasum -a 256 "$WINDOW_PLAN_ROOT/window-chain.zsh" > "$TRANSCRIPT_ROOT/window-chain.sha256"
```

Render `window.env` with exactly the 25 names at
`capture_t0_step.py:84-112`: `MEASUREMENT_REPO`, `WINDOW_ID`,
`BRACKET_SESSION_ID`, `FROZEN_PLAN=$GAMMA_PACK_ROOT/calibration_plan.json`,
`PACK_ROOT=$GAMMA_PACK_ROOT`, `PACK_ID`, `PLAN_ID`, `EVIDENCE_ROOT_ID`,
`IDENTITY_EPOCH_JSON`, `T1_BINDINGS_JSON`, `PRE_ATTEMPT_ID`,
`POST_ATTEMPT_ID`, `RUNS_ROOT`, `BOUND_RUNS_ROOT`, `CALIBRATION_LEDGER`,
`LEDGER_HEAD_PIN`, `ARM_READINESS_CUSTODY_ROOT`,
`CUSTODY_ROOT=$WINDOW_CUSTODY_ROOT`, `WINDOW_CUSTODY_ROOT`,
`QUARANTINE_ROOT`, `CLAIM_BACKUP_DEST`, `BOUND_BACKUP_DEST`, `WAIVER_PATH`,
`POWER_POLICY`, and `SETTLE_S=180`. Every path is absolute and literal. After
B6, the shared parser also supplies the author-produced arm and launch paths.

**D2 — six T-0 captures in code order. BLOCKED-UNTIL-CURE B3/B5/B6.** CWD:
`$SMOKE_CHECKOUT`. Timing: ≥10 min because `prewindow-check` must prove 600 s
continuous clean dwell (`capture_t0_step.py:641-645`). Expected artifacts under
`$ARM_READINESS_CUSTODY_ROOT/$GAMMA_PACK_ID/arm_readiness.t0.inputs/`:
`clock-reference.json`, `clock-disable.json`, `quiet-mac-prep.json`,
`prewindow-check.json`, `ledger-readiness.json`, `ledger-reservation.json`, plus
derived `arm-context.json` and `launch-manifest.json`. Expected refusal when a
predecessor is skipped: `evidence_author_t0_capture_sequence_invalid`
(`:608-666`). Current code says `clock-reference`, not the runbook's stale
`clock-prior-state` (`:41-49,527-602`).

```sh
for step in clock-reference clock-disable quiet-mac-prep prewindow-check ledger-readiness ledger-reservation; do
  "$PY" scripts/capture_t0_step.py "$step" \
    --pack-root "$GAMMA_PACK_ROOT" \
    --custody-root "$ARM_READINESS_CUSTODY_ROOT" \
    --window-plan-root "$WINDOW_PLAN_ROOT" \
    > "$TRANSCRIPT_ROOT/t0-$step.json" || exit 1
done
```

**D3 — author and verify the arm — ED PROMPT. BLOCKED-UNTIL-CURE B3/B9.**
CWD: `$SMOKE_CHECKOUT`. Timing: 1 min. Expected artifacts: one
`arm-NNNN.json` plus sidecar in readiness custody; verifier prints PASS/GO.
Expected refusal if D2 is incomplete or marker/admission is unresolved:
`readiness_*` NO_GO. The `--arm-context` value is the JSON object itself
(`generate_arm_readiness.py:65-73,91-103`), not a path.

```sh
export ARM_CONTEXT_JSON="$(/usr/bin/jq -c . "$ARM_READINESS_CUSTODY_ROOT/$GAMMA_PACK_ID/arm_readiness.t0.inputs/arm-context.json")"
"$PY" scripts/generate_arm_readiness.py arm --pack-root "$GAMMA_PACK_ROOT" \
  --arm-context "$ARM_CONTEXT_JSON" \
  --window-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  > "$TRANSCRIPT_ROOT/arm.json"
export ARM_RECEIPT="$(/usr/bin/jq -er '.receipt_path' "$TRANSCRIPT_ROOT/arm.json")"
"$PY" scripts/generate_arm_readiness.py verify --pack-root "$GAMMA_PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" > "$TRANSCRIPT_ROOT/arm-verify.json"
export LAUNCH_MANIFEST="$ARM_READINESS_CUSTODY_ROOT/$GAMMA_PACK_ID/arm_readiness.t0.inputs/launch-manifest.json"
```

### Phase E — T-0 launch and foreground measurement chain

**QUIET-MAC boundary.** Close all agents. Ed invokes E1 once. No monitoring,
retry, dry-run, direct `window-chain.zsh`, or second launcher is permitted.

**E1 — physical launch through execve — ED PROMPT. BLOCKED-UNTIL-CURE B6/B9.**
CWD: `$SMOKE_CHECKOUT`. Timing: invocation <1 min; it does not return on
success. Expected artifacts: launch consumption primary+sidecar, then start,
settle and completion lifecycle receipts and `.joulewise-launch-lineage.json`
under both runs roots. Expected refusal if the frozen manifest or FD-198
handoff is absent: `launch_consumption_*` / `launch_handoff_invalid`. Flags are
the current parser (`launch_window.py:38-60`). The B3/B9 cure must define the
non-marker confirmation/admission input; do not fabricate a step-6 table.

```sh
cd "$SMOKE_CHECKOUT"
"$PY" scripts/launch_window.py \
  --pack-root "$GAMMA_PACK_ROOT" \
  --arm-receipt "$ARM_RECEIPT" \
  --arm-readiness-custody-root "$ARM_READINESS_CUSTODY_ROOT" \
  --launch-manifest "$LAUNCH_MANIFEST"
```

**E2 — frozen `window-chain.zsh` behavior (executed only by E1).** CWD is
`$SMOKE_CHECKOUT`, as authenticated in T-0. The chain must use the exact
`run_campaign.py` collection form below (`run_campaign.py:660-719`) with real
CLI, real MLX and real powermetrics; no `--cli-cmd`, no `--dry-run`, no
environment override. It runs: lifecycle `start`; 180 s settle; pre protocol-v3
calibration through `validate_powermetrics_fiducial.py`; pre-calibration screen;
NEG-8 bound corpus and bound mint; start reference triplet; the two tiny floor
pack roots; midpoint reference; gamma pack root; end reference triplet; post
protocol-v3 calibration; lifecycle `completion`.

Each science/reference stage uses this exact function:

```sh
"$PY" scripts/run_campaign.py "$CONFIG_ROOT" \
  --runs-dir "$TARGET_RUNS_ROOT" \
  --log "$TARGET_RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy "$POLICY" \
  --instrument-calibration-dir "$PRE_CAL_CUSTODY" \
  --instrument-power-policy "$POWER_POLICY" \
  --arm-quiet-mode --arm-countdown-s 20 --max-failures 1
```

Expected artifact per config: one immutable bundle under the selected root and
one `campaign_manifests/*.json` producer record. Any nonzero exit or missing
bundle stops `set -e`; it is not retried. Quarantine assertion: both target
roots resolve under `$ANALYSIS_ROOT`; run IDs are unique; gamma has exactly four
science bundles, and each floor pack has only its cured fixed-n=1 decode cells.

Calibration uses the runbook's `calibrate_slot` command form:

```sh
"$PY" scripts/validate_powermetrics_fiducial.py --allow-live \
  --arm-countdown-s 20 --sleep-display-before-capture \
  --output-root "$RUNS_ROOT/instrument_validation" \
  --ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --session-id "$BRACKET_SESSION_ID" --slot "$SLOT" --attempt-id "$ATTEMPT_ID" \
  --power-policy "$POWER_POLICY"
```

Expected artifacts: finalized pre and post protocol-v3 custody plus a finalized
ledger session. If either calibration refuses, ABORT; never select a later
calibration. The actual chain content must be hashed before D2 and its digest
recorded in `$TRANSCRIPT_ROOT/window-chain.sha256`.

### Phase F — postcollection binding, verdict, extraction, and floor

These are desk steps after launch completion. Agent sessions may resume only
after all capture processes have ended.

**F1 — build the bracket binding before the verdict.** CWD:
`$SMOKE_CHECKOUT`. Timing: <1 min. Expected artifact:
`$RUNS_ROOT/bracket-binding.json` with schema
`joulewise.calibration_bracket_binding.v1`. Expected refusal if E2 did not
finalize both ledger endpoints: `bracket_binding_session_not_finalized` or
`bracket_binding_session_endpoints_invalid`. This order is required by code:
the builder takes ledger/session/plan/root inputs and no verdict
(`build_bracket_binding.py:383-413,523-541`); the evaluator consumes the binding
(`run_campaign.py:734-760`); finalization then consumes both
(`finalize_analysis_manifest.py:30-38`).

```sh
cd "$SMOKE_CHECKOUT"
/bin/cp -p "$GAMMA_PACK_ROOT/calibration_plan.json" "$ANALYSIS_ROOT/prospective/calibration_plan.json"
/bin/cp -p "$GAMMA_PACK_ROOT/plan_tree.json" "$ANALYSIS_ROOT/prospective/plan_tree.json"
/bin/cp -p "$GAMMA_PACK_ROOT/analysis_manifest_v3.json" "$ANALYSIS_ROOT/prospective/analysis_manifest_v3.json"
/usr/bin/cmp -s "$GAMMA_PACK_ROOT/calibration_plan.json" "$ANALYSIS_ROOT/prospective/calibration_plan.json"
/usr/bin/cmp -s "$GAMMA_PACK_ROOT/plan_tree.json" "$ANALYSIS_ROOT/prospective/plan_tree.json"
/usr/bin/cmp -s "$GAMMA_PACK_ROOT/analysis_manifest_v3.json" "$ANALYSIS_ROOT/prospective/analysis_manifest_v3.json"
"$PY" scripts/build_bracket_binding.py \
  --custody-root "$ANALYSIS_ROOT" --session-id "$BRACKET_SESSION_ID" \
  --window-id "$WINDOW_ID" --plan-id "$PLAN_ID" --plan-sha256 "$PLAN_SHA256" \
  --frozen-plan "$ANALYSIS_ROOT/prospective/calibration_plan.json" \
  --evidence-root-id "$EVIDENCE_ROOT_ID" --runs-root "$RUNS_ROOT" \
  --calibration-ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --output "$RUNS_ROOT/bracket-binding.json" \
  > "$TRANSCRIPT_ROOT/bracket-binding.json"
```

F1 first copies exact generator bytes (never edits) to the analysis root and
asserts equality: gamma `calibration_plan.json`, `plan_tree.json`, and
`analysis_manifest_v3.json` → `$ANALYSIS_ROOT/prospective/`. The binding CLI
requires its frozen plan to exist under custody before the builder starts
(`build_bracket_binding.py:420-440`).

**F2 — emit exactly one whole-window verdict, consuming F1.
BLOCKED-UNTIL-CURE B10.** CWD:
`$SMOKE_CHECKOUT`. Timing: <1 min. Expected artifact:
`$ANALYSIS_ROOT/whole-window-verdict.json`, `status: passed`. Expected refusal
if the supplied binding is missing or outside `$RUNS_ROOT`:
`calibration_bracket_binding_invalid`. **B10 — current whole-window and claim
consumers have no authenticated quarantine-ledger route.** Add
`--calibration-ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN"` to
both parsers and commands, or derive the exact authenticated ledger from
finalized custody. F2 and G2 remain **BLOCKED-UNTIL-CURE** until that route
exists. The output flag is current at `run_campaign.py:741-760`; the two ledger
flags below are future cure flags.

```sh
"$PY" scripts/run_campaign.py --whole-window-verdict \
  --runs-dir "$RUNS_ROOT" --log "$RUNS_ROOT/campaign_log.jsonl" \
  --campaign-policy "$POLICY" \
  --calibration-ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --neg8-drift-bound "$BOUND_RUNS_ROOT/neg8-drift-bound.json" \
  --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
  --whole-window-verdict-output "$ANALYSIS_ROOT/whole-window-verdict.json" \
  > "$TRANSCRIPT_ROOT/whole-window-verdict.stdout" \
  2> "$TRANSCRIPT_ROOT/whole-window-verdict.stderr"
/usr/bin/jq -e '.status == "passed"' "$ANALYSIS_ROOT/whole-window-verdict.json"
```

**F3 — extract both decode floor components.** CWD: `$SMOKE_CHECKOUT`.
Timing: 1–2 min. Expected artifacts: two extraction reports with
`all_cells_extractable: true`. Expected refusal if F2 or a bundle is absent:
nonzero exit with per-cell `idle_admission_refusals`/membership refusals. Flags
are `extract_detection_floors.py:48-99`.

```sh
export WHOLE_WINDOW_BASIS_SHA256="$(/usr/bin/jq -er '.evaluation_basis.sha256' "$ANALYSIS_ROOT/whole-window-verdict.json")"
export FLOOR_15_SPEC="$PACK_OUTPUT_ROOT/$(jq -er '.downstream_contract.extraction_spec.path' "$FLOOR_15_PACK_ROOT/plan_tree.json")"
export FLOOR_7_SPEC="$PACK_OUTPUT_ROOT/$(jq -er '.downstream_contract.extraction_spec.path' "$FLOOR_7_PACK_ROOT/plan_tree.json")"
test "$(shasum -a 256 "$FLOOR_15_SPEC" | awk '{print $1}')" = "$(jq -er '.downstream_contract.extraction_spec.sha256' "$FLOOR_15_PACK_ROOT/plan_tree.json")"
test "$(shasum -a 256 "$FLOOR_7_SPEC" | awk '{print $1}')" = "$(jq -er '.downstream_contract.extraction_spec.sha256' "$FLOOR_7_PACK_ROOT/plan_tree.json")"
"$PY" scripts/extract_detection_floors.py --runs-root "$RUNS_ROOT" \
  --spec "$FLOOR_15_SPEC" \
  --out "$ANALYSIS_ROOT/floor/floor-15-extraction.json" \
  --evaluation-basis-sha256 "$WHOLE_WINDOW_BASIS_SHA256" \
  --consumption-semantics-id d078_minted_envelopes_v1 --hash-bundles
"$PY" scripts/extract_detection_floors.py --runs-root "$RUNS_ROOT" \
  --spec "$FLOOR_7_SPEC" \
  --out "$ANALYSIS_ROOT/floor/floor-7-extraction.json" \
  --evaluation-basis-sha256 "$WHOLE_WINDOW_BASIS_SHA256" \
  --consumption-semantics-id d078_minted_envelopes_v1 --hash-bundles
```

If the cured generators retain another filename for the extraction spec, the
cure must publish that exact relative path in the plan tree; replace the two
paths only from those authenticated bytes, never by directory search.

**F4 — mint the aggregate floor. BLOCKED-UNTIL-CURE B7.** CWD:
`$SMOKE_CHECKOUT`. Timing: 1–2 min. Expected artifacts:
`$ANALYSIS_ROOT/floor/aggregate-floor.json` and the single-count statement.
Expected refusal if the pinset/input manifest is absent or mismatched, or if
actual Git HEAD differs from `$MINT_HEAD`: `MintError`, nonzero, no artifact.

```sh
export FLOOR_PINSET="$ANALYSIS_ROOT/prospective/floor-pinset-v2.json"
export FLOOR_PINSET_SHA256="$(shasum -a 256 "$FLOOR_PINSET" | awk '{print $1}')"
export FLOOR_INPUT_MANIFEST="$ANALYSIS_ROOT/prospective/floor-mint-inputs-v2.json"
"$PY" scripts/mint_floor_artifact_generalized.py \
  --pinset "$FLOOR_PINSET" --pinset-sha256 "$FLOOR_PINSET_SHA256" \
  --v2-input-manifest "$FLOOR_INPUT_MANIFEST" \
  --out "$ANALYSIS_ROOT/floor/aggregate-floor.json" \
  --single-count-out "$ANALYSIS_ROOT/floor/single-count-statement.json" \
  --project-commit "$MINT_HEAD" --project-tree-state clean \
  > "$TRANSCRIPT_ROOT/floor-mint.stdout" 2> "$TRANSCRIPT_ROOT/floor-mint.stderr"
```

### Phase G — H6 finalization and claim edge

**G1 — finalize once under the DISTINCT ANALYSIS ROOT.** CWD:
`$SMOKE_CHECKOUT`. Timing: <1 min. Expected artifact:
`$ANALYSIS_ROOT/am-<sha>.finalized.json`; stdout JSON has
`status: FINALIZED`. Expected refusal if F1, F2, or F4 was skipped:
`analysis_finalization_input_unreadable`, exit 2. Every flag is required at
`finalize_analysis_manifest.py:30-38`.

```sh
"$PY" scripts/finalize_analysis_manifest.py \
  --prospective-manifest "$ANALYSIS_ROOT/prospective/analysis_manifest_v3.json" \
  --plan-tree "$ANALYSIS_ROOT/prospective/plan_tree.json" \
  --custody-root "$ANALYSIS_ROOT" --runs-root "$RUNS_ROOT" \
  --whole-window-verdict "$ANALYSIS_ROOT/whole-window-verdict.json" \
  --bracket-binding "$RUNS_ROOT/bracket-binding.json" \
  --calibration-ledger "$CALIBRATION_LEDGER" \
  --aggregate-floor-artifact "$ANALYSIS_ROOT/floor/aggregate-floor.json" \
  --output-dir "$ANALYSIS_ROOT" > "$TRANSCRIPT_ROOT/finalize.json"
export FINALIZED_MANIFEST="$(/usr/bin/jq -er '.output' "$TRANSCRIPT_ROOT/finalize.json")"
```

**G2 — run the claim edge. BLOCKED-UNTIL-CURE B10.** CWD: `$SMOKE_CHECKOUT`.
Timing: <1 min. Expected artifact: `$ANALYSIS_ROOT/claim_verdicts.json`. If G1
is skipped, no finalized path exists and the manifest input is unreadable;
this command does not pass a prospective manifest and therefore cannot emit
`analysis_manifest_prospective_not_consumable`. If a contract join fails, the
claim artifact contains CONTRACT reasons and the PASS helper below fails.
Current flags are verified by `python -m joulewise analyze-claims --help`; the
two ledger flags below are future B10 cure flags.

```sh
export FLOOR_15_EVIDENCE_ROOT_ID="$(/usr/bin/jq -er '.window_identity.evidence_root_id' "$FLOOR_15_PACK_ROOT/plan_tree.json")"
export FLOOR_7_EVIDENCE_ROOT_ID="$(/usr/bin/jq -er '.window_identity.evidence_root_id' "$FLOOR_7_PACK_ROOT/plan_tree.json")"
"$PY" -m joulewise analyze-claims \
  --analysis-manifest "$FINALIZED_MANIFEST" --runs-root "$RUNS_ROOT" \
  --evidence-root "$FLOOR_15_EVIDENCE_ROOT_ID=$RUNS_ROOT" \
  --evidence-root "$FLOOR_7_EVIDENCE_ROOT_ID=$RUNS_ROOT" \
  --calibration-ledger "$CALIBRATION_LEDGER" --head-pin "$LEDGER_HEAD_PIN" \
  --floor-artifact "$ANALYSIS_ROOT/floor/aggregate-floor.json" \
  --output "$ANALYSIS_ROOT/claim_verdicts.json"
```

### Phase H — assertions, quarantine closure, and preservation

Run every assertion below. Then record `git status`; do not commit, register,
marker-sign, move into production roots, or delete any bundle.

## Runnable acceptance assertions

All commands run from `$SMOKE_CHECKOUT` with the variables above.

**S11 A1 — science manifests carry the gamma manifest identity and exact
SHA.** Expected output: `PASS S11-A1 <n>` with `n >= 1`.

```sh
"$PY" - "$GAMMA_PACK_ROOT/analysis_manifest_v3.json" "$RUNS_ROOT" <<'PY'
import hashlib,json,pathlib,sys
mp=pathlib.Path(sys.argv[1]); root=pathlib.Path(sys.argv[2]); raw=mp.read_bytes(); m=json.loads(raw)
rows=[]
for p in sorted((root/'campaign_manifests').glob('*.json')):
    v=json.loads(p.read_text())
    if v.get('analysis_manifest_id') is not None: rows.append((p,v))
assert rows
for p,v in rows:
    assert v['analysis_manifest_id'] == m['manifest_id'], p
    assert v['analysis_manifest_sha256'] == hashlib.sha256(raw).hexdigest(), p
print('PASS S11-A1',len(rows))
PY
```

**S11 A2 — the cooldown join is non-empty and covers collected gamma
bundles.** Expected output: `PASS S11-A2 <n>`.

```sh
"$PY" - "$RUNS_ROOT" "$FINALIZED_MANIFEST" <<'PY'
import json,pathlib,sys
from joulewise.analysis_engine.inputs import campaign_cooldown_evidence
root=pathlib.Path(sys.argv[1]); final=json.loads(pathlib.Path(sys.argv[2]).read_text())
mid=final['lineage']['collection_manifest_id']; joined=campaign_cooldown_evidence(root,mid)
assert joined
expected=set()
for p in (root/'campaign_manifests').glob('*.json'):
    v=json.loads(p.read_text())
    if v.get('analysis_manifest_id')==mid:
        for member in v['members']: expected.update(member.get('bundle_ids',[]))
assert expected and expected <= set(joined)
print('PASS S11-A2',len(joined))
PY
```

**S11 A3 — no bundle has `campaign_cooldown_evidence_missing`.** Expected
output: `PASS S11-A3`.

```sh
/usr/bin/jq -e '[..|objects|.reason_codes? // empty|.[]?] | index("campaign_cooldown_evidence_missing") == null' "$ANALYSIS_ROOT/claim_verdicts.json" >/dev/null && echo 'PASS S11-A3'
```

**S11 A4 — every applicable null-bound stage still collects.** This is **not
vacuous** here: NEG-8, the start/midpoint/end references, and both floor packs
are enumerated. Expected output: `PASS S11-A4 6`.

```sh
"$PY" - "$RUNS_ROOT" "$BOUND_RUNS_ROOT" "$SMOKE_CHECKOUT" "$FLOOR_15_PACK_ROOT" "$FLOOR_7_PACK_ROOT" <<'PY'
import json,pathlib,sys
runs,bound,checkout,floor15,floor7=map(pathlib.Path,sys.argv[1:])
expected={
    str((checkout/'configs/campaigns/neg8_reference_corpus').resolve()): bound,
    str((checkout/'configs/campaigns/window_references/start_triplet').resolve()): runs,
    str((checkout/'configs/campaigns/window_references/midpoint').resolve()): runs,
    str((checkout/'configs/campaigns/window_references/end_triplet').resolve()): runs,
    str(floor15.resolve()): runs,
    str(floor7.resolve()): runs,
}
seen=set()
for identity,root in expected.items():
    matches=[]
    for p in (root/'campaign_manifests').glob('*.json'):
        v=json.loads(p.read_text())
        if v.get('analysis_manifest_id') is None and str(pathlib.Path(v['config_dir']).resolve())==identity:
            assert v.get('members'), p
            assert any(m.get('execution') in {'invoked','existing'} for m in v['members']), p
            matches.append(p)
    assert matches, identity
    seen.add(identity)
assert seen==set(expected)
print('PASS S11-A4',len(seen))
PY
```

**S11 A5 — gamma manifest ID is self-derived.** Expected output:
`PASS S11-A5`.

```sh
"$PY" - "$GAMMA_PACK_ROOT/analysis_manifest_v3.json" <<'PY'
import json,pathlib,re,sys
from joulewise.analysis_manifest_v3 import calculate_manifest_id
v=json.loads(pathlib.Path(sys.argv[1]).read_text())
assert re.fullmatch(r'am-[0-9a-f]{64}',v['manifest_id'])
assert v['manifest_id']==calculate_manifest_id(v)
print('PASS S11-A5')
PY
```

**F-5.1 — cooldown raw JSONL is re-derived and selected by collection ID.**
Expected output: `PASS F5-cooldown-raw`. The public join already calls
`_verified_cooldown_raw_artifact`, which hashes and re-derives disposition at
`inputs.py:1982-2034`; this assertion requires every selected row to carry the
verified descriptor.

```sh
"$PY" - "$RUNS_ROOT" "$FINALIZED_MANIFEST" <<'PY'
import json,pathlib,sys
from joulewise.analysis_engine.inputs import campaign_cooldown_evidence
root=pathlib.Path(sys.argv[1]); f=json.loads(pathlib.Path(sys.argv[2]).read_text())
j=campaign_cooldown_evidence(root,f['lineage']['collection_manifest_id'])
assert j and all(x.get('raw_artifact') for x in j.values())
print('PASS F5-cooldown-raw')
PY
```

**F-5.2 — whole-window reasons attach to every bundle.** On the required
`status: passed` smoke, the reason set is empty, so the attachment half is
**vacuous by design**; the important non-vacuous checks are status passed and
that every claimed bundle is in the authenticated evaluation basis. Expected
output: `PASS F5-whole-window 0`.

```sh
"$PY" - "$ANALYSIS_ROOT/whole-window-verdict.json" "$ANALYSIS_ROOT/claim_verdicts.json" <<'PY'
import json,pathlib,sys
v=json.loads(pathlib.Path(sys.argv[1]).read_text()); c=json.loads(pathlib.Path(sys.argv[2]).read_text())
assert v['status']=='passed'; reasons=set(v.get('reason_codes',[])); assert not reasons
basis={x['bundle_id'] for x in v['evaluation_basis']['members']}
seen={bid for ctr in c['contrasts']
      for bid in ctr['bundle_blocks']['included_bundle_ids']}
assert seen and seen <= basis
print('PASS F5-whole-window',len(reasons))
PY
```

**F-5.3 — runs-root equality.** Expected output: `PASS F5-runs-root`.

```sh
/usr/bin/jq -er --arg root "$RUNS_ROOT" '.runs_root == $root' "$RUNS_ROOT/bracket-binding.json" >/dev/null && echo 'PASS F5-runs-root'
```

**F-5.4 — supersession scan excludes conflicts.** Expected output:
`PASS F5-supersession-clean`.

```sh
"$PY" - "$RUNS_ROOT" "$WHOLE_WINDOW_BASIS_SHA256" <<'PY'
import pathlib,sys
from joulewise.analysis_engine.inputs import supersession_visibility_scan
r=supersession_visibility_scan(pathlib.Path(sys.argv[1]),scope='analysis_corpus',evidence_root_id=None,authenticated_basis={'kind':'whole_window_evaluation_basis_sha256','sha256':sys.argv[2]})
assert r['status']=='clean',r
print('PASS F5-supersession-clean')
PY
```

**DATA-only predicate.** Expected output: `PASS DATA-only`.

```sh
"$PY" - "$ANALYSIS_ROOT/claim_verdicts.json" <<'PY'
import json,pathlib,sys
from joulewise.analysis_engine.reason_kinds import assert_data_reason_only
artifact=json.loads(pathlib.Path(sys.argv[1]).read_text())
assert_data_reason_only(artifact,expect_lock=None)
print('PASS DATA-only')
PY
```

**Quarantine, no marker, registry untouched, checkout clean.** Expected output:
four PASS lines. The registry check is byte equality, not absence of a textual
pack ID alone.

```sh
test -z "$(/usr/bin/find "$SMOKE_ROOT" -name 'd117_family_publication_v4.json' -o -name '*family_marker*')" && echo 'PASS no marker'
test -z "$(rg -n 'd117_.*_v9' "$SMOKE_CHECKOUT/configs/arm_readiness/d117_row_registry_v2.json" || true)" && echo 'PASS registry has no v9 row'
(cd "$TRANSCRIPT_ROOT" && shasum -a 256 -c registry-before.sha256) >/dev/null && echo 'PASS registry bytes unchanged'
test -z "$(git -C "$SMOKE_CHECKOUT" status --porcelain=v1 --untracked-files=all)" && echo 'PASS checkout clean'
```

## ABORT — any refusal, no retry

1. Stop the chain. Do not run the skipped successor, do not edit a receipt,
   reuse a create-only name, select another calibration, or re-arm-and-hope.
2. Preserve the exact stdout, stderr, exit code, and invoked argv. Copy them to
   `$REFUSAL_ROOT/<UTC-step>/`; copy (never move) the arm receipt and sidecar,
   launch manifest, any launch consumption/lifecycle receipts, T-0 captures,
   calibration ledger/head pin, binding/verdict/finalizer outputs already
   present, and both `git status --short --branch` and
   `git status --porcelain=v1 --untracked-files=all`.
3. Record whether a create-only freeze/arm/output file now exists. Its existence
   governs whether the slot is spent; never infer that from prose.
4. Report immediately to Ed and the Fable lead with: reviewed head, phase/step,
   exact argv, exit code, refusal reason code, first stderr line, paths and
   SHA-256s of all receipts, boot-session ID, and whether any capture bytes were
   written. Classify the attempt `ABORTED_NON_CLAIM_BEARING`.
5. Keep every bundle immutable. Do not delete `/Users/edr/JouleWise-smoke` and
   do not copy anything into production runs, configs, marker, registry, floor,
   or claim roots.

**Standing escalation trigger:** two consecutive rounds with the same signature
(same defect class, missed call site, or failed formulation) trigger a consult;
there is no round three (`real-transaction-runbook.md:1617-1626`).

## Post-run — preserve as the TIER2 corpus

After every assertion passes, make the tree read-only only through the ruled
custody mechanism; do not improvise filesystem flags. Preserve exact bytes for:

- all three generated pack roots, generators, plans, plan trees, order and
  analysis manifests, U11 receipts, and readiness-freeze receipts;
- both runs roots in full, including raw powermetrics, configs, metadata,
  summaries, campaign manifests/logs, cooldown raw JSONL, launch lineage, and
  all reference, bound, floor and contrast bundles;
- pre/post protocol-v3 calibration custody, ledger, head pin, bracket binding,
  whole-window verdict, extraction reports, v2 mint pinset/input manifest,
  aggregate floor, finalized manifest, and claim verdicts;
- every T-0 capture, arm/verify/consumption/lifecycle receipt, frozen
  `window.env`, `window-chain.zsh` and their SHA-256s;
- all stdout/stderr transcripts, pre/post `git status`, reviewed head, registry
  before/after digest, assertion outputs, and the PASS declaration.

These immutable live bytes become the input corpus for
`PIPELINE-SMOKE-TIER2-01`. They remain quarantined and claim-ineligible; replay
uses copies or read-only access and never rewrites this source.
