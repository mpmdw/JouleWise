# 12 — Pairing refuter (contract lens, Opus 5), cold-gate ruling 70

Charter §5 pairing output. Read-only; repo at `1238d7cf`, code paths
byte-identical to `a90ab4e8` (diff over `joulewise scripts configs tests`
empty). All seven exhibit digests re-hashed and match the manifest; charter
hashes `099de884…c95d81` as pinned. Every `file:line` below was read here.

## A. Per-question falsification

| Q | Ruling | Refuter | Note |
|---|---|---|---|
| Q1 | AFFIRM | **CONFIRMED** | `run_night.py:841` (`t0+window_max_s+WINDOW_SHUTDOWN_GRACE_S`), `:69`=300, `:1402-1405` dead-man, `:1507` completion — none reads a GO instant. Chain `:187` `reservation_call` precedes `:218` `settle`, so condition (iii) holds. Prereg `:116-117`, `:143-144` ✓. |
| Q2 | AFFIRM | **CONFIRMED** | No contract text bears on sample count; correctly plan data. Contingency on a REFUSED Q4 makes it inert (§8: REFUSE authorizes nothing) — coherent, not defective. |
| Q3 | AFFIRM cond. | **CONFIRMED** | `night_gate.py:57` `LOAD_MAX = 2.0`, `:1208` `if load_1m > LOAD_MAX`. D-161 `decision_log.md:207` ("fail-closed STAYS where the failure is PHYSICS/EVIDENCE or PRE-REGISTRATION") and D-181 `:11914-11916` ("…the census at arm and at t0") verified verbatim. |
| Q4 | REFUSE | **CONFIRMED** | See check 1. Both values verified: exhibit G `:42` `"busy_core_max": 0.05`, `:49` "is a PLACEHOLDER … Do not describe it as validated"; exhibit A's 0.01 per packet Q4. Two values, no named cutoff. D-078 cl.11 `decision_log.md:4745-4760` quoted correctly (0.29–0.49 J; 0.7–1.0 J envelope). |
| Q5 | AFFIRM cond. | **PARTIAL** | Arithmetic right (check 7), but the measured round is `ps`×2 + `top` only; the Q6 condition adds a **fresh `pgrep` census per sample** not in the 0.217 cpu-s figure, so the affirmed budget under-measures the design it binds. `PROBE_TIMEOUT_S = 30` at `:62` ✓. |
| Q6 | AFFIRM | **PARTIAL** | Semantics confirmed: AC `night_gate.py:1164`, display `:1184`, thermal `:1224-1241` (empty `thermal_limits` ⇒ `any()` False ⇒ PASS), HID `:46-52`+`:1146` (`hid.stdout.strip() != "0"` on the `com.apple.screensaver` `idleTime` preference), prereg `:264-268`. Replay claim ✓. Added per-sample-fresh-census requirement exceeds the proposition (check 6). |
| Q7 | AFFIRM | **CONFIRMED** | Constants and enforcement site verified (check 2). |
| Q8 | AFFIRM | **CONFIRMED** | `night_gate.py:217-221`, `:22-26` (`v2` plan / `v3` pack), `:1375-1377`. Independent grep: `night_plan.v4`, `unattended_night_receipt.v3` occur nowhere in `joulewise scripts tests docs/contracts`. |
| Q9 | REJECT | **REFUTED (material)** | See check 3. The stated premise — that Ed reserved the ruling — is false in tracked text, and the charter required REFUSE here, not a merits verdict. |
| Q10 | 4 items | **PARTIAL** | Items 1, 2, 4 confirmed (item 4: `NIGHT_HANDBACK.md:134-142` is R1 operative text through the retry-class sentence). Item 3's mechanism is wrong (check 4). Table pointer "Q10 | see §11" should read §12 (NIT). |

## B. The eight named checks

1. **480 s slot / joule arithmetic — CONFIRMED.** `gen_derivation_night.py:88`
   `DEFAULT_SLOT_CAPTURE_BUDGET_S = 480`; prereg `:100-102` "then one 480 s
   capture budget for the twelfth slot. 600 + 11 × 600 + 480 = 7680". Exhibit G
   `:18` does say "roughly 300 J over a 60 s capture slot"; 480/60 = 8×.
   Recomputed: 0.05 × 5 W × 480 s = **120 J**; 0.01 → **24 J**; 1 J ÷ (5 × 480)
   = **4.17e-4 core** ⇒ "0.0004", below the sampler's 0.0072. All four correct.
   *NIT:* 480 s is a budget, so the joule figures are upper bounds used as
   durations without saying so. The P/E asymmetry the ruling flags is real and
   now pinned: `hw.perflevel0/1.logicalcpu` = 12 / 4, `hw.logicalcpu` = 16.
2. **Schedule arithmetic — CONFIRMED.** 600 + 6600 + 480 = 7680; +300 = 7980
   (`:74` slot count 12, `:86-88` constants, `:95` allowance, enforced at
   `:511-513`, line 513 being `if plan.window_max_s < required_window:`).
   9600 − 600 = 9000; 9000 − 7980 = **1020**, equal to today's. Packet
   cross-checks 1620 (t0+0) and 1433 (t0+187) hold.
3. **§11 / Q9 — REFUTED, highest materiality.** The cited lines are real
   (`arm_retry.py:31`, `:88-90`, `:164-166`; `NIGHT_HANDBACK.md:142`; prereg
   `:78` "quiet-census, boot/clock, and **no-retry** conditions must still
   pass"). But "A212 part (b) is recorded as awaiting Ed's ruling" is **false
   at its own source**. In
   `…/2026-09-15-activation-08ca8197/06-refusal-fast-retry-lane-registration.md`,
   lines 36–40 are the pre-amendment paragraph; lines **44–61** are
   "## Amendment (2026-09-16 ~00:40 PDT) — part (b) ruled", quoting Ed at
   00:35 — *"unless there's a scientific reason that's an unsound decision
   absolutely reduce the hours to 20 min"* — and stating (`:51-55`) "part (b)
   is RULED, not ruling-gated. A zero-capture t0 refusal on machine state
   (`night_refused_not_quiet`, `night_refused_agent_present`,
   `night_refused_hid_idle`, `night_refused_boot_clock`; `refusal.json`
   present, no receipt, no `chain.started`) is a pre-authorized retry".
   Corroborated at `docs/process/automation_history_2026-09-16.md:286-288`
   and `:429`.
   Exhibit E §E4 quotes `1-12` and `28-40`, stops **four lines short** of the
   amendment heading, then tells the judge "lines 36–40 say the remedy is not
   yet authorized" — omitted contrary evidence from the same file, unlabeled
   argument, no digest or contiguous context: charter §4 admissibility failure.
   **What IS tracked:** Ed's ruling exists in two process-trace/history docs;
   there is **no** decision-log entry (`grep A212|REFUSAL-FAST-RETRY` over
   `docs/decision_log.md` returns nothing) and `NIGHT_HANDBACK.md:465` still
   says "queued, not landed", `:142` still limits successor arms to
   retry-class aborts, and `night_refused_not_quiet` is still keyed into
   `COLD_GATE_CODES`. So "not installed in contract text" survives; "Ed
   reserved it" does not, and the cure — "a dated decision-log addendum **by
   Ed**" — demands an act already performed. Correct cure: install the existing
   ruling as that addendum (the registration's own plan at `:39-40`), then
   decide the open point — whether a **bind-expiry** refusal, a class that did
   not exist when Ed ruled, is inside the four codes he named. Compounding:
   charter §4 ("If an excerpt's completeness or neutrality cannot be verified,
   REFUSE the affected question") was triggered by the ruling's own §13
   admission, and a merits REJECT issued anyway.
4. **§12 item 3 — REFUTED as reasoned; conclusion survives on other grounds.**
   `DISPOSITIONS` (`arm_retry.py:74-79`) is
   `{**dict.fromkeys(COLD_GATE_CODES, "cold_gate"), …}` — only **keys** enter
   classification, and `classify_abort` (`:90`) defaults unknown causes to
   `"cold_gate"`. Reusing `night_refused_not_quiet` and minting a new code
   therefore classify **identically**; "it feeds the retry classification
   table" does not distinguish them. The real exposure is the *description
   string* at `:31`, published into the handback by `render_policy` (`:195`,
   rows `:202`) — already item 2 — plus `:28` "registry additions must force
   review". MATERIAL reasoning defect, not verdict-changing.
5. **§8 census-replay claim — CONFIRMED.** `run_night.py:2057-2064`, legacy
   branch: `cached = [initial_probe]`; `first_census(argv)` returns
   `cached.pop()` when `tuple(argv) == night_gate.AGENT_CENSUS_ARGV`. The
   driver's first census is replayed into the evaluator exactly as ruled.
6. **§5's binding condition — CONFIRMED within authority (NIT on form).**
   Q3 asks whether load may cease to veto **admission**; the design replaces it
   with a CPU predicate, so conditioning the AFFIRM on that replacement being
   in force is scope-marking, not rule-making, with D-161/D-181 as the reason
   the unconditioned reading would delete a physics refusal. *But* "AFFIRM
   (conditional)"/"(design)" are not charter §8 verdict tokens; the magistrate
   must record them verbatim, never as a bare AFFIRM. The **§8/Q6** condition
   goes further: a fresh census on **every** sample is a cadence the
   proposition does not ask about, and is uncosted in Q5.
7. **Probe arithmetic — CONFIRMED.** 45.2/30.1 = 1.5017 → 1.50; 9.36 + 3.6 =
   12.96 %, × 16 = 2.0736 → 2.07 (16 logical CPUs confirmed); 0.217/30 =
   0.00723 → 0.0072 and /60 = 0.0036; 0.0072 × 5 W = 0.036 W, × 30 s = 1.08 J
   ≈ 1 J; 0.0072/0.01 = 72 %. All correct. The per-process attributions and
   19:47 timestamps are the judge's own live observations, not reproducible
   here, and correctly labelled under §7.
8. **Charter compliance — PARTIAL.** One verdict per Q1–Q9 ✓; severity tiers ✓;
   hygiene section non-trivial ✓; no rule amended ✓; lead's disposition
   addressed ✓. Defects: (a) Q9 merits verdict where §4 mandated REFUSE;
   (b) 14,295 bytes — under 14 KiB (14,336) but over a decimal 14 kB;
   (c) §0 discloses `~/.claude/CLAUDE.md` and the session `MEMORY.md` index as
   auto-loaded, which §4 forbids — honest about an unavoidable harness load,
   but that index carries "Refusal fast-retry ruling — Ed 2026-09-16:
   zero-capture t0 refusals auto-retry (A212)", which **contradicts §11** and
   went unreconciled; (d) the packet's Q10 is an enumeration, not an
   AFFIRM/REJECT/REFUSE proposition — an unnamed hygiene defect; (e) table
   pointer "Q10 | see §11" (should be §12).

## C. Errors ordered by materiality

1. **§11/Q9 premise false** — Ed ruled A212(b) on 2026-09-16; the ruling says
   he reserved it. Changes the cure and the actor. REJECT survives as "not
   installed in contract text", but reasoning and remedy need rewriting.
   *(BLOCKER for acting on §11 as written.)*
2. **Q9 should have been REFUSED under charter §4**, given the ruling's own
   admission that the excerpt's neutrality was unverified — and it was in fact
   selectively cut. *(BLOCKER, procedural.)*
3. **Packet defect (not the judge's):** exhibit E §E4 omits the amendment four
   lines past its excerpt and adds an unlabeled conclusion about it.
   *(BLOCKER for the packet; re-cut it.)*
4. **§12 item 3's mechanism claim is wrong** — key reuse and a new code
   classify identically. *(MATERIAL; conclusion survives, reasoning must be
   restated.)*
5. **Q5/Q6 coupling unreconciled** — the affirmed observer budget excludes the
   per-sample fresh census Q6 makes binding. *(MATERIAL for sizing; changes
   neither verdict.)*
6. **Q6's per-sample-fresh-census condition exceeds the proposition.**
   *(MATERIAL; defensible as corollary; carry it as guidance.)*
7. NITs: 480 s ceiling used as a duration; "Q10 | see §11"; size compliant
   only on the binary reading; auto-loaded doctrine/memory; Q10 not atomic.

## D. Actionability

The magistrate may act on **Q1, Q2, Q3, Q4, Q7 and Q8 as written**: every
load-bearing citation there is correct at the stated lines, the joule and
schedule arithmetic recompute exactly, and the Q4 REFUSE with its four-part
minimum cure is within the charter and right on the evidence supplied.
**Q5 and Q6 are actionable with the coupling noted** — the observer budget
must be re-measured *including* the census probe before the 0.007-core floor
is quoted in any cutoff derivation, and Q6's per-sample condition carried as
guidance, not as a ruled requirement. **Q9 and §12 item 3 must be corrected
before use.** Q9 rests on an excerpt cut four lines short of Ed's 2026-09-16
ruling that a zero-capture machine-state refusal *is* a pre-authorized retry;
the charter required REFUSE once the judge found that excerpt's neutrality
unverifiable, and the cure it names asks Ed for a ruling he already gave. The
outcome is unchanged — nothing in exhibit G §D7 may land yet — but for a
different reason: the ruled remedy is not *installed* (no decision-log
addendum; `NIGHT_HANDBACK.md:142` and `:465` unchanged), and whether a
bind-expiry refusal sits inside the four codes Ed named is genuinely open.
Item 3's reason must be restated as the published description text, or folded
into item 2. Recommend: re-cut exhibit E §E4 with the amendment and convene a
bounded post-seal rebuttal round on Q9 alone.
