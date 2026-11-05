# Block-5 Results renderer — 2026-11-05

Branch: `lane/2026-11-05-b5-results-renderer`, based on local `origin/main`
`92026c184`. User-directed [AGENT] renderer work takes precedence over the
historical queue pointers; no stop card was active. The clone was clean and
detached at intake. No study energy, external user path or `restricted/`
directory was opened; no network, measurement, analysis driver, process
control, full suite, push or integration authorization was used.

## Delivered

`docs/process/b5_results_renderer.md` records authority, exact inputs, paper-tree
destinations, precision limits, provenance and remaining lead decisions.
`joulewise/b5_analysis/results_renderer.py` and `scripts/render_b5_results.py`
prepare a digest-bound leaf checklist, render a pending preview or checked
Results candidate, and validate the complete emitted bytes. The new
`docs/paper/block5/Results.template.md` contains the complete contrast census,
every contrast field, and literal released disclosures. It is not installed
in the submission build and grants no paper issuance.

The renderer reuses the comparator's structural/coverage gates on recorded
release outputs, checks the fill against its verdict parent and both views
against the disclosure record, and refuses missing/extra/changed content.
Concrete pointers and file hashes trace all values and text, with automatic
comparison keys, listed metadata or explicit manual-check status. Uncovered
numbers/nulls and all disclosure text require the post-release reader; reviewed
output additionally requires recorded release/Results-gate references. It does
not fabricate a human verification or independently authenticate those records.

All publication sites remain STOP_FILL / NEEDS-LEAD. No claim prose, new
headline selection, figure, arithmetic, scientific gate, bars, registered
wording or sealed file was changed. Raw outcome identifiers and registered
disclosure text are copied. Nulls stay null. D-189's 9b non-issuance is printed
and never becomes claim-evidence authority.

## Verification

Targeted unittest modules were run one at a time under Python 3.13, plus a
compile check and state/diff checks. The full suite was intentionally not run: the user's standing
rule protects the concurrent seven-worker job and overrides the repo default.
Synthetic fixtures were generated under TMPDIR; comparator tests use the
explicit `artifacts/` directory, never the comparator's usual restricted path.

The new tests exercise prepare/preview/render/verify, row and leaf census,
parent/file digests, deterministic disclosure views, per-leaf recompute joins,
stale/manual checks, wrong bars, numeric/JSON defects, symlink refusal and
failed-write cleanup. The real estimator/evaluator/finalizer/adapter builders
exercise all five outcomes plus a genuinely refused, null floor at the display
boundary. This is fixture evidence, not hardware or live release validation.

| Command | Result |
|---|---|
| `python3.13 -B -m unittest tests.b5_analysis.test_results_renderer` | 12 tests OK; synthetic prepare/preview/render/validate and refusal witnesses. |
| `python3.13 -B -m unittest tests.b5_analysis.test_step11_null_outcomes` | 9 tests OK, 1.219 s. |
| `python3.13 -B -m unittest tests.test_results_fill_adapter` | 6 tests OK, 0.142 s. |
| `python3.13 -B -m unittest tests.test_gen_state` | 44 tests OK, 2.806 s. |
| `python3.13 -B -m compileall -q -x '(^\|/)restricted(/\|$)' joulewise tests` | Exit 0; compilation only, restricted directory exclusion retained. |
| `python3.13 -B scripts/gen_state.py --check` | Exit 0; generated views agree with the kernel. |
| `git diff --check` | Exit 0. |

The initial new-renderer replay was 9 tests OK; structural-gate strengthening
then exposed two expected-error-code assertions and an untranslated comparator
refusal in those new tests. The API boundary and assertions were corrected.
Final replays include the added disclosure/write/null-gap witnesses (12 tests).
No baseline upstream scientific test failed. Repeated focused runs total well
under the user's 20-minute budget; Python 3.11 and the full suite were not run.

## Open questions / exact next step

**NEEDS-LEAD:** adopt the paper placements, issuing routes, registered claim
sentences, final digits and any figure/headline choices; run the actual Results
cold gate after authorized release. The renderer remains a working candidate.

**Existing independent-comparator null gap:** `Comparison.numeric` rejects
null contrast/floor values; the comparator's refused-arm-null regression at
`tests/independent_recompute/test_input_gate.py:522` intentionally expects an
unmapped-fill refusal. Some legitimate D-190 outcomes therefore cannot pass
the current upstream report. Renderer display handles them, but its CLI
preserves that failed gate. No bar or gate was waived. The lead must route a
reviewed comparator repair or govern a separate recompute disposition before
those releases can be filled end to end. This is a code/test finding, not an
inference about which state the blind study contains.

No phase exit-checklist row exists for this new bounded renderer task; no
phase completion is claimed. The live kernel carries the remaining lead
adoption/gate work. `RUN_STATE.md` and `TASK_QUEUE.md` record this lane and
regenerate from that kernel; advisor-facing scientific state is unchanged.
