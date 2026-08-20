```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The conditional _v4 runsheet is complete, but execution requires rulings on the 24-hour envelope, a confirmed R1 lifecycle circularity, and the V6 publication marker.",
  "workspace": {
    "base_requested": "5bd7acf",
    "base_mode": "exact",
    "head_start": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "head_end": "5bd7acf38fbdd71e77c5da30094e1e6183777697",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "The ruled transaction cannot fit a 24-hour fuse once Ed's unbounded step-6 latency is included",
        "evidence": "The fixed author-through-final-window budget is 22.6767 hours before Ed latency. Thus completion is 22h40m36s + L_Ed; even L_Ed=0 leaves only 1h19m24s.",
        "recommendation": "Before mint, raise the ten live freeze-generic policies to 72 hours and bind Ed's step-6 response to T0+24h; otherwise no finite horizon proves the unbounded schedule."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "title": "The ruled empty lifecycle allowlist makes author-then-commit evidence stale before freeze",
        "evidence": "A scratch Git reproduction committed a valid R1 source and receipt after their derivation head. validate_r1_evidence_lifecycle refused with DEPENDENCY_CHANGED_SET naming both authored paths. Current production ordering performs the same author-commit-freeze transition.",
        "recommendation": "Magistrate must authorize a narrowly authenticated transaction-output exclusion and require a complete three-pack synthetic author-to-freeze integration proof before any live authoring."
      },
      {
        "id": "F3",
        "severity": "blocker",
        "title": "V6 remains a transaction-blocking Ed decision",
        "evidence": "The registry cannot install an unresolved family_publication_marker_schema, and step 6 must mechanically refuse publication until either a real marker validates or the UNBUILT canary blocks the campaign.",
        "recommendation": "Choose option (a), build-at-boundary, before registry finalization."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence.R1EvidenceLifecycleTests.test_changed_set_primary_gate_and_manifest_conjunct_discriminate tests.test_arm_readiness_evidence.R1EvidenceLifecycleTests.test_plan_tree_normalization_subtracts_only_freeze_slot",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.454s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && shasum -a 256 configs/arm_readiness/d117_row_registry_v1.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "5bd7acf38fbdd71e77c5da30094e1e6183777697",
          "d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5  configs/arm_readiness/d117_row_registry_v1.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5bd7acf38fbdd71e77c5da30094e1e6183777697.*d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The 24-hour envelope is mathematically unfit with unbounded step-6 latency.",
      "needs": "Obtain Ed approval for 72-hour freeze-generic evidence plus a T0+24h confirmation deadline."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The current changed-set gate refuses the transaction's own committed evidence outputs.",
      "needs": "Obtain a magistrate ruling on authenticated lifecycle-output treatment and prove it end to end."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "V6 marker option is unresolved.",
      "needs": "Ed selects marker option (a) or (b) before registry bytes are finalized."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This was a read-only design review; no canonical suite or live hardware/quiet-window action was performed.",
      "needs": ""
    }
  ]
}
```

## Findings

### F1 — Blocker: envelope arithmetic

Let `T0` be the earliest issuance time among the ten live freeze-generic evidence sets. The family deadline is the earliest `valid_until`, not the last pack’s mint.

| Fuse-bound segment | Reserved time |
|---|---:|
| Three-pack evidence authoring and commit | 0.50 h |
| Plan regeneration, U11 projections, three `freeze-0004` mints | 0.50 h |
| P1/P2/P3, one dry-run, marker instance, exact-byte table | 0.50 h |
| Ed step-6 confirmation | `L_Ed`, unbounded |
| Atomic publication and custody | 0.25 h |
| Published-head canonical suite | 1.00 h |
| D-139 shakedown, including reduction and ten-minute idle | 0.50 h |
| Three inter-window GO/arm/closeout reserves | 1.50 h |
| Alpha campaign | 6.28 h |
| Beta campaign | 6.48 h |
| Gamma campaign | 5.1667 h |
| **Fixed total** | **22.6767 h** |

Therefore:

`T_finish − T0 = 22h40m36s + L_Ed`

The 24-hour policy does not fit. With zero Ed latency, margin is only 1h19m24s. An overnight-shaped 12-hour response produces 34h40m36s. Because `L_Ed` is unbounded, no finite horizon can provide an unconditional proof.

Pre-mint proposal to Ed:

- Change the ten live generic rows to policy `r1.execution_bound.freeze_generic_72h.v1`, horizon `259200000000000` ns.
- Keep the four `NO_R1_AUTHORING_LANE` rows at 24 hours, the two T-0 procedural rows at six hours, and all 20-minute/six-hour T-0 tiers unchanged.
- Bind step-6 confirmation to `T0 + 24h`. No yes by then means abort while reversible, remove only governed unissued outputs, and re-author/re-mint later.
- Preserve the one-boot conjunct. A reboot voids the family regardless of remaining wall-clock time.
- Recompute against the actual minimum deadline before step 6 and before every window.

At the 24-hour Ed deadline, the schedule reaches 46h40m36s, leaving 25h19m24s inside 72 hours.

Freshness cost: the ten suite-derived and execution-derived facts may be almost three days old at final consumption instead of one. Same boot, final reviewed HEAD, P1/P2/P3, and shakedown reduce some risk, but the B-1 fingerprint comparator only protects authoring reuse; it does not establish that the environment remained unchanged until arm. If Ed will not accept that cost and the 24-hour response bound, refuse to mint.

### F2 — Blocker: the lifecycle transaction is circular

At current HEAD, R1 computes every path changed between `derivation_commit` and current reviewed HEAD, subtracts `irrelevant_path_allowlist`, and refuses if anything remains. The ruled registry sets that allowlist to `[]`.

The required ordering then does this:

1. Author evidence with derivation commit `H`.
2. Commit `arm_readiness.sources/**` and `arm_readiness.evidence/**`, producing `H+1`.
3. Ask freeze to authenticate the evidence at `H+1`.

The scratch probe reproduced the result:

- `PROBE_RESULT=REFUSE`
- role `DEPENDENCY_CHANGED_SET`
- changed paths were the newly committed evidence source and receipt.

The later plan-tree, projection, freeze-receipt, and sibling-pack commits enlarge the same changed set. The existing synthetic author-to-freeze test uses the dormant v1 registry, so it does not cover the installed R1 path.

Recommended ruling: preserve `irrelevant_path_allowlist: []`, but allow the lifecycle gate to subtract an exact, transaction-scoped output manifest only after those bytes have been independently authenticated. That manifest must cover all three packs’ governed sources, receipts, sidecars, normalized plan-tree freeze slots, identity projections, and freeze receipts. It must not accept globs or unrelated post-derivation files.

Required proof:

- Three synthetic `_v4` roots.
- Author all evidence at one reviewed head, commit it, regenerate plans, issue U11 projections, and mint three `freeze-0004` receipts.
- Dry-run and verification replay succeed under the installed v2 registry.
- Mutating any ordinary dependency after derivation still emits `readiness_r1_dependency_changed_set`.
- Adding an unexpected file beneath a governed output directory also refuses.
- Plan-tree normalization continues to forgive only the freeze slot.
- No live authoring starts until this proof is green.

This is the largest risk. I would refuse to proceed without the ruling and that executed integration proof.

### F3 — Blocker: V6 marker selection

Recommendation: option (a), build-at-boundary.

Use schema id `joulewise.d117_family_publication_marker.v1` and an external canonical marker, proposed at `configs/campaigns/d117_family_publication_v4.json`. It must bind:

- The three `_v4` pack IDs and paths.
- Their three final committed plan-tree digests.
- Their three `freeze-0004` receipt paths and SHA-256 values.
- The exact installed registry `{registry_id, path, sha256}`.
- A complete-family predicate requiring all three entries.

The schema and consumer land before mint; only instance construction and validation consume fuse time. Step 6 refuses publication unless the candidate instance validates.

If Ed chooses option (b), install exactly `joulewise.d117_family_publication_marker.UNBUILT.v0`; step 6 mechanically refuses publication, the entire `_v4` campaign remains unwired, and later repair costs `_v5`. If another family is already likely because of the envelope or F2, that incremental `_v5` price is correspondingly smaller.

### Executable transaction runsheet

This is conditional on F1–F3 being resolved.

**Step 0 — Pre-mint release gate**

- Preconditions: Ed selects V6; approves the 72-hour/24-hour-decision proposal; F2 is ruled and proven; D-144 BIG gauntlet and C-028 delta audits are green; final extra two-seat implementation pass and Fable review are complete; canonical baseline is green.
- Ed hands: install or confirm D-148.1 mint permissions for both freeze CLIs at the actual measurement checkout, or commit to running the six mint commands personally.
- Ed hands: authenticate and install `scripts/joulewise-network-time.sudoers` as `/etc/sudoers.d/joulewise-network-time`. Qualify exactly `/usr/sbin/systemsetup -setusingnetworktime off/on`, restore prior state, perform the privileged prior-state read, and confirm `sudo -n /usr/bin/powermetrics` works.
- Lead: verify clean final HEAD, no active stop card, no reboot planned, no claim window scheduled, and one uninterrupted measurement session reserved through step 5.
- Verify: scheduler’s mechanical shakedown gate, marker consumer, mint classifier, sudo qualification, and archive checkout are all present.
- Abort: any unresolved Ed item, red gate, unqualified privilege, dirty checkout, or inability to keep one boot.

**Step 1 — Install registry, code, and `_v4` roots**

- Role: delegated sessions build bounded deltas; lead reviews and integrates.
- Commit canonical `configs/arm_readiness/d117_row_registry_v2.json` with outer id `d117-row-registry-v2`, inner id `d117-r1-lifecycle-v1`, `_v4` successor IDs, resolved policies, V4 vocabulary, 300s/300s arm policy, marker schema, and the nine predecessor-binding keys.
- In the same commit as the registry, land the four mandatory V4 code changes, B-1 comparator, token allowlist, path constant, horizon assertion, B2 catch, predecessor assertion, and the F2 ruling.
- Emit and review:

  - `d117_floor_qwen25_1p5b_v4`
  - `d117_floor_qwen25_7b_v4`
  - `d117_contrast_qwen25_1p5b_vs_7b_v4`

- `d117_row_registry_v1.json` remains an unreferenced archival companion at SHA-256 `d248fdc521cb904b7ad8f1c4ecb834f7810a1d8f39697b462591f2feac39a2e5`.
- Run the roughly fifteen-file literal sweep: update live current-state consumers and tests; classify historical reports and frozen v1/v2/v3 pack bytes as immutable.
- Resolve the registry-driven `PACK_FAMILY` successor route. If the marker pass does not discharge the third carry, mark it TERMINAL, add the plain-language `CLAIMS_STATUS.md` limitation, and escalate to Ed.
- Verify: resolved registry loads; `_v4` profiles resolve ALPHA/BETA/GAMMA; v1 SHA pin holds; frozen historical trees are byte-identical; focused suites and canonical pass.
- Abort: any later code change after the reviewed evidence head, any historical byte movement, or any unresolved `PACK_FAMILY` carry.

**Step 2 — Author `_v4` evidence**

- Role: lead at the measurement checkout; no quiet measurement is started.
- Preconditions: final reviewed HEAD from step 1, same boot, F2 integration proof green, and 72-hour policy installed.
- Author fresh evidence for all three packs. Do not reuse prior namespaces. For reuse checks, compare the stored builder-emitted fingerprint digest against the freshly derived digest in `_authenticate_existing_r1`.
- `EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE` mismatch emits author refusal `evidence_author_environment_changed`; it is routine authoring noise, not pack corruption and not a D-078 attempt.
- Verify: all governed receipts PASS, derive from the exact reviewed HEAD, carry correct classes/policy IDs, and have a common one-boot envelope. Record the earliest issuance and earliest deadline as family `T0` and `T_expiry`.
- Abort: any refusal, namespace collision, HEAD drift, reboot, or less than the approved remaining envelope.

**Step 3 — Regenerate plan trees**

- Role: lead execution; delegated verification may be read-only.
- Preconditions: step-2 evidence committed and F2’s authenticated-output rule active.
- Regenerate all three plan trees against the v2 registry and final evidence. No science or runtime-budget delta is permitted.
- Verify: registry reference, plan IDs, pack IDs, evidence manifests, `_v4` names, and null freeze slots are exact.
- Abort: generator drift, unexpected inventory, science-facing delta, or an unclassified changed path.

**Step 4 — U11 and `freeze-0004` mints**

- Role: lead under the D-148.1 license; Ed runs the commands if the classifier is not licensed.
- Run U11 projection for ALPHA, BETA, GAMMA, then freeze each `_v4` root with its corresponding `_v3` predecessor.
- Verify every receipt is singleton `freeze-0004`, PASS, and binds exactly these sorted predecessor keys: `evidence_set_sha256`, `freeze_receipt`, `identity_receipt`, `pack_digest_algorithm`, `pack_id`, `pack_path`, `pack_sha256`, `plan_id`, `plan_sha256`.
- Verify ordinal is predecessor `freeze-0003 + 1`, paths point to the absolute measurement checkout, and all three final pack/tree/receipt hashes are recorded.
- Abort: any failed or partial mint. Do not publish a surviving subset; diagnose and restart the whole family under fresh evidence if necessary.

**Step 5 — Ceremony, probes, and marker candidate**

- Role: lead.
- Run file-09 P1/P2/P3 against each `_v4` pack: live registry reference loads, freeze reference authenticates, and arm semantics cross the registry gate.
- Run exactly one `generate_arm_readiness.py dry-run` per required governed ceremony. No real arm, verify, or consumption is issued.
- Under option (a), build the external marker instance and validate it. Assemble Ed’s exact-byte table containing all three plan-tree digests, all three `freeze-0004` receipt hashes, registry id/path/SHA, marker bytes/SHA, earliest expiry, boot UUID, and old-registry archival SHA.
- Archival `_v3` replay is valid only at both coordinates: its pre-install commit and absolute `/Users/edr/JouleWise-measurement-20260818` checkout. A location refusal elsewhere is expected, not corruption.
- Verify: P1/P2/P3 OK, dry-run PASS, no attempt/session ID spent, marker exact and complete.
- Abort: any probe/dry-run refusal, marker mismatch, reboot, or insufficient remaining envelope.

**Step 6 — Ed confirmation and publication-refusal anchor**

- Role: Ed hands; lead presents and records.
- Publication mechanically refuses until Ed confirms the exact table.
- Option (a): refusal remains until the marker instance validates.
- Option (b): the `UNBUILT.v0` canary refuses publication unconditionally.
- The proposed confirmation deadline is `T0 + 24h`.
- Verify: Ed’s explicit yes identifies the exact table digest, registry digest, marker digest, three pack digests, and three receipt digests.
- Abort: silence past the deadline, qualified/no/changed answer, altered bytes, reboot, or expiry. Everything remains unpublished and reversible.

**Step 7 — Atomic publication, kernel, canonical, custody**

- Role: lead; merge/publication gates remain lead-owned.
- Publish the one external family marker atomically for all three packs. Update current kernel rows and generated state, never frozen pack bytes.
- Run `python3 -m unittest discover -s tests` at the published head, then state-generation/check commands and custody hashes. Reserve one hour; the prior 3,755-test canonical run took about 46.3 minutes.
- Verify: full green, marker consumer authenticates all bindings, state checks clean, and custody records exact published HEAD.
- Abort: any red means no shakedown or claim window. Preserve the published failure record; no post-mint registry/pack repair is allowed. Correction is `_v5`-priced.

**Step 8 — First D-139 shakedown: the V5 measurement**

- Role: lead-owned unattended scheduler; all agents exit for the actual quiet capture.
- Issue the first real `_v4` arm under a D-149 GO receipt. Run the 59-pulse calibration, immediate reduction, in-band r6 check, ten-minute idle, custody close, and empty-or-recorded refusal log.
- The receipt records T-0 timestamp, arm timestamp, consume timestamp, T-0→arm gap, arm→consume observation, sample count, and predeclared p99. For the first sample, the conservative p99 is the sole/max observation.
- `arm_to_consume_budget_ns=300s` remains the minimum T-0 lifetime required at arm; it is not the measured arm→consume statistic.
- Mechanical scheduler gate requires T-0→arm ≤900s and p99 arm→consume ≤240s before authorizing alpha.
- The custodied shakedown GO receipt is the `_v4` reason-code-delta proof point.
- Abort: any refusal, out-of-band result, missing/malformed receipt, gap violation, or reason-code closure failure. Halt before all claims, give Ed the observed numbers, and price any policy change as `_v5`.

**Steps 9–11 — Alpha, beta, gamma claim campaigns**

- Role: lead-owned scheduler; no active agent during capture.
- Order: ALPHA 6.28h, BETA 6.48h, GAMMA 5.1667h.
- Each window gets its own fresh D-149 GO receipt, T-0 evidence, arm, no-retry acknowledgment, boot check, clock discipline, quiet census, custody root, closeout, and backup.
- Before each authorization, the scheduler authenticates the family marker, relevant `freeze-0004`, published HEAD, shakedown GO receipt, mechanical gap gate, same boot, and remaining generic-evidence deadline.
- Verify each window against its ratified count/budget and immutable plan.
- Abort on any refusal or failed closeout. No retry, registry edit, or `_v4` byte repair; diagnose from custody and escalate.

### Code-delta manifest and test pins

| Seam | Required delta | Mandatory test pins |
|---|---|---|
| Four V4 sets | Add `R1_LIFECYCLE_POLICY_CODES`, `R1_LIFECYCLE_LIFECYCLE_CODES`, `R1_LIFECYCLE_CUSTODY_CODES`, and `R1_LIFECYCLE_IDENTITY_CODES`; union them into `READINESS_REASON_CODES` and type-map them. | Exact membership, exact type per code, all eight roles unique, and receipts carrying each code validate. |
| Registry load closure | Reject a resolved refusal entry unless its code is registered and its type equals `REASON_TYPE_BY_CODE[code]`. | Mutate every code, type, duplicate, omission, and unknown role; every variant fails registry load. |
| B-1 comparator | In `_authenticate_existing_r1`, compare stored fingerprint SHA with the current builder-emitted SHA; mismatch emits `evidence_author_environment_changed` without overwriting append-only bytes. | Stable reuse passes; changed environment/interpreter/path refuses; PACK_AUTHENTICATION full-`os.environ` noise refuses; explicit fresh-author recovery passes. |
| Comparison tokens | Admit `EXECUTION_ENVIRONMENT_FINGERPRINT_EXACT_AT_REUSE` and `NO_R1_AUTHORING_LANE`; use the latter only for GIT_CHECKOUT, PRIVILEGE_INSTALLATION, IDENTITY_PIN_PROJECTION, DRY_RUN_REHEARSAL. | Exact four-kind assignment; illegal token or misassignment fails; no-lane kinds never enter generic comparator logic. |
| Horizon consistency | At resolved registry load, compare every one of the 13 T-0-authored kinds with `_validity_horizon_ns`; assert 300s budget equals capability horizon and remains below 20 minutes. | Mutate each class/kind independently; load fails. Confirm ten live generic rows carry Ed’s final 72-hour decision and only those ten changed. |
| B2 catch | Catch `EvidenceLifecycleError` around `_freeze_evidence_for_arm` in arm generation and append its governed refusal instead of escaping. | Synthetic frozen lifecycle defect returns a structured NO_GO/REFUSE with the exact `readiness_r1_*` code; no traceback. |
| Predecessor bindings | Assert registry bindings equal `sorted(FREEZE_PREDECESSOR_KEYS)`. | Exact nine pass; omission, addition, substitution, duplicate, and ordering mutation fail. |
| Registry path/archive | Point `ROW_REGISTRY_RELATIVE_PATH` to v2; retain v1 at its exact SHA; classify the full literal sweep. | New packs pin v2; old v1/v2/v3 artifacts remain byte-stable; current references contain no stale v1 path. |
| F2 lifecycle outputs | Implement the magistrate-approved exact authenticated-output manifest, not a broad allowlist. | Full three-pack author→commit→regen→U11→freeze proof; unexpected or ordinary changed paths still refuse. |
| Marker and `PACK_FAMILY` | Add marker schema/consumer, atomic three-pack validation, publication refusal, and registry-driven successor family derivation. | Missing/swapped/duplicated pack, receipt, registry, path, or digest refuses; no one- or two-pack publication; `_v4` PACK_FAMILY derives only from `_v4`. |
| Shakedown scheduler | Add a machine-readable gap receipt and enforce it before claim launch. | Absent/malformed/foreign receipt, >900s T-0→arm, or >240s p99 refuses; valid receipt authorizes; post-mint policy mutation is impossible. |

### WRITE_SCOPE and implementation decomposition

Do not assign this BIG delta to one Sol session. Use sequential, bounded sessions with independent review.

1. **S0 — F2 lifecycle correction**

   WRITE_SCOPE: `joulewise/arm_readiness.py`, `tests/test_arm_readiness_evidence.py`, `tests/test_arm_readiness_integration.py`, `tests/test_arm_readiness_lifecycle.py`.

   One Sol implementation session after the magistrate ruling; one adversarial review session.

2. **S1 — Core v2 registry and lifecycle contract**

   WRITE_SCOPE: `configs/arm_readiness/d117_row_registry_v2.json`, `joulewise/arm_readiness.py`, `joulewise/arm_readiness_evidence.py`, `joulewise/arm_readiness_evidence_t0.py`, `tests/test_arm_readiness_evidence.py`, `tests/test_arm_readiness_evidence_author.py`, `tests/test_arm_readiness_evidence_t0.py`, `tests/test_arm_readiness_registry.py`, `tests/test_arm_readiness_schemas.py`, `tests/test_arm_readiness_integration.py`, `tests/test_arm_readiness_lifecycle.py`.

   One Sol session, sequential after S0 because the files overlap; separate contract and execution lenses.

3. **S2 — V6 marker and successor-family route**

   Proposed WRITE_SCOPE, subject to Ed’s option/ruling: `joulewise/family_publication.py`, `scripts/publish_d117_family.py`, `joulewise/arm_readiness_evidence.py`, `tests/test_family_publication.py`, `tests/test_arm_readiness_evidence_author.py`.

   Marker schema/consumer implementation is one Sol session. The fuse-bound marker instance is not authored by that session; the lead builds it at step 5.

4. **S3 — D-149 mechanical shakedown gate**

   WRITE_SCOPE: `scripts/d149_go_evaluator.py`, `scripts/run_campaign.py`, `tests/test_d149_go_evaluator.py`, `tests/test_run_campaign.py`, `docs/process/d149-go-receipt-template.md`.

   One Sol session with a separate fail-closed scheduler lens.

5. **S4 — `_v4` family emission**

   WRITE_SCOPE: `configs/campaigns/d117_floor_qwen25_1p5b_v4/**`, `configs/campaigns/d117_floor_qwen25_7b_v4/**`, `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v4/**`, `configs/floor_mint/d117_qwen25_1p5b_v4_extraction_spec.json`, `configs/floor_mint/d117_qwen25_7b_v4_extraction_spec.json`, `tests/test_d117_v4_family.py`, `tests/test_d117_floor_qwen25_1p5b_plan.py`, `tests/test_d117_floor_qwen25_7b_plan.py`, `tests/test_d117_decode_contrast_plan.py`.

   One Sol emission session can own all three roots because family atomicity requires one generator view.

6. **S5 — Current-reference consistency**

   WRITE_SCOPE: `docs/phase_2/alpha_arm_readiness.md`, `docs/phase_2/beta_arm_readiness.md`, `docs/phase_2/gamma_arm_readiness.md`, `docs/phase_2/window_runbook.md`, `CLAIMS_STATUS.md`, `WINDOW_STATUS.md`, `tests/test_docs_freshness.py`, `tests/test_gen_state.py`.

   One bounded consistency session. Historical process traces and frozen pack bytes are read-only.

Lead-only:

- Ed decisions, scope/ruling adjudication, D-148.1 and sudo installation.
- Final integration, C-028 adjudication, extra two-seat pass, Fable final, canonical acceptance, and merges.
- `RUN_STATE.md`, `TASK_QUEUE.md`, `PROJECT_STATUS.md`, `docs/decision_log.md`, dated run reports, and generated site/state custody.
- The measurement checkout, evidence authoring, U11, mints, step-6 packet, publication, shakedown, and claim windows.
- All live or quiet-machine verification.

## Residual risk

No full canonical suite, live arm, hardware qualification, or quiet-window measurement was run in this read-only seat. The 72-hour recommendation also depends on Ed accepting the explicit 24-hour confirmation deadline and must be recalculated from the actual earliest monotonic deadline at step 2.