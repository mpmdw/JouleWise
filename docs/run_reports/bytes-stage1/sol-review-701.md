# Independent Sol review of PR #701

Reviewed head: `ed2b2d72b3937b67c9c8e10690b302626ae0bb50`.
Review branch: `bytes/2026-11-07-sol-review-701` (already selected on intake).
Date: 2026-11-07 PST / 2026-11-08 UTC. Reviewer: Sol, independent of the
implementation session; no peer consult or delegation.

**Verdict: ADMIT_WITH_FIXES. Do not use the new driver on study inputs until
the pre-release and census defects below are fixed and reviewed. The merged
head also needs its Block-5 comparison boundary restored before analysis use.**
These are bounded driver/landing corrections, not a reason to discard the lineage.
No production code was changed by this review.

## Boundaries and authority

Read the local commit bodies, stage-1 plan, BYTES registration (especially
§§11–13 and 21), the freeze addendum, relevant code/tests, Mission M0,
orchestration, and targeted D-188 authority. The explicit review brief selects
this work over the ordinary queue. No active stop card was present.

No network, weights, real measurement archive, real withheld store, held-out
outcome, stage-2 outcome, Block-5 analysis pipeline, or quiet-machine operation
was used. Absolute data paths in tracked text were not followed. Git object
reads used this clone's ordinary object access; no other checkout was opened.
All executable data probes used temporary synthetic files. No keys, including
real fit keys, were released. Coordination files were left untouched as ordered.
The estimator SHA-256 is the registered
`18582818c7e03bad148b54dce8b8d60a62e2ffc5597e701ae3ab0418dffc0a71`.
The registration text and Block-6 catalog also reproduce their stated digests
(`4fd5f0ea…daf9800` and `01767fe4…9a1dd0c`, respectively).

## Findings requiring disposition

### F1 — P1: refusal disagreement is detected after releasing fit keys

`scripts/bytes_stage1.py:270–279` runs both no-key probes, but checks only
whether either exit is zero before calling `release_fn`. Exits **1 and 2**
both pass that check. The registered comparer checks exact equality of these
exits (`tests/test_bytes_agreement.py:1278`), but is next called only **after**
release and keyed analysis. This violates §12's exact exit-code agreement and
the promise to attribute a disagreement before release. An unrelated failure
or a killed no-key probe also counts as a successful refusal today.

The independent `test_no_key_refusal_exit_mismatch_stops_before_release`
injects different nonzero exits and reaches a release trap. It copies no key.
Fix: compare the no-key results before release and require the intended
missing-key refusal, with an explicit stop on mismatch or execution failure.

### F2 — P1: recursive census can open a nested withheld CSV

`scripts/bytes_stage1.py:73–78` recursively inventories every CSV. It excludes
only a table whose **immediate parent** is named `withheld`. The registered
layout is `withheld/<pack>/<session>.runs.csv`, whose immediate parent is the
pack. If a visible CSV is missing/misplaced but its sidecar remains, a table
in that nested layout is paired with the sidecar and opened at line 128.
Ordinary duplicate-visible-and-withheld layouts refuse, but that does not
establish the stronger claim that no store is ever opened.

`test_nested_withheld_directory_is_never_opened_as_visible_export` moves one
synthetic visible table to that layout and traps the attempted open. No real
store is involved. Fix: constrain visible table discovery to the documented
export layout, exclude withheld subtrees before traversal/open, and reject
CSV/store path aliases. Check the downstream analysis/twin discovery too,
since the driver hands the directory roots to them.

### F3 — P2: a missing withheld file is made a new stage-1 refusal

`scripts/bytes_stage1.py:122–124` appends its absence to `reasons`; census
therefore returns REFUSED, and `main(run)` stops. §11 item 4 explicitly says
the missing store is a recorded `bytes.withheld_missing` condition and **no
stage refuses**. The explanation in the new error text does not provide a
registered override or a way to acknowledge it and continue. The original
test currently asserts the new refusal rather than the registration.

`test_missing_store_does_not_refuse_under_section_11_item_4` demonstrates
the conflict. Fix: retain the structural disclosure/counts, permit stage 1,
and preserve the registered later missing-cell/one-pass behavior. Amend the
operator plan's stop instructions to agree, or obtain an explicit registration
disposition before changing this rule.

### F4 — P2: timing-closure check recognizes only one clock column

`CLOCK_COLUMNS` at line 54 contains only `run_start_utc`. A CSV with
`run_end_utc` passes census. §11 item 2 forbids that column **or any other
clock**, because reference gaps expose withheld durations.
`test_other_clock_column_also_refuses_under_section_11_item_2` reproduces it.
Fix: validate the permitted pre-commit schema, including a bounded rule for
clock-bearing columns, rather than treating one known column as exhaustive.

### F5 — P2: missing blinded products can satisfy an exit-only comparison

The comparer at `tests/test_bytes_agreement.py:1282–1283` skips all blinded
cell/NEG-8 comparisons when the twin product or analysis directory is absent.
The driver checks `above()` but does not require those products/comparison
groups. With both blinded exits zero and both products absent, it reaches
release after checking only equal exit records. This is a missing-output
mistake probe, not evidence that the current unmodified child programs
normally omit their products.

`test_missing_blinded_products_cannot_count_as_agreement` uses the **actual**
registered comparer and a stub child launcher to reproduce that gate gap.
Fix: require the expected blinded artifacts and substantive comparison groups
before release. Apply the same completeness requirement to the final fit
comparison, whose optional-file branches have the same shape.

### F6 — P2: the five-file landing's blanket Block-5 inertness claim is false

`tests/b5_analysis/test_frozen_files.py:23–29` calls every edit inert for
Block 5, including the runner hooks. The hooks are selected by `hazard is
not None`, without a Block-6 pack selector. `_hazard_effective_wait_cap`
returns **1500 seconds** for an old enabled `IdleAdmissionPolicy` with no
new wait settings; `run_campaign.py:11214` adds it to the old 1800-second
member timeout. The new pause and per-member sleep-clock/flag hooks likewise
execute on the shared HAZARD path. A future Block-5 run at this head would
have different acquisition timing/behavior. The independent
`test_legacy_idle_policy_now_extends_hazard_timeout` records this counterexample.

This does **not** establish a change to already collected Block-5 outcomes:
their collection ran at pinned historical commits, and the reviewed desk
paths do not launch a new campaign. Fix the freeze/rebind justification to
state that narrower boundary, explicitly bind Block-5 collection to its old
commit, or gate the new collection behavior to Block 6. Do not use the rebind
test's passing hashes as a proof of semantic inertness or D-188 equivalence.

### F7 — P1: the merge applies Block-6 comparison tolerances to Block 5

The merged `joulewise/b5/harvest.py:1042–1048` changes `_close` from
`rel_tol=1e-9, abs_tol=1e-9` on main to `rel_tol=0, abs_tol=1e-3` without
checking the block. `neg8_bound_member_problems` calls it for every bound
member's rederived gross and idle-subtracted points (lines 1022–1024).
The sealed Block-5 registration's member check (vii),
`configs/campaigns/v5_claim_25g83/registration_block5.md:2877–2879`, explicitly
requires relative and absolute tolerances of **10⁻⁹**, and the same paragraph
says failure removes the window under `neg8.bound_not_derived`.

The independent
`test_b5_neg8_member_comparison_keeps_registered_one_e_minus_nine_bar` shows
that points 1.0 and 1.0005 now compare equal. Main's registered comparison
rejects them. This is a numeric admission difference, not merely an audit
artifact. The lane's `6ae3965bf` deliberately introduced the Block-6 bars;
that does not authorize changing Block 5's registered rule at this merge.
Shared `whole_window` stored/fresh reference checks also adopt the 1 mJ bar
at lines 5576/5585, and calibration scalar checks expand from 1 ns to 1 us
at lines 2134/7110. Those shared changes need the same scope audit.

Fix: keep the historical Block-5 comparisons and select Block-6 tolerances
only on an explicit Block-6 path, or install the required authorized ruling
and equivalence disposition. Do not run a fresh Block-5 analysis at this merge
head on the strength of the frozen-file hash rebind. I did not inspect study
values and cannot say whether any actual member falls between the bars.

## Answers to the requested review questions

**(a) Literal respelling:** no new reason emission is hidden by these two
particular spellings. `busy_fraction_admitted` is a metadata key used by the
Q3 controller-admission predicate, not a returned refusal code.
`compression_records` names a restoration-journal keyword, not a refusal.
`"busy" + "_fraction_admitted"` evaluates to the same key, and
`dict(compression_records=...)` supplies the same kwargs as the former dict
literal. The generator scans every snake-case string constant, including
metadata keys, so those keys are false positives for its reason-code purpose.
The Q3 behavior and restore behavior themselves are real earlier lane
changes and must be reviewed on their merits; the unchanged literal census
does not prove them equivalent. The registered mask/R3 classification is
unchanged. Prefer a documented exclusion for non-reason keys in a future
properly authorized census revision over accumulating opaque spellings.

**(b) Five frozen files:** `catalog.py` adds proposals; `load_catalog` still
uses the sealed file and never falls back to `DRAFT_CODES`. `core.py` adds
code family/class lookup entries without changing old entries.
`exclusions.compute` retains `pack_scoped=True`, and the sealed Block-5
`cell.below_minimum` effect is still EXCLUDE_WINDOW, so its new effect check
does not change that valid-catalog case. The independent synthetic loss sweep
compares all outputs with main's old exclusion function for 0–10 lost quads.
`harvest_b5_window.py` adds a StorageStop exit for new compressed-restore
failures; ordinary plain inputs keep their previous path. `run_campaign.py`
is not universally inert (F6). Historical pinned collection is a valid
isolation argument; universal runtime equivalence is not.

**(c) Eight added pre-harvest codes:** correct, registered in the Block-6
catalog and all twelve BYTES pack effect maps; the three replication
registrations also carry the same effects. They intentionally are not additions
to the sealed Block-5 catalog. The core candidate is
`calibration.acceptance_preflight_unverified` (DISCLOSE). The seven driver
candidates are `agent.capture_overlap`, `agent.presence`,
`agent.presence_overlap`, `sleep.assertion_lost`, `sleep.assertion_unverified`,
`sleep.in_chain`, `sleep.reading_unmeasured`. Only the two presence codes are
EXCLUDE_MEMBER; the other five disclose. `agent.presence` is a window-scoped
interval fact with a member-exclusion effect, so only overlapped members are
excluded, and the unit rule drops their complete quad. The independent probe
checks that behavior with the production exclusion function. RF-3 candidate
coverage must include it even though the harvest does not emit it itself.

**(d) Driver:** normal census does not interpret or report energy/power/duration
values: deliberately nonnumeric energy/power strings pass, and an open spy
sees only sidecars/visible CSVs in the normal separate-store layout. This is
semantic blindness, not a claim that CSV energy bytes are never read into
memory: `DictReader` parses complete rows. Store existence is statted; a normal
locator is not opened. The universal no-store-read claim fails F2. Standard
held-out identity and `run_start_utc` refusals fire, but F3/F4 need correction.

The successful synthetic integration follows blinded analysis/twin → comparer
→ no-key probes → fit-only release → fit analysis/twin → comparer → exact
prediction-file hash check → READY_TO_COMMIT. It neither commits predictions
nor invokes a held-out release, stage 2, or `--stage1-commit`. Normal release
is precisely the three fit config keys plus `neg8_reference`; the production
release helper independently rejects held-out keys and never draws missing
ones. Synthetic injected blinded failure/disagreement and no-key success all
stop before the release trap. F1/F5 prevent an unconditional claim that
**every** refusal/disagreement stops before any release. §11 requires fit keys
to be released before producing predictions; only held-out keys wait for the
commitment. The plan correctly keeps the live run on the separate registered
run branch, not this merged head.

**(e) Merge preservation:** no accidental source loss found in the inspected
merge resolutions. The initial merge is `003f6e12a` (parents `c88b45ced` and
`5c66a5199`, base `e9aab7ba1`); the final main merge is `ed2b2d72b` (main
parent `722f3a293`, base `20413903b`). Blob-map comparisons over
`joulewise/`, `scripts/`, `tests/`, `configs/` found no unilateral production
code change discarded by either merge, or the three intervening merges.
The initial merge's four unilateral deviations are intentional test edits:
auth-recorder refusal-site count, frozen-file rebinds, inverted-corner-clamp
test's digest rebind, and thermal replay normalization. Across the complete
Git tree, the only additional unilateral deviations are the documented
CANONICAL row, freeze addendum, and KB registration slot fill. Source paths changed on
both sides were inspected for main's D-188/authentication/cache paths plus
the lane's readable-run, compressed fallback, and StorageStop paths. The final
merge's only overlapping path there is `tests/test_analysis_integration.py`;
it preserves main's campaign-level fixture rows and the lane's unreadable-I/O
mock-seam correction. BYTES estimator/twin/thermal
driver and `joulewise/b6/` bytes are unchanged from the initial run-lane parent.
This is a bounded code/merge audit, not an exhaustive equivalence proof of
the thousands of imported documentation/configuration artifacts or study data.
It does find a substantive main-policy regression: F7's shared comparison
change loses main's registered Block-5 refusal boundary even though neither
parent's source files were accidentally dropped.

## Verification

All commands use Python 3.13 with `-B` for tests. The full suite and
`tests.test_bytes_analysis` were deliberately not run under the binding
machine-load/test-budget rule. No hardware validation is claimed.

Each table row is a separate process running
`python3.13 -B -m unittest <module>`; times are unittest's reported seconds.

| Module | Result | Seconds |
|---|---|---:|
| `tests.test_bytes_stage1` | 10 passed | 86.949 |
| `tests.b6.test_audit_record_fixes` | 8 passed | 229.305 |
| `tests.b6.test_capture_list` | 4 passed | 0.239 |
| `tests.b6.test_blinding` | 12 passed | 0.447 |
| `tests.b6.test_survivor_screen` | 14 passed | 0.012 |
| `tests.test_fix573f_restore` | 14 passed | 201.368 |
| `tests.test_fix573g_restore` | 10 passed | 73.499 |
| `tests.test_bytes_stage1_sol_review_701` | 11 passed, 6 expected failures | 1.525 |
| `tests.b5_analysis.test_frozen_files` | 4 passed | 1.078 |
| `tests.b5_analysis.test_step4_reason_table` | 8 passed | 5.275 |
| `tests.b5_analysis.test_auth_recorder_and_verdict_memo` | 34 passed | 0.753 |
| `tests.test_harvest_b5_window` | INCOMPLETE: timed out at the aggregate budget; 53 progress dots, no printed failure | 560.956 (process wall time) |
| `tests.test_harvest_b5_window.PreHarvestCodeTests` | 8 passed | 0.262 |
| `tests.b6.test_bytes_p2_thermal_window.ThermalWindowTests` | 9 passed | 0.446 |
| `tests.flags.test_flags_exclusions` | 34 passed | 0.635 |

The initial 14-probe draft run (1.921 s) briefly overlapped the audit-record
module for about two seconds. That was a scheduling error, disclosed during
the review; the completed 17-probe file and subsequent modules ran serially.
The serial batch had an 850-second wall-time cap; after its timeout, a separate
18-second-capped focused batch finished in 3.581 seconds. Including the first
stage-1/audit-record commands and the draft probe, aggregate test time was
about **19.6 minutes**. Completed final commands account for 180 passes and
six expected failures. The incomplete module is not counted as passing.
The full thermal replay module was not started after the cap; only its
explicit nine-test pure-window class ran. Full harvest/thermal replay remains
for CI or an authorized later session.

`PYTHONPYCACHEPREFIX=/private/tmp/jwsol-review701-pycache python3.13 -m compileall -q joulewise tests`
and `git diff --cached --check` are the final cheap syntax/whitespace checks.

## Handoff

Changed only this report and `tests/test_bytes_stage1_sol_review_701.py`.
The six expected-failure probes encode F1–F5 and F7 as desired safety invariants;
they are visible known defects, not passing evidence for those invariants.
Remove each decorator when the corresponding production fix is made.

Next exact step: lead dispositions F1–F7, restores the Block-5 comparison
boundary, and fixes the accepted driver defects on
the **run branch as well as the merge branch**, then reruns these probes and
the synthetic stage-1 integration. Preserve §11's commitment boundary and
obtain the normal independent fix review. Run broader CI off this busy Mac.
No native MLX test was required by the review's test/report-only changes;
native acquisition/equivalence remains with the lead on the appropriate
pinned checkout outside this sandbox. No unresolved science ruling is
invented here; missing-store policy must follow §11 unless the lead installs
an authorized amendment. Real-data and full-suite equivalence remain unverified.
