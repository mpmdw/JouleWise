```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "No candidate discharges the current seven-step pre-window contract; G2-b is the correct current-pack modular corpus, but closing full-edge L10 with it would require a cold-gated rescope.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "b28be2553803555eb0e2ba3e8d85e5a275cb14b3",
    "head_end": "b28be2553803555eb0e2ba3e8d85e5a275cb14b3",
    "upstream_end": "b28be2553803555eb0e2ba3e8d85e5a275cb14b3",
    "branch": "feat/2026-09-01-l10-rehearsal-phase"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "text": "No listed corpus can both run all seven ED-FIRST steps successfully and remain a pre-window, same-head production-pack corpus."
      },
      {
        "id": "F2",
        "severity": "blocker",
        "text": "G2-b deliberately stops at analysis_finalization_member_cover_mismatch and therefore cannot prove finalized-manifest creation, analyze-claims, or Results fills."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "text": "The OPEN RULING inaccurately describes ED-L10-1 as a corpus replay that occurred and proved something; its committed record says it remained OPEN and produced no artifact."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "python3 -m json.tool docs/process/state_kernel.json >/dev/null; git diff --check; git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## feat/2026-09-01-l10-rehearsal-phase...origin/feat/2026-09-01-l10-rehearsal-phase"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "## feat/2026-09-01-l10-rehearsal-phase\\.\\.\\.origin/feat/2026-09-01-l10-rehearsal-phase"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "A C1/D-only edit cannot make G2-b satisfy the existing full-edge C2/C3 acceptance; closing L10 requires either a split gate or a cold-gated reversal.",
      "needs": "Rule whether D-162 supersedes the full-edge L10 acceptance or only supplies a separate modular pre-window gate."
    },
    {
      "id": "R2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The off-repository a9/a10 and live G2 custody were not inspected; conclusions are from committed contracts and records.",
      "needs": ""
    }
  ]
}
```

## Findings

- **F1 — blocker:** The current contract is unsatisfiable. The production corpus is the only candidate that can satisfy every seven-step input relation, but it exists too late. Every pre-window candidate either has the wrong pack or cannot pass finalization.

- **F2 — blocker:** G2-b is expressly a one-block proof whose success condition is exact finalizer refusal. It must not create a finalized manifest or claim artifact. Calling it a seven-step full-edge PASS would be false.

- **F3 — should-fix:** ED-L10-1 did not “use” the a9/a10 corpus in an executed replay. The record describes the intended replay, then says no artifact was produced and the row remained open. [ED-L10-1 record:609](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-19-prep-sprint/ready-packet/30-ED-QUALIFICATION-rows.md:609), [status:614](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-19-prep-sprint/ready-packet/30-ED-QUALIFICATION-rows.md:614), [open disposition:626](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-19-prep-sprint/ready-packet/30-ED-QUALIFICATION-rows.md:626)

## Q1. Candidate-by-candidate

The exact kernel fence is:

> “Same head, production pack: a synthetic or smoke-scoped replay does not discharge this row (D-160 R-1 forbids a synthetic clean leg standing in for the real edge)”

[state_kernel.json:1927](/Users/edr/code/JouleWise-wt-l10/docs/process/state_kernel.json:1927)

“Claim-eligible” is an additional §C1 precondition, not part of that exact fence. [v5-l10-rehearsal-phase.md:156](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:156)

| Corpus | Same head | Production pack | R-1: real/non-smoke; no floor relaxation | R-2 clean-proof shape | Current §C1 claim eligibility | Timing |
|---|---|---|---|---|---|---|
| D-160 R-2 tiny quarantined generation | Conditional: yes only if rerun at the transaction head | **No** | **Yes**: real telemetry and real floor cells | **Yes, exactly**: tiny real generation, `fixed_n=1`, decode-only, one ABBA block, zero seams | Only for its own tiny plan; not established against the `_v5` prospective manifest | Pre-window/evening-before |
| Retained a9/a10 | A current-head replay is possible, but the evidence and matching pack are historical | **No**: Qwen2.5 generation, not Qwen3 `_v5` | **Yes**: real, non-smoke evidence | **No**: not the ruled live tiny generation or its fixed-n plan | Historically asserted; current record warns the supersession barrier may make the demanded PASSED basis impossible | Pre-window, but wrong generation |
| `_v5` G2-b | **Yes**, provided the transaction remains at the reviewed G2-b head | **Yes** | **Yes**: real telemetry, real pack, no synthetic or smoke-floor relaxation | **Partial only**: one ABBA block and real bytes, but not a clean end-to-end pass, own fixed-n mini-family, or own floor-cell mint | **No by construction**; never reusable by floor, mint, or claim | Pre-transaction |
| Completed production corpus | **Yes**, if processed before any head change | **Yes** | **Yes** | Not the literal tiny/quarantined R-2 mechanism, though it is stronger evidence for the production transaction | **Yes** | **Fails pre-window sequencing** |

D-160 R-1 rejects a synthetic clean leg and preserves the smoke-floor refusal; R-2 affirmatively selects the live tiny generation as the clean proof. [D-160 ruling:50](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-27-t26/smoke-corpus-consult/04-MAGISTRATE-RULING.md:50)

G2-b uniquely meets the literal kernel fence, but it violates the extra §C1 claim-eligibility sentence. Its own contract says it is diagnostic/non-claim, never consumed by a floor, mint, or claim. [G2 runsheet:10](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:10)

The production corpus meets the evidence clauses but violates §D’s requirement that L10 PASS exist before the first claim-bearing `_v5` launch. [v5-l10-rehearsal-phase.md:336](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:336)

## Q2. What the seven steps actually prove

“Claim-eligible input” and “claim evidence” must remain distinct: L10 may consume evidence eligible for the governed path while all its outputs remain `QUALIFICATION_ONLY_NOT_CLAIM_EVIDENCE`. [v5-l10-rehearsal-phase.md:64](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:64)

| Step | Failure modes exercised | Corpus properties actually needed | Defect a wrong corpus can miss |
|---|---|---|---|
| 1. Strict validation | Missing declared member; structural or raw-to-summary invalidity | **Real:** essential. **Production pack:** essential for current launch/config lineage. **Claim-eligible:** not intrinsically | A tiny/old corpus can validate while a Qwen3 `_v5` bundle’s configuration, manifest, or reducer lineage fails on transaction night. [phase:189](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:189) |
| 2. Reduction | Missing output, overwrite, or output written inside immutable bundle | **Real:** needed for the actual raw format. **Production pack:** needed for current reducer/config semantics. **Claim-eligible:** no | An old corpus can miss a current bundle-layout or current reducer-version incompatibility. [phase:201](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:201) |
| 3. Floor extraction | No report; non-extractable registered cells; wrong manifest/basis/semantics binding | **Real:** yes. **Current floor-producer pack/spec:** yes. **Claim-ready producer evidence:** needed for the clean downstream leg | G2-b is not the floor-producer corpus. An old or diagnostic root can emit a report but leave `_v5` extraction-spec, cell, and basis failures undiscovered until mint. [phase:212](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:212) |
| 4. Mint | Missing output; output-exists refusal; dirty-tree acceptance; pin/input mismatch | **Real authenticated producer evidence:** yes. **Current pinset/input manifest/head:** critical. **Claim-ready cells:** critical | A historical pack can exercise the CLI while missing `_v5` pinset, input-manifest, dominance-sidecar, or custody joins. [phase:227](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:227) |
| 5. Finalization | Failure to emit the append-only finalized manifest; bad member cover, verdict, bracket, ledger, floor, or plan bindings | **Production pack:** critical. **Complete production-pack member cover:** critical. **Claim-licensing verdict:** critical | G2-b reaches only `analysis_finalization_member_cover_mismatch`; it does not prove successful manifest publication or downstream consumability. [phase:241](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:241), [G2 refusal:1150](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1150) |
| 6. Claim gate | Crash; absent artifact; unregistered refusal spelling; evidence/floor/family/multiplicity failure | **Real:** needed for actual metric paths. **Production pack and finalized manifest:** critical. **Governed eligible evidence:** critical | A tiny or old pack can miss the exact two `_v5` contrasts, frozen family/multiplicity, new selectors, and current evidence-root joins. [phase:256](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:256) |
| 7. Results fills | Missing output, `STOP_FILL`, leftover token, or rendered validation failure | **Production `_v5` artifact schemas/registry:** critical. Scientific direction need not be favorable. **Issued governed inputs:** required | An older corpus can exercise the frozen 109-key renderer while missing the `_v5` successor adapter and D-165 close-out inputs. [phase:272](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:272), [artifact gap:20](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-artifact-flow.md:20) |

The global rehearsal also detects head drift, pack-hash drift, missing artifacts, unregistered refusal spellings, and writes outside rehearsal custody. [v5-l10-rehearsal-phase.md:288](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-l10-rehearsal-phase.md:288)

Consequently:

- R-2’s tiny corpus proves a generic real clean suffix, but can miss `_v5` pack-specific joins.
- a9/a10 can at best prove the historical CLI path; ED-L10-1 never actually supplied even that receipt.
- G2-b proves the current-pack prefix through the exact member-cover refusal, but bugs in successful finalization, `analyze-claims`, and Results fills remain able to reach close-out.
- The production corpus proves all seven, but only after collection risk has already been spent.

## Q3. Recommendation and exact amendment

Recommendation: use **G2-b as the pre-window corpus**, but call the result the **D-162 modular contract-prefix rehearsal**, not the existing seven-step full-edge L10 PASS.

That is the only candidate which is simultaneously real, same-head, and bound to the actual `_v5` production pack. D-162 explicitly selected this shape: real pack, one block, real verdict and binding, then exact incomplete-campaign finalizer refusal. [D-162 ruling:25](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-28-live-smoke/proof-consult/04-MAGISTRATE-RULING.md:25)

No amendment to the exact kernel fence is needed. The extra §C1 `claim-eligible` requirement should instead be narrowed.

Proposed replacement for §C1 lines 156–163:

> For the PRE-WINDOW modular gate, `RUNS_ROOT` must be the immutable G2-b shakedown root: real, strict-valid evidence collected at `TRANSACTION_HEAD` from the authenticated production `_v5` pack. It is diagnostic, qualification-only evidence and is never promoted into a campaign, floor, mint, or claim input. It must contain exactly one authoritative passed whole-window verdict, the pre-verdict bracket binding, and the finalized calibration-ledger session plus its reviewed adjacent head pin. `PRODUCER_RUNS_ROOT` remains a distinct real, authenticated floor-producer corpus named by the `_v5` pinset and input manifest; G2-b is not a substitute for that producer evidence. Synthetic and smoke-scoped evidence do not discharge either root under D-160 R-1.

Proposed replacement for §D:

> `V5-TRANSACTION-01` launches no claim-bearing `_v5` window until G2-b and the custodied `l10-sacrificial-rehearsal-record.json` both PASS at the transaction head. For the pre-window record, PASS means Strict validation, Reduction, Floor extraction, and Mint emit their required artifacts, and Finalization refuses with exactly `analysis_finalization_member_cover_mismatch` on the one-block G2-b basis. The record must carry `"proof_scope": "D162_G2B_CONTRACT_PREFIX"` and must not claim that a finalized manifest, claim verdict, or Results fill was produced. After the complete immutable production corpus exists, and before any claim or Results fill is issued, a separate full-edge record must execute successful Finalization, Claim gate, and Results fills.

Those C1/D edits are not sufficient alone. To avoid internal contradiction, the same ruling must also:

- Change C2 step 5 to the exact-refusal oracle.
- Mark C2 steps 6–7 post-complete-corpus, not pre-window ED-FIRST.
- Split C3’s PASS definition.
- Amend the L10 kernel acceptance and the artifact-flow L10 row, which presently still promise a full edge before collection. [state_kernel.json:1907](/Users/edr/code/JouleWise-wt-l10/docs/process/state_kernel.json:1907), [v5-artifact-flow.md:10](/Users/edr/code/JouleWise-wt-l10/docs/process/v5-artifact-flow.md:10)

G2-b already emits:

- A finalized bracket-session ledger and reviewed adjacent head pin, then restages the exact pair. [G2 runsheet:1029](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1029)
- The pre-verdict bracket binding. [G2 runsheet:1055](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1055)
- One authoritative passed whole-window verdict and exact published copy. [G2 runsheet:1083](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1083)

It does **not** emit—and explicitly must not emit—a finalized manifest or claim artifact. [G2 runsheet:1124](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:1124)

Thus its only additional emission should be the hash-bound modular L10 record. No extra verdict, binding, or ledger artifact is missing. Making it produce a successful finalized manifest would require completing all 80 frozen members; that would cease to be G2-b.

## Q4. Reversal or parameter fix?

Argument for parameter fix:

- R-1’s operative prohibition is synthetic/smoke substitution. G2-b is real telemetry on the real production pack and relaxes no smoke-floor rule.
- It preserves R-2’s core anti-seam properties: real bytes, one ABBA block, no synthetic production seam.
- D-162 later confronted the arithmetic impossibility and explicitly changed the live-proof gate to the G1/G2/G3 modular proof; D-167 then installed G2-b and the transaction dependency. [D-162 ruling:37](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-28-live-smoke/proof-consult/04-MAGISTRATE-RULING.md:37), [D-167:10407](/Users/edr/code/JouleWise-wt-l10/docs/decision_log.md:10407)

Argument for reversal:

- D-160 R-2 says **“end-to-end clean proof,”** with a real tiny family, its own real floor cells, and `fixed_n=1`. G2-b has the production manifest’s `n=10` contract and deliberately produces a refusal rather than a clean finalization.
- The L10 authority independently requires “the full claim edge” before any window, not merely reaching an expected refusal. Closing that row on G2-b would delete the successful Finalization, Claim gate, and Results-fill proof.
- G2’s own contract says its PASS “does not mean that any downstream artifact was produced or licensed.” [G2 runsheet:10](/Users/edr/code/JouleWise-wt-l10/docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md:10)

Decision: **G2-b as the D-162 modular pre-window corpus is a parameter/label fix already supported by D-162/D-167. G2-b as discharge of the current full-edge L10 row is a reversal.**

Therefore the one-corpus proposal, if used to close existing L10 without splitting its acceptance, must be cold-gated. The safe ruling is to split the obligations: G2-b gates the transaction pre-window; the completed production corpus gates successful finalization and claim/results issuance post-collection. Do not mark the current full-edge L10 row complete from G2-b alone.

## Residual risk

The retained a9/a10 and future G2-b custody are outside this checkout, so their byte-level validity was not independently verified. The committed ED-L10 record itself says its replay artifact never existed; no contrary closure record was found.