# Run report — environment guard, idle admission, and cooldown v2

Date: 2026-07-17  
Status: implementation complete; fixture/FakeClock verified; live quiet-Mac
validation remains **PROVISIONAL**  
Base head: `96d00cb1baaaebc836da294b5442dad13ab1b707`

## Outcome

Implemented the adjudicated D-077 measurement-apparatus change without
starting a quiet-Mac measurement or changing persistent host settings:

- one pure environment-policy evaluator now supplies advisor-only doctor
  findings and enforcing, post-lock campaign preflight findings;
- the campaign runner defaults to a strict, byte-hashed production sidecar,
  supports explicit transient display-sleep arming plus full re-probe, and
  accepts only an override bound to the exact snapshot and findings digests;
- run bundles gain nullable display/screensaver/HID evidence, policy and
  preflight provenance, per-run admission evidence with one distinct-artifact
  retry, and a lightweight post-run transition observation;
- production admission aborts after a persistent suspect window, while the
  exploratory-only flag path applies the universal, unwaivable
  `environment_admission_failed` barrier to gross, idle-subtracted, and
  throughput claims; exact environment overrides apply the corresponding
  `environment_override` barrier;
- cooldown v2 requires a complete duration-weighted 30-second evidence
  window, applies the one-sided upper bound and conjunctive Nominal-thermal
  rule, validates reference eligibility, and falls back only to a policy-bound
  frozen clean anchor; and
- `scripts/quiet_mac_prep.sh` now shows screensaver/HID evidence, requests
  transient display sleep after a countdown, and verifies display plus
  screensaver/HID state again afterward.

The policy owner is separate from `BenchmarkConfig`. The shipped sidecars are
`configs/campaign_policies/quiet_mac_p2_production.json` (abort) and
`quiet_mac_exploratory.json` (flag). A byte-for-byte legacy normalized-config
hash regression proves the additive sections remain omission-serialized.

## Contract and decision record

D-077 records the environment guard, exact override custody, per-run
admission, and cooldown v2 decisions. It explicitly amends D-014's recovery
semantics and D-057's reason vocabulary with
`environment_admission_failed` and `environment_override`. It is separate
from AUD-WO-033, which remains behavior-preserving; historical recovered rows
and sealed bundles are not reinterpreted.

Updated contracts:

- `docs/contracts/run_bundle_layout.md`: additive bundle fields, retry raw
  artifacts, campaign policy/preflight/admission provenance, and cooldown
  reference/anchor evidence;
- `docs/contracts/doctor_preflight.md`: shared evaluator, new sudo-free probes,
  load-as-evidence-only rule, and advisor-not-certificate boundary; and
- `docs/contracts/measurement_methodology.md`: enforcing preflight, explicit
  transient arming, exact override consequences, fixed-n admission, and
  cooldown v2 release/anchor semantics.

## Verification

- `python3 -m unittest tests.test_schemas tests.test_environment tests.test_controller tests.test_experiment tests.test_run_campaign tests.test_powermetrics`
  — 268 tests in 78.659 seconds, pass (`skipped=1`).
- `python3 -m unittest tests.test_experiment tests.test_controller tests.test_environment tests.test_doctor tests.test_run_campaign`
  — 192 tests in 81.498 seconds, pass.
- `python3 -m unittest discover -s tests`
  — 1,698 tests in 343.759 seconds on the exact final code, pass
  (`skipped=13`).
- `bash -n scripts/quiet_mac_prep.sh` — pass.
- JSON parsing for both shipped policy sidecars and the test policy fixture —
  pass.
- Python compile check for every edited Python implementation file — pass.
- Scoped `git diff --check` — pass.

The new FakeClock/fixture coverage includes the previous single-5-second
cooldown release defect, below-reference recovery, contaminated-reference
frozen-anchor fallback, admission retry-then-abort, retry-then-pass,
exploratory flagging, exact override binding, and the universal claim barrier.

## Live-validation boundary and next quiet-window action

No `[QUIET-MAC]` campaign, powermetrics collection, or other hardware
measurement was run in this agent session. The sudo-free command parsers are
fixture-tested. `pmset -g systemstate` handling is intentionally defensive:
recognized current capabilities with `Graphics` means at least one display is
awake; missing `Graphics` is accepted as asleep only with valid online-display
inventory; unrecognized output is unknown and fails closed.

**Live-validation TODO:** during the next lead-owned quiet-window prep, with no
agent load, capture `pmset -g systemstate`, screensaver defaults, and HID-idle
output once with the display verifiably awake and once immediately after
`pmset displaysleepnow`. Confirm the observed Ventura strings match the
defensive parser before promoting this surface beyond PROVISIONAL. Do not
alter persistent display or screensaver preferences for that validation.

## Workspace custody

The pre-existing `docs/site/*.html` modifications and untracked
`node_modules/` tree were not touched. No commit, push, merge, generated-site
refresh, or quiet-Mac execution was performed. Lead owns final diff review,
the live validation gate, and commit/merge custody.

## Fix round 1 — 2026-07-18

Resolved the eleven accepted execution-review findings without running a
quiet-Mac measurement:

- cooldown completeness now combines a full retained wall-clock span with an
  explicit minimum evidence-coverage fraction (default 0.8), recording span,
  required/observed coverage, thresholds, and both conjuncts in gate evidence;
- controller repetitions now enforce reference eligibility, frozen-clean
  anchor fallback, policy-specific no-anchor behavior, a full per-repetition
  environment recapture, and a post-capture guard observation after every idle
  attempt;
- campaign provenance now assigns the true first-run exemption only to the
  first physical bundle, promotes each later repetition's actual controller
  gate evidence, freezes the first eligible evaluation in execution order, and
  gives multi-entry AXI campaigns the same between-entry cooldown ceremony;
- rejected or malformed environment preflights append a terminal
  `joulewise.campaign_verdict.v2` row before exit;
- canonical analysis preserves `environment_admission_failed` and
  `environment_override`; the shell preparation parser accepts the live
  `Capabilities are:` spelling; and an absent screensaver defaults domain uses
  the macOS 1200-second default without overriding the independent engagement
  probe.

Regression coverage is defect-shaped for every finding, including the
29.995/30-second probe-gap reproduction, a below-threshold genuine evidence
hole, physical r2/r3 exemption isolation, first-eligible anchor freezing,
Battery transition abort, and terminal preflight verdict custody. Verification
on the final scoped diff:

- `python3 -m unittest discover -s tests` — 1,717 tests in 344.030 seconds,
  pass (`skipped=13`);
- the explicit 14-test F1–F11 regression selection — pass in 1.767 seconds;
- `bash -n scripts/quiet_mac_prep.sh` — pass; and
- Python compile plus scoped `git diff --check` — pass.

## Fix round 2 — 2026-07-18

Resolved the four delta re-audit findings without running a quiet-Mac
measurement:

- governed admission now evaluates the prepare-end environment snapshot, so a
  power-source change during preparation fails closed under the abort policy;
- the cooldown cap is evaluated before recovery on every iteration, with
  release criteria first met at or after the deadline retained as `cap_hit`
  and recorded as late in the trace;
- the campaign's frozen clean anchor is passed explicitly through the CLI into
  the child experiment, deep-copied there, and used when a preceding
  repetition baseline is ineligible; and
- canonical analysis reads per-physical-repetition cooldown rows when present,
  verifies the first-run exemption against the true `config__r1` bundle, and
  retains the top-level row for single-repetition and legacy compatibility.

Final verification on the scoped diff:

- `python3 -m unittest discover -s tests` — 1,722 tests in 367.585 seconds,
  pass (`skipped=13`);
- the explicit four-test N1–N4 regression selection — pass in 0.485 seconds;
- the additional in-process N3 immutable-anchor fallback regression — pass as
  part of the full suite; and
- Python compile, scoped `git diff --check`, and bridge scope-lease validation
  — pass.

No commit, push, merge, generated-site refresh, or quiet-Mac execution was
performed. Lead retains final diff review and merge custody.
