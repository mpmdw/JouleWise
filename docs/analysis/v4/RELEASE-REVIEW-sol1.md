# ALIGN v4 release tools: independent Sol review 1

2026-11-08. **Verdict: HOLD.** Synthetic witnesses identify a shared violation of
the adopted calibration rule, incomplete row coverage, a legitimate W1 path
that holds wrongly, and an unchecked producer identity. None requires a
deliberate adversary or a filesystem race.

## Scope and authority

Reviewed release-tools `99875485d`, engine-r23h
`244ef6f395e8ad13c836ceb23fef10530861eb86`, and recompute
`de553c002879f93cdd32f15861f638a18dbd74f0`. Read the A0–A36 interpretation
text at `a3465eda8:docs/analysis/v4/INTERPRETATION-RULINGS-DRAFT.md`, its
adoption/amendment in `origin/main:RUN_STATE.md` item 230, and items 233–239
(A37, R22–R26). The draft is absent from main; its adopted source commit is
therefore material. The later rulings supersede the original A17 counting rule.

This is an independent review, not a production fix or an unseal authorization.
The only repository writes are this report and
`tests/v4_release/test_review_sol1.py`. Coordination state is lead-owned and
unchanged. No network, weights, real measurements, real restricted directory,
or quiet-machine operation was used. No other review agent was consulted.

## F1 — shared stale calibration rule can AGREE wrongly or refuse a valid reserve

**Release-blocking; confirmed in both pinned implementations.** R22-2/R24
require exactly eight admitted calibration windows. A structurally barred window
contributes nothing and is replaced, with C9–C14 available in frozen order.

The recompute's `calibration_stop()` (lines 1397–1439) zeroes a barred window's
eligible counts but still sets `counts_window = captured > 0`. The engine
passes captured-member ledger rows to its pinned `v4_cadence.calibration_stop()`
and counts the same barred window. Its `engine.py:29` ORDER also admits only
C1–C8 followed by T1–T3; the order check at line 513 rejects a C9 replacement.

Witnesses:

- `test_r22_both_builds_complete_after_only_seven_admitted_windows`: C1 is
  barred, C2–C8 each supply seven benign members per pair. Both stop predicates
  say `calibration_complete` with 49 per pair, although only seven windows were
  admitted. This is a shared semantic defect that cross-build agreement cannot
  detect. This witness executes the two predicates, not a full release.
- `test_r24_valid_eighth_admitted_window_is_refused`: add healthy C9. There are
  now eight admitted windows; both predicates throw because they count nine.
  The engine's earlier ORDER fence is an additional refusal path.

**Required:** update both builds from R22/R24 text, including admission,
replacement ordering/seeds and terminal states; review R25 reserve U3 scope and
contention disclosures alongside that change. Re-pin only after a synthetic
bar-plus-reserve rehearsal. The existing rehearsal never includes C9–C14.

## F2 — leaf accounting does not prove row completeness

**Release-blocking; four end-to-end comparator witnesses.** Many comparisons
iterate only what the engine printed. Removing a required row removes its
leaves from both the comparator walk and the regenerated engine inventory.
`row_manifest()` covers only selected families and usually counts a whole
member or pair as one unit. A surviving row elsewhere keeps the family nonempty.

Each following mutation retains valid JSON and a matching leaf inventory, then
returns **exit 0, AGREE, zero unmapped leaves**:

| Witness | Removed required output | Why it escapes |
|---|---|---|
| `test_r26_whole_h_grid_can_disappear` | Every score row's `H_grid` | `_known_h()` iterates printed tables; first-k/council rows keep `known_h_doses` nonempty |
| `test_r26_interior_carrier_curve_dose_can_disappear` | Dose 384 and its denominator in both pair curves | `carrier_curve()` iterates printed doses; the manifest still sees two pair units |
| `test_a13_u3_replay_pair_can_disappear` | C2 D replay pairs in both acceptance and window reports | `_checks()` compares the surviving aggregate verdict and never requires the absent pair |
| `test_per_turn_residual_tail_can_disappear` | All but the first residual of each score row | `fits_and_scores()` iterates printed residuals without a per-member turn cardinality check |

These model an omitted/filtered output table or a producer printing only a
prefix. They require no changes to raw data or to the numerical comparison bars.
They directly defeat R22-4/R-C2 and, for the first two, R26's required doses.

**Required:** derive expected keys and cardinalities on both sides from roster,
registered dose grids and recomputed turn counts. Require exact row sets with
explicit structural exclusions. Checking only existing engine leaves is
insufficient. Add per-family/per-member manifests rather than treating a
nonempty family as complete.

## F3 — legitimate A19 W1 INCONCLUSIVE becomes a false HOLD

**Functional false hold; confirmed with both pinned producer functions.** A19
explicitly permits fewer than eight eligible token-identical contrast runs:
the result is INCONCLUSIVE, without a fit.

`test_a19_legitimate_unavailable_w1_creates_false_disagreements` calls both
producers with unavailable contrast runs. Both return INCONCLUSIVE. The engine
reason is `requires 2 token-identical eligible runs in each template/arm`; the
recompute reason is `not exactly 8 eligible token-identical runs`. `w1()` compares
these implementation-specific strings exactly. It also compares absent fit
fields through MISSING, producing `absent_recompute` failures even when neither
side could legitimately compute a statistic. Seven eligible runs take this same
producer branch. The witness uses the zero-eligible endpoint of that branch.

**Required:** compare fixed structural reason categories, check the common
absence of statistics under the registered unavailable condition, and retain
strict value comparisons whenever a fit should exist. Do not fill absent
statistics with zeros or waive all INCONCLUSIVE rows.

## F4 — engine commit attestation is not checked against producer identity

**Operator binding gap; confirmed through the full release wrapper.**
`stage_digests()` checks a manually authored record's commit label against the
engine pin and hashes artifacts against that same record. It does not validate
the engine freeze's `loaded_scorer_sha256` against the pinned build. The
comparator exempts that field as `build_digests` in `claim()`.

`test_changed_loaded_scorer_binding_is_exempt` changes the printed loaded-scorer
identity and still gets comparator AGREE. The stronger
`test_release_accepts_changed_producer_identity_in_recorded_artifacts` changes it
consistently in fill/freeze, writes an otherwise correct run record using the
default pinned commit, and runs the real release wrapper from a clean disposable
checkout. All numerical outputs and raw inputs stay unchanged. The release
accepts the contradictory producer identity with exit 0 / AGREE.

The mistake path is recording the intended/default engine commit for artifacts
made by another loaded build. This is a binding witness, not a demonstration
that a particular old engine changes an estimand. It does not establish an
actual stale production run.

**Required:** verify the loaded scorer/reducer identity against the pinned
engine, accounting for the interpreter identity already included in the scorer
hash; bind the engine run record to that verified execution. A hash-consistent
operator-created record alone cannot establish which code ran.

## Bars, exits and sealed outputs

The numeric bars inspected follow the adopted scale distinctions: strict energy
bars, explicit score bars, log-relative tail bounds, exact rank/member identity,
and exact bootstrap recipe/output. I found no separately established
release-blocking tolerance defect. This does not certify conditioning on every
possible real fit.

Positive controls in the new module confirm that an injected token-count leaf
on an engine sealed member refuses as `unmapped_leaf`, and simultaneous energy
disagreement plus eligible-m disagreement returns refused 2 over hold 1. The
wrapper also validates comparator exit/verdict consistency. Existing release
tests exercise pin, raw digest, crosswalk and checkout refusals.

The wrapper's inspected paths put recompute values, comparison rows and child
streams under its newly created mode-0700 output; the public verdict contains
fixed structure/count fields. I did not reproduce an outcome-bearing scored
C-sabotage value on that public path. The A27 control is deliberately an
engine-side count leak; it is not a general proof about every possible future
producer extension. Presence-only seal comparison remains the adopted rule,
not a demand to compare the two builds' incompatible hashes.

## Verification and handoff

All modules ran sequentially with Python 3.13, one module per process:

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.v4_release.test_compare_v4` | 18 tests OK, 358.840 s, including cold synthetic rehearsal |
| `python3.13 -B -m unittest tests.v4_release.test_review_sol1` | Final run: 12 tests OK, 20.685 s |
| `python3.13 -B -m unittest tests.v4_release.test_release_v4` | 13 tests OK, 11.125 s |
| AST parse of the new witness module | OK |
| `git diff --check` | OK |

The first new-module run executed nine tests and had one class-setup error:
loading the pinned thermal module imported a symbol absent from this checkout's
older attribution module. The helper now extracts only the verbatim pinned
function needed for the empty-input witness, avoiding unrelated imports. The
complete rerun above passed. Including that 21.043 s failed run, total unittest
time was approximately 412 s, below the requested 20-minute budget. The full
suite and the costly separate rehearsal-mutation module were not run, per the
task's test/resource restrictions and the test/report-only scope.

Witness tests intentionally assert the observed bad behavior: passing them
reproduces the findings. They must be converted to rejection/coverage
regressions when the fixes land. Source and bar files are unchanged. Local
handoff branch: `align/2026-11-08-release-tools-sol1`; no push was performed.

No production files were changed. No native MLX/hardware tests are needed for
this test/report-only change, and none were run. Lead next step: disposition
F1–F4, repair and re-pin the builds/tools as appropriate, then re-run these
witnesses and a synthetic series containing structural bars, reserves and an
unavailable W1 contrast. Actual data and unsealing remain with the lead.
