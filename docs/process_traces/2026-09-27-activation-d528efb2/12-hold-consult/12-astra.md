```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Recommend epoch-scoped claim authority, separate diagnostic access, and mandatory authority checks at arm and claim boundaries.",
  "workspace": {
    "base_requested": "8458f797",
    "base_mode": "exact",
    "head_start": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "head_end": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id":"F1","severity":"blocker","summary":"File authentication is being treated as claim authority despite an epoch-scoped hold."},
      {"id":"F2","severity":"should_fix","summary":"Promotion validation permits missing citations and substantive hold text."},
      {"id":"F3","severity":"should_fix","summary":"R7-freeze tests do not distinguish frozen references from the current default."},
      {"id":"F4","severity":"should_fix","summary":"Replay freshness requirement conflicts with production hold enforcement."}
    ]
  },
  "verification": [
    {
      "id":"V1","kind":"test",
      "cmd":"TMPDIR=/tmp/holdc-d528efb2/astra/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_claim_hold_routes",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["Ran 8 tests in 5.568s","OK"]},
      "expected":{"exit_code":0,"tail_regex":"OK"}
    },
    {
      "id":"V2","kind":"other",
      "cmd":"PYTHONDONTWRITEBYTECODE=1 python3 -B /tmp/holdc-d528efb2/astra/probe.py",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["nested mixed policy admitted","flat mixed policy admitted","held bytes authenticate directly; loader refuses; id-only screen returns 0.013701","PROBE_COMPLETE"]},
      "expected":{"exit_code":0,"tail_regex":"PROBE_COMPLETE"}
    },
    {
      "id":"V3","kind":"inspection",
      "cmd":"git status --short --branch",
      "cwd":".",
      "observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)"]},
      "expected":{"exit_code":0,"tail_regex":"^## HEAD \\(no branch\\)$"}
    }
  ],
  "flags": [
    {"id":"G1","kind":"lead_ruling","level":"blocking","text":"The proposed authority contract requires cold-gate adjudication before implementation.","needs":"Rule the epoch selector, diagnostic authority contract, and revised replay requirement."},
    {"id":"G2","kind":"verification_gap","level":"nonblocking","text":"Read-only design consult: focused tests and probes only; no implementation, historical RED runs, full arm, canonical suite, or hardware verification.","needs":"Lead owns implementation and final verification."}
  ]
}
```

SEAT: GPT-6 Astra — HOLD-BY-CONSTRUCTION-01

## Findings

**F1 — BLOCKER: make claim authority a separate, epoch-bound object.**

Citation shorthand: **CB** = `joulewise/calibration_bracketing.py`; **T** = `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/`.

H1 forbids *arming* claim-bearing windows at 25G83, while permitting non-claim evidence collection (`docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md:158–164`). The first ruling enforced a file-ID hold at admission; its addendum retained R7 and moved enforcement into the loader (`T/11-d138-design/21-coldgate-fable-ruling.md:299–322`; `31-addendum-ruling.md:100–166`).

The current primitive authenticates held bytes and returns an ordinary dictionary; the loader alone suppresses it. Operatives also return by ID without a hold check (CB:590–638,1197–1266). Admission chooses the first declared ID, while arm evidence chooses another field (`joulewise/arm_readiness.py:6205–6220`; `joulewise/arm_readiness_evidence.py:895–947`). V2 independently reproduced both mixed-policy admissions and both authority shortcuts. The refuter reports no number reached and explicitly did not execute a full arm (`T/50-d138-issuance-seat/refuters/hold-refuter-2-opus.md:60–68`).

**Design proposal—all recommendations below are inference.** Adopt the epoch-keyed proposal, but distinguish **authentic data** from **permission to use it for a claim**. Moving the existing boolean into the lower primitive would preserve a general escape hatch.

One authority module should:

- Authenticate bytes, pins and derivations into immutable calibration data.
- Issue a separate `ClaimAuthority` only after checking the authenticated calibration epoch, requested operating epoch, continuation chain, and active holds.
- Bind that authority to acceptance digest, operating epoch, operation/window, continuation evidence and hold-policy version. Missing or conflicting bindings refuse.
- Apply H1 to `os_build == "25G83"`, independent of acceptance ID or estimator revision. Thus interim reissues cannot escape through changed identity fields. A continuation cannot grant authority into 25G83; R7 remains usable at its original epoch.
- Require this authority at arm issuance/verification and claim-result issuance/consumption. A dictionary containing `claim_eligible: true`, a diagnostic result, or a previously serialized authority is insufficient without revalidation.

The requested operating epoch matters: merely checking the calibration’s original epoch misses R7 continued into 25G83. Continuations currently append judged epochs separately ( `joulewise/calibration_epoch_continuation.py:348–364`).

**Non-claim access:** use named governance/diagnostic entry points returning a different result type, never `ClaimAuthority`. Authorize capture access from a sealed, registered non-claim plan whose purpose and scope are verified by the entry point. Governance inspection can authenticate data without capture permission. No CLI flag, environment variable, caller boolean, or deserialized purpose string should grant claim authority.

Keep R7 as default. Preserve route-R derivation captures without the old level screen, including capped/abandoned attempts. The addendum explains why screening these captures would recreate selection bias (`T/11-d138-design/31-addendum-ruling.md:96`). Explicitly decouple derivation eligibility from ordinary claim preflight: today the input writer accepts only an epoch-mismatch refusal, so replacing that with a hold refusal would accidentally break it (`scripts/write_derivation_night_inputs.py:146–186`).

**Alternatives:** file-ID lists and checks scattered among callers repeat the failed design. Removing the issued file prevents useful governance work. A loader-only gate cannot cover direct authentication or continuation authority. The separate authority object costs more plumbing but makes the protected property explicit.

**Minimum coherent implementation, proposed:**

- Add `joulewise/calibration_authority.py`: hold policy, data/authority types, sole grant constructor and verifier.
- CB: split `_acceptance_bound_from_authenticated_bytes`; route loader, explicit authentication, operative access, allowance projection and bracket evaluation through it. Keep raw operative lookup private to data validation to avoid recursive authorization.
- `calibration_epoch_continuation.py`: feed authenticated continuation data into that grant decision.
- `arm_readiness.py`: shared policy normalization rejecting disagreement among every supplied ID/path/digest; enforce grants in `generate_arm_receipt` and verification. `arm_readiness_evidence.py`: use the same normalized binding and grant.
- `scripts/run_campaign.py` and the shared controller launch boundary: claim admission must precede the no-marker shortcut, which currently returns immediately (`scripts/run_campaign.py:1866–1879`).
- `scripts/validate_powermetrics_fiducial.py` and `write_derivation_night_inputs.py`: separate claim authorization from diagnostic identity/derivation checks.
- Mechanically migrate operative consumers in `detection_floor.py`, `floor_mint_estimator.py`, and generalized mint; migrate loader consumers in whole-window, analysis and mint to verified authority. Update governance readers to data-only access. These call sites exist at `joulewise/detection_floor.py:2536`, `joulewise/floor_mint_estimator.py:156`, `scripts/mint_floor_artifact_generalized.py:3596`, `joulewise/whole_window.py:508`, and `joulewise/analysis_engine/inputs.py:3123`.

**Counterfactual tests, proposed—not executed:**

| Route | Required discriminator |
|---|---|
| Round 1: R7 declaration, moved default | Hold active: refuse arm and bracket regardless of default. Use `325d9f77` for historical RED. |
| Round 1: manual/no pack | Held-epoch claim policy refuses before child launch; diagnostic plan remains admissible. Test without invoking admission-list code. |
| B-1 | Nested and flat mixed IDs refuse both admission and evidence certification; consistent old-epoch controls pass. |
| S-1 | Direct authenticated-byte call cannot produce held claim authority. |
| S-2 | Variable, integer, environment expression and `**kwargs` cannot elevate diagnostic access. |
| S-3 | ID-only operative access cannot authorize a floor/claim; authenticated diagnostic inspection still works. |
| S-4 | Register a different-ID 25G83 generation and an R7→25G83 continuation in fixtures: neither grants claim authority. Old-epoch R7 still works. |

For each, preserve RED on the vulnerable head or a precisely named gate-removal mutant, then GREEN on the implementation. Positive controls must satisfy unrelated freshness/pin conditions.

**Unknown-route test:** maintain an architectural census of calibration readers, authority constructors and claim sinks. Resolve imports/aliases; reject unclassified dynamic access within that graph. Combine it with runtime file-read tracing and sink tests rejecting fabricated mappings and diagnostic objects. Plant a new helper that reads calibration JSON directly and submits copied operatives: the census must fail even though no known loader call changed. This is stronger than today’s literal-`True` census (`tests/test_claim_hold_routes.py:172–184`).

**F2 — SHOULD-FIX: promotion completeness.**

The verifier checks citations only when both fields exist; H1 presence needs no text (`scripts/promote_calibration_candidate.py:75–119`). **Recommendation:** validate required nested structures first, then authenticate every citation; require prescribed hold entries and canonical text. Add deletion, empty-text and wrong-type mutants. Current committed bytes are not thereby disproven (`T/50-d138-issuance-seat/refuters/contract-refuter-2-astra.md:117–145`).

**F3 — SHOULD-FIX: R7 mutants.**

The four survivors are recorded at `T/50-d138-issuance-seat/mutation2/report.md:111–114`. **Inference:** equivalent under the current default assignment, but a real coverage gap for the promised freeze. Before importing each consumer, substitute a different registered, unheld default; verify predecessor checks, parser defaults and simulation still select R7. Kill all four mutants there.

**F4 — SHOULD-FIX: replay contract.**

The addendum requires freshness with the keyword, but explicit bracket authentication reloads without it (`T/11-d138-design/31-addendum-ruling.md:305`; CB:1337). **Recommendation:** require two observations: production authorization refuses H1; isolated diagnostic evaluation reports calibration freshness while remaining ineligible for claims. Do not propagate an unrestricted bypass through production evaluation.

## Residual risk

**Inference:** a third route remains plausible until authority consumers are migrated and the census is mutation-tested. Python conventions and AST checks cannot prove absence of arbitrary dynamic bypasses.

Trusted epoch provenance is also essential: the capture script accepts a test identity file (`scripts/validate_powermetrics_fiducial.py:2046–2058`). Restrict that seam to synthetic execution; otherwise an epoch hold can inspect a false epoch.

The defensible guarantee is bounded: under authenticated identity and unmodified reviewed code, every supported arm/claim boundary requires the sole authority constructor. Cold-gate adjudication of that contract is the next step.