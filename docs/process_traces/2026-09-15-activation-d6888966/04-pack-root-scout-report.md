```json
{
  "schema":"claude-codex-report/v1",
  "genre":"scout",
  "status":"findings",
  "completion":"partial",
  "summary":"BUILD is the ruled route after G2-a; generators omit freeze custody, GAMMA emits incompatible root keys, and A5 cannot prove full readiness.",
  "workspace":{
    "base_requested":"3d5b7623",
    "base_mode":"exact",
    "head_start":"3d5b7623a484577c85e07eaefdd217680578bfde",
    "head_end":"3d5b7623a484577c85e07eaefdd217680578bfde",
    "upstream_end":"1d39729c7f4b1dd7b732b9a92f76bad451cadea8",
    "branch":"feat/2026-09-15-pack-root-successor-v5-01"
  },
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"rows":[
    {"row":"GAMMA root-key repair","action":"start_now"},
    {"row":"Production pack generation","action":"wait_for","wait_for":"issued G2-a pin and V5-DESK-DAY-01"},
    {"row":"Roster replacement","action":"needs_ruling"},
    {"row":"Quiet-machine collection in this session","action":"do_not_start"}
  ]},
  "verification":[{
    "id":"V1","kind":"test",
    "cmd":"python3 -B -m unittest tests.test_arm_readiness_registry.ArmReadinessRegistryTests.test_registry_has_complete_unique_35_row_profiles tests.test_d117_floor_qwen3_v5_generate.D117FloorQwen3V5PackTests.test_routing_constants_are_the_only_producer_routing_sources",
    "cwd":".",
    "observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 0.043s","OK"]},
    "expected":{"exit_code":0,"tail_regex":"OK"}
  }],
  "flags":[
    {"id":"F1","kind":"environment","level":"blocking","text":"Read-only filesystem policy prevents temporary copies and genuine generator/clone replay. In-memory inspection used fixture inputs.","needs":"Lead repeats Q2 and Q5 in an authorized writable temporary checkout."},
    {"id":"F2","kind":"baseline_drift","level":"nonblocking","text":"Requested HEAD remained fixed and clean; origin/main was already ahead and advanced concurrently. No network used.","needs":"Revalidate findings on the landing candidate."}
  ]
}
```

## Scheduling matrix

| Row | action | wait_for | collision surface |
|---|---|---|---|
| GAMMA root fields | start_now | — | generator, T-0 tests |
| Three production roots | wait_for | G2-a issued pin | V5-DESK-DAY-01 |
| Freeze/publication | wait_for | generated family, reviewed inputs | all three roots, pinset |
| Roster substitution | needs_ruling | Ed | live registry |

## Critical path

References below: **A** = `joulewise/arm_readiness.py`; **T** = `joulewise/arm_readiness_evidence_t0.py`; **P** = `configs/campaigns/`.

**Q1 — Complete root versus A5 minimum.**

A5 needs committed `plan_tree.json`, its exact GNU `plan_tree.sha256`, and the pack-relative plan, normally `calibration_plan.json`. A:4487–4511 authenticates the tree; A:5737–5822 reads `plan.path`, `plan_id`, optional `actual_sha256`/`declared_sha256`, checks committed bytes and matching plan JSON `plan_id`.

Later T-0 reads:

- `roots.claim_root_leaf/bound_root_leaf` (T:1014–1020);
- `window_identity.window_id/evidence_root_id`, `plan.plan_id` (T:1532–1537);
- `stage_graph[].launch.commands[].argv_template.arguments` for power policy (T:974–989);
- `arm_attachments.arm_readiness.arm_receipt_namespace` (T:900);
- `external_inputs.artifacts[]` and `manifests[].manifest/members[]`, each `path/sha256` (T:1743–1765);
- identity projection declaration, frozen receipt and model/runtime/config inputs through `identity_pins.py:1998,2154,1604` (T:1768–1780).

Full ARM additionally needs the generated inventory in Q2, U11 projection receipt/sidecar, generic evidence receipts/sidecars and their sources, and the plan-pinned D-134 freeze receipt/sidecar. A:4573–4596 requires attachment keys `contract_id`, `required_before_arm`, `row_registry`, `freeze_receipt`, `arm_receipt_namespace`, `pack_digest_algorithm`. Registry reference is `{registry_id,path,sha256,plan_profile}`.

Digest distinctions:

- `plan_sha256` = SHA-256 of exact calibration-plan bytes; pinned by tree declarations and freeze `pack_identity` (A:5592–5607,5814–5820).
- `pack_digest_algorithm` = `joulewise.committed_pack_tree_sha256.v1`. A:3064–3188 hashes **every HEAD-committed pack blob**, including generator, evidence and sidecars. Frame: domain plus byte-sorted relative paths, each `path NUL mode NUL decimal-length NUL SHA256(file) LF`. Disk bytes/modes must match HEAD; extras, missing files and symlinks refuse.
- Registry installs names/policies, not final pack digests. Generic evidence records its derivation-time pack digest; ARM/T-0 bind the completed pack. Freeze binds plan identity and evidence digests, avoiding a self-hash. Final pack expectations also enter family/histsem publication and GO custody. The R1 plan-slot normalization is a dependency-comparison exception, **not** a pack-hash exclusion (A:4814–4857).

**Q2 — Generator execution and inventories.**

Executed, with no pin and no writes:

```text
python3 -B P/d117_floor_qwen3-1p7b_v5/generate_configs.py --output-root /tmp/magistrate-1acf2aee/pack-scout/alpha
python3 -B P/d117_floor_qwen3-8b_v5/generate_configs.py --output-root /tmp/magistrate-1acf2aee/pack-scout/beta
=> each rc=1: generation failed: prefill_prompt_pin_unresolved ...
```

Here `P/` abbreviates the directory defined above. GAMMA with the correct panel/model flags refuses `prefill_length_unresolved` without a length, then `prefill_prompt_pin_unresolved` with `--prefill-length 512`.

Temporary-copy execution was unavailable. Supplemental **in-memory** execution used the test’s synthetic 512 pin and substituted the historical receipt-oracle object because its production replay needs temporary files. Floor `generate()` and GAMMA `_generate()` produced inventories matching `expected_pack_paths()` exactly; this is inventory evidence, not production generation proof.

Compact file lists:

```text
COMMON:
README.md generate_configs.py calibration_plan.{json,sha256}
order_manifest.json plan_tree.{json,sha256}

ALPHA/BETA: 123 files each
COMMON + producer_contract.json extraction_spec.json
decode_prompt_manifest.json decode_workload_candidate.json
condition_families/{decode,p42,p512 definitions} [3]
prefill_pin/prefill_prompt_pin.json
prefill_pin/authority/{prompt-ladder,selection-record}.json
01_phase_decode_absolute/                         [10 configs + order_manifest]
02/03_phase_decode_abba_blocks_{01_05,06_10}/      [20 + manifest each]
04_phase_prefill_p512_absolute/                   [10 + manifest]
05/06_phase_prefill_p512_abba_blocks_{01_05,06_10}/ [20 + manifest each]

GAMMA: 115 files
COMMON + analysis_manifest_v3.json consumer_family_declaration.json
decode_workload_candidate.json prefill_prompt_candidate.json
condition_families/{decode,p512}×{A,B}             [4]
decode_prompt_manifests/{qwen3-1p7b,qwen3-8b}/     [8 each]
01/02_decode_contrast_blocks_{01_05,06_10}/         [20 + manifest each]
03/04_prefill_p512_contrast_blocks_{01_05,06_10}/  [20 + manifest each]
```

Inventory owners: floor generator:3047–3115; contrast generator:1269–1297.

Historical v3 floor roots have 8 top-level files, 106 stage files, 3 families; GAMMA has 10 top-level files, 84 stage files, 4 families. **Each additionally has** `arm_readiness.sources/` [11], `arm_readiness.evidence/` [22], `arm_readiness.freeze.receipts/` [2], `identity_pin_projection.receipts/` [2]. These 37 custody files are absent from generator output. Calibration plans **are generated**. Evidence comes from `scripts/author_arm_readiness_evidence.py`, projection from `scripts/project_identity_pins.py freeze`, freeze from `scripts/generate_arm_readiness.py freeze`; never copy historical receipts.

**Q3 — Admissibility and authority.**

Registry `configs/arm_readiness/d117_row_registry_v2.json:517–536` installs the three names, publication threshold 5 and predecessor bindings. A:420–432 checks approved shapes; A:4520–4537 requires committed registry bytes; A:4573 rejects mismatched plan declarations.

The 14 FREEZE_AND_ARM rows are `clock.restore_recipe` plus `desk.{acceptance_owner,acceptance_successor,arming_procedure,current_pack,estimator_identity,identity_pin_projection,mint_trust,multicell_mint,pack_family,reason_code_plumbing,receipt_oracle,recovery_ledger_path,three_window_regression}`. Successor acceptance is conditional. Eleven ordinary generic kinds cover the currently issued acceptance route, plus specialized U11 evidence.

R1 fields include freshness class/policy, derivation commit, dependency-manifest digest, pack digest, facts/checks/status/reasons/assurance; execution receipts additionally carry boot, deadline and environment fingerprint (A:616–635). Admission checks policy agreement, ancestry, whole-repository changed-set allowlist, dependency replay, boot/expiry/environment and re-derivation where applicable (A:5014–5185,6220–6399). Legacy generic receipts cannot migrate.

The ruled v5 chain uses authenticated **v3 predecessors → freeze-0004**, not freeze-0005 (A:7804–7811,7920–8002). Generate/commit → projection → fresh evidence/commit → freeze/commit → successor histsem pinset → marker/confirmation proof. `docs/contracts/receipt_histsem_verifier.md:310–326` owns publication ordering.

Authority: `docs/decision_log.md:8995` D-134; :10462 D-139; :9269 freeze semantics; :210–213 D-164/165/166/167. D-173’s adopted paper-custody rules (:11363) do not authorize fixture promotion. D-176 (:11451) governs pack-night authorization/GO. Step-6 and transaction GO are already delegated by D-171:10928–10937; no new blanket Ed approval should be invented. Roster changes remain Ed’s, cold-gate 65 ruling `10-coldgate-fable-ruling.md:20`.

**Q4 — GAMMA.**

Yes: `P/d117_contrast_v5/generate_configs.py:1095–1103` derives exactly `P/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5` from panel IDs. Use `--panel configs/model_panels/qwen3_4bit.json --model-a qwen3-1p7b --model-b qwen3-8b`, issued pin and selected length. Preserve the umbrella directory’s registration files.

**Defect:** contrast generator:2697 emits `claim_leaf/bound_leaf`; T:1017–1018 requires `claim_root_leaf/bound_root_leaf`.

**Q5 — Exact future A5 replay.**

After landing, from an allowed local source whose `main` is the accepted commit, on macOS:

```sh
mkdir -p /tmp/magistrate-1acf2aee/pack-scout
PACK_SCOUT=$(mktemp -d /tmp/magistrate-1acf2aee/pack-scout/a5.XXXXXX)
git clone --no-hardlinks --branch main /Users/edr/code/JouleWise-wt-pack-root "$PACK_SCOUT/repo"
mkdir "$PACK_SCOUT/custody"
cd "$PACK_SCOUT/repo"
python3 -B -c '
import json,subprocess,sys
from pathlib import Path
from joulewise import arm_readiness as a
r,_=a.load_registry(Path.cwd())
for role,name in r["freeze_evidence_lifecycle"]["successor_policy"]["successor_pack_ids"].items():
 p=Path("configs/campaigns")/name
 assert a.reviewed_main(p)["exact_match"]
 x=subprocess.run([sys.executable,"-B","scripts/author_arm_evidence_t0.py","--pack-root",str(p),"--custody-root",sys.argv[1]],capture_output=True,text=True)
 print(role,x.returncode,x.stdout,x.stderr)
 assert x.returncode==2
 assert json.loads(x.stdout)["reason_codes"]==["evidence_author_t0_clock_attestation_missing"]
' "$PACK_SCOUT/custody" > "$PACK_SCOUT/a5.trace"
cat "$PACK_SCOUT/a5.trace"
```

Order: CLI strict path resolution → reviewed-main → tree/sidecar (`readiness_pack_unreadable`, A:4493) → committed plan/pack → boot probe → registry/profile (`readiness_row_registry_mismatch`, A:4469) → first clock derivation (`evidence_author_t0_clock_attestation_missing`, T:181,520–538,1134). Main sequence: T:2255–2319. Thus missing-tree refusal precedes profile refusal. Absent GAMMA directory fails even earlier as CLI `evidence_author_t0_io_error`.

**Q6 / disagreement with brief.**

BUILD follows settled science; it is not merely directory repair. `V5-DESK-DAY-01` already owns this work and is hard-blocked on G2-a (`docs/process/state_kernel.json:6949–7029`). READY does not authorize inventing its pin. Floor generators accept only 512; another selected rung requires re-authoring/ruling reconciliation, already disclosed in `2026-09-02-v5-floor-generator/01-sol-landing-report.md:242–245`.

A5 proves neither correct root keys nor freeze readiness. It stops before both. Replacing the roster merely to pass it would pre-empt Ed.

**Lead double-check:** actual issued G2-a custody/selected rung; calibration-head advancement; GAMMA root repair; fresh-head generator replay; all three freeze/publication proofs. No such live evidence was inspected here.

## Delegation contracts

**Q7 — proposed order; no seats launched.**

1. Repair seat: WRITE_SCOPE = contrast umbrella `generate_configs.py`, `tests/test_d117_contrast_v5_pack.py`, `tests/test_arm_readiness_evidence_t0.py`. Pin generated root keys and exercise the later T-0 root check.
2. After G2-a, generation seat: WRITE_SCOPE = the three registry-named `P/<pack-id>/**` roots. Use issued inputs; run generator checks and focused floor/contrast modules.
3. Lead-controlled freeze/publication: same roots sequentially, then exact successor pinset path; authorize trace/kernel paths separately. Preserve predecessors. Add clean-clone three-profile A5 and mutation tests for sidecars, registry identity, plan binding and omitted custody.

Twelve-row inputs: fresh audit; paired contract/execution lenses; dictated fixes; delta audits; signature statements; Opus counter-review; Fable design gate; prune; lead integration full-suite tail; post-change fresh review; final CI/integration review; magistrate exact-head review. `.github/pull_request_template.md:9–20` specifies the evidence format. Full-suite replay belongs to that lead gate, not this scout.