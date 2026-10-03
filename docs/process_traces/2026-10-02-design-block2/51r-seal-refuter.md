REFUTER G2A-25G83-B2: AGREE

# Refuter record, cold registration gate G2A-25G83-B2 (Opus 5.5)

## Phase 1: independent findings

Provisional first line (the form the charge prescribes for the judge):

`SEAL: ADMIT` (conditional: the arm head H must carry the two harvest code fixes R-1 and R-2
below, each with a test, before the seal record is written; the registration text is right on both
and should not change)

Written before reading any judge output. `51-seal-ruling.md` did not exist when this section was
written.

### Contamination disclosure

- Read everything the charge lists: the registration (sha256 verified `2188e0e6…a78d`), the D-166
  index row, the 2026-08-30 records 01 and 03 in full and 02 by heading/keyword skim, design record
  00, Sol consult 11, readiness scout 12 (first ~150 lines: verification table and summary), erratum
  E-NT1 42, Revision 6 §5 "Network time", and the named code.
- Read beyond the list, for verification only: `joulewise/cli.py` (`validate_bundle`,
  `_strict_problems`, `_strict_uncertainty_evidence_problems`, `_powermetrics_trace_endpoint_s`),
  `joulewise/window_duration_margins.py` (how D-166's named `overlapping_power_interval_count` is
  derived), `joulewise/network_time_off.py` (`admit`, `off_stdout_admitted`),
  `joulewise/controller.py:2170-2190`, `joulewise/night_gate.py` (D-166 pin lines), grep hits in
  `joulewise/uncertainty_evidence.py`, the tests `tests/test_harvest_g2a_window.py` (setup and
  verdict tests), and the retained ledger file's sha256 and line count. Reason: the charge asks
  whether code implements the text; these are the functions the named code calls.
- The working tree carries one uncommitted edit to `50-seal-charge.md` (placeholders HEAD_SHA,
  PR_NUMBER, REG_SHA filled in); I read the filled-in version. I saw the file name
  `50r-seal-refuter-charge.md` in a directory listing and did not open it (my prompt is the
  refuter charge). I read no RUN_STATE, TASK_QUEUE, CLAUDE*, AGENTS, memory or skill file; my
  session context did auto-load the user's global and project CLAUDE.md and a memory index, which I
  did not use for any finding.
- No sudo, launchctl, systemsetup, powermetrics, model load, capture, git write/fetch/checkout.
  Scratch writes only under `/tmp/cg-g2a-b2-refuter/`.

### Executed checks

| # | Command (cwd = worktree unless noted) | Result |
|---|---|---|
| C1 | `git rev-parse HEAD`; `shasum -a 256` registration | `e8681d61…`; `2188e0e6…a78d` (matches charge) |
| C2 | `shasum -a 256` D-166 registration JSON, acceptance JSON; grep `D166_REGISTRATION_SHA256` in `night_gate.py` | `dfe55f8d…c265`, `f949f511…3660`; both match §2/§3 and the night-gate pin |
| C3 | `cat configs/calibration/calibration_ledger_head.json`; sha256 + `wc -l` of the retained C2 ledger | sequence 376, digest `a5b825b7…7014`; ledger `3c9b6844…72fb`, 376 lines (matches §3) |
| C4 | `pytest -q` on the seven G2-a test files (harvest, selector, summarizer, gen window, gen phase D, probe inputs, prompt pin) | 102 passed, 52 subtests passed |
| C5 | `gen_g2_phase_d.py --check` | `PASS generated Phase D matches pinned runbook bytes`, exit 0 (the check runs `authenticated_screen_source` on runbook and runsheet, so it fails on acceptance-derived screen drift) |
| C6 | `gen_g2_phase_d.py --emit-chain /tmp/…/chain.zsh --night-date 20261004`; read the chain | `PRE_CAL_FIDUCIAL_MAX_S=0.036462861644980` (acceptance `…_r2`, sha `f949f511`); stage loop `small` then `large` × 512/1024/2048/4096; each stage `run_campaign.py … --arm-quiet-mode --max-failures 1`; post bracket after all stages; summarizer then `jq -e … all(.small_members >= 5)` |
| C7 | import `gen_g2_phase_d`, print `NIGHT_PROGRAMMED_SPAN_S` and `ceil((span+2700)/60)*60` | 17248 and 19980 (match §4) |
| C8 | selector run (with `PYTHONPATH`) on four synthetic four-row summaries | FFTT → 2048; FFFF → refused, collect 4096, `no_g2a_prefill_rung_qualifies`; TTTT → 512; FTFT → 1024 (shortest qualifying, non-monotone case correct) |
| C9 | `off_stdout_admitted` on nine strings | admits both E-NT1 statements under whitespace/case/period normalization and a wrapped statement; refuses getter form, ON, empty, admin text, OFF-then-ON (matches §5(a) and E-NT1) |
| C10 | Scratch test P1 (harness of `tests/test_harvest_g2a_window.py`): chain writes its summary over all members (as the emitted chain does), then one small member fails strict validation | harvest verdict **REFUSED** `['chain_summary_byte_mismatch']` (registration requires RECOVER) |
| C11 | Scratch test P2: one small member's `uncertainty_evidence.clock_anchor` = `{status: unresolved, reason: wall_minus_monotonic_span_exceeded}`, strict validation returning no problem (what the real validator does, see R-2) | harvest verdict **SELECT**, member `valid: True`; the network report records the refusal but nothing acts on it |
| C12 | Read `reduce._in_window_sample_count` vs `window_duration_margins` | the summarizer's `in_window_sample_count` is computed by the same function D-166's `overlapping_power_interval_count` uses (support-interval overlap) |
| — | Live arm path, installer, driver admission, `run_night.py` beyond the span/deadline lines | NOT EXECUTED (read only at the cited lines) |

### Rulings 1-7

1. **Unambiguity.** The verdict rules are mechanical and two operators would agree, except where
   the code applies them differently from the text (R-1: a strict-invalid member after a clean
   chain exit becomes REFUSED, and a harvest re-run reproduces the same refusal, so REFUSED's
   "fix and re-run" route has no defined exit). Smaller ambiguities: "a RECOVER window whose chain
   made no capture counts like a null window" is not computed by the harvest (it is decidable
   from the archived tree, so acceptable), and whether the null-window "same refusal signature
   twice" rule also applies to those no-capture RECOVERs is unstated (minor).
2. **D-166 fidelity.** Faithful: ladder 512/1024/2048/4096, count ≥ 5 (stated as a count),
   ≥ 5 small members per rung, reducer floor 3 checked live, 4096 fallback, two-way refusal,
   large model non-gating, selection-record hash bound. Requiring all four rungs evaluable for
   SELECT is ratification A4's precondition ("G2-a sweep (≥5 members/rung) made the selection's
   precondition"), not a change. One text overreach: §8 says the selector prints the two-way
   wording "per member class"; the selector only carries the wording template (R-4).
3. **Validity and stop rules.** Validity is independent of the prefill count in code: the strict
   validator and the reducer fail a bundle only on the whole measured window (< 2 records), never
   on the prefill count, and a count < 3 member stays `succeeded` (C4 fixture test plus code
   read). The selected rung cannot be one that did not qualify (C8). Recovery and null rules are
   sound. Waste risk the text accepts silently: a large-model member failure (`--max-failures 1`,
   `set -e`) stops the chain before the post bracket and makes the window RECOVER, so the
   non-gating model can cost the sweep (R-3).
4. **Network time.** (a)+(b) is the right physical test: the count depends only on the alignment
   of the phase markers with the power records inside one capture, which the within-capture
   wall-minus-monotonic admission protects; a step between captures changes no count, so the
   receipt-to-capture comparison protects no number and is correctly report-only. But the binding
   part (b) is not implemented for members (R-2).
5. **Code vs text.** Selector, span literal, screen derivation, OFF recognizer, ledger pin and
   hashes agree. Two harvest mismatches, code side should change: R-1, R-2. Two minor: `--new-g2a-window`
   accepts any `window_max_s ≥ span + 900` rather than the registered 19,980 s, and any plan id
   rather than the registered form (R-5).
6. **Pruning.** Nothing number-protecting is missing from the text; the missing protection is in
   code (R-2). No pruned item needs restoring.
7. **Claim boundary and blindness.** Sound. Harvest stdout is custody-only (test asserts no
   energy/fiducial/drift/count text); measured values stay in archived files.

### Findings

**R-1 (major; `scripts/harvest_g2a_window.py:170-172` vs registration §6-§7).** Claim: if the
chain exits 0 but harvest-time strict validation refuses any member, the harvest returns
REFUSED (`chain_summary_byte_mismatch`) instead of RECOVER. Evidence: the emitted chain runs
`summarize_g2a_prefill_probe.py` without a validity filter and writes into `window-plan/`; the
harvest regenerates with `valid_run_ids` and refuses on byte difference (C10). Deterministic, so
a re-run cannot cure it. Consequence: no wrong selection, but a window that the text calls
RECOVER sits in the tooling-fault route with no defined exit. Fix (code): compare the chain's
bytes against a regeneration over the chain's own member set (no filter), and derive the verdict
from the filtered regeneration; add C10 as a test.

**R-2 (major, a selection-protecting gap; `scripts/harvest_g2a_window.py:139-146` vs
registration §5(b), §6).** Claim: §5(b) makes the within-capture clock-movement admission binding
("a capture refused by it, or with an empty clock fit, is invalid"); the harvest's member
validity is only strict validation plus `status == succeeded`, and neither enforces it. Evidence:
the reducer turns an unresolved anchor into a `clock_anchor_unresolved` precheck barrier while
keeping `status=SUCCEEDED` (`reduce.py` `_unresolved_anchor_context`, `:2420`); strict validation
replays the fallback endpoint and adds no problem ("the claim barrier stays in the precheck, never
here", `cli.py:1546-1552`, `:1299-1316`); the summarizer reads only `in_window_sample_count`. C11:
such a member is counted and the window SELECTs. Physical consequence: that member's phase window
is placed on the power records through a structural fallback rather than a bounded anchor, so its
overlap count is not protected, and it enters the "every member ≥ 5" test. Fix (code): a member
is invalid when its recorded `uncertainty_evidence.clock_anchor.status != "bounded"` (the same
field the network report already reads), with a test; confirm the bracket decision refuses an
unresolved-anchor slot (I did not trace that path: NOT EXECUTED).

**R-3 (minor, waste; registration §4 item 3, §7).** The large (non-gating) stages run under
`--max-failures 1` before the post bracket, so one large-model failure stops the chain and makes
the window RECOVER. Text and code agree, so no rule is broken; the cost should be stated so no
one reads "non-gating" as "cannot cost the window". Text: after "Qwen3-8B probes are recorded and
never gate" in §1 add "(a large-model member failure still stops the chain before the post
bracket, which makes the window RECOVER under §7)".

**R-4 (minor; §8 Computation).** Old: "with the D-166 two-way refusal wording printed per member
class (count < 3, count 3-4)". New: "and the selection record carries the D-166 two-way refusal
wording (count < 3: the reducer's refusal; count 3-4: below the pre-registered count floor of 5)
for the `_v5` prefill arm's printed result". Reason: the selector prints no per-member class, and
D-166's wording governs the `_v5` arm's result, not the probe.

**R-5 (minor; §2, §4 vs `gen_g2_phase_d.py:303-323`).** The authoring command accepts any
`window_max_s ≥ span + 900` and any plan id. A smaller value leaves less than the clean dwell's
2,700 s cap before the latest chain start, risking a NULL window. Either the arm recipe pins
`--window-max-s 19980` and the plan-id form, or the authoring code derives them.

**R-6 (nit; `summarize_g2a_prefill_probe.py` row builder).** A rung with 1-4 valid small members
reports `small_minimum_count` 0, and a rung with 0 reports 0 where the selector requires `null`
(selector would refuse the summary as contradictory). Unreachable on SELECT (harvest returns
RECOVER first); worth aligning.

**R-7 (nit).** `select_g2a_prefill_length.py` run as a script needs `PYTHONPATH` set to the repo
(C8 first attempt: `ModuleNotFoundError: joulewise`); the harvest calls it in-process, so no
effect on the verdict.

## Phase 2: on the ruling

Read `51-seal-ruling.md` (38,720 bytes, first line `SEAL: ADMIT`, stable over 60 s) after Phase 1
was written. Phase 2 extra reads: `RAW_SAMPLES_NAME` in the adapters; the reservation and
`mkdir` lines of my emitted chain; a read-only tally of `uncertainty_evidence.clock_anchor`
(method, status) in retained `metadata.json` files under `~/code/JouleWise/runs`,
`~/night-custody` and `~/night-archive` (anchor fields only; no energy, count or fiducial read).

### Agreement with my Phase 1

The judge found both harvest defects independently and executed them the same way: F1 = my R-2
(clock-refused member counted; its scenario A reproduces my C11), F2 = my R-1 (REFUSED instead of
RECOVER; its scenarios B and C reproduce my C10 and extend it to a large member). F4 = R-3, F8 =
R-5, F10 = R-6. Its facts that I checked independently match: span 17,248 s, `window_max_s`
19,980 s, screen literal `0.036462861644980` from acceptance `…_r2`, the D-166 and acceptance
hashes, ledger 376 records with sha `3c9b6844…`, count floor 5, reducer floor 3, the
selector's fallback record, and its account of network time (ruling 4). Its F3 (the recovery
window cannot be armed under §3/§12 as written, because the first harvest advances the pin past
the only registered ledger source) is a real defect that I missed; I confirmed the mechanism
(harvest lines 211-222 advance the pin whenever a session exists, and the chain executes the
reservation, which opens the session, before its first capture).

### Attempts to break the ruling

**D1 (minor-to-major for time, not for numbers): T6 grants the new head H′ only to "a recovery
window"; every other later window of the block falls under "Any other difference needs a new
seal".** Two cases the text then sends to a new cold seal:
- A RECOVER that made no capture. The chain runs the reservation (chain lines 98-111, 256) before
  `g2a_chain_start` and the pre slot, so the session exists, the harvest aborts it and advances
  the pin. §7 says this window "counts like a null window" and is re-armed; T5 gives its re-arm a
  ledger source, but T6 gives it no head, and its head must differ from H by the pin advance.
- A NULL window whose cause was a code defect: its fix changes a §12-pinned script.
Neither selects a wrong rung or spends a window, but each forces a new cold gate for a re-arm
that §7 already licenses. Exact text for T6's third sentence:
old: "A recovery window is armed from a head H′ that differs from H only by the
merged pin advance of the first window's harvest and by gated fixes that make code agree with
this text (§11);"
new: "Any later window of this block (a recovery window, or the re-arm of a null window or of a
RECOVER window that made no capture) is armed from a head H′ that differs from H only by the
merged pin advances of this block's earlier harvests and by gated fixes that make code agree
with this text (§11);"

**D2 (minor, a pre-arm check, not a defect in the ruling): C1 has not been shown achievable on a
real member.** C1 makes a member valid only if its stored anchor status is `bounded`. If the
member capture path at H routinely produced `unknown`, every small rung would fall short and
every window would be RECOVER (a window spent by rule). I looked for evidence: 271 retained real
bundles under the older envelope method are `bounded` and 2 fixture bundles under the
native-intersection method are `bounded`; I found no real member bundle under the method the
members will use at H, and none with a non-`bounded` status. The ruling does not create this
risk (§5(b) already makes the admission binding and the text was always going to need it), and
the bracket captures that passed in block 1 used the same instrument. But the seal record should
cite one desk or smoke member bundle produced at H whose stored anchor is `bounded`, so the
first window does not discover this.

**D3 (nit): T4 drops the chain-copy check whenever any member is invalid.** Equality is then
not checked at all. A stronger form keeps it in every case: compare the chain's copy with a
harvest regeneration over the chain's own member set (no validity filter), and take the verdict
and the selection input from the filtered regeneration. Not required: the selection input is
regenerated from raw either way, so no number depends on the chain's copy.

**D4 (nit): T2b would need a summarizer change as well as a chain change.** A failed large
member's `summary_metrics.json` has no `window_evidence_precheck`, so the chain's unfiltered
summarizer raises `summary_prefill_count_missing`, and under `set -e` the chain exits nonzero
anyway (read of `_prefill_count` and the member loop; NOT EXECUTED). T2a, the variant for the
chain as built, is correct.

**D5 (nit): T1's "the OFF receipt of §5(a) is admitted by the harvest".** The harvest's
`network_time_off.admit` checks exit status, wording and identity fields, not the 600 s or the
same boot; the driver checks those before the chain starts. Clear enough in practice, since a
chain that started passed the driver's check.

**D6 (minor, carried from my R-4, not addressed by the ruling).** §8 still says the two-way
refusal wording is "printed per member class"; the selector only carries the wording template,
and D-166's wording governs the `_v5` arm's printed result. My Phase 1 replacement text stands as
an optional ninth change.

T3 (member validity as a stored-status test, explicitly not the count-dependent eligibility flag),
T5 (ledger source follows the merged pin), T7 (blindness protects the overlap count, permits
reading bracket evidence to name a RECOVER cause) and T8 (`powermetrics*.plist` under `runs/`;
the member raw name is `powermetrics.plist`, `joulewise/adapters/powermetrics.py:51`, and
instrument-validation captures sit under `runs/`) are each correct as I read them. None of the
changes makes a selection depend on a count, changes the ladder, either floor, the per-rung
member minimum, the fallback or the refusal wording, so none contradicts D-166.

### Verdict

AGREE. No defect in the ruling would let the block select a wrong rung, spend a window by rule,
or contradict D-166. D1 should be applied with T6 (it saves a cold gate, not a number); D2
belongs in the seal record as a pre-arm citation.

## Summary

The judge and I independently found the same two harvest defects (a member whose clock check failed is still counted; an invalid member after a clean chain exit gives REFUSED instead of RECOVER), and the judge also caught a third that I missed (the recovery window had no usable ledger source or arm head).
I agree with SEAL: ADMIT and its eight text changes and two code conditions. One gap remains: T6 lets only a recovery window use a new head, so re-arming after a null window, or after a RECOVER that made no capture, would need a new seal. Replacement text is above.
Before arming, the seal record should cite one real member bundle produced at H whose clock anchor is `bounded`, so the new validity rule cannot turn every window into RECOVER.
