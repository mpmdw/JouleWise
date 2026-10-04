SEAL: ADMIT

# Cold registration gate G2A-25G83-B3: ruling (cold judge, Claude Fable 5.1, 2026-10-03)

ADMIT is conditional on the five registration text changes in §4 (T1-T5) and the two arm-recipe
changes in §5 (R1, R2) being applied verbatim before the seal record is written. No code
condition is placed on the arm head: the code at this commit does what the registration says for
every window of this block. One code obligation is named for the desk day (§6, F5), and it
applies only if the block ends in its end state.

What was judged: `configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md`, sha256
`5c224a91b968538f503f1ec8da47b73380c0aac33edcbe5b5b14c5ef4134d426` (verified), 368 lines, in the
detached worktree at `4add670b6ce766f62ba32f7e108f3f9416d56b21` whose parent is
`53be872e1a3d2bc0a1628707682c084bac616c5d` (both verified). Block 2's sealed registration beside
it has sha256 `8e45a0e0…a5b8`, equal to block 2's seal record. Session 19:52-20:13 PDT (about 21
of the 75 budgeted minutes). Each "old" block in §4 and §5 was checked by script to occur exactly
once, byte for byte, in its file.

Short version of the result. The rules are fixed before data and carry D-166 unchanged apart
from the end state. Four things in the text needed repair: (1) the end state's early trigger was
a judgment call that two operators could make differently; (2) the end state was described as
"D-166's exhausted-ladder branch", which it is not, and that label could become a false sentence
in the paper; (3) the reasoning about background work during a measured window claimed a
protection that neither D-166 nor the `_v5` code provides; (4) the arm-head rule let any
`docs/`-only commit through without a new seal, and the chain's settle length and summary guard
are bytes of two files under `docs/`.

## 1. Contamination disclosure

**Injected before the charge, not chosen by me.** The harness placed in my context the owner's
global `CLAUDE.md` (a writing standard and pointers to orchestration skills), this repository's
`CLAUDE.md` (Codex bridge notes), a memory index `MEMORY.md` of about 120 one-line hooks (among
them "paper threat = hallucination, not forgery", "check the physics, not the proxy", "never
brief halt-on-fixable", checkpoint lines for 2026-10-01), a git status snapshot with five recent
commit subjects, and a list of skills and tools. The charge forbids reading these. I could not
avoid the injected text; I opened no file behind any hook, no `CLAUDE.local.md`, no skill file,
and wrote no memory. Where a hook overlaps the charge (threat model, physical gates) I used the
charge's wording. No ruling rests on the injected text.

**Read beyond the charge's list, and why.**

| What | Why |
|---|---|
| `joulewise/adapters/powermetrics.py` lines 1210-1262 (`_capture_idle_slice`) | §4 says attempt 2 is a fresh 75 s baseline; I had to see that frames recorded during the wait are skipped |
| `joulewise/uncertainty_evidence.py` (grep for the 5 ms cap constants only) | §4's "exceeds 5 ms" |
| `scripts/issue_g2a_prefill_prompt_pin.py` (grep, about 30 lines) | Whether the end state's binding ("in place of a selection record") exists in code (ruling 9) |
| `configs/campaigns/d117_contrast_v5/generate_configs.py` lines 99-134 and a grep | Where D-166's two-way refusal wording lives in the `_v5` generator (ruling 6) |
| `scripts/validate_powermetrics_fiducial.py` lines 2150-2172 | A `tests/fixtures` path found by grep; needed to see it is test-mode only (ruling 8) |
| `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` (three export lines by grep; the whole file in memory through the generator) and `docs/phase_2/window_runbook.md` (in memory through the generator only) | The generator renders the chain from these two files (ruling 8) |
| `tests/test_harvest_g2a_window.py` lines 1-80 and its test names; test names of `tests/test_controller_retry_backoff.py` | To know what the fixtures mock before citing the tests as evidence |
| `configs/calibration/calibration_ledger_head.json`; `shasum` and line count of block 2 `w2`'s re-harvest `derived/terminal-ledger.jsonl` | §3's registered ledger seed and pin |
| `git log`/`git show -s` for design-branch commits `34871f70`, `97ff5035`, `ab2b3979` and the registration's history since `97ff5035` | To check the design record's claim that the end state was committed before the blindness slip |
| `docs/decision_log.md` D-078 index row and a grep for "re-collect" | Charge item 5 names D-078 |
| An emitted chain in scratch (`/tmp/cg-g2a-b3/emit/chain.zsh`) | Charge item 9 |

**Allowed by the charge and read:** block 2's two `harvest.json` files (`…20261003T0820Z-r2`,
`…20261003T1748Z-r2`), fields `verdict`, `cause_codes`, `capture_made`, member `valid` and
`clock_anchor_status` only. No file named `summary*`, `counts*`, `*counts-receipt*`,
`*resolvability-summary*` or `selection*` under the three night roots was opened. The synthetic
selector inputs I wrote live in `/tmp/cg-g2a-b3/sel/` under names beginning `syn-`.

**Listed files read only in part.** Block 2's `51r-seal-refuter.md`: about the first 150 lines.
`02-refuter-opus.md`, `51-seal-ruling.md`, `52-seal-record.md` of the earlier gates: in full.
`joulewise/controller.py`: lines 1040-1190. `joulewise/schemas.py`: lines 462-511 and 751-752.
`scripts/gen_g2_phase_d.py`: lines 1-560 and 640-685. `scripts/harvest_g2a_window.py` and
`scripts/select_g2a_prefill_length.py`: in full. `scripts/run_night.py`: grep for the span and
expiry lines. `scripts/generate_g2a_probe_inputs.py`, `scripts/summarize_g2a_prefill_probe.py`
and `joulewise/environment_admission.py`: not read line by line; exercised through their tests.
`joulewise/reduce.py`: the live value of `MIN_PHASE_SAMPLES` only. `docs/decision_log.md`: the
D-166 row.

**An inference the reading list itself makes available.** The `w2` session record (listed by the
charge) says the fix seat's real-data replay of `w2`'s twelve valid members ended "summary and
selection exit 0", and the design record §3 says the body of PR #463 "names the selector's
refusal code". Read together with the selector's code, these permit a guess about what block 2's
partial data would have selected. I did not seek it, did not read any PR body, cannot confirm
it, and no ruling below depends on it. I record it because the registration's blindness
statement should not claim more than is true (finding F6, change T5).

**Seen, not read.** `50-seal-charge.md`, `50-seal-charge.filled.md`, `50r-seal-refuter-charge.md`
(directory listing only). During the session an untracked `51r-seal-refuter.md` appeared in this
directory (the parallel refuter's output); I did not open it. Not read: `RUN_STATE.md`,
`TASK_QUEUE.md`, `AGENTS.md`, `CLAUDE.local.md`, any memory or skill file, any pull-request body
or comment. No subagent, no background task, no git write, fetch or checkout, no sudo,
launchctl, powermetrics or systemsetup, no model load, no capture.

**A discrepancy in the charge.** Charge item 5 asks about "a 600 s wait". The registration, the
policy file, the tests and the design record (§1, wait-length row) all say 300 s; 600 s was the
first ruling and was withdrawn after the clock audit. I ruled on 300 s. The seal record should
note that the charge's number was stale.

## 2. Executed checks

Interpreter `/Users/edr/code/JouleWise/.venv/bin/python -B` from the worktree root,
`TMPDIR=/tmp/cg-g2a-b3`. The tree afterwards holds this file and the refuter's file, nothing else
changed.

| # | Command (abridged) | Result |
|---|---|---|
| 1 | `git rev-parse HEAD HEAD^`; `shasum -a 256` of both registrations | `4add670b…`, `53be872e…`; `5c224a91…d426` (as charged); `8e45a0e0…a5b8` (block 2 seal record) |
| 2 | `diff -u registration_block2.md registration_block3.md` | Changes confined to: header, §1 (why a block 3), §2 labels, §3 (policy bullet, chain `POLICY`, ledger seed, unchecked-contention bullet), §4 (delayed retry, span), §6 (one sentence), §7 (end state), §8-§10 (end state, block 2 coverage), §12. §5 unchanged |
| 3 | `unittest tests.test_controller_retry_backoff tests.test_gen_g2a_window tests.test_harvest_g2a_window tests.test_schemas tests.test_select_g2a_prefill_length tests.test_summarize_g2a_prefill_probe tests.test_generate_g2a_probe_inputs tests.test_gen_g2_phase_d` | 184 tests, OK (1 skipped) |
| 4 | `unittest tests.test_idle_admission tests.test_environment_admission tests.test_controller tests.test_run_campaign` | 371 tests, OK |
| 5 | `scripts/gen_g2_phase_d.py --check` | `PASS generated Phase D matches pinned runbook bytes`, exit 0 |
| 6 | `NIGHT_PROGRAMMED_SPAN_S`; `ceil((span+2700)/60)*60`; `G2A_CAMPAIGN_POLICY_PATH`; `IDLE_RETRY_ALLOWANCE_COUNT`; `MIN_PHASE_SAMPLES` | 18868; 21600; `configs/campaign_policies/quiet_mac_p2_g2a_b3.json`; 4; 3. All equal §3-§4 and §8 |
| 7 | `diff` of the production and block-3 policy files; `shasum`; `git log` of the production file | Exactly two differences: `policy_id`, and `retry_backoff_s: 300` added. Production sha256 `b0d7b228…5efd`, last changed long before the lane base; block-3 sha256 `04bdbec4…edc7` |
| 8 | `CampaignPolicy.from_mapping` on both files | production `retry_backoff_s=0.0`; block 3 `300.0`; both `retry_attempts=1`, `on_fail=abort`, `enabled=True` |
| 9 | `gen_g2_phase_d.py --emit-chain /tmp/cg-g2a-b3/emit/chain.zsh --night-date 20261004 --plan-id …`; `zsh -n`; greps | Emitted, syntax OK. One `export POLICY=…/quiet_mac_p2_g2a_b3.json`, zero mentions of the production policy; `NIGHT_PROGRAMMED_SPAN_S=18868`; `SETTLE_S=600`; `PRE_CAL_FIDUCIAL_MAX_S=0.036462861644980` with the acceptance comment `…25g83_r2 (sha f949f511...)`; stages small then large × 512/1024/2048/4096; `--arm-quiet-mode … --max-failures 1`; `--campaign-policy "$POLICY"` on every stage and on the input check; summarizer and `all(.small_members >= 5)` last |
| 10 | Selector on six synthetic four-row summaries (`/tmp/cg-g2a-b3/sel/syn-*.json`) | minimum counts 4,4,5,9 → 2048; 5,5,5,5 → 512; 2,3,4,4 → refused `no_g2a_prefill_rung_qualifies`, collect 4096; 3,6,4,7 → 1024 (shortest qualifying, non-monotone); four members at 512 → 1024; a zero-member rung written as 0 → `summary_internally_contradictory`, exit 2. Rule record: ladder 512-4096, count floor 5, 5 members per rung, reducer floor 3 |
| 11 | Harvest verdict logic: the 52 tests of `tests.test_harvest_g2a_window` inside check 3, by name | SELECT on a complete window; RECOVER on shortfall, post-bracket failure, nonzero or missing exit, unadmitted OFF receipt, open session; NULL when the chain never started; REFUSED on authentication faults; a non-`bounded` clock anchor makes a member invalid; a count below 3 with a bounded anchor stays valid; `capture_made` from the archive copy; the bracket is judged under the window's own inventory policy for both a block-2 and a block-3 fixture; a policy that is not claim-grade is REFUSED |
| 12 | In-memory mutation of the runsheet text (`export SETTLE_S=600` → `60`; `all(.small_members >= 5)` → `>= 1`) through the generator's own `--check` logic and `render_g2a_night_chain` | Both mutated documents pass the check; the emitted chain then carries `export SETTLE_S=60`. Finding F1 |
| 13 | Scratch test of the replacement `case` statement R1 (`/tmp/cg-g2a-b3/recipe/check.zsh`) | docs/tests/RUN_STATE/pin file pass; either chain-source document exits 3; an unlisted code file exits 3; a file listed under `## H′ extensions` passes |
| 14 | `shasum` of the D-166 registration file and the acceptance file; `calibration_ledger_head.json`; `shasum` and `wc -l` of the registered ledger seed | `dfe55f8d…c265`; `f949f511…3660`; pin sequence 392; seed `84bb9aee…475b`, 392 lines. All equal §2-§3 |
| 15 | Block 2 `harvest.json` × 2 (permitted fields) | `w1`: RECOVER, `capture_made` true, 0/24 valid, all 24 `not recorded`. `w2`: RECOVER (`bracket_incomplete`, `chain_nonzero_or_missing_exit`, `rung_valid_small_members_shortfall`), `capture_made` true, 12/24 valid, 12 `bounded`, 12 `not recorded`. Agrees with §1's account |
| 16 | `git show -s` on `34871f70`, `97ff5035`, `ab2b3979`; `git show 97ff5035:…registration_block3.md` grep; `git diff 97ff5035 HEAD` on the registration | Ruling 18:23:03, draft registration 18:27:57 (already containing the end state at 4096), recipe 18:29:27, all before the 18:29:45 read the design record discloses. Later rule changes: 600 s → 300 s, the span and window numbers, the sizing paragraph. Nothing in the selection rule or the end state |

**NOT EXECUTED.** The whole test suite. Any live command (`--new-g2a-window`, `bind-window`,
`check`, the driver, the harvest on a real window, the recipe's steps 0-5). A real bundle with a
delayed retry through the strict validator and the clock-anchor estimator (the lane's evidence is
a fixture and synthetic records). The block-2 clock figures the sizing rests on (drift about
3.2 ppm, half-widths up to 2.31 ms, about 104 s per idle attempt): I did not re-read member
metadata; they come from the code lane's final pass (record 21). The burst timeline in the
unified log. Mutation probes of the controller (the lane's executing review reports six, all
killed; I did not repeat them). D-078's full text (index row only).

## 3. Rulings

### 1. Fixed before data, and unambiguous?

Fixed before data: yes. No count or energy of block 2 or block 3 is in the file; the ladder, the
floors, the member numbers, the verdict classes, the wait length, the window length and the stop
rules are literals; the verdict and the selection are computed by code. SELECT, RECOVER, NULL
and REFUSED are each one mechanical test in `scripts/harvest_g2a_window.py`, and two operators
running the harvest on the same files get the same verdict (check 11).

One rule can be applied two ways: **the early trigger of the end state** (§7). The draft stops
the block after the first RECOVER when "a cause named after the first RECOVER is systematic and
not removable (for example most members' clock anchors not `bounded`)". "Systematic and not
removable" is a judgment. The realistic case is a second window lost to a macOS maintenance
burst longer than the wait: the design record itself says no setting removes that class of
disturbance, so one magistrate would call it systematic and go straight to the end state, and
another would call it a transient and arm the recovery window. The two readings give different
papers (a length selected by a probe, or a length fixed by default), so the trigger has to be
mechanical. T1 keeps the one example the draft names and makes it a test on `harvest.json`: at
least 5 members that ran and recorded a clock-anchor status, more than half of them not
`bounded`. Every other cause gets the recovery window. The cost of this choice is at most one
window (about 6 h on a dedicated machine) in a systematic case the test does not name; the gain
is that the probe cannot lose its second window to a reading of two adjectives. F2.

Nothing else needs a second reading. "Null window", "made no capture", "same refusal reason code
twice" and the recovery allowance are as block 2 sealed them, and block 2's two windows
exercised the RECOVER and REFUSED paths on real files.

### 2. D-166 as amended, carried faithfully?

Yes, with one sentence to remove.

| D-166 element (index row; 2026-08-30 records 01-03) | Registration | Code at this commit |
|---|---|---|
| Ladder 512/1024/2048/4096, shortest that clears | §1, §8 | `LADDER`, `qualifying[0]` (check 10) |
| Count ≥ 5 in every small member, stated as a count | §1, §8 | `MIN_OVERLAPPING_POWER_INTERVAL_COUNT = 5` |
| ≥ 5 small members per rung, else not selectable | §1, §6 | `MIN_SMALL_MEMBERS = 5`; four members at 512 never select 512 (check 10) |
| Reducer floor 3, checked live | §8 | selector refuses `reducer_floor_drift` unless `MIN_PHASE_SAMPLES == 3` (check 6) |
| No rung clears: collect at 4096 | §1, §8 | `collection_prefill_tokens = 4096`, `collect_at_4096` |
| Two-way refusal wording | §1, §8 | `"<3"` → `not_resolvable_sample_count`; `"3-4"` → "below the pre-registered count floor of 5", reducer result disclosed |
| Large model recorded, never gating the rule | §1, §7, §8 | large rows never enter `qualifying` |
| Sweep with ≥ 5 members per rung is the selection's precondition (A4) | §6-§7: all four small rungs evaluable before SELECT | harvest returns RECOVER on any shortfall and does not run the selector |

The sentence to remove is in §9, third bullet: "`_v5` members … print their own counts with
D-166's wording, so a shortfall at the selected rung is reported as a refusal, never as an
energy." D-166 attaches the two-way wording to the 4096 fallback only, and the `_v5` generator
encodes it that way (`PREFILL_EXHAUSTED_LADDER_BRANCH`, condition
`no_rung_clears_pre_registered_count_floor`). At a selected rung a `_v5` member with 3 or 4
overlapping records has a valid reducer energy under D-166. So the draft sentence either changes
D-166 in a second place (which §1 says the registration does not do) or describes a protection
that does not exist. T3 replaces it with what is true. F4.

### 3. The §7 end state

**Admitted, as amended by T1.** What it is: D-166 as ratified on 2026-08-30 gives two routes to
the `_v5` prefill length: a rung selected from a complete sweep, or 4096 when a complete sweep
shows no rung clearing. Ratification A4 makes the sweep the precondition of both. The end state
adds a third route: 4096 by default when the sweep cannot be completed within this block's
allowance.

Why it is an admissible prospective amendment:

- **It is fixed before the data it governs.** No block-3 data exists. The clause was committed
  at 18:27:57, before the one blindness slip on record (check 16), and it was proposed by a
  consult seat that was blind to block 2's counts.
- **Its trigger cannot see a count.** RECOVER is defined without reference to any overlap
  count, the harvest prints none, and the selector does not run on a RECOVER window. Nobody can
  reach the end state because a result looked unwelcome.
- **Its outcome is not chosen by the data either.** 4096 is the top of the ladder D-166 already
  fixed, the length at which a prefill phase overlaps the most power records, and the length
  D-166 already prescribes when the probe gives no answer in the other way.
- **It bounds the loop.** Block 2 spent two windows; block 3 may spend two more that make a
  capture. Without the clause the next step would be a fourth registration. A gate exists to
  protect numbers and to stop wasted windows; this clause does the second without touching the
  first.

Could it let a wrong number into the paper? No. The energy to prefill a pinned 4096-token
prompt is as well defined as at any other rung, and each `_v5` member is still judged by the
reducer's floor of 3 records and printed with the two-way wording.

Could it let a misleading sentence in? Two, and T1 closes both:

1. *"No rung qualified, so the prefill arm was collected at 4096."* The draft says the question
   "is closed by D-166's exhausted-ladder branch". That branch means a ladder was evaluated and
   every rung failed. Under the end state no ladder was evaluated. A reader of the draft, or a
   later seat writing the paper from it, could carry the label across. T1 says in the
   registration that the end state borrows the branch's outcome and is not the branch, and that
   no record or sentence may say no rung qualified.
2. *"The pre-registered rule selected 4096."* The draft already requires the paper to say the
   length was fixed by the end state and not selected. T1 spells the sentence out, including
   that nothing is claimed about which shorter lengths would have qualified.

What the amendment gives up, stated plainly: if the end state occurs, the paper cannot say its
prefill length was the shortest resolvable one. The 2026-08-30 cold ruling rejected "fix 4096
outright" for exactly that reason, at a time when a measured selection was still available at
no cost. Here it is given up only after four capture-bearing windows have failed to complete a
sweep, and the paper says so.

**The sentence the decision log can cite.** D-166 is amended prospectively by the cold
registration gate G2A-25G83-B3 (2026-10-03, this ruling,
`docs/process_traces/2026-10-03-design-block3/51-seal-ruling.md`): if block 3's recovery window
also ends RECOVER after making a capture, or the first such RECOVER shows at least 5 members with
a recorded clock-anchor status and more than half of them not `bounded`, the G2-a sweep stops
being the precondition and the `_v5` prefill arm is collected at 4096 prompt tokens as a default
fixed in advance, not a selection, with every member's count printed under D-166's two-way
wording, the paper saying the length was not selected by a probe, and the `_v5` pre-registration
binding the block-3 registration's sha256 and each window's `harvest.json` sha256 in place of a
selection record.

This ruling is the amendment's record.

### 4. "It never goes to a third blind window"

Block 3 is consistent with that clause. The clause closes a list in block 2 §7: after a second
incomplete sweep "the block stops and the question goes to a consult (Sol 6.1 plus Opus, blind),
then to the orchestrator's ruling … It never goes to a third blind window." What it forbids is
arming again under block 2's seal without that route: a third window armed without knowing why
the first two failed. What happened is the route itself: two seats consulted blind to each other
and to the counts, a cause was named from logs (both of one member's idle checks fell inside a
six-minute maintenance burst, and the retry started half a second after the first attempt), the
code was changed and reviewed, and a new registration was written and brought to a cold gate. A
consult whose only permitted answers excluded "run a corrected sweep under a new seal" would
have no purpose.

Two things keep this from being a way around the clause in future. First, block 3 carries its
own hard stop: the end state means there is no block 4 for this question. Second, the selection
rule is unchanged from D-166, so nothing learned from block 2 could have been used to tune it.

"Blind to block 2's partial data" is true of the counts and summaries and of everything that
shaped the rules. It is not true without exception: see the disclosure in §1 and finding F6. The
exception came after the rules it could have touched were committed, and the rule changes made
afterwards (the wait length and the span) came from a clock audit, not from any count.

### 5. The delayed retry

**Does a 300 s wait weaken the quiet-machine bar?** No. The bar is the state a member must be in
when it is admitted: over a fresh 75 s idle baseline, CPU busy ratio at the 95th percentile no
higher than 0.5 over at least 30 records, processor power at the 95th percentile no higher than
1.0 W, GPU idle, and the environment guard (AC power, displays asleep, no screensaver, thermal
state nominal). Attempt 2 is judged on exactly those tests (check 7: the two policy files differ
only in the id and the wait), on frames recorded after the wait (the adapter skips every frame
completed during the wait and one more that straddles the boundary,
`joulewise/adapters/powermetrics.py` 1244-1254), after the environment guard is observed again.
The wait changes when the second look happens, not what it must see.

**Does it bias which members are measured?** No. Admission happens before the member's prefill,
so it cannot depend on the member's count. No member is skipped, replaced or re-run: every
roster member runs in the fixed order, and a member that fails both attempts stops the chain
(`--max-failures 1`), which makes the window RECOVER, not a window with a missing member. The
only difference from block 2 is that a member whose first check met a transient is measured
about seven minutes later instead of ending the window. That member is measured on a machine
that passed the same screen as every other member. Whether leftover background work could still
touch its count is the question of ruling 6, and applies to every member alike.

**Is it re-collection?** No. The registration's own rule (§7) is that no member or rung is
collected again inside a window. Here the member keeps its run id, both idle captures stay in
its bundle, nothing is replaced, and the second attempt is the one retry the production policy
has always allowed. D-078's index row is a soundness gate on corpora with a defective time
anchor; I found no re-collection rule in it that this could breach (full text not read).

**Does the code do exactly what §4 says?** Yes (`joulewise/controller.py` 1107-1162; checks 3,
4, 7, 8):

| §4 statement | Code |
|---|---|
| Wait only after a rejected attempt 1 | line 1110 `if not attempts[-1]["admitted"]`, then 1111 `if admission.retry_backoff_s > 0` |
| Not when attempt 1's own environment guard failed | `_enforce_post_capture_admission_guard(1)` at 1109 raises before the wait |
| Environment guard observed again, then attempt 2 | 1120-1132 |
| Same criteria | one policy object; no branch on the attempt number |
| One retry; abort on the second rejection | schema refuses `retry_attempts != 1`; 1151-1162 raises "idle environment admission failed after one retry" |
| Production policy byte-identical, wait 0 | file untouched; parses to 0.0; the wait block is skipped at 0 |
| Wait recorded, not counted as an attempt | `environment_admission["retry_backoff"]`, outside `attempts` and `guard_observations` |

Tests executed: the seven controller tests and two clock-anchor tests of
`tests/test_controller_retry_backoff.py`, plus the schema, generator and harvest tests (184 OK),
and the admission, controller and campaign-runner modules (371 OK).

**Two risks the registration states honestly and I confirm are window risks, not number
risks.** (a) The wait is sized on one burst: 300 s would have started the retry about 30 to 50 s
after that burst's logged end. A burst a minute longer loses the window. (b) A retried member's
power stream is long (an estimated 520 to 683 s), and the clock-step test refuses a stream whose
bound exceeds 5 ms; at block 2's drift of about 3.2 parts per million the estimate is about
4.5 ms, and the tolerance is about 3.9 parts per million. If the clock drifts faster during
block 3 a retried member is invalid and the window is RECOVER. Both fail closed: the member is
refused, never counted. Neither justifies a text change. F8.

### 6. Background work during a measured window

The draft's reasoning is "its only possible effect … is to lengthen a prefill phase, which can
raise a member's record count, never lower it". That is half of the physics.

The count is the number of power records whose time span overlaps the prefill phase. Two things
set it: how long the phase lasts, and how long each record is. Background work can change both.

- It can slow the prefill (competition for the GPU or for the threads that feed it). A longer
  phase overlaps more records: the count rises.
- It can delay the power sampler, which is itself a process that must be scheduled. Delayed
  samples come out as longer records, and in the worst case two merge into one. The 2026-08-30
  cold ruling records exactly this in the retained corpus (a 460.7 ms record against a median of
  about 121 ms) and names it as one of the two events that lower a count. Longer records mean
  fewer of them overlap a phase of the same length: the count falls.

So "never lower" is wrong. The conclusion survives, because the two directions have different
consequences and neither is a false number:

- A lowered count can only make a rung fail that would have passed on a quieter machine. The
  selection moves to a longer rung or to the 4096 fallback, where the prefill is more
  resolvable. Cost: a prefill arm longer than necessary.
- A raised count can make a rung pass that would have failed, so the selected rung could be one
  step too short. This needs every one of the five members at that rung to reach 5, so the
  disturbance must hit each member that would otherwise show 3 or 4, each of which passed a 75 s
  idle screen seconds earlier.

Is the stated consequence complete? No (ruling 2): the draft says a shortfall at the selected
rung "is reported as a refusal, never as an energy". What actually protects the paper is the
reducer's floor, not the count floor: a `_v5` member with fewer than 3 overlapping records gets
the reducer's refusal and no energy; a member with 3 or more has a valid energy. The floor of 5
is, in the 2026-08-30 ratification's words, a declared safety factor: its job is to keep `_v5`
members from falling below 3 on a worse draw than the probe saw. A rung chosen one step too
short therefore costs `_v5` members (refused phases, a weaker or lost prefill contrast), never a
wrong energy.

**Is a check needed, and what number would it protect?** No check is needed, and none would
protect a number in the paper. The only thing a check could protect is the protocol parameter
itself, that is, the margin of the `_v5` prefill arm against reducer refusals. There is also no
sensible check to write: during the measured window the machine is busy by design, so the idle
criteria cannot be applied, and a threshold on "extra" activity would have to be invented. T2
and T3 correct the reasoning and the consequence.

### 7. Network time, validity and stop rules, claim boundary, blindness

- **Network time (§5).** Unchanged from block 2, byte for byte (check 2), and the block-2 gate's
  reasoning holds: the count is taken inside one capture, the binding within-capture clock test
  is what protects it, and a step between captures changes no count. The delayed retry makes
  that binding test bite harder on retried members (ruling 5, risk b); the registration says so
  in §4 and §6. No change.
- **Validity (§6).** One added sentence (a member admitted on attempt 2 is judged by the same
  rules). Right, and true in code: the harvest's member test never looks at the attempt number.
  No change.
- **Stop rules (§7).** T1 (rulings 1 and 3). Otherwise as sealed for block 2.
- **Claim boundary (§9).** T3. The other bullets are right, including the two new ones (block
  2's bundles are never a selection input; the #416 audit applies before the first claim-bearing
  window at a head containing the controller change; I could not verify the #416 wording without
  reading memory, as in block 2).
- **Blindness (§10).** The extension to block 2's windows is right. The sentence should carry
  the one known exception and name the PR bodies as places the block-2 replay outcome sits. T5.

### 8. §12's arm-head rule and the recipe's check

The rule's shape is sound: the arm head may differ from the sealed head by pin advances, by
gated fixes that make code agree with the text and are listed in the seal record, and by
commits that touch only documentation, tests and the two state files. The recipe checks it per
changed file with `git diff --name-only`, which is stricter than §12's pin list (any code file
not on the allow-list stops the arm, pinned or not).

**The hole.** Clause (iii) and the recipe's `docs/*` pattern treat everything under `docs/` as
unable to change the window. Two files under `docs/` are the chain's source:
`scripts/gen_g2_phase_d.py` renders the chain from
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` (`RUNSHEET_PATH`, line 311),
whose bracket region is in turn generated from `docs/phase_2/window_runbook.md`. The settle
length (`export SETTLE_S=600`), the stage helpers and the summarizer's guard
(`all(.small_members >= 5)`) are bytes of those documents. Check 12: changing `SETTLE_S` to 60
in the runsheet, or the guard to `>= 1`, passes the generator's own `--check`, and the emitted
chain carries the changed value. Such a commit is "docs only", so under the draft it needs no
new seal and the recipe's step2 passes it, although §3 and §4 fix the chain and the 600 s
settles. The threat here is an honest edit (a documentation sweep, a regenerated region), which
is the threat model the owner named. F1.

**The cure.** T4 pins the two documents in §12 and takes them out of clause (iii). R1 makes the
recipe's check refuse a change to either unless the seal record lists it as a gated fix (check
13).

**What the mechanical check does not and cannot do.** It cannot tell whether a listed fix
really "makes code agree with this text"; that judgment is the gated pull request's and, as in
block 2, a cold ruling's. The allow-list is read from the seal record at the arm head, and the
seal record is itself under `docs/`, so the check certifies that a difference was written down,
not that it was allowed. That is acceptable for a check whose job is to catch an unnoticed
difference. Two nits on the same lines (F9): the match is a substring match over everything
after the heading to the end of the file, and the pin file is allowed to differ whether or not
the advance came from this block (step1's ledger check then requires a ledger that matches it).

### 9. Does the code implement the registration?

Yes for everything a window of this block executes.

| Registration | Code at this commit | Evidence |
|---|---|---|
| §3 policy = production + id + wait 300 | two-field diff | check 7 |
| §3 chain exports that policy, once | one `export POLICY=` naming it; no production reference | check 9; recipe step2 repeats it |
| §4 span 18,868 s; window 21,600 s | `NIGHT_PROGRAMMED_SPAN_S = 18868`; formula gives 21600 | check 6; 7947.40625 + 4800 + 1200 + 1440 + 1440 + 420 + 1620 = 18,867.4, rounded up |
| §4 four delayed retries of 300 s plus the attempt-2 capture | `4 * (300 + 75 + 30) = 1620` | generator lines 90-93 |
| §4 stage order, settles, `--arm-quiet-mode --max-failures 1` | emitted chain | check 9 |
| §4 screen literal from the acceptance in force | `--check` passes; literal carries the acceptance id and sha prefix | checks 5, 9 |
| §4 the wait | controller 1107-1162 | ruling 5 |
| §6-§7 verdicts | harvest lines 125-131, 170-182, 238-254 | check 11 |
| §8 selector | `select_g2a_prefill_length.py` | check 10 |
| §2-§3 hashes, ledger seed, pin | as registered | check 14 |

Mismatches between text and code:

| | Text | Code | Which side changes |
|---|---|---|---|
| F5 | §7, §8: under the end state the `_v5` pre-registration binds this registration's sha256 and the harvest records' sha256s in place of a selection record | `scripts/issue_g2a_prefill_prompt_pin.py` requires `--selection-record` and checks it against a summary; the `_v5` generator's refusal wording is keyed to the condition `no_rung_clears_pre_registered_count_floor`, which would be false | **Code**, at the desk day, by a gated pull request, and only if the end state occurs. It fails closed today (no pin, no `_v5` pack). Not a condition on any window of this block |
| F4 | §9: `_v5` members print with D-166's wording at a selected rung | the wording exists only for the exhausted-ladder branch | **Text** (T3) |
| F10 | §4: `window_max_s` = span + 2700 rounded up | `--new-g2a-window` accepts any value ≥ span + 900 | Neither must: recipe step2 refuses any other value. Carried over from block 2 (its F8) |

## 4. Required registration text changes (apply verbatim before the seal record is written)

Line breaks in the "old" blocks are the file's own.

**T1 (§7, end state: mechanical trigger; the end state is not the exhausted-ladder branch; the paper's sentence).**

Old:
```
**End state (pre-committed; the one change to D-166, ruled by this block's seal).** If the
recovery window also ends RECOVER, or a cause named after the first RECOVER is systematic and not
removable (for example most members' clock anchors not `bounded`), the block stops, and the
prefill-length question is closed by D-166's exhausted-ladder branch without a further probe:
the `_v5` prefill arm is collected at 4096 prompt tokens, every `_v5` member's prefill count is
printed with D-166's two-way refusal wording (count < 3: the reducer's refusal; count 3-4: "below
the pre-registered count floor of 5", with the reducer's resolvable result disclosed alongside),
and the paper states that the length was fixed by this end state, not selected by a probe. The
```
New:
```
**End state (pre-committed; the one change to D-166, ruled by this block's seal).** If the
recovery window also ends RECOVER, or the `harvest.json` of the first RECOVER that made a capture
shows the one systematic cause registered here (at least 5 members whose `clock_anchor_status`
is other than `not recorded`, and more than half of those other than `bounded`: the clock-step
test of §5(b) is then failing for the instrument, which re-arming cannot remove), the block
stops, and the prefill-length question is closed without a further probe. Any other cause of a
first RECOVER leads to the recovery window. The end state borrows the outcome of D-166's
exhausted-ladder branch and is not that branch: no ladder was evaluated, so no record or
sentence may say that no rung qualified. Under the end state
the `_v5` prefill arm is collected at 4096 prompt tokens, every `_v5` member's prefill count is
printed with D-166's two-way refusal wording (count < 3: the reducer's refusal; count 3-4: "below
the pre-registered count floor of 5", with the reducer's resolvable result disclosed alongside),
and the paper states that the 4096-token length was fixed in advance as the default for a probe
that could not be completed, that no probe selected it, and that nothing is claimed about which
shorter lengths would have qualified. The
```

**T2 (§3, last bullet: both directions of the effect).**

Old:
```
  screened. Registered as an unchecked condition because its only possible effect on this block's
  output is to lengthen a prefill phase, which can raise a member's record count, never lower it;
  §9 states what that means for the use of the result.
```
New:
```
  screened. Registered as an unchecked condition because neither of its two possible effects on
  this block's output can put a false number in the paper. It can lengthen a prefill phase, which
  raises a member's record count; §9 states what that means for the use of the result. It can
  also delay the power sampler so that its records come out longer than usual, or merged, which
  lowers a count; a lowered count can only move the selection to a longer rung or to the 4096
  fallback, where the prefill is more resolvable.
```

**T3 (§9, third bullet: what actually protects the paper at a selected rung).**

Old:
```
  step shorter than a quieter probe would select. The selection is used only as a protocol
  parameter; `_v5` members are collected under the same admission and print their own counts
  with D-166's wording, so a shortfall at the selected rung is reported as a refusal, never as an
  energy.
```
New:
```
  step shorter than a quieter probe would select. The selection is used only as a protocol
  parameter, and a rung that is too short cannot put a false energy in the paper: every `_v5`
  prefill phase is judged by the reducer's own floor of 3 overlapping records, so a `_v5` member
  below 3 prints the reducer's refusal (`not_resolvable_sample_count`) and no energy, and a
  member at 3 or more has a valid reducer energy, with its count recorded in its bundle. The
  count floor of 5 is the safety margin against losing `_v5` members to that refusal; what a
  too-short rung can cost is members, not a wrong number. D-166's two-way wording applies where
  D-166 puts it (the 4096 fallback) and under the §7 end state.
```

**T4 (§12: the chain's two source documents are pinned and are not "docs only"). Two replacements.**

Old (T4a):
```
`configs/model_panels/qwen3_4bit.json`, the D-166 registration file and the acceptance file.
```
New (T4a):
```
`configs/model_panels/qwen3_4bit.json`, the D-166 registration file, the acceptance file, and the
two documents the generator renders the chain from, `docs/phase_2/window_runbook.md` and
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` (the chain's settle length,
stage helpers and summary guard are bytes of these two files).
```

Old (T4b):
```
(§11), and (iii) commits that change only files under `docs/`, `tests/`, or the files
`RUN_STATE.md` and `TASK_QUEUE.md`; the arm checks (iii) with `git diff --name-only H H′`. The seal
record is extended with the H′ pins before each arm; no new seal is needed. Any other difference
needs a new seal.
```
New (T4b):
```
(§11), and (iii) commits that change only files under `docs/`, `tests/`, or the files
`RUN_STATE.md` and `TASK_QUEUE.md`, and that leave the two pinned chain-source documents named
above unchanged; the arm checks (iii) with `git diff --name-only H H′`, which must not list
either document unless the seal record lists it under (ii). The seal record is extended with the
H′ pins before each arm; no new seal is needed. Any other difference needs a new seal.
```

**T5 (§10: the one known exception to blindness, and where the block-2 replay outcome sits).**

Old:
```
counts, summaries and any selection replay stay unread until this block ends, and afterwards they
are diagnostic only. Naming the cause of a RECOVER, as §7 requires, may read that window's bracket
```
New:
```
counts, summaries and any selection replay stay unread until this block ends, and afterwards they
are diagnostic only. One exception is on record (design record 00 §3): after this file's
selection rule and end state were committed, the design seat read, in the body of PR #463, the
outcome code of a selector replay on block 2's partial data. The only rules changed after that
read are the wait length (600 s to 300 s, from the clock audit described in §4) and the changes
the sealing gate required. The bodies of PRs #461-#464 stay unread by every seat until this
block ends. Naming the cause of a RECOVER, as §7 requires, may read that window's bracket
```

## 5. Required arm-recipe changes (`40-g2a-b3-arm-recipe.md`; apply verbatim)

**R1 (step2, the §12 check: the two chain-source documents are not "docs only").**

Old:
```
  case "$f" in
    docs/*|tests/*|RUN_STATE.md|TASK_QUEUE.md|configs/calibration/calibration_ledger_head.json) ;;
    *) awk '/^## H′ extensions/{x=1} x' "$SEAL_RECORD" | grep -qF -- "$f" \
         || { echo "H differs from SEAL_H outside registration §12: $f"; exit 3; } ;;
  esac
```
New:
```
  case "$f" in
    docs/phase_2/window_runbook.md|docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md)
      awk '/^## H′ extensions/{x=1} x' "$SEAL_RECORD" | grep -qF -- "$f" \
        || { echo "H changes a pinned chain-source document outside registration §12: $f"; exit 3; } ;;
    docs/*|tests/*|RUN_STATE.md|TASK_QUEUE.md|configs/calibration/calibration_ledger_head.json) ;;
    *) awk '/^## H′ extensions/{x=1} x' "$SEAL_RECORD" | grep -qF -- "$f" \
         || { echo "H differs from SEAL_H outside registration §12: $f"; exit 3; } ;;
  esac
```

**R2 (§7 table, the first-RECOVER row: the same mechanical trigger as T1).**

Old:
```
If the cause is systematic and not removable (for example most members' clock anchors not `bounded`): the block stops in its END STATE (below).
```
New:
```
If `harvest.json` lists at least 5 members whose `clock_anchor_status` is other than `not recorded` and more than half of those are other than `bounded`: the block stops in its END STATE (below).
```

**For the seal record (not text changes).** List the sha256 of the two chain-source documents
at H with the other pins; keep the heading `## H′ extensions` with `none`; note that charge
item 5's "600 s" was stale and the gate ruled on 300 s; add the D-166 amendment note to the
decision-log row citing ruling 3's sentence; record F5 as an open desk-day obligation.

## 6. Findings

| # | Severity | Location | Claim | Evidence |
|---|---|---|---|---|
| F1 | major | Registration §12 clause (iii); recipe step2 `case` (`docs/*`); `scripts/gen_g2_phase_d.py` 20-24, 311 | A commit that changes only `docs/` can change the chain (settle length, summary guard, stage helpers) and needs no new seal under the draft, because the chain is rendered from two documents under `docs/`. The generator's `--check` does not catch it. Text and recipe change (T4, R1) | Check 12: runsheet with `SETTLE_S=60` or `all(.small_members >= 1)` passes the `--check` logic; emitted chain carries `export SETTLE_S=60`. Check 13: R1 refuses both documents |
| F2 | major | Registration §7 end state, "systematic and not removable"; recipe §7 first-RECOVER row | The early trigger is a judgment two magistrates can make differently (a second burst loss: "systematic", per the design record's own finding that no setting removes the class, or "transient"), and the two readings give a selected length or a default length. Text changes to a mechanical test (T1, R2) | Design record §2 item 2; recipe §7; block 2 `w2` harvest record shows the fields the test reads (check 15) |
| F3 | major | Registration §7 end state, "closed by D-166's exhausted-ladder branch" | The end state is not that branch (no ladder was evaluated). The label can turn into the false sentence "no rung qualified". Text changes (T1) | D-166 index row: "If no rung clears"; ratification A2, A4; the `_v5` generator's condition name `no_rung_clears_pre_registered_count_floor` |
| F4 | major | Registration §3 last bullet, §9 third bullet | "Never lower" is wrong (a delayed sampler gives longer or merged records, which lowers a count), and "a shortfall at the selected rung is reported as a refusal, never as an energy" claims a protection D-166 and the `_v5` generator give only for the 4096 fallback. No wrong number follows: the lower direction is the safe one, and the reducer's floor of 3 is what protects an energy. Text changes (T2, T3) | 2026-08-30 cold ruling Q1 item 3 (merged record, 460.7 ms); `generate_configs.py` 115-134; selector refusal record |
| F5 | minor (decided, not yet built) | Registration §7, §8 end-state binding; `scripts/issue_g2a_prefill_prompt_pin.py` (`--selection-record` required, `_selection_from_inputs`); `_v5` generator's exhausted-ladder condition | The end state's binding has no code path. Fails closed (no prompt pin, so no `_v5` pack). Code changes at the desk day by a gated pull request, only if the end state occurs; the registration text is right | grep of the issuer and generator (ruling 9) |
| F6 | minor | Registration §1 "blind to block 2's partial data", §10 | One block-2 selector replay outcome was read by the design seat after the rules were committed, and the records on this gate's reading list allow a guess at it. No rule could have been steered (check 16). The text should say so (T5) | Design record §3; `w2` session record, R3 paragraph; commit times in check 16 |
| F7 | minor | Charge item 5; lane brief (record 10) | Both say 600 s; the registration, policy, code and tests say 300 s. The gate ruled on 300 s. Seal record should note it | Checks 7, 8; design record §1 wait-length row |
| F8 | minor (window risk, stated in the text) | Registration §4 "Why 300 s" | The wait clears the one burst on record by under a minute, and a retried member's clock bound is estimated at 4.5 ms of a 5 ms cap (tolerance about 3.9 against about 3.2 parts per million observed). Either can lose a window; both fail closed; the end state caps the cost at two windows. No change | Lane records 12, 13, 21; `RetryBackoffClockAnchorTests` (check 3). Block-2 clock figures not re-read by me |
| F9 | nit | Recipe step2 | The `## H′ extensions` match is a substring match to the end of the file, and the pin file may differ whether or not this block advanced it (step1 then demands a matching ledger). Suggested, optional: list each extension as a line holding only the path and match with `grep -qxF` | Recipe lines 229-236 |
| F10 | nit | `gen_g2_phase_d.py` 349 | `--new-g2a-window` accepts any `window_max_s` ≥ span + 900; the recipe's step2 enforces 21,600. Carried from block 2 | Code read; recipe step2 |
| F11 | nit | Registration §4 item 3 | The text does not say that an environment-guard failure before attempt 2 also aborts the member (code 1120-1131). Consistent with §3's list of criteria. Optional: after "runs attempt 2" add "(a guard failure there aborts the member, as on attempt 1)" | Code read; `test_retry_guard_is_rechecked_after_wait_and_can_abort_before_capture` |
| F12 | nit | `gen_g2_phase_d.py` 90-93 | The retry allowance uses the nominal 75 s idle; block 2's attempts took about 104 s. About 9 s per retry, inside the member allowances | Lane record 20 (rejected there; I agree) |

No blocker. Nothing found contradicts D-166 outside the end-state clause once T3 is applied.

## 7. Plain summary

The block-3 rules are fixed before any data, carry D-166 unchanged, and the code at this commit does what they say: the retry waits 300 s only after a rejected first idle check, applies the same tests once more, and aborts on a second rejection (555 tests run, none failed, 1 skipped).
ADMIT, with five exact text replacements and two recipe replacements: the end state (4096 tokens by default if the probe cannot be completed twice more) is admitted as a prospective amendment of D-166, with a mechanical trigger, and the paper must say the length was fixed and not selected, never that no rung qualified.
One real hole was closed: a "docs only" commit could have changed the chain's 600 s settles without a new seal, because the chain is generated from two files under `docs/`; those files are now pinned.
