# ALIGN v4 release review — Sol seat 2

2026-11-08. **Verdict: HOLD.** Synthetic evidence only.

Reviewed release-tools `99875485da452f8941f4c49e5cfac0e76c2ed062` on
`align/2026-11-08-release-tools-sol2`, engine-r23h
`244ef6f395e8ad13c836ceb23fef10530861eb86`, and recompute
`de553c002879f93cdd32f15861f638a18dbd74f0`.

The blockers below have functional or ordinary operator-error paths. None
requires a deliberate adversary, a race, or access to study data. I changed
only this report and `tests/v4_release/test_review_sol2.py`; implementation,
pins, coordination files, and kernel tasks are untouched.

## Findings

### F1 — HIGH: both pinned builds retain the pre-R22 calibration policy

Authority: origin/main RUN_STATE 234 R22-2, 236/238 R24, and 239 R25.
Eight **admitted** calibration windows are required; a structurally barred
window contributes nothing and is replaced in order by C9-C14. Replacements
cannot repair low eligible counts. The prospective U3 budget includes the
reserve comparisons.

The pinned recompute's `calibration_stop` (lines 1397-1439) zeroes a barred
window's eligible counts, but sets `counts_window = captured > 0` regardless
of its bar. The engine does the same: `engine.py:576-627` passes a captured,
zero-count ledger row to the old `apple/v4_cadence.py:256-365` predicate,
without retaining a structural-bar field.

Witnesses execute the pinned functions with C1 barred and C2-C8 healthy.
**Both return `calibration_complete`, m=49 per pair, although only seven
windows were admitted.** Adding healthy C9 makes both predicates raise for
more than eight counted windows. Separately, the engine's `ORDER` and
`roster` (`engine.py:30-44`) reject C9 before reading any member. Its series
validation and CLI also enumerate only C1-C8/T1-T3.

R25 is missing as well: pinned `acceptance.py:31-65` hardcodes both the U3
tail calculation and printed comparison count to **16**. A synthetic bar
using the expanded roster has N=22 (old 16 plus six reserves); the recompute
accepts that input, while the engine still derives N=16. Keeping the old bar
lets the builds agree on the superseded budget; supplying the corrected bar
makes them disagree even before a reserve is used. The rehearsal writer
still supplies N=16 and has no barred-window replacement case.

This is a shared obsolete reading, not independent corroboration of the
registered policy. I cannot establish whether any code was copied.

**Fix:** integrate the structural bar into both stop predicates, roster and
series ordering, reserve seed law, and U3 comparison budget. Exercise a
barred C followed by its reserve, distinguish this from an unbarred low-m
window, and re-pin both builds only after a fresh rehearsal. The primary
engine freeze makes this a lead-owned integration decision, not a reason
to accept the old policy.

Witnesses: `test_r22_barred_window_does_not_complete_eight_admitted_windows`,
`test_r24_c9_replacement_is_not_a_ninth_counted_window`,
`test_r24_engine_roster_accepts_predeclared_c9`, and
`test_r25_u3_budget_includes_six_reserve_comparisons`.

### F2 — HIGH: partial H* and dose omissions still AGREE

Authority: R26, A7/A8, and R-C2.

`compare_v4_recompute.py:690-724` iterates only the engine's present dose
rows. At lines 742-751, it compares H* only if the engine emitted that block.
The unit manifest (lines 1657-1676) has no H* obligation or per-member dose
identity/count obligation. An empty-family guard cannot detect partial loss.

From the otherwise agreeing full rehearsal:

* Delete **one** scored row's H* block, retaining the other H* blocks:
  comparator exit **0**.
* Delete **one** nominal H=1536 row from a registered logged H grid:
  comparator exit **0**.

Both mutations retain a valid engine leaf inventory. A dropped serialization
block or grid-construction bug can therefore remove the very quantity that
would disagree, while the remaining family still reports AGREE.

**Fix:** derive the expected member/convention/dose keys independently from
the roster and registered grids; require their exact coverage, including
null/unreachable cells and every required H* block. Count keys, not just
families or scored-member units. Do not widen the numerical bars.

Witnesses: `test_r26_missing_one_h_star_row_cannot_agree` and
`test_r26_missing_one_grid_dose_cannot_agree`.

### F3 — MEDIUM: the engine pin authenticates a record label, not its producer

`release_v4.py:141-158` checks the manually supplied record's engine commit
and hashes its files. It never validates the engine's recorded
`loaded_scorer_sha256` or `raw_reducer_sha256` against the pinned producer.
The comparator exempts these through `build_digests` (`claim()`, lines
1540-1542). Hashing an output against its run record does not establish
which code produced it.

Witness: replace both producer identities in the synthetic fill and its
matching thresholds file, update the inventory, and generate the ordinary
run record with its default pinned commit. The **entire release returns
exit 0 / AGREE**. This models recording outputs from a stale or modified
engine checkout under a default commit label. No recompute pin or numerical
bar is changed.

I did not run a second foreign engine in this witness; the demonstrated
failure is acceptance of explicitly foreign producer identities. A numeric
defect in such a producer would often be caught by comparison, but exempt
output is not covered by that protection.

**Fix:** verify the producer bindings against the pinned engine under the
actual interpreter (the scorer identity includes Python version), or run
the producer from a verified pinned checkout and bind the invocation to
the record. Checking that the supplied commit merely exists is insufficient.

Witness: `test_pinned_engine_identity_cannot_be_relabelled_in_the_record`.

### F4 — MEDIUM: referenced thermal journals are omitted from digest replay

The engine raw adapter accepts `journal` as a digest-bound reference and
reads it with `read_blob` (`raw.py:80-83`). Stage (a) promises to rehash every
raw-source reference, but `release_v4.py:172-184` visits only `episode`,
`powermetrics`, and `dc_streams`.

An isolated synthetic stage-(a) fixture records a journal digest, finalizes
the manifest and run record, then changes the journal bytes. Stage (a)
still reports **verified**. This is relevant to an incomplete restore or
sync after the engine run, without any manifest forgery.

This witness establishes the false integrity verdict, not that every
meaningful journal change survives the later numerical comparison. Such
comparison is not a substitute for the promised input binding.

**Fix:** include referenced journals in the same local-path and digest
checks. Audit the census against every raw-adapter reference type.

Witness: `test_changed_referenced_journal_refuses_in_digest_stage`.

### F5 — MEDIUM: malformed exports can exit 1 without a structure-only verdict

Authority: refused 2 > hold 1 > agree 0.

`release_v4.py:167` calls `.get` on an unvalidated census row; `release()`
and `main()` catch only `Refused`. A valid-JSON export with
`input_census: [null]`, correctly hashed by its run record, raises an
uncaught `AttributeError`. The actual release subprocess returns **1** and
no JSON verdict. That exit is reserved for a comparator HOLD.

**Fix:** validate nested input shapes and convert expected malformed-input
exceptions into fixed refusal codes. Keep exception details in the private
output. Check both the exit and the presence/shape of stdout in regressions.

Witness: `test_malformed_census_is_refused_2_not_an_uncaught_exit_1`.

### F6 — MEDIUM: copying the runbook command selects an obsolete recompute

`RELEASE-RUNBOOK-v4.md:49-52` still passes
`c0d1efcae85d4eae5967b2073ea0213f3a8a4d91`, while the wrapper requires
`de553c002879f93cdd32f15861f638a18dbd74f0`. Following the documented
command therefore refuses `recompute_commit_not_pinned` on valid custody.
This is an ordinary operator failure, with a direct text witness.

**Fix:** omit the optional commit flags to use the wrapper's pinned
defaults, or update the example and test it against those defaults.

Witness: `test_runbook_command_uses_the_release_recompute_pin`.

### F7 — HIGH: U5 mapping creates false HOLDs for valid signed slopes and deltas

Authority: A15; U5 remains descriptive and never triggers R20.

Both builds use the absolute slope for the point-shift decision. The
engine prints `point_shift_j = abs(beta_T) * delta_slow_c` and
`upper90_shift_j = max(abs(CI endpoints)) * delta_slow_c`
(`acceptance.py:235-242`). The recompute's `abs_upper_90` is the absolute
**slope** bound in J/C (`independent_recompute_v4.py:1756-1763`).

The comparator instead compares the point magnitude against signed
`beta_T * delta_slow_c`, and the interval-derived shift against the
unscaled slope bound (`compare_v4_recompute.py:1189-1195`).

Two otherwise agreeing synthetic output pairs demonstrate the failures:
reflecting the designed-state energies to give a negative slope produces
exit **1**; doubling delta from 1 C to 2 C, with both engine shifts scaled
correctly, also produces exit **1**. Negative estimated temperature slopes
are plausible, and non-unit delta is a supported thermal-policy setting.
The original rehearsal's positive slope and delta=1 hide both errors.

**Fix:** compare the point against `abs(beta) * delta`, and the upper shift
against `abs_upper_90 * delta`. Preserve the registered descriptive verdict
and numerical bars.

Witnesses: `test_u5_negative_slope_agrees_on_absolute_point_shift` and
`test_u5_interval_slope_bound_is_scaled_to_joules`.

## Other review coverage and limits

I read the adopted A0-A36 text at `a3465eda8`, the A15 override in RUN_STATE
230, A37 in item 233, and items 234-239 on local `origin/main`
`157a1d4c04288fab7d602a6a8f932a3f34813832`. No fetch or network was used.
The review covered the raw-export and clock rules (A0/A2/A10/A21/A37),
owned-energy OLS, count variants and within-window LOTO/full fits
(A1/A3-A6/A24-A26), known-H and carriers (A7/A8/R26), exclusion union and
thermal checks (A9/A11-A16/A22/A23/A28-A30), counts and tests (A17/A18),
W1 and DC mapping (A19/A20/A31/A34), and the explicit operational/print
exemptions (A32/A33/A35/A36). These are code-review coverage statements,
not proof over every possible real record.

The numerical bars match the signed interpretation table closely enough
that this review requests no relaxation. The demonstrated coverage gaps
and U5 unit/sign errors must be fixed before reconsidering tolerances.
The existing exact bootstrap, rank/member, eligible-m refusal, and empty
family controls pass their baseline tests.

For A27, the witness that adds a literal token count to a sealed scored
C-sabotage row **refuses 2** as unmapped; the literal is absent from public
stdout. A12's string-valued `not_applicable` release part also compares
correctly. In the tested wrapper, value-bearing outputs remain inside its
new mode-0700 output, and the existing release test confirms the public
verdict is structure-only. I found no demonstrated public C-sabotage
literal leak. This does not certify an external renderer or authorize
unsealing. Recompute reduction metadata still exists inside its private
output; an exporter must not treat the whole recompute JSON as public.

## Verification and handoff

All tests used Python 3.13, one module per process, on synthetic fixtures.
The cold common rehearsal generated its data in about 18 s, ran the pinned
engine in about 285 s and recompute in about 4.5 s. Total test time remained
well below 20 minutes; no full suite, Block-5 pipeline, measurement, model
download, real custody read, or MLX execution was attempted.

* `python3.13 -B -m unittest tests.v4_release.test_compare_v4` —
  **18 passed**, 333.717 s including the cold rehearsal.
* `python3.13 -B -m unittest tests.v4_release.test_release_v4` —
  **13 passed**, 12.938 s.
* `python3.13 -B -m unittest -v tests.v4_release.test_review_sol2` —
  preliminary 11-test version: 2 passed, 9 expected failures, 29.139 s.
* Final review module: loaded with
  `unittest.defaultTestLoader.loadTestsFromName('tests.v4_release.test_review_sol2')`
  and run by `unittest.TextTestRunner`, with each expected-failure traceback
  checked to be an assertion failure at the intended safety property.
  **14 tests: 2 positive controls passed, 12 expected failures**, 23.041 s.
  An intermediate 13-test version also ran this way (24.866 s).
* `git diff --check` — clean.

Expected failures assert the required safe behavior. They are **open
findings**, not passing safety tests; remove the matching decorator with
each fix. Baseline checks and the two positive controls pass normally.
The tests use fresh comparison/release invocations; the pre-existing cached
rehearsal is only an immutable synthetic input fixture. No production
decision cache or throughput change was introduced.

**Next exact step:** lead adjudicates F1 and installs the R22/R24/R25 policy
in both builds, fixes F2-F7, then runs these witnesses without expected-
failure decorators and repeats the full synthetic rehearsal before
re-pinning. This review does not amend the frozen engine or authorize a
real-data run. No new native/Metal test is needed for these stdlib tools;
real-custody and publication gates remain with the lead. Nothing was pushed.
