# apply-r11 — Track 1 handoff

Brief date: 2026-11-08. Branch: `align/2026-11-08-v4-r11`, provisioned at
`6daa3d657` (the registration build). **Not registered; W1 cannot arm.**
No network/fetch, weights, real measurement data, Block-5 pipeline, external
study paths, process census or hardware probes were used. Coordination files
and R1's lane/pin are unchanged. All execution evidence below is synthetic.

Authority read from local Git objects: RUN_STATE 202–210 and **212** on
`origin/main` at `bfaf119f2c912921d37a12712fa6cb7338bb1b70`; adopted
AGREEMENT-FINAL Track 1 at `4526de7d587a412073cf792c959090401e8d4797`.
The requested design, reviewer2, registration, tripwire-directions and prereg
refs were available locally; no remote freshness is asserted. Protocol v4,
energy residual, chair/lead rulings, M0, decision-log and orchestration text
were read. Absolute data locations in source text were never followed.

First merged `origin/align/2026-11-07-km003c-align` at `1c5a790f2`:
**`199006f16`**, “Merge KM003C capture checks and secondary DC desk into v4
registration.” Resolved the session hook by preserving both registration and
secondary DC reporting, including on missing-registration evidence. Rebuilt
the two conflicting generated digests. The meter test's old single-gate
expectation was updated to preserve the independent registration gate.
R11 changes are in the subsequent commit containing this report (`git log -1`).
No push or publication occurred.

## One R-item disposition and evidence map

DONE means the specified code/text repair is present, not native qualification.
PARTIAL names the remaining gate; OPEN denotes an unresolved scientific or
lead-owned choice. Protocol v4 and LEAD-RULINGS-2 Round 11 cite RUN_STATE 212
and point here. The pending registration receipt binds current/committed
protocol, deviations, rulings, kit/desk/runtime code, inputs/plan, identity
inventory/verification, U3, WP19 and both gate reports; it supplies no approval.

| Item | Status | Implementation / retained coverage; remaining work and owner |
|---|---|---|
| R01 | PARTIAL | Existing exact-candidate receipt/admission retained; added lead-rulings, budget-procedure, meter and identity-artifact bindings. `v4_registration`, kit/session and receipt template; receipt drift tests pass. Lead still owes actual native inputs, deviations/access chronology, Stage A/B independent gates and signature. No header/signature is treated as execution evidence. |
| R02 | PARTIAL | `battery_arm` uses required **InstantAmperage**, allows absent optional Amperage, refuses missing SoC/current, keeps ≥99%, freshness, completed-top-up/OBC evidence requirements and charging exclusion. Removed the builder's unruled separate ≤1 B bar: counts remain, `bar_pass=None`. Lead/Ed own the numeric window consequence, actual top-up timing/OBC and whole-window battery-flow evidence. |
| R03 | OPEN | **No k=3, 2.576 or fixed energy floor.** U3 export is descriptive/PENDING; old constant receipts are refused and v4 never falls back to v3's margin. Protocol contains the predictive/OC/dependence/D-transfer derivation block. Lead/statistics must supply and freeze the derivation, then scoped implementation and independent admission. This is deliberately not a usable numeric bar. |
| R04 | PARTIAL | Retained distinct controlled-state/drift/precision semantics, W1-in-U4, 5/17, c=1 U5, clustered U6/per-position eligibility and imprecision labels. Pending U3 is INCONCLUSIVE. No new U5 diagnostic waiver adopted. Lead/statistics owe U6 OC at the actual final Q6 roster and the D-series desk gate. |
| R05 | PARTIAL | Correct 5/17 identity and existing completed/clean/≥3-turn sentinel admission retained. Alternate 18 no longer prints a singleton E_ref; neither valid source gives unresolved, not automatic extension recovery. Diagnostics mark final-policy comparison required. Lead must qualify final model/stack/policy comparability and any matched alternate reference/recovery; no native source was inspected. |
| R06 | DONE | V4 delivery is now checked **per template**, retaining eligible eight-row stage-adjusted fit, 3 residual df, positive d_X/d_Y and ruled rejection band. One template cannot borrow the other's delivery. Existing v3 fit remains unchanged. `test_v4_r11` and registration/thermal-desk tests cover this. No native T verdict is claimed. |
| R07 | PARTIAL | **R11-2 choice implemented:** own contrast cap and bound `contrast_fit` on receipt/no-receipt paths; failed/incomplete proof is predeclared non-veto INCONCLUSIVE in procedure and both desks. Explicit R10 (iv)/MEDIUM-2 contrast-only supersession recorded. Missing/nonpositive remaining cap gives zero-cap G0 timeout; capped predecessor-heat change disclosed. Partial native X cannot pass WP19. Lead still owes all-turn X/Y/native identity and review of actual changed heat history. |
| R08 | PARTIAL | Bare fallback step+authority cannot admit; 450-s/4-bit steps refused in this kit. A changed S6 needs a new passing measured record. Passing duty labels require explicit no-X7 evidence. No budget-X7 exception adopted; any later exception needs completed-turn evidence including missing/censored cases. Lead owns actual fallback remeasurement/qualification. |
| R09 | DONE | Existing checkpoint-off/all-transition rewrite split and actual fed/rebuild accounting retained; cache tests pass. Rebuild/no-rebuild sensitivity remains printed. No redundant R0 tool or native qualification claim added; owning native cache gate still applies. |
| R10 | PARTIAL | **R11-2 seed choice retained:** `qwen3.8-27b`, explicit 8-bit label/deviation, no pooling/CRN inference. Kit binds R0 record digest to sensors. Desk adds source/revision, observed MLX/MLX-LM/artifact identity and effective execution/thermal-policy hashes beside four fixed slots; missing identity fails. Lead must fill `R0.record_sha256` and verify full stack/final-policy transfer and actual prior access history. Recorded runtime fields alone do not qualify the entire stack. |
| R11 | PARTIAL | By-day source/config/digest/time-bound receipts retained; removed invented 24-h duration. Require prospective lead-signed `daytime_offload_freshness` in config/receipt, no default. Empty-offload waiver and arm census retained. **No qualified continuous mount-event collector/audit exists here**; lead/measurement owner must qualify full-span coverage and missing-evidence consequences. Polling or `/Volumes` alone is insufficient. Meter attachment is not a mounted disk. |
| R12 | PARTIAL | Retained align-local unobserved-R refusal before model prepare, failed custody, SystemExit observer absorption/KeyboardInterrupt latch and power restore. Protocol records accurate chain-loss semantics. No shared-chain rewrite. Lead still owes #694-on-#699 delta receipt and actual R1/W1 scheduling/power evidence; no schedule-bias magnitude inferred. |
| R13 | OPEN | Q4/Q6 affirmative, ≥39/pair plus locked test retained. Removed builder's unruled D8/≥6-sabotage authority. Protocol records 42 before losses, 35 after one whole-window loss. Magistrate/series-plan owner proposes margin and explicit fit/C/test roster, both-pair/all-condition stopping OC and cap; lead rules **before W1**. At cap insufficient calibration/unresolved; no extensions authorized here. |
| R14 | PARTIAL | Exact rank helper/diagnostics and protocol/residual/public text agree: m=39 rank 38 ≤5%, rank 39 ≤2.5%, strict `>`, conditional exchangeability/common frozen scorer. Generic .025 maximum only at 39–78. Public page was absent in this clone: imported its local `origin/main` snapshot and corrected the FPR/scorer/DC statements; not published. **Legacy LOTO/full-fit scorer is unchanged and not qualified as D registration scoring**. Lead/statistics own final scorer wiring, asymmetry/dependence disposition and independent gate. |
| R15 | PARTIAL | Carrier calibration uses other source carriers' untouched H=0, strict .025 rank, ≥40 total for ≥39 remaining. Strict H*, actual integer doses, duplicate rejection, incomplete-grid denominators, nonmonotone/undefined crossings and bootstrap undefined counts retained. Bootstrap preserves window multiplicity with thresholds frozen first; explicitly conditional, not calibration-uncertainty inference. Independent common-shift/tie/39-vs-40 oracles pass. Final D wiring/full uncertainty OC and admission remain lead-owned. |
| R16 | PARTIAL | Procedure and kit check actual whole-turn opportunity at the **chosen B_D**, using per-turn counts/completion/totals/source digests for all three gated D rows. Known <3 → (b); missing/inconsistent → unresolved/R1-RERUN. 6,144 with two capped 4,096 turns is tested. Lead must supply count-only exports and actual freeze/access chronology; no retrospective pre-R0-read declaration or sabotage-capability claim is made. |

Assumed/adopted lead rulings: R11-1 HC/HR as qualified, R11-2 R07/R10/R03/
R14 choices, R11-3 existing reader + **secondary** DC (GPU residual retained),
R11-4 two acquisition additions only. Builder M choices: explicit signed
offload freshness rather than a duration default; qualified remeasurement
instead of a duty-label waiver; bootstrap conditioned on frozen thresholds,
with its narrower scope printed. No U constant, U5 waiver, budget-X7 waiver,
capacity increase, native gate or v5 estimator was invented. Full sealed
reasoning/transcript capture remains the separate fan-out's integration gate;
no transcript was scored.

## Files and verification

Changed after the merge:

- Code: `joulewise/align/apple/{v4_registration,v4_estimands,thermal_desk,thermal_gates}.py`;
  `scripts/{align_v4_kit,align_v4_session,align_v4_thermal_desk,align_v4_u3_bar,align_v4_offloads,align_w1_budget_procedure,validate_align_v4_w1_plan}.py`.
- Synthetic harness: `scripts/align_v4_w1_synthetic.py` gains explicit synthetic
  R0/count/contrast evidence; acquisition settings and roster unchanged.
- Tests: new `tests/align/test_v4_r11.py`; updated registration, estimand, kit,
  R10, protocol, thermal-desk and W1 synthetic tests for the new contracts.
  Two unrelated CLI-table tests mock the deliberately pending U3 validator;
  their output is rendering evidence only. The real refusal has direct tests.
- Docs: protocol v4, LEAD-RULINGS-2 Round 11, residual distinction, deviations,
  `docs/research/energy-tripwire.html`, this report.
- Kit: generated README/tree/identity digests, W1 template, pending receipt.
  Anchors, model/sampler/thermal settings, seed witnesses and roster unchanged.

Failing-first: the first 16 R11 regressions produced 12 failures and 6 errors
(including subtests) before implementation. Added red cases then exposed grid
interpolation, incomplete-grid denominator shrinkage, missing model/stack
binding, unruled offload/B defaults, v3 U3 fallback, missing template/desk
propagation and a passing duty label over observed X7. Existing fixtures were
updated to supply **synthetic** count/digest evidence. Initial old tests
failed on superseded semantics; no remaining failure is concealed.

Every command below ran **one module/selection per process, sequentially**, with
`python3.13 -B -m unittest <selection>`. Final results:

| Selection | Result |
|---|---|
| `tests.align.test_v4_r11` | 27 pass |
| `tests.align.test_v4_registration` | 19 pass |
| `tests.align.test_v4_estimands` | 14 pass |
| `tests.align.test_v4_kit` | 116 pass |
| `tests.align.test_w1_kit_r10` | 30 pass |
| `tests.align.test_v4_w1_plan` | 12 pass |
| `tests.align.test_protocol_v4_doc` | 6 pass |
| `tests.align.test_km003c` | 16 pass |
| `tests.align.test_thermal_desk` | 24 pass |
| `tests.align.test_thermal_gate` | 44 pass; synthetic clocks/endpoints |
| `tests.align.test_v4_w1_synthetic` | 4 pass, 14 full-WP22 opt-in skips |
| `tests.align.test_window_reference_custody` | 5 pass |
| `tests.align.test_pilot3_cache` | 13 pass |
| `tests.align.test_r1_round8_exec_review.SwallowedSignalLatchTests` | 2 pass |
| `tests.test_run_night.Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc` | 1 pass |

333 passed, 14 skipped in these selections. Test time including red runs and
rechecks stayed far below 20 minutes. No full suite or MLX execution.
`python3.13 -m compileall -q joulewise tests` plus touched scripts passed;
`git diff --check` passed. Kit/template generation passed. Kit `--check`
correctly returns 1 on pending R0/R1 leaves, not generated drift; its success
must not be asserted. Registration receipt stays unsigned/PENDING.

**Next exact step:** lead reviews the implementation and dispositions the OPEN/
PARTIAL rows; obtain the series-plan margin ruling before W1, U3 derivation,
B-window consequence and qualified mount audit, then supply authorized R0/R1/
count/WP19 evidence, regenerate and obtain exact-candidate Stage A/B gates.
After integration, the lead must run native tiny synthetic
`tests.align.test_cache_checkpoint_native` and `tests.align.test_thermal_mlx`
with MLX/Metal, and native WP19 tokenizer/history/RNG plus battery/meter-clock/
coverage/custody/mount qualifications. Full WP22 (`JW_WP22_FULL=1`) remains a
separate integration check. Hardware checks require the clean machine-state
gate outside this active sandbox/job. None of these are completed by green
synthetic tests, the logger launch, or the SECONDARY DC fit.
