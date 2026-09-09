```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "No new defect found in the bounded non-issuing landing; arithmetic and registration checks pass, while production custody remains incomplete.",
  "workspace": {
    "base_requested": "e241e0b7",
    "base_mode": "exact",
    "head_start": "720b166c4766bc95eb5328f95696a0716f97f7e7",
    "head_end": "720b166c4766bc95eb5328f95696a0716f97f7e7",
    "upstream_end": null,
    "branch": "feat/2026-09-08-paper-S2"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {"findings": []},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -c \"import tempfile,unittest; tempfile.tempdir='/tmp'; from tests.test_paper_reported_energy import ReportedEnergyTests as T; from tests.test_d117_floor_qwen25_1p5b_plan import D179V5ReportedEnergyRegistrationTests as R; s=unittest.TestSuite(T(n) for n in unittest.defaultTestLoader.getTestCaseNames(T) if n!='test_d173_is_only_evidence_entry_and_fixture_cannot_render'); s.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(R)); r=unittest.TextTestRunner().run(s); print('READ_ONLY_TESTS_OK='+str(r.wasSuccessful())); raise SystemExit(not r.wasSuccessful())\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK", "READ_ONLY_TESTS_OK=True"]},
      "expected": {"exit_code": 0, "tail_regex": "READ_ONLY_TESTS_OK=True"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -c \"import math\nfrom tests.test_paper_reported_energy import synthetic_input\nfrom joulewise.paper_reported_energy import _project_cell\nx=synthetic_input(); p=_project_cell(x['spec']['reported_energy_cells'][0],**x['cells'][0])\nv=2827/300; h=2.262157162798205*math.sqrt(v)\nprint(p['mean_j'],p['interval'],p['lower_j'],p['upper_j'],p['per_token']['j_per_token'])\nprint('roundoff',p['interval']['variance']-v,p['interval']['h_j']-h)\nassert p['mean_j']==42.5 and p['lower_j']==42.5-(h+.6) and p['upper_j']==42.5+(h+.6)\nprint('ARITHMETIC_OK')\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["roundoff 3.552713678800501e-15 8.881784197001252e-16", "ARITHMETIC_OK"]},
      "expected": {"exit_code": 0, "tail_regex": "ARITHMETIC_OK"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Read-only audit: temporary-file fixture integration and full legacy plan suite were not run. In-memory boundary probes and base/head generator comparison were executed.",
      "needs": "Lead reruns filesystem integration checks."
    },
    {
      "id": "R2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "Existing F2 remains blocking for production issuance, not for this non-issuing increment.",
      "needs": "Complete authenticated production joins and registration-before-spec ordering proof before registering issuance."
    }
  ]
}
```

## Findings

None against the bounded landing.

**Arithmetic:** [kernel:246](/Users/edr/code/JouleWise-wt-paper-S2/joulewise/paper_reported_energy.py:246), independently recomputed:

- ΣE=2125; m=42.5 J.
- Sample variances, both dividing by **9**: sᵣ²=55/6; sᵦ²=440/3. Thus sᵣ=3.0276503540974917 and sᵦ=12.110601416389967; blocks are four-member **means**.
- V=2827/300; implemented V=9.423333333333337, differing by +3.552713678800501×10⁻¹⁵.
- ν=9; implemented h=6.944245259576741 J, differing by +8.881784197001252×10⁻¹⁶.
- Kind averages=(0.1,0.2,0.3); B=0.6 J.
- Endpoints=(34.95575474042326,50.04424525957674) J; independent endpoint differences zero.
- Decode ΣE/ΣT=2125/1275=1.6666666666666667. Prefill-p42=2125/2100; prefill-p512=2125/25600.

The pooled regression genuinely has sᵣ≠sᵦ; pooled h=10.068304877749199, versus stratified 6.944245259576741.

**Registration:** Both generators at `:2116` call the same registration builders for all three cell IDs. Metadata agrees after model substitution; literal model-bound bytes appropriately differ. Refusal is pinned at [kernel:89](/Users/edr/code/JouleWise-wt-paper-S2/joulewise/paper_reported_energy.py:89). The [plan test:1634](/Users/edr/code/JouleWise-wt-paper-S2/tests/test_d117_floor_qwen25_1p5b_plan.py:1634) passed; an in-memory generator mutation deleting `projection_registration` made it fail. Independently executing base/head `build_extraction_spec` functions found **all pre-existing spec content byte-equivalent**, including floor members, after removing only the new metadata.

**Custody:** Executed census, supply-map and refusal probes confirm:

- Existing evidence ingress uses mapped roles and authenticated reads at [custody:1395](/Users/edr/code/JouleWise-wt-paper-S2/joulewise/paper_custody.py:1395); synthetic records arrive inside that fixture input. Production joins do not yet exist.
- New validator and whole owner module enter the transitive source census at `paper_custody.py:735`.
- [Renderer:41](/Users/edr/code/JouleWise-wt-paper-S2/joulewise/paper_rendering.py:41) reads only projection cells. Its body succeeded with an unusable mint-report payload; public fixture rendering refused.
- No reported-energy gate exists at `paper_custody.py:655`. Supply-map active roles are exclusively non-issuing fixtures; pending production roles contain no digests.

**Counterfactual table:** Every row’s assertion was inspected. References below are to [tests/test_paper_reported_energy.py](/Users/edr/code/JouleWise-wt-paper-S2/tests/test_paper_reported_energy.py:81). V1 executed all listed tests except `:249`; that row received separate in-memory boundary probes.

| Lines | Actual distinction |
|---|---|
| 81 | Pooled h differs as quantified above. |
| 98,103 | Missing observation/member refuses. |
| 108 | Equal-unit mean=32; changed weights refuse. |
| 115,124 | Zeroing kind moves endpoints inward 0.2 J; omission refuses. |
| 129 | Named prediction substitutions refuse. |
| 139,191 | Invalid token values/scopes refuse ratio; mean remains 42.5. |
| 152 | Mean-of-ratios=2.1239043777715305; substituted projection refuses. |
| 160,225 | Reordering/duplication, including coordinated reported census changes, refuses. |
| 171,201 | Model/phase/pin/basis/validity mutations refuse. |
| 180 | Endpoints, denominator, count and extra-field mutations refuse. |
| 207 | Floor=1000 leaves endpoints unchanged. |
| 214 | Existing B8 validator rejects sibling object. |
| 234 | Both models’ three cells reproduce observed totals. |
| 242,249 | Census/gate assertions pass; raw inputs and fixture rendering refuse. |

## Residual risk

F2 remains exactly the work enumerated at [contract:134](/Users/edr/code/JouleWise-wt-paper-S2/docs/contracts/paper_reported_energy.md:134): authenticate clean-Git selection, prompt-pin and frozen-spec parents; replay the closed mint report; authenticate/admit the exact whole-window row, model, basis and membership; authenticate every strict bundle and transitive file; derive energies, allocated bounds and four token surfaces; reopen the exact census; issue cell-specific projection grants.

Separately, prove the registered source/digest existed **before the spec’s first existence**, then bind that registration to the frozen spec. Current digest equality, ordering text and “spec absent now” assertion cannot establish that historical ordering.

Synthetic `strict_valid` flags, matching hashes and fixture receipts could be overread as provenance evidence, but the landing explicitly labels them non-issuing and leaves the production gate absent. No files changed.