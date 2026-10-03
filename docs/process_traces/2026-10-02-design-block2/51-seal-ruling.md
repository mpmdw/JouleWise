SEAL: ADMIT

# Cold registration gate G2A-25G83-B2: ruling (cold judge, Claude Fable 5.1, 2026-10-02)

ADMIT is conditional on the eight required text changes in §4 (T1-T8) being applied verbatim, and
on the two code conditions in §5 (C1, C2) being present at the arm head H before the seal record
is written. The rules of the registration are sound and carry D-166 unchanged. What is wrong is
(a) four places where the text can be applied two ways or cannot be executed for the recovery
window, and (b) two places where the harvest code at `e8681d61` does not do what the text says.
None of these needs a second cold gate: T1-T8 are exact replacements, and C1-C2 are "a fix that
only makes code agree with this text" (§11), which goes through the ordinary gated pull request
(PR 458 is not yet merged, so both can land in it).

Registration read: `configs/campaigns/g2a_prefill_probe_25g83/registration_block2.md`, sha256
`2188e0e64f0ca64c3d63f12bfec6960bf79e92da0ccf2eff5bbcb0c7820ea78d` (verified), 252 lines.
Worktree head `e8681d61713e20d81617ee160503d38556acf1f4` (verified). Session 20:59-21:13 PDT (14 of the 60 budgeted minutes). Each "old" block in §4 was checked by
script to occur exactly once, byte for byte, in the registration.

## 1. Contamination disclosure

**Injected before the charge, not chosen by me.** The harness placed three texts in my context
ahead of the charge: the owner's global `CLAUDE.md` (a writing standard and a pointer to
orchestration skills), this repository's `CLAUDE.md` (Codex bridge notes), and the memory index
`MEMORY.md` (about 120 one-line hooks, including owner directives such as "check the physics,
not the proxy", "paper threat = hallucination, not forgery", and the #416 triple-audit line). The
charge forbids reading these. I could not avoid the injected text; I opened none of the files and
no memory file behind any hook. No ruling below rests on them: where a hook overlaps the charge
(network time, threat model), I used the charge's own wording. I could not verify §9's statement
about directive #416 without reading memory, so it is marked unverified in §3.

**Read beyond the charge's list, and why.**

| What | Why |
|---|---|
| `git diff` of `50-seal-charge.md` (the charge itself, modified in the tree) | To see why the tree was dirty: placeholders (head, PR number, registration hash) filled in; nothing else |
| `joulewise/cli.py` `validate_bundle`, `_strict_problems`, `_strict_uncertainty_evidence_problems` | The strict validator §6 names; needed to see what "valid" means in code |
| `joulewise/uncertainty_evidence.py` (limits, refusal shapes; grep and two excerpts) | The clock admission §5(b) names |
| `joulewise/network_time_off.py` (whole file, 140 lines) | The OFF receipt recognizer §5(a) describes |
| `joulewise/reduce.py` beyond the two named sites (precheck assembly, unresolved-anchor branches) | To trace where the count comes from and what a clock refusal does to a member |
| `joulewise/bundle_read.py`, `joulewise/adapters/mlx_runtime.py`, `joulewise/controller.py` (greps and short excerpts) | Whether the warm-up run can contribute a prefill window; where clock status is written |
| `scripts/run_campaign.py` (`evaluate_member`, failure accounting, `claim_evidence_flags`) | Whether a short prefill or a clock refusal fails a member during the chain |
| `scripts/reserve_calibration_window_bracket.py`, `joulewise/night_gate.py` (greps) | Directory creation at reservation; the D-166 registration hash constant |
| `tests/test_harvest_g2a_window.py` (whole), excerpts of `tests/test_reduce.py`, `tests/test_run_campaign.py`, `tests/test_summarize_g2a_prefill_probe.py` | The charge asks me to execute the verdict logic on the fixtures; I had to see what the fixtures mock |
| `configs/campaign_policies/quiet_mac_p2_production.json`, `configs/calibration/calibration_ledger_head.json` | Policy keys; the committed pin §3 cites |
| The Revision 6 C2 ledger outside the worktree (`shasum` and a line count only) | To verify the path, sha256 and record count §3 registers |

**Listed files read only in part.** `02-refuter-opus.md`: headings, then lines 245-739 (Q4-Q7,
findings, amendments); lines 1-244 not read. `12-sol-g2a-readiness-scout.md`: lines 1-160 of 451.
`preregistration_d079_epoch_25g83_rev1.md`: lines 990-1029 (the network-time item). 
`docs/decision_log.md`: the D-166 row only. `scripts/run_night.py` (4400 lines),
`scripts/generate_g2a_probe_inputs.py` (1430) and `joulewise/calibration_bracketing.py` (2938):
the G2-a-relevant functions only, found by grep.

**Seen, not read.** During the session an untracked file `51r-seal-refuter.md` appeared in this
directory (the parallel refuter's output). I did not open it. I did not read `RUN_STATE.md`,
`TASK_QUEUE.md`, `AGENTS.md`, `CLAUDE.local.md` or any skill file. No subagent, no background
task, no git write, no capture, no model load.

## 2. Executed checks

Interpreter `/Users/edr/code/JouleWise/.venv/bin/python -B`, `TMPDIR=/tmp/cg-g2a-b2`. The tree was
unchanged afterwards apart from the charge file's pre-existing edit and the refuter's file.

| # | Command (abridged) | Result |
|---|---|---|
| 1 | `git rev-parse HEAD`; `shasum -a 256 registration_block2.md` | `e8681d61…`; `2188e0e6…a78d`, both as charged |
| 2 | `unittest tests.test_harvest_g2a_window tests.test_select_g2a_prefill_length tests.test_summarize_g2a_prefill_probe` | 43 tests, OK |
| 3 | `unittest tests.test_gen_g2_phase_d tests.test_gen_g2a_window tests.test_generate_g2a_probe_inputs` | 48 tests, OK |
| 4 | `scripts/gen_g2_phase_d.py --check` | `PASS generated Phase D matches pinned runbook bytes`, exit 0 |
| 5 | `gen_g2_phase_d.NIGHT_PROGRAMMED_SPAN_S`; `ceil((span+2700)/60)*60` | 17248; 19980. Both equal §4's literals |
| 6 | `joulewise.reduce.MIN_PHASE_SAMPLES` | 3 |
| 7 | `shasum` of the D-166 registration file and the acceptance file; `night_gate.D166_REGISTRATION_SHA256` | `dfe55f8d…c265` (file and constant agree); `f949f511…3660`. Both equal §2-§3 |
| 8 | `gen_g2_phase_d.py --emit-chain /tmp/cg-g2a-b2/emit/chain.zsh --night-date 20261004 --plan-id …`; `zsh -n` | Emitted, syntax OK. `PRE_CAL_FIDUCIAL_MAX_S=0.036462861644980` with the comment naming acceptance `…25g83_r2 (sha f949f511...)`; `NIGHT_PROGRAMMED_SPAN_S=17248`; `SETTLE_S=600`; stage order small 512-4096 then large 512-4096; `--arm-quiet-mode --max-failures 1`; summarizer last |
| 9 | `unittest tests.test_run_campaign.G2aLowCountCampaignTests` (real mock capture, real reducer, real strict validator, real campaign runner) | OK: a prefill with count < 3 is `succeeded`, strict-valid, labelled `not_resolvable_sample_count`, and does not spend the failure budget |
| 10 | Scratch scenario A on the lane's harvest fixture (`/tmp/cg-g2a-b2/cg_scenarios.py`): all five small-p512 members carry `uncertainty_evidence.clock_anchor.status = "unknown"` (reason `wall_minus_monotonic_span_exceeded`) | `verdict SELECT`, 24/24 valid, selected 512; `network-time.json` reports `within_capture.status = unknown` for the five. Finding F1 |
| 11 | Scenario B: chain's own summary present, one small member invalid at harvest | `REFUSED ['chain_summary_byte_mismatch']` (text says RECOVER). Finding F2 |
| 12 | Scenario C: chain's own summary present, one large member invalid at harvest | `REFUSED ['chain_summary_byte_mismatch']` (text says SELECT). Finding F2 |
| 13 | Scenario D: one large member invalid, no chain summary | `SELECT`, 23/24 valid. Large model does not gate the verdict: agrees with text |
| 14 | Scenario E: chain started, no bracket session, empty `runs/`, exit 1 | `RECOVER ['bracket_incomplete','chain_nonzero_or_missing_exit','rung_valid_small_members_shortfall']`; the record has no field saying whether a capture exists. Finding F7 |
| 15 | Scenario F: selector on a summary with a zero-member rung as the summarizer writes it (`small_minimum_count: 0`); and with 4 members at 512 | Selector refuses `summary_internally_contradictory` (it expects `null`); with 4 members the standalone selector selects 1024. Findings F10 and ruling 2 |
| 16 | Scenario G: one small-p512 member at count 3, 4, 5 through the harvest | selected 1024, 1024, 512. The floor is count ≥ 5, never 8 |
| 17 | `shasum` and line count of the registered C2 ledger; `calibration_ledger_head.json` | `3c9b6844…72fb`, 376 records; pin sequence 376. Equal §3 |

**NOT EXECUTED.** The whole test suite. Any live command (`--new-g2a-window`, `bind-window`,
`check`, the driver, the harvest on a real window). The real strict validator on a real bundle
with a refused clock (established by reading `reduce.py` 2420-2439 and 3488-3512 and by the
repository's own test `test_051_unresolved_anchor_is_a_claim_barrier_not_a_fallback`, which I
read and did not run by itself). The numeric drift rule inside `calibration_bracketing.py`. The
driver's in-window agent census. The content of the arm notice and courier mail.

## 3. Rulings

### 1. Fixed before data, and unambiguous?

Every rule is fixed before data: no measured value of this block appears in the file, the ladder,
floors, member counts, verdict classes and stop rules are literals, and the selection is code.
Four rules can be applied two ways as written. Each is cured by a text change in §4.

- **Member validity against the clock (§5(b), §6).** The text says a member refused by the
  within-capture clock admission is invalid. The harvest does not apply that: it reports the
  clock outcome and still counts the member (check 10). An operator who trusts the harvest
  verdict and one who reads `network-time.json` against §6 reach different verdicts. F1; T3, C1.
- **A member found invalid at harvest after a complete chain (§7, §8).** Text: RECOVER for a
  small member, no effect for a large one. Code: REFUSED either way, because the chain's own
  summary counted the member and the byte comparison fails (checks 11-12). REFUSED is defined as
  "never a science outcome", and re-running the harvest returns the same refusal. F2; T4, C2.
- **A sweep that is physically complete but whose chain exit is nonzero or missing (§7).** The
  SELECT bullet is satisfied (brackets pass, four rungs evaluable) and the RECOVER bullet also
  lists "a nonzero or missing chain exit". Code says RECOVER. The code also has a cause the text
  does not list (`network_time_off_not_admitted`). F5; T1, T2.
- **"Made no capture" (§7).** "No directory under `runs/instrument_validation/`" does not say
  whether an attempt directory created before a capture began counts, and the harvest does not
  compute the class. F7; T8.

REFUSED and NULL are otherwise unambiguous: NULL is exactly "`night/chain.started` absent"
(harvest line 115, fixture test passes), and every `HarvestRefusal` or unexpected exception is
REFUSED with exit 3.

### 2. D-166 as amended, carried faithfully?

Yes, nothing in D-166 is changed.

| D-166 element (index row, records 01-03) | Registration | Code at `e8681d61` |
|---|---|---|
| Ladder 512/1024/2048/4096, shortest that clears | §1, §8 | `LADDER`, `qualifying[0]` in the selector |
| Count ≥ 5 in every small member (count, not margin; never 8) | §1, §8 | `MIN_OVERLAPPING_POWER_INTERVAL_COUNT = 5`; check 16 |
| ≥ 5 small members per rung, else not selectable | §1, §6 | `MIN_SMALL_MEMBERS = 5` in summarizer and selector |
| Reducer floor 3, consistency check | §8 | selector refuses `reducer_floor_drift` unless live `MIN_PHASE_SAMPLES == 3` |
| Counts read from the production reducer, never recomputed | §1 | summarizer reads `window_evidence_precheck.phase.prefill.windows[0].in_window_sample_count`, which is `_in_window_sample_count`, the same function the reducer compares with `MIN_PHASE_SAMPLES` (`reduce.py` 975, 3006, 3843) |
| No rung clears: collect at 4096 | §1, §8 | `collection_prefill_tokens = 4096`, `fallback_action: collect_at_4096` |
| Two-way refusal wording (A2) | §1, §8 | `count_range "<3"` → `not_resolvable_sample_count`; `"3-4"` → "below the pre-registered count floor of 5", `disclose_reducer_resolvable_result: true` |
| Large model recorded, non-gating | §1, §8 | large rows never enter `qualifying`; check 13 |
| Selection record hash bound by the `_v5` pre-registration | §8 | selection record path and sha256 in the harvest record |

One addition, which I rule is not a change to D-166: §6-§7 require all four small rungs to have
five valid members before any selection. D-166 alone would let a window with four valid members
at 512 select 1024 (check 15, second line). The registration's stricter rule stops an accident of
validity from moving the selection to a longer rung, and it is what ratification A4 means by
making the four-rung sweep the selection's precondition.

### 3. Validity and stop rules

**Can a rule select a rung that did not truly qualify?** One path, and it is in the code, not
the text: a member whose within-capture clock admission was refused keeps `status: succeeded`
(the reducer treats an unresolved clock anchor as a claim barrier on energy and falls back to the
stored timeline), its count is taken from that unverified timeline, and the harvest counts it
(F1). With C1 in place I find no other path. The count is the reducer's own; the selector refuses
a self-contradictory summary; a rung with fewer than five valid members can never qualify.

**Can members be excluded in a way that depends on their counts?** No. Validity is `succeeded`
plus strict validation (plus, after C1, the clock status). A prefill with fewer than 3 records
stays `succeeded`, strict-valid and "ok" to the campaign runner (check 9, executed on the real
code path), so a low count neither invalidates the member nor stops the chain. The only
sample-count failure in the reducer is fewer than 2 records in the whole measured request window,
which a 512-token decode cannot produce. T3 words the clock test as a status field precisely so
that nobody implements it as "precheck eligible", which would be count-dependent
(`insufficient_in_window_samples`).

**Recovery rule.** Sound in design: RECOVER is defined without reference to any count, the
harvest prints no count and does not run the selector on a RECOVER window, so a second sweep
cannot be triggered by an unwelcome result; no pooling and no top-up keep each sweep's five
members a single draw; the first complete sweep decides; a second incomplete sweep goes to a
consult. Two defects in its execution:

- As written the recovery window cannot be armed without voiding the seal. Every harvest of a
  window whose chain opened a bracket session advances the ledger pin (harvest lines 211-222), so
  after the first window the committed pin is past sequence 376, the C2 clone that §3 names as the
  only restore source no longer matches it, and §3 says a mismatch refuses the arm and any change
  to §3 needs a new seal. The same applies to the arm head: a code-defect fix between the windows
  changes the pinned script hashes of §12. F3; T5, T6.
- A large-model stage that fails stops the chain before the post bracket (`set -e`,
  `--max-failures 1`, large stages precede the post bracket), so all twenty small members are
  lost with it. That does not contradict D-166 (the large model still never gates the selection
  rule), but it is a window lost to the model D-166 calls non-gating, and §1's "never gate" reads
  as if it could not happen. F4; T2 states it honestly, and offers the containment variant.

**Null-window rule.** Sound. A window whose chain never started made no capture and opened no
ledger session, so there is nothing to pool or to bias; treating a started chain that made no
capture the same way is right for the same reason. The "same refusal twice goes to a consult"
bound stops a re-arm loop. One cost, not a soundness defect: the harvest will not issue NULL
before `t0 + window_max_s + 300` (about 5.6 h after t0) even though the driver finished within
minutes (F9).

### 4. Network time

Yes: (a) the OFF state plus (b) the binding within-capture clock-movement admission is the right
physical test for this window, and the receipt-to-capture offset comparison is rightly
report-only.

The hazard the owner named is a clock correction landing inside a capture. This block's only
output is, per member, the number of power records whose time span overlaps the prefill phase.
Both sides of that overlap (phase markers and record stamps) live inside one capture, and the
only thing that can misplace one against the other is wall-clock movement relative to the
monotonic clock during that capture. That is exactly what (b) bounds (15 ms span backstop and
25 ppm sustained rate under the active method, `uncertainty_evidence.py` 71-80, 1090-1130; a fit
needs 60 s of baseline, which the 75 s idle supplies). A step between two captures moves both
sides of every later overlap together and changes no count. The same holds for the two bracket
quantities: each fiducial bound is computed inside its own capture, and the drift is the
difference of two such bounds.

If the offset comparison were binding it would protect no number of this block. The only
cross-capture facts the block uses are orderings (members enclosed by the brackets, acceptance
freshness), which are separated by 600 s settles and by hours; a 15 ms flag threshold is five
orders of magnitude below anything that could reorder them. Voiding on it would only add a way
to lose a window. Keeping it as a report is right: a flag is evidence that OFF did not hold and
belongs with the orchestrator.

Two conditions on that answer. First, (b) must actually bind members in code (F1, C1); today it
binds only the bracket captures (through the calibration validator) and is a report for members.
Second, §5(a) matches the driver as built: one write-once receipt from the setter at t0, exit 0,
either OFF wording under E-NT1's normalization, same boot, at least 600 s on both clocks before
the chain starts (`network_time_off.py` `admit`, `seconds_since_receipt`; `run_night.py`
2994-3015). No exact-stdout comparison survives anywhere in that path.

### 5. Code against text at `e8681d61`

Agreements (executed unless marked): span literal 17,248 and `window_max_s` 19,980; screen
literal derived from the acceptance in force and `--check` passing; chain shape of §4 (settle,
pre bracket, screen, eight stages in the registered order, post bracket, terminal boundary,
summarizer); the selector's rule, floor check and fallback record; NULL, RECOVER and SELECT on the
lane's fixtures; count below 3 is valid; stdout carries no measured value; the D-166 registration
and acceptance hashes; the ledger source hash and record count.

Mismatches:

| | Text | Code | Which side changes |
|---|---|---|---|
| F1 | §5(b), §6: a clock-refused member is invalid | harvest: valid if `succeeded` and strict-valid; clock outcome only reported | **Code** (C1). The text is the physically right rule; T3 makes it mechanical |
| F2 | §7: invalid small member → RECOVER; large → no effect | REFUSED `chain_summary_byte_mismatch` whenever the chain wrote its summary | **Both**: T4 states the input rule exactly; C2 makes the harvest follow it |
| F5 | §7 SELECT does not mention chain exit or the OFF receipt | RECOVER on nonzero or missing exit and on an unadmitted receipt | **Text** (T1, T2). The code's reading is the conservative one and needs no change |
| F8 | §4: `window_max_s` = span + 2700 rounded up (19,980) | `author_g2a_window` accepts any value ≥ span + 900 | **Neither must**: the arm record must show `--window-max-s 19980`; a one-line equality check in the author command is recommended |
| F10 | — | summarizer writes `small_minimum_count: 0` for a rung with fewer than 5 members; the selector expects `null` when there are 0 members and refuses | **Code**, low priority: unreachable through the harvest (the selector runs only on SELECT) |

### 6. Pruned without reason, or missing a protection?

Nothing the registration drops protected a number of this block: the exact-stdout match (E-NT1),
the Revision 6 start manifest (it asserts facts about a prior Revision 6 session that a G2-a
window does not have), the binding offset comparison (ruling 4), the September overnight
cutoffs, and the #416 triple audit (the registration says the amended directive applies before
claim-bearing runs; I could not verify the directive's wording without reading memory, so that
sentence is **unverified by this gate**; the claim boundary in §9 is what makes the block
diagnostic, and that I do confirm).

Missing protections, all cured by the changes below: the clock rule not enforced for members
(F1); no stated head for the harvest and selector (T6); no route for the recovery window's ledger
and head (F3).

One piece of machinery that protects no number and costs hours: the harvest's completion-boundary
wait applied to a window whose chain never started (F9). Recommended, not required.

Nothing else in the block is ritual. The pre-calibration screen, the brackets, the input
inventory check and the byte-for-byte regeneration each stop a specific false count or a wasted
sweep.

### 7. Claim boundary (§9) and blindness (§10)

§9 is right and complete: one licence (the `_v5` prefill length or the 4096 fallback), no energy,
floor, comparison, dominance, difficulty or phase-attribution statement, bundles never promoted,
bracket captures governed by the acceptance's own rules, no authority over G2-b or the `_v5`
transaction.

§10's mechanism is right and holds in code: the harvest prints the verdict, a valid-member tally,
paths and hashes (fixture test and check 2), never a count; the selector does not run on a
RECOVER window. One sentence overreaches: "no person or agent reads a measured value to decide
anything in this block" cannot be kept alongside §7's "armed only after the cause is named",
because naming a pre-screen stop or a bracket failure means reading a fiducial bound or a drift.
The value that must stay unread is the overlap count, the selection variable. T7 says that. F6.

## 4. Required text changes (apply verbatim before the seal record is written)

Line breaks in the "old" blocks are the file's own.

**T1 (§7, SELECT bullet).**

Old:
```
- **SELECT**: both brackets pass and all four small-model rungs are evaluable. The window is
  *complete*; the analysis plan (§8) runs on it. The block ends.
```
New:
```
- **SELECT**: the chain exited 0, the OFF receipt of §5(a) is admitted by the harvest, both
  brackets pass and all four small-model rungs are evaluable. The window is *complete*; the
  analysis plan (§8) runs on it. The block ends.
```

**T2 (§7, RECOVER bullet).** Apply exactly one variant: T2a if the chain at H is the one at
`e8681d61` (a large-stage failure stops it); T2b only if the lane changes the chain so that a
failed large-model stage is logged and the post bracket still runs.

Old:
```
- **RECOVER**: the chain started and the window is not complete (a pre-screen stop, a bracket
  failure, any small-model rung with fewer than 5 valid members, a nonzero or missing chain exit).
  The harvest names the cause codes.
```
New (T2a):
```
- **RECOVER**: the chain started and the window is not complete (a pre-screen stop, a bracket
  failure, any small-model rung with fewer than 5 valid members, a nonzero or missing chain exit,
  an OFF receipt the harvest does not admit). A large-model stage that fails stops the chain
  before the post bracket, so it also ends RECOVER: the large model never gates the selection
  rule of §8, but its four stages are part of the one chain. The harvest names the cause codes.
```
New (T2b):
```
- **RECOVER**: the chain started and the window is not complete (a pre-screen stop, a bracket
  failure, any small-model rung with fewer than 5 valid members, a nonzero or missing chain exit,
  an OFF receipt the harvest does not admit). A large-model stage that fails does not stop the
  chain: the chain logs the failure, runs the remaining stages and the post bracket, and exits 0;
  the window is then judged on its brackets and its small-model rungs alone. The harvest names
  the cause codes.
```

**T3 (§6, Member bullet).**

Old:
```
- **Member.** A member is valid when its bundle passes strict validation from its raw evidence
  (`joulewise/cli.py` strict validator, re-reducing raw artifacts), every capture-level admission
  passes (including §5(b)'s binding part), and it is enclosed by the window's pre and post
  brackets. A member whose prefill phase overlaps fewer than 3 records is VALID: its reducer
  outcome `not_resolvable_sample_count` is a result, and its count is recorded. Validity never
  depends on the member's count or on any energy.
```
New:
```
- **Member.** A member is valid when all of these hold: its `summary_metrics.json` status is
  `succeeded`; its bundle passes strict validation from its raw evidence (`joulewise/cli.py`
  strict validator, re-reducing raw artifacts); and §5(b)'s binding part passes, read as
  `uncertainty_evidence.clock_anchor.status` equal to `bounded` in the member's `metadata.json`
  (any other status, or no such record, makes the member invalid). Enclosure by the window's pre
  and post brackets is judged once for the window, over its valid members: a failure makes the
  window RECOVER (§7), it does not make one member invalid. A member whose prefill phase overlaps
  fewer than 3 records is VALID: its reducer outcome `not_resolvable_sample_count` is a result,
  and its count is recorded. Validity never depends on the member's count or on any energy; in
  particular the reducer's per-phase eligibility flag, which a low count turns off, is not a
  validity test.
```

**T4 (§8, Input bullet).**

Old:
```
- **Input.** Only the authenticated four-row summary and counts receipt of the SELECT window, as
  regenerated byte-identically by the harvest from raw bundles.
```
New:
```
- **Input.** Only the four-row summary and counts receipt that the harvest regenerates from the
  SELECT window's raw bundles, counting valid members only (§6). The copy of those two files that
  the chain wrote is a check, not an input. When every roster member is valid, the regenerated
  bytes must equal the chain's copy; a difference is REFUSED (a tooling fault). When the harvest
  found a member invalid, the two differ by construction; the harvest records the difference and
  the verdict follows §7 from the regenerated summary (RECOVER if a small-model rung is left with
  fewer than 5 valid members, otherwise unaffected).
```

**T5 (§3, Ledger bullet).**

Old:
```
- **Ledger.** The measurement clone's calibration observation ledger is restored byte-exact from
  the retained Revision 6 C2 clone
  (`/Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/runs/calibration_observation_ledger.jsonl`,
  file sha256 `3c9b6844e22958a6ba0eaee28cfab63642f3d0310f15b9bbc9e82363a2d772fb`, 376 records),
  whose head equals the committed pin `configs/calibration/calibration_ledger_head.json` at H
  (sequence 376 unless a later merged harvest advanced it; the arm recipe re-reads it). A ledger
  that fails custody audit or does not match the pin refuses the arm.
```
New:
```
- **Ledger.** The measurement clone's calibration observation ledger is restored byte-exact from
  the retained ledger whose head equals the committed pin
  `configs/calibration/calibration_ledger_head.json` at the arm head. At the seal that is the
  Revision 6 C2 clone
  (`/Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/runs/calibration_observation_ledger.jsonl`,
  file sha256 `3c9b6844e22958a6ba0eaee28cfab63642f3d0310f15b9bbc9e82363a2d772fb`, 376 records,
  pin sequence 376). Every harvest of a window whose chain opened a bracket session advances the
  pin. Once such an advance is merged (this is always the case for a recovery window), the source
  is that harvest's archived `derived/terminal-ledger.jsonl`, whose head equals the merged pin;
  the arm record names the source path and its sha256. Using the source this rule names is not a
  change to this section. A ledger that fails custody audit or does not match the pin refuses the
  arm.
```

**T6 (§12, append after the existing paragraph; the existing paragraph is unchanged).**

Old (last line of the file):
```
`configs/model_panels/qwen3_4bit.json`, the D-166 registration file and the acceptance file.
```
New:
```
`configs/model_panels/qwen3_4bit.json`, the D-166 registration file and the acceptance file.

H must contain a harvest that applies §6's member rule as written (a member whose clock anchor
status is not `bounded` is invalid) and §8's input rule (a member found invalid at harvest gives
the §7 verdict, never REFUSED for a summary byte difference); the seal record cites the tests
that show both. The harvest and the selector are run from a checkout whose pinned files match
the seal record. A recovery window is armed from a head H′ that differs from H only by the
merged pin advance of the first window's harvest and by gated fixes that make code agree with
this text (§11); the seal record is extended with the H′ pins and no new seal is needed. Any
other difference needs a new seal.
```

**T7 (§10).**

Old:
```
in the archived files. The verdict and the selection are computed by code from fixed rules; no
person or agent reads a measured value to decide anything in this block. The selected rung is the
one result this block exists to produce and is recorded as a parameter.
```
New:
```
in the archived files. The verdict and the selection are computed by code from fixed rules. No
person or agent reads a per-member overlap count, or a row of any window's summary, before the
block ends (a SELECT, or the consult of §7). Naming the cause of a RECOVER, as §7 requires, may
read that window's bracket and admission evidence (fiducial bound, drift, clock outcome, logs);
it never reads an overlap count. The selected rung is the one result this block exists to
produce and is recorded as a parameter.
```

**T8 (§7, the no-capture sentence).**

Old:
```
A RECOVER window whose chain made no capture (no directory under the probe root's
`runs/instrument_validation/` and no member directory under `runs/`) took no data; for the
allowance below it counts like a null window. After any other **RECOVER**, at most one recovery
```
New:
```
A RECOVER window whose chain made no capture (in the harvest's archive copy of the probe root,
no file named `powermetrics*.plist` in any `raw/` directory under `runs/`) took no data; for the
allowance below it counts like a null window. After any other **RECOVER**, at most one recovery
```

## 5. Code conditions on H (ordinary gated pull request; no new cold gate)

- **C1 (cures F1).** `scripts/harvest_g2a_window.py` treats a roster member as invalid unless its
  `metadata.json` has `uncertainty_evidence.clock_anchor.status == "bounded"`. Test to cite in
  the seal record: on the lane's fixture, five small-p512 members with a non-`bounded` status give
  `valid: false` for each and `RECOVER` with `rung_valid_small_members_shortfall`; one large
  member with a non-`bounded` status leaves the verdict `SELECT`; a member with count 2 and a
  `bounded` status stays valid (so the test proves the rule is not count-dependent). Note for
  the implementer: the mock-telemetry bundle of `G2aLowCountCampaignTests` has no anchor context,
  so that test does not exercise this field; the fixture must set it.
- **C2 (cures F2).** The harvest's comparison with the chain's own summary and counts receipt
  follows T4: byte equality is required only when every roster member is valid; otherwise the
  difference is recorded and the verdict comes from the regenerated summary. Test to cite: my
  scenarios B and C (`/tmp/cg-g2a-b2/cg_scenarios.py`, reproduced in the lane's test file) give
  `RECOVER` and `SELECT` respectively, not `REFUSED`. C2 is needed for C1 to work: after C1, a
  clock-refused member in a chain that exited 0 is exactly the case where the chain's summary
  counted a member the harvest rejects.

Recommended, not conditions: record in `harvest.json` whether any capture file exists (the T8
test), so the allowance class is in the record (F7); refuse a `--window-max-s` other than the
registered formula's value in `--new-g2a-window` (F8); let the harvest issue NULL as soon as
`courier.sent` exists and `chain.started` is absent (F9); make the summarizer write `null` for a
zero-member rung and refuse a prefill precheck whose `window_count` is not 1 (F10, F11).

## 6. Findings

| # | Severity | Location | Claim | Evidence |
|---|---|---|---|---|
| F1 | major | Registration §5(b), §6; `scripts/harvest_g2a_window.py` 139-146, 187-189 | The harvest counts a member whose within-capture clock admission was refused. Its count comes from the stored, unverified timeline, so a rung can qualify on a count the registration calls invalid. Code should change (C1); T3 makes the text mechanical | Check 10: five members with `clock_anchor.status = "unknown"` → `SELECT`, 24/24 valid, 512 selected, while `network-time.json` reports the refusals. `reduce.py` 2420-2439: an unresolved anchor only adds `clock_anchor_unresolved` to gate reasons; 3488-3512: the stored curve is kept. `tests/test_reduce.py` 2764-2791: such a bundle is `SUCCEEDED` and "falls back to the stored timeline value". Not executed on a real refused bundle through the strict validator |
| F2 | major | Registration §7, §8 "regenerated byte-identically"; harvest 170-172 | After a chain that completed and wrote its summary, a member the harvest finds invalid gives REFUSED, not RECOVER (small) or no effect (large). REFUSED cannot be cured by re-running. Becomes the normal path for a clock-refused member once C1 lands | Checks 11-12: `REFUSED ['chain_summary_byte_mismatch']` in both. Check 13 shows the intended behaviour when no chain summary exists. Chain tail (emitted chain, last 12 lines) always writes the summary without a validity filter |
| F3 | major | Registration §3 Ledger, §12 | The recovery window cannot be armed under the text: the first window's harvest advances the pin past 376, the only registered restore source (C2 clone, 376 records) then mismatches, and §3 says a mismatch refuses the arm and a change to §3 needs a new seal. Same for a code fix between windows against §12's pinned hashes | Harvest 211-222 (`terminal-pin`, `advance-head-pin --execute`, `needs_operator_commit`); fixture test `…advances_via_governed_procedure`; check 17 (source is at 376 now). T5, T6 |
| F4 | major (window waste, not a wrong number) | Registration §1 "never gate", §4 item 3; emitted chain `for role in small large` under `set -euo pipefail` | A failed large-model stage stops the chain before the post bracket and costs the whole sweep, including twenty valid small members. Does not contradict D-166 (selection rule untouched) but the text hides it. T2a states it; T2b plus a chain change contains it. Seat's choice before the seal record | Check 8: stage loop, `--max-failures 1`, post bracket after the loop. Sol consult (record 11) made the same containment point about a rider stage |
| F5 | minor | Registration §7 SELECT and RECOVER bullets; harvest 190-203 | The two bullets overlap for a physically complete sweep with a nonzero or missing chain exit; the code's cause `network_time_off_not_admitted` is not in the text. Text changes (T1, T2); code stays | Harvest 195-199; fixture test `test_missing_or_unadmitted_OFF_receipt_recovers` |
| F6 | minor | Registration §10 | "No person or agent reads a measured value to decide anything" contradicts §7's cause-naming. The protected value is the overlap count. T7 | §7 "armed only after the cause is named"; chain logs `pre_calibration_fiducial_s` for exactly that diagnosis |
| F7 | minor | Registration §7 no-capture sentence; harvest record | The "made no capture" class is defined by directories that can exist without a capture, and the harvest does not record it. T8; recording it is recommended | Check 14: record keys carry no capture field. `calibrate_slot` passes `--output-root runs/instrument_validation`; the generated region creates that directory at chain start |
| F8 | minor | Registration §4 `window_max_s`; `gen_g2_phase_d.py` 322-323 | The registered value is a formula; the author command accepts any value ≥ span + 900. Arm record must show 19,980 | Check 5; code read |
| F9 | minor | Harvest 94-95 before 115-121 | NULL cannot be issued until `t0 + window_max_s + 300` although nothing ran. Hours idle on a dedicated machine, no number at stake. Recommended code change | Code read; fixture `now` is set to the boundary in every test |
| F10 | nit | `summarize_g2a_prefill_probe.py` 519-523; `select_g2a_prefill_length.py` 79-83 | Zero-member rung written as `small_minimum_count: 0`, selector expects `null` and refuses. Unreachable through the harvest | Check 15 |
| F11 | nit | `summarize_g2a_prefill_probe.py` 288-295 | Reads `windows[0]` without asserting exactly one prefill window. Safe today (configs fix `repetitions: 1`; the warm-up emits no phase markers, `mlx_runtime.py` 351-375) | Code read |
| F12 | nit | Registration §1 worked example | "A prefill lasting 0.45 s overlaps at least 5 records" is true only if records are exactly 100 ms long; the 2026-08-30 cold ruling records real record lengths of about 112-129 ms, at which 0.45 s can overlap 4. No rule depends on the example, since the count is measured. Suggested, optional: insert "with records exactly 100 ms long" after "0.45 s" | `01-COLD-RULING.md` Q1 item 3 |
| F13 | nit | Registration §7 "the same refusal signature" | Not defined. Suggested, optional: "the same refusal reason code in the driver's result record" | Text read |

No blocker. Nothing found contradicts D-166.

## 7. Plain summary

The registration's rules are fixed before data, carry D-166 unchanged, and its network-time test (OFF state plus a binding within-capture clock check, offset comparison report-only) is the right physical test for a count taken inside one capture.
ADMIT, with eight exact text replacements (the main ones: say mechanically what a valid member is, say which summary is the selection input, and give the recovery window a ledger source and arm head it can actually use) and two harvest fixes at H, because today the harvest counts a clock-refused member and returns REFUSED where the text says RECOVER.
A low prefill count never invalidates a member or stops the chain (run on the real code path), the count floor is 5 and the reducer floor 3 in code, the span literal is 17,248 s and the screen literal matches the acceptance in force.
