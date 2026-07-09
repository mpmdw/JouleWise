## ATTACKS

1. **BLOCKER — The proposed RUN_STATE repair preserves a decision-log violation.**

   The synthesis calls `RUN_STATE.md:91-96` “**correct**” and contrasts it with the stale Wave-2 block ([synthesis](/private/tmp/claude-501/-Users-edr-code-JouleWise/e48cf22e-209a-4355-bb28-9b6a37636b34/scratchpad/synthesis-draft.md:52)). The META lens says the opposite:

   > “RUN_STATE ... says the `[AGENT]` lane should take P2-022/P2-023, while simultaneously admitting their post-2M sequencing; binding D-041 explicitly keeps both post-2M.”

   ([META lens](/private/tmp/claude-501/-Users-edr-code-JouleWise/e48cf22e-209a-4355-bb28-9b6a37636b34/scratchpad/lens-meta.md:16))

   D-041 is unambiguous: shim and import work “**are post-2M**” ([decision log](/Users/edr/code/JouleWise/docs/decision_log.md:2050)). Therefore the first restart block is not correct; it advertises blocked work as the next agent lane. Deleting only the second block would leave the more dangerous contradiction in place. The correct repair is one generated restart pointer whose `[AGENT]` result is currently “no unambiguously READY item; repair/clarify queue.”

2. **BLOCKER — This is not an adjudication because it lacks a complete disposition table.**

   The synthesis lists B1–B8, seven severity notes, and several discussion items, but never maps every lens finding to accepted/rejected/deferred/duplicate/false-positive status. “Add queue rows for every accepted finding” is non-executable because “accepted” is not enumerated. The repository’s council rule requires counts and a `finding → ruling → owner → target → closure check` table ([orchestration](/Users/edr/code/JouleWise/docs/orchestration.md:185)).

   Material findings disappear into this gap: RIGOR’s missing production clock/drift evidence path, STATS’s unspecified D-054 small-sample factor, TOPDOCS’s D-058 stack-table violation, ARCH’s remote integration/conformance gap, and REVERSE’s stale status-authority closures. Folding some into “contracts without an engine” does not provide ownership or closure criteria.

3. **BLOCKER — The synthesis identifies the statistical-engine gap but fails to put it in front of Window A.**

   The immediate actions are bookkeeping-only, yet the next quiet-machine action is P2-015. That is unsafe sequencing:

   - No production code writes `clock_anchor_bound_s` or `idle_drift_bound_w`; only tests synthesize them.
   - No floor calculator, artifact validator, ABBA implementation, contrast engine, or frozen analysis manifest exists.
   - D-054 requires the `5 <= n < 10` guard factor to be pre-registered, but the factor is still unspecified.
   - `run_campaign` calls any all-usable membership set “publishable,” including one bundle.

   This is not merely missing Phase-4 reporting machinery. It affects whether Window-A bundles can exercise the claimed fail-closed path and whether a failed-repetition calibration cell can be evaluated without post-data discretion. At minimum, freeze the guard factor, produce the required metadata in the real Mac path, and validate a versioned floor artifact before P2-015 proceeds beyond smoke. Before P2-006 interpretation, the contrast/claim engine must exist.

4. **SHOULD-FIX — The synthesis overstates the legacy-gate finding.**

   The synthesis says:

   > “None of the six existing real bundles passed the advertised gates.”

   ([synthesis](/private/tmp/claude-501/-Users-edr-code-JouleWise/e48cf22e-209a-4355-bb28-9b6a37636b34/scratchpad/synthesis-draft.md:31))

   RIGOR actually says:

   > “The claim ladder explicitly leaves historical claims under manual review,”

   and recommends:

   > “Treat all six existing bundles explicitly as legacy L1 observations with documented waivers.”

   ([RIGOR lens](/private/tmp/claude-501/-Users-edr-code-JouleWise/e48cf22e-209a-4355-bb28-9b6a37636b34/scratchpad/lens-rigor.md:27))

   D-037 binds claims “from Slice 2M onward,” and L1 requires three strict-valid bundles plus scoped provenance—not the later L2/L3 floor/contrast engine ([claims ladder](/Users/edr/code/JouleWise/docs/contracts/claims_ladder.md:3)). D-054 also explicitly says unknown terms do not block L0/L1 ([decision log](/Users/edr/code/JouleWise/docs/decision_log.md:2636)). The legacy headlines need correct denominators, basis labels, stack identity, L1 labeling, and waivers. Saying they “failed” a later inapplicable gate invites an unnecessary ex-post-protocol defense problem.

5. **SHOULD-FIX — B6’s exact verification claim is false, although the D-031 breach is real.**

   The synthesis says all four commits were “verified to contain code+tests” ([synthesis](/private/tmp/claude-501/-Users-edr-code-JouleWise/e48cf22e-209a-4355-bb28-9b6a37636b34/scratchpad/synthesis-draft.md:59)). REVERSE says only that `36d5641` contains a 33-line `build_site.py` behavior change mixed with deployment output ([REVERSE lens](/private/tmp/claude-501/-Users-edr-code-JouleWise/e48cf22e-209a-4355-bb28-9b6a37636b34/scratchpad/lens-reverse.md:48)). Git confirms `36d5641` has code but no test file.

   The substantive ruling survives: all four are non-bookkeeping direct-main commits and therefore breach D-031. The synthesis must say “three code+test commits and one untested code/site commit,” not manufacture stronger uniform evidence.

6. **SHOULD-FIX — The ARCH trio needs split severity.**

   The zero-length successful strict bundle is an immediate core-path blocker. The SSE token-count and NVIDIA raw-lineage defects are real, but they are gated blockers for claim-bearing NVIDIA/Jetson execution; those paths remain explicitly provisional. Treating all three as undifferentiated project blockers distorts current critical-path priority. They should be hard acceptance gates on P1-006/2K live promotion, not reasons to delay Mac Window A.

7. **SHOULD-FIX — Invocation recoverability is asserted, not demonstrated.**

   The repository manifest has exactly two `/bin/echo` smoke rows, while the required role/model/report fields are missing. That part is confirmed. But the synthesis additionally asserts that “real evidence exists in codex-run’s observer index outside the repo” without an inventory, stable pointer, or hash. The lens reports do not establish that all claimed invocations are recoverable. The remedy should begin with a recoverability audit and label each invocation `recovered`, `partially recovered`, or `unrecoverable`; it must not state recoverability as fact first.

8. **SHOULD-FIX — The corrective action omits the required historical addendum.**

   “Living docs only” is insufficient. Both TOPDOCS and RIGOR require an append-only correction to the dated 2026-07-06 report. History must not be rewritten, but an addendum should state that the old `energy_token_j` row used prompt-plus-output tokens and give the corrected output-token values. Otherwise the same incorrect table remains an authoritative-looking evidence pointer.

9. **SHOULD-FIX — The new-model calibration note is premature and self-contradictory.**

   The note proposes proceeding to a sealed A/B while simultaneously making 5.6-sol-xhigh the default review model immediately. “7/7 returned OK,” output length, and absence of stalls measure completion, not adjudicated precision. This counterreview has already found one synthesis blocker caused by misreading a lens and one false exact verification statement. Record this as one promising calibration batch; do not change default doctrine before the pre-registered comparison.

## SPOT-CHECK RESULTS

| Item re-verified | Result | Evidence |
|---|---|---|
| B1 token denominator | **PASS** | README says 77–88 mJ/generated token, while the three small-model `energy_output_token_j` values are 79.397, 90.463, and 90.448 mJ. `energy_token_j` uses the total-token denominator. |
| B3 “first restart block is correct” | **FAIL** | The stale Wave-2 block is real, but the first block also violates D-041 by naming P2-022/P2-023 before 2M. |
| B4 missing claim machinery/unowned obligation | **PASS** | No paired/block contrast or floor evaluator exists in `joulewise/`; the reducer checks presence, not floor/effect magnitude; no queue row owns the integrated engine. |
| B4 one-bundle “publishable” | **PASS** | `verdict_for()` returns `publishable` whenever all evaluated members are usable; the test fixture exercises this with one bundle. |
| B5 invocation manifest | **PASS** | Two smoke rows only; both pending; missing `parent_report`, `role_or_lens`, and `model`. |
| B6 four D-031 breaches | **PASS** | All four are first-parent, direct-main, non-bookkeeping code commits. |
| B6 “all four contain code+tests” | **FAIL** | `36d5641` changes `scripts/build_site.py` and generated/site artifacts but no tests. |
| B7 vLLM chunk counting | **PASS** | `_run_vllm_runtime()` increments `token_count` once per streamed text piece; its test hardcodes `["A","B","C"]`. |
| B7 raw-lineage scope | **PASS** | Strict raw-to-trace reconstruction is powermetrics-specific and returns early for normal NVIDIA raw artifacts. |
| B7 zero-window success | **PASS** | Reducer explicitly returns a successful zero summary; strict sampling checks run only when duration is positive. |
| B8 outcome-dependent top-ups | **PASS** | AP rows trigger top-ups based on observed near-floor CIs, LOO changes, and rank/crossover behavior. |
| B8 empirical-min comparator | **PASS** | Split Q1 defines `split - min(monolithic_prefill_node, monolithic_decode_node)`, creating post-observation comparator selection unless inference handles both references jointly. |
| B8 legacy claims “failed advertised gates” | **FAIL** | Those later L2/L3 gates were not applicable to the pre-2M observations; the correct disposition is legacy L1/manual-waiver labeling. |

## POSITIONS

### Q1 — Stage the migration, but make the machine-readable state kernel Stage 1

The synthesis presents a false choice between big-bang migration and deferring structured state. Do neither. Introduce a minimal machine-readable kernel now containing task ID, lane, status, dependencies, authority, acceptance pointer, and stop-card pointer. Generate the sole restart block and live queue view from it. Do not migrate history, completed rows, current policy, findings ledgers, and every status document simultaneously.

Deferring the kernel while first generating `current_policy.md` leaves the demonstrated failure mode—two hand-maintained next-action blocks—fully active. Policy generation is also harder than state generation because decision supersession requires semantic judgment. The thin state kernel is the lowest-risk first vertical slice and immediately closes the drift window.

### Q2 — “Three applicable sessions, severity-weighted” is not enforceable as written

“Applicable” simply moves discretion upstream. A layer can be protected by declaring failed sessions inapplicable, or killed by counting low-exposure sessions. “Severity-weighted” is equally gameable unless weights and duplicate rules are frozen.

Applicability must be determined before results are known from mechanical predicates. For example, integration review counts only when at least two independently developed streams merge and touch a shared consumer, contract, generated artifact, or dependency surface. Outcome taxonomy must keep accepted unique defect, duplicate detection, clean verification, and false-positive suppression separate; suppression is useful but is not a “catch.”

Three exposures may trigger review, but not automatic deletion. For rare high-loss controls, three is plainly too small—the observed zero/zero/five sequence proves it. Require a predeclared exposure predicate, fixed severity weights, measured review cost, and an explicit expected-loss decision. Safety/final-head/integration controls should not be auto-dropped solely for zero observed defects.

### Q3 — Freeze n for confirmatory work; alpha spending is optional, not the default

For this capstone, fixed-n confirmatory analysis is easier to defend than combining group-sequential monitoring, Holm/BH families, detection floors, LOO sensitivity, and small-sample block inference. Use independent Window-A variance/MDE evidence to choose each later pack’s n before observing that pack’s effects. Predeclare replacements for technically invalid runs; do not let effect size, CI direction, floor proximity, or LOO instability trigger confirmatory additions.

The proposed demotion rule is coherent only if made explicit:

- Once an outcome-dependent top-up occurs, that contrast loses confirmatory status.
- Preserve and report the original fixed-n analysis regardless of its direction.
- Pooled original-plus-top-up estimates are exploratory; an ordinary “95% CI” may be descriptive but must not be presented as retaining nominal confirmatory coverage.
- No later claim can regain confirmation merely because the topped-up interval becomes convenient.

A simple pre-registered two-look alpha-spending design would also be valid and is not mathematically enormous, but it adds avoidable defense surface. Use it only for a specifically justified expensive campaign, with maximum n and look boundaries frozen. The default should be fixed n, probably closer to 10 than 5 for near-floor comparisons.

### Q4 — The stop-line direction is right, but its gates are simultaneously too soft and too rigid

It is too soft scientifically because it omits the executable floor/contrast/claim path. It is too rigid operationally because an unavailable external rubric could freeze all breadth indefinitely.

I would amend the gates as follows:

1. **Rubric/calendar:** obtain them by a hard date; if unavailable, adopt and record a provisional grading contract and conservative internal deadlines. External silence must trigger scope fallback, not indefinite paralysis.
2. **Backup:** hard gate before retaining any new irreplaceable campaign evidence. Require off-machine destination plus restore proof. It must not block report drafting, analysis tooling, or correctness fixes.
3. **Window A:** expand this gate to include smoke, frozen sampling rule and small-n factor, production uncertainty metadata, versioned floor calculation, floors, baselines, and an executable contrast/claim-readiness path before L2 interpretation.
4. **Vertical slice:** require a real report source skeleton and a reproducible `bundle → analysis artifact → figure/table → claims-index row → report page` path. Legacy bundles may test mechanics, but the page must label their legacy L1 status.

This should be an append-only amendment to D-041/D-052 and R-012, not a new free-floating stop line competing with three existing authorities. “No new breadth” should still permit work that closes these gates, correctness defects, report writing, and already-obligated hardware preparations.

## VERDICT

**With changes.** I would sign only after:

- Correcting the D-041 restart adjudication.
- Adding the complete finding disposition/ownership table.
- Making statistical production evidence and floor/contrast tooling pre-Window-A gates.
- Reclassifying legacy results as legacy L1/manual-review evidence rather than failed later gates.
- Splitting immediate versus remote-gated ARCH severity.
- Correcting the D-031 `code+tests` overstatement and qualifying observer-index recoverability.
- Adding append-only historical claim corrections.
- Replacing the process/state, layer-drop, sequential-sampling, and stop-line language as argued above.
- Removing the immediate model-doctrine promotion pending the sealed comparison.

**CHECKS PERFORMED:** Read the synthesis and all seven lens reports; inspected D-031, D-037, D-041, D-050, and D-053–D-059; checked current state/queue/contracts, six real summaries, reducer/campaign/strict/NVIDIA code and tests, invocation manifest/schema, and Git objects for all four cited commits. Read-only only; no files changed, tests run, hardware commands, or network calls.