# R11 delta2 review — Sol2

**Verdict: HOLD.** The original delta witnesses pass, but two HIGH receipt
findings still affect exact-candidate validity. Three MED findings concern
permitted sentinel rosters and battery evidence. The witnesses are in
`tests/align/test_r11_delta2_sol2.py`; negative witnesses intentionally remain
red for the lead's repairs. No product code was changed.

Seat: `align/2026-11-08-v4-r11-delta2-sol2`. Candidate:
`f993b784f`; reviewed range: `git diff 353446ad6..f993b784f` (33 paths),
plus necessary callers and the two Sol delta / Opus cold reports named in
the brief. This does not admit the inherited historical stack or authorize
registration or an arm.

## Findings

### D2-S2-H1 — HIGH: two actual executable entry points remain outside the receipt

`scripts/run_campaign.py:1577` constructs `python -m joulewise run ...`.
Python executes `joulewise/__main__.py`, which dispatches to `cli.main`.
That file is absent from both the walker result and `ARTIFACTS`.

The committed registration input at `registration/inputs.json:106` selects
`scripts/align_r1_runtime.py`. `align_r1_rehearsal.runtime_argv_from_inputs`
(`:1965–1979`) validates and launches precisely that path. The wrapper is
also absent from both sets. Binding `joulewise/align/apple/r1_runtime.py`
does not bind a wrapper that can change its arguments or replace its call.

`ExecutionBindingWitnesses` creates a valid synthetic receipt with the
original entry point committed, commits changed executable bytes, proves
the worktree is clean, and expects refusal. Both negative witnesses fail:
the receipt still validates. The W1 `-m` edge alone is sufficient for this
finding; it does not depend on when the R1 receipt is minted.

The current walker computes **278 paths**, merged with named artifacts to
give **292 bound paths** (96 classified strict). Thus 292 is the artifact
set size, not a completeness proof. Exact Python string matching misses
the actual config-selected R1 edge; import traversal misses `-m` package
entry points. These are existing first-party edges, not hypothetical future
dynamic imports. Declaring computed paths a separate boundary does not
supply their missing binding.

**Repair:** add explicit execution edges for module launches and the
registered runtime argv, walk their imports, and bind the resulting files.
Exercise the walker with `-m`, config-selected entry points, and an ordinary
equivalent path construction; keep a small independent inventory of the
actual launch spine. Do not execute native code to collect this inventory.
The R1 runtime config itself (`configs/align/v4/r1_runtime.json`) is also
unbound; its configured/template inputs should be considered explicitly
when qualifying that boundary rather than assumed covered by an AST walk.

### D2-S2-H2 — HIGH: launched calibration code is admitted through amendment rows

`STRICT_SCRIPTS` (`v4_registration.py:316`) omits these actual chain tools:

* `scripts/reserve_calibration_window_bracket.py`;
* `scripts/validate_powermetrics_fiducial.py`;
* `scripts/b5_window_calibration_verdict.py`.

`joulewise/b5/chain.py:141–146,1181–1186` names and launches them; the W1
plan includes bracket reservation and calibration captures. They are bound,
but `is_strict` returns false. A clean committed replacement plus an
otherwise valid lead-signed amendment validates for **all three** in
`StrictLaunchTierWitnesses`. In particular, the fiducial program defines
the calibration acquisition and its physics gates; this is not unrelated
maintenance pulled into an oversized closure.

Protocol `pilot_protocol_v4.md:747–758` explicitly makes every launched
W1/D/R1 script in the spine strict. The implementation currently lets a
lead use the lighter amendment procedure for those scripts, without the
scoped delta reviews/re-registration required for that tier. Extend the
strict inventory to the actual calibration spine and audit the other
measurement-bearing shared dependencies before freezing it. Shared B5/B6
infrastructure may retain the lead-ruled amendment tier; this finding does
not request making every closure path strict.

**Direct answer to the bypass question:** an amendment row for a path
already classified strict is refused before working-byte validation. The
passing `scripts/launch_window.py` control confirms it. The defect is the
classification of real execution paths, not a way through that guard.

### D2-S2-M1 — MED: a permitted two-sentinel addition is rejected as impossible counts

`v4_cadence.py:224,283` hard-codes a maximum of 22 captured members.
The protocol (`:506,831`) requires two extra sentinels in remaining
windows after U4/U5 inconclusive. A default 22-member D window then has
24 captures, still only seven eligible benign calibrators per pair.
`CalibrationRosterWitnesses` supplies eight such final windows and gets
`ValueError` instead of `calibration_complete`.

This would strand the next triage for a registered consequence even with
honest, conserved counts. Derive the capture ceiling from the authorized
prospective roster (including added sentinels), while keeping the integer,
subset, per-pair and fixed-eight checks. Do not increase calibrator counts
or silently enlarge the roster.

### D2-S2-M2 — MED: untimed invalid battery rows disappear from float evidence

`v4_topup.derive:70` filters unusable rows. Its subsequent invalid-row check
(`:85`) inspects only rows with finite timestamps later than the last
completion. A valid JSON object containing `probe_error: true` and
`wall_time_s: null` is therefore ignored. Insert it in a dense, otherwise
valid old-charge log: `derive` still admits `continuous_float`.

`TopupWitnesses.test_unknown_timestamp_row_cannot_disappear_from_continuous_float_evidence`
fails. This requires no false charging value: it is malformed supplied
evidence that the validator can detect. An observation whose time
is unknown cannot prove that its error preceded the claimed continuous
interval. Refuse malformed/untimed records rather than deleting them from
the evidence sequence; retain legitimately charging observations even
though their ordinary float predicate is false.

### D2-S2-M3 — MED: basis (a) spuriously inherits basis (b)'s continuity requirement

The protocol (`:617–621`) and module docstring define alternatives:
completed charge within 1800 s, **or** continuous float since an older
completion with gaps at most 300 s. The implementation applies the gap
and subsequent-float checks before choosing the basis (`:85–99`).

The witness supplies charging at arm−1300 s, completion at arm−1200 s,
and a current floating observation at arm−100 s. It refuses solely for
the 1100 s gap, although the completion is within the hard 1800 s bound.
The separate live arm predicate still checks fresh AC, 99–100%, no
charging, current and OBC attestation. The positive boundary/old-charge
control passes with dense observations and exactly 1800 s admitted.

**Repair:** implement the two documented bases separately, or obtain and
record a ruling that both require continuous logging, with an operable
sampling plan. Do not silently extend the 1800 s bound. For back-to-back
windows there is an additional operational precondition: the documented
sampler runs “between windows”, but basis (b) cannot survive a long
unsampled window with an old completion. This review does not authorize
running an extra sampler during measurement or relaxing the gap rule;
the lead must resolve that evidence plan before relying on continuous float.

## Disposition of the supplied findings

| Supplied finding | Assessment at this candidate |
|---|---|
| Delta H01 / S2-H1, omitted launched scripts | The named campaign/helper/hazard wrappers are now bound; both original modules pass. The larger execution obligation still has H1 above. |
| Delta H02 / S2-M1, impossible counts | Repaired for the default roster: integers, captures, disjoint eligible sum, totals, and fixed-eight test entry are checked. The new ceiling causes M1. |
| Delta M01, provisional zero capture | Repaired: unfinished zero-capture attempts hold pending; final zero captures do not consume a slot. |
| Delta M02 / S2-M2, contradictory flags | Repaired for supplied packet identity: W1 is derived from the window id, code/config drift from current artifact bytes versus the last desk digest; contradictory flags refuse. This does not authenticate the lead's record assertions. |
| Delta M03 / Opus L2, retention | Repaired: packet, canonical digest, file digest on the file-input route, counts and rulings are retained. |
| Opus HIGH-1, red WP22 | Contrast is recomputed after the WP18 update with matching X-G stand-in turns; stage and delivery inputs reach the desk. PENDING U3 no longer aborts all diagnostics. Minimal default and full verification results are below. |
| Opus MED-1, brittle receipt | A genuine signed/chained amendment path exists. Unamended drift, malformed rows, broken chains, immutable-pin edits, and amendments to classified strict paths refuse. H1/H2 limit admission. |
| Opus MED-2a, escalation deadlock | Signed lead rulings reset the trailing zero-capture escalation without dropping history; retained in the arm record. |
| Opus MED-2b, secondary-meter deadlock | Previous coverage is recorded/non-gating; reader liveness is a separate gate. Gaps no longer permanently block the next arm. |
| Opus MED-3, top-up evidence | Free timestamps removed; logged evidence and own arm clock used. M2/M3 remain. |
| Opus MED-4, DC blinding | On the current session-desk output route, non-benign/missing-condition member rows are replaced before printing and retention, including nested values. Benign-only training keeps the published DC model free of sabotage values. No new DC value leak found on that route. |
| Opus L1/L3/L5/L7/L8/L9 | Synthetic R1 exporter/backfill binds input digests and checks counts; commit existence is checked; window id uses state; packet template exists; pmset is evidence only; bool/string H* scores refuse. These are bounded fixes, not live provenance or hardware qualification. |

## WP22 test changes and uncertainty

**U3 inconclusive is correct.** The v4 acceptance route passes an invalid/pending
bar into `u3_margin`, which refuses the historical constant. `validate_u3`
continues to refuse arming unconditionally. The desk change enables other
diagnostics; it grants no missing U3 clearance. Its broad `except ValueError`
also labels malformed but parseable bars pending today; no numerical bar is
currently admissible. Narrow it when an actual derivation is installed.

**The 0.1 J comparison is not evidence of an estimator defect, but it is a
weaker oracle.** The current `contrast_oracle` still fits four columns
(template, arm, drift; df=4), while v4 correctly fits five with stage
(df=3). Comparing those coefficients at 1e−4 J was not the right v4
invariant. The cited 0.057 J discrepancy can reflect that design mismatch;
I did not independently reproduce that exact decimal from retained full
window bytes. The new review control uses the independently implemented
`dry.ols` on an eight-row, five-column design with stage effects and checks
both the coefficient and 90% CI tightly. Its result is recorded below.
Prefer updating the synthetic oracle to the registered v4 model, retaining
independent world energy integration, over treating 0.1 J as a universal
allowed fit error. No product estimator repair is justified by this
tolerance change alone.

The one expected failure is
`InjectedWindowTests.test_collector_death_is_x4_and_episode_continues`:
the old design expectation says the member succeeds, while the implemented
WP8 F2 policy fails fast on collector death. It predates this delta and is
recorded as WP22 F3 in the integration report and LEAD-RULINGS-2. The
companion tests verify that the failure is still X4, contributes to U1,
and cannot supply eligible thermal/energy evidence. Acceptable as that
documented divergence for this delta; it is not a surprise clean-window
failure or hardware qualification.

## Verification and handoff

Every touched test module ran alone in a process, sequentially, using
`python3.13 -B -m unittest tests.align.<module>`. Additional original
witness, thermal, meter and protocol modules ran the same way. All 20
ordinary selections passed: **400 tests run, including 14 default WP22
skips**. The separate `JW_WP22_FULL=1` selection passed: **20 tests, one
expected failure** (WP22 F3). There was no unexpected baseline failure.

The new `tests.align.test_r11_delta2_sol2` ran **10 tests: four controls
pass; six methods expose the five findings**, reported by unittest as
**7 failures and 1 error** because H2 has three failing subtests and M1
raises on an allowed roster. These are deliberate failing-first witnesses,
not a passing gate. The stage-adjusted independent coefficient/CI and DC
sealing controls pass. Total test wall time was about **382 s** (6.4 min),
well below twenty minutes. Compile and whitespace results, command table,
and local commits are in the companion run report
`docs/run_reports/2026-11-08-align-v4-r11-delta2-sol2.md`.

No network, model weights, MLX execution, real measurement input, Block-5
analysis, sealed directory, host-setting change, process census of the
running job, full suite, push or merge was used. Host-state locations were
overridden to a synthetic directory under `/private/tmp`. The pre-existing
seat branch was clean at intake. M0/stop card (NONE), queue, conventions,
orchestration, targeted decisions and the local origin/main authority
(including fixed-eight item 217) were read. The explicit brief supersedes
queue selection, full-suite and coordination-write requirements. No peer
agent was invoked; this is the Sol2 independent seat, not a substitute for
Sol1's review.

**Next exact step:** lead adjudicates H1/H2 and M1–M3 with the other seat,
repairs the bounded execution/tier/evidence defects, then runs the supplied
new witnesses and affected modules one process at a time. Preserve pending
U3, final-roster U6 OC, B consequence/charge hold, actual C/F/T manifest,
scorer/dependence qualification, native identity/cache and live custody
gates. This report does not close any of them. Outside this sandbox the
lead must run the tiny/offline native gates at the integrated candidate:
`tests.align.test_cache_checkpoint_native`,
`JW_ALIGN_MLX_NATIVE_TESTS=1 tests.align.test_thermal_mlx`,
`tests.align.test_r0_mlx_native`, and the authorized native R1
termination/census checks. Use importability gates and existing tiny models;
download no weights and do not interrupt the blinded job.
