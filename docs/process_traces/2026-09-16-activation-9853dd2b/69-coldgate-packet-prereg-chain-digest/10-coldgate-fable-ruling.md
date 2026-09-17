# Cold-gate ruling 69 — PREREG-CHAIN-DIGEST-ADDENDUM-01 (Fable 5.1, cold judge, 2026-09-17)

## 0. Disclosure and trust anchors

Auto-loaded into my context before I read anything: `~/.claude/CLAUDE.md`, the project `CLAUDE.md`, and the memory index `MEMORY.md`. I did not read CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, or any narrative state doc. No subagents, no background tasks, no discovery suite, no launchctl, no custody paths touched, no file edited other than this ruling.

Charter digest: expected `099de884…a870…c95d81` (convening prompt), observed `099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81`; method: `scripts/validate_gate_packet.py` receipt v2. First run with the prompt's deliberate-typo sha (`…a880…`) returned REFUSE `charter_trusted_observed_mismatch`, rc 2. Second run with the correct sha returned PASS, rc 0, packet sha `a77c4ab3…0410b0`, all six exhibit digests observed = expected. Checkout `5472ff53`, tracked chain in the working tree = `4f1ede1e…`.

## 1. Executed probes (primary evidence)

- P1 `python3 scripts/gen_derivation_night.py --check` on main: `PASS generated derivation-night wrapper region matches`, rc 0.
- P2 Chain SHA-256 by `git show <rev>:scripts/night_chains/calibration_derivation_only.zsh | shasum -a 256`: d81c4cae → `b8bf5b0a…`; 3015cb39 → `b8bf5b0a…`; 5472ff53 → `4f1ede1e…`; a4d530cd → `b5beea46…`. Exhibit B's table reproduces exactly. `git merge-base HEAD a4d530cd` = 5472ff53: the abort lane is one commit ahead of main, chain diff 5472ff53..a4d530cd is only the `abort_window_exhausted` hunk (`--custody-budget-s`).
- P3 Generator timing literals, `git show 3015cb39:scripts/gen_derivation_night.py` vs `a4d530cd`, grep on SETTLE/CADENCE/SLOT_COUNT/CAPTURE_BUDGET/PRE_REGISTERED/DIAGNOSTIC_NO_PACK: identical values at every hit, line numbers shifted by +7. `PRE_REGISTERED_SLOT_COUNT = 12`, `DEFAULT_SETTLE_S = 600`, `DEFAULT_SLOT_CADENCE_S = 600`, `DEFAULT_SLOT_CAPTURE_BUDGET_S = 480`, `PRE_SETTLE_ALLOWANCE_S = 300`, `DERIVATION_RECEIPT_CLASS = "DIAGNOSTIC_NO_PACK"` (a4d530cd lines 74–95). The full generator diff 3015cb39..a4d530cd is docstring, comments and rendered runsheet prose only; no code path changed.
- P4 Chain on main, science-bearing lines: defaults `SLOT_COUNT 12 / SETTLE_S 600 / SLOT_CADENCE_S 600 / SLOT_CAPTURE_BUDGET_S 480` (85–90); ONE `settle` at 211, after the reservation and before the slot loop (215); cadence anchored to actual slot start (275); `window_exhausted` abort never compresses a slot (219–235); writer flags `--allow-live --derivation-only` (245–246); `--sleep-display-before-capture` absent, stated at 47–49; `--power-policy ac_high_power` (256).
- P5 What the gate binds (`joulewise/night_gate.py:292`, `scripts/run_night.py:1799–1806`): the plan's `chain_path` (the generated wrapper) against the arm-time sidecar; the wrapper (`gen_derivation_night.py:408–409`) binds the tracked chain's digest. No code reads the pre-registration's digest sentence. Exhibit F's characterization is correct.
- P6 Pre-registration revision 1, lines 279–284, "Fields filled at commit": `[CHAIN_SHA256]` (the capture chain's digest) is listed with `[SEQ]`, `[DIGEST]`, `[MLX_VERSION]` as "a fact that does not exist yet; none is a scientific choice, and filling them does not reopen any rule above."

## 2. Packet hygiene (charter §6)

- MATERIAL, cured by P3: exhibit C's block "Timing literals in the generator at a4d530cd (grep)" is EMPTY. The exhibit therefore proves nothing about a4d530cd on its own; the packet's central claim rested on it. I executed the probe myself; the claim holds.
- MATERIAL, not cured by the packet: exhibits D and E summarize the chain change as "no change to any timing, capture, slot or settle constant." True for constants, but the diff (exhibit B) also (1) DELETES the separate pre-reserve `readiness` command, folding it into `--pre-reserve-strict`; (2) adds `--custody-deadline-epoch-s $((WINDOW_END_EPOCH_S - 10))` to every capture writer, so a governed read that cannot finish 10 s before window end is now a typed refusal (writer rc 2 → `slot_refused`, chain exits with the session open, chain 262–268) where before it would have run past the window; (3) moves the operator-log `mkdir` after the reservation. None is a timing literal, but (2) is a new slot-outcome path and must be named in the revision, not hidden under "operational."
- NIT: exhibit F's closing sentence calls the digest sentence "a SCIENCE pin"; revision 1 itself (P6) calls it a filled-at-commit fact that is "not a scientific choice." Unlabeled characterization; the primary text governs.
- NIT, out of scope: the same "Ledger baseline" paragraph pins head sequence 76 / `08456d50…`, also a filled-at-commit field; the packet does not ask whether it is still current.

## 3. Q1 — may the sealed chain-digest field be re-pinned by a dated revision 3?

**AFFIRM, option (iii): affirm with the as-merged condition.** Deciding evidence: P6. Revision 1 classifies `[CHAIN_SHA256]` as a non-scientific fact filled at commit, so re-filling it by a dated revision is what revision 1 already contemplates, provided no science rule moves. That no science rule moved is proven by P3 (generator literals identical), P1 (runsheet region regenerates byte-exact from the current chain), and P4 (settle-once-before-d01, 12 × 600 s cadence anchored to start, fixed order, protocol id, writer-flag omission, DIAGNOSTIC_NO_PACK, all present on main). Option (ii) is rejected: the instrument is `powermetrics_pulse_fiducial_v3` under the epoch tuple at lines 133–137, not the launcher's plumbing bytes; re-registering would restart a campaign whose sample definition has not changed.

The condition: revision 3 must pin the digest of the chain AS MERGED at the arm head. Today main carries `4f1ede1e…`; exhibits D and E already quote `b5beea46…`, which exists only on the unmerged abort lane. A revision written today against either value is stale the moment the other lands. So revision 3 is written with a placeholder, filled at the arm head, and verified by the regression in Q4(a).

Mechanism vs contract: this is a **contract change to the registration record** (a dated revision under rule 11, needing this gate's or Ed's authority), of a field the contract itself designates non-scientific. No science rule is amended. Severity of the underlying defect: MATERIAL (a night armed today would carry a registration whose digest names bytes the repository no longer contains).

## 4. Q2 — revision 3 text, to be appended verbatim after revision 2's last line

```
---

# Revision 3 (2026-09-17, cold-gate ruling 69, packet 69)

STATUS: cold-gate ruling 69 (packet 69, activation 9853dd2b); recorded by the
magistrate; not a magistrate amendment (rule 11)

Revision 1 above is sealed and revision 2 stands as written. Not one word of
either is edited here. This revision does one thing and nothing else: it
re-fills the `[CHAIN_SHA256]` field that revision 1 lists under "Fields filled
at commit" as "a fact that does not exist yet; none is a scientific choice, and
filling them does not reopen any rule above."

## Provenance

Cold-gate packet 69 (docs/process_traces/2026-09-16-activation-9853dd2b/
69-coldgate-packet-prereg-chain-digest/00-PACKET.md, sha256 a77c4ab3…0410b0)
and its exhibits A–F, adjudicated by the cold Fable judge in 10-coldgate-fable-
ruling.md of the same directory. The chain digest history is exhibit B; the
generator literal comparison is the judge's own probe P3.

## The one change

Revision 1, "Sample.", reads: "chain digest
b8bf5b0a85bb2012eed9763f70743963d6f24c3ec3038142525766c00f1ac8cf."

For every capture night opened after this revision lands, that sentence is
read as: "chain digest <CHAIN_SHA256_AT_ARM_HEAD>, the SHA-256 of
scripts/night_chains/calibration_derivation_only.zsh at the committed head the
night is armed from."

The placeholder is filled by the magistrate, at the arm head, with the output
of `shasum -a 256 scripts/night_chains/calibration_derivation_only.zsh`, in
the same commit that arms the night, and it is verified three ways: the test
tests/test_preregistration_chain_digest.py (ruling 69 Q4) fails unless this
sentence's digest equals the tracked chain's; `python3
scripts/gen_derivation_night.py --check` passes at that head; and the plan
sidecar the night gate reads at t0 refuses `night_chain_digest_mismatch` if
the bytes move afterwards.

## Why no science rule moved

The chain changed on 2026-09-17 (PR #350 and the end-of-window abort lane)
to: bound every governed custody read by a budget (`--custody-budget-s`) and
a deadline (`--custody-deadline-epoch-s`, window end minus 10 s); fold the
separate pre-reserve readiness command into `--pre-reserve-strict` on the
reservation itself; add a verify-only reservation probe (`NIGHT_VERIFY_ONLY`);
export a refusal-document path and a custody-budget marker; and bound the
session abort. One consequence is stated so it cannot be read as hidden: a
capture whose custody read cannot finish before the deadline is now a typed
refusal (slot_refused, session left open for desk recovery) where the sealed
chain would have run past the window. That is a stop condition, not a
tuning: it changes no value any capture records.

Evidence, verifiable at the arm head: the generator's timing literals
(PRE_REGISTERED_SLOT_COUNT 12, DEFAULT_SETTLE_S 600, DEFAULT_SLOT_CADENCE_S
600, DEFAULT_SLOT_CAPTURE_BUDGET_S 480, receipt class DIAGNOSTIC_NO_PACK) are
byte-identical between the sealed head 3015cb39 and the arm head; the
runsheet check regenerates byte-exact; the chain still performs one settle
after the reservation and before slot d01, anchors each next start to the
actual slot start, aborts window_exhausted without compressing a slot, runs
the writer with --derivation-only and --power-policy ac_high_power, and omits
--sleep-display-before-capture.

## What this revision does NOT change

The epoch tuple, the powermetrics and MLX pins, the ledger baseline sentence,
the sample size and window shape (one 600 s settle, 12 slots at 600 s
start-to-start cadence, fixed order, agent-free), the protocol id, the
membership, exclusion, stopping and analysis rules, V3, the known-conditions
section, revision 2's equivalence rule and both of its branches. It authorizes
no window and licenses no measurement.
```

## 5. Q3 — should the pre-registration pin chain bytes at all? (named, not ruled)

This is a **contract change**, not a mechanism choice: it rewrites the sealed "Sample." sentence's binding object from a byte digest to a literal tuple, and under rule 11 that is a dated revision by this gate or Ed. It is a small one, because revision 1 already says the digest is not a scientific choice, and because the gate never reads the sentence (P5). The sentence a future revision would need:

"Sample. … The night is bound by these literals, verified by regression against `scripts/gen_derivation_night.py` and the tracked chain at the arm head: one 600 s settle after the reservation and before slot d01; 12 declared slots; 600 s start-to-start cadence anchored to each slot's actual start; 480 s capture budget; fixed order d01–d12; `pulse_protocol_id` powermetrics_pulse_fiducial_v3; `--derivation-only` present and `--sleep-display-before-capture` absent; receipt class DIAGNOSTIC_NO_PACK. The launcher's byte digest is pinned per night by the plan sidecar the night gate refuses on, and is recorded in each night's arm record, not here."

## 6. Q4 — the regression

**Rule (c), both, as one module `tests/test_preregistration_chain_digest.py`, no discovery-suite dependency.**

- (a) Parse the pre-registration, take the digest from the LATEST revision (revision 3's replacement sentence once filled; revision 1's line 144 until then), and assert it equals `sha256(scripts/night_chains/calibration_derivation_only.zsh)`. It must be revision-aware, or revision 3 can never satisfy it. What it forces: every chain edit, however operational, fails CI until a dated revision re-fills the field, which under rule 11 means a cold gate or Ed before the edit can be armed. That is the intended cost; lane 227 asks for exactly this.
- (b) Assert `gen_derivation_night.PRE_REGISTERED_SLOT_COUNT == 12`, `DEFAULT_SETTLE_S == 600`, `DEFAULT_SLOT_CADENCE_S == 600`, `DEFAULT_SLOT_CAPTURE_BUDGET_S == 480`, `DERIVATION_RECEIPT_CLASS == "DIAGNOSTIC_NO_PACK"`, each parsed from the pre-registration's own text rather than hard-coded twice; and assert the chain text contains `--derivation-only` and does not contain `--sleep-display-before-capture`. What it forces: a literal edit fails until the science rule itself is re-registered, which is a new campaign, not an addendum. The existing `--check` tripwire (tests/test_gen_derivation_night.py:980) covers runsheet drift only and does not bind the pre-registration; (b) closes that gap.

(a) alone would let the next chain edit pass once the digest is re-filled even if a literal moved with it; (b) alone lets bytes drift silently. Together, (a) makes drift loud and (b) makes the loud event cheap to adjudicate, because the judge can read one test's pass to know no science rule moved.

## 7. Disagreements with the lead's labeled disposition

None on the answer. Two on the record: the packet's "operational only" summary omits the new deadline-refusal outcome (§2, cured in the revision text), and exhibit C's empty a4d530cd block was a defect the judge had to cure by probe.
