# Cold-gate ruling 70 — NIGHT-GATE-QUIET-ADMISSION-01 (Fable 5.1, cold seat, 2026-09-17 19:45–19:5x PDT)

## 0. Trust anchors and disclosure

- Auto-loaded before any choice of mine: `~/.claude/CLAUDE.md`, project `CLAUDE.md`, memory index `MEMORY.md`. Not read: CLAUDE.local.md, RUN_STATE.md, TASK_QUEUE.md, any narrative state doc beyond the bounded quote checks in §12.
- Validator run 1 (charter sha `…870ff…` typo variant `…880ff…`): `REFUSE`, `charter_trusted_observed_mismatch`, rc 2. Run 2 with charter `099de884…c95d81` and packet `be6e071a…113c53`: `PASS`, rc 0, seven exhibits digest-matched. Method: `scripts/validate_gate_packet.py` receipt v2; expected values taken from the convening prompt, observed values from the receipt.
- Checkout `80ff3a01`; `git diff a90ab4e8 HEAD --stat` over `joulewise scripts configs tests` and the cited docs is empty, so every `a90ab4e8` line below was read at the same bytes. Every `file:line` cited was read by me this session.

## 1. Own observations on this machine (a live interactive session was present; the census would have refused; these characterise the sampler, not a quiet machine)

| Time (PDT) | Probe | Result |
|---|---|---|
| 19:47:22→19:47:52 | `ps -Ao pid,lstart,time,comm` twice, 30.1 s apart, Σ ΔCPU / elapsed | **1.50 busy-core-equivalents** (45.2 cpu-s); `mds_stores` 0.96 core, `WindowServer` 0.14, Terminal 0.07, this judge's two `claude` processes 0.06 + 0.04; 7 exited processes unaccounted |
| 19:47:57 | `top -l 2 -s 5 -n 0`, second sample only | 9.36 % user + 3.6 % sys = 12.96 % busy × 16 logical CPUs = **2.07 host busy cores** (earlier second samples: 0.52 at 19:45:33, 1.37 at 19:46:52) |
| 19:50:01 | `sysctl -n vm.loadavg` | `{ 2.31 2.11 2.34 }` |
| 19:50:01 | one sampler round (`ps`×2 + `top -l 2 -s 5`), children rusage | **0.217 cpu-s → 0.0072 core per 30 s interval** (0.0036 per 60 s) |

Reading: `mds_stores` alone is ~1 core at load 2.1–2.3, the direction the packet reports. The sampler's own cost is 72 % of the consult's 0.01-core candidate.

## 2. Verdicts

| Q | Verdict | Severity | Deciding evidence |
|---|---|---|---|
| Q1 | AFFIRM | MATERIAL | D2/D3/D4 (`run_night.py:841,1402-1405,1507`), D6 (`chain:187,218`), prereg `:116-117` |
| Q2 | AFFIRM | MATERIAL | D6 (settle after reservation); own probe §1 |
| Q3 | AFFIRM (conditional) | MATERIAL | B2, B4; own probe §1; D-181 `:11914-11916` |
| Q4 | REFUSE | BLOCKER (for activation only) | packet defect: no evidence in joules; own probe §1 |
| Q5 | AFFIRM (conditional) | MATERIAL | own probe §1 (0.0072 core/round); D1 `run_night.py:62` |
| Q6 | AFFIRM | MATERIAL | C6 `night_gate.py:1164-1251`; D5 `run_night.py:2058-2064`; D-181 `:11914-11916`; D-161 `:207` |
| Q7 | AFFIRM | NIT | D7 arithmetic re-verified; `gen_derivation_night.py:74,86-88,95,511-513`; prereg `:103-117` |
| Q8 | AFFIRM (design) | MATERIAL | C1 `:22-26`, C3 `:221`, C7 `:1375-1377`; schema ids `v4`/receipt `v3` unoccupied (grep) |
| Q9 | REJECT | BLOCKER (for exhibit G §D7) | E1 `arm_retry.py:31`, E3 `NIGHT_HANDBACK.md:142`, E4 `:36-40`; prereg `:78` |
| Q10 | see §11 | — | exhibit G |

## 3. Q1 — waiting inside a sealed bind allocation: AFFIRM

Every boundary the registered schedule cares about derives from `t0` and `window_max_s` only: forced shutdown `t0+window_max_s+300` (`run_night.py:841`, `:69`), completion `+300` (`:1507`), dead-man (`:1402-1405`). None reads a GO instant. After GO the chain reserves first (`calibration_derivation_only.zsh:187`) and then runs its one settle (`:218`), so a pre-reservation wait moves no registered quantity. The pre-registration defines the window by its END (`:116-117`) and the sample by settle + 12 slots (`:143-144`); it says nothing about when between `t0` and `E` the gate may admit. Conditions: (i) the first sample is taken AT `t0` so D-181's "census at `t0`" (`decision_log.md:11915`) is kept literally; (ii) the wait is plan data in a NEW plan (Q8), never a default; (iii) the receipt must state that admission evidence is not capture evidence (the settle and reservation follow it). Severity MATERIAL because of (iii): a GO receipt must never be read as a clean-window certificate.

## 4. Q2 — two consecutive 30 s quiet intervals: AFFIRM

Interval CPU-time differencing already integrates over 30 s, so one sample is not a snapshot; a second consecutive sample is the minimum that distinguishes a finished burst from a pause inside one. The count is an operational parameter carried as plan data, not a science tolerance, and it is not "microscopic". It rules nothing about capture quality: the 600 s settle after reservation (D6) is what protects the first slot. AFFIRM contingent on Q4: with no ruled cutoff there is nothing for the two samples to be quiet against.

## 5. Q3 — load average may cease to veto: AFFIRM, conditional

Executed evidence: two clean-census nights refused on load (B2 `load_1m` 2.55, B4 3.66); three hours later load 1.3–1.5 with `fseventsd` at ~0.9 core (B4 line 25, a `%CPU` decaying-average reading, corroborated by the cumulative 1152 CPU-min figure); my own probe: `mds_stores` at 0.96 core under load 2.1–2.3. The load average is run-queue length, not the energy-bearing quantity. Condition (binding): the load veto may be removed ONLY in a plan whose interval-CPU predicate is active with a cutoff this gate has affirmed (Q4). Removing the veto with no CPU fence in force would delete a physics/evidence refusal, which D-161 (`decision_log.md:207`) and D-181 (`:11914-11916`) forbid. Load stays recorded as a diagnostic on every sample and receipt. Until Q4 is satisfied v2 semantics (`LOAD_MAX`, `night_gate.py:57,1208`) remain the only admission rule.

## 6. Q4 — the aggregate CPU cutoff is scientifically adequate: REFUSE

Defect: the packet contains no evidence in the instrument's units. It offers wattage arithmetic (exhibit A §2; exhibit G "5 W × 60 s = 300 J") and two different candidate values, 0.01 (A) and 0.05 (G, "placeholder"), so the proposition does not even name one cutoff. The arithmetic is also mis-scaled: a slot's capture budget is 480 s (`gen_derivation_night.py:88`; prereg `:100-102`), not 60 s. At the brief's own 5 W/core, 0.05 core → 120 J per slot and 0.01 core → 24 J per slot, against the ≈1 J attribution limit and ≈5 J claim bar of D-078 cl.11 (`decision_log.md:4745-4760`: repeatability 0.29–0.49 J, clock-anchor envelope 0.7–1.0 J); a 1 J-per-slot ceiling at 5 W/core would be 0.0004 core, below the sampler's own 0.0072 core. Either the W/core assumption is wrong for the E-core/P-core mix or stationary background largely cancels in the ABBA contrast; which one is exactly what must be measured, not assumed. The consult's own recommendation is argument and did not decide this.

Minimum cure (evidence that would satisfy the gate, instrument units):
1. Measured joules per slot attributable to a stationary synthetic load at the candidate cutoff and at 10× the candidate, run through the actual floor pipeline (ABBA contrast, 480 s captures), reported as ΔJ per floor against the ≈1 J / ≈5 J bars, on this machine under the 25G83 epoch.
2. The sampler's `busy_cores` distribution during captures already accepted as clean (r6 envelope or the six clean bundles), so the cutoff sits above the clean-machine floor including the observer's ~0.007 core.
3. The sampler's reading under the known contaminant (my 1.50-core reading is one such point).
4. One named cutoff derived from (1)–(2), sealed as plan data.
Severity BLOCKER for activating `cpu_interval_v1` with any value; not a blocker for building the mechanism with the value as plan data and no admitting default.

## 7. Q5 — sampler observer effect acceptable: AFFIRM, conditional

Measured: 0.217 cpu-s per round → 0.0072 core over a 30 s interval, ~0.036 W at 5 W/core, ≈1 J over a 30 s interval, and it runs only BEFORE reservation, so it never overlaps a capture. Acceptable as admission overhead provided (i) it is counted, labelled `observer: true`, never subtracted (exhibit G §D2), and (ii) any cutoff ruled under Q4 is set knowing the floor is ≈0.007 core, which makes the 0.01 candidate practically unattainable. `PROBE_TIMEOUT_S = 30` (`run_night.py:62`) cannot wrap a 30 s sampler; the driver needs separate supervision (exhibit G §D6). No measurement of the sampler under a quiet machine exists; the packet supplied none (hygiene, §12).

## 8. Q6 — non-CPU predicates stay terminal during binding: AFFIRM

Census, AC power, screensaver-configuration, thermal, boot/clock, malformed observations, registration/digest are physics, evidence or pre-registration refusals; D-161 keeps them fail-closed and D-181 names the census at `t0` explicitly. Present semantics verified: AC `night_gate.py:1164`, display `:1184`, thermal passes with no `CPU_Speed_Limit` line (`:1224-1241`), HID reads the `idleTime` default (`:46-52`, `:1146`; prereg `:264-268` records the same). Binding condition: each is re-evaluated on EVERY sample with a FRESH census; today's evaluator replays the driver's first census (`run_night.py:2058-2064`), and that replay must not survive into the bind loop. Compound question noted (§12); the set is answerable because no member differs.

## 9. Q7 — 9600 s preserves the registered schedule: AFFIRM

Re-derived: settle 600 + 11 × 600 + 480 = 7680 (`gen_derivation_night.py:86-88`), + 300 allowance (`:95`) = 7980, enforced at `:511-513` with `PRE_REGISTERED_SLOT_COUNT = 12` (`:74`). GO at the bind deadline `t0+600` leaves 9000 s ≥ 7980 (slack 1020 s, equal to today's). The pre-registration pins the MINIMUM 7980 and calls 9000 "recommended" (`:103-111`); the window end is `t0+window_max_s` (`:116-117`). Nothing registered changes. NIT: the generator must validate `window_max_s ≥ bind_max_s + post_bind_budget_s` AND `post_bind_budget_s ≥ 7980` from the constants, not from prose.

## 10. Q8 — explicit v4 keeps v2/v3 sealed: AFFIRM as a design proposition

`from_mapping` dispatches on `receipt_class` only and demands an exact key set (`:217-221`); receipts demand exact keys and a single `SCHEMA` (`:1375-1377`). A v4 plan reaching v2 code is refused `night_plan_malformed` (fail-closed), and a v2 plan reaching v4 code must take the legacy branch unchanged. `night_plan.v4` and `unattended_night_receipt.v3` are unoccupied in `joulewise`, `scripts`, `tests`, `docs/contracts` (grep), and no `docs/contracts` file pins the night receipt schema. Not yet built; the affirmation binds the implementation to exhibit G regression 7 (byte-identical v2 output, no default insertion) and untouched transaction-pack v3 tests.

## 11. Q9 — bind-expiry refusal within the authorized successor-retry remedy: REJECT

There is no such authorized remedy today. `night_refused_not_quiet` is on the cold-gate path (`arm_retry.py:31,88-90,164-166`); only retry-class aborts authorise a successor without a new gate (`NIGHT_HANDBACK.md:142`); A212 part (b) is recorded as awaiting Ed's ruling (E4 `:36-40`); the pre-registration lists a "no-retry" condition among those a DIAGNOSTIC_NO_PACK receipt must pass (`:78`). A bind-expiry refusal is a machine-state refusal with zero capture; whether it SHOULD license a new-plan successor is a process rule (charter §3.4) that this packet does not present as a proposition and that Ed reserved. Cure: a dated decision-log addendum by Ed (or a gate convened on the rule text with Ed's sight) BEFORE `zero_capture_successor_allowed`, the R1 sentence and the `COLD_GATE_CODES` text change land. Until then exhibit G §D7 installs an unratified rule. Note D-181 "no artificial spacing" supports the direction; support is not authorization.

## 12. Q10 — exhibit G items that exceed mechanism choice

1. `busy_core_max: 0.05` in fixtures, docs and any generated plan: a threshold value, and a different one from the consult's 0.01. Even labelled placeholder it is not the magistrate's; fixtures must carry a value that admits nothing until Q4 is cured.
2. §D7 entire: `zero_capture_successor_allowed`, the new R1 sentence, and rewriting `COLD_GATE_CODES["night_refused_not_quiet"]` (which `render_policy` publishes into the handback). Process rule (Q9).
3. Reusing reason code `night_refused_not_quiet` for bind expiry: it feeds the retry classification table, so it is contract, not journal representation; a distinct code or an explicit ruling is required.
4. Editing NIGHT_HANDBACK R1 (`:134-142`) at all: A172 ruling text.
Mechanism, within the magistrate's discretion: factoring `evaluate_night`, the sample journal, receipt v3 fields, sampler supervision, `_artifact_list`, generator flag, the `:59` "85 minutes" correction (code already derives `t0−600`, `run_night.py:1415`, `magistrate_watchdog.py:86`; land it as its own commit).

## 13. Packet hygiene

- Compound/ambiguous Q4: two candidate cutoffs (0.01 A; 0.05 G) and no single "proposed" value; the summary does not flag the discrepancy. Effect: Q4 REFUSE.
- Unsupported arithmetic: exhibit G's "60 s capture slot"/"300 J" understates a slot by 8× (480 s). The packet repeats the ≈5 J bar without the slot duration. Effect: Q4.
- Incomplete for Q5: no observer-cost measurement anywhere; supplied here by my probe.
- Incomplete for Q9: the pre-registration's "no-retry conditions" (`:78`) is not excerpted in F6 though it is contrary evidence.
- Convening apparatus not frozen: `01-convene-script.sh` is modified and uncommitted in this worktree (checkout reference changed from `a90ab4e8` to `80ff3a01`); the packet and exhibits are digest-pinned and unaffected. NIT.
- Narrative excerpts (B3, B4 lines 25/47, E4, F3) are labelled and bounded; I verified E4 `:36-40`, B4 `:47` and F3 `:145-147` byte-for-byte at their stated lines and read nothing beyond them, so surrounding neutrality is unverified. B4's "85–100 % CPU" is a decaying `%CPU` reading, the metric the consult disqualifies; the cumulative-CPU-minutes figure is the sound part.
- Neutral otherwise: contrary evidence (two of four nights not load losses) is stated; D-181's opposing clauses are quoted whole.

No labeled lead disposition exists in the packet; I concur with the consult's "approve mechanism, withhold activation" shape and REJECT Q9, which exhibit G already builds.
