```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The battery gate is intact; the remaining tests need a ruled claim-evidence strategy, not another broad fixture round.",
  "workspace": {
    "base_requested": "5283d7d01353b5228102cafcc747e91df442b99d",
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
        "text": "The ruled FakeClock builder cannot create claim-ready environment evidence: the controller explicitly records skipped guard and post-run observations."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "text": "A3 generalized one strict-bundle builder to claim-path tests before establishing that it could satisfy later window, floor, and provenance predicates."
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
        "tail_regex": "HEAD \\(no branch\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "A3's round-2 stop conditions were met; a third repair round needs a new ruling on test purpose, synthetic evidence, scope, and acceptance.",
      "needs": "Cold judge rules the route before seats start."
    }
  ]
}
```

SEAT: Sol 6.0 — S1-REPAIR-ROUTE-01

## Findings

**F1 — A valid bundle is not yet a valid claim window.** The current builder runs the production controller with replayed powermetrics and a synthetic battery reading; it does not supply campaign policy, preflight, or calibration inputs (`tests/bfgs_fixtures.py:101-173`; `joulewise/controller.py:239-253`). Its `FakeClock` is a decisive limit: the controller writes `capture_skipped: true` for admission guards and leaves the post-run observation time absent, while the claim validator requires unskipped guards and a post-run observation after the measured window (`joulewise/controller.py:1202-1219,2328-2353`; `joulewise/environment_admission.py:193-206,459-477`). Strict validation and battery `pass` therefore cannot establish claim readiness. Seat A reports 64 integration outcomes and seven campaign IDs still failing; seat B’s golden extraction excludes all five members (`30-s1-repair/25-r2-seat-A-report.md:128-147`; `30-s1-repair/24-r2-seat-B-report.md:100-108`).

| Later predicate | What it needs; hardware-free test route |
|---|---|
| Environment | An eligible policy-bound snapshot, ordered admission attempts, unskipped before/after guards, timed rich telemetry, and post-run observation. A test could feed coherent synthetic observations **through production writers**, using a real-clock-shaped run and injected collectors; the present `FakeClock` writer cannot do it. Actual environmental truth requires capture (`joulewise/environment_admission.py:127-206,406-502`; `joulewise/controller.py:990-1031,1202-1219`). |
| Idle and NEG-8 | CPU busy and combined-power samples, GPU idle verdict, known stable adapter wattage, valid attempt ledger, and compatible start/end reference energies with a fresh drift bound. The pure evaluator accepts injected records, so a synthetic *structural* test is possible; an actual idle or drift claim needs observed hardware (`joulewise/idle_admission.py:1-24,392-465`; `scripts/run_campaign.py:5085-5128,5153-5222`; `30-s1-repair/25-r2-seat-A-report.md:144-147`). |
| Anchor, cadence, clock | Raw powermetrics stamps must agree with causal clock stamps; the reducer requires enough in-window samples, adequate cadence, a bounded clock term, and per-metric energy envelopes. Coherent raw replay plus production reduction can test these checks; a true measured bound needs a real capture and its calibration (`joulewise/reduce.py:970-998,1743-1811`; `joulewise/analysis_engine/inputs.py:3484-3551`; `joulewise/floor_extraction.py:2121-2141`). |
| Floor custody and provenance | Every referenced floor root must contain the named bundle and authentic metadata; current summaries need eligible source provenance. Whole-window evaluation bases bind member config, metadata, and summary digests. Production floor/window writers can derive these from synthetic bundles in tests, but fabricated directory placeholders cannot stand in for them (`joulewise/analysis_engine/inputs.py:1639-1691,1894-1899,993-1010`; `joulewise/whole_window.py:4884-4951`; `30-s1-repair/25-r2-seat-A-report.md:132-138`). |

**F2 — A3’s method was too broad, though its stop rule was right.** A3 correctly forbade hand-written missing evidence and predicate replacement, and required a return when the builder met a later refusal (`30-s1-repair/31-coldgate-returns-ruling.md:124-126,439`). Its claim that replacing corpus members with this builder while retaining assertions was a general repair method was premature: the builder starts from one example config, replays one sample, and uses `FakeClock`; A3 had not converted an integration corpus end to end (`tests/bfgs_fixtures.py:118-169`; `30-s1-repair/31-coldgate-returns-ruling.md:124-126`). The exceeded thresholds require the cold-gate return A3 specified (`30-s1-repair/31-coldgate-returns-ruling.md:465-472`).

## Routes and recommendation

| Route | Soundness and cost (estimates are inference) |
|---|---|
| **A. Extend per-test production building** | Sound for structural claims if injected observations are causally consistent and the predicates remain unchanged. It needs a real-clock-shaped writer path, then window and floor writers. Estimate **3–5 seat-rounds**; high risk of another same-signature round because each test may expose another omitted layer (inference from the round-2 returns). |
| **B. Produce a digest-pinned synthetic claim corpus once** | Best common input for genuine claim-path integration tests. Generate it through production writers, record its synthetic origin, pin every byte, and keep it inside test custody; passing it proves code behavior, **not** a real measurement. Estimate **2–3 seat-rounds** after a one-scenario feasibility proof; moderate risk (inference). |
| **C. Re-scope tests by subject** | Sound when a test about classification, transport, or an earlier refusal asserts the S1 refusal at that boundary and a sibling preserves the displaced numeric or barrier assertion. It cannot replace all positive claim-path tests. Estimate **1–2 seat-rounds** plus review of each R-list entry; low same-signature risk (inference; precedent in `36-s1-regression-consult/21-coldgate-fable-ruling.md:105-110,244-247`). |
| **D. Split S1 by consumer** | Landing any claim consumer before its gate leaves that claim path ungated and conflicts with directive #421. A split is sound only if every unfinished consumer is also unable to issue a claim artifact; that requires a separately proved issuance lock. Otherwise reject it (inference from the strict call-site rule in `36-s1-regression-consult/21-coldgate-fable-ruling.md:79-101`). |

**Rule before seats start:** approve a per-test purpose/R-list census; permit synthetic observations only at production *input* seams; decide whether a test-only corpus may pass claim predicates; grant exact writer and fixture paths; and retain unchanged predicates, mock refusal, and a ban on treating corpus numbers as live evidence. Then prove **one** representative environment → idle → whole-window → floor → analysis path with production writers. Stop if that path needs a predicate waiver, hand-authored custody, an unruled production change, or cannot produce a golden report with admitted members. If it passes, generate and pin route B, apply route C to tests with other subjects, then run focused modules and the full guarded suite. This is a proposed ruling, not an existing authorization (inference from `30-s1-repair/31-coldgate-returns-ruling.md:465-472`).

## Residual risk

No tests were run in this read-only consult. Synthetic evidence can exercise consistency checks but cannot verify battery float, quiet environment, instrument calibration, or energy values on this laptop; those conclusions still require a real capture (inference from `joulewise/bundle_read.py:282-360` and the physical inputs named above).