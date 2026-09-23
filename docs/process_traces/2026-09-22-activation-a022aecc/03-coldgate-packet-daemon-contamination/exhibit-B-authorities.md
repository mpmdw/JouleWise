# Exhibit B — controlling authorities (verbatim extracts at main `91f80870`)

Every block is the verbatim output of `git show 91f80870:<path> | sed -n '<a>,<b>p'`; the path and line range are stated above each block. No commentary beyond the one-line labels.

## B1 — `docs/decision_log.md`: D-181, D-182, D-161

### B1a — D-181 (complete entry)
`git show 91f80870:docs/decision_log.md | sed -n '11888,11957p'`  (lines 11888-11957 of 12073)

~~~~markdown
## D-181: Windows run whenever the machine is quiet; Fable 5.1 is the final eyes on every merge; the owner's hands step is prepared now (Ed, 2026-09-14)

**Status:** ratified by Ed, 2026-09-14 16:43 PDT, as directive issue #337 (owner, at the
machine), verbatim in
`docs/process_traces/2026-09-13-activation-24b9d3dd/55-ed-directive-337-verbatim.md`.
Recorded by the headless magistrate (activation `24b9d3dd`) through this PR, the same
way issue #316 became D-180 (Ed's words: "Record this ruling as a dated decision-log
entry through a PR under the normal gate, the same way #316 became D-180; do not amend
rule text yourself outside that PR"); nothing below is installed in code, runbooks or
the night machinery by this entry — each clause names its implementation lane, and
until that lane lands the existing mechanism's limits remain facts, not rules (decided
≠ done: the ruling is in force from the moment it names; what the machinery cannot yet
do is a mechanism limit, as Ed's clause 1 says). The ruling is standing;
by its own text it applies after the night armed under directive #336
(`d079-epoch-25g83-derivation-n1-20260915`, t0 2026-09-15 02:56 PDT) and to every
window after it, and it does not touch that night. Forcing context (factual, no rule):
the 2026-09-13 night fired and was refused by its own t0 census (an interactive session
and agent desktop apps present); the 2026-09-14 morning install span closed without an
arm because the arm-time census never cleared; the ordinary documented recovery was a
new plan for the next calendar night, until directive #336's one-night owner
authorization of an evening install. Ed rules that the spacing was never a scientific
requirement.

1. **Windows run as soon as the machine is quiet; no cadence rule.** Whenever the
   census is clean, day or night, several windows per day if the gates pass, with no
   artificial spacing (no "one night in three", no "only at 02:56", no minimum gap
   between windows). Ed keeps the machine quiet whenever he is not using it and will
   close every interactive session and quit the agent desktop apps on request; a
   notice email is enough. The soundness fences stay exactly as they are: physics and
   evidence refusals, pre-registration before data, the census at arm and at t0, the
   twelve-row gate, email-then-arm with Ed's NO overriding. Nothing else about timing
   is a rule. Implementation: the current machinery pins one plan at a fixed daily
   launchd minute inside the 02:45–03:30 belt with a single 07:00 dead-man and a
   calendar-day install span — a mechanism limit, not a scientific one. Lanes
   `INSTALL-WINDOWS-MULTI-01` (install spans as a list, dead-man per span),
   `ARM-RETRY-CLASS-01` and `ARM-CENSUS-IDLE-INTERACTIVE-01` are promoted to the top of
   the queue in that order, immediately after tonight's harvest and the §2.5 outcome
   action; they are designed so a plan can carry a t0 at any clock time and so a second
   window can be armed as soon as the previous harvest is done. (This supersedes the D-180 sequencing note "after G2-a
   instrument validation" on those three rows.) Queue mechanism, describing the kernel
   edit: `INSTALL-WINDOWS-MULTI-01` takes the agent lane's rank 0 (the lane head, ahead
   of every rank-1-and-up row) and is blocked on a hard start EVENT dependency — the
   09-15 night harvested and its §2.5 action taken — released in the bookkeeping that
   records both; the other two are blocked on their predecessor by a hard start
   dependency and take rank 0 in the bookkeeping that closes it — so the kernel refuses
   the first lane before the harvest event and refuses a successor before its
   predecessor closes; the head position of each successor is carried by the rank edit
   in that closing bookkeeping, not by the kernel on its own.
2. **Fable 5.1 is the final eyes on every merge.** Every PR that merges carries a
   terminal review by Fable 5.1 — the magistrate at the pinned model, reading the final
   head itself, not a delegate's summary — as its last review before merge. The
   twelve-row gate already requires this (row 7, the apex Fable code-reading diff gate;
   row 12, the magistrate's non-delegable terminal review of the final head sha). Both
   rows stay exactly as they are; never downgraded or delegated; the final head sha is
   cited in row 12 on every PR. No lane: this clause changes no text.
3. **Clear the owner's hands step for the first pack night now.** Lane
   `ARM-CENSUS-BROWSER-PROBE-SYSTEM-SERVICES-01` (lane `ed_external`) needs a desk
   proof by Ed (`author_arm_evidence_t0` against a `TRANSACTION_PACK` pack root with
   no browser, no agents, no caffeinate). The magistrate prepares that pack root and
   window-custody root and emails Ed the exact command and when to run it; Ed runs it
   at the next moment the machine is otherwise idle. This step must not be the reason
   the first G2-a pack window waits.

Housekeeping recorded with the rulings, in Ed's words: "PR #330's conflicts are resolved
at d80e5e37 (kernel 170 rows, tests OK); its body still lacks the gate ledger. Take it
through the gate and merge it under Fable's terminal review." (170 is that PR's kernel
row count after its four closures, not the live count at this entry.) Obligation
recorded, not yet performed at the time of this entry: "Comment the outcome of each
ruling on this issue and close it when all three are recorded."

~~~~

### B1b — D-182 (complete entry)
`git show 91f80870:docs/decision_log.md | sed -n '11958,12018p'`  (lines 11958-12018 of 12073)

~~~~markdown
## D-182: A zero-capture machine-state refusal licenses one new-plan successor (Ed, 2026-09-17)

**Status:** ratified by Ed, 2026-09-17 ~20:30 PDT, in the interactive session
5c919872 ("affirm of course" to the text below; verbatim exchange in
`docs/process_traces/2026-09-17-interactive-5c919872/06-ed-ruling-d182-verbatim.md`).
Recorded by the magistrate through this PR the same way directive #337 became D-181;
nothing is installed by this entry. Implementation lanes: the desk-side successor
route is stage D7 of NIGHT-GATE-QUIET-ADMISSION-01 (kernel 231: `joulewise/arm_retry.py`,
NIGHT_HANDBACK R1) and the watchdog-side release of the census hold is
WATCHDOG-EARLY-REFUSAL-RELEASE-01 (kernel 234). Provenance correction (Opus pairing refuter on
ruling 70, record 12): Ed had ALREADY ruled A212 part (b) on 2026-09-16 00:35 PDT
("unless there's a scientific reason that's an unsound decision absolutely reduce the
hours to 20 min"), recorded as the amendment at lines 44–61 of
`docs/process_traces/2026-09-15-activation-08ca8197/06-refusal-fast-retry-lane-registration.md`
and corroborated at `docs/process/automation_history_2026-09-16.md:286-288`; packet 70's
exhibit E stopped four lines short of that amendment, so cold-gate ruling 70 Q9 rejected
the route as unauthorised. This entry therefore (a) promotes the 09-16 ruling from a lane
record to the decision log, (b) extends it to the bind-window expiry class, which did not
exist on 09-16, and (c) carries Ed's 09-17 re-affirmation of the consolidated text.

**The rule (Ed's affirmed text):**

> A night that refuses on machine state with zero capture (census, load or CPU
> quietness, bind-window expiry, screensaver, boot clock) licenses ONE new-plan
> successor once the courier has delivered: new plan id, fresh notice, at least
> 60 s spacing, bounded by install close; never a re-arm of the same plan; every
> observed NO still stops.

**Terms, so the rule can be applied without this session's context.** A *night*
is one armed unattended measurement plan. It *refuses on machine state* when the
night gate returns one of the machine-state codes: `night_refused_agent_present`
(an interactive agent session in the process census), `night_refused_not_quiet`
(today the load, power and thermal predicates; under plan v4 the interval-CPU
predicate), the bind-window expiry code that NIGHT-GATE-QUIET-ADMISSION-01
introduces (a distinct code per cold-gate ruling 70 §12 item 3), the
screensaver-configuration refusal the code calls HID idle, and the boot-clock
refusal. *Zero capture* means no reservation opened a ledger session, no capture
writer ran and the plan's `runs/instrument_validation` directory is empty; the
successor route requires positive evidence of all three, never the mere
existence of a refusal file. *The courier has delivered* means `courier.sent`
exists for the refused plan. A *new-plan successor* is a plan with its own id,
its own notice email (the standing no-objection window applies), armed no
sooner than 60 s after the refused plan's terminal write and only while the
successor's own `install_close_epoch` lies ahead; the refused plan is never
re-armed. *Every observed NO still stops*: a NO on any notice thread halts the
successor exactly as it halts a first arm.

**Why now.** Cold-gate ruling 70 (Q9) REJECTED the successor route on a packet that
omitted the 09-16 amendment (see Status); the consolidated rule now lives where a cold
judge reads first. The 2026-09-17 refusal at 15:30 was harvested at
18:09 and produced no successor, roughly three hours of idle quiet machine
against the ~20-minute target of REFUSAL-FAST-RETRY-01. D-181 already forbids
artificial spacing between windows; this entry supplies the authorisation D-181
did not.

**What this does not change.** Physics, evidence and pre-registration refusals
stay fail-closed (D-161); the successor passes every gate anew at its own t0,
including the census (D-181); the refusal that ends a span ends it (no waiting
inside a refused span beyond the bind window the plan itself seals); no
frequency bound is added (every bound must be scientific, D-181).

~~~~

### B1c — D-161 heading paragraph (first 25 lines of the entry)
`git show 91f80870:docs/decision_log.md | sed -n '10687,10711p'`  (lines 10687-10711 of 12073)

~~~~markdown
## D-161: threat-model prune (Ed, 2026-08-27)

Index row carries the operative detail. Trace: the prune consult under
`docs/process_traces/2026-08-27-t26/threat-model-prune/` — three blind seats
+ `04-MAGISTRATE-RULING.md` (ADDENDUM, 2026-08-27 PM): the operative test is
MISTAKE vs DELIBERATE (fail-closed for physics/evidence, pre-registration and
operator mistakes; deliberate-only guards retire); the histsem pin is cured
ASYMMETRICALLY (historical-side equality stays B; current-side equality and
the delta list → warn after `_v4`); HISTPACK-PROMISOR-NOFETCH-01 RETIRED
unbuilt; only the refresh lane lands before the night; the post-transaction
prune waves (a)–(f) are enumerated in the ruling; refresh lane: stream S14,
`feat/pinset-refresh-row-lane`.


## D-162: the live-proof gate, corrected (magistrate, 2026-08-28)

Index row carries the operative detail. Trace:
`docs/process_traces/2026-08-28-live-smoke/proof-consult/`.


## D-163: the week after `_v4` (magistrate, 2026-08-28)

Index row carries the operative detail. Trace:
`docs/process_traces/2026-08-28-ladder-consult/`.

~~~~

## B2 — `docs/process/automation_history_2026-09-16.md`

### B2a — the 09-15 night refused on load alone: fseventsd at ~184 %
`git show 91f80870:docs/process/automation_history_2026-09-16.md | sed -n '95,112p'`  (lines 95-112 of 444)

~~~~markdown
  pass of the unattended chain.
- **The first science night**, checking whether calibration remained valid after an OS change (n1-20260913; ordered by issue #316): fired 02:56:02, REFUSED
  at t0 because Ed's interactive session (pid 24974) and the ChatGPT desktop app's bundled Codex helper were in the
  census (`docs/process_traces/2026-09-13-activation-c5048879/01-equivalence-night-20260913-harvest-record.md`). The
  09-14 03:00–06:30 install span then closed without an arm because the arm-time census never cleared
  (`docs/process_traces/2026-09-13-activation-24b9d3dd/49-no-arm-record-n1-20260915.md`).
- **The next science attempt** (n1-20260915): Ed's directive (issue #336) authorised an evening install; the plan was armed 16:45:46 09-14 after Ed closed his
  session and the census went clean at 16:44:13 (`…24b9d3dd/52-arm-record-n1-20260915.md`); fired 02:56:03 09-15 and was
  REFUSED on load alone: 1-min load 2.55 > 2.0 with a clean census. The load was `fseventsd` (pid 553) at ~184 % CPU
  with 4721 CPU-minutes over 12 days of uptime
  (`docs/process_traces/2026-09-15-activation-1acf2aee/01-equivalence-night-20260915-harvest-record.md`).

Two rulings came out of these nights. The **arm-retry ruling** (`docs/decision_log.md` D-180; Ed, 2026-09-10, after
the 09-10 arm was blocked by two idle interactive sessions): permitted installation intervals recur within a day; a pre-authorised retry
class exists for non-physics arm aborts (idle interactive session, stale notice hash, watchdog
`CLOCK_UNCERTAIN`/`NETWORK_UNCERTAIN`, transport failure); idle interactive sessions do not block a stub's
arm-time census (D-180 items 1–3). The **any-time-windows ruling** (D-181; Ed, issue #337, 2026-09-14 16:43): windows
run whenever the machine is quiet, day or night, several per day, no cadence rule; the fixed daily minute inside the
~~~~

### B2b — sensible gates
`git show 91f80870:docs/process/automation_history_2026-09-16.md | sed -n '140,150p'`  (lines 140-150 of 444)

~~~~markdown
  refusal whose only actor is the trusted operator and downgrades it to warn-and-record or retires it; fail-closed
  behaviour STAYS for measurement validity, evidence or pre-registration (missing calibration, unresolved clock alignment, absent
  floor, stale drift evidence, unfrozen plan, post-hoc analysis choice); the repository is tamper-EVIDENT for the
  operator's benefit, not tamper-PROOF. The addendum's operative test: MISTAKE vs DELIBERATE, guard against mistakes,
  retire deliberate-only guards (`docs/decision_log.md:207` index row; `:10685-10696`).
- **Sensible gates (Ed, 2026-09-10 ~04:20).** "make sure there are no silly gates on accepting numbers … recall that
  time where you wanted a tolerance of like 1e-15 sensitivity or something ridiculously microscopic compared to the
  measurement". Every tolerance on the claim path is sized to the instrument, boundary-attribution limit ≈ 1 J and minimum difference required for a claim
  ≈ 5 J (`docs/decision_log.md` D-078 cl.11), never to decimal places; measurement-validity and evidence refusals stay. The review of measurement checks
  (lane GATE-SENSIBILITY-SWEEP-01) inventoried 299 gates and merged three repairs (R1/R3/R4) plus the prefill probe's idle setting (G2-a `idle_seconds 75`) in
  PR #314 (`0d4bb4fb`), and sent the zero-point band (an `isclose(rel_tol=1e-9, abs_tol=1e-12)` comparison of two
~~~~

### B2c — D-161 tolerances
`git show 91f80870:docs/process/automation_history_2026-09-16.md | sed -n '430,440p'`  (lines 430-440 of 444)

~~~~markdown
- When Gmail is down, the notice goes out as a `directive-notice` issue (directive issue #349; memory file `notice-transport-fallback-ruling.md`).
- Merge on green local replay + quick tier; hosted CI is post-merge confirmation (memory file `ci-postmerge-ruling.md`).
- Never `gh pr create --body` without the twelve-row ledger; `gh pr checks` must show gate-ledger green; branch protection is the durable fix (memory file `pr-body-gate-ledger-required.md`).
- Batch bookkeeping pushes; docs-only pushes skip the matrix; cancel redundant queued main runs (memory file `ci-queue-bookkeeping-pushes.md`).
- Two consecutive repair rounds for the same failure class require consultation before further repair (orchestration rule 11 in `/Users/edr/code/JouleWise/CLAUDE.local.md`; the round-6 cold gate ruling Q3 and the delta-3 stop record cited in §2.6).
- "No round N" rules stop death spirals, not nearly-done designs converging under executed evidence (memory file `stop-conditions-are-antispiral.md`, Ed 09-15, applied at 23:15 to round 8).
- A bound is observed, not predicted; no invented ceiling constants (cold gate 25 Q2 in §2.6, `MAX_INSTALL_DURATION_S` rejected).
- Fail-closed only for physics, evidence and pre-registration; checks only against deliberate operator tampering retire; tolerances are sized to the instrument (≈ 1 J / ≈ 5 J) (threat-model prune `docs/decision_log.md` D-161; memory file `sensible-gates-directive.md`; the `codex|claude|t3` census kept in PR #334).
- Treat unknown process liveness as loaded; a test double that cannot represent unknown cannot verify that rule (Opus design seat record Q3 in §2.6).
- Delegated sessions run in linked worktrees, never main; briefs under enforced `WRITE_SCOPE` (memory file `codex-seat-launch-rules.md`).
- Never guard a bookkeeping chain on a clean tree; read every commit's `--stat` before claiming it landed (memory file `bookkeeping-chain-guard.md`).
~~~~

## B3 — `docs/process/NIGHT_HANDBACK.md`

### B3a — the pre-check census wording ruled by the 2026-09-21 cold gate
`git show 91f80870:docs/process/NIGHT_HANDBACK.md | sed -n '405,420p'`  (lines 405-420 of 948)

~~~~markdown
Record 17's script set remains the fallback until the first live use succeeds.

Pre-check step, ruled by the cold gate 2026-09-21 (packet 05 Q3, wording
corrected by the cold gate's packet 06 ruling): the census lists every process
whose full command line matches `codex`, `claude` or `t3` (the exact command is
`night_gate.AGENT_CENSUS_ARGV`, a `pgrep -lf` over those three words) and
classifies each listed process that is neither the checking process nor one of
its ancestors as foreign (`arm_census.classify_arm_census`); a process whose
command line matches none of the three words is never foreign, whatever its
ancestry. The tracked check refuses on any foreign PID, so the session's own
MCP helpers, which match `codex`, must be gone first. The ruled text, with its
commands corrected by the cold gate 2026-09-21 (activation ce7c57a9, round-3
packet, Q2; `pgrep -lP` prints process names only and `pkill -P` reaches
immediate children only, both verified against the installed manual and a live
process tree):

~~~~

### B3b — "Gate and driver refusals — cold-gate path" table header and the `night_refused_not_quiet` row
`git show 91f80870:docs/process/NIGHT_HANDBACK.md | sed -n '79,86p'`  (lines 79-86 of 948)

~~~~markdown
**Gate and driver refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `night_refused_agent_present` | Production census refusal, including a receipt at t0; never an idle arm event. Zero-capture successor route per D-182. |
| `night_refused_not_quiet` | One-shot load refusal for v2, or a terminal power/thermal predicate failure. For v4, load is diagnostic and the CPU cutoff is a sealed plan parameter with a named ruling. Zero-capture successor route per D-182. |
| `night_refused_bind_expired` | Bind window expired with every sample recorded. Load is diagnostic; the CPU cutoff is a sealed plan parameter. Zero-capture successor route per D-182. |
| `night_refused_hid_idle` | Screensaver-configuration guard failed; this is not a live inactivity measurement. Zero-capture successor route per D-182. |
~~~~

### B3c — "Other explicit refusals — cold-gate path" table header and the `HOLD_CENSUS` row
`git show 91f80870:docs/process/NIGHT_HANDBACK.md | sed -n '127,133p'`  (lines 127-133 of 948)

~~~~markdown
**Other explicit refusals — cold-gate path.**

| Exact cause | Why A172 grants no retry exception |
|---|---|
| `HOLD_CENSUS` | A supervisor census hold alone does not establish the narrowly evidenced idle arm cause. |
| `slot_refused` | A measurement slot refused; cure the finding before any further night. |

~~~~

## B4 — `docs/process_traces/2026-09-19-activation-d0b83820/10a-adjudication-stage-a-executor.md` (whole file, 21 lines)

### B4 — complete
`git show 91f80870:docs/process_traces/2026-09-19-activation-d0b83820/10a-adjudication-stage-a-executor.md | sed -n '1,21p'`  (lines 1-21 of 21)

~~~~markdown
# Record 10a — adjudication of cold gate packet 10 (ruling 10 + Opus contract refuter 11): Stage A evidence executor (lead, 2026-09-19 12:3x PDT)

## Q1 — registration guard: RULED (a′) as both seats converge, with one binding detail fixed by the lead

Both seats refuse (b) (the D-166 attestation would be false: `night_gate.py:1349, :1362` writes "D-166 registration hash passed" into every DIAGNOSTIC_NO_PACK receipt). Both rule a **digest-keyed ruled-registration table** in `night_gate.py` (`RULED_REGISTRATIONS = {sha256: {label, ruling, binds_chain}}`), lookup replacing the single equality at `:1349`, `None` → `night_refused_registration`, receipt row C1 carrying `registration_label` / `registration_ruling` and a detail string derived from the label (never the D-166 literal for a non-D-166 entry — the refuter's "the receipt still lies" point). No v2 schema key (both). Binding of the evidence registration to its chain: the judge puts `chain_sha256` in the registration file; the refuter pins it in the table entry. **Lead's fix:** the per-plan `chain.zsh` digest is only known at arm time, so neither can bind it; the stable object is the **chain SOURCE digest** (`chain.zsh.chain-source.sha256`, the tracked template, already measured by `_check_chain_identity` and carried in the receipt as `chain_source_sha256`). The evidence registration file carries `"chain_source_sha256"` of the tracked evidence chain template; the gate compares it to the measured chain-source digest; D-166 stays grandfathered (`binds_chain: False`). The table is amended only by cold-gate ruling (NIGHT_HANDBACK.md:134 clause appended, refusal row added at :88).

## Q2 — the pilot: RULED idle-only variance pilot as the first window; block two authored only after the measured spread

Judge: 6 × 600 s (70 min), δ = 1 J, `n = ⌈8 s²/δ²⌉`, floor 3, stop branch `s_pair > 2 J`. Refuter: 12 × 600 s + 900 s settle (≈ 2 h 15 m), δ = 0.5 J, sizing from the UPPER confidence bound on `s_pair` (df = 5 carries a 2.09× one-sided factor; a 6-envelope pilot can under-size block two 4–8×), stop branch at 24 pairs. **Synthesis:** N = 12 envelopes of 600 s with the 480 s interior (the refuter's df argument is arithmetic, not taste), settle 600 s after GO (the judge's; 900 s adds nothing measured), total ≈ 2 h 10 m inside a 9000 s `window_max_s`; **δ = 1 J** (the judge's; the instrument's attribution limit is ≈ 1 J and Ed's sensible-gates directive sizes tolerances to the instrument — 0.5 J is below what the instrument can see); sizing uses the upper 90 % confidence bound on `s_pair` (refuter); minimum retained 8 envelopes (≥ 6 adjacent pairs) else INCONCLUSIVE, no top-up; stop branch pre-registered: if the sized `n` exceeds 24 pairs, or the observer floor's own busy cores exceed the smallest holdable share, or block two's upper bound at that share exceeds 1 J → "no cutoff qualifies", deliverable = the upper bound and the clean-machine busy-core distribution. Exclusions decided by NAMED mechanisms frozen in the protocol file: census not clean, AC probe not "AC Power", `CPU_Speed_Limit` < 100 or probe error, clock anchor unresolved, incomplete interior support. **`busy_cores` from the in-chain sampler is a recorded covariate only — no exclusion threshold reads it** (both seats; a post-hoc threshold would be a cutoff, the circularity cold gate 70 refused). The protocol file (`configs/campaigns/quiet_predicate_evidence_01/pilot_protocol_v1.json`) is the Q1 registration; its digest enters the table in the same PR.

## Q3 — probe receipt: RULED a typed evidence probe receipt, a SECOND probe kind; it IS a contract amendment

Both seats. Dispatch by ONE literal export in the pinned chain, `export NIGHT_PAYLOAD_KIND=quiet_predicate_evidence` (absent → calibration probe byte-for-byte unchanged; present with `CALIBRATION_LEDGER` also exported, or more than once → install refusal `probe payload kind ambiguous`), at both dispatch points (worker `run_night.py:3216/3275`; installer `validate_probe_receipt`). Schema `joulewise.night_evidence_probe_receipt.v1` with the judge's field set (plan/chain/chain-source/manifest/harness digests, registration digest + label, interpreters, `verify_only: true`, `outcome`), admission gates reusing v1's freshness rules and comparing every digest to the tracked files at `measurement_head`. Amendment scope: NIGHT_HANDBACK.md :563–575 ("binds … ledger head …" gains the evidence-payload alternative; refuter) AND the runbook :3048 verify-only probe table gains a second row (judge). The authoring tool is a NEW `scripts/gen_evidence_night.py` (lead authority; refusal set ruled: refuses any class but `DIAGNOSTIC_NO_PACK`, any calibration/derivation chain, any CLI override of the frozen protocol). The in-chain sampler as recorder is plain code on the judge's three conditions (admits nothing; journals to a file not named `quiet_samples.jsonl`; PROVISIONAL covariate).

## Dissent

None on substance; the chain-source binding is a lead correction of a shared imprecision, recorded here for Ed.

## Order

Lane STAGE-A-EVIDENCE-EXECUTOR-01 (register at the next kernel touch): seat (Astra xhigh, brief 46) implements the ruled shape — gate table + receipt row + refusal, evidence probe receipt + dispatch + installer validation, `gen_evidence_night.py`, evidence chain template `scripts/night_chains/quiet_predicate_evidence.zsh`, the frozen pilot protocol v1 file, harness admissibility fixes (`os_build` in rows; per-round AC/thermal probe retention; load-log join; interior-interval support reduction), tests, and the two docs amendments — then refuters (contract + execution), delta re-audit, Opus counter-review, full replay, PR; then pilot night one under NIGHT_HANDBACK.
~~~~

## B5 — `docs/process_traces/2026-09-19-activation-d0b83820/46b-ruling-stage-a-seat-r3.md` (whole file, 11 lines; every `grep -n` hit for sizing / s_upper / maximum 24 pairs / stop branch falls inside it)

### B5 — complete
`git show 91f80870:docs/process_traces/2026-09-19-activation-d0b83820/46b-ruling-stage-a-seat-r3.md | sed -n '1,11p'`  (lines 1-11 of 11)

~~~~markdown
# Record 46b — lead answer to seat 46's NEEDS_RULING R3 (block-two sizing: the upper confidence bound on the paired spread), 2026-09-19 13:3x PDT

**Question (seat 46 part 2):** which upper-90 % confidence construction, dependence assumption and effective degrees of freedom apply to the eleven OVERLAPPING adjacent differences of twelve envelopes (and to retained patterns after exclusions)?

**Ruled: disjoint adjacent pairs for the sizing statistic; overlapping differences reported as a diagnostic only.** Reason: adjacent differences of one series share envelopes, so their SD has no clean degrees of freedom; the cold judge's own df = 5 arithmetic (ruling 10 Q2, refuter 11) presumed six independent pairs. Protocol v1 therefore fixes, before the pilot runs:

- Pairs `(e1,e2), (e3,e4), …, (e11,e12)` → up to n = 6 differences `Δ_k = J(e_{2k}) − J(e_{2k−1})` over the 480 s interiors; a pair is retained only if BOTH envelopes are retained (an excluded envelope drops exactly its pair; pairs are never re-formed across a gap — no bridging, as the seat already implements); minimum retained pairs 4 (else INCONCLUSIVE, no top-up; consistent with "minimum retained 8 envelopes").
- `s_pair` = sample SD of the retained Δ_k (df = n − 1); `s_upper` = the one-sided upper 90 % confidence bound on σ from the chi-square construction: `s_upper = s_pair · sqrt((n−1) / χ²_{0.10, n−1})` (n = 6 → factor `sqrt(5/1.610) = 1.762`; n = 4 → `sqrt(3/0.584) = 2.266`). Normality is an assumption of this construction and is stated as such in the memo; the pilot's eleven overlapping differences and the twelve single-envelope values are reported beside it as diagnostics (spread, drift, any pair with |Δ| > 3·s_pair named).
- Block-two sizing (unchanged from 10a otherwise): `n_pairs = max(3, ⌈8 · s_upper² / δ²⌉)`, δ = 1 J; stop branch if `n_pairs > 24`.

This is a protocol-file detail fixed before capture (pre-registration discipline), not a process rule; Ed's methodology authority is preserved because the protocol file and its digest are in the PR he can veto, and the "no cutoff qualifies" branch stays pre-registered. Implement in `joulewise/quiet_predicate_campaign.py` (the sizing function and the pairing), the protocol JSON/README, and the campaign tests; nothing else changes.
~~~~

## B6 — `docs/process_traces/2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md` (the PRIOR night)

### B6a — §2 Verdict, through its per-envelope table
`git show 91f80870:docs/process_traces/2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md | sed -n '23,83p'`  (lines 23-83 of 318)

~~~~markdown
## §2 Verdict (executed evidence, read at the bench 04:58 PDT from the custody root)

Custody root
`/Users/edr/night-custody/qpe01-pilot-n1-20260922-0217-20260922-0217-1790068620-d45378c6010b538ca1bb74ae0f2222dceb4df1e4`
(`night_plan.json` v2, `measurement_head` = `repo_head` = `d45378c6`,
`window_max_s` 9000, t0 1790068620 = 02:17:00 PDT).

- `night.log`: 02:17:00.60 driver started; gate verdict GO; chain digest
  verified; **04:27:11.85 result verdict=GO**; 04:28:36 and 04:32:34 "durable
  record failed" (the results push, §5); 04:31:21 courier attempt=1 sent=True.
- `night/chain.started` 02:17:00.67 (pid 98681); `night/chain.exited`
  04:27:10.96 **exit_code 0**; `chain.stderr.log` EMPTY; `chain.stdout.log`:
  600 s settle, twelve `envelope_start`/`envelope_end` pairs each `rc=0
  cleanup_proven=True`, `evidence_end outcome=complete cleanup_proven=True`.
- `night/result.json`: verdict GO, `aborted_reason` null, no refusal
  documents, receipt class `DIAGNOSTIC_NO_PACK`; `night/receipt.json` (02:17)
  C1 PASS, C2 NOT_APPLICABLE, C3 PASS, C4 PASS, C5 PASS. `launchd.night.err`
  EMPTY; `launchd.night.out` = the courier's closing summary.
- `night/evidence_outcome.json`: outcome `complete`, `envelopes_attempted 12`,
  `cleanup_proven true`, error null. `evidence_cleanup.json`: recorder group
  98772 absent, residue empty, no signal errors, budget 30 s.
- Courier: Gmail `1a0c8e258b89b05f` sent 04:31 (`courier.sent`: pid 11817,
  epoch 1790076681); the courier's reading of the summary and of the push
  failure matches this record.
- `night/evidence/summary.json`: **status INCONCLUSIVE, retained 2 of 12**
  (envelopes 2 and 12: 154.88 J and 151.03 J over their 480 s interiors),
  `retained_pairs 0`, `pair_sd_j` null ("fewer than four retained disjoint
  pairs or eight retained envelopes; no top-up"), `block_two_stop.outcome`
  **"no cutoff qualifies"** (cause `observer_floor_above_smallest_holdable_share`),
  `cutoff_authority false`. Diagnostics only: unfiltered single-envelope SD
  1.454 J (five envelopes with a joule value: 154.88, 152.15, 151.86, 152.81,
  151.03), overlapping adjacent-pair SD 1.058 J (deltas −0.28 J, −1.78 J),
  first-to-last retained drift −3.86 J. Busy cores p50 0.24, p90 0.32, max
  0.74 (covariate only). All twelve envelopes passed census, AC and thermal
  probes; 260 driver censuses, zero hits.

Per-envelope disposition (from each `envelope-NN/session.json`, fields
`interior.status`, `interior.reason`, `interior.native_samples`,
`power.anchor.status`, `power.anchor.detail`, `start_drift_s`):

| env | wall span (PDT) | anchor | detail | interior | native samples | start drift s |
|---|---|---|---|---|---|---|
| 01 | 02:27:01–02:37:01 | unknown | wall_minus_monotonic_span_exceeded (8.04 ms) | partial, clock anchor unresolved | 0 | 0.32 |
| 02 | 02:37:08–02:47:01 | bounded (0.42 ms span, 1.12 ms bound) | — | complete | 2056 | 8.01 |
| 03 | 02:47:11–02:57:00 | unknown | affine_clock_fit_empty (4.44 ms change) | partial, clock anchor unresolved | 0 | 10.23 |
| 04 | 02:57:08–03:07:01 | unknown | affine_clock_fit_empty (1.33 ms change) | partial, clock anchor unresolved | 0 | 7.81 |
| 05 | 03:07:08–03:17:01 | bounded (1.19 / 2.98 ms) | — | partial, incomplete interior support | 2038 | 7.89 |
| 06 | 03:17:11–03:27:01 | bounded (1.15 / 2.16 ms) | — | partial, incomplete interior support | 2038 | 10.18 |
| 07 | 03:27:10–03:37:00 | unknown | wall_minus_monotonic_span_exceeded (22.36 ms) | partial, clock anchor unresolved | 0 | 9.53 |
| 08 | 03:37:08–03:47:00 | unknown | effective_clock_anchor_bound_exceeded (4.54 ms span, 5.08 ms bound) | partial, clock anchor unresolved | 0 | 7.75 |
| 09 | 03:47:10–03:57:00 | unknown | effective_clock_anchor_bound_exceeded (4.53 ms span, 5.35 ms bound) | partial, clock anchor unresolved | 0 | 10.06 |
| 10 | 03:57:10–04:07:00 | unknown | wall_minus_monotonic_span_exceeded (+13.05 ms) | partial, clock anchor unresolved | 0 | 9.24 |
| 11 | 04:07:08–04:17:00 | bounded (1.52 / 4.02 ms) | — | partial, incomplete interior support | 2039 | 7.85 |
| 12 | 04:17:10–04:27:00 | bounded (1.51 / 1.94 ms) | — | complete | 2070 | 9.60 |

The three "incomplete interior support" envelopes (5, 6, 11) have full rail
coverage (480.000 s on both rails) but `span_mismatch true`: the native
frames' summed overlap differs from 480 s by more than the 1 µs tolerance,
so the deriver reports them partial although a joule value exists. That is a
second, smaller defect class (§6 finding 3).

~~~~

### B6b — §7 Ruling
`git show 91f80870:docs/process_traces/2026-09-22-activation-22666c9f/01-qpe01-pilot-n1-20260922-0217-harvest-record.md | sed -n '239,254p'`  (lines 239-254 of 318)

~~~~markdown
## §7 Ruling (magistrate, within its authority; no process rule touched)

1. The night is a `DIAGNOSTIC_NO_PACK` GO with two retained envelopes and no
   disjoint pair. **"No cutoff qualifies" stands**; block two is not sized;
   no quiet-admission threshold is activated; everything stays PROVISIONAL.
2. **No next pilot night is prepared on this code.** With the present caps
   and the daemon's observed behaviour the expected yield is about five
   bounded envelopes in twelve, below the eight-envelope / four-pair floor
   the summary needs; another night would spend a window to reproduce §6.
   The critical path is the anchor lane's cold-gate packet (§8), then a
   re-run of the pilot under the ruled caps.
3. The results-branch publication waits for Ed's choice (§5); the push is
   not retried by any courier or magistrate.
4. Registration only: the three lanes in §8 are registered in the kernel with
   this record as authority; none is a ruling.

~~~~

## B7 — `configs/campaigns/quiet_predicate_evidence_01/README.md` (complete)

### B7 — complete
`git show 91f80870:configs/campaigns/quiet_predicate_evidence_01/README.md | sed -n '1,98p'`  (lines 1-98 of 98)

~~~~markdown
# QPE-01: the first quiet-predicate evidence night

This pilot measures how much consecutive idle energy observations vary on the
current Mac. It collects evidence for a future CPU activity limit; it does not
choose or activate a limit. All results are **PROVISIONAL**. Stage B and a
separate cold-gate ruling remain necessary before activation.

The frozen registration is `pilot_protocol_v1.json`, under cold gate 10 Q1/Q2
(2026-09-19), adjudication 10a and sizing ruling 46b. Its exact SHA-256 fingerprint is a key in
`night_gate.RULED_REGISTRATIONS`. That table can change only by cold-gate ruling.
The registration also names the fingerprint of the tracked evidence chain
source. The gate measures that source at the plan's measurement commit and
compares it to the literal in the pinned wrapper. An advisory sidecar cannot
substitute for the measured source.

The plan uses v2 `DIAGNOSTIC_NO_PACK` admission and a 9000-second window. After
GO, the chain settles for 600 seconds, then schedules 12 consecutive 600-second
envelopes. Each analysis interval is the interior 480 seconds, starting 60
seconds into its envelope. There is no load generator. Absolute start times
prevent cumulative schedule drift; collection ends at each scheduled envelope
boundary. Late starts remain visible, and starts more than ten seconds from schedule
are excluded. Nothing is compressed, retried or topped up.

The chain runs `quiet_admission.sample_interval` every 30 seconds as a recorder.
It writes `evidence_busy_cores.jsonl`, never `quiet_samples.jsonl`. Its busy-core
intervals are joined to scheduled envelopes by monotonic support; the summary
reports each envelope's median/max and the distribution for envelopes passing
census, AC and thermal probes. These numbers are covariates: they describe the machine and are **never an exclusion
or admission input**. Observer CPU cost includes the whole observer and its
reaped children, including the recorder and census, and is never subtracted.

Envelopes are excluded only by frozen, named mechanisms: the census is not
clean or is unknown; the AC probe does not report “AC Power” or errors; a
`CPU_Speed_Limit` is below 100 or the thermal probe errors; the clock anchor is
unresolved; or native sample support does not cover the complete interior.
A collector failure is `collect_error`; unproven per-envelope cleanup is
`cleanup_unproven`. Both exclude that envelope and continue on the frozen
cadence. Two consecutive cleanup failures or a chain refusal/crash (including
a dead recorder) abort with a typed refusal document.
The frozen schedule also excludes `start_drift` above ten seconds. Partial
rows, original power files and exclusion reasons remain in the evidence.
Energy is integrated over native support, not inferred by multiplying a
whole-envelope mean by 480 seconds. CPU+GPU+ANE joules are the main quantity;
combined power is a cross-check. OS build, boot identity, tool identity,
per-round AC/thermal results, cadence and observer cost accompany the numbers.

Sizing uses the six fixed, disjoint pairs `(e1,e2), (e3,e4), …, (e11,e12)`.
Each difference is the second envelope's interior joules minus the first's.
A pair survives only when both envelopes are retained and share boot and OS
identity. Excluding one envelope drops exactly its original pair; pairs are
never re-formed across a gap. At least eight retained envelopes and four
retained disjoint pairs are required (`minimum_adjacent_pairs` counts these
disjoint pairs). Otherwise the pilot is INCONCLUSIVE and leaves the upper
bound and sizing unset. There is no top-up.

For `n` retained pairs, `s_pair` is the sample standard deviation of their
differences, with `n − 1` degrees of freedom. The one-sided upper 90% confidence
bound is `s_upper = s_pair * sqrt((n − 1) / χ²(0.10, n − 1))`, using the
chi-square lower-tail 10th percentile. The factors are approximately 1.762
for six pairs and 2.266 for four pairs. The implementation numerically inverts
the regularized gamma function using the Python standard library, without
rounding these factors for sizing. **Independence and normality of the pair
differences are assumptions of this construction**, not pilot findings.

The next plan can be authored only after the pilot's spread is measured.
The source for all five sizing constants is `pilot_protocol_v1.json`: δ = 1 J,
multiplier 8, minimum 3 pairs, stop above 24 pairs, and smallest holdable
block-two share 0.05 core. Code reads these registered values. Its sample size is
`n_pairs = max(3, ceil(8 * s_upper² / δ²))`. The eleven overlapping adjacent
differences and twelve single-envelope values remain diagnostics only; neither
sizes block two. The report includes their spreads, first-to-last retained
energy drift, and names every overlapping original adjacent pair with `|Δ| > 3 * s_pair`.
Excluded observations remain visible in those diagnostics; magnitude is never
an exclusion rule. Missing observations remain explicit and cannot bridge a gap.

The pre-registered negative result is **“no cutoff qualifies”** if the sized
sample exceeds 24 pairs, the observer's own busy-core floor exceeds the smallest
holdable share, or block two's upper bound at that share exceeds 1 J. The
result is then the upper bound and the clean-machine busy-core distribution.
Block two would test idle against the smallest holdable share (0.05 core), one
profile and one QoS, with idle–load–idle bracketing; it is not authored here.

For an already authored v2 plan, render its wrapper, sealed manifest and
sidecars with `python3 -B scripts/gen_evidence_night.py --plan /absolute/plan.json
--render-only` (one command). The generator accepts no count, timing, cadence
or protocol overrides and refuses calibration/derivation chains. Every pinned
file must match the measurement commit. The separate evidence verify-only
probe reads files and checks imports, emits exactly one matching manifest
line, and never starts collection, synthetic load or power sampling. It is not
permission to arm. Follow NIGHT_HANDBACK for lead-owned review and arming.

At runtime, collector, recorder, power and sampler groups are journaled and
terminated under bounded cleanup budgets. Only a process-absence census
proves cleanup; a denied group signal is logged, and the power recorder keeps
its supervised stop path. The executor or driver writes one cleanup record;
the courier reads it and reports even pre-execute refusals and unproven cleanup.
A missing process journal means nothing was launched and nothing needs cleaning. The courier may describe completed envelopes,
exclusions and uncertainty; it cannot make a scientific decision.
~~~~

## B8 — `docs/process_traces/2026-09-22-activation-ca45291d/01-arm-record-qpe01-pilot-n1-20260922-2100.md` (complete; the arm record of the night in question)

### B8 — complete
`git show 91f80870:docs/process_traces/2026-09-22-activation-ca45291d/01-arm-record-qpe01-pilot-n1-20260922-2100.md | sed -n '1,95p'`  (lines 1-95 of 95)

~~~~markdown
# Activation ca45291d — arm record for qpe01-pilot-n1-20260922-2100 (2026-09-22, ARMED)

Headless magistrate activation `ca45291d-5492-447a-896e-d9155965b8cd`, spawned by the
watchdog at 20:08:07 PDT (attempt 80) after activation 59857fe5 exited at 20:05 under
D-183 (its resident supervisor pre-dated the arm head). Every step below was executed by
this activation between 20:08 and 20:13 PDT; command outputs are under
`/tmp/*-ca45291d.out` for this boot and, durably, in the staging `lifecycle/` records.

## Authority

- Cold ruling 21 (bounded round 2 of cold gate #3, sealed in packet 08 of activation
  59857fe5): the arm may proceed on the raw replay rows; conditions C1 (addendum 24b,
  done by 59857fe5), C2 (notice links, discharged below), C3 (driver amendment PR after
  the arm, still owed).
- RUN_STATE top block on main `48842569` (successor's exact arm procedure, steps 0–9).
- Ed's NO on any thread overrides at every step; none observed (Gmail search of the
  last day for NO/stop/stand down/directive/NIGHT returned nothing inbound; no owner
  directive issue open; no `standdown.request`, no `STOP`).

## Frozen triple

| Field | Value |
|---|---|
| plan_id | `qpe01-pilot-n1-20260922-2100` (attempt 2 for this date; prior candidate `qpe01-pilot-n1-20260922-0217`) |
| repo_head = measurement_head = H | `dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432` |
| measurement_root (clone) | `/Users/edr/JouleWise-measurement-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432-qpe01-pilot-n1` (HEAD verified = H) |
| custody root | `/Users/edr/night-custody/qpe01-pilot-n1-20260922-2100-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432` |
| staging | `/Users/edr/night-plan-staging/qpe01-pilot-n1-20260922-2100-20260922-2100-1790136000-dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432` |
| t0 | 2026-09-22 21:00:00 PDT = epoch 1790136000 |
| install close (excluded) / REQUEST | 20:50:00 / 20:52:00 PDT |
| TERM / KILL | 20:54:00 / 20:55:00 PDT |
| window end / courier deadline | 23:30:00 / 23:35:00 PDT (window_max_s 9000) |
| daily dead-man | 2026-09-23 00:35:00 PDT |
| registration | `pilot_protocol_v2.json` sha256 `2c5392401a7956dfbb30f316a084541e0f53f214a4ce98c7d56d595ddb2779f1` |
| plan sha256 | `280c811fbc27369b5c4219d3eece2e1b47f423e5d51fa4c36b9566d87e34939b` |
| code frozen since | replay merge `4f8bc36d`: `git diff --stat 4f8bc36d..dbd5cd59 -- joulewise scripts configs` prints nothing (run 20:14 PDT in this worktree) |

## Executed steps (all from `/Users/edr/code/JouleWise`, `python3 -B -m joulewise.evidence_night …`)

| # | Step | Result |
|---|---|---|
| 0 | heartbeat; `env | grep EVIDENCE_POWER_RECORDER` | heartbeat written (pid 15976); env grep empty (rc 1) |
| 0 | `launchctl list | grep joulewise` before | only `com.joulewise.magistrate`; no night plist on disk |
| 0 | launch email to Ed | Gmail `1a0cc3d69e48eec4` (20:09); `notice.ack` written |
| 1 | staged plan reuse | time 20:09 < 20:45 → the 59857fe5 staging (prepare sha256 `f97788d6…`) checked as-is; no re-prepare |
| 2 | terminate own MCP helpers | ROOT 15976 (`claude -p`); TERM 15991 (`node /opt/homebrew/bin/codex mcp-server -c model="gpt-5.6-sol" -c model_reasoning_effort="high" -c mcp_servers.claude.enabled=false`) and its descendant 15993 (vendor `codex mcp-server` binary); descendant scan for `codex mcp-server` empty afterwards. Nothing outside ROOT's subtree touched. |
| 3 | `check --candidate $STAGE` | rc 0, `armable: true`, `fake_launchctl: false`, eight checks pass (`sealed`, `night_agents`, `canonical` [fast_forward null — canonical `48842569` already contains H], `supervisor` [pid 15972 started 1790132887 > H arrival 1790132149], `courier`, `retained_roots`, `census`, `retry`); check id `3f8ccb3136fd` at 20:10:35 |
| 4 | `notice --candidate $STAGE` | rc 0; body == `lifecycle/notice.txt` (5743 bytes, sha256 `859aaf9f8fbfb2086a92abc7a63c50e94fe3b04131a4497947c78b04f576c843`) |
| 5 | send notice | Gmail `1a0cc3fa26b13a44` accepted ≈20:11:30, one recipient `claude2.glaring610@passmail.net`, no cc; subject and body VERBATIM from `notice.txt` plus exactly one appended line (below) |
| 6 | `veto --candidate $STAGE` | rc 0, `clear: true`, `production: true`; NO / STOP / standdown / directives all clear; `non_owner_directives: []` (20:12:12) |
| 7 | `publish-install --candidate $STAGE --notice-accepted 1a0cc3fa26b13a44` | rc 0, `outcome: installed`, `installed: true`, `phase: complete`, published 20:12:28 (epoch 1790133147.9), 22 min before install close; pre-publication both labels ABSENT; probe receipt sha256 `e1457eac…`; `arm-attempts/000001/` holds `plan.json`, `baseline.json`, `install.json`, `veto-at-publication.json`; `notice_verified: false` is the tool's standing statement that it cannot compare sent bytes (it verifies only id-unused + notice newer than sealed artefacts) |
| 8 | `verify --candidate $STAGE` | rc 0: `com.joulewise.night` LOADED, plist sha256 == render sha256 `f2d6c9e8…`, calendar Month 9 Day 22 Hour 21 Minute 0; `com.joulewise.night.deadman` LOADED, `14b5c767…`, calendar Hour 0 Minute 35; baseline drift false (20:12:53) |
| 9 | `launchctl list | grep joulewise` | `com.joulewise.night`, `com.joulewise.magistrate`, `com.joulewise.night.deadman` (all status 0, not running) |

Attempt numbering note: the notice says "Arm attempt 2" (second candidate for the date)
while the staging directory numbers this plan's own first publication
`arm-attempts/000001`; both are the tool's own counters.

## The one appended line (ruling 21 C2), pasted exactly as sent

```
Ruled pre-arm bench replay (cold gate #3 ruling 10 §Q7, cold ruling 21): docs/process_traces/2026-09-22-activation-59857fe5/24-bench-replay-start-drift.md sha256 609d302ebda1dbd59237211fb2231b6fd8f1a52869b7b567a3be29fb0e2108bb + 24-bench-replay.json sha256 1882e92b3053eedcedf7437e2113a38b787a390f9022eac5b96ae00f7c6b0a58 + 24b-bench-replay-addendum-ruling-21.md + 08-coldgate-packet-a267-merge-transaction/21-coldgate-fable-replay-verdict-ruling.md at main dbd5cd59517fe6088bd316a2ea1e66e9cb4d9432 — twelve chain-level start_drift_s, max 0.352 s ≤ 0.5 s; replay executed at merge 4f8bc36d, D-138 transaction 7eb53eff is its ancestor (P7.3).
```

All four files are tracked at `dbd5cd59` (verified with `git cat-file -e`); the two sha256
values were computed at the bench at 20:10 PDT. The addendum's sha256 is
`2b8b37682c9f1e8709543d02ced1c0bcf3c7debcb1d739f970253fa953fb8107` and ruling 21's is
`52f33f60311b0b521f48fe40eaf9cb90ae92996e8702f2d406a32c40ba21f175` (not in the sent line).

## Divergences recorded, not cured (docs frozen at H)

1. `docs/process/NIGHT_HANDBACK.md` §"Where the results are" / §"Next lane" name the
   custody suffix `qpe01-pilot-n1-20260922-2030` (the runbook's planned t0); the night
   that ran is `…-2100`. The Executed block for this plan id, not those sections, names
   the night; the courier reads the handback from the clone at H, so the mismatch is a
   reporting matter only. Same shape as the dc2237d5 arm.
2. The generated notice says "The 7,800-second program fits inside 9,000 seconds"; the
   runbook and handback §"Purpose" derive 8,020 s (600 settle + 11 × 620 pitch + 600).
   The notice text is generated by `render_notice`, sent verbatim by rule; the plan's
   `window_max_s` 9000 bounds either figure. Lane for the successor: reconcile the notice
   template's span arithmetic (docs/template only, never the frozen chain).
3. Notice `notice_verified: false` (see step 7).

## What happens next (successor)

- Machine untouched and agent-free from 20:52 to 23:35 PDT; this activation exits before
  20:52 after pushing this record. The LaunchAgent is the wake source.
- After `night/courier.sent` in the custody root: harvest byte-exact to
  `/Users/edr/night-archive/qpe01-pilot-n1-20260922-2100-harvest-<date>`, verify
  `SHA256SUMS`, then `python3 -B -m joulewise.evidence_night uninstall --candidate $STAGE`
  from the clone (record rc; `launchctl list | grep -c joulewise.night` → 0).
- Then the driver-amendment PR (ruling 21 C3: re-run `verdict()` on `24-bench-replay.json`
  to PASS before any later artifact), the notice-span reconciliation lane, and the
  handback per-night sections for the next plan. A268 waits on Ed. No Codex seats
  (quota until ≈ 09-24 03:00 PDT).
~~~~

