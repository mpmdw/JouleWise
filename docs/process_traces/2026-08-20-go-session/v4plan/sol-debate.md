```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The empty allowlist defect is the previously identified lifecycle circularity, now mechanically confirmed; _v4 needs a pre-mint r4 amendment, a 168-hour horizon, corrected ordering, and a full three-pack clone proof.",
  "workspace": {
    "base_requested": "5bd7acf",
    "base_mode": "exact",
    "head_start": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "head_end": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "upstream_end": "b9e197a61e884ee1040bcbc6f9f1092a7c027282",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The ruled empty allowlist makes _v4 structurally unarmable",
        "evidence": "The arm path supplies reviewed_main(pack_root).head_commit to every frozen R1 generic receipt; a throwaway-clone probe produced EMPTY=REFUSE:DEPENDENCY_CHANGED_SET and passed beyond line 3212 only with exact transaction-output paths.",
        "recommendation": "Amend D-148.5 pre-mint with the exact output allowlist, U11-before-authoring order, and family-wide freeze-slot normalization; require a full three-pack clone proof."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The generic horizon must be 168 hours, not 72",
        "evidence": "The ratified nightly shape reaches the last arm around T+74h clean and T+146h with one refused night per lane; 72h misses even the clean schedule.",
        "recommendation": "Ed approves 604800000000000 ns for the ten generic policies, a T0+24h exact-byte response deadline, and per-window residual re-pinning."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "The opposing ordering still leaves a dependency-manifest refusal",
        "evidence": "Actual _v3 plan trees before U11 versus after freeze remain unequal after freeze-slot normalization because U11 changes projection state, identity units, projection receipt, and producer-contract binding.",
        "recommendation": "Run all three U11 projections and all ordinary tracked commits before evidence derivation; after derivation permit only authenticated evidence, freeze, and marker outputs."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "title": "EvidenceLifecycleError escapes from both generation and verification",
        "evidence": "The unguarded calls are arm generation at 6139-6141 and verification re-derivation at 6334-6336; the existing catch at 4613 and temporal catches do not cover either call.",
        "recommendation": "Add governed refusal conversion and a defect-shaped regression at both sites."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "title": "The four-type V4 assignment and staged implementation should follow the opposing decomposition",
        "evidence": "SUCCESSOR_CHAIN is not registry-expressible as a type, while its failure is Git ancestry; S-0 isolates the lifecycle correction that gates every downstream stage.",
        "recommendation": "Use POLICY/LIFECYCLE/CUSTODY/GIT and make S-0 plus its adversarial review a prerequisite for S-1 through S-5."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence.R1EvidenceLifecycleTests.test_changed_set_primary_gate_and_manifest_conjunct_discriminate tests.test_arm_readiness_evidence.R1EvidenceLifecycleTests.test_plan_tree_normalization_subtracts_only_freeze_slot tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_successor_chain_refusal_is_governed_and_typed",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.452s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python3 \"$TMPDIR/v4_arm_gate_probe.py\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "EMPTY=REFUSE:DEPENDENCY_CHANGED_SET",
          "EXACT=PASS_PAST_3212:1:1",
          "TAMPER=REFUSE:DEPENDENCY_MANIFEST"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "EMPTY=REFUSE:DEPENDENCY_CHANGED_SET.*EXACT=PASS_PAST_3212:1:1.*TAMPER=REFUSE:DEPENDENCY_MANIFEST"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c \"import subprocess; from joulewise.arm_readiness import normalize_plan_tree_for_freeze_evidence as n; p='configs/campaigns/d117_floor_qwen25_1p5b_v3/plan_tree.json'; g=lambda c: subprocess.run(['git','show',c+':'+p],check=True,capture_output=True).stdout; print('NORMALIZED_EQUAL='+str(n(g('1d3873bb7a37e9363202429f14587c85a0b4efc0'))==n(g('5e38f1e62c982198186e275df350493d69b010aa'))))\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "NORMALIZED_EQUAL=False"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "NORMALIZED_EQUAL=False"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "5bd7acf38fbdd71e77c5da30094e1e6183777697"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## HEAD \\(no branch\\).*5bd7acf38fbdd71e77c5da30094e1e6183777697"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "D-148.5 currently mandates an empty allowlist and an order incompatible with its own lifecycle gate.",
      "needs": "Magistrate issues r4 before registry mint."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The 168-hour freshness trade and response deadline require Ed.",
      "needs": "Ed approves or the transaction remains unmintable."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The executed clone probe covered one frozen R1 item, not the complete three-pack transaction.",
      "needs": "Run the specified three-pack author-through-arm proof against final candidate bytes."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No canonical suite, live arm, hardware qualification, or quiet-window measurement was performed.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — Blocker: same lifecycle defect, stronger mechanism

This is the same defect as my “confirmed R1 lifecycle circularity,” not a separate third defect. Opus supplied the complete arm-time explanation.

`generate_arm_receipt` obtains the repository HEAD through `reviewed_main(pack_root)` and passes it into evidence discovery. `_freeze_evidence_for_arm` independently recomputes that same pack repository’s HEAD. At the measurement pack path, this is therefore the live measurement-checkout HEAD.

Every generic item recorded in a v2-schema freeze receipt is looped through `_authenticate_generic_evidence_item`, whose R1 branch calls `validate_r1_evidence_lifecycle`. The precise active span is 4319–4364; line 4318 alone merely stores the decoded source.

The throwaway-clone result was decisive:

- Empty list: `DEPENDENCY_CHANGED_SET`.
- Exact transaction paths: execution returned from `_freeze_evidence_for_arm`, proving passage beyond 3212.
- A non-freeze plan-tree mutation still refused as `DEPENDENCY_MANIFEST`.

The defect must be ruled before mint because the registry value, normalization semantics, evidence derivation commit, plan-tree registry digest, and freeze receipts become mutually pinned. A post-mint correction costs `_v5`.

The determinate allowlist, after moving U11 before evidence, is the Cartesian expansion of these three roots:

- `configs/campaigns/d117_floor_qwen25_1p5b_v4`
- `configs/campaigns/d117_floor_qwen25_7b_v4`
- `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4`

over these eleven applicable slugs:

`acceptance-owner`, `doctrine-pin`, `estimator-identity`, `mint-trust`, `multicell-mint`, `pack-authentication`, `pack-family`, `reason-code-coverage`, `receipt-oracle`, `recovery-ledger-test`, `three-window-regression`

and these exact forms:

- `arm_readiness.sources/<slug>.json`
- `arm_readiness.evidence/evidence-<slug>.json`
- `arm_readiness.evidence/evidence-<slug>.json.sha256`
- `arm_readiness.freeze.receipts/freeze-0004.json`
- `arm_readiness.freeze.receipts/freeze-0004.json.sha256`
- `plan_tree.json`
- `plan_tree.sha256`

That is 37 exact paths per root, 111 total. If option-(a) publication is committed in-repository after derivation, add only:

- `configs/campaigns/d117_family_publication_v4.json`
- `configs/campaigns/d117_family_publication_v4.json.sha256`

No identity-projection or `producer_contract.json` path belongs in the allowlist: U11 must precede derivation.

The code must additionally normalize the exact freeze slot for all three registry-declared successor plan trees, not merely the current pack’s plan tree. `PACK_FAMILY` binds sibling plan trees; otherwise sibling freeze commits still fail the manifest conjunct.

Required S-0 gate: repeat the full three-pack transaction in a throwaway clone—U11 ×3, common-head evidence authoring, evidence commit, freeze ×3, marker construction, arm generation and verification for every pack—and prove:

- all items cross 3212;
- both arm and verification paths return governed results;
- an ordinary changed path refuses;
- an unexpected output-directory file refuses;
- a non-freeze mutation in the current or sibling plan tree refuses;
- missing, extra, or unused allowlist entries fail the candidate contract.

### F2 — Blocker: converge on 168 hours

**CONCEDED:** use 168 hours, `604800000000000` ns, proposed policy ID `r1.execution_bound.freeze_generic_168h.v1`.

The 72-hour recommendation fails the ruled operational shape: the clean nightly schedule reaches the last arm near T+74h, while a refused night in each lane reaches approximately T+146h. A seven-day horizon leaves approximately 94h and 22h respectively.

My `T0+24h` Ed-response bound and Opus’s per-window re-pin are complementary:

- No exact-byte yes by `T0+24h`: abort and re-author while unpublished.
- Before every window: revalidate the same boot, reviewed HEAD, remaining earliest deadline, acceptance binding, estimator-pinned files, and other explicitly identified non-T0 residuals.

Freshness cost to Ed: the ten generic facts may be legally reused for up to seven days instead of one, widening the maximum undetected interval by six days for state not covered by Git/dirty-tree checks, boot binding, the environment fingerprint, or fresh T-0 evidence. The response deadline and per-window re-pin reduce that residual; they do not erase the policy trade.

**DISPUTED:** GAMMA’s 5.17-hour runtime is not part of the generic-evidence fuse before the last arm. ALPHA and BETA occupancy delay GAMMA’s arm; GAMMA execution follows its own arm/consume instant. This does not alter the 168-hour conclusion.

### F3 — Blocker: corrected transaction order

**AGREED with correction:** kernel, canonical, ordinary custody, runsheet, code, registry, marker consumer, scheduler, current references, and other tracked commits must land before evidence authoring.

Opus’s order still placed U11 after evidence. Executed comparison against the real `_v3` transaction shows that U11 changes non-freeze fields, so the existing manifest normalization cannot forgive it.

Correct order:

1. S-0 lifecycle correction and full clone proof.
2. Land all registry/code/marker/scheduler/current-reference and `_v4` root changes.
3. Run U11 projection for all three packs and commit it.
4. Land kernel/runsheet/custody changes; run canonical at this final pre-evidence tree.
5. Make Ed’s tree-preserving terminal-review attestation. This HEAD is the common derivation head.
6. Author all three evidence sets at that common HEAD and commit them together.
7. Mint and commit `freeze-0004` for ALPHA, BETA, and GAMMA.
8. Run ceremony/dry-run checks, build the marker candidate, and obtain Ed’s exact-byte response by `T0+24h`.
9. Publish the authenticated family marker atomically. If tracked, only its two exact paths are allowed.
10. Run the published-head suite without another ordinary tracked commit in the measurement checkout; then shakedown and ALPHA→BETA→GAMMA with the checkout pinned.

The “6–9 commits after evidence” count is therefore **DISPUTED as an invariant**. It describes the old ordering; corrected ordering moves U11 and ordinary custody ahead of derivation. Empty `[]` remains fatal even with fewer commits.

### F4 — Should-fix: second exception escape confirmed

**CONCEDED:** 6334–6336 joins the code-delta manifest.

The two unguarded sites are:

- Arm generation: 6139–6141.
- Verification semantic replay: 6334–6336.

Each needs its own regression proving `EvidenceLifecycleError` becomes the registry-derived structured refusal and never escapes as a traceback.

### F5 — Should-fix: typing, stages, and final disposition

**CONCEDED:** use Opus’s four-type allocation:

- `POLICY`: `CLASS_MISMATCH`, `UNKNOWN_POLICY`
- `LIFECYCLE`: `DEPENDENCY_CHANGED_SET`, `DEPENDENCY_MANIFEST`, `TEMPORAL_BUDGET`, `V1_GRANDFATHERING`
- `CUSTODY`: `FAMILY_PUBLICATION`
- `GIT`: `SUCCESSOR_CHAIN`

`SUCCESSOR_CHAIN` is not an admissible registry type, and this role is specifically about Git ancestry, so `GIT` is more accurate than my prior identity-oriented typing.

**CONCEDED:** several bounded implementation sessions with S-0 gating all later work is the safer decomposition. S-0 must complete before core registry, marker/successor route, scheduler gate, family emission, or consistency stages proceed.

**DISPUTED:** “33 receipts PASS ×3 packs” is incorrect. The current family has eleven generic receipts per pack, 33 across the family. The final `_v4` applicability census must mechanically confirm the same eleven before the 111-path allowlist is accepted.

Final amended deltas versus my original design:

| Position | Disposition |
|---|---|
| Empty allowlist causes structural unarmability | **AGREED**; same F2 lifecycle circularity, with Opus’s fuller mechanism |
| Use exact output allowlist instead of my open-ended authenticated-manifest proposal | **CONCEDED**, provided U11 moves earlier and all allowed bytes have independent authentication |
| 168h rather than 72h | **CONCEDED** |
| `T0+24h` Ed deadline | **AGREED**, retained |
| Per-window residual re-pin | **AGREED**, added |
| Kernel/canonical/custody before evidence | **AGREED** |
| U11 after evidence | **DISPUTED**; executed plan-tree comparison refutes it |
| Second B2 catch at 6334 | **CONCEDED** |
| Four-type mapping ending in `GIT` | **CONCEDED** |
| S-0-gated multi-session decomposition | **CONCEDED** |
| GAMMA runtime added to the pre-last-arm fuse | **DISPUTED** |
| 33 receipts per pack | **DISPUTED** |

Single ruling list:

- **D-148.5 r4 amendment:** replace `irrelevant_path_allowlist: []`; add family-wide freeze-slot normalization; amend R-4.5 ordering; raise the ten generic policies to 168h; extend B2 catch to both sites; fix the exact V4 type map; require S-0’s three-pack proof.
- **Ed:** approve the seven-day freshness cost and `T0+24h` response bound; choose the V6 publication-marker path; install/confirm mint-command and sudo qualifications; commit to the same-boot campaign span.
- **Plan-internal:** staged WRITE_SCOPE decomposition, U11-before-authoring, one common evidence derivation HEAD, exact 111/113-path generation, negative mutation matrix, published-checkout pinning, and per-window re-pin implementation.

## Residual risk

The replayable clone probe used one frozen R1 item to isolate the gate. It proves the mechanism and the viability of an exact authenticated exclusion, but it is not the required three-pack author→U11→freeze→marker→arm integration proof. No live arm, full canonical suite, hardware qualification, or quiet-window operation was performed.