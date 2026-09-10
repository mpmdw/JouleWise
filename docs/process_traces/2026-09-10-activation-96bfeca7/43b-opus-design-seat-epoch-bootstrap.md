I have the full mechanism picture. Here is the memo.

---

# Design memo — governed bootstrap for calibration identity epoch 25G83 (Opus seat, blind)

**Scope.** Read-only. Nothing edited. Every mechanism claim below was read this session in `/Users/edr/code/JouleWise-wt-bk-96bfeca7` at `bookkeeping/2026-09-10-activation-96bfeca7`. Line numbers are that tree's.

## Summary of the binding constraint set (what the code actually enforces)

1. The live writer refuses before hardware work when the measured epoch differs from the issued acceptance: `scripts/validate_powermetrics_fiducial.py:1710-1719` calls `_derive_preflight_systematic_screen_s(planned_epoch)` (`:364`), which raises `acceptance_artifact_epoch_mismatch` at `:397-407`.
2. That same function **already supports `identity_epoch=None`** (`:365`, guard at `:397`), in which case it still authenticates the artifact bytes, role, protocol sha256 and all four estimator-code hashes (`:371-392`) but skips the epoch equality test. `:441` already calls it that way to publish the module-level comparator.
3. The screen is used exactly once more, to classify the finalized observation `valid` vs `systematic-invalid`: `:2213-2219`.
4. Trigger arithmetic in the acceptance evaluator is **epoch-filtered**: `joulewise/calibration_bracketing.py:1803-1826` counts only observations whose `identity_epoch` equals the artifact's. Endpoint matching is filtered by the full T1 vector including `os_build` and `powermetrics_sha256` (`:1656-1664`, fields at `joulewise/powermetrics_fiducial.py:106-119`).
5. Therefore **appending honest 25G83 rows to the canonical ledger cannot perturb the incumbent r6 (25F84) artifact.** This is the load-bearing fact that makes the small design possible.
6. The issued-artifact validator, by contrast, is hard-wired to the genesis import: exactly one catalog entry named `d079_epoch` (`:523-524`, `:566`), a prior set of exactly 38 observations at cutoff sequence 76 (`:591-592`), every corpus member's content id inside the prior set (`:576-580`, `:605-607`), and a cutoff prefix in which **every** row is import-marked (`:1349`, refusal at `:1378-1379`).
7. `scripts/calibration_ledger_bootstrap.py:289-291` is genesis-only historical import (`docs/contracts/calibration_ledger.md:17`) and is **not** on this path; the successor is built by a bespoke derivation script, as r5/r6 were.

## D1 — Derivation-only capture route

**Recommendation: a `--derivation-only` mode of the existing writer. No new night class, no new chain, no ledger schema change.**

The mode is five behaviours, all in `scripts/validate_powermetrics_fiducial.py::main`:

- **Authenticate, do not epoch-match.** Call `_derive_preflight_systematic_screen_s()` with no `identity_epoch` (`:1710-1719` → pass `None`). The prior artifact's bytes, role, protocol and estimator hashes are still fully checked (`:371-392`); only the epoch equality at `:397-407` is skipped.
- **Refuse when it would be a bypass.** Compute `stale_fields` locally and refuse with a new `RefusalCode.DERIVATION_ONLY_EPOCH_UNCHANGED` if it is empty. Derivation-only is usable *only* when the epoch genuinely differs; it can never substitute for a same-epoch check.
- **Refuse in bracket mode.** `bracket_mode` is computed at `:1609`; derivation-only must refuse if any of `--session-id/--slot/--attempt-id` is present. That structurally excludes the mode from every G2/pack chain, which always reserves brackets (`scripts/reserve_calibration_window_bracket.py`).
- **Classify under the prior artifact.** Keep `:2213-2219` unchanged, using the prior r6 comparator `0.032898493715362`. This is not a new rule: D-102 cl.2 already says a trigger observation "is judged under the PRIOR artifact — never incorporated into a threshold that judges itself" (`docs/decision_log.md:6474-6484`). Record `screen_basis: {acceptance_id, artifact_sha256, epoch: <prior>}` and `derivation_only: true` in `instrument_evidence.json` and `manifest.json` so the provenance is in the hashed bytes.
- **Record the measured reality.** `planned_epoch` (`:1700-1707`) and `planned_t1` (`:1738-1742`) already carry the live `kern.osversion`, `hw.model` and the sampler binary hash; nothing to add. The ledger row carries the honest 25G83 epoch via `_CaptureLedgerLifecycle` (`:1748-1757`).

**What it does not license.** It writes one ordinary reservation/finalization pair; it issues nothing, pins nothing, and produces no acceptance. Every downstream consumer still refuses under the incumbent artifact because the epoch check at `joulewise/calibration_bracketing.py:1516-1540` and the writer preflight are untouched. No G2-a, no floors, no claims — not by labelling, but because no 25G83 acceptance exists to make any of them pass.

**Night shape.** `DIAGNOSTIC_NO_PACK` (`joulewise/night_gate.py:27-31`, class table `:435-445`) with a derivation-only chain. C1 and C3-C5 still apply; nothing is exempted.

## D2 — Ledger representation

**Recommendation: ONE canonical ledger carrying both epochs, with the successor's `ledger_cutoff` ADVANCED past the bootstrap rows and a two-entry epoch catalog.** Reject a separately anchored second ledger: it needs a second head pin and custody chain, forces every consumer to choose a ledger, and reopens exactly the rollback/stale-head surface the chain exists to close (`docs/contracts/calibration_ledger.md:8-13`); it also breaks D-124 single-sourcing.

The cutoff must advance, and this is not a preference — it is forced:

> If the successor keeps cutoff 76 and the 38-row import prior set, every bootstrap row is a *new* post-cutoff observation (`joulewise/calibration_bracketing.py:1780-1799`). A single bootstrap capture above the prior screen is recorded `systematic-invalid` at the successor's own epoch, which fires `new_systematic_failure_challenges_preflight_screen` (`:1876-1882`) — the one trigger that hard-stales the artifact (`:1837-1850`). **The successor would refuse from the moment it was issued.** Advancing the cutoff so the bootstrap rows sit in the prior set removes them from `new_observations` and closes this.

Advancing also makes the member/prior linkage clauses (`:576-580`, `:605-607`) pass unchanged, since corpus members are then prior-set rows.

**Corpus purity.** Add a `derivation_corpus.epoch_id` field naming the catalog entry, and a new check that every member's prior-set row carries that epoch id. The current single-catalog design got purity for free; a two-epoch catalog must state it.

## D3 — Corpus design and stopping rule (pre-registration text)

**Arithmetic.** One observation is 3 warmups + 59 pulses of 1.0 s, gap `1.5 + vdC_2(j)`, 5 s baseline each side (`docs/contracts/powermetrics_fiducial.md:27-31`; constants `joulewise/powermetrics_fiducial.py:59-65`). Computed this session from `van_der_corput` (`:355-378`): 62 pulses, 62.0 s on, 123.03 s of gaps, 195.03 s = **3.25 min instrumented**. Planning cost 4-8 min per observation covers launch, sudo sampler start, artifact write, hashing and ledger fsync.

| Design | Window | Settle | Usable | n | Worst-case capture | Margin |
|---|---|---|---|---|---|---|
| One night | 03:00-06:30 = 210 min | 600 s = 10 min | 200 min | 17 | 136 min | 64 min (32%) |
| One night | 210 min | 10 min | 200 min | 20 | 160 min | 40 min (20%) |
| One night | 210 min | 10 min | 200 min | 24 | 192 min | 8 min (4%) — reject |
| Two nights | 2 x 210 min | 2 x 10 min | 400 min | 10 + 10 | 80 min/night | 120 min/night (60%) |

**Recommendation: two nights, 10 + 10.** Reason, and it is not conservatism-for-its-own-sake: r6's corpus spans four days (`docs/decision_log.md:6483`), so its range carries the day-to-day nuisance component. A one-night corpus omits it and will be narrower. Three of the four derived quantities move in the safe direction when the corpus narrows (tighter preflight screen, smaller two-draw ceiling, smaller budget cap — all more refusals). **One moves the wrong way:** the never-zero allowance `A_s = max(observed_drift_s, floor)` (D-102 cl.3, `docs/decision_log.md:6485-6493`) takes its floor from the corpus range — n=19 range `0.010817749309353528` gave `0.010818`; n=17 range `0.00972358928879385` gave `0.009724` (`joulewise/calibration_bracketing.py:194-216`; `tests/verify_calibration_acceptance_corpus.py:31-47`). A narrower corpus lowers the floor, shrinking the operative bound and making claims *easier*. That is anti-conservative and it is the same conflict Ed still owns as D-125 (`TASK_QUEUE.md:655`).

**Corpus membership must be all-or-nothing, and this is also forced by code.** If any *valid* same-epoch bootstrap row is excluded from the corpus while sitting outside the retained members' min/max, it fires `new_valid_same_identity_capture_expands_observed_range` (`joulewise/calibration_bracketing.py:1811-1826`). Outcome-based selection is therefore both scientifically wrong and mechanically self-defeating.

**Pre-registration text (commit before the first capture; this is the whole of it):**

> **Pre-registration: D-079 acceptance corpus for identity epoch 25G83 (rev 1, authored 2026-09-__, before any capture).**
> **Epoch.** `{os_build: 25G83, hardware_model: Mac15,9, power_policy: ac_high_power, sampling_interval_ms: 100, estimator_revision: joint_loss_sublevel_interval_branch_v2, pulse_protocol_id: powermetrics_pulse_fiducial_v3}`. The `/usr/bin/powermetrics` sha256 in force is `b762e5bf7628e77d279012882c096e922633a47aa38bd5f05c0381cfb21330c5`; a change to it voids this registration.
> **Target n.** 20 observations, 10 per night, across two agent-free `[QUIET-MAC]` windows on distinct calendar days.
> **Schedule.** Each window: 600 s settle after the last operator action, then observations back to back with no operator interaction. Protocol `powermetrics_pulse_fiducial_v3` unmodified; no parameter is tuned between observations.
> **Classification.** Each observation is classified by the writer under the PRIOR issued artifact `d079_calibration_acceptance_v2_n17_r6` (`preflight_level_screen_s = 0.032898493715362`), per D-102 cl.2's judge-under-prior-artifact rule. The comparator is recorded in the evidence bytes.
> **Membership.** The derivation corpus is **every** observation of this registration whose disposition is `valid`. No observation is excluded on the basis of its `b_fiducial_s`.
> **Exclusions (mechanism-named, outcome-independent, decided before capture).** An observation is excluded only if (a) the estimator's own clock-anchor feasibility model refuses it (the r6 exclusion class, `docs/process_traces/2026-08-18-anchor-v3-science-review/03-cold-science-review.md:55-75`); (b) a protocol gate fails (plateau, SNR, 59-pulse detection, spurious plateau, edge coverage — `docs/contracts/powermetrics_fiducial.md:33-36`); or (c) the window was interrupted by a recorded operator or system event. Every exclusion is recorded with its named mechanism and its ledger row is retained.
> **Stopping rule.** Capture until n = 20 valid members or the window's usable time is exhausted, whichever comes first. If the two windows together yield fewer than 12 valid members, the corpus is not issued and a third window is scheduled; the shortfall reason is recorded before the third window is planned.
> **Screen-challenge rule (the D-102 cl.2 "new systematic failure" reading for a fresh epoch).** Because no 25G83 screen exists, the prior screen is the comparator. If **two or more** observations of this registration are classified `systematic-invalid`, the night constitutes evidence that the new epoch's level distribution differs materially from the prior epoch's; the corpus is NOT issued, the finding is written up, and Ed rules before any further capture. One `systematic-invalid` observation is recorded, excluded from the corpus, and does not block issuance.
> **No self-fitting.** No G2-a, floor, or claim output of any kind is an input to this derivation.

**Ed's to decide** (all scientific): target n and one-vs-two nights; the two-or-more screen-challenge threshold; the allowance-floor rule (D-125); whether the 12-member minimum is right. **The magistrate's**: mechanism and code shape, registry rows, transaction assembly, custody, calendar sequencing.

## D4 — Successor issuance

Derivation is a bespoke `scripts/build_r7.py`-shaped script over the raw corpus bytes, the r5/r6 precedent, not `scripts/reissue_calibration_acceptance.py` — that tool re-derives the predecessor's members only and STOPs on any changed member or science-facing field (`scripts/reissue_calibration_acceptance.py:127`, `:249`). It computes, in `Decimal` at prec 80 exactly as the validator does (`joulewise/calibration_bracketing.py:618-640`): min, max, range, mean and sample sd presentation values; the 95%/99% two-draw predictions; the four ratified operatives; the preflight screen and bracket screen; the budget cap.

**Minimal change list (file:function).**

| Change | Where | What |
|---|---|---|
| 1 | `scripts/validate_powermetrics_fiducial.py::main` (argparse near `:1582`; preflight `:1710-1719`) | `--derivation-only` flag; pass `identity_epoch=None`; refuse on empty `stale_fields`; refuse in bracket mode; record `derivation_only` + `screen_basis` in the evidence and manifest payloads (`:2180-2200`) |
| 2 | `joulewise/refusals.py` (RefusalCode enum) | `DERIVATION_ONLY_EPOCH_UNCHANGED`, `DERIVATION_ONLY_BRACKET_CONFLICT` |
| 3 | `joulewise/calibration_bracketing.py::_valid_acceptance_bound` `:523-524`, `:566` | epoch catalog: accept a generation-registered multi-entry catalog; each prior row's `epoch_id` must be a catalog key; artifact `identity_epoch` must equal exactly one entry |
| 4 | same function, `:591-592` | replace the literals `38` and `2 * len(...)` with generation-registered `prior_observation_count` and `cutoff_sequence` (do not keep the 2N identity — one abandoned attempt breaks it) |
| 5 | same function, after `:607` | NEW check: every corpus member's prior row carries `derivation_corpus.epoch_id` (corpus purity, previously free) |
| 6 | `joulewise/calibration_bracketing.py::_prior_set_matches_import_cutoff_prefix` `:1378-1379` | drop the "every prefix row is import-marked" clause; retain the exact set equality on (attempt_id, content_id, disposition, epoch_id) at `:1391-1394`, which is the load-bearing check. Rename to `_prior_set_matches_cutoff_prefix` |
| 7 | `joulewise/calibration_bracketing.py` `:132-160`, `:194-230` | new `ISSUED_ACCEPTANCE_REGISTRY` row and `_D102_GENERATION_DERIVATIONS` row for `d079_calibration_acceptance_v2_n<N>_r7` (corpus_n, doubling trigger vocabulary, two predictions, four operatives, prior count, cutoff sequence) |
| 8 | `tests/verify_calibration_acceptance_corpus.py:25-63` | new generation row with `stored_lexeme_is_member_value: True` (a fresh v3 capture stores its own value; unlike r3-r6 it is not a re-derivation of superseded scalars — `:19-24`) |
| 9 | `docs/contracts/calibration_ledger.md:17`, `:48-57`, `:226-233` | state that the cutoff prefix may contain live rows under a registered generation, and update the issued-state paragraph |
| 10 | `docs/contracts/powermetrics_fiducial.md` (after `:83`) | one paragraph naming the derivation-only mode, its prior-artifact classification basis, and that it licenses nothing |
| 11 | `docs/decision_log.md` | D-102 dated addendum recording the epoch-rollover mechanism, plus Ed's D-125 ruling |

**The D-138 atomic transaction must carry**, in one branch (`docs/decision_log.md:182`; atomic-fan-out condition at `03-cold-science-review.md:111-115`): successor acceptance bytes + registry rows (items 7, 8) + `DEFAULT_ACCEPTANCE_BOUND_PATH` flip + every pack/extraction/acceptance-owner pin + T1 projections + regenerated chain digests + the staged `15-r2-coverage-ulp-staged-for-d138.patch` and its four regressions + the fan-out surfaces enumerated by consult 38 Q5 (`analysis_engine/inputs.py`, `mint_floor_artifact*.py`, `floor_mint_estimator.py`, `arm_readiness.py`, `scripts/floor_mint_pinsets/schema_v2.json`). Historical generations stay byte-identical.

**Desk time, honestly.** Items 1-2: ~1 h plus regressions. Items 3-6: ~3 h — this is the acceptance validator, the highest-consequence file in the repo, and every clause needs a defect-shaped regression. Items 7-8 and the build script: ~2 h. Fan-out and the transaction: ~3 h. Cold science gate and two review rounds with delta re-audits: ~4 h. **Call it one full working day of agent desk time before the corpus night, and a second after it** — not an afternoon.

## Calendar

Both designs assume the 09-11 03:00-06:30 rehearsal-20260911 harvest clears and the stub is retired on 09-11, per record 39.

**One-night design.** 09-10 desk: this consult adjudicated, Ed's D3/D-125 rulings, changes 1-6 implemented and reviewed. 09-11: rehearsal harvest, stub retirement, pre-registration committed, derivation-only chain reviewed, plan authored (note the 36-hour authorship horizon, record 39), bind, arm. **09-12 03:00-06:30 corpus night (n=20).** 09-12 desk: harvest, derive, cold science gate. 09-12/13: D-138 transaction, review, CI, merge. 09-13 desk: bind-window/check, arm. **Earliest G2-a: 09-14 03:00.**

**Two-night design.** Identical through 09-11. **Corpus nights 09-12 and 09-13 (10 + 10).** 09-13 desk: harvest and derive. 09-14: transaction, review, merge, arm. **Earliest G2-a: 09-15 03:00.**

Two nights costs exactly one calendar day of G2-a. Under the "quiet windows any time" reading (quiet = census-clean machine state, not darkness), two daytime windows on 09-12 would recover that day — Ed's machine time, so it is a question, not a plan.

## Risks

- **R1 (closed by the D2 recommendation, fatal if ignored).** Cutoff-at-76 plus any `systematic-invalid` bootstrap capture self-stales the successor at issuance (`joulewise/calibration_bracketing.py:1876-1882`, `:1837-1850`).
- **R2 (permanent, accept knowingly).** Bootstrap rows are ordinary live `valid` rows, so they enter the anti-withholding equality check (`:1620-1625`) and must load through `_candidate_from_observation` (`:1245-1258`) forever. An unreadable bootstrap custody directory refuses **every future window**, not just its own. The existing 38 rows are exempt because they are import-marked (`:2091-2096`). Mitigation: pinned custody manifest and backup before the transaction, and a regression that asserts the refusal is `calibration_ledger_off_ledger_artifact` and not silent.
- **R3.** `--derivation-only` as a bypass. Mitigations are the empty-`stale_fields` refusal and the bracket-mode refusal; both need mutation-killed regressions naming the production call site, not a fixture.
- **R4.** One-night corpus lowers the allowance floor (anti-conservative). Blocked behind Ed's D-125 ruling.
- **R5.** The 2026-08-18 cold science gate's conditions attach again: detector-budget re-sweep before the freeze (`03-cold-science-review.md:104-107`) — the sweep was done under the old binary and must be re-run or explicitly carried — and the float64 representation-error pricing (`:108-110`).
- **R6.** Fix rounds on the acceptance validator historically introduce defects; delta re-audit every round.
- **R7.** A rehearsal failure on 09-11 slides everything by a day in both designs.

## D5 — Recurrence (proposed shape, not ruled here)

- **A standing `EPOCH-ROLLOVER-<build>` lane template**, so the next macOS update costs one night and no design round: (i) desk epoch-diff record; (ii) pre-registration from the D3 template with only n, dates and the binary hash filled; (iii) one derivation-only night; (iv) build script + two registry rows (items 7-8, which after this session are pure data); (v) D-138 fan-out; (vi) cold science gate; (vii) bind/arm. Everything except (ii) and (iii) becomes mechanical once items 3-6 land.
- **Move the detection to the desk, daily.** The update landed 2026-09-02 20:35 and was discovered 2026-09-10 at bind-window: **eight days.** The bind-window check is correct but far too late. Add a two-subprocess epoch watch to the magistrate's step-0 digest check and to `gen_state --check`: compare `sysctl -n kern.osversion`, `sysctl -n hw.model` and `sha256(/usr/bin/powermetrics)` against the active acceptance's `identity_epoch` and the last ledger row's `t1_bindings`. Cost: milliseconds. Value here would have been eight days.
- **One gap worth naming.** The identity epoch has six fields and **does not include the powermetrics binary hash** (`joulewise/calibration_ledger.py:100-106`); the hash lives only in the T1 binding vector (`joulewise/powermetrics_fiducial.py:106-119`). A Rapid Security Response that swaps the binary without moving `kern.osversion` would pass the writer's epoch preflight and be caught only downstream at bundle/reduce time. Adding it to the epoch is a large-blast-radius contract change (every stored row's epoch shape); the cheap correct answer is that the desk watch covers the binary explicitly. Flagging, not proposing.

## Questions for Ed

1. **One night (n=20) or two nights (10 + 10)?** Recommendation: two nights. Cost: one calendar day of G2-a.
2. **The D-125 allowance-floor conflict must be ruled before the successor can be derived** (`TASK_QUEUE.md:655`): does a new corpus's range set the never-zero allowance floor, or does the lineage floor `0.010818` bind as a lower bound? Proposed rule: `A_floor = max(new corpus range, 0.010818)`, which makes the corpus width unable to weaken the bound and removes most of the one-night risk.
3. **Screen-challenge threshold.** Proposed: two or more `systematic-invalid` observations under the prior r6 screen means the corpus is not issued and Ed rules. Is two right?
4. **Exclusions.** Confirm mechanism-named, outcome-independent exclusions only, and that the corpus is every valid observation of the registration.
5. **Daytime quiet windows** on 09-12 to run both halves of the two-night design in one day?
6. **Automatic macOS updates** on the measurement machine: disable, or keep with an announced-update discipline?
