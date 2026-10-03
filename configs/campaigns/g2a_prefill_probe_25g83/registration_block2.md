# Registration G2A-25G83-B2: the G2-a prefill resolvability probe on macOS build 25G83 (measurement block 2), with its analysis plan

Status: DRAFT, written 2026-10-02 by the block-2 design seat (Opus 5.5, headless orchestrator seat
holding the orchestrator's design authority, RUN_STATE item 7). It becomes binding when a cold
Fable registration gate seals it (§12). Every rule below is fixed before any data of this block
exists. No value measured by this block appears in this file or may be added to it.

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
`docs/process_traces/2026-08-30-prefill-margin-coldgate/` records 01-03. This registration does not
change that rule. It fixes everything D-166 leaves to the window: the operating condition, the
window shape, what makes a capture valid, how many windows may run, when the block stops, and
what the result may and may not be used for.

**Worked example of the count.** A Qwen3-1.7B prefill that lasts 0.33 s can overlap 4 records
(for instance records covering 0.00-0.10, 0.10-0.20, 0.20-0.30 and 0.30-0.40 s when the phase runs
from 0.05 to 0.38 s); it is reducible (4 ≥ 3) but does not qualify (4 < 5). A prefill lasting
0.45 s overlaps at least 5 records and qualifies. The probe measures this count directly at each
rung; nothing about energy is used.

## 2. The block

One **G2-a window**, plus at most one **recovery window** under §7. Queue row
`V5-G2A-PREFILL-PROBE-01`. Receipt class `DIAGNOSTIC_NO_PACK` (no `_v5` pack exists or is touched).
Window plan ids have the form `d117-g2a-prefill-probe-<t0 UTC as YYYYMMDDTHHMMZ>`; the recovery
window, if any, has its own t0 and therefore its own id. The night gate's registration for the
plan is the D-166 registration file
`configs/campaigns/d117_contrast_v5/d166_dominance_criterion_registration.json` (sha256
`dfe55f8d96cd21e07cd1c7fe230fef34f485f027f3920ce96b8a9ebacc1ac265`, in
`joulewise/night_gate.py` `RULED_REGISTRATIONS`); this file is bound to the window by its sha256 in
the arm record and the seal record (§12).

## 3. Operating condition (each item is checked by code at arm or at t0)

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
  input inventory); 75 s idle before each member; the producer's fixed output budget. Every
  config, the panel file and the runtime adapter are bound by sha256 in the G2-a input inventory,
  which `generate_g2a_probe_inputs.py check` re-authenticates inside the chain before anything is
  reserved.
- **Chain.** The zsh chain emitted at H by the recorded G2-a window command of
  `scripts/gen_g2_phase_d.py` (lane G2A-NIGHT-25G83-01), with its pre-calibration screen literal
  derived from the acceptance above by the writer's own derivation and checked two ways by
  `gen_g2_phase_d.py --check`. Its sha256 sidecar is pinned in the plan.
- **Network time.** §5.
- **Ledger.** The measurement clone's calibration observation ledger is restored byte-exact from
  the retained Revision 6 C2 clone
  (`/Users/edr/night-custody/measurement/JouleWise-measurement-20261001T2252Z-r6-c2/runs/calibration_observation_ledger.jsonl`,
  file sha256 `3c9b6844e22958a6ba0eaee28cfab63642f3d0310f15b9bbc9e82363a2d772fb`, 376 records),
  whose head equals the committed pin `configs/calibration/calibration_ledger_head.json` at H
  (sequence 376 unless a later merged harvest advanced it; the arm recipe re-reads it). A ledger
  that fails custody audit or does not match the pin refuses the arm.

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
   `--arm-quiet-mode --max-failures 1`.
4. **Post bracket.** One governed pulse calibration in the same bracket session.
5. **Terminal boundary.** The ledger session is finalized; the chain records the terminal head
   candidate (`physical_ahead`) and stops with the tracked pin unchanged. The counts receipt and
   the four-row summary are written by `scripts/summarize_g2a_prefill_probe.py`.

`window_max_s` = `NIGHT_PROGRAMMED_SPAN_S` (the literal the generator writes into the chain from
the code constants, including its declared allowance for model load and inference; 17,248 s at
lane G2A-NIGHT-25G83-01) + 2700 s (the clean dwell's own cap), rounded up to a whole minute
(19,980 s at that span). If the chain runs past `t0 + window_max_s`, the driver's window expiry
stops it and the window is RECOVER (a stopped chain cannot leave a complete sweep with a passed
post bracket). Nothing in the window may be shortened,
skipped, reordered or repeated at arm or at run time.

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
- **Member.** A member is valid when its bundle passes strict validation from its raw evidence
  (`joulewise/cli.py` strict validator, re-reducing raw artifacts), every capture-level admission
  passes (including §5(b)'s binding part), and it is enclosed by the window's pre and post
  brackets. A member whose prefill phase overlaps fewer than 3 records is VALID: its reducer
  outcome `not_resolvable_sample_count` is a result, and its count is recorded. Validity never
  depends on the member's count or on any energy.
- **Rung evaluable.** A small-model rung is evaluable when it has at least 5 valid members. The
  configured roster has exactly 5 small members per rung, so a rung is evaluable only when all
  five are valid.

## 7. Counting, verdicts and stop rules

The harvest (`scripts/harvest_g2a_window.py`) writes one mechanical verdict per window:

- **SELECT**: both brackets pass and all four small-model rungs are evaluable. The window is
  *complete*; the analysis plan (§8) runs on it. The block ends.
- **RECOVER**: the chain started and the window is not complete (a pre-screen stop, a bracket
  failure, any small-model rung with fewer than 5 valid members, a nonzero or missing chain exit).
  The harvest names the cause codes.
- **NULL**: the chain never started (`night/chain.started` absent: night-gate refusal, OFF receipt
  failure, clean dwell timeout, admission budget exceeded). This is a **null window**: it is not a
  sweep and consumes nothing in this section.
- **REFUSED**: the harvest itself could not archive or authenticate (a tooling fault). It is fixed
  through the standing refusal route (R3) and the harvest re-run; it is never a science outcome.

A null window is re-armed with a new plan id after its named cause is gone, under
the standing re-arm rules; the same refusal signature twice in a row sends the next step to a
consult (Sol 6.1 plus Opus), not a third arm.

A RECOVER window whose chain made no capture (no directory under the probe root's
`runs/instrument_validation/` and no member directory under `runs/`) took no data; for the
allowance below it counts like a null window. After any other **RECOVER**, at most one recovery
window runs: a fresh, complete sweep with its own plan id,
bracket session, probe root and inputs regenerated by the same producer command (same prompt bytes,
same configs), armed only after the cause is named and, where it can be removed (a code defect, a
machine state), removed. The first window to reach SELECT supplies the selection input; members
are never pooled across windows, never topped up, and no member or rung is ever re-collected
inside a window (D-078). If the recovery window also ends RECOVER, the block stops and the
question goes to a consult (Sol 6.1 plus Opus, blind), then to the orchestrator's ruling; a
science disagreement between the two seats goes to a cold Fable judge. It never goes to a third
blind window.

## 8. Analysis plan

- **Input.** Only the authenticated four-row summary and counts receipt of the SELECT window, as
  regenerated byte-identically by the harvest from raw bundles.
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
  selected from").
- **Nothing else is computed.** No energy, power, duration, ratio or statistic of any member is
  computed, summarized, compared or reported by this block. Large-model counts are recorded in the
  summary and are not used by the rule.

## 9. What this block may and may not be used for

- It licenses exactly one thing: the `_v5` prefill length (or the D-166 4096 fallback) at the
  desk day.
- It is not a claim. It licenses no energy number, floor, minimum detectable effect, comparison,
  dominance sentence, difficulty statement or phase-attribution validation.
- Its member bundles, campaign log, configs, counts receipt and summary are diagnostic. They are
  never members of G2-b, the `_v5` transaction, any floor, mint or calibration corpus, and never
  enter any claim path. They are retained unchanged.
- Its two bracket captures are ordinary calibration-ledger observations, governed by the issued
  acceptance's own rules; this registration changes none of those rules.
- It does not authorize G2-b, the `_v5` transaction or any claim-bearing window. Those need their
  own gates; the pre-arm triple audit (#416, amended: before any claim-bearing run) applies before
  the first claim-bearing window, not to this diagnostic block.

## 10. Blindness

The harvest prints paths, shas, member counts (how many members, not their record counts) and the
verdict, never an energy, a fiducial bound, a drift value or a per-member overlap count; those stay
in the archived files. The verdict and the selection are computed by code from fixed rules; no
person or agent reads a measured value to decide anything in this block. The selected rung is the
one result this block exists to produce and is recorded as a parameter.

## 11. Changes after the seal

None to §§3-10 for an armed or completed window. A defect found later that changes a rule is
settled in one erratum by a cold gate; a fix that only makes code agree with this text goes
through the ordinary gated pull request.

## 12. Seal

Pinned at the seal (the seal record lists each with its sha256 at H): this file; the arm head H
(a main commit containing lane G2A-NIGHT-25G83-01); `scripts/gen_g2_phase_d.py`,
`scripts/generate_g2a_probe_inputs.py`, `scripts/summarize_g2a_prefill_probe.py`,
`scripts/select_g2a_prefill_length.py`, `scripts/harvest_g2a_window.py`, `scripts/run_night.py`,
`configs/model_panels/qwen3_4bit.json`, the D-166 registration file and the acceptance file.
