```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "SEAT: GPT-6 Astra — S1-REPAIR-ROUTE-01",
  "workspace": {
    "base_requested": "5283d7d0",
    "base_mode": "exact",
    "head_start": "5283d7d01353b5228102cafcc747e91df442b99d",
    "head_end": "5283d7d01353b5228102cafcc747e91df442b99d",
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
        "title": "Prove one complete claim fixture before authorizing further migration"
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "title": "Replace A3's inadequate builder acceptance and impossible sibling instruction"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["## HEAD (no branch)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^## HEAD \\(no branch\\)$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Further implementation needs a ruled fixture boundary, acceptance demonstration, and revised assertion authority.",
      "needs": "Adjudicate the ordered proposal below before starting seats."
    }
  ]
}
```

## Findings

**F1 — Recommendation: a bounded production-generation prototype, then a pinned corpus plus selective test separation. Do not launch another broad migration.** This is my recommendation, not an authority decision. A3 explicitly stops further rounds when more than five builder consumers meet later refusals; the supplied reports exceed that threshold. [A3:465–470; A:130–147; B:106–108.]

Citation aliases: **R** = `/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/`; **A3** = R`31-coldgate-returns-ruling.md`; **A** = R`25-r2-seat-A-report.md`; **B** = R`24-r2-seat-B-report.md`. Other paths are candidate-relative.

**Diagnosis**

The remaining failures are a dependency chain, not approximately 100 independent battery defects. Floor roots are separate evidence from experiment members; fixing the latter does not populate the former. [A:134–146; `joulewise/analysis_engine/inputs.py:1850–1899`.]

| Predicate | What must exist |
|---|---|
| Environment admission | Registered policy binding; a snapshot whose eligibility and digests recompute; valid admission attempts before measurement, final admission within 600 seconds; timestamped idle telemetry contained inside its attempt; post-run observation after measurement, explicitly captured, displays asleep and screensaver disengaged; uninterrupted nominal thermal records through window end. [`joulewise/environment_admission.py:30–63,127–215,246–403`.] |
| Idle admission | Sufficient CPU telemetry with p95 busy/power below policy limits, passed GPU admission, consistent final attempt ledger, known adapter wattage and continuity evidence. NEG-8 additionally needs governed reference bundles and derived bounds, with resolved matching OS/power/calibration identities inside the 86,400-second validity horizon. [`joulewise/idle_admission.py:392–597`; `scripts/run_campaign.py:5115–5124`; `joulewise/whole_window.py:134–136,1299–1367,3743–3788`.] |
| Anchor, cadence, clock | Native integer elapsed times and whole-second labels consistent with ordered wall/monotonic stamps; bounded uncertainty without fallback; finite ordered energy envelopes. Cadence is duration divided by the greater of p95 sample gap and endpoint bracketing gap; thresholds are 4 for request windows and 2 for short windows, with three samples where required. Clock bound must not exceed one-quarter window duration. [`joulewise/uncertainty_evidence.py:974–1019`; `joulewise/analysis_engine/inputs.py:183–225`; `joulewise/reduce.py:116–118,970–998,1072–1102,2328–2348`.] |
| Floor custody | Every named absolute/comparative member must resolve under its declared root, authenticate battery evidence, pass strict validation and source/telemetry checks, and supply bundle/config hashes and the named metric. A descriptor-only directory cannot substitute. [`joulewise/analysis_engine/inputs.py:1850–1956`.] |
| Provenance | Known, clean, unchanged source snapshots; workload provenance checked by strict validation; registered production claim-bearing policy and recomputed whole-window evidence. Preserving a stored “passed” label is insufficient. [`joulewise/publication_privacy.py:537–609`; `joulewise/cli.py:707`; `joulewise/whole_window.py:4400–4514`.] |

**Production feasibility — inference from these interfaces:** none of those software predicates inherently requires touching hardware during a test. Parsers, controller writers, reducers, reference-bound derivation, extractors and minters can operate on injected observations. Physical truth—whether the laptop actually floated, stayed quiet, or obeyed the clock model—does require real capture. A successful synthetic test proves software behavior conditional on its inputs, not those physical facts.

There is a concrete obstacle to extending today’s builder unchanged: it uses `FakeClock`; the controller deliberately writes `capture_skipped=True` for post-run environment capture, which the consumer rejects. A newly ruled clock/command replay arrangement must exercise the actual observation path; changing the skipped flag afterward is not a repair. [`tests/bfgs_fixtures.py:129,167–169`; `joulewise/controller.py:2328–2353`; `joulewise/environment_admission.py:57–63`.]

Source cleanliness is another independent constraint: production samples the actual source checkout. Per-test generation from an edited checkout can correctly become claim-ineligible. Generate from a clean recorded revision; never patch eligibility. [`joulewise/bundle.py:767–843`; `joulewise/publication_privacy.py:537–609`.]

**Routes — estimates and judgments below are inference, not measured commitments.** A seat-round means one bounded implementation assignment; review is additional.

| Route | Soundness, estimated size, recurrence risk |
|---|---|
| **(a) Extend generation end to end** | Viable if injection stops at primitive command, clock and runtime inputs and all downstream writers/checkers remain real. Production writers alone cannot prevent physically inconsistent synthetic inputs. Approximately **3–5 seat-rounds**; high recurrence risk if migration precedes a complete demonstration. |
| **(b) Generate and pin a synthetic corpus** | Preferred distribution mechanism after (a) proves feasible. Digests freeze bytes, not truth. Include generator, primitive transcripts, source revision and explicit synthetic identity outside production evidence; prohibit publication use. Approximately **1–2 additional seat-rounds**; lower repeated generation/dirty-tree risk. Replay must preserve historical timing relationships, not silently refresh evidence. |
| **(c) Separate test responsibilities** | Appropriate for pure calculation/classification tests: retain public-boundary refusal coverage and move numeric assertions to direct calculation tests; retain representative successful public flows on (a)/(b). Unsound if an expected successful claim is merely rewritten as refusal. Approximately **2–3 seat-rounds**, lower risk after a named coverage map. |
| **(d) Split S1 by consumer** | Leaving any callable claim consumer without the gate leaves a claim path ungated and violates the supplied #421 constraint. Safe only if deferred consumers are disabled fail-closed; that sacrifices functionality rather than repairing coverage. Approximately **1–2 seat-rounds plus review**, with substantial integration risk. |
| **(e) Replay genuine captures** | Useful independent acceptance evidence if a complete eligible corpus exists. Do not retrofit missing battery readings into old captures. Approximately **1–2 packaging seat-rounds if available**; otherwise an unestimated, lead-controlled quiet capture. It reduces synthetic-model risk but introduces availability and custody costs. |

**Ordered proposal — requires ruling**

1. **Authorize one feasibility assignment only:** produce the smallest *valid* dependency set reaching successful floor extraction, minting, binding and final analysis through public paths. Include required reference cohorts, not one isolated bundle. Accept only included/estimable members and nonempty outputs; record every refused predicate.
2. **Stop that assignment** upon needing an unruled production change, predicate replacement, hand-written derived evidence, or inability to close the dependency set within its budget. Return a concrete obstruction; do not start migration.
3. **After demonstrated success**, generate the pinned corpus and migrate tests by subject. Require negative controls for battery corruption, missing custody, stale reference bounds and failed environment admission.
4. **Lead closes** with assertion/coverage reconciliation, permitted golden leaf diffs, repins, canonical suite and independent review. Any newly discovered production defect returns for ruling.

Before seats start, rule exact paths and budget; permitted primitive injections and clock mechanism; corpus generation/replay semantics; synthetic provenance labeling; each allowed assertion change; and whether new numerical goldens may replace old synthetic values. These are proposals, not scope grants.

**F2 — A3 needs correction in two places.**

Its builder acceptance proves battery passage and strict validation, but not claim admissibility. The ruling acknowledged the uncertainty yet commissioned broad migration. Replace that acceptance with the complete demonstration above. [A3:106–126.]

Its instruction to call the mock barrier’s “own function” is inapplicable where the barrier is inline. Rule an equivalent direct-input test or a narrowly extracted seam; do not demand an unavailable function. [`joulewise/analysis_engine/inputs.py:1938–1944`; A:93–97.]

I support A3’s stop rule and prohibition on fabricated derived evidence. Its extractor/validator schema repair addresses a genuine producer-reader mismatch. [A3:214–220,465–470.]

## Residual risk

Inspection only: no tests, captures, battery reads, or file writes. End-to-end synthetic feasibility and the exact remaining count were not independently executed; reported failures are attributed to the supplied reports.