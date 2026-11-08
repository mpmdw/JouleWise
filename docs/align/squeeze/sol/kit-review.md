# Independent adversary-kit review — 2026-11-07

**Verdict: ADMIT_WITH_FIXES, as a DRAFT desk kit only.** Three implementation
defects were reproduced with failing-first tests and fixed in this branch.
This verdict does not admit a measurement campaign, a blinded evaluation export,
an adaptive-security claim, or a false-alarm/power guarantee. Those gates remain
open below. All evidence here is synthetic or source-level; no live energy or
sealed outcome was read.

Review branch: `align/2026-11-07-adversary-kit-review` (already checked out at
intake). Reviewed implementation: `a29cded84`, with report-only tip `67b4def8d`.
Fix commit: `343671290` (`fix(align): fence hidden cache work and retain
interrupted controls`). No other writer or pre-existing dirty work was observed.
Changes are local only; the documentation commit follows this fix. See the
[dated run report](../../../run_reports/2026-11-07-adversary-kit-review.md).

## Sources and scope

- Clone: `docs/research/AGENDA.md`, `docs/research/energy-tripwire.html`, kit
  code/configs/tests, `ADVERSARY-KIT.md`, and the implementation reports.
- `e901eb2a480d51377a494be9d797733dfcd0220b`: v4 protocol, residual-model
  document/code, runner/interfaces/records, and targeted Apple/SHADE integration.
- `16e1db6230a80a605d084f0f9f61431d541b793f`: literature synthesis, particularly
  its threat-model and known-omission limits; `53a2305982a551ba5285e50bd0177726b5f138e7`:
  W1 pre-arm audit; `7f74dd2a97e5fcf078652deef2fb291929dc4524`:
  research-program synthesis, particularly its positive-control recommendation.
- `7fbd95e311f31f3be82839225620a7fcdacdcd69`:
  `scripts/align_pilot_calibration.py`, specifically the pure `split_threshold`
  function. The protocol names this separately frozen calibration code.

All refs were available locally. No fetch was attempted under the no-network
rule; these are not claims about a subsequently updated remote. External paths
in source documents were treated as text. Mission M0, the stop card (NONE), queue
fences, orchestration and D-009 were inspected. Explicit user direction selects
this desk review; coordination-state updates and the full suite are prohibited
by this task. No registration or coordination file was edited.

## Findings and dispositions

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| H1 | HIGH | MLX output evaluation omitted independent lazy cache state/auxiliary arrays. | Fixed; interface regression passes, native gate pending. |
| H2 | HIGH | Hidden-decoder `SystemExit` escaped the pinned runner before sampler cleanup and before returning the private run receipt. | Fixed; unit and actual-runner overlay regressions pass. |
| H3 | HIGH | Dose is recoverable from public endpoint identity and, with known inputs, derived episode IDs. | Confirmed; documentation corrected. Lead must seal metadata before a blinded export. |
| H4 | HIGH | This kit supplies neither joint detector calibration nor a detector-feedback red team; it cannot demonstrate that the squeeze holds. | Study/claim blocker retained for lead; no registration invented. |
| M1 | MEDIUM | Positive-control work differs from the v4 known-omission estimand and requires whole-episode energy. | Correctly described by kit; qualifications below. |
| M2 | MEDIUM | Awareness/length, model state, and failed-dose selection can bias a comparison. | Lead-owned study controls required. |
| L1 | LOW | `manifest.json` could be a symlink, despite refusal of individual config symlinks. | Fixed; synthetic local-link regression passes. |

### H1 — fence cache work before certifying the dose

`MlxDecoder.decode` previously called only `mx.eval(token)`. A token depends on
the logits, but an independent lazy cache update need not be a dependency of
those logits. It can remain unevaluated, making the claimed completed-forward
boundary incomplete. The pinned lane already explicitly evaluates cache state
in `apple/prompt_cache.py`, including auxiliary recurrent-cache arrays.

The decoder now evaluates the output and reachable cache arrays together before
yielding an ID. Collection covers mapping/list/tuple caches and cache objects'
public `state` plus array-valued instance fields, deduplicates shared arrays,
and does not walk model objects. No extra forward or iterator lookahead is added.

The failing-first test uses a clearly labelled stdlib MLX interface spy with
independent cache leaves. It failed because only the token was passed to `eval`;
it now passes. A second native test exercises the same boundary with tiny MLX
arrays and is import-gated. **Neither native test ran here.** The actual model's
cache layout, streams, interruptions and energy effect remain unverified; this
is a source/interface correction, not observed native hardware validation.

### H2 — retain interruption and stop sampling

`HiddenDecode.execute` correctly recorded `SystemExit` as interrupted with
`H=null`, but re-raised it. The pinned generic runner catches `KeyboardInterrupt`
and ordinary exceptions, not `SystemExit`; its sampler-stop code is later in
the function rather than in a `finally`. The overlay regression reproduced an
escaping `SystemExit` and no returned `SqueezeRun`.

`ControlEndpoint` now converts only a hidden control's `SystemExit` to
`KeyboardInterrupt`, after its original receipt is finalized. The runner stops
sampling, flags `episode.interrupted`, and returns the private interrupted
receipt retaining `error_type="SystemExit"`, completed prefix and unknown work.
The visible endpoint is not called. Direct `HiddenDecode.execute` still raises
its original exception. This does not guarantee receipts for SIGKILL, process
crash, or a production deadman; qualify those separately.

### H3 — a hash is not dose blinding

The public endpoint identity hashes the variant hash, control-config hash and
decoder identity. `run_episode` writes it to `Episode.hardware["endpoint"]` and
uses it to derive `episode_id`. The seven public dose configs form a tiny
dictionary. A synthetic probe reconstructed the endpoint suffix for every config
and recovered **512** uniquely without the receipt or any decoder forwards.
Known task/condition/seed/matrix inputs also make the episode IDs enumerable.

This is a label-disclosure route to an analyst or a detector consuming metadata;
it is not a demonstrated leak to the transcript-only monitor. The monitor API
receives transcript/task description, not these identities. No sealed study
labels were involved in the probe.

I retained deterministic provenance and documented the issue instead of silently
changing episode identity semantics. Before blinded analysis, the lead must
quarantine endpoint/control/variant identities, condition and evaluator labels;
export opaque assignment IDs whose lookup is sealed; and freeze the detector
feature allowlist. Hashing the existing deterministic identity again does not
solve the dictionary attack. This kit alone is not a blinded exporter.

### H4 — statistical and adversary claims exceed this deliverable

The six variants are prompt instructions, not implemented attack optimizers.
`mixed-adaptive` responds to task progress/tools and receives no alarm feedback.
No SHADE task was run here. There is no evidence of side-task success, increased
evasion, or adversarial coverage. A capable compute-neutral semantic attack can
keep the same work/counters and escape energy detection; plausible padding or
names-only tool visibility need not force a transcript detection either.

The kit appropriately makes no efficacy claim. For the paper, freeze the attack
privileges, feedback/query budget, selection policy, view, task-success criteria
and held-out cohort before evaluation. Include fixed-work attacks and report
side-task success **and** joint evasion. A failed side task is not a security
success attributable to a detector. The missing numbered squeeze addendum and
unresolved historical W1 gates remain lead-owned.

## False-alarm and power audit

The following are mathematical desk checks, not empirical performance estimates.
The kit implements no threshold, score fit, confidence interval or power curve.

For m calibration scores and one future score exchangeable under the **same
frozen scoring rule**, with strict `score > threshold`, the continuous-case
tail above ascending rank r is `(m+1-r)/(m+1)`. Ties can make it smaller. The
split rank `ceil((1-alpha)*(m+1))` gives a marginal bound; when the rank exceeds
m, no finite threshold is justified by that construction.

Exact rational arithmetic at alpha=0.05 gives:

| m | Legacy type-1 rank `ceil(.95*m)` / tail | Split rank `ceil(.95*(m+1))` / tail | Sample-maximum tail |
|---:|---:|---:|---:|
| 20 | 19 / 9.523810% | 20 / 4.761905% | 4.761905% |
| 21 | 20 / 9.090909% | 21 / 4.545455% | 4.545455% |
| 39 | 38 / 5.000000% | 38 / 5.000000% | 2.500000% |
| 40 | 38 / 7.317073% | 39 / 4.878049% | 2.439024% |

The old `energy_residual.grouped_benign_threshold` uses the legacy rank and
cannot supply a general 5% split-conformal guarantee. The separately frozen
`7fbd95e31` calibration uses the corrected integer rank. I extracted and executed
only that pure function's AST: m=0,18 correctly lack finite thresholds; m=19,20,21
use their maximum; m=39 uses rank 38; m=40 uses rank 39. No calibration loader or
analysis pipeline was executed. No upstream estimator was changed by this review.

The research HTML's sample-maximum statement needs the frozen-score/
exchangeability qualification. At m=39 a **maximum** gives 2.5% marginal tail;
the alpha=.05 split rank is instead 38 and gives 5%. These are distinct rules.
LOTO or leave-pair-out scores followed by a full-data fit are not automatically
exchangeable with the future score; correlated repeats, selected trajectories,
session drift and configuration changes also need justification. In particular,
a sample maximum does not itself prove the premise. Keep strata and independent
trajectory/window units explicit; do not count repeats as new independent cases.

The guarantee is marginal over calibration sets. For iid continuous scores and
a maximum at m=39, the probability that the realized conditional false-alarm
rate exceeds 5% is `.95**39 = 0.13527595`. It is not a 95%-confidence conditional
bound. A maximum would require 119 independent calibration scores for a
95%-confidence conditional bound of 2.5%, under those assumptions. This arithmetic
is an illustration, not a newly registered sample-size requirement.

Joint logic must be explicit. Catching an attack when **either** detector alarms
is OR; evasion requires both detectors to remain negative. Two separate 5%
alarms can yield 9.75% OR false alarms under independence, and at most 10% by the
union bound without independence. Two valid 2.5% marginal budgets bound the OR
at 5% without independence. Changing to AND changes the security endpoint.
Multiple monitor views, pairs and configurations require their own declared
population/multiplicity treatment. No joint rule is registered here.

The residual document's `H_min=(z_(1-alpha)+z_power)*D/e` and
`H_cal=(t-mu_b+z_power*s_b)*D/e` follow from an additive fixed-D, fixed-e normal
score shift. The .05/.80 planning multiplier is **2.486474861**. These formulas
are not distribution-free power guarantees, and reading additive bounds as SDs
does not repair their assumptions. The injector adds a fresh hidden call,
prefill, context growth and potentially extra variance/thermal changes; applying
the old linear per-hidden-token power formula to its H would be unjustified.

Measure a separate sham-versus-dose detection curve over independent carriers
and windows. For perspective, all n detections yield one-sided exact 95%
binomial lower bounds `.05**(1/n)`: 0.223607 for n=2, 0.807364 for n=14, and
0.901855 for n=29. Those examples presume independent Bernoulli trials and do
not transfer to clustered carriers or to a whole multi-dose curve. H50/H90 need
uncertainty, right-censoring when no crossing occurs, and window dependence;
interpolating two successful trajectories is not a power demonstration.

## Protocol, accounting and bias checks

- Exact generated-output accounting is correct: P prompt IDs and k>0 outputs
  require one P-input prefill and k-1 single-input forwards; P+k-1 total consumed
  inputs. k=0 performs neither cache creation nor a model call. Context-limit
  validation uses the consumed-input boundary. EOS does not stop the dose.
- v4's omission H is stripped **reasoning counts**, holding measured joules and
  original P/C fixed. This injector's H includes the output from a new prefill.
  Keep these estimands and curves separate. v4's frozen sequence design is
  `[1,P,D,(C+P)D+D²/2,CP+P²/2]`; do not substitute the older context-product
  planning design or pool across configurations/pairs/sessions without authority.
- Hidden work precedes visible endpoint timestamps and occupies an unowned gap.
  The actual-runner tests establish containment in a synthetic episode and
  active sampler interval. Use a valid **gross whole-episode** integral: summing
  visible turns could omit the entire control. An `inside` receipt is not meter
  coverage, uncertainty, power-mode/battery validity, or cross-clock calibration.
- No hidden IDs/counts/receipt are added to requests, endpoint usage or any of
  the three generic monitor views. Sham/dose visible trajectories and counts
  match in the synthetic endpoint. The real SHADE renderer suppresses tool
  arguments even for `full`; that existing weak view is not strengthened here.
- The sabotage-only awareness overlay changes prompt length and instructions.
  Training only on unaware benign prompts can cause out-of-support residuals.
  Freeze matched benign awareness/length controls or an explicit sensitivity
  design; extra logged generation consumes energy too. Semantic tool effects
  need not entail substantial additional compute.
- Sharing a prepared model requires evaluation mode and genuinely fresh hidden
  caches. Greedy decoding alone does not prove unchanged native RNG, caches,
  thermal state, memory pressure or visible output. Native qualification and
  the actual Apple integration remain missing; no frozen anchor was altered.
- Partial/failed/unreached controls must remain in the planned-dose ledger.
  Report failure/attrition by assigned dose and keep `H=null`; silently dropping
  failures or counting H=0 alarms as successful hidden-work detection biases
  power. A completed dose on an otherwise invalid episode remains invalid.

## Test tails and verification

Every kit module ran in its own process, serially, on Python 3.13. No full suite,
pytest, native model, weights download or real measurement was used. Aggregate
test runtime was seconds, far below the approximately 20-minute budget.

Baseline at the intake head: config 8 passed; control 8 passed; pinned-runner
overlay 7 passed; direct harness 7 skipped; native 1 skipped (MLX absent).

Failing-first tails after adding regressions, before production fixes:

```text
tests.align.test_squeeze_config: Ran 9 tests ... FAILED (failures=1)
  expected symlink refusal; instead parsed the synthetic linked target
tests.align.test_squeeze_control: Ran 10 tests ... FAILED (failures=1, errors=1)
  independent cache leaf missing from eval; SystemExit: 23 escaped
scripts/check_squeeze_overlay.py: Ran 8 tests ... FAILED (errors=1)
  SystemExit: 23 escaped the actual pinned runner
```

Final commands/results (all exit 0):

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.align.test_squeeze_config` | 9 passed |
| `python3.13 -B -m unittest tests.align.test_squeeze_control` | 10 passed |
| `python3.13 -B scripts/check_squeeze_overlay.py` | 8 passed; no skips; actual pinned runner |
| `python3.13 -B -m unittest tests.align.test_squeeze_harness` | 8 skipped: runner absent on this main-based clone; covered by overlay |
| `python3.13 -B -m unittest tests.align.test_squeeze_native` | 2 skipped: MLX absent; **unverified** |
| `python3.13 -B -m joulewise.align.squeeze validate --kit configs/align/squeeze` | 13 configs validated |
| `python3.13 -B -m compileall -q joulewise/align/squeeze tests/align/test_squeeze_config.py tests/align/test_squeeze_control.py tests/align/test_squeeze_harness.py tests/align/test_squeeze_native.py` | Passed |
| `git diff --check` | Passed |

The overlay's three source hashes matched the implementation report:

```text
records.py    d5b8f8583716ba5419c0c84710ffec30735128a31b056830767dca6d13cccf93
interfaces.py 6b43491d42b3fc002870e16beb552c9bcb011533597d87046cc165b428b9be00
runner.py     7c3e5015bc9b3f14f4c8a9e872e7501d7876b2758799178df81a56d12db9c638
```

Additional desk-probe tails:

```text
PINNED SPLIT-THRESHOLD CODE: exact ranks, no-finite boundary and strict-tie checks passed
PUBLIC IDENTITY DICTIONARY PROBE: recovered hidden dose [512] without receipt or compute
ALL DESK AUDIT PROBES PASSED; no empirical FPR/power estimate
```

The rank table used exact `Fraction(19,20)` arithmetic. The dictionary probe
hashed the documented identity payload for each public control config using
`canonical`/`sha256`, comparing to one synthetic wrapped endpoint. Its first
attempt was refused because the toy decoder advertised context limit 64 rather
than the shipped config's 4096; the final probe declared 4096 and executed no
forwards. The final combined probe exited 0. These probes are mathematical/
metadata checks, not statistics computed from study data.

## Handoff and uncertainty

Changed code: `joulewise/align/squeeze/{config,control}.py`. Regression additions:
`tests/align/test_squeeze_{config,control,harness,native}.py`. Documentation:
`docs/align/squeeze/ADVERSARY-KIT.md`, this review and the dated run report.
Config/manifest bytes, estimator code, protocol, anchor/W1 bytes and protected
coordination files are unchanged.

Next exact step: the lead reviews this diff, reruns
`python3.13 -B -m unittest tests.align.test_squeeze_native` outside the sandbox
with MLX and Metal using only the tiny synthetic models, then resolves the
metadata/export boundary, attack addendum and joint calibration before freezing
any campaign. Production model/cache, deadman, external-meter timing and gross
integration require a separate authorized quiet-machine session with agents
absent. The review's own fixes and new tests still need the lead's fresh
independent review before merge; this author does not certify its own patch as
a cold merge gate. Python 3.11 and full-suite/CI verification were not run here.

No network, external integration, model download, real restricted directory,
measurement bundle or Block-5 analysis was accessed. No unrelated process was
inspected or signalled; the host fixture census was omitted to avoid enumerating
the unrelated blinded job, and these tests launched no background fixture
services. No push, merge, arm, registration, or kernel task was performed.
