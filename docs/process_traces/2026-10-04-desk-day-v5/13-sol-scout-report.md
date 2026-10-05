```json
{
  "schema": "claude-codex-report/v1",
  "genre": "scout",
  "status": "findings",
  "completion": "complete",
  "summary": "Use a committed portable pin bundle; repair contrast replay and resolve floor compatibility before clone proof; register pack rehearsal then G2-b before any claim-bearing v5 transaction.",
  "workspace": {
    "base_requested": "8fa002f7",
    "base_mode": "exact",
    "head_start": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "head_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "upstream_end": "8fa002f77db7af1e261a30e3787e38af2ab5e946",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "rows": [
      {"id": "V5-DESK-DAY-01", "action": "wait_for", "wait_for": "Gated harvest-authenticating issuer, contrast authentication replay repair, and floor pin compatibility disposition"},
      {"id": "PACK-ROOT-SUCCESSOR-V5-01", "action": "wait_for", "wait_for": "Desk-day generation, evidence authoring and clean-clone A5 refusal proof"},
      {"id": "FLOOR-V5-DRIFT-REPIN-01", "action": "needs_ruling", "wait_for": "Resolve post-freeze source repinning against frozen pack immutability"},
      {"id": "RENDERER-V5-SUCCESSOR-01", "action": "start_now", "wait_for": ""},
      {"id": "CLONE-READINESS-01", "action": "start_now", "wait_for": "Preparation only; final deployment waits for reviewed transaction head and live prerequisites"},
      {"id": "NIGHT-PACK-REHEARSAL-01", "action": "wait_for", "wait_for": "Desk proof, prerequisite rehearsal closure, frozen pack-night plan and sealed live registration"},
      {"id": "V5-G2B-SHAKEDOWN-01", "action": "wait_for", "wait_for": "Harvested pack rehearsal, sealed registration and governed unattended first-block stop"},
      {"id": "L10-A-G2B-CONTRACT-PREFIX-01", "action": "wait_for", "wait_for": "Immutable real G2-b root"},
      {"id": "V5-LAUNCH-REALIZATION-RECHECK-01", "action": "start_now", "wait_for": ""},
      {"id": "V5-TRANSACTION-01", "action": "do_not_start", "wait_for": "G2-b, L10-A, launch recheck, liveness closure or ruling, battery-compliant freeze, directive 416 audit, and CAMPAIGN_TRANSACTION authorization"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\nfrom joulewise import arm_readiness_evidence as e\nraw=Path('configs/campaigns/d117_contrast_v5/generate_configs.py').read_bytes()\ntry:\n    e._generator_invocation('generate_configs.py',raw,kind='PACK_AUTHENTICATION',preserve_current_frozen_bytes=False)\nexcept e.EvidenceAuthoringError as exc:\n    assert 'flagless generator' in str(exc)\n    print('CONFIRMED contrast authentication rejects flagless generator')\nelse:\n    raise AssertionError('unexpected authentication acceptance')\nPY\n git status --short --branch\n git rev-parse HEAD main origin/main",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CONFIRMED contrast authentication rejects flagless generator",
          "## HEAD (no branch)",
          "8fa002f77db7af1e261a30e3787e38af2ab5e946",
          "8fa002f77db7af1e261a30e3787e38af2ab5e946",
          "8fa002f77db7af1e261a30e3787e38af2ab5e946"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CONFIRMED contrast authentication rejects flagless generator[\\s\\S]*## HEAD \\(no branch\\)[\\s\\S]*8fa002f77db7af1e261a30e3787e38af2ab5e946"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Main's contrast generator is rejected by generic PACK_AUTHENTICATION as a flagless generator with a preservation mechanism; its required model and panel CLI arguments are also absent from generic replay.",
      "needs": "Land a reviewed self-contained replay interface before evidence authoring or freeze."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "A69 schedules generator source-byte/domain repinning after freeze, while the pack digest covers committed generator bytes. Battery S3 also contains an explicit stop-and-ruling condition before committing readiness sources.",
      "needs": "Resolve sequencing before the terminal freeze; preserve historical frozen packs."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "Both floor generators enforce a fixed PREFILL_LENGTH and the selected-branch selection-record schema. This scout deliberately did not inspect the selected coordinate.",
      "needs": "Check compatibility privately after issuance; repair incompatible validators prospectively before generation."
    },
    {
      "id": "F4",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Queue/kernel still contain pre-SELECT desk dependencies and older calibration-issuance state; generators still bind the older successor acceptance despite the issued 25G83 r2 default.",
      "needs": "Reconcile records and acceptance pins before claim-bearing freeze; do not substitute live ledger head 402 for the acceptance cutoff."
    },
    {
      "id": "F5",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was read-only inspection. No selection record or measured counts were opened, and no generator, clone proof, suite, arm, installation or hardware capture was executed.",
      "needs": "Lead executes the plan below in an authorized writable checkout and custodies its results."
    }
  ]
}
```

## 1. The pin’s home

Use the documented, **committed repository bundle**:

```text
configs/campaigns/d117_contrast_v5/prefill_pin/prefill-prompt-pin.json
configs/campaigns/d117_contrast_v5/prefill_pin/<selection_record.path>
configs/campaigns/d117_contrast_v5/prefill_pin/<prompt_ladder.path>
```

The runsheet explicitly copies the bundle there and passes that repository-relative pin path to contrast generation. Preserve the pin’s relative bundle paths; do not flatten or rename the copies independently. Evidence: `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:639–655,661–674`.

There is **no loader rule requiring this one directory**. The initial contrast loader can read a pin elsewhere, provided its referenced bundle files resolve beneath the pin’s parent and authenticate. However, an external absolute path recorded through `PREFILL_PIN_FILE_ARGUMENT` is unsuitable for portable committed-tree replay. Evidence authoring requires committed artifacts and reproduces the generator in an archived repository tree. The documented repository home therefore resolves the portability requirement; an outside-root issuance location is only an intermediate location. Evidence: `configs/campaigns/d117_contrast_v5/generate_configs.py:810–834,1128–1132`; `joulewise/arm_readiness_evidence.py:255–259,1655–1701,1786–1809`.

The floors additionally emit self-contained copies under their own pack roots:

```text
<payload pack>/prefill_pin/prefill_prompt_pin.json
<payload pack>/prefill_pin/<selection reference>
<payload pack>/prefill_pin/<ladder reference>
```

Their pin filename uses underscores. Contrast’s closed generated inventory does not perform an equivalent bundle copy, so its repository source bundle must remain committed and replayable. Evidence: both floor generators, `generate_configs.py:169,2563–2576,3099–3116`; contrast generator, `:1270–1297`.

The existing authority constants must agree with the issued v2 pin:

- `PREFILL_RULING_TRACE_PATH`: `docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md`.
- `PREFILL_RULING_TRACE_PATHS`: that path followed by `docs/process_traces/2026-09-01-fresh-model-review/16b-RULING-g2a-producers.md`.
- `PREFILL_LADDER_PROMPT_TOKENS`, the small-model/member and interval threshold constants, `PREFILL_MIN_PHASE_SAMPLES_PINNED`, `PREFILL_SAMPLE_COUNT_MARGIN_FLOOR`, `PREFILL_SELECTION_EXPRESSION`, and `PREFILL_EXHAUSTED_LADDER_BRANCH`.

These protocol constants agree across the three generators on this main head; the ruling files exist. Their equality checks are executable validation requirements, including agreement with the reducer minimum and the ordered authority-path list. Evidence: contrast generator, `:94–133,746–791`; both floor generators, `:79–114,1018–1054`.

**Issuance remains gated on the parallel issuer PR.** The latest brief forbids issuance before harvest authentication lands and requires reading the archive rather than the live runs root. The old Phase D issuance command is superseded by that obligation and the new CLI described in this assignment. Evidence: `docs/process_traces/2026-10-04-activation-df31cb27/40-desk-day-seat-brief.md:24–30`.

For the new `--ruling-trace` argument, the presently accepted primary trace is the ratification path above. If the parallel implementation intends another authority trace, it must coordinate that change with all three validators; merely substituting a block-3 trace will fail the existing equality contract. Evidence: contrast generator, `:106–114,778–791`; floor generators, `:1040–1054`.

## 2. Pack generation

The registry’s exact identities are:

| Profile | Pack ID/output subtree | Generator source |
|---|---|---|
| ALPHA | `d117_floor_qwen3-1p7b_v5` | Same-named subtree |
| BETA | `d117_floor_qwen3-8b_v5` | Same-named subtree |
| GAMMA | `d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` | `d117_contrast_v5` |

Evidence: `configs/arm_readiness/d117_row_registry_v2.json:532–535`; contrast generator, `:1095–1102`. The GAMMA source umbrella is not its emitted pack root.

The following are commands for the lead’s writable checkout, **after the prerequisites below land**. The coordinate is taken privately from the authenticated issued pin; it is never printed.

```sh
cd "$REPO"
PY="$REPO/.venv/bin/python"
HARVEST_ARCHIVE=/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261004T1305Z-r2
PIN_REL=configs/campaigns/d117_contrast_v5/prefill_pin/prefill-prompt-pin.json

"$PY" scripts/issue_g2a_prefill_prompt_pin.py \
  --harvest "$HARVEST_ARCHIVE/harvest.json" \
  --registration configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md \
  --ruling-trace docs/process_traces/2026-08-30-prefill-margin-coldgate/03-MAGISTRATE-RATIFICATION.md \
  --output "$PIN_REL"

PREFILL_LENGTH="$(/usr/bin/jq -er '.prefill_length' "$PIN_REL")"

"$PY" configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py \
  --output-root "$REPO" \
  --prefill-prompt-pin "$PIN_REL" \
  --no-preserve-current-frozen-bytes

"$PY" configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py \
  --output-root "$REPO" \
  --prefill-prompt-pin "$PIN_REL" \
  --no-preserve-current-frozen-bytes

"$PY" configs/campaigns/d117_contrast_v5/generate_configs.py \
  --output-root "$REPO" \
  --panel configs/model_panels/qwen3_4bit.json \
  --model-a qwen3-1p7b \
  --model-b qwen3-8b \
  --decode-workload configs/workloads/real_prompts_v1.json \
  --prefill-length "$PREFILL_LENGTH" \
  --prefill-prompt-pin "$PIN_REL"
```

The first command is the **post-PR interface specified by the assignment**, not an interface available on this main head. The generation interfaces are evidenced by contrast `generate_configs.py:3533–3562`, both floor generators `:3252–3304`, and the Phase D command at `SHAKEDOWN-G2-RUNSHEET.md:661–674`.

Repeat each generation command with `--check` before committing its output. The floor panel and model identities are embedded inputs, rather than CLI arguments: `configs/model_panels/qwen3_4bit.json`, respectively `qwen3-1p7b` and `qwen3-8b`, plus `configs/workloads/real_prompts_v1.json`. Evidence: both floor generators, `:158–169,3252–3304`.

Each floor writes its embedded generator, README, calibration plan and sidecar, plan tree and sidecar, order/configuration manifests, producer/extraction contracts, workload-family candidates, prompt manifest, staged member configurations, and copied pin bundle. GAMMA writes its corresponding contrast inventory, prospective analysis manifest and consumer declarations. These commands change the declared files beneath the three output subtrees and add the source bundle beneath `d117_contrast_v5/prefill_pin`; they do not author readiness or freeze receipts. Evidence: floor generators, `:2553–2576,3085–3140`; contrast generator, `:1270–1297,3057–3066`.

Two current code conditions require attention:

1. **Floor compatibility is unresolved without opening the coordinate.** Both floors require the pin’s length and selected-branch record to equal their fixed `PREFILL_LENGTH`; there is no length CLI override. Privately check compatibility after issuance. If it fails, change the prospective producers through the code gate; do not edit the selection record. Evidence: both floor generators, `:78,1018–1038,1105–1129,3252–3274`.
2. **Contrast cannot presently pass generic generator authentication.** The authentication helper rejects its preservation mechanism without the required boolean preservation flag. Even beyond that rejection, generic replay supplies `--check`, not its required panel/model/pin arguments. The emitted generator retains source bytes rather than baking a self-contained invocation. This was reproduced read-only. Evidence: `joulewise/arm_readiness_evidence.py:1180–1212,1340–1368`; contrast generator, `:402–414,3533–3550`.

The generators also still bind the older successor acceptance. Main now has an issued, claim-eligible 25G83 r2 acceptance and a recorded live-default move. Repin the prospective packs to the intended current issuance before terminal claim-capable freeze. **Do not replace the acceptance-cutoff digest with ledger head 402:** the floor check compares its literal to the acceptance cutoff and permits a later live head. Evidence: contrast generator, `:447–456`; floor generators, `:201–213,2477–2517`; `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json:8–24`; `RUN_STATE.md:89`.

## Scheduling matrix

| Row/lane | action | wait_for | collision surface |
|---|---|---|---|
| Harvest-authenticating issuer | wait_for | Parallel gated PR | Selection/registration authentication; true pin-generation prerequisite |
| Contrast replay repair | start_now | Reviewed implementation | Emitted generator identity and generic authentication; true evidence/freeze prerequisite |
| Floor coordinate compatibility | wait_for | Issued pin | Fixed producer coordinate; generation prerequisite if incompatible |
| A196 `PACK-ROOT-SUCCESSOR-V5-01` | wait_for | Desk generation and evidence | Same pack roots; desk-day work closes it, rather than a separate prerequisite PR |
| A69 `FLOOR-V5-DRIFT-REPIN-01` | needs_ruling | Terminal source/domain bytes | Queue orders repinning after freeze; changing frozen generator bytes changes pack identity |
| A71 `RENDERER-V5-SUCCESSOR-01` | start_now | G2-a selection dependency is satisfied | Successor paper renderer; not generation, freeze or launch |
| A153 `D166-PROMPT0-01` | wait_for | Census, supersession and regenerated proof | Contrast prompt-derived identities; implementation already has fixed prompt 0 |
| A72 `D165-E2E-01` | wait_for | Its renderer/result-flow dependencies | Later result production; not pack generation |
| E166 `CLONE-READINESS-01` | start_now | Preparation now; final reviewed head later | Production ledger/custody and isolated live rehearsal checkout; not the disposable desk clone |
| `RUN-CONFIG-NORMALIZED-PIN-01` / attach-guard tests | start_now | Block 3 has ended | Independent post-block code/test lanes; not automatically generation prerequisites |

Evidence: `TASK_QUEUE.md:696,757–761,807,832`; `docs/process/state_kernel.json:2764,2846,3767–3799,6940–6968,8185–8227,10298–10349`; contrast generator, `:135–157,680–689`; latest desk brief, `:32–35`.

A196 closes only with usable committed pack roots and the specified clean-clone A5 refusal—not directory creation alone. Its acceptance names `evidence_author_t0_clock_attestation_missing`, rather than registry mismatch or unreadable pack. Evidence: `TASK_QUEUE.md:832`.

A69’s sequencing requires a lead disposition: derive and settle mutable source/domain pins before final freeze, or adopt a non-rewriting verification approach consistent with its acceptance. Committed generator files are in the pack digest; editing them after freeze cannot preserve that freeze’s identity. Evidence: `docs/process/state_kernel.json:3770–3772,3789–3799`; `docs/phase_2/window_runbook.md:340–358`.

## 3. Re-proof in a throwaway clone

This is an **`[AGENT]` desk proof**. It can establish freeze, conditional admission, and receipt semantics without campaign bundles. It cannot establish an all-green live GO under the requested constraints. S0 expressly allows a governed non-null refusal receipt and canonical verification refusal when live prerequisites are absent; it forbids fabricated T0 evidence. Evidence: `docs/process_traces/2026-08-22-t20/s0-runsheet-r4.md:2477–2480`.

Use estate-12 as the procedure template, incorporating the current CLI and predecessor corrections below. Its clone must use the exact reviewed full commit and authentic repository objects. Evidence: `docs/process_traces/2026-08-30-t28-estate11/estate-12-delta-template.md:24–39,73–99`.

```sh
git clone --no-local "$SOURCE_REPOSITORY" "$CLONE"
git -C "$CLONE" checkout --detach "$BASE"
cd "$CLONE"

"$PY" scripts/derive_estate_anchors.py "$CLONE" \
  --output "$CUSTODY/estate-12-anchor-map.json"
```

Set the exact pack/predecessor arrays:

```sh
PACKS=(
  configs/campaigns/d117_floor_qwen3-1p7b_v5
  configs/campaigns/d117_floor_qwen3-8b_v5
  configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5
)
PREDS=(
  configs/campaigns/d117_floor_qwen25_1p5b_v3
  configs/campaigns/d117_floor_qwen25_7b_v3
  configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3
)
```

These are the ruled non-adjacent mappings. The expected receipt is **`freeze-0004`**, despite the `_v5` suffix. Evidence: `joulewise/arm_readiness.py:80–85`; battery S3 ruling, `docs/process_traces/2026-09-26-activation-6bec2aa6/40-bfgs-consult/50-coldgate/30-addendum/21-coldgate-fable-addendum-ruling.md:125`.

The executable order is:

1. **Identity projection and generation checks.** Re-run the generation checks from §2 in the clone. Freeze each actual identity projection and commit those changes before common-head readiness authoring:

   ```sh
   for pack in "${PACKS[@]}"; do
     "$PY" scripts/project_identity_pins.py freeze "$CLONE/$pack"
   done
   ```

   This uses real runtime/model/tokenizer identity inputs. A fixture substitution does not establish real identity. Evidence: `scripts/project_identity_pins.py:27–45`; estate template, `:125,193–251`.

2. **Pre-author tests and one common derivation head.**

   ```sh
   "$PY" -m unittest \
     tests.test_arm_readiness_schemas \
     tests.test_receipt_histsem \
     tests.test_mint_analysis_admission \
     tests.test_d117_contrast_v5_pack \
     tests.test_d117_floor_qwen3_v5_generate

   EVIDENCE_DERIVATION_HEAD="$(git rev-parse HEAD)"
   for pack in "${PACKS[@]}"; do
     "$PY" scripts/author_arm_readiness_evidence.py \
       --pack-root "$CLONE/$pack" \
       --measurement-checkout "$CLONE"
   done
   ```

   Assert complete declared receipt applicability, then make one local evidence commit. Do not commit between the author invocations. Evidence: estate template, `:245–259`; S0 runsheet, `:1794–1864`; current author CLI, `scripts/author_arm_readiness_evidence.py:34–35`.

3. **Sacrificial freeze first.** Clone the evidence commit into `$PREFLIGHT`; run the following there with `--measurement-checkout "$PREFLIGHT"`. Require clean PASS for every pack before touching the primary clone’s write-once freeze slots. Then run in the primary clone:

   ```sh
   for i in 1 2 3; do
     "$PY" scripts/generate_arm_readiness.py freeze \
       --pack-root "$CLONE/${PACKS[$i]}" \
       --measurement-checkout "$CLONE" \
       --predecessor-pack-root "$CLONE/${PREDS[$i]}"
   done
   ```

   Assert PASS, expected receipt identity and sidecars; make the local freeze commit. A terminal refused freeze poisons that clone’s slot: abandon it rather than rewriting the receipt. Evidence: S0 runsheet, `:1866–1934`; current CLI, `scripts/generate_arm_readiness.py:36–57`; runbook, `:284–302`.

4. **Historical receipt semantics and family marker.**

   ```sh
   FREEZE_COMMIT="$(git rev-parse HEAD)"
   SUCCESSOR_PINSET=configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json

   "$PY" scripts/build_v4_histsem_pinset.py \
     --repository "$CLONE" \
     --base-pinset "$BASE_PINSET" \
     --historical-head "$EVIDENCE_DERIVATION_HEAD" \
     --current-head "$FREEZE_COMMIT" \
     --pack-root "${PACKS[1]}" \
     --pack-root "${PACKS[2]}" \
     --pack-root "${PACKS[3]}" \
     --output "$CLONE/$SUCCESSOR_PINSET"

   "$PY" scripts/verify_receipt_histsem.py \
     --repository-root "$CLONE" \
     --pinset "$SUCCESSOR_PINSET" \
     --pack-root "${PACKS[1]}" \
     --pack-root "${PACKS[2]}" \
     --pack-root "${PACKS[3]}" \
     --output "$CUSTODY/receipt-histsem.json"

   "$PY" scripts/build_family_marker.py \
     --repository "$CLONE" --head "$FREEZE_COMMIT" \
     --pack-root "${PACKS[1]}" \
     --pack-root "${PACKS[2]}" \
     --pack-root "${PACKS[3]}" \
     --phase candidate --candidate-manifest "$MANIFEST" \
     --output "$CUSTODY/d117_family_publication_v5.json"

   "$PY" scripts/verify_family_marker.py \
     --repository "$CLONE" \
     --marker "$CUSTODY/d117_family_publication_v5.json" \
     --phase candidate --candidate-manifest "$MANIFEST" \
     --receipt-out "$CUSTODY/family-marker-verification.json"
   ```

   `$BASE_PINSET` and `$MANIFEST` are reviewed estate inputs, not guessed filenames or permissive manifests. The historical head precedes evidence authoring. Candidate proof does not constitute published-main proof. Evidence: S0 runsheet, `:1985–2034,2667`; `scripts/build_v4_histsem_pinset.py:27–35`; `scripts/verify_receipt_histsem.py:22–28`; marker CLIs, `scripts/build_family_marker.py:20–33`, `scripts/verify_family_marker.py:20–34`.

5. **Admission and receipt replay, confined to disposable custody.** Complete the reviewed S0 step-6 table/transcript pair. The current table filename is `d117_step6_confirmation_table_v5.json`; obtain `hC` from the independent confirmation, not by re-hashing the table and calling that confirmation. Evidence: `joulewise/arm_readiness.py:78–79`; D-176, `docs/decision_log.md:11520–11525`.

   Use the S0 arm context from `s0-runsheet-r4.md:2421–2428`, with every root beneath fresh `$CUSTODY/arm-context`, then:

   ```sh
   "$PY" scripts/generate_arm_readiness.py arm \
     --pack-root "$CLONE/$PACK" \
     --arm-context "$ARM_CONTEXT" \
     --window-custody-root "$CUSTODY/windows" \
     --expected-confirmation-digest "$hC"

   "$PY" scripts/generate_arm_readiness.py verify \
     --pack-root "$CLONE/$PACK" \
     --arm-receipt "$ARM_RECEIPT" \
     --expected-confirmation-digest "$hC"
   ```

   Preserve exact return codes/reasons. An early null receipt is not receipt proof. Execute the S0 falsifier cases in fresh clones, including path/namespace changes, dependency tampering, historical semantics and poisoned freeze behavior. Never consume a launch capability or run a window chain. Evidence: S0 runsheet, `:2431–2480,2848–4039`.

6. **A196’s separate dry gate.**

   ```sh
   "$PY" scripts/author_arm_evidence_t0.py \
     --pack-root "$CLONE/$PACK" \
     --custody-root "$CUSTODY/a5/$PROFILE"
   ```

   In the clean, deliberately unattested desk case, require the row’s named clock-attestation refusal. That is the proof that pack/profile resolution has advanced far enough—not a T0 PASS. Evidence: `scripts/author_arm_evidence_t0.py:25–27,55–61`; `TASK_QUEUE.md:832`.

No step above needs sudo, launchctl, powermetrics or a quiet measurement window. The optional readiness `dry-run` is also a bounded rehearsal, explicitly omitting live privilege, clock, machine, power and launch-consumption proof. It does not discharge those gates. Evidence: `docs/phase_2/window_runbook.md:367–392`; latest desk brief, `:41`.

The older estate template’s Ed-confirmation and unconditional all-green wording must be reconciled with D-171 delegation and S0’s conditional-admission rule. A real privileged-anchor positive control remains Ed-owned; it belongs to live rehearsal, not this clone proof. Evidence: estate template, `:249–282`; `docs/decision_log.md:10926–10947,11529`.

## 4. The next measurement block

## Critical path

```text
Authenticated issuer + compatible/replayable producers
    → portable pin bundle + three generated packs
    → terminal desk freeze and disposable-clone proof
    → isolated NIGHT-PACK-REHEARSAL-01, harvested
    → registered real-pack G2-b, harvested
    → L10-A + empirical T0-liveness closure/ruling
    → launch-realization recheck + claim registration + directive 416 audit
    → CAMPAIGN_TRANSACTION authorization
    → ALPHA small-model floor
    → BETA large-model floor
    → GAMMA contrast
    → G3 checks / L10-B and L10-C at their governed downstream gates
```

The desk-to-G2-b ordering is explicit. D-176 additionally inserts the pack-bound rehearsal before G2-b, and requires empirical T0 liveness to close or be reruled before ALPHA. Evidence: `docs/decision_log.md:211–213,11539–11542`; `TASK_QUEUE.md:703–704`; `docs/process/v5-l10-rehearsal-phase.md:103–110`.

The first claim-bearing pack is **ALPHA**, not another prefill probe or G2-b. Floors are minted from the transaction corpus; an aggregate floor artifact is not a G2-b prerequisite. Evidence: `docs/process/v5-l10-rehearsal-phase.md:103–110`; `SHAKEDOWN-G2-RUNSHEET.md:156–162,240`.

| Link | Agent-doable now? | Live/authority gate |
|---|---|---|
| Issuer, producer fixes, pin/pack generation, clone proof | Yes, in an authorized writable seat | Code/record gates; no quiet capture |
| Rehearsal plan and registration preparation | Yes | Seal before collection |
| Pack-bound rehearsal | Preparation only | `[QUIET-MAC]`; authentic producer launch, isolated roots, zero agents/operator actions at T0; Ed’s privileged positive control remains |
| G2-b design and unattended stop implementation | Yes | Registration plus cold Fable gate and one Opus refuter |
| G2-b collection | No active scout execution | `[QUIET-MAC]`, fresh authorization/T0; non-claim |
| L10-A and empirical receipt analysis | After immutable inputs exist | Bench work; cold ruling if liveness cannot close |
| Launch-realization recheck | Yes | Reviewed code before transaction |
| First claim registration and #416 audit | Yes | Frozen code/protocol and cold gates |
| Transaction GO | Magistrate decision after G2-b | Authenticated `CAMPAIGN_TRANSACTION`; not supplied by G2-b’s authorization |
| ALPHA/BETA/GAMMA collection | No active scout execution | `[QUIET-MAC]`, valid battery-compliant freeze and purpose-bound authorization |

Evidence: latest desk brief, `:36,41–46`; D-176, `docs/decision_log.md:11515–11542`; `docs/orchestration.md:80–88`; queue, `TASK_QUEUE.md:691,703–704`.

`PIPELINE-SMOKE-LIVE-01` Q13 is the modular G1/G2/G3 proof lane, not authorization for an extra diagnostic family. Its older `_v4` wording must be reconciled with the current runsheet. G3 runs after campaign windows, before the next campaign arm. Evidence: `TASK_QUEUE.md:710,758`; `docs/process/state_kernel.json:10626–10627`; `SHAKEDOWN-G2-RUNSHEET.md:28–43`.

L10-A uses the real G2-b prefix, validates/reduces its bundles and exercises finalization only in scratch custody. PASS requires the exact singleton `analysis_finalization_member_cover_mismatch`, empty floor directories and unchanged G2-b bytes. L10-B requires the real transaction floor corpus; L10-C belongs to the full campaign/publication path. Evidence: `docs/process/v5-l10-rehearsal-phase.md:331–365,387–424,103–110`.

The launch recheck remains a genuine transaction prerequisite. Current launcher code verifies consumption and proceeds to `execve`; the queued lane calls for a fresh projection/digest recheck at that boundary. Evidence: `scripts/launch_window.py:272–286`; `docs/process/state_kernel.json:10561`; `TASK_QUEUE.md:704`.

**Ed lanes.** E7’s `[ED-EXTERNAL]` lane is stale for transaction authorization: its own updated acceptance delegates the decision to the magistrate under D-171/D-176. E166 mixes agent-doable clone/custody preparation with hardware/privilege work; its old production head is not current deployment authority. The privileged-anchor positive control is still explicitly Ed-owned. WALL-METER-GAIN E214 remains a separate physical metrology lane; it is not an installed dependency of Q3/Q4 and should not silently be treated as their extra measurement window. Evidence: `TASK_QUEUE.md:691,696,698,703–704`; `docs/decision_log.md:10926–10947,11529`; battery ruling, `:127`.

**Directive #416** bites before the first claim-bearing `_v5` window, at a head containing #465. Run the blind Astra 6 xhigh, Fable 5.1 and Opus 5.5 xhigh full-system audit once per frozen code/protocol change. It does not substitute for registration’s cold Fable gate/refuter or the issuer/pack code gates. Evidence: latest desk brief, `:36,43`; `docs/process_traces/2026-09-24-interactive-4b/30-prearm-audit-kit-416.md:1–11,33–60`.

**Directive #421** bites on every window, including rehearsal and G2-b. Battery authentication governs capture attachment, both bracket-selection paths, bundle access and whole-window consumers. Battery S3 explicitly forbids transaction-pack arms before the new freeze is verified and contains a pre-commit stop if specified helper/preregistration files are pinned; that choice must be settled before terminal desk freeze. Evidence: latest desk brief, `:36`; `docs/decision_log.md:12220`; battery ruling, `:119–125,131`.

### Recommended registration

Register **one next measurement block with separately authorized occurrences**:

- **`r1`**, proposed label: `rehearsal-t0-unattended-v5-<UTC>`, isolated pack-bound rehearsal, `purpose=T0_REHEARSAL`, non-claim.
- **`s1`**, proposed label: `d117-v5-g2b-shakedown-<UTC>`, only after `r1` passes and is harvested, `purpose=G2B_SHAKEDOWN`, `claim_eligible=false`, one authentic ABBA block and governed post-bracket stop.
- Reserve an ARM-ABORT proof occurrence with separate custody; do not reuse its expired arm or T0 evidence for `s1`.

These labels are proposals for the lead to seal. The rehearsal prefix and purpose are contractual; G2-b’s non-claim purpose and permitted-block restriction are contractual. Evidence: `docs/decision_log.md:11515–11518,11529–11541`; `SHAKEDOWN-G2-RUNSHEET.md:220–222,689`.

The registration must fix, before collection:

- Reviewed code head; issued pin/bundle hashes; exact pack IDs/digests, predecessor and freeze identities; current acceptance identity and the distinct acceptance-cutoff/live-seed roles.
- Isolated roots, backup destinations, custody, launch-chain bytes, step-6 record and independently confirmed `hC`.
- Rehearsal G1–G10 closure, privileged-control handling, ARM-ABORT expiry and fresh G2-b T0.
- Exact first-stage/block stopping mechanism, whole-window/bracket review, physical-ahead terminal boundary, harvest and recovery rules.
- Battery evidence obligations, clock and clean-dwell policy, agent teardown, capture deadline and bounded shutdown/courier behavior.
- Exact L10-A refusal and empty-floor invariant; no promotion of either diagnostic occurrence into campaign evidence.

Evidence: `docs/decision_log.md:11515–11532`; `SHAKEDOWN-G2-RUNSHEET.md:156–203,220–240`; `scripts/run_night.py:73–99`; latest desk brief, `:36`.

There is a concrete unattended-planning gap to close: `gen_g2_phase_d.py` offers `--new-g2a-window`, not a G2-b plan writer, and its rendered G2-b stop still expects a second-terminal SIGINT. Seal and implement a governed unattended boundary before scheduling `s1`; do not invent a `--new-g2b-window` command. Pack-night plans must use the canonical writer and exact `pack_night` custody bindings. Evidence: `scripts/gen_g2_phase_d.py:529–545,603–622`; `joulewise/night_plan_writer.py:18–50`; `joulewise/night_gate.py:481–523`.

## 5. Stale or contradictory rows

| Record | Required disposition |
|---|---|
| Q2 `V5-G2A-PREFILL-PROBE-01` and A67’s G2-a hard dependency | Already stale: block 3 is COMPLETE SELECT. Close/reconcile rather than register another probe. |
| A67 kernel acceptance requesting selector/pin advancement | Record those completed obligations; issuance and pack proof remain. |
| A196 missing successor roots | Becomes stale only after generated evidence-bearing roots and the clean-clone A5 proof land. |
| A69 blocked on desk day | Becomes ready after desk closure, but its post-freeze rewriting order needs ruling before freeze. |
| A71 blocked on G2-a | Already unblocked; desk closure does not finish the renderer. |
| A153 prompt-0 implementation-in-flight note | Producer has fixed prompt 0; census, supersession and clone-proof closure must still be recorded. |
| Q3 desk dependency | Becomes satisfied after full desk proof; pack rehearsal remains an independent hard gate. |
| E166 provisional September checkout/pin notes | Replace with the reviewed deployment head and authenticated current custody; keep actual live prerequisites. |
| `NIGHT-REHEARSAL-01` closure versus pending rehearsal dependency | Kernel notes describe completed acceptance while downstream still waits; reconcile harvested closure, do not assume a new stub night is needed. |
| E7/Q4 “Ed-authorized” lane wording | Update to delegated magistrate authorization while preserving G2-b and authenticated-record requirements. |
| Q13 `_v4`/older refusal wording | Align with the current `_v5` runsheet and exact L10-A singleton. |
| Old calibration-issuance/cap-hold kernel state | Reconcile with issued 25G83 r2; do not automatically erase an unresolved cap obligation or schedule another calibration block from stale text. |
| Battery A308 stage-progress notes | Reconcile landed work and outstanding S3/S4 disposition; desk freeze alone does not close the entire directive. |

Evidence: `TASK_QUEUE.md:691,696,702–704,710,757–760,807,832`; `docs/process/state_kernel.json:1518–1556,3586–3605,3770–3799,5545–5628,5776,10298–10375`; `RUN_STATE.md:13,89`; latest desk brief, `:11–17`; `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json:8–24`.

Also correct procedure contradictions before executing them: generic adjacent-predecessor/ordinal text conflicts with the ruled `_v3`→`_v5` mapping; old step-6 `_v4` filenames conflict with current `_v5` constants; aggregate-floor preconditions conflict with ruling 97; unconditional desk arm PASS conflicts with S0’s governed-refusal criterion. Evidence: `docs/phase_2/window_runbook.md:307–315`; `joulewise/arm_readiness.py:78–85`; estate template, `:274–308`; S0 runsheet, `:2477–2480`; `SHAKEDOWN-G2-RUNSHEET.md:43,156–162`.

## Plan

Estimates below are planning judgments in working hours, excluding CI queues, cold-seat availability and retries. Commands are for subsequently authorized lead work; this scout made no repository changes.

| Step | Commands/work | Files changed | Gate tier | Estimate |
|---|---|---|---|---:|
| 1 | Finish parallel issuer PR; verify harvest/registration authentication and archive-only reads. | `scripts/issue_g2a_prefill_prompt_pin.py`, relevant tests | **Code:** Sol executing review, whole suite, CI, Fable final pass, dispositions/Impact | 2–4 |
| 2 | Resolve floor compatibility privately; repair contrast’s self-contained generic replay; settle current acceptance and battery S3/S4/A69 sequencing. | Three prospective generator sources, focused tests; ruling record if needed | **Code** for implementation; **light** for recording settled facts; cold gate for changed contracts | 3–6 |
| 3 | Run the issuer command in §2 directly into the portable source bundle. Verify references/hashes without logging the coordinate. | `configs/campaigns/d117_contrast_v5/prefill_pin/**` | **Records: light**, after issuer gate | 0.5–1 |
| 4 | Run ALPHA, BETA, GAMMA commands in §2; repeat with `--check`; review declared output inventories and prompt-0 supersession census. | Three pack subtrees; source bundle; supersession/census record | **Code/measurement gate** for changed producers and claim-capable packs | 1–2 |
| 5 | Run focused tests and canonical suite: `python3 -m unittest discover -s tests`; obtain CI and Fable final pass at the reviewed combined head. | Gate/run records; code only if a defect is fixed | **Code** | 2–4 |
| 6 | Execute §3 in independent primary/sacrificial throwaway clones; run the full S0 falsifier sections, not only happy-path freeze. | Clone-local projections, evidence, freeze receipts, pinset; external custody/transcripts | Desk evidence; publication still requires actual main/CI authentication | 3–5 |
| 7 | Close A67/A196 with exact proof; reconcile the stale rows in §5 and regenerate their views through the state-kernel workflow. | `docs/process/state_kernel.json`, generated queue/restart views, dated report | **Docs/records: light** | 0.5–1 |
| 8 | Prepare final measurement and disjoint rehearsal checkouts; authenticate restored production ledger/custody, avoiding production restoration into rehearsal. | External checkouts/custody and clone-readiness record | **Records: light**; actual hardware/privilege gates separate | 1–2 |
| 9 | Implement/review unattended G2-b boundary and pack-night plan production. Use `NightPlan.from_mapping` and `write_night_plan`; run `python3 scripts/gen_g2_phase_d.py --check`. | Governed generator/chain/plan adapter and tests; generated runsheet region | **Code**, Fable final pass; registration cold gate | 2–5 |
| 10 | Seal proposed `r1`/`s1` block and analysis plan with cold Fable + one Opus refuter. Prepare exact authorization, step-6 and harvest artifacts. | Registration/analysis records; external plan/custody files | **Docs/records light plus mandatory cold science gate** | 2–4 |
| 11 | Lead prepares installer output with `scripts/install_night_agent.sh --plan "$PLAN" --python "$PY" --render-only "$CUSTODY/render"`; actual install/live driver is a separate lead-controlled handoff. Runtime interfaces: `scripts/run_night.py rehearse --plan "$REHEARSAL_PLAN"` and `scripts/run_night.py run --plan "$G2B_PLAN"`. | External installation artifacts, live custody/receipts/harvests | **`[QUIET-MAC]`**; no active scout; privileged positive control Ed-owned | 1–3 per occurrence, registered ceilings govern |
| 12 | After G2-b, run `python -m joulewise validate-bundle "$BUNDLE" --strict`, `python -m joulewise reduce "$BUNDLE" --output "$REDUCTION"`, and the exact scratch checker below. Analyze empirical T0 receipts; close or rerule liveness. | External L10 custody and immutable analysis records | Bench analysis; **cold gate** for changed analysis/limitation ruling | 1–3 |
| 13 | Land launch-realization recheck; freeze claim protocol; run #416 triple audit; seal claim registration; magistrate issues `CAMPAIGN_TRANSACTION`. | Launcher/tests, audit and registration/authorization records | **Code** plus cold science gate and #416 | 3–6 |
| 14 | Lead-controlled ALPHA → BETA → GAMMA transaction occurrences; G3 after each window and L10-B/C at their proper corpus gates. | Raw immutable bundles, ledger/custody, harvest and claim artifacts | **`[QUIET-MAC]`**, #421 on every window; no active scout | Registration must budget actual duration |

The exact L10-A finalizer command is:

```sh
"$PY" scripts/check_window_provenance.py \
  --expect-finalize-refusal \
  --scratch-dir "$L10_A_SCRATCH_ROOT" \
  --prospective-manifest "$L10_A_STAGING_ROOT/prospective/analysis_manifest_v3.json" \
  --plan-tree "$L10_A_STAGING_ROOT/prospective/plan_tree.json" \
  --custody-root "$L10_A_STAGING_ROOT" \
  --runs-root "$L10_A_STAGING_ROOT/g2b" \
  --whole-window-verdict "$L10_A_STAGING_ROOT/g2b/whole-window-verdict.json" \
  --bracket-binding "$L10_A_STAGING_ROOT/g2b/bracket-binding.json" \
  --calibration-ledger "$L10_A_STAGING_ROOT/calibration/calibration_observation_ledger.jsonl" \
  --aggregate-floor-artifact "$L10_A_STAGING_ROOT/floors/d117-v5-aggregate-floor.json" \
  --output-dir "$L10_A_STAGING_ROOT/analysis-output"
```

The aggregate-floor path is intentionally absent. Assert empty floor directories before and after, identical G2-b tree hashes, and the exact singleton refusal. Evidence: `docs/process/v5-l10-rehearsal-phase.md:387–424`.

Gate tiers follow the current six-key code and light-record doctrine; live driver and render-only interfaces are present on main. Evidence: `docs/process_prune_2026-09-29.md:9–11`; latest desk brief, `:43`; `scripts/install_night_agent.sh:5,24`; `scripts/run_night.py:4313–4347,4387–4394`.