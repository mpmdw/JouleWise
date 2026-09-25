# PROPOSED equivalence-night replacement

**Status: PROPOSED.** This is a desk design under R-Q4(a), not a registered or installed admission rule. M1 requires registration before any night whose admission uses it. The existing rule remains operative until that gate.

## What the rule would decide

The **old corpus** is the set of valid, resolved timing-bound values in the acceptance generation already in force. The **new night** contributes m valid, resolved values authenticated from its closed ledger session. A **refusal** means m is below the minimum or the required old-corpus sample is too small; the rule makes no equivalence judgment. A **PASS** asserts that the new mean is close enough to the old mean and that the two sample variances are close enough by the declared ratios. A **FAIL** is a completed judgment that at least one of those two requirements did not hold.

The **mean-equivalence margin** Δ is measured in units of σ, the standard deviation of the block's local error. The **TOST** procedure is two one-sided tests of whether the mean difference lies strictly between −Δ and +Δ. It passes when the two-sided 90% t interval is wholly inside that open range at one-sided α=0.05. The simulated standard error uses the old and new sample variances divided by their sample sizes; the degrees of freedom are the smaller of old n−1 and m−1, a conservative choice compared with the usual Welch approximation. The **variance ratio** is new sample variance divided by old sample variance. Its screen passes if it lies within [1/B, B], where B is the registered ratio bound. Both screens must pass. The simulation calls the repository's `student_t_quantile` for the interval and runs this proposed decision in [sim.py](sim.py); no production code is changed.

## Proposed parameters and operating characteristics

**Candidate for later registration:** old n≥17, retained m=12, mean margin Δ=3.5σ, one-sided α=0.05, variance-ratio bound B=20. An authenticated night with fewer than twelve retained captures is INCONCLUSIVE under this proposal. An old corpus below seventeen also refuses. For a concrete physical candidate, the sample standard deviation of the seventeen `b_fiducial_s` members in `configs/calibration/calibration_acceptance_d079_v2_n17_r7.json` is **0.002460856207694636 s**. Thus Δ would be **0.008612996726931225 s** (about 8.613 ms). The later registration must authenticate that corpus and freeze this conversion before seeing a new night. The desk model treats σ as a local-error scale; the empirical corpus spread can also contain night-level variation, so the physical conversion is a proposal, not a validated tolerance.

The operating target is **false FAIL ≤5% under no change** for each declared model at old n=17 and m=12. The measured maximum was 1.33% (heavy-tailed model, 8/600); a one-sided 95% binomial upper bound is about 2.5%, still below the target. The named detection target is **≥95% power for a +5σ mean shift** at those sample sizes. The measured minimum was 97.83% in the shared-plus-local model. These are model-conditional simulation targets, not guarantees for a different physical process. Candidate B=10 missed the false-alarm target in one 600-trial heavy-tail cell (5.17%), so B=20 is the selected desk candidate.

At old n=17 and m=12, each row contains 600 trials per state. "PASS" on a changed state is a false admission; one minus it is detection power. The 90% coverage column is for the ordinary mean-difference interval used by TOST.

| Model | No-change PASS | +3σ PASS | +5σ PASS | ×4 variance PASS | 90% interval coverage, no change |
|---|---:|---:|---:|---:|---:|
| Gaussian | 0.998 | 0.435 | 0.005 | 0.930 | 0.568 |
| Heavy t3 | 0.987 | 0.463 | 0.007 | 0.902 | 0.562 |
| Linear drift | 0.998 | 0.432 | 0.002 | 0.918 | 0.633 |
| Shared plus local | 0.995 | 0.492 | 0.022 | 0.882 | 0.335 |

False-admission rates for +5σ are 0.002–0.022; missed-effect rates for that change are the same PASS rates, because PASS misses the change. Under no change, false FAIL ranges 0.002–0.013. Refusal is zero at old n=17/m=12 and one at old n=12 or retained m<12. The current rule's no-change PASS at old n=17/m=12 ranges 0.387–0.455, so its false FAIL ranges 0.545–0.613. The proposal's variance-ratio criterion detects only 0.070–0.118 of fourfold variance changes in these models.

## Registration requirements and limits

The future registration must freeze the physical seconds margin, the exact old-corpus membership and old n, the method for retained captures and their minimum m, Δ, α and B before looking at the new night. It must state whether the old and new samples represent independent nights and how multiple nights are handled. The data here show that an ordinary within-night t interval undercovers when old and new nights have separate common shocks; simulation-calibrated false-alarm rates are the immediate design evidence, not a guarantee of nominal interval coverage. The variance-ratio screen is deliberately broad to hold the no-change false-alarm target under heavy tails and therefore has limited power against a fourfold variance increase. A changed variance alone can pass. The proposal cannot be used as a general absence-of-change claim without a narrower registered model or additional independent nights.

The production `epoch_equivalence_check.evaluate_session` was called for the old numerical verdict using synthetic retained rows. Its ledger authentication was not exercised. The proposed rule has no production implementation. The later registration and code change must use actual authenticated ledger values and must undergo its own gate before any night is admitted with it.
