# Structural-bound design consult (rule 2; escalation trigger) — Opus 5, read-only, 2026-09-17 03:36–03:46 PDT

Brief: record 35. Verbatim report as received by the magistrate:

# Structural-bound consult — NIGHT-RESERVE-HANG-01, read-only Opus, worktree `/Users/edr/code/JouleWise-wt-rh-consult` @ `3c685b6e`

Read-only: no edits, no tests run (so I predict no test outcomes), no launchctl, canonical root untouched. All file:line below are at `3c685b6e` in that worktree.

## 1. Structural bound — recommendation, with one disagreement with the premise

**Recommend the process-wide marker, but as an inherited BUDGET, not an absolute night deadline.** The lead's provisional preference breaks the one path it is meant to fix. `abort_window_exhausted` (`scripts/night_chains/calibration_derivation_only.zsh:119`) runs *because* the window is nearly gone: the trigger is `slot_start + SLOT_CAPTURE_BUDGET_S > WINDOW_END_EPOCH_S` (`:213`, `:225`), which fires with as little as 0 s of window left. `CustodyDeadline.__init__` raises `WINDOW_EXHAUSTED` when the clipped remainder is ≤ 0 (`joulewise/calibration_ledger.py:1924-1926`). An ambient *absolute* deadline would therefore make the end-of-night abort refuse instead of closing the session — a regression against today's behaviour. The abort must outlive the window; it needs a fresh per-operation allowance, not the window clip.

Concrete change list (≈40 lines in one module, plus one export):

1. `joulewise/calibration_ledger.py`, new module-level `night_custody_budget_s()` reading `JOULEWISE_NIGHT_CUSTODY_BUDGET_S` (float, absent ⇒ `None`). Precedent for env-driven custody behaviour already exists at `:5156` (`JOULEWISE_BACKUP_ROOTS`).
2. Three entry functions take the bounded route when no deadline was threaded and the marker is present — `custody_deadline = custody_deadline or ambient()`:
   - `artifact_hashes` `:286-304` (worker op `hashes`)
   - `_custody_state` `:5257-5275` (worker op `state`)
   - the snapshot's custody branch `:2441-2446` (worker op `verify`, via `bounded_custody_reasons` `:2120`)
   All three already have a worker route, so this is a branch selector, not new machinery.
3. Backstop in `probe_custody` `:5184`: when the marker is set, raise `LEDGER_CUSTODY_INVALID` with context `{"reason": "custody_read_unbounded_under_night_budget", "caller": inspect.__qualname__, "locator": …}` unless the call passes a new `metadata_only=True` (only `_assert_absolute_nonsymlink_directory` `:2706`). **`probe_custody` is the sole gateway**: every unbounded governed read in the module reaches it — `:2150`, `:2706`, `:2722`, `:2744`, `:5272` — and the only direct `read_authentication_input*` calls on custody bytes outside it are `_custody_store_reasons` `:2293`/`:2312`, which no night caller reaches (§2 row 17). So "a future caller cannot miss it" is a property of one guard, not of reviewer diligence.
4. Ambient branch refuses rather than re-maps when `mode == "read_replay"` and `JOULEWISE_BACKUP_ROOTS` is non-empty: the bounded branch hardcodes `mode="issuing"` (`:5262`) and sends the unmapped locator, so auto-bounding a replay call would silently change *which bytes* are read. Two lines. Note this cannot bite the abort path: `abort_calibration_session` calls `_refuse_custody_override_mint()` first (`:5874`, raising if `JOULEWISE_BACKUP_ROOTS` is set), so under abort, issuing and replay resolve identically (`:5155-5168`) and the auto-bound is semantics-preserving.
5. Export the marker in the chain (`calibration_derivation_only.zsh`, one `export` beside the existing `CUSTODY_BUDGET_S` uses at `:178`/`:241`) so it reaches reservation, writer **and** `recover_calibration_ledger.py abort-session` by inheritance; and pop it in `scripts/run_night.py:_chain_environment` `:465-467` next to the existing `NIGHT_VERIFY_ONLY` pop, so an inherited desk value cannot leak in. Cost: the chain is digest-pinned (runsheet + arm-time guard, digest `a7578b5c…`), so this forces one re-pin — name it in the PR.
6. **Do not** thread a deadline through `abort_calibration_session` → `calibration_session_status` → `recover_calibration_ledger.py`. Call-site threading is the mechanism that has now failed twice; adding a fourth parameter and a new desk-tool CLI flag buys nothing the marker does not, and leaves the next call site uncovered.

A caller that forgets the marker gets nothing new (it is inherited, not passed). A caller that invents a *new read shape* with no worker route gets an immediate typed refusal naming its own qualname — fail-closed, in-budget, diagnosable.

**Versus the lint/witness:** unsound here. The chain crosses two process boundaries (zsh → `recover_calibration_ledger.py`), the module imports the worker lazily inside functions (`:5176`, `:5279`, `:2713`), and the reads dispatch through lambdas (`:2151`, `:2723`). A static reachability lint over that is expensive to write, easy to satisfy vacuously, and gives no runtime protection. Keep a cheap *unit* test instead: assert every `probe_custody` call site in the module either passes `metadata_only=True` or is covered by a bounded route (AST walk, ~20 lines) — an addition to the guard, not a substitute.

## 2. Enumeration — every governed-artifact read reachable from the chain at `3c685b6e`

| # | Entry (chain-reachable) | Read | Bounding object |
|---|---|---|---|
| 1 | Reservation pre-reserve readiness `reserve_calibration_window_bracket.py:281` → `calibration_readiness` → snapshot `calibration_ledger.py:5418-5428` → `bounded_custody_reasons:2443` | whole corpus | `CustodyDeadline` built `:221` (budget 120, epoch `WINDOW_END−10`) |
| 2 | Reservation retry `calibration_session_status` `:298-306` | corpus-free; per-slot state | same deadline; unreachable anyway — `--pre-reserve-strict` raises first (`:290-296`, chain `:177`) |
| 3 | Verify-only probe (same as 1, returns `:359`) | whole corpus | same deadline **plus** supervisor `communicate(timeout=…)` `run_night.py:2152` |
| 4 | Writer preflight snapshot `validate_powermetrics_fiducial.py:2008` | whole corpus (pass 1) | `CustodyDeadline` built `:1862` |
| 5 | Writer pre-lease slot check `:1509` | none (reuses 4) | n/a |
| 6 | Writer under-lease snapshot `:1517` | whole corpus (pass 2) | same object `:1426` |
| 7 | Writer under-lease slot check `:1524` | none (reuses 6) | n/a |
| 8 | Writer enforcing readiness `:1561` → `:5418` | whole corpus (pass 3) | same object |
| 9 | Writer slot validation `:1573` → `:1348` | whole corpus (pass 4) | same object |
| 10 | Pre-slot custody state inside readiness `:5474-5477` | 1 locator | same object (worker op `state`) |
| 11 | Writer abandon `:1634-1641` | slot's 2 artifacts | fresh `next_operation()` `:1634` |
| 12 | Writer finalize `:1673-1682` | slot's 2 artifacts | fresh `next_operation()` `:1673` |
| 13 | **Chain `abort_window_exhausted` zsh:119** → `recover_calibration_ledger.py:511` → `abort_calibration_session:5882` → `calibration_session_status` → `_custody_state(…, custody_deadline=None)` `:5336` → `probe_custody:5272` → `_custody_state_unbounded:5278` → `_governed_raw_nofollow_unbounded:2750` → `_read_contained_nofollow_unbounded:2728` | 2 JSON files per declared slot with a reserved locator | **NONE** — 2 s metadata probe, then unbounded `open()+read()` (`probe_custody` docstring `:5203`: "narrows the hang window; it does not bound reads") |
| 14 | `repair_calibration_ledger` `:5877` (abort) | ledger/journal files in the clone, no governed artifact | n/a |
| 15 | Driver `run_night.py` | `_artifact_list:611-631` hashes night.log/result/receipt under the *night* custody root — night documents, not governed artifacts | NONE (adjacent class, out of lane; flag, do not fix here) |
| 16 | Courier | night documents only (`NIGHT_COURIER_PROMPT.md:10-13`) | n/a |
| 17 | Custody-store route `:2293`/`:2312` | store bytes | not chain-reachable: only `mint_floor_artifact_generalized.py`, `build_bracket_binding.py:499` pass `calibration_custody_store` |
| 18 | `resume_finalize_bracket_session` `:5742`/`:5750`, `_reauthenticate_historical_import_plan:3794` | governed bytes | not chain-reachable — the chain calls only `abort-session` (zsh:123) |
| 19 | `night_gate.py` | grep for `calibration_ledger`/`probe_custody`/`custody_state` returns nothing | n/a |

Row 13 is the only NONE in the lane's scope. The marker closes it without touching its signature.

## 3. Writer budget model, with numbers

Let **T** = one whole-corpus verified pass — exactly what the arm-time probe reports as `custody_elapsed_s` (`reserve_calibration_window_bracket.py:340`, `:346`; reservation makes one pass, row 1).

- **Today:** writer passes P = 4 (rows 4, 6, 8, 9) on **one** budget object (`:1426`, reset only at `:1634`/`:1673`); reservation P = 1. Both get the same `${CUSTODY_BUDGET_S:-120}` (zsh `:178`, `:241`). Feasibility therefore requires 4T ≤ 120 ⇒ **T ≤ 30 s**, while the probe certifies only T ≤ 120. Record 36's worked case stands: T = 90 s is a passing arm receipt and a guaranteed `calibration_ledger_custody_timeout` on d01.
- **(a) Reuse — sound, but only under the lease.** Memoize on the `CustodyDeadline` a `(ledger physical head digest, frozenset of (attempt_id, locator, artifact_sha256))` verified-set; reuse when the head digest is unchanged and the required set is a subset. Sound because custody verification is a pure function of (locator, expected hash) pairs that are re-derived from the ledger on every pass — only the disk bytes are cached. **Not** sound across the lease boundary: `:1516-1517`'s own comment places the under-lease authentication after acquisition precisely so recovery cannot mutate first, so pass 1 must not feed pass 2. `repair_calibration_ledger` runs at `:1526` between passes 2 and 3, so key the memo on the head digest: repair-as-no-op ⇒ passes 2/3/4 collapse (**P = 2**); repair-mutated ⇒ memo invalidates, one honest re-read (**P = 3**). Result: T ≤ 60 s (P=2).
- **(b) `next_operation()` per preparation operation — reject.** It grants a full fresh budget each time (`:1937-1950`), so N operations cost N×120 s of wall clock bounded only by the window clip. Keep ONE budget for all pre-capture preparation; leave `next_operation()` where it is (abandon/finalize, 2 small files each).
- **(c) Separate writer budget — not needed if the multiplier is enforced.** The load-bearing change is mechanical, not documentary: add `WRITER_CUSTODY_PASSES = 2` beside `PROBE_CODE_PATHS` (`night_agent_install.py:632-637`) and, in `validate_probe_receipt` (`:718`, which today checks `custody_elapsed_s` only for shape at `:742-749`), **refuse the install unless `custody_elapsed_s × WRITER_CUSTODY_PASSES × 1.5 ≤ custody_budget_s`**. With P=2, B=120 ⇒ probe must show **T ≤ 40 s**; if F2 is not fixed, set the constant to 4 ⇒ **T ≤ 20 s**. Also refuse `observations == 0` while the ledger holds finalized observations — a zero-observation probe certifies nothing and passes today (`:750-751`).
- **Runbook:** state it in `docs/phase_2/derivation_night_runbook.md` §1.2 (the 7680/7980/9000 arithmetic, `:1160-1225`) and in the arm checklist: *"the probe measures ONE corpus pass; the writer makes `WRITER_CUSTODY_PASSES`; arm only if T ≤ B/(P×1.5)"*, naming the constant so prose and gate cannot drift.
- **Launchd dry run must show:** `outcome: "ok"`, `refusal_code: null`, `launchd_label` = probe label, `custody_budget_s` = plan value, `observations` = the real finalized count (> 0), `custody_elapsed_s` = T satisfying the headroom gate, and `code_digests` covering `validate_powermetrics_fiducial.py` and `run_night.py` (F3, in flight as seat B round 3).
- **Cadence:** the premise "N×120 s before each capture" is wrong — the shared budget means preparation is ≤ **120 s total**, not 4×120, because the timeout fires at B. Worst case per slot = 120 s prep + capture + ≤120 s finalize. The capture's pulse plan alone is (3 warmup + 59) × (1.0 s + 1.5 s gap) ≈ 155 s (`joulewise/powermetrics_fiducial.py:59-63`), so worst case ≈ 400–450 s against `SLOT_CAPTURE_BUDGET_S=480` (predictive only — it gates *starting* a slot, `zsh:213`/`:225`, and never kills the writer) and a 600 s start-to-start cadence. It fits, thinly. Drift costs tail slots to `window_exhausted`, and the equivalence night needs ≥ 6 retained values (runbook `:2800`) — another reason the headroom gate, not a bigger budget, is the right lever.

## 4. Abort-path exposure

Realistically blocking? **Unlikely for the consent reason, real for two others.** The reads are 2 small JSONs per slot under `RUNS_ROOT = <custody_root>/runs` (runbook `:2177`), written minutes earlier by the same launchd process identity, so a fresh macOS consent prompt is implausible — the write already needed it. But (i) `custody_root` is operator-configurable, and Ed's standing iCloud-offload directive makes a synced/evictable custody root a live possibility, which reproduces the cured failure mode exactly; (ii) any hung mount or unresponsive volume blocks an `open()` regardless of consent. The cost if it happens is worse than it looks: the abort holds `CalibrationWriterLease` (`:5876`), so a hang leaves the session OPEN with a live lease, the driver has no wall-clock bound (`run_night.py:564-604`; A221 unlanded), and desk recovery is blocked by `LIVE_WRITER_CONTENTION` until the process is killed — the 2026-09-16 shape, at 06:30 instead of 09:45.

**Bound it anyway.** The lane's acceptance says "every night-path custody verification"; the bound costs nothing extra under the marker (row 13 auto-bounds); and an acceptance claim with one known-unbounded reachable read is the kind of wording that gets re-litigated later. Regression shape: FIFO-blocked `manifest.json` in a finalized slot dir during `abort-session` ⇒ typed refusal within budget + bounded cleanup, ledger and head-pin bytes unchanged, session still open, lease reacquirable from another process.

## 5. Merge shape

**Split — but not on the lead's line. Land the structural bound in THIS PR; gate the pass-count fix.**

In this PR: (1) the marker + `probe_custody` backstop + the three ambient selectors (§1), which closes the defect *class* and subsumes F1 without a fourth threading round; (2) the two admission gates in `validate_probe_receipt` (headroom, `observations > 0`), ~10 lines; (3) F3/F4/F6/F7, already in flight.

Gated follow-up before the next arm: the under-lease memoization (F2's real cure), because it changes what "enforcing under lease" verifies and deserves its own review round — and the escalation trigger says the next spend after two same-signature rounds is not a third round of the same shape.

Risk of merging the structural bound now: the guard is new global behaviour, and a mis-scoped `metadata_only` or a desk caller with the marker inherited gets a refusal instead of a read. That is fail-closed, cheap to regress, and the `_chain_environment` pop bounds the blast radius to processes the chain actually starts.

Risk of deferring the memoization: none that can arm a bad night **provided the headroom gate lands with it** — with `WRITER_CUSTODY_PASSES = 4` in the constant, a corpus needing more than 20 s per pass refuses the *install*, loudly, at the desk, instead of timing out on d01 at 03:00. That mechanical coupling is the whole reason I would accept the split; without the gate in this PR, "gated before the next arm" is exactly the ruled-not-installed pattern this repo has already been bitten by, and then F2 must land here.

Risk of landing everything now: a third fix round on a head that has already taken two, more delta re-audit, and the same signature the escalation trigger exists to stop.
