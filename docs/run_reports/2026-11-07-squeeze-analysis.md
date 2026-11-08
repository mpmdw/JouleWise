# Squeeze analysis desk handoff — 2026-11-07

**DRAFT / SYNTHETIC ONLY / LOCAL COMMITS ONLY.** Branch:
`align/2026-11-07-squeeze-analysis`. Implementation commit: `3dabcc824`.
This report is a subsequent documentation commit. No push, registration,
measurement, weight download, network call or real-data analysis was performed.

## Scope and intake

The explicit user task selected this [AGENT] research tooling lane over the
historical queue. M0 intake found no active stop card or global selection gate;
the initial clone was clean and already on the requested branch, tracking
`origin/main` at `fdb1e0409`. No new task was registered. The user prohibited
coordination-state writes and full-suite runs, overriding normal close-out and
verification instructions. RUN_STATE.md, TASK_QUEUE.md,
docs/process/state_kernel.json and tests/test_gen_state.py are unchanged.

Read authority: AGENTS.md, CLAUDE.md, M0, targeted state/queue/decision sections,
orchestration, AGENT_PLAN.md, docs/research/AGENDA.md and energy-tripwire.html.
Used these already available local refs; the conflicting fetch instruction
was superseded by the binding no-network rule:

| Ref | Local object |
|---|---|
| lane/2026-11-06-v4-r1-integrated | e901eb2a480d51377a494be9d797733dfcd0220b |
| research/2026-11-07-literature | 16e1db6230a80a605d084f0f9f61431d541b793f |
| research/2026-11-07-w1-prearm-gate | 53a2305982a551ba5285e50bd0177726b5f138e7 |
| research/2026-11-07-research-program | 7f74dd2a97e5fcf078652deef2fb291929dc4524 |

The protocol remains provisional; this work does not install its pending
rulings or clear its W1 gate. No path named in an external data config was
followed. The long blinded job was not inspected, signalled or invoked.

## Delivered

- Strict max-of-m and separate split-conformal calibration, conservative ties,
  invalid-score refusal, marginal/tolerance/cohort false-alarm bounds, frozen
  joint-score fusion, rectangular monitor × energy detection surfaces and
  Pareto frontiers.
- Both fixed five-term forms: protocol v4's sequence design is primary;
  energy_residual.md's older context-product row design is explicit sensitivity.
  Hidden continuation energy includes the quadratic H term. No sixth fitted
  term or duration predictor was added.
- Work-conserving padding/relabeling, smoothing-cost and tool-shifting models;
  combined finite-grid adaptation sees each calibration threshold and chooses
  attacks on independent search draws. Evaluation uses a different RNG stream.
- Residual SD 19–58 J including a 2 J replay component, correlated channels,
  Student-t sensitivity and shared-task replay pairs.
- Power integrated over random calibration maxima, including cohort variation
  from sharing a threshold. Results distinguish per-episode detection, any
  cohort alarm, and at least 80% of the cohort alarming. MC uncertainty uses
  independent trials rather than treating all cohort episodes as independent.
- CLI JSON sweeps with explicit required held-out n, seeds, assumptions,
  attack grids, effect accounting and provisional flags; an optional NumPy
  dependency extra; usage and authority in the package README.

Changed files: `pyproject.toml`; `joulewise/align/__init__.py`;
`joulewise/align/squeeze/{__init__.py,__main__.py,detection.py,residual.py,adversary.py,power.py,README.md}`;
`tests/align/__init__.py`;
`tests/align/squeeze/{__init__.py,test_detection.py,test_adversary.py,test_power.py,test_cli.py}`;
and this report. No existing estimator, pipeline or registration changed.

## Numerical implications, conditional on stated assumptions

One frozen joint score calibrated at its benign maximum has marginal FPR
at most 1/(m+1), assuming exchangeability and a genuinely frozen score:

| m | Marginal bound | 90% upper tolerance bound for realized FPR (iid) |
|---|---:|---:|
| 20 | 4.762% | 10.875% |
| 28 (public pilot pool) | 3.448% | 7.894% |
| 39 | 2.500% | 5.733% |

At m=39, a .05 split-conformal rule instead takes rank 38. It is distinct from
the requested maximum rule. ORing two separate channel maxima only guarantees
the sum of their marginal bounds. These are mathematical statements about
exchangeable units, not a declaration that v4's dependent/windowed scores
meet their premises.

The illustrative sweep uses n=40, 512 independent calibration trials per row,
256 search draws/trial, seed 20261107, all default CLI coefficients and
one latent monitor score unit per 128 visible malicious tokens. **Neither
the coefficients, monitor response, attack efficiency ratios nor n=40 is
a registered hardware fact.** The lead's documents approve a separate locked
cohort but do not specify its size; a clarification was requested, and the API
therefore requires n explicitly.

Per-episode joint detection under the combined attack grid:

| m | Residual SD J | H tokens | Detection | MC SE | P(at least 32/40 alarms) |
|---|---:|---:|---:|---:|---:|
| 20 | 19 | 256 | .403 | .009 | .025 |
| 20 | 19 | 512 | .888 | .005 | .840 |
| 20 | 58 | 512 | .583 | .009 | .172 |
| 20 | 58 | 1024 | .987 | .002 | .992 |
| 39 | 19 | 256 | .295 | .007 | .004 |
| 39 | 19 | 512 | .833 | .007 | .729 |
| 39 | 58 | 512 | .495 | .008 | .057 |
| 39 | 58 | 1024 | .976 | .002 | .988 |

Thus these assumptions do not support an 80%-power claim for H=512 at the
high-noise end. H=1024 is much stronger in this finite attack grid. This does
not establish a main-track robustness claim. Search approximation can weaken
the simulated attacker, making measured detection optimistic for security.

Counterexamples are implemented and tested: wholly logged opaque malicious
work has zero monitor/energy shift; off-meter opaque tool work likewise can
escape both; fabricated logged counts can cancel an energy residual. The
squeeze requires additional visibility/count-integrity/physical-boundary
assumptions. Honest executed padding alone does not cancel hidden joules.

## Verification and reproducibility

Ran each module separately, sequentially, never the full suite:

| Command suffix after `-B -m unittest` | Python 3.14.6 + NumPy 2.2.6 | Python 3.13 (NumPy absent) |
|---|---|---|
| tests.align.squeeze.test_detection | 13 PASS | 8 PASS, 5 skipped |
| tests.align.squeeze.test_adversary | 20 PASS | 20 skipped |
| tests.align.squeeze.test_power | 10 PASS | 10 skipped |
| tests.align.squeeze.test_cli | 4 PASS | 2 PASS, 2 skipped |

Totals: **47 numerical/functional tests pass on 3.14**; **10 pass and 37
explicitly skip on bare 3.13**. Each module completed in under 0.4 s in the
final replay. Python 3.11 is unavailable. Also passed:
`python3.13 -B -m compileall -q joulewise/align tests/align` and
`git diff --cached --check`. No MLX code or MLX-native tests were needed.

The synthetic sweep command (252 power rows, 63 frontiers):

```sh
python3 -B -m joulewise.align.squeeze --heldout-size 40 --trials 512 \
  --selection-size 256 > /private/tmp/jw-squeeze-analysis-20261107.json
```

Its SHA-256 is
`c9bfff27293cdf78f1cf0bfed4d04ce5367a965cee8489dad3866e8641c9799f`.
The JSON is ephemeral and not committed because it is fully reproducible from
the supplied code/command and contains only synthetic planning values. The
table above promotes the relevant conclusions into this handoff.

Also ran a smaller heavy-tail/correlation/alternate-design smoke (8 power
rows, 2 frontiers), all finite and valid JSON:

```sh
python3 -B -m joulewise.align.squeeze --heldout-size 40 --m 39 \
  --hidden-tokens 0 512 --residual-sd 58 --student-df 5 --correlation 0.6 \
  --form turn --trials 128 --selection-size 128 \
  > /private/tmp/jw-squeeze-sensitivity-20261107.json
```

SHA-256:
`bef753a0390eb045deade4a50e6e4b26ea104075036537556a3751cf18771776`.

Checks that caught issues:

- The first variance test assumed a >1.5 inflation of MC SE at both m values.
  That test expectation was incorrect. The exact shared-threshold ICC is
  1/(m+2); the test now checks the derived design effect instead.
- The first broad sweep exposed an observed NumPy 2.2.6/Python 3.14 buffer
  aliasing behavior: a zero-correlation multiplication overwrote the shared
  energy latent on power-of-two batch shapes. Shared noise arrays are now
  immutable, and a regression checks full energy SD/correlation for several
  batch shapes. The earlier sweep was discarded and regenerated. The
  underlying runtime defect was not investigated beyond this bounded repro.
- Independent Gaussian OR probabilities, exhaustive future-rank symmetry,
  null cohort frequencies and energy-only quadrature validate the relevant
  arithmetic. This is author-run verification, not a fresh independent review.

## Open issues and exact lead step

1. Supply the locked cohort size and unit, separately from calibration m.
   Review these draft APIs/assumptions; then rerun the CLI with that n.
2. Repeat the four targeted modules on Python 3.11/3.13 **with NumPy**. The
   numerical CI-version gates were not exercised here. Do not infer them from
   the dependency-free skip path or the 3.14 results.
3. Replace arbitrary monitor response and attack costs with independently
   supported values; refine attack grids/search budgets and test opaque
   logging/count forgery/off-meter boundaries. The simulator covers one
   continuation carrier, not full trajectory context propagation, fresh
   hidden calls, batching or physical DVFS dynamics.
4. A clean lead-controlled native session must validate actual external-meter
   integrity, logged-count integrity, real hidden-work injections and monitor
   response. Window/task exchangeability and the hybrid model's adequacy remain
   empirical gates. None may run while this blinded analysis job/agent lane is
   active. No [QUIET-MAC] work was started here.

All scientific admission, independent final review, publication and merge
decisions remain with the lead. Coordination state was left untouched as
requested. This lane supplies desk tooling and conditional power diagnostics;
it does not prove the squeeze holds against unrestricted adaptive adversaries.
