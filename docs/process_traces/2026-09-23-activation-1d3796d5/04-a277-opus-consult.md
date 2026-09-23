# A277 design consult — Opus 5.5 seat (subagent, read-only, worktree wt-1d3796d5-consult at 313efcca)

# A277 design consult: Opus 5.5 seat answer

Worktree `/Users/edr/code/wt-1d3796d5-consult` at 313efcca. All reads were read-only.

## Answers first

- **Q1:** Option B, in a reshaped form. Pull the watchdog's disk-fact code, together with its presence preconditions, into one new joulewise module. It should return a typed facts record (counts, not a single bool). `arm_retry` stays pure and makes its decision from that record, not from a C5 block. Reject A.
- **Q2:** The only production chokepoint is `joulewise/evidence_night.check`. Add a new `successor` check row next to `retained_roots`. `publish_install` already refuses to publish without a fresh armable check, and it should also create a create-once successor claim outside the predecessor's custody.
- **Q3:** Nine regressions at `check` and `publish_install`, listed below.
- **Q4:** Nine existing paths plus one new module, listed below.
- **Q5:** The lane text is wrong on three points: there is no harvest code; the real successor path already exists and skips the one-successor rule; and the 60 s spacing is not enforced.

## Brief claims checked

- **Confirmed: nothing in production writes the block.** The block is read at `joulewise/arm_retry.py:270`. The only hits for `zero_capture_evidence` outside docs are `tests/test_arm_retry.py:459-501`.
- **Confirmed: `successor_arm_allowed` (:287) and `zero_capture_successor_allowed` (:247) have no production caller.** Production imports `arm_retry` in exactly two places:
  - `evidence_night.py:1036`, `classify_abort`, inside `retry_inventory`;
  - `magistrate_watchdog.py:49`, `terminal_zero_capture_refusal`.
- **The real successor path today** is an ordinary fresh plan run through `evidence_night` prepare → check → notice → veto → publish-install (`evidence_night.py:1587-1608`).
  - It only works as a successor because `check` → `retained_roots` (:1081, :723-760) calls the watchdog's `plan_span_active` (:749).
  - `plan_span_active` returns False once A234 has latched a release (`magistrate_watchdog.py:931-933`).
  - So PR #393 already opened a successor door without the dead eligibility code. That door does **not** enforce:
    - **One successor.** No production source of `successors_used` exists; the grep hits only tests, `arm_retry` and the contract. The successor's own zero-capture refusal gets released too, so a third plan passes `retained_roots`. That breaks D-182's "ONE" and the addendum's "A second abort, in the successor itself, licenses nothing further" (`decision_log.md:12100`).
    - **The 60 s spacing from `result.ended_epoch_s`.** The latch fires on the first tick with empty probes after `courier.sent` (:1600-1625), and nothing ties that to `ended_epoch_s`.
  - The derivation-night route (`gen_derivation_night.py` + `install_night_agent.sh`) has no check of earlier nights at all.
- **The brief's descriptions of `terminal_zero_capture_refusal` and `_zero_capture_disk_facts` are accurate:**
  - A bare C5 row is neither evidence nor veto (:205-208, :228-241), already pinned at `test_arm_retry.py:469-472`.
  - Symlinks count as present (`Storage.exists` :278-279; `_tree_has_match` :809-813).
  - The envelope index must be a regular empty file (:843-848).
- **One caveat the brief misses:** a *missing* custody root makes the reservation and capture checks come back vacuously clean (`FileNotFoundError → False`, :810-811). It fails closed today only because `_delivered_zero_capture_refusal` first requires `courier.sent`, `result.json` and `receipt.json` inside that custody root (:876-888).
- **One D-182 term has no disk fact:** "no ledger session" (`decision_log.md:11994`). `session_id` is only checked when a caller supplies it, and the disk facts look only for `*.consumed.json`.

## Q1: Option B, reshaped

**Why not A:**
1. `night/receipt.json` is written once with `O_EXCL` by the driver (`run_night.py:3062, 3163, 3168`, `_write_bytes_exclusive`). The admission contract says "The predecessor stays immutable" (`night_quiet_admission.md:327`). The pack contract pins "unchanged `night/receipt.json` for every class and refusal" and a read-only validator (`pack_night_go_receipt.md:642`). The courier has already delivered those bytes, so writing into C5 would falsify delivered custody.
2. There is no harvest code: no `def harvest`, and nothing writes `successors_used`. Harvest is a desk procedure, "inspection and preservation of the night's records" (`NIGHT_HANDBACK.md:57`). The block would be an agent vouching for its own facts.
3. A gives two sources of truth: the release would read live disk while the successor reads a snapshot. A write-once sidecar (call it A′) still has a new writer and a stale snapshot.

**Fail-closed comparison:**
- **Torn or partial harvest.**
  - A: a missing field refuses (tests :498-501). It fails closed, but it also refuses every real night.
  - B: harvest output is never consumed; facts are re-read at check time.
- **Symlinked custody or evidence directories.** B inherits the `lstat` rule: any symlink counts as present and blocks.
- **Missing custody root.**
  - The shared module must **not** export the bare disk-fact function. It must export the composed predicate, which first requires the custody root to be a real directory, `courier.sent` present, and `result.json`/`receipt.json` readable. A regression must pin this.
  - A worse hole affects both options: if cleanup moves the predecessor's custody root away before the successor check, `retained_roots`' glob (:729) never sees it, and the candidate arms as an ordinary night. So the successor count must not live in predecessor custody (see Q2).

**Shape for A270:**
- **One pure function:** `successor_license(result, receipt, facts, delivery, claims)`. It lives in `arm_retry` and stays stdlib-only, which is pinned at `test_arm_retry.py:440-446`. Its "door" is chosen by the exact refusal reason. The two doors are disjoint:
  - **Door 1 (zero-capture):**
    - reason in `ZERO_CAPTURE_MACHINE_REFUSALS`;
    - null chain fields;
    - `facts.chain_started` false;
    - zero reservation markers;
    - zero capture entries;
    - `envelopes_captured == 0`.
  - **Door 2 (A270 adds it):**
    - reason exactly `non_observer_process_busy`;
    - chain started *and* exited;
    - `1 <= facts.envelopes_captured < minimum_retained`, with `minimum_retained` read from the sealed registration, never from the result.
- **Shared tail:** both doors share the delivery, count/claim, 60 s and freshness rules.
- **Why the facts record carries counts:** A270 then reads `envelopes_captured` without redefining any fact. Door 1's conditions are never loosened: any capture or reservation fact refuses door 1, and door 2 is reachable only through its own reason code.
- **Left to A270:** whether the watchdog releases door 2's hold (the `chain.started` branch at :926-930).

## Q2: Production call site

- **`evidence_night.check`:** add a row `successor`, placed after `retained_roots` (:1081).
  - For each retained plan whose span would still be active without a latched release (now ≤ `plan_completion_epoch` and release observed), the candidate *is* that plan's successor.
  - The row loads the shared facts and calls `successor_license`. It refuses if more than one such predecessor exists, or if `now - result.ended_epoch_s < 60`.
- **`publish_install` already enforces the row:** it requires a fresh armable `check.json` (:1417, :1238-1244), and the notice must be newer than `check.json` (:1430). That already gives D-182's fresh-notice rule, since the check can only pass after the release.
- **One-successor claim:**
  - Just before publication, `publish_install` creates an `O_EXCL` claim at `~/night-custody/successor-claims/<predecessor plan_id>.json`, naming the successor's plan id and sha256.
  - The directory contains no `night_plan.json`, so both `retained_roots` (:729) and the watchdog's `glob_plans` (:292) ignore it.
  - Eligibility refuses if a claim for the predecessor already names a different plan, or if the predecessor itself is named as a successor in any claim.
  - Re-publishing the same claimed candidate (same id and sha) stays allowed.
- **What to do with the old functions:** retire `zero_capture_successor_allowed`'s C5-block requirement. Either delete `successor_arm_allowed` or turn it into a thin adapter; its plan/notice shapes are `retry_allowed`'s desk format, which `evidence_night` does not produce.
- **Derivation route:** declare it not a successor route in NIGHT_HANDBACK and file a follow-up lane. Don't try to install the check in shell.

## Q3: Regressions

Each one uses a real custody fixture tree, driver-shaped result and receipt bytes (bare C5 row, no block) and a magistrate `state.json` with the release latched.

1. A live-shaped delivered zero-capture refusal: `check` has a `successor` row that passes, and `publish_install` writes exactly one claim. **On 313efcca:** the row does not exist and no claim is written.
2. The same bytes but with `courier.sent` missing, or no latch, or a bare receipt fed through `successor_license` without facts: refused. A bare C5 row never licenses.
3. Each fact blocks, one test per fact:
   - `chain.started` present;
   - a `*.consumed.json` at depth 3;
   - a symlinked `night/evidence`;
   - a non-empty or symlinked `evidence_envelopes.jsonl`;
   - any `instrument_validation` entry for a calibration chain;
   - a symlinked custody root;
   - a missing custody root.
4. A fact appears *after* the one-way latch, for example a `*.consumed.json` written post-release: `check` refuses. This proves the check re-reads the disk and does not trust the latch.
5. A second successor is refused because a claim exists. The successor's own zero-capture refusal, once released, licenses no third plan.
6. `now - ended_epoch_s = 59.99` is refused.
7. The predecessor's custody root is removed after the claim: the count still holds.
8. Parity: the watchdog's `_delivered_zero_capture_refusal` and the `check` row compute identical facts on the same fixture, and the watchdog imports the shared module.
9. Door disjointness: `non_observer_process_busy` is refused by door 1 even with zero envelopes, which pins that A270 must add door 2.

Also rewrite `ZeroCaptureSuccessorTests` (`test_arm_retry.py:453-545`) deliberately, not by deletion alone.

## Q4: WRITE_SCOPE

`joulewise/zero_capture_facts.py` (new), `joulewise/arm_retry.py`, `scripts/magistrate_watchdog.py`, `joulewise/evidence_night.py`, `tests/test_arm_retry.py`, `tests/test_magistrate_watchdog.py`, `tests/test_evidence_night.py`, `docs/process/NIGHT_HANDBACK.md`, `docs/phase_2/derivation_night_runbook.md` (both carry the `render_policy` block byte-for-byte), `docs/contracts/night_quiet_admission.md`.

## Q5: What I believe is wrong

1. **"A field the harvest is meant to add under the refusal receipt's C5 row" (lane A277).** There is no harvest code, and the receipt is write-once custody. The contract itself says the predecessor stays immutable (`night_quiet_admission.md:327`). Option A as worded is ruled out.
2. **"A234 releases the hold but does not itself deliver the successor."** That is half true. Combined with `retained_roots` → `plan_span_active`, A234 *already lets a successor arm*, with no one-successor bound and no 60 s bound. So today's live defect is too permissive, not only too strict. It should be stated in the registration and weighed before the next arm.
3. **A270's text routes through `zero_capture_successor_allowed` / `successor_arm_allowed` "in `joulewise/arm_retry.py`" at "production call sites".** Those functions are dead code. A270's production site must be the new `check` row, and the A270 row should be amended when A277 lands.
4. **D-182's "no ledger session" has no disk fact.** `*.consumed.json` stands in for it. The magistrate should rule whether the reservation marker is enough, or whether the ledger file must also be inspected.
5. **The lane lists `_zero_capture_disk_facts` as the fact source.** Exported on its own it is not fail-closed when the custody root is missing (:810-811). Only the composed predicate is.