```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "SEAT: Astra 6 — CAP-COUNCIL-25G83-01. Recommend route R, a fresh successor corpus, and corrections to the extrapolation and clock-step claims.",
  "workspace": {
    "base_requested": "e7c8bcc6",
    "base_mode": "descendant",
    "head_start": "00c399da62702f6f79ef70d58618524c1e27b2d8",
    "head_end": "00c399da62702f6f79ef70d58618524c1e27b2d8",
    "upstream_end": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {"id": "F1", "severity": "blocker", "title": "Claim-window clearance needs prospective evidence under the successor instrument"},
      {"id": "F2", "severity": "should_fix", "title": "A1 overstates statistical and cadence evidence"},
      {"id": "F3", "severity": "should_fix", "title": "Clock-span failures do not establish abrupt clock steps"}
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["## HEAD (no branch)"]},
      "expected": {"exit_code": 0, "tail_regex": "^## HEAD \\(no branch\\)$"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --exit-code e7c8bcc6 HEAD -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Recommendations are advisory; no cap value was computed and no file was modified.",
      "needs": "Lead adjudication of sizing, membership, and successor registration."
    }
  ]
}
```

## Findings

SEAT: Astra 6 — CAP-COUNCIL-25G83-01

Citation abbreviations: **A1** = `docs/process_traces/2026-09-27-activation-77b1bee2/70-science-gate/31-addendum-ruling.md`; **G** = sibling `21-science-gate-ruling.md`; **P** = `configs/calibration/preregistration_d079_epoch_25g83_rev1.md`. Recommendations and estimates below are proposals, not established measurements.

**F1 — Route R, with a fresh successor corpus.**

**1. Purpose.** The cap bounds reproducible computational work on pathological loss surfaces. A separate 120-second deadline handles unexpected per-cell cost. It also indirectly limits retained-cell storage; it is not a physical admissibility threshold or comprehensive memory limit. The original 100,000 came from a synthetic trace; 165,000 came from 34 real convergences. (`joulewise/powermetrics_fiducial.py:77–92`, `:665–695`; `docs/decision_log.md:10149–10174`.)

A fixed count is unnecessary in principle: a deterministic formula could allocate work by pulse count and frame geometry. But frames, pulses and duration alone do not predict pruning efficiency: the code prunes according to the observed loss surface. Its exhaustive geometric bound would preserve termination while permitting enormous work. **Inference:** cadence scaling is an engineering model requiring validation, not a bound supplied by physics. I recommend a generous fixed cap over an explicitly supported cadence range first. Either formula or constant changes a pinned file and requires the same D-138 reissue and dependent-pin transaction. (`joulewise/powermetrics_fiducial.py:636–695`; `docs/decision_log.md:10361–10380`.)

**2. Route and cost.** Choose R. Route M requires a credible comparison with abandoned workloads; when the pre-capture abort prevents execution, there is no workload energy to recover. Obtaining it requires a separately authorized diagnostic continuation. M also retains substantial attrition and needs an equivalence criterion, not merely a nonsignificant difference. These are design inferences from A1:148–168.

Budget **at least four 12-slot windows**: two for prospective sizing and two for independent confirmation/fresh derivation, supplemented by usable archived design traces. At 150 minutes per window, that is approximately ten quiet-machine hours. With review and spacing, allow **3–5 calendar days**, conditional on coverage and successful captures; missing cadence coverage or clock failures can require more. This is a planning estimate, not a deadline. (P:99–114, :612.)

**3. Proposed sizing rule, written before computing its value.**

- Scope: unchanged 59-pulse protocol; **per-capture median native frame length 120–140 ms**. Divide into four 5-ms bins, left-inclusive, with 140 ms included in the last.
- Freeze the design roster before count extraction. Permit August raw traces, all 24 September captures, and registered new design captures. Use completed projection counts and frame lengths only. The four clock-unresolved September captures contribute no complete count; never substitute zero. Re-evaluate counts under the final staged estimator.
- Require at least six completed counts per bin, including at least two captures with medians of 139–140 ms. Missing coverage means **no supported cap yet**, not extrapolation.
- Set  
  **C = 1,000 × ceil(2 × maximum completed design count / 1,000).**  
  The factor two is an explicit engineering reserve, not a statistical confidence guarantee. Include every completed count in the frozen roster, irrespective of its B or eventual membership. Unfinished diagnostic projections remain censored; unresolved censoring blocks sizing.
- Freeze C. In independent non-claim windows, obtain at least 24 captures that actually exercise the projection, including coverage of all four bins, with zero cell-cap or wall-deadline stops. Do not count clock-gate bypasses as successful projection tests. Failure returns to a new design round; no quiet upward adjustment.
- Outside 120–140 ms, refuse claim eligibility and record the reason. Report claims as conditional on the supported cadence domain and retain all attempted-bracket dispositions. Extending the domain requires prospective evidence and another ruling.

This avoids relying on a regression extrapolation by requiring actual counts through the upper boundary. It does **not** prove every future capture inside the interval will finish. Retain the deadline and test pathological termination offline. Cell accounting and the independent deadline are established at `joulewise/powermetrics_fiducial.py:533–550`.

**4. Membership.** Use a **fresh corpus** under a successor registration, ideally sharing the independent confirmation captures when that dual purpose is registered beforehand.

Keeping only the old 12 preserves selection by the obsolete cap. Adding the eight retrospectively combines changed eligibility with known outcomes and contradicts their diagnostic-only disposition. Ledger immutability does not logically prohibit a separately identified scientific reanalysis, but such reanalysis is not fresh confirmatory evidence. Preserve every original row and disclose all known B values as design inputs. (`docs/contracts/calibration_ledger.md:3–15`; A1:101–109, :179; P:618.)

**5. Sequence — proposed order.**

1. Complete `dbad7cc7` issuance with all four files unchanged; retain the claim HOLD. (A1:133–139.)
2. Rule on successor membership and sizing. Integrate the cap work and only the reviewed, needed estimator branches into one later D-138 staging tree; finish H4 investigation concurrently.
3. Conduct the three-family full-system audit required by the charge on that integrated implementation **before fresh confirmatory capture**. Fix findings and freeze code.
4. Run the sizing stage; compute and freeze C. Audit the final cap change and registration before confirmation.
5. Run ≥24 qualifying non-claim confirmation captures under that exact code; derive the fresh candidate using preregistered membership and stopping rules.
6. Complete final audit coverage of the candidate, issuance and dependent pins; atomically reissue under D-138. Any derivation-changing repair requires renewed evidence.
7. Close H1/H4 in writing before arming claims. (A1:160–166; `docs/decision_log.md:10371–10380`.)

**F2 — Correct A1’s evidential claims.**

The launch table’s 134.8 ms is a percentile of **individual frames**, whereas the regression predictor is a **capture median**. Substituting one for the other is not a calibrated workload prediction. The warning about extrapolation remains sensible; that numerical example cannot establish expected workload. (P:620–625; A1:81, :170.)

“No selection on B” is stronger than the evidence: nonsignificant association in 20 observations does not establish independence. Nor does applying the same filter guarantee the same population across calibration and workload contexts. (G:80–85; A1:156.) Likewise, zero failures in 24 independent trials still permits roughly an 11.7% one-sided 95% failure-rate upper bound; correlated captures weaken that assurance further. **Statistical inference:** H2 is a commissioning minimum, not proof that the filter vanished.

D-143’s reserve was reasonable operationally, but never guaranteed portability across cadence regimes; its original scout explicitly required recalibration for new classes (`docs/process_traces/2026-08-18-shakedown-first-light/03-budget-calibration-sweep.md:2`).

**F3 — Investigate span failures before changing clock physics.**

Five milliseconds is a frozen error-budget choice, not a universal physical threshold. Keep it for the current method. The span includes wall-versus-monotonic movement **and timestamp acquisition intervals**; failure alone cannot distinguish a step, smooth slew or scheduling delay. (`joulewise/uncertainty_evidence.py:354–372`, `:1090–1125`.)

Cheapest proposed investigation: inspect existing paired stamps and their widths, correlate capture times with retained `timed`/time-service and sleep/wake logs, and check recorded network-time provenance. If insufficient, prepare an ordinary agent-active wall/monotonic logger for mechanism diagnosis, explicitly non-calibration. Do not change clock settings experimentally during calibration. The estimator assumes an affine clock and documents network-time-OFF admission; changing span/rate treatment requires separate method validation. (`joulewise/uncertainty_evidence.py:891–924`.)

## Residual risk

Inspection only: no raw-corpus replay, historical system-log investigation, tests, capture, powermetrics or repository writes. The calendar estimate depends on obtaining the proposed cadence coverage; inability to obtain it must return to council rather than silently narrow the claim.