```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Prospectively recharacterize 25G83, shorten acceptance only where local bracket and claim gates preserve soundness, then arm G2-a.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "a4f0d00e304bc4a36599e633486bdb0ea4ecb1f2",
    "head_end": "a4f0d00e304bc4a36599e633486bdb0ea4ecb1f2",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "text": "Replace the three-day, n>=19 default with a prospectively tested one-day acceptance route, contingent on pulse and clock validation; preserve automatic escalation if its fixed gates fail."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "text": "Treat old-epoch exceedances and S>=C as rule-design challenges rather than physical proof that a new-epoch instrument is unusable."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "text": "State that the historical ~1 J example and ~5 J planning figure are not guarantees for 25G83 or arbitrary within-sample physical energy."
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
      "id": "R1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The proposed shorter route changes the operative registration and issuer rules; this seat has made no such change.",
      "needs": "Magistrate and Ed rule on the prospective design before any capture uses it."
    },
    {
      "id": "R2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Calendar dates are conditional floors, not READY findings; no live instrument run or arm check occurred.",
      "needs": ""
    }
  ]
}
```

# Sol 6.0

## Findings

**F1 — Recommended path: A → C → a shorter B.** Resolve the instrument enough to calibrate it; do not make proof of *why* macOS changed the cadence a prerequisite to acceptance.

1. **Desk, now:** replay archived native intervals and exclusions; freeze a diagnostic comparing requested intervals, sampler sets, output paths and observer hooks. The existing analysis found 20,605 raw frames with one-to-one CSV parity, but no independent arrival timestamps, so binary versus scheduler causation remains open. [cadence consult:5–9,28,40–48](docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md) No agents should run during the measurement itself.

2. **Ed’s sudo/hardware quiet window:** run that approximately 35-minute matched diagnostic under a registered plan. If a production-compatible setting restores roughly 0.120 s *native* intervals, validate it with the unchanged 59-pulse and clock protocol. Otherwise validate a deliberately longer pulse, initially 2 s, against measured interval tails, all 59 plateau interiors, edge coverage, anchor feasibility and representative thermal/load states. The current pulse lengths are authenticated only from 0.8–1.2 s, and the detector requires an interval wholly inside the pulse after 0.25 s is removed from each end; a 2 s change therefore needs a new protocol identity and prospective validation. [cadence consult:40–62](docs/process_traces/2026-09-19-activation-a743be05/06-consult-instrument-cadence-astra.md) [fiducial.py:95–103,737–762](joulewise/powermetrics_fiducial.py)

3. **Desk rule and cold gate before collection:** simulate the proposed issuer and later claim path under normal, heavy-tailed and day-varying B and drift; register the chosen protocol, all 12 slots, exclusions, stopping and failure escalation. My proposed fast route is **one 12-slot day with at least 10 valid, resolved captures**, all retained B values included, and no B-driven retries or top-ups. Ten is a proposed operating minimum, not a proved 99.5% distribution-free sample size. Require the simulation to show that the shorter route does not admit a false paper claim through the actual local-bracket, floor and decision-interval gates; if it cannot, register two distinct days before taking the first acceptance capture. The present three-day/19-member rule was selected from historical yield arithmetic, not an error bound: 24 slots projected 16.95 retained and 36 projected 25.4. [preregistration:91–94,143–185](configs/calibration/preregistration_d079_epoch_25g83_rev1.md)

4. **One acceptance window, then desk issuance:** run the frozen derivation session on a census-clean machine; authenticate every ledger and evidence byte; derive the new level, range, sample SD and two-draw prediction; review exclusions and day/state diagnostics; issue through the D-138 atomic successor transaction. If yield or physics checks fail, stop and use the *predeclared* second-day route or repair the instrument under a new registration. Regenerate G2-a bindings and pass fresh-clone, rehearsal and arm checks. The currently issued r7 still names 25F84, and the ordinary validator refuses a live epoch absent from the artifact. [r7 artifact:20–26](configs/calibration/calibration_acceptance_d079_v2_n17_r7.json) [validator:424–434](scripts/validate_powermetrics_fiducial.py) [D-138:9184–9193](docs/decision_log.md) [critical path:68–88](docs/process_traces/2026-09-24-activation-278ebc9e/20b-acceptance-critical-path-report.md)

5. **Science windows:** G2-a first under its registered payload, then the context-rung rails/USB-C calibration night after its own registration, meter alignment, battery and reader-overhead controls, and 32k desk smoke. The existing council set this order but did not verify G2-a READY. [council ruling:18–24,50–54](docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md)

**Why the cadence matters, and why it does not simply double the joules error.** The 25G83 D-079 captures have slot medians of about 0.244–0.254 s versus 0.120 s on the reference, with no evidence of alternate-frame loss. Six invalid first-night captures lacked a complete sampled plateau interior. That is a direct threat to **fiducial yield**; it is not by itself a measured doubling of energy bias. [cadence facts:9–10,18–33](docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/01-cadence-facts.md) The fiducial B is the largest fitted pulse-edge residual **plus** its anchor bound, not one sample width. [fiducial.py:1021–1047](joulewise/powermetrics_fiducial.py)

For a segment with complete support, the reducer computes each interval-average power × its overlap with the segment. A longer interval does not accumulate a 0.245 s error on every sample: only boundary allocation changes for a fixed segment. Ten seconds has roughly 41 such samples and 600 s roughly 2,450, but the important count is the **two boundaries**. [reduce.py:167–180,1865–1878](joulewise/reduce.py) At the historical 33 W phase step, a hypothetical 0.245 s half-cell is about 4.0 J at one edge; 0.120 s gives about 2.0 J. A 0.133 s B corresponds to 4.4 J at that step and 0.173 s to 5.7 J **before** local anchor and bracket terms. Those are scale checks, not calculated floors. The September records contain B values of 0.133 s and 0.173 s; the historical ~1 J example used approximately 31 ms × 33 W. [night-two harvest:59–73](docs/process_traces/2026-09-19-activation-d0b83820/01-n2-20260919-harvest-record.md) [first-night diagnosis:1–2](docs/process_traces/2026-09-19-activation-b165c535/03-diagnostic-invalid-captures-astra.md) [D-078:4758–4769](docs/decision_log.md)

The effective bracket bound is `max(Bpre,Bpost) + max(observed drift,S)`; current reduction also adds the bundle-local anchor term and edge span, then evaluates energy over the allowed shift. Thus a higher measured B can raise a floor and make a small contrast unclaimable, while a long segment’s larger effect may still clear. It cannot inherit the old ~1 J example. More strongly, the later D-078 addendum says these are bounds for the **interval-overlap estimand conditional on held-average reconstruction**, not arbitrary physical power allocation inside a sample. It also withdraws “F+B ≈ 5 J” as an acceptance guarantee; the actual floor and widened decision interval are separate gates. [bracketing.py:2490–2495,2571–2579](joulewise/calibration_bracketing.py) [reduce.py:1712–1732,2064–2076](joulewise/reduce.py) [D-078/D-083 addenda:11268–11303](docs/decision_log.md)

**F2 — Barrier rulings.**

| Barrier | Recommendation | Scientific reason |
|---|---|---|
| Three **distinct days** | Change to one registered derivation day, with a second day fixed *before capture* if desk simulation or state validation requires it. Treat G2-a’s later-day brackets as an out-of-sample challenge, not corpus members. | Day effects are real to test, but three dates cannot prove continuous stability inside a future window. That risk is handled chiefly by local pre/post brackets and fail-closed claims. The current three-day rule is a yield projection. [preregistration:91–94,173–186](configs/calibration/preregistration_d079_epoch_25g83_rev1.md) [D-079:4835–4852](docs/decision_log.md) |
| Retained **n ≥ 19** | Change to **n ≥ 10 of 12**, conditional on pre-capture simulation of the complete admission path; escalate prospectively if it fails. | `Q99 = t(0.995,n−1)·SD·√2` is model dependent. The t multiplier is about 3.25 at n=10 versus 2.88 at n=19: a modest precision cost, not a physical discontinuity at 19. Neither sample size proves a nonparametric 99.5% tail; under iid continuous draws, a future draw exceeds a sample maximum with probability `1/(n+1)`—about 9.1% at 10 and 5% at 19. [preregistration:79–89,173–177,193–207](configs/calibration/preregistration_d079_epoch_25g83_rev1.md) [D-102:6464–6477](docs/decision_log.md) |
| Pulse, SNR, edge and anchor **screens** | Keep; validate any longer pulse prospectively. Keep authentication, complete support, bracket endpoints and uncertainty propagation. | Empty plateau interiors and unresolved anchors occurred in the actual captures; those prevent an interpretable B. [evidence inventory:7–8](docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/03-evidence-inventory.md) [preregistration:156–171](configs/calibration/preregistration_d079_epoch_25g83_rev1.md) |
| Historical **level/range challenge** and `S ≥ C` | Drop the old-epoch exceedance as an automatic **new-epoch** issuance veto; retain it as a reported change diagnostic. Change `S ≥ C` to refuse only when `S > C`, allowing `C = S` with zero drift headroom, or predeclare a coherent successor cap. Never silently lower S. | The 25F84 maximum/range are empirical comparators, not 25G83 physical limits. If `C = S`, a bracket with observed drift ≤ S still carries S once in its operative bound; excess drift refuses. The current strict inequality adds headroom as a condition for existence of an artifact, even when no excess is allowed. [preregistration:188–190,232–250](configs/calibration/preregistration_d079_epoch_25g83_rev1.md) [bracketing.py:2555–2579](joulewise/calibration_bracketing.py) |
| **12 slots/day** | Keep 12 for this short route; drop its status as a universal physical constant. | Twelve fixes the opportunity count and avoids optional stopping; its 128-minute program and 150-minute reserve are machinery constraints. The earlier 11/24 valid yield makes repair/validation the first priority. [preregistration:96–114,143–147](configs/calibration/preregistration_d079_epoch_25g83_rev1.md) [evidence inventory:14](docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/03-evidence-inventory.md) |
| Old-epoch **equivalence rule** | Drop it for this failed 25G83 route; simulate and register a replacement only for a future epoch that uses one. | It compares every new B and the range against historical sample extremes, so it can reject an unchanged population often; the independent review estimated PASS ≈0.48 at m=12. This is distinct from successor issuance. [review:66–70](docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md) [critical path:80](docs/process_traces/2026-09-24-activation-278ebc9e/20b-acceptance-critical-path-report.md) |

**Rules before data.** The 19 September n1/n2 roots may inform diagnostic design, simulations and explicit retrospective sensitivity analysis. They cannot become unseen members of a new prospective corpus: their B values and failed verdict have been read, and Ed expressly ruled that neither night counts. The `qpe01` captures are idle-power pilot envelopes under a different protocol, so they can inform cadence and observer-state diagnostics only. A replacement issuer must explicitly account for the valid prior-set ledger rows, because the present rule refuses valid same-epoch observations outside its registered corpus. [Ed ruling:5–14](docs/process_traces/2026-09-19-activation-a743be05/01-ed-ruling-fail-route-c.md) [evidence inventory:5–16](docs/process_traces/2026-09-24-activation-278ebc9e/22-acceptance-council-packet/03-evidence-inventory.md) [preregistration:156–163](configs/calibration/preregistration_d079_epoch_25g83_rev1.md)

**F3 — Falsifier and dates.** This path is wrong if the validated setting still misses plateau interiors, produces unresolved anchors or wide B excursions; if desk simulation shows false claim admission under plausible drift/tail models; or if the first later-day G2-a brackets fail the new screen or yield claim intervals too wide for the intended effect. The diagnostic, fixed 12-slot acceptance outcome, later brackets and actual floor/claim reduction expose those failures in order. No failed result is made acceptable by trimming a member or changing a threshold after inspection. [preregistration:156–190,250–259](configs/calibration/preregistration_d079_epoch_25g83_rev1.md) [bracketing.py:2513–2553](joulewise/calibration_bracketing.py) [D-078/D-083 addenda:11268–11303](docs/decision_log.md)

With **24 September** as the first diagnostic/validation day and the rule frozen before a **25 September** derivation window, the earliest *conditional* G2-a arm is **26 September** after issuance, bindings and fresh arm checks; the council-ordered calibration night is **27 September** after its own desk gates. Quiet means census-clean at any hour, so a 4–5-window/day ceiling does not itself force another date. A one-day rule that fails its prospective validation moves both dates later; the unchanged three-distinct-day fallback, if begun on 24 September, has only a **26 September capture floor**, not an armable G2-a date. [preregistration:96–114,143–177](configs/calibration/preregistration_d079_epoch_25g83_rev1.md) [critical path:82–88](docs/process_traces/2026-09-24-activation-278ebc9e/20b-acceptance-critical-path-report.md) [council ruling:50–54](docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md)

## Residual risk

The question risks treating *instrument acceptance* as validation of all paper numbers. Acceptance establishes a usable **conditional timing and eligibility system**; it cannot establish missing DRAM/fabric power in CPU+GPU+ANE rails, calibrate the USB-C meter, or bound arbitrary within-record physical energy. The registered calibration night’s adjacent-idle input-power comparison and explicit USB-C boundary label address part of that independent validity problem. [review:52–64](docs/process_traces/2026-09-24-interactive-02a24110/02-fresh-opus-review-verified.md) [D-078 addendum:11268–11283](docs/decision_log.md) [council ruling:20–24](docs/process_traces/2026-09-24-activation-278ebc9e/13-coldgate-packet-407/20-coldgate-fable-council-ruling.md)