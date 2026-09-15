# Exhibit C — the live arm-readiness registry's pack naming and the committed pack directories (main 3b53478a)

`configs/arm_readiness/d117_row_registry_v2.json` keys containing 'pack'/'successor':

```json
{}
```

`configs/campaigns/` directories:

- `d117_contrast_qwen25_1p5b_vs_7b_v1` (has calibration_plan.json)
- `d117_contrast_qwen25_1p5b_vs_7b_v2` (has calibration_plan.json)
- `d117_contrast_qwen25_1p5b_vs_7b_v3` (has calibration_plan.json)
- `d117_contrast_v5`
- `d117_floor_qwen25_1p5b_v1` (has calibration_plan.json)
- `d117_floor_qwen25_1p5b_v2` (has calibration_plan.json)
- `d117_floor_qwen25_1p5b_v3` (has calibration_plan.json)
- `d117_floor_qwen25_7b_v1` (has calibration_plan.json)
- `d117_floor_qwen25_7b_v2` (has calibration_plan.json)
- `d117_floor_qwen25_7b_v3` (has calibration_plan.json)
- `d117_floor_qwen3-1p7b_v5`
- `d117_floor_qwen3-8b_v5`
- `exploratory_2026_07_17`
- `metrology_v1`
- `neg8_reference_corpus`
- `p2_015_floors` (has calibration_plan.json)
- `p2_015_smoke`
- `qwen25_7b_decode_floor_v1` (has calibration_plan.json)
- `splitwise_decode_v1` (has calibration_plan.json)
- `window_references`

Registry lines naming successor packs (grep):

```
213:      "configs/arm_readiness/legacy_receipt_histsem_pinset_v5_v1.json",
214:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-acceptance-owner.json",
215:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-acceptance-owner.json.sha256",
216:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-doctrine-pin.json",
217:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-doctrine-pin.json.sha256",
218:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-estimator-identity.json",
219:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-estimator-identity.json.sha256",
220:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-mint-trust.json",
221:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-mint-trust.json.sha256",
222:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-multicell-mint.json",
223:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-multicell-mint.json.sha256",
224:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-pack-authentication.json",
225:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-pack-authentication.json.sha256",
226:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-pack-family.json",
227:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-pack-family.json.sha256",
228:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-reason-code-coverage.json",
229:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-reason-code-coverage.json.sha256",
230:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-receipt-oracle.json",
231:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-receipt-oracle.json.sha256",
232:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-recovery-ledger-test.json",
233:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-recovery-ledger-test.json.sha256",
234:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-three-window-regression.json",
235:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.evidence/evidence-three-window-regression.json.sha256",
236:      "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/arm_readiness.freeze.recei```
