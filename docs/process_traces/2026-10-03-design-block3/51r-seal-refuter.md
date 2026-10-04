REFUTER G2A-25G83-B3: AGREE

PROVISIONAL (Phase 1): SEAL: ADMIT

# Refuter for cold registration gate G2A-25G83-B3 (Opus 5.5)

Worktree `/Users/edr/code/JouleWise-wt-db3-seal`, HEAD `4add670b6ce766f62ba32f7e108f3f9416d56b21`
(parent `53be872e`, main `295fe151` with PR #465). Registration sha256 verified
`5c224a91b968538f503f1ec8da47b73380c0aac33edcbe5b5b14c5ef4134d426`. Scratch `/tmp/cg-g2a-b3-refuter/`.

## Phase 1: independent findings

Written before any judge output was opened.

### Contamination disclosure

- **Loaded automatically by the session harness, not opened by me:** the user's global
  `~/.claude/CLAUDE.md`, this worktree's `CLAUDE.md`, and the auto-memory index `MEMORY.md` were
  injected into my context at session start. I did not open them. They hold process doctrine and
  checkpoint titles; none holds a block-2 or block-3 count, summary row or selection result. They
  bear on nothing below.
- **Read beyond the charge's list, and why:**
  - `50r-seal-refuter-charge.md` (my own charge) and `50-seal-charge.md` (the unfilled template,
    diffed against the filled charge to see why Q5 says 600 s).
  - `git log`/`git diff` of the design branch and of lane commits `871a43f6..295fe151`, and
    `git show 97ff5035:…/registration_block3.md` (the first draft), to check the design record §3
    claim that the end state predates the blindness slip.
  - `tests/test_controller_retry_backoff.py` (tests are permitted reading).
  - `scripts/issue_g2a_prefill_prompt_pin.py` (grep and lines 162-191, 435-502, 715-730),
    `joulewise/analysis_manifest_v3.py:341-349`, a grep of
    `configs/campaigns/d117_contrast_v5/generate_configs.py`: to test whether §7's end state can
    be executed by the `_v5` code (Q3).
  - Greps over `joulewise/` and `scripts/` for runtime reads of `docs/` or imports from `tests/`
    (Q8), with hits in `scripts/gen_g2_phase_d.py`, `joulewise/night_gate.py`,
    `joulewise/arm_readiness_evidence*.py`; a grep of
    `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md` and a modified scratch copy
    of it (Q8 probe below).
  - `joulewise/controller.py:1060-1175, 2240-2270`; `scripts/harvest_g2a_window.py:160-260`;
    `scripts/select_g2a_prefill_length.py:17-138`; the block-3 policy JSON in full.
  - The w2 session record lines 45-60 and Opus consult lines 9-10 (both listed) for the burst timing.
- **Not opened:** any `summary*`, `counts*`, `*counts-receipt*`, `*resolvability-summary*`, or
  `selection*` file anywhere; nothing under `/Users/edr/night-g2a`, `/Users/edr/night-custody`,
  `/Users/edr/night-archive`; no PR body or comment; no RUN_STATE, TASK_QUEUE, AGENTS, skill file.
  No block-2 or block-3 overlap count is known to me.

### Executed checks

| # | Command (from worktree root, `PY=/Users/edr/code/JouleWise/.venv/bin/python`) | Result |
|---|---|---|
| 1 | `shasum -a 256 configs/campaigns/g2a_prefill_probe_25g83/registration_block3.md` | `5c224a91…d426`, equals the charge |
| 2 | `diff -u registration_block2.md registration_block3.md` | 361-line diff; every change is in the areas the design record names (title/status, §1 change sentence and "Why a block 3", §2 labels, §3 policy and unchecked-contention items, §4 wait and span, §6 attempt-2 sentence, §7 end state, §8/§9/§10 end-state and block-2 clauses, §12 pins and H′ rule) |
| 3 | `git show 97ff5035:…/registration_block3.md` diffed against HEAD | §7 end state byte-identical since 18:27:57, before the 18:29:45 PR #463 read; later edits are 600→300 s, span/window fill, "Why 300 s", and the provenance sentence. Design record §3's timing claim holds |
| 4 | `$PY -B -m pytest -q tests/test_controller_retry_backoff.py tests/test_gen_g2a_window.py tests/test_generate_g2a_probe_inputs.py tests/test_harvest_g2a_window.py tests/test_schemas.py tests/test_run_campaign.py tests/test_select_g2a_prefill_length.py tests/test_summarize_g2a_prefill_probe.py` | **436 passed, 1 skipped**, 132,602 subtests passed (264.9 s) |
| 5 | `$PY -B scripts/gen_g2_phase_d.py --check` | `PASS generated Phase D matches pinned runbook bytes`, rc 0 |
| 6 | `NIGHT_PROGRAMMED_SPAN_S`; `ceil((span+2700)/60)*60` | **18868**, **21600**: equal to §4. Hand arithmetic: 7947.40625+4800+1200+1440+1440+420+1620 = 18867.41 → 18868 |
| 7 | `CampaignPolicy.from_mapping` on both policies | production: `retry_backoff_s=0.0`; block 3: `300.0`; both `on_fail=ABORT`, `retry_attempts=1`, profile PRODUCTION |
| 8 | `diff` of sorted-key JSON of production vs block-3 policy; `git diff --quiet 871a43f6 295fe151 -- …production.json` | only `retry_backoff_s: 300` and `policy_id` differ; production file unchanged by the lane. Text's §3 criteria (p95 ≤ 0.5, ≥ 30 samples, ≤ 1.0 W) match the file |
| 9 | `shasum -a 256` block-3 policy | `04bdbec45cf3b609b33886c1487e9982f030564b3212e636f8cf4631b5d4edc7` (for the seal record) |
| 10 | `from joulewise.reduce import MIN_PHASE_SAMPLES` | 3; selector refuses on drift (`reducer_floor_drift`) |
| 11 | `gen_g2_phase_d.py --emit-chain /tmp/cg-g2a-b3-refuter/chain.zsh …` | `export POLICY=…/quiet_mac_p2_g2a_b3.json` once; `NIGHT_PROGRAMMED_SPAN_S=18868`; `--max-failures 1`; loop `small large` × `512 1024 2048 4096`; no `quiet_mac_p2_production` |
| 12 | **Probe:** scratch copy of `SHAKEDOWN-G2-RUNSHEET.md` with `export SETTLE_S=600` → `60`; `g.RUNSHEET_PATH` pointed at it; `main(["--check"])`; emit chain | `--check` **PASS rc 0**; emitted chain differs from #11 only at `export SETTLE_S=60`. A docs-only edit changes the executed window |
| 13 | Read of selector `select()` | shortest rung with `small_members ≥ 5` and `all_small_count_ge_5`; else 4096 with D-166 two-way wording; matches §8 |
| 14 | Read of harvest verdict block | SELECT iff bracket passed, every row `small_members ≥ 5`, chain exit 0, OFF admitted, no pre-screen stop; member valid iff strict-valid, `succeeded`, anchor `bounded`; large-member validity never gates; matches §6-§7 except finding F4 |
| 15 | Read of controller lines 1106-1135 | wait only when `retry_backoff_s > 0` and attempt 1 not admitted, after the post-capture guard; then guard, attempt 2, abort on second rejection; no third attempt. Matches §4 |
| 16 | grep for runtime `docs/` reads in `joulewise/`, `scripts/` | `gen_g2_phase_d.py` reads `docs/phase_2/window_runbook.md` and the runsheet to render the chain; other hits are record-name strings or off the G2-a path |
| — | Rename behaviour of `git diff --name-only` | NOT EXECUTED (no git writes even in scratch); stated from git's documented rename detection |

### Rulings 1-9

**1. Fixed and unambiguous?** Mostly yes. The SELECT/RECOVER/NULL/REFUSED verdicts are computed by
code that matches the text (checks 13-15). One verdict-level rule a magistrate can apply two ways is
the end-state trigger "a cause named after the first RECOVER is systematic and not removable (for
example most members' clock anchors not `bounded`)". "Systematic", "removable" and "most members"
are judgments with no recorded test. One magistrate arms `b3w2`, another ends the block, from the
same files (F3). A second, smaller one: §4 says a voided retried member makes the window RECOVER.
That is false for a large member (F4).

**2. D-166 carried faithfully?** Yes. The ladder {512, 1024, 2048, 4096}, count ≥ 5 in every one of
≥ 5 small members, reducer floor 3 checked live, 4096 fallback, two-way wording and large
non-gating are all in §1/§8 and in the selector (check 13). Nothing else in D-166 is changed. The
§9 "one step shorter" bullet and the contention item are disclosures, not rule changes.

**3. End state.** Admissible as a prospective amendment of A4's precondition. It is fixed before any
block-3 data, and the text was committed before the design seat's blindness slip (check 3). It
picks D-166's own most-resolvable outcome, and `_v5` prints every member's count with the two-way
wording, so no false energy can enter. Two defects, both fixable in text:

- **F2, not executable as written.** The `_v5` prompt-pin issuer accepts only a selection record
  that equals `select(summary)` (`issue_g2a_prefill_prompt_pin.py:162-191, 443-502`). It does not
  check the harvest verdict. Under the end state no selection record exists, so a code change is
  needed. Until one lands, the only input the issuer accepts is a selector output, and running the
  selector on a RECOVER window's regenerated `derived/summary.json` would make one. If such a window
  had five valid all-≥5 members at a short rung, that record would select the short rung from a
  window §7 forbids as a selection input.
- **F6, wording.** "closed by D-166's exhausted-ladder branch" invites the sentence "no rung
  cleared". Under the end state no rung was evaluated, so that sentence would be false.

**4. Third blind window?** Consistent. Block 2 §7 routed a second RECOVER to a consult and then to the
orchestrator's ruling. Both happened (30-32, record 00 §1). The cause was named: a dasd maintenance
burst plus a 0.5 s retry gap. The code was changed (PR #465), and block 3 is blind to block 2's
counts (§10). "Blind" in the block-2 clause means a re-run with no named cause and no change, and
block 3 is not that. The design seat's read of PR #463's replay outcome came after the end state
and the rest of the rule text were committed (check 3). The 600→300 change was driven by clock
diagnostics, not counts.

**5. Delayed retry.** It does not weaken the bar: same criteria, same guard re-observed after the wait,
one retry, abort on the second rejection (check 15, tests in check 4). It is not re-collection: no
capture is discarded, attempt 1's records stay in the stream, and attempt 2 always existed. It
causes no count-changing selection bias beyond Q6's direction: every rostered member is still run
in fixed order, and the wait only changes when attempt 2 starts. Code matches §4. Production is
byte-identical with backoff 0 (checks 7-8). Arithmetic of "Why 300 s" verified: 683 s × 3.2 ppm =
2.19 ms + 2.31 ms = 4.50 ms; 983 s gives 5.46 ms; tolerance (5 − 2.31)/683 = 3.94 ppm. Burst timing:
start 12:55:00, attempt 1 at 12:55:11 (11 s ✓); attempt 1 ended ≈12:56:54, so a retry at +300 s
starts ≈13:01:54, after the ~13:01 logged end ✓. The margin is thin and rests on one burst. Its
failure costs a window, never a number. **Note:** the charge's Q5 says "a 600 s wait". The
registration, the policy and the code all say 300 s (the charge template was drafted at 18:30,
before the 18:56 change). The ruling should rule on 300 s (F7).

**6. Contention.** The conclusion is right but the physics is incomplete (F5). Background work can
lengthen a prefill phase, which raises a count. On the CPU it can also delay the `powermetrics`
sampler so that records run longer than 100 ms and fewer overlap a phase; that lowers the count.
The D-166 ratification A1 already records that merged records occur. "Never lower it" is therefore
false. The lowering direction can only make a rung fail that a quiet machine would pass, which
pushes toward a longer rung or 4096 (more records). So the safety conclusion survives. No check is
needed to protect a number: the only number at stake is the selected rung. A too-short rung shows
up in `_v5` as printed refusals, which cost resolvable `_v5` members, not truth. The consequence
§9 omits is that cost: fewer resolvable prefill members in `_v5`.

**7. Network time, validity, stop rules, claim boundary, blindness.** §5 is unchanged from block 2
and §6-§7 are unchanged apart from F3/F4. §9 and §10 are sound; §10's extension to block 2 is
right. No change needed beyond those findings.

**8. §12 arm-head rule.** There is a real hole (F1). The chain's executable source is two files under
`docs/`: `docs/phase_2/window_runbook.md` and
`docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`. `gen_g2_phase_d.py` renders
the chain from them (`emit_g2a_night_chain` reads `RUNSHEET_PATH`). Check 12 shows a docs-only edit
that cuts the 600 s settle to 60 s: `--check` still passes, the §12 (iii) exemption admits it, and
the recipe's `docs/*` case passes it. The seal pins `gen_g2_phase_d.py` but not those two documents.
Block 2's H′ rule had no docs exemption, so this hole is new in block 3. Smaller recipe holes:

- `git diff --name-only` uses rename detection by default, so a code file renamed into `docs/` or
  `tests/` lists only its new path. Not executed; from git's documented behaviour.
- `awk '/^## H′ extensions/{x=1} x'` reads to end of file, so any path named in any later section of
  the seal record passes.
- `grep -qF -- "$f"` is a substring test.
- The seal record itself lives under `docs/`, so a light-tier docs commit can add an H′ extension.
  This relies on "gated" in (ii) meaning the code gate. The registration should say so.

**9. Code implements the registration?** Yes on span, window, `POLICY` export, `--check`, selector,
harvest verdict and member validity, policy bytes and controller wait (checks 4-15). There is one
text/code mismatch (F4): §4 says a voided retried member makes the window RECOVER. The controller
records an unbounded anchor without failing the run (`controller.py:2257-2260`), and the harvest
never gates on large-member validity (check 14). So a voided **large** member, which is §4's own
worked case (8B at 4096), leaves the window SELECT-capable. The text should change; the code is
right, because large members never gate.

### Findings

| ID | Severity | Location | Claim | Evidence |
|---|---|---|---|---|
| F1 | **major** | §12 (iii); recipe step2 `case` | A docs-only commit can change the executed chain (settle, stage loop, flags) between seal and arm without a new seal | check 12; `gen_g2_phase_d.py:20-23, 311`; pins list omits the two source docs |
| F2 | **major** | §7 End state | The end state is not executable by current `_v5` code: the issuer requires a selector record and never checks the harvest verdict. This invites making a selection record from a RECOVER window, which §7 forbids and which could select a short rung | `issue_g2a_prefill_prompt_pin.py:162-191, 435-502` |
| F3 | minor | §7 End state trigger; recipe §7 row 2 | "systematic and not removable … most members" is a judgment two magistrates can apply two ways (end the block, or arm `b3w2`) | text |
| F4 | minor | §4 "Why 300 s", last sentences | A voided retried **large** member does not make the window RECOVER; the text says it does | `controller.py:2257-2260`; harvest lines 170-182, 238-251 |
| F5 | minor | §3 last bullet; §9 third bullet | "can raise a count, never lower it" is false (sampler delay merges records). The conclusion survives because lowering is conservative | physics; D-166 ratification A1 |
| F6 | minor | §7 End state, first sentence | "exhausted-ladder branch" invites the false paper sentence "no rung cleared" | text |
| F7 | nit | charge Q5 | The charge says 600 s; registration/policy/code say 300 s | check 3; `50-seal-charge.md` 18:30 vs `87d68ba7` 18:56 |
| F8 | nit | recipe step2 | rename detection; `awk` reads to end of file; `grep -F` substring | recipe lines 230-235 |
| F9 | nit | §3 policy item | "the GPU idle check" is not a policy field, and the environment-guard list omits `require_external_connected` and `require_low_power_mode_off` (unchanged values, so no rule effect) | policy JSON |

### Required text changes I would impose (old → new; whitespace-collapsed match)

- **R1 (F1), §12 pinned list.** Old: "`configs/model_panels/qwen3_4bit.json`, the D-166 registration
  file and the acceptance file." → New: "`configs/model_panels/qwen3_4bit.json`,
  `docs/phase_2/window_runbook.md` and `docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`
  (the chain's executable source, from which `scripts/gen_g2_phase_d.py` renders the chain), the
  D-166 registration file and the acceptance file."
- **R1, §12 (iii).** Old: "(iii) commits that change only files under `docs/`, `tests/`, or the files
  `RUN_STATE.md` and `TASK_QUEUE.md`; the arm checks (iii) with `git diff --name-only H H′`." → New:
  "(iii) commits that change only files under `docs/` (except the two chain-source documents pinned
  above), `tests/`, or the files `RUN_STATE.md` and `TASK_QUEUE.md`; the arm checks (iii) with
  `git diff --no-renames --name-only H H′`. A fix under (ii) passes the same gate as code, whatever
  directory it touches."
- **R1, recipe step2** (mechanical form):
  - Add `docs/phase_2/window_runbook.md|docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md`
    as a case arm *before* `docs/*` that falls to the H′-extension test.
  - Use `git diff --no-renames --name-only`.
  - Make the awk stop at the next heading: `awk '/^## H′ extensions/{x=1;next} /^## /{x=0} x'`.
  - Use `grep -qxF` against one-path-per-line entries.
- **R2 (F2), §7 End state.** Old: "The stop and the end state are reported to Ed by email." → New:
  "The stop and the end state are reported to Ed by email. The end-state binding is made by a gated
  change to the `_v5` prompt-pin issuer (`scripts/issue_g2a_prefill_prompt_pin.py`, which today
  accepts only a selection record). The change adds one branch that accepts exactly this
  registration's sha256 and the block's `harvest.json` records, each with verdict RECOVER, and
  emits 4096. The selector is never run on the summary of a window that did not reach SELECT, and
  no selection record from such a window is ever an input to the issuer."
- **R3 (F3), §7 End state trigger.** Old: "or a cause named after the first RECOVER is systematic and
  not removable (for example most members' clock anchors not `bounded`)," → New: "or the cause
  named after the first RECOVER is one the recovery window would meet unchanged and that no change
  allowed by §12 can remove, as recorded with its evidence in the session record and agreed by a
  blind consult of Sol 6.1 and Opus (for example more than half of the window's captured
  small-model members with a clock anchor status other than `bounded`); if the two seats disagree,
  the recovery window is armed,". Mirror this in recipe §7 row 2.
- **R4 (F4), §4.** Old: "it is then invalid (§6), never admitted, and the window is RECOVER." → New:
  "it is then invalid (§6) and never admitted. A voided small-model member leaves its rung short
  and the window is RECOVER; a voided large-model member is recorded invalid and, like every
  large-model result, does not gate (§7)."
- **R5 (F5), §3 last bullet.** Old: "Registered as an unchecked condition because its only possible
  effect on this block's output is to lengthen a prefill phase, which can raise a member's record
  count, never lower it; §9 states what that means for the use of the result." → New: "Registered as
  an unchecked condition. Such work can lengthen a prefill phase, which can raise a member's record
  count. It can also delay the power sampler so that records run longer than 100 ms and fewer
  overlap the phase, which can lower the count. A lowered count can only make a rung fail that a
  quieter machine would pass, which pushes the selection to a longer rung with more records. §9
  states what a raised count means for the use of the result." In §9 third bullet, after "never as
  an energy", add: "; its cost is fewer resolvable prefill members in `_v5`, not a false number".
- **R6 (F6), §7 End state.**
  - Old: "the prefill-length question is closed by D-166's exhausted-ladder branch without a further
    probe:" → New: "the prefill-length question is closed at D-166's fallback length without a
    further probe (no rung was evaluated, so this is not D-166's finding that no rung clears):".
  - Old: "and the paper states that the length was fixed by this end state, not selected by a
    probe." → New: "and the paper states that the length was fixed by this end state, not selected
    by a probe, and never states or implies that a shorter rung was tested and failed."

None of F1-F9 is a REFUSE defect on its own: each is fixable by verbatim text, and none
lets the block as armed at a clean H select a wrong rung. F1 and F2 are the two a ruling must not
omit, because each leaves a route by which a wrong rung or a changed window shape could be
reached without a new seal.

## Phase 2: on the ruling

Ruling read: `51-seal-ruling.md`, 618 lines, first line `SEAL: ADMIT`, file stable at 49,776 bytes
over 60 s (20:11-20:12 PDT). Before Phase 2 I had opened nothing of it.

**Phase-1 disclosure addendum.** A grep of the listed `w2` session record (line 11) showed me the
courier's per-rung member success tallies ("p512 5/5 ok, p1024 5/5 ok, …"). These count members
that ran, not overlap counts or summary rows. No ruling here depends on them.

### Checks run on the ruling

| # | Check | Result |
|---|---|---|
| P1 | Python: each "Old" block of T1-T5 and R1 counted in the registration or recipe | each occurs exactly once in its file; R2's old sentence occurs once in the recipe (`grep -c` = 1) |
| P2 | Scratch `/tmp/cg-g2a-b3-refuter/r1/`: the judge's R1 `case` run against a seal record laid out as block 2's was, with a pins table, then `## H′ extensions` / `none`, then an H′ pins table appended below, as block 2's 52 record says ("Later windows append their H′ pins below") | **`PASS scripts/harvest_g2a_window.py`** and **`PASS docs/…/SHAKEDOWN-G2-RUNSHEET.md`**, although neither is a listed extension. Only files missing from every table after the heading are refused |
| P3 | The same files through a heading-bounded, one-path-per-line, exact-match form (D1 below) | both refused; an explicitly listed extension `- \`joulewise/controller.py\`` passes; a path mentioned in a later section is refused |
| P4 | `anchor_status` in `harvest_g2a_window.py:36-43` | returns the literal `not recorded` when absent, so T1's test reads a field the harvest really writes |
| P5 | `issue_g2a_prefill_prompt_pin.py:160-172, 430-480` | the issuer takes any summary/counts receipt plus a selection that equals `select(summary)`, with the selection under the window-plan root. It never reads a `harvest.json` verdict |

### Where the ruling is right and I concede

- **T3 is better than my R5 addendum.** The ruling is right that D-166 attaches the two-way wording
  only to the 4096 fallback, and that at a selected rung a `_v5` member with 3 or 4 records has a
  valid reducer energy. The draft's §9 sentence promised a protection that does not exist. My
  Phase-1 Q6 answer accepted it and only added the cost. I missed that.
- **T1** (mechanical clock trigger, "borrows the outcome … is not that branch") covers my F3 and F6.
  **T2** covers my F5. **T4/R1** has the same diagnosis as my F1, reproduced independently with the
  same `SETTLE_S=60` probe. **F5** (end-state binding has no code path) is my F2's first half.
- My `--no-renames` point is withdrawn as a defect. With rename detection, the *new* path is
  listed, so a rename onto a pinned path is caught. A rename *away* from a pinned path makes the
  generator or importer fail closed.
- The ruling's decision-log sentence (ruling 3) matches T1's trigger and the registration's
  capture rule.

### Defects in the ruling (findings, with the changes I require)

| ID | Severity | Location | Claim | Evidence |
|---|---|---|---|---|
| D1 | **major** | Ruling §5 R1 (recipe step2); ruling F9 rated "nit, optional" | R1's cure for F1 is defeated by ordinary use of the seal record. Its `awk '/^## H′ extensions/{x=1} x'` reads to the end of the file, and `grep -qF` is a substring test. §12 requires the seal record "extended with the H′ pins before each arm", and block 2's record appended those pin tables, which name every pinned file, below its pins section. Once such a table sits after the H′ heading, every pinned file passes, including both chain-source documents. F1 then reopens for the recovery window `b3w2`, the one window that always arms from an H′ | P2, P3 |
| D2 | major (desk-day, end-state path) | Ruling F5, "fails closed today" | The end-state binding fails closed, but the existing issuer path does not: it accepts a selection record computed from a non-SELECT window's chain-written summary. Example: a RECOVER from a clock-voided small member after a chain exit 0, where the chain's own copy still counts all five. Under the end state that is the easiest way to obtain a pin, and it could carry a short rung or a "no rung qualifies" record, which T1 now forbids in words only | P5 |
| D3 | minor | Registration §4 "Why 300 s" last sentences; ruling 5 risk (b) repeats it | "a retried member … is then invalid (§6), never admitted, and the window is RECOVER" is false for a large member, which is §4's own worked case (8B at 4096). The controller records a non-`bounded` anchor without failing the run (`controller.py:2257-2260`), and the harvest never gates on large-member validity. No wrong rung and no wasted window: the code is right and the text is wrong. The ruling missed this text/code mismatch, which charge item 9 asks for | Phase-1 F4 |
| D4 | minor | Ruling T1 "which re-arming cannot remove" | A majority of non-`bounded` anchors could come from a removable code defect, for example a regression at H′. T1 then ends the block by rule and gives up a selection that a fix could have produced. This costs only a selection, never a number or a window, and the mechanical trigger is worth that cost. No change required; the seal record should note the trade | T1 text |
| D5 | nit | Registration §3 policy bullet | "the GPU idle check" names no policy field, and the environment-guard list omits `require_external_connected` and `require_low_power_mode_off`. Values are unchanged, so no rule effect. Not addressed by the ruling | Phase-1 F9 |

**Required changes (apply with T1-T5 and R1-R2, verbatim; old → new):**

- **D1, recipe step2, replacing the ruling's R1 "New" block.** Old (the ruling's R1 New):
  ```
      docs/phase_2/window_runbook.md|docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md)
        awk '/^## H′ extensions/{x=1} x' "$SEAL_RECORD" | grep -qF -- "$f" \
          || { echo "H changes a pinned chain-source document outside registration §12: $f"; exit 3; } ;;
      docs/*|tests/*|RUN_STATE.md|TASK_QUEUE.md|configs/calibration/calibration_ledger_head.json) ;;
      *) awk '/^## H′ extensions/{x=1} x' "$SEAL_RECORD" | grep -qF -- "$f" \
           || { echo "H differs from SEAL_H outside registration §12: $f"; exit 3; } ;;
  ```
  New:
  ```
      docs/phase_2/window_runbook.md|docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md)
        awk '/^## H′ extensions[[:space:]]*$/{x=1;next} /^#/{x=0} x' "$SEAL_RECORD" | sed -n 's/^- `\(.*\)`$/\1/p' | grep -qxF -- "$f" \
          || { echo "H changes a pinned chain-source document outside registration §12: $f"; exit 3; } ;;
      docs/*|tests/*|RUN_STATE.md|TASK_QUEUE.md|configs/calibration/calibration_ledger_head.json) ;;
      *) awk '/^## H′ extensions[[:space:]]*$/{x=1;next} /^#/{x=0} x' "$SEAL_RECORD" | sed -n 's/^- `\(.*\)`$/\1/p' | grep -qxF -- "$f" \
           || { echo "H differs from SEAL_H outside registration §12: $f"; exit 3; } ;;
  ```
  Also, for the seal record: the `## H′ extensions` section holds only lines of the exact form
  ``- `path` `` (or the single word `none`). It is placed after the pins table, and **H′ pin tables
  are never written inside it**; they go under their own `## H′ n pins` headings.
- **D2, seal record, F5 obligation** (wording for the desk-day item). The desk-day change to
  `scripts/issue_g2a_prefill_prompt_pin.py` must do both of the following, by a gated PR:
  - (a) accept a selection record only when its sha256 equals `selection.sha256` in a block-3
    `harvest.json` with verdict SELECT;
  - (b) under the end state, accept exactly the registration sha256 and the block's RECOVER
    `harvest.json` records and emit 4096, with no selection record and no "no rung qualifies"
    condition.

  Until it lands, no `_v5` pin is issued from any block-3 window.
- **D3, registration §4.** Old: "it is then invalid (§6), never admitted, and the window is
  RECOVER." → New: "it is then invalid (§6) and never admitted; a voided small-model member leaves
  its rung short and the window is RECOVER, while a voided large-model member is recorded invalid
  and, like every large-model result, does not gate (§7)." (The "old" string occurs once in the
  registration, lines 166-167, whitespace-collapsed.)

### Verdict reasoning

The ruling's facts check out wherever I could test them (P1, P4, and Phase-1 checks 4-16 repeat
its checks 3-14 with the same numbers). Its required changes do not make any rule ambiguous or
any selection wrong. D1 is a defect in the cure for F1, not a new way to a wrong rung. It needs a
second unsealed change to land on main, and it is fixable in place. D2 needs a seat to break §7
and T1 in words. D3 is text only. By the AGREE definition (no defect in the ruling that lets the
block select a wrong rung, waste a window by rule, contradict D-166 outside the end state, or make
the end state unsound), I agree, provided D1-D3 are applied with T1-T5 and R1-R2.

### Plain summary

The cold judge admitted block 3 with five text changes and two recipe changes. I checked them and agree: they are correct, they apply cleanly, and the end state (4096 by default if the probe fails twice more) is a sound, pre-committed amendment of D-166.
One of the judge's fixes doesn't hold up in practice: the arm-time check that stops unsealed edits to the chain's source documents would wave them through once the seal record carries the H′ pin tables its own rules require. D1 replaces it with an exact, heading-bounded match.
Two smaller repairs: the `_v5` pin issuer must only accept a selection from a SELECT window (D2, desk day), and §4 must stop saying that a clock-voided large-model member makes the window RECOVER (D3).
