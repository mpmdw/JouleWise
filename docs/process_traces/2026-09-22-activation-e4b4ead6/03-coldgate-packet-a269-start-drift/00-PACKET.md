# Cold-gate packet — lane ENVELOPE-START-DRIFT-01 (A269): the evidence-night harness overruns its own 600 s slot pitch by 7.6–10.2 s per envelope, and the cure choice amends a ruled pre-registration and a sealed cold ruling (rule 11 triggers: reinterpretation of a prior verdict — ruling 14 R6's precondition and its factual premise; a change to a ruled registration; a measurement-window commitment depends on the ruling)

Assembled 2026-09-22 by the resident magistrate (activation e4b4ead6). Mechanically assembled: exhibit A is verbatim `git show ecbc0fac:<path>` function extracts located by `ast` (generator in this directory); exhibit B is verbatim file/line extracts at `ecbc0fac`; exhibit C is verbatim generator output executed this session over the READ-ONLY harvest archive (each session record's sha256 is printed in C2); exhibits D1 and D2 are the two independent design consults, verbatim and complete, as delivered (LABELED ARGUMENT from two model families, read-only seats, each with license to disagree). The magistrate wrote only this file, the exhibit headings, and the two generators.

## What happened

Pilot night `qpe01-pilot-n1-20260922-0217` scheduled twelve 600 s envelopes at `first + (i−1) × envelope_s` and blocked on each collector's exit before spawning the next (A `execute`). Every collector stops sampling at `scheduled + 600` regardless of when it started (A `collect`, deadline from `--envelope-start-mono-s`), then serially waits for the recorder, parses a ~133 MB plist, derives the anchor, integrates, hashes, writes; the chain then reaps 113 process groups with one `pgrep` each (A `cleanup_groups` → `_group_census`) and spawns the next collector. C2 measures that tail from the archive's own monotonic stamps: `postparse − stop` 4.85–5.07 s, derive/integrate 0.01–2.29 s (present only when the fit completes), `next pre_spawn − end` 2.61–3.02 s; the chain-level start drift of envelopes 02–12 is 7.63–10.11 s, session-level 7.75–10.23 s (C2), against the registration's `start_drift_max_s: 10` (B1, C1). Envelope 01, the one slot with no predecessor, drifted 0.160 s (C2). Bench re-measurement (C4–C6): `parse_frames` 5.32 s on the envelope-02 plist; one `pgrep -lf -g` 10.9 ms median × 113 = 1.23 s; the A267 attestation query 0.70/0.84 s wall.

**The fact the record got wrong.** Sealed refuter 11's BLOCKER 3 (B3 lines 172, 226) and record 02 (B5, first paragraph) state that `start_drift` "removes" envelopes 03, 06 and 09. C3 executes the summary: envelopes 3, 6, 9 carry `start_drift` AND `incomplete_interior_support` (3 and 9 also `clock_anchor_unresolved`); the set excluded for `start_drift` ALONE is empty. As an as-observed causal claim about this night the premise is false; ruling 14 R6 (B2) rests on it. D1 §Q6(b) gives the forward form both consults accept: once A267 lands (the anchor caps and the exact tiling cure `clock_anchor_unresolved` on 01/03/04/07/08/09/10 and `incomplete_interior_support` on 05/06/11), `start_drift` becomes the sole surviving exclusion on 03, 06, 09 and cuts a potential 12 retained / 6 disjoint pairs to 9 / 3 against `minimum_adjacent_pairs: 4` (B1). Whether that forward argument sustains R6 as written is Q5.

**Two facts that bear on cost.** (i) The registration's `exclusions` list (B1) is pre-registration text pinned by `night_gate.QPE01_PILOT_REGISTRATION_SHA256` and checked byte-for-byte by `frozen_protocol`/`validate_protocol` (A); ruling 14 R4 (B2) orders two new exclusion reasons (`network_time_slew_attested`, `network_time_unattested`), so landing A267 already changes the registration's text or leaves the pinned list incomplete. (ii) `RULED_REGISTRATIONS` (A, `night_gate.py`) admits a registration only by a ruled digest; a re-registration is therefore a ruling, not a magistrate edit.

**The seats' arithmetic (D1 §Q1, D2 §Q1; both re-derived in C).** Plain cure 1 (capture-only collector, batch finalisation after envelope 12, everything else serial) removes parse + derive + hash but leaves stop lag 0.15 + recorder exit ≤ 0.35 + exit 0.2 + census 1.2–2.6 + attestation 0.7–1.45 + spawn 0.05 ≈ 2.5–4.8 s: above the 2 s bar R6 sets. Cure 1 + batched census (one `pgrep -g <list>`, 13.8 ms, C5) serial ≈ 1.0–1.9 s chain-level, ~1.2–2.1 s session-level: at the bar with no margin. D2's design (cure 1 + spawn collector i+1 at its instant after a bounded ≤ 1.5 s wait, attestation and cleanup afterwards in the next slot's lead-in, journal cut so the reaper never touches the live capture) ≈ 0.6–0.9 s session-level, margin > 1 s, but runs the census and the `log show` query while the next capture is recording; D1 §Q2 objects that `log show`'s real work is done by `logd`, a system daemon outside the chain's `observer_cpu_s` (SELF + reaped CHILDREN, C3 `observer_definition` in summary.json), so its energy inside a capture window is unattributed. D1's design (cure 2: `slot_pitch_s: 620` with `envelope_s: 600` unchanged, under a re-registered protocol; output contract untouched; batched census for variance) makes every slot an envelope-01: drift = `Popen` latency, 0.16 s measured; the whole tail (≤ 10.2 s) plus attestation (≤ 1.5 s) sits inside a 20 s gap with no capture running; window 600 + 11 × 620 + 600 = 8020 s < 9000 (C1). Cure 3 (`start_drift_max_s` 10 → 20) leaves the harness overrunning its schedule; both consults decline it.

**Materiality.** The interior is placed from the frozen schedule (`interior_epoch = start.epoch_s − start_drift_s + interior_offset_s`, A `collect`) and `interior.complete_support` proves containment per envelope (A `reduce_interior`); a 10 s drift sits 50 s inside the 60 s offset. Nothing measured on the night was harmed by the drift (D1 §Q6(f), D2 §Q6.4). The cost is cadence: a gate that fires by construction, and window minutes.

The lead's labeled disposition (argument, not evidence): Q1 option (c); Q2 option (a); Q3 option (c); Q4 as stated; Q5 option (a).

## Q1 — Cure: which design makes the harness meet its own schedule with `start_drift_s` ≤ 2 s on every envelope

Options. (a) Cure 1 alone: capture-only collector, batch finalisation after envelope 12, serial attestation and cleanup, batched census. (b) D2's design: cure 1 + bounded-wait spawn-first + journal cut, attestation and cleanup inside the next slot's lead-in. (c) D1's design: cure 2, `slot_pitch_s: 620` (new registration field; `envelope_s` 600 unchanged; `execute` schedules at `first + (i−1) × slot_pitch_s`, window check uses the pitch, `pilot_summary`'s covariate filter unchanged), batched census, attestation and all finalisation inside the gap with no capture running, output contract unchanged. (d) Cure 3: re-size `start_drift_max_s` under a new registration and leave the mechanism.

Lead's disposition: (c). Reasons (argument): it is the only option whose ≤ 2 s bound is measured rather than budgeted (envelope 01, C2); it never places observer or `logd` work inside a capture; it leaves the one-pass `session.json` contract and every consumer untouched; and its registration cost is sunk because R4 already forces a re-registration (Q2). Against: it changes the ruled registration (a ruling is needed, which this gate is) and adds ~220 s to the night (8020 s, C1).

Deliver: the ruled option, or a better one, with the per-slot serial budget you accept as evidence (C2, C4–C6) and, for a harness-only option, the executed number that shows ≤ 2 s with margin rather than a budget.

## Q2 — Registration: does landing ruling 14 R4's two exclusion reasons and (if Q1(c)) `slot_pitch_s` require a new ruled registration before the next night, and what is its exact content

Options. (a) One new ruled registration, `pilot_protocol_v2.json`, byte-identical to v1 except: `exclusions` gains `network_time_slew_attested` and `network_time_unattested`; `slot_pitch_s: 620` added (if Q1(c)); `chain_source_sha256` re-pinned only if the chain script's bytes change; `ruling` names this gate; a new `RULED_REGISTRATIONS` entry with the new digest, v1 retained as ruled history. Everything else — sizing, retention floors, `start_drift_max_s`, `interior_*`, `envelope_s`, `settle_s`, `window_max_s` — unchanged. (b) No re-registration: keep the pinned list as documentary and let `hard_exclusions` carry the new vocabulary in code. (c) Refer to Ed.

Lead's disposition: (a). Deliver: the exact field-by-field content of the re-registration you rule, and whether the new registration must land in the same PR as A267 Part 3 or may follow it.

## Q3 — The R6 precondition's shape: how the "live-installer dry check showing `start_drift_s` ≤ 2 s on every envelope" is to be satisfied

Both consults find (D1 §Q4, D2 §Q4) that a faithful check runs `sudo powermetrics` and is therefore a `[QUIET-MAC]` measurement that cannot run while an agent session is alive; the protocol is byte-pinned to 600 + 12 × 600 s, so no short live variant exists without a registration. Options. (a) R6 as written: one armed, agent-free diagnostic night under the full protocol (`DIAGNOSTIC_NO_PACK`), then the re-run night. (b) A three-envelope cadence night under its own registered identity (D1). (c) Amend R6: the re-run night is itself the dry check under a pre-registered in-chain early drift abort — after envelope 02, `start_drift_s` > 2 s on either envelope writes a refusal and ends the night (≈ t0 + 21 min), so the precondition is disproved cheaply or satisfied by the night that counts (D1's proposal; D2 §Q4 names the same reading as "a cold-gate question, not a magistrate call"). (d) Pre-register "the diagnostic night also serves as the re-run if every envelope ≤ 2 s" (D2). In every option, a daytime bench replay with the real chain and collector and an injected recorder replaying an archived plist (no sudo, no measurement) is a necessary pre-step, never labeled as R6 evidence.

Lead's disposition: (c). Reasons (argument): the precondition exists to stop a known-cause failure from spending a 2.6 h window; an early abort stops it at 21 minutes and keeps rules-before-data (the abort rule is registered before t0). Against: it amends a sealed ruling's clause, which only this gate may do.

Deliver: the ruled shape with exact text for the R6 clause it replaces or keeps, the abort rule's exact threshold and envelope count if (c), and where the rule lives (registration field vs chain code).

## Q4 — Attestation mechanics raised by the consults that the A267 seat must follow

(i) Window: ruling 14 R4 derives `--start`/`--end` from epoch stamps ± 1 s; D1 §Q6(e) notes a wall-clock step inside the envelope moves those stamps. Lead's disposition: widen to the union — start = min(`sampling_started.epoch`, `sampling_stopped.epoch` − monotonic span) − 1 s; end = max(`sampling_stopped.epoch`, `sampling_started.epoch` + monotonic span) + 1 s. (ii) Placement: never concurrent with a capture (D1 §Q2: `logd` work is unattributed observer energy); under Q1(c) it runs in the gap. Lead's disposition: affirm as a rule. (iii) Record: ruling 14 R4 says the envelope's provenance gains the attestation (an atomic `session.json` rewrite by the chain after the collector exits); D1 §Q3 proposes a sibling `attestation.json`. Lead's disposition: keep R4's shape.

Deliver: AFFIRM/REJECT each of (i)–(iii) with exact text where you amend.

## Q5 — Record correction and the standing of the p1 promotion

The as-observed premise of refuter 11 BLOCKER 3 and record 02 is false (C3): no envelope was excluded for `start_drift` alone. Options. (a) Correct both by dated addendum (never by editing sealed text); the p1 promotion and R6's precondition stand on the forward argument (D1 §Q6(b): post-A267, 9 retained / 3 pairs < 4). (b) The premise's failure voids R6's precondition; A269 returns to an idle-time lane and the re-run proceeds on A267 alone. (c) REFUSE pending a re-run.

Lead's disposition: (a). Deliver: the ruled disposition and the exact addendum sentence for the record.

## Regressions

For the ruled Q1 option, deliver the defect-shaped regressions a seat must add (D1 §Q5 and D2 §Q5 each propose a set; adopt, amend, or replace), each with the counterfactual that must FAIL at `ecbc0fac` (the harness with a stub collector that burns 5–7 s after the capture) and the production call site it exercises.

## Constraints on the judge

Read-only. Nothing is armed. Do NOT run `systemsetup`, `sudo`, or `powermetrics` in any form. No suite-wide runs; at most one run of the single module `tests.test_quiet_predicate_campaign` (about 30 s). Probes allowed: `git show ecbc0fac:<path>`, `grep`/`rg`, `sed -n`, `python3` over the session records under `/Users/edr/night-archive/qpe01-pilot-n1-20260922-0217-harvest-20260922/night/` (read-only; C2 prints each file's sha256), `shasum`, `/usr/bin/log show` for the window in C4, and `/usr/bin/pgrep` timing as in C5.

## Charter pin

Charter: `docs/process/coldgate_charter.md`
sha256:
099de884b1d081ffa547dfd8ff5837e75813a870ff8c7285c749c1b440c95d81

The judge independently checks this digest against the separately supplied pin in the convening prompt.

## Exhibit manifest

```
8a80bb4214053b447fcfae73fad72d09b1dd353ed005a781b5c960b54290afcc  exhibit-A-code-at-main.md
98a027200806e51e85570c5fa3f381b0006ee5466836f469e0ab1de52541ff21  exhibit-A-generator.py
4fd1c37870af7a7943339a375df87e18369cacb3e0288e6e9a180be16ffc8803  exhibit-B-authorities.md
40359c7330f4f039529f22b5c572ac4fa8d27e424c0818694600a2f6e8ad679f  exhibit-C-executed-evidence.md
b3106d43b49114fb9a695fbb3e1a5e13563a61787b9e5d0bc27406ffb1bc707b  exhibit-C-generator.py
8126ed51b9591abbc4d550ffaf34a90cebcbe5f945710a5515231c2e2f1bdfad  exhibit-D1-consult-opus-seat.md
95354a1970999c36a0d4ce2dce87c4f645c9f72032498897e02bd8e4cd80d9f5  exhibit-D2-consult-fable-seat.md
```
