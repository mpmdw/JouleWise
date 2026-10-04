# Registration G2A-25G83-B3: the G2-a prefill resolvability probe on macOS build 25G83 (measurement block 3), with its analysis plan

Status: DRAFT for the cold registration gate G2A-25G83-B3. Written 2026-10-03 by the block-3 design
seat (Opus 5.5, headless orchestrator seat holding the orchestrator's design authority, RUN_STATE
item 7), from the sealed block-2 registration
`configs/campaigns/g2a_prefill_probe_25g83/registration_block2.md` and the orchestrator's ruling
under its §7 (`docs/process_traces/2026-10-03-design-block3/00-design-record.md` §1). Every rule
below is fixed before any data of this block exists. No count, energy or other result measured
by block 2 or block 3 appears in this file or may be added to it; block 2's clock diagnostics are
used by reference only (§4 item 3).

## 1. What this block measures, and why it is needed

**The physical question.** The Mac's power instrument (`powermetrics`) reports power as a series
of records, one every 100 ms. A language model's *prefill* phase (reading the whole prompt before
writing the first output token) can be shorter than a few records when the prompt is short. The
reducer that attributes energy to a phase (`joulewise/reduce.py`) needs at least
`MIN_PHASE_SAMPLES` = 3 power records that overlap the phase in time; with fewer it reports the
phase as `not_resolvable_sample_count` instead of an energy. Paper B (the phase-energy capstone on
the pinned Qwen3 1.7B and 8B pair, campaign generation `_v5`) needs a prefill prompt length long
enough that the small model's prefill is reliably resolvable, and no longer than necessary.

**The rule that uses this block (already fixed, D-166 as amended 2026-08-30).** The `_v5` prefill
length is the shortest of 512, 1024, 2048 and 4096 prompt tokens at which every one of at least
five Qwen3-1.7B probe members shows a prefill overlapping-power-record count of at least 5 (the
reducer floor of 3 plus a declared safety margin of 2). A rung with fewer than five valid
small-model members cannot be selected. Qwen3-8B probes are recorded and never gate. If no rung
qualifies, the prefill arm is still collected at 4096 and the printed result separates the two
refusals (count below 3: the reducer's refusal, printed as itself; count 3 or 4: "below the
pre-registered count floor of 5", with the reducer's resolvable result disclosed alongside).
Source: `docs/decision_log.md` D-166 index row and
`docs/process_traces/2026-08-30-prefill-margin-coldgate/` records 01-03. This registration changes
that rule in one place only, §7 "End state", which says what happens if this block also ends
without a complete sweep; the cold gate that seals this file rules on that clause as a prospective
amendment of D-166's precondition. Everything else D-166 leaves to the window (operating
condition, window shape, validity, number of windows, stop rules, use of the result) is fixed
here.

**Worked example of the count.** A Qwen3-1.7B prefill that lasts 0.33 s can overlap 4 records
(for instance records covering 0.00-0.10, 0.10-0.20, 0.20-0.30 and 0.30-0.40 s when the phase runs
from 0.05 to 0.38 s); it is reducible (4 ≥ 3) but does not qualify (4 < 5). A prefill lasting
0.45 s overlaps at least 5 records (with records exactly 100 ms long) and qualifies. The probe
measures this count directly at each rung; nothing about energy is used.

**Why a block 3.** Block 2 (sealed 2026-10-02) stopped under its §7 without a complete sweep. Its
first window `w1` lost its data to a code defect (fixed by PR #461). Its recovery window `w2`
stopped when one small-model member failed the idle-admission screen twice: both attempts fell
inside a macOS maintenance burst of about six minutes, and the one retry starts about half a second
after the first attempt, so it cannot outwait such a burst. The orchestrator's ruling under block
2 §7 (record 00 §1, after a blind consult of Sol 6.1 and Opus 5.5) closes block 2 and opens this
block with one change to the window: the retry waits 300 s first (§4). Block 2's own text says a
second incomplete sweep "never goes to a third blind window"; this block is not a third block-2
window but a new registration, written after the cause was named and the code changed, and blind
to block 2's partial data (§10).

## 2. The block

One **G2-a window** (label `b3w1`), plus at most one **recovery window** (label `b3w2`) under §7.
Queue row `V5-G2A-PREFILL-PROBE-01`. Receipt class `DIAGNOSTIC_NO_PACK` (no `_v5` pack exists or is
touched). Window plan ids have the form `d117-g2a-prefill-probe-<t0 UTC as YYYYMMDDTHHMMZ>`; each
window has its own t0 and therefore its own id, distinct from block 2's two ids. The night gate's
registration for the plan is the D-166 registration file
`configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` (sha256
`dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265`, in
`joulewise/night_gate.py` `RULED_REGISTRATIONS`); this file is bound to the window by its sha256 in
the arm record and the seal record (§12).

## 3. Operating condition (each item is checked by code at arm or at t0, except the last)

- **Machine.** The one M3 Max (model identifier Mac15,9), macOS build 25G83, on AC power with the
  battery at float, power mode `ac_high_power`, `powermetrics` sample interval 100 ms. Agent-free
  during the window: no `claude`, `codex`, `t3` or MCP process alive from t0 to the chain's exit.
  The night gate's census and the clean dwell check this at the start; the magistrate's
  stand-down (no seat alive past t0 − 8 min) and the arm notice's `/exit` instruction to Ed keep it
  true afterwards.
- **Calibration acceptance in force.** `d079_calibration_acceptance_v2_n24_25g83_r2`, file
  `configs/calibration/calibration_acceptance_d079_v2_n24_25g83_r2.json`, sha256
  `f949f511254e03b50b0be1cea37f74c1e8e6b4c49926c6c197024beea07b3660` (issued by PR #457, merge
  `6857428d`). It is the live default; the window's brackets are judged against it and against no
  other file.
- **Models.** `mlx-community/Qwen3-1.7B-4bit` (small, gating) and `mlx-community/Qwen3-8B-4bit`
  (large, non-gating), at the revisions and file hashes pinned by the panel file
  `configs/model_panels/qwen3_4bit.json` at the arm head H; tokenizer bytes as pinned there.
- **Probe inputs.** Built by `scripts/generate_g2a_probe_inputs.py build-probes --small-members 5
  --large-members 1` at H: for each rung, raw prompt text (no chat template, so the thinking switch
  is never rendered) built from one fixed seven-token sentence repeated a whole number of times
  plus the rung's fixed closing sentence, re-tokenized and refused unless its count equals the
  rung exactly; greedy decoding (the runtime adapter's fail-closed default, hash-bound in the
  input inventory); 75 s idle before each member; the producer's fixed output budget. These are
  the same prompt bytes and configs as block 2. Every config, the panel file, the campaign policy
  and the runtime adapter are bound by sha256 in the G2-a input inventory, which
  `generate_g2a_probe_inputs.py check` re-authenticates inside the chain before anything is
  reserved.
- **Campaign policy.** `configs/campaign_policies/quiet_mac_p2_g2a_b3.json` (sha256 in the seal
  record), bound into the input inventory by `bind-window` and passed to every probe stage. It is
  the production policy `configs/campaign_policies/quiet_mac_p2_production.json` with two fields
  changed: `policy_id` = `quiet-mac-p2-g2a-b3`, and `idle_admission.retry_backoff_s` = 300 (§4).
  Every admission criterion is the production value: CPU busy ratio p95 ≤ 0.5 over at least 30
  records, processor combined power p95 ≤ 1.0 W, the GPU idle check, the environment guard
  (AC power, displays asleep, screensaver disengaged, thermal nominal), exactly one retry, abort
  on the second rejection.
- **Chain.** The zsh chain emitted at H by the recorded G2-a window command of
  `scripts/gen_g2_phase_d.py`, with its pre-calibration screen literal derived from the acceptance
  above by the writer's own derivation and checked two ways by `gen_g2_phase_d.py --check`, and
  its `POLICY` export naming the campaign policy above. Its sha256 sidecar is pinned in the plan.
- **Network time.** §5.
- **Ledger.** The measurement clone's calibration observation ledger is restored byte-exact from
  the retained ledger whose head equals the committed pin
  `configs/calibration/calibration_ledger_head.json` at the arm head. At this writing that is
  block 2 `w2`'s re-harvest terminal ledger
  (`/Users/edr/night-archive/harvest-d117-g2a-prefill-probe-20261003T1748Z-r2/derived/terminal-ledger.jsonl`,
  file sha256 `84bb9aee4a9358c13491832e12e9e504c02fb838d1a167974a235e8d2942475b`, 392 records,
  pin sequence 392, merged by PR #464). Every harvest of a window whose chain opened a bracket
  session advances the pin. Once such an advance is merged (always the case for a recovery
  window), the source is that harvest's archived `derived/terminal-ledger.jsonl`, whose head
  equals the merged pin; the arm record names the source path and its sha256. Using the source
  this rule names is not a change to this section. A ledger that fails custody audit or does not
  match the pin refuses the arm.
- **Not checked: background work during a measured window.** Admission screens the 75 s idle
  baseline just before each member; work that starts during a member's measured window is not
  screened. Registered as an unchecked condition because its only possible effect on this block's
  output is to lengthen a prefill phase, which can raise a member's record count, never lower it;
  §9 states what that means for the use of the result.

A change to any item in this section after the seal voids the seal for windows not yet armed; a
new seal is required.

## 4. Window shape

In order, inside one chain run under the unattended night driver:

1. **Start conditions (physics only, no calendar gap).** The driver issues the network-time OFF
   receipt at t0 and runs the 600 s clean dwell (`scripts/prewindow_check.sh`) while the receipt
   settles; the night gate then checks census, AC power, battery float, display, load average and
   thermal state. The chain starts no earlier than 600 s after the receipt on both clocks and no
   later than `t0 + window_max_s − NIGHT_PROGRAMMED_SPAN_S`. The chain is authored, with its plan
   and sha256 sidecar, by `scripts/gen_g2_phase_d.py --new-g2a-window` and nothing else.
2. **Pre bracket.** A 600 s settle, then one governed pulse calibration (59 pulses, protocol
   `powermetrics_pulse_fiducial_v3`) in the window's bracket session, then the pre-calibration
   screen: the capture's fiducial bound must not exceed the screen derived from the acceptance in
   force (runbook §5B logic, D-079 clause 3). A screen failure stops the chain before any member.
3. **Probe stages.** Eight stages in this fixed order: small-p512, small-p1024, small-p2048,
   small-p4096, large-p512, large-p1024, large-p2048, large-p4096; each stage is a 600 s settle,
   then `scripts/run_campaign.py` on that stage's config (5 members for small stages, 1 for large),
   `--arm-quiet-mode --max-failures 1`, with the campaign policy of §3.
   **Idle admission of each member (the one change from block 2).** The member's 75 s idle
   baseline is attempt 1. If attempt 1 is rejected, the controller waits 300 s
   (`retry_backoff_s`), during which nothing new is measured or admitted and the running power
   sampler's records are retained unchanged in the member's raw stream; then it observes the
   environment guard again and runs attempt 2, the one retry, under the same criteria. If attempt
   2 is also rejected, the member aborts, `--max-failures 1` stops the campaign and the chain, and
   the window is RECOVER (§7). The wait is the same for small and large members. It is a pause
   inside one member's own admission, before its prefill; it does not re-run a member, re-collect
   a rung or replace any capture (§7).
   *Why 300 s.* One power sampler runs from the start of attempt 1 to the end of the member's
   measured window, and the clock-step test of §5(b) fits every record of that stream. The active
   test refuses a capture when the clock anchor's effective bound (its half-width plus the
   wall-minus-monotonic span that clock drift builds up over the stream) exceeds 5 ms, so a wait
   that makes the stream too long voids the member. The wait was sized against the worst-case
   retried member (Qwen3-8B at 4096 tokens, decoding at the code's worst-case 5 tokens/s, guards
   near their timeouts: about 683 s of stream at 300 s) using block 2's member clock records
   (instrument diagnostics, not results of the probe; their drift, widest half-width and idle
   attempt duration are the inputs of `tests/test_controller_retry_backoff.py` at H). At 300 s
   that member stays inside the 5 ms bound; at 600 s it would not. If the drift during this block
   is well above block 2's, a retried member can still be voided; it is then invalid (§6), never
   admitted, and the window is RECOVER. 300 s also outlasts the one burst on record: it started
   about 11 s before the failed member's first attempt and lasted about six minutes; a retry 300 s
   after that attempt ended would have begun about 30 s after the burst's logged end.
4. **Post bracket.** One governed pulse calibration in the same bracket session.
5. **Terminal boundary.** The ledger session is finalized; the chain records the terminal head
   candidate (`physical_ahead`) and stops with the tracked pin unchanged. The counts receipt and
   the four-row summary are written by `scripts/summarize_g2a_prefill_probe.py`.

`window_max_s` = `NIGHT_PROGRAMMED_SPAN_S` (the literal the generator writes into the chain from
the code constants, including its declared allowance for model load and inference and for four
delayed retries of 300 s each plus their attempt-2 capture; 18,868 s at lane
G2A-B3-RETRY-BACKOFF-01) + 2700 s (the clean dwell's own cap), rounded up to a whole minute
(21,600 s at that span). If the chain runs past `t0 + window_max_s`, the driver's window
expiry stops it and the window is RECOVER (a stopped chain cannot leave a complete sweep with a
passed post bracket). Nothing in the window may be shortened, skipped, reordered or repeated at
arm or at run time.

## 5. Network time (Ed, 2026-10-02: the point is that network time is off so syncing cannot interrupt a capture)

Registered as the physical state, in two parts:

- **(a) The state.** Network time is OFF at t0, shown by the window's one write-once receipt from
  the driver's setter run (`sudo -n /usr/sbin/systemsetup -setusingnetworktime off`) with exit 0
  and standard output stating the OFF end state in either macOS wording, recognized exactly as
  erratum E-NT1 to Revision 6 reads it (whitespace-collapsed, trimmed, trailing periods removed,
  case ignored: `setUsingNetworkTime: Off` or `Network Time is already off`; any other statement,
  empty output, an ON statement or the administrator-access text refuses), taken on the same boot
  as the first capture and at least 600 s before it on both the wall clock and the monotonic
  clock. Nothing turns network time ON during the window. No exact-stdout comparison is
  registered.
- **(b) The clock-step test.** Binding: every capture (both brackets and every member) passes the
  estimator's existing within-capture clock-movement admission (the wall-minus-monotonic span and
  rate limits in `joulewise/uncertainty_evidence.py`, unchanged); a capture refused by it, or with
  an empty clock fit, is invalid. Reported, not binding: for each capture whose records and the
  receipt share a monotonic source, the difference between the receipt's wall-minus-monotonic
  offset and the capture's, flagged above 0.015 s. Why the second part is report-only: this
  window's output is a count of power records overlapping a phase inside one capture, and each
  capture's internal time alignment is exactly what the binding part protects; a clock step
  between two captures cannot change any count, so voiding on it would protect no number. A flag
  goes into the harvest record and to the orchestrator as evidence that the OFF state did not hold.

## 6. Validity

- **Bracket.** The pre and post calibrations pass when the existing bracketing decision
  (`joulewise/calibration_bracketing.py`, against the acceptance in force) admits both: each slot
  authenticated, bound to this window's session and plan, in family (the pre-screen for the pre
  slot), the pre-to-post drift within the acceptance's drift rule including its registered
  allowance, and the acceptance still fresh. A bracket that does not pass leaves the window
  incomplete (§7). The ledger's `physical_ahead` terminal state is the expected hand-back
  boundary, not evidence that the bracket passed.
- **Member.** A member is valid when all of these hold: its `summary_metrics.json` status is
  `succeeded`; its bundle passes strict validation from its raw evidence (`joulewise/cli.py`
  strict validator, re-reducing raw artifacts); and §5(b)'s binding part passes, read as
  `uncertainty_evidence.clock_anchor.status` equal to `bounded` in the member's `metadata.json`
  (any other status, or no such record, makes the member invalid). A member admitted on attempt 2
  after the §4 wait is judged by exactly the same rules as one admitted on attempt 1. Enclosure by
  the window's pre and post brackets is judged once for the window, over its valid members: a
  failure makes the window RECOVER (§7), it does not make one member invalid. A member whose
  prefill phase overlaps fewer than 3 records is VALID: its reducer outcome
  `not_resolvable_sample_count` is a result, and its count is recorded. Validity never depends on
  the member's count or on any energy; in particular the reducer's per-phase eligibility flag,
  which a low count turns off, is not a validity test.
- **Rung evaluable.** A small-model rung is evaluable when it has at least 5 valid members. The
  configured roster has exactly 5 small members per rung, so a rung is evaluable only when all
  five are valid.

## 7. Counting, verdicts, stop rules and the end state

The harvest (`scripts/harvest_g2a_window.py`) writes one mechanical verdict per window:

- **SELECT**: the chain exited 0, the OFF receipt of §5(a) is admitted by the harvest, both
  brackets pass and all four small-model rungs are evaluable. The window is *complete*; the
  analysis plan (§8) runs on it. The block ends.
- **RECOVER**: the chain started and the window is not complete (a pre-screen stop, a bracket
  failure, any small-model rung with fewer than 5 valid members, a nonzero or missing chain exit,
  an OFF receipt the harvest does not admit). A large-model stage that fails stops the chain
  before the post bracket, so it also ends RECOVER: the large model never gates the selection
  rule of §8, but its four stages are part of the one chain. The harvest names the cause codes.
- **NULL**: the chain never started (`night/chain.started` absent: night-gate refusal, OFF receipt
  failure, clean dwell timeout, admission budget exceeded). This is a **null window**: it is not a
  sweep and consumes nothing in this section.
- **REFUSED**: the harvest itself could not archive or authenticate (a tooling fault). It is fixed
  through the standing refusal route (R3) and the harvest re-run; it is never a science outcome.

A null window is re-armed with a new plan id after its named cause is gone, under the standing
re-arm rules; the same refusal reason code in the driver's result record twice in a row sends the
next step to a consult (Sol 6.1 plus Opus), not a third arm.

A RECOVER window whose chain made no capture (in the harvest's archive copy of the probe root, no
file named `powermetrics*.plist` in any `raw/` directory under `runs/`) took no data; for the
allowance below it counts like a null window. After any other **RECOVER**, at most one recovery
window runs: a fresh, complete sweep with its own plan id, bracket session, probe root and inputs
regenerated by the same producer command (same prompt bytes, same configs), armed only after the
cause is named and, where it can be removed (a code defect, a machine state), removed. The first
window to reach SELECT supplies the selection input; members are never pooled across windows or
blocks, never topped up, and no member or rung is ever re-collected inside a window (D-078). The
§4 wait inside one member's admission is not a re-collection: the member, its run id and every
capture it made stay as they are, and attempt 2 is the retry the policy always allowed.

**End state (pre-committed; the one change to D-166, ruled by this block's seal).** If the
recovery window also ends RECOVER, or a cause named after the first RECOVER is systematic and not
removable (for example most members' clock anchors not `bounded`), the block stops, and the
prefill-length question is closed by D-166's exhausted-ladder branch without a further probe:
the `_v5` prefill arm is collected at 4096 prompt tokens, every `_v5` member's prefill count is
printed with D-166's two-way refusal wording (count < 3: the reducer's refusal; count 3-4: "below
the pre-registered count floor of 5", with the reducer's resolvable result disclosed alongside),
and the paper states that the length was fixed by this end state, not selected by a probe. The
`_v5` pre-registration object then binds, in place of a selection record, this registration's
sha256 and the sha256s of the block's harvest records (`harvest.json` of each window). A null
window, or a RECOVER window that made no capture, never triggers the end state. The stop and the
end state are reported to Ed by email. Why this is fixed now: 4096 is the outcome D-166 already
prescribes when no rung qualifies, and it is the longest, most resolvable rung; fixing it before
data prevents a third probe block, and the `_v5` per-member printing keeps any shortfall visible.

## 8. Analysis plan

- **Input.** Only the four-row summary and counts receipt that the harvest regenerates from the
  SELECT window's raw bundles, counting valid members only (§6). The copy of those two files that
  the chain wrote is a check, not an input. When every roster member is valid, the regenerated
  bytes must equal the chain's copy; a difference is REFUSED (a tooling fault). When the harvest
  found a member invalid, the two differ by construction; the harvest records the difference and
  the verdict follows §7 from the regenerated summary (RECOVER if a small-model rung is left with
  fewer than 5 valid members, otherwise unaffected).
- **Computation.** `scripts/select_g2a_prefill_length.py` on that summary, unmodified: the rule
  is shortest qualifying rung, where a rung qualifies when it has at least 5 small-model members
  and every one of them has an overlapping-record count of at least 5; the reducer floor is read
  from the live `MIN_PHASE_SAMPLES` and must equal the pre-registered 3 (the selector refuses
  otherwise). If no rung qualifies: the selected length is 4096, with the D-166 two-way refusal
  wording printed per member class (count < 3, count 3-4).
- **Output.** One selection record (path and sha256), produced by the selector. The orchestrator
  records the path and sha256 in the session record and RUN_STATE; the selected rung is a protocol
  parameter and is recorded with the selection record's path. The desk day's `_v5`
  pre-registration object binds the selection record's sha256 (D-166: "the G2-a record hash it
  selected from"). Under the §7 end state there is no selection record and no computation; the
  output is the end-state binding of §7.
- **Nothing else is computed.** No energy, power, duration, ratio or statistic of any member is
  computed, summarized, compared or reported by this block. Large-model counts are recorded in the
  summary and are not used by the rule.

## 9. What this block may and may not be used for

- It licenses exactly one thing: the `_v5` prefill length (selected, or 4096 under D-166's
  fallback or under the §7 end state) at the desk day.
- It is not a claim. It licenses no energy number, floor, minimum detectable effect, comparison,
  dominance sentence, difficulty statement or phase-attribution validation.
- Because background work during a measured window is not screened (§3), a member's count could
  be higher than the same member would show on a quieter machine, so a selected rung could be one
  step shorter than a quieter probe would select. The selection is used only as a protocol
  parameter; `_v5` members are collected under the same admission and print their own counts
  with D-166's wording, so a shortfall at the selected rung is reported as a refusal, never as an
  energy.
- Its member bundles, campaign log, configs, counts receipt and summary are diagnostic. They are
  never members of G2-b, the `_v5` transaction, any floor, mint or calibration corpus, and never
  enter any claim path. They are retained unchanged.
- Its two bracket captures per window are ordinary calibration-ledger observations, governed by
  the issued acceptance's own rules; this registration changes none of those rules.
- It does not authorize G2-b, the `_v5` transaction or any claim-bearing window. Those need their
  own gates; the pre-arm triple audit (#416, amended: before any claim-bearing run) applies before
  the first claim-bearing window, at a head containing this block's controller change, not to
  this diagnostic block.
- Block 2's member bundles, counts and summaries are never a selection input for this block or for
  `_v5`, and are never pooled with this block's members.

## 10. Blindness

The harvest prints paths, shas, member counts (how many members, not their record counts) and the
verdict, never an energy, a fiducial bound, a drift value or a per-member overlap count; those stay
in the archived files. The verdict and the selection are computed by code from fixed rules. No
person or agent reads a per-member overlap count, or a row of any window's summary, before the
block ends (a SELECT, or the §7 end state). This covers block 2's two windows as well: their
counts, summaries and any selection replay stay unread until this block ends, and afterwards they
are diagnostic only. Naming the cause of a RECOVER, as §7 requires, may read that window's bracket
and admission evidence (fiducial bound, drift, clock outcome, logs); it never reads an overlap
count. The selected rung is the one result this block exists to produce and is recorded as a
parameter.

## 11. Changes after the seal

None to §§3-10 for an armed or completed window. A defect found later that changes a rule is
settled in one erratum by a cold gate; a fix that only makes code agree with this text goes
through the ordinary gated pull request.

## 12. Seal

Pinned at the seal (the seal record lists each with its sha256 at H): this file; the arm head H
(a main commit containing lane G2A-B3-RETRY-BACKOFF-01); `scripts/gen_g2_phase_d.py`,
`scripts/generate_g2a_probe_inputs.py`, `scripts/summarize_g2a_prefill_probe.py`,
`scripts/select_g2a_prefill_length.py`, `scripts/harvest_g2a_window.py`, `scripts/run_night.py`,
`scripts/run_campaign.py`, `joulewise/controller.py`, `joulewise/schemas.py`,
`joulewise/environment_admission.py`, `configs/campaign_policies/quiet_mac_p2_g2a_b3.json`,
`configs/model_panels/qwen3_4bit.json`, the D-166 registration file and the acceptance file.

H must contain the harvest rules block 2's seal required (a member whose clock anchor status is
not `bounded` is invalid; a member found invalid at harvest gives the §7 verdict, never REFUSED
for a summary byte difference) and the §4 wait; the seal record cites the tests that show each.
The harvest and the selector are run from a checkout whose pinned files match the seal record.
Any window of this block is armed from a head H′ that differs from H only by (i) the merged pin
advances of this block's earlier harvests, (ii) gated fixes that make code agree with this text
(§11), and (iii) commits that change only files under `docs/`, `tests/`, or the files
`RUN_STATE.md` and `TASK_QUEUE.md`; the arm checks (iii) with `git diff --name-only H H′`. The seal
record is extended with the H′ pins before each arm; no new seal is needed. Any other difference
needs a new seal.
