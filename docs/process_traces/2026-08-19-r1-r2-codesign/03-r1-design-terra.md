```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Adopt p2-038.3 as a new, inseparable v3 capture identity; preserve v2 only for stored-method verification/replay, and reissue D-079 r5 because the adapter flip changes an r4-pinned estimator source.",
  "workspace": {
    "base_requested": "integration/phase2-transaction@9f7f0917751cd7cdbdd61351c98d2fac6132b9e4",
    "base_mode": "exact",
    "head_start": "9f7f0917751cd7cdbdd61351c98d2fac6132b9e4",
    "head_end": "9f7f0917751cd7cdbdd61351c98d2fac6132b9e4",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "adopt_p2038_3_with_stored_method_replay_and_d079_r5",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "r4 becomes stale when the four adapter v2 calls are flipped",
        "detail": "r4 pins joulewise/adapters/powermetrics.py among its four estimator sources. D-138 requires a new D-079 issuance and dependent-pin migration after this source changes."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Strict verification and claim admission must remain distinct",
        "detail": "Stored p2-038.2 bundles must verify by v2 re-derivation, but direct v2 evidence must be barred from future campaign, floor, whole-window, and claim consumption."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "title": "The existing whole-window red is a required mixed-identity regression",
        "detail": "Its calibration_ledger_custody_invalid refusal is the real v2-measurement/v3-calibration incompatibility; replace the positive fixture with genuine v3 evidence and retain an explicit mixed-era refusal test."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git diff --name-only && git rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)", "9f7f0917751cd7cdbdd61351c98d2fac6132b9e4"]
      },
      "expected": {"exit_code": 0, "tail_regex": "9f7f091"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "tail -n 220 /private/tmp/claude-501/-Users-edr-code-JouleWise/d6206bd4-5fa1-4141-9529-e3e811ea7da4/scratchpad/final-full.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["FAIL: test_d079_real_selector_to_real_reducer_embeds_allowance_once", "AssertionError: False is not true : ('calibration_ledger_custody_invalid',)", "Ran 3726 tests in 1998.216s", "FAILED (failures=16, errors=22, skipped=95)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "calibration_ledger_custody_invalid"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FileNotFoundError: [Errno 2] No usable temporary directory found"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "G1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "This read-only sandbox has no writable temporary directory, so local unittest execution fails during import before the target test runs.",
      "needs": "Replay focused and canonical tests in the writable re-freeze checkout."
    }
  ]
}
```

## Findings

### F1 — Blocker: r4 cannot remain the live acceptance generation after this flip

#### (a) Ratifiable decision

1. Production capture mints the new schema label `p2-038.3`, paired exactly with `powermetrics_native_second_rate_aware_set_membership_v1`. The pair is the capture-pipeline identity; neither field alone is sufficient.

2. `p2-038.2` is not retired or relabeled. It remains the immutable historical v2 identity, with its v2 derivation and trace reconstruction. This follows the D-078 `.1 → .2` precedent: stored bytes retain their stored algorithm; they are not silently judged under the successor.

3. Strict verification dispatches by the stored schema/method pair:

   | Stored identity | Strict action |
   |---|---|
   | `p2-038.1` | Existing D-078 frozen legacy replay |
   | `p2-038.2` + v2 method | Exact v2 raw re-derivation |
   | `p2-038.3` + v3 method | Exact v3 raw re-derivation |

   A crossed pair, unknown schema, or attempt to verify a v2 bundle under v3 fails strict validation. V3 unresolved-anchor fallback traces remain strictly replayable, but never campaign-admissible.

4. The adapter flip changes [`joulewise/adapters/powermetrics.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/joulewise/adapters/powermetrics.py:525), one of r4’s four `estimator_code_sha256` sources. Per D-138, mint `d079_calibration_acceptance_v2_n17_r5`, retaining r3 and r4 byte-for-byte as historical generations. R5 must replay the authenticated 19-member input set, preserve the r4 science outputs, and pin the final adapter bytes. It is a science-neutral pin reissue, not a re-key.

### F2 — Should fix: v2’s historical verifiability does not grant prospective admission

#### (c) Historical-bundle admission policy

| Consumer | Stored v2 (`p2-038.2`) after flip | Required evidence |
|---|---|---|
| Strict verify | Admit as historical evidence only; rederive with v2 and require byte-exact stored clock, phase, trace, and rich telemetry outputs. | Original raw bytes plus stored v2 identity. No v3 reinterpretation. |
| Campaign gate | Refuse unconditionally. | A new capture must carry the exact v3 schema/method pair and satisfy all normal bounded/raw/strict gates. |
| Analysis admission | Permit diagnostic or validation-only replay, never direct prospective/floor input. | If used for D-079 validation, create a separate immutable v3 rederivation record bound to source raw/manifest/event hashes and marked `validation_only`. |
| Floor / whole-window / claim consumption | Refuse direct v2 evidence with new registered D-078 reason `capture_pipeline_superseded`. | No rederivation promotes an old v2 collection into the prospective frozen claim family. Claim use requires a newly captured v3 bundle. |

This distinguishes D-078 correctly: “not re-judged” applies to historical strict replay. It does not mean a falsified rate=1 capture model remains claim-eligible.

#### (b) Exact touch points

Production code:

- [`joulewise/adapters/powermetrics.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/joulewise/adapters/powermetrics.py:525): the four verified v2 execution sites are lines 525, 540, 563, and 755. Also update the import at 41–46, `TIMESTAMP_DERIVATION` at 72–83, and the obsolete v2-only projection docstring at 1832.

- [`joulewise/uncertainty_evidence.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/joulewise/uncertainty_evidence.py:1281): centralize a closed schema → method → full-evidence-deriver mapping alongside the existing v2/v3 registries. The active identity must expose both schema and method, not merely `ACTIVE_CAPTURE_ANCHOR_METHOD`.

- [`joulewise/cli.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/joulewise/cli.py:1215): extend strict dispatch at 1232–1303, fallback endpoint replay at 1536–1557, and rich-telemetry replay at 1560–1615 to all stored current-era identities.

- [`scripts/run_campaign.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/scripts/run_campaign.py:1595): change the campaign gate’s v2 schema/method literals at 1635 and 1644 to the sole v3 production identity.

- [`joulewise/controller.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/joulewise/controller.py:1355): do not relabel a missing adapter result as v3. For powermetrics, omit/mark incomplete evidence so strict validation fails; a fallback did not execute the v3 pipeline.

Claim consumers:

- [`joulewise/analysis_engine/inputs.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/joulewise/analysis_engine/inputs.py:1829): enforce `capture_pipeline_superseded` after strict validation, and correct the stale p2-038.2 comment at 110–115.

- [`joulewise/floor_extraction.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/joulewise/floor_extraction.py:1918): apply the same prospective identity gate before a strict-valid bundle can enter a floor.

- [`joulewise/whole_window.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/joulewise/whole_window.py:710): reject a v2 member before calibration bracket selection; current strict-summary classification at 3159–3187 is not enough.

D-079 / contracts:

- `configs/calibration/calibration_acceptance_d079_v2_n17_r4.json:28–43`: retain unchanged; create r5 rather than edit it.
- [`joulewise/calibration_bracketing.py`](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtR1-terra/joulewise/calibration_bracketing.py:83): add r5 to the multi-generation registry and make it live only after authenticating the final adapter digest.
- `joulewise/arm_readiness.py:4145–4149`: extend issued-generation routing for r5.
- `docs/contracts/run_bundle_layout.md:511–529`, `docs/contracts/powermetrics_fiducial.md:142–175`, and `docs/contracts/analysis_plans.md:260–293`: preserve v2 as historical wording and add the prospective v3/claim-bar rule.
- The D-078 closed registry must register `capture_pipeline_superseded`; using `clock_anchor_unresolved` would falsely claim that a bounded v2 calculation is missing rather than superseded.

### F3 — Should fix: migrate tests and goldens by proving the boundary

#### (d) Migration and FULL GREEN plan

1. Implement stored-identity dispatch and the four adapter-call flip first. Do not soften strict verification or the existing failing whole-window test.

2. Produce and authenticate R5 only after the final adapter source is present. Require r4’s live-pin validation to fail before R5, then require R5 to pass with all four source digests and the unchanged n=17 science result.

3. Replace positive synthetic production fixtures with independently derived v3 evidence. Preserve `tests/fixtures/d117_v2_production` as an immutable historical-v2 fixture; add a v3 fixture rather than changing its label.

4. Convert the current positive whole-window test into real v3 measurement plus real v3 calibration. Add a retained negative test for the present v2-measurement/v3-calibration shape, asserting `capture_pipeline_superseded`, not an accidental custody error.

5. Add attack-shaped coverage:

   - Each of the four adapter paths emits p2-038.3/v3, including no-data and stop-prefix paths.
   - Strict replay passes v2 only under v2 and v3 only under v3; crossed schema/method pairs fail.
   - A copied v3 label on v2-derived evidence fails strict re-derivation.
   - Campaign gate rejects a byte-valid v2 bundle and accepts only v3.
   - Analysis, floor extraction, and whole-window each refuse direct v2 independently.
   - Controller cannot manufacture a v3 label when no v3 derivation ran.
   - R4 staleness and R5 authentication are both explicit tests.

6. Update D-079 golden consumers: `tests/test_calibration_bracketing.py:570–593`, `tests/test_powermetrics_fiducial.py:1545–1560`, and `tests/verify_calibration_acceptance_corpus.py:52–57`. R3/r4 stay historical assertions; R5 becomes the live-generation assertion.

7. Run focused suites, then canonical `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests` in a writable transaction checkout. FULL GREEN means zero failures/errors, including the 16 failures and 22 errors recorded at bb81323—not merely curing the named whole-window failure.

#### (e) Rejected alternatives

- Keep `p2-038.2` and version only the method elsewhere: rejected. It makes one label describe two different derivations and destroys stored-method replay semantics.

- Reject v2 in strict verify: rejected. It erases historical auditability and misapplies D-078’s claim rule to a verifier.

- Treat v2 exact replay as sufficient for future claims: rejected. The rate=1 premise is known false; reproducibility of a superseded calculation is not scientific admissibility.

- Relabel or mutate the 54 stored bundles: rejected. It changes custody bytes and can falsely make an old raw-to-trace product appear v3-derived.

- Leave r4 live after editing the adapter: rejected. R4 explicitly pins the adapter hash, and D-138 makes that staleness a live invariant.

- Re-mint or edit existing freeze receipts in place: rejected. Receipt paths are identity-bearing.

#### (f) Explicit disagreements with the brief

- The campaign gate is not in `cli.py:1644`; that line is nvidia-smi strict replay. The relevant gate is `scripts/run_campaign.py:1595–1645`.

- “Four powermetrics sites” is correct only for the four v2 execution calls. A safe flip also requires strict replay, campaign admission, claim consumers, contracts, and a D-079 reissue.

- R4 is not the terminal acceptance state for this operation. Its adapter digest proves that the requested source edit requires R5.

- `controller.py:1357` is a missing-evidence fallback, not a capture pipeline. Calling it p2-038.3 without a derivation would be a false identity claim.

#### (g) Open questions only Ed can rule

None newly created. The existing Ed-reserved exact-byte approval and publication decision remains required after R5, R2’s separate mint fan-out, and complete successor-family verification.

## Residual risk

The local sandbox cannot execute tests because it has no writable temporary directory. The saved bb81323 canonical log supplies the relevant failure evidence, but final verification must run in the writable re-freeze environment.

For composition with the parked family: R1 must finish before R2 consumes the live acceptance generation. R2 must use R5, not R4. Only after all successor pack bytes are final may the atomic re-freeze mint successor `freeze-0002` receipts at `/Users/edr/JouleWise-measurement-20260818`; existing r2-era receipts remain untouched historical predecessors, never copied or edited in place.